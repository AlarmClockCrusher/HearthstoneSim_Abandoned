"""Madness at the Darkmoon Faire"""

"""Mana 1 cards"""
"""Mana 2 cards"""
"""Mana 3 cards"""
"""Mana 4 cards"""
"""Mana 5 cards"""
#Assume corrupted card don't inherit any buff/debuff
#Assume transformation happens when card is played
class FleethoofPearltusk(Minion):
	Class, race, name = "Neutral", "Beast", "Fleethoof Pearltusk"
	mana, attack, health = 5, 4, 4
	index = "Darkmoon~Neutral~Minion~5~4~4~Beast~Fleethoof Pearltusk~Rush"
	requireTarget, keyWord, description = False, "Rush", "Rush. Corrupt: Gain +4/+4"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsHand = [Trig_FleethoofPearltusk(self)] #只有在手牌中才会升级
		
class Trig_FleethoofPearltusk(TrigHand):
	def __init__(self, entity, humanType):
		self.blank_init(entity, ["ManaPaid"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.inHand and ID == self.entity.ID and number > 5
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.Game.Hand_Deck.replaceCardinHand(self.entity, FleethoofPearltusk_Corrupted(self.entity.Game, self.entity.ID))
		
class FleethoofPearltusk_Corrupted(Minion):
	Class, race, name = "Neutral", "Beast", "Fleethoof Pearltusk"
	mana, attack, health = 5, 8, 8
	index = "Darkmoon~Neutral~Minion~5~8~8~Beast~Fleethoof Pearltusk~Rush~Uncollectible"
	requireTarget, keyWord, description = False, "Rush", "Rush"
	
"""Mana 6 cards"""
"""Mana 7 cards"""
"""Mana 8 cards"""
"""Mana 9 cards"""
"""Mana 10 cards"""
#Assume one can get CThun as long as pieces are played, even if it didn't start in their deck
class Trig_CThun:
	def __init__(self, Game, ID):
		self.Game, self.ID = Game, ID
		self.temp = False
		self.piece = []
		
	def connect(self):
		try: self.Game.trigsBoard[self.ID]["CThunPiece"].append(self)
		except: self.Game.trigsBoard[self.ID]["CThunPiece"] = [self]
		
	def disconnect(self):
		try: self.Game.trigsBoard[self.ID]["CThunPiece"].remove(self)
		except: pass
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return subject.ID == self.ID and subject == self.spellDiscovered
		
	def trigger(self, signal, ID, subject, target, number, comment, choice=0):
		if self.canTrigger(signal, ID, subject, target, number, comment):
			if self.Game.GUI: self.Game.GUI.showOffBoardTrig(CThuntheShattered(self.Game, self.ID), linger=False)
			self.effect(signal, ID, subject, target, number, comment)
			
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		if ID == self.ID and number not in self.pieces:
			self.pieces.append(number)
			if len(self.pieces) > 3:
				PRINT("Player %d's C'Thun is completed and shuffles into the deck"%ID)
				self.Game.Hand_Deck.shuffleCardintoDeck(CThuntheShattered(self.Game, ID), ID)
				self.disconnect()
				
	def createCopy(self, game): #不是纯的只在回合结束时触发，需要完整的createCopy
		if self not in game.copiedObjs: #这个扳机没有被复制过
			trigCopy = type(self)(game, self.ID)
			trigCopy.pieces = [i for i in self.pieces]
			game.copiedObjs[self] = trigCopy
			return trigCopy
		else: #一个扳机被复制过了，则其携带者也被复制过了
			return game.copiedObjs[self]
			
class BodyofCThun(Spell):
	Class, name = "Neutral", "Body of C'Thun"
	requireTarget, mana = False, 5
	index = "Darkmoon~Neutral~Spell~5~Body of C'Thun~Uncollectible"
	description = "Summon a 6/6 C'Thun's body with Taunt"
	def available(self):
		return self.Game.space(self.ID) > 0
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		PRINT(self.Game, "Body of C'Thun summons a 6/6 Body of C'Thun")
		self.Game.summon(BodyofCThun(self.Game, self.ID), -1, self.ID)
		#Assume the spell effect will increase the counter
		if "CThunPiece" not in self.Game.trigsBoard[self.ID]:
			Trig_CThun.connect()
		self.Game.sendSignal("CThunPiece", self.ID, None, None, 1, "")
		return None
		
class BodyofCThun_Minion(Minion):
	Class, race, name = "Neutral", "", "Body of C'Thun"
	mana, attack, health = 6, 6, 6
	index = "Darkmoon~Neutral~Minion~6~6~6~None~Body of C'Thun~Taunt~Uncollectible"
	requireTarget, keyWord, description = False, "Taunt", "Taunt"
	
class EyeofCThun(Spell):
	Class, name = "Neutral", "Eye of C'Thun"
	requireTarget, mana = False, 5
	index = "Darkmoon~Neutral~Spell~5~Eye of C'Thun~Uncollectible"
	description = "Deal 7 damage randomly split among all enemies"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		damage = (7 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		side, curGame = 3 - self.ID, self.Game
		if curGame.mode == 0:
			PRINT(curGame, "Eye of C'Thun deals %d damage randomly split among enemies."%damage)
			for num in range(damage):
				char = None
				if curGame.guides:
					i, where = curGame.guides.pop(0)
					if where: char = curGame.find(i, where)
				else:
					objs = curGame.charsAlive(side)
					if objs:
						char = npchoice(objs)
						curGame.fixedGuides.append((side, "hero") if char.type == "Hero" else (char.position, "minion%d"%side))
					else:
						curGame.fixedGuides.append((0, ''))
				if char:
					self.dealsDamage(char, 1)
				else: break
		if "CThunPiece" not in self.Game.trigsBoard[self.ID]:
			Trig_CThun.connect()
		self.Game.sendSignal("CThunPiece", self.ID, None, None, 2, "")
		return None
		
class HeartofCThun(Spell):
	Class, name = "Neutral", "Heart of C'Thun"
	requireTarget, mana = False, 5
	index = "Darkmoon~Neutral~Spell~5~Heart of C'Thun~Uncollectible"
	description = "Deal 3 damage to all minions"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		damage = (3 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		targets = self.Game.minionsonBoard(1) + self.Game.minionsonBoard(2)
		PRINT(self.Game, "Heart of C'Thun deals %d damage to all minions."%damage)
		self.dealsAOE(targets, [damage] * len(targets))
		if "CThunPiece" not in self.Game.trigsBoard[self.ID]:
			Trig_CThun.connect()
		self.Game.sendSignal("CThunPiece", self.ID, None, None, 3, "")
		return None
		
class MawofCThun(Spell):
	Class, name = "Neutral", "Maw of C'Thun"
	requireTarget, mana = False, 5
	index = "Darkmoon~Neutral~Spell~5~Maw of C'Thun~Uncollectible"
	description = "Destroy a minion"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			PRINT(self.Game, "Maw of C'Thun destroys minion %s"%target.name)
			self.Game.killMinion(self, target)
		#Assume the counter still works even if there is no target designated
		if "CThunPiece" not in self.Game.trigsBoard[self.ID]:
			Trig_CThun.connect()
		self.Game.sendSignal("CThunPiece", self.ID, None, None, 4, "")
		return None
		
class CThuntheShattered(Minion):
	Class, race, name = "Neutral", "", "C'Thun, the Shattered"
	mana, attack, health = 10, 6, 6
	index = "Darkmoon~Neutral~Minion~10~6~6~None~C'Thun, the Shattered~Battlecry~Start of Game~Legendary"
	requireTarget, keyWord, description = False, "", "Start of Game: Break into pieces. Battlecry: Deal 30 damage randomly split among all enemies"
	
	def startofGame(self):
		#Remove the card from deck. Assume the final card WON't count as deck original card 
		curGame, ID = self.Game, self.ID
		curGame.Hand_Deck.extractfromDeck(self, ID=0, all=False, enemyCanSee=True)
		curGame.Hand_Deck.shuffleCardintoDeck([BodyofCThun(curGame, ID), EyeofCThun(curGame, ID), HeartofCThun(curGame ID), MawofCThun(curGame, ID)], ID)
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		side, curGame = 3-self.ID, self.Game
		if curGame.mode == 0:
			PRINT(curGame, "C'Thun, the Shattered's battlecry deals 30 damage randomly split among all enemies")
			for num in range(30):
				char = None
				if curGame.guides:
					i, where = curGame.guides.pop(0)
					if where: char = curGame.find(i, where)
				else:
					objs = curGame.charsAlive(side)
					if objs:
						char = npchoice(objs)
						curGame.fixedGuides.append((side, "hero") if char.type == "Hero" else (char.position, "minion%d"%side))
					else:
						curGame.fixedGuides.append((0, ''))
				if char:
					self.dealsDamage(char, 1)
				else: break
		return None
		
		
class DarkmoonRabbit(Minion):
	Class, race, name = "Neutral", "Beast", "Darkmoon Rabbit"
	mana, attack, health = 10, 1, 1
	index = "Darkmoon~Neutral~Minion~10~1~1~Beast~Darkmoon Rabbit~Rush~Poisonous"
	requireTarget, keyWord, description = False, "Rush,Poisonous", "Rush, Poisonous. Also damages the minions next to whomever this attacks"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.marks["Sweep"] = 1
		
		
class NZothGodoftheDeep(Minion):
	
class YoggSaronMasterofFate(Minion):
	
class YShaarjtheDefiler(Minion):

"""Demon Hunter cards"""
"""Druid cards"""
"""Hunter cards"""
"""Mage cards"""
"""Paladin cards"""
"""Priest cards"""
"""Rogue cards"""
"""Shaman cards"""
"""Warlock cards"""
"""Warrior cards"""