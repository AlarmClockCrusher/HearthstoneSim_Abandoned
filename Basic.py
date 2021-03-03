from CardTypes import *
from Triggers_Auras import *
from numpy.random import choice as npchoice
from numpy.random import randint as nprandint
from numpy.random import shuffle as npshuffle
from numpy import inf as npinf
import numpy as np

"""Basic"""

class SearingTotem(Minion):
	Class, race, name = "Shaman", "Totem", "Searing Totem"
	mana, attack, health = 1, 1, 1
	index = "Basic~Shaman~Minion~1~1~1~Totem~Searing Totem~Uncollectible"
	requireTarget, keyWord, description = False, "", ""
	name_CN = "灼热图腾"
	
class StoneclawTotem(Minion):
	Class, race, name = "Shaman", "Totem", "Stoneclaw Totem"
	mana, attack, health = 1, 0, 2
	index = "Basic~Shaman~Minion~1~0~2~Totem~Stoneclaw Totem~Taunt~Uncollectible"
	requireTarget, keyWord, description = False, "Taunt", "Taunt"
	name_CN = "石爪图腾"
	
class HealingTotem(Minion):
	Class, race, name = "Shaman", "Totem", "Healing Totem"
	mana, attack, health = 1, 0, 2
	index = "Basic~Shaman~Minion~1~0~2~Totem~Healing Totem~Uncollectible"
	requireTarget, keyWord, description = False, "", "At the end of your turn, restore 1 health to all friendly minions"
	name_CN = "治疗图腾"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_HealingTotem(self)]
		
class Trig_HealingTotem(TrigBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["TurnEnds"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and ID == self.entity.ID
		
	def text(self, CHN):
		heal = 2 * (2 ** self.entity.countHealDouble())
		return "在你的回合结束时，为所有友方随从恢复%d生命值"%heal if CHN else "At the end of your turn, restore %d health to all friendly minions"%heal
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		heal = 1 * (2 ** self.entity.countHealDouble())
		targets = self.entity.Game.minionsonBoard(self.entity.ID)
		self.entity.restoresAOE(targets, [heal for minion in targets])
		
class StrengthTotem(Minion):
	Class, race, name = "Shaman", "Totem", "Strength Totem"
	mana, attack, health = 1, 0, 2
	index = "Basic~Shaman~Minion~1~0~2~Totem~Strength Totem~Uncollectible"
	requireTarget, keyWord, description = False, "", "At the end of your turn, give another friendly minion +1 Attack"
	name_CN = "力量图腾"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_StrengthTotem(self)]
		
class Trig_StrengthTotem(TrigBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["TurnEnds"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and ID == self.entity.ID
		
	def text(self, CHN):
		return "在你的回合结束时，为使另一个友方随从获得+1攻击力" if CHN else "At the end of your turn, give another friendly minion +1 Attack"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		curGame = self.entity.Game
		if curGame.mode == 0:
			if curGame.guides:
				i = curGame.guides.pop(0)
			else:
				minions = curGame.minionsonBoard(self.entity.ID, self.entity)
				i = npchoice(minions).pos if minions else -1
				curGame.fixedGuides.append(i)
			if i > -1: curGame.minions[self.entity.ID][i].buffDebuff(1, 0)
			
#class WrathofAirTotem(Minion):
#	Class, race, name = "Shaman", "Totem", "Wrath of Air Totem"
#	mana, attack, health = 1, 0, 2
#	index = "Basic~Shaman~Minion~1~0~2~Totem~Wrath of Air Totem~Spell Damage~Uncollectible"
#	requireTarget, keyWord, description = False, "Spell Damage", "Spell Damage +1"#Default Spell Damage is 1.
#	name_CN = "空气之怒图腾"
	
BasicTotems = [SearingTotem, StoneclawTotem, HealingTotem, StrengthTotem]

"""Basic Hero Powers"""
class DemonClaws(HeroPower):
	mana, name, requireTarget = 1, "Demon Claws", False
	index = "Demon Hunter~Basic Hero Power~1~Demon Claws"
	description = "+1 Attack this turn"
	name_CN = "恶魔之爪"
	def effect(self, target=None, choice=0):
		self.Game.heroes[self.ID].gainAttack(1)
		return 0
		
class DemonsBite(HeroPower):
	mana, name, requireTarget = 1, "Demon's Bite", False
	index = "Demon Hunter~Upgraded Hero Power~1~Demon's Bite"
	description = "+2 Attack this turn"
	name_CN = "恶魔之咬"
	def effect(self, target=None, choice=0):
		self.Game.heroes[self.ID].gainAttack(2)
		return 0
		
#Druid basic and upgraded powers
class Shapeshift(HeroPower):
	mana, name, requireTarget = 2, "Shapeshift", False
	index = "Druid~Basic Hero Power~2~Shapeshift"
	description = "+1 Attack this turn. +1 Armor"
	name_CN = "变形"
	def effect(self, target=None, choice=0):
		self.Game.heroes[self.ID].gainsArmor(1)
		self.Game.heroes[self.ID].gainAttack(1)
		return 0
		
class DireShapeshift(HeroPower):
	mana, name, requireTarget = 2, "Dire Shapeshift", False
	index = "Druid~Upgraded Hero Power~2~Dire Shapeshift"
	description = "+2 Attack this turn. +2 Armor"
	name_CN = "恐怖变形"
	def effect(self, target=None, choice=0):
		self.Game.heroes[self.ID].gainsArmor(2)
		self.Game.heroes[self.ID].gainAttack(2)
		return 0
		
#Hunter basic and upgraded powers
class SteadyShot(HeroPower):
	mana, name, requireTarget = 2, "Steady Shot", False
	index = "Hunter~Basic Hero Power~2~Steady Shot"
	description = "Deal 2 damage to the enemy hero"
	name_CN = "稳固射击"
	def returnFalse(self, choice=0):
		return self.Game.status[self.ID]["Power Can Target Minions"] > 0
		
	def targetCorrect(self, target, choice=0):
		return (target.type == "Minion" or target.type == "Hero") and target.onBoard
		
	def text(self, CHN):
		damage = (2 + self.Game.status[self.ID]["Power Damage"]) * (2 ** self.countDamageDouble())
		if self.Game.status[self.ID]["Power Can Target Minions"] > 0:
			return "造成%d点伤害"%damage if CHN else "Deal %d damage"%damage
		else:
			return "对敌方英雄造成%d点伤害"%damage if CHN else "Deal %d damage to the enemy hero"%damage
			
	def effect(self, target=None, choice=0):
		damage = (2 + self.Game.status[self.ID]["Power Damage"]) * (2 ** self.countDamageDouble())
		self.dealsDamage(target if target else self.Game.heroes[3-self.ID], damage)
		return 0
		
class BallistaShot(HeroPower):
	mana, name, requireTarget = 2, "Ballista Shot", False
	index = "Hunter~Upgraded Hero Power~2~Ballista Shot"
	description = "Deal 3 damage to the enemy hero"
	name_CN = "弩炮射击"
	def returnFalse(self, choice=0):
		return self.Game.status[self.ID]["Power Can Target Minions"] > 0
		
	def targetCorrect(self, target, choice=0):
		if self.Game.status[self.ID]["Power Can Target Minions"] > 0:
			return (target.type == "Minion" or target.type == "Hero") and target.onBoard
		else:
			return target.type == "Hero" and target.ID != self.ID and target.onBoard
			
	def text(self, CHN):
		damage = (3 + self.Game.status[self.ID]["Power Damage"]) * (2 ** self.countDamageDouble())
		if self.Game.status[self.ID]["Power Can Target Minions"] > 0:
			return "造成%d点伤害"%damage if CHN else "Deal %d damage"%damage
		else:
			return "对敌方英雄造成%d点伤害"%damage if CHN else "Deal %d damage to the enemy hero"%damage
			
	def effect(self, target=None, choice=0):
		damage = (3 + self.Game.status[self.ID]["Power Damage"]) * (2 ** self.countDamageDouble())
		self.dealsDamage(target if target else self.Game.heroes[3-self.ID], damage)
		return 0
		
#Mage basic and upgraded powers
class Fireblast(HeroPower):
	mana, name, requireTarget = 2, "Fireblast", True
	index = "Mage~Basic Hero Power~2~Fireblast"
	description = "Deal 1 damage"
	name_CN = "火焰冲击"
	def text(self, CHN):
		damage = (1 + self.Game.status[self.ID]["Power Damage"]) * (2 ** self.countDamageDouble())
		return "造成%d点伤害"%damage if CHN else "Deal %d damage"%damage
		
	def effect(self, target, choice=0):
		damage = (1 + self.Game.status[self.ID]["Power Damage"]) * (2 ** self.countDamageDouble())
		dmgTaker, damageActual = self.dealsDamage(target, damage)
		if dmgTaker.health < 1 or dmgTaker.dead: return 1
		return 0
		
class FireblastRank2(HeroPower):
	mana, name, requireTarget = 2, "Fireblast Rank 2", True
	index = "Mage~Upgraded Hero Power~2~Fireblast Rank 2"
	description = "Deal 2 damage"
	name_CN = "二级火焰冲击"
	def text(self, CHN):
		damage = (2 + self.Game.status[self.ID]["Power Damage"]) * (2 ** self.countDamageDouble())
		return "造成%d点伤害"%damage if CHN else "Deal %d damage"%damage
		
	def effect(self, target, choice=0):
		damage = (2 + self.Game.status[self.ID]["Power Damage"]) * (2 ** self.countDamageDouble())
		dmgTaker, damageActual = self.dealsDamage(target, damage)
		if dmgTaker.health < 1 or dmgTaker.dead: return 1
		return 0
		
#Paladin basic and upgraded powers
class Reinforce(HeroPower):
	mana, name, requireTarget = 2, "Reinforce", False
	index = "Paladin~Basic Hero Power~2~Reinforce"
	description = "Summon a 1/1 Silver Hand Recruit"
	name_CN = "增援"
	def available(self):
		return not self.chancesUsedUp() and self.Game.space(self.ID)
		
	def effect(self, target=None, choice=0):
		#Hero Power summoning won't be doubled by Khadgar.
		self.Game.summon(SilverHandRecruit(self.Game, self.ID), -1, self.ID, "")
		return 0
		
class TheSilverHand(HeroPower):
	mana, name, requireTarget = 2, "The Silver Hand", False
	index = "Paladin~Upgraded Hero Power~2~The Silver Hand"
	description = "Summon two 1/1 Silver Hand Recruits"
	name_CN = "白银之手"
	def available(self):
		return not self.chancesUsedUp() and self.Game.space(self.ID)
		
	def effect(self, target=None, choice=0):
		self.Game.summon([SilverHandRecruit(self.Game, self.ID) for i in range(2)], (-1, "totheRightEnd"), self.ID, "")
		return 0
		
#Priest basic and upgraded powers
class LesserHeal(HeroPower):
	mana, name, requireTarget = 2, "Lesser Heal", True
	index = "Priest~Basic Hero Power~2~Lesser Heal"
	description = "Restore 2 Health"
	name_CN = "次级治疗术"
	def text(self, CHN):
		heal = 2 * (2 ** self.countHealDouble())
		return "恢复%d点生命值"%heal if CHN else "Restore %d Health"%heal
		
	def effect(self, target, choice=0):
		heal = 2 * (2 ** self.countHealDouble())
		obj, targetSurvival = self.restoresHealth(target, heal)
		if targetSurvival > 1: return 1
		return 0
		
class Heal(HeroPower):
	mana, name, requireTarget = 2, "Heal", True
	index = "Priest~Upgraded Hero Power~2~Heal"
	description = "Restore 4 Health"
	name_CN = "治疗术"
	def text(self, CHN):
		heal = 3 * (2 ** self.countHealDouble())
		return "恢复%d点生命值"%heal if CHN else "Restore %d Health"%heal
		
	def effect(self, target, choice=0):
		heal = 4 * (2 ** self.countHealDouble())
		obj, targetSurvival = self.restoresHealth(target, heal)
		if targetSurvival > 1: return 1
		return 0
		
#Rogue basic and upgraded powers
class DaggerMastery(HeroPower):
	mana, name, requireTarget = 2, "Dagger Mastery", False
	index = "Rogue~Basic Hero Power~2~Dagger Mastery"
	description = "Equip a 1/2 Weapon"
	name_CN = "匕首精通"
	def effect(self, target=None, choice=0):
		self.Game.equipWeapon(WickedKnife(self.Game, self.ID))
		return 0
		
class PoisonedDaggers(HeroPower):
	mana, name, requireTarget = 2, "Poisoned Daggers", False
	index = "Rogue~Upgraded Hero Power~2~Poisoned Daggers"
	description = "Equip a 2/2 Weapon"
	name_CN = "浸毒匕首"
	def effect(self, target=None, choice=0):
		self.Game.equipWeapon(PoisonedDagger(self.Game, self.ID))
		return 0
		
#Shaman basic and upgraded powers
class TotemicCall(HeroPower):
	mana, name, requireTarget = 2, "Totemic Call", False
	index = "Shaman~Basic Hero Power~2~Totemic Call"
	description = "Summon a random totem"
	name_CN = "图腾召唤"
	def available(self):
		return not self.chancesUsedUp() and self.Game.space(self.ID) and self.viableTotems()[0]
		
	def effect(self, target=None, choice=0):
		curGame = self.Game
		if curGame.mode == 0:
			if curGame.guides:
				totem = curGame.guides.pop(0)
			else:
				size, totems = self.viableTotems()
				totem = npchoice(totems) if size else None
				curGame.fixedGuides.append(totem)
			if totem: curGame.summon(totem(curGame, self.ID), -1, self.ID, '')
		return 0
		
	def viableTotems(self):
		viableTotems = [SearingTotem, StoneclawTotem, HealingTotem, StrengthTotem]
		for minion in self.Game.minionsonBoard(self.ID):
			try: viableTotems.remove(type(minion))
			except: pass
		return len(viableTotems), viableTotems
		
class TotemicSlam(HeroPower):
	mana, name, requireTarget = 2, "Totemic Slam", False
	index = "Shaman~Upgraded Hero Power~2~Totemic Call"
	description = "Summon a totem of your choice"
	name_CN = "图腾崇拜"
	def available(self):
		return not self.chancesUsedUp() and self.Game.space(self.ID) 
		
	def effect(self, target=None, choice=0):
		curGame = self.Game
		if curGame.mode == 0:
			if curGame.guides:
				curGame.summon(curGame.guides.pop(0)(curGame, self.ID), -1, self.ID, '')
			else:
				curGame.options = [totem(curGame, self.ID) for totem in [SearingTotem, StoneclawTotem, HealingTotem, StrengthTotem]]
				curGame.Discover.startDiscover(self)
		return 0
		
	def discoverDecided(self, option, pool):
		self.Game.fixedGuides.append(type(option))
		self.Game.summon(option, -1, self.ID, "")
		
#Warloc basic and upgraded powers
class LifeTap(HeroPower):
	mana, name, requireTarget = 2, "Life Tap", False
	index = "Warlock~Basic Hero Power~2~Life Tap"
	description = "Draw a card and take 2 damage"
	name_CN = "生命分流"
	def text(self, CHN):
		damage = (2 + self.Game.status[self.ID]["Power Damage"]) * (2 ** self.countDamageDouble())
		return "抽一张牌并受到%d点伤害"%damage if CHN else "Draw a card and take %d damage"%damage
		
	def effect(self, target=None, choice=0):
		damage = (2 + self.Game.status[self.ID]["Power Damage"]) * (2 ** self.countDamageDouble())
		self.dealsDamage(self.Game.heroes[self.ID], damage)
		card, mana = self.Game.Hand_Deck.drawCard(self.ID)
		if card:
			self.Game.sendSignal("CardDrawnfromHeroPower", self.ID, self, card, mana, "")
		return 0
		
class SoulTap(HeroPower):
	mana, name, requireTarget = 2, "Soul Tap", False
	index = "Warlock~Upgraded Hero Power~2~Soul Tap"
	description = "Draw a card"
	name_CN = "灵魂分流"
	def effect(self, target=None, choice=0):
		card, mana = self.Game.Hand_Deck.drawCard(self.ID)
		if card:
			self.Game.sendSignal("CardDrawnfromHeroPower", self.ID, self, card, mana, "")
		return 0
		
#Warrior basic and upgraded powers
class ArmorUp(HeroPower):
	mana, name, requireTarget = 2, "Armor Up!", False
	index = "Warrior~Basic Hero Power~2~Armor Up!"
	description = "Gain 2 Armor"
	name_CN = "全副武装！"
	def effect(self, target=None, choice=0):
		self.Game.heroes[self.ID].gainsArmor(2)
		return 0
		
class TankUp(HeroPower):
	mana, name, requireTarget = 2, "Tank Up!", False
	index = "Warrior~Upgraded Hero Power~2~Tank Up!"
	description = "Gain 4 Armor"
	name_CN = "铜墙铁壁！"
	def effect(self, target=None, choice=0):
		self.Game.heroes[self.ID].gainsArmor(4)
		return 0
		
Basicpowers = [Shapeshift, SteadyShot, Fireblast, Reinforce, LesserHeal, DaggerMastery, TotemicCall, LifeTap, ArmorUp]
Upgradedpowers = [DireShapeshift, BallistaShot, FireblastRank2, TheSilverHand, Heal, PoisonedDaggers, TotemicSlam, SoulTap, TankUp]
"""Basic Heroes"""
class Illidan(Hero):
	Class, name, heroPower = "Demon Hunter", "Illidan", DemonClaws
	name_CN = "伊利丹"
	
class Rexxar(Hero):
	Class, name, heroPower = "Hunter", "Rexxar", SteadyShot
	name_CN = "雷克萨"
	
class Valeera(Hero):
	Class, name, heroPower = "Rogue", "Valeera", DaggerMastery
	name_CN = "瓦莉拉"
	
class Malfurion(Hero):
	Class, name, heroPower = "Druid", "Malfurion", Shapeshift
	name_CN = "玛法里奥"
	
class Garrosh(Hero):
	Class, name, heroPower = "Warrior", "Garrosh", ArmorUp
	name_CN = "加尔鲁什"
	
class Uther(Hero):
	Class, name, heroPower = "Paladin", "Uther", Reinforce
	name_CN = "乌瑟尔"
	
class Thrall(Hero):
	Class, name, heroPower = "Shaman", "Thrall", TotemicCall
	name_CN = "萨尔"
	
class Jaina(Hero):
	Class, name, heroPower = "Mage", "Jaina", Fireblast
	name_CN = "吉安娜"
	
class Anduin(Hero):
	Class, name, heroPower = "Priest", "Anduin", LesserHeal
	name_CN = "安度因"
	
class Guldan(Hero):
	Class, name, heroPower = "Warlock", "Gul'dan", LifeTap
	name_CN = "古尔丹"
	
"""Mana 0 cards"""
class TheCoin(Spell):
	Class, school, name = "Neutral", "", "The Coin"
	requireTarget, mana = False, 0
	index = "Basic~Neutral~Spell~0~The Coin~Uncollectible"
	description = "Gain 1 mana crystal for this turn."
	name_CN = "幸运币"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if self.Game.Manas.manas[self.ID] < 10:
			self.Game.Manas.manas[self.ID] += 1
		return None
		
"""mana 1 minions"""
class ElvenArcher(Minion):
	Class, race, name = "Neutral", "", "Elven Archer"
	mana, attack, health = 1, 1, 1
	index = "Basic~Neutral~Minion~1~1~1~~Elven Archer~Battlecry"
	requireTarget, keyWord, description = True, "", "Battlecry: Deal 1 damamge"
	name_CN = "精灵弓箭手"
	#Dealing damage to minions not on board(moved to grave and returned to deck) won't have any effect.
	#Dealing damage to minions in hand will trigger Frothing Berserker, but that minion will trigger its own damage taken response.
	#When the minion in hand takes damage, at the moment it's replayed, the health will be reset even if it's reduced to below 0.
	#If this is killed before battlecry, will still deal damage.
	#If this is returned to hand before battlecry, will still deal damage.
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			self.dealsDamage(target, 1) #dealsDamage() on targets in grave/deck will simply pass.
		return target
		
		
class GoldshireFootman(Minion):
	Class, race, name = "Neutral", "", "Goldshire Footman"
	mana, attack, health = 1, 1, 2
	index = "Basic~Neutral~Minion~1~1~2~~Goldshire Footman~Taunt"
	requireTarget, keyWord, description = False, "Taunt", "Taunt"
	name_CN = "闪金镇步兵"
	
	
class GrimscaleOracle(Minion):
	Class, race, name = "Neutral", "Murloc", "Grimscale Oracle"
	mana, attack, health = 1, 1, 1
	index = "Basic~Neutral~Minion~1~1~1~Murloc~Grimscale Oracle"
	requireTarget, keyWord, description = False, "", "Your other Murlocs have +1 Attack"
	name_CN = "暗鳞先知"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.auras["Your other Murlocs have +1 Attack"] = StatAura_Others(self, 1, 0)
		
	def applicable(self, target):
		return "Murloc" in target.race
		
		
class MurlocRaider(Minion):
	Class, race, name = "Neutral", "Murloc", "Murloc Raider"
	mana, attack, health = 1, 2, 1
	index = "Basic~Neutral~Minion~1~2~1~Murloc~Murloc Raider"
	requireTarget, keyWord, description = False, "", ""
	name_CN = "鱼人袭击者"
	
	
class StonetuskBoar(Minion):
	Class, race, name = "Neutral", "Beast", "Stonetusk Boar"
	mana, attack, health = 1, 1, 1
	index = "Basic~Neutral~Minion~1~1~1~Beast~Stonetusk Boar~Charge"
	requireTarget, keyWord, description = False, "Charge", "Charge"
	name_CN = "石牙野猪"
	
	
class VoodooDoctor(Minion):
	Class, race, name = "Neutral", "", "Voodoo Doctor"
	mana, attack, health = 1, 2, 1
	index = "Basic~Neutral~Minion~1~2~1~~Voodoo Doctor~Battlecry"
	requireTarget, keyWord, description = True, "", "Battlecry: Restore 2 health"
	name_CN = "巫医"
	
	def text(self, CHN):
		heal = 2 * (2 ** self.countHealDouble())
		return "战吼：恢复%d点生命值"%heal if CHN else "Battlecry: Restore %d health"%heal
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			heal = 2 * (2 ** self.countHealDouble())
			self.restoresHealth(target, heal)
		return target
		
		
class SilverHandRecruit(Minion):
	Class, race, name = "Paladin", "", "Silver Hand Recruit"
	mana, attack, health = 1, 1, 1
	index = "Basic~Paladin~Minion~1~1~1~~Silver Hand Recruit~Uncollectible"
	requireTarget, keyWord, description = False, "", ""
	name_CN = "白银之手新兵"
	
"""Mana 2 minions"""
class AcidicSwampOoze(Minion):
	Class, race, name = "Neutral", "", "Acidic Swamp Ooze"
	mana, attack, health = 2, 3, 2
	index = "Basic~Neutral~Minion~2~3~2~~Acidic Swamp Ooze~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Destroy you opponent's weapon"
	name_CN = "酸性沼泽 软泥怪"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		for weapon in self.Game.weapons[3-self.ID]:
			weapon.destroyed()
		return None
		
		
class BloodfenRaptor(Minion):
	Class, race, name = "Neutral", "Beast", "Bloodfen Raptor"
	mana, attack, health = 2, 3, 2
	index = "Basic~Neutral~Minion~2~3~2~Beast~Bloodfen Raptor"
	requireTarget, keyWord, description = False, "", ""
	name_CN = "血沼迅猛龙"
	
	
class BluegillWarrior(Minion):
	Class, race, name = "Neutral", "Murloc", "Bluegill Warrior"
	mana, attack, health = 2, 2, 1
	index = "Basic~Neutral~Minion~2~2~1~Murloc~Bluegill Warrior~Charge"
	requireTarget, keyWord, description = False, "Charge", "Charge"
	name_CN = "蓝鳃战士"
	
	
class FrostwolfGrunt(Minion):
	Class, race, name = "Neutral", "", "Frostwolf Grunt"
	mana, attack, health = 2, 2, 2
	index = "Basic~Neutral~Minion~2~2~2~~Frostwolf Grunt~Taunt"
	requireTarget, keyWord, description = False, "Taunt", "Taunt"
	name_CN = "霜狼步兵"
	
	
class KoboldGeomancer(Minion):
	Class, race, name = "Neutral", "", "Kobold Geomancer"
	mana, attack, health = 2, 2, 2
	index = "Basic~Neutral~Minion~2~2~2~~Kobold Geomancer~Spell Damage"
	requireTarget, keyWord, description = False, "Spell Damage", "Spell Damage +1"
	name_CN = "狗头人地卜师"
	
	
class MurlocTidehunter(Minion):
	Class, race, name = "Neutral", "Murloc", "Murloc Tidehunter"
	mana, attack, health = 2, 2, 1
	index = "Basic~Neutral~Minion~2~2~1~Murloc~Murloc Tidehunter~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Summon a 1/1 Murloc Scout"
	name_CN = "鱼人猎潮者"
	#If controlled by enemy, will summon for enemy instead.
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.Game.summon(MurlocScout(self.Game, self.ID), self.pos+1, self.ID)
		return None
		
class MurlocScout(Minion):
	Class, race, name = "Neutral", "Murloc", "Murloc Scout"
	mana, attack, health = 1, 1, 1
	index = "Basic~Neutral~Minion~1~1~1~Murloc~Murloc Scout~Uncollectible"
	requireTarget, keyWord, description = False, "", ""
	name_CN = "鱼人斥侯"
	
	
class NoviceEngineer(Minion):
	Class, race, name = "Neutral", "", "Novice Engineer"
	mana, attack, health = 2, 1, 1
	index = "Basic~Neutral~Minion~2~1~1~~Novice Engineer~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Draw a card"
	name_CN = "工程师学徒"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.Game.Hand_Deck.drawCard(self.ID)
		return None
		
		
class RiverCrocolisk(Minion):
	Class, race, name = "Neutral", "Beast", "River Crocolisk"
	mana, attack, health = 2, 2, 3
	index = "Basic~Neutral~Minion~2~2~3~Beast~River Crocolisk"
	requireTarget, keyWord, description = False, "", ""
	name_CN = "淡水鳄"
	
"""Mana 3 minions"""		
class DalaranMage(Minion):
	Class, race, name = "Neutral", "", "Dalaran Mage"
	mana, attack, health = 3, 1, 4
	index = "Basic~Neutral~Minion~3~1~4~~Dalaran Mage~Spell Damage"
	requireTarget, keyWord, description = False, "Spell Damage", "Spell Damage +1"
	name_CN = "达拉然法师"
	
	
class IronforgeRifleman(Minion):
	Class, race, name = "Neutral", "", "Ironforge Rifleman"
	mana, attack, health = 3, 2, 2
	index = "Basic~Neutral~Minion~3~2~2~~Ironforge Rifleman~Battlecry"
	requireTarget, keyWord, description = True, "", "Battlecry: Deal 1 damage"
	name_CN = "铁炉堡火枪手"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			self.dealsDamage(target, 1)
		return target
		
		
class IronfurGrizzly(Minion):
	Class, race, name = "Neutral", "Beast", "Ironfur Grizzly"
	mana, attack, health = 3, 3, 3
	index = "Basic~Neutral~Minion~3~3~3~Beast~Ironfur Grizzly~Taunt"
	requireTarget, keyWord, description = False, "Taunt", "Taunt"
	name_CN = "铁鬃灰熊"
	
	
class MagmaRager(Minion):
	Class, race, name = "Neutral", "Elemental", "Magma Rager"
	mana, attack, health = 3, 5, 1
	index = "Basic~Neutral~Minion~3~5~1~Elemental~Magma Rager"
	requireTarget, keyWord, description = False, "", ""
	name_CN = "岩浆暴怒者"
	
	
class RaidLeader(Minion):
	Class, race, name = "Neutral", "", "Raid Leader"
	mana, attack, health = 3, 2, 3
	index = "Basic~Neutral~Minion~3~2~3~~Raid Leader"
	requireTarget, keyWord, description = False, "", "Your other minions have +1 Attack"
	name_CN = "团队领袖"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.auras["Your other minions have +1 Attack"] = StatAura_Others(self, 1, 0)
		
		
class RazorfenHunter(Minion):
	Class, race, name = "Neutral", "", "Razorfen Hunter"
	mana, attack, health = 3, 2, 3
	index = "Basic~Neutral~Minion~3~2~3~~Razorfen Hunter~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Summon a 1/1 Boar"
	name_CN = "剃刀猎手"
	
	#Infer from Dragonling Mechanic.
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.Game.summon(Boar(self.Game, self.ID), self.pos+1, self.ID)
		return None
		
class Boar(Minion):
	Class, race, name = "Neutral", "Beast", "Boar"
	mana, attack, health = 1, 1, 1
	index = "Basic~Neutral~Minion~1~1~1~Beast~Boar~Uncollectible"
	requireTarget, keyWord, description = False, "", ""
	name_CN = "野猪"
	
	
class ShatteredSunCleric(Minion):
	Class, race, name = "Neutral", "", "Shattered Sun Cleric"
	mana, attack, health = 3, 3, 2
	index = "Basic~Neutral~Minion~3~3~2~~Shattered Sun Cleric~Battlecry"
	requireTarget, keyWord, description = True, "", "Battlecry: Give friendly minion +1/+1"
	name_CN = "破碎残阳祭司"
	
	def targetExists(self, choice=0):
		return self.selectableFriendlyMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.ID == self.ID and target.onBoard and target != self
		
	#Infer from Houndmaster: Buff can apply on targets on board, in hand, in deck.
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			target.buffDebuff(1, 1)
		return target
		
		
class SilverbackPatriarch(Minion):
	Class, race, name = "Neutral", "Beast", "Silverback Patriarch"
	mana, attack, health = 3, 1, 4
	index = "Basic~Neutral~Minion~3~1~4~Beast~Silverback Patriarch~Taunt"
	requireTarget, keyWord, description = False, "Taunt", "Taunt"
	name_CN = "银背族长"
	
	
class Wolfrider(Minion):
	Class, race, name = "Neutral", "", "Wolfrider"
	mana, attack, health = 3, 3, 1
	index = "Basic~Neutral~Minion~3~3~1~~Wolfrider~Charge"
	requireTarget, keyWord, description = False, "Charge", "Charge"
	name_CN = "狼骑兵"
	
"""Mana 4 minions"""
class ChillwindYeti(Minion):
	Class, race, name = "Neutral", "", "Chillwind Yeti"
	mana, attack, health = 4, 4, 5
	index = "Basic~Neutral~Minion~4~4~5~~Chillwind Yeti"
	requireTarget, keyWord, description = False, "", ""
	name_CN = "冰风雪人"
	
	
class DragonlingMechanic(Minion):
	Class, race, name = "Neutral", "", "Dragonling Mechanic"
	mana, attack, health = 4, 2, 4
	index = "Basic~Neutral~Minion~4~2~4~~Dragonling Mechanic~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Summon a 2/1 Mechanical Dragonling"
	name_CN = "机械幼龙 技工"
	
	#If returned to hand, will summon to the rightend of the board.
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.Game.summon(MechanicalDragonling(self.Game, self.ID), self.pos+1, self.ID)
		return None
		
class MechanicalDragonling(Minion):
	Class, race, name = "Neutral", "Mech", "Mechanical Dragonling"
	mana, attack, health = 1, 2, 1
	index = "Basic~Neutral~Minion~1~2~1~Mech~Mechanical Dragonling~Uncollectible"
	requireTarget, keyWord, description = False, "", ""
	name_CN = "机械幼龙"
	
	
class GnomishInventor(Minion):
	Class, race, name = "Neutral", "", "Gnomish Inventor"
	mana, attack, health = 4, 2, 4
	index = "Basic~Neutral~Minion~4~2~4~~Gnomish Inventor~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Draw a card"
	name_CN = "侏儒发明家"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.Game.Hand_Deck.drawCard(self.ID)
		return None
		
		
class OasisSnapjaw(Minion):
	Class, race, name = "Neutral", "Beast", "Oasis Snapjaw"
	mana, attack, health = 4, 2, 7
	index = "Basic~Neutral~Minion~4~2~7~Beast~Oasis Snapjaw"
	requireTarget, keyWord, description = False, "", ""
	name_CN = "绿洲钳嘴龟"
	
	
class OgreMagi(Minion):
	Class, race, name = "Neutral", "", "Ogre Magi"
	mana, attack, health = 4, 4, 4
	index = "Basic~Neutral~Minion~4~4~4~~Ogre Magi~Spell Damage"
	requireTarget, keyWord, description = False, "Spell Damage", "Spell Damage +1"
	name_CN = "食人魔法师"
	
	
class SenjinShieldmasta(Minion):
	Class, race, name = "Neutral", "", "Sen'jin Shieldmasta"
	mana, attack, health = 4, 3, 5
	index = "Basic~Neutral~Minion~4~3~5~~Sen'jin Shieldmasta~Taunt"
	requireTarget, keyWord, description = False, "Taunt", "Taunt"
	name_CN = "森金持盾卫士"
	
	
class StormwindKnight(Minion):
	Class, race, name = "Neutral", "", "Stormwind Knight"
	mana, attack, health = 4, 2, 5
	index = "Basic~Neutral~Minion~4~2~5~~Stormwind Knight~Charge"
	requireTarget, keyWord, description = False, "Charge", "Charge"
	name_CN = "暴风城骑士"
	
"""Mana 5 minions"""
class BootyBayBodyguard(Minion):
	Class, race, name = "Neutral", "", "Booty Bay Bodyguard"
	mana, attack, health = 5, 5, 4
	index = "Basic~Neutral~Minion~5~5~4~~Booty Bay Bodyguard~Taunt"
	requireTarget, keyWord, description = False, "Taunt", "Taunt"
	name_CN = "藏宝海湾保镖"
	
	
class DarkscaleHealer(Minion):
	Class, race, name = "Neutral", "", "Darkscale Healer"
	mana, attack, health = 5, 4, 5
	index = "Basic~Neutral~Minion~5~4~5~~Darkscale Healer~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Restore 2 health to all friendly characters"
	name_CN = "暗鳞治愈者"
	
	def text(self, CHN):
		heal = 2 * (2 ** self.countHealDouble())
		return "战吼：为所有友方角色恢复%d生命值"%heal if CHN else "Battlecry: Restore %d health to all friendly characters"%heal
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		heal = 2 * (2 ** self.countHealDouble())
		targets = [self.Game.heroes[self.ID]] + self.Game.minionsonBoard(self.ID)
		self.restoresAOE(targets, [heal for obj in targets])
		return None
		
		
class FrostwolfWarlord(Minion):
	Class, race, name = "Neutral", "", "Frostwolf Warlord"
	mana, attack, health = 5, 4, 4
	index = "Basic~Neutral~Minion~5~4~4~~Frostwolf Warlord~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Gain +1/+1 for each other friendly minion on the battlefield"
	name_CN = "霜狼督军"
	
	#For self buffing effects, being dead and removed before battlecry will prevent the battlecry resolution.
	#If this minion is returned hand before battlecry, it can still buff it self according to living friendly minions.
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if self.onBoard or self.inHand: #For now, no battlecry resolution shuffles this into deck.
			num = len(self.Game.minionsAlive(self.ID, self))
			self.buffDebuff(num, num)
		return None
		
#When takes damage in hand(Illidan/Juggler/Anub'ar Ambusher), won't trigger the +3 Attack buff.
class GurubashiBerserker(Minion):
	Class, race, name = "Neutral", "", "Gurubashi Berserker"
	mana, attack, health = 5, 2, 8
	index = "Basic~Neutral~Minion~5~2~8~~Gurubashi Berserker"
	requireTarget, keyWord, description = False, "", "Whenever this minion takes damage, gain +3 Attack"
	name_CN = "古拉巴什 狂暴者"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_GurubashiBerserker(self)]
		
class Trig_GurubashiBerserker(TrigBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionTakesDmg"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return target == self.entity and self.entity.onBoard
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.buffDebuff(3, 0)
		
	def text(self, CHN):
		return "每当该随从受到伤害，便获得+3攻击力" if CHN else "Whenever this minion takes damage, gain +3 Attack"
		
		
class Nightblade(Minion):
	Class, race, name = "Neutral", "", "Nightblade"
	mana, attack, health = 5, 4, 4
	index = "Basic~Neutral~Minion~5~4~4~~Nightblade~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Deal 3 damage to the enemy hero"
	name_CN = "夜刃刺客"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.dealsDamage(self.Game.heroes[3-self.ID], 3)
		return None
		
		
class StormpikeCommando(Minion):
	Class, race, name = "Neutral", "", "Stormpike Commando"
	mana, attack, health = 5, 4, 2
	index = "Basic~Neutral~Minion~5~4~2~~Stormpike Commando~Battlecry"
	requireTarget, keyWord, description = True, "", "Battlecry: Deal 2 damage"
	name_CN = "雷矛特种兵"
	#Infer from Fire Plume Phoenix
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			self.dealsDamage(target, 2)
		return target
		
"""Mana 6 minions"""
class LordoftheArena(Minion):
	Class, race, name = "Neutral", "", "Lord of the Arena"
	mana, attack, health = 6, 6, 5
	index = "Basic~Neutral~Minion~6~6~5~~Lord of the Arena~Taunt"
	requireTarget, keyWord, description = False, "Taunt", "Taunt"
	name_CN = "竞技场领主"
	
	
class Archmage(Minion):
	Class, race, name = "Neutral", "", "Archmage"
	mana, attack, health = 6, 4, 7
	index = "Basic~Neutral~Minion~6~4~7~~Archmage~Spell Damage"
	requireTarget, keyWord, description = False, "Spell Damage", "Spell Damage +1"
	name_CN = "大法师"
	
	
class BoulderfistOgre(Minion):
	Class, race, name = "Neutral", "", "Boulderfist Ogre"
	mana, attack, health = 6, 6, 7
	index = "Basic~Neutral~Minion~6~6~7~~Boulderfist Ogre"
	requireTarget, keyWord, description = False, "", ""
	name_CN = "石拳食人魔"
	
	
class RecklessRocketeer(Minion):
	Class, race, name = "Neutral", "", "Reckless Rocketeer"
	mana, attack, health = 6, 5, 2
	index = "Basic~Neutral~Minion~6~5~2~~Reckless Rocketeer~Charge"
	requireTarget, keyWord, description = False, "Charge", "Charge"
	name_CN = "鲁莽火箭兵"
	
"""Mana 7 minions"""
class CoreHound(Minion):
	Class, race, name = "Neutral", "Beast", "Core Hound"
	mana, attack, health = 7, 9, 5
	index = "Basic~Neutral~Minion~7~9~5~Beast~Core Hound"
	requireTarget, keyWord, description = False, "", ""
	name_CN = "熔火恶犬"
	
	
class StormwindChampion(Minion):
	Class, race, name = "Neutral", "", "Stormwind Champion"
	mana, attack, health = 7, 6, 6
	index = "Basic~Neutral~Minion~7~6~6~~Stormwind Champion"
	requireTarget, keyWord, description = False, "", "Your other minions have +1/+1"
	name_CN = "暴风城勇士"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.auras["Your other minions have +1/+1"] = StatAura_Others(self, 1, 1)
		
		
class WarGolem(Minion):
	Class, race, name = "Neutral", "", "War Golem"
	mana, attack, health = 7, 7, 7
	index = "Basic~Neutral~Minion~7~7~7~~War Golem"
	requireTarget, keyWord, description = False, "", ""
	name_CN = "战争傀儡"
	
"""Demon Hunter cards"""
class ShadowhoofSlayer(Minion):
	Class, race, name = "Demon Hunter", "Demon", "Shadowhoof Slayer"
	mana, attack, health = 1, 2, 1
	index = "Basic~Demon Hunter~Minion~1~2~1~Demon~Shadowhoof Slayer~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Give your hero +1 Attack this turn"
	name_CN = "影蹄杀手"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.Game.heroes[self.ID].gainAttack(1)
		return None
		
		
class ChaosStrike(Spell):
	Class, school, name = "Demon Hunter", "", "Chaos Strike"
	requireTarget, mana = False, 2
	index = "Basic~Demon Hunter~Spell~2~Chaos Strike"
	description = "Give your hero +2 Attack this turn. Draw a card"
	name_CN = "混乱打击"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.Game.heroes[self.ID].gainAttack(2)
		self.Game.Hand_Deck.drawCard(self.ID)
		return None
		
		
class SightlessWatcher(Minion):
	Class, race, name = "Demon Hunter", "Demon", "Sightless Watcher"
	mana, attack, health = 2, 3, 2
	index = "Basic~Demon Hunter~Minion~2~3~2~Demon~Sightless Watcher~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Look at 3 cards in your deck. Choose one to put on top"
	name_CN = "盲眼观察者"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		ownDeck = curGame.Hand_Deck.decks[self.ID]
		if curGame.turn == self.ID and ownDeck:
			if curGame.mode == 0:
				if curGame.guides:
					ownDeck.append(ownDeck.pop(curGame.guides.pop(0)))
				else:
					if "byOthers" in comment:
						i = nprandint(len(ownDeck))
						curGame.fixedGuides.append(i)
						ownDeck.append(ownDeck.pop(i))
					else:
						curGame.options = npchoice(ownDeck, min(3, len(ownDeck)), replace=False)
						curGame.Discover.startDiscover(self)
		return None
		
	def discoverDecided(self, option, pool):
		ownDeck = self.Game.Hand_Deck.decks[self.ID]
		i = ownDeck.index(option)
		self.Game.fixedGuides.append(i)
		ownDeck.append(ownDeck.pop(i))
		
		
class AldrachiWarblades(Weapon):
	Class, name, description = "Demon Hunter", "Aldrachi Warblades", "Lifesteal"
	mana, attack, durability = 3, 2, 2
	index = "Basic~Demon Hunter~Weapon~3~2~2~Aldrachi Warblades~Lifesteal"
	name_CN = "奥达奇战刃"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.keyWords["Lifesteal"] = 1
		
		
class CoordinatedStrike(Spell):
	Class, school, name = "Demon Hunter", "", "Coordinated Strike"
	requireTarget, mana = False, 3
	index = "Basic~Demon Hunter~Spell~3~Coordinated Strike"
	description = "Summon three 1/1 Illidari with Rush"
	name_CN = "协同打击"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.Game.summon([IllidariInitiate(self.Game, self.ID) for i in range(3)], (-1, "totheRightEnd"), self.ID)
		return None
		
class IllidariInitiate(Minion):
	Class, race, name = "Demon Hunter", "", "Illidari Initiate"
	mana, attack, health = 1, 1, 1
	index = "Basic~Demon Hunter~Minion~1~1~1~~Illidari Initiate~Rush~Uncollectible"
	requireTarget, keyWord, description = False, "Rush", "Rush"
	name_CN = "伊利达雷 新兵"
	
class SatyrOverseer(Minion):
	Class, race, name = "Demon Hunter", "Demon", "Satyr Overseer"
	mana, attack, health = 3, 4, 2
	index = "Basic~Demon Hunter~Minion~3~4~2~Demon~Satyr Overseer"
	requireTarget, keyWord, description = False, "", "After your hero attacks, summon a 2/2 Satyr"
	name_CN = "萨特监工"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_SatyrOverseer(self)]
		
class Trig_SatyrOverseer(TrigBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["HeroAttackedMinion", "HeroAttackedHero"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject == self.entity.Game.heroes[self.entity.ID]
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.Game.summon(IllidariSatyr(self.entity.Game, self.entity.ID), self.entity.pos+1, self.entity.ID)
		
	def text(self, CHN):
		return "在你的英雄攻击后，召唤一个2/2的萨特" if CHN else "After your hero attacks, summon a 2/2 Satyr"
		
class IllidariSatyr(Minion):
	Class, race, name = "Demon Hunter", "Demon", "Illidari Satyr"
	mana, attack, health = 2, 2, 2
	index = "Basic~Demon Hunter~Minion~2~2~2~Demon~Illidari Satyr~Uncollectible"
	requireTarget, keyWord, description = False, "", ""
	name_CN = "伊利达雷萨特"
	
	
class SoulCleave(Spell):
	Class, school, name = "Demon Hunter", "", "Soul Cleave"
	requireTarget, mana = False, 3
	index = "Basic~Demon Hunter~Spell~3~Soul Cleave"
	description = "Lifesteal. Deal 2 damage to two random enemy minions"
	name_CN = "灵魂裂劈"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.keyWords["Lifesteal"] = 1
		
	def text(self, CHN):
		damage = (2 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		return "吸血。对两个随机敌方随从造成%d点伤害"%damage if CHN else "Lifesteal. Deal %d damage to two random enemy minions"%damage
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		damage = (2 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		curGame = self.Game
		minions = curGame.minionsAlive(3-self.ID)
		if minions:
			if curGame.mode == 0:
				if curGame.guides:
					minions = [curGame.minions[3-self.ID][i] for i in curGame.guides.pop(0)]
				else:
					minions = list(npchoice(minions, min(2, len(minions)), replace=False))
					curGame.fixedGuides.append(tuple([minion.pos for minion in minions]))
				self.dealsAOE(minions, [damage]*len(minions))
		return None
		
		
class ChaosNova(Spell):
	Class, school, name = "Demon Hunter", "", "Chaos Nova"
	requireTarget, mana = False, 5
	index = "Basic~Demon Hunter~Spell~5~Chaos Nova"
	description = "Deal 4 damage to all minions"
	name_CN = "混乱新星"
	def text(self, CHN):
		damage = (4 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		return "对所有随从造成%d点伤害"%damage if CHN else "Deal %d damage to all minions"%damage
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		damage = (4 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		targets = self.Game.minionsonBoard(1) + self.Game.minionsonBoard(2)
		self.dealsAOE(targets, [damage for obj in targets])
		return None
		
		
class GlaiveboundAdept(Minion):
	Class, race, name = "Demon Hunter", "", "Glaivebound Adept"
	mana, attack, health = 5, 6, 4
	index = "Basic~Demon Hunter~Minion~5~6~4~~Glaivebound Adept~Battlecry"
	requireTarget, keyWord, description = True, "", "Battlecry: If your hero attacked this turn, deal 4 damage"
	name_CN = "刃缚精锐"
	
	def effCanTrig(self):
		self.effectViable = self.Game.Counters.heroAttackTimesThisTurn[self.ID] > 0
		
	def returnTrue(self, choice=0):
		return self.Game.Counters.heroAttackTimesThisTurn[self.ID] > 0
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target and self.Game.Counters.heroAttackTimesThisTurn[self.ID] > 0:
			self.dealsDamage(target, 4)
		return target
		
		
class InnerDemon(Spell):
	Class, school, name = "Demon Hunter", "", "Inner Demon"
	requireTarget, mana = False, 8
	index = "Basic~Demon Hunter~Spell~8~Inner Demon"
	description = "Give your hero +8 Attack this turn"
	name_CN = "心中的恶魔"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.Game.heroes[self.ID].gainAttack(8)
		return None
		
"""Druid cards"""
class Innervate(Spell):
	Class, school, name = "Druid", "", "Innervate"
	requireTarget, mana = False, 0
	index = "Basic~Druid~Spell~0~Innervate"
	description = "Gain 1 Mana Crystal this turn only"
	name_CN = "激活"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if self.Game.Manas.manas[self.ID] < 10:
			self.Game.Manas.manas[self.ID] += 1
		return None
		
		
class Moonfire(Spell):
	Class, school, name = "Druid", "", "Moonfire"
	requireTarget, mana = True, 0
	index = "Basic~Druid~Spell~0~Moonfire"
	description = "Deal 1 damage"
	name_CN = "月火术"
	def text(self, CHN):
		damage = (1 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		return "造成%d点伤害"%damage if CHN else "Deal %d damage"%damage
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			damage = (1 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			self.dealsDamage(target, damage)
		return target
		
		
class Claw(Spell):
	Class, school, name = "Druid", "", "Claw"
	requireTarget, mana = False, 1
	index = "Basic~Druid~Spell~1~Claw"
	description = "Give your hero +2 Attack this turn. Gain 2 Armor"
	name_CN = "爪击"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.Game.heroes[self.ID].gainAttack(2)
		self.Game.heroes[self.ID].gainsArmor(2)
		return None
		
		
class MarkoftheWild(Spell):
	Class, school, name = "Druid", "", "Mark of the Wild"
	requireTarget, mana = True, 2
	index = "Basic~Druid~Spell~2~Mark of the Wild"
	description = "Give a minion +2/+2 ant Taunt"
	name_CN = "野性印记"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		if target.type == "Minion" and target.onBoard:
			return True
		return False
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			target.buffDebuff(2, 2) #buffDebuff() and getsKeyword() will check if the minion is onBoard or inHand.
			target.getsKeyword("Taunt")
		return target
		
		
class HealingTouch(Spell):
	Class, school, name = "Druid", "", "Healing Touch"
	requireTarget, mana = True, 3
	index = "Basic~Druid~Spell~3~Healing Touch"
	description = "Restore 8 health"
	name_CN = "治疗之触"
	def text(self, CHN):
		heal = 8 * (2 ** self.countHealDouble())
		return "恢复%d点生命值"%heal if CHN else "Restore %d health"%heal
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			heal = 8 * (2 ** self.countHealDouble())
			self.restoresHealth(target, heal)
		return target
		
		
class SavageRoar(Spell):
	Class, school, name = "Druid", "", "Savage Roar"
	requireTarget, mana = False, 3
	index = "Basic~Druid~Spell~3~Savage Roar"
	description = "Give your characters +2 Attack this turn"
	name_CN = "野蛮咆哮"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.Game.heroes[self.ID].gainAttack(2)
		for minion in self.Game.minionsonBoard(self.ID):
			minion.buffDebuff(2, 0, "EndofTurn")
		return None
		
		
class WildGrowth(Spell):
	Class, school, name = "Druid", "", "Wild Growth"
	requireTarget, mana = False, 3
	index = "Basic~Druid~Spell~3~Wild Growth"
	description = "Gain an empty Mana Crystal"
	name_CN = "野性生长"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if self.Game.Manas.gainEmptyManaCrystal(1, self.ID) == False:
			self.Game.Hand_Deck.addCardtoHand(ExcessMana(self.Game, self.ID), self.ID, creator=type(self))
		return None
		
class ExcessMana(Spell):
	Class, school, name = "Druid", "", "Excess Mana"
	requireTarget, mana = False, 0
	index = "Basic~Druid~Spell~0~Excess Mana~Uncollectible"
	description = "Draw a card"
	name_CN = "法力过剩"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.Game.Hand_Deck.drawCard(self.ID)
		return None
		
		
class Swipe(Spell):
	Class, school, name = "Druid", "", "Swipe"
	requireTarget, mana = True, 4
	index = "Basic~Druid~Spell~4~Swipe"
	description = "Deal 4 damage to an enemy and 1 damage to all other enemies"
	name_CN = "横扫"
	def available(self):
		return self.selectableEnemyExists()
		
	def targetCorrect(self, target, choice=0):
		return (target.type == "Minion" or target.type == "Hero") and target.ID != self.ID and target.onBoard
		
	def text(self, CHN):
		AOEdamage = (1 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		targetdamage = (4 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		return "对一个敌人造成%d点伤害，并对所有其他敌人造成%d点伤害"%(targetdamage, AOEdamage) if CHN \
				else "Deal %d damage to an enemy and %d damage to all other enemies"%(targetdamage, AOEdamage)
				
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			AOEdamage = (1 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			targetdamage = (4 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			targets = [self.Game.heroes[3-self.ID]] + self.Game.minionsonBoard(3-self.ID)
			try: targets.remove(target)
			except: pass
			if targets:
				self.dealsAOE([target]+targets, [targetdamage]+[AOEdamage for obj in targets])
			else:
				self.dealsDamage(target, targetdamage)
		return target
		
		
class Starfire(Spell):
	Class, school, name = "Druid", "", "Starfire"
	requireTarget, mana = True, 6
	index = "Basic~Druid~Spell~6~Starfire"
	description = "Deal 5 damage. Draw a card"
	name_CN = "星火术"
	def text(self, CHN):
		damage = (5 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		return "造成%d点伤害，抽一张牌"%damage if CHN else "Deal %d damage. Draw a card"%damage
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			damage = (5 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			self.dealsDamage(target, damage)
		self.Game.Hand_Deck.drawCard(self.ID)
		return target
		
		
class IronbarkProtector(Minion):
	Class, race, name = "Druid", "", "Ironbark Protector"
	mana, attack, health = 8, 8, 8
	index = "Basic~Druid~Minion~8~8~8~~Ironbark Protector~Taunt"
	requireTarget, keyWord, description = False, "Taunt", "Taunt"
	name_CN = "埃隆巴克 保护者"
	
"""Hunter Cards"""
class ArcaneShot(Spell):
	Class, school, name = "Hunter", "", "Arcane Shot"
	requireTarget, mana = True, 1
	index = "Basic~Hunter~Spell~1~Arcane Shot"
	description = "Deal 2 damage"
	name_CN = "奥术射击"
	def text(self, CHN):
		damage = (2 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		return "造成%d点伤害"%damage if CHN else "Deal %d damage"%damage
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			damage = (2 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			self.dealsDamage(target, damage)
		return target
		
		
class TimberWolf(Minion):
	Class, race, name = "Hunter", "Beast", "Timber Wolf"
	mana, attack, health = 1, 1, 1
	index = "Basic~Hunter~Minion~1~1~1~Beast~Timber Wolf"
	requireTarget, keyWord, description = False, "", "Your other Beasts have +1 Attack"
	name_CN = "森林狼"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.auras["Your other Beasts have +1 Attack"] = StatAura_Others(self, 1, 0)
		
	def applicable(self, target):
		return "Beast" in target.race
		
#In real game, when there is only one card left in deck,
# player still needs to choose, despite only one option available.
class Tracking(Spell):
	Class, school, name = "Hunter", "", "Tracking"
	requireTarget, mana = False, 1
	index = "Basic~Hunter~Spell~1~Tracking"
	description = "Look at the top 3 cards of your deck. Draw one and discard the others."
	name_CN = "追踪术"
	def draw1DitchOthers(self, info):
		indextoDraw, indstoDis = info[0], info[1]
		if isinstance(indstoDis, (int, np.int32, np.int64)): #
			if indstoDis < indextoDraw: indextoDraw -= 1
			self.Game.Hand_Deck.extractfromDeck(indstoDis, self.ID)
			self.Game.Hand_Deck.drawCard(self.ID, indextoDraw)
		else: #这个函数可以适用于-1, (-3, -2)
			indstoDis = indstoDis[::-1] #把序号变为从大到小
			#例如26, (25, 24). 只要首个比26小，则后面那个即使有26减少1，仍然会比25小
			if indextoDraw > -1:
				for i in indstoDis:
					if i < indextoDraw: indextoDraw -= 1
				for i in indstoDis: self.Game.Hand_Deck.extractfromDeck(i, self.ID) #这个indstoDis是序号从小到大排列好的
				self.Game.Hand_Deck.drawCard(self.ID, indextoDraw)
			else: #如果info是-1, (-3, -2)
				for i in indstoDis: self.Game.Hand_Deck.extractfromDeck(i, self.ID) #这个indstoDis是序号从小到大排列好的
				self.Game.Hand_Deck.drawCard(self.ID)
				
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		numCardsLeft = len(curGame.Hand_Deck.decks[self.ID])
		if numCardsLeft == 1:
			curGame.Hand_Deck.drawCard(self.ID)
		elif numCardsLeft > 1:
			if curGame.mode == 0:
				if curGame.guides:
					Tracking.draw1DitchOthers(self, curGame.guides.pop(0))
				else:
					num = min(3, numCardsLeft)
					indices = [numCardsLeft-3, numCardsLeft-2, numCardsLeft-1] if num == 3 else [numCardsLeft-2, numCardsLeft-1]
					if self.ID != curGame.turn or "byOthers" in comment:
						index = indices.pop(nprandint(num))
						info = (index, tuple(indices))
						curGame.fixedGuides.append(info)
						Tracking.draw1DitchOthers(self, info)
					else:
						cards = [curGame.Hand_Deck.decks[self.ID][i] for i in indices]
						curGame.options = cards
						curGame.Discover.startDiscover(self, indices)
		return None
		
	#产生选择选项的时候是牌库顶的牌在最选项的最左面
	def discoverDecided(self, option, pool):
		i = self.Game.options.index(option)
		index = pool.pop(i)
		info = (index, tuple(pool))
		self.Game.fixedGuides.append(info)
		Tracking.draw1DitchOthers(self, info)
		
		
class HuntersMark(Spell):
	Class, school, name = "Hunter", "", "Hunter's Mark"
	requireTarget, mana = True, 2
	index = "Basic~Hunter~Spell~2~Hunter's Mark"
	description = "Change a minion's health to 1"
	name_CN = "猎人印记"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		if target.type == "Minion" and target.onBoard:
			return True
		return False
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			target.statReset(False, 1)
		return target
		
class AnimalCompanion(Spell):
	Class, school, name = "Hunter", "", "Animal Companion"
	requireTarget, mana = False, 3
	index = "Basic~Hunter~Spell~3~Animal Companion"
	description = "Summon a random Beast Companion"
	name_CN = "动物伙伴"
	def available(self):
		return self.Game.space(self.ID) > 0
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if curGame.space(self.ID) > 0:
			if curGame.mode == 0:
				if curGame.guides:
					companion = curGame.guides.pop(0)
				else:
					companion = npchoice([Huffer, Leokk, Misha])
					curGame.fixedGuides.append(companion)
				curGame.summon(companion(curGame, self.ID), -1, self.ID)
		return None
		
class Huffer(Minion):
	Class, race, name = "Hunter", "Beast", "Huffer"
	mana, attack, health = 3, 4, 2
	index = "Basic~Hunter~Minion~3~4~2~Beast~Huffer~Charge~Uncollectible"
	requireTarget, keyWord, description = False, "Charge", "Charge"
	name_CN = "霍弗"
	
class Leokk(Minion):
	Class, race, name = "Hunter", "Beast", "Leokk"
	mana, attack, health = 3, 2, 4
	index = "Basic~Hunter~Minion~3~2~4~Beast~Leokk~Uncollectible"
	requireTarget, keyWord, description = False, "", "Your other minions have +1 Attack"
	name_CN = "雷欧克"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.auras["Your other minions have +1 Attack"] = StatAura_Others(self, 1, 0)
		
class Misha(Minion):
	Class, race, name = "Hunter", "Beast", "Misha"
	mana, attack, health = 3, 4, 4
	index = "Basic~Hunter~Minion~3~4~4~Beast~Misha~Taunt~Uncollectible"
	requireTarget, keyWord, description = False, "Taunt", "Taunt"
	name_CN = "米莎"
	
	
class KillCommand(Spell):
	Class, school, name = "Hunter", "", "Kill Command"
	requireTarget, mana = True, 3
	index = "Basic~Hunter~Spell~3~Kill Command"
	description = "Deal 3 damage. If you control a Beast, deal 5 damage instead"
	name_CN = "杀戮指令"
	def effCanTrig(self):
		return any("Beast" in minion.race for minion in self.Game.minionsonBoard(self.ID))
		
	def text(self, CHN):
		damage_3 = (3 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		damage_5 = (5 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		return "造成%d点伤害。如果你控制一个野兽，则改为造成%d点伤害"%(damage_3, damage_5) if CHN else "Deal %d damage. If you control a Beast, deal %d damage instead"%(damage_3, damage_5)
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			base = 3 + 2 * any("Beast" in minion.race for minion in self.Game.minionsonBoard(self.ID))
			damage = (base + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			self.dealsDamage(target, damage)
		return target
		
		
class Houndmaster(Minion):
	Class, race, name = "Hunter", "", "Houndmaster"
	mana, attack, health = 4, 4, 3
	index = "Basic~Hunter~Minion~4~4~3~~Houndmaster~Battlecry"
	requireTarget, keyWord, description = True, "", "Battlecry: Give a friendly Beast +2/+2 and Taunt"
	name_CN = "驯兽师"
	
	def targetExists(self, choice=0):
		return self.selectableFriendlyMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.ID == self.ID and "Beast" in target.race and target != self and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			target.buffDebuff(2, 2)
			target.getsKeyword("Taunt")
		return target
		
		
class MultiShot(Spell):
	Class, school, name = "Hunter", "", "Multi-Shot"
	requireTarget, mana = False, 4
	index = "Basic~Hunter~Spell~4~Multi-Shot"
	description = "Deal 3 damage to two random enemy minions"
	name_CN = "多重射击"
	def available(self):
		return self.Game.minionsonBoard(3-self.ID) != []
		
	def text(self, CHN):
		damage = (3 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		return "对两个随机敌方随从造成%d点伤害"%damage if CHN else "Deal %d damage to two random enemy minions"%damage
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		damage = (3 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		curGame = self.Game
		minions = curGame.minionsAlive(3-self.ID)
		if minions:
			if curGame.mode == 0:
				if curGame.guides:
					minions = [curGame.minions[3-self.ID][i] for i in curGame.guides.pop(0)]
				else:
					minions = list(npchoice(minions, min(2, len(minions)), replace=False))
					curGame.fixedGuides.append(tuple([minion.pos for minion in minions]))
				self.dealsAOE(minions, [damage]*len(minions))
		return None
		
		
class StarvingBuzzard(Minion):
	Class, race, name = "Hunter", "Beast", "Starving Buzzard"
	mana, attack, health = 5, 3, 2
	index = "Basic~Hunter~Minion~5~3~2~Beast~Starving Buzzard"
	requireTarget, keyWord, description = False, "", "Whenever you summon a Beast, draw a card"
	name_CN = "饥饿的秃鹫"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_StarvingBuzzard(self)]
		
class Trig_StarvingBuzzard(TrigBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionSummoned"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and self.entity.health > 0 and subject.ID == self.entity.ID and "Beast" in subject.race and subject != self.entity
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.Game.Hand_Deck.drawCard(self.entity.ID)
		
	def text(self, CHN):
		return "每当你召唤一个野兽，抽一张牌" if CHN else "Whenever you summon a Beast, draw a card"
		
class TundraRhino(Minion):
	Class, race, name = "Hunter", "Beast", "Tundra Rhino"
	mana, attack, health = 5, 2, 5
	index = "Basic~Hunter~Minion~5~2~5~Beast~Tundra Rhino"
	requireTarget, keyWord, description = False, "", "Your Beasts have Charge"
	name_CN = "苔原犀牛"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.auras["Your Beasts have Charge"] = EffectAura(self, "Charge")
		
	def applicable(self, target):
		return "Beast" in target.race
		
"""Mage cards"""
class ArcaneMissiles(Spell):
	Class, school, name = "Mage", "", "Arcane Missiles"
	requireTarget, mana = False, 1
	index = "Basic~Mage~Spell~1~Arcane Missiles"
	description = "Deal 3 damage randomly split among all enemies"
	name_CN = "奥术飞弹"
	def text(self, CHN):
		damage = (3 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		return "造成%d点伤害，随机分配到所有敌人身上"%damage if CHN else "Deal %d damage randomly split among all enemies"%damage
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		damage = (3 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		side, curGame = 3-self.ID, self.Game
		if curGame.mode == 0:
			for num in range(damage):
				char = None
				if curGame.guides:
					i, where = curGame.guides.pop(0)
					if where: char = curGame.find(i, where)
				else:
					objs = curGame.charsAlive(side)
					if objs:
						char = npchoice(objs)
						curGame.fixedGuides.append((char.pos, char.type+str(char.ID)))
					else:
						curGame.fixedGuides.append((0, ''))
				if char:
					self.dealsDamage(char, 1)
				else: break
		return None
		
		
class MirrorImage(Spell):
	Class, school, name = "Mage", "", "Mirror Image"
	requireTarget, mana = False, 1
	index = "Basic~Mage~Spell~1~Mirror Image"
	description = "Summon two 0/2 minions with Taunt"
	name_CN = "镜像"
	def available(self):
		return self.Game.space(self.ID) > 0
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.Game.summon([MirrorImage_Minion(self.Game, self.ID) for i in range(2)], (-1, "totheRightEnd"), self.ID)
		return None
		
class MirrorImage_Minion(Minion):
	Class, race, name = "Mage", "", "Mirror Image"
	mana, attack, health = 0, 0, 2
	index = "Basic~Mage~Minion~0~0~2~~Mirror Image~Taunt~Uncollectible"
	requireTarget, keyWord, description = False, "Taunt", "Taunt"
	name_CN = "镜像"
	
	
class ArcaneExplosion(Spell):
	Class, school, name = "Mage", "", "Arcane Explosion"
	requireTarget, mana = False, 2
	index = "Basic~Mage~Spell~2~Arcane Explosion"
	description = "Deal 1 damage to all enemy minions"
	name_CN = "魔爆术"
	def text(self, CHN):
		damage = (1 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		return "对所有敌方随从造成%d点伤害"%damage if CHN else "Deal %d damage to all enemy minions"%damage
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		damage = (1 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		targets = self.Game.minionsonBoard(3-self.ID)
		self.dealsAOE(targets, [damage for obj in targets])
		return None
		
		
class Frostbolt(Spell):
	Class, school, name = "Mage", "", "Frostbolt"
	requireTarget, mana = True, 2
	index = "Basic~Mage~Spell~2~Frostbolt"
	description = "Deal 3 damage to a character and Freeze it"
	name_CN = "寒冰箭"
	def text(self, CHN):
		damage = (3 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		return "对一个角色造成%d点伤害，并使其冻结"%damage if CHN else "Deal %d damage to a character and Freeze it"%damage
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			damage = (3 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			self.dealsDamage(target, damage)
			target.getsFrozen()
		return target
		
		
class ArcaneIntellect(Spell):
	Class, school, name = "Mage", "", "Arcane Intellect"
	requireTarget, mana = False, 3
	index = "Basic~Mage~Spell~3~Arcane Intellect"
	description = "Draw 2 cards"
	name_CN = "奥术智慧"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.Game.Hand_Deck.drawCard(self.ID)
		self.Game.Hand_Deck.drawCard(self.ID)
		return None
		
		
class FrostNova(Spell):
	Class, school, name = "Mage", "", "Frost Nova"
	requireTarget, mana = False, 3
	index = "Basic~Mage~Spell~3~Frost Nova"
	description = "Freeze all enemy minions"
	name_CN = "霜冻新星"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		#Fix the targets so that minions that resolutions that summon minions due to minion being frozen won't make the list expand.
		for minion in self.Game.minionsonBoard(3-self.ID):
			minion.getsFrozen()
		return None
		
		
class Fireball(Spell):
	Class, school, name = "Mage", "", "Fireball"
	requireTarget, mana = True, 4
	index = "Basic~Mage~Spell~4~Fireball"
	description = "Deal 6 damage"
	name_CN = "火球术"
	def text(self, CHN):
		damage = (6 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		return "造成%d点伤害"%damage if CHN else "Deal %d damage"%damage
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			damage = (6 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			self.dealsDamage(target, damage)
		return target
		
		
class Polymorph(Spell):
	Class, school, name = "Mage", "", "Polymorph"
	requireTarget, mana = True, 4
	index = "Basic~Mage~Spell~4~Polymorph"
	description = "Transform a minion into a 1/1 Sheep"
	name_CN = "变形术"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			newMinion = Sheep(self.Game, target.ID)
			self.Game.transform(target, newMinion)
			target = newMinion
		return target
		
class Sheep(Minion):
	Class, race, name = "Neutral", "Beast", "Sheep"
	mana, attack, health = 1, 1, 1
	index = "Basic~Neutral~Minion~1~1~1~Beast~Sheep~Uncollectible"
	requireTarget, keyWord, description = False, "", ""
	name_CN = "绵羊"
	
	
class WaterElemental(Minion):
	Class, race, name = "Mage", "Elemental", "Water Elemental"
	mana, attack, health = 4, 3, 6
	index = "Basic~Mage~Minion~4~3~6~Elemental~Water Elemental"
	requireTarget, keyWord, description = False, "", "Freeze any character damaged by this minion"
	name_CN = "水元素"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_WaterElemental(self)]
		
class Trig_WaterElemental(TrigBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionTakesDmg", "HeroTakesDmg"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject == self.entity
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		target.getsFrozen()
		
	def text(self, CHN):
		return "冻结任何受到该随从伤害的角色" if CHN else "Freeze any character damaged by this minion"
		
		
class Flamestrike(Spell):
	Class, school, name = "Mage", "", "Flamestrike"
	requireTarget, mana = False, 7
	index = "Basic~Mage~Spell~7~Flamestrike"
	description = "Deal 4 damage to all enemy minions"
	name_CN = "烈焰风暴"
	def text(self, CHN):
		damage = (4 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		return "对所有敌方随从造成%d点伤害"%damage if CHN else "Deal %d damage to all enemy minions"%damage
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		damage = (4 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		targets = self.Game.minionsonBoard(3-self.ID)
		self.dealsAOE(targets, [damage for minion in targets])
		return None
		
		
"""Paladin Cards"""
class BlessingofMight(Spell):
	Class, school, name = "Paladin", "", "Blessing of Might"
	requireTarget, mana = True, 1
	index = "Basic~Paladin~Spell~1~Blessing of Might"
	description = "Give a minion +3 Attack"
	name_CN = "力量祝福"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			target.buffDebuff(3, 0)
		return target
		
		
class HandofProtection(Spell):
	Class, school, name = "Paladin", "", "Hand of Protection"
	requireTarget, mana = True, 1
	index = "Basic~Paladin~Spell~1~Hand of Protection"
	description = "Give a minion Divine Shield"
	name_CN = "保护之手"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			target.getsKeyword("Divine Shield")
		return target
		
		
class Humility(Spell):
	Class, school, name = "Paladin", "", "Humility"
	requireTarget, mana = True, 1
	index = "Basic~Paladin~Spell~1~Humility"
	description = "Change a minion's Attack to 1"
	name_CN = "谦逊"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			target.statReset(1, False)
		return target
		
		
class LightsJustice(Weapon):
	Class, name, description = "Paladin", "Light's Justice", ""
	mana, attack, durability = 1, 1, 4
	index = "Basic~Paladin~Weapon~1~1~4~Light's Justice"
	name_CN = "圣光的正义"
	
	
class HolyLight(Spell):
	Class, school, name = "Paladin", "Holy", "Holy Light"
	requireTarget, mana = True, 2
	index = "Basic~Paladin~Spell~2~Holy~Holy Light"
	description = "Restore 8 health"
	name_CN = "圣光术"
	def text(self, CHN):
		heal = 8 * (2 ** self.countHealDouble())
		return "恢复%d点生命值"%heal if CHN else "Restore %d health"%heal
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			heal = 8 * (2 ** self.countHealDouble())
			self.restoresHealth(target, heal)
		return target
		
		
class BlessingofKings(Spell):
	Class, school, name = "Paladin", "", "Blessing of Kings"
	requireTarget, mana = True, 4
	index = "Basic~Paladin~Spell~4~Blessing of Kings"
	description = "Give a minion +4/+4"
	name_CN = "王者祝福"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			target.buffDebuff(4, 4)
		return target
		
		
class Consecration(Spell):
	Class, school, name = "Paladin", "", "Consecration"
	requireTarget, mana = False, 4
	index = "Basic~Paladin~Spell~4~Consecration"
	description = "Deal 2 damage to all enemies"
	name_CN = "奉献"
	def text(self, CHN):
		damage = (2 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		return "对所有敌人造成%d点伤害"%damage if CHN else "Deal %d damage to all enemies"%damage
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		damage = (2 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		targets = [self.Game.heroes[3-self.ID]] + self.Game.minionsonBoard(3-self.ID)
		self.dealsAOE(targets, [damage for obj in targets])
		return None
		
		
class HammerofWrath(Spell):
	Class, school, name = "Paladin", "", "Hammer of Wrath"
	requireTarget, mana = True, 4
	index = "Basic~Paladin~Spell~4~Hammer of Wrath"
	description = "Deal 3 damage. Draw a card"
	name_CN = "愤怒之锤"
	def text(self, CHN):
		damage = (3 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		return "造成%d点伤害，抽一张牌"%damage if CHN else "Deal %d damage. Draw a card"%damage
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			damage = (3 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			self.dealsDamage(target, damage)
			self.Game.Hand_Deck.drawCard(self.ID)
		return target
		
		
class TruesilverChampion(Weapon):
	Class, name, description = "Paladin", "Truesilver Champion", "Whenever your hero attacks, restore 2 Health to it"
	mana, attack, durability = 4, 4, 2
	index = "Basic~Paladin~Weapon~4~4~2~Truesilver Champion"
	name_CN = "真银圣剑"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_TruesilverChampion(self)]
		
class Trig_TruesilverChampion(TrigBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["HeroAttackingMinion", "HeroAttackingHero"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject == self.entity.Game.heroes[self.entity.ID] and self.entity.onBoard
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		heal = 2 * (2 ** self.entity.countHealDouble())
		self.entity.restoresHealth(self.entity.Game.heroes[self.entity.ID], heal)
		
	def text(self, CHN):
		heal = 2 * (2 ** self.entity.countHealDouble())
		return "每当你的英雄进攻，便为其恢复%d点生命值"%heal if CHN else "Whenever your hero attacks, restore %d Health to it"%heal
		
		
class GuardianofKings(Minion):
	Class, race, name = "Paladin", "", "Guardian of Kings"
	mana, attack, health = 7, 5, 6
	index = "Basic~Paladin~Minion~7~5~6~~Guardian of Kings~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Restore 6 health to your hero"
	name_CN = "列王守卫"
	
	def text(self, CHN):
		heal = 6 * (2 ** self.countHealDouble())
		return "战吼：为你的英雄恢复%d点生命值"%heal if CHN else "Battlecry: Restore %d health to your hero"%heal
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		heal = 6 * (2 ** self.countHealDouble())
		self.restoresHealth(self.Game.heroes[self.ID], heal)
		return None
		
"""Priest Cards"""
class PowerWordShield(Spell):
	Class, school, name = "Priest", "", "Power Word: Shield"
	requireTarget, mana = True, 0
	index = "Basic~Priest~Spell~0~Power Word: Shield"
	description = "Give a minion +2 Health"
	name_CN = "真言术：盾"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			target.buffDebuff(0, 2)
		return target
		
		
class HolySmite(Spell):
	Class, school, name = "Priest", "", "Holy Smite"
	requireTarget, mana = True, 1
	index = "Basic~Priest~Spell~1~Holy Smite"
	description = "Deal 3 damage to a minion"
	name_CN = "神圣惩击"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
		
	def text(self, CHN):
		damage = (3 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		return "对一个随从造成%d点伤害"%damage if CHN else "Deal %d damage to a minion"%damage
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			damage = (3 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			self.dealsDamage(target, damage)
		return target
		
		
class MindVision(Spell):
	Class, school, name = "Priest", "", "Mind Vision"
	requireTarget, mana = False, 1
	index = "Basic~Priest~Spell~1~Mind Vision"
	description = "Put a copy of a random card in your opponent's hand into your hand"
	name_CN = "心灵视界"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		enemyHand = curGame.Hand_Deck.hands[3-self.ID]
		if curGame.mode == 0:
			pool = tuple(type(card) for card in enemyHand)
			if curGame.guides:
				i = curGame.guides.pop(0)
			else:
				i = nprandint(len(enemyHand)) if enemyHand else -1
				curGame.fixedGuides.append(i)
			if i > -1: curGame.Hand_Deck.addCardtoHand(enemyHand[i].selfCopy(self.ID), self.ID, creator=type(self), possi=pool)
		return None
		
		
class PsychicConjurer(Minion):
	Class, race, name = "Priest", "", "Psychic Conjurer"
	mana, attack, health = 1, 1, 1
	index = "Basic~Priest~Minion~1~1~1~~Psychic Conjurer~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Copy a card in your opponent's deck and add it to your hand"
	name_CN = "心灵咒术师"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		enemyDeck = curGame.Hand_Deck.decks[3-self.ID]
		if curGame.mode == 0:
			pool = tuple(possi[1][0] for possi in curGame.Hand_Deck.cards_1Possi[3-self.ID] if len(possi) == 1)
			if curGame.guides:
				i = curGame.guides.pop(0)
			else:
				i = nprandint(len(enemyDeck)) if enemyDeck else -1
				curGame.fixedGuides.append(i)
			if i > -1: curGame.Hand_Deck.addCardtoHand(enemyDeck[i].selfCopy(self.ID), self.ID, creator=type(self), possi=pool)
		return None
		
		
class Radiance(Spell):
	Class, school, name = "Priest", "", "Radiance"
	requireTarget, mana = False, 1
	index = "Basic~Priest~Spell~1~Radiance"
	description = "Restore 5 health to your hero"
	name_CN = "圣光闪耀"
	def text(self, CHN):
		heal = 5 * (2 ** self.countHealDouble())
		return "为你的英雄恢复%d生命值"%heal if CHN else "Restore %d Health to your hero"%heal
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		heal = 5 * (2 ** self.countHealDouble())
		self.restoresHealth(self.Game.heroes[self.ID], heal)
		return None
		
		
class ShadowWordDeath(Spell):
	Class, school, name = "Priest", "", "Shadow Word: Death"
	requireTarget, mana = True, 2
	index = "Basic~Priest~Spell~2~Shadow Word: Death"
	description = "Destroy a minion with 5 or more Attack"
	name_CN = "暗言术：灭"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.attack > 4 and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			self.Game.killMinion(self, target)
		return target
		
		
class ShadowWordPain(Spell):
	Class, school, name = "Priest", "", "Shadow Word: Pain"
	requireTarget, mana = True, 2
	index = "Basic~Priest~Spell~2~Shadow Word: Pain"
	description = "Destroy a minion with 3 or less Attack"
	name_CN = "暗言术：痛"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.attack < 4 and target.onBoard
		
	#Target after returned to hand will be discarded.
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			self.Game.killMinion(self, target)
		return target
		
		
class HolyNova(Spell):
	Class, school, name = "Priest", "Holy", "Holy Nova"
	requireTarget, mana = False, 4
	index = "Basic~Priest~Spell~4~Holy~Holy Nova"
	description = "Deal 2 damage to all enemy minions. Restore 2 Health to all friendly characters"
	name_CN = "神圣新星"
	def text(self, CHN):
		damage = (2 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		heal = 2 * (2 ** self.countHealDouble())
		return "对所有敌方随从造成%d点伤害，为所有友方角色恢复%d生命值"%(damage, heal) if CHN \
				else "Deal %d damage to all enemy minions. Restore %d Health to all friendly characters"%(damage, heal)
				
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		damage = (2 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		heal = 2 * (2 ** self.countHealDouble())
		enemies = self.Game.minionsonBoard(3-self.ID)
		friendlies = [self.Game.heroes[self.ID]] + self.Game.minionsonBoard(self.ID)
		self.dealsAOE(enemies, [damage]*len(enemies))
		self.restoresAOE(friendlies, [heal]*len(friendlies))
		return None
		
class PowerInfusion(Spell):
	Class, school, name = "Priest", "", "Power Infusion"
	requireTarget, mana = True, 4
	index = "Basic~Priest~Spell~4~Power Infusion"
	description = "Give a minion +2/+6"
	name_CN = "能量灌注"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			target.buffDebuff(2, 6)
		return target
		
		
class MindControl(Spell):
	Class, school, name = "Priest", "", "Mind Control"
	requireTarget, mana = True, 10
	index = "Basic~Priest~Spell~10~Mind Control"
	description = "Take control of an enemy minion"
	name_CN = "精神控制"
	def available(self):
		return self.selectableEnemyMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.ID != self.ID and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target and target.ID != self.ID:
			self.Game.minionSwitchSide(target) #minionSwitchSide() will takes care of the case where minion is in hand
		return target
		
"""Rogue Cards"""
class Backstab(Spell):
	Class, school, name = "Rogue", "", "Backstab"
	requireTarget, mana = True, 0
	index = "Basic~Rogue~Spell~0~Backstab"
	description = "Deal 2 damage to an undamage minion"
	name_CN = "背刺"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.health == target.health_max and target.onBoard
		
	def text(self, CHN):
		damage = (2 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		return "对一个未受伤的随从造成%d点伤害"%damage if CHN else "Deal %d damage to an undamage minion"%damage
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			damage = (2 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			self.dealsDamage(target, damage)
		return target
		
		
class WickedKnife(Weapon):
	Class, name, description = "Rogue", "Wicked Knife", ""
	mana, attack, durability = 1, 1, 2
	index = "Basic~Rogue~Weapon~1~1~2~Wicked Knife~Uncollectible"
	name_CN = "邪恶短刀"
	
class PoisonedDagger(Weapon):
	Class, name, description = "Rogue", "Poisoned Dagger", ""
	mana, attack, durability = 1, 2, 2
	index = "Basic~Rogue~Weapon~1~2~2~Poisoned Dagger~Uncollectible"
	name_CN = "浸毒匕首"
	
	
class DeadlyPoison(Spell):
	Class, school, name = "Rogue", "", "Deadly Poison"
	requireTarget, mana = False, 1
	index = "Basic~Rogue~Spell~1~Deadly Poison"
	description = "Give your weapon +2 Attack"
	name_CN = "致命药膏"
	def available(self):
		return self.Game.availableWeapon(self.ID) is not None
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		weapon = self.Game.availableWeapon(self.ID)
		if weapon:
			weapon.gainStat(2, 0)
		return None
		
		
class SinisterStrike(Spell):
	Class, school, name = "Rogue", "", "Sinister Strike"
	requireTarget, mana = False, 1
	index = "Basic~Rogue~Spell~1~Sinister Strike"
	description = "Deal 3 damage to the enemy hero"
	name_CN = "影袭"
	def text(self, CHN):
		damage = (3 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		return "对敌方英雄造成%d点伤害"%damage if CHN else "Deal %d damage to the enemy hero"%damage
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		damage = (3 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		self.dealsDamage(self.Game.heroes[3-self.ID], damage)
		return None
		
		
class Sap(Spell):
	Class, school, name = "Rogue", "", "Sap"
	requireTarget, mana = True, 2
	index = "Basic~Rogue~Spell~2~Sap"
	description = "Return an enemy minion to your opponent's hand"
	name_CN = "闷棍"
	def available(self):
		return self.selectableEnemyMinionExists()
		
	def targetCorrect(self, target, choice=0):
		if target.type == "Minion" and target.ID != self.ID and target.onBoard:
			return True
		return False
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			self.Game.returnMiniontoHand(target)
		return target
		
		
class Shiv(Spell):
	Class, school, name = "Rogue", "", "Shiv"
	requireTarget, mana = True, 2
	index = "Basic~Rogue~Spell~2~Shiv"
	description = "Deal 1 damage. Draw a card"
	name_CN = "毒刃"
	def text(self, CHN):
		damage = (1 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		return "造成%d点伤害，抽一张牌"%damage if CHN else "Deal %d damage. Draw a card"%damage
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			damage = (1 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			self.dealsDamage(target, damage)
		self.Game.Hand_Deck.drawCard(self.ID)
		return target
		
		
class FanofKnives(Spell):
	Class, school, name = "Rogue", "", "Fan of Knives"
	requireTarget, mana = False, 3
	index = "Basic~Rogue~Spell~3~Fan of Knives"
	description = "Deal 1 damage to all enemy minions. Draw a card"
	name_CN = "刀扇"
	def text(self, CHN):
		damage = (1 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		return "对所有敌方随从造成%d点伤害，抽一张牌"%damage if CHN else "Deal %d damage to all enemy minions. Draw a card"%damage
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		damage = (1 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		targets = self.Game.minionsonBoard(3-self.ID)
		self.dealsAOE(targets, [damage for minion in targets])
		self.Game.Hand_Deck.drawCard(self.ID)
		return None
		
		
class Plaguebringer(Minion):
	Class, race, name = "Rogue", "", "Plaguebringer"
	mana, attack, health = 4, 3, 3
	index = "Basic~Rogue~Minion~4~3~3~~Plaguebringer~Battlecry"
	requireTarget, keyWord, description = True, "", "Battlecry: Give a friendly Poisonous"
	name_CN = "瘟疫使者"
	
	def targetExists(self, choice=0):
		return self.selectableFriendlyMinionExists()
		
	def targetCorrect(self, target, choice=0):
		if target.type == "Minion" and target.ID == self.ID and target != self and target.onBoard:
			return True
		return False
		
	#Infer from Windfury: Target when in hand should be able to gets Poisonous and keep it next time it's played.
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			target.getsKeyword("Poisonous")
		return target
		
		
class Assassinate(Spell):
	Class, school, name = "Rogue", "", "Assassinate"
	requireTarget, mana = True, 5
	index = "Basic~Rogue~Spell~5~Assassinate"
	description = "Destroy an enemy minion"
	name_CN = "刺杀"
	def available(self):
		return self.selectableEnemyMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.ID != self.ID and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			self.Game.killMinion(self, target)
		return target
		
		
class AssassinsBlade(Weapon):
	Class, name, description = "Rogue", "Assassin's Blade", ""
	mana, attack, durability = 5, 3, 4
	index = "Basic~Rogue~Weapon~5~3~4~Assassin's Blade"
	name_CN = "刺客之刃"
	
	
class Sprint(Spell):
	Class, school, name = "Rogue", "", "Sprint"
	requireTarget, mana = False, 7
	index = "Basic~Rogue~Spell~7~Sprint"
	description = "Draw 4 cards"
	name_CN = "疾跑"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		for num in range(4):
			self.Game.Hand_Deck.drawCard(self.ID)
		return None
		
"""Shaman Cards"""
class AncestralHealing(Spell):
	Class, school, name = "Shaman", "", "Ancestral Healing"
	requireTarget, mana = True, 0
	index = "Basic~Shaman~Spell~0~Ancestral Healing"
	description = "Restore a minion to full health and give it Taunt"
	name_CN = "先祖治疗"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			self.restoresHealth(target, target.health_max)
		return target
		
		
class TotemicMight(Spell):
	Class, school, name = "Shaman", "", "Totemic Might"
	requireTarget, mana = False, 0
	index = "Basic~Shaman~Spell~0~Totemic Might"
	description = "Give you Totems +2 Health"
	name_CN = "图腾之力"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		for minion in self.Game.minionsonBoard(self.ID):
			if "Totem" in minion.race: minion.buffDebuff(0, 2)
		return None
		
		
class FrostShock(Spell):
	Class, school, name = "Shaman", "", "Frost Shock"
	requireTarget, mana = True, 1
	index = "Basic~Shaman~Spell~1~Frost Shock"
	description = "Deal 1 damage to an enemy character and Freeze it"
	name_CN = "冰霜震击"
	def available(self):
		return self.selectableEnemyExists()
		
	def targetCorrect(self, target, choice=0):
		return (target.type == "Minion" or target.type == "Hero") and target.ID != self.ID and target.onBoard
		
	def text(self, CHN):
		damage = (1 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		return "对一个敌方角色造成%d点伤害，并使其冻结"%damage if CHN else "Deal %d damage to an enemy character and Freeze it"%damage
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			damage = (1 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			self.dealsDamage(target, damage)
			target.getsFrozen()
		return target
		
		
class RockbiterWeapon(Spell):
	Class, school, name = "Shaman", "", "Rockbiter Weapon"
	requireTarget, mana = True, 2
	index = "Basic~Shaman~Spell~2~Rockbiter Weapon"
	description = "Give a friendly character +3 Attack this turn"
	name_CN = "石化武器"
	def available(self):
		return self.selectableFriendlyExists()
		
	def targetCorrect(self, target, choice=0):
		return (target.type == "Minion" or target.type == "Hero") and target.ID == self.ID and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			if target.type == "Hero":
				target.gainAttack(3)
			else:
				target.buffDebuff(3, 0, "EndofTurn")
		return target
		
		
class Windfury(Spell):
	Class, school, name = "Shaman", "Nature", "Windfury"
	requireTarget, mana = True, 2
	index = "Basic~Shaman~Spell~2~Nature~Windfury"
	description = "Give a minion Windfury"
	name_CN = "风怒"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			target.getsKeyword("Windfury")
		return target
		
		
class FlametongueTotem(Minion):
	Class, race, name = "Shaman", "Totem", "Flametongue Totem"
	mana, attack, health = 3, 0 ,3
	index = "Basic~Shaman~Minion~3~0~3~Totem~Flametongue Totem"
	requireTarget, keyWord, description = False, "", "Adjacent minions have +2 Attack"
	name_CN = "火舌图腾"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.auras["Adjacent minions have +2 Attack"] = StatAura_Adjacent(self, 2, 0)
		
		
class Hex(Spell):
	Class, school, name = "Shaman", "", "Hex"
	requireTarget, mana = True, 4
	index = "Basic~Shaman~Spell~4~Hex"
	description = "Transform a minion into a 0/1 Frog with Taunt"
	name_CN = "妖术"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			newMinion = Frog(self.Game, target.ID)
			self.Game.transform(target, newMinion)
			target = newMinion
		return target
		
class Frog(Minion):
	Class, race, name = "Neutral", "Beast", "Frog"
	mana, attack, health = 0, 0, 1
	index = "Basic~Neutral~Minion~0~0~1~Beast~Frog~Taunt~Uncollectible"
	requireTarget, keyWord, description = False, "Taunt", "Taunt"
	name_CN = "青蛙"
	
	
class Windspeaker(Minion):
	Class, race, name = "Shaman", "", "Windspeaker"
	mana, attack, health = 4, 3, 3
	index = "Basic~Shaman~Minion~4~3~3~~Windspeaker~Battlecry"
	requireTarget, keyWord, description = True, "", "Battlecry: Give a friendly minion Windfury"
	name_CN = "风语者"
	
	def targetExists(self, choice=0):
		return self.selectableFriendlyMinionExists()
		
	def targetCorrect(self, target, choice=0):
		if target.type == "Minion" and target.ID == self.ID and target != self and target.onBoard:
			return True
		return False
		
	#Gurubashi Berserker is returned to hand and then given Windfury. It still has Windfury when replayed.
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			target.getsKeyword("Windfury")
		return target
		
		
class Bloodlust(Spell):
	Class, school, name = "Shaman", "", "Bloodlust"
	requireTarget, mana = False, 5
	index = "Basic~Shaman~Spell~5~Bloodlust"
	description = "Give your minions +3 Attack this turn"
	name_CN = "嗜血"
	def available(self):
		return self.Game.minionsonBoard(self.ID) != []
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		for minion in self.Game.minionsonBoard(self.ID):
			minion.buffDebuff(3, 0, "EndofTurn")
		return None
		
		
class FireElemental(Minion):
	Class, race, name = "Shaman", "Elemental", "Fire Elemental"
	mana, attack, health = 6, 6, 5
	index = "Basic~Shaman~Minion~6~6~5~Elemental~Fire Elemental~Battlecry"
	requireTarget, keyWord, description = True, "", "Battlecry: Deal 3 damage"
	name_CN = "火元素"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			self.dealsDamage(target, 3)
		return target
		
"""Warlock Cards"""
class SacrificialPact(Spell):
	Class, school, name = "Warlock", "", "Sacrificial Pact"
	requireTarget, mana = True, 0
	index = "Basic~Warlock~Spell~0~Sacrificial Pact"
	description = "Destroy a friendly Demon. Restore 5 health to you hero"
	name_CN = "牺牲契约"
	def available(self):
		return self.selectableFriendlyMinionExists()
		
	def text(self, CHN):
		heal = 5 * (2 ** self.countHealDouble())
		return "消灭一个友方恶魔，为你的英雄恢复%d生命值"%heal if CHN else "Destroy a friendly Demon. Restore %d Health to your hero"%heal
		
	def targetCorrect(self, target, choice=0):
		if target.ID != self.ID: return False
		if target.type == "Minion" and "Demon" in target.race and target.onBoard:
			return True
		elif target.name == "Lord Jaraxxus": return True
		return False
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			heal = 5 * (2 ** self.countHealDouble())
			self.Game.killMinion(self, target)
			self.restoresHealth(self.Game.heroes[self.ID], heal)
		return target
		
		
class Corruption(Spell):
	Class, school, name = "Warlock", "", "Corruption"
	requireTarget, mana = True, 1
	index = "Basic~Warlock~Spell~1~Corruption"
	description = "Choose an enemy minion. At the start of your turn, destroy it"
	name_CN = "腐蚀术"
	def available(self):
		return self.selectableEnemyMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.ID != self.ID and target.onBoard
		
	#Tested: Corruption won't have any effect on minions in hand. They won't be discarded nor marked after played.
	#The Corruption effect can be cleansed with Silence effect.
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target and target.onBoard:
			trig = Trig_Corruption(target)
			trig.ID = self.ID
			target.trigsBoard.append(trig)
			trig.connect()
		return target
		
class Trig_Corruption(TrigBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["TurnStarts"])
		self.inherent = False
		self.ID = 1
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and ID == self.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.Game.killMinion(None, self.entity)
		self.disconnect()
		try: self.entity.trigsBoard.remove(self)
		except: pass
		
	def text(self, CHN):
		return "随从会在玩家%d的回合开始时死亡"%self.ID if CHN else "Minion dies at the start of player %d's turn"%self.ID
		
	def selfCopy(self, recipient):
		trig = type(self)(recipient)
		trig.ID = self.ID
		return trig
		
		
class MortalCoil(Spell):
	Class, school, name = "Warlock", "", "Mortal Coil"
	requireTarget, mana = True, 1
	index = "Basic~Warlock~Spell~1~Mortal Coil"
	description = "Deal 1 damage to a minion. If that kills it, draw a card"
	name_CN = "死亡缠绕"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
		
	def text(self, CHN):
		damage = (1 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		return "对一个随从造成%d点伤害。如果‘死亡缠绕’消灭该随从，抽一张牌"%damage if CHN else "Deal %d damage to a minion. If that kills it, draw a card"%damage
		
	#When cast by Archmage Vargoth, this spell can target minions with health <=0 and automatically meet the requirement of killing.
	#If the target minion dies before this spell takes effect, due to being killed by Violet Teacher/Knife Juggler, Mortal Coil still lets
	#player draw a card.
	#If the target is None due to Mayor Noggenfogger's randomization, nothing happens.
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			damage = (1 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			dmgTaker, damageActual = self.dealsDamage(target, damage)
			if dmgTaker.health < 1 or dmgTaker.dead:
				self.Game.Hand_Deck.drawCard(self.ID)
		return target
		
		
class Soulfire(Spell):
	Class, school, name = "Warlock", "", "Soulfire"
	requireTarget, mana = True, 1
	index = "Basic~Warlock~Spell~1~Soulfire"
	description = "Deal 4 damage. Discard a random card"
	name_CN = "灵魂之火"
	def text(self, CHN):
		damage = (4 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		return "造成%d点伤害，随机弃一张牌"%damage if CHN else "Deal %d damage. Discard a random card"%damage
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		ownHand = curGame.Hand_Deck.hands[self.ID]
		if target:
			damage = (4 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			self.dealsDamage(target, damage)
		if curGame.mode == 0:
			if curGame.guides:
				i = curGame.guides.pop(0)
			else:
				ownHand = curGame.Hand_Deck.hands[self.ID]
				i = nprandint(len(ownHand)) if ownHand else -1
				curGame.fixedGuides.append(i)
			if i > -1: curGame.Hand_Deck.discard(self.ID, i)
		return target
		
		
class Voidwalker(Minion):
	Class, race, name = "Warlock", "Demon", "Voidwalker"
	mana, attack, health = 1, 1, 3
	index = "Basic~Warlock~Minion~1~1~3~Demon~Voidwalker~Taunt"
	requireTarget, keyWord, description = False, "Taunt", "Taunt"
	name_CN = "虚空行者"
	
	
class Felstalker(Minion):
	Class, race, name = "Warlock", "Demon", "Felstalker"
	mana, attack, health = 2, 4, 3
	index = "Basic~Warlock~Minion~2~4~3~Demon~Felstalker~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Discard a random card"
	name_CN = "魔犬"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if curGame.mode == 0:
			if curGame.guides:
				i = curGame.guides.pop(0)
			else:
				ownHand = curGame.Hand_Deck.hands[self.ID]
				i = nprandint(len(ownHand)) if ownHand else -1
				curGame.fixedGuides.append(i)
			if i > -1: curGame.Hand_Deck.discard(self.ID, i)
		return None
		
		
class DrainLife(Spell):
	Class, school, name = "Warlock", "", "Drain Life"
	requireTarget, mana = True, 3
	index = "Basic~Warlock~Spell~3~Drain Life"
	description = "Deal 2 damage. Restore 2 Health to your hero"
	name_CN = "吸取生命"
	def text(self, CHN):
		damage = (2 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		heal = 2 * (2 ** self.countHealDouble())
		return "造成%d点伤害，为你的英雄恢复%d点生命值"%(damage, heal) if CHN else "Deal %d damage. Restore %d Health to your hero"%(damage, heal)
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			damage = (2 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			self.dealsDamage(target, damage)
		heal = 2 * (2 ** self.countHealDouble())
		self.restoresHealth(self.Game.heroes[self.ID], heal)
		return target
		
		
class ShadowBolt(Spell):
	Class, school, name = "Warlock", "", "Shadow Bolt"
	requireTarget, mana = True, 3
	index = "Basic~Warlock~Spell~3~Shadow Bolt"
	description = "Deal 4 damage to a minion"
	name_CN = "暗影箭"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
		
	def text(self, CHN):
		damage = (4 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		return "对一个随从造成%d点伤害"%damage if CHN else "Deal %d damage to a minion"%damage
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			damage = (4 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			self.dealsDamage(target, damage)
		return target
		
		
class Hellfire(Spell):
	Class, school, name = "Warlock", "", "Hellfire"
	requireTarget, mana = False, 4
	index = "Basic~Warlock~Spell~4~Hellfire"
	description = "Deal 3 damage to ALL characters"
	name_CN = "地狱烈焰"
	def text(self, CHN):
		damage = (3 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		return "对所有角色造成%d点伤害"%damage if CHN else "Deal %d damage to ALL characters"%damage
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		damage = (3 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		targets = [self.Game.heroes[1], self.Game.heroes[2]] + self.Game.minionsonBoard(1) + self.Game.minionsonBoard(2)
		self.dealsAOE(targets, [damage for obj in targets])
		return None
		
		
class DreadInfernal(Minion):
	Class, race, name = "Warlock", "Demon", "Dread Infernal"
	mana, attack, health = 6, 6, 6
	index = "Basic~Warlock~Minion~6~6~6~Demon~Dread Infernal~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Deal 1 damage to ALL other characters"
	name_CN = "恐惧地狱火"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		targets = [self.Game.heroes[1], self.Game.heroes[2]] + self.Game.minionsonBoard(self.ID, self) + self.Game.minionsonBoard(3-self.ID)
		self.dealsAOE(targets, [1]*len(targets))
		return None
		
"""Warrior Cards"""
class Whirlwind(Spell):
	Class, school, name = "Warrior", "", "Whirlwind"
	requireTarget, mana = False, 1
	index = "Basic~Warrior~Spell~1~Whirlwind"
	description = "Deal 1 damage to ALL minions"
	name_CN = "旋风斩"
	def text(self, CHN):
		damage = (1 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		return "对所有随从造成%d点伤害"%damage if CHN else "Deal %d damage to ALL minions"%damage
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		damage = (1 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		targets = self.Game.minionsonBoard(1) + self.Game.minionsonBoard(2)
		self.dealsAOE(targets, [damage for minion in targets])
		return None
		
		
class Charge(Spell):
	Class, school, name = "Warrior", "", "Charge"
	requireTarget, mana = True, 1
	index = "Basic~Warrior~Spell~1~Charge"
	description = "Give a friendly minion Charge. It can't attack heroes this turn"
	name_CN = "冲锋"
	def available(self):
		return self.selectableFriendlyMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.ID == self.ID and target.onBoard
		
	#This can't attack hero state doesn't count as enchantment.
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			target.getsKeyword("Charge")
			target.marks["Can't Attack Hero"] += 1
			trig = Trig_Charge(target)
			trig.connect()
			target.trigsBoard.append(trig)
		return target
		
class Trig_Charge(TrigBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["TurnEnds"])
		self.inherent = False
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard #Even if the current turn is not minion's owner's turn
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.marks["Can't Attack Hero"] -= 1
		self.disconnect()
		try: self.entity.trigsBoard.remove(self)
		except: pass
		
	def text(self, CHN):
		return "随从重新可以攻击英雄" if CHN else "Minion can attack heroes again"
		
		
class Execute(Spell):
	Class, school, name = "Warrior", "", "Execute"
	requireTarget, mana = True, 2
	index = "Basic~Warrior~Spell~2~Execute"
	description = "Destroy a damaged enemy minion"
	name_CN = "斩杀"
	def available(self):
		return self.selectableEnemyMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.ID != self.ID and target.health < target.health_max and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			self.Game.killMinion(self, target)
		return target
		
		
class Cleave(Spell):
	Class, school, name = "Warrior", "", "Cleave"
	requireTarget, mana = False, 2
	index = "Basic~Warrior~Spell~2~Cleave"
	description = "Deal 2 damage to two random enemy minions"
	name_CN = "顺劈斩"
	def available(self):
		return self.Game.minionsonBoard(3-self.ID) != []
		
	def text(self, CHN):
		damage = (2 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		return "对两个随机敌方随从造成%d点伤害"%damage if CHN else "Deal %d damage to two random enemy minions"%damage
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		damage = (2 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		curGame = self.Game
		minions = curGame.minionsAlive(3-self.ID)
		if minions:
			if curGame.mode == 0:
				if curGame.guides:
					minions = [curGame.minions[3-self.ID][i] for i in curGame.guides.pop(0)]
				else:
					minions = list(npchoice(minions, min(2, len(minions)), replace=False))
					curGame.fixedGuides.append(tuple([minion.pos for minion in minions]))
				self.dealsAOE(minions, [damage]*len(minions))
		return None
		
		
class HeroicStrike(Spell):
	Class, school, name = "Warrior", "", "Heroic Strike"
	requireTarget, mana = False, 2
	index = "Basic~Warrior~Spell~2~Heroic Strike"
	description = "Give your hero +4 Attack this turn"
	name_CN = "英勇打击"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.Game.heroes[self.ID].gainAttack(4)
		return None
		
		
class FieryWarAxe(Weapon):
	Class, name, description = "Warrior", "Fiery War Axe", ""
	mana, attack, durability = 3, 3, 2
	index = "Basic~Warrior~Weapon~3~3~2~Fiery War Axe"
	name_CN = "炽炎战斧"
	
	
class ShieldBlock(Spell):
	Class, school, name = "Warrior", "", "Shield Block"
	requireTarget, mana = False, 3
	index = "Basic~Warrior~Spell~3~Shield Block"
	description = "Gain 5 Armor. Draw a card"
	name_CN = "盾牌格挡"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.Game.heroes[self.ID].gainsArmor(5)
		self.Game.Hand_Deck.drawCard(self.ID)
		return None
		
#Charge gained by enchantment and aura can also be buffed by this Aura.
class WarsongCommander(Minion):
	Class, race, name = "Warrior", "", "Warsong Commander"
	mana, attack, health = 3, 2, 3
	index = "Basic~Warrior~Minion~3~2~3~~Warsong Commander"
	requireTarget, keyWord, description = False, "", "Your Charge minions have +1 Attack"
	name_CN = "战歌指挥官"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.auras["Your Charge minions have +1 Attack"] = StatAura_WarsongCommander(self)
		
#战歌指挥官的光环相对普通的buff光环更特殊，因为会涉及到随从获得和失去光环的情况
class StatAura_WarsongCommander(HasAura_toMinion):
	def __init__(self, entity):
		self.entity = entity
		self.signals, self.auraAffected = ["MinionAppears", "MinionChargeChanged"], []
		
	#All minions appearing on the same side will be subject to the buffAura.
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		#注意，战歌指挥官的光环可以作用在自己身上，这点区分于其他所有身材buff型光环。
		#随从只要发生了冲锋状态的变化就要调用战歌指挥官的Aura_Dealer，如果冲锋状态失去，则由该光环来移除其buff状态
		return self.entity.onBoard and subject.ID == self.entity.ID and ((signal == "MinionAppears" and subject.keyWords["Charge"] > 0) or signal == "MinionChargeChanged")
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.applies(signal, subject)
		
	def applies(self, signal, subject):
		if signal == "MinionAppears":
			if subject.keyWords["Charge"] > 0:
				Stat_Receiver(subject, self, 1, 0).effectStart()
		else: #signal == "MinionChargeChanged"
			if subject.keyWords["Charge"] > 0:
				if not any(subject is recipient for recipient, receiver in self.auraAffected):
					Stat_Receiver(subject, self, 1, 0).effectStart()
			elif subject.keyWords["Charge"] < 1:
				for recipient, receiver in self.auraAffected:
					if subject is recipient:
						receiver.effectClear()
						break
						
	def auraAppears(self):
		for minion in self.entity.Game.minionsonBoard(self.entity.ID):
			self.applies("MinionAppears", minion) #The signal here is a placeholder and directs the function to first-time aura applicatioin
		for sig in self.signals:
			try: self.entity.Game.trigsBoard[self.entity.ID][sig].remove(self)
			except: pass
			
	def selfCopy(self, recipient):
		return type(self)(recipient)
	#可以通过HasAura_toMinion的createCopy方法复制
	
	
class KorkronElite(Minion):
	Class, race, name = "Warrior", "", "Kor'kron Elite"
	mana, attack, health = 4, 4, 3
	index = "Basic~Warrior~Minion~4~4~3~~Kor'kron Elite~Charge"
	requireTarget, keyWord, description = False, "Charge", "Charge"
	name_CN = "库卡隆 精英卫士"
	
	
class ArcaniteReaper(Weapon):
	Class, name, description = "Warrior", "Arcanite Reaper", ""
	mana, attack, durability = 5, 5, 2
	index = "Basic~Warrior~Weapon~5~5~2~Arcanite Reaper"
	name_CN = "奥金斧"
	
	
	
	
Basic_Indices = { #Heroes and standard Hero Powers
				"Hero: Demon Hunter": Illidan, "Hero: Druid": Malfurion, 
				"Hero: Hunter": Rexxar, "Hero: Mage": Jaina, 
				"Hero: Paladin": Uther, "Hero: Priest": Anduin, 
				"Hero: Rogue": Valeera, "Hero: Shaman": Thrall, 
				"Hero: Warlock": Guldan, "Hero: Warrior": Garrosh, 
				"Demon Hunter~Basic Hero Power~1~Demon Claws": DemonClaws,
				"Demon Hunter~Upgraded Hero Power~1~Demon's Bite": DemonsBite,
				"Druid~Basic Hero Power~2~Shapeshift": Shapeshift,
				"Druid~Upgraded Hero Power~2~Dire Shapeshift": DireShapeshift,
				"Hunter~Basic Hero Power~2~Steady Shot": SteadyShot,
				"Hunter~Upgraded Hero Power~2~Ballista Shot": BallistaShot,
				"Mage~Basic Hero Power~2~Fireblast": Fireblast,
				"Mage~Upgraded Hero Power~2~Fireblast Rank 2": FireblastRank2,
				"Paladin~Basic Hero Power~2~Reinforce": Reinforce,
				"Paladin~Upgraded Hero Power~2~The Silver Hand": TheSilverHand,
				"Priest~Basic Hero Power~2~Lesser Heal": LesserHeal,
				"Priest~Upgraded Hero Power~2~Heal": Heal,
				"Rogue~Basic Hero Power~2~Dagger Mastery": DaggerMastery,
				"Rogue~Upgraded Hero Power~2~Poisoned Daggers": PoisonedDaggers,
				"Shaman~Basic Hero Power~2~Totemic Call": TotemicCall,
				"Shaman~Upgraded Hero Power~2~Totemic Call": TotemicSlam,
				"Warlock~Basic Hero Power~2~Life Tap": LifeTap,
				"Warlock~Upgraded Hero Power~2~Soul Tap": SoulTap,
				"Warrior~Basic Hero Power~2~Armor Up!": ArmorUp,
				"Warrior~Upgraded Hero Power~2~Tank Up!": TankUp,
				
				"Basic~Neutral~Spell~0~The Coin~Uncollectible": TheCoin,
				"Basic~Neutral~Minion~1~1~1~~Elven Archer~Battlecry": ElvenArcher,
				"Basic~Neutral~Minion~1~1~2~~Goldshire Footman~Taunt": GoldshireFootman,
				"Basic~Neutral~Minion~1~1~1~Murloc~Grimscale Oracle": GrimscaleOracle,
				"Basic~Neutral~Minion~1~2~1~Murloc~Murloc Raider": MurlocRaider,
				"Basic~Neutral~Minion~1~1~1~Beast~Stonetusk Boar~Charge": StonetuskBoar,
				"Basic~Neutral~Minion~1~2~1~~Voodoo Doctor~Battlecry": VoodooDoctor,
				"Basic~Paladin~Minion~1~1~1~~Silver Hand Recruit~Uncollectible": SilverHandRecruit,
				"Basic~Shaman~Minion~1~1~1~Totem~Searing Totem~Uncollectible": SearingTotem,
				"Basic~Shaman~Minion~1~0~2~Totem~Stoneclaw Totem~Taunt~Uncollectible": StoneclawTotem,
				"Basic~Shaman~Minion~1~0~2~Totem~Healing Totem~Uncollectible": HealingTotem,
				"Basic~Shaman~Minion~1~0~2~Totem~Strength Totem~Spell Damage~Uncollectible": StrengthTotem,
				"Basic~Neutral~Minion~2~3~2~~Acidic Swamp Ooze~Battlecry": AcidicSwampOoze,
				"Basic~Neutral~Minion~2~3~2~Beast~Bloodfen Raptor": BloodfenRaptor,
				"Basic~Neutral~Minion~2~2~1~Murloc~Bluegill Warrior~Charge": BluegillWarrior,
				"Basic~Neutral~Minion~2~2~2~~Frostwolf Grunt~Taunt": FrostwolfGrunt,
				"Basic~Neutral~Minion~2~2~2~~Kobold Geomancer~Spell Damage": KoboldGeomancer,
				"Basic~Neutral~Minion~2~2~1~Murloc~Murloc Tidehunter~Battlecry": MurlocTidehunter,
				"Basic~Neutral~Minion~1~1~1~Murloc~Murloc Scout~Uncollectible": MurlocScout,
				"Basic~Neutral~Minion~2~1~1~~Novice Engineer~Battlecry": NoviceEngineer,
				"Basic~Neutral~Minion~2~2~3~Beast~River Crocolisk": RiverCrocolisk,
				"Basic~Neutral~Minion~3~1~4~~Dalaran Mage~Spell Damage": DalaranMage,
				"Basic~Neutral~Minion~3~2~2~~Ironforge Rifleman~Battlecry": IronforgeRifleman,
				"Basic~Neutral~Minion~3~3~3~Beast~Ironfur Grizzly~Taunt": IronfurGrizzly,
				"Basic~Neutral~Minion~3~5~1~Elemental~Magma Rager": MagmaRager,
				"Basic~Neutral~Minion~3~2~2~~Raid Leader": RaidLeader,
				"Basic~Neutral~Minion~3~2~3~~Razorfen Hunter~Battlecry": RazorfenHunter,
				"Basic~Neutral~Minion~1~1~1~Beast~Boar~Uncollectible": Boar,
				"Basic~Neutral~Minion~3~3~2~~Shattered Sun Cleric~Battlecry": ShatteredSunCleric,
				"Basic~Neutral~Minion~3~1~4~Beast~Silverback Patriarch~Taunt": SilverbackPatriarch,
				"Basic~Neutral~Minion~3~3~1~~Wolfrider~Charge": Wolfrider,
				"Basic~Neutral~Minion~4~4~5~~Chillwind Yeti": ChillwindYeti,
				"Basic~Neutral~Minion~4~2~4~~Dragonling Mechanic~Battlecry": DragonlingMechanic,
				"Basic~Neutral~Minion~1~2~1~Mech~Mechanical Dragonling~Uncollectible": MechanicalDragonling,
				"Basic~Neutral~Minion~4~2~4~~Gnomish Inventor~Battlecry": GnomishInventor,
				"Basic~Neutral~Minion~4~2~7~Beast~Oasis Snapjaw": OasisSnapjaw,
				"Basic~Neutral~Minion~4~4~4~~Ogre Magi~Spell Damage": OgreMagi,
				"Basic~Neutral~Minion~4~3~5~~Sen'jin Shieldmasta~Taunt": SenjinShieldmasta,
				"Basic~Neutral~Minion~4~2~5~~Stormwind Knight~Charge": StormwindKnight,
				"Basic~Neutral~Minion~5~5~4~~Booty Bay Bodyguard~Taunt": BootyBayBodyguard,
				"Basic~Neutral~Minion~5~4~5~~Darkscale Healer~Battlecry": DarkscaleHealer,
				"Basic~Neutral~Minion~5~4~4~~Frostwolf Warlord~Battlecry": FrostwolfWarlord,
				"Basic~Neutral~Minion~5~2~7~~Gurubashi Berserker": GurubashiBerserker,
				"Basic~Neutral~Minion~5~4~4~~Nightblade~Battlecry": Nightblade,
				"Basic~Neutral~Minion~5~4~2~~Stormpike Commando~Battlecry": StormpikeCommando,
				"Basic~Neutral~Minion~6~6~5~~Lord of the Arena~Taunt": LordoftheArena,
				"Basic~Neutral~Minion~6~4~7~~Archmage~Spell Damage": Archmage,
				"Basic~Neutral~Minion~6~6~7~~Boulderfist Ogre": BoulderfistOgre,
				"Basic~Neutral~Minion~6~5~2~~Reckless Rocketeer~Charge": RecklessRocketeer,
				"Basic~Neutral~Minion~7~9~5~Beast~Core Hound": CoreHound,
				"Basic~Neutral~Minion~7~6~6~~Stormwind Champion": StormwindChampion,
				"Basic~Neutral~Minion~7~7~7~~War Golem": WarGolem,
				#Demon Hunter
				"Basic~Demon Hunter~Minion~1~2~1~Demon~Shadowhoof Slayer~Battlecry": ShadowhoofSlayer,
				"Basic~Demon Hunter~Spell~2~Chaos Strike": ChaosStrike,
				"Basic~Demon Hunter~Minion~2~3~2~Demon~Sightless Watcher~Battlecry": SightlessWatcher,
				"Basic~Demon Hunter~Weapon~3~2~2~Aldrachi Warblades~Lifesteal": AldrachiWarblades,
				"Basic~Demon Hunter~Spell~3~Coordinated Strike": CoordinatedStrike,
				"Basic~Demon Hunter~Minion~1~1~1~~Illidari Initiate~Rush~Uncollectible": IllidariInitiate,
				"Basic~Demon Hunter~Minion~3~4~2~Demon~Satyr Overseer": SatyrOverseer,
				"Basic~Demon Hunter~Minion~2~2~2~Demon~Illidari Satyr~Uncollectible": IllidariSatyr,
				"Basic~Demon Hunter~Spell~3~Soul Cleave": SoulCleave,
				"Basic~Demon Hunter~Spell~5~Chaos Nova": ChaosNova,
				"Basic~Demon Hunter~Minion~5~6~4~~Glaivebound Adept~Battlecry": GlaiveboundAdept,
				"Basic~Demon Hunter~Spell~8~Inner Demon": InnerDemon,
				#Druid
				"Basic~Druid~Spell~0~Innervate": Innervate,
				"Basic~Druid~Spell~0~Moonfire": Moonfire,
				"Basic~Druid~Spell~1~Claw": Claw,
				"Basic~Druid~Spell~2~Mark of the Wild": MarkoftheWild,
				"Basic~Druid~Spell~3~Healing Touch": HealingTouch,
				"Basic~Druid~Spell~3~Savage Roar": SavageRoar,
				"Basic~Druid~Spell~3~Wild Growth": WildGrowth,
				"Basic~Druid~Spell~0~Excess Mana~Uncollectible": ExcessMana,
				"Basic~Druid~Spell~4~Swipe": Swipe,
				"Basic~Druid~Spell~6~Starfire": Starfire,
				"Basic~Druid~Minion~8~8~8~~Ironbark Protector~Taunt": IronbarkProtector,
				#Hunter
				"Basic~Hunter~Spell~1~Arcane Shot": ArcaneShot,
				"Basic~Hunter~Minion~1~1~1~Beast~Timber Wolf": TimberWolf,
				"Basic~Hunter~Spell~1~Tracking": Tracking,
				"Basic~Hunter~Spell~2~Hunter's Mark": HuntersMark,
				"Basic~Hunter~Spell~3~Animal Companion": AnimalCompanion,
				"Basic~Hunter~Minion~3~4~2~Beast~Huffer~Charge~Uncollectible": Huffer,
				"Basic~Hunter~Minion~3~2~4~Beast~Leokk~Uncollectible": Leokk,
				"Basic~Hunter~Minion~3~4~4~Beast~Misha~Taunt~Uncollectible": Misha,
				"Basic~Hunter~Spell~3~Kill Command": KillCommand,
				"Basic~Hunter~Minion~4~4~3~~Houndmaster~Battlecry": Houndmaster,
				"Basic~Hunter~Spell~4~Multi-Shot": MultiShot,
				"Basic~Hunter~Minion~5~3~2~Beast~Starving Buzzard": StarvingBuzzard,
				"Basic~Hunter~Minion~5~2~5~Beast~Tundra Rhino": TundraRhino,
				#Mage
				"Basic~Mage~Spell~1~Arcane Missiles": ArcaneMissiles,
				"Basic~Mage~Spell~1~Mirror Image": MirrorImage,
				"Basic~Mage~Minion~0~0~2~~Mirror Image~Taunt~Uncollectible": MirrorImage_Minion,
				"Basic~Mage~Spell~2~Arcane Explosion": ArcaneExplosion,
				"Basic~Mage~Spell~2~Frostbolt": Frostbolt,
				"Basic~Mage~Spell~3~Arcane Intellect": ArcaneIntellect,
				"Basic~Mage~Spell~3~Frost Nova": FrostNova,
				"Basic~Mage~Spell~4~Fireball": Fireball,
				"Basic~Mage~Spell~4~Polymorph": Polymorph,
				"Basic~Neutral~Minion~1~1~1~Beast~Sheep~Uncollectible": Sheep,
				"Basic~Mage~Minion~4~3~6~Elemental~Water Elemental": WaterElemental,
				"Basic~Mage~Spell~7~Flamestrike": Flamestrike,
				#Paladin
				"Basic~Paladin~Spell~1~Blessing of Might": BlessingofMight,
				"Basic~Paladin~Spell~1~Hand of Protection": HandofProtection,
				"Basic~Paladin~Spell~1~Humility": Humility,
				"Basic~Paladin~Weapon~1~1~4~Light's Justice": LightsJustice,
				"Basic~Paladin~Spell~2~Holy Light": HolyLight,
				"Basic~Paladin~Spell~4~Blessing of Kings": BlessingofKings,
				"Basic~Paladin~Spell~4~Consecration": Consecration,
				"Basic~Paladin~Spell~4~Hammer of Wrath": HammerofWrath,
				"Basic~Paladin~Weapon~4~4~2~Truesilver Champion": TruesilverChampion,
				"Basic~Paladin~Minion~7~5~6~~Guardian of Kings~Battlecry": GuardianofKings,
				#Priest
				"Basic~Priest~Spell~0~Power Word: Shield": PowerWordShield,
				"Basic~Priest~Spell~1~Holy Smite": HolySmite,
				"Basic~Priest~Spell~1~Mind Vision": MindVision,
				"Basic~Priest~Minion~1~1~1~~Psychic Conjurer~Battlecry": PsychicConjurer,
				"Basic~Priest~Spell~1~Radiance": Radiance,
				"Basic~Priest~Spell~2~Shadow Word: Death": ShadowWordDeath,
				"Basic~Priest~Spell~2~Shadow Word: Pain": ShadowWordPain,
				"Basic~Priest~Spell~4~Holy Nova": HolyNova,
				"Basic~Priest~Spell~4~Power Infusion": PowerInfusion,
				"Basic~Priest~Spell~10~Mind Control": MindControl,
				#Rogue
				"Basic~Rogue~Spell~0~Backstab": Backstab,
				"Basic~Rogue~Weapon~1~1~2~Wicked Knife~Uncollectible": WickedKnife,
				"Basic~Rogue~Weapon~1~2~2~Poisoned Dagger~Uncollectible": PoisonedDagger,
				"Basic~Rogue~Spell~1~Deadly Poison": DeadlyPoison,
				"Basic~Rogue~Spell~1~Sinister Strike": SinisterStrike,
				"Basic~Rogue~Spell~2~Sap": Sap,
				"Basic~Rogue~Spell~2~Shiv": Shiv,
				"Basic~Rogue~Spell~3~Fan of Knives": FanofKnives,
				"Basic~Rogue~Minion~4~3~3~~Plaguebringer~Battlecry": Plaguebringer,
				"Basic~Rogue~Spell~5~Assassinate": Assassinate,
				"Basic~Rogue~Weapon~5~3~4~Assassin's Blade": AssassinsBlade,
				"Basic~Rogue~Spell~7~Sprint": Sprint,
				#Shaman
				"Basic~Shaman~Spell~0~Ancestral Healing": AncestralHealing,
				"Basic~Shaman~Spell~0~Totemic Might": TotemicMight,
				"Basic~Shaman~Spell~1~Frost Shock": FrostShock,
				"Basic~Shaman~Spell~2~Rockbiter Weapon": RockbiterWeapon,
				"Basic~Shaman~Spell~2~Windfury": Windfury,
				"Basic~Shaman~Minion~3~0~3~Totem~Flametongue Totem": FlametongueTotem,
				"Basic~Shaman~Spell~4~Hex": Hex,
				"Basic~Neutral~Minion~0~0~1~Beast~Frog~Taunt~Uncollectible": Frog,
				"Basic~Shaman~Minion~4~3~3~~Windspeaker~Battlecry": Windspeaker,
				"Basic~Shaman~Spell~5~Bloodlust": Bloodlust,
				"Basic~Shaman~Minion~6~6~5~Elemental~Fire Elemental~Battlecry": FireElemental,
				#Warlock
				"Basic~Warlock~Spell~0~Sacrificial Pact": SacrificialPact,
				"Basic~Warlock~Spell~1~Corruption": Corruption,
				"Basic~Warlock~Spell~1~Mortal Coil": MortalCoil,
				"Basic~Warlock~Spell~1~Soulfire": Soulfire,
				"Basic~Warlock~Minion~1~1~3~Demon~Voidwalker~Taunt": Voidwalker,
				"Basic~Warlock~Minion~2~4~3~Demon~Felstalker~Battlecry": Felstalker,
				"Basic~Warlock~Spell~3~Drain Life": DrainLife,
				"Basic~Warlock~Spell~3~Shadow Bolt": ShadowBolt,
				"Basic~Warlock~Spell~4~Hellfire": Hellfire,
				"Basic~Warlock~Minion~6~6~6~Demon~Dread Infernal~Battlecry": DreadInfernal,
				#Warrior
				"Basic~Warrior~Spell~1~Whirlwind": Whirlwind,
				"Basic~Warrior~Spell~1~Charge": Charge,
				"Basic~Warrior~Spell~2~Execute": Execute,
				"Basic~Warrior~Spell~2~Cleave": Cleave,
				"Basic~Warrior~Spell~2~Heroic Strike": HeroicStrike,
				"Basic~Warrior~Weapon~3~3~2~Fiery War Axe": FieryWarAxe,
				"Basic~Warrior~Spell~3~Shield Block": ShieldBlock,
				"Basic~Warrior~Minion~3~2~3~~Warsong Commander": WarsongCommander,
				"Basic~Warrior~Minion~4~4~3~~Kor'kron Elite~Charge": KorkronElite,
				"Basic~Warrior~Weapon~5~5~2~Arcanite Reaper": ArcaniteReaper
				}