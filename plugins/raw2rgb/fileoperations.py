#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'Zheng Jiacheng'
__version__ = '0.0.2'

import os
import numpy as np
import aiofiles
from PIL import Image
from .config import *
from .multi_coroutine_cc import MultiCoroutine


class FileOperations(object):
    '''This module encapsulates part of the file operations of the raw2rgb module.

    '''
    def __init__(self):
        pass

    @staticmethod
    def get_file_list_from_path(path:'list or str', ext:str=""):
        L = list()
        if isinstance(path, list):
            for item in path:
                L.extend(FileOperations.get_file_list_from_path(item, ext))
        elif isinstance(path, str):
            if os.path.isdir(path):
                L.extend(FileOperations.get_file_list_from_str(path, ext))
            elif os.path.isfile(path) and isinstance(ext, str):
                L.append(path)  if not ext else (L.append(path) if os.path.splitext(path)[1] == ext else None)
        return L

    @staticmethod
    def get_file_list_from_str(path:str, ext:str=""):
        L = list()
        for root, _, files in os.walk(path):
            for file in files:
                if not ext:
                    L.append(os.path.join(root, file))
                elif ext == os.path.splitext(file)[1]:
                    L.append(os.path.join(root, file))
        return L
    
    @staticmethod
    def read_raw_data(path):
        "Read a mipi raw file."
        try:
            return np.fromfile(path, dtype=np.uint8).astype(np.uint16)
        except Exception as e:
            print("E: File read failed Exception:", e)
    
    @staticmethod
    def read_raw_data_list(path:list) ->[] :
        "Read a list of mipi raw files."
        args = [[item] for item in path]
        rets = MultiCoroutine.coroutine_queue(FileOperations._read_raw_data_list, args, 3)
        return [np.asarray(list(item),np.uint16) for item in rets]
    

    @staticmethod
    async def _read_raw_data_list(path) -> np.ndarray:
        async with aiofiles.open(path, "rb") as f:
                raw_data = await f.read()
        return raw_data           

    
    @staticmethod
    def save(path:str, extension:str, rgb_array:np.ndarray):
        try:
            fullfilename, ext = os.path.splitext(path)
            fullfilename = fullfilename + extension
            Image.fromarray(rgb_array).save(fullfilename)
        except Exception as e:
            print("E: File written failed Exception:", e)
        else:
            print("M: File written successfully, path:", fullfilename)


