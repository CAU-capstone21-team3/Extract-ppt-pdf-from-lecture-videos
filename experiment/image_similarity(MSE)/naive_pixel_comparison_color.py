#pixel한개 한개 비교하는 방식. 느리다.

import numpy as np
import cv2

sample1 = cv2.imread("./sample1_1280x720.PNG", cv2.IMREAD_UNCHANGED)
sample2 = cv2.imread("./sample5_1280x720.PNG", cv2.IMREAD_UNCHANGED)

count = 0
#shape[0] : 세로(height), shape[1] : 가로(width)
for y in range(sample1.shape[1]):
    for x in range(sample1.shape[0]):
        if abs(int(sample1[x][y][0])- int(sample2[x][y][0]))>50\
                or abs(int(sample1[x][y][1])-int(sample2[x][y][1]))>50\
                or abs(int(sample1[x][y][2])-int(sample2[x][y][2]))>50\
                or abs(int(sample1[x][y][3])-int(sample2[x][y][3]))>50:
            sample1[x][y]= [0,255,0,255]
            count+=1

print(count)
cv2.imshow("resample", sample1)
cv2.waitKey(0)
