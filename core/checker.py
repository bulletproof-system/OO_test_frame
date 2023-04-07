'''
Author: ltt
Date: 2023-03-31 13:45:51
LastEditors: ltt
LastEditTime: 2023-04-06 22:27:39
FilePath: checker.py
'''
import threading, os, subprocess, time, re
from config import settings
from queue import PriorityQueue

from core import utils
from core.request import *
from core.elevator import Elevator
from core.person import Person
from core.data import Data
from core.project import Project
from core.floor import Floor

class Checker():
    __id = 0
    __id_lock = threading.Lock()
    @classmethod
    def getId(cls):
        with cls.__id_lock:
            cls.__id += 1
            return cls.__id
    def __init__(self, data: Data, project: Project, task) -> None:
        self.id = Checker.getId()
        self.data = data
        self.project = project
        self.elevators = Elevator.init_elevators()
        self.passengers = {}
        self.floors = [Floor(i) for i in range(12)]
        self.result = {
            "project" : self.project.path,
            "test_data" : self.data.path,
            "state" : "WAITTING",
            "run_time" : -1,
            "cpu_time" : -1,
            "stderr" : "",
            "result" : ""
        }
        self.task = task
        self.log_path = os.path.join("log", f"checker-{self.id}.log")
        self.error_path = os.path.join("temp", f"checker-{self.id}.err")
        self.interval = []
        self.update()
        
    def run(self):
        self.result["state"] = "RUNNING"
        self.update()
        self.result["state"], self.result["cpu_time"]= self.project.run(self.data, self.log_path, self.error_path)
        try:
            if (self.result["state"] != "RUNNING"):
                raise Exception("")
            infos = []
            with open(self.log_path, "r") as f:
                for line in f.readlines():
                    infos.append(Info.parse(line))
            # infos += self.data.requests
            infos = self.data.requests + infos
            infos.sort()
            self.result["run_time"] = infos[-1].time
            for info in infos:
                self.__parse(info)
            for elevator in self.elevators.values():
                elevator.check()
            for passenger in self.passengers.values():
                passenger.check()
            for floor in self.floors:
                floor.check()
            self.result["state"] = "AC"
        except Exception as e:
            if self.result["state"] == "RUNNING":
                self.result["state"] = "WA"
                self.result["result"] = e.args[0]
        finally:
            with open(self.error_path, "r") as err:
                self.result["stderr"] = err.read()
            with open(self.log_path, "r+", encoding="utf-8") as f:
                content = f.read()
                f.seek(0, 0)
                f.write(str(self) + content)
        self.update()
        if settings.display.brief:
            if (self.result["state"] == "AC"):
                os.remove(self.log_path)
        os.remove(self.error_path)
        return

    def __parse(self, info: Info):
        try:
            info.update(self.elevators, self.passengers, self.floors)
        except Exception as e:
            ret = [info.to_string()]
            for argv in e.args:
                ret.append(str(argv))
            raise Exception('\n'.join(ret))
    
    def update(self):
        self.task.update(self)

    def __str__(self):
        return f"""
id : {self.id}
project : {self.result["project"]}
test_data : {self.result["test_data"]}
state : {self.result["state"]}
run_time : {self.result["run_time"]}
cpu_time : {self.result["cpu_time"]}
stderr : 
{self.result["stderr"]}
result : 
{self.result["result"]}
"""
