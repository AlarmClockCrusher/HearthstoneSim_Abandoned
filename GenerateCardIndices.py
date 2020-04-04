from CardIndices import *
import copy

cardPool = {}
cardPool.update(Basic_Indices)
cardPool.update(Classic_Indices)

cardPool.update(Shadows_Indices)
cardPool.update(Uldum_Indices)
cardPool.update(Dragons_Indices)
cardPool.update(Galakrond_Indices)
cardPool.update(DemonHunterInit_Indices)

cardPool.update(Outlands_Indices)

filename = "CardIndices_Asist.txt"

#Need MinionswithRace, MinionsofCost
#ClassicCards, NeutralMinions, LegendaryMinions
MinionswithRace = {"Beast": {}, "Demon": {}, "Dragon": {}, "Elemental":{},
				"Murloc": {}, "Mech": {}, "Pirate":{}, "Totem": {}}
MinionsofCost = {}
ClassCards = {}
NeutralMinions = {}
LegendaryMinions = {}
#The Galakrond cards can't be in the RNGPools
keys, values = list(cardPool.keys()), list(cardPool.values())
for key, value in zip(keys, values):
	if "Galakrond" in value.description or "Invoke" in value.description or "invoke" in value.description:
		del cardPool[key]
	if value.description.startswith("Quest: "):
		del cardPool[key]
		
for key, value in cardPool.items(): #Fill MinionswithRace
	if "~Uncollectible" not in key:
		if "~Beast~" in key:
			MinionswithRace["Beast"][key] = value
		if "~Demon~" in key:
			MinionswithRace["Demon"][key] = value
		if "~Dragon~" in key:
			MinionswithRace["Dragon"][key] = value
		if "~Elemental~" in key:
			MinionswithRace["Elemental"][key] = value
		if "~Murloc~" in key:
			MinionswithRace["Murloc"][key] = value
		if "~Mech~" in key:
			MinionswithRace["Mech"][key] = value
		if "~Pirate~" in key:
			MinionswithRace["Pirate"][key] = value
		if "~Totem~" in key:
			MinionswithRace["Totem"][key] = value
			
for key, value in cardPool.items(): #Fill MinionsofCost
	if "~Uncollectible" not in key and "~Minion~" in key:
		cost = int(key.split('~')[3])
		if cost not in MinionsofCost.keys():
			MinionsofCost[cost] = {key: value}
		else:
			MinionsofCost[cost][key] = value
			
for key, value in cardPool.items():  #Fill NeutralMinions
	if "~Uncollectible" not in key:
		Class = str(key.split('~')[1])
		if Class != "Neutral":
			if Class not in ClassCards.keys():
				ClassCards[Class] = {key: value}
			else:
				ClassCards[Class][key] = value
		else:
			NeutralMinions[key] = value
			
for key, value in cardPool.items(): #Fill ClassicCards
	if "~Uncollectible" not in key and "~Legendary" in key and "~Minion~" in key:
		LegendaryMinions[key] = value
		
with open(filename, "w") as out_file:
	#MinionswithRace
	out_file.write("MinionswithRace = {\n")
	for race, dict in MinionswithRace.items():
		out_file.write("\t\t\t'%s': {\n"%race)
		for index, obj in dict.items(): #value is dict
			out_file.write('\t\t\t\t"%s": %s,\n'%(index, obj.__name__))
		out_file.write("\t\t\t},\n")
	out_file.write("\t\t\t}\n\n")
	
	#MinionsofCost
	out_file.write("MinionsofCost = {\n")
	for cost, dict in MinionsofCost.items():
		out_file.write("\t\t\t%d: {\n"%cost)
		for index, obj in dict.items():
			out_file.write('\t\t\t"%s": %s,\n'%(index, obj.__name__))
		out_file.write("\t\t\t},\n")
	out_file.write("\t\t}\n\n")
	
	#ClassCards
	out_file.write("ClassCards = {\n")
	for Class, dict in ClassCards.items():
		out_file.write("\t\t\t'%s': {\n"%Class)
		for index, obj in dict.items(): #value is dict
			out_file.write('\t\t\t\t"%s": %s,\n'%(index, obj.__name__))
		out_file.write("\t\t\t},\n")
	out_file.write("\t\t\t}\n\n")
	
	#NeutralMinions
	out_file.write("NeutralMinions = {\n")
	for index, obj in NeutralMinions.items():
		out_file.write('\t\t\t"%s": %s,\n'%(index, obj.__name__))
	out_file.write("\t\t}\n\n")
	
	#LegendaryMinions
	out_file.write("LegendaryMinions = {\n")
	for index, obj in LegendaryMinions.items():
		out_file.write('\t\t\t"%s": %s,\n'%(index, obj.__name__))
	out_file.write("\t\t}\n\n")
	
	