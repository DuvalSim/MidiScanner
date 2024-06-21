import cv2
from midi_scanner.utils import preprocessing as preproc
from midi_scanner.utils import ImageProcessor
from midi_scanner.utils.gui_utils import cv2_to_tkinter_image 

import tkinter as tk

import logging

CROP_KEYBOARD_WINDOW_NAME = 'Crop keyboard'
CROP_PREVIEW_WINDOW_NAME = 'Preview'
CROP_RESULT_WINDOW_NAME = "Cropped image"

class KeyboardRoiWindow(tk.Frame):    

    def __init__(self, parent, video_capture, image_processor: ImageProcessor, frame_idx: int) -> None:

        tk.Frame.__init__(self, parent)
        
        self.logger = logging.getLogger("CroppingWindow")
        
        video_capture.set(cv2.CAP_PROP_POS_FRAMES,frame_idx)
        _, clean_frame = video_capture.read()

        self.image_processor = image_processor

        self.keyboard_img = self.image_processor.get_keyboard_image(clean_frame)

        self.current_black_white_limit = self.initial_black_white_limit = self.image_processor.calculate_and_set_black_white_limit(self.keyboard_img)

        keyboard_img_tk = cv2_to_tkinter_image(self.keyboard_img)
        
        self.img_canvas = tk.Canvas(self, width=keyboard_img_tk.width(), height=keyboard_img_tk.height())
        self.img_canvas.grid(column=0, row=0, columnspan=2)

        # Add the image to the canvas
        self.img_canvas.create_image(0, 0, anchor=tk.NW, image=keyboard_img_tk)
        self.img_canvas.image = keyboard_img_tk
        # Draw the initial horizontal line
        self.black_white_line_id = self.img_canvas.create_line(0, keyboard_img_tk.height() // 2, keyboard_img_tk.width(), keyboard_img_tk.height() // 2, fill="red", width=2)
        self.img_canvas.tag_bind(self.black_white_line_id, "<Button-1>", lambda event: self.img_canvas.bind("<B1-Motion>", self._on_move_line))
        self.img_canvas.tag_bind(self.black_white_line_id, "<ButtonRelease-1>", lambda event: self.img_canvas.unbind("<B1-Motion>"))

        ## Preview at the bottom of the other canvas
        self.preview_label = tk.Label(self)
        self.preview_label.grid(column=0, row=2, columnspan=2, sticky="N")
        
        if self.initial_black_white_limit != -1:
            self._update_height(self.initial_black_white_limit)
            self.confirm_button = tk.Button(self, text="Use suggested value", command=self.destroy)
            self.confirm_button.grid(row=1, column=0, sticky="NSEW")

            reset_button = tk.Button(self, text="Discard changes", command=self._reset)
            reset_button.grid(row=1, column=1, sticky="NSEW")
        
        else:
            self.confirm_button = tk.Button(self, text="Use current value", command=self.destroy)
            self.confirm_button.grid(row=1, column=0, sticky="NSEW")
        

    def _on_move_line(self, event):
        # Do not move line if outside of bounds
        if event.y < 0 or event.y >= self.keyboard_img.shape[0]:
            return
        
        if event.y != self.initial_black_white_limit:
            self.confirm_button.configure(text="Use current value")
        else:
            self.confirm_button.configure(text="Use calculated value")

        self._update_height(event.y)

    def _update_height(self, height):
         # Update line
        self.img_canvas.moveto(self.black_white_line_id, 0, height)
        self.current_black_white_limit = height

        # Update preview
        preview_image = self._get_current_image_bottom()
        self.preview_label.configure(image=preview_image)
        self.preview_label.image = preview_image

        self.image_processor.set_black_white_limit(height)
         

    def _get_current_image_bottom(self):
        bottom_img = self.keyboard_img[self.current_black_white_limit:,:]
        preview_image_tk = cv2_to_tkinter_image(bottom_img)
        return preview_image_tk
    
    def _reset(self):
        self.confirm_button.configure(text="Use calculated value")
        self._update_height(self.initial_black_white_limit)
        
         
        
         