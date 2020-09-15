#-*- encoding: utf-8 -*-

__author__ = 'Qiu Bowen'

import numpy as np

r_gain=0
g_gain=0
b_gain=0
category='RGB'
def gain(data,gain):
    data = data*gain
    data[data>255] = 255
    data[data<0] = 0
    return data

def rgb_by_gain(r,g,b,r_gain,g_gain,b_gain):
    r = gain(r,r_gain)
    g = gain(g,g_gain)
    b = gain(b,b_gain)
    return r,g,b

def gray_world_assumption(r,g,b):
    b_ave, g_ave, r_ave = np.mean(b),np.mean(g),np.mean(r)
    k = (b_ave + g_ave + r_ave) / 3
    b_gain,g_gain,r_gain = k/b_ave,k/g_ave,k/r_ave
    return r_gain,g_gain,b_gain


def setParameters(rGain=0,gGain=0,bGain=0):
    global r_gain,g_gain,b_gain
    r_gain        = rGain
    g_gain        = gGain
    b_gain        = bGain


def run(rgb_array):
    global r_gain,g_gain,b_gain

    r = rgb_array[:,:,0]
    g = rgb_array[:,:,1]
    b = rgb_array[:,:,2]

    if(r_gain==0 and g_gain==0 and b_gain==0):
        _r_gain,_g_gain,_b_gain = gray_world_assumption(r,g,b)
        r,g,b = rgb_by_gain(r,g,b,_r_gain,_g_gain,_b_gain)
    else:
        r,g,b = rgb_by_gain(r,g,b,r_gain,g_gain,b_gain)

    rgb_array[:,:,0] = r
    rgb_array[:,:,1] = g
    rgb_array[:,:,2] = b

    return rgb_array
