from CardTypes import *
from Triggers_Auras import *
from VariousHandlers import TempManaEffect
from Basic import Trigger_Corruption, Fireball
import numpy as np

def extractfrom(target, listObject):
	temp = None
	for i in range(len(listObject)):
		if listObject[i] == target:
			temp = listObject.pop(i)
			break
	return temp
	
def fixedList(listObject):
	return listObject[0:len(listObject)]
	
	
"""mana 0 minion"""
class Wisp(Minion):
	Class, race, name = "Neutral", "", "Wisp"
	mana, attack, health = 0, 1, 1
	index = "Classic-Neutral-0-1-1-Minion-None-Wisp"
	needTarget, keyWord, description = False, "", ""
	
"""mana 1 minions"""
class AbusiveSergeant(Minion):
	Class, race, name = "Neutral", "", "Abusive Sergeant"
	mana, attack, health = 1, 1, 1
	index = "Classic-Neutral-1-1-1-Minion-None-Abusive Sergeant-Battlecry"
	needTarget, keyWord, description = True, "", "Give a minion +2 Attack this turn"
	
	def targetExists(self, choice=0):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target != self and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			print("Abusive Sergeant's battlecry gives minion %s +2 attack this turn."%target.name)
			target.buffDebuff(2, 0, "EndofTurn")
		return self, target
		
		
class ArgentSquire(Minion):
	Class, race, name = "Neutral", "", "Argent Squire"
	mana, attack, health = 1, 1, 1
	index = "Classic-Neutral-1-1-1-Minion-None-Argent Squire-Divine Shield"
	needTarget, keyWord, description = False, "Divine Shield", "Divine Shield"
	
	
class AngryChicken(Minion):
	Class, race, name = "Neutral", "Beast", "Angry Chicken"
	mana, attack, health = 1, 1, 1
	index = "Classic-Neutral-1-1-1-Minion-Beast-Angry Chicken"
	needTarget, keyWord, description = False, "", "Has +5 Attack while damaged"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggers["StatChanges"] = [self.handleEnrage]
		self.activated = False
		
	def handleEnrage(self):
		if self.silenced == False and self.onBoard:
			if self.activated == False and self.health < self.health_upper:
				self.activated = True
				self.statChange(5, 0)
			elif self.activated and self.health >= self.health_upper:
				self.activated = False
				self.statChange(-5, 0)
				
				
class BloodsailCorsair(Minion):
	Class, race, name = "Neutral", "Pirate", "Bloodsail Corsair"
	mana, attack, health = 1, 1, 2
	index = "Classic-Neutral-1-1-2-Minion-Pirate-Bloodsail Corsair-Battlecry"
	needTarget, keyWord, description = False, "", "Battlecry: Remove 1 Durability from your opponent's weapon"
	
	def whenEffective(self, target=None, comment="", choice=0):
		weapon = self.Game.availableWeapon(self.ID)
		if weapon != None:
			print("Bloodsail Corsair's battlecry removes 1 Durability from opponent's weapon.")
			weapon.loseDurability()
		return self, None
		
		
class HungryCrab(Minion):
	Class, race, name = "Neutral", "Beast", "Hungry Crab"
	mana, attack, health = 1, 1, 2
	index = "Classic-Neutral-1-1-2-Minion-Beast-Hungry Crab-Battlecry"
	needTarget, keyWord, description = True, "", "Battlecry: Destroy a Murloc and gain +2/+2"
	
	def targetExists(self, choice=0):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and "Murloc" in target.race and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			print("Hungry Crab's battlecry destroys Murloc %s and gives minion +2/+2."%target.name)
			if target.onBoard:
				target.dead = True
				self.buffDebuff(2, 2)
			elif target.inHand:
				self.Game.Hand_Deck.discardCard(target.ID, target)
				self.buffDebuff(2, 2)
			elif target.dead:
				self.buffDebuff(2, 2)
		return self, target
		
		
class LeperGnome(Minion):
	Class, race, name = "Neutral", "", "Leper Gnome"
	mana, attack, health = 1, 1, 1
	index = "Classic-Neutral-1-1-1-Minion-None-Leper Gnome-Deathrattle"
	needTarget, keyWord, description = False, "", "Deathrattle: Deal 2 damage to the enemy hero"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [Deal2DamagetoEnemyHero(self)]
		
class Deal2DamagetoEnemyHero(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("Deathrattle: Deal 2 damage to the enemy hero triggers")
		self.entity.dealsDamage(self.entity.Game.heroes[3-self.entity.ID], 2)
		
		
class LightWarden(Minion):
	Class, race, name = "Neutral", "", "Light Warden"
	mana, attack, health = 1, 1, 2
	index = "Classic-Neutral-1-1-2-Minion-None-Light Warden"
	needTarget, keyWord, description = False, "", "Whenever a character is healed, gain +2 Attack"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_LightWarden(self)]
		
class Trigger_LightWarden(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionGetsHealed", "HeroGetsHealed"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("A character is healed and %s gains +2 attack."%self.entity.name)
		self.entity.buffDebuff(2, 0)
		
		
class MurlocTidecaller(Minion):
	Class, race, name = "Neutral", "Murloc", "Murloc Tidecaller"
	mana, attack, health = 1, 1, 2
	index = "Classic-Neutral-1-1-2-Minion-Murloc-Murloc Tidecaller"
	needTarget, keyWord, description = False, "", "Whenever you summon a Murloc, gain +1 Attack"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_MurlocTidecaller(self)]
		
class Trigger_MurlocTidecaller(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionSummoned"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject.ID == self.entity.ID and "Murloc" in subject.race and subject != self.entity
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("A friendly Murloc %s is summoned and %s gains +1 attack."%(subject.name, self.entity.name))
		self.entity.buffDebuff(1, 0)
		
#When the secret is countered by the Couterspell, Secret Keeper doesn't respond.
#Neither does Questing Adventurer.
class SecretKeeper(Minion):
	Class, race, name = "Neutral", "", "Secret Keeper"
	mana, attack, health = 1, 1, 2
	index = "Classic-Neutral-1-1-2-Minion-None-Secret Keeper"
	needTarget, keyWord, description = False, "", "Whenever a Secret is played, gain +1/+1"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_SecretKeeper(self)]
		
class Trigger_SecretKeeper(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["SpellPlayed"])
		
	#Assume Secret Keeper and trigger while dying.
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and "--Secret" in subject.index
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("A Secret is played and %s gains 1/+1."%self.entity.name)
		self.entity.buffDebuff(1, 1)
		
		
class Shieldbearer(Minion):
	Class, race, name = "Neutral", "", "Shieldbearer"
	mana, attack, health = 1, 0, 4
	index = "Classic-Neutral-1-0-4-Minion-None-Shieldbearer-Taunt"
	needTarget, keyWord, description = False, "Taunt", "Taunt"
	
	
class SouthseaDeckhand(Minion):
	Class, race, name = "Neutral", "Pirate", "Southsea Deckhand"
	mana, attack, health = 1, 2, 1
	index = "Classic-Neutral-1-2-1-Minion-Pirate-Southsea Deckhand"
	needTarget, keyWord, description = False, "", "Has Charge while you have a weapon equipped"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.auras["Self Charge"] = SouthseaDeckhand_Dealer(self)
		
class SouthseaDeckhand_Dealer:
	def __init__(self, minion):
		self.minion = minion #For now, there are only three minions that provide this kind aura: Tundra Rhino, Houndmaster Shaw, Whirlwind Tempest
		self.auraAffected = []
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		if self.minion.onBoard:
			return (signal == "WeaponEquipped" and subject.ID == self.minion.ID) or (signal == "WeaponRemoved" and target.ID == self.minion.ID)
		return False
		
	def trigger(self, signal, ID, subject, target, number, comment, choice=0):
		if self.canTrigger(signal, ID, subject, target, number, comment):
			self.effect(signal, ID, subject, target, number, comment)
			
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.applies(self.minion)
		
	def applies(self, subject):
		if subject.Game.availableWeapon(subject.ID) != None:
			print("Southsea Deckhand gains Charge due to presence of friendly weapon")
			aura_Receiver = HasAura_Receiver(subject, self, "Charge")
			aura_Receiver.effectStart()
		else:
			print("Southsea Deckhand loses Charge due to absence of friendly weapon")
			for minion, aura_Receiver in self.auraAffected:
				aura_Receiver.effectClear()
				
	def auraAppears(self):
		self.applies(self.minion)
		self.minion.Game.triggersonBoard[self.minion.ID].append((self, "WeaponEquipped"))
		self.minion.Game.triggersonBoard[self.minion.ID].append((self, "WeaponRemoved"))
		
	def auraDisappears(self):
		for minion, aura_Receiver in self.auraAffected:
			aura_Receiver.effectClear()
			
		self.auraAffected = []
		extractfrom((self, "WeaponEquipped"), self.minion.Game.triggersonBoard[self.minion.ID])
		extractfrom((self, "WeaponRemoved"), self.minion.Game.triggersonBoard[self.minion.ID])
		
class WorgenInfiltrator(Minion):
	Class, race, name = "Neutral", "", "Worgen Infiltrator"
	mana, attack, health = 1, 2, 1
	index = "Classic-Neutral-1-2-1-Minion-None-Worgen Infiltrator-Stealth"
	needTarget, keyWord, description = False, "Stealth", "Stealth"
	
	
class YoungDragonhawk(Minion):
	Class, race, name = "Neutral", "Beast", "Young Dragonhawk"
	mana, attack, health = 1, 1, 1
	index = "Classic-Neutral-1-1-1-Minion-Beast-Young Dragonhawk-Windfury"
	needTarget, keyWord, description = False, "Windfury", "Windfury"
	
	
class YoungPriestess(Minion):
	Class, race, name = "Neutral", "", "Young Priestess"
	mana, attack, health = 1, 2, 1
	index = "Classic-Neutral-1-2-1-Minion-None-Young Priestess"
	needTarget, keyWord, description = False, "", "At the end of your turn, give another random friendly minion +1 Health"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_YoungPriestess(self)]
		
class Trigger_YoungPriestess(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["TurnEnds"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		print("The turn ends for player %d, and this minion has ID"%ID, self.entity.ID)
		return self.entity.onBoard and ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		targets = self.entity.Game.minionsonBoard(self.entity.ID)
		extractfrom(self.entity, targets)
		if targets != []:
			target = np.random.choice(targets)
			print("At the end of turn, %s gvies another random friendly minion %s +1 Health."%(self.entity.name, target.name))
			target.buffDebuff(0, 1)
			
"""mana 2 minions"""
class AmaniBerserker(Minion):
	Class, race, name = "Neutral", "", "Amani Berserker"
	mana, attack, health = 2, 2, 3
	index = "Classic-Neutral-2-2-3-Minion-None-Amani Berserker"
	needTarget, keyWord, description = False, "", "Has +3 Attack while damaged"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggers["StatChanges"] = [self.handleEnrage]
		self.activated = False
		
	def handleEnrage(self):
		if self.silenced == False and self.onBoard:
			if self.activated == False and self.health < self.health_upper:
				self.activated = True
				self.statChange(3, 0)
			elif self.activated and self.health >= self.health_upper:
				self.activated = False
				self.statChange(-3, 0)
				
				
class AncientWatcher(Minion):
	Class, race, name = "Neutral", "", "Ancient Watcher"
	mana, attack, health = 2, 4, 5
	index = "Classic-Neutral-2-4-5-Minion-None-Ancient Watcher"
	needTarget, keyWord, description = False, "", "Can't Attack"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.marks["Can't Attack"] = 1
		
		
class BloodmageThalnos(Minion):
	Class, race, name = "Neutral", "", "Bloodmage Thalnos"
	mana, attack, health = 2, 1, 1
	index = "Classic-Neutral-2-1-1-Minion-None-Bloodmage Thalnos-Deathrattle-Spell Damage-Legendary"
	needTarget, keyWord, description = False, "Spell Damage", "Spell Damage +1. Deathrattle: Draw a card"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [DrawaCard(self)]
		
class DrawaCard(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("Deathrattle: Draw a card triggers.")
		self.entity.Game.Hand_Deck.drawCard(self.entity.ID)
		
		
class BloodsailRaider(Minion):
	Class, race, name = "Neutral", "Pirate", "Bloodsail Raider"
	mana, attack, health = 2, 2, 3
	index = "Classic-Neutral-2-2-3-Minion-Pirate-Bloodsail Raider-Battlecry"
	needTarget, keyWord, description = False, "", "Battlecry: Gain Attack equal to the Attack of your weapon"
	
	def whenEffective(self, target=None, comment="", choice=0):
		weapon = self.Game.availableWeapon(self.ID)
		if weapon != None:
			print("Bloodsail Raider's battlecry lets minion gain the Attack equal to the Attack of player's weapon.")
			self.buffDebuff(weapon.attack, 0)
		return self, None
		
		
class CrazedAlchemist(Minion):
	Class, race, name = "Neutral", "", "Crazed Alchemist"
	mana, attack, health = 2, 2, 2
	index = "Classic-Neutral-2-2-2-Minion-None-Crazed Alchemist-Battlecry"
	needTarget, keyWord, description = True, "", "Battlecry: Swap the Attack and Health of a minion"
	
	def targetExists(self, choice=0):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target != self and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			print("Crazed Alchemist's battlecry swaps minion %s's attack/health."%target.name)
			target.statReset(target.health, target.attack)
		return self, target
		
		
class DireWolfAlpha(Minion):
	Class, race, name = "Neutral", "Beast", "Dire Wolf Alpha"
	mana, attack, health = 2, 2, 2
	index = "Classic-Neutral-2-2-2-Minion-Beast-Dire Wolf Alpha"
	needTarget, keyWord, description = False, "", "Adjacent minions have +1 Attack"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.auras["Buff Aura"] = BuffAura_Dealer_Adjacent(self, None, 1, 0)
		
		
class Doomsayer(Minion):
	Class, race, name = "Neutral", "", "Doomsayer"
	mana, attack, health = 2, 0, 7
	index = "Classic-Neutral-2-0-7-Minion-None-Doomsayer"
	needTarget, keyWord, description = False, "", "At the start of your turn, destroy ALL minions"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_Doomsayer(self)]
		
class Trigger_Doomsayer(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["TurnStarts"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("At the start of turn, %s destroys all minions"%self.entity.name)
		for minion in self.entity.Game.minionsonBoard(1) + self.entity.Game.minionsonBoard(2):
			minion.dead = True
			
			
class FaerieDragon(Minion):
	Class, race, name = "Neutral", "Dragon", "Faerie Dragon"
	mana, attack, health = 2, 3, 2
	index = "Classic-Neutral-2-3-2-Minion-Dragon-Faerie Dragon"
	needTarget, keyWord, description = False, "", "Can't be targeted by spells or Hero Powers"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.marks["Evasive"] = 1
		
		
#For a target spell/battlecry, if the above resolution kills the minion before it can take effect, the targeting part is simply wasted and 
#the following effect will still trigger.
#For example, if the minion before Mortal Coil is cast on it. The Mortal Coil still lets player draw a card.
#Another example, if the spell is Dire Frenzy, there will still be 3 copes to be shuffled..
class KnifeJuggler(Minion):
	Class, race, name = "Neutral", "", "Knife Juggler"
	mana, attack, health = 2, 2, 2
	index = "Classic-Neutral-2-2-2-Minion-None-Knife Juggler"
	needTarget, keyWord, description = False, "", "After you summon a minion, deal 1 damage to a random enemy"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_KnifeJuggler(self)]
		
class Trigger_KnifeJuggler(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionBeenSummoned"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject.ID == self.entity.ID and subject != self.entity
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		targets = [self.entity.Game.heroes[3-self.entity.ID]]
		for minion in self.entity.Game.minionsonBoard(3-self.entity.ID):
			if minion.health > 0 and minion.dead == False:
				targets.append(minion)
				
		target = np.random.choice(targets)
		print("A friendly minion %s is summoned and %s deals 1 damage to random enemy"%(subject.name, self.entity.name), target.name)
		self.entity.dealsDamage(target, 1)
		
		
class LootHoarder(Minion):
	Class, race, name = "Neutral", "", "Loot Hoarder"
	mana, attack, health = 2, 2, 1
	index = "Classic-Neutral-2-2-1-Minion-None-Loot Hoarder-Deathrattle"
	needTarget, keyWord, description = False, "", "Deathrattle: Draw a card"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [DrawaCard(self)] #This deathrattle obj defined in Bloodmage Thalnos.
		
		
class LorewalkerCho(Minion):
	Class, race, name = "Neutral", "", "Lorewalker Cho"
	mana, attack, health = 2, 0, 4
	index = "Classic-Neutral-2-0-4-Minion-None-Lorewalker Cho-Legendary"
	needTarget, keyWord = False, ""
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_LorewalkerCho(self)]
		
class Trigger_LorewalkerCho(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["SpellPlayed"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("Spell %s is cast and Lorewalker Cho gives the other player a copy of it"%subject.name)
		card = type(subject)(self.entity.Game, 3-subject.ID)
		self.entity.Game.Hand_Deck.addCardtoHand(card, 3-subject.ID)
		
		
class MadBomber(Minion):
	Class, race, name = "Neutral", "", "Mad Bomber"
	mana, attack, health = 2, 3, 2
	index = "Classic-Neutral-2-3-2-Minion-None-Mad Bomber-Battlecry"
	needTarget, keyWord, description = False, "", "Battlecry: Deal 3 damage randomly split among all other characters"
	
	def randomorDiscover(self):
		return "Random"
		
	def whenEffective(self, target=None, comment="", choice=0):
		print("Mad Bomber's battlecry deals 3 damage randomly split among other characters.")
		for i in range(3):
			targets = [self.Game.heroes[1], self.Game.heroes[2]]
			for minion in self.Game.minionsonBoard(1) + self.Game.minionsonBoard(2):
				if minion.health > 0 and minion.dead == False and minion != self:
					targets.append(minion)
			target = np.random.choice(targets)
			print("Mad Bomber's battlecry deals 1 damage to", target.name)
			self.dealsDamage(target, 1)
		return self, None
		
		
class ManaAddict(Minion):
	Class, race, name = "Neutral", "", "Mana Addict"
	mana, attack, health = 2, 1, 3
	index = "Classic-Neutral-2-1-3-Minion-None-Mana Addict"
	needTarget, keyWord, description = False, "", "Whenever you cast a spell, gain +2 Attack this turn"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_ManaAddict(self)]
		
class Trigger_ManaAddict(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["SpellPlayed"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject.ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("Player casts a spell and Mana Addict gains +2 attack this turn.")
		self.entity.buffDebuff(2, 0, "EndofTurn")
		
		
class ManaWraith(Minion):
	Class, race, name = "Neutral", "", "Mana Wraith"
	mana, attack, health = 2, 2, 2
	index = "Classic-Neutral-2-2-2-Minion-None-Mana Wraith"
	needTarget, keyWord, description = False, "", "ALL minions cost (1) more"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.manaAura = AllMinionsCost1More(self)
		self.appearResponse = [self.activateAura]
		self.disappearResponse = [self.deactivateAura]
		self.silenceResponse = [self.deactivateAura]
		
	def activateAura(self):
		self.Game.ManaHandler.CardAuras.append(self.manaAura)
		print("Mana Wraith's mana aura is included. All minions cost 1 more now.")
		self.Game.ManaHandler.calcMana_All()
		
	def deactivateAura(self):
		extractfrom(self.manaAura, self.Game.ManaHandler.CardAuras)
		print("Mana Wraith's mana aura is removed. All minions cost 1 less now.")
		self.Game.ManaHandler.calcMana_All()
		
class AllMinionsCost1More:
	def __init__(self, minion):
		self.minion = minion
		self.temporary = False
		
	def handleMana(self, target):
		if target.cardType == "Minion":
			target.mana += 1
			
			
class MasterSwordsmith(Minion):
	Class, race, name = "Neutral", "", "Master Swordsmith"
	mana, attack, health = 2, 1, 3
	index = "Classic-Neutral-2-1-3-Minion-None-Master Swordsmith"
	needTarget, keyWord, description = False, "", "At the end of your turn, give another random friendly minion +1 Attack"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_MasterSwordsmith(self)]
		
class Trigger_MasterSwordsmith(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["TurnEnds"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		targets = self.entity.Game.minionsonBoard(self.entity.ID)
		extractfrom(self.entity, targets)
		if targets != []:
			target = np.random.choice(targets)
			print("At the end of turn, %s gives friendly minion %s +1 attack"%(self.entity.name, target.name))
			target.buffDebuff(1, 0)
			
			
class MillhouseManastorm(Minion):
	Class, race, name = "Neutral", "", "Millhouse Manastorm"
	mana, attack, health = 2, 4, 4
	index = "Classic-Neutral-2-4-4-Minion-None-Millhouse Manastorm-Battlecry-Legendary"
	needTarget, keyWord, description = False, "", "Battlecry: Your opponent's spells cost (0) next turn"
	
	def whenEffective(self, target=None, comment="", choice=0):
		print("Millhouse Manastorm's battlecry makes enemy spells cost 0 next turn.")
		self.Game.ManaHandler.CardAuras_Backup.append(SpellsCost0NextTurn(self.Game, 3-self.ID))
		return self, None
		
class SpellsCost0NextTurn(TempManaEffect):
	def __init__(self, Game, ID):
		self.ID = ID
		self.Game = Game
		self.temporary = True
		self.triggersonBoard = []
		
	def handleMana(self, target):
		if target.cardType == "Spell" and target.ID == self.ID:
			target.mana = 0
			
			
class NatPagle(Minion):
	Class, race, name = "Neutral", "", "Nat Pagle"
	mana, attack, health = 2, 0, 4
	index = "Classic-Neutral-2-0-4-Minion-None-Nat Pagle-Legendary"
	needTarget, keyWord, description = False, "", "At the start of your turn, you have a 50% chance to draw an extra card"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_NatPagle(self)]
		
class Trigger_NatPagle(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["TurnStarts"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and ID == self.entity.ID
		
	#不确定纳特帕格是直接让玩家摸一张牌还是确定多摸之后在后续的抽牌阶段摸一张。
	#暂时假设是直接摸一张牌。
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("At the start of turn, Nat Pagle has 50% chance to lets player draw a card.")
		if np.random.randint(2) == 1:
			print("Nat Pagle lets player draw a card.")
			self.entity.Game.Hand_Deck.drawCard(self.entity.ID)
			
			
class PintsizedSummoner(Minion):
	Class, race, name = "Neutral", "", "Pint-sized Summoner"
	mana, attack, health = 2, 2, 2
	index = "Classic-Neutral-2-2-2-Minion-None-Pint-sized Summoner"
	needTarget, keyWord, description = False, "", "The first minion you play each turn costs (1) less"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.manaAura = YourFirstMinionCosts1LessThisTurn(self)
		self.triggersonBoard = [Trigger_PintsizedSummoner(self)]
		self.appearResponse = [self.activateAura]
		self.disappearResponse = [self.deactivateAura]
		self.silenceResponse = [self.deactivateAura]
		
	def activateAura(self):
		print("Pint-sized Summoner lets the first minion played by player cost 1 less.")
		if self.Game.turn == self.ID and self.Game.CounterHandler.numMinionsPlayedThisTurn[self.ID] == 0:
			print("Pint-sized Summoner makes player's first minion this turn cost 1 less.")
			self.Game.ManaHandler.CardAuras.append(self.manaAura)
			self.Game.ManaHandler.calcMana_All()
			
	def deactivateAura(self):
		print("Pint-sized Summoner's mana aura is removed. Player's first minion each turn no longer costs 1 less.")
		extractfrom(self.manaAura, self.Game.ManaHandler.CardAuras)
		self.Game.ManaHandler.calcMana_All()
		
class Trigger_PintsizedSummoner(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["TurnStarts", "ManaCostPaid"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		#不需要响应回合结束，因为光环自身被标记为temporary，会在回合结束时自行消失。
		if signal == "TurnStarts" and self.entity.onBoard and ID == self.entity.ID:
			return True
		if signal == "ManaCostPaid" and self.entity.onBoard and subject.cardType == "Minion" and subject.ID == self.entity.ID:
			return True
		return False
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		if signal == "TurnStarts":
			print("At the start of turn, %s restarts the mana aura and reduces the cost of the first minion by 1."%self.entity.name)
			self.entity.activateAura()
		else: #signal == "ManaCostPaid"
			self.entity.deactivateAura()
			
class YourFirstMinionCosts1LessThisTurn:
	def __init__(self, minion):
		self.minion = minion
		self.temporary = True
		
	def handleMana(self, target):
		if target.cardType == "Minion" and target.ID == self.minion.ID:
			if target.mana > 0:
				target.mana -= 1
			else:
				target.mana = 0
				
	def deactivate(self): #这个函数由Game.ManaHandler来调用，用于回合结束时的费用光环取消。
		extractfrom(self, self.minion.Game.ManaHandler.CardAuras)
		self.minion.Game.ManaHandler.calcMana_All()
		
		
class SunfuryProtector(Minion):
	Class, race, name = "Neutral", "", "Sunfury Protector"
	mana, attack, health = 2, 2, 2
	index = "Classic-Neutral-2-2-3-Minion-None-Sunfury Protector-Battlecry"
	needTarget, keyWord, description = False, "", "Battlecry: Give adjacent minions Taunt"
	
	def whenEffective(self, target=None, comment="", choice=0):
		if self.onBoard: #只有在场的随从拥有相邻随从。
			targets, distribution = self.Game.findAdjacentMinions(self)
			if targets != []:
				print("Sunfury Protector's battlecry gives adjacent friendly minions Taunt.")
				for target in targets:
					target.getsKeyword("Taunt")
		return self, None
		
#Look into Electra Stormsurge and Casting spell on adjacent minions.
class WildPyromancer(Minion):
	Class, race, name = "Neutral", "", "Wild Pyromancer"
	mana, attack, health = 2, 3, 2
	index = "Classic-Neutral-2-3-2-Minion-None-Wild Pyromancer"
	needTarget, keyWord, description = False, "", "After you cast a spell, deal 1 damage to ALL minions"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_WildPyromancer(self)]
		
class Trigger_WildPyromancer(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["SpellBeenPlayed"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject.ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("After player casts a spell, %s deals 1 damage to all minions."%self.entity.name)
		targets = self.entity.Game.minionsonBoard(1) + self.entity.Game.minionsonBoard(2)
		self.entity.dealsAOE(targets, [1 for minion in targets])
		
		
class YouthfulBrewmaster(Minion):
	Class, race, name = "Neutral", "", "Youthful Brewmaster"
	mana, attack, health = 2, 3, 2
	index = "Classic-Neutral-2-3-2-Minion-None-Youthful Brewmaster-Battlecry"
	needTarget, keyWord, description = True, "", "Battlecry: Return a friendly minion from the battlefield to you hand"
	
	def targetExists(self, choice=0):
		return self.selectableFriendlyMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.ID == self.ID and target != self and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None and target.onBoard:
			print("Youthful Brewmaster's battlecry returns friendly minion %s to player's hand."%target.name)
			self.Game.returnMiniontoHand(target)
		return self, target
		
"""mana 3 minions"""
class AcolyteofPain(Minion):
	Class, race, name = "Neutral", "", "Acolyte of Pain"
	mana, attack, health = 3, 1, 3
	index = "Classic-Neutral-3-1-3-Minion-None-Acolyte of Pain"
	needTarget, keyWord, description = False, "", "Whenever this minion takes damage, draw a card"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_AcolyteofPain(self)]
		
class Trigger_AcolyteofPain(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionTakesDamage"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and target == self.entity
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("%s takes damage and lets player draw a card."%self.entity.name)
		self.entity.Game.Hand_Deck.drawCard(self.entity.ID)
		
		
class ArcaneGolem(Minion):
	Class, race, name = "Neutral", "", "Arcane Golem"
	mana, attack, health = 3, 4, 4
	index = "Classic-Neutral-3-4-4-Minion-None-Arcane Golem-Battlecry"
	needTarget, keyWord, description = False, "", "Battlecry: Give your opponent a Mana Crystal"
	
	def whenEffective(self, target=None, comment="", choice=0):
		print("Arcane Golem's battlecry gives opponent 1 mana crystal.")
		self.Game.ManaHandler.gainManaCrystal(1, 3-self.ID)
		return self, None
		
		
class BloodKnight(Minion):
	Class, race, name = "Neutral", "", "Blood Knight"
	mana, attack, health = 3, 3, 3
	index = "Classic-Neutral-3-3-3-Minion-None-Blood Knight-Battlecry"
	needTarget, keyWord, description = False, "", "Battlecry: All minions lose Divine Shield. Gain +3/+3 for each Shield lost"
	#仍视为随从连续两次施放战吼，但是第二次由于各随从的圣盾已经消失，所以可以在每一次战吼触发时检测是否有铜须光环的存在。
	#如果有铜须光环，则每一次战吼触发的时候就获得双倍buff
	def whenEffective(self, target=None, comment="", choice=0):
		num = 0
		for minion in self.Game.minionsonBoard(1) + self.Game.minionsonBoard(2):
			if minion.keyWords["Divine Shield"] > 0:
				minion.losesKeyword("Divine Shield")
				num += 1
				
		if self.Game.playerStatus[self.ID]["Battlecry Trigger Twice"] + self.Game.playerStatus[self.ID]["Shark Battlecry Trigger Twice"] > 0 and comment != "InvokedbyOthers":
			print("Blood Knight's battlecry removes all Divine Shields and minion gains +6/+6 for each.")
			self.buffDebuff(6*num, 6*num)
		else:
			print("Blood Knight's battlecry removes all Divine Shields and minion gains +3/+3 for each.")
			self.buffDebuff(3*num, 3*num)
		return self, None
		
		
class Brightwing(Minion):
	Class, race, name = "Neutral", "Dragon", "Brightwing"
	mana, attack, health = 3, 3, 2
	index = "Classic-Neutral-3-3-2-Minion-Dragon-Brightwing-Battlecry-Legendary"
	needTarget, keyWord, description = False, "", "Battlecry: Add a random Legendary minion to your hand"
	
	def randomorDiscover(self):
		return "RNG"
		
	def whenEffective(self, target=None, comment="", choice=0):
		print("Brightwing's battlecry adds a random Legendary minion to player's hand.")
		if self.Game.Hand_Deck.handNotFull(self.ID):
			self.Game.Hand_Deck.addCardtoHand(np.random.choice(LegendaryMinions), self.ID, comment="CreateUsingType")
		return self, None
		
		
class ColdlightSeer(Minion):
	Class, race, name = "Neutral", "Murloc", "Coldlight Seer"
	mana, attack, health = 3, 2, 3
	index = "Classic-Neutral-3-2-3-Minion-Murloc-Coldlight Seer-Battlecry"
	needTarget, keyWord, description = False, "", "Battlecry: Give your other Murlocs +2 Health"
	
	def whenEffective(self, target=None, comment="", choice=0):
		print("Coldlight Seer's battlecry gives all friendly murlocs +2 health.")
		for minion in self.Game.minionsonBoard(self.ID):
			if "Murloc" in minion.race:
				minion.buffDebuff(0, 2)
		return self, None
		
		
class Demolisher(Minion):
	Class, race, name = "Neutral", "Mech", "Demolisher"
	mana, attack, health = 3, 1, 4
	index = "Classic-Neutral-3-1-4-Minion-Mech-Demolisher"
	needTarget, keyWord, description = False, "", "At the start of your turn, deal 2 damage to a random enemy"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_Demolisher(self)]
		
class Trigger_Demolisher(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["TurnStarts"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		targets = [self.entity.Game.heroes[3-self.entity.ID]]
		for minion in self.entity.Game.minionsonBoard(3-self.entity.ID):
			if minion.health > 0 and minion.dead == False:
				targets.append(minion)
				
		target = np.random.choice(targets)
		print("At the start of turn, %s deals 2 damage to a random enemy"%self.entity.name, target.name)
		self.entity.dealsDamage(target, 2)
		
		
class EarthenRingFarseer(Minion):
	Class, race, name = "Neutral", "", "Earthen Ring Farseer"
	mana, attack, health = 3, 3, 3
	index = "Classic-Neutral-3-3-3-Minion-None-Earthen Ring Farseer-Battlecry"
	needTarget, keyWord, description = True, "", "Battlecry: Restore 3 health"
	
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			heal = 3 * (2 ** self.countHealDouble())
			print("Earthen Ring Farseer's battlecry restores %d health to"%heal, target.name)
			self.restoresHealth(target, heal)
		return self, target
		
		
class EmperorCobra(Minion):
	Class, race, name = "Neutral", "Beast", "Emperor Cobra"
	mana, attack, health = 3, 2, 3
	index = "Classic-Neutral-3-2-3-Minion-Beast-Emperor Cobra-Poisonous"
	needTarget, keyWord, description = False, "Poisonous", "Poisonous"
	
	
class FlesheatingGhoul(Minion):
	Class, race, name = "Neutral", "", "Flesheating Ghoul"
	mana, attack, health = 3, 2, 3
	index = "Classic-Neutral-3-2-3-Minion-None-Flesheating Ghoul"
	needTarget, keyWord, description = False, "", "Whenever a minion dies, gain +1 Attack"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_FlesheatingGhoul(self)]
		
class Trigger_FlesheatingGhoul(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionDies"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and target != self.entity #Technically, minion has to disappear before dies. But just in case.
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("A minion %s dies and %s gains +1 attack."%(target.name, self.entity.name))
		self.entity.buffDebuff(1, 0)
		
		
class HarvestGolem(Minion):
	Class, race, name = "Neutral", "Mech", "Harvest Golem"
	mana, attack, health = 3, 2, 3
	index = "Classic-Neutral-3-2-3-Minion-Mech-Harvest Golem-Deathrattle"
	needTarget, keyWord, description = False, "", "Deathrattle: Summon a 2/1 Damaged Golem"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [SummonaDamagedGolem(self)]
		
class SummonaDamagedGolem(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("Deathrattle: Summon a 2/1 Damaged Golem triggers.")
		self.entity.Game.summonMinion(DamagedGolem(self.entity.Game, self.entity.ID), self.entity.position+1, self.entity.ID)
		
class DamagedGolem(Minion):
	Class, race, name = "Neutral", "Mech", "Damaged Golem"
	mana, attack, health = 1, 2, 1
	index = "Classic-Neutral-1-2-1-Minion-Mech-Damaged Golem-Uncollectible"
	needTarget, keyWord, description = False, "", ""
	
	
class ImpMaster(Minion):
	Class, race, name = "Neutral", "", "Imp Master"
	mana, attack, health = 3, 1, 5
	index = "Classic-Neutral-3-1-5-Minion-None-Imp Master"
	needTarget, keyWord, description = False, "", "At the end of your turn, deal 1 damage to this minion and summon a 1/1 Imp"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_ImpMaster(self)]
		
class Trigger_ImpMaster(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["TurnEnds"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("At the end of turn, %s deals 1 damage to itself and summons a 1/1 Imp."%self.entity.name)
		self.entity.dealsDamage(self.entity, 1)
		self.entity.Game.summonMinion(Imp(self.entity.Game, self.entity.ID), self.entity.position+1, self.entity.ID)
		
class Imp(Minion):
	Class, race, name = "Neutral", "Demon", "Imp"
	mana, attack, health = 1, 1, 1
	index = "Classic-Neutral-1-1-1-Minion-Demon-Imp-Uncollectible"
	needTarget, keyWord, description = False, "", ""
	
	
class InjuredBlademaster(Minion):
	Class, race, name = "Neutral", "", "Injured Blademaster"
	mana, attack, health = 3, 4, 7
	index = "Classic-Neutral-3-4-7-Minion-None-Injured Blademaster-Battlecry"
	needTarget, keyWord, description = False, "", "Battlecry: Deal 4 damage to HIMSELF"
	
	def whenEffective(self, target=None, comment="", choice=0):
		print("Injured Blademaster's battlecry deals 4 damage to the minion.")
		self.dealsDamage(self, 4)
		return self, None
		
		
class IronbeakOwl(Minion):
	Class, race, name = "Neutral", "Beast", "Ironbeak Owl"
	mana, attack, health = 3, 2, 1
	index = "Classic-Neutral-3-2-1-Minion-Beast-Ironbeak Owl-Battlecry"
	needTarget, keyWord, description = True, "", "Battlecry: Silence a minion"
	
	def targetExists(self, choice=0):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target != self and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			print("Ironbeak Owl's battlecry silences minion ", target.name)
			target.getsSilenced()
		return self, target
		
		
class JunglePanther(Minion):
	Class, race, name = "Neutral", "Beast", "Jungle Panther"
	mana, attack, health = 3, 4, 2
	index = "Classic-Neutral-3-4-2-Minion-Beast-Jungle Panther-Stealth"
	needTarget, keyWord, description = False, "Stealth", "Stealth"
	
	
class KingMukla(Minion):
	Class, race, name = "Neutral", "Beast", "King Mukla"
	mana, attack, health = 3, 5, 5
	index = "Classic-Neutral-3-5-5-Minion-Beast-King Mukla-Battlecry-Legendary"
	needTarget, keyWord, description = False, "", "Battlecry: Give your opponent 2 Bananas"
	
	def whenEffective(self, target=None, comment="", choice=0):
		print("King Mukla's battlecry gives opponent two Bananas.")
		if self.Game.Hand_Deck.handNotFull(3-self.ID):
			self.Game.Hand_Deck.addCardtoHand([Banana, Banana], 3-self.ID, comment="CreateUsingType")
		return self, None
		
class Banana(Spell):
	Class, name = "Neutral", "Banana"
	needTarget, mana = True, 1
	index = "Classic-Neutral-1-Spell-Banana-Uncollectible"
	description = "Give a minion +1/+1"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			print("Banana is cast and gives minion %s +1/+1."%target.name)
			target.buffDebuff(1, 1)
		return target
		
		
class MindControlTech(Minion):
	Class, race, name = "Neutral", "", "Mind Control Tech"
	mana, attack, health = 3, 3, 3
	index = "Classic-Neutral-3-3-3-Minion-None-Mind Control Tech-Battlecry"
	needTarget, keyWord, description = False, "", "Battlecry: If your opponent has 4 or more minions, take control of one at random"
	def effectCanTrigger(self):
		return len(self.Game.minionsonBoard(3-self.ID)) > 3
		
	def whenEffective(self, target=None, comment="", choice=0):
		if len(self.Game.minionsonBoard(3-self.ID)) > 3:
			print("Mind Control Tech's battlecry gains control of a random enemy minion.")
			self.Game.minionSwitchSide(np.random.choice(self.Game.minionsonBoard(3-self.ID)))
		return self, None
		
		
class MurlocWarleader(Minion):
	Class, race, name = "Neutral", "Murloc", "Murloc Warleader"
	mana, attack, health = 3, 3, 3
	index = "Classic-Neutral-3-3-3-Minion-Murloc-Murloc Warleader"
	needTarget, keyWord, description = False, "", "Your others Murlocs have +2 Attack"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.auras["Buff Aura"] = BuffAura_Dealer_All(self, self.applicable, 2, 0)
		
	def applicable(self, target):
		return "Murloc" in target.race
		
#Gains +1/+1 before friendly AOE takes effect.
class QuestingAdventurer(Minion):
	Class, race, name = "Neutral", "", "Questing Adventurer"
	mana, attack, health = 3, 2, 2
	index = "Classic-Neutral-3-2-2-Minion-None-Questing Adventurer"
	needTarget, keyWord, description = False, "", "Whenever your play a card, gain +1/+1"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_QuestingAdventurer(self)]
		
class Trigger_QuestingAdventurer(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionPlayed", "SpellPlayed", "WeaponPlayed", "HeroCardPlayed"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject.ID == self.entity.ID and subject != self.entity
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("Player plays a card and %s gains +1/+1."%self.entity.name)
		self.entity.buffDebuff(1, 1)
		
		
class RagingWorgen(Minion):
	Class, race, name = "Neutral", "", "Raging Worgen"
	mana, attack, health = 3, 3, 3
	index = "Classic-Neutral-3-3-3-Minion-None-Raging Worgen"
	needTarget, keyWord, description = False, "", "Has +1 Attack and Windfury while damaged"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggers["StatChanges"] = [self.handleEnrage]
		self.activated = False
		
	def handleEnrage(self):
		if self.silenced == False and self.onBoard:
			if self.activated == False and self.health < self.health_upper:
				self.activated = True
				self.statChange(1, 0)
				self.getsKeyword("Windfury")
			elif self.activated and self.health >= self.health_upper:
				self.activated = False
				self.statChange(-1, 0)
				self.losesKeyword("Windfury")
				
				
class ScarletCrusader(Minion):
	Class, race, name = "Neutral", "", "Scarlet Crusader"
	mana, attack, health = 3, 3, 1
	index = "Classic-Neutral-3-3-1-Minion-None-Scarlet Crusader-Divine Shield"
	needTarget, keyWord, description = False, "Divine Shield", "Divine Shield"
	
	
class SouthseaCaptain(Minion):
	Class, race, name = "Neutral", "Pirate", "Southsea Captain"
	mana, attack, health = 3, 3, 3
	index = "Classic-Neutral-3-3-3-Minion-Pirate-Southsea Captain"
	needTarget, keyWord, description = False, "", "Your other Pirates have +1/+1"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.auras["Buff Aura"] = BuffAura_Dealer_All(self, self.applicable, 1, 1)
		
	def applicable(self, target):
		return "Pirate" in target.race
		
		
class TaurenWarrior(Minion):
	Class, race, name = "Neutral", "", "Tauren Warrior"
	mana, attack, health = 3, 2, 3
	index = "Classic-Neutral-3-2-3-Minion-None-Tauren Warrior-Taunt"
	needTarget, keyWord, description = False, "Taunt", "Taunt. Has +3 attack while damaged"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggers["StatChanges"] = [self.handleEnrage]
		self.activated = False
		
	def handleEnrage(self):
		if self.silenced == False and self.onBoard:
			if self.activated == False and self.health < self.health_upper:
				self.activated = True
				self.statChange(3, 0)
			elif self.activated and self.health >= self.health_upper:
				self.activated = False
				self.statChange(-3, 0)
				
				
class ThrallmarFarseer(Minion):
	Class, race, name = "Neutral", "", "Thrallmar Farseer"
	mana, attack, health = 3, 2, 3
	index = "Classic-Neutral-3-2-3-Minion-None-Thrallmar Farseer-Windfury"
	needTarget, keyWord, description = False, "Windfury", "Windfury"
	
	
class TinkmasterOverspark(Minion):
	Class, race, name = "Neutral", "", "Tinkmaster Overspark"
	mana, attack, health = 3, 3, 3
	index = "Classic-Neutral-3-3-3-Minion-None-Tinkmaster Overspark-Battlecry-Legendary"
	needTarget, keyWord, description = False, "", "Battlecry: Transform another random minion into a 5/5 Devilsaur or 1/1 Squirrel"
	
	def whenEffective(self, target=None, comment="", choice=0):
		print("Tinkmaster Overspark's battlecry transforms a random minion into a 1/1 Squirrel or 5/5 Devilsaur.")
		minions = self.Game.minionsonBoard(1) + self.Game.minionsonBoard(2)
		extractfrom(self, minions)
		if minions != []:
			target = np.random.choice(minions)
			if np.random.randint(2):
				self.Game.transform(target, Devilsaur(self.Game, target.ID))
			else:
				self.Game.transform(target, Squirrel(self.Game, target.ID))
		return self, None
		
class Devilsaur(Minion):
	Class, race, name = "Neutral", "Beast", "Devilsaur"
	mana, attack, health = 5, 5, 5
	index = "Classic-Neutral-5-5-5-Minion-Beast-Devilsaur-Uncollectible"
	needTarget, keyWord, description = False, "", ""
	
class Squirrel(Minion):
	Class, race, name = "Neutral", "Beast", "Squirrel"
	mana, attack, health = 1, 1, 1
	index = "Classic-Neutral-1-1-1-Minion-Beast-Squirrel-Uncollectible"
	needTarget, keyWord, description = False, "", ""
	
"""Mana 4 minion"""
class AncientBrewmaster(Minion):
	Class, race, name = "Neutral", "", "Ancient Brewmaster"
	mana, attack, health = 4, 5, 4
	index = "Classic-Neutral-4-5-4-Minion-None-Ancient Brewmaster-Battlecry"
	needTarget, keyWord, description = True, "", "Battlecry: Return a friendly minion from battlefield to your hand"
	
	def targetExists(self, choice=0):
		return self.selectableFriendlyMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.ID == self.ID and target != self and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None and target.onBoard:
			print("Ancient Brewmaster's battlecry returns friendly minion %s to player's hand."%target.name)
			self.Game.returnMiniontoHand(target)
		return self, target
		
		
class AncientMage(Minion):
	Class, race, name = "Neutral", "", "Ancient Mage"
	mana, attack, health = 4, 2, 5
	index = "Classic-Neutral-4-2-5-Minion-None-Ancient Mage-Battlecry"
	needTarget, keyWord, description = False, "", "Battlecry: Give adjacent minions Spell Damage +1"
	
	def whenEffective(self, target=None, comment="", choice=0):
		if self.onBoard:
			print("Ancient Mage's battlecry gives adjacent friendly minions Spell Damage +1.")
			targets, distribution = self.Game.findAdjacentMinions(self)
			for target in targets:
				target.keyWords["Spell Damage"] += 1
		return self, None
		
#When die from an AOE, no card is drawn.
class CultMaster(Minion):
	Class, race, name = "Neutral", "", "Cult Master"
	mana, attack, health = 4, 4, 2
	index = "Classic-Neutral-4-4-2-Minion-None-Cult Master"
	needTarget, keyWord, description = False, "", "Whenever one of your other minion dies, draw a card"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_CultMaster(self)]
		
class Trigger_CultMaster(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionDies"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and target != self.entity and target.ID == self.entity.ID#Technically, minion has to disappear before dies. But just in case.
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("A friendly minion %s dies and %s lets player draw a card."%(target.name, self.entity.name))
		self.entity.Game.Hand_Deck.drawCard(self.entity.ID)
		
		
class DarkIronDwarf(Minion):
	Class, race, name = "Neutral", "", "Dark Iron Dwarf"
	mana, attack, health = 4, 4, 4
	index = "Classic-Neutral-4-4-4-Minion-None-Dark Iron Dwarf-Battlecry"
	needTarget, keyWord, description = True, "", "Battlecry: Give a minion +2 Attack"
	
	def targetExists(self, choice=0):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target != self and target.onBoard
		
	#手牌中的随从也会受到临时一回合的加攻，回合结束时消失。
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			print("Dard Iron Dwarf's battlecry gives minion %s +2 attack this turn."%target.name)
			target.buffDebuff(2, 0, "EndofTurn")
		return self, target
		
		
class DefenderofArgus(Minion):
	Class, race, name = "Neutral", "", "Defender of Argus"
	mana, attack, health = 4, 2, 3
	index = "Classic-Neutral-4-2-3-Minion-None-Defender of Argus-Battlecry"
	needTarget, keyWord, description = False, "", "Battlecry: Given adjacent minions +1/+1 and Taunt"
	
	def whenEffective(self, target=None, comment="", choice=0):
		if self.onBoard:
			print("Defender of Argus's battlecry gives adjacent friendly minions +1/+1 and Taunt.")
			for minion in self.Game.findAdjacentMinions(self)[0]:
				minion.buffDebuff(1, 1)
				minion.getsKeyword("Taunt")
		return self, None
		
		
class DreadCorsair(Minion):
	Class, race, name = "Neutral", "Pirate", "Dread Corsair"
	mana, attack, health = 4, 3, 3
	index = "Classic-Neutral-4-3-3-Minion-Pirate-Dread Corsair-Taunt"
	needTarget, keyWord, description = False, "Taunt", "Taunt. Costs (1) less per Attack your weapon"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersinHand = [Trigger_DreadCorsair(self)]
		
	def selfManaChange(self):
		weapon = self.Game.availableWeapon(self.ID)
		if weapon != None:
			self.mana -= weapon.attack
			self.mana = max(0, self.mana)
		if self.keyWords["Echo"] > 0 and self.mana < 1:
			self.mana = 1
			
class Trigger_DreadCorsair(TriggerinHand):
	def __init__(self, entity):
		self.blank_init(entity, ["WeaponEquipped", "WeaponRemoved"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.inHand and ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.Game.ManaHandler.calcMana_Single(self.entity)
		
		
class MogushanWarden(Minion):
	Class, race, name = "Neutral", "", "Mogu'shan Warden"
	mana, attack, health = 4, 1, 7
	index = "Classic-Neutral-4-1-7-Minion-None-Mogu'shan Warden-Taunt"
	needTarget, keyWord, description = False, "Taunt", "Taunt"
	
	
class SilvermoonGuardian(Minion):
	Class, race, name = "Neutral", "", "Silvermoon Guardian"
	mana, attack, health = 4, 3, 3
	index = "Classic-Neutral-4-3-3-Minion-None-Silvermoon Guardian-Divine Shield"
	needTarget, keyWord, description = False, "Divine Shield", "Divine Shield"
	
	
class SI7Infiltrator(Minion):
	Class, race, name = "Neutral", "", "SI: 7 Infiltrator"
	mana, attack, health = 4, 5, 4
	index = "Classic-Neutral-4-5-4-Minion-None-SI:7 Infiltrator-Battlecry"
	needTarget, keyWord, description = False, "", "Destroy a random enemy secret"
	
	def whenEffective(self, target=None, comment="", choice=0):
		print("SI:7 Infiltrator's battlecry destroys a random enemy secret.")
		self.Game.SecretHandler.extractSecrets(3-self.ID)
		return self, None
		
		
class Spellbreaker(Minion):
	Class, race, name = "Neutral", "", "Spellbreaker"
	mana, attack, health = 4, 4, 3
	index = "Classic-Neutral-4-4-3-Minion-None-Spellbreaker-Battlecry"
	needTarget, keyWord, description = True, "", "Battlecry: Silence a minion"
	def targetExists(self, choice=0):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target != self and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			print("Spellbreaker's battlecry silences minion ", target.name)
			target.getsSilenced()
		return self, target
		
		
class TwilightDrake(Minion):
	Class, race, name = "Neutral", "Dragon", "Twilight Drake"
	mana, attack, health = 4, 4, 1
	index = "Classic-Neutral-4-4-1-Minion-Dragon-Twilight Drake-Battlecry"
	needTarget, keyWord, description = False, "", "Battlecry: Gain +1 Health for each card in your hand"
	
	def whenEffective(self, target=None, comment="", choice=0):
		num = len(self.Game.Hand_Deck.hands[self.ID])
		print("Twilight Drake's battlecry gives minion +1 health for every card in player's hand.")
		self.buffDebuff(0, num)
		return self, None
		
		
class VioletTeacher(Minion):
	Class, race, name = "Neutral", "", "Violet Teacher"
	mana, attack, health = 4, 3, 5
	index = "Classic-Neutral-4-3-5-Minion-None-Violet Teacher"
	needTarget, keyWord, description = False, "", "Whenever you cast a spell, summon a 1/1 Violet Apperentice"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_VioletTeacher(self)]
		
class Trigger_VioletTeacher(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["SpellPlayed"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject.ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("Player casts a spell and %s summons a 1/1 Violet Apprentice."%self.entity.name)
		self.entity.Game.summonMinion(VioletApprentice(self.entity.Game, self.entity.ID), self.entity.position+1, self.entity.ID)
		
class VioletApprentice(Minion):
	Class, race, name = "Neutral", "", "Violet Apprentice"
	mana, attack, health = 1, 1, 1
	index = "Classic-Neutral-1-1-1-Minion-None-Violet Apprentice-Uncollectible"
	needTarget, keyWord, description = False, "", ""
	
"""Mana 5 minions"""
class Abomination(Minion):
	Class, race, name = "Neutral", "", "Abomination"
	mana, attack, health = 5, 4, 4
	index = "Classic-Neutral-5-4-4-Minion-None-Abomination-Taunt-Deathrattle"
	needTarget, keyWord, description = False, "Taunt", "Taunt. Deathrattle: Deal 2 damage to ALL characters"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [Deal2DamagetoAllCharacters(self)]
		
class Deal2DamagetoAllCharacters(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		targets = [self.entity.Game.heroes[1], self.entity.Game.heroes[2]] + self.entity.Game.minionsonBoard(1) + self.entity.Game.minionsonBoard(2)
		damages = [2 for obj in targets]
		print("Deathrattle: Deal 2 damage to all characters triggers.")
		self.entity.dealsAOE(targets, damages)
		
		
class BigGameHunter(Minion):
	Class, race, name = "Neutral", "", "Big Game Hunter"
	mana, attack, health = 5, 4, 2
	index = "Classic-Neutral-5-4-2-Minion-None-Big Game Hunter-Battlecry"
	needTarget, keyWord, description = True, "", "Battlecry: Destroy a minion with 7 or more Attack"
	
	def targetExists(self, choice=0):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target != self and target.attack > 6 and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			print("Big Game Hunter's battlecry destroys minion %s with 7 or more attack."%target.name)
			self.destroyMinion(target)
		return self, target
		
		
class CaptainGreenskin(Minion):
	Class, race, name = "Neutral", "Pirate", "Captain Greenskin"
	mana, attack, health = 5, 5, 4
	index = "Classic-Neutral-5-5-4-Minion-Pirate-Captain Greenskin-Battlecry-Legendary"
	needTarget, keyWord, description = False, "", "Battlecry: Give your weapon +1/+1"
	
	def whenEffective(self, target=None, comment="", choice=0):
		if self.Game.availableWeapon(self.ID) != None:
			print("Captain Greenskin's battlecry gives player's weapon +1/+1.")
			self.Game.availableWeapon(self.ID).gainStat(1, 1)
		return self, None
		
		
class FacelessManipulator(Minion):
	Class, race, name = "Neutral", "", "Faceless Manipulator"
	mana, attack, health = 5, 3, 3
	index = "Classic-Neutral-5-3-3-Minion-None-Faceless Manipulator-Battlecry"
	needTarget, keyWord, description = True, "", "Battlecry: Choose a minion and become a copy of it"
	
	def targetExists(self, choice=0):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target != self and target.onBoard
		
	#无面上场时，先不变形，正常触发Illidan的召唤，以及飞刀。之后进行判定。如果无面在战吼触发前死亡，则没有变形发生。
	#之后无面开始进行变形，即使被返回到时我方手牌中，在手牌中的无面会变形成为base copy。
	#如果那个目标随从被返回手牌，则变形成base copy
	#Faceless Manipulator can't trigger its battlecry twice.
	#If there is Mayor Noggenfogger randomizing two selections, the minion is already transformed into the first copy
	#Randomizing twice is no different than randomizing only once.
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
		
	#如果自己死亡，不触发战吼。
	#没有死亡的情况下，有一方不在场的话，则变形为base copy（即使自己在手牌中）
	#双方都在场的时候，则自己在场，目标不在场（死亡，回手，进牌库）： base copy
	#自己在场，目标在场： Accurate copy
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None and self.dead == False: #战吼触发时自己不能死亡。
			if self.onBoard:
				if target.onBoard:
					Copy = target.selfCopy(self.ID)
					print("Faceless Manipulator's battlecry transforms minion into a copy of ", target.name)
					print("The new copy has Aura's and trigger:")
					Copy.statusPrint()
					self.Game.transform(self, Copy)
					return Copy, target
				else: #target not on board. This Faceless Manipulator becomes a base copy of it.
					Copy = type(target)(self.Game, self.ID)
					print("Faceless Manipulator's battlecry transforms minion into a base copy of ", target.name)
					self.Game.transform(self, Copy)
					return Copy, target
			elif self.inHand:
				Copy = type(target)(self.Game, self.ID)
				print("Faceless Manipulator's battlecry triggers in hand and transforms minion into a copy of ", target.name)
				self.Game.Hand_Deck.replaceCardinHand(self, Copy)
				return Copy, target
			
		return self, target
			
			
class FenCreeper(Minion):
	Class, race, name = "Neutral", "", "Fen Creeper"
	mana, attack, health = 5, 3, 6
	index = "Classic-Neutral-5-3-6-Minion-None-Fen Creeper-Taunt"
	needTarget, keyWord, description = False, "Taunt", "Taunt"
	
	
class HarrisonJones(Minion):
	Class, race, name = "Neutral", "", "Harrison Jones"
	mana, attack, health = 5, 5, 4
	index = "Classic-Neutral-5-5-4-Minion-None-Harrison Jones-Battlecry-Legendary"
	needTarget, keyWord, description = False, "", "Battlecry: Destroy your opponent's weapon and draw cards equal to its Durability"
	
	def whenEffective(self, target=None, comment="", choice=0):
		weapon = self.Game.availableWeapon(3-self.ID)
		if weapon != None:
			num = weapon.durability
			weapon.destroyed()
			if self.Game.playerStatus[self.ID]["Battlecry Trigger Twice"] + self.Game.playerStatus[self.ID]["Shark Battlecry Trigger Twice"] > 0 and comment != "InvokedbyOthers":
				print("Harrison Jones's battlecry destroys enemy weapon and player draws two cards for each of its durability")
				for i in range(2 * num):
					self.Game.Hand_Deck.drawCard(self.ID)
			else:
				print("Harrison Jones's battlecry destroys enemy weapon and player draws a card for each of its durability")
				for i in range(num):
					self.Game.Hand_Deck.drawCard(self.ID)
		return self, None
		
		
class LeeroyJenkins(Minion):
	Class, race, name = "Neutral", "", "Leeroy Jenkins"
	mana, attack, health = 5, 6, 2
	index = "Classic-Neutral-5-6-2-Minion-None-Leeroy Jenkins-Battlecry-Charge-Legendary"
	needTarget, keyWord, description = False, "Charge", "Charge. Battlecry: Summon two 1/1 Whelps for your opponent"
	
	def whenEffective(self, target=None, comment="", choice=0):
		print("Leeroy Jenkins's battlecry summons two 1/1 Whelps for opponent.")
		self.Game.summonMinion([Whelp(self.Game, 3-self.ID) for i in range(2)], (-1, "totheRightEnd"), self.ID)
		return self, None
		
class Whelp(Minion):
	Class, race, name = "Neutral", "Dragon", "Whelp"
	mana, attack, health = 1, 1, 1
	index = "Classic-Neutral-1-1-1-Minion-Dragon-Whelp-Uncollectible"
	needTarget, keyWord, description = False, "", ""
	
	
class SilverHandKnight(Minion):
	Class, race, name = "Neutral", "", "Silver Hand Knight"
	mana, attack, health = 5, 4, 4
	index = "Classic-Neutral-5-4-4-Minion-None-Silver Hand Knight-Battlecry"
	needTarget, keyWord, description = False, "", "Battlecry: Summon a 2/2 Squire"
	
	def whenEffective(self, target=None, comment="", choice=0):
		print("Silver Hand Knight's battlecry summons a 2/2 Squire.")
		self.Game.summonMinion(Squire(self.Game, self.ID), self.position+1, self.ID)
		return self, None
		
class Squire(Minion):
	Class, race, name = "Neutral", "", "Squire"
	mana, attack, health = 1, 2, 2
	index = "Classic-Neutral-2-2-2-Minion-None-Squire-Uncollectible"
	needTarget, keyWord, description = False, "", ""
	
	
class SpitefulSmith(Minion):
	Class, race, name = "Neutral", "", "Spiteful Smith"
	mana, attack, health = 5, 4, 6
	index = "Classic-Neutral-5-4-6-Minion-None-Spiteful Smith"
	needTarget, keyWord, description = False, "", "Your weapon has +2 Attack while this is damaged"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.auras["Spiteful Smith Aura"] = WeaponBuffAura_SpitefulSmith(self)
		self.triggers["StatChanges"] = [self.handleEnrage]
		self.activated = False
		
	#随从出场时，就会根据是否有受伤来决定是否启动光环。
	#激怒开启，启动光环。激怒消失，关闭光环。
	#如果在激怒状态下被转移控制权，光环经历正常的消失和再启动。
	#如果是在非激怒状态下转移，应该没有任何区别。
	#将这个光环编为Aura_Dealer之后，其消失和转移都由光环的控制来操控。
	def handleEnrage(self):
		if self.silenced == False and self.onBoard:
			if self.activated == False and self.health < self.health_upper:
				self.activated = True
				print("Spiteful Smith becomes enraged and starts WeaponBuffAura")
				#在随从登场之后，当出现激怒之后再次尝试建立光环。应该可以成功。
				self.auras["Spiteful Smith Aura"].auraAppears()
			elif self.activated and self.health >= self.health_upper:
				self.activated = False
				print("Spiteful Smith is no longer enraged and shuts down WeaponBuffAura")
				#随从不再处于激怒状态时，取消光环，无论此时有无武器装备。
				self.auras["Spiteful Smith Aura"].auraDisappears()
				
				
class StampedingKodo(Minion):
	Class, race, name = "Neutral", "Beast", "Stampeding Kodo"
	mana, attack, health = 5, 3, 5
	index = "Classic-Neutral-5-3-5-Minion-Beast-Stampeding Kodo-Battlecry"
	needTarget, keyWord, description = False, "", "Battlecry: Destroy a random enemy minion with 2 or less Attack"
	
	def whenEffective(self, target=None, comment="", choice=0):
		targets = []
		for minion in self.Game.minionsonBoard(3-self.ID):
			if minion.attack < 3 and minion.dead == False:
				targets.append(minion)
				
		if targets != []:
			print("Stampeding Kodo's battlecry destroys a random enemy minion with 2 or less attack.")
			np.random.choice(targets).dead = True
		return self, None
		
		
class StranglethornTiger(Minion):
	Class, race, name = "Neutral", "Beast", "Stranglethorn Tiger"
	mana, attack, health = 5, 5, 5
	index = "Classic-Neutral-5-5-5-Minion-Beast-Stranglethorn Tiger-Stealth"
	needTarget, keyWord, description = False, "Stealth", "Stealth"
	
	
class VentureCoMercenary(Minion):
	Class, race, name = "Neutral", "", "Venture Co. Mercenary"
	mana, attack, health = 5, 7, 6
	index = "Classic-Neutral-5-7-6-Minion-None-Venture Co. Mercenary"
	needTarget, keyWord, description = False, "", "Your minions cost (3) more"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.manaAura = YourMinionsCost3More(self)
		self.appearResponse = [self.activateAura]
		self.disappearResponse = [self.deactivateAura]
		self.silenceResponse = [self.deactivateAura]
		
	def activateAura(self):
		print("Venture Co. Mercenary appears and starts its mana aura. Player's minions now cost 3 more.")
		self.Game.ManaHandler.CardAuras.append(self.manaAura)
		self.Game.ManaHandler.calcMana_All()
		
	def deactivateAura(self):
		print("Venture Co. Mercenary's mana aura is removed. Player's minions now cost 3 less.")
		extractfrom(self.manaAura, self.Game.ManaHandler.CardAuras)
		self.Game.ManaHandler.calcMana_All()
		
class YourMinionsCost3More:
	def __init__(self, minion):
		self.minion = minion
		self.temporary = False
		
	def handleMana(self, target):
		if target.cardType == "Minion" and target.ID == self.minion.ID:
			target.mana += 3
			
"""Mana 6 minions"""
class ArgentCommander(Minion):
	Class, race, name = "Neutral", "", "Argent Commander"
	mana, attack, health = 6, 4, 2
	index = "Classic-Neutral-6-4-2-Minion-None-Argent Commander-Divine Shield-Charge"
	needTarget, keyWord, description = False, "Charge,Divine Shield", "Charge, Divine Shield"
	
	
class CairneBloodhoof(Minion):
	Class, race, name = "Neutral", "", "Cairne Bloodhoof"
	mana, attack, health = 6, 4, 5
	index = "Classic-Neutral-6-4-5-Minion-None-Cairne Bloodhoof-Deathrattle-Legendary"
	needTarget, keyWord, description = False, "", "Deathrattle: Summon a 4/5 Baine Bloodhoof"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [SummonBaineBloodhoof(self)]
		
class SummonBaineBloodhoof(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("Deathrattle: Summone a 4/5 Baine Bloodhoof triggers.")
		self.entity.Game.summonMinion(BaineBloodhoof(self.entity.Game, self.entity.ID), self.entity.position+1, self.entity.ID)
		
class BaineBloodhoof(Minion):
	Class, race, name = "Neutral", "", "Baine Bloodhoof"
	mana, attack, health = 6, 4, 5
	index = "Classic-Neutral-6-4-5-Minion-None-Baine Bloodhoof-Uncollectible-Legendary"
	needTarget, keyWord, description = False, "", ""
	
	
class FrostElemental(Minion):
	Class, race, name = "Neutral", "Elemental", "Frost Elemental"
	mana, attack, health = 6, 5, 5
	index = "Classic-Neutral-6-5-5-Minion-Elemental-Frost Elemental-Battlecry"
	needTarget, keyWord, description = True, "", "Battlecry: Freeze a character"
	
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			print("Frost Elemental's battlecry freezes minion ", target.name)
			target.getsFrozen()
		return self, target
		
		
class GadgetzanAuctioneer(Minion):
	Class, race, name = "Neutral", "", "Gadgetzan Auctioneer"
	mana, attack, health = 6, 4, 4
	index = "Classic-Neutral-6-4-4-Minion-None-Gadgetzan Auctioneer"
	needTarget, keyWord, description = False, "", "Whenever you cast a spell, draw a card"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_GadgetzanAuctioneer(self)]
		
class Trigger_GadgetzanAuctioneer(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["SpellPlayed"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject.ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("Player casts a spell and %s lets player draw a card."%self.entity.name)
		self.entity.Game.Hand_Deck.drawCard(self.entity.ID)
		
		
class Hogger(Minion):
	Class, race, name = "Neutral", "", "Hogger"
	mana, attack, health = 6, 4, 4
	index = "Classic-Neutral-6-4-4-Minion-None-Hogger-Legendary"
	needTarget, keyWord, description = False, "", "At the end of your turn, summon a 2/2 Gnoll with Taunt"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_Hogger(self)]
		
class Trigger_Hogger(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["TurnEnds"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("At the end of turn, %s summons a 2/2 Gnoll with Taunt."%self.entity.name)
		self.entity.Game.summonMinion(Gnoll(self.entity.Game, self.entity.ID), self.entity.position+1, self.entity.ID)
		
class Gnoll(Minion):
	Class, race, name = "Neutral", "", "Gnoll"
	mana, attack, health = 2, 2, 2
	index = "Classic-Neutral-2-2-2-Minion-None-Gnoll-Taunt-Uncollectible"
	needTarget, keyWord, description = False, "Taunt", "Taunt"
	
#Lady Goya can swap a friendly minion with a minion in deck.
#When Illidan and Knife Juggler are present, Lady Goya selects a friendly minion, then before the battlecry triggers,
#the Illidan/KnifeJuggler combo kills Sylvanas, which takes control of the target friendly minion
#Lady Goya's battlecry triggers and can still return the minion to our deck.
#Once battlecry locks on the target, it wants to finish no matter what.
class IllidanStormrage(Minion):
	Class, race, name = "Neutral", "Demon", "Illidan Stormrage"
	mana, attack, health = 6, 7, 5
	index = "Classic-Neutral-6-7-5-Minion-Demon-Illidan Stormrage-Legendary"
	needTarget, keyWord, description = False, "", "Whenever you play a card, summon a 2/1 Flame of Azzinoth"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_IllidanStormrage(self)]
		
class Trigger_IllidanStormrage(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionPlayed", "SpellPlayed", "WeaponPlayed", "HeroCardPlayed"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject.ID == self.entity.ID and subject != self.entity
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("Player plays a card and %s summons a Flame of ."%self.entity.name)
		self.entity.Game.summonMinion(FlameofAzzinoth(self.entity.Game, self.entity.ID), self.entity.position+1, self.entity.ID)		
		
class FlameofAzzinoth(Minion):
	Class, race, name = "Neutral", "Elemental", "Flame of Azzinoth"
	mana, attack, health = 1, 2, 1
	index = "Classic-Neutral-1-2-1-Minion-Elemental-Flame of Azzinoth-Uncollectible"
	needTarget, keyWord, description = False, "", ""
	
	
class PriestessofElune(Minion):
	Class, race, name = "Neutral", "", "Priestess of Elune"
	mana, attack, health = 6, 5, 4
	index = "Classic-Neutral-6-5-4-Minion-None-Priestess of Elune-Battlecry"
	needTarget, keyWord, description = False, "", "Battlecry: Restore 4 health to your hero"
	
	def whenEffective(self, target=None, comment="", choice=0):
		heal = 4 * (2 ** self.countHealDouble())
		print("Priestess of Elune's battlecry restores %d health to player."%heal)
		self.restoresHealth(self.Game.heroes[self.ID], heal)
		return self, None
		
		
class Sunwalker(Minion):
	Class, race, name = "Neutral", "", "Sunwalker"
	mana, attack, health = 6, 4, 5
	index = "Classic-Neutral-6-4-5-Minion-None-Sunwalker-Divine Shield-Taunt"
	needTarget, keyWord, description = False, "Taunt,Divine Shield", "Taunt, Divine Shield"
	
	
class TheBeast(Minion):
	Class, race, name = "Neutral", "Beast", "The Beast"
	mana, attack, health = 6, 9, 7
	index = "Classic-Neutral-6-9-7-Minion-Beast-The Beast-Deathrattle-Legendary"
	needTarget, keyWord, description = False, "", "Deathrattle: Summon a 3/3 Finkle Einhorn for your opponent"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [SummonFinkleEinhornsforOpponent(self)]
		
class SummonFinkleEinhornsforOpponent(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("Deathrattle: Summon a 3/3 Finkle Einhorn for opponent triggers.")
		self.entity.Game.summonMinion(FinkleEinhorn(self.entity.Game, 3-self.entity.ID), -1, self.entity.ID)
		
class FinkleEinhorn(Minion):
	Class, race, name = "Neutral", "", "Finkle Einhorn"
	mana, attack, health = 3, 3, 3
	index = "Classic-Neutral-3-3-3-Minion-None-Finkle Einhorn-Uncollectible-Legendary"
	needTarget, keyWord, description = False, "", ""
	
	
class TheBlackKnight(Minion):
	Class, race, name = "Neutral", "", "The Black Knight"
	mana, attack, health = 6, 4, 5
	index = "Classic-Neutral-6-4-5-Minion-None-The Black Knight-Battlecry-Legendary"
	needTarget, keyWord, description = True, "", "Battlecry: Destroy a minion with Taunt"
	
	def targetExists(self, choice=0):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.keyWords["Taunt"] > 0 and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			print("The Black Knight's battlecry destroys minion %s with Taunt."%target.name)
			self.destroyMinion(target)
		return self, target
		
class WindfuryHarpy(Minion):
	Class, race, name = "Neutral", "", "Windfury Harpy"
	mana, attack, health = 6, 4, 5
	index = "Classic-Neutral-6-4-5-Minion-None-Windfury Harpy-Windfury"
	needTarget, keyWord, description = False, "Windfury", "Windfury"
	
"""Mana 7 minions"""
class BarrensStablehand(Minion):
	Class, race, name = "Neutral", "", "Barrens Stablehand"
	mana, attack, health = 7, 4, 4
	index = "Classic-Neutral-7-4-4-Minion-None-Barrens Stablehand-Battlecry"
	needTarget, keyWord, description = False, "", "Battlecry: Summon a random Beast"
	
	def randomorDiscover(self):
		return "Random"
		
	def whenEffective(self, target=None, comment="", choice=0):
		beasts = list(self.Game.MinionswithRace["Beast"].values())
		print("Barrens Stablehand's battlecry summons a random Beast.")
		self.Game.summonMinion(np.random.choice(beasts)(self.Game, self.ID), self.position+1, self.ID)
		return self, None
		
		
class BaronGeddon(Minion):
	Class, race, name = "Neutral", "Elemental", "Baron Geddon"
	mana, attack, health = 7, 7, 5
	index = "Classic-Neutral-7-7-5-Minion-Elemental-Baron Geddon-Legendary"
	needTarget, keyWord, description = False, "", "At the end of turn, deal 2 damage to ALL other characters"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_BaronGeddon(self)]
		
class Trigger_BaronGeddon(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["TurnEnds"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("At the end of turn, %s deals 2 damage to ALL other characters."%self.entity.name)
		targets = [self.entity.Game.heroes[1], self.entity.Game.heroes[2]] + self.entity.Game.minionsonBoard(1) + self.entity.Game.minionsonBoard(2)
		extractfrom(self.entity, targets)
		self.entity.dealsAOE(targets, [2 for obj in targets])
		
		
class HighInquisitorWhitemane(Minion):
	Class, race, name = "Neutral", "", "High Inquisitor Whitemane"
	mana, attack, health = 7, 6, 8
	index = "Classic-Neutral-7-6-8-Minion-None-High Inquisitor Whitemane-Battlecry-Legendary"
	needTarget, keyWord, description = False, "", "Battlecry: Summon all friendly minions that died this turn"
	
	def whenEffective(self, target=None, comment="", choice=0):
		print("High Inquisitor Whitemane's battlecry summons friendly minions that died this turn.")
		numMinionsDied = len(self.Game.CounterHandler.minionsDiedThisTurn[self.ID])
		numSummon = min(self.Game.spaceonBoard(self.ID), numMinionsDied)
		if numSummon > 0:
			indices = np.random.choice(self.Game.CounterHandler.minionsDiedThisTurn[self.ID], numSummon, replace=False)
			pos = (self.position, "totheRight") if self in self.Game.minions[self.ID] else (-1, "totheRightEnd")
			self.Game.summonMinion([self.Game.cardPool[index](self.Game, self.ID) for index in indices], (self.position, "totheRight"), self.ID)		
		return self, None
		
		
class RavenholdtAssassin(Minion):
	Class, race, name = "Neutral", "", "Ravenholdt Assassin"
	mana, attack, health = 7, 7, 5
	index = "Classic-Neutral-7-7-5-Minion-None-Ravenholdt Assassin-Stealth"
	needTarget, keyWord, description = False, "Stealth", "Stealth"
	
"""Mana 8 Minions"""
class ArcaneDevourer(Minion):
	Class, race, name = "Neutral", "Elemental", "Arcane Devourer"
	mana, attack, health = 8, 5 ,5
	index = "Classic-Neutral-8-5-5-Minion-Elemental-Arcane Devourer"
	needTarget, keyWord, description = False, "", "Whenever you cast a spell, gain +2/+2"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_ArcaneDevourer(self)]
		
class Trigger_ArcaneDevourer(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["SpellPlayed"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject.ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("Player casts a spell and %s gains +2/+2."%self.entity.name)
		self.entity.buffDebuff(2, 2)
		
		
class Gruul(Minion):
	Class, race, name = "Neutral", "", "Gruul"
	mana, attack, health = 8, 7, 7
	index = "Classic-Neutral-8-7-7-Minion-None-Gruul-Legendary"
	needTarget, keyWord, description = False, "", "At the end of each turn, gain +1/+1"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_Gruul(self)]
		
class Trigger_Gruul(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["TurnEnds"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("At the end of each turn, %s gains +1/+1."%self.entity.name)
		self.entity.buffDebuff(1, 1)
		
"""Mana 9 minions"""
class Alexstrasza(Minion):
	Class, race, name = "Neutral", "Dragon", "Alexstrasza"
	mana, attack, health = 9, 8, 8
	index = "Classic-Neutral-9-8-8-Minion-Dragon-Alexstrasza-Battlecry-Legendary"
	needTarget, keyWord, description = True, "", "Battlecry: Set a hero's remaining Health to 15"
	
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Hero" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			print("Alexstrasza's battlecry sets hero %s's health to 15."%target.name)
			if target.health_upper < 15:
				target.health_upper = 15
			target.health = 15
		return self, target
		
		
class Malygos(Minion):
	Class, race, name = "Neutral", "Dragon", "Malygos"
	mana, attack, health = 9, 4, 12
	index = "Classic-Neutral-9-4-12-Minion-Dragon-Malygos-Spell Damage-Legendary"
	needTarget, keyWord, description = False, "", "Spell Damage +5"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.keyWords["Spell Damage"] = 5
		
		
class Nozdormu(Minion):
	Class, race, name = "Neutral", "Dragon", "Nozdormu"
	mana, attack, health = 9, 8, 8
	index = "Classic-Neutral-9-8-8-Minion-Dragon-Nozdormu-Legendary"
	needTarget, keyWord, description = False, "", ""
	
	
class Onyxia(Minion):
	Class, race, name = "Neutral", "Dragon", "Onyxia"
	mana, attack, health = 9, 8, 8
	index = "Classic-Neutral-9-8-8-Minion-Dragon-Onyxia-Battlecry-Legendary"
	needTarget, keyWord, description = False, "", "Battlecry: Summon 1/1 Whelps until your side of the battlefield is full"
	
	def whenEffective(self, target=None, comment="", choice=0):
		print("Onyxia's battlecry fills the board with 1/1 Whelps.")
		if self.onBoard:
			self.Game.summonMinion([Whelp(self.Game, self.ID) for i in range(6)], (self.position, "leftandRight"), self.ID)
		else:
			self.Game.summonMinion([Whelp(self.Game, self.ID) for i in range(7)], (-1, "totheRightEnd"), self.ID)
		return self, None
		
		
class Ysera(Minion):
	Class, race, name = "Neutral", "Dragon", "Ysera"
	mana, attack, health = 9, 4, 12
	index = "Classic-Neutral-9-4-12-Minion-Dragon-Ysera-Legendary"
	needTarget, keyWord, description = False, "", "At the end of your turn, add a Dream Card to your hand"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_Ysera(self)]
		
class Trigger_Ysera(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["TurnEnds"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("At the end of turn, %s adds a Dream Card into player's hand."%self.entity.name)
		card = np.random.choice([Dream, Nightmare, YseraAwakens, LaughingSister, EmeraldDrake])
		self.entity.Game.Hand_Deck.addCardtoHand(card, self.entity.ID, "CreateUsingType")
		
class Dream(Spell):
	Class, name = "DreamCard", "Dream"
	needTarget, mana = True, 0
	index = "Classic-DreamCard-0-Spell-Dream-Uncollectible"
	description = "Return a minion to its owner's hand"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			print("Dream is cast and returns minion %s to its owner's hand."%target.name)
			self.Game.returnMiniontoHand(target)
		return target
		
class Nightmare(Spell):
	Class, name = "DreamCard", "Nightmare"
	needTarget, mana = True, 0
	index = "Classic-DreamCard-0-Spell-Nightmare-Uncollectible"
	description = "Give a minion +5/+5. At the start of your next turn, destroy it."
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None and target.onBoard:
			print("Nightmare is cast and gives minion %s +5/+5. It dies at the start of player's turn."%target.name)
			target.buffDebuff(5, 5)
			trigger = Trigger_Corruption(target)
			trigger.ID = self.ID
			target.triggersonBoard.append(trigger)
			trigger.connect()
		return target
		
class YseraAwakens(Spell):
	Class, name = "DreamCard", "Ysera Awakens"
	needTarget, mana = False, 2
	index = "Classic-DreamCard-2-Spell-Ysera Awakens-Uncollectible"
	description = "Deal 5 damage to all characters except Ysera"
	def whenEffective(self, target=None, comment="", choice=0):
		damage = (5 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		print("Ysera Awakens is cast and deals %d damage to all characters except Ysera."%damage)
		targets = [self.Game.heroes[1], self.Game.heroes[2]]
		for minion in self.Game.minionsonBoard(1) + self.Game.minionsonBoard(2):
			if minion.name != "Ysera" or minion.name != "Ysera, Unleashed":
				targets.append(minion)
				
		self.dealsAOE(targets, [damage for obj in targets])
		return None
		
class LaughingSister(Minion):
	Class, race, name = "DreamCard", "", "Laughing Sister"
	mana, attack, health = 3, 3, 5
	index = "Classic-DreamCard-3-3-5-Minion-None-Laughing Sister-Uncollectible"
	needTarget, keyWord, description = False, "", "Can't targeted by spells or Hero Powers"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.marks["Evasive"] = 1
		
class EmeraldDrake(Minion):
	Class, race, name = "DreamCard", "Dragon", "Emerald Drake"
	mana, attack, health = 4, 7, 6
	index = "Classic-DreamCard-4-7-6-Minion-Dragon-Emerald Drake-Uncollectible"
	needTarget, keyWord, description = False, "", ""
	
"""Mana 10 minions"""
class Deathwing(Minion):
	Class, race, name = "Neutral", "Dragon", "Deathwing"
	mana, attack, health = 10, 12, 12
	index = "Classic-Neutral-10-12-12-Minion-Dragon-Deathwing-Battlecry-Legendary"
	needTarget, keyWord, description = False, "", "Battlecry: Destroy all other minions and discard your hands"
	
	def whenEffective(self, target=None, comment="", choice=0):
		print("Deahtwing's battlecry destroys all other minions and discard all of player's hand.")
		for minion in self.Game.minionsonBoard(1) + self.Game.minionsonBoard(2):
			if minion != self:
				minion.dead = True
		self.Game.Hand_Deck.discardCard(self.ID, card=None, discardAll=True)
		return self, None
		
		
class SeaGiant(Minion):
	Class, race, name = "Neutral", "", "Sea Giant"
	mana, attack, health = 10, 8, 8
	index = "Classic-Neutral-10-8-8-Minion-None-Sea Giant"
	needTarget, keyWord, description = False, "", "Costs (1) less for each other minion on the battlefield"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersinHand = [Trigger_SeaGiant(self)]
		
	def selfManaChange(self):
		num = len(self.Game.minionsonBoard(1)) + len(self.Game.minionsonBoard(2))
		print("Sea Giant reduces its own cost by", num)
		self.mana -= num
		self.mana = max(0, self.mana)
		if self.keyWords["Echo"] > 0 and self.mana < 1:
			self.mana = 1
			
class Trigger_SeaGiant(TriggerinHand):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionAppears", "MinionDisappears"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.inHand
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.Game.ManaHandler.calcMana_Single(self.entity)
		
"""Mana 12 minions"""
class MountainGiant(Minion):
	Class, race, name = "Neutral", "Elemental", "Mountain Giant"
	mana, attack, health = 12, 8, 8
	index = "Classic-Neutral-12-8-8-Minion-Elemental-Mountain Giant"
	needTarget, keyWord, description = False, "", "Costs (1) less for each other card in your hand"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersinHand = [Trigger_MountainGiant(self)]
		
	def selfManaChange(self):
		manaReduction = len(self.Game.Hand_Deck.hands[self.ID]) - 1
		print("Mountain Giant reduces its own cost by (%d)"%manaReduction)
		self.mana -= manaReduction
		self.mana = max(0, self.mana)
		if self.keyWords["Echo"] > 0 and self.mana < 1:
			self.mana = 1
			
class Trigger_MountainGiant(TriggerinHand):
	def __init__(self, entity):
		self.blank_init(entity, ["CardLeavesHand", "CardEntersHand"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.inHand and target.ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.Game.ManaHandler.calcMana_Single(self.entity)
		
		
		
"""Druid Cards"""
class Savagery(Spell):
	Class, name = "Druid", "Savagery"
	needTarget, mana = True, 1
	index = "Classic-Druid-1-Spell-Savagery"
	description = "Deal equal to your hero's Attack to a minion"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			damage = (self.Game.heroes[self.ID].attack + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			print("Savagery is cast and deals %d damage to minion "%damage, target.name)
			self.dealsDamage(target, damage)
		return target
		
		
class PoweroftheWild(Spell):
	Class, name = "Druid", "Power of the Wild"
	needTarget, mana = False, 2
	index = "Classic-Druid-2-Spell-Power of the Wild-Choose One"
	description = "Choose One- Give your minions +1/+1; or Summon a 3/2 Panther"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.chooseOne = 1
		self.options = [LeaderofthePack_Option(), SummonaPanther_Option(self)]
	#needTarget() always returns False
	def whenEffective(self, target=None, comment="", choice=0):
		if choice == "ChooseBoth" or choice == 1:
			print("Power of the Wild summons a 3/2 Panther.")
			self.Game.summonMinion(Panther(self.Game, self.ID), -1, self.ID)
		if choice == "ChooseBoth" or choice == 0:
			print("Power of the Wild gives all friendly minions +1/+1.")
			for minion in self.Game.minionsonBoard(self.ID):
				minion.buffDebuff(1, 1)
		return None
		
class LeaderofthePack_Option:
	def __init__(self):
		self.name = "Leader of the Pack"
		self.description = "+1/+1"
		self.index = "Classic-Druid-2-Spell-Leader of the Pack-Uncollectible"
		
	def available(self):
		return True
		
class SummonaPanther_Option:
	def __init__(self, spell):
		self.spell = spell
		self.name = "Summon a Panther"
		self.description = "Summon Panther"
		self.index = "Classic-Druid-2-Spell-Summon a Panther-Uncollectible"
		
	def available(self):
		return self.spell.Game.spaceonBoard(self.pell.ID) > 0
		
class LeaderofthePack(Spell):
	Class, name = "Druid", "Leader of the Pack"
	needTarget, mana = False, 2
	index = "Classic-Druid-2-Spell-Leader of the Pack-Uncollectible"
	description = "Give your minions +1/+1"
	def available(self):
		return True
		
	def whenEffective(self, target=None, comment="", choice=0):
		print("Leader of the Pack is cast and gives friendly minions +1/+1.")
		for minion in self.Game.minionsonBoard(self.ID):
			minion.buffDebuff(1, 1)
		return None
		
class SummonaPanther(Spell):
	Class, name = "Druid", "Summon a Panther"
	needTarget, mana = False, 2
	index = "Classic-Druid-2-Spell-Summon a Panther-Uncollectible"
	description = "Summon a 3/2 Panther"
	def available(self):
		return self.Game.spaceonBoard(self.ID) > 0
		
	def whenEffective(self, target=None, comment="", choice=0):
		print("Summon a Panther is cast and summons a 3/2 Panther")
		self.Game.summonMinion(Panther(self.Game, self.ID), -1, self.ID)
		return None
		
class Panther(Minion):
	Class, race, name = "Druid", "Beast", "Panther"
	mana, attack, health = 2, 3, 2
	index = "Classic-Druid-2-3-2-Minion-Beast-Panther-Uncollectible"
	needTarget, keyWord, description = False, "", ""
	
	
class Wrath(Spell):
	Class, name = "Druid", "Wrath"
	needTarget, mana = True, 2
	index = "Classic-Druid-2-Spell-Wrath-Choose One"
	description = "Choose One- Deal 3 damage to a minion; or Deal 1 damage and draw a card"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.chooseOne = 1
		self.options = [SolarWrath_Option(self), NaturesWrath_Option(self)]
		
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			damage_3 = (3 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			damage_1 = (1 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			if choice == "ChooseBoth" or choice == 0:
				print("Wrath deals %d damage to minion "%damage_3, target.name)
				self.dealsDamage(target, damage_3)
			if choice == "ChooseBoth" or choice == 1:
				print("Wrath deals %d damage to minion %s and lets player draw a card."%(damage_1, target.name))
				self.dealsDamage(target, damage_1)
				self.Game.Hand_Deck.drawCard(self.ID)
		return target
		
class SolarWrath_Option:
	def __init__(self, spell):
		self.spell = spell
		self.name = "Solar Wrath"
		self.description = "3 damage"
		self.index = "Classic-Druid-2-Spell-Solar Wrath-Uncollectible"
		
	def available(self):
		return self.spell.selectableMinionExists(0)
		
class NaturesWrath_Option:
	def __init__(self, spell):
		self.spell = spell
		self.name = "Nature's Wrath"
		self.description = "1 damage. Draw card."
		self.index = "Classic-Druid-2-Spell-Nature's Wrath-Uncollectible"
		
	def available(self):
		return self.spell.selectableMinionExists(1)
		
class SolarWrath(Spell):
	Class, name = "Druid", "Solar Wrath"
	needTarget, mana = True, 2
	index = "Classic-Druid-2-Spell-Solar Wrath-Uncollectible"
	description = "Deal 3 damage to a minion"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0):
		damage = (3 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		print("Solar Wrath is cast and deals %d damage to minion "%damage, target.name)
		self.dealsDamage(target, damage)
		return target
		
class NaturesWrath(Spell):
	Class, name = "Druid", "Nature's Wrath"
	needTarget, mana = True, 2
	index = "Classic-Druid-2-Spell-Nature's Wrath-Uncollectible"
	description = "Deal 1 damage to a minion. Draw a card"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0):
		damage = (1 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		print("Nature's Wrath is cast, deals %d damage to minion %s and lets player draw a card."%(damage, target.name))
		self.dealsDamage(target, damage)
		self.Game.Hand_Deck.drawCard(self.ID)
		return target
		
class MarkofNature(Spell):
	Class, name = "Druid", "Mark of Nature"
	needTarget, mana = True, 3
	index = "Classic-Druid-3-Spell-Mark of Nature-Choose One"
	description = "Choose One- Give a minion +4 Attack; or +4 Health and Taunt"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.chooseOne = 1
		self.options = [TigersFury_Option(self), ThickHide_Option(self)]
		
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			if choice == "ChooseBoth" or choice == 0:
				print("Mark of Nature gives minion %s +4 attack."%target.name)
				target.buffDebuff(4, 0)
			if choice == "ChooseBoth" or choice == 1:
				print("Mark of Nature gives minion %s +4 health and Taunt."%target.name)
				target.buffDebuff(0, 4)
				target.getsKeyword("Taunt")
		return target
		
class TigersFury_Option:
	def __init__(self, spell):
		self.spell = spell
		self.name = "Tiger's Fury"
		self.description = "+4 attack"
		self.index = "Classic-Druid-3-Spell-Tiger's Fury-Uncollectible"
		
	def available(self):
		return self.spell.selectableMinionExists(0)
		
class ThickHide_Option:
	def __init__(self, spell):
		self.spell = spell
		self.name = "Thick Hide"
		self.description = "+4 Health and Taunt"
		self.index = "Classic-Druid-3-Spell-Thick Hide-Uncollectible"
		
	def available(self):
		return self.spell.selectableMinionExists(1)
		
class TigersFury(Spell):
	Class, name = "Druid", "Tiger's Fury"
	needTarget, mana = True, 3
	index = "Classic-Druid-3-Spell-Tiger's Fury-Uncollectible"
	description = "Give a minion +4 Attack"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0):
		print("Tiger's Fury is cast and gives minion %s +4 attack."%target.name)
		target.buffDebuff(4, 0)
		return target
		
class ThickHide(Spell):
	Class, name = "Druid", "Thick Hide"
	needTarget, mana = True, 3
	index = "Classic-Druid-3-Spell-Thick Hide-Uncollectible"
	description = "Give a minion +4 Health and Taunt"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0):
		print("Thick Hide is cast and gives minion %s +4 health and Taunt."%target.name)
		target.buffDebuff(0, 4)
		target.getsKeyword("Taunt")
		return target
		
		
class Bite(Spell):
	Class, name = "Druid", "Bite"
	needTarget, mana = False, 4
	index = "Classic-Druid-4-Spell-Bite"
	description = "Give your hero +4 Attack this turn. Gain 4 Armor"
	def whenEffective(self, target=None, comment="", choice=0):
		print("Bite is cast and gives player +4 armor and +4 attack this turn.")
		self.Game.heroes[self.ID].gainTempAttack(4)
		self.Game.heroes[self.ID].gainsArmor(4)
		return None
		
		
class KeeperoftheGrove(Minion):
	Class, race, name = "Druid", "", "Keeper of the Grove"
	mana, attack, health = 4, 2, 2
	index = "Classic-Druid-4-2-2-Minion-None-Keeper of the Grove-Choose One"
	needTarget, keyWord, description = True, "", "Choose One- Deal 2 damage; or Silence a minion"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.chooseOne = 1
		self.options = [Moonfire_Option(), Dispel_Option(self)]
		
	def targetExists(self, choice=0):
		if choice == "ChooseBoth" or choice == 0: #Deal 2 damage
			return self.selectableCharacterExists(choice)
		else:
			return self.selectableMinionExists()
			
	def targetCorrect(self, target, choice=0):
		if choice == "ChooseBoth" or choice == 0:
			if (target.cardType == "Minion" or target.cardType == "Hero") and target.onBoard:
				return True
		else:
			if target.cardType == "Minion" and target.onBoard:
				return True
		return False
		
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			if (choice == "ChooseBoth" or choice == 1) and target.cardType == "Minion":
				print("Keeper of the Grove silences minion ", target.name)
				target.getsSilenced()
			if choice == "ChooseBoth" or choice == 0:
				print("Keeper of the Grove deals 2 damage to ", target.name)
				self.dealsDamage(target, 2)
		return self, target
		
#Deals 2 damage
class Moonfire_Option:
	def __init__(self):
		self.name = "Moonfire"
		self.description = "2 damage"
		
	def available(self):
		return True
		
#Silences a minion.
class Dispel_Option:
	def __init__(self, minion):
		self.minion = minion
		self.name = "Dispel"
		self.description = "Silence"
		
	def available(self):
		return self.minion.selectableMinionExists(1)
		
class SouloftheForest(Spell):
	Class, name = "Druid", "Soul of the Forest"
	needTarget, mana = False, 4
	index = "Classic-Druid-4-Spell-Soul of the Forest"
	description = "Give your minions 'Deathrattle: Summon a 2/2 Treant'"
	def available(self):
		return self.Game.minionsonBoard(self.ID) != []
		
	def whenEffective(self, target=None, comment="", choice=0):
		print("Soul of the Forest is cast and gives all friendly minions Deathrattle: Summon a 2/2 Treant.")
		for minion in self.Game.minionsonBoard(self.ID):
			trigger = SummonaTreant(minion)
			minion.deathrattles.append(trigger)
			trigger.connect()
		return None
		
class SummonaTreant(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		#This Deathrattle can't possibly be triggered in hand
		print("Deathrattle: Resummon a 2/2 Treant triggers.")
		self.entity.Game.summonMinion(Treant_SoulofForest(self.entity.Game, self.entity.ID), self.entity.position+1, self.entity.ID)
		
class Treant_SoulofForest(Minion):
	Class, race, name = "Druid", "", "Treant"
	mana, attack, health = 2, 2, 2
	index = "Classic-Druid-2-2-2-Minion-None-Treant Soul of Forest-Uncollectible"
	needTarget, keyWord, description = False, "", ""
	
	
class DruidoftheClaw(Minion):
	Class, race, name = "Druid", "", "Druid of the Claw"
	mana, attack, health = 5, 4, 4
	index = "Classic-Druid-5-4-4-Minion-None-Druid of the Claw-Choose One"
	needTarget, keyWord, description = False, "", "Choose One- Transform into a 4/4 with Charge; or a 4/6 with Taunt"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.chooseOne = 1
		self.options = [CatForm_Option(), BearForm_Option()]
		
	def played(self, target=None, choice=0, mana=0, comment=""):
		self.statReset(self.attack_Enchant, self.health_Enchant)
		self.appears()
		if choice == "ChooseBoth":
			minion = DruidoftheClaw_Both(self.Game, self.ID)
		elif choice == 0:
			minion = DruidoftheClaw_Charge(self.Game, self.ID)
		else:
			minion = DruidoftheClaw_Taunt(self.Game, self.ID)
		#抉择变形类随从的入场后立刻变形。
		self.Game.transform(self, minion)
		self.Game.sendSignal("MinionPlayed", self.ID, minion, None, mana, "", choice)
		self.Game.sendSignal("MinionSummoned", self.ID, minion, None, mana, "")
		self.Game.gathertheDead()
		if minion != None and minion.onBoard:
			self.Game.sendSignal("MinionBeenSummoned", self.ID, minion, None, mana, "")
			
		return minion
		
class CatForm_Option:
	def __init__(self):
		self.name = "Cat Form"
		self.description = "Charge"
		
	def available(self):
		return True
		
class BearForm_Option:
	def __init__(self):
		self.name = "Bear Form"
		self.description = "+4 health and Taunt"
		
	def available(self):
		return True
		
class DruidoftheClaw_Charge(Minion):
	Class, race, name = "Druid", "Beast", "Druid of the Claw"
	mana, attack, health = 5, 4, 4
	index = "Classic-Druid-5-4-4-Minion-Beast-Druid of the Claw-Charge-Uncollectible"
	needTarget, keyWord, description = False, "Charge", "Charge"
	
class DruidoftheClaw_Taunt(Minion):
	Class, race, name = "Druid", "Beast", "Druid of the Claw"
	mana, attack, health = 5, 4, 6
	index = "Classic-Druid-5-4-6-Minion-Beast-Druid of the Claw-Taunt-Uncollectible" 
	needTarget, keyWord, description = False, "Taunt", "Taunt"
	
class DruidoftheClaw_Both(Minion):
	Class, race, name = "Druid", "Beast", "Druid of the Claw"
	mana, attack, health = 5, 4, 6
	index = "Classic-Druid-5-4-6-Minion-Beast-Druid of the Claw-Taunt-Charge-Uncollectible" 
	needTarget, keyWord, description = False, "Taunt,Charge", "Taunt, Charge"
	
	
class ForceofNature(Spell):
	Class, name = "Druid", "Force of Nature"
	needTarget, mana = False, 5
	index = "Classic-Druid-5-Spell-Force of Nature"
	description = "Summon three 2/2 Treants"
	def available(self):
		return self.Game.spaceonBoard(self.ID) > 0
		
	def whenEffective(self, target=None, comment="", choice=0):
		print("Force of Nature is cast and summons three 2/2 Treants")
		self.Game.summonMinion([Treant_ForceofNature(self.Game, self.ID) for i in range(3)], (-1, "totheRightEnd"), self.ID)
		return None
		
class Treant_ForceofNature(Minion):
	Class, race, name = "Druid", "", "Treant"
	mana, attack, health = 2, 2, 2
	index = "Classic-Druid-2-2-2-Minion-None-Treant Force of Nature-Uncollectible"
	needTarget, keyWord, description = False, "", ""
	
	
class Starfall(Spell):
	Class, name = "Druid", "Starfall"
	needTarget, mana = True, 5
	index = "Classic-Druid-5-Spell-Starfall-Choose One"
	description = "Choose One- Deal 5 damage to a minion; or Deal 2 damage to all enemy minions"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.chooseOne = 1
		self.options = [Starlord_Option(self), StellarDrift_Option()]
		
	def returnTrue(self, choice=0):
		return choice == "ChooseBoth" or choice == 0
		
	def available(self):
		#当场上有全选光环时，变成了一个指向性法术，必须要有一个目标可以施放。
		if self.Game.playerStatus[self.ID]["Choose Both"] > 0:
			return self.selectableMinionExists("ChooseBoth")
		else: #Deal 2 AOE damage.
			return True
			
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0):
		damage_5 = (5 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		damage_2 = (2 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		if choice == "ChooseBoth" or choice == 0:
			if target != None:
				print("Starfall deals %d damage to minion "%damage_5, target.name)
				self.dealsDamage(target, damage_5)
		if choice == "ChooseBoth" or choice == 1:
			print("Starfall deals %d damage to all enemy minions."%damage_2)
			targets = self.Game.minionsonBoard(3-self.ID)
			self.dealsAOE(targets, [damage_2 for minion in targets])	
		return target
		
class Starlord_Option:
	def __init__(self, spell):
		self.spell = spell
		self.name = "Starlord"
		self.description = "5 damage"
		self.index = "Classic-Druid-5-Spell-Starlord-Uncollectible"
		
	def available(self):
		return self.spell.selectableMinionExists(0)
		
class StellarDrift_Option:
	def __init__(self):
		self.name = "Stellar Drift"
		self.description = "2 damage AOE"
		self.index = "Classic-Druid-5-Spell-Stellar Drift-Uncollectible"
		
	def available(self):
		return True
		
class Starlord(Spell):
	Class, name = "Druid", "Starlord"
	needTarget, mana = True, 5
	index = "Classic-Druid-5-Spell-Starlord-Uncollectible"
	description = "Deal 5 damage to a minion"
	def available(self):
		return self.selectableMinionExists(0)
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			damage = (5 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			print("Starlord is cast and deals %d damage to minion "%damage, target.name)
			self.dealsDamage(target, damage)
		return target
		
class StellarDrift(Spell):
	Class, name = "Druid", "Stellar Drift"
	needTarget, mana = False, 5
	index = "Classic-Druid-5-Spell-Stellar Drift-Uncollectible"
	description = "Deal 2 damage to all enemy minions"
	def whenEffective(self, target=None, comment="", choice=0):
		damage = (2 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		print("Stellar Drift is cast and deals %d damage to emeny minions."%damage)
		targets = self.Game.minionsonBoard(3-self.ID)
		self.dealsAOE(targets, [damage for minion in targets])
		return None
		
		
class Nourish(Spell):
	Class, name = "Druid", "Nourish"
	needTarget, mana = False, 6
	index = "Classic-Druid-6-Spell-Nourish-Choose One"
	description = "Choose One- Gain 2 Mana Crystals; or Draw 3 cards"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.chooseOne = 1
		self.options = [RampantGrowth_Option(), Enrich_Option()]
		
	def whenEffective(self, target=None, comment="", choice=0):
		if choice == "ChooseBoth" or choice == 0:
			print("Nourish gives player 2 mana crystals.")
			self.Game.ManaHandler.gainManaCrystal(2, self.ID)
		if choice == "ChooseBoth" or choice == 1:
			print("Nourish lets player draw 3 cards.")
			self.Game.Hand_Deck.drawCard(self.ID)
			self.Game.Hand_Deck.drawCard(self.ID)
			self.Game.Hand_Deck.drawCard(self.ID)
		return None
		
class RampantGrowth_Option:
	def __init__(self):
		self.name = "Rampant Growth"
		self.description = "2 mana crystals"
		self.index = "Classic-Druid-6-Spell-Rampant Growth-Uncollectible"
		
	def available(self):
		return True
		
class Enrich_Option:
	def __init__(self):
		self.name = "Enrich"
		self.description = "Draw 3 cards"
		self.index = "Classic-Druid-6-Spell-Enrich-Uncollectible"
		
	def available(self):
		return True
		
class RampantGrowth(Spell):
	Class, name = "Druid", "Rampant Growth"
	needTarget, mana = False, 6
	index = "Classic-Druid-6-Spell-Rampant Growth-Uncollectible"
	description = "Gain 2 Mana Crystals"
	def whenEffective(self, target=None, comment="", choice=0):
		print("Rampant Growth is cast and gives player 2 mana crystals.")
		self.Game.ManaHandler.gainManaCrystal(2, self.ID)
		return None
		
class Enrich(Spell):
	Class, name = "Druid", "Enrich"
	needTarget, mana = False, 6
	index = "Classic-Druid-6-Spell-Enrich-Uncollectible"
	description = "Draw 3 cards"
	def whenEffective(self, target=None, comment="", choice=0):
		print("Enrich is cast and lets player draw 3 cards.")
		self.Game.Hand_Deck.drawCard(self.ID)
		self.Game.Hand_Deck.drawCard(self.ID)
		self.Game.Hand_Deck.drawCard(self.ID)
		return None
		
#Maybe need to rewrite.			
class AncientofLore(Minion):
	Class, race, name = "Druid", "", "Ancient of Lore"
	mana, attack, health = 7, 5, 5
	index = "Classic-Druid-7-5-5-Minion-None-Ancient of Lore-Choose One"
	needTarget, keyWord, description = True, "", "Choose One- Draw a card; or Restore 5 Health"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.chooseOne = 1
		self.options = [AncientTeachings_Option(), AncientSecrets_Option()]
		
	def returnTrue(self, choice=0):
		return choice == "ChooseBoth" or choice == 1
		
	def targetExists(self, choice=1):
		return True
		
	def whenEffective(self, target=None, comment="", choice=0):
		if choice == "ChooseBoth" or choice == 1:
			if target != None:
				heal = 5 * (2 ** self.countHealDouble())
				print("Ancient of Lore restores %d health to "%heal, target.name)
				self.restoresHealth(target, heal)
		if choice == "ChooseBoth" or choice == 0:
			print("Ancient of Lore lets player draw a card.")
			self.Game.Hand_Deck.drawCard(self.ID)
		return self, target
		
class AncientTeachings_Option:
	def __init__(self):
		self.name = "Ancient Teachings"
		self.description = "Draw a card"
		
	def available(self):
		return True
		
class AncientSecrets_Option:
	def __init__(self):
		self.name = "Ancient Secrets"
		self.description = "Restore 5 health"
		
	def available(self):
		return True
		
		
class AncientofWar(Minion):
	Class, race, name = "Druid", "", "Ancient of War"
	mana, attack, health = 7, 5, 5
	index = "Classic-Druid-7-5-5-Minion-None-Ancient of War-Choose One"
	needTarget, keyWord, description = False, "", "Choose One- +5 Attack; or +5 Health and Taunt"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.chooseOne = 1
		self.options = [Uproot_Option(), Rooted_Option()]
		
	def whenEffective(self, target=None, comment="", choice=0):
		if choice == "ChooseBoth" or choice == 0:
			print("Ancient of War gains +5 attack.")
			self.buffDebuff(5, 0)
		if self.Game.playerStatus[self.ID]["Choose Both"] > 0 or comment == 1:
			print("Ancient of War gains +5 health and Taunt.")
			self.buffDebuff(0, 5)
			self.getsKeyword("Taunt")
		return self, None
		
class Uproot_Option:
	def __init__(self):
		self.name = "Uproot"
		self.description = "+5 attack"
		
	def available(self):
		return True
		
class Rooted_Option:
	def __init__(self):
		self.name = "Rooted"
		self.description = "+5 health and Taunt"
		
	def available(self):
		return True
		
		
class GiftoftheWild(Spell):
	Class, name = "Druid", "Gift of the Wild"
	needTarget, mana = False, 8
	index = "Classic-Druid-8-Spell-Gift of the Wild"
	description = "Give your minions +2/+2 and Taunt"
	def whenEffective(self, target=None, comment="", choice=0):
		print("Gift of the Wild is cast and gives all friendly minions +2/+2 and Taunt.")
		for minion in self.Game.minionsonBoard(self.ID):
			minion.buffDebuff(2, 2)
			minion.getsKeyword("Taunt")
		return None
		
		
class Cenarius(Minion):
	Class, race, name = "Druid", "", "Cenarius"
	mana, attack, health = 9, 5, 8
	index = "Classic-Druid-9-5-8-Minion-None-Cenarius-Choose One-Legendary"
	needTarget, keyWord, description = False, "", "Choose One-Give your other minions +2/+2; or Summon two 2/2 Treants with Taunt"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.chooseOne = 1
		# 0: Give other minion +2/+2; 1:Summon two Treants with Taunt.
		self.options = [DemigodsFavor_Option(), ShandosLesson_Option(self)]
		
	#对于抉择随从而言，应以与战吼类似的方式处理，打出时抉择可以保持到最终结算。但是打出时，如果因为鹿盔和发掘潜力而没有选择抉择，视为到对方场上之后仍然可以而没有如果没有
	def whenEffective(self, target=None, comment="", choice=0):
		print("Cenarius played with choice: ", choice)
		if choice == "Choose Both" or choice == 1:
			print("Cenarius summons two 2/2 Treants with Taunt and then give other all friendly minions +2/+2.")
			pos = (self.position, "leftandRight") if self.onBoard else (-1, "totheRightEnd")
			self.Game.summonMinion([Treant_Taunt(self.Game, self.ID) for i in range(2)], pos, self.ID)
			
		if choice == "Choose Both" or choice == 0:
			print("Cenarius gives all other friendly minions +2/+2.")
			for minion in self.Game.minionsonBoard(self.ID):
				if minion != self:
					minion.buffDebuff(2, 2)
					
		return self, None
		
class Treant_Taunt(Minion):
	Class, race, name = "Druid", "", "Treant"
	mana, attack, health = 2, 2, 2
	index = "Classic-Druid-2-2-2-Minion-None-Treant-Taunt-Uncollectible"
	needTarget, keyWord, description = False, "Taunt", "Taunt"
	
class DemigodsFavor_Option:
	def __init__(self):
		self.name = "Demigod's Favor"
		self.description = "Other minions +2/+2"
		
	def available(self):
		return True
		
class ShandosLesson_Option:
	def __init__(self, minion):
		self.minion = minion
		self.name = "Shan'do's Lesson"
		self.description = "2 Treants with Taunt"
		
	def available(self):
		return self.minion.Game.spaceonBoard(self.minion.ID) > 0
		
		
"""Hunter Cards"""
class BestialWrath(Spell):
	Class, name = "Hunter", "Bestial Wrath"
	needTarget, mana = True, 1
	index = "Classic-Hunter-1-Spell-Bestial Wrath"
	description = "Give a friendly Beast +2 Attack and Immune this turn"
	def available(self):
		return self.selectableFriendlyMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return "-Beast-" in target.index and target.ID == self.ID and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None and (target.inHand or target.onBoard):
			#Assume the Immune status of the minion will vanish in hand at the end of turn, too.
			print("Bestial Wrath is cast and gives %s +2 attack and Immune this turn.")
			target.status["Immune"] = 1
			target.buffDebuff(2, 0, "EndofTurn")
		return target
		
		
class ExplosiveTrap(Secret):
	Class, name = "Hunter", "Explosive Trap"
	needTarget, mana = False, 2
	index = "Classic-Hunter-2-Spell-Explosive Trap--Secret"
	description = "When your hero is attacked, deal 2 damage to all enemies"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_ExplosiveTrap(self)]
		
class Trigger_ExplosiveTrap(SecretTrigger):
	def __init__(self, entity):
		self.blank_init(entity, ["HeroAttacksHero", "MinionAttacksHero"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.ID != self.entity.Game.turn and target == self.entity.Game.heroes[self.entity.ID]
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		damage = (2 + self.entity.countSpellDamage()) * (2 ** self.entity.countDamageDouble())
		print("When player is attacked, Secret Explosive Trap is triggered and deals %d damage to all enemies."%damage)
		enemies = [self.entity.Game.heroes[3-self.entity.ID]] + self.entity.Game.minionsonBoard(3-self.entity.ID)
		self.entity.dealsAOE(enemies, [damage for obj in enemies])
		
		
class FreezingTrap(Secret):
	Class, name = "Hunter", "Freezing Trap"
	needTarget, mana = False, 2
	index = "Classic-Hunter-2-Spell-Freezing Trap--Secret"
	description = "When an enemy minion attacks, return it to its owner's hand. It costs (2) more."
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_FreezingTrap(self)]
		
class Trigger_FreezingTrap(SecretTrigger):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionAttacksMinion", "MinionAttacksHero"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.ID != self.entity.Game.turn and subject.cardType == "Minion" and subject.ID != self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("When enemy minion %s attacks, Secret Freezing Trap is triggered and returns it to its owner's hand."%subject.name)
		minion = self.entity.Game.returnMiniontoHand(subject)
		if minion != None:
			print("The minion %s returned to hand now costs (2) more."%minion.name)
			minion.mana_set += 2
			self.entity.Game.ManaHandler.calcMana_Single(minion)
			
			
class Misdirection(Secret):
	Class, name = "Hunter", "Misdirection"
	needTarget, mana = False, 2
	index = "Classic-Hunter-2-Spell-Misdirection--Secret"
	description = "When your hero is attacked, deal 2 damage to all enemies"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_Misdirection(self)]
		
class Trigger_Misdirection(SecretTrigger):
	def __init__(self, entity):
		self.blank_init(entity, ["HeroAttacksHero", "MinionAttacksHero"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		#The target needs to be your hero
		if self.entity.ID != self.entity.Game.turn and target.cardType == "Hero" and target.ID == self.entity.ID:
			if self.entity.Game.heroes[1] != self.entity.Game.target and self.entity.Game.heroes[1] != subject:
				return True
			if self.entity.Game.heroes[2] != self.entity.Game.target and self.entity.Game.heroes[2] != subject:
				return True
			for minion in self.entity.Game.minionsonBoard(1) + self.entity.Game.minionsonBoard(2):
				if minion != self.entity.Game.target and minion != subject:
					return True
		return False
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		otherTargets = []
		if self.entity.ID != self.entity.Game.turn and target.cardType == "Hero" and target.ID == self.entity.ID:
			if self.entity.Game.heroes[1] != self.entity.Game.target and self.entity.Game.heroes[1] != subject:
				otherTargets.append(self.entity.Game.heroes[1])
			if self.entity.Game.heroes[2] != self.entity.Game.target and self.entity.Game.heroes[2] != subject:
				otherTargets.append(self.entity.Game.heroes[2])
			for minion in self.entity.Game.minionsonBoard(1) + self.entity.Game.minionsonBoard(2):
				if minion != self.entity.Game.target and minion != subject:
					otherTargets.append(minion)
		if otherTargets != []:
			self.entity.Game.target = np.random.choice(otherTargets)
			print("When player is attacked, Secret Misdirection is triggered and redirects the attack to another target", self.entity.Game.target.name)
			
			
class SnakeTrap(Secret):
	Class, name = "Hunter", "Snake Trap"
	needTarget, mana = False, 2
	index = "Classic-Hunter-2-Spell-Snake Trap--Secret"
	description = "When one of your minions is attacked, summon three 1/1 Snakes"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_SnakeTrap(self)]
		
class Trigger_SnakeTrap(SecretTrigger):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionAttacksMinion", "HeroAttacksMinion"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		#The target has to a friendly minion and there is space on board to summon minions.
		return self.entity.ID != self.entity.Game.turn and target.cardType == "Minion" and target.ID == self.entity.ID and self.entity.Game.spaceonBoard(self.entity.ID) > 0
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("When a friendly minion %s is attacked, Secret Snake Trap is triggered and summons three 1/1 Snakes."%target.name)
		self.entity.Game.summonMinion([Snake(self.entity.Game, self.entity.ID) for i in range(3)], (-1, "totheRightEnd"), self.entity.ID)
		
class Snake(Minion):
	Class, race, name = "Hunter", "Beast", "Snake"
	mana, attack, health = 1, 1, 1
	index = "Classic-Hunter-1-1-1-Minion-Beast-Snake-Uncollectible"
	needTarget, keyWord, description = False, "", ""
	
	
class Snipe(Secret):
	Class, name = "Hunter", "Snipe"
	needTarget, mana = False, 2
	index = "Classic-Hunter-2-Spell-Snipe--Secret"
	description = "After your opponent plays a minion, deal 4 damage to it"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_Snipe(self)]
		
class Trigger_Snipe(SecretTrigger):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionBeenPlayed"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		#不确定是否只会对生命值大于1的随从触发。一般在"MinionBeenPlayed"信号发出的时候随从都是处于非濒死状态的。
		return self.entity.ID != self.entity.Game.turn and subject.ID != self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		damage = (4 + self.entity.countSpellDamage()) * (2 ** self.entity.countDamageDouble())
		print("After enemy minion %s is played, Secret Snipe is triggered and deals %d damage to it."%(subject, damage))
		self.entity.dealsDamage(subject, damage)
		
		
class Flare(Spell):
	Class, name = "Hunter", "Flare"
	needTarget, mana = False, 2
	index = "Classic-Hunter-2-Spell-Flare"
	description = "All minions lose Stealth. Destroy all enemy secrets. Draw a card"
	def whenEffective(self, target=None, comment="", choice=0):
		print("Flare is cast. All minions lose Stealth. All enemy secrets are destroyed and player draws a card.")
		for minion in self.Game.minionsonBoard(1) + self.Game.minionsonBoard(2):
			minion.keyWords["Stealth"] = 0
			minion.status["Temp Stealth"] = 0
		self.Game.SecretHandler.extractSecrets(3-self.ID, True)
		self.Game.Hand_Deck.drawCard(self.ID)
		return None
		
		
class ScavengingHyena(Minion):
	Class, race, name = "Hunter", "Beast", "Scavenging Hyena"
	mana, attack, health = 2, 2, 2
	index = "Classic-Hunter-2-2-2-Minion-Beast-Scavenging Hyena"
	needTarget, keyWord, description = False, "", "Whenever a friendly Beast dies, gain +2/+1"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_ScavengingHyena(self)]
		
class Trigger_ScavengingHyena(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionDies"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		#Technically, minion has to disappear before dies. But just in case.
		return self.entity.onBoard and target != self.entity and target.ID == self.entity.ID and "Beast" in target.race
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("A friendly Beast %s dies and %s gains +2/+1."%(target.name, self.entity.name))
		self.entity.buffDebuff(2, 1)
		
		
class DeadlyShot(Spell):
	Class, name = "Hunter", "Deadly Shot"
	needTarget, mana = False, 3
	index = "Classic-Hunter-3-Spell-Deadly Shot"
	description = "Destroy a random enemy minion"
	def whenEffective(self, target=None, comment="", choice=0):
		minions = self.Game.minionsonBoard(3-self.ID)
		if minions != []:
			target = np.random.choice(minions)
			print("Deadly shot cast. The enemy minion", target, "will die")
			target.dead = True
		return None
		
		
class EaglehornBow(Weapon):
	Class, name, description = "Hunter", "Eaglehorn Bow", "Whenever a friendly Secret is revealed, gain +1 Durability"
	mana, attack, durability = 3, 3, 2
	index = "Classic-Hunter-3-3-2-Weapon-Eaglehorn Bow"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_EaglehornBow(self)]
		
class Trigger_EaglehornBow(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["SecretRevealed"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return subject.ID == self.entity.ID and self.entity.onBoard
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("A friendly Secret is revealed and %s gains +1 Durability."%self.entity.name)
		self.entity.gainStat(0, 1)
		
		
class UnleashtheHounds(Spell):
	Class, name = "Hunter", "Unleash the Hounds"
	needTarget, mana = False, 3
	index = "Classic-Hunter-3-Spell-Unleash the Hounds"
	description = "For each enemy minion, summon a 1/1 Hound with Charge"
	def available(self):
		if self.Game.spaceonBoard(self.ID) > 0 and self.Game.minionsonBoard(3-self.ID) != []:
			return True
		return False
		
	def whenEffective(self, target=None, comment="", choice=0):
		print("Unleash the Hounds is cast and summons a 1/1 Hound with Charge for each enemy minion.")
		numHounds = min(self.Game.spaceonBoard(self.ID), len(self.Game.minionsonBoard(3-self.ID)))
		self.Game.summonMinion([Hound(self.Game, self.ID) for i in range(numHounds)], (-1, "totheRightEnd"), self.ID)
		return None
		
class Hound(Minion):
	Class, race, name = "Hunter", "Beast", "Hound"
	mana, attack, health = 1, 1, 1
	index = "Classic-Hunter-1-1-1-Minion-Beast-Hound-Charge-Uncollectible"
	needTarget, keyWord, description = False, "Charge", ""
	
	
class ExplosiveShot(Spell):
	Class, name = "Hunter", "Explosive Shot"
	needTarget, mana = True, 5
	index = "Classic-Hunter-5-Spell-Explosive Shot"
	description = "Deal 5 damage to a minion and 2 damage to adjacent ones"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			damage_target = (5 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			damage_adjacent = (3 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			print("Explosive Shot is cast and deals %d damage to %s and %d damage to minions adjacent to it."%(damage_target, target.name, damage_adjacent))
			if target.onBoard and self.Game.findAdjacentMinions(target)[0] != []:
				targets = [target] + self.Game.findAdjacentMinions(target)[0]
				damages = [damage_target] + [damage_adjacent for minion in targets]
				self.dealsAOE(targets, damages)
			else:
				self.dealsDamage(target, damage_target)
		return target
		
		
class SavannahHighmane(Minion):
	Class, race, name = "Hunter", "Beast", "Savannah Highmane"
	mana, attack, health = 6, 6, 5
	index = "Classic-Hunter-6-6-5-Minion-Beast-Savannah Highmane-Deathrattle"
	needTarget, keyWord, description = False, "", "Deathrattle: Summon two 2/2 Hyenas"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [SummonTwoHyenas(self)]
		
class SummonTwoHyenas(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		pos = (self.entity.position, "totheRight") if self.entity in self.entity.Game.minions[self.entity.ID] else (-1, "totheRightEnd")
		print("Deathrattle: Summon two 2/2 Hyenas triggers.")
		self.entity.Game.summonMinion([Hyena(self.entity.Game, self.entity.ID) for i in range(2)], pos, self.entity.ID)
		
class Hyena(Minion):
	Class, race, name = "Hunter", "Beast", "Hyena"
	mana, attack, health = 2, 2, 2
	index = "Classic-Hunter-2-2-2-Minion-Beast-Hyena-Uncollectible"
	needTarget, keyWord, description = False, "", ""
	
	
class GladiatorsLongbow(Weapon):
	Class, name, description = "Hunter", "Gladiator's Longbow", "Your hero is Immune while attacking"
	mana, attack, durability = 7, 5, 2
	index = "Classic-Hunter-7-5-2-Weapon-Gladiator's Longbow"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_GladiatorsLongbow(self)]
		
class Trigger_GladiatorsLongbow(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["BattleStarted", "BattleFinished"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return subject == self.entity.Game.heroes[self.entity.ID] and self.entity.onBoard
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		if signal == "BattleStarted":
			print("Before attack begins, %s gives the attacking hero Immune"%self.entity.name)
			self.entity.Game.playerStatus[self.entity.ID]["Immune"] += 1
		else:
			print("After attack finished, %s removes the Immune from the attacking hero."%self.entity.name)
			if self.entity.Game.playerStatus[self.entity.ID]["Immune"] > 0:
				self.entity.Game.playerStatus[self.entity.ID]["Immune"] -= 1
				
				
class KingCrush(Minion):
	Class, race, name = "Hunter", "Beast", "King Crush"
	mana, attack, health = 9, 8, 8
	index = "Classic-Hunter-9-8-8-Minion-Beast-King Crush-Charge-Legendary"
	needTarget, keyWord, description = False, "Charge", "Charge"
	
	
"""Mage cards"""
class TomeofIntellect(Spell):
	Class, name = "Mage", "Tome of Intellect"
	needTarget, mana = False, 1
	index = "Classic-Mage-1-Spell-Tome of Intellect"
	description = "Add a random Mage spell to your hand"
	def whenEffective(self, target=None, comment="", choice=0):
		print("Tome of Intellect is cast and adds a random Mage card to player's hand.")	
		if self.Game.Hand_Deck.handNotFull(self.ID):
			spells = []
			for key, value in self.Game.ClassCards["Mage"].items():
				if "-Spell-" in key:
					spells.append(value)
			self.Game.Hand_Deck.addCardtoHand(np.random.choice(spells), self.ID, "CreateUsingType")
		return None
		
		
class Icicle(Spell):
	Class, name = "Mage", "Icicle"
	needTarget, mana = True, 2
	index = "Classic-Mage-2-Spell-Icicle"
	description = "Deal 2 damage to a minion. If it's Frozen, draw a card"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0):
		damage = (2 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		print("Icicle is cast and deals %d damage to "%damage, target.name)
		self.dealsDamage(target, damage)
		if target.status["Frozen"]:
			print("Icicle targets a Frozen minion and lets player draws a card.")
			self.Game.Hand_Deck.drawCard(self.ID)
		return target
		
		
class ManaWyrm(Minion):
	Class, race, name = "Mage", "", "Mana Wyrm"
	mana, attack, health = 2, 1, 3
	index = "Classic-Mage-2-1-3-Minion-None-Mana Wyrm"
	needTarget, keyWord, description = False, "", "Whenever you cast a spell, gain 1 Attack"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_ManaWyrm(self)]
		
class Trigger_ManaWyrm(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["SpellPlayed"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject.ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("Player cast a spell and %s gains +1 Attack."%self.entity.name)
		self.entity.buffDebuff(1, 0)
		
		
class SorcerersApprentice(Minion):
	Class, race, name = "Mage", "", "Sorcerer's Apprentice"
	mana, attack, health = 2, 3, 2
	index = "Classic-Mage-2-3-2-Minion-None-Sorcerer's Apprentice"
	needTarget, keyWord, description = False, "", "Your spells cost (1) less"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.manaAura = YourSpellsCost1Less(self)
		self.appearResponse = [self.activateAura]
		self.disappearResponse = [self.deactivateAura]
		self.silenceResponse = [self.deactivateAura]
		
	def activateAura(self):
		print("Sorcerer's Apprentice's mana aura is included. Player's spells cost 1 less now.")
		self.Game.ManaHandler.CardAuras.append(self.manaAura)
		self.Game.ManaHandler.calcMana_All()
		
	def deactivateAura(self):
		extractfrom(self.manaAura, self.Game.ManaHandler.CardAuras)
		print("Sorcerer's Apprentice's mana aura is removed. Player's spells no longer cost 1 less now.")
		self.Game.ManaHandler.calcMana_All()
		
class YourSpellsCost1Less:
	def __init__(self, minion):
		self.minion = minion
		self.temporary = False
		
	def handleMana(self, target):
		if target.cardType == "Spell" and target.ID == self.minion.ID:
			if target.mana > 0:
				target.mana -= 1
			else:
				target.mana = 0
				
#Counterspell is special, it doesn't need a trigger. All spells played by player will directly
#check if this Secret is onBoard.
class Counterspell(Secret):
	Class, name = "Mage", "Counterspell"
	needTarget, mana = False, 3
	index = "Classic-Mage-3-Spell-Counterspell--Secret"
	description = "When your opponent casts a spell, Counter it."
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_Counterspell(self)]
		
class Trigger_Counterspell(SecretTrigger):
	def __init__(self, entity):
		self.blank_init(entity, ["TriggerCounterspell"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return subject.ID != self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("Secret Counterspell Counters player's attempt to cast spell", subject.name)
		#But actually nothing happens in this trigger. The Game will simply skip all the resolution at the playSpell() function.
		
		
class IceBarrier(Secret):
	Class, name = "Mage", "Ice Barrier"
	needTarget, mana = False, 3
	index = "Classic-Mage-3-Spell-Ice Barrier--Secret"
	description = "When your hero is attacked, gain 8 Armor"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_IceBarrier(self)]
		
class Trigger_IceBarrier(SecretTrigger):
	def __init__(self, entity):
		self.blank_init(entity, ["HeroAttacksHero", "MinionAttacksHero"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.ID != self.entity.Game.turn and target.ID == self.entity.ID and target.cardType == "Hero"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("When hero %s is attack, Secret Ice Barrier is triggered and player gains 8 Armor."%target.name)
		self.entity.Game.heroes[self.entity.ID].gainsArmor(8)
		
		
class MirrorEntity(Secret):
	Class, name = "Mage", "Mirror Entity"
	needTarget, mana = False, 3
	index = "Classic-Mage-3-Spell-Mirror Entity--Secret"
	description = "After your opponent plays a minion, summon a copy of it"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_MirrorEntity(self)]
		
class Trigger_MirrorEntity(SecretTrigger):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionBeenPlayed"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		#To send "MinionBeenPlayed", the minion has to be onBoard.
		#Assume this only copies minions not dying.
		#print("Testing if Mirror Entity can trigger. The space on board is:", self.entity.Game.spaceonBoard(self.entity.ID))
		#print("Mirror Entity can trigger", self.entity.ID != self.entity.Game.turn and subject.ID != self.entity.ID and self.entity.Game.spaceonBoard(self.entity.ID) > 0)
		return self.entity.ID != self.entity.Game.turn and subject.ID != self.entity.ID and self.entity.Game.spaceonBoard(self.entity.ID) > 0
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("After enemy minion %s is played, Secret Mirro Entity is triggered and summons a copy of it."%subject.name)
		Copy = subject.selfCopy(self.entity.ID)
		self.entity.Game.summonMinion(Copy, -1, self.entity.ID)
		
		
class Spellbender(Secret):
	Class, name = "Mage", "Mirror Entity"
	needTarget, mana = False, 3
	index = "Classic-Mage-3-Spell-Spellbender--Secret"
	description = "After your opponent plays a minion, summon a copy of it"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_Spellbender(self)]
		
class Trigger_Spellbender(SecretTrigger):
	def __init__(self, entity):
		self.blank_init(entity, ["SpellTargetDecision"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		print("Testing if Spellbender can respond to signal", signal)
		return self.entity.ID != self.entity.Game.turn and subject.ID != self.entity.ID and target != None and self.entity.Game.spaceonBoard(self.entity.ID) > 0
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("When an enemy cast spell %s on a minion, Secret Spellbender summons a 1/3 as the new target."%subject.name)
		spellbender = Spellbender_Minion(self.entity.Game, self.entity.ID)
		self.entity.Game.summonMinion(spellbender, -1, self.entity.ID)
		self.entity.Game.target = spellbender
		
class Spellbender_Minion(Minion):
	Class, race, name = "Mage", "", "Spellbender"
	mana, attack, health = 1, 1, 3
	index = "Classic-Mage-1-1-3-Minion-None-Spellbender-Uncollectible"
	needTarget, keyWord, description = False, "", ""
	
	
class Vaporize(Secret):
	Class, name = "Mage", "Vaporize"
	needTarget, mana = False, 3
	index = "Classic-Mage-3-Spell-Vaporize--Secret"
	description = "When a minion attacks your hero, destroy it"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_Vaporize(self)]
		
class Trigger_Vaporize(SecretTrigger):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionAttacksHero"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.ID != self.entity.Game.turn and target == self.entity.Game.heroes[self.entity.ID] and subject.cardType == "Minion"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("When minion %s attacks player, Secret Vaporize is triggered and destroys it"%subject.name)
		subject.dead = True
		
		
class KirinTorMage(Minion):
	Class, race, name = "Mage", "", "Kirin Tor Mage"
	mana, attack, health = 3, 4, 3
	index = "Classic-Mage-3-4-3-Minion-None-Kirin Tor Mage-Battlecry"
	needTarget, keyWord, description = False, "", "Battlecry: Your next Secret this turn costs (0)"
	
	def whenEffective(self, target=None, comment="", choice=0):
		print("Kirin Tor Mage's battlecry makes player's next secret this turn cost 0.")
		tempAura = YourNextSecretCosts0ThisTurn(self.Game, self.ID)
		tempAura.activate()
		return self, None
		
class YourNextSecretCosts0ThisTurn(TempManaEffect):
	def __init__(self, Game, ID):
		self.ID = ID
		self.Game = Game
		self.temporary = True
		self.triggersonBoard = [Trigger_YourNextSecretCosts0ThisTurn(self)]
		
	def handleMana(self, target):
		if "--Secret" in target.index and target.ID == self.ID:
			target.mana = 0
			
class Trigger_YourNextSecretCosts0ThisTurn(TriggeronBoard): 
	def __init__(self, entity):
		self.blank_init(entity, ["ManaCostPaid"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		#不需要响应回合结束，因为光环自身被标记为temporary，会在回合结束时自行消失。
		print("Testing if Kirin Tor Mage's mana need to expire for", subject.index)
		print("Can trigger", subject.ID == self.entity.ID and "--Secret" in subject.index)
		return subject.ID == self.entity.ID and "--Secret" in subject.index
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("Kirin Tor Mage's 'Your next Secret costs (0)' expires.")
		self.entity.deactivate()
		
		
class ConeofCold(Spell):
	Class, name = "Mage", "Cone of Cold"
	needTarget, mana = True, 4
	index = "Classic-Mage-4-Spell-Cone of Cold"
	description = "Freeze a minion and the minions next to it, and deal 1 damage to them"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			damage = (1 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			print("Cone of Cold is cast and deals %d damage to %s and minions adjacent to it."%(damage, target.name))
			adjacentMinions, distribution = self.Game.findAdjacentMinions(target)
			if adjacentMinions == []:
				self.dealsDamage(target, damage)
				target.getsFrozen()
			else:
				targets = [target] + adjacentMinions
				self.dealsAOE(targets, [damage for minion in targets])
				for minion in targets:
					minion.getsFrozen()
		return target
		
		
class EtherealArcanist(Minion):
	Class, race, name = "Mage", "", "Ethereal Arcanist"
	mana, attack, health = 4, 3, 3
	index = "Classic-Mage-4-3-3-Minion-None-Ethereal Arcanist"
	needTarget, keyWord, description = False, "", "If you control a Secret at the end of your turn, gain +2/+2"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_EtherealArcanist(self)]
		
class Trigger_EtherealArcanist(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["TurnEnds"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and ID == self.entity.ID and self.entity.Game.SecretHandler.secrets[self.entity.ID] != []
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("At the end of turn, player controls a Secret and %s gain +2/+2."%self.entity.name)
		self.entity.buffDebuff(2, 2)
		
		
class Blizzard(Spell):
	Class, name = "Mage", "Blizzard"
	needTarget, mana = False, 6
	index = "Classic-Mage-6-Spell-Blizzard"
	description = "Deal 2 damage to all enemy minions and Freeze them"
	def whenEffective(self, target=None, comment="", choice=0):
		damage = (2 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		print("Blizzard deals %d damage to all enemy minions and freezes them."%damage)
		targets = self.Game.minionsonBoard(3-self.ID)
		#Spell AOE can only be take effect before deathrattle triggering. Don't need to make sure 
		self.dealsAOE(targets, [damage for minion in targets])
		for minion in self.Game.minionsonBoard(3-self.ID):
			minion.getsFrozen()
		return None
		
		
class ArchmageAntonidas(Minion):
	Class, race, name = "Mage", "", "Archmage Antonidas"
	mana, attack, health = 7, 5, 7
	index = "Classic-Mage-7-5-7-Minion-None-Archmage Antonidas-Legendary"
	needTarget, keyWord, description = False, "", "Whenever you cast a spell, add a 'Fireball' spell to your hand"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_ArchmageAntonidas(self)]
		
class Trigger_ArchmageAntonidas(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["SpellPlayed"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject.ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("Player cast a spell and %s add a 'Fireball' spell to player's hand."%self.entity.name)
		self.entity.Game.Hand_Deck.addCardtoHand(Fireball, self.entity.ID, "CreateUsingType")
		
		
class Pyroblast(Spell):
	Class, name = "Mage", "Pyroblast"
	needTarget, mana = True, 10
	index = "Classic-Mage-10-Spell-Pyroblast"
	description = "Deal 10 damage"
	def whenEffective(self, target=None, comment="", choice=0):
		damage = (10 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		print("Pyroblast is cast and deals %d damage to "%damage, target.name)
		self.dealsDamage(target, damage)
		return target
		
"""Paladin cards"""
#If minion attacks and triggers this, drawing card from empty deck kills the hero. Then the attack will be stopped early.
class BlessingofWisdom(Spell):
	Class, name = "Paladin", "Blessing of Wisdom"
	needTarget, mana = True, 1
	index = "Classic-Paladin-1-Spell-Blessing of Wisdom"
	description = "Choose a minion. Whenever it attacks, draw a card"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None and (target.inHand or target.onBoard):
			print("Blessing of Wisdom is cast on target %s. Whenever it attacks, player draws a card."%target.name)
			trigger = Trigger_BlessingofWisdom(target)
			target.triggersonBoard.append(trigger)
			if target.onBoard:
				trigger.connect()
		return target
		
class Trigger_BlessingofWisdom(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionAttackingHero", "MinionAttackingMinion"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject == self.entity
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("Minoin %s attacks and Blessing of Wisdom lets its owner draw a card."%self.entity.name)
		self.entity.Game.Hand_Deck.drawCard(self.entity.ID)
		
		
class EyeforanEye(Secret):
	Class, name = "Paladin", "Eye for an Eye"
	needTarget, mana = False, 1
	index = "Classic-Paladin-1-Spell-Eye for an Eye--Secret"
	description = "When your hero takes damage, deal that much damage to the enemy hero"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_EyeforanEye(self)]
		
class Trigger_EyeforanEye(SecretTrigger):
	def __init__(self, entity):
		self.blank_init(entity, ["HeroTakesDamage"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.ID != self.entity.Game.turn and target.ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		damage = (number + self.entity.countSpellDamage()) * (2 ** self.entity.countDamageDouble())
		print("When player takes %d damage, Secret Eye for an Eye is triggered and deals %d damage to the enemy hero."%(number, damage))
		self.entity.dealsDamage(self.entity.Game.heroes[3-self.entity.ID], damage)
		
		
class SacredSacrifice(Secret):
	Class, name = "Paladin", "Sacred Sacrifice"
	needTarget, mana = False, 1
	index = "Classic-Paladin-1-Spell-Sacred Sacrifice--Secret"
	description = "When an enemy attacks, summon a 2/1 Defender as the new target"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_SacredSacrifice(self)]
		
class Trigger_SacredSacrifice(SecretTrigger):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionAttacksHero", "MinionAttacksMinion", "HeroAttacksHero", "HeroAttacksMinion"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.ID != self.entity.Game.turn and subject.ID != self.entity.ID and self.entity.Game.spaceonBoard(self.entity.ID) > 0
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("When enemy minion %s attacks, Secret Sacred Sacrifice triggers and summons a 2/1 Defender as new target."%subject.name)
		newTarget = Defender(self.entity.Game, self.entity.ID)
		self.entity.Game.summonMinion(newTarget, -1, self.entity.ID)
		self.entity.Game.target = newTarget
		
		
class Defender(Minion):
	Class, race, name = "Paladin", "", "Defender"
	mana, attack, health = 1, 2, 1
	index = "Classic-Paladin-1-2-1-Minion-None-Defender-Uncollectible"
	needTarget, keyWord, description = False, "", ""
	
	
class Redemption(Secret):
	Class, name = "Paladin", "Redemption"
	needTarget, mana = False, 1
	index = "Classic-Paladin-1-Spell-Redemption--Secret"
	description = "When an enemy attacks, summon a 2/1 Defender as the new target"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_Redemption(self)]
		
class Trigger_Redemption(SecretTrigger):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionDies"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.ID != self.entity.Game.turn and target.ID == self.entity.ID and self.entity.Game.spaceonBoard(self.entity.ID) > 0
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("When friendly minion %d dies, Secret Redemption returns it to life with 1 Health."%target.name)
		minion = type(target)(self.entity.Game, self.entity.ID)
		minion.health = 1
		self.entity.Game.summonMinion(minion, -1, self.entity.ID)
		
		
class Repentence(Secret):
	Class, name = "Paladin", "Repentence"
	needTarget, mana = False, 1
	index = "Classic-Paladin-1-Spell-Repentence--Secret"
	description = "After your opponent plays a minion, reduce its Health to 1"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_Repentence(self)]
		
class Trigger_Repentence(SecretTrigger):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionBeenPlayed"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.ID != self.entity.Game.turn and subject.ID != self.entity
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("After enemy minion %s is played, Secret Repentence is triggered and reduces its Health to 1."%subject.name)
		subject.statReset(False, 1)
		
		
class ArgentProtector(Minion):
	Class, race, name = "Paladin", "", "Argent Protector"
	mana, attack, health = 2, 2, 2
	index = "Classic-Paladin-2-2-2-Minion-None-Argent Protector-Battlecry"
	needTarget, keyWord, description = True, "", "Battlecry: Give a friendly minion Divine Shield"
	
	def targetExists(self, choice=0):
		return self.selectableFriendlyMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.ID == self.ID and target != self and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None: #The minion's getsKeyword() is only effective if minion is onBoard or inHand
			print("Argent Protector's battlecry gives friendly minion %s Divine Shield."%target.name)
			target.getsKeyword("Divine Shield")
		return self, target
		
		
class Equality(Spell):
	Class, name = "Paladin", "Equality"
	needTarget, mana = False, 4
	index = "Classic-Paladin-4-Spell-Equality"
	description = "Change the Health of ALL minions to 1"
	def whenEffective(self, target=None, comment="", choice=0):
		print("Equality is cast and sets all minions' health to 1.")
		for minion in self.Game.minionsonBoard(1) + self.Game.minionsonBoard(2):
			minion.statReset(False, 1)
		return None
		
		
class ArdorPeacekeeper(Minion):
	Class, race, name = "Paladin", "", "Ardor Peacekeeper"
	mana, attack, health = 3, 3, 3
	index = "Classic-Paladin-3-3-3-Minion-None-Ardor Peacekeeper-Battlecry"
	needTarget, keyWord, description = True, "", "Battlecry: Change an enemy minion's Attack to 1"
	
	def targetExists(self, choice=0):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target != self and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None and (target.inHand or target.onBoard):
			print("Ardor Peacekeeper's battlecry sets minion %s's attack to 1."%target.name)
			target.statReset(1, False)
		return self, target
		
		
class SwordofJustice(Weapon):
	Class, name, description = "Paladin", "Sword of Justice", "After you summon a minion, give it +1/+1 and this loses 1 Durability"
	mana, attack, durability = 3, 1, 5
	index = "Classic-Paladin-3-1-5-Weapon-Sword of Justice"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_SwordofJustice(self)]
		
class Trigger_SwordofJustice(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionBeenSummoned"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		#Can only buff if there is still durability left
		return subject.ID == self.entity.ID and self.entity.onBoard and self.entity.durability > 0
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("A friendly minion %s is summoned and %s gives it +1/+1 and loses 1 Durability."%(subject.name, self.entity.name))
		subject.buffDebuff(1, 1)
		self.entity.loseDurability()
		
		
class BlessedChampion(Spell):
	Class, name = "Paladin", "Blessed Champion"
	needTarget, mana = True, 5
	index = "Classic-Paladin-5-Spell-Blessed Champion"
	description = "Double a minion's Attack"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			print("Blessed Champion is cast and doubles %s's attack."%target.name)
			target.statReset(2*target.attack, False)
		return target
		
		
class HolyWrath(Spell):
	Class, name = "Paladin", "Holy Wrath"
	needTarget, mana = True, 5
	index = "Classic-Paladin-5-Spell-Holy Wrath"
	description = "Draw a card and deal damage equal to its cost"
	def whenEffective(self, target=None, comment="", choice=0):
		#drawCard() method returns a tuple (card, mana)
		card = self.Game.Hand_Deck.drawCard(self.ID)
		if card[0] == None:
			print("Holy Wrath lets player draw a card but it can't deal damage.")
		else:
			if target != None:
				damage = (card[1] + self.countSpellDamage()) * (2 ** self.countDamageDouble())
				print("Holy Wrath lets player draw a card and deals %d damage equal to its cost to "%damage, target.name)
				self.dealsDamage(target, damage)
		return target
		
		
class Righteousness(Spell):
	Class, name = "Paladin", "Righteousness"
	needTarget, mana = False, 5
	index = "Classic-Paladin-5-Spell-Righteousness"
	description = "Give your minions Divine Shield"
	def whenEffective(self, target=None, comment="", choice=0):
		print("Righteousness is cast and gives all friendly minions Divine Shield.")
		for minion in self.Game.minionsonBoard(self.ID):
			minion.getsKeyword("Divine Shield")
		return None
		
		
class AvengingWrath(Spell):
	Class, name = "Paladin", "Avenging Wrath"
	needTarget, mana = False, 6
	index = "Classic-Paladin-6-Spell-Avenging Wrath"
	description = "Deal 8 damage randomly split among all enemies"
	def whenEffective(self, target=None, comment="", choice=0):
		damage = (8 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		print("Avenging Wrath is cast and randomly splits %d damage among enemies"%damage)
		for i in range(damage):
			targets = [self.Game.heroes[3-self.ID]]
			for minion in self.Game.minionsonBoard(3-self.ID):
				if minion.dead == False and minion.health > 0 and minion.onBoard:
					targets.append(minion)
					
			self.dealsDamage(np.random.choice(targets), 1)
		return None
		
		
class LayonHands(Spell):
	Class, name = "Paladin", "Lay on Hands"
	needTarget, mana = True, 8
	index = "Classic-Paladin-8-Spell-Lay on Hands"
	description = "Restore 8 Health. Draw 3 cards"
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			heal = 8 * (2 ** self.countHealDouble())
			print("Lay on Hands restores %d health to"%heal, target.name)
			self.restoresHealth(target, heal)
		print("Lay on Hands lets player draw 3 cards.")
		self.Game.Hand_Deck.drawCard(self.ID)
		self.Game.Hand_Deck.drawCard(self.ID)
		self.Game.Hand_Deck.drawCard(self.ID)
		return target
		
		
class TirionFordring(Minion):
	Class, race, name = "Paladin", "", "Tirion Fordring"
	mana, attack, health = 8, 6, 6
	index = "Classic-Paladin-8-6-6-Minion-None-Tirion Fordring-Taunt-Divine Shield-Deathrattle-Legendary"
	needTarget, keyWord, description = False, "Divine Shield,Taunt", "Divine Shield, Taunt. Deathrattle: Equip a 5/3 Ashbringer"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [EquipAshbringer(self)]
		
class EquipAshbringer(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("Deathrattle: Equip an Ashbringer triggers.")
		self.entity.Game.equipWeapon(Ashbringer(self.entity.Game, self.entity.ID))
		
class Ashbringer(Weapon):
	Class, name, description = "Paladin", "Ashbringer", ""
	mana, attack, durability = 5, 5, 3
	index = "Classic-Paladin-5-5-3-Weapon-Ashbringer-Uncollectible-Legendary"
	
	
"""Priest cards"""
class CircleofHealing(Spell):
	Class, name = "Priest", "Circle of Healing"
	needTarget, mana = False, 0
	index = "Classic-Priest-0-Spell-Circle of Healing"
	description = "Restore 4 health to ALL minions"
	def whenEffective(self, target=None, comment="", choice=0):
		heal = 4 * (2 ** self.countHealDouble())
		targets = self.Game.minionsonBoard(1) + self.Game.minionsonBoard(2)
		print("Circle of Healing is cast and restores %d heal to all minions."%heal)
		self.dealsAOE([], [], targets, [heal for minion in targets])
		return None
		
		
class Silence(Spell):
	Class, name = "Priest", "Silence"
	needTarget, mana = True, 0
	index = "Classic-Priest-0-Spell-Silence"
	description = "Silence a minion"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			print("Silence is cast and silences minion ", target.name)
			target.getsSilenced()
		return target
		
		
class InnerFire(Spell):
	Class, name = "Priest", "Inner Fire"
	needTarget, mana = True, 1
	index = "Classic-Priest-1-Spell-Inner Fire"
	description = "Change a minion's Attack to be equal to its Health"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			print("Inner Fire is cast and changes %s's attack equal to its health."%target.name)
			target.statReset(target.health, False)
		return target
		
		
class Lightwell(Minion):
	Class, race, name = "Priest", "", "Lightwell"
	mana, attack, health = 2, 0, 5
	index = "Classic-Priest-2-0-5-Minion-None-Lightwell"
	needTarget, keyWord, description = False, "", "At the start of your turn, restore 3 health to a damaged friendly character"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_Lightwell(self)]
		
class Trigger_Lightwell(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["TurnStarts"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		targets = []
		if self.entity.Game.heroes[self.entity.ID].health < self.entity.Game.heroes[self.entity.ID].health_upper:
			targets.append(self.entity.Game.heroes[self.entity.ID])
		for minion in self.entity.Game.minionsonBoard(self.entity.ID):
			if minion.health < minion.health_upper:
				targets.append(minion)
				
		if targets != []:
			target = np.random.choice(targets)
			heal = 3 * (2 ** self.entity.countHealDouble())
			print("At the end of turn, %s restores %d health to damaged friendly character all friendly minions"%(self.entity.name, heal), target.name)
			self.entity.restoresHealth(target, heal)
			
			
class Shadowform(Spell):
	Class, name = "Priest", "Shadowform"
	needTarget, mana = False, 3
	index = "Classic-Priest-3-Spell-Shadowform"
	description = "Your Hero Power becomes 'Deal 2 damage'. If already in Shadowform: 3 damage"
	def whenEffective(self, target=None, comment="", choice=0):
		if self.Game.heroPowers[self.ID].name == "Mind Spike" or self.Game.heroPowers[self.ID].name == "Mind Shatter":
			print("Shadowform is cast and changes hero ability to Mind Shatter that does 3 damage.")
			MindShatter(self.Game, self.ID).replaceHeroPower()
		else:
			print("Shadowform is cast and changes hero ability to Mind Spike that does 2 damage.")
			MindSpike(self.Game, self.ID).replaceHeroPower()
		return None
		
class MindSpike(HeroPower):
	name, needTarget = "Mind Spike", True
	index = "Priest-2-Hero Power-Mind Spike"
	description = "Deal 2 damage"
	def effect(self, target, choice=0):
		damage = (2 + self.Game.playerStatus[self.ID]["Temp Damage Boost"]) * (2 ** self.countDamageDouble())
		print("Hero Power Mind Spike deals %d damage to"%damage, target.name)
		objtoTakeDamage, targetSurvival = self.dealsDamage(target, damage)
		if targetSurvival > 1:
			return 1
		return 0
		
class MindShatter(HeroPower):
	name, needTarget = "Mind Shatter", True
	index = "Priest-2-Hero Power-Mind Shatter"
	description = "Deal 3 damage"
	def effect(self, target, choice=0):
		damage = (3 + self.Game.playerStatus[self.ID]["Temp Damage Boost"]) * (2 ** self.countDamageDouble())
		print("Hero Power Mind Shatter deals %d damage to"%damage, target.name)
		objtoTakeDamage, targetSurvival = self.dealsDamage(target, damage)
		if targetSurvival > 1:
			return 1
		return 0
		
		
class Thoughtsteal(Spell):
	Class, name = "Priest", "Thoughtsteal"
	needTarget, mana = False, 3
	index = "Classic-Priest-3-Spell-Thoughtsteal"
	description = "Copy 2 card in your opponent's hand and add them to your hand"
	def randomorDiscover(self):
		return "Random"
		
	#Thoughtsteal can copy all enchanements of a card in enemy deck. (Buffed Immortal Prelate)
	#MindVision can also copy the enchanements of a card in enemy hand.
	def whenEffective(self, target=None, comment="", choice=0):
		deckLength = len(self.Game.Hand_Deck.decks[3-self.ID])
		if deckLength == 0:
			print("Thoughtsteal provides no card because enemy deck is empty.")
		elif deckLength == 1:
			card = self.Game.Hand_Deck.decks[3-self.ID][0].selfCopy(self.ID)
			print("Enemy deck has only 1 card, and Thoughtsteal copies that card.")
			self.Game.Hand_Deck.addCardtoHand(card, self.ID)
		else:
			cards = np.random.choice(self.Game.Hand_Deck.decks[3-self.ID], 2, replace=False)
			copies = []
			for card in cards:
				copies.append(card.selfCopy(self.ID))
				
			self.Game.Hand_Deck.addCardtoHand(copies, self.ID)
		return None
		
		
class AuchenaiSoulpriest(Minion):
	Class, race, name = "Priest", "", "Auchenai Soulpriest"
	mana, attack, health = 4, 3, 5
	index = "Classic-Priest-4-3-5-Minion-None-Auchenai Soulpriest"
	needTarget, keyWord, description = False, "", "Your cards and powers that restore Health no deal damage instead"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.appearResponse = [self.activateAura]
		self.disappearResponse = [self.deactivateAura]
		self.silenceResponse = [self.deactivateAura]
		
	def activateAura(self):
		print("Auchenai Soulpriest's aura is registered. Player %d's heals now deal damage instead."%self.ID)
		self.Game.playerStatus[self.ID]["Heal to Damage"] += 1
		
	def deactivateAura(self):
		print("Auchenai Soulpriest's aura is removed. Player %d's heals are heals correctly."%self.ID)
		if self.Game.playerStatus[self.ID]["Heal to Damage"] > 0:
			self.Game.playerStatus[self.ID]["Heal to Damage"] -= 1
			
			
class Lightspawn(Minion):
	Class, race, name = "Priest", "", "Lightspawn"
	mana, attack, health = 4, 0, 5
	index = "Classic-Priest-4-0-5-Minion-None-Lightspawn"
	needTarget, keyWord, description = False, "", "This minion's Attack is always equal to its Health"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.appearResponse.append(self.setAttackEqualtoHealth)
		self.triggers["StatChanges"] = [self.setAttackEqualtoHealth]
		
	def setAttackEqualtoHealth(self):
		if self.silenced == False and self.onBoard:
			self.attack = self.health
			
			
class MassDispel(Spell):
	Class, name = "Priest", "Mass Dispel"
	needTarget, mana = False, 4
	index = "Classic-Priest-4-Spell-Mass Dispel"
	description = "Silence all enemy minions. Draw a card"
	def whenEffective(self, target=None, comment="", choice=0):
		print("Mass Dispel is cast, silences all enemy minions and draws a card")
		for minion in self.Game.minionsonBoard(3-self.ID):
			minion.getsSilenced()
			
		self.Game.Hand_Deck.drawCard(self.ID)
		return None
		
		
class Mindgames(Spell):
	Class, name = "Priest", "Mindgames"
	needTarget, mana = False, 4
	index = "Classic-Priest-4-Spell-Mindgames"
	description = "Put a copy of a random minion from your opponent's deck into the battlefield"
	def available(self):
		return self.Game.spaceonBoard(self.ID) > 0
		
	def whenEffective(self, target=None, comment="", choice=0):
		minions = []
		for card in self.Game.Hand_Deck.decks[3-self.ID]:
			if card.cardType == "Minion":
				minions.append(card)
		#Don't know if Mindgames can copy the enchanements of minion.
		if minions != []:
			copiedMinion = np.random.choice(minions).selfCopy(self.ID)
			print("Mindgames is cast and copies a minion %s from the opponent's deck."%copiedMinion.name)
			self.Game.summonMinion(copiedMinion, -1, self.ID)
		else:
			print("Mindgames is cast, but the opponent's deck has no minion and can only summon a 0/1 Shadow of Nothing.")
			self.Game.summonMinion(ShadowofNothing(self.Game, self.ID), -1, self.ID)
		return None
		
class ShadowofNothing(Minion):
	Class, race, name = "Priest", "", "Shadow of Nothing"
	mana, attack, health = 1, 0, 1
	index = "Classic-Priest-1-0-1-Minion-None-Shadow of Nothing-Uncollectible"
	needTarget, keyWord, description = False, "", "Mindgames whiffed! Your opponent had no minions!"
	
#被控制的随从会在回合结束效果触发之后立刻返还原有控制者，之后其他随从的回合结束触发会生效
#若我方可以进攻的随从被对方在我方回合暂时夺走，则沉默该随从后，该随从返回我方场上且仍可攻击。

#当一个随从被连续两次使用暗影狂乱更改控制权时，第二次的控制会擦除第一次的原控制者记录。
#我方本回合召唤的随从被暗中破坏者触发的敌方暗影狂乱夺走时，如果再用暗影狂乱把那个随从夺回，那个随从会可以攻击，然后回合结束时归对方所有。

#控制一个对方机械后然后磁力贴上飞弹机器人，那个机械会首先回到对方场上，但不触发飞弹机器人的特效，因为此时飞弹机器人算是新入场的turnEndTrigger
#暂时控制+永久控制 = 永久控制
#暂时控制 + 暂时控制 = 每一次暂时控制者得到
#
class ShadowMadness(Spell):
	Class, name = "Priest", "Shadow Madness"
	needTarget, mana = True, 4
	index = "Classic-Priest-4-Spell-Shadow Madness"
	description = "Gain control of an enemy minion with 3 or less Attack until end of turn"
	def available(self):
		return self.selectableEnemyMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.ID != self.ID and target.attack < 4 and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None and target.onBoard and target.ID != self.ID:
			print("Shadow Madness is cast and gains control of enemy minion %s this turn."%target.name)
			self.Game.minionSwitchSide(target, activity="Borrow")
		return target
		
#这个扳机的目标：当随从在回合结束时有多个同类扳机，只会触发第一个，这个可以通过回合ID和自身ID是否符合来决定
class Trigger_ShadowMadness(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["TurnEnds"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		#只有当前要结束的回合的ID与自身ID相同的时候可以触发，于是即使有多个同类扳机也只有一个会触发。
		return self.entity.onBoard and ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("At the end of turn, temporarily controlled minion %s is returned to the other side."%self.entity.name)
		#Game的minionSwitchSide方法会自行移除所有的此类扳机。
		self.entity.Game.minionSwitchSide(self.entity, activity="Return")
		
class CabalShadowPriest(Minion):
	Class, race, name = "Priest", "", "Cabal Shadow Priest"
	mana, attack, health = 6, 4, 5
	index = "Classic-Priest-6-4-5-Minion-None-Cabal Shadow Priest-Battlecry"
	needTarget, keyWord, description = True, "", "Battlecry: Take control of an enemy minion with 2 or less Attack"
	
	def targetExists(self, choice=0):
		return self.selectableEnemyMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.ID != self.ID and target.attack < 3 and target != self and target.onBoard
		
	#If the minion is shuffled into deck already, then nothing happens.
	#If the minion is returned to hand, move it from enemy hand into our hand.
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None and target.ID != self.ID:
			print("Cabal Shadow Priest's battlecry gains control of enemy minion %s with 2 or less attack."%target.name)
			self.Game.minionSwitchSide(target)
		return self, target
		
		
class HolyFire(Spell):
	Class, name = "Priest", "Holy Fire"
	needTarget, mana = True, 6
	index = "Classic-Priest-6-Spell-Holy Fire"
	description = "Deal 5 damage. Restore 5 Health to your hero"
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			damage = (5 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			heal = 5 * (2 ** self.countHealDouble())
			print("Holy Fire deals %d damage to %s and restores %d health to player."%(damage, target.name, heal))
			self.dealsDamage(target, damage)
			self.restoresHealth(self.Game.heroes[self.ID], heal)
		return target
		
class TempleEnforcer(Minion):
	Class, race, name = "Priest", "", "Temple Enforcer"
	mana, attack, health = 6, 6, 6
	index = "Classic-Priest-6-6-6-Minion-None-Temple Enforcer-Battlecry"
	needTarget, keyWord, description = True, "", "Battlecry: Give a friendly minion +3 health"
	
	def targetExists(self, choice=0):
		return self.selectableFriendlyMinionExists(choice)
		
	def targetCorrect(self, target, choice=0):
		if target.cardType == "Minion" and target.ID == self.ID and target != self and target.onBoard:
			return True
		return False
		
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			print("Temple Enforcer's battlecry gives friendly minion %s +3 health."%target.name)
			target.buffDebuff(0, 3)
		return self, target
		
		
class ProphetVelen(Minion):
	Class, race, name = "Priest", "", "Prophet Velen"
	mana, attack, health = 7, 7, 7
	index = "Classic-Priest-7-7-7-Minion-None-Prophet Velen-Legendary"
	needTarget, keyWord, description = False, "", "Double the damage and healing of your spells and Hero Power"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.marks["Spell Double Heal and Damage"] = 1
		self.marks["Hero Power Double Heal and Damage"] = 1
		
		
"""Rogue cards"""
class Preparation(Spell):
	Class, name = "Rogue", "Preparation"
	needTarget, mana = False, 0
	index = "Classic-Rogue-0-Spell-Preparation"
	description = "The next spell you cast this turn costs (2) less"
	
	def whenEffective(self, target=None, comment="", choice=0):
		print("Preparation is cast and next spell this turn costs 2 less.")
		tempAura = YourNextSpellCosts2LessThisTurn(self.Game, self.ID)
		tempAura.activate()
		self.Game.ManaHandler.calcMana_All()
		return None
		
class YourNextSpellCosts2LessThisTurn(TempManaEffect):
	def __init__(self, Game, ID):
		self.ID = ID
		self.Game = Game
		self.temporary = True
		self.triggersonBoard = [Trigger_YourNextSpellCosts2LessThisTurn(self)]
		
	def handleMana(self, target):
		if target.cardType == "Spell" and target.ID == self.ID:
			target.mana -= 2
			target.mana = max(0, target.mana)
			
class Trigger_YourNextSpellCosts2LessThisTurn(TriggeronBoard): 
	def __init__(self, entity):
		self.blank_init(entity, ["ManaCostPaid"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		#不需要响应回合结束，因为光环自身被标记为temporary，会在回合结束时自行消失。
		return subject.ID == self.entity.ID and subject.cardType == "Spell"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.deactivate()
		
		
class Shadowstep(Spell):
	Class, name = "Rogue", "Shadowstep"
	needTarget, mana = True, 0
	index = "Classic-Rogue-0-Spell-Shadowstep"
	description = "Return a friendly minion to your hand. It costs (2) less"
	def targetExists(self, choice=0):
		return self.selectableFriendlyMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.ID == self.ID and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0):
		print("Shadowstep is cast and returns %s to owner's hand."%target.name)
		ID = target.ID
		card = self.Game.returnMiniontoHand(target)
		if card != None:
			print("Minion %s has been returned to player's hand and it costs (2) now."%target.name)
			card.mana_set -= 2
			card.mana_set = max(0, card.mana_set)
			self.Game.ManaHandler.calcMana_Single(card)
		return target
		
		
class Pilfer(Spell):
	Class, name = "Rogue", "Pilfer"
	needTarget, mana = False, 1
	index = "Classic-Rogue-1-Spell-Pilfer"
	description = "Add a random card from another class to your hand"
	def whenEffective(self, target=None, comment="", choice=0):
		if self.Game.Hand_Deck.handNotFull(self.ID):
			otherClasses = list(self.Game.ClassCards.keys())
			extractfrom(self.Game.heroes[self.ID].Class, otherClasses)
			Class = np.random.choice(otherClasses)
			print("Pilfer is cast and adds a random card from another class to player's hand.")
			cards = list(self.Game.ClassCards[Class].values())
			self.Game.Hand_Deck.addCardtoHand(np.random.choice(cards), self.ID, "CreateUsingType")
		return None
		
#Betrayal lets target deal damage to adjacent minions.
#Therefore, the overkill and lifesteal can be triggered.
class Betrayal(Spell):
	Class, name = "Rogue", "Betrayal"
	needTarget, mana = True, 2
	index = "Classic-Rogue-2-Spell-Betrayal"
	description = "Force a minion to deal its damage to minions next to it"
	def available(self):
		return self.selectableEnemyMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.ID != self.ID and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			print("Betrayal is cast and lets target minion %s deals damage equal to its attack to adjacent minions."%target.name)
			adjacentMinions, distribution = self.Game.findAdjacentMinions(target)
			attack = target.attack
			target.dealsAOE(adjacentMinions, [attack for minion in adjacentMinions])
		return target
		
		
class ColdBlood(Spell):
	Class, name = "Rogue", "Cold Blood"
	needTarget, mana = True, 2
	index = "Classic-Rogue-2-Spell-Cold Blood-Combo"
	description = "Give a minion +2 Attack. Combo: +4 Attack instead"
	def effectCanTrigger(self):
		return self.Game.CounterHandler.cardsPlayedThisTurn[self.ID] != []
		
	def targetExists(self, choice=0):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			if self.Game.CounterHandler.cardsPlayedThisTurn[self.ID] != []:
				print("Cold Blood is cast and gives %s +4 attack"%target.name)
				target.buffDebuff(4, 0)
			else:
				print("Cold Blood is cast and gives %s +2 attack"%target.name)
				target.buffDebuff(2, 0)
		return target
		
		
class DefiasRingleader(Minion):
	Class, race, name = "Rogue", "", "Defias Ringleader"
	mana, attack, health = 2, 2, 2
	index = "Classic-Rogue-2-2-2-Minion-None-Defias Ringleader-Combo"
	needTarget, keyWord, description = False, "", "Combo: Summon a 2/1 Defias Bandit"
	
	def effectCanTrigger(self):
		return self.Game.CounterHandler.cardsPlayedThisTurn[self.ID] != []
		
	def whenEffective(self, target=None, comment="", choice=0):
		if self.Game.CounterHandler.cardsPlayedThisTurn[self.ID] != []:
			print("Defias Ringleader' Combo triggers and summons a 2/1 Defias Bandit.")
			pos = self.position + 1 if self.onBoard else -1
			self.Game.summonMinion(DefiasBandit(self.Game, self.ID), pos, self.ID)
		return self, None
		
class DefiasBandit(Minion):
	Class, race, name = "Rogue", "", "Defias Bandit"
	mana, attack, health = 1, 2, 1
	index = "Classic-Rogue-1-2-1-Minion-None-Defias Bandit-Uncollectible"
	needTarget, keyWord, description = False, "", ""
	
	
class Eviscerate(Spell):
	Class, name = "Rogue", "Eviscerate"
	needTarget, mana = True, 2
	index = "Classic-Rogue-2-Spell-Eviscerate-Combo"
	description = "Deal 2 damage. Combo: Deal 4 instead"
	def effectCanTrigger(self):
		return self.Game.CounterHandler.cardsPlayedThisTurn[self.ID] != []
		
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			if self.Game.CounterHandler.cardsPlayedThisTurn[self.ID] != []:
				damage = (4 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			else:
				damage = (2 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
				
			print("Eviscerate is cast and deals %d damage to "%damage, target.name)	
			self.dealsDamage(target, damage)
		return target
		
		
class PatientAssassin(Minion):
	Class, race, name = "Rogue", "", "Patient Assassin"
	mana, attack, health = 2, 1, 1
	index = "Classic-Rogue-2-1-1-Minion-None-Patient Assassin-Poisonous-Stealth"
	needTarget, keyWord, description = False, "Stealth,Poisonous", "Stealth, Poisonous"
	
	
class EdwinVancleef(Minion):
	Class, race, name = "Rogue", "", "Edwin Vancleef"
	mana, attack, health = 3, 2, 2
	index = "Classic-Rogue-3-2-2-Minion-None-Edwin Vancleef-Combo-Legendary"
	needTarget, keyWord, description = False, "", "Combo: Gain +2/+2 for each other card you've played this turn"
	
	def effectCanTrigger(self):
		return self.Game.CounterHandler.cardsPlayedThisTurn[self.ID] != []
		
	def whenEffective(self, target=None, comment="", choice=0):
		#Dead minions or minions in deck can't be buffed or reset.
		if self.Game.CounterHandler.cardsPlayedThisTurn[self.ID] != []:
			numCardsPlayed = len(self.Game.CounterHandler.cardsPlayedThisTurn[self.ID])
			print("Edwin Vancleef's Combo triggers and gains +2/+2 for each card player played this turn.")
			statGain = 2 * numCardsPlayed
			self.buffDebuff(statGain, statGain)
		return self, None
		
		
class Headcrack(Spell):
	Class, name = "Rogue", "Headcrack"
	needTarget, mana = False, 3
	index = "Classic-Rogue-3-Spell-Headcrack-Combo"
	description = "Deal 2 damage to the enemy hero. Combo: Return this to your hand next turn."
	def effectCanTrigger(self):
		return self.Game.CounterHandler.cardsPlayedThisTurn[self.ID] != []
		
	def whenEffective(self, target=None, comment="", choice=0):
		damage = (2 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		print("Headcrack is cast and deals %d damage to the enemy hero."%damage)
		self.dealsDamage(self.Game.heroes[3-self.ID], damage)
		if self.Game.CounterHandler.cardsPlayedThisTurn[self.ID] != []:
			trigger = Trigger_HeadCrack(self)
			trigger.ID = self.ID
			trigger.connect()
		return None
		
class Trigger_HeadCrack(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["TurnStarts"])
		self.ID = 1
		
	def connect(self):
		for signal in self.signals:
			self.entity.Game.triggersonBoard[self.ID].append((self, signal))
			
	def disconnect(self):
		for signal in self.signals:
			extractfrom((self, signal), self.entity.Game.triggersonBoard[self.ID])
			
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return ID == self.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("At the start of turn, Headcrack is added to players hand.")
		self.entity.Game.Hand_Deck.addCardtoHand(Headcrack, self.ID, "CreateUsingType")
		self.disconnect()
		
		
class PerditionsBlade(Weapon):
	Class, name, description = "Rogue", "Perdition's Blade", "Battlecry: Deal 1 damage. Combo: Deal 2 instead"
	mana, attack, durability = 3, 2, 2
	index = "Classic-Rogue-3-2-2-Weapon-Perdition's Blade-Combo-Battlecry"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.needTarget = True
		
	def effectCanTrigger(self):
		return self.Game.CounterHandler.cardsPlayedThisTurn[self.ID] != []
		
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			if self.Game.CounterHandler.cardsPlayedThisTurn[self.ID] != []:
				damage = 2
			else:
				damage = 1
			print("Perdition's Blade's battlecry deals %d damage to "%damage, target.name)
			self.dealsDamage(target, damage)
		#For the sake of Shudderwock	
		return self, target
		
		
class SI7Agent(Minion):
	Class, race, name = "Rogue", "", "SI:7 Agent"
	mana, attack, health = 3, 3, 3
	index = "Classic-Rogue-3-3-3-Minion-None-SI:7 Agent-Combo"
	needTarget, keyWord, description = True, "", "Combo: Deal 2 damage"
	
	def returnTrue(self, choice=0):
		return self.Game.CounterHandler.cardsPlayedThisTurn[self.ID] != []
		
	def effectCanTrigger(self):
		return self.Game.CounterHandler.cardsPlayedThisTurn[self.ID] != []
		
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None and self.Game.CounterHandler.cardsPlayedThisTurn[self.ID] != []:
			print("SI:7 Agent's Combo triggers and deals 2 damage to ", target.name)
			self.dealsDamage(target, 2)
		return self, target
		
#This spell is the subject that deals damage, can be boosted by Spell Damage, and the destroyed weapon won't respond to dealing damage.
#Therefore, Lifesteal and Overkill won't be triggered by this spell.
#However, Doomerang let weapon deal the damage and won't be boosted by Spell Damage.
class BladeFlurry(Spell):
	Class, name = "Rogue",  "Blade Flurry"
	needTarget, mana = False, 4
	index = "Classic-Rogue-4-Spell-Blade Flurry"
	description = "Destroy your weapon and deal its damage to all enemy minions"
	def available(self):
		return self.Game.availableWeapon(self.ID) != None
		
	def whenEffective(self, target=None, comment="", choice=0):
		weapon = self.Game.availableWeapon(self.ID)
		if weapon != None:
			damage = (weapon.attack + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			weapon.destroyed()
			print("Blade Flurry is cast, destroys player's weapon and deals %d damage to all enemy minions."%damage)
			targets = self.Game.minionsonBoard(3-self.ID)
			self.dealsAOE(targets, [damage for minion in targets])
		return None
		
		
class MasterofDisguise(Minion):
	Class, race, name = "Rogue", "", "Master of Disguise"
	mana, attack, health = 4, 4, 4
	index = "Classic-Rogue-4-4-4-Minion-None-Master of Disguise-Battlecry"
	needTarget, keyWord, description = True, "", "Battlecry: Give a friendly minion Stealth until your next turn"
	
	def targetExists(self, choice=0):
		return self.selectableFriendlyMinionExists(choice)
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.ID == self.ID and target != self and target.onBoard
		
	#Only onBoard or inHand minions can be given keywords.
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None and (target.onBoard or target.inHand):
			print("Master of Disguise's battlecry gives friendly minion %s Stealth until next turn."%target.name)
			target.status["Temp Stealth"] = 1
		return self, target
		
		
class Kidnapper(Minion):
	Class, race, name = "Rogue", "", "Kidnapper"
	mana, attack, health = 6, 5, 3
	index = "Classic-Rogue-6-5-3-Minion-None-Kidnapper-Combo"
	needTarget, keyWord, description = True, "", "Combo: Return a minion to its owner's hand"
	
	def returnTrue(self, choice=0):
		return self.Game.CounterHandler.cardsPlayedThisTurn[self.ID] != []
		
	def effectCanTrigger(self):
		return self.Game.CounterHandler.cardsPlayedThisTurn[self.ID] != []
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.onBoard
		
	def targetExists(self, choice=0):
		return self.selectableMinionExists(choice)
	#测试洗回牌库的随从是否会加入手牌。
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None and self.Game.CounterHandler.cardsPlayedThisTurn[self.ID] != []:
			print("Kidnapper's Combo effect returns minion %s to its owner's hand"%target.name)
			self.Game.returnMiniontoHand(target)
		return self, target
		
		
"""Shaman cards"""
#Overload minions' played() don't invoke the effectwhenPlayed()
#Overload is not part of the effectwhenPlayed(). Shudderwock repeating Sandstorm Elemental's battlecry won't overload the mana.
class DustDevil(Minion):
	Class, race, name = "Shaman", "Elemental", "Dust Devil"
	mana, attack, health = 1, 3, 1
	index = "Classic-Shaman-1-3-1-Minion-Elemental-Dust Devil-Overloaded-Windfury"
	needTarget, keyWord, description = False, "Windfury", "Windfury. Overload: (2)"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.overload = 2
		
		
class EarthShock(Spell):
	Class, name = "Shaman", "Earth Shock"
	needTarget, mana = True, 1
	index = "Classic-Shaman-1-Spell-Earth Shock"
	description = "Silence a minion. Then deal 1 damage to it."
	
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			damage = (1 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			print("EarthShock is cast and silences %s before dealing %d damage to it."%(target.name, damage))
			target.getsSilenced()
			self.dealsDamage(target, damage)
		return target
		
		
class ForkedLightning(Spell):
	Class, name = "Shaman", "Forked Lightning"
	needTarget, mana = False, 1
	index = "Classic-Shaman-1-Spell-Forked Lightning-Overload"
	description = "Deal 2 damage to 2 random enemy minions. Overload: (2)"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.overload = 2
		
	def available(self):
		return self.Game.minionsonBoard(3-self.ID) != []
		
	def whenEffective(self, target=None, comment="", choice=0):
		damage = (2 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		minions = []
		for minion in self.Game.minionsonBoard(3-self.ID):
			if minion.health > 0:
				minions.append(minion)
				
		if len(minions) > 1:
			targets = np.random.choice(minions, 2, replace=False)
			print("Forked Lightning is cast and deals %d damage to two random minions: "%damage, targets)
			self.dealsAOE(targets, [damage, damage])
		elif len(minions) == 1:
			print("Forked Lightning is cast and deals %d damage to minion "%damage, minions[0].name)
			self.dealsDamage(minions[0], damage)
		return None
		
		
class LightningBolt(Spell):
	Class, name = "Shaman", "Lightning Bolt"
	needTarget, mana = True, 1
	index = "Classic-Shaman-1-Spell-Lightning Bolt-Overload"
	description = "Deal 3 damage. Overload: (1)"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.overload = 1
		
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			damage = (3 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			print("Lightning Bolt is cast and deals %d damage to "%damage, target.name)
			self.dealsDamage(target, damage)
		return target
		
		
class AncestralSpirit(Spell):
	Class, name = "Shaman",  "Ancestral Spirit"
	needTarget, mana = True, 2
	index = "Classic-Shaman-2-Spell-Ancestral Spirit"
	description = "Give a minion 'Deathrattle: Resummon this minion.'"
	def targetExists(self, choice=0):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None and (target.onBoard or target.inHand):
			print("Ancestral Spirit gives %s deathrattle: Summon this minion again."%target.name)
			trigger = ResummonMinion(target)
			target.deathrattles.append(trigger)
			if target.onBoard:
				trigger.connect()
		return target
		
class ResummonMinion(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("Deathrattle: Resummon the minion %s triggers."%self.entity.name)
		newMinion = type(self.entity)(self.entity.Game, self.entity.ID)
		self.entity.Game.summonMinion(newMinion, self.entity.position+1, self.entity.ID)
		
		
class StormforgedAxe(Weapon):
	Class, name, description = "Shaman", "Stormforged Axe", "Overload: (1)"
	mana, attack, durability = 2, 2, 3
	index = "Classic-Shaman-2-2-3-Weapon-Stormforged Axe-Overload"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.overload = 1
		
		
class FarSight(Spell):
	Class, name = "Shaman", "Far Sight"
	needTarget, mana = False, 3
	index = "Classic-Shaman-3-Spell-Far Sight"
	description = "Draw a card. That card costs (3) less"
	def whenEffective(self, target=None, comment="", choice=0):
		print("Far Sight is cast and draws a card. It costs 3 less.")
		card = self.Game.Hand_Deck.drawCard(self.ID)[0]
		if card != None:
			card.mana_set -= 3
			card.mana_set = max(0, card.mana_set)
			self.Game.ManaHandler.calcMana_Single(card)
		return None
		
		
class FeralSpirit(Spell):
	Class, name = "Shaman", "Feral Spirit"
	needTarget, mana = False, 3
	index = "Classic-Shaman-3-Spell-Feral Spirit-Overload"
	description = "Summon two 2/3 Spirit Wolves with Taunt. Overload: (2)"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.overload = 2
		
	def available(self):
		return self.Game.spaceonBoard(self.ID)
		
	def whenEffective(self, target=None, comment="", choice=0):
		print("Feral Spirit is cast and summons two 2/3 Spirit Wolf with Taunt.")
		self.Game.summonMinion([SpiritWolf(self.Game, self.ID) for i in range(2)], (-1, "totheRightEnd"), self.ID)
		return None
		
class SpiritWolf(Minion):
	Class, race, name = "Shaman", "", "Spirit Wolf"
	mana, attack, health = 2, 2, 3
	index = "Classic-Shaman-2-2-3-Minion-None-Spirit Wolf-Taunt-Uncollectible"
	needTarget, keyWord, description = False, "Taunt", "Taunt"
	
#Overload spells targeting adjacent minions will overload multiple times.
#Overload spells repeated by Electra Stormsurge will also overload twice.
class LavaBurst(Spell):
	Class, name = "Shaman", "Lava Burst"
	needTarget, mana = True, 3
	index = "Classic-Shaman-3-Spell-Lava Burst-Overload"
	description = "Deal 5 damage. Overload: (2)"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.overload = 2
		
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			damage = (5 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			print("Lava Burst is cast and deals %d damage to "%damage, target.name)
			self.dealsDamage(target, damage)
		return target
		
		
class LightningStorm(Spell):
	Class, name = "Shaman", "Lightning Storm"
	needTarget, mana = False, 3
	index = "Classic-Shaman-3-Spell-Lightning Storm-Overload"
	description = "Deal 2-3 damage to all enemy minions. Overload: (2)"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.overload = 2
		
	def whenEffective(self, target=None, comment="", choice=0):
		damage2 = (2 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		damage3 = (3 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		targets = self.Game.minionsonBoard(3-self.ID)
		damages = [np.random.choice([damage2, damage3]) for minion in targets]
		print("Lightning Storm is cast and randomly deals %d or %d damage to enemy minions."%(damage2, damage3))
		self.dealsAOE(targets, damages)
		return None
		
		
class ManaTideTotem(Minion):
	Class, race, name = "Shaman", "Totem", "Mana Tide Totem"
	mana, attack, health = 3, 0, 3
	index = "Classic-Shaman-3-0-3-Minion-Totem-Mana Tide Totem"
	needTarget, keyWord, description = False, "", "At the end of your turn, draw a card"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_ManaTideTotem(self)]
		
class Trigger_ManaTideTotem(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["TurnEnds"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("At the end of turn, Mana Tide Totem lets player draw a card.")
		self.entity.Game.Hand_Deck.drawCard(self.entity.ID)
		
		
class UnboundElemental(Minion):
	Class, race, name = "Shaman", "Elemental", "Unbound Elemental"
	mana, attack, health = 3, 2, 4
	index = "Classic-Shaman-3-2-4-Minion-Elemental-Unbound Elemental"
	needTarget, keyWord, description = False, "", "Whenever you play a card with Overload, gain +1/+1"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_UnboundElemental(self)]
		
class Trigger_UnboundElemental(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionPlayed", "SpellPlayed", "WeaponPlayed", "HeroCardPlayed"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject.ID == self.entity.ID and subject.overload > 0
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("Player plays a card %s with Overload and %s gains +1/+1."%(subject.name, self.entity.name))
		self.entity.buffDebuff(1, 1)
		
		
class Doomhammer(Weapon):
	Class, name, description = "Shaman", "Doomhammer", "Windfury, Overload: (2)"
	mana, attack, durability = 5, 2, 8
	index = "Classic-Shaman-5-2-8-Weapon-Doomhammer-Windfury-Overload"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.keyWords["Windfury"] = 1
		self.overload = 2
		
		
class EarthElemental(Minion):
	Class, race, name = "Shaman", "Elemental", "Earth Elemental"
	mana, attack, health = 5, 7, 8
	index = "Classic-Shaman-5-7-8-Minion-Elemental-Earth Elemental-Taunt-Overload"
	needTarget, keyWord, description = False, "Taunt", "Taunt. Overload: (3)"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.overload = 3
		
		
class AlAkirtheWindlord(Minion):
	Class, race, name = "Shaman", "Elemental", "Al'Akir the Windlord"
	mana, attack, health = 8, 3, 5
	index = "Classic-Shaman-8-3-5-Minion-Elemental-Al'Akir the Windlord-Taunt-Charge-Windfury-Divine Shield-Legendary"
	needTarget, keyWord, description = False, "Taunt,Charge,Divine Shield,Windfury", "Taunt,Charge,Divine Shield,Windfury"
	
	
"""Warlock cards"""
class BloodImp(Minion):
	Class, race, name = "Warlock", "Demon", "Blood Imp"
	mana, attack, health = 1, 0, 1
	index = "Classic-Warlock-1-0-1-Minion-Demon-Blood Imp-Stealth"
	needTarget, keyWord, description = False, "Stealth", "At the end of your turn, give another random friendly minion +1 Health"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_BloodImp(self)]
		
class Trigger_BloodImp(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["TurnEnds"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		targets = self.entity.Game.minionsonBoard(self.entity.ID)
		extractfrom(self.entity, targets)
		if targets != []:
			target = np.random.choice(targets)
			print("At the end of turn, Blood Imp gives random friendly minion %s +1 Health."%target.name)
			target.buffDebuff(0, 1)
			
			
class CalloftheVoid(Spell):
	Class, name = "Warlock", "Call of the Void"
	needTarget, mana = False, 1
	index = "Classic-Warlock-1-Spell-Call of the Void"
	description = "Add a random Demon to your hand"
	def whenEffective(self, target=None, comment="", choice=0):
		if self.Game.Hand_Deck.handNotFull(self.ID):
			print("Call of the Void is cast and adds a random demon to player's hand")
			demons = list(self.Game.MinionswithRace["Demon"].values())
			demon = np.random.choice(demons)(self.Game, self.ID)
			self.Game.Hand_Deck.addCardtoHand(demon, self.ID)
		return None
		
		
class FlameImp(Minion):
	Class, race, name = "Warlock", "Demon", "Flame Imp"
	mana, attack, health = 1, 3, 2
	index = "Classic-Warlock-1-3-2-Minion-Demon-Flame Imp-Battlecry"
	needTarget, keyWord, description = False, "", "Battlecry: Deal 3 damage to your hero"
	
	def whenEffective(self, target=None, comment="", choice=0):
		print("Flame Imp's battlecry deals 3 damage to the player.")
		self.dealsDamage(self.Game.heroes[self.ID], 3)
		return self, None
		
		
class Demonfire(Spell):
	Class, name = "Warlock", "Demonfire"
	needTarget, mana = True, 2
	index = "Classic-Warlock-2-Spell-Demonfire"
	description = "Deal 2 damage to a minion. If it's friendly Demon, give it +2/+2 instead"
	def targetExists(self, choice=0):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			if "Demon" in target.race and target.ID == self.ID:
				print("Demonfire gives friendly demon %s +2/+2"%target.name)
				target.buffDebuff(2, 2)
			else:
				damage = (2 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
				print("Demonfire is cast and deals %d damage to "%damage, target.name)
				self.dealsDamage(target, damage)
		return target
		
#If the hands are full, both of the cards will be milled. Tested with Archmage Vargoth.
class SenseDemon(Spell):
	Class, name = "Warlock", "Sense Demon"
	needTarget, mana = False, 3
	index = "Classic-Warlock-3-Spell-Sense Demon"
	description = "Draw 2 Demons from your deck"
	def whenEffective(self, target=None, comment="", choice=0):
		print("Sense Demon is cast and player draws two demon from the deck.")
		demonsinDeck = []
		for card in self.Game.Hand_Deck.decks[self.ID]:
			if card.cardType == "Minion" and "Demon" in card.race:
				demonsinDeck.append(card)
				
		if demonsinDeck != []:
			if len(demonsinDeck) == 1:
				self.Game.Hand_Deck.drawCard(self.ID, demonsinDeck[0])
			else: #At least two demons in deck
				demons = np.random.choice(demonsinDeck, 2, replace=False)
				self.Game.Hand_Deck.drawCard(self.ID, demons)
		return None
		
		
class SummoningPortal(Minion):
	Class, race, name = "Warlock", "", "Summoning Portal"
	mana, attack, health = 4, 0, 4
	index = "Classic-Warlock-4-0-4-Minion-None-Summoning Portal"
	needTarget, keyWord, description = False, "", "Your minions cost (2) less, but not less than (1)"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.manaAura = YourMinionsCost2LessbutNoLessthan1(self)
		self.appearResponse = [self.activateAura]
		self.disappearResponse = [self.deactivateAura]
		self.silenceResponse = [self.deactivateAura]
		
	def activateAura(self):
		print("Summoning Portal's aura is included and player's minions now cost 2 less( no less than 1).")
		self.Game.ManaHandler.CardAuras.append(self.manaAura)
		self.Game.ManaHandler.calcMana_All()
		
	def deactivateAura(self):
		print("Summoning Portal's aura is removed and player's minions no longer cost 2 less.")
		extractfrom(self.manaAura, self.Game.ManaHandler.CardAuras)
		self.Game.ManaHandler.calcMana_All()
		
class YourMinionsCost2LessbutNoLessthan1:
	def __init__(self, minion):
		self.minion = minion
		self.temporary = False
		
	def handleMana(self, target):
		if target.cardType == "Minion" and target.ID == self.minion.ID:
			target.mana -= 2
			target.mana = max(target.mana, 1)
			
			
class Felguard(Minion):
	Class, race, name = "Warlock", "Demon", "Felguard"
	mana, attack, health = 3, 3, 5
	index = "Classic-Warlock-3-3-5-Minion-Demon-Felguard-Taunt-Battlecry"
	needTarget, keyWord, description = False, "Taunt", "Taunt. Battlecry: Destroy one of your Mana Crystals"
	
	def whenEffective(self, target=None, comment="", choice=0):
		print("Felguard's battlecry destroys a mana crystal.")
		self.Game.ManaHandler.destroyManaCrystal(1, self.ID)
		return self, None
		
		
class VoidTerror(Minion):
	Class, race, name = "Warlock", "Demon", "Void Terror"
	mana, attack, health = 3, 3, 3
	index = "Classic-Warlock-3-3-3-Minion-Demon-Void Terror-Battlecry"
	needTarget, keyWord, description = False, "", "Battlecry: Destroy both adjacent minions and gain their Attack and Health"
	
	def whenEffective(self, target=None, comment="", choice=0):
		if self.onBoard: #Can't trigger if returned to hand already, since cards in hand don't have adjacent minions on board.
			adjacentMinions, distribution = self.Game.findAdjacentMinions(self)
			if adjacentMinions != []:
				attackGain = 0
				healthGain = 0
				for minion in adjacentMinions:
					attackGain += max(0, minion.attack)
					healthGain += max(0, minion.health)
					minion.dead = True
					
				print("Void Terror's battlecry lets minion destroy adjacent minions and gain their stats.")
				self.buffDebuff(attackGain, healthGain)
		return self, None
		
		
class PitLord(Minion):
	Class, race, name = "Warlock", "Demon", "Pit Lord"
	mana, attack, health = 4, 5, 6
	index = "Classic-Warlock-4-5-6-Minion-Demon-Pit Lord-Battlecry"
	needTarget, keyWord, description = False, "", "Battlecry: Deal 5 damage to your hero"
	
	def whenEffective(self, target=None, comment="", choice=0):
		print("Pit Lord's battlecry deals 5 damage to player.")
		self.dealsDamage(self.Game.heroes[self.ID], 5)
		return self, None
		
		
class Shadowflame(Spell):
	Class, name = "Warlock", "Shadowflame"
	needTarget, mana = True, 4
	index = "Classic-Warlock-4-Spell-Shadowflame"
	description = "Destroy a friendly minion and deals its Attack damage to all enemy minions"
	def targetExists(self, choice=0):
		return self.selectableFriendlyMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.ID == self.ID and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			damage = (max(0, target.attack) + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			target.dead = True
			print("Shadowflame is cast, destroys friendly minion %s and deals %d damage to all enemy minions"%(target.name, damage))
			targets = self.Game.minionsonBoard(3-self.ID)
			self.dealsAOE(targets, [damage for minion in targets])
		return target
		
		
class BaneofDoom(Spell):
	Class, name = "Warlock", "Bane of Doom"
	needTarget, mana = True, 5
	index = "Classic-Warlock-5-Spell-Bane of Doom"
	description = "Deal 2 damage to a character. It that kills it, summon a random Demon"
	def targetExists(self, choice=0):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			damage = (2 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			print("Bane of Doom is cast and deals %d damage to  "%damage, target.name)
			objtoTakeDamage, targetSurvival = self.dealsDamage(target, damage)
			if targetSurvival > 1 and self.Game.spaceonBoard(self.ID) > 0:
				print("Bane of Doom kills the target minion and summons a random demon.")
				demons = list(self.Game.MinionswithRace["Demon"].values())
				self.Game.summonMinion(np.random.choice(demons)(self.Game, self.ID), -1, self.ID)
		return target
		
		
class SiphonSoul(Spell):
	Class, name = "Warlock", "Siphon Soul"
	needTarget, mana = True, 6
	index = "Classic-Warlock-6-Spell-Siphon Soul"
	description = "Destroy a minion. Restore 3 Health to your hero"
	def targetExists(self, choice=0):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			heal = 3 * (2 ** self.countHealDouble())
			print("Siphon Soul is cast and destroys minion %s. Then restores %d health to player."%(target.name, heal))
			target.dead = True
			self.restoresHealth(self.Game.heroes[self.ID], heal)
		return target
		
		
class Siegebreaker(Minion):
	Class, race, name = "Warlock", "Demon", "Siegebreaker"
	mana, attack, health = 7, 5, 8
	index = "Classic-Warlock-7-5-8-Minion-Demon-Siegebreaker-Taunt"
	needTarget, keyWord, description = False, "Taunt", "Your other Demons have +1 Attack"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.auras["Buff Aura"] = BuffAura_Dealer_All(self, self.applicable, 1, 0)
		
	def applicable(self, target):
		return "Demon" in target.race
		
		
class TwistingNether(Spell):
	Class, name = "Warlock", "Twisting Nether"
	needTarget, mana = False, 8
	index = "Classic-Warlock-8-Spell-Twisting Nether"
	description = "Destroy all minions"
	def whenEffective(self, target=None, comment="", choice=0):
		print("Twisting Nether is cast and destroys all minions.")
		for minion in self.Game.minionsonBoard(1) + self.Game.minionsonBoard(2):
			minion.dead = True
		return None
		
#Won't trigger Knife Juggler, but will trigger Illidan Stormrage
#Will trigger Mirror Entity, however.
class LordJaraxxus(Minion):
	Class, race, name = "Warlock", "Demon", "Lord Jaraxxus"
	mana, attack, health = 9, 3, 15
	index = "Classic-Warlock-9-3-15-Minion-Demon-Lord Jaraxxus-Battlecry-Legendary"
	needTarget, keyWord, description = False, "", "Battlecry: Destroy your hero and replace it with Lord Jaraxxus"
	
	#打出过程：如果大王被提前消灭了，则不会触发变身过程。此时应该返回self，成为一个普通的早夭随从。、
	#如果大王留在场上或者被返回手牌，则此时应该会变身成为英雄，返回应该是None
	
	#If invoked by Shudderwock, then Shudderwock will transform and replace your hero with Jaraxxus.
	#Then Shudderwock's battlecry is stopped.
	def whenEffective(self, target=None, comment="", choice=0):
		print("Lord Jaraxxus' battlecry replaces player's hero with Lord Jaraxxus.")
		if self.inHand: #Returned to hand. Assume the card in hand is gone and then hero still gets replaced.
			self.Game.Hand_Deck.extractfromHand(self)
			LordJaraxxus_Hero(self.Game, self.ID).replaceHero()
			return None, None
		elif self.onBoard:
			self.disappears()
			self.Game.removeMinionorWeapon(self)
			LordJaraxxus_Hero(self.Game, self.ID).replaceHero()
			print("The weapon is ", self.Game.availableWeapon(self.ID))
			return None, None
		else: #Jaraxxus is killed before battlecry can trigger.
			return self, None
			
class Inferno(Minion):
	Class, race, name = "Warlock", "Demon", "Inferno"
	mana, attack, health = 6, 6, 6
	index = "Classic-Warlock-6-6-6-Minion-Demon-Inferno-Uncollectible"
	needTarget, keyWord, description = False, "", ""
	
class Inferno_HeroPower(HeroPower):
	name, needTarget = "Inferno!", False
	index = "Warlock-2-Hero Power-Inferno!"
	description = "Summon a 6/6 Inferno"
	def available(self, choice=0):
		if self.heroPowerTimes >= self.heroPowerChances_base + self.heroPowerChances_extra:
			return False
		if self.Game.spaceonBoard(self.ID) < 1:
			return False
		return True
		
	def effect(self, target=None, choice=0):
		print("Hero Power Inferno! summons a 6/6 Inferno")
		self.Game.summonMinion(Inferno(self.Game, self.ID), -1, self.ID, "")
		return 0
		
class BloodFury(Weapon):
	Class, name, description = "Warlock", "Blood Fury", ""
	mana, attack, durability = 3, 3, 8
	index = "Classic-Warlock-3-3-8-Weapon-Blood Fury-Uncollectible"
	
class LordJaraxxus_Hero(Hero):
	mana, weapon, description = 0, BloodFury, ""
	Class, name, heroPower, armor = "Warlock", "Lord Jaraxxus", Inferno_HeroPower, 0
	index = ""
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.health, self.health_upper, self.armor = 15, 15, 0
		
		
"""Warrior cards"""
class InnerRage(Spell):
	Class, name = "Warrior", "Inner Rage"
	needTarget, mana = True, 0
	index = "Classic-Warrior-0-Spell-Inner Rage"
	description = "Deal 1 damage to a minion and give it +2 Attack"
	def targetExists(self, choice=0):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			damage = (1 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			print("Inner Rage is cast and deals %d damage to %s and gives it +2 attack."%(damage, target.name))
			self.dealsDamage(target, damage)
			target.buffDebuff(2, 0)
		return target
		
		
class ShieldSlam(Spell):
	Class, name = "Warrior", "Shield Slam"
	needTarget, mana = True, 1
	index = "Classic-Warrior-1-Spell-Shield Slam"
	description = "Deal 1 damage to a minion for each Armor you have"
	def available(self):
		if self.Game.heroes[self.ID].armor > 0 or self.countSpellDamage() > 0:
			return self.selectableMinionExists()
		return False
		
	def targetExists(self, choice=0):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			damage = (self.Game.heroes[self.ID].armor + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			print("Shield Slam is cast and deals %d damage to "%damage, target.name)
			self.dealsDamage(target, damage)
		return target
		
		
class Upgrade(Spell):
	Class, name = "Warrior", "Upgrade!"
	needTarget, mana = False, 1
	index = "Classic-Warrior-1-Spell-Upgrade!"
	description = "If your have a weapon, give it +1/+1. Otherwise, equip a 1/3 weapon"
	def whenEffective(self, target=None, comment="", choice=0):
		weapon = self.Game.availableWeapon(self.ID)
		if weapon == None:
			print("Upgrade! is cast and player equips a 1/3 weapon.")
			self.Game.equipWeapon(HeavyAxe(self.Game, self.ID))
		else:
			print("Upgrade! is cast and player's weapon gains +1/+1.")
			weapon.gainStat(1, 1)
		return None
		
class HeavyAxe(Weapon):
	Class, name, description = "Warrior", "Heavy Axe", ""
	mana, attack, durability = 1, 1, 3
	index = "Classic-Warrior-1-1-3-Weapon-Heavy Axe-Uncollectible"
	
	
class Armorsmith(Minion):
	Class, race, name = "Warrior", "", "Armorsmith"
	mana, attack, health = 2, 1, 4
	index = "Classic-Warrior-2-1-4-Minion-None-Armorsmith"
	needTarget, keyWord, description = False, "", "Whenever a friendly minion takes damage, gain +1 Armor"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_Armorsmith(self)]
		
class Trigger_Armorsmith(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionTakesDamage"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and target.ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("Friendly minion %s takes damage and %s lets player gain 1 Armor."%(target.name, self.entity.name))
		self.entity.Game.heroes[self.entity.ID].gainsArmor(1)
		
		
class BattleRage(Spell):
	Class, name = "Warrior", "Battle Rage"
	needTarget, mana = False, 2
	index = "Classic-Warrior-2-Spell-Battle Rage"
	description = "Draw a card for each damaged friendly character"
	def whenEffective(self, target=None, comment="", choice=0):
		print("Battle Rage is cast and player draws a card for each damaged friendly.")
		numDamagedCharacters = 0
		for minion in self.Game.minionsonBoard(self.ID):
			if minion.health < minion.health_upper:
				numDamagedCharacters += 1
		if self.Game.heroes[self.ID].health < self.Game.heroes[self.ID].health_upper:
			numDamagedCharacters += 1
			
		for i in range(numDamagedCharacters):
			self.Game.Hand_Deck.drawCard(self.ID)
		return None
#Creates an on-going effect(Aura) that affects your minions. Prevents damage when minion at 1 Health already.
#Reduces damage so that it can only reduce the Health to 1
#与Snapjaw Shellfighter的结算顺序->Shellfighter先上场，然后是命令怒吼，1血生物攻击与剧毒随从，Shellfighter先结算，承担伤害，因为剧毒死亡。
#先命令怒吼，然后Shellfighter，1血生物攻击与剧毒随从，仍然是Shellfighter先结算，无关先后顺序
#先执行Shellfighter的预伤害扳机结算，然后在随从自己的damageRequest中结算是否要将伤害无效或者是减少。
class CommandingShout(Spell):
	Class, name = "Warrior", "Commanding Shout"
	needTarget, mana = False, 2
	index = "Classic-Warrior-2-Spell-Commanding Shout"
	description = "Your minions can't be reduced below 1 Health this turn. Draw a card"
	def whenEffective(self, target=None, comment="", choice=0):
		print("Commanding Shout will prevent player's minions' health be reduced below 1 this turn. Player draws a card.")
		self.Game.playerStatus[self.ID]["Commanding Shout"] += 1
		self.Game.turnEndTrigger.append(RemoveCommandingShoutEffect(self.Game, self.ID))
		self.Game.Hand_Deck.drawCard(self.ID)
		return None
		
class RemoveCommandingShoutEffect:
	def __init__(self, Game, ID):
		self.Game = Game
		self.ID = ID
		
	def trigger(self):
		print("Player %d's Commanding Shout effect vanishes."%self.ID)
		self.Game.playerStatus[self.ID]["Commanding Shout"] -= 1
		
		
class CruelTaskmaster(Minion):
	Class, race, name = "Warrior", "", "Cruel Taskmaster"
	mana, attack, health = 2, 2, 2
	index = "Classic-Warrior-2-2-2-Minion-None-Cruel Taskmaster-Battlecry"
	needTarget, keyWord, description = True, "", "Battlecry: Deal 1 damage to a minion and give it +2 Attack"
	
	def targetExists(self, choice=0):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.onBoard
		
	#Minion in deck can't get buff/reset.
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			print("Cruel Taskmaster's battlecry deals 1 damage to minion %s and gives it +2 attack."%target.name)
			self.dealsDamage(target, 1)
			target.buffDebuff(2, 0)
		return self, target
		
		
class Rampage(Spell):
	Class, name = "Warrior", "Rampage"
	needTarget, mana = True, 2
	index = "Classic-Warrior-2-Spell-Rampage"
	description = "Give a damaged minion +3/+3"
	def targetExists(self, choice=0):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.health < target.health_upper and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			print("Rampage is cast and gives damaged minion %s +3/+3."%target.name)
			target.buffDebuff(3, 3)
		return target
		
#Deals 2 damage to Frothing Berserker, Berserker gains +1 attack then this draws card.
class Slam(Spell):
	Class, name = "Warrior", "Slam"
	needTarget, mana = True, 2
	index = "Classic-Warrior-2-Spell-Slam"
	description = "Deal 2 damage to a minion. If it survives, draw a card"
	def targetExists(self, choice=0):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			damage = (2 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			print("Slam is cast and deals %d damage to "%damage, target.name)
			self.dealsDamage(target, damage)
			if target.health > 0 and target.dead == False:
				print("The minion survives and Slam lets player draws a card.")
				self.Game.Hand_Deck.drawCard(self.ID)
		return target
		
		
class FrothingBerserker(Minion):
	Class, race, name = "Warrior", "", "Frothing Berserker"
	mana, attack, health = 3, 2, 4
	index = "Classic-Warrior-3-2-4-Minion-None-Frothing Berserker"
	needTarget, keyWord, description = False, "", "Whenever a minion takes damage, gain +1 Attack"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_FrothingBerserker(self)]
		
class Trigger_FrothingBerserker(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionTakesDamage"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("Minion %s takes damage and %s gains +1 Attack."%(target.name, self.entity.name))
		self.entity.buffDebuff(1, 0)
		
		
class ArathiWeaponsmith(Minion):
	Class, race, name = "Warrior", "", "Arathi Weaponsmith"
	mana, attack, health = 4, 3, 3
	index = "Classic-Warrior-4-3-3-Minion-None-Arathi Weaponsmith-Battlecry"
	needTarget, keyWord, description = False, "", "Battlecry: Equip a 2/2 weapon"
	#Triggers regardless of minion's status.
	def whenEffective(self, target=None, comment="", choice=0):
		print("Arathi Weaponsmith's battlecry lets player equip a 2/2 weapon.")
		self.Game.equipWeapon(BattleAxe(self.Game, self.ID))
		return self, None
		
class BattleAxe(Weapon):
	Class, name, description = "Warrior", "Battle Axe", ""
	mana, attack, durability = 1, 2, 2
	index = "Classic-Warrior-1-2-2-Weapon-Battle Axe-Uncollectible"
	
	
class MortalStrike(Spell):
	Class, name = "Warrior", "Mortal Strike"
	needTarget, mana = True, 4
	index = "Classic-Warrior-4-Spell-Mortal Strike"
	description = "Deal 4 damage. If your have 12 or less Health, deal 6 instead"
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			if self.Game.heroes[self.ID].health < 13:
				damage = (6 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			else:
				damage = (4 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
				
			print("Mortal Strike is cast and deals %d damage to "%damage, target.name)
			self.dealsDamage(target, damage)
		return target
		
		
class Brawl(Spell):
	Class, name = "Warrior", "Brawl"
	needTarget, mana = False, 5
	index = "Classic-Warrior-5-Spell-Brawl"
	description = "Destroy all minions except one. (Chosen randomly)"
	def whenEffective(self, target=None, comment="", choice=0):
		print("Brawl is cast and only one random minion survives.")
		minions = self.Game.minionsonBoard(1) + self.Game.minionsonBoard(2)
		if len(minions) > 1:
			survivor = np.random.choice(minions)
			for minion in minions:
				if minion != survivor:
					minion.dead = True
		return None
		
		
class Gorehowl(Weapon):
	Class, name, description = "Warrior", "Gorehowl", "Attacking a minion costs 1 Attack instead of 1 Durability"
	mana, attack, durability = 7, 7, 1
	index = "Classic-Warrior-7-7-1-Weapon-Gorehowl"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_Gorehowl(self)]
		self.canLoseDurability = True
		
	def loseDurability(self):
		if self.canLoseDurability:
			print("Weapon %s loses 1 Durability"%self.name)
			self.durability -= 1
		else:
			print("Weapon %s loses 1 Attack instead of Durability"%self.name)
			self.attack -= 1
			self.Game.heroes[self.ID].attack = self.Game.heroes[self.ID].attack_bare + max(0, self.attack)
			self.canLoseDurability = True #把武器的可以失去耐久度恢复为True
			if self.attack < 1:
				self.tobeDestroyed = True
				
class Trigger_Gorehowl(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["HeroAttackingMinion"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return subject == self.entity.Game.heroes[self.entity.ID] and target.cardType == "Minion" and self.entity.onBoard
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("Player's weapon Gorehowl won't lose Durability when attacking minion.")
		self.entity.canLoseDurability = False
		
		
class GrommashHellscream(Minion):
	Class, race, name = "Warrior", "", "Grommash Hellscream"
	mana, attack, health = 8, 4, 9
	index = "Classic-Warrior-8-4-9-Minion-None-Grommash Hellscream-Charge-Legendary"
	needTarget, keyWord, description = False, "Charge", "Charge. Has +6 attack while damaged"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggers["StatChanges"] = [self.handleEnrage]
		self.activated = False
		
	def handleEnrage(self):
		if self.silenced == False and self.onBoard:
			if self.activated == False and self.health < self.health_upper:
				self.activated = True
				self.statChange(6, 0)
			elif self.activated and self.health >= self.health_upper:
				self.activated = False
				self.statChange(-6, 0)