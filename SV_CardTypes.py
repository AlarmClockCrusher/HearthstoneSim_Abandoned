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


class SVMinion(Minion):
    attackAdd, healthAdd = 2, 2

    def blank_init(self, Game, ID):
        super().blank_init(Game, ID)
        self.targets = []

    def evolve(self):
        if self.onBoard and self.status["Evolved"] < 1:
            self.attack_0 += self.attackAdd
            self.health_0 += self.healthAdd
            self.statReset(self.attack + self.attackAdd, self.health + self.healthAdd)
            self.status["Evolved"] += 1
            PRINT(self.Game, self.name + " evolves.")
            self.Game.Counters.evolvedThisGame[self.ID] += 1
            self.Game.Counters.evolvedThisTurn[self.ID] += 1
            for card in self.Game.Hand_Deck.hands[self.ID]:
                if isinstance(card, SVMinion) and "UB" in card.marks:
                    card.marks["UB"] -= 1
            self.inEvolving()
            self.Game.sendSignal("MinionEvolved", self.ID, self, None, 0, "", 0)

    def inEvolving(self):
        return

    def inHandEvolving(self, target=None):
        return

    def willEnhance(self):
        return False

    def willAccelerate(self):
        return False

    # 当费用不足以释放随从本体但又高于结晶费用X时，打出会以结晶方式打出，此时随从变形为一张护符打出在战场上，护符名为结晶：{随从名}，效果与随从本体无关。可能会具有本体不具有的额外种族。不会被本体减费影响，但若本体费用低于结晶费用则结晶无法触发。同一个随从可以同时具有结晶和爆能强化。
    def willCrystallize(self):
        return False

    def becomeswhenPlayed(self):
        return type(self).accelerateSpell(self.Game, self.ID) if self.willAccelerate() \
                   else (type(self).crystallizeAmulet(self.Game, self.ID) if self.willCrystallize() else self) \
            , self.getMana()

    # 优先判定能否激奏，如果可以，不再检测能否结晶。若不能激奏，则再检测是否能结晶
    def getTypewhenPlayed(self):
        return "Spell" if self.willAccelerate() else ("Amulet" if self.willCrystallize() else "Minion")

    def afterInvocation(self, signal, ID, subject, target, number, comment):
        return

    def returnTrue(self, choice=0):  # 只有在还没有选择过目标的情况下才能继续选择
        if self.needTarget:
            return not self.targets
        else:
            return True

    def canSelect(self, target):
        targets = target if isinstance(target, list) else [target]
        for target in targets:
            targetType = target.type
            selectable = target.inHand or target.onBoard and targetType != "Dormant" and targetType != "Power" and \
                         (
                                 (targetType == "Hero" and (
                                         target.ID == self.ID or self.Game.status[target.ID]["Immune"] +
                                         target.status["Temp Stealth"] + target.marks["Enemy Effect Evasive"] < 1) \
                                  and not ((self.type == "Power" or self.type == "Spell") and
                                           self.Game.status[target.ID]["Evasive"] > 1)) \
                                 # 不能被法术或者英雄技能选择的随从是： 魔免随从 或者 是对敌方魔免且法术或英雄技能是敌方的
                                 or (targetType == "Minion" and (
                                 target.ID == self.ID or target.status["Immune"] + target.keyWords["Stealth"] +
                                 target.status["Temp Stealth"] + target.marks["Enemy Effect Evasive"] < 1) \
                                     and not ((self.type == "Power" or self.type == "Spell") and (
                                         target.marks["Evasive"] > 1 or (
                                         target.ID != self.ID and target.marks["Enemy Evasive"] > 1)))) \
                                 or (targetType == "Amulet" and (
                                 target.ID == self.ID or target.marks["Enemy Effect Evasive"] < 1) \
                                     and not (self.type == "Spell" and target.marks["Evasive"] > 1)) \
 \
                             )
            if not selectable: return False
        return True

    def findTargets(self, comment="", choice=0):
        game, targets, indices, wheres = self.Game, [], [], []
        for ID in range(1, 3):
            hero = game.heroes[ID]
            if self.targetCorrect(hero, choice) and (comment == "" or self.canSelect(hero)):
                targets.append(hero)
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

    # Minions that initiates discover or transforms self will be different.
    # For minion that transform before arriving on board, there's no need in setting its onBoard to be True.
    # By the time this triggers, death resolution caused by Illidan/Juggler has been finished.
    # If Brann Bronzebeard/ Mayor Noggenfogger has been killed at this point, they won't further affect the battlecry.
    # posinHand在played中主要用于记录一张牌是否是从手牌中最左边或者最右边打出（恶魔猎手职业关键字）
    def played(self, target=None, choice=0, mana=0, posinHand=-2, comment=""):
        # 即使该随从在手牌中的生命值为0或以下，打出时仍会重置为无伤状态。
        self.statReset(self.attack_Enchant, self.health_max)
        # 此时，随从可以开始建立光环，建立侦听，同时接受其他光环。例如： 打出暴风城勇士之后，光环在Illidan的召唤之前给随从加buff，同时之后打出的随从也是先接受光环再触发Illidan。
        self.appears()
        # 使用阶段
        # 使用时步骤,触发“每当你使用一张xx牌”的扳机,如伊利丹，任务达人，无羁元素和魔能机甲等
        # 触发信号依次得到主玩家的场上，手牌和牌库的侦听器的响应，之后是副玩家的侦听器响应。
        # 伊利丹可以在此时插入召唤和飞刀的结算，之后在战吼结算开始前进行死亡的判定，同时subject和target的位置情况会影响战吼结果。
        self.Game.sendSignal("MinionPlayed", self.ID, self, target, mana, "", choice)
        # 召唤时步骤，触发“每当你召唤一个xx随从”的扳机.如鱼人招潮者等。
        self.Game.sendSignal("MinionSummoned", self.ID, self, target, mana, "")
        # 过载结算
        if self.overload > 0:
            PRINT(self.Game, "%s is played and Overloads %d mana crystals." % (self.name, self.overload))
            self.Game.Manas.overloadMana(self.overload, self.ID)

        magneticTarget = None
        if self.magnetic > 0:
            if self.onBoard:
                neighbors, dist = self.Game.neighbors2(self)
                if dist == 1 and "Mech" in neighbors[1].race:
                    magneticTarget = neighbors[1]
                elif dist == 2 and "Mech" in neighbors[0].race:
                    magneticTarget = neighbors[0]
        # 使用阶段结束，开始死亡结算。视随从的存活情况决定战吼的触发情况，此时暂不处理胜负问题。
        self.Game.gathertheDead()  # At this point, the minion might be removed/controlled by Illidan/Juggler combo.
        # 结算阶段
        if self.magnetic > 0:
            # 磁力相当于伪指向性战吼，一旦指定目标之后，不会被其他扳机改变
            # 磁力随从需要目标和自己都属于同一方,且磁力目标在场时才能触发。
            if magneticTarget and magneticTarget.onBoard and self.ID == magneticTarget.ID:
                # 磁力结算会让随从离场，不会触发后续的随从召唤后，打出后的扳机
                self.magnetCombine(magneticTarget)
        # 磁力随从没有战吼等入场特效，因而磁力结算不会引发死亡，不必进行死亡结算
        else:  # 无磁力的随从
            # 市长会在战吼触发前检测目标，指向性战吼会被随机取向。一旦这个随机过程完成，之后的第二次战吼会重复对此目标施放。
            # 如果场上有随从可供战吼选择，但是因为免疫和潜行导致打出随从时没有目标，则不会触发随机选择，因为本来就没有目标。
            # 在战吼开始检测之前，如果铜须已经死亡，则其并不会让战吼触发两次。也就是扳机的机制。
            # 同理，如果此时市长已经死亡，则其让选择随机化的扳机也已经离场，所以不会触发随机目标。
            if target and not isinstance(target, list):
                targetHolder = [target]
                self.Game.sendSignal("BattlecryTargetDecision", self.ID, self, targetHolder, 0, "", choice)
                if target != targetHolder[0] and self.Game.GUI:
                    target = targetHolder[0]
                    self.Game.GUI.target = target
                    self.Game.GUI.wait(400)
                else:
                    target = targetHolder[0]
            # 市长不会让发现和抉择选项的选择随机化。
            # 不管target是否还在场上，此时只要市长还在，就要重新在场上寻找合法目标。如果找不到，就不能触发战吼的指向性部分，以及其产生的后续操作。
            # 随机条件下，如果所有合法目标均已经消失，则return None. 由随从的战吼决定是否继续生效。

            # 在随从战吼/连击开始触发前，检测是否有战吼/连击翻倍的情况。如果有且战吼可以进行，则强行执行战吼至两次循环结束。无论那个随从是死亡，在手牌中还是牌库
            num = 1
            if "~Battlecry" in self.index and self.Game.status[self.ID]["Battlecry x2"] + self.Game.status[self.ID][
                "Shark Battlecry x2"] > 0:
                num = 2
            if "~Combo" in self.index and self.Game.status[self.ID]["Shark Battlecry x2"] > 0:
                num = 2
            # 不同的随从会根据目标和自己的位置和状态来决定effectwhenPlayed()产生体积效果。
            # 可以变形的随从，如无面操纵者，会有自己的played（） 方法。 大王同理。
            # 战吼随从自己不会进入牌库，因为目前没有亡语等效果可以把随从返回牌库。
            # 发现随从如果在战吼触发前被对方控制，则不会引起发现，因为炉石没有对方回合外进行操作的可能。
            # 结算战吼，连击，抉择
            for i in range(num):
                target = self.whenEffective(target, mana, choice, posinHand)

            # 结算阶段结束，处理死亡情况，不处理胜负问题。
            self.Game.gathertheDead()
        return target

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


class Amulet(Dormant):
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
        self.counter = -1
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
        self.keyWords = {"Taunt": 0, "Stealth": 0,
                         "Divine Shield": 0, "Spell Damage": 0,
                         "Lifesteal": 0, "Poisonous": 0,
                         "Windfury": 0, "Mega Windfury": 0,
                         "Charge": 0, "Rush": 0,
                         "Echo": 0
                         }
        self.marks = {"Sweep": 0,
                      "Evasive": 0, "Enemy Evasive": 0,
                      "Can't Attack": 0, "Can't Attack Hero": 0,
                      "Heal x2": 0,  # Crystalsmith Kangor
                      "Power Heal&Dmg x2": 0,  # Prophet Velen, Clockwork Automation
                      "Spell Heal&Dmg x2": 0,
                      "Enemy Effect Evasive": 0, "Enemy Effect Damage Immune": 0,
                      "Can't Break": 0, "Can't Disappear": 0, "Can't Be Attacked": 0, "Disappear When Die": 0,
                      "Next damage 0": 0, "Ignore Taunt": 0, "UB": 10, "Can't Evolve": 0, "Free Evolve": 0,
                      "Max Damage": -1}
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

    def willEnhance(self):
        return False

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

    def findTargets(self, comment="", choice=0):
        game, targets, indices, wheres = self.Game, [], [], []
        for ID in range(1, 3):
            hero = game.heroes[ID]
            if self.targetCorrect(hero, choice) and (comment == "" or self.canSelect(hero)):
                targets.append(hero)
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
        if "~Battlecry" in self.index and self.Game.status[self.ID]["Battlecry x2"] + self.Game.status[self.ID][
            "Shark Battlecry x2"] > 0:
            num = 2
        for i in range(num):
            target = self.whenEffective(target, "", choice, posinHand)

        # 结算阶段结束，处理死亡情况，不处理胜负问题。
        self.Game.gathertheDead()
        return target

    def countdown(self, subject, number):
        if self.counter > 0:
            self.counter = max(0, self.counter - number)
            if number > 0:
                self.Game.sendSignal(self, "Countdown", self.ID, subject, self, number, "")
            else:
                self.Game.sendSignal(self, "Countup", self.ID, subject, self, -number, "")
        if self.counter == 0:
            PRINT(self.Game, f"{self.name}'s countdown is 0 and destroys itself")
            self.Game.killMinion(None, self)

    def canSelect(self, target):
        targets = target if isinstance(target, list) else [target]
        for target in targets:
            targetType = target.type
            selectable = target.inHand or target.onBoard and targetType != "Dormant" and targetType != "Power" and \
                         (
                                 (targetType == "Hero" and (
                                         target.ID == self.ID or self.Game.status[target.ID]["Immune"] +
                                         target.status["Temp Stealth"] + target.marks["Enemy Effect Evasive"] < 1) \
                                  and not ((self.type == "Power" or self.type == "Spell") and
                                           self.Game.status[target.ID]["Evasive"] > 1)) \
                                 # 不能被法术或者英雄技能选择的随从是： 魔免随从 或者 是对敌方魔免且法术或英雄技能是敌方的
                                 or (targetType == "Minion" and (
                                 target.ID == self.ID or target.status["Immune"] + target.keyWords["Stealth"] +
                                 target.status["Temp Stealth"] + target.marks["Enemy Effect Evasive"] < 1) \
                                     and not ((self.type == "Power" or self.type == "Spell") and (
                                         target.marks["Evasive"] > 1 or (
                                         target.ID != self.ID and target.marks["Enemy Evasive"] > 1)))) \
                                 or (targetType == "Amulet" and (
                                 target.ID == self.ID or target.marks["Enemy Effect Evasive"] < 1) \
                                     and not (self.type == "Spell" and target.marks["Evasive"] > 1))
                             )
            if not selectable: return False
        return True

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
            Copy.counter = self.counter
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


class SVSpell(Spell):
    def __init__(self, Game, ID):
        super().__init__(Game, ID)
        self.targets = []

    def returnTrue(self, choice=0):
        if self.needTarget:
            return not self.targets
        else:
            return True

    def willEnhance(self):
        return False

    def findTargets(self, comment="", choice=0):
        game, targets, indices, wheres = self.Game, [], [], []
        for ID in range(1, 3):
            hero = game.heroes[ID]
            if self.targetCorrect(hero, choice) and (comment == "" or self.canSelect(hero)):
                targets.append(hero)
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

    def played(self, target=None, choice=0, mana=0, posinHand=-2, comment=""):
        repeatTimes = 2 if self.Game.status[self.ID]["Spells x2"] > 0 else 1
        if self.Game.GUI:
            self.Game.GUI.showOffBoardTrig(self)
            self.Game.GUI.wait(500)
        self.Game.sendSignal("SpellPlayed", self.ID, self, None, mana, "", choice)
        self.Game.sendSignal("Spellboost", self.ID, self, None, mana, "", choice)
        # 假设SV的法术在选取上不触发重导向扳机
        self.Game.gathertheDead()
        if target:
            self.Game.Counters.spellsonFriendliesThisGame[self.ID] += [self.index for obj in target if
                                                                       obj.ID == self.ID]
        # 假设SV的法术不受到"对相邻的法术也释放该法术"的影响
        for i in range(repeatTimes):
            if target:
                for obj in target:  # 每个目标都会检测是否记录该法术的作用历史
                    if (obj.type == "Minion" or obj.type == "Amulet") and obj.onBoard:
                        obj.history["Spells Cast on This"].append(self.index)
            target = self.whenEffective(target, mana, choice, posinHand)

        # 仅触发风潮，星界密使等的光环移除扳机。“使用一张xx牌之后”的扳机不在这里触发，而是在Game的playSpell函数中结算。
        self.Game.sendSignal("SpellBeenCast", self.Game.turn, self, None, 0, "", choice)
        self.Game.gathertheDead()  # At this point, the minion might be removed/controlled by Illidan/Juggler combo.
        if self.Game.GUI: self.Game.GUI.eraseOffBoardTrig(self.ID)

    def canSelect(self, target):
        targets = target if isinstance(target, list) else [target]
        for target in targets:
            targetType = target.type
            selectable = target.inHand or target.onBoard and targetType != "Dormant" and targetType != "Power" and \
                         (
                                 (targetType == "Hero" and (
                                         target.ID == self.ID or self.Game.status[target.ID]["Immune"] +
                                         target.status["Temp Stealth"] + target.marks["Enemy Effect Evasive"] < 1) \
                                  and not ((self.type == "Power" or self.type == "Spell") and
                                           self.Game.status[target.ID]["Evasive"] > 1)) \
                                 # 不能被法术或者英雄技能选择的随从是： 魔免随从 或者 是对敌方魔免且法术或英雄技能是敌方的
                                 or (targetType == "Minion" and (
                                 target.ID == self.ID or target.status["Immune"] + target.keyWords["Stealth"] +
                                 target.status["Temp Stealth"] + target.marks["Enemy Effect Evasive"] < 1) \
                                     and not ((self.type == "Power" or self.type == "Spell") and (
                                         target.marks["Evasive"] > 1 or (
                                         target.ID != self.ID and target.marks["Enemy Evasive"] > 1)))) \
                                 or (targetType == "Amulet" and (
                                 target.ID == self.ID or target.marks["Enemy Effect Evasive"] < 1) \
                                     and not (self.type == "Spell" and target.marks["Evasive"] > 1))
                             )
            if not selectable: return False
        return True
