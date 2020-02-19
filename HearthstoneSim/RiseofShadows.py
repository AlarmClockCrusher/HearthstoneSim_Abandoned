from CardTypes import *
from VariousHandlers import *
from Triggers_Auras import *
from Basic import TheCoin
from Classic import PatientAssassin
from Witchwood import Trigger_Echo
from Boomsday import Bomb

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
	
	
"""Mana 1 cards"""
class PotionVendor(Minion):
	Class, race, name = "Neutral", "", "Potion Vendor"
	mana, attack, health = 1, 1, 1
	index = "Shadows-Neutral-1-1-1-Minion-None-Potion Vendor-Battlecry"
	needTarget, keyWord, description = False, "", "Battlecry: Restore 2 Health to all friendly characters"
	
	def whenEffective(self, target=None, comment="", choice=0):
		heal = 2 * (2 ** self.countHealDouble())
		targets = [self.Game.heroes[self.ID]] + self.Game.minions[self.ID]
		heals = [heal for i in range(len(targets))]
		print("Potion Vendor's battlecry restores %d health to all friendly characters"%heal)
		self.dealsAOE([], [], targets, heals)
		return self, None
		
		
class Toxfin(Minion):
	Class, race, name = "Neutral", "Murloc", "Toxfin"
	mana, attack, health = 1, 1, 2
	index = "Shadows-Neutral-1-1-2-Minion-Murloc-Toxfin-Battlecry"
	needTarget, keyWord, description = True, "", "Battlecry: Give a friendly Murloc Poisonous"
	
	def targetExists(self, choice=0):
		return self.selectableFriendlyMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and "Murloc" in target.race and target.ID == self.ID and target != self and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			print("Toxfin's battlecry gives friendly Murloc %s Poisonous."%target.name)
			target.getsKeyword("Poisonous")
		return self, target
		
		
class EtherealLackey(Minion):
	Class, race, name = "Neutral", "", "Ethereal Lackey"
	mana, attack, health = 1, 1, 1
	index = "Shadows-Neutral-1-1-1-Minion-None-Ethereal Lackey-Battlecry-Uncollectible"
	needTarget, keyWord, description = False, "", "Battlecry: Discover a spell"
	
	def whenEffective(self, target=None, comment="", choice=0):
		Class = self.Game.heroes[self.ID].Class
		spells = []
		for key, value in self.Game.ClassCards[Class].items():
			if "-Spell-" in key:
				spells.append(value)
				
		if comment == "InvokedbyOthers":
			print("Ethereal Lackey's battlecry adds a random %s spell to player's hand"%Class)
			self.Game.Hand_Deck.addCardtoHand(np.random.choice(spells), self.ID, "CreateUsingType")
		else:
			spells = np.random.choice(spells, 3, replace=False)
			self.Game.options = [spell(self.Game, self.ID) for spell in spells]
			print("Ethereal Lackey's battlecry lets player discover a spell")
			self.Game.DiscoverHandler.startDiscover(self)
			
		return self, None
		
	def discoverDecided(self, option):
		print("Spell ", option.name, " is put into player's hand.")
		self.Game.Hand_Deck.addCardtoHand(option, self.ID)
		
class FacelessLackey(Minion):
	Class, race, name = "Neutral", "", "Faceless Lackey"
	mana, attack, health = 1, 1, 1
	index = "Shadows-Neutral-1-1-1-Minion-None-Faceless Lackey-Battlecry-Uncollectible"
	needTarget, keyWord, description = False, "", "Battlecry: Summon a 2-Cost minion"
	
	def whenEffective(self, target=None, comment="", choice=0):
		print("Faceless Lackey's battlecry summons a random 2-Cost minions.")
		minion = np.random.choice(list(self.Game.MinionswithCertainCost[2].values()))
		self.Game.summonMinion(minion(self.Game, self.ID), self.position+1, self.ID)
		return self, None
		
class GoblinLackey(Minion):
	Class, race, name = "Neutral", "", "Goblin Lackey"
	mana, attack, health = 1, 1, 1
	index = "Shadows-Neutral-1-1-1-Minion-None-Goblin Lackey-Battlecry-Uncollectible"
	needTarget, keyWord, description = True, "", "Battlecry: Give a friendly minion +1 Attack and Rush"
	
	def targetExists(self, choice=0):
		return self.selectableFriendlyMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.ID == self.ID and target != self and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			print(self.name, " is played and gives friendly minion %s +2 attack and Rush."%target.name)
			target.buffDebuff(1, 0)
			target.getsKeyword("Rush")
		return self, target
		
class KoboldLackey(Minion):
	Class, race, name = "Neutral", "", "Kobold Lackey"
	mana, attack, health = 1, 1, 1
	index = "Shadows-Neutral-1-1-1-Minion-None-Kobold Lackey-Battlecry-Uncollectible"
	needTarget, keyWord, description = True, "", "Battlecry: Deal 2 damage"
	
	def targetExists(self, choice=0):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target != self and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			print("Kobold Lackey's battlecry deals 2 damage to ", target.name)
			self.dealsDamage(target, 2)
		return self, target
		
class WitchyLackey(Minion):
	Class, race, name = "Neutral", "", "Witchy Lackey"
	mana, attack, health = 1, 1, 1
	index = "Shadows-Neutral-1-1-1-Minion-None-Witchy Lackey-Battlecry-Uncollectible"
	needTarget, keyWord, description = True, "", "Battlecry: Transform a friendly minion into one that costs (1) more"
	
	def targetExists(self, choice=0):
		return self.selectableFriendlyMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.ID == self.ID and target != self and target.onBoard
	#不知道如果目标随从被返回我方手牌会有什么结算，可能是在手牌中被进化
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			print("Witchy Lackey's battlecry transforms friendly minion %s into one that costs 1 more."%target.name)
			#The target has changed and needs to be tracked.
			target = self.Game.mutate(target, 1)
		return self, target
		
"""Mana 2 cards"""
class ArcaneServant(Minion):
	Class, race, name = "Neutral", "Elemental", "Arcane Servant"
	mana, attack, health = 2, 2, 3
	index = "Shadows-Neutral-2-2-3-Minion-Elemental-Arcane Servant"
	needTarget, keyWord, description = False, "", ""
	
	
class DalaranLibrarian(Minion):
	Class, race, name = "Neutral", "", "Dalaran Librarian"
	mana, attack, health = 2, 2, 3
	index = "Shadows-Neutral-2-2-3-Minion-None-Dalaran Librarian-Battlecry"
	needTarget, keyWord, description = False, "", "Battlecry: Silences adjacent minions"
	
	def whenEffective(self, target=None, comment="", choice=0):
		if self.onBoard:
			adjacentMinions, distribution = self.Game.findAdjacentMinions(self)
			if adjacentMinions != []:
				print("Dalaran Librarian's battlecry Silences adjacent minions.")
				for minion in adjacentMinions:
					minion.getsSilenced()
		return self, None
		
		
class EvilCableRat(Minion):
	Class, race, name = "Neutral", "Beast", "Evil Cable Rat"
	mana, attack, health = 2, 1, 1
	index = "Shadows-Neutral-2-1-1-Minion-Beast-Evil Cable Rat-Battlecry"
	needTarget, keyWord, description = False, "", "Battlecry: Add a Lackey to your hand"
	
	def whenEffective(self, target=None, comment="", choice=0):
		print("Evil Cable Rat's battlecry adds a random Lackey to player's hand.")
		lackey = np.random.choice(Lackeys)(self.Game, self.ID)
		self.Game.Hand_Deck.addCardtoHand(lackey, self.ID)
		return self, None
		
		
class HenchClanHogsteed(Minion):
	Class, race, name = "Neutral", "Beast", "Hench-Clan Hogsteed"
	mana, attack, health = 2, 2, 1
	index = "Shadows-Neutral-2-2-1-Minion-Beast-Hench-Clan Hogsteed-Rush-Deathrattle"
	needTarget, keyWord, description = False, "", "Deathrattle: Summon a 1/1 Murloc"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [SummonaHenchClanSquire]
		
class SummonaHenchClanSquire(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("Deathrattle: Summon a 1/1 Murloc triggers.")
		self.entity.Game.summonMinion(HenchClanSquire(self.entity.Game, self.entity.ID), self.entity.position+1, self.entity.ID)
		
class HenchClanSquire(Minion):
	Class, race, name = "Neutral", "Murloc", "Hench-Clan Squire"
	mana, attack, health = 1, 1, 1
	index = "Shadows-Neutral-1-1-1-Minion-Murloc-Hench-Clan Squire-Uncollectible"
	needTarget, keyWord, description = False, "", ""
	
	
class ManaReservoir(Minion):
	Class, race, name = "Neutral", "Elemental", "Mana Reservoir"
	mana, attack, health = 2, 0, 6
	index = "Shadows-Neutral-2-0-6-Minion-Elemental-Mana Reservoir-Spell Damage"
	needTarget, keyWord, description = False, "Spell Damage", "Spell Damage +1"
	
	
class SpellbookBinder(Minion):
	Class, race, name = "Neutral", "", "Spellbook Binder"
	mana, attack, health = 2, 2, 3
	index = "Shadows-Neutral-2-2-3-Minion-None-Spellbook Binder-Battlecry"
	needTarget, keyWord, description = False, "", "Battlecry: If you have Spell Damage, draw a card"
	
	def whenEffective(self, target=None, comment="", choice=0):
		haveSpellDamage = False
		if self.Game.playerStatus[self.ID]["Spell Damage"] > 0:
			haveSpellDamage = True
		if haveSpellDamage == False:
			for minion in self.Game.minionsonBoard(self.ID):
				if minion.keyWords["Spell Damage"] > 0:
					haveSpellDamage = True
					break
					
		if haveSpellDamage:
			print("Spellbook Binder's battlecry lets player draws a cards.")
			self.Game.Hand_Deck.drawCard(self.ID)
		return self, None
		
		
class SunreaverSpy(Minion):
	Class, race, name = "Neutral", "", "Sunreaver Spy"
	mana, attack, health = 2, 2, 3
	index = "Shadows-Neutral-2-2-3-Minion-None-Sunreaver Spy-Battlecry"
	needTarget, keyWord, description = False, "", "Battlecry: If you control a Secret, gain +1/+1"
	
	def whenEffective(self, target=None, comment="", choice=0):
		if self.Game.SecretHandler.secrets[self.ID] != []:
			print("Sunreaver Spy's battlecry lets minion gain +1/+1.")
			self.buffDebuff(1, 1)
		return self, None
		
class ZayleShadowCloak(Minion):
	Class, race, name = "Neutral", "", "Zayle. Shadow Cloak"
	mana, attack, health = 2, 3, 2
	index = "Shadows-Neutral-2-3-2-Minion-None-Zayle. Shadow Cloak-Legendary"
	needTarget, keyWord, description = False, "", "You start the game with one of Zayle's EVIL Decks!"
	
"""Mana 3 cards"""
class ArcaneWatcher(Minion):
	Class, race, name = "Neutral", "", "Arcane Watcher"
	mana, attack, health = 3, 5, 6
	index = "Shadows-Neutral-3-5-6-Minion-None-Arcane Watcher"
	needTarget, keyWord, description = False, "", "Can't attack unless you have Spell Damage"
	
	def haveSpellDamage(self):
		if self.Game.playerStatus[self.ID]["Spell Damage"] > 0:
			return True
		for minion in self.Game.minionsonBoard(self.ID):
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
		if self.status["Can't Attack"] or (self.haveSpellDamage() == False and self.silenced == False):
			return False
		return True
		
		
class FacelessRager(Minion):
	Class, race, name = "Neutral", "", "Faceless Rager"
	mana, attack, health = 3, 5, 1
	index = "Shadows-Neutral-3-5-1-Minion-None-Faceless Rager-Battlecry"
	needTarget, keyWord, description = True, "", "Battlecry: Copy a friendly minion's Health"
	
	def targetExists(self, choice=0):
		return self.selectableFriendlyMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.ID == self.ID and target != self and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			print("Faceless Rager's battlecry lets minion copy friendly minion %s's health"%target.name)
			self.statReset(False, target.health)
		return self, target
		
		
class FlightMaster(Minion):
	Class, race, name = "Neutral", "", "Flight Master"
	mana, attack, health = 3, 3, 4
	index = "Shadows-Neutral-3-3-4-Minion-None-Flight Master-Battlecry"
	needTarget, keyWord, description = False, "", "Battlecry: Summon a 2/2 Gryphon for each player"
	
	def whenEffective(self, target=None, comment="", choice=0):
		print("Flight Master's battlecry summons a 2/2 Gryphon for each player.")
		self.Game.summonMinion(Gryphon(self.Game, self.ID), self.position+1, self.ID)
		self.Game.summonMinion(Gryphon(self.Game, self.ID), -1, 3-self.ID)
		return self, None
		
class Gryphon(Minion):
	Class, race, name = "Neutral", "Beast", "Gryphon"
	mana, attack, health = 2, 2, 2
	index = "Shadows-Neutral-2-2-2-Minion-Beast-Gryphon-Uncollectible"
	needTarget, keyWord, description = False, "", ""
	
	
class HenchClanSneak(Minion):
	Class, race, name = "Neutral", "", "Hench-Clan Sneak"
	mana, attack, health = 3, 3, 3
	index = "Shadows-Neutral-3-3-3-Minion-None-Hench-Clan Sneak-Stealth"
	needTarget, keyWord, description = False, "Stealth", "Stealth"
	
	
class MagicCarpet(Minion):
	Class, race, name = "Neutral", "", "Magic Carpet"
	mana, attack, health = 3, 1, 6
	index = "Shadows-Neutral-3-1-6-Minion-None-Magic Carpet"
	needTarget, keyWord, description = False, "", "After you play a 1-Cost minion, give it +1 Attack and Rush"
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
		print("A 1-Cost friendly minion %s is played and %s gives it Poisonous."%(subject.name, self.entity.name))
		subject.getsKeyword("Rush")
		subject.buffDebuff(1, 0)
		
		
class SpellwardJeweler(Minion):
	Class, race, name = "Neutral", "", "Spellward Jeweler"
	mana, attack, health = 3, 3, 4
	index = "Shadows-Neutral-3-3-4-Minion-None-Spellward Jeweler-Battlecry"
	needTarget, keyWord, description = False, "", "Battlecry: Your hero can't be targeted by spells or Hero Powers until your next turn"
	
	def whenEffective(self, target=None, comment="", choice=0):
		print(self.name, " is played and player can't be targeted by Spells or hero powers until next turn.")
		self.Game.playerStatus[self.ID]["Evasive"] += 1
		self.Game.playerStatus[self.ID]["EvasiveTillYourNextTurn"] += 1
		return self, None
		
"""Mana 4 cards"""
class ArchmageVargoth(Minion):
	Class, race, name = "Neutral", "", "Archmage Vargoth"
	mana, attack, health = 4, 2, 6
	index = "Shadows-Neutral-4-2-6-Minion-None-Archmage Vargoth-Legendary"
	needTarget, keyWord, description = False, "", "At the end of your turn, cast a spell you've cast this turn (targets chosen randomly)"
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
		for index in self.entity.Game.CounterHandler.cardsPlayedThisTurn[self.entity.ID]:
			if "-Spell-" in index:
				spells.append(index)
		if spells != []:
			spell = np.random.choice(spells)
			print("At the end of turn, %s casts spell %s that player has cast this turn."%(self.entity.name, spell.name))
			spell.cast()
			
			
class Hecklebot(Minion):
	Class, race, name = "Neutral", "Mech", "Hecklebot"
	mana, attack, health = 4, 3, 8
	index = "Shadows-Neutral-4-3-8-Minion-Mech-Hecklebot-Taunt-Battlecry"
	needTarget, keyWord, description = False, "Taunt", "Taunt. Battlecry: Your opponent summons a minion from their deck"
	
	def whenEffective(self, target=None, comment="", choice=0):
		if self.Game.spaceonBoard(3-self.ID) > 0:
			minions = []
			for card in self.Game.Hand_Deck.decks[3-self.ID]:
				if card.cardType == "Minion":
					minions.append(card)
					
			print("Hecklebot's battlecry lets opponent summon a minion from deck.")
			if minions != []:
				self.Game.summonfromDeck(np.random.choice(minions), -1, self.ID)
		return self, None
		
		
class HenchClanHag(Minion):
	Class, race, name = "Neutral", "", "Hench-Clan Hag"
	mana, attack, health = 4, 3, 3
	index = "Shadows-Neutral-4-3-3-Minion-None-Hench-Clan Hag-Battlecry"
	needTarget, keyWord, description = False, "", "Battlecry: Summon two 1/1 Amalgams with all minions types"
	
	def whenEffective(self, target=None, comment="", choice=0):
		print("Hench-Clan Hag's battlecry summons two 1/1 Amalgams with all minion types.")
		pos = (self.position, "leftandRight") if self.onBoard else (-1, "totheRightEnd")
		self.Game.summonMinion([Amalgam(self.Game, self.ID) for i in range(2)], pos, self.ID)
		return self, None
		
class Amalgam(Minion):
	Class, race, name = "Neutral", "Elemental, Mech, Demon, Murloc, Dragon, Beast, Pirate, Totem", "Amalgam"
	mana, attack, health = 1, 1, 1
	index = "Shadows-Neutral-1-1-1-Minion-Beast-Murloc-Pirate-Mech-Totem-Demon-Elemental-Dragon-Amalgam-Uncollectible"
	needTarget, keyWord, description = False, "", "This is an Elemental, Mech, Demon, Murloc, Dragon, Beast, Pirate and Totem"
	
	
class PortalKeeper(Minion):
	Class, race, name = "Neutral", "Demon", "Portal Keeper"
	mana, attack, health = 4, 5, 2
	index = "Shadows-Neutral-4-5-2-Minion-Demon-Portal Keeper-Battlecry"
	needTarget, keyWord, description = False, "", "Battlecry: Shuffle 3 Portals into your deck. When drawn, summon a 2/2 Demon with Rush"
	
	def whenEffective(self, target=None, comment="", choice=0):
		print("Portal Keeper's battlecry shuffles 3 Portals into player's deck.")
		portals = [FelhoundPortal(self.Game, self.ID) for i in range(3)]
		self.Game.Hand_Deck.shuffleCardintoDeck(portals, self.ID)
		return self, None
		
class FelhoundPortal(Spell):
	Class, name = "Neutral", "Felhound Portal"
	needTarget, mana = False, 2
	index = "Shadows-Neutral-2-Spell-Felhound Portal-Casts When Drawn"
	description = "Casts When Drawn. Summon a 2/2 Felhound with Rush"
	def whenEffective(self, target=None, comment="", choice=0):
		print("Felhound Portal is cast and summons a 2/2 Felhound with Rush.")
		self.Game.summonMinion(Felhound(self.Game, self.ID), -1, self.ID)
		return None
		
class Felhound(Minion):
	Class, race, name = "Neutral", "Demon", "Felhound"
	mana, attack, health = 2, 2, 2
	index = "Shadows-Neutral-2-2-2-Minion-Demon-Felhound-Rush-Uncollectible"
	needTarget, keyWord, description = False, "Rush", "Rush"
	
	
class ProudDefender(Minion):
	Class, race, name = "Neutral", "Demon", "Felhound"
	mana, attack, health = 4, 2, 6
	index = "Shadows-Neutral-4-2-6-Minion-None-Proud Defender-Taunt"
	needTarget, keyWord, description = False, "Taunt", "Taunt. Has +2 Attack while you have no other minions"
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
				print("Proud Defender gains +2 Attack because there's no other friendly minion")
				self.statChange(2, 0)
				self.activated = True
			elif noOtherFriendlyMinions == False and self.activated:
				print("Proud Defender loses +2 Attack because there are other friendly minions")
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
		print("%s checks board due to board change."%self.entity.name)
		self.entity.checkBoard()
		
		
class SoldierofFortune(Minion):
	Class, race, name = "Neutral", "Elemental", "Soldier of Fortune"
	mana, attack, health = 4, 5, 6
	index = "Shadows-Neutral-4-5-6-Minion-Elemental-Soldier of Fortune"
	needTarget, keyWord, description = False, "", "Whenever this minion attacks, give your opponent a coin"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_SoldierofFortune(self)]
		
class Trigger_SoldierofFortune(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionAttacksMinion", "MinionAttacksHero"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject == self.entity
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("Whenever it attacks, %s gives opponent a Coin."%self.entity.name)
		self.entity.Game.Hand_Deck.addCardtoHand(TheCoin(self.entity.Game, 3-self.entity.ID), 3-self.entity.ID)
		
		
class TravelingHealer(Minion):
	Class, race, name = "Neutral", "", "Traveling Healer"
	mana, attack, health = 4, 3, 2
	index = "Shadows-Neutral-4-3-2-Minion-None-Traveling Healer-Battlecry-Divine Shield"
	needTarget, keyWord, description = True, "Divine Shield", "Divine Shield. Battlecry: Restore 3 Health."
	
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			heal = 3 * (2 ** self.countHealDouble())
			self.restoresHealth(target, heal)
		return self, target
		
		
class VioletSpellsword(Minion):
	Class, race, name = "Neutral", "", "Violet Spellsword"
	mana, attack, health = 4, 1, 6
	index = "Shadows-Neutral-4-1-6-Minion-None-Violet Spellsword-Battlecry"
	needTarget, keyWord, description = False, "", "Battlecry: Gain +1 Attack for each spell in your hand"
	
	def whenEffective(self, target=None, comment="", choice=0):
		numSpells = 0
		for card in self.Game.Hand_Deck.hands[self.ID]:
			if card.cardType == "Spell":
				numSpells += 1
				
		print("Violet Spellward's battlecry lets the minion gain +1 health for every card in player's hand")
		self.buffDebuff(numSpells, 0)
		return self, None
		
"""Mana 5 cards"""
class AzeriteElemental(Minion):
	Class, race, name = "Neutral", "Elemental", "Azerite Elemental"
	mana, attack, health = 5, 2, 7
	index = "Shadows-Neutral-5-2-7-Minion-Elemental-Azerite Elemental"
	needTarget, keyWord, description = False, "", "At the start of your turn, gain Spell Damage +2"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_AzeriteElemental(self)]
		
class Trigger_AzeriteElemental(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["TurnStarts"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("At the start of turn, %s gains Spell Damage +2"%self.entity.name)
		self.entity.getsKeyword("Spell Damage")
		self.entity.getsKeyword("Spell Damage")
		
		
class BaristaLinchen(Minion):
	Class, race, name = "Neutral", "", "Barista Linchen"
	mana, attack, health = 5, 4, 5
	index = "Shadows-Neutral-5-4-5-Minion-None-Barista Linchen-Battlecry-Legendary"
	needTarget, keyWord, description = False, "", "Battlecry: Add a copy of each of your other Battlecry minions to your hand"
	
	def whenEffective(self, target=None, comment="", choice=0):
		battlecryMinions = []
		for minion in self.Game.minions[self.ID]:
			if "-Battlecry" in minion.index:
				battlecryMinions.append(minion)
		if battlecryMinions != []:
			print("Barista Linchen's battlecry adds copies of all other friendly Battlecry minions to player's hand.")
			for minion in battlecryMinions:
				self.Game.Hand_Deck.addCardtoHand(type(minion)(self.Game, self.ID), self.ID)
		return self, None
		
		
class DalaranCrusader(Minion):
	Class, race, name = "Neutral", "", "Dalaran Crusader"
	mana, attack, health = 5, 5, 4
	index = "Shadows-Neutral-5-5-4-Minion-None-Dalaran Crusader-Divine Shield"
	needTarget, keyWord, description = False, "Divine Shield", "Divine Shield"
	
	
class RecurringVillain(Minion):
	Class, race, name = "Neutral", "", "Recurring Villain"
	mana, attack, health = 5, 3, 6
	index = "Shadows-Neutral-5-3-6-Minion-None-Recurring Villain-Deathrattle"
	needTarget, keyWord, description = False, "", "Deathrattle: If this minion has 4 or more Attack, resummon it"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID, mana_0, attack_0,	health_0)
		self.deathrattles = [ResummonifAttackGreaterthan3(self)]
		
class ResummonifAttackGreaterthan3(Deathrattle_Minion):
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return target == self.entity and number > 3
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("Deathrattle: Resummon the minion %s triggers."%self.entity.name)
		newMinion = type(self.entity)(self.entity.Game, self.entity.ID)
		self.entity.Game.summonMinion(newMinion, self.entity.position+1, self.entity.ID)
		
		
class SunreaverWarmage(Minion):
	Class, race, name = "Neutral", "", "Sunreaver Warmage"
	mana, attack, health = 5, 4, 4
	index = "Shadows-Neutral-5-4-4-Minion-None-Sunreaver Warmage-Battlecry"
	needTarget, keyWord, description = True, "", "Battlecry: If you're holding a spell costs (5) or more, deal 4 damage"
	
	def returnTrue(self, choice=0):
		return self.Game.Hand_Deck.holdingSpellwith5CostorMore(self.ID)
		
	def effectCanTrigger(self):
		return self.Game.Hand_Deck.holdingSpellwith5CostorMore(self.ID)
		
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None and self.Game.Hand_Deck.holdingSpellwith5CostorMore(self.ID):
			print("Sunreaver Warmage's battlecry deals 4 damage to target", target.name)
			target.takesDamage(self, 4)
		return self, target
		
"""Mana 6 cards"""
class EccentricScribe(Minion):
	Class, race, name = "Neutral", "", "Eccentric Scribe"
	mana, attack, health = 6, 6, 4
	index = "Shadows-Neutral-6-6-4-Minion-None-Eccentric Scribe-Deathrattle"
	needTarget, keyWord, description = False, "", "Deathrattle: Summon four 1/1 Vengeful Scrolls"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [Summon4VengefulScrolls(self)]
		
def Summon4VengefulScrolls(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		pos = (self.entity.position, "totheRight") if self.entity in self.entity.Game.minions[self.entity.ID] else (-1, "totheRightEnd")
		print("Deathrattle: Summon four 1/1 Vengeful Scrolls triggers.")
		self.entity.Game.summonMinion([VengefulScroll(self.entity.Game, self.entity.ID) for i in range(4)], pos, self.entity.ID)
		
class VengefulScroll(Minion):
	Class, race, name = "Neutral", "", "Vengeful Scroll"
	mana, attack, health = 1, 1, 1
	index = "Shadows-Neutral-1-1-1-Minion-None-Vengeful Scroll-Uncollectible"
	needTarget, keyWord, description = False, "", ""
	
	
class MadSummoner(Minion):
	Class, race, name = "Neutral", "Demon", "Mad Summoner"
	mana, attack, health = 6, 4, 4
	index = "Shadows-Neutral-6-4-4-Minion-Demon-Mad Summoner-Battlecry"
	needTarget, keyWord, description = False, "", "Battlecry: Fill each player's board with 1/1 Imps"
	#假设是轮流为我方和对方召唤两个小鬼
	def whenEffective(self, target=None, comment="", choice=0):
		print("Mad Summoner's battlecry fills the Board with 1/1 Imps.")
		while True:
			friendlyBoardNotFull, enemyBoardNotFull = True, True
			if self.Game.spaceonBoard(self.ID) > 0:
				self.Game.summonMinion([Imp_RiseofShadows(self.Game, self.ID) for i in range(2)], (-1, "totheRightEnd"), self.ID)
			else:
				friendlyBoardNotFull = False
			if self.Game.spaceonBoard(3-self.ID) > 0:
				self.Game.summonMinion([Imp_RiseofShadows(self.Game, 3-self.ID) for i in range(2)], (-1, "totheRightEnd"), 3-self.ID)
			else:
				enemyBoardNotFull = False
			if friendlyBoardNotFull == False and enemyBoardNotFull == False:
				break
				
		return self, None
		
class Imp_RiseofShadows(Minion):
	Class, race, name = "Neutral", "Demon", "Imp"
	mana, attack, health = 1, 1, 1
	index = "Shadows-Neutral-1-1-1-Minion-Demon-Imp-Uncollectible"
	needTarget, keyWord, description = False, "", ""
	
	
class PortalOverfiend(Minion):
	Class, race, name = "Neutral", "Demon", "Portal Overfiend"
	mana, attack, health = 6, 5, 6
	index = "Shadows-Neutral-6-5-6-Minion-Demon-Portal Overfiend-Battlecry"
	needTarget, keyWord, description = False, "", "Battlecry: Shuffle 3 Portals into your deck. When drawn, summon a 2/2 Demon with Rush"
	
	
	def whenEffective(self, target=None, comment="", choice=0):
		print("Portal Overfiend's battlecry shuffles 3 Portals into player's deck.")
		portals = [FelhoundPortal(self.Game, self.ID) for i in range(3)]
		self.Game.Hand_Deck.shuffleCardintoDeck(portals, self.ID)
		return self, None
		
		
class Safeguard(Minion):
	Class, race, name = "Neutral", "Mech", "Safeguard"
	mana, attack, health = 6, 4, 5
	index = "Shadows-Neutral-6-4-5-Minion-Mech-Safeguard-Taunt-Deathrattle"
	needTarget, keyWord, description = False, "Taunt", "Taunt. Deathrattle: Summon a 0/5 Vault Safe with Taunt"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [SummonaVaultSafe(self)]
		
class SummonaVaultSafe(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("Deathrattle: Summon a 0/5 Vault Safe triggers.")
		self.entity.Game.summonMinion(VaultSafe(self.entity.Game, self.entity.ID), self.entity.position+1, self.entity.ID)
		
class VaultSafe(Minion):
	Class, race, name = "Neutral", "Mech", "Vault Safe"
	mana, attack, health = 2, 0, 5
	index = "Shadows-Neutral-2-0-5-Minion-Mech-Vault Safe-Taunt-Uncollectible"
	needTarget, keyWord, description = False, "Taunt", "Taunt"
	
	
class UnseenSaboteur(Minion):
	Class, race, name = "Neutral", "", "Unseen Saboteur"
	mana, attack, health = 6, 5, 6
	index = "Shadows-Neutral-6-5-6-Minion-None-Unseen Saboteur-Battlecry"
	needTarget, keyWord, description = False, "", "Battlecry: Your opponent casts a random spell from their hand (targets chosen randomly)"
	
	def whenEffective(self, target=None, comment="", choice=0):
		print("Unseen Saboteur's battlecry lets opponent cast a random spell from hand with random target.")
		spellsinHand = []
		for card in self.Game.Hand_Deck.hands[3-self.ID]:
			if card.cardType == "Spell":
				spellsinHand.append(card)
				
		if spellsinHand != []:
			spelltoCast = np.random.choice(spellsinHand)
			self.Game.Hand_Deck.extractfromHand(spelltoCast)
			spelltoCast.cast()
		return self, None
		
		
class VioletWarden(Minion):
	Class, race, name = "Neutral", "", "Violet Warden"
	mana, attack, health = 6, 4, 7
	index = "Shadows-Neutral-6-4-7-Minion-None-Violet Warden-Taunt-Spell Damage"
	needTarget, keyWord, description = False, "Taunt,Spell Damage", "Taunt, Spell Damage +1"
	
"""Mana 7 cards"""
class ChefNomi(Minion):
	Class, race, name = "Neutral", "", "Chef Nomi"
	mana, attack, health = 7, 6, 6
	index = "Shadows-Neutral-7-6-6-Minion-None-Chef Nomi-Battlecry-Legendary"
	needTarget, keyWord, description = False, "", "Battlecry: If your deck is empty, summon six 6/6 Greasefire Elementals"
	
	def whenEffective(self, target=None, comment="", choice=0):
		if self.Game.Hand_Deck.decks[self.ID] == []:
			print("Chef Nomi's battlecry fills the player's board with 6/6 Greasefire Elementals.")
			if self.onBoard:
				self.Game.summonMinion([GreasefireElemental(self.Game, self.ID) for i in range(6)], (self.position, "leftandRight"), self.ID)
			else:
				self.Game.summonMinion([GreasefireElemental(self.Game, self.ID) for i in range(7)], (-1, "totheRightEnd"), self.ID)
		return self, None
		
class GreasefireElemental(Minion):
	Class, race, name = "Neutral", "Elemental", "Greasefire Elemental"
	mana, attack, health = 6, 6, 6
	index = "Shadows-Neutral-6-6-6-Minion-Elemental-Greasefire Elemental-Uncollectible"
	needTarget, keyWord, description = False, "", ""
	
	
class ExoticMountseller(Minion):
	Class, race, name = "Neutral", "", "Exotic Mountseller"
	mana, attack, health = 7, 5, 8
	index = "Shadows-Neutral-7-5-8-Minion-None-Exotic Mountseller"
	needTarget, keyWord, description = False, "", "Whenever you cast a spell, summon a random 3-Cost Beast"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_ExoticMountseller]
		self.cost3Beasts = []
		for key, value in self.Game.MinionswithRace["Beast"].items():
			if key.split('-')[2] == '3':
				self.cost3Beasts.append(value)
				
class Trigger_ExoticMountseller(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["SpellPlayed"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject.ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("Player casts a spell and %s summons a random cost-3 Beast."%self.entity.name)
		beast = np.random.choice(self.entity.cost3Beasts)(self.entity.Game, self.entity.ID)
		self.entity.Game.summonMinion(beast(self.entity.Game, self.entity.ID), self.entity.position+1, self.entity.ID)
		
		
class TunnelBlaster(Minion):
	Class, race, name = "Neutral", "", "Tunnel Blaster"
	mana, attack, health = 7, 3, 8
	index = "Shadows-Neutral-7-3-8-Minion-None-Tunnel Blaster-Taunt-Deathrattle"
	needTarget, keyWord, description = False, "Taunt", "Taunt. Deathrattle: Deal 3 damage to all minions"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [Deal3DamagetoAllMinions(self)]
		
class Deal3DamagetoAllMinions(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		targets = self.entity.Game.minionsonBoard(1) + self.entity.Game.minionsonBoard(2)
		damages = [3 for obj in targets]
		print("Deathrattle: Deal 3 damage to all minions triggers.")
		self.entity.dealsAOE(targets, damages)
		
		
class UnderbellyOoze(Minion):
	Class, race, name = "Neutral", "", "Underbelly Ooze"
	mana, attack, health = 7, 3, 5
	index = "Shadows-Neutral-7-3-5-Minion-None-Underbelly Ooze"
	needTarget, keyWord, description = False, "", "After this minion survives damage, summon a copy of it"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_UnderbellyOoze(self)]
		
class Trigger_UnderbellyOoze(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionTakesDamage"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and target == self.entity and self.entity.health > 0 and self.entity.dead == False
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("%s survives damage and summon a copy of itself."%self.entity.name)
		Copy = self.entity.selfCopy(self.entity.ID)
		self.entity.Game.summonMinion(Copy, self.entity.position+1, self.entity.ID)
		
"""Mana 8 cards"""
class Batterhead(Minion):
	Class, race, name = "Neutral", "", "Batterhead"
	mana, attack, health = 8, 3, 12
	index = "Shadows-Neutral-8-3-12-Minion-None-Batterhead-Rush"
	needTarget, keyWord, description = False, "Rush", "Rush. After this attacks and kills a minion, it may attack again"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_Batterhead(self)]
		
class Trigger_Batterhead(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionAttackedMinion"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and self.entity.health > 0 and self.entity.dead == False and (target.health < 1 or target.dead == True)
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("After %s attacks and kills a minion %s, it gains an extra attack chance."%(self.entity.name, target.name))
		self.entity.attChances_extra += 1
		
		
class HeroicInnkeeper(Minion):
	Class, race, name = "Neutral", "", "Heroic Innkeeper"
	mana, attack, health = 8, 4, 4
	index = "Shadows-Neutral-8-4-4-Minion-None-Heroic Innkeeper-Taunt-Battlecry"
	needTarget, keyWord, description = False, "Taunt", "Taunt. Battlecry: Gain +2/+2 for each other friendly minion"
	
	def whenEffective(self, target=None, comment="", choice=0):
		if self.onBoard or self.inHand:
			targets = self.minionsonBoard(self.ID)
			extractfrom(self, targets)
			buff = 2 * len(targets)
		print("Heroic Innkeeper's battlecry gives minion +2/+2 for each other friendly minion.")
		self.buffDebuff(buff, buff)
		return self, None
		
		
class JepettoJoybuzz(Minion):
	Class, race, name = "Neutral", "", "Jepetto Joybuzz"
	mana, attack, health = 8, 6, 6
	index = "Shadows-Neutral-8-6-6-Minion-None-Jepetto Joybuzz-Battlecry-Legendary"
	needTarget, keyWord, description = False, "", "Battlecry: Draw 2 minions from your deck. Set their Attack, Health, and Cost to 1"
	
	def whenEffective(self, target=None, comment="", choice=0):
		print("Jepetto Joybuzz's battlecry draws 2 minions from player's deck and sets their Attack, Health and Cost to 1")
		minionsinDeck = []
		for card in self.Game.Hand_Deck.decks[self.ID]:
			if card.cardType == "Minion":
				minionsinDeck.append(card)
				
		if minionsinDeck != []:
			if len(minionsinDeck) == 1:
				card, mana = self.Game.Hand_Deck.drawCard(minionsinDeck[0])
				if card != None:
					card.mana_set = 1
					self.Game.ManaHandler.calcMana_Single(card)
			else:
				cards = np.random.choice(minionsinDeck, 2, replace=True)
				for i in range(2):
					card, mana = self.Game.Hand_Deck.drawCard(cards[i])
					if card != None:
						card.mana_set = 1
						self.Game.ManaHandler.calcMana_Single(card)
		return self, None
		
		
class WhirlwindTempest(Minion):
	Class, race, name = "Neutral", "Elemental", "Whirlwind Tempest"
	mana, attack, health = 8, 6, 6
	index = "Shadows-Neutral-8-6-6-Minion-Elemental-Whirlwind Tempest"
	needTarget, keyWord, description = False, "", "Your Windfury minions have Mega Windfury"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.auras["Has Aura"] = HasAura_Dealer(self, self.applicable, "Mega Windfury")
		
	def applicable(self, target):
		return target.keyWords["Windfury"] > 0
		
"""Mana 9 cards"""
class BurlyShovelfist(Minion):
	Class, race, name = "Neutral", "", "Burly Shovelfist"
	mana, attack, health = 9, 9, 9
	index = "Shadows-Neutral-9-9-9-Minion-None-Burly Shovelfist-Rush"
	needTarget, keyWord, description = False, "Rush", "Rush"
	
	
class ArchivistElysiana(Minion):
	Class, race, name = "Neutral", "", "Archivist Elysiana"
	mana, attack, health = 9, 7, 7
	index = "Shadows-Neutral-9-7-7-Minion-None-Archivist Elysiana-Battlecry-Legendary"
	needTarget, keyWord, description = False, "", "Battlecry: Discover 5 cards. Replace your deck with 2 copies of each"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.newDeck = []
		
	def whenEffective(self, target=None, comment="", choice=0):
		Class = self.Game.heroes[self.ID].Class
		possibilities = []
		possibilities += list(self.Game.NeutralMinions.values())
		possibilities += list(self.Game.ClassCards[Class].values())
		self.newDeck = []
		if comment == "InvokedbyOthers":
			for i in range(5):
				newCard = np.random.choice(possibilities)
				self.newDeck.append(newCard(self.Game, self.ID))
				self.newDeck.append(newCard(self.Game, self.ID))
		else:
			for i in range(5):
				cards = np.random.choice(possibilities, 3, replace=False)
				self.Game.options = [card(self.Game, self.ID) for card in cards]
				self.Game.DiscoverHandler.startDiscover(self)
				
		self.Game.Hand_Deck.extractfromDeck(None, all=True, ID=self.ID)
		self.Game.Hand_Deck.decks[self.ID] = self.newDeck
		np.random.shuffle(self.Game.Hand_Deck.decks[self.ID])
		self.newDeck = []
		return self, None
		
	def discoverDecided(self, option):
		print("Two copies of %s added to the deck replacement."%option.name)
		self.newDeck.append(option)
		self.newDeck.append(type(option)(self.Game, self.ID))
		
"""Mana 10 cards"""		
class BigBadArchmage(Minion):
	Class, race, name = "Neutral", "", "Big Bad Archmage"
	mana, attack, health = 10, 6, 6
	index = "Shadows-Neutral-10-6-6-Minion-None-Big Bad Archmage"
	needTarget, keyWord, description = False, "", "At the end of your turn, summon a random 6-Cost minion"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_BigBadArchmage(self)]
		
class Trigger_BigBadArchmage(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["TurnEnds"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("At the end of turn, %s summons a 6-Cost minion."%self.entity.name)
		minion = np.random.choice(list(self.entity.Game.MinionswithCertainCost[6].values()))
		self.entity.Game.summonMinion(minion(self.entity.Game, self.entity.ID), self.entity.position+1, self.entity.ID)
		
"""Druid cards"""
class Acornbearer(Minion):
	Class, race, name = "Druid", "", "Acornbearer"
	mana, attack, health = 1, 2, 1
	index = "Shadows-Druid-1-2-1-Minion-None-Acornbearer-Deathrattle"
	needTarget, keyWord, description = False, "", "Deathrattle: Add two 1/1 Squirrels to your hand"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [AddTwoSquirrelstoHand(self)]
		
class AddTwoSquirrelstoHand(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("Deathrattle: Summon a 2/1 Damaged Golem triggers.")
		self.entity.Game.Hand_Deck.addCardtoHand([Squirrel, Squirrel], self.entity.ID, "CreateUsingType")
		
class Squirrel(Minion):
	Class, race, name = "Neutral", "Beast", "Squirrel"
	mana, attack, health = 1, 1, 1
	index = "Shadows-Druid-1-1-1-Minion-Beast-Squirrel-Uncollectible"
	needTarget, keyWord, description = False, "", ""
	
	
class CrystalPower(Spell):
	Class, name = "Druid", "Crystal Power"
	needTarget, mana = True, 1
	index = "Shadows-Druid-1-Spell-Crystal Power-Choose One"
	description = "Choose One- Deal 2 damage to a minion; or Restore 5 Health"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.chooseOne = 1
		self.options = [PiercingThorns_Option(self), HealingBlossom_Option(self)]
		
	#available() only needs to check selectableCharacerExists
	def targetCorrect(self, target, choice=0):
		if choice == "ChooseBoth" or choice == 1:
			return (target.cardType == "Minion" or target.cardType == "Hero") and target.onBoard
		else:
			return target.cardType == "Minion" and target.onBoard
			
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			#When Choosing Both, it deals damage first and then heals
			if (choice == "ChooseBoth" or choice == 0) and target.cardType == "Minion":
				damage = (2 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
				self.dealsDamage(target, damage)
			#If the minion is killed, it won't be healed.
			if choice == "ChooseBoth" or choice == 1:
				if target.cardType != "Minion" or target.health > 0:
					heal = 5 * (2 ** self.countHealDouble())
					self.restoresHealth(target, heal)
		return target
		
class PiercingThorns_Option:
	def __init__(self, spell):
		self.spell = spell
		self.name = "Piercing Thorns"
		self.description = "2 damage to minion"
		self.index = "Shadows-Druid-1-Spell-Piercing Thorns-Uncollectible"
		
	def available(self):
		return self.spell.selectableMinionExists()
		
class HealingBlossom_Option:
	def __init__(self, spell):
		self.spell = spell
		self.name = "Healing Blossom"
		self.description = "Heal 5"
		self.index = "Shadows-Druid-1-Spell-Healing Blossom-Uncollectible"
		#available() is the generic method for all targeting spells
		
class PiercingThorns(Spell):
	Class, name = "Druid", "Piercing Thorns"
	needTarget, mana = True, 1
	index = "Shadows-Druid-1-Spell-Piercing Thorns-Uncollectible"
	description = "Deal 2 damage to a minion"
	
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			damage = (2 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			print("Piercing Thorns is cast and deals %d damage to"%damage, target.name)
			self.dealsDamage(target, damage)
		return target
		
class HealingBlossom(Spell):
	Class, name = "Druid", "Healing Blossom"
	needTarget, mana = True, 1
	index = "Shadows-Druid-1-Spell-Healing Blossom-Uncollectible"
	description = "Restores 5 Health"
	
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			heal = 5 * (2 ** self.countHealDouble())
			print("Healing Blossom is cast and restores %d health to"%heal, target.name)
			self.restoresHealth(target, heal)
		return target
		
		
class CrystalsongPortal(Spell):
	Class, name = "Druid", "Crystalsong Portal"
	needTarget, mana = False, 2
	index = "Shadows-Druid-2-Spell-Crystalsong Portal"
	description = "Discover a Druid minion. If your hand has no minions, keep all 3"
	
	def randomorDiscover(self):
		handHasMinion = False
		for card in self.Game.Hand_Deck.hands[self.ID]:
			if card.cardType == "Minion":
				handHasMinion = True
				return "Discover"
		return "Random"
		
	def whenEffective(self, target=None, comment="", choice=0):
		handHasMinion = False
		for card in self.Game.Hand_Deck.hands[self.ID]:
			if card.cardType == "Minion":
				handHasMinion = True
				break
		minions = []
		for key, value in self.Game.ClassCards["Druid"].items():
			if "-Minion-" in key:
				minions.append(value)
		minions = np.random.choice(minions, 3, replace=False)
		if handHasMinion == False:
			print("Crystalsong Portal is cast and adds all three Druid minions to player's hand.")
			self.Game.Hand_Deck.addCardtoHand(minions, self.ID, "CreateUsingType")
		else:
			if comment == "CastbyOthers":
				print("Crystalsong Portal is cast and adds a random Druid minion to player's hand")
				self.Game.Hand_Deck.addCardtoHand(np.random.choice(minions), self.ID, "CreateUsingType")
			else:
				print("Crystalsong Portal is cast and lets player discover a Druid Minion.")
				self.Game.options = [minion(self.Game, self.ID) for minion in minions]
				self.Game.DiscoverHandler.startDiscover(self)
				
		return None
		
	def discoverDecided(self, option):
		rint("Minion ", option.name, " is put into player's hand.")
		self.Game.Hand_Deck.addCardtoHand(option, self.ID)
		
		
class DreamwayGuardians(Spell):
	Class, name = "Druid", "Dreamway Guardians"
	needTarget, mana = False, 2
	index = "Shadows-Druid-2-Spell-Dreamway Guardians"
	description = "Summon two 1/2 Dryads with Lifesteal"
	def available(self):
		return self.Game.spaceonBoard(self.ID) > 0
		
	def whenEffective(self, target=None, comment="", choice=0):
		print("Dreamway Guardians is played and summons two 1/2 Dryads with Lifesteal.")
		self.Game.summonMinion([Dryad(self.Game, self.ID) for i in range(2)], (-1, "totheRightEnd"), self.ID)
		return None
		
class Dryad(Minion):
	Class, race, name = "Druid", "", "Dryad"
	mana, attack, health = 1, 1, 2
	index = "Shadows-Druid-1-1-2-Minion-None-Dryad-Lifesteal-Uncollectible"
	needTarget, keyWord, description = False, "Lifesteal", "Lifesteal"
	
	
class KeeperStalladris(Minion):
	Class, race, name = "Druid", "", "Keeper Stalladris"
	mana, attack, health = 2, 2, 3
	index = "Shadows-Druid-2-2-3-Minion-None-Keeper Stalladris-Legendary"
	needTarget, keyWord, description = False, "", "After you cast a Choose One spell, add copies of both choices to your hand"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_KeeperStalladris(self)]
		
class Trigger_KeeperStalladris(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["SpellBeenPlayed"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject.ID == self.entity.ID and subject.chooseOne > 0
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("After player casts spell %s, %s adds copies of both choices to player's hand."%(subject.name, self.entity.name))
		for option in subject.options:
			self.entity.Game.Hand_Deck.addCardtoHand(option.index, self.entity.ID, "CreateUsingIndex")
			
			
class Lifeweaver(Minion):
	Class, race, name = "Druid", "", "Lifeweaver"
	mana, attack, health = 3, 2, 5
	index = "Shadows-Druid-3-2-5-Minion-None-Lifeweaver"
	needTarget, keyWord, description = False, "", "Whenever you restore Health, add a random Druid spell to your hand"
	def __init__(self, Game, ID,):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_Lifeweaver(self)]
		self.druidSpells = []
		for key, value in self.Game.ClassCards["Druid"].items():
			if "-Spell-" in key:
				self.druidSpells.append(value)
				
class Trigger_Lifeweaver(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionGetsHealed", "HeroGetsHealed"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject.ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("Player restores Health, and %s adds a random Druid spell to player's hand."%self.entity.name)
		self.entity.Game.Hand_Deck.addCardtoHand(np.random.choice(self.entity.druidSpells), self.entity.ID, "CreateUsingType")
		
		
class CrystalStag(Minion):
	Class, race, name = "Druid", "Beast", "Crystal Stag"
	mana, attack, health = 5, 4, 4
	index = "Shadows-Druid-5-4-4-Minion-Beast-Crystal Stag-Rush-Battlecry"
	needTarget, keyWord, description = False, "Rush", "Rush. Battlecry: If you've restored 5 Health this game, summon a copy of this"
	
	def whenEffective(self, target=None, comment="", choice=0):
		if self.Game.healthRestored[self.ID] > 4:
			print("Crystal Stag's battlecry summons a copy of itself.")
			Copy = self.selfCopy(self.ID)
			self.Game.summonMinion(Copy, self.position+1, self.ID)
		return self, None
		
		
class BlessingoftheAncients_Twinspell(Spell):
	Class, name = "Druid", "Blessing of the Ancients"
	needTarget, mana = False, 3
	index = "Shadows-Druid-3-Spell-Blessing of the Ancients-Twinspell"
	description = "Twinspell. Give your minions +1/+1"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.twinSpell = 1
		
	def whenEffective(self, target=None, comment="", choice=0):
		print("Blessing of the Ancients is played and gives all friendly minions +1/+1.")
		for minion in self.Game.minionsonBoard(self.ID):
			minion.buffDebuff(1, 1)
		return None
		
class BlessingoftheAncients(Spell):
	Class, name = "Druid", "Blessing of the Ancients"
	needTarget, mana = False, 3
	index = "Shadows-Druid-3-Spell-Blessing of the Ancients-Uncollectible"
	description = "Give your minions +1/+1"
	
	def whenEffective(self, target=None, comment="", choice=0):
		print("Blessing of the Ancients is played and gives all friendly minions +1/+1.")
		for minion in self.Game.minionsonBoard(self.ID):
			minion.buffDebuff(1, 1)
		return None
		
		
class Lucentbark(Minion):
	Class, race, name = "Druid", "", "Lucentbark"
	mana, attack, health = 8, 4, 8
	index = "Shadows-Druid-8-4-8-Minion-None-Lucentbark-Taunt-Deathrattle-Legendary"
	needTarget, keyWord, description = False, "Taunt", "Taunt. Deathrattle: Go dormant. Restore 5 Health to awaken this minion"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [BecomeSpiritofLucentbark(self)]
		
class BecomeSpiritofLucentbark(Deathrattle_Minion):
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return target == self.entity and self.entity.Game.spaceonBoard(self.entity.ID) > 0
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("Deathrattle: Turn into Spirit of Lucentbark triggers")
		permanent = SpiritofLucentbark(self.entity.Game, self.entity.ID)
		self.entity.Game.transform(self.entity, permanent)
		
class SpiritofLucentbark(Permanent):
	Class, name = "Druid", "Spirit of Lucentbark"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.healthRestored = 0
		self.triggersonBoard = [Trigger_SpiritofLucentbark(self)]
		
class Trigger_SpiritofLucentbark(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionGetsHealed", "HeroGetsHealed"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject.ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("Player restores %d Health, and %s's counter records it."%(number, self.entity.name))
		self.entity.healthRestored += number
		if self.entity.healthRestored > 4:
			print("Spirit of Lucentbark transforms into Lucentbark")
			self.entity.Game.transform(self.entity, Lucentbark(self.entity.Game, self.entity.ID))
			
			
class TheForestsAid_Twinspell(Spell):
	Class, name = "Druid", "The Forest's Aid"
	needTarget, mana = False, 8
	index = "Shadows-Druid-8-Spell-The Forest's Aid-Twinspell"
	description = "Twinspell. Summon five 2/2 Treants"
	
	def whenEffective(self, target=None, comment="", choice=0):
		print("The Forest's Aid is played and summons five 2/2 Treants.")
		self.Game.summonMinion([Treant(self.Game, self.ID) for i in range(5)], (-1, "totheRightEnd"), self.ID)
		return None
		
class TheForestsAid(Spell):
	Class, name = "Druid", "The Forest's Aid"
	needTarget, mana = False, 8
	index = "Shadows-Druid-8-Spell-The Forest's Aid-Uncollectible"
	description = "Summon five 2/2 Treants"
	
	def whenEffective(self, target=None, comment="", choice=0):
		print("The Forest's Aid is played and summons five 2/2 Treants.")
		self.Game.summonMinion([Treant(self.Game, self.ID) for i in range(5)], (-1, "totheRightEnd"), self.ID)
		return None
		
"""Hunter cards"""
class RapidFire_Twinspell(Spell):
	Class, name = "Hunter", "Rapid Fire"
	needTarget, mana = True, 1
	index = "Shadows-Hunter-1-Spell-Rapid Fire-Twinspell"
	description = "Twinspell. Deal 1 damage"
	
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			damage = (1 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			print("Rapid Fire is cast and deals %d damage to "%damage, target.name)
			self.dealsDamage(target, damage)
		return target
		
class RapidFire(Spell):
	Class, name = "Hunter", "Rapid Fire"
	needTarget, mana = True, 1
	index = "Shadows-Hunter-1-Spell-Rapid Fire-Uncollectible"
	description = "Deal 1 damage"
	
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			damage = (1 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			print("Rapid Fire is cast and deals %d damage to "%damage, target.name)
			self.dealsDamage(target, damage)
		return target
			
			
class Shimmerfly(Minion):
	Class, race, name = "Hunter", "Beast", "Shimmerfly"
	mana, attack, health = 1, 1, 1
	index = "Shadows-Hunter-1-1-1-Minion-Beast-Shimmerfly-Deathrattle"
	needTarget, keyWord, description = False, "", "Deathrattle: Add a random Hunter spell to your hand"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [AddaHunterSpelltoHand(self)]
		
class AddaHunterSpelltoHand(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		if self.entity.Game.Hand_Deck.handNotFull(self.entity.ID):
			hunterSpells = []
			for key, value in self.Game.ClassCards["Hunter"].items():
				if "-Spell-" in key:
					hunterSpells.append(value)
					
			print("Deathrattle: Summon a random Hunter spell to your hand triggers.")
			self.entity.Game.Hand_Deck.addCardtoHand(np.random.choice(hunterSpells), self.entity.ID, "CreateUsingType")
			
			
class NineLives(Spell):
	Class, name = "Hunter", "Nine Lives"
	needTarget, mana = False, 3
	index = "Shadows-Hunter-3-Spell-Nine Lives"
	description = "Discover a friendly Deathrattle minion that died this game. Also trigger its Deathrattle"
	
	def randomorDiscover(self):
		return "Discover"
		
	def whenEffective(self, target=None, comment="", choice=0):
		if self.Game.Hand_Deck.handNotFull(self.ID):
			deathrattleMinions, deathrattleIndices = [], []
			for index in self.Game.CounterHandler.minionsDiedThisGame[self.ID]:
				if "-Deathrattle" in index and "-Minion-" in index and index not in deathrattleIndices:
					deathrattleMinions.append(index)
					
			if deathrattleMinions != []:
				if comment == "CastbyOthers":
					print("Nine Lives is cast and adds a random friendly Deathrattle minion that died this game")
					minion = self.Game.cardPool[np.random.choice(deathrattleMinions)](self.Game, self.ID)
					self.Game.Hand_Deck.addCardtoHand(minion, self.ID)
					print("Nine Lives triggers the Deathrattle of the minion %s added to hand"%minion.name)
					for trigger in minion.deathrattles:
						trigger.trigger("DeathrattleTriggers", self.ID, None, minion, minion.attack, "")
				else:
					print("Nine Lives is cast and lets player discover adds a random friendly Deathrattle minion that died this game")
					minions = np.random.choice(deathrattleMinions, 3, replace=False)
					self.Game.options = [self.Game.cardPool[np.random.choice(minion)](self.Game, self.ID) for minion in minions]
					self.Game.DiscoverHandler.startDiscover(self)
					
		return None
		
	def discoverDecided(self, option):
		print("Deathrattle minion ", option.name, " is put into player's hand.")
		self.Game.Hand_Deck.addCardtoHand(option, self.ID)
		for trigger in option.deathrattles:
			trigger.trigger("DeathrattleTriggers", self.ID, None, option, option.attack, "")
			
			
class Ursatron(Minion):
	Class, race, name = "Hunter", "Mech", "Ursatron"
	mana, attack, health = 3, 3, 3
	index = "Shadows-Hunter-3-3-3-Minion-Mech-Ursatron-Deathrattle"
	needTarget, keyWord, description = False, "", "Deathrattle: Draw a Mech from your deck"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [DrawaMech(self)]
		
class DrawaMech(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("Deathrattle: Draw a Mech from your deck triggers")
		mechs = []
		for card in self.entity.Game.Hand_Deck.decks[self.entity.ID]:
			if card.cardType == "Minion" and "Mech" in card.race:
				mechs.append(card)
				
		if mechs != []:
			self.entity.Game.Hand_Deck.drawCard(self.entity.ID, np.random.choice(mechs))
			
			
class MarkedShot(Spell):
	Class, name = "Hunter", "Marked Shot"
	needTarget, mana = True, 4
	index = "Shadows-Hunter-4-Spell-Marked Shot"
	description = "Deal 4 damage to a minion. Discover a Spell"
	
	def randomorDiscover(self):
		return "Discover"
		
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			damage = (4 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			print("Marked Shot is cast and deals %d damage to"%damage, target.name)
			self.dealsDamage(target, damage)
			Class = self.Game.heroesp[self.ID].Class
			if Class == "Neutral":
				Class = self.Class
			spells = []
			for key, value in self.Game.ClassCards[Class].items():
				if "-Spell-" in key:
					spells.append(value)
					
			if comment == "CastbyOthers":
				print("Marked Shot is cast and adds a random spell to player's hand")
				self.Game.Hand_Deck.addCardtoHand(np.random.choice(spells), self.ID, "CreateUsingType")
			else:
				print("Marked Shot lets player discover a spell")
				spells = np.random.choice(spells, 3, replace=False)
				self.Game.options = [spell(self.Game, self.ID) for spell in spells]
				self.Game.DiscoverHandler.startDiscover(self)
				
		return target
		
	def discoverDecided(self, option):
		print("Spell ", target.name, " is put into player's hand.")
		self.Game.Hand_Deck.addCardtoHand(option, self.ID)
		
		
class HuntingParty(Spell):
	Class, name = "Hunter", "Hunting Party"
	needTarget, mana = False, 5
	index = "Shadows-Hunter-5-Spell-Hunting Party"
	description = "Copy all Beasts in your hand"
	
	def whenEffective(self, target=None, comment="", choice=0):
		print("Hunting Party is cast and copies all Beasts in player's hand.")
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
	index = "Shadows-Hunter-6-3-4-Minion-Mech-Oblivitron-Deathrattle-Legendary"
	needTarget, keyWord, description = False, "", "Deathrattle: Summon a Mech from your hand and trigger its Deathrattle"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [SummonMechfromHandandTriggeritsDeathrattle(self)]
		
class SummonMechfromHandandTriggeritsDeathrattle(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("Deathrattle: Summon a Mech from your hand and trigger its Deathrattle triggers")
		mechs = []
		for card in self.entity.Game.Hand_Deck.hands[self.entity.ID]:
			if "-Mech-" in card.index:
				mechs.append(card)
				
		if mechs != [] and self.entity.Game.spaceonBoard(self.entity.ID) > 0:
			mech = np.random.choice(mechs)
			self.entity.Game.summonfromHand(mech, self.entity.position+1, self.entity.ID)
			#Deathrattle triggered by others.
			for trigger in mech.deathrattles:
				trigger.trigger("DeathrattleTriggers", self.ID, None, mech, mech.attack, "")
				
class UnleashtheBeast_Twinspell(Spell):
	Class, name = "Hunter", "Unleash the Beast"
	needTarget, mana = False, 6
	index = "Shadows-Hunter-6-Spell-Unleash the Beast-Twinspell"
	description = "Twinspell. Summon a 5/5 Wyvern with Rush"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.twinSpell = 1
		
	def whenEffective(self, target=None, comment="", choice=0):
		print("Unleash the Beast is cast and summons a 5/5 Wyvern.")
		self.Game.summonMinion(Wyvern(self.Game, self.ID), -1, self.ID)
		return None
		
class UnleashtheBeast(Spell):
	Class, name = "Hunter", "Unleash the Beast"
	needTarget, mana = False, 6
	index = "Shadows-Hunter-6-Spell-Unleash the Beast-Uncollectible"
	description = "Summon a 5/5 Wyvern with Rush"
	
	def whenEffective(self, target=None, comment="", choice=0):
		print("Unleash the Beast is cast and summons a 5/5 Wyvern.")
		self.Game.summonMinion(Wyvern(self.Game, self.ID), -1, self.ID)
		return None
		
class Wyvern(Minion):
	Class, race, name = "Hunter", "Beast", "Wyvern"
	mana, attack, health = 5, 5, 5
	index = "Shadows-Hunter-5-5-5-Minion-Beast-Wyvern-Rush-Uncollectible"
	needTarget, keyWord, description = False, "Rush", "Rush"
	
	
class VereesaWindrunner(Minion):
	Class, race, name = "Hunter", "", "Vereesa Windrunner"
	mana, attack, health = 7, 5, 6
	index = "Shadows-Hunter-7-5-6-Minion-None-Vereesa Windrunner-Battlecry-Legendary"
	needTarget, keyWord, description = False, "", "Battlecry: Equip Thori'dal, the Stars' Fury"
	
	def whenEffective(self, target=None, comment="", choice=0):
		print("Vereesa Windrunner's battlecry equips Thori'dal, the Stars' Fury.")
		self.Game.equipWeapon(ThoridaltheStarsFury(self.Game, self.ID))
		return self, None
		
class ThoridaltheStarsFury(Weapon):
	Class, name, description = "Hunter", "Thori'dal, the Stars' Fury", "After your hero attacks, gain Spell Damage +2 this turn"
	mana, attack, durability = 3, 2, 3
	index = "Shadows-Hunter-3-2-3-Weapon-Thori'dal, the Stars' Fury-Legendary-Uncollectible"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_ThoridaltheStarsFury(self)]
		
class Trigger_ThoridaltheStarsFury(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["BattleFinished"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return subject == self.entity.Game.heroes[self.entity.ID] and self.entity.onBoard
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("After player attacks, Thori'dal, the Stars' Fury gives gives player Spell Damage +2 this turn.")
		self.entity.Game.playerStatus[self.entity.ID]["Spell Damage"] += 2
		trigger = Trigger_ThoridaltheStarsFury_TurnEnds(self.entity)
		trigger.ID = self.entity.ID
		trigger.connect()
		return self, None
		
class Trigger_ThoridaltheStarsFury_TurnEnds(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["TurnEnds"])
		self.ID = 1
		
	def connect(self):
		for signal in self.signals:
			self.entity.Game.triggersonBoard[self.ID].append((self, signal))
			
	def disconnect(self):
		for signal in self.signals:
			extractfrom((self, signal), self.entity.Game.triggersonBoard[self.ID])
			
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return True
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.Game.playerStatus[self.ID]["Spell Damage"] -= 2
		self.entity.Game.playerStatus[self.ID]["Spell Damage"] = max(0, self.entity.Game.playerStatus[self.ID]["Spell Damage"])
		self.disconnect()
		
"""Mage cards"""
class RayofFrost_Twinspell(Spell):
	Class, name = "Mage", "Ray of Frost"
	needTarget, mana = True, 1
	index = "Shadows-Mage-1-Spell-Ray of Frost-Twinspell"
	description = "Twinspell. Freeze a minion. If it's already Frozen, deal 2 damage to it"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.twinSpell = 1
		
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			if target.status["Frozen"]:
				damage = (2 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
				print("Ray of Frost is cast and deals %d damage to the already Frozen minion"%damage, target.name)
				self.dealsDamage(target, damage)
			else:
				print("Ray of Frost is cast and Freezes minion", target.name)
				target.getsFrozen()
		return target
		
class RayofFrost(Spell):
	Class, name = "Mage", "Ray of Frost"
	needTarget, mana = True, 1
	index = "Shadows-Mage-1-Spell-Ray of Frost-Uncollectible"
	description = "Freeze a minion. If it's already Frozen, deal 2 damage to it"
	
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			if target.status["Frozen"]:
				damage = (2 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
				print("Ray of Frost is cast and deals %d damage to the already Frozen minion"%damage, target.name)
				self.dealsDamage(target, damage)
			else:
				print("Ray of Frost is cast and Freezes minion", target.name)
				target.getsFrozen()
		return target
		
		
class Khadgar(Minion):
	Class, race, name = "Mage", "", "Khadgar"
	mana, attack, health = 2, 2, 2
	index = "Shadows-Mage-2-2-2-Minion-None-Khadgar-Legendary"
	needTarget, keyWord, description = False, "", "Your cards that summon minions summon twice as many"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.appearResponse = [self.activateAura]
		self.disappearResponse = [self.deactivateAura]
		self.silenceResponse = [self.deactivateAura]
		
	def activateAura(self):
		print("Khadgar's aura is registered. Player %d's cards' summoning effects now summon twice as many."%self.ID)
		self.Game.playerStatus[self.ID]["Double Summoning by Cards"] += 1
		
	def deactivateAura(self):
		print("Khadgar's aura is removed. Player %d's cards' summoning effects no longer summon twice as many."%self.ID)
		self.Game.playerStatus[self.ID]["Double Summoning by Cards"] -= 1
		self.Game.playerStatus[self.ID]["Double Summoning by Cards"] = max(0, self.Game.playerStatus[self.ID]["Double Summoning by Cards"])
		
		
class MagicDartFrog(Minion):
	Class, race, name = "Mage", "Beast", "Magic Dart Frog"
	mana, attack, health = 2, 1, 3
	index = "Shadows-Mage-2-1-3-Minion-Beast-Magic Dart Frog"
	needTarget, keyWord, description = False, "", "After you cast a spell, deal 1 damage to a random enemy minion"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_MagicDartFrog(self)]
		
class Trigger_MagicDartFrog(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["SpellBeenPlayed"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject.ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		targets = []
		for minion in self.entity.Game.minionsonBoard(3-self.entity.ID):
			if minion.health > 0 and minion.dead == False:
				targets.append(minion)
				
		if targets != []:
			target = np.random.choice(targets)
			print("After player casts a spell, %s deals 1 damage to a random enemy minion."%self.entity.name)
			self.entity.dealsDamage(target, 1)
			
			
class MessengerRaven(Minion):
	Class, race, name = "Mage", "Beast", "Messenger Raven"
	mana, attack, health = 3, 3, 2
	index = "Shadows-Mage-3-3-2-Minion-Beast-Messenger Raven-Battlecry"
	needTarget, keyWord, description = False, "", "Battlecry: Discover a Mage minion"
	
	def randomorDiscover(self):
		return "Discover"
		
	def whenEffective(self, target=None, comment="", choice=0):
		if self.Game.Hand_Deck.handNotFull(self.ID):
			mageMinions = []
			for key, value in self.Game.ClassCards["Mage"].values():
				if "-Minion-" in key:
					mageMinions.append(value)
					
			if comment == "InvokedbyOthers":
				print("Messenger Raven's battlecry adds random Mage minion to player's hand.")
				self.Game.Hand_Deck.addCardtoHand(np.random.choice(mageMinions), self.ID, "CreateUsingType")
			else:
				print("Messenger Raven's battlecry lets player discover a Mage minion.")
				minions = np.random.choice(mageMinions, 3, replace=False)
				self.Game.options = [minion(self.Game, self.ID) for minion in minions]
				self.Game.DiscoverHandler.startDiscover(self)
				
		return self, None
		
	def discoverDecided(self, option):
		print("Mage minion ", option.name, " is put into player's hand.")
		self.Game.Hand_Deck.addCardtoHand(option, self.ID)
		
		
class MagicTrick(Spell):
	Class, name = "Mage", "Magic Trick"
	needTarget, mana = False, 1
	index = "Shadows-Mage-1-Spell-Magic Trick"
	description = "Discover a spell that costs (3) or less"
	
	def whenEffective(self, target=None, comment="", choice=0):
		if self.Game.Hand_Deck.handNotFull(self.ID):
			Class = self.Game.heroes[self.ID].Class
			if Class == "Neutral":
				Class == self.Class
			spells = []
			for key, value in self.Game.ClassCards[Class].items():
				if "-Spell-" in key and str(key.split("-")[2]) < 4:
					spells.append(value)
					
			if comment == "CastbyOthers":
				print("Magic Trick adds a random spell that costs 3 or less to player's hand.")
				self.Game.Hand_Deck.addCardtoHand(np.random.choice(spells), self.ID, "CreateUsingType")
			else:
				print("Magic Trick lets player discover a spell that cost 3 or less.")
				spells = np.random.choice(spells, 3, replace=False)
				self.Game.options = [spell(self.Game, self.ID) for spell in spells]
				self.Game.DiscoverHandler.startDiscover(self)
				
		return None
		
	def discoverDecided(self, option):
		print("Spell ", option.name, " is put into player's hand.")
		self.Game.Hand_Deck.addCardtoHand(option, self.ID)
		
		
class ConjurersCalling_Twinspell(Spell):
	Class, name = "Mage", "Conjurer's Calling"
	needTarget, mana = True, 4
	index = "Shadows-Mage-4-Spell-Conjurer's Calling-Twinspell"
	description = "Twinspell. Destroy a minion. Summon 2 minions of the same Cost to replace it"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.twinSpell = 1
		
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.onBoard
	#咒术师的召唤会让随从先强制死亡，但是召唤出来的随从还是在原先死亡的随从的右侧，
	#所以需要改写gathertheDead（）的结算，可以让随从不会离场，仍然在列表中，到召唤之后将死亡的随从移除。
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			cost = target.mana
			print("Conjurer's Calling is cast, destroys minion %s and summons two minions with the same cost"%target.name, mana)
			minions = list(self.Game.MinionswithCertainCost[cost].values())
			target.dead = True
			#强制死亡需要在此插入死亡结算，并让随从离场
			self.Game.gathertheDead(decideWinner=False, deadMinionsLinger=True)
			minions = np.random.choice(minions, 2, replace=True)
			self.Game.summonMinion([minion(self.Game, target.ID) for minion in minions], (target.position, "totheRight"), self.ID)
			#之前死亡的随从仍在场上，它们可能已经因为死亡扳机而离开场上，此时将剩余的死亡过的随从移除出列表
			for minion in fixedList(self.Game.minions[1] + self.Game.minions[2]):
				if minion.onBoard == False:
					self.Game.removeMinionorWeapon(minion)
		return target
		
class ConjurersCalling(Spell):
	Class, name = "Mage", "Conjurer's Calling"
	needTarget, mana = True, 4
	index = "Shadows-Mage-4-Spell-Conjurer's Calling-Uncollectible"
	description = "Destroy a minion. Summon 2 minions of the same Cost to replace it"
	
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.onBoard
	#咒术师的召唤会让随从先强制死亡，但是召唤出来的随从还是在原先死亡的随从的右侧，
	#所以需要改写gathertheDead（）的结算，可以让随从不会离场，仍然在列表中，到召唤之后将死亡的随从移除。
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			cost = target.mana
			print("Conjurer's Calling is cast, destroys a minion and summons two minions with the same cost"%target.name, mana)
			minions = list(self.Game.MinionswithCertainCost[cost].values())
			target.dead = True
			#强制死亡需要在此插入死亡结算，并让随从离场
			self.Game.gathertheDead(decideWinner=False, deadMinionsLinger=True)
			minions = np.random.choice(minions, 2, replace=True)
			self.Game.summonMinion([minion(self.Game, target.ID) for minion in minions], (target.position, "totheRight"), self.ID)
			for minion in fixedList(self.Game.minions[1] + self.Game.minions[2]):
				if minion.onBoard == False:
					self.Game.removeMinionorWeapon(minion)
		return target
		
		
class KirinTorTricaster(Minion):
	Class, race, name = "Mage", "", "Kirin Tor Tricaster"
	mana, attack, health = 4, 3, 3
	index = "Shadows-Mage-4-3-3-Minion-None-Kirin Tor Tricaster"
	needTarget, keyWord, description = False, "", "Spell Damage +3. Your spells cost (1) more"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.keyWords["Spell Damage"] = 3
		self.manaAura = YourSpellsCost1More(self)
		self.appearResponse = [self.activateAura]
		self.disappearResponse = [self.deactivateAura]
		self.silenceResponse = [self.deactivateAura]
		
	def activateAura(self):
		print("Kirin Tor Tricaster's mana aura is included. Player's spells cost 1 more now.")
		self.Game.ManaHandler.CardAuras.apend(self.manaAura)
		self.Game.ManaHandler.calcMana_All()
		
	def deactivateAura(self):
		extractfrom(self.manaAura, self.Game.ManaHandler.CardAuras)
		print("Kirin Tor Tricaster's mana aura is removed. Player's spells no longer cost 1 more now.")
		self.Game.ManaHandler.calcMana_All()
		
class YourSpellsCost1More:
	def __init__(self, minion):
		self.minion = minion
		self.temporary = False
		
	def handleMana(self, target):
		if target.cardType == "Spell" and target.ID == self.minion.ID:
			target.mana += 1
			
			
class ManaCyclone(Minion):
	Class, race, name = "Mage", "Elemental", "Mana Cyclone"
	mana, attack, health = 2, 2, 2
	index = "Shadows-Mage-2-2-2-Minion-Elemental-Mana Cyclone-Battlecry"
	needTarget, keyWord, description = False, "", "Battlecry: For each spell you've cast this turn, add a random Mage spell to your hand"
	
	def whenEffective(self, target=None, comment="", choice=0):
		print("Mana Cyclone's battlecry adds a random Mage spell into player's hand for each spell played this turn.")
		mageSpells = []
		for key, value in self.Game.ClassCards["Mage"].items():
			if "-Spell-" in key:
				mageSpells.append(value)
				
		spells = np.random.choice(mageSpells, len(self.Game.numSpellsPlayedThisTurn[self.ID]), replace=True)
		self.Game.Hand_Deck.addCardtoHand(spells, self.ID, "CreateUsingType")
		return self, None
		
		
class PowerofCreation(Spell):
	Class, name = "Mage", "Power of Creation"
	needTarget, mana = False, 8
	index = "Shadows-Mage-8-Spell-Power of Creation"
	description = "Discover a 6-Cost minion. Summon two copies of it"
	
	def whenEffective(self, target=None, comment="", choice=0):
		print("Power of Creation is cast, player discovers a 6-cost minion and summon two copies of it.")
		Class = self.Game.heroes[self.ID].Class
		minions = []
		for key, value in self.Game.MinionswithCertainCost[6].items():
			if "-%s-"%Class in key or "-Neutral-" in key:
				minions.append(value)
				
		if comment == "CastbyOthers":
			print("Power of Creation summons two copies of a random 6-cost minion.")
			minion = np.random.choice(minions)
			self.Game.summonMinion([minion(self.Game, self.ID) for i in range(2)], (-1, "totheRightEnd"), self.ID)
		else:
			minions = np.random.choice(minions, 3, replace=False)
			self.Game.options = [minion(self.Game, self.ID) for minion in minions]
			print("Power of creation lets player discover a 6-cost minion to summon two copies.")
			self.Game.DiscoverHandler.startDiscover(self)
			
		return None
		
	def discoverDecided(self, option):
		print("Power of Creation summons two copies of discovered 6-cost minion ", target.name)
		self.Game.summonMinion([option, type(option)(self.Game, self.ID)], (-1, "totheRightEnd"), self.ID)
		
		
class Kalecgos(Minion):
	Class, race, name = "Mage", "Dragon", "Kalecgos"
	mana, attack, health = 10, 4, 12
	index = "Shadows-Mage-10-4-12-Minion-Dragon-Kalecgos-Legendary"
	needTarget, keyWord, description = False, "", "Your first spell costs (0) each turn. Battlecry: Discover a spell"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.manaAura = YourFirstSpellCosts0ThisTurn(self)
		self.triggersonBoard = [Trigger_Kalecgos(self)]
		self.appearResponse = [self.activateAura]
		self.disappearResponse = [self.deactivateAura]
		self.silenceResponse = [self.deactivateAura]
		
	def activateAura(self):
		print("Kalecgos appears and starts its mana aura. Player's first spell each turn costs 0.")
		if self.Game.turn == self.ID and self.Game.CounterHandler.numSpellsPlayedThisTurn[self.ID] == 0:
			self.Game.ManaHandler.CardAuras.apend(self.manaAura)
			self.Game.ManaHandler.calcMana_All()
			
	def deactivateAura(self):
		print("Kalecgos's mana aura is removed. Player's first spell each turn no longer costs 0.")
		extractfrom(self.manaAura, self.Game.ManaHandler.CardAuras)
		self.Game.ManaHandler.calcMana_All()
		
	def refreshAura(self, ID):
		if self.onBoard and self.health > 0 and ID == self.ID:
			print("At the start of turn, Kalecgos sets player's spells in hand to cost 0.")
			self.Game.ManaHandler.CardAuras.apend(self.manaAura)
			self.Game.ManaHandler.calcMana_All()
			
class Trigger_Kalecgos(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["TurnStarts", "ManaCostPaid"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		#不需要响应回合结束，因为费用光环自身被标记为temporary，会在回合结束时自行消失。
		if self.entity.onBoard:
			if signal == "TurnStarts" and ID == self.entity.ID:
				return True
			if signal == "ManaCostPaid" and subject.ID == self.entity.ID and subject.cardType == "Minion":
				return True
		return False
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		if signal == "TurnStarts":
			print("At the start of turn, %s restarts the mana aura and reduces the cost of the first minion by 1."%self.entity.name)
			self.entity.activateAura()
		else: #signal == "ManaCostPaid"
			self.entity.deactivateAura()
			
class YourFirstSpellCosts0ThisTurn:
	def __init__(self, minion):
		self.minion = minion
		self.temporary = True
		
	def handleMana(self, target):
		if target.cardType == "Spell" and target.ID == self.minion.ID:
			target.mana = 0
			
	def deactivate(self): #这个函数由Game.ManaHandler来调用，用于回合结束时的费用光环取消。
		extractfrom(self, self.minion.Game.ManaHandler.CardAuras)
		self.minion.Game.ManaHandler.calcMana_All()
		
		
class NeverSurrender(Secret):
	Class, name = "Paladin", "Never Surrender!"
	needTarget, mana = False, 1
	index = "Shadows-Paladin-1-Spell-Never Surrender!--Secret"
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
		print("When the opponent casts a spell, Secret Never Surrender! is triggered and gives friendly minions +2 Health.")
		for minion in self.entity.Game.minionsonBoard(self.entity.ID):
			minion.buffDebuff(0, 2)
			
			
class LightforgedBlessing_Twinspell(Spell):
	Class, name = "Paladin", "Lightforged Blessing"
	needTarget, mana = True, 2
	index = "Shadows-Paladin-2-Spell-Lightforged Blessing-Twinspell"
	description = "Twinspell. Give a friendly minion Lifesteal"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.twinSpell = 1
		
	def available(self):
		return self.selectableFriendlyMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.ID == self.ID and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			print("Lightforged Blessing is cast and gives a friendly minion Lifesteal.")
			target.getsKeyword("Lifesteal")
		return target
		
class LightforgedBlessing(Spell):
	Class, name = "Paladin", "Lightforged Blessing"
	needTarget, mana = True, 2
	index = "Shadows-Paladin-2-Spell-Lightforged Blessing-Uncollectible"
	description = "Give a friendly minion Lifesteal"
	
	def available(self):
		return self.selectableFriendlyMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.ID == self.ID and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			print("Lightforged Blessing is cast and gives a friendly minion Lifesteal.")
			target.getsKeyword("Lifesteal")
		return target
		
		
class BronzeHerald(Minion):
	Class, race, name = "Paladin", "Dragon", "Bronze Herald"
	mana, attack, health = 3, 3, 2
	index = "Shadows-Paladin-3-3-2-Minion-Dragon-Bronze Herald-Deathrattle"
	needTarget, keyWord, description = False, "", "Deathrattle: Add two 4/4 Dragons to your hand"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [AddTwoBronzeDragonstoHand(self)]
		
class AddTwoBronzeDragonstoHand(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("Deathrattle: Add Two 4/4 Bronze Dragons to hand triggers.")
		self.entity.Game.Hand_Deck.addCardtoHand([BronzeDragon, BronzeDragon], self.entity.ID, "CreateUsingType")
		
class BronzeDragon(Minion):
	Class, race, name = "Paladin", "Dragon", "Bronze Dragon"
	mana, attack, health = 4, 4, 4
	index = "Shadows-Paladin-4-4-4-Minion-Dragon-Bronze Dragon-Uncollectible"
	needTarget, keyWord, description = False, "", ""
	
	
class DesperateMeasures_Twinspell(Spell):
	Class, name = "Paladin", "Desperate Measures"
	needTarget, mana = False, 1
	index = "Shadows-Paladin-1-Spell-Desperate Measures-Twinspell"
	description = "Twinspell. Cast a random Paladin Secrets"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.twinSpell = 1
		
	def whenEffective(self, target=None, comment="", choice=0):
		print("Desperate Measures is cast and casts a random Paladin Secret.")
		secrets = []
		for key, value in self.Game.ClassCards["Paladin"].items():
			if "--Secret" in key and self.Game.SecretHandler.isSecretDeployedAlready(key, self.ID) == False:
				secrets.append(value)
				
		if secrets != []:
			np.random.choice(secrets)(self.Game, self.ID).cast()
		return None
		
class DesperateMeasures(Spell):
	Class, name = "Paladin", "Desperate Measures"
	needTarget, mana = False, 1
	index = "Shadows-Paladin-1-Spell-Desperate Measures-Uncollectible"
	description = "Cast a random Paladin Secrets"
	
	def whenEffective(self, target=None, comment="", choice=0):
		print("Desperate Measures is cast and casts a random Paladin Secret.")
		secrets = []
		for key, value in self.Game.ClassCards["Paladin"].items():
			if "--Secret" in key and self.Game.SecretHandler.isSecretDeployedAlready(key, self.ID) == False:
				secrets.append(value)
				
		if secrets != []:
			np.random.choice(secrets)(self.Game, self.ID).cast()
		return None
		
		
class MysteriousBlade(Weapon):
	Class, name, description = "Paladin", "Mysterious Blade", "Battlecry: If you control a Secret, gain +1 Attack"
	mana, attack, durability = 2, 2, 2
	index = "Shadows-Paladin-2-2-2-Weapon-Mysterious Blade-Battlecry"
	
	def whenEffective(self, target=None, comment="", choice=0):
		if self.Game.SecretHandler.secrets[self.ID] != []:
			print("Mysterious Blade's battlecry gives weapon +1 attack.")
			self.gainStat(1, 0)
		return self, None
		
		
class CalltoAdventure(Spell):
	Class, name = "Paladin", "Call to Adventure"
	needTarget, mana = False, 3
	index = "Shadows-Paladin-3-Spell-Call to Adventure"
	description = "Draw the lowest Cost minion from your deck. Give it +2/+2"
	def whenEffective(self, target=None, comment="", choice=0):
		print("Call to Adventure is cast. Player draws the lowest Cost card from deck, and it gains +2/+2.")
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
	index = "Shadows-Paladin-5-3-5-Minion-None-Dragon Speaker-Battlecry"
	needTarget, keyWord, description = False, "", "Battlecry: Give all Dragons in your hand +3/+3"
	
	def whenEffective(self, target=None, comment="", choice=0):
		print("Dragon Speaker's battlecry gives all Dragons in player's hand +3/+3.")
		for card in self.Game.Hand_Deck.hands[self.ID]:
			if card.cardType == "Minion" and "Dragon" in card.race:
				card.buffDebuff(3, 3)
		return self, None
		
#Friendly minion attacks. If the the minion has "Can't Attack", then it won't attack.
#Attackchances won't be consumed. If it survives, it can attack again. triggers["DealsDamage"] functions can trigger.
class Duel(Spell):
	Class, name = "Paladin", "Duel!"
	needTarget, mana = False, 5
	index = "Shadows-Paladin-5-Spell-Duel!"
	description = "Summon a minion from each player's deck. They fight"
	def whenEffective(self, target=None, comment="", choice=0):
		print("Duel! is cast and summons a minion from each player's deck. They fight.")
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
	index = "Shadows-Paladin-3-4-3-Minion-None-Commander Rhyssa-Legendary"
	needTarget, keyWord, description = False, "", "Your Secrets trigger twice"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.appearResponse = [self.activateAura]
		self.disappearResponse = [self.deactivateAura]
		self.silenceResponse = [self.deactivateAura]
		
	def activateAura(self):
		print("Commander Rhyssa's aura is registered. Player %d's Secrets now trigger twice."%self.ID)
		self.Game.playerStatus[self.ID]["Secret Trigger Twice"] += 1
		
	def deactivateAura(self):
		print("Commander Rhyssa's aura is removed. Player %d's Secrets no longer trigger twice."%self.ID)
		if self.Game.playerStatus[self.ID]["Secret Trigger Twice"] > 0:
			self.Game.playerStatus[self.ID]["Secret Trigger Twice"] -= 1
			
			
class Nozari(Minion):
	Class, race, name = "Paladin", "Dragon", "Nozari"
	mana, attack, health = 10, 4, 12
	index = "Shadows-Paladin-10-4-12-Minion-Dragon-Nozari-Battlecry-Legendary"
	needTarget, keyWord, description = False, "", "Battlecry: Restore both heroes to full Health"
	
	def whenEffective(self, target=None, comment="", choice=0):
		print("Nozari's battlecry restores all health to both players.")
		heal1 = self.Game.heroes[1].health_upper * (2 ** self.countHealDouble())
		heal2 = self.Game.heroes[2].health_upper * (2 ** self.countHealDouble())
		self.dealsAOE([], [], [self.Game.heroes[1], self.Game.heroes[2]], [heal1, heal2])
		return self, None
		
"""Priest cards"""
class EvilConscriper(Minion):
	Class, race, name = "Priest", "", "EVIL Conscripter"
	mana, attack, health = 2, 2, 2
	index = "Shadows-Priest-2-2-2-Minion-None-EVIL Conscripter-Deathrattle"
	needTarget, keyWord, description = False, "", "Deathrattle: Add a Lackey to your hand"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [AddaRandomLackeytoHand(self)]
		
class AddaRandomLackeytoHand(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("Deathrattle: Add A random Lackey to player's hand triggers.")
		self.entity.Game.Hand_Deck.addCardtoHand(np.random.choice(Lackeys), self.entity.ID, "CreateUsingType")
		
		
class HenchClanShadequill(Minion):
	Class, race, name = "Priest", "", "Hench-Clan Shadequill"
	mana, attack, health = 4, 4, 7
	index = "Shadows-Priest-4-4-7-Minion-None-Hench-Clan Shadequill-Deathrattle"
	needTarget, keyWord, description = False, "", "Deathrattle: Restore 5 Health to the enemy hero"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [Restore5HealthtoEnemyHero(self)]
		
class Restore5HealthtoEnemyHero(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		heal = 5 * (2 ** self.countHealDouble())
		print("Deathrattle: Restore %d health to enemy hero triggers to player's hand triggers."%heal)
		self.entity.restoresHealth(self.entity.Game.heroes[3-self.entity.ID], heal)
		
#If the target minion is killed due to Teacher/Juggler combo, summon a fresh new minion without enchantment.
class UnsleepingSoul(Spell):
	Class, name = "Priest", "Unsleeping Soul"
	needTarget, mana = True, 4
	index = "Shadows-Priest-4-Spell-Unsleeping Soul"
	description = "Silence a minion, then summon a copy of it"
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			print("Unsleeping Soul is cast, Silences friendly minion %s and summons a copy of it."%target.name)
			target.getsSilenced()
			#If the minion is controlled by the other side, then summon it at -1.
			self.Game.summonMinion(target.selfCopy(self.ID), target.position+1, self.ID)
		return target
		
		
class ForbiddenWords(Spell):
	Class, name = "Priest", "Forbidden Words"
	needTarget, mana = True, 0
	index = "Shadows-Priest-0-Spell-Forbidden Words"
	description = "Spell all your Mana. Destroy a minion with that much Attack or less"
	
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.attack <= self.Game.ManaHandler.manas[self.ID] and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0):
		#假设如果没有指定目标则不会消耗法力值
		if target != None:
			print("Forbidden Words is cast, spends all of player's mana and destroys minion ", target.name)
			self.Game.CounterHandler.manaSpentonSpells[self.ID] += self.Game.ManaHandler.manas[self.ID]
			self.Game.ManaHandler.manas[self.ID] = 0
			target.dead = True
		return target
		
		
class ConvincingInfiltrator(Minion):
	Class, race, name = "Priest", "", "Convincing Infiltrator"
	mana, attack, health = 5, 2, 6
	index = "Shadows-Priest-5-2-6-Minion-None-Convincing Infiltrator-Taunt-Deathrattle"
	needTarget, keyWord, description = False, "Taunt", "Taunt. Deathrattle: Destroy a random enemy minion"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [DestroyaRandomEnemyMinion(self)]
		
class DestroyaRandomEnemyMinion(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("Deathrattle: Destroy a random enemy minion triggers.")
		minions = []
		for minion in self.entity.Game.minionsonBoard(3-self.minion.ID):
			if minion.dead == False:
				minions.append(minion)
				
		if minions != []:
			np.random.choice(minions).dead = True
			
			
class MassResurrection(Spell):
	Class, name = "Priest", "Mass Resurrection"
	needTarget, mana = False, 9
	index = "Shadows-Priest-9-Spell-Mass Resurrection"
	
	def available(self):
		return self.Game.spaceonBoard(self.ID) > 0
		
	def whenEffective(self, target=None, comment="", choice=0):
		print("Mass Resurrection is cast and summons 3 friendly minions that died this turn.")
		numMinionsDied = len(self.Game.CounterHandler.minionsDiedThisGame[self.ID])
		numSummon = min(3, self.Game.spaceonBoard(self.ID), numMinionsDied)
		if numSummon > 0:
			indices = np.random.choice(self.Game.CounterHandler.minionsDiedThisGame[self.ID], numSummon, replace=False)
			self.Game.summonMinion([self.Game.cardPool[index](self.Game, self.ID) for index in indices], (-1, "totheRightEnd"), self.ID)
		return None
		
#Upgrades at the end of turn.
class LazulsScheme(Spell):
	Class, name = "Priest", "Lazul's Scheme"
	needTarget, mana = True, 0
	index = "Shadows-Priest-0-Spell-Lazul's Scheme"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.progress = 1
		self.triggersinHand = [Trigger_Upgrade(self)]
		
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			print("Lazul's Scheme is cast and reduces minion %s's attack by %d until player's next turn."%(target.name, self.progress))
			timePoint = "StartofTurn 1" if self.ID == 1 else "StartofTurn 2"
			target.buffDebuff(-self.progress, 0, timePoint)
		return target
		
class Trigger_Upgrade(TriggerinHand):
	def __init__(self, entity):
		self.blank_init(entity, ["TurnEnds"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.inHand and ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("At the end of turn, %s upgrades"%self.entity.name)
		self.entity.progress += 1
		
		
class ShadowFigure(Minion):
	Class, race, name = "Priest", "", "Shadow Figure"
	mana, attack, health = 2, 2, 2
	index = "Shadows-Priest-2-2-2-Minion-None-Shadow Figure-Battlecry"
	needTarget, keyWord, description = True, "", "Battlecry: Transform into a 2/2 copy of a friendly Deathrattle minion"
	
	def effectCanTrigger(self):
		return self.selectableFriendlyMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target != self and target.ID == self.ID and target.deathrattles != [] and target.onBoard
		
	def played(self, target=None, choice=0, mana=0, comment=""):
		self.statReset(self.attack_Enchant, self.health_Enchant)
		self.appears()
		self.Game.sendSignal("MinionPlayed", self.ID, self, target, mana, "", choice)
		self.Game.sendSignal("MinionSummoned", self.ID, self, target, mana, "")
		self.Game.gathertheDead() #At this point, the minion might be removed/controlled by Illidan/Juggler combo.		
		#变形成果复制的随从不会计算双倍战吼。
		self.Game.target = target
		self.Game.sendSignal("MinionBattlecryTargetSelected", self.ID, self, target, 0, "", choice)
		target = self.Game.target
		minion, target = self.whenEffective(target, choice)
		self.Game.gathertheDead()
		if minion != None and minion.onBoard:
			self.Game.sendSignal("MinionBeenSummoned", self.ID, minion, target, mana, "")
			
		return minion
		
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None and self.dead == False: #战吼触发时自己不能死亡。
			if self.onBoard:
				if target.onBoard:
					Copy = target.selfCopy(self.ID, 2, 2)
					print("Shadow Figure's battlecry transforms minion into a copy of ", target.name)
					print("The new copy has Aura's and trigger:")
					Copy.statusPrint()
					self.Game.transform(self, Copy)
					return Copy, target
				else: #target not on board. This Faceless Manipulator becomes a base copy of it.
					Copy = type(target)(self.Game, self.ID)
					Copy.statReset(2, 2)
					print("Shadow Figure's battlecry transforms minion into a base copy of ", target.name)
					self.Game.transform(self, Copy)
					return Copy, target
			elif self.inHand:
				Copy = type(target)(self.Game, self.ID)
				#假设在手牌中时不会涉及身材的修改。
				print("Shadow Figure's battlecry triggers in hand and transforms minion into a 2/2 copy of ", target.name)
				self.Game.Hand_Deck.replaceCardinHand(self, Copy)
				return Copy, target
		return self, target
		
		
class MadameLazul(Minion):
	Class, race, name = "Priest", "", "Madame Lazul"
	mana, attack, health = 3, 3, 2
	index = "Shadows-Priest-3-3-2-Minion-None-Madame Lazul-Battlecry-Legendary"
	needTarget, keyWord, description = False, "", "Battlecry: Discover a copy of a card in your opponent's hand"
	#不知道如果手牌中有多个同类型的随从，但是接受了不同的buff等效果，是否会发现不同的类型
	#def randomorDiscover(self):
	#	if self.Game.Hand_Deck.hands[3-self.ID] < 2:
	#		return "No RNG"
	#	else:
	#		return "Discover"
	#		
	#def whenEffective(self, target=None, comment="", choice=0):
	#	if self.Game.Hand_Deck.hands[3-self.ID] != [] and self.Game.Hand_Deck.handNotFull(self.ID):
	#		if len(self.Game.Hand_Deck.hands[3-self.ID]) == 1:
	#			print("Opponent only has one card in hand, Madame Lazul's battlecry copies it")
	#			Copy = self.Game.Hand_Deck.hands[3-self.ID][0].selfCopy(self.ID)
	#			self.Game.Hand_Deck.addCardtoHand(Copy, self.ID)
	#		else:
	#			if comment == "InvokedbyOthers":
	#				print("Madame Lazul's battlecry adds a copy of a random card in opponent's hand to player's hand.")
	#				Copy = np.random.choice(self.Game.Hand_Deck.hands[3-self.ID]).selfCopy(self.ID)
	#				self.Game.Hand_Deck.addCardtoHand(Copy, self.ID)
	#			else:
	#				print("Madame Lazul's battlecry lets player discover a copy of card in opponent's hand.")
	#				num = 
	#	return self, None
	
class CatrinaMuerte(Minion):
	Class, race, name = "Priest", "", "Catrina Muerte"
	mana, attack, health = 8, 6, 8
	index = "Shadows-Priest-8-6-8-Minion-None-Catrina Muerte-Legendary"
	needTarget, keyWord, description = False, "", "At the end of your turn, summon a friendly minion that died this game"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_CatrinaMuerte(self)]
		
class Trigger_CatrinaMuerte(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["TurnEnds"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("At the end of turn, %s summons a friendly minion that died this game."%self.entity.name)
		if self.entity.Game.CounterHandler.minionsDiedThisGame[self.entity.ID] != []:
			minion = np.random.choice(self.entity.Game.CounterHandler.minionsDiedThisGame[self.entity.ID])
			self.entity.Game.summonMinion(minion(self.entity.Game, self.entity.ID), self.entity.position+1, self.entity.ID)
			
"""Rogue cards"""
class DaringEscape(Spell):
	Class, name = "Rogue", "Daring Escape"
	needTarget, mana = False, 1
	index = "Shadows-Rogue-1-Spell-Daring Escape"
	description = "Return all friendly minions to your hand"
	def whenEffective(self, target=None, comment="", choice=0):
		print("Daring Escape is cast and returns all friendly minions to player's hand.")
		for minion in self.Game.minionsonBoard(self.ID):
			self.Game.returnMiniontoHand(minion)
		return None
		
		
class EVILMiscreant(Minion):
	Class, race, name = "Rogue", "", "EVIL Miscreant"
	mana, attack, health = 3, 1, 4
	index = "Shadows-Rogue-3-1-4-Minion-None-EVIL Miscreant-Combo"
	needTarget, keyWord, description = False, "", "Combo: Add two 1/1 Lackeys to your hand"
	
	def effectCanTrigger(self):
		return self.Game.CounterHandler.cardsPlayedThisTurn[self.ID] != []
		
	#Will only be invoked if self.effectCanTrigger() returns True in self.played()
	def whenEffective(self, target=None, comment="", choice=0):
		if self.Game.CounterHandler.cardsPlayedThisTurn[self.ID] != []:
			print("EVIL Miscreant's Combo triggers and adds two Lackeys to player's hand.")
			self.Game.Hand_Deck.addCardtoHand(np.random.choice(Lackeys, 2, replace=False), self.ID, "CreateUsingType")
		return self, None
		
		
class HenchClanBurglar(Minion):
	Class, race, name = "Rogue", "", "Hench-Clan Burglar"
	mana, attack, health = 4, 4, 3
	index = "Shadows-Rogue-4-4-3-Minion-None-Hench-Clan Burglar-Battlecry"
	needTarget, keyWord, description = False, "", "Battlecry: Discover a spell from another class"
	
	def whenEffective(self, target=None, comment="", choice=0):
		if self.ID == self.Game.turn:
			Class = self.Game.heroes[self.ID].Class
			if Class == "Neutral":
				Class = "Rogue"
				
			spells = list(self.Game.ClassCards[Class].values())
			if comment == "InvokedbyOthers":
				print("Hench-Clan Burglar's battlecry adds a random spell from another class to player's hand")
				self.Game.Hand_Deck.addCardtoHand(np.random.choice(spells), self.ID, "CreateUsingType")
			else:
				print("Hench-Clan Burglar's battlecry lets player Discover a spell from another class")
				spells = np.random.choice(spells, 3, replace=False)
				self.Game.options = [spell(self.Game, self.ID) for spell in spells]
				self.Game.DiscoverHandler.startDiscover(self)
		return self, None
		
	def discoverDecided(self, option):
		print("Spell", option.name, "is added to player's hand")
		self.Game.Hand_Deck.addCardtoHand(option, self.ID)
		
		
class TogwagglesScheme(Spell):
	Class, name = "Rogue", "Togwaggle's Scheme"
	needTarget, mana = True, 1
	index = "Shadows-Rogue-1-Spell-Togwaggle's Scheme"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.progress = 1
		self.triggersinHand = [Trigger_Upgrade(self)]
		
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.ID == self.ID and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			print("Togwaggle's Scheme is cast and shuffles %d copies of a friendly minion to player's hand.")
			for i in range(self.progress):
				Copy = type(target)(self.Game, self.ID)
				self.Game.Hand_Deck.shuffleCardintoDeck(Copy, initiatorID=self.ID)
		return target
		
		
class UnderbellyFence(Minion):
	Class, race, name = "Rogue", "", "Underbelly Fence"
	mana, attack, health = 2, 2, 3
	index = "Shadows-Rogue-2-2-3-Minion-None-Underbelly Fence-Battlecry"
	needTarget, keyWord, description = False, "", "Battlecry: If you're holding a card from another class, gain +1/+1 and Rush"
	
	def effectCanTrigger(self):
		if self.inHand:
			return self.Game.Hand_Deck.holdingCardfromAnotherClass(self.ID, self)
		else:
			return self.Game.Hand_Deck.holdingCardfromAnotherClass(self.ID)
			
	#Will only be invoked if self.effectCanTrigger() returns True in self.played()
	def whenEffective(self, target=None, comment="", choice=0):
		if self.inHand and self.Game.Hand_Deck.holdingCardfromAnotherClass(self.ID, self):
			print("Underbelly Fence's battlecry gives minion +1/+1 and Rush.")
			self.buffDebuff(1, 1)
			self.getsKeyword("Rush")
		elif self.onBoard and self.Game.Hand_Deck.holdingCardfromAnotherClass(self.ID):
			print("Underbelly Fence's battlecry gives minion +1/+1 and Rush.")
			self.buffDebuff(1, 1)
			self.getsKeyword("Rush")
		return self, None
		
		
class Vendetta(Spell):
	Class, name = "Rogue", "Vendetta"
	needTarget, mana = True, 4
	index = "Shadows-Rogue-4-Spell-Vendetta"
	description = "Deal 4 damage to a minion. Costs (0) if you're holding a card from another class"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersinHand = [Trigger_Vendetta(self)]
		
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.onBoard
		
	def selfManaChange(self):
		if self.Game.Hand_Deck.holdingCardfromAnotherClass(self.ID):
			self.mana = 0
			
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			damage = (4 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			print("Vendetta is cast and deals %d damage to minion "%damage, target.name)
			self.dealsDamage(target, damage)
		return target
		
class Trigger_Vendetta(TriggerinHand):
	def __init__(self, entity):
		self.blank_init(entity, ["CardLeavesHand", "CardEntersHand"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		#Only cards with a different class than your hero class will trigger this
		return self.entity.inHand and target.ID == self.entity.ID and target.Class != self.entity.Game.heroes[self.entity.ID].Class
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.Game.ManaHandler.calcMana_Single(self.entity)
		
		
class WagglePick(Weapon):
	Class, name, description = "Rogue", "Waggle Pick", "Deathrattle: Return a random friendly minion to your hand"
	mana, attack, durability = 4, 4, 2
	index = "Shadows-Rogue-4-4-2-Weapon-Waggle Pick-Deathrattle"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [ReturnaFriendlyMiniontoHand(self)]
		
#There are minions who also have this deathrattle.
class ReturnaFriendlyMiniontoHand(Deathrattle_Weapon):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		if self.entity.Game.minionsonBoard(self.entity.ID) != []:
			print("Deathrattle: Return a random friendly minion to your hand triggers")
			miniontoReturn = np.random.choice(self.entity.Game.minionsonBoard(self.entity.ID))
			miniontoReturn = self.entity.Game.returnMiniontoHand(miniontoReturn)
			if miniontoReturn != None:
				miniontoReturn.mana_set -= 2
				miniontoReturn.mana_set = max(0, miniontoReturn.mana_set)
				self.entity.Game.ManaHandler.calcMana_Single(self.entity)
				
				
class UnidentifiedContract(Spell):
	Class, name = "Rogue", "Unidentified Contract"
	needTarget, mana = True, 6
	index = "Shadows-Rogue-6-Spell-Unidentified Contract"
	description = "Destroy a minion. Gain a bonus effect in your hand"
	def entersHand(self):
		#本牌进入手牌的结果是本卡消失，变成其他的牌
		self.onBoard, self.inHand, self.inDeck = False, False, False
		self.mana = self.mana_set
		#This card doesn't have have triggerinHand. It immediately transforms when enters hand
		card = np.random.choice([AssassinsContract, LucrativeContract, RecruitmentContract, TurncoatContract])(self.Game, self.ID)
		return card
		
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.ID == self.ID and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			print("Unidentified Contract is cast and destroys minion", target.name)
			target.dead = True
		return target
		
class AssassinsContract(Spell):
	Class, name = "Rogue", "Assassin's Contract"
	needTarget, mana = True, 6
	index = "Shadows-Rogue-6-Spell-Assassin's Contract-Uncollectible"
	description = "Destroy a minion. Summon a 1/1 Patient Assassin"
	
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.ID == self.ID and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			print("Assassin's Contract is cast and destroys minion", target.name)
			target.dead = True
		print("Assassin's Contract also summons a 1/1 Patient Assassin")
		self.Game.summonMinion(PatientAssassin(self.Game, self.ID), -1, self.ID)
		return target
		
class LucrativeContract(Spell):
	Class, name = "Rogue", "Lucrative Contract"
	needTarget, mana = True, 6
	index = "Shadows-Rogue-6-Spell-Lucrative Contract-Uncollectible"
	description = "Destroy a minion. Add two Coins to your hand"
	
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.ID == self.ID and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			print("Lucrative Contract is cast and destroys minion", target.name)
			target.dead = True
		print("Lucrative Contract also adds two Coins to player's hand")
		self.Game.Hand_Deck.addCardtoHand([TheCoin, TheCoin], self.ID, "CreateUsingType")
		return target
		
class RecruitmentContract(Spell):
	Class, name = "Rogue", "Recruitment Contract"
	needTarget, mana = True, 6
	index = "Shadows-Rogue-6-Spell-Recruitment Contract-Uncollectible"
	description = "Destroy a minion. Add two Coins to your hand"
	
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.ID == self.ID and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			print("Recruitment Contract is cast and destroys minion", target.name)
			target.dead = True
		print("Recruitment Contract also adds a copy of the minion to player's hand")
		self.Game.Hand_Deck.addCardtoHand(type(target), self.ID, "CreateUsingType")
		return target
		
class TurncoatContract(Spell):
	Class, name = "Rogue", "Turncoat Contract"
	needTarget, mana = True, 6
	index = "Shadows-Rogue-6-Spell-Turncoat Contract-Uncollectible"
	description = "Destroy a minion. Add two Coins to your hand"
	
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.ID == self.ID and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			print("Turncoat Contract is cast and destroys minion", target.name)
			target.dead = True
		if target.onBoard:
			print("Turncoat Contract also lets the minion deal its damage to adjacent minions")
			adjacentMinions, distribution = self.Game.findAdjacentMinions(target)
			if adjacentMinions != []:
				target.dealsAOE(adjacentMinions, [target.attack for minion in adjacentMinions])
		return target
		
		
class HeistbaronTogwaggle(Minion):
	Class, race, name = "Rogue", "", "Heistbaron Togwaggle"
	mana, attack, health = 6, 5, 5
	index = "Shadows-Rogue-6-5-5-Minion-None-Heistbaron Togwaggle-Battlecry"
	needTarget, keyWord, description = False, "", "Battlecry: If you control a Lackey, choose a fantastic treasure"
	
	def effectCanTrigger(self):
		for minion in self.Game.minionsonBoard(self.ID):
			if type(minion) in Lackeys:
				return True
		return False
		
	#Will only be invoked if self.effectCanTrigger() returns True in self.played()
	#def whenEffective(self, target=None, comment="", choice=0):
	#	controlsLackey = False
	#	for minion in self.Game.minionsonBoard(self.ID):
	#		if type(minion) in Lackeys:
	#			controlsLackey = True
	#			break
	#			
	#	if controlsLackey and self.ID == self.turn and 
	#		print("Heistbaron Togwaggle's battlecry lets player choose a fantastic treasure.")
	#		
	#	return self, None
	
	def discoverDecided(self, option):
		print("Treasure", option.name, "is added to player's hand")
		self.Game.Hand_Deck.addCardtoHand(option, self.ID)
		
		
class TakNozwhisker(Minion):
	Class, race, name = "Rogue", "", "Tak Nozwhisker"
	mana, attack, health = 7, 6, 6
	index = "Shadows-Rogue-7-6-6-Minion-None-Tak Nozwhisker"
	needTarget, keyWord, description = False, "", "Whenever you shuffle a card into your deck, add a copy to your hand"
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
		print("Player shuffles cards into deck and %s adds a copy to player's hand for each"%self.entity.name)
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
	needTarget, mana = True, 0
	index = "Shadows-Shaman-0-Spell-Mutate"
	description = "Transf a friendly minion to a random one that costs (1) more"
	def available(self):
		return self.selectableFriendlyMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.ID == self.ID and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			print("Mutate is cast and transforms friendly minion %s to one that costs 1 more."%target.name)
			target = self.Game.mutate(target, 1)
		return target
		
		
class SludgeSlurper(Minion):
	Class, race, name = "Shaman", "Murloc", "Sludge Slurper"
	mana, attack, health = 1, 1, 1
	index = "Shadows-Shaman-1-1-1-Minion-Murloc-Sludge Slurper-Battlecry-Overload"
	needTarget, keyWord, description = False, "", "Battlecry: Add a Lackey to your hand. Overload: (1)"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.overload = 1
		
	def whenEffective(self, target=None, comment="", choice=0):
		print("Sludge Slurper battlecry adds a Lackey to player's hand.")
		self.Game.Hand_Deck.addCardtoHand(np.random.choice(Lackeys), self.ID, "CreateUsingType")
		return self, None
		
		
class SouloftheMurloc(Spell):
	Class, name = "Shaman", "Soul of the Murloc"
	needTarget, mana = False, 2
	index = "Shadows-Shaman-2-Spell-Soul of the Murloc"
	description = "Give your minions 'Deathrattle: Summon a 1/1 Murloc'"
	def available(self):
		return self.Game.minionsonBoard(self.ID) != []
		
	def whenEffective(self, target=None, comment="", choice=0):
		print("Soul of the Murloc is cast and gives all friendly minions Deathrattle: Summon a 1/1 Murloc.")
		for minion in self.Game.minionsonBoard[self.ID]:
			trigger = SummonaMurlocScout(minion)
			minion.deathrattles.append(trigger)
			trigger.connect()
		return None
		
class SummonaMurlocScout(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("Deathrattle: Summon a 1/1 Murloc triggers")
		self.entity.Game.summonMinion(MurlocScout(self.entity.Game, self.entity.ID), self.entity.position+1, self.entity.ID)
		
		
class UnderbellyAngler(Minion):
	Class, race, name = "Shaman", "Murloc", "Underbelly Angler"
	mana, attack, health = 2, 2, 3
	index = "Shadows-Shaman-2-2-3-Minion-Murloc-Underbelly Angler"
	needTarget, keyWord, description = False, "", "After you play a Murloc, add a random Murloc to your hand"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_UnderbellyAngler(self)]
		
class Trigger_UnderbellyAngler(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionBeenSummoned"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject.ID == self.entity.ID and subject != self.entity
	#Assume if Murloc gets controlled by the enemy, this won't trigger
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("After player plays Murloc %s, %s adds a random Murloc to player's hand."%(subject.name, self.entity.name))
		murloc = np.random.choice(list(self.entity.Game.MinionswithRace["Murloc"].values()))
		self.entity.Game.Hand_Deck.addCardtoHand(murloc(self.entity.Game, self.entity.ID), self.entity.ID)
		
		
class HagathasScheme(Spell):
	Class, name = "Shaman", "Hagatha's Scheme"
	needTarget, mana = False, 5
	index = "Shadows-Shaman-5-Spell-Hagatha's Scheme"
	description = "Deal 1 damage to all minions. (Upgrades each turn)!"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.progress = 1
		self.triggersinHand = [Trigger_Upgrade(self)]
		
	def whenEffective(self, target=None, comment="", choice=0):
		damage = (self.progress + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		print("Hagatha's Scheme is cast and deals %d damage to all minions."%damage)
		targets = self.Game.minionsonBoard(1) + self.Game.minionsonBoard(2)
		self.dealsDamage(targets, [damage for minion in targets])
		return None
		
		
class WalkingFountain(Minion):
	Class, race, name = "Shaman", "Elemental", "Walking Fountain"
	mana, attack, health = 8, 4, 8
	index = "Shadows-Shaman-8-4-8-Minion-Elemental-Walking Fountain-Rush-Lifesteal-Windfury"
	needTarget, keyWord, description = False, "Rush,Windfury,Lifesteal", "Rush, Windfury, Lifesteal"
	
	
class WitchsBrew(Spell):
	Class, name = "Shaman", "Witch's Brew"
	needTarget, mana = True, 2
	index = "Shadows-Shaman-2-Spell-Witch's Brew"
	description = "Restore 4 Health. Repeatable this turn"
	
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			heal = 4 * (2 ** self.countHealDouble())
			print("Witch's Brew is cast and restores %d health to "%damage, target.name)
			self.restoresHealth(target, heal)
			
		print("Witch's Brew adds another Witch's Brew to player's hand, which disappears at the end of turn.")
		echo = WitchsBrew(self.Game, self.ID)
		trigger = Trigger_Echo(echo)
		echo.triggersinHand.append(trigger)
		trigger.connect()
		return target
		
		
class Muckmorpher(Minion):
	Class, race, name = "Shaman", "", "Muckmorpher"
	mana, attack, health = 5, 4, 4
	index = "Shadows-Shaman-5-4-4-Minion-None-Muckmorpher-Battlecry"
	needTarget, keyWord, description = False, "", "Battlecry: Transform in to a 4/4 copy of a different minion in your deck"
	
	def played(self, target=None, choice=0, mana=0, comment=""):
		self.statReset(self.attack_Enchant, self.health_Enchant)
		self.appears()
		self.Game.sendSignal("MinionPlayed", self.ID, self, target, mana, "", choice)
		self.Game.sendSignal("MinionSummoned", self.ID, self, target, mana, "")
		self.Game.gathertheDead() #At this point, the minion might be removed/controlled by Illidan/Juggler combo.		
		#变形成果复制的随从不会计算双倍战吼。
		minion, target = self.whenEffective(target, choice)
		self.Game.gathertheDead()
		if minion != None and minion.onBoard:
			self.Game.sendSignal("MinionBeenSummoned", self.ID, minion, target, mana, "")
			
		return minion
		
	def whenEffective(self, target=None, comment="", choice=0):
		if self.dead == False: #The minion has to be alive to transform
			print("Muckmorpher's battlecry transforms the minion into a 4/4 copy of a minion in player's deck.")
			minionsinDeck = []
			for card in self.Game.Hand_Deck.decks[self.ID]:
				if card.cardType == "Minion":
					minionsinDeck.append(card)
					
			if minionsinDeck != []:
				if self.onBoard:
					Copy = np.random.choice(minionsinDeck).selfCopy(self.ID, 4, 4)
					self.Game.transform(self, Copy)
					return Copy, None
				elif self.inHand:
					Copy = type(np.random.choice(minionsinDeck))(self.Game, self.ID)
					Copy.statReset(4, 4)
					self.Game.replaceCardinHand(self, Copy)
					return Copy, None
					
		return self, None
		
		
class Scargil(Minion):
	Class, race, name = "Shaman", "Murloc", "Scargil"
	mana, attack, health = 4, 4, 4
	index = "Shadows-Shaman-4-4-4-Minion-Murloc-Scargil-Legendary"
	needTarget, keyWord, description = False, "", "Your Murlocs cost (1)"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.manaAura = YourMurlocsCost1(self)
		self.appearResponse = [self.activateAura]
		self.disappearResponse = [self.deactivateAura]
		self.silenceResponse = [self.deactivateAura]
		
	def activateAura(self):
		print("Scargil's mana aura is included. Player's Murlocs cost 1 now.")
		self.Game.ManaHandler.CardAuras.apend(self.manaAura)
		self.Game.ManaHandler.calcMana_All()
		
	def deactivateAura(self):
		extractfrom(self.manaAura, self.Game.ManaHandler.CardAuras)
		print("Scargil's mana aura is removed. Player's Murlocs no longer cost 1 now.")
		self.Game.ManaHandler.calcMana_All()
		
class YourMurlocsCost1:
	def __init__(self, minion):
		self.minion = minion
		self.temporary = False
		
	def handleMana(self, target):
		if target.cardType == "Minion" and "Murloc" in target.race and target.ID == self.minion.ID:
			target.mana = 1
			
			
class SwampqueenHagatha(Minion):
	Class, race, name = "Shaman", "", "Swampqueen Hagatha"
	mana, attack, health = 7, 5, 5
	index = "Shadows-Shaman-7-5-5-Minion-None-Swampqueen Hagatha-Battlecry-Legendary"
	needTarget, keyWord, description = False, "", "Battlecry: Add a 5/5 Horror to your hand. Teach it two Shaman spells"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.firstSpellneedsTarget = False
		self.spell1, self.spell2 = None, None
		
	def whenEffective(self, target=None, comment="", choice=0):
		self.firstSpellneedsTarget, self.spell1, self.spell2 = False, None, None
		if self.Game.Hand_Deck.handNotFull(self.ID):
			print("Swampqueen Hagatha's battlecry lets player create a 5/5 Horror and teach it two Shaman Spells.")
			shamanSpells = []
			nonTargetingShamanSpells = []
			for key, value in self.Game.ClassCards["Shaman"].items():
				if "-Spell-" in key:
					shamanSpells.append(value)
					if value.needTarget == False:
						nonTargetingShamanSpells.append(value)
						
			if comment == "InvokedbyOthers":
				spell1 = np.random.choice(shamanSpells)
				extractfrom(spell1, shamanSpells)
				spell2 = np.random.choice(nonTargetingShamanSpells) if spell1.needTarget else np.random.choice(shamanSpells)
			else:
				spells = np.random.choice(shamanSpells, 3, replace=False)
				self.Game.options = [spell(self.Game, self.ID) for spell in spells]
				self.Game.DiscoverHandler.startDiscover(self)
				extractfrom(self.spell1, shamanSpells)
				if self.firstSpellneedsTarget:
					spells = np.random.choice(nonTargetingShamanSpells, 3, replace=False)
				else:
					spells = np.random.choice(shamanSpells, 3, replace=False)
				self.Game.options = [spell(self.Game, self.ID) for spell in spells]
				self.Game.DiscoverHandler.startDiscover(self)
				spell1, spell2 = self.spell1, self.spell2
				
			spell1ClassName = str(type(spell1)).split(".")[1].split("'")[0]
			spell2ClassName = str(type(spell2)).split(".")[1].split("'")[0]
			needTarget = spell1.needTarget or spell2.needTarget
			newIndex = "Shadows-Shaman-5-5-5-Minion-None-Drustvar Horror_%s_%s-Battlecry-Uncollectible"%(spell1.name, spell2.name)
			subclass = type("DrustvarHorror_"+spell1ClassName+spell2ClassName, (DrustvarHorror, ), 
							{"needTarget": needTarget, "learnedSpell1": spell1, "learnedSpell2":spell2,
							"index": newIndex
							}
							)
			self.Game.cardPool[newIndex] = subclass
			self.Game.Hand_Deck.addCardtoHand(subclass(self.Game, self.ID), self.ID)
			
		return self, None
		
	def discoverDecided(self, option):
		if self.spell1 == None:
			self.spell1 = type(option)
		else:
			self.spell2 = type(option)
			
			
class DrustvarHorror(Minion):
	Class, race, name = "Shaman", "", "Drustvar Horror"
	mana, attack, health = 5, 5, 5
	index = "Shadows-Shaman-5-5-5-Minion-None-Drustvar Horror-Battlecry-Uncollectible"
	needTarget, keyWord, description = False, "", "Battlecry: Cast (0) and (1)"
	learnedSpell1, learnedSpell2 = None, None
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.learnedSpell1 = type(self).learnedSpell1
		self.learnedSpell2 = type(self).learnedSpell2
		
	def whenEffective(self, target=None, comment="", choice=0):
		print("Drustvar Horror's battlecry casts the FIRST spell %s it learned on"%self.learnedSpell1.name, target)
		spell1 = self.learnedSpell1(self.Game, self.ID)
		#假设恐魔的第一个战吼会触发风潮的效果而使用两次
		repeatTimes = 2 if self.Game.playerStatus[self.ID]["Spells Cast Twice"] > 0 else 1
		for i in range(repeatTimes):
			if spell1.overload > 0:
				print(spell1.name, "is played and Overloads %d mana crystals."%self.overload)
				self.Game.ManaHandler.overloadMana(spell1.overload, self.ID)
			if spell1.twinSpell > 0:
				self.Game.Hand_Deck.addCardtoHand(spell1.index.replace("-Twinspell", "") + "-Uncollectible", self.ID, "CreateUsingIndex")
			target = spell1.whenEffective(target, "CastbyOthers", choice=0)
		self.Game.sendSignal("SpellBeenCast", self.Game.turn, spell1, target, 0, "CastbyOthers")
		
		print("Drustvar Horror's battlecry casts the SECOND spell %s it learned on"%self.learnedSpell1.name, target)
		spell2 = self.learnedSpell2(self.Game, self.ID)
		if spell2.overload > 0:
			print(spell2.name, "is played and Overloads %d mana crystals."%self.overload)
			self.Game.ManaHandler.overloadMana(spell2.overload, self.ID)
		if spell2.twinSpell > 0:
			self.Game.Hand_Deck.addCardtoHand(spell2.index.replace("-Twinspell", "") + "-Uncollectible", self.ID, "CreateUsingIndex")
		target = spell2.whenEffective(target, "CastbyOthers", choice=0)
		
		return self, target
		
"""Warlock cards"""
class EVILGenius(Minion):
	Class, race, name = "Warlock", "", "EVIL Genius"
	mana, attack, health = 2, 2, 2
	index = "Shadows-Warlock-2-2-2-Minion-None-EVIL Genius-Battlecry"
	needTarget, keyWord, description = True, "", "Battlecry: Destroy a friendly minion to add 2 random Lackeys to your hand"
	
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			print("EVIL Genius's battlecry destroys friendly minion %s and adds two lackeys to player's hand."%target.name)
			target.dead = True
			self.Game.Hand_Deck.addCardtoHand(np.random.choice(Lackeys, 2, replace=False), self.ID, "CreateUsingType")
		return self, target
		
class RafaamsScheme(Spell):
	Class, name = "Warlock", "Rafaam's Scheme"
	needTarget, mana = False, 3
	index = "Shadows-Warlock-3-Spell-Rafaam's Scheme"
	description = "Summon 1 1/1 Imp(Upgrades each turn!)"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.progress = 1
		self.triggersinHand = [Trigger_Upgrade(self)]
		
	def whenEffective(self, target=None, comment="", choice=0):
		print("Rafaam's Scheme is cast and summons %d Imps."%self.progress)
		self.Game.summonMinion([Imp_RiseofShadows(self.Game, self.ID) for i in range(self.progress)], (-1, "totheRightEnd"), self.ID)
		return None
		
		
class AranasiBroodmother(Minion):
	Class, race, name = "Warlock", "Demon", "Aranasi Broodmother"
	mana, attack, health = 6, 4, 6
	index = "Shadows-Warlock-6-4-6-Minion-Demon-Aranasi Broodmother-Taunt-Triggers when Drawn"
	needTarget, keyWord, description = False, "Taunt", "Taunt. When you draw this, restore 4 Health to your hero"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggers["Drawn"] = [self.restore4HealthtoHero]
		
	def restore4HealthtoHero(self):
		heal = 4 * (2 ** self.countHealDouble())
		print("Aranasi Broodmother is drawn and restores %d Health to player"%heal)
		self.restoresHealth(self.Game.heroes[self.ID], heal)
		
		
class PlotTwist(Spell):
	Class, name = "Warlock", "Plot Twist"
	needTarget, mana = False, 2
	index = "Shadows-Warlock-2-Spell-Plot Twist"
	description = "Shuffle your hand into your deck. Draw that many cards"
	def whenEffective(self, target=None, comment="", choice=0):
		print("Plot Twist is cast and shuffles all of player's hand into deck. Then draw that many cards.")
		handSize = len(self.Game.Hand_Deck.hands[self.ID])
		cardstoShuffle, mana, isRightmostCardinHand = self.Game.Hand_Deck.extractfromHand(None, True, self.ID) #Extract all cards.
		#Remove all the temp effects on cards in hand, e.g, TheSoularium and the echo trigger
		for card in cardstoShuffle:
			for trigger in card.triggersinHand:
				if trigger.temp:
					trigger.disconnect()
					extractfrom(trigger, card.triggersinHand)
					
			self.Game.Hand_Deck.shuffleCardintoDeck(card, self.ID) #Initiated by self.
			
		for i in range(handSize):
			self.drawCard(self.ID)
		return None
		
		
class Impferno(Spell):
	Class, name = "Warlock", "Impferno"
	needTarget, mana = False, 3
	index = "Shadows-Warlock-3-Spell-ImpfernoTwist"
	
	def whenEffective(self, target=None, comment="", choice=0):
		damage = (1 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		print("Impferno is cast, gives all friendly Demons +1 attack and deals %d damage to enemy minions."%damage)
		for minion in self.Game.minionsonBoard(self.ID):
			if "Demon" in minion.race:
				minion.buffDebuff(1, 1)
				
		targets = self.Game.minionsonBoard(3-self.ID)
		self.dealsAOE(targets, [damage for minion in targets])
		return None
		
		
class EagerUnderling(Minion):
	Class, race, name = "Warlock", "", "Eager Underling"
	mana, attack, health = 4, 2, 2
	index = "Shadows-Warlock-4-2-2-Minion-None-Eager Underling-Deathrattle"
	needTarget, keyWord, description = False, "", "Deathrattle: Give two random friendly minions +2/+2"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [GiveTwoRandomFriendlyMinionsPlus2Plus2(self)]
		
class GiveTwoRandomFriendlyMinionsPlus2Plus2(Deathrattle_Weapon):
	def trigger(self, signal, ID, subject, target, number, comment, choice=0):
		friendlyMinions = self.Game.minionsonBoard(self.entity.ID)
		print("Deathrattle: Give Two Random Friendly Minions +2/+2 triggers.")
		if len(friendlyMinions) > 1:
			minionstoBuff = np.random.choice(friendlyMinions, 2, replace=False)
			minionstoBuff[0].buffDebuff(2, 2)
			minionstoBuff[1].buffDebuff(2, 2)
		elif len(friendlyMinions) == 1:
			friendlyMinions[0].buffDebuff(2, 2)
			
			
class DarkestHour(Spell):
	Class, name = "Warlock", "Darkest Hour"
	needTarget, mana = False, 6
	index = "Shadows-Warlock-6-Spell-Darkest Hour"
	description = "Destroy all friendly minions. For each one, summon a random minion from your deck"
	def whenEffective(self, target=None, comment="", choice=0):
		print("Darkest Hour is cast, destroys all friendly minions and summons equal number of minions from deck.")
		boardSize = len(self.Game.minionsonBoard(self.ID))
		for minion in self.Game.minoinsonBoard:
			minion.dead = True
		#对于所有友方随从强制死亡，并令其离场，因为召唤的随从是在场上右边，不用记录死亡随从的位置
		self.Game.gathertheDead()
		minionsinDeck = []
		for card in self.Game.Hand_Deck.decks[self.ID]:
			if card.cardType == "Minion":
				minionsinDeck.append(card)
				
		numSummon = min(boardSize, len(minionsinDeck))
		if numSummon > 0:
			self.Game.summonMinion(np.random.choice(minionsinDeck, numSummon, replace=False), (-1, "totheRightEnd"), self.ID)
			
		return None
		
#For now, assume the mana change is on the mana_set and shuffling this card back into deck won't change its counter.
class JumboImp(Minion):
	Class, race, name = "Warlock", "Demon", "Jumbo Imp"
	mana, attack, health = 10, 8, 8
	index = "Shadows-Warlock-10-8-8-Minion-Demon-Jumbo Imp"
	needTarget, keyWord, description = False, "", "Costs (1) less whenever a friendly minion dies while this is in your hand"
	#def __init__(self, Game, ID):
	#	self.blank_init(Game, ID)
	#	self.triggersinHand = [Trigger_JumboImp(self)]
	##不知道这种减费是自己的基础费用减少还是最后结算费用的selfManaChange
	#def selfManaChange(self):
	#	numYourTreantsDiedThisGame = 0
	#	for index in self.Game.CounterHandler.minionsDiedThisGame[self.ID]:
	#		if "-Treant" in index:
	#			numYourTreantsDiedThisGame += 1
	#			
	#	self.mana -= numYourTreantsDiedThisGame
	#	self.mana = max(self.mana, 0)
		
class Trigger_JumboImp(TriggerinHand):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionDies"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.inHand and target.name == "Treant"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.Game.ManaHandler.calcMana_Single(self.entity)
		
			
class ArchVillainRafaam(Minion):
	Class, race, name = "Warlock", "", "Arch-Villain Rafaam"
	mana, attack, health = 7, 7, 8
	index = "Shadows-Warlock-7-7-8-Minion-None-Arch-Villain Rafaam-Taunt-Battlecry-Legendary"
	needTarget, keyWord, description = False, "Taunt", "Battlecry: Replace your hand and deck with Legendary minions"
	
	def whenEffective(self, target=None, comment="", choice=0):
		print("Arch-Villain Rafaam's battlecry replaces player's hand and deck with random Legendary minions.")
		minions = list(self.Game.LegendaryMinions.values())
		handSize = len(self.Game.Hand_Deck.hands[self.ID])
		self.Game.Hand_Deck.extractfromHand(None, True, self.ID)
		deckSize = len(self.Game.Hand_Deck.decks[self.ID])
		self.Game.Hand_Deck.extractfromDeck(None, True, self.ID)
		#choice will return empty lists if handSize/deckSize == 0
		minionstoHand = np.random.choice(minions, handSize, replace=True)
		self.Game.Hand_Deck.addCardtoHand(minionstoHand, self.ID, "CreateUsingType")
		minionstoDeck = np.random.choice(minions, deckSize, replace=True)
		self.Game.Hand_Deck.decks[self.ID] = [minion(self.Game, self.ID) for minion in minionstoDeck]
		for card in self.Game.Hand_Deck.decks[self.ID]:
			card.entersDeck()
		return self, None
		
		
class FelLordBetrug(Minion):
	Class, race, name = "Warlock", "Demon", "Fel Lord Betrug"
	mana, attack, health = 8, 5, 7
	index = "Shadows-Warlock-8-5-7-Minion-Demon-Fel Lord Betrug-Legendary"
	needTarget, keyWord, description = False, "", "Whenever you draw a minion, summon a copy with Rush that dies at end of turn"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_FelLordBetrug(self)]
		
class Trigger_FelLordBetrug(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["CardDrawn"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and target.cardType == "Minion" and target.ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("Whenever player draws minion %s, %s summons a copy of it that has Rush and dies at the end of turn."%(target.name, self.entity.name))
		minion = target.selfCopy(self.entity.ID)
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
		print("At the end of turn, minion %s affected by FelLord Betrug dies."%self.entity.name)
		self.entity.dead = True
		
"""Warrior cards"""
class ImproveMorale(Spell):
	Class, name = "Warrior", "Improve Morale"
	needTarget, mana = True, 1
	index = "Shadows-Warrior-1-Spell-Improve Morale"
	description = "Deal 1 damage to a minion. If it survives, add a Lackey to your hand"
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			damage = (1 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			print("Improve Morale is cast and deals %d damage to minion "%damage, target.name)
			self.dealsDamage(target, damage)
			if target.health > 0 and target.dead == False:
				print("The target survives Improve Morale, a Lackey is added to player's hand.")
				self.Game.Hand_Deck.addCardtoHand(np.random.choice(Lackeys), self.ID, "CreateUsingType")
		return target
		
		
class ViciousScraphound(Minion):
	Class, race, name = "Warrior", "Mech", "Vicious Scraphound"
	mana, attack, health = 2, 2, 2
	index = "Shadows-Warrior-2-2-2-Minion-Mech-Vicious Scraphound"
	needTarget, keyWord, description = False, "", "Whenever this minion deals damage, gain that much Armor"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_ViciousScraphound(self)]
		
class Trigger_ViciousScraphound(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionTakesDamage", "HeroTakesDamage"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return subject == self.entity
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print(self.entity.name, "deals damage to %s and player gains 2 Armor."%target.name)
		self.entity.Game.heroes[self.entity.ID].gainsArmor(number)
		
		
class DrBoomsScheme(Spell):
	Class, name = "Warrior", "Dr. Boom's Scheme"
	needTarget, mana = False, 4
	index = "Shadows-Warrior-4-Spell-Dr. Boom's Scheme"
	description = "Gain 1 Armor. (Upgrades each turn!)"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.progress = 1
		self.triggersinHand = [Trigger_Upgrade(self)]
		
	def whenEffective(self, target=None, comment="", choice=0):
		print("Dr. Boom's Scheme is cast and player gains %d Armor."%self.progress)
		self.Game.heroes[self.ID].gainsArmor(self.progress)
		return None
		
		
class SweepingStrike(Spell):
	Class, name = "Warrior", "Sweeping Strike"
	needTarget, mana = True, 2
	index = "Shadows-Warrior-2-Spell-Sweeping Strike"
	description = "Give a minion 'Also damages minions next to whoever this attacks'"
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			print("Sweeping Strike is cast and gives minion %s 'Also damage adjacent minions to whoever this attacks'."%target.name)
			target.marks["Attack Adjacent Minions"] += 1
		return target
		
		
class ClockworkGoblin(Minion):
	Class, race, name = "Warrior", "Mech", "Clockwork Goblin"
	mana, attack, health = 3, 3, 3
	index = "Shadows-Warrior-3-3-3-Minion-Mech-Clockwork Goblin-Battlecry"
	needTarget, keyWord, description = False, "", "Battlecry: Shuffle a Bomb in to your opponent's deck. When drawn, it explodes for 5 damage"
	
	def whenEffective(self, target=None, comment="", choice=0):
		print("Clockwork Goblin's battlecry shuffles a Bomb into opponents deck. When its drawn, it deals 5 damage to enemy hero.")
		self.Game.Hand_Deck.shuffleCardintoDeck(Bomb(self.Game, 3-self.ID), self.ID)
		return self, None
		
		
class DimensionalRipper(Spell):
	Class, name = "Warrior", "Dimensional Ripper"
	needTarget, mana = False, 10
	index = "Shadows-Warrior-10-Spell-Dimensional Ripper"
	description = "Summon 2 copies of a minion in your deck"
	
	def whenEffective(self, target=None, comment="", choice=0):
		print("Dimensional Ripper is cast and summons two copies of a minion in player's deck.")
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
	index = "Shadows-Warrior-4-4-5-Minion-Mech-Omega Devastator-Battlecry"
	needTarget, keyWord, description = False, "", "Battlecry: If you have 10 Mana Crystals, deal 10 damage to a minion"
	
	def returnTrue(self, choice=0):
		return self.Game.ManaHandler.manasUpper[self.ID] >= 10
		
	def effectCanTrigger(self):
		return self.Game.ManaHandler.manasUpper[self.ID] >= 10
		
	def targetExists(self, choice=0):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target):
		return target.cardType == "Minion" and target != self and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None and self.Game.ManaHandler.manasUpper[self.ID] >= 10:
			print("Omega Devastator's battlecry deals 10 damage to minion ", target.name)
			self.dealsDamage(target, 10)
		return self, target
		
		
class Wrenchcalibur(Weapon):
	Class, name, description = "Warrior", "Wrenchcalibur", "After your hero attacks, shuffle a Bomb into your Opponent's deck"
	mana, attack, durability = 4, 3, 2
	index = "Shadows-Warrior-4-3-2-Weapon-Wrenchcalibur"
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
		print("After hero attacks, Wrenchcalibur triggers and shuffles a Bomb in to opponent's deck")
		self.entity.Game.Hand_Deck.shuffleCardintoDeck(Bomb(self.entity.Game, 3-self.entity.ID), self.entity.ID)
		
		
class BlastmasterBoom(Minion):
	Class, race, name = "Warrior", "", "Blastmaster Boom"
	mana, attack, health = 7, 7, 7
	index = "Shadows-Warrior-7-7-7-Minion-Mech-Blastmaster Boom-Battlecry-Legendary"
	needTarget, keyWord, description = False, "", "Battlecry: Summon two 1/1 Boom Bots for each Bomb in your opponent's deck"
	
	def whenEffective(self, target=None, comment="", choice=0):
		numBombsinDeck = 0
		for card in self.Game.Hand_Deck.decks[3-self.ID]:
			if card.name == "Bomb":
				numBombsinDeck += 1
				
		numSummon = min(8, 2 * numBombsinDeck)
		print("Blastmaster Boom's battlecry summons two 1/1 Boom Bots for each Bomb in opponent's deck.")
		pos = (self.position, "leftandRight") if self.onBoard else (-1, "totheRightEnd")
		self.Game.summonMinion([BoomBot_Shadows(self.Game, self.ID) for i in range(numSummon)], pos, self.ID)
		return self, None
		
class BoomBot_Shadows(Minion):
	Class, race, name = "Neutral", "Mech", "Boom Bot"
	mana, attack, health = 1, 1, 1
	index = "Shadows-Neutral-1-1-1-Minion-Mech-Boom Bot-Deathrattle-Uncollectible"
	needTarget, keyWord, description = False, "", "Deathrattle: Deal 1~4 damage to a random enemy"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [Deal1to4DamagetoaRandomEnemy(self)]
		
class Deal1to4DamagetoaRandomEnemy(Deathrattle_Minion):
	def trigger(self, signal, ID, subject, target, number, comment, choice=0):
		print("Deathrattle: Deal 1~4 damage to a random enemy triggers.")
		targets = [self.entity.Game.heroes[3-self.entity.ID]]
		for minion in self.entity.Game.minionsonBoard(3-self.entity.ID):
			if minion.health > 0 and minion.dead == False:
				targets.append(minion)
				
		self.entity.dealsDamage(np.random.choice(targets), np.random.randint(1, 5))
		
		
class TheBoomReaver(Minion):
	Class, race, name = "Warrior", "Mech", "The Boom Reaver"
	mana, attack, health = 10, 7, 9
	index = "Shadows-Warrior-10-7-9-Minion-Mech-The Boom Reaver-Battlecry-Legendary"
	needTarget, keyWord, description = False, "", "Battlecry: Summon a copy of a minion in your deck. Give it Rush"
	
	def whenEffective(self, target=None, comment="", choice=0):
		print("The Boom Reaver's battlecry summons a copy of minion in player's deck and gives it Rush.")
		if self.Game.spaceonBoard(self.ID) > 0:
			minionsinDeck = []
			for card in self.Game.Hand_Deck.decks[self.ID]:
				if card.cardType == "Minion":
					minionsinDeck.append(card)
					
			if minionsinDeck != []:
				minion = np.random.choice(minionsinDeck).selfCopy(self.ID)
				minion.getsKeyword("Rush")
				self.Game.summonMinion(minion, self.position+1, self.ID)
		return self, None
		