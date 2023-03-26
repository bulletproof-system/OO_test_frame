'''
Author: ltt
Date: 2023-03-25 13:07:58
LastEditors: ltt
LastEditTime: 2023-03-26 10:04:41
FilePath: dataMaker.py
'''
import random
REQUESTNUM = 50
UPNUM = 15
DOWNNUM = 15
gapLow = 1  # 0.1s
gapHigh = 10 # 1s
currentTime = 1.0
for i in range(1,REQUESTNUM+1) :
    currentTime += 0.1 * (random.randint(gapLow, gapHigh))
    if UPNUM==0 :
        fromDoor = random.randint(3, 11)
        toDoor = random.randint(1, fromDoor - 1)
        DOWNNUM = DOWNNUM - 1
    elif DOWNNUM==0 :
        fromDoor = random.randint(1, 9)
        toDoor = random.randint(fromDoor + 1, 11)
        UPNUM = UPNUM - 1
    else :
        t = random.randint(0, 1)
        if t==0 :
            fromDoor = random.randint(1, 9)
            toDoor = random.randint(fromDoor + 1, 11)
            UPNUM = UPNUM - 1
        else :
            fromDoor = random.randint(3, 11)
            toDoor = random.randint(1, fromDoor - 1)
            DOWNNUM = DOWNNUM - 1
    print("[" + "{:.1f}".format(currentTime) + "]" + str(i) + "-FROM-" + str(fromDoor) + "-TO-" + str(toDoor))
