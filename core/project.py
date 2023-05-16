'''
Author: ltt
Date: 2023-03-31 18:13:27
LastEditors: ltt
LastEditTime: 2023-05-16 15:59:24
FilePath: project.py
'''
import threading, os, subprocess, time, psutil
from config import settings

from core import utils
from core.data import Data
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
            with open(data.path, "r") as input:
                with open(log_path, "w") as log:
                    with open(error_path, "w") as err:
                        cpu_time = 0
                        p = psutil.Popen(self.commond, shell=False, stdin=input, stdout=log, stderr=err)
                        def calc_ctime():
                            nonlocal cpu_time, p
                            try:
                                while True:
                                    cpu_time = sum(p.cpu_times()[:4])
                                    time.sleep(0.01)
                            except:
                                pass
                        threading.Thread(target=calc_ctime, daemon=True).start()
                    try:
                        return_code = p.wait(timeout=settings.timeout)
                        if (return_code != 0):
                            state = "RE"
                        
                        if (cpu_time > settings.timeout):
                            state = "CTLE"
                        return state, cpu_time
                    except psutil.TimeoutExpired as e:
                        try:
                            p.kill()
                        except:
                            pass
                        state = "RTLE"
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