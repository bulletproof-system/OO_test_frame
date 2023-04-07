'''
Author: ltt
Date: 2023-03-31 21:02:56
LastEditors: ltt
LastEditTime: 2023-04-06 20:51:57
FilePath: dataMaker-hw7.py
'''
import random

################################参数
REQUESTNUM = 70 # 总请求数
ASSEMBLE = 2 # 同一时间戳同时发出请求量的乘客数量
GAPLOW = 5  # 请求之间的最短时间间隔（单位为0.1s）
GAPHIGH = 10 # 请求之间的最长时间间隔（单位为0.1s）
STARTTIME = 1 # 第一个请求的最早时间（单位为1s）
ENDTIME = 50 # 最后一个请求的最晚时间
KEEPORNOT = True # 是否保留2台初始电梯
NEWELEFLOORS = 5 # 新电梯能到达的楼层数
ANTIMAINTAIN = False # 是否舍弃MAINTAIN请求
ANTIADD = False #是否舍弃ADD请求
RUNNUM = 10 # 同时可运行的最大电梯数

################################预处理ID
MAXNUMBER = 201
passengerId = [0 for _ in range(201)]
pOrder = 1
for i in range(1, 101) :
    id = random.randint(1, MAXNUMBER)
    yn = False
    for j in range(1, i+1) :
        if passengerId[j] == id :
            yn = True
            break
    while yn == True :
        id = random.randint(1, MAXNUMBER)
        yn = False
        for j in range(1, i+1) :
            if passengerId[j] == id :
                yn = True
                break
    passengerId[i] = id

elevators = [0 for _ in range(101)]
accessAll = [0 for _ in range(101)]
for i in range(1, 7) :
    elevators[i] = i
    accessAll[i] = 0x7FF
for i in range(7, 101) :
    id = random.randint(7, MAXNUMBER)
    yn = False
    for j in range(1, i+1) :
        if elevators[j] == id :
            yn = True
            break
    while yn == True :
        id = random.randint(1, MAXNUMBER)
        yn = False
        for j in range(1, i+1) :
            if elevators[j] == id :
                yn = True
                break
    elevators[i] = id

################################初始化
currentTime = STARTTIME
maintained = [False for _ in range(101)]
createTime = [-10.0 for _ in range(101)]
elevatorNum = 6 #当前电梯数量
runNum = 6
maintainNum = 0 #起始6台电梯有几台被maintain
request = REQUESTNUM

#################################生成
def canGenerate(type, toMaintain):
    reach = [[False for _ in range(20)] for _ in range(20)]
    if type==2 :
        if ANTIMAINTAIN :
            return False
        if toMaintain<=6 and maintainNum == 4 and KEEPORNOT :
            return False
        if maintained[toMaintain] :
            return False
        if currentTime - createTime[toMaintain] < 2.0 :
            return False
        for i in range(1, 12) :
            for j in range(i, 12) :
                if i==j :
                    reach[i][i] = True
                else :
                    for k in range(1, elevatorNum + 1) :
                        if maintained[k] == True or k == toMaintain :
                            continue
                        if (accessAll[k] & (1<<(i-1)))!=0 and (accessAll[k] & (1<<(j-1)))!=0 :
                            reach[i][j] = reach[j][i] = True
        for k in range(1, 12) :
            for i in range(1, 12) :
                if i==k :
                    continue
                for j in range(1, 12) :
                    if j==i or j==k :
                        continue
                    reach[i][j] |= reach[i][k] & reach[k][j]
        for i in range(1,12) :
            for j in range(1,12) :
                if reach[i][j] == False :
                    return False
    if type==3 :
        if runNum == RUNNUM :
            return False
        if ANTIADD :
            return False
    return True

while request != 0 :
    if request == REQUESTNUM and request > 4 and KEEPORNOT == False :
        for i in range(1,5) :
            request -= 1
            maintained[i] = True
            runNum -= 1
            maintainNum += 1
            print("[" + "{:.1f}".format(currentTime) + "]" + "MAINTAIN-Elevator-" + str(i))
    high = min(max(0, (int)(ENDTIME - currentTime) * 10), GAPHIGH)
    low = min(GAPLOW, high)
    currentTime += 0.1 * random.randint(low, high)
    if currentTime > ENDTIME :
        currentTime = ENDTIME
    assembleNum = min(ASSEMBLE, request)
    
    type = random.randint(1, 3)   # 1:REQUEST 2:MAINTAIN 3:ADD
    toMaintain = random.randint(1, elevatorNum)
    while canGenerate(type, toMaintain) == False:
        type = random.randint(1, 3)
        toMaintain = random.randint(1, elevatorNum)
    #REQUEST
    if type==1 : 
        request -= assembleNum
        while assembleNum!=0 :
            fromDoor = random.randint(1, 11)
            toDoor = random.randint(1, 11)
            while fromDoor==toDoor :
                toDoor = random.randint(1, 11)
            print("[" + "{:.1f}".format(currentTime) + "]" + str(passengerId[pOrder]) + "-FROM-" + str(fromDoor) + "-TO-" + str(toDoor))
            pOrder += 1
            assembleNum -= 1
    #MAINTAIN
    if type==2 : 
        request -= 1
        maintained[toMaintain] = True
        runNum -= 1
        if toMaintain <= 6 :
            maintainNum += 1
        print("[" + "{:.1f}".format(currentTime) + "]" + "MAINTAIN-Elevator-" + str(elevators[toMaintain]))
    #ADD
    if type==3 :
        request -= 1
        elevatorNum += 1
        createTime[elevatorNum] = currentTime
        floor = random.randint(1, 11)
        numLimit = random.randint(3, 8)
        movecost = random.randint(2, 6)
        runNum += 1
        canWork = 0
        access = 0
        while canWork <= NEWELEFLOORS:
            sit = random.randint(0, 10)
            while (access & (1<<sit)) != 0 :
                sit = random.randint(0, 10)
            canWork += 1
            access |= 1<<sit
        accessAll[elevatorNum] = access
        print("[" + "{:.1f}".format(currentTime) + "]" + "ADD-Elevator" 
              + "-" + str(elevators[elevatorNum]) 
              + "-" + str(floor)
              + "-" + str(numLimit)
              + "-0." + str(movecost)
              + "-" + str(access))

        
        
    


