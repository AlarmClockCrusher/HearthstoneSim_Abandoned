from SV_CardTypes import *
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
                    if isinstance(minion, SVMinion) and minion.keyWords["Free Evolve"] > 0:
                        hasFree = True
                        break
                return hasFree
        return False

    def targetCorrect(self, target, choice=0):
        if target.type == "Minion" and target.ID == self.ID and target.onBoard \
                and isinstance(target, SVMinion) and target.status["Evolved"] < 1 \
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


"""Mana 1 cards"""


class AirboundBarrage(SVSpell):
    Class, name = "Forestcraft", "Airbound Barrage"
    requireTarget, mana = True, 1
    index = "SV_Basic~Forestcraft~Spell~1~Airbound Barrage"
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
            self.entity.Game.killMinion(None, self.entity)


class Draw2Cards(Deathrattle_Minion):
    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        PRINT(self.entity.Game, "Deathrattle: Draw 2 cards triggers.")
        self.entity.Game.Hand_Deck.drawCard(self.entity.ID)
        self.entity.Game.Hand_Deck.drawCard(self.entity.ID)


class SellswordLucius(SVMinion):
    Class, race, name = "Swordcraft", "", "Sellsword Lucius"
    mana, attack, health = 1, 1, 1
    index = "SV_Basic~Swordcraft~1~1~1~Minion~None~Sellsword Lucius~Enhance~Fanfare"
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


class VesperWitchhunter(SVMinion):
    Class, race, name = "Runecraft", "", "Vesper, Witchhunter"
    mana, attack, health = 4, 3, 3
    index = "SV_Basic~Runecraft~4~3~3~Minion~None~Vesper, Witchhunter~Accelerate~Fanfare"
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


"""Mana 6 cards"""


class Terrorformer(SVMinion):
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

    def effectCanTrigger(self):
        self.effectViable = self.fusionMaterials > 1

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
            self.Game.killMinion(self, target[0])
        return target


"""Mana 10 cards"""


class RuinwebSpider_Amulet(Amulet):
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
    index = "SV_Basic~Bloodcraft~Minion~10~5~10~None~Ruinweb Spider~Crystallize"
    requireTarget, keyWord, description = False, "", "Crystallize 2; Countdown 10 During you turn, whenever an Amulet enters your board, reduce this Amulets countdown by 1. Last Words: Summon a Ruinweb Spider"
    crystallizeAmulet = RuinwebSpider_Amulet
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


class Goblin(SVMinion):
    Class, race, name = "Neutral", "", "Goblin"
    mana, attack, health = 1, 1, 2
    index = "SV_Basic~Neutral~Minion~1~1~2~None~Goblin"
    requireTarget, keyWord, description = False, "", ""
    attackAdd, healthAdd = 2, 2


class Fighter(SVMinion):
    Class, race, name = "Neutral", "", "Fighter"
    mana, attack, health = 2, 2, 2
    index = "SV_Basic~Neutral~Minion~2~2~2~None~Fighter"
    requireTarget, keyWord, description = False, "", ""
    attackAdd, healthAdd = 2, 2


class WellofDestiny(Amulet):
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


class MercenaryDrifter(SVMinion):
    Class, race, name = "Neutral", "", "Mercenary Drifter"
    mana, attack, health = 3, 3, 2
    index = "SV_Basic~Neutral~Minion~3~3~2~None~Mercenary Drifter"
    requireTarget, keyWord, description = False, "", ""
    attackAdd, healthAdd = 2, 2


class HarnessedFlame(SVMinion):
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


class HarnessedGlass(SVMinion):
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


class FlameandGlass(SVMinion):
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


class Goliath(SVMinion):
    Class, race, name = "Neutral", "", "Goliath"
    mana, attack, health = 4, 3, 4
    index = "SV_Basic~Neutral~Minion~4~3~4~None~Goliath"
    requireTarget, keyWord, description = False, "", ""
    attackAdd, healthAdd = 2, 2


class AngelicSwordMaiden(SVMinion):
    Class, race, name = "Neutral", "", "Angelic Sword Maiden"
    mana, attack, health = 5, 2, 6
    index = "SV_Basic~Neutral~Minion~5~2~6~None~Angelic Sword Maiden~Taunt"
    requireTarget, keyWord, description = False, "Taunt", "Ward."
    attackAdd, healthAdd = 2, 2


"""Forestcraft cards"""


class Fairy(SVMinion):
    Class, race, name = "Forestcraft", "", "Fairy"
    mana, attack, health = 1, 1, 1
    index = "SV_Basic~Forestcraft~Minion~1~1~1~None~Fairy~Uncollectible"
    requireTarget, keyWord, description = False, "", ""
    attackAdd, healthAdd = 2, 2


class WaterFairy(SVMinion):
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


class FairyWhisperer(SVMinion):
    Class, race, name = "Forestcraft", "", "Fairy Whisperer"
    mana, attack, health = 2, 1, 1
    index = "SV_Basic~Forestcraft~Minion~2~1~1~None~Fairy Whisperer~Battlecry"
    requireTarget, keyWord, description = False, "", "Fanfare: Put 2 Fairies into your hand."
    attackAdd, healthAdd = 2, 2

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        PRINT(self.Game, "Fairy Whisperer's Fanfare put a Fairy into your hand.")
        self.Game.Hand_Deck.addCardtoHand([Fairy for i in range(2)], self.ID, "CreateUsingType")
        return None


class ElfGuard(SVMinion):
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


class ElfMetallurgist(SVMinion):
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


class SylvanJustice(SVSpell):
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


class DarkElfFaure(SVMinion):
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


class Okami(SVMinion):
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


class RoseGardener(SVMinion):
    Class, race, name = "Forestcraft", "", "Rose Gardener"
    mana, attack, health = 4, 4, 3
    index = "SV_Basic~Forestcraft~Minion~4~4~3~None~Rose Gardener"
    requireTarget, keyWord, description = False, "", ""
    attackAdd, healthAdd = 1, 1

    def inHandEvolving(self, target=None):
        if target and target.onBoard:
            PRINT(self.Game, f"Rose Gardener's Evolve returns {target.name} to owner's hand.")
            self.Game.returnMiniontoHand(target, deathrattlesStayArmed=False)


class Treant(SVMinion):
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


class ElfTracker(SVMinion):
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


class MagnaBotanist(SVMinion):
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


class SteelcladKnight(SVMinion):
    Class, race, name = "Swordcraft", "Officer", "Steelclad Knight"
    mana, attack, health = 2, 2, 2
    index = "SV_Basic~Swordcraft~Minion~2~2~2~Officer~Steelclad Knight~Uncollectible"
    requireTarget, keyWord, description = False, "", ""
    attackAdd, healthAdd = 2, 2


class HeavyKnight(SVMinion):
    Class, race, name = "Swordcraft", "Officer", "Heavy Knight"
    mana, attack, health = 1, 1, 2
    index = "SV_Basic~Swordcraft~Minion~1~1~2~Officer~Heavy Knight~Uncollectible"
    requireTarget, keyWord, description = False, "", ""
    attackAdd, healthAdd = 2, 2


class Knight(SVMinion):
    Class, race, name = "Swordcraft", "Officer", "Knight"
    mana, attack, health = 1, 1, 1
    index = "SV_Basic~Swordcraft~Minion~1~1~1~Officer~Knight~Uncollectible"
    requireTarget, keyWord, description = False, "", ""
    attackAdd, healthAdd = 2, 2


class ShieldGuardian(SVMinion):
    Class, race, name = "Swordcraft", "Officer", "Shield Guardian"
    mana, attack, health = 1, 1, 1
    index = "SV_Basic~Swordcraft~Minion~1~1~1~Officer~Shield Guardian~Taunt~Uncollectible"
    requireTarget, keyWord, description = False, "Taunt", "Ward"
    attackAdd, healthAdd = 2, 2


class Quickblader(SVMinion):
    Class, race, name = "Swordcraft", "Officer", "Quickblader"
    mana, attack, health = 1, 1, 1
    index = "SV_Basic~Swordcraft~Minion~1~1~1~Officer~Quickblader~Charge"
    requireTarget, keyWord, description = False, "Charge", "Storm"
    attackAdd, healthAdd = 2, 2


class OathlessKnight(SVMinion):
    Class, race, name = "Swordcraft", "Officer", "Oathless Knight"
    mana, attack, health = 2, 1, 1
    index = "SV_Basic~Swordcraft~Minion~2~1~1~Officer~Oathless Knight~Battlecry"
    requireTarget, keyWord, description = False, "", "Fanfare: Summon a Knight."
    attackAdd, healthAdd = 2, 2

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        PRINT(self, "Oathless Knight's Fanfare summons a 1/1 Knight.")
        self.Game.summonMinion([Knight(self.Game, self.ID)], (-11, "totheRightEnd"), self.ID)
        return None


class KunoichiTrainee(SVMinion):
    Class, race, name = "Swordcraft", "Officer", "Kunoichi Trainee"
    mana, attack, health = 2, 2, 1
    index = "SV_Basic~Swordcraft~Minion~2~2~1~Officer~Kunoichi Trainee~Stealth"
    requireTarget, keyWord, description = False, "Stealth", "Ambush."
    attackAdd, healthAdd = 2, 2


class AsceticKnight(SVMinion):
    Class, race, name = "Swordcraft", "Officer", "Ascetic Knight"
    mana, attack, health = 3, 1, 2
    index = "SV_Basic~Swordcraft~Minion~3~1~2~Officer~Ascetic Knight~Battlecry"
    requireTarget, keyWord, description = False, "", "Fanfare: Summon a Heavy Knight."
    attackAdd, healthAdd = 2, 2

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        PRINT(self, "Ascetic Knight's Fanfare summons a 1/2 Heavy Knight.")
        self.Game.summonMinion([HeavyKnight(self.Game, self.ID)], (-11, "totheRightEnd"), self.ID)
        return None


class ForgeWeaponry(SVSpell):
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


class WhiteGeneral(SVMinion):
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


class FloralFencer(SVMinion):
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


class RoyalBanner(Amulet):
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
        PRINT(self.entity.Game, f"A friendly minion {subject.name} is summoned and Royal Banner gives it +1/+0.")
        subject.buffDebuff(1, 0)


class NinjaMaster(SVMinion):
    Class, race, name = "Swordcraft", "Officer", "Ninja Master"
    mana, attack, health = 5, 4, 4
    index = "SV_Basic~Swordcraft~Minion~5~4~4~Officer~Ninja Master~Stealth"
    requireTarget, keyWord, description = False, "Stealth", "Ambush."
    attackAdd, healthAdd = 2, 2


class SageCommander(SVMinion):
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


class ClayGolem(SVMinion):
    Class, race, name = "Runecraft", "", "Clay Golem"
    mana, attack, health = 2, 2, 2
    index = "SV_Basic~Runecraft~Minion~2~2~2~None~Clay Golem~Uncollectible"
    requireTarget, keyWord, description = False, "", ""
    attackAdd, healthAdd = 2, 2


class Snowman(SVMinion):
    Class, race, name = "Runecraft", "", "Snowman"
    mana, attack, health = 1, 1, 1
    index = "SV_Basic~Runecraft~Minion~1~1~1~None~Snowman~Uncollectible"
    requireTarget, keyWord, description = False, "", ""
    attackAdd, healthAdd = 2, 2


class EarthEssence(Amulet):
    Class, race, name = "Runecraft", "Earth Sigil", "Earth Essence"
    mana = 1
    index = "SV_Basic~Runecraft~Amulet~1~Earth Sigil~Earth Essence~Uncollectible"
    requireTarget, description = False, ""


class GuardianGolem(SVMinion):
    Class, race, name = "Runecraft", "", "Guardian Golem"
    mana, attack, health = 4, 3, 3
    index = "SV_Basic~Runecraft~Minion~4~3~3~None~Guardian Golem~Taunt~Uncollectible"
    requireTarget, keyWord, description = False, "Taunt", "Ward."
    attackAdd, healthAdd = 2, 2


class ScrapGolem(SVMinion):
    Class, race, name = "Runecraft", "", "Scrap Golem"
    mana, attack, health = 1, 0, 2
    index = "SV_Basic~Runecraft~Minion~1~0~2~None~Scrap Golem~Taunt~Uncollectible"
    requireTarget, keyWord, description = False, "Taunt", "Ward."
    attackAdd, healthAdd = 2, 2


class ConjureGuardian(SVSpell):
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


class Insight(SVSpell):
    Class, name = "Runecraft", "Insight"
    requireTarget, mana = False, 1
    index = "SV_Basic~Runecraft~Spell~1~Insight"
    description = "Draw a card."

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        PRINT(self, "Insight let player draw a card.")
        self.Game.Hand_Deck.drawCard(self.ID)
        return None


class SammyWizardsApprentice(SVMinion):
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


class MagicMissile(SVSpell):
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


class ConjureGolem(SVSpell):
    Class, name = "Runecraft", "Conjure Golem"
    requireTarget, mana = False, 2
    index = "SV_Basic~Runecraft~Spell~2~Conjure Golem"
    description = "Summon a Clay Golem."

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        PRINT(self, "Conjure Golem summons a Clay Golem")
        self.Game.summonMinion([ClayGolem(self.Game, self.ID)], (-11, "totheRightEnd"), self.ID)
        return None


class WindBlast(SVSpell):
    Class, name = "Runecraft", "Wind Blast"
    requireTarget, mana = True, 2
    index = "SV_Basic~Runecraft~Spell~2~Wind Blast~Spellboost"
    description = "Deal 1 damage to an enemy follower. Spellboost: Deal 1 more."

    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.trigsHand = [Trig_Spellboost(self)]
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


class SummonSnow(SVSpell):
    Class, name = "Runecraft", "Summon Snow"
    requireTarget, mana = False, 3
    index = "SV_Basic~Runecraft~Spell~2~Summon Snow~Spellboost"
    description = "Summon 1 Snowman. Spellboost: Summon 1 more."

    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.trigsHand = [Trig_Spellboost(self)]
        self.progress = 0

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        PRINT(self, "Insight let player draw a card.")
        self.Game.summonMinion([Snowman(self.Game, self.ID) for i in range(1 + self.progress)], (-11, "totheRightEnd"),
                               self.ID)
        return None


class DemonflameMage(SVMinion):
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


class ConjureTwosome(SVSpell):
    Class, name = "Runecraft", "Conjure Twosome"
    requireTarget, mana = False, 4
    index = "SV_Basic~Runecraft~Spell~4~Conjure Twosome"
    description = "Summon a Clay Golem."

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        PRINT(self, "Conjure Twosome summons two Clay Golems")
        self.Game.summonMinion([ClayGolem(self.Game, self.ID), ClayGolem(self.Game, self.ID)], (-11, "totheRightEnd"),
                               self.ID)
        return None


class LightningShooter(SVMinion):
    Class, race, name = "Runecraft", "", "Lightning Shooter"
    mana, attack, health = 5, 3, 3
    index = "SV_Basic~Runecraft~Minion~5~3~3~None~Lightning Shooter~Battlecry~Spellboost"
    requireTarget, keyWord, description = True, "", "Fanfare: Deal 1 damage to an enemy follower. Spellboost: Deal 1 more."
    attackAdd, healthAdd = 2, 2

    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.trigsHand = [Trig_Spellboost(self)]
        self.progress = 0

    def targetExists(self, choice=0):
        return self.selectableEnemyMinionExists()

    def targetCorrect(self, target, choice=0):
        return target.type == "Minion" and target.ID != self.ID and target.onBoard

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        numCardsPlayed = len(self.Game.Counters.cardsPlayedThisTurn[self.ID]["Indices"])
        if numCardsPlayed >= 2:
            self.dealsDamage(target, 1 + self.progress)
            PRINT(self.Game, f"Lightning Shooter deals {1 + self.progress} damage to {target.name}")
        return None


class FieryEmbrace(SVSpell):
    Class, name = "Runecraft", "Fiery Embrace"
    requireTarget, mana = True, 8
    index = "SV_Basic~Runecraft~Spell~8~Fiery Embrace~Spellboost"
    description = "Spellboost: Subtract 1 from the cost of this card. Destroy an enemy follower."

    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.trigsHand = [Trig_Spellboost(self)]
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
            self.Game.killMinion(self, target)
        return target


class FlameDestroyer(SVMinion):
    Class, race, name = "Runecraft", "", "Flame Destroyer"
    mana, attack, health = 10, 7, 7
    index = "SV_Basic~Runecraft~Minion~10~7~7~None~Flame Destroyer~Spellboost"
    requireTarget, keyWord, description = True, "", "Spellboost: Subtract 1 from the cost of this card."
    attackAdd, healthAdd = 2, 2

    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.trigsHand = [Trig_Spellboost(self)]
        self.progress = 0

    def selfManaChange(self):
        if self.inHand:
            self.mana -= self.progress
            self.mana = max(self.mana, 0)


"""Drangoncraft cards"""


class BuffAura_Overflow(AuraDealer_toMinion):
    def __init__(self, entity):
        self.entity = entity
        self.signals, self.auraAffected = ["ManaXtlsCheck"], []

    def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.onBoard and ID == self.entity.ID

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        isOverflow = self.entity.Game.Manas.manasUpper[self.entity.ID] >= 7
        if isOverflow == False and self.entity.activated:
            self.entity.activated = False
            for minion, aura_Receiver in fixedList(self.auraAffected):
                aura_Receiver.effectClear()
            self.auraAffected = []
        elif isOverflow and self.entity.activated == False:
            self.entity.activated = True
            self.applies(self.entity)

    def applies(self, subject):
        if subject == self.entity:
            aura_Receiver = BuffAura_Receiver(subject, self, 2, 0)
            aura_Receiver.effectStart()

    def auraAppears(self):
        isOverflow = self.entity.Game.Manas.manasUpper[self.entity.ID] >= 7
        if isOverflow:
            self.entity.activated = True
            self.applies(self.entity)
        try:
            self.entity.Game.trigsBoard[self.entity.ID]["ManaXtlsCheck"].append(self)
        except:
            self.entity.Game.trigsBoard[self.entity.ID]["ManaXtlsCheck"] = [self]

    def selfCopy(self, recipient):  # The recipientMinion is the minion that deals the Aura.
        return type(self)(recipient)
    # 可以通过AuraDealer_toMinion的createCopy方法复制


class BlazingBreath(SVSpell):
    Class, name = "Drangoncraft", "Blazing Breath"
    requireTarget, mana = True, 1
    index = "SV_Basic~Drangoncraft~Spell~1~Blazing Breath"
    description = "Deal 2 damage to an enemy follower."

    def available(self):
        return self.selectableEnemyMinionExists()

    def targetCorrect(self, target, choice=0):
        if isinstance(target, list): target = target[0]
        return target.type == "Minion" and target.ID != self.ID and target.onBoard

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if target:
            if isinstance(target, list): target = target[0]
            damage = (2 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
            PRINT(self.Game, f"Blazing Breath deals {damage} damage to enemy {target.name}")
            self.dealsDamage(target, damage)
        return target


class Dragonrider(SVMinion):
    Class, race, name = "Drangoncraft", "", "Dragonrider"
    mana, attack, health = 2, 2, 2
    index = "SV_Basic~Drangoncraft~Minion~2~2~2~None~Dragonrider"
    requireTarget, keyWord, description = False, "", "Gain +2/+0 if Overflow is active for you."
    attackAdd, healthAdd = 2, 2

    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.auras["Buff Aura"] = BuffAura_Dragonrider(self)
        self.activated = False


class BuffAura_Dragonrider(BuffAura_Overflow):
    def applies(self, subject):
        if subject == self.entity:
            aura_Receiver = BuffAura_Receiver(subject, self, 2, 0)
            aura_Receiver.effectStart()


class DragonOracle(SVSpell):
    Class, name = "Drangoncraft", "Dragon Oracle"
    requireTarget, mana = False, 2
    index = "SV_Basic~Drangoncraft~Spell~2~Dragon Oracle"
    description = "Gain an empty play point orb. Draw a card if Overflow is active for you."

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        PRINT(self.Game, "Dragon Oracle gives an empty play point orb")
        if self.Game.Manas.manasUpper[self.ID] >= 7:
            PRINT(self, "Dragon Oracle let player draw a card.")
            self.Game.Hand_Deck.drawCard(self.ID)
        self.Game.Manas.gainEmptyManaCrystal(1, self.ID)
        return None


class FirstbornDragon(SVMinion):
    Class, race, name = "Drangoncraft", "", "Firstborn Dragon"
    mana, attack, health = 3, 2, 3
    index = "SV_Basic~Drangoncraft~Minion~3~2~3~None~Firstborn Dragon"
    requireTarget, keyWord, description = False, "", "Gain Ward if Overflow is active for you."
    attackAdd, healthAdd = 2, 2

    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.auras["Buff Aura"] = BuffAura_FirstbornDragon(self)
        self.activated = False


class BuffAura_FirstbornDragon(BuffAura_Overflow):
    def applies(self, subject):
        if subject.Game.availableWeapon(subject.ID):
            aura_Receiver = HasAura_Receiver(subject, self, "Taunt")
            aura_Receiver.effectStart()
        else:
            for minion, aura_Receiver in self.auraAffected:
                aura_Receiver.effectClear()


class DeathDragon(SVMinion):
    Class, race, name = "Drangoncraft", "", "Death Dragon"
    mana, attack, health = 4, 4, 4
    index = "SV_Basic~Drangoncraft~Minion~4~4~4~None~Death Dragon"
    requireTarget, keyWord, description = False, "", " "
    attackAdd, healthAdd = 2, 2


class SerpentWrath(SVSpell):
    Class, name = "Drangoncraft", "Serpent Wrath"
    requireTarget, mana = True, 4
    index = "SV_Basic~Drangoncraft~Spell~4~Serpent Wrath"
    description = "Deal 6 damage to an enemy follower."

    def available(self):
        return self.selectableEnemyMinionExists()

    def targetCorrect(self, target, choice=0):
        if isinstance(target, list): target = target[0]
        return target.type == "Minion" and target.ID != self.ID and target.onBoard

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if target:
            if isinstance(target, list): target = target[0]
            damage = (6 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
            PRINT(self.Game, f"Serpent Wrath deals {damage} damage to enemy {target.name}")
            self.dealsDamage(target, damage)
        return target


class DisasterDragon(SVMinion):
    Class, race, name = "Drangoncraft", "", "Disaster Dragon"
    mana, attack, health = 5, 4, 5
    index = "SV_Basic~Drangoncraft~Minion~5~4~5~None~Disaster Dragon"
    requireTarget, keyWord, description = False, "", "Strike: Gain +2/+0 until the end of the turn."
    attackAdd, healthAdd = 2, 2

    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.trigsBoard = [Trig_DisasterDragon(self)]
        self.progress = 0


class Trig_DisasterDragon(TrigBoard):
    def __init__(self, entity):
        self.blank_init(entity, ["MinionAttackingMinion", "MinionAttackingHero"])

    def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.onBoard and subject.ID == self.entity.ID

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        PRINT(self.entity.Game, "Disaster Dragon gains +2/+0 this turn.")
        self.entity.buffDebuff(2, 0, "EndofTurn")


class Dragonguard(SVMinion):
    Class, race, name = "Drangoncraft", "", "Dragonguard"
    mana, attack, health = 6, 5, 6
    index = "SV_Basic~Drangoncraft~Minion~6~5~6~None~Dragonguard"
    requireTarget, keyWord, description = False, "", "Gain Ward if Overflow is active for you."
    attackAdd, healthAdd = 2, 2

    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.auras["Buff Aura"] = BuffAura_Dragonguard(self)
        self.activated = False


class BuffAura_Dragonguard(BuffAura_Overflow):
    def applies(self, subject):
        if subject.Game.availableWeapon(subject.ID):
            aura_Receiver = HasAura_Receiver(subject, self, "Taunt")
            aura_Receiver.effectStart()
        else:
            for minion, aura_Receiver in self.auraAffected:
                aura_Receiver.effectClear()


class DreadDragon(SVMinion):
    Class, race, name = "Drangoncraft", "", "Dread Dragon"
    mana, attack, health = 7, 4, 4
    index = "SV_Basic~Drangoncraft~Minion~7~4~4~None~Dread Dragon~Battlecry~Spellboost"
    requireTarget, keyWord, description = True, "", "Fanfare: Deal 4 damage to an enemy follower."
    attackAdd, healthAdd = 2, 2

    def targetExists(self, choice=0):
        return self.selectableEnemyMinionExists()

    def targetCorrect(self, target, choice=0):
        return target.type == "Minion" and target.ID != self.ID and target.onBoard

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        numCardsPlayed = len(self.Game.Counters.cardsPlayedThisTurn[self.ID]["Indices"])
        if numCardsPlayed >= 2:
            self.dealsDamage(target, 4)
            PRINT(self.Game, f"Dread Dragon deals 4 damage to {target.name}")
        return None


class Whirlwind(SVSpell):
    Class, name = "Drangoncraft", "Whirlwind"
    mana = False
    index = "SV_Basic~Drangoncraft~Spell~7~Whirlwind"
    requireTarget, keyWord, description = False, "", "Deal 4 damage to all followers."

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        damage = (4 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
        targets = self.Game.minionsonBoard(1) + self.Game.minionsonBoard(2)
        PRINT(self.Game, f"Whirlwind deals {damage} damage to all minions.")
        self.dealsAOE(targets, [damage for minion in targets])
        return None


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
    "SV_Basic~Bloodcraft~2~Amulet~None~Ruinweb Spider~Last Words": RuinwebSpider_Amulet,
    "SV_Basic~Bloodcraft~Minion~10~11~8~Dragon~XI. Erntz, Justice~Ward": XIErntzJustice,
    "SV_Basic~Forestcraft~Spell~1~Airbound Barrage": AirboundBarrage,
}
