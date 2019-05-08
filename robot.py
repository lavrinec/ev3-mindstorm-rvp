#!/usr/bin/env python3

import os
import sys
import time
import ev3dev.ev3 as ev3
from urllib.request import urlopen
import json

# state constants
ON = True
OFF = False
leftWheel = ev3.LargeMotor('outA')
rightWheel = ev3.LargeMotor('outC')
gyro = ev3.GyroSensor() 
color = ev3.ColorSensor() 
units = gyro.units
position = None
start = None
saving = []
wheelCirc = 0.17593 # in meters

integral = 0
e_old = 0
t_old = time.time()

# robot position on the grid
ev3x = 0
ev3y = 0
ev3Facing = 0 # north, south, east, west orientation

# Print debug messages to stderr
def debug_print(*args, **kwargs):
    print(*args, **kwargs, file=sys.stderr)


# Resets the console to the default state
def reset_console():
    print('\x1Bc', end='')


# Turn the cursor on or off
def set_cursor(state):
    if state:
        print('\x1B[?25h', end='')
    else:
        print('\x1B[?25l', end='')


# Sets the console font
def set_font(name):
    os.system('setfont ' + name)


# read gyro angle
def read_angle():
    angle = gyro.value()
    # print("Kot: ", str(angle) + " " + units)
    # debug_print("Kot: ", str(angle) + " " + units)
    return angle


# reset gyro
def reset_gyro():
    gyro.mode='GYRO-RATE'
    gyro.mode='GYRO-ANG'
    color.mode='COL-COLOR'


# read color sensor
def read_color():
    col = color.value()
    print("Barva: ", col)
    debug_print("Barva: ", col)
    return col


# read and parse map
def read_map():
    global start
    global ev3x
    global ev3y
    # url = "http://192.168.0.100/zemljevid.json"
    # url = "http://192.168.1.86/zemljevid.json"
    # url = "http://192.168.2.5/zemljevid.json"
    url = "http://192.168.0.200:8080/zemljevid.json"
    r = urlopen(url)
    data = json.loads(r.read().decode(r.info().get_param('charset') or 'utf-8'))
    position = data["start"]
    start = data["start"]
    saving.append(data["oseba1"])
    saving.append(data["oseba2"])
    saving.append(data["oseba3"])
    saving.append(data["oseba4"])
    debug_print(data)
    #map ni na voljo, naredi svoj primer
    
    """
    start = [0,0]
    saving.append([0,4])
    # saving.append([3,3])
    saving.append([4,1])
    """
    ev3x = start[0]
    ev3y = start[1]

def reset_for_pid():
    global e_old
    global integral
    global t_old
    integral = 0
    e_old = 0
    t_old = time.time()

# PID
def pid(Kp, Ki, Kd, angle_wanted):
    global e_old
    global integral
    global t_old
    angle = -read_angle()
    t = time.time()
    e = angle_wanted - angle
    delta_e = e - e_old
    delta_t = t - t_old
    
    P = Kp * e
    I = Ki * integral
    D = Kd * delta_e / delta_t
    u = P + I + D

    e_old = e
    t_old = t
    integral += e * delta_t

    #debug_print(angle," ",e," ",t)

    return u



# stop all motors
def stop_motors():
    leftWheel.stop(stop_action='hold')
    rightWheel.stop(stop_action='hold')
    time.sleep(0.5)
    # reset_gyro()
    time.sleep(0)


# turning left or right
def turn(left):
    cilj = -90
    if left:
        cilj = 90
        debug_print("obracam levo")
    else:
        debug_print("obracam desno")
    change_angle(cilj)

def change_angle(cilj):
    counter = 0
    speed_base = 100
    reset_for_pid()
    while True:
        u = pid(5,0,0,cilj) #pid(5,0,0,cilj)

        if u > speed_base:
            u = speed_base
        if u < -speed_base:
            u = -speed_base

        leftWheel.run_forever(speed_sp= -u)
        rightWheel.run_forever(speed_sp= u)

        angle = read_angle()

        # t = time.time()
        # debug_print(angle," ",t)
        if angle == -cilj:
           # stop_motors()
           # break
           counter += 1
        else:
            counter = 0

        if counter > 10:
            stop_motors()
            break

# going forward for cm
def drive_cm(cm):
    global ev3Facing
    debug_print("peljem naprej za ", cm, "cm")
    speed_base = 200
    reset_for_pid()
    leftWheel.position = 0
    # rightWheel.position = 0

    while True:
        u = pid(8,1,0,ev3Facing) #pid(8,1,0,0)

        if u > speed_base:
            u = speed_base
        if u < -speed_base:
            u = -speed_base

        # mogoce le nastavi speed brez se enega klica run_forever
        leftWheel.run_forever(speed_sp=speed_base - u)
        rightWheel.run_forever(speed_sp=speed_base + u)

        if abs(leftWheel.position * wheelCirc/3.60) > abs(cm):
            stop_motors()
            break


# go to coordinates of person
def robot_go_to(person):
    global ev3x
    global ev3y
    global ev3Facing

    debug_print("sem na [",ev3x,",",ev3y,"] obrnjen proti ",ev3Facing)
    debug_print("tarca je na ",person)

    # get required moves from ev3 pos to person
    moveX = person[0] - ev3x
    moveY = person[1] - ev3y

    debug_print("moja pot je: x ", moveX," y ",moveY)
    angle = read_angle()
    print("kot1: ", angle)

    # rotate for appropriate y direction
    if moveY > 0: # person is to the south
        debug_print("tarca je proti jugu")
        ev3Facing = -90
    
    if moveY < 0: # person is to the north
        debug_print("tarca je proti severu")
        ev3Facing = 90

    if moveY != 0:
        change_angle(ev3Facing)

    print("kot2: ", read_angle())

    # move square by square in y direction
    ev3y += moveY
    drive_cm(abs(moveY))
    print("kot3:", read_angle())
    """
    for y in range(0, int(abs(moveY)/10)):
        debug_print("sem na [",ev3x,",",ev3y,"] obrnjen proti ",ev3Facing)
        drive_cm(10)
        if moveY < 0:
            ev3y = ev3y - 10
        else:
            ev3y = ev3y + 10
    """

    # rotate for appropriate x direction
    if moveX < 0: # person is to the west
        debug_print("tarca je proti zahodu")
        ev3Facing = 180
    
    if moveX > 0: # person is to the east
        debug_print("tarca je proti vzhodu")
        ev3Facing = 0

    if moveX != 0:
        change_angle(ev3Facing)

    print("kot4:", read_angle())

    # move square by square in x direction
    ev3x += moveX
    drive_cm(abs(moveX))

    print("kot5:", read_angle())
    """
    for x in range(0, int(abs(moveX)/10)):
        debug_print("sem na [",ev3x,",",ev3y,"] obrnjen proti ",ev3Facing)
        drive_cm(10)
        if moveX < 0:
            ev3x = ev3x - 10
        else:
            ev3x = ev3x + 10
    """


# go rescue all people
def go_rescue():
    while saving:
        person = saving.pop()

        robot_go_to(person)

        color = read_color()
        if color == 3 or color == 5 or color == 2: # alive or damaged
            debug_print("Rescue this one")
            robot_go_to(start)
        else:
            debug_print("Dead")

        
# The main function of our program'
def main():
    # set the console just how we want it
    reset_console()
    set_cursor(OFF)
    set_font('Lat15-Terminus24x12')
    print("executing program")

    reset_gyro()
    read_map()

    leftWheel.ramp_up_sp = 2500
    rightWheel.ramp_up_sp = 2500

    debug_print("----------RESUJEM---------")
    go_rescue()
    robot_go_to(start)


if __name__ == '__main__':
    main()
