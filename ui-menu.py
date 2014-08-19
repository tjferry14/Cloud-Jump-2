import ui

def play_game(sender):
	ui.close_all()

def change_character(sender):
		v = ui.View()
		v.background_color = (0.40, 0.80, 1.00)
		header = ui.Label(frame = (200, 19.5, 700, 116.5))
		header.text_color = (1.00, 1.00, 1.00)
		header.text = 'Select A Character'
		header.font = ('AvenirNext-Heavy', 70)
		v.add_subview(header)
		
		char1 = ui.Button(frame=(40, 160, 100, 100), 
		                   image=ui.Image.named('Boy'))
		v.add_subview(char1)
		
		char2 = ui.Button(frame=(195, 160, 100, 100), 
		                   image=ui.Image.named('Girl'))
		v.add_subview(char2)
		
		char3 = ui.Button(frame=(340, 160, 100, 100), 
		                   image=ui.Image.named('Guardsman'))
		v.add_subview(char3)
		
		v.present(style='full_screen', hide_title_bar=True)

v = ui.load_view('ui-menu')
v.background_color = (0.40, 0.80, 1.00)
v.present(style='full_screen', hide_title_bar=True)
