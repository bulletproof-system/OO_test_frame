'''
Author: ltt
Date: 2023-03-23 22:59:43
LastEditors: ltt
LastEditTime: 2023-03-27 16:54:42
FilePath: core.py
'''
import sys, os

# sys.path.append(
#     os.path.abspath(os.path.dirname(os.path.dirname(
#         os.path.abspath(__file__)))))
from config import settings
from queue import PriorityQueue, Queue
import subprocess, re, threading, time, json, threading, random, traceback
import pandas as pd
from core.utils import Singleton
from core import utils
class Request():
    def __init__(self, s: str) -> None:
        ret = re.match(r"^\[ *(?P<time>\d+\.\d+)\](?P<id>\d+)-FROM-(?P<from>\d+)-TO-(?P<to>\d+)$", s)
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
        self.capacity = config["capacity"]
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
            "passengers" : list(self.passengers.keys()),
            "now" : self.now,
            "state" : self.state,
            "time" : self.time
        }
        return json.dumps(config, sort_keys=False,
                        indent=4, separators=(',', ': '))
    
    @classmethod
    def parse(cls, elevators: dict, passengers: dict, s):
        arrive = re.match(cls.ARRIVE, s)
        if (arrive != None):
            time, now, id = float(arrive.group("time")), int(arrive.group("now")), int(arrive.group("id"))
            if id not in elevators.keys():
                raise Exception(s, None, "没有该电梯")
            elevator: Elevator = elevators[id]
            if (elevator.state == "open"):
                raise Exception(s, elevator, "在电梯开门时移动")
            if (time - elevator.time < elevator.MOVE_TIME):
                raise Exception(s, elevator, "移动时间间隔错误")
            if (abs(elevator.now - now) != 1):
                raise Exception(s, elevator, "两次移动楼层差不为 1")
            elevator.now = now
            elevator.time = time
            return
        open = re.match(cls.OPEN, s)
        if (open != None):
            time, now, id = float(open.group("time")), int(open.group("now")), int(open.group("id"))
            if id not in elevators.keys():
                raise Exception(s, None, "没有该电梯")
            elevator: Elevator = elevators[id]
            if (elevator.state == "open"):
                raise Exception(s, elevator, "无效开门动作(门已打开)")
            if (elevator.now != now):
                raise Exception(s, elevator, "电梯不在当前层")
            if (elevator.floors.get(now, None) == None):
                raise Exception(s, elevator, "电梯不能在该层开门")
            elevator.state = "open"
            elevator.time = time
            return
        close = re.match(cls.CLOSE, s)
        if (close != None):
            time, now, id = float(close.group("time")), int(close.group("now")), int(close.group("id"))
            if id not in elevators.keys():
                raise Exception(s, None, "没有该电梯")
            elevator: Elevator = elevators[id]
            if (elevator.state == "close"):
                raise Exception(s, elevator, "无效关门动作(门已关闭)")
            if (time - elevator.time < elevator.OPEN_TIME + elevator.CLOSE_TIME):
                raise Exception(s, elevator, "开关门时间间隔过短")
            if (elevator.now != now):
                raise Exception(s, elevator, "电梯不在当前层")
            if (elevator.floors.get(now, None) == None):
                raise Exception(s, elevator, "电梯不能在该层关门")
            elevator.state = "close"
            elevator.time = time
            return
        enter = re.match(cls.IN, s)
        if (enter != None):
            time, pid, now, id = float(enter.group("time")), int(enter.group("pid")), int(enter.group("now")), int(enter.group("id"))
            if id not in elevators.keys():
                raise Exception(s, None, "没有该电梯")
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
            if (len(elevator.passengers) == elevator.capacity):
                raise Exception(s, elevator, "电梯超载")
            passenger: Person = passengers.pop(pid)
            elevator.passengers[pid] = passenger
            passenger.elevator = elevator
            return
        out = re.match(cls.OUT, s)
        if (out != None):
            time, pid, now, id = float(out.group("time")), int(out.group("pid")), int(out.group("now")), int(out.group("id"))
            if id not in elevators.keys():
                raise Exception(s, None, "没有该电梯")
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
    __id = 0
    __id_lock = threading.Lock()
    @classmethod
    def getId(cls):
        with cls.__id_lock:
            cls.__id += 1
            return cls.__id
    def __init__(self, path:str, jar:str, task) -> None:
        self.id = Checker.getId()
        self.path = path
        (_, self.data_name, _) = utils.split(path)
        (_, self.jar_name, _) = utils.split(jar)
        self.requsets = PriorityQueue()
        with open(path, "r") as f:
            for data in f.readlines():
                if data != '\n':
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
        self.task = task
        self.task.update(self)
        self.error = ''
        
    def run(self):
        log_path = os.path.join("temp", f"checker-{self.id}.log")
        try:
            with open(log_path, "w") as f:
                p = subprocess.Popen(self.commond, shell=False, 
                                    stdin=subprocess.PIPE, stdout=f, stderr=subprocess.PIPE)
                self.result["state"] = "RUNNING"
                self.task.update(self)
                def inputdata(stdin, requests: PriorityQueue):
                    now = 0
                    while not requests.empty():
                        request: Request = requests.get()
                        time.sleep(request.time - now)
                        now = request.time
                        self.persons[request.id] = Person(request)
                        stdin.write(bytes(str(request), 'utf-8'))
                        stdin.flush()
                    stdin.close()
                threading.Thread(target=inputdata, args=(p.stdin, self.requsets), daemon=True).start()
                try:
                    return_code = p.wait(timeout=settings.timeout)
                    self.error = p.stderr.read().decode()
                    if (return_code != 0):
                        self.result["state"] = "RE"
                        raise Exception()
                except subprocess.TimeoutExpired as e:
                    self.result["state"] = "TLE"
                    raise Exception()
                except Exception as e:
                    utils.printc("?")
            
            with open(log_path, "r") as f:
                try:
                    for info in f.readlines():
                        Elevator.parse(self.elevators, self.persons, info)
                except Exception as e:
                    self.result["state"] = "WA"
                    self.result["result"] = '\n'.join([e.args[2], e.args[0], str(e.args[1])])
                    raise Exception()
            for elevator in self.elevators.values():
                if len(elevator.passengers):
                    self.result["state"] = "WA"
                    self.result["result"] = '\n'.join(["电梯非空", str(elevator)])
                    raise Exception()
            for person in self.persons.values():
                if person.now != person.to:
                    self.result["state"] = "WA"
                    self.result["result"] = '\n'.join(["乘客未送达", str(person)])
                    raise Exception()
            self.result["state"] = "AC"
        except Exception as e:
            pass
        with open(log_path, "r+", encoding="utf-8") as f:
            content = f.read()
            f.seek(0, 0)
            f.write(str(self) + self.error + content)
        self.task.update(self)
        return
        
    def __str__(self):
        return f"""
id : {self.id}
project : {self.result["project"]}
test_data : {self.result["test_data"]}
state : {self.result["state"]}
{self.result["result"]}
"""

@Singleton
class Program():
    def __init__(self) -> None:
        self.threads: list[CheckThread] = []
        self.checkers = Queue()
        self.stop_flag = False
        os.makedirs("input", exist_ok=True)
        os.makedirs("output", exist_ok=True)
        os.makedirs("temp", exist_ok=True)

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
            utils.printc(f"checkThread-{self.id} running on checker-{checker.id}, data-{checker.data_name}, project-{checker.jar_name}\n", "blue", end='')
            try:
                checker.run()
            except Exception as e:
                utils.printc(f"checkThread-{self.id} ecxtption{checker}\n{traceback.print_exc()}", "red", end='')
            utils.printc(f"checkThread-{self.id} finish on checker-{checker.id}, data-{checker.data_name}, project-{checker.jar_name}\n", "blue", end='')    
        utils.printc(f"checkThread-{self.id} stop\n", "blue", end='')
            
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
@Singleton
class Generator():
    def __init__(self) -> None:
        self.data_id = 0
        self.__data_id_lock = threading.Lock()
        self.generators = {}
        for path in settings.generators:
            (filePath, fullname) = os.path.split(path)
            (name, suffix) = os.path.splitext(fullname)
            if suffix == ".py":
                command = ["python", path]
            elif suffix == ".jar":
                command = [os.path.join(settings.java_home, "bin", "java"), "-jar", path]
            elif suffix == ".exe" or suffix == "":
                command = [path]
            else:
                utils.printc(f"unsupport generator: {path}, suffix : {suffix}", "yellow")
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
        utils.mkdir("input")
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