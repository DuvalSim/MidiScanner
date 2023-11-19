class PlayedNote:

	def __init__(self, note, first_frame) -> None:
		self.start_frame = first_frame
		self.nb_frame = 0
		self.note = note
