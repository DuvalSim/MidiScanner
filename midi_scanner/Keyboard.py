import numpy as np
import cv2

from midi_scanner.utils.key_detection import get_black_keys, get_white_keys
from midi_scanner.utils.preprocessing import get_lower_image

class Keyboard:

    MIN_TRESHOLD_BOT = 30
    
    def __init__(self, img_clear_keyboard):
        self.white_keys = []
        self.black_keys = []
        self.img_clear_keyboard = img_clear_keyboard

        self._populate_keys(img_clear_keyboard)

    def _populate_keys(self, img_clear_keyboard):
        self.white_keys = get_white_keys(clean_frame=img_clear_keyboard)
        self.black_keys = get_black_keys(clean_frame=img_clear_keyboard)
    
    def get_pressed_keys(self, current_frame):

        gray_clear = cv2.cvtColor(self.img_clear_keyboard, cv2.COLOR_BGR2GRAY)
        gray_current = cv2.cvtColor(current_frame, cv2.COLOR_BGR2GRAY)

        diff = cv2.absdiff(gray_clear, gray_current)

        diff_bot, diff_top = get_lower_image(diff)

        t_value, thresh_bot = cv2.threshold(diff_bot, 100, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)#[1]	
        if t_value < Keyboard.MIN_TRESHOLD_BOT:
            thresh_bot = cv2.threshold(diff_bot, Keyboard.MIN_TRESHOLD_BOT, 255, cv2.THRESH_BINARY)[1]
        #print("thresh value bot - ", t_value)
        
        _, thresh_top = cv2.threshold(diff_top, 100, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)#[1]
        #print("thresh value top - ", t_value)

        

        pressed_keys = []

        # cv2.imshow("difference", diff)
        # cv2.imshow("diff top", diff_top)
        # cv2.imshow("diff bot", diff_bot)
        
        for key in self.white_keys:

            # print(f"Note {key.note} : {key.start_x} - {key.end_x} - {np.mean(thresh_bot[:,key.start_x:key.end_x] / 255)}")
            if np.mean(thresh_bot[:,key.start_x:key.end_x] / 255) > 0.4:
                pressed_keys.append(key)

        for key in self.black_keys:

            # print(f"Note {key.note} : {key.start_x} - {key.end_x} - {np.mean(thresh_top[:,key.start_x:key.end_x] / 255)}")

            if np.mean(thresh_top[:,key.start_x:key.end_x] / 255) > 0.4:
                pressed_keys.append(key)

        return pressed_keys
