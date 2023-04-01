'''
Author: ltt
Date: 2023-03-31 18:13:27
LastEditors: ltt
LastEditTime: 2023-04-01 17:12:56
FilePath: Project.py
'''
import threading, os, subprocess, time
from config import settings
from queue import PriorityQueue

from core import utils
from core.data import Data
from core.request import Request

class Project():
    projects = {}
    __projects_lock = threading.Lock()
    def __new__(cls, *args, **kwargs):
        path = args[0]
        with cls.__projects_lock:
            if cls.projects.get(path, None) != None:
                return cls.projects[path]
            return super().__new__(cls)
    def __init__(self, path) -> None:
        with self.__projects_lock:
            if (self.projects.get(path, None) != None):
                return
            self.projects[path] = self
            self.path = path
            (_, self.name, _) = utils.split(path)
            self.commond = [os.path.join(settings.java_home, "bin", "java"), "-jar", path]

    def run(self, data: Data, log_path: str, error_path):
        state = "RUNNING"
        try:
            with open(log_path, "w") as log:
                with open(error_path, "w") as err:
                    p = subprocess.Popen(self.commond, shell=False, 
                                        stdin=subprocess.PIPE, stdout=log, stderr=err)
                    def inputdata(stdin, requests: list[Request]):
                        now = 0
                        for request in requests:
                            time.sleep(request.time - now)
                            now = request.time
                            stdin.write(bytes(str(request), 'utf-8'))
                            stdin.flush()
                        stdin.close()
                    threading.Thread(target=inputdata, args=(p.stdin, data.requests), daemon=True).start()
                    try:
                        return_code = p.wait(timeout=settings.timeout)
                        if (return_code != 0):
                            state = "RE"
                        return state
                    except subprocess.TimeoutExpired as e:
                        stderr = p.stderr.read().decode()
                        state = "TLE"
                        return state
        except :
            state = "UE"
            return state