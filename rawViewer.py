#-*- encoding: utf-8 -*-
import os
import sys
import argparse
from importlib import *
from ctypes import *
import numpy as np
import pipeline
# from .plugins.raw2rgb.fileoperations import *

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
            print(dirs)
            self.pluginList.append(dirs)
            self.loadedPlugins[dirs]=self.loadPlugin(dirs)
        del options.imagePath
        print(vars(options))
        print(self.pluginList)
        self.pipe = pipeline.Pipeline()
        self.pipe.create()
        #plugin_init_data_list:[pluginObject, module name, [attributes]]
        for module in vars(options):
            if getattr(options,module):
                if self.loadedPlugins[module]:
                    paras = getattr(options,module)
                    paras.append(self._path)
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




if __name__=="__main__":
    parser = argparse.ArgumentParser(description='Choose plugins and their arguments to load')
    parser.add_argument('imagePath', type=str,  help='path to the mipi raw image to be processed')
    parser.add_argument('--raw2rgb', type=int, nargs='*')
    parser.add_argument('--mipiraw2raw', type=int, nargs='*')
    parser.add_argument('--blc', type=int, nargs=1)
    parser.add_argument('--awb', type=int, nargs='?')
    parser.add_argument('--demosaic', type=str, nargs='*')
    # add the plugin name as an argument here

    args=parser.parse_args(sys.argv[1:])
    RawProcessor=RawProcessor(args.imagePath, args)
    # print(RawProcessor.loadedPlugins)
    RawProcessor.process()