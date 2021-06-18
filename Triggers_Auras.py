#对于随从的场上扳机，其被复制的时候所有暂时和非暂时的扳机都会被复制。
#但是随从返回其额外效果的时候，只有其非暂时场上扳机才会被返回（永恒祭司），暂时扳机需要舍弃。
class TrigBoard:
	def __init__(self, entity, signals):
		self.entity, self.signals = entity, signals
		self.inherent, self.changesCard, self.nextAnimWaits = True, False, False
		self.counter = -1
		
	def connect(self):
		game, ID = self.entity.Game, self.entity.ID
		for sig in self.signals:
			try: game.trigsBoard[ID][sig].append(self)
			except: game.trigsBoard[ID][sig] = [self]
			
	def disconnect(self):
		game, ID = self.entity.Game, self.entity.ID
		for sig in self.signals:
			try: game.trigsBoard[ID][sig].remove(self)
			except: pass
			
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return True
		
	def trig(self, signal, ID, subject, target, number, comment, choice=0):
		if self.canTrig(signal, ID, subject, target, number, comment):
			btn, GUI = self.entity.btn, self.entity.Game.GUI
			if btn and "Trigger" in btn.icons:
				icon = btn.icons["Trigger"]
				if self.nextAnimWaits: GUI.seqHolder[-1].append(GUI.PARALLEL(GUI.FUNC(icon.trigAni), GUI.WAIT(1.5)))
				else: GUI.seqHolder[-1].append(GUI.FUNC(icon.trigAni))
				
			self.effect(signal, ID, subject, target, number, comment)
			
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		pass
		
	def text(self, CHN):
		return ''
		
	def rngPool(self, identifier):
		pool = self.entity.Game.RNGPools[identifier]
		try: pool.remove(type(self.entity))
		except: pass
		return pool
		
	#一般只有需要额外定义ID的回合开始和结束扳机需要有自己的selfCopy函数
	def selfCopy(self, recipient):
		return type(self)(recipient)
		
	#这个扳机会在复制随从列表，手牌和牌库列表之前调用，扳机所涉及的随从，武器等会被复制
	#游戏会检查trigsBoard中的每个(trig, signal),产生一个复制(trigCopy, signal)，并注册
	#这里负责处理产生一个trigCopy
	def createCopy(self, game):
		if self not in game.copiedObjs: #这个扳机没有被复制过
			entityCopy = self.entity.createCopy(game)
			trigCopy = self.selfCopy(entityCopy)
			trigCopy.counter = self.counter
			game.copiedObjs[self] = trigCopy
			return trigCopy
		else: #一个扳机被复制过了，则其携带者也被复制过了
			return game.copiedObjs[self]
			
			
class TrigHand:
	def __init__(self, entity, signals):
		self.entity, self.signals, self.inherent = entity, signals, True
		self.inherent, self.changesCard, self.nextAnimWaits = True, False, False
		self.counter = -1
		
	def connect(self):
		for sig in self.signals:
			try: self.entity.Game.trigsHand[self.entity.ID][sig].append(self)
			except: self.entity.Game.trigsHand[self.entity.ID][sig] = [self]
			
	def disconnect(self):
		for sig in self.signals:
			try: self.entity.Game.trigsHand[self.entity.ID][sig].remove(self)
			except: pass
			
	def trig(self, signal, ID, subject, target, number, comment, choice=0):
		if self.canTrig(signal, ID, subject, target, number, comment):
			if self.entity.Game.GUI: self.entity.Game.GUI.trigBlink(self.entity)
			self.effect(signal, ID, subject, target, number, comment)
			
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return True
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		pass
		
	def text(self, CHN):
		return ''
		
	def rngPool(self, identifier):
		pool = self.entity.Game.RNGPools[identifier]
		try: pool.remove(type(self.entity))
		except: pass
		return pool
		
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
	def __init__(self, entity, signals):
		self.entity, self.signals, self.inherent = entity, signals, True
		self.counter = 0
		
	def connect(self):
		for sig in self.signals:
			try: self.entity.Game.trigsDeck[self.entity.ID][sig].append(self)
			except: self.entity.Game.trigsDeck[self.entity.ID][sig] = [self]
			
	def disconnect(self):
		for sig in self.signals:
			try: self.entity.Game.trigsDeck[self.entity.ID][sig].remove(self)
			except: pass
			
	def trig(self, signal, ID, subject, target, number, comment, choice=0):
		if self.canTrig(signal, ID, subject, target, number, comment):
			self.effect(signal, ID, subject, target, number, comment)
			
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return True
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		pass
		
	def text(self, CHN):
		return ''
		
	def rngPool(self, identifier):
		pool = self.entity.Game.RNGPools[identifier]
		try: pool.remove(type(self.entity))
		except: pass
		return pool
		
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
		self.entity, self.signals = entity, ["MinionDies", "TrigDeathrattle"]
		self.inherent = True
		
	def trig(self, signal, ID, subject, target, number, comment, choice=0):
		minion, game = self.entity, self.entity.Game
		if game.status[minion.ID]["Deathrattle x2"] > 0:
			if self.canTrig(signal, ID, subject, target, number, comment):
				if game.GUI: game.GUI.deathrattleAni(minion, color="grey40")
				self.effect(signal, ID, subject, target, number, comment)
		if self.canTrig(signal, ID, subject, target, number, comment):
			if game: game.GUI.deathrattleAni(minion, color="grey40")
			self.effect(signal, ID, subject, target, number, comment)
		#随从通过死亡触发的亡语扳机需要在亡语触发之后注销。同样的，如果随从在亡语触发之后不在随从列表中了，如将随从洗回牌库，则同样要注销亡语
		#但是如果随从在由其他效果在场上触发的扳机，则这个亡语不会注销
		if signal[0] == 'M' or minion not in game.minions[minion.ID]:
			self.disconnect()
			
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.Game.status[self.entity.ID]["Deathrattle X"] < 1 and target == self.entity
		
		
class Deathrattle_Weapon(TrigBoard):
	def __init__(self, entity):
		self.entity, self.signals = entity, ["WeaponDestroyed"]
		self.inherent = True
		
	def trig(self, signal, ID, subject, target, number, comment, choice=0):
		weapon, game = self.entity, self.entity.Game
		if game.status[weapon.ID]["Weapon Deathrattle x2"] > 0:
			if self.canTrig(signal, ID, subject, target, number, comment):
				if game.GUI: game.GUI.deathrattleAni(weapon, color="grey40")
				self.effect(signal, ID, subject, target, number, comment)
		if self.canTrig(signal, ID, subject, target, number, comment):
			if game.GUI: game.GUI.deathrattleAni(weapon, color="grey40")
			self.effect(signal, ID, subject, target, number, comment)
		#目前没有触发武器亡语的效果，所以武器的亡语触发之后可以很安全地直接将其删除。
		self.disconnect()
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.Game.status[self.entity.ID]["Deathrattle X"] < 1 and target == self.entity
		
		
class SecretTrigger(TrigBoard):
	def __init__(self, entity, signals):
		super().__init__(entity, signals)
		self.dummy, self.realSecret = False, None
		
	#伪扳机的注册直接在Secrets.initSecretHint里面处理完毕
	def connect(self):
		secret = self.entity
		game, ID = secret.Game, secret.ID
		for sig in self.signals:
			try: game.trigsBoard[ID][sig].append(self)
			except: game.trigsBoard[ID][sig] = [self]
			
	#目前所有奥秘离开奥秘区的时候都标明其是什么奥秘，所以可以用于排除其他奥秘的可能性
	def disconnect(self):
		game, ID = self.entity.Game, self.entity.ID
		for sig in self.signals:
			try: game.trigsBoard[ID][sig].remove(self)
			except: pass
		#if self.dummy:
		#	self.realSecret.dummyTrigs.remove(self)
		#	#game.trigAuras[ID].remove(self)
		#else:
		#	game.Hand_Deck.ruleOut(self.entity, fromHD=1) #只从资源中进行移除
			
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return True
		
	#当一个伪扳机可以被触发并开始结算的时候，它会把自己直接移除，同时去除掉这个可能性
	#例如：召唤了一个随从，有两个奥秘：第一个可能是狙击或者寒冰护体，但是实际上是爆炸符文；第二个可能是狙击，但是实际上是冰冻陷阱
		#在结算中，狙击的伪扳机被触发了，需要移除第一个奥秘是狙击的可能性，而寒冰护体的伪扳机无法触发，暂时还不能排除其可能性。
			#真实的爆炸符文触发了，把随从打到了负血
			#第二个奥秘的狙击伪扳机无法再发动了，因为随从已经是负血，所以我们无法得知那个奥秘是不是真的狙击，所以第二个奥秘的可能性是没有变化的
	def trig(self, signal, ID, subject, target, number, comment, choice=0):
		secret, game = self.entity, self.entity.Game
		self.disconnect() #Handles removing dummy, too.
		#if self.dummy: #伪扳机能被触发的时候，需要移除可能性
		#	#上面已经把这个伪扳机从trigsBoard和trigAuras里面移除了，下面就是把它所用来服务的那个真正的奥秘的可能范围缩小
		#	self.realSecret.possi.remove(type(secret))
		#	game.Hand_Deck.ruleOut(secret, fromHD=2)
		#else: #如果这个扳机是真奥秘的扳机时，它触发时需要把其从对方的资源中移除
		try: game.Secrets.secrets[secret.ID].remove(secret)
		except: pass
		if game.status[secret.ID]["Secrets x2"] > 0:
			if self.canTrig(signal, ID, subject, target, number, comment):
				if game.GUI: game.GUI.secretTrigAni(secret)
				self.effect(signal, ID, subject, target, number, comment)
		if self.canTrig(signal, ID, subject, target, number, comment):
			if game.GUI: game.GUI.secretTrigAni(secret)
			self.effect(signal, ID, subject, target, number, comment)
		game.sendSignal("SecretRevealed", game.turn, secret, None, 0, "")
		game.Counters.numSecretsTriggeredThisGame[secret.ID] += 1
		#secret.realSecretReveal()
			
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		pass
		
	def text(self, CHN):
		return ''
		
	def rngPool(self, identifier):
		pool = self.entity.Game.RNGPools[identifier]
		try: pool.remove(type(self.entity))
		except: pass
		return pool
		
	def selfCopy(self, recipient):
		return type(self)(recipient)
		
	def createCopy(self, game):
		if self not in game.copiedObjs: #这个扳机没有被复制过
			entityCopy = self.entity.createCopy(game)
			trigCopy = self.selfCopy(entityCopy)
			trigCopy.dummy = self.dummy
			if self.realSecret:
				trigCopy.realSecret = self.realSecret.createCopy(game)
			game.copiedObjs[self] = trigCopy
			return trigCopy
		else: #一个扳机被复制过了，则其携带者也被复制过了
			return game.copiedObjs[self]
			
#这个扳机的目标：当随从在回合结束时有多个同类扳机，只会触发第一个，这个可以通过回合ID和自身ID是否符合来决定
class Trig_Borrow(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["TurnEnds"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		#只有当前要结束的回合的ID与自身ID相同的时候可以触发，于是即使有多个同类扳机也只有一个会触发。
		return self.entity.onBoard and ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		#Game的minionSwitchSide方法会自行移除所有的此类扳机。
		self.entity.Game.minionSwitchSide(self.entity, activity="Return")
		for trig in reversed(self.entity.trigsBoard):
			if isinstance(trig, Trig_Borrow):
				trig.disconnect()
				self.entity.trigsBoard.remove(trig)
				
				
class Trig_Echo(TrigHand):
	def __init__(self, entity):
		super().__init__(entity, ["TurnEnds"])
		self.changesCard = True
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.inHand #Echo disappearing should trigger at the end of any turn
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.Game.Hand_Deck.extractfromHand(self.entity)
		
		
class Trig_Corrupt(TrigHand):
	def __init__(self, entity, corruptedType):
		super().__init__(entity, ["ManaPaid"])
		self.corruptedType = corruptedType
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.inHand and ID == self.entity.ID and number > self.entity.mana and subject.type != "Power"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		card = self.entity
		newCard = self.corruptedType(card.Game, card.ID)
		try:
			#Buff and mana effects, etc, will be preserved
			#Buff to cards in hand will always be permanent or temporary, not from Auras
			if newCard.type == "Minion":
				#Temporary attack changes on minions are NOT included in attack_Enchant
				attBuff, healthBuff = card.attack_Enchant - card.attack_0, card.health_max - card.health_0
				newCard.buffDebuff(attBuff, healthBuff)
				for attGain, attRevertTime in card.tempAttChanges:
					newCard.buffDebuff(attGain, 0, attRevertTime)
				#There are no Corrupted cards with predefined Deathrattles, and given Deathrattles are very simple
				newCard.deathrattles = [type(deathrattle)(newCard) for deathrattle in card.deathrattles]
			elif newCard.type == "Weapon": #Only applicable to Felsteel Executioner
				attBuff, healthBuff = card.attack_Enchant - card.attack_0, card.health_max - card.health_0
				#Assume temporary attack changes applied on a minion won't carry over to the weapon
				newCard.gainStat(attBuff, healthBuff)
			#Keep the keywords and marks consistent
			for key, value in newCard.keyWords.items(): #Find keywords the new card doesn't have
				if value < 1 and card.keyWords[key] > 0: newCard.keyWords[key] = 1
			for key, value in newCard.marks.items():
				try:
					if value < 1 and card.marks[key] > 0: newCard.marks[key] = 1
				except: pass
			#Inhand triggers and mana modifications
			newCard.trigsHand += [trig for trig in card.trigsHand if not isinstance(trig, Trig_Corrupt)]
			newCard.manaMods = [manaMod.selfCopy(newCard) for manaMod in card.manaMods]
		except Exception as e:
			print(e, card, newCard)
		card.Game.Hand_Deck.replaceCardinHand(card, newCard)
		
	def selfCopy(self, recipient):
		return type(self)(recipient, self.corruptedType)
		
	def createCopy(self, game):
		if self not in game.copiedObjs: #这个扳机没有被复制过
			entityCopy = self.entity.createCopy(game)
			trigCopy = type(self)(entityCopy, self.corruptedType)
			game.copiedObjs[self] = trigCopy
			return trigCopy
		else: #一个扳机被复制过了，则其携带者也被复制过了
			return game.copiedObjs[self]
			
			
class Trig_DieatEndofTurn(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["TurnEnds"])
		self.inherent = False
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard #Even if the current turn is not the minion's owner's turn
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.Game.killMinion(None, self.entity)
		
		
class QuestTrigger(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["MinionBeenPlayed"])
		self.counter, self.accomplished = 0, False
		
	def trig(self, signal, ID, subject, target, number, comment, choice=0):
		if self.canTrig(signal, ID, subject, target, number, comment):
			if self.entity.Game.GUI: self.entity.Game.GUI.trigBlink(self.entity)
			self.effect(signal, ID, subject, target, number, comment)
			
			
			
"""Auras"""
class HasAura_toMinion:
	def __init__(self):
		self.entity = None
		
	def applicable(self, target):
		return self.entity.applicable(target)
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return True
	
	def trig(self, signal, ID, subject, target, number, comment, choice=0):
		if self.canTrig(signal, ID, subject, target, number, comment):
			self.effect(signal, ID, subject, target, number, comment)
			
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.applies(subject)
		
	def auraAppears(self):
		for minion in self.entity.Game.minionsonBoard(self.entity.ID):
			self.applies(minion)
		#Only need to handle minions that appear. Them leaving/silenced will be handled by the Stat_Receiver object.
		for sig in self.signals:
			try: self.entity.Game.trigsBoard[self.entity.ID][sig].append(self)
			except: self.entity.Game.trigsBoard[self.entity.ID][sig] = [self]
			
	def auraDisappears(self):
		for minion, receiver in self.auraAffected[:]:
			receiver.effectClear()
		self.auraAffected = []
		for sig in self.signals:
			try: self.entity.Game.trigsBoard[self.entity.ID][sig].remove(self)
			except: pass
			
	def selfCopy(self, recipient):
		return type(self)()
	
	#这个函数会在复制场上扳机列表的时候被调用。
	def createCopy(self, game):
		#一个光环的注册可能需要注册多个扳机
		if self not in game.copiedObjs: #这个光环没有被复制过
			entityCopy = self.entity.createCopy(game)
			Copy = self.selfCopy(entityCopy)
			game.copiedObjs[self] = Copy
			#复制一个随从的时候已经复制了其携带的光环buff状态receiver
			#这里只需要找到那个receiver的位置即可
			##注意一个随从在复制的时候需要把它的Stat_Receiver，keyWordAura_Reciever和manaMods一次性全部复制之后才能进行光环发出者的复制
			#相应地，这些光环receiver的来源全部被标为None，需要在之后处理它们的来源时一一补齐
			for minion, receiver in self.auraAffected:
				minionCopy = minion.createCopy(game)
				index = minion.auraReceivers.index(receiver)
				receiverCopy = minionCopy.auraReceivers[index]
				receiverCopy.source = Copy #补上这个receiver的source
				Copy.auraAffected.append((minionCopy, receiverCopy))
			return Copy
		else:
			return game.copiedObjs[self]
			
class Stat_Receiver:
	#Source is the Aura not the entity that creates the aura.
	def __init__(self, recipient, source, attGain, healthGain=0):
		self.source = source
		self.attGain = attGain #Positive by default.
		self.healthGain = healthGain
		self.recipient = recipient
		
	def effectStart(self):
		obj = self.recipient
		if obj.type == "Minion":
			obj.statChange(self.attGain, self.healthGain)
			obj.healthfromAura += self.healthGain
		elif obj.type == "Hero":
			obj.gainAttack(self.attGain, '')
		else: #For weapon
			obj.gainStat(self.attGain, 0)
		obj.attfromAura += self.attGain
		obj.auraReceivers.append(self)
		self.source.auraAffected.append((obj, self))
	#Cleanse the receiver from the receiver and delete the (receiver, receiver) from source aura's list.
	def effectClear(self):
		obj = self.recipient
		if obj.type == "Minion":
			obj.statChange(-self.attGain, -self.healthGain)
			obj.healthfromAura -= self.healthGain
		elif obj.type == "Hero":
			obj.gainAttack(-self.attGain, '')
		else:
			obj.gainStat(-self.attGain, 0)
		obj.attfromAura -= self.attGain
		try: obj.auraReceivers.remove(self)
		except: pass
		try: self.source.auraAffected.remove((obj, self))
		except: pass
	#Invoke when the affected minion is copied and because the aura_Dealer won't have reference to this copied receiver,
	#remove this copied receiver from copied receiver's auraReceivers.
	#Only minion selfCopy will invoke this
	def effectDiscard(self):
		obj = self.recipient
		if obj.type == "Minion":
			obj.statChange(-self.attGain, -self.healthGain)
			obj.healthfromAura -= self.healthGain
		elif obj.type == "Weapon":
			obj.gainStat(-self.attGain, 0)
		obj.attfromAura -= self.attGain
		try: obj.auraReceivers.remove(self)
		except: pass
		
	def selfCopy(self, recipient): #The recipient of the aura is the same minion when copying it.
		#Source won't change.
		return type(self)(recipient, self.source, self.attGain, self.healthGain)
	#receiver一定是附属于一个随从的，在复制游戏的过程中，优先会createCopy光环本体，之后是光环影响的随从，
	#随从createCopy过程中会复制出没有source的receiver，所以receiver本身没有必要有createCopy
	
	
class StatAura_Others(HasAura_toMinion):
	def __init__(self, entity, attack, health):
		self.entity = entity
		self.attack, self.health = attack, health
		self.signals, self.auraAffected = ["MinionAppears"], []
		
	#All minions appearing on the same side will be subject to the buffAura.
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject.ID == self.entity.ID and subject != self.entity and self.applicable(subject)
		
	def applies(self, subject):
		if self.applicable(subject) and subject != self.entity:
			Stat_Receiver(subject, self, self.attack, self.health).effectStart()
			
	def selfCopy(self, recipient): #The recipient is the entity that deals the Aura.
		#func that checks if subject is applicable will be the new copy's function
		return type(self)(recipient, self.attack, self.health)
		
		
#def __init__(self, minion, func, attack, health):
class StatAura_Adjacent(HasAura_toMinion):
	def __init__(self, entity, attack, health):
		self.entity = entity
		self.attack, self.health = attack, health
		self.signals, self.auraAffected = ["MinionAppears", "MinionDisappears"], []
	#Minions appearing/disappearing will let the minion reevaluate the aura.
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		#重置对于两侧随从的光环
		for minion, receiver in self.auraAffected[:]:
			receiver.effectClear()
		#Find adjacent minions to self.entity, then try to register them.
		for minion in self.entity.Game.neighbors2(self.entity)[0]:
			self.applies(minion)
			
	def applies(self, subject):
		if subject != self.entity:
			Stat_Receiver(subject, self, self.attack, self.health).effectStart()
			
	def auraAppears(self):
		game = self.entity.Game
		for minion in game.neighbors2(self.entity)[0]:
			self.applies(minion)
			
		#Only need to handle minions that appear. Them leaving/silenced will be handled by the Stat_Receiver object.
		for sig in self.signals: #随从离场时会自己清除自己的光环
			try: game.trigsBoard[self.entity.ID][sig].append(self)
			except: game.trigsBoard[self.entity.ID][sig] = [self]
			
	def selfCopy(self, recipient): #The recipient is the minion that deals the Aura.
		return type(self)(recipient, self.attack, self.health)
	#可以通过HasAura_toMinion的createCopy方法复制
	
	
class StatAura_Enrage(HasAura_toMinion):
	def __init__(self, entity, attack):
		self.entity = entity
		self.attack = attack
		self.on = False
		self.auraAffected = []
		
	#光环开启和关闭都取消，因为要依靠随从自己的handleEnrage来触发
	def auraAppears(self):
		minion = self.entity
		try: minion.Game.trigsBoard[minion.ID]["MinionStatCheck"].append(self)
		except: minion.Game.trigsBoard[minion.ID]["MinionStatCheck"] = [self]
		if minion.onBoard and minion.health < minion.health_max and not self.on:
			self.on = True
			self.applies(minion)
			
	def auraDisappears(self):
		self.on = False
		try: self.entity.Game.trigsBoard[self.entity.ID]["MinionStatCheck"].remove(self)
		except: pass
		for minion, receiver in self.auraAffected[:]:
			receiver.effectClear()
		self.auraAffected = []
		
	#To be overridden by other more unique enrage minions
	def applies(self, target):
		Stat_Receiver(target, self, self.attack, 0).effectStart()
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return target == self.entity and target.onBoard
		
	def trig(self, signal, ID, subject, target, number, comment, choice=0):
		if self.canTrig(signal, ID, subject, target, number, comment):
			self.effect(signal, ID, subject, target, number, comment)
			
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		minion = self.entity
		if minion.health < minion.health_max and not self.on:
			self.on = True
			self.applies(minion)
		elif minion.health >= minion.health_max and self.on:
			self.on = False
			for minion, receiver in self.auraAffected[:]:
				receiver.effectClear()
				
	def selfCopy(self, recipient): #The recipientMinion is the entity that deals the Aura.
		#func that checks if subject is applicable will be the new copy's function
		return type(self)(recipient, self.attack)
	#激怒的光环仍然可以通过HasAura_toMinion的createCopy复制
	
class Effect_Receiver:
	def __init__(self, recipient, source, keyWord):
		self.source = source #The aura.
		self.recipient = recipient
		self.keyWord = keyWord
		
	def effectStart(self):
		obj = self.recipient
		try: obj.effectfromAura[self.keyWord] += 1
		except: obj.effectfromAura[self.keyWord] = 1
		try: obj.getsStatus(self.keyWord)
		except: obj.marks[self.keyWord] += 1
		obj.auraReceivers.append(self)
		self.source.auraAffected.append((obj, self))
		
	#The aura on the receiver is cleared and the source will remove this receiver and receiver from it's list.
	def effectClear(self):
		obj = self.recipient
		obj.effectfromAura[self.keyWord] -= 1
		try: obj.losesStatus(self.keyWord)
		except: obj.marks[self.keyWord] -= 1
		try: obj.auraReceivers.remove(self)
		except: pass
		try: self.source.auraAffected.remove((obj, self))
		except: pass
		
	#After a receiver is deep copied, it will also copy this receiver, simply remove it.
	#The aura_Dealer won't have reference to this copied aura.
	def effectDiscard(self):
		obj = self.recipient
		obj.effectfromAura[self.keyWord] -= 1
		try: obj.losesStatus(self.keyWord)
		except: obj.marks[self.keyWord] -= 1
		try: obj.auraReceivers.remove(self)
		except: pass
		
	def selfCopy(self, recipient):
		return type(self)(recipient, self.source, self.keyWord)
		
class EffectAura(HasAura_toMinion):
	def __init__(self, entity, keyWord):
		super().__init__(entity)
		self.keyWord = keyWord
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject.ID == self.entity.ID and subject != self.entity and self.applicable(subject)
		
	def applies(self, subject):
		if self.applicable(subject):
			Effect_Receiver(subject, self, self.keyWord).effectStart()
			
	def selfCopy(self, recipient):
		return type(self)(recipient, self.keyWord)
	#关键字光环可以通过HasAura_toMinion的createCopy方法复制
	
	
class GameRuleAura:
	def __init__(self, entity):
		self.entity = entity
		
	def selfCopy(self, recipient): #The recipient is the entity that deals the Aura.
		return type(self)(recipient)
		
	def createCopy(self, game):
		if self not in game.copiedObjs:
			entityCopy = self.entity.createCopy(game)
			Copy = self.selfCopy(entityCopy)
			game.copiedObjs[self] = Copy
			return Copy
		else:
			return game.copiedObjs[self]
			
			
class ManaMod:
	def __init__(self, card, changeby=0, changeto=-1, source=None, lowerbound=0):
		self.card = card
		self.changeby, self.changeto = changeby, changeto
		self.lowerbound = lowerbound
		self.source = source
		
	def handleMana(self):
		if self.changeby:
			self.card.mana += self.changeby
			self.card.mana = max(self.lowerbound, self.card.mana) #用于召唤传送门的随从减费不小于1的限制。
		elif self.changeto >= 0: self.card.mana = self.changeto
		
	def applies(self):
		self.card.manaMods.append(self) #需要让卡牌自己也带有一个检测的光环，离开手牌或者牌库中需要清除。
		if self.card in self.card.Game.Hand_Deck.hands[self.card.ID] or self.card in self.card.Game.Hand_Deck.decks[self.card.ID]:
			mana_0 = self.card.mana
			self.card.Game.Manas.calcMana_Single(self.card)
			mana_1 = self.card.mana
			if mana_0 != mana_1 and self.card.Game.GUI:
				self.card.Game.GUI.manaChangeAni(self.card, mana_1)
				
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
class ManaAura:
	def __init__(self, entity, changeby=0, changeto=-1, lowerbound=0):
		self.entity = entity
		self.changeby, self.changeto, self.lowerbound = changeby, changeto, lowerbound
		self.auraAffected = []  #A list of (card, receiver)
		
	def manaAuraApplicable(self, target):
		return self.entity.manaAuraApplicable(target)
		
	#只要是有满足条件的卡牌进入手牌，就会触发这个光环。target是承载这个牌的列表。
	#applicable不需要询问一张牌是否在手牌中。光环只会处理在手牌中的卡牌
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and self.manaAuraApplicable(target[0])
		
	def trig(self, signal, ID, subject, target, number, comment, choice=0):
		if self.canTrig(signal, ID, subject, target, number, comment):
			self.effect(signal, ID, subject, target, number, comment)
			
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.applies(target[0])
		
	def applies(self, target): #This target is NOT holder.
		if self.manaAuraApplicable(target):
			manaMod = ManaMod(target, self.changeby, self.changeto, self, self.lowerbound)
			manaMod.applies()
			self.auraAffected.append((target, manaMod))
			
	def auraAppears(self):
		game = self.entity.Game
		for card in game.Hand_Deck.hands[1]: self.applies(card)
		for card in game.Hand_Deck.hands[2]: self.applies(card)
		
		try: game.trigsBoard[self.entity.ID]["CardEntersHand"].append(self)
		except: game.trigsBoard[self.entity.ID]["CardEntersHand"] = [self]
		game.Manas.calcMana_All()
		
	#When the aura object is no longer referenced, it vanishes automatically.
	def auraDisappears(self):
		minion = self.entity
		for card, manaMod in self.auraAffected[:]:
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
			
			
#TempManaEffects are supposed be single-usage and expires. But they can be modified to last longer, etc.
class TempManaEffect:
	def __init__(self, Game, ID, changeby=0, changeto=-1):
		self.Game, self.ID = Game, ID
		self.changeby, self.changeto = changeby, changeto
		self.temporary = True
		self.auraAffected = []
		self.signals = ["CardEntersHand", "ManaPaid"]
		
	def applicable(self, target):
		return True
	#signal有"CardEntersHand"和"ManaPaid",只要它们满足applicable就可以触发。
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.applicable(target[0] if signal[0] == "C" else subject)
		
	def trig(self, signal, ID, subject, target, number, comment, choice=0):
		if self.applicable(target[0] if signal[0] == "C" else subject):
			if signal[0] == "C": self.applies(target[0])
			else: self.auraDisappears() #"ManaPaid" check is done in the canTrig. Here it always turns off the disposable aura
			
	def applies(self, subject):
		if self.applicable(subject):
			manaMod = ManaMod(subject, self.changeby, self.changeto, self)
			manaMod.applies()
			self.auraAffected.append((subject, manaMod))
			
	def auraAppears(self):
		game = self.Game
		for card in game.Hand_Deck.hands[1]: self.applies(card)
		for card in game.Hand_Deck.hands[2]: self.applies(card)
		for sig in self.signals:
			try: game.trigsBoard[self.ID][sig].append(self)
			except: game.trigsBoard[self.ID][sig] = [self]
		game.trigAuras[self.ID].append(self)
		game.Manas.calcMana_All()
		
	def auraDisappears(self):
		game = self.Game
		for minion, manaMod in self.auraAffected[:]:
			manaMod.getsRemoved()
		self.auraAffected = []
		try: game.Manas.CardAuras.remove(self)
		except: pass
		for sig in self.signals:
			try: game.trigsBoard[self.ID][sig].remove(self)
			except: pass
		try: game.trigAuras[self.ID].remove(self)
		except: pass
		game.Manas.calcMana_All()
		
	def selfCopy(self, game):
		return type(self)(game, self.ID)
		
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
			
			
class ManaAura_1UsageEachTurn: #For Pint-sized Summoner, Kalecgos, etc
	def __init__(self, entity):
		self.entity = entity
		self.aura = None
	#只要是有满足条件的卡牌进入手牌，就会触发这个光环。target是承载这个牌的列表。
	#applicable不需要询问一张牌是否在手牌中。光环只会处理在手牌中的卡牌
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and ID == self.entity.ID
		
	def trig(self, signal, ID, subject, target, number, comment, choice=0):
		if self.canTrig(signal, ID, subject, target, number, comment):
			self.aura.auraAppears()
			
	def auraAppears(self):
		game, ID = self.entity.Game, self.entity.ID
		if game.turn == ID and game.Counters.numMinionsPlayedThisTurn[ID] < 1:
			self.aura = TempManaEffect(game, ID)
			self.aura.auraAppears()
		try: game.trigsBoard[ID]["TurnStarts"].append(self)
		except: game.trigsBoard[ID]["TurnStarts"] = [self]
		#self.aura.auraAppears will handle the calcMana_All()
		#When the aura object is no longer referenced, it vanishes automatically.
	def auraDisappears(self):
		if self.aura:
			self.aura.auraDisappears() #这个光环只负责（尝试）关掉它的TempManaEffect
			self.aura = None
		try: self.entity.Game.trigsBoard[self.entity.ID]["TurnStarts"].remove(self)
		except: pass
		
	def selfCopy(self, recipient): #The recipient is the entity that deals the Aura.
		return type(self)(recipient)
		
	def createCopy(self, game):
		if self not in game.copiedObjs:
			entityCopy = self.entity.createCopy(game)
			trigCopy = self.selfCopy(entityCopy)
			if self.aura: trigCopy.aura = self.aura.createCopy(game)
			return trigCopy
		else:
			return game.copiedObjs[self]
			
			
class TempManaEffect_Power:
	def __init__(self, Game, ID, changeby=0, changeto=-1):
		self.Game, self.ID = Game, ID
		self.changeby, self.changeto = changeby, changeto
		self.temporary = True
		self.auraAffected = []
		self.signals = ["HeroPowerAcquired", "ManaPaid"]
		
	def applicable(self, target):
		return True
	#signal有"CardEntersHand"和"ManaPaid",只要它们满足applicable就可以触发。
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.applicable(subject) #Hero Power的出现是不传递holder而是直接传递subject
		
	def trig(self, signal, ID, subject, target, number, comment, choice=0):
		if self.applicable(subject):
			if signal[0] == "H": self.applies(subject)
			elif subject == self.Game.powers[self.ID]: #Mana Paid consumes the aura
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
		for sig in self.signals:
			try: game.trigsBoard[self.ID][sig].append(self)
			except: game.trigsBoard[self.ID][sig] = [self]
		self.Game.Manas.calcMana_Powers()
		
	def auraDisappears(self):
		for power, manaMod in self.auraAffected[:]:
			manaMod.getsRemoved()
		self.auraAffected = []
		try: self.Game.Manas.PowerAuras.remove(self)
		except: pass
		for sig in self.signals:
			try: self.Game.trigsBoard[self.ID][sig].remove(self)
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
			
			
class ManaAura_Power:
	def __init__(self, entity, changeby=0, changeto=-1):
		self.entity = entity
		self.changeby, self.changeto = changeby, changeto
		self.auraAffected = []
	
	def manaAuraApplicable(self, subject):
		return self.entity.manaAuraApplicable(subject)
		
	#signal有"CardEntersHand"和"ManaPaid",只要它们满足applicable就可以触发。
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and self.manaAuraApplicable(subject) #Hero Power的出现是不传递holder而是直接传递subject
		
	def trig(self, signal, ID, subject, target, number, comment, choice=0):
		if self.canTrig(signal, ID, subject, target, number, comment):
			self.effect(signal, ID, subject, target, number, comment)
			
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.applies(subject)
		
	def applies(self, subject):
		if self.manaAuraApplicable(subject):
			manaMod = ManaMod(subject, self.changeby, self.changeto, self)
			manaMod.applies()
			self.auraAffected.append((subject, manaMod))
			
	def auraAppears(self):
		game = self.entity.Game
		self.applies(game.powers[1])
		self.applies(game.powers[2])
		try: game.trigsBoard[self.entity.ID]["HeroPowerAcquired"].append(self)
		except: game.trigsBoard[self.entity.ID]["HeroPowerAcquired"] = [self]
		game.Manas.calcMana_Powers()
		
	def auraDisappears(self):
		for power, manaMod in self.auraAffected[:]:
			manaMod.getsRemoved()
		self.auraAffected = []
		try: self.entity.Game.trigsBoard[self.entity.ID]["HeroPowerAcquired"].remove(self)
		except: pass
		self.entity.Game.Manas.calcMana_Powers()
		
	def selfCopy(self, game):
		return type(self)(game, self.entity.ID, self.changeby, self.changeto)
		
	def createCopy(self, game): #The recipient is the Game that handles the Aura.
		if self not in game.copiedObjs:
			Copy = self.selfCopy(game)
			game.copiedObjs[self] = Copy
			for power, manaMod in self.auraAffected:
				powerCopy = power.createCopy(game)
				manaModIndex = power.manaMods.index(manaMod)
				manaModCopy = powerCopy.manaMods[manaModIndex]
				manaModCopy.source = Copy
				Copy.auraAffected.append((powerCopy, manaModCopy))
			return Copy
		else:
			return game.copiedObjs[self]
			