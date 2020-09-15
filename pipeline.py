from enum import Enum
from collections.abc import Iterable
from plugins.raw2rgb.fileoperations  import *
fo = FileOperations()
# NODE_TYPE = Enum('node', ('MIPIRAW', 'RAW', 'RGB'))
import node as node
class Pipeline:
    def __init__(self):
        self._nodes = []
        self._links = []
        self._file_list  = []
        self._mipiraw_list = []#ndarray\
        self._output_list = []#ndarray
    # def call_next_node()
    # def call_prev_node()
    def create(self):
        mipiraw_processor=node.Node('MIPIRAW','NONE')
        self._nodes.append(mipiraw_processor)
        raw_processor=node.Node('RAW','MIPIRAW')
        self._nodes.append(raw_processor)
        rgb_processor=node.Node('RGB','RAW')
        self._nodes.append(rgb_processor)
    def initialize(self,path:"list or str", plugin_init_data_list):
        for node in self._nodes:
            node.initialize(plugin_init_data_list)
        self._file_list = fo.get_file_list_from_path(path)
        self._mipiraw_list = fo.read_raw_data_list(self._file_list)
    def process(self):
        for img in self._mipiraw_list:
            tempimg=img
            nodes = iter(self._nodes)
            while True:
                try:
                    node = next(nodes)
                    tempimg = node.process(tempimg)
                except StopIteration:
                    self._output_list.append(tempimg)
                    break
