import os
from os import listdir
from os.path import isfile, join
from Code2CardList import *
from CardPools import cardPool

#filepath = r"C:\Users\13041\Desktop\Python\HS_newGUI\Images\Outlands\For96x96"
#onlyfiles = [f for f in listdir(filepath) if isfile(join(filepath, f))]


for key, value in cardPool.items():
	if "Mutable" in value.__name__:
		cardName = value.__name__.split('_')[0]
		filepath = "Images\\%s\\%s.png"%(key.split('~')[0], cardName)
	else:
		filepath = "Images\\%s\\%s.png"%(key.split('~')[0], value.__name__)
		
	if os.path.exists(filepath) == False:
		print(value.__name__)
		
	if key != value.index:
		print("Index and card index doesn't match: ", value)
	stats = key.split('~')
	if stats[1] != value.Class:
		print("Class and card index doesn't match: ", value)
	if int(stats[3]) != value.mana:
		print("Mana and card index doesn't match: ", value)
	#"Dragons~Paladin~Minion~7~7~7~None~Lightforged Crusader~Battlecry"
	if "~Minion~" in key:
		if int(stats[4]) != value.attack:
			print("Attack and card index doesn't match: ", value)
		if int(stats[5]) != value.health:
			print("Health and card index doesn't match: ", value)
		if stats[6] != "None" and stats[6] != value.race:
			print("Race and card index doesn't match: ", value)
		if stats[7] != value.name:
			print("Name and card index doesn't match: ", value)
	#"Uldum~Rogue~Weapon~2~3~2~Mirage Blade~Uncollectible"
	elif "~Weapon~" in key:
		if int(stats[4]) != value.attack:
			print("Attack and card index doesn't match: ", value)
		if "~Minion~" in key and int(stats[5]) != value.durability:
			print("Durability and card index doesn't match: ", value)
		if stats[6] != value.name:
			print("Name and card index doesn't match: ", value)
	#"Classic~Hunter~Spell~5~Explosive Shot"
	#"Dragons~Priest~Hero Card~7~Galakrond, the Unspeakable~Battlecry~Legendary"
	else:
		if stats[4] != value.name:
			print("Name and card index doesn't match: ", value)
		if hasattr(value, "attack"):
			print("Type of value is wrong:", value)








