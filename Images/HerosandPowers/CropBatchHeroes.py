import os
from os import listdir
from os.path import isfile, join

from PIL import Image
#To crop 200x276, use 60, 40, 140, 120
#To crop 286x395, use 45, 60, 215, 230

filepath = "."
onlyfiles = [f for f in listdir(filepath) if isfile(join(filepath, f))]
print(onlyfiles)
for filename in onlyfiles:
	if filename.endswith(".py") == False:
		im = Image.open(filename)
		width, height = im.size
		if width == 200:
			im1 = im.crop((60, 40, 140, 120))
		elif width == 286:
			im1 = im.crop((45, 60, 215, 230))
		im1.save('Crop\\'+filename)
		
#singlefilename = "Illidan.png"
#im = Image.open(singlefilename) 
### Size of the image in pixels (size of orginal image) 
#left = 45
#top = 60
#right = 215
#bottom = 230
#im1 = im.crop((left, top, right, bottom)) 
##Image size will be 96x96
#im1.show() 
##im1.save('Crop96x96\\'+singlefilename)