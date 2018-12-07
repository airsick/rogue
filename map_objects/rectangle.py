class Rect:
	def __init__(self, x, y, w, h):
		self.x1 = x
		self.y1 = y
		self.x2 = x + w
		self.y2 = y + h

	def center(self):
		center_x = int((self.x1 + self.x2) / 2)
		center_y = int((self.y1 + self.y2) / 2)
		return (center_x, center_y)

	# Returns true if this rectangle intersects with another one
	def intersect(self, other):
		# Rectangles encompass entirely different spaces
		"""return ((self.x1 <= other.x2 and self.x1 >= other.x1 and self.y1 <= other.y2 and self.y1 >= other.y1) or
				(self.x2 <= other.x2 and self.x2 >= other.x1 and self.y1 <= other.y2 and self.y1 >= other.y1) or
				(self.x1 <= other.x2 and self.x1 >= other.x1 and self.y2 <= other.y2 and self.y2 >= other.y1) or
				(self.x2 <= other.x2 and self.x2 >= other.x1 and self.y2 <= other.y2 and self.y2 >= other.y1))"""
		# Rectangles don't entirely eat other rectangles
		return (self.x1 <= other.x2 and self.x2 >= other.x1 and
				self.y1 <= other.y2 and self.y2 >= other.y2)