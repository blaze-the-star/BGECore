import core.behavior.base
import core.behavior.camera
import core.behavior.control
from script import constant
from core import module

Object = base.Object
Scene = base.Scene

MouseLook = camera.MouseLook
CamPlayerControl = control.CamPlayerControl
FixPlayerControl = control.FixPlayerControl
OutPlayerControl = control.OutPlayerControl
ThirdPerson = control.ThirdPerson

def addScene(class_name, name):
	""" Adds a scene behavior class to a scene dictionary. This way when the KX_Scene is loaded the scene behavior will be inistanciated.
	
	:param behavior.Scene class_name: The scene behavior to use.
	:param string name: The name of the scene that will have this scene behavior.
	"""

	if name == constant.CORE_SCENE_GUI:
		module.scene_gui_behavior = class_name()
	else:
		module.scene_behavior_dict[name] = class_name

