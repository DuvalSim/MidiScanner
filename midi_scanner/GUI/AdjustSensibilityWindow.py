import logging
from midi_scanner.GUI.FrameSliderWindowBase import FrameSliderWindowBase 
from midi_scanner.Keyboard import Keyboard
from midi_scanner.utils.ImageProcessor import ImageProcessor
import tkinter as tk
import cv2

from midi_scanner.utils.gui_utils import cv2_to_tkinter_image
from midi_scanner.utils.visualization import display_pressed_keys

class AdjustSensibilityWindow(FrameSliderWindowBase):

    def __init__(self, parent, video_capture, image_processor: ImageProcessor, first_frame=0, last_frame=None) -> None:
        
        super(AdjustSensibilityWindow, self).__init__(parent, video_capture, first_frame, last_frame)

        
        self.image_processor = image_processor
        keyboard_frame = self.image_processor.get_keyboard_image(self.current_frame_cv)
        

        cv2.imshow("test", keyboard_frame)

        self.keyboard = Keyboard(keyboard_frame)

        self.ratio_black = tk.DoubleVar()
        self.ratio_black.set(Keyboard.MIN_RATIO_BLACK_KEYS)
        self.ratio_white = tk.DoubleVar()
        self.ratio_white.set(Keyboard.MIN_RATIO_WHITE_KEYS)

        self.min_threshold_white = tk.IntVar()
        self.min_threshold_white.set(Keyboard.MIN_TRESHOLD_WHITE)
        self.min_threshold_black = tk.IntVar()
        self.min_threshold_black.set(Keyboard.MIN_TRESHOLD_BLACK)

        min_threshold_black_scale = tk.Scale(self, label="Min_Black_Threshold", from_=0, to=255 , orient=tk.HORIZONTAL, variable=self.min_threshold_black, width=15, command=self.change_params)
        min_threshold_black_scale.pack()
        min_threshold_black_scale = tk.Scale(self, label="Min_White_Threshold", from_=0, to=255 , orient=tk.HORIZONTAL, variable=self.min_threshold_white, width=15, command=self.change_params)
        min_threshold_black_scale.pack()
        min_threshold_black_scale = tk.Scale(self, label="Min_Black_Ratio", from_=0, to=1, resolution=0.1 , orient=tk.HORIZONTAL, variable=self.ratio_black, width=15, command=self.change_params)
        min_threshold_black_scale.pack()
        min_threshold_black_scale = tk.Scale(self, label="Min_White_Ratio", from_=0, to=1 , resolution=0.1, orient=tk.HORIZONTAL, variable=self.ratio_white, width=15, command=self.change_params)
        min_threshold_black_scale.pack()

    def change_params(self, param_value):
        # print(f"current_value: {self.min_threshold_black.get()}")

        self.keyboard.min_binary_thresh_black = self.min_threshold_black.get()
        self.keyboard.min_binary_thresh_white = self.min_threshold_white.get()
        self.keyboard.min_diff_ratio_black_keys = self.ratio_black.get()
        self.keyboard.min_diff_ratio_white_keys = self.ratio_white.get()
        self._show_pressed_key()

    def change_current_frame(self, frame_idx):

        super().change_current_frame(frame_idx=frame_idx)

        self._show_pressed_key()

    def _show_pressed_key(self):

        cropped_frame = self.image_processor.get_keyboard_image(self.current_frame_cv)
        
        pressed_keys = self.keyboard.get_pressed_keys(cropped_frame)       
        
        display_pressed_keys(cropped_frame, pressed_keys, level=logging.DEBUG)