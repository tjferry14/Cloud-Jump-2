import scene, sound

MENU_FONT = 'AvenirNext-Heavy'
BUTTON_FONT = 'Arial-BoldMT'
player_name = 'TJ'
game_character = 'Boy'

class Start (scene.Scene):
	def draw(self):
		portrait = self.size.h > self.size.w
		scene.background(0.40, 0.80, 1.00) # light blue background color

		scene.fill(1.00, 1.00, 1.00) # button fill color
		if portrait:
			self.play_btn_ellipse = scene.ellipse(140, 600, 100, 100)
			self.char_btn_ellipse = scene.ellipse(260, 600, 100, 100)
			self.name_btn_ellipse = scene.ellipse(380, 600, 100, 100)
			self.leaderboard_btn_ellipse = scene.ellipse(500, 600, 100, 100)
		else:
			self.play_btn_ellipse = scene.ellipse(280, 358, 100, 100)
			self.char_btn_ellipse = scene.ellipse(400, 358, 100, 100)
			self.name_btn_ellipse = scene.ellipse(520, 358, 100, 100)
			self.leaderboard_btn_ellipse = scene.ellipse(640, 358, 100, 100)
			
		#scene.ellipse(*self.play_btn_ellipse)
		#scene.ellipse(*self.char_btn_ellipse)

		scene.tint(1.00, 1.00, 1.00) # white text color
		fs, x, y = (100, 385, 850) if portrait else (150, 525, 600)
		scene.text('Cloud Jump 2', MENU_FONT, font_size=fs, x=x, y=y)
		
		x, y = (165, 615) if portrait else (305, 375)
		scene.image('ionicons-ios7-play-32', x, y)
		x, y = (280, 615) if portrait else (420, 375)
		scene.image('ionicons-person-32', x, y)
		x, y = (400, 615) if portrait else (538, 375)
		scene.image('ionicons-ios7-compose-outline-32', x, y)
		x, y = (520, 615) if portrait else (659, 375)
		scene.image('ionicons-earth-32', x, y)
		
		fs =  30
		if portrait:
			x, y = self.bounds.w / 2.0, self.bounds.h / 1.34
		else:
			x, y = self.bounds.w / 2.0, self.bounds.h / 1.45
		s = 'Welcome {}!'.format(player_name)
		scene.text(s, MENU_FONT, font_size=fs, x=x, y=y)

		for i in xrange(11):
			scene.image('PC_Grass_Block', self.bounds.w / 11 * i, 0)

	def touch_ended(self, touch):
		if touch.location in self.play_btn_ellipse:
			main_scene.switch_scene('#Game Scene Here')
		elif touch.location in self.char_btn_ellipse:
			main_scene.switch_scene(CharacterSelect1)

class CharacterSelect1(scene.Scene):
	def setup(self):
		portrait = self.size.h > self.size.w
		if portrait:
			self.p1_rect = scene.Rect(80, 735, 250, 250)
			self.p2_rect = scene.Rect(400, 735, 250, 250)
			self.p3_rect = scene.Rect(80, 395, 250, 250)
			self.p4_rect = scene.Rect(400, 395, 250, 250)
			self.p5_rect = scene.Rect(80, 80, 250, 250)
			self.p6_rect = scene.Rect(400, 80, 250, 250)
		else:
			self.p1_rect = scene.Rect(40, 400, 250, 250)
			self.p2_rect = scene.Rect(395, 400, 250, 250)
			self.p3_rect = scene.Rect(735, 400, 250, 250)
			self.p4_rect = scene.Rect(40, 80, 250, 250)
			self.p5_rect = scene.Rect(395, 80, 250, 250)
			self.p6_rect = scene.Rect(735, 80, 250, 250)

	def draw(self):
		scene.background(0.40, 0.80, 1.00)

		scene.image('Boy', *self.p1_rect)
		scene.image('Girl', *self.p2_rect)
		scene.image('Guardsman', *self.p3_rect)
		scene.image('Hamster_Face', *self.p4_rect)
		scene.image('Mouse_Face', *self.p5_rect)
		scene.image('Man', *self.p6_rect)

	def touch_ended(self, touch):
		global game_character;
		if touch.location in self.p1_rect:
			game_character = 'Boy'
			sound.play_effect('Ding_3')
			main_scene.switch_scene('#Game Scene Here')
		elif touch.location in self.p2_rect:
			game_character = 'Girl'
			sound.play_effect('Ding_3')
			main_scene.switch_scene('#Game Scene Here')
		elif touch.location in self.p3_rect:
			game_character = 'Guardsman'
			sound.play_effect('Ding_3')
			main_scene.switch_scene('#Game Scene Here')
		elif touch.location in self.p4_rect:
			game_character = 'Hamster_Face'
			sound.play_effect('Ding_3')
			main_scene.switch_scene('#Game Scene Here')
		elif touch.location in self.p5_rect:
			game_character = 'Mouse_Face'
			sound.play_effect('Ding_3')
			main_scene.switch_scene('#Game Scene Here')
		elif touch.location in self.p6_rect:
			game_character = 'Man'
			sound.play_effect('Ding_3')
			main_scene.switch_scene('#Game Scene Here')

class MultiScene (scene.Scene):
	def __init__(self, start_scene):
		self.active_scene = start_scene()
		scene.run(self)

	def switch_scene(self, new_scene):
		self.active_scene = new_scene()
		self.setup()

	def setup(self):
		global screen_size
		screen_size = self.size
		self.active_scene.add_layer = self.add_layer
		self.active_scene.size = self.size
		self.active_scene.bounds = self.bounds
		self.active_scene.root_layer = self.root_layer
		self.active_scene.setup()

	def draw(self):
		self.active_scene.touches = self.touches
		self.active_scene.t = self.t
		self.active_scene.dt = self.dt
		self.active_scene.draw()

	def touch_began(self, touch):
		self.active_scene.touch_began(touch)

	def touch_moved(self, touch):
		self.active_scene.touch_moved(touch)

	def touch_ended(self, touch):
		self.active_scene.touch_ended(touch)

main_scene = MultiScene(Start)
