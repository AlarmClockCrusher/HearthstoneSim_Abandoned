from CardTypes import *
from Triggers_Auras import *
from VariousHandlers import *
from Basic import TheCoin
from Dragons import Lackeys

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
		
def classforDiscover(initiator):
	Class = initiator.Game.heroes[initiator.ID].Class
	if Class != "Neutral": #如果发现的发起者的职业不是中立，则返回那个职业
		return Class
	elif initiator.Class != "Neutral": #如果玩家职业是中立，但卡牌职业不是中立，则发现以那个卡牌的职业进行
		return initiator.Class
	else: #如果玩家职业和卡牌职业都是中立，则随机选取一个职业进行发现。
		return np.random.choice(Classes)
		
def fixedList(listObject):
	return listObject[0:len(listObject)]
	
Classes = ["Demon Hunter", "Druid", "Hunter", "Mage", "Paladin", "Priest", "Rogue", "Shaman", "Warlock", "Warrior"]
ClassesandNeutral = ["Demon Hunter", "Druid", "Hunter", "Mage", "Paladin", "Priest", "Rogue", "Shaman", "Warlock", "Warrior", "Neutral"]


class SkydivingInstructor(Minion):
	Class, race, name = "Neutral", "", "Skydiving Instructor"
	mana, attack, health = 3, 2, 2
	index = "Dragons~Neutral~Minion~3~2~2~None~Skydiving Instructor~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Summon a 1-Cost minion from your deck"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		PRINT(self, "Skydiving Instructor's battlecry summons a 1-Cost minion from player's deck")
		oneCostMinionsinDeck = []
		for card in self.Game.Hand_Deck.decks[self.ID]:
			if card.cardType == "Minion" and card.mana == 1:
				oneCostMinionsinDeck.append(card)
				
		if oneCostMinionsinDeck != [] and self.Game.spaceonBoard(self.ID) > 0:
			self.Game.summonfromDeck(np.random.choice(oneCostMinionsinDeck), self.position+1, self.ID)
		return None
		
		
class Hailbringer(Minion):
	Class, race, name = "Neutral", "Elemental", "Hailbringer"
	mana, attack, health = 5, 3, 4
	index = "Dragons~Neutral~Minion~5~3~4~Elemental~Hailbringer~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Summon two 1/1 Ice Shards that Freeze"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		PRINT(self, "Hailbringer's battlecry summons two 1/1 Ice Shards that Freeze")
		pos = (self.position, "leftandRight") if self.onBoard else (-1, "totheRightEnd")
		self.Game.summonMinion([IceShard(self.Game, self.ID) for i in range(2)], pos, self.ID)
		return None
		
class IceShard(Minion):
	Class, race, name = "Neutral", "Elemental", "Ice Shard"
	mana, attack, health = 1, 1, 1
	index = "Dragons~Neutral~Minion~1~1~1~Elemental~Ice Shard~Uncollectible"
	requireTarget, keyWord, description = False, "", "Freeze any character damaged by this minion"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_IceShard(self)]
		
class Trigger_IceShard(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionTakesDamage", "HeroTakesDamage"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return subject == self.entity
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self, "%s deals damage to %s and freezes it."%(self.entity.name, target.name))
		target.getsFrozen()
		
		
class LicensedAdventurer(Minion):
	Class, race, name = "Neutral", "", "Licensed Adventurer"
	mana, attack, health = 2, 3, 2
	index = "Dragons~Neutral~Minion~2~3~2~None~Licensed Adventurer~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: If you control a Quest, add a Coin to your hand"
	def effectCanTrigger(self):
		self.effectViable = self.Game.SecretHandler.mainQuests[self.ID] != [] or self.Game.SecretHandler.sideQuests[self.ID] != []
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if self.Game.SecretHandler.mainQuests[self.ID] != [] or self.Game.SecretHandler.sideQuests[self.ID] != []:
			PRINT(self, "Licensed Adventurer's battlecry adds a Coin to player's hand")
			self.Game.Hand_Deck.addCardtoHand(TheCoin, self.ID, "CreateUsingType")
		return None
		
class FrenziedFelwing(Minion):
	Class, race, name = "Neutral", "Demon", "Frenzied Felwing"
	mana, attack, health = 4, 3, 3
	index = "Dragons~Neutral~Minion~4~3~3~Demon~Frenzied Felwing"
	requireTarget, keyWord, description = False, "", "Costs (1) less for each damage dealt to your opponent this turn"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersinHand = [Trigger_FrenziedFelwing(self)]
		
	def selfManaChange(self):
		if self.inHand:
			manaReduction = self.Game.CounterHandler.damageonHeroThisTurn[3-self.ID]
			PRINT(self, "Frenzied Felwig reduces its own cost by (%d)"%manaReduction)
			self.mana -= manaReduction
			self.mana = max(0, self.mana)
			
class Trigger_FrenziedFelwing(TriggerinHand):
	def __init__(self, entity):
		self.blank_init(entity, ["HeroTakesDamage"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.inHand and target == self.entity.Game.heroes[3-self.entity.ID]
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.Game.ManaHandler.calcMana_Single(self.entity)
		
		
class EscapedManasaber(Minion):
	Class, race, name = "Neutral", "Beast", "Escaped Manasaber"
	mana, attack, health = 4, 3, 5
	index = "Dragons~Neutral~Minion~4~3~5~Beast~Escaped Manasaber~Stealth"
	requireTarget, keyWord, description = False, "Stealth", "Stealth. Whenever this attacks, gain 1 Mana Crystal this turn only"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_EscapedManasaber(self)]
		
class Trigger_EscapedManasaber(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionAttackingMinion", "MinionAttackingHero"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return subject == self.entity and self.entity.onBoard
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self, "Whenever it attacks, %s gives player a Mana Crystal for this turn only."%self.entity.name)
		if self.entity.Game.ManaHandler.manas[self.entity.ID] < 10:
			self.entity.Game.ManaHandler.manas[self.entity.ID] += 1
			
			
class BoompistolBully(Minion):
	Class, race, name = "Neutral", "", "Boompistol Bully"
	mana, attack, health = 5, 5, 5
	index = "Dragons~Neutral~Minion~5~5~5~None~Boompistol Bully~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Enemy Battlecry cards cost (5) more next turn"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		PRINT(self, "Boompistol Bully's battlecry makes enemy Battlecry cards cost (5) more next turn.")
		self.Game.ManaHandler.CardAuras_Backup.append(BattlecryCardsCost5MoreNextTurn(self.Game, 3-self.ID))
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
		
	#持续整个回合的光环可以不必注册"ManaCostPaid"
	def auraAppears(self):
		for card in self.Game.Hand_Deck.hands[1] + self.Game.Hand_Deck.hands[2]:
			self.applies(card)
		self.Game.triggersonBoard[self.ID].append((self, "CardEntersHand"))
		self.Game.ManaHandler.calcMana_All()
	#auraDisappears()可以尝试移除ManaCostPaid，当然没有反应，所以不必专门定义
	
	
class GrandLackeyErkh(Minion):
	Class, race, name = "Neutral", "", "Grand Lackey Erkh"
	mana, attack, health = 4, 2, 3
	index = "Dragons~Neutral~Minion~4~2~3~None~Grand Lackey Erkh~Legendary"
	requireTarget, keyWord, description = False, "", "After you play a Lackey, add a Lackey to your hand"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_GrandLackeyErkh(self)]
		
class Trigger_GrandLackeyErkh(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionBeenPlayed"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject.ID == self.entity.ID and subject.name.endswith(" Lackey")
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self, "After player plays a Lackey, %s adds a Lackey to player's hand"%self.entity.name)
		self.entity.Game.Hand_Deck.addCardtoHand(np.random.choice(Lackeys), self.entity.ID, "CreateUsingType")
		
		
class SkyGenralKragg(Minion):
	Class, race, name = "Neutral", "Pirate", "Sky Gen'ral Kragg"
	mana, attack, health = 4, 2, 3
	index = "Dragons~Neutral~Minion~4~2~3~Pirate~Sky Gen'ral Kragg~Battlecry~Legendary"
	requireTarget, keyWord, description = False, "Taunt", "Taunt. Battlecry: If you've played a Quest this game, summon a 4/2 Parrot with Rush"
	def effectCanTrigger(self):
		self.effectViable = self.Game.CounterHandler.hasPlayedQuestThisGame[self.ID]
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if self.Game.CounterHandler.hasPlayedQuestThisGame[self.ID]:
			PRINT(self, "Sky Gen'ral Kragg's battlecry summons a 4/2 Parrot with Rush")
			self.Game.summonMinion(Sharkbait(self.Game, self.ID), self.position+1, self.ID)
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
	index = "Dragons~Druid~Spell~2~Rising Winds~Choose One~Twinspell"
	description = "Twinspell. Choose One- Draw a card; or Summon a 3/2 Eagle"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.twinSpell = 1
		self.twinSpellCopy = risingwinds
		self.chooseOne = 1
		self.options = [TakeFlight_Option(), SwoopIn_Option(self)]
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if choice == "ChooseBoth" or choice == 0:
			PRINT(self, "Rising Winds lets player draw a card")
			self.Game.Hand_Deck.drawCard(self.ID)
		if choice == "ChooseBoth" or choice == 1:
			PRINT(self, "Rising Winds summons a 3/2 Eagle")
			self.Game.summonMinion(Eagle(self.Game, self.ID), -1, self.ID)
		return None
		
class risingwinds(Spell):
	Class, name = "Druid", "Rising Winds"
	requireTarget, mana = False, 2
	index = "Dragons~Druid~Spell~2~Rising Winds~Choose One~Uncollectible"
	description = "Choose One- Draw a card; or Summon a 3/2 Eagle"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.chooseOne = 1
		self.options = [TakeFlight_Option(), SwoopIn_Option(self)]
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if choice == "ChooseBoth" or choice == 0:
			PRINT(self, "Rising Winds lets player draw a card")
			self.Game.Hand_Deck.drawCard(self.ID)
		if choice == "ChooseBoth" or choice == 1:
			PRINT(self, "Rising Winds summons a 3/2 Eagle")
			self.Game.summonMinion(Eagle(self.Game, self.ID), -1, self.ID)
		return None
		
class TakeFlight_Option:
	def __init__(self):
		self.name = "Take Flight"
		self.description = "Draw a card"
		self.index = "Dragons~Druid~Spell~2~Take Flight~Uncollectible"
		
	def available(self):
		return True
		
	def selfCopy(self, recipient):
		return type(self)()
		
class SwoopIn_Option:
	def __init__(self, spell):
		self.spell = spell
		self.name = "Swoop In"
		self.description = "Summon 3/2"
		self.index = "Dragons~Druid~Spell~2~Swoop In~Uncollectible"
		
	def available(self):
		return self.spell.Game.spaceonBoard(self.spell.ID) > 0
		
	def selfCopy(self, recipient):
		return type(self)(recipient)
		
class TakeFlight(Spell):
	Class, name = "Druid", "Take Flight"
	requireTarget, mana = False, 2
	index = "Dragons~Druid~Spell~2~Take Flight~Uncollectible"
	description = "Draw a card"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		PRINT(self, "Take Flight is cast and lets player draw a card")
		self.Game.Hand_Deck.drawCard(self.ID)
		return None
		
class SwoopIn(Spell):
	Class, name = "Druid", "Swoop In"
	requireTarget, mana = False, 2
	index = "Dragons~Druid~Spell~2~Swoop In~Uncollectible"
	description = "Summon a 3/2 Eagle"
	def available(self):
		return self.Game.spaceonBoard(self.ID) > 0
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		PRINT(self, "Swoop In is cast and summons a 3/2 Eagle")
		self.Game.summonMinion(Eagle(self.Game, self.ID), -1, self.ID)
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
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if self.Game.Hand_Deck.holdingSpellwith5CostorMore(self.ID):
			PRINT(self, "Steel Beatle's battlecry lets player gain 5 Armor")
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
		return target.cardType == "Minion" and "Beast" in target.race and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if target != None:
			PRINT(self, "Fresh Scent is cast and gives Beast %s +2/+2"%target.name)
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
		return target.cardType == "Minion" and "Beast" in target.race and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if target != None:
			PRINT(self, "Fresh Scent is cast and gives Beast %s +2/+2"%target.name)
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
		self.triggersonBoard = [Trigger_ChopshopCopter(self)]
		
class Trigger_ChopshopCopter(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionDied"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and target.ID == self.entity.ID and "Mech" in target.race
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self, "After a friendly minion died, %s adds a random Mech to player's hand"%self.entity.name)
		self.entity.Game.Hand_Deck.addCardtoHand(np.random.choice(self.entity.Game.RNGPools["Mechs"]), self.entity.ID, "CreateUsingType")
		
		
class RotnestDrake(Minion):
	Class, race, name = "Hunter", "Dragon", "Rotnest Drake"
	mana, attack, health = 5, 6, 5
	index = "Dragons~Hunter~Minion~5~6~5~Dragon~Rotnest Drake~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: If you're holding a Dragon, destroy a random enemy minion"
	def effectCanTrigger(self):
		self.effectViable = self.Game.Hand_Deck.holdingDragon(self.ID, self)
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if self.Game.Hand_Deck.holdingDragon(self.ID):
			PRINT(self, "Rotnest Drake's battlecry destroys a random enemy minion")
			targets = []
			for minion in self.Game.minionsonBoard(3-self.ID):
				if minion.dead == False:
					targets.append(minion)
			if targets != []:
				minion = np.random.choice(targets)
				PRINT(self, "Rotnest Drake's battlecry destroys random enemy minion %s"%minion.name)
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
		PRINT(self, "Arcane Amplifier's aura is registered. Player %d's Hero Power now deals 2 extra damage, if applicable."%self.ID)
		self.Game.playerStatus[self.ID]["Hero Power Damage Boost"] += 2
		
	def deactivateAura(self):
		PRINT(self, "Arcane Amplifier's aura is removed. Player %d's Hero Power no longer deals 2 extra damage."%self.ID)
		self.Game.playerStatus[self.ID]["Hero Power Damage Boost"] -= 2
		
		
class AnimatedAvalanche(Minion):
	Class, race, name = "Mage", "Elemental", "Animated Avalanche"
	mana, attack, health = 7, 7, 6
	index = "Dragons~Mage~Minion~7~7~6~Elemental~Animated Avalanche~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: If you played an Elemental last turn, summon a copy of this"
	def effectCanTrigger(self):
		self.effectViable = self.Game.CounterHandler.numElementalsPlayedLastTurn[self.ID] > 0
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if self.Game.CounterHandler.numElementalsPlayedLastTurn[self.ID] > 0:
			PRINT(self, "Animated Avalanche's battlecry summons a copy of the minion.")
			self.Game.summonMinion(self.selfCopy(self.ID), self.position+1, self.ID)
		return None
		
		
class WhatDoesThisDo(HeroPower):
	mana, name, requireTarget = 0, "What Does This Do?", False
	index = "Mage~Hero Power~0~What Does This Do?"
	description = "Passive Hero Power. At the start of your turn, cast a random spell"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_WhatDoesThisDo(self)]
		
	def available(self, choice=0):
		return False
		
	def use(self, target=None, choice=0):
		return 0
		
	def appears(self):
		for trigger in self.triggersonBoard:
			trigger.connect() #把(obj, signal)放入Game.triggersonBoard 中
		self.Game.sendSignal("HeroPowerAcquired", self.ID, self, None, 0, "")
		
	def disappears(self):
		for trigger in self.triggersonBoard:
			trigger.disconnect()
			
class Trigger_WhatDoesThisDo(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["TurnStarts"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self, "At the start of turn, Hero Power What Does This Do? casts a random spell")
		spell = np.random.choice(self.entity.Game.RNGPools["Spells"])(self.entity.Game, self.entity.ID)
		spell.cast()
		
class TheAmazingReno(Hero):
	mana, description = 10, "Battlecry: Make all minions disappear. *Poof!*"
	Class, name, heroPower, armor = "Mage", "The Amazing Reno", WhatDoesThisDo, 5
	index = "Dragons~Mage~Hero Card~10~The Amazing Reno~Battlecry~Legendary"
	poolIdentifier = "Spells"
	@classmethod
	def generatePool(cls, Game):
		spells = []
		for Class in Classes:
			for key, value in Game.ClassCards[Class].items():
				if "~Spell~" in key:
					spells.append(value)
		return "Spells", spells
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		PRINT(self, "The Amazing Reno's battlecry makes all minions disappear.")
		minionstoRemove = []
		for minion in fixedList(self.Game.minionsonBoard(1) + self.Game.minionsonBoard(2)):
			minion.disappears(keepDeathrattlesRegistered=False)
			minionstoRemove.append(minion)
			
		for minion in minionstoRemove:
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
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		PRINT(self, "Air Raid is cast and summons two 1/1 Silve Hand Recruits")
		self.Game.summonMinion([SilverHandRecruit_Dragons(self.Game, self.ID) for i in range(2)], (-1, "totheRightEnd"), self.ID)
		return None
		
class airraid(Spell):
	Class, name = "Paladin", "Air Raid"
	requireTarget, mana = False, 2
	index = "Dragons~Paladin~Spell~2~Air Raid~Uncollectible"
	description = "Summon two 1/1 Silver Hand Recruits with Taunt"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		PRINT(self, "Air Raid is cast and summons two 1/1 Silve Hand Recruits")
		self.Game.summonMinion([SilverHandRecruit_Dragons(self.Game, self.ID) for i in range(2)], (-1, "totheRightEnd"), self.ID)
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
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		PRINT(self, "Scalelord's battlecry gives all Friendly Murlocs Divine Shield")
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
		return target.cardType == "Minion" and target != self and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if target != None:
			PRINT(self, "Aeon Reaver's battlecry deals damage to minion %s equal to its own Attack"%target.name)
			self.dealsDamage(target, target.attack)
		return target
		
		
class ClericofScales(Minion):
	Class, race, name = "Priest", "", "Cleric of Scales"
	mana, attack, health = 1, 1, 1
	index = "Dragons~Priest~Minion~1~1~1~None~Cleric of Scales~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: If you're holding a Dragon, Discover a spell from your deck"
	
	def effectCanTrigger(self):
		self.effectViable = self.Game.Hand_Deck.holdingDragon(self.ID)
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if self.Game.Hand_Deck.holdingDragon(self.ID) and self.ID == self.Game.turn:
			spellsinDeck, typesinDeck = [], []
			for card in self.Game.Hand_Deck.decks[self.ID]:
				if card.cardType == "Spell" and type(card) not in typesinDeck:
					spellsinDeck.append(card)
					typesinDeck.append(type(card))
					
			if spellsinDeck != []:
				if "InvokedbyOthers" in comment:
					PRINT(self, "Cleric of Scales' battlecry lets player draw a random spell from deck")
					self.Game.Hand_Deck.drawCard(self.ID, np.random.choice(spellsinDeck))
				else:
					if len(spellsinDeck) == 1:
						PRINT(self, "Cleric of Scales draws the only spell in player's deck")
						self.Game.Hand_Deck.drawCard(self.ID, spellsinDeck[0])
					else:
						spells = np.random.choice(spellsinDeck, min(3, len(spellsinDeck)), replace=False)
						PRINT(self, "Cleric of Scales' battlecry lets player Discover a spell from their deck")
						self.Game.options = list(spells)
						self.Game.DiscoverHandler.startDiscover(self)
						
		return None
		
	def discoverDecided(self, option):
		PRINT(self, "Spell %s is drawn."%option.name)
		self.Game.Hand_Deck.drawCard(self.ID, option)
		
		
class DarkProphecy(Spell):
	Class, name = "Priest", "Dark Prophecy"
	requireTarget, mana = False, 3
	index = "Dragons~Priest~Spell~3~Dark Prophecy"
	description = "Discover a 2-Cost minion. Summon it and give it +3 Health"
	poolIdentifier = "2-Cost Minions as Priest"
	@classmethod
	def generatePool(cls, Game):
		classes, lists, neutralCards = [], [], []
		classCards = {"Neutral": [], "Demon Hunter":[], "Druid":[], "Mage":[], "Hunter":[], "Paladin":[],
						"Priest":[], "Rogue":[], "Shaman":[], "Warlock":[], "Warrior":[]}
		for key, value in Game.MinionsofCost[2].items():
			classCards[key.split('~')[1]].append(value)
			
		for Class in Classes:
			classes.append("2-Cost Minions as "+Class)
			lists.append(classCards[Class]+classCards["Neutral"])
		return classes, lists #返回的包含“Class Cards except Hunter”等identifier的列表和其他职业卡表
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if self.Game.spaceonBoard(self.ID) > 0:
			key = "2-Cost Minions as " + classforDiscover(self)
			if "CastbyOthers" in comment:
				PRINT(self, "Dark Prophecy is cast and summons a random 2-Cost minion and gives it +3 Health")
				minion = np.random.choice(self.Game.RNGPools[key])(self.Game, self.ID)
				minion.buffDebuff(0, 3)
				self.Game.summonMinion(minion, -1, self.ID)
			else:
				minions = np.random.choice(self.Game.RNGPools[key], 3, replace=False)
				PRINT(self, "Dark Prophecy lets player Discover a 2-Cost minion to summon and gain +3 Health")
				self.Game.options = [minion(self.Game, self.ID) for minion in minions]
				self.Game.DiscoverHandler.startDiscover(self)
				
		return None
		
	def discoverDecided(self, option):
		PRINT(self, "Minion %s to summon and give +3 Health is chosen."%option.name)
		option.buffDebuff(0, 3)
		self.Game.summonMinion(option, -1, self.ID)
		
		
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
		PRINT(self, "Deathrattle: Draw a card triggers.")
		self.entity.Game.Hand_Deck.drawCard(self.entity.ID)
		
		
class Waxmancy(Spell):
	Class, name = "Rogue", "Waxmancy"
	requireTarget, mana = False, 2
	index = "Dragons~Rogue~Spell~2~Waxmancy"
	description = "Discover a Battlecry minion. Reduce its Cost by (2)"
	poolIdentifier = "Battlecry Minions as Rogue"
	@classmethod
	def generatePool(cls, Game):
		classes, lists, neutralMinions = [], [], []
		#确定中立的战吼随从列表
		for key, value in Game.NeutralMinions.items():
			if "~Minion~" in key and "~Battlecry~" in key:
				neutralMinions.append(value)
		#职业为中立时，视为作为萨满打出此牌
		for Class in Classes:
			classes.append("Battlecry Minions as " + Class)
			battlecryMinionsinClass = []
			for key, value in Game.ClassCards[Class].items():
				if "~Minion~" in key and "~Battlecry~" in key:
					battlecryMinionsinClass.append(value)
			#包含职业牌中的战吼随从和中立战吼随从
			lists.append(battlecryMinionsinClass+neutralMinions)
		return classes, lists
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if self.Game.Hand_Deck.handNotFull(self.ID):
			key = "Battlecry Minions as " + classforDiscover(self)
			if "CastbyOthers" in comment:
				PRINT(self, "Waxmancy is cast and adds a random Battlecry minion to player's hand. It costs (2) less")
				minion = np.random.choice(self.Game.RNGPools[key])(self.Game, self.ID)
				ManaModification(minion, changeby=-2, changeto=-1).applies()
				self.Game.Hand_Deck.addCardtoHand(minion, self.ID)
			else:
				minions = np.random.choice(self.Game.RNGPools[key], 3, replace=False)
				PRINT(self, "Waxmancy lets player Discover a Battlecry minion. It costs (2) less")
				self.Game.options = [minion(self.Game, self.ID) for minion in minions]
				self.Game.DiscoverHandler.startDiscover(self)
			
		return None
		
	def discoverDecided(self, option):
		PRINT(self, "Battlecry minion %s is added to hand and costs (2) less."%option.name)
		ManaModification(option, changeby=-2, changeto=-1).applies()
		self.Game.Hand_Deck.addCardtoHand(option, self.ID)
		self.Game.sendSignal("DiscoveredCardPutintoHand", self.ID, self, option, 0, "")
		
		
class ShadowSculptor(Minion):
	Class, race, name = "Rogue", "", "Shadow Sculptor"
	mana, attack, health = 5, 3, 2
	index = "Dragons~Rogue~Minion~5~3~2~None~Shadow Sculptor~Combo"
	requireTarget, keyWord, description = False, "", "Combo: Draw a card for each card you've played this turn"
	def effectCanTrigger(self):
		self.effectViable = self.Game.CounterHandler.numCardsPlayedThisTurn[self.ID] > 0
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if self.Game.CounterHandler.numCardsPlayedThisTurn[self.ID] > 0:
			numCardsPlayed = len(self.Game.CounterHandler.cardsPlayedThisTurn[self.ID]["Indices"])
			PRINT(self, "Shadow Sculptor's Combo triggers and lets player draw a card for each card they've played this turn")
			for i in range(numCardsPlayed):
				self.Game.Hand_Deck.drawCard(self.ID)
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
		costs, lists = [], []
		for cost in Game.MinionsofCost.keys():
			costs.append("%d-Cost Minions to Summon"%cost)
			lists.append(list(Game.MinionsofCost[cost].values()))
		return costs, lists
		
	def available(self):
		return self.selectableFriendlyMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.ID == self.ID and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if target != None:
			PRINT(self, "Explosive Evolution is cast and transforms friendly minion %s to one that costs (3) more."%target.name)
			target = self.Game.mutate(target, 3)
		return target
		
		
class EyeoftheStorm(Spell):
	Class, name = "Shaman", "Eye of the Storm"
	requireTarget, mana = False, 10
	index = "Dragons~Shaman~Spell~10~Eye of the Storm~Overload"
	description = "Summon three 5/6 Elementals with Taunt. Overload: (3)"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.overload = 3
		
	def available(self):
		return self.Game.spaceonBoard(self.ID) > 0
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		PRINT(self, "Eye of the Storm is cast and summons three 5/6 Elementals with Taunt.")
		self.Game.summonMinion([Stormblocker(self.Game, self.ID) for i in range(3)], (-1, "totheRightEnd"), self.ID)
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
		minions, costs = {}, []
		for key, value in Game.LegendaryMinions.items():
			cost = key.split('~')[3]
			if cost not in costs:
				minions[cost+"-Cost Legendary Minions to Summon"] = [value]
				costs.append(cost)
			else:
				minions[cost+"-Cost Legendary Minions to Summon"].append(value)
				
		return list(minions.keys()), list(minions.values())
		
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_TheFistofRaden(self)]
		
class Trigger_TheFistofRaden(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["SpellBeenPlayed"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return subject.ID == self.entity.ID and self.entity.onBoard and self.entity.durability > 0
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		if "%d-Cost Legendary Minions to Summon"%number in self.entity.Game.RNGPools.keys():
			PRINT(self, "After player casts a spell %s, %s summons a random Legendary minion with that Cost and loses 1 Durability."%(subject.name, self.entity.name))
			minion = np.random.choice(self.entity.Game.RNGPools["%d-Cost Legendary Minions to Summon"%number])
			self.entity.Game.summonMinion(minion(self.entity.Game, self.entity.ID), -1, self.entity.ID)
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
		PRINT(self, "Deathrattle: Give this minion's Attack %d to a random friendly minion triggers."%number)
		targets = self.entity.Game.minionsonBoard(self.entity.ID)
		if targets != []:
			target = np.random.choice(targets)
			PRINT(self, "%s gets the Attack given by %s"%(target.name, self.entity.Game))
			target.buffDebuff(number, 0)
		
			
class TwistedKnowledge(Spell):
	Class, name = "Warlock", "Twisted Knowledge"
	requireTarget, mana = False, 2
	index = "Dragons~Warlock~Spell~2~Twisted Knowledge"
	description = "Discover 2 Warlock cards"
	poolIdentifier = "Warlock Cards"
	@classmethod
	def generatePool(cls, Game):
		return "Warlock", list(Game.ClassCards["Warlock"].values())
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		for i in range(2):
			if self.Game.Hand_Deck.handNotFull(self.ID):
				if "CastbyOthers" in comment:
					PRINT(self, "Twisted Knowledge is cast and adds a random Warlock card to player's hand")
					self.Game.Hand_Deck.addCardtoHand(np.random.choice(self.Game.RNGPools["Warlock Cards"]), self.ID, "CreateUsingType")
				else:
					cards = np.random.choice(self.Game.RNGPools["Warlock Cards"], 3, replace=False)
					PRINT(self, "Twisted Knowledge lets player Discover a Warlock card")
					self.Game.options = [card(self.Game, self.ID) for card in cards]
					self.Game.DiscoverHandler.startDiscover(self)
			
		return None
		
	def discoverDecided(self, option):
		PRINT(self, "Warlock card %s is put into player's hand."%option.name)
		self.Game.Hand_Deck.addCardtoHand(option, self.ID)
		self.Game.sendSignal("DiscoveredCardPutintoHand", self.ID, self, option, 0, "")
		
#只会考虑当前的费用，寻找下回合法力值以下的牌。延时生效的法力值效果不会被考虑。
#如果被战吼触发前被对方控制了，则也会根据我方下个回合的水晶进行腐化。但是这个回合结束时就会丢弃（因为也算是一个回合。）
#https://www.bilibili.com/video/av92443139?from=search&seid=7929483619040209451
class ChaosGazer(Minion):
	Class, race, name = "Warlock", "Demon", "Chaos Gazer"
	mana, attack, health = 3, 4, 3
	index = "Dragons~Warlock~Minion~3~4~3~Demon~Chaos Gazer~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Corrupt a playable card in your opponent's hand. They have 1 turn to play it!"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		PRINT(self, "Chaos Gazer's battlecry corrupts a playable card in opponent's hand")
		ID, manaNextTurn = 3-self.ID, self.Game.ManaHandler.manasUpper[3-self.ID]
		manaNextTurn += 1
		manaNextTurn = min(10, manaNextTurn)
		manaNextTurn = max(0, manaNextTurn - self.Game.ManaHandler.manasOverloaded[ID])
		playableCards = []
		for card in self.Game.Hand_Deck.hands[ID]:
			if card.mana <= manaNextTurn:
				notCorrupted = True
				for trigger in card.triggersinHand:
					if type(trigger) == Trigger_CorruptedHand:
						notCorrupted = False
						break
				if notCorrupted:
					playableCards.append(card)
				
		if playableCards != []:
			card = np.random.choice(playableCards)
			PRINT(self, "Card %s in opponent's hand is corrupted."%card.name)
			trigger = Trigger_CorruptedHand(card)
			card.triggersinHand.append(trigger)
			trigger.connect()
		return None
		
class Trigger_CorruptedHand(TriggerinHand):
	def __init__(self, entity):
		self.blank_init(entity, ["TurnEnds"])
		self.temp = True
		self.makesCardEvanescent = True
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		#被腐蚀的卡只会在其拥有者的回合结束时才会被丢弃
		return self.entity.inHand and self.entity.ID == ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self, "At the end of turn, corrupted card %s is discarded from hand."%self.entity.name)
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
		classes_Mech, classes_Dragons, mechs, dragons = [], [], [], []
		classCards = {"Neutral": [], "Demon Hunter":[], "Druid":[], "Mage":[], "Hunter":[], "Paladin":[],
						"Priest":[], "Rogue":[], "Shaman":[], "Warlock":[], "Warrior":[]}
		for key, value in Game.MinionswithRace["Mech"].items():
			classCards[key.split('~')[1]].append(value)
			
		for Class in Classes:
			classes_Mech.append("Mechs as "+Class)
			mechs.append(classCards[Class]+classCards["Neutral"])
			
		classCards = {"Neutral": [], "Demon Hunter":[], "Druid":[], "Mage":[], "Hunter":[], "Paladin":[],
						"Priest":[], "Rogue":[], "Shaman":[], "Warlock":[], "Warrior":[]}
		for key, value in Game.MinionswithRace["Dragon"].items():
			classCards[key.split('~')[1]].append(value)
			
		for Class in Classes:
			classes_Dragons.append("Dragons as "+Class)
			dragons.append(classCards[Class]+classCards["Neutral"])
		return classes_Mech+classes_Dragons, mechs+dragons
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if self.Game.Hand_Deck.handNotFull(self.ID):
			key_Mech = "Mechs as " + classforDiscover(self)
			key_Dragon = "Dragons as " + classforDiscover(self)
			if "CastbyOthers" in comment:
				mixedPool = [Lackeys, self.Game.RNGPools[key_Mech], self.Game.RNGPools[key_Dragon]]
				PRINT(self, "Boom Squad is cast and adds a random Lackey, Mech, or Dragon card to player's hand")
				self.Game.Hand_Deck.addCardtoHand(np.random.choice(mixedPool[np.random.randint(3)]), self.ID, "CreateUsingType")
			else:
				cards = [np.random.choice(Lackeys), np.random.choice(self.Game.RNGPools[key_Mech]), np.random.choice(self.Game.RNGPools[key_Dragon])]
				PRINT(self, "Boom Squad lets player Discover a Lackey, Mech or Dragon")
				self.Game.options = [card(self.Game, self.ID) for card in cards]
				self.Game.DiscoverHandler.startDiscover(self)
				
		return None
		
	def discoverDecided(self, option):
		PRINT(self, "Card %s is put into player's hand."%option.name)
		self.Game.Hand_Deck.addCardtoHand(option, self.ID)
		self.Game.sendSignal("DiscoveredCardPutintoHand", self.ID, self, option, 0, "")
		
		
class RiskySkipper(Minion):
	Class, race, name = "Warrior", "Pirate", "Risky Skipper"
	mana, attack, health = 1, 1, 3
	index = "Dragons~Warrior~Minion~1~1~3~Pirate~Risky Skipper"
	requireTarget, keyWord, description = False, "", "After you play a minion, deal 1 damage to all minions"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_RiskySkipper(self)]
		
class Trigger_RiskySkipper(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionBeenPlayed"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject.ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self, "After player plays minion, %s deals 1 damage to all minions"%self.entity.name)
		targets = self.entity.Game.minionsonBoard(1) + self.entity.Game.minionsonBoard(2)
		self.entity.dealsAOE(targets, [1 for minion in targets])
		
	
class BombWrangler(Minion):
	Class, race, name = "Warrior", "", "Bomb Wrangler"
	mana, attack, health = 3, 2, 3
	index = "Dragons~Warrior~Minion~3~2~3~None~Bomb Wrangler"
	requireTarget, keyWord, description = False, "", "Whenever this minion takes damage, summon a 1/1 Boom Bot"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_BombWrangler(self)]
		
class Trigger_BombWrangler(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionTakesDamage"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and target == self.entity
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self, "Whenever %s takes damage, it summons a 1/1 Boom Bot"%self.entity.name)
		self.entity.Game.summonMinion(BoomBot_Dragons(self.entity.Game, self.entity.ID), self.entity.position+1, self.entity.ID)
		
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
		PRINT(self, "Deathrattle: Deal 1~4 damage to a random enemy triggers.")
		targets = self.entity.Game.livingObjtoTakeRandomDamage(3-self.entity.ID)
		if targets != []:
			target, damage = np.random.choice(targets), np.random.randint(1, 5)
			PRINT(self, "%s deals %d damage to %s"%(self.entity.name, damage, target))
			self.entity.dealsDamage(target, damage)