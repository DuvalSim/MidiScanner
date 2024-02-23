import cv2
from midi_scanner.utils import preprocessing as preproc
import tkinter as tk
from PIL import Image, ImageTk

SELECT_FIRST_FRAME_WINDOW_NAME = 'Select first frame'


class SelectCleanFrameWindow(tk.Frame):    

    def __init__(self, parent, video_filepath) -> None:

        tk.Frame.__init__(self, parent)
        
        self.video_capture = cv2.VideoCapture(video_filepath)
        
        _, current_frame = self.video_capture.read()

        video_nb_frames = int(self.video_capture.get(cv2.CAP_PROP_FRAME_COUNT))

        self.frame_idx = tk.StringVar()
        scale = tk.Scale(self, from_=0, to=video_nb_frames -1 , orient=tk.HORIZONTAL, variable=self.frame_idx, width=15, command=self.change_current_frame)

        button = tk.Button(self, text="Confirm", command=self.destroy)
        scale.pack(side="top", fill="x")
        button.pack(side="top", fill="x")

        img_pil = Image.fromarray(current_frame)
        img_tk = ImageTk.PhotoImage(image=img_pil)
        self.img_label = tk.Label(self, image= img_tk)
        self.img_label.image = img_tk
        self.img_label.pack(side="top")


    def get_user_frame(self):
        self.wait_window()
        frame_idx = self.frame_idx.get()
        self.video_capture.release()
        return frame_idx
    
        
    def change_current_frame(self, frame_idx):

        self.video_capture.set(cv2.CAP_PROP_POS_FRAMES,int(frame_idx))
        
        _, current_frame = self.video_capture.read()
        img_pil = Image.fromarray(current_frame)
        img_tk = ImageTk.PhotoImage(image=img_pil)
        self.img_label.configure(image=img_tk)
        self.img_label.image = img_tk
        

