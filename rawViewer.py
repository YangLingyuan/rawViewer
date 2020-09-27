#-*- encoding: utf-8 -*-
import os
import sys
import argparse
from importlib import *
from ctypes import *
import numpy as np
import pipeline
# from .plugins.raw2rgb.fileoperations import *
usecase = {
    "MIPIRAW" : ["MIPIRAW", "RAW", "RGB"],
    "PDAF" : ["PDAF"],
    "YUV" : ["YUV", "RGB"],
}
# image = 1
class RawProcessor:
    #do the action in the order as specified options
    def __init__(self, path:str,options:argparse.Namespace):
        self._path = path
        self.pluginList=[]
        self.loadedPlugins={}
        self.plugin_init_data_list=[]
        for dirs in os.listdir("plugins"):
            if dirs.startswith("_"):
                continue
            # print(dirs)
            self.pluginList.append(dirs)
            self.loadedPlugins[dirs]=self.loadPlugin(dirs)
        del options.imagePath
        # print(vars(options))
        # print(self.pluginList)
        self.pipe = pipeline.Pipeline()
        for module in vars(options):
            if getattr(options,module):
                if self.loadedPlugins[module]:
                    self.pipe.create(usecase[self.loadedPlugins[module].category])
                    break
        
        # if options[0]
        #plugin_init_data_list:[pluginObject, module name, [attributes]]
        for module in vars(options):
            if getattr(options,module):
                if self.loadedPlugins[module]:
                    paras = getattr(options,module)
                    print(paras)
                    paras.append(self._path)
                    # print(paras) 
                    self.plugin_init_data_list.append([self.loadedPlugins[module], module, paras])
                else: 
                    raise Exception("plugin"+module+" is not available, make sure you spell it correctly")
        print(self.plugin_init_data_list)
        self.pipe.initialize(self._path,self.plugin_init_data_list)
        


    #eg: /plugins/raw2rgb/raw2rgb.py
    def loadPlugin(self,pluginName):
        if os.path.splitext(pluginName)[0] in self.pluginList:
            if os.path.isdir("plugins/"+pluginName):
                if os.path.exists("plugins/"+pluginName+"/"+pluginName+".py"):
                    plugin = import_module("plugins."+pluginName+"."+pluginName)
                    return plugin
                if os.path.exists("plugins/"+pluginName+"/"+pluginName+".so"):
                    plugin = cdll.LoadLibrary("plugins/"+pluginName+"/"+pluginName+".so")
                    return plugin
            else:
                raise Exception("Invalid plugin path")
        raise Exception(pluginName+":plugin unavailable")

    def process(self):

        self.pipe.process()



def str_and_int(string):
    if string.isnumeric():
        return int(string)
    else :
        return string



if __name__=="__main__":
    parser = argparse.ArgumentParser(description='Choose plugins and their arguments to load')
    parser.add_argument('imagePath', type=str, nargs='*', 
        help='path to the mipi raw/yuv/pdaf raw image to be processed')
    parser.add_argument('--raw2rgb', type=int, nargs='*', 
        help='')
    parser.add_argument('--mipiraw2raw', type=int,  nargs='+', metavar='width:int height:int (stride:int) (bits:int) (loss:bool)', 
        help='')
    parser.add_argument('--yuv2rgb', type=str_and_int,  nargs=3, metavar=('yuv_type:str', 'width:int', 'height:int'), 
        help='')
    parser.add_argument('--blc', type=int, nargs=1, metavar='obc:int', help='')
    parser.add_argument('--demosaic', type=int, nargs=1)
    parser.add_argument('--awb', type=int, nargs=3, metavar=('r_gain:int', 'g_gain:int', 'b_gain:int'), 
        help='')
    parser.add_argument('--rgb2jpg', action='store_true', 
        help='')
    parser.add_argument('--pdgainmap', type=str_and_int, nargs='*', 
        # metavar=('path_pdaf:str', 'width_pdaf:int', 'height_pdaf:int', 'path_o:str', 'width_o:int', 'height_o:int', 'bits:int', 'rawtype:str', 'pattern:str', 'buffertype:str'), 
        metavar='...',
        help='path_pdaf:str, width_pdaf:int, height_pdaf:int, path_o:str, width_o:int, height_o:int, bits:int, rawtype:str, pattern:str, buffertype:str')
    parser.add_argument('--lsc', type=str_and_int, nargs='*', 
        # metavar=('eeprom_lsc_data_path:str', 'pattern:str', 'block_height:int', 'block_width:int'), 
        metavar='...',
        help='eeprom_lsc_data_path:str, pattern:str, block_height:int, block_width:int')
    parser.add_argument('--pdrawcorrection', type=str_and_int, nargs='*', 
        # metavar=('path_gain:str', 'path_pdaf:str', 'width_pdaf:int', 'height_pdaf:int', 'bits:int', 'rawtype:str', 'buffertype:str'), 
        metavar='...', 
        help='path_gain:str, path_pdaf:str, width_pdaf:int, height_pdaf:int, bits:int, rawtype:str, buffertype:str')
    parser.add_argument('--pdsplit', type=str_and_int, nargs='*', 
        # metavar=('XMlpath:str', 'path_raw:str', 'rawtype:str', 'width:int', 'height:int', 'bits:int', 'buffertype:str'), 
        metavar='...', 
        help='XMlpath:str, path_raw:str, rawtype:str, width:int, height:int, bits:int, buffertype:str')
    
    # add the plugin name as an argument here

    args=parser.parse_args(sys.argv[1:])
    RawProcessor=RawProcessor(args.imagePath, args)
    # print(RawProcessor.loadedPlugins)
    RawProcessor.process()
