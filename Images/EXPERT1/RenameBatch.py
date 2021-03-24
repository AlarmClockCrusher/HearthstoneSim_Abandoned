import os
from os import listdir
from os.path import isfile, join

from PIL import Image

filepath = "." #"C:\Users\13041\Desktop\Python\HS_newGUI\Images\Basic"
#onlyfiles = [f for f in listdir(filepath) if isfile(join(filepath, f))]

i = 0
def imageSizeWrong(filename):
	im = Image.open(filename)
	width, height = im.size
	return width != 200 or height != 276
	
#Remove the 
#for filename in onlyfiles:
#	if filename.endswith(".py") == False:
#		filename_new = filename.replace("[hearthstone.gamepedia.com][", 'g')
#		os.rename(filename, filename_new)

def removeSubstringsinFilenames(substring):
	onlyfiles = [f for f in listdir(filepath) if isfile(join(filepath, f))]
	for filename in onlyfiles:
		if filename.endswith(".py") == False:
			filename_new = filename.replace(substring, '')
			os.rename(filename, filename_new)
			
def removeNonLetterCharsinFilenames():
	onlyfiles = [f for f in listdir(filepath) if isfile(join(filepath, f))]
	for filename in onlyfiles:
		if filename.endswith(".py") == False:
			name = filename.split('.')[0]
			filename_new = ""
			filenamehasLetters = False
			for i in range(len(name)):
				if name[i].isalpha():
					filenamehasLetters = True
					filename_new += name[i]
			if filenamehasLetters:
				filename_new += '.png'
				try:
					os.rename(filename, filename_new)
				except: #If the filename_new already exists
					os.remove(filename)
				
				
def removeNonPicFiles():
	onlyfiles = [f for f in listdir(filepath) if isfile(join(filepath, f))]
	for filename in onlyfiles:
		if filename.endswith('.py') == False:
			if filename.endswith('.jpg') == False and filename.endswith('.png') == False:
				os.remove(filename)
				
				
def removeImageswithWrongSize():
	onlyfiles = [f for f in listdir(filepath) if isfile(join(filepath, f))]
	for filename in onlyfiles:
		if filename.endswith(".png") or filename.endswith(".jpg"):
			try:
				if imageSizeWrong(filename):
					os.remove(filename)
			except:
				os.remove(filename)
				
				
				
#removeSubstringsinFilenames('px')
#removeNonPicFiles()
#removeImageswithWrongSize()
#removeNonLetterCharsinFilenames()