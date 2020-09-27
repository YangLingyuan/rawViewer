import sys
import cv2
import numpy as np
import time
import awb_before_demosaic 
sys.path.append("python/raw2rgb")
from mipiraw2raw import *
from raw2rgb import *
sys.path.append("python/demosaic")
import demosaic
import common_func



def test_awb_before_demosaic(imgpath="python/demosaic/3264X2448_GRBG_10bit.RAWMIPI",width=3264,height=2448,pattern='BGGR' ):
    bayer_raw=Mipiraw2Raw(imgpath,width,height,bits=10).toraw().reshape(height,width)
    awb_before_demosaic.setParameters([pattern,10])
    bayer_raw=awb_before_demosaic.run(bayer_raw)
    demosaicked_rgb = demosaic.run(bayer_raw,pattern)
    demosaicked_rgb = Raw2RGB.raw_standardized2rgb(demosaicked_rgb)
    demosaicked_rgb = common_func.adjust_gamma(demosaicked_rgb, 2.2)
    demosaicked_rgb = (demosaicked_rgb * 255.0).astype(np.uint8)
    demosaicked_rgb = cv2.cvtColor(demosaicked_rgb,cv2.COLOR_RGB2BGR)
    demosaicked_rgb = cv2.resize(demosaicked_rgb, (int(demosaicked_rgb.shape[1]/2),int(demosaicked_rgb.shape[0]/2)))
    cv2.imwrite('python/awb_before_demosaic/awb_before_demosaic.jpg', demosaicked_rgb)

if __name__ == "__main__":
    test_awb_before_demosaic()




