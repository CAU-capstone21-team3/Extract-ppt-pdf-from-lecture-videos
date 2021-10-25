import cv2
from PIL import Image

def save_pdf(frame_array, output):
    image_array = []
    first_image = cv2.cvtColor(frame_array[0], cv2.COLOR_BGR2RGB)
    first_image = Image.fromarray(first_image)
    del frame_array[0]

    for frame in frame_array:
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(image)
        image_array.append(image)

    first_image.save(output, save_all=True, append_images = image_array)






