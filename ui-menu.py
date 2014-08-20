# this is meant to be viewed in landscape mode on an iPad
import ui

def play_game(sender):
    ui.close_all()

def make_header():
    header = ui.Label(frame = (200, 19.5, 700, 116.5))
    header.text_color = (1.00, 1.00, 1.00)
    header.text = 'Select A Character'
    header.font = ('AvenirNext-Heavy', 70)
    return header

def make_button(x, y, image_name = 'Boy'):
    return ui.Button(frame=(x, y, 100, 100), image=ui.Image.named(image_name))

def change_character(sender):
    v = ui.View()
    v.background_color = (0.40, 0.80, 1.00)
    v.add_subview(make_header())
    characters = [ make_button(40, 160, 'Boy'),
                   make_button(195, 160, 'Girl'),
                   make_button(340, 160, 'Guardsman'),
                   make_button(495, 160, 'Hamster_Face'),
                   make_button(640, 160, 'Mouse_Face'),
                   make_button(795, 160, 'Man') ]
    for character in characters:
        v.add_subview(character)

    v.present(style='full_screen', hide_title_bar=True)

v = ui.load_view('ui-menu')
v.background_color = (0.40, 0.80, 1.00)
v.present(style='full_screen', hide_title_bar=True)
