import console, json, math, os, random, scene, sound

IMAGE_WIDTH = 101
IMAGE_HEIGHT = 171
IMAGE_Y_OFFSET = -30
BLOCK_HEIGHT = 40
BLOCK_DEPTH = 80
DEAD_ZONE =  0.02
PLAYER_CONTROL_SPEED = 2000
PLAYER_BOUNCE_VELOCITY = 1700
PLAYER_INITIAL_BOUNCE = 1700
MAX_CLOUD_DIST = 505
DIFFICULTY_Q = 100000.0
GAME_GRAVITY = 2000
GAME_WAITING = 0
GAME_PLAYING = 1
GAME_DEAD = 2
ENEMY_DENSITY=0.2

if os.path.isfile("names.json"): # if there is a file with names...
    text_file = open("names.json") # only open it in normal mode
else: # if not...
    text_file = open("names.json", "w+") # make one

if os.stat("names.json").st_size > 0:
    for line in text_file:
        if line.istitle():
            player_name = line
        else:
            player_name = console.input_alert('What is your name? ').title()
            text_file = open("names.json", "w")
            text_file.write(player_name)
            text_file.close()
else:
    player_name = console.input_alert('What is your name? ').title()
    text_file = open("names.json", "w")
    text_file.write(player_name)
    text_file.close()

# to reduce latency, preload sound effects
for s in 'Boing_1 Crashing Powerup_1'.split():
    sound.load_effect(s)

def shadow_text(s, x, y): # text for end of game and score keeping
    scene.tint(0,0,0)
    scene.text(s, 'AppleSDGothicNeo-Bold', 48, x + 2, y - 2)
    scene.tint(0.00, 0.50, 1.00)
    scene.text(s, 'AppleSDGothicNeo-Bold', 48, x, y)

def score_text(s, x, y): # text for a new player high score
    scene.tint(0,0,0)
    scene.text(s, 'AppleSDGothicNeo-Bold', 48, x + 2, y - 2)
    scene.tint(1.00, 1.00, 0.40)
    scene.text(s, 'AppleSDGothicNeo-Bold', 48, x, y)

class Player(object):
    def __init__(self):
        self.bounds = scene.Rect()
        self.velocity = 0

    def draw(self):
        scene.tint(1,1,1)
        scene.image('Alien', self.bounds.x, self.bounds.y + IMAGE_Y_OFFSET)

class GroundBlock(object):
    def __init__(self):
        self.bounds = scene.Rect()

    def draw(self):
        scene.tint(1,1,1)
        scene.image('PC_Grass_Block', self.bounds.x, self.bounds.y)

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
        self.bounds = scene.Rect(0, 0, self.width, 60)

    def is_colliding(self, pos):
        startp = self.bounds.x - self.width/2
        endp = self.bounds.x + self.width/2
        if ((pos.x < endp) and (pos.x > startp) and
        (pos.y < (self.bounds.y + 30)) and
        (pos.y > (self.bounds.y + 10))):
            return True
        return False

    def draw(self):
        scene.push_matrix()
        scene.translate(self.bounds.x, self.bounds.y)
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
        #self.scene = scene
        #self.hit = False
        self.x = self.initial_x = start_cloud.bounds.x
        self.y = start_cloud.bounds.center().y
        #self.removed = False
        #self.dead = False
        self.size = 64
        self.color = scene.Color(1, 0, 1)
        self.speed = 0     #1.0 / self.size * 100
        self.amp = 0   #    random() * 300

    def update(self, dt):
        self.y -= self.speed
        self.x = self.initial_x +  math.sin(self.y / 100) * self.amp
        self.amp = max(self.amp * 0.99, 0)
        #if self.y < -64:
        #    self.removed = True

    def draw(self):
        scene.tint(self.color.r, self.color.g, self.color.b, 1.0)
        scene.image('Ghost', self.x - self.size/2,
                             self.y - self.size/2,
                             self.size, self.size)
        scene.tint(1, 1, 1)

        global enemy_bounds
        s = self.size
        enemy_bounds = scene.Rect(self.x - s/2 * 0.9,
                                  self.y - s/2 * 0.8,
                                  s * 0.9, s * 0.8)

class MyScene(scene.Scene):
    def __init__(self):
        scene.run(self)

    def create_ground(self):
        for x in range((int(self.bounds.w) / IMAGE_WIDTH) + 1):
            block = GroundBlock()
            block.bounds = scene.Rect(x * IMAGE_WIDTH, 0,
                                      IMAGE_WIDTH, IMAGE_HEIGHT)
            self.scenery.append(block)

    def generate_clouds(self):
        y = self.cloud_height
        while self.cloud_height < self.bounds.h * 2:
            q = min(self.climb, DIFFICULTY_Q)
            min_dist = int(MAX_CLOUD_DIST * q / DIFFICULTY_Q)
            max_dist = int(MAX_CLOUD_DIST / 2 + min_dist / 2)
            self.cloud_height += random.randint(min_dist, max_dist)
            cloud = Cloud()
            cloud.bounds.x = random.random() * (self.bounds.w - 150)
            cloud.bounds.y = self.cloud_height
            self.scenery.append(cloud)
            if random.random() < ENEMY_DENSITY:
                #generate new enemy
                self.enemies.append(Enemy(cloud))

    def cull_scenery(self):
        for sprite in self.scenery:
            if sprite.bounds.top() < 0:
                self.scenery.remove(sprite)

    def control_player(self):
        tilt = scene.gravity().x
        if abs(tilt) > DEAD_ZONE:
            move = self.dt * tilt * PLAYER_CONTROL_SPEED
            self.player.bounds.x += move
            if self.player.bounds.x < 0:
                self.player.bounds.x = 0
            elif self.player.bounds.x > self.bounds.w - self.player.bounds.w:
                self.player.bounds.x = self.bounds.w - self.player.bounds.w

    def lower_scenery(self, y):
        self.climb += y
        self.cloud_height -= y
        for sprite in self.scenery:
            sprite.bounds.y -= y
        for enemy in self.enemies:
            enemy.y -= y

    def run_gravity(self):
        global enemy_bounds
        player_y_move = self.dt * self.player.velocity
        scenery_y_move = 0
        old_velocity = self.player.velocity
        self.player.velocity -= self.dt * GAME_GRAVITY
        if old_velocity > 0 and self.player.velocity <= 0:
            self.player_apex_frame = True
        self.player.bounds.y += player_y_move
        if self.player.bounds.y >= self.player_max_y :
            scenery_y_move = self.player.bounds.y - self.player_max_y
            self.player.bounds.y = self.player_max_y
            self.lower_scenery(scenery_y_move)
        elif self.player.bounds.top() < 0 :
            self.game_state = GAME_DEAD
            sound.play_effect('Crashing')
        elif self.player.bounds.intersects(enemy_bounds):
            self.game_state = GAME_DEAD
            sound.play_effect('Powerup_1')

    def collision_detect(self):
        bounce = False
        if self.player.velocity < 0:
            p = scene.Point(self.player.bounds.x + self.player.bounds.w/2,
                            self.player.bounds.y)
            for sprite in self.scenery:
                if hasattr(sprite, 'is_colliding'):
                    collision = sprite.is_colliding(p)
                else:
                    collision = p in sprite.bounds
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
            shadow_text(s,                      x, self.bounds.h * 0.95)
        if(self.game_state == GAME_DEAD):
            shadow_text(s,                      x, self.bounds.h * 0.95)
            shadow_text('Game Over',            x, self.bounds.h * 0.6)
            shadow_text('Tap to Play Again',    x, self.bounds.h * 0.4)
            self.high_score(player_name, score)

    def setup(self):
        self.game_state = GAME_WAITING
        #self.bullets = []
        self.scenery = []
        self.climb = 0
        self.enemies = []
        self.create_ground()
        self.cloud_height = 200
        self.generate_clouds()
        self.player = Player()
        self.player_apex_frame = False
        self.player.bounds = scene.Rect(self.bounds.w / 2 - IMAGE_WIDTH / 2,
                                        BLOCK_HEIGHT + BLOCK_DEPTH / 2,
                                        IMAGE_WIDTH, IMAGE_HEIGHT)
        self.player_max_y = self.bounds.h * 0.6

    def draw(self):
        self.game_loop()
        scene.background(0.40, 0.80, 1.00)
        for sprite in self.scenery:
            sprite.draw()
        self.player.draw()
        self.draw_text()

        global enemy_bounds
        for enemy in self.enemies:
            enemy.update(self.dt)
            enemy.draw()
            enemy_rect = enemy_bounds

    def touch_began(self, touch):
        if self.game_state == GAME_WAITING:
            self.game_state = GAME_PLAYING
            self.player.velocity = PLAYER_INITIAL_BOUNCE
        elif self.game_state == GAME_DEAD:
            self.setup()

MyScene()
