from CardIndices import *
import copy

def concatenateDicts(dict1, dict2):
	for key in dict2.keys():
		if key not in dict1.keys():
			dict1[key] = copy.deepcopy(dict2[key])
		else:
			dict1[key] = concatenateDicts(dict1[key], dict2[key])
	return dict1
	
cardPool, MinionswithRace, MinionsofCost = {}, {}, {}
ClassCards, NeutralMinions, LegendaryMinions = {}, {}, {}
#之后的版本更新需要重写这些update，从而不让新版本覆盖老版本的dict
cardPool.update(Basic_indices)
cardPool.update(Classic_indices)
cardPool.update(Witchwood_indices)
cardPool.update(Boomsday_indices)
cardPool.update(Rumble_indices)
cardPool.update(Shadows_indices)
cardPool.update(Uldum_Indices)
cardPool.update(Dragons_Indices)
cardPool.update(Galakrond_Indices)

MinionswithRace = concatenateDicts(MinionswithRace, MinionswithRace_BasicClassic)
MinionswithRace = concatenateDicts(MinionswithRace, MinionswithRace_YearRaven)
MinionswithRace = concatenateDicts(MinionswithRace, MinionswithRace_YearDragon)

MinionsofCost = concatenateDicts(MinionsofCost, MinionsofCost_BasicClassic)
MinionsofCost = concatenateDicts(MinionsofCost, MinionsofCost_YearRaven)
MinionsofCost = concatenateDicts(MinionsofCost, MinionsofCost_YearDragon)

ClassCards = concatenateDicts(ClassCards, ClassCards_BasicClassic)
ClassCards = concatenateDicts(ClassCards, ClassCards_YearRaven)
ClassCards = concatenateDicts(ClassCards, ClassCards_YearDragons)
#NeutralMinions和LegendaryMinions只有一层字典，没有必要使用concatenateDicts
NeutralMinions.update(NeutralMinions_BasicClassic)
NeutralMinions.update(NeutralMinions_YearRaven)
NeutralMinions.update(NeutralMinions_YearDragon)

LegendaryMinions.update(LegendaryMinions_BasicClassic)
LegendaryMinions.update(LegendaryMinions_YearRaven)
LegendaryMinions.update(LegendaryMinions_YearDragon)

class PoolManager:
	def __init__(self):
		self.cardPool = {}
		
Game = PoolManager()
Game.cardPool = cardPool
Game.MinionswithRace = MinionswithRace
Game.MinionsofCost = MinionsofCost
Game.ClassCards = ClassCards
Game.LegendaryMinions = LegendaryMinions_BasicClassic
Game.NeutralMinions = NeutralMinions

RNGPools = {}

filename1 = "C:\\Users\\13041\\Desktop\\Python\\HearthStone\\CardIndices.py"
filename2 = "C:\\Users\\13041\\Desktop\\Python\\HearthStone\\CardPools.py"

with open(filename1, "r") as input_file, open(filename2, "w") as out_file:
	#确定RNGPools
	for card in cardPool.values():
		if hasattr(card, "poolIdentifier"):
			identifier, pool = card.generatePool(Game)
			#发现职业法术一定会生成一个职业列表，不会因为生成某个特定职业法术的牌而被跳过
			if type(identifier) != type([]): #单identifier
				if identifier not in RNGPools.keys():
					#print("Creating single key:", identifier)
					#if identifier == "Spells":
					#	print(card)
					#	print(pool)
					RNGPools[identifier] = pool
			else:
				for key, value in zip(identifier, pool):
					if key not in RNGPools.keys():
						#print("Creating multiple key:", key)
						#if key == "Spells":
						#	print(card)
						RNGPools[key] = value
						
	out_file.write("from Basic import *\n")
	out_file.write("from Classic import *\n")
	out_file.write("from Witchwood import *\n")
	out_file.write("from Boomsday import *\n")
	out_file.write("from Rumble import *\n")
	out_file.write("from Shadows import *\n")
	out_file.write("from Uldum import *\n")
	out_file.write("from Dragons import *\n")
	out_file.write("from Galakrond import *\n")
	#把cardPool写入python里面
	out_file.write("cardPool = {\n")
	for index, obj in cardPool.items():
		out_file.write('\t\t\t"%s": %s,\n'%(index, obj.__name__))
	out_file.write("\t\t}\n\n")
	
	#把MinionswithRace写入python里面
	out_file.write("MinionswithRace = {\n")
	for race, dict in MinionswithRace.items():
		out_file.write("\t\t\t'%s': {\n"%race)
		for index, obj in dict.items(): #value is dict
			out_file.write('\t\t\t\t"%s": %s,\n'%(index, obj.__name__))
		out_file.write("\t\t\t},\n")
	out_file.write("\t\t\t}\n\n")
	
	#把MinionsofCost写入python里面
	out_file.write("MinionsofCost = {\n")
	for cost, dict in MinionsofCost.items():
		out_file.write("\t\t\t%d: {\n"%cost)
		for index, obj in dict.items():
			out_file.write('\t\t\t"%s": %s,\n'%(index, obj.__name__))
		out_file.write("\t\t\t},\n")
	out_file.write("\t\t}\n")
	
	#把NeutralMinions写入python里面
	out_file.write("NeutralMinions = {\n")
	for index, obj in NeutralMinions.items():
		out_file.write('\t\t\t"%s": %s,\n'%(index, obj.__name__))
	out_file.write("\t\t}\n\n")
	
	#把RNGPool写入python里面
	out_file.write("RNGPools = {\n")
	#print(RNGPools)
	for poolIdentifier, obj in RNGPools.items():
		#if poolIdentifier == "Spells":
		#	print(poolIdentifier, type(obj), obj)
		if type(obj) == type([]):
			out_file.write("\t\t'%s': ["%poolIdentifier)
			i = 0
			for obj in obj:
				out_file.write(obj.__name__+', ')
				i += 1
				if i % 10 == 0:
					out_file.write('\n\t\t\t\t')
			out_file.write("],\n")
		elif type(obj) == type({}):
			out_file.write("\t\t\t'%s': {\n"%poolIdentifier)
			for index, value in obj.items():
				out_file.write('\t\t\t\t\t\t"%s": %s,\n'%(index, value.__name__))
			out_file.write("\t\t\t},\n")
	out_file.write("\t\t}")