#!/usr/bin/env python3

import os
import sys
import time
import ev3dev.ev3 as ev3

def debug_print(*args, **kwargs):
    '''Print debug messages to stderr.

    This shows up in the output panel in VS Code.
    '''
    print(*args, **kwargs, file=sys.stderr)

def main():
    mLeft = ev3.LargeMotor('outA')
    mRight = ev3.LargeMotor('outC')

    mLeft.reset()
    mRight.reset()

    mLeft.ramp_up_sp = 500
    mRight.ramp_up_sp = 500

    mLeft.run_forever(speed_sp=0)
    mRight.run_forever(speed_sp=0)
    mLeft.run_forever(speed_sp=100)
    mRight.run_forever(speed_sp=100)

    # move 10 cm
    path = 0 # in meters
    wheelCirc = 0.17593 # in meters
    while path <= 0.1: # drive 10 cm
        a = mLeft.position
        b = mRight.position
        debug_print("leftWheel= ",a," rightWheel= ",b) # degrees

        path = (a*wheelCirc)/360
    mLeft.stop(stop_action="hold") # forcefull break
    mRight.stop(stop_action="hold")

if __name__ == '__main__':
    main()