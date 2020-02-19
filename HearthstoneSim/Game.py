from Hand import *
from VariousHandlers import *

from CardIndices import *
from Witchwood import Trigger_Echo
from LegendaryfromPast import *
import numpy as np
import copy

def extractfrom(target, listObject):
	temp = None
	for i in range(len(listObject)):
		if listObject[i] == target:
			temp = listObject.pop(i)
			break
	return temp
	
def fixedList(listObject):
	return listObject[0:len(listObject)]
	
class Game:
	def __init__(self, player1=None, player2=None):
		self.mainPlayerID = np.random.randint(2) + 1
		self.heroes = {1:Uther(self, 1), 2:Malfurion(self, 2)}
		self.heroPowers = {1:self.heroes[1].heroPower, 2:self.heroes[2].heroPower}
		self.heroes[1].onBoard = True
		self.heroes[2].onBoard = True
		#This is for handling equipping multiple weapons in a row.
		self.weapons = {1:[], 2:[]} #The newly equipped weapon will be added to the weapon list.
		self.minions = {1:[], 2:[]}
		#Hand and deck handler.
		self.mulligans = {1:[], 2:[]}
		#Some other handlers.
		self.ManaHandler = ManaHandler(self)
		self.SecretHandler = SecretHandler(self)
		self.DamageHandler = DamageHandler(self)
		self.DiscoverHandler = DiscoverHandler(self)
		self.options = [] #For discover and Choose One handler
		self.option = None
		self.discoverInitiator = None
		self.players = {1:None, 2:None}
		
		self.target = None #Used for target change induced by triggers such Mayor Noggenfogger and Spell Bender.
		self.turn = 1
		#self.turnstoTake = {1:1, 2:1} #For Temporus & Open the Waygate
		self.deadPlayer = 0
		self.deathList = [[], []] #1st list records dead objects, 2nd records object attacks when they die.
		self.tempDeathList = [[], []]
		self.resolvingDeath = False
		self.tempImmuneStatus = {"ImmuneTillEndofTurn": 0, "ImmuneTillYourNextTurn":0}
		dict = {"Immune": 0,
				"ImmuneTillYourNextTurn": 0,
				"ImmuneTillEndofTurn": 0,
				"Evasive": 0,
				"EvasiveTillYourNextTurn": 0,
				"Spell Damage": 0,
				"Spells Have Lifesteal": 0,
				"Spells Target Adjacent Minions": 0,
				"Spells Cast Twice": 0,
				"Hero Power Target Adjacent Minions": 0,
				"Heal to Damage": 0,
				"Temp Damage Boost": 0, #Hero Power damage boost.
				"Choose Both": 0,
				"Battlecry Trigger Twice": 0,
				"Shark Battlecry Trigger Twice": 0,
				"Deathrattle Trigger Twice": 0,
				"Weapon Deathrattle Trigger Twice": 0,
				"Damage Taken This Turn": 0,
				"Double Summoning by Cards": 0,
				"Hero Takes 1 Damage at a Time": 0,
				"Commanding Shout": 0,
				"Secret Trigger Twice": 0
				}
		self.playerStatus = {1:dict, 2:copy.deepcopy(dict)}
		self.turnStartTrigger = []
		self.turnEndTrigger = []
		self.auras = []
		self.CounterHandler = CounterHandler(self)
		self.triggersonBoard = {1:[], 2:[]} #登记了的扳机，这些扳机的触发依次遵循主玩家的场上、手牌和牌库。
		self.triggersinHand = {1:[], 2:[]} #然后是副玩家的场上、手牌和牌库。
		self.triggersinDeck = {1:[], 2:[]}
		self.cardPool, self.standardCards = {}, {}
		self.cardPool.update(Basic_indices)
		self.cardPool.update(Classic_indices)
		self.cardPool.update(Witchwood_indices)
		self.cardPool.update(Boomsday_indices)
		self.cardPool.update(Rumble_indices)
		self.cardPool.update(RiseofShadows_indices)
		self.standardCards.update(self.cardPool)
		self.ClassCards = ClassCards
		#The entire cardpool also includes the LegendaryMinionsfromPast_All
		self.cardPool.update(LegendaryMinionsfromPast_All)
		self.NeutralMinions = NeutralMinions
		self.MinionswithCertainCost = MinionswithCertainCost
		self.MinionswithRace = MinionswithRace
		self.LegendaryMinions = LegendaryMinions
		#手牌需要留到所有卡池导入之后初始化，因为提前初始化手牌和牌库会导致眼睛卡池不完整的错误。
		self.Hand_Deck = Hand_Deck(self)
		
		
	def endGame(self, comment):
		print(comment)
		exit()
		
	def minionsAlive(self, ID, target=None):
		minions = []
		if target != None: #Return all living minions except target.
			for minion in self.minions[ID]:
				if minion.cardType == "Minion" and minion != target and minion.onBoard and minion.dead == False and minion.health > 0:
					minions.append(minion)
		else: #Return all living minions.
			for minion in self.minions[ID]:
				if minion.cardType == "Minion" and minion.onBoard and minion.dead == False and minion.health > 0:
					minions.append(minion)
		return minions
		
	#For AOE deathrattles.
	def minionsonBoard(self, ID, target=None):
		minions = []
		if target != None: #Return all minions on board except target.
			for minion in self.minions[ID]:
				if minion.cardType == "Minion" and minion.onBoard and minion != target:
					minions.append(minion)
			return minions
		else:
			for minion in self.minions[ID]:
				if minion.cardType == "Minion" and minion.onBoard:
					minions.append(minion)
			return minions
			
	def findAdjacentMinions(self, target):
		targets, ID, pos = [], target.ID, target.position
		leftMinionExists, rightMinionExists = False, False
		while pos > 0:
			pos -= 1
			obj_onLeft = self.minions[ID][pos]
			if obj_onLeft.cardType != "Minion":
				break
			else: #If the object on left is a minion on board, then return it.
				if obj_onLeft.onBoard: #If the minion is not onBoard, skip it.
					targets.append(obj_onLeft)
					leftMinionExists = True
					break
					
		pos = target.position
		boardSize = len(self.minions[ID])
		while pos < boardSize - 1:
			pos += 1
			obj_onRight = self.minions[ID][pos]
			if obj_onRight.cardType != "Minion":
				break
			else: #If the object on left is a minion on board, then return it.
				if obj_onRight.onBoard: #If the minion is not onBoard, skip it.
					targets.append(obj_onRight)
					rightMinionExists = True
					break
					
		if leftMinionExists:
			if rightMinionExists:
				distribution = "Minions on Both Sides"
			else:
				distribution = "Minions Only on the Left"
		else:
			if rightMinionExists:
				distribution = "Minions Only on the Right"
			else:
				distribution = "No Adjacent Minions"
				
		return targets, distribution
		
	#There probably won't be board size limit changing effects.
	#Minions to die will still count as a placeholder on board. Only minions that have entered the tempDeathList don't occupy space.
	def spaceonBoard(self, ID):
		num = 7
		for minion in self.minions[ID]:
			if minion.onBoard: #Minions and Permanents both occupy space as long as they are on board.
				num -= 1
		return num
		
	def playMinion(self, minion, target, position, choice=0, comment=""):
		ID = minion.ID
		self.skipDeathCalc = False
		canPlayMinion = False
		if self.ManaHandler.costAffordable(minion) == False:
			print("Not enough mana to play the minion", minion)	
		elif self.spaceonBoard(ID) < 1:
			print("The board is full and no minion can be played.")
		else:
			if minion.selectionLegit(target, choice):
				canPlayMinion = True
			else:
				print("Invalid selection to play minion %s, targeting"%minion.name, target, " with choice ", choice)
				
		if canPlayMinion:
			print("	   *********\nHandling play minion %s with target "%minion.name, target, ", with choice: ", choice, "\n	   *********")
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
			if minion.keyWords["Echo"] > 0:
				hasEcho = True
				echoCard = type(minion)(self, self.turn)
				trigger = Trigger_Echo(echoCard)
				echoCard.triggersinHand.append(trigger)
				trigger.connect()
			else:
				hasEcho = False
			minion, mana, isRightmostCardinHand = self.Hand_Deck.extractfromHand(minion)
			minionIndex = minion.index
			self.ManaHandler.payManaCost(minion, mana) #海魔钉刺者，古加尔和血色绽放的伤害生效。
			#The new minion played will have the largest sequence.
			#处理随从的位置的登场顺序。
			minion.sequence = len(self.minions[1]) + len(self.minions[2]) + len(self.weapons[1]) + len(self.weapons[2])
			if position < 0:
				self.minions[ID].append(minion)
			else:
				self.minions[ID].insert(position, minion)
			self.rearrangePosition()
			#使用随从牌、召唤随从牌、召唤结束信号会触发
				#把本回合召唤随从数的计数提前至打出随从之前，可以让小个子召唤师等“每回合第一张”光环在随从打出时正确结算。连击等结算仍依靠cardsPlayedThisTurn
			self.CounterHandler.numMinionsPlayedThisTurn[self.turn] += 1
			minion = minion.played(target, choice, mana, comment)
			#假设打出的随从被对面控制的话仍然会计为我方使用的随从。
			self.CounterHandler.cardsPlayedThisTurn[self.turn].append(minionIndex)
			self.CounterHandler.cardsPlayedThisGame[self.turn].append(minionIndex)
			#将回响牌加入打出者的手牌
			if hasEcho:
				self.Hand_Deck.addCardtoHand(echoCard, self.turn)
			#使用后步骤，触发镜像实体，狙击，顽石元素等“每当你使用一张xx牌”之后的扳机。
			if minion != None:
				print("Sending the signal 'MinionBeenPlayed' for minion", minion.name)
				if isRightmostCardinHand:
					self.sendSignal("MinionBeenPlayed", self.turn, minion, self.target, mana, "CardPlayedistheRightmostinHand", choice)
				else:
					self.sendSignal("MinionBeenPlayed", self.turn, minion, self.target, mana, "", choice)
					
			#............完成阶段结束，开始处理死亡情况，此时可以处理胜负问题。
			self.gathertheDead(True)
			
	#召唤随从会成为夹杂在其他的玩家行为中，不视为一个完整的阶段。也不直接触发亡语结算等。
	#This method can also summon minions for enemy.
	#SUMMONING MINIONS ONLY CONSIDERS ONBOARD MINIONS. MINIONS THAT HAVE ENTERED THE TEMPDEATHLIST DON'T COUNT AS MINIONS.
	#Khadgar doubles the summoning from any card, except Invoke-triggererd Galakrond(Galakrond, the Tempest; Galakrond, the Wretched).
	def doubleSummoning(self, subject, position):
		if type(subject) != type([]) and type(subject) != type(np.array([])): #Summon a single minion
			if self.spaceonBoard(subject.ID) > 0:
				newSubjects = [subject, subject.selfCopy(subject.ID)]
				pos = [position, position]
				self.summonMinion(newSubjects, pos, initiatorID, comment="")
		elif len(subject) == 1: #A list that has only 1 minion to summon
			if self.spaceonBoard(subject[0].ID) > 0:
				self.doubleSummoning(subject[0], position[0]) #Go back to doubling a single minion
		else:
			if self.spaceonBoard(subject[0].ID) > 0:
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
				self.summonMinion(newSubjects, newPositions, initiatorID, comment="")
				
	#只能为同一方召唤随从，如有需要，则多次引用这个函数即可
	def summonMinion(self, subject, position, initiatorID, comment="SummoningCanbeDoubled"):
		if comment == "SummoningCanbeDoubled" and self.playerStatus[initiatorID]["Double Summoning by Cards"] > 0:
			self.doubleSummoning(subject, position)
		else:
			if type(subject) != type([]) and type(subject) != type(np.array([])): #Summoning a single minion.
				if self.spaceonBoard(subject.ID) < 1:
					print("The board is full and no minion can be summoned.")
				else: #If there is available spots.
					#The first object to appear on board has Sequence 0.
					subject.sequence = len(self.minions[1]) + len(self.minions[2]) + len(self.weapons[1]) + len(self.weapons[2])
					if position == -1: #Summoning minion on the rightmost position is indicated by -1
						self.minions[subject.ID].append(subject)
					else:
						self.minions[subject.ID].insert(position, subject) #If position > num, the insert() method simply puts it at the end.
					self.rearrangePosition()
					subject.appears()
					self.sendSignal("MinionSummoned", self.turn, subject, None, 0, "")
					self.sendSignal("MinionBeenSummoned", self.turn, subject, None, 0, "")
					
			elif len(subject) == 1:
				self.summonMinion(subject[0], position[0], initiatorID, comment="")
			#If the subject is a list of minions
			#(pos. "leftandRight") (pos, "totheRight"), (-1, "totheRightEnd")
			else:
				if type(position) == type(()): #If the position is not preprocessed yet.
					num_orig, pos = len(subject), position[0]
					if position[1] == "totheRightEnd":
						newPositions = [-1 for i in range(num_orig)]
					elif position[1] == "leftandRight": #当随从两侧产生随从时，在翻倍的情况下只用考虑召唤最多3个的情况。
						newPositions = [pos+1, pos, pos+3, pos, pos+5, pos][0:num_orig]
					else: #position[1] == "totheRight"
						newPositions = [pos+1 for i in range(num_orig)]
					position = newPositions
					
				while subject != []:
					sub = subject.pop(0)
					pos = position.pop(0) #Can summon at most 7 minions.
					if self.spaceonBoard(sub.ID) < 1: #No space for the minion to summon.
						break
					else: #If there is space to summon.
						sub.sequence = len(self.minions[1]) + len(self.minions[2]) + len(self.weapons[1]) + len(self.weapons[2])
						if pos < 0:
							self.minions[sub.ID].append(sub)
						else:
							self.minions[sub.ID].insert(pos, sub) #If position > num, the insert() method simply puts it at the end.
						self.rearrangePosition()
						sub.appears()
						self.sendSignal("MinionSummoned", self.turn, sub, None, 0, "")
						self.sendSignal("MinionBeenSummoned", self.turn, sub, None, 0, "")
						
	#一次只从一方的手牌中召唤随从
	def summonfromHand(self, subject, position, initiatorID, comment="SummoningCanbeDoubled"):
		if type(subject) != type([]) and type(subject) != type(np.array([])):
			if self.spaceonBoard(subject.ID) > 0:
				self.summonMinion(self.Hand_Deck.extractfromHand(subject)[0], position, initiatorID, comment)
		else: #summon multiple minions from hand
			for minion in fixedList(subject):
				if self.spaceonBoard(minion.ID) > 0:
					self.summonMinion(self.Hand_Deck.extractfromHand(minion)[0], position, initiatorID, comment)
				else:
					break
	#一次只从一方的牌库中召唤随从
	def summonfromDeck(self, subject, position, initiatorID, comment="SummoningCanbeDoubled"):
		if type(subject) != type([]) and type(subject) != type(np.array([])):
			if self.spaceonBoard(subject.ID) > 0:
				self.summonMinion(self.Hand_Deck.extractfromDeck(subject)[0], position, initiatorID, comment)
		else: #summon multiple minions from hand
			for minion in fixedList(subject):
				if self.spaceonBoard(minion.ID) > 0:
					self.summonMinion(self.Hand_Deck.extractfromDeck(minion)[0], position, initiatorID, comment)
				else:
					break
					
	def transform(self, target, newMinion):
		ID = target.ID
		if target in self.minions[target.ID]:
			pos = target.position
			target.disappears(keepDeathrattlesRegistered=False)
			self.removeMinionorWeapon(target)
			#removeMinionorWeapon invokes rearrangePosition() and rearrangeSequence()
			newMinion.position = pos
			newMinion.sequence = len(self.minions[1]) + len(self.minions[2]) + len(self.weapons[1]) + len(self.weapons[2])
			self.minions[ID].insert(pos, newMinion)
			self.rearrangePosition()
			print(target.name, " has been transformed into ", newMinion.name)
			newMinion.appears()
		elif target.inHand:
			print("Minion %s in hand is transformed into"%target.name, newMinion.name)
			self.Hand_Deck.replaceCardinHand(target, newMinion)
			
	def mutate(self, target, manaChange):
		cost = type(target).mana + manaChange
		step = -1 if manaChange >= 0 else 1 #如果最终费用过高，则向下取可选值；如果太低，向上取可选值
		while True:
			if cost not in self.MinionswithCertainCost.keys():
				cost += step
			else:
				break
		#After deciding the cost of the new minion, transform/replace it depending on it's location
		newMinion = np.random.choice(list(self.MinionswithCertainCost[cost].values()))
		self.transform(target, newMinion(self, target.ID))
		return newMinion
		
	#This method is always invoked after the minion.disappears() method.
	def removeMinionorWeapon(self, target):
		if target.cardType == "Minion" or target.cardType == "Permanent":
			target.onBoard = False
			extractfrom(target, self.minions[target.ID])
			self.rearrangeSequence()
			self.rearrangePosition()
		elif target.cardType == "Weapon":
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
			
	def returnMiniontoHand(self, target, keepDeathrattlesRegistered=False):
		if target in self.minions[target.ID]: #如果随从仍在随从列表中
			if self.Hand_Deck.handNotFull(target.ID):
				ID, identity = target.ID, target.identity
				#如果onBoard仍为True，则其仍计为场上存活的随从，需调用disappears以注销各种扳机。
				if target.onBoard: #随从存活状态下触发死亡扳机的区域移动效果时，不会注销其他扳机
					target.disappears(keepDeathrattlesRegistered)
				#如onBoard为False,则disappears已被调用过了。主要适用于触发死亡扳机中的区域移动效果
				self.removeMinionorWeapon(target)
				target.__init__(self, ID)
				print(target.name, "has been reset after returned to owner's hand. All enchantments lost.")
				target.identity[0], target.identity[1] = identity[0], identity[1]
				self.Hand_Deck.addCardtoHand(target, ID)
				return target
			else: #让还在场上的活着的随从返回一个满了的手牌只会让其死亡
				if target.onBoard:
					print(target.name, " dies because player's hand is full.")
					self.destroy(target)
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
			print(target.name, "has been reset after returned to deck %d. All enchantments lost"%ID)
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
			card, mana, isRightmostCardinHand = self.Hand_Deck.extractfromHand(target)
			#addCardtoHand method will force the ID of the card to change to the target hand ID.
			#If the other side has full hand, then the card is extracted and thrown away.
			self.Hand_Deck.addCardtoHand(card, 3-card.ID)
		elif target.onBoard: #If the minion is on board.
			if self.spaceonBoard(3-target.ID) < 1:
				print(target.name, " dies because there is no available spots for it.")
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
					if target.status["Temp Controlled"] < 1:
						target.status["Temp Controlled"] = 1
						#因为回合结束扳机的性质，只有第一个同类扳机会触发，因为后面的扳机检测时会因为ID已经不同于当前回合的ID而不能继续触发
						trigger = Trigger_ShadowMadness(target)
						trigger.connect()
						target.triggersonBoard.append(trigger)
				else: #Return or permanent
					target.status["Temp Controlled"] = 0
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
		
	#Handle minions Divine Shields, only return the damages taken/heals restored and kills/overkills.
	#The survivals recorded are for the minions that take damage.
	#Heal to damage resolution is finished before invoking this function.
	
	#This method will only be invoked after identifying onBoard targets.
	#调用AOE_preprocess() 和AOE()的dealsAOE()会在调用前将生效目标严格限定为调用时存在的目标上。
	def AOE_preprocess(self, subject, targets_Damage, damages, targets_Heal=[], heals=[]):
		targets_damaged = []
		damagesConnected = []
		for target, damage in zip(targets_Damage, damages):
			#Handle Immune, Shellfighter and Ramshield here.
			objtoTakeDamage = self.DamageHandler.damageTransfer(target)
			#Handle the Divine Shield and Commanding Shout here.
			targetSurvival = objtoTakeDamage.damageRequest(subject, damage)
			if targetSurvival > 0:
				targets_damaged.append(objtoTakeDamage)
				damagesConnected.append(damage)
				
		targets_Healed = []
		healsConnected = []
		for target, heal in zip(targets_Heal, heals):
			if target.health < target.health_upper: #Only record those damage characters.
				targets_Healed.append(target)
				healsConnected.append(heal)
		#targets are the minions that actually take damage. 
		return targets_damaged, damagesConnected, targets_Healed, healsConnected
		
	#The targets are objs that actually take damage. The heals are real.
	#HOWEVER, the real damage taken will be decided based Commanding Shout status resolution.
	def AOE(self, subject, targets_damaged, damagesConnected, targets_Healed=[], healsConnected=[]):
		damagesActual = []
		healsActual = []
		damageSurvivals = []
		totalDamageDone = 0
		totalHealingDone = 0
		for target, damage in zip(targets_damaged, damagesConnected):
			#The Commanding Shout resolution decides the real damage taken by minions.
			damageActual, survival = target.takesDamage(subject, damage, sendDamageSignal=False)
			totalDamageDone += damageActual
			damagesActual.append(damageActual)
			damageSurvivals.append(survival)
			
		for target, heal in zip(targets_Healed, healsConnected):
			healActual, survival = target.getsHealed(subject, heal, sendHealSignal=False)
			totalHealingDone += healActual
			healsActual.append(healActual)
		#统一发送群体中受伤害的信号，触发相应扳机。
		for target, damageActual in zip(targets_damaged, damagesActual):
			self.sendSignal(target.cardType+"TakesDamage", self.turn, subject, target, damageActual, "")
			self.sendSignal(target.cardType+"TookDamage", self.turn, subject, target, damageActual, "")
		#统一发送群体中受治疗的信号，触发相应扳机。
		for target_heal, healActual in zip(targets_Healed, healsActual):
			if target_heal.health >= target.health_upper:
				self.sendSignal(target.cardType+"GetsHealed", self.turn, subject, target, healActual, "FullyHealed")
			else:
				self.sendSignal(target.cardType+"GetsHealed", self.turn, subject, target, healActual, "StillDamaged")
				
		return targets_damaged, damagesActual, targets_Healed, healsActual, totalDamageDone, totalHealingDone, damageSurvivals
		
	#During the triggering, if another signal is send, the response to the new signal will be interpolated.
	#When the signal is sent to triggers, only the triggers that have been present from the beginning will respond. Those added after the signal being sent won't respond.
	#pydispatch.dispatcher doesn't meet this requirement.
	def sendSignal(self, signal, ID, subject, target, number, comment, choice=0):
		mainPlayerID = self.mainPlayerID #如果中途主副玩家发生变化，则结束此次信号的结算之后，下次再扳机触发顺序。
		#Trigger the triggers on main player's side, in the following order board-> hand -> deck.
		#先触发主玩家的各个位置的扳机。
		#print("Sending signal %s, ID %d"%(signal, ID), "subject", subject, "target", target, "number", number, "comment", comment)
		for triggerID in [mainPlayerID, 3-mainPlayerID]:
		#场上扳机先触发
			triggersinPlay = []
			#print("TriggersonBoard are ", self.triggersonBoard[triggerID])
			for trigger, sig in self.triggersonBoard[triggerID]:
				#只有满足扳机条件的扳机才会被触发。
				if sig == signal and trigger.canTrigger(signal, ID, subject, target, number, comment, choice):
					triggersinPlay.append(trigger)
			#某个随从死亡导致的队列中，作为场上扳机，救赎拥有最低优先级，其始终在最后结算
			if signal == "MinionDies" and self.SecretHandler.isSecretDeployedAlready(Redemption, 3-self.turn):
				for i in range(len(triggersinPlay)):
					if type(triggersinPlay[i]) == Trigger_Redemption:
						triggersinPlay.append(triggersinPlay.pop(i)) #把救赎的扳机移到最后
						break
			if triggersinPlay != [] and signal == "MinionBeenPlayed":
				print("The triggers for signal 'MinionBeenPlayed' is ", triggersinPlay)
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
	def gathertheDead(self, decideWinner=False, deadMinionsLinger=False):
		#Determine what characters are dead. The die() method hasn't been invoked yet.
		#序列内部不包含胜负裁定，即只有回合开始、结束产生的序列；
		#回合开始抽牌产生的序列；打出随从，法术，武器，英雄牌产生的序列；
		#以及战斗和使用英雄技能产生的序列以及包含的所有亡语等结算结束之后，胜负才会被结算。
		for ID in range(1, 3):
			#Register the weapons to destroy.(There might be multiple weapons in queue, 
			#since you can trigger Tirion Fordring's deathrattle twice and equip two weapons in a row.)
			#Pop all the weapons until no weapon or the latest weapon equipped.
			while self.weapons[ID] != []:
				if self.weapons[ID][0].durability < 1 or self.weapons[ID][0].tobeDestroyed:
					self.weapons[ID][0].destroyed() #武器的被摧毁函数，负责其onBoard, tobeDestroyed和英雄风怒，攻击力和场上扳机的移除等。
					weapon = self.weapons[ID].pop(0)
					self.tempDeathList[0].append(weapon)
					self.tempDeathList[1].append(weapon.attack)
				else: #If the weapon is the latest weapon to equip
					break
			for minion in fixedList(self.minionsonBoard(ID)):
				if minion.health < 1 or minion.dead:
					minion.dead = True
					attackwhenDies = minion.attack
					#随从被记为已死亡时需要将其onBoard置为False，从而之后不会重复计算随从的死亡
					minion.disappears(keepDeathrattlesRegistered=True) #随从死亡时不会注销其死亡扳机，这些扳机会在触发之后自行注销
					self.CounterHandler.minionsDiedThisTurn[minion.ID].append(minion.index)
					self.CounterHandler.minionsDiedThisGame[minion.ID].append(minion.index)
					if "Mech" in minion.race:
						#List: [ [mechIndex, [magnetic upgrades]] ]
						self.CounterHandler.mechsDiedThisGame[minion.ID].append([minion.index, minion.history["Magnetic Upgrades"]])
					self.tempDeathList[0].append(minion)
					self.tempDeathList[1].append(minion.attack)
					
		if self.tempDeathList != [[], []]:
			#Rearrange the dead minions according to their sequences.
			self.tempDeathList[0], order = self.sort_Sequence(self.tempDeathList[0])
			temp = self.tempDeathList[1]
			self.tempDeathList[1] = []
			for i in range(len(order)):
				self.tempDeathList[1].append(temp[order[i]])
			print("The new dead minions/weapons to resolve death/destruction are ", self.tempDeathList[0])
			#If there is no current deathrattles queued, start the deathrattle calc process.
			if self.deathList == [[], []]:
				self.deathList = self.tempDeathList
			else:
				#If there is deathrattle in queue, simply add new deathrattles to the existing list.
				self.deathList[0] += self.tempDeathList[0]
				self.deathList[1] += self.tempDeathList[1]
				
			#The content stored in self.tempDeathList must be released.
			#Clean the temp list to wait for new input.
			self.tempDeathList = [[], []]
		#If the game is currently not in the death-resolving mode, the mode will start.
		#不管是否有新的随从、武器要摧毁都执行此方法。
		if self.resolvingDeath == False:
			self.deathHandle(decideWinner, deadMinionsLinger)
			
	#大法师施放的闷棍会打断被闷棍的随从的回合结束结算。可以视为提前离场。
	#死亡缠绕实际上只是对一个随从打1，然后如果随从的生命值在1以下，则会触发抽牌。它不涉及强制死亡导致的随从提前离场
	#当一个拥有多个亡语的随从死亡时，多个亡语触发完成之后才会开始结算其他随从死亡的结算。
	def deathHandle(self, decideWinner=False, deadMinionsLinger=False): 
		while self.deathList != [[], []]:
			self.resolvingDeath = True
			print("The dead/destroyed characters to handle are: ", self.deathList)
			#For now, assume Tirion Fordring's deathrattle equipping Ashbringer won't trigger player's weapon's deathrattles right away.
			#weapons with regard to deathrattle triggering is handled the same way as minions.
			print("Now handling the death/destruction of", self.deathList[0][0].name)
			#一个亡语随从另附一个亡语时，两个亡语会连续触发，之后才会去结算其他随从的亡语。
			#当死灵机械师与其他 亡语随从一同死亡的时候， 不会让那些亡语触发两次，即死灵机械师、瑞文戴尔需要活着才能有光环
			#场上有憎恶时，憎恶如果死亡，触发的第一次AOE杀死死灵机械师，则第二次亡语照常触发。所以亡语会在第一次触发开始时判定是否会多次触发
			self.deathList[0][0].deathResolution(self.deathList[1][0])	
			#不允许死亡随从逗留，或者死亡的实体不是随从（而是武器），则将这个随从移除出随从列表
			if deadMinionsLinger == False or self.deathList[0][0].cardType != "Minion":
				self.removeMinionorWeapon(self.deathList[0][0])
			self.deathList[0].pop(0)
			self.deathList[1].pop(0)
			self.gathertheDead(decideWinner, deadMinionsLinger) #See if the deathrattle results in more death or destruction.
			
		self.resolvingDeath = False
		#The reborn effect take place after the deathrattles of minions have been triggered.
		if decideWinner:
			hero1Dead, hero2Dead = False, False
			if self.heroes[1].dead or self.heroes[1].health <= 0:
				print("----------------Player 1 dies----------------")
				hero1Dead = True
			if self.heroes[2].dead or self.heroes[2].health <= 0:
				print("----------------Player 2 dies----------------")
				hero2Dead = True
			if hero1Dead:
				if hero2Dead:
					self.endGame("NoWinner")
				else:
					self.endGame("Player2Wins")
			else:
				if hero2Dead:
					self.endGame("Player1Wins")
					
	"""
	At the start of turn, the AOE destroy/AOE damage/damage effect won't kill minions make them leave the board.
	As long as the minion is still on board, it can still trigger its turn start/end effects.
	Special things are Sap/Defile, which will force the minion to leave board early.
	#The Defile will cause the game to preemptively start death resolution.
	Archmage casting spell will be able to target minions with health <= 0, since they are not regarded as dead yet.
	The deaths of minions will be handled at the end of triggering, which is then followed by drawing card.
	"""	
	def switchTurn(self):
		print("----------------------------------------\nThe turn ends for hero %d\n----------------------------------------"%self.turn)
		self.ManaHandler.turnEnds()
		for minion in self.minions[self.turn] + self.minions[3-self.turn]: #Include the Permanents.
			minion.turnEnds(self.turn) #Handle minions' attTimes and attChances
		for card in self.Hand_Deck.hands[self.turn]	+ self.Hand_Deck.hands[3-self.turn]:
			if card.cardType == "Minion": #Minions in hands will clear their temp buffDebuff
				card.turnEnds(self.turn) #Minions in hands can't defrost
				
		self.heroes[self.turn].turnEnds(self.turn)
		self.heroes[3-self.turn].turnEnds(self.turn)
		self.heroPowers[self.turn].turnEnds(self.turn)
		self.heroPowers[3-self.turn].turnEnds(self.turn)
		self.sendSignal("TurnEnds", self.turn, None, None, 0, "")
		self.gathertheDead(True)
		#The secrets and temp effects are cleared at the end of turn.
		for obj in self.turnEndTrigger:
			if obj.ID == self.turn:
				obj.trigger()
				
		self.CounterHandler.turnEnds()
		
		self.turn = 3 - self.turn #Changes the turn to another hero.
		print("----------------------------------------\nA new turn starts for hero %d\n----------------------------------------"%self.turn)
		for obj in self.turnStartTrigger: #This is for temp effects.
			if obj.ID == self.turn:
				obj.trigger()
		self.ManaHandler.turnStarts()
		self.heroes[self.turn].turnStarts(self.turn)
		self.heroes[3-self.turn].turnStarts(self.turn)
		self.heroPowers[self.turn].turnStarts(self.turn)
		self.heroPowers[3-self.turn].turnStarts(self.turn)
		for minion in self.minions[self.turn] + self.minions[3-self.turn]: #Include the Permanents.
			minion.turnStarts(self.turn) #Handle minions' attTimes and attChances
		for card in self.Hand_Deck.hands[self.turn]	+ self.Hand_Deck.hands[3-self.turn]:
			if card.cardType == "Minion":
				card.turnStarts(self.turn)
				
		self.sendSignal("TurnStarts", self.turn, None, None, 0, "")
		self.gathertheDead(True)
		#抽牌阶段之后的死亡处理可以涉及胜负裁定。
		self.Hand_Deck.drawCard(self.turn)
		self.gathertheDead(True) #There might be death induced by drawing cards.
		
	def battleRequest(self, subject, target, verifySelectable=True, consumeAttackChance=True):
		if verifySelectable and subject.canAttackTarget(target) == False:
			print("Battle not allowed between attacker %s and target%s"%(subject.name, target.name))
		else:
			print("			**********\nHandling battle request between %s and %s\n				***********"%(subject.name, target.name))
		#战斗阶段：
			#攻击前步骤： 触发攻击前扳机，列队结算，如爆炸陷阱，冰冻陷阱，误导
				#如果扳机结算完毕后，被攻击者发生了变化，则再次进行攻击前步骤的扳机触发。重复此步骤直到被攻击者没有变化为止。
				#在这些额外的攻击前步骤中，之前已经触发过的攻击前扳机不能再能触发。
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
			
			
			#如果英雄的武器为蜡烛弓和角斗士的长弓，则优先给予攻击英雄免疫，防止一切攻击前步骤带来的伤害。
			self.sendSignal("BattleStarted", self.turn, subject, target, 0, "")
			#在此，奥秘和健忘扳机会在此触发。需要记住初始的目标，然后可能会有诸多扳机可以对此初始信号响应。
			signal = subject.cardType + "Attacks" + target.cardType
			print("Battle initiated between attacker %s and target%s"%(subject.name, target.name))
			self.target = target
			self.sendSignal(signal, self.turn, subject, target, 0, "1stPre-attack")
			#第一轮攻击前步骤结束之后，Game的记录的target如果相对于初始目标发生了变化，则再来一轮攻击前步骤，直到目标不再改变为止。
			#例如，对手有游荡怪物、误导和毒蛇陷阱，则攻击英雄这个信号可以按扳机入场顺序触发误导和游荡怪物，改变了攻击目标。之后的额外攻击前步骤中毒蛇陷阱才会触发。
			#如果对手有崇高牺牲和自动防御矩阵，那么攻击随从这个信号会将两者都触发，此时攻击目标不会因为这两个奥秘改变。
			#健忘这个特性，如果满足触发条件，且错过了50%几率，之后再次满足条件时也不会再触发这个扳机。这个需要在每个食人魔随从上专门放上标记。
				#如果场上有多个食人魔勇士，则这些扳机都只会在每一次信号发出时触发。
			#如果一个攻击前步骤中，目标连续发生变化，如前面提到的游荡怪物和误导，则只会对最新的目标进行下一次攻击前步骤。
			#如果一个攻击前步骤中，目标连续发生变化，但最终又变回与初始目标相同，则不会产生新的攻击前步骤。
			
			#在之前的攻击前步骤中触发过的扳机不能再后续的额外攻击前步骤中再次触发，主要作用于傻子和市长，因为其他的攻击前扳机都是奥秘，触发之后即消失。
			while self.target != target:
				target = self.target #攻击前步骤改变了攻击目标，则再次进行攻击前步骤，与这个新的目标进行比对。
				signal = subject.cardType+"Attacks"+target.cardType #产生新的触发信号。
				self.sendSignal(signal, self.turn, subject, target, 0, "FollowingPre-attack")
				
			#攻击前步骤结束，开始结算攻击时步骤
			#攻击时步骤：触发“当xx攻击时”的扳机，如真银圣剑，血吼，智慧祝福，血吼，收集者沙库尔等
			signal = subject.cardType+"Attacking"+self.target.cardType
			self.sendSignal(signal, self.turn, subject, self.target, 0, "")
			#如果此时攻击者，攻击目标或者任意英雄濒死或离场所，则攻击取消，跳过伤害和攻击后步骤。
			battleContinues = True
			if subject.onBoard == False or subject.health < 1 or subject.dead:
				print("The attacker is not onBoard/alive anymore. Battle interrupted")
				battleContinues = False
			elif self.target.onBoard == False or self.target.health < 1 or self.target.dead:
				print("The target is not onBoard/alive anymore. Battle interrupted. The attacker's attack chance is still wasted.")
				battleContinues = False
				if consumeAttackChance: #If this attack is canceled, the attack time still increases.
					subject.attTimes += 1
			elif self.heroes[1].health < 1 or self.heroes[1].dead or self.heroes[2].health < 1 or self.heroes[2].dead:
				print("At least one of the players is dying, battle interrupted. But the attacker still wastes an attack chance.")
				battleContinues = False
				if consumeAttackChance: #If this attack is canceled, the attack time still increases.
					subject.attTimes += 1
			if battleContinues:
				#伤害步骤，攻击者移除潜行，攻击者对被攻击者造成伤害，被攻击者对攻击者造成伤害。然后结算两者的伤害事件。
				#攻击者和被攻击的血量都减少。但是此时尚不发出伤害判定。先发出攻击完成的信号，可以触发扫荡打击。
				subject.attacks(self.target, consumeAttackChance)
				#巨型沙虫的获得额外攻击机会的触发在随从死亡之前结算。同理达利乌斯克罗雷的触发也在死亡结算前，但是有隐藏的条件：自己不能处于濒死状态。
				self.sendSignal(subject.cardType+"Attacked"+target.cardType, self.turn, subject, target, 0, "")
			#重置蜡烛弓，角斗士的长弓，以及傻子和市长的triggeredDuringBattle标识。
			print("Sending signal 'BattleFinished'")
			self.sendSignal("BattleFinished", self.turn, subject, None, 0, "")
			#战斗阶段结束，处理亡语，此时可以处理胜负问题。
			self.gathertheDead(True)
			
	#comment = "InvokedbyAI", "Branching-i", ""(GUI by default) 
	def playSpell(self, spell, target, choice=0, comment=""):
		#np.random.seed(self.seed) #调用之前需要重置随机数生成器的种子
		canPlaySpell = False
		#古加尔的费用光环需要玩家的血量加护甲大于法术的当前费用或者免疫状态下才能使用
		if self.ManaHandler.costAffordable(spell) == False:
			print("Not enough mana/health to play the spell", spell, ", which costs %d"%spell.mana)
		else:
			if spell.available() and spell.selectionLegit(target, choice): #Non targeting spells.
				canPlaySpell = True
			else:
				print("Invalid selection to play spell %s, with choice "%spell.name, choice)
				
		if canPlaySpell:
			print("	   *********\nHandling play spell %s with target "%spell.name, target, ", with choice: ", choice, "\n	   *********")
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
			
			#支付法力值，结算血色绽放等状态。
			spell, mana, isRightmostCardinHand = self.Hand_Deck.extractfromHand(spell)
			self.ManaHandler.payManaCost(spell, mana)
			#请求使用法术，如果此时对方场上有法术反制，则取消后续序列。
			if self.SecretHandler.isSecretDeployedAlready(Counterspell, 3-self.turn):
				print("Player's spell %s played is Countered by Counterspell"%spell.name)
				self.sendSignal("TriggerCounterspell", spell.ID, spell, target, 0, "")
			else:
				spell.played(target, choice, mana, comment) #choice用于抉择选项，comment用于区分是GUI环境下使用还是AI分叉
				self.CounterHandler.numSpellsPlayedThisTurn[self.turn] += 1
				self.CounterHandler.cardsPlayedThisTurn[self.turn].append(spell.index)
				self.CounterHandler.cardsPlayedThisGame[self.turn].append(spell.index)
				#使用后步骤，触发“每当使用一张xx牌之后”的扳机，如狂野炎术士，西风灯神，星界密使的状态移除和伊莱克特拉风潮的状态移除。
				if isRightmostCardinHand:
					self.sendSignal("SpellBeenPlayed", self.turn, spell, self.target, mana, "CardPlayedistheRightmostinHand", choice)
				else:
					self.sendSignal("SpellBeenPlayed", self.turn, spell, self.target, mana, "", choice)
				#完成阶段结束，处理亡语，此时可以处理胜负问题。
				self.gathertheDead(True)
				
	def availableWeapon(self, ID):
		for weapon in self.weapons[ID]:
			if weapon.durability > 0 and weapon.onBoard:
				return weapon
		return None
		
	"""Weapon with target will be handle later"""
	def playWeapon(self, weapon, target):
		ID = weapon.ID
		if self.ManaHandler.costAffordable(weapon) == False:
			print("Not enough mana to play the weapon", weapon)
		else:
			print("	   *********")
			print("Handling play weapon %s with target "%weapon.name, target)
			print("	   *********")
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
			weapon, mana, isRightmostCardinHand = self.Hand_Deck.extractfromHand(weapon)
			weaponIndex = weapon.index
			self.ManaHandler.payManaCost(weapon, mana)
			#使用阶段，结算阶段。
			weapon.played(target) #There are no weapon with Choose One.
			self.CounterHandler.cardsPlayedThisTurn[self.turn].append(weaponIndex)
			self.CounterHandler.cardsPlayedThisGame[self.turn].append(weaponIndex)
			#完成阶段，触发“每当你使用一张xx牌”的扳机，如捕鼠陷阱和瑟拉金之种等。
			if isRightmostCardinHand:
				self.sendSignal("WeaponBeenPlayed", self.turn, weapon, self.target, mana, "CardPlayedistheRightmostinHand")
			else:
				self.sendSignal("WeaponBeenPlayed", self.turn, weapon, self.target, mana, "")
			#完成阶段结束，处理亡语，可以处理胜负问题。	
			self.gathertheDead(True)
			
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
		if self.ManaHandler.costAffordable(heroCard) == False:
			print("Not enough mana to play the hero card ", heroCard)
		else:
			print("	   *********\nHandling play hero card %s\n	   *********"%heroCard.name)
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
				
			#支付费用，以及费用状态移除
			heroCard, mana, isRightmostCardinHand = self.Hand_Deck.extractfromHand(heroCard)
			heroCardIndex = heroCard.index
			self.ManaHandler.payManaCost(heroCard, mana)
			#使用阶段，结算阶段的处理。
			heroCard.played(choice)
			self.CounterHandler.cardsPlayedThisTurn[self.turn].append(heroCardIndex)
			self.CounterHandler.cardsPlayedThisGame[self.turn].append(heroCardIndex)
		#完成阶段
			#使用后步骤，触发“每当你使用一张xx牌之后”的扳机，如捕鼠陷阱等。
			if isRightmostCardinHand:
				self.sendSignal("HeroCardBeenPlayed", self.turn, self, None, mana, "CardPlayedistheRightmostinHand", choice)
			else:
				self.sendSignal("HeroCardBeenPlayed", self.turn, self, None, mana, "", choice)
			#完成阶段结束，处理亡语，可以处理胜负问题。
			self.gathertheDead(True)