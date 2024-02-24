from typing import List
from midi_scanner.Keyboard import Keyboard
from midi_scanner.PlayedNote import PlayedNote
from midi_scanner.Key import Key

from matplotlib import pyplot as plt

from midi_scanner.utils.ImageProcessor import ImageProcessor

import cv2

class NoteRecorder:
    
    def __init__(self) -> None:
        
        self._notes_playing:List[PlayedNote] = []
        self._notes_played:List[PlayedNote] = []
        self._current_frame = 0

    

    def populate_next_frame(self, pressed_keys:List[Key]):
        
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
            self._notes_playing.append(PlayedNote(pressed_key.note, first_frame=self._current_frame))
        

    def end_recording(self):

        if len(self._notes_playing) > 0:
            print("WARNING - a note is still playing")

            self.populate_next_frame([])

    
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
    
    def record_notes(self, video_filepath, starting_frame, ending_frame, keyboard_roi, first_white_key, first_black_key ):


        self.logger.debug("test")
        exit(0)
        self._notes_playing = []
        self._notes_played = []
        self._current_frame = 0

        # TODO: add ratio for image
        image_processor = ImageProcessor(keyboard_roi)

        video_capture = cv2.VideoCapture(video_filepath)

        # Check if the video file was successfully opened
        if not video_capture.isOpened():
            print('Error opening video file')
            raise ValueError(f"File {video_filepath} could not be opened")
        

        total_nb_frames = video_capture.get(cv2.CAP_PROP_FRAME_COUNT)
        video_capture.set(cv2.CAP_PROP_POS_FRAMES,starting_frame)

        ret, first_frame = video_capture.read()

        first_frame = image_processor.get_keyboard_image(first_frame)
        
        keyboard = Keyboard(first_frame, first_white_key, first_black_key)

        fps = video_capture.get(cv2.CAP_PROP_FPS)

        while True:
            # Read the next frame from the video
            ret, current_frame = video_capture.read()

            # Check if the frame was successfully read
            if not ret:
                break

            cropped_frame = image_processor.get_keyboard_image(current_frame)

            bot, top = image_processor.get_lower_image(cropped_frame)
            
            
            pressed_keys = keyboard.get_pressed_keys(cropped_frame)
            
            #print(pressed_keys)
            display_pressed_keys(frame, pressed_keys)

            # if nb_frame%1000 == 0:
            #     cv2.waitKey(0)
            
            note_recorder.populate_next_frame(pressed_keys)

            #cv2.waitKey(0)
            #print(nb_frame)
            nb_frame += 1
            # print(nb_frame)
            # if nb_frame > 2300:
            #     k = cv2.waitKey(0)
            
            # Wait for a key press to exit
            if (k == ord('q')) or (nb_frame > 1340):
                cv2.destroyAllWindows()
                break


        cap.release()

        # Release the video capture object and close all windows

        note_recorder.end_recording()

        note_recorder.sort_played_notes()

        note_recorder.get_starting_frame_histogram()
        #note_recorder.round_frames()

        # note_recorder.get_starting_frame_histogram()

        note_nb_frames = [ played_note.nb_frame for played_note in  note_recorder.get_notes_recorded()]

        RYTHM_LENGTH = [0.25, 0.5, 0.75, 1, 1.25, 1.5, 2, 3 , 4]

        notes_recorded = note_recorder.get_notes_recorded()
        


