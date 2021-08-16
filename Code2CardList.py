from hearthstone import deckstrings
import json
#import re
import string
from CardPools import *

cardType2jsonType = {"Minion": "MINION", "Spell": "SPELL", "Weapon": "WEAPON", "Hero": "HERO"}

json_Collectibles = json.loads(open("cards.collectible.json", "r", encoding="utf-8").read())
json_Uncollectible = json.loads(open("cards.json", "r", encoding="utf-8").read())

def typeName2Class(typename):
	try:
		if typename.startswith("TransferStudent"): value = next(value for value in cardPool.values() if value.name == "Transfer Student" and "Uncollectible" not in value.index)
		else: value = next(value for value in cardPool.values() if value.__name__ == typename)
		return value
	except:
		print(typename, " not found")
		return None
		
def cardName2Class(cardName):
	for value in cardPool.values():
		if value.name == cardName and "~Uncollectible" not in value.index:
			return value
	print(cardName, " not found")
	return None
	
def parseDeckCode(s, hero, Class2HeroDict):
	deck, deckCorrect, hero = [], False, hero
	if s:
		try:
			if s.startswith("names||"):
				s = s.split('||')[1:]
				deck = [cardName2Class(name.strip()) for name in s if name]
			else: deck = decode_deckstring(s)
			deckCorrect = all(obj is not None for obj in deck)
		except:
			print("Parsing encountered mistake")
			pass
	else: deckCorrect = True
	if deckCorrect:
		for card in deck:
			if card.Class != "Neutral" and ',' not in card.Class:
				hero = Class2HeroDict[card.Class]
				break
	return deck, deckCorrect, hero
	
def getCardnameFromDbf(id):
	for cardInfo in json_Uncollectible:
		if cardInfo["dbfId"] == id:
			return cardInfo["name"]
			
def decode_deckstring(s, to="List"):
	deckTuple = deckstrings.parse_deckstring(s)[0]
	if to == "string":
		deckList = "["
		for each in deckTuple:
			#each is a tupel (dbfid, number of cards in the deck)
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
	for cardInfo in json_Uncollectible:
		words = cardType.index.split('~')
		jsonName, cardName = cardInfo["name"], cardType.name
		isCollectibleinJson, isCollectibleinType = "collectible" in cardInfo, "Uncollectible" not in cardType.index
		jsonType, translatedType = cardInfo["type"], cardType2jsonType[words[2]]
		if jsonName == cardName and cardInfo["set"] == words[0]:
			possibleCards.append((cardName, isCollectibleinJson, isCollectibleinType, jsonType, translatedType))
			if isCollectibleinJson == isCollectibleinType and jsonType == translatedType:
				return cardInfo
	return possibleCards
	
	
def checktheStatsofCards():
	raceAllCapDict = {"Elemental":"ELEMENTAL", "Mech": "MECHANICAL", "Demon": "DEMON", "Murloc": "MURLOC",
						"Dragon": "DRAGON", "Beast": "BEAST", "Pirate": "PIRATE", "Totem": "TOTEM"}
	exceptionList = []
	for key, value in cardPool.items():
		if key.startswith("SV_"): continue
		try:
			words = key.split('~')
			cardInfo = getAnyCardInfofromType(value) #Get the name
			if isinstance(cardInfo, list):
				print("Didn't find a match of the card {}/{}".format(value.__name__, value.name))
				print("Possible matches")
				print(cardInfo)
				continue
			if not (int(cardInfo["cost"]) == value.mana == int(words[3])):
					print(value, " has a wrong mana {}|{}|{}".format(cardInfo["cost"], value.mana, int(words[3])))
		except Exception as e:
			print("stopped at step 1 {}".format(value, e))
			continue
		#Will check the type of the cards (Minion, Spell, etc)
		cardType = words[2]
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
				elif value.race or words[6]: #If card doesn't have race
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
			else: #Spell
				if value.name != words[5]:
					print(value, " has a wrong name", cardInfo["name"], value.name, words[5])
					
		except Exception as e:
			#print("When checking ", value, e)
			exceptionList.append((value, cardType, e))
	return exceptionList
			
if __name__ == "__main__":
#	code = sys.argv[1]
#	deck = decode_deckstring(code, to="List")
#	print(deck)
	exceptionList = checktheStatsofCards()
	#Check if all collectible cards are matched in the json
	for key, value in cardPool.items():
		if "Uncollectible" not in key:
			for each in json_Collectibles:
				if each["name"] == value.name:
					name_withoutPunctuations = each["name"].translate(str.maketrans('', '', string.punctuation))
					name_NoSpace = name_withoutPunctuations.replace(' ', '')
					className = typeName2Class(name_NoSpace)
					if className != value: print(value)
					break
					
					
	with open("CardPoolCheck.txt", 'w') as file:
		for exception in exceptionList:
			file.write("{}".format(exception))