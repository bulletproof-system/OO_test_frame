'''
Author: ltt
Date: 2023-03-31 13:46:14
LastEditors: ltt
LastEditTime: 2023-03-31 22:47:53
FilePath: Task.py
'''
import threading, os
import pandas as pd
from config import settings


from core import utils
from core.core import Program
from core.checker import Checker
from core.generator import Generator
from core.data import Data
from core.project import Project

class Task(threading.Thread):
    __id = 0
    __id_lock = threading.Lock()
    @classmethod
    def getId(cls):
        with cls.__id_lock:
            cls.__id += 1
            return cls.__id
    def __init__(self, num=10, data_paths = [], jars = settings.jars) -> None:
        """当 data_paths 存在时, 使用给定的数据路径进行测试, 此时 num 参数禁用"""
        super().__init__(daemon=True)
        self.id = self.getId()
        self.name = f"task-{self.id}"
        self.jars = jars
        self.checkers: list[Checker] = []
        self.data_paths = data_paths
        self.num = num if data_paths == [] else 0
        self.update_lock = threading.Lock()
        self.funish_num = 0
        self.event = threading.Event()
        self.df = pd.DataFrame()
        
        
    def run(self):
        for _ in range(self.num):
            path = Generator().generate()
            for jar in self.jars:
                checker = Checker(Data(path), Project(jar), self)
                self.checkers.append(checker)
                self.funish_num += 1
                Program().checkers.put(checker)
        for path in self.data_paths:
            for jar in self.jars:
                checker = Checker(Data(path), Project(jar), self)
                self.checkers.append(checker)
                self.funish_num += 1
                Program().checkers.put(checker)
        self.event.wait()
        utils.printc(f"{self.name} finish\n", "green", end='')
    
    def dump(self):
        path = os.path.join("output", self.name+".csv")
        self.df.to_csv(path)
    
    def update(self, project_name, data_name, state, run_time):
        with self.update_lock:
            if (run_time != -1):
                self.df.loc[data_name, project_name] = state + '-' + str(run_time) + 's'
            else:
                self.df.loc[data_name, project_name] = state
            self.dump()
            if state != "RUNNING" and state != "WAITTING":
                self.funish_num -= 1
                if (self.funish_num == 0):
                    self.event.set()