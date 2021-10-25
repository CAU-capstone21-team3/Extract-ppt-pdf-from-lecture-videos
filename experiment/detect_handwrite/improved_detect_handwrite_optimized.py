import cv2
import numpy as np
from save_pdf import save_pdf
import time
import copy


def detect_difference(before_frame, after_frame):
    error = np.sum((before_frame.astype("int") - after_frame.astype("int"))**2)
    error /= int(before_frame.shape[0] * before_frame.shape[1])
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


def slice_and_visualize_difference(before, after, div):
    height, width, layers = before.shape

    block_width = width // div
    block_height = height // div

    temp_after = before.copy()

    for row in range(div):
        for col in range(div):
            temp_image1 = before[block_height * row:block_height * (row + 1),
                          block_width * col:block_width * (col + 1)].copy()
            temp_image2 = after[block_height * row:block_height * (row + 1),
                          block_width * col:block_width * (col + 1)].copy()
            temp_after[block_height * row:block_height * (row + 1),
                block_width * col:block_width * (col + 1)] = visualize_difference(temp_image1, temp_image2)

    return temp_after


def visualize_difference(before, after):
    height, width, layers = before.shape

    temp_after = after.copy()

    for row in range(height):
        for col in range(width):
            if get_dif(before[row, col], after[row, col]) > 50:
                temp_after[row, col] = before[row, col].copy()
            else:
                temp_after[row, col] = [255, 255, 255]

    return temp_after


def save_pdf_from_video(input, slice):
    start = time.time()

    # 비디오를 받아옴.
    capture = cv2.VideoCapture(input)

    # output에 저장할 frame 들을 저장하는 곳(buffer)
    frame_array = []

    # prev frame 저장하는 곳. 지금 당장은 첫 프레임 저장.
    ret, prev_frame = capture.read()
    height, width, layers = prev_frame.shape

    # origin slide 저장하는 곳.
    origin_slide_array = []
    origin_slide_array.append(prev_frame)

    # final slide 저장하는 곳.
    final_slide_array = []
    final_slide_array.append(prev_frame)

    # temp 비교를 위한 저장공간들
    # temp_origin_frame : 장면전환 후 첫 슬라이드(필기가 없는 . 흰화면)
    temp_origin_frame = prev_frame
    # temp_write_frame : 장면전환 후 필기부분이 확 변했을때 슬라이드 중 최신것.
    temp_write_frame = prev_frame
    # 원본과 최신 필기본의 다른 부분 비교 .  이 부분(다른부분 = 필기부분)이 지워진다면 , 저장이 필요하다.
    temp_diff_list = [[1 for col in range(slice)] for row in range(slice)]

    for i in range(slice):
        for j in range(slice):
            temp_diff_list[i][j] = 1

    count = 0

    while 1:
        ret, frame = capture.read()
        if frame is not None:
            # 문제점1 : 16등분 을 다 ~~하니까 너무 느리다.
            # 해결책1: 1초 안에 있는 필기는 비슷할 것이다 . 5프레임 정도에서 1개정도만 보자(시간절약)
            count += 1

            if count % 30 != 0:
                continue
            # 진행률 표시
            print(str(capture.get(cv2.CAP_PROP_POS_FRAMES) / capture.get(cv2.CAP_PROP_FRAME_COUNT) * 100) + "%")
            count = 0

            # 문제점2 : 가끔 교수가 피피티 앞뒤로 왔다 갔다 거리는데 그건 어떻게 거를까 ? ->아직 해결못함.

            # 전 프레임과 현프레임의 다른 부분을 저장.
            diff_list = [[0 for col in range(slice)] for row in range(slice)]

            # 한 조각의 width, height 계산
            slice_width = width // slice
            slice_height = height // slice

            # 16조각 순회하면서 다른 부분이 어디인지 찾는다.
            different_slice = 0
            for i in range(slice):
                for j in range(slice):
                    # 시작점 , 끝점 기록
                    start_width = slice_width * i
                    start_height = slice_height * j
                    end_width = slice_width * (i + 1)
                    end_height = slice_height * (j + 1)

                    # 이미지 자르기 sample1[y:y+h , x:x+h] (height:height+h, width:width+h)
                    temp_image1 = temp_origin_frame[start_height:end_height, start_width:end_width].copy()
                    temp_image2 = frame[start_height:end_height, start_width:end_width].copy()

                    if detect_difference(temp_image1, temp_image2) > 4000:
                        diff_list[i][j] = 1
                        different_slice += 1

            # 아예 다른 슬라이드 발견(슬라이드전환)
            if different_slice >= 6:
                exist = False
                for image in origin_slide_array:
                    if detect_difference(image, frame) < 50:
                        exist = True
                frame_array.append(prev_frame)
                final_slide_array.append(prev_frame)
                temp_origin_frame = frame
                prev_frame = frame
                if not exist:
                    origin_slide_array.append(frame)
                continue
            # 인접한 곳에서 필기가 되었는가 ? 떨어진 곳에 필기를 했는지 detect.
            # 문제점3 : 떨어진 곳에서 필기를 했으나 같은 필기의 내용인 경우.
            # 예 : 밑줄 치는 구간이 좀 떨어져 있는 구간 (표 맨위를 줄 칠 하고, 맨 아래를 줄 칠하면 2칸 이상 벌어져서
            # 이것도 차이가 있다고 느낀다.

            # 수정 3-1원본, 필기본 비교해서, 나중에 그 부분이 erase되면, 그때는 최신 필기본 저장한다.
            erased = False
            for i in range(slice):
                if erased:
                    break
                for j in range(slice):
                    if temp_diff_list[i][j] == 1 and diff_list[i][j] == 0:
                        print(temp_diff_list)
                        erased = True
                        break
            prev_frame = frame
            if erased:
                frame_array.append(temp_write_frame)
                temp_write_frame = frame
                temp_diff_list = copy.deepcopy(diff_list)
        else:
            # 맨 끝 프레임.
            frame_array.append(prev_frame)
            break

    del frame_array[0]
    save_pdf(frame_array, "video/result_pdf.pdf")
    print(len(frame_array))

    if len(origin_slide_array) == len(final_slide_array):
        temp_array = []
        for i in range(len(origin_slide_array) - 1):
            temp_array.append(slice_and_visualize_difference(origin_slide_array[i], final_slide_array[i + 1], 16))
        save_pdf(temp_array, "video/detect_write_result.pdf")

    print("time: ", end=" ")
    print(time.time() - start)


# Test part

save_pdf_from_video("video/lecture.mp4", 4)
