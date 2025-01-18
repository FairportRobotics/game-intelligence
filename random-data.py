import pandas as pd
import random
import csv


# 1.Red 1, name, 2025nyro, qm, match #, Red 1, team #, sc y/n, leave y/n, L1a, L2a, L3a, L4a, ana, apa, 
#           L1t, L2t, L3t, L4t, ant, apt, pickup c, final status, w/l, arp, crp, brp, immoblized, dropped y/n,
#           good partner y/n, comments " "


numTeams = 53
teams = set()
numGenerated = 0
data = []
pickup = ["s", "f", "b", "x"]
hang = ["p", "s", "d", "x"]



def genTeams():
    while len(teams) < numTeams:
        num = random.randint(1, 9999)
        if num not in teams:
            teams.add(num)


def simulate():
    numMatches = numTeams*8/6
    currentMatch = 1
    while(currentMatch < numMatches):
        teamsInMatch = []
        for x in range(3):
            rand = getNewRand(teamsInMatch)
            team = teams[rand]
            teamsInMatch.append(rand)
            al1 = random.randint(0,24)
            al2 = random.randint(0,12)
            al3 = random.randint(0,12)
            al4 = random.randint(0,12)
            apa = random.randint(0,9)
            ana = random.randint(0,9-apa)
            apt = random.randint(0, 9-apa-ana)
            ant = random.randint(0,9-apa-ana-apt)
            if(apt < 0):
                apt = 0
            if(ant < 0):
                ant = 0
            data.append([
                f"{currentMatch}.Red {x+1}", "aa", "2025nyro", "qm", currentMatch, f"Red {x+1}", team, 
                True, random.randint(0,1), al1, al2, al3, al4, ana, apa, random.randint(0,24-al1), 
                random.randint(0,12-al2), random.randint(0,12-al3), random.randint(0,12-al4), ant,
                apt, pickup[random.randint(0,3)], hang[random.randint(0,3)], random.randint(0,1)
            ])

        for y in range(3):
            rand = getNewRand(teamsInMatch)
            team = teams[rand]
            teamsInMatch.append(rand)
            al1 = random.randint(0,24)
            al2 = random.randint(0,12)
            al3 = random.randint(0,12)
            al4 = random.randint(0,12)
            apa = random.randint(0,9)
            ana = random.randint(0,9-apa)
            apt = random.randint(0, 9-apa-ana)
            ant = random.randint(0,9-apa-ana-apt)
            if(apt < 0):
                apt = 0
            if(ant < 0):
                ant = 0
            data.append([
                f"{currentMatch}.Blue {y+1}", "aa", "2025nyro", "qm", currentMatch, f"Blue {y+1}", team, 
                True, random.randint(0,1), al1, al2, al3, al4, ana, apa, random.randint(0,24-al1), 
                random.randint(0,12-al2), random.randint(0,12-al3), random.randint(0,12-al4), ant,
                apt, pickup[random.randint(0,3)], hang[random.randint(0,3)], random.randint(0,1)
            ])

        allLeftR = True
        for l in range (3):
            if(data[currentMatch*6-6+l][8] == 0):
                allLeftR = False
        scoredR = False
        for s in range(3):
            if(
                data[currentMatch*6-6+s][9] > 0 or data[currentMatch*6-6+s][10] > 0 or
                data[currentMatch*6-6+s][11] > 0 or data[currentMatch*6-6+s][12] > 0
                ):
                scoredR = True
        if(allLeftR and scoredR):
            for a in range(3):
                data[currentMatch*6-6+a].append(True)
        else:
            for a in range(3):
                data[currentMatch*6-6+a].append(False)

        allLeftB = True
        for l in range (3):
            if(data[currentMatch*6-6+l+3][8] == 0):
                allLeftB = False
        scoredB = False
        for s in range(3):
            if(
                data[currentMatch*6-6+s+3][9] > 0 or data[currentMatch*6-6+s+3][10] > 0 or
                data[currentMatch*6-6+s+3][11] > 0 or data[currentMatch*6-6+s+3][12] > 0
                ):
                scoredB = True
        if(allLeftB and scoredB):
            for a in range(3):
                data[currentMatch*6-6+a+3].append(True)
        else:
            for a in range(3):
                data[currentMatch*6-6+a+3].append(False)

        coopertitionR = False
        coopertitionB = False
        coopertition = False
        tallyPR = 0
        for w in range(3):
            tallyPR += data[currentMatch*6-6+w][14] + data[currentMatch*6-6+w][20]
        if(tallyPR > 1):
            coopertitionR = True
        
        tallyPB = 0
        for v in range(3):
            tallyPB += data[currentMatch*6-6+v+3][14] + data[currentMatch*6-6+v+3][20]
        if(tallyPB > 1):
            coopertitionB = True

        if(coopertitionB and coopertitionR):
            coopertition = True
        
        reefR = []
        for r in range(3):
            reefR.append(data[currentMatch*6-6+r][9] + data[currentMatch*6-6+r][15])
            reefR.append(data[currentMatch*6-6+r][10] + data[currentMatch*6-6+r][16])
            reefR.append(data[currentMatch*6-6+r][11] + data[currentMatch*6-6+r][17])
            reefR.append(data[currentMatch*6-6+r][12] + data[currentMatch*6-6+r][18])
        numSatisfied = 0
        for val in reefR:
            if(val >= 5):
                numSatisfied += 1
        if(coopertition and numSatisfied >= 3):
            for crp in range(3):
                data[currentMatch*6-6+crp].append(True)
        elif(numSatisfied == 4):
            for crp in range(3):
                data[currentMatch*6-6+crp].append(True)
        else:
            for crp in range(3):
                data[currentMatch*6-6+crp].append(False)

        reefB = []
        for b in range(3):
            reefB.append(data[currentMatch*6-6+b+3][9] + data[currentMatch*6-6+3+b][15])
            reefB.append(data[currentMatch*6-6+b+3][10] + data[currentMatch*6-6+3+b][16])
            reefB.append(data[currentMatch*6-6+b+3][11] + data[currentMatch*6-6+b+3][17])
            reefB.append(data[currentMatch*6-6+b+3][12] + data[currentMatch*6-6+b+3][18])
        numSatisfied = 0
        for val in reefB:
            if(val >= 5):
                numSatisfied += 1
        if(coopertition and numSatisfied >= 3):
            for crp in range(3):
                data[currentMatch*6-6+crp+3].append(True)
        elif(numSatisfied == 4):
            for crp in range(3):
                data[currentMatch*6-6+crp+3].append(True)
        else:
            for crp in range(3):
                data[currentMatch*6-6+crp+3].append(False)

        bargeScoreR = 0
        bargeScoreB = 0

        for bsr in range(3):
            level = data[currentMatch*6-6+bsr][22]
            if(level == "d"):
                bargeScoreR += 12
            elif(level == "s"):
                bargeScoreR += 6
            elif(level == "p"):
                bargeScoreR += 2
        if(bargeScoreR >= 14):
            for brp in range(3):
                data[currentMatch*6-6+brp].append(True)
        else:
            for brp in range(3):
                data[currentMatch*6-6+brp].append(False)

        for bsb in range(3):
            level = data[currentMatch*6-6+bsb+3][22]
            if(level == "d"):
                bargeScoreB += 12
            elif(level == "s"):
                bargeScoreB += 6
            elif(level == "p"):
                bargeScoreB += 2
        if(bargeScoreB >= 14):
            for brp in range(3):
                data[currentMatch*6-6+brp+3].append(True)
        else:
            for brp in range(3):
                data[currentMatch*6-6+brp+3].append(False)
        
        currentMatch += 1


def getNewRand(used:list):
    avalible = False
    while not avalible:
        avalible = True
        rand = random.randint(0,len(teams)-1)
        for i in used:
            if(rand == i):
                avalible = False
    return rand

# 1.Red 1, name, 2025nyro, qm, match #, Red 1, team #, sc y/n, leave y/n, L1a, L2a, L3a, L4a, ana, apa, 
#           L1t, L2t, L3t, L4t, ant, apt, pickup c, final status, w/l, arp, crp, brp,

def convert():
    df = pd.DataFrame(data)
    df.columns = [
        "Team-Match Key", "Scouter Name", "event key", "match level", "match number", "alliance position",
        "team number", "start w/ coral", "leave start", "L1 auto", "l2 auto", "L3 auto", "L4 auto",
        "net auto", "processor auto", "L1 teleop", "L2 teleop", "L3 teleop", "L4 teleop", "net teleop", 
        "processor teleop", "pickup coral", "final status", "win/lose", "arp", "crp", "brp"
        ]
    df.to_csv("./data/testingData.csv", sep=",", index=False, header=True)
    


genTeams()
teams = list(teams)
simulate()
convert()

