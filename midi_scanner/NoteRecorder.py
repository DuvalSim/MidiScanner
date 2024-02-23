from typing import List
from midi_scanner.PlayedNote import PlayedNote
from midi_scanner.Key import Key

from matplotlib import pyplot as plt

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
        


