from music21 import stream, meter, key, metadata, converter, clef
import music21 as music21
from midi_scanner.PlayedNote import PlayedNote

class ScoreWriter:

    note_nb_frames = [ played_note.nb_frame for played_note in  self._notes_played]

    RYTHM_LENGTH = [0.25, 0.5, 0.75, 1, 1.25, 1.5, 2, 3 , 4]

    def __init__(self) -> None:

        
        pass

    def create_part(self, played_note_list, played_rythms_list):
        trebble_clef = clef.TrebleClef()
        part = stream.Part([trebble_clef])

        for note, rythm in zip(played_note_list, played_rythms_list):
            if note != note.upper():
                note = note.upper() + "#"
            new_note = music21.note.Note(note)
            new_note.duration.quarterLength = rythm

            part.append(new_note)
        
        part.show()

    
    def create_musescore_file():
        # Create a stream (score) to hold the music
        score = stream.Score()

        # Add metadata to the score
        score.metadata = metadata.Metadata()
        score.metadata.title = "My MuseScore File"
        score.metadata.composer = "Your Name"

        # Create a part to hold the notes
        part = stream.Part()

        # Set the key and time signature
        part.append(key.KeySignature(0))  # 0 means no sharps or flats (C major)
        part.append(meter.TimeSignature('4/4'))

        # Add some notes to the part
        notes = ["C4", "D4", "E4", "F4", "G4", "A4", "B4", "C5"]
        for n in notes:
            part.append(note.Note(n, quarterLength=1))

        # Append the part to the score
        n = note.Note('C4')
        n.show()
        # print(t)
        # c.show('midi')
        

if __name__ == "__main__":
    NoteWriter.create_musescore_file()
