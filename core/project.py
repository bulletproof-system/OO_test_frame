'''
Author: ltt
Date: 2023-03-31 18:13:27
LastEditors: ltt
LastEditTime: 2023-03-31 21:34:39
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
            self.projects[path] = self
            self.path = path
            (_, self.name, _) = utils.split(path)
            self.commond = [os.path.join(settings.java_home, "bin", "java"), "-jar", path]

    def run(self, data: Data, log_path: str):
        (state, stderr) = ("RUNNING", "")
        try:
            with open(log_path, "w") as f:
                p = subprocess.Popen(self.commond, shell=False, 
                                    stdin=subprocess.PIPE, stdout=f, stderr=subprocess.PIPE)
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
                    stderr = p.stderr.read().decode()
                    if (return_code != 0):
                        state = "RE"
                    return (state, stderr)
                except subprocess.TimeoutExpired as e:
                    state = "TLE"
                    return (state, stderr)
        except :
            state = "UE"
            return (state, stderr)