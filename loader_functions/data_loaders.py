import os

import shelve



def save_game(players, entities, game_map, message_log, game_state, active_player):
	with shelve.open('savegame', 'n') as data_file:
		for i in range(len(players)):
			data_file['player{0}_index'.format(i)] = entities.index(players[i])
		data_file['entities'] = entities
		data_file['game_map'] = game_map
		data_file['message_log'] = message_log
		data_file['game_state'] = game_state
		data_file['active_player'] = active_player

def load_game(player_count):
	if not os.path.exists('savegame.dat'):
		raise FileNotFoundError

	players = []

	with shelve.open('savegame', 'r') as data_file:
		entities = data_file['entities']
		for i in range(player_count):
			player_index = data_file['player{0}_index'.format(i)]
			players.append(entities[player_index])
		game_map = data_file['game_map']
		message_log = data_file['message_log']
		game_state = data_file['game_state']
		active_player = data_file['active_player']

	return players, entities, game_map, message_log, game_state, active_player