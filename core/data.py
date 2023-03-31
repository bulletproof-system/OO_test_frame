'''
Author: ltt
Date: 2023-03-31 18:13:10
LastEditors: ltt
LastEditTime: 2023-03-31 23:47:33
FilePath: Data.py
'''
import threading

from core import utils
from core.request import *

class Data():
    datas = {}
    __datas_lock = threading.Lock()
    def __new__(cls, *args, **kwargs):
        path = args[0]
        with cls.__datas_lock:
            if cls.datas.get(path, None) != None:
                return cls.datas[path]
            return super().__new__(cls)
    def __init__(self, path) -> None:
        with self.__datas_lock:
            if (self.datas.get(path, None) != None):
                return
            self.datas[path] = self
            self.path = path
            (_, self.name, _) = utils.split(path)
            self.requests = []
            with open(path, "r") as f:
                for line in f.readlines():
                    self.requests.append(Request.parse(line))
            self.requests.sort()

            