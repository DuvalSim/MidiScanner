import cv2
from PIL import Image

def cv2_to_pil(image):
# convert for tkinter
        cv2_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        return Image.fromarray(cv2_image)