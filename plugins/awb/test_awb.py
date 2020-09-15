import sys
import awb
import cv2
import numpy as np
import time
from awb_before_demosaic import *
sys.path.append("../demosaic")
from raw2camerargb import *

# 对本地图片进行awb处理
def test_awb():
    orgImg = cv2.imread("test.png")
    b, g, r = cv2.split(orgImg)

    rgb_array = np.array([r,g,b]).T

    start_time = time.time()
    rgb_array= awb.run(rgb_array)
    end_time = time.time()
    print("awb run time %s" % str(end_time - start_time))

    merged = cv2.merge([rgb_array[:,:,2].T,rgb_array[:,:,1].T,rgb_array[:,:,0].T])

    cv2.imwrite('test_awb.jpg', merged)

def test_awb_before_demosaic():#demosaic 之前进行awb
    imgpath = "/home/sifei/PycharmProjects/GitLab/CViewer/python/demosaic/3264X2448_GRBG_10bit.RAWMIPI"  #
    bayer_raw = Mipiraw2Raw(imgpath, 3264, 2448, bits=10).toraw().reshape(2448, 3264)
    bayer_raw=raw_white_balance(bayer_raw,pattern='BGGR')
    demosaicked_rgb = demosaic_raw(bayer_raw,'BGGR')
    demosaicked_rgb=cv2.cvtColor(demosaicked_rgb,cv2.COLOR_RGB2BGR)
    demosaicked_rgb = cv2.resize(demosaicked_rgb, (int(demosaicked_rgb.shape[1]/2),int(demosaicked_rgb.shape[0]/2)))
    cv2.imshow('awb_before_demosaic', demosaicked_rgb)
    cv2.waitKey(0)
# demosaic 后对图片进行awb处理
def awb_after_demosaic():
    imgpath = "/home/sifei/PycharmProjects/GitLab/CViewer/python/demosaic/3264X2448_GRBG_10bit.RAWMIPI"  #


    bayer_raw=Mipiraw2Raw(imgpath,3264,2448,bits=10).toraw().reshape(2448,3264)
    #bayer_raw=raw_white_balance(bayer_raw,'BGGR')
    demosaicked_rgb = demosaic_raw(bayer_raw,'BGGR')
    demosaicked_rgb = awb.run(demosaicked_rgb)
    demosaicked_rgb=cv2.cvtColor(demosaicked_rgb,cv2.COLOR_RGB2BGR)
    demosaicked_rgb = cv2.resize(demosaicked_rgb, (int(demosaicked_rgb.shape[1]/2),int(demosaicked_rgb.shape[0]/2)))
    cv2.imshow('awb_after_demosaic', demosaicked_rgb)
   # cv2.waitKey(0)

if __name__ == "__main__":

    #test_awb()
    awb_after_demosaic()
    test_awb_before_demosaic()




