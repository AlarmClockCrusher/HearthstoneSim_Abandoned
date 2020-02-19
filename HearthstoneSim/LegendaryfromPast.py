from CardTypes import *
from VariousHandlers import *
from Triggers_Auras import *

from Basic import ArcaneMissiles
from Classic import LeperGnome
from CardIndices import Weapons, BasicHeroPowers, UpgradedHeroPowers, HunterSecrets

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
	
	
"""Curse of Naxxramas"""
class BaronRivendare(Minion):
	Class, race, name = "Neutral", "", "Baron Rivendare"
	mana, attack, health = 4, 1, 7
	index = "Naxxramas-Neutral-4-1-7-Minion-None-Baron Rivendare-Legendary"
	needTarget, keyWord, description = False, "", "Your minions trigger their Deathrattless twice"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.appearResponse = [self.activateAura]
		self.silenceResponse = [self.deactivateAura]
		self.disappearResponse = [self.deactivateAura]
		
	def activateAura(self):
		print("Baron Rivendare appears and minion Deathrattles will trigger twice.")
		self.Game.playerStatus[self.ID]["Deathrattle Trigger Twice"] += 1
		
	#Necromancer has to be alive to make deathrattles trigger twice.			
	def deactivateAura(self):
		print("Baron Rivendare no longer makes minion Deathrattles trigger twice.")
		if self.Game.playerStatus[self.ID]["Deathrattle Trigger Twice"] > 0:
			self.Game.playerStatus[self.ID]["Deathrattle Trigger Twice"] -= 1
			
			
class Feugen(Minion):
	Class, race, name = "Neutral", "", "Feugen"
	mana, attack, health = 5, 4, 7
	index = "Naxxramas-Neutral-5-4-7-Minion-None-Feugen-Deathrattle-Legendary"
	needTarget, keyWord, description = False, "", "Deathrattle: If Stalagg also died this game, summon Thaddius"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [SummonThaddius_Feugen(self)]
		
class SummonThaddius_Feugen(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("Deathrattle: If Stalagg also died this game, summon Thaddius triggers.")
		if "Naxxramas-Neutral-5-7-4-Minion-None-Stalagg-Deathrattle-Legendary" in self.entity.Game.CounterHandler.minionsDiedThisGame[1]:
			self.entity.Game.summonMinion(Thaddius(self.entity.Game, self.entity.ID), self.entity.position+1, self.entity.ID)
		elif "Naxxramas-Neutral-5-7-4-Minion-None-Stalagg-Deathrattle-Legendary" in self.entity.Game.CounterHandler.minionsDiedThisGame[2]:
			self.entity.Game.summonMinion(Thaddius(self.entity.Game, self.entity.ID), self.entity.position+1, self.entity.ID)
			
class Stalagg(Minion):
	Class, race, name = "Neutral", "", "Stalagg"
	mana, attack, health = 5, 7, 4
	index = "Naxxramas-Neutral-5-7-4-Minion-None-Stalagg-Deathrattle-Legendary"
	needTarget, keyWord, description = False, "", "Deathrattle: If Feugen also died this game, summon Thaddius"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [SummonThaddius_Stalagg(self)]
		
class SummonThaddius_Stalagg(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("Deathrattle: If Feugen also died this game, summon Thaddius triggers.")
		if "Naxxramas-Neutral-5-4-7-Minion-None-Feugen-Deathrattle-Legendary" in self.entity.Game.CounterHandler.minionsDiedThisGame[1]:
			self.entity.Game.summonMinion(Thaddius(self.entity.Game, self.entity.ID), self.entity.position+1, self.entity.ID)
		elif "Naxxramas-Neutral-5-4-7-Minion-None-Feugen-Deathrattle-Legendary" in self.entity.Game.CounterHandler.minionsDiedThisGame[2]:
			self.entity.Game.summonMinion(Thaddius(self.entity.Game, self.entity.ID), self.entity.position+1, self.entity.ID)
			
class Thaddius(Minion):
	Class, race, name = "Neutral", "", "Thaddius"
	mana, attack, health = 10, 11, 11
	index = "Naxxramas-Neutral-10-11-11-Minion-None-Thaddius-Legendary-Uncollectible"
	needTarget, keyWord, description = False, "", ""
	
	
class KelThuzad(Minion):
	Class, race, name = "Neutral", "", "Kel'Thuzad"
	mana, attack, health = 8, 6, 8
	index = "Naxxramas-Neutral-8-6-8-Minion-None-Kel'Thuzad-Legendary"
	needTarget, keyWord, description = False, "", "At the end of each turn, summon all friendly minions that died this turn"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_KelThuzad(self)]
		
class Trigger_KelThuzad(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["TurnEnds"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("At the end of each turn, %s summons all friendly minions that died this turn."%self.entity.name)
		#Kel'Thuzad resurrects dead minions in the same order they died.
		if self.entity.Game.CounterHandler.minionsDiedThisTurn[self.entity.ID] != []:
			print("The minions to potentially summon:", self.entity.Game.CounterHandler.minionsDiedThisTurn[self.entity.ID])
			numSummon = min(self.entity.Game.spaceonBoard(self.entity.ID), len(self.entity.Game.CounterHandler.minionsDiedThisTurn[self.entity.ID]))
			if numSummon > 0:
				indices = self.entity.Game.CounterHandler.minionsDiedThisTurn[self.entity.ID][0:numSummon]
				minionstoSummon = [self.entity.Game.cardPool[index](self.entity.Game, self.entity.ID) for index in indices]
				minionstoSummon.reverse() #Reverse the order of the list so that the first minion that died appears leftmost of the sequence
				self.entity.Game.summonMinion(minionstoSummon, (self.entity.position, "totheRight"), self.entity.ID)
				
				
class Loatheb(Minion):
	Class, race, name = "Neutral", "", "Loatheb"
	mana, attack, health = 5, 5, 5
	index = "Naxxramas-Neutral-5-5-5-Minion-None-Loatheb-Battlecry-Legendary"
	needTarget, keyWord, description = False, "", "Battlecry: Enemy spells cost (5) more next turn"
	
	def whenEffective(self, target=None, comment="", choice=0):
		print("Loatheb's battlecry makes enemy spells cost (5) more next turn.")
		self.Game.ManaHandler.CardAuras_Backup.append(SpellsCost5MoreNextTurn(self.Game, 3-self.ID))
		return self, None
		
class SpellsCost5MoreNextTurn(TempManaEffect):
	def handleMana(self, target):
		if target.cardType == "Spell" and target.ID == self.ID:
			target.mana += 5
			
			
class Maexxna(Minion):
	Class, race, name = "Neutral", "Beast", "Maexxna"
	mana, attack, health = 6, 2, 8
	index = "Naxxramas-Neutral-6-2-8-Minion-Beast-Maexxna-Poisonous-Legendary"
	needTarget, keyWord, description = False, "Poisonous", "Poisonous"
	
	
"""Goblin vs Gnome"""
class Blingtron3000(Minion):
	Class, race, name = "Neutral", "Mech", "Blingtron 3000"
	mana, attack, health = 5, 3, 4
	index = "GoblinvsGnome-Neutral-5-3-4-Minion-Mech-Blingtron 3000-Battlecry-Legendary"
	needTarget, keyWord, description = False, "", "Battlecry: Equip a random weapon for each player"
	
	def whenEffective(self, target=None, comment="", choice=0):
		print("Blingtron 3000's battlecry equips a weapon for each player")
		weapon1, weapon2 = np.random.choice(list(Weapons.values()), 2, replace=True)
		self.Game.equipWeapon(weapon1(self.Game, self.ID))
		self.Game.equipWeapon(weapon2(self.Game, 3-self.ID))
		return self, None
		
		
class HemetNesingwary(Minion):
	Class, race, name = "Neutral", "", "Hemet Nesingwary"
	mana, attack, health = 5, 6, 3
	index = "GoblinvsGnome-Neutral-5-6-3-Minion-None-Hemet Nesingwary-Battlecry-Legendary"
	needTarget, keyWord, description = True, "", "Battlecry: Destroy a Beast"
	
	def targetExists(self, choice=0):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and "Beast" in target.race and target != self and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			print("Hemet Nesingwary's battlecry destroys Beast", target.name)
			target.dead = True
		return self, target
		
		
class MimironsHead(Minion):
	Class, race, name = "Neutral", "Mech", "Mimiron's Head"
	mana, attack, health = 5, 4, 5
	index = "GoblinvsGnome-Neutral-5-4-5-Minion-Mech-Mimiron's Head-Legendary"
	needTarget, keyWord, description = False, "", "At the start of your turn, if your have at least 3 Mechs, destroy them all and form V-07-TR-ON"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_MimironsHead(self)]
		
class Trigger_MimironsHead(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["TurnStarts"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		if self.entity.onBoard and ID == self.entity.ID:
			numMechsControlled = 0
			for minion in self.entity.Game.minionsonBoard(self.entity.ID):
				if "Mech" in minion.race:
					numMechsControlled += 1
			if numMechsControlled > 2:
				return True
		return False
		
	#This fusion forces the minions to leave board early and trigger their deathrattles.
	#If the deathrattles fill the board, the V-07-TR-ON won't be summoned
	#Also, two Mimiron's Head will only summon one V-07-TR-ON, since the second Mimiron's Head leaves board before it can trigger
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("At the start of turn, player control 3 or more Mech, and %s destroys all of them to summon V-07-TR-ON"%self.entity.name)
		for minion in self.entity.Game.minionsonBoard(self.entity.ID):
			if "Mech" in minion.race:
				minion.dead = True
				
		self.entity.Game.gathertheDead(decideWinner=False, deadMinionsLinger=True)
		self.entity.Game.summonMinion(V07TRON(self.entity.Game, self.entity.ID), self.entity.position+1, self.entity.ID)
		for minion in fixedList(self.entity.Game.minions[1] + self.entity.Game.minions[2]):
			if minion.onBoard == False:
				self.entity.Game.removeMinionorWeapon(minion)
				
class V07TRON(Minion):
	Class, race, name = "Neutral", "Mech", "V-07-TR-ON"
	mana, attack, health = 8, 4, 8
	index = "GoblinvsGnome-Neutral-8-4-8-Minion-Mech-V-07-TR-ON-Charge-Mega-Windfury-Legendary-Uncollectible"
	needTarget, keyWord, description = False, "Charge,Mega Windfury", "Charge, Mega Windfury"
	
	
class Gazlowe(Minion):
	Class, race, name = "Neutral", "", "Gazlowe"
	mana, attack, health = 6, 3, 6
	index = "GoblinvsGnome-Neutral-6-3-6-Minion-None-Gazlowe-Legendary"
	needTarget, keyWord, description = False, "", "Whenever you cast a 1-mana spell, add a random Mech to your hand"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_Gazlowe(self)]
		
class Trigger_Gazlowe(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["SpellPlayed"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject.ID == self.entity.ID and number == 1
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("Player casts a 1-mana spell and %s summons adds a random Mech to player's hand"%self.entity.name)
		mechs = list(self.entity.Game.MinionswithRace["Mech"].values())
		self.entity.Game.Hand_Deck.addCardtoHand(np.random.choice(mechs), self.entity.ID, "CreateUsingType")
		
		
class MogortheOgre(Minion):
	Class, race, name = "Neutral", "", "Mogor the Ogre"
	mana, attack, health = 6, 7, 6
	index = "GoblinvsGnome-Neutral-6-7-6-Minion-None-Mogor the Ogre-Legendary"
	needTarget, keyWord, description = False, "", "All minions have a 50% chance to attack the wrong enemy"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_MogortheOgre(self)]
		
class Trigger_MogortheOgre(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["HeroAttacksHero", "HeroAttacksMinion", "MinionAttacksMinion", "MinionAttacksHero",
						"BattleFinished"])
		self.triggeredDuringBattle = False
		
	def returnOtherEnemies(self, subject, target):
		enemyID = 3 - subject.ID #即使其他扳机可能把目标改成友方目标，也会在此扳机触发时将其改回对方角色。
		otherEnemies = []
		if self.entity.Game.heroes[enemyID] != target:
			otherEnemies.append(self.entity.Game.heroes[enemyID])
		for minion in self.entity.Game.minionsonBoard(enemyID):
			if minion != target:
				otherEnemies.append(minion)
		return otherEnemies
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		print("Checking the response for Mogor the Ogre to signal", signal)
		if "Attacks" in signal:
			if target != None and self.entity.onBoard:
				#Can only trigger if there are enemies other than the target.
				#游荡怪物配合误导可能会将对英雄的攻击目标先改成对召唤的随从，然后再发回敌方英雄，说明攻击一个错误的敌人应该也是游戏现记录的目标之外的角色。
				if self.triggeredDuringBattle == False and self.returnOtherEnemies(subject, self.entity.Game.target) != []:
					print("Mogor the Ogre's trigger is available in this battle, and there are other enemies than the current one for the attacker")
					return True
		else:
			print("Mogor's trigger is always allowed to reset itself after the battle finishes.")
			return True
		return False
		
	def trigger(self, signal, ID, subject, target, number, comment, choice=0):
		if self.entity.onBoard:
			if signal == "BattleFinished": #Reset the Forgetful for next battle event.
				self.triggeredDuringBattle = False
				print("The battle finishes and Mogor the Ogre's trigger is reset")
			elif target != None: #Attack signal
				otherEnemies = self.returnOtherEnemies(subject, self.entity.Game.target)
				if otherEnemies != []:
					#玩家命令的一次攻击中只能有一次触发机会。只要满足进入50%判定的条件，即使没有最终生效，也不能再次触发。
					self.triggeredDuringBattle = True
					print("Mogor the Ogre has a 50/50 chance to divert %s's attack to a wrong enemy."%subject.name)
					if np.random.randint(2) == 1:
						self.entity.Game.target = np.random.choice(otherEnemies)
						print("The target of attack is diverted by Mogor the Ogre to another random enemy ", self.entity.Game.target.name)
					else:
						print("The 50/50 chance didn't happen.")
						
class ArmorPlating(Spell):
	Class, name = "Neutral", "Armor Plating"
	needTarget, mana = True, 1
	index = "GoblinvsGnome-Neutral-1-Spell-Armor Plating-Uncollectible"
	description = "Give a minion +1 Health"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			print("Armor Plating gives minion %s +1 health"%target.name)
			target.buffDebuff(0, 1)
		return target
		
class EmergencyCoolant(Spell):
	Class, name = "Neutral", "Emergency Coolant"
	needTarget, mana = True, 1
	index = "GoblinvsGnome-Neutral-1-Spell-Emergency Coolant-Uncollectible"
	description = "Freeze a minion"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			print("Emergency Coolant Freezes minion", target.name)
			target.getsFrozen()
		return target
		
class FinickyCloakshield(Spell):
	Class, name = "Neutral", "Finicky Cloakshield"
	needTarget, mana = True, 1
	index = "GoblinvsGnome-Neutral-1-Spell-Finicky Cloakshield-Uncollectible"
	description = "Give a friendly minion Stealth until your next turn"
	def available(self):
		return self.selectableFriendlyMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.ID == self.ID and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			print("Finicky Cloakshield gives friendly minion %s Stealth until player's next turn"%target.name)
			target.status["Temp Stealth"] += 1
		return target
		
class ReversingSwitch(Spell):
	Class, name = "Neutral", "Reversing Switch"
	needTarget, mana = True, 1
	index = "GoblinvsGnome-Neutral-1-Spell-Reversing Switch-Uncollectible"
	description = "Swap a minion's Attack and Health"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			print("Reversing Switch swaps minion %s Attack and Health"%target.name)
			target.statReset(target.health, target.attack)
		return target
		
class RustyHorn(Spell):
	Class, name = "Neutral", "Rusty Horn"
	needTarget, mana = True, 1
	index = "GoblinvsGnome-Neutral-1-Spell-Rusty Horn-Uncollectible"
	description = "Give a minion Taunt"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			print("Rusty Horn gives minion %s Taunt"%target.name)
			target.getsKeyword("Taunt")
		return target
		
class TimeRewinder(Spell):
	Class, name = "Neutral", "Time Rewinder"
	needTarget, mana = True, 1
	index = "GoblinvsGnome-Neutral-1-Spell-Time Rewinder-Uncollectible"
	description = "Return a friendly minion to your hand"
	def available(self):
		return self.selectableFriendlyMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.ID == self.ID and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			print("Time Rewinder returns friendly minion %s to owner's hand"%target.name)
			self.Game.returnMiniontoHand(target)
		return target
		
class WhirlingBlades(Spell):
	Class, name = "Neutral", "Whirling Blades"
	needTarget, mana = True, 1
	index = "GoblinvsGnome-Neutral-1-Spell-Whirling Blades-Uncollectible"
	description = "Give a minion +1 Attack"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			print("Whirling Blades gives minion %s +1 Attack"%target.name)
			target.buffDebuff(1, 0)
		return target
		
SpareParts = [ArmorPlating, EmergencyCoolant, FinickyCloakshield, ReversingSwitch, TimeRewinder, RustyHorn, WhirlingBlades]

class Toshley(Minion):
	Class, race, name = "Neutral", "", "Toshley"
	mana, attack, health = 6, 5, 7
	index = "GoblinvsGnome-Neutral-6-5-7-Minion-None-Toshley-Battlecry-Deathrattle-Legendary"
	needTarget, keyWord, description = False, "", "Battlecry and Deathrattle: Add a Spare Part card to your hand"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [AddaSpareParttoYourHand(self)]
		
	def whenEffective(self, target=None, comment="", choice=0):
		print("Toshley's battlecry adds a random Spare Part to player's hand")
		self.Game.Hand_Deck.addCardtoHand(np.random.choice(SpareParts), self.ID, "CreateUsingType")
		return self, None
		
class AddaSpareParttoYourHand(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("Deathrattle: Add a Spare Part to your hand triggers.")
		self.entity.Game.Hand_Deck.addCardtoHand(np.random.choice(SpareParts), self.entity.ID, "CreateUsingType")
		
		
class DrBoom(Minion):
	Class, race, name = "Neutral", "", "Dr. Boom"
	mana, attack, health = 7, 7, 7
	index = "GoblinvsGnome-Neutral-7-7-7-Minion-None-Dr. Boom-Battlecry-Legendary"
	needTarget, keyWord, description = False, "", "Battlecry: Summon two 1/1 Boom Bots. WARNING: Bots may explode"
	
	def whenEffective(self, target=None, comment="", choice=0):
		print("Dr. Boom's battlecry summons two 1/1 Boom Bots")
		pos = (self.position, "leftandRight") if self.onBoard else (-1, "totheRightEnd")
		self.Game.summonMinion([BoomBot_GoblinvsGnome(self.Game, self.ID) for i in range(2)], pos, self.ID)
		return self, None
		
class BoomBot_GoblinvsGnome(Minion):	
	Class, race, name = "Neutral", "Mech", "Boom Bot"
	mana, attack, health = 1, 1, 1
	index = "GoblinvsGnome-Neutral-1-1-1-Minion-Mech-Boom Bot-Deathrattle-Uncollectible"
	needTarget, keyWord, description = False, "", "Deathrattle: Deal 1~4 damage to a random enemy"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [Deal1to4DamagetoaRandomEnemy(self)]
		
class Deal1to4DamagetoaRandomEnemy(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("Deathrattle: Deal 1~4 damage to a random enemy triggers.")
		targets = [self.entity.Game.heroes[3-self.entity.ID]]
		for minion in self.entity.Game.minionsonBoard(3-self.entity.ID):
			if minion.health > 0 and minion.dead == False:
				targets.append(minion)
				
		target, damage = np.random.choice(targets), np.random.randint(1, 5)
		print(self.entity.name, "deals %d damage to"%damage, target)
		self.entity.dealsDamage(target, damage)
		
		
class TroggzortheEarthinator(Minion):
	Class, race, name = "Neutral", "", "Troggzor the Earthinator"
	mana, attack, health = 7, 6, 6
	index = "GoblinvsGnome-Neutral-7-6-6-Minion-None-Troggzor the Earthinator-Legendary"
	needTarget, keyWord, description = False, "", "Whenever your opponent casts a spell, summon a Burly Rockjaw Trogg"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_TroggzortheEarthinator(self)]
		
class Trigger_TroggzortheEarthinator(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["SpellPlayed"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject.ID != self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("Opponent casts a spell and %s summons a 3/5 Burly Rockjaw Trogg."%self.entity.name)
		self.entity.Game.summonMinion(BurlyRockjawTrogg(self.entity.Game, self.entity.ID), self.entity.position+1, self.entity.ID)
		
class BurlyRockjawTrogg(Minion):
	Class, race, name = "Neutral", "", "Burly Rockjaw Trogg"
	mana, attack, health = 4, 3, 5
	index = "GoblinvsGnome-Neutral-4-3-5-Minion-None-Burly Rockjaw Trogg"
	needTarget, keyWord, description = False, "", "Whenever your opponent casts a spell, gain +2 Attack"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_BurlyRockjawTrogg(self)]
		
class Trigger_BurlyRockjawTrogg(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["SpellPlayed"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject.ID != self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("Opponent casts a spell and %s gains +2 Attack"%self.entity.name)
		self.entity.buffDebuff(2, 0)
		
		
class FoeReaper4000(Minion):
	Class, race, name = "Neutral", "Mech", "Foe Reaper 4000"
	mana, attack, health = 8, 6, 9
	index = "GoblinvsGnome-Neutral-8-6-9-Minion-Mech-Foe Reaper 4000-Legendary"
	needTarget, keyWord, description = False, "", "Also damages the minions next to whoever it attacks"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.marks["Attack Adjacent Minions"] = 1
		
		
class SneedsOldShredder(Minion):
	Class, race, name = "Neutral", "Mech", "Sneed's Old Shredder"
	mana, attack, health = 8, 5, 7
	index = "GoblinvsGnome-Neutral-8-5-7-Minion-Mech-Sneed's Old Shredder-Deathrattle-Legendary"
	needTarget, keyWord, description = False, "", "Deathrattle: Summon a random Legendary minion"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [SummonaRandomLegendaryMinion(self)]
		
class SummonaRandomLegendaryMinion(Deathrattle_Minion):
	def trigger(self, signal, ID, subject, target, number, comment, choice=0):
		print("Deathrattle: Summon a random Legendary minion triggers.")
		legendaryMinion = np.random.choice(list(self.entity.Game.LegendaryMinions.values()))
		self.entity.Game.summonMinion(legendaryMinion(self.entity.Game, self.entity.ID), self.entity.position+1, self.entity.ID)
		
		
class MekgineerThermaplugg(Minion):
	Class, race, name = "Neutral", "Mech", "Mekgineer Thermaplugg"
	mana, attack, health = 9, 9, 7
	index = "GoblinvsGnome-Neutral-9-9-7-Minion-Mech-Mekgineer Thermaplugg-Legendary"
	needTarget, keyWord, description = False, "", "Whenever an enemy minion dies, summon a Leper Gnome"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_MekgineerThermaplugg(self)]
		
class Trigger_MekgineerThermaplugg(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionDies"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		#Technically, minion has to disappear before dies. But just in case.
		return self.entity.onBoard and target.ID != self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("An enemy minion %s dies and %s summons a Leper Gnome."%(target.name, self.entity.name))
		self.entity.Game.summonMinion(LeperGnome(self.entity.Game, self.entity.ID), self.entity.position+1, self.entity.ID)
		
		
class Malorne(Minion):
	Class, race, name = "Druid", "Beast", "Malorne"
	mana, attack, health = 9, 9, 7
	index = "GoblinvsGnome-Druid-9-9-7-Minion-Beast-Malorne-Deathrattle-Legendary"
	needTarget, keyWord, description = False, "", "Deathrattle: Shuffle this minion into your deck"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [ShuffleThisintoYourDeck(self)]
		
class ShuffleThisintoYourDeck(Deathrattle_Minion):
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		#如果随从身上已经有其他区域移动扳机触发过，则这个扳机不能两次触发，检测条件为仍在随从列表中
		return target == self.entity and self.entity in self.entity.Game.minions[self.entity.ID]
		
	def trigger(self, signal, ID, subject, target, number, comment, choice=0):
		print("Deathrattle: Shuffle this minion into your deck triggers")
		self.entity.Game.returnMiniontoDeck(self.entity, targetDeckID=self.entity.ID, initiatorID=self.entity.ID, keepDeathrattlesRegistered=True)
		
		
class Gahzrilla(Minion):
	Class, race, name = "Hunter", "Beast", "Gahz'rilla"
	mana, attack, health = 7, 6, 9
	index = "GoblinvsGnome-Hunter-7-6-9-Minion-Beast-Gahz'rilla-Legendary"
	needTarget, keyWord, description = False, "", "Whenever this minion takes damage, double its Attack"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_Gahzrilla(self)]
		
class Trigger_Gahzrilla(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionTakesDamage"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return target == self.entity and self.entity.onBoard
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print(self.entity.name, "takes Damage and doubles its Attack.")
		attack = max(0, self.entity.attack)
		self.entity.statReset(2 * attack, False)
		
		
class FlameLeviathan(Minion):
	Class, race, name = "Mage", "Mech", "Flame Leviathan"
	mana, attack, health = 7, 7, 7
	index = "GoblinvsGnome-Mage-7-7-7-Minion-Mech-Flame Leviathan-Triggers when Drawn"
	needTarget, keyWord, description = False, "", "When you draw this, deal 2 damage to all characters"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggers["Drawn"] = [self.deal2DamagetoAllCharacters]
		
	def deal2DamagetoAllCharacters(self):
		print("Flame Leviathan is drawn and deals 2 damage to all characters")
		targets = [self.Game.heroes[1], self.Game.heroes[2]] + self.Game.minionsonBoard(1) + self.Game.minionsonBoard(2)
		self.dealsAOE(targets, [2 for obj in targets])
		
		
class BolvarFordragon(Minion):
	Class, race, name = "Paladin", "", "Bolvar Fordragon"
	mana, attack, health = 5, 1, 7
	index = "GoblinvsGnome-Paladin-5-1-7-Minion-None-Bolvar Fordragon-Legendary"
	needTarget, keyWord, description = False, "", "Whenever a friendly minion dies while this is in your hand, gain +1 Attack"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersinHand = [Trigger_BolvarFordragon_GoblinvsGnome(self)]
	#不知道这种减费是自己的基础费用减少还是最后结算费用的selfManaChange
	
class Trigger_BolvarFordragon_GoblinvsGnome(TriggerinHand):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionDies"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.inHand and target.ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.buffDebuff(1, 0)
		
		
class Voljin(Minion):
	Class, race, name = "Priest", "", "Vol'jin"
	mana, attack, health = 5, 6, 2
	index = "GoblinvsGnome-Priest-5-6-2-Minion-None-Vol'jin-Battlecry-Legendary"
	needTarget, keyWord, description = True, "", "Battlecry: Swap Health with another minion"
	
	def targetExists(self, choice=0):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target != self and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			print("Vol'jin's battlecry swaps the minion's Health with another minion", target.name)
			targetHealth = target.health if target.onBoard or target.inHand else type(target).health
			selfHealth = self.health if self.onBoard or self.inHand else type(self).health
			#只用随从在场上或者手牌中时才会接受身材的改变
			target.statReset(False, selfHealth)
			self.statReset(False, targetHealth)
		return self, target
		
		
class TradePrinceGallywix(Minion):
	Class, race, name = "Rogue", "", "Trade Prince Gallywix"
	mana, attack, health = 6, 5, 8
	index = "GoblinvsGnome-Rogue-6-5-8-Minion-None-Trade Prince Gallywix-Legendary"
	needTarget, keyWord, description = False, "", "Whenever your opponent casts a spell, gain a copy of it and given them a coin"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_TradePrinceGallywix(self)]
		
class Trigger_TradePrinceGallywix(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["SpellPlayed"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		#加里维克斯不能对其自己产生的硬币做出反应，防止无限硬币的发生
		return self.entity.onBoard and subject.ID != self.entity.ID and type(subject) != GallywixsCoin
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("Opponent casts a spell and %s summons a 3/5 Burly Rockjaw Trogg."%self.entity.name)
		Copy = type(subject)(self.entity.Game, self.entity.ID)
		self.entity.Game.Hand_Deck.addCardtoHand(Copy, self.entity.ID)
		self.entity.Game.Hand_Deck.addCardtoHand(GallywixsCoin, 3-self.entity.ID, "CreateUsingType")
		
class GallywixsCoin(Spell):
	Class, name = "Neutral", "Gallywix's Coin"
	needTarget, mana = False, 0
	index = "GoblinvsGnome-Neutral-0-Spell-Gallywix's Coin-Uncollectible"
	description = "Gain 1 mana crystal for this turn."
	def whenEffective(self, target=None, comment="", choice=0):
		print("The Coin is cast and lets hero gain a mana this turn.")
		if self.Game.ManaHandler.manas[self.ID] < 10:
			self.Game.ManaHandler.manas[self.ID] += 1
		return None
		
		
class Neptulon(Minion):
	Class, race, name = "Shaman", "Elemental", "Neptulon"
	mana, attack, health = 7, 7, 7
	index = "GoblinvsGnome-Shaman-7-7-7-Minion-Elemental-Neptulon-Battlecry-Legendary"
	needTarget, keyWord, description = False, "", "Battlecry: Add 4 random Murlocs to your hand. Overload: (3)"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.overload = 3
		
	def whenEffective(self, target=None, comment="", choice=0):
		if self.Game.Hand_Deck.handNotFull(self.ID):
			print("Neptulon's battlecry adds 4 random Murlocs to player's hand")
			murlocs = list(self.Game.MinionswithRace["Murloc"].values())
			self.Game.Hand_Deck.addCardtoHand(np.random.choice(murlocs, 4, replace=True), self.ID, "CreateUsingType")
		return self, None
		
		
class MalGanis(Minion):
	Class, race, name = "Warlock", "Demon", "Mal'Ganis"
	mana, attack, health = 9, 9, 7
	index = "GoblinvsGnome-Warlock-9-9-7-Minion-Demon-Mal'Ganis-Legendary"
	needTarget, keyWord, description = False, "", "Your other Demons have +2/+2. Your hero is Immune"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.auras["Buff Aura"] = BuffAura_Dealer_All(self, self.applicable, 2, 2)
		self.appearResponse = [self.activateAura]
		self.disappearResponse = [self.deactivateAura]
		self.silenceResponse = [self.deactivateAura]
		
	def applicable(self, target):
		return "Demon" in target.race
		
	def activateAura(self):
		print("Mal'Ganis appears and gives player Immune")
		self.Game.playerStatus[self.ID]["Immune"] += 1
		
	def deactivateAura(self):
		print("Mal'Ganis no longer gives player Immune")
		if self.Game.playerStatus[self.ID]["Immune"] > 0:
			self.Game.playerStatus[self.ID]["Immune"] -= 1
			
			
class IronJuggernaut(Minion):
	Class, race, name = "Warrior", "Mech", "Iron Juggernaut"
	mana, attack, health = 6, 6, 5
	index = "GoblinvsGnome-Warrior-6-6-5-Minion-Mech-Iron Juggernaut-Battlecry-Legendary"
	needTarget, keyWord, description = False, "", "Battlecry: Shuffle a mine into your opponent's deck. When drawn, it explodes for 10 damage"
	
	def whenEffective(self, target=None, comment="", choice=0):
		print("Iron Juggernaut's battlecry shuffles a Mine into opponents deck. When its drawn, it deals 10 damage to the player.")
		self.Game.Hand_Deck.shuffleCardintoDeck(BurrowingMine(self.Game, 3-self.ID), self.ID)
		return self, None
		
class BurrowingMine(Spell):
	Class, name = "Warrior", "Burrowing Mine"
	needTarget, mana = False, 6
	index = "GoblinvsGnome-Warrior-6-Spell-Burrowing Mine-Casts When Drawn-Uncollectible"
	description = "Casts When Drawn. You take 10 damage"
	def whenEffective(self, target=None, comment="", choice=0):
		damage = (10 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		print("Burrowing Mine is cast and deals %d damage to player."%damage)
		self.dealsDamage(self.Game.heroes[self.ID], damage)
		return None
		
"""Black Rock Mountain"""
class EmperorThaurissan(Minion):
	Class, race, name = "Neutral", "", "Emperor Thaurissan"
	mana, attack, health = 6, 5, 5
	index = "BlackRockMountain-Neutral-6-5-5-Minion-None-Emperor Thaurissan-Legendary"
	needTarget, keyWord, description = False, "", "At the end of your turn, reduce the Cost of cards in your hand by (1)"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_EmperorThaurissan(self)]
		
class Trigger_EmperorThaurissan(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["TurnEnds"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("At the end of turn, %s reduces the Cost of cards in player's hand by (1)."%self.entity.name)
		#Kel'Thuzad resurrects dead minions in the same order they died.
		for card in self.entity.Game.Hand_Deck.hands[self.entity.ID]:
			if card.mana_set > 0:
				card.mana_set -= 1
		self.entity.Game.ManaHandler.calcMana_All()
		
		
class RendBlackhand(Minion):
	Class, race, name = "Neutral", "", "Rend Blackhand"
	mana, attack, health = 7, 8, 4
	index = "BlackRockMountain-Neutral-7-8-4-Minion-None-Rend Blackhand-Battlecry-Legendary"
	needTarget, keyWord, description = True, "", "Battlecry: If you are holding a Dragon, destroy a Legendary minion"
	
	def returnTrue(self, choice=0):
		return self.Game.Hand_Deck.holdingDragon(self.ID)
		
	def targetExists(self, choice=0):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and "Legendary" in target.index and target != self and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None and self.Game.Hand_Deck.holdingDragon(self.ID):
			print("Rend Blackhand's battlecry destroys Legendary minion", target.name)
			target.dead = True
		return self, target
		
		
class Chromaggus(Minion):
	Class, race, name = "Neutral", "Dragon", "Chromaggus"
	mana, attack, health = 8, 6, 8
	index = "BlackRockMountain-Neutral-8-6-8-Minion-Dragon-Chromaggus-Legendary"
	needTarget, keyWord, description = False, "", "Whenever you draw a card, add another copy into your hand"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_Chromaggus(self)]
		
class Trigger_Chromaggus(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["CardDrawn"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and target.ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("When player draws a card, %s adds a copy of it to player's hand"%self.entity.name)
		Copy = target.selfCopy(self.entity.ID)
		self.entity.Game.Hand_Deck.addCardtoHand(Copy, self.entity.ID, self.entity.ID)
		
		
class MajordomoExecutus(Minion):
	Class, race, name = "Neutral", "", "Majordomo Executus"
	mana, attack, health = 9, 9, 7
	index = "BlackRockMountain-Neutral-9-9-7-Minion-None-Majordomo Executus-Deathrattle-Legendary"
	needTarget, keyWord, description = False, "", "Deathrattle: Replace your hero with Ragnaros, the Firelord"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [ReplaceYourHerowithRagnaros(self)]
		
class ReplaceYourHerowithRagnaros(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("Deathrattle: Replace your hero with Ragnaros, the Firelord triggers.")
		RagnarostheFirelord(self.entity.Game, self.entity.ID).replaceHero()
		
class DIEINSECT(HeroPower):
	name, needTarget = "DIE. INSECT!", False
	index = "Neutral-2-Hero Power-DIE. INSECT!"
	description = "Deal 8 damage to a random enemy"
	
	def effect(self, target=None, choice=0):
		damage = (8 + self.Game.playerStatus[self.ID]["Temp Damage Boost"]) * (2 ** self.countDamageDouble())
		print("Hero Power DIE. INSECT! deals %d damage to a random enemy"%damage)
		enemies = [self.Game.heroes[3-self.ID]]
		for minion in self.Game.minionsonBoard(3-self.ID):
			if minion.health > 0 and minion.dead == False:
				enemies.append(minion)
				
		target = np.random.choice(enemies)
		self.dealsDamage(target, damage)
		if target.health < 1 or target.dead:
			return 1
		return 0
		
class RagnarostheFirelord(Hero):
	mana, weapon, description = 0, None, ""
	Class, name, heroPower, armor = "Neutral", "Ragnaros, the Firelord", DIEINSECT, 0
	index = ""
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.health, self.health_upper, self.armor = 8, 8, 0
		
		
class Nefarian(Minion):
	Class, race, name = "Neutral", "Dragon", "Nefarian"
	mana, attack, health = 9, 8, 8
	index = "BlackRockMountain-Neutral-9-8-8-Minion-Dragon-Nefarian-Battlecry-Legendary"
	needTarget, keyWord, description = False, "", "Battlecry: Add 2 random spells to your hand (from your opponent's class)"
	
	def whenEffective(self, target=None, comment="", choice=0):
		if self.Game.Hand_Deck.handNotFull(self.ID):
			spells = []
			for key, value in self.Game.ClassCards[self.Game.heroes[3-self.ID].Class].items():
				if "-Spell-" in key:
					spells.append(value)
					
			if spells != []:
				print("Nefarian's battlecry adds a random card from opponent's class to player's hand.")
				self.Game.Hand_Deck.addCardtoHand(np.random.choice(spells, 2, replace=True), self.ID, "CreateUsingType")
		return self, None
		
"""The Grand Tournament cards"""
class EydisDarkbane(Minion):
	Class, race, name = "Neutral", "", "Eydis Darkbane"
	mana, attack, health = 3, 3, 4
	index = "Tournament-Neutral-3-3-4-Minion-None-Eydis Darkbane-Legendary"
	needTarget, keyWord, description = False, "", "Whenever you target this minion with a spell, deal 3 damage to a random enemy"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_EydisDarkbane(self)]
		
class Trigger_EydisDarkbane(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["SpellPlayed"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject.ID == self.entity.ID and target == self.entity
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("Whenever player casts a spell on %s, it deals 3 damage to a random enemy"%self.entity.name)
		targets = [self.entity.Game.heroes[3-self.entity.ID]]
		for minion in self.entity.Game.minionsonBoard(3-self.entity.ID):
			if minion.health > 0 and minion.dead == False:
				targets.append(minion)
				
		self.entity.dealsDamage(np.random.choice(targets), 3)
	
	
class FjolaLightbane(Minion):
	Class, race, name = "Neutral", "", "Fjola Lightbane"
	mana, attack, health = 3, 3, 4
	index = "Tournament-Neutral-3-3-4-Minion-None-Fjola Lightbane-Legendary"
	needTarget, keyWord, description = False, "", "Whenever you target this minion with a spell, gain Divine Shield"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_FjolaLightbane(self)]
		
class Trigger_FjolaLightbane(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["SpellPlayed"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject.ID == self.entity.ID and target == self.entity
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("Whenever player casts a spell on %s, it gains Divine Shield"%self.entity.name)
		self.entity.getsKeyword("Divine Shield")
		
		
class GormoktheImpaler(Minion):
	Class, race, name = "Neutral", "", "Gormok the Impaler"
	mana, attack, health = 4, 4, 4
	index = "Tournament-Neutral-4-4-4-Minion-None-Gormok the Impaler-Battlecry-Legendary"
	needTarget, keyWord, description = True, "", "Battlecry: If you have at least 4 other minions, deal 4 damage"
	
	def returnTrue(self, choice=0):
		return len(self.Game.minionsonBoard(self.ID)) > 3
		
	def targetExists(self, choice=0):
		return self.selectableMinionExists()
		
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			otherMinions = 0
			for minion in self.Game.minionsonBoard(self.ID):
				if minion != self:
					otherMinions += 1
					
			if otherMinions > 3:
				print("Gormok the Impaler's battlecry deals 4 damage to", target.name)
				self.dealsDamage(target, 4)
		return self, target
		
		
class NexusChampionSaraad(Minion):
	Class, race, name = "Neutral", "", "Nexus-Champion Saraad"
	mana, attack, health = 5, 3, 4
	index = "Tournament-Neutral-5-3-4-Minion-None-Nexus-Champion Saraad-Legendary"
	needTarget, keyWord, description = False, "", "Inspire: Add a random spell to your hand"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_NexusChampionSaraad(self)]
		self.spells = []
		for Class in self.Game.ClassCards.keys():
			for key, value in self.Game.ClassCards[Class].items():
				if "-Spell-" in key:
					self.spells.append(value)
					
class Trigger_NexusChampionSaraad(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["HeroUsedAbility"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("After player uses Hero Power, %s adds a random spell to player's hand"%self.entity.name)
		self.entity.Game.Hand_Deck.addCardtoHand(np.random.choice(self.entity.spells), self.entity.ID, "CreateUsingType")
		
		
class BolfRamshield(Minion):
	Class, race, name = "Neutral", "", "Bolf Ramshield"
	mana, attack, health = 6, 3, 9
	index = "Tournament-Neutral-6-3-9-Minion-None-Bolf Ramshield-Legendary"
	needTarget, keyWord, description = False, "", "Whenever your hero takes damage, this minion takes it instead"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.appearResponse = [self.activateAura]
		self.disappearResponse = [self.deactivateAura]
		self.silenceResponse = [self.deactivateAura]
		
	def activateAura(self):
		print("Bolf Ramshield appears and starts taking potential damage for player.")
		self.Game.DamageHandler.RamshieldExists[self.ID] += 1
		
	def deactivateAura(self):
		if self.Game.DamageHandler.RamshieldExists[self.ID] > 0:
			print("Bolf Ramshield no longer takes potential damage for player.")
			self.Game.DamageHandler.RamshieldExists[self.ID] -= 1
			
			
class JusticarTrueheart(Minion):
	Class, race, name = "Neutral", "", "Justicar Trueheart"
	mana, attack, health = 6, 6, 3
	index = "Tournament-Neutral-6-6-3-Minion-None-Justicar Trueheart-Battlecry-Legendary"
	needTarget, keyWord, description = False, "", "Battlecry: Replace your starting Hero Power with a better one"
	
	def whenEffective(self, target=None, comment="", choice=0):
		for i in range(len(BasicHeroPowers)):
			if type(self.Game.heroPowers[self.ID]) == BasicHeroPowers[i]:
				print("Justicar Trueheart's battlecry upgrades player's Hero Power from basic to a better one")
				UpgradedHeroPowers[i](self.Game, self.ID).replaceHeroPower()
				break
		return self, None
		
		
class TheSkeletonKnight(Minion):
	Class, race, name = "Neutral", "", "The Skeleton Knight"
	mana, attack, health = 6, 7, 4
	index = "Tournament-Neutral-6-7-4-Minion-None-The Skeleton Knight-Deathrattle-Legendary"
	needTarget, keyWord, description = False, "", "Deathrattle: Reveal a minion in each deck. If yours costs more, return this to your hand"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [RevealtoReturnThistoYourHand(self)]
		
class RevealtoReturnThistoYourHand(Deathrattle_Minion):
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		#如果随从身上已经有其他区域移动扳机触发过，则这个扳机不能两次触发，检测条件为仍在随从列表中
		return target == self.entity and self.entity in self.entity.Game.minions[self.entity.ID]
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("Deathrattle: Reveal a minion in each deck. If yours costs more, return this to your hand triggers.")
		minions = []
		for card in self.entity.Game.Hand_Deck.decks[self.entity.ID]:
			if card.cardType == "Minion":
				minions.append(card)
		friendlyMinion = np.random.choice(minions) if minions != [] else None
		minions = []
		for card in self.entity.Game.Hand_Deck.decks[3-self.entity.ID]:
			if card.cardType == "Minion":
				minions.append(card)
		enemyMinion = np.random.choice(minions) if minions != [] else None
		if friendlyMinion != None:
			if enemyMinion == None or friendlyMinion.mana_set > enemyMinion.mana_set:
				self.entity.Game.returnMiniontoHand(self.entity, keepDeathrattlesRegistered=True)
				
				
class Chillmaw(Minion):
	Class, race, name = "Neutral", "Dragon", "Chillmaw"
	mana, attack, health = 7, 6, 6
	index = "Tournament-Neutral-7-6-6-Minion-Dragon-Chillmaw-Deathrattle-Legendary"
	needTarget, keyWord, description = False, "Taunt", "Taunt. Deathrattle: If you're holding a Dragon, deal 3 damage to all minions"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [Deal3DamagetoAllMinionsifHoldingDragon(self)]
		
class Deal3DamagetoAllMinionsifHoldingDragon(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		if self.entity.Game.Hand_Deck.holdingDragon(self.entity.ID):
			print("Deathrattle: If you're holding a Dragon, deal 3 damage to all minions triggers")
			targets = self.entity.Game.minionsonBoard(1) + self.entity.Game.minionsonBoard(2)
			self.entity.dealsAOE(targets, [3 for minion in targets])
			
			
class SkycapnKragg(Minion):
	Class, race, name = "Neutral", "Pirate", "Skycap'n Kragg"
	mana, attack, health = 7, 4, 6
	index = "Tournament-Neutral-7-4-6-Minion-Pirate-Skycap'n Kragg-Charge-Legendary"
	needTarget, keyWord, description = False, "Charge", "Charrrrrge. Costs (1) less for each friendly Pirate"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersinHand = [Trigger_SkycapnKragg(self)]
		
	def selfManaChange(self):
		num = 0
		for minion in self.Game.minionsonBoard(self.ID):
			if "Pirate" in minion.race:
				num += 1
				
		self.mana -= num
		self.mana = max(0, self.mana)
		if self.keyWords["Echo"] > 0 and self.mana < 1:
			self.mana = 1
			
class Trigger_SkycapnKragg(TriggerinHand):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionAppears", "MinionDisappears"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.inHand and "Pirate" in subject.race
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.Game.ManaHandler.calcMana_Single(self.entity)
		
	
class Icehowl(Minion):
	Class, race, name = "Neutral", "", "Icehowl"
	mana, attack, health = 9, 10, 10
	index = "Tournament-Neutral-9-10-10-Minion-None-Icehowl-Charge-Legendary"
	needTarget, keyWord, description = False, "Charge", "Charge. Can't attack heroes"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.marks["Can't Attack Hero"] = 1
		
		
class Aviana(Minion):
	Class, race, name = "Druid", "", "Aviana"
	mana, attack, health = 10, 5, 5
	index = "Tournament-Druid-10-5-5-Minion-None-Aviana-Legendary"
	needTarget, keyWord, description = False, "", "Your minions cost (1)"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.manaAura = YourMinionsCost1(self)
		self.appearResponse = [self.activateAura]
		self.disappearResponse = [self.deactivateAura]
		self.silenceResponse = [self.deactivateAura]
		
	def activateAura(self):
		print("Aviana's mana aura is included. Player's minions cost 1 now.")
		self.Game.ManaHandler.CardAuras.apend(self.manaAura)
		self.Game.ManaHandler.calcMana_All()
		
	def deactivateAura(self):
		extractfrom(self.manaAura, self.Game.ManaHandler.CardAuras)
		print("Aviana's mana aura is removed. Player's minions no longer cost 1 now.")
		self.Game.ManaHandler.calcMana_All()
		
class YourMinionsCost1:
	def __init__(self, minion):
		self.minion = minion
		self.temporary = False
		
	def handleMana(self, target):
		if target.cardType == "Minion" and target.ID == self.minion.ID:
			target.mana = 1
			
			
class Dreadscale(Minion):
	Class, race, name = "Hunter", "Beast", "Dreadscale"
	mana, attack, health = 3, 4, 2
	index = "Tournament-Hunter-3-4-2-Minion-Beast-Dreadscale-Legendary"
	needTarget, keyWord, description = False, "", "At the end of your turn, deal 1 damage to all other minions"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_Dreadscale(self)]
		
class Trigger_Dreadscale(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["TurnEnds"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("At the end of turn, %s deals 1 damage to all other minions."%self.entity.name)
		targets = self.entity.Game.minionsonBoard(1) + self.entity.Game.minionsonBoard(2)
		extractfrom(self.entity, targets)
		self.entity.dealsAOE(targets, [1 for minion in targets])
		
		
class Acidmaw(Minion):
	Class, race, name = "Hunter", "Beast", "Acidmaw"
	mana, attack, health = 7, 4, 2
	index = "Tournament-Hunter-7-4-2-Minion-Beast-Acidmaw-Legendary"
	needTarget, keyWord, description = False, "", "Whenever another minion takes damage, destroy it"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_Acidmaw(self)]
		
class Trigger_Acidmaw(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionTakesDamage"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and target != self and target.onBoard
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("Whenever minion %s takes damage, %s destroys it."%(target.name, self.entity.name))
		target.dead = True
		
		
class Rhonin(Minion):
	Class, race, name = "Mage", "", "Rhonin"
	mana, attack, health = 8, 7, 7
	index = "Tournament-Mage-8-7-7-Minion-None-Rhonin-Deathrattle-Legendary"
	needTarget, keyWord, description = False, "", "Deathrattle: Add 3 copies of Arcane Missiles to your hand"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [Add3ArcaneMissilestoYourHand(self)]
		
class Add3ArcaneMissilestoYourHand(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("Deathrattle: Add 3 copies of Arcane Missiles to your hand triggers.")
		self.entity.Game.Hand_Deck.addCardtoHand([ArcaneMissiles for i in range(3)], self.entity.ID, "CreateUsingType")
		
		
class EadricthePure(Minion):
	Class, race, name = "Paladin", "", "Eadric the Pure"
	mana, attack, health = 7, 3, 7
	index = "Tournament-Paladin-7-3-7-Minion-None-Eadric the Pure-Battlecry-Legendary"
	needTarget, keyWord, description = False, "", "Battlecry: Change all enemy minions' Attack to 1"
	
	def whenEffective(self, target=None, comment="", choice=0):
		print("Eadric the Pure's battlecry changes the Attack of all enemy minions to 1")
		for minion in fixedList(self.Game.minionsonBoard(3-self.ID)):
			minion.statReset(1, False)
		return self, None
		
		
class ConfessorPaletress(Minion):
	Class, race, name = "Priest", "", "Confessor Paletress"
	mana, attack, health = 7, 5, 4
	index = "Tournament-Priest-7-5-4-Minion-None-Confessor Paletress-Legendary"
	needTarget, keyWord, description = False, "", "Inspire: Summon a random Legendary minion"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_ConfessorPaletress(self)]
		
class Trigger_ConfessorPaletress(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["HeroUsedAbility"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("After player uses Hero Power, %s summons a random Legendary minion"%self.entity.name)
		legendaryMinion = np.random.choice(list(self.entity.Game.LegendaryMinions.values()))(self.entity.Game, self.entity.ID)
		self.entity.Game.summonMinion(legendaryMinion, self.entity.position+1, self.entity.ID)
		
		
class Anubarak(Minion):
	Class, race, name = "Rogue", "", "Anub'arak"
	mana, attack, health = 9, 8, 4
	index = "Tournament-Rogue-9-8-4-Minion-None-Anub'arak-Deathrattle-Legendary"
	needTarget, keyWord, description = False, "", "Deathrattle: Return this to your hand and summon a 4/4 Nerubian"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [ReturnThistoYourHandandSummonaNerubian(self)]
		
class ReturnThistoYourHandandSummonaNerubian(Deathrattle_Minion):
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		#如果随从身上已经有其他区域移动扳机触发过，则这个扳机不能两次触发，检测条件为仍在随从列表中
		return self.entity == target and self.entity in self.entity.Game.minions[self.entity.ID]
		
	def trigger(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.Game.returnMiniontoHand(self.entity, keepDeathrattlesRegistered=True)
		if self.entity.Game.playerStatus[self.entity.ID]["Deathrattle Trigger Twice"] > 0:
			print("Deathrattle: Return this minion to your hand and summon a 4/4 Nerubian triggers")
			self.entity.Game.summonMinion(Nerubian(self.entity.Game, self.entity.ID), -1, self.entity.ID)
		print("Deathrattle: Return this minion to your hand and summon a 4/4 Nerubian triggers")
		self.entity.Game.summonMinion(Nerubian(self.entity.Game, self.entity.ID), -1, self.entity.ID)
		
class Nerubian(Minion):
	Class, race, name = "Neutral", "", "Nerubian"
	mana, attack, health = 4, 4, 4
	index = "Tournament-Neutral-4-4-4-Minion-None-Nerubian-Uncollectible"
	needTarget, keyWord, description = False, "", ""
	
	
class TheMistcaller(Minion):
	Class, race, name = "Shaman", "", "The Mistcaller"
	mana, attack, health = 6, 4, 4
	index = "Tournament-Shaman-6-4-4-Minion-None-The Mistcaller-Battlecry-Legendary"
	needTarget, keyWord, description = False, "", "Battlecry: Give all minions in your hand and deck +1/+1"
	
	def whenEffective(self, target=None, comment="", choice=0):
		print("The Mistcaller's battlecry gives all minions in player's hand and deck +1/+1")
		for card in self.Game.Hand_Deck.hands[self.ID]:
			if card.cardType == "Minion":
				card.buffDebuff(1, 1)
		for card in self.Game.Hand_Deck.decks[self.ID]:
			if card.cardType == "Minion":
				self.attack_Enchant += 1
				self.health_Enchant += 1
		return self, None
		
		
class WilfredFizzlebang(Minion):
	Class, race, name = "Warlock", "", "Wilfred Fizzlebang"
	mana, attack, health = 6, 4, 4
	index = "Tournament-Warloc-6-4-4-Minion-None-Wilfred Fizzlebang-Legendary"
	needTarget, keyWord, description = False, "", "Cards you draw from your Hero Power costs(0)"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_WilfredFizzlebang(self)]
		
class Trigger_WilfredFizzlebang(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["CardDrawnfromHeroPower"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and ID == self.entity.ID and card != None
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("After player uses Hero Power and draws card, %s reduces its Cost to (0)"%self.entity.name)
		target.mana_set = 0
		self.entity.Game.ManaHandler.calcMana_Single(target)
		
		
class VarianWrynn(Minion):
	Class, race, name = "Warrior", "", "Varian Wrynn"
	mana, attack, health = 10, 7, 7
	index = "Tournament-Warrior-10-7-7-Minion-None-Varian Wrynn-Battlecry-Legendary"
	needTarget, keyWord, description = False, "", "Battlecry: Draw 3 cards. Put any minions you drew directly into the battlefield"
	
	def whenEffective(self, target=None, comment="", choice=0):
		print("Varian Wrynn's battlecry lets player draw 3 cards and summon the minions drawn")
		for i in range(3):
			card, mana = self.Game.Hand_Deck.drawCard(self.ID)
			if card != None and card.cardType == "Minion" and self.Game.spaceonBoard(self.ID) > 0:
				minion, mana, isRightmostCardinHand = self.Game.Hand_Deck.extractfromHand(card)
				self.Game.summonMinion(minion, self.position+1, self.ID)
		return self, None
		
		
"""League of Explorers cards"""
class SirFinleyMrrgglton(Minion):
	Class, race, name = "Neutral", "Murloc", "Sir Finley Mrrgglton"
	mana, attack, health = 1, 1, 3
	index = "Explorers-Neutral-1-1-3-Minion-Murloc-Sir Finley Mrrgglton-Battlecry-Legendary"
	needTarget, keyWord, description = False, "", "Battlecry: Discover a new basic Hero Power"
	
	def whenEffective(self, target=None, comment="", choice=0):
		heroPowerPool = BasicHeroPowers
		currentHeroPower = type(self.Game.heroPowers[self.ID])
		extractfrom(currentHeroPower, BasicHeroPowers)
		if comment == "InvokedbyOthers":
			newHeroPower = np.random.choice(heroPowerPool)(self.Game, self.ID)
			print("Sir Finley Mrrgglton's battlecry changes player's Hero Power to", newHeroPower.name)
			newHeroPower.replaceHeroPower()
		elif self.ID == self.Game.turn:
			newHeroPowers = np.random.choice(heroPowerPool, 3, replace=False)
			self.Game.options = [heroPower(self.Game, self.ID) for heroPower in newHeroPowers]
			self.Game.DiscoverHandler.startDiscover(self)
			
		return self, None
		
	def discoverDecided(self, option):
		print("New basic Hero Power", option.name, "replaces the current one")
		option.replaceHeroPower()
		
		
class BrannBronzebeard(Minion):
	Class, race, name = "Neutral", "", "Brann Bronzebeard"
	mana, attack, health = 3, 2, 4
	index = "Explorers-Neutral-3-2-4-Minion-None-Brann Bronzebeard-Legendary"
	needTarget, keyWord, description = False, "", "Your Battlecries trigger twice"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.appearResponse = [self.activateAura]
		self.disappearResponse = [self.deactivateAura]
		self.silenceResponse = [self.deactivateAura]
		
	def activateAura(self):
		print("Brann Bronzebeard's aura appears. Player %d's Battlecries trigger twice now."%self.ID)
		self.Game.playerStatus[self.ID]["Battlecry Trigger Twice"] += 1
		
	def deactivateAura(self):
		print("Brann Bronzebeard's aura is removed. Player %d's no longer trigger twice."%self.ID)
		if self.Game.playerStatus[self.ID]["Battlecry Trigger Twice"] > 0:
			self.Game.playerStatus[self.ID]["Battlecry Trigger Twice"] -= 1
			
			
class EliseStarseeker(Minion):
	Class, race, name = "Neutral", "", "Elise Starseeker"
	mana, attack, health = 4, 3, 5
	index = "Explorers-Neutral-4-3-5-Minion-None-Elise Starseeker-Battlecry-Legendary"
	needTarget, keyWord, description = False, "", "Battlecry: Shuffle the 'Map to the Golden Monkey' into your deck"
	
	def whenEffective(self, target=None, comment="", choice=0):
		print("Elise Starseeker's battlecry shuffles the 'Map to the Golden Monkey' into player's hand")
		self.Game.Hand_Deck.shuffleCardintoDeck(MaptotheGoldenMonkey(self.Game, self.ID), self.ID)
		return self, None
		
class MaptotheGoldenMonkey(Spell):
	Class, name = "Neutral", "Map to the Golden Monkey"
	needTarget, mana = False, 2
	index = "Explorers-Neutral-2-Spell-Map to the Golden Monkey-Uncollectible"
	description = "Shuffle the Golden Monkey into your deck. Draw a card"
	def whenEffective(self, target=None, comment="", choice=0):
		print("Map to the Golden Monkey is cast and shuffles the Golden Monkey into player's deck. Player draws a card.")
		self.Game.Hand_Deck.shuffleCardintoDeck(GoldenMonkey(self.Game, self.ID), self.ID)
		self.Game.Hand_Deck.drawCard(self.ID)
		return None
		
class GoldenMonkey(Minion):
	Class, race, name = "Neutral", "", "Golden Monkey"
	mana, attack, health = 4, 6, 6
	index = "Explorers-Neutral-4-6-6-Minion-None-Golden Monkey-Battlecry-Uncollectible"
	needTarget, keyWord, description = False, "Taunt", "Taunt. Battlecry: Replace your hand and deck with Legendary minions"
	
	def whenEffective(self, target=None, comment="", choice=0):
		print("Golden Monkey's battlecry replaces player's hand and deck with Legendary minions")
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
		
		
class RenoJackson(Minion):
	Class, race, name = "Neutral", "", "Reno Jackson"
	mana, attack, health = 6, 4, 6
	index = "Explorers-Neutral-6-4-6-Minion-None-Reno Jackson-Battlecry-Legendary"
	needTarget, keyWord, description = False, "", "Battlecry: If your deck has no duplicates, fully heal your hero"
	
	def whenEffective(self, target=None, comment="", choice=0):
		if self.Game.Hand_Deck.noDuplicatesinDeck(self.ID):
			heal = self.Game.heroes[self.ID].health_upper * (2 ** self.countHealDouble())
			self.restoresHealth(self.Game.heroes[self.ID], heal)
		return self, None
		
		
class MirrorofDoom(Spell):
	Class, name = "Neutral", "Mirror of Doom"
	needTarget, mana = False, 10
	index = "Explorers-Neutral-10-Spell-Mirror of Doom-Uncollectible"
	description = "Fill your board with 3/3 Mummy Zombies"
	def whenEffective(self, target=None, comment="", choice=0):
		print("Mirror of Doom is cast and fills the player's board with Mummy Zombies.")
		self.Game.summonMinion([MummyZombie(self.Game, self.ID) for i in range(7)], (-1, "totheRightEnd"), self.ID)
		return None
		
class MummyZombie(Minion):
	Class, race, name = "Neutral", "", "Mummy Zombie"
	mana, attack, health = 3, 3, 3
	index = "Explorers-Neutral-3-3-3-Minion-None-Mummy Zombie-Uncollectible"
	needTarget, keyWord, description = False, "", ""
	
class TimepieceofHorror(Spell):
	Class, name = "Neutral", "Timepiece of Horror"
	needTarget, mana = False, 10
	index = "Explorers-Neutral-10-Spell-Timepiece of Horror-Uncollectible"
	description = "Deal 10 damage randomly split among all enemies"
	def whenEffective(self, target=None, comment="", choice=0):
		num = (10 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		print("Timepiece of Horror is cast and deals %d damage randomly split among all enemies.")
		for i in range(0, num):
			targets = [self.Game.heroes[3-self.ID]]
			for minion in self.Game.minionsonBoard(3-self.ID):
				if minion.health > 0 and minion.dead == False:
					targets.append(minion)
					
			self.dealsDamage(np.random.choice(targets), 1)
		return None
		
class LanternofPower(Spell):
	Class, name = "Neutral", "Lantern of Power"
	needTarget, mana = True, 10
	index = "Explorers-Neutral-10-Spell-Lantern of Power-Uncollectible"
	description = "Give a minion +10/+10"
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			print("Lantern of Power is cast and gives minion %s +10/+10")
			target.buffDebuff(10, 10)
		return target
		
PowerfulArtifacts = [MirrorofDoom, TimepieceofHorror, LanternofPower]

class ArchThiefRafaam(Minion):
	Class, race, name = "Neutral", "", "Arch-Thief Rafaam"
	mana, attack, health = 9, 7, 8
	index = "Explorers-Neutral-9-7-8-Minion-None-Arch-Thief Rafaam-Battlecry-Legendary"
	needTarget, keyWord, description = False, "", "Battlecry: Discover a powerful Artifact"
	
	def whenEffective(self, target=None, comment="", choice=0):
		if comment == "InvokedbyOthers":
			print("Arch-Thief Rafaam's battlecry adds a random powerful Artifact to player's hand.")
			self.Game.Hand_Deck.addCardtoHand(np.random.choice(PowerfulArtifact), self.ID, "CreateUsingType")
		elif self.ID == self.Game.turn:
			self.Game.options = [artifact(self.Game, self.ID) for artifact in PowerfulArtifacts]
			print("Arch-Thief Rafaam's battlecry lets player Discover a powerful Artifact")
			self.Game.DiscoverHandler.startDiscover(self)
		
		return self, None
		
	def discoverDecided(self, option):
		print("Powerful Artifact", option.name, "is added to player's hand")
		self.Game.Hand_Deck.addCardtoHand(option, self.ID)
		
		
