from turtle import Turtle, Screen, heading, left
from random import randint, random
# import numpy as np
from time import sleep, time
from os import system
# import math

# health states
HEALTHY = "blue"
EXPOSED = "green"
ASYM = "yellow"
SICK = "red"
RECOVERY = "orange"
DEAD = "black"

states = {
    HEALTHY: "Healthy",
    EXPOSED: "Exposed",
    ASYM: "Asymptomatic",
    SICK: "Sick",
    RECOVERY: "Immune",
    DEAD: "Dead"
}


stateList = [HEALTHY, EXPOSED, SICK,ASYM, RECOVERY, DEAD]
# constants
# all time in seconds
LENGTH = 400  # board width
TURN_RANGE = 60  # range of turing for turtle
STEP_DIST = 10  # step distance per loop iteration
SICK_STEP_OFFSET = 9
TURT_SIZE = .75  # radius of person
PEOPLE_AMT = 100  # people in model

SEC_PER_DAY = .5   # seconds to day converson
DISTANCE = 20  # range of virus spread
SPREAD_TIME = .2 * SEC_PER_DAY  # time to be in range for spread
VIRAL_LOAD = 7 * SEC_PER_DAY  # time exposed before becoming sick/asym
RECOVERY_TIME = 14 * SEC_PER_DAY  # time sick before becoming healed
RT_SICK_RANGE = 1.5 * SEC_PER_DAY  # offset recovery time for sick people
IMMUNE_TIME = 90 * SEC_PER_DAY  # time with anitbodies after recovery
MUTATION_RATE = .93  # rate at which covid will mutate
CHANCE_OF_ASYM = .3  # percent chance of being asymptomatic
CHANCE_OF_Death = .1  # percent chance of dying
NEW_MUTUATION_LIMIT = .6  # percent at which virus mutates
STARTING_COVID_STRAIN = "A"
strainList = [STARTING_COVID_STRAIN]



class Person():
    def __init__(self, x, y, ID):
        self.state = HEALTHY
        self.contactDebounce = False
        self.contactTime = -1   # time of first contact with sick person
        self.timeOfExposure = -1  # time of becoming exposed
        self.viralLoad = -1     # time in exposed state
        self.sickTime = -1  # time of becoming sick
        self.covidVarient = -1  # current covid varient
        self.timeOfHealed = -1  # time starting recovery
        self.currentStrain = -1
        self.id = ID
        self.die = False

        # turtle set up
        self.turt = Turtle()
        self.turt.ht()
        self.turt.color(self.state)
        self.turt.shape("circle")
        self.turt.pencolor('black')
        self.turt.shapesize(TURT_SIZE)
        self.turt.pu()
        self.turt.speed(0)
        self.turt.goto(x, y)
        self.turt.st()

    def __str__(self):
        return f"""
        ID: {self.id}
        State: {states[self.state]}
        Covid Strain: {self.currentStrain}
        Varience of Strain: {round(self.covidVarient,2)}
        Location: {self.turt.pos()}
        """

    # check dist and time for spread of covid
    def checkSpread(self, turt2, worldTime):
        if self.state == HEALTHY or (self.state == RECOVERY and self.currentStrain != turt2.currentStrain):
            if turt2.state in (SICK, ASYM):
                if self.turt.distance(turt2.turt) <= DISTANCE:
                    # print(f"Current Dist: {self.turt.distance(turt2.turt)}")

                    if self.contactDebounce == False:
                        self.contactTime = worldTime
                        self.contactDebounce = True
                        # print(f"contact time set: {self.contactTime}")

                    if worldTime - self.contactTime > SPREAD_TIME:
                        # print("EXPOSED BOI")
                        self.timeOfExposure = worldTime
                        self.contactDebounce = False
                        return True

                    # print(f"Time in Contact: {round(worldTime - self.contactTime,2)}")
                else:
                    self.contactTime = -1
                    self.contactDebounce = False

    # person movement
    def move(self):
        self.turt.rt(randint(-TURN_RANGE, TURN_RANGE))
        if self.state == SICK:
            self.turt.fd(STEP_DIST-SICK_STEP_OFFSET)
        else:
            self.turt.fd(STEP_DIST)

        # model borders
        if self.turt.xcor() + STEP_DIST > LENGTH/2:
            self.turt.seth(180)
        if self.turt.xcor() - STEP_DIST < -LENGTH/2:
            self.turt.seth(0)
        if self.turt.ycor() + STEP_DIST > LENGTH/2:
            self.turt.seth(270)
        if self.turt.ycor() - STEP_DIST < -LENGTH/2:
            self.turt.seth(90)

    # change state and color of person
    def updateState(self, state):
        self.state = state
        self.turt.color(self.state)
        self.turt.pencolor('black')

    # returns true if viral load large enough to become sick
    def checkViralLoad(self, wordlTime):
        self.viralLoad = wordlTime - self.timeOfExposure

        if self.viralLoad > VIRAL_LOAD:
            return True
        else:
            return False

    # set to sick or asymptomatic according to chance
    def sickOrAsym(self, worldTime):
        if random() > CHANCE_OF_ASYM:
            self.updateState(SICK)
        else:
            self.updateState(ASYM)

        self.sickTime = worldTime

    # set persons covid varient given varience rate
    def setVarient(self, sickPerson=1):
        if sickPerson == 1:
            self.covidVarient = 1
        else:
            self.covidVarient = sickPerson.covidVarient * MUTATION_RATE

    # checks time to get healed
    def checkRecovery(self, worldTime):
        if self.state == SICK:
            rtSickOffset = random() * RT_SICK_RANGE
        else:
            rtSickOffset = 0

        if worldTime - self.sickTime > RECOVERY_TIME + rtSickOffset:
            return True
        else:
            return False

    # checks for when no longer immune
    def checkForHealed(self, worldTime):
        if worldTime - self.timeOfHealed > IMMUNE_TIME:
            return True
        else:
            return False

    def chanceDeath(self):
        if random() < CHANCE_OF_Death:
            self.die = True



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

class Writer:
    def __init__(self, x,y) -> None:
        self.t = Turtle()
        self.t.ht()
        self.t.pu()
        self.t.goto(x,y)

    def write(self, text, dir, info = ("Arial", 20, "normal")):
         self.t.clear()
         self.t.write(text,False,dir, info)

def stats(turt):
    global amtExposed, infectedIndicies, amtImmune, strainList
    # strains = (*strainList, sep = ", ")
    turt.write(f"Stats\nExposed: {amtExposed}\nSick: {len(infectedIndicies)}\nImmune: {amtImmune}\nStrains: {strainList}", "left")

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

writeTitle = Writer(0, LENGTH*2/3)
writeTitle.write("COVID-19 VARIANCE MODEL", "center", ("Arial", 40, "normal"))

writeDay = Writer(-LENGTH/2, LENGTH/2)
writeDay.write(f"Day: {day}", "left")

writePeople = Writer(LENGTH/2, LENGTH/2)
writePeople.write(f"Number of People: {PEOPLE_AMT}", "right")

writeStats = Writer(-LENGTH/2, -LENGTH/2 - 120)
stats(writeStats)

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






people = list()
# people = np.array([], object)
for i in range(PEOPLE_AMT):
    p = Person(randint(-LENGTH/2, LENGTH/2),
               randint(-LENGTH/2, LENGTH/2), i)
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
                    stats(writeStats)

                    if p.state == SICK:
                        p.chanceDeath()

            # no longer immune to current strain
            elif p.state == RECOVERY:
                if p.checkForHealed(worldTime):
                    p.updateState(HEALTHY)
                    p.currentStrain = -1
                    amtImmune -= 1
                    stats(writeStats)

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
                stats(writeStats)
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
                            stats(writeStats)

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
                                        stats(writeStats)
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
