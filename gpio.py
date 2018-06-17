#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import time

try:
    from RPi.GPIO import *
except ImportError:
    #----------------------------[setmode]
    def setmode(board):
        return

    #----------------------------[BOARD]
    def BOARD():
        return

    #----------------------------[setup]
    def setup(led, state):
        return

    #----------------------------[OUT]
    def OUT():
        return

    #----------------------------[LOW]
    def LOW():
        return 0

    #----------------------------[HIGH]
    def HIGH():
        return 1

    #----------------------------[output]
    def output(led, state):
        return

    #----------------------------[cleanup]
    def cleanup():
        return

rel_out = 7
usb_grn = 12
usb_red = 16
tcp_red = 32
tcp_grn = 36

#----------------------------[tcp_blink]
def tcp_blink(status):
    if status == 0:
        output(tcp_grn, HIGH)
        time.sleep(0.5)
        output(tcp_grn, LOW)
    else:
        output(tcp_red, HIGH)
        time.sleep(0.5)
        output(tcp_red, LOW)
    return

#----------------------------[tcp_status]
def tcp_status(status):
    if status == 0:
        output(tcp_grn, HIGH)
        output(tcp_red, LOW)
    else:
        output(tcp_grn, LOW)
        output(tcp_red, HIGH)
    return

#----------------------------[usb_blink]
def usb_blink(status):
    if status == 0:
        output(usb_grn, HIGH)
        time.sleep(0.5)
        output(usb_grn, LOW)
    else:
        output(usb_red, HIGH)
        time.sleep(0.5)
        output(usb_red, LOW)
    return

#----------------------------[usb_ok]
def usb_status(status):
    if status == 0:
        output(usb_grn, HIGH)
        output(usb_red, LOW)
    else:
        output(usb_grn, LOW)
        output(usb_red, HIGH)
    return

#----------------------------[relais]
def relay(value):
    if value == 1:
        output(rel_out, HIGH)
    else:
        output(rel_out, LOW)
    return

#----------------------------[init]
def init():
    setmode(BOARD)
    setup(usb_grn, OUT)
    setup(usb_red, OUT)
    setup(tcp_grn, OUT)
    setup(tcp_red, OUT)
    setup(rel_out, OUT)

    relay(0)
    return
