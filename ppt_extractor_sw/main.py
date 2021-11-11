import time
from tkinter import *
import cv2
import numpy as np
import pyautogui
import win32gui
import win32ui
import win32con
import win32api
from win32api import GetSystemMetrics
from save_pdf import save_pdf

# global variable
start_mouse_state = win32api.GetKeyState(0x01)  # Left button down = 0 or 1. Button up = -127 or -128
clicked = False
first_area_pos = None
second_area_pos = None
frame = None
prev_frame = None
origin_frame_array = []
frame_array = []
current_frame_index = None
slide_num = None
in_progress = False

def get_screenshot():
    # Calculate position of rectangle
    x = min(first_area_pos[0], second_area_pos[0])
    y = min(first_area_pos[1], second_area_pos[1])
    width = abs(first_area_pos[0] - second_area_pos[0])
    height = abs(first_area_pos[1] - second_area_pos[1])

    # grab a handle to the main desktop window
    hdesktop = win32gui.GetDesktopWindow()

    # create a device context
    desktop_dc = win32gui.GetWindowDC(hdesktop)
    img_dc = win32ui.CreateDCFromHandle(desktop_dc)

    # create a memory based device context
    mem_dc = img_dc.CreateCompatibleDC()

    # create a bitmap object
    bitmap = win32ui.CreateBitmap()
    bitmap.CreateCompatibleBitmap(img_dc, width, height)
    mem_dc.SelectObject(bitmap)

    # copy the screen into our memory device context
    mem_dc.BitBlt((0, 0), (width, height), img_dc, (x, y), win32con.SRCCOPY)

    # Convert bitmap to opencv-image
    signedIntsArray = bitmap.GetBitmapBits(True)
    img = np.frombuffer(signedIntsArray, dtype='uint8')
    img.shape = (height, width, 4)

    # free our objects
    mem_dc.DeleteDC()
    win32gui.DeleteObject(bitmap.GetHandle())

    return cv2.cvtColor(img, cv2.COLOR_RGBA2RGB)

def get_mouse_up():
    global second_area_pos, clicked
    mouse_state = win32api.GetKeyState(0x01)

    if mouse_state != start_mouse_state and mouse_state >= 0 and clicked:
        clicked = False
        second_area_pos = pyautogui.position()
        label.config(text="(" + str(first_area_pos[0]) + ", " + str(first_area_pos[1]) + ") ~ (" + str(second_area_pos[0]) + ", " + str(second_area_pos[1]) + ")")
    else:
        root.after(5, get_mouse_up)

    dc = win32gui.GetDC(0)
    hwnd = win32gui.WindowFromPoint((0, 0))
    monitor = (0, 0, GetSystemMetrics(0), GetSystemMetrics(1))

    m = win32gui.GetCursorPos()
    win32gui.InvalidateRect(hwnd, monitor, True)  # Refresh the entire monitor
    for i in range((m[0] - first_area_pos[0]) // 4):
        win32gui.SetPixel(dc, first_area_pos[0] + 4 * i, first_area_pos[1], 0)
        win32gui.SetPixel(dc, first_area_pos[0] + 4 * i, m[1], 0)
    for i in range((m[1] - first_area_pos[1]) // 4):
        win32gui.SetPixel(dc, first_area_pos[0], first_area_pos[1] + 4 * i, 0)
        win32gui.SetPixel(dc, m[0], first_area_pos[1] + 4 * i, 0)

def get_mouse_down():
    global first_area_pos, clicked
    mouse_state = win32api.GetKeyState(0x01)

    if mouse_state != start_mouse_state and mouse_state < 0 and not clicked:
        clicked = True
        first_area_pos = pyautogui.position()
        root.after(5, get_mouse_up)
    else:
        root.after(5, get_mouse_down)

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

def start():
    global prev_frame, origin_frame_array, frame_array, current_frame_index, slide_num, in_progress
    prev_frame = get_screenshot()
    origin_frame_array = [prev_frame]
    frame_array = []
    current_frame_index = 0
    slide_num = 0
    in_progress = True
    label.config(text="녹화중...")
    root.after(1000, update)

def update():
    global frame, prev_frame, origin_frame_array, frame_array, current_frame_index, slide_num
    start_time = time.time()
    frame = get_screenshot()
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

        if not exist[0] and not exist[1]:
            origin_frame_array.append(frame)
            slide_num += 1
            current_frame_index = slide_num
        elif exist[0] and not exist[1]:
            current_frame_index = index[0]
        elif not exist[0] and exist[1]:
            current_frame_index = index[1]

        prev_exist = False
        for i in range(len(frame_array)):
            if detect_difference(frame_array[i][0], prev_frame) < 50:
                prev_exist = True

        if not prev_exist:
            frame_array.append([prev_frame, current_frame_index])

    prev_frame = frame
    if in_progress:
        if int((time.time() - start_time) * 1000) < 1000:
            root.after(1000 - int((time.time() - start_time) * 1000), update)
        else:
            update()

def stop():
    global in_progress
    in_progress = False
    temp_array = []
    for i in frame_array:
        temp_array.append(i[0])
    save_pdf(temp_array, "result.pdf")
    label.config(text="PDF 변환 완료")

# GUI
root = Tk()
root.title("PDF")
root.geometry("200x250+1400+300")
root.resizable(False, False)

label = Label(root, text="영역을 설정해주세요")
label.pack()
set_area_button = Button(root, text="Set Area", command=get_mouse_down, width=10, height=2, padx=3, pady=3)
start_button = Button(root, text="Start", command=start, width=10, height=2, padx=3, pady=3)
stop_button = Button(root, text="Stop", command=stop, width=10, height=2, padx=3, pady=3)

set_area_button.pack(pady=10)
start_button.pack()
stop_button.pack(pady=10)

root.mainloop()