from CardTypes import *
from Triggers_Auras import *
from Basic import TheCoin
from Dragons import Lackeys

from numpy.random import choice as npchoice
from numpy.random import randint as nprandint
from numpy.random import shuffle as npshuffle

def extractfrom(target, listObj):
	try: return listObj.pop(listObj.index(target))
	except: return None
	
def fixedList(listObj):
	return listObj[0:len(listObj)]
	
def PRINT(game, string, *args):
	if game.GUI:
		if not game.mode: game.GUI.printInfo(string)
	elif not game.mode: print("game's guide mode is 0\n", string)
	
def classforDiscover(initiator):
	Class = initiator.Game.heroes[initiator.ID].Class
	if Class != "Neutral": return Class #如果发现的发起者的职业不是中立，则返回那个职业
	elif initiator.Class != "Neutral": return initiator.Class #如果玩家职业是中立，但卡牌职业不是中立，则发现以那个卡牌的职业进行
	else: return npchoice(initiator.Game.Classes) #如果玩家职业和卡牌职业都是中立，则随机选取一个职业进行发现。
	
def fixedList(listObj):
	return listObj[0:len(listObj)]
	
"""Neutral cards"""
class SkydivingInstructor(Minion):
	Class, race, name = "Neutral", "", "Skydiving Instructor"
	mana, attack, health = 3, 2, 2
	index = "Dragons~Neutral~Minion~3~2~2~None~Skydiving Instructor~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Summon a 1-Cost minion from your deck"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if curGame.mode == 0:
			PRINT(curGame, "Skydiving Instructor's battlecry summons a 1-Cost minion from player's deck")
			if curGame.guides:
				i = curGame.guides.pop(0)
			else:
				minions = [i for i, card in enumerate(curGame.Hand_Deck.decks[self.ID]) if card.mana == 1]
				i = npchoice(minions) if minions and curGame.space(self.ID) > 0 else -1
				curGame.fixedGuides.append(i)
			if i > -1: curGame.summonfromDeck(i, self.ID, self.position+1, self.ID)
		return None
		
		
class Hailbringer(Minion):
	Class, race, name = "Neutral", "Elemental", "Hailbringer"
	mana, attack, health = 5, 3, 4
	index = "Dragons~Neutral~Minion~5~3~4~Elemental~Hailbringer~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Summon two 1/1 Ice Shards that Freeze"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		PRINT(self.Game, "Hailbringer's battlecry summons two 1/1 Ice Shards that Freeze")
		pos = (self.position, "leftandRight") if self.onBoard else (-1, "totheRightEnd")
		self.Game.summon([IceShard(self.Game, self.ID) for i in range(2)], pos, self.ID)
		return None
		
class IceShard(Minion):
	Class, race, name = "Neutral", "Elemental", "Ice Shard"
	mana, attack, health = 1, 1, 1
	index = "Dragons~Neutral~Minion~1~1~1~Elemental~Ice Shard~Uncollectible"
	requireTarget, keyWord, description = False, "", "Freeze any character damaged by this minion"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_IceShard(self)]
		
class Trig_IceShard(TrigBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionTakesDmg", "HeroTakesDmg"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return subject == self.entity
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self.entity.Game, "%s deals damage to %s and freezes it."%(self.entity.name, target.name))
		target.getsFrozen()
		
		
class LicensedAdventurer(Minion):
	Class, race, name = "Neutral", "", "Licensed Adventurer"
	mana, attack, health = 2, 3, 2
	index = "Dragons~Neutral~Minion~2~3~2~None~Licensed Adventurer~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: If you control a Quest, add a Coin to your hand"
	def effectCanTrigger(self):
		self.effectViable = self.Game.Secrets.mainQuests[self.ID] != [] or self.Game.Secrets.sideQuests[self.ID] != []
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if self.Game.Secrets.mainQuests[self.ID] != [] or self.Game.Secrets.sideQuests[self.ID] != []:
			PRINT(self.Game, "Licensed Adventurer's battlecry adds a Coin to player's hand")
			self.Game.Hand_Deck.addCardtoHand(TheCoin, self.ID, "type")
		return None
		
class FrenziedFelwing(Minion):
	Class, race, name = "Neutral", "Demon", "Frenzied Felwing"
	mana, attack, health = 4, 3, 2
	index = "Dragons~Neutral~Minion~4~3~2~Demon~Frenzied Felwing"
	requireTarget, keyWord, description = False, "", "Costs (1) less for each damage dealt to your opponent this turn"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsHand = [Trig_FrenziedFelwing(self)]
		
	def selfManaChange(self):
		if self.inHand:
			manaReduction = self.Game.Counters.damageonHeroThisTurn[3-self.ID]
			PRINT(self.Game, "Frenzied Felwig reduces its own cost by (%d)"%manaReduction)
			self.mana -= manaReduction
			self.mana = max(0, self.mana)
			
class Trig_FrenziedFelwing(TrigHand):
	def __init__(self, entity):
		self.blank_init(entity, ["HeroTakesDmg"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.inHand and target == self.entity.Game.heroes[3-self.entity.ID]
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.Game.Manas.calcMana_Single(self.entity)
		
		
class EscapedManasaber(Minion):
	Class, race, name = "Neutral", "Beast", "Escaped Manasaber"
	mana, attack, health = 4, 3, 5
	index = "Dragons~Neutral~Minion~4~3~5~Beast~Escaped Manasaber~Stealth"
	requireTarget, keyWord, description = False, "Stealth", "Stealth. Whenever this attacks, gain 1 Mana Crystal this turn only"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_EscapedManasaber(self)]
		
class Trig_EscapedManasaber(TrigBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionAttackingMinion", "MinionAttackingHero"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return subject == self.entity and self.entity.onBoard
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self.entity.Game, "Whenever it attacks, %s gives player a Mana Crystal for this turn only."%self.entity.name)
		if self.entity.Game.Manas.manas[self.entity.ID] < 10:
			self.entity.Game.Manas.manas[self.entity.ID] += 1
			
			
class BoompistolBully(Minion):
	Class, race, name = "Neutral", "", "Boompistol Bully"
	mana, attack, health = 5, 5, 5
	index = "Dragons~Neutral~Minion~5~5~5~None~Boompistol Bully~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Enemy Battlecry cards cost (5) more next turn"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		PRINT(self.Game, "Boompistol Bully's battlecry makes enemy Battlecry cards cost (5) more next turn.")
		self.Game.Manas.CardAuras_Backup.append(BattlecryCardsCost5MoreNextTurn(self.Game, 3-self.ID))
		return None
		
class BattlecryCardsCost5MoreNextTurn(TempManaEffect):
	def __init__(self, Game, ID):
		self.Game, self.ID = Game, ID
		self.changeby, self.changeto = +5, -1
		self.temporary = True
		self.auraAffected = []
		
	def applicable(self, subject):
		return subject.ID == self.ID and "~Battlecry" in subject.index
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.applies(target[0])
		
	#持续整个回合的光环可以不必注册"ManaPaid"
	def auraAppears(self):
		for card in self.Game.Hand_Deck.hands[1]: self.applies(card)
		for card in self.Game.Hand_Deck.hands[2]: self.applies(card)
			
		try: self.Game.trigsBoard[self.ID]["CardEntersHand"].append(self)
		except: self.Game.trigsBoard[self.ID]["CardEntersHand"] = [self]
		self.Game.Manas.calcMana_All()
		
	#auraDisappears()可以尝试移除ManaPaid，当然没有反应，所以不必专门定义
	def selfCopy(self, game):
		return type(self)(game, self.ID)
		
		
class GrandLackeyErkh(Minion):
	Class, race, name = "Neutral", "", "Grand Lackey Erkh"
	mana, attack, health = 4, 2, 3
	index = "Dragons~Neutral~Minion~4~2~3~None~Grand Lackey Erkh~Legendary"
	requireTarget, keyWord, description = False, "", "After you play a Lackey, add a Lackey to your hand"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_GrandLackeyErkh(self)]
		
class Trig_GrandLackeyErkh(TrigBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionBeenPlayed"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject.ID == self.entity.ID and subject.name.endswith(" Lackey")
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		curGame = self.entity.Game
		if curGame.mode == 0:
			if curGame.guides:
				lackey = curGame.guides.pop(0)
			else:
				lackey = npchoice(Lackeys)
				curGame.fixedGuides.append(lackey)
			PRINT(curGame, "After player plays a Lackey, Grand Lackey Erkh adds a Lackey to player's hand")
			curGame.Hand_Deck.addCardtoHand(lackey, self.entity.ID, "type")
			
			
class SkyGenralKragg(Minion):
	Class, race, name = "Neutral", "Pirate", "Sky Gen'ral Kragg"
	mana, attack, health = 4, 2, 3
	index = "Dragons~Neutral~Minion~4~2~3~Pirate~Sky Gen'ral Kragg~Battlecry~Legendary"
	requireTarget, keyWord, description = False, "Taunt", "Taunt. Battlecry: If you've played a Quest this game, summon a 4/2 Parrot with Rush"
	def effectCanTrigger(self):
		self.effectViable = self.Game.Counters.hasPlayedQuestThisGame[self.ID]
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if self.Game.Counters.hasPlayedQuestThisGame[self.ID]:
			PRINT(self.Game, "Sky Gen'ral Kragg's battlecry summons a 4/2 Parrot with Rush")
			self.Game.summon(Sharkbait(self.Game, self.ID), self.position+1, self.ID)
		return None
		
class Sharkbait(Minion):
	Class, race, name = "Neutral", "Beast", "Sharkbait"
	mana, attack, health = 4, 4, 2
	index = "Dragons~Neutral~Minion~4~4~2~Beast~Sharkbait~Rush~Legendary~Uncollectible"
	requireTarget, keyWord, description = False, "Rush", "Rush"
	
	
"""Druid cards"""
class RisingWinds(Spell):
	Class, name = "Druid", "Rising Winds"
	requireTarget, mana = False, 2
	index = "Dragons~Druid~Spell~2~Rising Winds~Twinspell~Choose One"
	description = "Twinspell. Choose One- Draw a card; or Summon a 3/2 Eagle"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.twinSpell = 1
		self.twinSpellCopy = risingwinds
		self.chooseOne = 1
		self.options = [TakeFlight_Option(self), SwoopIn_Option(self)]
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if choice < 1:
			PRINT(self.Game, "Rising Winds lets player draw a card")
			self.Game.Hand_Deck.drawCard(self.ID)
		if choice != 0:
			PRINT(self.Game, "Rising Winds summons a 3/2 Eagle")
			self.Game.summon(Eagle(self.Game, self.ID), -1, self.ID)
		return None
		
class risingwinds(Spell):
	Class, name = "Druid", "Rising Winds"
	requireTarget, mana = False, 2
	index = "Dragons~Druid~Spell~2~Rising Winds~Choose One~Uncollectible"
	description = "Choose One- Draw a card; or Summon a 3/2 Eagle"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.chooseOne = 1
		self.options = [TakeFlight_Option(self), SwoopIn_Option(self)]
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if choice < 1:
			PRINT(self.Game, "Rising Winds lets player draw a card")
			self.Game.Hand_Deck.drawCard(self.ID)
		if choice != 0:
			PRINT(self.Game, "Rising Winds summons a 3/2 Eagle")
			self.Game.summon(Eagle(self.Game, self.ID), -1, self.ID)
		return None
		
class TakeFlight_Option(ChooseOneOption):
	name, description = "Take Flight", "Draw a card"
	index = "Dragons~Druid~Spell~2~Take Flight~Uncollectible"
	
class SwoopIn_Option(ChooseOneOption):
	name, description = "Swoop In", "Summon a 3/2 Eagle"
	index = "Dragons~Druid~Spell~2~Swoop In~Uncollectible"
	def available(self):
		return self.entity.Game.space(self.entity.ID) > 0
		
class TakeFlight(Spell):
	Class, name = "Druid", "Take Flight"
	requireTarget, mana = False, 2
	index = "Dragons~Druid~Spell~2~Take Flight~Uncollectible"
	description = "Draw a card"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		PRINT(self.Game, "Take Flight is cast and lets player draw a card")
		self.Game.Hand_Deck.drawCard(self.ID)
		return None
		
class SwoopIn(Spell):
	Class, name = "Druid", "Swoop In"
	requireTarget, mana = False, 2
	index = "Dragons~Druid~Spell~2~Swoop In~Uncollectible"
	description = "Summon a 3/2 Eagle"
	def available(self):
		return self.Game.space(self.ID) > 0
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		PRINT(self.Game, "Swoop In is cast and summons a 3/2 Eagle")
		self.Game.summon(Eagle(self.Game, self.ID), -1, self.ID)
		return None
		
class Eagle(Minion):
	Class, race, name = "Druid", "Beast", "Eagle"
	mana, attack, health = 2, 3, 2
	index = "Dragons~Druid~Minion~2~3~2~Beast~Eagle~Uncollectible"
	requireTarget, keyWord, description = False, "", ""
	
	
class SteelBeetle(Minion):
	Class, race, name = "Druid", "Beast", "Steel Beetle"
	mana, attack, health = 2, 2, 3
	index = "Dragons~Druid~Minion~2~2~3~Beast~Steel Beetle~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: If you're holding a spell that costs (5) or more, gain 5 Armor"
	def effectCanTrigger(self):
		self.effectViable = self.Game.Hand_Deck.holdingSpellwith5CostorMore(self.ID)
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if self.Game.Hand_Deck.holdingSpellwith5CostorMore(self.ID):
			PRINT(self.Game, "Steel Beatle's battlecry lets player gain 5 Armor")
			self.Game.heroes[self.ID].gainsArmor(5)
		return None
		
		
class WingedGuardian(Minion):
	Class, race, name = "Druid", "Beast", "Winged Guardian"
	mana, attack, health = 7, 6, 8
	index = "Dragons~Druid~Minion~7~6~8~Beast~Winged Guardian~Taunt~Reborn"
	requireTarget, keyWord, description = False, "Taunt,Reborn", "Taunt, Reborn. Can't be targeted by spells or Hero Powers"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.marks["Evasive"] = True
		
		
"""Hunter cards"""
class FreshScent(Spell):
	Class, name = "Hunter", "Fresh Scent"
	requireTarget, mana = True, 2
	index = "Dragons~Hunter~Spell~2~Fresh Scent~Twinspell"
	description = "Twinspell. Given a Beast +2/+2"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.twinSpell = 1
		self.twinSpellCopy = freshscent
		
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and "Beast" in target.race and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			PRINT(self.Game, "Fresh Scent is cast and gives Beast %s +2/+2"%target.name)
			target.buffDebuff(2, 2)
		return None
		
class freshscent(Spell):
	Class, name = "Hunter", "Fresh Scent"
	requireTarget, mana = True, 2
	index = "Dragons~Hunter~Spell~2~Fresh Scent~Uncollectible"
	description = "Given a Beast +2/+2"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and "Beast" in target.race and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			PRINT(self.Game, "Fresh Scent is cast and gives Beast %s +2/+2"%target.name)
			target.buffDebuff(2, 2)
		return None
		
		
class ChopshopCopter(Minion):
	Class, race, name = "Hunter", "Mech", "Chopshop Copter"
	mana, attack, health = 3, 2, 4
	index = "Dragons~Hunter~Minion~3~2~4~Mech~Chopshop Copter"
	requireTarget, keyWord, description = False, "", "After a friendly Mech dies, add a random Mech to your hand"
	poolIdentifier = "Mechs"
	@classmethod
	def generatePool(cls, Game):
		return "Mechs", list(Game.MinionswithRace["Mech"].values())
		
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_ChopshopCopter(self)]
		
class Trig_ChopshopCopter(TrigBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionDied"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and target.ID == self.entity.ID and "Mech" in target.race
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		curGame = self.entity.Game
		if curGame.mode == 0:
			if curGame.guides:
				mech = curGame.guides.pop(0)
			else:
				mech = npchoice(curGame.RNGPools["Mechs"])
				curGame.fixedGuides.append(mech)
			PRINT(curGame, "After a friendly minion died, Chopshop Copter adds a random Mech to player's hand")
			curGame.Hand_Deck.addCardtoHand(mech, self.entity.ID, "type")
			
			
class RotnestDrake(Minion):
	Class, race, name = "Hunter", "Dragon", "Rotnest Drake"
	mana, attack, health = 5, 6, 5
	index = "Dragons~Hunter~Minion~5~6~5~Dragon~Rotnest Drake~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: If you're holding a Dragon, destroy a random enemy minion"
	def effectCanTrigger(self):
		self.effectViable = self.Game.Hand_Deck.holdingDragon(self.ID, self)
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if curGame.mode == 0:
			PRINT(curGame, "Rotnest Drake's battlecry destroys a random enemy minion")
			if curGame.guides:
				i = curGame.guides.pop(0)
			else:
				minions = [minion.position for minion in curGame.minionsAlive(3-self.ID)]
				i = npchoice(minions) if minions else -1
				curGame.fixedGuides.append(i)
			if i > -1:
				minion = curGame.minions[3-self.ID][i]
				PRINT(curGame, "Rotnest Drake's battlecry destroys random enemy minion %s"%minion.name)
				minion.dead = True
		return None
		
		
"""Mage cards"""
class ArcaneAmplifier(Minion):
	Class, race, name = "Mage", "Elemental", "Arcane Amplifier"
	mana, attack, health = 3, 2, 5
	index = "Dragons~Mage~Minion~3~2~5~Elemental~Arcane Amplifier"
	requireTarget, keyWord, description = False, "", "Your Hero Power deals 2 extra damage"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.appearResponse = [self.activateAura]
		self.disappearResponse = [self.deactivateAura]
		self.silenceResponse = [self.deactivateAura]
		
	def activateAura(self):
		PRINT(self.Game, "Arcane Amplifier's aura is registered. Player %d's Hero Power now deals 2 extra damage, if applicable."%self.ID)
		self.Game.status[self.ID]["Power Damage"] += 2
		
	def deactivateAura(self):
		PRINT(self.Game, "Arcane Amplifier's aura is removed. Player %d's Hero Power no longer deals 2 extra damage."%self.ID)
		self.Game.status[self.ID]["Power Damage"] -= 2
		
		
class AnimatedAvalanche(Minion):
	Class, race, name = "Mage", "Elemental", "Animated Avalanche"
	mana, attack, health = 7, 7, 6
	index = "Dragons~Mage~Minion~7~7~6~Elemental~Animated Avalanche~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: If you played an Elemental last turn, summon a copy of this"
	def effectCanTrigger(self):
		self.effectViable = self.Game.Counters.numElementalsPlayedLastTurn[self.ID] > 0
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if self.Game.Counters.numElementalsPlayedLastTurn[self.ID] > 0:
			PRINT(self.Game, "Animated Avalanche's battlecry summons a copy of the minion.")
			Copy = self.selfCopy(self.ID) if self.onBoard else type(self)(self.Game, self.ID)
			self.Game.summon(Copy, self.position+1, self.ID)
		return None
		
		
class WhatDoesThisDo(HeroPower):
	mana, name, requireTarget = 0, "What Does This Do?", False
	index = "Mage~Hero Power~0~What Does This Do?"
	description = "Passive Hero Power. At the start of your turn, cast a random spell"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_WhatDoesThisDo(self)]
		
	def available(self, choice=0):
		return False
		
	def use(self, target=None, choice=0):
		return 0
		
	def appears(self):
		for trigger in self.trigsBoard:
			trigger.connect() #把(obj, signal)放入Game.trigsBoard 中
		self.Game.sendSignal("HeroPowerAcquired", self.ID, self, None, 0, "")
		
	def disappears(self):
		for trigger in self.trigsBoard:
			trigger.disconnect()
			
class Trig_WhatDoesThisDo(TrigBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["TurnStarts"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		curGame = self.entity.Game
		if curGame.mode == 0:
			PRINT(curGame, "At the start of turn, Hero Power What Does This Do? casts a random spell")
			if curGame.guides:
				spell = curGame.guides.pop(0)
			else:
				spell = npchoice(curGame.RNGPools["Spells"])
				curGame.fixedGuides.append(spell)
			PRINT(curGame, "Hero Power What Does This Do? casts spell %s"%spell.name)
			spell(curGame, self.entity.ID).cast()
			
class TheAmazingReno(Hero):
	mana, description = 10, "Battlecry: Make all minions disappear. *Poof!*"
	Class, name, heroPower, armor = "Mage", "The Amazing Reno", WhatDoesThisDo, 5
	index = "Dragons~Mage~Hero Card~10~The Amazing Reno~Battlecry~Legendary"
	poolIdentifier = "Spells"
	@classmethod
	def generatePool(cls, Game):
		spells = []
		for Class in Game.Classes:
			spells += [value for key, value in Game.ClassCards[Class].items() if "~Spell~" in key]
		return "Spells", spells
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		PRINT(self.Game, "The Amazing Reno's battlecry makes all minions disappear.")
		for minion in fixedList(self.Game.minionsonBoard(1) + self.Game.minionsonBoard(2)):
			minion.disappears(deathrattlesStayArmed=False)
			self.Game.removeMinionorWeapon(minion)
		return None
		
		
"""Paladin cards"""
class Shotbot(Minion):
	Class, race, name = "Paladin", "Mech", "Shotbot"
	mana, attack, health = 2, 2, 2
	index = "Dragons~Paladin~Minion~2~2~2~Mech~Shotbot~Reborn"
	requireTarget, keyWord, description = False, "Reborn", "Reborn"
	
	
class AirRaid(Spell):
	Class, name = "Paladin", "Air Raid"
	requireTarget, mana = False, 2
	index = "Dragons~Paladin~Spell~2~Air Raid~Twinspell"
	description = "Twinspell. Summon two 1/1 Silver Hand Recruits with Taunt"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.twinSpell = 1
		self.twinSpellCopy = airraid
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		PRINT(self.Game, "Air Raid is cast and summons two 1/1 Silve Hand Recruits")
		self.Game.summon([SilverHandRecruit_Dragons(self.Game, self.ID) for i in range(2)], (-1, "totheRightEnd"), self.ID)
		return None
		
class airraid(Spell):
	Class, name = "Paladin", "Air Raid"
	requireTarget, mana = False, 2
	index = "Dragons~Paladin~Spell~2~Air Raid~Uncollectible"
	description = "Summon two 1/1 Silver Hand Recruits with Taunt"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		PRINT(self.Game, "Air Raid is cast and summons two 1/1 Silve Hand Recruits")
		self.Game.summon([SilverHandRecruit_Dragons(self.Game, self.ID) for i in range(2)], (-1, "totheRightEnd"), self.ID)
		return None
		
		
class SilverHandRecruit_Dragons(Minion):
	Class, race, name = "Paladin", "", "Silver Hand Recruit"
	mana, attack, health = 1, 1, 1
	index = "Dragons~Paladin~Minion~1~1~1~None~Silver Hand Recruit~Taunt~Uncollectible"
	requireTarget, keyWord, description = False, "Taunt", "Taunt"
	
	
class Scalelord(Minion):
	Class, race, name = "Paladin", "Dragon", "Scalelord"
	mana, attack, health = 5, 5, 6
	index = "Dragons~Paladin~Minion~5~5~6~Dragon~Scalelord~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Give your Murlocs Divine Shield"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		PRINT(self.Game, "Scalelord's battlecry gives all Friendly Murlocs Divine Shield")
		for minion in fixedList(self.Game.minionsonBoard(self.ID)):
			if "Murloc" in minion.race:
				minion.getsKeyword("Divine Shield")
		return None
		
		
"""Priest cards"""
class AeonReaver(Minion):
	Class, race, name = "Priest", "Dragon", "Aeon Reaver"
	mana, attack, health = 6, 4, 4
	index = "Dragons~Priest~Minion~6~4~4~Dragon~Aeon Reaver~Battlecry"
	requireTarget, keyWord, description = True, "", "Battlecry: Deal damage to a minion equal to its Attack"
	def targetExists(self, choice=0):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target != self and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			PRINT(self.Game, "Aeon Reaver's battlecry deals damage to minion %s equal to its own Attack"%target.name)
			self.dealsDamage(target, target.attack)
		return target
		
		
class ClericofScales(Minion):
	Class, race, name = "Priest", "", "Cleric of Scales"
	mana, attack, health = 1, 1, 1
	index = "Dragons~Priest~Minion~1~1~1~None~Cleric of Scales~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: If you're holding a Dragon, Discover a spell from your deck"
	
	def effectCanTrigger(self):
		self.effectViable = self.Game.Hand_Deck.holdingDragon(self.ID)
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if curGame.Hand_Deck.holdingDragon(self.ID) and self.ID == curGame.turn:
			if curGame.mode == 0:
				if curGame.guides:
					i = curGame.guides.pop(0)
					if i > -1:
						PRINT(curGame, "Cleric of Scales' battlecry lets player draw a spell from deck")
						curGame.Hand_Deck.drawCard(self.ID, i)
				else:
					spells, types = [], []
					for i, card in enumerate(curGame.Hand_Deck.decks[self.ID]):
						if card.type == "Spell" and type(card) not in types:
							spells.append(i)
							types.append(type(card))
					if spells:
						if "byOthers" in comment:
							i = npchoice(spells)
							curGame.fixedGuides.append(i)
							PRINT(curGame, "Cleric of Scales' battlecry lets player draw a random spell from deck")
							curGame.Hand_Deck.drawCard(self.ID, i)
						else:
							PRINT(curGame, "Cleric of Scales' battlecry lets player Discover a spell from their deck")
							curGame.options = npchoice(spells, min(3, len(spells)), replace=False)
							curGame.Discover.startDiscover(self)
					else: curGame.fixedGuides.append(-1)
		return None
		
	def discoverDecided(self, option, info):
		i = self.Game.Hand_Deck.decks[self.ID].index(option)
		self.Game.fixedGuides.append(i)
		self.Game.Hand_Deck.drawCard(self.ID, i)
		
		
class DarkProphecy(Spell):
	Class, name = "Priest", "Dark Prophecy"
	requireTarget, mana = False, 3
	index = "Dragons~Priest~Spell~3~Dark Prophecy"
	description = "Discover a 2-Cost minion. Summon it and give it +3 Health"
	poolIdentifier = "2-Cost Minions as Priest"
	@classmethod
	def generatePool(cls, Game):
		classCards = {s : [] for s in Game.ClassesandNeutral}
		for key, value in Game.MinionsofCost[2].items():
			for Class in key.split('~')[1].split(','):
				classCards[Class].append(value)
		return ["2-Cost Minions as "+Class for Class in Game.Classes], \
			[classCards[Class]+classCards["Neutral"] for Class in Game.Classes]
			
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if curGame.mode == 0:
			if curGame.guides:
				PRINT(curGame, "Dark Prophecy summons a 2-Cost minion with +3 Health")
				minion = curGame.guides.pop(0)(curGame, self.ID)
				minion.buffDebuff(0, 3)
				curGame.summon(minion, -1, self.ID)
			else:
				key = "2-Cost Minions as " + classforDiscover(self)
				if self.ID != curGame.turn or "byOthers" in comment:
					minion = npchoice(curGame.RNGPools[key])
					curGame.fixedGuides.append(minion)
					PRINT(curGame, "Dark Prophecy is cast and summons a random 2-Cost minion and gives it +3 Health")
					minion = minion(curGame, self.ID)
					minion.buffDebuff(0, 3)
					curGame.summon(minion, -1, self.ID)
				else:
					minions = npchoice(curGame.RNGPools[key], 3, replace=False)
					PRINT(curGame, "Dark Prophecy lets player Discover a 2-Cost minion to summon and gain +3 Health")
					curGame.options = [minion(curGame, self.ID) for minion in minions]
					curGame.Discover.startDiscover(self)
		return None
		
	def discoverDecided(self, option, info):
		self.Game.fixedGuides.append(type(option))
		PRINT(self.Game, "Minion %s to summon and give +3 Health is chosen."%option.name)
		option.buffDebuff(0, 3)
		self.Game.summon(option, -1, self.ID)
		
		
"""Rogue cards"""
class Skyvateer(Minion):
	Class, race, name = "Rogue", "Pirate", "Skyvateer"
	mana, attack, health = 2, 1, 3
	index = "Dragons~Rogue~Minion~2~1~3~Pirate~Skyvateer~Stealth~Deathrattle"
	requireTarget, keyWord, description = False, "Stealth", "Stealth. Deathrattle: Draw a card"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [DrawaCard(self)]
		
class DrawaCard(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self.entity.Game, "Deathrattle: Draw a card triggers.")
		self.entity.Game.Hand_Deck.drawCard(self.entity.ID)
		
		
class Waxmancy(Spell):
	Class, name = "Rogue", "Waxmancy"
	requireTarget, mana = False, 2
	index = "Dragons~Rogue~Spell~2~Waxmancy"
	description = "Discover a Battlecry minion. Reduce its Cost by (2)"
	poolIdentifier = "Battlecry Minions as Rogue"
	@classmethod
	def generatePool(cls, Game):
		classCards = {s : [value for key, value in Game.ClassCards[s].items() if "~Minion~" in key and "~Battlecry" in key] for s in Game.Classes}
		classCards["Neutral"] = [value for key, value in Game.NeutralCards.items() if "~Minion~" in key and "~Battlecry" in key]
		return ["Battlecry Minions as "+Class for Class in Game.Classes], \
			[classCards[Class]+classCards["Neutral"] for Class in Game.Classes]
			
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if curGame.mode == 0:
			if curGame.guides:
				PRINT(curGame, "Waxmancy is cast and adds a Battlecry minion to player's hand. It costs (2) less")
				minion = curGame.guides.pop(0)(curGame, self.ID)
				ManaMod(minion, changeby=-2, changeto=-1).applies()
				curGame.Hand_Deck.addCardtoHand(minion, self.ID, byDiscover=True)
			else:
				key = "Battlecry Minions as " + classforDiscover(self)
				if self.ID != curGame.turn or "byOthers" in comment:
					PRINT(curGame, "Waxmancy is cast and adds a random Battlecry minion to player's hand. It costs (2) less")
					minion = npchoice(curGame.RNGPools[key])
					curGame.fixedGuides.append(minion)
					minion = minion(curGame, self.ID)
					ManaMod(minion, changeby=-2, changeto=-1).applies()
					curGame.Hand_Deck.addCardtoHand(minion, self.ID, byDiscover=True)
				else:
					minions = npchoice(curGame.RNGPools[key], 3, replace=False)
					PRINT(curGame, "Waxmancy lets player Discover a Battlecry minion. It costs (2) less")
					curGame.options = [minion(curGame, self.ID) for minion in minions]
					curGame.Discover.startDiscover(self)
		return None
		
	def discoverDecided(self, option, info):
		self.Game.fixedGuides.append(type(option))
		ManaMod(option, changeby=-2, changeto=-1).applies()
		self.Game.Hand_Deck.addCardtoHand(option, self.ID, byDiscover=True)
		
		
class ShadowSculptor(Minion):
	Class, race, name = "Rogue", "", "Shadow Sculptor"
	mana, attack, health = 5, 3, 2
	index = "Dragons~Rogue~Minion~5~3~2~None~Shadow Sculptor~Combo"
	requireTarget, keyWord, description = False, "", "Combo: Draw a card for each card you've played this turn"
	def effectCanTrigger(self):
		self.effectViable = self.Game.Counters.numCardsPlayedThisTurn[self.ID] > 0
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if self.Game.Counters.numCardsPlayedThisTurn[self.ID] > 0:
			numCardsPlayed = len(self.Game.Counters.cardsPlayedThisTurn[self.ID]["Indices"])
			PRINT(self.Game, "Shadow Sculptor's Combo triggers and lets player draw a card for each card they've played this turn")
			for i in range(numCardsPlayed): self.Game.Hand_Deck.drawCard(self.ID)
		return None
		
"""Shaman cards"""
class ExplosiveEvolution(Spell):
	Class, name = "Shaman", "Explosive Evolution"
	requireTarget, mana = True, 2
	index = "Dragons~Shaman~Spell~2~Explosive Evolution"
	description = "Transform a friendly minion into a random one that costs (3) more"
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
				PRINT(curGame, "Explosive Evolution is cast and transforms friendly minion %s to one that costs (3) more."%target.name)
				if curGame.guides:
					newMinion = curGame.guides.pop(0)
				else:
					cost = type(target).mana + 3
					while cost not in curGame.MinionsofCost:
						cost -= 1
					newMinion = npchoice(curGame.RNGPools["%d-Cost Minions to Summon"%cost])
					curGame.fixedGuides.append(newMinion)
				newMinion = newMinion(curGame, target.ID)
				curGame.transform(target, newMinion)
		return newMinion
		
		
class EyeoftheStorm(Spell):
	Class, name = "Shaman", "Eye of the Storm"
	requireTarget, mana = False, 10
	index = "Dragons~Shaman~Spell~10~Eye of the Storm~Overload"
	description = "Summon three 5/6 Elementals with Taunt. Overload: (3)"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.overload = 3
		
	def available(self):
		return self.Game.space(self.ID) > 0
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		PRINT(self.Game, "Eye of the Storm is cast and summons three 5/6 Elementals with Taunt.")
		self.Game.summon([Stormblocker(self.Game, self.ID) for i in range(3)], (-1, "totheRightEnd"), self.ID)
		return None
		
class Stormblocker(Minion):
	Class, race, name = "Shaman", "Elemental", "Stormblocker"
	mana, attack, health = 5, 5, 6
	index = "Dragons~Shaman~Minion~5~5~6~Elemental~Stormblocker~Taunt~Uncollectible"
	requireTarget, keyWord, description = False, "Taunt", "Taunt"
	
	
#莱登之拳对于费用不在随机池中的法术不会响应，但是埃提耶什会消耗一个耐久度，但是不会召唤随从
class TheFistofRaden(Weapon):
	Class, name, description = "Shaman", "The Fist of Ra-den", "After you cast a spell, summon a Legendary minion of that Cost. Lose 1 Durability"
	mana, attack, durability = 4, 1, 4
	index = "Dragons~Shaman~Weapon~4~1~4~The Fist of Ra-den~Legendary"
	poolIdentifier = "1-Cost Legendary Minions to Summon"
	@classmethod
	def generatePool(cls, Game):
		minions = {}
		for key, value in Game.LegendaryMinions.items():
			s = key.split('~')[3] + "-Cost Legendary Minions to Summon"
			try: minions[s].append(value)
			except: minions[s] = [value]
		return list(minions.keys()), list(minions.values())
		
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_TheFistofRaden(self)]
		
class Trig_TheFistofRaden(TrigBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["SpellBeenPlayed"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return subject.ID == self.entity.ID and self.entity.onBoard and self.entity.durability > 0
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		curGame = self.entity.Game
		if curGame.mode == 0:
			PRINT(curGame, "After player casts a spell %s, The Fist of Raden summons a random Legendary minion with that Cost and loses 1 Durability."%subject.name)
			if curGame.guides:
				minion = curGame.guides.pop(0)
			else:
				s = "%d-Cost Legendary Minions to Summon"%number
				minion = npchoice(curGame.RNGPools[s]) if s in curGame.RNGPools and curGame.space(self.entity.ID) > 0 else None
				curGame.fixedGuides.append(minion)
			if minion:
				curGame.summon(minion(curGame, self.entity.ID), -1, self.entity.ID)
				self.entity.loseDurability()
				
				
"""Warlock cards"""
class FiendishServant(Minion):
	Class, race, name = "Warlock", "Demon", "Fiendish Servant"
	mana, attack, health = 1, 2, 1
	index = "Dragons~Warlock~Minion~1~2~1~Demon~Fiendish Servant~Deathrattle"
	requireTarget, keyWord, description = False, "", "Deathrattle: Give this minion's Attack to a random friendly minion"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [GiveAttacktoaRandomFriendlyMinion(self)]
		
class GiveAttacktoaRandomFriendlyMinion(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		curGame = self.entity.Game
		if curGame.mode == 0:
			PRINT(curGame, "Deathrattle: Give this minion's Attack %d to a random friendly minion triggers."%number)
			if curGame.guides:
				i = curGame.guides.pop(0)
			else:
				minions = [minion.position for minion in curGame.minionsonBoard(self.entity.ID)]
				i = npchoice(minions) if minions else -1
				curGame.fixedGuides.append(i)
			if i > -1:
				minion = curGame.minions[self.entity.ID][i]
				PRINT(curGame, "%s gets the Attack given by %s"%(target.name, self.entity.Game))
				minion.buffDebuff(number, 0)
				
				
class TwistedKnowledge(Spell):
	Class, name = "Warlock", "Twisted Knowledge"
	requireTarget, mana = False, 2
	index = "Dragons~Warlock~Spell~2~Twisted Knowledge"
	description = "Discover 2 Warlock cards"
	poolIdentifier = "Warlock Cards"
	@classmethod
	def generatePool(cls, Game):
		return "Warlock", list(Game.ClassCards["Warlock"].values())
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		for num in range(2):
			curGame = self.Game
			if curGame.mode == 0:
				if curGame.guides:
					PRINT(curGame, "Twisted Knowledge adds a Warlock card to player's hand")
					curGame.Hand_Deck.addCardtoHand(curGame.guides.pop(0), self.ID, "type", byDiscover=True)
				else:
					if self.ID != curGame.turn or "byOthers" in comment:
						card = npchoice(curGame.RNGPools["Warlock Cards"])
						curGame.fixedGuides.append(card)
						PRINT(curGame, "Twisted Knowledge is cast and adds a random Warlock card to player's hand")
						curGame.Hand_Deck.addCardtoHand(curGame, self.ID, "type", byDiscover=True)
					else:
						cards = npchoice(curGame.RNGPools["Warlock Cards"], 3, replace=False)
						PRINT(curGame, "Twisted Knowledge lets player Discover a Warlock card")
						curGame.options = [card(curGame, self.ID) for card in cards]
						curGame.Discover.startDiscover(self)
		return None
		
	def discoverDecided(self, option, info):
		self.Game.fixedGuides.append(type(option))
		self.Game.Hand_Deck.addCardtoHand(option, self.ID, byDiscover=True)
		
#只会考虑当前的费用，寻找下回合法力值以下的牌。延时生效的法力值效果不会被考虑。
#如果被战吼触发前被对方控制了，则也会根据我方下个回合的水晶进行腐化。但是这个回合结束时就会丢弃（因为也算是一个回合。）
#https://www.bilibili.com/video/av92443139?from=search&seid=7929483619040209451
class ChaosGazer(Minion):
	Class, race, name = "Warlock", "Demon", "Chaos Gazer"
	mana, attack, health = 3, 4, 3
	index = "Dragons~Warlock~Minion~3~4~3~Demon~Chaos Gazer~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Corrupt a playable card in your opponent's hand. They have 1 turn to play it!"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if curGame.mode == 0:
			PRINT(curGame, "Chaos Gazer's battlecry corrupts a playable card in opponent's hand")
			if curGame.guides:
				i = curGame.guides.pop(0)
			else:
				manaNextTurn = max(0, min(10, curGame.Manas.manasUpper[3-self.ID] + 1) - curGame.Manas.manasOverloaded[3-self.ID])
				cards = [i for i, card in enumerate(curGame.Hand_Deck.hands[3-self.ID]) \
							if card.mana <= manaNextTurn and Trig_CorruptedHand not in [type(trig) for trig in card.trigsHand]]
				i = npchoice(cards) if cards else -1
				curGame.fixedGuides.append(i)
			if i > -1:
				card = curGame.Hand_Deck.hands[3-self.ID][i]
				trig = Trig_CorruptedHand(card)
				card.trigsHand.append(trig)
				trig.connect()
		return None
		
class Trig_CorruptedHand(TrigHand):
	def __init__(self, entity):
		self.blank_init(entity, ["TurnEnds"])
		self.temp = True
		self.makesCardEvanescent = True
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		#被腐蚀的卡只会在其拥有者的回合结束时才会被丢弃
		return self.entity.inHand and self.entity.ID == ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self.entity.Game, "At the end of turn, corrupted card %s is discarded from hand."%self.entity.name)
		self.entity.Game.Hand_Deck.discardCard(self.entity.ID, self.entity)
		
		
"""Warrior cards"""
class BoomSquad(Spell):
	Class, name = "Warrior", "Boom Squad"
	requireTarget, mana = False, 1
	index = "Dragons~Warrior~Spell~1~Boom Squad"
	description = "Discover a Lackey, Mech, or a Dragon"
	poolIdentifier = "Mechs as Warrior"
	@classmethod
	def generatePool(cls, Game):
		classes_Mech = ["Mechs as %s"+Class for Class in Game.Classes]
		classCards = {s : [] for s in Game.ClassesandNeutral}
		for key, value in Game.MinionswithRace["Mech"].items():
			for Class in key.split('~')[1].split(','):
				classCards[Class].append(value)
		mechs = [classCards[Class]+classCards["Neutral"] for Class in Game.Classes]
		classes_Dragon = ["Dragons as %s"+Class for Class in Game.Classes]
		classCards = {s : [] for s in Game.ClassesandNeutral}
		for key, value in Game.MinionswithRace["Dragon"].items():
			for Class in key.split('~')[1].split(','):
				classCards[Class].append(value)
		dragons = [classCards[Class]+classCards["Neutral"] for Class in Game.Classes]
		return classes_Mech+classes_Dragon, mechs+dragons
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if curGame.mode == 0:
			if curGame.guides:
				PRINT(curGame, "Boom Squad is cast and adds a Lackey/Mech/Dragon to player's hand")
				curGame.Hand_Deck.addCardtoHand(curGame.guides.pop(0), self.ID, "type", byDiscover=True)
			else:
				Class = classforDiscover(self)
				key_Mech, key_Dragon = "Mechs as " + Class, "Dragons as " + Class
				if self.ID != curGame.turn or "byOthers" in comment:
					mixedPool = [Lackeys, curGame.RNGPools[key_Mech], curGame.RNGPools[key_Dragon]]
					card = npchoice(mixedPool[nprandint(3)])
					curGame.fixedGuides.append(card)
					PRINT(curGame, "Boom Squad is cast and adds a random Lackey, Mech, or Dragon card to player's hand")
					curGame.Hand_Deck.addCardtoHand(card, self.ID, "type", byDiscover=True)
				else:
					cards = [npchoice(Lackeys), npchoice(curGame.RNGPools[key_Mech]), npchoice(curGame.RNGPools[key_Dragon])]
					PRINT(curGame, "Boom Squad lets player Discover a Lackey, Mech or Dragon")
					curGame.options = [card(curGame, self.ID) for card in cards]
					curGame.Discover.startDiscover(self)
		return None
		
	def discoverDecided(self, option, info):
		self.Game.fixedGuides.append(type(option))
		self.Game.Hand_Deck.addCardtoHand(option, self.ID, byDiscover=True)
		
		
class RiskySkipper(Minion):
	Class, race, name = "Warrior", "Pirate", "Risky Skipper"
	mana, attack, health = 1, 1, 3
	index = "Dragons~Warrior~Minion~1~1~3~Pirate~Risky Skipper"
	requireTarget, keyWord, description = False, "", "After you play a minion, deal 1 damage to all minions"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_RiskySkipper(self)]
		
class Trig_RiskySkipper(TrigBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionBeenPlayed"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject.ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self.entity.Game, "After player plays minion, %s deals 1 damage to all minions"%self.entity.name)
		targets = self.entity.Game.minionsonBoard(1) + self.entity.Game.minionsonBoard(2)
		self.entity.dealsAOE(targets, [1 for minion in targets])
		
	
class BombWrangler(Minion):
	Class, race, name = "Warrior", "", "Bomb Wrangler"
	mana, attack, health = 3, 2, 3
	index = "Dragons~Warrior~Minion~3~2~3~None~Bomb Wrangler"
	requireTarget, keyWord, description = False, "", "Whenever this minion takes damage, summon a 1/1 Boom Bot"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_BombWrangler(self)]
		
class Trig_BombWrangler(TrigBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionTakesDmg"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and target == self.entity
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self.entity.Game, "Whenever %s takes damage, it summons a 1/1 Boom Bot"%self.entity.name)
		self.entity.Game.summon(BoomBot_Dragons(self.entity.Game, self.entity.ID), self.entity.position+1, self.entity.ID)
		
class BoomBot_Dragons(Minion):
	Class, race, name = "Neutral", "Mech", "Boom Bot"
	mana, attack, health = 1, 1, 1
	index = "Dragons~Neutral~Minion~1~1~1~Mech~Boom Bot~Deathrattle~Uncollectible"
	requireTarget, keyWord, description = False, "", "Deathrattle: Deal 1~4 damage to a random enemy"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [Deal1to4DamagetoaRandomEnemy(self)]
		
class Deal1to4DamagetoaRandomEnemy(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		curGame = self.entity.Game
		if curGame.mode == 0:
			enemy = None
			PRINT(curGame, "Deathrattle: Deal 1~4 damage to a random enemy triggers.")
			if curGame.guides:
				i, where, damage = curGame.guides.pop(0)
				if where: enemy = curGame.find(i, where)
			else:
				targets = curGame.charsAlive(3-self.entity.ID)
				if targets:
					enemy, damage = npchoice(targets), nprandint(1, 5)
					curGame.fixedGuides.append((enemy.position, "minion%d"%enemy.ID, damage) if enemy.type == "Minion" else (enemy.ID, "hero", damage))
				else:
					curGame.fixedGuides.append((0, '', 0))
			if enemy:
				self.entity.dealsDamage(enemy, damage)
				
				
Galakrond_Indices = {"Dragons~Neutral~Minion~3~2~2~None~Skydiving Instructor~Battlecry": SkydivingInstructor,
					"Dragons~Neutral~Minion~5~3~4~Elemental~Hailbringer~Battlecry": Hailbringer,
					"Dragons~Neutral~Minion~1~1~1~Elemental~Ice Shard~Uncollectible": IceShard,
					"Dragons~Neutral~Minion~2~3~2~None~Licensed Adventurer~Battlecry": LicensedAdventurer,
					"Dragons~Neutral~Minion~4~3~2~Demon~Frenzied Felwing": FrenziedFelwing,
					"Dragons~Neutral~Minion~4~3~5~Beast~Escaped Manasaber~Stealth": EscapedManasaber,
					"Dragons~Neutral~Minion~5~5~5~None~Boompistol Bully~Battlecry": BoompistolBully,
					"Dragons~Neutral~Minion~4~2~3~None~Grand Lackey Erkh~Legendary": GrandLackeyErkh,
					"Dragons~Neutral~Minion~4~2~3~Pirate~Sky Gen'ral Kragg~Battlecry~Legendary": SkyGenralKragg,
					"Dragons~Neutral~Minion~4~4~2~Beast~Sharkbait~Rush~Legendary~Uncollectible": Sharkbait,
					"Dragons~Druid~Spell~2~Rising Winds~Twinspell~Choose One": RisingWinds,
					"Dragons~Druid~Spell~2~Rising Winds~Choose One~Uncollectible": risingwinds,
					"Dragons~Druid~Spell~2~Take Flight~Uncollectible": TakeFlight,
					"Dragons~Druid~Spell~2~Swoop In~Uncollectible": SwoopIn,
					"Dragons~Druid~Minion~2~3~2~Beast~Eagle~Uncollectible": Eagle,
					"Dragons~Druid~Minion~2~2~3~Beast~Steel Beetle~Battlecry": SteelBeetle,
					"Dragons~Druid~Minion~7~6~8~Beast~Winged Guardian~Taunt~Reborn": WingedGuardian,
					"Dragons~Hunter~Spell~2~Fresh Scent~Twinspell": FreshScent,
					"Dragons~Hunter~Spell~2~Fresh Scent~Uncollectible": freshscent,
					"Dragons~Hunter~Minion~3~2~4~Mech~Chopshop Copter": ChopshopCopter,
					"Dragons~Hunter~Minion~5~6~5~Dragon~Rotnest Drake~Battlecry": RotnestDrake,
					"Dragons~Mage~Minion~3~2~5~Elemental~Arcane Amplifier": ArcaneAmplifier,
					"Dragons~Mage~Minion~7~7~6~Elemental~Animated Avalanche~Battlecry": AnimatedAvalanche,
					"Dragons~Mage~Hero Card~10~The Amazing Reno~Battlecry~Legendary": TheAmazingReno,
					"Dragons~Paladin~Minion~2~2~2~Mech~Shotbot~Reborn": Shotbot,
					"Dragons~Paladin~Spell~2~Air Raid~Twinspell": AirRaid,
					"Dragons~Paladin~Spell~2~Air Raid~Uncollectible": airraid,
					"Dragons~Paladin~Minion~1~1~1~None~Silver Hand Recruit~Taunt~Uncollectible": SilverHandRecruit_Dragons,
					"Dragons~Paladin~Minion~5~5~6~Dragon~Scalelord~Battlecry": Scalelord,
					"Dragons~Priest~Minion~6~4~4~Dragon~Aeon Reaver~Battlecry": AeonReaver,
					"Dragons~Priest~Minion~1~1~1~None~Cleric of Scales~Battlecry": ClericofScales,
					"Dragons~Priest~Spell~3~Dark Prophecy": DarkProphecy,
					"Dragons~Rogue~Minion~2~1~3~Pirate~Skyvateer~Stealth~Deathrattle": Skyvateer,
					"Dragons~Rogue~Spell~2~Waxmancy": Waxmancy,
					"Dragons~Rogue~Minion~5~3~2~None~Shadow Sculptor~Combo": ShadowSculptor,
					"Dragons~Shaman~Spell~2~Explosive Evolution": ExplosiveEvolution,
					"Dragons~Shaman~Spell~10~Eye of the Storm~Overload": EyeoftheStorm,
					"Dragons~Shaman~Minion~5~5~6~Elemental~Stormblocker~Taunt~Uncollectible": Stormblocker,
					"Dragons~Shaman~Weapon~4~1~4~The Fist of Ra-den~Legendary": TheFistofRaden,
					"Dragons~Warlock~Minion~1~2~1~Demon~Fiendish Servant~Deathrattle": FiendishServant,
					"Dragons~Warlock~Spell~2~Twisted Knowledge": TwistedKnowledge,
					"Dragons~Warlock~Minion~3~4~3~Demon~Chaos Gazer~Battlecry": ChaosGazer,
					"Dragons~Warrior~Spell~1~Boom Squad": BoomSquad,
					"Dragons~Warrior~Minion~1~1~3~Pirate~Risky Skipper": RiskySkipper,
					"Dragons~Warrior~Minion~3~2~3~None~Bomb Wrangler": BombWrangler,
					"Dragons~Neutral~Minion~1~1~1~Mech~Boom Bot~Deathrattle~Uncollectible": BoomBot_Dragons
					}
					