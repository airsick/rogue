import libtcodpy as libtcod
from random import randint

from render_functions import RenderOrder

from components.ai import BasicMonster
from components.equipment import EquipmentSlots
from components.equippable import Equippable
from components.fighter import Fighter
from components.item import Item
from components.stairs import Stairs

from entity import Entity

from game_messages import Message

from item_functions import heal, cast_lightning, cast_fireball, cast_confuse

from map_objects.tile import Tile
from map_objects.rectangle import Rect
from map_objects.generator_functions import make_map, make_town

from random_utils import from_dungeon_level, random_choice_from_dict


class GameMap:
	def __init__(self, width, height, walls=True, dungeon_level=1, generator=make_map):
		self.width = width
		self.height = height
		self.tiles = self.initialize_tiles(walls)
		self.make_map = generator

		self.dungeon_level = dungeon_level

	def initialize_tiles(self, walls=True):
		# Make a big ol' pile of floor tiles
		tiles = [[Tile(walls, "Wall" if walls else "Floor", libtcod.Color(130, 110, 50), libtcod.Color(0,0,100), char='#' if walls else '.') for y in range(self.height)] for x in range(self.width)]

		return tiles

	

	def create_room(self, room):
		# Go through the tiles in the rectangle and make them passable
		for x in range(room.x1 + 1, room.x2):
			for y in range(room.y1 + 1, room.y2):
				self.tiles[x][y] = Tile(False, "Floor", libtcod.Color(0,128,0), libtcod.Color(32, 32, 125), char='.')

	def create_h_tunnel(self, x1, x2, y):
		for x in range(min(x1, x2), max(x1, x2) + 1):
			self.tiles[x][y] = Tile(False, "Floor", libtcod.Color(200, 180, 50), libtcod.Color(50, 50, 150), char='.')

	def create_v_tunnel(self, y1, y2, x):
		for y in range(min(y1, y2), max(y1, y2) + 1):
			self.tiles[x][y] = Tile(False, "Floor", libtcod.Color(200, 180, 50), libtcod.Color(50, 50, 150), char='.')

	def place_entities(self, room, entities):
		max_monsters_per_room = from_dungeon_level([[2, 1], [3, 4], [5, 6]], self.dungeon_level)
		max_items_per_room = from_dungeon_level([[1, 1], [2, 4]], self.dungeon_level)

		# Get a random number of monsters
		number_of_monsters = randint(0, max_monsters_per_room)
		number_of_items = randint(0, max_items_per_room)

		monster_chances = {
			'rat': from_dungeon_level([[80, 1], [40, 3], [20, 5], [ 0, 7]], self.dungeon_level),
			'orc': from_dungeon_level([[20, 1], [35, 3], [50, 5], [40, 7]], self.dungeon_level),
			'troll': from_dungeon_level([       [15, 3], [30, 5], [60, 7]], self.dungeon_level)
		}
		item_chances = {
			'healing_potion': 35,
			'sword': from_dungeon_level([[5, 4]], self.dungeon_level),
			'shield': from_dungeon_level([[15, 8]], self.dungeon_level),
			'lightning_scroll': from_dungeon_level([[25, 4]], self.dungeon_level),
			'fireball_scroll': from_dungeon_level([[25, 6]], self.dungeon_level),
			'confusion_scroll': from_dungeon_level([[10, 2]], self.dungeon_level)
		}

		for i in range(number_of_monsters):
			# Choose a random location in the room
			x = randint(room.x1 + 1, room.x2 - 1)
			y = randint(room.y1 + 1, room.y2 - 1)


			if not any([entity for entity in entities if entity.x == x and entity.y == y]):
				monster_choice = random_choice_from_dict(monster_chances)

				if monster_choice == 'rat':
					fighter_component = Fighter(hp=5, defense=0, power=3, xp=20)
					ai_component = BasicMonster()

					monster = Entity(x, y, 'r', libtcod.lighter_sepia, 'Rat', blocks = True, 
									render_order=RenderOrder.ACTOR, fighter=fighter_component, ai=ai_component)
				
				elif monster_choice == 'orc':
					fighter_component = Fighter(hp=20, defense=0, power=4, xp=35)
					ai_component = BasicMonster()

					monster = Entity(x, y, 'o', libtcod.desaturated_green, 'Orc', blocks = True, 
									render_order=RenderOrder.ACTOR, fighter=fighter_component, ai=ai_component)
				elif monster_choice == 'troll':
					fighter_component = Fighter(hp=30, defense=2, power=8, xp=100)
					ai_component = BasicMonster()

					monster = Entity(x, y, 'T', libtcod.darker_green, 'Troll', blocks = True, 
									render_order=RenderOrder.ACTOR, fighter=fighter_component, ai=ai_component)

				entities.append(monster)

		# Place items
		for i in range(number_of_items):
			x = randint(room.x1 + 1, room.x2 - 1)
			y = randint(room.y1 + 1, room.y2 - 1)

			if not any([entity for entity in entities if entity.x == x and entity.y == y]):
				item_choice = random_choice_from_dict(item_chances)

				# Healing potion
				if item_choice == 'healing_potion':
					item_component = Item(use_function=heal, amount=40)
					item = Entity(x, y, '!', libtcod.violet, 'Healing Potion', render_order=RenderOrder.ITEM,
									item=item_component)
				# Sword
				if item_choice == 'sword':
					equippable_component = Equippable(EquipmentSlots.MAIN_HAND, power_bonus=3)
					item = Entity(x, y, '/', libtcod.sky, 'Sword', render_order=RenderOrder.ITEM,
									equippable=equippable_component)
				# Shield
				if item_choice == 'shield':
					equippable_component = Equippable(EquipmentSlots.OFF_HAND, power_bonus=1)
					item = Entity(x, y, '[', libtcod.darker_orange, 'Shield', render_order=RenderOrder.ITEM,
									equippable=equippable_component)
				# Lightning scroll
				if item_choice == 'lightning_scroll':
					item_component = Item(use_function=cast_lightning, damage=40, maximum_range=5)
					item = Entity(x, y, '#', libtcod.yellow, 'Lightning Scroll', render_order=RenderOrder.ITEM,
									item=item_component)
				# Fireball scroll
				if item_choice == 'fireball_scroll':
					item_component = Item(use_function=cast_fireball, targeting=True, targeting_message=Message(
										'Left-click a target tile for the fireball, or right-click to cancel.', libtcod.light_cyan),
										damage=25, radius=3)
					item = Entity(x, y, '#', libtcod.red, 'Fireball Scroll', render_order=RenderOrder.ITEM,
									item=item_component)
				# Confusion scroll
				if item_choice == 'confusion_scroll':
					item_component = Item(use_function=cast_confuse, targeting=True, targeting_message=Message(
										'Left-click aan enemy to confuse it, or right-click to cancel.', libtcod.light_cyan),)
					item = Entity(x, y, '#', libtcod.light_pink, 'Confusion Scroll', render_order=RenderOrder.ITEM,
									item=item_component)
				entities.append(item)

	def is_blocked(self, x, y):
		if self.tiles[x][y].blocked:
			return True

		return False

	def next_floor(self, players, message_log, constants):
		self.dungeon_level += 1
		entities = []
		for player in players:
			entities.append(player)

		self.make_map(self, constants['max_rooms'], constants['room_min_size'], constants['room_max_size'],
					  constants['map_width'], constants['map_height'], players, entities)

		for player in players:
			player.fighter.heal(player.fighter.max_hp // 2)

		message_log.add_message(Message('You take a moment to rest, and recover your strength.', libtcod.light_violet))

		return entities
