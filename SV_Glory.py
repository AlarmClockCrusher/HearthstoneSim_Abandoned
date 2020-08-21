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


def fixedList(listObject):
    return listObject[0:len(listObject)]


def PRINT(game, string, *args):
    if game.GUI:
        if not game.mode: game.GUI.printInfo(string)
    elif not game.mode:
        print("game's guide mode is 0\n", string)


"""Mana 1 cards"""


class AirboundBarrage(SVSpell):
    Class, name = "Forestcraft", "Airbound Barrage"
    requireTarget, mana = True, 1
    index = "SV_Glory~Forestcraft~Spell~1~Airbound Barrage"
    description = "Return an allied follower or amulet to your hand. Then deal 3 damage to an enemy follower.(Can be played only when both a targetable allied card and enemy card are in play.)"

    def returnTrue(self, choice=0):
        return len(self.targets) < 2

    def available(self):
        return (
                       self.selectableFriendlyMinionExists() or self.selectableFriendlyAmuletExists()) and self.selectableEnemyMinionExists(
            choice=1)

    def targetCorrect(self, target, choice=0):
        if isinstance(target, list):
            allied, enemy = target[0], target[1]
            return (
                           allied.type == "Minion" or allied.type == "Amulet") and allied.onBoard and allied.ID == self.ID and enemy.type == "Minion" and enemy.ID != self.ID and enemy.onBoard
        else:
            if self.targets or choice:  # When checking the 2nd target
                return target.type == "Minion" and target.ID != self.ID and target.onBoard
            else:  # When checking the 1st target
                print("Checking target", target.name,
                      (target.type == "Minion" or target.type == "Amulet") and target.ID == self.ID and target.onBoard)
                return (target.type == "Minion" or target.type == "Amulet") and target.ID == self.ID and target.onBoard

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if target:
            allied, enemy = target[0], target[1]
            self.Game.returnMiniontoHand(allied, deathrattlesStayArmed=False)
            damage = (3 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
            PRINT(self.Game, "Airbound Barrage deals %d damage to enemy %s." % (damage, enemy.name))
            self.dealsDamage(enemy, damage)
        return target


class SacredPlea(Amulet):
    Class, race, name = "Havencraft", "", "Sacred Plea"
    mana = 1
    index = "SV_Glory~Havencraft~1~Amulet~None~Sacred Plea~Last Words"
    requireTarget, description = False, "Countdown 3. Last Words: Draw 2 cards"

    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.trigsBoard = [Trig_SacredPlea(self)]
        self.deathrattles = [Draw2Cards(self)]


class Trig_SacredPlea(TrigBoard):
    def __init__(self, entity):
        self.blank_init(entity, ["TurnStarts"])
        self.counter = 3

    def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.onBoard and ID == self.entity.ID

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        PRINT(self.entity.Game, "At the start of turn, Sacred Plea's countdown -1")
        self.counter -= 1
        if self.counter < 1:
            PRINT(self.entity.Game, "Sacred Plea's countdown is 0 and destroys itself")
            self.entity.Game.killMinion(None, self.entity)


class Draw2Cards(Deathrattle_Minion):
    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        PRINT(self.entity.Game, "Deathrattle: Draw 2 cards triggers.")
        self.entity.Game.Hand_Deck.drawCard(self.entity.ID)
        self.entity.Game.Hand_Deck.drawCard(self.entity.ID)


class SellswordLucius(SVMinion):
    Class, race, name = "Swordcraft", "", "Sellsword Lucius"
    mana, attack, health = 1, 1, 1
    index = "SV_Glory~Swordcraft~1~1~1~Minion~None~Sellsword Lucius~Enhance~Fanfare"
    requireTarget, keyWord, description = True, "", "Fanfare: Enhance 5. Destroy an enemy follower"

    def getMana(self):
        return max(5, self.mana) if self.Game.Manas.manas[self.ID] >= 5 else self.mana

    def willEnhance(self):
        return self.Game.Manas.manas[self.ID] >= 5

    def effectCanTrigger(self):
        self.effectViable = self.willEnhance()

    def returnTrue(self, choice=0):  # 只有在还没有选择过目标的情况下才能继续选择
        return not self.targets and self.Game.Manas.manas[self.ID] >= 5

    def targetExists(self, choice=0):
        return self.selectableEnemyMinionExists()

    def targetCorrect(self, target, choice=0):
        if isinstance(target, list): target = target[0]
        return target.type == "Minion" and target.ID != self.ID and target.onBoard

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if target:
            PRINT(self.Game, "Sellsword Lucius's Enhanced Fanfare destroys enemy minion %s" % target[0].name)
            self.Game.killMinion(self, target[0])
        return target


"""Mana 4 cards"""


class VesperWitchhunter_Accelerate(SVSpell):
    Class, name = "Runecraft", "Vesper, Witchhunter"
    requireTarget, mana = True, 2
    index = "SV_Glory~Runecraft~Spell~2~Vesper, Witchhunter~Uncollectible"
    description = "Deal 1 damage to an enemy"

    def targetCorrect(self, target, choice=0):
        if isinstance(target, list): target = target[0]
        return (target.type == "Minion" or target.type == "Hero") and target.ID != self.ID and target.onBoard

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if target:
            damage = (1 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
            PRINT(self.Game, "Vesper, Witchhunter, as spell, deals %d damage to enemy %s." % (damage, target[0].name))
            self.dealsDamage(target[0], damage)
        return target


class VesperWitchhunter(SVMinion):
    Class, race, name = "Runecraft", "", "Vesper, Witchhunter"
    mana, attack, health = 4, 3, 3
    index = "SV_Glory~Runecraft~4~3~3~Minion~None~Vesper, Witchhunter~Accelerate~Fanfare"
    requireTarget, keyWord, description = True, "", "Accelerate 2: Deal 1 damage to an enemy. Fanfare: xxx. Deal 3 damage to an enemy minion, and deal 1 damage to the enemy hero"
    accelerateSpell = VesperWitchhunter_Accelerate

    def getMana(self):
        return min(2, self.mana) if self.Game.Manas.manas[self.ID] < self.mana else self.mana

    def willAccelerate(self):
        curMana = self.Game.Manas.manas[self.ID]
        return self.mana > curMana >= 2

    def effectCanTrigger(self):
        self.effectViable = "sea green" if self.willAccelerate() else False

    def returnTrue(self, choice=0):
        return not self.targets

    def available(self):
        return self.selectableEnemyExists()

    def targetExists(self, choice=0):
        return self.selectableEnemyMinionExists()

    def targetCorrect(self, target, choice=0):
        if isinstance(target, list): target = target[0]
        return (target.type == "Minion" or (self.willAccelerate() and target.type == "Hero")) \
               and target.ID != self.ID and target.onBoard

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if target:
            PRINT(self.Game,
                  "Vesper, Witchhunter's Fanfare deals 3 damage to enemy minion %s and 1 damage to the enemy hero." %
                  target[0].name)
            self.dealsDamage(target[0], 3)
            self.dealsDamage(self.Game.heroes[3 - self.ID], 1)
        return target


"""Mana 10 cards"""


class RuinwebSpider_Crystallize(Amulet):
    Class, race, name = "Bloodcraft", "", "Ruinweb Spider"
    mana = 2
    index = "SV_Glory~Bloodcraft~2~Amulet~None~Ruinweb Spider~Last Words"
    requireTarget, description = False, "Countdown 3. Last Words: Draw 2 cards"

    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.trigsBoard = [Trig_RuinwebSpider_Crystallize(self)]
        self.deathrattles = [SummonaRuinwebSpider(self)]


class Trig_RuinwebSpider_Crystallize(TrigBoard):
    def __init__(self, entity):
        self.blank_init(entity, ["TurnStarts", "AmuletAppears"])
        self.counter = 10

    def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
        if signal == "TurnStarts":
            return self.entity.onBoard and ID == self.entity.ID
        else:
            return self.entity.onBoard and subject != self.entity and subject.ID == self.entity.ID == self.entity.Game.turn  # TurnStarts and AmuletAppears both send the correct ID

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        if signal == "TurnStarts":
            PRINT(self.entity.Game, "At the start of turn, Ruinweb Spider's countdown -1")
        else:
            PRINT(self.entity.Game,
                  "When another Amulet enters player's board during player's turn, Ruinweb Spider's countdown -1")
        self.counter -= 1
        if self.counter < 1:
            PRINT(self.entity.Game, "Ruinweb Spider's countdown is 0 and destroys itself")
            self.entity.Game.killMinion(None, self.entity)


class SummonaRuinwebSpider(Deathrattle_Minion):
    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        PRINT(self.entity.Game, "Deathrattle: Summon a Ruinweb Spider triggers.")
        self.entity.Game.summon(RuinwebSpider(self.entity.Game, self.entity.ID), self.entity.position + 1,
                                self.entity.ID)


class RuinwebSpider(SVMinion):
    Class, race, name = "Bloodcraft", "", "Ruinweb Spider"
    mana, attack, health = 10, 5, 10
    index = "SV_Glory~Bloodcraft~Minion~10~5~10~None~Ruinweb Spider~Crystallize"
    requireTarget, keyWord, description = False, "", "Crystallize 2; Countdown 10 During you turn, whenever an Amulet enters your board, reduce this Amulets countdown by 1. Last Words: Summon a Ruinweb Spider"
    crystallizeAmulet = RuinwebSpider_Crystallize
    attackAdd, healthAdd = 2, 2

    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.trigsBoard = [Trig_RuinwebSpider(self)]
        self.appearResponse = [self.enemyMinionsCantAttackThisTurn]

    def getMana(self):
        return min(2, self.mana) if self.Game.Manas.manas[self.ID] < self.mana else self.mana

    def willCrystallize(self):
        curMana = self.Game.Manas.manas[self.ID]
        return self.mana > curMana >= 2

    def effectCanTrigger(self):
        self.effectViable = "sea green" if self.willCrystallize() else False

    def enemyMinionsCantAttackThisTurn(self):
        PRINT(self.Game, "Ruinweb Spider appears and enemy minions can't attack until the end of opponent's turn")
        for minion in self.Game.minionsonBoard(3 - self.ID):
            minion.marks["Can't Attack"] += 1
            trig = Trig_CantAttack4aTurn(minion)
            trig.connect()
            minion.trigsBoard.append(trig)


class Trig_RuinwebSpider(TrigBoard):
    def __init__(self, entity):
        self.blank_init(entity, ["MinionBeenPlayed"])

    def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.onBoard and subject.ID != self.entity.ID

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        PRINT(self.entity.Game,
              "After opponent plays minion %s, Ruinweb Spider prevents it from attacking until the end of opponent's turn" % subject.name)
        trig = Trig_CantAttack4aTurn(subject)
        trig.connect()
        subject.trigsBoard.append(trig)


class Trig_CantAttack4aTurn(TrigBoard):
    def __init__(self, entity):
        self.blank_init(entity, ["TurnEnds"])
        self.temp = True

    def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.onBoard and ID == self.entity.ID

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        PRINT(self.entity.Game, "At the end of turn, minion %s can attack again." % self.entity.name)
        self.entity.marks["Can't Attack"] -= 1
        self.disconnect()
        try:
            self.entity.trigsBoard.remove(self)
        except:
            pass


class XIErntzJustice(SVMinion):
    Class, race, name = "Bloodcraft", "Dragon", "XI. Erntz, Justice"
    mana, attack, health = 10, 11, 8
    index = "SV_Glory~Bloodcraft~Minion~10~11~8~Dragon~XI. Erntz, Justice~Ward"
    requireTarget, keyWord, description = False, "Taunt", ""
    attackAdd, healthAdd = 2, 2

    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.appearResponse = [self.draw3Cards]
        self.disappearResponse = [self.restore8HealthtoPlayer]

    def draw3Cards(self):
        PRINT(self.Game, "XI. Erntz, Justice appears and lets player draw 3 cards")
        for num in range(3):
            self.Game.Hand_Deck.drawCard(self.ID)

    def restore8HealthtoPlayer(self):
        heal = 8 * (2 ** self.countHealDouble())
        PRINT(self.Game, "XI. Erntz, Justice leaves board and restores %d health to player" % heal)
        self.restoresHealth(self.Game.heroes[self.ID], heal)


"""Neutral cards"""

"""Forestcraft cards"""

"""Swordcraft cards"""

"""Runecraft cards"""

"""Dragoncraft cards"""

"""Shadowcraft cards"""

"""Bloodcraft cards"""

"""Havencraft cards"""

"""Portalcraft cards"""

"""DLC cards"""

SV_Glory_Indices = {
    "SV_Glory~Runecraft~4~3~3~Minion~None~Vesper, Witchhunter~Accelerate~Fanfare": VesperWitchhunter,
    "SV_Glory~Runecraft~Spell~2~Vesper, Witchhunter~Uncollectible": VesperWitchhunter_Accelerate,
    "SV_Glory~Havencraft~1~Amulet~None~Sacred Plea~Last Words": SacredPlea,
    "SV_Glory~Bloodcraft~Minion~10~5~10~None~Ruinweb Spider~Crystallize": RuinwebSpider,
    "SV_Glory~Bloodcraft~2~Amulet~None~Ruinweb Spider~Last Words": RuinwebSpider_Crystallize,
    "SV_Glory~Bloodcraft~Minion~10~11~8~Dragon~XI. Erntz, Justice~Ward": XIErntzJustice,
    "SV_Glory~Forestcraft~Spell~1~Airbound Barrage": AirboundBarrage,
}