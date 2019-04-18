import os
import stat  # defines constants for chmod
'''
for path in os.listdir( "./"):
	if os.path.isdir( path):
		#os.chmod( path, stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP)
		print("making directory rwxr-x---", path )
	if os.path.isfile( path):
		#os.chmod( path, stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP)
		print("making file      rw-r-----", path )
		
	
import os, sys
'''
# Assuming /tmp/foo.txt exists and has read/write permissions.
for path in os.listdir( "./"):
	fsize = os.path.getsize(path)
	print(fsize,path)