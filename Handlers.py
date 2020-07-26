from CardPools import *
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
				if i > -1: curGame.Hand_Deck.extractfromDeck(i, ID)[0].whenEffective()
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
		if type(secret) == type(""): #If secret is the index
			for deployedSecret in self.secrets[ID]:
				if deployedSecret.index == secret:
					return True
			return False
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
		
		
		
class Hand_Deck:
	def __init__(self, Game, deck1=[], deck2=[]): #通过卡组列表加载卡组
		self.Game = Game
		self.hands = {1:[], 2:[]}
		self.decks = {1:[], 2:[]}
		self.noCards = {1:0, 2:0}
		self.handUpperLimit = {1: 10, 2: 10}
		self.initialDecks = {1: Default1 if deck1 == [] else deck1,
							2: Default2 if deck2 == [] else deck2}
		self.startingDeckIdentities = {1:[], 2:[]}
		self.startingHandIdentities = {1:[], 2:[]}
		
	def initialize(self):
		self.initializeDecks()
		self.initializeHands()
		
	def initializeDecks(self):
		for ID in range(1, 3):
			Class = self.Game.heroes[ID].Class #Hero's class
			for obj in self.initialDecks[ID]:
				card = obj(self.Game, ID)
				if "Galakrond, " in card.name:
					#检测过程中，如果目前没有主迦拉克隆或者与之前检测到的迦拉克隆与玩家的职业不符合，则把检测到的迦拉克隆定为主迦拉克隆
					if self.Game.Counters.primaryGalakronds[ID] is None or (self.Game.Counters.primaryGalakronds[ID].Class != Class and card.Class == Class):
						self.Game.Counters.primaryGalakronds[ID] = card
				self.decks[ID].append(card)
				self.startingDeckIdentities[ID].append(card.identity)	
			npshuffle(self.decks[ID])
			
	def initializeHands(self):#起手要换的牌都已经从牌库中移出到mulligan列表中，
		#如果卡组有双传说任务，则起手时都会上手
		mainQuests = {1:[], 2:[]}
		mulliganSize = {1:3, 2:4}
		for ID in range(1, 3):
			mainQuests[ID] = [card for card in self.decks[ID] if card.description.startswith("Quest")]
			numQueststoDraw = min(len(mainQuests[ID]), mulliganSize[ID])
			if numQueststoDraw > 0:
				queststoDraw = npchoice(mainQuests[ID], numQueststoDraw, replace=False)
				for quest in queststoDraw:
					self.Game.mulligans[ID].append(extractfrom(quest, self.decks[ID]))
			for i in range(mulliganSize[ID]-numQueststoDraw):
				self.Game.mulligans[ID].append(self.decks[ID].pop())
				
	def mulligan(self, indices1, indices2):
		indices = {1:indices1, 2:indices2} #indicesCards是要替换的手牌的列表序号，如[1, 3]
		for ID in range(1, 3):
			cardstoReplace = []
			#self.Game.mulligans is the cards currently in players' hands.
			if indices[ID]:
				for num in range(1, len(indices[ID])+1):
					#起手换牌的列表mulligans中根据要换掉的牌的序号从大到小摘掉，然后在原处补充新手牌
					cardstoReplace.append(self.Game.mulligans[ID].pop(indices[ID][-num]))
					self.Game.mulligans[ID].insert(indices[ID][-num], self.decks[ID].pop())
			self.decks[ID] += cardstoReplace
			for card in self.decks[ID]: card.entersDeck() #Cards in deck arm their possible trigDeck
			npshuffle(self.decks[ID]) #Shuffle the deck after mulligan
			#手牌和牌库中的牌调用entersHand和entersDeck,注册手牌和牌库扳机
			self.hands[ID] = [card.entersHand() for card in self.Game.mulligans[ID]]
			self.Game.mulligans[ID] = []
			self.startingHandIdentities[ID] = [card.identity for card in self.hands[ID]] #Record starting hand
			for card in self.hands[1] + self.hands[2]:
				card.effectCanTrigger()
				card.checkEvanescent()
				
		if self.Game.GUI: self.Game.GUI.update()
		self.addCardtoHand(TheCoin(self.Game, 2), 2)
		self.Game.Manas.calcMana_All()
		for ID in range(1, 3):
			for card in self.hands[ID] + self.decks[ID]:
				if "Start of Game" in card.index:
					card.startofGame()
		self.drawCard(1)
		for card in self.hands[1] + self.hands[2]:
			card.effectCanTrigger()
			card.checkEvanescent()
			
	#双人游戏中一方很多控制自己的换牌，之后两个游戏中复制对方的手牌和牌库信息
	def mulligan1Side(self, ID, indices):
		cardstoReplace = []
		if indices:
			for num in range(1, len(indices)+1):
				cardstoReplace.append(self.Game.mulligans[ID].pop(indices[-num]))
				self.Game.mulligans[ID].insert(indices[-num], self.decks[ID].pop())
		self.hands[ID] = self.Game.mulligans[ID]
		self.decks[ID] += cardstoReplace
		for card in self.decks[ID]: card.entersDeck()
		npshuffle(self.decks[ID])
	#在双方给予了自己的手牌和牌库信息之后把它们注册同时触发游戏开始时的效果
	def startGame(self): #This ID is the opponent's ID
		for ID in range(1, 3): #直接拿着mulligans开始
			self.hands[ID] = [card.entersHand() for card in self.hands[ID]]
			for card in self.decks[ID]: card.entersDeck()
			self.Game.mulligans[ID] = []
		for ID in range(1, 3):
			for card in self.hands[ID]:
				self.startingHandIdentities[ID].append(card.identity)
				for card in self.hands[1] + self.hands[2]:
					card.effectCanTrigger()
					card.checkEvanescent()
					
		self.addCardtoHand(TheCoin(self.Game, 2), 2)
		self.Game.Manas.calcMana_All()
		for ID in range(1, 3):
			for card in self.hands[ID] + self.decks[ID]:
				if "Start of Game" in card.index: card.startofGame()
		self.drawCard(1)
		for card in self.hands[1] + self.hands[2]:
			card.effectCanTrigger()
			card.checkEvanescent()
			
	def handNotFull(self, ID):
		return len(self.hands[ID]) < self.handUpperLimit[ID]
		
	def spaceinHand(self, ID):
		return self.handUpperLimit[ID] - len(self.hands[ID])
		
	def outcastcanTrigger(self, card):
		posinHand = self.hands[card.ID].index(card)
		return posinHand == 0 or posinHand == len(self.hands[card.ID]) - 1
		
	def noDuplicatesinDeck(self, ID):
		record = []
		for card in self.decks[ID]:
			if type(card) not in record:
				record.append(type(card))
			else:
				return False
		return True
		
	def noMinionsinDeck(self, ID):
		for card in self.decks[ID]:
			if card.type == "Minion":
				return False
		return True
		
	def holdingDragon(self, ID, minion=None):
		if minion == None: #When card not in hand and wants to check if a Dragon is in hand
			for card in self.hands[ID]:
				if card.type == "Minion" and "Dragon" in card.race:
					return True
		else: #When the minion is inHand and wants to know if it can trigger after being played.
			for card in self.hands[ID]:
				if card.type == "Minion" and "Dragon" in card.race and card != minion:
					return True
		return False
		
	def holdingSpellwith5CostorMore(self, ID):
		for card in self.hands[ID]:
			if card.type == "Spell" and card.mana >= 5:
				return True
		return False
		
	def holdingCardfromAnotherClass(self, ID, card=None):
		Class = self.Game.heroes[ID].Class
		if card:
			for cardinHand in self.hands[ID]:
				if Class not in cardinHand.Class and cardinHand.Class != "Neutral" and cardinHand != card:
					return True
		else:
			for cardinHand in self.hands[ID]:
				if Class not in cardinHand.Class and cardinHand.Class != "Neutral":
					return True
		return False
			
	#抽牌一次只能一张，需要废除一次抽多张牌的功能，因为这个功能都是用于抽效果指定的牌。但是这些牌中如果有抽到时触发的技能，可能会导致马上抽牌把列表后面的牌提前抽上来
	#现在规则为如果要连续抽2张法术，则分两次检测牌库中的法术牌，然后随机抽一张。
	#如果这个规则是正确的，则在牌库只有一张夺灵者哈卡的堕落之血时，抽到这个法术之后会立即额外抽牌，然后再塞进去两张堕落之血，那么第二次抽法术可能会抽到新洗进去的堕落之血。
	#Damage taken due to running out of card will keep increasing. Refilling the deck won't reset the damage you take next time you draw from empty deck
	def drawCard(self, ID, card=None):
		game, GUI = self.Game, self.Game.GUI
		if card is None: #Draw from top of the deck.
			PRINT(game, "Hero %d draws from the top of the deck"%ID)
			if self.decks[ID]: #Still have cards left in deck.
				card = self.decks[ID].pop()
				mana = card.mana
			else:
				PRINT(game, "Hero%d's deck is empty and will take damage"%ID)
				self.noCards[ID] += 1 #如果在疲劳状态有卡洗入牌库，则疲劳值不会减少，在下次疲劳时，仍会从当前的非零疲劳值开始。
				damage = self.noCards[ID]
				if GUI: GUI.fatigueAni(ID, damage)
				dmgTaker = game.scapegoat4(game.heroes[ID])
				dmgTaker.takesDamage(None, damage) #疲劳伤害没有来源
				return (None, 0)
		else:
			if isinstance(card, (int, np.int32, np.int64)):
				card = self.decks[ID].pop(card)
			else: card = extractfrom(card, self.decks[ID])
			PRINT(game, "Hero %d draws %s from the deck"%(ID, card.name))
			mana = card.mana
		card.leavesDeck()
		if self.handNotFull(ID):
			if GUI: btn = GUI.drawCardAni_1(card)
			cardTracker = [card] #把这张卡放入一个列表，然后抽牌扳机可以对这个列表进行处理同时传递给其他抽牌扳机
			game.sendSignal("CardDrawn", ID, None, cardTracker, mana, "")
			if cardTracker[0].type == "Spell" and "Casts When Drawn" in cardTracker[0].index:
				PRINT(game, "%s is drawn and cast."%cardTracker[0].name)
				if GUI: btn.remove()
				cardTracker[0].whenEffective()
				self.drawCard(ID)
				cardTracker[0].afterDrawingCard()
			else: #抽到的牌可以加入手牌。
				if cardTracker[0].type == "Minion" and cardTracker[0].triggers["Drawn"] != []:
					PRINT(game, "%s is drawn and triggers its effect."%cardTracker[0].name)
					for func in cardTracker[0].triggers["Drawn"]:
						func()
				cardTracker[0] = cardTracker[0].entersHand()
				self.hands[ID].append(cardTracker[0])
				if GUI: GUI.drawCardAni_2(btn, cardTracker[0])
				game.sendSignal("CardEntersHand", ID, None, cardTracker, mana, "")
				game.Manas.calcMana_All()
			return (cardTracker[0], mana)
		else:
			PRINT(game, "Player's hand is full. The drawn card %s is milled"%card.name)
			if GUI: GUI.millCardAni(card)
			return (None, 0)
			
	#Will force the ID of the card to change.
	def addCardtoHand(self, obj, ID, comment="", i=-1):
		game, GUI = self.Game, self.Game.GUI
		if not isinstance(obj, (list, np.ndarray, tuple)): #if the obj is not a list, turn it into a single-element list
			obj = [obj]
		morethan3 = len(obj) > 2
		for card in obj:
			if self.handNotFull(ID):
				if comment == "type": card = card(game, ID)
				elif comment == "index": card = game.cardPool[card](game, ID)
				card.ID = ID
				if GUI: btn = GUI.cardEntersHandAni_1(card)
				self.hands[ID].insert(i+100*(i < 0), card)
				if GUI: GUI.cardEntersHandAni_2(btn, i+100*(i < 0), steps=5 if morethan3 else 10)
				card = card.entersHand()
				game.sendSignal("CardEntersHand", ID, None, [card], 0, comment)
			else: break
		game.Manas.calcMana_All()
		
	def replaceCardDrawn(self, targetHolder, newCard):
		ID = targetHolder[0].ID
		isPrimaryGalakrond = targetHolder[0] == self.Game.Counters.primaryGalakronds[ID]
		targetHolder[0] = newCard
		if isPrimaryGalakrond: self.Game.Counters.primaryGalakronds[ID] = newCard
		
	def replaceCardinHand(self, card, newCard):
		ID = card.ID
		for i in range(len(self.hands[ID])):
			if self.hands[ID][i] == card:
				card.leavesHand()
				self.hands[ID].pop(i)
				self.Game.sendSignal("CardLeavesHand", ID, None, card, 0, "")
				self.addCardtoHand(newCard, ID, "card", i)
				break
				
	def replaceCardinDeck(self, card, newCard):
		ID = card.ID
		try:
			i = self.decks[ID].index(card)
			card.leavesDeck()
			self.decks[ID].pop(i)
			self.decks[ID].insert(i, newCard)
		except: pass
		
	#All the cards shuffled will be into the same deck. If necessary, invoke this function for each deck.
	#PlotTwist把手牌洗入牌库的时候，手牌中buff的随从两次被抽上来时buff没有了。
	#假设洗入牌库这个动作会把一张牌初始化
	def shuffleCardintoDeck(self, obj, initiatorID, enemyCanSee=True):
		curGame = self.Game
		if curGame.GUI: curGame.GUI.shuffleCardintoDeckAni(obj, enemyCanSee)
		if isinstance(obj, (list, np.ndarray)):
			ID = obj[0].ID
			newDeck = self.decks[ID]
			newDeck += obj
			for card in obj: card.entersDeck()
		else: #Shuffle a single card
			ID = obj.ID
			newDeck = self.decks[ID]
			newDeck.append(obj)
			obj.entersDeck()
			
		if curGame.mode == 0:
			if curGame.guides:
				order = curGame.guides.pop(0)
			else:
				order = list(range(len(self.hands[ID])))
				npshuffle(order)
				curGame.fixedGuides.append(tuple(order))
			self.decks[ID] = [newDeck[i] for i in order]
		curGame.sendSignal("CardShuffled", initiatorID, None, obj, 0, "")
		
	def discardAll(self, ID):
		if self.hands[ID]:
			cards, cost, isRightmostCardinHand = self.extractfromHand(None, all=True, ID=ID, enemyCanSee=True)
			for card in cards:
				PRINT(self.Game, "Card %s in player's hand is discarded:"%card.name)
				for func in card.triggers["Discarded"]: func()
				self.Game.Counters.cardsDiscardedThisGame[ID].append(card.index)
				self.Game.sendSignal("PlayerDiscardsCard", card.ID, None, card, 0, "")					
			self.Game.Manas.calcMana_All()
			
	def discardCard(self, ID, card=None):
		if card is None: #Discard a random card.
			if self.hands[ID]:
				card = npchoice(self.hands[ID])
				card, cost, isRightmostCardinHand = self.extractfromHand(card, enemyCanSee=True)
				PRINT(self.Game, "Card %s in player's hand is discarded:"%card.name)
				for func in card.triggers["Discarded"]: func()
				self.Game.Manas.calcMana_All()
				self.Game.Counters.cardsDiscardedThisGame[ID].append(card.index)
				self.Game.sendSignal("CardLeavesHand", card.ID, None, card, 0, "")
				self.Game.sendSignal("PlayerDiscardsCard", card.ID, None, card, 0, "")
		else: #Discard a chosen card.
			i = card if isinstance(card, (int, np.int32, np.int64)) else self.hands[ID].index(card)
			card = self.hands[ID].pop(i)
			card.leavesHand()
			if self.Game.GUI: self.Game.GUI.cardsLeaveHandAni(card, enemyCanSee=True)
			PRINT(self.Game, "Card %s in player's hand is discarded:"%card.name)
			for func in card.triggers["Discarded"]: func()
			self.Game.Manas.calcMana_All()
			self.Game.Counters.cardsDiscardedThisGame[ID].append(card.index)
			self.Game.sendSignal("CardLeavesHand", card.ID, None, card, 0, "")
			self.Game.sendSignal("PlayerDiscardsCard", card.ID, None, card, 0, "")					
			
	#只能全部拿出手牌中的所有牌或者拿出一个张，不能一次拿出多张指定的牌
	def extractfromHand(self, card, all=False, ID=0, enemyCanSee=False):
		if all: #Extract the entire hand.
			temp = self.hands[ID]
			self.hands[ID] = []
			for card in temp:
				card.leavesHand()
				self.Game.sendSignal("CardLeavesHand", card.ID, None, card, 0, '')
			#一般全部取出手牌的时候都是直接洗入牌库，一般都不可见
			if self.Game.GUI: self.Game.GUI.cardsLeaveHandAni(temp, False)
			return temp, 0, -2 #-2 means the positioninHand doesn't have real meaning.
		else:
			if not isinstance(card, (int, np.int32, np.int64)):
				#Need to keep track of the card's location in hand.
				for i in range(len(self.hands[card.ID])):
					if self.hands[card.ID][i] == card:
						index, cost = i, card.mana
						break
				positioninHand = index if index < len(self.hands[card.ID]) -1 else -1
				card = self.hands[card.ID].pop(index)
			else: #card is a number
				positioninHand = card if card < len(self.hands[ID]) -1 else -1
				card = self.hands[ID].pop(card)
				cost = card.mana
			card.leavesHand()
			if self.Game.GUI: self.Game.GUI.cardsLeaveHandAni(card, enemyCanSee)
			self.Game.sendSignal("CardLeavesHand", card.ID, None, card, 0, '')
			return card, cost, positioninHand
	#只能全部拿牌库中的所有牌或者拿出一个张，不能一次拿出多张指定的牌
	def extractfromDeck(self, card, ID=0, all=False):
		if all: #For replacing the entire deck or throwing it away.
			temp = self.decks[ID]
			self.decks[ID] = []
			for card in temp: card.leavesDeck()
			return temp, 0, False
		else:
			if not isinstance(card, (int, np.int32, np.int64)): card = extractfrom(card, self.decks[card.ID])
			else: card = self.decks[ID].pop(card)
			card.leavesDeck()
			return card, 0, False
			
	def removeDeckTopCard(self, ID):
		try: #Should have card most of the time.
			card = self.decks[ID].pop(0)
			card.leavesDeck()
			PRINT(self.Game, "The top card %s in player %d's deck is removed"%(card.name, ID))
			return card
		except: return None
			
	def createCopy(self, game):
		if self not in game.copiedObjs:
			Copy = type(self)(game)
			game.copiedObjs[self] = Copy
			Copy.startingDeckIdentities, Copy.startingHandIdentities = self.startingDeckIdentities, self.startingHandIdentities
			Copy.initialDecks = self.initialDecks
			Copy.hands, Copy.decks = {1:[], 2:[]}, {1:[], 2:[]}
			Copy.knownDecks = {1:{"to self":[]}, 2:{"to self":[]}}
			Copy.noCards, Copy.handUpperLimit = copy.deepcopy(self.noCards), copy.deepcopy(self.handUpperLimit)
			Copy.decks = {1: [card.createCopy(game) for card in self.decks[1]], 2: [card.createCopy(game) for card in self.decks[2]]}
			Copy.hands = {1: [card.createCopy(game) for card in self.hands[1]], 2: [card.createCopy(game) for card in self.hands[2]]}
			return Copy
		else:
			return game.copiedObjs[self]
			
			
Default1 = [ElvenArcher, ElvenArcher, JunglePanther, JunglePanther, JunglePanther, JunglePanther]

Default2 = [ElvenArcher, ElvenArcher, ElvenArcher, ElvenArcher, ElvenArcher, ElvenArcher, ElvenArcher, ElvenArcher, ElvenArcher, ]