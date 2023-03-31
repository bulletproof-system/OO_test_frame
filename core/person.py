import json

from core.request import Request

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