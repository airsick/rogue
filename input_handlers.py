import libtcodpy as libtcod


def handle_keys(key):
	# Movement keys
	if key.vk == libtcod.KEY_UP or key.vk == libtcod.KEY_KP8:
		return {'move': (0,-1)}
	elif key.vk == libtcod.KEY_DOWN or key.vk == libtcod.KEY_KP2:
		return {'move': (0, 1)}
	elif key.vk == libtcod.KEY_LEFT or key.vk == libtcod.KEY_KP4:
		return {'move': (-1,0)}
	elif key.vk == libtcod.KEY_RIGHT or key.vk == libtcod.KEY_KP6:
		return {'move': ( 1,0)}
	# Diagonals
	elif key.vk == libtcod.KEY_KP7:
		return {'move': (-1,-1)}
	elif key.vk == libtcod.KEY_KP9:
		return {'move': ( 1,-1)}
	elif key.vk == libtcod.KEY_KP1:
		return {'move': (-1, 1)}
	elif key.vk == libtcod.KEY_KP3:
		return {'move': ( 1, 1)}

	# Alt Enter toggles full screen
	if key.vk == libtcod.KEY_ENTER and key.lalt:
		return {'fullscreen': True}

	# Exit on escape
	elif key.vk == libtcod.KEY_ESCAPE:
		return {'exit': True}

	# No key was pressed
	return {}