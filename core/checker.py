import threading, os, subprocess, time
from config import settings
from queue import PriorityQueue

from core import utils
from core.request import Request
from core.elevator import Elevator
from core.person import Person

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
        if settings.display.brief:
            if (self.result["state"] == "AC"):
                os.remove(log_path)
        return
    
    def getState(self):
        return self.result["state"]
        
    def __str__(self):
        return f"""
id : {self.id}
project : {self.result["project"]}
test_data : {self.result["test_data"]}
state : {self.result["state"]}
{self.result["result"]}
"""