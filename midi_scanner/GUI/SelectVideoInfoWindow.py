import cv2
import tkinter as tk
from PIL import Image, ImageTk
import logging

from midi_scanner.utils.gui_utils import cv2_to_tkinter_image
from midi_scanner.GUI.FrameSliderWindowBase import FrameSliderWindowBase

class VideoInfoWindow(FrameSliderWindowBase):

    def __init__(self, parent, video_capture) -> None:

        super(VideoInfoWindow, self).__init__(parent, video_capture=video_capture)
        
        self.img_label.bind("<Button-1>", self.on_img_click)

        self.color_canvas = tk.Canvas(self, width=50, height=50)
        self.color_canvas.pack()


    def on_img_click(self, event):
        """Handle mouse click event."""
        x = event.x
        y = event.y
        pixel_value = self.current_frame_cv[y, x]
        print("Pixel value at ({}, {}): {}".format(x, y, pixel_value))
        color = '#%02x%02x%02x' % (pixel_value[2], pixel_value[1], pixel_value[0])
        self.color_canvas.config(bg=color)
        self.color_canvas.update()

