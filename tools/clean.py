#####################################
#		BGECore Framework - Cleaning tool
#	
#Usage: python clean.py ../template
#
#Description:
#Cleans the game directory of ".pyc" and .blend copies.
#####################################
	
	
import os, sys, shutil
from fnmatch import fnmatch

root = sys.argv[1]
patterns = "*.pyc", "*.blend1"

datadir = os.path.join(root, "data")
if not os.path.isdir(datadir):
	print("Invalid directory, it is not the root of a BGECore Framework game directory.")
	sys.exit(0)
	
flistx = []
for path, subdirs, files in os.walk(datadir):
	for name in files:
		for pattern in patterns:
			if fnmatch(name, pattern):
				flistx.append(os.path.join(path, name))
		
rmt = []
flist = []
for i, path in enumerate(flistx):
	x = path.find("__pycache__")
	if x > 0:
		tr = path[:x+len("__pycache__")]
		if tr not in rmt: rmt.append(tr)
	else: flist.append(path)
		
for path in rmt:
	shutil.rmtree(path)
	print("Remove: ", path)
	
for path in flist:
	os.remove(path)
	print("Remove: ", path)
	
if len(flist) == 0 and len(rmt) == 0:
	print("Directory already clean.")
		
		