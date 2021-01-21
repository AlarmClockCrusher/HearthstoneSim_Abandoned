from numpy.random import choice as npchoice

def concatenateDicts(dict1, dict2):
	for key in dict2.keys():
		dict1[key] = copy.deepcopy(dict2[key]) if key not in dict1 else concatenateDicts(dict1[key], dict2[key])
	return dict1
	
def indexHasClass(index, Class):
	return Class in index.split('~')[1]
	
def canBeGenerated(cardType):
	return not cardType.index.startswith("SV_") and not cardType.description.startswith("Quest:") and \
			not ("Galakrond" in cardType.name or "Galakrond" in cardType.description or "Invoke" in cardType.description or "invoke" in cardType.description)
			
			
class PoolManager:
	def __init__(self):
		self.cardPool = {}
		
from Basic import *
from Classic import *
from AcrossPacks import *
from DemonHunterInitiate import *
from Outlands import *
from Academy import *
from Darkmoon import *

from Monk import *
from SV_Basic import *
from SV_Ultimate import *
from SV_Uprooted import *
from SV_Fortune import *
from SV_Rivayle import *
from SV_Eternal import *

def makeCardPool(board="0 Random Game Board",monk=0,SV=0):
	cardPool, info = {}, ""
	
	cardPool.update(Basic_Indices)
	info += "from Basic import *\n"
	
	cardPool.update(Classic_Indices)
	info += "from Classic import *\n"
	
	cardPool.update(AcrossPacks_Indices)
	info += "from AcrossPacks import *\n"
	
	cardPool.update(DemonHunterInit_Indices)
	info += "from DemonHunterInitiate import *\n"
	
	cardPool.update(Outlands_Indices)
	info += "from Outlands import *\n"

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
		"26 Darkmoon Faire": TransferStudent_Darkmoon,
		}
	if board == "0 Random Game Board": board = npchoice(list(transferStudentPool))
	transferStudent = transferStudentPool[board]
	Academy_Indices[transferStudent.index] = transferStudent
	cardPool.update(Academy_Indices)
	info += "from Academy import *\n"
	
	cardPool.update(Darkmoon_Indices)
	info += "from Darkmoon import *\n"
	
	if monk:
		print("Including Monk")
		cardPool.update(Monk_Indices)
		info += "from Monk import *\n"

	if SV:
		cardPool.update(SV_Basic_Indices)
		info += "from SV_Basic import *\n"

		cardPool.update(SV_Ultimate_Indices)
		info += "from SV_Ultimate import *\n"

		cardPool.update(SV_Uprooted_Indices)
		info += "from SV_Uprooted import *\n"

		cardPool.update(SV_Fortune_Indices)
		info += "from SV_Fortune import *\n"

		cardPool.update(SV_Rivayle_Indices)
		info += "from SV_Rivayle import *\n"

		cardPool.update(SV_Eternal_Indices)
		info += "from SV_Eternal import *\n"

	BasicPowers, UpgradedPowers, Classes, ClassesandNeutral, ClassDict = [], [], [], [], {}
	for key in list(cardPool.keys()):
		if "Hero: " in key:
			Class = key.split(":")[1].strip()
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
	
	#print("SV cards included in card pool:", "SV_Basic~Runecraft~4~3~3~Minion~None~Vesper, Witchhunter~Accelerate~Fanfare" in Game.cardPool)
	#cardPool本身需要保留各种祈求牌
	Game.MinionswithRace = {"Beast": {}, "Demon": {}, "Dragon": {}, "Elemental":{},
							"Murloc": {}, "Mech": {}, "Pirate":{}, "Totem": {}}
	for key, value in Game.cardPool.items(): #Fill MinionswithRace
		if "~Uncollectible" not in key and hasattr(value, "race") and value.race and canBeGenerated(value):
			for race in value.race.split(','):
				Game.MinionswithRace[race][key] = value
				
	Game.MinionsofCost = {}
	for key, value in Game.cardPool.items():
		if "~Minion~" in key and "~Uncollectible" not in key and canBeGenerated(value):
			cost = int(key.split('~')[3])
			try: Game.MinionsofCost[cost][key] = value
			except: Game.MinionsofCost[cost] = {key: value}
			
	Game.ClassCards = {s:{} for s in Game.Classes}
	Game.NeutralCards = {}
	for key, value in Game.cardPool.items():  #Fill NeutralCards
		if "~Uncollectible" not in key and canBeGenerated(value):
			for Class in key.split('~')[1].split(','):
				if Class != "Neutral":
					try: Game.ClassCards[Class][key] = value
					except: print("Failed Class Assignment is ", Class, key, value)
				else: Game.NeutralCards[key] = value
				
	Game.LegendaryMinions = {}
	for key, value in Game.cardPool.items():
		if "~Legendary" in key and "~Minion~" in key and "~Uncollectible" not in key and canBeGenerated(value):
			Game.LegendaryMinions[key] = value
			
	RNGPools = {}
	
	with open("CardPools.py", "w") as out_file:
		#确定RNGPools
		for card in cardPool.values():
			if hasattr(card, "poolIdentifier"):
				identifier, pool = card.generatePool(Game)
				#发现职业法术一定会生成一个职业列表，不会因为生成某个特定职业法术的牌而被跳过
				if isinstance(identifier, list):
					for key, value in zip(identifier, pool):
						RNGPools[key] = value
				else: RNGPools[identifier] = pool
				
		#专门为转校生进行卡池生成
		for card in [TransferStudent_Dragons, TransferStudent_Academy]:
			identifier, pool = card.generatePool(Game)
			if isinstance(identifier, list): #单identifier
				for key, value in zip(identifier, pool):
					RNGPools[key] = value
			else: RNGPools[identifier] = pool
			
		#print(info)
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
		
		#把NeutralCards写入python里面
		out_file.write("NeutralCards = {\n")
		for index, obj in Game.NeutralCards.items():
			out_file.write('\t\t\t"%s": %s,\n'%(index, obj.__name__))
		out_file.write("\t\t}\n\n")
		
		#把RNGPool写入python里面
		out_file.write("RNGPools = {\n")
		for poolIdentifier, objs in RNGPools.items():
			if isinstance(objs, list):
				#出来就休眠的随从现在不能出现在召唤池中
				if poolIdentifier.endswith(" to Summon"):
					try: objs.remove(Magtheridon)
					except: pass
				out_file.write("\t\t'%s': ["%poolIdentifier)
				i = 0
				for obj in objs:
					try: out_file.write(obj.__name__+', ')
					except: out_file.write("'%s', "%obj)
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
		
	return board, transferStudent
	
if __name__ == "__main__":
	makeCardPool(board="0 Random Game Board", monk=0, SV=0)