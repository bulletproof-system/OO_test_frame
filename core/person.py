'''
Author: ltt
Date: 2023-03-31 13:45:29
LastEditors: ltt
LastEditTime: 2023-03-31 22:13:47
FilePath: Person.py
'''
import json

class Person():
    def __init__(self, id, origin, to) -> None:
        self.id = id
        self.origin = origin
        self.to = to
        self.now = origin
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

    def check(self):
        if self.now != self.to:
            raise Exception("乘客未送达\n" + str(self))
    
    def __str__(self) -> str:
        return json.dumps(self.getConfig(), sort_keys=False,
                        indent=4, separators=(',', ': '))