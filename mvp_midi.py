import argparse

from midi_scanner.utils.StateSaver import StateSaver

from midi_scanner.NoteRecorder import NoteRecorder
from midi_scanner.utils.ImageLogger import setup_image_logger
import logging

import tkinter as tk   # from tkinter import Tk for Python 3.x
from tkinter.ttk import Progressbar 
from tkinter.filedialog import askopenfilename
from ctypes import windll
from midi_scanner.GUI.CroppingWindow import CroppingWindow
from midi_scanner.GUI.SelectFrameWindow import SelectFrameWindow
from midi_scanner.GUI.SelectVideoInfoWindow import VideoInfoWindow

from midi_scanner.GUI.MusicInfoWindow import MusicInfoWindow

import cv2

from midi_scanner.utils.ImageProcessor import ImageProcessor

from midi_scanner.NoteWriter import MidiWriter

from midi_scanner.utils.ColorMidiScanner import MidiScannerColor, ColorFormat
import midi_scanner.utils.postprocessing as postprocessing
from midi_scanner.utils import visualization

import music21
import subprocess

windll.shcore.SetProcessDpiAwareness(1)

SELECT_FIRST_FRAME_LABEL= 'Select first frame (with clean keyboard)'
SELECT_LAST_FRAME_LABEL = 'Select last frame to handle'

RECORD_IN_PROGRESS_WINDOW_NAME = 'Detecting notes played...'

class ApplicationController:
    def __init__(self, root):
        self.root = root
        self.current_window = None
        self.window_stack = []  # Stack to keep track of opened windows

        self.logger = logging.getLogger("ApplicationController")

        self.music_video_filepath = ""
        self.video_capture = None

    def show_window(self, window_class):
        if self.current_window:
            self.current_window.destroy()
        self.current_window = window_class(self.root, self)

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
        
    def run_record_note_progress(self) -> callable:
        #start progress bar

        record_note_progress_popup = tk.Toplevel()
        label = tk.Label(record_note_progress_popup, text=RECORD_IN_PROGRESS_WINDOW_NAME)

        progress_var = tk.DoubleVar()
        progress_bar = Progressbar(record_note_progress_popup, variable=progress_var, maximum=100)
        label.pack()
        progress_bar.pack()

        progress_var.set(0)

        def update_progress_var(value):
            progress_var.set(value)
            if value == 100:
                self.logger.info("End of note recording tracking")
                record_note_progress_popup.destroy()
            self.root.update()

        return update_progress_var


    def quit(self):
        if self.video_capture:
            self.video_capture.release()
        self.root.destroy()
        exit()

    def run(self):

        self.root.withdraw()
        # https://stackoverflow.com/questions/41083597/trackbar-hsv-opencv-tkinter-python
        
        music_video_filepath = askopenfilename(filetypes = (("videos", "*.mp4"), ("all files", "*.*"))) # show an "Open" dialog box and return the path to the selected file
        
        if not music_video_filepath:
            
            self.logger.critical("No file was selected")
            self.quit()
            
            
        self.__open_video(music_video_filepath)

        # self.root.deiconify()
        # self.root.withdraw()
        # t = VideoInfoWindow(self.root, self.video_capture)
        # t.pack()
        # test = t.pick_music_info()
        
        # logging.debug(f"Got colors: {test}")

        

        self.root.deiconify()

        tk_first_frame = SelectFrameWindow(self.root, self.video_capture, window_name=SELECT_FIRST_FRAME_LABEL)
        tk_first_frame.pack()
        clean_frame_idx = tk_first_frame.get_user_frame()
        clean_frame_idx = 164
        last_frame_idx = 2500
        logging.debug(f"Clean frame idx: [{clean_frame_idx}]")

        # tk_last_frame = SelectFrameWindow(self.root, self.video_capture, window_name=SELECT_LAST_FRAME_LABEL, first_frame=clean_frame_idx)
        # tk_last_frame.pack()
        # last_frame_idx = tk_last_frame.get_user_frame()
        # logging.debug(f"last frame idx: [{last_frame_idx}]")

        
        self.root.withdraw()
        self.keyboard_roi = CroppingWindow(video_capture=self.video_capture, frame_idx=clean_frame_idx).get_cropped_dimension()
        # self.keyboard_roi = (0,246,635,350)
        logging.debug(f"keyboard roi: [{self.keyboard_roi}]")
        status_callback = self.run_record_note_progress()
        
        note_recorder = NoteRecorder()
        note_recorder.record_notes(video_capture=self.video_capture, starting_frame=clean_frame_idx, ending_frame=last_frame_idx, keyboard_roi=self.keyboard_roi,first_white_key="C3", first_black_key="c3", status_callback=status_callback)
        
        

        self.logger.info("Got notes, ending")
        
        note_played = note_recorder.get_notes_recorded()
        colors = postprocessing.get_possible_colors(note_played)

        for i, color in enumerate(colors):
            visualization.display_color(color, f"Color nb {i}")

        cv2.waitKey(0)
            

        # # write notes to music sheet

        # cluster_centers, clustered_notes = postprocessing.get_clusters(note_recorder.get_notes_recorded())
        # fps = self.video_capture.get(cv2.CAP_PROP_FPS)
        # suggested_bpm = postprocessing.get_possible_bpm(fps, cluster_centers)

        # cluster_population_percentage = [ round((clustered_notes == cluster_idx).mean() *100) for cluster_idx in range(len(cluster_centers))]
        
        # bpm_picker = MusicInfoWindow(self.root, suggested_bpm, cluster_population_percentage)
        # bpm_picker.pack()

        # bpm = bpm_picker.pick_number()

        # self.logger.info(f"BPM chosen: [{bpm}]")

        # # Create midi file

        # note_writer = MidiWriter(note_recorder.get_notes_recorded(), bpm, fps)
        # stream = note_writer.generate_stream()
        # stream.timeSignature = music21.meter.TimeSignature('4/4')
        # stream.show('lily.pdf')
        # stream.write('midi', fp='./output_files/go.mid')

        # # convert to xml with musescore
        
        # subprocess.run(['C:\\Program Files\\MuseScore 4\\bin\\MuseScore4.exe', "--export-to","./output_files/go.musicxml", "./output_files/go.mid"])

        # t = music21.converter.parse("./output_files/go.musicxml")
        
        # newScore = music21.stream.Score()


        # for idx, part in enumerate(t.parts):
            
        #     flat_part = part.flatten()
        #     # Only for the first part
        #     if idx == 0:
        #         current_bpm = flat_part.getElementsByClass(music21.tempo.MetronomeMark)[0]
        #         new_bpm = music21.tempo.MetronomeMark(number=bpm)
        #         new_bpm.placement = "above"
        #         flat_part.replace(current_bpm, new_bpm)

            
        #     flat_part.timeSignature = music21.meter.TimeSignature('4/4')
            
        #     flat_part.makeNotation(inPlace=True)
        #     newScore.insert(0, flat_part)
        
        # newScore.write('musicxml', fp='./output_files/final.xml')
        
        # self.quit()


    
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
    music21.environment.set("lilypondPath", "C:\\Program Files (x86)\\lilypond\\bin\\lilypond.exe")

    args = parser.parse_args()
    setup_image_logger(args.loglevel)
    
    root = tk.Tk()
    root.title("My Tkinter Application")


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