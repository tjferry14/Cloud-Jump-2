# this is meant to be viewed in landscape mode on an iPad
import ui

characters = 'Boy Girl Guardsman Hamster_Face Mouse_Face Man'.split()
high_scores = {n:(i+1)*1000 for i, n in enumerate('Al Bob Carl David Elliot Freddie Godzilla'.split())}

class SelectACharacterView(ui.View):
    def __init__(self):
        self.name = 'Cloud Jump 2 -- Select A Character'
        self.background_color = (0.40, 0.80, 1.00)
        self.add_subview(self.make_header())
        for i, character in enumerate(characters):
            self.add_subview(self.make_button(40 + i * 155, character))
        self.present()

    @classmethod
    def make_header(cls):
        header = ui.Label(frame = (200, 19.5, 700, 116.5))
        header.text_color = 'white'
        header.text = 'Select A Character'
        header.font = ('AvenirNext-Heavy', 70)
        return header

    @classmethod
    def character_tapped(cls, sender):
        print('The user wants to be: ' + sender.name)
        sender.superview.close()

    @classmethod
    def make_button(cls, x, image_name = 'Boy'):
        img = ui.Image.named(image_name).with_rendering_mode(ui.RENDERING_MODE_ORIGINAL)
        button = ui.Button(name=image_name, frame=(x, 160, 128, 128), image=img)
        button.action=cls.character_tapped
        return button

class HighScoreView(ui.View):
    def __init__(self, high_scores=high_scores):
        self.name = 'Cloud Jump 2 -- Leaderboard'
        tv = ui.TableView()
        tv.flex = 'WH'
        tv.data_source = ui.ListDataSource(items=self.scores_list(high_scores))
        tv.allows_selection = tv.data_source.delete_enabled = False 
        self.add_subview(tv)
        self.present('sheet')

    @classmethod
    def scores_list(cls, high_scores):
        scores_sorted = sorted(zip(high_scores.values(),
                                   high_scores.keys()), reverse=True)
        return ['{:7>}  |  {}'.format(s, n) for s, n in scores_sorted]

class UserNameView(ui.View):
    def __init__(self, default_user_name='Name'):
        self.name = 'Cloud Jump 2 -- Username'
        self.background_color = 0.40, 0.80, 1.00
        self.label = ui.Label(frame=(12, 100, 2000, 70))
        self.label.text = 'What is your name?'
        self.label.text_color = 'black'
        self.label.font = ('Avenir-Black', 55)
        self.add_subview(self.label)
        self.text_field = ui.TextField(frame=(155, 175, 200, 32))
        self.text_field.text = default_user_name
        self.text_field.text_color = 'grey'
        self.text_field.clear_button_mode = 'while_editing'
        self.add_subview(self.text_field)
        button = ui.Button(background_color='white',
                   frame=(360, 175, 75, 36),
                   image=ui.Image.named('ionicons-arrow-right-a-32'))
        button.action = self.button_tapped
        self.add_subview(button)
        self.present('sheet')

    @classmethod
    def button_tapped(cls, sender):
        username = sender.superview.text_field.text
        if username:
            print('The username is: ' + username)
            sender.superview.close()

def change_character(sender):
    SelectACharacterView()

def change_name(sender):
    UserNameView()

def show_leaderboard(sender):
    HighScoreView()

def play_game(sender):
    ui.close_all()

v = ui.load_view('ui-menu')
v.background_color = (0.40, 0.80, 1.00)
v.present()
