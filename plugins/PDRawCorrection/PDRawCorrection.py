#! /usr/bin/env python3
#-*- encoding: utf-8 -*-

__author__ = 'Zhao Hailang'

import sys
sys.path.append("pdsplit")
sys.path.append('pdsplit/raw2rgb')
import numpy as np
import argparse 
import math
#import copy as cp
import check_rules as cr
import sys
from  mipiraw2raw import Mipiraw2Raw
from fileoperations import test_run_time
from scipy import interpolate 


class PDRawCorrection(object):
    def __init__(self,path_gain:str="cas_semco_ov48c_m24c64x_pdaf_OTP.txt", path_pdaf:str="pdaf.raw", width_pdaf:int=496, height_pdaf:int=750,bits:int=10, rawtype:str="raw",buffertype:str="RL"):        
        #Public property initialization
        # parameter of padf raw
        self.path_pdaf = path_pdaf   
        self.width_pdaf = width_pdaf
        self.height_pdaf = height_pdaf
        
        self.bits=bits
        
        self.BUFFERTYPE=buffertype


        #raw data of pdaf
        self.raw_data_pdaf = None
        self.pdaf_raw_left=None
        self.pdaf_raw_right=None

        self.rawtype=rawtype

        self.path_gain=path_gain
        
    def rawtype_check(self):  
        if(bool(1-(cr.get_rawtype(self.rawtype)))):
            return -1;   #raw type error         

    def pattern_type_check(self,bits):
        return(cr.get_pattern_type(bits))
        
    def pdbuffer_type_check(self):
        print(self.BUFFERTYPE)
        
 
    def Bits_type_check(self):
        if(bool(1-(cr.get_bits_type(self.bits)))):
            return -3;   #buffer type error  
        
    def read_file(self):
        if(self.rawtype_check==-1):
            print("raw typer error!")
        
        if(self.Bits_type_check==-3):
            print("bits typer error!")   #bits type error
            
        if(self.rawtype=="mipi"):
            self.MipiRaw10toRaw()
        else:
            self.read_raw()   
        
    def MipiRaw10toRaw(self):    
        
        raw_data=Mipiraw2Raw(self.path_pdaf,self.width_pdaf,self.height_pdaf,bits=self.bits).toraw()     
        self.raw_data_pdaf=raw_data.reshape(self.height_pdaf,self.width_pdaf)
               
    def read_raw(self):
        raw_array=np.fromfile (self.path_pdaf,dtype=np.uint16)
        self.raw_data_pdaf=raw_array.reshape(self.height_pdaf,self.width_pdaf)
        
    
        
    def PdafRawDataSplit(self):  
        self.read_file()              
        self.raw_data_pdaf=self.raw_data_pdaf.reshape(self.height_pdaf,self.width_pdaf)
        
        if(self.BUFFERTYPE=="RL"):
            self.pdaf_raw_right=self.raw_data_pdaf[1::2]
            self.pdaf_raw_left=self.raw_data_pdaf[::2]
        elif(self.BUFFERTYPE=="LR"):
            self.pdaf_raw_left=self.raw_data_pdaf[::2]
            self.pdaf_raw_right=self.raw_data_pdaf[1::2]
        else:
            print("buffer type error!")
            
        return 0;
    
    def format_save(self,array):
         W=array.shape[1]
         H=array.shape[0]
         array_save=array.flatten()
         array_save=array_save.astype(np.uint16)
         
         return (W,H,array_save)  
     
    def get_gain(self):
        
        BLOCK_W = 17
        BLOCK_H = 13
        
        Gainmap_L=np.ones([BLOCK_H,BLOCK_W])
        Gainmap_R=np.ones([BLOCK_H,BLOCK_W])
        
        f=open(self.path_gain,"r",encoding='utf-8')
        line=f.readline()   
        key="Left GainMap"
        while line:
            if key in line:               
                break
            line=f.readline()
        
        for i in range(0,BLOCK_H):
            line=f.readline()              
            array=np.array(line.split(","))
            for j in range(0,BLOCK_W):
                Gainmap_L[i][j]=array[j]
        
        line=f.readline() 
        key="Right GainMap"
        if key not in line:
            print("error")
            
        for i in range(0,BLOCK_H):
            line=f.readline()              
            array=np.array(line.split(","))
            for j in range(0,BLOCK_W):
                Gainmap_R[i][j]=array[j]    
        
        Gainmap_L=Gainmap_L/256
        Gainmap_R=Gainmap_R/256
            
        return (Gainmap_L,Gainmap_R)
    @test_run_time
    def run(self):
        if(self.PdafRawDataSplit()==-1): 
            print ("pd buffer type error!")
            
        BLOCK_W = 17
        BLOCK_H = 13
        Sub_Gainmap_L=np.ones([BLOCK_H,BLOCK_W])
        Sub_Gainmap_R=np.ones([BLOCK_H,BLOCK_W])
        
        Gainmap_L=np.ones([BLOCK_H,BLOCK_W])
        Gainmap_R=np.ones([BLOCK_H,BLOCK_W])
        
        Sub_L_H=np.ones([BLOCK_H,BLOCK_W])
        Sub_L_W=np.ones([BLOCK_H,BLOCK_W])
        
        Sub_R_H=np.ones([BLOCK_H,BLOCK_W])
        Sub_R_W=np.ones([BLOCK_H,BLOCK_W])
        
        strideX=math.floor(self.pdaf_raw_left.shape[1]/BLOCK_W)
        strideY=math.floor(self.pdaf_raw_left.shape[0]/BLOCK_H)
                       
        (Gainmap_L,Gainmap_R)=self.get_gain()
        
 
        for i in range(0,BLOCK_W ):
            for j in range(0,BLOCK_H):                                  
                 Hcenter=int((j*strideY+(j+1)*strideY)/2)
                 Wcenter=int((i*strideX+(i+1)*strideX)/2)
                 Sub_L_H[j][i]=Hcenter
                 Sub_L_W[j][i]=Wcenter
                 
                 Sub_R_H[j][i]=Hcenter
                 Sub_R_W[j][i]=Wcenter

        Sub_L_H=Sub_L_H.flatten()
        Sub_L_W=Sub_L_W.flatten()
        
        Sub_R_H=Sub_L_H.flatten()
        Sub_R_W=Sub_L_W.flatten()        
         
        cols=self.pdaf_raw_left.shape[1]  #w
        rows=self.pdaf_raw_left.shape[0]  #h
        xitp = range(0,rows)
        yitp = range(0,cols)
        
        F_L=interpolate.interp2d(Sub_L_W,Sub_L_H,Gainmap_L,kind='linear')
        F_R=interpolate.interp2d(Sub_L_W,Sub_L_H,Gainmap_R,kind='linear')
        
        Zi_L=F_L(yitp,xitp)
        Zi_R=F_R(yitp,xitp)
        
        Zi_L=np.array(Zi_L)
        Zi_R=np.array(Zi_R)
        #print(Zi_L.shape,Zi_R)
        
        
        PDraw_left=self.pdaf_raw_left*Zi_L
        PDraw_right=self.pdaf_raw_right*Zi_R
        
        PDRaw_H=self.pdaf_raw_left.shape[0]  
        PDRaw_W=self.pdaf_raw_left.shape[1] 
        PDraw_all=np.ones([PDRaw_H*2,PDRaw_W])
        k=0
        for i in range(0, PDRaw_H):
            for j in range(0,PDRaw_W ):                   
               if(self.BUFFERTYPE=="LR"):
                   PDraw_all[2*i][j]=PDraw_left[i][j]
                   PDraw_all[2*i+1][j]=PDraw_right[i][j]
                   k+=1
               elif(self.BUFFERTYPE=="RL"):
                   PDraw_all[2*i][j]=PDraw_right[i][j]
                   PDraw_all[2*i+1][j]=PDraw_left[i][j]
                   k+=1  
                   
                  
        (W_PDAll,H_PDAll,PDraw_all)=self.format_save(PDraw_all)
          
        PDraw_all.tofile("W"+str(W_PDAll)+"H"+str(H_PDAll)+"PDraw_all.raw")
               
def main():
    parser = argparse.ArgumentParser(description="This is a python module that get PDAF gain map.")
    # Required parameters
       
    parser.add_argument('--path_gain', type=str, default='cas_semco_ov48c_m24c64x_pdaf_OTP.txt' ,help='eeprom gain file path')
    parser.add_argument('--path_pdaf', type=str, default='pdaf.raw' ,help='pdaf raw source file path')
    parser.add_argument('--width_pdaf', type=int, default =496, help='Image width')
    parser.add_argument('--height_pdaf', type=int, default=750,help='Image height')
    
    parser.add_argument('--bits', '-b', type=int, default=10, help='Raw precision')
    parser.add_argument('--rawtype','-r', type = str, default="raw", help='Raw type')

    parser.add_argument('--buffertype', '-bft', type = str, default="RL", help='PD buffer type')
 
    
    
    args = parser.parse_args()
    PDRawCorrection(args.path_gain,args.path_pdaf, args.width_pdaf, args.height_pdaf,args.bits,args.rawtype,args.buffertype).run()
    # python3 PDRawCorrection.py --path_gain 'cas_semco_ov48c_m24c64x_pdaf_OTP.txt' --path_pdaf 'pdaf.raw' --width_pdaf 496 --height_pdaf 750 --bits 10 --rawtype 'raw' --buffertype 'RL'
if __name__ == "__main__":
        main()
