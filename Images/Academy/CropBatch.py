import os
from os import listdir
from os.path import isfile, join

from PIL import Image
#To crop 200x271, use 52, 42, 148, 138  Crop 96x96
#To crop 286x395, use 83, 70, 203, 190  Crop 120x120
#To crop 300x454, use 80, 90, 220, 230 Crop 140x140

#To crop 375x518 minion, use 100, 90, 270, 260 Crop 140x140(Download from HS official gallery)
#To crop 375x518 weapon, use 105, 85, 275, 255 Crop 140x140(Download from HS official gallery)
#To crop 375x518 spell, use 100, 85, 275, 260 Crop 140x140(Download from HS official gallery)
#To crop 300x414 minion, use 80, 75, 215, 210 Crop 140x140
#To crop 300x414 weapon, use 80, 60, 225, 205 Crop 140x140
#
#filepath = "."
#onlyfiles = [f for f in listdir(filepath) if isfile(join(filepath, f))]
#print(onlyfiles)
#for filename in ["DruidoftheClaw_Charge.png", "DruidoftheClaw_Taunt.png","DruidoftheClaw_Both.png",]:
#	if filename.endswith(".py") == False:
#		im = Image.open(filename)
#		im1 = im.crop((83, 70, 203, 190)) 
#		im1.save('Crop96x96\\'+filename)

singlefilename = "WretchedTutor.png"
im = Image.open(singlefilename)
## Size of the image in pixels (size of orginal image) 
im1 = im.crop((105, 75, 270, 240))
#Image size will be 96x96
im1.show()
im1.save("Crops\\"+singlefilename)