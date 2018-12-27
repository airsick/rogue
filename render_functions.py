import libtcodpy as libtcod

from enum import Enum

from game_states import GameStates

from menus import inventory_menu, level_up_menu, character_screen


class RenderOrder(Enum):
	STAIRS = 1
	CORPSE = 2
	ITEM = 3
	ACTOR = 4

def get_names_under_mouse(mouse, entities, game_map, players):
	(x, y) = (mouse.cx, mouse.cy)

	names = [entity.name for entity in entities
			if entity.x == x and entity.y == y and any(libtcod.map_is_in_fov(player.vision.fov_map, entity.x, entity.y) for player in players)]
	names = ', '.join(names)
	if x < game_map.width and x >= 0 and y <game_map.height and y>= 0 and game_map.tiles[x][y].explored:
		if names != '':
			names += ', '
		names += game_map.tiles[x][y].name

	return names.capitalize()

def render_bar(panel, x, y, total_width, name, value, maximum, bar_color, back_color):
	bar_width = int(float(value) / maximum * total_width)

	libtcod.console_set_default_background(panel, back_color)
	libtcod.console_rect(panel, x + bar_width, y, total_width - bar_width, 1, False, libtcod.BKGND_SCREEN)

	libtcod.console_set_default_background(panel, bar_color)
	if bar_width > 0:
		libtcod.console_rect(panel, x, y, bar_width, 1, False, libtcod.BKGND_SCREEN)

	libtcod.console_set_default_foreground(panel, libtcod.white)
	libtcod.console_print_ex(panel, int(x + total_width / 2), y, libtcod.BKGND_NONE, libtcod.CENTER,
								'{0}: {1}/{2}'.format(name, value, maximum))

def render_all(con, panel, entities, players, active_player, game_map, fov_recompute, message_log, screen_width, screen_height, bar_width,
					panel_height, panel_y, mouse, colors, game_state):
	if fov_recompute:
		# Draw all the tiles in the game map
		for y in range(game_map.height):
			for x in range(game_map.width):
				visible = libtcod.map_is_in_fov(players[0].vision.fov_map, x, y)
				for player in players:
					visible |= libtcod.map_is_in_fov(player.vision.fov_map, x, y)
				wall = game_map.tiles[x][y].block_sight
				tile = game_map.tiles[x][y]

				# Use light colors if the tile is visible
				if visible:
					# Draw the char if it exists
					if tile.char:
						libtcod.console_set_default_foreground(con, tile.light_color)
						libtcod.console_put_char(con, x, y, tile.char, libtcod.BKGND_NONE)
					# Otherwise change the background color
					else:
						libtcod.console_set_char_background(con, x, y, tile.light_color, libtcod.BKGND_SET)
					
					tile.explored = True
				# And dark colors otherwise
				#else: #fully explored for debug
				elif tile.explored:
					# Draw the char if it exists
					if tile.char:
						libtcod.console_set_default_foreground(con, tile.dark_color)
						libtcod.console_put_char(con, x, y, tile.char, libtcod.BKGND_NONE)
					# Otherwise change the background color
					else:
						libtcod.console_set_char_background(con, x, y, tile.dark_color, libtcod.BKGND_SET)
					
	# Draw all entities in the list
	entities_in_render_order = sorted(entities, key=lambda x: x.render_order.value)

	for entity in entities_in_render_order:
		for player in players:
			draw_entity(con, entity, player.vision.fov_map, game_map)

	
	libtcod.console_blit(con, 0, 0, screen_width, screen_height, 0, 0, 0)

	# Render bars
	libtcod.console_set_default_background(panel, libtcod.black)
	libtcod.console_clear(panel)

	# Print the game messages, one line at a time
	y = 1
	for message in message_log.messages:
		libtcod.console_set_default_foreground(panel, message.color)
		libtcod.console_print_ex(panel, message_log.x, y, libtcod.BKGND_NONE, libtcod.LEFT, message.text)
		y +=1

	# Render HP and dungeon level
	for i in range(len(players)):
		render_bar(panel, 2, i+2, bar_width-1, 'HP', players[i].fighter.hp, players[i].fighter.max_hp,
				libtcod.red, libtcod.darker_red)
	# Print > next to active player
	libtcod.console_print_ex(panel, 1, active_player + 2, libtcod.BKGND_NONE, libtcod.LEFT, '>')
	libtcod.console_print_ex(panel, 1, 1, libtcod.BKGND_NONE, libtcod.LEFT,
							'Dungeon level: {0}'.format(game_map.dungeon_level))

	libtcod.console_set_default_foreground(panel, libtcod.light_gray)
	libtcod.console_print_ex(panel, 1, 0, libtcod.BKGND_NONE, libtcod.LEFT,
							get_names_under_mouse(mouse, entities, game_map, players))

	libtcod.console_blit(panel, 0, 0, screen_width, panel_height, 0, 0, panel_y)

	if game_state in (GameStates.SHOW_INVENTORY, GameStates.DROP_INVENTORY):
		if game_state == GameStates.SHOW_INVENTORY:
			inventory_title = 'Press the key next to an item to use it, or Esc to cancel.\n'
		else:
			inventory_title = 'Press the key next to an item to drop it, or Esc to cancel.\n'
		
		inventory_menu(con, inventory_title, players[active_player], 50, screen_width, screen_height)

	elif game_state == GameStates.LEVEL_UP:
		level_up_menu(con, 'Level up! Choose a stat to raise:', players[active_player], 40, screen_width, screen_height)

	elif game_state == GameStates.CHARACTER_SCREEN:
		character_screen(players[active_player], 30, 10, screen_width, screen_height)

def clear_all(con, entities, game_map):
	for entity in entities:
		clear_entity(con, entity, game_map)


def draw_entity(con, entity, fov_map, game_map):
	if libtcod.map_is_in_fov(fov_map, entity.x, entity.y) or (entity.stairs and game_map.tiles[entity.x][entity.y].explored):
		libtcod.console_set_default_foreground(con, entity.color)
		libtcod.console_put_char(con, entity.x, entity.y, entity.char, libtcod.BKGND_NONE)

# Erase the character that represents this object
def clear_entity(con, entity, game_map):
	if game_map.tiles[entity.x][entity.y].explored:
		libtcod.console_set_default_foreground(con, game_map.tiles[entity.x][entity.y].dark_color)
		char = ' '
		if game_map.tiles[entity.x][entity.y].char:
			char = game_map.tiles[entity.x][entity.y].char
			libtcod.console_put_char(con, entity.x, entity.y, char, libtcod.BKGND_NONE)