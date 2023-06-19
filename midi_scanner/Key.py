class Key:

	def __init__(self, note, is_black=False, start_x=None, end_x=None):
		self.start_x = start_x
		self.end_x = end_x
		self.note = note
		self.is_black = is_black
