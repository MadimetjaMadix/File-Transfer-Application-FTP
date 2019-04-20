import os,time#, string
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

# Assuming /tmp/foo.txt exists and has read/write permissions.
for path in os.listdir( "./"):
	fsize = os.path.getsize(path)
	print(fsize,path)
	
directory_list  = os.listdir( "./")

fileInfo = []
for file in directory_list :
	mtime = time.strftime("%X %x", time.gmtime(os.path.getmtime(file)))
	fsize = str(os.path.getsize(file))
	if os.path.isfile(file):
		mode = '-a----'
	else:
		mode = 'd-----'
	fileInfo = [mode]
	fileInfo.append(mtime)
	fileInfo.append(fsize)
	fileInfo.append(file)
	print(fileInfo)
	[str(x) for x in fileInfo]
	print(fileInfo)
	fileInfo = ','.join(fileInfo)
	print(fileInfo.encode())
	
filename = input(str("Enter file name :  "))
while filename:
	if os.path.isfile(filename):
		print ("File exists")
	else: 
		print ("File doesn't exists")
	filename = input(str("Enter file name :  "))
	'''
	
path = os.getcwd()
print(path)
os.chdir("..")
path = os.getcwd()
print(path)
	
	