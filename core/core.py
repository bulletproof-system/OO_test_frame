'''
Author: ltt
Date: 2023-03-23 22:59:43
LastEditors: ltt
LastEditTime: 2023-04-01 17:13:56
FilePath: core.py
'''
from config import settings
from queue import Queue
import os, threading, threading, traceback

from core import utils            
from core.utils import Singleton
from core.checker import Checker

@Singleton
class Program():
    def __init__(self) -> None:
        self.threads: list[CheckThread] = []
        self.checkers = Queue()
        self.stop_flag = False
        os.makedirs("input", exist_ok=True)
        os.makedirs("output", exist_ok=True)
        os.makedirs("temp", exist_ok=True)
        os.makedirs("log", exist_ok=True)

    def start(self):
        utils.printc("Program start...\n", "green", end='')
        for i in range(settings.threads):
            checkThread = CheckThread(i)
            checkThread.start()
            self.threads.append(checkThread)

    def stop(self):
        self.stop_flag = True
        for thread in self.threads:
            thread.join()
        utils.printc("Program stop\n", "green", end='')
        
class CheckThread(threading.Thread):
    def __init__(self, id) -> None:
        super().__init__(daemon=True)
        self.id = id
        
    def run(self):
        while not Program().stop_flag:
            try:
                checker: Checker = Program().checkers.get(timeout = 5)
            except:
                continue
            utils.printc(f"checkThread-{self.id} running on checker-{checker.id}, data-{checker.data.name}, project-{checker.project.name}\n", "blue", end='')
            try:
                checker.run()
            except Exception as e:
                utils.printc(f"checkThread-{self.id} ecxtption{checker}\n{traceback.print_exc()}", "red", end='')
            utils.printc(f"checkThread-{self.id} finish on checker-{checker.id}, data-{checker.data.name}, project-{checker.project.name}, state-{checker.result['state']}\n", 
                         "blue" if checker.result['state'] == "AC" else "red", end='')    
        utils.printc(f"checkThread-{self.id} stop\n", "blue", end='')
            