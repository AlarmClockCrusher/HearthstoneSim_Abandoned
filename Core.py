from CardTypes import *
from Triggers_Auras import *
from numpy.random import choice as npchoice
from numpy.random import randint as nprandint
from numpy.random import shuffle as npshuffle
from numpy import inf as npinf
import numpy as np

"""Core"""
class SilverHandRecruit(Minion):
	Class, race, name = "Paladin", "", "Silver Hand Recruit"
	mana, attack, health = 1, 1, 1
	index = "Core~Paladin~Minion~1~1~1~~Silver Hand Recruit~Uncollectible"
	requireTarget, keyWord, description = False, "", ""
	name_CN = "白银之手新兵"


class WickedKnife(Weapon):
	Class, name, description = "Rogue", "Wicked Knife", ""
	mana, attack, durability = 1, 1, 2
	index = "Core~Rogue~Weapon~1~1~2~Wicked Knife~Uncollectible"
	name_CN = "邪恶短刀"

class PoisonedDagger(Weapon):
	Class, name, description = "Rogue", "Poisoned Dagger", ""
	mana, attack, durability = 1, 2, 2
	index = "Core~Rogue~Weapon~1~2~2~Poisoned Dagger~Uncollectible"
	name_CN = "浸毒匕首"


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
		