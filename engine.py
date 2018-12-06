import libtcodpy as libtcod

from entity import Entity
from input_handlers import handle_keys
from map_objects.game_map import GameMap
from render_functions import clear_all, render_all


def main():
	# Screen size
	screen_width = 80
	screen_height = 50

	# Map size
	map_width = 80
	map_height = 45

	# Generator constants
	room_max_size = 10
	room_min_size = 6
	max_rooms = 30

	# Colors
	colors = {
		'dark_wall': libtcod.Color(5,5,25),
		'dark_ground': libtcod.Color(100, 100, 150)
	}

	# Starting entities
	player = Entity(int(screen_width/2), int(screen_height/2), '@', libtcod.white)
	npc = Entity(int(screen_width/2 - 5), int(screen_height/2), '@', libtcod.yellow)
	entities = [npc, player]

	# Set font
	libtcod.console_set_custom_font('arial10x10.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
	# Create game window
	libtcod.console_init_root(screen_width, screen_height, 'Roguelike Bitches', False)

	# Create a console (Drawing Layer?)
	con = libtcod.console_new(screen_width, screen_height)

	# Create the game map
	game_map = GameMap(map_width, map_height)
	game_map.make_map(max_rooms, room_min_size, room_max_size, map_width, map_height, player)

	# Holds keyboard and mouse input
	key = libtcod.Key()
	mouse = libtcod.Mouse()

	# Game loop
	while not libtcod.console_is_window_closed():
		# Input listener I guess
		libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS, key, mouse)

		# Render all entities
		render_all(con, entities, game_map, screen_width, screen_height, colors)
		# Clear console for next frame
		libtcod.console_flush()

		# Clear old entity positions
		clear_all(con, entities)

		# Determine action
		action = handle_keys(key)

		# Process the action object
		move = action.get('move')
		exit = action.get('exit')
		fullscreen = action.get('fullscreen')

		# Movement
		if move:
			dx, dy = move
			if not game_map.is_blocked(player.x + dx, player.y + dy):
				player.move(dx, dy)

		# Exit on escape
		if exit:
			return True

		# Toggle fullscreen
		if fullscreen:
			libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())


if __name__ == '__main__':
	main()