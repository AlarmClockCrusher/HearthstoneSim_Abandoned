from CardTypes import *
from Triggers_Auras import *
from numpy.random import choice as npchoice
from numpy.random import randint as nprandint
from numpy.random import shuffle as npshuffle
from numpy import inf as npinf

from AcrossPacks import TheCoin, MurlocScout
from Classic import PatientAssassin
from AcrossPacks import *

import copy

"""Rise of Shadows"""

"""Mana 1 cards"""
class PotionVendor(Minion):
	Class, race, name = "Neutral", "", "Potion Vendor"
	mana, attack, health = 1, 1, 1
	index = "DALARAN~Neutral~Minion~1~1~1~~Potion Vendor~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Restore 2 Health to all friendly characters"
	name_CN = "药水商人"
	def text(self, CHN):
		heal = 2 * (2 ** self.countHealDouble())
		return "战吼：为所有友方角色恢复%d点生命值"%heal if CHN else "Battlecry: Restore %d Health to all friendly characters"%heal
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		heal = 2 * (2 ** self.countHealDouble())
		targets = [self.Game.heroes[self.ID]] + self.Game.minions[self.ID]
		self.restoresAOE(targets, [heal] * len(targets))
		return None
		
		
class Toxfin(Minion):
	Class, race, name = "Neutral", "Murloc", "Toxfin"
	mana, attack, health = 1, 1, 2
	index = "DALARAN~Neutral~Minion~1~1~2~Murloc~Toxfin~Battlecry"
	requireTarget, keyWord, description = True, "", "Battlecry: Give a friendly Murloc Poisonous"
	name_CN = "毒鳍鱼人"
	
	def targetExists(self, choice=0):
		return self.selectableFriendlyMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and "Murloc" in target.race and target.ID == self.ID and target != self and target.onBoard
		
	def effCanTrig(self):
		self.effectViable = any("Murloc" in minion.race for minion in self.Game.minionsonBoard(self.ID))
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			target.getsKeyword("Poisonous")
		return target
		

"""Mana 2 cards"""
class ArcaneServant(Minion):
	Class, race, name = "Neutral", "Elemental", "Arcane Servant"
	mana, attack, health = 2, 2, 3
	index = "DALARAN~Neutral~Minion~2~2~3~Elemental~Arcane Servant"
	requireTarget, keyWord, description = False, "", ""
	name_CN = "奥术仆从"
	
	
class DalaranLibrarian(Minion):
	Class, race, name = "Neutral", "", "Dalaran Librarian"
	mana, attack, health = 2, 2, 3
	index = "DALARAN~Neutral~Minion~2~2~3~~Dalaran Librarian~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Silences adjacent minions"
	name_CN = "达拉然 图书管理员"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if self.onBoard:
			for minion in self.Game.neighbors2(self)[0]:
				minion.getsSilenced()
		return None
		
		
class EVILCableRat(Minion):
	Class, race, name = "Neutral", "Beast", "EVIL Cable Rat"
	mana, attack, health = 2, 1, 1
	index = "DALARAN~Neutral~Minion~2~1~1~Beast~EVIL Cable Rat~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Add a Lackey to your hand"
	name_CN = "怪盗布缆鼠"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if curGame.mode == 0:
			if curGame.guides:
				lackey = curGame.guides.pop(0)
			else:
				lackey = npchoice(Lackeys)
				curGame.fixedGuides.append(lackey)
			curGame.Hand_Deck.addCardtoHand(lackey, self.ID, byType=True)
		return None
		
		
class HenchClanHogsteed(Minion):
	Class, race, name = "Neutral", "Beast", "Hench-Clan Hogsteed"
	mana, attack, health = 2, 2, 1
	index = "DALARAN~Neutral~Minion~2~2~1~Beast~Hench-Clan Hogsteed~Rush~Deathrattle"
	requireTarget, keyWord, description = False, "Rush", "Rush. Deathrattle: Summon a 1/1 Murloc"
	name_CN = "荆棘帮斗猪"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [SummonaHenchClanSquire(self)]
		
class SummonaHenchClanSquire(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.Game.summon(HenchClanSquire(self.entity.Game, self.entity.ID), self.entity.pos+1, self.entity)
		
	def text(self, CHN):
		return "亡语：召唤一个1/1的鱼人" if CHN else "Deathrattle: Summon a 1/1 Murloc"
		
class HenchClanSquire(Minion):
	Class, race, name = "Neutral", "Murloc", "Hench-Clan Squire"
	mana, attack, health = 1, 1, 1
	index = "DALARAN~Neutral~Minion~1~1~1~Murloc~Hench-Clan Squire~Uncollectible"
	requireTarget, keyWord, description = False, "", ""
	name_CN = "荆棘帮马仔"
	
	
class ManaReservoir(Minion):
	Class, race, name = "Neutral", "Elemental", "Mana Reservoir"
	mana, attack, health = 2, 0, 6
	index = "DALARAN~Neutral~Minion~2~0~6~Elemental~Mana Reservoir~Spell Damage"
	requireTarget, keyWord, description = False, "Spell Damage", "Spell Damage +1"
	name_CN = "法力之池"
	
	
class SpellbookBinder(Minion):
	Class, race, name = "Neutral", "", "Spellbook Binder"
	mana, attack, health = 2, 3, 2
	index = "DALARAN~Neutral~Minion~2~3~2~~Spellbook Binder~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: If you have Spell Damage, draw a card"
	name_CN = "魔法订书匠"
	
	def effCanTrig(self):
		self.effectViable = False
		if self.Game.status[self.ID]["Spell Damage"] > 0:
			self.effectViable = True
		else:
			for minion in self.Game.minionsonBoard(self.ID):
				if minion.keyWords["Spell Damage"] > 0:
					self.effectViable = True
					break
					
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		haveSpellDamage = False
		if self.Game.status[self.ID]["Spell Damage"] > 0:
			haveSpellDamage = True
		else:
			for minion in self.Game.minionsonBoard(self.ID):
				if minion.keyWords["Spell Damage"] > 0:
					haveSpellDamage = True
					break
					
		if haveSpellDamage:
			self.Game.Hand_Deck.drawCard(self.ID)
		return None
		
		
class SunreaverSpy(Minion):
	Class, race, name = "Neutral", "", "Sunreaver Spy"
	mana, attack, health = 2, 2, 3
	index = "DALARAN~Neutral~Minion~2~2~3~~Sunreaver Spy~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: If you control a Secret, gain +1/+1"
	name_CN = "夺日者间谍"
	
	def effCanTrig(self):
		self.effectViable = self.Game.Secrets.secrets[self.ID] != []
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if self.Game.Secrets.secrets[self.ID] != []:
			self.buffDebuff(1, 1)
		return None
		
class ZayleShadowCloak(Minion):
	Class, race, name = "Neutral", "", "Zayle, Shadow Cloak"
	mana, attack, health = 2, 3, 2
	index = "DALARAN~Neutral~Minion~2~3~2~~Zayle, Shadow Cloak~Legendary"
	requireTarget, keyWord, description = False, "", "You start the game with one of Zayle's EVIL Decks!"
	name_CN = "泽尔， 暗影斗篷"
	
"""Mana 3 cards"""
class ArcaneWatcher(Minion):
	Class, race, name = "Neutral", "", "Arcane Watcher"
	mana, attack, health = 3, 5, 6
	index = "DALARAN~Neutral~Minion~3~5~6~~Arcane Watcher"
	requireTarget, keyWord, description = False, "", "Can't attack unless you have Spell Damage"
	name_CN = "奥术守望者"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.marks["Can't Attack"] = 1
		
	def hasSpellDamage(self):
		return self.Game.status[self.ID]["Spell Damage"] > 0 \
				or any(minion.keyWords["Spell Damage"] > 0 for minion in self.Game.minions[self.ID])
				
	def canAttack(self):
		return self.actionable() and self.attack > 0 and self.status["Frozen"] < 1 \
				and self.attChances_base + self.attChances_extra <= self.attTimes \
				and (self.silenced or self.hasSpellDamage())
				
				
class FacelessRager(Minion):
	Class, race, name = "Neutral", "", "Faceless Rager"
	mana, attack, health = 3, 5, 1
	index = "DALARAN~Neutral~Minion~3~5~1~~Faceless Rager~Battlecry"
	requireTarget, keyWord, description = True, "", "Battlecry: Copy a friendly minion's Health"
	name_CN = "无面暴怒者"
	
	def targetExists(self, choice=0):
		return self.selectableFriendlyMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.ID == self.ID and target != self and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			self.statReset(False, target.health)
		return target
		
		
class FlightMaster(Minion):
	Class, race, name = "Neutral", "", "Flight Master"
	mana, attack, health = 3, 3, 4
	index = "DALARAN~Neutral~Minion~3~3~4~~Flight Master~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Summon a 2/2 Gryphon for each player"
	name_CN = "飞行管理员"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.Game.summon(Gryphon(self.Game, self.ID), self.pos+1, self)
		self.Game.summon(Gryphon(self.Game, 3-self.ID), -1, 3-self)
		return None
		
class Gryphon(Minion):
	Class, race, name = "Neutral", "Beast", "Gryphon"
	mana, attack, health = 2, 2, 2
	index = "DALARAN~Neutral~Minion~2~2~2~Beast~Gryphon~Uncollectible"
	requireTarget, keyWord, description = False, "", ""
	name_CN = "狮鹫"
	
	
class HenchClanSneak(Minion):
	Class, race, name = "Neutral", "", "Hench-Clan Sneak"
	mana, attack, health = 3, 3, 3
	index = "DALARAN~Neutral~Minion~3~3~3~~Hench-Clan Sneak~Stealth"
	requireTarget, keyWord, description = False, "Stealth", "Stealth"
	name_CN = "荆棘帮小偷"
	
	
class MagicCarpet(Minion):
	Class, race, name = "Neutral", "", "Magic Carpet"
	mana, attack, health = 3, 1, 6
	index = "DALARAN~Neutral~Minion~3~1~6~~Magic Carpet"
	requireTarget, keyWord, description = False, "", "After you play a 1-Cost minion, give it +1 Attack and Rush"
	name_CN = "魔法飞毯"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_MagicCarpet(self)]
		
class Trig_MagicCarpet(TrigBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionBeenPlayed"])
	#The number here is the mana used to play the minion
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject != self.entity and subject.ID == self.entity.ID and number == 1
		
	def text(self, CHN):
		return "在你使用一张法力值消耗为(1)的随从牌后，使其获得+1攻击力和突袭" if CHN \
				else "After you play a 1-Cost minion, give it +1 Attack and Rush"
				
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		subject.getsKeyword("Rush")
		subject.buffDebuff(1, 0)
		
		
class SpellwardJeweler(Minion):
	Class, race, name = "Neutral", "", "Spellward Jeweler"
	mana, attack, health = 3, 3, 4
	index = "DALARAN~Neutral~Minion~3~3~4~~Spellward Jeweler~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Your hero can't be targeted by spells or Hero Powers until your next turn"
	name_CN = "破咒珠宝师"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.Game.status[self.ID]["Evasive"] += 1
		self.Game.status[self.ID]["Evasive2NextTurn"] += 1
		return None
		
"""Mana 4 cards"""
#随机放言的法术不能对潜行随从施放，同时如果没有目标，则指向性法术整体失效，没有任何效果会结算
class ArchmageVargoth(Minion):
	Class, race, name = "Neutral", "", "Archmage Vargoth"
	mana, attack, health = 4, 2, 6
	index = "DALARAN~Neutral~Minion~4~2~6~~Archmage Vargoth~Legendary"
	requireTarget, keyWord, description = False, "", "At the end of your turn, cast a spell you've cast this turn (targets chosen randomly)"
	name_CN = "大法师瓦格斯"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_ArchmageVargoth(self)]
		
class Trig_ArchmageVargoth(TrigBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["TurnEnds"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and ID == self.entity.ID
		
	def text(self, CHN):
		return "在你的回合结束时，施放你在本回合中施放过的一个法术(目标随机而定)" if CHN \
				else "At the end of your turn, cast a spell you've cast this turn (targets chosen randomly)"
				
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		curGame = self.entity.Game
		if curGame.mode == 0:
			if curGame.guides:
				spell = curGame.guides.pop(0)
			else:
				spells = [curGame.cardPool[index] for index in curGame.Counters.cardsPlayedThisTurn[self.entity.ID]["Indices"] if "~Spell~" in index]
				spell = npchoice(spells) if spells else None
				curGame.fixedGuides.append(spell)
			if spell: spell(curGame, self.entity.ID).cast()
			
			
class Hecklebot(Minion):
	Class, race, name = "Neutral", "Mech", "Hecklebot"
	mana, attack, health = 4, 3, 8
	index = "DALARAN~Neutral~Minion~4~3~8~Mech~Hecklebot~Taunt~Battlecry"
	requireTarget, keyWord, description = False, "Taunt", "Taunt. Battlecry: Your opponent summons a minion from their deck"
	name_CN = "机械拷问者"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if curGame.mode == 0:
			if curGame.guides:
				i = curGame.guides.pop(0)
			else:
				minions = [i for i, card in enumerate(curGame.Hand_Deck.decks[3-self.ID]) if card.type == "Minion"]
				i = npchoice(minions) if minions and curGame.space(3-self.ID) > 0 else -1
				curGame.fixedGuides.append(i)
			if i > -1: curGame.summonfrom(i, 3-self.ID, -1, self, fromHand=False)
		return None
		
		
class HenchClanHag(Minion):
	Class, race, name = "Neutral", "", "Hench-Clan Hag"
	mana, attack, health = 4, 3, 3
	index = "DALARAN~Neutral~Minion~4~3~3~~Hench-Clan Hag~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Summon two 1/1 Amalgams with all minions types"
	name_CN = "荆棘帮巫婆"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		pos = (self.pos, "leftandRight") if self.onBoard else (-1, "totheRightEnd")
		self.Game.summon([Amalgam(self.Game, self.ID) for i in range(2)], pos, self)
		return None
		
class Amalgam(Minion):
	Class, race, name = "Neutral", "Elemental,Mech,Demon,Murloc,Dragon,Beast,Pirate,Totem", "Amalgam"
	mana, attack, health = 1, 1, 1
	index = "DALARAN~Neutral~Minion~1~1~1~Elemental,Mech,Demon,Murloc,Dragon,Beast,Pirate,Totem~Amalgam~Uncollectible"
	requireTarget, keyWord, description = False, "", "This is an Elemental, Mech, Demon, Murloc, Dragon, Beast, Pirate and Totem"
	name_CN = "融合怪"
	
	
class PortalKeeper(Minion):
	Class, race, name = "Neutral", "Demon", "Portal Keeper"
	mana, attack, health = 4, 5, 2
	index = "DALARAN~Neutral~Minion~4~5~2~Demon~Portal Keeper~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Shuffle 3 Portals into your deck. When drawn, summon a 2/2 Demon with Rush"
	name_CN = "传送门守护者"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		portals = [FelhoundPortal(self.Game, self.ID) for i in range(3)]
		self.Game.Hand_Deck.shuffleintoDeck(portals, creator=self)
		return None
		
class FelhoundPortal(Spell):
	Class, school, name = "Neutral", "", "Felhound Portal"
	requireTarget, mana = False, 2
	index = "DALARAN~Neutral~Spell~2~Felhound Portal~Casts When Drawn~Uncollectible"
	description = "Casts When Drawn. Summon a 2/2 Felhound with Rush"
	name_CN = "地狱犬传送门"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.Game.summon(Felhound(self.Game, self.ID), -1, self)
		return None
		
class Felhound(Minion):
	Class, race, name = "Neutral", "Demon", "Felhound"
	mana, attack, health = 2, 2, 2
	index = "DALARAN~Neutral~Minion~2~2~2~Demon~Felhound~Rush~Uncollectible"
	requireTarget, keyWord, description = False, "Rush", "Rush"
	name_CN = "地狱犬"
	
	
class ProudDefender(Minion):
	Class, race, name = "Neutral", "", "Proud Defender"
	mana, attack, health = 4, 2, 6
	index = "DALARAN~Neutral~Minion~4~2~6~~Proud Defender~Taunt"
	requireTarget, keyWord, description = False, "Taunt", "Taunt. Has +2 Attack while you have no other minions"
	name_CN = "骄傲的防御者"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.auras["Has +2 Attack while you have no other minions"] = StatAura_ProudDefender(self)
		
class StatAura_ProudDefender(GameRuleAura):
	def __init__(self, entity):
		self.entity = entity
		self.signals = ["MinionAppears", "MinionDisappears"]
		self.on = False
		self.auraAffected = []
		
	def auraAppears(self):
		game, ID = self.entity.Game, self.entity.ID
		for sig in self.signals:
			try: game.trigsBoard[ID][sig].append(self)
			except: game.trigsBoard[ID][sig] = [self]
		if not game.minionsonBoard(ID, target=self.entity): #No other minions on board
			self.on = True
			Stat_Receiver(self.entity, self, 2, 0).effectStart()
			
	def auraDisappears(self):
		for minion, receiver in self.auraAffected[:]:
			receiver.effectClear()
		self.auraAffected = []
		self.on = False
		game, ID = self.entity.Game, self.entity.ID
		for sig in self.signals:
			try: game.trigsBoard[ID][sig].remove(self)
			except: pass
			
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and ID == self.entity.ID
		
	def trig(self, signal, ID, subject, target, number, comment, choice=0):
		if self.canTrig(signal, ID, subject, target, number, comment):
			self.effect(signal, ID, subject, target, number, comment)
			
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		otherMinions = self.entity.Game.minionsonBoard(self.entity.ID, self.entity)
		if self.on and otherMinions:
			self.on = False
			for minion, receiver in self.auraAffected[:]:
				receiver.effectClear()
			self.auraAffected = []
		elif not self.on and not otherMinions:
			self.on = True
			Stat_Receiver(self.entity, self, 2, 0).effectStart()
			
			
class SoldierofFortune(Minion):
	Class, race, name = "Neutral", "Elemental", "Soldier of Fortune"
	mana, attack, health = 4, 5, 6
	index = "DALARAN~Neutral~Minion~4~5~6~Elemental~Soldier of Fortune"
	requireTarget, keyWord, description = False, "", "Whenever this minion attacks, give your opponent a coin"
	name_CN = "散财军士"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_SoldierofFortune(self)]
		
class Trig_SoldierofFortune(TrigBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionAttackingMinion", "MinionAttackingHero"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject == self.entity
		
	def text(self, CHN):
		return "每当该随从进行攻击，使你的对手获得一个幸运币" if CHN \
				else "Whenever this minion attacks, give your opponent a coin"
				
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.Game.Hand_Deck.addCardtoHand(TheCoin(self.entity.Game, 3-self.entity.ID), 3-self.entity.ID)
		
		
class TravelingHealer(Minion):
	Class, race, name = "Neutral", "", "Traveling Healer"
	mana, attack, health = 4, 3, 2
	index = "DALARAN~Neutral~Minion~4~3~2~~Traveling Healer~Battlecry~Divine Shield"
	requireTarget, keyWord, description = True, "Divine Shield", "Divine Shield. Battlecry: Restore 3 Health."
	name_CN = "旅行医者"
	def text(self, CHN):
		heal = 3 * (2 ** self.countHealDouble())
		return "战吼：恢复%d点生命值"%heal if CHN else "Divine Shield. Battlecry: Restore %d Health"%heal
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			heal = 3 * (2 ** self.countHealDouble())
			self.restoresHealth(target, heal)
		return target
		
		
class VioletSpellsword(Minion):
	Class, race, name = "Neutral", "", "Violet Spellsword"
	mana, attack, health = 4, 1, 6
	index = "DALARAN~Neutral~Minion~4~1~6~~Violet Spellsword~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Gain +1 Attack for each spell in your hand"
	name_CN = "紫罗兰 魔剑士"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		numSpells = 0
		for card in self.Game.Hand_Deck.hands[self.ID]:
			if card.type == "Spell":
				numSpells += 1
				
		self.buffDebuff(numSpells, 0)
		return None
		
"""Mana 5 cards"""
class AzeriteElemental(Minion):
	Class, race, name = "Neutral", "Elemental", "Azerite Elemental"
	mana, attack, health = 5, 2, 7
	index = "DALARAN~Neutral~Minion~5~2~7~Elemental~Azerite Elemental"
	requireTarget, keyWord, description = False, "", "At the start of your turn, gain Spell Damage +2"
	name_CN = "艾泽里特元素"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_AzeriteElemental(self)]
		
class Trig_AzeriteElemental(TrigBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["TurnStarts"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and ID == self.entity.ID
		
	def text(self, CHN):
		return "在你的回合开始时，获得法术伤害+2" if CHN else "At the start of your turn, gain Spelldamage +2"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.getsKeyword("Spell Damage")
		self.entity.getsKeyword("Spell Damage")
		
		
class BaristaLynchen(Minion):
	Class, race, name = "Neutral", "", "Barista Lynchen"
	mana, attack, health = 5, 4, 5
	index = "DALARAN~Neutral~Minion~5~4~5~~Barista Lynchen~Battlecry~Legendary"
	requireTarget, keyWord, description = False, "", "Battlecry: Add a copy of each of your other Battlecry minions to your hand"
	name_CN = "咖啡师林彻"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		battlecryMinions = []
		for minion in self.Game.minions[self.ID]:
			if "~Battlecry" in minion.index and minion != self:
				battlecryMinions.append(minion)
		if battlecryMinions != []:
			for minion in battlecryMinions:
				self.Game.Hand_Deck.addCardtoHand(type(minion)(self.Game, self.ID), self.ID)
		return None
		
		
class DalaranCrusader(Minion):
	Class, race, name = "Neutral", "", "Dalaran Crusader"
	mana, attack, health = 5, 5, 4
	index = "DALARAN~Neutral~Minion~5~5~4~~Dalaran Crusader~Divine Shield"
	requireTarget, keyWord, description = False, "Divine Shield", "Divine Shield"
	name_CN = "达拉然圣剑士"
	
	
class RecurringVillain(Minion):
	Class, race, name = "Neutral", "", "Recurring Villain"
	mana, attack, health = 5, 3, 6
	index = "DALARAN~Neutral~Minion~5~3~6~~Recurring Villain~Deathrattle"
	requireTarget, keyWord, description = False, "", "Deathrattle: If this minion has 4 or more Attack, resummon it"
	name_CN = "再生大盗"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [ResummonifAttackGreaterthan3(self)]
		
class ResummonifAttackGreaterthan3(Deathrattle_Minion):
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return target == self.entity and number > 3
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		newMinion = type(self.entity)(self.entity.Game, self.entity.ID)
		self.entity.Game.summon(newMinion, self.entity.pos+1, self.entity)
		
	def text(self, CHN):
		return "亡语：如果该随从的攻击力大于或等于4，则再次召唤该随从" if CHN \
				else "Deathrattle: If this minion has 4 or more Attack, resummon it"
				
				
class SunreaverWarmage(Minion):
	Class, race, name = "Neutral", "", "Sunreaver Warmage"
	mana, attack, health = 5, 4, 4
	index = "DALARAN~Neutral~Minion~5~4~4~~Sunreaver Warmage~Battlecry"
	requireTarget, keyWord, description = True, "", "Battlecry: If you're holding a spell costs (5) or more, deal 4 damage"
	name_CN = "夺日者战斗法师"
	
	def effCanTrig(self):
		self.effectViable = self.Game.Hand_Deck.holdingSpellwith5CostorMore(self.ID)
		
	def returnTrue(self, choice=0):
		return self.Game.Hand_Deck.holdingSpellwith5CostorMore(self.ID)
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target and self.Game.Hand_Deck.holdingSpellwith5CostorMore(self.ID):
			self.dealsDamage(target, 4)
		return target
		
"""Mana 6 cards"""
class EccentricScribe(Minion):
	Class, race, name = "Neutral", "", "Eccentric Scribe"
	mana, attack, health = 6, 6, 4
	index = "DALARAN~Neutral~Minion~6~6~4~~Eccentric Scribe~Deathrattle"
	requireTarget, keyWord, description = False, "", "Deathrattle: Summon four 1/1 Vengeful Scrolls"
	name_CN = "古怪的铭文师"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [Summon4VengefulScrolls(self)]
		
class Summon4VengefulScrolls(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		minion = self.entity
		pos = (minion.pos, "totheRight") if minion in minion.Game.minions[minion.ID] else (-1, "totheRightEnd")
		minion.Game.summon([VengefulScroll(minion.Game, minion.ID) for i in range(4)], pos, minion)
		
	def text(self, CHN):
		return "亡语：召唤四个1/1的复仇卷轴" if CHN else "Deathrattle: Summon four 1/1 Vengeful Scrolls"
		
class VengefulScroll(Minion):
	Class, race, name = "Neutral", "", "Vengeful Scroll"
	mana, attack, health = 1, 1, 1
	index = "DALARAN~Neutral~Minion~1~1~1~~Vengeful Scroll~Uncollectible"
	requireTarget, keyWord, description = False, "", ""
	name_CN = "复仇卷轴"
	
	
class MadSummoner(Minion):
	Class, race, name = "Neutral", "Demon", "Mad Summoner"
	mana, attack, health = 6, 4, 4
	index = "DALARAN~Neutral~Minion~6~4~4~Demon~Mad Summoner~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Fill each player's board with 1/1 Imps"
	name_CN = "疯狂召唤师"
	#假设是轮流为我方和对方召唤两个小鬼
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		while True:
			friendlyBoardNotFull, enemyBoardNotFull = True, True
			if self.Game.space(self.ID) > 0:
				self.Game.summon([Imp_Shadows(self.Game, self.ID) for i in range(2)], (-1, "totheRightEnd"), self)
			else:
				friendlyBoardNotFull = False
			if self.Game.space(3-self.ID) > 0:
				self.Game.summon([Imp_Shadows(self.Game, 3-self.ID) for i in range(2)], (-1, "totheRightEnd"), 3-self)
			else:
				enemyBoardNotFull = False
			if friendlyBoardNotFull == False and enemyBoardNotFull == False:
				break
				
		return None
		
class Imp_Shadows(Minion):
	Class, race, name = "Neutral", "Demon", "Imp"
	mana, attack, health = 1, 1, 1
	index = "DALARAN~Neutral~Minion~1~1~1~Demon~Imp~Uncollectible"
	requireTarget, keyWord, description = False, "", ""
	name_CN = "小鬼"
	
	
class PortalOverfiend(Minion):
	Class, race, name = "Neutral", "Demon", "Portal Overfiend"
	mana, attack, health = 6, 5, 6
	index = "DALARAN~Neutral~Minion~6~5~6~Demon~Portal Overfiend~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Shuffle 3 Portals into your deck. When drawn, summon a 2/2 Demon with Rush"
	name_CN = "传送门大恶魔"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		portals = [FelhoundPortal(self.Game, self.ID) for i in range(3)]
		self.Game.Hand_Deck.shuffleintoDeck(portals, creator=self)
		return None
		
		
class Safeguard(Minion):
	Class, race, name = "Neutral", "Mech", "Safeguard"
	mana, attack, health = 6, 4, 5
	index = "DALARAN~Neutral~Minion~6~4~5~Mech~Safeguard~Taunt~Deathrattle"
	requireTarget, keyWord, description = False, "Taunt", "Taunt. Deathrattle: Summon a 0/5 Vault Safe with Taunt"
	name_CN = "机械保险箱"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [SummonaVaultSafe(self)]
		
class SummonaVaultSafe(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.Game.summon(VaultSafe(self.entity.Game, self.entity.ID), self.entity.pos+1, self.entity)
		
	def text(self, CHN):
		return "亡语：召唤一个0/5并具有嘲讽的保险柜" if CHN \
				else "Deathrattle: Summon a 0/5 Vault Safe with Taunt"
				
class VaultSafe(Minion):
	Class, race, name = "Neutral", "Mech", "Vault Safe"
	mana, attack, health = 2, 0, 5
	index = "DALARAN~Neutral~Minion~2~0~5~Mech~Vault Safe~Taunt~Uncollectible"
	requireTarget, keyWord, description = False, "Taunt", "Taunt"
	name_CN = "保险柜"
	
	
class UnseenSaboteur(Minion):
	Class, race, name = "Neutral", "", "Unseen Saboteur"
	mana, attack, health = 6, 5, 6
	index = "DALARAN~Neutral~Minion~6~5~6~~Unseen Saboteur~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Your opponent casts a random spell from their hand (targets chosen randomly)"
	name_CN = "隐秘破坏者"
	#不知道是否会拉出不能使用的法术
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if curGame.mode == 0:
			if curGame.guides:
				i = curGame.guides.pop(0)
			else:
				spells = [i for i, card in enumerate(curGame.Hand_Deck.hands[3-self.ID]) if card.type == "Spell"]
				i = npchoice(spells) if spells and curGame.space(3-self.ID) > 0 else -1
				curGame.fixedGuides.append(i)
			if i > -1: curGame.Hand_Deck.extractfromHand(i, 3-self.ID)[0].cast()
		return None
		
		
class VioletWarden(Minion):
	Class, race, name = "Neutral", "", "Violet Warden"
	mana, attack, health = 6, 4, 7
	index = "DALARAN~Neutral~Minion~6~4~7~~Violet Warden~Taunt~Spell Damage"
	requireTarget, keyWord, description = False, "Taunt,Spell Damage", "Taunt, Spell Damage +1"
	name_CN = "紫罗兰典狱官"
	
"""Mana 7 cards"""
class ChefNomi(Minion):
	Class, race, name = "Neutral", "", "Chef Nomi"
	mana, attack, health = 7, 6, 6
	index = "DALARAN~Neutral~Minion~7~6~6~~Chef Nomi~Battlecry~Legendary"
	requireTarget, keyWord, description = False, "", "Battlecry: If your deck is empty, summon six 6/6 Greasefire Elementals"
	name_CN = "大厨诺米"
	
	def effCanTrig(self):
		self.effectViable = self.Game.Hand_Deck.decks[self.ID] == []
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if self.Game.Hand_Deck.decks[self.ID] == []:
			if self.onBoard:
				self.Game.summon([GreasefireElemental(self.Game, self.ID) for i in range(6)], (self.pos, "leftandRight"), self)
			else:
				self.Game.summon([GreasefireElemental(self.Game, self.ID) for i in range(7)], (-1, "totheRightEnd"), self)
		return None
		
class GreasefireElemental(Minion):
	Class, race, name = "Neutral", "Elemental", "Greasefire Elemental"
	mana, attack, health = 6, 6, 6
	index = "DALARAN~Neutral~Minion~6~6~6~Elemental~Greasefire Elemental~Uncollectible"
	requireTarget, keyWord, description = False, "", ""
	name_CN = "猛火元素"
	
	
class ExoticMountseller(Minion):
	Class, race, name = "Neutral", "", "Exotic Mountseller"
	mana, attack, health = 7, 5, 8
	index = "DALARAN~Neutral~Minion~7~5~8~~Exotic Mountseller"
	requireTarget, keyWord, description = False, "", "Whenever you cast a spell, summon a random 3-Cost Beast"
	name_CN = "特殊坐骑商人"
	poolIdentifier = "3-Cost Beasts to Summon"
	@classmethod
	def generatePool(cls, Game):
		return "3-Cost Beasts to Summon", [value for key, value in Game.MinionswithRace["Beast"].items() if key.split('~')[3] == "3"]
		
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_ExoticMountseller(self)]
		
class Trig_ExoticMountseller(TrigBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["SpellPlayed"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject.ID == self.entity.ID
		
	def text(self, CHN):
		return "每当你施放一个法术，随机召唤一个法力值消耗为(3)的野兽" if CHN else "Whenever you cast a spell, summon a random 3-Cost Beast"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		curGame = self.entity.Game
		if curGame.mode == 0:
			if curGame.guides:
				beast = curGame.guides.pop(0)
			else:
				beast = npchoice(self.rngPool("3-Cost Beasts to Summon"))
				curGame.fixedGuides.append(beast)
			curGame.summon(beast(curGame, self.entity.ID), self.entity.pos+1, self.entity)
		
		
class TunnelBlaster(Minion):
	Class, race, name = "Neutral", "", "Tunnel Blaster"
	mana, attack, health = 7, 3, 7
	index = "DALARAN~Neutral~Minion~7~3~7~~Tunnel Blaster~Taunt~Deathrattle"
	requireTarget, keyWord, description = False, "Taunt", "Taunt. Deathrattle: Deal 3 damage to all minions"
	name_CN = "坑道爆破手"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [Deal3DamagetoAllMinions(self)]
		
class Deal3DamagetoAllMinions(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		targets = self.entity.Game.minionsonBoard(1) + self.entity.Game.minionsonBoard(2)
		self.entity.dealsAOE(targets, [3]*len(targets))
		
	def text(self, CHN):
		return "对所有随从造成3点伤害" if CHN else "Deathrattle: Deal 3 damage to all minions"
		
		
class UnderbellyOoze(Minion):
	Class, race, name = "Neutral", "", "Underbelly Ooze"
	mana, attack, health = 7, 3, 5
	index = "DALARAN~Neutral~Minion~7~3~5~~Underbelly Ooze"
	requireTarget, keyWord, description = False, "", "After this minion survives damage, summon a copy of it"
	name_CN = "下水道软泥怪"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_UnderbellyOoze(self)]
		
class Trig_UnderbellyOoze(TrigBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionTakesDmg"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and target == self.entity and self.entity.health > 0 and self.entity.dead == False
		
	def text(self, CHN):
		return "在该随从受到伤害并没有死亡后，召唤一个它的复制" if CHN else "After this minion survives damage, summon a copy of it"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		Copy = self.entity.selfCopy(self.entity.ID)
		self.entity.Game.summon(Copy, self.entity.pos+1, self.entity)
		
"""Mana 8 cards"""
class Batterhead(Minion):
	Class, race, name = "Neutral", "", "Batterhead"
	mana, attack, health = 8, 3, 12
	index = "DALARAN~Neutral~Minion~8~3~12~~Batterhead~Rush"
	requireTarget, keyWord, description = False, "Rush", "Rush. After this attacks and kills a minion, it may attack again"
	name_CN = "莽头食人魔"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_Batterhead(self)]
		
class Trig_Batterhead(TrigBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionAttackedMinion"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject == self.entity and self.entity.health > 0 and self.entity.dead == False and (target.health < 1 or target.dead == True)
		
	def text(self, CHN):
		return "在该随从攻击并消灭一个随从后，可再次攻击" if CHN else "After this attacks and kills a minion, it may attack again"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.attChances_extra += 1
		
		
class HeroicInnkeeper(Minion):
	Class, race, name = "Neutral", "", "Heroic Innkeeper"
	mana, attack, health = 8, 4, 4
	index = "DALARAN~Neutral~Minion~8~4~4~~Heroic Innkeeper~Taunt~Battlecry"
	requireTarget, keyWord, description = False, "Taunt", "Taunt. Battlecry: Gain +2/+2 for each other friendly minion"
	name_CN = "霸气的 旅店老板娘"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if self.onBoard or self.inHand:
			targets = self.Game.minionsonBoard(self.ID, self)
			buff = 2 * len(targets)
			self.buffDebuff(buff, buff)
		return None
		
		
class JepettoJoybuzz(Minion):
	Class, race, name = "Neutral", "", "Jepetto Joybuzz"
	mana, attack, health = 8, 6, 6
	index = "DALARAN~Neutral~Minion~8~6~6~~Jepetto Joybuzz~Battlecry~Legendary"
	requireTarget, keyWord, description = False, "", "Battlecry: Draw 2 minions from your deck. Set their Attack, Health, and Cost to 1"
	name_CN = "耶比托·乔巴斯"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		for num in range(2):
			if curGame.mode == 0:
				if curGame.guides:
					i = curGame.guides.pop(0)
				else:
					minions = [i for i, card in enumerate(curGame.Hand_Deck.decks[self.ID]) if card.type == "Minion"]
					i = npchoice(minions) if minions else -1
					curGame.fixedGuides.append(i)
				if i > -1:
					minion = curGame.Hand_Deck.drawCard(self.ID, i)[0]
					if minion:
						minion.statReset(1, 1)
						ManaMod(minion, changeby=0, changeto=1).applies()
				else: break
		return None
		
		
class WhirlwindTempest(Minion):
	Class, race, name = "Neutral", "Elemental", "Whirlwind Tempest"
	mana, attack, health = 8, 6, 6
	index = "DALARAN~Neutral~Minion~8~6~6~Elemental~Whirlwind Tempest"
	requireTarget, keyWord, description = False, "", "Your Windfury minions have Mega Windfury"
	name_CN = "暴走旋风"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.auras["Your Windfury minions have Mega Windfury"] = EffectAura(self, "Mega Windfury")
		
	def applicable(self, target):
		return target.keyWords["Windfury"] > 0
		
"""Mana 9 cards"""
class BurlyShovelfist(Minion):
	Class, race, name = "Neutral", "", "Burly Shovelfist"
	mana, attack, health = 9, 9, 9
	index = "DALARAN~Neutral~Minion~9~9~9~~Burly Shovelfist~Rush"
	requireTarget, keyWord, description = False, "Rush", "Rush"
	name_CN = "推土壮汉"
	
	
class ArchivistElysiana(Minion):
	Class, race, name = "Neutral", "", "Archivist Elysiana"
	mana, attack, health = 9, 7, 7
	index = "DALARAN~Neutral~Minion~9~7~7~~Archivist Elysiana~Battlecry~Legendary"
	requireTarget, keyWord, description = False, "", "Battlecry: Discover 5 cards. Replace your deck with 2 copies of each"
	name_CN = "档案员 艾丽西娜"
	poolIdentifier = "Cards as Druid"
	@classmethod
	def generatePool(cls, Game):
		return ["Cards as "+Class for Class in Game.Classes], [list(Game.ClassCards[Class].values())+list(Game.NeutralCards.values()) for Class in Game.Classes]
		
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.newDeck = []
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if self.ID == curGame.turn:
			if curGame.mode == 0:
				if curGame.guides:
					deck = curGame.guides.pop(0)
				else:
					self.newDeck, key = [], "Cards as "+classforDiscover(self)
					if "byOthers" in comment:
						for i in range(5):
							newCard = npchoice(self.rngPool(key))
							self.newDeck.append(newCard(curGame, self.ID))
							self.newDeck.append(newCard(curGame, self.ID))
					else:
						for i in range(5):
							cards = npchoice(self.rngPool(key), 3, replace=False)
							self.Game.options = [card(self.Game, self.ID) for card in cards]
							self.Game.Discover.startDiscover(self)
					npshuffle(self.newDeck)
					deck = self.newDeck
					curGame.fixedGuides.append(tuple(deck))
					self.newDeck = []
				curGame.Hand_Deck.extractfromDeck(None, self.ID, True)
				curGame.Hand_Deck.decks[self.ID] = [card(curGame, self.ID) for card in deck]
				for card in curGame.Hand_Deck.decks[self.ID]: card.entersDeck()
		return None
		
	def discoverDecided(self, option, pool):
		self.newDeck.append(option)
		self.newDeck.append(type(option)(self.Game, self.ID))
		
"""Mana 10 cards"""
class BigBadArchmage(Minion):
	Class, race, name = "Neutral", "", "Big Bad Archmage"
	mana, attack, health = 10, 6, 6
	index = "DALARAN~Neutral~Minion~10~6~6~~Big Bad Archmage"
	requireTarget, keyWord, description = False, "", "At the end of your turn, summon a random 6-Cost minion"
	name_CN = "恶狼大法师"
	poolIdentifier = "6-Cost Minions to Summon"
	@classmethod
	def generatePool(cls, Game):
		return "6-Cost Minions to Summon", list(Game.MinionsofCost[6].values())
		
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_BigBadArchmage(self)]
		
class Trig_BigBadArchmage(TrigBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["TurnEnds"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and ID == self.entity.ID
		
	def text(self, CHN):
		return "在你的回合结束时，随机召唤一个法力值消耗为(6)的随从" if CHN else "At the end of your turn, summon a random 6-Cost minion"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		curGame = self.entity.Game
		if curGame.mode == 0:
			if curGame.guides:
				minion = curGame.guides.pop(0)
			else:
				minion = npchoice(self.rngPool("6-Cost Minions to Summon"))
				curGame.fixedGuides.append(minion)
			curGame.summon(minion(curGame, self.entity.ID), self.entity.pos+1, self.entity)
			
"""Druid cards"""
class Acornbearer(Minion):
	Class, race, name = "Druid", "", "Acornbearer"
	mana, attack, health = 1, 2, 1
	index = "DALARAN~Druid~Minion~1~2~1~~Acornbearer~Deathrattle"
	requireTarget, keyWord, description = False, "", "Deathrattle: Add two 1/1 Squirrels to your hand"
	name_CN = "橡果人"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [AddTwoSquirrelstoHand(self)]
		
class AddTwoSquirrelstoHand(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.Game.Hand_Deck.addCardtoHand([Squirrel_Shadows, Squirrel_Shadows], self.entity.ID, byType=True)
		
	def text(self, CHN):
		return "亡语：将两张1/1“松鼠”置入你的手牌" if CHN \
				else "Deathrattle: Add two 1/1 Squirrels to your hand"
				
class Squirrel_Shadows(Minion):
	Class, race, name = "Druid", "Beast", "Squirrel"
	mana, attack, health = 1, 1, 1
	index = "DALARAN~Druid~Minion~1~1~1~Beast~Squirrel~Uncollectible"
	requireTarget, keyWord, description = False, "", ""
	name_CN = "松鼠"
	
	
class CrystalPower(Spell):
	Class, school, name = "Druid", "Nature", "Crystal Power"
	requireTarget, mana = True, 1
	index = "DALARAN~Druid~Spell~1~Nature~Crystal Power~Choose One"
	description = "Choose One - Deal 2 damage to a minion; or Restore 5 Health"
	name_CN = "水晶之力"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.options = [PiercingThorns_Option(self), HealingBlossom_Option(self)]
		
	def need2Choose(self):
		return True
		
	def available(self):
		return self.selectableCharacterExists(1)
		
	#available() only needs to check selectableCharacterExists
	def targetCorrect(self, target, choice=0):
		return target.onBoard and (target.type == "Minion" or (choice != 0 and target.type == "Hero"))
		
	def text(self, CHN):
		damage = (2 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		heal = 5 * (2 ** self.countHealDouble())
		return "抉择：对一个随从造成%d点伤害； 或者恢复%d点生命值"%(damage, heal) if CHN \
				else "Choose One - Deal %d damage to a minion; or Restore %d Health"%(damage, heal)
				
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			if choice < 0: #如果目标是一个随从，先对其造成伤害，如果目标存活，才能造成治疗
				if target.type == "Minion": #只会对随从造成伤害
					damage = (2 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
					self.dealsDamage(target, damage)
				if target.health > 0 and target.dead == False: #法术造成伤害之后，那个随从必须活着才能接受治疗，不然就打2无论如何都变得没有意义
					heal = 5 * (2 ** self.countHealDouble())
					self.restoresHealth(target, heal)
			elif choice == 0:
				if target.type == "Minion":
					damage = (2 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
					self.dealsDamage(target, damage)
			else: #Choice == 1
				heal = 5 * (2 ** self.countHealDouble())
				self.restoresHealth(target, heal)
		return target
		
class PiercingThorns_Option(ChooseOneOption):
	name, description = "Piercing Thorns", "Deal 2 damage to minion"
	index = "DALARAN~Druid~Spell~1~Nature~Piercing Thorns~Uncollectible"
	def available(self):
		return self.entity.selectableMinionExists(0)
		
class HealingBlossom_Option(ChooseOneOption):
	name, description = "Healing Blossom", "Restore 5 Health"
	index = "DALARAN~Druid~Spell~1~Nature~Healing Blossom~Uncollectible"
	def available(self):
		return self.entity.selectableCharacterExists(1)
		
class PiercingThorns(Spell):
	Class, school, name = "Druid", "Nature", "Piercing Thorns"
	requireTarget, mana = True, 1
	index = "DALARAN~Druid~Spell~1~Nature~Piercing Thorns~Uncollectible"
	description = "Deal 2 damage to a minion"
	name_CN = "利刺荆棘"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
		
	def text(self, CHN):
		damage = (2 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		return "对一个随从造成%d点伤害"%damage if CHN else "Deal %d damage to a minion"%damage
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			damage = (2 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			self.dealsDamage(target, damage)
		return target
		
class HealingBlossom(Spell):
	Class, school, name = "Druid", "Nature", "Healing Blossom"
	requireTarget, mana = True, 1
	index = "DALARAN~Druid~Spell~1~Nature~Healing Blossom~Uncollectible"
	description = "Restore 5 Health"
	name_CN = "愈合之花"
	def text(self, CHN):
		heal = 5 * (2 ** self.countHealDouble())
		return "恢复%d点生命值"%heal if CHN else "Restore %d Health"%heal
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			heal = 5 * (2 ** self.countHealDouble())
			self.restoresHealth(target, heal)
		return target
		
		
class CrystalsongPortal(Spell):
	Class, school, name = "Druid", "Nature", "Crystalsong Portal"
	requireTarget, mana = False, 2
	index = "DALARAN~Druid~Spell~2~Nature~Crystalsong Portal"
	description = "Discover a Druid minion. If your hand has no minions, keep all 3"
	name_CN = "晶歌传送门"
	poolIdentifier = "Druid Minions"
	@classmethod
	def generatePool(cls, Game):
		return "Druid Minions", [value for key, value in Game.ClassCards["Druid"].items() if "~Minion~" in key]
		
	def effCanTrig(self):
		self.effectViable = True
		for card in self.Game.Hand_Deck.hands[self.ID]:
			if card.type == "Minion":
				self.effectViable = False
				break
				
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		handHasMinion = False
		for card in curGame.Hand_Deck.hands[self.ID]:
			if card.type == "Minion":
				handHasMinion = True
				break
		if curGame.mode == 0:
			if not handHasMinion:
				if curGame.guides:
					minions = curGame.guides.pop(0)
				else:
					minions = npchoice(self.rngPool("Druid Minions"), 3, replace=False)
					curGame.fixedGuides.append(tuple(minions))
				curGame.Hand_Deck.addCardtoHand(minions, self.ID, byType=True)
			else:
				if curGame.guides:
					minion = curGame.guides.pop(0)
					curGame.Hand_Deck.addCardtoHand(minion, self.ID, byType=True, byDiscover=True)
				else:
					if self.ID != curGame.turn or "byOthers" in comment:
						minion = npchoice(self.rngPool("Druid Minions"))
						curGame.fixedGuides.append(minion)
						curGame.Hand_Deck.addCardtoHand(minion, self.ID, byType=True, byDiscover=True)
					else:
						minions = npchoice(self.rngPool("Druid Minions"), 3, replace=False)
						curGame.options = [minion(curGame, self.ID) for minion in minions]
						curGame.Discover.startDiscover(self)
		return None
		
	def discoverDecided(self, option, pool):
		self.Game.fixedGuides.append(type(option))
		self.Game.Hand_Deck.addCardtoHand(option, self.ID, byDiscover=True)
		
		
class DreamwayGuardians(Spell):
	Class, school, name = "Druid", "", "Dreamway Guardians"
	requireTarget, mana = False, 2
	index = "DALARAN~Druid~Spell~2~Dreamway Guardians"
	description = "Summon two 1/2 Dryads with Lifesteal"
	name_CN = "守卫梦境之路"
	def available(self):
		return self.Game.space(self.ID) > 0
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.Game.summon([CrystalDryad(self.Game, self.ID) for i in range(2)], (-1, "totheRightEnd"), self)
		return None
		
class CrystalDryad(Minion):
	Class, race, name = "Druid", "", "Crystal Dryad"
	mana, attack, health = 1, 1, 2
	index = "DALARAN~Druid~Minion~1~1~2~~Crystal Dryad~Lifesteal~Uncollectible"
	requireTarget, keyWord, description = False, "Lifesteal", "Lifesteal"
	name_CN = "水晶树妖"
	
	
class KeeperStalladris(Minion):
	Class, race, name = "Druid", "", "Keeper Stalladris"
	mana, attack, health = 2, 2, 3
	index = "DALARAN~Druid~Minion~2~2~3~~Keeper Stalladris~Legendary"
	requireTarget, keyWord, description = False, "", "After you cast a Choose One spell, add copies of both choices to your hand"
	name_CN = "守护者 斯塔拉蒂斯"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_KeeperStalladris(self)]
		
class Trig_KeeperStalladris(TrigBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["SpellBeenPlayed"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject.ID == self.entity.ID and subject.need2Choose()
		
	def text(self, CHN):
		return "在你施放一个抉择法术后，将每个选项的复制置入你的手牌" if CHN \
				else "After you cast a Choose One spell, add copies of both choices to your hand"
				
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		game = self.entity.Game
		for option in subject.options:
			spell = game.cardPool[option.index]
			try: game.Hand_Deck.addCardtoHand(spell, self.entity.ID, "index")
			except: pass
			
			
class Lifeweaver(Minion):
	Class, race, name = "Druid", "", "Lifeweaver"
	mana, attack, health = 3, 2, 5
	index = "DALARAN~Druid~Minion~3~2~5~~Lifeweaver"
	requireTarget, keyWord, description = False, "", "Whenever you restore Health, add a random Druid spell to your hand"
	name_CN = "织命者"
	poolIdentifier = "Druid Spells"
	@classmethod
	def generatePool(cls, Game):
		return "Druid Spells", [value for key, value in Game.ClassCards["Druid"].items() if "~Spell~" in key]
		
	def __init__(self, Game, ID,):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_Lifeweaver(self)]
			
class Trig_Lifeweaver(TrigBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionGetsHealed", "HeroGetsHealed"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject.ID == self.entity.ID
		
	def text(self, CHN):
		return "每当有角色获得你的治疗时，随机将一张德鲁伊法术牌置入你的手牌" if CHN \
				else "Whenever you restore Health, add a random Druid spell to your hand"
				
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		curGame = self.entity.Game
		if curGame.mode == 0:
			if curGame.guides:
				spell = curGame.guides.pop(0)
			else:
				spell = npchoice(self.rngPool("Druid Spells"))
				curGame.fixedGuides.append(spell)
			curGame.Hand_Deck.addCardtoHand(spell, self.entity.ID, byType=True)
			
			
class CrystalStag(Minion):
	Class, race, name = "Druid", "Beast", "Crystal Stag"
	mana, attack, health = 5, 4, 4
	index = "DALARAN~Druid~Minion~5~4~4~Beast~Crystal Stag~Rush~Battlecry"
	requireTarget, keyWord, description = False, "Rush", "Rush. Battlecry: If you've restored 5 Health this game, summon a copy of this"
	name_CN = "晶角雄鹿"
	
	def effCanTrig(self):
		self.effectViable = self.Game.Counters.healthRestoredThisGame[self.ID] > 4
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if self.Game.Counters.healthRestoredThisGame[self.ID] > 4:
			Copy = self.selfCopy(self.ID)
			self.Game.summon(Copy, self.pos+1, self)
		return None
		
		
class BlessingoftheAncients(Spell):
	Class, school, name = "Druid", "Nature", "Blessing of the Ancients"
	requireTarget, mana = False, 3
	index = "DALARAN~Druid~Spell~3~Nature~Blessing of the Ancients~Twinspell"
	description = "Twinspell. Give your minions +1/+1"
	name_CN = "远古祝福"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.twinSpell = 1
		self.twinSpellCopy = BlessingoftheAncients2
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		for minion in self.Game.minionsonBoard(self.ID):
			minion.buffDebuff(1, 1)
		return None
		
class BlessingoftheAncients2(Spell):
	Class, school, name = "Druid", "Nature", "Blessing of the Ancients"
	requireTarget, mana = False, 3
	index = "DALARAN~Druid~Spell~3~Nature~Blessing of the Ancients~Uncollectible"
	description = "Give your minions +1/+1"
	name_CN = "远古祝福"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		for minion in self.Game.minionsonBoard(self.ID):
			minion.buffDebuff(1, 1)
		return None
		
		
class Lucentbark(Minion):
	Class, race, name = "Druid", "", "Lucentbark"
	mana, attack, health = 8, 4, 8
	index = "DALARAN~Druid~Minion~8~4~8~~Lucentbark~Taunt~Deathrattle~Legendary"
	requireTarget, keyWord, description = False, "Taunt", "Taunt. Deathrattle: Go dormant. Restore 5 Health to awaken this minion"
	name_CN = "卢森巴克"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [BecomeSpiritofLucentbark(self)]
		
class BecomeSpiritofLucentbark(Deathrattle_Minion):
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return target == self.entity and self.entity.Game.space(self.entity.ID) > 0
	#这个变形亡语只能触发一次。
	def trig(self, signal, ID, subject, target, number, comment, choice=0):
		if self.canTrig(signal, ID, subject, target, number, comment):
			if self.entity.Game.GUI:
				self.entity.Game.GUI.deathrattleAni(self.entity)
			dormant = SpiritofLucentbark(self.entity.Game, self.entity.ID)
			self.entity.Game.transform(self.entity, dormant)
			
	def text(self, CHN):
		return "亡语：进入休眠状态。累计恢复5生命可唤醒该随从" if CHN \
				else "Deathrattle: Go dormant. Restore 5 Health to awaken this minion"
				
class SpiritofLucentbark(Dormant):
	Class, school, name = "Druid", "", "Spirit of Lucentbark"
	description = "Restore 5 Health to awaken"
	name_CN = "卢森巴克之魂"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_SpiritofLucentbark(self)]
		self.prisoner = Lucentbark
		
class Trig_SpiritofLucentbark(TrigBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionGetsHealed", "HeroGetsHealed"])
		self.counter = 0
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject.ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.counter += number
		if self.counter > 4:
			self.entity.Game.transform(self.entity, Lucentbark(self.entity.Game, self.entity.ID))
			
			
class TheForestsAid(Spell):
	Class, school, name = "Druid", "Nature", "The Forest's Aid"
	requireTarget, mana = False, 8
	index = "DALARAN~Druid~Spell~8~Nature~The Forest's Aid~Twinspell"
	description = "Twinspell. Summon five 2/2 Treants"
	name_CN = "森林的援助"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.twinSpell = 1
		self.twinSpellCopy = TheForestsAid2
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.Game.summon([Treant_Shadows(self.Game, self.ID) for i in range(5)], (-1, "totheRightEnd"), self)
		return None
		
class TheForestsAid2(Spell):
	Class, school, name = "Druid", "Nature", "The Forest's Aid"
	requireTarget, mana = False, 8
	index = "DALARAN~Druid~Spell~8~Nature~The Forest's Aid~Uncollectible"
	description = "Summon five 2/2 Treants"
	name_CN = "森林的援助"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.Game.summon([Treant_Shadows(self.Game, self.ID) for i in range(5)], (-1, "totheRightEnd"), self)
		return None
		
class Treant_Shadows(Minion):
	Class, race, name = "Druid", "", "Treant"
	mana, attack, health = 2, 2, 2
	index = "DALARAN~Druid~Minion~2~2~2~~Treant~Uncollectible"
	requireTarget, keyWord, description = False, "", ""
	name_CN = "树人"
	
"""Hunter cards"""
class RapidFire(Spell):
	Class, school, name = "Hunter", "", "Rapid Fire"
	requireTarget, mana = True, 1
	index = "DALARAN~Hunter~Spell~1~Rapid Fire~Twinspell"
	description = "Twinspell. Deal 1 damage"
	name_CN = "急速射击"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.twinSpell = 1
		self.twinSpellCopy = RapidFire2
		
	def text(self, CHN):
		damage = (1 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		return "双生法术。造成%d点伤害"%damage if CHN else "Twinspell. Deal %d damage"%damage
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			damage = (1 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			self.dealsDamage(target, damage)
		return target
		
class RapidFire2(Spell):
	Class, school, name = "Hunter", "", "Rapid Fire"
	requireTarget, mana = True, 1
	index = "DALARAN~Hunter~Spell~1~Rapid Fire~Uncollectible"
	description = "Deal 1 damage"
	name_CN = "急速射击"
	def text(self, CHN):
		damage = (1 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		return "造成%d点伤害"%damage if CHN else "Deal %d damage"%damage
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			damage = (1 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			self.dealsDamage(target, damage)
		return target
			
			
class Shimmerfly(Minion):
	Class, race, name = "Hunter", "Beast", "Shimmerfly"
	mana, attack, health = 1, 1, 1
	index = "DALARAN~Hunter~Minion~1~1~1~Beast~Shimmerfly~Deathrattle"
	requireTarget, keyWord, description = False, "", "Deathrattle: Add a random Hunter spell to your hand"
	name_CN = "闪光蝴蝶"
	poolIdentifier = "Hunter Spells"
	@classmethod
	def generatePool(cls, Game):
		return "Hunter Spells", [value for key, value in Game.ClassCards["Hunter"].items() if "~Spell~" in key]
		
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [AddaHunterSpelltoHand(self)]
		
class AddaHunterSpelltoHand(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		curGame = self.entity.Game
		if curGame.mode == 0:
			if curGame.guides:
				spell = curGame.guides.pop(0)
			else:
				spell = npchoice(self.rngPool("Hunter Spells"))
				curGame.fixedGuides.append(spell)
			curGame.Hand_Deck.addCardtoHand(spell, self.entity.ID, byType=True)
			
	def text(self, CHN):
		return "亡语：随机将一张猎人法术牌置入你的手牌" if CHN \
				else "Deathrattle: Add a random Hunter spell to your hand"
				
				
class NineLives(Spell):
	Class, school, name = "Hunter", "", "Nine Lives"
	requireTarget, mana = False, 3
	index = "DALARAN~Hunter~Spell~3~Nine Lives"
	description = "Discover a friendly Deathrattle minion that died this game. Also trigger its Deathrattle"
	name_CN = "九命兽魂"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if curGame.mode == 0:
			if curGame.guides:
				minion = curGame.guides.pop(0)
				if minion:
					minion = minion(curGame, self.ID)
					curGame.Hand_Deck.addCardtoHand(minion, self.ID, byDiscover=True)
					for trig in minion.deathrattles:
						trig.trig("TrigDeathrattle", self.ID, None, minion, minion.attack, "")
			else:
				minions, indices = [], []
				for index in curGame.Counters.minionsDiedThisGame[self.ID]:
					if "~Deathrattle" in index and index not in indices:
						minions.append(curGame.cardPool[index])
						indices.append(index)
				if minions:
					if self.ID != curGame.turn or "byOthers" in comment:
						minion = npchoice(minions)
						curGame.fixedGuides.append(minion)
						minion = minion(curGame, self.ID)
						curGame.Hand_Deck.addCardtoHand(minion, self.ID, byDiscover=True)
						for trig in minion.deathrattles:
							trig.trig("TrigDeathrattle", self.ID, None, minion, minion.attack, "")
					else:
						minions = npchoice(minions, min(3, len(minions)), replace=False)
						curGame.options = [curGame.cardPool[minion](curGame, self.ID) for minion in minions]
						curGame.Discover.startDiscover(self)
				else:
					curGame.fixedGuides.append(None)
		return None
		
	def discoverDecided(self, option, pool):
		self.Game.fixedGuides.append(type(option))
		self.Game.Hand_Deck.addCardtoHand(option, self.ID, byDiscover=True)
		for trig in option.deathrattles:
			trig.trig("TrigDeathrattle", self.ID, None, option, option.attack, "")
			
			
class Ursatron(Minion):
	Class, race, name = "Hunter", "Mech", "Ursatron"
	mana, attack, health = 3, 3, 3
	index = "DALARAN~Hunter~Minion~3~3~3~Mech~Ursatron~Deathrattle"
	requireTarget, keyWord, description = False, "", "Deathrattle: Draw a Mech from your deck"
	name_CN = "机械巨熊"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [DrawaMech(self)]
		
class DrawaMech(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		curGame = self.entity.Game
		if curGame.mode == 0:
			if curGame.guides:
				i = curGame.guides.pop(0)
			else:
				mechs = [i for i, card in enumerate(curGame.Hand_Deck.decks[self.entity.ID]) if card.type == "Minion" and "Mech" in card.race]
				i = npchoice(mechs)	if mechs else -1
				curGame.fixedGuides.append(i)
			if i > -1: curGame.Hand_Deck.drawCard(self.entity.ID, i)
			
	def text(self, CHN):
		return "亡语：从你的牌库中抽一张机械牌" if CHN else "Deathrattle: Draw a Mech from your deck"
		
		
class ArcaneFletcher(Minion):
	Class, race, name = "Hunter", "", "Arcane Fletcher"
	mana, attack, health = 4, 3, 3
	index = "DALARAN~Hunter~Minion~4~3~3~~Arcane Fletcher"
	requireTarget, keyWord, description = False, "", "Whenever you play a 1-Cost minion, draw a spell from your deck"
	name_CN = "奥术弓箭手"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_ArcaneFletcher(self)]
		
class Trig_ArcaneFletcher(TrigBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionPlayed"])
	#The number here is the mana used to play the minion
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject != self.entity and subject.ID == self.entity.ID and number == 1
		
	def text(self, CHN):
		return "每当你使用一张法力值消耗为(1)的随从牌，从你的牌库中抽一张法术牌" if CHN \
				else "Whenever you play a 1-Cost minion, draw a spell from your deck"
				
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		curGame = self.entity.Game
		if curGame.mode == 0:
			if curGame.guides:
				i = curGame.guides.pop(0)
			else:
				spells = [i for i, card in enumerate(curGame.Hand_Deck.decks[self.entity.ID]) if card.type == "Spell"]
				i = npchoice(spells) if spells else -1
				curGame.fixedGuides.append(i)
			if i > -1: curGame.Hand_Deck.drawCard(self.entity.ID, i)
			
			
class MarkedShot(Spell):
	Class, school, name = "Hunter", "", "Marked Shot"
	requireTarget, mana = True, 4
	index = "DALARAN~Hunter~Spell~4~Marked Shot"
	description = "Deal 4 damage to a minion. Discover a Spell"
	name_CN = "标记射击"
	poolIdentifier = "Hunter Spells"
	@classmethod
	def generatePool(cls, Game):
		return [Class+" Spells" for Class in Game.Classes], \
				[[value for key, value in Game.ClassCards[Class].items() if "~Spell~" in key] for Class in Game.Classes]
				
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
		
	def text(self, CHN):
		damage = (4 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		return "对一个随从造成%d点伤害。发现一张猎人法术牌"%damage if CHN \
				else "Deal %d damage to a minion. Discover a Spell"%damage
				
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if target:
			damage = (4 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			self.dealsDamage(target, damage)
			if curGame.mode == 0:
				if curGame.guides:
					curGame.Hand_Deck.addCardtoHand(curGame.guides.pop(0), self.ID, byType=True, byDiscover=True)
				else:
					key = classforDiscover(self)+" Spells"
					if self.ID != curGame.turn or "byOthers" in comment:
						spell = npchoice(self.rngPool(key))
						curGame.fixedGuides.append(spell)
						curGame.Hand_Deck.addCardtoHand(spell, self.ID, byType=True, byDiscover=True)
					else:
						spells = npchoice(self.rngPool(key), 3, replace=False)
						curGame.options = [spell(curGame, self.ID) for spell in spells]
						curGame.Discover.startDiscover(self)
		return target
		
	def discoverDecided(self, option, pool):
		self.Game.fixedGuides.append(type(option))
		self.Game.Hand_Deck.addCardtoHand(option, self.ID, byDiscover=True)
		
		
class HuntingParty(Spell):
	Class, school, name = "Hunter", "", "Hunting Party"
	requireTarget, mana = False, 5
	index = "DALARAN~Hunter~Spell~5~Hunting Party"
	description = "Copy all Beasts in your hand"
	name_CN = "狩猎盛宴"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if self.Game.Hand_Deck.handNotFull(self.ID):
			copies = []
			for card in self.Game.Hand_Deck.hands[self.ID]:
				if card.type == "Minion" and "Beast" in card.race:
					copies.append(card.selfCopy(self.ID))
					
			for Copy in copies:
				self.Game.Hand_Deck.addCardtoHand(Copy, self.ID)
		return None
		
class Oblivitron(Minion):
	Class, race, name = "Hunter", "Mech", "Oblivitron"
	mana, attack, health = 6, 3, 4
	index = "DALARAN~Hunter~Minion~6~3~4~Mech~Oblivitron~Deathrattle~Legendary"
	requireTarget, keyWord, description = False, "", "Deathrattle: Summon a Mech from your hand and trigger its Deathrattle"
	name_CN = "湮灭战车"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [SummonMechfromHandandTriggeritsDeathrattle(self)]
		
class SummonMechfromHandandTriggeritsDeathrattle(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		minion = self.entity
		curGame = minion.Game
		if curGame.mode == 0:
			if curGame.guides:
				i = curGame.guides.pop(0)
			else:
				mechs = [i for i, card in enumerate(curGame.Hand_Deck.hands[minion.ID]) if card.type == "Minion" and "Mech" in card.race]
				i = npchoice(mechs) if mechs and curGame.space(minion.ID) > 0 else -1
				curGame.fixedGuides.append(i)
			if i > -1:
				mech = curGame.summonfrom(i, minion.ID, minion.pos+1, minion, fromHand=True)
				for trig in mech.deathrattles:
					trig.trig("TrigDeathrattle", minion.ID, None, mech, mech.attack, "")
					
	def text(self, CHN):
		return "亡语：从你的手牌中召唤一个机械，并触其亡语" if CHN \
				else "Deathrattle: Summon a Mech from your hand and trigger its Deathrattle"
				
				
class UnleashtheBeast(Spell):
	Class, school, name = "Hunter", "", "Unleash the Beast"
	requireTarget, mana = False, 6
	index = "DALARAN~Hunter~Spell~6~Unleash the Beast~Twinspell"
	description = "Twinspell. Summon a 5/5 Wyvern with Rush"
	name_CN = "猛兽出笼"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.twinSpell = 1
		self.twinSpellCopy = UnleashtheBeast2
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.Game.summon(Wyvern(self.Game, self.ID), -1, self)
		return None
		
class UnleashtheBeast2(Spell):
	Class, school, name = "Hunter", "", "Unleash the Beast"
	requireTarget, mana = False, 6
	index = "DALARAN~Hunter~Spell~6~Unleash the Beast~Uncollectible"
	description = "Summon a 5/5 Wyvern with Rush"
	name_CN = "猛兽出笼"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.Game.summon(Wyvern(self.Game, self.ID), -1, self)
		return None
		
class Wyvern(Minion):
	Class, race, name = "Hunter", "Beast", "Wyvern"
	mana, attack, health = 5, 5, 5
	index = "DALARAN~Hunter~Minion~5~5~5~Beast~Wyvern~Rush~Uncollectible"
	requireTarget, keyWord, description = False, "Rush", "Rush"
	name_CN = "双足飞龙"
	
	
class VereesaWindrunner(Minion):
	Class, race, name = "Hunter", "", "Vereesa Windrunner"
	mana, attack, health = 7, 5, 6
	index = "DALARAN~Hunter~Minion~7~5~6~~Vereesa Windrunner~Battlecry~Legendary"
	requireTarget, keyWord, description = False, "", "Battlecry: Equip Thori'dal, the Stars' Fury"
	name_CN = "温蕾萨·风行者"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.Game.equipWeapon(ThoridaltheStarsFury(self.Game, self.ID))
		return None
		
class ThoridaltheStarsFury(Weapon):
	Class, name, description = "Hunter", "Thori'dal, the Stars' Fury", "After your hero attacks, gain Spell Damage +2 this turn"
	mana, attack, durability = 3, 2, 3
	index = "DALARAN~Hunter~Weapon~3~2~3~Thori'dal, the Stars' Fury~Legendary~Uncollectible"
	name_CN = "索利达尔， 群星之怒"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_ThoridaltheStarsFury(self)]
		
class Trig_ThoridaltheStarsFury(TrigBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["HeroAttackedMinion", "HeroAttackedHero"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject.ID == self.entity.ID and self.entity.onBoard
		
	def text(self, CHN):
		return "在你的英雄攻击后，在本回合中获得法术伤害+2" if CHN \
				else "After your hero attacks, gain Spell Damage +2 this turn"
				
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.Game.status[self.entity.ID]["Spell Damage"] += 2
		self.entity.Game.turnEndTrigger.append(ThoridaltheStarsFury_Effect(self.entity.Game, self.entity.ID))
		
class ThoridaltheStarsFury_Effect:
	def __init__(self, Game, ID):
		self.Game, self.ID = Game, ID
		
	def turnEndTrigger(self):
		self.Game.status[self.ID]["Spell Damage"] -= 2
		try: self.Game.turnEndTrigger.remove(self)
		except: pass
		
	def createCopy(self, game):
		return type(self)(game, self.ID)
		
"""Mage cards"""
class RayofFrost(Spell):
	Class, school, name = "Mage", "Frost", "Ray of Frost"
	requireTarget, mana = True, 1
	index = "DALARAN~Mage~Spell~1~Frost~Ray of Frost~Twinspell"
	description = "Twinspell. Freeze a minion. If it's already Frozen, deal 2 damage to it"
	name_CN = "霜冻射线"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.twinSpell = 1
		self.twinSpellCopy = RayofFrost2
		
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
		
	def text(self, CHN):
		damage = (2 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		return "双生法术。冻结一个随从。如果该随从已被冻结，则对其造成%d点伤害"%damage if CHN \
				else "Twinspell. Freeze a minion. If it's already Frozen, deal %d damage to it"%damage
				
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			if target.status["Frozen"]:
				damage = (2 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
				self.dealsDamage(target, damage)
			else:
				target.getsFrozen()
		return target
		
class RayofFrost2(Spell):
	Class, school, name = "Mage", "Frost", "Ray of Frost"
	requireTarget, mana = True, 1
	index = "DALARAN~Mage~Spell~1~Frost~Ray of Frost~Uncollectible"
	description = "Freeze a minion. If it's already Frozen, deal 2 damage to it"
	name_CN = "霜冻射线"
	
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
		
	def text(self, CHN):
		damage = (2 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		return "冻结一个随从。如果该随从已被冻结，则对其造成%d点伤害"%damage if CHN \
				else "Freeze a minion. If it's already Frozen, deal %d damage to it"%damage
				
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			if target.status["Frozen"]:
				damage = (2 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
				self.dealsDamage(target, damage)
			else:
				target.getsFrozen()
		return target
		
		
#卡德加在场时，连续从手牌或者牌库中召唤随从时，会一个一个的召唤，然后根据卡德加的效果进行双倍，如果双倍召唤提前填满了随从池，则后面的被招募随从就不再离开牌库或者手牌。，
#两个卡德加在场时，召唤数量会变成4倍。（卡牌的描述是翻倍）
#两个卡德加时，打出鱼人猎潮者，召唤一个1/1鱼人。会发现那个1/1鱼人召唤之后会在那个鱼人右侧再召唤一个（第一个卡德加的翻倍），然后第二个卡德加的翻倍触发，在最最左边的鱼人的右边召唤两个鱼人。
#当场上有卡德加的时候，灰熊守护者的亡语招募两个4费以下随从，第一个随从召唤出来时被翻倍，然后第二召唤出来的随从会出现在第一个随从的右边，然后翻倍，结果是后面出现的一对随从夹在第一对随从之间。
#对一次性召唤多个随从的机制的猜测应该是每一个新出来的随从都会盯紧之前出现的那个随从，然后召唤在那个随从的右边。如果之前召唤那个随从引起了新的随从召唤，无视之。
#目前没有在连续召唤随从之间出现随从提前离场的情况。上面提到的始终紧盯是可以实现的。
class Khadgar(Minion):
	Class, race, name = "Mage", "", "Khadgar"
	mana, attack, health = 2, 2, 2
	index = "DALARAN~Mage~Minion~2~2~2~~Khadgar~Legendary"
	requireTarget, keyWord, description = False, "", "Your cards that summon minions summon twice as many"
	name_CN = "卡德加"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.auras["Your cards that summon minions summon twice as many"] = GameRuleAura_Khadgar(self)
		
class GameRuleAura_Khadgar(GameRuleAura):
	def auraAppears(self):
		self.entity.Game.status[self.entity.ID]["Summon x2"] += 1
		
	def auraDisappears(self):
		self.entity.Game.status[self.entity.ID]["Summon x2"] -= 1
		
		
class MagicDartFrog(Minion):
	Class, race, name = "Mage", "Beast", "Magic Dart Frog"
	mana, attack, health = 2, 1, 3
	index = "DALARAN~Mage~Minion~2~1~3~Beast~Magic Dart Frog"
	requireTarget, keyWord, description = False, "", "After you cast a spell, deal 1 damage to a random enemy minion"
	name_CN = "魔法蓝蛙"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_MagicDartFrog(self)]
		
class Trig_MagicDartFrog(TrigBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["SpellBeenPlayed"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject.ID == self.entity.ID
		
	def text(self, CHN):
		return "在你施放一个法术后，随机对一个敌方随从造成1伤害" if CHN \
				else "After you cast a spell, deal 1 damage to a random enemy minion"
				
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		curGame = self.entity.Game
		if curGame.mode == 0:
			if curGame.guides:
				i = curGame.guides.pop(0)
			else:
				minions = curGame.minionsAlive(3-self.entity.ID)
				i = npchoice(minions).pos if minions else -1
				curGame.fixedGuides.append(i)
			if i > -1:
				self.entity.dealsDamage(curGame.minions[3-self.entity.ID][i], 1)
				
				
class MessengerRaven(Minion):
	Class, race, name = "Mage", "Beast", "Messenger Raven"
	mana, attack, health = 3, 3, 2
	index = "DALARAN~Mage~Minion~3~3~2~Beast~Messenger Raven~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Discover a Mage minion"
	name_CN = "渡鸦信使"
	poolIdentifier = "Mage Minions"
	@classmethod
	def generatePool(cls, Game):
		return "Mage Minions", [value for key, value in Game.ClassCards["Mage"].items() if "~Minion~" in key]
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if self.ID == curGame.turn:
			if curGame.mode == 0:
				if curGame.guides:
					curGame.Hand_Deck.addCardtoHand(curGame.guides.pop(0), self.ID, byType=True, byDiscover=True)
				else:
					if "byOthers" in comment:
						minion = npchoice(self.rngPool("Mage Minions"))
						curGame.fixedGuides.append(minion)
						curGame.Hand_Deck.addCardtoHand(minion, self.ID, byType=True, byDiscover=True)
					else:
						minions = npchoice(self.rngPool("Mage Minions"), 3, replace=False)
						curGame.options = [minion(curGame, self.ID) for minion in minions]
						curGame.Discover.startDiscover(self)
		return None
		
	def discoverDecided(self, option, pool):
		self.Game.fixedGuides.append(type(option))
		self.Game.Hand_Deck.addCardtoHand(option, self.ID, byDiscover=True)
		
		
class MagicTrick(Spell):
	Class, school, name = "Mage", "Arcane", "Magic Trick"
	requireTarget, mana = False, 1
	index = "DALARAN~Mage~Spell~1~Arcane~Magic Trick"
	description = "Discover a spell that costs (3) or less"
	name_CN = "魔术戏法"
	poolIdentifier = "Spells 3-Cost or less as Mage"
	@classmethod
	def generatePool(cls, Game):
		return ["Spells 3-Cost or less as %s"%Class for Class in Game.Classes], \
				[[value for key, value in Game.ClassCards[Class].items() if "~Spell~" in key and int(key.split('~')[3]) < 4] for Class in Game.Classes]
				
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if self.ID == curGame.turn:
			if curGame.mode == 0:
				if curGame.guides:
					curGame.Hand_Deck.addCardtoHand(curGame.guides.pop(0), self.ID, byType=True, byDiscover=True)
				else:
					key = "Spells 3-Cost or less as "+classforDiscover(self)
					if self.ID != curGame.turn or "byOthers" in comment:
						spell = npchoice(self.rngPool(key))
						curGame.fixedGuides.append(spell)
						curGame.Hand_Deck.addCardtoHand(spell, self.ID, byType=True, byDiscover=True)
					else:
						spells = npchoice(self.rngPool(key), 3, replace=False)
						curGame.options = [spell(curGame, self.ID) for spell in spells]
						curGame.Discover.startDiscover(self)
		return None
		
	def discoverDecided(self, option, pool):
		self.Game.fixedGuides.append(type(option))
		self.Game.Hand_Deck.addCardtoHand(option, self.ID, byDiscover=True)
		
		
class ConjurersCalling(Spell):
	Class, school, name = "Mage", "Arcane", "Conjurer's Calling"
	requireTarget, mana = True, 4
	index = "DALARAN~Mage~Spell~4~Arcane~Conjurer's Calling~Twinspell"
	description = "Twinspell. Destroy a minion. Summon 2 minions of the same Cost to replace it"
	name_CN = "咒术师的召唤"
	poolIdentifier = "1-Cost Minions to Summon"
	@classmethod
	def generatePool(cls, Game):
		return ["%d-Cost Minions to Summon"%cost for cost in Game.MinionsofCost.keys()], \
				[list(Game.MinionsofCost[cost].values()) for cost in Game.MinionsofCost.keys()]
				
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.twinSpell = 1
		self.twinSpellCopy = ConjurersCalling2
		
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
	#首先记录随从当前场上位置，强制死亡然后检测当前场上情况，然后在相同位置上召唤两个随从
	#例如，自爆绵羊在生效前是场上第3个随从，强制死亡并结算所有死亡情况之后，在场上的第3个位置召唤两个随从（即第2个随从的右边）
	#如果位置溢出，则直接召唤到场上的最右边。
	#当与风潮配合而生效两次的时候，第一次召唤随从是在原来的位置，之后的召唤是在最右边。说明第二次生效时目标已经被初始化，失去了原有的位置信息。
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			curGame = self.Game
			cost = type(target).mana
			key = "%d-Cost Minions to Summon"%cost
			targetID, position = target.ID, target.pos
			if target.onBoard: curGame.killMinion(self, target)
			elif target.inHand: self.Game.Hand_Deck.discard(target) #如果随从在手牌中则将其丢弃
			#强制死亡需要在此插入死亡结算，并让随从离场
			curGame.gathertheDead()
			if curGame.mode == 0:
				if curGame.guides:
					minions = list(curGame.guides.pop(0))
				else:
					minions = npchoice(self.rngPool(key), 2, replace=True)
					curGame.fixedGuides.append(tuple(minions))
			if position == 0: pos = (-1, "totheRight") #Summon to the leftmost
			#如果目标之前是第4个(position=3)，则场上最后只要有3个随从或者以下，就会召唤到最右边。
			#如果目标不在场上或者是第二次生效时已经死亡等被初始化，则position=-2会让新召唤的随从在场上最右边。
			elif position < 0 or position >= len(curGame.minionsonBoard(targetID)):
				pos = (-1, "totheRightEnd")
			else: pos = (position, "totheRight")
			curGame.summon([minion(curGame, target.ID) for minion in minions], pos, self)
		return target
		
class ConjurersCalling2(Spell):
	Class, school, name = "Mage", "Arcane", "Conjurer's Calling"
	requireTarget, mana = True, 4
	index = "DALARAN~Mage~Spell~4~Arcane~Conjurer's Calling~Uncollectible"
	description = "Destroy a minion. Summon 2 minions of the same Cost to replace it"
	name_CN = "咒术师的召唤"
	
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			curGame = self.Game
			cost = type(target).mana
			key = "%d-Cost Minions to Summon"%cost
			targetID, position = target.ID, target.pos
			if target.onBoard: curGame.killMinion(self, target)
			elif target.inHand: self.Game.Hand_Deck.discard(target) #如果随从在手牌中则将其丢弃
			#强制死亡需要在此插入死亡结算，并让随从离场
			curGame.gathertheDead()
			if curGame.mode == 0:
				if curGame.guides:
					minions = list(curGame.guides.pop(0))
				else:
					minions = npchoice(self.rngPool(key), 2, replace=True)
					curGame.fixedGuides.append(tuple(minions))
			if position == 0: pos = (-1, "totheRight") #Summon to the leftmost
			#如果目标之前是第4个(position=3)，则场上最后只要有3个随从或者以下，就会召唤到最右边。
			#如果目标不在场上或者是第二次生效时已经死亡等被初始化，则position=-2会让新召唤的随从在场上最右边。
			elif position < 0 or position >= len(curGame.minionsonBoard(targetID)):
				pos = (-1, "totheRightEnd")
			else: pos = (position, "totheRight")
			curGame.summon([minion(curGame, target.ID) for minion in minions], pos, self)
		return target
		
		
class KirinTorTricaster(Minion):
	Class, race, name = "Mage", "", "Kirin Tor Tricaster"
	mana, attack, health = 4, 3, 3
	index = "DALARAN~Mage~Minion~4~3~3~~Kirin Tor Tricaster"
	requireTarget, keyWord, description = False, "", "Spell Damage +3. Your spells cost (1) more"
	name_CN = "肯瑞托 三修法师"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.keyWords["Spell Damage"] = 3
		self.auras["Your spells cost (1) more"] = ManaAura(self, +1, -1)
		
	def manaAuraApplicable(self, subject):
		return subject.ID == self.ID and subject.type == "Spell"
		
		
class ManaCyclone(Minion):
	Class, race, name = "Mage", "Elemental", "Mana Cyclone"
	mana, attack, health = 2, 2, 2
	index = "DALARAN~Mage~Minion~2~2~2~Elemental~Mana Cyclone~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: For each spell you've cast this turn, add a random Mage spell to your hand"
	name_CN = "法力飓风"
	poolIdentifier = "Mage Spells"
	@classmethod
	def generatePool(cls, Game):
		return "Mage Spells", [value for key, value in Game.ClassCards["Mage"].items() if "~Spell~" in key]
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if curGame.mode == 0:
			if curGame.guides:
				spells = curGame.guides.pop(0)
			else:
				num = min(curGame.Hand_Deck.spaceinHand(self.ID), curGame.Counters.numSpellsPlayedThisTurn[self.ID])
				spells = tuple(npchoice(self.rngPool("Mage Spells"), num, replace=True)) if num else ()
				curGame.fixedGuides.append(spells)
			if spells: curGame.Hand_Deck.addCardtoHand(spells, self.ID, byType=True)
		return None
		
		
class PowerofCreation(Spell):
	Class, school, name = "Mage", "Arcane", "Power of Creation"
	requireTarget, mana = False, 8
	index = "DALARAN~Mage~Spell~8~Arcane~Power of Creation"
	description = "Discover a 6-Cost minion. Summon two copies of it"
	name_CN = "创世之力"
	poolIdentifier = "6-Cost Minions as Mage to Summon"
	@classmethod
	def generatePool(cls, Game):
		classes = ["6-Cost Minions as %s to Summon"%Class for Class in Game.Classes]
		classCards = {s : [] for s in Game.ClassesandNeutral}
		for key, value in Game.MinionsofCost[6].items():
			for Class in key.split('~')[1].split(','):
				classCards[Class].append(value)
		return classes, [classCards[Class]+classCards["Neutral"] for Class in Game.Classes]
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if curGame.mode == 0:
			if curGame.guides:
				minion = curGame.guides.pop(0)
				curGame.summon([minion(curGame, self.ID) for i in range(2)], (-1, "totheRightEnd"), self)
			else:
				key = "6-Cost Minions as %s to Summon"%classforDiscover(self)
				if self.ID != curGame.turn or "byOthers" in comment:
					minion = npchoice(self.rngPool(key))
					curGame.fixedGuides.append(minion)
					curGame.summon([minion(curGame, self.ID) for i in range(2)], (-1, "totheRightEnd"), self)
				else:
					minions = npchoice(self.rngPool(key), 3, replace=False)
					curGame.options = [minion(curGame, self.ID) for minion in minions]
					curGame.Discover.startDiscover(self)
		return None
		
	def discoverDecided(self, option, pool):
		self.Game.fixedGuides.append(type(option))
		self.Game.summon([option, type(option)(self.Game, self.ID)], (-1, "totheRightEnd"), self)
		
		
class Kalecgos(Minion):
	Class, race, name = "Mage", "Dragon", "Kalecgos"
	mana, attack, health = 10, 4, 12
	index = "DALARAN~Mage~Minion~10~4~12~Dragon~Kalecgos~Legendary"
	requireTarget, keyWord, description = False, "", "Your first spell costs (0) each turn. Battlecry: Discover a spell"
	name_CN = "卡雷苟斯"
	poolIdentifier = "Mage Spells"
	@classmethod
	def generatePool(cls, Game):
		return [Class+" Spells" for Class in Game.Classes], \
				[[value for key, value in Game.ClassCards[Class].items() if "~Spell~" in key] for Class in Game.Classes]
				
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.auras["Your first spell costs (0) each turn"] = ManaAura_1stSpell0(self)
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if self.ID == curGame.turn:
			if curGame.mode == 0:
				if curGame.guides:
					curGame.Hand_Deck.addCardtoHand(curGame.guides.pop(0), self.ID, byType=True, byDiscover=True)
				else:
					key = classforDiscover(self)+" Spells"
					if "byOthers" in comment:
						spell = npchoice(self.rngPool(key))
						curGame.fixedGuides.append(spell)
						curGame.Hand_Deck.addCardtoHand(spell, self.ID, byType=True, byDiscover=True)
					else:
						spells = npchoice(self.rngPool(key), 3, replace=False)
						curGame.options = [spell(curGame, self.ID) for spell in spells]
						curGame.Discover.startDiscover(self)
		return None
		
	def discoverDecided(self, option, pool):
		self.Game.fixedGuides.append(type(option))
		self.Game.Hand_Deck.addCardtoHand(option, self.ID, byDiscover=True)
		
class GameManaAura_InTurn1stSpell0(TempManaEffect):
	def __init__(self, Game, ID, changeby=0, changeto=-1):
		self.blank_init(Game, ID, 0, 0)
		
	def applicable(self, target):
		return target.ID == self.ID and target.type == "Spell"
		
class ManaAura_1stSpell0(ManaAura_1UsageEachTurn):
	def auraAppears(self):
		game, ID = self.entity.Game, self.entity.ID
		if game.turn == ID and game.Counters.numSpellsPlayedThisTurn[ID] < 1:
			self.aura = GameManaAura_InTurn1stSpell0(game, ID)
			game.Manas.CardAuras.append(self.aura)
			self.aura.auraAppears()
		try: game.trigsBoard[ID]["TurnStarts"].append(self)
		except: game.trigsBoard[ID]["TurnStarts"] = [self]
		
		
class NeverSurrender(Secret):
	Class, school, name = "Paladin", "", "Never Surrender!"
	requireTarget, mana = False, 1
	index = "DALARAN~Paladin~Spell~1~Never Surrender!~~Secret"
	description = "Secret: Whenever your opponent casts a spell, give your minions +2 Health"
	name_CN = "永不屈服"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_NeverSurrender(self)]
		
class Trig_NeverSurrender(SecretTrigger):
	def __init__(self, entity):
		self.blank_init(entity, ["SpellPlayed"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.ID != self.entity.Game.turn and subject.ID != self.entity.ID and self.entity.Game.minionsonBoard(self.entity.ID) != []
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		for minion in self.entity.Game.minionsonBoard(self.entity.ID):
			minion.buffDebuff(0, 2)
			
			
class LightforgedBlessing(Spell):
	Class, school, name = "Paladin", "Holy", "Lightforged Blessing"
	requireTarget, mana = True, 2
	index = "DALARAN~Paladin~Spell~2~Holy~Lightforged Blessing~Twinspell"
	description = "Twinspell. Give a friendly minion Lifesteal"
	name_CN = "光铸祝福"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.twinSpell = 1
		self.twinSpellCopy = LightforgedBlessing2
		
	def available(self):
		return self.selectableFriendlyMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.ID == self.ID and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			target.getsKeyword("Lifesteal")
		return target
		
class LightforgedBlessing2(Spell):
	Class, school, name = "Paladin", "", "Lightforged Blessing"
	requireTarget, mana = True, 2
	index = "DALARAN~Paladin~Spell~2~Lightforged Blessing~Uncollectible"
	description = "Give a friendly minion Lifesteal"
	name_CN = "光铸祝福"
	
	def available(self):
		return self.selectableFriendlyMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.ID == self.ID and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			target.getsKeyword("Lifesteal")
		return target
		
		
class BronzeHerald(Minion):
	Class, race, name = "Paladin", "Dragon", "Bronze Herald"
	mana, attack, health = 3, 3, 2
	index = "DALARAN~Paladin~Minion~3~3~2~Dragon~Bronze Herald~Deathrattle"
	requireTarget, keyWord, description = False, "", "Deathrattle: Add two 4/4 Dragons to your hand"
	name_CN = "青铜传令官"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [AddTwoBronzeDragonstoHand(self)]
		
class AddTwoBronzeDragonstoHand(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.Game.Hand_Deck.addCardtoHand([BronzeDragon, BronzeDragon], self.entity.ID, byType=True)
		
	def text(self, CHN):
		return "亡语：将两张4/4的“青铜传令官”置入你的手牌" if CHN else "Deathrattle: Add Two 4/4 Bronze Dragons to your hand"
		
class BronzeDragon(Minion):
	Class, race, name = "Paladin", "Dragon", "Bronze Dragon"
	mana, attack, health = 4, 4, 4
	index = "DALARAN~Paladin~Minion~4~4~4~Dragon~Bronze Dragon~Uncollectible"
	requireTarget, keyWord, description = False, "", ""
	name_CN = "青铜龙"
	
	
class DesperateMeasures(Spell):
	Class, school, name = "Paladin", "", "Desperate Measures"
	requireTarget, mana = False, 1
	index = "DALARAN~Paladin~Spell~1~Desperate Measures~Twinspell"
	description = "Twinspell. Cast a random Paladin Secrets"
	name_CN = "孤注一掷"
	poolIdentifier = "Paladin Secrets"
	@classmethod
	def generatePool(cls, Game):
		return "Paladin Secrets", [value for key, value in Game.ClassCards["Paladin"].items() if value.description.startswith("Secret:")]
		
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.twinSpell = 1
		self.twinSpellCopy = DesperateMeasures2
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if curGame.mode == 0:
			if curGame.guides:
				secret = curGame.guides.pop(0)
			else:
				secrets = [value for value in self.rngPool("Paladin Secrets") if not curGame.Secrets.sameSecretExists(value, self.ID)]
				secret = npchoice(secrets) if secrets else None
				curGame.fixedGuides.append(secret)
			if secret: secret(curGame, self.ID).cast()
		return None
		
class DesperateMeasures2(Spell):
	Class, school, name = "Paladin", "", "Desperate Measures"
	requireTarget, mana = False, 1
	index = "DALARAN~Paladin~Spell~1~Desperate Measures~Uncollectible"
	description = "Cast a random Paladin Secrets"
	name_CN = "孤注一掷"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if curGame.mode == 0:
			if curGame.guides:
				secret = curGame.guides.pop(0)
			else:
				secrets = [value for value in self.rngPool("Paladin Secrets") if not curGame.Secrets.sameSecretExists(value, self.ID)]
				secret = npchoice(secrets) if secrets else None
				curGame.fixedGuides.append(secret)
			if secret: secret(curGame, self.ID).cast()
		return None
		
		
class MysteriousBlade(Weapon):
	Class, name, description = "Paladin", "Mysterious Blade", "Battlecry: If you control a Secret, gain +1 Attack"
	mana, attack, durability = 2, 2, 2
	index = "DALARAN~Paladin~Weapon~2~2~2~Mysterious Blade~Battlecry"
	name_CN = "神秘之刃"
	def effCanTrig(self):
		self.effectViable = self.Game.Secrets.secrets[self.ID] != []
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if self.Game.Secrets.secrets[self.ID] != []:
			self.gainStat(1, 0)
		return None
		
		
class CalltoAdventure(Spell):
	Class, school, name = "Paladin", "", "Call to Adventure"
	requireTarget, mana = False, 3
	index = "DALARAN~Paladin~Spell~3~Call to Adventure"
	description = "Draw the lowest Cost minion from your deck. Give it +2/+2"
	name_CN = "冒险号角"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if curGame.mode == 0:
			if curGame.guides:
				i = curGame.guides.pop(0)
			else:
				minions, lowestCost = [], npinf
				for i, card in enumerate(curGame.Hand_Deck.decks[self.ID]):
					if card.type == "Minion":
						if card.mana < lowestCost: minions, lowestCost = [i], card.mana
						elif card.mana == lowestCost: minions.append(i)
				i = npchoice(minions) if minions else -1
				curGame.fixedGuides.append(i)
			if i > -1:
				minion = self.Game.Hand_Deck.drawCard(self.ID, i)[0]
				if minion: minion.buffDebuff(2, 2)
		return None
		
		
class DragonSpeaker(Minion):
	Class, race, name = "Paladin", "", "Dragon Speaker"
	mana, attack, health = 5, 3, 5
	index = "DALARAN~Paladin~Minion~5~3~5~~Dragon Speaker~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Give all Dragons in your hand +3/+3"
	name_CN = "龙语者"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		for card in self.Game.Hand_Deck.hands[self.ID]:
			if card.type == "Minion" and "Dragon" in card.race:
				card.buffDebuff(3, 3)
		return None
		
#Friendly minion attacks. If the the minion has "Can't Attack", then it won't attack.
#Attackchances won't be consumed. If it survives, it can attack again. triggers["DealsDamage"] functions can trigger.
class Duel(Spell):
	Class, school, name = "Paladin", "", "Duel!"
	requireTarget, mana = False, 5
	index = "DALARAN~Paladin~Spell~5~Duel!"
	description = "Summon a minion from each player's deck. They fight"
	name_CN = "决斗"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if curGame.mode == 0:
			if curGame.guides:
				i, j = curGame.guides.pop(0)
			else:
				enemyMinions = [i for i, card in enumerate(curGame.Hand_Deck.decks[3-self.ID]) if card.type == "Minion"]
				friendlyMinions = [i for i, card in enumerate(curGame.Hand_Deck.decks[self.ID]) if card.type == "Minion"]
				i = npchoice(friendlyMinions) if friendlyMinions and curGame.space(self.ID) > 0 else -1
				j = npchoice(enemyMinions) if enemyMinions and curGame.space(3-self.ID) > 0 else -1
				curGame.fixedGuides.append((i, j))
			enemy, friendly = None, None
			if i > -1: friendly = curGame.summonfrom(i, self.ID, -1, self, fromHand=False)
			if j > -1: enemy = curGame.summonfrom(j, 3-self.ID, -1, self, fromHand=False)
			#如果我方随从有不能攻击的限制，如Ancient Watcher之类，不能攻击。
			#攻击不消耗攻击机会
			#需要测试有条件限制才能攻击的随从，如UnpoweredMauler
			if friendly and enemy and friendly.marks["Can't Attack"] < 1:
				curGame.battle(friendly, enemy, verifySelectable=False, useAttChance=False, resolveDeath=False)
		return None
		
		
class CommanderRhyssa(Minion):
	Class, race, name = "Paladin", "", "Commander Rhyssa"
	mana, attack, health = 3, 4, 3
	index = "DALARAN~Paladin~Minion~3~4~3~~Commander Rhyssa~Legendary"
	requireTarget, keyWord, description = False, "", "Your Secrets trigger twice"
	name_CN = "指挥官蕾撒"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.auras["Your Secrets trigger twice"] = GameRuleAura_CommanderRhyssa(self)
		
class GameRuleAura_CommanderRhyssa(GameRuleAura):
	def auraAppears(self):
		self.entity.Game.status[self.entity.ID]["Secrets x2"] += 1
		
	def auraDisappears(self):
		self.entity.Game.status[self.entity.ID]["Secrets x2"] -= 1
		
		
class Nozari(Minion):
	Class, race, name = "Paladin", "Dragon", "Nozari"
	mana, attack, health = 10, 4, 12
	index = "DALARAN~Paladin~Minion~10~4~12~Dragon~Nozari~Battlecry~Legendary"
	requireTarget, keyWord, description = False, "", "Battlecry: Restore both heroes to full Health"
	name_CN = "诺萨莉"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		heal1 = self.Game.heroes[1].health_max * (2 ** self.countHealDouble())
		heal2 = self.Game.heroes[2].health_max * (2 ** self.countHealDouble())
		self.restoresAOE([self.Game.heroes[1], self.Game.heroes[2]], [heal1, heal2])
		return None
		
"""Priest cards"""
class EVILConscripter(Minion):
	Class, race, name = "Priest", "", "EVIL Conscripter"
	mana, attack, health = 2, 2, 2
	index = "DALARAN~Priest~Minion~2~2~2~~EVIL Conscripter~Deathrattle"
	requireTarget, keyWord, description = False, "", "Deathrattle: Add a Lackey to your hand"
	name_CN = "怪盗征募员"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [AddaRandomLackeytoHand(self)]
		
class AddaRandomLackeytoHand(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		curGame = self.entity.Game
		if curGame.mode == 0:
			if curGame.guides:
				lackey = curGame.guides.pop(0)
			else:
				lackey = npchoice(Lackeys)
				curGame.fixedGuides.append(lackey)
			curGame.Hand_Deck.addCardtoHand(lackey, self.entity.ID, byType=True)
			
	def text(self, CHN):
		return "亡语：将一张跟班牌置入你的手牌" if CHN else "Deathrattle: Add A random Lackey to your hand"
		
			
class HenchClanShadequill(Minion):
	Class, race, name = "Priest", "", "Hench-Clan Shadequill"
	mana, attack, health = 4, 4, 7
	index = "DALARAN~Priest~Minion~4~4~7~~Hench-Clan Shadequill~Deathrattle"
	requireTarget, keyWord, description = False, "", "Deathrattle: Restore 5 Health to the enemy hero"
	name_CN = "荆棘帮箭猪"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [Restore5HealthtoEnemyHero(self)]
		
class Restore5HealthtoEnemyHero(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		heal = 5 * (2 ** self.entity.countHealDouble())
		self.entity.restoresHealth(self.entity.Game.heroes[3-self.entity.ID], heal)
		
	def text(self, CHN):
		heal = 5 * (2 ** self.entity.countHealDouble())
		return "亡语：为敌方英雄恢复%d点生命值"%heal if CHN else "Deathrattle: Restore %d health to enemy hero"%heal
		
#If the target minion is killed due to Teacher/Juggler combo, summon a fresh new minion without enchantment.
class UnsleepingSoul(Spell):
	Class, school, name = "Priest", "", "Unsleeping Soul"
	requireTarget, mana = True, 4
	index = "DALARAN~Priest~Spell~4~Unsleeping Soul"
	description = "Silence a friendly minion, then summon a copy of it"
	name_CN = "不眠之魂"
	def targetExists(self, choice=0):
		return self.selectableFriendlyMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.ID == self.ID and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			target.getsSilenced()
			Copy = target.selfCopy(target.ID) if target.onBoard else type(target)(self.Game, target.ID)
			self.Game.summon(Copy, target.pos+1, self)
		return target
		
		
class ForbiddenWords(Spell):
	Class, school, name = "Priest", "Shadow", "Forbidden Words"
	requireTarget, mana = True, 0
	index = "DALARAN~Priest~Spell~0~Shadow~Forbidden Words"
	description = "Spell all your Mana. Destroy a minion with that much Attack or less"
	name_CN = "禁忌咒文"
	
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.attack <= self.Game.Manas.manas[self.ID] and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		#假设如果没有指定目标则不会消耗法力值
		if target:
			self.Game.Counters.manaSpentonSpells[self.ID] += self.Game.Manas.manas[self.ID]
			self.Game.Manas.manas[self.ID] = 0
			self.Game.killMinion(self, target)
		return target
		
		
class ConvincingInfiltrator(Minion):
	Class, race, name = "Priest", "", "Convincing Infiltrator"
	mana, attack, health = 5, 2, 6
	index = "DALARAN~Priest~Minion~5~2~6~~Convincing Infiltrator~Taunt~Deathrattle"
	requireTarget, keyWord, description = False, "Taunt", "Taunt. Deathrattle: Destroy a random enemy minion"
	name_CN = "无面渗透者"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [DestroyaRandomEnemyMinion(self)]
		
class DestroyaRandomEnemyMinion(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		curGame = self.entity.Game
		if curGame.mode == 0:
			if curGame.guides:
				i = curGame.guides.pop(0)
			else:
				minions = curGame.minionsAlive(3-self.entity.ID)
				i = npchoice(minions).pos if minions else -1
				curGame.fixedGuides.append(i)
			if i > -1:
				curGame.killMinion(self.entity, curGame.minions[3-self.entity.ID][i])
				
	def text(self, CHN):
		return "亡语：随机消灭一个敌方随从" if CHN else "Deathrattle: Destroy a random enemy minion"
		
				
class MassResurrection(Spell):
	Class, school, name = "Priest", "Holy", "Mass Resurrection"
	requireTarget, mana = False, 9
	index = "DALARAN~Priest~Spell~9~Holy~Mass Resurrection"
	description = "Summon 3 friendly minions that died this game"
	name_CN = "群体复活"
	def available(self):
		return self.Game.space(self.ID) > 0
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if curGame.mode == 0:
			if curGame.guides:
				minions = curGame.guides.pop(0)
			else:
				minionsDied = curGame.Counters.minionsDiedThisGame[self.ID]
				indices = npchoice(minionsDied, min(3, len(minionsDied)), replace=False) if minionsDied else []
				minions = tuple([curGame.cardPool[index] for index in indices])
				curGame.fixedGuides.append(minions)
			if minions: curGame.summon([minion(curGame, self.ID) for minion in minions], (-1, "totheRightEnd"), self)
		return None
		
#Upgrades at the end of turn.
class LazulsScheme(Spell):
	Class, school, name = "Priest", "Shadow", "Lazul's Scheme"
	requireTarget, mana = True, 0
	index = "DALARAN~Priest~Spell~0~Shadow~Lazul's Scheme"
	name_CN = "拉祖尔的阴谋"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.progress = 1
		self.trigsHand = [Trig_Upgrade(self)]
		
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			target.buffDebuff(-self.progress, 0, "StartofTurn 1" if self.ID == 1 else "StartofTurn 2")
		return target
		
class Trig_Upgrade(TrigHand):
	def __init__(self, entity):
		self.blank_init(entity, ["TurnEnds"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.inHand and ID == self.entity.ID
			
	def text(self, CHN):
		return "在你的回合结束时，升级" if CHN else "At the end of your turn, upgrade"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.progress += 1
		
		
class ShadowyFigure(Minion):
	Class, race, name = "Priest", "", "Shadowy Figure"
	mana, attack, health = 2, 2, 2
	index = "DALARAN~Priest~Minion~2~2~2~~Shadowy Figure~Battlecry"
	requireTarget, keyWord, description = True, "", "Battlecry: Transform into a 2/2 copy of a friendly Deathrattle minion"
	name_CN = "阴暗的人影"
	
	def targetExists(self, choice=0):
		return self.selectableFriendlyMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target != self and target.ID == self.ID and target.deathrattles != [] and target.onBoard
		
	def effCanTrig(self):
		self.effectViable = self.targetExists()
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		#目前只有打随从从手牌打出或者被沙德沃克调用可以触发随从的战吼。这些手段都要涉及self.Game.minionPlayed
		#如果self.Game.minionPlayed不再等于自己，说明这个随从的已经触发了变形而不会再继续变形。
		if target and self.dead == False and self.Game.minionPlayed == self: #战吼触发时自己不能死亡。
			if self.onBoard or self.inHand:
				if target.onBoard:
					Copy = target.selfCopy(self.ID, 2, 2)
				else: #target not on board. This Shadowy Figure becomes a base copy of it.
					Copy = type(target)(self.Game, self.ID)
					Copy.statReset(2, 2)
				self.Game.transform(self, Copy)
		return target
		
		
class MadameLazul(Minion):
	Class, race, name = "Priest", "", "Madame Lazul"
	mana, attack, health = 3, 3, 2
	index = "DALARAN~Priest~Minion~3~3~2~~Madame Lazul~Battlecry~Legendary"
	requireTarget, keyWord, description = False, "", "Battlecry: Discover a copy of a card in your opponent's hand"
	name_CN = "拉祖尔女士"
	#暂时假定无视手牌中的牌的名字相同的规则，发现中可以出现名字相同的牌
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		enemyHand = curGame.Hand_Deck.hands[3-self.ID]
		if self.ID == curGame.turn and enemyHand:
			if curGame.mode == 0:
				if curGame.guides:
					Copy = enemyHand[curGame.guides.pop(0)].selfCopy(self.ID)
					curGame.Hand_Deck.addCardtoHand(Copy, self.ID, byDiscover=True)
				else:
					cards, cardTypes = [], []
					for i, card in enumerate(enemyHand):
						if type(card) not in cardTypes:
							cards.append(i)
							cardTypes.append(type(card))
					if "byOthers" in comment:
						i = npchoice(cards)
						curGame.fixedGuides.append(i)
						Copy = enemyHand[i].selfCopy(self.ID)
						curGame.Hand_Deck.addCardtoHand(Copy, self.ID, byDiscover=True)
					else:
						indices = npchoice(cards, min(3, len(cards)), replace=False)
						curGame.options = [enemyHand[i] for i in indices]
						curGame.Discover.startDiscover(self)
		return None
		
	def discoverDecided(self, option, pool):
		for i, card in enumerate(self.Game.Hand_Deck.hands[3-self.ID]):
			if card == option:
				self.Game.fixedGuides.append(i)
				break
		self.Game.Hand_Deck.addCardtoHand(option.selfCopy(self.ID), self.ID, byDiscover=True)
		
		
class CatrinaMuerte(Minion):
	Class, race, name = "Priest", "", "Catrina Muerte"
	mana, attack, health = 8, 6, 8
	index = "DALARAN~Priest~Minion~8~6~8~~Catrina Muerte~Legendary"
	requireTarget, keyWord, description = False, "", "At the end of your turn, summon a friendly minion that died this game"
	name_CN = "亡者卡特林娜"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_CatrinaMuerte(self)]
		
class Trig_CatrinaMuerte(TrigBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["TurnEnds"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and ID == self.entity.ID
				
	def text(self, CHN):
		return "在你的回合结束时，召唤一个在本局对战中死亡的友方随从" if CHN else "At the end of your turn, summon a friendly minion that died this game"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		curGame = self.entity.Game
		if curGame.mode == 0:
			if curGame.guides:
				minion = curGame.guides.pop(0)
			else:
				minions = curGame.Counters.minionsDiedThisGame[self.entity.ID]
				minion = curGame.cardPool[npchoice(minions)] if minions else None
				curGame.fixedGuides.append(minion)
			if minion: curGame.summon(minion(curGame, self.entity.ID), self.entity.pos+1, self.entity)
			
"""Rogue cards"""
class DaringEscape(Spell):
	Class, school, name = "Rogue", "", "Daring Escape"
	requireTarget, mana = False, 1
	index = "DALARAN~Rogue~Spell~1~Daring Escape"
	description = "Return all friendly minions to your hand"
	name_CN = "战略转移"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		for minion in self.Game.minionsonBoard(self.ID):
			self.Game.returnMiniontoHand(minion)
		return None
		
		
class EVILMiscreant(Minion):
	Class, race, name = "Rogue", "", "EVIL Miscreant"
	mana, attack, health = 3, 1, 4
	index = "DALARAN~Rogue~Minion~3~1~4~~EVIL Miscreant~Combo"
	requireTarget, keyWord, description = False, "", "Combo: Add two 1/1 Lackeys to your hand"
	name_CN = "怪盗恶霸"
	
	def effCanTrig(self):
		self.effectViable = self.Game.Counters.numCardsPlayedThisTurn[self.ID] > 0
		
	#Will only be invoked if self.effCanTrig() returns True in self.played()
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if curGame.Counters.numCardsPlayedThisTurn[self.ID] > 0:
			if curGame.mode == 0:
				if curGame.guides:
					lackeys = list(curGame.guides.pop(0))
				else:
					lackeys = npchoice(Lackeys, 2, replace=True)
					curGame.fixedGuides.append(tuple(lackeys))
				curGame.Hand_Deck.addCardtoHand(lackeys, self.ID, byType=True)
		return None
		
		
class HenchClanBurglar(Minion):
	Class, race, name = "Rogue", "Pirate", "Hench-Clan Burglar"
	mana, attack, health = 4, 4, 3
	index = "DALARAN~Rogue~Minion~4~4~3~Pirate~Hench-Clan Burglar~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Discover a spell from another class"
	name_CN = "荆棘帮蟊贼"
	poolIdentifier = "Druid Spells"
	@classmethod
	def generatePool(cls, Game):
		return [Class+" Spells" for Class in Game.Classes], \
				[[value for key, value in Game.ClassCards[Class].items() if "~Spell~" in key] for Class in Game.Classes]
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if self.ID == curGame.turn:
			if curGame.mode == 0:
				if curGame.guides:
					curGame.Hand_Deck.addCardtoHand(curGame.guides.pop(0), self.ID, byType=True, byDiscover=True)
				else:
					Class, classes = curGame.heroes[self.ID].Class, curGame.Classes[:]
					if Class == "Neutral": Class = "Rogue"
					try: classes.remove(Class)
					except: pass
					if "byOthers" in comment:
						spell = npchoice(self.rngPool("%s Spells"%npchoice(classes)))
						curGame.fixedGuides.append(spell)
						curGame.Hand_Deck.addCardtoHand(spell, self.ID, byType=True, byDiscover=True)
					else:
						spells = [npchoice(self.rngPool("%s Spells"%Class)) for Class in npchoice(classes, 3, replace=False)]
						curGame.options = [spell(curGame, self.ID) for spell in spells]
						curGame.Discover.startDiscover(self)
		return None
		
	def discoverDecided(self, option, pool):
		self.Game.fixedGuides.append(type(option))
		self.Game.Hand_Deck.addCardtoHand(option, self.ID, byDiscover=True)
		
		
class TogwagglesScheme(Spell):
	Class, school, name = "Rogue", "", "Togwaggle's Scheme"
	requireTarget, mana = True, 1
	index = "DALARAN~Rogue~Spell~1~Togwaggle's Scheme"
	name_CN = "托瓦格尔的 阴谋"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.progress = 1
		self.trigsHand = [Trig_Upgrade(self)]
		
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.ID == self.ID and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			copies = [type(target)(self.Game, self.ID) for i in range(self.progress)]
			self.Game.Hand_Deck.shuffleintoDeck(copies, creator=self)
		return target
		
		
class UnderbellyFence(Minion):
	Class, race, name = "Rogue", "", "Underbelly Fence"
	mana, attack, health = 2, 2, 3
	index = "DALARAN~Rogue~Minion~2~2~3~~Underbelly Fence~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: If you're holding a card from another class, gain +1/+1 and Rush"
	name_CN = "下水道销赃人"
	
	def effCanTrig(self):
		if self.inHand:
			self.effectViable = self.Game.Hand_Deck.holdingCardfromAnotherClass(self.ID, self)
		else:
			self.effectViable = self.Game.Hand_Deck.holdingCardfromAnotherClass(self.ID)
			
	#Will only be invoked if self.effCanTrig() returns True in self.played()
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if self.inHand and self.Game.Hand_Deck.holdingCardfromAnotherClass(self.ID, self):
			self.buffDebuff(1, 1)
			self.getsKeyword("Rush")
		elif self.onBoard and self.Game.Hand_Deck.holdingCardfromAnotherClass(self.ID):
			self.buffDebuff(1, 1)
			self.getsKeyword("Rush")
		return None
		
		
class Vendetta(Spell):
	Class, school, name = "Rogue", "", "Vendetta"
	requireTarget, mana = True, 4
	index = "DALARAN~Rogue~Spell~4~Vendetta"
	description = "Deal 4 damage to a minion. Costs (0) if you're holding a card from another class"
	name_CN = "宿敌"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsHand = [Trig_Vendetta(self)]
		
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
		
	def selfManaChange(self):
		if self.inHand and self.Game.Hand_Deck.holdingCardfromAnotherClass(self.ID):
			self.mana = 0
			
	def text(self, CHN):
		damage = (4 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		return "对一个随从造成%d点伤害。如果你的手牌中有另一职业的卡牌，则法力值消耗为(0)点"%damage if CHN \
				else "Deal %d damage to a minion. Costs (0) if you're holding a card from another class"%damage
				
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			damage = (4 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			self.dealsDamage(target, damage)
		return target
		
class Trig_Vendetta(TrigHand):
	def __init__(self, entity):
		self.blank_init(entity, ["CardLeavesHand", "CardEntersHand"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		#Only cards with a different class than your hero class will trigger this
		card = target[0] if signal == "CardEntersHand" else target
		return self.entity.inHand and card.ID == self.entity.ID and self.entity.Game.heroes[self.entity.ID].Class not in card.Class
		
	def text(self, CHN):
		return "当你的手牌中有其他职业的牌加入或离开时，重新计算费用" if CHN \
				else "Whenever a card from another class enters/leaves your hand, recalculate the cost"
				
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.Game.Manas.calcMana_Single(self.entity)
		
		
class WagglePick(Weapon):
	Class, name, description = "Rogue", "Waggle Pick", "Deathrattle: Return a random friendly minion to your hand. It costs (2) less"
	mana, attack, durability = 4, 4, 2
	index = "DALARAN~Rogue~Weapon~4~4~2~Waggle Pick~Deathrattle"
	name_CN = "摇摆矿锄"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [ReturnaFriendlyMiniontoHand(self)]
		
#There are minions who also have this deathrattle.
class ReturnaFriendlyMiniontoHand(Deathrattle_Weapon):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		curGame = self.entity.Game
		if curGame.mode == 0:
			if curGame.guides:
				i = curGame.guides.pop(0)
			else:
				minions = curGame.minionsonBoard(self.entity.ID)
				i = npchoice(minions).pos if minions else -1
				curGame.fixedGuides.append(i)
			if i > -1:
				minion = curGame.minions[self.entity.ID][i]
				#假设那张随从在进入手牌前接受-2费效果。可以被娜迦海巫覆盖。
				manaMod = ManaMod(minion, changeby=-2, changeto=-1)
				curGame.returnMiniontoHand(minion, deathrattlesStayArmed=False, manaMod=manaMod)
				
	def text(self, CHN):
		return "亡语：随机将一个友方随从返回你的手牌，它的法力值消耗减少(2)点" if CHN \
				else "Whenever this minion deals damage, gain that much Armor"
				
				
class UnidentifiedContract(Spell):
	Class, school, name = "Rogue", "", "Unidentified Contract"
	requireTarget, mana = True, 6
	index = "DALARAN~Rogue~Spell~6~Unidentified Contract"
	description = "Destroy a minion. Gain a bonus effect in your hand"
	name_CN = "未鉴定的合约"
	def entersHand(self):
		#本牌进入手牌的结果是本卡消失，变成其他的牌
		self.onBoard = self.inHand = self.inDeck = False
		mana = self.mana #假设变成其他牌之后会保留当前的费用状态
		curGame = self.Game
		if curGame.mode == 0:
			if curGame.guides:
				contract = curGame.guides.pop(0)
			else:
				contract = npchoice([AssassinsContract, LucrativeContract, RecruitmentContract, TurncoatContract])
			card = contract(curGame, self.ID)
			ManaMod(card, changeby=0, changeto=mana).applies()
			card.inHand = True
			card.onBoard = card.inDeck = False
			card.enterHandTurn = card.Game.numTurn
			for trig in card.trigsHand: trig.connect()
		return card
		
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			self.Game.killMinion(self, target)
		return target
		
class AssassinsContract(Spell):
	Class, school, name = "Rogue", "", "Assassin's Contract"
	requireTarget, mana = True, 6
	index = "DALARAN~Rogue~Spell~6~Assassin's Contract~Uncollectible"
	description = "Destroy a minion. Summon a 1/1 Patient Assassin"
	name_CN = "刺客合约"
	
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			self.Game.killMinion(self, target)
		self.Game.summon(PatientAssassin(self.Game, self.ID), -1, self)
		return target
		
class LucrativeContract(Spell):
	Class, school, name = "Rogue", "", "Lucrative Contract"
	requireTarget, mana = True, 6
	index = "DALARAN~Rogue~Spell~6~Lucrative Contract~Uncollectible"
	description = "Destroy a minion. Add two Coins to your hand"
	name_CN = "赏金合约"
	
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			self.Game.killMinion(self, target)
		self.Game.Hand_Deck.addCardtoHand([TheCoin, TheCoin], self.ID, byType=True)
		return target
		
class RecruitmentContract(Spell):
	Class, school, name = "Rogue", "", "Recruitment Contract"
	requireTarget, mana = True, 6
	index = "DALARAN~Rogue~Spell~6~Recruitment Contract~Uncollectible"
	description = "Destroy a minion. Add a copy of it to your hand"
	name_CN = "招募合约"
	
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			self.Game.killMinion(self, target)
		self.Game.Hand_Deck.addCardtoHand(type(target), self.ID, byType=True)
		return target
		
class TurncoatContract(Spell):
	Class, school, name = "Rogue", "", "Turncoat Contract"
	requireTarget, mana = True, 6
	index = "DALARAN~Rogue~Spell~6~Turncoat Contract~Uncollectible"
	description = "Destroy a minion. It deals damage to adjacent minions"
	name_CN = "叛变合约"
	
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			self.Game.killMinion(self, target)
			if target.onBoard:
				adjacentMinions, distribution = self.Game.neighbors2(target)
				if adjacentMinions != []:
					target.dealsAOE(adjacentMinions, [target.attack]*len(adjacentMinions))
		return target
		
		
FantasticTreasures = [GoldenKobold, TolinsGoblet, WondrousWand, ZarogsCrown]

class HeistbaronTogwaggle(Minion):
	Class, race, name = "Rogue", "", "Heistbaron Togwaggle"
	mana, attack, health = 6, 5, 5
	index = "DALARAN~Rogue~Minion~6~5~5~~Heistbaron Togwaggle~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: If you control a Lackey, choose a fantastic treasure"
	name_CN = "劫匪之王 托瓦格尔"
	
	def effCanTrig(self):
		self.effectViable = False
		for minion in self.Game.minionsonBoard(self.ID):
			if minion.name.endswith("Lackey"):
				self.effectViable = True
				break
				
	#Will only be invoked if self.effCanTrig() returns True in self.played()
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame, controlsLackey = self.Game, False
		for minion in curGame.minionsonBoard(self.ID):
			if minion.name.endswith("Lackey"):
				controlsLackey = True
				break
		if controlsLackey and self.ID == curGame.turn:
			if curGame.mode == 0:
				if curGame.guides:
					curGame.Hand_Deck.addCardtoHand(curGame.guides.pop(0), self.ID, byType=True)
				else:
					if "byOthers" in comment:
						treasure = npchoice(FantasticTreasures)
						curGame.fixedGuides.append(treasure)
						curGame.Hand_Deck.addCardtoHand(treasure, self.ID, byType=True)
					else:
						curGame.options = [treasure(curGame, self.ID) for treasure in FantasticTreasures]
						curGame.Discover.startDiscover(self)
		return None
		
	def discoverDecided(self, option, pool):
		self.Game.fixedGuides.append(type(option))
		self.Game.Hand_Deck.addCardtoHand(option, self.ID)
		
		
class TakNozwhisker(Minion):
	Class, race, name = "Rogue", "", "Tak Nozwhisker"
	mana, attack, health = 7, 6, 6
	index = "DALARAN~Rogue~Minion~7~6~6~~Tak Nozwhisker"
	requireTarget, keyWord, description = False, "", "Whenever you shuffle a card into your deck, add a copy to your hand"
	name_CN = "塔克·诺兹维克"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_TakNozwhisker(self)]
		
class Trig_TakNozwhisker(TrigBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["CardShuffled"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		#Only triggers if the player is the initiator
		return self.entity.onBoard and ID == self.entity.ID
		
	def text(self, CHN):
		return "每当你将一张牌洗入你的牌库时，将该牌的一张复制置入你的手牌" if CHN \
				else "Whenever you shuffle a card into your deck, add a copy to your hand"
				
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		if isinstance(target, (list, np.ndarray)):
			for card in target:
				if self.entity.Game.Hand_Deck.handNotFull(self.entity.ID):
					Copy = card.selfCopy(self.entity.ID)
					self.entity.Game.Hand_Deck.addCardtoHand(Copy, self.entity.ID)
				else:
					break
		else: #A single card is shuffled.
			Copy = target.selfCopy(self.entity.ID)
			self.entity.Game.Hand_Deck.addCardtoHand(Copy, self.entity.ID)
			
"""Shaman cards"""
class Mutate(Spell):
	Class, school, name = "Shaman", "", "Mutate"
	requireTarget, mana = True, 0
	index = "DALARAN~Shaman~Spell~0~Mutate"
	description = "Transf a friendly minion to a random one that costs (1) more"
	name_CN = "突变"
	poolIdentifier = "1-Cost Minions to Summon"
	@classmethod
	def generatePool(cls, Game):
		return ["%d-Cost Minions to Summon"%cost for cost in Game.MinionsofCost.keys()], \
				[list(Game.MinionsofCost[cost].values()) for cost in Game.MinionsofCost.keys()]
		
	def available(self):
		return self.selectableFriendlyMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.ID == self.ID and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			curGame = self.Game
			if curGame.mode == 0:
				if curGame.guides:
					newMinion = curGame.guides.pop(0)
				else:
					cost = type(target).mana + 1
					while cost not in curGame.MinionsofCost:
						cost -= 1
					newMinion = npchoice(self.rngPool("%d-Cost Minions to Summon"%cost))
					curGame.fixedGuides.append(newMinion)
				newMinion = newMinion(curGame, target.ID)
				curGame.transform(target, newMinion)
			target = newMinion
		return target
		
		
class SludgeSlurper(Minion):
	Class, race, name = "Shaman", "Murloc", "Sludge Slurper"
	mana, attack, health = 1, 2, 1
	index = "DALARAN~Shaman~Minion~1~2~1~Murloc~Sludge Slurper~Battlecry~Overload"
	requireTarget, keyWord, description = False, "", "Battlecry: Add a Lackey to your hand. Overload: (1)"
	name_CN = "淤泥吞食者"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.overload = 1
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if curGame.mode == 0:
			if curGame.guides:
				lackey = curGame.guides.pop(0)
			else:
				lackey = npchoice(Lackeys)
				curGame.fixedGuides.append(lackey)
			curGame.Hand_Deck.addCardtoHand(lackey, self.ID, byType=True)
		return None
		
		
class SouloftheMurloc(Spell):
	Class, school, name = "Shaman", "", "Soul of the Murloc"
	requireTarget, mana = False, 2
	index = "DALARAN~Shaman~Spell~2~Soul of the Murloc"
	description = "Give your minions 'Deathrattle: Summon a 1/1 Murloc'"
	name_CN = "鱼人之魂"
	def available(self):
		return self.Game.minionsonBoard(self.ID) != []
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		for minion in self.Game.minionsonBoard(self.ID):
			trig = SummonaMurlocScout(minion)
			minion.deathrattles.append(trig)
			trig.connect()
		return None
		
class SummonaMurlocScout(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.Game.summon(MurlocScout(self.entity.Game, self.entity.ID), self.entity.pos+1, self.entity)
		
	def text(self, CHN):
		return "亡语：召唤一个1/1的鱼人" if CHN else "Deathrattle: Summon a 1/1 Murloc"
		
		
class UnderbellyAngler(Minion):
	Class, race, name = "Shaman", "Murloc", "Underbelly Angler"
	mana, attack, health = 2, 2, 3
	index = "DALARAN~Shaman~Minion~2~2~3~Murloc~Underbelly Angler"
	requireTarget, keyWord, description = False, "", "After you play a Murloc, add a random Murloc to your hand"
	name_CN = "下水道渔人"
	poolIdentifier = "Murlocs"
	@classmethod
	def generatePool(cls, Game):
		return "Murlocs", list(Game.MinionswithRace["Murloc"].values())
		
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_UnderbellyAngler(self)]
		
class Trig_UnderbellyAngler(TrigBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionBeenSummoned"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject.ID == self.entity.ID and subject != self.entity and "Murloc" in subject.race
		
	def text(self, CHN):
		return "在你使用一张鱼人牌后，随机将一张鱼人牌置入你的手牌" if CHN else "After you play a Murloc, add a random Murloc to your hand"
		
	#Assume if Murloc gets controlled by the enemy, this won't trigger
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		curGame = self.entity.Game
		if curGame.mode == 0:
			if curGame.guides:
				murloc = curGame.guides.pop(0)
			else:
				murloc = npchoice(self.rngPool("Murlocs"))
				curGame.fixedGuides.append(murloc)
			curGame.Hand_Deck.addCardtoHand(murloc, self.entity.ID, byType=True)
			
			
class HagathasScheme(Spell):
	Class, school, name = "Shaman", "Nature", "Hagatha's Scheme"
	requireTarget, mana = False, 5
	index = "DALARAN~Shaman~Spell~5~Nature~Hagatha's Scheme"
	description = "Deal 1 damage to all minions. (Upgrades each turn)!"
	name_CN = "哈加莎的阴谋"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.progress = 1
		self.trigsHand = [Trig_Upgrade(self)]
		
	def text(self, CHN):
		base = self.progress
		damage = (base + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		return "对所有随从造成%d点伤害。（已升级至%d）"%(damage, base) if CHN \
				else "Deal %d damage to all minions. (Has upgraded to %d)"%(damage, base)
				
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		damage = (self.progress + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		targets = self.Game.minionsonBoard(1) + self.Game.minionsonBoard(2)
		self.dealsAOE(targets, [damage]*len(targets))
		return None
		
		
class WalkingFountain(Minion):
	Class, race, name = "Shaman", "Elemental", "Walking Fountain"
	mana, attack, health = 8, 4, 8
	index = "DALARAN~Shaman~Minion~8~4~8~Elemental~Walking Fountain~Rush~Lifesteal~Windfury"
	requireTarget, keyWord, description = False, "Rush,Windfury,Lifesteal", "Rush, Windfury, Lifesteal"
	name_CN = "活动喷泉"
	
	
class WitchsBrew(Spell):
	Class, school, name = "Shaman", "Nature", "Witch's Brew"
	requireTarget, mana = True, 2
	index = "DALARAN~Shaman~Spell~2~Nature~Witch's Brew"
	description = "Restore 4 Health. Repeatable this turn"
	name_CN = "女巫杂酿"
	def text(self, CHN):
		heal = 4 * (2 ** self.countHealDouble())
		return "恢复%d点生命值，在本回合可以重复使用"%heal if CHN else "Restore %d Health. Repeatable this turn"%heal
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			heal = 4 * (2 ** self.countHealDouble())
			self.restoresHealth(target, heal)
			
		echo = WitchsBrew(self.Game, self.ID)
		echo.trigsHand.append(Trig_Echo(echo))
		self.Game.Hand_Deck.addCardtoHand(echo, self.ID)
		return target
		
		
class Muckmorpher(Minion):
	Class, race, name = "Shaman", "", "Muckmorpher"
	mana, attack, health = 5, 4, 4
	index = "DALARAN~Shaman~Minion~5~4~4~~Muckmorpher~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Transform in to a 4/4 copy of a different minion in your deck"
	name_CN = "泥泽变形怪"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		#目前只有打随从从手牌打出或者被沙德沃克调用可以触发随从的战吼。这些手段都要涉及self.Game.minionPlayed
		#如果self.Game.minionPlayed不再等于自己，说明这个随从的已经触发了变形而不会再继续变形。
		curGame = self.Game
		if not self.dead and curGame.minionPlayed == self: #战吼触发时自己不能死亡。
			if self.onBoard or self.inHand:
				if curGame.guides:
					i = curGame.guides.pop(0)
				else:
					minions = [i for i, card in enumerate(curGame.Hand_Deck.decks[self.ID]) if card.type == "Minion" and type(card) != type(self)]
					i = npchoice(minions) if minions else -1
					curGame.fixedGuides.append(i)
				if i > -1:
					minion = type(curGame.Hand_Deck.decks[self.ID][i])(curGame, self.ID)
					minion.statReset(4, 4)
					curGame.transform(self, minion)
		return None
		
		
class Scargil(Minion):
	Class, race, name = "Shaman", "Murloc", "Scargil"
	mana, attack, health = 4, 4, 4
	index = "DALARAN~Shaman~Minion~4~4~4~Murloc~Scargil~Legendary"
	requireTarget, keyWord, description = False, "", "Your Murlocs cost (1)"
	name_CN = "斯卡基尔"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.auras["Your Murlocs cost (1)"] = ManaAura(self, changeby=0, changeto=1)
		
	def manaAuraApplicable(self, subject):
		return subject.ID == self.ID and subject.type == "Minion" and "Murloc" in subject.race
		
		
class SwampqueenHagatha(Minion):
	Class, race, name = "Shaman", "", "Swampqueen Hagatha"
	mana, attack, health = 7, 5, 5
	index = "DALARAN~Shaman~Minion~7~5~5~~Swampqueen Hagatha~Battlecry~Legendary"
	requireTarget, keyWord, description = False, "", "Battlecry: Add a 5/5 Horror to your hand. Teach it two Shaman spells"
	name_CN = "沼泽女王 哈加莎"
	poolIdentifier = "Shaman Spells"
	@classmethod
	def generatePool(cls, Game):
		spells, targetingSpells, nontargetingSpells = [], [], []
		for key, value in Game.ClassCards["Shaman"].items():
			if "~Spell~" in key:
				spells.append(value)
				if value.requireTarget: targetingSpells.append(value)
				else: nontargetingSpells.append(value)
		return ["Shaman Spells", "Targeting Shaman Spells", "Non-targeting Shaman Spells"], [spells, targetingSpells, nontargetingSpells]
		
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.firstSpellneedsTarget = False
		self.spell1, self.spell2 = None, None
	#有可能发现两个相同的非指向性法术。
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.spell1, self.spell2 = None, None
		curGame = self.Game
		if self.ID == curGame.turn:
			if curGame.mode == 0:
				if curGame.guides:
					spell1, spell2 = curGame.guides.pop(0)
				else:
					if "byOthers" in comment:
						spell1 = npchoice(self.rngPool("Shaman Spells"))
						#If the first spell is not a targeting spell, then the 2nd has no restrictions
						spell2 = npchoice(self.rngPool("Non-targeting Shaman Spells")) if spell1.requireTarget else npchoice(self.rngPool("Shaman Spells"))
						curGame.fixedGuides.append((spell1, spell2))
					else:
						spells = npchoice(self.rngPool("Shaman Spells"), 3, replace=False)
						curGame.options = [spell(curGame, self.ID) for spell in spells]
						curGame.Discover.startDiscover(self)
						if self.spell1.requireTarget: spells = npchoice(self.rngPool("Non-targeting Shaman Spells"), 3, replace=False)
						else: spells = npchoice(self.rngPool("Shaman Spells"), 3, replace=False)
						curGame.options = [spell(curGame, self.ID) for spell in spells]
						curGame.Discover.startDiscover(self)
						spell1, spell2 = self.spell1, self.spell2
						self.spell1, self.spell2 = None, None
						curGame.fixedGuides.append((spell1, spell2))
				#The 2 spells are both class types, whether they come from Discover or random
				spell1ClassName, spell2ClassName = spell1.__name__, spell2.__name__
				requireTarget = spell1.requireTarget or spell2.requireTarget
				newIndex = "DALARAN~Shaman~5~5~5~Minion~~Drustvar Horror_%s_%s~Battlecry~Uncollectible"%(spell1.name, spell2.name)
				subclass = type("DrustvarHorror__"+spell1ClassName+spell2ClassName, (DrustvarHorror, ),
								{"requireTarget": requireTarget, "learnedSpell1": spell1, "learnedSpell2":spell2,
								"index": newIndex
								}
								)
				curGame.cardPool[newIndex] = subclass
				curGame.Hand_Deck.addCardtoHand(subclass(curGame, self.ID), self.ID)
		return None
		
	def discoverDecided(self, option, pool):
		if self.spell1 is None: self.spell1 = type(option)
		else: self.spell2 = type(option)
		
class DrustvarHorror(Minion):
	Class, race, name = "Shaman", "", "Drustvar Horror"
	mana, attack, health = 5, 5, 5
	index = "DALARAN~Shaman~Minion~5~5~5~~Drustvar Horror~Battlecry~Uncollectible"
	requireTarget, keyWord, description = True, "", "Battlecry: Cast (0) and (1)"
	name_CN = "德鲁斯瓦恐魔"
	learnedSpell1, learnedSpell2 = None, None
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.learnedSpell1 = type(self).learnedSpell1(self.Game, self.ID)
		self.learnedSpell2 = type(self).learnedSpell2(self.Game, self.ID)
		self.description = "Battlecry: Cast %s and %s"%(self.learnedSpell1.name, self.learnedSpell2.name)
		
	#无指向的法术的available一般都会返回True，不返回True的时候一般是场上没有格子了，但是这种情况本来就不能打出随从，不会影响判定。
	#有指向的法术的available会真正决定可指向目标是否存在。
	def targetExists(self, choice=0): #假设可以指向魔免随从
		#这里调用携带的法术类的available函数的同时需要向其传导self，从而让其知道self.selectableCharacterExists用的是什么实例的方法
		self.learnedSpell1.ID, self.learnedSpell2.ID = self.ID, self.ID
		return self.learnedSpell1.available() and self.learnedSpell2.available()
		
	def targetCorrect(self, target, choice=0):
		if self == target:
			return False
		self.learnedSpell1.ID, self.learnedSpell2.ID = self.ID, self.ID
		if self.learnedSpell1.needTarget():
			return self.learnedSpell1.targetCorrect(target)
		if self.learnedSpell2.needTarget():
			return self.learnedSpell2.targetCorrect(target)
		return True
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		#不知道施放的法术是否会触发发现，还是直接随机选取一个发生选项
		#假设是随机选取一个选项。
		self.learnedSpell1.cast(target)
		self.learnedSpell2.cast(target)
		return target
		
"""Warlock cards"""
class EVILGenius(Minion):
	Class, race, name = "Warlock", "", "EVIL Genius"
	mana, attack, health = 2, 2, 2
	index = "DALARAN~Warlock~Minion~2~2~2~~EVIL Genius~Battlecry"
	requireTarget, keyWord, description = True, "", "Battlecry: Destroy a friendly minion to add 2 random Lackeys to your hand"
	name_CN = "怪盗天才"
	def targetExists(self, choice=0):
		return self.selectableFriendlyMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.ID == self.ID and target != self and target.onBoard 
		
	def effCanTrig(self):
		self.effectViable = self.targetExists()
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			curGame = self.Game
			self.Game.killMinion(self, target)
			if curGame.mode == 0:
				if curGame.guides:
					lackeys = curGame.guides.pop(0)
				else:
					lackeys = npchoice(Lackeys, 2, replace=True)
					curGame.fixedGuides.append(lackeys)
				curGame.Hand_Deck.addCardtoHand(lackeys, self.ID, byType=True)
		return target
		
		
class RafaamsScheme(Spell):
	Class, school, name = "Warlock", "Fire", "Rafaam's Scheme"
	requireTarget, mana = False, 3
	index = "DALARAN~Warlock~Spell~3~Fire~Rafaam's Scheme"
	description = "Summon 1 1/1 Imp(Upgrades each turn!)"
	name_CN = "拉法姆的阴谋"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.progress = 1
		self.trigsHand = [Trig_Upgrade(self)]
		
	def text(self, CHN):
		return "召唤%d个1/1的小鬼"%self.progress if CHN else "Summon %d 1/1 Imp(s)"%self.progress
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.Game.summon([Imp_Shadows(self.Game, self.ID) for i in range(self.progress)], (-1, "totheRightEnd"), self)
		return None
		
		
class AranasiBroodmother(Minion):
	Class, race, name = "Warlock", "Demon", "Aranasi Broodmother"
	mana, attack, health = 6, 4, 6
	index = "DALARAN~Warlock~Minion~6~4~6~Demon~Aranasi Broodmother~Taunt~Triggers when Drawn"
	requireTarget, keyWord, description = False, "Taunt", "Taunt. When you draw this, restore 4 Health to your hero"
	name_CN = "阿兰纳斯蛛后"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		
	def whenDrawn(self):
		heal = 4 * (2 ** self.countHealDouble())
		self.restoresHealth(self.Game.heroes[self.ID], heal)
		
#把随从洗回牌库会消除其上的身材buff（+2、+2的飞刀杂耍者的buff消失）
#卡牌上的费用效果也会全部消失(大帝的-1效果)
#被祈求升级过一次的迦拉克隆也会失去进度。
#说明这个动作是把手牌中所有牌初始化洗回去
class PlotTwist(Spell):
	Class, school, name = "Warlock", "", "Plot Twist"
	requireTarget, mana = False, 2
	index = "DALARAN~Warlock~Spell~2~Plot Twist"
	description = "Shuffle your hand into your deck. Draw that many cards"
	name_CN = "情势反转"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		handSize = len(self.Game.Hand_Deck.hands[self.ID])
		self.Game.Hand_Deck.shuffle_Hand2Deck(0, self.ID, initiatorID=self.ID, all=True)
		for i in range(handSize): self.Game.Hand_Deck.drawCard(self.ID)
		return None
		
		
class Impferno(Spell):
	Class, school, name = "Warlock", "Fire", "Impferno"
	requireTarget, mana = False, 3
	index = "DALARAN~Warlock~Spell~3~Fire~Impferno"
	description = "Give your Demons +1 Attack. Deal 1 damage to all enemy minions"
	name_CN = "小鬼狱火"
	def text(self, CHN):
		damage = (1 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		return "使你的恶魔获得+1攻击力，对所有敌方随从造成%d点伤害"%damage if CHN \
				else "Give your Demons +1 Attack. Deal %d damage to all enemy minions"%damage
				
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		damage = (1 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		for minion in self.Game.minionsonBoard(self.ID):
			if "Demon" in minion.race:
				minion.buffDebuff(1, 1)
				
		targets = self.Game.minionsonBoard(3-self.ID)
		self.dealsAOE(targets, [damage]*len(targets))
		return None
		
		
class EagerUnderling(Minion):
	Class, race, name = "Warlock", "", "Eager Underling"
	mana, attack, health = 4, 2, 2
	index = "DALARAN~Warlock~Minion~4~2~2~~Eager Underling~Deathrattle"
	requireTarget, keyWord, description = False, "", "Deathrattle: Give two random friendly minions +2/+2"
	name_CN = "性急的杂兵"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [GiveTwoRandomFriendlyMinionsPlus2Plus2(self)]
		
class GiveTwoRandomFriendlyMinionsPlus2Plus2(Deathrattle_Weapon):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		curGame = self.entity.Game
		if curGame.mode == 0:
			if curGame.guides:
				minions = [curGame.minions[self.entity.ID][i] for i in curGame.guides.pop(0)]
			else:
				minions = curGame.minionsonBoard(self.entity.ID)
				minions = npchoice(minions, min(len(minions), 2), replace=True)
				curGame.fixedGuides.append(tuple([minion.pos for minion in minions]))
			for minion in minions: minion.buffDebuff(2, 2)
			
	def text(self, CHN):
		return "亡语：随机使两个友方随从获得+2/+2" if CHN else "Deathrattle: Give Two Random Friendly Minions +2/+2"
		
		
class DarkestHour(Spell):
	Class, school, name = "Warlock", "Shadow", "Darkest Hour"
	requireTarget, mana = False, 6
	index = "DALARAN~Warlock~Spell~6~Shadow~Darkest Hour"
	description = "Destroy all friendly minions. For each one, summon a random minion from your deck"
	name_CN = "至暗时刻"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		friendlyMinions = curGame.minionsonBoard(self.ID)
		boardSize = len(friendlyMinions)
		curGame.killMinion(self, friendlyMinions)
		#对于所有友方随从强制死亡，并令其离场，因为召唤的随从是在场上右边，不用记录死亡随从的位置
		curGame.gathertheDead()
		ownDeck = curGame.Hand_Deck.decks[self.ID]
		if curGame.mode == 0:
			for num in range(boardSize):
				if curGame.guides:
					i = curGame.guides.pop(0)
				else:
					minions = [i for i, card in enumerate(ownDeck) if card.type == "Minion"]
					i = npchoice(minions) if minions and curGame.space(self.ID) > 0 else -1
					curGame.fixedGuides.append(i)
				if i > -1: curGame.summonfrom(i, self.ID, -1, self, fromHand=False)
				else: break
		return None
		
#For now, assume the mana change is on the mana and shuffling this card back into deck won't change its counter.
class JumboImp(Minion):
	Class, race, name = "Warlock", "Demon", "Jumbo Imp"
	mana, attack, health = 10, 8, 8
	index = "DALARAN~Warlock~Minion~10~8~8~Demon~Jumbo Imp"
	requireTarget, keyWord, description = False, "", "Costs (1) less whenever a friendly minion dies while this is in your hand"
	name_CN = "巨型小鬼"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsHand = [Trig_JumboImp(self)]
		self.friendlyDemonsDied = 0
		
	def selfManaChange(self):
		self.mana -= self.friendlyDemonsDied
		self.mana = max(self.mana, 0)
		
class Trig_JumboImp(TrigHand):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionDies"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.inHand and target.ID == self.entity.ID and "Demon" in target.race
		
	def text(self, CHN):
		return "当该随从在你的手牌中时，每当一个友方恶魔死亡，法力值消耗就减少(1)点" if CHN \
				else "Costs (1) less whenever a friendly minion dies while this is in your hand"
				
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.friendlyDemonsDied += 1
		self.entity.Game.Manas.calcMana_Single(self.entity)
		
		
class ArchVillainRafaam(Minion):
	Class, race, name = "Warlock", "", "Arch-Villain Rafaam"
	mana, attack, health = 7, 7, 8
	index = "DALARAN~Warlock~Minion~7~7~8~~Arch-Villain Rafaam~Taunt~Battlecry~Legendary"
	requireTarget, keyWord, description = False, "Taunt", "Battlecry: Replace your hand and deck with Legendary minions"
	name_CN = "至尊盗王 拉法姆"
	poolIdentifier = "Legendary Minions"
	@classmethod
	def generatePool(cls, Game):
		return "Legendary Minions", list(Game.LegendaryMinions.values())
	#不知道拉法姆的替换手牌、牌库和迦拉克隆会有什么互动。假设不影响主迦拉克隆。
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if curGame.mode == 0:
			if curGame.guides:
				hand, deck = curGame.guides.pop(0)
			else:
				minions = self.rngPool("Legendary Minions")
				hand = tuple(npchoice(minions, len(curGame.Hand_Deck.hands[self.ID]), replace=True))
				deck = tuple(npchoice(minions, len(curGame.Hand_Deck.dekcs[self.ID]), replace=True))
				curGame.fixedGuides.append(hand, deck)
			if hand or deck:
				curGame.Hand_Deck.extractfromHand(None, self.ID, all=True)
				curGame.Hand_Deck.addCardtoHand(hand, self.ID, byType=True)
				curGame.Hand_Deck.replaceWholeDeck(self.ID, [card(curGame, self.ID) for card in deck])
		return None
		
		
class FelLordBetrug(Minion):
	Class, race, name = "Warlock", "Demon", "Fel Lord Betrug"
	mana, attack, health = 8, 5, 7
	index = "DALARAN~Warlock~Minion~8~5~7~Demon~Fel Lord Betrug~Legendary"
	requireTarget, keyWord, description = False, "", "Whenever you draw a minion, summon a copy with Rush that dies at end of turn"
	name_CN = "邪能领主 贝图格"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_FelLordBetrug(self)]
		
class Trig_FelLordBetrug(TrigBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["CardDrawn"])
		self.inherent = False
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and target[0].type == "Minion" and target[0].ID == self.entity.ID
		
	def text(self, CHN):
		return "每当你抽到一张随从牌，召唤一个它的复制，该复制具有突袭，并会在回合结束时死亡" if CHN \
				else "Whenever you draw a minion, summon a copy with Rush that dies at end of turn"
				
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		minion = target[0].selfCopy(self.entity.ID)
		minion.trigsBoard.append(Trig_DieatEndofTurn(minion))
		self.entity.Game.summon(minion, self.entity.pos+1, self.entity)
		if minion.onBoard:
			minion.getsKeyword("Rush")
			
"""Warrior cards"""
class ImproveMorale(Spell):
	Class, school, name = "Warrior", "", "Improve Morale"
	requireTarget, mana = True, 1
	index = "DALARAN~Warrior~Spell~1~Improve Morale"
	description = "Deal 1 damage to a minion. If it survives, add a Lackey to your hand"
	name_CN = "提振士气"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
		
	def text(self, CHN):
		damage = (1 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		return "对一个随从造成%d点伤害,如果它仍然存活，则将一张随从牌置入你的手牌"%damage if CHN \
				else "Deal %d damage to a minion. If it survives, add a Lackey to your hand"%damage
				
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			curGame = self.Game
			damage = (1 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			self.dealsDamage(target, damage)
			if target.health > 0 and not target.dead:
				if curGame.mode == 0:
					if curGame.guides:
						lackey = curGame.guides.pop(0)
					else:
						lackey = npchoice(Lackeys)
						curGame.fixedGuides.append(lackey)
					curGame.Hand_Deck.addCardtoHand(lackey, self.ID, byType=True)
		return target
		
		
class ViciousScraphound(Minion):
	Class, race, name = "Warrior", "Mech", "Vicious Scraphound"
	mana, attack, health = 2, 2, 2
	index = "DALARAN~Warrior~Minion~2~2~2~Mech~Vicious Scraphound"
	requireTarget, keyWord, description = False, "", "Whenever this minion deals damage, gain that much Armor"
	name_CN = "凶恶的废钢猎犬"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_ViciousScraphound(self)]
		
class Trig_ViciousScraphound(TrigBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionTakesDmg", "HeroTakesDmg"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject == self.entity
		
	def text(self, CHN):
		return "每当该随从造成伤害时，获得等量的护甲值" if CHN \
				else "Whenever this minion deals damage, gain that much Armor"
				
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.Game.heroes[self.entity.ID].gainsArmor(number)
		
		
class DrBoomsScheme(Spell):
	Class, school, name = "Warrior", "", "Dr. Boom's Scheme"
	requireTarget, mana = False, 4
	index = "DALARAN~Warrior~Spell~4~Dr. Boom's Scheme"
	description = "Gain 1 Armor. (Upgrades each turn!)"
	name_CN = "砰砰博士的 阴谋"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.progress = 1
		self.trigsHand = [Trig_Upgrade(self)]
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.Game.heroes[self.ID].gainsArmor(self.progress)
		return None
		
		
class SweepingStrikes(Spell):
	Class, school, name = "Warrior", "", "Sweeping Strikes"
	requireTarget, mana = True, 2
	index = "DALARAN~Warrior~Spell~2~Sweeping Strikes"
	description = "Give a minion 'Also damages minions next to whoever this attacks'"
	name_CN = "横扫攻击"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			target.marks["Sweep"] += 1
		return target
		
		
class ClockworkGoblin(Minion):
	Class, race, name = "Warrior", "Mech", "Clockwork Goblin"
	mana, attack, health = 3, 3, 3
	index = "DALARAN~Warrior~Minion~3~3~3~Mech~Clockwork Goblin~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Shuffle a Bomb in to your opponent's deck. When drawn, it explodes for 5 damage"
	name_CN = "发条地精"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.Game.Hand_Deck.shuffleintoDeck(Bomb(self.Game, 3-self.ID), creator=self)
		return None
		
		
class OmegaDevastator(Minion):
	Class, race, name = "Warrior", "Mech", "Omega Devastator"
	mana, attack, health = 4, 4, 5
	index = "DALARAN~Warrior~Minion~4~4~5~Mech~Omega Devastator~Battlecry"
	requireTarget, keyWord, description = True, "", "Battlecry: If you have 10 Mana Crystals, deal 10 damage to a minion"
	name_CN = "欧米茄毁灭者"
	
	def returnTrue(self, choice=0):
		return self.Game.Manas.manasUpper[self.ID] >= 10
		
	def effCanTrig(self):
		self.effectViable = self.Game.Manas.manasUpper[self.ID] >= 10 and self.targetExists()
		
	def targetExists(self, choice=0):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target != self and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target and self.Game.Manas.manasUpper[self.ID] >= 10:
			self.dealsDamage(target, 10)
		return target
		
		
class Wrenchcalibur(Weapon):
	Class, name, description = "Warrior", "Wrenchcalibur", "After your hero attacks, shuffle a Bomb into your Opponent's deck"
	mana, attack, durability = 4, 3, 2
	index = "DALARAN~Warrior~Weapon~4~3~2~Wrenchcalibur"
	name_CN = "圣剑扳手"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_Wrenchcalibur(self)]
		
class Trig_Wrenchcalibur(TrigBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["HeroAttackedMinion", "HeroAttackedHero"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		#The target can't be dying to trigger this
		return subject == self.entity.Game.heroes[self.entity.ID] and self.entity.onBoard
		
	def text(self, CHN):
		return "在你的英雄攻击后，将一张”“炸弹”牌洗入你对手的牌库" if CHN \
				else "After your hero attacks, shuffle a Bomb into your Opponent's deck"
				
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		weapon = self.entity
		weapon.Game.Hand_Deck.shuffleintoDeck(Bomb(weapon.Game, 3-weapon.ID), creator=weapon)
		
		
class BlastmasterBoom(Minion):
	Class, race, name = "Warrior", "", "Blastmaster Boom"
	mana, attack, health = 7, 7, 7
	index = "DALARAN~Warrior~Minion~7~7~7~~Blastmaster Boom~Battlecry~Legendary"
	requireTarget, keyWord, description = False, "", "Battlecry: Summon two 1/1 Boom Bots for each Bomb in your opponent's deck"
	name_CN = "爆破之王砰砰"
	
	def effCanTrig(self):
		self.effectViable = any(card.name == "Bomb" for card in self.Game.Hand_Deck.decks[3-self.ID])
				
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		numSummon = min(8, 2 * sum(card.name == "Bomb" for card in self.Game.Hand_Deck.decks[3-self.ID]))
		pos = (self.pos, "leftandRight") if self.onBoard else (-1, "totheRightEnd")
		if numSummon > 0:
			self.Game.summon([BoomBot(self.Game, self.ID) for i in range(numSummon)], pos, self)
		return None
		
				
class DimensionalRipper(Spell):
	Class, school, name = "Warrior", "", "Dimensional Ripper"
	requireTarget, mana = False, 10
	index = "DALARAN~Warrior~Spell~10~Dimensional Ripper"
	description = "Summon 2 copies of a minion in your deck"
	name_CN = "空间撕裂器"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if curGame.mode == 0:
			if curGame.guides:
				i = curGame.guides.pop(0)
			else:
				minions = [i for i, card in enumerate(curGame.Hand_Deck.decks[self.ID]) if card.type == "Minion"]
				i = npchoice(minions) if minions else -1
				curGame.fixedGuides.append(i)
			if i > -1:
				minion = curGame.Hand_Deck.decks[self.ID][i]
				curGame.summon([minion.selfCopy(self.ID) for i in range(2)], (-1, "totheRightEnd"), self)
		return None
		
		
class TheBoomReaver(Minion):
	Class, race, name = "Warrior", "Mech", "The Boom Reaver"
	mana, attack, health = 10, 7, 9
	index = "DALARAN~Warrior~Minion~10~7~9~Mech~The Boom Reaver~Battlecry~Legendary"
	requireTarget, keyWord, description = False, "", "Battlecry: Summon a copy of a minion in your deck. Give it Rush"
	name_CN = "砰砰机甲"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if curGame.mode == 0:
			if curGame.guides:
				i = curGame.guides.pop(0)
			else:
				minions = [i for i, card in enumerate(curGame.Hand_Deck.decks[self.ID]) if card.type == "Minion"]
				i = npchoice(minions) if minions else -1
				curGame.fixedGuides.append(i)
			if i > -1:
				minion = curGame.Hand_Deck.decks[self.ID][i]
				if curGame.summon(minion.selfCopy(self.ID), self.pos+1, self):
					minion.getsKeyword("Rush")
		return None
		
		
Shadows_Indices = {"DALARAN~Neutral~Minion~1~1~1~~Potion Vendor~Battlecry": PotionVendor,
					"DALARAN~Neutral~Minion~1~1~2~Murloc~Toxfin~Battlecry": Toxfin,
					"DALARAN~Neutral~Minion~2~2~3~Elemental~Arcane Servant": ArcaneServant,
					"DALARAN~Neutral~Minion~2~2~3~~Dalaran Librarian~Battlecry": DalaranLibrarian,
					"DALARAN~Neutral~Minion~2~1~1~Beast~EVIL Cable Rat~Battlecry": EVILCableRat,
					"DALARAN~Neutral~Minion~2~2~1~Beast~Hench-Clan Hogsteed~Rush~Deathrattle": HenchClanHogsteed,
					"DALARAN~Neutral~Minion~1~1~1~Murloc~Hench-Clan Squire~Uncollectible": HenchClanSquire,
					"DALARAN~Neutral~Minion~2~0~6~Elemental~Mana Reservoir~Spell Damage": ManaReservoir,
					"DALARAN~Neutral~Minion~2~3~2~~Spellbook Binder~Battlecry": SpellbookBinder,
					"DALARAN~Neutral~Minion~2~2~3~~Sunreaver Spy~Battlecry": SunreaverSpy,
					"DALARAN~Neutral~Minion~2~3~2~~Zayle, Shadow Cloak~Legendary": ZayleShadowCloak,
					"DALARAN~Neutral~Minion~3~5~6~~Arcane Watcher": ArcaneWatcher,
					"DALARAN~Neutral~Minion~3~5~1~~Faceless Rager~Battlecry": FacelessRager,
					"DALARAN~Neutral~Minion~3~3~4~~Flight Master~Battlecry": FlightMaster,
					"DALARAN~Neutral~Minion~2~2~2~Beast~Gryphon~Uncollectible": Gryphon,
					"DALARAN~Neutral~Minion~3~3~3~~Hench-Clan Sneak~Stealth": HenchClanSneak,
					"DALARAN~Neutral~Minion~3~1~6~~Magic Carpet": MagicCarpet,
					"DALARAN~Neutral~Minion~3~3~4~~Spellward Jeweler~Battlecry": SpellwardJeweler,
					"DALARAN~Neutral~Minion~4~2~6~~Archmage Vargoth~Legendary": ArchmageVargoth,
					"DALARAN~Neutral~Minion~4~3~8~Mech~Hecklebot~Taunt~Battlecry": Hecklebot,
					"DALARAN~Neutral~Minion~4~3~3~~Hench-Clan Hag~Battlecry": HenchClanHag,
					"DALARAN~Neutral~Minion~1~1~1~Elemental,Mech,Demon,Murloc,Dragon,Beast,Pirate,Totem~Amalgam~Uncollectible": Amalgam,
					"DALARAN~Neutral~Minion~4~5~2~Demon~Portal Keeper~Battlecry": PortalKeeper,
					"DALARAN~Neutral~Spell~2~Felhound Portal~Casts When Drawn~Uncollectible": FelhoundPortal,
					"DALARAN~Neutral~Minion~2~2~2~Demon~Felhound~Rush~Uncollectible": Felhound,
					"DALARAN~Neutral~Minion~4~2~6~~Proud Defender~Taunt": ProudDefender,
					"DALARAN~Neutral~Minion~4~5~6~Elemental~Soldier of Fortune": SoldierofFortune,
					"DALARAN~Neutral~Minion~4~3~2~~Traveling Healer~Battlecry~Divine Shield": TravelingHealer,
					"DALARAN~Neutral~Minion~4~1~6~~Violet Spellsword~Battlecry": VioletSpellsword,
					"DALARAN~Neutral~Minion~5~2~7~Elemental~Azerite Elemental": AzeriteElemental,
					"DALARAN~Neutral~Minion~5~4~5~~Barista Lynchen~Battlecry~Legendary": BaristaLynchen,
					"DALARAN~Neutral~Minion~5~5~4~~Dalaran Crusader~Divine Shield": DalaranCrusader,
					"DALARAN~Neutral~Minion~5~3~6~~Recurring Villain~Deathrattle": RecurringVillain,
					"DALARAN~Neutral~Minion~5~4~4~~Sunreaver Warmage~Battlecry": SunreaverWarmage,
					"DALARAN~Neutral~Minion~6~6~4~~Eccentric Scribe~Deathrattle": EccentricScribe,
					"DALARAN~Neutral~Minion~1~1~1~~Vengeful Scroll~Uncollectible": VengefulScroll,
					"DALARAN~Neutral~Minion~6~4~4~Demon~Mad Summoner~Battlecry": MadSummoner,
					"DALARAN~Neutral~Minion~1~1~1~Demon~Imp~Uncollectible": Imp_Shadows,
					"DALARAN~Neutral~Minion~6~5~6~Demon~Portal Overfiend~Battlecry": PortalOverfiend,
					"DALARAN~Neutral~Minion~6~4~5~Mech~Safeguard~Taunt~Deathrattle": Safeguard,
					"DALARAN~Neutral~Minion~2~0~5~Mech~Vault Safe~Taunt~Uncollectible": VaultSafe,
					"DALARAN~Neutral~Minion~6~5~6~~Unseen Saboteur~Battlecry": UnseenSaboteur,
					"DALARAN~Neutral~Minion~6~4~7~~Violet Warden~Taunt~Spell Damage": VioletWarden,
					"DALARAN~Neutral~Minion~7~6~6~~Chef Nomi~Battlecry~Legendary": ChefNomi,
					"DALARAN~Neutral~Minion~6~6~6~Elemental~Greasefire Elemental~Uncollectible": GreasefireElemental,
					"DALARAN~Neutral~Minion~7~5~8~~Exotic Mountseller": ExoticMountseller,
					"DALARAN~Neutral~Minion~7~3~7~~Tunnel Blaster~Taunt~Deathrattle": TunnelBlaster,
					"DALARAN~Neutral~Minion~7~3~5~~Underbelly Ooze": UnderbellyOoze,
					"DALARAN~Neutral~Minion~8~3~12~~Batterhead~Rush": Batterhead,
					"DALARAN~Neutral~Minion~8~4~4~~Heroic Innkeeper~Taunt~Battlecry": HeroicInnkeeper,
					"DALARAN~Neutral~Minion~8~6~6~~Jepetto Joybuzz~Battlecry~Legendary": JepettoJoybuzz,
					"DALARAN~Neutral~Minion~8~6~6~Elemental~Whirlwind Tempest": WhirlwindTempest,
					"DALARAN~Neutral~Minion~9~9~9~~Burly Shovelfist~Rush": BurlyShovelfist,
					"DALARAN~Neutral~Minion~9~7~7~~Archivist Elysiana~Battlecry~Legendary": ArchivistElysiana,
					"DALARAN~Neutral~Minion~10~6~6~~Big Bad Archmage": BigBadArchmage,
					#Druid
					"DALARAN~Druid~Minion~1~2~1~~Acornbearer~Deathrattle": Acornbearer,
					"DALARAN~Druid~Minion~1~1~1~Beast~Squirrel~Uncollectible": Squirrel_Shadows,
					"DALARAN~Druid~Spell~1~Crystal Power~Choose One": CrystalPower,
					"DALARAN~Druid~Spell~1~Piercing Thorns~Uncollectible": PiercingThorns,
					"DALARAN~Druid~Spell~1~Healing Blossom~Uncollectible": HealingBlossom,
					"DALARAN~Druid~Spell~2~Crystalsong Portal": CrystalsongPortal,
					"DALARAN~Druid~Spell~2~Dreamway Guardians": DreamwayGuardians,
					"DALARAN~Druid~Minion~1~1~2~~Crystal Dryad~Lifesteal~Uncollectible": CrystalDryad,
					"DALARAN~Druid~Minion~2~2~3~~Keeper Stalladris~Legendary": KeeperStalladris,
					"DALARAN~Druid~Minion~3~2~5~~Lifeweaver": Lifeweaver,
					"DALARAN~Druid~Minion~5~4~4~Beast~Crystal Stag~Rush~Battlecry": CrystalStag,
					"DALARAN~Druid~Spell~3~Blessing of the Ancients~Twinspell": BlessingoftheAncients,
					"DALARAN~Druid~Spell~3~Blessing of the Ancients~Uncollectible": BlessingoftheAncients2,
					"DALARAN~Druid~Minion~8~4~8~~Lucentbark~Taunt~Deathrattle~Legendary": Lucentbark,
					"DALARAN~Druid~Spell~8~The Forest's Aid~Twinspell": TheForestsAid,
					"DALARAN~Druid~Spell~8~The Forest's Aid~Uncollectible": TheForestsAid2,
					"DALARAN~Druid~Minion~2~2~2~~Treant~Uncollectible": Treant_Shadows,
					#Hunter
					"DALARAN~Hunter~Spell~1~Rapid Fire~Twinspell": RapidFire,
					"DALARAN~Hunter~Spell~1~Rapid Fire~Uncollectible": RapidFire2,
					"DALARAN~Hunter~Minion~1~1~1~Beast~Shimmerfly~Deathrattle": Shimmerfly,
					"DALARAN~Hunter~Spell~3~Nine Lives": NineLives,
					"DALARAN~Hunter~Minion~3~3~3~Mech~Ursatron~Deathrattle": Ursatron,
					"DALARAN~Hunter~Minion~4~3~3~~Arcane Fletcher": ArcaneFletcher,
					"DALARAN~Hunter~Spell~4~Marked Shot": MarkedShot,
					"DALARAN~Hunter~Spell~5~Hunting Party": HuntingParty,
					"DALARAN~Hunter~Minion~6~3~4~Mech~Oblivitron~Deathrattle~Legendary": Oblivitron,
					"DALARAN~Hunter~Spell~6~Unleash the Beast~Twinspell": UnleashtheBeast,
					"DALARAN~Hunter~Spell~6~Unleash the Beast~Uncollectible": UnleashtheBeast2,
					"DALARAN~Hunter~Minion~5~5~5~Beast~Wyvern~Rush~Uncollectible": Wyvern,
					"DALARAN~Hunter~Minion~7~5~6~~Vereesa Windrunner~Battlecry~Legendary": VereesaWindrunner,
					"DALARAN~Hunter~Weapon~3~2~3~Thori'dal, the Stars' Fury~Legendary~Uncollectible": ThoridaltheStarsFury,
					#Mage
					"DALARAN~Mage~Spell~1~Ray of Frost~Twinspell": RayofFrost,
					"DALARAN~Mage~Spell~1~Ray of Frost~Uncollectible": RayofFrost2,
					"DALARAN~Mage~Minion~2~2~2~~Khadgar~Legendary": Khadgar,
					"DALARAN~Mage~Minion~2~1~3~Beast~Magic Dart Frog": MagicDartFrog,
					"DALARAN~Mage~Minion~3~3~2~Beast~Messenger Raven~Battlecry": MessengerRaven,
					"DALARAN~Mage~Spell~1~Magic Trick": MagicTrick,
					"DALARAN~Mage~Spell~4~Conjurer's Calling~Twinspell": ConjurersCalling,
					"DALARAN~Mage~Spell~4~Conjurer's Calling~Uncollectible": ConjurersCalling2,
					"DALARAN~Mage~Minion~4~3~3~~Kirin Tor Tricaster": KirinTorTricaster,
					"DALARAN~Mage~Minion~2~2~2~Elemental~Mana Cyclone~Battlecry": ManaCyclone,
					"DALARAN~Mage~Spell~8~Power of Creation": PowerofCreation,
					"DALARAN~Mage~Minion~10~4~12~Dragon~Kalecgos~Legendary": Kalecgos,
					#Paladin
					"DALARAN~Paladin~Spell~1~Never Surrender!~~Secret": NeverSurrender,
					"DALARAN~Paladin~Spell~2~Lightforged Blessing~Twinspell": LightforgedBlessing,
					"DALARAN~Paladin~Spell~2~Lightforged Blessing~Uncollectible": LightforgedBlessing2,
					"DALARAN~Paladin~Minion~3~3~2~Dragon~Bronze Herald~Deathrattle": BronzeHerald,
					"DALARAN~Paladin~Minion~4~4~4~Dragon~Bronze Dragon~Uncollectible": BronzeDragon,
					"DALARAN~Paladin~Spell~1~Desperate Measures~Twinspell": DesperateMeasures,
					"DALARAN~Paladin~Spell~1~Desperate Measures~Uncollectible": DesperateMeasures2,
					"DALARAN~Paladin~Weapon~2~2~2~Mysterious Blade~Battlecry": MysteriousBlade,
					"DALARAN~Paladin~Spell~3~Call to Adventure": CalltoAdventure,
					"DALARAN~Paladin~Minion~5~3~5~~Dragon Speaker~Battlecry": DragonSpeaker,
					"DALARAN~Paladin~Spell~5~Duel!": Duel,
					"DALARAN~Paladin~Minion~3~4~3~~Commander Rhyssa~Legendary": CommanderRhyssa,
					"DALARAN~Paladin~Minion~10~4~12~Dragon~Nozari~Battlecry~Legendary": Nozari,
					#Priest
					"DALARAN~Priest~Minion~2~2~2~~EVIL Conscripter~Deathrattle": EVILConscripter,
					"DALARAN~Priest~Minion~4~4~7~~Hench-Clan Shadequill~Deathrattle": HenchClanShadequill,
					"DALARAN~Priest~Spell~4~Unsleeping Soul": UnsleepingSoul,
					"DALARAN~Priest~Spell~0~Forbidden Words": ForbiddenWords,
					"DALARAN~Priest~Minion~5~2~6~~Convincing Infiltrator~Taunt~Deathrattle": ConvincingInfiltrator,
					"DALARAN~Priest~Spell~9~Mass Resurrection": MassResurrection,
					"DALARAN~Priest~Spell~0~Lazul's Scheme": LazulsScheme,
					"DALARAN~Priest~Minion~2~2~2~~Shadowy Figure~Battlecry": ShadowyFigure,
					"DALARAN~Priest~Minion~3~3~2~~Madame Lazul~Battlecry~Legendary": MadameLazul,
					"DALARAN~Priest~Minion~8~6~8~~Catrina Muerte~Legendary": CatrinaMuerte,
					#Rogue
					"DALARAN~Rogue~Spell~1~Daring Escape": DaringEscape,
					"DALARAN~Rogue~Minion~3~1~4~~EVIL Miscreant~Combo": EVILMiscreant,
					"DALARAN~Rogue~Minion~4~4~3~Pirate~Hench-Clan Burglar~Battlecry": HenchClanBurglar,
					"DALARAN~Rogue~Spell~1~Togwaggle's Scheme": TogwagglesScheme,
					"DALARAN~Rogue~Minion~2~2~3~~Underbelly Fence~Battlecry": UnderbellyFence,
					"DALARAN~Rogue~Spell~4~Vendetta": Vendetta,
					"DALARAN~Rogue~Weapon~4~4~2~Waggle Pick~Deathrattle": WagglePick,
					"DALARAN~Rogue~Spell~6~Unidentified Contract": UnidentifiedContract,
					"DALARAN~Rogue~Spell~6~Assassin's Contract~Uncollectible": AssassinsContract,
					"DALARAN~Rogue~Spell~6~Lucrative Contract~Uncollectible": LucrativeContract,
					"DALARAN~Rogue~Spell~6~Recruitment Contract~Uncollectible": RecruitmentContract,
					"DALARAN~Rogue~Spell~6~Turncoat Contract~Uncollectible": TurncoatContract,
					"DALARAN~Rogue~Minion~6~5~5~~Heistbaron Togwaggle~Battlecry": HeistbaronTogwaggle,
					"DALARAN~Rogue~Minion~7~6~6~~Tak Nozwhisker": TakNozwhisker,
					#Shaman
					"DALARAN~Shaman~Spell~0~Mutate": Mutate,
					"DALARAN~Shaman~Minion~1~2~1~Murloc~Sludge Slurper~Battlecry~Overload": SludgeSlurper,
					"DALARAN~Shaman~Spell~2~Soul of the Murloc": SouloftheMurloc,
					"DALARAN~Shaman~Minion~2~2~3~Murloc~Underbelly Angler": UnderbellyAngler,
					"DALARAN~Shaman~Spell~5~Hagatha's Scheme": HagathasScheme,
					"DALARAN~Shaman~Minion~8~4~8~Elemental~Walking Fountain~Rush~Lifesteal~Windfury": WalkingFountain,
					"DALARAN~Shaman~Spell~2~Witch's Brew": WitchsBrew,
					"DALARAN~Shaman~Minion~5~4~4~~Muckmorpher~Battlecry": Muckmorpher,
					"DALARAN~Shaman~Minion~4~4~4~Murloc~Scargil~Legendary": Scargil,
					"DALARAN~Shaman~Minion~7~5~5~~Swampqueen Hagatha~Battlecry~Legendary": SwampqueenHagatha,
					#Warlock
					"DALARAN~Warlock~Minion~2~2~2~~EVIL Genius~Battlecry": EVILGenius,
					"DALARAN~Warlock~Spell~3~Rafaam's Scheme": RafaamsScheme,
					"DALARAN~Warlock~Minion~6~4~6~Demon~Aranasi Broodmother~Taunt~Triggers when Drawn": AranasiBroodmother,
					"DALARAN~Warlock~Spell~2~Plot Twist": PlotTwist,
					"DALARAN~Warlock~Spell~3~Impferno": Impferno,
					"DALARAN~Warlock~Minion~4~2~2~~Eager Underling~Deathrattle": EagerUnderling,
					"DALARAN~Warlock~Spell~6~Darkest Hour": DarkestHour,
					"DALARAN~Warlock~Minion~10~8~8~Demon~Jumbo Imp": JumboImp,
					"DALARAN~Warlock~Minion~7~7~8~~Arch-Villain Rafaam~Taunt~Battlecry~Legendary": ArchVillainRafaam,
					"DALARAN~Warlock~Minion~8~5~7~Demon~Fel Lord Betrug~Legendary": FelLordBetrug,
					#Warrior
					"DALARAN~Warrior~Spell~1~Improve Morale": ImproveMorale,
					"DALARAN~Warrior~Minion~2~2~2~Mech~Vicious Scraphound": ViciousScraphound,
					"DALARAN~Warrior~Spell~4~Dr. Boom's Scheme": DrBoomsScheme,
					"DALARAN~Warrior~Spell~2~Sweeping Strikes": SweepingStrikes,
					"DALARAN~Warrior~Minion~3~3~3~Mech~Clockwork Goblin~Battlecry": ClockworkGoblin,
					"DALARAN~Warrior~Spell~10~Dimensional Ripper": DimensionalRipper,
					"DALARAN~Warrior~Minion~4~4~5~Mech~Omega Devastator~Battlecry": OmegaDevastator,
					"DALARAN~Warrior~Weapon~4~3~2~Wrenchcalibur": Wrenchcalibur,
					"DALARAN~Warrior~Minion~7~7~7~~Blastmaster Boom~Battlecry~Legendary": BlastmasterBoom,
					"DALARAN~Warrior~Minion~10~7~9~Mech~The Boom Reaver~Battlecry~Legendary": TheBoomReaver,
					}