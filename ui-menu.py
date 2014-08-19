import ui
import os
images_root = os.path.expanduser('~/Documents/Images')

def play_game(sender):
	ui.close_all()
	
def change_character(sender):
		v = ui.View()
		v.background_color = (0.40, 0.80, 1.00)		
		image_name = 'Banana'
		image_path = os.path.join(images_root, image_name + '.png')
		char1 = ui.ImageView()
		char1.image = ui.Image.named(image_path)
		char1.frame = (40, 600, 100, 100)	
		v.add_subview(char1)
		v.present(style='full_screen', hide_title_bar=True)

v = ui.load_view('ui-menu')
v.background_color = (0.40, 0.80, 1.00)
v.present(style='full_screen', hide_title_bar=True)