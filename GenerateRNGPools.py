from CardIndices import *
import copy

def concatenateDicts(dict1, dict2):
	for key in dict2.keys():
		if key not in dict1.keys():
			dict1[key] = copy.deepcopy(dict2[key])
		else:
			dict1[key] = concatenateDicts(dict1[key], dict2[key])
	return dict1
	
cardPool = {}
#之后的版本更新需要重写这些update，从而不让新版本覆盖老版本的dict
cardPool.update(Basic_Indices)
cardPool.update(Classic_Indices)
cardPool.update(Shadows_Indices)
cardPool.update(Uldum_Indices)
cardPool.update(Dragons_Indices)
cardPool.update(Galakrond_Indices)
cardPool.update(DemonHunterInit_Indices)
cardPool.update(Outlands_Indices)

class PoolManager:
	def __init__(self):
		self.cardPool = {}
		
Game = PoolManager()
Game.cardPool = cardPool
Game.MinionswithRace = MinionswithRace
Game.MinionsofCost = MinionsofCost
Game.ClassCards = ClassCards
Game.LegendaryMinions = LegendaryMinions
Game.NeutralMinions = NeutralMinions

RNGPools = {}

filename1 = "CardIndices.py"
filename2 = "CardPools.py"

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
	out_file.write("from Shadows import *\n")
	out_file.write("from Uldum import *\n")
	out_file.write("from Dragons import *\n")
	out_file.write("from Galakrond import *\n")
	out_file.write("from DemonHunterInitiate import *\n")
	out_file.write("from Outlands import *\n")
	
	#把cardPool写入python里面
	out_file.write("cardPool = {\n")
	for index, obj in cardPool.items():
		out_file.write('\t\t\t"%s": %s,\n'%(index, obj.__name__))
	out_file.write("\t\t}\n\n")
	
	#把MinionswithRace写入python里面
	out_file.write("MinionswithRace = {\n")
	for Class, dict in MinionswithRace.items():
		out_file.write("\t\t\t'%s': {\n"%Class)
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
	
	#把ClassCards写入python里面
	out_file.write("ClassCards = {\n")
	for race, dict in ClassCards.items():
		out_file.write("\t\t\t'%s': {\n"%race)
		for index, obj in dict.items(): #value is dict
			out_file.write('\t\t\t\t"%s": %s,\n'%(index, obj.__name__))
		out_file.write("\t\t\t},\n")
	out_file.write("\t\t\t}\n\n")
	
	#把NeutralMinions写入python里面
	out_file.write("NeutralMinions = {\n")
	for index, obj in NeutralMinions.items():
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