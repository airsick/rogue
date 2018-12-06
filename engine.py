import libtcodpy as libtcod

from input_handlers import handle_keys


def main():
	# Screen size
	screen_width = 80
	screen_height = 50

	# Player position
	player_x = int(screen_width/2)
	player_y = int(screen_height/2)

	# Set font
	libtcod.console_set_custom_font('arial10x10.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
	# Create game window
	libtcod.console_init_root(screen_width, screen_height, 'Roguelike Bitches', False)

	# Create a console (Drawing Layer?)
	con = libtcod.console_new(screen_width, screen_height)

	# Holds keyboard and mouse input
	key = libtcod.Key()
	mouse = libtcod.Mouse()

	# Game loop
	while not libtcod.console_is_window_closed():
		# Input listener I guess
		libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS, key, mouse)

		# Sets @ color
		libtcod.console_set_default_foreground(con, libtcod.white)
		# Draws @ to screen at 1, 1
		libtcod.console_put_char(con, player_x, player_y, '@', libtcod.BKGND_NONE)
		libtcod.console_blit(con, 0, 0, screen_width, screen_height, 0, 0, 0)
		# Push changes to screen
		libtcod.console_flush()

		# Clear old position (Idk why its after console flush)
		libtcod.console_put_char(con, player_x, player_y, ' ', libtcod.BKGND_NONE)

		# Determine action
		action = handle_keys(key)

		# Process the action object
		move = action.get('move')
		exit = action.get('exit')
		fullscreen = action.get('fullscreen')

		# Movement
		if move:
			dx, dy = move
			player_x += dx
			player_y += dy

		# Exit on escape
		if exit:
			return True

		# Toggle fullscreen
		if fullscreen:
			libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())


if __name__ == '__main__':
	main()