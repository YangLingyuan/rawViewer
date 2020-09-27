#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'Zheng Jiacheng'
__version__ = '0.0.2'

import os
import numpy as np
import aiofiles
from PIL import Image

from config import *
from multi_coroutine_cc import MultiCoroutine

class FileOperations(object):
    '''This module encapsulates part of the file operations of the raw2rgb module.

    '''

    @staticmethod
    def get_file_list_from_path(path:"list or str", ext:str="") -> "list[fullpath]":
        L = list()
        if isinstance(path, list):
            for item in path:
                L.extend(FileOperations.get_file_list_from_path(item, ext))
        elif isinstance(path, str):
            if os.path.isdir(path):
                L.extend(FileOperations.get_file_list_from_str(path, ext))
            elif os.path.isfile(path):
                L.append(path) if not ext else (L.append(path) if os.path.splitext(path)[1] == ext else None)
        return L

    @staticmethod
    def get_file_list_from_str(path:str, ext:str="") -> "list[fullpath]":
        L = list()
        for root, _, files in os.walk(path):
            for file in files:
                if not ext:
                    L.append(os.path.join(root, file))
                elif ext == os.path.splitext(file)[1]:
                    L.append(os.path.join(root, file))
        return L
    
    @staticmethod
    def read_raw_data(path:str) -> np.ndarray: 
        try:
            return np.fromfile(path, dtype=np.uint8).astype(np.uint16)
        except Exception as e:
            print("E: File read failed Exception:", e)
    
    @staticmethod
    def read_raw_data_with_type(path:str, types:np.dtype) -> np.ndarray:
        try:
            return np.fromfile(path, dtype=types)
        except Exception as  e:
            print_e("File read failed Exception:", e)
    
    @staticmethod
    def read_raw_data_list_with_type(path_list:list, types:np.dtype) -> np.ndarray:
        args = [[item,types] for item in path_list]
        rets = MultiCoroutine.coroutine_queue(FileOperations._read_raw_data_list_with_type, args, 3)
        return rets

    @staticmethod
    async def _read_raw_data_list_with_type(path:str, types:np.dtype) -> np.ndarray:
        try:
            ret = np.fromfile(path, dtype = types)
        except Exception as e:
            print_e("File read failed Exception:", e)
        else:
            return ret 

    @staticmethod
    def read_raw_data_list(path_list:list) ->"list[np.ndarray]" :
        args = [[item,] for item in path_list]
        rets = MultiCoroutine.coroutine_queue(FileOperations._read_raw_data_list, args, 3)
        return [np.asarray(list(item),np.uint16) for item in rets]
    
    @staticmethod
    async def _read_raw_data_list(path:"str") -> "bytearray":
        async with aiofiles.open(path, "rb") as f:
                raw_data = await f.read()
                return raw_data           

    @staticmethod
    def save(path:str, rgb_array:np.ndarray):
        try:
            Image.fromarray(rgb_array).save(path)
        except Exception as e:
            print_e("File written failed Exception:", e)
        else:
            print_m("File written successfully, path:", path)
    
    @staticmethod
    def save_list(filename_list:list, rgb_array_list:"np.ndarray list"):
        args = list()
        for index in range(len(rgb_array_list)):
            args.append([filename_list[index], rgb_array_list[index]])
        MultiCoroutine.coroutine_queue(FileOperations._save_list, args, 3)
    
    @staticmethod
    async def _save_list(filename:str, rgb_array:np.ndarray):
        try:
            Image.fromarray(rgb_array).save(filename)
        except Exception as e:
            print_e("File written failed Exception:", e)
            return None
        else:
            print_m("File written successfully, path:", filename)


