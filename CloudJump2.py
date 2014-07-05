import console, Image, ImageDraw, json, math, os, random, scene, sound, time

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
USER_FILE = 'user.json'

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

# to reduce latency, preload sound effects
for s in 'Boing_1 Crashing Powerup_1'.split():
    sound.load_effect(s)

def tinted_text(s, x, y, tint_color = scene.Color(0, 0, 1)):
    scene.tint(0, 0, 0)
    scene.text(s, GAME_FONT, 48, x + 2, y - 2)
    scene.tint(*tint_color)
    scene.text(s, GAME_FONT, 48, x, y)

def shadow_text(s, x, y):
    tinted_text(s, x, y, scene.Color(0.0, 0.5, 1.0))

def score_text(s, x, y):
    tinted_text(s, x, y, scene.Color(1.0, 1.0, 0.4))

def generate_shapes(num_circles):
    shapes = []
    for i in xrange(num_circles):
        x = (i * 20 - ((num_circles/2)*30))+90
        y = ((random.random()-0.5) * 30)+15
        rad = random.randint(50, 100)
        shapes.append([x, y, rad])
    return shapes

def draw_cloud(draw):
    num_circles = random.randint(5, 6)
    circles = generate_shapes(num_circles)
    for i in circles:
        r = i[2]
        bbox = (i[0], 40-i[1], i[0]+r, 40-i[1]+r)
        draw.ellipse(bbox, fill='rgb(90%,90%,90%)')
    for i in circles:
        r = i[2]
        bbox = (i[0], 40-i[1]-10, i[0]+r, 40-i[1]+r-10)
        draw.ellipse(bbox, fill='white')

def cloud_maker():
    image_size = (220, 140)
    theImage = Image.new('RGBA', image_size) #, 'pink')
    draw = ImageDraw.Draw(theImage)
    draw_cloud(draw)
    del draw
    return theImage

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

class Player(Sprite):
    def __init__(self, rect = scene.Rect(), parent = None):
        super(self.__class__, self).__init__(rect, parent, GAME_CHARACTER)
        self.velocity = 0

class GrassBlock(Sprite):
    def __init__(self, rect = scene.Rect(), parent = None):
        super(self.__class__, self).__init__(rect, parent, 'PC_Grass_Block')

class Enemy(Sprite):
    def __init__(self, rect = scene.Rect(), parent = None):
        super(self.__class__, self).__init__(rect, parent, 'Alien_Monster')
        self.tint = scene.Color(1, 0, 1)

class Cloud(Sprite):
    def __init__(self, rect = scene.Rect(), parent = None):
        cloud_image = cloud_maker()
        rect = pil_rect_to_scene_rect(cloud_image.getbbox())
        rect.x = rect.y = 0
        super(self.__class__, self).__init__(rect, parent, scene.load_pil_image(cloud_image))
        #self.background = scene.Color(1, 0, 1)  # show cloud rect problem

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
            cloud = Cloud(None, self)
            cloud.frame.x = random.random() * (self.bounds.w - 150)
            cloud.frame.y = self.cloud_height
            if random.random() < ENEMY_DENSITY:
                #generate new enemy
                rect = scene.Rect(0, 0, 64, 64)
                rect.center(cloud.frame.center())
                rect.y = cloud.frame.top() - 8
                #rect.y += 40
                Enemy(rect, self)

    def cull_scenery(self):
        for sublayer in self.root_layer.sublayers:
            if sublayer.frame.top() < 0:
                self.root_layer.remove_layer(sublayer)
                del sublayer

    def control_player(self):
        tilt = scene.gravity().x
        if abs(tilt) > DEAD_ZONE:
            move = self.dt * tilt * PLAYER_CONTROL_SPEED
            self.player.frame.x += move
            x = self.player.frame.x
            self.player.frame.x = max(x, 0)
            self.player.frame.x = min(x, self.bounds.w - self.player.frame.w)

    def lower_scenery(self, y):
        self.climb += y
        self.cloud_height -= y
        for sublayer in self.root_layer.sublayers:
            if sublayer is not self.player:
                sublayer.frame.y -= y

    def end_game(self):
        self.game_state = GAME_DEAD
        for sublayer in self.root_layer.sublayers:
            sublayer.frame.y = -500
        self.generate_clouds()

    def run_gravity(self):
        global enemy_frame
        player_y_move = self.dt * self.player.velocity
        scenery_y_move = 0
        old_velocity = self.player.velocity
        self.player.velocity -= self.dt * GAME_GRAVITY
        if old_velocity > 0 and self.player.velocity <= 0:
            self.player_apex_frame = True
        self.player.frame.y += player_y_move
        if self.player.frame.y >= self.player_max_y :
            scenery_y_move = self.player.frame.y - self.player_max_y
            self.player.frame.y = self.player_max_y
            self.lower_scenery(scenery_y_move)
        elif self.player.frame.top() < 0:
            sound.play_effect('Crashing')
            self.end_game()

    def collision_detect(self):
        bounce = False
        if self.player.velocity < 0:
            p = scene.Point(self.player.frame.center().x, self.player.frame.y - 10)
            for sublayer in self.root_layer.sublayers:
                if (isinstance(sublayer, Enemy)
                and self.player.frame.intersects(sublayer.frame)):
                    sound.play_effect('Powerup_1')
                    self.end_game()
                    return True  # player was killed
                elif isinstance(sublayer, Cloud) and p in sublayer.frame:
                    bounce = True
        if bounce:
            self.player.velocity = PLAYER_BOUNCE_VELOCITY
            sound.play_effect('Boing_1')
        return False  # player was not killed

    def game_loop(self):
        if self.game_state == GAME_PLAYING:
            self.run_gravity()
            self.collision_detect()
            self.control_player()
            if self.player_apex_frame:
                self.cull_scenery()
                self.generate_clouds()
                self.player_apex_frame = False

    def high_score(self, name, score):
        file_name = 'highscores.json'
        high_scores = {}

        try:
            with open(file_name) as in_file:
                high_scores = json.load(in_file)
        except IOError:
            pass

        curr_high_score = high_scores.get(name, score - 1)
        if score >= curr_high_score:
            high_scores[name] = score
            score_text('NEW HIGH SCORE!', self.bounds.w / 2, self.bounds.h * 0.75)
            with open(file_name, 'w') as out_file:
                json.dump(high_scores, out_file)
            for i in xrange(3):
                sound.play_effect('Hit_3')
                time.sleep(0.3)

    def draw_text(self):
        x = self.bounds.center().x
        score = int(self.climb / 10)
        score_text = 'Score: {}'.format(score)
        if self.game_state == GAME_PLAYING:
            shadow_text(score_text, x, self.bounds.h * 0.95)
        elif self.game_state == GAME_DEAD:
            shadow_text(score_text, x, self.bounds.h * 0.95)
            shadow_text('Game Over', x, self.bounds.h * 0.6)
            shadow_text('Tap to Play Again', x, self.bounds.h * 0.4)
            self.high_score(player_name, score)
        elif self.game_state == GAME_WAITING:
            shadow_text('Tap Screen to Start',  x, self.bounds.h * 0.6)
            shadow_text('Tilt Screen to Steer', x, self.bounds.h * 0.4)

    def setup(self):
        self.game_state = GAME_WAITING
        self.climb = 0
        ground_level = self.create_ground(12)
        self.cloud_height = 200
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
            self.player.velocity = PLAYER_INITIAL_BOUNCE
        elif self.game_state == GAME_DEAD:
            self.setup()

MyScene()
