import cv2
import tkinter as tk
from PIL import Image, ImageTk

class ImageDisplay:
    def __init__(self, master, image_path):
        self.master = master
        self.cv2_image = cv2.imread(image_path)
        self.tkinter_image = self.cv2_to_tkinter_image(self.cv2_image)
        self.label = tk.Label(master)
        self.label.config(image=self.tkinter_image)
        self.label.image = self.tkinter_image
        self.label.pack()
        self.label.bind("<Button-1>", self.on_click)

    def cv2_to_tkinter_image(self, cv2_image):
        """Convert a cv2 image to a tkinter image."""
        cv2_image = cv2.cvtColor(cv2_image, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(cv2_image)
        tkinter_image = ImageTk.PhotoImage(image=pil_image)
        return tkinter_image

    def on_click(self, event):
        """Handle mouse click event."""
        x = event.x
        y = event.y
        pixel_value = self.cv2_image[y, x]
        print("Pixel value at ({}, {}): {}".format(x, y, pixel_value))

def display_image(image_path):
    """Display an image in a tkinter window."""
    root = tk.Tk()
    root.title("Image Display")
    image_display = ImageDisplay(root, image_path)
    root.mainloop()

# Path to your image file
image_path = "C:\\Users\\simon\\Documents\\Projets\\MidiScanner\\media\\test_frame.png"

# Display the image
display_image(image_path)
