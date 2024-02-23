import tkinter as tk   # from tkinter import Tk for Python 3.x
from tkinter.filedialog import askopenfilename
from ctypes import windll
from midi_scanner.GUI.CroppingWindow import CroppingWindow
from midi_scanner.GUI.SelectCleanFrameWindow import SelectCleanFrameWindow

import cv2

windll.shcore.SetProcessDpiAwareness(1)

class ApplicationController:
    def __init__(self, root):
        self.root = root
        self.current_window = None
        self.window_stack = []  # Stack to keep track of opened windows

    def show_window(self, window_class):
        if self.current_window:
            self.current_window.destroy()
        self.current_window = window_class(self.root, self)

    def start(self):
        self.root.withdraw()
        # https://stackoverflow.com/questions/41083597/trackbar-hsv-opencv-tkinter-python
        
        music_video_filepath = askopenfilename(filetypes = (("videos", "*.mp4"), ("all files", "*.*"))) # show an "Open" dialog box and return the path to the selected file

        self.root.deiconify()

        new_frame = SelectCleanFrameWindow(self.root, music_video_filepath)
        new_frame.pack()
        value = new_frame.get_user_frame()

        print(value)
        
        WINDOW_NAME_SELECT_FIRST_FRAME = 'Select first frame'

        
        

        first_frame_idx = 0

        print(music_video_filepath)

        self.root.destroy()


    
def main():
    root = tk.Tk()
    root.title("My Tkinter Application")

    app_controller = ApplicationController(root)

    # Show the initial window
    app_controller.start()

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