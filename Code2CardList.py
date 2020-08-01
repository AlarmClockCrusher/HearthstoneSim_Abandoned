from hearthstone import deckstrings
import json
import re
import string
from CardPools import *
import sys

j = json.loads(open("cards.collectible.json", "r", encoding="utf-8").read())
def typeName2Class(typename):
	for value in cardPool.values():
		if value.__name__ == typename:
			return value
	print(typename, " not found")
	return None
	
def cardName2Class(cardName):
	for value in cardPool.values():
		if value.name == cardName:
			return value
	print(cardName, " not found")
	return None
	
def getCardnameFromDbf(id):
	for each in j:
		if each["dbfId"] == id:
			return each["name"]
			
def decode_deckstring(s, to="List"):
	deckTuple = deckstrings.parse_deckstring(s)[0]
	if to == "string":
		deckList = "["
		for each in deckTuple:
			#print(each) #(cardID, number of cards in the deck)
			for i in range(each[1]):
				cardName = getCardnameFromDbf(each[0])
				name_withoutPunctuations = cardName.translate(str.maketrans('', '', string.punctuation))
				name_NoSpace = name_withoutPunctuations.replace(' ', '')
				deckList += name_NoSpace+', '
				
		deckList += ']'
		return deckList
	else: #to == "List"
		deckList = []
		for each in deckTuple:
			#print(each) #(cardID, number of cards in the deck)
			for i in range(each[1]):
				cardName = getCardnameFromDbf(each[0])
				name_withoutPunctuations = cardName.translate(str.maketrans('', '', string.punctuation))
				name_NoSpace = name_withoutPunctuations.replace(' ', '')
				className = typeName2Class(name_NoSpace)
				deckList.append(className)
		return deckList
		
if __name__ == "__main__":
#	code = sys.argv[1]
#	deck = decode_deckstring(code, to="List")
#	print(deck)

	#Check if card names are matched in the json
	#for key, value in cardPool.items():
	#	if "Uncollectible" not in key:
	#		nameExists = False
	#		for each in j:
	#			if each["name"] == value.name:
	#				nameExists = True
	#				break
	#		if not nameExists: print(value)
			
	#Check if all collectible cards are matched in the json
	for key, value in cardPool.items():
		if "Uncollectible" not in key:
			for each in j:
				if each["name"] == value.name:
					name_withoutPunctuations = each["name"].translate(str.maketrans('', '', string.punctuation))
					name_NoSpace = name_withoutPunctuations.replace(' ', '')
					className = typeName2Class(name_NoSpace)
					if className != value: print(value)
					break
					