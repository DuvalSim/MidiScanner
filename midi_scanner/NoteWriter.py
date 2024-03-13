from typing import List
from music21 import stream, meter, key, metadata, converter, clef
import music21 as music21
from midi_scanner.PlayedNote import PlayedNote

from sklearn.cluster import KMeans
from kneed import KneeLocator
from matplotlib import pyplot as plt

import numpy as np

import logging

class MidiWriter:

    RYTHM_LENGTH = [0.25, 0.5, 0.75, 1, 1.25, 1.5, 2, 3 , 4]

    def __init__(self, note_list: List[PlayedNote], bpm: int, frame_per_seconds: int) -> None:
        self.logger = logging.getLogger("MidiWriter")
        self.notes_to_write = note_list
        self.notes_nb_frames = [note.nb_frame for note in note_list]

        self.bpm = bpm
        self.beat_per_frame =  bpm / (frame_per_seconds*60)

    def generate_stream(self):

        start_offset = self.notes_to_write[0].start_frame
        
        stream = music21.stream.Stream()

        stream.insert(0, music21.tempo.MetronomeMark(number=self.bpm))

        for note_recorded in self.notes_to_write:

            note = music21.note.Note(note_recorded.note)
            # Set the duration of the note
            
            #duration = round(note_recorded.nb_frame / rythm_in_frames,2)
            
            duration = MidiWriter.__get_closest_rythm(note_recorded.nb_frame * self.beat_per_frame)
            
            note.duration = music21.duration.Duration(duration)
            
            # moment where to insert the note
            start = round((note_recorded.start_frame - start_offset) * self.beat_per_frame,1)
            
            # Add the Note object to the Stream
            stream.insert(start, note)
        
        return stream

    @staticmethod
    def __get_closest_rythm(duration:float):

        closest_distance = 10
        rythm_result = None
        for duration_rounded in MidiWriter.RYTHM_LENGTH:
            diff = abs(duration_rounded - duration) 
            if diff < closest_distance:
                rythm_result = duration_rounded
                closest_distance = diff

        return rythm_result

# class ScoreWriter:

#     note_nb_frames = [ played_note.nb_frame for played_note in  self._notes_played]

#     RYTHM_LENGTH = [0.25, 0.5, 0.75, 1, 1.25, 1.5, 2, 3 , 4]

#     def __init__(self) -> None:

        
#         pass

#     def create_part(self, played_note_list, played_rythms_list):
#         trebble_clef = clef.TrebleClef()
#         part = stream.Part([trebble_clef])

#         for note, rythm in zip(played_note_list, played_rythms_list):
#             if note != note.upper():
#                 note = note.upper() + "#"
#             new_note = music21.note.Note(note)
#             new_note.duration.quarterLength = rythm

#             part.append(new_note)
        
#         part.show()

    
#     def create_musescore_file():
#         # Create a stream (score) to hold the music
#         score = stream.Score()

#         # Add metadata to the score
#         score.metadata = metadata.Metadata()
#         score.metadata.title = "My MuseScore File"
#         score.metadata.composer = "Your Name"

#         # Create a part to hold the notes
#         part = stream.Part()

#         # Set the key and time signature
#         part.append(key.KeySignature(0))  # 0 means no sharps or flats (C major)
#         part.append(meter.TimeSignature('4/4'))

#         # Add some notes to the part
#         notes = ["C4", "D4", "E4", "F4", "G4", "A4", "B4", "C5"]
#         for n in notes:
#             part.append(note.Note(n, quarterLength=1))

#         # Append the part to the score
#         n = note.Note('C4')
#         n.show()
#         # print(t)
#         # c.show('midi')
        

# if __name__ == "__main__":
#     NoteWriter.create_musescore_file()
