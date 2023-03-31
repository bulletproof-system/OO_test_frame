import re

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