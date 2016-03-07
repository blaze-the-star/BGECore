from filter2D import Filter2D

class Vignetting(Filter2D):
	"""
	Creates an envoirment effect of some color.
	
	.. attribute:: colorR
		
		The color Red value, 0 <= x <= 1
		
		:type: float
	
	.. attribute:: colorG
		
		The color Green value, 0 <= x <= 1
		
		:type: float
	
	.. attribute:: colorB
		
		The color Blue value, 0 <= x <= 1
		
		:type: float
		
	.. attribute:: colorA
		
		Should change the Alpha value, but it doesn't seem to do anything.
		
		:type: float
		
	.. attribute:: size
		
		Modifies the size of the shader, or it seems so. 0 <= x <= ?
		
		:type: float
	
	.. warning::
	
		Doesn't seem to work very well on embedded mode, the size seems not correct.
	
	"""
	
	
	colorR = 0.0
	colorG = 0.0
	colorB = 0.0
	colorA = 0.0
	size = 0.8