import copy

def concatenateDicts(dict1, dict2):
	for key in dict2.keys():
		dict1[key] = copy.deepcopy(dict2[key]) if key not in dict1 else concatenateDicts(dict1[key], dict2[key])
	return dict1
	
def extractfrom(target, listObject):
	try: return listObject.pop(listObject.index(target))
	except: return None
	
cardPool, info = {}, ""

from Basic import *
cardPool.update(Basic_Indices)
info += "from Basic import *\n"

from Classic import *
cardPool.update(Classic_Indices)
info += "from Classic import *\n"

from Shadows import *
cardPool.update(Shadows_Indices)
info += "from Shadows import *\n"

from Uldum import *
cardPool.update(Uldum_Indices)
info += "from Uldum import *\n"

from Dragons import *
cardPool.update(Dragons_Indices)
info += "from Dragons import *\n"

from Galakrond import *
cardPool.update(Galakrond_Indices)
info += "from Galakrond import *\n"

from DemonHunterInitiate import *
cardPool.update(DemonHunterInit_Indices)
info += "from DemonHunterInitiate import *\n"

from Outlands import *
cardPool.update(Outlands_Indices)
info += "from Outlands import *\n"

from Monk import *
cardPool.update(Monk_Indices)
info += "from Monk import *\n"

class PoolManager:
	def __init__(self):
		self.cardPool = {}
		
UpgradedHeroPowers, Classes, ClassesandNeutral, ClassDict = [], [], [], {}
for key in list(cardPool.keys()):
	if "Hero: " in key:
		Class = key.split(": ")[1]
		Classes.append(Class)
		ClassesandNeutral.append(Class)
		ClassDict[Class] = cardPool[key]
		del cardPool[key]
	elif " Hero Power~" in key:
		if "~Upgraded Hero Power~" in key:
			UpgradedHeroPowers.append(cardPool[key])
		del cardPool[key]
		
ClassesandNeutral.append("Neutral")

Game = PoolManager()
Game.Classes = Classes
Game.ClassesandNeutral = ClassesandNeutral
Game.ClassDict = ClassDict
Game.cardPool = cardPool
keys, values = list(cardPool.keys()), list(cardPool.values())
for key, value in zip(keys, values):
	if "Galakrond" in value.description or "Invoke" in value.description or "invoke" in value.description:
		del Game.cardPool[key]
	if value.description.startswith("Quest: "):
		del Game.cardPool[key]
		
Game.MinionswithRace = {"Beast": {}, "Demon": {}, "Dragon": {}, "Elemental":{},
						"Murloc": {}, "Mech": {}, "Pirate":{}, "Totem": {}}
for key, value in Game.cardPool.items(): #Fill MinionswithRace
	if "~Uncollectible" not in key:
		for race in Game.MinionswithRace.keys():
			if "~%s~"%race in key: Game.MinionswithRace[race][key] = value
			
Game.MinionsofCost = {}
for key, value in Game.cardPool.items():
	if "~Minion~" in key and "~Uncollectible" not in key:
		cost = int(key.split('~')[3])
		try: Game.MinionsofCost[cost][key] = value
		except: Game.MinionsofCost[cost] = {key: value}
		
Game.ClassCards = {}
Game.NeutralMinions = {}
for key, value in Game.cardPool.items():  #Fill NeutralMinions
	if "~Uncollectible" not in key:
		Class = str(key.split('~')[1])
		if Class != "Neutral":
			try: Game.ClassCards[Class][key] = value
			except: Game.ClassCards[Class] = {key: value}
		else:
			Game.NeutralMinions[key] = value
			
Game.LegendaryMinions = {}
for key, value in Game.cardPool.items():
	if "~Legendary" in key and "~Minion~" in key and "~Uncollectible" not in key:
		Game.LegendaryMinions[key] = value
		
RNGPools = {}

with open("CardPools.py", "w") as out_file:
	#确定RNGPools
	for card in cardPool.values():
		if hasattr(card, "poolIdentifier"):
			identifier, pool = card.generatePool(Game)
			#发现职业法术一定会生成一个职业列表，不会因为生成某个特定职业法术的牌而被跳过
			if isinstance(identifier, list): #单identifier
				for key, value in zip(identifier, pool):
					if key not in RNGPools: RNGPools[key] = value
			else:
				if identifier not in RNGPools: RNGPools[identifier] = pool
				
	out_file.write(info)
	
	#把UpgradedHeroPowers, Classes, ClassesandNeutral, ClassDict写入python里面
	out_file.write("\nUpgradedHeroPowers = [")
	for power in UpgradedHeroPowers: out_file.write(power.__name__+", ")
	out_file.write(']\n')
	out_file.write("Classes = [")
	for s in Classes: out_file.write("'%s', "%s)
	out_file.write(']\n')
	out_file.write("ClassesandNeutral = [")
	for s in ClassesandNeutral: out_file.write("'%s', "%s)
	out_file.write(']\n')
	out_file.write("ClassDict = {")
	for key, value in ClassDict.items(): out_file.write("'%s': %s, "%(key, value.__name__))
	out_file.write("}\n\n")
	
	#把cardPool写入python里面
	out_file.write("cardPool = {\n")
	for index, obj in cardPool.items():
		out_file.write('\t\t\t"%s": %s,\n'%(index, obj.__name__))
	out_file.write("\t\t}\n\n")
	
	##把MinionswithRace写入python里面
	#out_file.write("MinionswithRace = {\n")
	#for Class, dict in Game.MinionswithRace.items():
	#	out_file.write("\t\t\t'%s': {\n"%Class)
	#	for index, obj in dict.items(): #value is dict
	#		out_file.write('\t\t\t\t"%s": %s,\n'%(index, obj.__name__))
	#	out_file.write("\t\t\t},\n")
	#out_file.write("\t\t\t}\n\n")
	
	#把MinionsofCost写入python里面
	out_file.write("MinionsofCost = {\n")
	for cost, dict in Game.MinionsofCost.items():
		out_file.write("\t\t\t%d: ["%cost)
		i = 1
		for obj in dict.values():
			out_file.write(obj.__name__+", ")
			i += 1
			if i % 10 == 0: out_file.write("\n\t\t\t")
		out_file.write("\t\t\t],\n")
	out_file.write("\t\t}\n")
	
	#把ClassCards写入python里面
	out_file.write("ClassCards = {\n")
	for race, dict in Game.ClassCards.items():
		out_file.write("\t\t\t'%s': {\n"%race)
		for index, obj in dict.items(): #value is dict
			out_file.write('\t\t\t\t"%s": %s,\n'%(index, obj.__name__))
		out_file.write("\t\t\t},\n")
	out_file.write("\t\t\t}\n\n")
	
	#把NeutralMinions写入python里面
	out_file.write("NeutralMinions = {\n")
	for index, obj in Game.NeutralMinions.items():
		out_file.write('\t\t\t"%s": %s,\n'%(index, obj.__name__))
	out_file.write("\t\t}\n\n")
	
	#把RNGPool写入python里面
	out_file.write("RNGPools = {\n")
	#print(RNGPools)
	for poolIdentifier, obj in RNGPools.items():
		if type(obj) == type([]):
			#出来就休眠的随从现在不能出现在召唤池中
			if poolIdentifier.endswith(" to Summon"):
				extractfrom(Magtheridon, obj)
				#extractfrom(TheDarkness, obj)
			out_file.write("\t\t'%s': ["%poolIdentifier)
			i = 0
			for obj in obj:
				out_file.write(obj.__name__+', ')
				i += 1
				if i % 10 == 0:
					out_file.write('\n\t\t\t\t')
			out_file.write("],\n")
		elif type(obj) == type({}): #专门给了不起的杰弗里斯提供的
			out_file.write("\t\t\t'%s': {\n"%poolIdentifier)
			for index, value in obj.items():
				out_file.write('\t\t\t\t\t\t"%s": %s,\n'%(index, value.__name__))
			out_file.write("\t\t\t},\n")
	out_file.write("\t\t}")