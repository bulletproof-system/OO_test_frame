import threading, os
import pandas as pd
from config import settings


from core import utils
from core.core import Program
from core.checker import Checker
from core.generator import Generator

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
        self.funish_num = len(data_paths) * len(jars)
        self.event = threading.Event()
        self.df = pd.DataFrame()
        
        
    def run(self):
        for _ in range(self.num):
            path = Generator().generate()
            for jar in self.jars:
                checker = Checker(path, jar, self)
                self.checkers.append(checker)
                Program().checkers.put(checker)
        for path in self.data_paths:
            for jar in self.jars:
                checker = Checker(path, jar, self)
                self.checkers.append(checker)
                Program().checkers.put(checker)
        self.event.wait()
        utils.printc(f"{self.name} finish\n", "green", end='')
    
    def dump(self):
        path = os.path.join("output", self.name+".csv")
        self.df.to_csv(path)
    
    def update(self, checker: Checker):
        with self.update_lock:
            (_, data_name, _) = utils.split(checker.path)
            (_, project_name, _) = utils.split(checker.jar_name)
            self.df.loc[data_name, project_name] = checker.result["state"]
            self.dump()
            if checker.result["state"] != "RUNNING" and checker.result["state"] != "WAITTING":
                self.funish_num -= 1
                if (self.funish_num == 0):
                    self.event.set()