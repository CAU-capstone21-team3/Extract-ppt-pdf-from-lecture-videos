"""
한 개 frame 흑백으로 만들어서
color diagram 했는데, 판별하기 어려움(탈락)
"""
from matplotlib import pyplot as plt
import cv2

sample1 = cv2.imread("./sample6.jpg", cv2.IMREAD_UNCHANGED)
sample2 = cv2.imread("./sample5_1280x720.PNG", cv2.IMREAD_UNCHANGED)
sample1 = cv2.cvtColor(sample1, cv2.COLOR_BGR2GRAY)

hist = cv2.calcHist([sample1],[0],None,[256],[0,256])
plt.plot(hist)
plt.xlim([0,256])
plt.show()