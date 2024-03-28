import cv2
from PIL import Image, ImageTk

def cv2_to_pil(image):
# convert for tkinter
        cv2_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        return Image.fromarray(cv2_image)

def cv2_to_tkinter_image(cv2_image):
        """Convert a cv2 image to a tkinter image."""
        cv2_image = cv2.cvtColor(cv2_image, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(cv2_image)
        tkinter_image = ImageTk.PhotoImage(image=pil_image)
        return tkinter_image