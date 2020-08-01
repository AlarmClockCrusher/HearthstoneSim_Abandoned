from CardPools import *
from Academy import TransferStudent
import copy
from numpy.random import shuffle as npshuffle
from numpy.random import choice as npchoice
import numpy as np

import inspect

def extractfrom(target, listObj):
	try: return listObj.pop(listObj.index(target))
	except: return None
	
def fixedList(listObj):
	return listObj[0:len(listObj)]
	
def PRINT(game, string, *args):
	if game.GUI:
		if not game.mode: game.GUI.printInfo(string)
	elif not game.mode: print("game's guide mode is 0\n", string)
	
#对卡牌的费用机制的改变
#主要参考贴（冰封王座BB还在的时候）：https://www.diyiyou.com/lscs/news/194867.html
#
#费用的计算方式是对于一张牌，不考虑基础费用而是把费用光环和费用赋值一视同仁，根据其执行顺序来决定倒数第二步的费用，最终如果一张牌有自己赋值或者费用修改的能力，则这个能力在最后处理。
#
#BB给出的机制例子中：AV娜上场之后，热情的探险者抽一张牌，抽到融核巨人之后的结算顺序是：
#	AV的变1光环首先生效，然后探险者的费用赋值把那张牌的费用拉回5，然后融核巨人再根据自己的血量进行减费用。
#确实可以解释当前娜迦沙漠女巫与费用光环和大帝减费的问题。
#1：对方场上一个木乃伊，我方一个沙漠女巫，对方一个木乃伊，然后分别是-1光环，赋值为5，-1光环，法术的费用变成4费
#2：对方场上一个木乃伊，我方一个沙漠女巫，对方一个木乃伊，然后大帝。结算结果是-1光环，赋值为5，-1光环，-1赋值。结果是3费
#3.对方场上一个木乃伊，我方一个沙漠女巫，对方一个木乃伊，然后大帝，然后第一个木乃伊被连续杀死，光环消失。结算是赋值为5，-1光环，-1费用变化。最终那张法术的费用为3.
#4.对方场上一个木乃伊，我方一个沙漠女巫，对方一个木乃伊，然后大帝，第二个木乃伊被连续杀死，则那个法术-1光环，赋值为5，-1费用变化，最终费用为4.（已经验证是确实如此）
#5。对方场上一个木乃伊，我方一个沙漠女巫，对方一个木乃伊，然后大帝，第一个木乃伊被连续杀死，则那个法术会经历赋值为5，-1光环，-1费用变化，变为3费（注意第一个木乃伊第一次死亡的时候会复生出一个新的带光环的木乃伊，然后把费用变成2费，但是再杀死那个复生出来的木乃伊之后，费用就是正确的3费。）
class Manas:
	def __init__(self, Game):
		self.Game = Game
		self.manas = {1:1, 2:0}
		self.manasUpper = {1:1, 2:0}
		self.manasLocked = {1:0, 2:0}
		self.manasOverloaded = {1:0, 2:0}
		self.manas_UpperLimit = {1:10, 2:10}
		self.manas_withheld = {1:0, 2:0}
		#CardAuras只存放临时光环，永久光环不再注册于此
		#对于卡牌的费用修改效果，每张卡牌自己处理。
		self.CardAuras, self.CardAuras_Backup = [], []
		self.PowerAuras, self.PowerAuras_Backup = [], []
		self.status = {1: {"Spells Cost Health Instead": 0},
						2: {"Spells Cost Health Instead": 0}
						}
						
	#If there is no setting mana aura, the mana is simply adding/subtracting.
	#If there is setting mana aura
		#The temp mana change aura works in the same way as ordinary mana change aura.
	
	'''When the setting mana aura disappears, the calcMana function
	must be cited again for every card in its registered list.'''
	def overloadMana(self, num, ID):
		self.manasOverloaded[ID] += num
		self.Game.sendSignal("ManaOverloaded", ID, None, None, 0, "")
		self.Game.sendSignal("OverloadCheck", ID, None, None, 0, "")
		
	def unlockOverloadedMana(self, ID):
		self.manas[ID] += self.manasLocked[ID]
		self.manas[ID] = min(self.manas_UpperLimit[ID], self.manas[ID])
		self.manasLocked[ID] = 0
		self.manasOverloaded[ID] = 0
		self.Game.sendSignal("OverloadCheck", ID, None, None, 0, "")
		
	def setManaCrystal(self, num, ID):
		self.manasUpper[ID] = num
		if self.manas[ID] > num:
			self.manas[ID] = num
		self.Game.sendSignal("ManaXtlsCheck", ID, None, None, 0, "")
		
	def gainManaCrystal(self, num, ID):
		self.manas[ID] += num
		self.manas[ID] = min(self.manas_UpperLimit[ID], self.manas[ID])
		self.manasUpper[ID] += num
		self.manasUpper[ID] = min(self.manas_UpperLimit[ID], self.manasUpper[ID])
		self.Game.sendSignal("ManaXtlsCheck", ID, None, None, 0, "")
		
	def gainEmptyManaCrystal(self, num, ID):
		if self.manasUpper[ID] + num <= self.manas_UpperLimit[ID]:
			self.manasUpper[ID] += num
			self.Game.sendSignal("ManaXtlsCheck", ID, None, None, 0, "")
			return True
		else: #只要获得的空水晶量高于目前缺少的空水晶量，即返回False
			self.manasUpper[ID] = self.manas_UpperLimit[ID]
			self.Game.sendSignal("ManaXtlsCheck", ID, None, None, 0, "")
			return False
			
	def restoreManaCrystal(self, num, ID, restoreAll=False):
		if restoreAll:
			self.manas[ID] = self.manasUpper[ID] - self.manasLocked[ID]
		else:
			self.manas[ID] += num
			self.manas[ID] = min(self.manas[ID], self.manasUpper[ID] - self.manasLocked[ID])
			
	def destroyManaCrystal(self, num, ID):
		self.manasUpper[ID] -= num
		self.manasUpper[ID] = max(0, self.manasUpper[ID])
		self.manas[ID] = min(self.manas[ID], self.manasUpper[ID])
		self.Game.sendSignal("ManaXtlsCheck", ID, None, None, 0, "")
		
	def affordable(self, subject):
		ID = subject.ID
		return {"Spell": (self.status[ID]["Spells Cost Health Instead"] > 0 and subject.mana < self.Game.heroes[ID].health + self.Game.heroes[ID].armor or self.Game.status[ID]["Immune"] > 0) \
					or subject.mana <= self.manas[ID], #目前只考虑法术的法力消耗改生命消耗光环
				"Minion": subject.mana <= self.manas[ID],
				"Weapon": subject.mana <= self.manas[ID],
				"Power": subject.mana <= self.manas[ID],
				"Hero": subject.mana <= self.manas[ID]
				}[subject.type]
				
	def payManaCost(self, subject, mana):
		ID, mana = subject.ID, max(0, mana)
		if subject.type == "Spell" and self.status[ID]["Spells Cost Health Instead"] > 0:
			dmgTaker = self.Game.scapegoat4(self.Game.heroes[ID])
			dmgTaker.takesDamage(None, mana)
		else: self.manas[ID] -= mana
		self.Game.sendSignal("ManaPaid", ID, subject, None, mana, "")
		if subject.type == "Minion":
			self.Game.Counters.manaSpentonPlayingMinions[ID] += mana
		elif subject.type == "Spell":
			self.Game.Counters.manaSpentonSpells[ID] += mana
			
	#At the start of turn, player's locked mana crystals are removed.
	#Overloaded manas will becomes the newly locked mana.
	def turnStarts(self):
		ID = self.Game.turn
		self.gainEmptyManaCrystal(1, ID)
		self.manasLocked[ID] = self.manasOverloaded[ID]
		self.manasOverloaded[ID] = 0
		self.manas[ID] = max(0, self.manasUpper[ID] - self.manasLocked[ID] - self.manas_withheld[ID])
		self.Game.sendSignal("OverloadCheck", ID, None, None, 0, "")
		#卡牌的费用光环加载
		for aura in self.CardAuras_Backup:
			if aura.ID == self.Game.turn:
				tempAura = extractfrom(aura, self.CardAuras_Backup)
				self.CardAuras.append(tempAura)
				tempAura.auraAppears()
		self.calcMana_All()
		#英雄技能的费用光环加载
		for aura in self.PowerAuras_Backup:
			if aura.ID == self.Game.turn:
				tempAura = extractfrom(aura, self.PowerAuras_Backup)
				self.PowerAuras.append(tempAura)
				tempAura.auraAppears()
		self.calcMana_Powers()
		
	#Manas locked at this turn doesn't disappear when turn ends. It goes away at the start of next turn.
	def turnEnds(self):
		for aura in self.CardAuras + self.PowerAuras:
			if hasattr(aura, "temporary") and aura.temporary:
				PRINT(self.Game, "{} expires at the end of turn.".format(aura))
				aura.auraDisappears()
		self.calcMana_All()
		self.calcMana_Powers()
		
	def calcMana_All(self, comment="HandOnly"):
		#舍弃之前的卡牌的基础法力值设定
		#卡牌的法力值计算：从卡牌的的基础法力值开始，把法力值光环和法力按照入场顺序进行排列，然后依次进行处理。最后卡牌如果有改变自己费用的能力，则其最后结算，得到最终的法力值。
		#对卡牌的法力值增减和赋值以及法力值光环做平等的处理。
		if comment == "HandOnly":
			cards = self.Game.Hand_Deck.hands[1] + self.Game.Hand_Deck.hands[2]
		else: #comment == "IncludingDeck"
			cards = self.Game.Hand_Deck.hands[1] + self.Game.Hand_Deck.hands[2] + self.Game.Hand_Deck.decks[1] + self.Game.Hand_Deck.decks[2]
		for card in cards:
			self.calcMana_Single(card)
			
	def calcMana_Single(self, card):
		card.mana = type(card).mana
		for manaMod in card.manaMods:
			manaMod.handleMana()
		#随从的改变自己法力值的效果在此结算。如果卡牌有回响，则其法力值不能减少至0
		card.selfManaChange()
		if card.mana < 0: #费用修改不能把卡的费用降为0
			card.mana = 0
		if card.type == "Minion" and card.mana < 1 and card.keyWords["Echo"] > 0:
			card.mana = 1
		elif card.type == "Spell" and card.mana < 1 and "Echo" in card.index:
			card.mana = 1
			
	def calcMana_Powers(self):
		for ID in range(1, 3):
			self.Game.powers[ID].mana = type(self.Game.powers[ID]).mana
			for manaMod in self.Game.powers[ID].manaMods:
				manaMod.handleMana()
			if self.Game.powers[ID].mana < 0:
				self.Game.powers[ID].mana = 0
				
	def createCopy(self, recipientGame):
		Copy = type(self)(recipientGame)
		for key, value in self.__dict__.items():
			if key == "Game" or callable(value):
				pass
			elif "Auras" not in key: #不承载光环的列表都是数值，直接复制即可
				Copy.__dict__[key] = copy.deepcopy(value)
			else: #承载光环和即将加载的光环的列表
				for aura in value:
					Copy.__dict__[key].append(aura.createCopy(recipientGame))
		return Copy
		
			
class Secrets:
	def __init__(self, Game):
		self.Game = Game
		self.secrets = {1:[], 2:[]}
		self.mainQuests = {1: [], 2: []}
		self.sideQuests = {1:[], 2:[]}
		
	def areaNotFull(self, ID):
		return len(self.mainQuests[ID]) + len(self.sideQuests[ID]) + len(self.secrets[ID]) < 5
		
	def spaceinArea(self, ID):
		return 5 - (len(self.mainQuests[ID]) + len(self.sideQuests[ID]) + len(self.secrets[ID]))
		
	def deploySecretsfromDeck(self, ID, num=1):
		curGame = self.Game
		for i in range(num):
			if curGame.mode == 0:
				if curGame.guides:
					i = curGame.guides.pop(0)
				else:
					secrets = [i for i, card in enumerate(curGame.Hand_Deck.decks[ID]) if "~~Secret" in card.index and not self.sameSecretExists(card, ID)]
					i = npchoice(secrets) if secrets and self.areaNotFull(ID) else -1
					curGame.fixedGuides.append(i)
				if i > -1: curGame.Hand_Deck.extractfromDeck(i, ID, enemyCanSee=False)[0].whenEffective()
				else: break
				
	def extractSecrets(self, ID, index=0):
		secret = self.secrets[ID].pop(index)
		secret.active = False
		for trigger in secret.trigsBoard:
			trigger.disconnect()
		PRINT(self.Game, "Secret %s is removed"%secret.name)
		return secret
		
	#secret can be type, index or real card.
	def sameSecretExists(self, secret, ID):
		if isinstance(secret, str):
			for deployedSecret in self.secrets[ID]:
				if deployedSecret.index == secret:
					return True
		else: #If secret is real card or type
			for deployedSecret in self.secrets[ID]:
				if deployedSecret.name == secret.name:
					return True
		return False
			
	#只有Game自己会引用Secrets
	def createCopy(self, recipientGame):
		Copy = type(self)(recipientGame)
		for ID in range(1, 3):
			for secret in self.secrets[ID]:
				Copy.secrets[ID].append(secret.createCopy(recipientGame))
			for quest in self.mainQuests[ID]:
				Copy.mainQuests[ID].append(quest.createCopy(recipientGame))
			for quest in self.sideQuests[ID]:
				Copy.sideQuests[ID].append(quest.createCopy(recipientGame))
		return Copy
		
		
class Counters:
	def __init__(self, Game):
		self.Game = Game
		self.cardsPlayedThisGame = {1:[], 2:[]}
		self.minionsDiedThisGame = {1:[], 2:[]}
		self.weaponsDestroyedThisGame = {1:[], 2:[]}
		self.mechsDiedThisGame = {1:[], 2:[]}
		self.manaSpentonSpells = {1: 0, 2: 0}
		self.manaSpentonPlayingMinions = {1: 0, 2: 0}
		self.numPogoHoppersPlayedThisGame = {1: 0, 2: 0}
		self.healthRestoredThisGame = {1: 0, 2: 0}
		self.cardsDiscardedThisGame = {1:[], 2:[]}
		self.createdCardsPlayedThisGame = {1:0, 2:0}
		self.spellsonFriendliesThisGame = {1:[], 2:[]}
		
		self.numSpellsPlayedThisTurn = {1: 0, 2: 0}
		self.numMinionsPlayedThisTurn = {1: 0, 2: 0}
		self.minionsDiedThisTurn = {1:[], 2:[]}
		self.numCardsPlayedThisTurn = {1:0, 2:0} #Specifically for Combo. Because even Countered spells can trigger Combos
		self.cardsPlayedThisTurn = {1: {"Indices": [], "ManasPaid": []},
									2: {"Indices": [], "ManasPaid": []}} #For Combo and Secret.
		self.damageonHeroThisTurn = {1:0, 2:0}
		self.damageDealtbyHeroPower = {1:0, 2:0}
		self.numElementalsPlayedLastTurn = {1:0, 2:0}
		self.spellsPlayedLastTurn = {1:[], 2:[]}
		self.cardsPlayedLastTurn = {1:[], 2:[]}
		self.heroAttackTimesThisTurn = {1:0, 2:0}
		self.primaryGalakronds = {1: None, 2: None}
		self.invocationCounts = {1:0, 2:0} #For Galakrond
		self.hasPlayedQuestThisGame = {1:False, 2:False}
		self.timesHeroChangedHealth_inOwnTurn = {1:0, 2:0}
		self.heroChangedHealthThisTurn = {1:False, 2:False}
		self.powerUsedThisTurn = 0
		
	def turnEnds(self):
		self.numElementalsPlayedLastTurn[self.Game.turn] = 0
		self.cardsPlayedLastTurn[self.Game.turn] = [] + self.cardsPlayedThisTurn[self.Game.turn]["Indices"]
		for index in self.cardsPlayedThisTurn[self.Game.turn]["Indices"]:
			if "~Elemental~" in index:
				self.numElementalsPlayedLastTurn[self.Game.turn] += 1
		self.spellsPlayedLastTurn[self.Game.turn] = []
		for index in self.cardsPlayedThisTurn[self.Game.turn]["Indices"]:
			if "~Spell~" in index:
				self.spellsPlayedLastTurn[self.Game.turn].append(index)
		self.cardsPlayedThisTurn = {1:{"Indices": [], "ManasPaid": []},
									2:{"Indices": [], "ManasPaid": []}}
		self.numCardsPlayedThisTurn = {1:0, 2:0}
		self.numMinionsPlayedThisTurn = {1:0, 2:0}
		self.numSpellsPlayedThisTurn = {1:0, 2:0}
		self.damageonHeroThisTurn = {1:0, 2:0}
		self.minionsDiedThisTurn = {1:[], 2:[]}
		self.heroAttackTimesThisTurn = {1:0, 2:0}
		self.heroChangedHealthThisTurn = {1:False, 2:False}
		self.powerUsedThisTurn = 0
		
	#只有Game自己会引用Counters
	def createCopy(self, recipientGame):
		Copy = type(self)(recipientGame)
		for key, value in self.__dict__.items():
			if value == self.Game:
				pass
			elif callable(value):
				pass
			elif isinstance(value, (type, type(None), int, np.int64, float, str, bool)):
				Copy.__dict__[key] = value
			elif type(value) == list or type(value) == dict or type(value) == tuple:
				Copy.__dict__[key] = self.copyListDictTuple(value, recipientGame)
			else:
				#因为Counters内部的值除了Game都是数字组成的，可以直接deepcopy
				Copy.__dict__[key] = value.createCopy(recipientGame)
		return Copy
		
	def copyListDictTuple(self, obj, recipientGame):
		if isinstance(obj, list):
			objCopy = []
			for element in obj:
				#check if they're basic types, like int, str, bool, NoneType, 
				if isinstance(element, (type(None), int, float, str, bool)):
					#Have tested that basic types can be appended and altering the original won't mess with the content in the list.
					objCopy.append(element)
				elif inspect.isclass(element):
					objCopy.append(element)
				elif type(element) == list or type(element) == dict or type(element) == tuple: #If the element is a list or dict, just recursively use this function.
					objCopy.append(self.copyListDictTuple(element, recipientGame))
				else: #If the element is a self-defined class. All of them have selfCopy methods.
					objCopy.append(element.createCopy(recipientGame))
		elif isinstance(obj, dict):
			objCopy = {}
			for key, value in obj.items():
				if isinstance(value, (type(None), int, float, str, bool)):
					objCopy[key] = value
				elif inspect.isclass(value):
					objCopy[key] = value
				elif type(value) == list or type(value) == dict or type(value) == tuple:
					objCopy[key] = self.copyListDictTuple(value, recipientGame)
				else:
					objCopy[key] = value.createCopy(recipientGame)
		else: #elif isinstance(obj, tuple):
			tupleTurnedList = list(obj) #tuple因为是immutable的，所以要根据它生成一个列表
			objCopy = self.copyListDictTuple(tupleTurnedList, recipientGame) #复制那个列表
			objCopy = list(objCopy) #把那个列表转换回tuple
		return objCopy
		
		
class Discover:
	def __init__(self, Game):
		self.Game = Game
		self.initiator = None
		
	#When there is no GUI selection, the player_HandleRNG should do the discover right away.
	#当Player决定打出一张触发发现的手牌时，进入发现过程，然后player会假设挑选所有的发现选项，然后根据不同的发现选项来分析得到这个发现选项之后的行为（同样
	#是NO_RNG和有一次随机的选项，然后和其他的对比），取分数最高的挑选。
	#这次挑选之后如果有再次发现的情况，则需要再次进行以上流程。
	def branch_discover(self, initiator):
		self.initiator = initiator
		for i in range(len(discoverOptions)):
			game = copy.deepcopy(self.Game)
			option = game.options[i]
			initiatorCopy = game.initiator
			#拿到提供的一个发现选项。
			initiatorCopy.discoverDecided(option)#这里可能会返回多次发现的情况，如档案管理员
			game.options = []
			#根据这个发现选项进行排列组合，挑选无随机的所有可能性。记录下那个分数，和之后其他选项的对比
			discover_branch[key+initiator.name+"_chooses_"+option.name+";"] = game
			
	def startDiscover(self, initiator, info=None):
		if self.Game.GUI:
			self.initiator = initiator
			self.Game.GUI.update()
			self.Game.GUI.waitforDiscover(info)
			self.initiator, self.Game.options = None, []
			
	def typeCardName(self, initiator):
		if self.Game.GUI:
			self.initiator = initiator
			PRINT(self.Game, "Start to type the name of a card you want")
			self.Game.GUI.update()
			self.Game.GUI.wishforaCard(initiator)
			self.Game.options = []
		
	#除了Game本身，没有东西会在函数外引用Game.Discover
	def createCopy(self, recipientGame):
		return type(self)(recipientGame)
		