from core import utils, module
from bge import logic, events
from core import key as core_key
import traceback

_hold = False
_selok = False
selected = None
_last = None

def _over_event_call(new):
	global _last
	old = _last
	if not old and not new: return
	if old == new: _over_event_loop(new, 2)
	else:
		if not new: _over_event_loop(old, 3)
		if not old: _over_event_loop(new, 1)
		if new and old:
			#The order is not clear, but it is important. A worng order could overwrite worngly _selok and _hold and thus making slected = None
			_over_event_loop(old, 3)
			_over_event_loop(new, 1)
	_last = new

def _over_event_loop(own, status):
	global _hold, _selok
	global selected
	list = module.widget_dict
	
	if status == 3:
		try:
			list[own]._mouseOut()
			if cam.pointInsideFrustum(pos): list[own].mouseOut()
		except: pass
		_selok = False
		if _hold == False: selected = None
		
	if status == 2:
		try: list[own].mouseOver()
		except: pass
	
	if status == 1:
		if _hold == False or selected==own:
			try:
				if own in list:
					list[own]._mouseIn()
					if module.window.cursorInsideFrustum(): list[own].mouseIn()
			except: utils.debug("_over_event_loop: Forgot to disable collisions?")
			selected = own
			_selok = True
			
def _click_event_loop(status):
	global _hold, _selok
	global selected
	list = module.widget_dict
	
	if status == 1 and selected: _hold = True
	if status == 2:
		if selected in list: list[selected].mousePressed()
	
	if status != 3: return
	
	if selected and _selok == True and _hold == True:
		try:
			if selected in list and list[selected]._active == True:
				list[selected]._mouseClick()
				if module.window.cursorInsideFrustum(): list[selected].mouseClick()
		except:
			utils.debug("_click_event_loop: Forgot to disable collisions?")
			utils.debug(traceback.format_exc())
		
	_hold = False
	
last_keyevents = [[],[],[],[]]
def _key_event_loop():
	global last_keyevents
	
	listen_list = [x for x in module.listen_input_list if x._immuse_keyboard == True]
	for x in module.listen_input_list: x._immuse_keyboard = x.use_keyboard
	keyevents = [[],[],[],[]]
	for key, status in logic.keyboard.active_events.items(): keyevents[status].append(key)
	for key, status in logic.mouse.active_events.items():
		if key == events.MOUSEX: continue
		if key == events.MOUSEY: continue
		keyevents[status].append(key)

	for si, status in enumerate(keyevents):
		for i, k in enumerate(status):
			if k in core_key.mod:
				keyevents[si][i] = core_key.mod[k]
	
	if len(keyevents[1]) > 0 and keyevents[1] != last_keyevents[1]:
		for b in listen_list: b.onKeyDown(keyevents[1])
	if len(keyevents[2]) > 0:
		for b in listen_list: b.onKeyPressed(keyevents[2])
	if len(keyevents[3]) > 0 and keyevents[3] != last_keyevents[3]:
		for b in listen_list: b.onKeyUp(keyevents[3])

	last_keyevents = keyevents
	