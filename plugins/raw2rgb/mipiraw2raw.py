#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'Zheng Jiacheng'
__version__ = '0.0.1'

import numpy as np

try:
    from .fileoperations import *
    from .conversion_rules import *
    from .config import *
    from .multi_coroutine_cc import MultiCoroutine
except ImportError:
    from fileoperations import *
    from conversion_rules import *
    from config import *
    from multi_coroutine_cc import MultiCoroutine    

class Mipiraw2Raw(FileOperations):
    '''This module is used to convert mipiraw to raw image
    
    Parameters
    ----------
    path        : 
                    File path to be resolved.
    width       : 
                    The width of the original image.
    height      : 
                    The height of the original image.
    stride      :
                    The Stride of mipi raw pictures.
    bits        :
                    Store the bit of a pixel.
    loss        :    
                    Whether to discard the 2 low-order data when converting 10bit mipi raw images, the default value is True.

    '''
    def __init__(self, path:str, width:int, height:int, stride:int=None, bits:int=10, loss:bool=False):
        self.__path = path
        self.__width = width
        self.__height = height
        self.__stride = stride
        self.__bits = bits
        self.__loss = loss

        self.__checked = False
        
        self.path = self.__path
        self.width = self.__width
        self.height = self.__height
        self.stride = self.__stride
        self.bits = self.__bits

        self.__checked = True

        self.__rawdata = None

    # Attribute operations
    @property
    def path(self):
        return self.__path                                                                                                                   

    @path.setter
    def path(self, path):
        if not self.__checked: 
            if type(path) in [list, str]:
                self.__file_list = super().get_file_list_from_path(path)
                self.__path = path
            else:
                print_e("Path parameter type error.")
    
    @property
    def width(self):
        return self.__width
    
    @width.setter
    def width(self, width):
        pass
    
    @property
    def height(self):
        return self.__height
    
    @height.setter
    def height(self, height):
        pass

    @property
    def stride(self):
        return self.__stride
    
    @stride.setter
    def stride(self, stride):
        if not self.__checked: 
            if not stride:
                self.__stride = cr_stride_calc(width=self.__width, bits=self.__bits)
            else:
                if cr_stride_check(stride=self.__stride, width=self.__width):
                    print_e("The stride parameter input is incorrect, the stride parameter should be greater than the width parameter.")
                self.__stride = stride
    @property
    def bits(self):
        return self.__bits
    
    @bits.setter
    def bits(self, bits):
        if not self.__checked:
            if cr_bits_check(bits):
                self.__bits = bits
            else:
                print_e("Bit type error.")
    
    @property
    def mipiraw_data(self):
        return self.__mipiraw_data
    
    @mipiraw_data.setter
    def mipiraw_data(self, mipiraw_data):
        if isinstance(mipiraw_data, np.ndarray):
            mipiraw_data_len = mipiraw_data.size
            print_m("The reading is successful, the data file length is:", mipiraw_data_len)
            if not cr_raw_data_check(mipiraw_data_len, self.__height, self.__width, "mipi", self.__bits):
                print_e("The input length and width parameters do not match the file size, please check the input.")
            self.__mipiraw_data = mipiraw_data
        elif isinstance(mipiraw_data, list):
            self.__mipiraw_data = list()
            for item in mipiraw_data:
                item_len = item.size
                print_m("The reading is successful, the data file length is:", item_len)
                if not cr_raw_data_check(item_len, self.__height, self.__width, "mipi", self.__bits):
                    print_e("The input length and width parameters do not match the file size, please check the input.")
                else:
                    self.__mipiraw_data.append(item)   

    def toraw(self):
        "The main process of mipi raw conversion to rgb image."    
        if len(self.__file_list) == 1:
            self.__toraw_single()
        elif len(self.__file_list) > 1:
            self.__toraw_multiple()
        return self.raw_array
    
    def __toraw_single(self):    
        self.mipiraw_data = super().read_raw_data(self.__file_list[0])
        self.raw_data_bytearray = self.mipiraw_remove_stride(self.__mipiraw_data, self.__width, self.__height, self.__stride)
        self.raw_array = self.mipiraw2raw(self.raw_data_bytearray, self.__bits, self.__loss)
    
    def __toraw_multiple(self):
        self.mipiraw_data = super().read_raw_data_list(self.__file_list)
        self.raw_data_bytearray = list()
        for item in self.mipiraw_data:
            self.raw_data_bytearray.append(self.mipiraw_remove_stride(item, self.__width, self.__height, self.__stride))    
        self.raw_array = list()
        for item in self.raw_data_bytearray:
            self.raw_array.append(self.mipiraw2raw(item, self.__bits, self.__loss))

    # public classmethod
    @classmethod
    @test_run_time
    def mipiraw_remove_stride(cls, raw_data:np.ndarray, width:int, height:int, stride:int) -> np.ndarray:
        if raw_data.size == height * stride:
            return raw_data
        return raw_data.reshape([height, -1])[:, :stride].reshape(height*stride)  

    @classmethod
    def mipiraw2raw(cls, mipiraw_array:np.ndarray, bits:int=10, loss:bool= False) -> np.ndarray:
        if bits==8 :return cls.mipiraw8toraw(mipiraw_array)
        elif bits==10 and loss : return cls.mipiraw10toraw_l(mipiraw_array)
        elif bits==10 and not loss : return cls.mipiraw10toraw(mipiraw_array)
        elif bits==12 and loss : return cls.mipiraw12toraw_l(mipiraw_array)
        elif bits==12 and not loss : return cls.mipiraw12toraw(mipiraw_array)
        elif bits==14 and loss : return cls.mipiraw14toraw_l(mipiraw_array)
        elif bits==14 and not loss : return cls.mipiraw14toraw(mipiraw_array)
        elif bits==16 : return cls.mipiraw16toraw(mipiraw_array)
        return None
        
    @classmethod
    @test_run_time
    def mipiraw8toraw(cls, mipiraw8_array:np.ndarray)->np.ndarray:
        return mipiraw8_array
    
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
    
    @classmethod
    @test_run_time
    def mipiraw12toraw(cls, mipiraw12_array:np.ndarray)->np.ndarray:
        mipiraw12_array = mipiraw12_array.reshape((-1,3)).astype(np.uint16)
        mipiraw12_array[:,0] = np.left_shift(mipiraw12_array[:,0], 4)
        mipiraw12_array[:,1] = np.left_shift(mipiraw12_array[:,1], 4)
        mipiraw12_array[:,0] = mipiraw12_array[:,0] | np.bitwise_and(mipiraw12_array[:,2], 0b1111)
        mipiraw12_array[:,1] = mipiraw12_array[:,1] | np.bitwise_and(np.right_shift(mipiraw12_array[:,2],4),0b1111)
        return np.delete(mipiraw12_array,-1,axis=1).reshape((1,-1))
    
    @classmethod
    @test_run_time
    def mipiraw12toraw_l(cls, mipiraw12_array:np.ndarray)->np.ndarray:
        return np.left_shift(np.delete(mipiraw12_array, np.s_[2::3]), 4)
    

    @classmethod
    @test_run_time
    def mipiraw14toraw_l(cls, mipiraw14_array:np.ndarray)->np.ndarray:
        mipiraw14_array.reshape((-1, 7)).astype(np.uint16)
        np.delete(mipiraw14_array,[4,5,6,7],1)
        mipiraw14_array = np.left_shift(mipiraw14_array.reshape((1,-1)), 6)
        return mipiraw14_array
    
    @classmethod
    @test_run_time
    def mipiraw14toraw(cls, mipiraw14_array:np.ndarray)->np.ndarray:
        mipiraw14_array.reshape((-1, 7)).astype(np.uint16)
        for index in range(4):
            mipiraw14_array[:,index] = np.left_shift(mipiraw14_array[:, index], 6)
        mipiraw14_array[:,0] = mipiraw14_array[:,0] | np.bitwise_and(mipiraw14_array[:,4],0b111111)
        mipiraw14_array[:,1] = mipiraw14_array[:,1] | np.bitwise_and(np.right_shift(mipiraw14_array[:,4],6),0b11)
        mipiraw14_array[:,1] = mipiraw14_array[:,1] | np.bitwise_and(np.left_shift(mipiraw14_array[:,5],2),0b001111)
        mipiraw14_array[:,2] = mipiraw14_array[:,2] | np.bitwise_and(np.right_shift(mipiraw14_array[:,5],4),0b1111)
        mipiraw14_array[:,2] = mipiraw14_array[:,2] | np.bitwise_and(np.left_shift(mipiraw14_array[:,6],4),0b000011)
        mipiraw14_array[:,3] = mipiraw14_array[:,3] | np.bitwise_and(np.right_shift(mipiraw14_array[:,6],6),0b111111)
        return np.delete(mipiraw14_array,[4,5,6,7],1).reshape((1,-1))
    
    @classmethod
    @test_run_time
    def mipiraw16toraw(cls, mipiraw16_array:np.ndarray) -> np.ndarray:
        mipiraw16_array.reshape((-1,2)).astype(np.uint16)
        mipiraw16_array[:,1] = np.left_shift(mipiraw16_array[:,1],8) | mipiraw16_array[:,0]
        return np.delete(mipiraw16_array,[0],1).reshape((1,-1))

# Shell model Interface
mipiraw2raw = Mipiraw2Raw