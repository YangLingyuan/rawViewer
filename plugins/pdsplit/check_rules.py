#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from . import Pconfig as cn

def get_bits_type(bits):
    return bits in cn.BITS_TYPE

def get_pattern_type(pattern):
    return pattern in cn.PATTERN

def get_rawtype(rawtype):
    return rawtype in cn.RAWTYPE_O

def get_buffer_type(buffertype):
    return buffertype in cn.BUFFERTYPE