'''
Author: ltt
Date: 2023-04-01 09:29:28
LastEditors: ltt
LastEditTime: 2023-04-05 22:02:05
FilePath: elevator.py
'''
import re, json
from config import settings

from core.person import Person


class Elevator():
    ARRIVE = r"^\[ *(?P<time>\d+\.\d+)\]ARRIVE-(?P<now>\d+)-(?P<id>\d+)$"
    OPEN = r"^\[ *(?P<time>\d+\.\d+)\]OPEN-(?P<now>\d+)-(?P<id>\d+)$"
    CLOSE = r"^\[ *(?P<time>\d+\.\d+)\]CLOSE-(?P<now>\d+)-(?P<id>\d+)$"
    IN = r"^\[ *(?P<time>\d+\.\d+)\]IN-(?P<pid>\d+)-(?P<now>\d+)-(?P<id>\d+)$"
    OUT = r"^\[ *(?P<time>\d+\.\d+)\]OUT-(?P<pid>\d+)-(?P<now>\d+)-(?P<id>\d+)$"
    @staticmethod
    def init_elevators():
        elevators = {}
        for id, config in settings.elevators.items():
            if (id == "default"):
                continue
            id = int(id)
            elevators[id] = Elevator(id, config)
        return elevators

    def __init__(self, id: int, config: dict, time = 0) -> None:
        default = settings.elevators["default"]
        self.id = id
        self.now = config.get("initial_floor", default["initial_floor"])
        self.capacity = config.get("capacity", default["capacity"])
        self.MOVE_TIME = config.get("move_time", default["move_time"])
        self.OPEN_TIME = config.get("open_time", default["open_time"])
        self.CLOSE_TIME = config.get("close_time", default["close_time"])
        self.floors = {}
        if (config.get("floors", None) != None):
            for floor in config["floors"]:
                self.floors[floor] = True
        else:
            for floor in default["floors"]:
                self.floors[floor] = True
        self.passengers = {}
        self.state = "close"
        self.main_tain = "not send"
        self.main_tain_num = 0
        self.time = time
        self.pre = {}
    
    def check(self):
        if len(self.passengers) != 0:
            raise Exception("电梯非空" + str(self))
        if self.main_tain == "send":
            raise Exception("电梯未输出 MAINTAIN_ACCEPT" + str(self))
        if self.main_tain == "accept":
            raise Exception("电梯未输出 MAINTAIN_ABLE" + str(self))
        if self.state == "open":
            raise Exception("电梯未关门" + str(self))
    
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
            "main_tain" : self.main_tain,
            "time" : self.time
        }
        return json.dumps(config, sort_keys=False,
                        indent=4, separators=(',', ': '))