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
				result1 = cardName.translate(str.maketrans('', '', string.punctuation))
				result2 = result1.replace(' ', '')
				deckList += result2+', '
				
		deckList += ']'
		return deckList
	else: #to == "List"
		deckList = []
		for each in deckTuple:
			#print(each) #(cardID, number of cards in the deck)
			for i in range(each[1]):
				cardName = getCardnameFromDbf(each[0])
				result1 = cardName.translate(str.maketrans('', '', string.punctuation))
				result2 = result1.replace(' ', '')
				className = typeName2Class(result2)
				deckList.append(className)
		return deckList
		
if __name__ == "__main__":
	code = sys.argv[1]
	deck = decode_deckstring(code, to="List")
	print(deck)