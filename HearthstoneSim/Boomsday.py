from CardTypes import *
import CardIndices
from Classic import Deal2DamagetoEnemyHero
from Triggers_Auras import *
from VariousHandlers import *

import numpy as np
import copy 
import random

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
class Crystalizer(Minion):
	Class, race, name = "Neutral", "", "Crystalizer"
	mana, attack, health = 1, 1, 3
	index = "Boomsday-Neutral-1-1-3-Minion-None-Crystalizer-Battlecry"
	needTarget, keyWord, description = False, "", "Battlecry: Deal 5 damage to your hero. Gain 5 Armor"
	
	def whenEffective(self, target=None, comment="", choice=0):
		print("Crystalizer's battlecry deals 5 damage to player's hero. Play then gains 5 Armor.")
		self.dealsDamage(self.Game.heroes[self.ID], 5)
		self.Game.heroes[self.ID].gainsArmor(5)
		return self, None
		
		
class FaithfulLumi(Minion):
	Class, race, name = "Neutral", "Mech", "Faithful Lumi"
	mana, attack, health = 1, 1, 1
	index = "Boomsday-Neutral-1-1-1-Minion-Mech-Faithful Lumi-Battlecry"
	needTarget, keyWord, description = True, "", "Battlecry: Give a friendly Mech +1/+1"
	
	def targetExists(self, choice=0):
		return self.selectableFriendlyMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and "Mech" in target.race and target.ID == self.ID and target != self
		
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			print("Faithful Lumi's battlecry gives friendly Mech %s +1/+1."%target.name)
			target.buffDebuff(1, 1)
		return self, target
		
		
class GoblinBomb(Minion):
	Class, race, name = "Neutral", "Mech", "Goblin Bomb"
	mana, attack, health = 1, 0, 2
	index = "Boomsday-Neutral-1-0-2-Minion-Mech-Goblin Bomb-Deathrattle"
	needTarget, keyWord, description = False, "", "Deathrattle: Deal 2 damage to the enemy hero"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [Deal2DamagetoEnemyHero(self)] #Refer to Classic card: Leper Gnome
		
class Mecharoo(Minion):
	Class, race, name = "Neutral", "Mech", "Mecharoo"
	mana, attack, health = 1, 1, 1
	index = "Boomsday-Neutral-1-1-1-Minion-Mech-Mecharoo-Deathrattle"
	needTarget, keyWord, description = False, "", "Deathrattle: Summon a 1/1 Jo-E Bot"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [SummonaJoeBot(self)]
		
class SummonaJoeBot(Deathrattle_Minion):
	def trigger(self, signal, ID, subject, target, number, comment, choice=0):
		print("Deathrattle: Summon a 1/1 Jo-E Bot triggers.")
		self.entity.Game.summonMinion(JoEBot(self.entity.Game, self.entity.ID), self.entity.position+1, self.entity.ID)
		
class JoEBot(Minion):
	Class, race, name = "Neutral", "Mech", "Jo-E Bot"
	mana, attack, health = 1, 1, 1
	index = "Boomsday-Neutral-1-1-1-Minion-Mech-Jo-E Bot-Uncollectible"
	needTarget, keyWord, description = False, "", ""
	
	
class Skaterbot(Minion):
	Class, race, name = "Neutral", "Mech", "Skaterbot"
	mana, attack, health = 1, 1, 1
	index = "Boomsday-Neutral-1-1-1-Minion-Mech-Skaterbot-Rush-Magnetic"
	needTarget, keyWord, description = False, "Rush", "Rush, Magnetic"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.magnetic = 1
		
"""Mana 2 cards"""		
class CloakscaleChemist(Minion):
	Class, race, name = "Neutral", "", "Cloakscale Chemist"
	mana, attack, health = 2, 1, 2
	index = "Boomsday-Neutral-2-1-2-Minion-None-Cloakscale Chemist-Stealth-Divine Shield"
	needTarget, keyWord, description = False, "Stealth,Divine Shield", "Stealth, Divine Shield"
	
	
class Galvanizer(Minion):
	Class, race, name = "Neutral", "Mech", "Galvanizer"
	mana, attack, health = 2, 1, 2
	index = "Boomsday-Neutral-2-1-2-Minion-Mech-Galvanizer-Battlecry"
	needTarget, keyWord, description = False, "", "Battlecry: Reduce the cost of Mechs in your hand by (1)"
	
	def whenEffective(self, target=None, comment="", choice=0):
		print("Galvanizer's battlecry reduces the cost of Mechs in player's hand by (1).")
		for card in self.Game.Hand_Deck.hands[self.ID]:
			if card.cardType == "Minion" and "Mech" in card.race:
				card.mana_set -= 1
				
		self.Game.ManaHandler.calcMana_All()
		return self, None
		
		
class SparkEngine(Minion):
	Class, race, name = "Neutral", "Mech", "Spark Engine"
	mana, attack, health = 2, 2, 1
	index = "Boomsday-Neutral-2-2-1-Minion-Mech-Spark Engine-Battlecry"
	needTarget, keyWord, description = False, "", "Battlecry: Add a 1/1 Spark with Rush into your hand"
	
	def whenEffective(self, target=None, comment="", choice=0):
		print("Spark Engine's battlecry adds a 1/1 Spark with Rush into player's hand.")
		self.Game.Hand_Deck.addCardtoHand(Spark(self.Game, self.ID), self.ID)
		return self, None
		
class Spark(Minion):
	Class, race, name = "Neutral", "Elemental", "Spark"
	mana, attack, health = 1, 1, 1
	index = "Boomsday-Neutral-1-1-1-Minion-Elemental-Spark-Rush-Uncollectible"
	needTarget, keyWord, description = False, "Rush", "Rush"
	
	
class Toxicologist(Minion):
	Class, race, name = "Neutral", "", "Toxicologist"
	mana, attack, health = 2, 2, 2
	index = "Boomsday-Neutral-2-2-2-Minion-None-Toxicologist-Battlecry"
	needTarget, keyWord, description = False, "", "Battlecry: Give your weapon +1 Attack"
	
	def whenEffective(self, target=None, comment="", choice=0):
		weapon = self.Game.availableWeapon(self.ID)
		if weapon != None:
			print("Toxicologist's battlecry gives player's weapon +1 attack.")
			weapon.gainStat(1, 0)
		return self, None
		
		
class UnpoweredMauler(Minion):
	Class, race, name = "Neutral", "Mech", "Unpowered Mauler"
	mana, attack, health = 2, 2, 4
	index = "Boomsday-Neutral-2-2-4-Minion-Mech-Unpowered Mauler"
	needTarget, keyWord, description = False, "", "Can only attack if you cast a spell this turn"
	
	def canAttack(self):
		if self.actionable() == False or self.attack < 1 or self.status["Frozen"] > 0:
			return False
		if self.silenced == False and self.Game.CounterHandler.numSpellsPlayedThisTurn[self.ID] < 1:
			return False
		if self.attChances_base + self.attChances_extra <= self.attTimes:
			return False
		if self.marks["Can't Attack"] > 0:
			return False
		return True	
		
		
class UpgradeableFramebot(Minion):
	Class, race, name = "Neutral", "Mech", "Upgradeable Framebot"
	mana, attack, health = 2, 1, 5
	index = "Boomsday-Neutral-2-1-5-Minion-Mech-Upgradeable Framebot"
	needTarget, keyWord, description = False, "", ""
	
	
class Whirlglider(Minion):
	Class, race, name = "Neutral", "", "Whirlglider"
	mana, attack, health = 2, 2, 1
	index = "Boomsday-Neutral-2-2-1-Minion-None-Whirlglider-Battlecry"
	needTarget, keyWord, description = False, "", "Battlecry: Summon a 0/2 Goblin Bomb"
	
	def whenEffective(self, target=None, comment="", choice=0):
		print("Whirlglider's battlecry summons a 0/2 Goblin Bomb.")
		self.Game.summonMinion(GoblinBomb(self.Game, self.ID), self.position+1, self.ID)
		return self, None
		
"""Mana 3 cards"""
class AugmentedElekk(Minion):
	Class, race, name = "Neutral", "Beast", "Augmented Elekk"
	mana, attack, health = 3, 3, 4
	index = "Boomsday-Neutral-3-3-4-Minion-Beast-Augmented Elekk"
	needTarget, keyWord, description = False, "", "Whenver you shuffle a card into a deck, shuffle in an extra copy"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_AugmentedElekk(self)]
		
class Trigger_AugmentedElekk(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["CardShuffled"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("Player shuffles a card into deck and %s shuffles in an extra copy of it."%self.entity.name)
		if type(target) == type([]) or type(target) == type(np.array([])):
			for card in obj:
				Copy = card.selfCopy(card.ID)
				self.Game.decks[card.ID].append(Copy)
				Copy.entersDeck()
			np.random.shuffle(self.Game.decks[target[0].ID])
		else: #A single card is shuffled.
			Copy = target.selfCopy(target.ID)
			self.Game.decks[target.ID].append(Copy)
			Copy.entersDeck()
			np.random.shuffle(self.Game.decks[target.ID])
			
			
class Brainstormer(Minion):
	Class, race, name = "Neutral", "", "Brainstormer"
	mana, attack, health = 3, 3, 1
	index = "Boomsday-Neutral-3-3-1-Minion-None-Brainstormer-Battlecry"
	needTarget, keyWord, description = False, "", "Battlecry: Gain +1 Health for each spell in your hand"
		
	def whenEffective(self, target=None, comment="", choice=0):
		if self.inHand or self.onBoard:
			numSpellsinHand = 0
			for card in self.Game.Hand_Deck.hands[self.ID]:
				if "-Spell-" in card.index:
					numSpellsinHand += 1
			print("Brainstormer's battlecry gives +1 health for each spell in player's hand.")
			self.buffDebuff(0, numSpellsinHand)
		return self, None
		
		
class BronzeGatekeeper(Minion):
	Class, race, name = "Neutral", "Mech", "Bronze Gatekeeper"
	mana, attack, health = 3, 1, 5
	index = "Boomsday-Neutral-3-1-5-Minion-Mech-Bronze Gatekeeper-Taunt-Magnetic"
	needTarget, keyWord, description = False, "Taunt", "Taunt, Magnetic"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.magnetic = 1
	
class Electrowright(Minion):
	Class, race, name = "Neutral", "", "Electrowright"
	mana, attack, health = 3, 3, 3
	index = "Boomsday-Neutral-3-3-3-Minion-None-Electrowright-Battlecry"
	needTarget, keyWord, description = False, "", "Battlecry: If you are holding a spell that costs (5) or more, gain +1/+1"
	
	def whenEffective(self, target=None, comment="", choice=0):
		for card in self.Game.Hand_Deck.hands[self.ID]:
			if card.cardType == "Spell" and card.mana > 4:
				print("Electrowright's battlecry gains +1/+1 for holding spells that cost no less than 5.")
				self.buffDebuff(1, 1)
				break
		return self, None
		
		
class KaboomBot(Minion):
	Class, race, name = "Neutral", "Mech", "Kaboom Bot"
	mana, attack, health = 3, 2, 2
	index = "Boomsday-Neutral-3-2-2-Minion-Mech-Kaboom Bot-Deathrattle"
	needTarget, keyWord, description = False, "", "Deathrattle: Deal 4 damage to a random enemy minion"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [Deal4DamagetoaRandomEnemyMinion(self)]
		
class Deal4DamagetoaRandomEnemyMinion(Deathrattle_Minion):
	def trigger(self, signal, ID, subject, target, number, comment, choice=0):
		enemyMinions = []
		for obj in self.entity.Game.minions[3-self.entity.ID]:
			if obj.cardType == "Minion" and obj.health > 0 and obj.dead == False:
				enemyMinions.append(obj)
				
		if enemyMinions != []:
			print("Deathrattle: Deal 4 damage to a random enemy minion triggers.")
			self.entity.dealsDamage(np.random.choice(enemyMinions), 4)
			
			
class MicrotechController(Minion):
	Class, race, name = "Neutral", "", "Microtech Controller"
	mana, attack, health = 3, 2, 1
	index = "Boomsday-Neutral-3-2-1-Minion-None-Microtech Controller-Battlecry"
	needTarget, keyWord, description = False, "", "Battlecry: Summon two 1/1 Microbots"
	
	def whenEffective(self, target=None, comment="", choice=0):
		print("Microtech Controller's battlecry summons two 1/1 Microbots.")
		pos = (self.position, "leftandRight") if self.onBoard else (-1, "totheRightEnd")
		self.Game.summonMinion([Microbot(self.Game, self.ID) for i in range(2)], pos, self.ID)
		return self, None
		
class Microbot(Minion):
	Class, race, name = "Neutral", "Mech", "Microbot"
	mana, attack, health = 1, 1, 1
	index = "Boomsday-Neutral-1-1-1-Minion-Mech-Microbot-Uncollectible"
	needTarget, keyWord, description = False, "", ""
	
	
class Sn1pSn4p(Minion):
	Class, race, name = "Neutral", "Mech", "Sn1p-Sn4p"
	mana, attack, health = 3, 2, 3
	index = "Boomsday-Neutral-3-2-3-Minion-Mech-Sn1p-Sn4p-Magnetic-Echo-Deathrattle-Legendary"
	needTarget, keyWord, description = False, "Echo", "Magnetic, Echo. Deathrattle: Summon two 1/1 Microbots"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.magnetic = 1
		self.deathrattles = [SummonTwoMicrobots(self)]
		
class SummonTwoMicrobots(Deathrattle_Minion):
	def trigger(self, signal, ID, subject, target, number, comment, choice=0):
		pos = (self.entity.position, "totheRight") if self.entity in self.entity.Game.minions[self.entity.ID] else (-1, "totheRightEnd")
		print("Deathrattle: Summon two 1/1 Microbots triggers")
		self.entity.Game.summonMinion([Microbot(self.entity.Game, self.entity.ID) for i in range(2)], pos, self.entity.ID)
		
		
class SpringRocket(Minion):
	Class, race, name = "Neutral", "Mech", "Spring Rocket"
	mana, attack, health = 3, 2, 1
	index = "Boomsday-Neutral-3-2-1-Minion-Mech-Spring Rocket-Battlecry"
	needTarget, keyWord, description = True, "", "Battlecry: Deal 2 damage"
	
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			print("Spring Rocket's battlecry deals 2 damage to ", target.name)
			self.dealsDamage(target, 2)
		return self, target
		
"""Mana 4 cards"""
class CoppertailImposter(Minion):
	Class, race, name = "Neutral", "Mech", "Coppertail Imposter"
	mana, attack, health = 4, 4, 4
	index = "Boomsday-Neutral-4-4-4-Minion-Mech-Coppertail Imposter-Battlecry"
	needTarget, keyWord, description = False, "", "Battlecry: Gain Stealth until your next turn"
	
	def whenEffective(self, target=None, comment="", choice=0):
		print("Coppertail Imposter's battlecry gives minion Stealth until next turn.")
		self.status["Temp Stealth"] += 1
		return self, None
		
		
class Explodinator(Minion):
	Class, race, name = "Neutral", "Mech", "Explodinator"
	mana, attack, health = 4, 3, 2
	index = "Boomsday-Neutral-4-3-2-Minion-Mech-Explodinator-Battlecry"
	needTarget, keyWord, description = False, "", "Battlecry: Summon two 0/2 Goblin Bombs"
	
	def whenEffective(self, target=None, comment="", choice=0):
		print("Explodinator's battlecry summons two 0/2 Goblin Bombs.")
		self.Game.summonMinion([GoblinBomb(self.Game, self.ID) for i in range(2)], (self.position, "leftandRight", 2), self.ID)
		return self, None
		
		
class HarbingerCelestia(Minion):
	Class, race, name = "Neutral", "", "Harbinger Celestia"
	mana, attack, health = 4, 5, 6
	index = "Boomsday-Neutral-4-5-6-Minion-None-Harbinger Celestia-Legendary"
	needTarget, keyWord, description = False, "Stealth", "Stealth. After your opponent plays a minion, become a copy of it"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_HarbingerCelestia(self)]
		
class Trigger_HarbingerCelestia(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionBeenPlayed"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject.ID != self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("An enemy minion %s is played and %s becomes a copy of it."%(subject.name, self.entity.name))
		Copy = subject.selfCopy(self.entity.ID)
		self.entity.Game.transforms(self.entity, Copy)
		
		
class OmegaDefender(Minion):
	Class, race, name = "Neutral", "", "Omega Defender"
	mana, attack, health = 4, 2, 6
	index = "Boomsday-Neutral-4-2-6-Minion-None-Omega Defender-Taunt-Battlecry"
	needTarget, keyWord, description = False, "Taunt", "Taunt. Battlecry: If you have 10 Mana Crystals, gain +10 Attack"
	
	def whenEffective(self, target=None, comment="", choice=0):
		if self.Game.ManaHandler.manasUpper[self.ID] > 9:
			print("Omega Defender's battlecry gives minion +10 attack, because player has 10 mana crystals.")
			self.buffDebuff(10, 0)
		return self, None
		
		
class PilotedReaper(Minion):
	Class, race, name = "Neutral", "Mech", "Piloted Reaper"
	mana, attack, health = 4, 4, 3
	index = "Boomsday-Neutral-4-4-3-Minion-Mech-Piloted Reaper-Deathrattle"
	needTarget, keyWord, description = False, "", "Deathrattle: Summon minion from your hand that costs (2) or less"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [SummonaMinionfromHandthatCosts2orLess(self)]
		
class SummonaMinionfromHandthatCosts2orLess(Deathrattle_Minion):
	def trigger(self, signal, ID, subject, target, number, comment, choice=0):
		minionsinHandwithCost2orLess = []
		for card in self.entity.Game.Hand_Deck[self.entity.ID]:
			if card.cardType == "Minion" and card.mana < 3:
				minionsinHandwithCost2orLess.append(card)
				
		if minionsinHandwithCost2orLess != []:
			print("Deathrattle: Summon a minion from your hand that costs (2) or less triggers")
			self.entity.Game.summonMinion(np.random.choice(minionsinHandwithCost2orLess), self.entity.position+1, self.entity.ID)
			
			
class ReplicatingMenace(Minion):
	Class, race, name = "Neutral", "Mech", "Replicating Menace"
	mana, attack, health = 4, 3, 1
	index = "Boomsday-Neutral-4-3-1-Minion-Mech-Replicating Menace-Magnetic-Deathrattle"
	needTarget, keyWord, description = False, "", "Magnetic. Deathrattle: Summon three 1/1 Microbots"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.magnetic = 1
		self.deathrattles = [SummonThreeMicrobots(self)]
		
class SummonThreeMicrobots(Deathrattle_Minion):
	def trigger(self, signal, ID, subject, target, number, comment, choice=0):
		pos = (self.entity.position, "totheRight") if self.entity in self.entity.Game.minions[self.entity.ID] else (-1, "totheRightEnd")
		print("Deathrattle: Summon three 1/1 Microbots triggers")
		self.entity.Game.summonMinion([Microbot(self.entity.Game, self.entity.ID) for i in range(3)], pos, self.entity.ID)
		
		
class SteelRager(Minion):
	Class, race, name = "Neutral", "Mech", "Steel Rager"
	mana, attack, health = 4, 5, 1
	index = "Boomsday-Neutral-4-5-1-Minion-Mech-Steel Rager-Rush"
	needTarget, keyWord, description = False, "Rush", "Rush"
	
	
class WeaponizedPinata(Minion):
	Class, race, name = "Neutral", "Mech", "Weaponized Pinata"
	mana, attack, health = 4, 4, 3
	index = "Boomsday-Neutral-4-4-3-Minion-Mech-Weaponized Pinata-Deathrattle"
	needTarget, keyWord, description = False, "", "Deathrattle:"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [AddaRandomLegendaryMiniontoYourHand(self)]
		
class AddaRandomLegendaryMiniontoYourHand(Deathrattle_Minion):
	def trigger(self, signal, ID, subject, target, number, comment, choice=0):
		legendaryMinions = list(LegendaryMinions.values())
		print("Deathrattle: Add a random Legendary minion to your hand triggers")
		self.entity.Game.Hand_Deck.addCardtoHand(np.random.choice(legendaryMinions), self.entity.ID, "CreateUsingType")
		
		
class WhizbangtheWonderful(Minion):
	Class, race, name = "Neutral", "", "Whizbang the Wonderful"
	mana, attack, health = 4, 4, 5
	index = "Boomsday-Neutral-4-4-5-Minion-None-Whizbang the Wonderful-Legendary"
	needTarget, keyWord, description = False, "", ""
	
"""Mana 5 cards"""
class EMPOperatives(Minion):
	Class, race, name = "Neutral", "", "E.M.P. Operatives"
	mana, attack, health = 5, 3, 3
	index = "Boomsday-Neutral-5-3-3-Minion-None-E.M.P. Operatives-Battlecry"
	needTarget, keyWord, description = True, "", "Battlecry: Destroy a Mech"
	
	def targetExists(self, choice=0):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and "Mech" in target.race and target.ID == self.ID and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			print("E.M.P. Operatives's battlecry destroys Mech ", target.name)
			target.dead = True
		return self, target
		
		
class Holomancer(Minion):
	Class, race, name = "Neutral", "", "Holomancer"
	mana, attack, health = 5, 3, 3
	index = "Boomsday-Neutral-5-3-3-Minion-None-Holomancer"
	needTarget, keyWord, description = False, "", "After your opponent plays a minion, summon a 1/1 copy of it"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_Holomancer(self)]
	
class Trigger_Holomancer(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionBeenPlayed"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("After an enemy minion %s is played, Holomancer summons a copy of it."%subject.name)
		Copy = subject.selfCopy(self.entity.ID, 1, 1)
		self.entity.Game.summonMinion(Copy, self.entity.position+1, self.entity.ID)
		
		
class LooseSpecimen(Minion):
	Class, race, name = "Neutral", "Beast", "Loose Specimen"
	mana, attack, health = 5, 6, 6
	index = "Boomsday-Neutral-5-6-6-Minion-Beast-Loose Specimen-Battlecry"
	needTarget, keyWord, description = False, "", "Battlecry: Deal 6 damage randomly split among other friendly minions"
	def randomorDiscover(self):
		totalHealth = 0
		totalDamage = 6
		for minion in self.Game.minions[self.ID]:
			if minion.cardType == "Minion":
				totalHealth += minion.health
				
		if self.Game.playerStatus[self.ID]["Battlecry Trigger Twice"] + self.Game.playerStatus[self.ID]["Shark Battlecry Trigger Twice"]:
			totalDamage = 12
		if totalHealth <= totalDamage:
			return "No RNG"
		return "Random"
		
	def whenEffective(self, target=None, comment="", choice=0):
		for i in range(6):
			targets = []
			for minion in self.Game.minionsonBoard(self.ID):
				if minion.health > 0 and minion.dead == False and minion != self:
					targets.append(minion)
					
			if targets == []:
				break
			else:
				self.dealsDamage(np.random.choice(targets), 1)
		return self, None
		
		
class RustyRecycler(Minion):
	Class, race, name = "Neutral", "Mech", "Rusty Recycler"
	mana, attack, health = 5, 2, 6
	index = "Boomsday-Neutral-5-2-6-Minion-Mech-Rusty Recycler-Taunt-Lifesteal"
	needTarget, keyWord, description = False, "Taunt,Lifesteal", "Taunt, Lifesteal"
	
	
class SeaforiumBomber(Minion):
	Class, race, name = "Neutral", "", "Seaforium Bomber"
	mana, attack, health = 5, 5, 5
	index = "Boomsday-Neutral-5-5-5-Minion-None-Seaforium Bomber-Battlecry"
	needTarget, keyWord, description = False, "", "Battlecry: Shuffle a Bomb into opponent's deck"
	
	def whenEffective(self, target=None, comment="", choice=0):
		print("Seaforium Bomber's battlecry shuffles a Bomb into opponent's deck.")
		self.Game.Hand_Deck.shuffleCardintoDeck(Bomb(self.Game, 3-self.ID), self.ID)
		return self, None
		
class Bomb(Spell):
	Class, name = "Neutral", "Bomb"
	needTarget, mana = False, 5
	index = "Boomsday-Neutral-5-Spell-Bomb-Casts When Drawn-Uncollectible"
	description = "Casts When Drawn. Deal 5 damage to your hero"
	def whenEffective(self, target=None, comment="", choice=0):
		damage = (5 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		print("Bomb is cast and deals %d damage to player."%damage)
		self.dealsDamage(self.Game.heroes[self.ID], damage)
		return None
		
		
class Subject9(Minion):
	Class, race, name = "Neutral", "Beast", "Subject 9"
	mana, attack, health = 5, 4, 4
	index = "Boomsday-Neutral-5-4-4-Minion-Beast-Subject 9-Battlecry-Legendary"
	needTarget, keyWord, description = False, "", "Battlecry: Draw 5 different Secrets from your deck"
	
	def whenEffective(self, target=None, comment="", choice=0):
		secrets = []
		secretIndices = []
		for card in self.Game.Hand_Deck.hands[self.ID]:
			if "--Secret" in card.index and card.index not in secretIndices:
				secrets.append(card)
				secretIndices.append(card.index)
				
		for card in secrets:
		#Stops when hand is full and card is milled.
			if self.Game.Hand_Deck.drawCard(self.ID, card)[0] == None:
				break
				
		return self, None
		
		
class Wargear(Minion):
	Class, race, name = "Neutral", "Mech", "Wargear"
	mana, attack, health = 5, 5, 5
	index = "Boomsday-Neutral-5-5-5-Minion-Mech-Wargear-Magnetic"
	needTarget, keyWord, description = False, "", "Magnetic"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.magnetic = 1
	
class Zilliax(Minion):
	Class, race, name = "Neutral", "Mech", "Zilliax"
	mana, attack, health = 5, 3, 2
	index = "Boomsday-Neutral-5-3-2-Minion-Mech-Zilliax-Divine Shield-Taunt-Lifesteal-Rush-Magnetic"
	needTarget, keyWord, description = False, "Divine Shield,Taunt,Lifesteal,Rush", "Magnetic, Divine Shield, Taunt, Lifesteal, Rush"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.magnetic = 1
	
"""Mana 6 cards"""
class ArcaneDynamo(Minion):
	Class, race, name = "Neutral", "", "Arcane Dynamo"
	mana, attack, health = 6, 3, 4
	index = "Boomsday-Neutral-6-3-4-Minion-None-Arcane Dynamo-Battlecry"
	needTarget, keyWord, description = False, "", "Battlecry: Discover a spell that costs (5) or more"
	
	def randomorDiscover(self):
		return "Discover"
		
	def whenEffective(self, target=None, comment="", choice=0):
		if self.ID == self.Game.turn:
			Class = self.Game.heroes[self.ID].Class
			spells = []
			for key, value in self.Game.ClassCards[Class].items():
				if "-Spell-" in key and (int)(key.split('-')[2]) > 4:
					spells.append(value)
				
			if spells != []:
				if comment == "InvokedbyOthers":
					print("Arcane Dynamo's battlecry adds a random spell costing 5 or more to player's hand.")
					spell = np.random.choice(spells)(self.Game, self.ID)
					self.Game.Hand_Deck.addCardtoHand(spell, self.ID)
				else:
					spells = np.random.choice(spells, min(3, len(spells)), replace=False)
					self.Game.options = [spell(self.Game, self.ID) for spell in spells]
					self.Game.DiscoverHandler.startDiscover(self)
					
		return self, None
		
	def discoverDecided(self, option):
		print("Spell %s is put into player's hand."%option.name)
		self.Game.Hand_Deck.addCardtoHand(option, self.ID)
		
		
class DamagedStegotron(Minion):
	Class, race, name = "Neutral", "Mech", "Damaged Stegotron"
	mana, attack, health = 6, 5, 12
	index = "Boomsday-Neutral-6-5-12-Minion-Mech-Damaged Stegotron-Taunt-Battlecry"
	needTarget, keyWord, description = False, "Taunt", "Taunt. Battlecry: Deal 6 damage to this minion"
	
	def whenEffective(self, target=None, comment="", choice=0):
		print("Damaged Stegotron's battlecry deals 6 damage to the minion.")
		self.dealsDamage(self, 6)
		return self, None
		
		
class MechanicalWhelp(Minion):
	Class, race, name = "Neutral", "Mech", "Mechanical Whelp"
	mana, attack, health = 6, 2, 2
	index = "Boomsday-Neutral-6-2-2-Minion-Mech-Mechanical Whelp-Deathrattle"
	needTarget, keyWord, description = False, "", "Deathrattle: Summon a 7/7 Mechanical Dragon"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [SummonaMechanicalDragon(self)]
		
class SummonaMechanicalDragon(Deathrattle_Minion):
	def trigger(self, signal, ID, subject, target, number, comment, choice=0):
		print("Deathrattle: Summon a 7/7 Mechanical Dragon triggers.")
		self.entity.Game.summonMinion(MechanicalDragon(self.entity.Game, self.entity.ID), self.entity.position+1, self.entity.ID)
		
class MechanicalDragon(Minion):
	Class, race, name = "Neutral", "Mech", "Mechanical Dragon"
	mana, attack, health = 7, 7, 7
	index = "Boomsday-Neutral-7-7-7-Minion-Mech-Mechanical Dragon-Uncollectible"
	needTarget, keyWord, description = False, "", ""
	
	
class MissileLauncher(Minion):
	Class, race, name = "Neutral", "Mech", "Missile Launcher"
	mana, attack, health = 6, 4, 4
	index = "Boomsday-Neutral-6-4-4-Minion-Mech-Missile Launcher-Magnetic"
	needTarget, keyWord, description = False, "", "Magnetic. At the end of turn, deal 1 damage to all other characters"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.magnetic = 1
		self.triggersonBoard = [Trigger_MissileLauncher(self)]
		
class Trigger_MissileLauncher(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["TurnEnds"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("At the end of turn, %s deals 1 damage to all other characters."%self.entity.name)
		targets = [self.entity.Game.heroes[1], self.entity.Game.heroes[2]] + self.entity.Game.minionsonBoard(1) + self.entity.Game.minionsonBoard(2)
		extractfrom(self.entity, targets)
		self.entity.dealsAOE(targets, [1 for obj in targets])
		
		
class SparkDrill(Minion):
	Class, race, name = "Neutral", "Mech", "Spark Drill"
	mana, attack, health = 6, 5, 1
	index = "Boomsday-Neutral-6-5-1-Minion-Mech-Spark Drill-Rush-Deathrattle"
	needTarget, keyWord, description = False, "Rush", "Rush. Deathrattle: Add two 1/1 Sparks with Rush to your hand"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [AddTwoSparkstoHand(self)]
		
class AddTwoSparkstoHand(Deathrattle_Minion):
	def trigger(self, signal, ID, subject, target, number, comment, choice=0):
		print("Deathrattle: Add two 1/1 Sparks with Rush to your hand triggers.")
		self.entity.Game.Hand_Deck.addCardtoHand([Sparks, Sparks], self.entity.ID, "CreateUsingType")
		
"""Mana 7 cards"""
class GigglingInventor(Minion):
	Class, race, name = "Neutral", "", "Giggling Inventor"
	mana, attack, health = 7, 2, 1
	index = "Boomsday-Neutral-7-2-1-Minion-None-Giggling Inventor-Battlecry"
	needTarget, keyWord, description = False, "", "Battlecry: Summon two 1/2 Mechs with Taunt and Divine Shield"
	
	def whenEffective(self, target=None, comment="", choice=0):
		print("Giggling Inventor's battlecry summons two 1/2 Mechs with Taunt and Divine Shield.")
		pos = (self.position, "leftandRight") if self.onBoard else (-1, "totheRightEnd")
		self.Game.summonMinion([AnnoyoTron(self.Game, self.ID) for i in range(2)], pos, self.ID)
		return self, None
		
class AnnoyoTron_Boomsday(Minion):
	Class, race, name = "Neutral", "", "Annoy-o-Tron"
	mana, attack, health = 2, 1, 2
	index = "Boomsday-Neutral-2-1-2-Minion-Mech-Annoy-o-Tron-Taunt-Divine Shield-Uncollectible"
	needTarget, keyWord, description = False, "Taunt,Divine Shield", "Taunt, Divine Shield"
	
	
class StarAligner(Minion):
	Class, race, name = "Neutral", "", "Star Aligner"
	mana, attack, health = 7, 7, 7
	index = "Boomsday-Neutral-7-7-7-Minion-None-Star Aligner-Battlecry"
	needTarget, keyWord, description = False, "", "Battlecry: If you control 3 minions with 7 Health, deal 7 damage to all enemies"
	
	def effectCanTrigger(self):
		controlMinionwith7Attack = 0
		for minion in self.Game.minionsonBoard(self.ID):
			if minion.health == 7:
				controlMinionwith7Attack += 1
				
		return controlMinionwith7Attack > 1
		
	def whenEffective(self, target=None, comment="", choice=0):
		controlMinionwith7Attack = 0
		for minion in self.Game.minionsonBoard(self.ID):
			if minion.health == 7:
				controlMinionwith7Attack += 1
				
		if controlMinionwith7Attack > 2:
			targets = [self.Game.heroes[3-self.ID]] + self.Game.minionsonBoard(3-self.ID)
			print("Star Aligner's battlecry deals 7 damage to all enemies.")
			self.dealsAOE(targets, [7 for obj in targets])
		return self, None
		
"""Mana 9 cards"""
class BullDozer(Minion):
	Class, race, name = "Neutral", "Mech", "Bull Dozer"
	mana, attack, health = 9, 9, 7
	index = "Boomsday-Neutral-9-9-7-Minion-Mech-Bull Dozer-Divine Shield"
	needTarget, keyWord, description = False, "Divine Shield", "Divine Shield"
	
"""Mana 10 cards"""
class Mechathun(Minion):
	Class, race, name = "Neutral", "Mech", "Mecha'thun"
	mana, attack, health = 10, 10, 10
	index = "Boomsday-Neutral-10-10-10-Minion-Mech-Mecha'thun-Deathrattle-Legendary"
	needTarget, keyWord, description = False, "", "Deathrattle: If you have no cards in your deck, hand and battlefield, destroy the enemy hero"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [DestroyEnemyHero(self)]
		
class DestroyEnemyHero(Deathrattle_Minion):
	def trigger(self, signal, ID, subject, target, number, comment, choice=0):
		canTrigger = True
		if self.entity.Game.Hand_Deck.hands[self.entity.ID] != [] or self.entity.Game.Hand_Deck.decks[self.entity.ID] != [] or self.entity.Game.minionsonBoard(self.entity.ID) != []:
			canTrigger = False
			
		if canTrigger:
			print("Deathrattle: Destroy the enemy hero triggers")
			#需要确定如果对方英雄在标记为死亡之后被替换，即（拉格纳罗斯），是否会抹除这个效果
			self.entity.Game.heroes[3-self.entity.ID].dead = True
			
"""Druid cards"""
class BiologyProject(Spell):
	Class, name = "Druid", "Biology Project"
	needTarget, mana = False, 1
	index = "Boomsday-Druid-1-Spell-Biology Project"
	description = "Each player gains 2 Mana Crystals"
	
	def whenEffective(self, target=None, comment="", choice=0):
		print("Biology Project is cast and gives each player two mana crystals.")
		self.Game.ManaHandler.gainManaCrystal(2, 1)
		self.Game.ManaHandler.gainManaCrystal(2, 2)
		return None
		
		
class FloopsGloriousGloop(Spell):
	Class, name = "Druid", "Floop's Glorious Gloop"
	needTarget, mana = False, 1
	index = "Boomsday-Druid-1-Spell-Floop's Glorious Gloop-Legendary"
	description = "Whenever a minion dies this turn, gain 1 Mana Crystal this turn only"
	
	def whenEffective(self, target=None, comment="", choice=0):
		print("Floop's Glorious Gloop is cast. Every minion that dies this turn will give the player a mana crystal for this turn.")
		trigger = Trigger_FloopsGloriousGloop(self)
		trigger.connect()
		return None
		
class Trigger_FloopsGloriousGloop(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionDies", "TurnEnds"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		if signal == "TurnEnds":
			return self.entity.onBoard and ID == self.entity.ID
		else:
			return True
			
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		if signal == "MinionDies":
			print("A minion dies and Floop's Glorious Gloop gives player a Mana Crystal this turn.")
			self.entity.Game.ManaHandler.manas[self.ID] += 1
			self.entity.Game.ManaHandler.manas[self.ID] = min(10, self.Game.ManaHandler.manas[self.ID])
		else: #signal == "TurnEnds"
			extractfrom((self, "MinionDies"), self.entity.Game.triggersonBoard[self.entity.ID])
			extractfrom((self, "TurnEnds"), self.entity.Game.triggersonBoard[self.entity.ID])
			
			
class Dendrologist(Minion):
	Class, race, name = "Druid", "", "Dendrologist"
	mana, attack, health = 2, 2, 3
	index = "Boomsday-Druid-2-2-3-Minion-None-Dendrologist-Battlecry"
	needTarget, keyWord, description = False, "", "Battlecry: If you control a Treant, Discover a spell"
	
	def randomorDiscover(self):
		for minion in self.Game.minionsonBoard(self.ID):
			if minion.name == "Treant":
				return "Discover"
				
		return "No RNG"
		
	def whenEffective(self, target=None, comment="", choice=0):
		controlTreant = False
		for minion in self.Game.minionsonBoard(self.ID):
			if minion.name == "Treant":
				controlTreant = True
				break
		if controlTreant:
			Class = self.Game.heroes[self.ID].Class
			spells = list(self.Game.ClassCards[Class].values())
			if comment == "InvokedbyOthers":
				print("Dendrologist's battlecry adds a random %s spell to player's hand."%Class)
				self.Game.Hand_Deck.addCardtoHand(np.random.choice(spells), self.ID, "CreateUsingType")
			else:
				spells = np.random.choice(spells, 3, replace=False)
				self.Game.options = [spell(self.Game, self.ID) for spell in spells]
				self.Game.DiscoverHandler.startDiscover(self)
				
		return self, None
		
	def discoverDecided(self, option):
		print("Spell %s is put into player's hand."%option.name)
		self.Game.Hand_Deck.addCardtoHand(option, self.ID)
		
		
class Landscaping(Spell):
	Class, name = "Druid", "Landscaping"
	needTarget, mana = False, 3
	index = "Boomsday-Druid-3-Spell-Landscaping"
	description = "Summon two 2/2 Treants"
	
	def whenEffective(self, target=None, comment="", choice=0):
		print("Landscaping is cast and summons two 2/2 Treants.")
		self.Game.summonMinion([Treant_Boomsday(self.Game, self.ID) for i in range(2)], (-1, "totheRightEnd"), self.ID)
		return None
		
class Treant_Boomsday(Minion):
	Class, race, name = "Druid", "", "Treant"
	mana, attack, health = 2, 2, 2
	index = "Boomsday-Druid-2-2-2-Minion-None-Treant-Uncollectible"
	needTarget, keyWord, description = False, "", ""
	
class FlobbidinousFloop(Minion):
	Class, race, name = "Druid", "", "Flobbidinous Floop"
	mana, attack, health = 4, 3, 4
	index = "Boomsday-Druid-4-3-4-Minion-None-Flobbidinous Floop-Legendary"
	needTarget, keyWord, description = False, "", "While in your hand, this is a 3/4 copy of the last minion you played"
	
	
class JuicyPsychmelon(Spell):
	Class, name = "Druid", "Juicy Psychmelon"
	needTarget, mana = False, 4
	index = "Boomsday-Druid-4-Spell-Juicy Psychmelon"
	description = "Draw a 7, 8, 9 and 10-Cost minion from your deck"
	
	def whenEffective(self, target=None, comment="", choice=0):
		print("Juicy Psychmelon is cast and lets player draw a 7, 8, 9 and 10 cost minion from deck.")
		minionsinDeck = {7:[], 8:[], 9:[], 10:[]}
		for card in self.Game.Hand_Deck.decks[self.ID]:
			if card.cardType == "Minion" and card.mana_set > 6 and card.mana_set < 11:
				minionsinDeck[card.mana_set].append(card)
				
		for cost in minionsinDeck.keys():
			if minionsinDeck[cost] != []:
				self.Game.Hand_Deck.drawCard(self.ID, np.random.choice(minionsinDeck[cost]))
		return None
		
		
class TendingTauren(Minion):
	Class, race, name = "Druid", "", "Tending Tauren"
	mana, attack, health = 6, 3, 4
	index = "Boomsday-Druid-6-3-4-Minion-None-Tending Tauren-Choose One"
	needTarget, keyWord, description = False, "", "Choose One- Give your other minions +1/+1; or Summon two 2/2 Treants"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.chooseOne = 1
		self.options = [OldGrowth_Option(), NewGrowth_Option(self)]
		
	def whenEffective(self, target=None, comment="", choice=0):
		if choice == "ChooseBoth" or choice == 1:
			print("Tending Tauren summons two 2/2 Treants.")
			pos = (self.position, "leftandRight") if self.onBoard else (-1, "totheRightEnd")
			self.Game.summonMinion([Treant_Boomsday(self.Game, self.ID) for i in range(2)], pos, self.ID)
		if choice == "ChooseBoth" or choice == 0:
			print("Tending Tauren gives all other friendly minions +1/+1.")
			for minion in self.Game.minionsonBoard(self.ID):
				if minion != self:
					minion.buffDebuff(1, 1)
		return self, None
		
class OldGrowth_Option_Option:
	def __init__(self):
		self.name = "Old Growth"
		self.description = "Other minions +1/+1"
		
	def available(self):
		return True
		
class NewGrowth_Option:
	def __init__(self, minion):
		self.minion = minion
		self.name = "New Growth"
		self.description = "2 Treants"
		
	def available(self):
		return self.minion.Game.spaceonBoard(self.minion.ID) > 0
		
		
class DreampetalFlorist(Minion):
	Class, race, name = "Druid", "", "Dreampetal Florist"
	mana, attack, health = 7, 4, 4
	index = "Boomsday-Druid-7-4-4-Minion-None-Dreampetal Florist"
	needTarget, keyWord, description = False, "", "At the end of your turn, reduced the Cost of a random minion in your hand by (7)"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_DreampetalFlorist(self)]
		
class Trigger_DreampetalFlorist(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["TurnEnds"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		minionsinHand = []
		for card in self.entity.Game.Hand_Deck.hands[self.entity.ID]:
			if card.cardType == "Minion":
				minionsinHand.append(card)
				
		print("At the end of turn, %s gives friendly minion %s +1 attack"%(self.entity.name, target.name))
		if minionsinHand != []:
			minion = np.random.choice(minionsinHand)
			minion.mana_set -= 7
			self.entity.Game.ManaHandler.calcMana_Single(minion)
			
			
class GloopSprayer(Minion):
	Class, race, name = "Druid", "", "Gloop Sprayer"
	mana, attack, health = 7, 4, 4
	index = "Boomsday-Druid-7-4-4-Minion-None-Gloop Sprayer-Battlecry"
	needTarget, keyWord, description = False, "", "Battlecry: Summon a copy of each adjacent minion"
	
	def whenEffective(self, target=None, comment="", choice=0):
		if self.onBoard:
			adjacentMinions, distribution = self.Game.findAdjacentMinions(self)
			print("Gloop Sprayer's battlecry summons a copy of each adjacent minion.")
			if distribution == "Minions on Both Sides":
				minion_left = adjacentMinions[0].selfCopy(self.ID)
				minion_right = adjacentMinions[1].selfCopy(self.ID)
				self.Game.summonMinion([minion_right, minion_left], (self.position, "leftandRight", 2), self.ID)
			elif distribution == "Minions Only on the Left":
				minion_left = adjacentMinions[0].selfCopy(self.ID)
				self.Game.summonMinion(minion_left, self.position, self.ID)
			elif distribution == "Minions Only on the Right":
				minion_right = adjacentMinions[0].selfCopy(self.ID)
				self.Game.summonMinion(minion_right, self.position+1, self.ID)
		return self, None
		
		
class Mulchmuncher(Minion):
	Class, race, name = "Druid", "Mech", "Mulchmuncher"
	mana, attack, health = 9, 8, 8
	index = "Boomsday-Druid-9-8-8-Minion-Mech-Mulchmuncher-Rush"
	needTarget, keyWord, description = False, "Rush", "Rush. Costs (1) for each friendly Treant that died this game"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersinHand = [Trigger_Mulchmuncher(self)]
		
	def selfManaChange(self):
		numYourTreantsDiedThisGame = 0
		for index in self.Game.CounterHandler.minionsDiedThisGame[self.ID]:
			if "-Treant" in index:
				numYourTreantsDiedThisGame += 1
				
		self.mana -= numYourTreantsDiedThisGame
		self.mana = max(self.mana, 0)
		if self.keyWords["Echo"] > 0 and self.mana < 1:
			self.mana = 1
			
class Trigger_Mulchmuncher(TriggerinHand):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionDies"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.inHand and target.name == "Treant"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.Game.ManaHandler.calcMana_Single(self.entity)
		
		
"""Hunter cards"""
class SecretPlan(Spell):
	Class, name = "Hunter", "Secret Plan"
	needTarget, mana = False, 1
	index = "Boomsday-Hunter-1-Spell-Secret Plan"
	description = "Discover a Secret"
	
	def randomorDiscover(self):
		return "Discover"
		
	def whenEffective(self, target=None, comment="", choice=0):
		Class = self.Game.heroes[self.ID].Class
		secrets = []
		if Class not in ["Mage", "Paladin", "Hunter"]:
			Class = "Hunter"
			
		for key, value in self.Game.ClassCards[Class].items():
			if "--Secret" in key:
				secrets.append(value)
				
		if comment == "InvokedbyOthers":
			print("Secret Plan is cast and adds random %s Secret into player's hand."%Class)
			self.Game.Hand_Deck.addCardtoHand(np.random.choice(secrets), self.ID, "CreateUsingType")
		else:
			print("Secret Plan is cast and lets player discover a %s secret."%Class)
			secrets = np.random.choice(secrets, 3, replace=False)
			self.Game.options = [secret(self.Game, self.ID) for secret in secrets]
			self.Game.DiscoverHandler.startDiscover(self)
			
		return None
		
	def discoverDecided(self, option):
		print("Secret ", option.name, " is put into player's hand.")
		self.Game.Hand_Deck.addCardtoHand(option, self.ID)
		
		
class BombToss(Spell):
	Class, name = "Hunter", "Bomb Toss"
	needTarget, mana = True, 2
	index = "Boomsday-Hunter-2-Spell-Bomb Toss"
	description = "Deal 2 damage. Summon a 0/2 Goblin Bomb"
	
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			damage = (2 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			print("Bomb Toss is cast and deals %d damage to %s. Then summons a 0/2 Goblin Bomb."%(damage, target.name))
			self.dealsDamage(target, damage)
			self.Game.summonMinion(GoblinBomb(self.Game, self.ID), -1, self.ID)
		return target
		
		
class Venomizer(Minion):
	Class, race, name = "Hunter", "Mech", "Venomizer"
	mana, attack, health = 2, 2, 2
	index = "Boomsday-Hunter-2-2-2-Minion-Mech-Venomizer-Poisonous-Magnetic"
	needTarget, keyWord, description = False, "Poisonous", "Magnetic, Poisonous"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.magnetic = 1
		
class CybertechChip(Spell):
	Class, name = "Hunter", "Cybertech Chip"
	needTarget, mana = False, 2
	index = "Boomsday-Hunter-2-Spell-Cybertech Chip"
	description = "Give your minions 'Deathrattle: Add a random Mech to your hand'"
	
	def available(self):
		return self.Game.minionsonBoard(self.ID) != []
		
	def whenEffective(self, target=None, comment="", choice=0):
		print("Cybertech Chip is cast and gives all friendly minions 'Deathrattle: Add a random Mech to player's hand.'")
		for minion in self.Game.minionsonBoard(self.ID):
			trigger = AddaRandomMechtoHand(minion)
			minion.deathrattles.append(trigger)
			trigger.connect()
		return None
		
class AddaRandomMechtoHand(Deathrattle_Minion):
	def trigger(self, signal, ID, subject, target, number, comment, choice=0):
		mechs = list(self.Game.MinionswithRace["Mech"].values())
		print("Deathrattle: Add a random Mech to your hand triggers")
		self.entity.Game.Hand_Deck.addCardtoHand(np.random.choice(mechs), self.entity.ID, "CreateUsingType")
		
		
class FireworksTech(Minion):
	Class, race, name = "Hunter", "", "Fireworks Teck"
	mana, attack, health = 2, 2, 1
	index = "Boomsday-Hunter-2-2-1-Minion-None-Fireworks Tech-Battlecry"
	needTarget, keyWord, description = True, "", "Battlecry: Give a friendly Mech +1/+1. If it has Deathrattle, trigger it"
	
	def targetExists(self, choice=0):
		return self.selectableFriendlyMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and "Mech" in target.race and target.ID == self.ID and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			print("Fireworks Tech's battlecry gives friendly Mech %s +1/+1 and triggers its deathrattle if applicable."%target.name)
			target.buffDebuff(1, 1)
			for trigger in target.deathrattles:
				trigger.trigger("DeathrattleTriggers", self.ID, None, minion, minion.attack, "")
		return self, target
		
		
class GoblinPrank(Spell):
	Class, name = "Hunter", "Goblin Prank"
	needTarget, mana = True, 2
	index = "Boomsday-Hunter-2-Spell-Goblin Prank"
	description = "Give a friendly minion +3/+3 and Rush. It dies at end of turn"
	
	def available(self):
		return self.selectableFriendlyMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.ID == self.ID and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			print("Goblin Prank is cast on target %s. It gains +3/+3 and dies at the end of turn."%target.name)
			target.buffDebuff(3, 3)
			target.getsKeyword("Rush")
			if target.onBoard:
				trigger = Trigger_GoblinPrank(target)
				trigger.connect()
				target.triggersonBoard.append(trigger)
		return target
		
class Trigger_GoblinPrank(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["TurnEnds"])
		self.temp = True
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard #Even if the current turn is not the minion's owner's turn
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("At the end of turn, minion %s affected by Goblin Prank dies."%self.entity.name)
		self.entity.dead = True
		
		
class SpiderBomb(Minion):
	Class, race, name = "Hunter", "Mech", "Spider Bomb"
	mana, attack, health = 3, 2, 2
	index = "Boomsday-Hunter-3-2-2-Minion-Mech-Spider Bomb-Magnetic-Deathrattle"
	needTarget, keyWord, description = False, "", "Magnetic. Deathrattle: Destroy a random enemy minion"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.magnetic = 1
		self.deathrattles = [DestroyaRandomEnemyMinion(self)]
		
class DestroyaRandomEnemyMinion(Deathrattle_Minion):
	def trigger(self, signal, ID, subject, target, number, comment, choice=0):
		enemyMinions = []
		for obj in self.entity.Game.minionsonBoard(3-self.entity.ID):
			if obj.health > 0 and obj.dead == False:
				enemyMinions.append(obj)
				
		if enemyMinions != []:
			minion = np.random.choice(enemyMinions)
			print("Deathrattle: Destroy a random enemy minion triggers and destroys", minion.name)
			minion.dead = True
			
			
class Necromechanic(Minion):
	Class, race, name = "Hunter", "", "Necromechanic"
	mana, attack, health = 4, 3, 6
	index = "Boomsday-Hunter-4-3-6-Minion-None-Necromechanic"
	needTarget, keyWord, description = False, "", "Your Deathrattles trigger twice"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.appearResponse = [self.activateAura]
		self.silenceResponse = [self.removeEffect]
		self.disappearResponse = [self.deactivateAura]
		
	def activateAura(self):
		print("Necromechanic appears and deathrattles will trigger twice.")
		self.Game.playerStatus[self.ID]["Deathrattle Trigger Twice"] += 1
		self.Game.playerStatus[self.ID]["Weapon Deathrattle Trigger Twice"] += 1
	#Necromancer has to be alive to make deathrattles trigger twice.			
	def deactivateAura(self):
		print("Necromechanic no longer makes deathrattle trigger twice.")
		if self.Game.playerStatus[self.ID]["Deathrattle Trigger Twice"] > 0:
			self.Game.playerStatus[self.ID]["Deathrattle Trigger Twice"] -= 1
		if self.Game.playerStatus[self.ID]["Weapon Deathrattle Trigger Twice"] > 0:
			self.Game.playerStatus[self.ID]["Weapon Deathrattle Trigger Twice"] -= 1
			
			
class BoommasterFlark(Minion):
	Class, race, name = "Hunter", "", "Boommaster Flark"
	mana, attack, health = 7, 5, 5
	index = "Boomsday-Hunter-7-5-5-Minion-None-Boommaster Flark-Battlecry-Legendary"
	needTarget, keyWord, description = False, "", "Battlecry: Summon four 0/2 Goblin Bombs"
	
	def whenEffective(self, target=None, comment="", choice=0):
		print("Boommaster Flark's battlecry summons four 0/2 Goblin Bombs.")
		pos = (self.position, "leftandRight") if self.onBoard else (-1, "totheRightEnd")
		self.Game.summonMinion([GoblinBomb(self.Game, self.ID) for i in range(4)], pos, self.ID)
		return self, None
		
		
class FlarksBoomZooka(Spell):
	Class, name = "Hunter", "Flark's Boom-Zooka"
	needTarget, mana = False, 7
	index = "Boomsday-Hunter-7-Spell-Flark's Boom-Zooka-Legendary"
	description = "Summon 3 minions from your deck. They attack enemy minions, then die"
	
	#def whenEffective(self, target=None, comment="", choice=0):
	#	print("Flark's Boom-Zooka is cast and \and summons 3 minions from deck to attack the enemy minions. After that, they die.")
	#	minionsinDeck = []
	#	for card in self.Game.Hand_Deck.decks[self.ID]:
	#		if card.cardType == "Minion":
	#			minionsinDeck.append(card)
	#			
	#	numMinionstoSummon = min(3, self.Game.spaceonBoard(self.ID), len(minionsinDeck))
	#	if numMinionstoSummon > 0:
	#		minions = np.random.choice(minionsinDeck, numMinionstoSummon, replace=False)
	#		self.Game.Hand_Deck.extractfromDeck(minions)
	#		self.Game.summonMinion(minions, -1 if numMinionstoSummon == 1 else (-1, "totheRightEnd", numMinionstoSummon), self.ID)
	#		for minion in minions:
	#			target = self.returnanEnemyMiniontoAttack()
	#			if target != None:
	#				self.Game.battleRequest(minion, target, False, True)
	#			else:
	#				break
	#				
	#		for minion in minions:
	#			minion.dead = True
	#	return None
	
	def returnanEnemyMiniontoAttack(self):
		livingEnemyMinions = []
		for minion in self.Game.minions[3-self.ID]:
			if minion.cardType == "Minion" and minion.health > 0 and minion.dead == False and minion.onBoard:
				livingEnemyMinions.append(minion)
				
		if livingEnemyMinions != []:
			return np.random.choice(livingEnemyMinions)
		else:
			return None
			
#class Trigger_FlarksBoomZooka(TriggeronBoard):
#	def __init__(self, entity):
#		self.blank_init(entity, ["SpellBeenCast", "TurnEnds"])
#		
#	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
#		return subject.ID == 1 if signal == "SpellBeenCast" else return True
#		
#	def effect(self, signal, ID, subject, target, number, comment, choice=0):
#		
		
"""Mage cards"""
class ShootingStar(Spell):
	Class, name = "Mage", "Shooting Star"
	needTarget, mana = True, 1
	index = "Boomsday-Mage-1-Spell-Shooting Star"
	description = "Deal 1 damage to a minion and the minions next to it"
	
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			damage = (1 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			if target.onBoard and self.Game.findAdjacentMinions(target)[0] != []:
				print("Shooting Star is cast and deals %d damage to minion %s and the one next to it."%(damage, target.name))
				targets = [target] + self.Game.findAdjacentMinions(target)[0]
				self.dealsAOE(targets, [damage for minion in targets])
			else:
				print("Shooting Star is cast and deals %d damage to minion"%damage, target.name)
				self.dealsDamage(target, damage)
		return target
		
		
class AstralRift(Spell):
	Class, name = "Mage", "Astral Rift"
	needTarget, mana = False, 2
	index = "Boomsday-Mage-2-Spell-Astral Rift"
	description = "Add two random minions to your hand"
	
	def whenEffective(self, target=None, comment="", choice=0):
		print("Astral Rift is cast and adds two random minions to player's hand.")
		if self.Game.Hand_Deck.handNotFull(self.ID):
			minions = []
			for cost in self.Game.MinionswithCertainCost.keys():
				minions.append(list(self.Game.MinionswithCertainCost[cost].values()))
				
			minions = np.random.choice(minions, 2, replace=True)
			self.Game.Hand_Deck.addCardtoHand(minions, self.ID, "CreateUsingType")
		return None
		
#After the CelestialEmissary is played, the next spell cancelled by 
#Counterspell won't waste the spell damage, the following spell still has spell damage.
#Yogg-Saron's Puzzle box will waste CelestialEmissary's spell damage.
#With Zentimo, the spell is boosted by spell damage  for each target.
#The first spell cast by Wonder Deck will use up the Spell Damage.
#Playing Celestial and then 西风灯神， only the first spell on the original target will be boosted.
#Playing 灯神 and then Celestial, the spell cast on 灯神 is still boosted.
#There is some point where the spell sends out the signal, notifying the Celestial and 灯神, that they need to repson.
#If 灯神 responds first, the spell is copied and preserves the spell damage boost.
#If Celestial responds first, the spell damage boost is cancelled before 灯神 can respond.

#For Zentimo and Celestial, the spells on the targets will always be boosted.
#For Stormsurge and Celestial, the two times Frostbolt is cast, it does 5x2 damage.
#结论，除了风潮和泽蒂摩的重复、群体指向法术之外，其他法术都会用掉星界密使的法强加成
class CelestialEmissary(Minion):
	Class, race, name = "Mage", "Elemental", "Celestial Emissary"
	mana, attack, health = 2, 2, 1
	index = "Boomsday-Mage-2-2-1-Minion-Elemental-Celestial Emissary-Battlecry"
	needTarget, keyWord, description = False, "", "Battlecry: Your next spell this turn ahs Spell Damage +2"
	
	def whenEffective(self, target=None, comment="", choice=0):
		print("Celestial Emissary's battlecry player's next spell this turn has Spell Damage +2.")
		self.Game.playerStatus[self.ID]["Spell Damage"] += 2
		trigger = Trigger_CelestialEmissary(self)
		trigger.ID = self.ID
		trigger.connect()
		return self, None
		
class Trigger_CelestialEmissary(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["SpellBeenCast", "TurnEnds"])
		self.ID = 1
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		if signal == "SpellBeenCast":
			return subject.ID == self.ID
		return True
		
	def connect(self):
		for signal in self.signals:
			self.entity.Game.triggersonBoard[self.ID].append((self, signal))
			
	def disconnect(self):
		for signal in self.signals:
			extractfrom((self, signal), self.entity.Game.triggersonBoard[self.ID])
			
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		if signal == "SpellBeenCast":
			print("Spell %s is played/cast and Celestial Emissary's Spell Damage +2 expires.")
		self.Game.playerStatus[self.ID]["Spell Damage"] -= 2
		self.Game.playerStatus[self.ID]["Spell Damage"] = max(0, self.Game.playerStatus[self.ID]["Spell Damage"])
		extractfrom((self, "SpellBeenCast"), self.entity.Game.triggersonBoard[self.ID])
		extractfrom((self, "TurnEnds"), self.entity.Game.triggersonBoard[self.ID])
		
		
class ResearchProject(Spell):
	Class, name = "Mage", "Research Project"
	needTarget, mana = False, 2
	index = "Boomsday-Mage-2-Spell-Research Project"
	description = "Each player draws two cards"
	
	def whenEffective(self, target=None, comment="", choice=0):
		print("Research Project is cast and each player draws two cards.")
		self.Game.Hand_Deck.drawCard(self.ID)
		self.Game.Hand_Deck.drawCard(self.ID)
		self.Game.Hand_Deck.drawCard(3-self.ID)
		self.Game.Hand_Deck.drawCard(3-self.ID)
		return None
		
		
class StargazerLuna(Minion):
	Class, race, name = "Mage", "", "Stargazer Luna"
	mana, attack, health = 3, 2, 4
	index = "Boomsday-Mage-3-2-4-Minion-None-Stargazer Luna-Legendary"
	needTarget, keyWord, description = False, "", "Spell Damage +2"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_StargazerLuna(self)]
		
class Trigger_StargazerLuna(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionBeenPlayed", "SpellBeenPlayed", "WeaponBeenPlayed", "HeroCardBeenPlayed"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		#Technically, minion has to disappear before dies. But just in case.
		return self.entity.onBoard and subject.ID == self.entity.ID and subject != self.entity and comment == "CardPlayedistheRightmostinHand"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("After player plays the rightmost card in hand, Stargazer Luna lets player draw a card.")
		self.entity.Game.Hand_Deck.drawCard(self.entity.ID)
		
		
class UnexpectedResults(Spell):
	Class, name = "Mage", "Unexpected Results"
	needTarget, mana = False, 3
	index = "Boomsday-Mage-3-Spell-Unexpected Results"
	description = "Summon two random 2-Cost minions (improved by Spell damage)"
	
	def available(self):
		return self.Game.spaceonBoard(self.ID) > 0
		
	def whenEffective(self, target=None, comment="", choice=0):
		cost = 2 + self.countSpellDamage()
		print("Unexpected Results is cast and summons two random %d-cost minions."%cost)
		#假设法术伤害过高，超出了费用范围，则取最高的可选费用
		while True:
			if cost not in self.Game.MinionswithCertainCost.keys():
				cost -= 1
			else:
				break
				
		minions = list(self.Game.MinionswithCertainCost[cost].values())
		minion = np.random.choice(minions, 2, replace=True)
		self.Game.summonMinion([minion(self.Game, self.ID) for minion in minions], (-1, "totheRightEnd"), self.ID)
		return None
		
		
class CosmicAnomaly(Minion):
	Class, race, name = "Mage", "Elemental", "Cosmic Anomaly"
	mana, attack, health = 4, 4, 3
	index = "Boomsday-Mage-4-4-3-Minion-Elemental-Cosmic Anomaly-Spell Damage"
	needTarget, keyWord, description = False, "", "Spell Damage +2"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.keyWords["Spell Damage"] = 2
		
		
class Meteorologist(Minion):
	Class, race, name = "Mage", "", "Meteorologist"
	mana, attack, health = 6, 3, 3
	index = "Boomsday-Mage-6-3-3-Minion-None-Meteorologist-Battlecry"
	needTarget, keyWord, description = False, "", "Battlecry: For each card in your hand, deal 1 damage to a random enemy"
	
	def whenEffective(self, target=None, comment="", choice=0):
		handSize = len(self.Game.Hand_Deck.hands[self.ID])
		if handSize > 0:
			print("Meteorologist's battlecry deals 1 damage to a random enemy for each card in hand.")
			for i in range(handSize):
				targets = [self.Game.heroes[3-self.ID]]
				for minion in self.Game.minionsonBoard(3-self.ID):
					if minion.health > 0 and minion.dead == False:
						targets.append(minion)
						
				self.dealsDamage(np.random.choice(targets), 1)
		return self, None
		
		
class Astromancer(Minion):
	Class, race, name = "Mage", "", "Astromancer"
	mana, attack, health = 7, 5, 5
	index = "Boomsday-Mage-7-5-5-Minion-None-Astromancer-Battlecry"
	needTarget, keyWord, description = False, "", "Battlecry: Summon a random minion with Cost equal to your hand size"
	
	def whenEffective(self, target=None, comment="", choice=0):
		handSize = len(self.Game.Hand_Deck.hands[self.ID])
		minions = list(self.Game.MinionswithCertainCost[handSize].values())
		print("Astromancer's battlecry summons a minion with cost equal to player's hand size.")
		self.Game.summonMinion(np.random.choice(minions)(self.Game, self.ID), self.position+1, self.ID)
		return self, None
		
		
class LunasPocketGalaxy(Spell):
	Class, name = "Mage", "Luna's Pocket Galaxy"
	needTarget, mana = False, 7
	index = "Boomsday-Mage-7-Spell-Luna's Pocket Galaxy-Legendary"
	description = "Change the Cost of minions in your deck to (1)"
	
	def whenEffective(self, target=None, comment="", choice=0):
		print("Luna's Pocket Galaxy is cast and turns the cost of all minions in player's deck to 1.")
		for card in self.Game.Hand_Deck.decks[self.ID]:
			if card.cardType == "Minion":
				card.mana_set = 1
				card.mana = 1
		return None
		
"""Paladin cards"""
class AutodefenseMatrix(Secret):
	Class, name = "Paladin", "Autodefense Matrix"
	needTarget, mana = False, 1
	index = "Boomsday-Paladin-1-Spell-Autodefense Matrix--Secret"
	description = "When one of your minions is attacked, give it Divine Shield"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_AutodefenseMatrix(self)]
		
class Trigger_AutodefenseMatrix(SecretTrigger):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionAttacksMinion", "HeroAttacksMinion"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		#The target has to a friendly minion and there is space on board to summon minions.
		return self.entity.ID != self.entity.Game.turn and target.cardType == "Minion" and target.ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("When a friendly minion %s is attacked, Secret Autodefense Matrix is triggered and gives it Divine Shield."%target.name)
		target.getsKeyword("Divine Shield")
		
		
class Crystology(Spell):
	Class, name = "Paladin", "Crystology"
	needTarget, mana = False, 1
	index = "Boomsday-Paladin-1-Spell-Crystology"
	description = "Draw two 1-Attack minions from your deck"
	
	def whenEffective(self, target=None, comment="", choice=0):
		print("Crystology is cast and player draws two 1-attack minions from deck.")
		oneAttackMinions = []
		for card in self.Game.Hand_Deck.decks[self.ID]:
			if card.cardType == "Minion" and card.attack == 1:
				oneAttackMinions.append(card)
				
		if len(oneAttackMinions) > 1:
			minions = np.random.choice(oneAttackMinions, 2, replace=False)
			self.Game.Hand_Deck.drawCard(self.ID, minions)
		elif len(oneAttackMinions) == 1:
			self.Game.Hand_Deck.drawCard(self.ID, oneAttackMinions[0])
			
		return None
		
		
class GlowTron(Minion):
	Class, race, name = "Paladin", "Mech", "Glow-Tron"
	mana, attack, health = 1, 1, 3
	index = "Boomsday-Paladin-1-1-3-Minion-Mech-Glow-Tron-Magnetic"
	needTarget, keyWord, description = False, "", "Magnetic"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.magnetic = 1
		
		
class CrystalsmithKangor(Minion):
	Class, race, name = "Paladin", "", "Crystalsmith Kangor"
	mana, attack, health = 2, 1, 2
	index = "Boomsday-Paladin-2-1-2-Minion-None-Crystalsmith Kangor-Divine Shield-Lifesteal-Legendary"
	needTarget, keyWord, description = False, "Divine Shield,Lifesteal", "Divine Shield, Lifesteal. Your healing is doubled"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.marks["Double Heal"] = 1
		
		
class AnnoyoModule(Minion):
	Class, race, name = "Paladin", "Mech", "Annoy-o-Module"
	mana, attack, health = 4, 2, 4
	index = "Boomsday-Paladin-4-2-4-Minion-Mech-Annoy-o-Module-Taunt-Divine Shield-Magnetic"
	needTarget, keyWord, description = False, "Divine Shield,Taunt", "Magnetic, Divine Shield, Taunt"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.magnetic = 1
	
class PrismaticLens(Spell):
	Class, name = "Paladin", "Prismatic Lens"
	needTarget, mana = False, 4
	index = "Boomsday-Paladin-4-Spell-Prismatic Lens"
	description = "Draw a minion and spell from your deck. Swap their Costs"
	
	def whenEffective(self, target=None, comment="", choice=0):
		print("Prismatic Lens is cast and player draws a minion and a spell from deck. Then their costs are swapped.")
		minionsinDeck = []
		spellsinDeck = []
		for card in self.Game.Hand_Deck.decks[self.ID]:
			if card.cardType == "Minion":
				minionsinDeck.append(card)
			elif card.cardType == "Spell":
				spellsinDeck.append(card)
		#What if one of the cards is milled. Assume the mana won't swap then.
		minion = None
		if minionsinDeck != []:
			minion = self.Game.Hand_Deck.drawCard(self.ID, np.random.choice(minionsinDeck))[0]
		spell = None
		if spellsinDeck != []:
			spell = self.Game.Hand_Deck.drawCard(self.ID, np.random.choice(spellsinDeck))[0]
			
		if minion != None and spell != None:
			temp = spell.mana_set
			spell.mana_set = minion.mana_set
			minion.mana_set = temp
		return None
		
		
class GlowstoneTechnician(Minion):
	Class, race, name = "Paladin", "", "Glowstone Technician"
	mana, attack, health = 5, 3, 4
	index = "Boomsday-Paladin-5-3-4-Minion-None-Glowstone Technician-Battlecry"
	needTarget, keyWord, description = False, "", "Battlecry: Give all minions in your hand +2/+2"
	
	def whenEffective(self, target=None, comment="", choice=0):
		print("Glowstone Technician's battlecry gives all minion in player's hand +2/+2")
		for card in self.Game.Hand_Deck.hands[self.ID]:
			if card.cardType == "Minion":
				card.buffDebuff(2, 2)
		return self, None
		
		
class MechanoEgg(Minion):
	Class, race, name = "Paladin", "Mech", "Mechano-Egg"
	mana, attack, health = 5, 0, 5
	index = "Boomsday-Paladin-5-0-5-Minion-Mech-Mechano-Egg-Deathrattle"
	needTarget, keyWord, description = False, "", "Deathrattle: Summon a 8/8 Robosaur"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [SummonaRobosaur(self)]
		
class SummonaRobosaur(Deathrattle_Minion):
	def trigger(self, signal, ID, subject, target, number, comment, choice=0):	
		print("Deathrattle: Summon an 8/8 Robosaur triggers")
		self.entity.Game.summonMinion(Robosaur(self.entity.Game, self.entity.ID), self.entity.position+1, self.entity.ID)
		
class Robosaur(Minion):
	Class, race, name = "Paladin", "Mech", "Robosaur"
	mana, attack, health = 8, 8, 8
	index = "Boomsday-Paladin-8-8-8-Minion-Mech-Robosaur-Uncollectible"
	needTarget, keyWord, description = False, "", ""
	
	
class ShrinkRay(Minion):
	Class, name = "Paladin", "Shrink Ray"
	needTarget, mana = False, 5
	index = "Boomsday-Paladin-5-Spell-Shrink Ray"
	description = "Set the Attack and Health of all minions to 1/1"
	
	def whenEffective(self, target=None, comment="", choice=0):
		print("Shrink Ray is cast and sets all minions on board to 1/1.")
		for minion in self.Game.minionsonBoard(1) + self.Game.minionsonBoard(2):
			minion.statReset(1, 1)
		return None
		
		
class KangorsEndlessArmy(Spell):
	Class, name = "Paladin", "Kangor's Endless Army"
	needTarget, mana = False, 7
	index = "Boomsday-Paladin-7-Spell-Kangor's Endless Army-Legendary"
	description = "Resurrect 3 friendly Mechs. They keep any Magnetic upgrades"
	
	def whenEffective(self, target=None, comment="", choice=0):
		print("Kangor's Endless Army is cast and summons 3 friendly Mechs. They keep any magnetic upgrades.")
		numDeadMechs = len(self.Game.CounterHandler.mechsDiedThisGame[self.ID])
		print("The mechs that died are", self.Game.CounterHandler.mechsDiedThisGame[self.ID])
		numSummon = min(3, numDeadMechs, self.Game.spaceonBoard(self.ID))
		if numSummon > 0:
			indices = random.sample(range(numDeadMechs), numSummon)
			mechs = []
			for i in indices:
				mechs.append(self.Game.CounterHandler.mechsDiedThisGame[self.ID][i])
			mechstoSummon = []
			for mech_History in mechs: #mechandUpgrade: [index, (index, attack, health)]
				baseMech, upgrades = mech_History[0], mech_History[1]
				baseMech = self.Game.cardPool[baseMech](self.Game, self.ID)
				for key, value in upgrades["Keywords"].items():
					baseMech.keyWords[key] += value
				for key, value in upgrades["Marks"].items():
					baseMech.marks[key] += value
				for deathrattle_Class in upgrades["Deathrattles"]:
					baseMech.deathrattles.append(deathrattle_Class(baseMech))
				for trigger_Class in upgrades["Triggers"]:
					baseMech.triggersonBoard.append(trigger_Class(baseMech))
					
				baseMech.buffDebuff(upgrades["AttackGain"], upgrades["HealthGain"])
				baseMech.history["Magnetic Upgrades"] = copy.deepcopy(upgrades)
				mechstoSummon.append(baseMech)
				
			self.Game.summonMinion(mechstoSummon, (-1, "totheRightEnd"), self.ID)
			
		return None
		
"""Priest cards"""
class TopsyTurvy(Spell):
	Class, name = "Priest", "Topsy Turvy"
	needTarget, mana = True, 0
	index = "Boomsday-Priest-0-Spell-Topsy Turvy"
	description = "Swap a minion's Attack and Health"
	
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			print("Topsy Turvy is cast and swaps the attack and health of minion ", target.name)
			target.statReset(target.health, target.attack)
		return target
		
class CloningDevice(Spell):
	Class, name = "Priest", "Cloning Device"
	needTarget, mana = False, 1
	index = "Boomsday-Priest-1-Spell-Cloning Device"
	description = "Discover a copy of a minion in your opponent's deck"
	
	def whenEffective(self, target=None, comment="", choice=0):
		minionsinDeck = []
		for card in self.Game.Hand_Deck.decks[3-self.ID]:
			if card.cardType == "Minion":
				minionsinDeck.append(card)
				
		if minionsinDeck != [] and self.Game.Hand_Deck.handNotFull(self.ID):
			if comment == "CastbyOthers":
				print("Cloning Device is cast and adds a copy of a random minion in opponent's deck into player's hand.")
				Copy = type(np.random.choice(minionsinDeck))(self.Game, self.ID)
				self.Game.Hand_Deck.addCardtoHand(Copy, self.ID)
			else:
				print("Cloning Device is cast and lets player discover a copy of a minion in opponent's deck.")
				numOptions = min(3, len(minionsinDeck))
				copies = []
				for minion in np.random.choice(minionsinDeck, numOptions, replace=False):
					copies.append(type(minion)(self.Game, self.ID))
					
				self.Game.options = copies
				self.Game.DiscoverHandler.startDiscover(self)
		return None
		
	def discoverDecided(self, subject, target):
		if subject == self:
			print("Copy of minion in opponent's deck", target.name, "is put into player's hand.")
			self.Game.Hand_Deck.addCardtoHand(target, self.ID)
			
			
class TestSubject(Minion):
	Class, race, name = "Priest", "", "Test Subject"
	mana, attack, health = 1, 0, 2
	index = "Boomsday-Priest-1-0-2-Minion-None-Test Subject-Deathrattle"
	needTarget, keyWord, description = False, "", "Deathrattle: Return any spells you cast on this minion to your hand"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [ReturnAllSpellsCastonThis(self)]
		
class ReturnAllSpellsCastonThis(Deathrattle_Minion):
	def trigger(self, signal, ID, subject, target, number, comment, choice=0):
		print("Deathrattle: Return any spell cast on this minion to your hand triggers")
		for index in self.entity.history["Spells Cast on This"]:
			if self.entity.Game.Hand_Deck.handNotFull(self.entity.ID):
				self.entity.Game.Hand_Deck.addCardtoHand(index, self.entity.ID, "CreateUsingIndex")
			else:
				break
				
				
class DeadRinger(Minion):
	Class, race, name = "Priest", "Mech", "Dead Ringer"
	mana, attack, health = 2, 2, 1
	index = "Boomsday-Priest-2-2-1-Minion-Mech-Dead Ringer-Deathrattle"
	needTarget, keyWord, description = False, "", "Deathrattle: Draw a Deathrattle minion from your deck"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [DrawaDeathrattlemMinion(self)]
		
class DrawaDeathrattlemMinion(Deathrattle_Minion):
	def trigger(self, signal, ID, subject, target, number, comment, choice=0):
		deathrattleMinions = []
		for card in self.entity.Game.Hand_Deck.decks[self.entity.ID]:
			if card.cardType == "Minion" and card.deathrattles != []:
				deathrattleMinions.append(card)
				
		if deathrattleMinions != []:
			print("Dead Ringer's deathrattle triggers and lets player draw a Deathrattle minion from deck.")
			self.entity.Game.Hand_Deck.drawCard(self.entity.ID, np.random.choice(deathrattleMinions))
			
			
class ExtraArms(Spell):
	Class, name = "Priest", "Extra Arms"
	needTarget, mana = True, 3
	index = "Boomsday-Priest-3-Spell-Extra Arms"
	description = "Give a minion +2/+2. Add 'More Arms' to your hand that gives +2/+2"
	
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			print("Extra Arms is cast and gives +2/+2 to minion ", target.name)
			target.buffDebuff(2, 2)
		print("Extra Arms puts a More Arms to player's hand")
		self.Game.Hand_Deck.addCardtoHand(MoreArms(self.Game, self.ID), self.ID)
		return target
		
class MoreArms(Spell):
	Class, name = "Priest", "More Arms!"
	needTarget, mana = True, 3
	index = "Boomsday-Priest-3-Spell-More Arms!-Uncollectible"
	description = "Give a minion +2/+2"
	
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			print("Extra Arms is cast and gives +2/+2 to minion ", target.name)
			target.buffDebuff(2, 2)
		return target
		
		
class OmegaMedic(Minion):
	Class, race, name = "Priest", "", "Omega Medic"
	mana, attack, health = 3, 3, 4
	index = "Boomsday-Priest-3-3-4-Minion-None-Omega Medic-Battlecry"
	needTarget, keyWord, description = False, "", "Battlecry: If your have 10 Mana Crystals, restore 10 health to your hero"
	
	def whenEffective(self, target=None, comment="", choice=0):
		if self.Game.ManaHandler.manasUpper[self.ID] == 10:
			heal = 10 * (2 ** self.countHealDouble())
			print("Omega Medic's battlecry restores %d health to player."%heal)
			self.Game.heroes[self.ID].getsHealed(self, heal)
		return self, None
		
		
class PowerWordReplicate(Spell):
	Class, name = "Priest", "Power Word: Replicate"
	needTarget, mana = True, 5
	index = "Boomsday-Priest-5-Spell-Power Word: Replicate"
	description = "Choose a friendly minion. Summon a 5/5 copy of it"
	
	def available(self):
		return self.selectableFriendlyMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.ID == self.ID and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None and self.spaceonBoard(self.ID) > 0:
			print("Power Word: Replicate is cast and summons a 5/5 copy of friendly minion")
			Copy = target.selfCopy(self.ID) if target.onBoard else type(target)(self.Game, self.ID)
			Copy.statReset(5, 5)
			self.Game.summonMinion(Copy, target.position+1, self.ID)
		return target
		
class RecklessExperimenter(Minion):
	Class, race, name = "Priest", "", "Reckless Experimenter"
	mana, attack, health = 5, 4, 6
	index = "Boomsday-Priest-5-4-6-Minion-None-Reckless Experimenter"
	needTarget, keyWord, description = False, "", "Deathrattle minions you play cost (3) less, but die at end of turn.(cost can't be reduced below 1)"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.manaAura = YourDeathrattleMinionsCost3LessbutNoLessthan1(self)
		self.appearResponse = [self.activateAura]
		self.disappearResponse = [self.deactivateAura]
		self.silenceResponse = [self.deactivateAura]
		self.triggersonBoard = [Trigger_RecklessExperimenter(self)]
		
	def activateAura(self):
		print("Reckless Experimenter's mana aura is included. Player's deathrattle minions now cost 3 less(Cost can't be reduced to below 1), but they die at the end of turn.")
		self.Game.ManaHandler.CardAuras.append(self.manaAura)
		self.Game.ManaHandler.calcMana()
		
	def deactivateAura(self):
		print("Reckless Experimenter's mana aura is removed. Deathrattle minions no longer cost 3 less.")
		extractfrom(self.manaAura, self.Game.ManaHandler.CardAuras)
		self.Game.ManaHandler.calcMana()
		
class YourDeathrattleMinionsCost3LessbutNoLessthan1:
	def __init__(self, minion):
		self.minion = minion
		self.temporary = False
		
	def handleMana(self, target):
		if target.cardType == "Minion" and target.ID == self.minion.ID and target.deathrattles != []:
			target.mana -= 3
			target.mana = max(target.mana, 1)
			
class Trigger_RecklessExperimenter(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionPlayed"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject.ID == self.entity.ID and subject.deathrattles != []
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("Player plays Deathrattle minion %s, Reckless Experimenter sets it to die at the end of turn."%subject.name)
		trigger = Trigger_GoblinPrank(subject)
		trigger.connect()
		subject.triggersonBoard.append(trigger) #Borrow from Hunter Spell Goblin Prank
		
		
class ZerekMasterCloner(Minion):
	Class, race, name = "Priest", "", "Zerek. Master Cloner"
	mana, attack, health = 6, 5, 5
	index = "Boomsday-Priest-6-5-5-Minion-None-Zerek. Master Cloner-Deathrattle-Legendary"
	needTarget, keyWord, description = False, "", "Deathrattle: If you've cast any spells on this minion, resummon it"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [ResummonThisifBeenTargetedbyYourSpells(self)]
		
class ResummonThisifBeenTargetedbyYourSpells(Deathrattle_Minion):
	def trigger(self, signal, ID, subject, target, number, comment, choice=0):
		if self.entity.history["Spells Cast on This"] != []:
			print("Deathrattle: If you've cast spells on this minion, resummon it triggers")
			self.entity.Game.summonMinion(ZerekMasterCloner(self.entity.Game, self.entity.ID), self.entity.position+1, self.entity.ID)
			
			
class ZereksCloningGallery(Spell):
	Class, name = "Priest", "Zerek's Cloning Gallery"
	needTarget, mana = False, 9
	index = "Boomsday-Priest-9-Spell-Zerek's Cloning Gallery-Legendary"
	description = "Summon a 1/1 copy of each minion in your deck"
	
	def randomorDiscover(self):
		num = 0
		for card in self.Game.Hand_Deck.decks[self.ID]:
			if card.cardType == "Minion":
				num += 1
				if num > 7:
					return "Random"
					
		return "No RNG"
		
	def whenEffective(self, target=None, comment="", choice=0):
		print("Zerek's Cloning Gallery is cast and summons a 1/1 copy of each minion in player's deck.")
		minionstoSummon = []
		for card in self.Game.Hand_Deck.decks[self.ID]:
			if card.cardType == "Minion":
				minionstoSummon.append(card)
				
		if minionstoSummon != []:
			minionstoSummon = np.random.choice(minionstoSummon, min(len(minionstoSummon), self.Game.spaceonBoard(self.ID)), replace=False)
			minions = []
			for element in minionstoSummon:
				Copy = type(element)(self.Game, self.ID)
				Copy.statReset(1, 1)
				minions.append(Copy)
				
			self.Game.summonMinion(minions, (-1, "totheRightEnd"), self.ID)
		return None
		
		
"""Rogue cards"""
class LabRecruiters(Minion):
	Class, race, name = "Rogue", "", "Lab Recruiters"
	mana, attack, health = 2, 3, 2
	index = "Boomsday-Rogue-2-3-2-Minion-None-Lab Recruiters-Battlecry"
	needTarget, keyWord, description = True, "", "Battlecry: Shuffle 3 copies of a friendly minion into your deck"
	
	def targetExists(self, choice=0):
		return self.selectableFriendlyMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.ID == self.ID and target != self and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			print("Lab Recruiter's battlecry shuffles 3 copies of a friendly Minion %s into deck."%target.name)
			cards = [type(target)(self.Game, self.ID) for i in range(3)]
			self.Game.Hand_Deck.shuffleCardintoDeck(cards, self.ID)
		return self, target
		
		
class VioletHaze(Spell):
	Class, name = "Rogue", "Violet Haze"
	needTarget, mana = False, 2
	index = "Boomsday-Rogue-2-Spell-Violet Haze"
	description = "Add two Deathrattle cards to your hand"
	
	def randomorDiscover(self):
		return "Random"
		
	def whenEffective(self, target=None, comment="", choice=0):
		print("Violet Haze is cast and adds two Deathrattle cards to player's hand.")
		if self.Game.Hand_Deck.handNotFull(self.ID):
			deathrattleCards = []
			for key, value in self.Game.cardPool.keys():
				if "-Deathrattle" in key and "Uncollectible" not in key:
					deathrattleCards.append(value)
					
			cards = np.random.choice(deathrattleCards, 2, replace=True)
			self.Game.Hand_Deck.addCardtoHand(cards, self.ID, "CreateUsingType")
		return None
		
		
class CrazedChemist(Minion):
	Class, race, name = "Rogue", "", "Crazed Chemist"
	mana, attack, health = 5, 4, 4
	index = "Boomsday-Rogue-5-4-4-Minion-None-Crazed Chemist-Combo"
	needTarget, keyWord, description = True, "", "Combo: Give a friendly minion +4 Attack"
	
	def returnTrue(self, choice=0):
		return self.Game.CounterHandler.cardsPlayedThisTurn[self.ID] != []
		
	def effectCanTrigger(self):
		return self.Game.CounterHandler.cardsPlayedThisTurn[self.ID] != []
		
	def targetExists(self, choice=0):
		return self.selectableFriendlyMinionExists(choice)
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.ID == self.ID and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None and self.Game.CounterHandler.cardsPlayedThisTurn[self.ID] != []:
			print("Crazed Chemist's Combo triggers and gives friendly minion %s +4 Attack"%target.name)
			target.buffDebuff(4, 0)
		return self, target
		
		
class PogoHopper(Minion):
	Class, race, name = "Rogue", "Mech", "Pogo-Hopper"
	mana, attack, health = 1, 1, 1
	index = "Boomsday-Rogue-1-1-1-Minion-Mech-Pogo-Hopper-Battlecry"
	needTarget, keyWord, description = False, "", "Battlecry: Gain +2/+2 for each other Pogo-Hopper you played this game"
	
	def whenEffective(self, target=None, comment="", choice=0):
		numPogoHoppersPlayedThisGame = 0
		for index in self.Game.CounterHandler.cardsPlayedThisGame[self.ID]:
			if index == self.index:
				numPogoHoppersPlayedThisGame += 1
				
		print("Pogo-Hopper's battlecry triggers and minion gains +2/+2 for each Pogo-Hopper player played this game.")
		self.buffDebuff(numPogoHoppersPlayedThisGame, numPogoHoppersPlayedThisGame)
		return self, None
		
		
class NecriumBlade(Weapon):
	Class, name, description = "Rogue", "Necrium Blade", "Deathrattle: Trigger the Deathrattle of a random friendly minion"
	mana, attack, durability = 3, 3, 2
	index = "Boomsday-Rogue-3-3-2-Weapon-Necrium Blade-Deathrattle"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [TriggerDeathrattleofRandomFriendlyMinion(self)]
		
class TriggerDeathrattleofRandomFriendlyMinion(Deathrattle_Weapon):
	def trigger(self, signal, ID, subject, target, number, comment, choice=0):
		deathrattleMinions = []
		for minion in self.entity.Game.minionsonBoard(self.entity.ID):
			if minion.deathrattles != []:
				deathrattleMinions.append(minion)
				
		if deathrattleMinions != []:
			minion = np.random.choice(deathrattleMinions)
			print("Deathrattle: Trigger random friendly minion %s's Deathrattle triggers"%minion.name)
			for trigger in minion.deathrattles:
				trigger.trigger("DeathrattleTriggers", self.ID, None, minion, minion.attack, "")
				
				
class BlightnozzleCrawler(Minion):
	Class, race, name = "Rogue", "Mech", "Blightnozzle Crawler"
	mana, attack, health = 4, 2, 4
	index = "Boomsday-Rogue-4-2-4-Minion-Mech-Blightnozzle Crawler-Deathrattle"
	needTarget, keyWord, description = False, "", "Deathrattle: Summon a 1/1 Ooze with Poisonous and Rush"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [SummonanOoze(self)]
		
class SummonanOoze(Deathrattle_Minion):
	def trigger(self, signal, ID, subject, target, number, comment, choice=0):
		print("Deathrattle summon a 1/1 Ooze with Poisonous and Rush triggers")
		self.entity.Game.summonMinion(RadioactiveOoze(self.entity.Game, self.entity.ID), self.entity.position+1, self.entity.ID)
		
class RadioactiveOoze(Minion):
	Class, race, name = "Rogue", "", "Radioactive Ooze"
	mana, attack, health = 1, 1, 1
	index = "Boomsday-Rogue-1-1-1-Minion-None-Radioactive Ooze-Rush-Poisonous-Uncollectible"
	needTarget, keyWord, description = False, "Poisonous,Rush", "Poisonous, Rush"
	
	
class AcademicEspionage(Spell):
	Class, name = "Rogue", "Academic Espionage"
	needTarget, mana = False, 4
	index = "Boomsday-Rogue-4-Spell-Academic Espionage"
	description = "Shuffle 10 1-Cost cards from another class(from your opponent's class)"
	
	def randomorDiscover(self):
		return "Random"
		
	def whenEffective(self, target=None, comment="", choice=0):
		print("Academic Espionage is cast and shuffles 10 Cost-1 copies of cards from opponent's class into player's deck.")
		Class = self.Game.heroes[3-self.ID].Class
		enemyClassCards = list(self.Game.ClassCards[Class].values())
		for i in range(10):
			card = np.random.choice(enemyClassCards)(self.Game, self.ID)
			card.mana_set, card.mana = 1, 1
			self.Game.Hand_Deck.shuffleCardintoDeck(card, self.ID)
		return None
		
		
class NecriumVial(Spell):
	Class, name = "Rogue", "Necrium Vial"
	needTarget, mana = True, 5
	index = "Boomsday-Rogue-5-Spell-Necrium Vial"
	description = "Trigger a friendly minion's Deathrattle twice"
	
	def available(self):
		return self.selectableFriendlyMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.ID == self.ID and target.onBoard and target.deathrattles != []
		
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			print("Necrium Vial is cast and triggers friendly Deathrattle minion's deathrattles twice.")
			comment = "TriggeredonBoard" if target.onBoard else ""
			for i in range(2):
				for trigger in target.deathrattles:
					trigger.trigger("DeathrattleTriggers", self.ID, None, target, target.attack, "")
		return target
		
		
class MyraRotspring(Minion):
	Class, race, name = "Rogue", "", "Myra Rotspring"
	mana, attack, health = 5, 4, 2
	index = "Boomsday-Rogue-5-4-2-Minion-None-Myra Rotspring-Battlecry-Legendary"
	needTarget, keyWord, description = False, "", "Battlecry: Discover a Deathrattle minion. Also gain its Deathrattle"
	
	def randomorDiscover(self):
		return "Discover"
		
	def whenEffective(self, target=None, comment="", choice=0):
		Class = self.Game.heroes[self.ID].Class
		deathrattleMinions = []
		for key, value in self.Game.ClassCards[Class].items():
			if "Minion" in key and "Deathrattle" in key:
				deathrattleMinions.append(value)
		for key, value in self.Game.ClassCards["Neutral"].items():
			if "Minion" in key and "Deathrattle" in key:
				deathrattleMinions.append(value)
				
		if comment == "InvokedbyOthers":
			minion = np.random.choice(deathrattleMinions)(self.Game, self.ID)
			print("Myra Rotspring's battlecry adds a random Deathrattle minion %s to player's hand. Then it gains its Deathrattle."%minion.name)
			self.Game.Hand_Deck.addCardtoHand(minion, self.ID)
			for obj in minion.deathrattles:
				self.deathrattles.append(type(obj)(self))
		else:
			minions = np.random.choice(deathrattleMinions, 3, replace=False)
			self.Game.options = [minion(self.Game, self.ID) for minion in minions]
			self.Game.DiscoverHandler.startDiscover(self)
			
		return self, None
		
	def discoverDecided(self, option):
		self.Game.Hand_Deck.addCardtoHand(option, self.ID)
		for obj in option.deathrattles:
			self.deathrattles.append(type(obj)(self))
			
			
class MyrasUnstableElement(Spell):
	Class, name = "Rogue", "Myra's Unstable Element"
	needTarget, mana = False, 5
	index = "Boomsday-Rogue-5-Spell-Myra's Unstable Element-Legendary"
	description = "Draw your entire deck"
	def randomorDiscover(self):
		return "Random"
		
	def whenEffective(self, target=None, comment="", choice=0):
		print("Myra's Unstable Element is cast and player draws the entire deck.")
		handSize = len(self.Game.Hand_Deck.hands[self.ID])
		deckSize = len(self.Game.Hand_Deck.decks[self.ID])
		for i in range(min(self.Game.Hand_Deck.handUpperLimit[self.ID]-handSize, deckSize)):
			self.Game.Hand_Deck.drawCard(self.ID)
			
		self.Game.Hand_Deck.extractfromDeck(None, all=True, ID=self.ID)
		return None
		
"""Shaman cards"""
class BeakeredLightnining(Spell):
	Class, name = "Shaman", "Beakered Lightnining"
	needTarget, mana = False, 1
	index = "Boomsday-Shaman-0-Spell-Beakered Lightnining-Overload"
	description = "Deal 1 damage to all minions. Overload: (2)"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.overload = 2
		
	def whenEffective(self, target=None, comment="", choice=0):
		damage = (1 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		print("Beakered Lightnining is cast and deals %d damage to all minions."%damage)
		targets = self.Game.minionsonBoard(1) + self.Game.minionsonBoard(2)
		self.dealsAOE(targets, [damage for obj in targets])
		return None
		
		
class ElementaryReaction(Spell):
	Class, name = "Shaman", "Elementary Reaction"
	needTarget, mana = False, 2
	index = "Boomsday-Shaman-2-Spell-Elementary Reaction"
	description = "Draw a card. If you played an Elemental last turn, add a copy of it into your hand"
	
	def whenEffective(self, target=None, comment="", choice=0):
		print("Elementary Reaction is cast and lets player draw a card.")
		card = self.Game.Hand_Deck.drawCard(self.ID)[0]
		if card != None and self.Game.CounterHandler.numElementalsPlayedLastTurn[self.ID] > 0:
			print("Elementary Reaction adds a copy of the drawn card because player played an Elemental last turn.")
			self.Game.Hand_Deck.addCardtoHand(card.selfCopy(self.ID), self.ID)
		return None
		
		
class MenacingNimbus(Minion):
	Class, race, name = "Shaman", "Elemental", "Menacing Nimbus"
	mana, attack, health = 2, 2, 2
	index = "Boomsday-Shaman-2-2-2-Minion-Elemental-Menacing Nimbus-Battlecry"
	needTarget, keyWord, description = False, "", "Battlecry: Add a random Elemental to your hand"
	
	def randomorDiscover(self):
		return "RNG"
		
	def whenEffective(self, target=None, comment="", choice=0):
		elementals = list(self.Game.MinionswithRace["Elemental"].values())
		print("Menacing Nimbus's battlecry adds a random Elemental to player's hand.")
		self.Game.Hand_Deck.addCardtoHand(np.random.choice(elementals), self.ID, "CreateUsingType")
		return self, None
		
		
class OmegaMind(Minion):
	Class, race, name = "Shaman", "", "Omega Mind"
	mana, attack, health = 2, 2, 3
	index = "Boomsday-Shaman-2-2-3-Minion-None-Omega Mind-Battlecry"
	needTarget, keyWord, description = False, "", "Battlecry: If your have 10 Mana Crystals, your spells have Lifesteal this turn"
	
	def whenEffective(self, target=None, comment="", choice=0):
		if self.Game.ManaHandler.manasUpper[self.ID] >= 10:
			print("Omega Mind's battlecry players spells have lifesteal this turn.")
			self.Game.playerStatus[self.ID]["Spells Have Lifesteal"] += 1
			trigger = Trigger_OmegaMind(self)
			trigger.ID = self.ID
			trigger.connect()
		return self, None
		
class Trigger_OmegaMind(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["TurnEnds"])
		self.ID = 1
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return True
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		extractfrom((self, "TurnEnds"), self.entity.Game.triggersonBoard[self.ID])
		
		
class VoltaicBurst(Minion):
	Class, name = "Shaman", "Voltaic Burst"
	needTarget, mana = False, 1
	index = "Boomsday-Shaman-1-Spell-Voltaic Burst-Overload"
	description = "Summon two 1/1 Sparks with Rush. Overload: (1)"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.overload = 1
		
	def whenEffective(self, target=None, comment="", choice=0):
		print("Voltaic Burst is cast and summons two 1/1 Sparks with Rush.")
		self.Game.summonMinion([Spark(self.Game, self.ID) for i in range(2)], (-1, "totheRightEnd"), self.ID)
		return None
		
		
class StormChaser(Minion):
	Class, race, name = "Shaman", "Elemental", "Thunderhead"
	mana, attack, health = 4, 3, 4
	index = "Boomsday-Shaman-4-3-4-Minion-Elemental-Storm Chaser-Battlecry"
	needTarget, keyWord, description = False, "", "Battlecry: Draw a spell from your deck that costs (5) or more"
	
	def randomorDiscover(self):
		return "Random"
		
	def whenEffective(self, target=None, comment="", choice=0):
		spellsinDeckCosting5orMore = []
		for card in self.Game.Hand_Deck.decks[self.ID]:
			if card.cardType == "Spell" and card.mana_set > 4:
				spellsinDeckCosting5orMore.append(card)
				
		print("Storm Chaser's battlecry lets player draw two spells from deck that cost 5 or more.")
		if spellsinDeckCosting5orMore != []:
			self.Game.Hand_Deck.drawCard(self.ID, np.random.choice(spellsinDeckCosting5orMore))
		return self, None
		
		
class Eureka(Spell):
	Class, name = "Shaman", "Eureka!"
	needTarget, mana = False, 6
	index = "Boomsday-Shaman-6-Spell-Eureka!"
	description = "Summon a copy of a minion in your hand"
	
	def randomorDiscover(self):
		numMinionsinHand = 0
		for card in self.Game.Hand_Deck.hands[self.ID]:
			if card.cardType == "Minion":
				numMinionsinHand += 1
		if numMinionsinHand > 1:
			return "Random"
		else:
			return "No RNG"
			
	def whenEffective(self, target=None, comment="", choice=0):
		print("Eureka! is cast and summons a copy of a random minion in player's hand.")
		minionsinHand = []
		for card in self.Game.Hand_Deck.hands[self.ID]:
			if card.cardType == "Minion":
				minionsinHand.append(card)
				
		if minionsinHand != []:
			self.Game.summonMinion(np.random.choice(minionsinHand).selfCopy(self.ID), -1, self.ID)
		return None
		
		
class Thunderhead(Minion):
	Class, race, name = "Shaman", "Elemental", "Thunderhead"
	mana, attack, health = 4, 3, 6
	index = "Boomsday-Shaman-4-3-6-Minion-Elemental-Thunderhead"
	needTarget, keyWord, description = False, "", "After you play a card with Overload, summon two 1/1 Sparks with Rush"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_Thunderhead(self)]
		
class Trigger_Thunderhead(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionBeenPlayed", "SpellBeenPlayed", "WeaponBeenPlayed", "HeroCardBeenPlayed"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject.ID == self.entity.ID and subject.overload > 0
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("After player plays card %s with Overload, %s summons two 1/1 Sparks with Rush."%(subject.name, self.entity.name))
		self.entity.Game.summonMinion([Sparks(self.entity.Game, self.entity.ID)], (self.entity.position, "leftandRight"), self.entity.ID)
		
#Electra Stormsurge's repeated targeting spell will be cast upon the same target.
#The repeated spell is before the death resolution.
#Choose One spells, when repeated, will adopt a random choice.

#The Choose One spells will be cast with the same options and targets.
#The discover activities won't be skipped and has to be finished by player.
#The spells takes effect twice before Wild Pyromancer can deal AOE damage.

#Raven Idol will be repeated with the same option and player can discover for a second time..
class ElectraStormsurge(Minion):
	Class, race, name = "Shaman", "Elemental", "Electra Stormsurge"
	mana, attack, health = 3, 3, 3
	index = "Boomsday-Shaman-3-3-3-Minion-Elemental-Electra Stormsurge-Battlecry-Legendary"
	needTarget, keyWord, description = False, "", "Battlecry: Your next spell this turn casts twice"
	
	def whenEffective(self, target=None, comment="", choice=0):
		print("Electra Stormsurge's battlecry player's next spell this turn casts twice.")
		self.Game.playerStatus[self.ID]["Spells Cast Twice"] += 1
		trigger = Trigger_ElectraStormsurge(self)
		trigger.ID = self.ID
		trigger.connect()
		return self, None
		
class Trigger_ElectraStormsurge(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["SpellBeenCast", "TurnEnds"])
		self.ID = 1
		
	def connect(self):
		for signal in self.signals:
			self.entity.Game.triggersonBoard[self.ID].append((self, signal))
			
	def disconnect(self):
		for signal in self.signals:
			extractfrom((self, signal), self.entity.Game.triggersonBoard[self.ID])
			
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		if signal == "SpellBeenCast":
			return subject.ID == self.ID
		return True
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		if signal == "SpellBeenCast":
			print("Spell %s is played/cast and Electra Stormsurge's Next Spell Casts Twice expires.")
			
		if self.Game.playerStatus[self.ID]["Spells Cast Twice"] > 0:
			self.Game.playerStatus[self.ID]["Spells Cast Twice"] -= 1
		extractfrom((self, "SpellBeenCast"), self.entity.Game.triggersonBoard[self.ID])
		extractfrom((self, "TurnEnds"), self.entity.Game.triggersonBoard[self.ID])
		
		
class TheStormBringer(Spell):
	Class, name = "Shaman", "The Storm Bringer"
	needTarget, mana = False, 6
	index = "Boomsday-Shaman-6-Spell-The Storm Bringer-Legendary"
	description = "Transform your minions into random Legendary minions"
	
	def randomorDiscover(self):
		return "Random"
		
	def whenEffective(self, target=None, comment="", choice=0):
		print("The Storm Bringer is cast and transforms all friendly minions into random Legendary Minions.")
		for minion in fixedList(self.Game.minionsonBoard(self.ID)):
			legendary = np.random.choice(self.Game.LegendaryMinions)(self.Game, self.ID)
			self.Game.transform(minion, legendary)
		return None
		
"""Warlock cards"""
class SpiritBomb(Spell):
	Class, name = "Warlock", "Spirit Bomb"
	needTarget, mana = True, 1
	index = "Boomsday-Warlock-1-Spell-Spirit Bomb"
	description = "Deal 4 damage to a minion and your hero"
	
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0):
		damage = (4 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		if target != None:
			print("Spirit Bomb deals %d damage to minion", target.name)
			self.dealsDamage(target, damage)
			
		print("Spirit Bomb deals %d damage to player", self.Game.heroes[self.ID].name)
		self.dealsDamage(self.Game.heroes[self.ID], damage)
		return target
		
		
class DemonicProject(Spell):
	Class, name = "Warlock", "Demonic Project"
	needTarget, mana = False, 2
	index = "Boomsday-Warlock-2-Spell-Demonic Project"
	description = "Transform a random minion in each player's hand into a Demon"
	
	def randomorDiscover(self):
		return "Random"
		
	def whenEffective(self, target=None, comment="", choice=0):
		print("Demonic Project is cast and each player transforms a minion in hand into a random Demon.")
		demons = list(self.Game.MinionswithRace["Demon"].values())
		for ID in range(1, 3):
			minionsinHand = []
			for card in self.Game.Hand_Deck.hands[1]:
				if card.cardType == "Minion":
					minionsinHand.append(card)
					
			if minionsinHand != []:
				minion = np.random.choice(minionsinHand)
				demon = np.random.choice(demons)(self.Game, 1)
				self.Game.Hand_Deck.replaceCardinHand(minion, demon)
				print("Demonic Project transforms player %d's minion %s into Demon"%(ID, minion.name), demon.name)
				
		return None
		
		
class DoublingImp(Minion):
	Class, race, name = "Warlock", "Demon", "Doubling Imp"
	mana, attack, health = 3, 2, 2
	index = "Boomsday-Warlock-3-2-2-Minion-Demon-Doubling Imp-Battlecry"
	needTarget, keyWord, description = False, "", "Battlecry: Summon a copy of this minion"
	
	def whenEffective(self, target=None, comment="", choice=0):
		print("Doubling Imp's battlecry minion summons a copy of itself.")
		minion = self.selfCopy(self.ID)
		self.Game.summonMinion(minion, self.position+1, self.ID)
		return self, None
		
		
class SoulInfusion(Spell):
	Class, name = "Warlock", "Soul Infusion"
	needTarget, mana = False, 1
	index = "Boomsday-Warlock-1-Spell-Soul Infusion"
	description = "Give the leftmost minion in your hand +2/+2"
	
	def whenEffective(self, target=None, comment="", choice=0):
		print("Soul Infusion is cast and gives the leftmost minion in player's hand +2/+2.")
		for i in range(len(self.Game.Hand_Deck.hands[self.ID])):
			if self.Game.Hand_Deck.hands[self.ID][i].cardType == "Minion":
				self.Game.Hand_Deck.hands[self.ID][i].buffDebuff(2, 2)
				break
				
		return None
		
		
class VoidAnalyst(Minion):
	Class, race, name = "Warlock", "Demon", "Void Analyst"
	mana, attack, health = 2, 2, 2
	index = "Boomsday-Warlock-2-2-2-Minion-Demon-Void Analyst-Deathrattle"
	needTarget, keyWord, description = False, "", "Deathrattle: Give all Demons in your hand +1/+1"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [GiveDemonsinHandPlus1Plus1(self)]
		
class GiveDemonsinHandPlus1Plus1(Deathrattle_Minion):
	def trigger(self, signal, ID, subject, target, number, comment, choice=0):
		print("Deathrattle: Give all minions in your hand +1/+1 triggers")
		for card in self.entity.Game.Hand_Deck.hands[self.entity.ID]:
			if card.cardType == "Minion" and "Demon" in card.race:
				card.buffDebuff(1, 1)
				
				
class NethersoulBuster(Minion):
	Class, race, name = "Warlock", "Demon", "Nethersoul Buster"
	mana, attack, health = 3, 1, 5
	index = "Boomsday-Warlock-3-1-5-Minion-Demon-Nethersoul Buster-Battlecry"
	needTarget, keyWord, description = False, "", "Battlecry: Gain +1 Attack for each damage your hero has taken this turn"
	
	def whenEffective(self, target=None, comment="", choice=0):
		if self.Game.CounterHandler.damageonHeroThisTurn[self.ID] > 0:
			print("Nethersoul Buster's battlecry gives minion +1 attack for each damage player has taken this turn.")
			self.buffDebuff(self.Game.CounterHandler.damageonHeroThisTurn[self.ID], 0)
		return self, None
		
		
class OmegaAgent(Minion):
	Class, race, name = "Warlock", "", "Omega Agent"
	mana, attack, health = 5, 4, 5
	index = "Boomsday-Warlock-5-4-5-Minion-None-Omega Agent-Battlecry"
	needTarget, keyWord, description = False, "", "Battlecry: If you have 10 Mana Crystals, summon 2 copies of this minion"
	
	def whenEffective(self, target=None, comment="", choice=0):
		if self.Game.ManaHandler.manasUpper[self.ID] == 10:
			pos = (self.position, "leftandRight") if self.onBoard else (-1, "totheRightEnd")
			self.Game.summonMinion([self.selfCopy(self.ID) for i in range(2)], pos, self.ID)
		return self, None
		
		
class Ectomancy(Spell):
	Class, name = "Warlock", "Ectomancy"
	needTarget, mana = False, 6
	index = "Boomsday-Warlock-6-Spell-Ectomancy"
	description = "Summon copies of all Demons you control"
	
	def whenEffective(self, target=None, comment="", choice=0):
		demons = []
		for minion in self.Game.minionsonBoard(self.ID):
			if "Demon" in minion.race:
				demons.append(minion)
				
		if demons != []:
			copies = []
			for demon in demons:
				self.Game.summonMinion(demon.selfCopy(self.ID), demon.position+1, self.ID)
				
		return None
#How to mark the cards drawn to be discarded at the end of turn.
#Then how to cleanse the mark after shuffling them back into deck.
class TheSoularium(Spell):
	Class, name = "Warlock", "The Soularium"
	needTarget, mana = False, 1
	index = "Boomsday-Warlock-1-Spell-The Soularium-Legendary"
	description = "Draw 3 cards. At the end of your turn, discard them"
	
	def whenEffective(self, target=None, comment="", choice=0):
		cardsDrawn = []
		for i in range(3):
			card = self.Game.Hand_Deck.drawCard(self.ID)[0]
			if card != None:
				trigger = Trigger_TheSoularium(card)
				trigger.connect()
				card.triggersinHand[1].append(trigger)
				
		return None
		
class Trigger_TheSoularium(TriggerinHand):
	def __init__(self, entity):
		self.blank_init(entity, ["TurnEnds"])
		self.temp = True
		
	#They will be discarded at the end of any turn
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.inHand
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("At the end of turn, card %s drawn by The Soularium is discarded"%self.entity.name)
		#The discard() func takes care of disconnecting the TriggerinHand
		self.entity.Game.Hand_Deck.discard(self.ID, self.entity)
		
#We don't know if this deathrattle overlapping with Immortal Prelate will cause the Immortal Prelate's enchantment to vanish.
class DrMorrigan(Minion):
	Class, race, name = "Warlock", "", "Dr. Morrigan"
	mana, attack, health = 6, 5, 5
	index = "Boomsday-Warlock-6-5-5-Minion-None-Dr. Morrigan-Deathrattle-Legendary"
	needTarget, keyWord, description = False, "", "Deathrattle: Swap this with a minion in your deck"
#	def __init__(self, Game, ID):
#		self.blank_init(Game, ID)
#		#self.deathrattles = [SwapThiswithMinioninDeck(self)]
#		
#	#已经验证，在牌库没有随从的时候，亡语无法触发。这个亡语有无阻循环的可能，应该在Game.deathHandle()里面设置只能循环7将从 的条件。
#class SwapThiswithMinioninDeck(Deathrattle_Minion):
#	#当一个随从上有多个区域移动类的扳机时，只有第一个会生效
#	#假设随从因为其他亡语而已经返回手牌之后则这个亡语就还会再触发了
#	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
#		#如果随从身上已经有其他区域移动扳机触发过，则这个扳机不能两次触发，检测条件为仍在随从列表中
#		return self.entity == target and self.entity in self.entity.Game.minions[self.entity.ID]
#		
#	def trigger(self, signal, ID, subject, target, number, comment, choice=0):
#		minion = self.minion
#		num = 2 if minion.Game.playerStatus[minion.ID]["Deathrattle Trigger Twice"] > 0 else 1
#		for i in range(num):
#			print("Deathrattle: Swap this with a minion in your deck triggers")
#			for card in minion.Game.Hand_Deck.decks[minoin.ID]:
#				if card.cardtype == "Minion" and card != self:
#					minioninDeck.append(card)
#					
#			if minioninDeck != [] and minion.Game.spaceonBoard(minion.ID) > 0:
#				miniontoSummon = minion.Game.Hand_Deck.extractfromDeck(np.random.choice(minionsinDeck))
#				#For now, assume the two minions summoned will both be next to the original position
#				minion.Game.summonMinion(miniontoSummon, minion.position+1, minion.ID)
#				
#		minion.Game.removeMinionorWeapon(minion) #The minion is removed early. Shuffle handle the inDeck label
#		minion.Game.Hand_Deck.shuffleCardintoDeck(minion, minion.ID)
		
"""Warrior cards"""
class EterniumRover(Minion):
	Class, race, name = "Warrior", "Mech", "Eternium Rover"
	mana, attack, health = 1, 1, 3
	index = "Boomsday-Warrior-1-1-3-Minion-Mech-Eternium Rover"
	needTarget, keyWord, description = False, "", "Whenever this minions takes damage, gain 2 Armor"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_EterniumRover(self)]
		
class Trigger_EterniumRover(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionTakesDamage"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return target == self.entity and self.entity.onBoard
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print(self.entity.name, "takes Damage and player gains 3 Armor")
		self.entity.Game.heroes[self.entity.ID].gainsArmor(2)
		
	
class OmegaAssembly(Spell):
	Class, name = "Warrior", "Omega Assembly"
	needTarget, mana = False, 1
	index = "Boomsday-Warrior-1-Spell-Omega Assembly"
	description = "Discover a Mech. If your have 10 Mana Crystals, keep all 3 cards"
	
	def whenEffective(self, target=None, comment="", choice=0):
		if self.Game.Hand_Deck.handNotFull(self.ID):
			mechs = list(self.Game.MinionswithRace["Mech"].values())
			if self.Game.ManaHandler.manasUpper[self.ID] >= 10:
				print("Omega Assembly is cast and player has 10 mana crystals. Three Mechs are added to player's hand.")
				mechs = np.random.choice(mechs, 3, replace=False)
				self.Game.Hand_Deck.addCardtoHand(mechs, self.ID, "CreateUsingIndex")			
			else:
				if comment == "CastbyOthers":
					print("Omega Assembly is cast and adds a random Mech to player's hand")
					self.Game.Hand_Deck.addCardtoHand(np.random.choice(mechs), self.ID, "CreateUsingType")
				else:
					print("Omega Assembly is cast and lets player discover a Mech.")
					mechs = np.random.choice(mechs, 3, replace=False)
					self.Game.options = [mech(self.Game, self.ID) for mech in mechs]
					self.Game.DiscoverHandler.startDiscover(self)
					
		return None
		
	def discoverDecided(self, option):
		print("Mech %s is put into player's hand."%option.name)
		self.Game.Hand_Deck.addCardtoHand(option, self.ID)
		
		
class RocketBoots(Spell):
	Class, name = "Warrior", "Rocket Boots"
	needTarget, mana = True, 2
	index = "Boomsday-Warrior-2-Spell-Rocket Boots"
	description = "Give a minion Rush. Draw a card"
	
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			print("Rocket Boots gives minion %s Rush."%target.name)
			target.getsKeyword("Rush")
			
		print("Rocket Boots lets player draw a card.")
		self.Game.Hand_Deck.drawCard(self.ID)
		return target
		
class WeaponsProject(Spell):
	Class, name = "Warrior", "Weapons Project"
	needTarget, mana = False, 2
	index = "Boomsday-Warrior-2-Spell-Weapons Project"
	description = "Each player equips a 2/3 Weapon and gain 6 Armor"
	
	def whenEffective(self, target=None, comment="", choice=0):
		print("Weapons Project is cast and both players equips a 2/3 Weapon and gains 6 Armor.")
		self.Game.equipsWeapon(Gearblade(self.Game, 1))
		self.Game.heroes[1].gainsArmor(6)
		self.Game.equipsWeapon(Gearblade(self.Game, 2))
		self.Game.heroes[2].gainsArmor(6)
		return None
		
class Gearblade(Weapon):
	Class, name, description = "Warrior", "Gearblade", ""
	mana, attack, durability = 2, 2, 3
	index = "Boomsday-Warrior-2-2-3-Weapon-Gearblade-Uncollectible"
	
	
class Dynomatic(Minion):
	Class, race, name = "Warrior", "Mech", "Dyn-o-matic"
	mana, attack, health = 5, 3, 4
	index = "Boomsday-Warrior-5-3-4-Minion-Mech-Dyn-o-matic-Battlecry"
	needTarget, keyWord, description = False, "", "Battlecry: Deal 5 damage randomly split among all minions except Mechs"
	
	def whenEffective(self, target=None, comment="", choice=0):
		nonMechminions = []
		for i in range(5):
			for minion in self.Game.minionsonBoard(1) + self.Game.minionsonBoard(2):
				if "Mech" in minion.race and minion.health > 0 and minion.dead == False:
					nonMechminions.append(minion)
					
			if nonMechminions != []:
				self.dealsDamage(np.random.choice(nonMechminions), 1)
			else:
				break
		return self, None
		
		
class Supercollider(Weapon):
	Class, name, description = "Warrior", "Supercollider", "After you attack a minion, force it to attack one of its neighbors"
	mana, attack, durability = 5, 1, 3
	index = "Boomsday-Warrior-5-1-3-Weapon-Supercollider"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_Supercollider(self)]
		
class Trigger_Supercollider(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["HeroAttackedMinion"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		#The target can't be dying to trigger this
		return subject == self.entity.Game.heroes[self.entity.ID] and self.entity.onBoard and target.onBoard and target.health > 0 and target.dead == False
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		adjacentMinions = self.entity.Game.findAdjacentMinions(target)[0]
		if adjacentMinions != []:
			minion = np.random.choice(adjacentMinions)
			print("After player attacked minion %s, Supercollider lets it attack a random adjacent minion"%target.name, minion.name)
			self.entity.Game.battleRequest(target, minion, False, False)
			
			
class SecurityRover(Minion):
	Class, race, name = "Warrior", "Mech", "Security Rover"
	mana, attack, health = 6, 2, 6
	index = "Boomsday-Warrior-6-2-6-Minion-Mech-Security Rover"
	needTarget, keyWord, description = False, "", "Whenever this minion takes damage, summon a 2/3 Mech with Taunt"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_SecurityRover(self)]
		
class Trigger_SecurityRover(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionTakesDamage"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return target == self.entity and self.entity.onBoard
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print(self.entity.name, "takes Damage and player gains 3 Armor")
		self.entity.Game.summonMinion(GuardBot(self.entity.Game, self.entity.ID), self.entity.position+1, self.entity.ID)
		
class GuardBot(Minion):
	Class, race, name = "Warrior", "Mech", "Guard Bot"
	mana, attack, health = 2, 2, 3
	index = "Boomsday-Warrior-2-2-3-Minion-Mech-Guard Bot-Taunt-Uncollectible"
	needTarget, keyWord, description = False, "Taunt", "Taunt"
	
	
class BerylliuimNullifier(Minion):
	Class, race, name = "Warrior", "Mech", "Berylliuim Nullifier"
	mana, attack, health = 7, 4, 8
	index = "Boomsday-Warrior-7-4-8-Minion-Mech-Berylliuim Nullifier-Magnetic"
	needTarget, keyWord, description = False, "", "Magnetic. Can't be targeted by spells and Hero Powers"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.marks["Evasive"] = 1
		self.magnetic = 1
		
class BigRedButton(HeroPower):
	name, needTarget = "Big Red Button", False
	index = "Warrior-2-Hero Power-Big Red Button"
	description = "Activate this turn's Mech Suit power!"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_BigRedButton(self)]
		
	def appears(self):
		for trigger in self.triggersonBoard[0]:
			trigger.connect() #把(obj, signal)放入Game.triggersonBoard 中
		self.heroPowerChances, self.heroPowerTimes = 1, 0
		self.Game.sendSignal("HeroPowerAcquired", self.ID, self, None, 0, "")
		self.name = np.random.choice(["Blast Shield", "Delivery Drone", "KABOOM!", "Micro-squad", "Zap Cannon"])
		
	def disappears(self):
		for trigger in self.triggersonBoard:
			#The instance retrives itself from the game's registered triggersonBoard
			trigger.disconnect()
			
	def returnTrue(self, choice=0):
		return self.name == "Zap Cannon"
		
	def available(self):
		if self.heroPowerTimes >= self.heroPowerChances_base + self.heroPowerChances_extra:
			return False
			
		if self.name == "Blast Shield" or self.name == "KABOOM!":
			return True
		elif self.name == "Delivery Drone":
			return self.Game.Hand_Deck.handNotFull(self.ID)
		elif self.name == "Micro-squad":
			return self.Game.spaceonBoard(self.ID) > 0
		else: #"Zap Cannon"
			return self.selectableCharacterExists()
			
	def effect(self, target=None, choice=0):
		if self.name == "Blast Shield":
			print("Hero Power Blast Shield gives player 7 Armor")
			self.Game.heroes[self.ID].gainsArmor(7)
			return 0
		elif self.name == "Delivery Drone":
			print("Delivery Drone lets player discover a Mech")
			mechs = list(self.Game.MinionswithRace["Mech"].values())
			mechs = np.random.choice(mechs, 3, replace=False)
			self.Game.options = [mech(self.Game, self.ID) for mech in mechs]
			self.Game.DiscoverHandler.startDiscover(self)
			return 0
		elif self.name == "KABOOM!":
			damage = (1 + self.Game.playerStatus[self.ID]["Temp Damage Boost"]) * (2 ** self.countDamageDouble())
			print("Hero Power KABOOM! deals %d damage to all enemies")
			targets = [self.Game.heroes[3-self.ID]] + self.Game.minionsonBoard(3-self.ID)
			targets_damaged, damagesActual, targets_Healed, healsActual, totalDamageDone, totalHealingDone, damageSurvivals = self.dealsAOE(target, [damage for obj in targets])
			numKills = 0
			for survival in damageSurvivals:
				if survival > 1:
					numKills += 1
			return numKills
		elif self.name == "Micro-squad":
			print("Hero Power Micro-squad summons three 1/1 Microbots")
			#This summoning won't be doubled by Khadgar
			self.Game.summonMinion([Microbot(self.Game, self.ID) for i in range(3)], (-1, "totheRightEnd"), self.ID, "")
			return 0
		else: #"Zap Cannon"
			damage = (3 + self.Game.playerStatus[self.ID]["Temp Damage Boost"]) * (2 ** self.countDamageDouble())
			print("Hero Power KABOOM! deals %d damage to all enemies")
			objtoTakeDamage, targetSurvival = self.dealsDamage(target, damage)
			if targetSurvival > 1:
				return 1
			return 0
			
	def discoverDecided(self, option):
		print("Mech %s is put into player's hand."%option.name)
		self.Game.Hand_Deck.addCardtoHand(option, self.ID)
		
class Trigger_BigRedButton(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["TurnEnds"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		possibilities = ["Blast Shield", "Delivery Drone", "KABOOM!", "Micro-squad", "Zap Cannon"]
		extractfrom(self.entity.name, possibilities)
		self.entity.name = np.random.choice(possibilities)
		print("At the end of turn, Hero Power Big Rad Button becomes", self.entity.name)
		
class DrBoomMadGenius(Hero):
	mana, description = 9, "Battlecry: For the rest of the game, your Mechs have Rush"
	Class, name, heroPower, armor = "Warrior", "Dr. Boom. Mad Genius", BigRedButton, 7
	index = "Boomsday-Warrior-9-Hero Card-Dr. Boom. Mad Genius-Battlecry-Legendary"
	def whenEffective(self, target=None, comment="", choice=0):
		print("Dr. Boom. Mad Genius' battlecry player's Mechs have Rush for the rest of the game.")
		self.Game.auras.append(MechsHaveRush(self.Game, self.ID))
		return self, None
		
		
class TheBoomship(Spell):
	Class, name = "Warrior", "The Boomship"
	needTarget, mana = False, 9
	index = "Boomsday-Warrior-9-Spell-The Boomship-Legendary"
	description = "Summon 3 random minions from your hand. Give them Rush"
	
	def whenEffective(self, target=None, comment="", choice=0):
		print("The Boomship is cast and summons three minions from player's hand, then gives them Rush.")
		minionsinHand = []
		for card in self.Game.Hand_Deck.hands[self.ID]:
			if card.cardType == "Minion":
				minionsinHand.append(card)
				
		num = min(3, len(minionsinHand), self.Game.spaceonBoard(self.ID))
		if num > 0:
			minionstoSummon = np.random.choice(minionsinHand, num, replace=False)
			for minion in minionstoSummon:
				minion.minion.getsKeyword("Rush")
				self.Game.summonfromHand(minion, -1, self.ID)
		return None