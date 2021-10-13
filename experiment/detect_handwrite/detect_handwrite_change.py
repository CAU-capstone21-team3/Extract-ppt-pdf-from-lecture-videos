import cv2
import numpy as np
from save_pdf import save_pdf 
from dataclasses import dataclass

@dataclass
class Coord:
    x: int = None
    y: int = None

def detect_difference(before_frame, after_frame):
    error = np.sum((before_frame.astype("int")-after_frame.astype("int"))**2)
    error /= int(before_frame.shape[0] * after_frame.shape[1])
    error = abs(error)

    if error>100:
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

#전 프레임은 전전프레임과 어디가 달랐을까 ? 저장
prev_diff_list = []
while 1:
    ret, frame = capture.read()
    if frame is not None:
        diff_list = []
        # 사진 몇 조각으로 나눌래 ?
        # ex ) slice = 4 -> 4(가로)*4(세로) = 16조각
        slice = 4

        # 한 조각의 width, height 계산
        slice_width = width // slice
        slice_height = height // slice

        for i in range(slice):
            for j in range(slice):
                count=0
                # 시작점 , 끝점 기록
                start_width = (width // slice) * i
                start_height = (height // slice) * j
                end_width = start_width + slice_width
                end_height = start_height + slice_height

                # 이미지 자르기 sample1[y:y+h , x:x+h] (height:height+h, width:width+h)
                temp_image1 = prev_frame[start_height:end_height, start_width:end_width].copy()
                temp_image2 = frame[start_height:end_height, start_width:end_width].copy()

                if detect_difference(temp_image1, temp_image2):
                    temp_coord = Coord()
                    temp_coord.x = i
                    temp_coord.y = j
                    diff_list.append(temp_coord)

        #아예 다른 장면 검출! 전 프레임이 ppt 넘어가기 직전 프레임이므로, 저장한다.
        if len(diff_list) >=4 :
            frame_array.append(prev_frame)
            prev_frame = frame
            prev_diff_list = diff_list
            continue

        #인접한 곳에서 필기가 되었는가 ? 떨어진 곳에 필기를 했는지 detect.
        for i in range(len(diff_list)):
            pass_var = 0
            for j in range(len(prev_diff_list)):
                if abs(diff_list[i].x-prev_diff_list[j].x)<=1 and abs(diff_list[i].y-prev_diff_list[j].y)<=1:
                    pass_var=1
                    break

            if pass_var ==0:
                frame_array.append(prev_frame)
                break
        prev_diff_list = diff_list
        prev_frame = frame
    else:
        #맨 끝 프레임.
        frame_array.append(prev_frame)
        break

for i in range(len(frame_array)):
    name = "video/result"+str(i)+".png"
    cv2.imwrite(name, frame_array[i])

save_pdf(frame_array)

print(len(frame_array))