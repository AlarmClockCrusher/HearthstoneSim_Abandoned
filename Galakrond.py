from CardTypes import *
from Triggers_Auras import *
from numpy.random import choice as npchoice
from numpy.random import randint as nprandint
from numpy.random import shuffle as npshuffle
from numpy import inf as npinf

from AcrossPacks import TheCoin, SilverHandRecruit, BoomBot, Lackeys

"""Awakening of Galakrond"""

"""Neutral cards"""
class SkydivingInstructor(Minion):
	Class, race, name = "Neutral", "", "Skydiving Instructor"
	mana, attack, health = 3, 2, 2
	index = "YEAR_OF_THE_DRAGON~Neutral~Minion~3~2~2~~Skydiving Instructor~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Summon a 1-Cost minion from your deck"
	name_CN = "伞降教官"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		indices = [i for i, card in enumerate(self.Game.Hand_Deck.decks[self.ID]) if card.type == "Minion" and card.mana == 1]
		if indices: self.Game.summonfrom(npchoice(indices), self.ID, self.pos+1, self, source='D')
		return None
		
		
class Hailbringer(Minion):
	Class, race, name = "Neutral", "Elemental", "Hailbringer"
	mana, attack, health = 5, 3, 4
	index = "YEAR_OF_THE_DRAGON~Neutral~Minion~5~3~4~Elemental~Hailbringer~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Summon two 1/1 Ice Shards that Freeze"
	name_CN = "冰雹使者"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		pos = (self.pos, "leftandRight") if self.onBoard else (-1, "totheRightEnd")
		self.summon([IceShard(self.Game, self.ID) for i in range(2)], pos)
		return None
		
class IceShard(Minion):
	Class, race, name = "Neutral", "Elemental", "Ice Shard"
	mana, attack, health = 1, 1, 1
	index = "YEAR_OF_THE_DRAGON~Neutral~Minion~1~1~1~Elemental~Ice Shard~Uncollectible"
	requireTarget, keyWord, description = False, "", "Freeze any character damaged by this minion"
	name_CN = "寒冰碎片"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_IceShard(self)]
		
class Trig_IceShard(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["MinionTakesDmg", "HeroTakesDmg"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject == self.entity
		
	def text(self, CHN):
		return "冻结任何受到该随从伤害的角色" if CHN \
				else "Freeze any character damaged by this minion"
				
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		target.getsStatus("Frozen")
		
		
class LicensedAdventurer(Minion):
	Class, race, name = "Neutral", "", "Licensed Adventurer"
	mana, attack, health = 2, 3, 2
	index = "YEAR_OF_THE_DRAGON~Neutral~Minion~2~3~2~~Licensed Adventurer~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: If you control a Quest, add a Coin to your hand"
	name_CN = "资深探险者"
	def effCanTrig(self):
		self.effectViable = self.Game.Secrets.mainQuests[self.ID] != [] or self.Game.Secrets.sideQuests[self.ID] != []
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if self.Game.Secrets.mainQuests[self.ID] != [] or self.Game.Secrets.sideQuests[self.ID] != []:
			self.addCardtoHand(TheCoin, self.ID)
		return None
		
class FrenziedFelwing(Minion):
	Class, race, name = "Neutral", "Demon", "Frenzied Felwing"
	mana, attack, health = 4, 3, 2
	index = "YEAR_OF_THE_DRAGON~Neutral~Minion~4~3~2~Demon~Frenzied Felwing"
	requireTarget, keyWord, description = False, "", "Costs (1) less for each damage dealt to your opponent this turn"
	name_CN = "狂暴邪翼蝠"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsHand = [Trig_FrenziedFelwing(self)]
		
	def selfManaChange(self):
		if self.inHand:
			manaReduction = self.Game.Counters.dmgonHeroThisTurn[3-self.ID]
			self.mana -= manaReduction
			self.mana = max(0, self.mana)
			
class Trig_FrenziedFelwing(TrigHand):
	def __init__(self, entity):
		super().__init__(entity, ["HeroTakesDmg"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.inHand and target == self.entity.Game.heroes[3-self.entity.ID]
		
	def text(self, CHN):
		return "在本回合中，你的对手每受到1点伤害，该牌的法力值消耗便减少(1)点" if CHN \
				else "Costs (1) less for each damage dealt to your opponent this turn"
				
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.Game.Manas.calcMana_Single(self.entity)
		
		
class EscapedManasaber(Minion):
	Class, race, name = "Neutral", "Beast", "Escaped Manasaber"
	mana, attack, health = 4, 3, 5
	index = "YEAR_OF_THE_DRAGON~Neutral~Minion~4~3~5~Beast~Escaped Manasaber~Stealth"
	requireTarget, keyWord, description = False, "Stealth", "Stealth. Whenever this attacks, gain 1 Mana Crystal this turn only"
	name_CN = "奔逃的魔晶豹"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_EscapedManasaber(self)]
		
class Trig_EscapedManasaber(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["MinionAttackingMinion", "MinionAttackingHero"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject == self.entity and self.entity.onBoard
		
	def text(self, CHN):
		return "每当该随从攻击，便获得一个仅限本回合可用的法力水晶" if CHN else "Whenever this attacks, gain 1 Mana Crystal this turn only"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		if self.entity.Game.Manas.manas[self.entity.ID] < 10:
			self.entity.Game.Manas.manas[self.entity.ID] += 1
			
			
class BoompistolBully(Minion):
	Class, race, name = "Neutral", "", "Boompistol Bully"
	mana, attack, health = 5, 5, 5
	index = "YEAR_OF_THE_DRAGON~Neutral~Minion~5~5~5~~Boompistol Bully~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Enemy Battlecry cards cost (5) more next turn"
	name_CN = "持枪恶霸"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.Game.Manas.CardAuras_Backup.append(GameManaAura_InTurnBattlecry5More(self.Game, 3-self.ID))
		return None
		
class GameManaAura_InTurnBattlecry5More(TempManaEffect):
	def __init__(self, Game, ID, changeby=0, changeto=-1):
		super().__init__(Game, ID, +5, -1)
		self.signals = ["CardEntersHand"]
		
	def applicable(self, subject):
		return subject.ID == self.ID and "~Battlecry" in subject.index
		
		
class GrandLackeyErkh(Minion):
	Class, race, name = "Neutral", "", "Grand Lackey Erkh"
	mana, attack, health = 4, 2, 3
	index = "YEAR_OF_THE_DRAGON~Neutral~Minion~4~2~3~~Grand Lackey Erkh~Legendary"
	requireTarget, keyWord, description = False, "", "After you play a Lackey, add a Lackey to your hand"
	name_CN = "高级跟班厄尔克"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_GrandLackeyErkh(self)]
		
class Trig_GrandLackeyErkh(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["MinionBeenPlayed"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject.ID == self.entity.ID and subject.name.endswith(" Lackey")
		
	def text(self, CHN):
		return "在你使用一张跟班牌后，将一张跟班牌置入你的手牌" if CHN \
				else "After you play a Lackey, add a Lackey to your hand"
				
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.addCardtoHand(npchoice(Lackeys), self.entity.ID)
		
		
class SkyGenralKragg(Minion):
	Class, race, name = "Neutral", "Pirate", "Sky Gen'ral Kragg"
	mana, attack, health = 4, 2, 3
	index = "YEAR_OF_THE_DRAGON~Neutral~Minion~4~2~3~Pirate~Sky Gen'ral Kragg~Taunt~Battlecry~Legendary"
	requireTarget, keyWord, description = False, "Taunt", "Taunt. Battlecry: If you've played a Quest this game, summon a 4/2 Parrot with Rush"
	name_CN = "天空上将库拉格"
	def effCanTrig(self):
		self.effectViable = self.Game.Counters.hasPlayedQuestThisGame[self.ID]
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if self.Game.Counters.hasPlayedQuestThisGame[self.ID]:
			self.summon(Sharkbait(self.Game, self.ID), self.pos+1)
		return None
		
class Sharkbait(Minion):
	Class, race, name = "Neutral", "Beast", "Sharkbait"
	mana, attack, health = 4, 4, 2
	index = "YEAR_OF_THE_DRAGON~Neutral~Minion~4~4~2~Beast~Sharkbait~Rush~Legendary~Uncollectible"
	requireTarget, keyWord, description = False, "Rush", "Rush"
	name_CN = "鲨鱼饵"
	
	
"""Druid cards"""
class RisingWinds(Spell):
	Class, school, name = "Druid", "", "Rising Winds"
	requireTarget, mana = False, 2
	index = "YEAR_OF_THE_DRAGON~Druid~Spell~2~Rising Winds~Twinspell~Choose One"
	description = "Twinspell. Choose One- Draw a card; or Summon a 3/2 Eagle"
	name_CN = "乘风而起"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.twinSpell = 1
		self.twinSpellCopy = RisingWinds2
		self.options = [TakeFlight_Option(self), SwoopIn_Option(self)]
		
	def need2Choose(self):
		return True
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if choice < 1:
			self.Game.Hand_Deck.drawCard(self.ID)
		if choice != 0:
			self.summon(Eagle(self.Game, self.ID), -1)
		return None
		
class RisingWinds2(Spell):
	Class, school, name = "Druid", "", "Rising Winds"
	requireTarget, mana = False, 2
	index = "YEAR_OF_THE_DRAGON~Druid~Spell~2~Rising Winds~Choose One~Uncollectible"
	description = "Choose One- Draw a card; or Summon a 3/2 Eagle"
	name_CN = "乘风而起"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.options = [TakeFlight_Option(self), SwoopIn_Option(self)]
		
	def need2Choose(self):
		return True
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if choice < 1:
			self.Game.Hand_Deck.drawCard(self.ID)
		if choice != 0:
			self.summon(Eagle(self.Game, self.ID), -1)
		return None
		
class TakeFlight_Option(Option):
	name, description = "Take Flight", "Draw a card"
	index = "YEAR_OF_THE_DRAGON~Druid~Spell~2~Take Flight~Uncollectible"
	mana, attack, health = 2, -1, -1
	
class SwoopIn_Option(Option):
	name, description = "Swoop In", "Summon a 3/2 Eagle"
	index = "YEAR_OF_THE_DRAGON~Druid~Spell~2~Swoop In~Uncollectible"
	mana, attack, health = 2, -1, -1
	def available(self):
		return self.entity.Game.space(self.entity.ID) > 0
		
class TakeFlight(Spell):
	Class, school, name = "Druid", "", "Take Flight"
	requireTarget, mana = False, 2
	index = "YEAR_OF_THE_DRAGON~Druid~Spell~2~Take Flight~Uncollectible"
	description = "Draw a card"
	name_CN = "雏鹰起飞"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.Game.Hand_Deck.drawCard(self.ID)
		return None
		
class SwoopIn(Spell):
	Class, school, name = "Druid", "", "Swoop In"
	requireTarget, mana = False, 2
	index = "YEAR_OF_THE_DRAGON~Druid~Spell~2~Swoop In~Uncollectible"
	description = "Summon a 3/2 Eagle"
	name_CN = "猛禽飞掠"
	def available(self):
		return self.Game.space(self.ID) > 0
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.summon(Eagle(self.Game, self.ID), -1)
		return None
		
class Eagle(Minion):
	Class, race, name = "Druid", "Beast", "Eagle"
	mana, attack, health = 2, 3, 2
	index = "YEAR_OF_THE_DRAGON~Druid~Minion~2~3~2~Beast~Eagle~Uncollectible"
	requireTarget, keyWord, description = False, "", ""
	name_CN = "鹰"
	
	
class SteelBeetle(Minion):
	Class, race, name = "Druid", "Beast", "Steel Beetle"
	mana, attack, health = 2, 2, 3
	index = "YEAR_OF_THE_DRAGON~Druid~Minion~2~2~3~Beast~Steel Beetle~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: If you're holding a spell that costs (5) or more, gain 5 Armor"
	name_CN = "钢铁甲虫"
	def effCanTrig(self):
		self.effectViable = self.Game.Hand_Deck.holdingSpellwith5CostorMore(self.ID)
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if self.Game.Hand_Deck.holdingSpellwith5CostorMore(self.ID):
			self.Game.heroes[self.ID].gainsArmor(5)
		return None
		
		
class WingedGuardian(Minion):
	Class, race, name = "Druid", "Beast", "Winged Guardian"
	mana, attack, health = 7, 6, 8
	index = "YEAR_OF_THE_DRAGON~Druid~Minion~7~6~8~Beast~Winged Guardian~Taunt~Reborn"
	requireTarget, keyWord, description = False, "Taunt,Reborn", "Taunt, Reborn. Can't be targeted by spells or Hero Powers"
	name_CN = "飞翼守护者"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.marks["Evasive"] = True
		
		
"""Hunter cards"""
class FreshScent(Spell):
	Class, school, name = "Hunter", "", "Fresh Scent"
	requireTarget, mana = True, 2
	index = "YEAR_OF_THE_DRAGON~Hunter~Spell~2~Fresh Scent~Twinspell"
	description = "Twinspell. Given a Beast +2/+2"
	name_CN = "新鲜气息"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.twinSpell = 1
		self.twinSpellCopy = FreshScent2
		
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and "Beast" in target.race and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			target.buffDebuff(2, 2)
		return None
		
class FreshScent2(Spell):
	Class, school, name = "Hunter", "", "Fresh Scent"
	requireTarget, mana = True, 2
	index = "YEAR_OF_THE_DRAGON~Hunter~Spell~2~Fresh Scent~Uncollectible"
	description = "Given a Beast +2/+2"
	name_CN = "新鲜气息"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and "Beast" in target.race and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			target.buffDebuff(2, 2)
		return None
		
		
class ChopshopCopter(Minion):
	Class, race, name = "Hunter", "Mech", "Chopshop Copter"
	mana, attack, health = 3, 2, 4
	index = "YEAR_OF_THE_DRAGON~Hunter~Minion~3~2~4~Mech~Chopshop Copter"
	requireTarget, keyWord, description = False, "", "After a friendly Mech dies, add a random Mech to your hand"
	name_CN = "拆件旋翼机"
	poolIdentifier = "Mechs"
	@classmethod
	def generatePool(cls, pools):
		return "Mechs", list(pools.MinionswithRace["Mech"].values())
		
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_ChopshopCopter(self)]
		
class Trig_ChopshopCopter(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["MinionDied"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and target.ID == self.entity.ID and "Mech" in target.race
		
	def text(self, CHN):
		return "在一个友方机械死亡，随机将一张机械牌置入你的手牌" if CHN else "After a friendly Mech dies, add a random Mech to your hand"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.addCardtoHand(npchoice(self.rngPool("Mechs")), self.entity.ID)
			
			
class RotnestDrake(Minion):
	Class, race, name = "Hunter", "Dragon", "Rotnest Drake"
	mana, attack, health = 5, 6, 5
	index = "YEAR_OF_THE_DRAGON~Hunter~Minion~5~6~5~Dragon~Rotnest Drake~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: If you're holding a Dragon, destroy a random enemy minion"
	name_CN = "腐巢幼龙"
	def effCanTrig(self):
		self.effectViable = self.Game.Hand_Deck.holdingDragon(self.ID, self)
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		minions = self.Game.minionsAlive(3-self.ID)
		if minions: self.Game.killMinion(self, npchoice(minions))
		return None
		
		
"""Mage cards"""
class ArcaneAmplifier(Minion):
	Class, race, name = "Mage", "Elemental", "Arcane Amplifier"
	mana, attack, health = 3, 2, 5
	index = "YEAR_OF_THE_DRAGON~Mage~Minion~3~2~5~Elemental~Arcane Amplifier"
	requireTarget, keyWord, description = False, "", "Your Hero Power deals 2 extra damage"
	name_CN = "奥术增幅体"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.auras["Your Hero Power deals 2 extra damage"] = GameRuleAura_ArcaneAmplifier(self)
		
class GameRuleAura_ArcaneAmplifier(GameRuleAura):
	def auraAppears(self):
		self.entity.Game.status[self.entity.ID]["Power Damage"] += 2
		
	def auraDisappears(self):
		self.entity.Game.status[self.entity.ID]["Power Damage"] -= 2
		
		
class AnimatedAvalanche(Minion):
	Class, race, name = "Mage", "Elemental", "Animated Avalanche"
	mana, attack, health = 7, 7, 6
	index = "YEAR_OF_THE_DRAGON~Mage~Minion~7~7~6~Elemental~Animated Avalanche~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: If you played an Elemental last turn, summon a copy of this"
	name_CN = "活化雪崩"
	def effCanTrig(self):
		self.effectViable = self.Game.Counters.numElementalsPlayedLastTurn[self.ID] > 0
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if self.Game.Counters.numElementalsPlayedLastTurn[self.ID] > 0:
			Copy = self.selfCopy(self.ID, self) if self.onBoard else type(self)(self.Game, self.ID)
			self.summon(Copy, self.pos+1)
		return None
		
		
class WhatDoesThisDo(Power):
	mana, name, requireTarget = 0, "What Does This Do?", False
	index = "Mage~Hero Power~0~What Does This Do?"
	description = "Passive Hero Power. At the start of your turn, cast a random spell"
	name_CN = "这是什么？"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_WhatDoesThisDo(self)]
		
	def available(self, choice=0):
		return False
		
	def use(self, target=None, choice=0, comment=''):
		return 0
		
	def appears(self):
		for trig in self.trigsBoard: trig.connect()
		self.Game.sendSignal("HeroPowerAcquired", self.ID, self, None, 0, "")
		
	def disappears(self):
		for trig in self.trigsBoard: trig.disconnect()
		
class Trig_WhatDoesThisDo(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["TurnStarts"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		npchoice(self.rngPool("Spells"))(self.entity.Game, self.entity.ID).cast()
		
			
class TheAmazingReno(Hero):
	mana, description = 10, "Battlecry: Make all minions disappear. *Poof!*"
	Class, name, heroPower, armor = "Mage", "The Amazing Reno", WhatDoesThisDo, 5
	index = "YEAR_OF_THE_DRAGON~Mage~Hero Card~10~The Amazing Reno~Battlecry~Legendary"
	name_CN = "神奇的雷诺"
	poolIdentifier = "Spells"
	@classmethod
	def generatePool(cls, pools):
		spells = []
		for Class in pools.Classes:
			spells += [value for key, value in pools.ClassCards[Class].items() if "~Spell~" in key]
		return "Spells", spells
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		for minion in self.Game.minionsonBoard(1) + self.Game.minionsonBoard(2):
			self.Game.banishMinion(self, minion)
		return None
		
		
"""Paladin cards"""
class Shotbot(Minion):
	Class, race, name = "Paladin", "Mech", "Shotbot"
	mana, attack, health = 2, 2, 2
	index = "YEAR_OF_THE_DRAGON~Paladin~Minion~2~2~2~Mech~Shotbot~Reborn"
	requireTarget, keyWord, description = False, "Reborn", "Reborn"
	name_CN = "炮火机甲"
	
	
class AirRaid(Spell):
	Class, school, name = "Paladin", "", "Air Raid"
	requireTarget, mana = False, 2
	index = "YEAR_OF_THE_DRAGON~Paladin~Spell~2~Air Raid~Twinspell"
	description = "Twinspell. Summon two 1/1 Silver Hand Recruits with Taunt"
	name_CN = "空中团战"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.twinSpell = 1
		self.twinSpellCopy = AirRaid2
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		minions = [SilverHandRecruit(self.Game, self.ID) for i in range(2)]
		for minion in minions: minion.keyWords["Taunt"] += 1
		self.summon(minions, (-1, "totheRightEnd"), self)
		return None
		
class AirRaid2(Spell):
	Class, school, name = "Paladin", "", "Air Raid"
	requireTarget, mana = False, 2
	index = "YEAR_OF_THE_DRAGON~Paladin~Spell~2~Air Raid~Uncollectible"
	description = "Summon two 1/1 Silver Hand Recruits with Taunt"
	name_CN = "空中团战"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		minions = [SilverHandRecruit(self.Game, self.ID) for i in range(2)]
		for minion in minions: minion.keyWords["Taunt"] += 1
		self.summon(minions, (-1, "totheRightEnd"))
		return None
		
		
class Scalelord(Minion):
	Class, race, name = "Paladin", "Dragon", "Scalelord"
	mana, attack, health = 5, 5, 6
	index = "YEAR_OF_THE_DRAGON~Paladin~Minion~5~5~6~Dragon~Scalelord~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Give your Murlocs Divine Shield"
	name_CN = "鳞甲领主"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		for minion in self.Game.minionsonBoard(self.ID):
			if "Murloc" in minion.race:
				minion.getsStatus("Divine Shield")
		return None
		
		
"""Priest cards"""
class AeonReaver(Minion):
	Class, race, name = "Priest", "Dragon", "Aeon Reaver"
	mana, attack, health = 6, 4, 4
	index = "YEAR_OF_THE_DRAGON~Priest~Minion~6~4~4~Dragon~Aeon Reaver~Battlecry"
	requireTarget, keyWord, description = True, "", "Battlecry: Deal damage to a minion equal to its Attack"
	name_CN = "永恒掠夺者"
	def targetExists(self, choice=0):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target != self and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			self.dealsDamage(target, target.attack)
		return target
		
		
class ClericofScales(Minion):
	Class, race, name = "Priest", "", "Cleric of Scales"
	mana, attack, health = 1, 1, 1
	index = "YEAR_OF_THE_DRAGON~Priest~Minion~1~1~1~~Cleric of Scales~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: If you're holding a Dragon, Discover a spell from your deck"
	name_CN = "龙鳞祭司"
	
	def effCanTrig(self):
		self.effectViable = self.Game.Hand_Deck.holdingDragon(self.ID)
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if self.Game.Hand_Deck.holdingDragon(self.ID):
			self.discoverfromList(ClericofScales, comment, conditional=lambda card: card.type == "Spell",
								  ls=self.Game.Hand_Deck.hands[self.ID])
		return None
		
	def discoverDecided(self, option, case, info_RNGSync=None, info_GUISync=None):
		self.handleDiscoveredCardfromList(option, case, ls=self.Game.Hand_Deck.hands[self.ID],
										  func=lambda index, card: self.Game.Hand_Deck.drawCard(self.ID, index),
										  info_RNGSync=info_RNGSync, info_GUISync=info_GUISync)
		
		
class DarkProphecy(Spell):
	Class, school, name = "Priest", "Shadow", "Dark Prophecy"
	requireTarget, mana = False, 3
	index = "YEAR_OF_THE_DRAGON~Priest~Spell~3~Shadow~Dark Prophecy"
	description = "Discover a 2-Cost minion. Summon it and give it +3 Health"
	name_CN = "黑暗预兆"
	poolIdentifier = "2-Cost Minions as Priest"
	@classmethod
	def generatePool(cls, pools):
		classCards = {s : [] for s in pools.ClassesandNeutral}
		for key, value in pools.MinionsofCost[2].items():
			for Class in key.split('~')[1].split(','):
				classCards[Class].append(value)
		return ["2-Cost Minions as "+Class for Class in pools.Classes], \
			[classCards[Class]+classCards["Neutral"] for Class in pools.Classes]
			
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.discoverandGenerate(DarkProphecy, comment, poolFunc=lambda : self.rngPool("2-Cost Minions as "+classforDiscover(self)))
		return None
		
	def summonDiscoveredMinion(self, card):
		card.buffDebuff(0, 3)
		self.summon(card, -1)
	
	def discoverDecided(self, option, case, info_RNGSync=None, info_GUISync=None):
		self.handleDiscoverGeneratedCard(option, case, info_RNGSync, info_GUISync,
										 func=lambda cardType, card: DarkProphecy.summonDiscoveredMinion(self, card))
		
		
"""Rogue cards"""
class Skyvateer(Minion):
	Class, race, name = "Rogue", "Pirate", "Skyvateer"
	mana, attack, health = 2, 1, 3
	index = "YEAR_OF_THE_DRAGON~Rogue~Minion~2~1~3~Pirate~Skyvateer~Stealth~Deathrattle"
	requireTarget, keyWord, description = False, "Stealth", "Stealth. Deathrattle: Draw a card"
	name_CN = "空中私掠者"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.deathrattles = [DrawaCard(self)]
		
class DrawaCard(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.Game.Hand_Deck.drawCard(self.entity.ID)
		
	def text(self, CHN):
		return "亡语：抽一张牌" if CHN else "Deathrattle: Draw a card"
		
		
class Waxmancy(Spell):
	Class, school, name = "Rogue", "", "Waxmancy"
	requireTarget, mana = False, 2
	index = "YEAR_OF_THE_DRAGON~Rogue~Spell~2~Waxmancy"
	description = "Discover a Battlecry minion. Reduce its Cost by (2)"
	name_CN = "蜡烛学"
	poolIdentifier = "Battlecry Minions as Rogue"
	@classmethod
	def generatePool(cls, pools):
		classCards = {s : [value for key, value in pools.ClassCards[s].items() if "~Minion~" in key and "~Battlecry" in key] for s in pools.Classes}
		classCards["Neutral"] = [value for key, value in pools.NeutralCards.items() if "~Minion~" in key and "~Battlecry" in key]
		return ["Battlecry Minions as "+Class for Class in pools.Classes], \
			[classCards[Class]+classCards["Neutral"] for Class in pools.Classes]
			
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.discoverandGenerate(Waxmancy, comment, poolFunc=lambda: self.rngPool("Battlecry Minions as"+classforDiscover(self)))
		return None
		
	def addCard_Cost2Less(self, card):
		ManaMod(card, changeby=-2, changeto=-1).applies()
		self.addCardtoHand(card, self.ID, byDiscover=True)
	
	def discoverDecided(self, option, case, info_RNGSync=None, info_GUISync=None):
		self.handleDiscoverGeneratedCard(option, case, info_RNGSync, info_GUISync,
										 func=lambda cardType, card: Waxmancy.addCard_Cost2Less(self, card))
		
		
class ShadowSculptor(Minion):
	Class, race, name = "Rogue", "", "Shadow Sculptor"
	mana, attack, health = 5, 3, 2
	index = "YEAR_OF_THE_DRAGON~Rogue~Minion~5~3~2~~Shadow Sculptor~Combo"
	requireTarget, keyWord, description = False, "", "Combo: Draw a card for each card you've played this turn"
	name_CN = "暗影塑形师"
	def effCanTrig(self):
		self.effectViable = self.Game.Counters.numCardsPlayedThisTurn[self.ID] > 0
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if self.Game.Counters.numCardsPlayedThisTurn[self.ID] > 0:
			numCardsPlayed = self.Game.combCards(self.ID)
			for i in range(numCardsPlayed): self.Game.Hand_Deck.drawCard(self.ID)
		return None
		
"""Shaman cards"""
class ExplosiveEvolution(Spell):
	Class, school, name = "Shaman", "Nature", "Explosive Evolution"
	requireTarget, mana = True, 2
	index = "YEAR_OF_THE_DRAGON~Shaman~Spell~2~Nature~Explosive Evolution"
	description = "Transform a friendly minion into a random one that costs (3) more"
	name_CN = "惊爆异变"
	poolIdentifier = "1-Cost Minions to Summon"
	@classmethod
	def generatePool(cls, pools):
		return ["%d-Cost Minions to Summon"%cost for cost in pools.MinionsofCost.keys()], \
				[list(pools.MinionsofCost[cost].values()) for cost in pools.MinionsofCost.keys()]
				
	def available(self):
		return self.selectableFriendlyMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.ID == self.ID and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			cost = type(target).mana + 3
			while "%d-Cost Minions to Summon" % cost not in self.Game.RNGPools:
				cost -= 1
			newMinion = npchoice(self.rngPool("%d-Cost Minions to Summon" % cost))(self.Game, target.ID)
			self.transform(target, newMinion)
			target = newMinion
		return target
		
		
class EyeoftheStorm(Spell):
	Class, school, name = "Shaman", "Nature", "Eye of the Storm"
	requireTarget, mana = False, 10
	index = "YEAR_OF_THE_DRAGON~Shaman~Spell~10~Nature~Eye of the Storm~Overload"
	description = "Summon three 5/6 Elementals with Taunt. Overload: (3)"
	name_CN = "风暴之眼"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.overload = 3
		
	def available(self):
		return self.Game.space(self.ID) > 0
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.summon([Stormblocker(self.Game, self.ID) for i in range(3)], (-1, "totheRightEnd"))
		return None
		
class Stormblocker(Minion):
	Class, race, name = "Shaman", "Elemental", "Stormblocker"
	mana, attack, health = 5, 5, 6
	index = "YEAR_OF_THE_DRAGON~Shaman~Minion~5~5~6~Elemental~Stormblocker~Taunt~Uncollectible"
	requireTarget, keyWord, description = False, "Taunt", "Taunt"
	name_CN = "拦路风暴"
	
	
#莱登之拳对于费用不在随机池中的法术不会响应，但是埃提耶什会消耗一个耐久度，但是不会召唤随从
class TheFistofRaden(Weapon):
	Class, name, description = "Shaman", "The Fist of Ra-den", "After you cast a spell, summon a Legendary minion of that Cost. Lose 1 Durability"
	mana, attack, durability = 4, 1, 4
	index = "YEAR_OF_THE_DRAGON~Shaman~Weapon~4~1~4~The Fist of Ra-den~Legendary"
	name_CN = "莱登之拳"
	poolIdentifier = "1-Cost Legendary Minions to Summon"
	@classmethod
	def generatePool(cls, pools):
		minions = {}
		for key, value in pools.LegendaryMinions.items():
			s = key.split('~')[3] + "-Cost Legendary Minions to Summon"
			try: minions[s].append(value)
			except: minions[s] = [value]
		return list(minions.keys()), list(minions.values())
		
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_TheFistofRaden(self)]
		
class Trig_TheFistofRaden(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["SpellBeenPlayed"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject.ID == self.entity.ID and self.entity.onBoard and self.entity.durability > 0
		
	def text(self, CHN):
		return "在你施放一个法术后，召唤一个法力值消耗相同的传说随从，失去1点耐久度" if CHN \
				else "After you cast a spell, summon a Legendary minion of that Cost. Lose 1 Durability"
				
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		key = "%d-Cost Legendary Minions to Summon" % number
		minions = npchoice(self.rngPool(key)) if key in self.rngPool(key) and self.entity.Game.space(self.entity.ID) > 0 else None
		if minions:
			self.entity.summon(npchoice(minions)(self.entity.Game, self.entity.ID), -1)
			self.entity.loseDurability()
		
"""Warlock cards"""
class FiendishServant(Minion):
	Class, race, name = "Warlock", "Demon", "Fiendish Servant"
	mana, attack, health = 1, 2, 1
	index = "YEAR_OF_THE_DRAGON~Warlock~Minion~1~2~1~Demon~Fiendish Servant~Deathrattle"
	requireTarget, keyWord, description = False, "", "Deathrattle: Give this minion's Attack to a random friendly minion"
	name_CN = "邪魔仆人"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.deathrattles = [GiveAttacktoaRandomFriendlyMinion(self)]
		
class GiveAttacktoaRandomFriendlyMinion(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		minions = self.entity.Game.minionsonBoard(self.entity.ID)
		if minions: npchoice(minions).buffDebuff(number, 0)
		
	def text(self, CHN):
		return "亡语：随机使一个友方随从获得该随从的攻击力" if CHN \
				else "Deathrattle: Give this minion's Attack to a random friendly minion"
				
				
class TwistedKnowledge(Spell):
	Class, school, name = "Warlock", "Shadow", "Twisted Knowledge"
	requireTarget, mana = False, 2
	index = "YEAR_OF_THE_DRAGON~Warlock~Spell~2~Shadow~Twisted Knowledge"
	description = "Discover 2 Warlock cards"
	name_CN = "扭曲学识"
	poolIdentifier = "Warlock Cards"
	@classmethod
	def generatePool(cls, pools):
		return "Warlock Cards", list(pools.ClassCards["Warlock"].values())
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.discoverandGenerate(TwistedKnowledge, comment, poolFunc=lambda : self.rngPool("Warlock Cards"))
		self.discoverandGenerate(TwistedKnowledge, comment, poolFunc=lambda : self.rngPool("Warlock Cards"))
		return None
		
#只会考虑当前的费用，寻找下回合法力值以下的牌。延时生效的法力值效果不会被考虑。
#如果被战吼触发前被对方控制了，则也会根据我方下个回合的水晶进行腐化。但是这个回合结束时就会丢弃（因为也算是一个回合。）
#https://www.bilibili.com/video/av92443139?from=search&seid=7929483619040209451
class ChaosGazer(Minion):
	Class, race, name = "Warlock", "Demon", "Chaos Gazer"
	mana, attack, health = 3, 4, 3
	index = "YEAR_OF_THE_DRAGON~Warlock~Minion~3~4~3~Demon~Chaos Gazer~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Corrupt a playable card in your opponent's hand. They have 1 turn to play it!"
	name_CN = "混乱凝视者"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		manaNextTurn = max(0, min(10, self.Game.Manas.manasUpper[3 - self.ID] + 1) - self.Game.Manas.manasOverloaded[3 - self.ID])
		cards = [card for card in self.Game.Hand_Deck.hands[3 - self.ID] \
				 if card.mana <= manaNextTurn and not any(isinstance(trig, Trig_CorruptedHand) for trig in card.trigsHand)]
		if cards:
			card = npchoice(cards)
			card.getsTrig(Trig_CorruptedHand(card), trigType="TrigHand", connect=True)
		return None
		
class Trig_CorruptedHand(TrigHand):
	def __init__(self, entity):
		super().__init__(entity, ["TurnEnds"])
		self.inherent = False
		self.changesCard = True
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		#被腐蚀的卡只会在其拥有者的回合结束时才会被丢弃
		return self.entity.inHand and self.entity.ID == ID
		
	def text(self, CHN):
		return "你的回合结束时，弃掉这张手牌" if CHN else "At the end of this turn, discard this card"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.Game.Hand_Deck.discard(self.entity.ID, self.entity)
		
		
"""Warrior cards"""
class BoomSquad(Spell):
	Class, school, name = "Warrior", "", "Boom Squad"
	requireTarget, mana = False, 1
	index = "YEAR_OF_THE_DRAGON~Warrior~Spell~1~Boom Squad"
	description = "Discover a Lackey, Mech, or a Dragon"
	name_CN = "砰砰战队"
	poolIdentifier = "Mechs as Warrior"
	@classmethod
	def generatePool(cls, pools):
		classes_Mech = ["Mechs as %s"+Class for Class in pools.Classes]
		classCards = {s : [] for s in pools.ClassesandNeutral}
		for key, value in pools.MinionswithRace["Mech"].items():
			for Class in key.split('~')[1].split(','):
				classCards[Class].append(value)
		mechs = [classCards[Class]+classCards["Neutral"] for Class in pools.Classes]
		classes_Dragon = ["Dragons as %s"+Class for Class in pools.Classes]
		classCards = {s : [] for s in pools.ClassesandNeutral}
		for key, value in pools.MinionswithRace["Dragon"].items():
			for Class in key.split('~')[1].split(','):
				classCards[Class].append(value)
		dragons = [classCards[Class]+classCards["Neutral"] for Class in pools.Classes]
		return classes_Mech+classes_Dragon, mechs+dragons
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.discoverandGenerate_MultiplePools(BoomSquad, comment,
											   poolFuncs=[lambda : Lackeys,
														  lambda : self.rngPool("Mechs as "+classforDiscover(self)),
														  lambda : self.rngPool("Dragons as "+classforDiscover(self))])
		return None
		
		
class RiskySkipper(Minion):
	Class, race, name = "Warrior", "Pirate", "Risky Skipper"
	mana, attack, health = 1, 1, 3
	index = "YEAR_OF_THE_DRAGON~Warrior~Minion~1~1~3~Pirate~Risky Skipper"
	requireTarget, keyWord, description = False, "", "After you play a minion, deal 1 damage to all minions"
	name_CN = "冒进的艇长"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_RiskySkipper(self)]
		
class Trig_RiskySkipper(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["MinionBeenPlayed"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject.ID == self.entity.ID
		
	def text(self, CHN):
		return "在你使用一张随从牌后，对所有随从造成1点伤害" if CHN \
				else "After you play a minion, deal 1 damage to all minions"
				
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		targets = self.entity.Game.minionsonBoard(1) + self.entity.Game.minionsonBoard(2)
		self.entity.dealsAOE(targets, [1 for minion in targets])
		
	
class BombWrangler(Minion):
	Class, race, name = "Warrior", "", "Bomb Wrangler"
	mana, attack, health = 3, 2, 3
	index = "YEAR_OF_THE_DRAGON~Warrior~Minion~3~2~3~~Bomb Wrangler"
	requireTarget, keyWord, description = False, "", "Whenever this minion takes damage, summon a 1/1 Boom Bot"
	name_CN = "炸弹牛仔"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_BombWrangler(self)]
		
class Trig_BombWrangler(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["MinionTakesDmg"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and target == self.entity
		
	def text(self, CHN):
		return "每当该随从受到伤害，召唤一个1/1的砰砰机器人" if CHN \
				else "Whenever this minion takes damage, summon a 1/1 Boom Bot"
				
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.summon(BoomBot(self.entity.Game, self.entity.ID), self.entity.pos+1)
		
				
Galakrond_Indices = {"YEAR_OF_THE_DRAGON~Neutral~Minion~3~2~2~~Skydiving Instructor~Battlecry": SkydivingInstructor,
					"YEAR_OF_THE_DRAGON~Neutral~Minion~5~3~4~Elemental~Hailbringer~Battlecry": Hailbringer,
					"YEAR_OF_THE_DRAGON~Neutral~Minion~1~1~1~Elemental~Ice Shard~Uncollectible": IceShard,
					"YEAR_OF_THE_DRAGON~Neutral~Minion~2~3~2~~Licensed Adventurer~Battlecry": LicensedAdventurer,
					"YEAR_OF_THE_DRAGON~Neutral~Minion~4~3~2~Demon~Frenzied Felwing": FrenziedFelwing,
					"YEAR_OF_THE_DRAGON~Neutral~Minion~4~3~5~Beast~Escaped Manasaber~Stealth": EscapedManasaber,
					"YEAR_OF_THE_DRAGON~Neutral~Minion~5~5~5~~Boompistol Bully~Battlecry": BoompistolBully,
					"YEAR_OF_THE_DRAGON~Neutral~Minion~4~2~3~~Grand Lackey Erkh~Legendary": GrandLackeyErkh,
					"YEAR_OF_THE_DRAGON~Neutral~Minion~4~2~3~Pirate~Sky Gen'ral Kragg~Taunt~Battlecry~Legendary": SkyGenralKragg,
					"YEAR_OF_THE_DRAGON~Neutral~Minion~4~4~2~Beast~Sharkbait~Rush~Legendary~Uncollectible": Sharkbait,
					"YEAR_OF_THE_DRAGON~Druid~Spell~2~Rising Winds~Twinspell~Choose One": RisingWinds,
					"YEAR_OF_THE_DRAGON~Druid~Spell~2~Rising Winds~Choose One~Uncollectible": RisingWinds2,
					"YEAR_OF_THE_DRAGON~Druid~Spell~2~Take Flight~Uncollectible": TakeFlight,
					"YEAR_OF_THE_DRAGON~Druid~Spell~2~Swoop In~Uncollectible": SwoopIn,
					"YEAR_OF_THE_DRAGON~Druid~Minion~2~3~2~Beast~Eagle~Uncollectible": Eagle,
					"YEAR_OF_THE_DRAGON~Druid~Minion~2~2~3~Beast~Steel Beetle~Battlecry": SteelBeetle,
					"YEAR_OF_THE_DRAGON~Druid~Minion~7~6~8~Beast~Winged Guardian~Taunt~Reborn": WingedGuardian,
					"YEAR_OF_THE_DRAGON~Hunter~Spell~2~Fresh Scent~Twinspell": FreshScent,
					"YEAR_OF_THE_DRAGON~Hunter~Spell~2~Fresh Scent~Uncollectible": FreshScent2,
					"YEAR_OF_THE_DRAGON~Hunter~Minion~3~2~4~Mech~Chopshop Copter": ChopshopCopter,
					"YEAR_OF_THE_DRAGON~Hunter~Minion~5~6~5~Dragon~Rotnest Drake~Battlecry": RotnestDrake,
					"YEAR_OF_THE_DRAGON~Mage~Minion~3~2~5~Elemental~Arcane Amplifier": ArcaneAmplifier,
					"YEAR_OF_THE_DRAGON~Mage~Minion~7~7~6~Elemental~Animated Avalanche~Battlecry": AnimatedAvalanche,
					"YEAR_OF_THE_DRAGON~Mage~Hero Card~10~The Amazing Reno~Battlecry~Legendary": TheAmazingReno,
					"YEAR_OF_THE_DRAGON~Paladin~Minion~2~2~2~Mech~Shotbot~Reborn": Shotbot,
					"YEAR_OF_THE_DRAGON~Paladin~Spell~2~Air Raid~Twinspell": AirRaid,
					"YEAR_OF_THE_DRAGON~Paladin~Spell~2~Air Raid~Uncollectible": AirRaid2,
					"YEAR_OF_THE_DRAGON~Paladin~Minion~5~5~6~Dragon~Scalelord~Battlecry": Scalelord,
					"YEAR_OF_THE_DRAGON~Priest~Minion~6~4~4~Dragon~Aeon Reaver~Battlecry": AeonReaver,
					"YEAR_OF_THE_DRAGON~Priest~Minion~1~1~1~~Cleric of Scales~Battlecry": ClericofScales,
					"YEAR_OF_THE_DRAGON~Priest~Spell~3~Dark Prophecy": DarkProphecy,
					"YEAR_OF_THE_DRAGON~Rogue~Minion~2~1~3~Pirate~Skyvateer~Stealth~Deathrattle": Skyvateer,
					"YEAR_OF_THE_DRAGON~Rogue~Spell~2~Waxmancy": Waxmancy,
					"YEAR_OF_THE_DRAGON~Rogue~Minion~5~3~2~~Shadow Sculptor~Combo": ShadowSculptor,
					"YEAR_OF_THE_DRAGON~Shaman~Spell~2~Explosive Evolution": ExplosiveEvolution,
					"YEAR_OF_THE_DRAGON~Shaman~Spell~10~Eye of the Storm~Overload": EyeoftheStorm,
					"YEAR_OF_THE_DRAGON~Shaman~Minion~5~5~6~Elemental~Stormblocker~Taunt~Uncollectible": Stormblocker,
					"YEAR_OF_THE_DRAGON~Shaman~Weapon~4~1~4~The Fist of Ra-den~Legendary": TheFistofRaden,
					"YEAR_OF_THE_DRAGON~Warlock~Minion~1~2~1~Demon~Fiendish Servant~Deathrattle": FiendishServant,
					"YEAR_OF_THE_DRAGON~Warlock~Spell~2~Twisted Knowledge": TwistedKnowledge,
					"YEAR_OF_THE_DRAGON~Warlock~Minion~3~4~3~Demon~Chaos Gazer~Battlecry": ChaosGazer,
					"YEAR_OF_THE_DRAGON~Warrior~Spell~1~Boom Squad": BoomSquad,
					"YEAR_OF_THE_DRAGON~Warrior~Minion~1~1~3~Pirate~Risky Skipper": RiskySkipper,
					"YEAR_OF_THE_DRAGON~Warrior~Minion~3~2~3~~Bomb Wrangler": BombWrangler,
					}