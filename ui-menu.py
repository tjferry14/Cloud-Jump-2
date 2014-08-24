# this is meant to be viewed in landscape mode on an iPad
import ui

characters = 'Boy Girl Guardsman Hamster_Face Mouse_Face Man'.split()
high_scores = {n:(i+1)*1000 for i, n in enumerate('Al Bob Carl David Elliot Freddie Godzilla'.split())}

class SelectACharacterView(ui.View):
    def __init__(self):
        self.background_color = (0.40, 0.80, 1.00)
        self.add_subview(self.make_header())
        for i, character in enumerate(characters):
            self.add_subview(self.make_button(40 + i * 155, character))
        self.present(style='full_screen', hide_title_bar=True)

    @classmethod
    def make_header(cls):
        header = ui.Label(frame = (200, 19.5, 700, 116.5))
        header.text_color = (1.00, 1.00, 1.00)
        header.text = 'Select A Character'
        header.font = ('AvenirNext-Heavy', 70)
        return header

    @classmethod
    def character_tapped(cls, sender):
        print('The user wants to be: ' + sender.name)

    @classmethod
    def make_button(cls, x, image_name = 'Boy'):
        button = ui.Button(name=image_name,
                           frame=(x, 160, 128, 128),
                           image=ui.Image.named(image_name).with_rendering_mode(ui.RENDERING_MODE_ORIGINAL))
        button.action=cls.character_tapped
        return button

class HighScoreView(ui.View):
    def __init__(self, high_scores=high_scores):
        self.title = 'CloudJump2 -- Leaderboard'
        self.text = 'CloudJump2 -- Leaderboard'
        tv = ui.TableView()
        tv.flex = 'WH'
        tv.data_source = ui.ListDataSource(items=self.scores_list(high_scores))
        tv.allows_selection = tv.data_source.delete_enabled = False 
        self.add_subview(tv)
        self.present('sheet')
        #self.wait_modal()

    @classmethod
    def scores_list(cls, high_scores):
        scores_sorted = sorted(zip(high_scores.values(),
                                   high_scores.keys()), reverse=True)
        return ['{:7>}  |  {}'.format(s, n) for s, n in scores_sorted]

def change_character(sender):
    SelectACharacterView()

def change_name(sender):
    superview = sender.superview
    label = ui.Label()
    label.text = 'Your name?'
    label.center = superview.center
    label.y *= 1.5
    superview.add_subview(label)
    user_name = ui.TextField(frame=(0, 0, 200, 25))
    user_name.text = 'TJ'
    user_name.center = label.center
    user_name.y += 30
    #button_items = [ui.ButtonItem(title=n) for n in 'Al Bob Carl David Elliot Freddie'.split()]
    #user_name.left_button_items = button_items
    user_name.clear_button_mode = 'unless_editing'
    superview.add_subview(user_name)
    OK = ui.Button(title = 'OK')
    OK.center = user_name.center
    OK.y += 30
    superview.add_subview(OK)

def show_leaderboard(sender):
    HighScoreView()

def play_game(sender):
    ui.close_all()

v = ui.load_view('ui-menu')
v.background_color = (0.40, 0.80, 1.00)
v.present(style='full_screen', hide_title_bar=True)
