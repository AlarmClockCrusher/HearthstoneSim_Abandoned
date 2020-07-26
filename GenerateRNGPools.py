import copy
from Triggers_Auras import ManaMod
import numpy as np

def concatenateDicts(dict1, dict2):
	for key in dict2.keys():
		dict1[key] = copy.deepcopy(dict2[key]) if key not in dict1 else concatenateDicts(dict1[key], dict2[key])
	return dict1
	
def extractfrom(target, listObject):
	try: return listObject.pop(listObject.index(target))
	except: return None
	
class PoolManager:
	def __init__(self):
		self.cardPool = {}
		
from Basic import *
from Classic import *
from Shadows import *
from Uldum import *
from Dragons import *
from Galakrond import *
from DemonHunterInitiate import *
from Outlands import *
from Monk import *
from Academy import *

def makeCardPool(monk=0, board="0 Random Game Board"):
	cardPool, info = {}, ""
	
	cardPool.update(Basic_Indices)
	info += "from Basic import *\n"
	
	cardPool.update(Classic_Indices)
	info += "from Classic import *\n"
	
	cardPool.update(Shadows_Indices)
	info += "from Shadows import *\n"
	
	cardPool.update(Uldum_Indices)
	info += "from Uldum import *\n"
	
	cardPool.update(Dragons_Indices)
	info += "from Dragons import *\n"
	
	cardPool.update(Galakrond_Indices)
	info += "from Galakrond import *\n"
	
	cardPool.update(DemonHunterInit_Indices)
	info += "from DemonHunterInitiate import *\n"
	
	cardPool.update(Outlands_Indices)
	info += "from Outlands import *\n"
	
	if monk:
		cardPool.update(Monk_Indices)
		info += "from Monk import *\n"
		
	transferStudentPool = {"1 Classic Ogrimmar": TransferStudent_Ogrimmar,
		"2 Classic Stormwind": TransferStudent_Stormwind,
		"3 Classic Stranglethorn": TransferStudent_Stranglethorn,
		"4 Classic Four Wind Valley": TransferStudent_FourWindValley,
		#"5 Naxxramas": TransferStudent_Naxxramas,
		#"6 Goblins vs Gnomes": TransferStudent_GvG,
		#"7 Black Rock Mountain": TransferStudent_BlackRockM,
		#"8 The Grand Tournament": TransferStudent_Tournament,
		#"9 League of Explorers Museum": TransferStudent_LOEMuseum,
		#"10 League of Explorers Ruins": TransferStudent_LOERuins,
		#"11 Corrupted Stormwind": TransferStudent_OldGods,
		#"12 Karazhan": TransferStudent_Karazhan,
		#"13 Gadgetzan": TransferStudent_Gadgetzan,
		#"14 Un'Goro": TransferStudent_UnGoro,
		#"15 Frozen Throne": TransferStudent_FrozenThrone,
		#"16 Kobolds": TransferStudent_Kobold,
		#"17 Witchwood": TransferStudent_Witchwood,
		#"18 Boomsday Lab": TransferStudent_Boomsday,
		#"19 Rumble": TransferStudent_Rumble,
		"20 Dalaran": TransferStudent_Shadows,
		"21 Uldum Desert": TransferStudent_UldumDesert,
		"22 Uldum Oasis": TransferStudent_UldumOasis,
		"23 Dragons": TransferStudent_Dragons,
		"24 Outlands": TransferStudent_Outlands,
		"25 Scholomance Academy": TransferStudent_Academy,
		}
	if board == "0 Random Game Board": board = np.random.choice(list(transferStudentPool.keys()))
	transferStudent = transferStudentPool[board]
	Academy_Indices[transferStudent.index] = transferStudent
	cardPool.update(Academy_Indices)
	info += "from Academy import *\n"
	
	BasicPowers, UpgradedPowers, Classes, ClassesandNeutral, ClassDict = [], [], [], [], {}
	for key in list(cardPool.keys()):
		if "Hero: " in key:
			Class = key.split(": ")[1]
			Classes.append(Class)
			ClassesandNeutral.append(Class)
			ClassDict[Class] = cardPool[key]
			del cardPool[key]
		elif " Hero Power~" in key:
			if "~Upgraded Hero Power~" in key: UpgradedPowers.append(cardPool[key])
			else: BasicPowers.append(cardPool[key])
			del cardPool[key]
			
	ClassesandNeutral.append("Neutral")
	
	Game = PoolManager()
	Game.Classes = Classes
	Game.ClassesandNeutral = ClassesandNeutral
	Game.ClassDict = ClassDict
	Game.cardPool = cardPool
	Game.basicPowers = BasicPowers
	Game.upgradedPowers = UpgradedPowers
	
	keys, values = list(cardPool.keys()), list(cardPool.values())
	for key, value in zip(keys, values):
		if key.startswith("Dragons~") and "Galakrond" in value.description or "Invoke" in value.description or "invoke" in value.description:
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
			Class = key.split('~')[1]
			if Class != "Neutral":
				for str in Class.split(','):
					try: Game.ClassCards[str][key] = value
					except: Game.ClassCards[str] = {key: value}
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
		
		#把BasicPowers, UpgradedPowers, Classes, ClassesandNeutral, ClassDict写入python里面
		out_file.write("\nBasicPowers = [")
		for power in BasicPowers: out_file.write(power.__name__+", ")
		out_file.write(']\n')
		out_file.write("\nUpgradedPowers = [")
		for power in UpgradedPowers: out_file.write(power.__name__+", ")
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
		
	return board