#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'Zheng Jiacheng'
__version__ = '0.0.7'


import argparse 
import numpy as np
from PIL import Image, ImageDraw
import math

from .config import *
from .fileoperations import *
from .mipiraw2raw import *
from .const_def import *
from .conversion_rules import *
from .multi_coroutine_cc import MultiCoroutine


class Raw2RGB(FileOperations, Mipiraw2Raw): 
    '''This module is used to convert mipi raw format files into jpg or png formats, and provide viewing functions.
    
    Parameters
    ----------
    path    : 
                File path to be resolved.
    width   : 
                The width of the original image.
    height  : 
                The height of the original image.
    stride  :
                The Stride of mipi raw pictures.
    pattern :
                Bayer arrangement pattern.
    gain    :
                The gain of the picture, the default value is 1.0.
    loss    :    
                Whether to discard the 2 low-order data when converting 10bit mipi raw images, the default value is True.
    Returns
    -------
    out : jpg, png
        The file in .jpg or .png format will be output under the specified path. 
        If the path is not specified, the output file will be output to the same path as the input file.
    

    See Also
    --------
    fileoperations : Encapsulates some common file operations.

    Examples
    --------
    Convert 10bit mipi raw format source files to RGB format:

    >>> Raw2RGB("./Sample", 4000, 3000,  5000, 10,"RGGB", mipi, 1.0, True)    
    
    '''
    def __init__(self, path:str, width:int, height:int, stride:int=None, bits:int=10, pattern:str="RGGB", rawtype:str="mipi", gain:float=1.0, loss:bool=False):        
        # Super class attribute initialization
        super().__init__()
        # Attributes initialization
        self.__path = path
        self.__width = width
        self.__height = height
        self.__stride = stride
        self.__bits = bits
        self.__pattern = pattern
        self.__rawtype = rawtype
        self.__gain = gain
        self.__loss = loss

        # Temporary attributes initialization
        self.__raw_data = None
        self.raw_data_bytearray = None
        self.raw_array = None
        self.rgb_array = None
        self.__file_list = list()
        
        # Parameter check  
        # Observe the following order:
        # rawtype->bits->pattern->width,height->stride
        # gain,loss

        self.__checked = False
              
        self.path = self.__path
        self.rawtype = self.__rawtype
        self.bits = self.__bits
        self.pattern = self.__pattern
        self.width = self.__width
        self.height = self.__height
        self.stride = self.__stride
        self.gain = self.__gain
        self.loss = self.__loss
        
        self.__checked = True




        
    # Attribute operations
    @property
    def path(self):
        return self.__path                                                                                                                   

    @path.setter
    def path(self, path):
        self.__path = path
        if type(path) in [list, str]:
            self.__file_list = super().get_file_list_from_path(path)

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
        if not self.__checked and self.__rawtype == "mipi": 
            if not stride:
                self.__stride = cr_stride_calc(width=self.__width, bits=self.__bits)
            else:
                self.__stride = stride
            if cr_stride_check(stride=self.__stride, width=self.__width):
                print_e("The stride parameter input is incorrect, the stride parameter should be greater than the width parameter.")
    
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
    def pattern(self):
        return self.__pattern

    @pattern.setter
    def pattern(self, pattern):
        if not self.__checked:
            if cr_pattern_check(pattern):
                self.__pattern = pattern
            else:
                print_e("E: Unknown Bayer arrangement")
    
    @property
    def rawtype(self):
        return self.__rawtype
    
    @rawtype.setter
    def rawtype(self, rawtype):
        if not self.__checked:
            if cr_rawtype_check(rawtype):
                self.__rawtype = rawtype
            else:
                print_e("File type error")
    
    @property
    def gain(self):
        return self.__gain

    @gain.setter
    def gain(self, gain):
        self.__gain = gain

    @property
    def loss(self):
        return self.__loss
    
    @loss.setter
    def loss(self, loss):
        pass

    @property
    def raw_data(self):
        return self.__raw_data
    
    @raw_data.setter
    def raw_data(self, raw_data):
        if isinstance(raw_data, np.ndarray):
            raw_data_len = raw_data.size
            print_m("The reading is successful, the data file length is: {}".format(raw_data_len))
            if not cr_raw_data_check(raw_data_len, self.__height, self.__width, self.__rawtype, self.__bits):
                print_e("The input length and width parameters do not match the file size, please check the input.")
            self.__raw_data = raw_data
        elif isinstance(raw_data, list):
            self.__raw_data = list()
            for item in raw_data:
                item_len = item.size
                print_m("The reading is successful, the data file length is: {}".format(item_len))
                if not cr_raw_data_check(item_len, self.__height, self.__width, self.__rawtype, self.__bits):
                    print_e("The input length and width parameters do not match the file size, please check the input.")
                else:
                    self.__raw_data.append(item)

    # Method
    def torgb(self):
        "The main process of mipi raw conversion to rgb image."    
        if len(self.__file_list) == 1:
            self.__torgb_single(self.path)
        elif len(self.__file_list) > 1:
            self.__torgb_multiple(self.path)
        return self
        
    def __torgb_single(self, path):
        self.raw_data = super().read_raw_data(self.__file_list[0])
        if self.__rawtype == "mipi":            
            self.raw_data_bytearray = super().mipiraw_remove_stride(self.__raw_data, self.__width, self.__height, self.__stride)
            self.raw_array = super().mipiraw2raw(self.raw_data_bytearray, self.__bits, self.__loss)
            self.rgb_array = self.raw2rgb(self.raw_array, self.__width, self.__height, self.__pattern, self.__gain)
        else:
            self.raw_data_bytearray = self.__raw_data
        
    
    def __torgb_multiple(self, path):
        self.raw_data = super().read_raw_data_list(self.__file_list)
        for item in self.raw_data:
            print(item) 
        
    @staticmethod
    def raw_standardized2rgb(rgb_array):        
        rgb_array_min = np.min(rgb_array)
        rgb_array_max = np.max(rgb_array)
        rgb_array = (rgb_array - rgb_array_min)/(rgb_array_max - rgb_array_min)*255
        return rgb_array       
    
    @staticmethod
    @test_run_time
    def raw2rgb(raw_array:np.ndarray, width:int, height:int, pattern:str, gain:float):
        "This is the method to convert from raw format to RGB format."
        channels = {'R': [1, 0, 0], 'G': [0, 1, 0], 'B': [0, 0, 1]}
        channel_marker = np.zeros([height, width, 3])
        for channel, (y, x) in zip(pattern, [(0, 0), (0, 1), (1, 0), (1, 1)]):
            channel_marker[y::2, x::2] = channels[channel]
        channel_marker = channel_marker.reshape([width * height, 3]).T
        rgb_array = (raw_array * channel_marker).T
        rgb_array = rgb_array.reshape([height, width, 3])
        rgb_array = Raw2RGB.raw_standardized2rgb(rgb_array)      
        if abs(1.000000 - gain) > 0.000001:
            rgb_array = rgb_array*gain
        rgb_array[rgb_array>255] = 255
        rgb_array[rgb_array<0] = 0
        return rgb_array.astype(np.uint8)
  

    def show(self):
        output = Image.fromarray(self.rgb_array)
        output.show()
    
    def save(self ,path="", extension=".jpg"):
        if extension in [".jpg",".png"]:
            if not path:
                super().save(self.__path, extension, self.rgb_array)
            else:
                super().save(path, extension, self.rgb_array)
        else:
            print_e("File extension type error.")
  
if debug:
    def main():
        ""
        # __init__(self, path:str, width:int, height:int, stride:int=None, bits:int=10, pattern:str="RGGB", rawtype:str="mipi", gain:float=1.0, loss:bool=False): 
        raw = Raw2RGB(["sample/Sample.raw","sample/Sample.raw"], 4000, 3000, 5000, 10, "RGGB", "mipi", 3, False).torgb()
else:
    def main():
        "Invoke a single module from the command line"
        # __init__(self, path:str, width:int, height:int, stride:int=None, bits:int=10, pattern:str="RGGB", rawtype:str="mipi", gain:float=1.0, loss:bool=False): 
        parser = argparse.ArgumentParser(description="This is a python module that parses raw format.")
        
        # Required parameters
        parser.add_argument('path', help='Raw source file path', required=True)
        parser.add_argument('--width', '-w', type=int, help='Raw width', required=True)
        parser.add_argument('--height', '-h', type=int, help='Raw height', required=True) 
        
        # Optional parameters
        parser.add_argument('--stride', '-s', type=int, help='mipiraw stride')
        parser.add_argument('--bits', '-b', type=int, default=10, help='Raw precision')    
        parser.add_argument('--pattern', '-p', type = str, default="RGGB", help='Image bayer pattern')
        parser.add_argument('--rawtype' '-r', type = str, default= "mipi", help='Raw type')
        parser.add_argument('--gain', '-g', type = float, default=1.0, help='Gain applied to image')
        parser.add_argument('--loss', '-l', type = bool, default=False, help='Choose whether to lose two bits of binary precision')
        args = parser.parse_args()

        # Call main function
        raw = Raw2RGB(  args.path, 
                        args.width,
                        args.height, 
                        args.stride,
                        args.bits, 
                        args.pattern,
                        args.rawtype,
                        args.gain, 
                        args.loss).run()
        raw.show()


if __name__ == "__main__":
    main()
