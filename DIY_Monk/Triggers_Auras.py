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
		
#对于随从的场上扳机，其被复制的时候所有暂时和非暂时的扳机都会被复制。
#但是随从返回其额外效果的时候，只有其非暂时场上扳机才会被返回（永恒祭司），暂时扳机需要舍弃。
class TriggeronBoard:
	def __init__(self, entity):
		self.blank_init(entity, [])
		
	def blank_init(self, entity, signals):
		self.entity = entity
		self.signals = signals
		self.temp = False
		
	def connect(self):
		for signal in self.signals:
			self.entity.Game.triggersonBoard[self.entity.ID].append((self, signal))
			
	def disconnect(self):
		for signal in self.signals:
			extractfrom((self, signal), self.entity.Game.triggersonBoard[self.entity.ID])
			
	def trigger(self, signal, ID, subject, target, number, comment, choice=0):
		if self.canTrigger(signal, ID, subject, target, number, comment):
			self.effect(signal, ID, subject, target, number, comment)
			
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return True
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		pass
		
	#一般只有需要额外定义ID的回合开始和结束扳机需要有自己的selfCopy函数
	def selfCopy(self, recipient):
		return type(self)(recipient)
		
	#这个扳机会在复制随从列表，手牌和牌库列表之前调用，扳机所涉及的随从，武器等会被复制
	#游戏会检查triggersonBoard中的每个(trig, signal),产生一个复制(trigCopy, signal)，并注册
	#这里负责处理产生一个trigCopy
	def createCopy(self, recipientGame):
		if self not in recipientGame.copiedObjs: #这个扳机没有被复制过
			entityCopy = self.entity.createCopy(recipientGame)
			trigCopy = self.selfCopy(entityCopy)
			recipientGame.copiedObjs[self] = trigCopy
			return trigCopy
		else: #一个扳机被复制过了，则其携带者也被复制过了
			return recipientGame.copiedObjs[self]
			
			
class TriggerinHand:
	def __init__(self, entity):
		self.blank_init(entity, [])
		
	def blank_init(self, entity, signals):
		self.entity = entity
		self.signals = signals
		self.temp = False
		
	def connect(self):
		for signal in self.signals:
			self.entity.Game.triggersinHand[self.entity.ID].append((self, signal))
			
	def disconnect(self):
		for signal in self.signals:
			extractfrom((self, signal), self.entity.Game.triggersinHand[self.entity.ID])
			
	def trigger(self, signal, ID, subject, target, number, comment, choice=0):
		if self.canTrigger(signal, ID, subject, target, number, comment):
			self.effect(signal, ID, subject, target, number, comment)
			
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return True
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		pass
		
	def selfCopy(self, recipient):
		return type(self)(recipient)
		
	def createCopy(self, recipientGame):
		if self not in recipientGame.copiedObjs: #这个扳机没有被复制过
			entityCopy = self.entity.createCopy(recipientGame)
			trigCopy = type(self)(entityCopy)
			recipientGame.copiedObjs[self] = trigCopy
			return trigCopy
		else: #一个扳机被复制过了，则其携带者也被复制过了
			return recipientGame.copiedObjs[self]
			
			
class TriggerinDeck:
	def __init__(self, entity):
		self.blank_init(entity, [])
		
	def blank_init(self, entity, signals):
		self.entity = entity
		self.signals = signals
		self.temp = False
		
	def connect(self):
		for signal in self.signals:
			self.entity.Game.triggersinDeck[self.entity.ID].append((self, signal))
			
	def disconnect(self):
		for signal in self.signals:
			extractfrom((self, signal), self.entity.Game.triggersinDeck[self.entity.ID])
			
	def trigger(self, signal, ID, subject, target, number, comment, choice=0):
		if self.canTrigger(signal, ID, subject, target, number, comment):
			self.effect(signal, ID, subject, target, number, comment)
			
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return True
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		pass
		
	def selfCopy(self, recipient):
		return type(self)(recipient)
		
	def createCopy(self, recipientGame):
		if self not in recipientGame.copiedObjs: #这个扳机没有被复制过
			entityCopy = self.entity.createCopy(recipientGame)
			trigCopy = type(self)(entityCopy)
			recipientGame.copiedObjs[self] = trigCopy
			return trigCopy
		else: #一个扳机被复制过了，则其携带者也被复制过了
			return recipientGame.copiedObjs[self]
			
			
"""Variants of triggeronBoard, triggerinHand, triggerinDeck"""
class Deathrattle_Minion(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity)
		
	def blank_init(self, entity):
		self.entity = entity
		self.signals = ["MinionDies", "DeathrattleTriggers"]
		
	def trigger(self, signal, ID, subject, target, number, comment, choice=0):
		if self.entity.Game.playerStatus[self.entity.ID]["Deathrattle Trigger Twice"] > 0:
			if self.canTrigger(signal, ID, subject, target, number, comment):
				self.effect(signal, ID, subject, target, number, comment)
		if self.canTrigger(signal, ID, subject, target, number, comment):
			self.effect(signal, ID, subject, target, number, comment)
			if signal == "MinionDies": #随从通过死亡触发的亡语扳机需要在亡语触发之后注销。
				self.disconnect()
		else: #随从通过其他效果触发亡语之后，如果随从不再在场上的话，注销死亡扳机
			#随从可能被其他卡片效果触发亡语的位置有场上和手牌中，在手牌中触发时不会注册扳机
			#因而只要不在随从列表中就可以在触发死亡扳机后注销，主要适用于死亡扳机的区域移动效果
			if self.entity not in self.entity.Game.minions[self.entity.ID]:
				self.disconnect() #如果这个扳机没有实际注册，则注销时无事发生
				
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return target == self.entity
		
		
class Deathrattle_Weapon(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity)
		
	def blank_init(self, entity):
		self.entity = entity
		self.signals = ["WeaponDestroyed"]
		
	def trigger(self, signal, ID, subject, target, number, comment, choice=0):
		if self.entity.Game.playerStatus[self.entity.ID]["Weapon Deathrattle Trigger Twice"] > 0:
			if self.canTrigger(signal, ID, subject, target, number, comment):
				self.effect(signal, ID, subject, target, number, comment)
		if self.canTrigger(signal, ID, subject, target, number, comment):
			self.effect(signal, ID, subject, target, number, comment)
			
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return target == self.entity
		
		
class SecretTrigger(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionBeenPlayed"])
		
	def blank_init(self, entity, signals):
		self.entity = entity
		self.signals = signals
		
	def trigger(self, signal, ID, subject, target, number, comment, choice=0):
		if self.entity.Game.playerStatus[self.entity.ID]["Secret Trigger Twice"] > 0:
			if self.canTrigger(signal, ID, subject, target, number, comment):
				self.effect(signal, ID, subject, target, number, comment)
				
		if self.canTrigger(signal, ID, subject, target, number, comment):
			self.effect(signal, ID, subject, target, number, comment)
			
		self.entity.Game.sendSignal("SecretRevealed", self.entity.Game.turn, self.entity, None, 0, "")
		self.disconnect()
		extractfrom(self.entity, self.entity.Game.SecretHandler.secrets[self.entity.ID])
		
		
class Trigger_Echo(TriggerinHand):
	def __init__(self, entity):
		self.blank_init(entity, ["TurnEnds"])
		self.temp = True
		self.makesCardEvanescent = True
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.inHand #Echo disappearing should trigger at the end of any turn
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self, "At the end of turn, Echo card %s disappears."%self.entity.name)
		self.entity.Game.Hand_Deck.extractfromHand(self.entity)
		
		
class Trigger_WorgenShift_FromHuman(TriggerinHand):
	def __init__(self, entity, worgenType):
		self.blank_init(entity, ["TurnEnds"])
		self.worgenType = worgenType
		self.makesCardEvanescent = True
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.inHand and ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self, "At the end of turn, %s transforms for into a worgen"%self.entity.name)
		worgen = self.worgenType(self.entity.Game, self.entity.ID)
		worgen.statReset(self.entity.health_Enchant, self.entity.attack_Enchant)
		worgen.identity = self.entity.identity
		#狼人形态会复制人形态的场上扳机，但是目前没有给随从外加手牌和牌库扳机的机制。
		#目前不考虑狼人牌在变形前保有的临时攻击力buff
		worgen.triggersonBoard = self.entity.triggersonBoard
		self.entity.Game.Hand_Deck.replaceCardinHand(self.entity, worgen)
		
		
class Trigger_WorgenShift_FromWorgen(TriggerinHand):
	def __init__(self, entity, humanType):
		self.blank_init(entity, ["TurnEnds"])
		self.humanType = humanType
		self.makesCardEvanescent = True
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.inHand and ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self, "At the end of turn, %s transforms for into a worgen"%self.entity.name)
		human = self.humanType(self.entity.Game, self.entity.ID)
		human.statReset(self.entity.health_Enchant, self.entity.attack_Enchant)
		human.identity = self.entity.identity
		#狼人形态会复制人形态获得的场上扳机，但是目前没有给随从外加手牌和牌库扳机的机制。
		#目前不考虑狼人牌在变形前保有的临时攻击力buff
		human.triggersonBoard = self.entity.triggersonBoard
		self.entity.Game.Hand_Deck.replaceCardinHand(self.entity, human)
		
		
class QuestTrigger(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionBeenPlayed"])
		
	def blank_init(self, entity, signals):
		self.entity = entity
		self.signals = signals
		self.accomplished = False
		
	def trigger(self, signal, ID, subject, target, number, comment, choice=0):
		if self.canTrigger(signal, ID, subject, target, number, comment):
			self.effect(signal, ID, subject, target, number, comment)
			
			
#def __init__(self, receiver, source, attackChange, healthChange):
class BuffAura_Receiver:
	#Source is the Aura not the entity that creates the aura.
	def __init__(self, receiver, source, attackChange, healthChange):
		self.source = source
		self.attackChange = attackChange #Positive by default.
		self.healthChange = healthChange
		self.receiver = receiver
		
	def effectStart(self):
		self.receiver.statChange(self.attackChange, self.healthChange)
		self.receiver.statbyAura[0] += self.attackChange
		self.receiver.statbyAura[1] += self.healthChange
		self.receiver.statbyAura[2].append(self)
		self.source.auraAffected.append((self.receiver, self))
		#PRINT(self.receiver, "Minion %s gains buffAura and its stat is %d/%d."%(self.receiver.name, self.receiver.attack, self.receiver.health))
	#Cleanse the aura_Receiver from the receiver and delete the (receiver, aura_Receiver) from source aura's list.
	def effectClear(self):
		self.receiver.statChange(-self.attackChange, -self.healthChange)
		self.receiver.statbyAura[0] -= self.attackChange
		self.receiver.statbyAura[1] -= self.healthChange
		extractfrom(self, self.receiver.statbyAura[2])
		extractfrom((self.receiver, self), self.source.auraAffected)
		#PRINT(self.receiver, "Minion %s loses buffAura and its stat is %d/%d."%(self.receiver.name, self.receiver.attack, self.receiver.health))
	#Invoke when the receiver is copied and because the aura_Dealer won't have reference to this copied receiver,
	#remove this copied aura_Receiver from copied receiver's statbyAura[2].
	def effectDiscard(self):
		self.receiver.statChange(-self.attackChange, -self.healthChange)
		self.receiver.statbyAura[0] -= self.attackChange
		self.receiver.statbyAura[1] -= self.healthChange
		extractfrom(self, self.receiver.statbyAura[2])
		#PRINT(self.receiver, "Minion %s loses buffAura and its stat is %d/%d."%(self.receiver.name, self.receiver.attack, self.receiver.health))
		
	def selfCopy(self, recipient): #The recipient of the aura is the same minion when copying it.
		#Source won't change.
		return type(self)(recipient, self.source, self.attackChange, self.healthChange)
	#aura_Receiver一定是附属于一个随从的，在复制游戏的过程中，优先会createCopy光环本体，之后是光环影响的随从，
	#随从createCopy过程中会复制出没有source的receiver，所以receiver本身没有必要有createCopy
	
	
class AuraDealer_toMinion:
	def applicable(self, target):
		return self.entity.applicable(target)
		
	def trigger(self, signal, ID, subject, target, number, comment, choice=0):
		if self.canTrigger(signal, ID, subject, target, number, comment):
			self.effect(signal, ID, subject, target, number, comment)
			
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.applies(subject)
		
	def auraAppears(self):
		for minion in self.entity.Game.minionsonBoard(self.entity.ID):
			self.applies(minion)
		#Only need to handle minions that appear. Them leaving/silenced will be handled by the BuffAura_Receiver object.
		for signal in self.signals:
			self.entity.Game.triggersonBoard[self.entity.ID].append((self, signal))
			
	def auraDisappears(self):
		for minion, aura_Receiver in fixedList(self.auraAffected):
			aura_Receiver.effectClear()
			
		self.auraAffected = []
		for signal in self.signals:
			extractfrom((self, signal), self.entity.Game.triggersonBoard[self.entity.ID])
			
	#这个函数会在复制场上扳机列表的时候被调用。
	def createCopy(self, recipientGame):
		#一个光环的注册可能需要注册多个扳机
		if self not in recipientGame.copiedObjs: #这个光环没有被复制过
			entityCopy = self.entity.createCopy(recipientGame)
			Copy = self.selfCopy(entityCopy)
			recipientGame.copiedObjs[self] = Copy
			if hasattr(self, "keyWord"): #是关键字光环
				for minion, aura_Receiver in self.auraAffected:
					minionCopy = minion.createCopy(recipientGame)
					#复制一个随从的时候已经复制了其携带的光环buff状态receiver
					#这里只需要找到那个receiver的位置即可
					##注意一个随从在复制的时候需要把它的buffAura_Receiver，keyWordAura_Reciever和manaMods一次性全部复制之后才能进行光环发出者的复制
					#相应地，这些光环receiver的来源全部被标为None，需要在之后处理它们的来源时一一补齐
					receiverIndex = minion.keyWordbyAura["Auras"].index(aura_Receiver)
					receiverCopy = minionCopy.keyWordbyAura["Auras"][receiverIndex]
					receiverCopy.source = Copy #补上这个receiver的source
					Copy.auraAffected.append((minionCopy, receiverCopy))
			else: #不是关键字光环，而是buff光环
				for minion, aura_Receiver in self.auraAffected:
					minionCopy = minion.createCopy(recipientGame)
					receiverIndex = minion.statbyAura[2].index(aura_Receiver)
					receiverCopy = minionCopy.statbyAura[2][receiverIndex]
					receiverCopy.source = Copy #补上这个receiver的source
					Copy.auraAffected.append((minionCopy, receiverCopy))
			return Copy
		else:
			return recipientGame.copiedObjs[self]
			
#def __init__(self, minion, func, attack, health):
class BuffAura_Dealer_Adjacent(AuraDealer_toMinion):
	def __init__(self, entity, attack, health):
		self.entity = entity
		self.attack, self.health = attack, health
		self.signals, self.auraAffected = ["MinionAppears", "MinionDisappears"], []
	#Minions appearing/disappearing will let the minion reevaluate the aura.
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		#重置对于两侧随从的光环
		for minion, aura_Receiver in fixedList(self.auraAffected):
			aura_Receiver.effectClear()
		#Find adjacent minions to self.entity, then try to register them.
		for minion in self.entity.Game.findAdjacentMinions(self.entity)[0]:
			self.applies(minion)
			
	def applies(self, subject):
		if subject != self.entity:
			aura_Receiver = BuffAura_Receiver(subject, self, self.attack, self.health)
			aura_Receiver.effectStart()
			
	def auraAppears(self):
		for minion in self.entity.Game.findAdjacentMinions(self.entity)[0]:
			self.applies(minion)
			
		#Only need to handle minions that appear. Them leaving/silenced will be handled by the BuffAura_Receiver object.
		self.entity.Game.triggersonBoard[self.entity.ID].append((self, "MinionAppears"))
		#随从disappears的时候已经把 光环效果清除并将自己从光环影响列表中移除。这里只是刷新光环而已。
		self.entity.Game.triggersonBoard[self.entity.ID].append((self, "MinionDisappears"))
		
	def selfCopy(self, recipientMinion): #The recipientMinion is the minion that deals the Aura.
		return type(self)(recipientMinion, self.attack, self.health)
	#可以通过AuraDealer_toMinion的createCopy方法复制
	
	
class BuffAura_Dealer_All(AuraDealer_toMinion):
	def __init__(self, entity, attack, health):
		self.entity = entity
		self.attack, self.health = attack, health
		self.signals, self.auraAffected = ["MinionAppears"], []
		
	#All minions appearing on the same side will be subject to the buffAura.
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		if self.entity.onBoard and subject.ID == self.entity.ID and subject != self.entity:
			if self.applicable(subject):
				return True
		return False
		
	def applies(self, subject):
		if self.applicable(subject) and subject != self.entity:
			aura_Receiver = BuffAura_Receiver(subject, self, self.attack, self.health)
			aura_Receiver.effectStart()
			
	def selfCopy(self, recipient): #The recipient is the entity that deals the Aura.
		#func that checks if subject is applicable will be the new copy's function
		return type(self)(recipient, recipient.applicable, self.attack, self.health)
		
		
class BuffAura_Dealer_Enrage(AuraDealer_toMinion):
	def __init__(self, entity, attack):
		self.entity = entity
		self.attack = attack
		self.auraAffected = [] #A list of (entity, aura_Receiver)
	#光环开启和关闭都取消，因为要依靠随从自己的handleEnrage来触发
	def auraAppears(self):
		pass
		
	def auraDisappears(self):
		pass
		
	def handleEnrage(self):
		if self.entity.onBoard:
			if self.entity.activated == False and self.entity.health < self.entity.health_upper:
				self.entity.activated = True
				BuffAura_Receiver(self.entity, self, self.attack, 0).effectStart()
			elif self.entity.activated and self.entity.health >= self.entity.health_upper:
				self.entity.activated = False
				for entity, aura_Receiver in fixedList(self.auraAffected):
					aura_Receiver.effectClear()
					
	def selfCopy(self, recipientMinion): #The recipientMinion is the entity that deals the Aura.
		#func that checks if subject is applicable will be the new copy's function
		return type(self)(recipientMinion, self.attack)
	#激怒的光环仍然可以通过AuraDealer_toMinion的createCopy复制
	
#战歌指挥官的光环相对普通的buff光环更特殊，因为会涉及到随从获得和失去光环的情况
class WarsongCommander_Aura(AuraDealer_toMinion):
	def __init__(self, entity):
		self.entity = entity
		self.signals, self.auraAffected = ["MinionAppears", "MinionChargeKeywordChange"], []
		
	#All minions appearing on the same side will be subject to the buffAura.
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		if self.entity.onBoard and subject.ID == self.entity.ID:
			#注意，战歌指挥官的光环可以作用在自己身上，这点区分于其他所有身材buff型光环。
			if signal == "MinionAppears" and subject.keyWords["Charge"] > 0:
				return True
			#随从只要发生了冲锋状态的变化就要调用战歌指挥官的Aura_Dealer，如果冲锋状态失去，则由该光环来移除其buff状态
			if signal == "MinionChargeKeywordChange":
				return True
		return False
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.applies(signal, subject)
		
	def applies(self, signal, subject):
		if signal == "MinionAppears":
			if subject.keyWords["Charge"] > 0:
				aura_Receiver = BuffAura_Receiver(subject, self, 1, 0)
				aura_Receiver.effectStart()
		else: #signal == "MinionChargeKeywordChange"
			if subject.keyWords["Charge"] > 0:
				notAffectedPreviously = True
				for receiver, aura_Receiver in fixedList(self.auraAffected):
					if subject == receiver:
						notAffectedPreviously = False
						break
				if notAffectedPreviously:
					aura_Receiver = BuffAura_Receiver(subject, self, 1, 0)
					aura_Receiver.effectStart()
			elif subject.keyWords["Charge"] < 1:
				for receiver, aura_Receiver in fixedList(self.auraAffected):
					if subject == receiver:
						aura_Receiver.effectClear()
						break
						
	def auraAppears(self):
		for minion in self.entity.Game.minionsonBoard(self.entity.ID):
			self.applies("MinionAppears", minion) #The signal here is a placeholder and directs the function to first-time aura applicatioin
			
		for signal in self.signals:
			extractfrom((self, signal), self.entity.Game.triggersonBoard[self.entity.ID])
			
	def selfCopy(self, recipientMinion):
		return type(self)(recipientMinion)
	#可以通过AuraDealer_toMinion的createCopy方法复制
	
class HasAura_Receiver:
	def __init__(self, receiver, source, keyWord):
		self.source = source #The aura.
		self.receiver = receiver
		self.keyWord = keyWord
		
	def effectStart(self):
		if self.keyWord in self.receiver.keyWordbyAura:
			self.receiver.keyWordbyAura[self.keyWord] += 1
		else:
			self.receiver.keyWordbyAura[self.keyWord] = 1
		self.receiver.getsKeyword(self.keyWord)
		self.receiver.keyWordbyAura["Auras"].append(self)
		self.source.auraAffected.append((self.receiver, self))
		
	#The aura on the receiver is cleared and the source will remove this receiver and aura_Receiver from it's list.
	def effectClear(self):
		if self.receiver.keyWordbyAura[self.keyWord] > 0:
			self.receiver.keyWordbyAura[self.keyWord] -= 1
		self.receiver.losesKeyword(self.keyWord)
		extractfrom(self, self.receiver.keyWordbyAura["Auras"])
		extractfrom((self.receiver, self), self.source.auraAffected)
		
	#After a receiver is deep copied, it will also copy this aura_Receiver, simply remove it.
	#The aura_Dealer won't have reference to this copied aura.
	def effectDiscard(self):
		if self.receiver.keyWordbyAura[self.keyWord] > 0:
			self.receiver.keyWordbyAura[self.keyWord] -= 1
			self.receiver.losesKeyword(self.keyWord)
		extractfrom(self, self.receiver.keyWordbyAura["Auras"])
		
	def selfCopy(self, recipient):
		return type(self)(recipient, self.source, self.keyWord)
		
class HasAura_Dealer(AuraDealer_toMinion):
	def __init__(self, entity, keyWord):
		self.entity = entity
		self.keyWord = keyWord
		self.signals, self.auraAffected = ["MinionAppears"], [] #List of (receiver, aura_Receiver)
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		if self.entity.onBoard and subject.ID == self.entity.ID and subject != self.entity:
			if self.applicable(subject):
				return True
		return False
		
	def applies(self, subject):
		if self.applicable(subject):
			aura_Receiver = HasAura_Receiver(subject, self, self.keyWord)
			aura_Receiver.effectStart()
			
	def selfCopy(self, recipient):
		return type(self)(recipient, self.keyWord)
	#关键字光环可以通过AuraDealer_toMinion的createCopy方法复制
	
#Dr. Boom. Mad Genius's Aura. You Mechs have Rush.
class MechsHaveRush(AuraDealer_toMinion):
	def __init__(self, Game, ID):
		self.Game, self.ID = Game, ID
		self.keyWord = "Rush"
		self.signals, self.hasAuraAffected = ["MinionAppears"], []
		
	def applicable(self, target):
		return "Mech" in target.race and target.ID == self.ID
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return subject.ID == self.ID and self.applicable(subject)
		
	def applies(self, subject):
		if self.applicable(subject):
			aura_Receiver = HasAura_Receiver(subject, self, "Rush")
			aura_Receiver.effectStart()
			
	def auraAppears(self):
		PRINT(self, "Dr. Boom. Mad Genius' aura starts it's effect.")
		for minion in self.Game.minionsonBoard(self.ID):
			self.applies(minion)
			
		self.Game.triggersonBoard[self.ID].append((self, "MinionAppears"))
		
	def auraDisappears(self):
		pass
		
	def selfCopy(self, recipient):
		return type(self)(recipient, self.ID)
	#可以通过AuraDealer_toMinion的createCopy方法复制
	
#Currently only Spiteful Smith has this aura
#def __init__(self, receiver, source):
#目前为止所有的武器光环都是+2攻
class WeaponBuffAura_Receiver:
	def __init__(self, receiver, source):
		self.source = source
		self.receiver = receiver
		
	def effectStart(self):
		self.receiver.gainStat(2, 0)
		self.receiver.statbyAura[0] += 2
		self.receiver.statbyAura[1].append(self)
		self.source.auraAffected.append((self.receiver, self))
	#Cleanse the aura_Receiver from the receiver and delete the (receiver, aura_Receiver) from source aura's list.
	def effectClear(self):
		self.receiver.gainStat(-2, 0)
		self.receiver.statbyAura[0] -= 2
		extractfrom(self, self.receiver.statbyAura[1])
		extractfrom((self.receiver, self), self.source.auraAffected)
	#Invoke when the receiver is copied and because the aura_Dealer won't have reference to this copied receiver,
	#remove this copied aura_Receiver from copied receiver's statbyAura[2].
	def effectDiscard(self):
		self.receiver.gainStat(-2, 0)
		self.receiver.statbyAura[0] -= 2
		extractfrom(self, self.receiver.statbyAura[1])
		
	def selfCopy(self, recipient):
		return type(self)(recipient, self.source)
	#武器的本体复制一定优先，其复制过程中会自行创建没有source的receiver，receiver自己没有必要创建createCopy方法
	