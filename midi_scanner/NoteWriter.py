from typing import List
import music21 as music21
from midi_scanner.PlayedNote import PlayedNote

from sklearn.cluster import KMeans
from kneed import KneeLocator
from matplotlib import pyplot as plt

import numpy as np

import logging

class MidiWriter:

    RYTHM_LENGTH = [0.25, 0.5, 0.75, 1, 1.25, 1.5, 2, 3 , 4]

    def __init__(self, note_list: List[PlayedNote], note_assigned_cluster: List[int], bpm: int, frame_per_seconds: int) -> None:
        self.logger = logging.getLogger("MidiWriter")
        
        unique_clusters = sorted(set(note_assigned_cluster))
        self.notes_to_write = [[] for _ in range(len(unique_clusters))]
        self.logger.debug(f"Nb Notes:{len(note_list)} - {len(note_assigned_cluster)}")
        for note_idx, note in enumerate(note_list):
            
            cluster_idx = note_assigned_cluster[note_idx]
            self.notes_to_write[cluster_idx].append(note)

        self.bpm = bpm
        self.beat_per_frame =  bpm / (frame_per_seconds*60)

    def generate_score(self):
        score = music21.stream.Score()
        # time_signature = music21.meter.TimeSignature('4/4')
        # key_signature = music21.key.KeySignature(0)  # C Major
        # tempo_mark = music21.tempo.MetronomeMark(number=self.bpm)
        
        # parts = [music21.stream.Part(), music21.stream.Part()]
        # parts[0].append(music21.clef.TrebleClef())
        # parts[1].append(music21.clef.BassClef())

        start_offset = min([note_list[0].start_frame for note_list in self.notes_to_write])

        for part_idx, note_list in enumerate(self.notes_to_write):

        #     parts[part_idx].append(time_signature)
        #     parts[part_idx].append(key_signature)
        #     parts[part_idx].append(tempo_mark)

            
            score.insert(0, self.generate_part(note_list, start_offset=start_offset))

        return score
    
    def generate_streams(self):
        streams = []
        start_offset = min([note_list[0].start_frame for note_list in self.notes_to_write])
        for note_list in self.notes_to_write:
            streams.append(self.generate_stream(note_list, start_offset))

        return streams
    
    def generate_part(self, notes_to_write, start_offset):
        stream = music21.stream.Part()

        stream.insert(0, music21.tempo.MetronomeMark(number=self.bpm))
        stream.insert(0,music21.meter.TimeSignature('4/4'))
        # stream.insert(0,music21.key.KeySignature(0))  # C Major
        
        for note_recorded in notes_to_write:

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
    
    def generate_stream(self, notes_to_write, start_offset):
        
        stream = music21.stream.Stream()

        stream.insert(0, music21.tempo.MetronomeMark(number=self.bpm))

        for note_recorded in notes_to_write:

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
