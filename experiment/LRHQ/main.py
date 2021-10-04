from skimage.metrics import structural_similarity
import cv2
import os
import numpy as np


def detect_difference(before, after):
    before_gray = cv2.cvtColor(before, cv2.COLOR_BGR2GRAY)
    after_gray = cv2.cvtColor(after, cv2.COLOR_BGR2GRAY)

    (score, diff) = structural_similarity(before_gray, after_gray, full=True)

    diff = (diff * 255).astype("uint8")

    thresh = cv2.threshold(diff, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
    contours = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = contours[0] if len(contours) == 2 else contours[1]

    mask = np.zeros(before.shape, dtype='uint8')
    filled_after = after.copy()

    for c in contours:
        area = cv2.contourArea(c)
        if area > 40:
            return True
    return False


input_path = "video/lecture.mp4"
output_path = "video/output.mp4"

frame_array = []

capture = cv2.VideoCapture(input_path)

ret, prev_frame = capture.read()
height, width, layers = prev_frame.shape
size = (width, height)

while 1:
    ret, frame = capture.read()
    if frame is not None:
        if detect_difference(prev_frame, frame):
            frame_array.append(frame)
            prev_frame = frame
        else:
            frame_array.append(prev_frame)
    else:
        break

out = cv2.VideoWriter("video/h264-lecture-without-audio.mp4", cv2.VideoWriter_fourcc(*'avc1'), 30, size)
for i in range(len(frame_array)):
    out.write(frame_array[i])
out.release()

os.system("ffmpeg -i " + input_path + " -vn -acodec copy audio/audio.aac")
os.system("ffmpeg -i video/h264-lecture-without-audio.mp4 -i audio/audio.aac " + output_path)
