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


class IoJourneymage(SVMinion):
    Class, race, name = "Neutral", "", "Io, Journeymage"
    mana, attack, health = 2, 1, 2
    index = "SV_Eternal~Neutral~Minion~2~1~2~None~Io, Journeymage~Battlecry~Enhance"
    requireTarget, keyWord, description = True, "", "Fanfare: Deal 1 damage to an enemy follower and then 1 damage to the enemy leader. Restore 1 defense to your leader.Enhance (5): Deal 2 damage, restore 2 defense, and gain +2/+2 instead.Enhance (8): Deal 4 damage, restore 4 defense, and gain +4/+4 instead."
    attackAdd, healthAdd = 2, 2
    name_CN = "苍心的少女·伊欧"

    def returnTrue(self, choice=0):
        return self.targetExists(choice) and not self.targets

    def getMana(self):
        if self.Game.Manas.manas[self.ID] >= 8:
            return 8
        else:
            if self.Game.Manas.manas[self.ID] >= 5:
                return 5
            else:
                return self.mana

    def willEnhance(self):
        return self.Game.Manas.manas[self.ID] >= 5

    def effCanTrig(self):
        self.effectViable = self.willEnhance()

    def targetExists(self, choice=0):
        return self.selectableEnemyMinionExists()

    def targetCorrect(self, target, choice=0):
        if isinstance(target, list): target = target[0]
        return target.type == "Minion" and target.ID != self.ID and target.onBoard

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if target:
            if isinstance(target, list): target = target[0]
        if comment == 8:
            if target:
                self.dealsDamage(target, 4)
            self.dealsDamage(self.Game.heroes[3 - self.ID], 4)
            self.restoresHealth(self.Game.heroes[self.ID], 4)
            self.buffDebuff(4, 4)
        elif comment == 5:
            if target:
                self.dealsDamage(target, 2)
            self.dealsDamage(self.Game.heroes[3 - self.ID], 2)
            self.restoresHealth(self.Game.heroes[self.ID], 2)
            self.buffDebuff(2, 2)
        else:
            if target:
                self.dealsDamage(target, 1)
            self.dealsDamage(self.Game.heroes[3 - self.ID], 1)
            self.restoresHealth(self.Game.heroes[self.ID], 1)
        return None


class ArchangelofRemembrance(SVMinion):
    Class, race, name = "Neutral", "", "Archangel of Remembrance"
    mana, attack, health = 2, 2, 1
    index = "SV_Eternal~Neutral~Minion~2~2~1~None~Archangel of Remembrance~Battlecry~Enhance"
    requireTarget, keyWord, description = True, "", "Fanfare: Banish an enemy follower with 1 defense."
    attackAdd, healthAdd = 2, 2
    evolveRequireTarget = True
    name_CN = "追忆的大天使"

    def returnTrue(self, choice=0):
        return self.targetExists(choice) and not self.targets

    def targetExists(self, choice=0):
        minions = self.Game.minionsonBoard(3 - self.ID)
        for minion in minions:
            if self.canSelect(minion) and minion.health == 1:
                return True
        return False

    def targetCorrect(self, target, choice=0):
        if isinstance(target, list): target = target[0]
        return target.type == "Minion" and target.ID != self.ID and target.onBoard and target.health == 1

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if target:
            if isinstance(target, list): target = target[0]
            self.Game.banishMinion(self, target)
        return None

    def evolveTargetExists(self, choice=0):
        return len(self.Game.Hand_Deck.hands[self.ID]) > 0

    def evolveTargetCorrect(self, target, choice=0):
        if isinstance(target, list): target = target[0]
        return target.ID == self.ID and target.inHand and target != self

    def inHandEvolving(self, target=None):
        if target:
            if isinstance(target, list): target = target[0]
            self.Game.Hand_Deck.extractfromHand(target, self.ID)
            self.Game.Hand_Deck.shuffleintoDeck([type(target)(self.Game, self.ID)], self.ID)
            self.Game.Hand_Deck.drawCard(self.ID)
            self.Game.Hand_Deck.drawCard(self.ID)
        return target


"""Forestcraft cards"""

"""Swordcraft cards"""

"""Runecraft cards"""

"""Dragoncraft cards"""

"""Shadowcraft cards"""

"""Bloodcraft cards"""

"""Havencraft cards"""


class SummitTemple(Amulet):
    Class, race, name = "Havencraft", "", "Summit Temple"
    mana = 1
    index = "SV_Eternal~Havencraft~Amulet~1~Battlecry~Summit Temple"
    requireTarget, description = False, "Fanfare: If any other allied Summit Temples are in play, draw a card and then destroy this amulet.Whenever an allied Havencraft follower attacks, give it the following effect until the end of the turn: This follower deals damage equal to its defense."
    name_CN = "峰顶的教会"

    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.trigsBoard = [Trig_SummitTemple(self)]

    def effCanTrig(self):
        self.effectViable = any(amulet.name == "Summit Temple" for amulet in self.Game.amuletsonBoard(self.ID, self))

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if any(amulet.name == "Summit Temple" for amulet in self.Game.amuletsonBoard(self.ID, self)):
            self.Game.Hand_Deck.drawCard(self.ID)
            self.Game.killMinion(self, self)
        return None


class Trig_SummitTemple(TrigBoard):
    def __init__(self, entity):
        self.blank_init(entity, ["MinionAttacksHero", "MinionAttacksMinion"])

    def canTrig(self, signal, ID, subject, target, number, comment,
                choice=0):  # target here holds the actual target object
        return subject.ID == self.entity.ID and subject.Class == "Havencraft"

    def text(self, CHN):
        return "" if CHN else "When an allied Havencraft follower attacks, give it 'This follower deals damage equal to its defense until the end of this turn'"

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        trig = Trig_AttUsesHealth(subject)
        subject.trigsBoard.append(trig)
        trig.connect()


class Trig_AttUsesHealth(TrigBoard):
    def __init__(self, entity):
        self.blank_init(entity, ["BattleDmg?", "TurnEnds"])

    def canTrig(self, signal, ID, subject, target, number, comment,
                choice=0):  # target here holds the actual target object
        return signal[0] == 'T' or subject == self.entity

    def text(self, CHN):
        return "该从者给予的战斗伤害等于其生命值" if CHN else "During this turn, this follower deals damage equal to its defense when attacks"

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        if signal[0] == 'T':
            try:
                self.entity.trigsBoard.remove(self)
            except:
                pass
            self.disconnect()
        else:
            number[0] = max(0, self.entity.health)


class NoaPrimalShipwright_Crystallize(Amulet):
    Class, race, name = "Havencraft", "", "Crystallize: Noa, Primal Shipwright"
    mana = 1
    index = "SV_Eternal~Havencraft~Amulet~1~None~Noa, Primal Shipwright~Countdown~Crystallize~Deathrattle~Uncollectible"
    requireTarget, description = False, "Countdown (10) At the end of your turn, subtract X from this amulet's Countdown. X equals the number of allied followers with Ward in play. Last Words: Summon an Anvelt, Judgment's Cannon."
    name_CN = "结晶：星界的艇人·诺亚"

    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.counter = 4
        self.trigsBoard = [Trig_Countdown(self)]
        self.deathrattles = [Deathrattle_NoaPrimalShipwright_Crystallize(self)]


class Deathrattle_NoaPrimalShipwright_Crystallize(Deathrattle_Minion):
    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        self.entity.Game.summon([NoaPrimalShipwright(self.entity.Game, self.entity.ID)], (-1, "totheRightEnd"),
                                self.entity.ID)


class NoaPrimalShipwright(SVMinion):
    Class, race, name = "Havencraft", "", "Noa, Primal Shipwright"
    mana, attack, health = 7, 1, 1
    index = "SV_Eternal~Havencraft~Minion~7~1~1~None~Noa, Primal Shipwright~Taunt~Crystallize"
    requireTarget, keyWord, description = True, "", "Crystallize (1): Countdown (10) At the end of your turn, subtract X from this amulet's Countdown. X equals the number of allied followers with Ward in play.Last Words: Summon an Anvelt, Judgment's Cannon.Ward.When this follower comes into play, deal 4 damage to all enemy followers and then 2 damage to the enemy leader."
    crystallizeAmulet = NoaPrimalShipwright_Crystallize
    attackAdd, healthAdd = 2, 2
    name_CN = "星界的艇人·诺亚"

    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.appearResponse = [self.whenAppears]

    def whenAppears(self):
        link = self.Game.Counters.numMinionsSummonedThisGame[self.ID]
        self.buffDebuff(link, link)
        if link >= 10:
            self.evolve()

    def returnTrue(self, choice=0):
        return self.targetExists(choice) and not self.targets

    def targetExists(self, choice=0):
        if self.willCrystallize():
            return False
        return self.selectableEnemyMinionExists()

    def targetCorrect(self, target, choice=0):
        if isinstance(target, list): target = target[0]
        return not self.willCrystallize() and target.type == "Minion" and target.ID != self.ID and target.onBoard

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if target:
            if isinstance(target, list): target = target[0]
            target.loseAbility()
            target.buffDebuff(0, -5)
        return target

    def getMana(self):
        if self.Game.Manas.manas[self.ID] < self.mana:
            return 1
        else:
            return self.mana

    def willCrystallize(self):
        curMana = self.Game.Manas.manas[self.ID]
        return self.mana > curMana >= 1

    def effCanTrig(self):
        if self.willCrystallize():
            self.effectViable = "sky blue"
        else:
            self.effectViable = False


"""Portalcraft cards"""

"""DLC cards"""

SV_Eternal_Indices = {
    "SV_Eternal~Neutral~Minion~2~1~2~None~Io, Journeymage~Battlecry~Enhance": IoJourneymage,
    "SV_Eternal~Neutral~Minion~2~2~1~None~Archangel of Remembrance~Battlecry~Enhance": ArchangelofRemembrance,
    "SV_Eternal~Havencraft~Amulet~1~Battlecry~Summit Temple": SummitTemple,
    "SV_Eternal~Havencraft~Amulet~1~None~Noa, Primal Shipwright~Countdown~Crystallize~Deathrattle~Uncollectible": NoaPrimalShipwright_Crystallize,
    "SV_Eternal~Havencraft~Minion~7~1~1~None~Noa, Primal Shipwright~Taunt~Crystallize": NoaPrimalShipwright
}
