import argparse

from midi_scanner.utils.StateSaver import StateSaver

from midi_scanner.NoteRecorder import NoteRecorder
from midi_scanner.utils.ImageLogger import setup_image_logger
import logging

import tkinter as tk   # from tkinter import Tk for Python 3.x
from tkinter.filedialog import askopenfilename
from ctypes import windll
from midi_scanner.GUI.CroppingWindow import CroppingWindow
from midi_scanner.GUI.SelectFrameWindow import SelectFrameWindow

import cv2

from midi_scanner.utils.ImageProcessor import ImageProcessor

windll.shcore.SetProcessDpiAwareness(1)

SELECT_FIRST_FRAME_LABEL= 'Select first frame (with clean keyboard)'
SELECT_LAST_FRAME_LABEL = 'Select last frame to handle'

class ApplicationController:
    def __init__(self, root):
        self.root = root
        self.current_window = None
        self.window_stack = []  # Stack to keep track of opened windows

        self.music_video_filepath = ""

    def show_window(self, window_class):
        if self.current_window:
            self.current_window.destroy()
        self.current_window = window_class(self.root, self)


    def record_notes(self,  ):

        image_processor = ImageProcessor(keyboard_region_y=(keyboard_roi[1],keyboard_roi[3]), keyboard_region_x=(keyboard_roi[0],keyboard_roi[2]))
        first_frame = image_processor.get_keyboard_image(first_frame)

        cv2.imshow("first frame", first_frame)

        keyboard = Keyboard(first_frame, "C3", "c3")

    def __open_video(self, video_path):
        # Attempt to open the video file
        self.video_capture = cv2.VideoCapture(video_path)
        
        # Check if the video file was opened successfully
        if not self.video_capture.isOpened():
            logging.CRITICAL(f"Error: Could not open video file [{video_path}].")
            raise IOError("Could not read file")
        
        
        # Retrieve some properties of the video
        self.video_fps = self.video_capture.get(cv2.CAP_PROP_FPS)
        self.video_frame_count = int(self.video_capture.get(cv2.CAP_PROP_FRAME_COUNT))
        self.video_width = int(self.video_capture.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.video_height = int(self.video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        logging.debug(f"Video file opened successfully. FPS: {self.video_fps},\
                      Frame count: {self.video_frame_count}, Resolution: {self.video_width}x{self.video_height}")
        
        


    def run(self):
        

        self.root.withdraw()
        # https://stackoverflow.com/questions/41083597/trackbar-hsv-opencv-tkinter-python
        
        music_video_filepath = askopenfilename(filetypes = (("videos", "*.mp4"), ("all files", "*.*"))) # show an "Open" dialog box and return the path to the selected file

        self.__open_video(music_video_filepath)
        self.root.deiconify()

        tk_first_frame = SelectFrameWindow(self.root, self.video_capture, window_name=SELECT_FIRST_FRAME_LABEL)
        tk_first_frame.pack()
        clean_frame_idx = tk_first_frame.get_user_frame()

        tk_last_frame = SelectFrameWindow(self.root, self.video_capture, window_name=SELECT_LAST_FRAME_LABEL, first_frame=clean_frame_idx)
        tk_last_frame.pack()
        last_frame_idx = tk_last_frame.get_user_frame()


        self.root.withdraw()
        self.keyboard_roi = CroppingWindow(video_capture=self.video_capture, frame_idx=clean_frame_idx).get_cropped_dimension()

        NoteRecorder().record_notes(video_capture=self.video_capture, starting_frame=clean_frame_idx, ending_frame=last_frame_idx, keyboard_roi=self.keyboard_roi,first_white_key="C3", first_black_key="c3")
        
        print(self.keyboard_roi)




        self.video_capture.release()
        self.root.destroy()


    
def main():

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-d', '--debug',
        help="Print lots of debugging statements",
        action="store_const", dest="loglevel", const=logging.DEBUG,
        default=logging.WARNING,
    )
    parser.add_argument(
        '-v', '--verbose',
        help="Be verbose",
        action="store_const", dest="loglevel", const=logging.INFO,
    )

    # parser.add_argument(
    #     '--state-file',
    #     help="path to yml state file",
    #     dest="state_file"
    # )

    args = parser.parse_args()
    setup_image_logger(args.loglevel)
    
    root = tk.Tk()
    root.title("My Tkinter Application")

    test_logger = logging.getLogger("test2")
    test_mine = logging.getLogger("suuu")


    test_mine.debug("this is from mine")
    test_logger.debug("this is from other")

    app_controller = ApplicationController(root)


    # Show the initial window
    app_controller.run()

    root.mainloop()

if __name__ == "__main__":
    main()



# WINDOW_NAME_SELECT_FIRST_FRAME = 'Select first frame'
# WINDOW_NAME_CROP_KEYBOARD = 'Crop keyboard'

# first_frame_idx = 0

# def change_current_frame(frame_idx):
#     global video_capture
#     global current_img
#     global first_frame_idx
#     video_capture.set(cv2.CAP_PROP_POS_FRAMES,frame_idx)
#     first_frame_idx = frame_idx
#     _, current_img = video_capture.read()


# video_capture = cv2.VideoCapture(music_video_filepath)
# video_capture.set(cv2.CAP_PROP_POS_FRAMES,120)
# ret, current_img = video_capture.read()

# video_nb_frames = int(video_capture.get(cv2.CAP_PROP_FRAME_COUNT))

# cv2.namedWindow(WINDOW_NAME_SELECT_FIRST_FRAME)
# cv2.createTrackbar('frame', WINDOW_NAME_SELECT_FIRST_FRAME, 0, min(500, video_nb_frames-1), change_current_frame)

# while True:
#     cv2.imshow(WINDOW_NAME_SELECT_FIRST_FRAME,current_img )

#     key = cv2.waitKey(1) & 0xFF
#     if key == ord('c'):
#         break

# cv2.destroyAllWindows()

# print("Got first frame:", first_frame_idx)

# video_capture.set(cv2.CAP_PROP_POS_FRAMES,first_frame_idx)
# ret, first_frame = video_capture.read()

# img_copy = first_frame.copy()
# drawing = False
# top_left_pt, bottom_right_pt = (-1, -1), (-1, -1)

# def crop_image(image, top_left_point, bottom_right_point):

#     print("Cropped image:")
#     print("y:", top_left_point[1], bottom_right_point[1])
#     print("x", top_left_point[0], bottom_right_point[0])
#     cropped_image = image[top_left_point[1]:bottom_right_point[1], top_left_point[0]:bottom_right_point[0]]
#     return cropped_image

# def mouse_callback(event, x, y, flags, param):
#     global drawing, top_left_pt, bottom_right_pt, img_copy, first_frame

#     if event == cv2.EVENT_LBUTTONDOWN:
#         drawing = True
#         top_left_pt = (x, y)

#     elif event == cv2.EVENT_LBUTTONUP:
#         drawing = False
#         bottom_right_pt = (x, y)
#         img_copy = first_frame.copy()  # Reset img_copy to the original frame
#         cv2.rectangle(img_copy, top_left_pt, bottom_right_pt, (0, 255, 0), 2)
#         cv2.imshow(WINDOW_NAME_CROP_KEYBOARD, img_copy)

#         test = crop_image(first_frame, top_left_pt, bottom_right_pt)
#         cv2.imshow("Preview", test)
    
#     elif event == cv2.EVENT_MOUSEMOVE and drawing:
#         img_copy = first_frame.copy()  # Reset img_copy to the original frame
#         cv2.rectangle(img_copy, top_left_pt, (x, y), (0, 255, 0), 2)
#         cv2.imshow(WINDOW_NAME_CROP_KEYBOARD, img_copy)

# cv2.namedWindow(WINDOW_NAME_CROP_KEYBOARD)
# cv2.setMouseCallback(WINDOW_NAME_CROP_KEYBOARD, mouse_callback)


# while True:
#     cv2.imshow(WINDOW_NAME_CROP_KEYBOARD, img_copy)

#     key = cv2.waitKey(1) & 0xFF

#     if key == ord('c'):
#         cropped_image = crop_image(first_frame, top_left_pt, bottom_right_pt)
#         cv2.imshow("Cropped Image", cropped_image)
#         break

#     elif key == 27:
#         break

# cv2.destroyAllWindows()
# video_capture.release()