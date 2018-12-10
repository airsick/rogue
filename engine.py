import libtcodpy as libtcod

from death_functions import kill_monster, kill_player
from entity import get_blocking_entities_at_location
from fov_functions import initialize_fov, recompute_fov
from game_messages import Message
from game_states import GameStates
from input_handlers import handle_keys, handle_mouse, handle_main_menu
from loader_functions.initialize_new_game import get_constants, get_game_variables
from loader_functions.data_loaders import load_game, save_game
from menus import main_menu, message_box
from render_functions import clear_all, render_all


def main():
	constants = get_constants()

	# Set font
	libtcod.console_set_custom_font('arial10x10.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
	# Create game window
	libtcod.console_init_root(constants['screen_width'], constants['screen_height'], constants['window_title'], False)

	# Create a console (Drawing Layer?)
	con = libtcod.console_new(constants['screen_width'], constants['screen_height'])
	panel = libtcod.console_new(constants['screen_width'], constants['panel_height'])

	players = []
	entity = []
	game_map = None
	message_log = None
	game_state = None

	show_main_menu = True
	show_load_error_message = False

	main_menu_background_image = libtcod.image_load('menu_background.png')

	# Holds keyboard and mouse input
	key = libtcod.Key()
	mouse = libtcod.Mouse()

	# Menu loop
	while not libtcod.console_is_window_closed():
		libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS | libtcod.EVENT_MOUSE, key, mouse)

		if show_main_menu:
			main_menu(con, main_menu_background_image, constants['screen_width'], constants['screen_height'])

			if show_load_error_message:
				message_box(con, 'No save game to load', 50, constants['screen_width'], constants['screen_height'])

			libtcod.console_flush()

			action = handle_main_menu(key)

			new_game = action.get('new_game')
			load_saved_game = action.get('load_game')
			exit_game = action.get('exit')

			if show_load_error_message and (new_game or load_saved_game or exit_game):
				show_load_error_message = False
			elif new_game:
				players, entities, game_map, message_log, game_state = get_game_variables(constants)
				game_state = GameStates.PLAYERS_TURN

				show_main_menu = False
			elif load_saved_game:
				try:
					players, entities, game_map, message_log, game_state = load_game(constants['player_count'])
					game_state = GameStates.PLAYERS_TURN

					show_main_menu = False
				except FileNotFoundError:
					show_load_error_message = True
			elif exit_game:
				break
		else:
			libtcod.console_clear(con)
			play_game(players, entities, game_map, message_log, game_state, con, panel, constants)

			show_main_menu = True



def play_game(players, entities, game_map, message_log, game_state, con, panel, constants):
	# Flags if we need to update FOV
	fov_recompute = True

	fov_map = initialize_fov(game_map)

	# Holds keyboard and mouse input
	key = libtcod.Key()
	mouse = libtcod.Mouse()

	game_state = GameStates.PLAYERS_TURN
	previous_game_state = game_state

	targeting_item = None

	active_player = 0
	players[active_player].color = libtcod.white

	# Game loop
	while not libtcod.console_is_window_closed():
		# Input listener I guess
		libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS | libtcod.EVENT_MOUSE, key, mouse)

		# Update fov if needed
		if fov_recompute:
			recompute_fov(fov_map, players[active_player].x, players[active_player].y, constants['fov_radius'], constants['fov_light_walls'], constants['fov_algorithm'])

		# Render all entities
		render_all(con, panel, entities, players, active_player, game_map, fov_map, fov_recompute, message_log, constants['screen_width'], constants['screen_height'],
					constants['bar_width'], constants['panel_height'], constants['panel_y'], mouse, constants['colors'], game_state)

		fov_recompute = False

		# Clear console for next frame
		libtcod.console_flush()

		# Clear old entity positions
		clear_all(con, entities)

		# Determine action
		action = handle_keys(key, game_state)
		mouse_action = handle_mouse(mouse)

		# Process the action object
		move = action.get('move')
		wait = action.get('wait')
		pickup = action.get('pickup')
		show_inventory = action.get('show_inventory')
		drop_inventory = action.get('drop_inventory')
		inventory_index = action.get('inventory_index')
		take_stairs = action.get('take_stairs')
		level_up = action.get('level_up')
		exit = action.get('exit')
		show_character_screen = action.get('show_character_screen')
		fullscreen = action.get('fullscreen')

		# Handle mouseclicks
		left_click = mouse_action.get('left_click')
		right_click = mouse_action.get('right_click')

		# For the message log
		player_turn_results = []

		# Movement
		if move and game_state == GameStates.PLAYERS_TURN:
			dx, dy = move
			destination_x = players[active_player].x + dx
			destination_y = players[active_player].y + dy


			if not game_map.is_blocked(destination_x, destination_y):
				target = get_blocking_entities_at_location(entities, destination_x, destination_y)
				# If the way is blocked by a baddie
				if target:
					attack_results = players[active_player].fighter.attack(target)
					player_turn_results.extend(attack_results)
				else:
					players[active_player].move(dx, dy)

					fov_recompute = True

				# Change active player
				players[active_player].color = libtcod.blue
				players[(active_player+1)%constants['player_count']].color = libtcod.white
				active_player += 1
				if active_player >= constants['player_count']:
					active_player = 0
					game_state = GameStates.ENEMY_TURN

		if wait:
			# Change active player
			players[active_player].color = libtcod.blue
			players[(active_player+1)%constants['player_count']].color = libtcod.white
			active_player += 1
			if active_player >= constants['player_count']:
				active_player = 0
				game_state = GameStates.ENEMY_TURN

		# Picking up an item
		elif pickup and game_state == GameStates.PLAYERS_TURN:
			for entity in entities:
				if entity.item and entity.x == players[active_player].x and entity.y == players[active_player].y:
					pickup_results = players[active_player].inventory.add_item(entity)
					player_turn_results.extend(pickup_results)

					break
			else:
				message_log.add_message(Message('There is nothing here to pick up.', libtcod.yellow))

		# Show inventory menu
		if show_inventory:
			previous_game_state = game_state
			game_state = GameStates.SHOW_INVENTORY

		# Drop inventory
		if drop_inventory:
			previous_game_state = game_state
			game_state = GameStates.DROP_INVENTORY

		# Choose inventory item
		if inventory_index is not None and previous_game_state != GameStates.PLAYER_DEAD and inventory_index < len(players[active_player].inventory.items):
			item = players[active_player].inventory.items[inventory_index]
			
			if game_state == GameStates.SHOW_INVENTORY:
				player_turn_results.extend(players[active_player].inventory.use(item, entities=entities, fov_map=fov_map))
			elif game_state == GameStates.DROP_INVENTORY:
				player_turn_results.extend(players[active_player].inventory.drop_item(item))

		# Take stairs
		if take_stairs and game_state == GameStates.PLAYERS_TURN:
			for entity in entities:
				if entity.stairs and entity.x == players[active_player].x and entity.y == players[active_player].y:
					entities = game_map.next_floor(players, message_log, constants)
					fov_map = initialize_fov(game_map)
					fov_recompute = True
					libtcod.console_clear(con)

					break
			else:
				message_log.add_message(Message('There are no stairs here.', libtcod.yellow))

		# Level up
		if level_up:
			if level_up == 'hp':
				players[active_player].fighter.base_max_hp  += 20
				players[active_player].fighter.hp += 20
			elif level_up == 'str':
				players[active_player].fighter.base_power += 1
			elif level_up == 'def':
				players[active_player].fighter.base_defense += 1

			game_state = previous_game_state

		# Character screen
		if show_character_screen:
			previous_game_state = game_state
			game_state = GameStates.CHARACTER_SCREEN

		# Targeting
		if game_state == GameStates.TARGETING:
			if left_click:
				target_x, target_y = left_click

				item_use_results = players[active_player].inventory.use(targeting_item, entities=entities, fov_map=fov_map,
														target_x=target_x, target_y=target_y)
				player_turn_results.extend(item_use_results)
			elif right_click:
				player_turn_results.append({'targeting_cancelled': True})

		# Exit on escape
		if exit:
			if game_state in (GameStates.SHOW_INVENTORY, GameStates.DROP_INVENTORY, GameStates.CHARACTER_SCREEN):
				game_state = previous_game_state
			elif game_state == GameStates.TARGETING:
				player_turn_results.append({'targeting_cancelled': True})
			else:
				save_game(players, entities, game_map, message_log, game_state)

				return True

		# Toggle fullscreen
		if fullscreen:
			libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())

		# Print message results
		for player_turn_result in player_turn_results:
			message = player_turn_result.get('message')
			dead_entity = player_turn_result.get('dead')
			item_added = player_turn_result.get('item_added')
			item_consumed = player_turn_result.get('consumed')
			item_dropped = player_turn_result.get('item_dropped')
			equip = player_turn_result.get('equip')
			targeting = player_turn_result.get('targeting')
			targeting_cancelled = player_turn_result.get('targeting_cancelled')
			xp = player_turn_result.get('xp')

			if message:
				message_log.add_message(message)

			if dead_entity:
				if dead_entity == players[active_player]:
					message, game_state = kill_player(dead_entity)
				else:
					message = kill_monster(dead_entity)

				message_log.add_message(message)

			if item_added:
				entities.remove(item_added)

				# Change active player
				players[active_player].color = libtcod.blue
				players[(active_player+1)%constants['player_count']].color = libtcod.white
				active_player += 1
				if active_player >= constants['player_count']:
					active_player = 0
					game_state = GameStates.ENEMY_TURN

			if item_consumed:
				# Change active player
				players[active_player].color = libtcod.blue
				players[(active_player+1)%constants['player_count']].color = libtcod.white
				active_player += 1
				if active_player >= constants['player_count']:
					active_player = 0
					game_state = GameStates.ENEMY_TURN

			if item_dropped:
				entities.append(item_dropped)
				
				# Change active player
				players[active_player].color = libtcod.blue
				players[(active_player+1)%constants['player_count']].color = libtcod.white
				active_player += 1
				if active_player >= constants['player_count']:
					active_player = 0
					game_state = GameStates.ENEMY_TURN

			if equip:
				equip_results = players[active_player].equipment.toggle_equip(equip)

				for equip_result in equip_results:
					equipped = equip_result.get('equipped')
					dequipped = equip_result.get('dequipped')

					if equipped:
						message_log.add_message(Message('You equipped the {0}'.format(equipped.name)))

					if dequipped:
						message_log.add_message(Message('You dequipped the {0}'.format(dequipped.name)))

				# Change active player
				players[active_player].color = libtcod.blue
				players[(active_player+1)%constants['player_count']].color = libtcod.white
				active_player += 1
				if active_player >= constants['player_count']:
					active_player = 0
					game_state = GameStates.ENEMY_TURN

			if targeting:
				previous_game_state = GameStates.PLAYERS_TURN
				game_state = GameStates.TARGETING

				targeting_item = targeting

				message_log.add_message(targeting_item.item.targeting_message)

			if targeting_cancelled:
				game_state = previous_game_state

				message_log.add_message(Message('Targeting cancelled'))

			if xp:
				leveled_up = players[active_player].level.add_xp(xp)
				message_log.add_message(Message('You gain {0} experience point.'.format(xp)))

				if leveled_up:
					message_log.add_message(Message(
						'Your battle skills grow stronger! You reached level {0}'.format(
							players[active_player].level.current_level) + '!', libtcod.yellow))
					previous_game_state = game_state
					game_state = GameStates.LEVEL_UP

		# Enemy Movement
		if game_state == GameStates.ENEMY_TURN:
			for entity in entities:
				if entity.ai:
					enemy_turn_results = entity.ai.take_turn(players, fov_map, game_map, entities)

					for enemy_turn_result in enemy_turn_results:
						message = enemy_turn_result.get('message')
						dead_entity = enemy_turn_result.get('dead')

						if message:
							message_log.add_message(message)

						if dead_entity:
							if dead_entity in players:
								message, game_state = kill_player(dead_entity)
							else:
								message = kill_monster(dead_entity)

							message_log.add_message(message)

							if game_state == GameStates.PLAYER_DEAD:
								break

					if game_state == GameStates.PLAYER_DEAD:
						break
			else:
				game_state = GameStates.PLAYERS_TURN


if __name__ == '__main__':
	main()