import os
from os import listdir
from os.path import isfile, join

from PIL import Image

filepath = "."
onlyfiles = [f for f in listdir(filepath) if isfile(join(filepath, f))]
print(onlyfiles)
for filename in onlyfiles:
	if filename.endswith(".py") == False:
		im = Image.open(filename)
		left = 52 #width*0.2
		top = 42 #height*0.9
		right = 148 #width * 0.8
		bottom = 138# height * 0.5
		im1 = im.crop((left, top, right, bottom)) 
		im1.save('Crop96x96\\'+filename)

#im = Image.open("ElvenArcher.png") 
### Size of the image in pixels (size of orginal image) 
#left = 52 #width*0.2
#top = 42 #height*0.9
#right = 148 #width * 0.8
#bottom = 138# height * 0.5
#im1 = im.crop((left, top, right, bottom)) 
##Image size will be 96x96
#im1.show() 
##im1.save("Netherwalker.png")