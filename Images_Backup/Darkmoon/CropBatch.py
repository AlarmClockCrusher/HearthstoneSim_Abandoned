import os
from os import listdir
from os.path import isfile, join
import sys

from PIL import Image
#To crop 200x271, use 52, 42, 148, 138  Crop 96x96
#To crop 286x395, use 83, 70, 203, 190  Crop 120x120
#To crop 300x454, use 80, 90, 220, 230 Crop 140x140
#To crop 300x407, use 85, 50, 225, 190 Crop 140x140
#To crop 375x518, use 
#filepath = "."
#onlyfiles = [f for f in listdir(filepath) if isfile(join(filepath, f))]
#print(onlyfiles)
#for filename in onlyfiles:
#	if filename.endswith(".py") == False:
#		im = Image.open(filename)
#		im1 = im.crop((93, 90, 258, 255)) 
#		im1.save('Crops\\'+filename)

singlefilename = sys.argv[1]
im = Image.open(singlefilename) 
im1 = im.crop((95, 90, 260, 255)) #102, 80, 257, 235
#im1.show() 
im1.save('Crops\\'+singlefilename)