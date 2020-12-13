import os
from os import listdir
from os.path import isfile, join
from Code2CardList import *
from CardPools import cardPool

folderNameTable = {"Basic":"Basic", "Classic": "Classic",
					"GVG": "Pre_Dalaran", "Kobolds": "Pre_Dalaran", "Boomsday": "Pre_Dalaran",
					"Shadows": "Shadows", "Uldum": "Uldum", "Dragons": "Dragons", "Galakrond": "Galakrond",
					"DHInitiate": "DHInitiate", "Outlands": "Outlands", "Academy": "Academy", "Darkmoon": "Darkmoon",
					}
					
#filepath = r"C:\Users\13041\Desktop\Python\HS_newGUI\Images\Outlands\For96x96"
#onlyfiles = [f for f in listdir(filepath) if isfile(join(filepath, f))]

def checkFigExistence():
	for key, value in cardPool.items():
		if "Mutable" in value.__name__:
			cardName = value.__name__.split('_')[0]
			filepath = "Crops\\%s\\%s.png"%(folderNameTable[key.split('~')[0] ], cardName)
		elif "Hero Card" in value.index:
			filepath = "Crops\\HerosandPowers\\%s.png"%value.__name__
		else:
			filepath = "Crops\\%s\\%s.png"%(folderNameTable[key.split('~')[0] ], value.__name__)
			
		if os.path.exists(filepath) == False:
			print("No crop for", value.__name__)
			
		if key != value.index:
			print("Index and card index doesn't match: ", value)
			
	for key, value in cardPool.items():
		if "Mutable" in value.__name__:
			cardName = value.__name__.split('_')[0]
			filepath = "Images\\%s\\%s.png"%(folderNameTable[key.split('~')[0] ], cardName)
		elif "Hero Card" in value.index:
			filepath = "Images\\HerosandPowers\\%s.png"%value.__name__
		else:
			filepath = "Images\\%s\\%s.png"%(folderNameTable[key.split('~')[0] ], value.__name__)
			
		if os.path.exists(filepath) == False:
			print("No image for", value.__name__)
			
		if key != value.index:
			print("Index and card index doesn't match: ", value)
			
			
if __name__ == "__main__":
	checkFigExistence()