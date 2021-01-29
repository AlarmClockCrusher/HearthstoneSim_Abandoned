from CardTypes import *
from Triggers_Auras import *
from SV_Basic import *

import copy

from numpy.random import choice as npchoice
from numpy.random import randint as nprandint
from numpy.random import shuffle as npshuffle

import numpy as np


def extractfrom(target, listObj):
    try:
        return listObj.pop(listObj.index(target))
    except:
        return None


"""Neutral cards"""


class AssemblyDroid(SVMinion):
    Class, race, name = "Neutral", "Machina", "Assembly Droid"
    mana, attack, health = 1, 1, 1
    index = "SV_Uprooted~Neutral~Minion~1~1~1~Machina~Assembly Droid~Uncollectible"
    requireTarget, keyWord, description = False, "", ""
    attackAdd, healthAdd = 2, 2


class NaterranGreatTree(Amulet):
    Class, race, name = "Neutral", "Natura", "Naterran Great Tree"
    mana = 1
    index = "SV_Uprooted~Neutral~Amulet~1~Natura~Naterran Great Tree~Battlecry~Deathrattle~Uncollectible"
    requireTarget, description = False, "Fanfare: If any other allied Naterran Great Trees are in play, randomly destroy 1.Last Words: Draw a card."

    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.deathrattles = [Deathrattle_NaterranGreatTree(self)]

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        trees = []
        for amulet in self.Game.amuletsonBoard(self.ID, self):
            if amulet.name == "Naterran Great Tree":
                trees.append(amulet)
        if trees:
            curGame = self.Game
            if curGame.mode == 0:
                if curGame.guides:
                    i = curGame.guides.pop(0)
                else:
                    i = npchoice(trees).pos
                    curGame.fixedGuides.append(i)
                tree = curGame.minions[self.ID][i]
                self.Game.killMinion(self, tree)


class Deathrattle_NaterranGreatTree(Deathrattle_Minion):
    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        self.entity.Game.Hand_Deck.drawCard(self.entity.ID)


class WayfaringIllustrator(SVMinion):
    Class, race, name = "Neutral", "", "Wayfaring Illustrator"
    mana, attack, health = 2, 2, 2
    index = "SV_Uprooted~Neutral~Minion~2~2~2~None~Wayfaring Illustrator~Battlecry"
    requireTarget, keyWord, description = True, "", "Fanfare: Select an allied Machina or Natura follower and put a copy of it into your hand."
    attackAdd, healthAdd = 2, 2

    def targetExists(self, choice=0):
        return any(("Machina" in minion.race or "Natura" in minion.race) and self.canSelect(minion) for minion in self.Game.minionsAlive(self.ID))
		
    def targetCorrect(self, target, choice=0):
        if isinstance(target, list): target = target[0]
        return target.type == "Minion" and target.ID == self.ID and target.onBoard and (
                "Machina" in target.race or "Natura" in target.race)

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if target:
            if isinstance(target, list): target = target[0]
            self.Game.Hand_Deck.addCardtoHand([type(target)], self.ID, byType=True, creator=type(self))
        return None


class ChangewingCherub(SVMinion):
    Class, race, name = "Neutral", "Machina,Natura", "Changewing Cherub"
    mana, attack, health = 2, 1, 3
    index = "SV_Uprooted~Neutral~Minion~2~1~3~Machina,Natura~Changewing Cherub~Battlecry"
    requireTarget, keyWord, description = True, "", "Fanfare: Deal 2 damage to an enemy follower if at least 2 other cards were played this turn."
    attackAdd, healthAdd = 2, 2

    def returnTrue(self, choice=0):
        machina = 0
        for card in self.Game.Hand_Deck.hands[self.ID]:
            if card.type == "Minion" and card != self and "Machina" in card.race:
                machina += 1
        return machina >= 3 and self.targetExists(choice) and not self.targets

    def effCanTrig(self):
        machina, natura = 0, 0
        for card in self.Game.Hand_Deck.hands[self.ID]:
            if card.type == "Minion" and card != self:
                if "Natura" in card.race:
                    natura += 1
                if "Machina" in card.race:
                    machina += 1
        self.effectViable = machina >= 3 or natura >= 3

    def targetExists(self, choice=0):
        return self.selectableEnemyMinionExists()

    def targetCorrect(self, target, choice=0):
        if isinstance(target, list): target = target[0]
        return target.type == "Minion" and target.ID != self.ID and target.onBoard

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if target:
            if isinstance(target, list): target = target[0]
            self.dealsDamage(target, 2)
        natura = 0
        for card in self.Game.Hand_Deck.hands[self.ID]:
            if card.type == "Minion" and card != self and "Natura" in card.race:
                natura += 1
        if natura >= 3:
            self.restoresHealth(self.Game.heroes[self.ID], 2)
        return None

    def inHandEvolving(self, target=None):
        self.Game.options = [AssemblyDroid(self.Game, self.ID), NaterranGreatTree(self.Game, self.ID)]
        self.Game.Discover.startDiscover(self)

    def discoverDecided(self, option, pool):
        self.Game.fixedGuides.append(type(option))
        self.Game.Hand_Deck.addCardtoHand(option, self.ID, byDiscover=True)


class PluckyTreasureHunter(SVMinion):
    Class, race, name = "Neutral", "", "Plucky Treasure Hunter"
    mana, attack, health = 3, 2, 3
    index = "SV_Uprooted~Neutral~Minion~3~2~3~None~Plucky Treasure Hunter~Battlecry"
    requireTarget, keyWord, description = True, "", "Fanfare: If you have any Machina or Natura cards in your hand, discard 1. Then put 2 random cards that share a trait with that card from your deck into your hand."
    attackAdd, healthAdd = 2, 2

    def effCanTrig(self):
        for card in self.Game.Hand_Deck.hands[self.ID]:
            if card.type == "Minion" and card != self:
                if "Natura" in card.race or "Machina" in card.race:
                    self.effectViable = True

    def targetExists(self, choice=0):
        for card in self.Game.Hand_Deck.hands[self.ID]:
            if card.type == "Minion" and card != self:
                if "Natura" in card.race or "Machina" in card.race:
                    return True
        return False

    def targetCorrect(self, target, choice=0):
        if isinstance(target, list): target = target[0]
        return target.ID == self.ID and target.inHand and target != self and (
                "Natura" in target.race or "Machina" in target.race)

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if target:
            if isinstance(target, list): target = target[0]
            races = target.race.split(",")
            self.Game.Hand_Deck.discardCard(self.ID, target)
            curGame = self.Game
            if curGame.mode == 0:
                for n in range(2):
                    if curGame.guides:
                        i = curGame.guides.pop(0)
                    else:
                        cards = []
                        for i, card in enumerate(curGame.Hand_Deck.decks[self.ID]):
                            fit = False
                            for race in races:
                                if race in card.race:
                                    fit = True
                            if fit:
                                cards.append(i)
                        i = npchoice(cards) if cards else -1
                        curGame.fixedGuides.append(i)
                    if i > -1: curGame.Hand_Deck.drawCard(self.ID, i)
        return target


class RomanticChanteuse(SVMinion):
    Class, race, name = "Neutral", "", "Romantic Chanteuse"
    mana, attack, health = 3, 2, 3
    index = "SV_Uprooted~Neutral~Minion~3~2~3~None~Romantic Chanteuse~Battlecry"
    requireTarget, keyWord, description = True, "", "Fanfare: Give an enemy the following effect until the start of your next turn - Reduce all damage dealt to 0. (Applies to attacks and effects.)"
    attackAdd, healthAdd = 2, 2

    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.trigsBoard = [Trig_RomanticChanteuse(self)]

    def targetExists(self, choice=0):
        return self.selectableEnemyExists() or self.selectableEnemyAmuletExists()

    def targetCorrect(self, target, choice=0):
        if isinstance(target, list): target = target[0]
        return target.type in ["Minion", "Amulet", "Hero"] and target.ID != self.ID and target.onBoard

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if target:
            if isinstance(target, list): target = target[0]
            trigger = Trig_RomanticChanteuse(target)
            target.trigsBoard.append(trigger)
            trigger.connect()
        return target

class Trig_RomanticChanteuse(TrigBoard):
    def __init__(self, entity):
        self.blank_init(entity, ["BattleDmgHero", "BattleDmgMinion","AbilityDmgHero","AbilityDmgMinion", "TurnEnds"])

    def canTrig(self, signal, ID, subject, target, number, comment,
                choice=0):  # target here holds the actual target object
        return signal[0] == 'T' and ID == self.entity.ID or subject == self.entity

    def text(self, CHN):
        return "该从者给予的伤害皆转变为0" if CHN else "During this turn, this follower deals damage equal to its defense when attacks"

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        if signal[0] == 'T':
            try:
                self.entity.trigsBoard.remove(self)
            except:
                pass
            self.disconnect()
        else:
            number[0] = 0


class GabrielHeavenlyVoice(SVMinion):
    Class, race, name = "Neutral", "", "Gabriel, Heavenly Voice"
    mana, attack, health = 3, 2, 3
    index = "SV_Uprooted~Neutral~Minion~3~2~3~None~Gabriel, Heavenly Voice~Battlecry~Taunt~Legendary"
    requireTarget, keyWord, description = True, "Taunt", "Ward.Fanfare: Use X play points to give +X/+X to this follower and another allied follower. X equals your remaining play points."
    name_CN = "神谕的大天使·加百列"

    def targetExists(self, choice=0):
        return self.selectableFriendlyMinionExists(choice)

    def targetCorrect(self, target, choice=0):
        if isinstance(target, list): target = target[0]
        return target.type == "Minion" and target.ID == self.ID and target.onBoard and target != self

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        x = self.Game.Manas.manas[self.ID]
        self.Game.Manas.payManaCost(self, x)
        if target:
            if isinstance(target, list): target = target[0]
            target.buffDebuff(x, x)
        self.buffDebuff(x, x)
        return None


class GoblinWarpack(SVSpell):
    Class, name = "Neutral", "Goblin Warpack"
    requireTarget, mana = False, 3
    index = "SV_Uprooted~Neutral~Spell~2~Goblin Warpack~Enhance"
    description = "Summon 2 Goblins.Enhance (6): Summon 5 instead.Enhance (9): Then evolve all unevolved allied Goblins."

    def getMana(self):
        if self.Game.Manas.manas[self.ID] >= 9:
            return 9
        elif self.Game.Manas.manas[self.ID] >= 6:
            return 6
        else:
            return self.mana

    def willEnhance(self):
        return self.Game.Manas.manas[self.ID] >= 6

    def effCanTrig(self):
        self.effectViable = self.willEnhance()

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        n = 3
        if comment == 6 or comment == 9:
            n = 5
        minions = [Goblin(self.Game, self.ID) for i in range(n)]
        self.Game.summon(minions, (-1, "totheRightEnd"), self.ID)
        if comment == 9:
            for minion in minions:
                minion.evolve()
        return None


class WeveGotaCase(SVSpell):
    Class, name = "Neutral", "We've Got a Case!"
    requireTarget, mana = True, 6
    index = "SV_Uprooted~Neutral~Spell~6~We've Got a Case!"
    description = "Draw 3 cards. Then deal X damage to an enemy follower. X equals the number of cards in your hand."

    def targetCorrect(self, target, choice=0):
        if isinstance(target, list): target = target[0]
        return target.type == "Minion" and target.onBoard and target.ID != self.ID

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        for i in range(3):
            self.Game.Hand_Deck.drawCard(self.ID)
        if target:
            if isinstance(target, list): target = target[0]
            damage = (len(self.Game.Hand_Deck.hands[self.ID]) + self.countSpellDamage()) * (
                    2 ** self.countDamageDouble())
            self.dealsDamage(target, damage)
        return target


class BoomDevil(SVMinion):
    Class, race, name = "Neutral", "", "Boom Devil"
    mana, attack, health = 7, 5, 5
    index = "SV_Uprooted~Neutral~Minion~7~5~5~None~Boom Devil~Battlecry"
    requireTarget, keyWord, description = False, "", "Fanfare: Deal 5 damage to the enemy leader. If this is your tenth turn or later, deal 5 damage to all enemies instead."

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if self.Game.Counters.turns[self.ID] >= 10:
            self.dealsAOE(self.Game.minionsonBoard(3 - self.ID) + [self.Game.heroes[3 - self.ID]], 5)
        else:
            self.dealsDamage(self.Game.heroes[3 - self.ID], 5)
        return None


class Terrorformer(SVMinion):
    Class, race, name = "Neutral", "", "Terrorformer"
    mana, attack, health = 7, 6, 6
    index = "SV_Uprooted~Neutral~Minion~7~6~6~None~Terrorformer~Battlecry~Fusion~Legendary"
    requireTarget, keyWord, description = True, "", "Fusion: Machina or Natura Fanfare: Deal X damage to an enemy follower. Put X random Machina or Natura cards from your deck into your hand. If this card is fused with a Machina and Natura card, subtract 3 from their costs. X equals the number of cards fused to this card."
    attackAdd, healthAdd = 2, 2

    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.fusion = 1
        self.fusionMaterials = 0
        self.progress = 1

    def targetCorrect(self, target, choice=0):
        if isinstance(target, list): target = target[0]
        return target.type == "Minion" and target.ID != self.ID and target.onBoard

    def targetExists(self, choice=0):
        return self.selectableEnemyMinionExists()

    def findFusionMaterials(self):
        return [card for card in self.Game.Hand_Deck.hands[self.ID] if
                card.type == "Minion" and card != self and ("Natura" in card.race or "Machina" in card.race)]

    def fusionDecided(self, objs):
        if objs:
            self.fusionMaterials += len(objs)
            self.Game.Hand_Deck.extractfromHand(self, enemyCanSee=True)
            for obj in objs:
                if "Natura" in obj.race:
                    self.progress *= 2
                if "Machina" in obj.race:
                    self.progress *= 3
                self.Game.Hand_Deck.extractfromHand(obj, enemyCanSee=True)
            self.Game.Hand_Deck.addCardtoHand(self, self.ID)
            self.fusion = 0  # 一张卡每回合只有一次融合机会

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if target:
            if isinstance(target, list): target = target[0]
            self.dealsDamage(target, self.fusionMaterials)
            curGame = self.Game
            if curGame.mode == 0:
                for n in range(self.fusionMaterials):
                    if curGame.guides:
                        i = curGame.guides.pop(0)
                    else:
                        cards = []
                        for i, card in enumerate(curGame.Hand_Deck.decks[self.ID]):
                            if "Natura" in card.race or "Machina" in card.race:
                                cards.append(i)
                        i = npchoice(cards) if cards else -1
                        curGame.fixedGuides.append(i)
                    if i > -1: curGame.Hand_Deck.drawCard(self.ID, i)
        return target


"""Forestcraft cards"""

"""Swordcraft cards"""
class StrokeofConviction(SVSpell):
    Class, name = "Swordcraft", "Stroke of Conviction"
    requireTarget, mana = False, 3
    index = "SV_Uprooted~Swordcraft~Spell~3~Stroke of Conviction~Enhance"
    description = ""
	name_CN = "信念之剑闪"
	#艾莉卡的战技 #Erika's Sleight, 召唤2个迅捷的剑士到战场上
	#米丝特莉娜的剑刃 #Mistolina's Swordpla #随机给予1个敌方的从者5点伤害
	#贝里昂的号令 #Bayleyon's Command #给予自己的从者全体+1/+1效果
	#使自己的PP消耗与这张 卡牌等量的消费值，在使用这张卡牌时将其墨迹为命运抉择 所指定的卡牌
	#爆能强化6；由原本的命运抉择转变为召唤2个迅捷的剑士到战场上。随机给予一个敌方的从者5点伤害。给予自己的从者全体+1/+1效果
    def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.options = [ErikasSleight_Option(self), MistolinasSwordpla_Option(self),
						BayleyonsCommand_Option(self)]
		
	def getMana(self):
        if self.Game.Manas.manas[self.ID] >= 6:
            return 6
        return self.mana

	def need2Choose(self):
		return not self.willEnhance()
		
    def willEnhance(self):
        return self.Game.Manas.manas[self.ID] >= 6

	def becomeswhenPlayed(self, choice=0):
		return (self if self.willEnhance() else self.options[choice]), self.getMana()
		
    def effCanTrig(self):
        self.effectViable = self.willEnhance()

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        curGame = self.Game
		if comment == 6 or choice == 0:
			curGame.summon([Quickblader(curGame, self.ID) for i in range(2)], (-1, "totheRightEnd"), self)
		if comment == 6 or choice == 1:
			if curGame.mode == 0:
				if curGame.guides:
					i, where = curGame.guides.pop(0)
					minion = curGame.find(i, where) if i > -1 else None
				else:
					minions = curGame.minionsAlive(3-self.ID)
					minion = npchoice(minions) if minions else None
					curGame.fixedGuides.append((minion.pos, "Minion%d"%(3-self.ID)) if minion else (-1, ''))
				if minion: self.dealsDamage(minion, 5)
        if comment == 6 or choice == 2:
			for minion in curGame.minionsonBoard(self.ID):
				minion.buffDebuff(1, 1)
				
        return None

class ErikasSleight_Option(ChooseOneOption):
	name, description = "Erika's Sleight", "Summon 2 Quickbladers"
	index = "SV_Uprooted~Swordcraft~Spell~0~Erika's Sleight"
	def available(self):
		return True
		
		
class MistolinasSwordpla_Option(ChooseOneOption):
	name, description = "Mistolina's Swordpla", "Deal 5 damage to a random enemy follower"
	index = "SV_Uprooted~Swordcraft~Spell~0~Mistolina's Swordpla"
	def available(self):
		return True
		
class BayleyonsCommand_Option(ChooseOneOption):
	name, description = "Bayleyon's Command", "Give all allied followers +1/+1"
	index = "SV_Uprooted~Swordcraft~Spell~0~Bayleyon's Command"
	def available(self):
		return True
		
class ErikasSleight(SVSpell):
    Class, name = "Swordcraft", "Erika's Sleight"
    requireTarget, mana = False, 0
    index = "SV_Uprooted~Swordcraft~Spell~0~Erika's Sleight"
    description = ""
	name_CN = "艾莉卡的战技"
	
class MistolinasSwordpla(SVSpell):
    Class, name = "Swordcraft", "Mistolina’s Swordpla"
    requireTarget, mana = False, 0
    index = "SV_Uprooted~Swordcraft~Spell~0~Mistolina’s Swordpla"
    description = ""
	name_CN = "米丝特莉娜的剑刃"
	
class BayleyonsCommand(SVSpell):
    Class, name = "Swordcraft", "Bayleyon's Command"
    requireTarget, mana = False, 0
    index = "SV_Uprooted~Swordcraft~Spell~0~Bayleyon's Command"
    description = ""
	name_CN = "贝里昂的号令"
	
	

class PaulaIcyWarmth(SVMinion):
    Class, race, name = "Forestcraft", "", "Paula, Icy Warmth"
    mana, attack, health = 2, 2, 2
    index = "SV_Uprooted~Forestcraft~Minion~2~2~2~None~Paula, Icy Warmth"
    requireTarget, keyWord, description = True, "", ""
    attackAdd, healthAdd = 2, 2
	def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.options = [PaulaGentalWarmth_Option(self), PaulaPassionateWarmth_Option(self)]
		
	def need2Choose(self):
		return self.Game.Manas.manas[self.ID] > 2 \
				and self.Game.Counters.numCardsPlayedThisTurn[self.ID] > 2
		
    def targetCorrect(self, target, choice=0):
        if isinstance(target, list): target = target[0]
        if choice == 0:
			return (target.type == "Minion" or target.type == "Amulet") and target.ID == self.ID and target != self and target.onBoard
		else:
			return target.type == "Minion" and target.ID != self.ID and target.onBoard
			
	def returnTrue(self, choice=0):
		return self.Game.Manas.manas[self.ID] > 2 \
				and self.Game.Counters.numCardsPlayedThisTurn[self.ID] > 2
		
	def targetExists(self, choice=0):
		if choice == 0: return self.entity.selectableFriendlyMinionExists(0) \
								or self.entity.selectableFriendlyAmuletExists(0)
		else: return self.entity.selectableEnemyMinionExists(1)
		
	def becomeswhenPlayed(self, choice=0):
		return (self if choice < 0 else self.options[choice]), self.getMana()
		
    def effCanTrig(self):
        self.effectViable = self.Game.Manas.manas[self.ID] > 2 \
							and self.Game.Counters.numCardsPlayedThisTurn[self.ID] > 2

class PaulaGentalWarmth_Option(ChooseOneOption):
	name, description = "Paula, Gental Warmth", ""
	#入场曲：将战场上1个自己的其他随从或1个自己的护符收回手牌中
	def available(self):
		return self.entity.selectableFriendlyMinionExists(0) \
				or self.entity.selectableFriendlyAmuletExists(0)
		
class PaulaPassionateWarmth_Option(ChooseOneOption):
	name, description = "Paula, Passionate Warmth", ""
	#入场曲 给予1个敌方的随从1点伤害
	def available(self):
		return self.entity.selectableEnemyMinionExists(1)
		
class PaulaGentalWarmth(SVMinion):
    Class, race, name = "Forestcraft", "", "Paula, Gental Warmth"
    mana, attack, health = 2, 2, 2
    index = "SV_Uprooted~Forestcraft~Minion~2~2~2~None~Paula, Gental Warmth~Uncollectible"
    requireTarget, keyWord, description = True, "", ""
    attackAdd, healthAdd = 2, 2
	
class PaulaPassionateWarmth(SVMinion):
    Class, race, name = "Forestcraft", "", "Paula, Passionate Warmth"
    mana, attack, health = 2, 2, 2
    index = "SV_Uprooted~Forestcraft~Minion~2~2~2~None~Paula, Passionate Warmth~Uncollectible"
    requireTarget, keyWord, description = True, "", ""
    attackAdd, healthAdd = 2, 2
	
"""Runecraft cards"""

"""Dragoncraft cards"""

"""Shadowcraft cards"""

"""Bloodcraft cards"""

"""Havencraft cards"""

"""Portalcraft cards"""

"""DLC cards"""

SV_Uprooted_Indices = {
    "SV_Uprooted~Neutral~Minion~3~2~3~None~Gabriel, Heavenly Voice~Battlecry~Taunt~Legendary": GabrielHeavenlyVoice,
}
