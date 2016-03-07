.. _filter2D:

Filters 2D - GLSL Shaders
=================================
Filters are GLSL shaders, a post-render phase where the image is edited to mod it in any way. Here you can find a list of the default BGECore 2D Filters and a tutorial into how to make your own GLSL shaders.

.. note:: This module is standalone and can be used outside BGECore Framework by simple coping the ``data/core/glsl`` folder in the main game `.blend` directory.

Standard BGECore Shaders
-----------------------------------
Standard shaders can be used directly creatig an instance of a 2DFilter subclass. A shortcut to use them is the namescpace ``core.utils.filter2d``. Example:

.. code-block:: python

	from core import behavior, utils

	class EndOfTheWorld(behavior.Scene):
		def init(self):
			self.vignetting = utils.filter2D.Vignetting(colorR = 1.0)
			[...]
		
		def onKeyRelease(self, keys):
			if key.E in keys: self.vignetting.colorR = 0

.. automodule:: core.glsl
	:members:

Installing or creating custom shaders
-----------------------------------------------
BGECore Framewrok uses the directory ``data/core/glsl`` for GLSL shaders. Such shaders must use the extension **.filter2D** when disgned to be used as filters. If you have the source code of a shader, moving it there and creating a 2DFilter subclass should be enough to make it work, however shaders must be BGE complaint so you may need a little understanding of GLSL before you can use third party shaders not designed specifically for Blender.

The shaders are coded in GLSL, a language very similar to C that is compiled by BGE at runtime (when loading the shader). Depending on the version of Blender you're using you must guarantee that your shader can work with a min version of OpenGL.

.. note:: Currently only float unifoms are supported.

When porting a third party shader it's important to look at the following things:

* It must be a fragment shader, meaning that in the shader at some point the variable **gl_FragColor** is used.
* It should have a **sampler2D uniform**, you need to rename it to *bgl_RenderedTexture* to make it work in BGE.
* It must have a **main** method.
* Build-in types that are predefined macros or constants can be converted to uniforms if you want to modify them in realtime.
* For organitzation reasons when using game properties to control unifoms (deprecated), all uniforms must be prefixed with the name of the filter (in order to avoid name collisions). E.j: `Vignetting_colorR`

The following template can be used (FilterName.filter2D):

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
	
Once you have the shader done, you must create the documentation and specify the initialization values. The documentation is writted for ReST for Sphinx. The name of the class must be the filename of the shader. The class attributes will define the uniforms. Attributes defined in ``__init__`` won't be taken as uniforms. You can create new methods to use with complex shaders. Example:

.. code-block:: python

	from filter2D import Filter2D

	class FilterName(Filter2D):
		"""
		A filter2D subclass.
		
		.. attribute:: variableName
			
			This does something.
			
		[...]
		"""
		
		variableName = 0.0
		variableNameTwo = 6.182
	

Trublesome
-----------------------------------------------
The following list contains known features that break on some computers:

* Using implicit conversion of types, like ``float x = 1.0; x /= 2;``. Instead use explicit conversion ``x = x / 2.0``.