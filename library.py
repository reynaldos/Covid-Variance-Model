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
STEP_DIST = 4  # step distance per loop iteration
SICK_STEP_OFFSET = STEP_DIST - 2
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
CHANCE_OF_DEATH = .1  # percent chance of dying
NEW_MUTUATION_LIMIT = .6  # percent at which virus mutates
STARTING_COVID_STRAIN = "A"
strainList = [STARTING_COVID_STRAIN]


# person class that holds logic for people in the simulation
class Person():
    def __init__(self, x, y, ID, legend= False):
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
        # legend if self.turt.fd(0) else self.turt.rt(randint(0,360))

    # prints out person's info
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
            self.turt.fd(SICK_STEP_OFFSET)
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
        return worldTime - self.timeOfHealed > IMMUNE_TIME

    def chanceDeath(self):
        if random() < CHANCE_OF_DEATH:
            self.die = True


# class for writing text to screen
class Writer:
    def __init__(self, x,y) -> None:
        self.t = Turtle()
        self.t.ht()
        self.t.pu()
        self.t.goto(x,y)

    def write(self, text, dir, info = ("Arial", 20, "normal")):
         self.t.clear()
         self.t.write(text,False,dir, info)

# writes stats to screen
def stats(turt, values):
    # global amtExposed, infectedIndicies, amtImmune, strainList
    # strains = (*strainList, sep = ", ")
    turt.write(f"Stats\nExposed: {values[0]}\nSick: {values[1]}\nImmune: {values[2]}\nStrains: {values[3]}", "left")