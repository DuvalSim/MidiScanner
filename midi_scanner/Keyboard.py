import numpy as np
import cv2

from midi_scanner.utils.key_detection import get_black_keys, get_white_keys
from midi_scanner.utils.preprocessing import get_lower_image
from midi_scanner.utils.ColorMidiScanner import MidiScannerColor, ColorFormat
from midi_scanner.Key import Key, PressedKey

from midi_scanner.utils import visualization

from typing import List

import logging

class Keyboard:

    MIN_TRESHOLD_BOT = 20
    MIN_TRESHOLD_TOP = 40

    #BLACK_KEYS_MIN_AVG = 50
    
    def __init__(self, img_clear_keyboard, white_start_key="A0", black_start_key="a0"):
        self.white_keys = []
        self.black_keys = []
        self.img_clear_keyboard = img_clear_keyboard
        self._logger = logging.getLogger(__name__)

        self._populate_keys(img_clear_keyboard, white_start_key, black_start_key)

    def _populate_keys(self, img_clear_keyboard, white_start_key="A0", black_start_key="a0"):
        self.white_keys = get_white_keys(clean_frame=img_clear_keyboard, start_key=white_start_key)
        self.black_keys = get_black_keys(clean_frame=img_clear_keyboard, start_key=black_start_key)
    
    def get_pressed_keys(self, current_frame) -> List[PressedKey]:

        gray_clear = cv2.cvtColor(self.img_clear_keyboard, cv2.COLOR_BGR2GRAY)
        gray_current = cv2.cvtColor(current_frame, cv2.COLOR_BGR2GRAY)


        clean_bot, _ = get_lower_image(self.img_clear_keyboard)
        _, gray_clean_top = get_lower_image(gray_clear)
        current_bot, current_top = get_lower_image(current_frame)
        _, gray_current_top = get_lower_image(gray_current)
        


        diff_top = cv2.absdiff(gray_current_top, gray_clean_top)

        diff_bot = cv2.absdiff(clean_bot, current_bot)
        diff_bot = cv2.cvtColor(diff_bot, cv2.COLOR_BGR2GRAY)


        t_value_bot, thresh_bot = cv2.threshold(diff_bot, 100, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)#[1]	
        if t_value_bot < Keyboard.MIN_TRESHOLD_BOT:
            thresh_bot = cv2.threshold(diff_bot, Keyboard.MIN_TRESHOLD_BOT, 255, cv2.THRESH_BINARY)[1]
        #print("thresh value bot - ", t_value)
        
        
        t_value_top, thresh_top = cv2.threshold(diff_top, 100, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)#[1]
        if t_value_top < Keyboard.MIN_TRESHOLD_BOT:
            thresh_top = cv2.threshold(diff_top, Keyboard.MIN_TRESHOLD_TOP, 255, cv2.THRESH_BINARY)[1]
        #print("thresh value top - ", t_value_top)

        

        pressed_keys = []

        #cv2.imshow("difference", diff)
        #cv2.imshow("diff top", diff_top)
        #cv2.imshow("diff bot", diff_bot)
        #if t_value_bot >= Keyboard.MIN_TRESHOLD_BOT:
    
        for key in self.white_keys:

            #print(f"Note {key.note} : {key.start_x} - {key.end_x} - {np.mean(thresh_bot[:,key.start_x:key.end_x] / 255)}")
            if np.mean(thresh_bot[:,key.start_x:key.end_x] / 255) > 0.4:

                average_color = self.__get_average_key_color(key, current_image=current_bot)

                visualization.display_color(average_color, "PressedKey color", level=logging.DEBUG)

                pressed_key = PressedKey(key, average_color)
                pressed_keys.append(pressed_key)

        for key in self.black_keys:

            #print(f"Note {key.note} : {key.start_x} - {key.end_x} - {np.mean(thresh_top[:,key.start_x:key.end_x] / 255)}")

            if np.mean(thresh_top[:,key.start_x:key.end_x] / 255) > 0.4:

                average_color = self.__get_average_key_color(key, current_image=current_top)

                visualization.display_color(average_color, "PressedKey color", level=logging.DEBUG)

                pressed_key = PressedKey(key, average_color)
                
                pressed_keys.append(pressed_key)

        return pressed_keys
    
    @staticmethod
    def __get_average_key_color(key: Key, current_image) -> MidiScannerColor:
        
        average_color_np = np.mean(current_image[:,key.start_x:key.end_x],axis=(0,1))
        
        return MidiScannerColor(average_color_np, color_format=ColorFormat.BGR)
