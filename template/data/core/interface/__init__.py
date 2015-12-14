from bge import logic, events
from core import module
#import core.interface
import core.interface.event
import core.interface.window
import core.interface.widget
import core.interface.button
import core.interface.label
import core.interface.flabel
import script.constant

Window = window.Window
winmod = window
window = None
""" *window.Window* unique instance, initialized in the first tic of the interface loop. """

Button = button.Button
TextButton = button.TextButton
Menu = button.Menu
TextMenu = button.TextMenu
Label = label.Label

_init = False
def loop():
	""" Interface loop. Initializes and updates the game interface. """
	
	global _init, window
	if _init == False:
		_init = True
		module.window = Window()
		window = module.window
		
		for obj in window.scene_gui.objects:
			if obj.get("Text") and not obj.name.startswith("Font."): label.replaceBlenderText(obj)
		
	module.window.update()
	core.interface.event._click_event_loop(logic.mouse.events[events.LEFTMOUSE])
	
	#Make sure the cursor is always the last on the post_draw pipeline.
	ImageCursor = winmod.ImageCursor
	s = module.scene_gui
	if type(window.cursor) is ImageCursor and not type(s.post_draw[-1]) is ImageCursor:
			i = s.post_draw.index(window.cursor.draw)
			s.post_draw.insert(len(s.post_draw)-1, s.post_draw.pop(i))
