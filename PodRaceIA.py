
# -*- coding: Utf-8 -*- 
import sys
import random 
import math

debug = True
player = 1
NB_PODS = 3
WIDTH = 100
HEIGHT = 100
pods = []
walls = []
checkpoints = []
MAX_TRUST = 100
EXPO = 1.2
MAX_SPEED = 1000
MIN_SPEED = 1



def next_input_must_be(value):
    if input() != value:
        print("expected input was '",value,"'", sep="")
        if debug:print("expected input was '",value,"'", sep="",file=sys.stderr)
        quit()

def read_dimensions(parts):
    global WIDTH
    global HEIGHT
    WIDTH = int(parts[1])
    HEIGHT = int(parts[2])


def read_nb_pods(parts):
    global NB_PODS
    NB_PODS = int(parts[1])
    if debug:print("nb pods : ", NB_PODS, file=sys.stderr)
 

def read_list_of_circles(parts):
    nb = int(parts[1])
    l = []
    for i in range(nb):
        x,y,r = map(int, input().split())
        l.append({
            "x":x,
            "y":y,
            "radius":r,
            })
    return l

def read_walls(parts):
    global walls
    walls = read_list_of_circles(parts)

def read_checkpoints(parts):
    global checkpoints
    checkpoints = read_list_of_circles(parts)
    if debug:print("checkpoints : ", checkpoints, file=sys.stderr)




def dot(a,b):
    return sum(x*y for x,y in zip(a,b))



def get_turn(pod, cp):
        vec = (cp["x"]-pod["x"],cp["y"]-pod["y"])
        angle = (360+math.degrees(math.atan2(vec[1], vec[0])))%360
        return -(pod["dir"]-angle)/2
    

def get_trust(pod, cp):
        vec = (cp["x"]-pod["x"],cp["y"]-pod["y"])
        normvec = .00001+dot(vec,vec)**.5
        vec = (vec[0]/normvec,vec[1]/normvec)
        speed = (pod["vx"],pod["vy"])
        normspeed = .00001+dot(speed,speed)**.5
        speed = (speed[0]/normspeed,speed[1]/normspeed)
        if dot(vec, speed) > 0.5:
            if normspeed > MAX_SPEED:
                return 0
            if normspeed < MIN_SPEED:
                return MAX_TRUST
        trust = normvec**EXPO
        if trust > MAX_TRUST:
            return MAX_TRUST
        return trust
    


def check(i):
    pod = pods[i]
    cp = checkpoints[cur_cp[i]]
    vec = (cp["x"]-pod["x"],cp["y"]-pod["y"])
    if dot(vec, vec) < cp["radius"]**2:
        cur_cp[i]+=1



if len(sys.argv)>1:
    MAX_TRUST = float(sys.argv[1])
if len(sys.argv)>2:
    EXPO = float(sys.argv[2])
if len(sys.argv)>3:
    MIN_SPEED = float(sys.argv[3])
if len(sys.argv)>4:
    MAX_SPEED = float(sys.argv[4])


settings = {
    "DIMENSIONS":read_dimensions,
    "WALLS":read_walls,
    "CHECKPOINTS":read_checkpoints,
    "NB_PODS":read_nb_pods
}

next_input_must_be("START player")
player = int(input())
next_input_must_be("STOP player")


next_input_must_be("START settings")
line = input()
while line != "STOP settings":
    parts = line.split()
    settings[parts[0]](parts)
    line = input()
    
pods = []
cur_cp = [0]*NB_PODS
turn = 1
while True:
    next_input_must_be("START turn")
    end = "STOP turn"
    pods = []
    line = input()
    while line != end:
        play,pod,x,y,vx,vy,direction, health = map(float, line.split())

        if debug:print(play,pod,x,y,vx,vy,direction, health, file=sys.stderr)
        if play == player:
            pods.append({
                "x":x,
                "y":y,
                "vx":vx,
                "vy":vy,
                "dir":direction,
                "health":health
                }) 
        line = input()

    if debug:print(pods, file=sys.stderr)
    if debug:print(checkpoints, file=sys.stderr)
        
    print("START action")
    for i in range(NB_PODS):
        check(i)
        if debug:print("debug IA : ",get_turn(pods[i], checkpoints[cur_cp[i]]),
             get_trust(pods[i], checkpoints[cur_cp[i]]), end=";", file=sys.stderr)
        
        print(get_turn(pods[i], checkpoints[cur_cp[i]]),
             get_trust(pods[i], checkpoints[cur_cp[i]]), end=";")
        
    print("")
    print("STOP action")
    turn += 1
    