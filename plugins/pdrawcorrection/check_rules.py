#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from . import Config


def get_bits_type(bits):
    return bits in Config.BITS_TYPE

def get_pattern_type(pattern):
    return pattern in Config.PATTERN

def get_rawtype(rawtype):
    return rawtype in Config.RAWTYPE_O

def get_buffer_type(buffertype):
    return buffertype in Config.BUFFERTYPE