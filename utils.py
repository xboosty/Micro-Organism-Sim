# utils.py
import math

def clamp(x, a, b):
    return a if x < a else b if x > b else x

def wrap_pos(x, y, w, h):
    if x < 0: x += w
    if x >= w: x -= w
    if y < 0: y += h
    if y >= h: y -= h
    return x, y

def angle_wrap(a):
    while a <= -math.pi: a += 2*math.pi
    while a >  math.pi: a -= 2*math.pi
    return a

def lerp(a, b, t):
    return a + (b - a) * t
