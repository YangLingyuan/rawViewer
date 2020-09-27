#! /usr/bin/env python3
#-*- encoding: utf-8 -*-

__author__ = 'Zhao Hailang'

import sys
sys.path.append("pdsplit")
sys.path.append('pdsplit/raw2rgb')
import numpy as np
import argparse 
import math
import copy as cp
import check_rules as cr
import sys
from  mipiraw2raw import Mipiraw2Raw
from fileoperations import test_run_time
from PDSplit import PDsplit
from scipy import interpolate 
        
class PDGainmap(object):
    def __init__(self,path_pdaf:str="pdaf.raw", width_pdaf:int=496, height_pdaf:int=750, path_o:str="original.raw", width_o:int=4000, height_o:int=3000,bits:int=10, rawtype:str="raw",pattern:str="GRBG",buffertype:str="RL",PDpattern:str="G"):        
        #Public property initialization
        # parameter of padf raw
        self.path_pdaf = path_pdaf   
        self.width_pdaf = width_pdaf
        self.height_pdaf = height_pdaf
        
        #parameter of original raw
        self.path_o = path_o   
        self.width_o = width_o  
        self.height_o = height_o
        self.bits=bits
        
        self.BUFFERTYPE=buffertype
        self.pattern=pattern

        #raw data of pdaf
        self.raw_data_pdaf = None
        self.pdaf_raw_left=None
        self.pdaf_raw_right=None

        #raw data of original raw
        
        self.raw_data_o=None
        self.G=None
        self.AvgG=None
        self.Sub_AvgG=None
        
        self.PDpattern=PDpattern
        
        self.rawtype=rawtype

    def rawtype_check(self):  
        if(bool(1-(cr.get_rawtype(self.rawtype)))):
            return -1;   #raw type error         

    def pattern_type_check(self,bits):
        return(cr.get_pattern_type(bits))
        
    def pdbuffer_type_check(self):
        print(self.BUFFERTYPE)
        
        #if(bool(1-(cr.get_buffer_type(self.BUFFERTYPE)))):           
        #    return -2;   #buffer type error  
 
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
        
        raw_data=Mipiraw2Raw(self.path_o,self.width_o,self.height_o,bits=self.bits).toraw()     
        self.raw_data_o=raw_data.reshape(self.height_o,self.width_o)       
        
    def read_raw(self):
        raw_array=np.fromfile (self.path_o,dtype=np.uint16)
        self.raw_data_o=raw_array.reshape(self.height_o,self.width_o)
        
    def Get_SubGreen_center(self):
        if(bool(1-(self.pattern_type_check(self.pattern)))):
           return -2;   #patter type error
        
        self.read_file()
        
        center_H=int(self.height_o/2)
        center_W=int(self.width_o/2)
        if(center_H%2==0):
            center_H=center_H+1
        if(center_W%2==0):
            center_W=center_W+1
                            
        offset_h=int(self.height_o/64/2)
        offset_w=int(self.width_o/64/2)
        
        Start_H=center_H-1-offset_h
        End_H=Start_H+offset_h*2+2
        
        Start_W=center_W-1-offset_w
        End_W=Start_W+offset_w*2+2 
        
        sub_raw_o=self.raw_data_o[Start_H-1:End_H+1,Start_W-1:End_W+1]
 
        sub_H=sub_raw_o.shape[0]
        sub_W=sub_raw_o.shape[1]
            
        sub_Gimage=cp.deepcopy(sub_raw_o[1:sub_H-1,1:sub_W-1])
        sub_Rimage=cp.deepcopy(sub_raw_o[1:sub_H-1,1:sub_W-1])
        sub_Bimage=cp.deepcopy(sub_raw_o[1:sub_H-1,1:sub_W-1])
        #print (sub_Gimage.shape[0],sub_Gimage.shape[1],sub_H,sub_W)    
        
        if (self.pattern=="RGGB"):
            for i in range(1,sub_H-1,2):
                for j in range(1,sub_W-1,2):
                    m=i-1
                    n=j-1
                    temp=(sub_raw_o[i+1][j]+sub_raw_o[i][j+1]+sub_raw_o[i][j-1]+sub_raw_o[i-1][j])/4
                    sub_Gimage[m][n]=temp
                    sub_Gimage[m+1][n+1]=temp
                    
                    sub_Rimage[m][n+1]=(sub_raw_o[i][j-1]+sub_raw_o[i][j+1])/2
                    sub_Rimage[m+1][n]=(sub_raw_o[i][j-1]+sub_raw_o[i][j+1])/2 
                    sub_Rimage[m+1][n+1]=(sub_Rimage[m][n+1]+sub_Rimage[m+1][n])/2 
                                       
                    sub_Bimage[m][n+1]=(sub_raw_o[i-1][j]+sub_raw_o[i+1][j])/2
                    sub_Bimage[m+1][n]=(sub_raw_o[i][j-1]+sub_raw_o[i][j+1])/2
                    sub_Bimage[m][n]=(sub_Bimage[m][n+1]+sub_Bimage[m+1][n])/2
                    
        elif(self.pattern=="BGGR"):
            for i in range(1,sub_H-1,2):
                for j in range(1,sub_W-1,2):
                    m=i-1
                    n=j-1
                    temp=(sub_raw_o[i+1][j]+sub_raw_o[i][j+1]+sub_raw_o[i][j-1]+sub_raw_o[i-1][j])/4
                    sub_Gimage[i-1][j-1]=temp
                    sub_Gimage[i][j]=temp 

                    sub_Rimage[m][n+1]=(sub_raw_o[i-1][j]+sub_raw_o[i+1][j])/2
                    sub_Rimage[m+1][n]=(sub_raw_o[i][j-1]+sub_raw_o[i][j+1])/2 
                    sub_Rimage[m][n]=(sub_Rimage[m][n+1]+sub_Rimage[m+1][n])/2 
                                       
                    sub_Bimage[m][n+1]=(sub_raw_o[i][j-1]+sub_raw_o[i][j+1])/2
                    sub_Bimage[m+1][n]=(sub_raw_o[i-1][j]+sub_raw_o[i+1][j])/2
                    sub_Bimage[m+1][n+1]=(sub_Bimage[m][n+1]+sub_Bimage[m+1][n])/2
                                      
        elif(self.pattern=="GRBG"):
            for i in range(1,sub_H-1,2):
                for j in range(1,sub_W-1,2):
                    m=i-1
                    n=j-1                    
                    temp=(sub_raw_o[i+1][j]+sub_raw_o[i][j+1]+sub_raw_o[i][j-1]+sub_raw_o[i-1][j])/4
                    sub_Gimage[i][j-1]=temp
                    sub_Gimage[i-1][j]=temp 
                    
                    sub_Rimage[m][n]=(sub_raw_o[i][j-1]+sub_raw_o[i][j+1])/2
                    sub_Rimage[m+1][n+1]=(sub_raw_o[i-1][j]+sub_raw_o[i+1][j])/2 
                    sub_Rimage[m+1][n]=(sub_Rimage[m][n]+sub_Rimage[m+1][n+1])/2 
                                       
                    sub_Bimage[m][n]=(sub_raw_o[i-1][j]+sub_raw_o[i+1][j])/2
                    sub_Bimage[m+1][n+1]=(sub_raw_o[i][j-1]+sub_raw_o[i][j+1])/2
                    sub_Bimage[m][n+1]=(sub_Bimage[m][n]+sub_Bimage[m+1][n+1])/2                    
                        
        if(self.PDpattern=="R"):
            self.Sub_AvgG =  int(np.mean(sub_Gimage)) 
        elif(self.PDpattern=="G"):
            self.Sub_AvgG =  int(np.mean(sub_Gimage)) 
        elif(self.PDpattern=="B"):
            self.Sub_AvgG =  int(np.mean(sub_Gimage)) 
           
        return self.Sub_AvgG

    def Get_Green_center(self):
        if(bool(1-(self.pattern_type_check(self.pattern)))):
           return -2;   #patter type error
              
        self.read_file()
        if (self.pattern=="RGGB") or(self.pattern=="BGGR"):                           
            center_H=int(self.height_o/2)
            if(center_H%2==0):
                center_W=(int(self.width_o/4))*2
            else:
                center_W=(int(self.width_o/4))*2+1
            
        elif(self.pattern=="GRBG"):
            center_H=int(self.height_o/2)
            if(center_H%2==0):
                center_W=(int(self.width_o/4))*2+1
            else:
                center_W=(int(self.width_o/4))*2
                
        self.AvgG= (self.raw_data_o[center_H][center_W-1]+self.raw_data_o[center_H-1][center_W]+self.raw_data_o[center_H][center_W+1]++self.raw_data_o[center_H+1][center_W])/4
       
        return (self.AvgG)
        
    def PdafRawDataSplit(self):
        
        #if(bool(1-(self.pdbuffer_type_check(self.BUFFERTYPE)))):
        #    return -1;   
        self.read_file()
        
        
        array=np.fromfile (self.path_pdaf,dtype=np.uint16)       
        self.raw_data_pdaf=array.reshape(self.height_pdaf,self.width_pdaf)
            
        if(self.BUFFERTYPE=="RL"):
            self.pdaf_raw_right=self.raw_data_pdaf[::2]
            self.pdaf_raw_left=self.raw_data_pdaf[1::2]
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
               
        AvgG=self.Get_SubGreen_center()
        #AvgG=int((self.Get_Green_center()+self.Get_SubGreen_center())/2)
        #AvgG=self.Get_Green_center()
        
        if(AvgG==-2):
            print ("patter type error!")
 
        
        for i in range(0,BLOCK_W ):
            for j in range(0,BLOCK_H):                  
                 #Sub_Gainmap_L[j,i]= int(max(256*(AvgG/(np.mean(self.pdaf_raw_left[j*strideY:(j+1)*strideY,i*strideX:(i+1)*strideX]))),1))
                 Sub_Gainmap_L[j,i]= int(max(256*(AvgG/(np.mean(self.pdaf_raw_left[j*strideY:(j+1)*strideY,i*strideX:(i+1)*strideX]))),256))
                 Sub_Gainmap_R[j,i] =int(max(256*(AvgG/(np.mean(self.pdaf_raw_right[j*strideY:(j+1)*strideY,i*strideX:(i+1)*strideX]))),256))

                 Gainmap_R[j,i]= ((AvgG/(np.mean(self.pdaf_raw_right[j*strideY:(j+1)*strideY,i*strideX:(i+1)*strideX]))))
                 Gainmap_L[j,i]= ((AvgG/(np.mean(self.pdaf_raw_left[j*strideY:(j+1)*strideY,i*strideX:(i+1)*strideX]))))

                 
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
         
        cols=self.pdaf_raw_left.shape[1] 
        rows=self.pdaf_raw_left.shape[0]  
        xitp = range(0,rows)
        yitp = range(0,cols)
        
        F_L=interpolate.interp2d(Sub_L_W,Sub_L_H,Gainmap_L)
        F_R=interpolate.interp2d(Sub_L_W,Sub_L_H,Gainmap_R)
        
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
        (W_PDL,H_PDL,PDraw_L)=self.format_save(PDraw_left)        
        (W_PDR,H_PDR,PDraw_R)=self.format_save(PDraw_right)
        
        PDraw_L.tofile("W"+str(W_PDL)+"H"+str(H_PDL)+"PDRawLeft.raw")     
        PDraw_R.tofile("W"+str(W_PDR)+"H"+str(H_PDR)+"PDRawRight.raw")
        
        PDraw_all.tofile("W"+str(W_PDAll)+"H"+str(H_PDAll)+"PDraw_all.raw")
        
        
        #
        str_Header = np.array(["-------------PDAF data----------\nMapWidth 17, MapHeight 13"])
        str_Left = np.array(["-----------Left GainMap----------------"])
        str_Right = np.array(["-----------Right GainMap----------------"])
        
        np.savetxt("GainMap.txt",str_Header,fmt="%s")
        
        with open('GainMap.txt','ab') as f:
            np.savetxt(f,str_Left,fmt="%s")
            np.savetxt(f,Sub_Gainmap_L, fmt="%d",delimiter=", ")
            np.savetxt(f,str_Right,fmt="%s")
            np.savetxt(f,Sub_Gainmap_R, fmt="%d",delimiter=", ")

          
def main():
    parser = argparse.ArgumentParser(description="This is a python module that get PDAF gain map.")
    # Required parameters
     
    parser.add_argument('--path_pdaf', type=str, default='pdaf.raw' ,help='pdaf raw source file path')
    parser.add_argument('--width_pdaf', type=int, default =496, help='Image width')
    parser.add_argument('--height_pdaf', type=int, default=750,help='Image height')
    
    parser.add_argument('--path_o',type=str,  default='original.raw' ,help='original raw source file path')
    parser.add_argument('--width_o', type=int,default =4000, help='Image width')
    parser.add_argument('--height_o', type=int, default=3000,help='Image height')
    parser.add_argument('--bits', '-b', type=int, default=10, help='Raw precision')
    parser.add_argument('--rawtype','-r', type = str, default="raw", help='Raw type')
    
    parser.add_argument('--pattern', '-p', type = str, default="GRBG", help='Image bayer pattern')
    parser.add_argument('--buffertype', '-bft', type = str, default="RL", help='PD buffer type')
    parser.add_argument('--PDpattern', '-PDp', type = str, default="G", help='PD type') 
    
    
    args = parser.parse_args()
    PDGainmap(args.path_pdaf, args.width_pdaf, args.height_pdaf,args.path_o, args.width_o, args.height_o,args.bits,args.rawtype,args.pattern,args.buffertype,args.PDpattern).run()
    # python3 PDGainmap.py --path_pdaf pdaf.raw --width_pdaf 496 --height_pdaf 750 --path_o original.raw --width_o 4000 --height_o 3000 
if __name__ == "__main__":
        main()
