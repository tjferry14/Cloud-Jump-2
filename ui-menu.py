# this is meant to be viewed in landscape mode on an iPad
import ui

characters = 'Boy Girl Guardsman Hamster_Face Mouse_Face Man'.split()

def play_game(sender):
    ui.close_all()

def make_header():
    header = ui.Label(frame = (200, 19.5, 700, 116.5))
    header.text_color = (1.00, 1.00, 1.00)
    header.text = 'Select A Character'
    header.font = ('AvenirNext-Heavy', 70)
    return header

def character_tapped(sender):
    print('The user wants to be: ' + sender.name)

def make_button(x, image_name = 'Boy'):
    button = ui.Button(name=image_name,
                       frame=(x, 160, 128, 128),
                       image=ui.Image.named(image_name))
    button.action=character_tapped
    return button

def change_character(sender):
    v = ui.View()
    v.background_color = (0.40, 0.80, 1.00)
    v.add_subview(make_header())
    for i, character in enumerate(characters):
        v.add_subview(make_button(40 + i * 155, character))
    v.present(style='full_screen', hide_title_bar=True)

v = ui.load_view('ui-menu')
v.background_color = (0.40, 0.80, 1.00)
v.present(style='full_screen', hide_title_bar=True)
