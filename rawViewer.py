#-*- encoding: utf-8 -*-
#main1.py
import os
from ctypes import *
image = 1
class RawProcessor:
    def __init__(self):
        self.loadPlugins()

    def loadImage(self, from_):
        print ("loading image from %s." % from_)

    def loadPlugins(self):
        for filename in os.listdir("plugins"):
            if filename.startswith("_"):
                continue
            if filename.endswith(".so"):
                plugin = cdll.LoadLibrary("plugins/"+filename)
                plugin.run(image)
                continue
            if filename.endswith(".py"):
                pluginName=os.path.splitext(filename)[0]
                plugin=__import__("plugins."+pluginName, fromlist=[pluginName])
                plugin.run(self,image)

if __name__=="__main__":
    RawProcessor=RawProcessor()