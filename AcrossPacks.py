from CardTypes import *
from Triggers_Auras import *
import numpy as np


"""CORE cards"""
class TheCoin(Spell):
	Class, school, name = "Neutral", "", "The Coin"
	requireTarget, mana = False, 0
	index = "BASIC~Neutral~Spell~0~~The Coin~Uncollectible"
	description = "Gain 1 mana crystal for this turn."
	name_CN = "幸运币"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.Game.Manas.gainTempManaCrystal(1, ID=self.ID)
		return None


class SilverHandRecruit(Minion):
	Class, race, name = "Paladin", "", "Silver Hand Recruit"
	mana, attack, health = 1, 1, 1
	index = "BASIC~Paladin~Minion~1~1~1~~Silver Hand Recruit~Uncollectible"
	requireTarget, keyWord, description = False, "", ""
	name_CN = "白银之手新兵"


class WickedKnife(Weapon):
	Class, name, description = "Rogue", "Wicked Knife", ""
	mana, attack, durability = 1, 1, 2
	index = "BASIC~Rogue~Weapon~1~1~2~Wicked Knife~Uncollectible"
	name_CN = "邪恶短刀"


class PoisonedDagger(Weapon):
	Class, name, description = "Rogue", "Poisoned Dagger", ""
	mana, attack, durability = 1, 2, 2
	index = "TGT~Rogue~Weapon~1~2~2~Poisoned Dagger~Uncollectible"
	name_CN = "浸毒匕首"


class SearingTotem(Minion):
	Class, race, name = "Shaman", "Totem", "Searing Totem"
	mana, attack, health = 1, 1, 1
	index = "BASIC~Shaman~Minion~1~1~1~Totem~Searing Totem~Uncollectible"
	requireTarget, keyWord, description = False, "", ""
	name_CN = "灼热图腾"


class StoneclawTotem(Minion):
	Class, race, name = "Shaman", "Totem", "Stoneclaw Totem"
	mana, attack, health = 1, 0, 2
	index = "BASIC~Shaman~Minion~1~0~2~Totem~Stoneclaw Totem~Taunt~Uncollectible"
	requireTarget, keyWord, description = False, "Taunt", "Taunt"
	name_CN = "石爪图腾"


class HealingTotem(Minion):
	Class, race, name = "Shaman", "Totem", "Healing Totem"
	mana, attack, health = 1, 0, 2
	index = "BASIC~Shaman~Minion~1~0~2~Totem~Healing Totem~Uncollectible"
	requireTarget, keyWord, description = False, "", "At the end of your turn, restore 1 health to all friendly minions"
	name_CN = "治疗图腾"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_HealingTotem(self)]

class Trig_HealingTotem(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["TurnEnds"])
	
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and ID == self.entity.ID
	
	def text(self, CHN):
		heal = 2 * (2 ** self.entity.countHealDouble())
		return "在你的回合结束时，为所有友方随从恢复%d生命值" % heal if CHN else "At the end of your turn, restore %d health to all friendly minions" % heal
	
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		heal = 1 * (2 ** self.entity.countHealDouble())
		targets = self.entity.Game.minionsonBoard(self.entity.ID)
		self.entity.restoresAOE(targets, [heal] * len(targets))


class StrengthTotem(Minion):
	Class, race, name = "Shaman", "Totem", "Strength Totem"
	mana, attack, health = 1, 0, 2
	index = "BASIC~Shaman~Minion~1~0~2~Totem~Strength Totem~Uncollectible"
	requireTarget, keyWord, description = False, "", "At the end of your turn, give another friendly minion +1 Attack"
	name_CN = "力量图腾"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_StrengthTotem(self)]

class Trig_StrengthTotem(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["TurnEnds"])
	
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
		damage = (2 + self.marks["Damage Boost"] + self.Game.status[self.ID]["Power Damage"]) * (2 ** self.countDamageDouble())
		if self.Game.status[self.ID]["Power Can Target Minions"] > 0:
			return "造成%d点伤害" % damage if CHN else "Deal %d damage" % damage
		else:
			return "对敌方英雄造成%d点伤害" % damage if CHN else "Deal %d damage to the enemy hero" % damage
	
	def effect(self, target=None, choice=0):
		damage = (2 + self.Game.status[self.ID]["Power Damage"]) * (2 ** self.countDamageDouble())
		self.dealsDamage(target if target else self.Game.heroes[3 - self.ID], damage)
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
			return "造成%d点伤害" % damage if CHN else "Deal %d damage" % damage
		else:
			return "对敌方英雄造成%d点伤害" % damage if CHN else "Deal %d damage to the enemy hero" % damage
	
	def effect(self, target=None, choice=0):
		damage = (3 + self.marks["Damage Boost"] + self.Game.status[self.ID]["Power Damage"]) * (2 ** self.countDamageDouble())
		self.dealsDamage(target if target else self.Game.heroes[3 - self.ID], damage)
		return 0


#Mage basic and upgraded powers
class Fireblast(HeroPower):
	mana, name, requireTarget = 2, "Fireblast", True
	index = "Mage~Basic Hero Power~2~Fireblast"
	description = "Deal 1 damage"
	name_CN = "火焰冲击"
	
	def text(self, CHN):
		damage = (1 + self.Game.status[self.ID]["Power Damage"]) * (2 ** self.countDamageDouble())
		return "造成%d点伤害" % damage if CHN else "Deal %d damage" % damage
	
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
		return "造成%d点伤害" % damage if CHN else "Deal %d damage" % damage
	
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
		self.Game.summon(SilverHandRecruit(self.Game, self.ID), -1, self)
		return 0


class TheSilverHand(HeroPower):
	mana, name, requireTarget = 2, "The Silver Hand", False
	index = "Paladin~Upgraded Hero Power~2~The Silver Hand"
	description = "Summon two 1/1 Silver Hand Recruits"
	name_CN = "白银之手"
	
	def available(self):
		return not self.chancesUsedUp() and self.Game.space(self.ID)
	
	def effect(self, target=None, choice=0):
		self.Game.summon([SilverHandRecruit(self.Game, self.ID) for i in range(2)], (-1, "totheRightEnd"), self)
		return 0


#Priest basic and upgraded powers
class LesserHeal(HeroPower):
	mana, name, requireTarget = 2, "Lesser Heal", True
	index = "Priest~Basic Hero Power~2~Lesser Heal"
	description = "Restore 2 Health"
	name_CN = "次级治疗术"
	
	def text(self, CHN):
		heal = 2 * (2 ** self.countHealDouble())
		return "恢复%d点生命值" % heal if CHN else "Restore %d Health" % heal
	
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
		return "恢复%d点生命值" % heal if CHN else "Restore %d Health" % heal
	
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
			if totem: curGame.summon(totem(curGame, self.ID), -1, self)
		return 0
	
	def viableTotems(self):
		viableTotems = [SearingTotem, StoneclawTotem, HealingTotem, StrengthTotem]
		for minion in self.Game.minionsonBoard(self.ID):
			try:
				viableTotems.remove(type(minion))
			except:
				pass
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
				curGame.summon(curGame.guides.pop(0)(curGame, self.ID), -1, self)
			else:
				curGame.options = [totem(curGame, self.ID) for totem in [SearingTotem, StoneclawTotem, HealingTotem, StrengthTotem]]
				curGame.Discover.startDiscover(self)
		return 0
	
	def discoverDecided(self, option, pool):
		self.Game.fixedGuides.append(type(option))
		self.Game.summon(option, -1, self)


#Warloc basic and upgraded powers
class LifeTap(HeroPower):
	mana, name, requireTarget = 2, "Life Tap", False
	index = "Warlock~Basic Hero Power~2~Life Tap"
	description = "Draw a card and take 2 damage"
	name_CN = "生命分流"
	
	def text(self, CHN):
		damage = (2 + self.Game.status[self.ID]["Power Damage"]) * (2 ** self.countDamageDouble())
		return "抽一张牌并受到%d点伤害" % damage if CHN else "Draw a card and take %d damage" % damage
	
	def effect(self, target=None, choice=0):
		damage = (2 + self.marks["Damage Boost"] + self.Game.status[self.ID]["Power Damage"]) * (2 ** self.countDamageDouble())
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
	index = "BASIC"

class Rexxar(Hero):
	Class, name, heroPower = "Hunter", "Rexxar", SteadyShot
	name_CN = "雷克萨"
	index = "BASIC"

class Valeera(Hero):
	Class, name, heroPower = "Rogue", "Valeera", DaggerMastery
	name_CN = "瓦莉拉"
	index = "BASIC"

class Malfurion(Hero):
	Class, name, heroPower = "Druid", "Malfurion", Shapeshift
	name_CN = "玛法里奥"
	index = "BASIC"

class Garrosh(Hero):
	Class, name, heroPower = "Warrior", "Garrosh", ArmorUp
	name_CN = "加尔鲁什"
	index = "BASIC"

class Uther(Hero):
	Class, name, heroPower = "Paladin", "Uther", Reinforce
	name_CN = "乌瑟尔"
	index = "BASIC"

class Thrall(Hero):
	Class, name, heroPower = "Shaman", "Thrall", TotemicCall
	name_CN = "萨尔"
	index = "BASIC"

class Jaina(Hero):
	Class, name, heroPower = "Mage", "Jaina", Fireblast
	name_CN = "吉安娜"
	index = "BASIC"

class Anduin(Hero):
	Class, name, heroPower = "Priest", "Anduin", LesserHeal
	name_CN = "安度因"
	index = "BASIC"

class Guldan(Hero):
	Class, name, heroPower = "Warlock", "Gul'dan", LifeTap
	name_CN = "古尔丹"
	index = "BASIC"


class MurlocScout(Minion):
	Class, race, name = "Neutral", "Murloc", "Murloc Scout"
	mana, attack, health = 1, 1, 1
	index = "BASIC~Neutral~Minion~1~1~1~Murloc~Murloc Scout~Uncollectible"
	requireTarget, keyWord, description = False, "", ""
	name_CN = "鱼人斥侯"
	
	
class IllidariInitiate(Minion):
	Class, race, name = "Demon Hunter", "", "Illidari Initiate"
	mana, attack, health = 1, 1, 1
	index = "BASIC~Demon Hunter~Minion~1~1~1~~Illidari Initiate~Rush~Uncollectible"
	requireTarget, keyWord, description = False, "Rush", "Rush"
	name_CN = "伊利达雷新兵"


class ExcessMana(Spell):
	Class, school, name = "Druid", "", "Excess Mana"
	requireTarget, mana = False, 0
	index = "BASIC~Druid~Spell~0~~Excess Mana~Uncollectible"
	description = "Draw a card"
	name_CN = "法力过剩"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.Game.Hand_Deck.drawCard(self.ID)
		return None


class Claw(Spell):
	Class, school, name = "Druid", "", "Claw"
	requireTarget, mana = False, 1
	index = "BASIC~Druid~Spell~1~~Claw"
	description = "Give your hero +2 Attack this turn. Gain 2 Armor"
	name_CN = "爪击"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.Game.heroes[self.ID].gainAttack(2)
		self.Game.heroes[self.ID].gainsArmor(2)
		return None


class ArcaneMissiles(Spell):
	Class, school, name = "Mage", "Arcane", "Arcane Missiles"
	requireTarget, mana = False, 1
	index = "BASIC~Mage~Spell~1~Arcane~Arcane Missiles"
	description = "Deal 3 damage randomly split among all enemies"
	name_CN = "奥术飞弹"
	
	def text(self, CHN):
		damage = (3 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		return "造成%d点伤害，随机分配到所有敌人身上" % damage if CHN else "Deal %d damage randomly split among all enemies" % damage
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		damage = (3 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		side, curGame = 3 - self.ID, self.Game
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
						curGame.fixedGuides.append((char.pos, char.type + str(char.ID)))
					else: curGame.fixedGuides.append((0, ''))
				if char: self.dealsDamage(char, 1)
				else: break
		return None


class WaterElemental_Basic(Minion):
	Class, race, name = "Mage", "Elemental", "Water Elemental"
	mana, attack, health = 4, 3, 6
	index = "BASIC~Mage~Minion~4~3~6~Elemental~Water Elemental"
	requireTarget, keyWord, description = False, "", "Freeze any character damaged by this minion"
	name_CN = "水元素"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_WaterElemental(self)]

class Trig_WaterElemental(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["MinionTakesDmg", "HeroTakesDmg"])
	
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject == self.entity
	
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		target.getsStatus("Frozen")
	
	def text(self, CHN):
		return "冻结任何受到该随从伤害的角色" if CHN else "Freeze any character damaged by this minion"


class Pyroblast(Spell):
	Class, school, name = "Mage", "Fire", "Pyroblast"
	requireTarget, mana = True, 10
	index = "EXPERT1~Mage~Spell~10~Fire~Pyroblast"
	description = "Deal 10 damage"
	name_CN = "炎爆术"
	
	def text(self, CHN):
		damage = (10 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		return "造成%d点伤害" % damage if CHN else "Deal %d damage" % damage
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			damage = (10 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			self.dealsDamage(target, damage)
		return target


class TruesilverChampion(Weapon):
	Class, name, description = "Paladin", "Truesilver Champion", "Whenever your hero attacks, restore 2 Health to it"
	mana, attack, durability = 4, 4, 2
	index = "BASIC~Paladin~Weapon~4~4~2~Truesilver Champion"
	name_CN = "真银圣剑"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_TruesilverChampion(self)]

class Trig_TruesilverChampion(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["HeroAttackingMinion", "HeroAttackingHero"])
	
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject == self.entity.Game.heroes[self.entity.ID] and self.entity.onBoard
	
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		heal = 2 * (2 ** self.entity.countHealDouble())
		self.entity.restoresHealth(self.entity.Game.heroes[self.entity.ID], heal)
	
	def text(self, CHN):
		heal = 2 * (2 ** self.entity.countHealDouble())
		return "每当你的英雄进攻，便为其恢复%d点生命值" % heal if CHN else "Whenever your hero attacks, restore %d Health to it" % heal


class PatientAssassin(Minion):
	Class, race, name = "Rogue", "", "Patient Assassin"
	mana, attack, health = 2, 1, 2
	index = "EXPERT1~Rogue~Minion~2~1~2~~Patient Assassin~Poisonous~Stealth"
	requireTarget, keyWord, description = False, "Stealth,Poisonous", "Stealth, Poisonous"
	name_CN = "耐心的刺客"
	
	
class FieryWarAxe_Basic(Weapon):
	Class, name, description = "Warrior", "Fiery War Axe", ""
	mana, attack, durability = 3, 3, 2
	index = "BASIC~Warrior~Weapon~3~3~2~Fiery War Axe"
	name_CN = "炽炎战斧"
	
"""EXPERT1 cards"""
class Bananas(Spell):
	Class, school, name = "Neutral", "", "Bananas"
	requireTarget, mana = True, 1
	index = "EXPERT1~Neutral~Spell~1~~Bananas~Uncollectible"
	description = "Give a minion +1/+1"
	name_CN = "香蕉"
	
	def available(self):
		return self.selectableMinionExists()
	
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			target.buffDebuff(1, 1)
		return target


class Skeleton(Minion):
	Class, race, name = "Neutral", "", "Skeleton"
	mana, attack, health = 1, 1, 1
	index = "ICECROWN~Neutral~Minion~1~1~1~~Skeleton~Uncollectible"
	requireTarget, keyWord, description = False, "", ""
	name_CN = "骷髅"


class VioletApprentice(Minion):
	Class, race, name = "Neutral", "", "Violet Apprentice"
	mana, attack, health = 1, 1, 1
	index = "EXPERT1~Neutral~Minion~1~1~1~~Violet Apprentice~Uncollectible"
	requireTarget, keyWord, description = False, "", ""
	name_CN = "紫罗兰学徒"


class Whelp(Minion):
	Class, race, name = "Neutral", "Dragon", "Whelp"
	mana, attack, health = 1, 1, 1
	index = "EXPERT1~Neutral~Minion~1~1~1~Dragon~Whelp~Uncollectible"
	requireTarget, keyWord, description = False, "", ""
	name_CN = "雏龙"


class BaineBloodhoof(Minion):
	Class, race, name = "Neutral", "", "Baine Bloodhoof"
	mana, attack, health = 5, 5, 5
	index = "EXPERT1~Neutral~Minion~5~5~5~~Baine Bloodhoof~Legendary~Uncollectible"
	requireTarget, keyWord, description = False, "", ""
	name_CN = "贝恩·血蹄"


class Dream(Spell):
	Class, school, name = "DreamCard", "Nature", "Dream"
	requireTarget, mana = True, 1
	index = "EXPERT1~DreamCard~Spell~1~Nature~Dream~Uncollectible"
	description = "Return an enemy minion to its owner's hand"
	name_CN = "梦境"
	
	def available(self):
		return self.selectableEnemyMinionExists()
	
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard and target.ID != self.ID
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			self.Game.returnMiniontoHand(target)
		return target


class Nightmare(Spell):
	Class, school, name = "DreamCard", "Shadow", "Nightmare"
	requireTarget, mana = True, 0
	index = "EXPERT1~DreamCard~Spell~0~Shadow~Nightmare~Uncollectible"
	description = "Give a minion +4/+4. At the start of your next turn, destroy it."
	name_CN = "噩梦"
	
	def available(self):
		return self.selectableMinionExists()
	
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target and target.onBoard:
			target.buffDebuff(4, 4)
			trig = Trig_Corruption(target)
			trig.ID = self.ID
			target.trigsBoard.append(trig)
			trig.connect()
		return target

class Trig_Corruption(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["TurnStarts"])
		self.inherent = False
		self.ID = 1
	
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and ID == self.ID
	
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.Game.killMinion(None, self.entity)
		self.disconnect()
		try:
			self.entity.trigsBoard.remove(self)
		except:
			pass
	
	def text(self, CHN):
		return "随从会在玩家%d的回合开始时死亡" % self.ID if CHN else "Minion dies at the start of player %d's turn" % self.ID
	
	def selfCopy(self, recipient):
		trig = type(self)(recipient)
		trig.ID = self.ID
		return trig


class YseraAwakens(Spell):
	Class, school, name = "DreamCard", "Nature", "Ysera Awakens"
	requireTarget, mana = False, 3
	index = "EXPERT1~DreamCard~Spell~3~Nature~Ysera Awakens~Uncollectible"
	description = "Deal 5 damage to all minions except Ysera"
	name_CN = "伊瑟拉苏醒"
	
	def text(self, CHN):
		damage = (5 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		return "对除了伊瑟拉之外的所有随从造成%d点伤害" % damage if CHN else "Deal %d damage to all minions except Ysera" % damage
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		damage = (5 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		targets = []
		for minion in self.Game.minionsonBoard(1) + self.Game.minionsonBoard(2):
			if not minion.name.startswith("Ysera"):
				targets.append(minion)
		
		self.dealsAOE(targets, [damage] *len(targets))
		return None


class LaughingSister(Minion):
	Class, race, name = "DreamCard", "", "Laughing Sister"
	mana, attack, health = 2, 3, 5
	index = "EXPERT1~DreamCard~Minion~2~3~5~~Laughing Sister~Uncollectible"
	requireTarget, keyWord, description = False, "", "Can't targeted by spells or Hero Powers"
	name_CN = "欢笑的姐妹"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.marks["Evasive"] = 1


class EmeraldDrake(Minion):
	Class, race, name = "DreamCard", "Dragon", "Emerald Drake"
	mana, attack, health = 4, 7, 6
	index = "EXPERT1~DreamCard~Minion~4~7~6~Dragon~Emerald Drake~Uncollectible"
	requireTarget, keyWord, description = False, "", ""
	name_CN = "翡翠幼龙"


DreamCards = [Dream, Nightmare, YseraAwakens, LaughingSister, EmeraldDrake]


class LeaderofthePack(Spell):
	Class, school, name = "Druid", "", "Leader of the Pack"
	requireTarget, mana = False, 2
	index = "EXPERT1~Druid~Spell~2~~Leader of the Pack~Uncollectible"
	description = "Give your minions +1/+1"
	name_CN = "兽群领袖"
	
	def available(self):
		return True
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		for minion in self.Game.minionsonBoard(self.ID):
			minion.buffDebuff(1, 1)
		return None

class SummonaPanther(Spell):
	Class, school, name = "Druid", "", "Summon a Panther"
	requireTarget, mana = False, 2
	index = "EXPERT1~Druid~Spell~2~~Summon a Panther~Uncollectible"
	description = "Summon a 3/2 Panther"
	name_CN = "召唤猎豹"
	
	def available(self):
		return self.Game.space(self.ID) > 0
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.Game.summon(Panther(self.Game, self.ID), -1, self)
		return None


class Panther(Minion):
	Class, race, name = "Druid", "Beast", "Panther"
	mana, attack, health = 2, 3, 2
	index = "EXPERT1~Druid~Minion~2~3~2~Beast~Panther~Uncollectible"
	requireTarget, keyWord, description = False, "", ""
	name_CN = "猎豹"


class Treant_Classic(Minion):
	Class, race, name = "Druid", "", "Treant"
	mana, attack, health = 2, 2, 2
	index = "EXPERT1~Druid~Minion~2~2~2~~Treant~Uncollectible"
	requireTarget, keyWord, description = False, "", ""
	name_CN = "树人"


class Treant_Classic_Taunt(Minion):
	Class, race, name = "Druid", "", "Treant"
	mana, attack, health = 2, 2, 2
	index = "EXPERT1~Druid~Minion~2~2~2~~Treant~Taunt~Uncollectible"
	requireTarget, keyWord, description = False, "Taunt", "Taunt"
	name_CN = "树人"


class EvolveSpines(Spell):
	Class, school, name = "Druid", "", "Evolve Spines"
	requireTarget, mana = False, 3
	index = "OG~Druid~Spell~3~~Evolve Spines~Uncollectible"
	description = "Give your hero +4 Attack this turn"
	name_CN = "脊刺异变"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.Game.heroes[self.ID].gainAttack(4)
		return None


class EvolveScales(Spell):
	Class, school, name = "Druid", "", "Evolve Scales"
	requireTarget, mana = False, 3
	index = "OG~Druid~Spell~3~~Evolve Scales~Uncollectible"
	description = "Gain 8 Armor"
	name_CN = "鳞甲异变"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.Game.heroes[self.ID].gainsArmor(8)
		return None


class DruidoftheClaw_Charge(Minion):
	Class, race, name = "Druid", "Beast", "Druid of the Claw"
	mana, attack, health = 5, 5, 4
	index = "EXPERT1~Druid~Minion~5~5~4~Beast~Druid of the Claw~Rush~Uncollectible"
	requireTarget, keyWord, description = False, "Rush", "Rush"
	name_CN = "利爪德鲁伊"


class DruidoftheClaw_Taunt(Minion):
	Class, race, name = "Druid", "Beast", "Druid of the Claw"
	mana, attack, health = 5, 5, 6
	index = "EXPERT1~Druid~Minion~5~5~6~Beast~Druid of the Claw~Taunt~Uncollectible"
	requireTarget, keyWord, description = False, "Taunt", "Taunt"
	name_CN = "利爪德鲁伊"


class DruidoftheClaw_Both(Minion):
	Class, race, name = "Druid", "Beast", "Druid of the Claw"
	mana, attack, health = 5, 5, 6
	index = "EXPERT1~Druid~Minion~5~5~6~Beast~Druid of the Claw~Taunt~Rush~Uncollectible"
	requireTarget, keyWord, description = False, "Taunt,Rush", "Taunt, Rush"
	name_CN = "利爪德鲁伊"


class RampantGrowth(Spell):
	Class, school, name = "Druid", "Nature", "Rampant Growth"
	requireTarget, mana = False, 6
	index = "EXPERT1~Druid~Spell~6~Nature~Rampant Growth~Uncollectible"
	description = "Gain 2 Mana Crystals"
	name_CN = "快速生长"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.Game.Manas.gainManaCrystal(2, self.ID)
		return None


class Enrich(Spell):
	Class, school, name = "Druid", "Nature", "Enrich"
	requireTarget, mana = False, 6
	index = "EXPERT1~Druid~Spell~6~Nature~Enrich~Uncollectible"
	description = "Draw 3 cards"
	name_CN = "摄取养分"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.Game.Hand_Deck.drawCard(self.ID)
		self.Game.Hand_Deck.drawCard(self.ID)
		self.Game.Hand_Deck.drawCard(self.ID)
		return None


class Snake(Minion):
	Class, race, name = "Hunter", "Beast", "Snake"
	mana, attack, health = 1, 1, 1
	index = "EXPERT1~Hunter~Minion~1~1~1~Beast~Snake~Uncollectible"
	requireTarget, keyWord, description = False, "", ""
	name_CN = "蛇"


class Huffer(Minion):
	Class, race, name = "Hunter", "Beast", "Huffer"
	mana, attack, health = 3, 4, 2
	index = "BASIC~Hunter~Minion~3~4~2~Beast~Huffer~Charge~Uncollectible"
	requireTarget, keyWord, description = False, "Charge", "Charge"
	name_CN = "霍弗"


class Leokk(Minion):
	Class, race, name = "Hunter", "Beast", "Leokk"
	mana, attack, health = 3, 2, 4
	index = "BASIC~Hunter~Minion~3~2~4~Beast~Leokk~Uncollectible"
	requireTarget, keyWord, description = False, "", "Your other minions have +1 Attack"
	name_CN = "雷欧克"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.auras["Your other minions have +1 Attack"] = StatAura_Others(self, 1, 0)


class Misha(Minion):
	Class, race, name = "Hunter", "Beast", "Misha"
	mana, attack, health = 3, 4, 4
	index = "BASIC~Hunter~Minion~3~4~4~Beast~Misha~Taunt~Uncollectible"
	requireTarget, keyWord, description = False, "Taunt", "Taunt"
	name_CN = "米莎"


class Hyena_Classic(Minion):
	Class, race, name = "Hunter", "Beast", "Hyena"
	mana, attack, health = 2, 2, 2
	index = "EXPERT1~Hunter~Minion~2~2~2~Beast~Hyena~Uncollectible"
	requireTarget, keyWord, description = False, "", ""
	name_CN = "土狼"


class ManaWyrm(Minion):
	Class, race, name = "Mage", "", "Mana Wyrm"
	mana, attack, health = 1, 1, 2
	index = "EXPERT1~Mage~Minion~1~1~2~~Mana Wyrm"
	requireTarget, keyWord, description = False, "", "Whenever you cast a spell, gain 1 Attack"
	name_CN = "法力浮龙"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_ManaWyrm(self)]


class Trig_ManaWyrm(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["SpellPlayed"])
	
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject.ID == self.entity.ID
	
	def text(self, CHN):
		return "每当你施放一个法术，便获得+1攻击力" if CHN else "Whenever you cast a spell, gain 1 Attack"
	
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.buffDebuff(1, 0)


class Defender(Minion):
	Class, race, name = "Paladin", "", "Defender"
	mana, attack, health = 1, 2, 1
	index = "EXPERT1~Paladin~Minion~1~2~1~~Defender~Uncollectible"
	requireTarget, keyWord, description = False, "", ""
	name_CN = "防御者"


class Ashbringer(Weapon):
	Class, name, description = "Paladin", "Ashbringer", ""
	mana, attack, durability = 5, 5, 3
	index = "EXPERT1~Paladin~Weapon~5~5~3~Ashbringer~Legendary~Uncollectible"
	name_CN = "灰烬使者"


class SpiritWolf(Minion):
	Class, race, name = "Shaman", "", "Spirit Wolf"
	mana, attack, health = 2, 2, 3
	index = "EXPERT1~Shaman~Minion~2~2~3~~Spirit Wolf~Taunt~Uncollectible"
	requireTarget, keyWord, description = False, "Taunt", "Taunt"
	name_CN = "幽灵狼"


class Frog(Minion):
	Class, race, name = "Neutral", "Beast", "Frog"
	mana, attack, health = 0, 0, 1
	index = "BASIC~Neutral~Minion~0~0~1~Beast~Frog~Taunt~Uncollectible"
	requireTarget, keyWord, description = False, "Taunt", "Taunt"
	name_CN = "青蛙"


class Shadowbeast(Minion):
	Class, race, name = "Warlock", "", "Shadowbeast"
	mana, attack, health = 1, 1, 1
	index = "OG~Warlock~Minion~1~1~1~~Shadowbeast~Uncollectible"
	requireTarget, keyWord, description = False, "", ""
	name_CN = "暗影兽"


class Imp(Minion):
	Class, race, name = "Warlock", "Demon", "Imp"
	mana, attack, health = 1, 1, 1
	index = "EXPERT1~Warlock~Minion~1~1~1~Demon~Imp~Uncollectible"
	requireTarget, keyWord, description = False, "", ""
	name_CN = "小鬼"


class BloodFury(Weapon):
	Class, name, description = "Warlock", "Blood Fury", ""
	mana, attack, durability = 3, 3, 8
	index = "EXPERT1~Warlock~Weapon~3~3~8~Blood Fury~Uncollectible"
	name_CN = "血怒"
	
	
class Infernal(Minion):
	Class, race, name = "Warlock", "Demon", "Infernal"
	mana, attack, health = 6, 6, 6
	index = "EXPERT1~Warlock~Minion~6~6~6~Demon~Infernal~Uncollectible"
	requireTarget, keyWord, description = False, "", ""
	name_CN = "地狱火"


""""""
class Nerubian(Minion):
	Class, race, name = "Neutral", "", "Nerubian"
	mana, attack, health = 4, 4, 4
	index = "NAXX~Neutral~Minion~4~4~4~~Nerubian~Uncollectible"
	requireTarget, keyWord, description = False, "", ""
	name_CN = "蛛魔"


class BoomBot(Minion):
	Class, race, name = "Neutral", "Mech", "Boom Bot"
	mana, attack, health = 1, 1, 1
	index = "GVG~Neutral~Minion~1~1~1~Mech~Boom Bot~Deathrattle~Uncollectible"
	requireTarget, keyWord, description = False, "", "Deathrattle: Deal 1~4 damage to a random enemy"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.deathrattles = [Deal1to4DamagetoaRandomEnemy(self)]
		
class Deal1to4DamagetoaRandomEnemy(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		curGame = self.entity.Game
		if curGame.mode == 0:
			enemy, damage = None, 0
			if curGame.guides:
				i, where, damage = curGame.guides.pop(0)
				if where: enemy = curGame.find(i, where)
			else:
				targets = curGame.charsAlive(3-self.entity.ID)
				if targets:
					enemy, damage = npchoice(targets), np.random.randint(1, 5)
					curGame.fixedGuides.append((enemy.pos, enemy.type+str(enemy.ID), damage))
				else:
					curGame.fixedGuides.append((0, '', 0))
			if enemy:
				self.entity.dealsDamage(enemy, damage)
				
				

class GoldenKobold(Minion):
	Class, race, name = "Neutral", "", "Golden Kobold"
	mana, attack, health = 3, 6, 6
	index = "LOOTAPALOOZA~Neutral~Minion~3~6~6~~Golden Kobold~Taunt~Battlecry~Legendary~Uncollectible"
	requireTarget, keyWord, description = False, "Taunt", "Taunt. Battlecry: Replace your hand with Legendary minions"
	poolIdentifier = "Legendary Minions"
	@classmethod
	def generatePool(cls, pools):
		return "Legendary Minions", list(pools.LegendaryMinions.values())
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if curGame.mode == 0:
			if curGame.guides:
				hand = curGame.guides.pop(0)
			else:
				hand = tuple(npchoice(self.rngPool("Legendary Minions"), len(curGame.Hand_Deck.hands[self.ID]), replace=True))
				curGame.fixedGuides.append(hand)
			if hand:
				curGame.Hand_Deck.extractfromHand(None, self.ID, all=True)
				curGame.Hand_Deck.addCardtoHand(hand, self.ID, "type")
		return None
		
class TolinsGoblet(Spell):
	Class, school, name = "Neutral", "", "Tolin's Goblet"
	requireTarget, mana = False, 3
	index = "LOOTAPALOOZA~Neutral~Spell~3~~Tolin's Goblet~Uncollectible"
	description = "Draw a card. Fill your hand with copies of it"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		card, mana = self.Game.Hand_Deck.drawCard(self.ID)
		if card and self.Game.Hand_Deck.handNotFull(self.ID):
			copies = [card.selfCopy(self.ID, self) for i in range(self.Game.Hand_Deck.spaceinHand(self.ID))]
			self.Game.Hand_Deck.addCardtoHand(copies, self.ID)
		return None
		
class WondrousWand(Spell):
	Class, school, name = "Neutral", "", "Wondrous Wand"
	requireTarget, mana = False, 3
	index = "LOOTAPALOOZA~Neutral~Spell~3~~Wondrous Wand~Uncollectible"
	description = "Draw 3 cards. Reduce their costs to (0)"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		for i in range(3):
			card, mana = self.Game.Hand_Deck.drawCard(self.ID)
			if card:
				ManaMod(card, changeby=0, changeto=0).applies()
				self.Game.Manas.calcMana_Single(card)
		return None
		
class ZarogsCrown(Spell):
	Class, school, name = "Neutral", "", "Zarog's Crown"
	requireTarget, mana = False, 3
	index = "LOOTAPALOOZA~Neutral~Spell~3~~Zarog's Crown~Uncollectible"
	description = "Discover a Legendary minion. Summon two copies of it"
	poolIdentifier = "Legendary Minions as Druid to Summon"
	@classmethod
	def generatePool(cls, pools):
		classCards = {s : [value for key, value in pools.ClassCards[s].items() if "~Minion~" in key and "~Legendary" in key] for s in pools.Classes}
		classCards["Neutral"] = [value for key, value in pools.NeutralCards.items() if "~Minion~" in key and "~Legendary" in key]
		return ["Legendary Minions as %s to Summon"%Class for Class in pools.Classes], \
			[classCards[Class]+classCards["Neutral"] for Class in pools.Classes]
			
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if curGame.space(self.ID):
			if curGame.mode == 0:
				if curGame.guides:
					minion = curGame.guides.pop(0)
					curGame.summon([minion(self.Game, self.ID) for i in range(2)], (-1, "totheRightEnd"), self)
				else:
					key = "Legendary Minions as %s to Summon"%classforDiscover(self)
					if self.ID != curGame.turn or "byOthers" in comment:
						minion = npchoice(self.rngPool(key))
						curGame.fixedGuides.append(minion)
						curGame.summon([minion(self.Game, self.ID) for i in range(2)], (-1, "totheRightEnd"), self)
					else:
						minions = npchoice(self.rngPool(key), 3, replace=False)
						curGame.options = [minion(curGame, self.ID) for minion in minions]
						curGame.Discover.startDiscover(self)
		return None
		
	def discoverDecided(self, option, pool):
		self.Game.fixedGuides.append(type(option))
		self.Game.summon([option, type(option)(self.Game, self.ID)], (-1, "totheRightEnd"), self)
		

class Bomb(Spell):
	Class, school, name = "Neutral", "", "Bomb"
	requireTarget, mana = False, 5
	index = "BOOMSDAY~Neutral~Spell~5~~Bomb~Casts When Drawn~Uncollectible"
	description = "Casts When Drawn. Deal 5 damage to your hero"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		damage = (5 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		self.dealsDamage(self.Game.heroes[self.ID], damage)
		return None


class EtherealLackey(Minion):
	Class, race, name = "Neutral", "", "Ethereal Lackey"
	mana, attack, health = 1, 1, 1
	index = "DALARAN~Neutral~Minion~1~1~1~~Ethereal Lackey~Battlecry~Uncollectible"
	requireTarget, keyWord, description = False, "", "Battlecry: Discover a spell"
	poolIdentifier = "Druid Spells"
	@classmethod
	def generatePool(cls, pools):
		return [Class + " Spells" for Class in pools.Classes], \
			   [[value for key, value in pools.ClassCards[Class].items() if "~Spell~" in key] for Class in pools.Classes]

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if self.ID == curGame.turn:
			if curGame.mode == 0:
				pool = tuple(self.rngPool(classforDiscover(self) + " Spells"))
				if curGame.guides:
					curGame.Hand_Deck.addCardtoHand(curGame.guides.pop(0), self.ID, byType=True, byDiscover=True, creator=type(self), possi=pool)
				else:
					if "byOthers" in comment:
						spell = npchoice(pool)
						curGame.fixedGuides.append(spell)
						curGame.Hand_Deck.addCardtoHand(spell, self.ID, byType=True, byDiscover=True, creator=type(self), possi=pool)
					else:
						spells = npchoice(pool, 3, replace=False)
						curGame.options = [spell(curGame, self.ID) for spell in spells]
						curGame.Discover.startDiscover(self, pool)
		return None

	def discoverDecided(self, option, pool):
		self.Game.fixedGuides.append(type(option))
		self.Game.Hand_Deck.addCardtoHand(option, self.ID, byDiscover=True, creator=type(self), possi=pool)


class FacelessLackey(Minion):
	Class, race, name = "Neutral", "", "Faceless Lackey"
	mana, attack, health = 1, 1, 1
	index = "DALARAN~Neutral~Minion~1~1~1~~Faceless Lackey~Battlecry~Uncollectible"
	requireTarget, keyWord, description = False, "", "Battlecry: Summon a 2-Cost minion"
	poolIdentifier = "2-Cost Minions to Summon"

	@classmethod
	def generatePool(cls, pools):
		return "2-Cost Minions to Summon", list(pools.MinionsofCost[2].values())

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if curGame.mode == 0:
			if curGame.guides:
				minion = curGame.guides.pop(0)
			else:
				minion = npchoice(self.rngPool("2-Cost Minions to Summon"))
				curGame.fixedGuides.append(minion)
			curGame.summon(minion(curGame, self.ID), self.pos + 1, self)
		return None


class GoblinLackey(Minion):
	Class, race, name = "Neutral", "", "Goblin Lackey"
	mana, attack, health = 1, 1, 1
	index = "DALARAN~Neutral~Minion~1~1~1~~Goblin Lackey~Battlecry~Uncollectible"
	requireTarget, keyWord, description = True, "", "Battlecry: Give a friendly minion +1 Attack and Rush"

	def targetExists(self, choice=0):
		return self.selectableFriendlyMinionExists()

	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.ID == self.ID and target != self and target.onBoard

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			target.buffDebuff(1, 0)
			target.getsStatus("Rush")
		return target


class KoboldLackey(Minion):
	Class, race, name = "Neutral", "", "Kobold Lackey"
	mana, attack, health = 1, 1, 1
	index = "DALARAN~Neutral~Minion~1~1~1~~Kobold Lackey~Battlecry~Uncollectible"
	requireTarget, keyWord, description = True, "", "Battlecry: Deal 2 damage"

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			self.dealsDamage(target, 2)
		return target


class WitchyLackey(Minion):
	Class, race, name = "Neutral", "", "Witchy Lackey"
	mana, attack, health = 1, 1, 1
	index = "DALARAN~Neutral~Minion~1~1~1~~Witchy Lackey~Battlecry~Uncollectible"
	requireTarget, keyWord, description = True, "", "Battlecry: Transform a friendly minion into one that costs (1) more"
	poolIdentifier = "1-Cost Minions to Summon"

	@classmethod
	def generatePool(cls, pools):
		return ["%d-Cost Minions to Summon" % cost for cost in pools.MinionsofCost], \
			   [list(pools.MinionsofCost[cost].values()) for cost in pools.MinionsofCost]

	def targetExists(self, choice=0):
		return self.selectableFriendlyMinionExists()

	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.ID == self.ID and target != self and target.onBoard

	# 不知道如果目标随从被返回我方手牌会有什么结算，可能是在手牌中被进化
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			curGame = self.Game
			if curGame.mode == 0:
				if curGame.guides:
					newMinion = curGame.guides.pop(0)
				else:
					cost = type(target).mana + 1
					while "%d-Cost Minions to Summon"%cost not in curGame.RNGPools:
						cost -= 1
					newMinion = npchoice(self.rngPool("%d-Cost Minions to Summon" % cost))
					curGame.fixedGuides.append(newMinion)
				newMinion = newMinion(curGame, target.ID)
				curGame.transform(target, newMinion)
				target = newMinion
		return target


class TitanicLackey(Minion):
	Class, race, name = "Neutral", "", "Titanic Lackey"
	mana, attack, health = 1, 1, 1
	index = "ULDUM~Neutral~Minion~1~1~1~~Titanic Lackey~Battlecry~Uncollectible"
	requireTarget, keyWord, description = True, "", "Battlecry: Give a friendly minion +2 Health"

	def targetExists(self, choice=0):
		return self.selectableFriendlyMinionExists(choice)

	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.ID == self.ID and target != self and target.onBoard

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			target.buffDebuff(0, 2)
			target.getsStatus("Taunt")
		return target


class DraconicLackey(Minion):
	Class, race, name = "Neutral", "", "Draconic Lackey"
	mana, attack, health = 1, 1, 1
	index = "DRAGONS~Neutral~Minion~1~1~1~~Draconic Lackey~Battlecry~Uncollectible"
	requireTarget, keyWord, description = False, "", "Battlecry: Discover a Dragon"
	poolIdentifier = "Dragons as Druid"

	@classmethod
	def generatePool(cls, pools):
		classCards = {s: [] for s in pools.ClassesandNeutral}
		for key, value in pools.MinionswithRace["Dragon"].items():
			classCards[key.split('~')[1]].append(value)
		return ["Dragons as " + Class for Class in pools.Classes], \
			   [classCards[Class] + classCards["Neutral"] for Class in pools.Classes]

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if self.ID == curGame.turn:
			if curGame.mode == 0:
				if curGame.guides:
					curGame.Hand_Deck.addCardtoHand(curGame.guides.pop(0), self.ID, "type", byDiscover=True)
				else:
					key = "Dragons as " + classforDiscover(self)
					if "byOthers" in comment:
						dragon = npchoice(self.rngPool(key))
						curGame.fixedGuides.append(dragon)
						curGame.Hand_Deck.addCardtoHand(dragon, self.ID, "type", byDiscover=True)
					else:
						dragons = npchoice(self.rngPool(key), 3, replace=False)
						curGame.options = [dragon(curGame, self.ID) for dragon in dragons]
						curGame.Discover.startDiscover(self)
		return None

	def discoverDecided(self, option, pool):
		self.Game.fixedGuides.append(type(option))
		self.Game.Hand_Deck.addCardtoHand(option, self.ID, byDiscover=True)

Lackeys = [DraconicLackey, EtherealLackey, FacelessLackey, GoblinLackey, KoboldLackey, TitanicLackey, WitchyLackey]




AcrossPacks_Indices = {"Hero: Demon Hunter": Illidan, "Hero: Druid": Malfurion,
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
					
					"BASIC~Neutral~Spell~0~~The Coin~Uncollectible": TheCoin,
					"BASIC~Paladin~Minion~1~1~1~~Silver Hand Recruit~Uncollectible": SilverHandRecruit,
					"BASIC~Rogue~Weapon~1~1~2~Wicked Knife~Uncollectible": WickedKnife,
					"TGT~Rogue~Weapon~1~2~2~Poisoned Dagger~Uncollectible": PoisonedDagger,
					"BASIC~Shaman~Minion~1~1~1~Totem~Searing Totem~Uncollectible": SearingTotem,
					"BASIC~Shaman~Minion~1~0~2~Totem~Stoneclaw Totem~Taunt~Uncollectible": StoneclawTotem,
					"BASIC~Shaman~Minion~1~0~2~Totem~Healing Totem~Uncollectible": HealingTotem,
					"BASIC~Shaman~Minion~1~0~2~Totem~Strength Totem~Uncollectible": StrengthTotem,
					"BASIC~Demon Hunter~Minion~1~1~1~~Illidari Initiate~Rush~Uncollectible": IllidariInitiate,
					"BASIC~Druid~Spell~0~~Excess Mana~Uncollectible": ExcessMana,
					"BASIC~Hunter~Minion~3~4~2~Beast~Huffer~Charge~Uncollectible": Huffer,
					"BASIC~Hunter~Minion~3~2~4~Beast~Leokk~Uncollectible": Leokk,
					"BASIC~Hunter~Minion~3~4~4~Beast~Misha~Taunt~Uncollectible": Misha,
					"BASIC~Mage~Minion~4~3~6~Elemental~Water Elemental": WaterElemental_Basic,
					"BASIC~Warrior~Weapon~3~3~2~Fiery War Axe": FieryWarAxe_Basic,
					
					"EXPERT1~Neutral~Spell~1~~Bananas~Uncollectible": Bananas,
					"EXPERT1~Neutral~Minion~1~1~1~~Violet Apprentice~Uncollectible": VioletApprentice,
					"EXPERT1~Neutral~Minion~1~1~1~Dragon~Whelp~Uncollectible": Whelp,
					"EXPERT1~Neutral~Minion~5~5~5~~Baine Bloodhoof~Legendary~Uncollectible": BaineBloodhoof,
					"EXPERT1~DreamCard~Spell~1~Nature~Dream~Uncollectible": Dream,
					"EXPERT1~DreamCard~Spell~0~Shadow~Nightmare~Uncollectible": Nightmare,
					"EXPERT1~DreamCard~Spell~3~Nature~Ysera Awakens~Uncollectible": YseraAwakens,
					"EXPERT1~DreamCard~Minion~2~3~5~~Laughing Sister~Uncollectible": LaughingSister,
					"EXPERT1~DreamCard~Minion~4~7~6~Dragon~Emerald Drake~Uncollectible": EmeraldDrake,
					"EXPERT1~Druid~Spell~2~~Leader of the Pack~Uncollectible": LeaderofthePack,
					"EXPERT1~Druid~Spell~2~~Summon a Panther~Uncollectible": SummonaPanther,
					"EXPERT1~Druid~Minion~2~3~2~Beast~Panther~Uncollectible": Panther,
					"EXPERT1~Druid~Minion~2~2~2~~Treant~Uncollectible": Treant_Classic,
					"EXPERT1~Druid~Minion~2~2~2~~Treant~Taunt~Uncollectible": Treant_Classic_Taunt,
					"OG~Druid~Spell~3~~Evolve Spines~Uncollectible": EvolveSpines,
					"OG~Druid~Spell~3~~Evolve Scales~Uncollectible": EvolveScales,
					"EXPERT1~Druid~Minion~5~5~4~Beast~Druid of the Claw~Rush~Uncollectible": DruidoftheClaw_Charge,
					"EXPERT1~Druid~Minion~5~5~6~Beast~Druid of the Claw~Taunt~Uncollectible": DruidoftheClaw_Taunt,
					"EXPERT1~Druid~Minion~5~5~6~Beast~Druid of the Claw~Taunt~Rush~Uncollectible": DruidoftheClaw_Both,
					"EXPERT1~Druid~Spell~6~Nature~Rampant Growth~Uncollectible": RampantGrowth,
					"EXPERT1~Druid~Spell~6~Nature~Enrich~Uncollectible": Enrich,
					"EXPERT1~Hunter~Minion~1~1~1~Beast~Snake~Uncollectible": Snake,
					"EXPERT1~Hunter~Minion~2~2~2~Beast~Hyena~Uncollectible": Hyena_Classic,
					"EXPERT1~Mage~Minion~1~1~2~~Mana Wyrm": ManaWyrm,
					"EXPERT1~Mage~Spell~10~Fire~Pyroblast": Pyroblast,
					"EXPERT1~Paladin~Minion~1~2~1~~Defender~Uncollectible": Defender,
					"EXPERT1~Paladin~Weapon~5~5~3~Ashbringer~Legendary~Uncollectible": Ashbringer,
					"EXPERT1~Shaman~Minion~2~2~3~~Spirit Wolf~Taunt~Uncollectible": SpiritWolf,
					"BASIC~Neutral~Minion~0~0~1~Beast~Frog~Taunt~Uncollectible": Frog,
					"EXPERT1~Warlock~Minion~1~1~1~Demon~Imp~Uncollectible": Imp,
					"EXPERT1~Warlock~Weapon~3~3~8~Blood Fury~Uncollectible": BloodFury,
					"EXPERT1~Warlock~Minion~6~6~6~Demon~Infernal~Uncollectible": Infernal,
					"NAXX~Neutral~Minion~4~4~4~~Nerubian~Uncollectible": Nerubian,
					"GVG~Neutral~Minion~1~1~1~Mech~Boom Bot~Deathrattle~Uncollectible": BoomBot,
					"LOOTAPALOOZA~Neutral~Minion~3~6~6~~Golden Kobold~Taunt~Battlecry~Legendary~Uncollectible": GoldenKobold,
					"LOOTAPALOOZA~Neutral~Spell~3~~Tolin's Goblet~Uncollectible": TolinsGoblet,
					"LOOTAPALOOZA~Neutral~Spell~3~~Wondrous Wand~Uncollectible": WondrousWand,
					"LOOTAPALOOZA~Neutral~Spell~3~~Zarog's Crown~Uncollectible": ZarogsCrown,
					"BOOMSDAY~Neutral~Spell~5~~Bomb~Casts When Drawn~Uncollectible": Bomb,
					"DALARAN~Neutral~Minion~1~1~1~~Ethereal Lackey~Battlecry~Uncollectible": EtherealLackey,
					"DALARAN~Neutral~Minion~1~1~1~~Faceless Lackey~Battlecry~Uncollectible": FacelessLackey,
					"DALARAN~Neutral~Minion~1~1~1~~Goblin Lackey~Battlecry~Uncollectible": GoblinLackey,
					"DALARAN~Neutral~Minion~1~1~1~~Kobold Lackey~Battlecry~Uncollectible": KoboldLackey,
					"DALARAN~Neutral~Minion~1~1~1~~Witchy Lackey~Battlecry~Uncollectible": WitchyLackey,
					"ULDUM~Neutral~Minion~1~1~1~~Titanic Lackey~Battlecry~Uncollectible": TitanicLackey,
					"DRAGONS~Neutral~Minion~1~1~1~~Draconic Lackey~Battlecry~Uncollectible": DraconicLackey,
					}

