from .Bilinear_interpolation import *
from .Directional_filtering import  *



_pattern='GRBG'
_method=1
category='RAW'



def setParameters(list_parameter):
    global  _method
    _method = list_parameter[0]
def run(bayer_raw):
    global  _method
        # bayer_raw = Mipiraw2Raw(imgpath, width, height, bits=10).toraw().reshape(height, width)
    if _method==1:
        demosaicked_rgb = directional_filtering(bayer_raw, _pattern)
    elif _method==2:
        demosaicked_rgb = binear_interpolation(bayer_raw,_pattern)
    demosaicked_rgb = raw_standardized2rgb(demosaicked_rgb)
    demosaicked_rgb = adjust_gamma(demosaicked_rgb, 2.2)
    demosaicked_rgb = (demosaicked_rgb * 255.0).astype(np.uint8)
    print("demosaicked_rgb shape:")
    print(demosaicked_rgb.shape)
    return demosaicked_rgb

