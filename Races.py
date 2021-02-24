from CardTypes import *
from Triggers_Auras import *
from numpy.random import choice as npchoice
from numpy.random import randint as nprandint
from numpy.random import shuffle as npshuffle
from numpy import inf as npinf
from collections import Counter as cnt

from Classic import Bananas, Treant_Classic
from Outlands import Minion_Dormantfor2turns, MsshifnPrime, ZixorPrime, SolarianPrime, MurgurglePrime, ReliquaryPrime, \
					AkamaPrime, VashjPrime, KanrethadPrime, KargathPrime
from Academy import SoulFragment, Spellburst


"""Darkmoon Races"""

"""Neutral cards"""
class ArmorVendor(Minion):
	Class, race, name = "Neutral", "", "Armor Vendor"
	mana, attack, health = 1, 1, 3
	index = "Races~Neutral~Minion~1~1~3~~Armor Vendor~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Give 4 Armor to each hero"
	name_CN = "护甲商贩"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.Game.heroes[1].gainsArmor(4)
		self.Game.heroes[2].gainsArmor(4)
		return None
		
		
class Crabrider(Minion):
	Class, race, name = "Neutral", "Murloc", "Crabrider"
	mana, attack, health = 2, 1, 4
	index = "Races~Neutral~Minion~2~1~4~~Crabrider~Rush~Windfury"
	requireTarget, keyWord, description = False, "Rush,Windfury", "Rush, Windfury"
	name_CN = "螃蟹骑士"
	
	
class Deathwarden(Minion):
	Class, race, name = "Neutral", "", "Deathwarden"
	mana, attack, health = 3, 2, 5
	index = "Races~Neutral~Minion~3~2~5~~Deathwarden"
	requireTarget, keyWord, description = False, "", "Deathrattles can't trigger"
	name_CN = "死亡守望者"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.auras["Deathrattles can't trigger"] = GameRuleAura_Deathwarden(self)
		
class GameRuleAura_Deathwarden(GameRuleAura):
	def auraAppears(self):
		minion = self.entity
		minion.Game.status[minion.ID]["Deathrattles X"] += 1
		minion.Game.status[3-minion.ID]["Deathrattles X"] += 1
		
	def auraDisappears(self):
		minion = self.entity
		minion.Game.status[minion.ID]["Deathrattles X"] -= 1
		minion.Game.status[3-minion.ID]["Deathrattles X"] -= 1
		
		
class Moonfang(Minion):
	Class, race, name = "Neutral", "Beast", "Moonfang"
	mana, attack, health = 5, 6, 3
	index = "Races~Neutral~Minion~5~6~3~Beast~Moonfang~Legendary"
	requireTarget, keyWord, description = False, "", "Can only take 1 damage at a time"
	name_CN = "明月之牙"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_MoonFang(self)]
		
class Trig_MoonFang(TrigBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["FinalDmgonMinion?"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		#Can only prevent damage if there is still durability left
		return target == self.entity and self.entity.onBoard
		
	def text(self, CHN):
		return "每次只能受到1点伤害" if CHN else "Can only take 1 damage at a time"
				
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		number[0] = min(number[0], 1)
		
		
class RunawayBlackwing(Minion):
	Class, race, name = "Neutral", "Dragon", "Runaway Blackwing"
	mana, attack, health = 9, 9, 9
	index = "Races~Neutral~Minion~9~9~9~Dragon~Runaway Blackwing"
	requireTarget, keyWord, description = False, "", "At the end of your turn, deal 9 damage to a random enemy minion"
	name_CN = "窜逃的黑翼龙"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_RunawayBlackwing(self)]
		
class Trig_RunawayBlackwing(TrigBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["TurnEnds"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and ID == self.entity.ID
		
	def text(self, CHN):
		return "在你的回合结束时，随机对一个敌方随从造成9点伤害" if CHN else "At the end of your turn, deal 9 damage to a random enemy minion"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		curGame = self.entity.Game
		if curGame.mode == 0:
			enemy = None
			if curGame.guides:
				i, where = curGame.guides.pop(0)
				if where: enemy = curGame.find(i, where)
			else:
				targets = curGame.minionsAlive(3-self.entity.ID)
				if targets:
					enemy = npchoice(targets)
					curGame.fixedGuides.append((enemy.pos, enemy.type+str(enemy.ID)))
				else:
					curGame.fixedGuides.append((0, ''))
			if enemy: self.entity.dealsDamage(enemy, 9)
			
		
"""Demon Hunter Cards"""
class IllidariStudies(Spell):
	Class, school, name = "Demon Hunter", "", "Illidari Studies"
	requireTarget, mana = False, 1
	index = "Races~Demon Hunter~Spell~1~Illidari Studies"
	description = "Discover an Outcast card. Your next one costs (1) less"
	name_CN = "伊利达雷研习"
	poolIdentifier = "Outcast Cards"
	@classmethod
	def generatePool(cls, Game):
		return "Outcast Cards", [value for key, value in Game.ClassCards["Demon Hunter"].items() if "~Outcast" in key]
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if curGame.mode == 0:
			pool = tuple(self.rngPool("Outcast Cards"))
			if curGame.guides:
				card, possi = curGame.guides.pop(0)
				curGame.Hand_Deck.addCardtoHand(card, self.ID, byType=True, byDiscover=True, creator=type(self), possi=possi)
			else:
				if self.ID != curGame.turn or "byOthers" in comment:
					card = npchoice(pool)
					curGame.fixedGuides.append(card)
					curGame.Hand_Deck.addCardtoHand(card, self.ID, byType=True, byDiscover=True, creator=type(self), possi=pool)
				else:
					cards = npchoice(pool, 3, replace=False)
					curGame.options = [card(curGame, self.ID) for card in cards]
					curGame.Discover.startDiscover(self, pool)
		tempAura = GameManaAura_NextOutcast1Less(self.Game, self.ID)
		self.Game.Manas.CardAuras.append(tempAura)
		tempAura.auraAppears()
		return None
		
	def discoverDecided(self, option, pool):
		self.Game.fixedGuides.append(type(option))
		self.Game.Hand_Deck.addCardtoHand(option, self.ID, byDiscover=True, creator=type(self), possi=pool)
		
class GameManaAura_NextOutcast1Less(TempManaEffect):
	def __init__(self, Game, ID, changeby=0, changeto=-1):
		self.blank_init(Game, ID, -1, -1)
		self.temporary = False
		
	def applicable(self, target):
		return target.ID == self.ID and "~Outcast" in target.index
		
	def text(self, CHN):
		return "你的下一张流放牌的法力值消耗减少(1)点" if CHN else "Your next Outcast card costs (1) less"
		
		
class FelfireDeadeye(Minion):
	Class, race, name = "Demon Hunter,Hunter", "", "Felfire Deadeye"
	mana, attack, health = 2, 2, 3
	index = "Races~Demon Hunter,Hunter~Minion~2~2~3~~Felfire Deadeye"
	requireTarget, keyWord, description = False, "", "Your Hero Power costs (1) less"
	name_CN = "邪火神射手"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.auras["Your Hero Power costs (1) less"] = ManaAura_Power(self, -1, -1)
		
	def manaAuraApplicable(self, subject): #ID用于判定是否是我方手中的随从
		return subject.ID == self.ID
		
		
class Felsaber(Minion):
	Class, race, name = "Demon Hunter", "Demon", "Felsaber"
	mana, attack, health = 4, 5, 6
	index = "Races~Demon Hunter~Minion~4~5~6~Demon~Felsaber"
	requireTarget, keyWord, description = False, "", "Can only attack if your hero attacked this turn"
	name_CN = "邪刃豹"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.marks["Can't Attack"] = 1
		
	def canAttack(self):
		return self.actionable() and self.attack > 0 and self.status["Frozen"] < 1 \
				and self.attChances_base + self.attChances_extra <= self.attTimes \
				and (self.silenced or self.Game.Counters.heroAttackTimesThisTurn[self.ID] > 0)
				
				
"""Druid Cards"""
class Guidance(Spell):
	Class, school, name = "Druid,Shaman", "", "Guidance"
	requireTarget, mana = False, 1
	index = "Races~Druid,Shaman~Spell~1~Guidance"
	description = "Look at two spells. Add one to your hand or Overload: (1) to get both"
	name_CN = "灵魂指引"
	poolIdentifier = "Druid Spells"
	@classmethod
	def generatePool(cls, Game):
		return [Class+" Spells" for Class in Game.Classes], \
				[[value for key, value in Game.ClassCards[Class].items() if "~Spell~" in key] for Class in Game.Classes]
				
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if curGame.mode == 0:
			pool = tuple(self.rngPool(classforDiscover(self)+" Spells"))
			if curGame.guides:
				card1, card2, choice = curGame.guides.pop(0)
				if choice > 1:
					curGame.Hand_Deck.addCardtoHand([card1, card2], self.ID, byType=True, byDiscover=True, creator=type(self), possi=pool)
				else:
					curGame.Hand_Deck.addCardtoHand(card2 if choice else card1, self.ID, byType=True, byDiscover=True, creator=type(self), possi=pool)
					curGame.Manas.overloadMana(1, self.ID)
			else:
				if self.ID != curGame.turn or "byOthers" in comment:
					card = npchoice(pool)
					curGame.fixedGuides.append(card)
					curGame.Hand_Deck.addCardtoHand(card, self.ID, byType=True, byDiscover=True, creator=type(self), possi=pool)
				else:
					cards = npchoice(pool, 3, replace=False)
					curGame.options = [card(curGame, self.ID) for card in cards]
					curGame.Discover.startDiscover(self, pool)
		return None
		
	def discoverDecided(self, option, pool):
		card1, card2 = [type(card) for card in self.Game.options[0:2]]
		i = self.Game.options.index(option)
		self.Game.fixedGuides.append((card1, card2, i))
		if i == 2:
			self.Game.Hand_Deck.addCardtoHand(self.Game.options[0:2], self.ID, byDiscover=True, creator=type(self), possi=pool)
			self.Game.Manas.overloadMana(1, self.ID)
		else:
			self.Game.Hand_Deck.addCardtoHand(option, self.ID, byDiscover=True, creator=type(self), possi=pool)
			
class IWantBoth:
	def __init__(self):
		self.name = "I want both"
		self.description = "Have both cards and Overload (1)"
		
		
class DreamingDrake(Minion):
	Class, race, name = "Druid", "Dragon", "Dreaming Drake"
	mana, attack, health = 3, 3, 4
	index = "Races~Druid~Minion~3~3~4~Dragon~Dreaming Drake~Taunt~ToCorrupt"
	requireTarget, keyWord, description = False, "Taunt", "Taunt. Corrupt: Gain +2/+2"
	name_CN = "迷梦幼龙"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsHand = [Trig_Corrupt(self, DreamingDrake_Corrupt)] #只有在手牌中才会升级
		
class DreamingDrake_Corrupt(Minion):
	Class, race, name = "Druid", "Dragon", "Dreaming Drake"
	mana, attack, health = 3, 5, 6
	index = "Races~Druid~Minion~3~5~6~Dragon~Dreaming Drake~Taunt~Corrupted"
	requireTarget, keyWord, description = False, "Taunt", "Corrupted. Taunt"
	name_CN = "迷梦幼龙"
	
	
class ArborUp(Spell):
	Class, school, name = "Druid", "", "Arbor Up"
	requireTarget, mana = False, 5
	index = "Races~Druid~Spell~5~Arbor Up"
	description = "Summon two 2/2 Treants. Give your minions +2/+1"
	name_CN = "树木生长"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.Game.summon([Treant_Classic(self.Game, self.ID) for i in range(2)], (-1, "totheRightEnd"), self)
		for minion in self.Game.minionsonBoard(self.ID):
			minion.buffDebuff(2, 1)
		return None
		
		
"""Hunter Cards"""
class ResizingPouch(Spell):
	Class, school, name = "Hunter,Druid", "", "Resizing Pouch"
	requireTarget, mana = False, 1
	index = "Races~Hunter,Druid~Spell~1~Resizing Pouch"
	description = "Discover a card with Cost equal to your remaining Mana Crystals"
	name_CN = "随心口袋"
	poolIdentifier = "Cards as Hunter"
	@classmethod
	def generatePool(cls, Game):
		return ["Cards as "+Class for Class in Game.Classes], [list(Game.ClassCards[Class].values())+list(Game.NeutralCards.values()) for Class in Game.Classes]
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if curGame.mode == 0:
			cost = curGame.Manas.manas[self.ID]
			pool = (card for card in self.rngPool("Cards as %s"%classforDiscover(self)) if card.mana == cost)
			if curGame.guides:
				card = curGame.guides.pop(0)
				curGame.Hand_Deck.addCardtoHand(card, self.ID, byType=True, byDiscover=True, creator=type(self), possi=pool)
			else:
				if self.ID != curGame.turn or "byOthers" in comment:
					card = npchoice(pool)
					curGame.fixedGuides.append(card)
					curGame.Hand_Deck.addCardtoHand(card, self.ID, byType=True, byDiscover=True, creator=type(self), possi=pool)
				else:
					cards = npchoice(pool, 3, replace=False)
					curGame.options = [card(curGame, self.ID) for card in cards]
					curGame.Discover.startDiscover(self, pool)
		return None
		
	def discoverDecided(self, option, pool):
		self.Game.fixedGuides.append(type(option))
		self.Game.Hand_Deck.addCardtoHand(option, self.ID, byDiscover=True, creator=type(self), possi=pool)
		
		
class BolaShot(Spell):
	Class, school, name = "Hunter", "", "Bola Shot"
	requireTarget, mana = True, 2
	index = "Races~Hunter~Spell~2~Bola Shot"
	description = "Deal 1 damage to a minion and 2 damage to its neighbors"
	name_CN = "套索射击"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
		
	def text(self, CHN):
		damage1 = (1 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		damage2 = (2 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		return "对一个随从造成%d点伤害，并对其相邻的随从造成%d点伤害"%(damage1, damage2) \
				if CHN else "Deal %d damage to a minion and %d damage to its neighbors"%(damage1, damage2)
				
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			damage_target = (1 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			damage_adjacent = (2 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			neighbors = self.Game.neighbors2(target)[0]
			if target.onBoard and neighbors:
				targets = [target] + neighbors
				damages = [damage_target] + [damage_adjacent for minion in targets]
				self.dealsAOE(targets, damages)
			else:
				self.dealsDamage(target, damage_target)
		return target
		
		
class Saddlemaster(Minion):
	Class, race, name = "Hunter", "", "Saddlemaster"
	mana, attack, health = 3, 3, 4
	index = "Races~Hunter~Minion~3~3~4~~Saddlemaster"
	requireTarget, keyWord, description = False, "", "After you play a Beast, add a random Beast to your hand"
	name_CN = "鞍座大师"
	poolIdentifier = "Beasts"
	@classmethod
	def generatePool(cls, Game):
		return "Beasts", list(Game.MinionswithRace["Beast"].values())
		
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_Saddlemaster(self)]
		
class Trig_Saddlemaster(TrigBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionBeenPlayed"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject.ID == self.entity.ID and "Beast" in subject.race
		
	def text(self, CHN):
		return "在你使用一张野兽牌后，随机将一张野兽牌置入你的手牌" if CHN else "After you play a Beast, add a random Beast to your hand"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		curGame = self.entity.Game
		if curGame.mode == 0:
			pool = tuple(self.rngPool("Beasts"))
			if curGame.guides:
				card = curGame.guides.pop(0)
			else:
				card = npchoice(pool)
				curGame.fixedGuides.append(card)
			curGame.Hand_Deck.addCardtoHand(card, self.entity.ID, byType=True, creator=type(self.entity), possi=pool)
			
"""Mage Cards"""
class GlacierRacer(Minion):
	Class, race, name = "Mage", "", "Glacier Racer"
	mana, attack, health = 1, 1, 3
	index = "Races~Mage~Minion~1~1~3~~Glacier Racer"
	requireTarget, keyWord, description = False, "", "Spellburst: Deal 3 damage to all Frozen enemies"
	name_CN = "冰川竞速者"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_GlacierRacer(self)]
		
class Trig_GlacierRacer(Spellburst):
	def text(self, CHN):
		return "法术迸发：对所有已被冻结的矮人造成3点伤害" if CHN else "Spellburst: Deal 3 damage to all Frozen enemies"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		game, ID = self.entity.Game, self.entity.ID
		targets = [obj for obj in game.minionsonBoard(ID) if obj.status["Frozen"]]
		if game.heroes[3-ID].status["Frozen"] > 0: targets.append(game.heroes[3-ID])
		if targets: self.entity.dealsAOE(targets, [3] * len(targets))
		
		
class ConjureManaBiscuit(Spell):
	Class, school, name = "Mage", "", "Conjure Mana Biscuit"
	requireTarget, mana = False, 2
	index = "Races~Mage~Spell~2~Conjure Mana Biscuit"
	description = "Add a Biscuit to your hand that refreshes 2 Mana Crystals"
	name_CN = "制造法力饼干"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.Game.Hand_Deck.addCardtoHand(ManaBiscuit, self.ID, byType=True, creator=type(self))
		return None
		
class ManaBiscuit(Spell):
	Class, school, name = "Mage", "", "Mana Biscuit"
	requireTarget, mana = False, 0
	index = "Races~Mage~Spell~0~Mana Biscuit~Uncollectible"
	description = "Refresh 2 Mana Crystals"
	name_CN = "法力饼干"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.Game.Manas.restoreManaCrystal(2, self.ID, restoreAll=False)
		return None
		
		
class KeywardenIvory(Minion):
	Class, race, name = "Mage,Rogue", "", "Keywarden Ivory"
	mana, attack, health = 5, 4, 5
	index = "Races~Mage,Rogue~Minion~5~4~5~~Keywarden Ivory~Battlecry~Legendary"
	requireTarget, keyWord, description = False, "", "Battlecry: Discover a dual-class spell from any class. Spellburst: Get another copy"
	name_CN = "钥匙守护者 艾芙瑞"
	poolIdentifier = "Dual Class Spells"
	@classmethod
	def generatePool(cls, Game):
		spells = []
		for Class in Game.Classes:
			spells += [value for key, value in Game.ClassCards[Class].items() if "," in key.split('~')[1] and key.split('~')[2] == "Spell"]
		return "Dual Class Spells", spells
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if self.ID == curGame.turn:
			if curGame.mode == 0:
				pool = tuple(self.rngPool("Dual Class Spells"))
				if curGame.guides:
					spell = curGame.guides.pop(0)
					curGame.Hand_Deck.addCardtoHand(spell, self.ID, byType=True, byDiscover=True, creator=type(self), possi=pool)
					if self.onBoard or self.inHand:
						trig = Trig_KeywardenIvory(self, spell, pool)
						self.trigsBoard.append(trig)
						if self.onBoard: trig.connect()
				else:
					if "byOthers" in comment:
						spell = npchoice(pool)
						curGame.fixedGuides.append(spell)
						curGame.Hand_Deck.addCardtoHand(spell, self.ID, byType=True, byDiscover=True, creator=type(self), possi=pool)
						if self.onBoard or self.inHand:
							trig = Trig_KeywardenIvory(self, spell, pool)
							self.trigsBoard.append(trig)
							if self.onBoard: trig.connect()
					else:
						spells = npchoice(pool, 3, replace=False)
						curGame.options = [spell(curGame, self.ID) for spell in spells]
						curGame.Discover.startDiscover(self, pool)
		return None
		
	def discoverDecided(self, option, pool):
		self.Game.fixedGuides.append(type(option))
		self.Game.Hand_Deck.addCardtoHand(option, self.ID, byDiscover=True, creator=type(self), possi=pool)
		if self.onBoard or self.inHand:
			trig = Trig_KeywardenIvory(self, type(option), pool)
			self.trigsBoard.append(trig)
			if self.onBoard: trig.connect()
			
class Trig_KeywardenIvory(Spellburst):
	def __init__(self, entity, spell, pool):
		self.blank_init(entity, ["SpellBeenPlayed"])
		self.spell, self.pool = spell, pool
		
	def text(self, CHN):
		return "法术迸发：获得一个发现的双职业法术的复制" if CHN else "Spellburst: Get a copy of the Discovered dual-class spell"
	
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.Game.Hand_Deck.addCardtoHand(self.spell, self.entity.ID, byType=True, creator=type(self.entity), possi=self.pool)


"""Paladin Cards"""
class ImprisonedCelestial(Minion_Dormantfor2turns):
	Class, race, name = "Paladin", "", "Imprisoned Celestial"
	mana, attack, health = 3, 4, 5
	index = "Races~Paladin~Minion~3~4~5~~Imprisoned Celestial"
	requireTarget, keyWord, description = False, "", "Dormant for 2 turns. Spellburst: Give your minions Divine Shield"
	name_CN = "被禁锢的星骓"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_ImprisonedCelestial(self)]
		
class Trig_ImprisonedCelestial(Spellburst):
	def text(self, CHN):
		return "法术迸发：使你的随从获得圣盾" if CHN else "Spellburst: Give your minions Divine Shield"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		for minion in self.entity.Game.minionsonBoard(self.entity.ID):
			minion.getsKeyword("Divine Shield")
			
			
class Rally(Spell):
	Class, school, name = "Paladin,Priest", "", "Rally!"
	requireTarget, mana = False, 4
	index = "Races~Paladin,Priest~Spell~4~Rally!"
	description = "Resurrect a friendly 1-Cost, 2-Cost, and 3-Cost minion"
	name_CN = "开赛集结！"
	def available(self):
		return self.selectableMinionExists()
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if curGame.mode == 0:
			if curGame.guides:
				minions = curGame.guides.pop(0)
			else:
				minionsDied = curGame.Counters.minionsDiedThisTurn[self.ID]
				minions = []
				for i in ('1', '2', '3'):
					try: minions.append(npchoice((index for index in minionsDied if index.split('~')[3] == i)))
					except: pass
				minions = tuple((curGame.cardPool[index] for index in minions))
				curGame.fixedGuides.append(minions)
			if minions:
				curGame.summon([minion(curGame, self.ID) for minion in minions], (-1, "totheRightEnd"), self)
		return None
		
		
class LibramofJudgement(Weapon):
	Class, name, description = "Paladin", "Libram of Judgement", "Corrupt: Gain Lifesteal"
	mana, attack, durability = 7, 5, 3
	index = "Races~Paladin~Weapon~7~5~3~Libram of Judgement~ToCorrupt"
	name_CN = "审判圣契"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsHand = [Trig_Corrupt(self, NitroboostPoison_Corrupt)] #只有在手牌中才会升级
		
class LibramofJudgement_Corrupt(Weapon):
	Class, name, description = "Paladin", "Libram of Judgement", "Corrupted. Lifesteal"
	mana, attack, durability = 7, 5, 3
	index = "Races~Paladin~Weapon~7~5~3~Libram of Judgement~Lifesteal~Corrupted~Uncollectible"
	name_CN = "审判圣契"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.keyWords["Lifesteal"] = 1
		
"""Priest Cards"""
class Hysteria(Spell):
	Class, school, name = "Priest,Warlock", "", "Hysteria"
	requireTarget, mana = True, 3
	index = "Races~Priest,Warlock~Spell~3~Hysteria"
	description = "Choose a minion. It attacks random minions until it dies"
	name_CN = "狂乱"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target and target.onBoard:
			curGame = self.Game
			if curGame.mode == 0:
				num = 0
				#The minion must still be onBoard and alive in order to continue the loop
				#Assume the loop can only last 14 times
				while target.onBoard and target.health > 0 and not target.dead and num < 14:
					if curGame.guides:
						i, where = curGame.guides.pop(0)
						minion = curGame.find(i, where) if i > -1 else None
					else:
						minions = curGame.minionsAlive(target.ID, target) + curGame.minionsAlive(3-target.ID)
						if minions:
							minion = npchoice(minions)
							curGame.fixedGuides.append((minion.pos, "Minion%d"%minion.ID))
						else:
							minion = None
							curGame.fixedGuides.append((-1, ''))
					if minion:
						curGame.battle(target, minion, verifySelectable=False, useAttChance=True, resolveDeath=False, resetRedirTrig=False)
					else: break
					num += 1
		return target
		
		
class Lightsteed(Minion):
	Class, race, name = "Priest", "Elemental", "Lightsteed"
	mana, attack, health = 4, 3, 6
	index = "Races~Priest~Minion~4~3~6~Elemental~Lightsteed"
	requireTarget, keyWord, description = False, "", "Your healing effects also give affected minions +2 Health"
	name_CN = "圣光战马"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_Lightsteed(self)]
		
class Trig_Lightsteed(TrigBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionGetsCured"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject.ID == self.entity.ID
		
	def text(self, CHN):
		return "你的治疗效果同时会使受到影响的随从获得+2生命值" if CHN else "Your healing effects also give affected minions +2 Health"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		target.buffDebuff(0, 2)
		
		
class DarkInquisitorXanesh(Minion):
	Class, race, name = "Priest", "", "Dark Inquisitor Xanesh"
	mana, attack, health = 5, 3, 5
	index = "Races~Priest~Minion~5~3~5~~Dark Inquisitor Xanesh~Battlecry~Legendary"
	requireTarget, keyWord, description = False, "", "Your healing effects also give affected minions +2 Health"
	name_CN = "黑暗审判官 夏奈什"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		for card in self.Game.Hand_Deck.hands[self.ID]:
			if "~ToCorrupt" in card.index:
				ManaMod(card, changeby=-2, changeto=-1).applies()
		for card in self.Game.Hand_Deck.decks[self.ID]:
			if "~ToCorrupt" in card.index:
				ManaMod(card, changeby=-2, changeto=-1).applies()
		return None
		
"""Rogue Cards"""
class NitroboostPoison(Spell):
	Class, school, name = "Rogue,Warrior", "", "Nitroboost Poison"
	requireTarget, mana = True, 1
	index = "Races~Rogue,Warrior~Spell~1~Nitroboost Poison~ToCorrupt"
	description = "Give a minion +2 Attack. Corrupt: And your weapon"
	name_CN = "氮素制剂"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsHand = [Trig_Corrupt(self, NitroboostPoison_Corrupt)] #只有在手牌中才会升级
		
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			target.buffDebuff(2, 0)
		return target
		
class NitroboostPoison_Corrupt(Spell):
	Class, school, name = "Rogue,Warrior", "", "Nitroboost Poison"
	requireTarget, mana = True, 1
	index = "Races~Rogue,Warrior~Spell~1~Nitroboost Poison~Corrupted~Uncollectible"
	description = "Corrupted: Give a minion and your weapon +2 Attack"
	name_CN = "氮素制剂"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			target.buffDebuff(2, 0)
			weapon = self.Game.availableWeapon(self.ID)
			if weapon: weapon.gainStat(2, 0)
		return target
		
class Shenanigans(Secret):
	Class, school, name = "Rogue", "", "Shenanigans"
	requireTarget, mana = False, 2
	index = "Races~Rogue~Spell~2~Shenanigans~~Secret"
	description = "Secret: When your opponent draws their second card in a turn, transform it into a Banana"
	name_CN = "蕉猾诡计"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_Shenanigans(self)]
		
class Trig_Shenanigans(SecretTrigger):
	def __init__(self, entity):
		self.blank_init(entity, ["CardDrawn"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		#假设即使第二张被爆牌也会触发
		secret = self.entity
		return self.entity.ID != self.entity.Game.turn and self.entity.ID != ID and self.entity.Game.Counters.numCardsDrawnThisTurn[ID] == 1
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		card = Bananas(self.entity.Game, self.entity.ID)
		self.entity.Game.Hand_Deck.replaceCardDrawn(target, card)
		
		
class SparkjoyCheat(Minion_Dormantfor2turns):
	Class, race, name = "Rogue", "", "Sparkjoy Cheat"
	mana, attack, health = 3, 3, 3
	index = "Races~Rogue~Minion~3~3~3~~Sparkjoy Cheat~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: If you're holding a Secret, cast it and draw a card"
	name_CN = "欢脱的 作弊选手"
	def effCanTrig(self):
		self.effectViable = any(card.description.startswith("Secret:") and not self.Game.Secrets.sameSecretExists(card, self.ID) \
									for card in self.Game.Hand_Deck.hands[self.ID])
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if curGame.mode == 0:
			if curGame.guides:
				i = curGame.guides.pop(0)
			else:
				#假设如果场上有相同奥秘，则不会计入随机列表
				indices = [i for i, card in enumerate(self.Game.Hand_Deck.hands[self.ID]) \
								if card.description.startswith("Secret:") and not curGame.Secrets.sameSecretExists(card, self.ID)]
				i = npchoice(indices) if indices else -1
				curGame.fixedGuides.append(i)
			if i > -1:
				curGame.Hand_Deck.extractfromHand(i, self.ID, enemyCanSee=False)[0].whenEffective()
				curGame.Hand_Deck.drawCard(self.ID)
		return None
		
		
"""Shaman Cards"""
class ImprisonedPhoenix(Minion_Dormantfor2turns):
	Class, race, name = "Shaman,Mage", "Elemental", "Imprisoned Phoenix"
	mana, attack, health = 2, 2, 3
	index = "Races~Shaman,Mage~Minion~2~2~3~Elemental~Imprisoned Phoenix~Spell Damge"
	requireTarget, keyWord, description = False, "", "Dormant for 2 turns. Spell Damage +2"
	name_CN = "被禁锢的凤凰"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.keyWords["Spell Damage"] = 2
		
		
class Landslide(Spell):
	Class, school, name = "Shaman", "", "Landslide"
	requireTarget, mana = False, 2
	index = "Races~Shaman~Spell~2~Landslide"
	description = "Deal 1 damage to all enemy minions. If you're Overloaded, deal 1 damage again"
	name_CN = "氮素制剂"
	def text(self, CHN):
		damage = (1 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		return "对所有敌方随从造成%d点伤害。如果你有过载的法力水晶，再次造成%d点伤害"%(damage, damage) \
				if CHN else "Deal %d damage to all enemy minions. If you're Overloaded, deal %d damage again"%(damage, damage)
				
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		damage = (1 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		targets = self.Game.minionsonBoard(3-self.ID)
		if targets:
			self.dealsAOE(targets, [damage]*len(targets))
			#假设插入随从的死亡结算
			self.Game.gathertheDead()
			damage = (1 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			targets = self.Game.minionsonBoard(3-self.ID)
			self.dealsAOE(targets, [damage]*len(targets))
		return None
		
		
class Mistrunner(Minion):
	Class, race, name = "Shaman", "", "Mistrunner"
	mana, attack, health = 5, 4, 4
	index = "Races~Shaman~Minion~5~4~4~~Mistrunner~Battlecry~Overload"
	requireTarget, keyWord, description = True, "", "Battlecry: Give a friendly minion +3/+3. Overload: (1)"
	name_CN = "迷雾行者"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.overload = 1
		
	def targetExists(self, choice=0):
		return self.selectableFriendlyMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.ID == self.ID and target.onBoard and target != self
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			target.buffDebuff(3, 3)
		return target
		
"""Warlock Cards"""
class Backfire(Spell):
	Class, school, name = "Warlock", "", "Backfire"
	requireTarget, mana = False, 3
	index = "Races~Warlock~Spell~3~Backfire"
	description = "Draw 3 cards. Deal 3 damage to your hero"
	name_CN = "赛车回火"
	def text(self, CHN):
		damage = (3 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		return "抽3张牌。对你的英雄造成%d点伤害"%damage if CHN else "Draw 3 cards. Deal %d damage to your hero"%damage
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		damage = (3 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		for i in range(3):
			self.Game.Hand_Deck.drawCard(self.ID)
		self.dealsDamage(self.Game.heroes[self.ID], damage)
		return None
		
		
class LuckysoulHoarder(Minion):
	Class, race, name = "Warlock,Demon Hunter", "", "Luckysoul Hoarder"
	mana, attack, health = 3, 3, 4
	index = "Races~Warlock,Demon Hunter~Minion~3~3~4~~Luckysoul Hoarder~Battlecry~ToCorrupt"
	requireTarget, keyWord, description = False, "", "Battlecry: Shuffle 2 Soul Fragments into your deck. Corrupt: Draw a card"
	name_CN = "幸运之魂 囤积者"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsHand = [Trig_Corrupt(self, LuckysoulHoarder_Corrupt)] #只有在手牌中才会升级
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.Game.Hand_Deck.shuffleintoDeck([SoulFragment(self.Game, self.ID) for i in range(2)], creator=self)
		return None
		
class LuckysoulHoarder_Corrupt(Minion):
	Class, race, name = "Warlock,Demon Hunter", "", "Luckysoul Hoarder"
	mana, attack, health = 3, 3, 4
	index = "Races~Warlock,Demon Hunter~Minion~3~3~4~~Luckysoul Hoarder~Battlecry~Corrupted~Uncollectible"
	requireTarget, keyWord, description = False, "", "Corrupted. Battlecry: Shuffle 2 Soul Fragments into your deck. Draw a card"
	name_CN = "幸运之魂 囤积者"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.Game.Hand_Deck.shuffleintoDeck([SoulFragment(self.Game, self.ID) for i in range(2)], creator=self)
		self.Game.Hand_Deck.drawCard(self.ID)
		return None
		
		
class EnvoyRustwix(Minion):
	Class, race, name = "Warlock", "Demon", "Envoy Rustwix"
	mana, attack, health = 5, 5, 4
	index = "Races~Warlock~Minion~5~5~4~Demon~Envoy Rustwix~Deathrattle~Legendary"
	requireTarget, keyWord, description = False, "", "Deathrattle: Shuffle 3 random Prime Legendary minions into your deck"
	name_CN = "铁锈特使 拉斯维克斯"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [Shuffle3PrimesintoYourDeck(self)]
		
class Shuffle3PrimesintoYourDeck(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		pool = (MsshifnPrime, ZixorPrime, SolarianPrime, MurgurglePrime, ReliquaryPrime, 
					AkamaPrime, VashjPrime, KanrethadPrime, KargathPrime)
		minion = self.entity
		curGame = minion.Game
		if curGame.mode == 0:
			if curGame.guides:
				primes = curGame.guides.pop(0)
			else:
				primes = npchoice(pool, 3, replace=True)
				curGame.fixedGuides.append(primes)
			minion.Game.Hand_Deck.shuffleintoDeck([prime(curGame, minion.ID) for prime in primes], creator=minion, possi=pool)
			
	def text(self, CHN):
		return "亡语：随机将3张终极传说随从洗入你的牌库" if CHN else "Deathrattle: Shuffle 3 random Prime Legendary minions into your deck"
		
		
"""Warrior Cards"""
class SpikedWheel(Weapon):
	Class, name, description = "Warrior", "Spiked Wheel", "Has +3 Attack when your hero has Armor"
	mana, attack, durability = 3, 1, 4
	index = "Races~Warrior~Weapon~3~1~4~Spiked Wheel"
	name_CN = "尖刺轮盘"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.auras["Has +3 Attack when your hero has Armor"] = WeaponBuffAura_SpikedWheel(self)
		
class WeaponBuffAura_SpikedWheel:
	def __init__(self, weapon):
		self.weapon = weapon
		self.auraAffected = []
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.weapon.onBoard and ID == self.weapon.ID
		
	def trig(self, signal, ID, subject, target, number, comment, choice=0):
		if self.canTrigger(signal, ID, subject, target, number, comment):
			self.effect(signal, ID, subject, target, number, comment)
			
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		for weapon, receiver in self.auraAffected[:]:
			receiver.effectClear()
		armor = self.weapon.Game.heroes[ID].armor
		if armor > 0: Stat_Receiver(self.weapon, self, armor, 0).effectStart()
		
	def auraAppears(self):
		game, ID = self.weapon.Game, self.weapon.ID
		armor = game.heroes[ID].armor
		if armor > 0: Stat_Receiver(self.weapon, self, armor, 0).effectStart()
		
		try: game.trigsBoard[ID]["ArmorGained"].append(self)
		except: game.trigsBoard[ID]["ArmorGained"] = [self]
		try: game.trigsBoard[ID]["ArmorLost"].append(self)
		except: game.trigsBoard[ID]["ArmorLost"] = [self]
		
	def auraDisappears(self):
		game, ID = self.weapon.Game, self.weapon.ID
		for weapon, receiver in self.auraAffected[:]:
			receiver.effectClear()
		self.auraAffected = []
		try: game.trigsBoard[ID]["ArmorGained"].remove(self)
		except: pass
		try: game.trigsBoard[ID]["ArmorLost"].remove(self)
		except: pass
		
		
class Ironclad(Minion):
	Class, race, name = "Warrior", "Mech", "Ironclad"
	mana, attack, health = 3, 2, 4
	index = "Races~Warrior~Minion~3~2~4~Mech~Ironclad~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: If your hero has Armor, gain +2/+2"
	name_CN = "铁甲战车"
	
	def effCanTrig(self):
		self.effectViable = self.Game.heroes[self.ID].armor > 0
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if self.Game.heroes[self.ID].armor > 0:
			self.buffDebuff(2, 2)
		return None
		
		
class Barricade(Spell):
	Class, school, name = "Warrior,Paladin", "", "Barricade"
	requireTarget, mana = False, 4
	index = "Races~Warrior,Paladin~Spell~4~Barricade"
	description = "Summon a 2/4 Guard with Taunt. If it's your only minion, summon another"
	name_CN = "路障"
	def available(self):
		return self.Game.space(self.ID) > 0
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.Game.summon(Guard(self.Game, self.ID), -1, self)
		#Note that at this stage, there won't be deaths/deathrattles resolved.
		if len(self.Game.minionsonBoard(self.ID)) == 1:
			self.Game.summon(Guard(self.Game, self.ID), -1, self)
		return target
		
		
class Guard(Minion):
	Class, race, name = "Warrior,Paladin", "", "Ironclad"
	mana, attack, health = 3, 2, 4
	index = "Races~Warrior,Paladin~Minion~3~2~4~~Ironclad~Taunt~Uncollectible"
	requireTarget, keyWord, description = False, "Taunt", "Taunt"
	name_CN = ""
	
	
Races_Indices = {"Races~Neutral~Minion~1~1~3~~Armor Vendor~Battlecry": ArmorVendor,
				"Races~Neutral~Minion~2~1~4~~Crabrider~Rush~Windfury": Crabrider,
				"Races~Neutral~Minion~3~2~5~~Deathwarden": Deathwarden,
				"Races~Neutral~Minion~5~6~3~Beast~Moonfang~Legendary": Moonfang,
				"Races~Neutral~Minion~9~9~9~Dragon~Runaway Blackwing": RunawayBlackwing,
				"Races~Demon Hunter~Spell~1~Illidari Studies": IllidariStudies,
				"Races~Demon Hunter,Hunter~Minion~2~2~3~~Felfire Deadeye": FelfireDeadeye,
				"Races~Demon Hunter~Minion~4~5~6~Demon~Felsaber": Felsaber,
				"Races~Druid,Shaman~Spell~1~Guidance": Guidance,
				"Races~Druid~Minion~3~3~4~Dragon~Dreaming Drake~Taunt~ToCorrupt": DreamingDrake,
				"Races~Druid~Minion~3~5~6~Dragon~Dreaming Drake~Taunt~Corrupted": DreamingDrake_Corrupt,
				"Races~Druid~Spell~5~Arbor Up": ArborUp,
				"Races~Hunter,Druid~Spell~1~Resizing Pouch": ResizingPouch,
				"Races~Hunter~Spell~2~Bola Shot": BolaShot,
				"Races~Hunter~Minion~3~3~4~~Saddlemaster": Saddlemaster,
				"Races~Mage~Minion~1~1~3~~Glacier Racer": GlacierRacer,
				"Races~Mage~Spell~2~Conjure Mana Biscuit": ConjureManaBiscuit,
				"Races~Mage~Spell~0~Mana Biscuit~Uncollectible": ManaBiscuit,
				"Races~Mage,Rogue~Minion~5~4~5~~Keywarden Ivory~Battlecry~Legendary": KeywardenIvory,
				"Races~Paladin~Minion~3~4~5~~Imprisoned Celestial": ImprisonedCelestial,
				"Races~Paladin,Priest~Spell~4~Rally!": Rally,
				"Races~Paladin~Weapon~7~5~3~Libram of Judgement~ToCorrupt": LibramofJudgement,
				"Races~Paladin~Weapon~7~5~3~Libram of Judgement~Lifesteal~Corrupted~Uncollectible": LibramofJudgement_Corrupt,
				"Races~Priest,Warlock~Spell~3~Hysteria": Hysteria,
				"Races~Priest~Minion~4~3~6~Elemental~Lightsteed": Lightsteed,
				"Races~Priest~Minion~5~3~5~~Dark Inquisitor Xanesh~Battlecry~Legendary": DarkInquisitorXanesh,
				"Races~Rogue,Warrior~Spell~1~Nitroboost Poison~ToCorrupt": NitroboostPoison,
				"Races~Rogue,Warrior~Spell~1~Nitroboost Poison~Corrupted~Uncollectible": NitroboostPoison_Corrupt,
				"Races~Rogue~Spell~2~Shenanigans~~Secret": Shenanigans,
				"Races~Rogue~Minion~3~3~3~~Sparkjoy Cheat~Battlecry": SparkjoyCheat,
				"Races~Shaman,Mage~Minion~2~2~3~Elemental~Imprisoned Phoenix~Spell Damge": ImprisonedPhoenix,
				"Races~Shaman~Spell~2~Landslide": Landslide,
				"Races~Shaman~Minion~5~4~4~~Mistrunner~Battlecry~Overload": Mistrunner,
				"Races~Warlock~Spell~3~Backfire": Backfire,
				"Races~Warlock,Demon Hunter~Minion~3~3~4~~Luckysoul Hoarder~Battlecry~ToCorrupt": LuckysoulHoarder,
				"Races~Warlock,Demon Hunter~Minion~3~3~4~~Luckysoul Hoarder~Battlecry~Corrupted~Uncollectible": LuckysoulHoarder_Corrupt,
				"Races~Warlock~Minion~5~5~4~Demon~Envoy Rustwix~Deathrattle~Legendary": EnvoyRustwix,
				"Races~Warrior~Weapon~3~1~4~Spiked Wheel": SpikedWheel,
				"Races~Warrior~Minion~3~2~4~Mech~Ironclad~Battlecry": Ironclad,
				"Races~Warrior,Paladin~Spell~4~Barricade": Barricade,
				"Races~Warrior,Paladin~Minion~3~2~4~~Ironclad~Taunt~Uncollectible": Guard,
				}