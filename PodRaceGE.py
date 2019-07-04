import sys
import math
import random
from itertools import chain

visu = "display" in sys.argv
try : 
    import numpy as np
    import cv2
except Exception as e:
    print(e, file=sys.stderr)
    visu = False

NB_PODS = 3
POD_RADIUS = 10
FRICTION = 0.005
WIDTH = 800
HEIGHT = 800
TIME = 1
MAX_TRUST = 100
MAX_TURN = 15

def next_input_must_be(value):
    val = input()
    if val != value:
        print("expected input was '%s' instead of '%s'"%(value, val), file=sys.stderr)
        quit()


def sub(a,b):
    return [x-y for x,y in zip(a,b)]

def prod(a,b):
    return [x*y for x,y in zip(a,b)]


def dot(a,b):
    return sum(x*y for x,y in zip(a,b))


def get_arg(args, kwargs, pos, key, default):
    if pos < len(args):
        return args[pos]
    if key in kwargs:
        return kwargs[key]
    return default


class Element:
    def __init__(self,*args, **kwargs):
        self.x      = get_arg(args, kwargs, 0, "x",      0)
        self.y      = get_arg(args, kwargs, 1, "y",      0)
        self.radius = get_arg(args, kwargs, 2, "radius", 0)
        self.vx     = get_arg(args, kwargs, 3, "vx",     0)
        self.vy     = get_arg(args, kwargs, 4, "vy",     0)
        self.mass   = get_arg(args, kwargs, 5, "mass",   0)

    def get_velocity(self):
        return (self.vx, self.vy)

    def get_position(self):
        return (self.x, self.y)

    def collid_time(self, el):
        p1 = self.get_position()
        v1 = self.get_velocity()
        p2 = el.get_position()
        v2 = el.get_velocity()
        r1 = self.radius
        r2 = el.radius
        a = dot(v1,v1) + dot(v2,v2) - 2*dot(v1,v2)
        b = 2*(dot(p1,v1) + dot(p2,v2) - dot(p1,v2) - dot(p2,v1))
        c = dot(p1,p1) + dot(p2, p2) - 2*dot(p1,p2) - (r1+r2)**2
        delta = b**2-4*a*c
        if delta < 0 : return -1
        try:
            delta = delta**.5
            t1 = (- b - delta)/(2*a)
            t2 = (- b + delta)/(2*a)
            if t1 >= 0 : return t1
            return t2
        except:
            return -1


    #from http://www.vobarian.com/collisions/2dcollisions2.pdf
    def impact_redirection(self, el):
        p1 = self.get_position()
        v1 = self.get_velocity()
        p2 = el.get_position()
        v2 = el.get_velocity()
        m1 = self.mass
        m2 = el.mass
        n = sub(p2,p1)
        unorm = dot(n,n)**.5
        un = (n[0]/unorm, n[1]/unorm)
        ut = (-un[1], un[0])
        v1n = dot(un,v1)
        v2n = dot(un,v2)
        v1t = dot(ut,v1)
        v2t = dot(ut,v2)
        v1nf = (v1n*(m1-m2)+2*m2*v2n)/(m1+m2)
        v2nf = (v2n*(m2-m1)+2*m1*v1n)/(m1+m2)
        self.vx = v1nf*un[0]+v1t*ut[0]
        self.vy = v1nf*un[1]+v1t*ut[1]
        el.vx = v2nf*un[0]+v2t*ut[0]
        el.vy = v2nf*un[1]+v2t*ut[1]





    def intersect(self, el):
        return (self.x-el.x)**2+(self.y-el.y)**2<(self.radius+el.radius)**2

        

    def contains_center(self, el):
        return (self.x-el.x)**2+(self.y-el.y)**2<(self.radius)**2

    def update_velocity(self, time, acc):
        self.vx += acc[0]*time
        self.vy += acc[1]*time

    def update_position(self, time):
        self.x += self.vx*time
        self.y += self.vy*time


    def __str__(self):
        return "El"+"("+str(self.x)+","+str(self.y)+")"


pods = []
walls = []
checkpoints = []

class Pod(Element):
    def __init__(self, *args,**kwargs):
        Element.__init__(self,*args,**kwargs)
        self.direction = get_arg(args, kwargs, 6, "direction", 0)
        self.player = get_arg(args, kwargs, 7, "player", 1)
        self.next_check = 0



    def check_win(self):
        if self.next_check >= len(checkpoints):
            return True
        while checkpoints[self.next_check].contains_center(self):
            self.next_check+=1
            if self.next_check >= len(checkpoints):
                return True
        return False

    def turn(self, deg):
        self.direction+=deg

    def trust(self, power):
        angle = math.radians(self.direction)
        acc = (math.cos(angle)*power, math.sin(angle)*power)
        self.update_velocity( 0.01, acc)


    def friction(self, time):
        vel = self.get_velocity()
        norm = dot(vel, vel)**.5
        try:
            fri = [(time*FRICTION*x)/norm for x in vel]
            fri = [f if abs(f) < abs(v) else v for f,v in zip(fri, vel)]
            self.vx-=fri[0]
            self.vy-=fri[1]
        except:
            pass

    @property
    def color(self):
        colors = [(0,255,0),(0,0,255),(255,0,0),(255,0,255),(0,255,255),(255,255,0)]
        return colors[self.player-1]

    def draw(self, img):
        c = self.color
        cv2.circle(img,(int(self.x), int(self.y)), self.radius+1, (200,200,200) , -1)
        cv2.circle(img,(int(self.x), int(self.y)), self.radius, c , 2)
        rad = math.radians(self.direction)
        cv2.line(img,
                (int(self.x), int(self.y)), 
                (int(self.x+math.cos(rad)*self.radius), int(self.y+math.sin(rad)*self.radius)),c,2)
        
        cv2.putText(img,str(self.next_check),(int(self.x+self.radius), int(self.y-self.radius)), font, .5,c,2)

    def __str__(self):
        return "POD"+str(self.player)+"("+str(self.x)+","+str(self.y)+")"

    def __repr__(self):
        return "POD"+str(self.player)+"("+str(self.x)+","+str(self.y)+")"



def bounded(v,m,M):
    if v < m:return m
    if v > M:return M
    return v

def player_action(player, action):
    actions = action.split(";")
    try : 
        for i,act in enumerate(actions):
            deg, p = [float(s) for s in act.split() if s.strip()]
            deg = bounded(deg, -MAX_TURN, MAX_TURN)
            p = bounded(p, 0,MAX_TRUST)
            pods[player-1][i].turn(deg)
            pods[player-1][i].trust(p)
    except Exception as e:    
        print(e, file=sys.stderr)




def init_game(nb):
    global pods
    starts = [x for n in range(NB_PODS) for x in range(1, nb+1)]
    random.shuffle(starts)
    pods = [[] for i in range(nb)]
    x = POD_RADIUS*2
    y = POD_RADIUS*2
    for i in starts:
        pods[i-1].append(Pod(x,y,POD_RADIUS, 0,0,mass=1, player=i))
        y+=POD_RADIUS*4
        if y > HEIGHT - POD_RADIUS*2:
            y = POD_RADIUS*2
            x+= POD_RADIUS*4
            
    for i in range(random.randint(0,10)):
        walls.append(Element(random.randint(100,WIDTH),
                            random.randint(0,HEIGHT),
                            random.randint(0,WIDTH/10),
                            mass=1000000))

   

    nb_checks =  random.randint(1,10)
    while len(checkpoints) < nb_checks:
        radius = random.randint(10,WIDTH/20)
        e = Element(random.randint(100+radius,WIDTH-radius),
                            random.randint(radius,HEIGHT-radius),
                            random.randint(10,WIDTH/20),
                            mass=1000000)
       
        for o in chain(*pods, walls, checkpoints):
            if e.intersect(o):
                break
        else:
            checkpoints.append(e)
    


collisions = False
def update_game():
    global collisions
    collisions = False

    time = 0
    mt = TIME
    while time+0.01<TIME:
        mt = TIME-time
        pod, elem = None, None
        for p in chain(*pods):
            for o in chain(*pods, walls):
                if o == p:
                    continue
                t = p.collid_time(o)
                if t >= 0 and t < mt:
                    collisions = False
                    mt = t
                    pod = p
                    elem = o
        
        for p in chain(*pods):
            p.update_position(mt-0.001)
            p.friction(mt)
            p.check_win()
        time+=mt
        if pod:
            print("impact between", pod, "and", elem, file=sys.stderr)
            pod.impact_redirection(elem)            
        pod,elem = None, None

    winner = 0
    for player, plist in enumerate(pods,1):
        for p in plist:
            if p.check_win():
                winner = player
    return winner




#initialize visualization if possible
if visu:
    font = cv2.FONT_HERSHEY_SIMPLEX
    img = np.zeros((HEIGHT, WIDTH, 3), np.uint8)
    img[:, :] = [255, 255, 255]
    cv2.circle(img,(50, 100), 5, (0,255,0), -1)
    cv2.imshow('POD',img)
    cv2.waitKey(10)



def display_game(winner=0):

    if not visu:
        return
    img = np.zeros((HEIGHT, WIDTH, 3), np.uint8)
    if collisions:
        img[:, :] = [255, 155, 155]
    
    else:
        img[:, :] = [255, 255, 255]
    for w in walls:
        cv2.circle(img,(int(w.x), int(w.y)), w.radius, (0,0,0), -1)
    for index,c in enumerate(checkpoints):
        cv2.circle(img,(int(c.x), int(c.y)), c.radius, (100,100,100), 1)
        cv2.putText(img,str(index),(int(c.x), int(c.y)), font, 0.3,(100,100,100))
    for i,plist in enumerate(pods,1):
        for j,p in enumerate(plist,1):
            p.draw(img)
            cv2.putText(img,str(p.next_check),(int(j*20), int(i*20)), font, .5,p.color,2)
    if winner:
        cv2.putText(img,"WINNER : "+str(winner),(WIDTH//4, HEIGHT//2), font, 2,pods[winner-1][0].color,5)
        cv2.imshow('POD',img)
        return cv2.waitKey(-1)



    cv2.imshow('POD',img)
    return cv2.waitKey(1)
        














GE = True

if len(sys.argv) > 1 and sys.argv[1].lower() == "test":
    GE = False

try :
    if len(sys.argv)>1:
        NB_PODS = int(sys.argv[1])

except:
    pass


if GE : 
    #read number of players
    next_input_must_be("START players")
    players = int(input())
    next_input_must_be("STOP players")
    
    init_game(players)
    print("START settings")
    print("NB_PODS",NB_PODS)
    print("DIMENSIONS", WIDTH, HEIGHT)
    print("WALLS", len(walls))
    for w in walls:
        print(w.x,w.y,w.radius)
    print("CHECKPOINTS", len(checkpoints))
    for c in checkpoints:
        print(c.x,c.y,c.radius)
    print("STOP settings")


    turn = 1
    while True:
        winner = update_game()
        display_game(winner)
        for player in range(1,players+1):
            print("START turn %d %d"%(turn, player))
            if winner:
                print("WINNER",winner)
            else:
                for i,ppods in enumerate(pods,1):
                    for j,p in enumerate(ppods,1):
                        print("%d %d %d %d %.3f %.3f %d %d"%(i,j,p.x,p.y,p.vx,p.vy, p.direction,100))
            print("STOP turn %d %d"%(turn, player))
            next_input_must_be("START actions %d %d"%(turn, player))
            action = input()
            player_action(player, action)
            next_input_must_be("STOP actions %d %d"%(turn, player))
        if winner : 
            break
        turn += 1


else : 
    init_game(4)
    while True:
        update_game()
        k = display_game()
        for i,ppods in enumerate(pods,1):
                    for j,p in enumerate(ppods,1):
                        p.trust(10)
                        p.turn(1)
        if k > 0 : break
