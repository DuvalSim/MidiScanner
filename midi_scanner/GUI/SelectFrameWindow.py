import cv2
from midi_scanner.utils import preprocessing as preproc
import tkinter as tk
from PIL import ImageTk

from midi_scanner.utils.gui_utils import cv2_to_pil

import logging

# TODO: Change color of image

class SelectFrameWindow(tk.Frame):    

    def __init__(self, parent, video_capture, window_name, first_frame = 0, last_frame = None) -> None:

        self.logger = logging.getLogger(window_name)

        self.window_name = window_name

        tk.Frame.__init__(self, parent)
        
        self.video_capture = video_capture
        
        _, current_frame = self.video_capture.read()

        video_nb_frames = int(self.video_capture.get(cv2.CAP_PROP_FRAME_COUNT))

        if last_frame is not None and last_frame > (video_nb_frames -1):
            self.logger.info(f"Using video number of frame ([{video_nb_frames -1}])")
        
        last_frame = (video_nb_frames-1) if last_frame is None else min(last_frame, video_nb_frames-1)
        
        label = tk.Label(self, text=window_name)
        
        self.frame_idx = tk.IntVar()
        scale = tk.Scale(self, from_=first_frame, to=last_frame , orient=tk.HORIZONTAL, variable=self.frame_idx, width=15, command=self.change_current_frame)
        
        
        label.pack(side="top", fill="x")
        button = tk.Button(self, text="Confirm", command=self.destroy)
        scale.pack(side="top", fill="x")
        button.pack(side="top", fill="x")
        
        img_pil = cv2_to_pil(current_frame)
        img_tk = ImageTk.PhotoImage(image=img_pil)
        self.img_label = tk.Label(self, image= img_tk)
        self.img_label.image = img_tk
        self.img_label.pack(side="top")
        
    def get_user_frame(self) -> int:
        self.wait_window()
        frame_idx = int(self.frame_idx.get())

        return frame_idx
    
        
    def change_current_frame(self, frame_idx):

        self.video_capture.set(cv2.CAP_PROP_POS_FRAMES,int(frame_idx))
        
        _, current_frame = self.video_capture.read()
        img_pil = cv2_to_pil(current_frame)
        
        img_tk = ImageTk.PhotoImage(image=img_pil)
        self.img_label.configure(image=img_tk)
        self.img_label.image = img_tk
