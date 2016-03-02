from filter2D import Filter2D

class Vignetting(Filter2D):
	"""
	
	.. warning::
	
		Doesn't seem to work very well on embedded mode, the size seems not correct.
	
	"""
	
	
	colorR = 0.0
	colorG = 0.0
	colorB = 0.0
	colorA = 0.0
	size = 0.7
		