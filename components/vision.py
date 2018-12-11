from fov_functions import recompute_fov

class Vision:
	def __init__(self, vision_radius, fov_map=None):
		self.fov_map = fov_map
		self.vision_radius = vision_radius

	def update_fov():
		recompute_fov(self.fov_map, self.owner.x, self.owner.y, vision_radius, light_walls=True, algorithm=0)
	