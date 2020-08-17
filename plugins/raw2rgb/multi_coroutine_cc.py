#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'Zheng Jiacheng'
__version__ = '0.0.1'

import asyncio
import aiofiles
import random
import time
import threading
import numpy as np
import plugins.raw2rgb.config as config


# class SingletonMetaClass(type):
#     _lock = threading.Lock()
#     def __call__(cls, *args, **kwargs):
#         if not hasattr(cls, '_instance'):
#             with cls._lock:
#                 if not hasattr(cls, '_instance'):
#                     cls._instance = super(SingletonMetaClass, cls).__call__(*args, **kwargs)
#         return cls._instance


#Multi-coroutine computing channel
class MultiCoroutine():
    
    @classmethod
    @config.test_run_time
    def coroutine_queue(cls, func, jobs, concurrency):
        rets = asyncio.run(cls.__coroutine_queue(func, jobs, concurrency))
        return rets
    @classmethod
    async def __coroutine_queue(cls, func, jobs, concurrency):
        jobs_queue = asyncio.Queue()
        lock = asyncio.Lock()
        rets = []
        for job in jobs:
            jobs_queue.put_nowait(job)
        tasks = list()
        for item in range(concurrency):
            task = asyncio.create_task(cls.worker(func, jobs_queue , lock, rets))
            tasks.append(task)
        await jobs_queue.join()

        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
        return rets


    @classmethod
    async def worker(cls, func, q, lock, rets):
        while True:
            args = await q.get()
            ret = await func(*args) 
            with await lock:
                rets.append(ret)
            q.task_done()



# async def sync_proc(args):                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     
#     "Asynchronous IO read file."
#     async with aiofiles.open(args['file_path'], "rb") as f:
#         raw_data = await f.read()
#         return raw_data
    

    


# if __name__ == "__main__":
#     args1 = {'file_path':"sample/Sample.raw",'raw_data':None}
#     args2 = {'file_path':"sample/Sample_MIPIRAW10bit_Pattern_RGGB_W4000_H3000.raw",'raw_data':None}
#     tasks = [args1,args2]
#     rets = MultiCoroutine.coroutine_queue(sync_proc, tasks, 3)
#     print(np.asarray(list(rets[0]),np.uint8))
#     print(np.asarray(list(rets[1]),np.uint8))