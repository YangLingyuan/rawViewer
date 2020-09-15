from enum import Enum
import os

from plugins.raw2rgb.fileoperations import *

NODE_TYPE = Enum('node', ('MIPIRAW', 'RAW', 'RGB','NONE'))
final_action = ['mipiraw2raw','demosaic', 'raw2rgb']
import pipeline
class Node():
    def __init__(self, category:NODE_TYPE, dependency:NODE_TYPE):
        self._category   = category
        self._dependency = dependency
        self._actions = []

    def initialize(self,plugin_init_data_list):
        for plugin_init_data in plugin_init_data_list:
            if self._category != plugin_init_data[0].category:
                continue
            try:
                plugin_constructor = getattr(plugin_init_data[0],plugin_init_data[1])
                print(plugin_constructor)
                plugin = plugin_constructor(plugin_init_data[2])
            except :
                plugin = plugin_init_data[0]
                plugin.setParameters(plugin_init_data[2])
            self._actions.append(plugin)
        print("Node"+self._category+" initialized, has property:")
        print(self._actions)


    def process(self,img):
        actions = iter(self._actions)
        temp_img_nuffer = img
        while True:
            try:
                action = next(actions)
                temp_img_nuffer = action.run(temp_img_nuffer)
            except StopIteration:
                break
        return temp_img_nuffer