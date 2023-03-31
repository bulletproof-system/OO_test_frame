import re, json

from core.person import Person


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