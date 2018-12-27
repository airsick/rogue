class Tile:
	"""
	A tile on a map. It may or may not be blocked, and may or may not block sight.
	"""
	def __init__(self, blocked, name, light_color, dark_color, block_sight=None, char=None):
		self.blocked = blocked
		self.name = name
		self.light_color = light_color
		self.dark_color = dark_color
		self.char = char

		# By default, if a tile is blocked, it also blocks sight
		if block_sight is None:
			block_sight = blocked

		self.block_sight = block_sight

		self.explored = False