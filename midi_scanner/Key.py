from midi_scanner.utils.preprocessing import get_lower_image
from midi_scanner.utils.ColorMidiScanner import ColorFormat, MidiScannerColor


class Key:

	def __init__(self, note , start_x, end_x):
		self.start_x = start_x
		self.end_x = end_x
		self.note = note
	
	def is_black(self):
		return self.note == self.note.lower()
	
	def __repr__(self):
		return self.__str__()
	
	def __str__(self):
	 	return f"Key: note:[{self.note}]"
	
class PressedKey(Key):

	def __init__(self, key:Key, average_color: MidiScannerColor):
		super().__init__(key.note, key.start_x, key.end_x)
		self.average_color = average_color
