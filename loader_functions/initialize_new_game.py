import libtcodpy as libtcod

from components.equipment import Equipment
from components.equippable import Equippable
from components.fighter import Fighter
from components.inventory import Inventory
from components.level import Level
from components.vision import Vision

from entity import Entity

from equipment_slots import EquipmentSlots

from game_messages import MessageLog

from game_states import GameStates

from map_objects.game_map import GameMap

from render_functions import RenderOrder

def get_constants():
	window_title = 'Roguelike Bitches'

	# Screen size
	screen_width = 80
	screen_height = 50

	# GUI constants
	bar_width = 20
	panel_height = 7
	panel_y = screen_height - panel_height

	# Message constants
	message_x = bar_width + 2
	message_width = screen_width - bar_width + 2
	message_height = panel_height - 1


	# Map size
	map_width = 80
	map_height = 43

	# Generator constants
	room_max_size = 10
	room_min_size = 6
	max_rooms = 30

	# FOV constants
	fov_algorithm = 0
	fov_light_walls = True
	fov_radius = 10

	# Number of players
	player_count = 3

	# Colors
	colors = {
		'dark_wall': libtcod.Color(0,0,100),
		'dark_ground': libtcod.Color(50, 50, 150),
		'light_wall': libtcod.Color(130, 110, 50),
		'light_ground': libtcod.Color(200, 180, 50)
	}

	constants = {
	    'window_title': window_title,
	    'screen_width': screen_width,
	    'screen_height': screen_height,
	    'bar_width': bar_width,
	    'panel_height': panel_height,
	    'panel_y': panel_y,
	    'message_x': message_x,
	    'message_width': message_width,
	    'message_height': message_height,
	    'map_width': map_width,
	    'map_height': map_height,
	    'room_max_size': room_max_size,
	    'room_min_size': room_min_size,
	    'max_rooms': max_rooms,
	    'fov_algorithm': fov_algorithm,
	    'fov_light_walls': fov_light_walls,
	    'fov_radius': fov_radius,
	    'player_count': player_count,
	    'colors': colors
	}

	return constants

def get_game_variables(constants):
	entities = []
	players = []

	for i in range(constants['player_count']):
		# Building the players
		fighter_component = Fighter(hp=100, defense=1, power=2)
		inventory_component = Inventory(26)
		level_component = Level()
		equipment_component = Equipment()
		vision_component = Vision(None, constants['fov_radius'])
		players.append(Entity(0, 0, '@', libtcod.blue, 'Player{0}'.format(i+1), blocks = True, render_order = RenderOrder.ACTOR,
						fighter = fighter_component, inventory=inventory_component, level=level_component,
						equipment=equipment_component, vision=vision_component))
		

		# Give the player a dagger to start with
		equippable_component = Equippable(EquipmentSlots.MAIN_HAND, power_bonus=2)
		dagger = Entity(0, 0, '-', libtcod.sky, 'Dagger', equippable=equippable_component)
		players[-1].inventory.add_item(dagger)
		players[-1].equipment.toggle_equip(dagger)

		entities.append(players[-1])
	# Create the game map
	game_map = GameMap(constants['map_width'], constants['map_height'])
	game_map.make_map(constants['max_rooms'], constants['room_min_size'], constants['room_max_size'], constants['map_width'], constants['map_height'], players, entities)

	# Message log
	message_log = MessageLog(constants['message_x'], constants['message_width'], constants['message_height'])

	# Keep track of who's turn it is
	game_state = GameStates.PLAYERS_TURN

	return players, entities, game_map, message_log, game_state