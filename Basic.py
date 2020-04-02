from CardTypes import *
from Triggers_Auras import *

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
		
class SearingTotem(Minion):
	Class, race, name = "Shaman", "Totem", "Searing Totem"
	mana, attack, health = 1, 1, 1
	index = "Basic~Shaman~Minion~1~1~1~Totem~Searing Totem~Uncollectible"
	requireTarget, keyWord, description = False, "", ""
	
class StoneclawTotem(Minion):
	Class, race, name = "Shaman", "Totem", "Stoneclaw Totem"
	mana, attack, health = 1, 0, 2
	index = "Basic~Shaman~Minion~1~0~2~Totem~Stoneclaw Totem~Taunt~Uncollectible"
	requireTarget, keyWord, description = False, "Taunt", "Taunt"
	
class HealingTotem(Minion):
	Class, race, name = "Shaman", "Totem", "Healing Totem"
	mana, attack, health = 1, 0, 2
	index = "Basic~Shaman~Minion~1~0~2~Totem~Healing Totem~Uncollectible"
	requireTarget, keyWord, description = False, "", "At the end of your turn, restore 1 health to all friendly minions"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_HealingTotem(self)]
		
class Trigger_HealingTotem(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["TurnEnds"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self, "At the end of turn, %s restores 1 health to all friendly minions."%self.entity.name)
		heal = 1 * (2 ** self.entity.countHealDouble())
		targets = self.entity.Game.minionsonBoard(self.entity.ID)
		self.entity.restoresAOE(targets, [heal for minion in targets])
		
		
class WrathofAirTotem(Minion):
	Class, race, name = "Shaman", "Totem", "Wrath of Air Totem"
	mana, attack, health = 1, 0, 2
	index = "Basic~Shaman~Minion~1~0~2~Totem~Wrath of Air Totem~Spell Damage~Uncollectible"
	requireTarget, keyWord, description = False, "Spell Damage", "Spell Damage +1"#Default Spell Damage is 1.
	
BasicTotems = [SearingTotem, StoneclawTotem, HealingTotem, WrathofAirTotem]

"""Basic&Upgraded Hero Powers"""
#Steady Shot is defined in the CardTypes file as the vanilla Hero Power
class BallistaShot(HeroPower):
	mana, name, requireTarget = 2, "Ballista Shot", False
	index = "Hunter~Hero Power~2~Ballista Shot"
	description = "Deal 3 damage to the enemy hero"
	def returnFalse(self, choice=0):
		return self.Game.playerStatus[self.ID]["Hunter Hero Powers Can Target Minions"] > 0
		
	def targetCorrect(self, target, choice=0):
		if self.Game.playerStatus[self.ID]["Hunter Hero Powers Can Target Minions"] > 0:
			return (target.cardType == "Minion" or target.cardType == "Hero") and target.onBoard
		else:
			return target.cardType == "Hero" and target.ID != self.ID and target.onBoard
			
	def effect(self, target=None, choice=0):
		damage = (3 + self.Game.playerStatus[self.ID]["Hero Power Damage Boost"]) * (2 ** self.countDamageDouble())
		if target != None:
			PRINT(self, "Hero Power Ballista Shot deals %d damage to the character %s"%(damage, target.name))
			self.dealsDamage(target, damage)
		else:
			PRINT(self, "Hero Power Ballista Shot deals %d damage to the enemy hero %s"%(damage, self.Game.heroes[3-self.ID].name))
			self.dealsDamage(self.Game.heroes[3-self.ID], damage)
		return 0
		
class DaggerMastery(HeroPower):
	mana, name, requireTarget = 2, "Dagger Mastery", False
	index = "Rogue~Hero Power~2~Dagger Mastery"
	description = "Equip a 1/2 Weapon"
	def effect(self, target=None, choice=0):
		PRINT(self, "Hero Power Dagger Mastery equips a 1/2 Wicked Knife for player")
		self.Game.equipWeapon(WickedKnife(self.Game, self.ID))
		return 0
		
class DemonClaws(HeroPower):
	mana, name, requireTarget = 1, "Demon Claws", False
	index = "Demon Hunter~Hero Power~1~Demon Claws"
	description = "+1 Attack this turn"
	def effect(self, target=None, choice=0):
		PRINT(self, "Hero Power Demon Claws gives player gain +1 Attack this turn")
		self.Game.heroes[self.ID].gainTempAttack(1)
		return 0
		
class PoisonedDaggers(HeroPower):
	mana, name, requireTarget = 2, "Poisoned Daggers", False
	index = "Rogue~Hero Power~2~Poisoned Daggers"
	description = "Equip a 2/2 Weapon"
	def effect(self, target=None, choice=0):
		PRINT(self, "Hero Power Poisoned Daggers equips a 2/2 Poisoned Dagger for player")
		self.Game.equipWeapon(PoisonedDagger(self.Game, self.ID))
		return 0
		
class LifeTap(HeroPower):
	mana, name, requireTarget = 2, "Life Tap", False
	index = "Warlock~Hero Power~2~Life Tap"
	description = "Deal 2 damage to your hero. Draw a card"
	def effect(self, target=None, choice=0):
		damage = (2 + self.Game.playerStatus[self.ID]["Hero Power Damage Boost"]) * (2 ** self.countDamageDouble())
		PRINT(self, "Hero Power Life Tap deals %d damage to player and lets player draw a card")
		self.dealsDamage(self.Game.heroes[self.ID], damage)
		card, mana = self.Game.Hand_Deck.drawCard(self.ID)
		if card != None:
			self.Game.sendSignal("CardDrawnfromHeroPower", self.ID, self, card, mana, "")
		return 0
		
class SoulTap(HeroPower):
	mana, name, requireTarget = 2, "Soul Tap", False
	index = "Warlock~Hero Power~2~Soul Tap"
	description = "Draw a card"
	def effect(self, target=None, choice=0):
		PRINT(self, "Hero Power Soul Tap lets player draw a card")
		card, mana = self.Game.Hand_Deck.drawCard(self.ID)
		if card != None:
			self.Game.sendSignal("CardDrawnfromHeroPower", self.ID, self, card, mana, "")
		return 0
		
class Shapeshift(HeroPower):
	mana, name, requireTarget = 2, "Shapeshift", False
	index = "Druid~Hero Power~2~Shapeshift"
	description = "+1 Attack this turn. +1 Armor"
	def effect(self, target=None, choice=0):
		PRINT(self, "Hero Power Shapeshift gives lets player gain 1 Armor and 1 Attack this turn")
		self.Game.heroes[self.ID].gainsArmor(1)
		self.Game.heroes[self.ID].gainTempAttack(1)
		return 0
		
class DireShapeshift(HeroPower):
	mana, name, requireTarget = 2, "Dire Shapeshift", False
	index = "Druid~Hero Power~2~Dire Shapeshift"
	description = "+2 Attack this turn. +2 Armor"
	def effect(self, target=None, choice=0):
		PRINT(self, "Hero Power Dire Shapeshift gives lets player gain 2 Armor and 2 Attack this turn")
		self.Game.heroes[self.ID].gainsArmor(2)
		self.Game.heroes[self.ID].gainTempAttack(2)
		return 0
		
class ArmorUp(HeroPower):
	mana, name, requireTarget = 2, "Armor Up!", False
	index = "Warrior~Hero Power~2~Armor Up!"
	description = "Gain 2 Armor"
	def effect(self, target=None, choice=0):
		PRINT(self, "Hero Armor Up! lets player gain 2 Armor")
		self.Game.heroes[self.ID].gainsArmor(2)
		return 0
		
class TankUp(HeroPower):
	mana, name, requireTarget = 2, "Tank Up!", False
	index = "Warrior~Hero Power~2~Tank Up!"
	description = "Gain 4 Armor"
	def effect(self, target=None, choice=0):
		PRINT(self, "Hero Armor Up! lets player gain 2 Armor")
		self.Game.heroes[self.ID].gainsArmor(4)
		return 0
		
class Reinforce(HeroPower):
	mana, name, requireTarget = 2, "Reinforce", False
	index = "Paladin~Hero Power~2~Reinforce"
	description = "Summon a 1/1 Silver Hand Recruit"
	def available(self):
		if self.heroPowerTimes >= self.heroPowerChances_base + self.heroPowerChances_extra:
			return False
		if self.Game.spaceonBoard(self.ID) < 1:
			return False
		return True
		
	def effect(self, target=None, choice=0):
		#Hero Power summoning won't be doubled by Khadgar.
		PRINT(self, "Hero Power Reinforce summons a 1/1 Silver Hand Recruit")
		self.Game.summonMinion(SilverHandRecruit(self.Game, self.ID), -1, self.ID, "")
		return 0
		
class TheSilverHand(HeroPower):
	mana, name, requireTarget = 2, "The Silver Hand", False
	index = "Paladin~Hero Power~2~The Silver Hand"
	description = "Summon two 1/1 Silver Hand Recruits"
	def available(self):
		if self.heroPowerTimes >= self.heroPowerChances_base + self.heroPowerChances_extra:
			return False
		if self.Game.spaceonBoard(self.ID) < 1:
			return False
		return True
		
	def effect(self, target=None, choice=0):
		PRINT(self, "Hero Power The Silver Hand summons two 1/1 Silver Hand Recruits")
		self.Game.summonMinion([SilverHandRecruit(self.Game, self.ID) for i in range(2)], (-11, "totheRightEnd"), self.ID, "")
		return 0
		
class TotemicCall(HeroPower):
	mana, name, requireTarget = 2, "Totemic Call", False
	index = "Shaman~Hero Power~2~Totemic Call"
	description = "Summon a random totem"
	def available(self):
		if self.heroPowerTimes >= self.heroPowerChances_base + self.heroPowerChances_extra:
			return False
		if self.Game.spaceonBoard(self.ID) < 1 or self.viableTotems() == []:
			return False
		return True
		
	def effect(self, target=None, choice=0):
		viableTotems = self.viableTotems()
		PRINT(self, "Hero Power Totemic Call summons a random Basic Totem")
		self.Game.summonMinion(np.random.choice(viableTotems)(self.Game, self.ID), -1, self.ID, "")
		return 0
		
	def viableTotems(self):
		viableBasicTotems = [SearingTotem, StoneclawTotem, HealingTotem, WrathofAirTotem]
		for minion in self.Game.minionsonBoard(self.ID):
			if type(minion) in viableBasicTotems:
				extractfrom(type(minion), viableBasicTotems)
				
		return viableBasicTotems
		
class TotemicSlam(HeroPower):
	mana, name, requireTarget = 2, "Totemic Slam", False
	index = "Shaman~Hero Power~2~Totemic Call"
	description = "Summon a totem of your choice"
	def available(self):
		if self.heroPowerTimes >= self.heroPowerChances_base + self.heroPowerChances_extra:
			return False
		if self.Game.spaceonBoard(self.ID) < 1:
			return False
		return True
		
	def effect(self, target=None, choice=0):
		self.Game.options = [SearingTotem(self.Game, self.ID), StoneclawTotem(self.Game, self.ID),
							HealingTotem(self.Game, self.ID), WrathofAirTotem(self.Game, self.ID)]
		PRINT(self, "Hero Power Totemic Slam starts the discover for a basic totem to summon.")
		self.Game.DiscoverHandler.startDiscover(self)
		return 0
		
	def discoverDecided(self, option):
		PRINT(self, "Hero Power Totemic Slam summons totem %s"%target.name)
		self.Game.summonMinion(option, -1, self.ID, "")
		
class Fireblast(HeroPower):
	mana, name, requireTarget = 2, "Fireblast", True
	index = "Mage~Hero Power~2~Fireblast"
	description = "Deal 1 damage"
	def effect(self, target, choice=0):
		damage = (1 + self.Game.playerStatus[self.ID]["Hero Power Damage Boost"]) * (2 ** self.countDamageDouble())
		PRINT(self, "Hero Power Fireblast deals %d damage to %s"%(damage, target.name))
		objtoTakeDamage, damageActual = self.dealsDamage(target, damage)
		if objtoTakeDamage.health < 1 or objtoTakeDamage.dead:
			return 1
		return 0
		
class FireblastRank2(HeroPower):
	mana, name, requireTarget = 2, "Fireblast Rank 2", True
	index = "Mage~Hero Power~2~Fireblast Rank 2"
	description = "Deal 2 damage"
	def effect(self, target, choice=0):
		damage = (2 + self.Game.playerStatus[self.ID]["Hero Power Damage Boost"]) * (2 ** self.countDamageDouble())
		PRINT(self, "Hero Power Fireblast Rank 2 deals %d damage to %s"%(damage, target.name))
		objtoTakeDamage, damageActual = self.dealsDamage(target, damage)
		if objtoTakeDamage.health < 1 or objtoTakeDamage.dead:
			return 1
		return 0
		
class LesserHeal(HeroPower):
	mana, name, requireTarget = 2, "Lesser Heal", True
	index = "Priest~Hero Power~2~Lesser Heal"
	description = "Restore 2 health"
	def effect(self, target, choice=0):
		heal = 2 * (2 ** self.countHealDouble())
		PRINT(self, "Hero Power Lesser Heal restores %d Health to %s"%(heal, target.name))
		obj, targetSurvival = self.restoresHealth(target, heal)
		if targetSurvival > 1:
			return 1
		return 0
		
class Heal(HeroPower):
	mana, name, requireTarget = 2, "Heal", True
	index = "Priest~Hero Power~2~Heal"
	description = "Restore 4 health"
	def effect(self, target, choice=0):
		heal = 4 * (2 ** self.countHealDouble())
		PRINT(self, "Hero Power Heal restores %d Health to %s"%(heal, target.name))
		obj, targetSurvival = self.restoresHealth(target, heal)
		if targetSurvival > 1:
			return 1
		return 0
		
BasicHeroPowers = [Shapeshift, SteadyShot, Fireblast, Reinforce, LesserHeal, DaggerMastery, TotemicCall, LifeTap, ArmorUp]
UpgradedHeroPowers = [DireShapeshift, BallistaShot, FireblastRank2, TheSilverHand, Heal, PoisonedDaggers, TotemicSlam, SoulTap, TankUp]
"""Basic Heroes"""
class Illidan(Hero):
	Class, name, heroPower = "Demon Hunter", "Illidan", DemonClaws
	
class Rexxar(Hero):
	Class, name, heroPower = "Hunter", "Rexxar", SteadyShot
	
class Valeera(Hero):
	Class, name, heroPower = "Rogue", "Valeera", DaggerMastery
	
class Malfurion(Hero):
	Class, name, heroPower = "Druid", "Malfurion", Shapeshift
	
class Garrosh(Hero):
	Class, name, heroPower = "Warrior", "Garrosh", ArmorUp
	
class Uther(Hero):
	Class, name, heroPower = "Paladin", "Uther", Reinforce
	
class Thrall(Hero):
	Class, name, heroPower = "Shaman", "Thrall", TotemicCall
	
class Jaina(Hero):
	Class, name, heroPower = "Mage", "Jaina", Fireblast
	
class Anduin(Hero):
	Class, name, heroPower = "Priest", "Anduin", LesserHeal
	
class Guldan(Hero):
	Class, name, heroPower = "Warlock", "Gul'dan", LifeTap
	
ClassDict = {"Demon Hunter": Illidan, "Druid": Malfurion, "Hunter": Rexxar, "Mage":Jaina, "Paladin":Uther, "Priest":Anduin, "Rogue": Valeera, "Shaman":Thrall, "Warlock": Guldan, "Warrior":Garrosh}

"""Mana 0 cards"""
class TheCoin(Spell):
	Class, name = "Neutral", "The Coin"
	requireTarget, mana = False, 0
	index = "Basic~Neutral~Spell~0~The Coin~Uncollectible"
	description = "Gain 1 mana crystal for this turn."
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		PRINT(self, "The Coin is cast and lets hero gain a mana this turn.")
		if self.Game.ManaHandler.manas[self.ID] < 10:
			self.Game.ManaHandler.manas[self.ID] += 1
		return None
		
"""mana 1 minions"""
class ElvenArcher(Minion):
	Class, race, name = "Neutral", "", "Elven Archer"
	mana, attack, health = 1, 1, 1
	index = "Basic~Neutral~Minion~1~1~1~None~Elven Archer~Battlecry"
	requireTarget, keyWord, description = True, "", "Deal 1 damamge"
	#Dealing damage to minions not on board(moved to grave and returned to deck) won't have any effect.
	#Dealing damage to minions in hand will trigger Frothing Berserker, but that minion will trigger its own damage taken response.
	#When the minion in hand takes damage, at the moment it's replayed, the health will be reset even if it's reduced to below 0.
	#If this is killed before battlecry, will still deal damage.
	#If this is returned to hand before battlecry, will still deal damage.
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if target != None:
			PRINT(self, "Elven Archer's battlecry deals 1 damage to %s"%target.name)
			self.dealsDamage(target, 1) #dealsDamage() on targets in grave/deck will simply pass.
		return target
		
		
class GoldshireFootman(Minion):
	Class, race, name = "Neutral", "", "Goldshire Footman"
	mana, attack, health = 1, 1, 2
	index = "Basic~Neutral~Minion~1~1~2~None~Goldshire Footman~Taunt"
	requireTarget, keyWord, description = False, "Taunt", "Taunt"
	
	
class GrimscaleOracle(Minion):
	Class, race, name = "Neutral", "Murloc", "Grimscale Oracle"
	mana, attack, health = 1, 1, 1
	index = "Basic~Neutral~Minion~1~1~1~Murloc~Grimscale Oracle"
	requireTarget, keyWord, description = False, "", "Give your other Murlocs +1/+1"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.auras["Buff Aura"] = BuffAura_Dealer_All(self, self.applicable, 1, 0)
		
	def applicable(self, target):
		return "Murloc" in target.race
		
		
class MurlocRaider(Minion):
	Class, race, name = "Neutral", "Murloc", "Murloc Raider"
	mana, attack, health = 1, 2, 1
	index = "Basic~Neutral~Minion~1~2~1~Murloc~Murloc Raider"
	requireTarget, keyWord, description = False, "", ""
	
	
class StonetuskBoar(Minion):
	Class, race, name = "Neutral", "Beast", "Stonetusk Boar"
	mana, attack, health = 1, 1, 1
	index = "Basic~Neutral~Minion~1~1~1~Beast~Stonetusk Boar~Charge"
	requireTarget, keyWord, description = False, "Charge", "Charge"
	
	
class VoodooDoctor(Minion):
	Class, race, name = "Neutral", "", "Voodoo Doctor"
	mana, attack, health = 1, 2, 1
	index = "Basic~Neutral~Minion~1~2~1~None~Voodoo Doctor~Battlecry"
	requireTarget, keyWord, description = True, "", "Restore 2 health"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if target != None:
			heal = 2 * (2 ** self.countHealDouble())
			PRINT(self, "Voodoo Doctor's battlecry restores %d health to %s"%(heal, target.name))
			self.restoresHealth(target, heal)
		return target
		
		
class SilverHandRecruit(Minion):
	Class, race, name = "Paladin", "", "Silver Hand Recruit"
	mana, attack, health = 1, 1, 1
	index = "Basic~Paladin~Minion~1~1~1~None~Silver Hand Recruit~Uncollectible"
	requireTarget, keyWord, description = False, "", ""
	
	
"""Mana 2 minions"""
class AcidicSwampOoze(Minion):
	Class, race, name = "Neutral", "", "Acidic Swamp Ooze"
	mana, attack, health = 2, 3, 2
	index = "Basic~Neutral~Minion~2~3~2~None~Acidic Swamp Ooze~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Destroy you opponent's weapon"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		PRINT(self, "Acidic Swamp Ooze's battlecry destroys enemy weapon")
		for weapon in self.Game.weapons[3-self.ID]:
			weapon.destroyed()
		return None
		
		
class BloodfenRaptor(Minion):
	Class, race, name = "Neutral", "Beast", "Bloodfen Raptor"
	mana, attack, health = 2, 3, 2
	index = "Basic~Neutral~Minion~2~3~2~Beast~Bloodfen Raptor"
	requireTarget, keyWord, description = False, "", ""
	
	
class BluegillWarrior(Minion):
	Class, race, name = "Neutral", "Murloc", "Bluegill Warrior"
	mana, attack, health = 2, 2, 1
	index = "Basic~Neutral~Minion~2~2~1~Murloc~Bluegill Warrior~Charge"
	requireTarget, keyWord, description = False, "Charge", "Charge"
	
	
class FrostwolfGrunt(Minion):
	Class, race, name = "Neutral", "", "Frostwolf Grunt"
	mana, attack, health = 2, 2, 2
	index = "Basic~Neutral~Minion~2~2~2~None~Frostwolf Grunt~Taunt"
	requireTarget, keyWord, description = False, "Taunt", "Taunt"
	
	
class KoboldGeomancer(Minion):
	Class, race, name = "Neutral", "", "Kobold Geomancer"
	mana, attack, health = 2, 2, 2
	index = "Basic~Neutral~Minion~2~2~2~None~Kobold Geomancer~Spell Damage"
	requireTarget, keyWord, description = False, "Spell Damage", "Spell Damage +1"
	
	
class MurlocTidehunter(Minion):
	Class, race, name = "Neutral", "Murloc", "Murloc Tidehunter"
	mana, attack, health = 2, 2, 1
	index = "Basic~Neutral~Minion~2~2~1~Murloc~Murloc Tidehunter~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Summon a 1/1 Murloc Scout"
	#If controlled by enemy, will summon for enemy instead.
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		PRINT(self, "Murloc Tidehunter's battlecry summons a 1/1 Murloc Scout")
		self.Game.summonMinion(MurlocScout(self.Game, self.ID), self.position+1, self.ID)
		return None
		
class MurlocScout(Minion):
	Class, race, name = "Neutral", "Murloc", "Murloc Scout"
	mana, attack, health = 1, 1, 1
	index = "Basic~Neutral~Minion~1~1~1~Murloc~Murloc Scout~Uncollectible"
	requireTarget, keyWord, description = False, "", ""
	
	
class NoviceEngineer(Minion):
	Class, race, name = "Neutral", "", "Novice Engineer"
	mana, attack, health = 2, 1, 1
	index = "Basic~Neutral~Minion~2~1~1~None~Novice Engineer~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Draw a card"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		PRINT(self, "Novice Engineer's battlecry lets player draw a card.")
		self.Game.Hand_Deck.drawCard(self.ID)
		return None
		
		
class RiverCrocolisk(Minion):
	Class, race, name = "Neutral", "Beast", "River Crocolisk"
	mana, attack, health = 2, 2, 3
	index = "Basic~Neutral~Minion~2~2~3~Beast~River Crocolisk"
	requireTarget, keyWord, description = False, "", ""
	
"""Mana 3 minions"""		
class DalaranMage(Minion):
	Class, race, name = "Neutral", "", "Dalaran Mage"
	mana, attack, health = 3, 1, 4
	index = "Basic~Neutral~Minion~3~1~4~None~Dalaran Mage~Spell Damage"
	requireTarget, keyWord, description = False, "Spell Damage", "Spell Damage +1"
	
	
class IronforgeRifleman(Minion):
	Class, race, name = "Neutral", "", "Ironforge Rifleman"
	mana, attack, health = 3, 2, 2
	index = "Basic~Neutral~Minion~3~2~2~None~Ironforge Rifleman~Battlecry"
	requireTarget, keyWord, description = True, "", "Battlecry: Deal 1 damage"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if target != None:
			PRINT(self, "Ironforge Rifleman's battlecry deals 1 damage to %s"%target.name)
			self.dealsDamage(target, 1)
		return target
		
		
class IronfurGrizzly(Minion):
	Class, race, name = "Neutral", "Beast", "Ironfur Grizzly"
	mana, attack, health = 3, 3, 3
	index = "Basic~Neutral~Minion~3~3~3~Beast~Ironfur Grizzly~Taunt"
	requireTarget, keyWord, description = False, "Taunt", "Taunt"
	
	
class MagmaRager(Minion):
	Class, race, name = "Neutral", "Elemental", "Magma Rager"
	mana, attack, health = 3, 5, 1
	index = "Basic~Neutral~Minion~3~5~1~Elemental~Magma Rager"
	requireTarget, keyWord, description = False, "", ""
	
	
class RaidLeader(Minion):
	Class, race, name = "Neutral", "", "Raid Leader"
	mana, attack, health = 3, 2, 2
	index = "Basic~Neutral~Minion~3~2~2~None~Raid Leader"
	requireTarget, keyWord, description = False, "", "Your other minions have +1 Attack"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.auras["Buff Aura"] = BuffAura_Dealer_All(self, None, 1, 0)
		
		
class RazorfenHunter(Minion):
	Class, race, name = "Neutral", "", "Razorfen Hunter"
	mana, attack, health = 3, 2, 3
	index = "Basic~Neutral~Minion~3~2~3~None~Razorfen Hunter~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Summon a 1/1 Boar"
	
	#Infer from Dragonling Mechanic.
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		PRINT(self, "Razorfen Hunter's batlecry summons a 1/1 Boar.")
		self.Game.summonMinion(Boar(self.Game, self.ID), self.position+1, self.ID)
		return None
		
class Boar(Minion):
	Class, race, name = "Neutral", "Beast", "Boar"
	mana, attack, health = 1, 1, 1
	index = "Basic~Neutral~Minion~1~1~1~Beast~Boar~Uncollectible"
	requireTarget, keyWord, description = False, "", ""
	
	
class ShatteredSunCleric(Minion):
	Class, race, name = "Neutral", "", "Shattered Sun Cleric"
	mana, attack, health = 3, 3, 2
	index = "Basic~Neutral~Minion~3~3~2~None~Shattered Sun Cleric~Battlecry"
	requireTarget, keyWord, description = True, "", "Battlecry: Give friendly minion +1/+1"
	
	def targetExists(self, choice=0):
		return self.selectableFriendlyMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.ID == self.ID and target.onBoard and target != self
		
	#Infer from Houndmaster: Buff can apply on targets on board, in hand, in deck.
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if target != None:
			PRINT(self, "Shattered Sun Cleric's battlecry gives friendly minion %s +1/+1."%target.name)
			target.buffDebuff(1, 1)
		return target
		
		
class SilverbackPatriarch(Minion):
	Class, race, name = "Neutral", "Beast", "Silverback Patriarch"
	mana, attack, health = 3, 1, 4
	index = "Basic~Neutral~Minion~3~1~4~Beast~Silverback Patriarch~Taunt"
	requireTarget, keyWord, description = False, "Taunt", "Taunt"
	
	
class Wolfrider(Minion):
	Class, race, name = "Neutral", "", "Wolfrider"
	mana, attack, health = 3, 3, 1
	index = "Basic~Neutral~Minion~3~3~1~None~Wolfrider~Charge"
	requireTarget, keyWord, description = False, "Charge", "Charge"
	
"""Mana 4 minions"""
class ChillwindYeti(Minion):
	Class, race, name = "Neutral", "", "Chillwind Yeti"
	mana, attack, health = 4, 4, 5
	index = "Basic~Neutral~Minion~4~4~5~None~Chillwind Yeti"
	requireTarget, keyWord, description = False, "", ""
	
	
class DragonlingMechanic(Minion):
	Class, race, name = "Neutral", "", "Dragonling Mechanic"
	mana, attack, health = 4, 2, 4
	index = "Basic~Neutral~Minion~4~2~4~None~Dragonling Mechanic~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Summon a 2/1 Mechanical Dragonling"
	
	#If returned to hand, will summon to the rightend of the board.
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		PRINT(self, "Dragonling Mechanic's battlecry summons a 2/1 Mechanical Dragonling.")
		self.Game.summonMinion(MechanicDragonling(self.Game, self.ID), self.position+1, self.ID)
		return None
		
class MechanicalDragonling(Minion):
	Class, race, name = "Neutral", "Mech", "Dragonling Mechanic"
	mana, attack, health = 1, 2, 1
	index = "Basic~Neutral~Minion~1~2~1~Mech~Mechanical Dragonling~Uncollectible"
	requireTarget, keyWord, description = False, "", ""
	
	
class GnomishInventor(Minion):
	Class, race, name = "Neutral", "", "Gnomish Inventor"
	mana, attack, health = 4, 2, 4
	index = "Basic~Neutral~Minion~4~2~4~None~Gnomish Inventor~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Draw a card"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		PRINT(self, "Gnomish Inventor's battlecry lets player draw a card.")
		self.Game.Hand_Deck.drawCard(self.ID)
		return None
		
		
class OasisSnapjaw(Minion):
	Class, race, name = "Neutral", "Beast", "Oasis Snapjaw"
	mana, attack, health = 4, 2, 7
	index = "Basic~Neutral~Minion~4~2~7~Beast~Oasis Snapjaw"
	requireTarget, keyWord, description = False, "", ""
	
	
class OgreMagi(Minion):
	Class, race, name = "Neutral", "", "Ogre Magi"
	mana, attack, health = 4, 4, 4
	index = "Basic~Neutral~Minion~4~4~4~None~Ogre Magi~Spell Damage"
	requireTarget, keyWord, description = False, "Spell Damage", "Spell Damage +1"
	
	
class SenjinShieldmasta(Minion):
	Class, race, name = "Neutral", "", "Sen'jin Shieldmasta"
	mana, attack, health = 4, 3, 5
	index = "Basic~Neutral~Minion~4~3~5~None~Sen'jin Shieldmasta~Taunt"
	requireTarget, keyWord, description = False, "Taunt", "Taunt"
	
	
class StormwindKnight(Minion):
	Class, race, name = "Neutral", "", "Stormwind Knight"
	mana, attack, health = 4, 2, 5
	index = "Basic~Neutral~Minion~4~2~5~None~Stormwind Knight~Charge"
	requireTarget, keyWord, description = False, "Charge", "Charge"
	
"""Mana 5 minions"""
class BootyBayBodyguard(Minion):
	Class, race, name = "Neutral", "", "Booty Bay Bodyguard"
	mana, attack, health = 5, 5, 4
	index = "Basic~Neutral~Minion~5~5~4~None~Booty Bay Bodyguard~Taunt"
	requireTarget, keyWord, description = False, "Taunt", "Taunt"
	
	
class DarkscaleHealer(Minion):
	Class, race, name = "Neutral", "", "Darkscale Healer"
	mana, attack, health = 5, 4, 5
	index = "Basic~Neutral~Minion~5~4~5~None~Darkscale Healer~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Restore 2 health to all friendly characters"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		heal = 2 * (2 ** self.countHealDouble())
		targets = [self.Game.heroes[self.ID]] + self.Game.minionsonBoard(self.ID)
		PRINT(self, "Darkscale Healer's battlecry restores %d health to all friendly characters."%heal)
		self.restoresAOE(targets, [heal for obj in targets])
		return None
		
		
class FrostwolfWarlord(Minion):
	Class, race, name = "Neutral", "", "Frostwolf Warlord"
	mana, attack, health = 5, 4, 4
	index = "Basic~Neutral~Minion~5~4~4~None~Frostwolf Warlord~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Gain +1/+1 for each other friendly minion on the battlefield"
	
	#For self buffing effects, being dead and removed before battlecry will prevent the battlecry resolution.
	#If this minion is returned hand before battlecry, it can still buff it self according to living friendly minions.
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if self.onBoard or self.inHand: #For now, no battlecry resolution shuffles this into deck.
			num = len(self.Game.minionsAlive(self.ID, self))
			PRINT(self, "Frostwolf Warlord's battlecry gives minion +1/+1 for each other friendly minion.")
			self.buffDebuff(num, num)
		return None
		
#When takes damage in hand(Illidan/Juggler/Anub'ar Ambusher), won't trigger the +3 Attack buff.
class GurubashiBerserker(Minion):
	Class, race, name = "Neutral", "", "Gurubashi Berserker"
	mana, attack, health = 5, 2, 7
	index = "Basic~Neutral~Minion~5~2~7~None~Gurubashi Berserker"
	requireTarget, keyWord, description = False, "", "Whenever this minion takes damage, gain +3 Attack"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_GurubashiBerserker(self)]
		
class Trigger_GurubashiBerserker(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionTakesDamage"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return target == self.entity and self.entity.onBoard
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self, "%s takes Damage and gains +3 Attack."%self.entity.name)
		self.entity.buffDebuff(3, 0)
		
		
class Nightblade(Minion):
	Class, race, name = "Neutral", "", "Nightblade"
	mana, attack, health = 5, 4, 4
	index = "Basic~Neutral~Minion~5~4~4~None~Nightblade~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Deal 3 damage to the enemy hero"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		PRINT(self, "Nightblade's battlecry deals 3 damage to the enemy hero.")
		self.dealsDamage(self.Game.heroes[3-self.ID], 3)
		return None
		
		
class StormpikeCommando(Minion):
	Class, race, name = "Neutral", "", "Stormpike Commando"
	mana, attack, health = 5, 4, 2
	index = "Basic~Neutral~Minion~5~4~2~None~Stormpike Commando~Battlecry"
	requireTarget, keyWord, description = True, "", "Battlecry: Deal 2 damage"
	#Infer from Fire Plume Phoenix
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if target != None:
			PRINT(self, "Stormpike Commando's battlecry deals 2 damage to %s"%target.name)
			self.dealsDamage(target, 2)
		return target
		
"""Mana 6 minions"""
class LordoftheArena(Minion):
	Class, race, name = "Neutral", "", "Lord of the Arena"
	mana, attack, health = 6, 6, 5
	index = "Basic~Neutral~Minion~6~6~5~None~Lord of the Arena~Taunt"
	requireTarget, keyWord, description = False, "Taunt", "Taunt"
	
	
class Archmage(Minion):
	Class, race, name = "Neutral", "", "Archmage"
	mana, attack, health = 6, 4, 7
	index = "Basic~Neutral~Minion~6~4~7~None~Archmage~Spell Damage"
	requireTarget, keyWord, description = False, "Spell Damage", "Spell Damage +1"
	
	
class BoulderfistOgre(Minion):
	Class, race, name = "Neutral", "", "Boulderfist Ogre"
	mana, attack, health = 6, 6, 7
	index = "Basic~Neutral~Minion~6~6~7~None~Boulderfist Ogre"
	requireTarget, keyWord, description = False, "", ""
	
	
class RecklessRocketeer(Minion):
	Class, race, name = "Neutral", "", "Reckless Rocketeer"
	mana, attack, health = 6, 5, 2
	index = "Basic~Neutral~Minion~6~5~2~None~Reckless Rocketeer~Charge"
	requireTarget, keyWord, description = False, "Charge", "Charge"
	
"""Mana 7 minions"""
class CoreHound(Minion):
	Class, race, name = "Neutral", "Beast", "Core Hound"
	mana, attack, health = 7, 9, 5
	index = "Basic~Neutral~Minion~7~9~5~Beast~Core Hound"
	requireTarget, keyWord, description = False, "", ""
	
	
class StormwindChampion(Minion):
	Class, race, name = "Neutral", "", "Stormwind Champion"
	mana, attack, health = 7, 6, 6
	index = "Basic~Neutral~Minion~7~6~6~None~Stormwind Champion"
	requireTarget, keyWord, description = False, "", "Your other minions have +1/+1"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.auras["Buff Aura"] = BuffAura_Dealer_All(self, None, 1, 1)
		
		
class WarGolem(Minion):
	Class, race, name = "Neutral", "", "War Golem"
	mana, attack, health = 7, 7, 7
	index = "Basic~Neutral~Minion~7~7~7~None~War Golem"
	requireTarget, keyWord, description = False, "", ""
	
"""Demon Hunter cards"""
class ShadowhoofSlayer(Minion):
	Class, race, name = "Demon Hunter", "Demon", "Shadowhoof Slayer"
	mana, attack, health = 1, 2, 1
	index = "Basic~Demon Hunter~Minion~1~2~1~Demon~Shadowhoof Slayer~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Give your hero +1 Attack this turn"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		PRINT(self, "Shadowhoof Slayer's battlecry gives player +1 Attack this turn")
		self.Game.heroes[self.ID].gainTempAttack(1)
		return None
		
		
class ChaosStrike(Spell):
	Class, name = "Demon Hunter", "Chaos Strike"
	requireTarget, mana = False, 2
	index = "Basic~Demon Hunter~Spell~2~Chaos Strike"
	description = "Give your hero +2 Attack this turn. Draw a card"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		PRINT(self, "Chaos Strike is cast, gives player +2 Attack this turn and lets player draw a card")
		self.Game.heroes[self.ID].gainTempAttack(2)
		self.Game.Hand_Deck.drawCard(self.ID)
		return None
		
		
class SightlessWatcher(Minion):
	Class, race, name = "Demon Hunter", "Demon", "Sightless Watcher"
	mana, attack, health = 2, 3, 2
	index = "Basic~Demon Hunter~Minion~2~3~2~Demon~Sightless Watcher~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Look at 3 cards in your deck. Choose one to put on top"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if len(self.Game.Hand_Deck.decks[self.ID]) > 1: #卡组数小于2张时没有作用
			if "InvokedbyOthers" in comment :
				PRINT(self, "Sightless Watcher's battlecry puts a random card in player's deck on top of the deck")
				index = np.random.randint(len(self.Game.Hand_Deck.decks[self.ID]))
				self.Game.Hand_Deck.decks[self.ID].append(self.Game.Hand_Deck.decks[self.ID].pop(index))
			else:
				PRINT(self, "Sightless Watcher's battlecry lets player look at 3 cards in the deck and put one on top")
				numCardsLeft = len(self.Game.Hand_Deck.decks[self.ID])
				self.Game.options = np.random.choice(self.Game.Hand_Deck.decks[self.ID], min(3, numCardsLeft), replace=False)
				self.Game.DiscoverHandler.startDiscover(self)
		return None
		
	def discoverDecided(self, option):
		PRINT(self, "Card %s in player's deck will be put on top"%option.name)
		index = self.Game.Hand_Deck.decks[self.ID].index(option)
		self.Game.Hand_Deck.decks[self.ID].append(self.Game.Hand_Deck.decks[self.ID].pop(index))
		
		
class AldrachiWarblades(Weapon):
	Class, name, description = "Demon Hunter", "Aldrachi Warblades", "Lifesteal"
	mana, attack, durability = 3, 2, 3
	index = "Basic~Demon Hunter~Weapon~3~2~3~Aldrachi Warblades~Lifesteal"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.keyWords["Lifesteal"] = 1
		
		
class CoordinatedStrike(Spell):
	Class, name = "Demon Hunter", "Coordinated Strike"
	requireTarget, mana = False, 3
	index = "Basic~Demon Hunter~Spell~3~Coordinated Strike"
	description = "Summon three 1/1 Illidari with Rush"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		PRINT(self, "Coordinated Strike is cast and summons three 1/1 Illidari with Rush")
		self.Game.summonMinion([IllidariInitiate(self.Game, self.ID) for i in range(3)], (-1, "totheRightEnd"), self.ID)
		return None
		
class IllidariInitiate(Minion):
	Class, race, name = "Demon Hunter", "", "Illidari Initiate"
	mana, attack, health = 1, 1, 1
	index = "Basic~Demon Hunter~Minion~1~1~1~None~Illidari~Uncollectible"
	requireTarget, keyWord, description = False, "Rush", "Rush"
	
class SatyrOverseer(Minion):
	Class, race, name = "Demon Hunter", "Demon", "Satyr Overseer"
	mana, attack, health = 3, 4, 2
	index = "Basic~Demon Hunter~Minion~3~4~2~Demon~Satyr Overseer"
	requireTarget, keyWord, description = False, "", "After your hero attacks, summon a 2/2 Satyr"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_SatyrOverseer(self)]
		
class Trigger_SatyrOverseer(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["HeroAttackedMinion", "HeroAttackedHero"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject == self.entity.Game.heroes[self.entity.ID]
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self, "After friendly hero attacks, %s summons a 2/2 Satyr"%self.entity.name)
		self.entity.Game.summonMinion(IllidariSatyr(self.entity.Game, self.entity.ID), self.entity.position+1, self.entity.ID)
		
class IllidariSatyr(Minion):
	Class, race, name = "Demon Hunter", "Demon", "Illidari Satyr"
	mana, attack, health = 2, 2, 2
	index = "Basic~Demon Hunter~Minion~2~2~2~Demon~Illidari Satyr~Uncollectible"
	requireTarget, keyWord, description = False, "", ""
	
	
class SoulCleave(Spell):
	Class, name = "Demon Hunter", "Soul Cleave"
	requireTarget, mana = False, 3
	index = "Basic~Demon Hunter~Spell~3~Soul Cleave"
	description = "Lifesteal. Deal 2 damage to two random enemy minions"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.keyWords["Lifesteal"] = 1
		
	def randomorDiscover(self):
		if len(self.Game.minionsonBoard(3-self.ID)) < 3:
			return "No RNG"
		return "Random"
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		damage = (2 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		minions = self.Game.minionsonBoard(3-self.ID)
		if len(minions) > 1:
			targets = np.random.choice(minions, 2, replace=False)
			PRINT(self, "Soul Cleave deals {} damage to two random minions: {}".format(damage, targets))
			self.dealsAOE(targets, [damage, damage])
		elif len(minions) == 1:
			PRINT(self, "Soul Cleave deals %d damage to minion %s"%(damage, minions[0].name))
			self.dealsDamage(minions[0], damage)
		return None
		
		
class ChaosNova(Spell):
	Class, name = "Demon Hunter", "Chaos Nova"
	requireTarget, mana = False, 5
	index = "Basic~Demon Hunter~Spell~5~Chaos Nova"
	description = "Deal 4 damage to all minions"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		damage = (4 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		targets = self.Game.minionsonBoard(1) + self.Game.minionsonBoard(2)
		PRINT(self, "Chaos Nova deals %d damage to all minions."%damage)
		self.dealsAOE(targets, [damage for obj in targets])
		return None
		
		
class GlaiveboundAdept(Minion):
	Class, race, name = "Demon Hunter", "", "Glaivebound Adept"
	mana, attack, health = 5, 7, 4
	index = "Basic~Demon Hunter~Minion~5~7~4~None~Glaivebound Adept~Battlecry"
	requireTarget, keyWord, description = True, "", "Battlecry: If your hero attacked this turn, deal 4 damage"
	
	def effectCanTrigger(self):
		self.effectViable = self.Game.CounterHandler.heroAttackTimesThisTurn[self.ID] > 0
		
	def returnTrue(self, choice=0):
		return self.Game.CounterHandler.heroAttackTimesThisTurn[self.ID] > 0
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if target != None and self.Game.CounterHandler.heroAttackTimesThisTurn[self.ID] > 0:
			PRINT(self, "Glaivebound Adept's battlecry deals 4 damage to target %s"%target.name)
			self.dealsDamage(target, 4)
		return target
		
		
class InnerDemon(Spell):
	Class, name = "Demon Hunter", "Inner Demon"
	requireTarget, mana = False, 8
	index = "Basic~Demon Hunter~Spell~8~Inner Demon"
	description = "Give your hero +8 Attack this turn"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		PRINT(self, "Inner Demon is cast and gives player +8 Attack this turn")
		self.Game.heroes[self.ID].gainTempAttack(8)
		return None
		
"""Druid cards"""
class Innervate(Spell):
	Class, name = "Druid", "Innervate"
	requireTarget, mana = False, 0
	index = "Basic~Druid~Spell~0~Innervate"
	description = "Gain 1 Mana Crystal this turn only"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		PRINT(self, "Innervate hero gains a mana for this turn.")
		if self.Game.ManaHandler.manas[self.ID] < 10:
			self.Game.ManaHandler.manas[self.ID] += 1
		return None
		
		
class Moonfire(Spell):
	Class, name = "Druid", "Moonfire"
	requireTarget, mana = True, 0
	index = "Basic~Druid~Spell~0~Moonfire"
	description = "Deal 1 damage"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if target != None:
			damage = (1 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			PRINT(self, "Moonfire deals %d damage to %s"%(damage, target.name))
			self.dealsDamage(target, damage)
		return target
		
		
class Claw(Spell):
	Class, name = "Druid", "Claw"
	requireTarget, mana = False, 1
	index = "Basic~Druid~Spell~1~Claw"
	description = "Give your hero +2 Attack this turn. Gain 2 Armor"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		PRINT(self, "Claw hero %d %s gains 2 Sttack and 2 Armor"%(self.ID, self.Game.heroes[self.ID].name))
		self.Game.heroes[self.ID].gainTempAttack(2)
		self.Game.heroes[self.ID].gainsArmor(2)
		return None
		
		
class MarkoftheWild(Spell):
	Class, name = "Druid", "Mark of the Wild"
	requireTarget, mana = True, 2
	index = "Basic~Druid~Spell~2~Mark of the Wild"
	description = "Give a minion +2/+2 ant Taunt"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		if target.cardType == "Minion" and target.onBoard:
			return True
		return False
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if target != None:
			PRINT(self, "Mark of the Wild gives minion %s +2/+2 and Taunt."%target.name)
			target.buffDebuff(2, 2) #buffDebuff() and getsKeyword() will check if the minion is onBoard or inHand.
			target.getsKeyword("Taunt")
		return target
		
		
class HealingTouch(Spell):
	Class, name = "Druid", "Healing Touch"
	requireTarget, mana = True, 3
	index = "Basic~Druid~Spell~3~Healing Touch"
	description = "Restore 8 health"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if target != None:
			heal = 8 * (2 ** self.countHealDouble())
			PRINT(self, "Healing Touch restores %d health to %s"%(heal, target.name))
			self.restoresHealth(target, heal)
		return target
		
		
class SavageRoar(Spell):
	Class, name = "Druid", "Savage Roar"
	requireTarget, mana = False, 3
	index = "Basic~Druid~Spell~3~Savage Roar"
	description = "Give your characters +2 Attack this turn"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		PRINT(self, "Savage Roar gives all friendly characters +2 Attack this turn.")
		self.Game.heroes[self.ID].gainTempAttack(2)
		for minion in fixedList(self.Game.minionsonBoard(self.ID)):
			minion.buffDebuff(2, 0, "EndofTurn")
		return None
		
		
class WildGrowth(Spell):
	Class, name = "Druid", "Wild Growth"
	requireTarget, mana = False, 3
	index = "Basic~Druid~Spell~3~Wild Growth"
	description = "Gain an empty Mana Crystal"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		PRINT(self, "Wild Growth gives player an empty Mana Crystal.")
		if self.Game.ManaHandler.gainEmptyManaCrystal(1, self.ID) == False:
			PRINT(self, "Player's mana at upper limit already. Wild Growth gives player an Excess Mana instead.")
			self.Game.Hand_Deck.addCardtoHand(ExcessMana(self.Game, self.ID), self.ID)
		return None
		
class ExcessMana(Spell):
	Class, name = "Druid", "Excess Mana"
	requireTarget, mana = False, 0
	index = "Basic~Druid~Spell~0~Excess Mana~Uncollectible"
	description = "Draw a card"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		PRINT(self, "Excess Mana lets player draw a card.")
		self.Game.Hand_Deck.drawCard(self.ID)
		return None
		
		
class Swipe(Spell):
	Class, name = "Druid", "Swipe"
	requireTarget, mana = True, 4
	index = "Basic~Druid~Spell~4~Swipe"
	description = "Deal 4 damage to an enemy and 1 damage to all other enemies"
	def available(self):
		return self.selectableEnemyExists()
		
	def targetCorrect(self, target, choice=0):
		return (target.cardType == "Minion" or target.cardType == "Hero") and target.ID != self.ID and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if target != None:
			AOEdamage = (1 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			targetdamage = (4 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			targets = [self.Game.heroes[3-self.ID]] + self.Game.minionsonBoard(3-self.ID)
			PRINT(self, "Swipe deals %d damage to %s and %d damage to all other enemies"%(targetdamage, target.name, AOEdamage))
			extractfrom(target, targets)
			if targets != []:
				self.dealsAOE([target]+targets, [targetdamage]+[AOEdamage for obj in targets])
			else:
				self.dealsDamage(target, targetdamage)
		return target
		
		
class Starfire(Spell):
	Class, name = "Druid", "Starfire"
	requireTarget, mana = True, 6
	index = "Basic~Druid~Spell~6~Starfire"
	description = "Deal 5 damage. Draw a card"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if target != None:
			damage = (5 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			PRINT(self, "Starfire deals %d damage to %s and lets player draw a card."%(damage, target.name))
			self.dealsDamage(target, damage)
		self.Game.Hand_Deck.drawCard(self.ID)
		return target
		
		
class IronbarkProtector(Minion):
	Class, race, name = "Druid", "", "Ironbark Protector"
	mana, attack, health = 8, 8, 8
	index = "Basic~Druid~Minion~8~8~8~None~Ironbark Protector~Taunt"
	requireTarget, keyWord, description = False, "Taunt", "Taunt"
	
"""Hunter Cards"""
class ArcaneShot(Spell):
	Class, name = "Hunter", "Arcane Shot"
	requireTarget, mana = True, 1
	index = "Basic~Hunter~Spell~1~Arcane Shot"
	description = "Deal 2 damage"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if target != None:
			damage = (2 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			PRINT(self, "Arcane Shot deals %d damage to %s"%(damage, target.name))
			self.dealsDamage(target, damage)
		return target
		
class TimberWolf(Minion):
	Class, race, name = "Hunter", "Beast", "Timber Wolf"
	mana, attack, health = 1, 1, 1
	index = "Basic~Hunter~Minion~1~1~1~Beast~Timber Wolf"
	requireTarget, keyWord, description = False, "", "Your other Beasts have +1 Attack"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.auras["Buff Aura"] = BuffAura_Dealer_All(self, self.applicable, 1, 0)
		
	def applicable(self, target):
		return "Beast" in target.race
		
		
#In real game, when there is only one card left in deck,
# player still needs to choose, despite only one option available.
class Tracking(Spell):
	Class, name = "Hunter", "Tracking"
	requireTarget, mana = False, 1
	index = "Basic~Hunter~Spell~1~Tracking"
	description = "Look at the top 3 cards of your deck. Draw one and discard the others."
	def randomorDiscover(self):
		if len(self.Game.Hand_Deck.decks[self.ID]) < 2:
			return "No RNG"
		else:
			return "Discover"
			
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		PRINT(self, "Tracking is cast and enters the discover preparation.")
		numCardsLeft = len(self.Game.Hand_Deck.decks[self.ID])
		if numCardsLeft  == 1:
			PRINT(self, "Tracking player draws the only remaining card from deck.")					
			self.Game.Hand_Deck.drawCard(self.ID)
		elif numCardsLeft > 1:
			num = min(3, numCardsLeft)
			cards = [self.Game.Hand_Deck.decks[self.ID][-i] for i in range(num)]
			if "CastbyOthers" in comment:
				cardtoDraw = cards.pop(np.random.randint(num))
				PRINT(self, "Tracking randomly draws one of the top 3 cards. And removes the other two.")
				self.Game.Hand_Deck.drawCard(self.ID, cardtoDraw)
				self.Game.Hand_Deck.extractfromDeck(cards)
			else:
				self.Game.options = cards
				self.Game.DiscoverHandler.startDiscover(self)
				
		return None
		
	def discoverDecided(self, option):
		PRINT(self, "Tracking lets player draw card %s from the top 3 cards in deck"%option.name)
		cardtoDraw = extractfrom(option, self.Game.options)
		self.Game.Hand_Deck.drawCard(self.ID, cardtoDraw)
		self.Game.Hand_Deck.extractfromDeck(self.Game.options)
		
		
class HuntersMark(Spell):
	Class, name = "Hunter", "Hunter's Mark"
	requireTarget, mana = True, 2
	index = "Basic~Hunter~Spell~2~Hunter's Mark"
	description = "Change a minion's health to 1"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		if target.cardType == "Minion" and target.onBoard:
			return True
		return False
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if target != None:
			PRINT(self, "Hunter's Mark sets %s's health to 1."%target.name)
			target.statReset(False, 1)
		return target
		
class AnimalCompanion(Spell):
	Class, name = "Hunter", "Animal Companion"
	requireTarget, mana = False, 3
	index = "Basic~Hunter~Spell~3~Animal Companion"
	description = "Summon a random Beast Companion"
	def available(self):
		if self.Game.spaceonBoard(self.ID) > 0:
			return True
		return False
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if self.Game.spaceonBoard(self.ID) > 0:
			companion = np.random.choice([Huffer, Leokk, Misha])(self.Game, self.ID)
			PRINT(self, "Animal Companion summons %s"%companion.name)
			self.Game.summonMinion(companion, -1, self.ID)
		return None
		
class Huffer(Minion):
	Class, race, name = "Hunter", "Beast", "Huffer"
	mana, attack, health = 3, 4, 2
	index = "Basic~Hunter~Minion~3~4~2~Beast~Huffer~Charge~Uncollectible"
	requireTarget, keyWord, description = False, "Charge", "Charge"
	
class Leokk(Minion):
	Class, race, name = "Hunter", "Beast", "Leokk"
	mana, attack, health = 3, 2, 4
	index = "Basic~Hunter~Minion~3~2~4~Beast~Leokk~Uncollectible"
	requireTarget, keyWord, description = False, "", "Your other minions have +1 Attack"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.auras["Buff Aura"] = BuffAura_Dealer_All(self, None, 1, 0)
		
class Misha(Minion):
	Class, race, name = "Hunter", "Beast", "Misha"
	mana, attack, health = 3, 4, 4
	index = "Basic~Hunter~Minion~3~4~4~Beast~Misha~Taunt~Uncollectible"
	requireTarget, keyWord, description = False, "Taunt", "Taunt"
	
	
class KillCommand(Spell):
	Class, name = "Hunter", "Kill Command"
	requireTarget, mana = True, 3
	index = "Basic~Hunter~Spell~3~Kill Command"
	description = "Deal 3 damage. If you control a Beast, deal 5 damage instead"
	def effectCanTrigger(self):
		self.effectViable = False
		for minion in self.Game.minionsonBoard(self.ID):
			if "Beast" in minion.race:
				self.effectViable = True
				break
				
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if target != None:
			controlsBeast = False
			for minion in self.Game.minionsonBoard(self.ID):
				if "Beast" in minion.race:
					controlsBeast = True
					break
			if controlsBeast:
				damage = (5 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			else:
				damage = (3 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
				
			PRINT(self, "Kill Command deals %d damage to %s"%(damage, target.name))
			self.dealsDamage(target, damage)
		return target
		
		
class Houndmaster(Minion):
	Class, race, name = "Hunter", "", "Houndmaster"
	mana, attack, health = 4, 4, 3
	index = "Basic~Hunter~Minion~4~4~3~None~Houndmaster~Battlecry"
	requireTarget, keyWord, description = True, "", "Battlecry: Give a friendly Beast +2/+2 and Taunt"
	
	def targetExists(self, choice=0):
		return self.selectableFriendlyMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.ID == self.ID and "Beast" in target.race and target != self and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if target != None:
			PRINT(self, "Houndmaster's battlecry gives friendly Beast %s +2/+2 and Taunt."%target.name)
			target.buffDebuff(2, 2)
			target.getsKeyword("Taunt")
		return target
		
		
class MultiShot(Spell):
	Class, name = "Hunter", "Multi Shot"
	requireTarget, mana = False, 4
	index = "Basic~Hunter~Spell~4~Multi Shot"
	description = "Deal 3 damage to two random enemy minions"
	def randomorDiscover(self):
		if len(self.Game.minionsonBoard(3-self.ID)) < 3:
			return "No RNG"
		return "Random"
		
	def available(self):
		if self.Game.minionsonBoard(3-self.ID) != []:
			return True
		return False
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		damage = (3 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		minions = self.Game.minionsonBoard(3-self.ID)
		if len(minions) > 1:
			PRINT(self, "Multi Shot deals {} damage to two random minions: {}".format(damage, targets))
			targets = np.random.choice(minions, 2, replace=False)
			self.dealsAOE(targets, [damage, damage])
		elif len(minions) == 1:
			PRINT(self, "Multi Shot deals %d damage to minion %s"%(damage, minions[0].name))
			self.dealsDamage(minions[0], damage)
		return None
		
		
class StarvingBuzzard(Minion):
	Class, race, name = "Hunter", "Beast", "Starving Buzzard"
	mana, attack, health = 5, 3, 2
	index = "Basic~Hunter~Minion~5~3~2~Beast~Starving Buzzard"
	requireTarget, keyWord, description = False, "", "Whenever you summon a Beast, draw a card"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_StarvingBuzzard(self)]
		
class Trigger_StarvingBuzzard(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionSummoned"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and self.entity.health > 0 and subject.ID == self.entity.ID and "Beast" in subject.race and subject != self.entity
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self, "A friendly Beast is summoned and %s lets player draw a card."%self.entity.name)
		self.entity.Game.Hand_Deck.drawCard(self.entity.ID)
		
		
class TundraRhino(Minion):
	Class, race, name = "Hunter", "Beast", "Tundra Rhino"
	mana, attack, health = 5, 2, 5
	index = "Basic~Hunter~Minion~5~2~5~Beast~Tundra Rhino"
	requireTarget, keyWord, description = False, "", "Your Beasts have Charge"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.auras["Has Aura"] = HasAura_Dealer(self, self.applicable, "Charge")
		
	def applicable(self, target):
		return "Beast" in target.race
		
"""Mage cards"""
class ArcaneMissiles(Spell):
	Class, name = "Mage", "Arcane Missiles"
	requireTarget, mana = False, 1
	index = "Basic~Mage~Spell~1~Arcane Missiles"
	description = "Deal 3 damage randomly split among all enemies"
	def randomorDiscover(self):
		if self.Game.minionsonBoard(3-self.ID) == []:
			return "No RNG"
		return "Random"
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		num = (3 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		PRINT(self, "Arcane Missiles launches %d missiles."%num)
		for i in range(num):
			targets = self.Game.livingObjtoTakeRandomDamage(3-self.ID)
			target = np.random.choice(targets)
			PRINT(self, "Arcane Missile deals 1 damage to %s"%target.name)
			self.dealsDamage(target, 1)
		return None
		
		
class MirrorImage(Spell):
	Class, name = "Mage", "Mirror Image"
	requireTarget, mana = False, 1
	index = "Basic~Mage~Spell~1~Mirror Image"
	description = "Summon two 0/2 minions with Taunt"
	def available(self):
		if self.Game.spaceonBoard(self.ID):
			return True
		return False
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		PRINT(self, "Mirror Image summons two 0/2 Mirror Images with Taunt.")
		self.Game.summonMinion([MirrorImage_Minion(self.Game, self.ID) for i in range(2)], (-11, "totheRightEnd"), self.ID)
		return None
		
class MirrorImage_Minion(Minion):
	Class, race, name = "Mage", "", "Mirror Image"
	mana, attack, health = 1, 0, 2
	index = "Basic~Mage~Minion~1~0~2~None~Mirror Image~Taunt~Uncollectible"
	requireTarget, keyWord, description = False, "Taunt", "Taunt"
	
	
class ArcaneExplosion(Spell):
	Class, name = "Mage", "Arcane Explosion"
	requireTarget, mana = False, 2
	index = "Basic~Mage~Spell~2~Arcane Explosion"
	description = "Deal 1 damage to all enemy minions"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		damage = (1 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		targets = self.Game.minionsonBoard(3-self.ID)
		PRINT(self, "Arcane Explosion deals %d damage to all enemy minions"%damage)
		self.dealsAOE(targets, [damage for obj in targets])
		return None
		
		
class Frostbolt(Spell):
	Class, name = "Mage", "Frostbolt"
	requireTarget, mana = True, 2
	index = "Basic~Mage~Spell~2~Frostbolt"
	description = "Deal 3 damage to a character and Freeze it"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if target != None:
			damage = (3 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			PRINT(self, "Frostbolt deals %d damage to %s and freezes it."%(damage, target.name))
			self.dealsDamage(target, damage)
			target.getsFrozen()
		return target
		
		
class ArcaneIntellect(Spell):
	Class, name = "Mage", "Arcane Intellect"
	requireTarget, mana = False, 3
	index = "Basic~Mage~Spell~3~Arcane Intellect"
	description = "Draw 2 cards"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		PRINT(self, "Arcane Intellect lets player draws two cards")
		self.Game.Hand_Deck.drawCard(self.ID)
		self.Game.Hand_Deck.drawCard(self.ID)
		return None
		
		
class FrostNova(Spell):
	Class, name = "Mage", "Frost Nova"
	requireTarget, mana = False, 3
	index = "Basic~Mage~Spell~3~Frost Nova"
	description = "Freeze all enemy minions"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		PRINT(self, "Frost Nova freezes all enemy minions")
		#Fix the targets so that minions that resolutions that summon minions due to minion being frozen won't make the list expand.
		for minion in fixedList(self.Game.minionsonBoard(3-self.ID)):
			minion.getsFrozen()
		return None
		
		
class Fireball(Spell):
	Class, name = "Mage", "Fireball"
	requireTarget, mana = True, 4
	index = "Basic~Mage~Spell~4~Fireball"
	description = "Deal 6 damage"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if target != None:
			damage = (6 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			PRINT(self, "Fireball deals %d damage to %s"%(damage, target.name))
			self.dealsDamage(target, damage)
		return target
		
		
class Polymorph(Spell):
	Class, name = "Mage", "Polymorph"
	requireTarget, mana = True, 4
	index = "Basic~Mage~Spell~4~Polymorph"
	description = "Transform a minion into a 1/1 Sheep"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if target != None:
			PRINT(self, "Polymorph transforms minion %s into a 1/1 Sheep."%target.name)
			newMinion = Sheep(self.Game, target.ID)
			self.Game.transform(target, newMinion)
			target = newMinion
		return target
		
class Sheep(Minion):
	Class, race, name = "Neutral", "Beast", "Sheep"
	mana, attack, health = 1, 1, 1
	index = "Basic~Neutral~Minion~1~1~1~Beast~Sheep~Uncollectible"
	requireTarget, keyWord, description = False, "", ""
	
	
class WaterElemental(Minion):
	Class, race, name = "Mage", "Elemental", "Water Elemental"
	mana, attack, health = 4, 3, 6
	index = "Basic~Mage~Minion~4~3~6~Elemental~Water Elemental"
	requireTarget, keyWord, description = False, "", "Freeze any character damaged by this minion"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_WaterElemental(self)]
		
class Trigger_WaterElemental(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionTakesDamage", "HeroTakesDamage"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return subject == self.entity
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self, "%s deals damage to %s and freezes it."%(self.entity.name, target.name))
		target.getsFrozen()
		
		
class Flamestrike(Spell):
	Class, name = "Mage", "Flamestrike"
	requireTarget, mana = False, 7
	index = "Basic~Mage~Spell~7~Flamestrike"
	description = "Deal 4 damage to all enemy minions"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		damage = (4 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		PRINT(self, "Flamestrike deals %d damage to all enemy minions"%damage)
		targets = self.Game.minionsonBoard(3-self.ID)
		self.dealsAOE(targets, [damage for minion in targets])
		return None
		
"""Paladin Cards"""
class BlessingofMight(Spell):
	Class, name = "Paladin", "Blessing of Might"
	requireTarget, mana = True, 1
	index = "Basic~Paladin~Spell~1~Blessing of Might"
	description = "Give a minion +3 Attack"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if target != None:
			PRINT(self, "Blessing of Might gives minion %s +3 Attack."%target.name)
			target.buffDebuff(3, 0)
		return target
		
		
class HandofProtection(Spell):
	Class, name = "Paladin", "Hand of Protection"
	requireTarget, mana = True, 1
	index = "Basic~Paladin~Spell~1~Hand of Protection"
	description = "Give a minion Divine Shield"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if target != None:
			PRINT(self, "Hand of Protection gives %s Divine Shield."%target.name)
			target.getsKeyword("Divine Shield")
		return target
		
		
class Humility(Spell):
	Class, name = "Paladin", "Humility"
	requireTarget, mana = True, 1
	index = "Basic~Paladin~Spell~1~Humility"
	description = "Change a minion's Attack to 1"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if target != None:
			PRINT(self, "Humility sets minion %s's Attack to 1."%target.name)
			target.statReset(1, False)
		return target
		
		
class LightsJustice(Weapon):
	Class, name, description = "Paladin", "Light's Justice", ""
	mana, attack, durability = 1, 1, 4
	index = "Basic~Paladin~Weapon~1~1~4~Light's Justice"
	
	
class HolyLight(Spell):
	Class, name = "Paladin", "Holy Light"
	requireTarget, mana = True, 2
	index = "Basic~Paladin~Spell~2~Holy Light"
	description = "Restore 6 health"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if target != None:
			heal = 6 * (2 ** self.countHealDouble())
			PRINT(self, "Holy Light restores %d health to %s"%(heal, target.name))
			self.restoresHealth(target, heal)
		return target
		
		
class BlessingofKings(Spell):
	Class, name = "Paladin", "Blessing of Kings"
	requireTarget, mana = True, 4
	index = "Basic~Paladin~Spell~4~Blessing of Kings"
	description = "Give a minion +4/+4"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if target != None:
			PRINT(self, "Blessing of Kings gives %s +4/+4."%target.name)
			target.buffDebuff(4, 4)
		return target
		
		
class Consecration(Spell):
	Class, name = "Paladin", "Consecration"
	requireTarget, mana = False, 4
	index = "Basic~Paladin~Spell~4~Consecration"
	description = "Deal 2 damage to all enemies"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		damage = (2 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		targets = [self.Game.heroes[3-self.ID]] + self.Game.minionsonBoard(3-self.ID)
		PRINT(self, "Consecration deals %d damage to all enemies"%damage)
		self.dealsAOE(targets, [damage for obj in targets])
		return None
		
		
class HammerofWrath(Spell):
	Class, name = "Paladin", "Hammer of Wrath"
	requireTarget, mana = True, 4
	index = "Basic~Paladin~Spell~4~Hammer of Wrath"
	description = "Deal 3 damage. Draw a card"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if target != None:
			damage = (3 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			PRINT(self, "Hammer of Wrath deals %d damage to %s and freezes it. Then player draws a card."%(damage, target.name))
			self.dealsDamage(target, damage)
			self.Game.Hand_Deck.drawCard(self.ID)
		return target
		
		
class TruesilverChampion(Weapon):
	Class, name, description = "Paladin", "Truesilver Champion", "Whenever your hero attacks, restore 2 Health to it"
	mana, attack, durability = 4, 4, 2
	index = "Basic~Paladin~Weapon~4~4~2~Truesilver Champion"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_TruesilverChampion(self)]
		
class Trigger_TruesilverChampion(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["HeroAttackingMinion", "HeroAttackingHero"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return subject == self.entity.Game.heroes[self.entity.ID] and self.entity.onBoard
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		heal = 2 * (2 ** self.entity.countHealDouble())
		PRINT(self, "%s restores %d Health the hero when it attacks."%(self.entity.name, heal))
		self.entity.restoresHealth(self.entity.Game.heroes[self.entity.ID], heal)
		
		
class GuardianofKings(Minion):
	Class, race, name = "Paladin", "", "Guardian of Kings"
	mana, attack, health = 7, 5, 6
	index = "Basic~Paladin~Minion~7~5~6~None~Guardian of Kings~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Restore 6 health to your hero"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		heal = 6 * (2 ** self.countHealDouble())
		PRINT(self, "Guardian of Kings' battlecry restores %d health to player's hero."%heal)
		self.restoresHealth(self.Game.heroes[self.ID], heal)
		return None
		
"""Priest Cards"""
class PowerWordShield(Spell):
	Class, name = "Priest", "Power Word: Shield"
	requireTarget, mana = True, 0
	index = "Basic~Priest~Spell~0~Power Word: Shield"
	description = "Give a minion +2 Health"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if target != None:
			PRINT(self, "Power Word: Shield gives minion %s +2 health"%target.name)
			target.buffDebuff(0, 2)
		return target
		
		
class HolySmite(Spell):
	Class, name = "Priest", "Holy Smite"
	requireTarget, mana = True, 1
	index = "Basic~Priest~Spell~1~Holy Smite"
	description = "Deal 3 damage to a minion"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if target != None:
			damage = (3 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			PRINT(self, "Holy Smite deals %d damage to minion %s"%(damage, target.name))
			self.dealsDamage(target, damage)
		return target
		
		
class MindVision(Spell):
	Class, name = "Priest", "Mind Vision"
	requireTarget, mana = False, 1
	index = "Basic~Priest~Spell~1~Mind Vision"
	description = "Put a copy of a random card in your opponent's hand into your hand"
	def randomorDiscover(self):
		return "Random"
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if self.Game.Hand_Deck.handNotFull(self.ID) and self.Game.Hand_Deck.hands[3-self.ID] != []:
			PRINT(self, "Mind Vision copies a card from enemy hand")
			target = np.random.choice(self.Game.Hand_Deck.hands[3-self.ID])
			Copy = target.selfCopy(self.ID)
			self.Game.Hand_Deck.addCardtoHand(Copy, self.ID)
		return None
		
		
class PsychicConjurer(Minion):
	Class, race, name = "Priest", "", "Psychic Conjurer"
	mana, attack, health = 1, 1, 1
	index = "Basic~Priest~Minion~1~1~1~None~Psychic Conjurer-Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Copy a card in your opponent's deck and add it to your hand"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if self.Game.Hand_Deck.decks[3-self.ID] != []:
			PRINT(self, "Psychic Conjurer's battlecry puts a copy of a card from opponent's deck into player's hand")
			Copy = np.random.choice(self.Game.Hand_Deck.decks[3-self.ID]).selfCopy(self.ID)
			self.Game.Hand_Deck.addCardtoHand(Copy, self.ID)
		return None
		
		
class Radiance(Spell):
	Class, name = "Priest", "Radiance"
	requireTarget, mana = False, 1
	index = "Basic~Priest~Spell~1~Radiance"
	description = "Restore 5 health to your hero"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		heal = 5 * (2 ** self.countHealDouble())
		PRINT(self, "Radiance restores %d heal to hero"%heal)
		self.restoresHealth(self.Game.heroes[self.ID], heal)
		return None
		
		
class ShadowWordDeath(Spell):
	Class, name = "Priest", "Shadow Word: Death"
	requireTarget, mana = True, 2
	index = "Basic~Priest~Spell~2~Shadow Word: Death"
	description = "Destroy a minion with 5 or more Attack"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		if target.cardType == "Minion" and target.attack > 4 and target.onBoard:
			return True
		return False
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if target != None:
			if target.onBoard:
				PRINT(self, "Shadow Word: Death destroys minion %s with 3 or less Attack."%target.name)
				target.dead = True
			elif target.inHand: #Target in hand will be discarded.
				PRINT(self, "Shadow Word: Death discards the target %s returned to hand."%target.name)
				self.Game.Hand_Deck.discardCard(target.ID, target)
		return target
		
		
class ShadowWordPain(Spell):
	Class, name = "Priest", "Shadow Word: Pain"
	requireTarget, mana = True, 2
	index = "Basic~Priest~Spell~2~Shadow Word: Pain"
	description = "Destroy a minion with 3 or less Attack"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.attack < 4 and target.onBoard
		
	#Target after returned to hand will be discarded.
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if target != None:
			if target.onBoard:
				PRINT(self, "Shadow Word: Pain destroys minion %s with 3 or less Attack."%target.name)
				target.dead = True
			elif target.inHand: #Target in hand will be discarded.
				PRINT(self, "Shadow Word: Pain discards the target %s returned to hand."%target.name)
				self.Game.Hand_Deck.discardCard(target.ID, target)
		return target
		
		
class HolyNova(Spell):
	Class, name = "Priest", "Holy Nova"
	requireTarget, mana = False, 4
	index = "Basic~Priest~Spell~4~Holy Nova"
	description = "Deal 2 damage to all enemies. Restore 2 Health to all friendly characters"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		damage = (2 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		heal = 2 * (2 ** self.countHealDouble())
		enemies = [self.Game.heroes[3-self.ID]] + self.Game.minionsonBoard(3-self.ID)
		friendlies = [self.Game.heroes[self.ID]] + self.Game.minionsonBoard(self.ID)
		PRINT(self, "Holy Nova deals %d damage to all enemies and restores %d health to all friendlies."%(damage, heal))
		self.dealsAOE(enemies, [damage for obj in enemies])
		self.restoresAOE(friendlies, [heal for obj in friendlies])
		return None
		
		
class PowerInfusion(Spell):
	Class, name = "Priest", "Power Infusion"
	requireTarget, mana = True, 4
	index = "Basic~Priest~Spell~4~Power Infusion"
	description = "Give a minion +2/+6"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if target != None:
			PRINT(self, "Power Infusion gives minion %s +2/+6"%target.name)
			target.buffDebuff(2, 6)
		return target
		
		
class MindControl(Spell):
	Class, name = "Priest", "Mind Control"
	requireTarget, mana = True, 10
	index = "Basic~Priest~Spell~10~Mind Control"
	description = "Take control of an enemy minion"
	def available(self):
		return self.selectableEnemyMinionExists()
		
	def targetCorrect(self, target, choice=0):
		if target.cardType == "Minion" and target.ID != self.ID and target.onBoard:
			return True
		return False
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if target != None and target.ID != self.ID:
			PRINT(self, "Mind Control takes control of enemy minion %s"%target.name)
			self.Game.minionSwitchSide(target) #minionSwitchSide() will takes care of the case where minion is in hand
		return target
		
"""Rogue Cards"""
class Backstab(Spell):
	Class, name = "Rogue", "Backstab"
	requireTarget, mana = True, 0
	index = "Basic~Rogue~Spell~0~Backstab"
	description = "Deal 2 damage to an undamage minion"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.health == target.health_upper and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if target != None:
			damage = (2 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			PRINT(self, "Backstab deals %d damage to minion %s"%(damage, target.name))
			self.dealsDamage(target, damage)
		return target
		
		
class WickedKnife(Weapon):
	Class, name, description = "Rogue", "Wicked Knife", ""
	mana, attack, durability = 1, 1, 2
	index = "Basic~Rogue~Weapon~1~1~2~Wicked Knife~Uncollectible"
	
class PoisonedDagger(Weapon):
	Class, name, description = "Rogue", "Poisoned Dagger", ""
	mana, attack, durability = 1, 2, 2
	index = "Basic~Rogue~Weapon~1~2~2~Poisoned Dagger~Uncollectible"
	
	
class DeadlyPoison(Spell):
	Class, name = "Rogue", "Deadly Poison"
	requireTarget, mana = False, 1
	index = "Basic~Rogue~Spell~1~Deadly Poison"
	description = "Give your weapon +2 Attack"
	def available(self):
		if self.Game.availableWeapon(self.ID) == None:
			return False
		return True
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		weapon = self.Game.availableWeapon(self.ID)
		if weapon != None:
			PRINT(self, "Deadly Poison gives hero %d's weapon %s 2 Attack"%(self.ID, weapon.name))
			weapon.gainStat(2, 0)
		return None
		
		
class SinisterStrike(Spell):
	Class, name = "Rogue", "Sinister Strike"
	requireTarget, mana = False, 1
	index = "Basic~Rogue~Spell~1~Sinister Strike"
	description = "Deal 3 damage to the enemy hero"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		damage = (3 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		PRINT(self, "Sinister Strike deals %d damage to enemy hero"%damage)
		self.dealsDamage(self.Game.heroes[3-self.ID], damage)
		return None
		
		
class Sap(Spell):
	Class, name = "Rogue", "Sap"
	requireTarget, mana = True, 2
	index = "Basic~Rogue~Spell~2~Sap"
	description = "Return an enemy minion to your opponent's hand"
	def available(self):
		return self.selectableEnemyMinionExists()
		
	def targetCorrect(self, target, choice=0):
		if target.cardType == "Minion" and target.ID != self.ID and target.onBoard:
			return True
		return False
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if target != None:
			PRINT(self, "Sap returns enemy minion %s to its owner's hand."%target.name)
			self.Game.returnMiniontoHand(target)
		return target
		
		
class Shiv(Spell):
	Class, name = "Rogue", "Shiv"
	requireTarget, mana = True, 2
	index = "Basic~Rogue~Spell~2~Shiv"
	description = "Deal 1 damage. Draw a card"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if target != None:
			damage = (1 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			PRINT(self, "Shiv deals %d damage to target %s. Then player draws a card."%(damage, target.name))
			self.dealsDamage(target, damage)
		self.Game.Hand_Deck.drawCard(self.ID)
		return target
		
		
class FanofKnives(Spell):
	Class, name = "Rogue", "Fan of Knives"
	requireTarget, mana = False, 3
	index = "Basic~Rogue~Spell~3~Fan of Knives"
	description = "Deal 1 damage to all enemy minions. Draw a card"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		damage = (1 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		targets = self.Game.minionsonBoard(3-self.ID)
		PRINT(self, "Fan of Knives deals %d damage to all enemy minions."%damage)
		self.dealsAOE(targets, [damage for minion in targets])
		self.Game.Hand_Deck.drawCard(self.ID)
		return None
		
		
class Plaguebringer(Minion):
	Class, race, name = "Rogue", "", "Plaguebringer"
	mana, attack, health = 4, 3, 3
	index = "Basic~Rogue~Minion~4~3~3~None~Plaguebringer~Battlecry"
	requireTarget, keyWord, description = True, "", "Battlecry: Give a friendly Poisonous"
	
	def targetExists(self, choice=0):
		return self.selectableFriendlyMinionExists()
		
	def targetCorrect(self, target, choice=0):
		if target.cardType == "Minion" and target.ID == self.ID and target != self and target.onBoard:
			return True
		return False
		
	#Infer from Windfury: Target when in hand should be able to gets Poisonous and keep it next time it's played.
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if target != None:
			PRINT(self, "Plaguebringer's battlecry gives friendly minion %s Poisonous."%target.name)
			target.getsKeyword("Poisonous")
		return target
		
		
class Assassinate(Spell):
	Class, name = "Rogue", "Assassinate"
	requireTarget, mana = True, 5
	index = "Basic~Rogue~Spell~5~Assassinate"
	description = "Destroy an enemy minion"
	def available(self):
		return self.selectableEnemyMinionExists()
		
	def targetCorrect(self, target, choice=0):
		if target.cardType == "Minion" and target.ID != self.ID and target.onBoard:
			return True
		return False
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if target != None:
			PRINT(self, "Assassinate destroys enemy minion %s"%target.name)
			target.dead = True
		return target
		
		
class AssassinsBlade(Weapon):
	Class, name, description = "Rogue", "Assassin's Blade", ""
	mana, attack, durability = 5, 3, 4
	index = "Basic~Rogue~Weapon~5~3~4~Assassin's Blade"
	
	
class Sprint(Spell):
	Class, name = "Rogue", "Sprint"
	requireTarget, mana = False, 7
	index = "Basic~Rogue~Spell~7~Sprint"
	description = "Draw 4 cards"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		PRINT(self, "Sprint player draws 4 cards.")
		self.Game.Hand_Deck.drawCard(self.ID)
		self.Game.Hand_Deck.drawCard(self.ID)
		self.Game.Hand_Deck.drawCard(self.ID)
		self.Game.Hand_Deck.drawCard(self.ID)
		return None
		
"""Shaman Cards"""
class AncestralHealing(Spell):
	Class, name = "Shaman", "Ancestral Healing"
	requireTarget, mana = True, 0
	index = "Basic~Shaman~Spell~0~Ancestral Healing"
	description = "Restore a minion to full health and give it Taunt"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		if target.cardType == "Minion" and target.onBoard:
			return True
		return False
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if target != None:
			PRINT(self, "Ancestral Healing restores minion %s to its full health."%target.name)
			self.restoresHealth(target, target.health_upper)
		return target
		
		
class TotemicMight(Spell):
	Class, name = "Shaman", "Totemic Might"
	requireTarget, mana = False, 0
	index = "Basic~Shaman~Spell~0~Totemic Might"
	description = "Give you Totems +2 Health"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		PRINT(self, "Totemic Might gives all friendly totems +2 health")
		for minion in fixedList(self.Game.minionsonBoard(self.ID)):
			if "Totem" in minion.race:
				minion.buffDebuff(0, 2)
		return None
		
		
class FrostShock(Spell):
	Class, name = "Shaman", "Frost Shock"
	requireTarget, mana = True, 1
	index = "Basic~Shaman~Spell~1~Frost Shock"
	description = "Deal 1 damage to an enemy character and Freeze it"
	def available(self):
		return self.selectableEnemyExists()
		
	def targetCorrect(self, target, choice=0):
		if (target.cardType == "Minion" or target.cardType == "Hero") and target.ID != self.ID and target.onBoard:
			return True
		return False
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if target != None:
			damage = (1 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			PRINT(self, "Frost Shock deals %d damage to enemy %s. Then freezes it."%(damage, target.name))
			self.dealsDamage(target, damage)
			target.getsFrozen()
		return target
		
		
class RockbiterWeapon(Spell):
	Class, name = "Shaman", "Rockbiter Weapon"
	requireTarget, mana = True, 2
	index = "Basic~Shaman~Spell~2~Rockbiter Weapon"
	description = "Give a friendly character +3 Attack this turn"
	def available(self):
		return self.selectableFriendlyExists()
		
	def targetCorrect(self, target, choice=0):
		if (target.cardType == "Minion" or target.cardType == "Hero") and target.ID == self.ID and target.onBoard:
			return True
		return False
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if target != None:
			PRINT(self, "Rockbiter Weapon gives friendly %s +3 Attack this turn."%target.name)
			if target.cardType == "Hero":
				target.gainTempAttack(3)
			else:
				target.buffDebuff(3, 0, "EndofTurn")
		return target
		
		
class Windfury(Spell):
	Class, name = "Shaman", "Windfury"
	requireTarget, mana = True, 2
	index = "Basic~Shaman~Spell~2~Windfury"
	description = "Give a minion Windfury"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		if target.cardType == "Minion" and target.onBoard:
			return True
		return False
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if target != None:
			PRINT(self, "Windfury gives minion %s Windfury."%target.name)
			target.getsKeyword("Windfury")
		return target
		
		
class FlametongueTotem(Minion):
	Class, race, name = "Shaman", "Totem", "Flametongue Totem"
	mana, attack, health = 3, 0 ,3
	index = "Basic~Shaman~Minion~3~0~3~Totem~Flametongue Totem"
	requireTarget, keyWord, description = False, "", "Adjacent minions have +2 Attack"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.auras["Buff Aura"] = BuffAura_Dealer_Adjacent(self, None, 2, 0)
		
		
class Hex(Spell):
	Class, name = "Shaman", "Hex"
	requireTarget, mana = True, 4
	index = "Basic~Shaman~Spell~4~Hex"
	description = "Transform a minion into a 0/1 Frog with Taunt"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if target != None:
			PRINT(self, "Hex transforms minion %s into a 0/1 Frog with Taunt."%target.name)
			newMinion = Frog(self.Game, target.ID)
			self.Game.transform(target, newMinion)
			target = newMinion
		return target
		
class Frog(Minion):
	Class, race, name = "Neutral", "Beast", "Frog"
	mana, attack, health = 1, 0, 1
	index = "Basic~Neutral~Minion~1~0~1~Beast~Frog~Taunt~Uncollectible"
	requireTarget, keyWord, description = False, "Taunt", "Taunt"
	
	
class Windspeaker(Minion):
	Class, race, name = "Shaman", "", "Windspeaker"
	mana, attack, health = 4, 3, 3
	index = "Basic~Shaman~Minion~4~3~3~None~Windspeaker~Battlecry"
	requireTarget, keyWord, description = True, "", "Battlecry: Give a friendly minion Windfury"
	
	def targetExists(self, choice=0):
		return self.selectableFriendlyMinionExists()
		
	def targetCorrect(self, target, choice=0):
		if target.cardType == "Minion" and target.ID == self.ID and target != self and target.onBoard:
			return True
		return False
		
	#Gurubashi Berserker is returned to hand and then given Windfury. It still has Windfury when replayed.
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if target != None:
			PRINT(self, "Windspeaker's battlecry gives %s windfury"%target.name)
			target.getsKeyword("Windfury")
		return target
		
		
class Bloodlust(Spell):
	Class, name = "Shaman", "Bloodlust"
	requireTarget, mana = False, 5
	index = "Basic~Shaman~Spell~5~Bloodlust"
	description = "Give your minions +3 Attack this turn"
	def available(self):
		return self.Game.minionsonBoard(self.ID) != []
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		PRINT(self, "Bloodlust gives all friendly minions +3 Attack this turn.")
		for minion in fixedList(self.Game.minionsonBoard(self.ID)):
			minion.buffDebuff(3, 0, "EndofTurn")
		return None
		
		
class FireElemental(Minion):
	Class, race, name = "Shaman", "Elemental", "Fire Elemental"
	mana, attack, health = 6, 6, 5
	index = "Basic~Shaman~Minion~6~6~5~Elemental~Fire Elemental~Battlecry"
	requireTarget, keyWord, description = True, "", "Battlecry: Deal 3 damage"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if target != None:
			PRINT(self, "Fire Elemental's battlecry deals 3 damage to %s"%target.name)
			self.dealsDamage(target, 3)
		return target
		
"""Warlock Cards"""
class SacrificialPact(Spell):
	Class, name = "Warlock", "Sacrificial Pact"
	requireTarget, mana = True, 0
	index = "Basic~Warlock~Spell~0~Sacrificial Pact"
	description = "Destroy a Demon. Restore 5 health to you hero"
	def targetCorrect(self, target, choice=0):
		if target.cardType == "Minion" and "Demon" in target.race and target.onBoard:
			return True
		elif target.name == "Lord Jaraxxus":
			return True
		return False
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if target != None:
			heal = 5 * (2 ** self.countHealDouble())
			PRINT(self, "Sacrificial Pact destroys Demon %s. Then restores %d heal to player."%(target.name, heal))
			target.dead = True
			self.restoresHealth(self.Game.heroes[self.ID], heal)
		return target
		
		
class Corruption(Spell):
	Class, name = "Warlock", "Corruption"
	requireTarget, mana = True, 1
	index = "Basic~Warlock~Spell~1~Corruption"
	description = "Choose an enemy minion. At the start of your turn, destroy it"
	def available(self):
		return self.selectableEnemyMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.ID != self.ID and target.onBoard
		
	#Tested: Corruption won't have any effect on minions in hand. They won't be discarded nor marked after played.
	#The Corruption effect can be cleansed with Silence effect.
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if target != None and target.onBoard:
			PRINT(self, "Corruption chooses enemy minion %s to die at the start of player's next turn."%target.name)
			trigger = Trigger_Corruption(target)
			trigger.ID = self.ID
			target.triggersonBoard.append(trigger)
			trigger.connect()
		return target
		
class Trigger_Corruption(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["TurnStarts"])
		self.temp = True
		self.ID = 1
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and ID == self.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self, "At the start of player %d's turn, Corrupted minion %s dies."%(self.ID, self.entity.name))
		self.entity.dead = True
		self.disconnect()
		extractfrom(self, self.entity.triggersonBoard)
		
	def selfCopy(self, recipient):
		trigger = type(self)(recipient)
		trigger.ID = self.ID
		return trigger
		
class MortalCoil(Spell):
	Class, name = "Warlock", "Mortal Coil"
	requireTarget, mana = True, 1
	index = "Basic~Warlock~Spell~1~Mortal Coil"
	description = "Deal 1 damage to a minion. If that kills it, draw a card"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.onBoard
		
	#When cast by Archmage Vargoth, this spell can target minions with health <=0 and automatically meet the requirement of killing.
	#If the target minion dies before this spell takes effect, due to being killed by Violet Teacher/Knife Juggler, Mortal Coil still lets
	#player draw a card.
	#If the target is None due to Mayor Noggenfogger's randomization, nothing happens.
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if target != None:
			damage = (1 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			PRINT(self, "Mortal Coil deals %d damage to minion %s"%(damage, target.name))
			self.dealsDamage(target, damage)
			if target.health < 1 or target.dead:
				PRINT(self, "Mortal Coil kills the target and lets player draw a card.")
				self.Game.Hand_Deck.drawCard(self.ID)
		return target
		
		
class Soulfire(Spell):
	Class, name = "Warlock", "Soulfire"
	requireTarget, mana = True, 1
	index = "Basic~Warlock~Spell~1~Soulfire"
	description = "Deal 4 damage. Discard a random card"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if target != None:
			damage = (4 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			PRINT(self, "Soulfire deals %d damage to target %s. Then player discard a card."%(damage, target.name))
			self.dealsDamage(target, damage)
		self.Game.Hand_Deck.discardCard(self.ID)
		return target
		
		
class Voidwalker(Minion):
	Class, race, name = "Warlock", "Demon", "Voidwalker"
	mana, attack, health = 1, 1, 3
	index = "Basic~Warlock~Minion~1~1~3~Demon~Voidwalker~Taunt"
	requireTarget, keyWord, description = False, "Taunt", "Taunt"
	
	
class Felstalker(Minion):
	Class, race, name = "Warlock", "Demon", "Felstalker"
	mana, attack, health = 2, 4, 3
	index = "Basic~Warlock~Minion~2~4~3~Demon~Felstalker~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Discard a random card"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		PRINT(self, "Felstalker's battlecry discards a random card.")
		self.Game.Hand_Deck.discardCard(self.ID)
		return None
		
class DrainLife(Spell):
	Class, name = "Warlock", "Drain Life"
	requireTarget, mana = True, 3
	index = "Basic~Warlock~Spell~3~Drain Life"
	description = "Deal 2 damage. Restore 2 Health to your hero"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if target != None:
			damage = (2 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			PRINT(self, "Drain Life deals %d damage to %s"%(damage, target.name))
			self.dealsDamage(target, damage)
		heal = 2 * (2 ** self.countHealDouble())
		PRINT(self, "Drain Life restores %d Health to player."%heal)
		self.restoresHealth(self.Game.heroes[self.ID], heal)
		return target
		
		
class ShadowBolt(Spell):
	Class, name = "Warlock", "Shadow Bolt"
	requireTarget, mana = True, 3
	index = "Basic~Warlock~Spell~3~Shadow Bolt"
	description = "Deal 4 damage to a minion"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		if target.cardType == "Minion" and target.onBoard:
			return True
		return False
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if target != None:
			damage = (4 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			PRINT(self, "Shadow Bolt deals %d damage to minion %s"%(damage, target.name))
			self.dealsDamage(target, damage)
		return target
		
		
class Hellfire(Spell):
	Class, name = "Warlock", "Hellfire"
	requireTarget, mana = False, 4
	index = "Basic~Warlock~Spell~4~Hellfire"
	description = "Deal 3 damage to ALL characters"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		damage = (3 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		targets = [self.Game.heroes[1], self.Game.heroes[2]] + self.Game.minionsonBoard(1) + self.Game.minionsonBoard(2)
		PRINT(self, "Hellfire deals %d damage to all characters."%damage)
		self.dealsAOE(targets, [damage for obj in targets])
		return None
		
		
class DreadInfernal(Minion):
	Class, race, name = "Warlock", "Demon", "Dread Infernal"
	mana, attack, health = 6, 6, 6
	index = "Basic~Warlock~Minion~6~6~6~Demon~Dread Infernal~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Deal 1 damage to ALL other characters"
	
	#Will trigger: Returned to hand, killed, controlled by enemy.
	#Find all minions on board.
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		targets = [self.Game.heroes[1], self.Game.heroes[2]] + self.Game.minionsonBoard(1) + self.Game.minionsonBoard(2)
		extractfrom(self, targets)
		PRINT(self, "Dread Infernal's battlecry deals 1 damage to all other characters.")
		self.dealsAOE(targets, [1 for obj in targets])
		return None
		
"""Warrior Cards"""
class Whirlwind(Spell):
	Class, name = "Warrior", "Whirlwind"
	requireTarget, mana = False, 1
	index = "Basic~Warrior~Spell~1~Whirlwind"
	description = "Deal 1 damage to ALL minions"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		damage = (1 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		targets = self.Game.minionsonBoard(1) + self.Game.minionsonBoard(2)
		PRINT(self, "Whirlwind deals %d damage to all minions."%damage)
		self.dealsAOE(targets, [damage for minion in targets])
		return None
		
		
class Charge(Spell):
	Class, name = "Warrior", "Charge"
	requireTarget, mana = True, 1
	index = "Basic~Warrior~Spell~1~Charge"
	description = "Give a friendly minion Charge. It can't attack heroes this turn"
	def available(self):
		return self.selectableFriendlyMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.ID == self.ID and target.onBoard
		
	#This can't attack hero state doesn't count as enchantment.
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if target != None:
			PRINT(self, "Charge gives friendly minion %s Charge. But it can't attack heroes this turn."%target.name)
			target.getsKeyword("Charge")
			target.marks["Can't Attack Hero"] += 1
			trigger = Trigger_Charge(target)
			trigger.connect()
			target.triggersonBoard.append(trigger)
		return target
		
class Trigger_Charge(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["TurnEnds"])
		self.temp = True
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard #Even if the current turn is not minion's owner's turn
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self, "At the end of turn, minion %s can attack hero again."%self.entity.name)
		if self.entity.marks["Can't Attack Hero"] > 0:
			self.entity.marks["Can't Attack Hero"] -= 1
		self.disconnect()
		extractfrom(self, self.entity.triggersonBoard)
		
		
class Execute(Spell):
	Class, name = "Warrior", "Execute"
	requireTarget, mana = True, 2
	index = "Basic~Warrior~Spell~2~Execute"
	description = "Destroy a damaged enemy minion"
	def available(self):
		return self.selectableEnemyMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.ID != self.ID and target.health < target.health_upper and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if target != None:
			PRINT(self, "Execute destroys damaged minion %s"%target.name)
			target.dead = True
		return target
		
		
class Cleave(Spell):
	Class, name = "Warrior", "Cleave"
	requireTarget, mana = False, 2
	index = "Basic~Warrior~Spell~2~Cleave"
	description = "Deal 2 damage to two random enemy minions"
	def randomorDiscover(self):
		if len(self.Game.minionsonBoard(3-self.ID)) < 3:
			return "No RNG"
		return "Random"
		
	def available(self):
		return self.Game.minionsonBoard(3-self.ID) != []
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		damage = (2 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		minions = self.Game.minionsonBoard(3-self.ID)
		if len(minions) > 1:
			targets = np.random.choice(minions, 2, replace=False)
			PRINT(self, "Cleave deals {} damage to two random minions: {}".format(damage, targets))
			self.dealsAOE(targets, [damage, damage])
		elif len(minions) == 1:
			PRINT(self, "Cleave deals %d damage to minion %s"%(damage, minions[0].name))
			self.dealsDamage(minions[0], damage)
		return None
		
		
class HeroicStrike(Spell):
	Class, name = "Warrior", "Heroic Strike"
	requireTarget, mana = False, 2
	index = "Basic~Warrior~Spell~2~Heroic Strike"
	description = "Give your hero +4 Attack this turn"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		PRINT(self, "Heroic Strike gives hero +4 Attack.")
		self.Game.heroes[self.ID].gainTempAttack(4)
		return None
		
		
class FieryWarAxe(Weapon):
	Class, name, description = "Warrior", "Fiery War Axe", ""
	mana, attack, durability = 3, 3, 2
	index = "Basic~Warrior~Weapon~3~3~2~Fiery War Axe"
	
	
class ShieldBlock(Spell):
	Class, name = "Warrior", "Shield Block"
	requireTarget, mana = False, 3
	index = "Basic~Warrior~Spell~3~Shield Block"
	description = "Gain 5 Armor. Draw a card"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		PRINT(self, "Shield Block gives hero +5 armor.")
		self.Game.heroes[self.ID].gainsArmor(5)
		self.Game.Hand_Deck.drawCard(self.ID)
		return None
		
#Charge gained by enchantment and aura can also be buffed by this Aura.
class WarsongCommander(Minion):
	Class, race, name = "Warrior", "", "Warsong Commander"
	mana, attack, health = 3, 2, 3
	index = "Basic~Warrior~Minion~3~2~3~None~Warsong Commander"
	requireTarget, keyWord, description = False, "", "Your Charge minions have +1 Attack"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.auras["Buff Aura"] = WarsongCommander_Aura(self)
		
		
class KorkronElite(Minion):
	Class, race, name = "Warrior", "", "Kor'kron Elite"
	mana, attack, health = 4, 4, 3
	index = "Basic~Warrior~Minion~4~4~3~None~Kor'kron Elite~Charge"
	requireTarget, keyWord, description = False, "Charge", "Charge"
	
	
class ArcaniteReaper(Weapon):
	Class, name, description = "Warrior", "Arcanite Reaper", ""
	mana, attack, durability = 5, 5, 2
	index = "Basic~Warrior~Weapon~5~5~2~Arcanite Reaper"