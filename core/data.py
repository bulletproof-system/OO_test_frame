'''
Author: ltt
Date: 2023-03-31 18:13:10
LastEditors: ltt
LastEditTime: 2023-04-23 18:12:53
FilePath: data.py
'''
import threading

from core import utils
from core import std

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
            self.std_path = std.calc_std(path)