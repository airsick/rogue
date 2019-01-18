import libtcodpy as libtcod

from map_objects.generator_functions import make_map, make_town
from map_objects.game_map import GameMap

from loader_functions.initialize_new_game import get_constants, get_players
from render_functions import render_map, render_entities, clear_all

class MapViewer:
	def __init__(self):
		self.constants = get_constants()
		self.generator_function = make_map

	def main(self):

		# Set font
		libtcod.console_set_custom_font('dejavu_wide16x16_gs_tc.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
		# Create game window
		libtcod.console_init_root(self.constants['screen_width'], self.constants['screen_height'], self.constants['window_title'], False)

		# Create a console (Drawing Layer?)
		con = libtcod.console_new(self.constants['screen_width'], self.constants['screen_height'])


		# Holds keyboard and mouse input
		key = libtcod.Key()
		mouse = libtcod.Mouse()

		entities = []
		players = get_players(self.constants, entities)

		game_map = GameMap(self.constants['map_width'], self.constants['map_height'])
		make_town(game_map, self.constants['max_rooms'], self.constants['room_min_size'], self.constants['room_max_size'], self.constants['map_width'], self.constants['map_height'], players, entities)

		render_map(con, players, game_map, self.constants['screen_width'], self.constants['screen_height'], all_visible=True)
		render_entities(con, entities, players, game_map, self.constants['screen_width'], self.constants['screen_height'], all_visible=True)
		libtcod.console_flush()

		# Render loop
		while not libtcod.console_is_window_closed():
			libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS | libtcod.EVENT_MOUSE, key, mouse)

			if mouse.lbutton_pressed:
				# Clear all entities except players
				game_map.dungeon_level += 1
				entities = entities[:self.constants['player_count']]
				make_town(game_map, self.constants['max_rooms'], self.constants['room_min_size'], self.constants['room_max_size'], self.constants['map_width'], self.constants['map_height'], players, entities)

				
				render_map(con, players, game_map, self.constants['screen_width'], self.constants['screen_height'], all_visible=True)
				render_entities(con, entities, players, game_map, self.constants['screen_width'], self.constants['screen_height'], all_visible=True)
				libtcod.console_flush()

			if key.vk == libtcod.KEY_ESCAPE:
				return True

if __name__ == '__main__':
	viewer = MapViewer()
	viewer.main()