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
	
"""Basic&Upgraded Hero Powers"""
#Steady Shot is defined in the CardTypes file as the vanilla Hero Power
class BallistaShot(HeroPower):
	name, needTarget = "Ballista Shot", False
	index = "Hunter-2-Hero Power-Ballista Shot"
	description = "Deal 3 damage to the enemy hero"
	def effect(self, target=None, choice=0):
		damage = (3 + self.Game.playerStatus[self.ID]["Temp Damage Boost"]) * (2 ** self.countDamageDouble())
		print("Hero Power Steady Shot deals %d damage to the enemy hero"%damage, self.Game.heroes[3-self.ID].name)
		self.dealsDamage(self.Game.heroes[3-self.ID], damage)
		return 0
		
class DaggerMastery(HeroPower):
	name, needTarget = "Dagger Mastery", False
	index = "Rogue-2-Hero Power-Dagger Mastery"
	description = "Equip a 1/2 Weapon"
	def effect(self, target=None, choice=0):
		print("Hero Power Dagger Mastery equips a 1/2 Wicked Knife for player")
		self.Game.equipWeapon(WickedKnife(self.Game, self.ID))
		return 0
		
class PoisonedDaggers(HeroPower):
	name, needTarget = "Poisoned Daggers", False
	index = "Rogue-2-Hero Power-Poisoned Daggers"
	description = "Equip a 2/2 Weapon"
	def effect(self, target=None, choice=0):
		print("Hero Power Poisoned Daggers equips a 2/2 Poisoned Dagger for player")
		self.Game.heroes[self.ID].equipsWeapon(PoisonedDagger(self.Game, self.ID))
		return 0
		
class LifeTap(HeroPower):
	name, needTarget = "Life Tap", False
	index = "Warlock-2-Hero Power-Life Tap"
	description = "Deal 2 damage to your hero. Draw a card"
	def effect(self, target=None, choice=0):
		damage = (2 + self.Game.playerStatus[self.ID]["Temp Damage Boost"]) * (2 ** self.countDamageDouble())
		print("Hero Power Life Tap deals %d damage to player and lets player draw a card")
		self.dealsDamage(self.Game.heroes[self.ID], damage)
		card, mana = self.Game.Hand_Deck.drawCard(self.ID)
		if card != None:
			self.Game.sendSignal("CardDrawnfromHeroPower", self.ID, self, card, mana, "")
		return 0
		
class SoulTap(HeroPower):
	name, needTarget = "Soul Tap", False
	index = "Warlock-2-Hero Power-Soul Tap"
	description = "Draw a card"
	def effect(self, target=None, choice=0):
		print("Hero Power Soul Tap lets player draw a card")
		card, mana = self.Game.Hand_Deck.drawCard(self.ID)
		if card != None:
			self.Game.sendSignal("CardDrawnfromHeroPower", self.ID, self, card, mana, "")
		return 0
		
class Shapeshift(HeroPower):
	name, needTarget = "Shapeshift", False
	index = "Druid-2-Hero Power-Shapeshift"
	description = "Gain 1 Armor and 1 Attack this turn"
	def effect(self, target=None, choice=0):
		print("Hero Power Shapeshift gives lets player gain 1 Armor and 1 Attack this turn")
		self.Game.heroes[self.ID].gainsArmor(1)
		self.Game.heroes[self.ID].gainTempAttack(1)
		return 0
		
class DireShapeshift(HeroPower):
	name, needTarget = "Dire Shapeshift", False
	index = "Druid-2-Hero Power-Dire Shapeshift"
	description = "Gain 2 Armor and 2 Attack this turn"
	def effect(self, target=None, choice=0):
		print("Hero Power Dire Shapeshift gives lets player gain 2 Armor and 2 Attack this turn")
		self.Game.heroes[self.ID].gainsArmor(2)
		self.Game.heroes[self.ID].gainTempAttack(2)
		return 0
		
class ArmorUp(HeroPower):
	name, needTarget = "Armor Up!", False
	index = "Warrior-2-Hero Power-Armor Up!"
	description = "Gain 2 Armor"
	def effect(self, target=None, choice=0):
		print("Hero Armor Up! lets player gain 2 Armor")
		self.Game.heroes[self.ID].gainsArmor(2)
		return 0
		
class TankUp(HeroPower):
	name, needTarget = "Tank Up!", False
	index = "Warrior-2-Hero Power-Tank Up!"
	description = "Gain 4 Armor"
	def effect(self, target=None, choice=0):
		print("Hero Armor Up! lets player gain 2 Armor")
		self.Game.heroes[self.ID].gainsArmor(4)
		return 0
		
class Reinforce(HeroPower):
	name, needTarget = "Reinforce", False
	index = "Paladin-2-Hero Power-Reinforce"
	description = "Summon a 1/1 Silver Hand Recruit"
	def available(self, choice=0):
		if self.heroPowerTimes >= self.heroPowerChances_base + self.heroPowerChances_extra:
			return False
		if self.Game.spaceonBoard(self.ID) < 1:
			return False
		return True
		
	def effect(self, target=None, choice=0):
		#Hero Power summoning won't be doubled by Khadgar.
		print("Hero Power Reinforce summons a 1/1 Silver Hand Recruit")
		self.Game.summonMinion(SilverHandRecruit(self.Game, self.ID), -1, self.ID, "")
		return 0
		
class TheSilverHand(HeroPower):
	name, needTarget = "The Silver Hand", False
	index = "Paladin-2-Hero Power-The Silver Hand"
	description = "Summon two 1/1 Silver Hand Recruits"
	def available(self, choice=0):
		if self.heroPowerTimes >= self.heroPowerChances_base + self.heroPowerChances_extra:
			return False
		if self.Game.spaceonBoard(self.ID) < 1:
			return False
		return True
		
	def effect(self, target=None, choice=0):
		print("Hero Power The Silver Hand summons two 1/1 Silver Hand Recruits")
		self.Game.summonMinion([SilverHandRecruit(self.Game, self.ID) for i in range(2)], (-1, "totheRightEnd"), self.ID, "")
		return 0
		
class TotemicCall(HeroPower):
	name, needTarget = "Totemic Call", False
	index = "Shaman-2-Hero Power-Totemic Call"
	description = "Summon a random totem"
	def available(self, choice=0):
		if self.heroPowerTimes >= self.heroPowerChances_base + self.heroPowerChances_extra:
			return False
		if self.Game.spaceonBoard(self.ID) < 1 or self.viableTotems() == []:
			return False
		return True
		
	def effect(self, target=None, choice=0):
		viableTotems = list(self.viableTotems().values())
		print("Hero Power Totemic Call summons a random Basic Totem")
		self.Game.summonMinion(np.random.choice(viableTotems)(self.Game, self.ID), -1, self.ID, "")
		return 0
		
	def viableTotems(self):
		viableBasicTotems = {"Basic-Shaman-1-1-1-Minion-Totem-Searing Totem-Uncollectible": SearingTotem,
							"Basic-Shaman-1-0-2-Minion-Totem-Stoneclaw Totem-Taunt-Uncollectible": StoneclawTotem,
							"Basic-Shaman-1-0-2-Minion-Totem-Healing Totem-Uncollectible": HealingTotem,
							"Basic-Shaman-1-0-2-Minion-Totem-Wrath of Air Totem-Spell Damage-Uncollectible": WrathofAirTotem
							}
		for minion in self.Game.minionsonBoard(self.ID):
			if minion.index in viableBasicTotems:
				del viableBasicTotems[minion.index]
				
		return viableBasicTotems
		
class TotemicSlam(HeroPower):
	name, needTarget = "Totemic Slam", False
	index = "Shaman-2-Hero Power-Totemic Call"
	description = "Summon a totem of your choice"
	def available(self, choice=0):
		if self.heroPowerTimes >= self.heroPowerChances_base + self.heroPowerChances_extra:
			return False
		if self.Game.spaceonBoard(self.ID) < 1:
			return False
		return True
		
	def effect(self, target=None, choice=0):
		self.Game.options = [SearingTotem(self.Game, self.ID), StoneclawTotem(self.Game, self.ID),
							HealingTotem(self.Game, self.ID), WrathofAirTotem(self.Game, self.ID)]
		print("Hero Power Totemic Slam starts the discover for a basic totem to summon.")
		self.Game.DiscoverHandler.startDiscover(self)
		return 0
		
	def discoverDecided(self, option):
		print("Hero Power Totemic Slam summons totem", target.name)
		self.Game.summonMinion(option, -1, self.ID, "")
		
class Fireblast(HeroPower):
	name, needTarget = "Fireblast", True
	index = "Mage-2-Hero Power-Fireblast"
	description = "Deal 1 damage"
	def effect(self, target, choice=0):
		damage = (1 + self.Game.playerStatus[self.ID]["Temp Damage Boost"]) * (2 ** self.countDamageDouble())
		print("Hero Power Fireblast deals %d damage to"%damage, target.name)
		objtoTakeDamage, targetSurvival = self.dealsDamage(target, damage)
		if targetSurvival > 1:
			return 1
		return 0
		
class FireblastRank2(HeroPower):
	name, needTarget = "Fireblast Rank 2", True
	index = "Mage-2-Hero Power-Fireblast Rank 2"
	description = "Deal 2 damage"
	def effect(self, target, choice=0):
		damage = (2 + self.Game.playerStatus[self.ID]["Temp Damage Boost"]) * (2 ** self.countDamageDouble())
		print("Hero Power Fireblast Rank 2 deals %d damage to"%damage, target.name)
		objtoTakeDamage, targetSurvival = self.dealsDamage(target, damage)
		if targetSurvival > 1:
			return 1
		return 0
		
class LesserHeal(HeroPower):
	name, needTarget = "Lesser Heal", True
	index = "Priest-2-Hero Power-Lesser Heal"
	description = "Restore 2 health"
	def effect(self, target, choice=0):
		heal = 2 * (2 ** self.countHealDouble())
		print("Hero Power Lesser Heal restores %d Health to"%heal, target.name)
		obj, targetSurvival = self.restoresHealth(target, heal)
		if targetSurvival > 1:
			return 1
		return 0
		
class Heal(HeroPower):
	name, needTarget = "Heal", True
	index = "Priest-2-Hero Power-Heal"
	description = "Restore 4 health"
	def effect(self, target, choice=0):
		heal = 4 * (2 ** self.countHealDouble())
		print("Hero Power Heal restores %d Health to"%heal, target.name)
		obj, targetSurvival = self.restoresHealth(target, heal)
		if targetSurvival > 1:
			return 1
		return 0
		
		
"""Basic Heroes"""
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
	

"""Mana 0 cards"""
class TheCoin(Spell):
	Class, name = "Neutral", "The Coin"
	needTarget, mana = False, 0
	index = "Basic-Neutral-0-Spell-The Coin-Uncollectible"
	description = "Gain 1 mana crystal for this turn."
	def whenEffective(self, target=None, comment="", choice=0):
		print("The Coin is cast and lets hero gain a mana this turn.")
		if self.Game.ManaHandler.manas[self.ID] < 10:
			self.Game.ManaHandler.manas[self.ID] += 1
		return None
		
"""mana 1 minions"""
class ElvenArcher(Minion):
	Class, race, name = "Neutral", "", "Elven Archer"
	mana, attack, health = 1, 1, 1
	index = "Basic-Neutral-1-1-1-Minion-None-Elven Archer-Battlecry"
	needTarget, keyWord, description = True, "", "Deal 1 damamge"
	#Dealing damage to minions not on board(moved to grave and returned to deck) won't have any effect.
	#Dealing damage to minions in hand will trigger Frothing Berserker, but that minion will trigger its own damage taken response.
	#When the minion in hand takes damage, at the moment it's replayed, the health will be reset even if it's reduced to below 0.
	#If this is killed before battlecry, will still deal damage.
	#If this is returned to hand before battlecry, will still deal damage.
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			print("Elven Archer's battlecry deals 1 damage to ", target.name)
			self.dealsDamage(target, 1) #dealsDamage() on targets in grave/deck will simply pass.
		return self, target
		
		
class GoldshireFootman(Minion):
	Class, race, name = "Neutral", "", "Goldshire Footman"
	mana, attack, health = 1, 1, 2
	index = "Basic-Neutral-1-1-2-Minion-None-Goldshire Footman-Taunt"
	needTarget, keyWord, description = False, "Taunt", "Taunt"
	
	
class GrimscaleOracle(Minion):
	Class, race, name = "Neutral", "Murloc", "Grimscale Oracle"
	mana, attack, health = 1, 1, 1
	index = "Basic-Neutral-1-1-1-Minion-Murloc-Grimscale Oracle"
	needTarget, keyWord, description = False, "", "Give your other Murlocs +1/+1"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.auras["Buff Aura"] = BuffAura_Dealer_All(self, self.applicable, 1, 0)
		
	def applicable(self, target):
		if "Murloc" in target.race:
			return True
		return False
		
		
class MurlocRaider(Minion):
	Class, race, name = "Neutral", "Murloc", "Murloc Raider"
	mana, attack, health = 1, 2, 1
	index = "Basic-Neutral-1-2-1-Minion-Murloc-Murloc Raider"
	needTarget, keyWord, description = False, "", ""
	
	
class StonetuskBoar(Minion):
	Class, race, name = "Neutral", "Beast", "Stonetusk Boar"
	mana, attack, health = 1, 1, 1
	index = "Basic-Neutral-1-1-1-Minion-Beast-Stonetusk Boar-Charge"
	needTarget, keyWord, description = False, "Charge", "Charge"
	
	
class VoodooDoctor(Minion):
	Class, race, name = "Neutral", "", "Voodoo Doctor"
	mana, attack, health = 1, 2, 1
	index = "Basic-Neutral-1-2-1-Minion-None-Voodoo Doctor-Battlecry"
	needTarget, keyWord, description = True, "", "Restore 2 health"
	
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			heal = 2 * (2 ** self.countHealDouble())
			print("Voodoo Doctor's battlecry restores %d health to"%heal, target.name)
			self.restoresHealth(target, heal)
		return self, target
		
		
class SilverHandRecruit(Minion):
	Class, race, name = "Paladin", "", "Silver Hand Recruit"
	mana, attack, health = 1, 1, 1
	index = "Basic-Paladin-1-1-1-Minion-None-Silver Hand Recruit-Uncollectible"
	needTarget, keyWord, description = False, "", ""
	
	
class SearingTotem(Minion):
	Class, race, name = "Shaman", "Totem", "Searing Totem"
	mana, attack, health = 1, 1, 1
	index = "Basic-Shaman-1-1-1-Minion-Totem-Searing Totem-Uncollectible"
	needTarget, keyWord, description = False, "", ""
	
class StoneclawTotem(Minion):
	Class, race, name = "Shaman", "Totem", "Stoneclaw Totem"
	mana, attack, health = 1, 0, 2
	index = "Basic-Shaman-1-0-2-Minion-Totem-Stoneclaw Totem-Taunt-Uncollectible"
	needTarget, keyWord, description = False, "Taunt", "Taunt"
	
class HealingTotem(Minion):
	Class, race, name = "Shaman", "Totem", "Healing Totem"
	mana, attack, health = 1, 0, 2
	index = "Basic-Shaman-1-0-2-Minion-Totem-Healing Totem-Uncollectible"
	needTarget, keyWord, description = False, "", "At the end of your turn, restore 1 health to all friendly minions"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_HealingTotem(self)]
		
class Trigger_HealingTotem(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["TurnEnds"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		if self.entity.onBoard and ID == self.entity.ID:
			return True
		return False
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("At the end of turn, %s restores 1 health to all friendly minions."%self.entity.name)
		heal = 1 * (2 ** self.entity.countHealDouble())
		targets_Heal = self.entity.Game.minionsonBoard(self.entity.ID)
		self.entity.dealsAOE([], [], targets_Heal, [heal for minion in targets_Heal])
		
		
class WrathofAirTotem(Minion):
	Class, race, name = "Shaman", "Totem", "Wrath of Air Totem"
	mana, attack, health = 1, 0, 2
	index = "Basic-Shaman-1-0-2-Minion-Totem-Wrath of Air Totem-Spell Damage-Uncollectible"
	needTarget, keyWord, description = False, "Spell Damage", "Spell Damage +1"#Default Spell Damage is 1.
	
"""Mana 2 minions"""
class AcidicSwampOoze(Minion):
	Class, race, name = "Neutral", "", "Acidic Swamp Ooze"
	mana, attack, health = 2, 3, 2
	index = "Basic-Neutral-2-3-2-Minion-None-Acidic Swamp Ooze-Battlecry"
	needTarget, keyWord, description = False, "", "Battlecry: Destroy you opponent's weapon"
	
	def whenEffective(self, target=None, comment="", choice=0):
		print("Acidic Swamp Ooze's battlecry destroys enemy weapon")
		for weapon in self.Game.weapons[3-self.ID]:
			weapon.destroyed()
		return self, None
		
		
class BloodfenRaptor(Minion):
	Class, race, name = "Neutral", "Beast", "Bloodfen Raptor"
	mana, attack, health = 2, 3, 2
	index = "Basic-Neutral-2-3-2-Minion-Beast-Bloodfen Raptor"
	needTarget, keyWord, description = False, "", ""
	
	
class BluegillWarrior(Minion):
	Class, race, name = "Neutral", "Murloc", "Bluegill Warrior"
	mana, attack, health = 2, 2, 1
	index = "Basic-Neutral-2-2-1-Minion-Murloc-Bluegill Warrior-Charge"
	needTarget, keyWord, description = False, "Charge", "Charge"
	
	
class FrostwolfGrunt(Minion):
	Class, race, name = "Neutral", "", "Frostwolf Grunt"
	mana, attack, health = 2, 2, 2
	index = "Basic-Neutral-2-2-2-Minion-None-Frostwolf Grunt-Taunt"
	needTarget, keyWord, description = False, "Taunt", "Taunt"
	
	
class KoboldGeomancer(Minion):
	Class, race, name = "Neutral", "", "Kobold Geomancer"
	mana, attack, health = 2, 2, 2
	index = "Basic-Neutral-2-2-2-Minion-None-Kobold Geomancer-Spell Damage"
	needTarget, keyWord, description = False, "Spell Damage", "Spell Damage +1"
	
	
class MurlocTidehunter(Minion):
	Class, race, name = "Neutral", "Murloc", "Murloc Tidehunter"
	mana, attack, health = 2, 2, 1
	index = "Basic-Neutral-2-2-1-Minion-Murloc-Murloc Tidehunter-Battlecry"
	needTarget, keyWord, description = False, "", "Battlecry: Summon a 1/1 Murloc Scout"
	#If controlled by enemy, will summon for enemy instead.
	def whenEffective(self, target=None, comment="", choice=0):
		print("Murloc Tidehunter's battlecry summons a 1/1 Murloc Scout")
		self.Game.summonMinion(MurlocScout(self.Game, self.ID), self.position+1, self.ID)
		return self, None
		
class MurlocScout(Minion):
	Class, race, name = "Neutral", "Murloc", "Murloc Scout"
	mana, attack, health = 1, 1, 1
	index = "Basic-Neutral-1-1-1-Minion-Murloc-Murloc Scout-Uncollectible"
	needTarget, keyWord, description = False, "", ""
	
	
class NoviceEngineer(Minion):
	Class, race, name = "Neutral", "", "Novice Engineer"
	mana, attack, health = 2, 1, 1
	index = "Basic-Neutral-2-1-1-Minion-None-Novice Engineer-Battlecry"
	needTarget, keyWord, description = False, "", "Battlecry: Draw a card"
	#Whatever happens Novice Engineer, card-drawing battlecry can still take effect.
	def whenEffective(self, target=None, comment="", choice=0):
		print("Novice Engineer's battlecry lets player draw a card.")
		self.Game.Hand_Deck.drawCard(self.ID)
		return self, None
		
		
class RiverCrocolisk(Minion):
	Class, race, name = "Neutral", "Beast", "River Crocolisk"
	mana, attack, health = 2, 2, 3
	index = "Basic-Neutral-2-2-3-Minion-Beast-River Crocolisk"
	needTarget, keyWord, description = False, "", ""
	
"""Mana 3 minions"""		
class DalaranMage(Minion):
	Class, race, name = "Neutral", "", "Dalaran Mage"
	mana, attack, health = 3, 1, 4
	index = "Basic-Neutral-3-1-4-Minion-None-Dalaran Mage-Spell Damage"
	needTarget, keyWord, description = False, "Spell Damage", "Spell Damage +1"
	
	
class IronforgeRifleman(Minion):
	Class, race, name = "Neutral", "", "Ironforge Rifleman"
	mana, attack, health = 3, 2, 2
	index = "Basic-Neutral-3-2-2-Minion-None-Ironforge Rifleman-Battlecry"
	needTarget, keyWord, description = True, "", "Battlecry: Deal 1 damage"
	
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			print("Ironforge Rifleman's battlecry deals 1 damage to ", target.name)
			self.dealsDamage(target, 1)
		return self, target
		
		
class IronfurGrizzly(Minion):
	Class, race, name = "Neutral", "Beast", "Ironfur Grizzly"
	mana, attack, health = 3, 3, 3
	index = "Basic-Neutral-3-3-3-Minion-Beast-Ironfur Grizzly-Taunt"
	needTarget, keyWord, description = False, "Taunt", "Taunt"
	
	
class MagmaRager(Minion):
	Class, race, name = "Neutral", "Elemental", "Magma Rager"
	mana, attack, health = 3, 5, 1
	index = "Basic-Neutral-3-5-1-Minion-Elemental-Magma Rager"
	needTarget, keyWord, description = False, "", ""
	
	
class RaidLeader(Minion):
	Class, race, name = "Neutral", "", "Raid Leader"
	mana, attack, health = 3, 2, 2
	index = "Basic-Neutral-3-2-2-Minion-None-Raid Leader"
	needTarget, keyWord, description = False, "", "Your other minions have +1 Attack"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.auras["Buff Aura"] = BuffAura_Dealer_All(self, None, 1, 0)
		
		
class RazorfenHunter(Minion):
	Class, race, name = "Neutral", "", "Razorfen Hunter"
	mana, attack, health = 3, 2, 3
	index = "Basic-Neutral-3-2-3-Minion-None-Razorfen Hunter-Battlecry"
	needTarget, keyWord, description = False, "", "Battlecry: Summon a 1/1 Boar"
	
	#Infer from Dragonling Mechanic.
	def whenEffective(self, target=None, comment="", choice=0):
		print("Razorfen Hunter's batlecry summons a 1/1 Boar.")
		self.Game.summonMinion(Boar(self.Game, self.ID), self.position+1, self.ID)
		return self, None
		
class Boar(Minion):
	Class, race, name = "Neutral", "Beast", "Boar"
	mana, attack, health = 1, 1, 1
	index = "Basic-Neutral-1-1-1-Minion-Beast-Boar-Uncollectible"
	needTarget, keyWord, description = False, "", ""
	
	
class ShatteredSunCleric(Minion):
	Class, race, name = "Neutral", "", "Shattered Sun Cleric"
	mana, attack, health = 3, 3, 2
	index = "Basic-Neutral-3-3-2-Minion-None-Shattered Sun Cleric-Battlecry"
	needTarget, keyWord, description = True, "", "Battlecry: Give friendly minion +1/+1"
	
	def targetExists(self, choice=0):
		return self.selectableFriendlyMinionExists()
		
	def targetCorrect(self, target, choice=0):
		if target.cardType == "Minion" and target.ID == self.ID and target.onBoard and target != self:
			return True
		return False
		
	#Infer from Houndmaster: Buff can apply on targets on board, in hand, in deck.
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None and (target.onBoard or target.inDeck or target.inHand):
			print("Shattered Sun Cleric's battlecry gives friendly minion %s +1/+1."%target.name)
			target.buffDebuff(1, 1)
		return self, target
		
		
class SilverbackPatriarch(Minion):
	Class, race, name = "Neutral", "Beast", "Silverback Patriarch"
	mana, attack, health = 3, 1, 4
	index = "Basic-Neutral-3-1-4-Minion-Beast-Silverback Patriarch-Taunt"
	needTarget, keyWord, description = False, "Taunt", "Taunt"
	
	
class Wolfrider(Minion):
	Class, race, name = "Neutral", "", "Wolfrider"
	mana, attack, health = 3, 3, 1
	index = "Basic-Neutral-3-3-1-Minion-None-Wolfrider-Charge"
	needTarget, keyWord, description = False, "Charge", "Charge"
	
"""Mana 4 minions"""
class ChillwindYeti(Minion):
	Class, race, name = "Neutral", "", "Chillwind Yeti"
	mana, attack, health = 4, 4, 5
	index = "Basic-Neutral-4-4-5-Minion-None-Chillwind Yeti"
	needTarget, keyWord, description = False, "", ""
	
	
class DragonlingMechanic(Minion):
	Class, race, name = "Neutral", "", "Dragonling Mechanic"
	mana, attack, health = 4, 2, 4
	index = "Basic-Neutral-4-2-4-Minion-None-Dragonling Mechanic-Battlecry"
	needTarget, keyWord, description = False, "", "Battlecry: Summon a 2/1 Mechanical Dragonling"
	
	#If returned to hand, will summon to the rightend of the board.
	def whenEffective(self, target=None, comment="", choice=0):
		print("Dragonling Mechanic's battlecry summons a 2/1 Mechanical Dragonling.")
		self.Game.summonMinion(MechanicDragonling(self.Game, self.ID), self.position+1, self.ID)
		return self, None
		
class MechanicalDragonling(Minion):
	Class, race, name = "Neutral", "Mech", "Dragonling Mechanic"
	mana, attack, health = 1, 2, 1
	index = "Basic-Neutral-1-2-1-Minion-Mech-Mechanical Dragonling-Uncollectible"
	needTarget, keyWord, description = False, "", ""
	
	
class GnomishInventor(Minion):
	Class, race, name = "Neutral", "", "Gnomish Inventor"
	mana, attack, health = 4, 2, 4
	index = "Basic-Neutral-4-2-4-Minion-None-Gnomish Inventor-Battlecry"
	needTarget, keyWord, description = False, "", "Battlecry: Draw a card"
	
	def whenEffective(self, target=None, comment="", choice=0):
		print("Gnomish Inventor's battlecry lets player draw a card.")
		self.Game.Hand_Deck.drawCard(self.ID)
		return self, None
		
		
class OasisSnapjaw(Minion):
	Class, race, name = "Neutral", "Beast", "Oasis Snapjaw"
	mana, attack, health = 4, 2, 7
	index = "Basic-Neutral-4-2-7-Minion-Beast-Oasis Snapjaw"
	needTarget, keyWord, description = False, "", ""
	
	
class OgreMagi(Minion):
	Class, race, name = "Neutral", "", "Ogre Magi"
	mana, attack, health = 4, 4, 4
	index = "Basic-Neutral-4-4-4-Minion-None-Ogre Magi-Spell Damage"
	needTarget, keyWord, description = False, "Spell Damage", "Spell Damage +1"
	
	
class SenjinShieldmasta(Minion):
	Class, race, name = "Neutral", "", "Sen'jin Shieldmasta"
	mana, attack, health = 4, 3, 5
	index = "Basic-Neutral-4-3-5-Minion-None-Sen'jin Shieldmasta-Taunt"
	needTarget, keyWord, description = False, "Taunt", "Taunt"
	
	
class StormwindKnight(Minion):
	Class, race, name = "Neutral", "", "Stormwind Knight"
	mana, attack, health = 4, 2, 5
	index = "Basic-Neutral-4-2-5-Minion-None-Stormwind Knight-Charge"
	needTarget, keyWord, description = False, "Charge", "Charge"
	
"""Mana 5 minions"""
class BootyBayBodyguard(Minion):
	Class, race, name = "Neutral", "", "Booty Bay Bodyguard"
	mana, attack, health = 5, 5, 4
	index = "Basic-Neutral-5-5-4-Minion-None-Booty Bay Bodyguard-Taunt"
	needTarget, keyWord, description = False, "Taunt", "Taunt"
	
	
class DarkscaleHealer(Minion):
	Class, race, name = "Neutral", "", "Darkscale Healer"
	mana, attack, health = 5, 4, 5
	index = "Basic-Neutral-5-4-5-Minion-None-Darkscale Healer-Battlecry"
	needTarget, keyWord, description = False, "", "Battlecry: Restore 2 health to all friendly characters"
	
	def whenEffective(self, target=None, comment="", choice=0):
		heal = 2 * (2 ** self.countHealDouble())
		targets = [self.Game.heroes[self.ID]] + self.Game.minionsonBoard(self.ID)
		print("Darkscale Healer's battlecry restores %d health to all friendly characters."%heal)
		self.dealsAOE([], [], targets, [heal for obj in targets])
		return self, None
		
		
class FrostwolfWarlord(Minion):
	Class, race, name = "Neutral", "", "Frostwolf Warlord"
	mana, attack, health = 5, 4, 4
	index = "Basic-Neutral-5-4-4-Minion-None-Frostwolf Warlord-Battlecry"
	needTarget, keyWord, description = False, "", "Battlecry: Gain +1/+1 for each other friendly minion on the battlefield"
	
	#For self buffing effects, being dead and removed before battlecry will prevent the battlecry resolution.
	#If this minion is returned hand before battlecry, it can still buff it self according to living friendly minions.
	def whenEffective(self, target=None, comment="", choice=0):
		if self.onBoard or self.inHand: #For now, no battlecry resolution shuffles this into deck.
			numOtherFriendlyMinions = 0
			for minion in self.Game.minionsonBoard(self.ID):
				if minion != self:
					numOtherFriendlyMinions += 1
					
			print("Frostwolf Warlord's battlecry gives minion +1/+1 for each other friendly minion.")
			self.buffDebuff(numOtherFriendlyMinions, numOtherFriendlyMinions)
		return self, None
		
#When takes damage in hand(Illidan/Juggler/Anub'ar Ambusher), won't trigger the +3 Attack buff.
class GurubashiBerserker(Minion):
	Class, race, name = "Neutral", "", "Gurubashi Berserker"
	mana, attack, health = 5, 2, 7
	index = "Basic-Neutral-5-2-7-Minion-None-Gurubashi Berserker"
	needTarget, keyWord, description = False, "", "Whenever this minion takes damage, gain +3 Attack"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_GurubashiBerserker(self)]
		
class Trigger_GurubashiBerserker(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionTakesDamage"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return target == self.entity and self.entity.onBoard
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print(self.entity.name, "takes Damage and gains +3 Attack.")
		self.entity.buffDebuff(3, 0)
		
		
class Nightblade(Minion):
	Class, race, name = "Neutral", "", "Nightblade"
	mana, attack, health = 5, 4, 4
	index = "Basic-Neutral-5-4-4-Minion-None-Nightblade-Battlecry"
	needTarget, keyWord, description = False, "", "Battlecry: Deal 3 damage to the enemy hero"
	
	def whenEffective(self, target=None, comment="", choice=0):
		print("Nightblade's battlecry deals 3 damage to the enemy hero.")
		self.dealsDamage(self.Game.heroes[3-self.ID], 3)
		return self, None
		
		
class StormpikeCommando(Minion):
	Class, race, name = "Neutral", "", "Stormpike Commando"
	mana, attack, health = 5, 4, 2
	index = "Basic-Neutral-5-4-2-Minion-None-Stormpike Commando-Battlecry"
	needTarget, keyWord, description = True, "", "Battlecry: Deal 2 damage"
	#Infer from Fire Plume Phoenix
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			print("Stormpike Commando's battlecry deals 2 damage to ", target.name)
			self.dealsDamage(target, 2)
		return self, target
		
"""Mana 6 minions"""
class LordoftheArena(Minion):
	Class, race, name = "Neutral", "", "Lord of the Arena"
	mana, attack, health = 6, 6, 5
	index = "Basic-Neutral-6-6-5-Minion-None-Lord of the Arena-Taunt"
	needTarget, keyWord, description = False, "Taunt", "Taunt"
	
	
class Archmage(Minion):
	Class, race, name = "Neutral", "", "Archmage"
	mana, attack, health = 6, 4, 7
	index = "Basic-Neutral-6-4-7-Minion-None-Archmage-Spell Damage"
	needTarget, keyWord, description = False, "Spell Damage", "Spell Damage +1"
	
	
class BoulderfistOgre(Minion):
	Class, race, name = "Neutral", "", "Boulderfist Ogre"
	mana, attack, health = 6, 6, 7
	index = "Basic-Neutral-6-6-7-Minion-None-Boulderfist Ogre"
	needTarget, keyWord, description = False, "", ""
	
	
class RecklessRocketeer(Minion):
	Class, race, name = "Neutral", "", "Reckless Rocketeer"
	mana, attack, health = 6, 5, 2
	index = "Basic-Neutral-6-5-2-Minion-None-Reckless Rocketeer-Charge"
	needTarget, keyWord, description = False, "Charge", "Charge"
	
"""Mana 7 minions"""
class CoreHound(Minion):
	Class, race, name = "Neutral", "Beast", "Core Hound"
	mana, attack, health = 7, 9, 5
	index = "Basic-Neutral-7-9-5-Minion-Beast-Core Hound"
	needTarget, keyWord, description = False, "", ""
	
	
class StormwindChampion(Minion):
	Class, race, name = "Neutral", "", "Stormwind Champion"
	mana, attack, health = 7, 6, 6
	index = "Basic-Neutral-7-6-6-Minion-None-Stormwind Champion"
	needTarget, keyWord, description = False, "", "Your other minions have +1/+1"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.auras["Buff Aura"] = BuffAura_Dealer_All(self, None, 1, 1)
		
		
class WarGolem(Minion):
	Class, race, name = "Neutral", "", "War Golem"
	mana, attack, health = 7, 7, 7
	index = "Basic-Neutral-7-7-7-Minion-None-War Golem"
	needTarget, keyWord, description = False, "", ""
	
"""Druid cards"""
class Innervate(Spell):
	Class, name = "Druid", "Innervate"
	needTarget, mana = False, 0
	index = "Basic-Druid-0-Spell-Innervate"
	description = "Gain 1 Mana Crystal this turn only"
	def whenEffective(self, target=None, comment="", choice=0):
		print("Innervate hero gains a mana for this turn.")
		if self.Game.ManaHandler.manas[self.ID] < 10:
			self.Game.ManaHandler.manas[self.ID] += 1
		return None
		
		
class Moonfire(Spell):
	Class, name = "Druid", "Moonfire"
	needTarget, mana = True, 0
	index = "Basic-Druid-0-Spell-Moonfire"
	description = "Deal 1 damage"
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			damage = (1 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			print("Moonfire deals %d damage to "%damage, target.name)
			self.dealsDamage(target, damage)
		return target
		
		
class Claw(Spell):
	Class, name = "Druid", "Claw"
	needTarget, mana = False, 1
	index = "Basic-Druid-1-Spell-Claw"
	description = "Give your hero +2 Attack this turn. Gain 2 Armor"
	def whenEffective(self, target=None, comment="", choice=0):
		print("Claw hero %d %s gains 2 Sttack and 2 Armor"%(self.ID, self.Game.heroes[self.ID].name))
		self.Game.heroes[self.ID].gainTempAttack(2)
		self.Game.heroes[self.ID].gainsArmor(2)
		return None
		
		
class MarkoftheWild(Spell):
	Class, name = "Druid", "Mark of the Wild"
	needTarget, mana = True, 2
	index = "Basic-Druid-2-Spell-Mark of the Wild"
	description = "Give a minion +2/+2 ant Taunt"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		if target.cardType == "Minion" and target.onBoard:
			return True
		return False
		
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			print("Mark of the Wild gives minion %s +2/+2 and Taunt."%target.name)
			target.buffDebuff(2, 2) #buffDebuff() and getsKeyword() will check if the minion is onBoard or inHand.
			target.getsKeyword("Taunt")
		return target
		
		
class HealingTouch(Spell):
	Class, name = "Druid", "Healing Touch"
	needTarget, mana = True, 3
	index = "Basic-Druid-3-Spell-Healing Touch"
	description = "Restore 8 health"
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			heal = 8 * (2 ** self.countHealDouble())
			print("Healing Touch restores %d health to "%heal, target.name)
			self.restoresHealth(target, heal)
		return target
		
		
class SavageRoar(Spell):
	Class, name = "Druid", "Savage Roar"
	needTarget, mana = False, 3
	index = "Basic-Druid-3-Spell-Savage Roar"
	description = "Give your characters +2 Attack this turn"
	def whenEffective(self, target=None, comment="", choice=0):
		print("Savage Roar gives all friendly characters +2 Attack this turn.")
		self.Game.heroes[self.ID].gainTempAttack(2)
		for minion in fixedList(self.Game.minionsonBoard(self.ID)):
			minion.buffDebuff(2, 0, "EndofTurn")
		return None
		
		
class WildGrowth(Spell):
	Class, name = "Druid", "Wild Growth"
	needTarget, mana = False, 3
	index = "Basic-Druid-3-Spell-Wild Growth"
	description = "Gain an empty Mana Crystal"
	def whenEffective(self, target=None, comment="", choice=0):
		print("Wild Growth gives player an empty mana.")
		if self.Game.ManaHandler.gainEmptyManaCrystal(1, self.ID) == False:
			print("Player's mana at upper limit already. Wild Growth gives player an Excess Mana instead.")
			self.Game.Hand_Deck.addCardtoHand(ExcessMana(self.Game, self.ID), self.ID)
		return None
		
class ExcessMana(Spell):
	Class, name = "Druid", "Excess Mana"
	needTarget, mana = False, 0
	index = "Basic-Druid-0-Spell-Excess Mana-Uncollectible"
	description = "Draw a card"
	def whenEffective(self, target=None, comment="", choice=0):
		print("Excess Mana lets player draw a card.")
		self.Game.Hand_Deck.drawCard(self.ID)
		return None
		
		
class Swipe(Spell):
	Class, name = "Druid", "Swipe"
	needTarget, mana = True, 4
	index = "Basic-Druid-4-Spell-Swipe"
	description = "Deal 4 damage to an enemy and 1 damage to all other enemies"
	def available(self):
		return self.selectableEnemyExists()
		
	def targetCorrect(self, target, choice=0):
		if (target.cardType == "Minion" or target.cardType == "Hero") and target.ID != self.ID and target.onBoard:
			return True
		return False
		
	def whenEffective(self, target=None, comment="", choice=0):
		AOE_damage = (1 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		target_damage = (4 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		if target != None:
			print("Swipe deals %d damage to "%target_damage, target.name)
			self.dealsDamage(target, target_damage)
			targets = self.returnTargets(comment="IgnoreStealthandImmune")
			extractfrom(target, targets)
		else:
			targets = self.returnTargets(comment="IgnoreStealthandImmune")
			
		print("Swipe deals %d damage to %s and %d damage to all other enemies."%(target_damage, target, AOE_damage))
		self.dealsAOE(targets, [AOE_damage for obj in targets])
		return target
		
class Starfire(Spell):
	Class, name = "Druid", "Starfire"
	needTarget, mana = True, 6
	index = "Basic-Druid-6-Spell-Starfire"
	description = "Deal 5 damage. Draw a card"
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			damage = (5 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			print("Starfire deals %d damage to %s and lets player draw a card."%(damage, target.name))
			self.dealsDamage(target, damage)
		self.Game.Hand_Deck.drawCard(self.ID)
		return target
		
		
class IronbarkProtector(Minion):
	Class, race, name = "Druid", "", "Ironbark Protector"
	mana, attack, health = 8, 8, 8
	index = "Basic-Druid-8-8-8-Minion-None-Ironbark Protector-Taunt"
	needTarget, keyWord, description = False, "Taunt", "Taunt"
	
"""Hunter Cards"""
class ArcaneShot(Spell):
	Class, name = "Hunter", "Arcane Shot"
	needTarget, mana = True, 1
	index = "Basic-Hunter-1-Spell-Arcane Shot"
	description = "Deal 2 damage"
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			damage = (2 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			print("Arcane Shot deals %d damage to "%damage, target.name)
			self.dealsDamage(target, damage)
		return target
		
class TimberWolf(Minion):
	Class, race, name = "Hunter", "Beast", "Timber Wolf"
	mana, attack, health = 1, 1, 1
	index = "Basic-Hunter-1-1-1-Minion-Beast-Timber Wolf"
	needTarget, keyWord, description = False, "", "Your other Beasts have +1 Attack"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.auras["Buff Aura"] = BuffAura_Dealer_All(self, self.applicable, 1, 0)
		
	def applicable(self, target):
		return "Beast" in target.race
		
		
#In real game, when there is only one card left in deck,
# player still needs to choose, despite only one option available.
class Tracking(Spell):
	Class, name = "Hunter", "Tracking"
	needTarget, mana = False, 1
	index = "Basic-Hunter-1-Spell-Tracking"
	description = "Look at the top 3 cards of your deck. Draw one and discard the others."
	def randomorDiscover(self):
		if len(self.Game.Hand_Deck.decks[self.ID]) < 2:
			return "No RNG"
		else:
			return "Discover"
			
	def whenEffective(self, target=None, comment="", choice=0):
		print("Tracking is cast and enters the discover preparation.")
		numCardsLeft = len(self.Game.Hand_Deck.decks[self.ID])
		if numCardsLeft  == 1:
			print("Tracking player draws the only remaining card from deck.")					
			self.Game.Hand_Deck.drawCard(self.ID)
		elif numCardsLeft > 1:
			num = min(3, numCardsLeft)
			cards = [self.Game.Hand_Deck.decks[self.ID][-i] for i in range(num)]
			if comment == "CastbyOthers":
				cardtoDraw = cards.pop(np.random.randint(num))
				print("Tracking randomly draws one of the top 3 cards. And removes the other two.")
				self.Game.Hand_Deck.drawCard(self.ID, cardtoDraw)
				self.Game.Hand_Deck.extractfromDeck(cards)
			else:
				self.Game.options = cards
				self.Game.DiscoverHandler.startDiscover(self)
				
		return None
		
	def discoverDecided(self, option):
		cardtoDraw = extractfrom(option, self.Game.options)
		self.Game.Hand_Deck.drawCard(self.ID, cardtoDraw)
		self.Game.Hand_Deck.extractfromDeck(self.Game.options)
		
		
class HuntersMark(Spell):
	Class, name = "Hunter", "Hunter's Mark"
	needTarget, mana = True, 2
	index = "Basic-Hunter-2-Spell-Hunter's Mark"
	description = "Change a minion's health to 1"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		if target.cardType == "Minion" and target.onBoard:
			return True
		return False
		
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			print("Hunter's Mark sets %s's health to 1."%target.name)
			target.statReset(False, 1)
		return target
		
class AnimalCompanion(Spell):
	Class, name = "Hunter", "Animal Companion"
	needTarget, mana = False, 3
	index = "Basic-Hunter-3-Spell-Animal Companion"
	description = "Summon a random Beast Companion"
	def available(self):
		if self.Game.spaceonBoard(self.ID) > 0:
			return True
		return False
		
	def whenEffective(self, target=None, comment="", choice=0):
		if self.Game.spaceonBoard(self.ID) > 0:
			companion = np.random.choice([Huffer, Leokk, Misha])(self.Game, self.ID)
			print("Animal Companion summons ", companion.name)
			self.Game.summonMinion(companion, -1, self.ID)
		return None
		
class Huffer(Minion):
	Class, race, name = "Hunter", "Beast", "Huffer"
	mana, attack, health = 3, 4, 2
	index = "Basic-Hunter-3-4-2-Minion-Beast-Huffer-Charge-Uncollectible"
	needTarget, keyWord, description = False, "Charge", "Charge"
	
class Leokk(Minion):
	Class, race, name = "Hunter", "Beast", "Leokk"
	mana, attack, health = 3, 2, 4
	index = "Basic-Hunter-3-2-4-Minion-Beast-Leokk-Uncollectible"
	needTarget, keyWord, description = False, "", "Your other minions have +1 Attack"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.auras["Buff Aura"] = BuffAura_Dealer_All(self, None, 1, 0)
		
class Misha(Minion):
	Class, race, name = "Hunter", "Beast", "Misha"
	mana, attack, health = 3, 4, 4
	index = "Basic-Hunter-3-4-4-Minion-Beast-Misha-Taunt-Uncollectible"
	needTarget, keyWord, description = False, "Taunt", "Taunt"
	
	
class KillCommand(Spell):
	Class, name = "Hunter", "Kill Command"
	needTarget, mana = True, 3
	index = "Basic-Hunter-3-Spell-Kill Command"
	description = "Deal 3 damage. If you control a Beast, deal 5 damage instead"
	def bonusEffectCanTrigger(self):
		for minion in self.Game.minionsonBoard(self.ID):
			if "Beast" in minion.race:
				return True
				
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			if self.bonusEffectCanTrigger():
				damage = (5 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			else:
				damage = (3 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
				
			print("Kill Command deals %d damage to "%damage, target.name)
			self.dealsDamage(target, damage)
		return target
		
		
class Houndmaster(Minion):
	Class, race, name = "Hunter", "", "Houndmaster"
	mana, attack, health = 4, 4, 3
	index = "Basic-Hunter-4-4-3-Minion-None-Houndmaster-Battlecry"
	needTarget, keyWord, description = True, "", "Battlecry: Give a friendly Beast +2/+2 and Taunt"
	
	def targetExists(self, choice=0):
		return self.selectableFriendlyMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.ID == self.ID and "Beast" in target.race and target != self and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			print("Houndmaster's battlecry gives friendly Beast %s +2/+2 and Taunt."%target.name)
			target.buffDebuff(2, 2)
			target.getsKeyword("Taunt")
		return self, target
		
		
class MultiShot(Spell):
	Class, name = "Hunter", "Multi Shot"
	needTarget, mana = False, 4
	index = "Basic-Hunter-4-Spell-Multi Shot"
	description = "Deal 3 damage to two random enemy minions"
	def randomorDiscover(self):
		if len(self.Game.minionsonBoard(3-self.ID)) < 3:
			return "No RNG"
		return "Random"
		
	def available(self):
		if self.Game.minionsonBoard(3-self.ID) != []:
			return True
		return False
		
	def whenEffective(self, target=None, comment="", choice=0):
		damage = (3 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		minions = self.Game.minionsonBoard(3-self.ID)
		if len(minions) > 1:
			print("Multi Shot deals %d damage to two random minions: "%damage, targets)
			targets = np.random.choice(minions, 2, replace=False)
			self.dealsAOE(targets, [damage, damage])
		elif len(minions) == 1:
			print("Multi Shot deals %d damage to minion "%damage, minions[0].name)
			self.dealsDamage(minions[0], damage)
		return None
		
		
class StarvingBuzzard(Minion):
	Class, race, name = "Hunter", "Beast", "Starving Buzzard"
	mana, attack, health = 5, 3, 2
	index = "Basic-Hunter-5-3-2-Minion-Beast-Starving Buzzard"
	needTarget, keyWord, description = False, "", "Whenever you summon a Beast, draw a card"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_StarvingBuzzard(self)]
		
class Trigger_StarvingBuzzard(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionSummoned"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and self.entity.health > 0 and subject.ID == self.entity.ID and "Beast" in subject.race and subject != self.entity
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("A friendly Beast is summoned and %s lets player draw a card."%self.entity.name)
		self.entity.Game.Hand_Deck.drawCard(self.entity.ID)
		
		
class TundraRhino(Minion):
	Class, race, name = "Hunter", "Beast", "Tundra Rhino"
	mana, attack, health = 5, 2, 5
	index = "Basic-Hunter-5-2-5-Minion-Beast-Tundra Rhino"
	needTarget, keyWord, description = False, "", "Your Beasts have Charge"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.auras["Has Aura"] = HasAura_Dealer(self, self.applicable, "Charge")
		
	def applicable(self, target):
		return "Beast" in target.race
		
"""Mage cards"""
class ArcaneMissiles(Spell):
	Class, name = "Mage", "Arcane Missiles"
	needTarget, mana = False, 1
	index = "Basic-Mage-1-Spell-Arcane Missiles"
	description = "Deal 3 damage randomly split among all enemies"
	def randomorDiscover(self):
		if self.Game.minionsonBoard(3-self.ID) == []:
			return "No RNG"
		return "Random"
		
	def whenEffective(self, target=None, comment="", choice=0):
		num = (3 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		print("Arcane Missiles launches %d missiles."%num)
		for i in range(0, num):
			targets = [self.Game.heroes[3-self.ID]]
			for minion in self.Game.minionsonBoard(3-self.ID):
				if minion.health > 0 and minion.dead == False:
					targets.append(minion)
					
			self.dealsDamage(np.random.choice(targets), 1)
		return None
		
		
class MirrorImage(Spell):
	Class, name = "Mage", "Mirror Image"
	needTarget, mana = False, 1
	index = "Basic-Mage-1-Spell-Mirror Image"
	description = "Summon two 0/2 minions with Taunt"
	def available(self):
		if self.Game.spaceonBoard(self.ID):
			return True
		return False
		
	def whenEffective(self, target=None, comment="", choice=0):
		print("Mirror Image summons two 0/2 Mirror Images with Taunt.")
		self.Game.summonMinion([MirrorImage_Minion(self.Game, self.ID) for i in range(2)], (-1, "totheRightEnd"), self.ID)
		return None
		
class MirrorImage_Minion(Minion):
	Class, race, name = "Mage", "", "Mirror Image"
	mana, attack, health = 1, 0, 2
	index = "Basic-Mage-1-0-2-Minion-None-Mirror Image-Taunt-Uncollectible"
	needTarget, keyWord, description = False, "Taunt", "Taunt"
	
	
class ArcaneExplosion(Spell):
	Class, name = "Mage", "Arcane Explosion"
	needTarget, mana = False, 2
	index = "Basic-Mage-2-Spell-Arcane Explosion"
	description = "Deal 1 damage to all enemy minions"
	def whenEffective(self, target=None, comment="", choice=0):
		damage = (1 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		targets = self.Game.minionsonBoard(3-self.ID)
		print("Arcane Explosion deals %d damage to all enemy minions"%damage)
		self.dealsAOE(targets, [damage for obj in targets])
		return None
		
		
class Frostbolt(Spell):
	Class, name = "Mage", "Frostbolt"
	needTarget, mana = True, 2
	index = "Basic-Mage-2-Spell-Frostbolt"
	description = "Deal 3 damage to a character and Freeze it"
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			damage = (3 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			print("Frostbolt deals %d damage to %s and freezes it."%(damage, target.name))
			self.dealsDamage(target, damage)
			target.getsFrozen()
		return target
		
		
class ArcaneIntellect(Spell):
	Class, name = "Mage", "Arcane Intellect"
	needTarget, mana = False, 3
	index = "Basic-Mage-3-Spell-Arcane Intellect"
	description = "Draw 2 cards"
	def whenEffective(self, target=None, comment="", choice=0):
		print("Arcane Intellect lets player draws two cards")
		self.Game.Hand_Deck.drawCard(self.ID)
		self.Game.Hand_Deck.drawCard(self.ID)
		return None
		
		
class FrostNova(Spell):
	Class, name = "Mage", "Frost Nova"
	needTarget, mana = False, 3
	index = "Basic-Mage-3-Spell-Frost Nova"
	description = "Freeze all enemy minions"
	def whenEffective(self, target=None, comment="", choice=0):
		print("Frost Nova freezes all enemy minions")
		#Fix the targets so that minions that resolutions that summon minions due to minion being frozen won't make the list expand.
		for minion in fixedList(self.Game.minionsonBoard(3-self.ID)):
			minion.getsFrozen()
		return None
		
		
class Fireball(Spell):
	Class, name = "Mage", "Fireball"
	needTarget, mana = True, 4
	index = "Basic-Mage-4-Spell-Fireball"
	description = "Deal 6 damage"
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			damage = (6 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			print("Fireball deals %d damage to "%damage, target.name)
			self.dealsDamage(target, damage)
		return target
		
		
class Polymorph(Spell):
	Class, name = "Mage", "Polymorph"
	needTarget, mana = True, 4
	index = "Basic-Mage-4-Spell-Polymorph"
	description = "Transform a minion into a 1/1 Sheep"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			print("Polymorph transforms minion %s into a 1/1 Sheep."%target.name)
			newMinion = Sheep(self.Game, target.ID)
			self.Game.transform(target, newMinion)
			return newMinion
		else:
			return None
			
class Sheep(Minion):
	Class, race, name = "Neutral", "Beast", "Sheep"
	mana, attack, health = 1, 1, 1
	index = "Basic-Neutral-1-1-1-Minion-Beast-Sheep-Uncollectible"
	needTarget, keyWord, description = False, "", ""
	
	
class WaterElemental(Minion):
	Class, race, name = "Mage", "Elemental", "Water Elemental"
	mana, attack, health = 4, 3, 6
	index = "Basic-Mage-4-3-6-Minion-Elemental-Water Elemental"
	needTarget, keyWord, description = False, "", "Freeze any character damaged by this minion"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_WaterElemental(self)]
		
class Trigger_WaterElemental(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionTakesDamage", "HeroTakesDamage"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return subject == self.entity
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print(self.entity.name, "deals damage to %s and freezes it."%target.name)
		target.getsFrozen()
		
		
class Flamestrike(Spell):
	Class, name = "Mage", "Flamestrike"
	needTarget, mana = False, 7
	index = "Basic-Mage-7-Spell-Flamestrike"
	description = "Deal 4 damage to all enemy minions"
	def whenEffective(self, target=None, comment="", choice=0):
		damage = (4 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		print("Flamestrike deals %d damage to all enemy minions"%damage)
		targets = self.Game.minionsonBoard(3-self.ID)
		self.dealsAOE(targets, [damage for minion in targets])
		return None
		
"""Paladin Cards"""
class BlessingofMight(Spell):
	Class, name = "Paladin", "Blessing of Might"
	needTarget, mana = True, 1
	index = "Basic-Paladin-1-Spell-Blessing of Might"
	description = "Give a minion +3 Attack"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		if target.cardType == "Minion" and target.onBoard:
			return True
		return False
		
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			print("Blessing of Might gives minion %s +3 Attack."%target.name)
			target.buffDebuff(3, 0)
		return target
		
		
class HandofProtection(Spell):
	Class, name = "Paladin", "Hand of Protection"
	needTarget, mana = True, 1
	index = "Basic-Paladin-1-Spell-Hand of Protection"
	description = "Give a minion Divine Shield"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		if target.cardType == "Minion" and target.onBoard:
			return True
		return False
		
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			print("Hand of Protection gives %s Divine Shield."%target.name)
			target.getsKeyword("Divine Shield")
		return target
		
		
class Humility(Spell):
	Class, name = "Paladin", "Humility"
	needTarget, mana = True, 1
	index = "Basic-Paladin-1-Spell-Humility"
	description = "Change a minion's Attack to 1"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		if target.cardType == "Minion" and target.onBoard:
			return True
		return False
		
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			print("Humility sets minion %s's Attack to 1."%target.name)
			target.statReset(1, False)
		return target
		
		
class LightsJustice(Weapon):
	Class, name, description = "Paladin", "Light's Justice", ""
	mana, attack, durability = 1, 1, 4
	index = "Basic-Paladin-1-1-4-Weapon-Light's Justice"
	
	
class HolyLight(Spell):
	Class, name = "Paladin", "Holy Light"
	needTarget, mana = True, 2
	index = "Basic-Paladin-2-Spell-Holy Light"
	description = "Restore 6 health"
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			heal = 6 * (2 ** self.countHealDouble())
			print("Holy Light restores %d health to "%heal, target.name)
			self.restoresHealth(target, heal)
		return target
		
		
class BlessingofKings(Spell):
	Class, name = "Paladin", "Blessing of Kings"
	needTarget, mana = True, 4
	index = "Basic-Paladin-4-Spell-Blessing of Kings"
	description = "Give a minion +4/+4"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		if target.cardType == "Minion" and target.onBoard:
			return True
		return False
		
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			print("Blessing of Kings gives %s +4/+4."%target.name)
			target.buffDebuff(4, 4)
		return target
		
		
class Consecration(Spell):
	Class, name = "Paladin", "Consecration"
	needTarget, mana = False, 4
	index = "Basic-Paladin-4-Spell-Consecration"
	description = "Deal 2 damage to all enemies"
	def whenEffective(self, target=None, comment="", choice=0):
		damage = (2 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		targets = [self.Game.heroes[3-self.ID]] + self.Game.minionsonBoard(3-self.ID)
		print("Consecration deals %d damage to all enemies"%damage)
		self.dealsAOE(targets, [damage for obj in targets])
		return None
		
		
class HammerofWrath(Spell):
	Class, name = "Paladin", "Hammer of Wrath"
	needTarget, mana = True, 4
	index = "Basic-Paladin-4-Spell-Hammer of Wrath"
	description = "Deal 3 damage. Draw a card"
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			damage = (3 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			print("Hammer of Wrath deals %d damage to %s and freezes it. Then player draws a card."%(damage, target.name))
			self.dealsDamage(target, damage)
			self.Game.Hand_Deck.drawCard(self.ID)
		return target
		
		
class TruesilverChampion(Weapon):
	Class, name, description = "Paladin", "Truesilver Champion", "Whenever your hero attacks, restore 2 Health to it"
	mana, attack, durability = 4, 4, 2
	index = "Basic-Paladin-4-4-2-Weapon-Truesilver Champion"
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
		print(self.entity.name, "restores %d Health the hero when it attacks.")
		self.restoresHealth(self.entity.Game.heroes[self.entity.ID], heal)
		
		
class GuardianofKings(Minion):
	Class, race, name = "Paladin", "", "Guardian of Kings"
	mana, attack, health = 7, 5, 6
	index = "Basic-Paladin-7-5-6-Minion-None-Guardian of Kings-Battlecry"
	needTarget, keyWord, description = False, "", "Battlecry: Restore 6 health to your hero"
	
	def whenEffective(self, target=None, comment="", choice=0):
		heal = 6 * (2 ** self.countHealDouble())
		print("Guardian of Kings' battlecry restores %d health to player's hero."%heal)
		self.restoresHealth(self.Game.heroes[self.ID], heal)
		return self, None
		
"""Priest Cards"""
class HolySmite(Spell):
	Class, name = "Priest", "Holy Smite"
	needTarget, mana = True, 1
	index = "Basic-Priest-1-Spell-Holy Smite"
	description = "Deal 2 damage"
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			damage = (2 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			print("Holy Smite deals %d damage to "%damage, target.name)
			self.dealsDamage(target, damage)
		return target
		
		
class MindVision(Spell):
	Class, name = "Priest", "Mind Vision"
	needTarget, mana = False, 1
	index = "Basic-Priest-1-Spell-Mind Vision"
	description = "Put a copy of a random card in your opponent's hand into your hand"
	def randomorDiscover(self):
		return "Random"
		
	def whenEffective(self, target=None, comment="", choice=0):
		if self.Game.Hand_Deck.handNotFull(self.ID) and self.Game.Hand_Deck.hands[3-self.ID] != []:
			print("Mind Vision copies a card from enemy hand")
			target = np.random.choice(self.Game.Hand_Deck.hands[3-self.ID])
			Copy = target.selfCopy(self.ID)
			self.Game.Hand_Deck.addCardtoHand(Copy, self.ID)
		return None
		
		
class NorthshireCleric(Minion):
	Class, race, name = "Priest", "", "Northshire Cleric"
	mana, attack, health = 1, 1, 3
	index = "Basic-Priest-1-1-3-Minion-None-Northshire Cleric"
	needTarget, keyWord, description = False, "", "Whenever a minion is healed, draw a card"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_NorthshireCleric(self)]
		
class Trigger_NorthshireCleric(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionGetsHealed"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and self.entity.health > 0 and self.entity.dead == False
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("A character is healed and %s lets player draw a card."%self.entity.name)
		self.entity.Game.Hand_Deck.drawCard(self.entity.ID)
		
		
class PowerWordShield(Spell):
	Class, name = "Priest", "Power Word: Shield"
	needTarget, mana = True, 1
	index = "Basic-Priest-1-Spell-Power Word: Shield"
	description = "Give a minion +2 Health. Draw a card"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			print("Power Word: Shield gives minion %s +2 health. Then player draws a card."%target.name)
			target.buffDebuff(0, 2)
			self.Game.Hand_Deck.drawCard(self.ID)
		return target
		
		
class Radiance(Spell):
	Class, name = "Priest", "Radiance"
	needTarget, mana = False, 1
	index = "Basic-Priest-1-Spell-Radiance"
	description = "Restore 5 health to your hero"
	def whenEffective(self, target=None, comment="", choice=0):
		heal = 5 * (2 ** self.countHealDouble())
		print("Radiance restores %d heal to hero"%heal)
		self.restoresHealth(self.Game.heroes[self.ID], heal)
		return None
		
		
class DivineSpirit(Spell):
	Class, name = "Priest", "Divine Spirit"
	needTarget, mana = True, 2
	index = "Basic-Priest-2-Spell-Divine Spirit"
	description = "Double a minion's Health"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		if target.cardType == "Minion" and target.onBoard:
			return True
		return False
		
	#Divine Spirit double a minion's current health and compares the two values.
	#The different will be the +X health buff to the minion.
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			print("Divine Spirit doubles minion %s's health."%target.name)
			health = 2 * target.health
			difference = health - target.health
			target.buffDebuff(0, difference)
		return target
		
		
class ShadowWordPain(Spell):
	Class, name = "Priest", "Shadow Word: Pain"
	needTarget, mana = True, 2
	index = "Basic-Priest-2-Spell-Shadow Word: Pain"
	description = "Destroy a minion with 3 or less Attack"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		if target.cardType == "Minion" and target.attack < 4 and target.onBoard:
			return True
		return False
		
	#Target after returned to hand will be discarded.
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			if target.onBoard:
				print("Shadow Word: Pain destroys minion %s with 3 or less Attack."%target.name)
				target.dead = True
			elif target.inHand: #Target in hand will be discarded.
				print("Shadow Word: Pain discards the target %s returned to hand."%target.name)
				self.Game.Hand_Deck.discardCard(target.ID, target)
		return target
		
		
class ShadowWordDeath(Spell):
	Class, name = "Priest", "Shadow Word: Death"
	needTarget, mana = True, 3
	index = "Basic-Priest-3-Spell-Shadow Word: Death"
	description = "Destroy a minion with 5 or more Attack"
	def available(self):
		return selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		if target.cardType == "Minion" and target.attack > 4 and target.onBoard:
			return True
		return False
		
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			if target.onBoard:
				print("Shadow Word: Death destroys minion %s with 3 or less Attack."%target.name)
				target.dead = True
			elif target.inHand: #Target in hand will be discarded.
				print("Shadow Word: Death discards the target %s returned to hand."%target.name)
				self.Game.Hand_Deck.discardCard(target.ID, target)
		return target
		
		
class HolyNova(Spell):
	Class, name = "Priest", "Holy Nova"
	needTarget, mana = False, 5
	index = "Basic-Priest-5-Spell-Holy Nova"
	description = "Deal 2 damage to all enemies. Restore 2 Health to all friendly characters"
	def whenEffective(self, target=None, comment="", choice=0):
		damage = (2 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		heal = 2 * (2 ** self.countHealDouble())
		enemies = [self.Game.heroes[3-self.ID]] + self.Game.minionsonBoard(3-self.ID)
		friendlies = [self.Game.heroes[self.ID]] + self.Game.minionsonBoard(self.ID)
		print("Holy Nova deals %d damage to all enemies and restores %d health to all friendlies."%(damage, heal))
		self.dealsAOE(enemies, [damage for obj in enemies], friendlies, [heal for obj in friendlies])
		return None
		
		
class MindControl(Spell):
	Class, name = "Priest", "Mind Control"
	needTarget, mana = True, 10
	index = "Basic-Priest-10-Spell-Mind Control"
	description = "Take control of an enemy minion"
	def available(self):
		return self.selectableEnemyMinionExists()
		
	def targetCorrect(self, target, choice=0):
		if target.cardType == "Minion" and target.ID != self.ID and target.onBoard:
			return True
		return False
		
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None and target.ID != self.ID:
			print("Mind Control takes control of enemy minion ", target.name)
			self.Game.minionSwitchSide(target) #minionSwitchSide() will takes care of the case where minion is in hand
		return target
		
"""Rogue Cards"""
class Backstab(Spell):
	Class, name = "Rogue", "Backstab"
	needTarget, mana = True, 0
	index = "Basic-Rogue-0-Spell-Backstab"
	description = "Deal 2 damage to an undamage minion"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		if target.cardType == "Minion" and target.health == target.health_upper and target.onBoard:
			return True
		return False
		
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			damage = (2 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			print("Backstab deals %d damage to minion "%damage, target.name)
			self.dealsDamage(target, damage)
		return target
		
		
class WickedKnife(Weapon):
	Class, name, description = "Rogue", "Wicked Knife", ""
	mana, attack, durability = 1, 1, 2
	index = "Basic-Rogue-1-1-2-Weapon-Wicked Knife-Uncollectible"
	
class PoisonedDagger(Weapon):
	Class, name, description = "Rogue", "Poisoned Dagger", ""
	mana, attack, durability = 1, 2, 2
	index = "Basic-Rogue-1-2-2-Weapon-Poisoned Dagger-Uncollectible"
	
	
class DeadlyPoison(Spell):
	Class, name = "Rogue", "Deadly Poison"
	needTarget, mana = False, 1
	index = "Basic-Rogue-1-Spell-Deadly Poison"
	description = "Give your weapon +2 Attack"
	def available(self):
		if self.Game.availableWeapon(self.ID) == None:
			return False
		return True
		
	def whenEffective(self, target=None, comment="", choice=0):
		weapon = self.Game.availableWeapon(self.ID)
		if weapon != None:
			print("Deadly Poison gives hero %d's weapon %s 2 Attack"%(self.ID, weapon.name))
			weapon.gainStat(2, 0)
		return None
		
		
class SinisterStrike(Spell):
	Class, name = "Rogue", "Sinister Strike"
	needTarget, mana = False, 1
	index = "Basic-Rogue-1-Spell-Sinister Strike"
	description = "Deal 3 damage to the enemy hero"
	def whenEffective(self, target=None, comment="", choice=0):
		damage = (3 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		print("Sinister Strike deals %d damage to enemy hero"%damage)
		self.dealsDamage(self.Game.heroes[3-self.ID], damage)
		return None
		
		
class Sap(Spell):
	Class, name = "Rogue", "Sap"
	needTarget, mana = True, 2
	index = "Basic-Rogue-2-Spell-Sap"
	description = "Return an enemy minion to your opponent's hand"
	def available(self):
		return self.selectableEnemyMinionExists()
		
	def targetCorrect(self, target, choice=0):
		if target.cardType == "Minion" and target.ID != self.ID and target.onBoard:
			return True
		return False
		
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			print("Sap returns enemy minion %s to its owner's hand."%target.name)
			self.Game.returnMiniontoHand(target)
		return target
		
		
class Shiv(Spell):
	Class, name = "Rogue", "Shiv"
	needTarget, mana = True, 2
	index = "Basic-Rogue-2-Spell-Shiv"
	description = "Deal 1 damage. Draw a card"
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			damage = (1 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			print("Shiv deals %d damage to target %s. Then player draws a card."%(damage, target.name))
			self.dealsDamage(target, damage)
		self.Game.Hand_Deck.drawCard(self.ID)
		return target
		
		
class FanofKnives(Spell):
	Class, name = "Rogue", "Fan of Knives"
	needTarget, mana = False, 3
	index = "Basic-Rogue-3-Spell-Fan of Knives"
	description = "Deal 1 damage to all enemy minions. Draw a card"
	def whenEffective(self, target=None, comment="", choice=0):
		damage = (1 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		targets = self.Game.minionsonBoard(3-self.ID)
		print("Fan of Knives deals %d damage to all enemy minions."%damage)
		self.dealsAOE(targets, [damage for minion in targets])
		self.Game.Hand_Deck.drawCard(self.ID)
		return None
		
		
class Plaguebringer(Minion):
	Class, race, name = "Rogue", "", "Plaguebringer"
	mana, attack, health = 4, 3, 3
	index = "Basic-Rogue-4-3-3-Minion-None-Plaguebringer-Battlecry"
	needTarget, keyWord, description = True, "", "Battlecry: Give a friendly Poisonous"
	
	def targetExists(self, choice=0):
		return self.selectableFriendlyMinionExists()
		
	def targetCorrect(self, target, choice=0):
		if target.cardType == "Minion" and target.ID == self.ID and target != self and target.onBoard:
			return True
		return False
		
	#Infer from Windfury: Target when in hand should be able to gets Poisonous and keep it next time it's played.
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			print("Plaguebringer's battlecry gives friendly minion %s Poisonous."%target.name)
			target.getsKeyword("Poisonous")
		return self, target
		
		
class Assassinate(Spell):
	Class, name = "Rogue", "Assassinate"
	needTarget, mana = True, 5
	index = "Basic-Rogue-5-Spell-Assassinate"
	description = "Destroy an enemy minion"
	def available(self):
		return self.selectableEnemyMinionExists()
		
	def targetCorrect(self, target, choice=0):
		if target.cardType == "Minion" and target.ID != self.ID and target.onBoard:
			return True
		return False
		
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			print("Assassinate destroys enemy minion ", target.name)
			target.dead = True
		return target
		
		
class AssassinsBlade(Weapon):
	Class, name, description = "Rogue", "Assassin's Blade", ""
	mana, attack, durability = 5, 3, 4
	index = "Basic-Rogue-5-3-4-Weapon-Assassin's Blade"
	
	
class Sprint(Spell):
	Class, name = "Rogue", "Sprint"
	needTarget, mana = False, 7
	index = "Basic-Rogue-7-Spell-Sprint"
	description = "Draw 4 cards"
	def whenEffective(self, target=None, comment="", choice=0):
		print("Sprint player draws 4 cards.")
		self.Game.Hand_Deck.drawCard(self.ID)
		self.Game.Hand_Deck.drawCard(self.ID)
		self.Game.Hand_Deck.drawCard(self.ID)
		self.Game.Hand_Deck.drawCard(self.ID)
		return None
		
"""Shaman Cards"""
class AncestralHealing(Spell):
	Class, name = "Shaman", "Ancestral Healing"
	needTarget, mana = True, 0
	index = "Basic-Shaman-0-Spell-Ancestral Healing"
	description = "Restore a minion to full health and give it Taunt"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		if target.cardType == "Minion" and target.onBoard:
			return True
		return False
		
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			print("Ancestral Healing restores minion %s to its full health."%target.name)
			self.restoresHealth(target, target.health_upper)
		return target
		
		
class TotemicMight(Spell):
	Class, name = "Shaman", "Totemic Might"
	needTarget, mana = False, 0
	index = "Basic-Shaman-0-Spell-Totemic Might"
	description = "Give you Totems +2 Health"
	def whenEffective(self, target=None, comment="", choice=0):
		print("Totemic Might gives all friendly totems +2 health")
		for minion in fixedList(self.Game.minionsonBoard(self.ID)):
			if "Totem" in minion.race:
				minion.buffDebuff(0, 2)
		return None
		
		
class FrostShock(Spell):
	Class, name = "Shaman", "Frost Shock"
	needTarget, mana = True, 1
	index = "Basic-Shaman-1-Spell-Frost Shock"
	description = "Deal 1 damage to an enemy character and Freeze it"
	def available(self):
		return self.selectableEnemyExists()
		
	def targetCorrect(self, target, choice=0):
		if (target.cardType == "Minion" or target.cardType == "Hero") and target.ID != self.ID and target.onBoard:
			return True
		return False
		
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			damage = (1 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			print("Frost Shock deals %d damage to enemy %s. Then freezes it."%(damage, target.name))
			self.dealsDamage(target, damage)
			target.getsFrozen()
		return target
		
		
class RockbiterWeapon(Spell):
	Class, name = "Shaman", "Rockbiter Weapon"
	needTarget, mana = True, 2
	index = "Basic-Shaman-2-Spell-Rockbiter Weapon"
	description = "Give a friendly character +3 Attack this turn"
	def available(self):
		return self.selectableFriendlyExists()
		
	def targetCorrect(self, target, choice=0):
		if (target.cardType == "Minion" or target.cardType == "Hero") and target.ID == self.ID and target.onBoard:
			return True
		return False
		
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			print("Rockbiter Weapon gives friendly %s +3 Attack this turn."%target.name)
			if target.cardType == "Hero":
				target.gainTempAttack(3)
			else:
				target.buffDebuff(3, 0, "EndofTurn")
		return target
		
		
class Windfury(Spell):
	Class, name = "Shaman", "Windfury"
	needTarget, mana = True, 2
	index = "Basic-Shaman-2-Spell-Windfury"
	description = "Give a minion Windfury"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		if target.cardType == "Minion" and target.onBoard:
			return True
		return False
		
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			print("Windfury gives minion %s Windfury."%target.name)
			target.getsKeyword("Windfury")
		return target
		
		
class FlametongueTotem(Minion):
	Class, race, name = "Shaman", "Totem", "Flametongue Totem"
	mana, attack, health = 3, 0 ,3
	index = "Basic-Shaman-3-0-3-Minion-Totem-Flametongue Totem"
	needTarget, keyWord, description = False, "", "Adjacent minions have +2 Attack"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.auras["Buff Aura"] = BuffAura_Dealer_Adjacent(self, None, 2, 0)
		
		
class Hex(Spell):
	Class, name = "Shaman", "Hex"
	needTarget, mana = True, 4
	index = "Basic-Shaman-4-Spell-Hex"
	description = "Transform a minion into a 0/1 Frog with Taunt"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		if target.cardType == "Minion" and target.onBoard:
			return True
		return False
		
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			print("Hex transforms minion %s into a 0/1 Frog with Taunt."%target.name)
			newMinion = Frog(self.Game, target.ID)
			self.Game.transform(target, newMinion)
			return newMinion
		else:
			return None
		
class Frog(Minion):
	Class, race, name = "Neutral", "Beast", "Frog"
	mana, attack, health = 1, 0, 1
	index = "Basic-Neutral-1-0-1-Minion-Beast-Frog-Taunt-Uncollectible"
	needTarget, keyWord, description = False, "Taunt", "Taunt"
	
	
class Windspeaker(Minion):
	Class, race, name = "Shaman", "", "Windspeaker"
	mana, attack, health = 4, 3, 3
	index = "Basic-Shaman-4-3-3-Minion-None-Windspeaker-Battlecry"
	needTarget, keyWord, description = True, "", "Battlecry: Give a friendly minion Windfury"
	
	def targetExists(self, choice=0):
		return self.selectableFriendlyMinionExists()
		
	def targetCorrect(self, target, choice=0):
		if target.cardType == "Minion" and target.ID == self.ID and target != self and target.onBoard:
			return True
		return False
		
	#Gurubashi Berserker is returned to hand and then given Windfury. It still has Windfury when replayed.
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			print("Windspeaker's battlecry gives %s windfury"%target.name)
			target.getsKeyword("Windfury")
		return self, target
		
		
class Bloodlust(Spell):
	Class, name = "Shaman", "Bloodlust"
	needTarget, mana = False, 5
	index = "Basic-Shaman-5-Spell-Bloodlust"
	description = "Give your minions +3 Attack this turn"
	def available(self):
		return self.Game.minionsonBoard(self.ID) != []
		
	def whenEffective(self, target=None, comment="", choice=0):
		print("Bloodlust gives all friendly minions +3 Attack this turn.")
		for minion in fixedList(self.Game.minionsonBoard(self.ID)):
			minion.buffDebuff(3, 0, "EndofTurn")
		return None
		
		
class FireElemental(Minion):
	Class, race, name = "Shaman", "Elemental", "Fire Elemental"
	mana, attack, health = 6, 6, 5
	index = "Basic-Shaman-6-6-5-Minion-Elemental-Fire Elemental-Battlecry"
	needTarget, keyWord, description = True, "", "Battlecry: Deal 3 damage"
	
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			print("Fire Elemental's battlecry deals 3 damage to ", target.name)
			self.dealsDamage(target, 3)
		return self, target
		
"""Warlock Cards"""
class SacrificialPact(Spell):
	Class, name = "Warlock", "Sacrificial Pact"
	needTarget, mana = True, 0
	index = "Basic-Warlock-0-Spell-Sacrificial Pact"
	description = "Destroy a Demon. Restore 5 health to you hero"
	def targetCorrect(self, target, choice=0):
		if target.cardType == "Minion" and "Demon" in target.race and target.onBoard:
			return True
		elif target.name == "Lord Jaraxxus":
			return True
		return False
		
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			heal = 5 * (2 ** self.countHealDouble())
			print("Sacrificial Pact destroys Demon %s. Then restores %d heal to player."%(target.name, heal))
			target.dead = True
		self.restoresHealth(self.Game.heroes[self.ID], heal)
		return target
		
		
class Corruption(Spell):
	Class, name = "Warlock", "Corruption"
	needTarget, mana = True, 1
	index = "Basic-Warlock-1-Spell-Corruption"
	description = "Choose an enemy minion. At the start of your turn, destroy it"
	def available(self):
		return self.selectableEnemyMinionExists()
		
	def targetCorrect(self, target, choice=0):
		if target.cardType == "Minion" and target.ID != self.ID and target.onBoard:
			return True
		return False
	#Tested: Corruption won't have any effect on minions in hand. They won't be discarded nor marked after played.
	#The Corruption effect can be cleansed with Silence effect.
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None and target.onBoard:
			print("Corruption chooses enemy minion %s to die at the start of player's next turn."%target.name)
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
		
	def connect(self):
		for signal in self.signals:
			self.entity.Game.triggersonBoard[self.ID].append((self, signal))
			
	def disconnect(self):
		for signal in self.signals:
			extractfrom((self, signal), self.entity.Game.triggersonBoard[self.ID])
			
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and ID == self.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("At the start of player %d's turn, Corrupted minion %s dies."%(self.ID, self.entity.name))
		self.entity.dead = True
		self.disconnect()
		extractfrom(self, self.entity.triggersonBoard)
		
		
class MortalCoil(Spell):
	Class, name = "Warlock", "Mortal Coil"
	needTarget, mana = True, 1
	index = "Basic-Warlock-1-Spell-Mortal Coil"
	description = "Deal 1 damage to a minion. If that kills it, draw a card"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.onBoard
		
	#When cast by Archmage Vargoth, this spell can target minions with health <=0 and automatically meet the requirement of killing.
	#If the target minion dies before this spell takes effect, due to being killed by Violet Teacher/Knife Juggler, Mortal Coil still lets
	#player draw a card.
	#If the target is None due to Mayor Noggenfogger's randomization, nothing happens.
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			if target.onBoard or target.inHand:
				damage = (1 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
				print("Mortal Coil deals %d damage to minion "%damage, target.name)
				if self.dealsDamage(target, damage)[1] > 1:
					print("Mortal Coil kills the target and lets player draw a card.")
					self.Game.Hand_Deck.drawCard(self.ID)
			else: #The minion is dead and removed or shuffled into deck.
				if target.dead and target.inDeck == False: #The minion is dead already.
					self.Game.Hand_Deck.drawCard(self.ID)
		return target
		
		
class Soulfire(Spell):
	Class, name = "Warlock", "Soulfire"
	needTarget, mana = True, 1
	index = "Basic-Warlock-1-Spell-Soulfire"
	description = "Deal 4 damage. Discard a random card"
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			damage = (4 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			print("Soulfire deals %d damage to target %s. Then player discard a card."%(damage, target.name))
			self.dealsDamage(target, damage)
		self.Game.Hand_Deck.discardCard(self.ID)
		return target
		
		
class Voidwalker(Minion):
	Class, race, name = "Warlock", "Demon", "Voidwalker"
	mana, attack, health = 1, 1, 3
	index = "Basic-Warlock-1-1-3-Minion-Demon-Voidwalker-Taunt"
	needTarget, keyWord, description = False, "Taunt", "Taunt"
	
	
class Felstalker(Minion):
	Class, race, name = "Warlock", "Demon", "Felstalker"
	mana, attack, health = 2, 4, 3
	index = "Basic-Warlock-2-4-3-Minion-Demon-Felstalker-Battlecry"
	needTarget, keyWord, description = False, "", "Battlecry: Discard a random card"
	
	def whenEffective(self, target=None, comment="", choice=0):
		print("Felstalker's battlecry discards a random card.")
		self.Game.Hand_Deck.discardCard(self.ID)
		return self, None
		
class DrainLife(Spell):
	Class, name = "Warlock", "Drain Life"
	needTarget, mana = True, 3
	index = "Basic-Warlock-3-Spell-Drain Life"
	description = "Deal 2 damage. Restore 2 Health to your hero"
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			damage = (2 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			print("Drain Life deals %d damage to"%damage, target.name)
			self.dealsDamage(target, damage)
		heal = 2 * (2 ** self.countHealDouble())
		print("Drain Life restores %d Health to player."%heal)
		self.restoresHealth(self.Game.heroes[self.ID], heal)
		return target
		
		
class ShadowBolt(Spell):
	Class, name = "Warlock", "Shadow Bolt"
	needTarget, mana = True, 3
	index = "Basic-Warlock-3-Spell-Shadow Bolt"
	description = "Deal 4 damage to a minion"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		if target.cardType == "Minion" and target.onBoard:
			return True
		return False
		
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			damage = (4 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			print("Shadow Bolt deals %d damage to minion "%damage, target.name)
			self.dealsDamage(target, damage)
		return target
		
		
class Hellfire(Spell):
	Class, name = "Warlock", "Hellfire"
	needTarget, mana = False, 4
	index = "Basic-Warlock-4-Spell-Hellfire"
	description = "Deal 3 damage to ALL characters"
	def whenEffective(self, target=None, comment="", choice=0):
		damage = (3 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		targets = [self.Game.heroes[1], self.Game.heroes[2]] + self.Game.minionsonBoard(1) + self.Game.minionsonBoard(2)
		print("Hellfire deals %d damage to all characters."%damage)
		self.dealsAOE(targets, [damage for obj in targets])
		return None
		
		
class DreadInfernal(Minion):
	Class, race, name = "Warlock", "Demon", "Dread Infernal"
	mana, attack, health = 6, 6, 6
	index = "Basic-Warlock-6-6-6-Minion-Demon-Dread Infernal-Battlecry"
	needTarget, keyWord, description = False, "", "Battlecry: Deal 1 damage to ALL other characters"
	
	#Will trigger: Returned to hand, killed, controlled by enemy.
	#Find all minions on board.
	def whenEffective(self, target=None, comment="", choice=0):
		targets = [self.Game.heroes[1], self.Game.heroes[2]] + self.Game.minionsonBoard(1) + self.Game.minionsonBoard(2)
		extractfrom(self, targets)
		print("Dread Infernal's battlecry deals 1 damage to all other characters.")
		self.dealsAOE(targets, [1 for obj in targets])
		return self, None
		
"""Warrior Cards"""
class Whirlwind(Spell):
	Class, name = "Warrior", "Whirlwind"
	needTarget, mana = False, 1
	index = "Basic-Warrior-1-Spell-Whirlwind"
	description = "Deal 1 damage to ALL minions"
	def whenEffective(self, target=None, comment="", choice=0):
		damage = (1 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		targets = self.Game.minionsonBoard(1) + self.Game.minionsonBoard(2)
		print("Whirlwind deals %d damage to all minions."%damage)
		self.dealsAOE(targets, [damage for minion in targets])
		return None
		
		
class Charge(Spell):
	Class, name = "Warrior", "Charge"
	needTarget, mana = True, 1
	index = "Basic-Warrior-1-Spell-Charge"
	description = "Give a friendly minion Charge. It can't attack heroes this turn"
	def available(self):
		return self.selectableFriendlyMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.ID == self.ID and target.onBoard
		
	#This can't attack hero state doesn't count as enchantment.
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			print("Charge gives friendly minion %s Charge. But it can't attack heroes this turn."%target.name)
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
		print("At the end of turn, minion %s can attack hero again."%self.entity.name)
		if self.entity.marks["Can't Attack Hero"] > 0:
			self.entity.marks["Can't Attack Hero"] -= 1
		self.disconnect()
		extractfrom(self, self.entity.triggersonBoard)
		
		
class Execute(Spell):
	Class, name = "Warrior", "Execute"
	needTarget, mana = True, 2
	index = "Basic-Warrior-2-Spell-Execute"
	description = "Destroy a damaged enemy minion"
	def available(self):
		return self.selectableEnemyMinionExists()
		
	def targetCorrect(self, target, choice=0):
		if target.cardType == "Minion" and target.ID != self.ID and target.health < target.health_upper and target.onBoard:
			return True
		return False
		
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			print("Execute destroys damaged minion ", target.name)
			target.dead = True
		return target
		
		
class Cleave(Spell):
	Class, name = "Warrior", "Cleave"
	needTarget, mana = False, 2
	index = "Basic-Warrior-2-Spell-Cleave"
	description = "Deal 2 damage to two random enemy minions"
	def randomorDiscover(self):
		if len(self.Game.minionsonBoard(3-self.ID)) < 3:
			return "No RNG"
		return "Random"
		
	def available(self):
		return self.Game.minionsonBoard(3-self.ID) != []
		
	def whenEffective(self, target=None, comment="", choice=0):
		damage = (2 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		minions = self.Game.minionsonBoard(3-self.ID)
		if len(minions) > 1:
			targets = np.random.choice(minions, 2, replace=False)
			print("Cleave deals %d damage to two random minions: "%damage, targets)
			self.dealsAOE(targets, [damage, damage])
		elif len(minions) == 1:
			print("Cleave deals %d damage to minion "%damage, minions[0].name)
			self.dealsDamage(minions[0], damage)
		return None
		
		
class HeroicStrike(Spell):
	Class, name = "Warrior", "Heroic Strike"
	needTarget, mana = False, 2
	index = "Basic-Warrior-2-Spell-Heroic Strike"
	description = "Give your hero +4 Attack this turn"
	def whenEffective(self, target=None, comment="", choice=0):
		print("Heroic Strike gives hero +4 Attack.")
		self.Game.heroes[self.ID].gainTempAttack(4)
		return None
		
		
class FieryWarAxe(Weapon):
	Class, name, description = "Warrior", "Fiery War Axe", ""
	mana, attack, durability = 3, 3, 2
	index = "Basic-Warrior-3-3-2-Weapon-Fiery War Axe"
	
	
class ShieldBlock(Spell):
	Class, name = "Warrior", "Shield Block"
	needTarget, mana = False, 3
	index = "Basic-Warrior-3-Spell-Shield Block"
	description = "Gain 5 Armor. Draw a card"
	def whenEffective(self, target=None, comment="", choice=0):
		print("Shield Block gives hero +5 armor.")
		self.Game.heroes[self.ID].gainsArmor(5)
		self.Game.Hand_Deck.drawCard(self.ID)
		return None
		
#Charge gained by enchantment and aura can also be buffed by this Aura.
class WarsongCommander(Minion):
	Class, race, name = "Warrior", "", "Warsong Commander"
	mana, attack, health = 3, 2, 3
	index = "Basic-Warrior-3-2-3-Minion-None-Warsong Commander"
	needTarget, keyWord, description = False, "", "Your Charge minions have +1 Attack"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.auras["Buff Aura"] = WarsongCommander_Aura(self)
		
		
class KorkronElite(Minion):
	Class, race, name = "Warrior", "", "Kor'kron Elite"
	mana, attack, health = 4, 4, 3
	index = "Basic-Warrior-4-4-3-Minion-None-Kor'kron Elite-Charge"
	needTarget, keyWord, description = False, "Charge", "Charge"
	
	
class ArcaniteReaper(Weapon):
	Class, name, description = "Warrior", "Arcanite Reaper", ""
	mana, attack, durability = 5, 5, 2
	index = "Basic-Warrior-5-5-2-Weapon-Arcanite Reaper"