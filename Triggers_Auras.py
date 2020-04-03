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
		self.receiver.stat_AuraAffected[0] += self.attackChange
		self.receiver.stat_AuraAffected[1] += self.healthChange
		self.receiver.stat_AuraAffected[2].append(self)
		self.source.auraAffected.append((self.receiver, self))
		PRINT(self.receiver, "Minion %s gains buffAura and its stat is %d/%d."%(self.receiver.name, self.receiver.attack, self.receiver.health))
	#Cleanse the aura_Receiver from the receiver and delete the (receiver, aura_Receiver) from source aura's list.
	def effectClear(self):
		self.receiver.statChange(-self.attackChange, -self.healthChange)
		self.receiver.stat_AuraAffected[0] -= self.attackChange
		self.receiver.stat_AuraAffected[1] -= self.healthChange
		extractfrom(self, self.receiver.stat_AuraAffected[2])
		extractfrom((self.receiver, self), self.source.auraAffected)
		PRINT(self.receiver, "Minion %s loses buffAura and its stat is %d/%d."%(self.receiver.name, self.receiver.attack, self.receiver.health))
	#Invoke when the receiver is copied and because the aura_Dealer won't have reference to this copied receiver,
	#remove this copied aura_Receiver from copied receiver's stat_AuraAffected[2].
	def effectDiscard(self):
		self.receiver.statChange(-self.attackChange, -self.healthChange)
		self.receiver.stat_AuraAffected[0] -= self.attackChange
		self.receiver.stat_AuraAffected[1] -= self.healthChange
		extractfrom(self, self.receiver.stat_AuraAffected[2])
		PRINT(self.receiver, "Minion %s loses buffAura and its stat is %d/%d."%(self.receiver.name, self.receiver.attack, self.receiver.health))
		
	def selfCopy(self, recipientMinion): #The recipient of the aura is the same minion when copying it.
		#Source won't change. 
		return type(self)(recipientMinion, self.source, self.attackChange, self.healthChange)
		
#def __init__(self, minion, func, attack, health):
class BuffAura_Dealer_Adjacent:
	def __init__(self, minion, func, attack, health):
		self.minion = minion
		if func != None:
			self.applicable = func
		self.attack = attack
		self.health = health
		self.auraAffected = [] #A list of (minion, aura_Receiver)
		
	#Minions appearing/disappearing will let the minion reevaluate the aura.
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.minion.onBoard
		
	def trigger(self, signal, ID, subject, target, number, comment, choice=0):
		if self.canTrigger(signal, ID, subject, target, number, comment):
			self.effect(signal, ID, subject, target, number, comment)
			
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		#重置对于两侧随从的光环
		for minion, aura_Receiver in fixedList(self.auraAffected):
			aura_Receiver.effectClear()
		#Find adjacent minions to self.minion, then try to register them.
		for minion in self.minion.Game.findAdjacentMinions(self.minion)[0]:
			self.applies(minion)
			
	def applicable(self, target):
		return True
		
	def applies(self, subject):
		if self.applicable(subject) and subject != self.minion:
			PRINT(self.minion, "Minion %s gains the %d/%d aura from %s"%(subject.name, self.attack, self.health, self.minion))
			aura_Receiver = BuffAura_Receiver(subject, self, self.attack, self.health)
			aura_Receiver.effectStart()
			
	def auraAppears(self):
		PRINT(self.minion, "{} appears and starts its buff aura {}".format(self.minion.name, self))
		for minion in self.minion.Game.findAdjacentMinions(self.minion)[0]:
			self.applies(minion)
			
		#Only need to handle minions that appear. Them leaving/silenced will be handled by the BuffAura_Receiver object.
		#We want this Trigger_MinionAppears can handle everything including registration and buff and removing.
		#self.minion.Game.triggersonBoard[self.minion.ID].append((self, "BoardRearranged"))
		self.minion.Game.triggersonBoard[self.minion.ID].append((self, "MinionAppears"))
		#随从disappears的时候已经把 光环效果清除并将自己从光环影响列表中移除。这里只是刷新光环而已。
		self.minion.Game.triggersonBoard[self.minion.ID].append((self, "MinionDisappears"))
		
	#When the aura object is no longer referenced, it vanishes automatically.
	def auraDisappears(self):
		PRINT(self.minion, "%s disappears and removes its effect."%self.minion.name)
		for minion, aura_Receiver in fixedList(self.auraAffected):
			aura_Receiver.effectClear()
			
		self.auraAffected = []
		#extractfrom((self, "BoardRearranged"), self.minion.Game.triggersonBoard[self.minion.ID])
		extractfrom((self, "MinionAppears"), self.minion.Game.triggersonBoard[self.minion.ID])
		extractfrom((self, "MinionDisappears"), self.minion.Game.triggersonBoard[self.minion.ID])
		
	def selfCopy(self, recipientMinion): #The recipientMinion is the minion that deals the Aura.
		#func that checks if subject is applicable will be the new copy's function
		return type(self)(recipientMinion, recipientMinion.applicable, self.attack, self.health)
		
#def __init__(self, minion, func, attack, health):
class BuffAura_Dealer_All:
	def __init__(self, minion, func, attack, health):
		self.minion = minion
		if func != None:
			self.applicable = func
		self.attack = attack
		self.health = health
		self.auraAffected = [] #A list of (minion, aura_Receiver)
		
	def applicable(self, target):
		return True
	#All minions appearing on the same side will be subject to the buffAura.
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		if self.minion.onBoard and subject.ID == self.minion.ID and subject != self.minion:
			if self.applicable(subject):
				return True
		return False
		
	def trigger(self, signal, ID, subject, target, number, comment, choice=0):
		if self.canTrigger(signal, ID, subject, target, number, comment):
			self.effect(signal, ID, subject, target, number, comment)
			
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.applies(subject)
		
	def applies(self, subject):
		if self.applicable(subject) and subject != self.minion:
			PRINT(self.minion, "Minion %s gains the %d/%d aura from %s"%(subject.name, self.attack, self.health, self.minion))
			aura_Receiver = BuffAura_Receiver(subject, self, self.attack, self.health)
			aura_Receiver.effectStart()
			
	def auraAppears(self):
		PRINT(self.minion, "{} appears and starts its buff aura {}".format(self.minion.name, self))
		for minion in self.minion.Game.minionsonBoard(self.minion.ID):
			self.applies(minion)
			
		#Only need to handle minions that appear. Them leaving/silenced will be handled by the BuffAura_Receiver object.
		#We want this Trigger_MinionAppears can handle everything including registration and buff and removing.
		self.minion.Game.triggersonBoard[self.minion.ID].append((self, "MinionAppears"))
		
	#When the aura object is no longer referenced, it vanishes automatically.
	def auraDisappears(self):
		PRINT(self.minion, "%s disappears and removes its effect."%self.minion.name)
		for minion, aura_Receiver in fixedList(self.auraAffected):
			aura_Receiver.effectClear()
			
		self.auraAffected = []
		extractfrom((self, "MinionAppears"), self.minion.Game.triggersonBoard[self.minion.ID])
		
	def selfCopy(self, recipientMinion): #The recipientMinion is the minion that deals the Aura.
		#func that checks if subject is applicable will be the new copy's function
		return type(self)(recipientMinion, recipientMinion.applicable, self.attack, self.health)
		
		
class BuffAura_Dealer_Enrage:
	def __init__(self, minion, attack):
		self.minion = minion
		self.attack = attack
		self.auraAffected = [] #A list of (minion, aura_Receiver)
		
	def auraAppears(self):
		pass
		
	def auraDisappears(self):
		pass
		
	def handleEnrage(self):
		if self.minion.onBoard:
			if self.minion.activated == False and self.minion.health < self.minion.health_upper:
				self.minion.activated = True
				BuffAura_Receiver(self.minion, self, self.attack, 0).effectStart()
			elif self.minion.activated and self.minion.health >= self.minion.health_upper:
				self.minion.activated = False
				for minion, aura_Receiver in fixedList(self.auraAffected):
					aura_Receiver.effectClear()
					
	def selfCopy(self, recipientMinion): #The recipientMinion is the minion that deals the Aura.
		#func that checks if subject is applicable will be the new copy's function
		return type(self)(recipientMinion, self.attack)
		
		
#战歌指挥官的光环相对普通的buff光环更特殊，因为会涉及到随从获得和失去光环的情况
class WarsongCommander_Aura:
	def __init__(self, minion):
		self.minion = minion
		self.auraAffected = [] #A list of (minion, aura_Receiver)
		
	#All minions appearing on the same side will be subject to the buffAura.
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		if self.minion.onBoard and subject.ID == self.minion.ID:
			#注意，战歌指挥官的光环可以作用在自己身上，这点区分于其他所有身材buff型光环。
			if signal == "MinionAppears" and subject.keyWords["Charge"] > 0:
				return True
			#随从只要发生了冲锋状态的变化就要调用战歌指挥官的Aura_Dealer，如果冲锋状态失去，则由该光环来移除其buff状态
			if signal == "MinionChargeKeywordChange":
				return True
		return False
		
	def trigger(self, signal, ID, subject, target, number, comment, choice=0):
		if self.canTrigger(signal, ID, subject, target, number, comment):
			self.effect(signal, ID, subject, target, number, comment)
			
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.applies(signal, subject)
		
	def applies(self, signal, subject):
		if signal == "MinionAppears":
			if subject.keyWords["Charge"] > 0:
				PRINT(self.minion, "Minion %s gains the +1 Attack aura from Warsong Commander"%subject.name)
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
		PRINT(self.minion, "{} appears and starts its buff aura {}".format(self.minion.name, self))
		for minion in self.minion.Game.minionsonBoard(self.minion.ID):
			self.applies("MinionAppears", minion) #The signal here is a placeholder and directs the function to first-time aura applicatioin
			
		#Only need to handle minions that appear. Them leaving/silenced will be handled by the BuffAura_Receiver object.
		#We want this Trigger_MinionAppears can handle everything including registration and buff and removing.
		self.minion.Game.triggersonBoard[self.minion.ID].append((self, "MinionAppears"))
		self.minion.Game.triggersonBoard[self.minion.ID].append((self, "MinionChargeKeywordChange"))
		
	#When the aura object is no longer referenced, it vanishes automatically.
	def auraDisappears(self):
		PRINT(self, "%s disappears and removes its effect."%self.minion.name)
		for minion, aura_Receiver in fixedList(self.auraAffected):
			aura_Receiver.effectClear()
			
		#3/4 Voidwalker, buffed by Mal'Ganis, losing the aura will change it to 1/3.		
		self.auraAffected = []
		extractfrom((self, "MinionAppears"), self.minion.Game.triggersonBoard[self.minion.ID])
		extractfrom((self, "MinionChargeKeywordChange"), self.minion.Game.triggersonBoard[self.minion.ID])
		
	def selfCopy(self, recipientMinion):
		return type(self)(recipientMinion)
		
#def __init__(self, receiver, source, keyWord):
class HasAura_Receiver:
	def __init__(self, receiver, source, keyWord):
		self.source = source #The aura.
		self.receiver = receiver
		self.keyWord = keyWord
		
	def effectStart(self):
		if self.keyWord in self.receiver.keyWords_AuraAffected:
			self.receiver.keyWords_AuraAffected[self.keyWord] += 1
		else:
			self.receiver.keyWords_AuraAffected[self.keyWord] = 1
		self.receiver.getsKeyword(self.keyWord)
		self.receiver.keyWords_AuraAffected["Auras"].append(self)
		self.source.auraAffected.append((self.receiver, self))
		PRINT(self.receiver, "Minion {} gains {} from Aura {}".format(self.receiver.name, self.keyWord, self.source))
	#The aura on the receiver is cleared and the source will remove this receiver and aura_Receiver from it's list.
	def effectClear(self):
		if self.receiver.keyWords_AuraAffected[self.keyWord] > 0:
			self.receiver.keyWords_AuraAffected[self.keyWord] -= 1
		self.receiver.losesKeyword(self.keyWord)
		extractfrom(self, self.receiver.keyWords_AuraAffected["Auras"])
		extractfrom((self.receiver, self), self.source.auraAffected)
		
	#After a receiver is deep copied, it will also copy this aura_Receiver, simply remove it.
	#The aura_Dealer won't have reference to this copied aura.
	def effectDiscard(self):
		if self.receiver.keyWords_AuraAffected[self.keyWord] > 0:
			self.receiver.keyWords_AuraAffected[self.keyWord] -= 1
			self.receiver.losesKeyword(self.keyWord)
		extractfrom(self, self.receiver.keyWords_AuraAffected["Auras"])
		
	def selfCopy(self, recipientMinion):
		return type(self)(recipientMinion, self.source, self.keyWord)
		
class HasAura_Dealer:
	def __init__(self, minion, func, keyWord):
		self.minion = minion #For now, there are only three minions that provide this kind aura: Tundra Rhino, Houndmaster Shaw, Whirlwind Tempest
		if func != None:
			self.applicable = func
		self.keyWord = keyWord
		self.auraAffected = [] #List of (receiver, aura_Receiver)
		
	def applicable(self, target):
		return True
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		if self.minion.onBoard and subject.ID == self.minion.ID and subject != self.minion:
			if self.applicable(subject):
				return True
		return False
		
	def trigger(self, signal, ID, subject, target, number, comment, choice=0):
		if self.canTrigger(signal, ID, subject, target, number, comment):
			self.effect(signal, ID, subject, target, number, comment)
			
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.applies(subject)
		
	def applies(self, subject):
		if self.applicable(subject):
			PRINT(self.minion, "Minion %s gains keyWord %s from %s"%(subject.name, self.keyWord, self.minion))
			aura_Receiver = HasAura_Receiver(subject, self, self.keyWord)
			aura_Receiver.effectStart()
			
	def auraAppears(self):
		PRINT(self.minion, "{} appears and starts it's aura {}".format(self.minion.name, self))
		for minion in self.minion.Game.minionsonBoard(self.minion.ID):
			self.applies(minion)
			
		#Handle minion that appear and get silenced.
		self.minion.Game.triggersonBoard[self.minion.ID].append((self, "MinionAppears"))
		
	def auraDisappears(self):
		PRINT(self.minion, "Aura {} disappears and removes its effect.".format(self))
		for minion, aura_Receiver in fixedList(self.auraAffected):
			aura_Receiver.effectClear()
			
		self.auraAffected = []
		extractfrom((self, "MinionAppears"), self.minion.Game.triggersonBoard[self.minion.ID])
		
	def selfCopy(self, recipient):
		return type(self)(recipient, recipient.applicable, self.keyWord)
		
#Dr. Boom. Mad Genius's Aura. You Mechs have Rush.
class MechsHaveRush:
	def __init__(self, Game, ID):
		self.Game = Game
		self.ID = ID
		self.hasAuraAffected = []
		
	def applicable(self, target):
		return "Mech" in target.race and target.ID == self.ID
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return subject.ID == self.ID and self.applicable(subject)
		
	def trigger(self, signal, ID, subject, target, number, comment, choice=0):
		if self.canTrigger(signal, ID, subject, target, number, comment):
			self.effect(signal, ID, subject, target, number, comment)
			
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.applies(subject)
		
	def applies(self, subject):
		if self.applicable(subject):
			aura_Receiver = HasAura_Receiver(subject, self, "Rush")
			aura_Receiver.effectStart()
			
	def auraAppears(self):
		PRINT(self, "Dr. Boom. Mad Genius' aura starts it's effect.")
		for minion in self.Game.minionsonBoard(self.ID):
			self.applies(minion)
			
		#该光环一旦出现不会消失，所以可以直接在Game的triggersonBoard中登记，同时不需要存到其他的entity之下。
		self.Game.triggersonBoard[self.ID].append((self, "MinionAppears"))
		
	def selfCopy(self, recipientGame):
		return type(self)(recipientGame, self.ID)
		
		
#Currently only Spiteful Smith has this aura
#def __init__(self, receiver, source):
#目前为止所有的武器光环都是+2攻
class WeaponBuffAura_Receiver:
	def __init__(self, receiver, source):
		self.source = source
		self.receiver = receiver
		
	def effectStart(self):
		self.receiver.gainStat(2, 0)
		self.receiver.stat_AuraAffected[0] += 2
		self.receiver.stat_AuraAffected[1].append(self)
		self.source.auraAffected.append((self.receiver, self))
		
	#Cleanse the aura_Receiver from the receiver and delete the (receiver, aura_Receiver) from source aura's list.
	def effectClear(self):
		self.receiver.gainStat(-2, 0)
		self.receiver.stat_AuraAffected[0] -= 2
		extractfrom(self, self.receiver.stat_AuraAffected[1])
		extractfrom((self.receiver, self), self.source.auraAffected)
		
	#Invoke when the receiver is copied and because the aura_Dealer won't have reference to this copied receiver,
	#remove this copied aura_Receiver from copied receiver's stat_AuraAffected[2].
	def effectDiscard(self):
		self.receiver.gainStat(-2, 0)
		self.receiver.stat_AuraAffected[0] -= 2
		extractfrom(self, self.receiver.stat_AuraAffected[1])
		
	def selfCopy(self, recipient):
		return type(self)(recipient, self.source)
		
		
class WeaponBuffAura_SpitefulSmith:
	def __init__(self, minion):
		self.minion = minion
		self.auraAffected = []
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.minion.onBoard and subject.ID == self.minion.ID
		
	def trigger(self, signal, ID, subject, target, number, comment, choice=0):
		if self.canTrigger(signal, ID, subject, target, number, comment):
			self.effect(signal, ID, subject, target, number, comment)
			
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.applies(subject)
		
	def applies(self, subject):
		aura_Receiver = WeaponBuffAura_Receiver(subject, self)
		aura_Receiver.effectStart()
		
	def auraAppears(self):
		#在随从自己登场时，就会尝试开始这个光环，但是如果没有激怒，则无事发生。
		if self.minion.health < self.minion.health_upper:
			self.minion.activated = True
			weapon = self.minion.Game.availableWeapon(self.minion.ID)
			#这个Aura_Dealer可以由激怒和出场两个方式来控制。
			if weapon != None and weapon not in self.auraAffected:
				self.applies(weapon)
				
			self.minion.Game.triggersonBoard[self.minion.ID].append((self, "WeaponEquipped"))
			
	def auraDisappears(self):
		PRINT(self.minion, "WeaponBuffAura_Dealer is shut down. Now remove its effect on weapons, if any.")
		for weapon, aura_Receiver in fixedList(self.auraAffected):
			aura_Receiver.effectClear()
			
		self.auraAffected = []
		extractfrom((self, "WeaponEquipped"), self.minion.Game.triggersonBoard[self.minion.ID])
		
	def selfCopy(self, recipientMinion):
		return type(self)(recipientMinion)
		
		
class Deathrattle_Minion(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity)
		
	def blank_init(self, entity):
		self.entity = entity
		self.signals = ["MinionDies", "DeathrattleTriggers"]
		
	def connect(self):
		for signal in self.signals:
			self.entity.Game.triggersonBoard[self.entity.ID].append((self, signal))
			
	def disconnect(self):
		for signal in self.signals:
			extractfrom((self, signal), self.entity.Game.triggersonBoard[self.entity.ID])
			
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
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		pass
		
	def selfCopy(self, recipientMinion): #用于无面操纵者等复制场上随从时亡语的复制。
		return type(self)(recipientMinion) #巫毒娃娃等需要记录一定信息的亡语会有自己的专有函数
		
		
class Deathrattle_Weapon(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity)
		
	def blank_init(self, entity):
		self.entity = entity
		self.signals = ["WeaponDestroyed"]
		
	def connect(self):
		for signal in self.signals:
			self.entity.Game.triggersonBoard[self.entity.ID].append((self, signal))
			
	def disconnect(self):
		for signal in self.signals:
			extractfrom((self, signal), self.entity.Game.triggersonBoard[self.entity.ID])
			
	def trigger(self, signal, ID, subject, target, number, comment, choice=0):
		if self.entity.Game.playerStatus[self.entity.ID]["Weapon Deathrattle Trigger Twice"] > 0:
			if self.canTrigger(signal, ID, subject, target, number, comment):
				self.effect(signal, ID, subject, target, number, comment)
		if self.canTrigger(signal, ID, subject, target, number, comment):
			self.effect(signal, ID, subject, target, number, comment)
			
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return target == self.entity
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		pass
		
	def selfCopy(self, recipientWeapon):
		return type(self)(recipientWeapon)
		
		
class SecretTrigger(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionBeenPlayed"])
		
	def blank_init(self, entity, signals):
		self.entity = entity
		self.signals = signals
		
	def connect(self):
		for signal in self.signals:
			self.entity.Game.triggersonBoard[self.entity.ID].append((self, signal))
			
	def disconnect(self):
		for signal in self.signals:
			extractfrom((self, signal), self.entity.Game.triggersonBoard[self.entity.ID])
			
	def trigger(self, signal, ID, subject, target, number, comment, choice=0):
		if self.entity.Game.playerStatus[self.entity.ID]["Secret Trigger Twice"] > 0:
			if self.canTrigger(signal, ID, subject, target, number, comment):
				self.effect(signal, ID, subject, target, number, comment)
				
		if self.canTrigger(signal, ID, subject, target, number, comment):
			self.effect(signal, ID, subject, target, number, comment)
			
		self.entity.Game.sendSignal("SecretRevealed", self.entity.Game.turn, self.entity, None, 0, "")
		self.disconnect()
		extractfrom(self.entity, self.entity.Game.SecretHandler.secrets[self.entity.ID])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return True
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		pass
		
	def selfCopy(self, recipient):
		return type(self)(recipient)
		
		
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
		
	def connect(self):
		for signal in self.signals:
			PRINT(self, "Quest {} now registers trigger {}".format(self.entity, (self, signal)))
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
		
	def selfCopy(self, recipient):
		return type(self)(recipient)