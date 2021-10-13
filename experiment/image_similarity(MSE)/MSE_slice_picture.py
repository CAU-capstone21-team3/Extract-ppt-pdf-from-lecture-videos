import numpy as np
import cv2

def mse(image1, image2):
    error = np.sum((image1.astype("int")-image2.astype("int"))**2)
    error /= int(image1.shape[0] * image1.shape[1])
    return abs(error)


#이미지 읽고, 기본정보(너비,높이) 구함.
src = cv2.imread("apple.jpg", cv2.IMREAD_COLOR)

sample1 = cv2.imread("./sample1_1280x720.PNG", cv2.IMREAD_UNCHANGED)
sample2 = cv2.imread("./sample5_1280x720.PNG", cv2.IMREAD_UNCHANGED)

height1, width1, color1 = sample1.shape
height2, width2, color2 = sample2.shape

#사진 몇 조각으로 나눌래 ?
#ex ) slice = 4 -> 4(가로)*4(세로) = 16조각
slice =4

#한 조각의 width, height 계산
slice_width = width1 // slice
slice_height = height1 // slice
count = 0
for i in range(slice):
    for j in range(slice):

        #시작점 , 끝점 기록
        start_width = (width1//slice)*i
        start_height = (height1//slice)*j
        end_width = start_width + slice_width
        end_height = start_height + slice_height
        #이미지 자르기 sample1[y:y+h , x:x+h] (height:height+h, width:width+h)
        temp_image1 = sample1[start_height:end_height,start_width:end_width].copy()
        temp_image2 = sample2[start_height:end_height,start_width:end_width].copy()
        error = mse(temp_image1, temp_image2)
        if error > 100:
            count+=1
print(count)
"""
        if error>100:
            cv2.imshow("error", temp_image1)
            cv2.imshow("error2", temp_image2)
            cv2.waitKey(0)
 """








