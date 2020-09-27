#! /usr/bin/env python3
#-*- encoding: utf-8 -*-

import sys
sys.path.append('raw2rgb')
from xml.dom import minidom
import numpy as np
import argparse 
import xml.etree.ElementTree as ET
import copy as cp
import check_rules as cr
from  mipiraw2raw import Mipiraw2Raw

class PDsplit(object):
    def __init__(self, XMlpath:str, path_raw:str,rawtype:str,width:int, height:int,bits:int,buffertype:str):        
    
        #parameter of original raw
        self.XMlpath = XMlpath  
        self.width = width 
        self.height = height
        
        self.blockCoordinate_L=None
        self.blockCoordinate_R=None
        
        self.raw_data=None
        self.bits=bits
        self.path_raw=path_raw
        
        self.Coordinate_all_L=None
        self.Coordinate_all_R=None
        
        self.rawtype=rawtype
        self.buffertype=buffertype

    def rawtype_check(self):  
        if(bool(1-(cr.get_rawtype(self.rawtype)))):
            return -1;   #raw type error         

    def pattern_type_check(self,bits):
        return(cr.get_pattern_type(bits))
        
    def pdbuffer_type_check(self):
        if(bool(1-(cr.get_buffer_type(self.buffertype)))):
            return -2;   #buffer type error  
 
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
        
        self.raw_data=Mipiraw2Raw(self.path_raw,self.width,self.height,bits=self.bits).toraw()  
    
        self.raw_data=self.raw_data.reshape(self.height,self.width)
        
    def read_raw(self):
        raw_array=np.fromfile (self.path_raw,dtype=np.uint16)
        self.raw_data=raw_array.reshape(self.height,self.width)        
 
    def get_coordinate_block(self):
        
        xml_path=self.XMlpath
        
        dom=minidom.parse(xml_path) 
        PDX=dom.getElementsByTagName("PDXCoordinate") 
        PDY=dom.getElementsByTagName("PDYCoordinate")
        PDInf=dom.getElementsByTagName("PDPixelShieldInformation")
        
        len_Coordinate=len(PDX)
        blockCoordinate_L=np.ones([int(len(PDX)/2),2])
        blockCoordinate_R=np.ones([int(len(PDX)/2),2])
        k=0
        j=0
        for i in range(len_Coordinate):
            if(PDInf[i].firstChild.data=="LEFTSHIELDED"):
                blockCoordinate_L[k][0]=int(PDX[i].firstChild.data)     #W
                blockCoordinate_L[k][1]=int(PDY[i].firstChild.data)     #H
                k+=1
            else:
                blockCoordinate_R[j][0]=int(PDX[i].firstChild.data)   
                blockCoordinate_R[j][1]=int(PDY[i].firstChild.data)
                j+=1
                
        self.blockCoordinate_L=blockCoordinate_L
        self.blockCoordinate_R=blockCoordinate_R    
        
        return (blockCoordinate_L,blockCoordinate_R)
    
    def get_coordinate_all(self):  
        xml_path=self.XMlpath
        tree = ET.parse(xml_path)
        #rect={}
        root = tree.getroot()     
        
        for bndbox in root.iter('PDBlockDimensions'):
            for width in bndbox.iter('width'):
                block_w = int(width.text)
            for height in bndbox.iter('height'):
                block_h= int(height.text)   
                                 
        for PD_W in root.iter('PDBlockCountHorizontal'):
            PD_BLO_W=int(PD_W.text)            
        for PD_H in root.iter('PDBlockCountVertical'):
            PD_BLO_H=int(PD_H.text)       
                    
        blockCoordinate_L,blockCoordinate_R=self.get_coordinate_block()
                
        block_h_L=blockCoordinate_L.shape[0]
        
        block_mov_L=cp.deepcopy(blockCoordinate_L)
        block_mov_R=cp.deepcopy(blockCoordinate_R)
        
        k=0
        Coordinate_all_L=np.ones([PD_BLO_W*(PD_BLO_H)*block_h_L,2])
        Coordinate_all_R=np.ones([PD_BLO_W*(PD_BLO_H)*block_h_L,2])
    
        
        for i in range(0, PD_BLO_H):
            for j in range(0,block_h_L ):
                block_mov_L[j][0]=blockCoordinate_L[j][0]
                block_mov_L[j][1]=blockCoordinate_L[j][1]+block_h*i
                
                block_mov_R[j][0]=blockCoordinate_R[j][0]
                block_mov_R[j][1]=blockCoordinate_R[j][1]+block_h*i
                                
            for m in range(0,PD_BLO_W ):                  
                for n in range(0,block_h_L ):
                    Coordinate_all_L[k][1]=int(block_mov_L[n][1])
                    Coordinate_all_L[k][0]=int(block_mov_L[n][0]+block_w*m)
                    Coordinate_all_R[k][1]=int(block_mov_R[n][1])
                    Coordinate_all_R[k][0]=int(block_mov_R[n][0]+block_w*m)
                    k=k+1
                    
                    
                  
        Coordinate_all_L=Coordinate_all_L[:,[1,0]] #sawap 0 and 1 clom
        Coordinate_all_R=Coordinate_all_R[:,[1,0]]
         
         
        index1=np.lexsort([Coordinate_all_L[:,1], Coordinate_all_L[:,0]])
        self.Coordinate_all_L=Coordinate_all_L[index1,:]
        self.Coordinate_all_L=self.Coordinate_all_L.astype(int)
        
        
        
        index2=np.lexsort([Coordinate_all_R[:,1], Coordinate_all_R[:,0]])
        self.Coordinate_all_R=Coordinate_all_R[index2,:]
        self.Coordinate_all_R=self.Coordinate_all_R.astype(int)
           
        
        return (PD_BLO_W,PD_BLO_H)
   
    def format_save(self,array):
         W=array.shape[1]
         H=array.shape[0]
         array_save=array.flatten()
         array_save=array_save.astype(np.uint16)
         
         return (W,H,array_save)
    
    def run(self): 
        if(self.read_file()==-3):
            print("bits type error!")
        (PD_BLO_W,PD_BLO_H)=self.get_coordinate_all()
        
        count=0
        while self.Coordinate_all_L[count][0]==self.Coordinate_all_L[count+1][0]:
            count+=1
          
        PDRaw_W=count+1
        PDRaw_H=int(len(self.Coordinate_all_L)/PDRaw_W)
        
        
        PDraw_left=np.ones([PDRaw_H,PDRaw_W])
        PDraw_right=np.ones([PDRaw_H,PDRaw_W])
        PDraw_all=np.ones([PDRaw_H*2,PDRaw_W])
        k=0
        
        for i in range(0, PDRaw_H):
            for j in range(0,PDRaw_W ):        
               PDraw_left[i][j]=self.raw_data[self.Coordinate_all_L[k][0]][self.Coordinate_all_L[k][1]]
               PDraw_right[i][j]=self.raw_data[self.Coordinate_all_R[k][0]][self.Coordinate_all_R[k][1]]
               
               
               if(self.buffertype=="LR"):
                   PDraw_all[2*i][j]=PDraw_left[i][j]
                   PDraw_all[2*i+1][j]=PDraw_right[i][j]
                   k+=1
               elif(self.buffertype=="RL"):
                   PDraw_all[2*i][j]=PDraw_right[i][j]
                   PDraw_all[2*i+1][j]=PDraw_left[i][j]
                   k+=1                   
               elif(self.pdbuffer_type_check==-2):
                   print("pdbuffer type error!")
          
        #print (PDraw_all)           
        (W_PDAll,H_PDAll,PDraw_all)=self.format_save(PDraw_all)
        (W_PDL,H_PDL,PDraw_L)=self.format_save(PDraw_left)        
        (W_PDR,H_PDR,PDraw_R)=self.format_save(PDraw_right)
        
           
        PDraw_L.tofile("W"+str(W_PDL)+"H"+str(H_PDL)+"PDRawLeft.raw")     
        PDraw_R.tofile("W"+str(W_PDR)+"H"+str(H_PDR)+"PDRawRight.raw")  
        PDraw_all.tofile("W"+str(W_PDAll)+"H"+str(H_PDAll)+"PDraw_all.raw")
        
        
        return (PDraw_all,H_PDAll,W_PDAll)
               
def main():
    
    parser = argparse.ArgumentParser(description="This is a python module that  PD raw Split.")
   
    parser.add_argument('--XMlpath',type=str,  default='ov08a10_pdaf.xml' ,help='original raw source file path')
    parser.add_argument('--path_raw',type=str,  default='OriginalMiPIRaw.raw' ,help='original raw source file path include PD piexl')
    parser.add_argument('--rawtype','-r', type = str, default="mipi", help='Raw type')
    parser.add_argument('--width', type=int,default =3264, help='Image width')
    parser.add_argument('--height', type=int, default=2448,help='Image height')
    parser.add_argument('--bits', '-b', type=int, default=10, help='Raw precision')
    parser.add_argument('--buffertype', '-bft', type = str, default="LR", help='PD buffer type')
    args = parser.parse_args()
    PDsplit(args.XMlpath, args.path_raw,args.rawtype,args.width, args.height,args.bits,args.buffertype).run()

if __name__ == "__main__":
        main()

