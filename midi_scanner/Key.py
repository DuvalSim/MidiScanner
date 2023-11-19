class Key:

	def __init__(self, note , start_x, end_x):
		self.start_x = start_x
		self.end_x = end_x
		self.note = note
	
	def is_black(self):
		return self.note == self.note.lower()
