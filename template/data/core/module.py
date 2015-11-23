#Scenes and behaviors
scene_behavior_dict = {}
scene_behavior = None
scene_gui_behavior = None
scene_game = None
scene_gui = None

#Static of core.utils.setScene()
change_scene_frame = False

#Static of core.dynamic.loadScene()
change_scene_dynamic = False
change_scene_dynamic_state = 0

#Static of core.utils.setFilter2D()
filter_queue = []

#Static of core.utils.libLoad()
libload_queue = []

#Interface
window = None
widget_dict = {}

listen_input_list = []
labels = {}

video_playback_list = []
low_frequency_callbacks = []
height_frequency_callbacks = []

LOW_FREQUENCY_TICK = 0.1
HEIGHT_FREQUENCY_TICK = 0.02

cont = None

def enableInputFor(behavior):
	global listen_input_list
	behavior.use_keyboard = True
	listen_input_list.append(behavior)
	
def enableInputOnGUI():
	global listen_input_list
	scene_gui_behavior.use_keyboard = True
	listen_input_list.append(scene_gui_behavior)
	
def disableInputFor(behavior):
	global listen_input_list
	listen_input_list.remove(behavior)
	
def disableInputOnGUI():
	global listen_input_list
	listen_input_list.remove(scene_gui_behavior)