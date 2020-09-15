import numpy as np
# import cv2
from matplotlib import pyplot as plt
import math

category='RAW'

def read_lsc_eeprom_data(eeprom_lsc_data_path, block_height, block_width):
   with open(eeprom_lsc_data_path,'rb') as f:
      try:
         gain_map = f.readlines()
      except Exception as e:
         print(e)
         return None
   gain_map = [str(item, encoding="utf-8") for item in gain_map]
   gain_lines_dict = {  "R":gain_map.index("r_gain:\n")+1,
                        "GR":gain_map.index("gr_gain:\n")+1,
                        "GB":gain_map.index("gb_gain:\n")+1,
                        "B":gain_map.index("b_gain:\n")+1}
   gain_dict = {"R":list(),"GR":list(),"GB":list(),"B":list()}
   for index in range(block_height):
      for key in gain_dict.keys():
         gain_dict[key].append([float(item) for item in gain_map[gain_lines_dict[key]+index].split()])
   return {key: np.array(value, dtype=np.float32) for key,value in gain_dict.items()}

# def bayer_channel_interation(R_new,GR_new,GB_new,B_new,pattern='GRBG'):
#    size=int(R_new.size*4)
#    new_img=np.zeros(size,dtype=np.uint16)
#    height=int(2*len(R_new))
#    width=int(2*R_new.size/len(R_new))
#    new_img=new_img.reshape(height,width)
#    new_img[0::2,0::2]=R_new
#    new_img[0::2,1::2]=GR_new
#    new_img[1::2,0::2]=GB_new
#    new_img[1::2,1::2]=B_new
#    return new_img

def apply_shading_to_image(raw_array, pattern, height_block, width_block, gain_map_dict):
   raw_array_channel = [raw_array[0::2,0::2],raw_array[0::2,1::2],raw_array[1::2,0::2],raw_array[1::2,1::2]]
   raw_array_dict = dict()
   res_array =np.zeros(raw_array.shape,dtype=np.uint16)

   for index in range(4):
      raw_array_dict[pattern[index]] =  raw_array_channel[index]

   original_H, original_W = raw_array_dict["R"].shape

   H = math.ceil((original_H + height_block)/height_block) * height_block
   W = math.ceil((original_W + width_block)/ width_block) * width_block

   interpolation_size = (W, H)
   H_half_b_size, W_half_b_size = int(height_block / 2), int(width_block / 2)
   for item in ["R","GR","GB","B"]:
      gain_map_dict[item] = cv2.resize(gain_map_dict[item], interpolation_size)
      gain_map_dict[item] = gain_map_dict[item][H_half_b_size :H_half_b_size + original_H, W_half_b_size:W_half_b_size + original_W]
      raw_array_dict[item] = raw_array_dict[item] / (gain_map_dict[item]/1023)

   for row,col,channel in [[0,0,0],[0,1,1],[1,0,2],[1,1,3]]:
      res_array[row::2,col::2] = raw_array_dict[pattern[channel]]
# np.clip(res_array, a_min=0, a_max=1023)
   return res_array

# #校正数据的生成
# def creat_lsc_data(img, height_block, width_block, pattern):
#    # 分开四个颜色通道
#    R, GR, GB, B = bayer_channel_separation(img, pattern)
#    #得到每个颜色通道的高宽
#    HH, HW = R.shape
#    # 生成分少块
#    Hblocks =  math.ceil(HH/height_block)
#    Wblocks =  math.ceil(HW/width_block)

#    #分配存放结果的内存
#    R_LSC_data = np.zeros((Hblocks,Wblocks))
#    B_LSC_data = np.zeros((Hblocks, Wblocks))
#    GR_LSC_data = np.zeros((Hblocks, Wblocks))
#    GB_LSC_data = np.zeros((Hblocks, Wblocks))

#    # 存放每个块距离光心的距离
#    RA = np.zeros((Hblocks, Wblocks))
#    center_x = HH/2
#    center_y = HW/2

#    for y in range(0 , HH, height_block):
#       for x in range(0 , HW, width_block):
#          yy = y + height_block/2
#          xx= x + width_block/2
#          block_y_num = int(y / height_block)
#          block_x_num = int(x / width_block)
#          #求每个颜色通道的每块的平均值
#          RA[block_y_num, block_x_num] = (yy-center_y)*(yy-center_y) + (xx-center_x)*(xx-center_x)
#          R_LSC_data[block_y_num, block_x_num] = R[y:y + height_block, x:x + width_block].mean()
#          GR_LSC_data[block_y_num, block_x_num] = GR[y:y + height_block, x:x + width_block].mean()
#          GB_LSC_data[block_y_num, block_x_num] = GB[y:y + height_block, x:x + width_block].mean()
#          B_LSC_data[block_y_num,block_x_num] = B[y:y+height_block,x:x+width_block].mean()
   

#    # 寻找光心块
#    center_point = np.where(GR_LSC_data == np.max(GR_LSC_data))
#    print("center_point:", center_point)
#    center_y = center_point[0]*height_block + height_block/2
#    center_x = center_point[1]*width_block + width_block/2

#    for y in range(0, HH, height_block):
#       for x in range(0, HW, width_block):
#          xx = x + width_block/2
#          yy = y + height_block/2
#          block_y_num = int(y / height_block)
#          block_x_num = int(x / width_block)
#          RA[block_y_num, block_x_num] = (yy-center_y)*(yy-center_y) + (xx - center_x) * (xx - center_x)
   
#    RA_flatten = RA.flatten()
#    R_LSC_data_flatten = R_LSC_data.flatten()
#    GR_LSC_data_flatten = GR_LSC_data.flatten()
#    GB_LSC_data_flatten = GB_LSC_data.flatten()
#    B_LSC_data_flatten = B_LSC_data.flatten()   

#    Max_R = np.max(R_LSC_data_flatten)
#    Max_GR = np.max(GR_LSC_data_flatten)
#    Max_GB = np.max(GB_LSC_data_flatten)
#    Max_B = np.max(B_LSC_data_flatten)

#    G_R_LSC_data = Max_R / R_LSC_data
#    G_GR_LSC_data = Max_GR / GR_LSC_data
#    G_GB_LSC_data = Max_GB / GB_LSC_data
#    G_B_LSC_data = Max_B / B_LSC_data

#    R_R = R_LSC_data_flatten / np.max(R_LSC_data_flatten)
#    R_GR = GR_LSC_data_flatten / np.max(GR_LSC_data_flatten)
#    R_GB = GB_LSC_data_flatten / np.max(GB_LSC_data_flatten)
#    R_B = B_LSC_data_flatten / np.max(B_LSC_data_flatten)

#    plt.scatter(RA_flatten, R_B, color='blue')
#    plt.scatter(RA_flatten, R_GR, color='green')
#    plt.scatter(RA_flatten, R_GB, color= 'green')
#    plt.scatter(RA_flatten, R_R, color='red')
#    plt.show()

#    G_R = 1/R_R
#    G_GR = 1/R_GR
#    G_GB = 1/R_GB
#    G_B = 1/R_B
   
#    plt.scatter(RA_flatten, G_B, color='blue')
#    plt.scatter(RA_flatten, G_GR, color='green')
#    plt.scatter(RA_flatten, G_GB, color= 'green')
#    plt.scatter(RA_flatten, G_R, color='red')
#    plt.show()

#    par_R = np.polyfit(RA_flatten, G_R, 3)
#    par_GR = np.polyfit(RA_flatten, G_GR, 3)
#    par_GB = np.polyfit(RA_flatten, G_GB, 3)
#    par_B = np.polyfit(RA_flatten, G_B, 3)

#    ES_R = par_R[0] * (RA_flatten**3) + par_R[1] * (RA_flatten**2) + par_R[2] * (RA_flatten) + par_R[3]
#    ES_GR = par_GR[0] * (RA_flatten**3) + par_GR[1] * (RA_flatten**2) + par_GR[2] * (RA_flatten) + par_GR[3]
#    ES_GB = par_GB[0] * (RA_flatten**3) + par_GB[1] * (RA_flatten**2) + par_GB[2] * (RA_flatten) + par_GB[3]
#    ES_B = par_B[0] * (RA_flatten**3) + par_B[1] * (RA_flatten**2) + par_B[2] * (RA_flatten) + par_B[3]
   
#    plt.scatter(RA_flatten, ES_B, color='blue')
#    plt.scatter(RA_flatten, ES_GR, color='green')
#    plt.scatter(RA_flatten, ES_GB, color='green')
#    plt.scatter(RA_flatten, ES_R, color='red')
#    plt.show()

#    EX_RA = np.zeros((Hblocks+2, Wblocks+2))
#    EX_R = np.zeros((Hblocks+2 , Wblocks+2))
#    EX_GR = np.zeros((Hblocks+2 , Wblocks+2))
#    EX_GB = np.zeros((Hblocks+2, Wblocks+2))
#    EX_B = np.zeros((Hblocks+2, Wblocks+2))
   
#    new_center_y = center_point[0] + 1
#    new_center_x = center_point[1] + 1

#    for y in range(0, Hblocks + 2):
#       for x in range(0, Wblocks + 2):
#          EX_RA[y,x] = (y-new_center_y)*height_block*(y-new_center_y)*height_block + (x-new_center_x)*width_block*(x-new_center_x)*width_block
#          EX_R[y,x] = par_R[0] * (EX_RA[y,x]**3) +par_R[1] * (EX_RA[y,x]**2)+par_R[2] * (EX_RA[y,x]) + par_R[3]
#          EX_GR[y,x] = par_GR[0] * (EX_RA[y,x]**3) + par_GR[1]*(EX_RA[y,x]**2) + par_GR[2] * (EX_RA[y,x]) + par_GR[3]
#          EX_GB[y,x] = par_GB[0] * (EX_RA[y,x]**3) + par_GB[1]*(EX_RA[y,x]**2) + par_GB[2] * (EX_RA[y,x]) + par_GB[3]
#          EX_B[y,x] = par_B[0] * (EX_RA[y,x]**3) + par_B[1]**(EX_RA[y,x]**2) + par_B[2]*(EX_RA[y,x]) + par_B[3]

#    EX_R[1:1+Hblocks, 1:1 + Wblocks] = G_R_LSC_data
#    EX_GR[1:1+Hblocks, 1:1 + Wblocks] = G_GR_LSC_data
#    EX_GB[1:1+Hblocks, 1:1 + Wblocks] = G_GB_LSC_data
#    EX_B[1:1+Hblocks, 1:1 + Wblocks] = G_B_LSC_data

#    return EX_R, EX_GR, EX_GB, EX_B

def lsc_correct(src_raw_array, width, height, pattern=["R","GR","GB","B"], eeprom_lsc_data_path=None, block_height=13, block_width=17):
   if eeprom_lsc_data_path:
      new_raw_img=apply_shading_to_image(src_raw_array.reshape(height, width),pattern,block_height,block_width,read_lsc_eeprom_data(eeprom_lsc_data_path,block_height,block_width))
      return new_raw_img
   # TO DO: 
   # else:
   #    EX_R, EX_GR, EX_GB, EX_B=creat_lsc_data(src_raw_array,13,17,"RGGB")
   #    new_raw_img=apply_shading_to_image(src_raw_array,13,17,EX_R, EX_GR, EX_GB, EX_B)
   #    return new_raw_img


