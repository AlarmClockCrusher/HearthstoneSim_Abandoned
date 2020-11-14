import os
from os import listdir
from os.path import isfile, join

filepath = r"C:\Users\13041\Desktop\Python\HS_newGUI\Images\Outlands\bunch"
onlyfiles = [f for f in listdir(filepath) if isfile(join(filepath, f))]

print(onlyfiles)
for filename in onlyfiles:
	if name2Class():
		os.remove(filename)

#print(os.path.exists(""))