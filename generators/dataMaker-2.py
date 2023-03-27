import random
REQUESTNUM = 70
UPNUM = 15
DOWNNUM = 15
gapLow = 0  # 0s
gapHigh = 20 # 2s
currentTime = 1.0
for i in range(1,REQUESTNUM+1) :
    lastTime = int(currentTime) * 10
    addTime = random.randint(gapLow, min(500 - lastTime, gapHigh))
    currentTime += 0.1 * float(addTime)
    if currentTime > 50 :
        currentTime = 50.0
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


