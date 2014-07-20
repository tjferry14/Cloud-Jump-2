# Etude on Player Death - http://en.m.wikipedia.org/wiki/etude
# The player needs to die with more panache to give our game an
# arcade feel.  We could use your help on the sounds around the
# Player.die() method.  Better noises would be super cool. Thanks!

urls = [ 'http://powstudios.com/system/files/smokes.zip',
         'https://dl.dropboxusercontent.com/u/25234596/Exp_type_C.png' ]

import cStringIO, Image, os.path, requests, scene, sound, threading, time, zipfile

def get_remote_resources(in_urls = urls):
    def url_to_local_file(in_url, in_file_name):
        print('Downloading: {} --> {}'.format(in_url, in_file_name))
        with open(in_file_name, 'w') as out_file:
            out_file.write(requests.get(in_url).content)

    for url in in_urls:
        file_name = url.rpartition('/')[2] or url
        if not os.path.isfile(file_name):
            url_to_local_file(url, file_name)
    
get_remote_resources()

def slice_image_into_tiles(in_image, img_count_h, img_count_v = 1):
    w, h = in_image.size  # get the size of the big image
    w /= img_count_h      # calculate the size of smaller images
    h /= img_count_v
    return [scene.load_pil_image(in_image.crop((x*w, y*h, (x+1)*w, (y+1)*h)))
                for y in xrange(img_count_v) for x in xrange(img_count_h)]

def get_images_from_zip_file(file_name, directory, starts_with):
        with open(file_name) as in_file:
            starts_with = directory + '/' + starts_with
            zip_file = zipfile.ZipFile(in_file)
            return [scene.load_pil_image(Image.open(cStringIO.StringIO(zip_file.open(name).read())))
                    for name in zip_file.namelist() if name.startswith(starts_with)]

def tinted_text(s, x, y, tint_color = scene.Color(0, 0, 1)):
    font_name = 'AppleSDGothicNeo-Bold'
    scene.tint(0, 0, 0)
    scene.text(s, font_name, 48, x + 2, y - 2)
    scene.tint(*tint_color)
    scene.text(s, font_name, 48, x, y)

def shadow_text(s, x, y):
    tinted_text(s, x, y, scene.Color(0.0, 0.5, 1.0))

def player_killed_sounds():
    for i in xrange(4):
        sound.play_effect('Hit_{}'.format(i+1))
        time.sleep(0.5)

def run_in_thread(in_function):
    threading.Thread(None, in_function).start()

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

class AnimatedSprite(Sprite):
    def __init__(self, rect, parent, in_images, in_frames_per_image, **kwargs):
        super(self.__class__, self).__init__(rect, parent, in_images[0])
        assert in_images and isinstance(in_images, list)
        self.images = in_images
        self.frames_per_image = in_frames_per_image
        self.max_frames = len(in_images) * in_frames_per_image
        self.frame_count = 0
        self.looped = False
        self.is_done = True
        self.configure(**kwargs)

    def configure(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    def update(self, dt):
        super(AnimatedSprite, self).update(dt)
        if self.is_done:
            self.image = None 
            return
        self.image = self.images[int(self.frame_count / self.frames_per_image)]
        self.frame_count += 1
        if self.frame_count >= self.max_frames:
            if self.looped:
                self.frame_count %= self.max_frames
            else:
                self.is_done = True

class Player(Sprite):
    def __init__(self, rect = scene.Rect(), parent = None):
        super(self.__class__, self).__init__(rect, parent, 'Boy')

    def death_completion(self):
        self.superlayer.remove_layer(self)
        self.superlayer = None

    def die(self):
        run_in_thread(player_killed_sounds)
        self.animate('scale_x', 0.01)
        self.animate('scale_y', 0.01, completion=self.death_completion)
        #del self  # suicide is not an tenable option
        
class MyScene(scene.Scene):
    def __init__(self):
        scene.run(self)

    def end_game(self):
        self.smoke.frame.center(self.player.frame.center())
        self.smoke.configure(frame_count=0, is_done=False)
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
        rect = scene.Rect(0, 0, 200, 200)
        wimpy_smoke = True 
        if wimpy_smoke:
            images = get_images_from_zip_file('smokes.zip', 'smoke puff up', 'smoke_puff')
            frames_per_image = 8
        else:  # awesome smoke
            images = slice_image_into_tiles(Image.open('Exp_type_C.png'), 48)
            frames_per_image = 2
        self.smoke = AnimatedSprite(rect, self, images, frames_per_image)

        rect = scene.Rect(0, 0, 90, 100)
        rect.center(self.bounds.center())
        rect.y += 80
        self.player = Player(rect, self)

    def draw(self):
        scene.background(0.40, 0.80, 1.00)
        self.root_layer.update(self.dt)
        self.root_layer.draw()
        self.draw_text()

    def touch_began(self, touch):
        if self.player:
            self.end_game()
        else:
            self.setup()

MyScene()
