#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from math import ceil

from const_def import *


def cr_stride_calc(width, bits):
    return ceil(width*bits/8)    

def cr_stride_check(stride, width, bits):
    return cr_stride_calc(width,bits) <= stride

def cr_bits_check(bits):
    return bits in BITS_TYPE

def cr_pattern_check(pattern):
    return pattern in PATTERN

def cr_rawtype_check(rawtype):
    return rawtype in RAWTYPE

def cr_raw_data_check(raw_data_len, height, width, rawtype, bits):
    if rawtype == "mipi":
        return raw_data_len >= height * cr_stride_calc(width, bits)
    elif rawtype == "rawplain":
       return raw_data_len == height*width
    return False

def cr_arrangement_check(arrangement):
    return arrangement in ARRANGEMENT