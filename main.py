from library import *

screen = Screen()

# makes border
border = Turtle()
border.ht()
border.penup()
border.speed('fastest')
border.pensize(5)
border.color('#000000')
border.goto(-LENGTH/2, LENGTH/2)
border.pendown()

border.fillcolor('grey')
border.begin_fill()
for i in range(4):
    border.forward(LENGTH)
    border.right(90)

border.end_fill()


amtExposed = 1
amtImmune = 0
amtDead = 0

loop = True
day = 0

screen.tracer(10, 5)

# Holds the index of infected turtles
infectedIndicies = list()

stateVals = [amtExposed, len(infectedIndicies), amtImmune, strainList]

writeTitle = Writer(0, LENGTH*2/3)
writeTitle.write("COVID-19 VARIANCE MODEL", "center", ("Arial", 40, "normal"))

writeDay = Writer(-LENGTH/2, LENGTH/2)
writeDay.write(f"Day: {day}", "left")

writePeople = Writer(LENGTH/2, LENGTH/2)
writePeople.write(f"Number of People: {PEOPLE_AMT}", "right")

writeStats = Writer(-LENGTH/2, -LENGTH/2 - 120)
stats(writeStats, stateVals)

P_OFFSET = 20


def legend(person, text):
    person.turt.stamp()
    person.turt.ht()
    person.turt.fd(10)
    person.turt.rt(90)
    person.turt.fd(10)
    person.turt.write(text,False,"left", ("Arial", 20, "normal"))



for i in range(len(stateList)):
    p =Person(LENGTH/6, -LENGTH/2 - (i + 1)*P_OFFSET, "x")
    p.updateState(stateList[i])
    legend(p, states[stateList[i]])


borderOffset = 10

people = list()
# people = np.array([], object)
for i in range(PEOPLE_AMT):
    p = Person(randint(-LENGTH/2+borderOffset, LENGTH/2-borderOffset),
               randint(-LENGTH/2+borderOffset, LENGTH/2-borderOffset), i)
    if i == 0:
        p.updateState(EXPOSED)
        p.timeOfExposure = round(0, 2)
        p.covidVarient = 1
        p.currentStrain = STARTING_COVID_STRAIN

    people.append(p)
    # np.append(people, p)


# lowestVarient = 1

# time
START_TIME = time()

worldTime = round(time()-START_TIME, 2)

while loop:

    if worldTime > day * SEC_PER_DAY:
        writeDay.write(f"Day: {day}", "left")
        day += 1
        # print(day)

    # current world time
    worldTime = round(time()-START_TIME, 2)

    # everyone moves one step
    for p in people:
        if p != None:
            p.move()

    loop = False
    # state transition logic
    for i, p in enumerate(people):
        if p != None:
            # checks and updates viral load for exposed peope
            if p.state == EXPOSED:
                if p.checkViralLoad(worldTime):
                    p.sickOrAsym(worldTime)
                    infectedIndicies.append(i)
                    amtExposed -= 1
                    stats(writeStats, stateVals)

                    if p.state == SICK:
                        p.chanceDeath()

            # no longer immune to current strain
            elif p.state == RECOVERY:
                if p.checkForHealed(worldTime):
                    p.updateState(HEALTHY)
                    p.currentStrain = -1
                    amtImmune -= 1
                    stats(writeStats, stateVals)

            # if everyone is healed or in recovery then end
            if p.state in (EXPOSED, SICK, ASYM):
                # print(p)
                loop = True

    # checks for scpread
    for infected in infectedIndicies[::]:
        # print(people[infected])
        # if sick person is in recovery skip check
        if people[infected].checkRecovery(worldTime):
            if people[infected].die:
                infectedIndicies.remove(infected)
                people[infected].updateState("black")
                people[infected] = None
                amtDead += 1
                writePeople.write(f"Number of People: {PEOPLE_AMT-amtDead}", "right")
                # print(amtDead)
                continue

                # pass
            else:
                people[infected].updateState(RECOVERY)
                people[infected].timeOfHealed = worldTime
                infectedIndicies.remove(infected)
                stats(writeStats, stateVals)
                amtImmune += 1
                continue

        # checks distance bw infected and non infected people
        for i, p in enumerate(people):
            if p != None:
                if p.turt.distance(people[infected].turt) < DISTANCE + STEP_DIST:
                    if p.state in (HEALTHY, RECOVERY):
                        if p.checkSpread(people[infected], worldTime):
                            if p.state == RECOVERY:
                                amtImmune -= 1

                            p.updateState(EXPOSED)
                            p.setVarient(people[infected])
                            amtExposed += 1
                            stats(writeStats, stateVals)

                            if p.covidVarient < NEW_MUTUATION_LIMIT:
                                # print("NEW STRAIN ALERT")
                                i = ord(people[infected].currentStrain[0])
                                i += 1

                                newStrain = chr(i)
                                for i in range(len(strainList)):
                                    if newStrain in strainList:
                                        i = ord(people[infected].currentStrain[0])
                                        i += 1  
                                        newStrain = chr(i)

                                    else:
                                        strainList.append(newStrain)
                                        stats(writeStats, stateVals)
                                        break


                                
                                
                                p.currentStrain = newStrain
                                p.setVarient()
                                # if newStrain not in strainList:
                                #     strainList.append(newStrain)
                                #     stats(writeStats)
                            else:
                                p.currentStrain = people[infected].currentStrain

                            # if p.covidVarient < lowestVarient:
                            #     lowestVarient = p.covidVarient
                            #     print(round(lowestVarient, 2))


input()
    # system("clear")
    # print(worldTime)

# TODO
# improve person movement
# implement vaccine effect
