'''
Author: ltt
Date: 2023-04-01 09:29:28
LastEditors: ltt
LastEditTime: 2023-04-23 18:00:59
FilePath: generator.py
'''
import threading, os, random, subprocess
from config import settings

from core.utils import Singleton
from core import utils 


@Singleton
class Generator():
    def __init__(self) -> None:
        self.data_id = 0
        self.__data_id_lock = threading.Lock()
        self.generators = {}
        for path in settings.generators:
            try:
                command = utils.commond(path)
            except:
                continue
            self.generators[path] = command
        if self.generators == {}:
            utils.printc(f"没有可用的数据生成器", "red")
            
    def getId(self):
        with self.__data_id_lock:
            self.data_id += 1
            return self.data_id
    
    def generate(self, generators=None):
        id = self.getId()
        path = os.path.join("input", f"data-{id}"+".in")
        command = random.choice(list(self.generators.values()))
        with open(path, "w") as f:
            try:
                result = subprocess.run(command, stdout=f, timeout=10)
                if result.returncode != 0:
                    utils.printc("generator error")
            except subprocess.TimeoutExpired as e:
                utils.printc("generator TLE")
        return path