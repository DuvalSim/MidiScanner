from typing import List
from midi_scanner.Keyboard import Keyboard
from midi_scanner.PlayedNote import PlayedNote
from midi_scanner.Key import Key, PressedKey

from matplotlib import pyplot as plt

from midi_scanner.utils.ImageProcessor import ImageProcessor

import cv2

import logging

from midi_scanner.utils.visualization import display_pressed_keys

from typing import Callable

class NoteRecorder:
    
    def __init__(self) -> None:
        
        self._notes_playing:List[PlayedNote] = []
        self._notes_played:List[PlayedNote] = []
        self._current_frame = 0

        self.logger= logging.getLogger("NoteRecorder")

    

    def _populate_next_frame(self, pressed_keys:List[PressedKey]):
        
        self._current_frame += 1

        # tmp_pressed_keys = pressed_keys.copy()

        # notes_played_to_add:List[PlayedNote] = []

        # Keys released this frame
        ended_notes = []

        # print("--------Frame--------------")
        # print(self._notes_playing)
        # print(pressed_keys)
        for note_idx, note_playing in enumerate(self._notes_playing):
            
            for key_idx, pressed_key in enumerate(pressed_keys):
                
                # a key that was pressed is still pressed in that frame
                if pressed_key.note == note_playing.note:
                
                    self._notes_playing[note_idx].nb_frame += 1
                    pressed_keys.pop(key_idx)

                    break
            else:
                # The key is no longer pressed
                ended_notes.append(note_playing)


        for ended_note in ended_notes:
            self._notes_played.append(ended_note)
            self._notes_playing.remove(ended_note)

        # iterate through the remaining pressed keys
        # Add them to the notes being played   
        for pressed_key in pressed_keys:
            self._notes_playing.append(PlayedNote(pressed_key.note, first_frame=self._current_frame, color=pressed_key.average_color))
        

    def _end_recording(self):

        self.clean_ending = True

        if len(self._notes_playing) > 0:
            self.logger.warning(f"While ending recording - At least one note was still being played: {self._notes_playing} ")
            self._populate_next_frame([])
            self.clean_ending = False
            
    
    def sort_played_notes(self):
        self._notes_played = sorted(self._notes_played, key=lambda x: x.start_frame)

    def round_frames(self):

        for note_idx in range(len(self._notes_played)):
            self._notes_played[note_idx].start_frame = round(self._notes_played[note_idx].start_frame, -1)
            self._notes_played[note_idx].nb_frame = max(round(self._notes_played[note_idx].nb_frame, -1), 10) # do not want a note with 0 duration

    def get_starting_frame_histogram(self):

        list_to_plot = [note.nb_frame for note in self._notes_played]
        list_min = min(list_to_plot)
        list_max = max(list_to_plot)
        bins = [ i for i in range(list_min, list_max + 5, 1)]
        n, _,_ = plt.hist([note.nb_frame for note in self._notes_played], bins=bins)

        plt.show()

    def get_notes_recorded(self) -> List[PlayedNote]:
        return self._notes_played
    
    def record_notes(self, video_capture, starting_frame, ending_frame, keyboard_roi, first_white_key, first_black_key, status_callback: Callable[[float],None] = None ):

        self._notes_playing = []
        self._notes_played = []
        self._current_frame = 0

        # TODO: add ratio for image
        image_processor = ImageProcessor(keyboard_roi)
 
        total_nb_frames = video_capture.get(cv2.CAP_PROP_FRAME_COUNT)
        video_capture.set(cv2.CAP_PROP_POS_FRAMES,starting_frame)

        ret, first_frame = video_capture.read()

        first_frame = image_processor.get_keyboard_image(first_frame)
        
        keyboard = Keyboard(first_frame, first_white_key, first_black_key)

        fps = video_capture.get(cv2.CAP_PROP_FPS)

        ending_frame = min(ending_frame, total_nb_frames -1)
        max_nb_frame = ending_frame - starting_frame
        nb_frame = 0
        while True:
            # Read the next frame from the video
            ret, current_frame = video_capture.read()

            # Check if the frame was successfully read
            if not ret:
                break

            cropped_frame = image_processor.get_keyboard_image(current_frame)

            #bot, top = image_processor.get_lower_image(cropped_frame)

            self.logger.debug_image(cropped_frame, "Current frame")            
            
            pressed_keys = keyboard.get_pressed_keys(cropped_frame)
            
            
            display_pressed_keys(cropped_frame, pressed_keys, level=logging.DEBUG)
            
            self._populate_next_frame(pressed_keys)
            
            nb_frame += 1

            if nb_frame%100 == 0:
                self.logger.debug(f"Doing [{nb_frame}]/[{max_nb_frame}]")
            if status_callback is not None:
                status_callback((nb_frame/max_nb_frame)*100)

            
            #k = cv2.waitKey(1)
            # Wait for a key press to exit
            # if (k == ord('q')) or (nb_frame >= max_nb_frame):
            #     cv2.destroyAllWindows()
            #     break
            if (nb_frame >= max_nb_frame):
                cv2.destroyAllWindows()
                break


        # Release the video capture object and close all windows

        self._end_recording()

        self.sort_played_notes()

        #self.get_starting_frame_histogram()
        #note_recorder.round_frames()


        


