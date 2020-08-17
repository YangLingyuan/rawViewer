#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'Zheng Jiacheng'
__version__ = '0.0.1'
import numpy as np
from .fileoperations import *
from .config import *

class Mipiraw2Raw(object):
    '''
    '''
    def __init__(self):
        pass

    @classmethod
    @test_run_time
    def mipiraw_remove_stride(cls, raw_data:np.ndarray, width:int, height:int, stride:int) -> np.ndarray:
        if raw_data.size == height * stride:
            return raw_data
        return raw_data.reshape([height, -1])[:, :stride].reshape(height*stride)     
    
    @classmethod
    def mipiraw2raw(cls, mipiraw_array:np.ndarray, bits:int=10, loss:bool= False) -> np.ndarray:
        if bits==10 and loss : return cls.mipiraw10toraw_l(mipiraw_array)
        elif bits==10 and not loss : return cls.mipiraw10toraw(mipiraw_array)
        return None
        
    
    @classmethod
    @test_run_time
    def mipiraw10toraw_l(cls, mipiraw10_array: np.ndarray):
        "[0:1] bits are lost when mipi raw 10bit is converted to raw, which will lose precision."
        return (np.delete(mipiraw10_array, np.s_[4::5])*4).astype(np.uint16)
    
    @classmethod
    @test_run_time
    def mipiraw10toraw(cls, mipiraw10_array: np.ndarray):
        "This is the lossless conversion method of mipi raw to raw."
        mipiraw10_array = mipiraw10_array.reshape((-1,5)).astype(np.uint16)
        mipiraw10_array[:,0] = np.left_shift(mipiraw10_array[:,0],2)
        mipiraw10_array[:,1] = np.left_shift(mipiraw10_array[:,1],2)
        mipiraw10_array[:,2] = np.left_shift(mipiraw10_array[:,2],2)
        mipiraw10_array[:,3] = np.left_shift(mipiraw10_array[:,3],2)
        mipiraw10_array[:,0] = mipiraw10_array[:,0] | np.bitwise_and(mipiraw10_array[:,4],0x3)
        mipiraw10_array[:,1] = mipiraw10_array[:,1] | np.bitwise_and(np.right_shift(mipiraw10_array[:,4],2),0x3)
        mipiraw10_array[:,2] = mipiraw10_array[:,2] | np.bitwise_and(np.right_shift(mipiraw10_array[:,4],4),0x3)
        mipiraw10_array[:,3] = mipiraw10_array[:,3] | np.bitwise_and(np.right_shift(mipiraw10_array[:,4],6),0x3)
        return np.delete(mipiraw10_array,-1,axis=1).reshape((1,-1))
    

    