# import  cv2
from  math import ceil
# from  mipiraw2raw import Mipiraw2Raw
from .Directional_filtering import *
import numpy as np
def as_float_array(a):
    return np.asarray(a, dtype=np.float_)
def tsplit(a):
    a = np.asarray(a, dtype=np.float_)
    return np.array([a[..., x] for x in range(a.shape[-1])])
def tstack(a):
    a=np.asarray(a,dtype=np.float_)
    return np.concatenate([x[..., np.newaxis] for x in a], axis=-1)

def binear_interpolation(CFA,pattern="GRBG"):
    CFA = as_float_array(CFA)
    R_m, G_m, B_m = Bayer_mask(CFA.shape, pattern)

    H_G = as_float_array(
         [[0, 1, 0],
         [1, 4, 1],
         [0, 1, 0]]) / 4  # yapf: disable

    H_RB = as_float_array(
    [[1, 2, 1],
     [2, 4, 2],
     [1, 2, 1]]) / 4  # yapf: disable

    R = convolve(CFA * R_m, H_RB)
    G = convolve(CFA * G_m, H_G)
    B = convolve(CFA * B_m, H_RB)

    del R_m, G_m, B_m, H_RB, H_G

    return tstack([R, G, B])



def cr_stride_calc(width, bits):
    return {8:width, 10:ceil(width*10/8), 12:ceil(width*12/8), 14:ceil(width*14/8), 16:width}[bits]



def adjust_gamma(image, gamma = 1):  #伽马矫正
    image = np.clip(image.astype(np.float64) / 255.0, 0, 1)
    invGamma = 1.0 / gamma
    return np.power(image, invGamma)

def raw_standardized2rgb(raw_array):  #16bits transfer to 8bit
    raw_array_min = np.min(raw_array)
    raw_array_max = np.max(raw_array)
    rgb_array = np.array(np.rint(255 * (raw_array - raw_array_min) / (raw_array_max - raw_array_min)), dtype=np.uint8)
    return rgb_array



# def demosaic_raw(imgpath="3264X2448_GRBG_10bit.RAWMIPI",width=3264,height=2448,pattern='GRBG' ):
#     bayer_raw=Mipiraw2Raw(imgpath,width,height,bits=10).toraw().reshape(height,width)
#     demosaicked_rgb = binear_interpolation(bayer_raw,pattern)
#     demosaicked_rgb=raw_standardized2rgb(demosaicked_rgb)
#     demosaicked_rgb = adjust_gamma(demosaicked_rgb, 2.2)
#     demosaicked_rgb = (demosaicked_rgb * 255.0).astype(np.uint8)
#     return demosaicked_rgb



# if __name__=="__main__":
#     demosaicked_rgb = demosaic_raw("3264X2448_GRBG_10bit.RAWMIPI",3264,2448, 'BGGR')
#     demosaicked_rgb=cv2.cvtColor(demosaicked_rgb,cv2.COLOR_RGB2BGR)
#     demosaicked_rgb = cv2.resize(demosaicked_rgb, (int(demosaicked_rgb.shape[1]/4),int(demosaicked_rgb.shape[0]/4)))
#     cv2.imshow('demo', demosaicked_rgb)
#     cv2.waitKey(0)