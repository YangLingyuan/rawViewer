#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from .const_def import *
from math import ceil

def cr_stride_calc(width, bits):
    return {8:width, 10:ceil(width*10/8), 12:ceil(width*12/8), 14:ceil(width*14/8), 16:width}[bits]

def cr_stride_check(width, stride):
    return width>stride

def cr_bits_check(bits):
    return bits in BITS_TYPE

def cr_pattern_check(pattern):
    return pattern in PATTERN

def cr_rawtype_check(rawtype):
    return rawtype in RAWTYPE

def cr_raw_data_check(raw_data_len, height, width, rawtype, bits):
    if rawtype == "mipi":
        return raw_data_len >= height * cr_stride_calc(width, bits)
    elif rawtype == "raw":
        return raw_data_len >= ceil(bits/8)*height*width
    return False