import numpy as np
import cv2

def mse(image1, image2):
    error = np.sum((image1.astype("int")-image2.astype("int"))**2)
    error /= int(image1.shape[0] * image1.shape[1])
    return abs(error)

sample1 = cv2.imread("./sample1_1280x720.PNG", cv2.IMREAD_UNCHANGED)
sample2 = cv2.imread("./sample6_1280x720.PNG", cv2.IMREAD_UNCHANGED)
error = mse(sample1,sample2)
print(error)