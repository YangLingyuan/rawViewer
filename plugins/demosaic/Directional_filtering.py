from __future__ import division, unicode_literals

from scipy.ndimage.filters import convolve, convolve1d
# import  cv2
from  math import ceil
from  mipiraw2raw import Mipiraw2Raw
import numpy as np


def as_float_array(a):
    return np.asarray(a, dtype=np.float_)
def tsplit(a):
    a = np.asarray(a, dtype=np.float_)
    return np.array([a[..., x] for x in range(a.shape[-1])])
def tstack(a):
    a=np.asarray(a,dtype=np.float_)
    return np.concatenate([x[..., np.newaxis] for x in a], axis=-1)




def Bayer_mask(shape, pattern='RGGB'):#根据排列方式提取每个颜色通道
    pattern = pattern.upper()
    channels = dict((channel, np.zeros(shape)) for channel in 'RGB')
    for channel, (y, x) in zip(pattern, [(0, 0), (0, 1), (1, 0), (1, 1)]):
        channels[channel][y::2, x::2] = 1
    return tuple(channels[c].astype(bool) for c in 'RGB')

def _cnv_h(x, y):
    return convolve1d(x, y, mode='mirror')


def _cnv_v(x, y):
    return convolve1d(x, y, mode='mirror', axis=0)

def directional_filtering(CFA, pattern='RGGB', refining_step=True):#整个实现过程
    CFA = as_float_array(CFA)
    R_m, G_m, B_m = Bayer_mask(CFA.shape, pattern)
    h_0 = np.array([0, 0.5, 0, 0.5, 0])
    h_1 = np.array([-0.25, 0, 0.5, 0, -0.25])
    R = CFA * R_m
    G = CFA * G_m
    B = CFA * B_m
    G_H = np.where(G_m == 0, _cnv_h(CFA, h_0) + _cnv_h(CFA, h_1), G)#沿着水平方向估算G
    G_V = np.where(G_m == 0, _cnv_v(CFA, h_0) + _cnv_v(CFA, h_1), G)#沿着竖直方向估算G
    C_H = np.where(R_m == 1, R - G_H, 0)   #计算每个R/B像素和估算出G的插值（水平方向）
    C_H = np.where(B_m == 1, B - G_H, C_H)
    C_V = np.where(R_m == 1, R - G_V, 0)#同上（竖直方向）
    C_V = np.where(B_m == 1, B - G_V, C_V)
    D_H = np.abs(C_H - np.pad(C_H, ((0, 0),
                                    (0, 2)), mode=str('reflect'))[:, 2:])
    D_V = np.abs(C_V - np.pad(C_V, ((0, 2),
                                    (0, 0)), mode=str('reflect'))[2:, :])
    del h_0, h_1, CFA, C_V, C_H
    k = np.array(
        [[0, 0, 1, 0, 1],
         [0, 0, 0, 1, 0],
         [0, 0, 3, 0, 3],
         [0, 0, 0, 1, 0],
         [0, 0, 1, 0, 1]])
    d_H = convolve(D_H, k, mode='constant')
    d_V = convolve(D_V, np.transpose(k), mode='constant')
    del D_H, D_V
    mask = d_V >= d_H
    G = np.where(mask, G_H, G_V)
    M = np.where(mask, 1, 0)
    del d_H, d_V, G_H, G_V
  #找出R、B所在的行，将其所在的行全部置为1
    R_r = np.transpose(np.any(R_m == 1, axis=1)[np.newaxis]) * np.ones(R.shape)
    B_r = np.transpose(np.any(B_m == 1, axis=1)[np.newaxis]) * np.ones(B.shape)

    k_b = np.array([0.5, 0, 0.5])
    # 计算R、G行中G位置上的R
    R = np.where(
        np.logical_and(G_m == 1, R_r == 1),
        G + _cnv_h(R, k_b) - _cnv_h(G, k_b),
        R,
    )
    #计算R、B行中G位置上的R
    R = np.where(
        np.logical_and(G_m == 1, B_r == 1) == 1,
        G + _cnv_v(R, k_b) - _cnv_v(G, k_b),
        R,
    )
    #计算B、G行中G位置上的B
    B = np.where(
        np.logical_and(G_m == 1, B_r == 1),
        G + _cnv_h(B, k_b) - _cnv_h(G, k_b),
        B,
    )
    #计算R、G行中的G位置上的B
    B = np.where(
        np.logical_and(G_m == 1, R_r == 1) == 1,
        G + _cnv_v(B, k_b) - _cnv_v(G, k_b),
        B,
    )
    #计算B位置上的R
    R = np.where(
        np.logical_and(B_r == 1, B_m == 1),
        np.where(
            M == 1,
            B + _cnv_h(R, k_b) - _cnv_h(B, k_b),
            B + _cnv_v(R, k_b) - _cnv_v(B, k_b),
        ),
        R,
    )
   #计算R位置上的B
    B = np.where(
        np.logical_and(R_r == 1, R_m == 1),
        np.where(
            M == 1,
            R + _cnv_h(B, k_b) - _cnv_h(R, k_b),
            R + _cnv_v(B, k_b) - _cnv_v(R, k_b),
        ),
        B,
    )
    RGB = tstack([R, G, B])
    del R, G, B, k_b, R_r, B_r

    if refining_step:
        RGB = refining_step_function(RGB, tstack([R_m, G_m, B_m]), M)
    del M, R_m, G_m, B_m
    return RGB




def refining_step_function(RGB, RGB_m, M):  #后续细化过程

    R, G, B = tsplit(RGB)
    R_m, G_m, B_m = tsplit(RGB_m)
    M = as_float_array(M)

    del RGB, RGB_m

    R_G = R - G
    B_G = B - G

    FIR = np.ones(3) / 3

    B_G_m = np.where(
        B_m == 1,
        np.where(M == 1, _cnv_h(B_G, FIR), _cnv_v(B_G, FIR)),
        0,
    )
    R_G_m = np.where(
        R_m == 1,
        np.where(M == 1, _cnv_h(R_G, FIR), _cnv_v(R_G, FIR)),
        0,
    )

    del B_G, R_G

    G = np.where(R_m == 1, R - R_G_m, G)
    G = np.where(B_m == 1, B - B_G_m, G)


    R_r = np.transpose(np.any(R_m == 1, axis=1)[np.newaxis]) * np.ones(R.shape)

    R_c = np.any(R_m == 1, axis=0)[np.newaxis] * np.ones(R.shape)

    B_r = np.transpose(np.any(B_m == 1, axis=1)[np.newaxis]) * np.ones(B.shape)

    B_c = np.any(B_m == 1, axis=0)[np.newaxis] * np.ones(B.shape)

    R_G = R - G
    B_G = B - G

    k_b = np.array([0.5, 0, 0.5])

    R_G_m = np.where(
        np.logical_and(G_m == 1, B_r == 1),
        _cnv_v(R_G, k_b),
        R_G_m,
    )
    R = np.where(np.logical_and(G_m == 1, B_r == 1), G + R_G_m, R)
    R_G_m = np.where(
        np.logical_and(G_m == 1, B_c == 1),
        _cnv_h(R_G, k_b),
        R_G_m,
    )
    R = np.where(np.logical_and(G_m == 1, B_c == 1), G + R_G_m, R)

    del B_r, R_G_m, B_c, R_G

    B_G_m = np.where(
        np.logical_and(G_m == 1, R_r == 1),
        _cnv_v(B_G, k_b),
        B_G_m,
    )
    B = np.where(np.logical_and(G_m == 1, R_r == 1), G + B_G_m, B)
    B_G_m = np.where(
        np.logical_and(G_m == 1, R_c == 1),
        _cnv_h(B_G, k_b),
        B_G_m,
    )
    B = np.where(np.logical_and(G_m == 1, R_c == 1), G + B_G_m, B)
    del B_G_m, R_r, R_c, G_m, B_G

    R_B = R - B
    R_B_m = np.where(
        B_m == 1,
        np.where(M == 1, _cnv_h(R_B, FIR), _cnv_v(R_B, FIR)),
        0,
    )
    R = np.where(B_m == 1, B + R_B_m, R)
    R_B_m = np.where(
        R_m == 1,
        np.where(M == 1, _cnv_h(R_B, FIR), _cnv_v(R_B, FIR)),
        0,
    )
    B = np.where(R_m == 1, R - R_B_m, B)
    del R_B, R_B_m, R_m
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
#     demosaicked_rgb = directional_filtering(bayer_raw,pattern)
#     demosaicked_rgb=raw_standardized2rgb(demosaicked_rgb)
#     demosaicked_rgb = adjust_gamma(demosaicked_rgb, 2.2)
#     demosaicked_rgb = (demosaicked_rgb * 255.0).astype(np.uint8)
#     return demosaicked_rgb



# if __name__=="__main__":
#     demosaicked_rgb = demosaic_raw(imgpath='3264X2448_GRBG_10bit.RAWMIPI',width=3264,height=2448, pattern='BGGR')
#     demosaicked_rgb=cv2.cvtColor(demosaicked_rgb,cv2.COLOR_RGB2BGR)
#     demosaicked_rgb = cv2.resize(demosaicked_rgb, (int(demosaicked_rgb.shape[1]/4),int(demosaicked_rgb.shape[0]/4)))
#     cv2.imshow('demo', demosaicked_rgb)
#     cv2.waitKey(0)