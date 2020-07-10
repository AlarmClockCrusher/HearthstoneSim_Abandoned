from CardTypes import *
from Triggers_Auras import *
from VariousHandlers import *

class WindWalkerMistweaver(HeroPower): #踏风织雾
	mana, name, requireTarget = 2, "WindWalker-Mistweaver", True
	index = "Monk~Basic Hero Power~2~WindWalker-Mistweaver"
	description = "Give a friendly character +1 Attack this turn; or give an enemy character -1 Attack" #在本回合中，使用一个友方角色获得+1攻击力；或者使一个敌方角色获得-1攻击力
	def effect(self, target=None, choice=0):
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
		
class HighWindWalkerMistweaver(HeroPower): #精进踏风织雾
	mana, name, requireTarget = 2, "High WindWalker-Mistweaver", True
	index = "Monk~Upgraded Hero Power~2~High WindWalker-Mistweaver"
	description = "Give a friendly character +2 Attack this turn; or give an enemy character -2 Attack" #在本回合中，使用一个友方角色获得+1攻击力；或者使一个敌方角色获得-1攻击力
	def effect(self, target=None, choice=0):
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
	Class, name = "Monk", "Resuscitate"
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
			self.Game.returnMiniontoHand(target, keepDeathrattlesRegistered=False)
		self.Game.Manas.restoreManaCrystal(1, self.ID)
		return target
		
		
class ArchoftheTemple(Minion): #禅院的牌坊
	Class, race, name = "Monk", "", "Arch of the Temple"
	mana, attack, health = 1, 0, 2
	index = "Basic~Monk~Minion~1~0~2~None~Arch of the Temple~Taunt~Battlecry"
	requireTarget, keyWord, description = False, "Taunt", "Taunt. Battlecry: Add two 1/1 Monks with Rush to your hand" #嘲讽。战吼：将两张1/1并具有突袭的武僧置入你的手牌
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		PRINT(self.Game, "Arch of the Templer's battlecry adds two 1/1 Monks with Rush to player's hand")
		self.Game.Hand_Deck.addCardtoHand([MonkAttacker, MonkAttacker], self.ID, "CreateUsingType")
		return None
		
class MonkAttacker(Minion): #武僧袭击者
	Class, race, name = "Monk", "", "Monk Attacker"
	mana, attack, health = 1, 1, 1
	index = "Basic~Monk~Minion~1~1~1~None~Monk Attacker~Rush~Uncollectible"
	requireTarget, keyWord, description = False, "Rush", "Rush"
	
	
class CanewithaWineGourd(Weapon): #带酒葫芦的杖子
	#每当你的英雄攻击后为其恢复3点生命值
	Class, name, description = "Monk", "Cane with a Wine Gourd", "After your Hero attacks, restore 3 Health to it"
	mana, attack, durability = 1, 0, 4
	index = "Basic~Monk~Weapon~1~0~4~Cane with a Wine Gourd"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_CanewithaWineGourd(self)]
		
class Trigger_CanewithaWineGourd(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["HeroAttackedMinion", "HeroAttackedHero"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return subject == self.entity.Game.heroes[self.entity.ID] and self.entity.onBoard
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		heal = 3 * (2 ** self.entity.countHealDouble())
		PRINT(self.entity.Game, "%s restores %d Health the hero after it attacked."%(self.entity.name, heal))
		self.entity.restoresHealth(self.entity.Game.heroes[self.entity.ID], heal)
		
		
class MonksApprentice(Minion):
	#当该随从的攻击力大于或等于2时，使其获得这突袭和风怒
	Class, race, name = "Monk", "", "Monk's Apprentice"
	mana, attack, health = 1, 1, 3
	index = "Basic~Monk~Minion~1~1~3~None~Monk's Apprentice"
	requireTarget, keyWord, description = False, "", "While this minion has 2 or more Attack, it has Rush and Windfury"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.auras["RushandWindfury"] = Aura_MonksApprentice(self)
		self.triggers["StatChanges"] = [self.handleStatChange]
		self.activated = False
		
	def handleStatChange(self):
		self.auras["RushandWindfury"].handleStatChange()
		
class Aura_MonksApprentice(AuraDealer_toMinion):
	def __init__(self, entity):
		self.entity = entity
		signals, self.auraAffected = [], []
		
	def auraAppears(self):
		pass
		
	def auraDisappears(self):
		pass
		
	def handleStatChange(self):
		if self.entity.onBoard:
			if self.entity.activated == False and self.entity.attack > 1:
				self.entity.activated = True
				HasAura_Receiver(self.entity, self, "Rush").effectStart()
				HasAura_Receiver(self.entity, self, "Windfury").effectStart()
			elif self.entity.activated and self.entity.attack < 2:
				self.entity.activated = False
				for entity, aura_Receiver in fixedList(self.auraAffected):
					aura_Receiver.effectClear()
					
	def selfCopy(self, recipientMinion): #The recipientMinion is the minion that deals the Aura.
		#func that checks if subject is applicable will be the new copy's function
		return type(self)(recipientMinion)
		
	def createCopy(self, recipientGame):
		#一个光环的注册可能需要注册多个扳机
		if self not in recipientGame.copiedObjs: #这个光环没有被复制过
			entityCopy = self.entity.createCopy(recipientGame)
			Copy = self.selfCopy(entityCopy)
			recipientGame.copiedObjs[self] = Copy
			for minion, aura_Receiver in self.auraAffected:
				minionCopy = minion.createCopy(recipientGame)
				if hasattr(aura_Receiver, "keyWord"):
					receiverIndex = minion.keyWordbyAura["Auras"].index(aura_Receiver)
					receiverCopy = minionCopy.keyWordbyAura["Auras"][receiverIndex]
				else: #不是关键字光环，而是buff光环
					receiverIndex = minion.statbyAura[2].index(aura_Receiver)
					receiverCopy = minionCopy.statbyAura[2][receiverIndex]
				receiverCopy.source = Copy #补上这个receiver的source
				Copy.auraAffected.append((minionCopy, receiverCopy))
			return Copy
		else:
			return recipientGame.copiedObjs[self]
			
			
class ShaohaosProtection(Spell): #少昊的保护
	#使一个友方随从获得+2生命值且无法成为法术或英雄技能的目标
	Class, name = "Monk", "Shaohao's Protection"
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
	Class, name = "Monk", "Effusive Mists"
	requireTarget, mana = False, 2
	index = "Basic~Monk~Spell~2~Effusive Mists"
	description = "Change the Attack of 2 random enemy minions to 1" #将两个随机敌方随从的攻击力变为1
	def available(self):
		return self.Game.minionsonBoard(3-self.ID)
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		minions = self.Game.minionsonBoard(3-self.ID)
		if len(minions) > 1:
			targets = npchoice(minions, 2, replace=False)
			PRINT(self.Game, "Effusive Mists changes the Attack of random enemy minions {} to 1".format(targets))
			for minion in targets:
				minion.statReset(1, False)
		elif len(minions) == 1:
			PRINT(self.Game, "Effusive Mists changes the Attack minion %s to 1"%minions[0].name)
			minions[0].statReset(1, False)
		return None
		
		
class SwiftBrewmaster(Minion): #迷踪的酒仙
	#你的英雄技能在触发畅饮时会同时指向目标和其相邻随从
	Class, race, name = "Monk", "", "Swift Brewmaster"
	mana, attack, health = 2, 1, 4
	index = "Basic~Monk~Minion~2~1~4~None~Swift Brewmaster"
	requireTarget, keyWord, description = False, "", "Your Hero Power also targets adjacent minions if it triggers Quaff"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_SwiftBrewmaster(self)]
		
class Trigger_SwiftBrewmaster(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["ManaCostPaid", "HeroUsedAbility"])
		self.activated = False
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		minion, game = self.entity, self.entity.Game
		if signal == "ManaCostPaid": return subject == game.powers[minion.ID] and not self.activated and game.Manas.manas[minion.ID] == 0
		else: return ID == self.entity.ID and self.activated
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		if signal == "ManaCostPaid":
			PRINT(self.entity.entity, "Player's Hero Power triggers Quaff and %s enables it to also target adjacent minions"%self.entity.name)
			self.entity.Game.status[self.entity.ID]["Power Sweep"] += 1
			self.activated = True
		else:
			self.entity.Game.status[self.entity.ID]["Power Sweep"] -= 1
			self.activated = False
			
			
class Provoke(Spell): #嚎镇八方
	#在本回合中，使一个友方角色获得+4攻击力；或者使一个敌方角色获得-4攻击力
	Class, name = "Monk", "Provoke"
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
	index = "Basic~Monk~Minion~3~1~4~None~Sweeping Kick Fighter~Rush"
	requireTarget, keyWord, description = False, "Rush", "Rush. Also damages minions next to whoever this attacks"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.marks["Sweep"] = 1
		
			
class ShadoPanWuKao(Minion): #影踪派悟道者
	#在你的英雄攻击后，获得潜行
	Class, race, name = "Monk", "", "Shado-Pan Wu Kao"
	mana, attack, health = 3, 3, 4
	index = "Basic~Monk~Minion~3~3~4~None~Shado-Pan Wu Kao"
	requireTarget, keyWord, description = False, "", "After your hero attacks, gain Stealth"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_ShadoPanWuKao(self)]
		
class Trigger_ShadoPanWuKao(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["HeroAttackedMinion", "HeroAttackedHero"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject == self.entity.Game.heroes[self.entity.ID]
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self.entity.Game, "After friendly hero attacks, %s gains Stealth"%self.entity.name)
		self.entity.getsKeyword("Stealth")
		
		
"""Monk Classic Cards"""
class WiseLorewalkerCho(Minion): #睿智的游学者周卓
	#战吼：发现一张法力值消耗等同于你的法力水晶数量的其他职业的法术牌
	Class, race, name = "Monk", "", "Wise Lorewalker Cho"
	mana, attack, health = 1, 0, 4
	index = "Classic~Monk~Minion~1~0~4~None~Wise Lorewalker Cho~Battlecry~Legendary"
	requireTarget, keyWord, description = False, "", "Battlecry: Discover a spell from another class with Cost equal to your remaining Mana Crystals"
	poolIdentifier = "0-Cost Spells"
	@classmethod
	def generatePool(cls, Game):
		costs, lists = [], []
		for cost in range(11):
			spells, cond = [], "~Spell~%d~"%cost
			for Class in Game.Classes:
				for key, value in Game.ClassCards[Class].items():
					if cond in key:
						spells.append(value)
			costs.append("%d-Cost Spells"%cost)
			lists.append(spells)
		return costs, lists
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if self.Game.Hand_Deck.handNotFull(self.ID) and self.ID == self.Game.turn:
			Class = "Monk" if self.Game.heroes[self.ID].Class == "Neutral" else self.Game.heroes[self.ID].Class
			#需要把所有的职业捋一遍，出一个dict
			mana = self.Game.Manas.manas[self.ID]
			spells, pool = {}, self.Game.RNGPools["%d-Cost Spells"%mana]
			for spell in pool:
				if spell.Class in spells: spells[spell.Class].append(spell)
				else: spells[spell.Class] = [spell]
			if "byOthers" in comment:
				card = npchoice(npchoice(list(spells.keys())))
				PRINT(self.Game, "Wise Lorewalker Cho's battlecry adds a random spell from another class with cost equal player's remain mana to player's hand")
				self.Game.Hand_Deck.addCardtoHand(card, self.ID, "CreateUsingType")
			else:
				classes = list(spells.keys())
				classes = npchoice(classes, min(3, len(classes)), replace=False)
				for Class in classes:
					self.Game.options.append(npchoice(spells[Class])(self.Game, self.ID))
				PRINT(self.Game, "Wise Lorewalker Cho's battlecry lets player discover a Dragon")
				self.Game.Discover.startDiscover(self, None)
		return None
		
	def discoverDecided(self, option, info):
		PRINT(self.Game, "Spell %s is added to player's hand"%option.name)
		self.Game.Hand_Deck.addCardtoHand(option, self.ID)
		self.Game.sendSignal("DiscoveredCardPutintoHand", self.ID, self, option, 0, "")
		
		
class XuentheWhiteTiger_Mutable_1(Minion): #白虎 雪怒
	#突袭。在你使用一张牌后，将该随从移回你的手牌。并使其永久获得+2/+2和法力值消耗增加(1)点(最高不超过10点)。
	Class, race, name = "Monk", "Beast", "Xuen, the White Tiger"
	mana, attack, health = 1, 1, 1
	index = "Classic~Monk~Minion~1~1~1~Beast~Xuen, the White Tiger~Rush~Legendary"
	requireTarget, keyWord, description = False, "Rush", "Rush. After you play a card, return this to your hand and give it +2/+2 for the rest of the game. It costs (1) more(up to 10)"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_XuentheWhiteTiger(self)]
		
class Trigger_XuentheWhiteTiger(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionBeenPlayed", "SpellBeenPlayed", "WeaponBeenPlayed", "HeroCardBeenPlayed"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject.ID == self.entity.ID and subject != self.entity
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		minion = self.entity
		PRINT(minion.entity.Game, "Player played a card and %s returns itself to player's hand. It gain +2/+2 and costs (1) more permanently."%minion.name)
		if minion.Game.returnMiniontoHand(minion, keepDeathrattlesRegistered=False):
			cost = type(minion).mana + 1
			stat = cost * 2 - 1
			newIndex = "Classic~Monk~Minion~%d~%d~%d~Beast~Xuen, the White Tiger~Rush~Legendary~Uncollectible"%(cost, stat, stat)
			subclass = type("XuentheWhiteTiger_Mutable_%d"%cost, (XuentheWhiteTiger_Mutable_1, ),
						{"mana": cost, "attack": stat, "health": stat, "index": newIndex}
						)
			minion.Game.cardPool[newIndex] = subclass
			minion.Game.transform(minion, subclass(minion.Game, minion.ID))
			
			
class DefenseTechniqueMaster(Minion): #御术僧师
	#嘲讽。畅饮：获得‘亡语：本回合中，在使你的英雄获得+3攻击力’
	Class, race, name = "Monk", "", "Defense Technique Master"
	mana, attack, health = 2, 3, 2
	index = "Classic~Monk~Minion~2~3~2~None~Defense Technique Master~Taunt~Quaff"
	requireTarget, keyWord, description = False, "Taunt", "Taunt. Quaff: Gain 'Deathrattle: Give your hero +3 Attack this turn'"
	
	def effectCanTrigger(self):
		self.effectViable = (self.Game.Manas.manas[self.ID] == self.mana)
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if posinHand > -2 and not self.Game.Manas.manas[self.ID]:
			PRINT(self.Game, "Defense Technique Master's Quaff triggers and gives the minion 'Deathrattle: Give your hero +3 Attack this turn'")
			self.Game.sendSignal("QuaffTriggered", self.ID, None, None, 0, "")
			trigger = GiveYourHeroPlus3AttackThisTurn(self)
			self.deathrattles.append(trigger)
			if self.onBoard:
				trigger.connect()
		return None
		
class GiveYourHeroPlus3AttackThisTurn(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self.entity.Game, "Deathrattle: Give your hero +3 Attack this turn triggers.")
		self.entity.Game.heroes[self.entity.ID].gainTempAttack(3)
		
		
class PurifyingBrew(Spell): #活血酒
	Class, name = "Monk", "Purifying Brew"
	requireTarget, mana = False, 2
	index = "Classic~Monk~Spell~2~Purifying Brew~Quaff"
	description = "Draw a card. Quaff: Add a copy of it to your hand" #抽一张牌。畅饮： 复制该牌并置入你的手牌
	def effectCanTrigger(self):
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
	Class, name = "Monk", "Transcendance"
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
	Class, name = "Monk", "Liquor"
	requireTarget, mana = True, 3
	index = "Classic~Monk~Spell~3~Liquor~Quaff"
	description = "Target a minion. It can't attack for two turns. Quaff: Destroy it" #使一个随从两个回合无法攻击。畅饮：消灭该随从
	def effectCanTrigger(self):
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
				target.dead = True
			elif target.onBoard: #假设只有当目标随从还在场上的时候会生效
				PRINT(self.Game, "Liquor gives renders minion %s unable to attack for two turns"%target.name)
				target.marks["Can't Attack"] += 1
				trigger = Trigger_Liquor(target)
				target.triggersonBoard.append(trigger)
				trigger.connect()
		return target
		
class Trigger_Liquor(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["TurnEnds"])
		self.temp = True
		self.counter = 2
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.counter -= 1
		if self.counter < 1:
			PRINT(self.entity.Game, "%s can attack next turn."%self.entity.name)
			self.entity.marks["Can't Attack"] -= 1
			self.disconnect()
			extractfrom(self, self.entity.triggersonBoard)
		else:
			PRINT(self.entity.Game, "%s still can't attack for another turn"%self.entity.name)
			
	#一些扳机的counter可以随复制保留，但是Chenvaala在游戏内复制时，的counter不能保留
	def selfCopy(self, recipient):
		trig = type(self)(recipient)
		trig.counter = self.counter
		return trig
		
		
class StaveOff(Spell): #酒不离手
	Class, name = "Monk", "Stave Off"
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
	Class, name = "Monk", "Touch of Karma"
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
			self.Game.DmgHandler.scapegoatforHero[self.ID] = target
			trigger = Trigger_TouchofKarma(target, self.ID)
			target.triggersonBoard.append(trigger)
			if target.onBoard:
				trigger.connect()
		return target
		

class Trigger_TouchofKarma(TriggeronBoard):
	def __init__(self, entity, ID):
		self.blank_init(entity, ["TurnEnds"])
		self.ID = ID
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return True #不需要随从在场上，即使在手牌中也会过期
		
	def connect(self):
		for signal in self.signals:
			self.entity.Game.triggersonBoard[self.entity.ID].append((self, signal))
		self.entity.Game.DmgHandler.scapegoatforHero[self.ID] = self.entity
		
	def disconnect(self):
		for signal in self.signals:
			extractfrom((self, signal), self.entity.Game.triggersonBoard[self.entity.ID])
		if self.entity.Game.DmgHandler.scapegoatforHero[self.ID] == self.entity:
			self.entity.Game.DmgHandler.scapegoatforHero[self.ID] = None
			
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self.entity.Game, "At the end of turn, minion %s no longer intercepts damage on player %d."%(self.entity.name, self.ID))
		self.disconnect()
		extractfrom(self, self.entity.triggersonBoard)
		
	def selfCopy(self, recipient):
		return type(self)(recipient, self.ID)
		
		
class SpiritTether(Spell): #魂体束缚
	#将你的英雄技能替换为“使一个随从变形为2/2并具有嘲讽的魔像”。使用两次后，替换为原技能
	Class, name = "Monk", "Spirit Tether"
	requireTarget, mana = False, 3
	index = "Classic~Monk~Spell~3~Spirit Tether"
	description = "Swap your Hero Power to 'Transform a minion into a 2/2 Golem with Taunt'. After 2 uses, swap it back"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		PRINT(self.Game, "Metamorphosis is cast and swaps player's Hero Power to 'Deal 5 damage'. After 2 uses, swap it back")
		JadeTether(self.Game, self.ID).replaceHeroPower()
		return None
		
class JadeTether(HeroPower):
	mana, name, requireTarget = 2, "Jade Tether", True
	index = "Monk~Hero Power~2~Jade Tether"
	description = "Transform a minion into a 2/2 Golem with Taunt"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_JadeTether(self)]
		self.progress = 0
		self.heroPowerReplaced = None
		
	def effect(self, target, choice=0):
		if target:
			PRINT(self.Game, "Hero Power Jade Tether transforms %s into a 2/2 Golem with Taunt"%target.name)
			newMinion = TetheredGolem(self.Game, target.ID)
			self.Game.transform(target, newMinion)
			target = newMinion
		return 0
		
	def replaceHeroPower(self):
		self.heroPowerReplaced = type(self.Game.powers[self.ID])
		if self.Game.powers[self.ID]:
			self.Game.powers[self.ID].disappears()
			self.Game.powers[self.ID] = None
		self.Game.powers[self.ID] = self
		self.appears()
		
class Trigger_JadeTether(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["HeroUsedAbility"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return subject == self.entity
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.progress += 1
		PRINT(self.entity.Game, "Player uses Hero Power and Jade Tether has been used for %d times"%self.entity.progress)
		if self.entity.progress > 1:
			PRINT(self.entity.Game, "Player has used Hero Power Jade Tether twice and the Hero Power changes back to the original one it replaced")
			if self.entity.heroPowerReplaced:
				self.entity.heroPowerReplaced(self.entity.Game, self.entity.ID).replaceHeroPower()
				self.disconnect()
				
class TetheredGolem(Minion): #雪怒的子嗣
	#突袭。战吼：从你的牌库中发现一张法力值消耗为(1)的随从
	Class, race, name = "Monk", "", "Tethered Golem"
	mana, attack, health = 2, 2, 2
	index = "Classic~Monk~Minion~2~2~2~Beast~Tethered Golem~Taunt~Uncollectible"
	requireTarget, keyWord, description = False, "Taunt", "Taunt"
	
	
class DrunkenBoxing(Spell): #醉拳
	#在本回合中，使你的英雄获得+5攻击力，随机攻击所有随从。畅饮：每次攻击后，为你的英雄恢复3点生命值
	Class, name = "Monk", "Drunken Boxing"
	requireTarget, mana = False, 4
	index = "Classic~Monk~Spell~4~Drunken Boxing~Quaff"
	description = "Your Hero gains +5 Attack this turn and randomly attacks all minions. Quaff:　Restore 3 Health to your Hero after each attack"
	def effectCanTrigger(self):
		self.effectViable = (self.Game.Manas.manas[self.ID] == self.mana)
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		PRINT(self.Game, "Drunken Boxing gives player +5 Attack this turn. It randomly attacks all minions")
		hero = self.Game.heroes[self.ID]
		hero.gainTempAttack(5)
		quaffTriggered = (posinHand > -2 and self.Game.Manas.manas[self.ID] == 0)
		minionstoAttack = self.Game.minionsonBoard(1) + self.Game.minionsonBoard(2)
		npshuffle(minionstoAttack)
		if quaffTriggered:
			trigger = Trigger_DrunkenBoxing(self)
			trigger.connect()
			self.Game.sendSignal("QuaffTriggered", self.ID, None, None, 0, "")
		#注册扳机，检测英雄的攻击
		while minionstoAttack:
			attackTarget = minionstoAttack.pop()
			if attackTarget.health > 0 and not attackTarget.dead and hero.health > 0 and not hero.dead:
				PRINT(self.Game, "Drunken Boxing lets player attack minion %s"%attackTarget.name)
				#def battle(self, subject, target, verifySelectable=True, consumeAttackChance=True, resolveDeath=True, resetRedirectionTriggers=True)
				self.Game.battle(hero, attackTarget, False, True, False, False)
				self.Game.triggersonBoard[self.ID]
			elif attackTarget.health < 0 or attackTarget.dead:
				PRINT(self.Game, "Player doesn't attack target minion %s since it's dead already")
				continue
			else:
				PRINT(self.Game, "Player is dead and stops attacking minions")
				break
		if quaffTriggered: trigger.disconnect()
		return None
		
class Trigger_DrunkenBoxing(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["HeroAttackedMinion", "HeroAttackedHero"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return subject == self.entity.Game.heroes[self.entity.ID]
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		heal = 3 * (2 ** self.entity.countHealDouble())
		PRINT(self.entity.Game, "Drunken Boxing restores %d Health the hero after it attacked."%heal)
		self.entity.restoresHealth(self.entity.Game.heroes[self.entity.ID], heal)
		
		
class OnimaActuary(Minion): #秘典宗精算师
	Class, race, name = "Monk", "", "Onima Actuary"
	mana, attack, health = 4, 5, 4
	index = "Classic~Monk~Minion~4~5~4~Monk~Onima Actuary~Stealth"
	requireTarget, keyWord, description = False, "Stealth", "Stealth. After this attacks, your Hero Power costs (1) for the rest of the turn"
	#潜行。在该随从攻击后，本回合中你的英雄技能的法力值消耗为(1)点
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_OnimaActuary(self)]
		
class Trigger_OnimaActuary(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionAttackedMinion", "MinionAttackedHero"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
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
		
	def selfCopy(self, recipientGame):
		return type(self)(recipientGame, self.ID)
		
		
class SpawnofXuen(Minion): #雪怒的子嗣
	#突袭。战吼：从你的牌库中发现一张法力值消耗为(1)的随从
	Class, race, name = "Monk", "Beast", "Spawn of Xuen"
	mana, attack, health = 5, 3, 5
	index = "Classic~Monk~Minion~5~3~5~Beast~Spawn of Xuen~Rush~Battlecry"
	requireTarget, keyWord, description = False, "Rush", "Rush. Battlecry: Discover a 1-Cost minion from your deck"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		hdHandler = self.Game.Hand_Deck
		if hdHandler.handNotFull(self.ID) and self.Game.turn == self.ID:
			oneCostMinions = []
			for card in hdHandler.decks[self.ID]:
				if card.mana == 1 and card.type == "Minion": oneCostMinions.append(card)
			if oneCostMinions:
				if "byOthers" in comment or len(oneCostMinions) < 2:
					PRINT(self.Game, "Spawn of Xuen's battlecry lets player draw a random 1-Cost minion from deck")
					minion = npchoice(oneCostMinions)
					self.Game.Hand_Deck.drawCard(self.ID, minion)
				else:
					PRINT(self.Game, "Spawn of Xuen's battlecry lets player discover a 1-Cost minion from deck")
					self.Game.options = npchoice(oneCostMinions, min(3, len(oneCostMinions)), replace=False)
					self.Game.Discover.startDiscover(self, None)
			else: PRINT(self.Game, "No 1-Cost minion in deck. Spawn of Xuen's battlecry has no effect")
		return None
		
	def discoverDecided(self, option, info):
		PRINT(self.Game, "Player draws 1-Cost minion %s"%option.name)
		self.Game.Hand_Deck.drawCard(self.ID, option)
		
		
class QuickSip(Spell): #浅斟快饮
	#随机将你的牌库中的一张牌的3张复制置入你的手牌。畅饮：改为从你的牌库中发现这张牌
	Class, name = "Monk", "Quick Sip"
	requireTarget, mana = False, 5
	index = "Classic~Monk~Spell~5~Quick Sip~Quaff"
	description = "Add 3 copies of a random card in your deck to your hand. Quaff: Discover the card instead"
	def effectCanTrigger(self):
		self.effectViable = (self.Game.Manas.manas[self.ID] == self.mana)
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if self.Game.Hand_Deck.decks[self.ID]:
			if (posinHand == -2 or self.Game.Manas.manas[self.ID]) or "byOthers" in comment or len(self.Game.Hand_Deck.decks[self.ID]) == 1:
				PRINT(self.Game, "Quick Sip adds 3 copies of a random card in player's deck to player's hand"%target.name)
				card = npchoice(self.Game.Hand_Deck.decks[self.ID])
				self.Game.Hand_Deck.addCardtoHand([card.selfCopy(self.ID) for i in range(3)], self.ID)
			else: #Triggers Quaff
				PRINT(self.Game, "Quick Sip's Quaff triggers and lets player discover a card from the deck to add 3 copies of it to player's hand")
				self.Game.sendSignal("QuaffTriggered", self.ID, None, None, 0, "")
				numCardsLeft = len(self.Game.Hand_Deck.decks[self.ID])
				self.Game.options = npchoice(self.Game.Hand_Deck.decks[self.ID], min(3, numCardsLeft), replace=False)
				self.Game.Discover.startDiscover(self, None)
		return None
		
	def discoverDecided(self, option, info):
		PRINT(self.Game, "Quick Sip puts 3 copies of card %s into player's hand"%option.name)
		self.Game.Hand_Deck.addCardtoHand([option.selfCopy(self.ID) for i in range(3)], self.ID)
		
		
class PawnofShaohao(Minion): #少昊的禁卫
	#突袭。风怒
	Class, race, name = "Monk", "", "Pawn of Shaohao"
	mana, attack, health = 4, 5, 3
	index = "Classic~Monk~Minion~4~5~3~None~Pawn of Shaohao~Rush~Windfury"
	requireTarget, keyWord, description = False, "Rush,Windfury", "Rush, Windfury"
	
	
class ShaohaotheEmperor(Minion): #皇帝 少昊
	#其他友方角色只会成为你的法术或英雄技能的目标。战吼：获得潜行直到你的下个回合
	Class, race, name = "Monk", "", "Shaohao, the Emperor"
	mana, attack, health = 4, 3, 5
	index = "Classic~Monk~Minion~4~3~5~None~Shaohao, the Emperor~Battlecry~Legendary"
	requireTarget, keyWord, description = False, "", "Other friendly characters can only be targeted by your spells or Hero Power. Battlecry: Gain Stealth until your next turn"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.auras["Has Aura"] = OtherFriendlyMinionsHaveEvasive(self)
		
	def applicable(self, target):
		return target != self
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		PRINT(self.Game, "Shaohao, the Emperor's battlecry give the minion Stealth until player's next turn")
		self.status["Temp Stealth"] += 1
		return None
		
class OtherFriendlyMinionsHaveEvasive(HasAura_Dealer):
	def __init__(self, entity):
		self.entity = entity
		self.signals, self.auraAffected = ["MinionAppears"], []
		self.keyWord = "Evasive"
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject.ID == self.entity.ID and subject != self.entity
		
	def applies(self, subject):
		if self.applicable(subject):
			aura_Receiver = HasEvasive_Receiver(subject, self)
			aura_Receiver.effectStart()
			
	def selfCopy(self, recipient):
		return type(self)(recipient)
		
class HasEvasive_Receiver:
	def __init__(self, receiver, source):
		self.source = source #The aura.
		self.receiver = receiver #The minion that is affected
		self.keyWord = "Evasive"
		
	def effectStart(self):
		if "Evasive" in self.receiver.keyWordbyAura:
			self.receiver.keyWordbyAura["Evasive"] += 1
		else: self.receiver.keyWordbyAura["Evasive"] = 1
		self.receiver.marks["Evasive"] += 1
		self.receiver.keyWordbyAura["Auras"].append(self)
		self.source.auraAffected.append((self.receiver, self))
		
	#The aura on the receiver is cleared and the source will remove this receiver and aura_Receiver from it's list.
	def effectClear(self):
		if self.receiver.keyWordbyAura["Evasive"] > 0:
			self.receiver.keyWordbyAura["Evasive"] -= 1
		self.receiver.marks["Evasive"] -= 1
		extractfrom(self, self.receiver.keyWordbyAura["Auras"])
		extractfrom((self.receiver, self), self.source.auraAffected)
		
	#After a receiver is deep copied, it will also copy this aura_Receiver, simply remove it.
	#The aura_Dealer won't have reference to this copied aura.
	def effectDiscard(self):
		if self.receiver.keyWordbyAura["Evasive"] > 0:
			self.receiver.keyWordbyAura["Evasive"] -= 1
			self.receiver.marks["Evasive"] -= 1
		extractfrom(self, self.receiver.keyWordbyAura["Auras"])
		
	def selfCopy(self, recipient):
		return type(self)(recipient, self.source)
		
		
class InnerPeace(Spell): #平常心
#抽一张牌。如果你的生命值大于或等于15点，则为你的英雄恢复所有生命值
	Class, name = "Monk", "Inner Peace"
	requireTarget, mana = False, 6
	index = "Classic~Monk~Spell~6~Inner Peace"
	description = "Draw a card. If your Hero's Health is 15 or higher, fully heal your Hero"
	def effectCanTrigger(self):
		self.effectViable = self.Game.heroes[self.ID].health > 14
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		PRINT(self.Game, "Inner Peace is cast and lets player draw a card")
		self.Game.Hand_Deck.drawCard(self.ID)
		if self.Game.heroes[self.ID].health > 14:
			PRINT(self.Game, "Player's health is 15 or higher, and Inner Peace fully heals the player")
			heal = self.Game.heroes[self.ID].health_upper * (2 ** self.countHealDouble())
			self.restoresHealth(self.Game.heroes[self.ID], heal)
		return None
		
		
class LotusHealer(Minion): #玉莲帮医者
	#当该随从受到攻击后，为所有友方角色恢复1点生命值
	Class, race, name = "Monk", "", "Lotus Healer"
	mana, attack, health = 6, 3, 7
	index = "Classic~Monk~Minion~6~3~7~None~Lotus Healer~Taunt"
	requireTarget, keyWord, description = False, "Taunt", "Taunt. After this is attacked, restored 1 Health to all friendly minions"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_LotusHealer(self)]
		
class Trigger_LotusHealer(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionAttackedMinion", "HeroAttackedMinion"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and target == self.entity
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		heal = 1 * (2 ** self.entity.countHealDouble())
		PRINT(self.entity.Game, "After %s is attacked, it restores %d Health to all friendly minions"%(self.entity.name, heal))
		targets = self.entity.Game.minionsonBoard(self.entity.ID) + [self.entity.Game.heroes[self.entity.ID]]
		self.entity.restoresAOE(targets, [heal for minion in targets])
		
		
class RushingJadeWind(Spell): #碧玉疾风
	#对所有敌方随从造成等于敌方随从数的伤害
	Class, name = "Monk", "Rushing Jade Wind"
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
	index = "Classic~Monk~Minion~7~7~7~None~Kun-Lai Summit Zen Alchemist"
	requireTarget, keyWord, description = False, "", "At the end of your turn, change the Attack of a random enemy minion with 1 or more Attack to 1"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_KunLaiSummitZenAlchemist(self)]
		
class Trigger_KunLaiSummitZenAlchemist(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["TurnEnds"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
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
		self.blank_init(Game, ID)
		self.keyWords["Windfury"] = 1
		self.triggersonBoard = [Trigger_FistsoftheHeavens(self)]
		
class Trigger_FistsoftheHeavens(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["QuaffTriggered"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return ID == self.entity.ID and self.entity.onBoard
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self.entity.Game, "Player's Quaff triggers and %s gains +4 Durability."%self.entity.name)
		self.entity.Game.heroes[self.entity.ID].gainTempAttack(4)
		
			
class PandariaGuardian(Minion): #潘达利亚守护者
	#嘲讽。畅饮：获得+2生命值且无法成为法术或英雄技能的目标
	Class, race, name = "Monk", "", "Pandaria Guardian"
	mana, attack, health = 8, 6, 10
	index = "Classic~Monk~Minion~8~6~10~None~Pandaria Guardian~Taunt~Quaff"
	requireTarget, keyWord, description = False, "Taunt", "Taunt. Quaff: Gain +2 Health and 'Can't be targeted by spells or Hero Powers'"
	def effectCanTrigger(self):
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
	index = "Classic~Monk~Minion~9~4~12~None~Monk Dragon Keeper~Rush~Windfury~Quaff"
	requireTarget, keyWord, description = False, "Rush,Windfury", "Rush, Windfury. Quaff: Gain Taunt and 'Deathrattle: Shuffle this into your deck'"
	def effectCanTrigger(self):
		self.effectViable = (self.Game.Manas.manas[self.ID] == self.mana)
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if posinHand > -2 and self.Game.Manas.manas[self.ID] == 0:
			PRINT(self.Game, "Monk Dragon Keeper's Quaff triggers and gives the minion Taunt and 'Deathrattle: Shuffle this into your deck'")
			self.Game.sendSignal("QuaffTriggered", self.ID, None, None, 0, "")
			self.getsKeyword("Taunt")
			trigger = ShuffleThisintoYourDeck(self)
			self.deathrattles.append(trigger)
			trigger.connect()
		return None
		
class ShuffleThisintoYourDeck(Deathrattle_Minion):
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		#如果随从身上已经有其他区域移动扳机触发过，则这个扳机不能两次触发，检测条件为仍在随从列表中
		return target == self.entity and self.entity in self.entity.Game.minions[self.entity.ID]
		
	def trigger(self, signal, ID, subject, target, number, comment, choice=0):
		if self.canTrigger(signal, ID, subject, target, number, comment):
			PRINT(self.entity.Game, "Deathrattle: Shuffle this minion into your deck triggers")
			if self.entity.Game.withAnimation:
				self.entity.Game.GUI.triggerBlink(self.entity)
			self.entity.Game.returnMiniontoDeck(self.entity, targetDeckID=self.entity.ID, initiatorID=self.entity.ID, keepDeathrattlesRegistered=True)
			
Monk_Indices = { #Hero and standard Hero Powers
				"Hero: Monk": Chen,
				"Monk~Basic Hero Power~2~WindWalker-Mistweaver": WindWalkerMistweaver,
				"Monk~Upgraded Hero Power~2~High WindWalker-Mistweaver": HighWindWalkerMistweaver,
				
				"Basic~Monk~Spell~0~Resuscitate": Resuscitate,
				"Basic~Monk~Minion~1~0~2~None~Arch of the Temple~Taunt~Battlecry": ArchoftheTemple,
				"Basic~Monk~Minion~1~1~1~None~Monk Attacker~Rush~Uncollectible": MonkAttacker,
				"Basic~Monk~Weapon~1~0~4~Cane with a Wine Gourd": CanewithaWineGourd,
				"Basic~Monk~Minion~1~1~3~None~Monk's Apprentice": MonksApprentice,
				"Basic~Monk~Spell~1~Shaohao's Protection": ShaohaosProtection,
				"Basic~Monk~Spell~2~Effusive Mists": EffusiveMists,
				"Basic~Monk~Minion~2~1~4~None~Swift Brewmaster": SwiftBrewmaster,
				"Basic~Monk~Spell~3~Provoke": Provoke,
				"Basic~Monk~Minion~3~1~4~None~Sweeping Kick Fighter~Rush": SweepingKickFighter,
				"Basic~Monk~Minion~3~3~4~None~Shado-Pan Wu Kao": ShadoPanWuKao,
				
				"Classic~Monk~Minion~1~0~4~None~Wise Lorewalker Cho~Battlecry~Legendary": WiseLorewalkerCho,
				"Classic~Monk~Minion~1~1~1~Beast~Xuen, the White Tiger~Rush~Legendary": XuentheWhiteTiger_Mutable_1,
				"Classic~Monk~Minion~2~2~3~None~Defense Technique Master~Taunt~Quaff": DefenseTechniqueMaster,
				"Classic~Monk~Spell~2~Transcendance": Transcendance,
				"Classic~Monk~Spell~2~Purifying Brew~Quaff": PurifyingBrew,
				"Classic~Monk~Spell~3~Liquor~Quaff": Liquor,
				"Classic~Monk~Spell~3~Stave Off": StaveOff,
				"Classic~Monk~Spell~3~Touch of Karma": TouchofKarma,
				"Classic~Monk~Spell~3~Spirit Tether": SpiritTether,
				"Classic~Monk~Minion~2~2~2~Beast~Tethered Golem~Taunt~Uncollectible": TetheredGolem,
				"Classic~Monk~Spell~4~Drunken Boxing": DrunkenBoxing,
				"Classic~Monk~Minion~4~5~4~Monk~Onima Actuary~Stealth": OnimaActuary,
				"Classic~Monk~Minion~5~3~5~Beast~Spawn of Xuen~Rush~Battlecry": SpawnofXuen,
				"Classic~Monk~Spell~5~Quick Sip~Quaff": QuickSip,
				"Classic~Monk~Minion~4~5~3~None~Pawn of Shaohao~Rush~Windfury": PawnofShaohao,
				"Classic~Monk~Minion~4~3~5~None~Shaohao, the Emperor~Battlecry~Legendary": ShaohaotheEmperor,
				"Classic~Monk~Spell~6~Inner Peace": InnerPeace,
				"Classic~Monk~Minion~6~3~7~None~Lotus Healer~Taunt": LotusHealer,
				"Classic~Monk~Spell~6~Rushing Jade Wind": RushingJadeWind,
				"Classic~Monk~Minion~7~7~7~None~Kun-Lai Summit Zen Alchemist": KunLaiSummitZenAlchemist,
				"Classic~Monk~Weapon~8~2~4~Fists of the Heavens~Windfury": FistsoftheHeavens,
				"Classic~Monk~Minion~8~6~10~None~Pandaria Guardian~Taunt~Quaff": PandariaGuardian,
				"Classic~Monk~Minion~9~4~12~None~Monk Dragon Keeper~Rush~Windfury~Quaff": MonkDragonKeeper,
				
}