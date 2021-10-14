from skimage.metrics import structural_similarity
import numpy as np
import cv2
import time


def mse(image1, image2):
    error = np.sum((image1.astype("int") - image2.astype("int")) ** 2)
    error /= int(image1.shape[0] * image1.shape[1])
    return abs(error)


def get_dif(color1, color2):
    if color1 is None and color2 is not None:
        return color2
    elif color1 is not None and color2 is None:
        return color1
    elif color1 is None and color2 is None:
        return None
    elif len(color1) == 3 and len(color2) == 3:
        dif = 0
        for i in range(len(color1)):
            if color1[i] > color2[i]:
                dif += color1[i] - color2[i]
            else:
                dif += color2[i] - color1[i]
        return dif
    else:
        return None


def detect_difference(before, after, div):
    height, width, layers = before.shape

    block_width = width // div
    block_height = height // div

    temp_after = after.copy()
    count = 0
    block_array = []

    for row in range(div):
        for col in range(div):
            temp_image1 = before[block_height * row:block_height * (row + 1), block_width * col:block_width * (col + 1)].copy()
            temp_image2 = after[block_height * row:block_height * (row + 1), block_width * col:block_width * (col + 1)].copy()
            if mse(temp_image1, temp_image2) > 10:
                block_array.append([row, col])
                temp_after[block_height * row:block_height * (row + 1), block_width * col:block_width * (col + 1)] = visualize_difference(temp_image1, temp_image2)
                count += 1

    if count > 2:
        return 2, block_array, None
    elif count > 0:
        return 1, block_array, temp_after
    else:
        return 0, None, None


def visualize_difference(before, after):
    height, width, layers = before.shape

    temp_after = after.copy()

    for row in range(height):
        for col in range(width):
            if get_dif(before[row, col], after[row, col]) > 50:
                temp_after[row, col] = [255, 255, 0]

    return temp_after


def ssim(before, after):
    before_gray = cv2.cvtColor(before, cv2.COLOR_BGR2GRAY)
    after_gray = cv2.cvtColor(after, cv2.COLOR_BGR2GRAY)

    (score, diff) = structural_similarity(before_gray, after_gray, full=True)

    diff = (diff * 255).astype("uint8")

    thresh = cv2.threshold(diff, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
    contours = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = contours[0] if len(contours) == 2 else contours[1]

    filled_after = after.copy()
    count = 0
    for c in contours:
        area = cv2.contourArea(c)
        if area > 40:
            cv2.drawContours(filled_after, [c], 0, (255, 255, 0), -1)
            count += 1

    if count > 0:
        return 1, None, filled_after
    else:
        return 0, None, None


def test(input_path, output_path):
    start_time = time.time()

    capture = cv2.VideoCapture(input_path)
    frame_array = []
    ret, prev_frame = capture.read()
    height, width, layers = prev_frame.shape
    size = (width, height)

    while 1:
        print(str(capture.get(cv2.CAP_PROP_POS_FRAMES) / capture.get(cv2.CAP_PROP_FRAME_COUNT) * 100) + "%")
        ret, frame = capture.read()
        if frame is not None:
            result, block_array, temp_frame = detect_difference(prev_frame, frame, 16)
            if result == 0:
                frame_array.append(prev_frame)
            elif result == 1:
                frame_array.append(temp_frame)
                prev_frame = frame
            elif result == 2:
                frame_array.append(frame)
                prev_frame = frame
            else:
                print("Error")
        else:
            break

    out = cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc(*'avc1'), 30, size)
    for i in range(len(frame_array)):
        out.write(frame_array[i])
    out.release()

    end_time = time.time()
    print("Execution time (IIC) = " + str(end_time - start_time))


def test_using_ssim(input_path, output_path):
    start_time = time.time()

    capture = cv2.VideoCapture(input_path)
    frame_array = []
    ret, prev_frame = capture.read()
    height, width, layers = prev_frame.shape
    size = (width, height)

    while 1:
        print(str(capture.get(cv2.CAP_PROP_POS_FRAMES) / capture.get(cv2.CAP_PROP_FRAME_COUNT) * 100) + "%")
        ret, frame = capture.read()
        if frame is not None:
            result, block_array, temp_frame = ssim(prev_frame, frame)
            if result == 0:
                frame_array.append(prev_frame)
            elif result == 1:
                frame_array.append(temp_frame)
                prev_frame = frame
            elif result == 2:
                frame_array.append(frame)
                prev_frame = frame
            else:
                print("Error")
        else:
            break

    out = cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc(*'avc1'), 30, size)
    for i in range(len(frame_array)):
        out.write(frame_array[i])
    out.release()

    end_time = time.time()
    print("Execution time (ssim) = " + str(end_time - start_time))


test("./video/test1.mp4", "./video/test1-output1.mp4")
test_using_ssim("./video/test1.mp4", "./video/test1-output2.mp4")