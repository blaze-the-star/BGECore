You can get the documentation online at: http://bgecore.royalwebhosting.net/
(Mirror) http://bgecore.16mb.com/

To generate/update the documentation you need the following dependences:

Python3 (Not BGE-Python, but the original): https://www.python.org/downloads/
Sphinx: "pip install sphinx" or http://sphinx-doc.org/install.html
Graphviz: http://www.graphviz.org/Download_windows.php (Do not use pip)

Make sure that Python(Python3) and Dot (Graphviz) are on the system path or can be executed form anywhere in the system command line.

You can make the documentation executing "make" on this directory from the terminal or executing the"make.bat" file on Windows.

The documentation generated using the files on this folder and the "core" library found inside "template/data/core". If you had renamed "template" with the game of your game you can still make documentation by editing the "source/conf.py" file line 35 with the new path.