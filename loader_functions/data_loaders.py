import os

import shelve



def save_game(player, entities, game_map, message_log, game_state):
	with shelve.open('savegame', 'n') as data_file:
		data_file['player_index'] = entities.index(player)
		data_file['entities'] = entities
		data_file['game_map'] = game_map
		data_file['message_log'] = message_log
		data_file['game_state'] = game_state
	print('Game saved')

def load_game():
	#with open('savegame.dat','w+') as file:
	#	pass
	if not os.path.exists('savegame.dat'):
		print('Load Error')
		raise FileNotFoundError


	with shelve.open('savegame', 'r') as data_file:
		player_index = data_file['player_index']
		entities = data_file['entities']
		game_map = data_file['game_map']
		message_log = data_file['message_log']
		game_state = data_file['game_state']

	player = entities[player_index]

	print('Game loaded')

	return player, entities, game_map, message_log, game_state