#-------- HEX to RGB Helper Functions ---------
_NUMERALS = '0123456789abcdefABCDEF'
_HEXDEC = {v: int(v, 16) for v in (x+y for x in _NUMERALS for y in _NUMERALS)}
LOWERCASE, UPPERCASE = 'x', 'X'

def rgb(triplet):
    return _HEXDEC[triplet[0:2]], _HEXDEC[triplet[2:4]], _HEXDEC[triplet[4:6]]

def triplet(rgb, lettercase=LOWERCASE):
    return format(rgb[0]<<16 | rgb[1]<<8 | rgb[2], '06'+lettercase)
#------------------------------------------------------

import re

# A suggestion from the autor of this parser:
# If you want to make a VN. A basic VN or a game that is no more than just a VN. Then it's hightly recommended to use Ren'Py Visual Novel Engine directly.
# Combine Ren'Py files with BGECore or any other game engine only if you want to do something diferent (like a 3D game) that uses VN elements.

class Character():
	def __init__(self, name, color=(0,0,0,0)):
		self.name = name
		self._color = None
		self.color = color
		
	@property
	def color(self):
		return self._color
		
	@color.setter
	def color(self, val):
		if type(val) is str:
			if val[0] != "#": raise ValueError("Malformatted color string!")
			self._color = [x/255 for x in rgb(val[1:])]+[1]
		else:
			self._color = color
		
	
class RenPyParser():
	""" Parser Ren'Py files (**.rpy**). Can be used from InteractiveText behaviors to create a nice game. 
	
	Most of the features that Ren'Py provides are not ported to BGECore and will have to be done outside the RenPy script. This includes:
	* Jumping labels across multiple RenPy files.
	* Compiling *.rpy* files is not supported.
	* Anything outside the methods descrived here *http://www.renpy.org/doc/html/quickstart.html* is probably not supported.
	* The start of the script is the init block, you can't use any more.
	
	:param string filepath: Absolute filepath to the *.rpy* file to parse.
	
	.. attribute:: labels
	
		A dictionary of label block positions in the raw_data string representing the file. Uses the label name as the key.
		
	.. attribute:: dialogs
	
		After a label is parsed it contains a list of 3-val tuples containing the data in each line in the following form (tab_level, command/name, [dialog/arguments]), the name
		and the dialogs are quoted strings. If there is no name an emtpy string is used.
		
	"""
	
	blocks = {"label": {}, "init": {}, "menu": {}}
	dialogs = []
	store = {"store": {}}
	characters = {}
	line_index = 0
	
	def __init__(self, filepath):
		self.dialog_position = 0
	
		with open(filepath, 'r') as f:
			self.raw_data = "\n"
			self.raw_data += f.read().replace("    ", "\t")
			
		x = -1
		y = 0
		type, name = (None, None)
		while True:
			#x = self.raw_data.find("\nlabel ", y)
			c = y
			for line_index, line in enumerate(self.raw_data[y:].splitlines()):
				t = self.parseLine(line)
				self.line_index = line_index
				if t[0] == 0 and t[1] not in self.blocks.keys():
					self.execInitLine(t[1], t[2], line)
					
				x = line.rfind(":")
				t = max([line.rfind('#'), line.rfind('"')])
				if x > t: x = c; break
				else: c += len(line)+1
			
			y = self.raw_data.find("\n", x)
			if x == -1: break
			if type != "init" and name: self.blocks[type][name] = (self.blocks[type][name][0], x)
			t = self.raw_data[x:y-1].split()
			
			if len(t) == 1 and t[0] == "init":
				type = "init"
				name = x
			if len(t) == 2:
				type = t[0]
				name = t[1]
			self.blocks[type][name] = (y+1, None)
			
	def execInitLine(self, name, args, line):
		if name == "define":
			if args[1] != "=": raise NotImplementedError("At line " + str(self.line_index) + ". Wrong formated line. This line can't be interpreted with the current parser.")
			
			obj = eval(','.join(args[2:])) #EPIC HACK
			
			t = args[0].split(".", 1)
			if len(t) == 1:
				self.store["store"][args[0]] = obj
			if len(t) == 2:
				try: self.store[t[0]][t[1]] = obj
				except KeyError:
					self.store[t[0]] = {}
					self.store[t[0]][t[1]] = obj
					
			if type(obj) is Character: self.characters[args[0]] = obj
					
	def execLine(self, name, args):
		print(name, args)
		
	def parseLine(self, line):
		lvl= 0
		for i in range(len(line)):
			if line[i] != '\t': break
			lvl+=1
		line = line[lvl:]
		line = re.findall(r'(?:[^\s,"]|"(?:\\.|[^"])*")+', line)
		
		for i, l in enumerate(line):
			if l.startswith("#"):
				line.remove(l) 
				break
				
			x = l.rfind('"'); y = l.rfind("#")
			if y != -1 and x < y: line[i] = line[i][:y]
		
		if len(line) == 0: return (None, None, None)
		if len(line) == 1:
			if line[0][0] == '"' and line[0][-1] == '"':
				return (lvl, "", [line[0]])
			else: return (lvl, line[0], [])
		else:	
			return (lvl, line[0], line[1:])
	
	def parse(self, labelname):
		""" Parses a label block, by default you should start with "start", the jump command uses this. Parsing a new block will replace the data on self.dialogs. """
	
		self.dialogs = []
		self.dialog_position = 0
		x, y = self.blocks["label"][labelname]
		data = self.raw_data[x:y]
		for line in data.splitlines():
			t = self.parseLine(line)
			if t[0] != None: self.dialogs.append(t)
			
	def next(self):
		""" Returns the following pair of name-dialog. All commands/conditions/loops/scripts in beetween are executed. """
		
		#For starters we will simply return the next set in the dialogs list as strings, even if they include commands. Before that tough we must implement the InteractiveText Behavior.
		p = self.dialog_position
		self.dialog_position += 1
		
		is_command = True
		
		try:
			name = self.dialogs[p][1]
			text = self.dialogs[p][2]
		
			if len(text) > 0: text = text[0]
			else: text = ""
			
			if name == "" or name[0] == '"': is_command = False
			elif name in self.characters.keys():
				text = text.replace('\\"', '"')
				return (self.characters[name], text[1:-1])
			
		except IndexError: return ("", "")
		
		if not is_command:
			text = text.replace('\\"', '"')
			return (name[1:-1], text[1:-1])
		
		else:
			self.execLine(name, self.dialogs[p][2])
			return self.next()

#===========================================================
#				This are the behaviours, not part of the Parser
#===========================================================
		
	
from core.behavior.base import *
from core.interface import event
from core import module, key, sequencer
from bge import logic
class InteractiveText(Object):
	""" 
		Creates an interective text for Visual Novels and games alike. This class can be subclassed to expand functionality.
	"""
	
	parser = None
	name = None
	_filepath = None
	
	def init(self):
		self.parser.parse("start")
		self.obj.text = ""
		if self.name: self.name.text = ""
		self.twt = sequencer.Typewriter(self.obj)
		module.enableInputFor(self)

	@property
	def filepath(self):
		return self._filepath
		
	@filepath.setter
	def filepath(self, path):
		self._filepath = path
		if path.endswith(".rpy"):
			self.parser = RenPyParser(logic.expandPath("//" + path))
		else:
			raise RuntimeError("The InteractiveText behavior only supports .rpy files. ")
			
	def onKeyDown(self, keys):
		if event.selected == None and key.LEFTMOUSE in keys:
			if self.twt.status == True:
				self.twt.finish()
			else:
				name, text = self.parser.next()
				color = None
				
				if type(name) == Character:
					ch = name
					name = name.name
					color = ch.color
				
				self.twt.text = text
				if self.name:
					self.name.text = name
					if color: self.name.color = color