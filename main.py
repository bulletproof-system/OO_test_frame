'''
Author: ltt
Date: 2023-03-24 12:00:07
LastEditors: ltt
LastEditTime: 2023-03-25 14:38:58
FilePath: main.py
'''
from core import *

if __name__ == "__main__":
    Program().start()
    task = Task(30)
    task.start()
    task.join()
    Program().stop()