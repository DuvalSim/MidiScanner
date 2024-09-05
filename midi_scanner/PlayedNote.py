from midi_scanner.utils.ColorMidiScanner import MidiScannerColor

class PlayedNote:

	def __init__(self, note, first_frame, color: MidiScannerColor) -> None:
		self.start_frame = first_frame
		self.nb_frame = 0
		self.note = note
		self._color = color

	def is_black(self) -> bool:
		return self.note == self.note.lower()

	def get_played_color(self) -> MidiScannerColor:
		return self._color

	def __repr__(self):
		return self.__str__()
	
	def __str__(self):
	 	return f"PlayedNote: start:[{self.start_frame}] - nb frames:[{self.nb_frame}] - note:[{self.note}]"	
