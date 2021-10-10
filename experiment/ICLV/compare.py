from skimage.metrics import structural_similarity
import numpy as np
import cv2
import time


def mse(image1, image2):
    error = np.sum((image1.astype("int")-image2.astype("int"))**2)
    error /= int(image1.shape[0] * image1.shape[1])
    return abs(error)


def detect_difference(before, after, div):
    height, width, layers = before.shape

    block_width = width // div
    block_height = height // div

    result_array = []
    temp_after = after.copy()
    is_different = False
    for row in range(div):
        temp_array = []
        for col in range(div):
            temp_image1 = before[block_height * row:block_height * (row + 1), block_width * col:block_width * (col + 1)].copy()
            temp_image2 = after[block_height * row:block_height * (row + 1), block_width * col:block_width * (col + 1)].copy()
            if mse(temp_image1, temp_image2) > 10:
                temp_array.append(0)
                temp_after[block_height * row:block_height * (row + 1), block_width * col:block_width * (col + 1)] = visualize_difference_using_ssim(temp_image1, temp_image2)
                is_different = True
            else:
                temp_array.append(1)
        result_array.append(temp_array)

    if is_different:
        return result_array, temp_after
    else:
        return None, after


def visualize_difference_using_ssim(before, after):
    before_gray = cv2.cvtColor(before, cv2.COLOR_BGR2GRAY)
    after_gray = cv2.cvtColor(after, cv2.COLOR_BGR2GRAY)

    (score, diff) = structural_similarity(before_gray, after_gray, full=True)

    diff = (diff * 255).astype("uint8")

    thresh = cv2.threshold(diff, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
    contours = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = contours[0] if len(contours) == 2 else contours[1]

    filled_after = after.copy()

    for c in contours:
        area = cv2.contourArea(c)
        if area > 40:
            cv2.drawContours(filled_after, [c], 0, (255, 255, 0), -1)

    return filled_after


def SSIM(before, after):
    before_gray = cv2.cvtColor(before, cv2.COLOR_BGR2GRAY)
    after_gray = cv2.cvtColor(after, cv2.COLOR_BGR2GRAY)

    (score, diff) = structural_similarity(before_gray, after_gray, full=True)

    diff = (diff * 255).astype("uint8")

    thresh = cv2.threshold(diff, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
    contours = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = contours[0] if len(contours) == 2 else contours[1]

    filled_after = after.copy()
    is_different = False
    for c in contours:
        area = cv2.contourArea(c)
        if area > 40:
            cv2.drawContours(filled_after, [c], 0, (255, 255, 0), -1)
            is_different = True

    return is_different, filled_after


# ICLV test
start_time = time.time()

frame_array = []

capture = cv2.VideoCapture("./video/test.mp4")

ret, prev_frame = capture.read()
height, width, layers = prev_frame.shape
size = (width, height)

while 1:
    # print(str(capture.get(cv2.CAP_PROP_POS_FRAMES) / capture.get(cv2.CAP_PROP_FRAME_COUNT) * 100) + "%")
    ret, frame = capture.read()
    if frame is not None:
        result, temp_frame = detect_difference(prev_frame, frame, 16)
        if result is None:
            frame_array.append(prev_frame)
        else:
            frame_array.append(temp_frame)
            prev_frame = frame
    else:
        break

out = cv2.VideoWriter("./video/output1.mp4", cv2.VideoWriter_fourcc(*'avc1'), 30, size)
for i in range(len(frame_array)):
    out.write(frame_array[i])
out.release()

end_time = time.time()
print("1. Execution time = " + str(end_time - start_time))

# SSIM test
start_time = time.time()

frame_array = []

capture = cv2.VideoCapture("./video/test.mp4")

ret, prev_frame = capture.read()
height, width, layers = prev_frame.shape
size = (width, height)

while 1:
    # print(str(capture.get(cv2.CAP_PROP_POS_FRAMES) / capture.get(cv2.CAP_PROP_FRAME_COUNT) * 100) + "%")
    ret, frame = capture.read()
    if frame is not None:
        result, temp_frame = SSIM(prev_frame, frame)
        if result:
            frame_array.append(temp_frame)
            prev_frame = frame
        else:
            frame_array.append(prev_frame)
    else:
        break

out = cv2.VideoWriter("./video/output2.mp4", cv2.VideoWriter_fourcc(*'avc1'), 30, size)
for i in range(len(frame_array)):
    out.write(frame_array[i])
out.release()

end_time = time.time()
print("2. Execution time = " + str(end_time - start_time))
