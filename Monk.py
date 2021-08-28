from CardTypes import *
from Triggers_Auras import *

from numpy.random import choice as npchoice
from numpy.random import randint as nprandint
from numpy.random import shuffle as npshuffle

def PRINT(game, s):
	pass
	
class WindWalkerMistweaver(Power): #踏风织雾
	mana, name, requireTarget = 2, "WindWalker-Mistweaver", True
	index = "Monk~Basic Hero Power~2~WindWalker-Mistweaver"
	description = "Give a friendly character +1 Attack this turn; or give an enemy character -1 Attack" #在本回合中，使用一个友方角色获得+1攻击力；或者使一个敌方角色获得-1攻击力
	def effect(self, target=None, choice=0, comment=''):
		if target:
			if target.ID == self.ID:
				PRINT(self.Game, "Hero Power WindWalker-Mistweaver gives friendly character %s +1 Attack this turn"%target.name)
				attChange = 1
			else:
				PRINT(self.Game, "Hero Power WindWalker-Mistweaver gives enemy character %s -1 Attack this turn"%target.name)
				attChange = -1
			if target.type == "Hero": target.gainTempAttack(attChange)
			else: target.buffDebuff(attChange, 0, "EndofTurn")
		return 0
		
class HighWindWalkerMistweaver(Power): #精进踏风织雾
	mana, name, requireTarget = 2, "High WindWalker-Mistweaver", True
	index = "Monk~Upgraded Hero Power~2~High WindWalker-Mistweaver"
	description = "Give a friendly character +2 Attack this turn; or give an enemy character -2 Attack" #在本回合中，使用一个友方角色获得+1攻击力；或者使一个敌方角色获得-1攻击力
	def effect(self, target=None, choice=0, comment=''):
		if target:
			if target.ID == self.ID:
				PRINT(self.Game, "Hero Power WindWalker-Mistweaver gives friendly character %s +2 Attack this turn"%target.name)
				attChange = 2
			else:
				PRINT(self.Game, "Hero Power WindWalker-Mistweaver gives enemy character %s -2 Attack this turn"%target.name)
				attChange = -2
			if target.type == "Hero": target.gainTempAttack(attChange)
			else: target.buffDebuff(attChange, 0, "EndofTurn")
		return 0
		
class Chen(Hero):
	Class, name, heroPower = "Monk", "Chen", WindWalkerMistweaver
	
"""Monk Basic Cards"""
class Resuscitate(Spell): #轮回转世
	Class, school, name = "Monk", "", "Resuscitate"
	requireTarget, mana = True, 0
	index = "Basic~Monk~Spell~0~Resuscitate"
	description = "Return a friendly minion to your hand. Restore a Mana Crystal" #将一个友方随从移回你的手牌。复原一个法力水晶
	def available(self):
		return self.selectableFriendlyMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.ID == self.ID and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target and target.onBoard:
			PRINT(self.Game, "Resuscitate returns friendly minion %s to player's hand and restores a Mana Crystal"%target.name)
			self.Game.returnMiniontoHand(target, deathrattlesStayArmed=False)
		self.Game.Manas.restoreManaCrystal(1, self.ID)
		return target
		
		
class ArchoftheTemple(Minion): #禅院的牌坊
	Class, race, name = "Monk", "", "Arch of the Temple"
	mana, attack, health = 1, 0, 2
	index = "Basic~Monk~Minion~1~0~2~~Arch of the Temple~Taunt~Battlecry"
	requireTarget, keyWord, description = False, "Taunt", "Taunt. Battlecry: Add two 1/1 Monks with Rush to your hand" #嘲讽。战吼：将两张1/1并具有突袭的武僧置入你的手牌
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		PRINT(self.Game, "Arch of the Templer's battlecry adds two 1/1 Monks with Rush to player's hand")
		self.Game.Hand_Deck.addCardtoHand([MonkAttacker, MonkAttacker], self.ID, "type")
		return None
		
class MonkAttacker(Minion): #武僧袭击者
	Class, race, name = "Monk", "", "Monk Attacker"
	mana, attack, health = 1, 1, 1
	index = "Basic~Monk~Minion~1~1~1~~Monk Attacker~Rush~Uncollectible"
	requireTarget, keyWord, description = False, "Rush", "Rush"
	
	
class CanewithaWineGourd(Weapon): #带酒葫芦的杖子
	#每当你的英雄攻击后为其恢复3点生命值
	Class, name, description = "Monk", "Cane with a Wine Gourd", "After your Hero attacks, restore 3 Health to it"
	mana, attack, durability = 1, 0, 4
	index = "Basic~Monk~Weapon~1~0~4~Cane with a Wine Gourd"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_CanewithaWineGourd(self)]
		
class Trig_CanewithaWineGourd(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["HeroAttackedMinion", "HeroAttackedHero"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject == self.entity.Game.heroes[self.entity.ID] and self.entity.onBoard
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		heal = 3 * (2 ** self.entity.countHealDouble())
		PRINT(self.entity.Game, "%s restores %d Health the hero after it attacked."%(self.entity.name, heal))
		self.entity.restoresHealth(self.entity.Game.heroes[self.entity.ID], heal)
		
		
class MonksApprentice(Minion):
	#当该随从的攻击力大于或等于2时，使其获得这突袭和风怒
	Class, race, name = "Monk", "", "Monk's Apprentice"
	mana, attack, health = 1, 1, 3
	index = "Basic~Monk~Minion~1~1~3~~Monk's Apprentice"
	requireTarget, keyWord, description = False, "", "While this minion has 2 or more Attack, it has Rush and Windfury"
			
class ShaohaosProtection(Spell): #少昊的保护
	#使一个友方随从获得+2生命值且无法成为法术或英雄技能的目标
	Class, school, name = "Monk", "", "Shaohao's Protection"
	requireTarget, mana = True, 1
	index = "Basic~Monk~Spell~1~Shaohao's Protection"
	description = "Give a friendly minion +2 Health and 'Can't be targeted by spells or Hero Powers'"
	def available(self):
		return self.selectableFriendlyMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.ID == self.ID and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			PRINT(self.Game, "Shaohao's Protection gives friendly minion %s +2 Health. It can't be targeted by spells or Hero Powers anymore"%target.name)
			target.buffDebuff(0, 2)
			target.marks["Evasive"] += 1
		return target
		
		
class EffusiveMists(Spell): #流溢之雾
	Class, school, name = "Monk", "", "Effusive Mists"
	requireTarget, mana = False, 2
	index = "Basic~Monk~Spell~2~Effusive Mists"
	description = "Change the Attack of 2 random enemy minions to 1" #将两个随机敌方随从的攻击力变为1
	def available(self):
		return self.Game.minionsonBoard(3-self.ID)
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		minions = curGame.minionsonBoard(3-self.ID)
		if minions:
			if curGame.mode == 0:
				if curGame.picks:
					minions = [curGame.minions[3-self.ID][i] for i in curGame.picks.pop(0)]
				else:
					minions = list(npchoice(minions, min(2, len(minions)), replace=False))
					curGame.picks.append(tuple([minion.pos for minion in minions]))
				PRINT(curGame, "Effusive Mists sets the Attack of minions {} to 1".format(minions))
				for minion in minions: minion.statReset(1, False)
		return None
		
		
class SwiftBrewmaster(Minion): #迷踪的酒仙
	#你的英雄技能在触发畅饮时会同时指向目标和其相邻随从
	Class, race, name = "Monk", "", "Swift Brewmaster"
	mana, attack, health = 2, 1, 4
	index = "Basic~Monk~Minion~2~1~4~~Swift Brewmaster"
	requireTarget, keyWord, description = False, "", "Your Hero Power also targets adjacent minions if it triggers Quaff"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_SwiftBrewmaster(self)]
		
class Trig_SwiftBrewmaster(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["ManaPaid", "HeroUsedAbility"])
		self.on = False
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		minion, game = self.entity, self.entity.Game
		if signal == "ManaPaid": return subject == game.powers[minion.ID] and not self.on and game.Manas.manas[minion.ID] == 0
		else: return ID == self.entity.ID and self.on
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		if signal == "ManaPaid":
			self.entity.Game.status[self.entity.ID]["Power Sweep"] += 1
			self.on = True
		else:
			self.entity.Game.status[self.entity.ID]["Power Sweep"] -= 1
			self.on = False
			
			
class Provoke(Spell): #嚎镇八方
	#在本回合中，使一个友方角色获得+4攻击力；或者使一个敌方角色获得-4攻击力
	Class, school, name = "Monk", "", "Provoke"
	requireTarget, mana = True, 3
	index = "Basic~Monk~Spell~3~Provoke"
	description = "Give a friendly character +4 Attack this turn; or an enemy character -4 Attack this turn"
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			if target.ID == self.ID:
				PRINT(self.Game, "Provoke is cast and gives friendly character %s +4 Attack this turn"%target.name)
				attChange = 4
			else:
				PRINT(self.Game, "Provoke is cast and gives enemy character %s -4 Attack this turn"%target.name)
				attChange = -4
			if target.type == "Hero": target.gainTempAttack(attChange)
			else: target.buffDebuff(attChange, 0, "EndofTurn")
		return target
		
		
class SweepingKickFighter(Minion): #扫堂腿格斗师
	#突袭。同时对其攻击目标相邻的随从造成伤害
	Class, race, name = "Monk", "", "Sweeping Kick Fighter"
	mana, attack, health = 3, 1, 4
	index = "Basic~Monk~Minion~3~1~4~~Sweeping Kick Fighter~Rush"
	requireTarget, keyWord, description = False, "Rush", "Rush. Also damages minions next to whoever this attacks"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.marks["Sweep"] = 1
		
			
class ShadoPanWuKao(Minion): #影踪派悟道者
	#在你的英雄攻击后，获得潜行
	Class, race, name = "Monk", "", "Shado-Pan Wu Kao"
	mana, attack, health = 3, 3, 4
	index = "Basic~Monk~Minion~3~3~4~~Shado-Pan Wu Kao"
	requireTarget, keyWord, description = False, "", "After your hero attacks, gain Stealth"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_ShadoPanWuKao(self)]
		
class Trig_ShadoPanWuKao(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["HeroAttackedMinion", "HeroAttackedHero"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject == self.entity.Game.heroes[self.entity.ID]
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self.entity.Game, "After friendly hero attacks, %s gains Stealth"%self.entity.name)
		self.entity.getsStatus("Stealth")
		
		
"""Monk Classic Cards"""
class WiseLorewalkerCho(Minion): #睿智的游学者周卓
	#战吼：发现一张法力值消耗等同于你的法力水晶数量的其他职业的法术牌
	Class, race, name = "Monk", "", "Wise Lorewalker Cho"
	mana, attack, health = 1, 0, 4
	index = "Classic~Monk~Minion~1~0~4~~Wise Lorewalker Cho~Battlecry~Legendary"
	requireTarget, keyWord, description = False, "", "Battlecry: Discover a spell from another class with Cost equal to your remaining Mana Crystals"
	poolIdentifier = "0-Cost Spells"
	@classmethod
	def generatePool(cls, pools):
		costs, lists = [], []
		for cost in range(11):
			spells, s = [], "~Spell~%d~"%cost
			for Class in pools.Classes:
				spells += [value for key, value in pools.ClassCards[Class].items() if s in key]
			costs.append("%d-Cost Spells"%cost)
			lists.append(spells)
		return costs, lists
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if self.ID == self.Game.turn:
			Class = "Monk" if self.Game.heroes[self.ID].Class == "Neutral" else self.Game.heroes[self.ID].Class
			#需要把所有的职业捋一遍，出一个dict
			mana = self.Game.Manas.manas[self.ID]
			spells, pool = {}, self.rngPool["%d-Cost Spells"%mana]
			for spell in pool:
				for spellClass in spell.Class.split(','):
					if spellClass in spells: spells[spellClass].append(spell)
					else: spells[spellClass] = [spell]
			if "byOthers" in comment:
				card = npchoice(npchoice(list(spells.keys())))
				PRINT(self.Game, "Wise Lorewalker Cho's battlecry adds a random spell from another class with cost equal player's remain mana to player's hand")
				self.Game.Hand_Deck.addCardtoHand(card, self.ID, "type")
			else:
				classes = list(spells.keys())
				try: classes.remove(Class)
				except: pass
				classes = npchoice(classes, min(3, len(classes)), replace=False)
				for Class in classes:
					self.Game.options.append(npchoice(spells[Class])(self.Game, self.ID))
				PRINT(self.Game, "Wise Lorewalker Cho's battlecry lets player discover a Dragon")
				self.Game.Discover.startDiscover(self)
		return None
		
	def discoverDecided(self, option, pool=None):
		PRINT(self.Game, "Spell %s is added to player's hand"%option.name)
		self.Game.Hand_Deck.addCardtoHand(option, self.ID, byDiscover=True)
		
		
class XuentheWhiteTiger_Mutable_1(Minion): #白虎 雪怒
	#突袭。在你使用一张牌后，将该随从移回你的手牌。并使其永久获得+2/+2和法力值消耗增加(1)点(最高不超过10点)。
	Class, race, name = "Monk", "Beast", "Xuen, the White Tiger"
	mana, attack, health = 1, 1, 1
	index = "Classic~Monk~Minion~1~1~1~Beast~Xuen, the White Tiger~Rush~Legendary"
	requireTarget, keyWord, description = False, "Rush", "Rush. After you play a card, return this to your hand and give it +2/+2 for the rest of the game. It costs (1) more(up to 10)"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_XuentheWhiteTiger(self)]
		
class Trig_XuentheWhiteTiger(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["MinionBeenPlayed", "SpellBeenPlayed", "WeaponBeenPlayed", "HeroCardBeenPlayed"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject.ID == self.entity.ID and subject != self.entity
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		minion = self.entity
		PRINT(minion.Game, "Player played a card and %s returns itself to player's hand. It gain +2/+2 and costs (1) more permanently."%minion.name)
		if minion.Game.returnMiniontoHand(minion, deathrattlesStayArmed=False):
			cost = type(minion).mana + 1
			stat = cost * 2 - 1
			newIndex = "Classic~Monk~Minion~%d~%d~%d~Beast~Xuen, the White Tiger~Rush~Legendary~Uncollectible"%(cost, stat, stat)
			subclass = type("XuentheWhiteTiger__%d"%cost, (XuentheWhiteTiger_Mutable_1, ),
						{"mana": cost, "attack": stat, "health": stat, "index": newIndex}
						)
			minion.Game.transform(minion, subclass(minion.Game, minion.ID))
			
			
class DefenseTechniqueMaster(Minion): #御术僧师
	#嘲讽。畅饮：获得‘亡语：本回合中，在使你的英雄获得+3攻击力’
	Class, race, name = "Monk", "", "Defense Technique Master"
	mana, attack, health = 2, 3, 2
	index = "Classic~Monk~Minion~2~3~2~~Defense Technique Master~Taunt~Quaff"
	requireTarget, keyWord, description = False, "Taunt", "Taunt. Quaff: Gain 'Deathrattle: Give your hero +3 Attack this turn'"
	
	def effCanTrig(self):
		self.effectViable = (self.Game.Manas.manas[self.ID] == self.mana)
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if posinHand > -2 and not self.Game.Manas.manas[self.ID]:
			PRINT(self.Game, "Defense Technique Master's Quaff triggers and gives the minion 'Deathrattle: Give your hero +3 Attack this turn'")
			self.Game.sendSignal("QuaffTriggered", self.ID, None, None, 0, "")
			trig = GiveYourHeroPlus3AttackThisTurn(self)
			self.deathrattles.append(trig)
			if self.onBoard:
				trig.connect()
		return None
		
class GiveYourHeroPlus3AttackThisTurn(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self.entity.Game, "Deathrattle: Give your hero +3 Attack this turn triggers.")
		self.entity.Game.heroes[self.entity.ID].gainTempAttack(3)
		
		
class PurifyingBrew(Spell): #活血酒
	Class, school, name = "Monk", "", "Purifying Brew"
	requireTarget, mana = False, 2
	index = "Classic~Monk~Spell~2~Purifying Brew~Quaff"
	description = "Draw a card. Quaff: Add a copy of it to your hand" #抽一张牌。畅饮： 复制该牌并置入你的手牌
	def effCanTrig(self):
		self.effectViable = (self.Game.Manas.manas[self.ID] == self.mana)
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		PRINT(self.Game, "Purifying Brew lets player draw a card")
		card = self.Game.Hand_Deck.drawCard(self.ID)[0]
		if card and posinHand > -2 and not self.Game.Manas.manas[self.ID] and self.Game.Hand_Deck.handNotFull(self.ID):
			PRINT(self.Game, "Purifying Brew's Quaff triggers and adds a copy of the drawn card to player's hand")
			self.Game.sendSignal("QuaffTriggered", self.ID, None, None, 0, "")
			self.Game.Hand_Deck.addCardtoHand(card.selfCopy(self.ID), self.ID)
		return None
		
		
class Transcendance(Spell): #魂体双分
	#选择一个随从。将它的一个1/1复制置入你的手牌，其法力值消耗变为(1)点
	Class, school, name = "Monk", "", "Transcendance"
	requireTarget, mana = True, 2
	index = "Classic~Monk~Spell~2~Transcendance"
	description = "Choose a minion and add a 1/1 copy of it to your hand. It costs (1)"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target and self.Game.Hand_Deck.handNotFull(self.ID):
			PRINT(self.Game, "Transcendance is cast and adds a copy of minion %s to player's hand"%target.name)
			self.Game.Hand_Deck.addCardtoHand(target.selfCopy(self.ID, 1, 1, 1), self.ID)
		return target
		
		
class Liquor(Spell): #醉酿
	Class, school, name = "Monk", "", "Liquor"
	requireTarget, mana = True, 3
	index = "Classic~Monk~Spell~3~Liquor~Quaff"
	description = "Target a minion. It can't attack for two turns. Quaff: Destroy it" #使一个随从两个回合无法攻击。畅饮：消灭该随从
	def effCanTrig(self):
		self.effectViable = (self.Game.Manas.manas[self.ID] == self.mana)
		
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			if posinHand > -2 and not self.Game.Manas.manas[self.ID]: #Triggers Quaff
				PRINT(self.Game, "Liquor's Quaff triggers and destroys minion %s"%target.name)
				self.Game.sendSignal("QuaffTriggered", self.ID, None, None, 0, "")
				self.Game.killMinion(self, target)
			elif target.onBoard: #假设只有当目标随从还在场上的时候会生效
				PRINT(self.Game, "Liquor gives renders minion %s unable to attack for two turns"%target.name)
				target.marks["Can't Attack"] += 1
				trig = Trig_Liquor(target)
				target.trigsBoard.append(trig)
				trig.connect()
		return target
		
class Trig_Liquor(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["TurnEnds"])
		self.temp = True
		self.counter = 2
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.counter -= 1
		if self.counter < 1:
			PRINT(self.entity.Game, "%s can attack next turn."%self.entity.name)
			self.entity.marks["Can't Attack"] -= 1
			self.disconnect()
			try: self.entity.trigsBoard.remove(self)
			except: pass
		else:
			PRINT(self.entity.Game, "%s still can't attack for another turn"%self.entity.name)
			
	#复制的随从一并保留其沉醉扳机
	def selfCopy(self, recipient):
		trig = type(self)(recipient)
		trig.counter = self.counter
		return trig
		
		
class StaveOff(Spell): #酒不离手
	Class, school, name = "Monk", "", "Stave Off"
	requireTarget, mana = False, 3
	index = "Classic~Monk~Spell~3~Stave Off"
	description = "Draw 2 Quaff cards from your deck"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		PRINT(self.Game, "Stave Off is cast and player draws two Quaff cards from the deck.")
		for i in range(2):
			quaffCardsinDeck = []
			for card in self.Game.Hand_Deck.decks[self.ID]:
				if "~Quaff" in card.index:
					quaffCardsinDeck.append(card)
					
			if quaffCardsinDeck:
				self.Game.Hand_Deck.drawCard(self.ID, npchoice(quaffCardsinDeck))
		return None
		
		
class TouchofKarma(Spell): #业报之触
	#选择一个敌方随从。在本回合中，你的英雄受到的伤害改为由该随从承担
	Class, school, name = "Monk", "", "Touch of Karma"
	requireTarget, mana = True, 3
	index = "Classic~Monk~Spell~3~Touch of Karma"
	description = "Target an enemy minion. Damage on your Hero this turn will be taken by that minion instead"
	def available(self):
		return self.selectableEnemyMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.ID != self.ID and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target and target.onBoard:
			PRINT(self.Game, "Touch of Karma is cast and damage on player's Hero this turn will go to enemy minion %s instead"%target.name)
			trig = Trig_TouchofKarma(target, self.ID)
			target.trigsBoard.append(trig)
			trig.connect()
		return target
		
class Trig_TouchofKarma(TrigBoard):
	def __init__(self, entity, ID):
		super().__init__(entity, ["TurnEnds", "DmgTaker?"])
		self.ID = ID
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return signal == "TurnEnds" or (target[0].type == "Hero" and target[0].ID == self.ID)
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		if signal == "TurnEnds":
			PRINT(self.entity.Game, "At the end of turn, minion %s no longer intercepts damage on player %d."%(self.entity.name, self.ID))
			self.disconnect()
			try: self.entity.trigsBoard.remove(self)
			except: pass
		else:
			PRINT(self.entity.Game, "Minion %s takes the damage meant for player's Hero"%self.entity.name)
			target[0] = self.entity
			
	def selfCopy(self, recipient):
		return type(self)(recipient, self.ID)
		
		
class SpiritTether(Spell): #魂体束缚
	#将你的英雄技能替换为“使一个随从变形为2/2并具有嘲讽的魔像”。使用两次后，替换为原技能
	Class, school, name = "Monk", "", "Spirit Tether"
	requireTarget, mana = False, 3
	index = "Classic~Monk~Spell~3~Spirit Tether"
	description = "Swap your Hero Power to 'Transform a minion into a 2/2 Golem with Taunt'. After 2 uses, swap it back"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		PRINT(self.Game, "Spirit Tether is cast and swaps player's Hero Power to 'Transform a minion into a 2/2 Golem with Taunt''. After 2 uses, swap it back")
		JadeTether(self.Game, self.ID).replaceHeroPower()
		return None
		
class JadeTether(Power):
	mana, name, requireTarget = 2, "Jade Tether", True
	index = "Monk~Hero Power~2~Jade Tether"
	description = "Transform a minion into a 2/2 Golem with Taunt"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_JadeTether(self)]
		self.powerReplaced = None
		
	def effect(self, target, choice=0):
		if target:
			PRINT(self.Game, "Hero Power Jade Tether transforms %s into a 2/2 Golem with Taunt"%target.name)
			newMinion = TetheredGolem(self.Game, target.ID)
			self.Game.transform(target, newMinion)
			target = newMinion
		return 0
		
	def replaceHeroPower(self):
		self.powerReplaced = type(self.Game.powers[self.ID])
		if self.Game.powers[self.ID]:
			self.Game.powers[self.ID].disappears()
			self.Game.powers[self.ID] = None
		self.Game.powers[self.ID] = self
		self.appears()
		
class Trig_JadeTether(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["HeroUsedAbility"])
		self.counter = 0
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject == self.entity
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.counter += 1
		PRINT(self.entity.Game, "Player uses Hero Power and Jade Tether has been used for %d times"%self.counter)
		if self.counter > 1:
			PRINT(self.entity.Game, "Player has used Hero Power Jade Tether twice and the Hero Power changes back to the original one it replaced")
			if self.entity.powerReplaced:
				self.entity.powerReplaced(self.entity.Game, self.entity.ID).replaceHeroPower()
				self.disconnect()
				
class TetheredGolem(Minion): #雪怒的子嗣
	#突袭。战吼：从你的牌库中发现一张法力值消耗为(1)的随从
	Class, race, name = "Monk", "", "Tethered Golem"
	mana, attack, health = 2, 2, 2
	index = "Classic~Monk~Minion~2~2~2~Beast~Tethered Golem~Taunt~Uncollectible"
	requireTarget, keyWord, description = False, "Taunt", "Taunt"
	
	
class DrunkenBoxing(Spell): #醉拳
	#在本回合中，使你的英雄获得+5攻击力，随机攻击所有随从。畅饮：每次攻击后，为你的英雄恢复3点生命值
	Class, school, name = "Monk", "", "Drunken Boxing"
	requireTarget, mana = False, 4
	index = "Classic~Monk~Spell~4~Drunken Boxing~Quaff"
	description = "Your Hero gains +5 Attack this turn and randomly attacks all minions. Quaff:　Restore 3 Health to your Hero after each attack"
	def effCanTrig(self):
		self.effectViable = (self.Game.Manas.manas[self.ID] == self.mana)
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		PRINT(self.Game, "Drunken Boxing gives player +5 Attack this turn. It randomly attacks all minions")
		hero = self.Game.heroes[self.ID]
		hero.gainTempAttack(5)
		quaffTriggered = (posinHand > -2 and self.Game.Manas.manas[self.ID] == 0)
		minionstoAttack = self.Game.minionsonBoard(1) + self.Game.minionsonBoard(2)
		npshuffle(minionstoAttack)
		if quaffTriggered:
			trig = Trig_DrunkenBoxing(self)
			trig.connect()
			self.Game.sendSignal("QuaffTriggered", self.ID, None, None, 0, "")
		#注册扳机，检测英雄的攻击
		while minionstoAttack:
			attackTarget = minionstoAttack.pop()
			if attackTarget.health > 0 and not attackTarget.dead and hero.health > 0 and not hero.dead:
				PRINT(self.Game, "Drunken Boxing lets player attack minion %s"%attackTarget.name)
				#def battle(self, subject, target, verifySelectable=True, useAttChance=True, resolveDeath=True, resetRedirTrig=True)
				self.Game.battle(hero, attackTarget, verifySelectable=False, useAttChance=True, resolveDeath=False, resetRedirTrig=False)
				self.Game.trigsBoard[self.ID]
			elif attackTarget.health < 0 or attackTarget.dead:
				PRINT(self.Game, "Player doesn't attack target minion %s since it's dead already")
				continue
			else:
				PRINT(self.Game, "Player is dead and stops attacking minions")
				break
		if quaffTriggered: trig.disconnect()
		return None
		
class Trig_DrunkenBoxing(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["HeroAttackedMinion", "HeroAttackedHero"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject == self.entity.Game.heroes[self.entity.ID]
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		heal = 3 * (2 ** self.entity.countHealDouble())
		PRINT(self.entity.Game, "Drunken Boxing restores %d Health the hero after it attacked."%heal)
		self.entity.restoresHealth(self.entity.Game.heroes[self.entity.ID], heal)
		
		
class OnimaActuary(Minion): #秘典宗精算师
	Class, race, name = "Monk", "", "Onima Actuary"
	mana, attack, health = 4, 5, 4
	index = "Classic~Monk~Minion~4~5~4~~Onima Actuary~Stealth"
	requireTarget, keyWord, description = False, "Stealth", "Stealth. After this attacks, your Hero Power costs (1) for the rest of the turn"
	#潜行。在该随从攻击后，本回合中你的英雄技能的法力值消耗为(1)点
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_OnimaActuary(self)]
		
class Trig_OnimaActuary(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["MinionAttackedMinion", "MinionAttackedHero"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject == self.entity
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self.entity.Game, "After %s attacks, player's Hero Power costs (1) for the rest of turn"%self.entity.name)
		tempAura = YourHeroPowerCosts1ThisTurn(self.entity.Game, self.entity.ID)
		self.entity.Game.Manas.PowerAuras.append(tempAura)
		tempAura.auraAppears()
		
class YourHeroPowerCosts1ThisTurn(TempManaEffect_Power):
	def __init__(self, Game, ID):
		self.Game, self.ID = Game, ID
		self.changeby, self.changeto = 0, 1
		self.temporary = True
		self.auraAffected = []
		
	def applicable(self, target):
		return target.ID == self.ID
		
	def selfCopy(self, game):
		return type(self)(game, self.ID)
		
		
class SpawnofXuen(Minion): #雪怒的子嗣
	#突袭。战吼：从你的牌库中发现一张法力值消耗为(1)的随从
	Class, race, name = "Monk", "Beast", "Spawn of Xuen"
	mana, attack, health = 5, 3, 5
	index = "Classic~Monk~Minion~5~3~5~Beast~Spawn of Xuen~Rush~Battlecry"
	requireTarget, keyWord, description = False, "Rush", "Rush. Battlecry: Discover a 1-Cost minion from your deck"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if curGame.turn == self.ID:
			if curGame.mode == 0:
				if curGame.picks:
					i = curGame.picks.pop(0)
					if i > -1:
						PRINT(curGame, "SpawnofXuen's battlecry lets player draw a 1-Cost minion from deck")
						curGame.Hand_Deck.drawCard(self.ID, i)
				else:
					oneCostMinions = [i for i, card in enumerate(curGame.Hand_Deck.decks[self.ID]) if card.type == "Minion" and card.mana == 1]
					if oneCostMinions:
						if "byOthers" in comment:
							PRINT(curGame, "Spawn of Xuen's battlecry lets player draw a random 1-Cost minion from deck")
							i = npchoice(oneCostMinions)
							curGame.picks.append(i)
							curGame.Hand_Deck.drawCard(self.ID, i)
						else:
							PRINT(curGame, "Spawn of Xuen's battlecry lets player discover a 1-Cost minion from deck")
							indices = npchoice(oneCostMinions, min(3, len(oneCostMinions)), replace=False)
							curGame.options = [curGame.Hand_Deck.decks[self.ID][i] for i in indices]
							curGame.Discover.startDiscover(self)
					else: curGame.picks.append(-1)
		return None
		
	def discoverDecided(self, option, pool=None):
		for i, card in enumerate(self.Game.Hand_Deck.decks[self.ID]):
			if card == option:
				self.Game.picks.append(i)
				self.Game.Hand_Deck.drawCard(self.ID, option)
		
		
#class QuickSip(Spell): #浅斟快饮
#	#随机将你的牌库中的一张牌的3张复制置入你的手牌。畅饮：改为从你的牌库中发现这张牌
#	Class, school, name = "Monk", "", "Quick Sip"
#	requireTarget, mana = False, 5
#	index = "Classic~Monk~Spell~5~Quick Sip~Quaff"
#	description = "Add 3 copies of a random card in your deck to your hand. Quaff: Discover the card instead"
#	def effCanTrig(self):
#		self.effectViable = (self.Game.Manas.manas[self.ID] == self.mana)
#		
#	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
#		if self.Game.Hand_Deck.decks[self.ID]:
#			if (posinHand == -2 or self.Game.Manas.manas[self.ID]) or "byOthers" in comment or len(self.Game.Hand_Deck.decks[self.ID]) == 1:
#				PRINT(self.Game, "Quick Sip adds 3 copies of a random card in player's deck to player's hand"%target.name)
#				card = npchoice(self.Game.Hand_Deck.decks[self.ID])
#				self.Game.Hand_Deck.addCardtoHand([card.selfCopy(self.ID) for i in range(3)], self.ID)
#			else: #Triggers Quaff
#				PRINT(self.Game, "Quick Sip's Quaff triggers and lets player discover a card from the deck to add 3 copies of it to player's hand")
#				self.Game.sendSignal("QuaffTriggered", self.ID, None, None, 0, "")
#				numCardsLeft = len(self.Game.Hand_Deck.decks[self.ID])
#				self.Game.options = npchoice(self.Game.Hand_Deck.decks[self.ID], min(3, numCardsLeft), replace=False)
#				self.Game.Discover.startDiscover(self)
#		return None
#		
#	def discoverDecided(self, option, pool=None):
#		PRINT(self.Game, "Quick Sip puts 3 copies of card %s into player's hand"%option.name)
#		self.Game.Hand_Deck.addCardtoHand([option.selfCopy(self.ID) for i in range(3)], self.ID)
#		
#		
class PawnofShaohao(Minion): #少昊的禁卫
	#突袭。风怒
	Class, race, name = "Monk", "", "Pawn of Shaohao"
	mana, attack, health = 4, 5, 3
	index = "Classic~Monk~Minion~4~5~3~~Pawn of Shaohao~Rush~Windfury"
	requireTarget, keyWord, description = False, "Rush,Windfury", "Rush, Windfury"
	
	
class ShaohaotheEmperor(Minion): #皇帝 少昊
	#其他友方角色只会成为你的法术或英雄技能的目标。战吼：获得潜行直到你的下个回合
	Class, race, name = "Monk", "", "Shaohao, the Emperor"
	mana, attack, health = 4, 3, 5
	index = "Classic~Monk~Minion~4~3~5~~Shaohao, the Emperor~Battlecry~Legendary"
	requireTarget, keyWord, description = False, "", "Other friendly characters can only be targeted by your spells or Hero Power. Battlecry: Gain Stealth until your next turn"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.auras["Has Aura"] = OtherFriendlyMinionsHaveEvasive(self)
		
	def applicable(self, target):
		return target != self
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		PRINT(self.Game, "Shaohao, the Emperor's battlecry give the minion Stealth until player's next turn")
		self.status["Temp Stealth"] += 1
		return None
		
class OtherFriendlyMinionsHaveEvasive(EffectAura):
	def __init__(self, entity):
		self.entity = entity
		self.signals, self.auraAffected = ["MinionAppears"], []
		self.keyWord = "Evasive"
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject.ID == self.entity.ID and subject != self.entity
		
	def applies(self, subject):
		if self.applicable(subject):
			Effect_Receiver(subject, self, "Enemy Evasive").effectStart()
			
	def selfCopy(self, recipient):
		return type(self)(recipient)
		
		
class InnerPeace(Spell): #平常心
#抽一张牌。如果你的生命值大于或等于15点，则为你的英雄恢复所有生命值
	Class, school, name = "Monk", "", "Inner Peace"
	requireTarget, mana = False, 6
	index = "Classic~Monk~Spell~6~Inner Peace"
	description = "Draw a card. If your Hero's Health is 15 or higher, fully heal your Hero"
	def effCanTrig(self):
		self.effectViable = self.Game.heroes[self.ID].health > 14
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		PRINT(self.Game, "Inner Peace is cast and lets player draw a card")
		self.Game.Hand_Deck.drawCard(self.ID)
		if self.Game.heroes[self.ID].health > 14:
			PRINT(self.Game, "Player's health is 15 or higher, and Inner Peace fully heals the player")
			heal = self.Game.heroes[self.ID].health_max * (2 ** self.countHealDouble())
			self.restoresHealth(self.Game.heroes[self.ID], heal)
		return None
		
		
class LotusHealer(Minion): #玉莲帮医者
	#当该随从受到攻击后，为所有友方角色恢复1点生命值
	Class, race, name = "Monk", "", "Lotus Healer"
	mana, attack, health = 6, 3, 7
	index = "Classic~Monk~Minion~6~3~7~~Lotus Healer~Taunt"
	requireTarget, keyWord, description = False, "Taunt", "Taunt. After this is attacked, restored 1 Health to all friendly minions"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_LotusHealer(self)]
		
class Trig_LotusHealer(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["MinionAttackedMinion", "HeroAttackedMinion"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and target == self.entity
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		heal = 1 * (2 ** self.entity.countHealDouble())
		PRINT(self.entity.Game, "After %s is attacked, it restores %d Health to all friendly minions"%(self.entity.name, heal))
		targets = self.entity.Game.minionsonBoard(self.entity.ID) + [self.entity.Game.heroes[self.entity.ID]]
		self.entity.restoresAOE(targets, [heal for minion in targets])
		
		
class RushingJadeWind(Spell): #碧玉疾风
	#对所有敌方随从造成等于敌方随从数的伤害
	Class, school, name = "Monk", "", "Rushing Jade Wind"
	requireTarget, mana = False, 6
	index = "Classic~Monk~Spell~6~Rushing Jade Wind"
	description = "Deal damage to all enemy minions equal to the number of enemy minions"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		targets = self.Game.minionsonBoard(3-self.ID)
		damage = (len(targets) + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		PRINT(self.Game, "Rushing Jade Wind deals %d damage to all enemy minions"%damage)
		self.dealsAOE(targets, [damage for minion in targets])
		return None
		
		
class KunLaiSummitZenAlchemist(Minion): #昆莱山禅师
	#在你的回合结束时，随从使一个攻击力大于或等于2的敌方随从的攻击力变为1
	Class, race, name = "Monk", "", "Kun-Lai Summit Zen Alchemist"
	mana, attack, health = 7, 7, 7
	index = "Classic~Monk~Minion~7~7~7~~Kun-Lai Summit Zen Alchemist"
	requireTarget, keyWord, description = False, "", "At the end of your turn, change the Attack of a random enemy minion with 1 or more Attack to 1"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_KunLaiSummitZenAlchemist(self)]
		
class Trig_KunLaiSummitZenAlchemist(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["TurnEnds"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		enemyMinions = []
		for minion in self.entity.Game.minionsonBoard(3-self.entity.ID):
			if minion.attack > 1: enemyMinions.append(minion)
		if enemyMinions:
			enemyMinion = npchoice(enemyMinions)
			PRINT(self.entity.Game, "At the end of turn, %s changes the Attack of random enemy minion %s to 1."%(self.entity.name, enemyMinion.name))
			enemyMinion.statReset(1, False)
			
			
class FistsoftheHeavens(Weapon): #诸天之拳
#风怒。本回合中，每当你的畅饮牌触发后，便获得+4攻击力；或者使一个敌方角色获得-4攻击力
	Class, name, description = "Monk", "Fists of the Heavens", "Windfury. After your Quaff triggers, gain +4 Attack this turn"
	mana, attack, durability = 8, 2, 4
	index = "Classic~Monk~Weapon~8~2~4~Fists of the Heavens~Windfury"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.keyWords["Windfury"] = 1
		self.trigsBoard = [Trig_FistsoftheHeavens(self)]
		
class Trig_FistsoftheHeavens(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["QuaffTriggered"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return ID == self.entity.ID and self.entity.onBoard
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self.entity.Game, "Player's Quaff triggers and %s gains +4 Durability."%self.entity.name)
		self.entity.Game.heroes[self.entity.ID].gainTempAttack(4)
		
		
class PandariaGuardian(Minion): #潘达利亚守护者
	#嘲讽。畅饮：获得+2生命值且无法成为法术或英雄技能的目标
	Class, race, name = "Monk", "", "Pandaria Guardian"
	mana, attack, health = 8, 6, 10
	index = "Classic~Monk~Minion~8~6~10~~Pandaria Guardian~Taunt~Quaff"
	requireTarget, keyWord, description = False, "Taunt", "Taunt. Quaff: Gain +2 Health and 'Can't be targeted by spells or Hero Powers'"
	def effCanTrig(self):
		self.effectViable = (self.Game.Manas.manas[self.ID] == self.mana)
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if posinHand > -2 and self.Game.Manas.manas[self.ID] == 0:
			PRINT(self.Game, "Pandaria Guardian's Quaff triggers and gives the minion +2 Health and 'Can't be targeted by spells or Hero Powers'")
			self.Game.sendSignal("QuaffTriggered", self.ID, None, None, 0, "")
			self.buffDebuff(0, 2)
			self.marks["Evasive"] += 1
		return None
		
		
class MonkDragonKeeper(Minion): #驭龙武僧
	#风怒，突袭。畅饮：获得嘲讽，以及“亡语：‘将该随从洗入你的牌库’”
	Class, race, name = "Monk", "", "Monk Dragon Keeper"
	mana, attack, health = 9, 4, 12
	index = "Classic~Monk~Minion~9~4~12~~Monk Dragon Keeper~Rush~Windfury~Quaff"
	requireTarget, keyWord, description = False, "Rush,Windfury", "Rush, Windfury. Quaff: Gain Taunt and 'Deathrattle: Shuffle this into your deck'"
	def effCanTrig(self):
		self.effectViable = (self.Game.Manas.manas[self.ID] == self.mana)
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if posinHand > -2 and self.Game.Manas.manas[self.ID] == 0:
			PRINT(self.Game, "Monk Dragon Keeper's Quaff triggers and gives the minion Taunt and 'Deathrattle: Shuffle this into your deck'")
			self.Game.sendSignal("QuaffTriggered", self.ID, None, None, 0, "")
			self.getsStatus("Taunt")
			trig = ShuffleThisintoYourDeck(self)
			self.deathrattles.append(trig)
			trig.connect()
		return None
		
class ShuffleThisintoYourDeck(Deathrattle_Minion):
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		#如果随从身上已经有其他区域移动扳机触发过，则这个扳机不能两次触发，检测条件为仍在随从列表中
		return target == self.entity and self.entity in self.entity.Game.minions[self.entity.ID]
		
	def trig(self, signal, ID, subject, target, number, comment, choice=0):
		if self.canTrig(signal, ID, subject, target, number, comment):
			PRINT(self.entity.Game, "Deathrattle: Shuffle this minion into your deck triggers")
			if self.entity.Game.GUI:
				self.entity.Game.GUI.deathrattleAni(self.entity)
			self.entity.Game.Counters.deathrattlesTriggered[self.entity.ID].append(ShuffleThisintoYourDeck)
			self.entity.Game.returnMiniontoDeck(self.entity, targetDeckID=self.entity.ID, initiatorID=self.entity.ID, deathrattlesStayArmed=True)
			
Monk_Indices = { #Hero and standard Hero Powers
				"Hero: Monk": Chen,
				"Monk~Basic Hero Power~2~WindWalker-Mistweaver": WindWalkerMistweaver,
				"Monk~Upgraded Hero Power~2~High WindWalker-Mistweaver": HighWindWalkerMistweaver,
				
				"Basic~Monk~Spell~0~Resuscitate": Resuscitate,
				"Basic~Monk~Minion~1~0~2~~Arch of the Temple~Taunt~Battlecry": ArchoftheTemple,
				"Basic~Monk~Minion~1~1~1~~Monk Attacker~Rush~Uncollectible": MonkAttacker,
				"Basic~Monk~Weapon~1~0~4~Cane with a Wine Gourd": CanewithaWineGourd,
				"Basic~Monk~Minion~1~1~3~~Monk's Apprentice": MonksApprentice,
				"Basic~Monk~Spell~1~Shaohao's Protection": ShaohaosProtection,
				"Basic~Monk~Spell~2~Effusive Mists": EffusiveMists,
				"Basic~Monk~Minion~2~1~4~~Swift Brewmaster": SwiftBrewmaster,
				"Basic~Monk~Spell~3~Provoke": Provoke,
				"Basic~Monk~Minion~3~1~4~~Sweeping Kick Fighter~Rush": SweepingKickFighter,
				"Basic~Monk~Minion~3~3~4~~Shado-Pan Wu Kao": ShadoPanWuKao,
				
				"Classic~Monk~Minion~1~0~4~~Wise Lorewalker Cho~Battlecry~Legendary": WiseLorewalkerCho,
				"Classic~Monk~Minion~1~1~1~Beast~Xuen, the White Tiger~Rush~Legendary": XuentheWhiteTiger_Mutable_1,
				"Classic~Monk~Minion~2~3~2~~Defense Technique Master~Taunt~Quaff": DefenseTechniqueMaster,
				"Classic~Monk~Spell~2~Transcendance": Transcendance,
				"Classic~Monk~Spell~2~Purifying Brew~Quaff": PurifyingBrew,
				"Classic~Monk~Spell~3~Liquor~Quaff": Liquor,
				"Classic~Monk~Spell~3~Stave Off": StaveOff,
				"Classic~Monk~Spell~3~Touch of Karma": TouchofKarma,
				"Classic~Monk~Spell~3~Spirit Tether": SpiritTether,
				"Classic~Monk~Minion~2~2~2~Beast~Tethered Golem~Taunt~Uncollectible": TetheredGolem,
				"Classic~Monk~Spell~4~Drunken Boxing~Quaff": DrunkenBoxing,
				"Classic~Monk~Minion~4~5~4~~Onima Actuary~Stealth": OnimaActuary,
				"Classic~Monk~Minion~5~3~5~Beast~Spawn of Xuen~Rush~Battlecry": SpawnofXuen,
				#"Classic~Monk~Spell~5~Quick Sip~Quaff": QuickSip,
				"Classic~Monk~Minion~4~5~3~~Pawn of Shaohao~Rush~Windfury": PawnofShaohao,
				"Classic~Monk~Minion~4~3~5~~Shaohao, the Emperor~Battlecry~Legendary": ShaohaotheEmperor,
				"Classic~Monk~Spell~6~Inner Peace": InnerPeace,
				"Classic~Monk~Minion~6~3~7~~Lotus Healer~Taunt": LotusHealer,
				"Classic~Monk~Spell~6~Rushing Jade Wind": RushingJadeWind,
				"Classic~Monk~Minion~7~7~7~~Kun-Lai Summit Zen Alchemist": KunLaiSummitZenAlchemist,
				"Classic~Monk~Weapon~8~2~4~Fists of the Heavens~Windfury": FistsoftheHeavens,
				"Classic~Monk~Minion~8~6~10~~Pandaria Guardian~Taunt~Quaff": PandariaGuardian,
				"Classic~Monk~Minion~9~4~12~~Monk Dragon Keeper~Rush~Windfury~Quaff": MonkDragonKeeper,
				
}