#!/usr/bin/env python3
'''Hello to the world from ev3dev.org'''

import os
import sys
import time
import ev3dev.ev3 as ev3

# state constants
ON = True
OFF = False
leftWheel = ev3.LargeMotor('outA')
rightWheel = ev3.LargeMotor('outC')
gyro = ev3.GyroSensor() 
color = ev3.ColorSensor() 
units = gyro.units


def debug_print(*args, **kwargs):
    '''Print debug messages to stderr.

    This shows up in the output panel in VS Code.
    '''
    print(*args, **kwargs, file=sys.stderr)


def reset_console():
    '''Resets the console to the default state'''
    print('\x1Bc', end='')


def set_cursor(state):
    '''Turn the cursor on or off'''
    if state:
        print('\x1B[?25h', end='')
    else:
        print('\x1B[?25l', end='')


def set_font(name):
    '''Sets the console font

    A full list of fonts can be found with `ls /usr/share/consolefonts`
    '''
    os.system('setfont ' + name)


def main():
    '''The main function of our program'''
    # set the console just how we want it
    reset_console()
    set_cursor(OFF)

    # reset gyro
    gyro.mode='GYRO-RATE'
    gyro.mode='GYRO-ANG'
    color.mode='COL-COLOR'

    set_font('Lat15-Terminus24x12')

    # print something to the screen of the device
    print('Hello World!')

    # print something to the output panel in VS Code
    debug_print('Hello VS Code!')

    # moveForward(3600)

    # wait a bit so you have time to look at the display before the program
    # exits
    # time.sleep(2)

    readAngle()
    turn(True)
    readAngle()
    time.sleep(1)
    readAngle()
    time.sleep(1)
    readAngle()
    turn(False)
    readAngle()

    i = 0

    while i < 3:
        readAngle()
        col = color.value()
        print("Barva: ", col)
        debug_print("Barva: ", col)
        # ev3.Sound.tone(1000+angle*10, 1000).wait()
        time.sleep(1)
        i+=1

    ev3.Sound.beep()

def moveForward(time):
    leftWheel.run_timed(time_sp=time, speed_sp=500)
    
    rightWheel.run_timed(time_sp=time, speed_sp=500)

def turn(left):
    speed = 250
    milis = 1500
    if(left):
        rightWheel.run_timed(time_sp=milis, speed_sp=speed)
    else:
        leftWheel.run_timed(time_sp=milis, speed_sp=speed)
    time.sleep(milis/1000)

def readAngle():
    angle = gyro.value()
    print("Kot: ", str(angle) + " " + units)
    debug_print("Kot: ", str(angle) + " " + units)
    return angle

if __name__ == '__main__':
    main()
