# -*- coding: utf-8 -*-
"""
Convert YUV420P/I420 to rgb

@author: Zhou Ran

usage:
python3 yuv2rgb.py -S 'suzie_qcif_yuv420p_00.yuv' -D 'test_yuv.png' -W 176 -H 144
"""


from PIL import Image
import os
import cv2
import numpy as np
import argparse

class YUV2RGB():

    def __init__(self,srcpath:str,dstpath:str,width:int,height:int):
        # Attributes initialization
        self.__srcpath = srcpath
        self.__dstpath = dstpath
        self.__width = width
        self.__height = height

        # Temporary attributes initialization
        self.img_Y = None
        self.img_U = None
        self.img_V = None
        self.rgb_array = None
    # Attribute operations
    @property
    def srcpath(self):
        return self.__srcpath 
                                                                                                                        
    @property
    def dstpath(self):
        return self.__dstpath                                                                                                                    
    
    @property
    def width(self):
        return self.__width
    
    @property
    def height(self):
        return self.__height


    # Method
    def torgb(self):
        self.__read()
        self.__convert()
        return self
    
    def __read(self):

        """
        读取YUV文件，解析为Y, U, V图像
        """
        # create Y
        self.img_Y = np.zeros((self.__height, self.__width), np.uint8)
        # print(type(self.img_Y))

        # create U,V
        self.img_U = np.zeros((int(self.__height / 2), int(self.__width / 2)), np.uint8)
        # print(type(img_U))
        # print(img_U.shape)

        self.img_V = np.zeros((int(self.__height / 2), int(self.__width / 2)), np.uint8)
        # print(type(img_V))
        # print(img_V.shape)

        with open(self.__srcpath, 'rb') as reader:
            for i in range(self.__height):
                for j in range(self.__width):
                    self.img_Y[i, j] = ord(reader.read(1))

            for i in range(int(self.__height / 2)):
                for j in range(int(self.__width / 2)):
                    self.img_U[i, j] = ord(reader.read(1))

            for i in range(int(self.__height / 2)):
                for j in range(int(self.__width / 2)):
                    self.img_V[i, j] = ord(reader.read(1))

        return self

    'works for yuv420p'
    def __convert(self):
        
        enlarge_U = cv2.resize(self.img_U, (0, 0), fx=2.0, fy=2.0, interpolation=cv2.INTER_CUBIC)
        enlarge_V = cv2.resize(self.img_V, (0, 0), fx=2.0, fy=2.0, interpolation=cv2.INTER_CUBIC)

        # merge Y U V
        img_YUV = cv2.merge([self.img_Y, enlarge_U, enlarge_V])

        self.rgb_array = cv2.cvtColor(img_YUV, cv2.COLOR_YUV2BGR)
        return self

    def show(self):
        cv2.imshow("rgb", self.rgb_array)
    
    def save(self):
        cv2.imwrite(self.__dstpath, self.rgb_array)

    def run(self):
        return self.torgb()

        
    


def main():
    "Invoke a single module from the command line"
    parser = argparse.ArgumentParser(description="This is a python module that parses yuv420P format.")
    
    # Required parameters
    parser.add_argument('--srcpath', '-S', help='yuv file path', required=True)
    parser.add_argument('--dstpath', '-D', help='result file path', required=True)
    parser.add_argument('--width', '-W', type=int, help=' width', required=True)
    parser.add_argument('--height', '-H', type=int, help=' height', required=True)
    args = parser.parse_args() 

    # Call main function
    dst = YUV2RGB(args.srcpath,
                  args.dstpath,
                  args.width,
                  args.height).torgb()
    #test
    #dst = YUV2RGB('suzie_qcif_yuv420p_00.yuv','test_yuv.png',176,144).torgb()
    dst.show()
    dst.save()

    cv2.waitKey(0) 

if __name__ == '__main__':
    main()
    
  
