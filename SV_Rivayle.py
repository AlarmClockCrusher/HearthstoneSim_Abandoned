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


class DutifulSteed(Amulet):
    Class, race, name = "Neutral", "", "Dutiful Steed"
    mana = 1
    index = "SV_Rivayle~Neutral~Amulet~1~None~Dutiful Steed~Uncollectible"
    requireTarget, description = False, "During your turn, when an allied follower comes into play, give it +1/+1 and banish this amulet."
    name_CN = "顺从的骏马"

    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.trigsBoard = [Trig_DutifulSteed(self)]


class Trig_DutifulSteed(TrigBoard):
    def __init__(self, entity):
        self.blank_init(entity, ["MinionSummoned"])

    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
        return subject.Game.turn == self.entity.ID == subject.ID and self.entity.onBoard

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        self.entity.Game.banishMinion(self.entity, self.entity)
        subject.buffDebuff(1, 1)


class BulletBike(Amulet):
    Class, race, name = "Neutral", "", "Bullet Bike"
    mana = 2
    index = "SV_Rivayle~Neutral~Amulet~2~None~Bullet Bike~Uncollectible"
    requireTarget, description = False, "During your turn, when an allied follower comes into play, give it +1/+1 and banish this amulet."
    name_CN = "机动二轮车"

    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.trigsBoard = [Trig_BulletBike(self)]


class Trig_BulletBike(TrigBoard):
    def __init__(self, entity):
        self.blank_init(entity, ["MinionSummoned"])

    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
        return subject.Game.turn == self.entity.ID == subject.ID and self.entity.onBoard

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        self.entity.Game.banishMinion(self.entity, self.entity)
        subject.buffDebuff(2, 0)
        subject.getsKeyword("Rush")


class ArcanePersonnelCarrier(Amulet):
    Class, race, name = "Neutral", "", "Arcane Personnel Carrier"
    mana = 3
    index = "SV_Rivayle~Neutral~Amulet~3~None~Arcane Personnel Carrier~Uncollectible"
    requireTarget, description = False, "During your turn, when an allied follower comes into play, give it +1/+1 and banish this amulet."
    name_CN = "魔导装甲车"

    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.trigsBoard = [Trig_ArcanePersonnelCarrier(self)]


class Trig_ArcanePersonnelCarrier(TrigBoard):
    def __init__(self, entity):
        self.blank_init(entity, ["MinionSummoned"])

    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
        return subject.Game.turn == self.entity.ID == subject.ID and self.entity.onBoard

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        self.entity.Game.banishMinion(self.entity, self.entity)
        subject.buffDebuff(1, 3)
        subject.getsKeyword("Taunt")


class RivaylianBandit(SVMinion):
    Class, race, name = "Neutral", "", "Rivaylian Bandit"
    mana, attack, health = 1, 1, 1
    index = "SV_Rivayle~Neutral~Minion~1~1~1~None~Rivaylian Bandit~Enhance~Battlecry"
    requireTarget, keyWord, description = False, "", "Fanfare: Enhance (8) - Summon 2 Rivaylian Bandits. Then give +1/+1 to all allied Rivaylian Bandits. Once on each of your turns, when this follower's attack or defense is increased by an effect, gain +1/+2 and Rush."
    attackAdd, healthAdd = 2, 2
    name_CN = "勒比卢的恶徒"

    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.trigsBoard = [Trig_RivaylianBandit(self)]

    def getMana(self):
        if self.Game.Manas.manas[self.ID] >= 8:
            return 8
        else:
            return self.mana

    def willEnhance(self):
        return self.Game.Manas.manas[self.ID] >= 8

    def effCanTrig(self):
        self.effectViable = self.willEnhance()

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if comment == 8:
            self.Game.summon([RivaylianBandit(self.Game, self.ID), RivaylianBandit(self.Game, self.ID)],
                             (-1, "totheRightEnd"), self.ID)
            for minion in self.Game.minionsonBoard(self.ID, self):
                if minion.name == "Rivaylian Bandit":
                    minion.buffDebuff(1, 1)
            return target


class Trig_RivaylianBandit(TrigBoard):
    def __init__(self, entity):
        self.blank_init(entity, ["MinionBuffed"])

    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
        return subject.Game.turn == self.entity.ID and subject == self.entity and self.entity.onBoard

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        for t in self.entity.trigsBoard:
            if type(t) == Trig_RivaylianBandit:
                t.disconnect()
                self.entity.trigsBoard.remove(t)
                break
        trigger = Trig_EndRivaylianBandit(self.entity)
        self.entity.trigsBoard.append(trigger)
        trigger.connect()
        self.entity.buffDebuff(1, 2)
        self.entity.getsKeyword("Rush")


class Trig_EndRivaylianBandit(TrigBoard):
    def __init__(self, entity):
        self.blank_init(entity, ["TurnEnds"])

    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.onBoard and ID == self.entity.ID

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        for t in self.entity.trigsBoard:
            if type(t) == Trig_EndRivaylianBandit:
                t.disconnect()
                self.entity.trigsBoard.remove(t)
                break
        trigger = Trig_RivaylianBandit(self.entity)
        self.entity.trigsBoard.append(trigger)
        trigger.connect()


class QuixoticAdventurer(SVMinion):
    Class, race, name = "Neutral", "", "Quixotic Adventurer"
    mana, attack, health = 2, 2, 2
    index = "SV_Rivayle~Neutral~Minion~2~2~2~None~Quixotic Adventurer~Battlecry"
    requireTarget, keyWord, description = False, "", "Fanfare: Summon a Dutiful Steed. If it is your fifth turn or later, summon a Bullet Bike instead."
    attackAdd, healthAdd = 2, 2
    name_CN = "自由的冒险者"

    def effCanTrig(self):
        self.effectViable = self.Game.Counters.turns[self.ID] >= 5

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if self.Game.Counters.turns[self.ID] >= 5:
            self.Game.summon([BulletBike(self.Game, self.ID)], (-1, "totheRightEnd"),
                             self.ID)
        else:
            self.Game.summon([DutifulSteed(self.Game, self.ID)], (-1, "totheRightEnd"),
                             self.ID)
        return None


class WanderingChef(SVMinion):
    Class, race, name = "Neutral", "", "Wandering Chef"
    mana, attack, health = 2, 2, 2
    index = "SV_Rivayle~Neutral~Minion~2~2~2~None~Wandering Chef"
    requireTarget, keyWord, description = False, "", "Once on each of your turns, when this follower's attack or defense is increased by an effect, deal 3 damage to a random enemy follower and restore 3 defense to your leader."
    attackAdd, healthAdd = 2, 2
    name_CN = "浪游厨人"

    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.trigsBoard = [Trig_WanderingChef(self)]

    def inHandEvolving(self, target=None):
        self.Game.summon([ArcanePersonnelCarrier(self.Game, self.ID)], (-1, "totheRightEnd"),
                         self.ID)


class Trig_WanderingChef(TrigBoard):
    def __init__(self, entity):
        self.blank_init(entity, ["MinionBuffed"])

    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
        return subject.Game.turn == self.entity.ID and subject == self.entity and self.entity.onBoard

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        for t in self.entity.trigsBoard:
            if type(t) == Trig_WanderingChef:
                t.disconnect()
                self.entity.trigsBoard.remove(t)
                break
        trigger = Trig_EndWanderingChef(self.entity)
        self.entity.trigsBoard.append(trigger)
        trigger.connect()
        curGame = self.entity.Game
        if curGame.mode == 0:
            if curGame.guides:
                i = curGame.guides.pop(0)
            else:
                minions = curGame.minionsAlive(3 - self.entity.ID)
                i = npchoice(minions).pos if minions else -1
                curGame.fixedGuides.append(i)
            if i > -1:
                self.entity.dealsDamage(curGame.minions[3 - self.entity.ID][i], 3)
        heal = 3 * (2 ** self.entity.countHealDouble())
        self.entity.restoresHealth(curGame.heroes[self.entity.ID], heal)


class Trig_EndWanderingChef(TrigBoard):
    def __init__(self, entity):
        self.blank_init(entity, ["TurnEnds"])

    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.onBoard and ID == self.entity.ID

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        for t in self.entity.trigsBoard:
            if type(t) == Trig_EndWanderingChef:
                t.disconnect()
                self.entity.trigsBoard.remove(t)
                break
        trigger = Trig_WanderingChef(self.entity)
        self.entity.trigsBoard.append(trigger)
        trigger.connect()


class Ramiel(SVMinion):
    Class, race, name = "Neutral", "", "Ramiel"
    mana, attack, health = 2, 2, 2
    index = "SV_Rivayle~Neutral~Minion~2~2~2~None~Ramiel~Taunt~Legendary"
    requireTarget, keyWord, description = False, "Taunt", "Ward. Reduce damage from effects to 0."
    attackAdd, healthAdd = 2, 2
    name_CN = "蕾米尔"

    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.marks["Enemy Effect Damage Immune"] = 1

    def inHandEvolving(self, target=None):
        trigger = Trig_Ramiel(self)
        self.trigsBoard.append(trigger)
        trigger.connect()


class Trig_Ramiel(TrigBoard):
    def __init__(self, entity):
        self.blank_init(entity, ["TurnEnds"])

    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.onBoard and ID == self.entity.ID

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        if self.entity.Game.getEvolutionPoint(self.entity.ID) > self.entity.Game.getEvolutionPoint(3 - self.entity.ID):
            self.entity.Game.Manas.gainEmptyManaCrystal(1, self.entity.ID)


"""Forestcraft cards"""

"""Swordcraft cards"""

"""Runecraft cards"""

"""Dragoncraft cards"""

"""Shadowcraft cards"""

"""Bloodcraft cards"""

"""Havencraft cards"""


class Set_Accelerate(SVSpell):
    Class, name = "Havencraft", "Set"
    requireTarget, mana = False, 1
    index = "SV_Rivayle~Havencraft~Spell~1~Set~Accelerate~Uncollectible"
    description = "Restore 3 defense to your leader."
    name_CN = "赛特"

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        heal = 3 * (2 ** self.countHealDouble())
        self.restoresHealth(self.Game.heroes[self.ID], heal)
        return None


class Set(SVMinion):
    Class, race, name = "Havencraft", "", "Set"
    mana, attack, health = 7, 2, 8
    index = "SV_Rivayle~Havencraft~Minion~7~2~8~None~Set~Bane~Taunt~Accelerate"
    requireTarget, keyWord, description = False, "Bane,Taunt", "Accelerate (1): Restore 3 defense to your leader.Bane.Ward.Can't be targeted by enemy effects.At the end of your turn, restore 3 defense to your leader."
    accelerateSpell = Set_Accelerate
    attackAdd, healthAdd = 2, 2
    name_CN = "赛特"

    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.trigsBoard = [Trig_Set(self)]
        self.marks["Enemy Effect Evasive"] = 1

    def getMana(self):
        if self.Game.Manas.manas[self.ID] < self.mana:
            return 1
        else:
            return self.mana

    def willAccelerate(self):
        curMana = self.Game.Manas.manas[self.ID]
        return self.mana > curMana >= 1

    def effCanTrig(self):
        if self.willAccelerate() and self.targetExists():
            self.effectViable = "sky blue"
        else:
            self.effectViable = False

    def available(self):
        if self.willAccelerate():
            return True
        return True


class Trig_Set(TrigBoard):
    def __init__(self, entity):
        self.blank_init(entity, ["TurnEnds"])

    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.onBoard and ID == self.entity.ID

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        heal = 3 * (2 ** self.entity.countHealDouble())
        self.entity.restoresHealth(self.entity.Game.heroes[self.entity.ID], heal)


class AnveltJudgmentsCannon_Crystallize(Amulet):
    Class, race, name = "Havencraft", "", "Crystallize: Anvelt, Judgment's Cannon"
    mana = 1
    index = "SV_Rivayle~Havencraft~Amulet~1~None~Anvelt, Judgment's Cannon~Countdown~Crystallize~Deathrattle~Legendary~Uncollectible"
    requireTarget, description = False, "Countdown (10) At the end of your turn, subtract X from this amulet's Countdown. X equals the number of allied followers with Ward in play. Last Words: Summon an Anvelt, Judgment's Cannon."
    name_CN = "结晶：双炮神罚·安维特"

    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.counter = 10
        self.trigsBoard = [Trig_Countdown(self), Trig_AnveltJudgmentsCannon(self)]
        self.deathrattles = [Deathrattle_AnveltJudgmentsCannon_Crystallize(self)]


class Trig_AnveltJudgmentsCannon(TrigBoard):
    def __init__(self, entity):
        self.blank_init(entity, ["TurnEnds"])

    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.onBoard and ID == self.entity.ID

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        taunts = 0
        minions = self.entity.Game.minionsonBoard(self.entity.ID)
        for minion in minions:
            if minion.keyWords["Taunt"] > 0:
                taunts += 1
        self.entity.countdown(self.entity, taunts)


class Deathrattle_AnveltJudgmentsCannon_Crystallize(Deathrattle_Minion):
    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        self.entity.Game.summon([AnveltJudgmentsCannon(self.entity.Game, self.entity.ID)], (-1, "totheRightEnd"),
                                self.entity.ID)


class AnveltJudgmentsCannon(SVMinion):
    Class, race, name = "Havencraft", "", "Anvelt, Judgment's Cannon"
    mana, attack, health = 7, 5, 6
    index = "SV_Rivayle~Havencraft~Minion~7~5~6~None~Anvelt, Judgment's Cannon~Taunt~Crystallize~Legendary"
    requireTarget, keyWord, description = False, "Taunt", "Crystallize (1): Countdown (10) At the end of your turn, subtract X from this amulet's Countdown. X equals the number of allied followers with Ward in play.Last Words: Summon an Anvelt, Judgment's Cannon.Ward.When this follower comes into play, deal 4 damage to all enemy followers and then 2 damage to the enemy leader."
    crystallizeAmulet = AnveltJudgmentsCannon_Crystallize
    attackAdd, healthAdd = 2, 2
    name_CN = "双炮神罚·安维特"

    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.appearResponse = [self.whenAppears]

    def whenAppears(self):
        targets = self.Game.minionsonBoard(3 - self.ID)
        self.dealsAOE(targets, [4 for minion in targets])
        self.dealsDamage(self.Game.heroes[3 - self.ID], 2)

    def getMana(self):
        if self.Game.Manas.manas[self.ID] < self.mana:
            return 1
        else:
            return self.mana

    def willCrystallize(self):
        curMana = self.Game.Manas.manas[self.ID]
        return self.mana > curMana >= 1

    def effCanTrig(self):
        if self.willCrystallize() and self.targetExists():
            self.effectViable = "sky blue"
        else:
            self.effectViable = False


"""Portalcraft cards"""

"""DLC cards"""


class GoblinKing(SVMinion):
    Class, race, name = "Neutral", "", "Goblin King"
    mana, attack, health = 4, 5, 5
    index = "SV_Rivayle~Neutral~Minion~4~5~5~None~Goblin King~Taunt~Uncollectible"
    requireTarget, keyWord, description = False, "Taunt", "Ward."
    attackAdd, healthAdd = 2, 2
    name_CN = "哥布林王"


class GoblinQueen(SVMinion):
    Class, race, name = "Neutral", "", "Goblin Queen"
    mana, attack, health = 3, 3, 3
    index = "SV_Rivayle~Neutral~Minion~3~3~3~None~Goblin Queen~Battlecry"
    requireTarget, keyWord, description = False, "", "Fanfare: Put 2 Goblins into your hand."
    attackAdd, healthAdd = 2, 2
    evolveRequireTarget = True
    name_CN = "哥布林女王"

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        self.Game.Hand_Deck.addCardtoHand([Goblin for i in range(2)], self.ID, "type")

    def evolveTargetExists(self, choice=0):
        return any(minion.name == "Goblin" for minion in self.Game.minionsonBoard(self.ID, self))

    def evolveTargetCorrect(self, target, choice=0):
        if isinstance(target, list): target = target[0]
        return target.type == "Minion" and target.onBoard and target.ID == self.ID and target.name == "Goblin"

    def inHandEvolving(self, target=None):
        if target:
            if isinstance(target, list): target = target[0]
            if target and target.onBoard:
                newMinion = GoblinKing(self.Game, target.ID)
                self.Game.transform(target, newMinion)


SV_Rivayle_Indices = {
    "SV_Rivayle~Neutral~Amulet~1~None~Dutiful Steed~Uncollectible": DutifulSteed,
    "SV_Rivayle~Neutral~Amulet~2~None~Bullet Bike~Uncollectible": BulletBike,
    "SV_Rivayle~Neutral~Amulet~3~None~Arcane Personnel Carrier~Uncollectible": ArcanePersonnelCarrier,
    "SV_Rivayle~Neutral~Minion~1~1~1~None~Rivaylian Bandit~Enhance~Battlecry": RivaylianBandit,
    "SV_Rivayle~Neutral~Minion~2~2~2~None~Quixotic Adventurer~Battlecry": QuixoticAdventurer,
    "SV_Rivayle~Neutral~Minion~2~2~2~None~Wandering Chef": WanderingChef,
    "SV_Rivayle~Neutral~Minion~2~2~2~None~Ramiel~Taunt~Legendary": Ramiel,
    "SV_Rivayle~Havencraft~Spell~1~Set~Accelerate~Uncollectible": Set_Accelerate,
    "SV_Rivayle~Havencraft~Minion~7~2~8~None~Set~Bane~Taunt~Accelerate": Set,
    "SV_Rivayle~Havencraft~Amulet~1~None~Anvelt, Judgment's Cannon~Countdown~Crystallize~Deathrattle~Legendary~Uncollectible": AnveltJudgmentsCannon_Crystallize,
    "SV_Rivayle~Havencraft~Minion~7~5~6~None~Anvelt, Judgment's Cannon~Taunt~Crystallize~Legendary": AnveltJudgmentsCannon,
    "SV_Rivayle~Neutral~Minion~4~5~5~None~Goblin King~Taunt~Uncollectible": GoblinKing,
    "SV_Rivayle~Neutral~Minion~3~3~3~None~Goblin Queen~Battlecry": GoblinQueen
}
