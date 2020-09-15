from .Bilinear_interpolation import *
from .Directional_filtering import  *



_pattern='GRBG'
_method=1
category='RAW'



def setParameters(list_parameter):
    global imgpath, width, height, pattern, method
    # imgpath = list_parameter[0]
    # width = list_parameter[0]
    # height = list_parameter[1]
    # pattern = list_parameter[3]
    _method = list_parameter[0]
def run(bayer_raw):
        # bayer_raw = Mipiraw2Raw(imgpath, width, height, bits=10).toraw().reshape(height, width)
        if _method==1:
            demosaicked_rgb = directional_filtering(bayer_raw, _pattern)
        elif _method==2:
            demosaicked_rgb = binear_interpolation(bayer_raw,_pattern)
        demosaicked_rgb = raw_standardized2rgb(demosaicked_rgb)
        demosaicked_rgb = adjust_gamma(demosaicked_rgb, 2.2)
        demosaicked_rgb = (demosaicked_rgb * 255.0).astype(np.uint8)
        return demosaicked_rgb

