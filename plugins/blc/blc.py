#-*- encoding: utf-8 -*-

__author__ = 'Qiu Bowen'

import numpy as np
category='RAW'
obc=0
def setParameters(args):
    global obc
    obc=args[0]

def run(raw_data:np.ndarray):
    raw_data[raw_data < obc] = obc
    raw_data = raw_data - obc
    return raw_data