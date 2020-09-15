#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'Zheng Jiacheng'
__version__ = '0.0.1'

import asyncio
import aiofiles
import random
import numpy as np

try:
    from .config import *
except ImportError:
    from config import *

#Multi-coroutine computing channel
class MultiCoroutine():
    
    @classmethod
    @test_run_time
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