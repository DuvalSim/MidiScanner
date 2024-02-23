class PlayedNote:

	def __init__(self, note, first_frame) -> None:
		self.start_frame = first_frame
		self.nb_frame = 0
		self.note = note

	def __repr__(self):
		return self.__str__()
	
	def __str__(self):
	 	return f"PlayedNote: start:[{self.start_frame}] - nb:[{self.nb_frame}] - note:[{self.note}]"
