import console, json, math, os, random, scene, sound

IMAGE_WIDTH = 101
IMAGE_HEIGHT = 171
IMAGE_Y_OFFSET = -30
#BLOCK_HEIGHT = 40
#BLOCK_DEPTH = 80
DEAD_ZONE =  0.02
PLAYER_CONTROL_SPEED = 2000
PLAYER_BOUNCE_VELOCITY = 1700
PLAYER_INITIAL_BOUNCE = 1700
MAX_CLOUD_DIST = 505
DIFFICULTY_Q = 100000.0
GAME_GRAVITY = 2000
GAME_WAITING, GAME_PLAYING, GAME_DEAD = range(3)
ENEMY_DENSITY = 0.2
GAME_FONT = 'AppleSDGothicNeo-Bold' # easier to change font later
NAME_FILE = "names.json"

if os.path.isfile(NAME_FILE): # if there is a file with names...
    text_file = open(NAME_FILE) # only open it in normal mode
else: # if not...
    text_file = open(NAME_FILE, "w+") # make one

if os.stat(NAME_FILE).st_size > 0:
    for line in text_file:
        if line.istitle():
            player_name = line
        else:
            player_name = console.input_alert('What is your name? ').title()
            text_file = open(NAME_FILE, "w")
            text_file.write(player_name)
            text_file.close()
else:
    player_name = console.input_alert('What is your name? ').title()
    text_file = open(NAME_FILE, "w")
    text_file.write(player_name)
    text_file.close()

# to reduce latency, preload sound effects
for s in 'Boing_1 Crashing Powerup_1'.split():
    sound.load_effect(s)

def tinted_text(s, x, y, tint_color = scene.Color(0, 0, 1)):
    scene.tint(0, 0, 0)
    scene.text(s, 'AppleSDGothicNeo-Bold', 48, x + 2, y - 2)
    scene.tint(*tint_color)
    scene.text(s, 'AppleSDGothicNeo-Bold', 48, x, y)

def shadow_text(s, x, y):
    tinted_text(s, x, y, scene.Color(0.0, 0.5, 1.0))

def score_text(s, x, y):
    tinted_text(s, x, y, scene.Color(1.0, 1.0, 0.4))

class Sprite(scene.Layer):
    def __init__(self, rect = scene.Rect(), parent = None, image_name = 'PC_Grass_Block'):
        super(Sprite, self).__init__(rect)
        if parent:
            parent.add_layer(self)
        self.image = image_name

class Player(object):
    def __init__(self):
        self.frame = scene.Rect()
        self.velocity = 0

    def draw(self):
        scene.tint(1,1,1)
        scene.image('Boy', self.frame.x, self.frame.y + IMAGE_Y_OFFSET)

class GrassBlock(Sprite):
    def __init__(self, rect = scene.Rect(), parent = None):
        super(self.__class__, self).__init__(rect, parent, 'PC_Grass_Block')

class Cloud(object):
    def __init__(self):
        self.shapes = []

        num_circles = random.randint(4, 5)
        for i in xrange(num_circles):
            x = i * 20 - ((num_circles/2)*30)
            y = (random.random()-0.5) * 30
            rad = random.randint(50, 100)
            self.shapes.append([x, y, rad])

        self.width = num_circles * 30 + 30
        self.frame = scene.Rect(0, 0, self.width, 60)

    def is_colliding(self, pos):
        startp = self.frame.x - self.width/2
        endp   = self.frame.x + self.width/2
        return (startp < pos.x < endp
        and self.frame.y + 10 < pos.y < self.frame.y + 30)

    def draw(self):
        scene.push_matrix()
        scene.translate(self.frame.x, self.frame.y)
        scene.no_stroke()
        scene.fill(0.90, 0.90, 0.90)
        for i in self.shapes:
            scene.ellipse(i[0], i[1] - 5, i[2], i[2])

        scene.fill(1.00, 1.00, 1.00)
        for i in self.shapes:
            scene.ellipse(i[0], i[1] + 5, i[2], i[2])
        scene.pop_matrix()

class Enemy(object):
    def __init__(self, start_cloud):
        self.scene = scene
        self.hit = False
        self.x = self.initial_x = start_cloud.frame.x
        self.y = start_cloud.frame.center().y
        self.removed = False
        self.dead = False
        self.size = 64
        self.color = scene.Color(1, 0, 1)
        self.speed = 0     #1.0 / self.size * 100
        self.amp = 0   #    random() * 300

    def update(self, dt):
        self.y -= self.speed
        self.x = self.initial_x +  math.sin(self.y / 100) * self.amp
        self.amp = max(self.amp * 0.99, 0)

        if self.y < -64:
            self.removed = True
        else:
            pass

    def draw(self):
        scene.tint(self.color.r, self.color.g, self.color.b, 1.0)
        scene.image('Alien_Monster', self.x - self.size/2,
        self.y - self.size/2,
        self.size, self.size)
        scene.tint(1, 1, 1)

        global enemy_frame
        s = self.size
        enemy_frame = scene.Rect(self.x - s/2 * 0.9,
        self.y - s/2 * 0.8,
        s * 0.9, s * 0.8)

class MyScene(scene.Scene):
    def __init__(self):
        scene.run(self)

    def create_ground(self, max_blocks = 12):
        block_size = self.bounds.w / max_blocks
        for i in xrange(max_blocks):
            rect = scene.Rect(i * block_size, 0, block_size, block_size)
            self.scenery.append(GrassBlock(rect, self))
        return block_size  # the new ground level

    def generate_clouds(self):
        y = self.cloud_height
        while self.cloud_height < self.bounds.h * 2:
            q = min(self.climb, DIFFICULTY_Q)
            min_dist = int(MAX_CLOUD_DIST * q / DIFFICULTY_Q)
            max_dist = int(MAX_CLOUD_DIST / 2 + min_dist / 2)
            self.cloud_height += random.randint(min_dist, max_dist)
            cloud = Cloud()
            cloud.frame.x = random.random() * (self.bounds.w - 150)
            cloud.frame.y = self.cloud_height
            self.scenery.append(cloud)
            if random.random() < ENEMY_DENSITY:
                #generate new enemy
                self.enemies.append(Enemy(cloud))

    def cull_scenery(self):
        for sprite in self.scenery:
            if sprite.frame.top() < 0:
                self.scenery.remove(sprite)

    def control_player(self):
        tilt = scene.gravity().x
        if abs(tilt) > DEAD_ZONE:
            move = self.dt * tilt * PLAYER_CONTROL_SPEED
            self.player.frame.x += move
            if self.player.frame.x < 0:
                self.player.frame.x = 0
            elif self.player.frame.x > self.bounds.w - self.player.frame.w:
                self.player.frame.x = self.bounds.w - self.player.frame.w

    def lower_scenery(self, y):
        self.climb += y
        self.cloud_height -= y
        for sprite in self.scenery:
            sprite.frame.y -= y
        for enemy in self.enemies:
            enemy.y -= y

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
        elif self.player.frame.top() < 0 :
            self.game_state = GAME_DEAD
            sound.play_effect('Crashing')
        elif self.player.frame.intersects(enemy_frame):
            self.game_state = GAME_DEAD
            sound.play_effect('Powerup_1')

    def collision_detect(self):
        bounce = False
        if self.player.velocity < 0:
            p = scene.Point(self.player.frame.x + self.player.frame.w/2,
            self.player.frame.y)
            for sprite in self.scenery:
                if hasattr(sprite, 'is_colliding'):
                    collision = sprite.is_colliding(p)
                else:
                    collision = p in sprite.frame
                if collision:
                    self.player.velocity = PLAYER_BOUNCE_VELOCITY
                    sound.play_effect('Boing_1')
                    break

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
            score_text('NEW HIGH SCORE!',
            self.bounds.w / 2,
            self.bounds.h * 0.75)
            with open(file_name, 'w') as out_file:
                json.dump(high_scores, out_file)

    def draw_text(self):
        score = int(self.climb / 10)
        s = 'Score: {}'.format(score)
        x = self.bounds.center().x
        if self.game_state == GAME_WAITING:
            shadow_text('Tap Screen to Start',  x, self.bounds.h * 0.6)
            shadow_text('Tilt Screen to Steer', x, self.bounds.h * 0.4)
        elif self.game_state == GAME_PLAYING:
            shadow_text(s, x, self.bounds.h * 0.95)
        if(self.game_state == GAME_DEAD):
            shadow_text(s, x, self.bounds.h * 0.95)
            shadow_text('Game Over', x, self.bounds.h * 0.6)
            shadow_text('Tap to Play Again', x, self.bounds.h * 0.4)
            self.high_score(player_name, score)

    def setup(self):
        self.game_state = GAME_WAITING
        self.scenery = []
        self.climb = 0
        self.enemies = []
        ground_level = self.create_ground(12)
        self.cloud_height = 200
        self.generate_clouds()
        self.player = Player()
        self.player_apex_frame = False
        self.player.frame = scene.Rect(0, 0, IMAGE_WIDTH, IMAGE_HEIGHT)
        self.player.frame.center(self.bounds.center())
        self.player.frame.y = ground_level
        self.player_max_y = self.bounds.h * 0.6

    def draw(self):
        self.game_loop()
        scene.background(0.40, 0.80, 1.00)
        for sprite in self.scenery:
            sprite.draw()
        self.player.draw()
        self.draw_text()

        global enemy_frame
        for enemy in self.enemies:
            enemy.update(self.dt)
            enemy.draw()
            enemy_rect = enemy_frame

    def touch_began(self, touch):
        if self.game_state == GAME_WAITING:
            self.game_state = GAME_PLAYING
            self.player.velocity = PLAYER_INITIAL_BOUNCE
        elif self.game_state == GAME_DEAD:
            self.setup()

MyScene()
