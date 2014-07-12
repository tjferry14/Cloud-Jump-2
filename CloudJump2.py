import console, Image, ImageDraw, math, numpy, os, pickle, random, scene, sound, threading, time

DEAD_ZONE =  0.02
DIFFICULTY_Q = 100000.0
ENEMY_DENSITY = 0.2
GAME_CHARACTER = 'Boy'
GAME_FONT = 'AppleSDGothicNeo-Bold' # easier to change font later
GAME_GRAVITY = 2000
GAME_WAITING, GAME_PLAYING, GAME_DEAD = range(3)
IMAGE_WIDTH = 100
MAX_CLOUD_DIST = 505
PLAYER_BOUNCE_VELOCITY = 1700
PLAYER_CONTROL_SPEED = 2000
PLAYER_INITIAL_BOUNCE = 1700
USER_FILE = 'user.txt'

# === imported from HighScores.py ===

class HighScores(object):
    def __init__(self, in_file_name = 'highscores'):
        file_ext = '.pkl'
        self.file_name = in_file_name
        if not self.file_name.endswith(file_ext):
            self.file_name += file_ext
        self.high_scores = self.__load_scores()

    def __load_scores(self):  # private function
        try:
            with open(self.file_name, 'rb') as in_file:
                return pickle.load(in_file)
        except IOError:
            return {}

    def __save_scores(self):  # private function
        with open(self.file_name, 'wb') as out_file:
            pickle.dump(self.high_scores, out_file)

    def is_high_score(self, name, score):
        try:
            curr_high_score = self.high_scores.get(name, score-1)
        except TypeError:
            raise TypeError('The score arguement must be a number.')
        is_new_high_score = score > curr_high_score
        if is_new_high_score:
            self.high_scores[name] = score
            self.__save_scores()
        return is_new_high_score

# === end import from HighScores.py ===

def get_username(file_name = USER_FILE):
    player_name = None
    if os.path.isfile(file_name):
        with open(file_name) as f:
            for line in f.readlines():
                if line.istitle():
                    player_name = line
    if not player_name:
        player_name = console.input_alert('What is your name? ').title()
        if player_name:
            with open(file_name, 'w') as f:  
                f.write(player_name)
    return player_name or 'default'

player_name = get_username()
console.hud_alert('Player name: ' + player_name)

# to reduce latency, preload sound effects
#for s in 'Boing_1 Crashing Hit1 Hit2 Hit3 Hit4 Powerup_1'.split():
#    sound.load_effect(s)

def player_killed_sounds():
    for i in xrange(4):
        sound.play_effect('Hit_{}'.format(i+1))
        time.sleep(0.5)

def high_score_sounds():
    for i in xrange(4):
        sound.play_effect('Jump_{}'.format(i+1))
        time.sleep(0.3)

def run_in_thread(in_function):
    threading.Thread(None, in_function).start()

def tinted_text(s, x, y, tint_color = scene.Color(0, 0, 1)):
    scene.tint(0, 0, 0)
    scene.text(s, GAME_FONT, 48, x + 2, y - 2)
    scene.tint(*tint_color)
    scene.text(s, GAME_FONT, 48, x, y)

def shadow_text(s, x, y):
    tinted_text(s, x, y, scene.Color(0.0, 0.5, 1.0))

def score_text(s, x, y):
    tinted_text(s, x, y, scene.Color(1.0, 1.0, 0.4))

def pil_rect_to_scene_rect(pil_rect = (1, 2, 3 ,4)):
    if pil_rect:
        l, t, r, b = pil_rect
        return scene.Rect(l, t, r-l, b-t)
    else:
        return scene.Rect()

class Sprite(scene.Layer):
    def __init__(self, rect = scene.Rect(), parent = None, image_name = 'Boy'):
        super(Sprite, self).__init__(rect)
        if parent:
            parent.add_layer(self)
        self.image = image_name
        self.velocity = scene.Point(0, 0)

    def update(self, dt):  # make the clouds blow in the wind?
        super(Sprite, self).update(dt)
        self.frame.x += dt * self.velocity.x
        self.frame.y += dt * self.velocity.y

class Player(Sprite):
    def __init__(self, rect = scene.Rect(), parent = None):
        super(self.__class__, self).__init__(rect, parent, GAME_CHARACTER)

    def death_completion(self):
        self.superlayer.remove_layer(self)
        self.superlayer = None

    def die(self):
        run_in_thread(player_killed_sounds)
        self.animate('scale_x', 0.01)
        self.animate('scale_y', 0.01, completion=self.death_completion)
        #del self  # suicide is not an tenable option

class GrassBlock(Sprite):
    def __init__(self, rect = scene.Rect(), parent = None):
        super(self.__class__, self).__init__(rect, parent, 'PC_Grass_Block')

class Enemy(Sprite):
    def __init__(self, rect = scene.Rect(), parent = None):
        super(self.__class__, self).__init__(rect, parent, 'Alien_Monster')
        self.tint = scene.Color(1, 0, 1)

class Cloud(Sprite):
    def __init__(self, rect = scene.Rect(), parent = None):
        cloud_image = self.cloud_maker()
        new_rect = pil_rect_to_scene_rect(cloud_image.getbbox())
        rect.w, rect.h = new_rect.w, new_rect.h
        super(self.__class__, self).__init__(rect, parent, scene.load_pil_image(cloud_image))
        self.velocity.x = random.randint(-1, 4)  # give clouds a 2-in-6 chance to be moving
        if self.velocity.x > 1:
            self.velocity.x = 0
        self.velocity.x *= 50

    @classmethod
    def generate_shapes(cls, num_circles):
        shapes = []
        for i in xrange(num_circles):
            x = (i * 20 - ((num_circles/2)*30))+90
            y = ((random.random()-0.5) * 30)+15
            rad = random.randint(50, 100)
            shapes.append([x, y, rad])
        return shapes

    @classmethod
    def draw_cloud(cls, draw):
        num_circles = random.randint(5, 6)
        circles = cls.generate_shapes(num_circles)
        for i in circles:
            r = i[2]
            bbox = (i[0], 40-i[1], i[0]+r, 40-i[1]+r)
            draw.ellipse(bbox, fill='rgb(90%,90%,90%)')
        for i in circles:
            r = i[2]
            bbox = (i[0], 40-i[1]-10, i[0]+r, 40-i[1]+r-10)
            draw.ellipse(bbox, fill='white')

    # found on 'http://stackoverflow.com/questions/14211340/automatically-cropping-an-image-with-python-pil'
    @classmethod
    def crop_image(cls, img):
        image_data = numpy.asarray(img)
        image_data_bw = image_data.max(axis=2)
        non_empty_columns = numpy.where(image_data_bw.max(axis=0)>0)[0]
        non_empty_rows    = numpy.where(image_data_bw.max(axis=1)>0)[0]
        crop_box = (min(non_empty_rows),    max(non_empty_rows),
                    min(non_empty_columns), max(non_empty_columns))
        image_data_new = image_data[crop_box[0]:crop_box[1]+1,
                                    crop_box[2]:crop_box[3]+1, :]
        img = Image.fromarray(image_data_new)
        return img

    @classmethod
    def cloud_maker(cls):
        image_size = (220, 140)
        img = Image.new('RGBA', image_size)
        draw = ImageDraw.Draw(img)
        cls.draw_cloud(draw)
        del draw
        return cls.crop_image(img)

class MyScene(scene.Scene):
    def __init__(self):
        scene.run(self)

    def create_ground(self, max_blocks = 12):
        block_size_w = self.bounds.w / max_blocks
        block_size_h = block_size_w * 171 / 101  # image is 101 x 171 pixels
        for i in xrange(max_blocks):
            rect = scene.Rect(i * block_size_w, 0, block_size_w, block_size_h)
            GrassBlock(rect, self)
        return block_size_h * 0.7  # the new ground level

    def generate_clouds(self):
        y = self.cloud_height
        while self.cloud_height < self.bounds.h * 2:
            q = min(self.climb, DIFFICULTY_Q)
            min_dist = int(MAX_CLOUD_DIST * q / DIFFICULTY_Q)
            max_dist = int(MAX_CLOUD_DIST / 2 + min_dist / 2)
            self.cloud_height += random.randint(min_dist, max_dist)
            rect = scene.Rect(random.random() * (self.bounds.w - 150),
                              self.cloud_height, 0, 0)
            cloud = Cloud(rect, self)
            if random.random() < ENEMY_DENSITY:
                #generate new enemy
                rect = scene.Rect(0, 0, 64, 64)
                rect.center(cloud.frame.center())
                rect.y = cloud.frame.top() - 15
                enemy = Enemy(rect, self)
                enemy.velocity = cloud.velocity

    def cull_scenery(self):
        for sublayer in self.root_layer.sublayers:
            if sublayer.frame.top() < 0:
                sublayer.superlayer.remove_layer(sublayer)
                #self.root_layer.remove_layer(sublayer)
                del sublayer

    def control_player(self):
        tilt = scene.gravity().x
        if abs(tilt) > DEAD_ZONE:
            move = self.dt * tilt * PLAYER_CONTROL_SPEED
            self.player.frame.x += move
            self.player.frame.x = max(self.player.frame.x, 0)
            self.player.frame.x = min(self.player.frame.x,
                                      self.bounds.w - self.player.frame.w)

    def lower_scenery(self, y):
        self.climb += y
        self.cloud_height -= y
        for sublayer in self.root_layer.sublayers:
            if sublayer is not self.player:
                sublayer.frame.y -= y

    def end_game(self):
        self.game_state = GAME_DEAD
        self.player.velocity.y = 0
        self.player.die()
        del self.player
        self.player = None
        score = int(self.climb / 10)
        if self.high_scores.is_high_score(player_name, score):
            console.hud_alert('New high score!')
            run_in_thread(high_score_sounds)
            fmt = 'Congratulations {}:\nYou have a new high score!'
            self.high_score_msg = fmt.format(player_name)

    def run_gravity(self):
        player_y_move = self.dt * self.player.velocity.y
        scenery_y_move = 0
        old_velocity_y = self.player.velocity.y
        self.player.velocity.y -= self.dt * GAME_GRAVITY
        if old_velocity_y > 0 and self.player.velocity.y <= 0:
            self.player_apex_frame = True
        if self.player.frame.y >= self.player_max_y :
            scenery_y_move = self.player.frame.y - self.player_max_y
            self.player.frame.y = self.player_max_y
            self.lower_scenery(scenery_y_move)
        elif self.player.frame.center().y < 0:
            self.player.frame.y = 0
            sound.play_effect('Crashing')
            self.end_game()

    def collision_detect(self):
        bounce = False
        if self.player.velocity.y < 0:
            p = self.player.frame.center()
            for sublayer in self.root_layer.sublayers:
                if self.player.frame.center() in sublayer.frame:
                    if isinstance(sublayer, Enemy):
                        sound.play_effect('Powerup_1')
                        self.end_game()
                        return  # player killed by collision
                    elif isinstance(sublayer, Cloud):
                        bounce = True
        if bounce:
            self.player.velocity.y = PLAYER_BOUNCE_VELOCITY
            sound.play_effect('Boing_1')

    def game_loop(self):
        if self.game_state == GAME_PLAYING:
            self.run_gravity()
            if not self.player:
                return  # player killed by gravity
            self.collision_detect()
            if not self.player:
                return  # player killed by collision
            self.control_player()
            if self.player_apex_frame:
                self.cull_scenery()
                self.generate_clouds()
                self.player_apex_frame = False

    def draw_text(self):
        x = self.bounds.center().x
        score = int(self.climb / 10)
        score_as_text = 'Score: {}'.format(score)
        if self.game_state == GAME_PLAYING:
            shadow_text(score_as_text, x, self.bounds.h * 0.95)
        elif self.game_state == GAME_DEAD:
            shadow_text(score_as_text, x, self.bounds.h * 0.95)
            if self.high_score_msg:
                #print(self.high_score_msg)
                #print(score_text)
                score_text(self.high_score_msg, x, self.bounds.h * 0.78)
            shadow_text('Game Over', x, self.bounds.h * 0.6)
            shadow_text('Tap to Play Again', x, self.bounds.h * 0.4)
        elif self.game_state == GAME_WAITING:
            shadow_text('Tap Screen to Start',  x, self.bounds.h * 0.6)
            shadow_text('Tilt Screen to Steer', x, self.bounds.h * 0.4)

    def setup(self):
        self.climb = 0
        self.cloud_height = 200
        self.game_state = GAME_WAITING
        self.high_scores = HighScores('CloudJump2 high scores')
        self.high_score_msg = None
        ground_level = self.create_ground(12)
        self.generate_clouds()
        
        rect = scene.Rect(0, 0, IMAGE_WIDTH, IMAGE_WIDTH)
        rect.center(self.bounds.center())
        rect.y = ground_level
        self.player = Player(rect, self)
        self.player_apex_frame = False
        self.player_max_y = self.bounds.h * 0.6

    def draw(self):
        self.game_loop()
        scene.background(0.40, 0.80, 1.00)
        self.root_layer.update(self.dt)
        self.root_layer.draw()
        self.draw_text()

    def touch_began(self, touch):
        if self.game_state == GAME_WAITING:
            self.game_state = GAME_PLAYING
            self.player.velocity.y = PLAYER_INITIAL_BOUNCE
        elif self.game_state == GAME_DEAD:
            self.setup()

MyScene()
