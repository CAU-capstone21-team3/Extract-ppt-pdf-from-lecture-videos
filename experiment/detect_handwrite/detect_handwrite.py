import cv2
import numpy as np
from save_pdf import save_pdf
import time


def detect_difference(before_frame, after_frame):
    error = np.sum((before_frame.astype("int") - after_frame.astype("int"))**2)
    error /= int(before_frame.shape[0] * before_frame.shape[1])
    return abs(error)


def detect_different_part(before_frame, after_frame):
    height, width, layers = before_frame.shape

    slice = 4
    different_slice = 0

    slice_width = width // slice
    slice_height = height // slice

    for i in range(slice):
        for j in range(slice):
            temp_image1 = before_frame[slice_height * j:slice_height * (j + 1), slice_width * i:slice_width * (i + 1)].copy()
            temp_image2 = after_frame[slice_height * j:slice_height * (j + 1), slice_width * i:slice_width * (i + 1)].copy()

            if detect_difference(temp_image1, temp_image2) > 4000:
                different_slice += 1

    return different_slice


def save_pdf_from_video(input_path, output_path):
    start = time.time()

    capture = cv2.VideoCapture(input_path)

    ret, prev_frame = capture.read()
    height, width, layers = prev_frame.shape

    origin_frame_array = [prev_frame]
    frame_array = []
    current_frame_index = 0
    slide_num = 0

    count = 0
    while 1:
        ret, frame = capture.read()

        if frame is not None:
            count += 1
            if count % 30 != 0:
                continue
            print(str(capture.get(cv2.CAP_PROP_POS_FRAMES) / capture.get(cv2.CAP_PROP_FRAME_COUNT) * 100) + "%")
            count = 0

            if detect_different_part(origin_frame_array[current_frame_index], frame) >= 6:
                exist = [False, False]
                index = [0, 0]
                for i in range(len(origin_frame_array)):
                    if detect_difference(origin_frame_array[i], frame) < 50:
                        exist[0] = True
                        index[0] = i
                for i in range(len(frame_array)):
                    if detect_difference(frame_array[i][0], frame) < 50:
                        exist[1] = True
                        index[1] = frame_array[i][1]

                prev_exist = False
                for i in range(len(frame_array)):
                    if detect_difference(frame_array[i][0], prev_frame) < 50:
                        prev_exist = True

                if not prev_exist:
                    frame_array.append([prev_frame, current_frame_index])
                
                if not exist[0] and not exist[1]:
                    origin_frame_array.append(frame)
                    slide_num += 1
                    current_frame_index = slide_num
                elif exist[0] and not exist[1]:
                    current_frame_index = index[0]
                elif not exist[0] and exist[1]:
                    current_frame_index = index[1]

                prev_frame = frame
                continue

            prev_frame = frame

        else:
            frame_array.append([prev_frame, current_frame_index])
            break

    temp_array = []
    for i in frame_array:
        temp_array.append(i[0])
    save_pdf(temp_array, output_path)

    save_pdf(origin_frame_array, "video/origin.pdf")

    print("time: ", end=" ")
    print(time.time() - start)


# Test

save_pdf_from_video("video/1.mp4", "video/result.pdf")
