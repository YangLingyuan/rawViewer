#-*- encoding: utf-8 -*-
import os
import sys
import argparse
from importlib import *
from ctypes import *
import numpy as np
image = 1
class RawProcessor:
    def __init__(self, path:str,options:argparse.Namespace):
        self.pluginList=[]
        self.loadedPlugins={}
        for dirs in os.listdir("plugins"):
            if dirs.startswith("_"):
                continue
            self.pluginList.append(dirs)
        print("plugins under the dir:")
        print(self.pluginList)

        # load the plugin to object p, call the constructor to construct the raw2rgb class object mipiRawParser
        # make use of the mipiraw2raw method provided by the raw2rgb module 
        if options.raw2rgb:
            p=self.loadPlugin("raw2rgb")
            # set parameters
            mipiRawParser=p.Raw2RGB(path,options.raw2rgb[0],options.raw2rgb[1])
            self.loadedPlugins["mipiRawParser"]=mipiRawParser

            # TODO:seperate mipiraw2raw method from raw2rgb
            mipiRawParser.raw_data = mipiRawParser.read_raw_data(mipiRawParser.path)
            if mipiRawParser.rawtype == "mipi":            
                mipiRawParser.raw_data_bytearray = mipiRawParser.mipiraw_remove_stride(mipiRawParser.raw_data, mipiRawParser.width, mipiRawParser.height, mipiRawParser.stride)
                mipiRawParser.raw_array = mipiRawParser.mipiraw2raw(mipiRawParser.raw_data_bytearray, mipiRawParser.bits, mipiRawParser.loss)
            mipiRawParser.raw_array.tofile("temp.raw")
        
        if options.plusOne:
            plusOne=self.loadPlugin("plusOne")
            # set parameters
            plusOne.setParam(options.plusOne[0]);
            self.loadedPlugins["plusOne"]=plusOne



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
        raise Exception("plugin unavailable")

    def process(self):
        if "mipiRawParser" in self.loadedPlugins:
            self.loadedPlugins["mipiRawParser"].torgb().show()
        if "plusOne" in self.loadedPlugins:
            print(self.loadedPlugins["plusOne"].run())




if __name__=="__main__":
    parser = argparse.ArgumentParser(description='Choose plugins and their arguments to load')
    parser.add_argument('imagePath', type=str,  help='path to the mipi raw image to be processed')
    parser.add_argument('--raw2rgb', type=int, nargs='*')
    parser.add_argument('--plusOne', type=int, nargs='*')
    # add the plugin name as an argument here

    args=parser.parse_args(sys.argv[1:])
    RawProcessor=RawProcessor(args.imagePath, args)
    # print(RawProcessor.loadedPlugins)
    RawProcessor.process()