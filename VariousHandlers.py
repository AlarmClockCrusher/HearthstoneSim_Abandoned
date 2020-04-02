import numpy as np
import tkinter as tk

def extractfrom(target, listObject):
	temp = None
	for i in range(len(listObject)):
		if listObject[i] == target:
			temp = listObject.pop(i)
			break
	return temp
	
def fixedList(listObject):
	return listObject[0:len(listObject)]
	
def PRINT(obj, string, *args):
	if hasattr(obj, "GUI"):
		GUI = obj.GUI
	elif hasattr(obj, "Game"):
		GUI = obj.Game.GUI
	elif hasattr(obj, "entity"):
		GUI = obj.entity.Game.GUI
	else:
		GUI = None
	if GUI != None:
		GUI.printInfo(string)
	else:
		print(string)
		
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
class ManaHandler:
	def __init__(self, Game):
		self.Game = Game
		self.manas = {1:1, 2:0}
		self.manasUpper = {1:1, 2:0}
		self.manasLocked = {1:0, 2:0}
		self.manasOverloaded = {1:0, 2:0}
		self.manas_UpperLimit = {1:10, 2:10}
		self.manas_withheld = {1:0, 2:0}
		#CardAuras不再是放置所有费用修改效果的列表，而改为存放不直接寄存于随从上的费用光环。
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
		self.Game.sendSignal("OverloadStatusCheck", ID, None, None, 0, "")
		
	def unlockOverloadedMana(self, ID):
		self.manas[ID] += self.manasLocked[ID]
		self.manas[ID] = min(self.manas_UpperLimit[ID], self.manas[ID])
		self.manasLocked[ID] = 0
		self.manasOverloaded[ID] = 0
		self.Game.sendSignal("OverloadStatusCheck", ID, None, None, 0, "")
		
	def setManaCrystal(self, num, ID):
		self.manasUpper[ID] = num
		if self.manas[ID] > num:
			self.manas[ID] = num
		self.Game.sendSignal("EmptyManaCrystalCheck", ID, None, None, 0, "")
		
	def gainManaCrystal(self, num, ID):
		self.manas[ID] += num
		self.manas[ID] = min(self.manas_UpperLimit[ID], self.manas[ID])
		self.manasUpper[ID] += num
		self.manasUpper[ID] = min(self.manas_UpperLimit[ID], self.manasUpper[ID])
		self.Game.sendSignal("EmptyManaCrystalCheck", ID, None, None, 0, "")
		
	def gainEmptyManaCrystal(self, num, ID):
		if self.manasUpper[ID] + num <= self.manas_UpperLimit[ID]:
			self.manasUpper[ID] += num
			self.Game.sendSignal("EmptyManaCrystalCheck", ID, None, None, 0, "")
			return True
		else: #只要获得的空水晶量高于目前缺少的空水晶量，即返回False
			self.manasUpper[ID] = self.manas_UpperLimit[ID]
			self.Game.sendSignal("EmptyManaCrystalCheck", ID, None, None, 0, "")
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
		self.Game.sendSignal("EmptyManaCrystalCheck", ID, None, None, 0, "")
		
	def costAffordable(self, subject):
		ID = subject.ID
		if subject.cardType == "Spell": #目前只考虑法术的法力消耗改生命消耗光环
			if self.status[ID]["Spells Cost Health Instead"] > 0:
				if subject.mana < self.Game.heroes[ID].health + self.Game.heroes[ID].armor or self.Game.playerStatus[ID]["Immune"] > 0:
					return True
			else:
				if subject.mana <= self.manas[ID]:
					return True
		else:
			if subject.mana <= self.manas[ID]:
				return True
				
		return False
		
	def payManaCost(self, subject, mana):
		ID = subject.ID
		mana = max(0, mana)
		if subject.cardType == "Spell":
			if self.status[ID]["Spells Cost Health Instead"] > 0:
				objtoTakeDamage = self.Game.DamageHandler.damageTransfer(self.Game.heroes[ID])
				objtoTakeDamage.takesDamage(None, mana)
			else:
				self.manas[ID] -= mana
		else:
			self.manas[ID] -= mana
		self.Game.sendSignal("ManaCostPaid", ID, subject, None, mana, "")
		if subject.cardType == "Minion":
			self.Game.CounterHandler.manaSpentonPlayingMinions[ID] += mana
		elif subject.cardType == "Spell":
			self.Game.CounterHandler.manaSpentonSpells[ID] += mana
			
	#At the start of turn, player's locked mana crystals are removed.
	#Overloaded manas will becomes the newly locked mana.
	def turnStarts(self):
		ID = self.Game.turn
		self.gainEmptyManaCrystal(1, ID)
		self.manasLocked[ID] = self.manasOverloaded[ID]
		self.manasOverloaded[ID] = 0
		self.manas[ID] = max(0, self.manasUpper[ID] - self.manasLocked[ID] - self.manas_withheld[ID])
		self.Game.sendSignal("OverloadStatusCheck", ID, None, None, 0, "")
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
				PRINT(self, "{} expires at the end of turn.".format(aura))
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
		for manaMod in card.manaModifications:
			manaMod.handleMana()
		#随从的改变自己法力值的效果在此结算。如果卡牌有回响，则其法力值不能减少至0
		card.selfManaChange()
		if card.mana < 0: #费用修改不能把卡的费用降为0
			card.mana = 0
		if card.cardType == "Minion" and card.mana < 1 and card.keyWords["Echo"] > 0:
			card.mana = 1
		elif card.cardType == "Spell" and card.mana < 1 and "Echo" in card.index:
			card.mana = 1
			
	def calcMana_Powers(self):
		for ID in range(1, 3):
			self.Game.heroPowers[ID].mana = type(self.Game.heroPowers[ID]).mana
			for manaMod in self.Game.heroPowers[ID].manaModifications:
				manaMod.handleMana()
			if self.Game.heroPowers[ID].mana < 0:
				self.Game.heroPowers[ID].mana = 0
				
				
class ManaModification:
	def __init__(self, card, changeby=0, changeto=-1, source=None, lowerbound=0):
		self.card = card
		self.changeby, self.changeto, self.lowerbound = changeby, changeto, lowerbound
		self.source = source
		
	def handleMana(self):
		if self.changeby != 0:
			self.card.mana += self.changeby
			if self.card.mana < self.lowerbound: #用于召唤传送门的随从减费不小于1的限制。
				self.card.mana = self.lowerbound
		elif self.changeto >= 0:
			self.card.mana = self.changeto
			
	def applies(self):
		self.card.manaModifications.append(self) #需要让卡牌自己也带有一个检测的光环，离开手牌或者牌库中需要清除。
		if self.card in self.card.Game.Hand_Deck.hands[self.card.ID] or self.card in self.card.Game.Hand_Deck.decks[self.card.ID]:
			self.card.Game.ManaHandler.calcMana_Single(self.card)
			
	def getsRemoved(self):
		extractfrom(self, self.card.manaModifications)
		if self.source != None:
			extractfrom((self.card, self), self.source.auraAffected)
			
	def selfCopy(self, recipientCard):
		return ManaModification(recipientCard, self.changeby, self.changeto, self.source)
		
#既可以用于随从发出的费用光环，也可用于不寄存在随从实体上的暂时费用光环，如伺机待发等。
#随从发出的光环由随从自己控制光环的开关。
#不寄存于随从身上的光环一般用于一次性的费用结算。而洛欧塞布等持续一个回合的光环没有任何扳机而已
class ManaAura_Dealer:
	def __init__(self, minion, func, changeby=0, changeto=-1, lowerbound=0):
		self.blank_init(minion, func, changeby, changeto, lowerbound)
		
	def blank_init(self, minion, func, changeby, changeto, lowerbound):
		self.minion = minion
		if func != None:
			self.manaAuraApplicable = func
		self.changeby, self.changeto, self.lowerbound = changeby, changeto, lowerbound
		self.auraAffected = [] #A list of (minion, aura_Receiver)
		
	def manaAuraApplicable(self, target):
		return True
		
	#只要是有满足条件的卡牌进入手牌，就会触发这个光环。target是承载这个牌的列表。
	#applicable不需要询问一张牌是否在手牌中。光环只会处理在手牌中的卡牌
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.minion.onBoard and self.manaAuraApplicable(target[0])
		
	def trigger(self, signal, ID, subject, target, number, comment, choice=0):
		if self.canTrigger(signal, ID, subject, target, number, comment):
			self.effect(signal, ID, subject, target, number, comment)
			
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.applies(target[0])
		
	def applies(self, target): #This target is NOT holder.
		if self.manaAuraApplicable(target):
			PRINT(self.minion, "Card %s gains the Changeby %d/Changeto %d mana change from %s"%(target.name, self.changeby, self.changeto, self.minion.name))
			manaMod = ManaModification(target, self.changeby, self.changeto, self, self.lowerbound)
			manaMod.applies()
			self.auraAffected.append((target, manaMod))
			
	def auraAppears(self):
		PRINT(self.minion, "{} appears and starts its mana aura {}".format(self.minion.name, self))
		for card in self.minion.Game.Hand_Deck.hands[1] + self.minion.Game.Hand_Deck.hands[2]:
			self.applies(card)
			
		#Only need to handle minions that appear. Them leaving/silenced will be handled by the BuffAura_Receiver object.
		#We want this Trigger_MinionAppears can handle everything including registration and buff and removing.
		self.minion.Game.triggersonBoard[self.minion.ID].append((self, "CardEntersHand"))
		self.minion.Game.ManaHandler.calcMana_All()
		
	#When the aura object is no longer referenced, it vanishes automatically.
	def auraDisappears(self):
		PRINT(self.minion, "%s removes its effect."%self.minion.name)
		for minion, manaMod in fixedList(self.auraAffected):
			manaMod.getsRemoved()
			
		self.auraAffected = []
		extractfrom((self, "CardEntersHand"), self.minion.Game.triggersonBoard[self.minion.ID])
		self.minion.Game.ManaHandler.calcMana_All()
		
	def selfCopy(self, recipient): #The recipient is the entity that deals the Aura.
		#func that checks if subject is manaAuraApplicable will be the new copy's function
		return type(self)(recipient, recipient.manaAuraApplicable, self.changeby, self.changeto)
		
		
class TempManaEffect:
	def __init__(self, Game, ID, changeby=0, changeto=-1):
		self.Game, self.ID = Game, ID
		self.changeby, self.changeto = changeby, changeto
		self.temporary = True
		self.auraAffected = []
		
	def applicable(self, target):
		return True
	#signal有"CardEntersHand"和"ManaCostPaid",只要它们满足applicable就可以触发。
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		if signal == "CardEntersHand":
			return self.applicable(target[0])
		return subject.ID == self.ID and self.applicable(subject)
		
	def trigger(self, signal, ID, subject, target, number, comment, choice=0):
		if self.canTrigger(signal, ID, subject, target, number, comment):
			self.effect(signal, ID, subject, target, number, comment)
			
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		if signal == "CardEntersHand":
			self.applies(target[0])
		else: #signal == "ManaCostPaid"
			self.auraDisappears()
			
	def applies(self, subject):
		if self.applicable(subject):
			PRINT(self, "Card {} gains the Changeby {}/Changeto {} mana change from {}"%(subject.name, self.changeby, self.changeto, self.Game))
			manaMod = ManaModification(subject, self.changeby, self.changeto, self)
			manaMod.applies()
			self.auraAffected.append((subject, manaMod))
			
	def auraAppears(self):
		for card in self.Game.Hand_Deck.hands[1] + self.Game.Hand_Deck.hands[2]:
			self.applies(card)
		self.Game.triggersonBoard[self.ID].append((self, "CardEntersHand"))
		self.Game.triggersonBoard[self.ID].append((self, "ManaCostPaid"))
		self.Game.ManaHandler.calcMana_All()
		
	def auraDisappears(self):
		for minion, manaMod in fixedList(self.auraAffected):
			manaMod.getsRemoved()
		self.auraAffected = []
		extractfrom(self, self.Game.ManaHandler.CardAuras)
		extractfrom((self, "CardEntersHand"), self.Game.triggersonBoard[self.ID])
		extractfrom((self, "ManaCostPaid"), self.Game.triggersonBoard[self.ID])
		self.Game.ManaHandler.calcMana_All()
		
	def selfCopy(self, recipientGame): #The recipient is the Game that handles the Aura.
		return type(self)(recipientGame, self.ID, self.changeby, self.changeto)
		
		
class TempManaEffect_Power:
	def __init__(self, Game, ID, changeby=0, changeto=-1):
		self.Game, self.ID = Game, ID
		self.changeby, self.changeto = changeby, changeto
		self.temporary = True
		self.auraAffected = []
		
	def applicable(self, target):
		return True
	#signal有"CardEntersHand"和"ManaCostPaid",只要它们满足applicable就可以触发。
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.applicable(subject) #Hero Power的出现是不传递holder而是直接传递subject
		
	def trigger(self, signal, ID, subject, target, number, comment, choice=0):
		if self.canTrigger(signal, ID, subject, target, number, comment):
			self.effect(signal, ID, subject, target, number, comment)
			
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		if signal == "HeroPowerAcquired":
			self.applies(subject)
		else: #signal == "ManaCostPaid"
			self.auraDisappears()
			
	def applies(self, subject):
		if self.applicable(subject):
			PRINT(self, "Hero Power {} gains the Changeby {}/Changeto {} mana change from {}"%(subject.name, self.changeby, self.changeto, self))
			manaMod = ManaModification(subject, self.changeby, self.changeto, self)
			manaMod.applies()
			self.auraAffected.append((subject, manaMod))
			
	def auraAppears(self):
		self.applies(self.Game.heroPowers[1])
		self.applies(self.Game.heroPowers[2])
		self.Game.triggersonBoard[self.ID].append((self, "HeroPowerAcquired"))
		self.Game.triggersonBoard[self.ID].append((self, "ManaCostPaid"))
		self.Game.ManaHandler.calcMana_Powers()
		
	def auraDisappears(self):
		for minion, manaMod in fixedList(self.auraAffected):
			manaMod.getsRemoved()
		self.auraAffected = []
		extractfrom(self, self.Game.ManaHandler.PowerAuras)
		extractfrom((self, "HeroPowerAcquired"), self.Game.triggersonBoard[self.ID])
		extractfrom((self, "ManaCostPaid"), self.Game.triggersonBoard[self.ID])
		self.Game.ManaHandler.calcMana_Powers()
		
	def selfCopy(self, recipientGame): #The recipient is the Game.
		return type(self)(recipientGame, self.ID, self.changeby, self.changeto)
		
		
		
class SecretHandler:
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
		secretsAvailable = []
		for card in self.Game.Hand_Deck.decks[ID]:
			if "~~Secret" in card.index and self.isSecretDeployedAlready(card, ID) == False:
				secretsAvailable.append(card)
				
		if secretsAvailable != []:
			num = min(len(secretsAvailable), num)
			secrets = np.random.choice(secretsAvailable, num, replace=False)
			for secret in secrets:
				self.Game.Hand_Deck.extractfromDeck(secret)
				secret.whenEffective()
				
	def extractSecrets(self, ID, all=False):
		if all:
			numSecrets = len(self.secrets[ID])
			while self.secrets[ID] != []:
				self.secrets[ID][0].active = False
				self.secrets[ID].pop(0)
				
			return numSecrets
		else:
			if self.secrets[ID] != []:
				secret = self.secrets[ID].pop(np.random.randint(len(self.secrets[ID])))
				secret.active = False
				return secret
			else:
				return None
				
	#secret can be type, index or real card.
	def isSecretDeployedAlready(self, secret, ID):
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
			
			
class DamageHandler:
	def __init__(self, Game):
		self.Game = Game
		self.ShellfighterExists = {1: 0, 2: 0}
		self.RamshieldExists = {1: 0, 2: 0}
		
	def isActiveShellfighter(self, target):
		return target.name == "Snapjaw Shellfighter" and target.silenced == False
		
	def isActiveBolfRamshield(self, target):
		return target.name == "Bolf Ramshield" and target.silenced == False
		
	#Will return the leftmost Shellfighter in the chain or the minion itself.
	def leftmostShellfighter(self, minion):
		pos = minion.position
		Shellfighter_Left = minion
		while pos > 0: #Pos must be compared to the leftmost pos possible.
			minion_Left = self.Game.minionsonBoard(minion.ID)[pos-1]
			if self.isActiveShellfighter(minion_Left):
				Shellfighter_Left = minion_left
				pos -= 1
			else: #If the minion on the left is not Shellfighter, the previous Shellfighters has been stored in the Shellfighter_Left variable.
				break
				
		return Shellfighter_Left
		
	#Will return the rightmost Shellfighter in the chain or the minion itself.
	def rightmostShellfighter(self, minion):
		pos = minion.position
		Shellfighter_Right = minion
		rightEndPos = len(self.Game.minionsonBoard(minion.ID)) - 1
		while pos < rightEndPos:
			minion_Right = self.Game.minionsonBoard(minion.ID)[pos+1]
			if self.isActiveShellfighter(minion_Right):
				Shellfighter_Right = minion_Right
				pos += 1
			else: #If the minion on the left is not Shellfighter, the previous Shellfighters has been stored in the Shellfighter_Left variable.
				break
				
		return Shellfighter_Right
		
	#Return the correct minion to take damage.
	#已经测试过Immune的随从在受伤时不会转移给钳嘴龟盾卫
	#已经测试过圣盾随从在受伤时会转移转移给钳嘴龟盾卫，圣盾似乎只阻挡最后的伤害判定，不负责伤害目标转移
	def damageTransfer_InitiallyonMinion(self, minion):
		if minion.cardType == "Permanent":
			return minion
		#This method will never be invoked if the minion is dead already or in deck.
		else: #minion.cardType == "Minion"
			if minion.inHand:
				return minion
			elif minion.onBoard:
				if self.ShellfighterExists[minion.ID] <= 0 or minion.status["Immune"] > 0:
					return minion #Immune minions won't need to transfer damage
				else:
					adjacentMinions, distribution = self.Game.findAdjacentMinions(minion)
					if distribution == "Minions on Both Sides":
						ShellfighterontheLeft = self.isActiveShellfighter(adjacentMinions[0])
						ShellfighterontheRight = self.isActiveShellfighter(adjacentMinions[1])
						#If both sides are active Shellfighters, the early one on board will trigger.
						if ShellfighterontheLeft and ShellfighterontheRight:
							if adjacentMinions[0].sequence < adjacentMinions[1].sequence:
								miniontoTakeDamage = self.leftmostShellfighter(minion)
							else:
								miniontoTakeDamage = self.rightmostShellfighter(minion)
						#If there is only a Shellfighter on the left, find the leftmost Shellfighter
						elif ShellfighterontheLeft:
							miniontoTakeDamage = self.leftmostShellfighter(minion)
						#If there is only a Shellfighter on the right, find the rightmost Shellfighter
						else:
							miniontoTakeDamage = self.rightmostShellfighter(minion)
							
					elif distribution == "Minions Only on the Left":
						miniontoTakeDamage = self.leftmostShellfighter(minion)
					elif distribution == "Minions Only on the Right":
						miniontoTakeDamage = self.rightmostShellfighter(minion)
					elif distribution == "No Adjacent Minions":
						miniontoTakeDamage = minion
						
					return miniontoTakeDamage
					
	def damageTransfer_InitiallyonHero(self, hero):
		if self.RamshieldExists[hero.ID] <= 0 or self.Game.playerStatus[hero.ID]["Immune"] > 0:
			return hero
		else:
			Ramshields = []
			for minion in self.Game.minionsonBoard(hero.ID):
				if minion.name == "Bolf Ramshield" and minion.silenced == False:
					Ramshields.append(minion)
					
			if Ramshields != []:
				Ramshields, order = self.Game.sort_Sequence(Ramshield)
				minion = Ramshields[0]
				return self.damageTransfer_InitiallyonMinion(minion)
			else:
				return hero
				
	def damageTransfer(self, target):
		if target.cardType == "Minion":
			return self.damageTransfer_InitiallyonMinion(target)
		elif target.cardType == "Hero":
			return self.damageTransfer_InitiallyonHero(target)
			
			
class CounterHandler:
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
		self.spellsCastonFriendliesThisGame = {1:[], 2:[]}
		
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
		self.CThunAttack = {1:6, 2:6}
		self.jadeGolemCounter = {1:1, 2:1}
		
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
		
		
class DiscoverHandler:
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
			
	def startDiscover(self, initiator):
		if self.Game.GUI != None:
			self.initiator = initiator
			self.Game.GUI.update()
			self.Game.GUI.waitforDiscover()
			self.initiator, self.Game.options = None, []
		
	def typeCardName(self, initiator):
		if self.Game.GUI != None:
			self.initiator = initiator
			PRINT(self, "Start to type the name of a card you want")
			self.Game.GUI.update()
			self.Game.GUI.wishforaCard(initiator)
			self.Game.options = []