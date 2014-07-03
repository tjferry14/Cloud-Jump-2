import scene

class Start (scene.Scene):
	def draw(self):
		center = self.bounds.center()
		portrait = self.size.h > self.size.w
		landscape = self.size.w > self.size.h
		scene.background(0.40, 0.80, 1.00) # light blue background color
 
		scene.fill(0.50, 1.00, 0.00) # play button fill color
 
		if landscape: # play button landscape
			self.playpx, self.playpy = (20, 350)
			self.playsx, self.playsy = (358, 100)
			scene.rect(self.playpx, self.playpy, self.playsx, self.playsy)
 
		if portrait: # play button portrait
			self.playpx, self.playpy = (200, 600)
			self.playsx, self.playsy = (358, 100)
			scene.rect(self.playpx, self.playpy, self.playsx, self.playsy)
 
		scene.fill(1.00, 1.00, 1.00) # character select fill color
 
		if landscape: # character select button landscape
			self.characpx, self.characpy = (20, 230)
			self.characsx, self.characsy = (485, 100)
			scene.rect(self.characpx, self.characpy, self.characsx, self.characsy)
 
		if portrait: # character select button portrait
			self.characpx, self.characpy = (140, 470)
			self.characsx, self.characsy = (485, 100)
			scene.rect(self.characpx, self.characpy, self.characsx, self.characsy)
 
		scene.tint(1.00, 1.00, 1.00)
		if landscape:
			scene.text('Cloud Jump', MENU_FONT, font_size=150.0, x=525.0, y=600.0)
		if portrait:
			scene.text('Cloud Jump', MENU_FONT, font_size=100.0, x=385.0, y=850.0)
 
		if landscape: # landscape
			scene.text('Play Game', BUTTON_FONT, font_size=65.0, x=200.0, y=400.0)
		if portrait: # portrait
			scene.text('Play Game', BUTTON_FONT, font_size=65.0, x=380.0, y=650.0)
 
		scene.tint(0.00, 0.50, 1.00)
		if landscape: # landscape
			scene.text('Character Select', BUTTON_FONT, font_size=54, x=260, y=285.0)
		if portrait: # portrait
			scene.text('Character Select', BUTTON_FONT, font_size=54, x=380.0, y=521)
 
		scene.tint(1.00, 1.00, 1.00)
		if landscape: # landscape
			scene.text('Welcome ' + player_name + '!', MENU_FONT, font_size=30.0, x=self.bounds.w / 1.4, y=self.bounds.h / 1.7)
		if portrait: # portrait
			scene.text('Welcome ' + player_name + '!', MENU_FONT, font_size=30.0, x=self.bounds.w / 2, y=self.bounds.h / 1.34)
 
		scene.image('PC_Grass_Block', self.bounds.x, self.bounds.y)
		scene.image('PC_Grass_Block', self.bounds.x + 100, self.bounds.y)
		scene.image('PC_Grass_Block', self.bounds.x + 200, self.bounds.y)
		scene.image('PC_Grass_Block', self.bounds.x + 300, self.bounds.y)
		scene.image('PC_Grass_Block', self.bounds.x + 400, self.bounds.y)
		scene.image('PC_Grass_Block', self.bounds.x + 500, self.bounds.y)
		scene.image('PC_Grass_Block', self.bounds.x + 600, self.bounds.y)
		scene.image('PC_Grass_Block', self.bounds.x + 700, self.bounds.y)
		scene.image('PC_Grass_Block', self.bounds.x + 800, self.bounds.y)
		scene.image('PC_Grass_Block', self.bounds.x + 900, self.bounds.y)
		scene.image('PC_Grass_Block', self.bounds.x + 1000, self.bounds.y)
 
	def check(self, x, y, posx, posy, sizex, sizey):
		if x >= posx and x <= posx + sizex:
			if y >= posy and y <= posy + sizey:
				return True
		return False
 
	def check_character(self, x, y):
		return self.check(x, y, self.characpx, self.characpy, self.characsx ,self.characsy)
 
	def check_play(self, x, y):
		return self.check(x, y, self.playpx, self.playpy, self.playsx ,self.playsy)
 
	def touch_ended(self, touch):
		x, y = touch.location
		if self.check_play(x, y): main_scene.switch_scene(#Game Scene Here)
		if self.check_character(x, y): main_scene.switch_scene(#Character Select Scene Here)
		else: pass
 
class MultiScene (scene.Scene):
	def __init__(self, start_scene):
		self.active_scene = start_scene()
 
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
scene.run(main_scene)