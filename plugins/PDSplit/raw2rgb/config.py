#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Calculation mode switch
debug = True
release = False
parallel_computing_multi_coroutine = True
parallel_computing_multi_Progress = False
cuda_acceleration = False

if parallel_computing_multi_coroutine: # multi-coroutine
    import asyncio
    import aiofiles
elif parallel_computing_multi_Progress: # multi-Progress
    from multiprocessing import Process, Queue
elif cuda_acceleration:
    pass
    # Acceleration module
    '''
    It is planned to add CUDA support in B/S mode. 
    Limited by the use of the platform, there is currently no expansion plan.
    '''

# Release and debug mode configuration
if debug:
    from functools import wraps
    import time
    
    def test_run_time(fn):
        @wraps(fn)
        def measure_time(*args, **kwargs):
            start_time = time.time()
            res = fn(*args, **kwargs)
            end_time = time.time()
            print("M: @test_run_time: %s took %s seconds." % (fn.__name__, str(end_time - start_time)))
            return res
        return measure_time
    
    def print_e(e:str=""):
        raise Exception("E: {}".format(e))
    
    def print_m(*m_args):
        print("M: ",*m_args)
else:
    def test_run_time(fn):
        def measure_time(*args, **kwargs):
            return fn(*args, **kwargs)
        return measure_time
    
    def print_e(e:str=""):
        pass

    def print_m(m:str=""):
        pass
