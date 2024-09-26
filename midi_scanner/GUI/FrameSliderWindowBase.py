import cv2
from midi_scanner.utils import preprocessing as preproc
import tkinter as tk
from PIL import ImageTk

from midi_scanner.utils.gui_utils import cv2_to_tkinter_image

import logging

class FrameSliderWindowBase(tk.Frame):    

    def __init__(self, parent, video_capture, first_frame = 0, last_frame = None) -> None:

        tk.Frame.__init__(self, parent)
        
        self.logger = logging.getLogger(__class__.__name__)
       
        self.video_capture = video_capture

        self.video_capture.set(cv2.CAP_PROP_POS_FRAMES,int(first_frame))
        
        _, self.current_frame_cv = self.video_capture.read()

        video_nb_frames = int(self.video_capture.get(cv2.CAP_PROP_FRAME_COUNT))

        if last_frame is not None and last_frame > (video_nb_frames -1):
            self.logger.info(f"Using video number of frame ([{video_nb_frames -1}])")
        
        last_frame = (video_nb_frames-1) if last_frame is None else min(last_frame, video_nb_frames-1)
        
        
        self.frame_idx = tk.IntVar()
        scale = tk.Scale(self, from_=first_frame, to=last_frame , orient=tk.HORIZONTAL, variable=self.frame_idx, width=15, command=self.change_current_frame)
        
        
        
        
        self.current_img_tk = cv2_to_tkinter_image(self.current_frame_cv)
        self.img_label = tk.Label(self, image= self.current_img_tk)
        self.img_label.image = self.current_img_tk
        self.img_label.pack(side="top")

        scale.pack(side="top", fill="x")
    
        
    def change_current_frame(self, frame_idx):

        self.video_capture.set(cv2.CAP_PROP_POS_FRAMES,int(frame_idx))
        
        _, self.current_frame_cv = self.video_capture.read()
        self.current_img_tk = cv2_to_tkinter_image(self.current_frame_cv)
        
        self.img_label.configure(image=self.current_img_tk)
        self.img_label.image = self.current_img_tk
