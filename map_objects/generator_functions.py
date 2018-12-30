import libtcodpy as libtcod
from random import randint
from copy import deepcopy

from render_functions import RenderOrder

from components.stairs import Stairs

from entity import Entity


from map_objects.tile import Tile
from map_objects.rectangle import Rect

def make_map(self, max_rooms, room_min_size, room_max_size, map_width, map_height, players, entities):
	self.tiles = initialize_tiles(self)
	rooms = []
	num_rooms = 0

	center_of_last_room_x = None
	center_of_last_room_y = None

	for r in range(max_rooms):
		# random width and height
		w = randint(room_min_size, room_max_size)
		h = randint(room_min_size, room_max_size)
		# random position without going out of the boundaries of the map
		x = randint(0, map_width - w - 1)
		y = randint(0, map_height - h - 1)

		# "Rect" class makes rectangles easier to work with
		new_room = Rect(x, y, w, h)

		# run through the other rooms and see if they intersect with this one
		for other_room in rooms:
			if new_room.encompass(other_room):
				break
		else:
			# this means there are no intersections, so this room is valid
			# For-else statements are so cool

			# "paint" it to the map's tiles
			self.create_room(new_room)

			# center coordinates of new room, will be useful later
			(new_x, new_y) = new_room.center()

			# Update last room
			center_of_last_room_x = new_x
			center_of_last_room_y = new_y

			if num_rooms == 0:
				# this is the first room, where the players start at
				players_placed = 0

				while players_placed != len(players):
					# Choose a random location in the room
					x = randint(new_room.x1 + 1, new_room.x2 - 1)
					y = randint(new_room.y1 + 1, new_room.y2 - 1)
					if not any([entity for entity in players if entity.x == x and entity.y == y]):
						players[players_placed].x = x
						players[players_placed].y = y
						players_placed += 1
			else:
				# all rooms after the first:
				# connect it to the previous room with a tunnel

				# center coordinates of previous room
				(prev_x, prev_y) = rooms[num_rooms - 1].center()

				# flip a coin (random number that is 0 or 1)
				if randint(0,1) == 1:
					# first move horizontally, then vertically
					self.create_h_tunnel(prev_x, new_x, prev_y)
					self.create_v_tunnel(prev_y, new_y, new_x)
				else:
					# first move vertically, then horizontally
					self.create_v_tunnel(prev_y, new_y, prev_x)
					self.create_h_tunnel(prev_x, new_x, new_y)

			# Add baddies
			self.place_entities(new_room, entities)

			# finally, append the new room to the list
			rooms.append(new_room)
			num_rooms += 1

	stairs_component = Stairs(self.dungeon_level + 1)
	down_stairs = Entity(center_of_last_room_x, center_of_last_room_y, '>', libtcod.white, 'Stairs',
						render_order = RenderOrder.STAIRS, stairs=stairs_component)
	entities.append(down_stairs)

def make_town(game_map, max_rooms, room_min_size, room_max_size, map_width, map_height, players, entities):
	game_map.tiles = initialize_tiles(game_map, Tile(False, "Grass", libtcod.Color(0,128,0), libtcod.Color(32, 32, 125), char='.'))
	rooms = []
	num_rooms = 0

	center_of_last_room_x = None
	center_of_last_room_y = None

	for r in range(max_rooms):
		# random width and height
		w = randint(room_min_size, room_max_size)
		h = randint(room_min_size, room_max_size)
		# random position without going out of the boundaries of the map
		x = randint(1, map_width - w - 2)
		y = randint(1, map_height - h - 2)

		# "Rect" class makes rectangles easier to work with
		new_room = Rect(x, y, w, h)

		# run through the other rooms and see if they intersect with this one
		# leave a 1 tile gap between rooms
		for other_room in rooms:
			temp_room = Rect(other_room.x1-1, other_room.y1-1, other_room.x2-other_room.x1+2, other_room.y2-other_room.y1+2)
			if new_room.intersect(temp_room):
				break
		else:
			# this means there are no intersections, so this room is valid
			# For-else statements are so cool

			# "paint" it to the map's tiles
			create_house(game_map, new_room)

			# center coordinates of new room, will be useful later
			(new_x, new_y) = new_room.center()

			# Update last room
			center_of_last_room_x = new_x
			center_of_last_room_y = new_y

			if num_rooms == 0:
				# this is the first room, where the players start at
				players_placed = 0

				while players_placed != len(players):
					# Choose a random location in the room
					x = randint(new_room.x1 + 1, new_room.x2 - 1)
					y = randint(new_room.y1 + 1, new_room.y2 - 1)
					if not any([entity for entity in players if entity.x == x and entity.y == y]):
						players[players_placed].x = x
						players[players_placed].y = y
						players_placed += 1
			
			# cut out a door
			# decide which wall to cut it on
			side = randint(0,3)
			if side == 0:
				# North Wall
				game_map.tiles[randint(new_room.x1+1, new_room.x2-1)][new_room.y1] = Tile(False, "Door", libtcod.Color(200, 180, 50), libtcod.Color(50, 50, 150), char='+', block_sight=True)
			elif side == 1:
				# South wall
				game_map.tiles[randint(new_room.x1+1, new_room.x2-1)][new_room.y2] = Tile(False, "Door", libtcod.Color(200, 180, 50), libtcod.Color(50, 50, 150), char='+', block_sight=True)
			elif side == 2:
				# West wall
				game_map.tiles[new_room.x1][randint(new_room.y1+1, new_room.y2-1)] = Tile(False, "Door", libtcod.Color(200, 180, 50), libtcod.Color(50, 50, 150), char='+', block_sight=True)
			else:
				# East wall
				game_map.tiles[new_room.x2][randint(new_room.y1+1, new_room.y2-1)] = Tile(False, "Door", libtcod.Color(200, 180, 50), libtcod.Color(50, 50, 150), char='+', block_sight=True)
				
			# Add baddies
			game_map.place_entities(new_room, entities)

			# finally, append the new room to the list
			rooms.append(new_room)
			num_rooms += 1

	stairs_component = Stairs(game_map.dungeon_level + 1)
	down_stairs = Entity(center_of_last_room_x, center_of_last_room_y, '>', libtcod.white, 'Stairs',
						render_order = RenderOrder.STAIRS, stairs=stairs_component)
	entities.append(down_stairs)

def create_house(game_map, room):
	# Draw corners
	game_map.tiles[room.x1][room.y1] = Tile(True, "Wall", libtcod.dark_sepia, libtcod.Color(0,0,100), char=201)
	game_map.tiles[room.x2][room.y1] = Tile(True, "Wall", libtcod.dark_sepia, libtcod.Color(0,0,100), char=187)
	game_map.tiles[room.x1][room.y2] = Tile(True, "Wall", libtcod.dark_sepia, libtcod.Color(0,0,100), char=200)
	game_map.tiles[room.x2][room.y2] = Tile(True, "Wall", libtcod.dark_sepia, libtcod.Color(0,0,100), char=188)
		
	# Draw horizontal walls
	for x in range(room.x1+1, room.x2):
		game_map.tiles[x][room.y1] = Tile(True, "Wall", libtcod.dark_sepia, libtcod.Color(0,0,100), char=205)
		game_map.tiles[x][room.y2] = Tile(True, "Wall", libtcod.dark_sepia, libtcod.Color(0,0,100), char=205)

	# Draw vertical walls
	for y in range(room.y1+1, room.y2):
		game_map.tiles[room.x1][y] = Tile(True, "Wall", libtcod.dark_sepia, libtcod.Color(0,0,100), char=186)
		game_map.tiles[room.x2][y] = Tile(True, "Wall", libtcod.dark_sepia, libtcod.Color(0,0,100), char=186)

	for x in range(room.x1+1, room.x2):
		for y in range(room.y1+1, room.y2):
			game_map.tiles[x][y] = Tile(False, "Floor", libtcod.Color(130, 110, 50), libtcod.Color(0,0,100), char='.')

def initialize_tiles(game_map, tile=Tile(True, "Wall", libtcod.Color(130, 110, 50), libtcod.Color(0,0,100), char='#')):
	# Make a big ol' pile of floor tiles
	tiles = [[deepcopy(tile) for y in range(game_map.height)] for x in range(game_map.width)]

	return tiles