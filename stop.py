#!/usr/bin/env python3

import os
import sys
import time
import ev3dev.ev3 as ev3

def main():
    mLeft = ev3.LargeMotor('outA')
    mRight = ev3.LargeMotor('outC')

    mLeft.stop()
    mRight.stop()
    mLeft.reset()
    mRight.reset()

if __name__ == '__main__':
    main()