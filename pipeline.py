from enum import Enum
from collections.abc import Iterable
from plugins.raw2rgb.fileoperations  import *
# from queue import Queue
import multiprocessing
fo = FileOperations()
# NODE_TYPE = Enum('node', ('MIPIRAW', 'RAW', 'RGB'))
import node as node
class Pipeline:
    def __init__(self):
        self._nodes = []
        self._links = []
        self._file_list  = []
        self._input_list = []#ndarray
        # self._output_list = []#ndarray
        self._raw_queue = multiprocessing.Queue()
        self._rgb_queue = multiprocessing.Queue()
        self._input_queue = multiprocessing.Queue()
        self._result_queue = multiprocessing.Queue()

    def create_node_mipiraw(self):
        mipiraw_processor=node.Node('MIPIRAW', self._input_queue, self._raw_queue)
        self._nodes.append(mipiraw_processor)
        print("node MIPIRAW created")
    
    def create_node_yuv(self):
        raw_processor=node.Node('YUV',self._input_queue, self._rgb_queue)
        self._nodes.append(raw_processor)
        print("node YUV created")
    
    def create_node_pdaf(self):
        raw_processor=node.Node('PDAF',self._input_queue, self._raw_queue)
        self._nodes.append(raw_processor)
        print("node PDAF created")
    
    def create_node_raw(self):
        raw_processor=node.Node('RAW',self._raw_queue, self._rgb_queue)
        self._nodes.append(raw_processor)
        print("node RAW created")
    
    def create_node_rgb(self):
        rgb_processor=node.Node('RGB',self._rgb_queue,self._result_queue)
        self._nodes.append(rgb_processor)
        print("node RGB created")

    create_node = {
        "MIPIRAW" : create_node_mipiraw,
        "YUV" : create_node_yuv,
        "PDAF" : create_node_pdaf,
        "RAW" : create_node_raw,
        "RGB" : create_node_rgb,
    }
    
    def create(self,node_list):
        for n in node_list:
            self.create_node[n](self)
            
        # mipiraw_processor=node.Node('MIPIRAW', self._input_queue, self._raw_queue)
        # self._nodes.append(mipiraw_processor)
        # raw_processor=node.Node('RAW',self._raw_queue, self._rgb_queue)
        # self._nodes.append(raw_processor)
        # rgb_processor=node.Node('RGB',self._rgb_queue,self._result_queue)
        # self._nodes.append(rgb_processor)
    def initialize(self,path:"list or str", plugin_init_data_list):
        for node in self._nodes:
            node.initialize(plugin_init_data_list)
        self._file_list = fo.get_file_list_from_path(path)
        self._input_list = fo.read_raw_data_list(self._file_list)
        for mipiraw in self._input_list:
            self._input_queue.put(mipiraw)
    def process(self):
        for node in self._nodes:
            node.start()
        
        # for img in self._mipiraw_list:
        #     tempimg=img
        #     nodes = iter(self._nodes)
        #     while True:
        #         try:
        #             node = next(nodes)
        #             tempimg = node.process(tempimg)
        #         except StopIteration:
        #             self._output_list.append(tempimg)
        #             break
