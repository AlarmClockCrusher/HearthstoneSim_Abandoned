from hearthstone import deckstrings
import json
import re
import string
from CardIndices import *
import sys

j = json.loads(open("cards.collectible.json", "r", encoding="utf-8").read())

def getCardnameFromDbf(id):
	for each in j:
		if each["dbfId"] == id:
			return each["name"]
			
def decode_deckstring(s):
	deckTuple = deckstrings.parse_deckstring(s)[0]
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
	
def format_str(s):
	punc = "!#$%&'()*+-./:;<=>?@\^_`{|}~"
	for i in range(len(punc)):
		s = s.replace(punc[i], "")
	return s

if __name__ == "__main__":
	code = sys.argv[1]
	deck = decode_deckstring(code)
	print(deck)