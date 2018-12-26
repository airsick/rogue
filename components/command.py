class Command:
	def __init__(self, use_function=None, repeat=1, owner=None, *args, **kwargs):
		self.use_function = use_function
		self.repeat = repeat
		self.owner = owner
		self.args = args
		self.kwargs = kwargs

	def execute(self):
		results = []
		if self.repeat != 0:
			command_results = self.use_function(self.args, self.kwargs)
			results.extend(command_results)
			self.repeat = max(-1, self.repeat - 1)

		if self.repeat == 0:
			results.append({'finish_command':True})

		return results

class MoveCommand:
	def __init__(self, repeat, dx, dy, entities, game_map):
		self.repeat = repeat
		self.dx = dx
		self.dy = dy
		self.entities = entities
		self.game_map = game_map

	def execute(self):
		results = []
		if self.repeat != 0:
			moved = False
			# End turn if they waited
			if self.dx == 0 and self.dy == 0:
				results.append({'end_turn':True})
			# Otherwise try to move towards target
			else:
				moved = self.owner.move_towards(self.owner.x + self.dx, self.owner.y + self.dy, self.game_map, self.entities)
			# Only end turn if they moved (or waited)
			if moved:
				results.append({'redo_fov': True})
				results.append({'end_turn':True})
			self.repeat = max(-1, self.repeat - 1)

		if self.repeat == 0:
			results.append({'finish_command':True})

		return results

class FollowCommand:
	def __init__(self, repeat, target, entities, game_map):
		self.repeat = repeat
		self.target = target
		self.entities = entities
		self.game_map = game_map

	def execute(self):
		results = []
		if self.repeat != 0:
			# Don't move into their space
			if self.owner.distance_to(self.target) >= 2:
				self.owner.move_astar(self.target, self.entities, self.game_map)
				results.append({'redo_fov': True})
			results.append({'end_turn':True})
			self.repeat = max(-1, self.repeat - 1)

		if self.repeat == 0:
			results.append({'finish_command':True})
			print('finish')

		return results