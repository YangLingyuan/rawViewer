import numpy as np
from importlib import *
from ctypes import *

category = "YUV"
YUV_TYPE ={
    "YUV420P"  : c_uint(0xffff0001),
    "YUV422P"  : c_uint(0xffff0002),
	"YUV422SP" : c_uint(0xfff0003),
	"NV12"     : c_uint(0xfff0004),
    "NV21"     : c_uint(0xfff0005)
}
yuv_type = c_uint(0xffff0001)
width    = 0
height   = 0

yuv2rgb = cdll.LoadLibrary("plugins/yuv2rgb/libyuv2rgb.so")
# yuv2rgb.yuv_to_rgb24.argtypes = [
#     c_uint,
#     np.ctypeslib.ndpointer(dtype=np.uint8, ndim=1, flags="C_CONTIGUOUS"),
#     np.ctypeslib.ndpointer(dtype=np.uint8, ndim=1, flags="C_CONTIGUOUS"),
#     c_int,
#     c_int
# ]
def setParameters(args):
    global yuv_type,width,height
    yuv_type = YUV_TYPE[args[0]]
    width    = args[1]
    height   = args[2]

def run(input_buffer: np.ndarray):
    input_img = input_buffer.astype(np.uint8)
    print(input_img.shape)
    output_buffer = np.zeros((height,width,3)).astype(np.uint8)
    yuv2rgb.yuv_to_rgb24(
                        yuv_type,
                        input_img.ctypes.data_as(POINTER(c_uint8)), 
                        output_buffer.ctypes.data_as(POINTER(c_uint8)), 
                        width, 
                        height)
    print(output_buffer.shape)
    # output_buffer.reshape(3,width,-1)
    # print(output_buffer.shape)
    return output_buffer