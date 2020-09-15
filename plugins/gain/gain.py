import numpy as np
# import cv2

#alpha 0~300  Contrast
#beta 0~100   brightness
degain_data=0
category='RAW'
def updateApha(x,src_data):
    global degain_data
    alpha = cv2.getTrackbarPos('Alpha', 'image')
    alpha = alpha * 0.01
    beta = cv2.getTrackbarPos('Beta', 'image')
    degain_data = np.uint8(np.clip((alpha * src_data + beta), 0, 255))
    return degain_data

def updateBeta(x,src_data):
    global degain_data
    beta = cv2.getTrackbarPos('Beta','image')
    alpha = cv2.getTrackbarPos('Alpha', 'image')
    alpha = alpha * 0.01
    degain_data = np.uint8(np.clip((alpha * src_data + beta), 0, 255))
    return degain_data



def gain(src_data):
    # 创建窗口
    cv2.namedWindow('image')
    cv2.createTrackbar('Alpha', 'image', 0, 300, lambda x:updateApha(x,src_data))
    cv2.createTrackbar('Beta', 'image', 0, 255, lambda x:updateBeta(x,src_data))
    cv2.setTrackbarPos('Alpha', 'image', 100)
    cv2.setTrackbarPos('Beta', 'image', 10)

    while (True):
        cv2.imshow('image', degain_data)
        if cv2.waitKey(1) == ord('q'):
            break
    cv2.destroyAllWindows()
