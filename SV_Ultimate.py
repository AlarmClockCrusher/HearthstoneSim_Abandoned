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

"""Forestcraft cards"""

"""Swordcraft cards"""

"""Runecraft cards"""

"""Dragoncraft cards"""

"""Shadowcraft cards"""

"""Bloodcraft cards"""

"""Havencraft cards"""


class HolyCavalier(SVMinion):
    Class, race, name = "Havencraft", "", "Holy Cavalier"
    mana, attack, health = 2, 1, 2
    index = "SV_Ultimate~Havencraft~Minion~2~1~2~None~Holy Cavalier~Taunt~Uncollectible"
    requireTarget, keyWord, description = False, "Taunt", "Ward."
    attackAdd, healthAdd = 2, 2
    name_CN = "圣骑兵"


class WilbertGrandKnight_Accelerate(SVSpell):
    Class, name = "Havencraft", "Wilbert, Grand Knight"
    requireTarget, mana = False, 3
    index = "SV_Ultimate~Havencraft~Spell~3~Wilbert, Grand Knight~Accelerate~Uncollectible"
    description = "Summon 2 Holy Cavaliers."
    name_CN = "尊荣骑士·维尔伯特"

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        self.Game.summon([HolyCavalier(self.Game, self.ID), HolyCavalier(self.Game, self.ID)], (-1, "totheRightEnd"),
                         self.ID)
        return None


class WilbertGrandKnight(SVMinion):
    Class, race, name = "Havencraft", "", "Wilbert, Grand Knight"
    mana, attack, health = 6, 4, 6
    index = "SV_Ultimate~Havencraft~Minion~6~4~6~None~Wilbert, Grand Knight~Battlecry~Deathrattle~Accelerate"
    requireTarget, keyWord, description = False, "", "Accelerate (3): Summon 2 Holy Cavaliers.Ward.Fanfare: Give your leader the following effect - Whenever an enemy follower attacks an allied follower with Ward, deal 2 damage to the enemy leader. (This effect is not stackable and lasts for the rest of the match.)Last Words: Give your leader the following effect - At the start of your turn, summon 2 Holy Cavaliers, then remove this effect."
    accelerateSpell = WilbertGrandKnight_Accelerate
    attackAdd, healthAdd = 2, 2
    name_CN = "尊荣骑士·维尔伯特"

    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.deathrattles = [Deathrattle_WilbertGrandKnight(self)]

    def getMana(self):
        if self.Game.Manas.manas[self.ID] < self.mana:
            return 3
        else:
            return self.mana

    def willAccelerate(self):
        curMana = self.Game.Manas.manas[self.ID]
        return self.mana > curMana >= 3

    def effCanTrig(self):
        if self.willAccelerate() and self.targetExists():
            self.effectViable = "sky blue"
        else:
            self.effectViable = False

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        trigger = Trig_WilbertGrandKnight(self.Game.heroes[self.ID])
        for t in self.Game.heroes[self.ID].trigsBoard:
            if type(t) == type(trigger):
                return
        self.Game.heroes[self.ID].trigsBoard.append(trigger)
        trigger.connect()
        return None


class Deathrattle_WilbertGrandKnight(Deathrattle_Minion):
    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        trigger = Trig_WilbertGrandKnight_TurnStarts(self.entity.Game.heroes[self.entity.ID])
        self.entity.Game.heroes[self.entity.ID].trigsBoard.append(trigger)
        trigger.connect()


class Trig_WilbertGrandKnight(TrigBoard):
    def __init__(self, entity):
        self.blank_init(entity, ["BattleStarted"])

    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
        return target.ID == self.entity.ID and target.type == "Minion" and target.keyWords["Taunt"] > 0

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        self.entity.dealsDamage(self.entity.Game.heroes[3 - self.entity.ID], 2)


class Trig_WilbertGrandKnight_TurnStarts(TrigBoard):
    def __init__(self, entity):
        self.blank_init(entity, ["TurnStarts"])

    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.onBoard and ID == self.entity.ID

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        self.entity.Game.summon(
            [HolyCavalier(self.entity.Game, self.entity.ID), HolyCavalier(self.entity.Game, self.entity.ID)],
            (-1, "totheRightEnd"), self.entity.ID)
        for t in self.entity.trigsBoard:
            if type(t) == Trig_WilbertGrandKnight_TurnStarts:
                t.disconnect()
                self.entity.trigsBoard.remove(t)
                break


"""Portalcraft cards"""

"""DLC cards"""


class GoddessoftheWestWind(SVMinion):
    Class, race, name = "Havencraft", "", "Goddess of the West Wind"
    mana, attack, health = 6, 3, 3
    index = "SV_Ultimate~Havencraft~Minion~6~3~3~None~Goddess of the West Wind~Battlecry"
    requireTarget, keyWord, description = False, "", "Fanfare: Randomly put 2 different Havencraft followers with an original attack of 2 or less from your deck into play."
    accelerateSpell = WilbertGrandKnight_Accelerate
    attackAdd, healthAdd = 2, 2
    name_CN = "丰饶的西风神"

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        curGame = self.Game
        if curGame.mode == 0:
            if curGame.guides:
                i1, i2 = curGame.guides.pop(0)
            else:
                minions = [i for i, card in enumerate(curGame.Hand_Deck.decks[self.ID]) if
                           card.type == "Minion" and card.Class == "Havencraft" and card.attack_0 <= 2]
                for m in minions:
                    print(curGame.Hand_Deck.decks[self.ID][m].name)
                i1 = npchoice(minions) if minions and curGame.space(self.ID) > 0 else -1
                curGame.fixedGuides.append(i1)
                name = curGame.Hand_Deck.decks[self.ID][i1].name
                for minion in minions:
                    if curGame.Hand_Deck.decks[self.ID][minion].name == name:
                        minions.remove(minion)
                for m in minions:
                    print(curGame.Hand_Deck.decks[self.ID][m].name)
                i2 = npchoice(minions) if minions and curGame.space(self.ID) > 1 else -1
            if i1 > -1:
                curGame.summonfromDeck(i1, self.ID, -1, self.ID)
            if i2 > -1:
                curGame.summonfromDeck(i2, self.ID, -1, self.ID)
        return None


SV_Ultimate_Indices = {
    "SV_Ultimate~Havencraft~Minion~2~1~2~None~Holy Cavalier~Taunt~Uncollectible": HolyCavalier,
    "SV_Ultimate~Havencraft~Spell~3~Wilbert, Grand Knight~Accelerate~Uncollectible": WilbertGrandKnight_Accelerate,
    "SV_Ultimate~Havencraft~Minion~6~4~6~None~Wilbert, Grand Knight~Battlecry~Deathrattle~Accelerate": WilbertGrandKnight,
    "SV_Ultimate~Havencraft~Minion~6~3~3~None~Goddess of the West Wind~Battlecry": GoddessoftheWestWind
}
