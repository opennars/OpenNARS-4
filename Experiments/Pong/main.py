
"""
This is an experiment to let NARS play the pong game.
The speed of the bat is two times faster than the ball, the system does not need to predict future positions of the ball.
We are still debugging the system, and it does not work now. The system failed to track the ball.
I guess this is because something is wrong in the implementation of the control part.
Don't use this file for the moment.
"""
import os
import time
from random import randint
def CLEAR_SCREEN(): os.system('cls' if os.name == 'nt' else 'clear')
def SLEEP(ms=20): time.sleep(ms/1000)


from pynars.Narsese import Task, Judgement, Term, Stamp, Base
from pynars.NARS import Reasoner



ball_right = False
ball_left = False
good = False
pong_left_executed = False
t_pong_executed = -9999
pong_right_executed = False


def set_ball_left():
    global ball_left
    global ball_right
    ball_left = True
    ball_right = False


def set_ball_right():
    global ball_left
    global ball_right
    ball_left = False
    ball_right = True


def pong_left(args, task: Task, mem):
    global pong_left_executed
    global t_pong_executed
    t_now = task.stamp.t_occurrence
    if t_now > t_pong_executed:
        pong_left_executed = True
        t_pong_executed = t_now


def pong_right(args, task: Task, mem):
    global pong_right_executed
    global t_pong_executed
    t_now = task.stamp.t_occurrence
    if t_now > t_pong_executed:
        pong_right_executed = True
        t_pong_executed = t_now


nars = Reasoner(100, 100, record=True)

iterations = -1

print(">>NAR Pong start")
nars.register_operator("move_left", pong_left)
nars.register_operator("move_right", pong_right)

"""Prior knowledge"""
nars.input_narsese("<(&/, ball_left, ^move_left) =/> hit>.")
nars.input_narsese("<(&/, ball_right, ^move_right) =/> hit>.")

# nars.input_narsese("(^move_left, {SELF})! :|:", True)
# nars.cycles(1)
# print(1000)
# nars.cycles(1000)
# exit()

"""Game status"""
szX: int = 50
szY: int = 20
ballX: int = szX//2
ballY: int = szY//5
batX: int = 20
batVX: int = 0
batWidth: int = 4  # "radius", batWidth from middle to the left and right
vX: int = 1
vY: int = 1
hits: int = 0
misses: int = 0
t: int = 0

"""Run"""
try:
    while True:
        if t > iterations and iterations != -1:
            break
        t += 1

        """Print the screen"""
        CLEAR_SCREEN()

        print(f"{'':<{max(batX-batWidth+1, 0)}}", end='')
        print("@"*batWidth*2)

        for i in range(ballY):
            print(f"{'':<{szX}}", end='|\n')

        print(f"{'':<{ballX}}", end='#')
        print(f"{'':<{szX-(ballX+1)}}", end='|\n')

        for i in range(ballY+1, szY):
            print(f"{'':<{szX}}", end='|\n')

        """Update status"""
        if batX < ballX:
            set_ball_right()
        if ballX < batX:
            set_ball_left()

        if ballX <= 0:
            vX = 1
        if ballX >= szX-1:
            vX = -1
        if ballY <= 0:
            vY = 1
        if ballY >= szY-1:
            vY = -1

        ballX += vX
        ballY += vY

        good = False
        if ballY == 0:
            if abs(ballX-batX) <= batWidth:
                good = True
                print("good")
                hits += 1
            else:
                print("bad")
                misses += 1

        if ballY == 0: # or ballX == 0 or ballX >= szX-1:
            ballY = szY//2+randint(0, szY//2-1)
            ballX = randint(0, szX-1)
            vX = 1 if randint(0, 1) == 0 else -1

        if pong_left_executed:
            pong_left_executed = False
            print("Exec: move_left")
            batVX = -2

        if pong_right_executed:
            pong_right_executed = False
            print("Exec: move_right")
            batVX = 2

        batX = max(0, min(szX-1, batX+batVX*batWidth//2))

        """Print info"""
        print(f"Hits={hits} misses={misses} ratio={((hits) / ( hits + misses)) if hits+misses>0 else 0.0} time={t}")
        if iterations == -1:
            SLEEP(10)
        
        if ball_right:
            print("ball_right")
            nars.input_narsese("ball_right. :|:")
        if ball_left:
            print("ball_left")
            nars.input_narsese("ball_left. :|:")
        nars.input_narsese("hit! :|:", True)
        if good:
            nars.input_narsese("hit. :|:")

        nars.cycles(250)

        nars.input_narsese("<(&/, ball_left, ^move_left) =/> hit>.")
        nars.input_narsese("<(&/, ball_right, ^move_right) =/> hit>.")
except KeyboardInterrupt:
    pass