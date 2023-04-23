'''
Author: ltt
Date: 2023-03-31 13:45:51
LastEditors: ltt
LastEditTime: 2023-04-23 18:55:40
FilePath: checker.py
'''
import threading, os, subprocess, time, re, difflib
from config import settings

from core.data import Data
from core.project import Project

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
        self.result["state"], self.result["cpu_time"] = self.project.run(self.data, self.log_path, self.error_path)
        self.result["run_time"] = ""
        try:
            if (self.result["state"] != "RUNNING"):
                raise Exception("")
            # TODO
            with open(self.data.std_path, "r") as std_file:
                std = std_file.readlines()
            with open(self.log_path, "r") as out_file:
                out = out_file.readlines()
            self.result["result"] = difflib.ndiff(std, out)
            for line in self.result["result"]:
                if line[0] != ' ':
                    raise Exception()
            self.result["result"] = 'Accepted\n'
            self.result["state"] = "AC"
        except Exception as e:
            if self.result["state"] == "RUNNING":
                self.result["state"] = "WA"
                html_path = os.path.join("log", f"checker-{self.id}.html")
                with open(html_path, "w") as f:
                    f.write(diff = difflib.HtmlDiff().make_file(std.splitlines(), out.splitlines(), fromdesc=self.data.std_path, todesc=self.log_path))
                self.result["result"] = html_path
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
