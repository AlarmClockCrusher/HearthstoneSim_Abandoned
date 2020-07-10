import os
from os import listdir
from os.path import isfile, join

from PIL import Image
#To crop 200x271, use 52, 42, 148, 138  Crop 96x96
#To crop 286x395, use 83, 70, 203, 190  Crop 120x120
#To crop 300x454, use 80, 90, 220, 230 Crop 140x140

#filepath = "."
#onlyfiles = [f for f in listdir(filepath) if isfile(join(filepath, f))]
#print(onlyfiles)
#for filename in ["DruidoftheClaw_Charge.png", "DruidoftheClaw_Taunt.png","DruidoftheClaw_Both.png",]:
#	if filename.endswith(".py") == False:
#		im = Image.open(filename)
#		im1 = im.crop((83, 70, 203, 190)) 
#		im1.save('Crop96x96\\'+filename)

singlefilename = "Spellbender.png"
im = Image.open(singlefilename)
## Size of the image in pixels (size of orginal image) 
im1 = im.crop((83, 70, 203, 190))
#Image size will be 96x96
im1.show()
im1.save("Crop96x96\\"+singlefilename)