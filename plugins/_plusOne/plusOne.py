import numpy as np
from importlib import *
from ctypes import *


plusOne = cdll.LoadLibrary("./libplusOne.so")
io_arry = np.zeros(5).astype(np.uint8)
plusOne.run(io_arry.ctypes.data_as(POINTER(c_uint8)),5)
print(io_arry)