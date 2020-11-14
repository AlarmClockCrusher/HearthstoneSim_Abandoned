from hearthstone import deckstrings
import json
import re
import string
from CardPools import *
import sys

cardType2jsonType = {"Minion": "MINION", "Spell": "SPELL", "Weapon": "WEAPON", "Hero": "HERO"}
Pack2jsonSet = {"Basic": "CORE", "Classic": "EXPERT1", 
				"Shadows": "DALARAN", "Uldum": "ULDUM", "Dragons": "DRAGONS", "Galakrond": "YEAR_OF_THE_DRAGON",
				"DHInitiate": "DEMON_HUNTER_INITIATE", "Outlands": "BLACK_TEMPLE", "Academy": "SCHOLOMANCE", "Darkmoon": "DARKMOON_FAIRE",
				}
j = json.loads(open("cards.collectible.json", "r", encoding="utf-8").read())
k = json.loads(open("cards.json", "r", encoding="utf-8").read())

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
	for cardInfo in j:
		if cardInfo["dbfId"] == id:
			return cardInfo["name"]
	
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
		
def getAnyCardInfofromType(cardType):
	possibleCards = []
	for cardInfo in k:
		words = cardType.index.split('~')
		jsonName, cardName = cardInfo["name"], cardType.name
		jsonSet, translatedSet = cardInfo["set"], Pack2jsonSet[words[0]]
		isCollectibleinJson, isCollectibleinType = "collectible" in cardInfo, "Uncollectible" not in cardType.index
		jsonType, translatedType = cardInfo["type"], cardType2jsonType[words[2]]
		if jsonName == cardName:
			possibleCards.append((cardName, jsonSet, translatedSet, isCollectibleinJson, isCollectibleinType, jsonType, translatedType))
			if jsonSet ==  translatedSet and isCollectibleinJson == isCollectibleinType and jsonType == translatedType:
				return cardInfo
	return possibleCards
	
	
def checktheStatsofCards():
	raceAllCapDict = {"Elemental":"ELEMENTAL", "Mech": "MECHANICAL", "Demon": "DEMON", "Murloc": "MURLOC",
						"Dragon": "DRAGON", "Beast": "BEAST", "Pirate": "PIRATE", "Totem": "TOTEM"}
	exceptionList = []
	for key, value in cardPool.items():
		try:
			if key != value.index:
				print(value, " has a wrong index")
				print(key)
				print(value.index)
			words = key.split('~')
			cardInfo = getAnyCardInfofromType(value) #Get the name
			if isinstance(cardInfo, list):
				print("Didn't find a match of the card {}/{}".format(value.__name__, value.name))
				print("Possible matches")
				print(cardInfo)
			if not (int(cardInfo["cost"]) == value.mana == int(words[3])):
					print(value, " has a wrong mana {}|{}|{}".format(cardInfo["cost"], value.mana, int(words[3])))
			cardType = words[2]
		except Exception as e:
			print("stopped at step 1 {}".format(value, e))
			continue
		try:
			if cardType == "Minion":
				if value.name != words[7]:
					print(value, " has a wrong name\njson\t\t{} \nfrom type\t{} \nfrom index\t{}".format(cardInfo["name"], value.name, words[7]))
				
				if not (cardInfo["attack"] == value.attack == int(words[4]) \
						and cardInfo["health"] == value.health == int(words[5])):
					print(value, " has a wrong stat:")
					print(value, "Attack: {}|{}|{} Health: {}|{}|{}".format(cardInfo["attack"], value.attack, int(words[4]), cardInfo["health"], value.health, int(words[5])))
				if "race" in cardInfo:
					if not(value.race and value.race == words[6]):
						print(value, " race doesn't match index")
						print(value.race, words[6])
					if cardInfo["race"] == "All":
						if value.race != "Elemental,Mech,Demon,Murloc,Dragon,Beast,Pirate,Totem":
							print(value, " race should be 'Elemental,Mech,Demon,Murloc,Dragon,Beast,Pirate,Totem'")
					elif raceAllCapDict[value.race] !=cardInfo["race"]:
						print(value, " race doesn't match json")
						print(raceAllCapDict[value.race], cardInfo["race"])
				elif value.race or words[6] != "None": #If card doesn't have race
					print(value, " shouldn't have race", value.race, words[6])
				#Check the keyWords of the minion
				if value.keyWord:
					keyWords = value.keyWord.split(',')
					for word in keyWords:
						if word not in ["Taunt", "Divine Shield", "Stealth", "Lifesteal", "Spell Damage", "Windfury", "Mega Windfury", "Charge", 
										"Poisonous", "Rush", "Echo", "Reborn",]:
							print(value, " keyWord input is wrong {}.".format(word))
						if word not in value.index:
							print(value, "keyWord and index don't match")
			elif cardType == "Weapon":
				if value.name != words[6]:
					print(value, " has a wrong name", cardInfo["name"], value.name, words[6])
					
				if not(cardInfo["attack"] == value.attack == int(words[4]) \
						and cardInfo[""] == value.health == int(words[5])):
					print(value, " has a wrong stat")
			else:
				if value.name != words[4]:
					print(value, " has a wrong name", cardInfo["name"], value.name, words[4])
					
		except Exception as e:
			#print("When checking ", value, e)
			exceptionList.append((value, e))
	return exceptionList
			
if __name__ == "__main__":
#	code = sys.argv[1]
#	deck = decode_deckstring(code, to="List")
#	print(deck)
	exceptionList = checktheStatsofCards()
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
					
					
	with open("CardPoolCheck.txt", 'w') as file:
		for exception in exceptionList:
			file.write("{}".format(exception))