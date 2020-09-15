import numpy as np
import cv2
import gain

def test(PATH):
    src_data=cv2.imread(PATH)
    gain.gain(src_data)
if __name__=="__main__":
    test('./lll.png')

