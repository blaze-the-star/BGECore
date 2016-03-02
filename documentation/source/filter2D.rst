.. _filter2D:

Filters 2D - GLSL Shaders
=================================
Filters are GLSL shaders, a post-render phase where the image is edited to mod it in any way. Here you can find a list of the default BGECore 2D Filters and a tutorial into how to use your own GLSL shaders.

Standard BGECore Shaders
-----------------------------------
Standard shaders can be used directly calling *utils.setFilter2D(name, camera, slot)*, the name of the shader must be one of the following list (starting with capital letter).

Vignetting
************

The vignetting shader adds a color in the borders of the screen. Usually that color is black, but red has also been use to make a damage effect. The following uniforms are defined:

.. attribute:: Vignetting_size

	Unknown
	
	:type: float

.. attribute:: Vignetting_colorR
	
	Red component of the color of the border, 1 >= x >= 0
	
	:type: float
	
.. attribute:: Vignetting_colorG
	
	Green component of the color of the border, 1 >= x >= 0
	
	:type: float
	
.. attribute:: Vignetting_colorB
	
	Blue component of the color of the border, 1 >= x >= 0
	
	:type: float
	
.. attribute:: Vignetting_colorA

	Alpha component of the color of the border, 1 >= x >= 0

	
SBlur
************

The slow blur filter allows for more customization in echange of computing time.

.. attribute:: SBlur_percent
	
	The amount of blurred color used in the final image, 1 >= x >= 0. If x > 1 a weird effect happens.
	
	:type: float
	
.. attribute:: SBlur_radious
	
	The distance away to check for pixel color, x > 0 (Recomended: 5.000)
	
	:type: float
	
.. attribute:: SBlur_samples
	
	The amount of samples that will be taken, one of the following: 4, 8, 16, 32 (Recomended: 8)
	
	:type: int


Installing or creating custom shaders
---------------------------------------------
BGECore Framewrok uses the directory ``data/core/glsl`` for GLSL shaders. Such shaders must use the extension **.filter2D** when disgned to be used as filters. If you have the source code of a shader, moving it there
should be enough to make it work, however shaders must be BGE complaint so you may need a little understanding of GLSL before you can use third party shaders not designed specifically for Blender.

The shadres are coded in GLSL, a language very similar to C that is compiled by BGE at runtime (when loading the shader). Depending on the version of Blender you're using you must guarantee that your shader
can work with a min version of OpenGL, currently Blender 2.79 enforces OpenGL < 2. This means that you can't use features of modern OpenGL in your shaders in standard BGE.

When porting a third party shader it's important to look at the folling things:

* It must be a fragment shader, meaning that in the shader at some point the variable **gl_FragColor** is used.
* It should have a **sampler2D uniform**, you need to rename it to *bgl_RenderedTexture* to make it work in BGE.
* It must have a **main** method.
* Build-in types that are predefined macros or constants can be converted to uniforms if you want to modify them in realtime.
* A default value of 0 will be assigned to uniforms not initialized by BGE. This means that if you create/use an uniform to use in realtime you must also create a game property with the same name on the owner of the scene (the main object). Modifications of the property through Python will be applied, but if the property is created from Python they will not.
* As a consecuence of the avobe rule, BGECore Framewrok requests all user-defined uniforms to be prefixed with the name of the filter (in order to avoid name collisions). E.j: Vignetting_colorR

The following template can be used:

.. code-block:: c

	uniform sampler2D bgl_RenderedTexture;

	uniform FilterName_variableName;
	uniform FilterName_variableNameTwo;
	//More...
	
	const float tolerance = 0.6;
	//More...
	
	void main(void)
	{
		//More...
		gl_FragColor = vec4(1.0); //Or any other vec4 structure.
	}