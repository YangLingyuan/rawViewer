import sys
import blc
sys.path.append("python/raw2rgb")
from raw2rgb import Raw2RGB

if __name__ == "__main__":
    obj = Raw2RGB(r"sample/Sample_MIPIRAW10bit_Pattern_RGGB_W4000_H3000.raw",4000,3000,bits=10,rawtype="mipi")
    raw = obj.toraw()
    obj.torgb()

    obj.show()
    obj.rgb_array = Raw2RGB.raw2rgb(blc.run(raw, 255),4000,3000, "GRBG" ,1.0,"bayer" )
    obj.show()