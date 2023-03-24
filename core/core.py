'''
Author: ltt
Date: 2023-03-23 22:59:43
LastEditors: ltt
LastEditTime: 2023-03-24 12:47:13
FilePath: core.py
'''
import sys, os

sys.path.append(
    os.path.abspath(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__)))))
from config import settings
from queue import PriorityQueue
import os, subprocess, re, threading, time, json

class Request():
    def __init__(self, s: str) -> None:
        ret = re.match(r"^\[(?P<time>\d+\.\d+)\](?P<id>\d+)-FROM-(?P<from>\d+)-TO-(?P<to>\d+)$", s)
        self.time = float(ret.group("time"))
        self.id = int(ret.group("id"))
        self.origin = int(ret.group("from"))
        self.to = int(ret.group("to"))
    def __lt__(self, other):
        return self.time < other.time
    
    def __str__(self):
        return f"{self.id}-FROM-{self.origin}-TO-{self.to}\n"
    
class Elevator():
    ARRIVE = r"^\[ *(?P<time>\d+\.\d+)\]ARRIVE-(?P<now>\d+)-(?P<id>\d+)$"
    OPEN = r"^\[ *(?P<time>\d+\.\d+)\]OPEN-(?P<now>\d+)-(?P<id>\d+)$"
    CLOSE = r"^\[ *(?P<time>\d+\.\d+)\]CLOSE-(?P<now>\d+)-(?P<id>\d+)$"
    IN = r"^\[ *(?P<time>\d+\.\d+)\]IN-(?P<pid>\d+)-(?P<now>\d+)-(?P<id>\d+)$"
    OUT = r"^\[ *(?P<time>\d+\.\d+)\]OUT-(?P<pid>\d+)-(?P<now>\d+)-(?P<id>\d+)$"
    def __init__(self, config) -> None:
        self.id = config.id
        self.now = config["initial_floor"]
        self.MOVE_TIME = int(config["move_time"])
        self.OPEN_TIME = int(config["open_time"])
        self.CLOSE_TIME = int(config["close_time"])
        self.floors = {}
        for floor in config["floors"]:
            self.floors[floor] = True
        self.passengers = {}
        self.state = "close"
        self.time = 0
    
    def __str__(self) -> str:
        config = {
            "id" : self.id,
            "move_time" : self.MOVE_TIME,
            "open_time" : self.OPEN_TIME,
            "close_time" : self.CLOSE_TIME,
            "floors" : list(self.floors.keys()),
            "passenger" : list(self.passengers.keys()),
            "now" : self.now,
            "state" : self.state,
            "time" : self.time
        }
        return json.dumps(config, sort_keys=False,
                        indent=4, separators=(',', ': '))
    
    @classmethod
    def parse(cls, elevators, passengers: dict, s):
        arrive = re.match(cls.ARRIVE, s)
        if (arrive != None):
            time, now, id = float(arrive.group("time")), int(arrive.group("now")), int(arrive.group("id"))
            elevator: Elevator = elevators[id]
            if (elevator.state == "open"):
                raise Exception(s, elevator, "在电梯开门时移动")
            if (time - elevator.time < elevator.MOVE_TIME):
                raise Exception(s, elevator, "移动时间间隔错误")
            elevator.now = now
            elevator.time = time
            return
        open = re.match(cls.OPEN, s)
        if (open != None):
            time, now, id = float(open.group("time")), int(open.group("now")), int(open.group("id"))
            elevator: Elevator = elevators[id]
            if (elevator.state == "open"):
                raise Exception(s, elevator, "无效开门动作(门已打开)")
            if (elevator.now != now):
                raise Exception(s, elevator, "电梯不在当前层")
            elevator.state = "open"
            elevator.time = time
            return
        close = re.match(cls.CLOSE, s)
        if (close != None):
            time, now, id = float(close.group("time")), int(close.group("now")), int(close.group("id"))
            elevator: Elevator = elevators[id]
            if (elevator.state == "close"):
                raise Exception(s, elevator, "无效关门动作(门已关闭)")
            if (time - elevator.time < elevator.OPEN_TIME + elevator.CLOSE_TIME):
                raise Exception(s, elevator, "开关门时间间隔过短")
            if (elevator.now != now):
                raise Exception(s, elevator, "电梯不在当前层")
            elevator.state = "close"
            elevator.time = time
            return
        enter = re.match(cls.IN, s)
        if (enter != None):
            time, pid, now, id = float(enter.group("time")), int(enter.group("pid")), int(enter.group("now")), int(enter.group("id"))
            elevator: Elevator = elevators[id]
            if (time < elevator.time):
                raise Exception(s, elevator, "时间错误")
            if (passengers.get(pid, None) == None):
                raise Exception(s, elevator, "没有该乘客")
            if (passengers[pid].now != now):
                raise Exception(s, elevator, "乘客不在当前层")
            if (elevator.state != "open"):
                raise Exception(s, elevators, "电梯未打开")
            if (elevator.now != now):
                raise Exception(s, elevator, "电梯不在当前层")
            passenger: Person = passengers.pop(pid)
            elevator.passengers[pid] = passenger
            passenger.elevator = elevator
            return
        out = re.match(cls.OUT, s)
        if (out != None):
            time, pid, now, id = float(out.group("time")), int(out.group("pid")), int(out.group("now")), int(out.group("id"))
            elevator: Elevator = elevators[id]
            if (time < elevator.time):
                raise Exception(s, elevator, "时间错误")
            if (elevator.passengers.get(pid, None) == None):
                raise Exception(s, elevator, "没有该乘客")
            if (elevator.state != "open"):
                raise Exception(s, elevators, "电梯未打开")
            if (elevator.now != now):
                raise Exception(s, elevator, "电梯不在当前层")
            passenger: Person = elevator.passengers.pop(pid)
            passengers[pid] = passenger
            passenger.elevator = None
            passenger.now = now
            return
        raise Exception(s, '', "wrong output format")
            
            
        

class Person():
    def __init__(self, request: Request) -> None:
        self.id = request.id
        self.origin = request.origin
        self.to = request.to
        self.now = request.origin
        self.elevator = None
    
    def getConfig(self):
        config = {
            "id" : self.id,
            "from" : self.origin,
            "to" : self.to,
            "now" : self.now if self.elevator == None else self.elevator.now,
            "elevator" : None if self.elevator == None else self.elevator.id
        }
        return config
    
    def __str__(self) -> str:
        return json.dumps(self.getConfig(), sort_keys=False,
                        indent=4, separators=(',', ': '))

class Checker():
    def __init__(self, id, path:str, jar:str) -> None:
        self.id = id
        self.path = path
        self.requsets = PriorityQueue()
        with open(path, "r") as f:
            for data in f.readlines():
                self.requsets.put(Request(data))
        
        self.elevators = {}
        for config in settings.elevators:
            elevator = Elevator(config)
            self.elevators[elevator.id] = elevator
        self.persons = {}
        self.commond = [os.path.join(settings.java_home, "bin", "java"), "-jar", jar]
        self.result = {
            "project" : jar,
            "test_data" : path,
            "state" : "WAITTING",
            "result" : ""
        }
        
    def run(self):
        log_path = os.path.join("temp", f"checker-{self.id}.log")
        with open(log_path, "w") as f:
            p = subprocess.Popen(self.commond, shell=False, 
                                stdin=subprocess.PIPE, stdout=f)
            self.result["state"] = "RUNNING"
            def inputdata(stdin, requests: PriorityQueue):
                now = 0
                while not requests.empty():
                    request: Request = requests.get()
                    time.sleep(request.time - now)
                    now = request.time
                    self.persons[request.id] = Person(request)
                    stdin.write(bytes(str(request), 'utf-8'))
                stdin.close()
            threading.Thread(target=inputdata, args=(p.stdin, self.requsets), daemon=True).start()
            try:
                return_code = p.wait()
                if (return_code != 0):
                    self.result["state"] = "RE"
                    return
            except subprocess.TimeoutExpired as e:
                self.result["state"] = "TLE"
        
        with open(log_path, "r") as f:
            try:
                for info in f.readlines():
                    Elevator.parse(self.elevators, self.persons, info)
            except Exception as e:
                self.result["state"] = "WA"
                self.result["result"] = '\n'.join([e.args[2], e.args[0], str(e.args[1])])
                return
        
        self.result["state"] = "AC"
        
    def __str__(self):
        return f"""
project : {self.result["project"]}
test_data : {self.result["test_data"]}
state : {self.result["state"]}
{self.result["result"]}
"""
