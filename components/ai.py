import libtcodpy as libtcod

from random import randint

from game_messages import Message

class BasicMonster:
	def take_turn(self, players, game_map, entities):
		results = []

		monster = self.owner

		# Find closest player
		target = players[0]
		for player in players:
			if monster.distance_to(player) < monster.distance_to(target):
				target = player
				
		# Only monsters in sight get to move
		visible = libtcod.map_is_in_fov(players[0].vision.fov_map, monster.x, monster.y)
		for player in players:
			visible |= libtcod.map_is_in_fov(player.vision.fov_map, monster.x, monster.y)
		if visible:

			if monster.distance_to(target) >= 2:
				monster.move_astar(target, entities, game_map)

			elif target.fighter.hp > 0:
				attack_results = monster.fighter.attack(target)
				results.extend(attack_results)

		return results

class ConfusedMonster:
	def __init__(self, previous_ai, number_of_turns=10):
		self.previous_ai = previous_ai
		self.number_of_turns = number_of_turns

	def take_turn(self, players, game_map, entities):
		results = []

		if self.number_of_turns > 0:
			random_x = self.owner.x + randint(0, 2) -1
			random_y = self.owner.y + randint(0, 2) -1

			if random_x != self.owner.x or random_y != self.owner.y:
				self.owner.move_towards(random_x, random_y, game_map, entities)

			self.number_of_turns -= 1
		else:
			self.owner.ai = self.previous_ai
			results.append({'message': Message('The {0} is no longer confused!'.format(self.owner.name), libtcod.red)})

		return results
