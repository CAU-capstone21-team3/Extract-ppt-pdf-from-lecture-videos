import cv2
import os
import numpy as np

def detect_difference(before_frame, after_frame):
    error = np.sum((before_frame.astype("int")-after_frame.astype("int"))**2)
    error /= int(before_frame.shape[0] * after_frame.shape[1])
    error = abs(error)

    if error>10:
        #100하면 끊겨보임!!(실험해봄)
        #50도 조금 끊겨보임
        #5이하는 용량이커진다( 딱히 눈으로는 티도 안나는데)
        return True
    else:
        return False


#input , output 비디오 경로.
input_path = "video/lecture.mp4"
output_path = "video/output.mp4"

#비디오를 받아옴.
capture = cv2.VideoCapture(input_path)

#output에 저장할 frame 들을 저장하는 곳(buffer)
frame_array = []

#prev frame 저장하는 곳. 지금 당장은 첫 프레임 저장.
ret, prev_frame = capture.read()
height, width, layers = prev_frame.shape
size = (width, height)

while 1:
    ret, frame = capture.read()
    if frame is not None:
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
                    count+=1
                    #다르면 다른 거 유지 . (오리지날)
                    pass
                else:
                    #같으면 전 프레임의 것을 붙여 넣는다.
                    frame[start_height:end_height, start_width:end_width] = temp_image1

        frame_array.append(frame)
        prev_frame = frame
    else:
        #영상의 끝!
        break

#안되는코덱 (넣어봤음) : fmp4, divx, xvid, wmv2, yv12,x264
#avc1밖에 안되는 것인가?
out = cv2.VideoWriter("video/h264-lecture-without-audio.mp4", cv2.VideoWriter_fourcc(*'avc1'), 30, size)

for i in range(len(frame_array)):
    out.write(frame_array[i])
out.release()

#수정본 ffmpeg 변환
os.system("ffmpeg -i " + input_path + " -vn -acodec copy audio/audio.aac")
os.system("ffmpeg -i video/h264-lecture-without-audio.mp4 -i audio/audio.aac " + output_path)
#원본 ffmpeg 변환
os.system("ffmpeg -i video/lecture.mp4 video/original_output.mp4")
