import inspect
import bgl

#######################################
try:
	from script import constant
except:
	class constant:
		CORE_DEBUG_PRINT = True
		CORE_DEBUG_VERBOSE = True

def debug(text):
	if constant.CORE_DEBUG_PRINT == True: print(text)

def verbose(text):
	if constant.CORE_DEBUG_VERBOSE == True: print(text)
	
_loop = False
_nextframe_callbacks = []
_nextframe_callbacks2 = []
def _nextframe_predraw():
	global _nextframe_callbacks, _nextframe_callbacks2
	
	cpy = _nextframe_callbacks2
	
	_nextframe_callbacks2 = _nextframe_callbacks
	_nextframe_callbacks = []
	
	for call in cpy: call()

	
#######################################

def getShaderSource(program):
	maxCount = 1
	count = bgl.Buffer(bgl.GL_INT, 1)
	shaders = bgl.Buffer(bgl.GL_BYTE, [maxCount])
	bgl.glGetAttachedShaders(program, maxCount, count, shaders)
	 
	maxLength = 64000
	length = bgl.Buffer(bgl.GL_INT, 1)
	source = bgl.Buffer(bgl.GL_BYTE, [maxLength])
	bgl.glGetShaderSource(shaders[0], maxLength, length, source)
	return "".join(chr(source[i]) for i in range(length[0]))
	
class Filter2D():

	owner = None
	slot = None
	uslot = []
	
	def __init__(self, **kw):
		#Class attributes from children classes will be considered as uniforms,
		#they will also be accesed as instance attributes,
		#the uniform will be updated when an instance attribute that is also uniform is.
	
		self.uniforms = []
		self.program = None
		self.afdraw_list = []
		self.error = -2 #if >= 1 fail.
	
		#Make child class attributtes become instance attributtes.
		for key, value in self.__class__.__dict__.items() :
			if key.startswith('__'): continue
			if inspect.ismethod(getattr(self.__class__, key)): continue
			if inspect.isfunction(getattr(self.__class__, key)): continue
			
			self.__dict__[key] = value
			self.uniforms.append(key)
			
		#Make list of kw become instance attributes, override current attributes.
		self.__dict__.update(kw)
		
		#Components nescesary to setup the shader.
		name = self.__class__.__name__
			
		if not self.owner:
			from bge import logic
			self.owner = logic.getCurrentController().owner
			
		if self.slot == None:
			try: self.slot = max(Filter2D.uslot)+1
			except ValueError: self.slot = 0
			Filter2D.uslot.append(self.slot)
		else:
			if self.slot in Filter2D.uslot:
				raise ValueError("Filter2D slot already in use")
				
		#Remove uniforms that are properties
		self.uniforms = [x for x in self.uniforms if x not in self.owner.getPropertyNames()]
				
		#Setup the shader
		try:
			owner = self.owner
			slot = self.slot
			try: cont = owner.controllers["Python"]
			except: verbose("Filter2D failed, the camera doesn't have a controller named Python")
			
			if cont != logic.getCurrentController():
				
				module.filter_queue.append((name, owner, slot))
				module._arecallbacks = True
				return

			path = logic.expandPath("//core/glsl/" + name + ".filter2D")
			with open(path, "r") as input:
				text = input.read()

			filter = owner.actuators["F"+str(slot)]
			filter.mode = logic.RAS_2DFILTER_CUSTOMFILTER
			filter.passNumber = slot
			filter.shaderText = text
			cont.activate(filter)
			
			#Finally we bind the uniforms, but a frame later.
			global _nextframe_callbacks, _loop
			if not _loop:
				self.owner.scene.pre_draw.append(_nextframe_predraw)
				_loop = True
			_nextframe_callbacks.append(self.bindAllUnioforms)				
			
			verbose("Setted 2D Filter " + name + " to slot " + str(slot))
		
		except:
			import traceback
			traceback.print_exc()
		
	def __setattr__(self, name, value):
		super().__setattr__(name, value)
		if name in self.uniforms:
			self.bindUniformf(name)
		
			
	def bindAllUnioforms(self):
		for uniform in self.uniforms:
			self.bindUniformf(uniform)
		
	def findProgram(self):
		if self.program == None:
			filter = self.owner.actuators["F"+str(self.slot)]
			text = filter.shaderText
			self.program = -1
			for prog in range(32767):
				if bgl.glIsProgram(prog) == True:
					if text == getShaderSource(prog):
						self.program = prog
						
			if self.program == -1: #If shader code not found, wait until post_draw.
				raise RuntimeError("Shader " + self.__class__.__name__ + " not found!")
		return self.program
			
	def bindUniformf(self, name):
		self.findProgram()
		bgl.glUseProgram(self.program)
		pname = self.__class__.__name__ + '_' + name
		bgl.glUniform1f(bgl.glGetUniformLocation(self.program, pname), getattr(self, name))
		