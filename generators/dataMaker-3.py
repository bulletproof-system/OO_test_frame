'''
Author: ltt
Date: 2023-03-31 21:02:56
LastEditors: ltt
LastEditTime: 2023-04-01 13:51:16
FilePath: dataMaker-3.py
'''
import random

################################参数
REQUESTNUM = 70
ASSEMBLE = 7
GAPLOW = 10  # 1s
GAPHIGH = 30 # 3s
STARTTIME = 1.0
ENDTIME = 50

################################预处理ID
MAXNUMBER = 101
passengerId = [0 for _ in range(101)]
pOrder = 1
for i in range(1, 71) :
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
for i in range(1, 7) :
    elevators[i] = i
for i in range(7, 71) :
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
while request != 0 :
    high = min(max(0, (int)(ENDTIME - currentTime) * 10), GAPHIGH)
    low = min(GAPLOW, high)
    currentTime += 0.1 * random.randint(low, high)
    if currentTime > ENDTIME :
        currentTime = ENDTIME
    assembleNum = min(ASSEMBLE, request)
    
    type = random.randint(1, 3)   # 1:REQUEST 2:MAINTAIN 3:ADD
    toMaintain = random.randint(1, elevatorNum)
    while (type==2 and ((toMaintain<=6 and maintainNum == 4) or maintained[toMaintain]==True or (currentTime - createTime[toMaintain] < 2.0))) or (type == 3 and runNum == 10):
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
        print("[" + "{:.1f}".format(currentTime) + "]" + "ADD-Elevator" 
              + "-" + str(elevators[elevatorNum]) 
              + "-" + str(floor)
              + "-" + str(numLimit)
              + "-0." + str(movecost))

        
        
    


