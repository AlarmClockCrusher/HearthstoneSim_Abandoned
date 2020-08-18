from CardTypes import *
from Triggers_Auras import *

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


SVClasses = ["Forestcraft", "Swordcraft", "Runecraft", "Drangoncraft", "Shadowcraft", "Bloodcraft", "Havencraft",
             "Portalcraft"]
Classes = ["Demon Hunter", "Druid", "Hunter", "Mage", "Monk", "Paladin", "Priest", "Rogue", "Shaman", "Warlock",
           "Warrior",
           "Forestcraft", "Swordcraft", "Runecraft", "Drangoncraft", "Shadowcraft", "Bloodcraft", "Havencraft",
           "Portalcraft"]
ClassesandNeutral = ["Demon Hunter", "Druid", "Hunter", "Mage", "Monk", "Paladin", "Priest", "Rogue", "Shaman",
                     "Warlock", "Warrior", "Neutral", "Forestcraft", "Swordcraft", "Runecraft", "Drangoncraft",
                     "Shadowcraft", "Bloodcraft", "Havencraft", "Portalcraft"]


# SV_Basic cards and heroes

class ShadowverseMinion(Minion):
    attackAdd, healthAdd = 2, 2

    def blank_init(self, Game, ID):
        super().blank_init(Game, ID)
        self.targets = []

    def evolve(self):
        if self.status["Evolved"] < 1:
            self.attack_0 += self.attackAdd
            self.health_0 += self.healthAdd
            self.statReset(self.attack + self.attackAdd, self.health + self.healthAdd)
            self.status["Evolved"] += 1
            PRINT(self.Game, self.name + " evolves.")
            self.Game.Counters.evolvedThisGame[self.ID] += 1
            for card in self.Game.Hand_Deck.hands[self.ID]:
                if isinstance(card, ShadowverseMinion) and "UB" in card.marks:
                    card.marks["UB"] -= 1
            self.inEvolving()

    def inEvolving(self):
        return

    def inHandEvolving(self, target=None):
        return

    def findTargets(self, comment="", choice=0):
        game, targets, indices, wheres = self.Game, [], [], []
        for ID in range(1, 3):
            if self.targetCorrect(game.heroes[ID], choice) and (comment == "" or self.canSelect(game.heroes[ID])):
                targets.append(game.heroes[ID])
                indices.append(ID)
                wheres.append("hero")
            where = "minion%d" % ID
            for obj in game.minionsandAmuletsonBoard(ID):
                if self.targetCorrect(obj, choice) and (comment == "" or self.canSelect(obj)):
                    targets.append(obj)
                    indices.append(obj.position)
                    wheres.append(where)
            where = "hand%d" % ID
            for i, card in enumerate(game.Hand_Deck.hands[ID]):
                if self.targetCorrect(card, choice):
                    targets.append(card)
                    indices.append(i)
                    wheres.append(where)

        if targets:
            return targets, indices, wheres
        else:
            return [None], [0], ['']

    def actionable(self):
        return self.ID == self.Game.turn and \
               (not self.newonthisSide or (
                       self.status["Borrowed"] > 0 or self.keyWords["Charge"] > 0 or self.keyWords["Rush"] > 0 or
                       self.status["Evolved"] > 0))

    def canAttack(self):
        return self.actionable() and self.status["Frozen"] < 1 \
               and self.attChances_base + self.attChances_extra > self.attTimes \
               and self.marks["Can't Attack"] < 1

    def createCopy(self, game):
        if self in game.copiedObjs:
            return game.copiedObjs[self]
        else:
            Copy = type(self)(game, self.ID)
            game.copiedObjs[self] = Copy
            Copy.mana = self.mana
            Copy.manaMods = [mod.selfCopy(Copy) for mod in self.manaMods]
            Copy.attack, Copy.attack_0, Copy.attack_Enchant = self.attack, self.attack_0, self.attack_Enchant
            Copy.health_0, Copy.health, Copy.health_max = self.health_0, self.health, self.health_max
            Copy.tempAttChanges = copy.deepcopy(self.tempAttChanges)
            Copy.statbyAura = [self.statbyAura[0], self.statbyAura[1],
                               [aura_Receiver.selfCopy(Copy) for aura_Receiver in self.statbyAura[2]]]
            for key, value in self.keyWordbyAura.items():
                if key != "Auras":
                    Copy.keyWordbyAura[key] = value
                else:
                    Copy.keyWordbyAura[key] = [aura_Receiver.selfCopy(Copy) for aura_Receiver in
                                               self.keyWordbyAura["Auras"]]
            Copy.keyWords = copy.deepcopy(self.keyWords)
            Copy.marks = copy.deepcopy(self.marks)
            Copy.status = copy.deepcopy(self.status)
            Copy.identity = copy.deepcopy(self.identity)
            Copy.onBoard, Copy.inHand, Copy.inDeck, Copy.dead = self.onBoard, self.inHand, self.inDeck, self.dead
            if hasattr(self, "progress"): Copy.progress = self.progress
            Copy.effectViable, Copy.evanescent, Copy.activated, Copy.silenced = self.effectViable, self.evanescent, self.activated, self.silenced
            Copy.newonthisSide, Copy.firstTimeonBoard = self.newonthisSide, self.firstTimeonBoard
            Copy.sequence, Copy.position = self.sequence, self.position
            Copy.attTimes, Copy.attChances_base, Copy.attChances_extra = self.attTimes, self.attChances_base, self.attChances_extra
            Copy.options = [option.selfCopy(Copy) for option in self.options]
            for key, value in self.triggers.items():
                Copy.triggers[key] = [getattr(Copy, func.__qualname__.split(".")[1]) for func in value]
            Copy.appearResponse = [getattr(Copy, func.__qualname__.split(".")[1]) for func in self.appearResponse]
            Copy.disappearResponse = [getattr(Copy, func.__qualname__.split(".")[1]) for func in self.disappearResponse]
            Copy.silenceResponse = [getattr(Copy, func.__qualname__.split(".")[1]) for func in self.silenceResponse]
            for key, value in self.auras.items():
                Copy.auras[key] = value.createCopy(game)
            Copy.deathrattles = [trig.createCopy(game) for trig in self.deathrattles]
            Copy.trigsBoard = [trig.createCopy(game) for trig in self.trigsBoard]
            Copy.trigsHand = [trig.createCopy(game) for trig in self.trigsHand]
            Copy.trigsDeck = [trig.createCopy(game) for trig in self.trigsDeck]
            Copy.history = copy.deepcopy(self.history)
            Copy.attackAdd = self.attackAdd
            Copy.healthAdd = self.healthAdd
            self.assistCreateCopy(Copy)
            return Copy


class AccelerateMinion(ShadowverseMinion):
    accelerate, accelerateSpell = 0, None

    def getMana(self):
        return min(self.accelerate, self.mana) if self.Game.Manas.manas[self.ID] < self.mana else self.mana

    def getTypewhenPlayed(self):
        return "Spell" if self.willAccelerate() else "Minion"

    def willAccelerate(self):
        curMana = self.Game.Manas.manas[self.ID]
        return curMana < self.mana and curMana >= type(self).accelerate

    def becomeswhenPlayed(self):
        return type(self).accelerateSpell(self.Game, self.ID) if self.willAccelerate() else self, self.getMana()


class CrystallizeMinion(ShadowverseMinion):
    crystallize, crystallizeAmulet = 0, None

    def getMana(self):
        return min(self.crystallize, self.mana) if self.Game.Manas.manas[self.ID] < self.mana else self.mana

    def getTypewhenPlayed(self):
        return "Amulet" if self.willCrystallize() else "Minion"

    def willCrystallize(self):
        curMana = self.Game.Manas.manas[self.ID]
        return curMana < self.mana and curMana >= type(self).crystallize

    def becomeswhenPlayed(self):
        return type(self).crystallizeAmulet(self.Game, self.ID) if self.willCrystallize() else self, self.getMana()


class ShadowverseSpell(Spell):
    def __init__(self, Game, ID):
        super().__init__(Game, ID)
        self.targets = []

    def played(self, target=None, choice=0, mana=0, posinHand=-2, comment=""):
        repeatTimes = 2 if self.Game.status[self.ID]["Spells x2"] > 0 else 1
        if self.Game.GUI:
            self.Game.GUI.showOffBoardTrig(self)
            self.Game.GUI.wait(500)
        self.Game.sendSignal("SpellPlayed", self.ID, self, None, mana, "", choice)
        # 假设SV的法术在选取上不触发重导向扳机
        self.Game.gathertheDead()
        self.Game.Counters.spellsonFriendliesThisGame[self.ID] += [self.index for obj in target if obj.ID == self.ID]
        # 假设SV的法术不受到"对相邻的法术也释放该法术"的影响
        for i in range(repeatTimes):
            for obj in target:  # 每个目标都会检测是否记录该法术的作用历史
                if (obj.type == "Minion" or obj.type == "Amulet") and obj.onBoard:
                    obj.history["Spells Cast on This"].append(self.index)
            target = self.whenEffective(target, comment, choice, posinHand)

        # 仅触发风潮，星界密使等的光环移除扳机。“使用一张xx牌之后”的扳机不在这里触发，而是在Game的playSpell函数中结算。
        self.Game.sendSignal("SpellBeenCast", self.Game.turn, self, None, 0, "", choice)
        self.Game.gathertheDead()  # At this point, the minion might be removed/controlled by Illidan/Juggler combo.
        if self.Game.GUI: self.Game.GUI.eraseOffBoardTrig(self.ID)


class ShadowverseAmulet(Dormant):
    Class, race, name = "Neutral", "", "Vanilla"
    mana = 2
    index = "Vanilla~Neutral~2~Amulet~None~Vanilla~Uncollectible"
    requireTarget, description = False, ""

    def blank_init(self, Game, ID):
        self.Game, self.ID = Game, ID
        self.Class, self.name = type(self).Class, type(self).name
        self.type, self.race = "Amulet", type(self).race
        # 卡牌的费用和对于费用修改的效果列表在此处定义
        self.mana, self.manaMods = type(self).mana, []
        self.tempAttChanges = []  # list of tempAttChange, expiration timepoint
        self.description = type(self).description
        # 当一个实例被创建的时候，其needTarget被强行更改为returnTrue或者是returnFalse，不论定义中如何修改needTarget(self, choice=0)这个函数，都会被绕过。需要直接对returnTrue()函数进行修改。
        self.needTarget = self.returnTrue if type(self).requireTarget else self.returnFalse
        # Some state of the minion represented by the marks
        # 复制出一个游戏内的Copy时要重新设为初始值的attr
        # First two are for card authenticity verification. The last is to check if the minion has ever left board.
        # Princess Talanji needs to confirm if a card started in original deck.
        self.identity = [np.random.rand(), np.random.rand(), np.random.rand()]
        self.dead = False
        self.effectViable, self.evanescent = False, False
        self.newonthisSide, self.firstTimeonBoard = True, True  # firstTimeonBoard用于防止随从在休眠状态苏醒时再次休眠，一般用不上
        self.onBoard, self.inHand, self.inDeck = False, False, False
        self.activated = False  # This mark is for minion state change, such as enrage.
        # self.sequence records the number of the minion's appearance. The first minion on board has a sequence of 0
        self.sequence, self.position = -1, -2
        self.keyWords = {}
        self.marks = {"Evasive": 0, "Enemy Effect Evasive": 0, "Can't Break": 0}
        self.status = {}
        self.auras = {}
        self.options = []  # For Choose One minions.
        self.overload, self.chooseOne, self.magnetic = 0, 0, 0
        self.silenced = False

        self.triggers = {"Discarded": [], "StatChanges": [], "Drawn": []}
        self.appearResponse, self.disappearResponse, self.silenceResponse = [], [], []
        self.deathrattles = []  # 随从的亡语的触发方式与场上扳机一致，诸扳机之间与
        self.trigsBoard, self.trigsHand, self.trigsDeck = [], [], []
        self.history = {"Spells Cast on This": [],
                        "Magnetic Upgrades": {"Deathrattles": [], "Triggers": []
                                              }
                        }
        self.targets = []

    def applicable(self, target):
        return target != self

    """Handle the trigsBoard/inHand/inDeck of minions based on its move"""

    def appears(self):
        PRINT(self.Game, "%s appears on board." % self.name)
        self.newonthisSide = True
        self.onBoard, self.inHand, self.inDeck = True, False, False
        self.dead = False
        self.mana = type(self).mana  # Restore the minion's mana to original value.
        for value in self.auras.values():
            PRINT(self.Game, "Now starting amulet {}'s Aura {}".format(self.name, value))
            value.auraAppears()
        # 随从入场时将注册其场上扳机和亡语扳机
        for trig in self.trigsBoard + self.deathrattles:
            trig.connect()  # 把(obj, signal)放入Game.triggersonBoard中
        # Mainly mana aura minions, e.g. Sorcerer's Apprentice.
        for func in self.appearResponse: func()
        # The buffAuras/hasAuras will react to this signal.
        self.Game.sendSignal("AmuletAppears", self.ID, self, None, 0, "")
        for func in self.triggers["StatChanges"]: func()

    def disappears(self, deathrattlesStayArmed=True):  # The minion is about to leave board.
        self.onBoard, self.inHand, self.inDeck = False, False, False
        # Only the auras and disappearResponse will be invoked when the minion switches side.
        for value in self.auras.values():
            value.auraDisappears()
        # 随从离场时清除其携带的普通场上扳机，但是此时不考虑亡语扳机
        for trig in self.trigsBoard:
            trig.disconnect()
        if deathrattlesStayArmed == False:
            for trig in self.deathrattles:
                trig.disconnect()
        # 如果随从有离场时需要触发的函数，在此处理
        for func in self.disappearResponse: func()
        self.activated = False
        self.Game.sendSignal("AmuletDisappears", self.ID, None, self, 0, "")

    def STATUSPRINT(self):
        PRINT(self.Game, "Game is {}.".format(self.Game))
        PRINT(self.Game,
              "Amulet: %s. ID: %d Race: %s\nDescription: %s" % (self.name, self.ID, self.race, self.description))
        if self.manaMods != []:
            PRINT(self.Game, "\tCarries mana modification:")
            for manaMod in self.manaMods:
                if manaMod.changeby != 0:
                    PRINT(self.Game, "\t\tChanged by %d" % manaMod.changeby)
                else:
                    PRINT(self.Game, "\t\tChanged to %d" % manaMod.changeto)
        if self.trigsBoard != []:
            PRINT(self.Game, "\tAmulet's trigsBoard")
            for trigger in self.trigsBoard:
                PRINT(self.Game, "\t{}".format(type(trigger)))
        if self.trigsHand != []:
            PRINT(self.Game, "\tAmulet's trigsHand")
            for trigger in self.trigsHand:
                PRINT(self.Game, "\t{}".format(type(trigger)))
        if self.trigsDeck != []:
            PRINT(self.Game, "\tAmulet's trigsDeck")
            for trigger in self.trigsDeck:
                PRINT(self.Game, "\t{}".format(type(trigger)))
        if self.auras != {}:
            PRINT(self.Game, "Amulet's aura")
            for key, value in self.auras.items():
                PRINT(self.Game, "{}".format(value))
        if self.deathrattles != []:
            PRINT(self.Game, "\tMinion's Deathrattles:")
            for trigger in self.deathrattles:
                PRINT(self.Game, "\t{}".format(type(trigger)))

    def afterSwitchSide(self, activity):
        self.newonthisSide = True

    # Whether the minion can select the attack target or not.
    def canAttack(self):
        return False

    def canAttackTarget(self, target):
        return False

    def deathResolution(self, attackbeforeDeath, triggersAllowed_WhenDies, triggersAllowed_AfterDied):
        self.Game.sendSignal("AmuletDestroys", self.Game.turn, None, self, attackbeforeDeath, "", 0,
                             triggersAllowed_WhenDies)
        for trig in self.deathrattles:
            trig.disconnect()
        self.Game.sendSignal("AmuletDestroyed", self.Game.turn, None, self, 0, "", 0, triggersAllowed_AfterDied)

    # Minions that initiates discover or transforms self will be different.
    # For minion that transform before arriving on board, there's no need in setting its onBoard to be True.
    # By the time this triggers, death resolution caused by Illidan/Juggler has been finished.
    # If Brann Bronzebeard/ Mayor Noggenfogger has been killed at this point, they won't further affect the battlecry.
    # posinHand在played中主要用于记录一张牌是否是从手牌中最左边或者最右边打出（恶魔猎手职业关键字）
    def played(self, target=None, choice=0, mana=0, posinHand=-2, comment=""):
        self.appears()
        self.Game.sendSignal("AmuletPlayed", self.ID, self, target, mana, "", choice)
        self.Game.sendSignal("AmuletSummoned", self.ID, self, target, mana, "")
        self.Game.gathertheDead()  # At this point, the minion might be removed/controlled by Illidan/Juggler combo.
        # 假设不触发重导向扳机
        num = 1
        if "~Fanfare" in self.index and self.Game.status[self.ID]["Battlecry x2"] + self.Game.status[self.ID][
            "Shark Battlecry x2"] > 0:
            num = 2
        for i in range(num):
            target = self.whenEffective(target, "", choice, posinHand)

        # 结算阶段结束，处理死亡情况，不处理胜负问题。
        self.Game.gathertheDead()
        return target

    """buffAura effect, Buff/Debuff, stat reset, copy"""

    # 在原来的Game中创造一个Copy
    def selfCopy(self, ID, mana=False):
        Copy = self.hardCopy(ID)
        # 随从的光环和亡语复制完全由各自的selfCopy函数负责。
        Copy.activated, Copy.onBoard, Copy.inHand, Copy.inDeck = False, False, False, False
        size = len(Copy.manaMods)  # 去掉牌上的因光环产生的费用改变
        for i in range(size):
            if Copy.manaMods[size - 1 - i].source:
                Copy.manaMods.pop(size - 1 - i)
        # 在一个游戏中复制出新实体的时候需要把这些值重置
        Copy.identity = [np.random.rand(), np.random.rand(), np.random.rand()]
        Copy.dead = False
        Copy.effectViable, Copy.evanescent = False, False
        Copy.newonthisSide, Copy.firstTimeonBoard = True, True  # firstTimeonBoard用于防止随从在休眠状态苏醒时再次休眠，一般用不上
        Copy.onBoard, Copy.inHand, Copy.inDeck = False, False, False
        Copy.activated = False
        Copy.sequence, Copy.position = -1, -2
        Copy.attTimes, Copy.attChances_base, Copy.attChances_extra = 0, 0, 0
        return Copy

    def createCopy(self, game):
        if self in game.copiedObjs:
            return game.copiedObjs[self]
        else:
            Copy = type(self)(game, self.ID)
            game.copiedObjs[self] = Copy
            Copy.mana = self.mana
            Copy.manaMods = [mod.selfCopy(Copy) for mod in self.manaMods]
            Copy.marks = copy.deepcopy(self.marks)
            Copy.identity = copy.deepcopy(self.identity)
            Copy.onBoard, Copy.inHand, Copy.inDeck, Copy.dead = self.onBoard, self.inHand, self.inDeck, self.dead
            if hasattr(self, "progress"): Copy.progress = self.progress
            Copy.effectViable, Copy.evanescent, Copy.activated, Copy.silenced = self.effectViable, self.evanescent, self.activated, self.silenced
            Copy.newonthisSide, Copy.firstTimeonBoard = self.newonthisSide, self.firstTimeonBoard
            Copy.sequence, Copy.position = self.sequence, self.position
            Copy.options = [option.selfCopy(Copy) for option in self.options]
            for key, value in self.triggers.items():
                Copy.triggers[key] = [getattr(Copy, func.__qualname__.split(".")[1]) for func in value]
            Copy.appearResponse = [getattr(Copy, func.__qualname__.split(".")[1]) for func in self.appearResponse]
            Copy.disappearResponse = [getattr(Copy, func.__qualname__.split(".")[1]) for func in self.disappearResponse]
            Copy.silenceResponse = [getattr(Copy, func.__qualname__.split(".")[1]) for func in self.silenceResponse]
            for key, value in self.auras.items():
                Copy.auras[key] = value.createCopy(game)
            Copy.deathrattles = [trig.createCopy(game) for trig in self.deathrattles]
            Copy.trigsBoard = [trig.createCopy(game) for trig in self.trigsBoard]
            Copy.trigsHand = [trig.createCopy(game) for trig in self.trigsHand]
            Copy.trigsDeck = [trig.createCopy(game) for trig in self.trigsDeck]
            Copy.history = copy.deepcopy(self.history)
            self.assistCreateCopy(Copy)
            return Copy


class Evolve(HeroPower):
    mana, name, requireTarget = 0, "Evolve", True
    index = "SV_Basic~Hero Power~0~Evolve"
    description = "Evolve an unevolved friendly minion."

    def available(self):
        if self.selectableFriendlyMinionExists() and self.heroPowerTimes < self.heroPowerChances_base + \
                self.heroPowerChances_extra and \
                self.Game.Counters.turns[self.ID] >= \
                self.Game.Counters.numEvolutionTurn[self.ID]:
            if self.Game.Counters.numEvolutionPoint[self.ID] > 0:
                return True
            else:
                hasFree = False
                for minion in self.Game.minionsonBoard(self.ID):
                    if isinstance(minion, ShadowverseMinion) and minion.keyWords["Free Evolve"] > 0:
                        hasFree = True
                        break
                return hasFree
        return False

    def targetCorrect(self, target, choice=0):
        if target.type == "Minion" and target.ID == self.ID and target.onBoard \
                and isinstance(target, ShadowverseMinion) and target.status["Evolved"] < 1 \
                and target.marks["Can't Evolve"] == 0:
            if self.Game.Counters.numEvolutionPoint[self.ID] == 0:
                return target.marks["Free Evolve"] > 0
            else:
                return True
        return False

    def effect(self, target, choice=0):
        if target.marks["Free Evolve"] == 0:
            self.Game.Counters.numEvolutionPoint[self.ID] -= 1
        target.evolve()
        target.inHandEvolving()
        return 0


class Arisa(Hero):
    Class, name, heroPower = "Forestcraft", "Erika", Evolve

    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.health, self.health_max, self.armor = 20, 20, 0


class Erika(Hero):
    Class, name, heroPower = "Swordcraft", "Erika", Evolve

    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.health, self.health_max, self.armor = 20, 20, 0


class Isabelle(Hero):
    Class, name, heroPower = "Runecraft", "Erika", Evolve

    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.health, self.health_max, self.armor = 20, 20, 0


class Rowen(Hero):
    Class, name, heroPower = "Dragoncraft", "Erika", Evolve

    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.health, self.health_max, self.armor = 20, 20, 0


class Luna(Hero):
    Class, name, heroPower = "Shadowcraft", "Erika", Evolve

    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.health, self.health_max, self.armor = 20, 20, 0


class Urias(Hero):
    Class, name, heroPower = "Bloodcraft", "Erika", Evolve

    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.health, self.health_max, self.armor = 20, 20, 0


class Eris(Hero):
    Class, name, heroPower = "Havencraft", "Erika", Evolve

    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.health, self.health_max, self.armor = 20, 20, 0


class Yuwan(Hero):
    Class, name, heroPower = "Portalcraft", "Erika", Evolve

    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.health, self.health_max, self.armor = 20, 20, 0


class VesperWitchhunter_Accelerate(ShadowverseSpell):
    Class, name = "Runecraft", "Vesper, Witchhunter"
    requireTarget, mana = True, 2
    index = "SV_Basic~Runecraft~Spell~2~Vesper, Witchhunter~Uncollectible"
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


class VesperWitchhunter(AccelerateMinion):
    Class, race, name = "Runecraft", "", "Vesper, Witchhunter"
    mana, attack, health = 4, 3, 3
    index = "SV_Basic~Runecraft~4~3~3~Minion~None~Vesper, Witchhunter~Accelerate~Fanfare"
    requireTarget, keyWord, description = True, "", "Accelerate 2: Deal 1 damage to an enemy. Fanfare: xxx. Deal 3 damage to an enemy minion, and deal 1 damage to the enemy hero"
    accelerate, accelerateSpell = 2, VesperWitchhunter_Accelerate

    def effectCanTrigger(self):
        self.effectViable = self.willAccelerate()

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


class Terrorformer(ShadowverseMinion):
    Class, race, name = "Forestcraft", "", "Terrorformer"
    mana, attack, health = 6, 4, 4
    index = "SV_Basic~Forestcraft~Minion~6~4~4~None~Terrorformer~Fusion~Fanfare"
    requireTarget, keyWord, description = True, "", "Fusion: Forestcraft followers that originally cost 2 play points or more. Whenever 2 or more cards are fused to this card at once, gain +2/+0 and draw a card. Fanfare: If at least 2 cards are fused to this card, gain Storm. Then, if at least 4 cards are fused to this card, destroy an enemy follower."

    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.fusion = 1
        self.fusionMaterials = 0

    def returnTrue(self, choice=0):  # 需要targets里面没有目标，且有3个融合素材
        return not self.targets and self.fusionMaterials > 3

    def targetCorrect(self, target, choice=0):
        if isinstance(target, list): target = target[0]
        return target.type == "Minion" and target.ID != self.ID and target.onBoard

    def findFusionMaterials(self):
        return [card for card in self.Game.Hand_Deck.hands[self.ID] if
                card.type == "Minion" and card != self and type(card).mana > 1]

    def fusionDecided(self, objs):
        if objs:
            self.fusionMaterials += len(objs)
            self.Game.Hand_Deck.extractfromHand(self, enemyCanSee=True)
            for obj in objs: self.Game.Hand_Deck.extractfromHand(obj, enemyCanSee=True)
            self.Game.Hand_Deck.addCardtoHand(self, self.ID)
            if len(objs) > 1:
                PRINT(self.Game,
                      "Terrorformer's Fusion involves more than 1 minion. It gains +2/+0 and lets player draw a card")
                self.buffDebuff(2, 0)
                self.Game.Hand_Deck.drawCard(self.ID)
            self.fusion = 0  # 一张卡每回合只有一次融合机会

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        PRINT(self.Game, "Terrorformer's Fanfare gives minion Storm as it has no less than 2 fusion materials")
        self.getsKeyword("Charge")
        if target and self.fusionMaterials > 3:
            PRINT(self.Game, "Terrorformer's Fanfare destroys enemy follower" % target[0].name)
            target[0].dead = True
        return target


# 当费用不足以释放随从本体但又高于结晶费用X时，打出会以结晶方式打出，此时随从变形为一张护符打出在战场上，护符名为结晶：{随从名}，效果与随从本体无关。可能会具有本体不具有的额外种族。不会被本体减费影响，但若本体费用低于结晶费用则结晶无法触发。同一个随从可以同时具有结晶和爆能强化。


class SacredPlea(ShadowverseAmulet):
    Class, race, name = "Havencraft", "", "Sacred Plea"
    mana = 1
    index = "SV_Basic~Havencraft~1~Amulet~None~Sacred Plea~Last Words"
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
            self.entity.dead = True


class Draw2Cards(Deathrattle_Minion):
    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        PRINT(self.entity.Game, "Deathrattle: Draw 2 cards triggers.")
        self.entity.Game.Hand_Deck.drawCard(self.entity.ID)
        self.entity.Game.Hand_Deck.drawCard(self.entity.ID)


class AirboundBarrage(ShadowverseSpell):
    Class, name = "Forestcraft", "Airbound Barrage"
    requireTarget, mana = True, 1
    index = "SV_Basic~Forestcraft~Spell~1~Airbound Barrage"
    description = "Return an allied follower or amulet to your hand. Then deal 3 damage to an enemy follower.(Can be played only when both a targetable allied card and enemy card are in play.)"

    def returnTrue(self, choice=0):
        return len(self.targets) < 2

    def available(self):
        return (
                       self.selectableFriendlyMinionExists() or self.selectableFriendlyAmuletExists()) and self.selectableEnemyMinionExists()

    def targetCorrect(self, target, choice=0):
        if isinstance(target, list):
            allied, enemy = target[0], target[1]
            return (
                           allied.type == "Minion" or allied.type == "Amulet") and allied.onBoard and allied.ID == self.ID and enemy.type == "Minion" and enemy.ID != self.ID and enemy.onBoard
        else:
            if self.targets:  # When checking the 2nd target
                return target.type == "Minion" and target.ID != self.ID and target.onBoard
            else:  # When checking the 1st target
                return (target.type == "Minion" or target.type == "Amulet") and target.ID == self.ID and target.onBoard

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if target:
            allied, enemy = target[0], target[1]
            self.Game.returnMiniontoHand(allied, deathrattlesStayArmed=False)
            damage = (3 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
            PRINT(self.Game, "Airbound Barrage deals %d damage to enemy %s." % (damage, enemy.name))
            self.dealsDamage(enemy, damage)
        return target


class RuinwebSpider_Shadowverse_Amulet(ShadowverseAmulet):
    Class, race, name = "Bloodcraft", "", "Ruinweb Spider"
    mana = 2
    index = "SV_Basic~Bloodcraft~2~Amulet~None~Ruinweb Spider~Last Words"
    requireTarget, description = False, "Countdown 3. Last Words: Draw 2 cards"

    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.trigsBoard = [Trig_RuinwebSpider_Amulet(self)]
        self.deathrattles = [SummonaRuinwebSpider(self)]


class Trig_RuinwebSpider_Amulet(TrigBoard):
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
            PRINT(self.entity.Game, "Sacred Plea's countdown is 0 and destroys itself")
            self.entity.dead = True


class SummonaRuinwebSpider(Deathrattle_Minion):
    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        PRINT(self.entity.Game, "Deathrattle: Summon a Ruinweb Spider triggers.")
        self.entity.Game.summon(RuinwebSpider(self.entity.Game, self.entity.ID), self.entity.position + 1,
                                self.entity.ID)


class RuinwebSpider(CrystallizeMinion):
    Class, race, name = "Bloodcraft", "", "Ruinweb Spider"
    mana, attack, health = 10, 5, 10
    index = "SV_Basic~Bloodcraft~Minion~10~5~10~None~Ruinweb Spider~Crystallize"
    requireTarget, keyWord, description = False, "", "Crystallize 2; Countdown 10 During you turn, whenever an Amulet enters your board, reduce this Amulets countdown by 1. Last Words: Summon a Ruinweb Spider"
    crystallize, crystallizeAmulet = 2, RuinwebSpider_Shadowverse_Amulet
    attackAdd, healthAdd = 2, 2

    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.trigsBoard = [Trig_RuinwebSpider(self)]
        self.appearResponse = [self.enemyMinionsCantAttackThisTurn]

    def effectCanTrigger(self):
        self.effectViable = self.willCrystallize()

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


class XIErntzJustice(ShadowverseMinion):
    Class, race, name = "Bloodcraft", "Dragon", "XI. Erntz, Justice"
    mana, attack, health = 10, 11, 8
    index = "SV_Basic~Bloodcraft~Minion~10~11~8~Dragon~XI. Erntz, Justice~Ward"
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


class Goblin(ShadowverseMinion):
    Class, race, name = "Neutral", "", "Goblin"
    mana, attack, health = 1, 1, 2
    index = "SV_Basic~Neutral~Minion~1~1~2~None~Goblin"
    requireTarget, keyWord, description = False, "", ""
    attackAdd, healthAdd = 2, 2


class Fighter(ShadowverseMinion):
    Class, race, name = "Neutral", "", "Fighter"
    mana, attack, health = 2, 2, 2
    index = "SV_Basic~Neutral~Minion~2~2~2~None~Fighter"
    requireTarget, keyWord, description = False, "", ""
    attackAdd, healthAdd = 2, 2


class WellofDestiny(ShadowverseAmulet):
    Class, race, name = "Neutral", "", "Well of Destiny"
    mana = 2
    index = "SV_Basic~Neutral~Amulet~2~None~Well of Destiny"
    requireTarget, description = False, "At the start of your turn, give +1/+1 to a random allied follower."

    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.trigsBoard = [Trig_WellofDestiny(self)]


class Trig_WellofDestiny(TrigBoard):
    def __init__(self, entity):
        self.blank_init(entity, ["TurnStarts"])

    def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.onBoard and ID == self.entity.ID

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        curGame = self.entity.Game
        if curGame.mode == 0:
            if curGame.guides:
                i = curGame.guides.pop(0)
            else:
                minions = curGame.minionsonBoard(self.entity.ID)
                try:
                    minions.remove(self.entity)
                except:
                    pass
                i = npchoice(minions).position if minions else -1
                curGame.fixedGuides.append(i)
            if i > -1:
                minion = curGame.minions[self.entity.ID][i]
                PRINT(self.entity.Game, "At the start of turn, Well of Destiny give +1/+1 to a random allied follower.")
                minion.buffDebuff(1, 1)


class MercenaryDrifter(ShadowverseMinion):
    Class, race, name = "Neutral", "", "Mercenary Drifter"
    mana, attack, health = 3, 3, 2
    index = "SV_Basic~Neutral~Minion~3~3~2~None~Mercenary Drifter"
    requireTarget, keyWord, description = False, "", ""
    attackAdd, healthAdd = 2, 2


class HarnessedFlame(ShadowverseMinion):
    Class, race, name = "Neutral", "", "Harnessed Flame"
    mana, attack, health = 3, 2, 1
    index = "SV_Basic~Neutral~Minion~3~2~1~None~Harnessed Flame"
    requireTarget, keyWord, description = False, "", "Strike: Deal 2 damage to the enemy leader.At the start of your turn, this follower combines with an allied Harnessed Glass to become Flame and Glass."
    attackAdd, healthAdd = 2, 2

    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.trigsBoard = [Trig_HarnessedFlame(self), Trig_HarnessedFlameUnion(self)]


class Trig_HarnessedFlame(TrigBoard):
    def __init__(self, entity):
        self.blank_init(entity, ["MinionAttackingMinion", "MinionAttackingHero"])

    def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
        return subject == self.entity and self.entity.onBoard

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        PRINT(self.entity.Game, "When Harnessed Flame attacks, Deal 2 damage to the enemy leader.")
        self.entity.dealsDamage(self.entity.Game.heroes[3 - self.entity.ID], 2)


class Trig_HarnessedFlameUnion(TrigBoard):
    def __init__(self, entity):
        self.blank_init(entity, ["TurnStarts"])

    def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.onBoard and ID == self.entity.ID

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        minions = self.entity.Game.minionsonBoard(self.entity.ID)
        for minion in minions:
            if minion.name == "Harnessed Glass":
                minion.disappears(deathrattlesStayArmed=False)
                self.entity.Game.removeMinionorWeapon(minion)
                self.entity.Game.transform(self.entity, FlameandGlass(self.entity.Game, self.entity.ID))
                break


class HarnessedGlass(ShadowverseMinion):
    Class, race, name = "Neutral", "", "Harnessed Glass"
    mana, attack, health = 3, 1, 2
    index = "SV_Basic~Neutral~Minion~3~2~1~None~Harnessed Glass"
    requireTarget, keyWord, description = False, "", "Strike: Deal 1 damage to all enemy followers.At the start of your turn, this follower combines with an allied Harnessed Flame to become Flame and Glass."
    attackAdd, healthAdd = 2, 2

    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.trigsBoard = [Trig_HarnessedGlass(self), Trig_HarnessedGlassUnion(self)]


class Trig_HarnessedGlass(TrigBoard):
    def __init__(self, entity):
        self.blank_init(entity, ["MinionAttackingMinion", "MinionAttackingHero"])

    def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
        return subject == self.entity and self.entity.onBoard

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        PRINT(self.entity.Game, "When Harnessed Glass attacks, Deal 1 damage to all enemy followers.")
        targets = self.entity.Game.minionsonBoard(3 - self.entity.ID)
        self.entity.dealsAOE(targets, [1 for obj in targets])
        self.entity.Game.gathertheDead()
        if not target.onBoard:
            self.entity.attTimes += 1


class Trig_HarnessedGlassUnion(TrigBoard):
    def __init__(self, entity):
        self.blank_init(entity, ["TurnStarts"])

    def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.onBoard and ID == self.entity.ID

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        minions = self.entity.Game.minionsonBoard(self.entity.ID)
        for minion in minions:
            if minion.name == "Harnessed Flame":
                minion.disappears(deathrattlesStayArmed=False)
                self.entity.Game.removeMinionorWeapon(minion)
                self.entity.Game.transform(self.entity, FlameandGlass(self.entity.Game, self.entity.ID))
                break


class FlameandGlass(ShadowverseMinion):
    Class, race, name = "Neutral", "", "Flame and Glass"
    mana, attack, health = 7, 7, 7
    index = "SV_Basic~Neutral~Minion~7~7~7~None~Flame and Glass~Charge~Uncollectible"
    requireTarget, keyWord, description = False, "Charge", "Storm.Strike: Deal 7 damage to all enemies."
    attackAdd, healthAdd = 2, 2

    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.trigsBoard = [Trig_FlameandGlass(self)]


class Trig_FlameandGlass(TrigBoard):
    def __init__(self, entity):
        self.blank_init(entity, ["MinionAttackingMinion", "MinionAttackingHero"])

    def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
        return subject == self.entity and self.entity.onBoard

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        PRINT(self.entity.Game, "When Flame and Glass attacks, Deal 7 damage to all enemies.")
        targets = [self.entity.Game.heroes[3 - self.entity.ID]] + self.entity.Game.minionsonBoard(3 - self.entity.ID)
        self.entity.dealsAOE(targets, [7 for obj in targets])
        self.entity.Game.gathertheDead()
        if not target.onBoard:
            self.entity.attTimes += 1


class Goliath(ShadowverseMinion):
    Class, race, name = "Neutral", "", "Goliath"
    mana, attack, health = 4, 3, 4
    index = "SV_Basic~Neutral~Minion~4~3~4~None~Goliath"
    requireTarget, keyWord, description = False, "", ""
    attackAdd, healthAdd = 2, 2


class AngelicSwordMaiden(ShadowverseMinion):
    Class, race, name = "Neutral", "", "Angelic Sword Maiden"
    mana, attack, health = 5, 2, 6
    index = "SV_Basic~Neutral~Minion~5~2~6~None~Angelic Sword Maiden~Taunt"
    requireTarget, keyWord, description = False, "Taunt", "Ward."
    attackAdd, healthAdd = 2, 2


"""Forestcraft cards"""


class Fairy(ShadowverseMinion):
    Class, race, name = "Forestcraft", "", "Fairy"
    mana, attack, health = 1, 1, 1
    index = "SV_Basic~Forestcraft~Minion~1~1~1~None~Fairy~Uncollectible"
    requireTarget, keyWord, description = False, "", ""
    attackAdd, healthAdd = 2, 2


class WaterFairy(ShadowverseMinion):
    Class, race, name = "Forestcraft", "", "Water Fairy"
    mana, attack, health = 1, 1, 1
    index = "SV_Basic~Forestcraft~Minion~1~1~1~None~Water Fairy~Deathrattle"
    requireTarget, keyWord, description = False, "", "Last Words: Put a Fairy into your hand."
    attackAdd, healthAdd = 2, 2

    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.overload = 2
        self.deathrattles = [Deathrattle_WaterFairy(self)]


class Deathrattle_WaterFairy(Deathrattle_Minion):
    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        PRINT(self.entity.Game, "Water Fairy's Last Words put a Fairy into your hand.")
        self.entity.Game.Hand_Deck.addCardtoHand(Fairy, self.entity.ID, "CreateUsingType")


class FairyWhisperer(ShadowverseMinion):
    Class, race, name = "Forestcraft", "", "Fairy Whisperer"
    mana, attack, health = 2, 1, 1
    index = "SV_Basic~Forestcraft~Minion~2~1~1~None~Fairy Whisperer~Battlecry"
    requireTarget, keyWord, description = False, "", "Fanfare: Put 2 Fairies into your hand."
    attackAdd, healthAdd = 2, 2

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        PRINT(self.Game, "Fairy Whisperer's Fanfare put a Fairy into your hand.")
        self.Game.Hand_Deck.addCardtoHand([Fairy for i in range(2)], self.ID, "CreateUsingType")
        return None


class ElfGuard(ShadowverseMinion):
    Class, race, name = "Forestcraft", "", "Elf Guard"
    mana, attack, health = 2, 1, 3
    index = "SV_Basic~Forestcraft~Minion~2~1~3~None~Elf Guard~Battlecry"
    requireTarget, keyWord, description = False, "", "Fanfare: Gain +1/+1 and Ward if at least 2 other cards were played this turn."
    attackAdd, healthAdd = 2, 2

    def effectCanTrigger(self):
        return len(self.Game.Counters.cardsPlayedThisTurn[self.ID]["Indices"]) >= 2

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        numCardsPlayed = len(self.Game.Counters.cardsPlayedThisTurn[self.ID]["Indices"])
        if numCardsPlayed >= 2:
            PRINT(self.Game, "Elf Guard gains +1/+1 and Ward")
            self.buffDebuff(1, 1)
            self.getsKeyword("Taunt")
        return None


class ElfMetallurgist(ShadowverseMinion):
    Class, race, name = "Forestcraft", "", "Elf Metallurgist"
    mana, attack, health = 2, 2, 1
    index = "SV_Basic~Forestcraft~Minion~2~2~1~None~Elf Metallurgist~Battlecry"
    requireTarget, keyWord, description = True, "", "Fanfare: Deal 2 damage to an enemy follower if at least 2 other cards were played this turn."
    attackAdd, healthAdd = 2, 2

    def returnTrue(self, choice=0):
        return len(self.Game.Counters.cardsPlayedThisTurn[self.ID]["Indices"]) >= 2

    def effectCanTrigger(self):
        self.effectViable = len(self.Game.Counters.cardsPlayedThisTurn[self.ID]["Indices"]) >= 2

    def targetExists(self, choice=0):
        return self.selectableEnemyMinionExists()

    def targetCorrect(self, target, choice=0):
        return target.type == "Minion" and target.ID != self.ID and target.onBoard

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        numCardsPlayed = len(self.Game.Counters.cardsPlayedThisTurn[self.ID]["Indices"])
        if numCardsPlayed >= 2:
            self.dealsDamage(target, 2)
            PRINT(self.Game, f"Elf Metallurgist deals 2 damage to {target.name}")
        return None


class SylvanJustice(ShadowverseSpell):
    Class, name = "Forestcraft", "Sylvan Justice"
    requireTarget, mana = True, 2
    index = "SV_Basic~Forestcraft~Spell~2~Sylvan Justice"
    description = "Deal 2 damage to an enemy follower. Put a Fairy into your hand."

    def available(self):
        return self.selectableEnemyMinionExists()

    def targetCorrect(self, target, choice=0):
        return target.type == "Minion" and target.onBoard and target.ID != self.ID

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if target:
            damage = (2 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
            PRINT(self.Game,
                  f"Sylvan Justice deals {damage} damage to {target} and put a Fairy into your hand.")
            self.Game.Hand_Deck.addCardtoHand(Fairy, self.ID, "CreateUsingType")
        return target


class DarkElfFaure(ShadowverseMinion):
    Class, race, name = "Forestcraft", "", "Dark Elf Faure"
    mana, attack, health = 3, 2, 3
    index = "SV_Basic~Forestcraft~Minion~3~2~3~None~Dark Elf Faure"
    requireTarget, keyWord, description = False, "", "Strike: Put a Fairy into your hand."
    attackAdd, healthAdd = 2, 2

    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.trigsBoard = [Trig_DarkElfFaure(self)]


class Trig_DarkElfFaure(TrigBoard):
    def __init__(self, entity):
        self.blank_init(entity, ["MinionAttackingMinion", "MinionAttackingHero"])

    def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
        return subject == self.entity and self.entity.onBoard

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        PRINT(self.entity.Game, "Dark Elf Faure's Strike put a Fairy into your hand.")
        self.entity.Game.Hand_Deck.addCardtoHand(Fairy, self.entity.ID, "CreateUsingType")


class Okami(ShadowverseMinion):
    Class, race, name = "Forestcraft", "", "Okami"
    mana, attack, health = 4, 3, 4
    index = "SV_Basic~Forestcraft~Minion~4~3~4~None~Okami"
    requireTarget, keyWord, description = False, "", "Whenever another allied follower comes into play, gain +1/+0."
    attackAdd, healthAdd = 2, 2

    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.trigsBoard = [Trig_Okami(self)]


class Trig_Okami(TrigBoard):
    def __init__(self, entity):
        self.blank_init(entity, ["MinionSummoned"])

    def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.onBoard and subject.ID == self.entity.ID and subject != self.entity

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        PRINT(self.entity.Game,
              f"A friendly minion {subject.name} is summoned and Okami gains +1 attack.")
        self.entity.buffDebuff(1, 0)


class RoseGardener(ShadowverseMinion):
    Class, race, name = "Forestcraft", "", "Rose Gardener"
    mana, attack, health = 4, 4, 3
    index = "SV_Basic~Forestcraft~Minion~4~4~3~None~Rose Gardener"
    requireTarget, keyWord, description = False, "", ""
    attackAdd, healthAdd = 1, 1

    def inHandEvolving(self, target=None):
        if target and target.onBoard:
            PRINT(self.Game, f"Rose Gardener's Evolve returns {target.name} to owner's hand.")
            self.Game.returnMiniontoHand(target, deathrattlesStayArmed=False)


class Treant(ShadowverseMinion):
    Class, race, name = "Forestcraft", "", "Treant"
    mana, attack, health = 5, 4, 4
    index = "SV_Basic~Forestcraft~Minion~5~4~4~None~Treant~Battlecry"
    requireTarget, keyWord, description = False, "", "Fanfare: Gain +2/+2 if at least 2 other cards were played this turn."
    attackAdd, healthAdd = 2, 2

    def effectCanTrigger(self):
        return len(self.Game.Counters.cardsPlayedThisTurn[self.ID]["Indices"]) >= 2

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        numCardsPlayed = len(self.Game.Counters.cardsPlayedThisTurn[self.ID]["Indices"])
        if numCardsPlayed >= 2:
            PRINT(self.Game, "Elf Guard gains +2/+2")
            self.buffDebuff(2, 2)
        return None


class ElfTracker(ShadowverseMinion):
    Class, race, name = "Forestcraft", "", "Elf Tracker"
    mana, attack, health = 6, 4, 5
    index = "SV_Basic~Forestcraft~Minion~6~4~5~None~Elf Tracker~Battlecry"
    requireTarget, keyWord, description = False, "", "Fanfare: Deal 1 damage to a random enemy follower. Do this 2 times."
    attackAdd, healthAdd = 2, 2

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        side, curGame = 3 - self.ID, self.Game
        if curGame.mode == 0:
            for num in range(2):
                char = None
                if curGame.guides:
                    i, where = curGame.guides.pop(0)
                    if where: char = curGame.find(i, where)
                else:
                    objs = curGame.minionsonBoard(side)
                    if objs:
                        char = npchoice(objs)
                        curGame.fixedGuides.append((char.position, f"minion{side}"))
                    else:
                        curGame.fixedGuides.append((0, ''))
                if char:
                    self.dealsDamage(char, 1)
                    PRINT(self.Game, f"Elf Tracker's Fanfare deals 1 damage to {char.name}")
                else:
                    break
        return None


class MagnaBotanist(ShadowverseMinion):
    Class, race, name = "Forestcraft", "", "Magna Botanist"
    mana, attack, health = 6, 5, 5
    index = "SV_Basic~Forestcraft~Minion~6~5~5~None~Magna Botanist~Battlecry"
    requireTarget, keyWord, description = False, "", "Fanfare: Give +1/+1 to all allied followers if at least 2 other cards were played this turn."
    attackAdd, healthAdd = 2, 2

    def effectCanTrigger(self):
        return len(self.Game.Counters.cardsPlayedThisTurn[self.ID]["Indices"]) >= 2

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        numCardsPlayed = len(self.Game.Counters.cardsPlayedThisTurn[self.ID]["Indices"])
        if numCardsPlayed >= 2:
            PRINT(self.Game, "Magna Botanist's Fanfare Give +1/+1 to all allied followers")
            for minion in fixedList(self.Game.minionsonBoard(self.ID)):
                minion.buffDebuff(1, 1)
        return None


"""Swordcraft cards"""


class SteelcladKnight(ShadowverseMinion):
    Class, race, name = "Swordcraft", "Officer", "Steelclad Knight"
    mana, attack, health = 2, 2, 2
    index = "SV_Basic~Swordcraft~Minion~2~2~2~Officer~Steelclad Knight~Uncollectible"
    requireTarget, keyWord, description = False, "", ""
    attackAdd, healthAdd = 2, 2


class HeavyKnight(ShadowverseMinion):
    Class, race, name = "Swordcraft", "Officer", "Heavy Knight"
    mana, attack, health = 1, 1, 2
    index = "SV_Basic~Swordcraft~Minion~1~1~2~Officer~Heavy Knight~Uncollectible"
    requireTarget, keyWord, description = False, "", ""
    attackAdd, healthAdd = 2, 2


class Knight(ShadowverseMinion):
    Class, race, name = "Swordcraft", "Officer", "Knight"
    mana, attack, health = 1, 1, 1
    index = "SV_Basic~Swordcraft~Minion~1~1~1~Officer~Knight~Uncollectible"
    requireTarget, keyWord, description = False, "", ""
    attackAdd, healthAdd = 2, 2


class ShieldGuardian(ShadowverseMinion):
    Class, race, name = "Swordcraft", "Officer", "Shield Guardian"
    mana, attack, health = 1, 1, 1
    index = "SV_Basic~Swordcraft~Minion~1~1~1~Officer~Shield Guardian~Taunt~Uncollectible"
    requireTarget, keyWord, description = False, "Taunt", "Ward"
    attackAdd, healthAdd = 2, 2


class Quickblader(ShadowverseMinion):
    Class, race, name = "Swordcraft", "Officer", "Quickblader"
    mana, attack, health = 1, 1, 1
    index = "SV_Basic~Swordcraft~Minion~1~1~1~Officer~Quickblader~Charge"
    requireTarget, keyWord, description = False, "Charge", "Storm"
    attackAdd, healthAdd = 2, 2


class OathlessKnight(ShadowverseMinion):
    Class, race, name = "Swordcraft", "Officer", "Oathless Knight"
    mana, attack, health = 2, 1, 1
    index = "SV_Basic~Swordcraft~Minion~2~1~1~Officer~Oathless Knight~Battlecry"
    requireTarget, keyWord, description = False, "", "Fanfare: Summon a Knight."
    attackAdd, healthAdd = 2, 2

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        PRINT(self, "Oathless Knight's Fanfare summons a 1/1 Knight.")
        self.Game.summonMinion([Knight(self.Game, self.ID)], (-11, "totheRightEnd"), self.ID)
        return None


class KunoichiTrainee(ShadowverseMinion):
    Class, race, name = "Swordcraft", "Officer", "Kunoichi Trainee"
    mana, attack, health = 2, 2, 1
    index = "SV_Basic~Swordcraft~Minion~2~2~1~Officer~Kunoichi Trainee~Stealth"
    requireTarget, keyWord, description = False, "Stealth", "Ambush."
    attackAdd, healthAdd = 2, 2


class AsceticKnight(ShadowverseMinion):
    Class, race, name = "Swordcraft", "Officer", "Ascetic Knight"
    mana, attack, health = 3, 1, 2
    index = "SV_Basic~Swordcraft~Minion~3~1~2~Officer~Ascetic Knight~Battlecry"
    requireTarget, keyWord, description = False, "", "Fanfare: Summon a Heavy Knight."
    attackAdd, healthAdd = 2, 2

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        PRINT(self, "Ascetic Knight's Fanfare summons a 1/2 Heavy Knight.")
        self.Game.summonMinion([HeavyKnight(self.Game, self.ID)], (-11, "totheRightEnd"), self.ID)
        return None


class ForgeWeaponry(ShadowverseSpell):
    Class, name = "Swordcraft", "Forge Weaponry"
    requireTarget, mana = True, 3
    index = "SV_Basic~Swordcraft~Spell~3~Forge Weaponry"
    description = "Give +2/+2 to an allied follower. Rally (10): Give +4/+4 instead."

    def available(self):
        return self.selectableFriendlyMinionExists()

    def targetCorrect(self, target, choice=0):
        if isinstance(target, list): target = target[0]
        return target.type == "Minion" and target.ID == self.ID and target.onBoard

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if target:
            if isinstance(target, list): target = target[0]
            if self.Game.Counters.numMinionsSummonedThisGame[self.ID] > 10:
                PRINT(self.Game, f"Forge Weaponry gives +4/+4 to {target.name}.")
                target.buffDebuff(4, 4)
            else:
                PRINT(self.Game, f"Forge Weaponry gives +2/+2 to {target.name}.")
                target.buffDebuff(2, 2)

        return target


class WhiteGeneral(ShadowverseMinion):
    Class, race, name = "Forestcraft", "Commander", "White General"
    mana, attack, health = 4, 3, 3
    index = "SV_Basic~Forestcraft~Minion~4~3~3~Commander~White General~Battlecry"
    requireTarget, keyWord, description = True, "", "Fanfare: Give +2/+0 to an allied Officer follower."
    attackAdd, healthAdd = 2, 2

    def targetExists(self, choice=0):
        for minion in self.Game.minionsonBoard(self.ID):
            if "Officer" in minion.race:
                return True
        return False

    def targetCorrect(self, target, choice=0):
        return target.type == "Minion" and target.ID == self.ID and target.onBoard and "Officer" in target.race

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if target:
            target.buffDebuff(2, 0)
            PRINT(self.Game, f"White General gives +2/+0 to {target.name}.")
        return None


class FloralFencer(ShadowverseMinion):
    Class, race, name = "Swordcraft", "Officer", "Floral Fencer"
    mana, attack, health = 4, 3, 4
    index = "SV_Basic~Swordcraft~Minion~4~3~4~Officer~Floral Fencer"
    requireTarget, keyWord, description = False, "", ""
    attackAdd, healthAdd = 1, 1

    def inHandEvolving(self, target=None):
        PRINT(self, "Oathless Knight's Fanfare summons a 1/1 Knight and a 2/2 Steelclad Knight.")
        self.Game.summonMinion([Knight(self.Game, self.ID), SteelcladKnight(self.Game, self.ID)],
                               (-11, "totheRightEnd"), self.ID)
        return None


class RoyalBanner(ShadowverseAmulet):
    Class, race, name = "Swordcraft", "Commander", "Royal Banner"
    mana = 4
    index = "SV_Basic~Swordcraft~Amulet~4~Commander~Royal Banner~Battlecry"
    requireTarget, description = False, "Fanfare: Give +1/+0 to all allied Officer followers. Whenever an allied Officer follower comes into play, give it +1/+0."

    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.trigsBoard = [Trig_RoyalBanner(self)]

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        PRINT(self.Game, "Sage Commander's Fanfare gives +1/+0 to all allied Officer followers")
        for minion in fixedList(self.Game.minionsonBoard(self.ID)):
            if "Officer" in minion.race:
                minion.buffDebuff(1, 0)
        return None


class Trig_RoyalBanner(TrigBoard):
    def __init__(self, entity):
        self.blank_init(entity, ["MinionBeenSummoned"])

    def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
        return subject.ID == self.entity.ID and self.entity.onBoard and "Officer" in target.race

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        PRINT(self.entity.Game, f"A friendly minion {subject.name} is summoned and Royal Banner gives it +1/+0."
        subject.buffDebuff(1, 0)


class NinjaMaster(ShadowverseMinion):
    Class, race, name = "Swordcraft", "Officer", "Ninja Master"
    mana, attack, health = 5, 4, 4
    index = "SV_Basic~Swordcraft~Minion~5~4~4~Officer~Ninja Master~Stealth"
    requireTarget, keyWord, description = False, "Stealth", "Ambush."
    attackAdd, healthAdd = 2, 2


class SageCommander(ShadowverseMinion):
    Class, race, name = "Swordcraft", "Commander", "Sage Commander"
    mana, attack, health = 6, 4, 6
    index = "SV_Basic~Swordcraft~Minion~6~4~6~Commander~Sage Commander~Battlecry"
    requireTarget, keyWord, description = False, "", "Fanfare: Give +1/+1 to all other allied followers."
    attackAdd, healthAdd = 2, 2

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        PRINT(self.Game, "Sage Commander's Fanfare gives +1/+1 to all allied followers")
        for minion in fixedList(self.Game.minionsonBoard(self.ID)):
            minion.buffDebuff(1, 1)
        return None


"""Runecraft cards"""
class ClayGolem(ShadowverseMinion):
    Class, race, name = "Runecraft", "", "Clay Golem"
    mana, attack, health = 2, 2, 2
    index = "SV_Basic~Runecraft~Minion~2~2~2~None~Clay Golem~Uncollectible"
    requireTarget, keyWord, description = False, "", ""
    attackAdd, healthAdd = 2, 2

class Snowman(ShadowverseMinion):
    Class, race, name = "Runecraft", "", "Snowman"
    mana, attack, health = 1, 1, 1
    index = "SV_Basic~Runecraft~Minion~1~1~1~None~Snowman~Uncollectible"
    requireTarget, keyWord, description = False, "", ""
    attackAdd, healthAdd = 2, 2

class EarthEssence(ShadowverseAmulet):
    Class, race, name = "Runecraft", "Earth Sigil", "Earth Essence"
    mana = 1
    index = "SV_Basic~Runecraft~Amulet~1~Earth Sigil~Earth Essence~Uncollectible"
    requireTarget, description = False, ""

class GuardianGolem(ShadowverseMinion):
    Class, race, name = "Runecraft", "", "Guardian Golem"
    mana, attack, health = 4, 3, 3
    index = "SV_Basic~Runecraft~Minion~4~3~3~None~Guardian Golem~Taunt~Uncollectible"
    requireTarget, keyWord, description = False, "Taunt", "Ward."
    attackAdd, healthAdd = 2, 2

class ScrapGolem(ShadowverseMinion):
    Class, race, name = "Runecraft", "", "Scrap Golem"
    mana, attack, health = 1, 0, 2
    index = "SV_Basic~Runecraft~Minion~1~0~2~None~Scrap Golem~Taunt~Uncollectible"
    requireTarget, keyWord, description = False, "Taunt", "Ward."
    attackAdd, healthAdd = 2, 2

class ConjureGuardian(ShadowverseSpell):
    Class, name = "Runecraft", "Conjure Guardian"
    requireTarget, mana = False, 2
    index = "SV_Basic~Runecraft~Spell~2~Conjure Guardian~Uncollectible"
    description = "Summon a Guardian Golem."

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        PRINT(self, "Conjure Golem summons a Guardian Golem")
        self.Game.summonMinion([GuardianGolem(self.Game, self.ID)], (-11, "totheRightEnd"), self.ID)
        return None

class Trig_Spellboost(TrigHand):
    def __init__(self, entity):
        self.blank_init(entity, ["Spellboost"])

    def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.inHand and target.ID == self.entity.ID

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        self.entity.progress += 1


class Insight(ShadowverseSpell):
    Class, name = "Runecraft", "Insight"
    requireTarget, mana = False, 1
    index = "SV_Basic~Runecraft~Spell~1~Insight"
    description = "Draw a card."

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        PRINT(self, "Insight let player draw a card.")
        self.Game.Hand_Deck.drawCard(self.ID)
        return None


class SammyWizardsApprentice(ShadowverseMinion):
    Class, race, name = "Runecraft", "", "Sammy, Wizard's Apprentice"
    mana, attack, health = 2, 2, 2
    index = "SV_Basic~Runecraft~Minion~2~2~2~None~Sammy, Wizard's Apprentice~Battlecry"
    requireTarget, keyWord, description = False, "", "Fanfare: Give +1/+1 to all other allied followers."
    attackAdd, healthAdd = 2, 2

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        PRINT(self, "Insight let both player draw a card.")
        self.Game.Hand_Deck.drawCard(self.ID)
        self.Game.Hand_Deck.drawCard(3 - self.ID)
        return None


class MagicMissile(ShadowverseSpell):
    Class, name = "Runecraft", "Magic Missile"
    requireTarget, mana = True, 2
    index = "SV_Basic~Runecraft~Spell~2~Magic Missile"
    description = "Deal 1 damage to an enemy. Draw a card."

    def available(self):
        return self.selectableEnemyExists()

    def targetCorrect(self, target, choice=0):
        if isinstance(target, list): target = target[0]
        return (target.type == "Minion" or target.type == "Hero") and target.ID != self.ID and target.onBoard

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if target:
            if isinstance(target, list): target = target[0]
            damage = (1 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
            PRINT(self.Game, f"Unbridled Fury deals {damage} damage to enemy {target.name} and let player draw a card.")
            self.dealsDamage(target, damage)
            self.Game.Hand_Deck.drawCard(self.ID)
        return target


class ConjureGolem(ShadowverseSpell):
    Class, name = "Runecraft", "Conjure Golem"
    requireTarget, mana = False, 2
    index = "SV_Basic~Runecraft~Spell~2~Conjure Golem"
    description = "Summon a Clay Golem."

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        PRINT(self, "Conjure Golem summons a Clay Golem")
        self.Game.summonMinion([ClayGolem(self.Game, self.ID)], (-11, "totheRightEnd"), self.ID)
        return None



class WindBlast(ShadowverseSpell):
    Class, name = "Runecraft", "Wind Blast"
    requireTarget, mana = True, 2
    index = "SV_Basic~Runecraft~Spell~2~Wind Blast~Spellboost"
    description = "Deal 1 damage to an enemy follower. Spellboost: Deal 1 more."

    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.trigsHand = [Trig_Spellboost(self)]  # 只有在手牌中才会升级
        self.progress = 0

    def available(self):
        return self.selectableEnemyMinionExists()

    def targetCorrect(self, target, choice=0):
        if isinstance(target, list): target = target[0]
        return target.type == "Minion" and target.ID != self.ID and target.onBoard

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if target:
            if isinstance(target, list): target = target[0]
            damage = (1 + self.progress + self.countSpellDamage()) * (2 ** self.countDamageDouble())
            PRINT(self.Game, f"Wind Blast deals {damage} damage to enemy {target.name}")
            self.dealsDamage(target, damage)
        return target



class SummonSnow(ShadowverseSpell):
    Class, name = "Runecraft", "Summon Snow"
    requireTarget, mana = False, 3
    index = "SV_Basic~Runecraft~Spell~2~Summon Snow~Spellboost"
    description = "Summon 1 Snowman. Spellboost: Summon 1 more."

    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.trigsHand = [Trig_Spellboost(self)]  # 只有在手牌中才会升级
        self.progress = 0

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        PRINT(self, "Insight let player draw a card.")
        self.Game.summonMinion([Snowman(self.Game, self.ID) for i in range(1 + self.progress)], (-11, "totheRightEnd"), self.ID)
        return None

class DemonflameMage(ShadowverseMinion):
    Class, race, name = "Runecraft", "", "Demonflame Mage"
    mana, attack, health = 4, 3, 4
    index = "SV_Basic~Runecraft~Minion~4~3~4~None~Demonflame Mage"
    requireTarget, keyWord, description = False, "", ""
    attackAdd, healthAdd = 1, 1

    def inHandEvolving(self, target=None):
        PRINT(self, "Demonflame Mage's Evolve deals 1 damage to all enemy followers")
        targets = self.Game.minionsonBoard(3 - self.ID)
        self.dealsAOE(targets, [1 for obj in targets])
        return None

class ConjureTwosome(ShadowverseSpell):
    Class, name = "Runecraft", "Conjure Twosome"
    requireTarget, mana = False, 4
    index = "SV_Basic~Runecraft~Spell~4~Conjure Twosome"
    description = "Summon a Clay Golem."

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        PRINT(self, "Conjure Twosome summons two Clay Golems")
        self.Game.summonMinion([ClayGolem(self.Game, self.ID),ClayGolem(self.Game, self.ID)], (-11, "totheRightEnd"), self.ID)
        return None

class LightningShooter(ShadowverseMinion):
    Class, race, name = "Runecraft", "", "Lightning Shooter"
    mana, attack, health = 5, 3, 3
    index = "SV_Basic~Runecraft~Minion~5~3~3~None~Lightning Shooter~Battlecry~Spellboost"
    requireTarget, keyWord, description = True, "", "Fanfare: Deal 1 damage to an enemy follower. Spellboost: Deal 1 more."
    attackAdd, healthAdd = 2, 2

    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.trigsHand = [Trig_Spellboost(self)]  # 只有在手牌中才会升级
        self.progress = 0

    def targetExists(self, choice=0):
        return self.selectableEnemyMinionExists()

    def targetCorrect(self, target, choice=0):
        return target.type == "Minion" and target.ID != self.ID and target.onBoard

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        numCardsPlayed = len(self.Game.Counters.cardsPlayedThisTurn[self.ID]["Indices"])
        if numCardsPlayed >= 2:
            self.dealsDamage(target, 1 + self.progress)
            PRINT(self.Game, f"Lightning Shooter deals 2 damage to {target.name}")
        return None

class FieryEmbrace(ShadowverseSpell):
    Class, name = "Runecraft", "Fiery Embrace"
    requireTarget, mana = True, 8
    index = "SV_Basic~Runecraft~Spell~8~Fiery Embrace~Spellboost"
    description = "Spellboost: Subtract 1 from the cost of this card. Destroy an enemy follower."

    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.trigsHand = [Trig_Spellboost(self)]  # 只有在手牌中才会升级
        self.progress = 0

    def selfManaChange(self):
        if self.inHand:
            self.mana -= self.progress
            self.mana = max(self.mana, 0)

    def available(self):
        return self.selectableEnemyMinionExists()

    def targetCorrect(self, target, choice=0):
        if isinstance(target, list): target = target[0]
        return target.type == "Minion" and target.ID != self.ID and target.onBoard

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if target:
            if isinstance(target, list): target = target[0]
            PRINT(self.Game, f"Fiery Embrace destroys enemy {target.name}")
            target.dead = True
        return target

class FlameDestroyer(ShadowverseMinion):
    Class, race, name = "Runecraft", "", "Flame Destroyer"
    mana, attack, health = 10, 7, 7
    index = "SV_Basic~Runecraft~Minion~10~7~7~None~Flame Destroyer~Spellboost"
    requireTarget, keyWord, description = True, "", "Spellboost: Subtract 1 from the cost of this card."
    attackAdd, healthAdd = 2, 2

    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.trigsHand = [Trig_Spellboost(self)]  # 只有在手牌中才会升级
        self.progress = 0

    def selfManaChange(self):
        if self.inHand:
            self.mana -= self.progress
            self.mana = max(self.mana, 0)

"""Drangoncraft cards"""

"""Shadowcraft cards"""

"""Bloodcraft cards"""

"""Havencraft cards"""

"""Portalcraft cards"""

SV_Basic_Indices = {
    "SV_Hero: Forestcraft": Arisa,
    "SV_Hero: Swordcraft": Erika,
    "SV_Hero: Runecraft": Isabelle,
    "SV_Hero: Drangoncraft": Rowen,
    "SV_Hero: Shadowcraft": Luna,
    "SV_Hero: Bloodcraft": Urias,
    "SV_Hero: Havencraft": Eris,
    "SV_Hero: Portalcraft": Yuwan,
    "SV_Hero~Hero Power~0~Evolve": Evolve,

    "SV_Basic~Neutral~Minion~1~1~2~None~Goblin": Goblin,
    "SV_Basic~Neutral~Minion~2~2~2~None~Fighter": Fighter,
    "SV_Basic~Neutral~Amulet~2~None~Well of Destiny": WellofDestiny,
    "SV_Basic~Neutral~Minion~3~3~2~None~Mercenary Drifter": MercenaryDrifter,
    "SV_Basic~Neutral~Minion~3~2~1~None~Harnessed Flame": HarnessedFlame,
    "SV_Basic~Neutral~Minion~3~2~1~None~Harnessed Glass": HarnessedGlass,
    "SV_Basic~Neutral~Minion~7~7~7~None~Flame and Glass~Charge~Uncollectible": FlameandGlass,
    "SV_Basic~Neutral~Minion~4~3~4~None~Goliath": Goliath,
    "SV_Basic~Neutral~Minion~5~2~6~None~Angelic Sword Maiden~Taunt": AngelicSwordMaiden,
    "SV_Basic~Forestcraft~Minion~1~1~1~None~Fairy~Uncollectible": Fairy,
    "SV_Basic~Forestcraft~Minion~1~1~1~None~Water Fairy~Deathrattle": WaterFairy,
    "SV_Basic~Forestcraft~Minion~2~1~1~None~Fairy Whisperer~Battlecry": FairyWhisperer,
    "SV_Basic~Forestcraft~Minion~2~1~3~None~Elf Guard~Battlecry": ElfGuard,
    "SV_Basic~Forestcraft~Minion~2~2~1~None~Elf Metallurgist~Battlecry": ElfMetallurgist,
    "SV_Basic~Forestcraft~Spell~2~Sylvan Justice": SylvanJustice,
    "SV_Basic~Forestcraft~Minion~3~2~3~None~Dark Elf Faure": DarkElfFaure,
    "SV_Basic~Forestcraft~Minion~4~3~4~None~Okami": Okami,
    "SV_Basic~Forestcraft~Minion~4~4~3~None~Rose Gardener": RoseGardener,
    "SV_Basic~Forestcraft~Minion~5~4~4~None~Treant~Battlecry": Treant,
    "SV_Basic~Forestcraft~Minion~6~4~5~None~Elf Tracker~Battlecry": ElfTracker,
    "SV_Basic~Forestcraft~Minion~6~5~5~None~Magna Botanist~Battlecry": MagnaBotanist,

    "SV_Basic~Runecraft~4~3~3~Minion~None~Vesper, Witchhunter~Accelerate~Fanfare": VesperWitchhunter,
    "SV_Basic~Runecraft~Spell~2~Vesper, Witchhunter~Uncollectible": VesperWitchhunter_Accelerate,
    "SV_Basic~Havencraft~1~Amulet~None~Sacred Plea~Last Words": SacredPlea,
    "SV_Basic~Bloodcraft~Minion~10~5~10~None~Ruinweb Spider~Crystallize": RuinwebSpider,
    "SV_Basic~Bloodcraft~2~Amulet~None~Ruinweb Spider~Last Words": RuinwebSpider_Shadowverse_Amulet,
    "SV_Basic~Bloodcraft~Minion~10~11~8~Dragon~XI. Erntz, Justice~Ward": XIErntzJustice,
    "SV_Basic~Forestcraft~Spell~1~Airbound Barrage": AirboundBarrage,
}
