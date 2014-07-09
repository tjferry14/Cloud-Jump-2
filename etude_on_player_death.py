# Etude on Player Death - http://en.m.wikipedia.org/wiki/etude
# The player needs to die with more panache to give our game an
# arcade feel.  We could use your help on bot the sounds and the
# animations around the Player.die() method.  Better noises and 
# a player the shrinks to almost nothing and then is replace
# with a puff of smoke would be super cool. Thanks for playing!

import scene, sound, time

player_is_really_dead = False

def tinted_text(s, x, y, tint_color = scene.Color(0, 0, 1)):
    font_name = 'AppleSDGothicNeo-Bold'
    scene.tint(0, 0, 0)
    scene.text(s, font_name, 48, x + 2, y - 2)
    scene.tint(*tint_color)
    scene.text(s, font_name, 48, x, y)

def shadow_text(s, x, y):
    tinted_text(s, x, y, scene.Color(0.0, 0.5, 1.0))

class Sprite(scene.Layer):
    def __init__(self, rect = scene.Rect(), parent = None, image_name = 'Boy'):
        super(Sprite, self).__init__(rect)
        if parent:
            parent.add_layer(self)
        self.image = image_name
        self.velocity = scene.Point(0, 0)

    def update(self, dt):
        self.frame.x += dt * self.velocity.x
        self.frame.y += dt * self.velocity.y

def my_completion_routine():
    print('This text never gets printed.')
    global player_is_really_dead
    player_is_really_dead = True

class Player(Sprite):
    def __init__(self, rect = scene.Rect(), parent = None):
        super(self.__class__, self).__init__(rect, parent, 'Boy')
        global player_is_really_dead
        player_is_really_dead = False

    def die(self):
        self.animate('scale_x', 0.8, duration=1.0, completion=my_completion_routine)
        for i in xrange(4):
            sound.play_effect('Hit_{}'.format(i+1))
            time.sleep(0.5)
        global player_is_really_dead
        # The following is an infinate loop because
        # my_completion_routine() never gets called.
        #while not player_is_really_dead:
        #    time.sleep(1)
        self.superlayer.remove_layer(self)
        #del self  # suicide is not an tenable option
        #while min(self.frame.w, self.frame.h) > 0:
        #    print('s', self.frame)
        #    self.frame.x += 1
        #    self.frame.y += 1
        #    self.frame.w -= 2
        #    self.frame.h -= 2
        #    print('f', self.frame)
        #    self.draw(a=1)
        #    time.sleep(0.05)
        #    assert False

class MyScene(scene.Scene):
    def __init__(self):
        scene.run(self)

    def end_game(self):
        self.player.die()
        del self.player
        self.player = None

    def draw_text(self):
        x = self.bounds.center().x
        h = self.bounds.h
        msg = 'We could use your help.'
        shadow_text(msg, x, h * 0.95)
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
