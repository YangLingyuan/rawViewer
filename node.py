from enum import Enum
import os
import numpy as np
from plugins.raw2rgb.fileoperations import *
import time
NODE_TYPE = Enum('NODE_TYPE', ('MIPIRAW', 'RAW', 'RGB'))
final_action = ['mipiraw2raw','demosaic', 'raw2rgb']
import pipeline
# from threading import Thread, Condition
import multiprocessing


def mipiraw_check(img):
    if not isinstance(img, np.ndarray):
        raise TypeError("Input not a ndarray")
    if not img.ndim == 1:
        raise TypeError("mipiraw dim should be 1")
def raw_check(img):
    if not isinstance(img, np.ndarray):
        raise TypeError("Input not a ndarray")
    if not img.ndim == 2:
        raise TypeError("raw dim should be 2")
def rgb_check(img):
    if not isinstance(img, np.ndarray):
        raise TypeError("Input not a ndarray")
    if not img.ndim == 3:
        raise TypeError("rgb dim should be 3")



class Node(multiprocessing.Process):
    def __init__(self, category:NODE_TYPE, input_queue, output_queue):
        self._category      = category
        self._actions       = []
        self._input_queue   = input_queue
        self._output_queue  = output_queue
        self._task_count    = 0
        multiprocessing.Process.__init__(self)

    def initialize(self,task_count,plugin_init_data_list):
        for plugin_init_data in plugin_init_data_list:
            if self._category != plugin_init_data[0].category:
                continue
            plugin = plugin_init_data[0]
            plugin.setParameters(plugin_init_data[2])
            self._actions.append(plugin)
            self._task_count = task_count


    def run(self):
        i = self._task_count
        # print(i)
        while i>0:
            if self._category in ["MIPIRAW","YUV","PDAF"]:
                temp_img_buffer = self._input_queue.get_nowait()
            else:
                temp_img_buffer = self._input_queue.get()
            print('Run node process %s (%s)...' % (self._category, os.getpid()))
            print(time.time())
            print(temp_img_buffer)
            if self._category == 'MIPIRAW':
                mipiraw_check(temp_img_buffer)
            if self._category == 'RAW':
                raw_check(temp_img_buffer)
            if self._category == 'RGB':
                rgb_check(temp_img_buffer)
            for action in self._actions:
                start_time = time.time()
                # print("%s temp_img_buffer.shape before action" % self._category)
                # print(temp_img_buffer.shape)
                temp_img_buffer = action.run(temp_img_buffer)
                # print("%s temp_img_buffer.shape after action" % self._category)
                # print(temp_img_buffer.shape)
                end_time = time.time()
                # print("M: @test_run_time: %s took %s seconds." % (action.run.__name__, str(end_time - start_time)))
            self._output_queue.put(temp_img_buffer) 
            i = i-1
        print('Node %s finished, writed to output queue'%(self._category))
        return