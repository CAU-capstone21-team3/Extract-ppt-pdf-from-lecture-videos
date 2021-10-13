import cv2
import numpy as np
from dataclasses import dataclass
from save_pdf import save_pdf
import time

start = time.time()

# 사진 몇 조각으로 나눌래 ?
# ex ) slice = 4 -> 4(가로)*4(세로) = 16조각
slice =4

def detect_difference(before_frame, after_frame):
    error = np.sum((before_frame.astype("int")-after_frame.astype("int"))**2)
    error /= int(before_frame.shape[0] * after_frame.shape[1])
    error = abs(error)
    if error > 4000:
        return True
    else:
        return False


#input , output 비디오 경로.
input_path = "video/lecture2.mp4"

#비디오를 받아옴.
capture = cv2.VideoCapture(input_path)

#output에 저장할 frame 들을 저장하는 곳(buffer)
frame_array = []

#prev frame 저장하는 곳. 지금 당장은 첫 프레임 저장.
ret, prev_frame = capture.read()
height, width, layers = prev_frame.shape
size = (width, height)

#temp 비교를 위한 저장공간들
#temp_origin_frame : 장면전환 후 첫 슬라이드(필기가 없는 . 흰화면)
temp_origin_frame=prev_frame
#temp_write_frame : 장면전환 후 필기부분이 확 변했을때 슬라이드 중 최신것.
temp_write_frame = prev_frame
#원본과 최신 필기본의 다른 부분 비교 .  이 부분(다른부분 = 필기부분)이 지워진다면 , 저장이 필요하다.
temp_diff_list = [[1 for col in range(slice)]for row in range(slice)]

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
        #진행률 표시
        print(str(capture.get(cv2.CAP_PROP_POS_FRAMES) / capture.get(cv2.CAP_PROP_FRAME_COUNT) * 100) + "%")
        count = 0

        # 문제점2 : 가끔 교수가 피피티 앞뒤로 왔다 갔다 거리는데 그건 어떻게 거를까 ? ->아직 해결못함.

        #전 프레임과 현프레임의 다른 부분을 저장.
        diff_list = [[0 for col in range(4)]for row in range(4)]

        # 한 조각의 width, height 계산
        slice_width = width // slice
        slice_height = height // slice

        #16조각 순회하면서 다른 부분이 어디인지 찾는다.
        different_slice = 0
        for i in range(slice):
            for j in range(slice):
                # 시작점 , 끝점 기록
                start_width = (width // slice) * i
                start_height = (height // slice) * j
                end_width = start_width + slice_width
                end_height = start_height + slice_height

                # 이미지 자르기 sample1[y:y+h , x:x+h] (height:height+h, width:width+h)
                temp_image1 = temp_origin_frame[start_height:end_height, start_width:end_width].copy()
                temp_image2 = frame[start_height:end_height, start_width:end_width].copy()

                if detect_difference(temp_image1, temp_image2):
                    diff_list[i][j] = 1
                    different_slice +=1

        #아예 다른 슬라이드 발견(슬라이드전환)
        if different_slice >=6:
            frame_array.append(prev_frame)
            temp_origin_frame= frame
            prev_frame = frame
            continue
        #인접한 곳에서 필기가 되었는가 ? 떨어진 곳에 필기를 했는지 detect.
        #문제점3 : 떨어진 곳에서 필기를 했으나 같은 필기의 내용인 경우.
        #예 : 밑줄 치는 구간이 좀 떨어져 있는 구간 (표 맨위를 줄 칠 하고, 맨 아래를 줄 칠하면 2칸 이상 벌어져서
        #이것도 차이가 있다고 느낀다.

        # 수정 3-1원본, 필기본 비교해서, 나중에 그 부분이 erase되면, 그때는 최신 필기본 저장한다.
        removed = 0

        for i in range(slice):
            if removed == 1 :
                break
            for j in range(slice):
                if temp_diff_list[i][j] == 1 and diff_list[i][j] == 0:
                    print(temp_diff_list)
                    print("아~")
                    print(diff_list)
                    print("===========")
                    removed = 1
                    break
        if removed == 0 :
           prev_frame = frame
           continue
        else:
            frame_array.append(temp_write_frame)
            temp_write_frame = frame
            prev_frame = frame

        temp_diff_list = [[0 for col in range(slice)]for row in range(slice)]

        for i in range(slice):
            for j in range(slice):
                start_width = (width // slice) * i
                start_height = (height // slice) * j
                end_width = start_width + slice_width
                end_height = start_height + slice_height

                # 이미지 자르기 sample1[y:y+h , x:x+h] (height:height+h, width:width+h)
                temp_image1 = temp_origin_frame[start_height:end_height, start_width:end_width].copy()
                temp_image2 = temp_write_frame[start_height:end_height, start_width:end_width].copy()

                # 원본 슬라이드 (흰색) 과 같은 부분
                # 최신 필기본에서 원본과 다른 부분이 , 현 프레임과 원본과 같으면 안된다. (지워진거니까)
                if detect_difference(temp_image1, temp_image2)==True:
                    temp_diff_list[i][j] = 1
    else:
        #맨 끝 프레임.
        frame_array.append(prev_frame)
        break
"""
for i in range(len(frame_array)):
    name = "video/result"+str(i)+".png"
    cv2.imwrite(name, frame_array[i])"""
del frame_array[0]
save_pdf(frame_array)
print(len(frame_array))

end = time.time()
print("time!!")
print(end-start)