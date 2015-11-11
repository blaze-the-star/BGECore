from script import gui
from script import behavior
from bge import logic, events
from core import module, utils
from core.interface import event
import time
import traceback

start = time.time()

done = time.time()
elapsed = done - start

_state = 0
_last_time = time.time()
def loop():
	global _state, _last_time
	
	#Set scene
	if module.change_scene_frame == True:
		utils.setScene(None)
		return
	
	#Game initialization	
	if _state == 0:
		_state = 1
		logic.setMaxLogicFrame(1)
		module.scene_gui_behavior.scene = module.scene_gui
		module.scene_gui_behavior.init()
		for b in module.scene_gui_behavior.behaviors: b.init()
	
	if module.window.camera.sensors["Always"].status != logic.KX_SENSOR_ACTIVE: return
	
	#Key events
	event._key_event_loop()
	
	#GUI Behavior
	if module.scene_gui_behavior.paused == False: module.scene_gui_behavior.update()
	for b in module.scene_gui_behavior.behaviors:
		if b.paused == False: b.update()
	
	#Game Behavior
	try:
		if module.scene_behavior and module.change_scene_frame == False:
			if module.scene_behavior.paused == False:
				module.scene_behavior.update()
				module.scene_behavior.baseUpdate()
			if not module.scene_behavior: return #When removing the scene
			for b in module.scene_behavior.behaviors:
				if b.paused == False: b.update()
				if not module.scene_behavior: return #When removing the scene
	except:
		if module.scene_behavior: module.scene_behavior.paused = True
		utils.debug("Error during runtime. Scene behavior suspended!")
		traceback.print_exc()
	
	#Other callbacks
	for v in module.video_playback_list: v.updateVideo()
			
	done = time.time()
	if (done - _last_time) >= 0.1:
		_last_time = done
		for call in module.low_frequency_callbacks:
			call()