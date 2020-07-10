from VariousHandlers import *
from Triggers_Auras import Trigger_Echo

from Basic import Illidan, Anduin

import numpy as np
import copy
import time

def extractfrom(target, listObject):
	try: return listObject.pop(listObject.index(target))
	except: return None
	
def fixedList(listObject):
	return listObject[0:len(listObject)]
	
def belongstoClass(string, Class):
	return Class in string
	
def PRINT(game, string, *args):
	if game.GUI:
		if not game.mode: game.GUI.printInfo(string)
	elif not game.mode: print("game's guide mode is 0\n", string)
	
statusDict = {"Immune": 0, "Immune2NextTurn": 0, "ImmuneThisTurn": 0,
				"Evasive": 0, "Evasive2NextTurn": 0,
				"Spell Damage": 0, "Spells Lifesteal": 0, "Spells x2": 0, "Spells Sweep": 0,
				
				"Power Sweep": 0, "Power Damage": 0, #Power Damage.
				"Power Can Target Minions": 0,
				"Heal to Damage": 0,
				"Choose Both": 0,
				"Battlecry x2": 0, "Shark Battlecry x2": 0,
				"Deathrattle x2": 0, "Weapon Deathrattle x2": 0,
				"Summon x2": 0, "Secrets x2": 0,
				"Minions Can't Be Frozen": 0, #Living Dragonbreath prevents minions from being Frozen
				"Ignore Taunt": 0, #Kayn Sunfury allows player to ignore Taunt
				}
				
				
class Game:
	def __init__(self, GUI=None, player1=None, player2=None):
		self.mainPlayerID = np.random.randint(2) + 1
		self.GUI = GUI
		
	def initialize(self, cardPool, MinionsofCost, RNGPools, hero1=None, hero2=None, deck1=[], deck2=[]):
		self.heroes = {1:(Illidan if hero1 == None else hero1)(self, 1), 2:(Anduin if hero2 == None else hero2)(self, 2)}
		self.powers = {1:self.heroes[1].heroPower, 2:self.heroes[2].heroPower}
		self.heroes[1].onBoard, self.heroes[2].onBoard = True, True
		#Multipole weapons can coexitst at minions in lists. The newly equipped weapons are added to the lists
		self.minions, self.weapons = {1:[], 2:[]}, {1:[], 2:[]}
		self.options, self.mulligans = [], {1:[], 2:[]}
		self.players = {1:None, 2:None}
		#handlers.
		self.Counters, self.Manas, self.Discover, self.Secrets, self.DmgHandler = Counters(self), Manas(self), Discover(self), Secrets(self), DmgHandler(self)
		
		self.minionPlayed = None #Used for target change induced by triggers such Mayor Noggenfogger and Spell Bender.
		self.gameEnds, self.turn = 0, 1
		#self.turnstoTake = {1:1, 2:1} #For Temporus & Open the Waygate
		self.tempDeads, self.deads = [[], []], [[], []] #1st list records dead objects, 2nd records object attacks when they die.
		self.resolvingDeath = False
		self.tempImmuneStatus = {"ImmuneThisTurn": 0, "Immune2NextTurn":0}
		self.status = {1:statusDict, 2:copy.deepcopy(statusDict)}
		self.turnStartTrigger, self.turnEndTrigger = [], [] #用于一个回合的光环的取消
		self.auras = [] #用于一些永久光环，如砰砰博士的机械获得突袭。
		#登记了的扳机，这些扳机的触发依次遵循主玩家的场上、手牌和牌库。然后是副玩家的场上、手牌和牌库。
		self.triggersonBoard, self.triggersinHand, self.triggersinDeck = {1:[], 2:[]}, {1:[], 2:[]}, {1:[], 2:[]}
		self.cardPool, self.MinionsofCost, self.RNGPools = cardPool, MinionsofCost, RNGPools
		from Hand import Hand_Deck
		self.Hand_Deck = Hand_Deck(self, deck1, deck2)
		self.Hand_Deck.initialize()
		self.mode, self.withAnimation = 0, False
		self.fixedGuides, self.guides, self.moves = [], [], []
		
	def minionsAlive(self, ID, target=None):
		minions = []
		if target: #Return all living minions except target.
			for minion in self.minions[ID]:
				if minion.type == "Minion" and minion != target and minion.onBoard and minion.dead == False and minion.health > 0:
					minions.append(minion)
		else: #Return all living minions.
			for minion in self.minions[ID]:
				if minion.type == "Minion" and minion.onBoard and minion.dead == False and minion.health > 0:
					minions.append(minion)
		return minions
		
	#For AOE deathrattles.
	def minionsonBoard(self, ID, target=None):
		minions = []
		if target: #Return all minions on board except target.
			for minion in self.minions[ID]:
				if minion.type == "Minion" and minion.onBoard and minion != target:
					minions.append(minion)
			return minions
		else:
			for minion in self.minions[ID]:
				if minion.type == "Minion" and minion.onBoard:
					minions.append(minion)
			return minions
			
	def adjacentMinions2(self, target, countPermanents=False):
		targets, ID, pos, i = [], target.ID, target.position, 0
		while pos > 0:
			pos -= 1
			obj_onLeft = self.minions[ID][pos]
			if not countPermanents and obj_onLeft.type != "Minion": break #If Permanents aren't considered as adjacent entities, they block the search
			elif obj_onLeft.onBoard: #If the minion is not onBoard, skip it; if on board, count it.
				targets.append(obj_onLeft)
				i -= 1
				break
		pos = target.position
		boardSize = len(self.minions[ID])
		while pos < boardSize - 1:
			pos += 1
			obj_onRight = self.minions[ID][pos]
			if countPermanents == False and obj_onRight.type != "Minion": break
			elif obj_onRight.onBoard:
				targets.append(obj_onRight)
				i += 2
				break
		#i = 0 if no adjacent; -1 if only left; 1 if both; 2 if only right
		return targets, i
		
	def charsAlive(self, ID, target=None):
		objs = []
		if target == None:
			if self.heroes[ID].health > 0 and self.heroes[ID].dead == False:
				objs.append(self.heroes[ID])
			for minion in self.minionsonBoard(ID):
				if minion.health > 0 and minion.dead == False:
					objs.append(minion)
		else:
			if self.heroes[ID].health > 0 and self.heroes[ID].dead == False and self.heroes[ID] != target:
				objs.append(self.heroes[ID])
			for minion in self.minionsonBoard(ID):
				if minion.health > 0 and minion.dead == False and minion != target:
					objs.append(minion)
		return objs
		
	#There probably won't be board size limit changing effects.
	#Minions to die will still count as a placeholder on board. Only minions that have entered the tempDeads don't occupy space.
	def space(self, ID):
		num = 7
		for minion in self.minions[ID]:
			if minion.onBoard: num -= 1 #Minions and Permanents both occupy space as long as they are on board.
		return num
		
	def playMinion(self, minion, target, position, choice=0, comment=""):
		ID, canPlayMinion = minion.ID, False
		if not self.Manas.affordable(minion): PRINT(self, "Not enough mana to play minion {}".format(minion))
		elif self.space(ID) < 1: PRINT(self, "No more minion can be played.")
		else:
			if minion.selectionLegit(target, choice): canPlayMinion = True
			else: PRINT(self, "Invalid selection to play minion {}, targeting {}, with choice {}".format(minion.name, target, choice))
			
		if canPlayMinion:
			PRINT(self, "	   *******\nHandling play minion {} with target {}, with choice: {}\n	   *********".format(minion.name, target, choice))
			#打出随从到所有结算完结为一个序列，序列完成之前不会进行胜负裁定。
			#打出随从产生的序列分为 
				#1）使用阶段： 支付费用，随从进入战场（处理位置和刚刚召唤等），抉择变形类随从立刻提前变形，黑暗之主也在此时变形。
					#如果随从有回响，在此时决定其将在完成阶段结算回响
					#使用时阶段：使用时扳机，如伊利丹，任务达人和魔能机甲等
					#召唤时阶段：召唤时扳机，如鱼人招潮者，饥饿的秃鹫等
					#得到过载
					###开始结算死亡事件。此时序列还没有结束，不用处理胜负问题。
				#2）结算阶段： 根据随从的死亡，在手牌、牌库和场上等位置来决定战吼，战吼双次的扳机等。
					#开始时判定是否需要触发多次战吼，连击
					#指向型战吼连击和抉择随机选取目标。如果此时场上没有目标，则不会触发 对应指向部分效果和它引起的效果。
					#抉择和磁力也在此时结算，不过抉择变形类随从已经提前结算，此时略过。
					###开始结算死亡事件，不必处理胜负问题。
				#3）完成阶段
					#召唤后步骤：召唤后扳机触发：如飞刀杂耍者，船载火炮等
					#将回响牌加入打出者的手牌
					#使用后步骤：使用后扳机：如镜像实体，狙击，顽石元素。低语元素的状态移除结算和dk的技能刷新等。
					###结算死亡，此时因为序列结束可以处理胜负问题。
					
			#在打出序列的开始阶段决定是否要产生一个回响copy
			if self.withAnimation and self.GUI:
				self.GUI.updateCardinResolution(minion)
			hasEcho = False
			if minion.keyWords["Echo"] > 0:
				hasEcho = True
				echoCard = type(minion)(self, self.turn)
				trigger = Trigger_Echo(echoCard)
				echoCard.triggersinHand.append(trigger)
				
			subIndex, subWhere = self.Hand_Deck.hands[minion.ID].index(minion), "hand%d"%minion.ID
			if target:
				if target.type == "Minion": tarIndex, tarWhere = target.position, "minion%d"%target.ID
				else: tarIndex, tarWhere = target.ID, "hero"
			else: tarIndex, tarWhere = 0, ''
			minion, mana, positioninHand = self.Hand_Deck.extractfromHand(minion)
			minionIndex = minion.index
			self.Manas.payManaCost(minion, mana) #海魔钉刺者，古加尔和血色绽放的伤害生效。
			#The new minion played will have the largest sequence.
			#处理随从的位置的登场顺序。
			minion.sequence = len(self.minions[1]) + len(self.minions[2]) + len(self.weapons[1]) + len(self.weapons[2])
			if position < 0: self.minions[ID].append(minion)
			else: self.minions[ID].insert(position, minion)
			self.rearrangePosition()
			#使用随从牌、召唤随从牌、召唤结束信号会触发
				#把本回合召唤随从数的计数提前至打出随从之前，可以让小个子召唤师等“每回合第一张”光环在随从打出时正确结算。连击等结算仍依靠cardsPlayedThisTurn
			self.Counters.numMinionsPlayedThisTurn[self.turn] += 1
			self.minionPlayed = minion
			triggersAllowed = self.triggersAllowed("MinionBeenPlayed")
			if self.withAnimation and self.GUI:
				self.GUI.wait(0.4)
			target = minion.played(target, choice, mana, positioninHand, comment)
			#完成阶段
			#只有当打出的随从还在场上的时候，飞刀杂耍者等“在你召唤一个xx随从之后”才会触发。当大王因变形为英雄而返回None时也不会触发。
			#召唤后步骤，触发“每当你召唤一个xx随从之后”的扳机，如飞刀杂耍者，公正之剑和船载火炮等
			if self.minionPlayed and self.minionPlayed.onBoard:
				self.sendSignal("MinionBeenSummoned", self.turn, self.minionPlayed, target, mana, "")
			self.Counters.numCardsPlayedThisTurn[self.turn] += 1
			#假设打出的随从被对面控制的话仍然会计为我方使用的随从。被对方变形之后仍记录打出的初始随从
			self.Counters.cardsPlayedThisTurn[self.turn]["Indices"].append(minionIndex)
			self.Counters.cardsPlayedThisTurn[self.turn]["ManasPaid"].append(mana)
			self.Counters.cardsPlayedThisGame[self.turn].append(minionIndex)
			#将回响牌加入打出者的手牌
			if hasEcho: self.Hand_Deck.addCardtoHand(echoCard, self.turn)
			#使用后步骤，触发镜像实体，狙击，顽石元素等“每当你使用一张xx牌”之后的扳机。
			if self.minionPlayed and self.minionPlayed.type == "Minion":
				if self.minionPlayed.identity not in self.Hand_Deck.startingDeckIdentities[self.turn]:
					self.Counters.createdCardsPlayedThisGame[self.turn] += 1
				#The comment here is positioninHand, which records the position a card is played from hand. -1 means the rightmost, 0 means the leftmost
				self.sendSignal("MinionBeenPlayed", self.turn, self.minionPlayed, target, mana, positioninHand, choice, triggersAllowed)
			#............完成阶段结束，开始处理死亡情况，此时可以处理胜负问题。
			self.gathertheDead(True)
			for card in self.Hand_Deck.hands[1] + self.Hand_Deck.hands[2]:
				card.effectCanTrigger()
				card.checkEvanescent()
			PRINT(self, "Making move: playMinion %d %s %d %s"%(subIndex, subWhere, tarIndex, tarWhere))
			self.moves.append(("playMinion", subIndex, subWhere, tarIndex, tarWhere, position, choice))
			
	#召唤随从会成为夹杂在其他的玩家行为中，不视为一个完整的阶段。也不直接触发亡语结算等。
	#This method can also summon minions for enemy.
	#SUMMONING MINIONS ONLY CONSIDERS ONBOARD MINIONS. MINIONS THAT HAVE ENTERED THE tempDeads DON'T COUNT AS MINIONS.
	#Khadgar doubles the summoning from any card, except Invoke-triggererd Galakrond(Galakrond, the Tempest; Galakrond, the Wretched).
	def summonx2(self, subject, position):
		if type(subject) != type([]) and type(subject) != type(np.array([])): #Summon a single minion
			if self.space(subject.ID) > 0:
				newSubjects = [subject, subject.selfCopy(subject.ID)]
				pos = [position, position]
				self.summon(newSubjects, pos, initiatorID, comment="")
		elif len(subject) == 1: #A list that has only 1 minion to summon
			if self.space(subject[0].ID) > 0:
				self.summonx2(subject[0], position[0]) #Go back to doubling a single minion
		else:
			if self.space(subject[0].ID) > 0:
				newSubjects = []
				newPositions = []
				num_orig, pos = len(subject), position[0]
				if position[1] == "totheRightEnd":
					for sub in subject:
						newSubjects.append(sub)
						newSubjects.append(sub.selfCopy(sub.ID))
						newPositions.append(-1)
						newPositions.append(-1)
				elif position[1] == "leftandRight": #Can only be even: 2, 4, 6
					if num_orig == 2:
						newSubjects = [subject[0], subject[0].selfCopy(subject[0].ID), 
										subject[1], subject[1].selfCopy(subject[1].ID)]
						newPositions = [pos+1, pos+1, pos, pos]
					else: #num_orig == 4 or 6
						newSubjects = [subject[0], subject[0].selfCopy(subject[0].ID),
										subject[1], subject[1].selfCopy(subject[1].ID),
										subject[2], subject[2].selfCopy(subject[2].ID)]
						newPositions = [pos+1, pos+1, pos, pos, pos+5, pos+5]
				else: #position[1] == "totheRight":
					for i in range(min(4, num_orig)): #Deathrattle summoning is also handled here.
						newSubjects.append(subject[i])
						newSubjects.append(subject[i].selfCopy(subject[i].ID))
						newPositions.append(pos+1)
						newPositions.append(pos+1)
				#Preprocessing finished, don't invoke doubling. Use the newSubjects and newPositions created.
				self.summon(newSubjects, newPositions, initiatorID, comment="")
				
	#不考虑卡德加带来的召唤数量翻倍。用于被summonMinion引用。
	def summonSingle(self, subject, position):
		ID = subject.ID
		if self.space(ID) > 0:
			subject.sequence = len(self.minions[1]) + len(self.minions[2]) + len(self.weapons[1]) + len(self.weapons[2])
			if position == -1: #Summoning minion on the rightmost position is indicated by -1
				self.minions[subject.ID].append(subject)
			else: #如果position过大，则insert会直接把它接在最末尾
				self.minions[subject.ID].insert(position, subject) #If position > num, the insert() method simply puts it at the end.
			self.rearrangePosition()
			subject.appears()
			if self.withAnimation and self.GUI:
				self.GUI.update()
				self.GUI.wait(0.2)
			self.sendSignal("MinionSummoned", self.turn, subject, None, 0, "")
			self.sendSignal("MinionBeenSummoned", self.turn, subject, None, 0, "")
			return True
		else:
			PRINT(self, "The board is full and no minion can be summoned")
			return False
			
	#只能为同一方召唤随从，如有需要，则多次引用这个函数即可。subject不能是空的
	#注意，卡德加的机制是2 ** n倍。每次翻倍会出现多召唤1个，2个，4个的情况。目前不需要处理3个卡德加的情况，因为7个格子放不下。
	def summon(self, subject, position, initiatorID, comment="Enablex2"):
		if type(subject) != type([]) and type(subject) != type(np.array([])): #Summoning a single minion.
			ID, timesofDoubling = subject.ID, self.status[initiatorID]["Summon x2"]
			if comment == "": #如果是英雄技能进行的召唤，则不会翻倍。
				timesofDoubling = 0
			if timesofDoubling > 0: #最多只需要处理场上有3个卡德加的情况，再多了就放不下了
				numCopiedSummons = 2 ** timesofDoubling - 1
				copies = [subject.selfCopy(ID) for i in range(numCopiedSummons)]
				minionSummoned = self.summonSingle(subject, position)
				if minionSummoned: #只有最初的本体召唤成功的时候才会进行复制的随从的召唤
					minionSummoned = self.summonSingle(copies[0], subject.position+1)
					for i in range(1, numCopiedSummons): #复制的随从列表中剩余的随从，如果没有剩余随从了，直接跳过
						if self.summonSingle(copies[i], copies[i-1].position) == False: #翻倍出来的复制会始终紧跟在初始随从的右边。
							break
					return True #只要第一次召唤出随从就视为召唤成功
				return False
			else:
				return self.summonSingle(subject, position)
		else: #Summoning multiple minions in a row. But the list can be of length 1
			if len(subject) == 1: #用列表形式但是只召唤一个随从的时候，position一定是(self.position, "totheRight")或者（-1, "totheRightEnd"）
				position = position[0] + 1 if position[0] >= 0 else -1
				return self.summon(subject[0], position, initiatorID, comment)
			else: #真正召唤多个随从的时候，会把它们划分为多次循环。每次循环后下次循环召唤的随从紧贴在这次循环召唤的随从的右边。
				if position[1] == "leftandRight":
					centralMinion, totheRight = self.minions[subject[0].ID][position[0]], 1 #必须得到中间的随从的位置
					for i in range(len(subject)):
						if i == 0: pos = centralMinion.position+1 #i == 0 召唤的第一个随从直接出现在传递进来的位置的右+1，没有任何问题。但是之后的召唤需要得知发起随从的位置或者之前召唤的随从的位置
						elif i == 1: pos = centralMinion.position #这个召唤实际上是在列表中插入一个新的随从把中间随从向右挤
						else: #i > 1 向左侧召唤随从也是让新召唤的随从紧贴上一次在左边召唤出来的初始随从。
							pos = subject[i-2].position+1 if totheRight == 1 else subject[i-2].position
							
						minionSummoned = self.summon(subject[i], pos, initiatorID, comment)
						totheRight = 1 - totheRight
						if minionSummoned == False:
							if i == 0: return False #只有第一次召唤就因为没有位置而失败时会返回False
							else: break
					return True
				else: #totheRight or totheRightEnd
					#如果position[1]是"totheRight"，那么position[0]是-2的话会返回pos=1
					pos = -1 if position[1] == "totheRightEnd" else position[0]+1
					for i in range(len(subject)):
						pos = pos if i == 0 else subject[i-1].position+1
						minionSummoned = self.summon(subject[i], pos, initiatorID, comment)
						if minionSummoned == False and i == 0:
							return False
					return True
					
	#一次只从一方的手牌中召唤一个随从。没有列表，从手牌中召唤多个随从都是循环数次检索，然后单个召唤入场的。
	def summonfromHand(self, i, ID, position, initiatorID, comment="Enablex2"):
		subject = self.Hand_Deck.hands[ID][i]
		if self.space(ID) > 0:
			return self.summon(self.Hand_Deck.extractfromHand(subject)[0], position, initiatorID, comment)
		return None
		
	#一次只从一方的牌库中召唤随从。没有列表，从牌库中召唤多个随从都是循环数次检索，然后单个召唤入场的。
	def summonfromDeck(self, i, ID, position, initiatorID, comment="Enablex2"):
		subject = self.Hand_Deck.decks[ID][i]
		if self.space(subject.ID) > 0:
			return self.summon(self.Hand_Deck.extractfromDeck(subject)[0], position, initiatorID, comment)
		return None
		
	def transform(self, target, newMinion):
		ID = target.ID
		if target in self.minions[ID]:
			pos = target.position
			target.disappears(keepDeathrattlesRegistered=False)
			self.removeMinionorWeapon(target)
			if self.minionPlayed == target:
				self.minionPlayed = newMinion
			#removeMinionorWeapon invokes rearrangePosition() and rearrangeSequence()
			newMinion.sequence = len(self.minions[1]) + len(self.minions[2]) + len(self.weapons[1]) + len(self.weapons[2])
			self.minions[ID].insert(pos, newMinion)
			self.rearrangePosition()
			PRINT(self, "{} has been transformed into {}".format(target.name, newMinion.name))
			newMinion.appears()
		elif target in self.Hand_Deck.hands[target.ID]:
			PRINT(self, "Minion {} in hand is transformed into {}".format(target.name, newMinion.name))
			if self.minionPlayed == target:
				self.minionPlayed = newMinion
			self.Hand_Deck.replaceCardinHand(target, newMinion)
		elif target in self.Hand_Deck.decks[target.ID]:
			PRINT(self, "Minion %s is deck and can't be transformed")
			
	#This method is always invoked after the minion.disappears() method.
	def removeMinionorWeapon(self, target):
		if target.type == "Minion" or target.type == "Permanent":
			target.onBoard = False
			extractfrom(target, self.minions[target.ID])
			self.rearrangeSequence()
			self.rearrangePosition()
		elif target.type == "Weapon":
			target.onBoard = False
			extractfrom(target, self.weapons[target.ID])
			self.rearrangeSequence()
			
	#The leftmost minion has position 0.
	#Permanent的位置变化也要考虑
	def rearrangePosition(self):
		for ID in range(1, 3):
			for i in range(len(self.minions[ID])):
				self.minions[ID][i].position = i
				
		self.sendSignal("BoardRearranged", self.turn, None, None, 0, "")
		
	#Rearrange all livng minions' sequences if change is true. Otherwise, just return the list of the sequences.	
	#需要考虑Permanent的出场顺序
	def rearrangeSequence(self):
		sequenceList = []
		#Include players' weapons.
		for weapon in self.weapons[1] + self.weapons[2]:
			sequenceList.append(weapon.sequence)
		for minion in self.minions[1] + self.minions[2]:
			sequenceList.append(minion.sequence)
		#If the sequences will be changed, all minions will be considered.
		rearranged = np.asarray(sequenceList).argsort().argsort()
		#The rearranged array covers both sides, so the code is less straightforward.
		i = 0
		for weapon in self.weapons[1] + self.weapons[2]:
			weapon.sequence = rearranged[i]
			i += 1
		for minion in self.minions[1] + self.minions[2]:
			minion.sequence = rearranged[i]
			i += 1
			
	def returnMiniontoHand(self, target, keepDeathrattlesRegistered=False, manaModification=None):
		if target in self.minions[target.ID]: #如果随从仍在随从列表中
			if self.Hand_Deck.handNotFull(target.ID):
				ID, identity = target.ID, target.identity
				#如果onBoard仍为True，则其仍计为场上存活的随从，需调用disappears以注销各种扳机。
				if target.onBoard: #随从存活状态下触发死亡扳机的区域移动效果时，不会注销其他扳机
					target.disappears(keepDeathrattlesRegistered)
				#如onBoard为False,则disappears已被调用过了。主要适用于触发死亡扳机中的区域移动效果
				self.removeMinionorWeapon(target)
				target.__init__(self, ID)
				PRINT(self, "%s has been reset after returned to owner's hand. All enchantments lost."%target.name)
				target.identity[0], target.identity[1] = identity[0], identity[1]
				if manaModification:
					manaModification.applies()
				self.Hand_Deck.addCardtoHand(target, ID)
				return target
			else: #让还在场上的活着的随从返回一个满了的手牌只会让其死亡
				if target.onBoard:
					PRINT(self, "%s dies because player's hand is full."%target.name)
					self.destroyMinion(target)
				return None #如果随从这时已死亡，则满手牌下不会有任何事情发生。
		elif target.inDeck: #如果目标阶段已经在牌库中了，将一个基础复制置入其手牌。
			Copy = type(target)(self, target.ID)
			self.Hand_Deck.addCardtoHand(Copy, target.ID)
			return Copy
		elif target.inHand:
			return target
		else: #The target is dead and removed already
			return None
			
	#targetDeckID decides the destination. initiatorID is for triggers, such as Trigger_AugmentedElekk
	def returnMiniontoDeck(self, target, targetDeckID, initiatorID, keepDeathrattlesRegistered=False):
		if target in self.minions[target.ID]:
			ID, identity = targetDeckID, target.identity
			#如果onBoard仍为True，则其仍计为场上存活的随从，需调用disappears以注销各种扳机
			if target.onBoard: #随从存活状态下触发死亡扳机的区域移动效果时，不会注销其他扳机
				target.disappears(keepDeathrattlesRegistered)
			#如onBoard为False，则disappears已被调用过了。主要适用于触发死亡扳机中的区域移动效果
			self.removeMinionorWeapon(target)
			target.__init__(self, ID) #永恒祭司的亡语会备份一套enchantment，在调用该函数之后将初始化过的本体重新增益
			PRINT(self, "%s has been reset after returned to deck %d. All enchantments lost"%(target.name, ID))
			target.identity[0], target.identity[1] = identity[0], identity[1]
			self.Hand_Deck.shuffleCardintoDeck(target, initiatorID)
			return target
		elif target.inHand: #如果随从已进入手牌，仍会将其强行洗入牌库
			self.Hand_Deck.shuffleCardintoDeck(self.Hand_Deck.extractfromHand(target)[0])
			return target
		else:
			return None
			
	def destroyMinion(self, target):
		#如果随从在场上只是将其dead标志改为True;而如果随从在手牌中，则直接将其丢弃。
		if target in self.minions[target.ID]:
			target.dead = True
		elif target.inHand:
			self.Hand_Deck.discard(target.ID, target)
			
	def minionSwitchSide(self, target, activity="Permanent"):
		#如果随从在手牌中，则该会在手牌中换边；如果随从在牌库中，则无事发生。
		if target.inHand and target in self.Hand_Deck.hands[target.ID]:
			card, mana, positioninHand = self.Hand_Deck.extractfromHand(target)
			#addCardtoHand method will force the ID of the card to change to the target hand ID.
			#If the other side has full hand, then the card is extracted and thrown away.
			self.Hand_Deck.addCardtoHand(card, 3-card.ID)
		elif target.onBoard: #If the minion is on board.
			if self.space(3-target.ID) < 1:
				PRINT(self, "%s dies because there is no available spots for it."%target.name)
				target.dead = True
			else:
				target.disappears(keepDeathrattlesRegistered=False) #随从控制权的变更会注销其死亡扳机，随从会在另一方重新注册其所有死亡扳机
				target = extractfrom(target, self.minions[target.ID])
				target.ID = 3 - target.ID
				self.minions[target.ID].append(target)
				self.rearrangePosition() #The appearance sequence stays intact.
				target.appears()
				
				#Possible activities are "Permanent" "Borrow" "Return"
				#每个随从只有携带一个回合结束后将随从归为对方的turnEndTrigger
				#被暂时控制的随从如果被无面操纵者复制，复制者也可以攻击，回合时，连同复制者一并归还对面。
				if activity == "Borrow":
					if target.status["Borrowed"] < 1:
						target.status["Borrowed"] = 1
						#因为回合结束扳机的性质，只有第一个同类扳机会触发，因为后面的扳机检测时会因为ID已经不同于当前回合的ID而不能继续触发
						trigger = Trigger_ShadowMadness(target)
						trigger.connect()
						target.triggersonBoard.append(trigger)
				else: #Return or permanent
					target.status["Borrowed"] = 0
					#假设归还或者是控制对方随从的时候会清空所有暂时控制的标志，并取消回合结束归还随从的扳机
					#将triggersonBoard中的Trigger_ShadowMadness 实例全部断开连接并清除
					numTriggers = len(target.triggersonBoard)
					for i in range(numTriggers):
						if type(target.triggersonBoard[numTriggers-1-i]) == Trigger_ShadowMadness:
							target.triggersonBoard[numTriggers-1-i].disconnect()
							
				target.afterSwitchSide(activity)
				
	#Given a list of targets to sort, return the list that 
	#contains the targets in the right order to trigger.
	def sort_Sequence(self, targets):
		sequences = []
		temp = targets
		for target in targets:
			sequences.append(target.sequence)
		order = np.asarray(sequences).argsort()
		targets = []
		for i in range(len(order)):
			targets.append(temp[order[i]])
			
		return targets, order
		
	def triggersAllowed(self, signal):
		mainPlayerID, triggers = self.mainPlayerID, []
		for ID in [mainPlayerID, 3-mainPlayerID]:
			for trigger, sig in self.triggersonBoard[ID]+self.triggersinHand[ID]+self.triggersinDeck[ID]:
				if sig == signal: #只检测信号是否匹配。
					triggers.append(trigger)
		return triggers
		
	#During the triggering, if another signal is send, the response to the new signal will be interpolated.
	#When the signal is sent to triggers, only the triggers that have been present from the beginning will respond. Those added after the signal being sent won't respond.
	#pydispatch.dispatcher doesn't meet this requirement.
	def sendSignal(self, signal, ID, subject, target, number, comment, choice=0, triggerPool=None):
		if triggerPool: #主要用于打出xx牌和随从死亡时/后扳机，它们有预检测机制。
			for trigger in triggerPool: #扳机只有仍被注册情况下才能触发。
				if trigger.canTrigger(signal, ID, subject, target, number, comment, choice):
					if (trigger, signal) in self.triggersonBoard[1] + self.triggersinHand[1] + self.triggersinDeck[1] + self.triggersonBoard[2] + self.triggersinHand[2] + self.triggersinDeck[2]:
						trigger.trigger(signal, ID, subject, target, number, comment, choice)
		else: #向所有注册的扳机请求触发。
			mainPlayerID = self.mainPlayerID #如果中途主副玩家发生变化，则结束此次信号的结算之后，下次再扳机触发顺序。
			#Trigger the triggers on main player's side, in the following order board-> hand -> deck.
			#先触发主玩家的各个位置的扳机。
			for triggerID in [mainPlayerID, 3-mainPlayerID]:
			#场上扳机先触发
				triggersinPlay = []
				for trigger, sig in self.triggersonBoard[triggerID]:
					#只有满足扳机条件的扳机才会被触发。
					if sig == signal and trigger.canTrigger(signal, ID, subject, target, number, comment, choice):
						triggersinPlay.append(trigger)
				#某个随从死亡导致的队列中，作为场上扳机，救赎拥有最低优先级，其始终在最后结算
				if signal == "MinionDies" and self.Secrets.sameSecretExists(Redemption, 3-self.turn):
					for i in range(len(triggersinPlay)):
						if type(triggersinPlay[i]) == Trigger_Redemption:
							triggersinPlay.append(triggersinPlay.pop(i)) #把救赎的扳机移到最后
							break
				for trigger in triggersinPlay:
					trigger.trigger(signal, ID, subject, target, number, comment, choice)
			#然后是手牌扳机
				triggersinPlay = []
				for trigger, sig in self.triggersinHand[triggerID]:
					if sig == signal and trigger.canTrigger(signal, ID, subject, target, number, comment, choice):
						triggersinPlay.append(trigger)
				for trigger in triggersinPlay:
					trigger.trigger(signal, ID, subject, target, number, comment, choice)
			#最后是牌库扳机
				triggersinPlay = []
				for trigger, sig in self.triggersinDeck[triggerID]:
					#只有满足扳机条件的扳机才会被触发。
					if sig == signal and trigger.canTrigger(signal, ID, subject, target, number, comment, choice):
						triggersinPlay.append(trigger)
				for trigger in triggersinPlay:
					trigger.trigger(signal, ID, subject, target, number, comment, choice)
					
	#The weapon will also join the deathList and compare its own sequence against other minions.
	def gathertheDead(self, decideWinner=False):
		#Determine what characters are dead. The die() method hasn't been invoked yet.
		#序列内部不包含胜负裁定，即只有回合开始、结束产生的序列；
		#回合开始抽牌产生的序列；打出随从，法术，武器，英雄牌产生的序列；
		#以及战斗和使用英雄技能产生的序列以及包含的所有亡语等结算结束之后，胜负才会被结算。
		for ID in range(1, 3):
			#Register the weapons to destroy.(There might be multiple weapons in queue, 
			#since you can trigger Tirion Fordring's deathrattle twice and equip two weapons in a row.)
			#Pop all the weapons until no weapon or the latest weapon equipped.
			while self.weapons[ID] != []:
				if self.weapons[ID][0].durability < 1 or self.weapons[ID][0].dead:
					self.weapons[ID][0].destroyed() #武器的被摧毁函数，负责其onBoard, dead和英雄风怒，攻击力和场上扳机的移除等。
					weapon = self.weapons[ID].pop(0)
					self.Counters.weaponsDestroyedThisGame[weapon.ID].append(weapon.index)
					self.tempDeads[0].append(weapon)
					self.tempDeads[1].append(weapon.attack)
				else: #If the weapon is the latest weapon to equip
					break
			for minion in fixedList(self.minionsonBoard(ID)):
				if minion.health < 1 or minion.dead:
					minion.dead = True
					attackwhenDies = minion.attack
					#随从被记为已死亡时需要将其onBoard置为False，从而之后不会重复计算随从的死亡
					self.tempDeads[0].append(minion)
					self.tempDeads[1].append(minion.attack)
					minion.disappears(keepDeathrattlesRegistered=True) #随从死亡时不会注销其死亡扳机，这些扳机会在触发之后自行注销
					self.Counters.minionsDiedThisTurn[minion.ID].append(minion.index)
					self.Counters.minionsDiedThisGame[minion.ID].append(minion.index)
					if "Mech" in minion.race:
						#List: [ [mechIndex, [magnetic upgrades]] ]
						self.Counters.mechsDiedThisGame[minion.ID].append([minion.index, minion.history["Magnetic Upgrades"]])
			if self.heroes[ID].health < 1:
				self.heroes[ID].dead = True
				
		if self.tempDeads != [[], []]:
			#Rearrange the dead minions according to their sequences.
			self.tempDeads[0], order = self.sort_Sequence(self.tempDeads[0])
			temp = self.tempDeads[1]
			self.tempDeads[1] = []
			for i in range(len(order)):
				self.tempDeads[1].append(temp[order[i]])
			PRINT(self, "The new dead minions/weapons to resolve death/destruction are {}".format(self.tempDeads[0]))
			#If there is no current deathrattles queued, start the deathrattle calc process.
			if self.deads == [[], []]:
				self.deads = self.tempDeads
			else:
				#If there is deathrattle in queue, simply add new deathrattles to the existing list.
				self.deads[0] += self.tempDeads[0]
				self.deads[1] += self.tempDeads[1]
				
			#The content stored in self.tempDeads must be released.
			#Clean the temp list to wait for new input.
			self.tempDeads = [[], []]
			if self.withAnimation and self.GUI:
				self.GUI.wait(0.5)
				
		if self.resolvingDeath == False: #如果游戏目前已经处于死亡结算过程中，不会再重复调用deathHandle
			#如果要执行胜负判定或者有要死亡/摧毁的随从/武器，则调用deathHandle
			if decideWinner or self.deads != [[], []]:
				self.deathHandle(decideWinner)
				
	#大法师施放的闷棍会打断被闷棍的随从的回合结束结算。可以视为提前离场。
	#死亡缠绕实际上只是对一个随从打1，然后如果随从的生命值在1以下，则会触发抽牌。它不涉及强制死亡导致的随从提前离场
	#当一个拥有多个亡语的随从死亡时，多个亡语触发完成之后才会开始结算其他随从死亡的结算。
	#每次gathertheDead找到要死亡的随从之后，会在它们这一轮的死亡事件全部处理之后，才再次收集死者，用于下次死亡处理。
		#复生随从也会在一轮死亡结算之后统一触发。
	def deathHandle(self, decideWinner=False):
		while True:
			rebornMinions = []
			if self.deads == [[], []]: #If no minions are dead, then stop the loop
				break
			triggersAllowed_WhenDies = self.triggersAllowed("MinionDies") + self.triggersAllowed("WeaponDestroyed")
			triggersAllowed_AfterDied = self.triggersAllowed("MinionDied")
			PRINT(self, "The dead/destroyed characters to handle are:")
			for i in range(len(self.deads[0])):
				PRINT(self, "\tCharacter: {}	Attack when dies: {}".format(self.deads[0][i].name, self.deads[1][i]))
			while self.deads != [[], []]:
				self.resolvingDeath = True
				objtoDie, attackwhenDies = self.deads[0][0], self.deads[1][0]
				#For now, assume Tirion Fordring's deathrattle equipping Ashbringer won't trigger player's weapon's deathrattles right away.
				#weapons with regard to deathrattle triggering is handled the same way as minions.
				PRINT(self, "Now handling the death/destruction of {}".format(objtoDie.name))
				#一个亡语随从另附一个亡语时，两个亡语会连续触发，之后才会去结算其他随从的亡语。
				#当死灵机械师与其他 亡语随从一同死亡的时候， 不会让那些亡语触发两次，即死灵机械师、瑞文戴尔需要活着才能有光环
				#场上有憎恶时，憎恶如果死亡，触发的第一次AOE杀死死灵机械师，则第二次亡语照常触发。所以亡语会在第一次触发开始时判定是否会多次触发
				if objtoDie.type == "Minion" and objtoDie.keyWords["Reborn"] > 0:
					rebornMinions.append(objtoDie)
				objtoDie.deathResolution(attackwhenDies, triggersAllowed_WhenDies, triggersAllowed_AfterDied)
				self.removeMinionorWeapon(objtoDie) #结算完一个随从的亡语之后将其移除。
				objtoDie.__init__(self, objtoDie.ID)
				objtoDie.dead = True
				self.deads[0].pop(0)
				self.deads[1].pop(0)
			#当一轮死亡结算结束之后，召唤这次死亡结算中死亡的复生随从
			for rebornMinion in rebornMinions:
				PRINT(self, "Minion %s died with Reborn. Now a copy with only 1 Health is summoned"%rebornMinion.name)
				miniontoSummon = type(rebornMinion)(self, rebornMinion.ID)
				miniontoSummon.keyWords["Reborn"], miniontoSummon.health = 0, 1 #不需要特殊的身材处理，激怒等直接在随从的appears()函数中处理。
				self.summon(miniontoSummon, rebornMinion.position+1, rebornMinion.ID)
			#死亡结算每轮结束之后才进行死亡随从的收集，然后进行下一轮的亡语结算。
			self.gathertheDead(decideWinner) #See if the deathrattle results in more death or destruction.
			if self.deads == [[], []]: #只有没有死亡随从要结算了才会终结
				break
				
		self.resolvingDeath = False
		
		#The reborn effect take place after the deathrattles of minions have been triggered.
		if decideWinner: #游戏中选手的死亡状态
			hero1Dead, hero2Dead = False, False
			if self.heroes[1].dead or self.heroes[1].health <= 0:
				if self.heroes[2].dead or self.heroes[2].health <= 0:
					self.gameEnds = 3
					PRINT(self, "GAME TIES because both players died.")
				else:
					self.gameEnds = 1
					PRINT(self, "GAME OVER and player 2 wins")
			else:
				if self.heroes[2].dead or self.heroes[2].health <= 0:
					self.gameEnds = 2
					PRINT(self, "GAME OVER and player 1 wins")
				else: self.gameEnds = 0
				
	"""
	At the start of turn, the AOE destroy/AOE damage/damage effect won't kill minions make them leave the board.
	As long as the minion is still on board, it can still trigger its turn start/end effects.
	Special things are Sap/Defile, which will force the minion to leave board early.
	#The Defile will cause the game to preemptively start death resolution.
	Archmage casting spell will be able to target minions with health <= 0, since they are not regarded as dead yet.
	The deaths of minions will be handled at the end of triggering, which is then followed by drawing card.
	"""	
	def switchTurn(self):
		PRINT(self, "----------------\nThe turn ends for hero %d\n-----------------"%self.turn)
		for minion in self.minions[self.turn] + self.minions[3-self.turn]: #Include the Permanents.
			minion.turnEnds(self.turn) #Handle minions' attTimes and attChances
		for card in self.Hand_Deck.hands[self.turn]	+ self.Hand_Deck.hands[3-self.turn]:
			if card.type == "Minion": #Minions in hands will clear their temp buffDebuff
				card.turnEnds(self.turn) #Minions in hands can't defrost
				
		self.heroes[self.turn].turnEnds(self.turn)
		self.heroes[3-self.turn].turnEnds(self.turn)
		self.powers[self.turn].turnEnds(self.turn)
		self.powers[3-self.turn].turnEnds(self.turn)
		self.sendSignal("TurnEnds", self.turn, None, None, 0, "")
		self.gathertheDead(True)
		#The secrets and temp effects are cleared at the end of turn.
		for obj in self.turnEndTrigger: #所有一回合光环都是回合结束时消失，即使效果在自己回合外触发了也是如此
			obj.turnEndTrigger()
			
		self.Counters.turnEnds()
		self.Manas.turnEnds()
		
		self.turn = 3 - self.turn #Changes the turn to another hero.
		PRINT(self, "--------------------\nA new turn starts for hero %d\n-----------------"%self.turn)
		self.Manas.turnStarts()
		for obj in self.turnStartTrigger: #This is for temp effects.
			if obj.ID == self.turn:
				obj.turnStartTrigger()
		self.heroes[self.turn].turnStarts(self.turn)
		self.heroes[3-self.turn].turnStarts(self.turn)
		self.powers[self.turn].turnStarts(self.turn)
		self.powers[3-self.turn].turnStarts(self.turn)
		for minion in self.minions[1] + self.minions[2]: #Include the Permanents.
			minion.turnStarts(self.turn) #Handle minions' attTimes and attChances
		for card in self.Hand_Deck.hands[1]	+ self.Hand_Deck.hands[2]:
			if card.type == "Minion":
				card.turnStarts(self.turn)
				
		self.sendSignal("TurnStarts", self.turn, None, None, 0, "")
		self.gathertheDead(True)
		#抽牌阶段之后的死亡处理可以涉及胜负裁定。
		self.Hand_Deck.drawCard(self.turn)
		self.gathertheDead(True) #There might be death induced by drawing cards.
		for card in self.Hand_Deck.hands[1] + self.Hand_Deck.hands[2]:
			card.effectCanTrigger()
			card.checkEvanescent()
		self.moves.append(("EndTurn", ))
		
	def battle(self, subject, target, verifySelectable=True, consumeAttackChance=True, resolveDeath=True, resetRedirectionTriggers=True):
		if verifySelectable and not subject.canAttackTarget(target):
			PRINT(self, "Battle not allowed between attacker %s and target%s"%(subject.name, target.name))
		else:
			PRINT(self, "			**********\nHandling battle request between %s and %s\n				***********"%(subject.name, target.name))
		#战斗阶段：
			#攻击前步骤： 触发攻击前扳机，列队结算，如爆炸陷阱，冰冻陷阱，误导
				#如果扳机结算完毕后，被攻击者发生了变化，则再次进行攻击前步骤的扳机触发。重复此步骤直到被攻击者没有变化为止。
				#在这些额外的攻击前步骤中，之前已经触发过的攻击前扳机不能再能触发。主要是指市长和傻子
			#攻击时步骤：触发攻击时扳机，如真银圣剑，智慧祝福，血吼，收集者沙库尔等
			#如果攻击者，被攻击目标或者任意一方英雄离场或者濒死，则攻击取消，跳过伤害和攻击后步骤。
			#无论攻击是否取消，攻击者的attackedTimes都会增加。
			#伤害步骤：攻击者移除潜行，攻击者对被攻击者造成伤害，被攻击者对攻击者造成伤害。然后结算两者的伤害事件。
			#攻击后步骤：触发“当你的xx攻击之后”扳机。如捕熊陷阱，符文之矛。
				#蜡烛弓和角斗士的长弓给予的免疫被移除。
			#战斗阶段结束，处理死亡事件
		#如果有攻击之后的发现效果需要结算，则在此结算之后。
			
			
			#如果一个角色被迫发起攻击，如沼泽之王爵德，野兽之心，群体狂乱等，会经历上述的战斗阶段的所有步骤，之后没有发现效果结算。同时角色的attackedTimes不会增加。
			#之后没有阶段间步骤（因为这种强制攻击肯定是由其他序列引发的）
			#疯狂巨龙死亡之翼的连续攻击中，只有第一次目标选择被被市长改变，但之后的不会
			if self.withAnimation and self.GUI:
				#self.GUI.updateCardinResolution(subject)
				self.GUI.wait(0.5)
			if verifySelectable:
				if subject.type == "Minion": subIndex, subWhere = subject.position, "minion%d"%subject.ID
				else: subIndex, subWhere = subject.ID, "hero"
				if target.type  == "Minion": tarIndex, tarWhere = target.position, "minion%d"%target.ID
				else: tarIndex, tarWhere = target.ID, "hero"
			#如果英雄的武器为蜡烛弓和角斗士的长弓，则优先给予攻击英雄免疫，防止一切攻击前步骤带来的伤害。
			self.sendSignal("BattleStarted", self.turn, subject, target, 0, "") #这里的target没有什么意义，可以留为target
			#在此，奥秘和健忘扳机会在此触发。需要记住初始的目标，然后可能会有诸多扳机可以对此初始信号响应。
			targetHolder = [target, target] #第一个target是每轮要触发的扳机会对应的原始随从，目标重导向扳机会改变第二个
			signal = subject.type + "Attacks" + targetHolder[0].type
			PRINT(self, "Battle starts between attacker {} and target {}".format(subject.name, targetHolder[0].name))
			self.sendSignal(signal, self.turn, subject, targetHolder, 0, "1stPre-attack")
			#第一轮攻击前步骤结束之后，Game的记录的target如果相对于初始目标发生了变化，则再来一轮攻击前步骤，直到目标不再改变为止。
			#例如，对手有游荡怪物、误导和毒蛇陷阱，则攻击英雄这个信号可以按扳机入场顺序触发误导和游荡怪物，改变了攻击目标。之后的额外攻击前步骤中毒蛇陷阱才会触发。
			#如果对手有崇高牺牲和自动防御矩阵，那么攻击随从这个信号会将两者都触发，此时攻击目标不会因为这两个奥秘改变。
			#健忘这个特性，如果满足触发条件，且错过了50%几率，之后再次满足条件时也不会再触发这个扳机。这个需要在每个食人魔随从上专门放上标记。
				#如果场上有多个食人魔勇士，则这些扳机都只会在第一次信号发出时触发。
			#如果一个攻击前步骤中，目标连续发生变化，如前面提到的游荡怪物和误导，则只会对最新的目标进行下一次攻击前步骤。
			#如果一个攻击前步骤中，目标连续发生变化，但最终又变回与初始目标相同，则不会产生新的攻击前步骤。
			
			#在之前的攻击前步骤中触发过的扳机不能再后续的额外攻击前步骤中再次触发，主要作用于傻子和市长，因为其他的攻击前扳机都是奥秘，触发之后即消失。
			#只有在攻击前步骤中可能有攻击目标的改变，之后的信号可以大胆的只传递目标本体，不用targetHolder
			while targetHolder[1] != targetHolder[0]: #这里的target只是refrence传递进来的target，赋值过程不会更改函数外原来的target
				targetHolder[0] = targetHolder[1] #攻击前步骤改变了攻击目标，则再次进行攻击前步骤，与这个新的目标进行比对。
				if self.withAnimation and self.GUI:
					self.GUI.target = targetHolder[0]
					self.GUI.wait(0.4)
				signal = subject.type+"Attacks"+targetHolder[0].type #产生新的触发信号。
				self.sendSignal(signal, self.turn, subject, targetHolder, 0, "FollowingPre-attack")
			target = targetHolder[1] #攻击目标改向结束之后，把targetHolder里的第二个值赋给target(用于重导向扳机的那个),这个target不是函数外的target了
			#攻击前步骤结束，开始结算攻击时步骤
			#攻击时步骤：触发“当xx攻击时”的扳机，如真银圣剑，血吼，智慧祝福，血吼，收集者沙库尔等
			signal = subject.type+"Attacking"+target.type
			self.sendSignal(signal, self.turn, subject, target, 0, "")
			#如果此时攻击者，攻击目标或者任意英雄濒死或离场所，则攻击取消，跳过伤害和攻击后步骤。
			battleContinues = True
			#如果目标随从变成了休眠物，则攻击会取消，但是不知道是否会浪费攻击机会。假设会浪费
			if (subject.type != "Minion" and subject.type != "Hero") or subject.onBoard == False or subject.health < 1 or subject.dead:
				PRINT(self, "The attacker is not onBoard/alive anymore. Battle interrupted")
				battleContinues = False
			elif (target.type != "Minion" and target.type != "Hero") or target.onBoard == False or target.health < 1 or target.dead:
				PRINT(self, "The target is not onBoard/alive anymore. Battle interrupted. The attacker's attack chance is still wasted.")
				battleContinues = False
				if consumeAttackChance: #If this attack is canceled, the attack time still increases.
					subject.attTimes += 1
			elif self.heroes[1].health < 1 or self.heroes[1].dead or self.heroes[2].health < 1 or self.heroes[2].dead:
				PRINT(self, "At least one of the players is dying, battle interrupted. But the attacker still wastes an attack chance.")
				battleContinues = False
				if consumeAttackChance: #If this attack is canceled, the attack time still increases.
					subject.attTimes += 1
			if battleContinues:
				#伤害步骤，攻击者移除潜行，攻击者对被攻击者造成伤害，被攻击者对攻击者造成伤害。然后结算两者的伤害事件。
				#攻击者和被攻击的血量都减少。但是此时尚不发出伤害判定。先发出攻击完成的信号，可以触发扫荡打击。
				subject.attacks(target, consumeAttackChance)
				#巨型沙虫的获得额外攻击机会的触发在随从死亡之前结算。同理达利乌斯克罗雷的触发也在死亡结算前，但是有隐藏的条件：自己不能处于濒死状态。
				self.sendSignal(subject.type+"Attacked"+target.type, self.turn, subject, target, 0, "")
				if subject == self.heroes[1] or subject == self.heroes[2]:
					self.Counters.heroAttackTimesThisTurn[subject.ID] += 1
			#重置蜡烛弓，角斗士的长弓，以及傻子和市长的triggeredDuringBattle标识。
			if resetRedirectionTriggers: #这个选项目前只有让一个随从连续攻击其他目标时才会选择关闭，不会与角斗士的长弓冲突
				self.sendSignal("BattleFinished", self.turn, subject, None, 0, "")
			#战斗阶段结束，处理亡语，此时可以处理胜负问题。
			if resolveDeath:
				self.gathertheDead(True)
			for card in self.Hand_Deck.hands[1] + self.Hand_Deck.hands[2]:
				card.effectCanTrigger()
				card.checkEvanescent()
			if verifySelectable:
				self.moves.append(("battle", subIndex, subWhere, tarIndex, tarWhere))
			return battleContinues
	#comment = "InvokedbyAI", "Branching-i", ""(GUI by default) 
	def playSpell(self, spell, target, choice=0, comment=""):
		#np.random.seed(self.seed) #调用之前需要重置随机数生成器的种子
		canPlaySpell = False
		#古加尔的费用光环需要玩家的血量加护甲大于法术的当前费用或者免疫状态下才能使用
		if self.Manas.affordable(spell) == False:
			PRINT(self, "Not enough mana/health to play the spell {}, which costs {}".format(spell, spell.mana))
		else:
			if spell.available() and spell.selectionLegit(target, choice): #Non targeting spells.
				canPlaySpell = True
			else: PRINT(self, "Invalid selection to play spell {}, with choice {}".format(spell.name, choice))
			
		if canPlaySpell:
			PRINT(self, "	   ********\nHandling play spell {} with target {}, with choice: {}\n	   *********".format(spell.name, target, choice))
			#使用阶段：
				#支付费用，相关费用状态移除，包括血色绽放，墨水大师，卡雷苟斯以及暮陨者艾维娜。
				#奥秘和普通法术会进入不同的区域。法术反制触发的话会提前终止整个序列。
				#使用时步骤： 触发伊利丹，紫罗兰老师，法力浮龙等“每当你使用一张xx牌”的扳机
				#获得过载和双重法术。
			#结算阶段
				#目标随机化和修改：市长和扰咒术结算（有主副玩家和登场先后之分）
				#按牌面结算，泽蒂摩不算是扳机，所以只要法术开始结算时在场，那么后面即使提前离场也会使用第二次结算的法术对相信随从生效。
			#完成阶段：
				#如果该牌有回响，结算回响（没有其他牌可以让法术获得回响）
				#使用后步骤：触发“当你使用一张xx牌之后”的扳机，如狂野炎术士，西风灯神，星界密使和风潮的状态移除。
			
			#如果是施放的法术（非玩家亲自打出）
			#获得过载，与双生法术 -> 依照版面描述结算，如有星界密使或者风潮，这个法术也会被重复或者法强增益，但是不会触发泽蒂摩。 -> 星界密使和风潮的状态移除。
			#符文之矛和导演释放的法术也会使用风潮或者星界密使的效果。
			#西风灯神和沃拉斯的效果仅是获得过载和双生法术 ->结算法术牌面
			
			if self.withAnimation and self.GUI:
				self.GUI.updateCardinResolution(spell)
			subIndex, subWhere = self.Hand_Deck.hands[spell.ID].index(spell), "hand%d"%spell.ID
			if target:
				if target.type == "Minion": tarIndex, tarWhere = target.position, "minion%d"%target.ID
				else: tarIndex, tarWhere = target.ID, "hero"
			else: tarIndex, tarWhere = 0, ''
			#支付法力值，结算血色绽放等状态。
			spell, mana, positioninHand = self.Hand_Deck.extractfromHand(spell)
			self.Manas.payManaCost(spell, mana)
			#请求使用法术，如果此时对方场上有法术反制，则取消后续序列。
			#法术反制会阻挡使用时扳机，如伊利丹和任务达人等。但是法力值消耗扳机，如血色绽放，肯瑞托法师会触发，从而失去费用光环
			#被反制掉的法术会消耗“下一张法术减费”光环，但是卡雷苟斯除外（显然其是程序员自己后写的）
			#被反制掉的法术不会触发巨人的减费光环，不会进入你已经打出的法术列表，不计入法力飓风的计数
			#被反制的法术不会被导演们重复施放
			#很特殊的是，连击机制仍然可以通过被反制的法术触发。所以需要一个本回合打出过几张牌的计数器
			#https://www.bilibili.com/video/av51236298?zw
			if self.withAnimation and self.GUI:
				self.GUI.wait(0.5)
			if self.Secrets.sameSecretExists(Counterspell, 3-self.turn):
				PRINT(self, "Player's spell %s played is Countered by Counterspell"%spell.name)
				self.sendSignal("TriggerCounterspell", spell.ID, spell, target, 0, "")
				self.Counters.numCardsPlayedThisTurn[self.turn] += 1 #即使被法术反制取消掉，仍然会触发连击
			else:
				triggersAllowed = self.triggersAllowed("SpellBeenPlayed")
				self.Counters.cardsPlayedThisTurn[self.turn]["Indices"].append(spell.index)
				self.Counters.cardsPlayedThisTurn[self.turn]["ManasPaid"].append(mana)
				spell.played(target, choice, mana, positioninHand, comment) #choice用于抉择选项，comment用于区分是GUI环境下使用还是AI分叉
				self.Counters.numCardsPlayedThisTurn[self.turn] += 1
				self.Counters.numSpellsPlayedThisTurn[self.turn] += 1
				self.Counters.cardsPlayedThisGame[self.turn].append(spell.index)
				#使用后步骤，触发“每当使用一张xx牌之后”的扳机，如狂野炎术士，西风灯神，星界密使的状态移除和伊莱克特拉风潮的状态移除。
				if spell.identity not in self.Hand_Deck.startingDeckIdentities[self.turn]:
					self.Counters.createdCardsPlayedThisGame[self.turn] += 1
				self.sendSignal("SpellBeenPlayed", self.turn, spell, target, mana, positioninHand, choice, triggersAllowed)
				#完成阶段结束，处理亡语，此时可以处理胜负问题。
				self.gathertheDead(True)
				for card in self.Hand_Deck.hands[1] + self.Hand_Deck.hands[2]:
					card.effectCanTrigger()
					card.checkEvanescent()
			self.moves.append(("playSpell", subIndex, subWhere, tarIndex, tarWhere, choice))
			
	def availableWeapon(self, ID):
		for weapon in self.weapons[ID]:
			if weapon.durability > 0 and weapon.onBoard:
				return weapon
		return None
		
	"""Weapon with target will be handle later"""
	def playWeapon(self, weapon, target, choice=0):
		ID = weapon.ID
		if self.Manas.affordable(weapon) == False:
			PRINT(self, "Not enough mana to play the weapon {}".format(weapon))
		else:
			PRINT(self, "	   *******")
			PRINT(self, "Handling play weapon {} with target {}".format(weapon.name, target))
			PRINT(self, "	   *******")
		#使用阶段
			#卡牌从手中离开，支付费用，费用状态移除，但是目前没有根据武器费用支付而产生响应的效果。
			#武器进场，此时武器自身的扳机已经可以开始触发。如公正之剑可以通过触发的伊利丹召唤的元素来触发，并给予召唤的元素buff
			#使用时步骤，触发“每当你使用一张xx牌”的扳机”，如伊利丹，无羁元素等
			#结算过载。
			#结算死亡，尚不处理胜负问题。
		#结算阶段:
			#根据市长和铜须的存在情况决定战吼触发次数和目标（只有一个武器有指向性效果）
			#结算战吼、连击
			#消灭你的旧武器，将列表中前面的武器消灭，触发“每当你装备一把武器时”的扳机。
			#结算死亡（包括武器的亡语。）
		#完成阶段
			#使用后步骤，触发“每当你使用一张xx牌”之后的扳机。如捕鼠陷阱和瑟拉金之种等
			#死亡结算，可以处理胜负问题。
			if self.withAnimation and self.GUI:
				self.GUI.updateCardinResolution(weapon)
			subIndex, subWhere = self.Hand_Deck.hands[weapon.ID].index(weapon), "hand%d"%weapon.ID
			if target:
				if target.type == "Minion": tarIndex, tarWhere = target.position, "minion%d"%target.ID
				else: tarIndex, tarWhere = target.ID, "hero"
			else: tarIndex, tarWhere = 0, ''
			#卡牌从手中离开，支付费用，费用状态移除，但是目前没有根据武器费用支付而产生响应的效果。
			weapon, mana, positioninHand = self.Hand_Deck.extractfromHand(weapon)
			weaponIndex = weapon.index
			self.Manas.payManaCost(weapon, mana)
			#使用阶段，结算阶段。
			triggersAllowed = self.triggersAllowed("WeaponBeenPlayed")
			weapon.played(target, 0, mana, positioninHand, comment="") #There are no weapon with Choose One.
			self.Counters.numCardsPlayedThisTurn[self.turn] += 1
			self.Counters.cardsPlayedThisTurn[self.turn]["Indices"].append(weaponIndex)
			self.Counters.cardsPlayedThisTurn[self.turn]["ManasPaid"].append(mana)
			self.Counters.cardsPlayedThisGame[self.turn].append(weaponIndex)
			#完成阶段，触发“每当你使用一张xx牌”的扳机，如捕鼠陷阱和瑟拉金之种等。
			if weapon.identity not in self.Hand_Deck.startingDeckIdentities[self.turn]:
				self.Counters.createdCardsPlayedThisGame[self.turn] += 1
			self.sendSignal("WeaponBeenPlayed", self.turn, weapon, target, mana, positioninHand, 0, triggersAllowed)
			#完成阶段结束，处理亡语，可以处理胜负问题。	
			self.gathertheDead(True)
			for card in self.Hand_Deck.hands[1] + self.Hand_Deck.hands[2]:
				card.effectCanTrigger()
				card.checkEvanescent()
			self.moves.append(("playWeapon", subIndex, subWhere, tarIndex, tarWhere, 0))
			
	#只是为英雄装备一把武器。结算相对简单
	#消灭你的旧武器，新武器进场，这把新武器设置为新武器，并触发扳机。
	def equipWeapon(self, weapon):
		ID = weapon.ID
		if self.weapons[ID] != []: #There are currently weapons before it.
			for obj in self.weapons[ID]:
				#The destruction of the preivous weapons will be left to the gathertheDead() method.
				obj.destroyed() #如果此时英雄正在攻击，则蜡烛弓和角斗士的长弓仍然可以为英雄提供免疫，因为它们是依靠扳机的。
				
		self.weapons[ID].append(weapon)
		weapon.onBoard = True
		weapon.appears() #新武器的扳机在此登记。
		#武器被设置为英雄的新武器，触发“每当你装备一把武器时”的扳机。”
		weapon.setasNewWeapon()
		
	def playHero(self, heroCard, choice=0):
		ID = heroCard.ID
		if not self.Manas.affordable(heroCard):
			PRINT(self, "Not enough mana to play the hero card {}".format(heroCard))
		else:
			PRINT(self, "	   *******\nHandling play hero card %s\n	   *********"%heroCard.name)
			#使用阶段
				#支付费用，费用状态移除
				#英雄牌进入战场
				#使用时步骤，触发“每当你使用一张xx牌”的扳机，如魔能机甲，伊利丹等。
				#新英雄的最大生命值，当前生命值以及护甲被设定为与旧英雄一致。获得英雄牌上标注的额外护甲。
				#使用阶段结束，结算死亡情况。
			#结算阶段
				#获得新的英雄技能
				#确定战吼触发的次数。
				#结算战吼和抉择。
				#结算阶段结束，处理死亡。
			#完成阶段
				#使用后步骤，触发“每当你使用一张xx牌之后”的扳机。如捕鼠陷阱和瑟拉金之种等
				#完成阶段结束，处理死亡，可以处理胜负问题。
				
			if self.withAnimation and self.GUI:
				self.GUI.updateCardinResolution(heroCard)
			subIndex, subWhere = self.Hand_Deck.hands[heroCard.ID].index(heroCard), "hand%d"%heroCard.ID
			#支付费用，以及费用状态移除
			heroCard, mana, positioninHand = self.Hand_Deck.extractfromHand(heroCard)
			heroCardIndex = heroCard.index
			self.Manas.payManaCost(heroCard, mana)
			#使用阶段，结算阶段的处理。
			triggersAllowed = self.triggersAllowed("HeroCardBeenPlayed")
			heroCard.played(None, choice, mana, positioninHand, comment="")
			self.Counters.numCardsPlayedThisTurn[self.turn] += 1
			self.Counters.cardsPlayedThisTurn[self.turn]["Indices"].append(heroCardIndex)
			self.Counters.cardsPlayedThisTurn[self.turn]["ManasPaid"].append(mana)
			self.Counters.cardsPlayedThisGame[self.turn].append(heroCardIndex)
		#完成阶段
			#使用后步骤，触发“每当你使用一张xx牌之后”的扳机，如捕鼠陷阱等。
			if heroCard.identity not in self.Hand_Deck.startingDeckIdentities[self.turn]:
				self.Counters.createdCardsPlayedThisGame[self.turn] += 1
			self.sendSignal("HeroCardBeenPlayed", self.turn, heroCard, None, mana, positioninHand, choice, triggersAllowed)
			#完成阶段结束，处理亡语，可以处理胜负问题。
			self.gathertheDead(True)
			for card in self.Hand_Deck.hands[1] + self.Hand_Deck.hands[2]:
				card.effectCanTrigger()
				card.checkEvanescent()
			self.moves.append(("playHero", subIndex, subWhere, 0, "", choice))
			
	def createCopy(self, game):
		return game
		
	def copyGame(self, num=1):
		#start = datetime.now()
		copies = [Game(self.GUI, None, None) for i in range(num)]
		for Copy in copies:
			Copy.copiedObjs = {}
			Copy.mainPlayerID, Copy.GUI = self.mainPlayerID, self.GUI
			Copy.cardPool, Copy.MinionsofCost, Copy.RNGPools = self.cardPool, self.MinionsofCost, self.RNGPools
			#t1 = datetime.now()
			Copy.heroes = {1: self.heroes[1].createCopy(Copy), 2: self.heroes[2].createCopy(Copy)}
			Copy.powers = {1: self.powers[1].createCopy(Copy), 2: self.powers[2].createCopy(Copy)}
			Copy.weapons = {1: [weapon.createCopy(Copy) for weapon in self.weapons[1]], 2: [weapon.createCopy(Copy) for weapon in self.weapons[2]]}
			Copy.Hand_Deck = self.Hand_Deck.createCopy(Copy)
			Copy.minions = {1: [minion.createCopy(Copy) for minion in self.minions[1]],
							2: [minion.createCopy(Copy) for minion in self.minions[2]]}
			#t2 = datetime.now()
			#print("Time to copy characters onBoard", datetime.timestamp(t2)-datetime.timestamp(t1))
			#t1 = datetime.now()
			Copy.auras = [aura.createCopy(Copy) for aura in self.auras]
			Copy.mulligans, Copy.options, Copy.tempDeads, Copy.deads = {1:[], 2:[]}, [], [[], []], [[], []]
			Copy.Counters, Copy.Manas = self.Counters.createCopy(Copy), self.Manas.createCopy(Copy)
			Copy.minionPlayed, Copy.gameEnds, Copy.turn, Copy.resolvingDeath = None, self.gameEnds, self.turn, False
			Copy.tempImmuneStatus = self.tempImmuneStatus
			Copy.status = copy.copy(self.status)
			Copy.players = self.players
			Copy.Discover = self.Discover.createCopy(Copy)
			Copy.Secrets, Copy.DmgHandler = self.Secrets.createCopy(Copy), self.DmgHandler.createCopy(Copy)
			#t2 = datetime.now()
			#print("Time to copy various Handlers", datetime.timestamp(t2)-datetime.timestamp(t1))
			#t1 = datetime.now()
			#t2 = datetime.now()
			#print("Time to copy Hands/Decks", datetime.timestamp(t2)-datetime.timestamp(t1))
			#t1 = datetime.now()
			Copy.triggersonBoard, Copy.triggersinHand, Copy.triggersinDeck = {1:[], 2:[]}, {1:[], 2:[]}, {1:[], 2:[]}
			for trigs1, trigs2 in zip([Copy.triggersonBoard, Copy.triggersinHand, Copy.triggersinDeck], [self.triggersonBoard, self.triggersinHand, self.triggersinDeck]):
				for ID in range(1, 3):
					for trig, sig in trigs2[ID]: trigs1[ID].append((trig.createCopy(Copy), sig))
			Copy.turnStartTrigger, Copy.turnEndTrigger = [trig.createCopy(Copy) for trig in self.turnStartTrigger], [trig.createCopy(Copy) for trig in self.turnEndTrigger]
			#t2 = datetime.now()
			#print("Time to copy triggers", datetime.timestamp(t2)-datetime.timestamp(t1))
			Copy.withAnimation, Copy.mode = self.withAnimation, self.mode
			Copy.moves, Copy.fixedGuides, Copy.guides = copy.deepcopy(self.moves), copy.deepcopy(self.fixedGuides), copy.deepcopy(self.guides)
			del Copy.copiedObjs
			
		#finish = datetime.now()
		#print("Total time for copying %d games"%num, datetime.timestamp(finish)-datetime.timestamp(start))
		return copies
		
	def find(self, index, where):
		if where == "minion1":
			print("Minions 1", self.minions[1])
			return self.minions[1][index]
		elif where == "minion2":
			print("Minions 2", self.minions[2])
			return self.minions[2][index]
		elif where == "hand1":
			print(self.Hand_Deck.hands[1])
			return self.Hand_Deck.hands[1][index]
		elif where == "hand2":
			print(self.Hand_Deck.hands[2])
			return self.Hand_Deck.hands[2][index]
		elif where == "power": return self.powers[index]
		elif where == "hero": return self.heroes[index]
		elif where == "deck1": return self.Hand_Deck.decks[1][index]
		elif where == "deck2": return self.Hand_Deck.decks[2][index]
		raise
		
	def evolvewithGuide(self, moves, guides):
		self.fixedGuides, self.guides = fixedList(guides), fixedList(guides)
		for move in moves:
			print("Resolving play command", move)
			self.decodePlay(move)
			if self.withAnimation and self.GUI and move[0] != "EndTurn":
				self.GUI.wait(0.6)
		self.moves, self.fixedGuides, self.guides = [], [], []
		
	def decodePlay(self, move):
		if move[0] == "EndTurn": self.switchTurn()
		else:
			sub = self.find(move[1], move[2])
			tar = self.find(move[3], move[4]) if move[4] != "" else None
			if self.GUI and self.withAnimation:
				self.GUI.subject, self.GUI.target = sub, tar
			if move[0] == "battle": #("battle", subIndex, subWhere, tarIndex, tarWhere)
				self.battle(sub, tar)
			elif move[0] == "playMinion": #("playMinion", subIndex, subWhere, tarIndex, tarWhere, pos, choice)
				self.playMinion(sub, tar, move[5], move[6])
			elif move[0] == "power": #("power", subIndex, subWhere, tarIndex, tarWhere, choice)
				sub.use(tar, move[5])
			else: #play any other types of card from hand #(moveType, subIndex, subWhere, tarIndex, tarWhere, choice)
				getattr(self, move[0])(sub, tar, move[5])
			if self.GUI:
				self.GUI.subject, self.GUI.target = None, None