# Etude on Player Death - http://en.m.wikipedia.org/wiki/etude
# The player needs to die with more panache to give our game an
# arcade feel.  We could use your help on both the sounds and the
# animations around the Player.die() method.  Better noises and
# a player that shrinks to almost nothing and then is replaced
# with a puff of smoke would be super cool. Thanks for playing!

import scene, sound, time, zipfile, urllib, cStringIO, Image

def tinted_text(s, x, y, tint_color = scene.Color(0, 0, 1)):
	font_name = 'AppleSDGothicNeo-Bold'
	scene.tint(0, 0, 0)
	scene.text(s, font_name, 48, x + 2, y - 2)
	scene.tint(*tint_color)
	scene.text(s, font_name, 48, x, y)

def shadow_text(s, x, y):
	tinted_text(s, x, y, scene.Color(0.0, 0.5, 1.0))
	
class AnimatedSprite (object):
	def __init__(self, images, frame, w=1, h=1, steps=3, **kwargs):
		self.w = w
		self.h = h
		self.frame = frame
		self.original_size = frame.w, frame.h
		if isinstance(images, list):
			self.tiles = [scene.load_pil_image(i) for i in images]
			self.original_size = images[0].size
		else: 
			self.tiles = [self.get_frame(images, x, y) for y in xrange(h) for x in xrange(w)]
		self.step = 0
		self.frame_count = 0
		self.steps = steps
		self.rotation = 0
		self.tint = scene.Color(1,1,1,1)
		self.looped = False
		self.is_done = False
		self.configure(**kwargs)

	def configure(self, **kwargs):
		for k, v in kwargs.items():
			setattr(self, k, v)
	
	@classmethod
	def get_images_from_zip(self, url, directory, starts_with):
		images = []
		zip_file = zipfile.ZipFile(cStringIO.StringIO(urllib.urlopen(url).read()))
		for name in zip_file.namelist():
			if name.startswith(directory+starts_with):
				images.append(Image.open(cStringIO.StringIO(zip_file.open(name).read())))
		return images
			
	@classmethod
	def white_to_transparent(self, img):
		pixdata = img.load()
		for y in xrange(img.size[1]):
			for x in xrange(img.size[0]):
				if pixdata[x, y] == (255, 255, 255, 255):
					pixdata[x, y] = (255, 255, 255, 0)

	def get_frame(self, img, x, y):
		w, h = img.size
		w = w/self.w
		h = h/self.h
		frame = img.crop((x*w, y*h, (x+1)*w, (y+1)*h))
		self.original_size = frame.size
		return scene.load_pil_image(frame)

	def set_original_size(self):
		self.frame.w, self.frame.h = self.original_size

	def draw(self):
		if not self.is_done:
			self.frame_count += 1
			scene.push_matrix()
			scene.translate(*self.frame.origin())
			scene.rotate(self.rotation)
			scene.tint(*self.tint)
			scene.image(self.tiles[self.step], 0, 0, *self.frame.size())
			scene.pop_matrix()
			if self.frame_count % self.steps == 0 and not self.is_done:
				self.step += 1
			if not self.looped:
				if self.step == len(self.tiles)-1:
					self.step = 0					
					self.is_done = True
			else:
				if self.step == len(self.tiles)-1:
					self.step = 0

class Sprite(scene.Layer):
	def __init__(self, rect = scene.Rect(), parent = None, image_name = 'Boy'):
		super(Sprite, self).__init__(rect)
		if parent:
			parent.add_layer(self)
		self.image = image_name
		self.velocity = scene.Point(0, 0)

	def update(self, dt):
		super(Sprite, self).update(dt)
		self.frame.x += dt * self.velocity.x
		self.frame.y += dt * self.velocity.y

class Player(Sprite):
	def __init__(self, rect = scene.Rect(), parent = None):
		super(self.__class__, self).__init__(rect, parent, 'Boy')

	def death_completion(self):
		self.superlayer.remove_layer(self)
		self.superlayer = None

	def die(self):
		self.animation_done = False
		self.animate('scale_x', 0.01, repeat=2)
		self.animate('scale_y', 0.01, repeat=2, completion=self.death_completion)
		for i in xrange(4):
			sound.play_effect('Hit_{}'.format(i+1))
			time.sleep(0.5)
		#while self.superlayer:
		#    time.sleep(1)
		#print('Done')
		#del self  # suicide is not an tenable option

class MyScene(scene.Scene):
	def __init__(self):
		scene.run(self)

	def end_game(self):
		self.smoke.frame.center(self.player.frame.center())
		self.smoke.configure(step=0, is_done=False)
		self.player.die()
		del self.player
		self.player = None

	def draw_text(self):
		x = self.bounds.center().x
		h = self.bounds.h
		msg = 'Tap to kill me...' if self.player else 'The player is dead!'
		shadow_text(msg, x, h * 0.80)
		msg = '''Issue #9: When killed, the player
		should fade out with animation...'''
		shadow_text(msg, x, h * 0.35)
		msg = '''It will give the game a more arcade-like feel
		if player death is a bit more like in PacMan.'''
		shadow_text(msg, x, h * 0.15)

	def setup(self):
		rect = scene.Rect(0, 0, 90, 100)
		rect.center(self.bounds.center())
		rect.y += 80
		self.player = Player(rect, self)
		
		images = AnimatedSprite.get_images_from_zip('http://powstudios.com/system/files/smokes.zip', 'smoke puff up/', 'smoke_puff')
		self.smoke = AnimatedSprite(images, scene.Rect(self.size.w/2, self.size.h/2, 200, 200), w=10)
		self.smoke.configure(steps=4, looped=False, is_done=True, tint=scene.Color(1,1,1,0.6))

#		img = Image.open(cStringIO.StringIO(urllib.urlopen('https://dl.dropboxusercontent.com/u/25234596/Exp_type_C.png').read()))
#		self.smoke = AnimatedSprite(img, scene.Rect(0, 0, 200, 200), w=48)
#		self.smoke.configure(steps=2, looped=False, is_done=True, tint=scene.Color(1,1,1,0.6))

	def draw(self):
		scene.background(0.40, 0.80, 1.00)
		self.root_layer.update(self.dt)
		self.root_layer.draw()
		self.smoke.draw()
		self.draw_text()

	def touch_began(self, touch):
		if self.player:
			self.end_game()
		else:
			self.setup()

MyScene()
