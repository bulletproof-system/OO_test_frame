'''
Author: ltt
Date: 2023-03-31 18:13:27
LastEditors: ltt
LastEditTime: 2023-04-02 10:09:16
FilePath: Project.py
'''
import threading, os, subprocess, time, psutil
from config import settings

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
                    info = psutil.Process(p.pid)
                    (user, system, children_user, children_system) = info.cpu_times()
                    def inputdata(stdin, requests: list[Request]):
                        now = 0
                        for request in requests:
                            time.sleep(request.time - now)
                            now = request.time
                            stdin.write(bytes(str(request), 'utf-8'))
                            stdin.flush()
                        stdin.close()
                        nonlocal info, user, system, children_user, children_system
                        try:
                            while True:
                                (user, system, children_user, children_system) = info.cpu_times()
                                time.sleep(0.1)
                        except:
                            pass
                    threading.Thread(target=inputdata, args=(p.stdin, data.requests), daemon=True).start()
                    try:
                        return_code = p.wait(timeout=settings.timeout)
                        p.kill()
                        cpu_time = user + system + children_user + children_system
                        if (return_code != 0):
                            state = "RE"
                        if (cpu_time > 10):
                            state = "CTLE"
                        return state, cpu_time
                    except subprocess.TimeoutExpired as e:
                        p.kill()
                        cpu_time = user + system + children_user + children_system
                        state = "TLE"
                        return state, cpu_time
        except :
            state = "UE"
            return state, -1