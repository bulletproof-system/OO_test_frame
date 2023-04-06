'''
Author: ltt
Date: 2023-04-06 21:41:32
LastEditors: ltt
LastEditTime: 2023-04-06 22:32:43
FilePath: floor.py
'''
'''
Author: ltt
Date: 2023-04-06 09:59:20
LastEditors: ltt
LastEditTime: 2023-04-06 22:30:17
FilePath: floor.py
'''

from config import settings

class Floor():
    def __init__(self, floor) -> None:
        self.m = settings.Mx
        self.n = settings.Nx
        self.floor = floor
        self.m_result = []
        self.n_result = []

    def add(self, open, close, elevator, info, flag):
        self.m_result.append((open, 1, elevator, info))
        self.m_result.append((close, -1, elevator, info))
        if flag:
            self.n_result.append((open, 1, elevator, info))
            self.n_result.append((close, -1, elevator, info))

    def check(self):
        self.__check(self.m_result, self.m, "Mx")
        self.__check(self.n_result, self.n, "Nx")
    

    def __check(self, result, max_count, prefix):
        result.sort(key=lambda x : x[0])
        now = {}
        count = 0
        for ret in result:
            count += ret[1]
            if count > max_count:
                raise Exception(f"""
{ret[3]}
floor-{self.floor} {prefix} 超过阈值
elevators: {str(list(now.keys()))}
""")
            elevator = ret[2]
            if ret[1] == 1:
                now[elevator.id] = True
            else:
                now.pop(elevator.id)