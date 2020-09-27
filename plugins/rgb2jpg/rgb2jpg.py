import numpy as np
# import cv2
from PIL import Image, ImageDraw

category="RGB"
def setParameters(l):
    return 1


def run(rgb_array, number=0):
    if isinstance(rgb_array, np.ndarray):
        output = Image.fromarray(rgb_array)
        # cv2.imshow("img",rgb_array)
    elif isinstance(rgb_array, list):
        output = Image.fromarray(rgb_array[number])
    output.show()