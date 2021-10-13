import cv2
import numpy as np
from PIL import Image

def save_pdf(frame_array):
    image_array = []
    first_image = cv2.cvtColor(frame_array[0], cv2.COLOR_BGR2RGB)
    first_image = Image.fromarray(first_image)
    del frame_array[0]

    for frame in frame_array:
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(image)
        image_array.append(image)

    first_image.save("video/result_pdf.pdf", save_all=True, append_images = image_array)






