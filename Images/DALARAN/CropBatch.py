import os
from os import listdir
from os.path import isfile, join

from PIL import Image
#To crop 200x271, use 52, 42, 148, 138  Crop 96x96
#To crop 286x395, use 83, 70, 203, 190  Crop 120x120
#To crop 300x454, use 80, 90, 220, 230 Crop 140x140
#To crop 300x407, use 85, 50, 225, 190 Crop 140x140
#filepath = "."
#onlyfiles = [f for f in listdir(filepath) if isfile(join(filepath, f))]
#print(onlyfiles)
#for filename in onlyfiles:
#for filename in ["GoldenKolbold.png", "ZarogsCrown.png", "WondrousWand.png",]:
#	if filename.endswith(".py") == False:
#		im = Image.open(filename)
#		im1 = im.crop((85, 50, 225, 190)) 
#		im1.save('Crop96x96\\'+filename)

singlefilename = "AssassinsContract.png"
im = Image.open(singlefilename)
## Size of the image in pixels (size of orginal image)
im1 = im.crop((83, 70, 203, 190))
#Image size will be 96x96
im1.show()
im1.save("Crop96x96\\"+singlefilename)