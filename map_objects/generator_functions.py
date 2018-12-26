import libtcodpy as libtcod
from random import randint

from render_functions import RenderOrder

from components.stairs import Stairs

from entity import Entity

from map_objects.tile import Tile
from map_objects.rectangle import Rect

def make_map(self, max_rooms, room_min_size, room_max_size, map_width, map_height, players, entities):
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
				if new_room.intersect(other_room):
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