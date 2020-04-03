from CardTypes import *
from Triggers_Auras import *
from VariousHandlers import *

from Basic import TheCoin, MurlocScout
from Classic import PatientAssassin

import numpy as np
import copy

def extractfrom(target, listObject):
	temp = None
	for i in range(len(listObject)):
		if listObject[i] == target:
			temp = listObject.pop(i)
			break
	return temp
	
def fixedList(listObject):
	return listObject[0:len(listObject)]
	
def classforDiscover(initiator):
	Class = initiator.Game.heroes[initiator.ID].Class
	if Class != "Neutral": #如果发现的发起者的职业不是中立，则返回那个职业
		return Class
	elif initiator.Class != "Neutral": #如果玩家职业是中立，但卡牌职业不是中立，则发现以那个卡牌的职业进行
		return initiator.Class
	else: #如果玩家职业和卡牌职业都是中立，则随机选取一个职业进行发现。
		return np.random.choice(Classes)
		
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
		
		
Classes = ["Demon Hunter", "Druid", "Hunter", "Mage", "Paladin", "Priest", "Rogue", "Shaman", "Warlock", "Warrior"]
ClassesandNeutral = ["Demon Hunter", "Druid", "Hunter", "Mage", "Paladin", "Priest", "Rogue", "Shaman", "Warlock", "Warrior", "Neutral"]

"""Mana 1 cards"""
class PotionVendor(Minion):
	Class, race, name = "Neutral", "", "Potion Vendor"
	mana, attack, health = 1, 1, 1
	index = "Shadows~Neutral~Minion~1~1~1~None~Potion Vendor~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Restore 2 Health to all friendly characters"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		heal = 2 * (2 ** self.countHealDouble())
		targets = [self.Game.heroes[self.ID]] + self.Game.minions[self.ID]
		heals = [heal for i in range(len(targets))]
		PRINT(self, "Potion Vendor's battlecry restores %d health to all friendly characters"%heal)
		self.restoresAOE(targets, heals)
		return None
		
		
class Toxfin(Minion):
	Class, race, name = "Neutral", "Murloc", "Toxfin"
	mana, attack, health = 1, 1, 2
	index = "Shadows~Neutral~Minion~1~1~2~Murloc~Toxfin~Battlecry"
	requireTarget, keyWord, description = True, "", "Battlecry: Give a friendly Murloc Poisonous"
	
	def targetExists(self, choice=0):
		return self.selectableFriendlyMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and "Murloc" in target.race and target.ID == self.ID and target != self and target.onBoard
		
	def effectCanTrigger(self):
		self.effectViable = False
		for minion in self.Game.minionsonBoard(self.ID):
			if "Murloc" in minion.race:
				self.effectViable = True
				break
				
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if target != None:
			PRINT(self, "Toxfin's battlecry gives friendly Murloc %s Poisonous."%target.name)
			target.getsKeyword("Poisonous")
		return target
		
		
class DraconicLackey(Minion):
	Class, race, name = "Neutral", "", "Draconic Lackey"
	mana, attack, health = 1, 1, 1
	index = "Dragons~Neutral~Minion~1~1~1~None~Draconic Lackey~Battlecry~Uncollectible"
	requireTarget, keyWord, description = False, "", "Battlecry: Discover a Dragon"
	poolIdentifier = "Dragons as Druid"
	@classmethod
	def generatePool(cls, Game):
		classes, lists, neutralCards = [], [], []
		classCards = {"Neutral": [], "Demon Hunter":[], "Druid":[], "Mage":[], "Hunter":[], "Paladin":[],
						"Priest":[], "Rogue":[], "Shaman":[], "Warlock":[], "Warrior":[]}
		for key, value in Game.MinionswithRace["Dragon"].items():
			classCards[key.split('~')[1]].append(value)
			
		for Class in Classes:
			classes.append("Dragons as "+Class)
			lists.append(classCards[Class]+classCards["Neutral"])
		return classes, lists #返回的包含“Class Cards except Hunter”等identifier的列表和其他职业卡表
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if self.Game.Hand_Deck.handNotFull(self.ID) and self.ID == self.Game.turn:
			key = "Dragons as "+classforDiscover(self)
			if "InvokedbyOthers" in comment:
				PRINT(self, "Draconic Lackey's battlecry adds a random Dragon to player's hand")
				self.Game.Hand_Deck.addCardtoHand(np.random.choice(self.Game.RNGPools[key]), self.ID, "CreateUsingType")
			else:
				dragons = np.random.choice(self.Game.RNGPools[key], 3, replace=False)
				self.Game.options = [dragon(self.Game, self.ID) for dragon in dragons]
				PRINT(self, "Draconic Lackey's battlecry lets player discover a Dragon")
				self.Game.DiscoverHandler.startDiscover(self)
				
		return None
		
	def discoverDecided(self, option):
		PRINT(self, "Dragon %s is put into player's hand."%option.name)
		self.Game.Hand_Deck.addCardtoHand(option, self.ID)
		self.Game.sendSignal("DiscoveredCardPutintoHand", self.ID, self, option, 0, "")
		
class EtherealLackey(Minion):
	Class, race, name = "Neutral", "", "Ethereal Lackey"
	mana, attack, health = 1, 1, 1
	index = "Shadows~Neutral~Minion~1~1~1~None~Ethereal Lackey~Battlecry~Uncollectible"
	requireTarget, keyWord, description = False, "", "Battlecry: Discover a spell"
	poolIdentifier = "Druid Spells"
	@classmethod
	def generatePool(cls, Game):
		classes, lists = [], []
		for Class in Classes:
			classes.append(Class+" Spells")
			spellsinClass = []
			for key, value in Game.ClassCards[Class].items():
				if "~Spell~" in key:
					spellsinClass.append(value)
			lists.append(spellsinClass)
		return classes, lists
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if self.ID == self.Game.turn and self.Game.Hand_Deck.handNotFull(self.ID):
			key = classforDiscover(self)+" Spells"
			if "InvokedbyOthers" in comment:
				PRINT(self, "Ethereal Lackey's battlecry adds a random %s spell to player's hand"%Class)
				self.Game.Hand_Deck.addCardtoHand(np.random.choice(self.Game.RNGPools[key]), self.ID, "CreateUsingType")
			else:
				spells = np.random.choice(self.Game.RNGPools[key], 3, replace=False)
				self.Game.options = [spell(self.Game, self.ID) for spell in spells]
				PRINT(self, "Ethereal Lackey's battlecry lets player discover a spell")
				self.Game.DiscoverHandler.startDiscover(self)
				
		return None
		
	def discoverDecided(self, option):
		PRINT(self, "Spell %s is put into player's hand."%option.name)
		self.Game.Hand_Deck.addCardtoHand(option, self.ID)
		self.Game.sendSignal("DiscoveredCardPutintoHand", self.ID, self, option, 0, "")
		
class FacelessLackey(Minion):
	Class, race, name = "Neutral", "", "Faceless Lackey"
	mana, attack, health = 1, 1, 1
	index = "Shadows~Neutral~Minion~1~1~1~None~Faceless Lackey~Battlecry~Uncollectible"
	requireTarget, keyWord, description = False, "", "Battlecry: Summon a 2-Cost minion"
	poolIdentifier = "2-Cost Minions to Summon"
	@classmethod
	def generatePool(cls, Game):
		return "2-Cost Minions to Summon", list(Game.MinionsofCost[2].values())
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		PRINT(self, "Faceless Lackey's battlecry summons a random 2-Cost minions.")
		minion = np.random.choice(self.Game.RNGPools["2-Cost Minions to Summon"])
		self.Game.summonMinion(minion(self.Game, self.ID), self.position+1, self.ID)
		return None
		
class GoblinLackey(Minion):
	Class, race, name = "Neutral", "", "Goblin Lackey"
	mana, attack, health = 1, 1, 1
	index = "Shadows~Neutral~Minion~1~1~1~None~Goblin Lackey~Battlecry~Uncollectible"
	requireTarget, keyWord, description = True, "", "Battlecry: Give a friendly minion +1 Attack and Rush"
	
	def targetExists(self, choice=0):
		return self.selectableFriendlyMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.ID == self.ID and target != self and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if target != None:
			PRINT(self, "Goblin Lackey's battlecry gives friendly minion %s +2 attack and Rush."%target.name)
			target.buffDebuff(1, 0)
			target.getsKeyword("Rush")
		return target
		
class KoboldLackey(Minion):
	Class, race, name = "Neutral", "", "Kobold Lackey"
	mana, attack, health = 1, 1, 1
	index = "Shadows~Neutral~Minion~1~1~1~None~Kobold Lackey~Battlecry~Uncollectible"
	requireTarget, keyWord, description = True, "", "Battlecry: Deal 2 damage"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if target != None:
			PRINT(self, "Kobold Lackey's battlecry deals 2 damage to %s"%target.name)
			self.dealsDamage(target, 2)
		return target
		
class TitanicLackey(Minion):
	Class, race, name = "Neutral", "", "Titanic Lackey"
	mana, attack, health = 1, 1, 1
	index = "Uldum~Neutral~Minion~1~1~1~None~Titanic Lackey~Battlecry~Uncollectible"
	requireTarget, keyWord, description = True, "", "Battlecry: Give a friendly minion +2 Health"
	
	def targetExists(self, choice=0):
		return self.selectableFriendlyMinionExists(choice)
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.ID == self.ID and target != self and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if target != None:
			PRINT(self, "Titanic Lackey's battlecry gives friendly minion %s +2 Health and Taunt"%target.name)
			target.buffDebuff(0, 2)
			target.getsKeyword("Taunt")
		return target
		
class WitchyLackey(Minion):
	Class, race, name = "Neutral", "", "Witchy Lackey"
	mana, attack, health = 1, 1, 1
	index = "Shadows~Neutral~Minion~1~1~1~None~Witchy Lackey~Battlecry~Uncollectible"
	requireTarget, keyWord, description = True, "", "Battlecry: Transform a friendly minion into one that costs (1) more"
	poolIdentifier = "1-Cost Minions to Summon"
	@classmethod
	def generatePool(cls, Game):
		costs, lists = [], []
		for cost in Game.MinionsofCost.keys():
			costs.append("%d-Cost Minions to Summon"%cost)
			lists.append(list(Game.MinionsofCost[cost].values()))
		return costs, lists
		
	def targetExists(self, choice=0):
		return self.selectableFriendlyMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.ID == self.ID and target != self and target.onBoard
	#不知道如果目标随从被返回我方手牌会有什么结算，可能是在手牌中被进化
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if target != None:
			PRINT(self, "Witchy Lackey's battlecry transforms friendly minion %s into one that costs 1 more."%target.name)
			#The target has changed and needs to be tracked.
			target = self.Game.mutate(target, 1)
		return target
		
Lackeys = [DraconicLackey, EtherealLackey, FacelessLackey, GoblinLackey, KoboldLackey, TitanicLackey, WitchyLackey]
"""Mana 2 cards"""
class ArcaneServant(Minion):
	Class, race, name = "Neutral", "Elemental", "Arcane Servant"
	mana, attack, health = 2, 2, 3
	index = "Shadows~Neutral~Minion~2~2~3~Elemental~Arcane Servant"
	requireTarget, keyWord, description = False, "", ""
	
	
class DalaranLibrarian(Minion):
	Class, race, name = "Neutral", "", "Dalaran Librarian"
	mana, attack, health = 2, 2, 3
	index = "Shadows~Neutral~Minion~2~2~3~None~Dalaran Librarian~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Silences adjacent minions"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if self.onBoard:
			adjacentMinions, distribution = self.Game.findAdjacentMinions(self)
			if adjacentMinions != []:
				PRINT(self, "Dalaran Librarian's battlecry Silences adjacent minions.")
				for minion in adjacentMinions:
					minion.getsSilenced()
		return None
		
		
class EVILCableRat(Minion):
	Class, race, name = "Neutral", "Beast", "EVIL Cable Rat"
	mana, attack, health = 2, 1, 1
	index = "Shadows~Neutral~Minion~2~1~1~Beast~EVIL Cable Rat~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Add a Lackey to your hand"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		PRINT(self, "EVIL Cable Rat's battlecry adds a random Lackey to player's hand.")
		lackey = np.random.choice(Lackeys)(self.Game, self.ID)
		self.Game.Hand_Deck.addCardtoHand(lackey, self.ID)
		return None
		
		
class HenchClanHogsteed(Minion):
	Class, race, name = "Neutral", "Beast", "Hench-Clan Hogsteed"
	mana, attack, health = 2, 2, 1
	index = "Shadows~Neutral~Minion~2~2~1~Beast~Hench-Clan Hogsteed~Rush~Deathrattle"
	requireTarget, keyWord, description = False, "Rush", "Rush. Deathrattle: Summon a 1/1 Murloc"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [SummonaHenchClanSquire(self)]
		
class SummonaHenchClanSquire(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self, "Deathrattle: Summon a 1/1 Murloc triggers.")
		self.entity.Game.summonMinion(HenchClanSquire(self.entity.Game, self.entity.ID), self.entity.position+1, self.entity.ID)
		
class HenchClanSquire(Minion):
	Class, race, name = "Neutral", "Murloc", "Hench-Clan Squire"
	mana, attack, health = 1, 1, 1
	index = "Shadows~Neutral~Minion~1~1~1~Murloc~Hench-Clan Squire~Uncollectible"
	requireTarget, keyWord, description = False, "", ""
	
	
class ManaReservoir(Minion):
	Class, race, name = "Neutral", "Elemental", "Mana Reservoir"
	mana, attack, health = 2, 0, 6
	index = "Shadows~Neutral~Minion~2~0~6~Elemental~Mana Reservoir~Spell Damage"
	requireTarget, keyWord, description = False, "Spell Damage", "Spell Damage +1"
	
	
class SpellbookBinder(Minion):
	Class, race, name = "Neutral", "", "Spellbook Binder"
	mana, attack, health = 2, 2, 3
	index = "Shadows~Neutral~Minion~2~2~3~None~Spellbook Binder~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: If you have Spell Damage, draw a card"
	
	def effectCanTrigger(self):
		self.effectViable = False
		if self.Game.playerStatus[self.ID]["Spell Damage"] > 0:
			self.effectViable = True
		else:
			for minion in self.Game.minionsonBoard(self.ID):
				if minion.keyWords["Spell Damage"] > 0:
					self.effectViable = True
					break
					
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		haveSpellDamage = False
		if self.Game.playerStatus[self.ID]["Spell Damage"] > 0:
			haveSpellDamage = True
		else:
			for minion in self.Game.minionsonBoard(self.ID):
				if minion.keyWords["Spell Damage"] > 0:
					haveSpellDamage = True
					break
					
		if haveSpellDamage:
			PRINT(self, "Spellbook Binder's battlecry lets player draws a cards.")
			self.Game.Hand_Deck.drawCard(self.ID)
		return None
		
		
class SunreaverSpy(Minion):
	Class, race, name = "Neutral", "", "Sunreaver Spy"
	mana, attack, health = 2, 2, 3
	index = "Shadows~Neutral~Minion~2~2~3~None~Sunreaver Spy~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: If you control a Secret, gain +1/+1"
	
	def effectCanTrigger(self):
		self.effectViable = self.Game.SecretHandler.secrets[self.ID] != []
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if self.Game.SecretHandler.secrets[self.ID] != []:
			PRINT(self, "Sunreaver Spy's battlecry lets minion gain +1/+1.")
			self.buffDebuff(1, 1)
		return None
		
class ZayleShadowCloak(Minion):
	Class, race, name = "Neutral", "", "Zayle, Shadow Cloak"
	mana, attack, health = 2, 3, 2
	index = "Shadows~Neutral~Minion~2~3~2~None~Zayle, Shadow Cloak~Legendary"
	requireTarget, keyWord, description = False, "", "You start the game with one of Zayle's EVIL Decks!"
	
"""Mana 3 cards"""
class ArcaneWatcher(Minion):
	Class, race, name = "Neutral", "", "Arcane Watcher"
	mana, attack, health = 3, 5, 6
	index = "Shadows~Neutral~Minion~3~5~6~None~Arcane Watcher"
	requireTarget, keyWord, description = False, "", "Can't attack unless you have Spell Damage"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.marks["Can't Attack"] = 1
		
	def hasSpellDamage(self):
		if self.Game.playerStatus[self.ID]["Spell Damage"] > 0:
			return True
		for minion in self.Game.minions[self.ID]:
			if minion.keyWords["Spell Damage"] > 0:
				return True
		return False
		
	def canAttack(self):
		if self.actionable() == False:
			return False
		if self.attack < 1:
			return False
		if self.status["Frozen"] > 0:
			return False
		#THE CHARGE/RUSH MINIONS WILL GAIN ATTACKCHANCES WHEN THEY APPEAR
		if self.attChances_base + self.attChances_extra <= self.attTimes:
			return False
		if self.marks["Can't Attack"] > 0: #如果自己的不能攻击标签还在，则必定没有被沉默
			if self.hasSpellDamage() == False:
				return False
		return True
		
		
class FacelessRager(Minion):
	Class, race, name = "Neutral", "", "Faceless Rager"
	mana, attack, health = 3, 5, 1
	index = "Shadows~Neutral~Minion~3~5~1~None~Faceless Rager~Battlecry"
	requireTarget, keyWord, description = True, "", "Battlecry: Copy a friendly minion's Health"
	
	def targetExists(self, choice=0):
		return self.selectableFriendlyMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.ID == self.ID and target != self and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if target != None:
			PRINT(self, "Faceless Rager's battlecry lets minion copy friendly minion %s's health"%target.name)
			self.statReset(False, target.health)
		return target
		
		
class FlightMaster(Minion):
	Class, race, name = "Neutral", "", "Flight Master"
	mana, attack, health = 3, 3, 4
	index = "Shadows~Neutral~Minion~3~3~4~None~Flight Master~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Summon a 2/2 Gryphon for each player"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		PRINT(self, "Flight Master's battlecry summons a 2/2 Gryphon for each player.")
		self.Game.summonMinion(Gryphon(self.Game, self.ID), self.position+1, self.ID)
		self.Game.summonMinion(Gryphon(self.Game, 3-self.ID), -1, 3-self.ID)
		return None
		
class Gryphon(Minion):
	Class, race, name = "Neutral", "Beast", "Gryphon"
	mana, attack, health = 2, 2, 2
	index = "Shadows~Neutral~Minion~2~2~2~Beast~Gryphon~Uncollectible"
	requireTarget, keyWord, description = False, "", ""
	
	
class HenchClanSneak(Minion):
	Class, race, name = "Neutral", "", "Hench-Clan Sneak"
	mana, attack, health = 3, 3, 3
	index = "Shadows~Neutral~Minion~3~3~3~None~Hench-Clan Sneak~Stealth"
	requireTarget, keyWord, description = False, "Stealth", "Stealth"
	
	
class MagicCarpet(Minion):
	Class, race, name = "Neutral", "", "Magic Carpet"
	mana, attack, health = 3, 1, 6
	index = "Shadows~Neutral~Minion~3~1~6~None~Magic Carpet"
	requireTarget, keyWord, description = False, "", "After you play a 1-Cost minion, give it +1 Attack and Rush"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_MagicCarpet(self)]
		
class Trigger_MagicCarpet(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionBeenPlayed"])
	#The number here is the mana used to play the minion
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject != self.entity and subject.ID == self.entity.ID and number == 1
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self, "A 1-Cost friendly minion %s is played and %s gives it +1 Attack and Rush."%(subject.name, self.entity.name))
		subject.getsKeyword("Rush")
		subject.buffDebuff(1, 0)
		
		
class SpellwardJeweler(Minion):
	Class, race, name = "Neutral", "", "Spellward Jeweler"
	mana, attack, health = 3, 3, 4
	index = "Shadows~Neutral~Minion~3~3~4~None~Spellward Jeweler~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Your hero can't be targeted by spells or Hero Powers until your next turn"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		PRINT(self, self.name, " is played and player can't be targeted by Spells or hero powers until next turn.")
		self.Game.playerStatus[self.ID]["Evasive"] += 1
		self.Game.playerStatus[self.ID]["EvasiveTillYourNextTurn"] += 1
		return None
		
"""Mana 4 cards"""
class ArchmageVargoth(Minion):
	Class, race, name = "Neutral", "", "Archmage Vargoth"
	mana, attack, health = 4, 2, 6
	index = "Shadows~Neutral~Minion~4~2~6~None~Archmage Vargoth~Legendary"
	requireTarget, keyWord, description = False, "", "At the end of your turn, cast a spell you've cast this turn (targets chosen randomly)"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_ArchmageVargoth(self)]
		
class Trigger_ArchmageVargoth(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["TurnEnds"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		spells = []
		for index in self.entity.Game.CounterHandler.cardsPlayedThisTurn[self.entity.ID]["Indices"]:
			if "~Spell~" in index:
				spells.append(self.entity.Game.cardPool[index])
		if spells != []:
			spell = np.random.choice(spells)(self.entity.Game, self.entity.ID)
			PRINT(self, "At the end of turn, %s casts spell %s that player has cast this turn."%(self.entity.name, spell.name))
			spell.cast()
			
			
class Hecklebot(Minion):
	Class, race, name = "Neutral", "Mech", "Hecklebot"
	mana, attack, health = 4, 3, 8
	index = "Shadows~Neutral~Minion~4~3~8~Mech~Hecklebot~Taunt~Battlecry"
	requireTarget, keyWord, description = False, "Taunt", "Taunt. Battlecry: Your opponent summons a minion from their deck"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if self.Game.spaceonBoard(3-self.ID) > 0:
			minions = []
			for card in self.Game.Hand_Deck.decks[3-self.ID]:
				if card.cardType == "Minion":
					minions.append(card)
					
			PRINT(self, "Hecklebot's battlecry lets opponent summon a minion from deck.")
			if minions != []:
				self.Game.summonfromDeck(np.random.choice(minions), -1, self.ID)
		return None
		
		
class HenchClanHag(Minion):
	Class, race, name = "Neutral", "", "Hench-Clan Hag"
	mana, attack, health = 4, 3, 3
	index = "Shadows~Neutral~Minion~4~3~3~None~Hench-Clan Hag~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Summon two 1/1 Amalgams with all minions types"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		PRINT(self, "Hench-Clan Hag's battlecry summons two 1/1 Amalgams with all minion types.")
		pos = (self.position, "leftandRight") if self.onBoard else (-1, "totheRightEnd")
		self.Game.summonMinion([Amalgam(self.Game, self.ID) for i in range(2)], pos, self.ID)
		return None
		
class Amalgam(Minion):
	Class, race, name = "Neutral", "Elemental, Mech, Demon, Murloc, Dragon, Beast, Pirate, Totem", "Amalgam"
	mana, attack, health = 1, 1, 1
	index = "Shadows~Neutral~Minion~1~1~1~Beast~Murloc~Pirate~Mech~Totem~Demon~Elemental~Dragon~Amalgam~Uncollectible"
	requireTarget, keyWord, description = False, "", "This is an Elemental, Mech, Demon, Murloc, Dragon, Beast, Pirate and Totem"
	
	
class PortalKeeper(Minion):
	Class, race, name = "Neutral", "Demon", "Portal Keeper"
	mana, attack, health = 4, 5, 2
	index = "Shadows~Neutral~Minion~4~5~2~Demon~Portal Keeper~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Shuffle 3 Portals into your deck. When drawn, summon a 2/2 Demon with Rush"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		PRINT(self, "Portal Keeper's battlecry shuffles 3 Portals into player's deck.")
		portals = [FelhoundPortal(self.Game, self.ID) for i in range(3)]
		self.Game.Hand_Deck.shuffleCardintoDeck(portals, self.ID)
		return None
		
class FelhoundPortal(Spell):
	Class, name = "Neutral", "Felhound Portal"
	requireTarget, mana = False, 2
	index = "Shadows~Neutral~Spell~2~Felhound Portal~Casts When Drawn~Uncollectible"
	description = "Casts When Drawn. Summon a 2/2 Felhound with Rush"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		PRINT(self, "Felhound Portal is cast and summons a 2/2 Felhound with Rush.")
		self.Game.summonMinion(Felhound(self.Game, self.ID), -1, self.ID)
		return None
		
class Felhound(Minion):
	Class, race, name = "Neutral", "Demon", "Felhound"
	mana, attack, health = 2, 2, 2
	index = "Shadows~Neutral~Minion~2~2~2~Demon~Felhound~Rush~Uncollectible"
	requireTarget, keyWord, description = False, "Rush", "Rush"
	
	
class ProudDefender(Minion):
	Class, race, name = "Neutral", "", "Proud Defender"
	mana, attack, health = 4, 2, 6
	index = "Shadows~Neutral~Minion~4~2~6~None~Proud Defender~Taunt"
	requireTarget, keyWord, description = False, "Taunt", "Taunt. Has +2 Attack while you have no other minions"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.appearResponse = [self.checkBoard]
		self.disappearResponse = [self.deactivate]
		self.silenceResponse = [self.deactivate]
		self.triggersonBoard = [Trigger_ProudDefender(self)]
		
	def checkBoard(self):
		if self.onBoard:
			noOtherFriendlyMinions = True
			for minion in self.Game.minions[self.ID]:
				if minion.cardType == "Minion" and minion != self and minion.onBoard:
					noOtherFriendlyMinions = False
					break
			if noOtherFriendlyMinions and self.activated == False:
				PRINT(self, "Proud Defender gains +2 Attack because there's no other friendly minion")
				self.statChange(2, 0)
				self.activated = True
			elif noOtherFriendlyMinions == False and self.activated:
				PRINT(self, "Proud Defender loses +2 Attack because there are other friendly minions")
				self.statChange(-2, 0)
				self.activated = False
				
	def deactivate(self):
		if self.activated:
			self.statChange(-2, 0)
			
class Trigger_ProudDefender(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionAppears", "MinionDisappears"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		if signal == "MinionAppears":
			return self.entity.onBoard and subject.ID == self.entity.ID and subject != self.entity
		else:
			return self.entity.onBoard and target.ID == self.entity.ID and target != self.entity
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self, "%s checks board due to board change."%self.entity.name)
		self.entity.checkBoard()
		
		
class SoldierofFortune(Minion):
	Class, race, name = "Neutral", "Elemental", "Soldier of Fortune"
	mana, attack, health = 4, 5, 6
	index = "Shadows~Neutral~Minion~4~5~6~Elemental~Soldier of Fortune"
	requireTarget, keyWord, description = False, "", "Whenever this minion attacks, give your opponent a coin"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_SoldierofFortune(self)]
		
class Trigger_SoldierofFortune(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionAttackingMinion", "MinionAttackingHero"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject == self.entity
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self, "Whenever it attacks, %s gives opponent a Coin."%self.entity.name)
		self.entity.Game.Hand_Deck.addCardtoHand(TheCoin(self.entity.Game, 3-self.entity.ID), 3-self.entity.ID)
		
		
class TravelingHealer(Minion):
	Class, race, name = "Neutral", "", "Traveling Healer"
	mana, attack, health = 4, 3, 2
	index = "Shadows~Neutral~Minion~4~3~2~None~Traveling Healer~Battlecry~Divine Shield"
	requireTarget, keyWord, description = True, "Divine Shield", "Divine Shield. Battlecry: Restore 3 Health."
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if target != None:
			heal = 3 * (2 ** self.countHealDouble())
			self.restoresHealth(target, heal)
		return target
		
		
class VioletSpellsword(Minion):
	Class, race, name = "Neutral", "", "Violet Spellsword"
	mana, attack, health = 4, 1, 6
	index = "Shadows~Neutral~Minion~4~1~6~None~Violet Spellsword~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Gain +1 Attack for each spell in your hand"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		numSpells = 0
		for card in self.Game.Hand_Deck.hands[self.ID]:
			if card.cardType == "Spell":
				numSpells += 1
				
		PRINT(self, "Violet Spellward's battlecry lets the minion gain +1 health for every card in player's hand")
		self.buffDebuff(numSpells, 0)
		return None
		
"""Mana 5 cards"""
class AzeriteElemental(Minion):
	Class, race, name = "Neutral", "Elemental", "Azerite Elemental"
	mana, attack, health = 5, 2, 7
	index = "Shadows~Neutral~Minion~5~2~7~Elemental~Azerite Elemental"
	requireTarget, keyWord, description = False, "", "At the start of your turn, gain Spell Damage +2"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_AzeriteElemental(self)]
		
class Trigger_AzeriteElemental(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["TurnStarts"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self, "At the start of turn, %s gains Spell Damage +2"%self.entity.name)
		self.entity.getsKeyword("Spell Damage")
		self.entity.getsKeyword("Spell Damage")
		
		
class BaristaLynchen(Minion):
	Class, race, name = "Neutral", "", "Barista Lynchen"
	mana, attack, health = 5, 4, 5
	index = "Shadows~Neutral~Minion~5~4~5~None~Barista Lynchen~Battlecry~Legendary"
	requireTarget, keyWord, description = False, "", "Battlecry: Add a copy of each of your other Battlecry minions to your hand"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		battlecryMinions = []
		for minion in self.Game.minions[self.ID]:
			if "~Battlecry" in minion.index and minion != self:
				battlecryMinions.append(minion)
		if battlecryMinions != []:
			PRINT(self, "Barista Lynchen's battlecry adds copies of all other friendly Battlecry minions to player's hand.")
			for minion in battlecryMinions:
				self.Game.Hand_Deck.addCardtoHand(type(minion)(self.Game, self.ID), self.ID)
		return None
		
		
class DalaranCrusader(Minion):
	Class, race, name = "Neutral", "", "Dalaran Crusader"
	mana, attack, health = 5, 5, 4
	index = "Shadows~Neutral~Minion~5~5~4~None~Dalaran Crusader~Divine Shield"
	requireTarget, keyWord, description = False, "Divine Shield", "Divine Shield"
	
	
class RecurringVillain(Minion):
	Class, race, name = "Neutral", "", "Recurring Villain"
	mana, attack, health = 5, 3, 6
	index = "Shadows~Neutral~Minion~5~3~6~None~Recurring Villain~Deathrattle"
	requireTarget, keyWord, description = False, "", "Deathrattle: If this minion has 4 or more Attack, resummon it"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [ResummonifAttackGreaterthan3(self)]
		
class ResummonifAttackGreaterthan3(Deathrattle_Minion):
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return target == self.entity and number > 3
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self, "Deathrattle: Resummon the minion %s triggers."%self.entity.name)
		newMinion = type(self.entity)(self.entity.Game, self.entity.ID)
		self.entity.Game.summonMinion(newMinion, self.entity.position+1, self.entity.ID)
		
		
class SunreaverWarmage(Minion):
	Class, race, name = "Neutral", "", "Sunreaver Warmage"
	mana, attack, health = 5, 4, 4
	index = "Shadows~Neutral~Minion~5~4~4~None~Sunreaver Warmage~Battlecry"
	requireTarget, keyWord, description = True, "", "Battlecry: If you're holding a spell costs (5) or more, deal 4 damage"
	
	def effectCanTrigger(self):
		self.effectViable = self.Game.Hand_Deck.holdingSpellwith5CostorMore(self.ID)
		
	def returnTrue(self, choice=0):
		return self.Game.Hand_Deck.holdingSpellwith5CostorMore(self.ID)
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if target != None and self.Game.Hand_Deck.holdingSpellwith5CostorMore(self.ID):
			PRINT(self, "Sunreaver Warmage's battlecry deals 4 damage to target %s"%target.name)
			self.dealsDamage(target, 4)
		return target
		
"""Mana 6 cards"""
class EccentricScribe(Minion):
	Class, race, name = "Neutral", "", "Eccentric Scribe"
	mana, attack, health = 6, 6, 4
	index = "Shadows~Neutral~Minion~6~6~4~None~Eccentric Scribe~Deathrattle"
	requireTarget, keyWord, description = False, "", "Deathrattle: Summon four 1/1 Vengeful Scrolls"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [Summon4VengefulScrolls(self)]
		
class Summon4VengefulScrolls(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		pos = (self.entity.position, "totheRight") if self.entity in self.entity.Game.minions[self.entity.ID] else (-1, "totheRightEnd")
		PRINT(self, "Deathrattle: Summon four 1/1 Vengeful Scrolls triggers.")
		self.entity.Game.summonMinion([VengefulScroll(self.entity.Game, self.entity.ID) for i in range(4)], pos, self.entity.ID)
		
class VengefulScroll(Minion):
	Class, race, name = "Neutral", "", "Vengeful Scroll"
	mana, attack, health = 1, 1, 1
	index = "Shadows~Neutral~Minion~1~1~1~None~Vengeful Scroll~Uncollectible"
	requireTarget, keyWord, description = False, "", ""
	
	
class MadSummoner(Minion):
	Class, race, name = "Neutral", "Demon", "Mad Summoner"
	mana, attack, health = 6, 4, 4
	index = "Shadows~Neutral~Minion~6~4~4~Demon~Mad Summoner~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Fill each player's board with 1/1 Imps"
	#假设是轮流为我方和对方召唤两个小鬼
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		PRINT(self, "Mad Summoner's battlecry fills the Board with 1/1 Imps.")
		while True:
			friendlyBoardNotFull, enemyBoardNotFull = True, True
			if self.Game.spaceonBoard(self.ID) > 0:
				self.Game.summonMinion([Imp_Shadows(self.Game, self.ID) for i in range(2)], (-1, "totheRightEnd"), self.ID)
			else:
				friendlyBoardNotFull = False
			if self.Game.spaceonBoard(3-self.ID) > 0:
				self.Game.summonMinion([Imp_Shadows(self.Game, 3-self.ID) for i in range(2)], (-1, "totheRightEnd"), 3-self.ID)
			else:
				enemyBoardNotFull = False
			if friendlyBoardNotFull == False and enemyBoardNotFull == False:
				break
				
		return None
		
class Imp_Shadows(Minion):
	Class, race, name = "Neutral", "Demon", "Imp"
	mana, attack, health = 1, 1, 1
	index = "Shadows~Neutral~Minion~1~1~1~Demon~Imp~Uncollectible"
	requireTarget, keyWord, description = False, "", ""
	
	
class PortalOverfiend(Minion):
	Class, race, name = "Neutral", "Demon", "Portal Overfiend"
	mana, attack, health = 6, 5, 6
	index = "Shadows~Neutral~Minion~6~5~6~Demon~Portal Overfiend~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Shuffle 3 Portals into your deck. When drawn, summon a 2/2 Demon with Rush"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		PRINT(self, "Portal Overfiend's battlecry shuffles 3 Portals into player's deck.")
		portals = [FelhoundPortal(self.Game, self.ID) for i in range(3)]
		self.Game.Hand_Deck.shuffleCardintoDeck(portals, self.ID)
		return None
		
		
class Safeguard(Minion):
	Class, race, name = "Neutral", "Mech", "Safeguard"
	mana, attack, health = 6, 4, 5
	index = "Shadows~Neutral~Minion~6~4~5~Mech~Safeguard~Taunt~Deathrattle"
	requireTarget, keyWord, description = False, "Taunt", "Taunt. Deathrattle: Summon a 0/5 Vault Safe with Taunt"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [SummonaVaultSafe(self)]
		
class SummonaVaultSafe(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self, "Deathrattle: Summon a 0/5 Vault Safe triggers.")
		self.entity.Game.summonMinion(VaultSafe(self.entity.Game, self.entity.ID), self.entity.position+1, self.entity.ID)
		
class VaultSafe(Minion):
	Class, race, name = "Neutral", "Mech", "Vault Safe"
	mana, attack, health = 2, 0, 5
	index = "Shadows~Neutral~Minion~2~0~5~Mech~Vault Safe~Taunt~Uncollectible"
	requireTarget, keyWord, description = False, "Taunt", "Taunt"
	
	
class UnseenSaboteur(Minion):
	Class, race, name = "Neutral", "", "Unseen Saboteur"
	mana, attack, health = 6, 5, 6
	index = "Shadows~Neutral~Minion~6~5~6~None~Unseen Saboteur~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Your opponent casts a random spell from their hand (targets chosen randomly)"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		PRINT(self, "Unseen Saboteur's battlecry lets opponent cast a random spell from hand with random target.")
		spellsinHand = []
		for card in self.Game.Hand_Deck.hands[3-self.ID]:
			if card.cardType == "Spell":
				spellsinHand.append(card)
				
		if spellsinHand != []:
			spelltoCast = np.random.choice(spellsinHand)
			self.Game.Hand_Deck.extractfromHand(spelltoCast)
			spelltoCast.cast()
		return None
		
		
class VioletWarden(Minion):
	Class, race, name = "Neutral", "", "Violet Warden"
	mana, attack, health = 6, 4, 7
	index = "Shadows~Neutral~Minion~6~4~7~None~Violet Warden~Taunt~Spell Damage"
	requireTarget, keyWord, description = False, "Taunt,Spell Damage", "Taunt, Spell Damage +1"
	
"""Mana 7 cards"""
class ChefNomi(Minion):
	Class, race, name = "Neutral", "", "Chef Nomi"
	mana, attack, health = 7, 6, 6
	index = "Shadows~Neutral~Minion~7~6~6~None~Chef Nomi~Battlecry~Legendary"
	requireTarget, keyWord, description = False, "", "Battlecry: If your deck is empty, summon six 6/6 Greasefire Elementals"
	
	def effectCanTrigger(self):
		self.effectViable = self.Game.Hand_Deck.decks[self.ID] == []
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if self.Game.Hand_Deck.decks[self.ID] == []:
			PRINT(self, "Chef Nomi's battlecry fills the player's board with 6/6 Greasefire Elementals.")
			if self.onBoard:
				self.Game.summonMinion([GreasefireElemental(self.Game, self.ID) for i in range(6)], (self.position, "leftandRight"), self.ID)
			else:
				self.Game.summonMinion([GreasefireElemental(self.Game, self.ID) for i in range(7)], (-1, "totheRightEnd"), self.ID)
		return None
		
class GreasefireElemental(Minion):
	Class, race, name = "Neutral", "Elemental", "Greasefire Elemental"
	mana, attack, health = 6, 6, 6
	index = "Shadows~Neutral~Minion~6~6~6~Elemental~Greasefire Elemental~Uncollectible"
	requireTarget, keyWord, description = False, "", ""
	
	
class ExoticMountseller(Minion):
	Class, race, name = "Neutral", "", "Exotic Mountseller"
	mana, attack, health = 7, 5, 8
	index = "Shadows~Neutral~Minion~7~5~8~None~Exotic Mountseller"
	requireTarget, keyWord, description = False, "", "Whenever you cast a spell, summon a random 3-Cost Beast"
	poolIdentifier = "3-Cost Beasts to Summon"
	@classmethod
	def generatePool(cls, Game):
		threeCostBeasts = []
		for key, value in Game.MinionswithRace["Beast"].items():
			if key.split('~')[3] == "3":
				threeCostBeasts.append(value)
		return "3-Cost Beasts to Summon", threeCostBeasts
		
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_ExoticMountseller(self)]
		
class Trigger_ExoticMountseller(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["SpellPlayed"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject.ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self, "Player casts a spell and %s summons a random 3-Cost Beast."%self.entity.name)
		beast = np.random.choice(self.entity.Game.RNGPools["3-Cost Beasts to Summon"])(self.entity.Game, self.entity.ID)
		self.entity.Game.summonMinion(beast, self.entity.position+1, self.entity.ID)
		
		
class TunnelBlaster(Minion):
	Class, race, name = "Neutral", "", "Tunnel Blaster"
	mana, attack, health = 7, 3, 8
	index = "Shadows~Neutral~Minion~7~3~8~None~Tunnel Blaster~Taunt~Deathrattle"
	requireTarget, keyWord, description = False, "Taunt", "Taunt. Deathrattle: Deal 3 damage to all minions"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [Deal3DamagetoAllMinions(self)]
		
class Deal3DamagetoAllMinions(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		targets = self.entity.Game.minionsonBoard(1) + self.entity.Game.minionsonBoard(2)
		damages = [3 for obj in targets]
		PRINT(self, "Deathrattle: Deal 3 damage to all minions triggers.")
		self.entity.dealsAOE(targets, damages)
		
		
class UnderbellyOoze(Minion):
	Class, race, name = "Neutral", "", "Underbelly Ooze"
	mana, attack, health = 7, 3, 5
	index = "Shadows~Neutral~Minion~7~3~5~None~Underbelly Ooze"
	requireTarget, keyWord, description = False, "", "After this minion survives damage, summon a copy of it"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_UnderbellyOoze(self)]
		
class Trigger_UnderbellyOoze(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionTakesDamage"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and target == self.entity and self.entity.health > 0 and self.entity.dead == False
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self, "%s survives damage and summon a copy of itself."%self.entity.name)
		Copy = self.entity.selfCopy(self.entity.ID)
		self.entity.Game.summonMinion(Copy, self.entity.position+1, self.entity.ID)
		
"""Mana 8 cards"""
class Batterhead(Minion):
	Class, race, name = "Neutral", "", "Batterhead"
	mana, attack, health = 8, 3, 12
	index = "Shadows~Neutral~Minion~8~3~12~None~Batterhead~Rush"
	requireTarget, keyWord, description = False, "Rush", "Rush. After this attacks and kills a minion, it may attack again"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_Batterhead(self)]
		
class Trigger_Batterhead(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionAttackedMinion"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject == self.entity and self.entity.health > 0 and self.entity.dead == False and (target.health < 1 or target.dead == True)
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self, "After %s attacks and kills a minion %s, it gains an extra attack chance."%(self.entity.name, target.name))
		self.entity.attChances_extra += 1
		
		
class HeroicInnkeeper(Minion):
	Class, race, name = "Neutral", "", "Heroic Innkeeper"
	mana, attack, health = 1, 4, 4
	index = "Shadows~Neutral~Minion~8~4~4~None~Heroic Innkeeper~Taunt~Battlecry"
	requireTarget, keyWord, description = False, "Taunt", "Taunt. Battlecry: Gain +2/+2 for each other friendly minion"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if self.onBoard or self.inHand:
			targets = self.Game.minionsonBoard(self.ID)
			extractfrom(self, targets)
			buff = 2 * len(targets)
		PRINT(self, "Heroic Innkeeper's battlecry gives minion +2/+2 for each other friendly minion.")
		self.buffDebuff(buff, buff)
		return None
		
		
class JepettoJoybuzz(Minion):
	Class, race, name = "Neutral", "", "Jepetto Joybuzz"
	mana, attack, health = 8, 6, 6
	index = "Shadows~Neutral~Minion~8~6~6~None~Jepetto Joybuzz~Battlecry~Legendary"
	requireTarget, keyWord, description = False, "", "Battlecry: Draw 2 minions from your deck. Set their Attack, Health, and Cost to 1"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		PRINT(self, "Jepetto Joybuzz's battlecry draws 2 minions from player's deck and sets their Attack, Health and Cost to 1")
		for i in range(2):
			minionsinDeck = []
			for card in self.Game.Hand_Deck.decks[self.ID]:
				if card.cardType == "Minion":
					minionsinDeck.append(card)
					
			if minionsinDeck != []:
				card, mana = self.Game.Hand_Deck.drawCard(self.ID, np.random.choice(minionsinDeck))
				if card != None:
					ManaModification(card, changeby=0, changeto=1).applies()
					card.statReset(1, 1)
		return None
		
		
class WhirlwindTempest(Minion):
	Class, race, name = "Neutral", "Elemental", "Whirlwind Tempest"
	mana, attack, health = 8, 6, 6
	index = "Shadows~Neutral~Minion~8~6~6~Elemental~Whirlwind Tempest"
	requireTarget, keyWord, description = False, "", "Your Windfury minions have Mega Windfury"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.auras["Has Aura"] = HasAura_Dealer(self, self.applicable, "Mega Windfury")
		
	def applicable(self, target):
		return target.keyWords["Windfury"] > 0
		
"""Mana 9 cards"""
class BurlyShovelfist(Minion):
	Class, race, name = "Neutral", "", "Burly Shovelfist"
	mana, attack, health = 9, 9, 9
	index = "Shadows~Neutral~Minion~9~9~9~None~Burly Shovelfist~Rush"
	requireTarget, keyWord, description = False, "Rush", "Rush"
	
	
class ArchivistElysiana(Minion):
	Class, race, name = "Neutral", "", "Archivist Elysiana"
	mana, attack, health = 9, 7, 7
	index = "Shadows~Neutral~Minion~9~7~7~None~Archivist Elysiana~Battlecry~Legendary"
	requireTarget, keyWord, description = False, "", "Battlecry: Discover 5 cards. Replace your deck with 2 copies of each"
	poolIdentifier = "Cards as Druid"
	@classmethod
	def generatePool(cls, Game):
		classes, lists, neutralCards = [], [], list(Game.NeutralMinions.values())
		for Class in Classes:
			classes.append("Cards as "+Class)
			lists.append(list(Game.ClassCards[Class].values())+neutralCards)
		return classes, lists
		
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.newDeck = []
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		key = "Cards as "+classforDiscover(self)
		self.newDeck = []
		if "InvokedbyOthers" in comment:
			for i in range(5):
				newCard = np.random.choice(self.Game.RNGPools[key])
				self.newDeck.append(newCard(self.Game, self.ID))
				self.newDeck.append(newCard(self.Game, self.ID))
		else:
			for i in range(5):
				cards = np.random.choice(self.Game.RNGPools[key], 3, replace=False)
				self.Game.options = [card(self.Game, self.ID) for card in cards]
				self.Game.DiscoverHandler.startDiscover(self)
				
		self.Game.Hand_Deck.extractfromDeck(None, all=True, ID=self.ID)
		self.Game.Hand_Deck.decks[self.ID] = self.newDeck
		np.random.shuffle(self.Game.Hand_Deck.decks[self.ID])
		self.newDeck = []
		return None
		
	def discoverDecided(self, option):
		PRINT(self, "Two copies of %s added to the deck replacement."%option.name)
		self.newDeck.append(option)
		self.newDeck.append(type(option)(self.Game, self.ID))
		
"""Mana 10 cards"""
class BigBadArchmage(Minion):
	Class, race, name = "Neutral", "", "Big Bad Archmage"
	mana, attack, health = 10, 6, 6
	index = "Shadows~Neutral~Minion~10~6~6~None~Big Bad Archmage"
	requireTarget, keyWord, description = False, "", "At the end of your turn, summon a random 6-Cost minion"
	poolIdentifier = "6-Cost Minions to Summon"
	@classmethod
	def generatePool(cls, Game):
		return "6-Cost Minions to Summon", list(Game.MinionsofCost[6].values())
		
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_BigBadArchmage(self)]
		
class Trigger_BigBadArchmage(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["TurnEnds"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self, "At the end of turn, %s summons a 6-Cost minion."%self.entity.name)
		minion = np.random.choice(self.entity.Game.RNGPools["6-Cost Minions to Summon"])(self.entity.Game, self.entity.ID)
		self.entity.Game.summonMinion(minion, self.entity.position+1, self.entity.ID)
		
"""Druid cards"""
class Acornbearer(Minion):
	Class, race, name = "Druid", "", "Acornbearer"
	mana, attack, health = 1, 2, 1
	index = "Shadows~Druid~Minion~1~2~1~None~Acornbearer~Deathrattle"
	requireTarget, keyWord, description = False, "", "Deathrattle: Add two 1/1 Squirrels to your hand"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [AddTwoSquirrelstoHand(self)]
		
class AddTwoSquirrelstoHand(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self, "Deathrattle: Summon a 2/1 Damaged Golem triggers.")
		self.entity.Game.Hand_Deck.addCardtoHand([Squirrel, Squirrel], self.entity.ID, "CreateUsingType")
		
class Squirrel(Minion):
	Class, race, name = "Neutral", "Beast", "Squirrel"
	mana, attack, health = 1, 1, 1
	index = "Shadows~Druid~Minion~1~1~1~Beast~Squirrel~Uncollectible"
	requireTarget, keyWord, description = False, "", ""
	
	
class CrystalPower(Spell):
	Class, name = "Druid", "Crystal Power"
	requireTarget, mana = True, 1
	index = "Shadows~Druid~Spell~1~Crystal Power~Choose One"
	description = "Choose One - Deal 2 damage to a minion; or Restore 5 Health"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.chooseOne = 1
		self.options = [PiercingThorns_Option(self), HealingBlossom_Option(self)]
		
	def available(self):
		return self.selectableCharacterExists(1)
		
	#available() only needs to check selectableCharacterExists
	def targetCorrect(self, target, choice=0):
		if choice == "ChooseBoth" or choice == 1:
			return (target.cardType == "Minion" or target.cardType == "Hero") and target.onBoard
		else:
			return target.cardType == "Minion" and target.onBoard
			
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if target != None:
			if choice == "ChooseBoth": #如果目标是一个随从，先对其造成伤害，如果目标存活，才能造成治疗
				if target.cardType == "Minion": #只会对随从造成伤害
					damage = (2 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
					PRINT(self, "Crystal Power deals %d damage to %s"%(damage, target.name))
					self.dealsDamage(target, damage)
				if target.health > 0 and target.dead == False: #法术造成伤害之后，那个随从必须活着才能接受治疗，不然就打2无论如何都变得没有意义
					heal = 5 * (2 ** self.countHealDouble())
					PRINT(self, "Crystal Power restores %d Health to %s"%(heal, target.name))
					self.restoresHealth(target, heal)
			elif choice == 0:
				if target.cardType == "Minion":
					damage = (2 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
					PRINT(self, "Crystal Power deals %d damage to %s"%(damage, target.name))
					self.dealsDamage(target, damage)
			else: #Choice == 1
				heal = 5 * (2 ** self.countHealDouble())
				PRINT(self, "Crystal Power restores %d Health to %s"%(heal, target.name))
				self.restoresHealth(target, heal)
		return target
		
class PiercingThorns_Option:
	def __init__(self, spell):
		self.spell = spell
		self.name = "Piercing Thorns"
		self.description = "2 damage to minion"
		self.index = "Shadows~Druid~Spell~1~Piercing Thorns~Uncollectible"
		
	def available(self):
		return self.spell.selectableMinionExists(0)
		
	def selfCopy(self, recipient):
		return type(self)(recipient)
		
class HealingBlossom_Option:
	def __init__(self, spell):
		self.spell = spell
		self.name = "Healing Blossom"
		self.description = "Heal 5"
		self.index = "Shadows~Druid~Spell~1~Healing Blossom~Uncollectible"
		
	def available(self):
		return self.spell.selectableCharacterExists(1)
		
	def selfCopy(self, recipient):
		return type(self)(recipient)
		
class PiercingThorns(Spell):
	Class, name = "Druid", "Piercing Thorns"
	requireTarget, mana = True, 1
	index = "Shadows~Druid~Spell~1~Piercing Thorns~Uncollectible"
	description = "Deal 2 damage to a minion"
	
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if target != None:
			damage = (2 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			PRINT(self, "Piercing Thorns is cast and deals %d damage to %s"%(damage, target.name))
			self.dealsDamage(target, damage)
		return target
		
class HealingBlossom(Spell):
	Class, name = "Druid", "Healing Blossom"
	requireTarget, mana = True, 1
	index = "Shadows~Druid~Spell~1~Healing Blossom~Uncollectible"
	description = "Restores 5 Health"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if target != None:
			heal = 5 * (2 ** self.countHealDouble())
			PRINT(self, "Healing Blossom is cast and restores %d health to %s"%(heal, target.name))
			self.restoresHealth(target, heal)
		return target
		
		
class CrystalsongPortal(Spell):
	Class, name = "Druid", "Crystalsong Portal"
	requireTarget, mana = False, 2
	index = "Shadows~Druid~Spell~2~Crystalsong Portal"
	description = "Discover a Druid minion. If your hand has no minions, keep all 3"
	poolIdentifier = "Druid Minions"
	@classmethod
	def generatePool(cls, Game):
		druidMinions = []
		for key, value in Game.ClassCards["Druid"].items():
			if "~Minion~" in key:
				druidMinions.append(value)
		return "Druid Minions", druidMinions
		
	def effectCanTrigger(self):
		self.effectViable = True
		for card in self.Game.Hand_Deck.hands[self.ID]:
			if card.cardType == "Minion":
				self.effectViable = False
				break
				
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if self.Game.Hand_Deck.handNotFull(self.ID):
			handHasMinion = False
			for card in self.Game.Hand_Deck.hands[self.ID]:
				if card.cardType == "Minion":
					handHasMinion = True
					break
			if handHasMinion == False:
				PRINT(self, "Crystalsong Portal is cast and adds all 3 Druid minions to player's hand.")
				minions = np.random.choice(self.Game.RNGPools["Druid Minions"], 3, replace=False)
				self.Game.Hand_Deck.addCardtoHand(minions, self.ID, "CreateUsingType")
			else:
				if "CastbyOthers" in comment:
					PRINT(self, "Crystalsong Portal is cast and adds a random Druid minion to player's hand")
					minion = np.random.choice(self.Game.RNGPools["Druid Minions"])
					self.Game.Hand_Deck.addCardtoHand(minion, self.ID, "CreateUsingType")
				else:
					PRINT(self, "Crystalsong Portal is cast and lets player discover a Druid Minion.")
					minions = np.random.choice(self.Game.RNGPools["Druid Minions"], 3, replace=False)
					self.Game.options = [minion(self.Game, self.ID) for minion in minions]
					self.Game.DiscoverHandler.startDiscover(self)
					
		return None
		
	def discoverDecided(self, option):
		PRINT(self, "Druid Minion %s is put into player's hand."%option.name)
		self.Game.Hand_Deck.addCardtoHand(option, self.ID)
		self.Game.sendSignal("DiscoveredCardPutintoHand", self.ID, self, option, 0, "")
		
		
class DreamwayGuardians(Spell):
	Class, name = "Druid", "Dreamway Guardians"
	requireTarget, mana = False, 2
	index = "Shadows~Druid~Spell~2~Dreamway Guardians"
	description = "Summon two 1/2 Dryads with Lifesteal"
	def available(self):
		return self.Game.spaceonBoard(self.ID) > 0
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		PRINT(self, "Dreamway Guardians is played and summons two 1/2 Dryads with Lifesteal.")
		self.Game.summonMinion([CrystalDryad(self.Game, self.ID) for i in range(2)], (-1, "totheRightEnd"), self.ID)
		return None
		
class CrystalDryad(Minion):
	Class, race, name = "Druid", "", "Crystal Dryad"
	mana, attack, health = 1, 1, 2
	index = "Shadows~Druid~Minion~1~1~2~None~Crystal Dryad~Lifesteal~Uncollectible"
	requireTarget, keyWord, description = False, "Lifesteal", "Lifesteal"
	
	
class KeeperStalladris(Minion):
	Class, race, name = "Druid", "", "Keeper Stalladris"
	mana, attack, health = 2, 2, 3
	index = "Shadows~Druid~Minion~2~2~3~None~Keeper Stalladris~Legendary"
	requireTarget, keyWord, description = False, "", "After you cast a Choose One spell, add copies of both choices to your hand"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_KeeperStalladris(self)]
		
class Trigger_KeeperStalladris(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["SpellBeenPlayed"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject.ID == self.entity.ID and subject.chooseOne > 0
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self, "After player casts spell %s, %s adds copies of both choices to player's hand."%(subject.name, self.entity.name))
		for option in subject.options:
			self.entity.Game.Hand_Deck.addCardtoHand(option.index, self.entity.ID, "CreateUsingIndex")
			
			
class Lifeweaver(Minion):
	Class, race, name = "Druid", "", "Lifeweaver"
	mana, attack, health = 3, 2, 5
	index = "Shadows~Druid~Minion~3~2~5~None~Lifeweaver"
	requireTarget, keyWord, description = False, "", "Whenever you restore Health, add a random Druid spell to your hand"
	poolIdentifier = "Druid Spells"
	@classmethod
	def generatePool(cls, Game):
		druidSpells = []
		for key, value in Game.ClassCards["Druid"].items():
			if "~Spell~" in key:
				druidSpells.append(value)
		return "Druid Spells", druidSpells
		
	def __init__(self, Game, ID,):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_Lifeweaver(self)]
			
class Trigger_Lifeweaver(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionGetsHealed", "HeroGetsHealed"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject.ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self, "Player restores Health, and %s adds a random Druid spell to player's hand."%self.entity.name)
		self.entity.Game.Hand_Deck.addCardtoHand(np.random.choice(self.entity.Game.RNGPools["Druid Spells"]), self.entity.ID, "CreateUsingType")
		
		
class CrystalStag(Minion):
	Class, race, name = "Druid", "Beast", "Crystal Stag"
	mana, attack, health = 5, 4, 4
	index = "Shadows~Druid~Minion~5~4~4~Beast~Crystal Stag~Rush~Battlecry"
	requireTarget, keyWord, description = False, "Rush", "Rush. Battlecry: If you've restored 5 Health this game, summon a copy of this"
	
	def effectCanTrigger(self):
		self.effectViable = self.Game.CounterHandler.healthRestoredThisGame[self.ID] > 4
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if self.Game.CounterHandler.healthRestoredThisGame[self.ID] > 4:
			PRINT(self, "Crystal Stag's battlecry summons a copy of itself.")
			Copy = self.selfCopy(self.ID)
			self.Game.summonMinion(Copy, self.position+1, self.ID)
		return None
		
		
class BlessingoftheAncients(Spell):
	Class, name = "Druid", "Blessing of the Ancients"
	requireTarget, mana = False, 3
	index = "Shadows~Druid~Spell~3~Blessing of the Ancients~Twinspell"
	description = "Twinspell. Give your minions +1/+1"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.twinSpell = 1
		self.twinSpellCopy = blessingoftheancients
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		PRINT(self, "Twinspell Blessing of the Ancients is played and gives all friendly minions +1/+1.")
		for minion in self.Game.minionsonBoard(self.ID):
			minion.buffDebuff(1, 1)
		return None
		
class blessingoftheancients(Spell):
	Class, name = "Druid", "Blessing of the Ancients"
	requireTarget, mana = False, 3
	index = "Shadows~Druid~Spell~3~Blessing of the Ancients~Uncollectible"
	description = "Give your minions +1/+1"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		PRINT(self, "Blessing of the Ancients is played and gives all friendly minions +1/+1.")
		for minion in self.Game.minionsonBoard(self.ID):
			minion.buffDebuff(1, 1)
		return None
		
		
class Lucentbark(Minion):
	Class, race, name = "Druid", "", "Lucentbark"
	mana, attack, health = 8, 4, 8
	index = "Shadows~Druid~Minion~8~4~8~None~Lucentbark~Taunt~Deathrattle~Legendary"
	requireTarget, keyWord, description = False, "Taunt", "Taunt. Deathrattle: Go dormant. Restore 5 Health to awaken this minion"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [BecomeSpiritofLucentbark(self)]
		
class BecomeSpiritofLucentbark(Deathrattle_Minion):
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return target == self.entity and self.entity.Game.spaceonBoard(self.entity.ID) > 0
	#这个变形亡语只能触发一次。
	def trigger(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self, "Deathrattle: Turn into Spirit of Lucentbark triggers")
		permanent = SpiritofLucentbark(self.entity.Game, self.entity.ID)
		self.entity.Game.transform(self.entity, permanent)
		
class SpiritofLucentbark(Permanent):
	Class, name = "Druid", "Spirit of Lucentbark"
	description = "Restore 5 Health to awaken"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.progress = 0
		self.triggersonBoard = [Trigger_SpiritofLucentbark(self)]
		self.originalMinion = Lucentbark
		
class Trigger_SpiritofLucentbark(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionGetsHealed", "HeroGetsHealed"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject.ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self, "Player restores %d Health, and %s's counter records it."%(number, self.entity.name))
		self.entity.progress += number
		if self.entity.progress > 4:
			PRINT(self, "Spirit of Lucentbark transforms into Lucentbark")
			self.entity.Game.transform(self.entity, Lucentbark(self.entity.Game, self.entity.ID))
			
			
class TheForestsAid(Spell):
	Class, name = "Druid", "The Forest's Aid"
	requireTarget, mana = False, 8
	index = "Shadows~Druid~Spell~8~The Forest's Aid~Twinspell"
	description = "Twinspell. Summon five 2/2 Treants"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.twinSpell = 1
		self.twinSpellCopy = theforestsaid
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		PRINT(self, "Twinspell The Forest's Aid is played and summons five 2/2 Treants.")
		self.Game.summonMinion([Treant_Shadows(self.Game, self.ID) for i in range(5)], (-1, "totheRightEnd"), self.ID)
		return None
		
class theforestsaid(Spell):
	Class, name = "Druid", "The Forest's Aid"
	requireTarget, mana = False, 8
	index = "Shadows~Druid~Spell~8~The Forest's Aid~Uncollectible"
	description = "Summon five 2/2 Treants"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		PRINT(self, "The Forest's Aid is played and summons five 2/2 Treants.")
		self.Game.summonMinion([Treant_Shadows(self.Game, self.ID) for i in range(5)], (-1, "totheRightEnd"), self.ID)
		return None
		
class Treant_Shadows(Minion):
	Class, race, name = "Druid", "", "Treant"
	mana, attack, health = 2, 2, 2
	index = "Shadows~Druid~Minion~2~2~2~None~Treant~Uncollectible"
	requireTarget, keyWord, description = False, "", ""
	
"""Hunter cards"""
class RapidFire(Spell):
	Class, name = "Hunter", "Rapid Fire"
	requireTarget, mana = True, 1
	index = "Shadows~Hunter~Spell~1~Rapid Fire~Twinspell"
	description = "Twinspell. Deal 1 damage"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.twinSpell = 1
		self.twinSpellCopy = rapidfire
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if target != None:
			damage = (1 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			PRINT(self, "Twinspell Rapid Fire is cast and deals %d damage to %s"%(damage, target.name))
			self.dealsDamage(target, damage)
		return target
		
class rapidfire(Spell):
	Class, name = "Hunter", "Rapid Fire"
	requireTarget, mana = True, 1
	index = "Shadows~Hunter~Spell~1~Rapid Fire~Uncollectible"
	description = "Deal 1 damage"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if target != None:
			damage = (1 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			PRINT(self, "Rapid Fire is cast and deals %d damage to %s"%(damage, target.name))
			self.dealsDamage(target, damage)
		return target
			
			
class Shimmerfly(Minion):
	Class, race, name = "Hunter", "Beast", "Shimmerfly"
	mana, attack, health = 1, 1, 1
	index = "Shadows~Hunter~Minion~1~1~1~Beast~Shimmerfly~Deathrattle"
	requireTarget, keyWord, description = False, "", "Deathrattle: Add a random Hunter spell to your hand"
	poolIdentifier = "Hunter Spells"
	@classmethod
	def generatePool(cls, Game):
		hunterSpells = []
		for key, value in Game.ClassCards["Hunter"].items():
			if "~Spell~" in key:
				hunterSpells.append(value)
		return "Hunter Spells", hunterSpells
		
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [AddaHunterSpelltoHand(self)]
		
class AddaHunterSpelltoHand(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		if self.entity.Game.Hand_Deck.handNotFull(self.entity.ID):
			PRINT(self, "Deathrattle: Summon a random Hunter spell to your hand triggers.")
			self.entity.Game.Hand_Deck.addCardtoHand(np.random.choice(self.entity.Game.RNGPools["Hunter Spells"]), self.entity.ID, "CreateUsingType")
			
			
class NineLives(Spell):
	Class, name = "Hunter", "Nine Lives"
	requireTarget, mana = False, 3
	index = "Shadows~Hunter~Spell~3~Nine Lives"
	description = "Discover a friendly Deathrattle minion that died this game. Also trigger its Deathrattle"
	
	def randomorDiscover(self):
		return "Discover"
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if self.Game.Hand_Deck.handNotFull(self.ID):
			deathrattleMinions, deathrattleIndices = [], []
			for index in self.Game.CounterHandler.minionsDiedThisGame[self.ID]:
				if "~Deathrattle" in index and "~Minion~" in index and index not in deathrattleIndices:
					deathrattleMinions.append(index)
					
			if deathrattleMinions != []:
				if len(deathrattleMinions) == 1:
					PRINT(self, "There is only one friendly Deathrattle minion that died this game, and Nine Lives adds it to player's hand and triggers its deathrattles")
					minion = self.Game.cardPool[deathrattleMinions[0]](self.Game, self.ID)
					self.Game.Hand_Deck.addCardtoHand(minion, self.ID)
					for trigger in minion.deathrattles:
						trigger.trigger("DeathrattleTriggers", self.ID, None, minion, minion.attack, "")
				else:
					if "CastbyOthers" in comment:
						PRINT(self, "Nine Lives is cast and adds a random friendly Deathrattle minion that died this game")
						minion = self.Game.cardPool[np.random.choice(deathrattleMinions)](self.Game, self.ID)
						self.Game.Hand_Deck.addCardtoHand(minion, self.ID)
						PRINT(self, "Nine Lives triggers the Deathrattle of the minion %s added to hand"%minion.name)
						for trigger in minion.deathrattles:
							trigger.trigger("DeathrattleTriggers", self.ID, None, minion, minion.attack, "")
					else:
						PRINT(self, "Nine Lives is cast and lets player discover adds a random friendly Deathrattle minion that died this game")
						minions = np.random.choice(deathrattleMinions, min(3, len(deathrattleMinions)), replace=False)
						self.Game.options = [self.Game.cardPool[minion](self.Game, self.ID) for minion in minions]
						self.Game.DiscoverHandler.startDiscover(self)
		return None
		
	def discoverDecided(self, option):
		PRINT(self, "Deathrattle minion %s is put into player's hand."%option.name)
		self.Game.Hand_Deck.addCardtoHand(option, self.ID)
		self.Game.sendSignal("DiscoveredCardPutintoHand", self.ID, self, option, 0, "")
		for trigger in option.deathrattles:
			trigger.trigger("DeathrattleTriggers", self.ID, None, option, option.attack, "")
			
			
class Ursatron(Minion):
	Class, race, name = "Hunter", "Mech", "Ursatron"
	mana, attack, health = 3, 3, 3
	index = "Shadows~Hunter~Minion~3~3~3~Mech~Ursatron~Deathrattle"
	requireTarget, keyWord, description = False, "", "Deathrattle: Draw a Mech from your deck"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [DrawaMech(self)]
		
class DrawaMech(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self, "Deathrattle: Draw a Mech from your deck triggers")
		mechs = []
		for card in self.entity.Game.Hand_Deck.decks[self.entity.ID]:
			if card.cardType == "Minion" and "Mech" in card.race:
				mechs.append(card)
				
		if mechs != []:
			self.entity.Game.Hand_Deck.drawCard(self.entity.ID, np.random.choice(mechs))
			
			
class ArcaneFletcher(Minion):
	Class, race, name = "Hunter", "", "Arcane Fletcher"
	mana, attack, health = 4, 3, 3
	index = "Shadows~Hunter~Minion~4~3~3~None~Arcane Fletcher"
	requireTarget, keyWord, description = False, "", "Whenever you play a 1-Cost minion, draw a spell from your deck"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_ArcaneFletcher(self)]
		
class Trigger_ArcaneFletcher(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionPlayed"])
	#The number here is the mana used to play the minion
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject != self.entity and subject.ID == self.entity.ID and number == 1
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self, "A 1-Cost friendly minion %s is played and %s lets player draw a spell from the deck."%(subject.name, self.entity.name))
		spellsinDeck = []
		for card in self.entity.Game.Hand_Deck.decks[self.entity.ID]:
			if card.cardType == "Spell":
				spellsinClass.append(card)
		if spellsinDeck != []:
			spell = np.random.choice(spellsinDeck)
			self.entity.Game.Hand_Deck.drawCard(self.entity.ID, spell)
			
			
class MarkedShot(Spell):
	Class, name = "Hunter", "Marked Shot"
	requireTarget, mana = True, 4
	index = "Shadows~Hunter~Spell~4~Marked Shot"
	description = "Deal 4 damage to a minion. Discover a Spell"
	poolIdentifier = "Hunter Spells"
	@classmethod
	def generatePool(cls, Game):
		classes, lists = [], []
		for Class in Classes:
			classes.append(Class+" Spells")
			spellsinClass = []
			for key, value in Game.ClassCards[Class].items():
				if "~Spell~" in key:
					spellsinClass.append(value)
			lists.append(spellsinClass)
		return classes, lists
		
	def randomorDiscover(self):
		return "Discover"
		
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if target != None:
			damage = (4 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			PRINT(self, "Marked Shot is cast and deals %d damage to %s"%(damage, target.name))
			self.dealsDamage(target, damage)
			if self.Game.Hand_Deck.handNotFull(self.ID):
				key = classforDiscover(self)+" Spells"
				if "CastbyOthers" in comment:
					PRINT(self, "Marked Shot is cast and adds a random spell to player's hand")
					self.Game.Hand_Deck.addCardtoHand(np.random.choice(self.Game.RNGPools[key]), self.ID, "CreateUsingType")
				else:
					PRINT(self, "Marked Shot lets player discover a spell")
					spells = np.random.choice(self.Game.RNGPools[key], 3, replace=False)
					self.Game.options = [spell(self.Game, self.ID) for spell in spells]
					self.Game.DiscoverHandler.startDiscover(self)
					
		return target
		
	def discoverDecided(self, option):
		PRINT(self, "Spell %s is put into player's hand."%option.name)
		self.Game.Hand_Deck.addCardtoHand(option, self.ID)
		self.Game.sendSignal("DiscoveredCardPutintoHand", self.ID, self, option, 0, "")
		
		
class HuntingParty(Spell):
	Class, name = "Hunter", "Hunting Party"
	requireTarget, mana = False, 5
	index = "Shadows~Hunter~Spell~5~Hunting Party"
	description = "Copy all Beasts in your hand"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		PRINT(self, "Hunting Party is cast and copies all Beasts in player's hand.")
		if self.Game.Hand_Deck.handNotFull(self.ID):
			copies = []
			for card in self.Game.Hand_Deck.hands[self.ID]:
				if card.cardType == "Minion" and "Beast" in card.race:
					copies.append(card.selfCopy(self.ID))
					
			for Copy in copies:
				self.Game.Hand_Deck.addCardtoHand(Copy, self.ID)
		return None
		
class Oblivitron(Minion):
	Class, race, name = "Hunter", "Mech", "Oblivitron"
	mana, attack, health = 6, 3, 4
	index = "Shadows~Hunter~Minion~6~3~4~Mech~Oblivitron~Deathrattle~Legendary"
	requireTarget, keyWord, description = False, "", "Deathrattle: Summon a Mech from your hand and trigger its Deathrattle"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [SummonMechfromHandandTriggeritsDeathrattle(self)]
		
class SummonMechfromHandandTriggeritsDeathrattle(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self, "Deathrattle: Summon a Mech from your hand and trigger its Deathrattle triggers")
		mechs = []
		for card in self.entity.Game.Hand_Deck.hands[self.entity.ID]:
			if "~Mech~" in card.index:
				mechs.append(card)
				
		if mechs != [] and self.entity.Game.spaceonBoard(self.entity.ID) > 0:
			mech = np.random.choice(mechs)
			self.entity.Game.summonfromHand(mech, self.entity.position+1, self.entity.ID)
			#Deathrattle triggered by others.
			for trigger in mech.deathrattles:
				trigger.trigger("DeathrattleTriggers", self.entity.ID, None, mech, mech.attack, "")
				
				
class UnleashtheBeast(Spell):
	Class, name = "Hunter", "Unleash the Beast"
	requireTarget, mana = False, 6
	index = "Shadows~Hunter~Spell~6~Unleash the Beast~Twinspell"
	description = "Twinspell. Summon a 5/5 Wyvern with Rush"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.twinSpell = 1
		self.twinSpellCopy = unleashthebeast
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		PRINT(self, "Twinspell Unleash the Beast is cast and summons a 5/5 Wyvern.")
		self.Game.summonMinion(Wyvern(self.Game, self.ID), -1, self.ID)
		return None
		
class unleashthebeast(Spell):
	Class, name = "Hunter", "Unleash the Beast"
	requireTarget, mana = False, 6
	index = "Shadows~Hunter~Spell~6~Unleash the Beast~Uncollectible"
	description = "Summon a 5/5 Wyvern with Rush"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		PRINT(self, "Unleash the Beast is cast and summons a 5/5 Wyvern.")
		self.Game.summonMinion(Wyvern(self.Game, self.ID), -1, self.ID)
		return None
		
class Wyvern(Minion):
	Class, race, name = "Hunter", "Beast", "Wyvern"
	mana, attack, health = 5, 5, 5
	index = "Shadows~Hunter~Minion~5~5~5~Beast~Wyvern~Rush~Uncollectible"
	requireTarget, keyWord, description = False, "Rush", "Rush"
	
	
class VereesaWindrunner(Minion):
	Class, race, name = "Hunter", "", "Vereesa Windrunner"
	mana, attack, health = 7, 5, 6
	index = "Shadows~Hunter~Minion~7~5~6~None~Vereesa Windrunner~Battlecry~Legendary"
	requireTarget, keyWord, description = False, "", "Battlecry: Equip Thori'dal, the Stars' Fury"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		PRINT(self, "Vereesa Windrunner's battlecry equips Thori'dal, the Stars' Fury.")
		self.Game.equipWeapon(ThoridaltheStarsFury(self.Game, self.ID))
		return None
		
class ThoridaltheStarsFury(Weapon):
	Class, name, description = "Hunter", "Thori'dal, the Stars' Fury", "After your hero attacks, gain Spell Damage +2 this turn"
	mana, attack, durability = 3, 2, 3
	index = "Shadows~Hunter~Weapon~3~2~3~Thori'dal, the Stars' Fury~Legendary~Uncollectible"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_ThoridaltheStarsFury(self)]
		
class Trigger_ThoridaltheStarsFury(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["BattleFinished"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return subject == self.entity.Game.heroes[self.entity.ID] and self.entity.onBoard
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self, "After player attacks, Thori'dal, the Stars' Fury gives gives player Spell Damage +2 this turn.")
		self.entity.Game.playerStatus[self.entity.ID]["Spell Damage"] += 2
		self.Game.turnEndTrigger.append(SpellDamagePlus2Disappears(self.Game, self.ID))
		
class SpellDamagePlus2Disappears:
	def __init__(self, Game, ID):
		self.Game, self.ID = Game, ID
		
	def turnEndTrigger(self):
		PRINT(self, "At the end of turn, Thori'dal, the Stars' Fury's effect expires and player no longer has Spell Damage +2")
		self.Game.playerStatus[self.ID]["Spell Damage"] -= 2
		extractfrom(self, self.Game.turnEndTrigger)
		
	def selfCopy(self, recipientGame):
		return type(self)(recipientGame, self.ID)
		
		
"""Mage cards"""
class RayofFrost(Spell):
	Class, name = "Mage", "Ray of Frost"
	requireTarget, mana = True, 1
	index = "Shadows~Mage~Spell~1~Ray of Frost~Twinspell"
	description = "Twinspell. Freeze a minion. If it's already Frozen, deal 2 damage to it"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.twinSpell = 1
		self.twinSpellCopy = rayoffrost
		
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if target != None:
			if target.status["Frozen"]:
				damage = (2 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
				PRINT(self, "Twinspell Ray of Frost is cast and deals %d damage to the already Frozen minion %s"%(damage, target.name))
				self.dealsDamage(target, damage)
			else:
				PRINT(self, "Twinspell Ray of Frost is cast and Freezes minion %s"%target.name)
				target.getsFrozen()
		return target
		
class rayoffrost(Spell):
	Class, name = "Mage", "Ray of Frost"
	requireTarget, mana = True, 1
	index = "Shadows~Mage~Spell~1~Ray of Frost~Uncollectible"
	description = "Freeze a minion. If it's already Frozen, deal 2 damage to it"
	
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if target != None:
			if target.status["Frozen"]:
				damage = (2 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
				PRINT(self, "Ray of Frost is cast and deals %d damage to the already Frozen minion %s"%(damage, target.name))
				self.dealsDamage(target, damage)
			else:
				PRINT(self, "Ray of Frost is cast and Freezes minion %s"%target.name)
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
	index = "Shadows~Mage~Minion~2~2~2~None~Khadgar~Legendary"
	requireTarget, keyWord, description = False, "", "Your cards that summon minions summon twice as many"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.appearResponse = [self.activateAura]
		self.disappearResponse = [self.deactivateAura]
		self.silenceResponse = [self.deactivateAura]
		
	def activateAura(self):
		PRINT(self, "Khadgar's aura is registered. Player %d's cards' summoning effects now summon twice as many."%self.ID)
		self.Game.playerStatus[self.ID]["Double Summoning by Cards"] += 1
		
	def deactivateAura(self):
		PRINT(self, "Khadgar's aura is removed. Player %d's cards' summoning effects no longer summon twice as many."%self.ID)
		self.Game.playerStatus[self.ID]["Double Summoning by Cards"] -= 1
		
		
class MagicDartFrog(Minion):
	Class, race, name = "Mage", "Beast", "Magic Dart Frog"
	mana, attack, health = 2, 1, 3
	index = "Shadows~Mage~Minion~2~1~3~Beast~Magic Dart Frog"
	requireTarget, keyWord, description = False, "", "After you cast a spell, deal 1 damage to a random enemy minion"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_MagicDartFrog(self)]
		
class Trigger_MagicDartFrog(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["SpellBeenPlayed"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject.ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		targets = self.entity.Game.minionsAlive(3-self.entity.ID)
		if targets != []:
			target = np.random.choice(targets)
			PRINT(self, "After player casts a spell, %s deals 1 damage to a random enemy minion."%self.entity.name)
			self.entity.dealsDamage(target, 1)
			
			
class MessengerRaven(Minion):
	Class, race, name = "Mage", "Beast", "Messenger Raven"
	mana, attack, health = 3, 3, 2
	index = "Shadows~Mage~Minion~3~3~2~Beast~Messenger Raven~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Discover a Mage minion"
	poolIdentifier = "Mage Minions"
	@classmethod
	def generatePool(cls, Game):
		mageMinions = []
		for key, value in Game.ClassCards["Mage"].items():
			if "~Minion~" in key:
				mageMinions.append(value)
		return "Mage Minions", mageMinions
		
	def randomorDiscover(self):
		return "Discover"
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if self.ID == self.Game.turn and self.Game.Hand_Deck.handNotFull(self.ID):
			if "InvokedbyOthers" in comment:
				PRINT(self, "Messenger Raven's battlecry adds random Mage minion to player's hand.")
				self.Game.Hand_Deck.addCardtoHand(np.random.choice(self.Game.RNGPools["Mage Minions"]), self.ID, "CreateUsingType")
			else:
				PRINT(self, "Messenger Raven's battlecry lets player discover a Mage minion.")
				minions = np.random.choice(self.Game.RNGPools["Mage Minions"], 3, replace=False)
				self.Game.options = [minion(self.Game, self.ID) for minion in minions]
				self.Game.DiscoverHandler.startDiscover(self)
				
		return None
		
	def discoverDecided(self, option):
		PRINT(self, "Mage minion %s is put into player's hand."%option.name)
		self.Game.Hand_Deck.addCardtoHand(option, self.ID)
		self.Game.sendSignal("DiscoveredCardPutintoHand", self.ID, self, option, 0, "")
		
		
class MagicTrick(Spell):
	Class, name = "Mage", "Magic Trick"
	requireTarget, mana = False, 1
	index = "Shadows~Mage~Spell~1~Magic Trick"
	description = "Discover a spell that costs (3) or less"
	poolIdentifier = "Spells 3-Cost or less as Mage"
	@classmethod
	def generatePool(cls, Game):
		classes, lists = [], []
		#职业为中立时，随机挑选一个职业进行发现
		for Class in Classes:
			classes.append("Spells 3-Cost or less as " + Class)
			spells = []
			for key, value in Game.ClassCards[Class].items():
				strs = key.split('~')
				if strs[2] == "Spell" and int(strs[3]) < 4:
					spells.append(value)
			lists.append(spells)
			
		return classes, lists #返回的包含“Class Cards except Hunter”等identifier的列表和其他职业卡表
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if self.Game.Hand_Deck.handNotFull(self.ID):
			key = "Spells 3-Cost or less as "+classforDiscover(self)
			if "CastbyOthers" in comment:
				PRINT(self, "Magic Trick adds a random spell that costs 3 or less to player's hand.")
				self.Game.Hand_Deck.addCardtoHand(np.random.choice(self.Game.RNGPools[key]), self.ID, "CreateUsingType")
			else:
				PRINT(self, "Magic Trick lets player discover a spell that cost 3 or less.")
				spells = np.random.choice(self.Game.RNGPools[key], 3, replace=False)
				self.Game.options = [spell(self.Game, self.ID) for spell in spells]
				self.Game.DiscoverHandler.startDiscover(self)
				
		return None
		
	def discoverDecided(self, option):
		PRINT(self, "Spell %s is put into player's hand."%option.name)
		self.Game.Hand_Deck.addCardtoHand(option, self.ID)
		self.Game.sendSignal("DiscoveredCardPutintoHand", self.ID, self, option, 0, "")
		
		
class ConjurersCalling(Spell):
	Class, name = "Mage", "Conjurer's Calling"
	requireTarget, mana = True, 4
	index = "Shadows~Mage~Spell~4~Conjurer's Calling~Twinspell"
	description = "Twinspell. Destroy a minion. Summon 2 minions of the same Cost to replace it"
	poolIdentifier = "1-Cost Minions to Summon"
	@classmethod
	def generatePool(cls, Game):
		costs, lists = [], []
		for cost in Game.MinionsofCost.keys():
			costs.append("%d-Cost Minions to Summon"%cost)
			lists.append(list(Game.MinionsofCost[cost].values()))
		return costs, lists
		
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.twinSpell = 1
		self.twinSpellCopy = conjurerscalling
		
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.onBoard
	#首先记录随从当前场上位置，强制死亡然后检测当前场上情况，然后在相同位置上召唤两个随从
	#例如，自爆绵羊在生效前是场上第3个随从，强制死亡并结算所有死亡情况之后，在场上的第3个位置召唤两个随从（即第2个随从的右边）
	#如果位置溢出，则直接召唤到场上的最右边。
	#当与风潮配合而生效两次的时候，第一次召唤随从是在原来的位置，之后的召唤是在最右边。说明第二次生效时目标已经被初始化，失去了原有的位置信息。
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if target != None:
			cost = type(target).mana
			key = "%d-Cost Minions to Summon"%cost
			PRINT(self, "Twinspell Conjurer's Calling is cast, destroys minion %s and summons two minions with the same cost"%target.name, cost)
			targetID, position = target.ID, target.position
			self.Game.destroyMinion(target) #如果随从在手牌中则将其丢弃
			#强制死亡需要在此插入死亡结算，并让随从离场
			self.Game.gathertheDead()
			minions = np.random.choice(self.Game.RNGPools[key], 2, replace=True)
			if position == 0:
				pos = (-1, "totheRight") #Summon to the leftmost
			#如果目标之前是第4个(position=3)，则场上最后只要有3个随从或者以下，就会召唤到最右边。
			#如果目标不在场上或者是第二次生效时已经死亡等被初始化，则position=-2会让新召唤的随从在场上最右边。
			elif position < 0 or position >= len(self.Game.minionsonBoard(targetID)):
				pos = (-1, "totheRightEnd")
			else:
				pos = (position, "totheRight")
			self.Game.summonMinion([minion(self.Game, target.ID) for minion in minions], pos, self.ID)
		return target
		
class conjurerscalling(Spell):
	Class, name = "Mage", "Conjurer's Calling"
	requireTarget, mana = True, 4
	index = "Shadows~Mage~Spell~4~Conjurer's Calling~Uncollectible"
	description = "Destroy a minion. Summon 2 minions of the same Cost to replace it"
	
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if target != None:
			cost = type(target).mana
			key = "%d-Cost Minions"%cost
			PRINT(self, "Twinspell Conjurer's Calling is cast, destroys minion %s and summons two minions with the same cost"%target.name, cost)
			targetID, position = target.ID, target.position
			self.Game.destroyMinion(target) #如果随从在手牌中则将其丢弃
			#强制死亡需要在此插入死亡结算，并让随从离场
			self.Game.gathertheDead()
			minions = np.random.choice(self.Game.RNGPools[key], 2, replace=True)
			if position == 0:
				pos = (-1, "totheRight") #Summon to the leftmost
			#如果目标之前是第4个(position=3)，则场上最后只要有3个随从或者以下，就会召唤到最右边。
			#如果目标不在场上或者是第二次生效时已经死亡等被初始化，则position=-2会让新召唤的随从在场上最右边。
			elif position < 0 or position >= len(self.Game.minionsonBoard(targetID)):
				pos = (-1, "totheRightEnd")
			else:
				pos = (position, "totheRight")
			self.Game.summonMinion([minion(self.Game, target.ID) for minion in minions], pos, self.ID)
		return target
		
		
class KirinTorTricaster(Minion):
	Class, race, name = "Mage", "", "Kirin Tor Tricaster"
	mana, attack, health = 4, 3, 3
	index = "Shadows~Mage~Minion~4~3~3~None~Kirin Tor Tricaster"
	requireTarget, keyWord, description = False, "", "Spell Damage +3. Your spells cost (1) more"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.keyWords["Spell Damage"] = 3
		self.auras["Mana Aura"] = ManaAura_Dealer(self, self.manaAuraApplicable, +1, -1)
		
	def manaAuraApplicable(self, subject):
		return subject.ID == self.ID and subject.cardType == "Spell"
		
		
class ManaCyclone(Minion):
	Class, race, name = "Mage", "Elemental", "Mana Cyclone"
	mana, attack, health = 2, 2, 2
	index = "Shadows~Mage~Minion~2~2~2~Elemental~Mana Cyclone~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: For each spell you've cast this turn, add a random Mage spell to your hand"
	poolIdentifier = "Mage Spells"
	@classmethod
	def generatePool(cls, Game):
		mageSpells = []
		for key, value in Game.ClassCards["Mage"].items():
			if "~Spell~" in key:
				mageSpells.append(value)
		return "Mage Spells", mageSpells
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		PRINT(self, "Mana Cyclone's battlecry adds a random Mage spell into player's hand for each spell played this turn.")
		spells = np.random.choice(self.Game.RNGPools["Mage Spells"], self.Game.CounterHandler.numSpellsPlayedThisTurn[self.ID], replace=True)
		self.Game.Hand_Deck.addCardtoHand(spells, self.ID, "CreateUsingType")
		return None
		
		
class PowerofCreation(Spell):
	Class, name = "Mage", "Power of Creation"
	requireTarget, mana = False, 8
	index = "Shadows~Mage~Spell~8~Power of Creation"
	description = "Discover a 6-Cost minion. Summon two copies of it"
	poolIdentifier = "6-Cost Minions as Mage to Summon"
	@classmethod
	def generatePool(cls, Game):
		classes, lists, neutralCards = [], [], []
		classCards = {"Neutral": [], "Demon Hunter":[], "Druid":[], "Mage":[], "Hunter":[], "Paladin":[],
						"Priest":[], "Rogue":[], "Shaman":[], "Warlock":[], "Warrior":[]}
		for key, value in Game.MinionsofCost[6].items():
			classCards[key.split('~')[1]].append(value)
			
		for Class in Classes:
			classes.append("6-Cost Minions as %s to Summon"%Class)
			lists.append(classCards[Class]+classCards["Neutral"])
		return classes, lists #返回的包含“Class Cards except Hunter”等identifier的列表和其他职业卡表
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		PRINT(self, "Power of Creation is cast, player discovers a 6-Cost minion and summon two copies of it.")
		key = "6-Cost Minions as %s to Summon"%classforDiscover(self)
		if self.Game.spaceonBoard(self.ID) > 0:
			if "CastbyOthers" in comment:
				PRINT(self, "Power of Creation summons two copies of a random 6-Cost minion.")
				minion = np.random.choice(self.Game.RNGPools[key])
				self.Game.summonMinion([minion(self.Game, self.ID) for i in range(2)], (-1, "totheRightEnd"), self.ID)
			else:
				minions = np.random.choice(self.Game.RNGPools[key], 3, replace=False)
				self.Game.options = [minion(self.Game, self.ID) for minion in minions]
				PRINT(self, "Power of creation lets player discover a 6-Cost minion to summon two copies.")
				self.Game.DiscoverHandler.startDiscover(self)
		return None
		
	def discoverDecided(self, option):
		PRINT(self, "Power of Creation summons two copies of discovered 6-Cost minion %s"%option.name)
		self.Game.summonMinion([option, type(option)(self.Game, self.ID)], (-1, "totheRightEnd"), self.ID)
		
		
class Kalecgos(Minion):
	Class, race, name = "Mage", "Dragon", "Kalecgos"
	mana, attack, health = 10, 4, 12
	index = "Shadows~Mage~Minion~10~4~12~Dragon~Kalecgos~Legendary"
	requireTarget, keyWord, description = False, "", "Your first spell costs (0) each turn. Battlecry: Discover a spell"
	poolIdentifier = "Mage Spells"
	@classmethod
	def generatePool(cls, Game):
		classes, lists = [], []
		for Class in Classes:
			classes.append(Class+" Spells")
			spellsinClass = []
			for key, value in Game.ClassCards[Class].items():
				if "~Spell~" in key:
					spellsinClass.append(value)
			lists.append(spellsinClass)
		return classes, lists
		
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.auras["Mana Aura"] = ManaAura_Dealer(self, self.manaAuraApplicable, changeby=0, changeto=0)
		self.triggersonBoard = [Trigger_Kalecgos(self)]
		#随从的光环启动在顺序上早于appearResponse,关闭同样早于disappearResponse
		self.appearResponse = [self.checkAuraCorrectness]
		self.disappearResponse = [self.deactivateAura]
		self.silenceResponse = [self.deactivateAura]
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if self.ID == self.Game.turn and self.Game.Hand_Deck.handNotFull(self.ID):
			key = classforDiscover(self)+" Spells"
			if "InvokedbyOthers" in comment:
				PRINT(self, "Kalecgos' battlecry adds a random spell to player's hand")
				self.Game.Hand_Deck.addCardtoHand(np.random.choice(self.Game.RNGPools[key]), self.ID, "CreateUsingType")
			else:
				PRINT(self, "Kalecgos's battlecry lets player discover a spell")
				spells = np.random.choice(self.Game.RNGPools[key], 3, replace=False)
				self.Game.options = [spell(self.Game, self.ID) for spell in spells]
				self.Game.DiscoverHandler.startDiscover(self)
				
		return None
		
	def discoverDecided(self, option):
		PRINT(self, "Spell %s is put into player's hand."%option.name)
		self.Game.Hand_Deck.addCardtoHand(option, self.ID)
		self.Game.sendSignal("DiscoveredCardPutintoHand", self.ID, self, option, 0, "")
		
	def manaAuraApplicable(self, subject):
		return subject.ID == self.ID and subject.cardType == "Spell"
		
	def checkAuraCorrectness(self): #负责光环在随从登场时无条件启动之后的检测。如果光环的启动条件并没有达成，则关掉光环
		if self.Game.turn != self.ID or self.Game.CounterHandler.numSpellsPlayedThisTurn[self.ID] != 0:
			PRINT(self, "Kalecgos's mana aura is incorrectly activated. It will be shut down")
			self.auras["Mana Aura"].auraDisappears()
			
	def deactivateAura(self):
		PRINT(self, "Kalecgos's mana aura is removed. Player's first spell each turn no longer costs (0).")
		self.auras["Mana Aura"].auraDisappears()
		
#法术反制实际上不会消耗卡雷苟斯的光环，但是会消耗暮陨者艾维娜的光环，但是在此统一为会消耗。卡雷苟斯的光环显然是程序员自己没有参考之前的同类型光环然后自己写的。
class Trigger_Kalecgos(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["TurnStarts", "TurnEnds", "ManaCostPaid"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		if "Turn" in signal and self.entity.onBoard:
			return True
		if signal == "ManaCostPaid" and self.entity.onBoard and subject.cardType == "Spell" and subject.ID == self.entity.ID:
			return True
		return False
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		if "Turn" in signal: #回合开始结束时总会强制关闭然后启动一次光环。这样，即使回合开始或者结束发生了随从的控制变更等情况，依然可以保证光环的正确
			PRINT(self, "At the start/end of turn, %s attempts to restarts the mana aura and reduces the cost of the first card to (0)."%self.entity.name)
			self.entity.auras["Mana Aura"].auraDisappears()
			self.entity.auras["Mana Aura"].auraAppears()
			self.entity.checkAuraCorrectness()
		else: #signal == "ManaCostPaid" or signal == "TurnEnds"
			self.entity.auras["Mana Aura"].auraDisappears()
			
			
class NeverSurrender(Secret):
	Class, name = "Paladin", "Never Surrender!"
	requireTarget, mana = False, 1
	index = "Shadows~Paladin~Spell~1~Never Surrender!~~Secret"
	description = "Whenever your opponent casts a spell, give your minions +2 Health"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_NeverSurrender(self)]
		
class Trigger_NeverSurrender(SecretTrigger):
	def __init__(self, entity):
		self.blank_init(entity, ["SpellPlayed"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.ID != self.entity.Game.turn and subject.ID != self.entity.ID and self.entity.Game.minionsonBoard(self.entity.ID) != []
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self, "When the opponent casts a spell, Secret Never Surrender! is triggered and gives friendly minions +2 Health.")
		for minion in self.entity.Game.minionsonBoard(self.entity.ID):
			minion.buffDebuff(0, 2)
			
			
class LightforgedBlessing(Spell):
	Class, name = "Paladin", "Lightforged Blessing"
	requireTarget, mana = True, 2
	index = "Shadows~Paladin~Spell~2~Lightforged Blessing~Twinspell"
	description = "Twinspell. Give a friendly minion Lifesteal"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.twinSpell = 1
		self.twinSpellCopy = lightforgedblessing
		
	def available(self):
		return self.selectableFriendlyMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.ID == self.ID and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if target != None:
			PRINT(self, "Twinspell Lightforged Blessing is cast and gives a friendly minion Lifesteal.")
			target.getsKeyword("Lifesteal")
		return target
		
class lightforgedblessing(Spell):
	Class, name = "Paladin", "Lightforged Blessing"
	requireTarget, mana = True, 2
	index = "Shadows~Paladin~Spell~2~Lightforged Blessing~Uncollectible"
	description = "Give a friendly minion Lifesteal"
	
	def available(self):
		return self.selectableFriendlyMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.ID == self.ID and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if target != None:
			PRINT(self, "Lightforged Blessing is cast and gives a friendly minion Lifesteal.")
			target.getsKeyword("Lifesteal")
		return target
		
		
class BronzeHerald(Minion):
	Class, race, name = "Paladin", "Dragon", "Bronze Herald"
	mana, attack, health = 3, 3, 2
	index = "Shadows~Paladin~Minion~3~3~2~Dragon~Bronze Herald~Deathrattle"
	requireTarget, keyWord, description = False, "", "Deathrattle: Add two 4/4 Dragons to your hand"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [AddTwoBronzeDragonstoHand(self)]
		
class AddTwoBronzeDragonstoHand(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self, "Deathrattle: Add Two 4/4 Bronze Dragons to hand triggers.")
		self.entity.Game.Hand_Deck.addCardtoHand([BronzeDragon, BronzeDragon], self.entity.ID, "CreateUsingType")
		
class BronzeDragon(Minion):
	Class, race, name = "Paladin", "Dragon", "Bronze Dragon"
	mana, attack, health = 4, 4, 4
	index = "Shadows~Paladin~Minion~4~4~4~Dragon~Bronze Dragon~Uncollectible"
	requireTarget, keyWord, description = False, "", ""
	
	
class DesperateMeasures(Spell):
	Class, name = "Paladin", "Desperate Measures"
	requireTarget, mana = False, 1
	index = "Shadows~Paladin~Spell~1~Desperate Measures~Twinspell"
	description = "Twinspell. Cast a random Paladin Secrets"
	poolIdentifier = "Paladin Secrets"
	@classmethod
	def generatePool(cls, Game):
		paladinSecrets = []
		for key, value in Game.ClassCards["Paladin"].items():
			if "~~Secret" in key:
				paladinSecrets.append(value)
		return "Paladin Secrets", paladinSecrets
		
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.twinSpell = 1
		self.twinSpellCopy = desperatemeasures
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		PRINT(self, "Twinspell Desperate Measures is cast and casts a random Paladin Secret.")
		secrets = []
		for value in self.Game.RNGPools["Paladin Secrets"]:
			if self.Game.SecretHandler.isSecretDeployedAlready(value, self.ID) == False:
				secrets.append(value)
				
		if secrets != []:
			np.random.choice(secrets)(self.Game, self.ID).cast()
		return None
		
class desperatemeasures(Spell):
	Class, name = "Paladin", "Desperate Measures"
	requireTarget, mana = False, 1
	index = "Shadows~Paladin~Spell~1~Desperate Measures~Uncollectible"
	description = "Cast a random Paladin Secrets"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		PRINT(self, "Desperate Measures is cast and casts a random Paladin Secret.")
		secrets = []
		for value in self.Game.RNGPools["Paladin Secrets"]:
			if self.Game.SecretHandler.isSecretDeployedAlready(value, self.ID) == False:
				secrets.append(value)
		
		if secrets != []:
			np.random.choice(secrets)(self.Game, self.ID).cast()
		return None
		
		
class MysteriousBlade(Weapon):
	Class, name, description = "Paladin", "Mysterious Blade", "Battlecry: If you control a Secret, gain +1 Attack"
	mana, attack, durability = 2, 2, 2
	index = "Shadows~Paladin~Weapon~2~2~2~Mysterious Blade~Battlecry"
	def effectCanTrigger(self):
		self.effectViable = self.Game.SecretHandler.secrets[self.ID] != []
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if self.Game.SecretHandler.secrets[self.ID] != []:
			PRINT(self, "Mysterious Blade's battlecry gives weapon +1 attack.")
			self.gainStat(1, 0)
		return None
		
		
class CalltoAdventure(Spell):
	Class, name = "Paladin", "Call to Adventure"
	requireTarget, mana = False, 3
	index = "Shadows~Paladin~Spell~3~Call to Adventure"
	description = "Draw the lowest Cost minion from your deck. Give it +2/+2"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		PRINT(self, "Call to Adventure is cast. Player draws the lowest Cost card from deck, and it gains +2/+2.")
		minionsinDeck = []
		lowestCost = np.inf
		for card in self.Game.Hand_Deck.decks[self.ID]:
			if card.cardType == "Minion":
				if card.mana < lowestCost:
					minionsinDeck = [card]
					lowestCost = card.mana
				elif card.mana == lowestCost:
					minionsinDeck.append(card)
					
		if minionsinDeck != []:
			miniontoDraw = np.random.choice(minionsinDeck)
			card, mana = self.Game.Hand_Deck.drawCard(self.ID, miniontoDraw)
			if card != None:
				card.buffDebuff(2, 2)
		return None
		
		
class DragonSpeaker(Minion):
	Class, race, name = "Paladin", "", "Dragon Speaker"
	mana, attack, health = 5, 3, 5
	index = "Shadows~Paladin~Minion~5~3~5~None~Dragon Speaker~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Give all Dragons in your hand +3/+3"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		PRINT(self, "Dragon Speaker's battlecry gives all Dragons in player's hand +3/+3.")
		for card in self.Game.Hand_Deck.hands[self.ID]:
			if card.cardType == "Minion" and "Dragon" in card.race:
				card.buffDebuff(3, 3)
		return None
		
#Friendly minion attacks. If the the minion has "Can't Attack", then it won't attack.
#Attackchances won't be consumed. If it survives, it can attack again. triggers["DealsDamage"] functions can trigger.
class Duel(Spell):
	Class, name = "Paladin", "Duel!"
	requireTarget, mana = False, 5
	index = "Shadows~Paladin~Spell~5~Duel!"
	description = "Summon a minion from each player's deck. They fight"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		PRINT(self, "Duel! is cast and summons a minion from each player's deck. They fight.")
		minionsinEnemyDeck = []
		for card in self.Game.Hand_Deck.decks[3-self.ID]:
			if card.cardType == "Minion":
				minionsinEnemyDeck.append(card)
				
		minionsinFriendlyDeck = []
		for card in self.Game.Hand_Deck.decks[self.ID]:
			if card.cardType == "Minion":
				minionsinFriendlyDeck.append(card)
				
		enemyMinion, friendlyMinion = None, None
		if minionsinEnemyDeck != [] and self.Game.spaceonBoard(3-self.ID) > 0:
			enemyMinion, mana, isRightmostCardinHand = self.Game.Hand_Deck.extractfromDeck(np.random.choice(minionsinEnemyDeck))
			self.Game.summonMinion(enemyMinion, -1, self.ID)#comment="SummoningCanbeDoubled"
			
		if minionsinFriendlyDeck != [] and self.Game.spaceonBoard(self.ID) > 0:
			friendlyMinion, mana, isRightmostCardinHand = self.Game.Hand_Deck.extractfromDeck(np.random.choice(minionsinFriendlyDeck))
			self.Game.summonMinion(friendlyMinion, -1, self.ID)
		#如果我方随从有不能攻击的限制，如Ancient Watcher之类，不能攻击。
		#攻击不消耗攻击机会
		#需要测试有条件限制才能攻击的随从，如UnpoweredMauler
		if friendlyMinion != None and enemyMinion != None and friendlyMinion.marks["Can't Attack"] < 1:
			self.Game.battleRequest(friendlyMinion, enemyMinion, False, False)
			
		return None
		
		
class CommanderRhyssa(Minion):
	Class, race, name = "Paladin", "", "Commander Rhyssa"
	mana, attack, health = 3, 4, 3
	index = "Shadows~Paladin~Minion~3~4~3~None~Commander Rhyssa~Legendary"
	requireTarget, keyWord, description = False, "", "Your Secrets trigger twice"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.appearResponse = [self.activateAura]
		self.disappearResponse = [self.deactivateAura]
		self.silenceResponse = [self.deactivateAura]
		
	def activateAura(self):
		PRINT(self, "Commander Rhyssa's aura is registered. Player %d's Secrets now trigger twice."%self.ID)
		self.Game.playerStatus[self.ID]["Secret Trigger Twice"] += 1
		
	def deactivateAura(self):
		PRINT(self, "Commander Rhyssa's aura is removed. Player %d's Secrets no longer trigger twice."%self.ID)
		if self.Game.playerStatus[self.ID]["Secret Trigger Twice"] > 0:
			self.Game.playerStatus[self.ID]["Secret Trigger Twice"] -= 1
			
			
class Nozari(Minion):
	Class, race, name = "Paladin", "Dragon", "Nozari"
	mana, attack, health = 10, 4, 12
	index = "Shadows~Paladin~Minion~10~4~12~Dragon~Nozari~Battlecry~Legendary"
	requireTarget, keyWord, description = False, "", "Battlecry: Restore both heroes to full Health"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		PRINT(self, "Nozari's battlecry restores all health to both players.")
		heal1 = self.Game.heroes[1].health_upper * (2 ** self.countHealDouble())
		heal2 = self.Game.heroes[2].health_upper * (2 ** self.countHealDouble())
		self.restoresAOE([self.Game.heroes[1], self.Game.heroes[2]], [heal1, heal2])
		return None
		
"""Priest cards"""
class EVILConscripter(Minion):
	Class, race, name = "Priest", "", "EVIL Conscripter"
	mana, attack, health = 2, 2, 2
	index = "Shadows~Priest~Minion~2~2~2~None~EVIL Conscripter~Deathrattle"
	requireTarget, keyWord, description = False, "", "Deathrattle: Add a Lackey to your hand"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [AddaRandomLackeytoHand(self)]
		
class AddaRandomLackeytoHand(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self, "Deathrattle: Add A random Lackey to player's hand triggers.")
		self.entity.Game.Hand_Deck.addCardtoHand(np.random.choice(Lackeys), self.entity.ID, "CreateUsingType")
		
		
class HenchClanShadequill(Minion):
	Class, race, name = "Priest", "", "Hench-Clan Shadequill"
	mana, attack, health = 4, 4, 7
	index = "Shadows~Priest~Minion~4~4~7~None~Hench-Clan Shadequill~Deathrattle"
	requireTarget, keyWord, description = False, "", "Deathrattle: Restore 5 Health to the enemy hero"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [Restore5HealthtoEnemyHero(self)]
		
class Restore5HealthtoEnemyHero(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		heal = 5 * (2 ** self.entity.countHealDouble())
		PRINT(self, "Deathrattle: Restore %d health to enemy hero triggers to player's hand triggers."%heal)
		self.entity.restoresHealth(self.entity.Game.heroes[3-self.entity.ID], heal)
		
#If the target minion is killed due to Teacher/Juggler combo, summon a fresh new minion without enchantment.
class UnsleepingSoul(Spell):
	Class, name = "Priest", "Unsleeping Soul"
	requireTarget, mana = True, 4
	index = "Shadows~Priest~Spell~4~Unsleeping Soul"
	description = "Silence a friendly minion, then summon a copy of it"
	def targetExists(self, choice=0):
		return self.selectableFriendlyMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.ID == self.ID and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if target != None:
			PRINT(self, "Unsleeping Soul is cast, silences friendly minion %s and summons a copy of it."%target.name)
			target.getsSilenced()
			self.Game.summonMinion(target.selfCopy(target.ID), target.position+1, self.ID)
		return target
		
		
class ForbiddenWords(Spell):
	Class, name = "Priest", "Forbidden Words"
	requireTarget, mana = True, 0
	index = "Shadows~Priest~Spell~0~Forbidden Words"
	description = "Spell all your Mana. Destroy a minion with that much Attack or less"
	
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.attack <= self.Game.ManaHandler.manas[self.ID] and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		#假设如果没有指定目标则不会消耗法力值
		if target != None:
			PRINT(self, "Forbidden Words is cast, spends all of player's mana and destroys minion %s"%target.name)
			self.Game.CounterHandler.manaSpentonSpells[self.ID] += self.Game.ManaHandler.manas[self.ID]
			self.Game.ManaHandler.manas[self.ID] = 0
			target.dead = True
		return target
		
		
class ConvincingInfiltrator(Minion):
	Class, race, name = "Priest", "", "Convincing Infiltrator"
	mana, attack, health = 5, 2, 6
	index = "Shadows~Priest~Minion~5~2~6~None~Convincing Infiltrator~Taunt~Deathrattle"
	requireTarget, keyWord, description = False, "Taunt", "Taunt. Deathrattle: Destroy a random enemy minion"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [DestroyaRandomEnemyMinion(self)]
		
class DestroyaRandomEnemyMinion(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self, "Deathrattle: Destroy a random enemy minion triggers.")
		minions = []
		for minion in self.entity.Game.minionsonBoard(3-self.entity.ID):
			if minion.dead == False:
				minions.append(minion)
				
		if minions != []:
			np.random.choice(minions).dead = True
			
			
class MassResurrection(Spell):
	Class, name = "Priest", "Mass Resurrection"
	requireTarget, mana = False, 9
	index = "Shadows~Priest~Spell~9~Mass Resurrection"
	
	def available(self):
		return self.Game.spaceonBoard(self.ID) > 0
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		PRINT(self, "Mass Resurrection is cast and summons 3 friendly minions that died this turn.")
		numMinionsDied = len(self.Game.CounterHandler.minionsDiedThisGame[self.ID])
		numSummon = min(3, self.Game.spaceonBoard(self.ID), numMinionsDied)
		if numSummon > 0:
			indices = np.random.choice(self.Game.CounterHandler.minionsDiedThisGame[self.ID], numSummon, replace=False)
			self.Game.summonMinion([self.Game.cardPool[index](self.Game, self.ID) for index in indices], (-1, "totheRightEnd"), self.ID)
		return None
		
#Upgrades at the end of turn.
class LazulsScheme(Spell):
	Class, name = "Priest", "Lazul's Scheme"
	requireTarget, mana = True, 0
	index = "Shadows~Priest~Spell~0~Lazul's Scheme"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.progress = 1
		self.triggersinHand = [Trigger_Upgrade(self)]
		
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if target != None:
			PRINT(self, "Lazul's Scheme is cast and reduces minion %s's attack by %d until player's next turn."%(target.name, self.progress))
			timePoint = "StartofTurn 1" if self.ID == 1 else "StartofTurn 2"
			target.buffDebuff(-self.progress, 0, timePoint)
		return target
		
class Trigger_Upgrade(TriggerinHand):
	def __init__(self, entity):
		self.blank_init(entity, ["TurnEnds"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.inHand and ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self, "At the end of turn, %s upgrades"%self.entity.name)
		self.entity.progress += 1
		
		
class ShadowyFigure(Minion):
	Class, race, name = "Priest", "", "Shadowy Figure"
	mana, attack, health = 2, 2, 2
	index = "Shadows~Priest~Minion~2~2~2~None~Shadowy Figure~Battlecry"
	requireTarget, keyWord, description = True, "", "Battlecry: Transform into a 2/2 copy of a friendly Deathrattle minion"
	
	def targetExists(self, choice=0):
		return self.selectableFriendlyMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target != self and target.ID == self.ID and target.deathrattles != [] and target.onBoard
		
	def effectCanTrigger(self):
		self.effectViable = self.targetExists()
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		#目前只有打随从从手牌打出或者被沙德沃克调用可以触发随从的战吼。这些手段都要涉及self.Game.minionPlayed
		#如果self.Game.minionPlayed不再等于自己，说明这个随从的已经触发了变形而不会再继续变形。
		if target != None and self.dead == False and self.Game.minionPlayed == self: #战吼触发时自己不能死亡。
			if self.onBoard or self.inHand:
				if target.onBoard:
					Copy = target.selfCopy(self.ID, 2, 2)
					PRINT(self, "Shadowy Figure's battlecry transforms minion into a copy of %s"%target.name)
				else: #target not on board. This Shadowy Figure becomes a base copy of it.
					Copy = type(target)(self.Game, self.ID)
					Copy.statReset(2, 2)
					PRINT(self, "Shadowy Figure's battlecry transforms minion into a base copy of %s"%target.name)
				self.Game.transform(self, Copy)
		return target
		
		
class MadameLazul(Minion):
	Class, race, name = "Priest", "", "Madame Lazul"
	mana, attack, health = 3, 3, 2
	index = "Shadows~Priest~Minion~3~3~2~None~Madame Lazul~Battlecry~Legendary"
	requireTarget, keyWord, description = False, "", "Battlecry: Discover a copy of a card in your opponent's hand"
	#不知道如果手牌中有多个同类型的随从，但是接受了不同的buff等效果，是否会发现不同的类型
	#def randomorDiscover(self):
	#	if self.Game.Hand_Deck.hands[3-self.ID] < 2:
	#		return "No RNG"
	#	else:
	#		return "Discover"
	#		
	#def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
	#	if self.Game.Hand_Deck.hands[3-self.ID] != [] and self.Game.Hand_Deck.handNotFull(self.ID):
	#		if len(self.Game.Hand_Deck.hands[3-self.ID]) == 1:
	#			PRINT(self, "Opponent only has one card in hand, Madame Lazul's battlecry copies it")
	#			Copy = self.Game.Hand_Deck.hands[3-self.ID][0].selfCopy(self.ID)
	#			self.Game.Hand_Deck.addCardtoHand(Copy, self.ID)
	#		else:
	#			if "InvokedbyOthers" in comment:
	#				PRINT(self, "Madame Lazul's battlecry adds a copy of a random card in opponent's hand to player's hand.")
	#				Copy = np.random.choice(self.Game.Hand_Deck.hands[3-self.ID]).selfCopy(self.ID)
	#				self.Game.Hand_Deck.addCardtoHand(Copy, self.ID)
	#			else:
	#				PRINT(self, "Madame Lazul's battlecry lets player discover a copy of card in opponent's hand.")
	#				num = 
	#	return None
	
class CatrinaMuerte(Minion):
	Class, race, name = "Priest", "", "Catrina Muerte"
	mana, attack, health = 8, 6, 8
	index = "Shadows~Priest~Minion~8~6~8~None~Catrina Muerte~Legendary"
	requireTarget, keyWord, description = False, "", "At the end of your turn, summon a friendly minion that died this game"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_CatrinaMuerte(self)]
		
class Trigger_CatrinaMuerte(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["TurnEnds"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self, "At the end of turn, %s summons a friendly minion that died this game."%self.entity.name)
		if self.entity.Game.CounterHandler.minionsDiedThisGame[self.entity.ID] != []:
			minion = np.random.choice(self.entity.Game.CounterHandler.minionsDiedThisGame[self.entity.ID])
			minion = self.entity.Game.cardPool[minion](self.entity.Game, self.entity.ID)
			self.entity.Game.summonMinion(minion, self.entity.position+1, self.entity.ID)
			
"""Rogue cards"""
class DaringEscape(Spell):
	Class, name = "Rogue", "Daring Escape"
	requireTarget, mana = False, 1
	index = "Shadows~Rogue~Spell~1~Daring Escape"
	description = "Return all friendly minions to your hand"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		PRINT(self, "Daring Escape is cast and returns all friendly minions to player's hand.")
		for minion in self.Game.minionsonBoard(self.ID):
			self.Game.returnMiniontoHand(minion)
		return None
		
		
class EVILMiscreant(Minion):
	Class, race, name = "Rogue", "", "EVIL Miscreant"
	mana, attack, health = 3, 1, 4
	index = "Shadows~Rogue~Minion~3~1~4~None~EVIL Miscreant~Combo"
	requireTarget, keyWord, description = False, "", "Combo: Add two 1/1 Lackeys to your hand"
	
	def effectCanTrigger(self):
		self.effectViable = self.Game.CounterHandler.numCardsPlayedThisTurn[self.ID] > 0
		
	#Will only be invoked if self.effectCanTrigger() returns True in self.played()
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if self.Game.CounterHandler.numCardsPlayedThisTurn[self.ID] > 0:
			PRINT(self, "EVIL Miscreant's Combo triggers and adds two Lackeys to player's hand.")
			self.Game.Hand_Deck.addCardtoHand(np.random.choice(Lackeys, 2, replace=False), self.ID, "CreateUsingType")
		return None
		
		
class HenchClanBurglar(Minion):
	Class, race, name = "Rogue", "", "Hench-Clan Burglar"
	mana, attack, health = 4, 4, 3
	index = "Shadows~Rogue~Minion~4~4~3~None~Hench-Clan Burglar~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Discover a spell from another class"
	poolIdentifier = "Spells except Rogue"
	@classmethod
	def generatePool(cls, Game):
		classes, lists = [], []
		for Class in ClassesandNeutral:
			classes.append("Spells except "+Class)
			classPool = copy.deepcopy(Classes)
			extractfrom(Class, classPool)
			spells = []
			for ele in classPool:
				for key, value in Game.ClassCards[ele].items():
					if "~Spell~" in key:
						spells.append(value)
			lists.append(spells)
		return classes, lists
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if self.ID == self.Game.turn:
			Class = self.Game.heroes[self.ID].Class
			key = "Spells except "+Class
			if "InvokedbyOthers" in comment:
				PRINT(self, "Hench-Clan Burglar's battlecry adds a random spell from another class to player's hand")
				self.Game.Hand_Deck.addCardtoHand(np.random.choice(self.Game.RNGPools[key]), self.ID, "CreateUsingType")
			else:
				PRINT(self, "Hench-Clan Burglar's battlecry lets player Discover a spell from another class")
				spells = np.random.choice(self.Game.RNGPools[key], 3, replace=False)
				self.Game.options = [spell(self.Game, self.ID) for spell in spells]
				self.Game.DiscoverHandler.startDiscover(self)
		return None
		
	def discoverDecided(self, option):
		PRINT(self, "Spell %s is added to player's hand"%option.name)
		self.Game.Hand_Deck.addCardtoHand(option, self.ID)
		self.Game.sendSignal("DiscoveredCardPutintoHand", self.ID, self, option, 0, "")
		
		
class TogwagglesScheme(Spell):
	Class, name = "Rogue", "Togwaggle's Scheme"
	requireTarget, mana = True, 1
	index = "Shadows~Rogue~Spell~1~Togwaggle's Scheme"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.progress = 1
		self.triggersinHand = [Trigger_Upgrade(self)]
		
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.ID == self.ID and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if target != None:
			PRINT(self, "Togwaggle's Scheme is cast and shuffles %d copies of a friendly minion to player's hand.")
			for i in range(self.progress):
				Copy = type(target)(self.Game, self.ID)
				self.Game.Hand_Deck.shuffleCardintoDeck(Copy, initiatorID=self.ID)
		return target
		
		
class UnderbellyFence(Minion):
	Class, race, name = "Rogue", "", "Underbelly Fence"
	mana, attack, health = 2, 2, 3
	index = "Shadows~Rogue~Minion~2~2~3~None~Underbelly Fence~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: If you're holding a card from another class, gain +1/+1 and Rush"
	
	def effectCanTrigger(self):
		if self.inHand:
			self.effectViable = self.Game.Hand_Deck.holdingCardfromAnotherClass(self.ID, self)
		else:
			self.effectViable = self.Game.Hand_Deck.holdingCardfromAnotherClass(self.ID)
			
	#Will only be invoked if self.effectCanTrigger() returns True in self.played()
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if self.inHand and self.Game.Hand_Deck.holdingCardfromAnotherClass(self.ID, self):
			PRINT(self, "Underbelly Fence's battlecry gives minion +1/+1 and Rush.")
			self.buffDebuff(1, 1)
			self.getsKeyword("Rush")
		elif self.onBoard and self.Game.Hand_Deck.holdingCardfromAnotherClass(self.ID):
			PRINT(self, "Underbelly Fence's battlecry gives minion +1/+1 and Rush.")
			self.buffDebuff(1, 1)
			self.getsKeyword("Rush")
		return None
		
		
class Vendetta(Spell):
	Class, name = "Rogue", "Vendetta"
	requireTarget, mana = True, 4
	index = "Shadows~Rogue~Spell~4~Vendetta"
	description = "Deal 4 damage to a minion. Costs (0) if you're holding a card from another class"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersinHand = [Trigger_Vendetta(self)]
		
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.onBoard
		
	def selfManaChange(self):
		if self.inHand and self.Game.Hand_Deck.holdingCardfromAnotherClass(self.ID):
			self.mana = 0
			
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if target != None:
			damage = (4 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			PRINT(self, "Vendetta is cast and deals %d damage to minion %s"%(damage, target.name))
			self.dealsDamage(target, damage)
		return target
		
class Trigger_Vendetta(TriggerinHand):
	def __init__(self, entity):
		self.blank_init(entity, ["CardLeavesHand", "CardEntersHand"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		#Only cards with a different class than your hero class will trigger this
		card = target[0] if signal == "CardEntersHand" else target
		return self.entity.inHand and card.ID == self.entity.ID and card.Class != self.entity.Game.heroes[self.entity.ID].Class
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.Game.ManaHandler.calcMana_Single(self.entity)
		
		
class WagglePick(Weapon):
	Class, name, description = "Rogue", "Waggle Pick", "Deathrattle: Return a random friendly minion to your hand. It costs (2) less"
	mana, attack, durability = 4, 4, 2
	index = "Shadows~Rogue~Weapon~4~4~2~Waggle Pick~Deathrattle"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [ReturnaFriendlyMiniontoHand(self)]
		
#There are minions who also have this deathrattle.
class ReturnaFriendlyMiniontoHand(Deathrattle_Weapon):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		if self.entity.Game.minionsonBoard(self.entity.ID) != []:
			PRINT(self, "Deathrattle: Return a random friendly minion to your hand triggers")
			miniontoReturn = np.random.choice(self.entity.Game.minionsonBoard(self.entity.ID))
			#假设那张随从在进入手牌前接受-2费效果。可以被娜迦海巫覆盖。
			manaMod = ManaModification(miniontoReturn, changeby=-2, changeto=-1)
			self.entity.Game.returnMiniontoHand(miniontoReturn, keepDeathrattlesRegistered=False, manaModification=manaMod)
			
			
class UnidentifiedContract(Spell):
	Class, name = "Rogue", "Unidentified Contract"
	requireTarget, mana = True, 6
	index = "Shadows~Rogue~Spell~6~Unidentified Contract"
	description = "Destroy a minion. Gain a bonus effect in your hand"
	def entersHand(self):
		#本牌进入手牌的结果是本卡消失，变成其他的牌
		self.onBoard, self.inHand, self.inDeck = False, False, False
		mana = self.mana #假设变成其他牌之后会保留当前的费用状态
		card = np.random.choice([AssassinsContract, LucrativeContract, RecruitmentContract, TurncoatContract])(self.Game, self.ID)
		ManaModification(card, changeby=0, changeto=mana).applies()
		return card
		
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if target != None:
			PRINT(self, "Unidentified Contract is cast and destroys minion %s"%target.name)
			target.dead = True
		return target
		
class AssassinsContract(Spell):
	Class, name = "Rogue", "Assassin's Contract"
	requireTarget, mana = True, 6
	index = "Shadows~Rogue~Spell~6~Assassin's Contract~Uncollectible"
	description = "Destroy a minion. Summon a 1/1 Patient Assassin"
	
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if target != None:
			PRINT(self, "Assassin's Contract is cast and destroys minion %s"%target.name)
			target.dead = True
		PRINT(self, "Assassin's Contract also summons a 1/1 Patient Assassin")
		self.Game.summonMinion(PatientAssassin(self.Game, self.ID), -1, self.ID)
		return target
		
class LucrativeContract(Spell):
	Class, name = "Rogue", "Lucrative Contract"
	requireTarget, mana = True, 6
	index = "Shadows~Rogue~Spell~6~Lucrative Contract~Uncollectible"
	description = "Destroy a minion. Add two Coins to your hand"
	
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if target != None:
			PRINT(self, "Lucrative Contract is cast and destroys minion %s"%target.name)
			target.dead = True
		PRINT(self, "Lucrative Contract also adds two Coins to player's hand")
		self.Game.Hand_Deck.addCardtoHand([TheCoin, TheCoin], self.ID, "CreateUsingType")
		return target
		
class RecruitmentContract(Spell):
	Class, name = "Rogue", "Recruitment Contract"
	requireTarget, mana = True, 6
	index = "Shadows~Rogue~Spell~6~Recruitment Contract~Uncollectible"
	description = "Destroy a minion. Add a copy of it to your hand"
	
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if target != None:
			PRINT(self, "Recruitment Contract is cast and destroys minion %s"%target.name)
			target.dead = True
		PRINT(self, "Recruitment Contract also adds a copy of the minion to player's hand")
		self.Game.Hand_Deck.addCardtoHand(type(target), self.ID, "CreateUsingType")
		return target
		
class TurncoatContract(Spell):
	Class, name = "Rogue", "Turncoat Contract"
	requireTarget, mana = True, 6
	index = "Shadows~Rogue~Spell~6~Turncoat Contract~Uncollectible"
	description = "Destroy a minion. It deals damage to adjacent minions"
	
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if target != None:
			PRINT(self, "Turncoat Contract is cast and destroys minion %s"%target.name)
			target.dead = True
		if target.onBoard:
			PRINT(self, "Turncoat Contract also lets the minion deal its damage to adjacent minions")
			adjacentMinions, distribution = self.Game.findAdjacentMinions(target)
			if adjacentMinions != []:
				target.dealsAOE(adjacentMinions, [target.attack for minion in adjacentMinions])
		return target
		
		
class GoldenKobold_Shadows(Minion):
	Class, race, name = "Neutral", "", "Golden Kobold"
	mana, attack, health = 3, 6, 6
	index = "Shadows~Neutral~Minion~3~6~6~None~Golden Kobold~Taunt~Battlecry~Legendary~Uncollectible"
	requireTarget, keyWord, description = False, "Taunt", "Taunt. Battlecry: Replace your hand with Legendary minions"
	poolIdentifier = "Legendary Minions"
	@classmethod
	def generatePool(cls, Game):
		return "Legendary Minions", list(Game.LegendaryMinions.values())
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		PRINT(self, "Golden Kobold's battlecry replaces player's hand with Legendary minions")
		minions = list(self.Game.LegendaryMinions.values())
		handSize = len(self.Game.Hand_Deck.hands[self.ID])
		self.Game.Hand_Deck.extractfromHand(None, True, self.ID)
		minionstoHand = np.random.choice(minions, handSize, replace=True)
		self.Game.Hand_Deck.addCardtoHand(minionstoHand, self.ID, "CreateUsingType")
		return None
		
class TolinsGoblet_Shadows(Spell):
	Class, name = "Neutral", "Tolin's Goblet"
	requireTarget, mana = False, 3
	index = "Shadows~Neutral~Spell~3~Tolin's Goblet~Uncollectible"
	description = "Draw a card. Fill your hand with copies of it"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		PRINT(self, "Tolin's Goblet lets player draw a card and fills their hand with copies of it")
		card, mana = self.Game.Hand_Deck.drawCard(self.ID)
		if card != None and self.Game.Hand_Deck.handNotFull(self.ID):
			copies = [card.selfCopy(self.ID) for i in self.Game.Hand_Deck.spaceinHand(self.ID)]
			self.Game.Hand_Deck.addCardtoHand(copies, self.ID)
		return None
		
class WondrousWand_Shadows(Spell):
	Class, name = "Neutral", "Wondrous Wand"
	requireTarget, mana = False, 3
	index = "Shadows~Neutral~Spell~3~Wondrous Wand~Uncollectible"
	description = "Draw 3 cards. Reduce their costs to (0)"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		PRINT(self, "WondrousWand lets player draw 3 cards and reduces their costs to (0)")
		for i in range(3):
			card, mana = self.Game.Hand_Deck.drawCard(self.ID)
			if card != None:
				ManaModification(card, changeby=0, changeto=0).applies()
				self.Game.ManaHandler.calcMana_Single(card)
		return None
		
class ZarogsCrown_Shadows(Spell):
	Class, name = "Neutral", "Zarog's Crown"
	requireTarget, mana = False, 3
	index = "Shadows~Neutral~Spell~3~Zarog's Crown~Uncollectible"
	description = "Discover a Legendary minion. Summon two copies of it"
	poolIdentifier = "Legendary Minions as Druid to Summon"
	@classmethod
	def generatePool(cls, Game):
		classes, lists = [], []
		for Class in Classes:
			classes.append("Legendary Minions as %s to Summon"%Class)
			legendaryMinions = []
			for key, value in Game.LegendaryMinions.items():
				if "~%s~"%Class in key or "~Neutral~" in key:
					legendaryMinions.append(value)
					
			lists.append(legendaryMinions)
		return classes, lists
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if self.Game.spaceonBoard(self.ID) > 0:
			key = "Legendary Minions as %s to Summon"%classforDiscover(self)
			if "CastbyOthers" in comment:
				PRINT(self, "Zarog's Crown summons two copies of a random Legendary minion")
				minion = np.random.choice(self.Game.RNGPools[key])
				self.Game.summonMinion([minion(self.Game, self.ID) for i in range(2)], (-1, "totheRightEnd"), self.ID)
			else:
				PRINT(self, "Zarog's Crown lets playersummons two copies of a random Legendary minion")
				minions = np.random.choice(self.Game.RNGPools[key], 3, replace=False)
				self.Game.options = [minion(self.Game, self.ID) for minion in minions]
				self.Game.DiscoverHandler.startDiscover(self)
		return None
		
	def discoverDecided(self, option):
		PRINT(self, "Zarog's Crown summons two copies of Legendary minion %s"%option.name)
		self.Game.summonMinion([option, type(option)(self.Game, self.ID)], (-1, "totheRightEnd"), self.ID)
		
FantasticTreasures = [GoldenKobold_Shadows, TolinsGoblet_Shadows, WondrousWand_Shadows, ZarogsCrown_Shadows]

class HeistbaronTogwaggle(Minion):
	Class, race, name = "Rogue", "", "Heistbaron Togwaggle"
	mana, attack, health = 6, 5, 5
	index = "Shadows~Rogue~Minion~6~5~5~None~Heistbaron Togwaggle~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: If you control a Lackey, choose a fantastic treasure"
	
	def effectCanTrigger(self):
		self.effectViable = False
		for minion in self.Game.minionsonBoard(self.ID):
			if minion.name.endswith("Lackey"):
				self.effectViable = True
				break
				
	#Will only be invoked if self.effectCanTrigger() returns True in self.played()
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		controlsLackey = False
		for minion in self.Game.minionsonBoard(self.ID):
			if minion.name.endswith("Lackey"):
				controlsLackey = True
				break
				
		if controlsLackey and self.ID == self.Game.turn and self.Game.Hand_Deck.handNotFull(self.ID):
			if "InvokedbyOthers" in comment:
				PRINT(self, "Heistbaron Togwaggle's battlecry gives player a fantastic treasure")
				self.Game.Hand_Deck.addCardtoHand(np.random.choice(FantasticTreasures), self.ID, "CreateUsingType")
			else:
				PRINT(self, "Heistbaron Togwaggle's battlecry lets player choose a fantastic treasure.")
				self.Game.options = [treasure(self.Game, self.ID) for treasure in FantasticTreasures]
				self.Game.DiscoverHandler.startDiscover(self)
		return None
	
	def discoverDecided(self, option):
		PRINT(self, "Treasure %s is added to player's hand"%option.name)
		self.Game.Hand_Deck.addCardtoHand(option, self.ID)
		
		
class TakNozwhisker(Minion):
	Class, race, name = "Rogue", "", "Tak Nozwhisker"
	mana, attack, health = 7, 6, 6
	index = "Shadows~Rogue~Minion~7~6~6~None~Tak Nozwhisker"
	requireTarget, keyWord, description = False, "", "Whenever you shuffle a card into your deck, add a copy to your hand"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_TakNozwhisker(self)]
		
class Trigger_TakNozwhisker(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["CardShuffled"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		#Only triggers if the player is the initiator
		return self.entity.onBoard and ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self, "Player shuffles cards into deck and %s adds a copy to player's hand for each"%self.entity.name)
		if type(target) == type([]) or type(target) == type(np.array([])):
			for card in obj:
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
	Class, name = "Shaman", "Mutate"
	requireTarget, mana = True, 0
	index = "Shadows~Shaman~Spell~0~Mutate"
	description = "Transf a friendly minion to a random one that costs (1) more"
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
			PRINT(self, "Mutate is cast and transforms friendly minion %s to one that costs 1 more."%target.name)
			target = self.Game.mutate(target, 1)
		return target
		
		
class SludgeSlurper(Minion):
	Class, race, name = "Shaman", "Murloc", "Sludge Slurper"
	mana, attack, health = 1, 2, 1
	index = "Shadows~Shaman~Minion~1~2~1~Murloc~Sludge Slurper~Battlecry~Overload"
	requireTarget, keyWord, description = False, "", "Battlecry: Add a Lackey to your hand. Overload: (1)"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.overload = 1
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		PRINT(self, "Sludge Slurper battlecry adds a Lackey to player's hand.")
		self.Game.Hand_Deck.addCardtoHand(np.random.choice(Lackeys), self.ID, "CreateUsingType")
		return None
		
		
class SouloftheMurloc(Spell):
	Class, name = "Shaman", "Soul of the Murloc"
	requireTarget, mana = False, 2
	index = "Shadows~Shaman~Spell~2~Soul of the Murloc"
	description = "Give your minions 'Deathrattle: Summon a 1/1 Murloc'"
	def available(self):
		return self.Game.minionsonBoard(self.ID) != []
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		PRINT(self, "Soul of the Murloc is cast and gives all friendly minions Deathrattle: Summon a 1/1 Murloc.")
		for minion in self.Game.minionsonBoard(self.ID):
			trigger = SummonaMurlocScout(minion)
			minion.deathrattles.append(trigger)
			trigger.connect()
		return None
		
class SummonaMurlocScout(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self, "Deathrattle: Summon a 1/1 Murloc triggers")
		self.entity.Game.summonMinion(MurlocScout(self.entity.Game, self.entity.ID), self.entity.position+1, self.entity.ID)
		
		
class UnderbellyAngler(Minion):
	Class, race, name = "Shaman", "Murloc", "Underbelly Angler"
	mana, attack, health = 2, 2, 3
	index = "Shadows~Shaman~Minion~2~2~3~Murloc~Underbelly Angler"
	requireTarget, keyWord, description = False, "", "After you play a Murloc, add a random Murloc to your hand"
	poolIdentifier = "Murlocs"
	@classmethod
	def generatePool(cls, Game):
		return "Murlocs", list(Game.MinionswithRace["Murloc"].values())
		
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_UnderbellyAngler(self)]
		
class Trigger_UnderbellyAngler(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionBeenSummoned"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject.ID == self.entity.ID and subject != self.entity and "Murloc" in subject.race
	#Assume if Murloc gets controlled by the enemy, this won't trigger
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self, "After player plays Murloc %s, %s adds a random Murloc to player's hand."%(subject.name, self.entity.name))
		murloc = np.random.choice(self.entity.Game.RNGPools["Murlocs"])(self.entity.Game, self.entity.ID)
		self.entity.Game.Hand_Deck.addCardtoHand(murloc, self.entity.ID)
		
		
class HagathasScheme(Spell):
	Class, name = "Shaman", "Hagatha's Scheme"
	requireTarget, mana = False, 5
	index = "Shadows~Shaman~Spell~5~Hagatha's Scheme"
	description = "Deal 1 damage to all minions. (Upgrades each turn)!"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.progress = 1
		self.triggersinHand = [Trigger_Upgrade(self)]
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		damage = (self.progress + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		PRINT(self, "Hagatha's Scheme is cast and deals %d damage to all minions."%damage)
		targets = self.Game.minionsonBoard(1) + self.Game.minionsonBoard(2)
		self.dealsAOE(targets, [damage for minion in targets])
		return None
		
		
class WalkingFountain(Minion):
	Class, race, name = "Shaman", "Elemental", "Walking Fountain"
	mana, attack, health = 8, 4, 8
	index = "Shadows~Shaman~Minion~8~4~8~Elemental~Walking Fountain~Rush~Lifesteal~Windfury"
	requireTarget, keyWord, description = False, "Rush,Windfury,Lifesteal", "Rush, Windfury, Lifesteal"
	
	
class WitchsBrew(Spell):
	Class, name = "Shaman", "Witch's Brew"
	requireTarget, mana = True, 2
	index = "Shadows~Shaman~Spell~2~Witch's Brew"
	description = "Restore 4 Health. Repeatable this turn"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if target != None:
			heal = 4 * (2 ** self.countHealDouble())
			PRINT(self, "Witch's Brew is cast and restores %d health to %s"%(heal, target.name))
			self.restoresHealth(target, heal)
			
		PRINT(self, "Witch's Brew adds another Witch's Brew to player's hand, which disappears at the end of turn.")
		echo = WitchsBrew(self.Game, self.ID)
		trigger = Trigger_Echo(echo)
		echo.triggersinHand.append(trigger)
		self.Game.Hand_Deck.addCardtoHand(echo, self.ID)
		return target
		
		
class Muckmorpher(Minion):
	Class, race, name = "Shaman", "", "Muckmorpher"
	mana, attack, health = 5, 4, 4
	index = "Shadows~Shaman~Minion~5~4~4~None~Muckmorpher~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Transform in to a 4/4 copy of a different minion in your deck"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		#目前只有打随从从手牌打出或者被沙德沃克调用可以触发随从的战吼。这些手段都要涉及self.Game.minionPlayed
		#如果self.Game.minionPlayed不再等于自己，说明这个随从的已经触发了变形而不会再继续变形。
		if self.dead == False and self.Game.minionPlayed == self: #战吼触发时自己不能死亡。
			if self.onBoard or self.inHand:
				PRINT(self, "Muckmorpher's battlecry transforms the minion into a 4/4 copy of a minion in player's deck.")
				minionsinDeck = []
				for card in self.Game.Hand_Deck.decks[self.ID]:
					if card.cardType == "Minion":
						minionsinDeck.append(card)
				if minionsinDeck != []:
					Copy = type(np.random.choice(minionsinDeck))(self.Game, self.ID)
					Copy.statReset(4, 4)
					PRINT(self, "Muckmorpher's battlecry transforms the minion into a 4/4 copy of %s"%Copy.name)
					self.Game.transform(self, Copy)
		return None
		
		
class Scargil(Minion):
	Class, race, name = "Shaman", "Murloc", "Scargil"
	mana, attack, health = 4, 4, 4
	index = "Shadows~Shaman~Minion~4~4~4~Murloc~Scargil~Legendary"
	requireTarget, keyWord, description = False, "", "Your Murlocs cost (1)"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.auras["Mana Aura"] = ManaAura_Dealer(self, self.manaAuraApplicable, changeby=0, changeto=1)
		
	def manaAuraApplicable(self, subject):
		return subject.ID == self.ID and subject.cardType == "Minion" and "Murloc" in subject.race
		
		
class SwampqueenHagatha(Minion):
	Class, race, name = "Shaman", "", "Swampqueen Hagatha"
	mana, attack, health = 1, 5, 5
	index = "Shadows~Shaman~Minion~7~5~5~None~Swampqueen Hagatha~Battlecry~Legendary"
	requireTarget, keyWord, description = False, "", "Battlecry: Add a 5/5 Horror to your hand. Teach it two Shaman spells"
	poolIdentifier = "Shaman Spells"
	@classmethod
	def generatePool(cls, Game):
		shamanSpells, targetingShamanSpells, nontargetingShamanSpells = [], [], []
		for key, value in Game.ClassCards["Shaman"].items():
			if "~Spell~" in key:
				shamanSpells.append(value)
				if value.requireTarget:
					targetingShamanSpells.append(value)
				else:
					nontargetingShamanSpells.append(value)
		return ["Shaman Spells", "Targeting Shaman Spells", "Non-targeting Shaman Spells"], [shamanSpells, targetingShamanSpells, nontargetingShamanSpells]
		
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.firstSpellneedsTarget = False
		self.spell1, self.spell2 = None, None
	#有可能发现两个相同的非指向性法术。
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		self.spell1, self.spell2 = None, None
		if self.ID == self.Game.turn and self.Game.Hand_Deck.handNotFull(self.ID):
			PRINT(self, "Swampqueen Hagatha's battlecry lets player create a 5/5 Horror and teach it two Shaman Spells.")
			if "InvokedbyOthers" in comment:
				spell1 = np.random.choice(self.Game.RNGPools["Shaman Spells"])
				if spell1.requireTarget:
					spell2 = np.random.choice(self.Game.RNGPools["Non-targeting Shaman Spells"])
				else: #If the first spell is not a targeting spell, then the 2nd has no restrictions
					spell2 = np.random.choice(self.Game.RNGPools["Shaman Spells"])
			else:
				spells = np.random.choice(self.Game.RNGPools["Shaman Spells"], 3, replace=False)
				self.Game.options = [spell(self.Game, self.ID) for spell in spells]
				self.Game.DiscoverHandler.startDiscover(self)
				key = "Non-targeting Shaman Spells" if self.spell1.requireTarget else "Shaman Spells"
				spells = np.random.choice(self.Game.RNGPools[key], 3, replace=False)
				self.Game.options = [spell(self.Game, self.ID) for spell in spells]
				self.Game.DiscoverHandler.startDiscover(self)
				spell1, spell2 = self.spell1, self.spell2
				self.spell1, self.spell2 = None, None
			#The 2 spells are both class types, whether they come from Discover or random
			spell1ClassName, spell2ClassName = spell1.__name__, spell2.__name__
			requireTarget = spell1.requireTarget or spell2.requireTarget
			newIndex = "Shadows~Shaman~5~5~5~Minion~None~Drustvar Horror_%s_%s~Battlecry~Uncollectible"%(spell1.name, spell2.name)
			subclass = type("DrustvarHorror_Mutable_"+spell1ClassName+spell2ClassName, (DrustvarHorror_Mutable, ), 
							{"requireTarget": requireTarget, "learnedSpell1": spell1, "learnedSpell2":spell2,
							"index": newIndex
							}
							)
			self.Game.cardPool[newIndex] = subclass
			self.Game.Hand_Deck.addCardtoHand(subclass(self.Game, self.ID), self.ID)
			
		return None
		
	def discoverDecided(self, option):
		if self.spell1 == None:
			self.spell1 = type(option)
		else:
			self.spell2 = type(option)
			
class DrustvarHorror_Mutable(Minion):
	Class, race, name = "Shaman", "", "Drustvar Horror"
	mana, attack, health = 5, 5, 5
	index = "Shadows~Shaman~Minion~5~5~5~None~Drustvar Horror~Battlecry~Uncollectible"
	requireTarget, keyWord, description = True, "", "Battlecry: Cast (0) and (1)"
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
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		PRINT(self, "Drustvar Horror's battlecry casts the FIRST spell %s it learned on %s"%(self.learnedSpell1.name, target))
		#不知道施放的法术是否会触发发现，还是直接随机选取一个发生选项
		#假设是随机选取一个选项。
		comment = "CastbyOthers,withNoTarget" if target == None else "CastbyOthers"
		self.learnedSpell1.cast(target, comment)
		self.learnedSpell2.cast(target, comment)
		return target
		
"""Warlock cards"""
class EVILGenius(Minion):
	Class, race, name = "Warlock", "", "EVIL Genius"
	mana, attack, health = 2, 2, 2
	index = "Shadows~Warlock~Minion~2~2~2~None~EVIL Genius~Battlecry"
	requireTarget, keyWord, description = True, "", "Battlecry: Destroy a friendly minion to add 2 random Lackeys to your hand"
	def targetExists(self, choice=0):
		return self.selectableFriendlyMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.ID == self.ID and target != self and target.onBoard 
		
	def effectCanTrigger(self):
		self.effectViable = self.targetExists()
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if target != None:
			PRINT(self, "EVIL Genius's battlecry destroys friendly minion %s and adds two lackeys to player's hand."%target.name)
			target.dead = True
			self.Game.Hand_Deck.addCardtoHand(np.random.choice(Lackeys, 2, replace=False), self.ID, "CreateUsingType")
		return target
		
		
class RafaamsScheme(Spell):
	Class, name = "Warlock", "Rafaam's Scheme"
	requireTarget, mana = False, 3
	index = "Shadows~Warlock~Spell~3~Rafaam's Scheme"
	description = "Summon 1 1/1 Imp(Upgrades each turn!)"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.progress = 1
		self.triggersinHand = [Trigger_Upgrade(self)]
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		PRINT(self, "Rafaam's Scheme is cast and summons %d Imps."%self.progress)
		self.Game.summonMinion([Imp_Shadows(self.Game, self.ID) for i in range(self.progress)], (-1, "totheRightEnd"), self.ID)
		return None
		
		
class AranasiBroodmother(Minion):
	Class, race, name = "Warlock", "Demon", "Aranasi Broodmother"
	mana, attack, health = 6, 4, 6
	index = "Shadows~Warlock~Minion~6~4~6~Demon~Aranasi Broodmother~Taunt"
	requireTarget, keyWord, description = False, "Taunt", "Taunt. When you draw this, restore 4 Health to your hero"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggers["Drawn"] = [self.restore4HealthtoHero]
		
	def restore4HealthtoHero(self):
		heal = 4 * (2 ** self.countHealDouble())
		PRINT(self, "Aranasi Broodmother is drawn and restores %d Health to player"%heal)
		self.restoresHealth(self.Game.heroes[self.ID], heal)
		
#把随从洗回牌库会消除其上的身材buff（+2、+2的飞刀杂耍者的buff消失）
#卡牌上的费用效果也会全部消失(大帝的-1效果)
#被祈求升级过一次的迦拉克隆也会失去进度。
#说明这个动作是把手牌中所有牌初始化洗回去
class PlotTwist(Spell):
	Class, name = "Warlock", "Plot Twist"
	requireTarget, mana = False, 2
	index = "Shadows~Warlock~Spell~2~Plot Twist"
	description = "Shuffle your hand into your deck. Draw that many cards"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		PRINT(self, "Plot Twist is cast and shuffles all of player's hand into deck. Then draw that many cards.")
		handSize = len(self.Game.Hand_Deck.hands[self.ID])
		cardstoShuffle, mana, isRightmostCardinHand = self.Game.Hand_Deck.extractfromHand(None, True, self.ID) #Extract all cards.
		#Remove all the temp effects on cards in hand, e.g, TheSoularium and the echo trigger
		for card in cardstoShuffle:
			for trigger in card.triggersonBoard + card.triggersinHand + card.triggersinDeck:
				trigger.disconnect()
			identity = card.identity
			card.__init__(self.Game, self.ID)
			card.identity = identity
		
		self.Game.Hand_Deck.shuffleCardintoDeck(cardstoShuffle, self.ID) #Initiated by self.
		for i in range(handSize):
			self.Game.Hand_Deck.drawCard(self.ID)
		return None
		
		
class Impferno(Spell):
	Class, name = "Warlock", "Impferno"
	requireTarget, mana = False, 3
	index = "Shadows~Warlock~Spell~3~ImpfernoTwist"
	description = "Give your Demons +1 Attack. Deal 1 damage to all enemy minions"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		damage = (1 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		PRINT(self, "Impferno is cast, gives all friendly Demons +1 attack and deals %d damage to enemy minions."%damage)
		for minion in self.Game.minionsonBoard(self.ID):
			if "Demon" in minion.race:
				minion.buffDebuff(1, 1)
				
		targets = self.Game.minionsonBoard(3-self.ID)
		self.dealsAOE(targets, [damage for minion in targets])
		return None
		
		
class EagerUnderling(Minion):
	Class, race, name = "Warlock", "", "Eager Underling"
	mana, attack, health = 4, 2, 2
	index = "Shadows~Warlock~Minion~4~2~2~None~Eager Underling~Deathrattle"
	requireTarget, keyWord, description = False, "", "Deathrattle: Give two random friendly minions +2/+2"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [GiveTwoRandomFriendlyMinionsPlus2Plus2(self)]
		
class GiveTwoRandomFriendlyMinionsPlus2Plus2(Deathrattle_Weapon):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		friendlyMinions = self.Game.minionsonBoard(self.entity.ID)
		PRINT(self, "Deathrattle: Give Two Random Friendly Minions +2/+2 triggers.")
		if len(friendlyMinions) > 1:
			minionstoBuff = np.random.choice(friendlyMinions, 2, replace=False)
			minionstoBuff[0].buffDebuff(2, 2)
			minionstoBuff[1].buffDebuff(2, 2)
		elif len(friendlyMinions) == 1:
			friendlyMinions[0].buffDebuff(2, 2)
			
			
class DarkestHour(Spell):
	Class, name = "Warlock", "Darkest Hour"
	requireTarget, mana = False, 6
	index = "Shadows~Warlock~Spell~6~Darkest Hour"
	description = "Destroy all friendly minions. For each one, summon a random minion from your deck"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		PRINT(self, "Darkest Hour is cast, destroys all friendly minions and summons equal number of minions from deck.")
		boardSize = len(self.Game.minionsonBoard(self.ID))
		for minion in self.Game.minionsonBoard(self.ID):
			minion.dead = True
		#对于所有友方随从强制死亡，并令其离场，因为召唤的随从是在场上右边，不用记录死亡随从的位置
		self.Game.gathertheDead()
		for i in range(boardSize):
			if self.Game.spaceonBoard(self.ID) > 0:
				minionsinDeck = []
				for card in self.Game.Hand_Deck.decks[self.ID]:
					if card.cardType == "Minion":
						minionsinDeck.append(card)
				if minionsinDeck != []:
					minion = np.random.choice(minionsinDeck)
					self.Game.summonfromDeck(minion, -1, self.ID)
		return None
		
#For now, assume the mana change is on the mana and shuffling this card back into deck won't change its counter.
class JumboImp(Minion):
	Class, race, name = "Warlock", "Demon", "Jumbo Imp"
	mana, attack, health = 10, 8, 8
	index = "Shadows~Warlock~Minion~10~8~8~Demon~Jumbo Imp"
	requireTarget, keyWord, description = False, "", "Costs (1) less whenever a friendly minion dies while this is in your hand"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersinHand = [Trigger_JumboImp(self)]
		self.friendlyDemonsDied = 0
		
	def selfManaChange(self):
		self.mana -= self.friendlyDemonsDied
		self.mana = max(self.mana, 0)
		
class Trigger_JumboImp(TriggerinHand):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionDies"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.inHand and target.ID == self.entity.ID and "Demon" in target.race
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.friendlyDemonsDied += 1
		self.entity.Game.ManaHandler.calcMana_Single(self.entity)
		
		
class ArchVillainRafaam(Minion):
	Class, race, name = "Warlock", "", "Arch-Villain Rafaam"
	mana, attack, health = 7, 7, 8
	index = "Shadows~Warlock~Minion~7~7~8~None~Arch-Villain Rafaam~Taunt~Battlecry~Legendary"
	requireTarget, keyWord, description = False, "Taunt", "Battlecry: Replace your hand and deck with Legendary minions"
	poolIdentifier = "Legendary Minions"
	@classmethod
	def generatePool(cls, Game):
		return "Legendary Minions", list(Game.LegendaryMinions.values())
	#不知道拉法姆的替换手牌、牌库和迦拉克隆会有什么互动。假设不影响主迦拉克隆。
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		PRINT(self, "Arch-Villain Rafaam's battlecry replaces player's hand and deck with random Legendary minions.")
		handSize = len(self.Game.Hand_Deck.hands[self.ID])
		self.Game.Hand_Deck.extractfromHand(None, True, self.ID)
		deckSize = len(self.Game.Hand_Deck.decks[self.ID])
		self.Game.Hand_Deck.extractfromDeck(None, True, self.ID)
		#choice will return empty lists if handSize/deckSize == 0
		minionstoHand = np.random.choice(self.Game.RNGPools["Legendary Minions"], handSize, replace=True)
		self.Game.Hand_Deck.addCardtoHand(minionstoHand, self.ID, "CreateUsingType")
		minionstoDeck = np.random.choice(self.Game.RNGPools["Legendary Minions"], deckSize, replace=True)
		self.Game.Hand_Deck.decks[self.ID] = [minion(self.Game, self.ID) for minion in minionstoDeck]
		for card in self.Game.Hand_Deck.decks[self.ID]:
			card.entersDeck()
		return None
		
		
class FelLordBetrug(Minion):
	Class, race, name = "Warlock", "Demon", "Fel Lord Betrug"
	mana, attack, health = 8, 5, 7
	index = "Shadows~Warlock~Minion~8~5~7~Demon~Fel Lord Betrug~Legendary"
	requireTarget, keyWord, description = False, "", "Whenever you draw a minion, summon a copy with Rush that dies at end of turn"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_FelLordBetrug(self)]
		
class Trigger_FelLordBetrug(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["CardDrawn"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and target[0].cardType == "Minion" and target[0].ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self, "Whenever player draws minion %s, %s summons a copy of it that has Rush and dies at the end of turn."%(target[0].name, self.entity.name))
		minion = target[0].selfCopy(self.entity.ID)
		minion.keyWords["Rush"] = 1
		minion.triggersonBoard.append(Trigger_DieatEndofTurn(minion))
		self.entity.Game.summonMinion(minion, self.entity.position+1, self.entity.ID)
		
class Trigger_DieatEndofTurn(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["TurnEnds"])
		self.temp = True
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard #Even if the current turn is not the minion's owner's turn
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self, "At the end of turn, minion %s affected by FelLord Betrug dies."%self.entity.name)
		self.entity.dead = True
		
"""Warrior cards"""
class ImproveMorale(Spell):
	Class, name = "Warrior", "Improve Morale"
	requireTarget, mana = True, 1
	index = "Shadows~Warrior~Spell~1~Improve Morale"
	description = "Deal 1 damage to a minion. If it survives, add a Lackey to your hand"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if target != None:
			damage = (1 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			PRINT(self, "Improve Morale is cast and deals %d damage to minion %s"%(damage, target.name))
			self.dealsDamage(target, damage)
			if target.health > 0 and target.dead == False:
				PRINT(self, "The target survives Improve Morale, a Lackey is added to player's hand.")
				self.Game.Hand_Deck.addCardtoHand(np.random.choice(Lackeys), self.ID, "CreateUsingType")
		return target
		
		
class ViciousScraphound(Minion):
	Class, race, name = "Warrior", "Mech", "Vicious Scraphound"
	mana, attack, health = 2, 2, 2
	index = "Shadows~Warrior~Minion~2~2~2~Mech~Vicious Scraphound"
	requireTarget, keyWord, description = False, "", "Whenever this minion deals damage, gain that much Armor"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_ViciousScraphound(self)]
		
class Trigger_ViciousScraphound(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionTakesDamage", "HeroTakesDamage"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return subject == self.entity
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self, "%s deals damage to %s and player gains 2 Armor."%(self.entity.name, target.name))
		self.entity.Game.heroes[self.entity.ID].gainsArmor(number)
		
		
class DrBoomsScheme(Spell):
	Class, name = "Warrior", "Dr. Boom's Scheme"
	requireTarget, mana = False, 4
	index = "Shadows~Warrior~Spell~4~Dr. Boom's Scheme"
	description = "Gain 1 Armor. (Upgrades each turn!)"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.progress = 1
		self.triggersinHand = [Trigger_Upgrade(self)]
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		PRINT(self, "Dr. Boom's Scheme is cast and player gains %d Armor."%self.progress)
		self.Game.heroes[self.ID].gainsArmor(self.progress)
		return None
		
		
class SweepingStrikes(Spell):
	Class, name = "Warrior", "Sweeping Strikes"
	requireTarget, mana = True, 2
	index = "Shadows~Warrior~Spell~2~Sweeping Strikes"
	description = "Give a minion 'Also damages minions next to whoever this attacks'"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if target != None:
			PRINT(self, "Sweeping Strikes is cast and gives minion %s 'Also damage adjacent minions to whoever this attacks'."%target.name)
			target.marks["Attack Adjacent Minions"] += 1
		return target
		
		
class Bomb_Shadows(Spell):
	Class, name = "Neutral", "Bomb"
	requireTarget, mana = False, 5
	index = "Shadows~Neutral~Spell~5~Bomb~Casts When Drawn~Uncollectible"
	description = "Casts When Drawn. Deal 5 damage to your hero"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		damage = (5 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		PRINT(self, "Bomb is cast and deals %d damage to player."%damage)
		self.dealsDamage(self.Game.heroes[self.ID], damage)
		return None
		
class ClockworkGoblin(Minion):
	Class, race, name = "Warrior", "Mech", "Clockwork Goblin"
	mana, attack, health = 3, 3, 3
	index = "Shadows~Warrior~Minion~3~3~3~Mech~Clockwork Goblin~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Shuffle a Bomb in to your opponent's deck. When drawn, it explodes for 5 damage"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		PRINT(self, "Clockwork Goblin's battlecry shuffles a Bomb into opponents deck. When its drawn, it deals 5 damage to enemy hero.")
		self.Game.Hand_Deck.shuffleCardintoDeck(Bomb_Shadows(self.Game, 3-self.ID), self.ID)
		return None
		
		
class DimensionalRipper(Spell):
	Class, name = "Warrior", "Dimensional Ripper"
	requireTarget, mana = False, 10
	index = "Shadows~Warrior~Spell~10~Dimensional Ripper"
	description = "Summon 2 copies of a minion in your deck"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		PRINT(self, "Dimensional Ripper is cast and summons two copies of a minion in player's deck.")
		if self.Game.spaceonBoard(self.ID) > 0:
			minionsinDeck = []
			for card in self.Game.Hand_Deck.hands[self.ID]:
				if card.cardType == "Minion":
					minionsinDeck.append(card)
					
			if minionsinDeck != []:
				minion1 = np.random.choice(minionsinDeck).selfCopy(self.ID)
				minion2 = minion1.selfCopy(self.ID)
				self.Game.summonMinion([minion1, minion2], (-1, "totheRightEnd"), self.ID)
		return None
		
		
class OmegaDevastator(Minion):
	Class, race, name = "Warrior", "Mech", "Omega Devastator"
	mana, attack, health = 4, 4, 5
	index = "Shadows~Warrior~Minion~4~4~5~Mech~Omega Devastator~Battlecry"
	requireTarget, keyWord, description = True, "", "Battlecry: If you have 10 Mana Crystals, deal 10 damage to a minion"
	
	def returnTrue(self, choice=0):
		return self.Game.ManaHandler.manasUpper[self.ID] >= 10
		
	def effectCanTrigger(self):
		self.effectViable = self.Game.ManaHandler.manasUpper[self.ID] >= 10 and self.targetExists()
		
	def targetExists(self, choice=0):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target != self and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if target != None and self.Game.ManaHandler.manasUpper[self.ID] >= 10:
			PRINT(self, "Omega Devastator's battlecry deals 10 damage to minion %s"%target.name)
			self.dealsDamage(target, 10)
		return target
		
		
class Wrenchcalibur(Weapon):
	Class, name, description = "Warrior", "Wrenchcalibur", "After your hero attacks, shuffle a Bomb into your Opponent's deck"
	mana, attack, durability = 4, 3, 2
	index = "Shadows~Warrior~Weapon~4~3~2~Wrenchcalibur"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_Wrenchcalibur(self)]
		
class Trigger_Wrenchcalibur(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["HeroAttackedMinion", "HeroAttackedHero"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		#The target can't be dying to trigger this
		return subject == self.entity.Game.heroes[self.entity.ID] and self.entity.onBoard
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self, "After hero attacks, Wrenchcalibur triggers and shuffles a Bomb in to opponent's deck")
		self.entity.Game.Hand_Deck.shuffleCardintoDeck(Bomb_Shadows(self.entity.Game, 3-self.entity.ID), self.entity.ID)
		
		
class BlastmasterBoom(Minion):
	Class, race, name = "Warrior", "", "Blastmaster Boom"
	mana, attack, health = 7, 7, 7
	index = "Shadows~Warrior~Minion~7~7~7~None~Blastmaster Boom~Battlecry~Legendary"
	requireTarget, keyWord, description = False, "", "Battlecry: Summon two 1/1 Boom Bots for each Bomb in your opponent's deck"
	
	def effectCanTrigger(self):
		self.effectViable = False
		for card in self.Game.Hand_Deck.decks[3-self.ID]:
			if card.name == "Bomb":
				self.effectViable = True
				
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		numBombsinDeck = 0
		for card in self.Game.Hand_Deck.decks[3-self.ID]:
			if card.name == "Bomb":
				numBombsinDeck += 1
				
		numSummon = min(8, 2 * numBombsinDeck)
		PRINT(self, "Blastmaster Boom's battlecry summons two 1/1 Boom Bots for each Bomb in opponent's deck.")
		pos = (self.position, "leftandRight") if self.onBoard else (-1, "totheRightEnd")
		self.Game.summonMinion([BoomBot_Shadows(self.Game, self.ID) for i in range(numSummon)], pos, self.ID)
		return None
		
class BoomBot_Shadows(Minion):
	Class, race, name = "Neutral", "Mech", "Boom Bot"
	mana, attack, health = 1, 1, 1
	index = "Shadows~Neutral~Minion~1~1~1~Mech~Boom Bot~Deathrattle~Uncollectible"
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
			PRINT(self, "Deathrattle deals %d damage to %s"%(damage, target.name))
			self.entity.dealsDamage(target, damage)
			
			
class TheBoomReaver(Minion):
	Class, race, name = "Warrior", "Mech", "The Boom Reaver"
	mana, attack, health = 10, 7, 9
	index = "Shadows~Warrior~Minion~10~7~9~Mech~The Boom Reaver~Battlecry~Legendary"
	requireTarget, keyWord, description = False, "", "Battlecry: Summon a copy of a minion in your deck. Give it Rush"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		PRINT(self, "The Boom Reaver's battlecry summons a copy of minion in player's deck and gives it Rush.")
		if self.Game.spaceonBoard(self.ID) > 0:
			minionsinDeck = []
			for card in self.Game.Hand_Deck.decks[self.ID]:
				if card.cardType == "Minion":
					minionsinDeck.append(card)
					
			if minionsinDeck != []:
				minion = np.random.choice(minionsinDeck).selfCopy(self.ID)
				minion.getsKeyword("Rush")
				self.Game.summonMinion(minion, self.position+1, self.ID)
		return None
		