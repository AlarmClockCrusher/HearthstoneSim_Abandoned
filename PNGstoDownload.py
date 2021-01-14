from Darkmoon import *
import json

j = json.loads(open("cards.json", "r", encoding="utf-8").read())
with open("Params.txt", 'w') as output:
	for key, cardtype in Darkmoon_Indices.items():
		cardTypeName
		if "Corrupt" in cardtype.__name__:
			dbfId = next((cardInfo for cardInfo in j if cardInfo["name"] == cardtype.name and cardInfo["set"] == "DARKMOON_FAIRE" \
													and ("mechanics" in cardInfo and "CORRUPT" in cardInfo["mechanics"])), None)
		else:
			dbfId = next((cardInfo for cardInfo in j if cardInfo["name"] == cardtype.name and cardInfo["set"] == "DARKMOON_FAIRE" \
													and ("mechanics" not in cardInfo or "CORRUPT" not in cardInfo["mechanics"])), None)
													
		if dbfId: output.write("")
	bitsadmin /transfer job /download /priority normal https://raw.githubusercontent.com/AlarmClockCrusher/HearthstoneSim/master/CardTypes.py %cd%\CardTypes.py