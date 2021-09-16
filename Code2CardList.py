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
		if typename.startswith("TransferStudent"): value = next(value for value in cardPool if value.name == "Transfer Student" and "Uncollectible" not in value.index)
		else: value = next(value for value in cardPool if value.__name__ == typename)
		return value
	except:
		print(typename, " not found")
		return None
		
def cardName2Class(cardName):
	for card in cardPool:
		if card.name == cardName and "~Uncollectible" not in card.index:
			return card
	print(cardName, " not found")
	return None
	
def parseDeckCode(deckString, Class, Class2HeroDict, defaultDeck=None):
	deck, deckCorrect, hero = [], False, Class2HeroDict[Class]
	if deckString:
		try:
			if deckString.startswith("names||"):
				names = deckString.split('||')[1:]
				deck = [cardName2Class(name.strip()) for name in names if name]
			else: deck = decode_deckstring(deckString)
			deckCorrect = all(obj is not None for obj in deck)
		except Exception as e: print("Parsing encountered error", e)
	else:
		deck, deckCorrect = defaultDeck, True
	if deckCorrect:
		Class = next((card.Class for card in deck if card.Class != "Neutral" and ',' not in card.Class), None)
		if Class: hero = Class2HeroDict[Class]
	#print("Result of parse deck code: \nDECK CORRECT? {}  HERO {}\n".format(deckCorrect, hero.name), deck)
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
	for card in cardPool:
		if card.index.startswith("SV_"): continue
		try:
			words = card.index.split('~')
			cardInfo = getAnyCardInfofromType(card) #Get the name
			if isinstance(cardInfo, list):
				print("Didn't find a match of the card {}/{}".format(card.__name__, card.name))
				print("Possible matches")
				print(cardInfo)
				continue
			if not (int(cardInfo["cost"]) == card.mana == int(words[3])):
					print(card, " has a wrong mana {}|{}|{}".format(cardInfo["cost"], card.mana, int(words[3])))
		except Exception as e:
			print("stopped at step 1 {}".format(card, e))
			continue
		#Will check the type of the cards (Minion, Spell, etc)
		cardType = words[2]
		try:
			if cardType == "Minion":
				if card.name != words[7]:
					print(card, " has a wrong name\njson\t\t{} \nfrom type\t{} \nfrom index\t{}".format(cardInfo["name"], card.name, words[7]))
				
				if not (cardInfo["attack"] == card.attack == int(words[4]) \
						and cardInfo["health"] == card.health == int(words[5])):
					print(card, " has a wrong stat:")
					print(card, "Attack: {}|{}|{} Health: {}|{}|{}".format(cardInfo["attack"], card.attack, int(words[4]), cardInfo["health"], card.health, int(words[5])))
				if "race" in cardInfo:
					if not(card.race and card.race == words[6]):
						print(card, " race doesn't match index")
						print(card.race, words[6])
					if cardInfo["race"] == "All":
						if card.race != "Elemental,Mech,Demon,Murloc,Dragon,Beast,Pirate,Totem":
							print(card, " race should be 'Elemental,Mech,Demon,Murloc,Dragon,Beast,Pirate,Totem'")
					elif raceAllCapDict[card.race] !=cardInfo["race"]:
						print(card, " race doesn't match json")
						print(raceAllCapDict[card.race], cardInfo["race"])
				elif card.race or words[6]: #If card doesn't have race
					print(card, " shouldn't have race", card.race, words[6])
				#Check the card.indexWords of the minion
				if card.card.indexWord:
					card.indexWords = card.card.indexWord.split(',')
					for word in card.indexWords:
						if word not in ["Taunt", "Divine Shield", "Stealth", "Lifesteal", "Spell Damage", "Windfury", "Mega Windfury", "Charge", 
										"Poisonous", "Rush", "Echo", "Reborn",]:
							print(card, " card.indexWord input is wrong {}.".format(word))
						if word not in card.index:
							print(card, "card.indexWord and index don't match")
			elif cardType == "Weapon":
				if card.name != words[6]:
					print(card, " has a wrong name", cardInfo["name"], card.name, words[6])
					
				if not(cardInfo["attack"] == card.attack == int(words[4]) \
						and cardInfo[""] == card.health == int(words[5])):
					print(card, " has a wrong stat")
			else: #Spell
				if card.name != words[5]:
					print(card, " has a wrong name", cardInfo["name"], card.name, words[5])
					
		except Exception as e:
			#print("When checking ", card, e)
			exceptionList.append((card, cardType, e))
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