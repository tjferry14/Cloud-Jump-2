# this is meant to be viewed in landscape mode on an iPad
import ui

characters = 'Boy Girl Guardsman Hamster_Face Mouse_Face Man'.split()

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
                           image=ui.Image.named(image_name))
        button.action=cls.character_tapped
        return button


def change_character(sender):
    SelectACharacterView()

def play_game(sender):
    ui.close_all()
    
v = ui.load_view('ui-menu')
v.background_color = (0.40, 0.80, 1.00)
v.present(style='full_screen', hide_title_bar=True)
