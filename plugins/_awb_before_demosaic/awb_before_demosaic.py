import numpy as np
from skimage import filters
from scipy import signal

pattern ='RGGB'
bits    =10
#error code 
ResultSuccess        =0
ResultEParsingFiles  =1
ResultEInvalidArg    =2
ResultEOther         =5

def printE(error_code):
    print("E error code：%d" % error_code)

#颜色通道的分离
def bayer_channel_separation(data, pattern):
    #------------------------------------------------------
    #   Objective: Outputs four channels of the bayer pattern
    #   Input:
    #       data:   the bayer data
    #       pattern:    RGGB, GBRG, GBRG, or BGGR
    #   Output:
    #       R, GR, GB, B (Quarter resolution images)
    #------------------------------------------------------
    image_data=data
    if (pattern == "RGGB"):
        R = image_data[::2, ::2]
        GR = image_data[::2, 1::2]
        GB = image_data[1::2, ::2]
        B = image_data[1::2, 1::2]
    elif (pattern == "GRBG"):
        GR = image_data[::2, ::2]
        R = image_data[::2, 1::2]
        B = image_data[1::2, ::2]
        GB = image_data[1::2, 1::2]
    elif (pattern == "GBRG"):
        GB = image_data[::2, ::2]
        B = image_data[::2, 1::2]
        R = image_data[1::2, ::2]
        GR = image_data[1::2, 1::2]
    elif (pattern == "BGGR"):
        B = image_data[::2, ::2]
        GB = image_data[::2, 1::2]
        GR = image_data[1::2, ::2]
        R = image_data[1::2, 1::2]
    else:
        print("pattern must be one of :  RGGB, GBRG, GBRG, or BGGR")
        return

    return R, GR, GB, B

def gDer(f,sigma, iorder,jorder):
    break_off_sigma = 3.
    H,W=f.shape
    filtersize = np.floor(break_off_sigma*sigma+0.5)
    filtersize = filtersize.astype(np.int)
    #扩展边
    f=np.pad(f,((filtersize,filtersize),(filtersize,filtersize)),'edge')
    x=np.arange(-filtersize,filtersize+1)
    #翻转滤波核
    x=x*-1
    Gauss=1/(np.power(2 * np.pi,0.5) * sigma)* np.exp((x**2)/(-2 * sigma * sigma))
    if iorder==0:
        #高斯滤波
        Gx = Gauss / sum(Gauss)
    elif iorder==1:
        # 一阶求导
        Gx  =  -(x/sigma**2)*Gauss
        Gx  =  Gx/(np.sum(x*Gx))
    elif iorder == 2:
        #二阶求导
        Gx = (x**2/sigma**4-1/sigma**2)*Gauss
        Gx = Gx-sum(Gx)/(2*filtersize+1)
        Gx = Gx/sum(0.5*x*x*Gx)
    #扩展到二维
    Gx = Gx.reshape(1,-1)
        #Gx=np.transpose([Gx])
    #卷积
    h=signal.convolve(f, Gx, mode="same")

    if jorder==0:
        Gy = Gauss / sum(Gauss)
    elif jorder==1:
        Gy  =  -(x/sigma**2)*Gauss
        Gy  =  Gy/(np.sum(x*Gy))
    elif jorder == 2:
        Gy = (x**2/sigma**4-1/sigma**2)*Gauss
        Gy = Gy-sum(Gy)/(2*filtersize+1)
        Gy = Gy/sum(0.5*x*x*Gy)
    # 扩展到二维,转成二维
    Gy = Gy.reshape(1,-1).T
    res=signal.convolve(h, Gy, mode="same")
    res2=res[1:2,1:2]
    end_h=(filtersize+H)
    end_w=(filtersize+W)
    res2=np.array(res)[filtersize:end_h,filtersize:end_w]
    return res2

def NormDerivative(img, sigma, order):
    #一阶求导
    if (order == 1):
        Ix = gDer(img, sigma, 1, 0)
        Iy = gDer(img, sigma, 0, 1)
        Iw = np.power(Ix**2 + Iy**2,0.5)

    #二阶求导
    if (order == 2) :# computes frobius norm
        Ix = gDer(img, sigma, 2, 0)
        Iy = gDer(img, sigma, 0, 2)
        Ixy = gDer(img, sigma, 1, 1)
        Iw = np.power(Ix ** 2 + Iy ** 2+4* Ixy, 0.5)
    return Iw

def set_border(im,width,method):
    #sets border to either zero method=0,or method=1 to average
    hh,ll=im.shape
    im[0:width,:]=method
    im[hh-width:hh, :] = method
    im[:,0:width] = method
    im[:,ll-width:ll] = method
    return im

def dilation33(im):
    hh,ll=im.shape
    out1 = np.zeros((hh, ll))
    out2 = np.zeros((hh, ll))
    out3 = np.zeros((hh, ll))
    #H 方向扩展上下像素
    out1[0:hh-1,:]=im[1:hh,:]
    out1[hh-1, :] = im[hh-1, :]
    out2=im
    out3[0,:] = im[0, :]
    out3[1:hh, :] = im[0:hh-1, :]
    out_max=np.maximum(out1,out2)
    out_max=np.maximum(out_max,out3)
    #W方向扩展上下像素
    out1[:,0:ll-1]=out_max[:,1:ll]
    out1[:,ll-1] = out_max[:,ll-1]
    out2=out_max
    out3[:,0] = out_max[:,0]
    out3[:,1:ll] = out_max[:,0:ll-1]
    out_max=np.maximum(out1,out2)
    out_max=np.maximum(out_max,out3)
    return out_max
#将raw图各个颜色通道分离
def raw_awb_separation(image, pattern):
    image=image.astype(np.float)
    R, GR, GB, B = bayer_channel_separation(image, pattern)
    G=(GR+GB)/2
    return R, GR, GB, B, G


#njet 是否edge mink_norm shade的参数  sigma 滤波和求导参数
def grey_edge(R,G,B, njet=0, mink_norm=1, sigma=1,saturation_threshold: int = 1024):
    """
    Estimates the light source of an input_image as proposed in:
    J. van de Weijer, Th. Gevers, A. Gijsenij
    "Edge-Based Color Constancy"
    IEEE Trans. Image Processing, accepted 2007.
    Depending on the parameters the estimation is equal to Grey-World, Max-RGB, general Grey-World,
    Shades-of-Grey or Grey-Edge algorithm.
    """
    mask_im = np.zeros(R.shape)
    img_max=np.maximum(R,G)
    img_max=np.maximum(img_max,B)
    # 移除所有饱和像素
    itemindex = np.where(img_max >= saturation_threshold)
    saturation_map = np.zeros(R.shape)
    saturation_map[itemindex]=1
    #扩散
    mask_im = dilation33(saturation_map)
    mask_im = 1-mask_im
    #移除边的像素生成最终的有效像素mask
    mask_im2 = set_border(mask_im, sigma + 1, 0)
    #不去掉饱和像素尤其是buiding图片差别很大
    #mask_im2 = np.ones(R.shape)
    if njet == 0:
        if (sigma!=0):
            #去噪
            gauss_image_R = filters.gaussian(R, sigma=sigma, multichannel=True)
            gauss_image_G = filters.gaussian(G, sigma=sigma, multichannel=True)
            gauss_image_B = filters.gaussian(B, sigma=sigma, multichannel=True)
        else:
            gauss_image_R = R
            gauss_image_G = G
            gauss_image_B = B
        deriv_image_R = gauss_image_R[:, :]
        deriv_image_G = gauss_image_G[:, :]
        deriv_image_B = gauss_image_B[:, :]
    else:
       #
       deriv_image_R = NormDerivative(R, sigma, njet)
       deriv_image_G = NormDerivative(G, sigma, njet)
       deriv_image_B = NormDerivative(B, sigma, njet)

    # estimate illuminations
    if mink_norm == -1:  # mink_norm = inf
        estimating_func = lambda x: np.max(x*mask_im2.astype(np.int))
    else:
        estimating_func = lambda x: np.power(np.sum(np.power(x*mask_im2.astype(np.int), mink_norm)), 1 / mink_norm)
    RS = np.sum(np.power(deriv_image_R, mink_norm))
    GS = np.sum(np.power(deriv_image_G, mink_norm))
    BS = np.sum(np.power(deriv_image_B, mink_norm))
    illum_R = estimating_func(deriv_image_R)
    illum_G = estimating_func(deriv_image_G)
    illum_B = estimating_func(deriv_image_B)

    illum_max = np.maximum(illum_R, illum_G)
    illum_max = np.maximum(illum_max, illum_B)

    R_gain = illum_max / illum_R
    G_gain = illum_max / illum_G
    B_gain = illum_max / illum_B

    return  R_gain,G_gain,B_gain

#按照颜色根据不同的bayer合成
def bayer_channel_integration( R, GR, GB, B, pattern):
        #------------------------------------------------------
        #   Objective: combine data into a raw according to pattern
        #   Input:
        #       R, GR, GB, B:   the four separate channels (Quarter resolution)
        #       pattern:    RGGB, GBRG, GBRG, or BGGR
        #   Output:
        #       data (Full resolution image)
        #------------------------------------------------------
        size = np.shape(R)
        data = np.empty((size[0]*2, size[1]*2), dtype=np.float32)
        # casually use float32,maybe change later
        if (pattern == "RGGB"):
            data[::2, ::2] = R
            data[::2, 1::2] = GR
            data[1::2, ::2] = GB
            data[1::2, 1::2] = B
        elif (pattern == "GRBG"):
            data[::2, ::2] = GR
            data[::2, 1::2] = R
            data[1::2, ::2] = B
            data[1::2, 1::2] = GB
        elif (pattern == "GBRG"):
            data[::2, ::2] = GB
            data[::2, 1::2] = B
            data[1::2, ::2] = R
            data[1::2, 1::2] = GR
        elif (pattern == "BGGR"):
            data[::2, ::2] = B
            data[::2, 1::2] = GB
            data[1::2, ::2] = GR
            data[1::2, 1::2] = R
        else:
            print("pattern must be one of these: rggb, grbg, gbrg, bggr")
            return

        return data

def apply_raw(pattern,R, GR, GB, B,R_gain,G_gain,B_gain,max_value):
    R = np.minimum(R * R_gain, max_value)
    GR = np.minimum(GR * G_gain, max_value)
    GB = np.minimum(GB * G_gain, max_value)
    B = np.minimum(B * B_gain, max_value)
    result_image=bayer_channel_integration(R, GR, GB, B, pattern)
    return result_image



def setParameters(parameters):
    global pattern,bits
    try:
        pattern = parameters[0]
        bits    = int(parameters[1])
    except:
        printE(ResultEInvalidArg)
        return ResultEInvalidArg
    else:
        return ResultSuccess

def run(raw_array):  #raw图的白平衡计算
    global pattern,bits
    try:
        R, GR, GB, B, G = raw_awb_separation(raw_array, pattern)
    except:
        printE(ResultEInvalidArg)
        return ResultEInvalidArg
    else:
        max_value=2<<(bits-1)
        R_gain, G_gain, B_gain = grey_edge(R, G, B, njet=1, mink_norm=5, sigma=2,saturation_threshold=max_value)
        result_image = apply_raw(pattern,R, GR, GB, B,R_gain,G_gain,B_gain,max_value)
        return result_image
