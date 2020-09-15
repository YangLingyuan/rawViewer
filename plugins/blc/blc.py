#-*- encoding: utf-8 -*-

__author__ = 'Qiu Bowen'

import numpy as np
category='RAW'
def run(raw_data:np.ndarray,obc:int=0):
    raw_data[raw_data < obc] = obc
    raw_data = raw_data - obc
    return raw_data