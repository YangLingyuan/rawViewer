#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'Zheng Jiacheng'
__version__ = '0.0.7'


import argparse 
import numpy as np
from PIL import Image, ImageDraw
import math

import os
import sys
sys.path.append(os.path.dirname(__file__))
category='RGB'
try :
    from .config import *
    from .fileoperations import *
    from .mipiraw2raw import *
    from .const_def import *
    from .conversion_rules import *
    from .multi_coroutine_cc import MultiCoroutine
except ImportError:
    from config import *
    from fileoperations import *
    from mipiraw2raw import *
    from const_def import *
    from conversion_rules import *
    from multi_coroutine_cc import MultiCoroutine    


class Raw2RGB(Mipiraw2Raw, FileOperations): 
    '''This module is used to convert mipi raw format files into jpg or png formats, and provide viewing functions.
    
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
    pattern     :
                    Bayer arrangement pattern.
    rawtype     :
                    The types of raw include mipiraw, rawplain and so on.
    gain        :
                    The gain of the picture, the default value is 1.0.
    loss        :    
                    Whether to discard the 2 low-order data when converting 10bit mipi raw images, the default value is True.
    arrangement :
                    There are Bayer permutations, 4in1.
    Returns
    -------
    out : jpg, png
        The file in .jpg or .png format will be output under the specified path. 
        If the path is not specified, the output file will be output to the same path as the input file.
    
    out : rgb_array
        It can be directly output to three channel RGB, and the stored data structure is ndarray.  
    
    See Also
    --------
    fileoperations  : Encapsulates some common file operations.
    mipiraw2raw     : This module is used to convert mipiraw to raw image

    Examples
    --------
    Convert 10bit mipi raw format source files to RGB format:

    >>> Raw2RGB("./Sample", 4000, 3000).torgb()
    
    '''
    def __init__(self, path:str, wh, stride:int=None, bits:int=10, pattern:str="GRBG", rawtype:str="mipi", gain:float=1.0, loss:bool=False, arrangement:str="bayer"):

        # Attributes initialization
        self.__path = path
        self.__width = wh[0]
        self.__height = wh[1]
        self.__stride = stride
        self.__bits = bits
        self.__pattern = pattern
        self.__rawtype = rawtype
        self.__gain = gain
        self.__loss = loss
        self.__arrangement = arrangement

        # Temporary attributes initialization
        self.__to_raw = False 
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
        if not self.__checked and self.__rawtype == "mipi": 
            if not stride:
                self.__stride = cr_stride_calc(width=self.__width, bits=self.__bits)
            else:
                if cr_stride_check(stride=self.__stride, width=self.__width, bits=self.__bits):
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
        if type(gain) == float:
            self.__gain = gain

    @property
    def loss(self):
        return self.__loss
    
    @loss.setter
    def loss(self, loss):
        if type(loss) == bool:
            self.__loss = loss

    @property
    def arrangement(self):
        return self.__arrangement
    
    @arrangement.setter
    def arrangement(self,arrangement):
        if not self.__checked:
            if cr_arrangement_check(arrangement):
                self.__arrangement = arrangement
            else:
                print_e("Wrong arrangement type")

    @property
    def raw_data(self):
        return self.__raw_data
    
    @raw_data.setter
    def raw_data(self, raw_data):
        if isinstance(raw_data, np.ndarray):
            raw_data_len = raw_data.size
            print_m("The reading is successful, the data file length is:", raw_data_len)
            if not cr_raw_data_check(raw_data_len, self.__height, self.__width, self.__rawtype, self.__bits):
                print_e("The input length and width parameters do not match the file size, please check the input.")
            self.__raw_data = raw_data
        elif isinstance(raw_data, list):
            self.__raw_data = list()
            for item in raw_data:
                item_len = item.size
                print_m("The reading is successful, the data file length is:", item_len)
                if not cr_raw_data_check(item_len, self.__height, self.__width, self.__rawtype, self.__bits):
                    print_e("The input length and width parameters do not match the file size, please check the input.")
                else:
                    self.__raw_data.append(item)

    # Method
    def toraw(self):
        "The main process of mipi raw or raw plain convert to raw."    
        if len(self.__file_list) < 1 :
            print_e("No valid file detected, please check the input")
        if len(self.__file_list) == 1:
            self.__toraw_single()
        elif len(self.__file_list) > 1:
            self.__toraw_multiple()
        self.__to_raw = True
        return self.raw_array     

    def __toraw_single(self):
        if self.__rawtype == "mipi":     
            self.raw_data = super().read_raw_data(self.__file_list[0])
            self.raw_data_bytearray = super().mipiraw_remove_stride(self.__raw_data, self.__width, self.__height, self.__stride)
            self.raw_array = super().mipiraw2raw(self.raw_data_bytearray, self.__bits, self.__loss)
        elif self.__rawtype == "rawplain":
            self.raw_data = self.read_rawplain_data()
            self.raw_data_bytearray = self.__raw_data
            self.raw_array = self.__raw_data

    def __toraw_multiple(self):
        if self.__rawtype == "mipi":
            self.raw_data = super().read_raw_data_list(self.__file_list)
            self.raw_data_bytearray = list()
            for item in self.raw_data:
                self.raw_data_bytearray.append(super().mipiraw_remove_stride(item, self.__width, self.__height, self.__stride))    
            self.raw_array = list()
            for item in self.raw_data_bytearray:
                self.raw_array.append(super().mipiraw2raw(item, self.__bits, self.__loss))
        if self.__rawtype == "rawplain":
            self.raw_data = self.read_rawplain_data()
            self.raw_data_bytearray = self.__raw_data
            self.raw_array = self.__raw_data     

    def torgb(self):
        "The main process of mipi raw convert to rgb image."    
        if not self.__to_raw:
            self.toraw()
        if isinstance(self.raw_array, np.ndarray):
            self.rgb_array = self.raw2rgb(self.raw_array, self.__width, self.__height, self.__pattern, self.__gain, self.__arrangement)
        elif isinstance(self.raw_array, list):
            self.rgb_array = list()
            for item in self.raw_array:
                self.rgb_array.append(self.raw2rgb(item, self.__width, self.__height, self.__pattern, self.__gain, self.__arrangement))
        else:
            print_e("No valid RAW resolved")
        return self.rgb_array

    def read_rawplain_data(self) -> np.ndarray:
        if len(self.__file_list) == 1:
            if self.__bits == 16:
                return super().read_raw_data_with_type(self.__file_list[0], np.uint16)
        elif len(self.__file_list) > 1:
            if self.__bits == 16:
                return super().read_raw_data_list_with_type(self.__file_list, np.uint16)

    # Static Method
    @staticmethod
    def raw_standardized2rgb(rgb_array):        
        rgb_array_min = np.min(rgb_array)
        rgb_array_max = np.max(rgb_array)
        rgb_array = (rgb_array - rgb_array_min)/(rgb_array_max - rgb_array_min)*255
        return rgb_array      
    
    @staticmethod
    def raw2rgb(raw_array:np.ndarray, width:int, height:int, pattern:str, gain:float, arrangement:str):
        "This is the method to convert from raw format to RGB format."
        if arrangement == "bayer":
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
        elif arrangement == "4in1":
            channels = {'R': [1, 0, 0], 'G': [0, 1, 0], 'B': [0, 0, 1]}
            channel_marker = np.zeros([height, width, 3])
            for channel, (y, x) in zip(pattern, [(0, 0), (0, 2), (2, 0), (2, 2)]):
                channel_marker[y::4, x::4] = channels[channel]
            for channel, (y, x) in zip(pattern, [(0, 1), (0, 3), (2, 1), (2, 3)]):
                channel_marker[y::4, x::4] = channels[channel]
            for channel, (y, x) in zip(pattern, [(1, 0), (1, 2), (3, 0), (3, 2)]):
                channel_marker[y::4, x::4] = channels[channel]
            for channel, (y, x) in zip(pattern, [(1, 1), (1, 3), (3, 1), (3, 3)]):
                channel_marker[y::4, x::4] = channels[channel]           
            channel_marker = channel_marker.reshape([width * height, 3]).T
            rgb_array = (raw_array * channel_marker).T
            rgb_array = rgb_array.reshape([height, width, 3])
            rgb_array = Raw2RGB.raw_standardized2rgb(rgb_array)      
            if abs(1.000000 - gain) > 0.000001:
                rgb_array = rgb_array*gain
            rgb_array[rgb_array>255] = 255
            rgb_array[rgb_array<0] = 0
            return rgb_array.astype(np.uint8)

    def show(self, number=0):
        if isinstance(self.rgb_array, np.ndarray):
            output = Image.fromarray(self.rgb_array)
        elif isinstance(self.rgb_array, list):
            output = Image.fromarray(self.rgb_array[number])
        output.show()
        
    def save(self, ext=".jpg", path=""):
        if isinstance(self.rgb_array,list):
            filename_list = list()
            if path == "":             
                for filename in [ os.path.splitext(item)[0] for item in self.__file_list]:
                    filename_list.append(filename+ext)
                super().save_list(filename_list, self.rgb_array)
            else:
                for filename in [ os.path.basename(item) for item in self.__file_list]:
                    filename_list.append(os.path.join(path, filename+ext))
                super().save_list(filename_list, self.rgb_array)
        elif isinstance(self.rgb_array, np.ndarray):
            if not path:
                super().save(os.path.splitext(self.__path)[0]+ext, self.rgb_array)
            elif os.path.splitext(path)[0] in [".jpg",".png"]:
                super().save(path, self.rgb_array)
            else:
                print_e("File extension type error.")
        return self


@test_run_time
def run_debug():
    "" 
    # gray
    # raw = Raw2RGB(r"sample/Sample_MIPIRAW10bit_Pattern_RGGB_W4000_H3000.raw", 4000, 3000,arrangement="bayer",gain=1)
    # Image.fromarray(raw.toraw().reshape(3000,4000).astype(np.uint8)).show()
    # color
    raw = Raw2RGB(r"/home/jc/Projects/CViewer/GitLab/CViewer/sample/Sample.raw", 4000, 3000,arrangement="bayer",gain=1)
    raw.torgb()
    raw.show()

def run():
    "Invoke a single module from the command line"
    parser = argparse.ArgumentParser(description="This is a python module that parses raw format.")
    
    # Required parameters
    parser.add_argument('--path', '-P', help='Raw source file path', required=True)
    parser.add_argument('--width', '-W', type=int, help='Raw width', required=True)
    parser.add_argument('--height', '-H', type=int, help='Raw height', required=True) 
    
    # Optional parameters
    parser.add_argument('--stride', '-s', type=int, default=None, help='mipiraw stride')
    parser.add_argument('--bits', '-b', type=int, default=10, help='Raw precision')    
    parser.add_argument('--pattern', '-p', type = str, default="RGGB", help='Image bayer pattern')
    parser.add_argument('--rawtype','-r', type = str, default="mipi", help='Raw type')
    parser.add_argument('--gain', '-g', type = float, default=1.0, help='Gain applied to image')
    parser.add_argument('--loss', '-l', type = bool, default=False, help='Choose whether to lose two bits of binary precision')
    parser.add_argument('--arrangement', '-a', type = str, default="bayer", help='Can choose 4in1 or bayer arrangement')
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
                    args.loss,
                    args.arrangement).torgb()
    raw.show()



raw2rgb = Raw2RGB

# Shell model Interface
# def __init__(self, path:str, width:int, height:int, stride:int=None, bits:int=10, pattern:str="GRBG", rawtype:str="mipi", gain:float=1.0, loss:bool=False, arrangement:str="bayer"):
module_class            = raw2rgb
module_obj = None
module_help             = raw2rgb.__doc__

module_params           = {"path":None,"width":None,"height":None,"stride":None,"bits":10,"pattern":"GRBG", "rawtype":"mipi", "gain" : 1.0, "loss":False, "arrangement":"bayer"}
module_params_type      = {"path":str,"width":int,"height":int,"stride":int,"bits":int,"pattern":str, "rawtype":str, "gain" : float, "loss":bool, "arrangement":str}
module_params_help      = { "path":"file path",
                            "width":"The width of the original image",
                            "height":"The height of the original image.",
                            "stride":"The Stride of mipi raw pictures.",
                            "bits":"Store the bit of a pixel.",
                            "pattern":"Bayer arrangement pattern.", 
                            "rawtype":"The types of raw include mipiraw, rawplain and so on.", 
                            "gain" : "The gain of the picture, the default value is 1.0.", 
                            "loss":"Whether to discard the 2 low-order data when converting 10bit mipi raw images, the default value is True.", 
                            "arrangement":" There are Bayer permutations, 4in1."}

# module init
def module_init(params=None):
    global module_params, module_obj
    if params:
        module_obj = module_class(**params)
    else:
        module_obj = module_class(**module_params)
    return module_obj

# module functions
def module_function(func_name):
    global module_obj
    return {"toraw":module_obj.toraw,"torgb":module_obj.torgb,"show":module_obj.show}[func_name]()

module_function_help        = {"toraw":"mipiraw to raw", "torgb": "raw to rgb", "show": "show images"}

# module static function
module_static_function      = {"raw_standardized2rgb":module_class.raw_standardized2rgb,"raw2rgb":module_class.raw2rgb}
module_static_function_help = {"raw_standardized2rgb":module_class.raw_standardized2rgb.__doc__,"raw2rgb":module_class.raw2rgb.__doc__}


if __name__ == "__main__":
    if debug:
        run_debug()
    else:
        run()