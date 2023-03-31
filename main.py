'''
Author: ltt
Date: 2023-03-24 12:00:07
LastEditors: ltt
LastEditTime: 2023-03-31 21:37:13
FilePath: main.py
'''
from core import *

if __name__ == "__main__":
    Program().start()
    # task = Task(100)
    tasks = []
    for _ in range(10):
        # task = Task(data_paths=[f"input\\wa-{i+1}.in" for i in range(7)])
        # task = Task(data_paths=[f"input\\test-1.in"])
        task = Task(100)
        task.start()
        tasks.append(task)
    for task in tasks:
        task.join()
    Program().stop()