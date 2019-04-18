#Import os module
import os
#Import math and time module
import math,time

#Set listing start location
path = os.getcwd()
unit = None
fsize = None

listInDirectory = os.listdir(path)
def getmode(path):
	if os.access(path, os.F_OK):
	
		if os.access(path, os.R_OK):
			fileread = 'r'
		else: 
			fileread = '-'

		if os.access(path, os.W_OK):
			filewrite = 'w'
		else:
			filewrite = '-'

		if os.access(path, os.X_OK):
			filexe = 'x'
		else:
			filexe = '-'
			
		if os.path.isfile( path):
			filetype = '-'
		elif os.path.isdir( path):
			filetype = 'd'
			
		mode = filetype+fileread+filewrite+filexe
	return mode

def convertFileSize(file):
	fsize = os.path.getsize(file)
	# Convert file size to MB, KB or Bytes
	'''
	if (fsize > 1024 * 1024):
		fsize = math.ceil(fsize / (1024 * 1024))
		unit = "MB"
	elif (fsize > 1024):
		fsize = math.ceil(fsize / 1024)
		unit = "KB"
	else:
		fsize = fsize
		unit = "B"
	'''
	return fsize #,unit


print(listInDirectory)
modelist = []
modTime = []
fileSize = []

for item in listInDirectory:

	mtime = time.strftime("%X %x", time.gmtime(os.path.getmtime(item)))
	#mode = getmode(item)
	if os.path.isfile(item):
		mode = '-a----'
		fsize = convertFileSize(item)
		# Print file attributes
		#print('\t{:2s} {:18s}{:8d} {:2s} {:15.15s}'.format(mode,mtime,fsize,unit,item))
	else:
		mode = 'd-----'
		# Print file attributes
		#print('\t{:2s} {:8s} {:15.15s}'.format(mode,mtime, item))
	modelist.append(mode)
	modTime.append(mtime)
	fileSize.append(fsize)

print(modelist)
print(modTime)
print(fileSize)