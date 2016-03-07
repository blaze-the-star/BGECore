from filter2D import Filter2D

class SBlur(Filter2D):
	""" 
	The Slow Blur shader. Use with caution.
	
	.. attribute:: samples
	
		The amount of sample to be used. x = 4, 8, 16, 32
		
		:type: float
		
	.. attribute:: percent
	
		The prercentage of the mixing. Wierd effect over 1. 0 <= x <= 1
		
		:type: float
		
	.. attribute:: radious
	
		The distance where to go to find new pixels. Seriously this is an insult to guissan blur. Default: 8.0
		
		:type: float
	
	
	"""
	
	samples = 8
	percent = 1.0
	radious = 8.0