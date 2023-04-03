'''
Author: ltt
Date: 2023-03-31 18:13:27
LastEditors: ltt
LastEditTime: 2023-04-03 09:14:02
FilePath: project.py
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
        state, cpu_time = "RUNNING", -1
        try:
            with open(log_path, "w") as log:
                with open(error_path, "w") as err:
                    p = psutil.Popen(self.commond, shell=False, 
                                        stdin=subprocess.PIPE, stdout=log, stderr=err)
                    cpu_time = sum(p.cpu_times()[:4])
                    def inputdata(stdin, requests: list[Request]):
                        now = 0
                        nonlocal p, cpu_time
                        try:
                            for request in requests:
                                time.sleep(request.time - now)
                                now = request.time
                                stdin.write(bytes(str(request), 'utf-8'))
                                cpu_time = sum(p.cpu_times()[:4])
                                stdin.flush()
                            stdin.close()
                            while True:
                                cpu_time = sum(p.cpu_times()[:4])
                                time.sleep(0.1)
                        except:
                            pass
                    threading.Thread(target=inputdata, args=(p.stdin, data.requests), daemon=True).start()
                    try:
                        return_code = p.wait(timeout=settings.timeout)
                        if (return_code != 0):
                            state = "RE"
                        if (cpu_time > 10):
                            state = "CTLE"
                        return state, cpu_time
                    except psutil.TimeoutExpired as e:
                        try:
                            p.kill()
                        except:
                            pass
                        state = "TLE"
                        return state, cpu_time
                    except:
                        try:
                            p.kill()
                        except:
                            pass
                        raise
        except :
            state = "UE"
            return state, cpu_time