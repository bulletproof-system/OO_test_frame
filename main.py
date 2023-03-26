'''
Author: ltt
Date: 2023-03-24 12:00:07
LastEditors: ltt
LastEditTime: 2023-03-26 09:59:46
FilePath: main.py
'''
from core import *

if __name__ == "__main__":
    Program().start()
    task = Task(100)
    # task = Task(data_paths=[r"D:\LTT\repository\OO\OOAutoTest_v1_1\stdin.txt"])
    task.start()
    task.join()
    Program().stop()