#!/usr/bin/env python3

import os
import sys
import time
import ev3dev.ev3 as ev3
from urllib.request import urlopen
import json
import math
from threading import Thread

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
drivingDirection = 1

integral = 0
e_old = 0
t_old = time.time()
rescuing = None

# robot position on the grid
ev3x = 0
ev3y = 0
ev3Facing = 0 # north, south, east, west orientation
falling = 0
missed = False

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
    url = "http://192.168.2.7/zemljevid.json"
    # url = "http://192.168.0.200:8080/zemljevid.json"
    r = urlopen(url)
    data = json.loads(r.read().decode(r.info().get_param('charset') or 'utf-8'))
    position = data["start"]
    start = data["start"]
    saving.append(data["oseba1"])
    saving.append(data["oseba2"])
    saving.append(data["oseba3"])
    saving.append(data["oseba4"])
    saving.append(data["oseba5"])
    saving.append(data["oseba6"])
    saving.append(data["oseba7"])
    saving.append(data["oseba8"])
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
    angle = read_angle()
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

    # debug_print(angle," ",t)

    return u



# stop all motors
def stop_motors():
    leftWheel.stop(stop_action='hold')
    rightWheel.stop(stop_action='hold')
    time.sleep(0.5)
    # reset_gyro()
    # time.sleep(0)


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

        leftWheel.run_forever(speed_sp= u)
        rightWheel.run_forever(speed_sp= -u)

        angle = read_angle()

        # t = time.time()
        # debug_print(angle," ",t)
        if angle == cilj:
           counter += 1
        else:
            counter = 0

        if counter > 10:
            stop_motors()
            break

# going forward for cm
def drive_cm(cm):
    global ev3Facing
    global drivingDirection
    global missed
    debug_print("peljem naprej za ", cm, "cm")
    speed_base = 200
    reset_for_pid()
    leftWheel.position = 0
    # rightWheel.position = 0
    running = False
    while True:
        u = pid(10,5,1,ev3Facing) #pid(8,1,0,0)

        if u > speed_base:
            u = speed_base
        if u < -speed_base:
            u = -speed_base

        # mogoce le nastavi speed brez se enega klica run_forever
        if(running):
            leftWheel.speed_sp = ((speed_base + u) * drivingDirection)
            rightWheel.speed_sp = ((speed_base - u) * drivingDirection)
        else:
            leftWheel.run_forever(speed_sp=((speed_base + (u*drivingDirection)) * drivingDirection))
            rightWheel.run_forever(speed_sp=((speed_base - (u * drivingDirection)) * drivingDirection))
            # running = True

        distance = abs(leftWheel.position * wheelCirc/3.60)

        if missed:
            if distance < 8:
                if colorize(False):
                    return False
            else:
                missed = False


        if distance > abs(cm):
            stop_motors()
            return True


def optimize_angle(wanted, current):
    global drivingDirection
    drivingDirection = 1
    mod = 90
    if current < 0:
        mod = -90
    current = round(current,-1) 
    rounded = current % mod
    current -= rounded
    minimized = current % 360
    distance = wanted - minimized
    if abs(distance) == 180:
        drivingDirection *= -1
        debug_print("Spreminjam drivingDirection v ", drivingDirection)
        return current
    elif distance > 180:
        debug_print("+90")
        if(current > 180):
            drivingDirection *= -1
            return (current + 90)
        return (current - 90)
    elif distance < -180:
        debug_print("-90")
        if(current < -180):
            drivingDirection *= -1
            return (current - 90)
        return (current + 90)
    else:
        debug_print("distance ", distance, wanted, minimized)
        return (current + distance)

# go to coordinates of person
def robot_go_to(person):
    global ev3x
    global ev3y
    global ev3Facing
    global falling

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
        ev3Facing = 90
    
    if moveY < 0: # person is to the north
        debug_print("tarca je proti severu")
        ev3Facing = 270

    if moveY != 0:
        debug_print("optimiziraj ", ev3Facing)
        ev3Facing = optimize_angle(ev3Facing,angle)
        if(ev3Facing + 5 < angle):
            falling += 1
            if(falling % 2 == 0):
                ev3Facing -= 1
        debug_print("sem na kotu ", angle, " in zelim biti na ", ev3Facing)
        change_angle(ev3Facing)
        angle = read_angle()

    print("kot2: ", read_angle())

    # move square by square in y direction
    
    if drive_cm(abs(moveY)):
        ev3y += moveY
    else:
        return
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
        debug_print("optimiziraj ", ev3Facing)
        ev3Facing = optimize_angle(ev3Facing,angle)
        if(ev3Facing + 5 < angle):
            falling += 1
            if(falling % 2 == 0):
                ev3Facing -= 1
        debug_print("sem na kotu ", angle, " in zelim biti na ", ev3Facing)
        change_angle(ev3Facing)

    print("kot4:", read_angle())

    # move square by square in x direction
    
    if drive_cm(abs(moveX)):
        ev3x += moveX

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
    debug_print("sem na cilju [",ev3x,",",ev3y,"] obrnjen proti ",ev3Facing)

def dead_beep():
    ev3.Sound.tone(1500,1000).wait()
    time.sleep(0.5)
    ev3.Sound.tone(1500,1000).wait()
    time.sleep(0.5)
    ev3.Sound.tone(1500,1000).wait()

def colorize(set_missed):
    global missed
    color = read_color()
    if color == 2: # modra
        stop_motors()
        if missed and not set_missed:
            saving.append(rescuing)
        missed = False
        ev3.Sound.tone(1500,1000).wait()
    if color == 7: # rumena
        stop_motors()
        if missed and not set_missed:
            saving.append(rescuing)
        missed = False
        ev3.Sound.tone(1500,1000).wait()
        time.sleep(1)
        ev3.Sound.tone(1500,1000).wait()
    if color == 3 or color == 7 or color == 2: # alive or damaged
        debug_print("Rescue this one")
        robot_go_to(start)
        ev3.Sound.tone(1500,2000).wait()
        return True
    else:
        if color == 5:
            missed = False
            thread = Thread(target = dead_beep)
            thread.start()
        elif set_missed:
            missed = True
        debug_print("Dead ", color)
        return False

# go rescue all people
def go_rescue():
    global rescuing
    while saving:
        saving.sort(key = lambda p: math.sqrt((p[0] - ev3x)**2 + (p[1] - ev3y)**2))
        debug_print("Seznam: ", saving)
        # time.sleep( 10 )
        rescuing = saving.pop(0)

        robot_go_to(rescuing)

        colorize(True)


def test_pid():
    reset_gyro()
    drive_cm(50)
    angle = read_angle()
    t = time.time()
    debug_print(angle," ",t)
    debug_print("Zavijam za 180")
    reset_gyro()
    time.sleep(1)
    ev3Facing = 180
    change_angle(ev3Facing)
    t = time.time()
    angle = read_angle()
    debug_print(angle," ",t)


# The main function of our program'
def main():
    # set the console just how we want it
    reset_console()
    set_cursor(OFF)
    set_font('Lat15-Terminus24x12')
    # return test_pid()
    print("executing program")

    reset_gyro()
    read_map()

    leftWheel.ramp_up_sp = 4500
    rightWheel.ramp_up_sp = 4500

    debug_print("----------RESUJEM---------")
    # ev3.Sound.tone(1500,2000).wait()
    # global ev3Facing
    # global drivingDirection
    # drivingDirection = -1
    # i = 0
    # while(True):
    #     i += 1
    #     drive_cm(40)
    #     ev3Facing -= 986;
    #     change_angle(ev3Facing)
    #     print(read_angle())
    #     debug_print(read_angle())


    go_rescue()
    robot_go_to(start)
    ev3Facing = 0
    change_angle(ev3Facing)


if __name__ == '__main__':
    main()
