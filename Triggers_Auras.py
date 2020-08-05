def extractfrom(target, listObj):
	try: return listObj.pop(listObj.index(target))
	except: return None
	
def fixedList(listObj):
	return listObj[0:len(listObj)]
	
def PRINT(game, string, *args):
	if game.GUI:
		if not game.mode: game.GUI.printInfo(string)
	elif not game.mode: print("game's guide mode is 0\n", string)
	
#对于随从的场上扳机，其被复制的时候所有暂时和非暂时的扳机都会被复制。
#但是随从返回其额外效果的时候，只有其非暂时场上扳机才会被返回（永恒祭司），暂时扳机需要舍弃。
class TrigBoard:
	def __init__(self, entity):
		self.blank_init(entity, [])
		
	def blank_init(self, entity, signals):
		self.entity, self.signals, self.temp = entity, signals, False
		
	def connect(self):
		for sig in self.signals:
			try: self.entity.Game.trigsBoard[self.entity.ID][sig].append(self)
			except: self.entity.Game.trigsBoard[self.entity.ID][sig] = [self]
			
	def disconnect(self):
		for sig in self.signals:
			try: self.entity.Game.trigsBoard[self.entity.ID][sig].remove(self)
			except: pass
			
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return True
		
	def trigger(self, signal, ID, subject, target, number, comment, choice=0):
		if self.canTrigger(signal, ID, subject, target, number, comment):
			if self.entity.Game.GUI:
				self.entity.Game.GUI.triggerBlink(self.entity)
			self.effect(signal, ID, subject, target, number, comment)
			
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		pass
		
	#一般只有需要额外定义ID的回合开始和结束扳机需要有自己的selfCopy函数
	def selfCopy(self, recipient):
		return type(self)(recipient)
		
	#这个扳机会在复制随从列表，手牌和牌库列表之前调用，扳机所涉及的随从，武器等会被复制
	#游戏会检查triggersonBoard中的每个(trig, signal),产生一个复制(trigCopy, signal)，并注册
	#这里负责处理产生一个trigCopy
	def createCopy(self, game):
		if self not in game.copiedObjs: #这个扳机没有被复制过
			entityCopy = self.entity.createCopy(game)
			trigCopy = self.selfCopy(entityCopy)
			if hasattr(self, "counter"): trigCopy.counter = self.counter
			game.copiedObjs[self] = trigCopy
			return trigCopy
		else: #一个扳机被复制过了，则其携带者也被复制过了
			return game.copiedObjs[self]
			
			
class TrigHand:
	def __init__(self, entity):
		self.blank_init(entity, [])
		
	def blank_init(self, entity, signals):
		self.entity, self.signals, self.temp = entity, signals, False
		
	def connect(self):
		for sig in self.signals:
			try: self.entity.Game.trigsHand[self.entity.ID][sig].append(self)
			except: self.entity.Game.trigsHand[self.entity.ID][sig] = [self]
			
	def disconnect(self):
		for sig in self.signals:
			try: self.entity.Game.trigsHand[self.entity.ID][sig].remove(self)
			except: pass
			
	def trigger(self, signal, ID, subject, target, number, comment, choice=0):
		if self.canTrigger(signal, ID, subject, target, number, comment):
			if self.entity.Game.GUI: self.entity.Game.GUI.triggerBlink(self.entity)
			self.effect(signal, ID, subject, target, number, comment)
			
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return True
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		pass
		
	def selfCopy(self, recipient):
		return type(self)(recipient)
		
	def createCopy(self, game):
		if self not in game.copiedObjs: #这个扳机没有被复制过
			entityCopy = self.entity.createCopy(game)
			trigCopy = type(self)(entityCopy)
			game.copiedObjs[self] = trigCopy
			return trigCopy
		else: #一个扳机被复制过了，则其携带者也被复制过了
			return game.copiedObjs[self]
			
			
class TrigDeck:
	def __init__(self, entity):
		self.blank_init(entity, [])
		
	def blank_init(self, entity, signals):
		self.entity, self.signals, self.temp = entity, signals, False
		
	def connect(self):
		for sig in self.signals:
			try: self.entity.Game.trigsDeck[self.entity.ID][sig].append(self)
			except: self.entity.Game.trigsDeck[self.entity.ID][sig] = [self]
			
	def disconnect(self):
		for sig in self.signals:
			try: self.entity.Game.trigsDeck[self.entity.ID][sig].remove(self)
			except: pass
			
	def trigger(self, signal, ID, subject, target, number, comment, choice=0):
		if self.canTrigger(signal, ID, subject, target, number, comment):
			self.effect(signal, ID, subject, target, number, comment)
			
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return True
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		pass
		
	def selfCopy(self, recipient):
		return type(self)(recipient)
		
	def createCopy(self, game):
		if self not in game.copiedObjs: #这个扳机没有被复制过
			entityCopy = self.entity.createCopy(game)
			trigCopy = type(self)(entityCopy)
			game.copiedObjs[self] = trigCopy
			return trigCopy
		else: #一个扳机被复制过了，则其携带者也被复制过了
			return game.copiedObjs[self]
			
			
"""Variants of TrigBoard, TrigHand, TrigDeck"""
class Deathrattle_Minion(TrigBoard):
	def __init__(self, entity):
		self.blank_init(entity)
		
	def blank_init(self, entity):
		self.entity = entity
		self.signals = ["MinionDies", "TrigDeathrattle"]
		
	def trigger(self, signal, ID, subject, target, number, comment, choice=0):
		minion, game = self.entity, self.entity.Game
		if game.status[minion.ID]["Deathrattle x2"] > 0:
			if self.canTrigger(signal, ID, subject, target, number, comment):
				if game.GUI: game.GUI.triggerBlink(minion, color="grey40")
				self.effect(signal, ID, subject, target, number, comment)
		if self.canTrigger(signal, ID, subject, target, number, comment):
			if game: game.GUI.triggerBlink(minion, color="grey40")
			self.effect(signal, ID, subject, target, number, comment)
		#随从通过死亡触发的亡语扳机需要在亡语触发之后注销。同样的，如果随从在亡语触发之后不在随从列表中了，如将随从洗回牌库，则同样要注销亡语
		#但是如果随从在由其他效果在场上触发的扳机，则这个亡语不会注销
		if signal[0] == 'M' or minion not in game.minions[minion.ID]:
			self.disconnect()
			
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return target == self.entity
		
		
class Deathrattle_Weapon(TrigBoard):
	def __init__(self, entity):
		self.blank_init(entity)
		
	def blank_init(self, entity):
		self.entity = entity
		self.signals = ["WeaponDestroyed"]
		
	def trigger(self, signal, ID, subject, target, number, comment, choice=0):
		weapon, game = self.entity, self.entity.Game
		if game.status[weapon.ID]["Weapon Deathrattle x2"] > 0:
			if self.canTrigger(signal, ID, subject, target, number, comment):
				if game.GUI: game.GUI.triggerBlink(weapon, color="grey40")
				self.effect(signal, ID, subject, target, number, comment)
		if self.canTrigger(signal, ID, subject, target, number, comment):
			if game.GUI: game.GUI.triggerBlink(weapon, color="grey40")
			self.effect(signal, ID, subject, target, number, comment)
		#目前没有触发武器亡语的效果，所以武器的亡语触发之后可以很安全地直接将其删除。
		self.disconnect()
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return target == self.entity
		
		
class SecretTrigger(TrigBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionBeenPlayed"])
		
	def blank_init(self, entity, signals):
		self.entity, self.signals = entity, signals
		
	def trigger(self, signal, ID, subject, target, number, comment, choice=0):
		secret, game = self.entity, self.entity.Game
		if game.status[secret.ID]["Secrets x2"] > 0:
			if self.canTrigger(signal, ID, subject, target, number, comment):
				if game.GUI: game.GUI.triggerBlink(secret)
				self.effect(signal, ID, subject, target, number, comment)
		if self.canTrigger(signal, ID, subject, target, number, comment):
			if game.GUI: game.GUI.triggerBlink(secret)
			self.effect(signal, ID, subject, target, number, comment)
		game.sendSignal("SecretRevealed", game.turn, secret, None, 0, "")
		self.disconnect()
		try:
			game.Secrets.secrets[secret.ID].remove(secret)
			print("Counterspell has been triggered and removed")
		except: pass
		
		
#这个扳机的目标：当随从在回合结束时有多个同类扳机，只会触发第一个，这个可以通过回合ID和自身ID是否符合来决定
class Trig_Borrow(TrigBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["TurnEnds"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		#只有当前要结束的回合的ID与自身ID相同的时候可以触发，于是即使有多个同类扳机也只有一个会触发。
		return self.entity.onBoard and ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self.entity.Game, "At the end of turn, temporarily controlled minion %s is returned to the other side."%self.entity.name)
		#Game的minionSwitchSide方法会自行移除所有的此类扳机。
		self.entity.Game.minionSwitchSide(self.entity, activity="Return")
		for trig in reversed(self.entity.trigsBoard):
			if isinstance(trig, Trig_Borrow):
				trig.disconnect()
				self.entity.trigsBoard.remove(trig)
				
				
class Trig_Echo(TrigHand):
	def __init__(self, entity):
		self.blank_init(entity, ["TurnEnds"])
		self.temp = True
		self.makesCardEvanescent = True
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.inHand #Echo disappearing should trigger at the end of any turn
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self.entity.Game, "At the end of turn, Echo card %s disappears."%self.entity.name)
		self.entity.Game.Hand_Deck.extractfromHand(self.entity)
		
		
class Trig_WorgenShift_FromHuman(TrigHand):
	def __init__(self, entity, worgenType):
		self.blank_init(entity, ["TurnEnds"])
		self.worgenType = worgenType
		self.makesCardEvanescent = True
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.inHand and ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self.entity.Game, "At the end of turn, %s transforms for into a worgen"%self.entity.name)
		worgen = self.worgenType(self.entity.Game, self.entity.ID)
		worgen.statReset(self.entity.health_max, self.entity.attack_Enchant)
		worgen.identity = self.entity.identity
		#狼人形态会复制人形态的场上扳机，但是目前没有给随从外加手牌和牌库扳机的机制。
		#目前不考虑狼人牌在变形前保有的临时攻击力buff
		worgen.trigsBoard = self.entity.trigsBoard
		self.entity.Game.Hand_Deck.replaceCardinHand(self.entity, worgen)
		
		
class Trig_WorgenShift_FromWorgen(TrigHand):
	def __init__(self, entity, humanType):
		self.blank_init(entity, ["TurnEnds"])
		self.humanType = humanType
		self.makesCardEvanescent = True
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.inHand and ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self.entity.Game, "At the end of turn, %s transforms for into a worgen"%self.entity.name)
		human = self.humanType(self.entity.Game, self.entity.ID)
		human.statReset(self.entity.health_max, self.entity.attack_Enchant)
		human.identity = self.entity.identity
		#狼人形态会复制人形态获得的场上扳机，但是目前没有给随从外加手牌和牌库扳机的机制。
		#目前不考虑狼人牌在变形前保有的临时攻击力buff
		human.trigsBoard = self.entity.trigsBoard
		self.entity.Game.Hand_Deck.replaceCardinHand(self.entity, human)
		
		
class QuestTrigger(TrigBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionBeenPlayed"])
		
	def blank_init(self, entity, signals):
		self.entity, self.signals = entity, signals
		self.accomplished = False
		self.counter = 0
		
	def trigger(self, signal, ID, subject, target, number, comment, choice=0):
		if self.canTrigger(signal, ID, subject, target, number, comment):
			if self.entity.Game.GUI: self.entity.Game.GUI.triggerBlink(self.entity)
			self.effect(signal, ID, subject, target, number, comment)
			
			
class BuffAura_Receiver:
	#Source is the Aura not the entity that creates the aura.
	def __init__(self, receiver, source, attGain, healthGain):
		self.source = source
		self.attGain = attGain #Positive by default.
		self.healthGain = healthGain
		self.receiver = receiver
		
	def effectStart(self):
		self.receiver.statChange(self.attGain, self.healthGain)
		self.receiver.statbyAura[0] += self.attGain
		self.receiver.statbyAura[1] += self.healthGain
		self.receiver.statbyAura[2].append(self)
		self.source.auraAffected.append((self.receiver, self))
		#PRINT(self.receiver, "Minion %s gains buffAura and its stat is %d/%d."%(self.receiver.name, self.receiver.attack, self.receiver.health))
	#Cleanse the aura_Receiver from the receiver and delete the (receiver, aura_Receiver) from source aura's list.
	def effectClear(self):
		self.receiver.statChange(-self.attGain, -self.healthGain)
		self.receiver.statbyAura[0] -= self.attGain
		self.receiver.statbyAura[1] -= self.healthGain
		extractfrom(self, self.receiver.statbyAura[2])
		extractfrom((self.receiver, self), self.source.auraAffected)
		#PRINT(self.receiver, "Minion %s loses buffAura and its stat is %d/%d."%(self.receiver.name, self.receiver.attack, self.receiver.health))
	#Invoke when the receiver is copied and because the aura_Dealer won't have reference to this copied receiver,
	#remove this copied aura_Receiver from copied receiver's statbyAura[2].
	def effectDiscard(self):
		self.receiver.statChange(-self.attGain, -self.healthGain)
		self.receiver.statbyAura[0] -= self.attGain
		self.receiver.statbyAura[1] -= self.healthGain
		extractfrom(self, self.receiver.statbyAura[2])
		#PRINT(self.receiver, "Minion %s loses buffAura and its stat is %d/%d."%(self.receiver.name, self.receiver.attack, self.receiver.health))
		
	def selfCopy(self, recipient): #The recipient of the aura is the same minion when copying it.
		#Source won't change.
		return type(self)(recipient, self.source, self.attGain, self.healthGain)
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
		for sig in self.signals:
			try: self.entity.Game.trigsBoard[self.entity.ID][sig].append(self)
			except: self.entity.Game.trigsBoard[self.entity.ID][sig] = [self]
			
	def auraDisappears(self):
		for minion, aura_Receiver in fixedList(self.auraAffected):
			aura_Receiver.effectClear()
			
		self.auraAffected = []
		for sig in self.signals:
			try: self.entity.Game.trigsBoard[self.entity.ID][sig].remove(self)
			except: pass
			
	#这个函数会在复制场上扳机列表的时候被调用。
	def createCopy(self, game):
		#一个光环的注册可能需要注册多个扳机
		if self not in game.copiedObjs: #这个光环没有被复制过
			entityCopy = self.entity.createCopy(game)
			Copy = self.selfCopy(entityCopy)
			game.copiedObjs[self] = Copy
			if hasattr(self, "keyWord"): #是关键字光环
				for minion, aura_Receiver in self.auraAffected:
					minionCopy = minion.createCopy(game)
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
					minionCopy = minion.createCopy(game)
					receiverIndex = minion.statbyAura[2].index(aura_Receiver)
					receiverCopy = minionCopy.statbyAura[2][receiverIndex]
					receiverCopy.source = Copy #补上这个receiver的source
					Copy.auraAffected.append((minionCopy, receiverCopy))
			return Copy
		else:
			return game.copiedObjs[self]
			
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
		for minion in self.entity.Game.neighbors2(self.entity)[0]:
			self.applies(minion)
			
	def applies(self, subject):
		if subject != self.entity:
			aura_Receiver = BuffAura_Receiver(subject, self, self.attack, self.health)
			aura_Receiver.effectStart()
			
	def auraAppears(self):
		game = self.entity.Game
		for minion in game.neighbors2(self.entity)[0]:
			self.applies(minion)
			
		#Only need to handle minions that appear. Them leaving/silenced will be handled by the BuffAura_Receiver object.
		for sig in self.signals: #随从离场时会自己清除自己的光环
			try: game.trigsBoard[self.entity.ID][sig].append(self)
			except: game.trigsBoard[self.entity.ID][sig] = [self]
			
	def selfCopy(self, recipient): #The recipient is the minion that deals the Aura.
		return type(self)(recipient, self.attack, self.health)
	#可以通过AuraDealer_toMinion的createCopy方法复制
	
	
class BuffAura_Dealer_All(AuraDealer_toMinion):
	def __init__(self, entity, attack, health):
		self.entity = entity
		self.attack, self.health = attack, health
		self.signals, self.auraAffected = ["MinionAppears"], []
		
	#All minions appearing on the same side will be subject to the buffAura.
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject.ID == self.entity.ID and subject != self.entity and self.applicable(subject)
		
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
			if self.entity.activated == False and self.entity.health < self.entity.health_max:
				self.entity.activated = True
				BuffAura_Receiver(self.entity, self, self.attack, 0).effectStart()
			elif self.entity.activated and self.entity.health >= self.entity.health_max:
				self.entity.activated = False
				for entity, aura_Receiver in fixedList(self.auraAffected):
					aura_Receiver.effectClear()
					
	def selfCopy(self, recipient): #The recipientMinion is the entity that deals the Aura.
		#func that checks if subject is applicable will be the new copy's function
		return type(self)(recipient, self.attack)
	#激怒的光环仍然可以通过AuraDealer_toMinion的createCopy复制
	
#战歌指挥官的光环相对普通的buff光环更特殊，因为会涉及到随从获得和失去光环的情况
class WarsongCommander_Aura(AuraDealer_toMinion):
	def __init__(self, entity):
		self.entity = entity
		self.signals, self.auraAffected = ["MinionAppears", "MinionChargeChanged"], []
		
	#All minions appearing on the same side will be subject to the buffAura.
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		#注意，战歌指挥官的光环可以作用在自己身上，这点区分于其他所有身材buff型光环。
		#随从只要发生了冲锋状态的变化就要调用战歌指挥官的Aura_Dealer，如果冲锋状态失去，则由该光环来移除其buff状态
		return self.entity.onBoard and subject.ID == self.entity.ID and ((signal == "MinionAppears" and subject.keyWords["Charge"] > 0) or signal == "MinionChargeChanged")
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.applies(signal, subject)
		
	def applies(self, signal, subject):
		if signal == "MinionAppears":
			if subject.keyWords["Charge"] > 0:
				aura_Receiver = BuffAura_Receiver(subject, self, 1, 0)
				aura_Receiver.effectStart()
		else: #signal == "MinionChargeChanged"
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
			
		for sig in self.signals:
			try: self.entity.Game.trigsBoard[self.entity.ID][sig].remove(self)
			except: pass
			
	def selfCopy(self, recipient):
		return type(self)(recipient)
	#可以通过AuraDealer_toMinion的createCopy方法复制
	
class HasAura_Receiver:
	def __init__(self, receiver, source, keyWord):
		self.source = source #The aura.
		self.receiver = receiver
		self.keyWord = keyWord
		
	def effectStart(self):
		try: self.receiver.keyWordbyAura[self.keyWord] += 1
		except: self.receiver.keyWordbyAura[self.keyWord] = 1
		self.receiver.getsKeyword(self.keyWord)
		self.receiver.keyWordbyAura["Auras"].append(self)
		self.source.auraAffected.append((self.receiver, self))
		
	#The aura on the receiver is cleared and the source will remove this receiver and aura_Receiver from it's list.
	def effectClear(self):
		if self.receiver.keyWordbyAura[self.keyWord] > 0:
			self.receiver.keyWordbyAura[self.keyWord] -= 1
		self.receiver.losesKeyword(self.keyWord)
		try: self.receiver.keyWordbyAura["Auras"].remove(self)
		except: pass
		try: self.source.auraAffected.remove((self.receiver, self))
		except: pass
		
	#After a receiver is deep copied, it will also copy this aura_Receiver, simply remove it.
	#The aura_Dealer won't have reference to this copied aura.
	def effectDiscard(self):
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
		return self.entity.onBoard and subject.ID == self.entity.ID and subject != self.entity and self.applicable(subject)
		
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
		PRINT(self.entity.Game, "Dr. Boom. Mad Genius' aura starts it's effect.")
		for minion in self.Game.minionsonBoard(self.ID):
			self.applies(minion)
			
		try: self.entity.Game.trigsBoard[self.ID]["MinionAppears"].append(self)
		except: self.entity.Game.trigsBoard[self.ID]["MinionAppears"] = [self]
		
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
		try: self.receiver.statbyAura[1].remove(self)
		except: pass
		try: self.source.auraAffected.remove((self.receiver, self))
		except: pass
	#Invoke when the receiver is copied and because the aura_Dealer won't have reference to this copied receiver,
	#remove this copied aura_Receiver from copied receiver's statbyAura[2].
	def effectDiscard(self):
		self.receiver.gainStat(-2, 0)
		self.receiver.statbyAura[0] -= 2
		try: self.receiver.statbyAura[1].remove(self)
		except: pass
		
	def selfCopy(self, recipient):
		return type(self)(recipient, self.source)
	#武器的本体复制一定优先，其复制过程中会自行创建没有source的receiver，receiver自己没有必要创建createCopy方法
	
	
	
class ManaMod:
	def __init__(self, card, changeby=0, changeto=-1, source=None, lowerbound=0):
		self.card = card
		self.changeby, self.changeto, self.lowerbound = changeby, changeto, lowerbound
		self.source = source
		
	def handleMana(self):
		if self.changeby:
			self.card.mana += self.changeby
			self.card.mana = max(self.lowerbound, self.card.mana) #用于召唤传送门的随从减费不小于1的限制。
		elif self.changeto >= 0: self.card.mana = self.changeto
			
	def applies(self):
		self.card.manaMods.append(self) #需要让卡牌自己也带有一个检测的光环，离开手牌或者牌库中需要清除。
		if self.card in self.card.Game.Hand_Deck.hands[self.card.ID] or self.card in self.card.Game.Hand_Deck.decks[self.card.ID]:
			self.card.Game.Manas.calcMana_Single(self.card)
			
	def getsRemoved(self):
		try: self.card.manaMods.remove(self)
		except: pass
		if self.source:
			try: self.source.auraAffected.remove((self.card, self))
			except: pass
			
	def selfCopy(self, recipient):
		return ManaMod(recipient, self.changeby, self.changeto, self.source, self.lowerbound)
		
#既可以用于随从发出的费用光环，也可用于不寄存在随从实体上的暂时费用光环，如伺机待发等。
#随从发出的光环由随从自己控制光环的开关。
#不寄存于随从身上的光环一般用于一次性的费用结算。而洛欧塞布等持续一个回合的光环没有任何扳机而已
#永久费用光环另行定义
class ManaAura_Dealer:
	def __init__(self, entity, changeby=0, changeto=-1, lowerbound=0):
		self.blank_init(entity, changeby, changeto, lowerbound)
		
	def blank_init(self, entity, changeby, changeto, lowerbound):
		self.entity = entity
		self.changeby, self.changeto, self.lowerbound = changeby, changeto, lowerbound
		self.auraAffected = [] #A list of (card, aura_Receiver)
		
	def manaAuraApplicable(self, target):
		return self.entity.manaAuraApplicable(target)
		
	#只要是有满足条件的卡牌进入手牌，就会触发这个光环。target是承载这个牌的列表。
	#applicable不需要询问一张牌是否在手牌中。光环只会处理在手牌中的卡牌
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and self.manaAuraApplicable(target[0])
		
	def trigger(self, signal, ID, subject, target, number, comment, choice=0):
		if self.canTrigger(signal, ID, subject, target, number, comment):
			self.effect(signal, ID, subject, target, number, comment)
			
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.applies(target[0])
		
	def applies(self, target): #This target is NOT holder.
		if self.manaAuraApplicable(target):
			PRINT(self.entity.Game, "Card %s gains the Changeby %d/Changeto %d mana change from %s"%(target.name, self.changeby, self.changeto, self.entity.name))
			manaMod = ManaMod(target, self.changeby, self.changeto, self, self.lowerbound)
			manaMod.applies()
			self.auraAffected.append((target, manaMod))
			
	def auraAppears(self):
		game = self.entity.Game
		PRINT(game, "{} appears and starts its mana aura {}".format(self.entity.name, self))
		for card in game.Hand_Deck.hands[1]: self.applies(card)
		for card in game.Hand_Deck.hands[2]: self.applies(card)
		
		try: game.trigsBoard[self.entity.ID]["CardEntersHand"].append(self)
		except: game.trigsBoard[self.entity.ID]["CardEntersHand"] = [self]
		game.Manas.calcMana_All()
		
	#When the aura object is no longer referenced, it vanishes automatically.
	def auraDisappears(self):
		minion = self.entity
		PRINT(minion.Game, "%s removes its effect."%minion.name)
		for card, manaMod in fixedList(self.auraAffected):
			manaMod.getsRemoved()
			
		self.auraAffected = []
		try: minion.Game.trigsBoard[minion.ID]["CardEntersHand"].remove(self)
		except: pass
		minion.Game.Manas.calcMana_All()
		
	def selfCopy(self, recipient): #The recipient is the entity that deals the Aura.
		return type(self)(recipient, self.changeby, self.changeto, self.lowerbound)
		
	#可以在复制场上扳机列表的时候被调用
	#可以调用这个函数的时候，一定是因为要复制一个随从的费用光环，那个随从的复制已经创建完毕，可以在复制字典中查到
	def createCopy(self, game):
		if self not in game.copiedObjs:
			entityCopy = self.entity.createCopy(game)
			Copy = self.selfCopy(entityCopy)
			game.copiedObjs[self] = Copy
			for card, manaMod in self.auraAffected: #从自己的auraAffected里面复制内容出去
				cardCopy = card.createCopy(game)
				#重点是复制一个随从是，它自己会携带一个费用改变，这个费用改变怎么追踪到
				manaModIndex = card.manaMods.index(manaMod)
				manaModCopy = cardCopy.manaMods[manaModIndex]
				manaModCopy.source = Copy #在处理函数之前，所有的费用状态都已经被一次性复制完毕，它们的来源被迫留为None,需要在这里补上
				Copy.auraAffected.append((cardCopy, manaModCopy))
			return Copy
		else:
			return game.copiedObjs[self]
			
			
class TempManaEffect:
	def __init__(self, Game, ID, changeby=0, changeto=-1):
		self.Game, self.ID = Game, ID
		self.changeby, self.changeto = changeby, changeto
		self.temporary = True
		self.auraAffected = []
		
	def applicable(self, target):
		return True
	#signal有"CardEntersHand"和"ManaPaid",只要它们满足applicable就可以触发。
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
		else: #signal == "ManaPaid"
			self.auraDisappears()
			
	def applies(self, subject):
		if self.applicable(subject):
			manaMod = ManaMod(subject, self.changeby, self.changeto, self)
			manaMod.applies()
			self.auraAffected.append((subject, manaMod))
			
	def auraAppears(self):
		game = self.Game
		for card in game.Hand_Deck.hands[1]: self.applies(card)
		for card in game.Hand_Deck.hands[2]: self.applies(card)
		
		try: game.trigsBoard[self.ID]["CardEntersHand"].append(self)
		except: game.trigsBoard[self.ID]["CardEntersHand"] = [self]
		try: game.trigsBoard[self.ID]["ManaPaid"].append(self)
		except: game.trigsBoard[self.ID]["ManaPaid"] = [self]
		game.Manas.calcMana_All()
		
	def auraDisappears(self):
		for minion, manaMod in fixedList(self.auraAffected):
			manaMod.getsRemoved()
		self.auraAffected = []
		try: self.Game.Manas.CardAuras.remove(self)
		except: pass
		try: self.Game.trigsBoard[self.ID]["CardEntersHand"].remove(self)
		except: pass
		try: self.Game.trigsBoard[self.ID]["ManaPaid"].remove(self)
		except: pass
		self.Game.Manas.calcMana_All()
		
	def selfCopy(self, game):
		return type(self)(game, self.ID, self.changeby, self.changeto)
		
	def createCopy(self, game): #The recipient is the Game that handles the Aura.
		if self not in game.copiedObjs:
			Copy = self.selfCopy(game)
			game.copiedObjs[self] = Copy
			for card, manaMod in self.auraAffected:
				cardCopy = card.createCopy(game)
				manaModIndex = card.manaMods.index(manaMod)
				manaModCopy = cardCopy.manaMods[manaModIndex]
				manaModCopy.source = Copy
				Copy.auraAffected.append((cardCopy, manaModCopy))
			return Copy
		else:
			return game.copiedObjs[self]
			
			
class TempManaEffect_Power:
	def __init__(self, Game, ID, changeby=0, changeto=-1):
		self.Game, self.ID = Game, ID
		self.changeby, self.changeto = changeby, changeto
		self.temporary = True
		self.auraAffected = []
		
	def applicable(self, target):
		return True
	#signal有"CardEntersHand"和"ManaPaid",只要它们满足applicable就可以触发。
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.applicable(subject) #Hero Power的出现是不传递holder而是直接传递subject
		
	def trigger(self, signal, ID, subject, target, number, comment, choice=0):
		if self.canTrigger(signal, ID, subject, target, number, comment):
			self.effect(signal, ID, subject, target, number, comment)
			
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		if signal == "HeroPowerAcquired":
			self.applies(subject)
		elif subject == self.Game.powers[self.ID]:
			self.auraDisappears()
			
	def applies(self, subject):
		if self.applicable(subject):
			manaMod = ManaMod(subject, self.changeby, self.changeto, self)
			manaMod.applies()
			self.auraAffected.append((subject, manaMod))
			
	def auraAppears(self):
		game = self.Game
		self.applies(game.powers[1])
		self.applies(game.powers[2])
		try: game.trigsBoard[self.ID]["HeroPowerAcquired"].append(self)
		except: game.trigsBoard[self.ID]["HeroPowerAcquired"] = [self]
		try: game.trigsBoard[self.ID]["ManaPaid"].append(self)
		except: game.trigsBoard[self.ID]["ManaPaid"] = [self]
		self.Game.Manas.calcMana_Powers()
		
	def auraDisappears(self):
		for minion, manaMod in fixedList(self.auraAffected):
			manaMod.getsRemoved()
		self.auraAffected = []
		try: self.Game.Manas.PowerAuras.remove(self)
		except: pass
		try: self.Game.trigsBoard[self.ID]["HeroPowerAcquired"].remove(self)
		except: pass
		try: self.Game.trigsBoard[self.ID]["ManaPaid"].remove(self)
		except: pass
		self.Game.Manas.calcMana_Powers()
		
	def selfCopy(self, game):
		return type(self)(game, self.ID, self.changeby, self.changeto)
		
	def createCopy(self, game): #The recipient is the Game that handles the Aura.
		if self not in game.copiedObjs:
			Copy = self.selfCopy(game)
			game.copiedObjs[self] = Copy
			for heroPower, manaMod in self.auraAffected:
				heroPowerCopy = heroPower.createCopy(game)
				manaModIndex = heroPower.manaMods.index(manaMod)
				manaModCopy = heroPowerCopy.manaMods[manaModIndex]
				manaModCopy.source = Copy
				Copy.auraAffected.append((heroPowerCopy, manaModCopy))
			return Copy
		else:
			return game.copiedObjs[self]
			