'''
Author: ltt
Date: 2023-03-31 13:44:39
LastEditors: ltt
LastEditTime: 2023-04-07 19:35:58
FilePath: request.py
'''
import re
from config import settings

from core.elevator import Elevator
from core.person import Person
from core.floor import Floor

delta = 0.001

class Info():
    def __init__(self, s: str) -> None:
        self.time: float
        self.string = s

    def get_time(self):
        return self.time

    def to_string(self):
        return self.string
    
    def update(self, elevators: dict[int, Elevator], passengers: dict[int, Person], floors: list[Floor]):
        pass
    
    def __lt__(self, other):
        return self.get_time() < other.get_time()
    @classmethod
    def parse(cls, s: str):
        if re.match(PersonRequest.pattern, s) != None:
            return PersonRequest(s)
        elif re.match(ElevatorRequest.pattern, s) != None:
            return ElevatorRequest(s)
        elif re.match(MaintainRequest.pattern, s) != None:
            return MaintainRequest(s)
        elif re.match(Arrive.pattern, s) != None:
            return Arrive(s)
        elif re.match(Open.pattern, s) != None:
            return Open(s)
        elif re.match(Close.pattern, s) != None:
            return Close(s)
        elif re.match(In.pattern, s) != None:
            return In(s)
        elif re.match(Out.pattern, s) != None:
            return Out(s)
        elif re.match(MaintainAccept.pattern, s) != None:
            return MaintainAccept(s)
        elif re.match(MaintainAble.pattern, s) != None:
            return MaintainAble(s)
        else:
            return WrongFormat(s)

class WrongFormat(Info):
    def __init__(self, s: str) -> None:
        super().__init__(s)
        self.time = -1
    
    def __str__(self) -> str:
        return self.string
    
    def update(self, elevators: dict[int, Elevator], passengers: dict[int, Person], floors: list[Floor]):
        raise Exception("格式错误")

class Arrive(Info):
    # [时间戳]ARRIVE-所在层-电梯ID
    pattern = r"^\[ *(?P<time>\d+\.\d+)\]ARRIVE-(?P<now>\d+)-(?P<id>\d+)$"
    def __init__(self, s: str) -> None:
        super().__init__(s)
        ret = re.match(self.pattern, s)
        self.time = float(ret.group("time"))
        self.now = int(ret.group("now"))
        self.id = int(ret.group("id"))

    def update(self, elevators: dict[int, Elevator], passengers: dict[int, Person], floors: list[Floor]):
        elevator = elevators.get(self.id, None)
        if elevator == None:
            raise Exception("没有该电梯")
        if elevator.main_tain == "ready":
            raise Exception("电梯正在维修", elevator)
        if elevator.state == "open":
            raise Exception("电梯在开门时移动", elevator)
        if self.get_time() - elevator.time + delta < elevator.MOVE_TIME:
            raise Exception("移动时间间隔过短", elevator)
        if abs(elevator.now - self.now) != 1:
            raise Exception("两次移动楼层差不为 1", elevator)
        if self.now < 0 or self.now > 11:
            raise Exception("移动后电梯不在 [1,11] 区间", elevator)
        if elevator.main_tain == "accept":
            elevator.main_tain_num += 1
        if elevator.main_tain_num > 2:
            raise Exception("Maintain 后移动超过 2 层", elevator)
        elevator.now = self.now
        elevator.time = self.get_time()

class Open(Info):
    # [时间戳]OPEN-所在层-电梯ID
    pattern = r"^\[ *(?P<time>\d+\.\d+)\]OPEN-(?P<now>\d+)-(?P<id>\d+)$"
    def __init__(self, s: str) -> None:
        super().__init__(s)
        ret = re.match(self.pattern, s)
        self.time = float(ret.group("time"))
        self.now = int(ret.group("now"))
        self.id = int(ret.group("id"))

    def update(self, elevators: dict[int, Elevator], passengers: dict[int, Person], floors: list[Floor]):
        elevator = elevators.get(self.id, None)
        if elevator == None:
            raise Exception("没有该电梯")
        if elevator.main_tain == "ready":
            raise Exception("电梯正在维修", elevator)
        if elevator.state == "open":
            raise Exception("重复开门", elevator)
        if elevator.now != self.now:
            raise Exception("电梯不在当前层", elevator)
        if elevator.floors.get(self.now, None) == None:
            if elevator.main_tain != "accept":
                raise Exception("电梯不能在该层开门", elevator)
        if self.now < 0 or self.now > 11:
            raise Exception("电梯不在 [1,11] 区间", elevator)
        elevator.state = "open"
        elevator.time = self.get_time()
        elevator.pre = elevator.passengers.copy()

class Close(Info):
    # [时间戳]CLOSE-所在层-电梯ID
    pattern = r"^\[ *(?P<time>\d+\.\d+)\]CLOSE-(?P<now>\d+)-(?P<id>\d+)$"
    def __init__(self, s: str) -> None:
        super().__init__(s)
        ret = re.match(self.pattern, s)
        self.time = float(ret.group("time"))
        self.now = int(ret.group("now"))
        self.id = int(ret.group("id"))

    def update(self, elevators: dict[int, Elevator], passengers: dict[int, Person], floors: list[Floor]):
        elevator = elevators.get(self.id, None)
        if elevator == None:
            raise Exception("没有该电梯")
        if elevator.main_tain == "ready":
            raise Exception("电梯正在维修", elevator)
        if elevator.state == "close":
            raise Exception("重复关门", elevator)
        if self.get_time() - elevator.time + delta < elevator.OPEN_TIME + elevator.CLOSE_TIME:
            raise Exception("开关门时间间隔过短", elevator)
        if elevator.now != self.now:
            raise Exception("电梯不在当前层", elevator)
        if elevator.floors.get(self.now, None) == None:
            if elevator.main_tain != "accept":
                raise Exception("电梯不能在该层关门", elevator)
        if self.now < 0 or self.now > 11:
            raise Exception("电梯不在 [1,11] 区间", elevator)
        elevator.state = "close"
        flag = True
        for i in elevator.pre.keys():
            if elevator.passengers.get(i, None) == None:
                flag = False
                break
        floors[self.now].add(elevator.time, self.get_time(), elevator, self.to_string(), flag)
        elevator.time = self.get_time()

                

class In(Info):
    # [时间戳]IN-乘客ID-所在层-电梯ID
    pattern = r"^\[ *(?P<time>\d+\.\d+)\]IN-(?P<pid>\d+)-(?P<now>\d+)-(?P<id>\d+)$"
    def __init__(self, s: str) -> None:
        super().__init__(s)
        ret = re.match(self.pattern, s)
        self.time = float(ret.group("time"))
        self.pid = float(ret.group("pid"))
        self.now = int(ret.group("now"))
        self.id = int(ret.group("id"))
    
    def update(self, elevators: dict[int, Elevator], passengers: dict[int, Person], floors: list[Floor]):
        elevator = elevators.get(self.id, None)
        if elevator == None:
            raise Exception("没有该电梯")
        if elevator.main_tain == "ready":
            raise Exception("电梯正在维修", elevator)
        passenger = passengers.get(self.pid, None)
        if passenger == None:
            raise Exception("没有该乘客", elevator)
        if elevator.state != "open":
            raise Exception("电梯未打开", elevator, passenger)
        if elevator.now != self.now:
            raise Exception("电梯不在当前层", elevator, passenger)
        if (len(elevator.passengers) == elevator.capacity):
            raise Exception("电梯超载", elevator)
        passenger: Person = passengers.pop(self.pid)
        elevator.passengers[self.pid] = passenger
        passenger.elevator = elevator

class Out(Info):
    # [时间戳]OUT-乘客ID-所在层-电梯ID
    pattern = r"^\[ *(?P<time>\d+\.\d+)\]OUT-(?P<pid>\d+)-(?P<now>\d+)-(?P<id>\d+)$"
    def __init__(self, s: str) -> None:
        super().__init__(s)
        ret = re.match(self.pattern, s)
        self.time = float(ret.group("time"))
        self.pid = float(ret.group("pid"))
        self.now = int(ret.group("now"))
        self.id = int(ret.group("id"))
    def update(self, elevators: dict[int, Elevator], passengers: dict[int, Person], floors: list[Floor]):
        elevator = elevators.get(self.id, None)
        if elevator == None:
            raise Exception("没有该电梯")
        if elevator.main_tain == "ready":
            raise Exception("电梯正在维修", elevator)
        passenger = elevator.passengers.get(self.pid, None)
        if passenger == None:
            raise Exception("没有该乘客", elevator)
        if elevator.state != "open":
            raise Exception("电梯未打开", elevator, passenger)
        if elevator.now != self.now:
            raise Exception("电梯不在当前层", elevator, passenger)
        passenger: Person = elevator.passengers.pop(self.pid)
        passengers[self.pid] = passenger
        passenger.elevator = None
        passenger.now = self.now

class MaintainAccept(Info):
    # [时间戳]MAINTAIN_ACCEPT-电梯ID
    pattern = r"^\[ *(?P<time>\d+\.\d+)\]MAINTAIN_ACCEPT-(?P<id>\d+)$"
    def __init__(self, s: str) -> None:
        super().__init__(s)
        ret = re.match(self.pattern, s)
        self.time = float(ret.group("time"))
        self.id = int(ret.group("id"))
    
    def update(self, elevators: dict[int, Elevator], passengers: dict[int, Person], floors: list[Floor]):
        elevator = elevators.get(self.id, None)
        if elevator == None:
            raise Exception("没有该电梯")
        elevator.main_tain = "accept"

class MaintainAble(Info):
    # [时间戳]MAINTAIN_ABLE-电梯ID
    pattern = r"^\[ *(?P<time>\d+\.\d+)\]MAINTAIN_ABLE-(?P<id>\d+)$"
    def __init__(self, s: str) -> None:
        super().__init__(s)
        ret = re.match(self.pattern, s)
        self.time = float(ret.group("time"))
        self.id = int(ret.group("id"))
    
    def update(self, elevators: dict[int, Elevator], passengers: dict[int, Person], floors: list[Floor]):
        elevator = elevators.get(self.id, None)
        if elevator == None:
            raise Exception("没有该电梯")
        if elevator.main_tain == "ready":
            raise Exception("电梯正在维修", elevator)
        elevator.main_tain = "ready"

class Request(Info):
    @classmethod
    def parse(cls, s: str):
        if re.match(PersonRequest.pattern, s) != None:
            return PersonRequest(s)
        elif re.match(ElevatorRequest.pattern, s) != None:
            return ElevatorRequest(s)
        elif re.match(MaintainRequest.pattern, s) != None:
            return MaintainRequest(s)
        else:
            return WrongFormat(s)
    def get_time(self):
        return super().get_time() - settings.max_time_sync_error_second
        
class PersonRequest(Request):
    # [时间戳]乘客ID-FROM-起点层-TO-终点层
    pattern = r"^\[ *(?P<time>\d+\.\d+)\](?P<id>\d+)-FROM-(?P<from>\d+)-TO-(?P<to>\d+)$"
    def __init__(self, s: str) -> None:
        super().__init__(s)
        ret = re.match(self.pattern, s)
        self.time = float(ret.group("time"))
        self.id = int(ret.group("id"))
        self.origin = int(ret.group("from"))
        self.to = int(ret.group("to"))
    
    def to_person(self):
        return Person(self.id, self.origin, self.to)

    def update(self, elevators: dict[int, Elevator], passengers: dict[int, Person], floors: list[Floor]):
        passengers[self.id] = self.to_person()
    
    def __str__(self):
        return f"{self.id}-FROM-{self.origin}-TO-{self.to}\n"

class ElevatorRequest(Request):
    # [时间戳]ADD-Elevator-电梯ID-起始楼层-满载人数-移动一层的时间-可达性
    pattern = r"^\[ *(?P<time>\d+\.\d+)\]ADD-Elevator-(?P<id>\d+)-(?P<initial_floor>\d+)-(?P<capacity>\d+)-(?P<move_time>\d+\.\d+)-(?P<access>\d+)$"
    def __init__(self, s: str) -> None:
        super().__init__(s)
        ret = re.match(self.pattern, s)
        self.time = float(ret.group("time"))
        self.id = int(ret.group("id"))
        self.now = int(ret.group("initial_floor"))
        self.capacity = int(ret.group("capacity"))
        self.move_time = float(ret.group("move_time"))
        self.access = int(ret.group("access"))
    
    def to_elevator(self):
        floors = {}
        for i in range(1, 12):
            if 1<<i>>1 & self.access:
                floors[i] = True
        config = {
            "initial_floor" : self.now,
            "capacity" : self.capacity,
            "move_time" : self.move_time,
            "floors" : floors
        }
        return Elevator(self.id, config, self.get_time())
    
    def update(self, elevators: dict[int, Elevator], passengers: dict[int, Person], floors: list[Floor]):
        elevators[self.id] = self.to_elevator()

    def __str__(self) -> str:
        return f"ADD-Elevator-{self.id}-{self.now}-{self.capacity}-{self.move_time}-{self.access}\n"

class MaintainRequest(Request):
    # [时间戳]MAINTAIN-Elevator-电梯ID
    pattern = r"^\[ *(?P<time>\d+\.\d+)\]MAINTAIN-Elevator-(?P<id>\d+)$"
    def __init__(self, s: str) -> None:
        super().__init__(s)
        ret = re.match(self.pattern, s)
        self.time = float(ret.group("time"))
        self.id = int(ret.group("id"))

    def update(self, elevators: dict[int, Elevator], passengers: dict[int, Person], floors: list[Floor]):
        elevator = elevators.get(self.id, None)
        if elevator == None:
            raise Exception("没有该电梯")
        elevator.main_tain = "send"

    def __str__(self) -> str:
        return f"MAINTAIN-Elevator-{self.id}\n"