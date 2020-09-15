import numpy as np
import cv2
import lens_shading
import sys
sys.path.append("python/raw2rgb")
from raw2rgb import Raw2RGB
from PIL import Image

 
def test():
    # raw = Raw2RGB(r"python/lsc/IMG_20200823_060341-004_req[1]_b[0]_IFE[0][9]_w[4000]_h[3000]_s[0]_RealtimePreviewSAT01.RawPlain16LSB12bit",4000,3000,bits=16,rawtype="rawplain")
    raw = Raw2RGB(r"python/lsc/IMG_20200823_060341-004_req[1]_b[0]_IFE[0][9]_w[4000]_h[3000]_s[0]_RealtimePreviewSAT01.RawPlain16LSB12bit",4000,3000,bits=16,rawtype="rawplain")
    raw.torgb()
    raw.show()
    # lsc_correct(src_raw_array, width, height, pattern, eeprom_lsc_data_path=None, block_height=13, block_width=17)
    raw.raw_array = lens_shading.lsc_correct(raw.raw_array, 4000, 3000,["R","GR","GB","B"],"python/lsc/cas_semco_imx586_sem1215_lsc_OTP.txt").reshape((1,-1))
    raw.torgb()
    raw.show()


if __name__=="__main__":
    test()

