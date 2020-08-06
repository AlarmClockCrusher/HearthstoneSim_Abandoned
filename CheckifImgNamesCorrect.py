import os
from os import listdir
from os.path import isfile, join
from Code2CardList import *

onlyfiles = []
imageFilepaths = [r"C:\Users\13041\Desktop\Python\HS\Images\Basic",
				r"C:\Users\13041\Desktop\Python\HS\Images\Classic",
				r"C:\Users\13041\Desktop\Python\HS\Images\Shadows",
				r"C:\Users\13041\Desktop\Python\HS\Images\Uldum",
				r"C:\Users\13041\Desktop\Python\HS\Images\Dragons",
				r"C:\Users\13041\Desktop\Python\HS\Images\Outlands",
				r"C:\Users\13041\Desktop\Python\HS\Images\Academy",
				]
cropsFilepaths = [r"C:\Users\13041\Desktop\Python\HS\Crops\Basic",
				r"C:\Users\13041\Desktop\Python\HS\Crops\Classic",
				r"C:\Users\13041\Desktop\Python\HS\Crops\Shadows",
				r"C:\Users\13041\Desktop\Python\HS\Crops\Uldum",
				r"C:\Users\13041\Desktop\Python\HS\Crops\Dragons",
				r"C:\Users\13041\Desktop\Python\HS\Crops\Outlands",
				r"C:\Users\13041\Desktop\Python\HS\Crops\Academy",
				]
for filepath in cropsFilepaths:
	onlyfiles += [f for f in listdir(filepath) if isfile(join(filepath, f))]

	#print(onlyfiles)
	for filename in onlyfiles:
		if filename.endswith(".py") == False:
			typeName = filename.split(".")[0]
			
			classType = typeName2Class(typeName)
			if classType == None:
				print(typeName)
			
			
#print(os.path.exists(""))