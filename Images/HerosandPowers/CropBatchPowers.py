import os
from os import listdir
from os.path import isfile, join

from PIL import Image
#To crop 200x276, use 60, 40, 140, 120
#To crop 286x395, use 88, 60, 198, 170

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
			im1 = im.crop((88, 60, 198, 170))
		im1.save('Crop96x96\\'+filename)
		
#singlefilename = "ArmorUp.png"
#im = Image.open(singlefilename) 
### Size of the image in pixels (size of orginal image) 
#left = 88
#top = 60
#right = 198
#bottom = 170
#im1 = im.crop((left, top, right, bottom)) 
##Image size will be 96x96
#im1.show() 
##im1.save('Crop96x96\\'+singlefilename)