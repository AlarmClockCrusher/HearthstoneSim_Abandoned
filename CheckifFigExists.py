import os
from os import listdir
from os.path import isfile, join
from Code2CardList import *
from CardPools import cardPool


#filepath = r"C:\Users\13041\Desktop\Python\HS_newGUI\Images\Outlands\For96x96"
#onlyfiles = [f for f in listdir(filepath) if isfile(join(filepath, f))]

def checkFigExistence():
	for key, value in cardPool.items():
		filePath = ''
		if "__" in value.__name__:
			cardName = value.__name__.split('_')[0]
			filepath = "Images\\%s\\%s.png"%(key.split('~')[0], cardName)
		else:
			filepath = "Images\\%s\\%s.png"%(key.split('~')[0], value.__name__)
			
		if not os.path.exists(filepath):
			print("No image for", value.__name__, filePath, os.path.exists(filepath), )
			
		if key != value.index:
			print("Index and card index doesn't match: ", value)
			
			
if __name__ == "__main__":
	checkFigExistence()