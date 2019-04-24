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


# The main function of our program'
def main():
    # set the console just how we want it
    reset_console()
    set_cursor(OFF)
    set_font('Lat15-Terminus24x12')

    reset_gyro()
    read_map()

    leftWheel.ramp_up_sp = 1000
    rightWheel.ramp_up_sp = 1000

    go_rescue()

    # print something to the output panel in VS Code
    debug_print('Bye bye!')

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
    angle = read_angle()
    t = time.time()
    e = angle_wanted + angle
    delta_e = e - e_old
    delta_t = t - t_old
    
    P = Kp * e
    I = Ki * integral
    D = Kd * delta_e / delta_t
    u = P + I + D

    e_old = e
    t_old = t
    integral += e * delta_t

    return u

# stop all motors
def stop_motors():
    leftWheel.stop(stop_action='hold')
    rightWheel.stop(stop_action='hold')
    time.sleep(2)
    reset_gyro()
    time.sleep(2)


# turning left or right
def turn(left):
    cilj = -90
    counter = 0
    if left:
        cilj = 90
    speed_base = 300
    reset_for_pid()
    while True:
        u = pid(5,0,0,cilj)

        if u > speed_base:
            u = speed_base
        if u < -speed_base:
            u = -speed_base

        leftWheel.run_forever(speed_sp= -u)
        rightWheel.run_forever(speed_sp= u)

        angle = read_angle()
        if angle == -cilj:
            counter += 1
        else:
            counter = 0

        # debug_print(angle, cilj, counter)

        if counter > 10:
            stop_motors()
            break


# going forward for cm
def drive_cm(cm):
    speed_base = 500
    reset_for_pid()
    leftWheel.position = 0

    while True:
        u = pid(8,1,0,0)

        if u > speed_base:
            u = speed_base
        if u < -speed_base:
            u = -speed_base

        leftWheel.run_forever(speed_sp=speed_base - u)
        rightWheel.run_forever(speed_sp=speed_base + u)

        if abs(leftWheel.position * wheelCirc/3.60) > abs(cm):
            stop_motors()
            break


# go to coordinates
def robot_go_to(coordinate):
    # TODO implement
    debug_print('TODO')
    # TODO turn to right direction and drive cm


# go rescue all people
def go_rescue():
    while saving:
        person = saving.pop()
        debug_print(person)
        robot_go_to(person)
        color = read_color()
        turn(len(saving) % 2 == 0)
        drive_cm(40)
        if color == 1 or color == 2: # alive or damaged
            robot_go_to(start)
        


if __name__ == '__main__':
    main()
