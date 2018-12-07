import libtcodpy as libtcod

from components.fighter import Fighter
from death_functions import kill_monster, kill_player
from entity import Entity, get_blocking_entities_at_location
from fov_functions import initialize_fov, recompute_fov
from game_states import GameStates
from input_handlers import handle_keys
from map_objects.game_map import GameMap
from render_functions import clear_all, render_all, RenderOrder


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

	# FOV constants
	fov_algorithm = 0
	fov_light_walls = True
	fov_radius = 10

	max_monsters_per_room = 3

	# Colors
	colors = {
		'dark_wall': libtcod.Color(50,50,75),
		'dark_ground': libtcod.Color(100, 100, 150),
		'light_wall': libtcod.Color(130, 110, 50),
		'light_ground': libtcod.Color(200, 180, 50)
	}

	# Starting entities
	fighter_component = Fighter(hp=30, defense=2, power=5)
	player = Entity(0, 0, '@', libtcod.white, 'Player', blocks = True, render_order = RenderOrder.ACTOR, fighter = fighter_component)
	entities = [player]

	# Set font
	libtcod.console_set_custom_font('arial10x10.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
	# Create game window
	libtcod.console_init_root(screen_width, screen_height, 'Roguelike Bitches', False)

	# Create a console (Drawing Layer?)
	con = libtcod.console_new(screen_width, screen_height)

	# Create the game map
	game_map = GameMap(map_width, map_height)
	game_map.make_map(max_rooms, room_min_size, room_max_size, map_width, map_height, player, entities, max_monsters_per_room)

	# Flags if we need to update FOV
	fov_recompute = True

	fov_map = initialize_fov(game_map)

	# Holds keyboard and mouse input
	key = libtcod.Key()
	mouse = libtcod.Mouse()

	# Keep track of who's turn it is
	game_state = GameStates.PLAYERS_TURN

	# Game loop
	while not libtcod.console_is_window_closed():
		# Input listener I guess
		libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS, key, mouse)

		# Update fov if needed
		if fov_recompute:
			recompute_fov(fov_map, player.x, player.y, fov_radius, fov_light_walls, fov_algorithm)

		# Render all entities
		render_all(con, entities, player, game_map, fov_map, fov_recompute, screen_width, screen_height, colors)

		fov_recompute = False

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

		# For the message log
		player_turn_results = []

		# Movement
		if move and game_state == GameStates.PLAYERS_TURN:
			dx, dy = move
			destination_x = player.x + dx
			destination_y = player.y + dy


			if not game_map.is_blocked(destination_x, destination_y):
				target = get_blocking_entities_at_location(entities, destination_x, destination_y)

				# If the way is blocked by a baddie
				if target:
					attack_results = player.fighter.attack(target)
					player_turn_results.extend(attack_results)
				else:
					player.move(dx, dy)

					fov_recompute = True

				game_state = GameStates.ENEMY_TURN

		# Exit on escape
		if exit:
			return True

		# Toggle fullscreen
		if fullscreen:
			libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())

		# Print message results
		for player_turn_result in player_turn_results:
			message = player_turn_result.get('message')
			dead_entity = player_turn_result.get('dead')

			if message:
				print(message)

			if dead_entity:
				if dead_entity == player:
					message, game_state = kill_player(dead_entity)
				else:
					message = kill_monster(dead_entity)

				print(message)

		# Enemy Movement
		if game_state == GameStates.ENEMY_TURN:
			for entity in entities:
				if entity.ai:
					enemy_turn_results = entity.ai.take_turn(player, fov_map, game_map, entities)

					for enemy_turn_result in enemy_turn_results:
						message = enemy_turn_result.get('message')
						dead_entity = enemy_turn_result.get('dead')

						if message:
							print(message)

						if dead_entity:
							if dead_entity == player:
								message, game_state = kill_player(dead_entity)
							else:
								message = kill_monster(dead_entity)

							print(message)

							if game_state == GameStates.PLAYER_DEAD:
								break

					if game_state == GameStates.PLAYER_DEAD:
						break
			else:
				game_state = GameStates.PLAYERS_TURN


if __name__ == '__main__':
	main()