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


SVClasses = ["Forestcraft", "Swordcraft", "Runecraft", "Dragoncraft", "Shadowcraft", "Bloodcraft", "Havencraft",
             "Portalcraft"]
Classes = ["Demon Hunter", "Druid", "Hunter", "Mage", "Monk", "Paladin", "Priest", "Rogue", "Shaman", "Warlock",
           "Warrior",
           "Forestcraft", "Swordcraft", "Runecraft", "Dragoncraft", "Shadowcraft", "Bloodcraft", "Havencraft",
           "Portalcraft"]
ClassesandNeutral = ["Demon Hunter", "Druid", "Hunter", "Mage", "Monk", "Paladin", "Priest", "Rogue", "Shaman",
                     "Warlock", "Warrior", "Neutral", "Forestcraft", "Swordcraft", "Runecraft", "Dragoncraft",
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
                for minion in self.Game.minionsAlive(self.ID):
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
        if target.marks["Free Evolve"] < 1:
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


"""Neutral cards"""


class TrigInvocation(TrigDeck):
    def __init__(self, entity):
        self.blank_init(entity, ["TurnStarts"])

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        if self.entity.Game.space(self.entity.ID) > 0:
            curGame = self.entity.Game
            if curGame.mode == 0:
                if curGame.guides:
                    i = curGame.guides.pop(0)
                else:
                    minions = [i for i, card in enumerate(curGame.Hand_Deck.decks[self.entity.ID]) if
                               card.type == "Minion" and card.name == self.entity.name]
                    i = npchoice(minions) if minions and curGame.space(self.entity.ID) > 0 else -1
                    curGame.fixedGuides.append(i)
                if i > -1:
                    minion = curGame.summonfromDeck(i, self.entity.ID, -1, self.entity.ID)
                    PRINT(self.entity.Game, f"{minion.name} is summoned from player {self.entity.ID}'s deck.")
                    minion.afterInvocation(signal, ID, subject, target, number, comment)


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
                self.entity.disappears(deathrattlesStayArmed=False)
                self.entity.Game.removeMinionorWeapon(self.entity)
                self.entity.Game.summon([FlameandGlass(self.entity.Game, self.entity.ID)], (-1, "totheRightEnd"),
                                        self.entity.ID)
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
                self.entity.disappears(deathrattlesStayArmed=False)
                self.entity.Game.removeMinionorWeapon(self.entity)
                self.entity.Game.summon([FlameandGlass(self.entity.Game, self.entity.ID)], (-1, "totheRightEnd"),
                                        self.entity.ID)
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
        self.deathrattles = [Deathrattle_WaterFairy(self)]


class Deathrattle_WaterFairy(Deathrattle_Minion):
    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        PRINT(self.entity.Game, "Water Fairy's Last Words put a Fairy into your hand.")
        self.entity.Game.Hand_Deck.addCardtoHand(Fairy, self.entity.ID, "type")


class FairyWhisperer(SVMinion):
    Class, race, name = "Forestcraft", "", "Fairy Whisperer"
    mana, attack, health = 2, 1, 1
    index = "SV_Basic~Forestcraft~Minion~2~1~1~None~Fairy Whisperer~Battlecry"
    requireTarget, keyWord, description = False, "", "Fanfare: Put 2 Fairies into your hand."
    attackAdd, healthAdd = 2, 2

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        PRINT(self.Game, "Fairy Whisperer's Fanfare put a Fairy into your hand.")
        self.Game.Hand_Deck.addCardtoHand([Fairy for i in range(2)], self.ID, "type")
        return None


class ElfGuard(SVMinion):
    Class, race, name = "Forestcraft", "", "Elf Guard"
    mana, attack, health = 2, 1, 3
    index = "SV_Basic~Forestcraft~Minion~2~1~3~None~Elf Guard~Battlecry"
    requireTarget, keyWord, description = False, "", "Fanfare: Gain +1/+1 and Ward if at least 2 other cards were played this turn."
    attackAdd, healthAdd = 2, 2

    def effectCanTrigger(self):
        self.effectViable = self.Game.combCards(self.ID) >= 2

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        numCardsPlayed = self.Game.combCards(self.ID)
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
        return self.Game.combCards(self.ID) >= 2 and not self.targets

    def effectCanTrigger(self):
        self.effectViable = self.Game.combCards(self.ID) >= 2

    def targetExists(self, choice=0):
        return self.selectableEnemyMinionExists()

    def targetCorrect(self, target, choice=0):
        if isinstance(target, list): target = target[0]
        return target.type == "Minion" and target.ID != self.ID and target.onBoard

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        numCardsPlayed = self.Game.combCards(self.ID)
        if numCardsPlayed >= 2:
            if isinstance(target, list): target = target[0]
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
        if isinstance(target, list): target = target[0]
        return target.type == "Minion" and target.onBoard and target.ID != self.ID

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if target:
            if isinstance(target, list): target = target[0]
            damage = (2 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
            self.dealsDamage(target, damage)
            PRINT(self.Game,
                  f"Sylvan Justice deals {damage} damage to {target.name} and put a Fairy into your hand.")
            self.Game.Hand_Deck.addCardtoHand(Fairy, self.ID, "type")
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
        self.entity.Game.Hand_Deck.addCardtoHand(Fairy, self.entity.ID, "type")


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

    # TODO need target

    def inHandEvolving(self, target=None):
        if isinstance(target, list): target = target[0]
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
        self.effectViable = self.Game.combCards(self.ID) >= 2

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        numCardsPlayed = self.Game.combCards(self.ID)
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
                    objs = curGame.minionsAlive(side)
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
        self.effectViable = self.Game.combCards(self.ID) >= 2

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        numCardsPlayed = self.Game.combCards(self.ID)
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


class GildedBlade(SVSpell):
    Class, name = "Swordcraft", "Gilded Blade"
    requireTarget, mana = True, 1
    index = "SV_Basic~Swordcraft~Spell~1~Gilded Blade~Uncollectible"
    description = "Deal 1 damage to an enemy follower."

    def available(self):
        return self.selectableEnemyMinionExists()

    def targetCorrect(self, target, choice=0):
        if isinstance(target, list): target = target[0]
        return target.cardType == "Minion" and target.ID != self.ID and target.onBoard

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if target:
            if isinstance(target, list): target = target[0]
            damage = (1 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
            PRINT(self.Game, f"Gilded Blade deals {damage} damage to minion {target.name}")
            self.dealsDamage(target, damage)
        return target


class GildedGoblet(SVSpell):
    Class, name = "Swordcraft", "Gilded Goblet"
    requireTarget, mana = True, 1
    index = "SV_Basic~Swordcraft~Spell~1~Gilded Goblet~Uncollectible"
    description = "Restore 2 defense to an ally."

    def targetCorrect(self, target, choice=0):
        if isinstance(target, list): target = target[0]
        return target.ID == self.ID and target.onBoard

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if target:
            if isinstance(target, list): target = target[0]
            heal = 2 * (2 ** self.countHealDouble())
            PRINT(self.Game, f"Gilded Goblet restores {heal} Health to {target.name}")
            self.restoresHealth(target, heal)


class GildedBoots(SVSpell):
    Class, name = "Swordcraft", "Gilded Boots"
    requireTarget, mana = True, 1
    index = "SV_Basic~Swordcraft~Spell~1~Gilded Boots~Uncollectible"
    description = "Give Rush to an allied follower."

    def available(self):
        return self.selectableFriendlyExists()

    def targetCorrect(self, target, choice=0):
        if isinstance(target, list): target = target[0]
        return target.cardType == "Minion" and target.ID == self.ID and target.onBoard

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if target:
            if isinstance(target, list): target = target[0]
            PRINT(self.Game, f"Gilded Boots gives minion {target.name} Rush")
            target.getsKeyword("Rush")
        return target


class GildedNecklace(SVSpell):
    Class, name = "Swordcraft", "Gilded Necklace"
    requireTarget, mana = True, 1
    index = "SV_Basic~Swordcraft~Spell~1~Gilded Necklace~Uncollectible"
    description = "Give +1/+1 to an allied follower."

    def available(self):
        return self.selectableFriendlyExists()

    def targetCorrect(self, target, choice=0):
        if isinstance(target, list): target = target[0]
        return target.cardType == "Minion" and target.ID == self.ID and target.onBoard

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if target:
            if isinstance(target, list): target = target[0]
            PRINT(self.Game, f"Gilded Necklace gives minion {target.name} +1/+1")
            target.buffDebuff(1, 1)
        return target


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
        PRINT(self.Game, "Oathless Knight's Fanfare summons a 1/1 Knight.")
        self.Game.summon([Knight(self.Game, self.ID)], (-1, "totheRightEnd"), self.ID)
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
        PRINT(self.Game, "Ascetic Knight's Fanfare summons a 1/2 Heavy Knight.")
        self.Game.summon([HeavyKnight(self.Game, self.ID)], (-1, "totheRightEnd"), self.ID)
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
    Class, race, name = "Swordcraft", "Commander", "White General"
    mana, attack, health = 4, 3, 3
    index = "SV_Basic~Swordcraft~Minion~4~3~3~Commander~White General~Battlecry"
    requireTarget, keyWord, description = True, "", "Fanfare: Give +2/+0 to an allied Officer follower."
    attackAdd, healthAdd = 2, 2

    def targetExists(self, choice=0):
        for minion in self.Game.minionsAlive(self.ID):
            if "Officer" in minion.race:
                return True
        return False

    def targetCorrect(self, target, choice=0):
        if isinstance(target, list): target = target[0]
        return target.type == "Minion" and target.ID == self.ID and target.onBoard and "Officer" in target.race

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if target:
            if isinstance(target, list): target = target[0]
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
        PRINT(self.Game, "Oathless Knight's Fanfare summons a 1/1 Knight and a 2/2 Steelclad Knight.")
        self.Game.summon([Knight(self.Game, self.ID), SteelcladKnight(self.Game, self.ID)],
                         (-1, "totheRightEnd"), self.ID)
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
        for minion in fixedList(self.Game.minionsonBoard(self.ID, self)):
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
        PRINT(self.Game, "Conjure Golem summons a Guardian Golem")
        self.Game.summon([GuardianGolem(self.Game, self.ID)], (-1, "totheRightEnd"), self.ID)
        return None


class Trig_Spellboost(TrigHand):
    def __init__(self, entity):
        self.blank_init(entity, ["Spellboost"])

    def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.inHand and subject.ID == self.entity.ID

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        self.entity.progress += 1
        self.entity.Game.Manas.calcMana_Single(self.entity)


class Insight(SVSpell):
    Class, name = "Runecraft", "Insight"
    requireTarget, mana = False, 1
    index = "SV_Basic~Runecraft~Spell~1~Insight"
    description = "Draw a card."

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        PRINT(self.Game, "Insight let player draw a card.")
        self.Game.Hand_Deck.drawCard(self.ID)
        return None


class SammyWizardsApprentice(SVMinion):
    Class, race, name = "Runecraft", "", "Sammy, Wizard's Apprentice"
    mana, attack, health = 2, 2, 2
    index = "SV_Basic~Runecraft~Minion~2~2~2~None~Sammy, Wizard's Apprentice~Battlecry"
    requireTarget, keyWord, description = False, "", "Fanfare: Give +1/+1 to all other allied followers."
    attackAdd, healthAdd = 2, 2

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        PRINT(self.Game, "Sammy, Wizard's Apprentice's Fanfare let both player draw a card.")
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
            PRINT(self.Game, f"Magic Missile deals {damage} damage to enemy {target.name} and let player draw a card.")
            self.dealsDamage(target, damage)
            self.Game.Hand_Deck.drawCard(self.ID)
        return target


class ConjureGolem(SVSpell):
    Class, name = "Runecraft", "Conjure Golem"
    requireTarget, mana = False, 2
    index = "SV_Basic~Runecraft~Spell~2~Conjure Golem"
    description = "Summon a Clay Golem."

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        PRINT(self.Game, "Conjure Golem summons a Clay Golem")
        self.Game.summon([ClayGolem(self.Game, self.ID)], (-1, "totheRightEnd"), self.ID)
        return None


class WindBlast(SVSpell):
    Class, name = "Runecraft", "Wind Blast"
    requireTarget, mana = True, 2
    index = "SV_Basic~Runecraft~Spell~2~Wind Blast~Spellboost"
    description = "Deal 1 damage to an enemy follower. Spellboost: Deal 1 more."

    def __init__(self, Game, ID):
        super().__init__(Game, ID)
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
        super().__init__(Game, ID)
        self.blank_init(Game, ID)
        self.trigsHand = [Trig_Spellboost(self)]
        self.progress = 0

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        PRINT(self.Game, f"Summon Snow summons {1 + self.progress} Snowmans")
        self.Game.summon([Snowman(self.Game, self.ID) for i in range(1 + self.progress)], (-1, "totheRightEnd"),
                         self.ID)
        return None


class DemonflameMage(SVMinion):
    Class, race, name = "Runecraft", "", "Demonflame Mage"
    mana, attack, health = 4, 3, 4
    index = "SV_Basic~Runecraft~Minion~4~3~4~None~Demonflame Mage"
    requireTarget, keyWord, description = False, "", ""
    attackAdd, healthAdd = 1, 1

    def inHandEvolving(self, target=None):
        PRINT(self.Game, "Demonflame Mage's Evolve deals 1 damage to all enemy followers")
        targets = self.Game.minionsonBoard(3 - self.ID)
        self.dealsAOE(targets, [1 for obj in targets])
        return None


class ConjureTwosome(SVSpell):
    Class, name = "Runecraft", "Conjure Twosome"
    requireTarget, mana = False, 4
    index = "SV_Basic~Runecraft~Spell~4~Conjure Twosome"
    description = "Summon a Clay Golem."

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        PRINT(self.Game, "Conjure Twosome summons two Clay Golems")
        self.Game.summon([ClayGolem(self.Game, self.ID), ClayGolem(self.Game, self.ID)], (-1, "totheRightEnd"),
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
        if isinstance(target, list): target = target[0]
        return target.type == "Minion" and target.ID != self.ID and target.onBoard

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if isinstance(target, list): target = target[0]
        self.dealsDamage(target, 1 + self.progress)
        PRINT(self.Game, f"Lightning Shooter deals {1 + self.progress} damage to {target.name}")
        return None


class FieryEmbrace(SVSpell):
    Class, name = "Runecraft", "Fiery Embrace"
    requireTarget, mana = True, 8
    index = "SV_Basic~Runecraft~Spell~8~Fiery Embrace~Spellboost"
    description = "Spellboost: Subtract 1 from the cost of this card. Destroy an enemy follower."

    def __init__(self, Game, ID):
        super().__init__(Game, ID)
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
    requireTarget, keyWord, description = False, "", "Spellboost: Subtract 1 from the cost of this card."
    attackAdd, healthAdd = 2, 2

    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.trigsHand = [Trig_Spellboost(self)]
        self.progress = 0

    def selfManaChange(self):
        if self.inHand:
            self.mana = max(self.mana - self.progress, 0)


"""Dragoncraft cards"""


class BuffAura_Overflow(AuraDealer_toMinion):
    def __init__(self, entity):
        self.entity = entity
        self.signals, self.auraAffected = ["ManaXtlsCheck"], []

    def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.onBoard and ID == self.entity.ID

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        isOverflow = self.entity.Game.isOverflow(self.entity.ID)
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
    Class, name = "Dragoncraft", "Blazing Breath"
    requireTarget, mana = True, 1
    index = "SV_Basic~Dragoncraft~Spell~1~Blazing Breath"
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
    Class, race, name = "Dragoncraft", "", "Dragonrider"
    mana, attack, health = 2, 2, 2
    index = "SV_Basic~Dragoncraft~Minion~2~2~2~None~Dragonrider"
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
    Class, name = "Dragoncraft", "Dragon Oracle"
    requireTarget, mana = False, 2
    index = "SV_Basic~Dragoncraft~Spell~2~Dragon Oracle"
    description = "Gain an empty play point orb. Draw a card if Overflow is active for you."

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        PRINT(self.Game, "Dragon Oracle gives an empty play point orb")
        if self.Game.isOverflow(self.ID):
            PRINT(self.Game, "Dragon Oracle let player draw a card.")
            self.Game.Hand_Deck.drawCard(self.ID)
        self.Game.Manas.gainEmptyManaCrystal(1, self.ID)
        return None


class FirstbornDragon(SVMinion):
    Class, race, name = "Dragoncraft", "", "Firstborn Dragon"
    mana, attack, health = 3, 2, 3
    index = "SV_Basic~Dragoncraft~Minion~3~2~3~None~Firstborn Dragon"
    requireTarget, keyWord, description = False, "", "Gain Ward if Overflow is active for you."
    attackAdd, healthAdd = 2, 2

    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.auras["Buff Aura"] = BuffAura_FirstbornDragon(self)
        self.activated = False


class BuffAura_FirstbornDragon(BuffAura_Overflow):
    def applies(self, subject):
        aura_Receiver = HasAura_Receiver(subject, self, "Taunt")
        aura_Receiver.effectStart()


class DeathDragon(SVMinion):
    Class, race, name = "Dragoncraft", "", "Death Dragon"
    mana, attack, health = 4, 4, 4
    index = "SV_Basic~Dragoncraft~Minion~4~4~4~None~Death Dragon"
    requireTarget, keyWord, description = False, "", " "
    attackAdd, healthAdd = 2, 2


class SerpentWrath(SVSpell):
    Class, name = "Dragoncraft", "Serpent Wrath"
    requireTarget, mana = True, 4
    index = "SV_Basic~Dragoncraft~Spell~4~Serpent Wrath"
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
    Class, race, name = "Dragoncraft", "", "Disaster Dragon"
    mana, attack, health = 5, 4, 5
    index = "SV_Basic~Dragoncraft~Minion~5~4~5~None~Disaster Dragon"
    requireTarget, keyWord, description = False, "", "Strike: Gain +2/+0 until the end of the turn."
    attackAdd, healthAdd = 2, 2

    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.trigsBoard = [Trig_DisasterDragon(self)]


class Trig_DisasterDragon(TrigBoard):
    def __init__(self, entity):
        self.blank_init(entity, ["MinionAttackingMinion", "MinionAttackingHero"])

    def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.onBoard and subject.ID == self.entity.ID

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        PRINT(self.entity.Game, "Disaster Dragon gains +2/+0 this turn.")
        self.entity.buffDebuff(2, 0, "EndofTurn")


class Dragonguard(SVMinion):
    Class, race, name = "Dragoncraft", "", "Dragonguard"
    mana, attack, health = 6, 5, 6
    index = "SV_Basic~Dragoncraft~Minion~6~5~6~None~Dragonguard"
    requireTarget, keyWord, description = False, "", "Gain Ward if Overflow is active for you."
    attackAdd, healthAdd = 2, 2

    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.auras["Buff Aura"] = BuffAura_Dragonguard(self)
        self.activated = False


class BuffAura_Dragonguard(BuffAura_Overflow):
    def applies(self, subject):
        aura_Receiver = HasAura_Receiver(subject, self, "Taunt")
        aura_Receiver.effectStart()


class DreadDragon(SVMinion):
    Class, race, name = "Dragoncraft", "", "Dread Dragon"
    mana, attack, health = 7, 4, 4
    index = "SV_Basic~Dragoncraft~Minion~7~4~4~None~Dread Dragon~Battlecry"
    requireTarget, keyWord, description = True, "", "Fanfare: Deal 4 damage to an enemy follower."
    attackAdd, healthAdd = 2, 2

    def targetExists(self, choice=0):
        return self.selectableEnemyMinionExists()

    def targetCorrect(self, target, choice=0):
        if isinstance(target, list): target = target[0]
        return target.type == "Minion" and target.ID != self.ID and target.onBoard

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if isinstance(target, list): target = target[0]
        self.dealsDamage(target, 4)
        PRINT(self.Game, f"Dread Dragon deals 4 damage to {target.name}")
        return None


class Conflagration(SVSpell):
    Class, name = "Dragoncraft", "Conflagration"
    mana, requireTarget = 7, False
    index = "SV_Basic~Dragoncraft~Spell~7~Conflagration"
    description = "Deal 4 damage to all followers."

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        damage = (4 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
        targets = self.Game.minionsonBoard(1) + self.Game.minionsonBoard(2)
        PRINT(self.Game, f"Conflagration deals {damage} damage to all minions.")
        self.dealsAOE(targets, [damage for minion in targets])
        return None


"""Shadowcraft cards"""


class Skeleton(SVMinion):
    Class, race, name = "Shadowcraft", "", "Skeleton"
    mana, attack, health = 1, 1, 1
    index = "SV_Basic~Shadowcraft~Minion~1~1~1~None~Skeleton~Uncollectible"
    requireTarget, keyWord, description = False, "", ""
    attackAdd, healthAdd = 2, 2


class Zombie(SVMinion):
    Class, race, name = "Shadowcraft", "", "Zombie"
    mana, attack, health = 2, 2, 2
    index = "SV_Basic~Shadowcraft~Minion~2~2~2~None~Zombie~Uncollectible"
    requireTarget, keyWord, description = False, "", ""
    attackAdd, healthAdd = 2, 2


class Lich(SVMinion):
    Class, race, name = "Shadowcraft", "", "Lich"
    mana, attack, health = 4, 4, 4
    index = "SV_Basic~Shadowcraft~Minion~4~4~4~None~Lich~Uncollectible"
    requireTarget, keyWord, description = False, "", ""
    attackAdd, healthAdd = 2, 2


class Ghost(SVMinion):
    Class, race, name = "Shadowcraft", "", "Ghost"
    mana, attack, health = 1, 1, 1
    index = "SV_Basic~Shadowcraft~Minion~1~1~1~None~Ghost~Charge~Uncollectible"
    requireTarget, keyWord, description = False, "Charge", "Storm. Banish this follower when it leaves play or when your turn ends."
    attackAdd, healthAdd = 2, 2

    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.marks["Disappear When Die"] = 1
        self.trigsBoard = [Trig_Ghost(self)]
        self.progress = 0


class Trig_Ghost(TrigBoard):
    def __init__(self, entity):
        self.blank_init(entity, ["TurnEnds"])

    def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.onBoard and ID == self.entity.ID

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        PRINT(self.entity.Game, "Ghost disappears.")
        self.entity.Game.banishMinion(self.entity, self.entity)


class SpartoiSergeant(SVMinion):
    Class, race, name = "Shadowcraft", "", "Spartoi Sergeant"
    mana, attack, health = 2, 2, 2
    index = "SV_Basic~Shadowcraft~Minion~2~2~2~None~Spartoi Sergeant~Battlecry"
    requireTarget, keyWord, description = False, "", "Fanfare: Gain 1 shadow."
    attackAdd, healthAdd = 2, 2

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        self.Game.Counters.shadows[self.ID] += 1
        PRINT(self.Game, f"Spartoi Sergeant's Fanfare gains 1 shadow.")
        return None


class Spectre(SVMinion):
    Class, race, name = "Shadowcraft", "", "Spectre"
    mana, attack, health = 2, 2, 1
    index = "SV_Basic~Shadowcraft~Minion~2~2~1~None~Spectre~Bane"
    requireTarget, keyWord, description = False, "Bane", "Bane."
    attackAdd, healthAdd = 2, 2


class UndyingResentment(SVSpell):
    Class, name = "Shadowcraft", "Undying Resentment"
    requireTarget, mana = True, 2
    index = "SV_Basic~Shadowcraft~Spell~2~Undying Resentment~Necromancy"
    description = "Deal 3 damage to an enemy follower. Necromancy (2): Deal 5 damage instead."

    def effectCanTrigger(self):
        self.effectViable = self.Game.Counters.shadows[self.ID] >= 2

    def available(self):
        return self.selectableEnemyMinionExists()

    def targetCorrect(self, target, choice=0):
        if isinstance(target, list): target = target[0]
        return target.type == "Minion" and target.ID != self.ID and target.onBoard

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if target:
            if isinstance(target, list): target = target[0]
            if self.Game.necromancy(self, self.ID, 2):
                damage = 5
            else:
                damage = 3
            damage = (damage + self.countSpellDamage()) * (2 ** self.countDamageDouble())
            PRINT(self.Game, f"Undying Resentment deals {damage} damage to enemy {target.name}")
            self.dealsDamage(target, damage)
        return target


class ApprenticeNecromancer(SVMinion):
    Class, race, name = "Shadowcraft", "", "Apprentice Necromancer"
    mana, attack, health = 3, 2, 3
    index = "SV_Basic~Shadowcraft~Minion~3~2~3~None~Apprentice Necromancer~Battlecry~Necromancy"
    requireTarget, keyWord, description = False, "", "Fanfare: Necromancy (4) - Summon a Zombie."
    attackAdd, healthAdd = 2, 2

    def effectCanTrigger(self):
        self.effectViable = self.Game.Counters.shadows[self.ID] >= 4

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if self.Game.necromancy(self, self.ID, 4):
            PRINT(self.Game, "Apprentice Necromancer's Fanfare summons a 2/2 Zombie.")
            self.Game.summon([Zombie(self.Game, self.ID)], (-1, "totheRightEnd"), self.ID)
        return None


class ElderSpartoiSoldier(SVMinion):
    Class, race, name = "Shadowcraft", "", "Elder Spartoi Soldier"
    mana, attack, health = 4, 4, 3
    index = "SV_Basic~Shadowcraft~Minion~4~4~3~None~Elder Spartoi Soldier~Battlecry"
    requireTarget, keyWord, description = False, "", "Fanfare: Gain 2 shadow."
    attackAdd, healthAdd = 2, 2

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        self.Game.Counters.shadows[self.ID] += 2
        PRINT(self.Game, f"Elder Spartoi Soldier's Fanfare gains 2 shadow.")
        return None


class PlayfulNecromancer(SVMinion):
    Class, race, name = "Shadowcraft", "", "Playful Necromancer"
    mana, attack, health = 4, 4, 3
    index = "SV_Basic~Shadowcraft~Minion~4~4~3~None~Playful Necromancer"
    requireTarget, keyWord, description = False, "", ""
    attackAdd, healthAdd = 1, 1

    def inHandEvolving(self, target=None):
        PRINT(self.Game, "Playful Necromancer's Evolve summons two 1/1 Ghosts.")
        self.Game.summon([Ghost(self.Game, self.ID), Ghost(self.Game, self.ID)], (-1, "totheRightEnd"), self.ID)


class HellsUnleasher(SVMinion):
    Class, race, name = "Shadowcraft", "", "Hell's Unleasher"
    mana, attack, health = 4, 1, 1
    index = "SV_Basic~Shadowcraft~Minion~4~1~1~None~Hell's Unleasher~Deathrattle"
    requireTarget, keyWord, description = False, "", "Last Words: Summon a Lich."
    attackAdd, healthAdd = 2, 2

    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.deathrattles = [Deathrattle_HellsUnleasher(self)]


class Deathrattle_HellsUnleasher(Deathrattle_Minion):
    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        PRINT(self.entity.Game, "Last Words: Summon a Lich.")
        self.entity.Game.summon([Lich(self.entity.Game, self.entity.ID)], (-1, "totheRightEnd"),
                                self.entity.ID)


class CalloftheVoid(SVSpell):
    Class, name = "Shadowcraft", "Call of the Void"
    requireTarget, mana = True, 4
    index = "SV_Basic~Shadowcraft~Spell~4~Call of the Void"
    description = "Destroy an enemy follower. Necromancy (4): Summon a Lich."

    def effectCanTrigger(self):
        self.effectViable = self.Game.Counters.shadows[self.ID] >= 4

    def available(self):
        return self.selectableEnemyMinionExists()

    def targetCorrect(self, target, choice=0):
        if isinstance(target, list): target = target[0]
        return target.type == "Minion" and target.ID != self.ID and target.onBoard

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if target:
            if isinstance(target, list): target = target[0]
            PRINT(self.Game, f"Call of the Void destroys enemy {target.name}")
            self.Game.killMinion(self, target)
            if self.Game.necromancy(self, self.ID, 4):
                PRINT(self.Game, "Call of the Void summons a 4/4 Lich.")
                self.Game.summon([Lich(self.Game, self.ID)], (-1, "totheRightEnd"), self.ID)
        return target


class Gravewaker(SVMinion):
    Class, race, name = "Shadowcraft", "", "Gravewaker"
    mana, attack, health = 5, 3, 3
    index = "SV_Basic~Shadowcraft~Minion~5~3~3~None~Gravewaker~Deathrattle"
    requireTarget, keyWord, description = False, "", "Last Words: Summon a Zombie."
    attackAdd, healthAdd = 2, 2

    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.deathrattles = [Deathrattle_Gravewaker(self)]


class Deathrattle_Gravewaker(Deathrattle_Minion):
    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        PRINT(self.entity.Game, "Last Words: Summon a Zombie.")
        self.entity.Game.summon([Zombie(self.entity.Game, self.entity.ID)], (-1, "totheRightEnd"),
                                self.entity.ID)


class GhostlyRider(SVMinion):
    Class, race, name = "Shadowcraft", "", "Ghostly Rider"
    mana, attack, health = 6, 5, 5
    index = "SV_Basic~Shadowcraft~Minion~6~5~5~None~Ghostly Rider~Deathrattle"
    requireTarget, keyWord, description = False, "Taunt", "Ward. Last Words: Give Ward to a random allied follower."
    attackAdd, healthAdd = 2, 2

    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.deathrattles = [Deathrattle_GhostlyRider(self)]


class Deathrattle_GhostlyRider(Deathrattle_Minion):
    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        curGame = self.entity.Game
        if curGame.mode == 0:
            PRINT(curGame, f"Last Words: Give Ward to a random allied follower.")
            if curGame.guides:
                i = curGame.guides.pop(0)
            else:
                minions = [minion.position for minion in curGame.minionsAlive(self.entity.ID)]
                i = npchoice(minions) if minions else -1
                curGame.fixedGuides.append(i)
            if i > -1:
                minion = curGame.minions[self.entity.ID][i]
                PRINT(curGame, f"{minion.name} gets Ward")
                minion.getsKeyword("Taunt")


class UndeadKing(SVMinion):
    Class, race, name = "Shadowcraft", "", "Undead King"
    mana, attack, health = 7, 4, 4
    index = "SV_Basic~Shadowcraft~Minion~7~4~4~None~Undead King~Deathrattle"
    requireTarget, keyWord, description = False, "", "Last Words: Summon twi Zombies."
    attackAdd, healthAdd = 2, 2

    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.deathrattles = [Deathrattle_UndeadKing(self)]


class Deathrattle_UndeadKing(Deathrattle_Minion):
    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        PRINT(self.entity.Game, "Last Words: Summon two Zombies.")
        self.entity.Game.summon([Zombie(self.entity.Game, self.entity.ID), Zombie(self.entity.Game, self.entity.ID)],
                                (-1, "totheRightEnd"),
                                self.entity.ID)


"""Bloodcraft cards"""


class ForestBat(SVMinion):
    Class, race, name = "Bloodcraft", "", "Forest Bat"
    mana, attack, health = 1, 1, 1
    index = "SV_Basic~Shadowcraft~Minion~1~1~1~None~Fores tBat~Uncollectible"
    requireTarget, keyWord, description = False, "", ""
    attackAdd, healthAdd = 2, 2


class Nightmare(SVMinion):
    Class, race, name = "Bloodcraft", "", "Nightmare"
    mana, attack, health = 2, 2, 2
    index = "SV_Basic~Bloodcraft~Minion~2~2~2~None~Nightmare~Battlecry"
    requireTarget, keyWord, description = False, "", "Fanfare: Gain +2/+0 if Vengeance is active for you."
    attackAdd, healthAdd = 2, 2

    def effectCanTrigger(self):
        self.effectViable = self.Game.isVengeance(self.ID)

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if self.Game.isVengeance(self.ID):
            PRINT(self.Game, "Nightmare's Fanfare gives it +2/+0")
            self.buffDebuff(2, 0)
        return None


class SweetfangVampire(SVMinion):
    Class, race, name = "Bloodcraft", "", "Sweetfang Vampire"
    mana, attack, health = 2, 1, 3
    index = "SV_Basic~Bloodcraft~Minion~2~1~3~None~Sweetfang Vampire~Drain"
    requireTarget, keyWord, description = False, "Drain", "Drain."
    attackAdd, healthAdd = 2, 2


class BloodPact(SVSpell):
    Class, name = "Bloodcraft", "Blood Pact"
    requireTarget, mana = False, 2
    index = "SV_Basic~Bloodcraft~Spell~2~Blood Pact"
    description = "Deal 2 damage to your leader. Draw 2 cards."

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        damage = (2 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
        PRINT(self.Game, f"Blood Pact deals {damage} damage your leader. Draw 2 cards.")
        self.dealsDamage(self.Game.heroes[self.ID], damage)
        self.Game.Hand_Deck.drawCard(self.ID)
        self.Game.Hand_Deck.drawCard(self.ID)
        return target


class RazoryClaw(SVSpell):
    Class, name = "Bloodcraft", "Razory Claw"
    requireTarget, mana = True, 2
    index = "SV_Basic~Bloodcraft~Spell~2~Razory Claw"
    description = "Deal 2 damage to your leader and 3 damage to an enemy."

    def available(self):
        return self.selectableEnemyExists()

    def targetCorrect(self, target, choice=0):
        if isinstance(target, list): target = target[0]
        return (target.type == "Minion" or target.type == "Hero") and target.ID != self.ID and target.onBoard

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if target:
            if isinstance(target, list): target = target[0]
            damage1 = (2 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
            damage2 = (3 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
            PRINT(self.Game,
                  f"Razory Claw deals {damage1} damage to your leader and deals {damage2} damage to enemy {target.name}")
            self.dealsDamage(self.Game.heroes[self.ID], damage1)
            self.dealsDamage(target, damage2)
        return target


class CrazedExecutioner(SVMinion):
    Class, race, name = "Bloodcraft", "", "Crazed Executioner"
    mana, attack, health = 3, 3, 3
    index = "SV_Basic~Bloodcraft~Minion~3~3~3~None~Crazed Executioner~Battlecry"
    requireTarget, keyWord, description = False, "", "Fanfare: Deal 2 damage to your leader."
    attackAdd, healthAdd = 2, 2

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        PRINT(self.Game, "Crazed Executioner's Fanfare deals 2 damage to your leader")
        self.dealsDamage(self.Game.heroes[self.ID], 2)
        return None


class DarkGeneral(SVMinion):
    Class, race, name = "Bloodcraft", "", "Dark General"
    mana, attack, health = 4, 4, 3
    index = "SV_Basic~Bloodcraft~Minion~4~4~3~None~Dark General~Battlecry"
    requireTarget, keyWord, description = False, "", "Fanfare: Gain Storm if Vengeance is active for you."
    attackAdd, healthAdd = 2, 2

    def effectCanTrigger(self):
        self.effectViable = self.Game.isVengeance(self.ID)

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if self.Game.isVengeance(self.ID):
            PRINT(self.Game, "Dark General's Fanfare gives it Storm")
            self.getsKeyword("Charge")
        return None


class WardrobeRaider(SVMinion):
    Class, race, name = "Bloodcraft", "", "Wardrobe Raider"
    mana, attack, health = 4, 3, 4
    index = "SV_Basic~Bloodcraft~Minion~4~3~4~None~Wardrobe Raider"
    requireTarget, keyWord, description = False, "", ""
    attackAdd, healthAdd = 1, 1

    # TODO need target

    def inHandEvolving(self, target=None):
        if isinstance(target, list): target = target[0]
        if target and target.onBoard:
            PRINT(self.Game,
                  f"Wardrobe Raider's Evolve deals 2 damage to enemy {target.name} and restore 2 defense to your leader.")
            self.dealsDamage(target, 2)
            self.restoresHealth(self.Game.heroes[self.ID], 2)


class CrimsonPurge(SVSpell):
    Class, name = "Bloodcraft", "Crimson Purge"
    requireTarget, mana = True, 4
    index = "SV_Basic~Bloodcraft~Spell~4~Crimson Purge"
    description = "Deal 2 damage to your leader. Destroy an enemy follower."

    def available(self):
        return self.selectableEnemyMinionExists()

    def targetCorrect(self, target, choice=0):
        if isinstance(target, list): target = target[0]
        return target.type == "Minion" and target.ID != self.ID and target.onBoard

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if target:
            if isinstance(target, list): target = target[0]
            damage = (2 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
            PRINT(self.Game, f"Crimson Purge deals {damage} damage your leader")
            self.dealsDamage(self.Game.heroes[self.ID], damage)
            PRINT(self.Game, f"Crimson Purge destroys enemy {target.name}")
            self.Game.killMinion(self, target)
            return target


class ImpLancer(SVMinion):
    Class, race, name = "Bloodcraft", "", "Imp Lancer"
    mana, attack, health = 6, 3, 6
    index = "SV_Basic~Bloodcraft~Minion~6~3~6~None~Imp Lancer~Charge"
    requireTarget, keyWord, description = False, "Charge", "Storm."
    attackAdd, healthAdd = 2, 2


class DemonicStorm(SVSpell):
    Class, name = "Bloodcraft", "Demonic Storm"
    mana, requireTarget = 6, False
    index = "SV_Basic~Bloodcraft~Spell~6~Demonic Storm"
    description = "Deal 3 damage to all allies and enemies."

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        damage = (3 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
        targets = [self.Game.heroes[self.ID]] + self.Game.minionsonBoard(1) + self.Game.minionsonBoard(2) + \
                  [self.Game.heroes[3 - self.ID]]
        PRINT(self.Game, f"Demonic Storm deals {damage} damage to all allies and enemies.")
        self.dealsAOE(targets, [damage for minion in targets])
        return None


class AbyssBeast(SVMinion):
    Class, race, name = "Bloodcraft", "", "Abyss Beast"
    mana, attack, health = 7, 5, 6
    index = "SV_Basic~Bloodcraft~Minion~7~5~6~None~Abyss Beast~Battlecry"
    requireTarget, keyWord, description = True, "", "Fanfare: Deal 5 damage to an enemy follower if Vengeance is active for you."
    attackAdd, healthAdd = 2, 2

    def returnTrue(self, choice=0):
        return self.Game.isVengeance(self.ID) and not self.targets

    def effectCanTrigger(self):
        self.effectViable = self.Game.isVengeance(self.ID)

    def targetExists(self, choice=0):
        return self.selectableEnemyMinionExists() and self.Game.isVengeance(self.ID)

    def targetCorrect(self, target, choice=0):
        if isinstance(target, list): target = target[0]
        return target.type == "Minion" and target.ID != self.ID and target.onBoard

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if isinstance(target, list): target = target[0]
        self.dealsDamage(target, 5)
        PRINT(self.Game, f"Abyss Beast deals 5 damage to {target.name}")
        return None


"""Havencraft cards"""


class Pegasus(SVMinion):
    Class, race, name = "Havencraft", "", "Pegasus"
    mana, attack, health = 5, 5, 3
    index = "SV_Basic~Havencraft~Minion~5~5~3~None~Pegasus~Uncollectible"
    requireTarget, keyWord, description = False, "", ""
    attackAdd, healthAdd = 2, 2


class HolyflameTiger(SVMinion):
    Class, race, name = "Havencraft", "", "Holyflame Tiger"
    mana, attack, health = 4, 4, 4
    index = "SV_Basic~Havencraft~Minion~4~4~4~None~Holyflame Tiger~Uncollectible"
    requireTarget, keyWord, description = False, "", ""
    attackAdd, healthAdd = 2, 2


class HolywingDragon(SVMinion):
    Class, race, name = "Havencraft", "", "Holywing Dragon"
    mana, attack, health = 6, 6, 6
    index = "SV_Basic~Havencraft~Minion~6~6~6~None~Holywing Dragon~Uncollectible"
    requireTarget, keyWord, description = False, "", ""
    attackAdd, healthAdd = 2, 2


class Trig_Countdown(TrigBoard):
    def __init__(self, entity):
        self.blank_init(entity, ["TurnStarts"])
        self.counter = self.entity.counter

    def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.onBoard and ID == self.entity.ID

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        PRINT(self.entity.Game, f"At the start of turn, {self.entity.name}'s countdown -1")
        self.entity.countdown(self.entity, 1)


class SummonPegasus(Amulet):
    Class, race, name = "Havencraft", "", "Summon Pegasus"
    mana = 1
    index = "SV_Basic~Havencraft~Amulet~1~None~Summon Pegasus~Countdown~Last Words"
    requireTarget, description = False, "Countdown (4) Last Words: Summon a Pegasus."

    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.counter = 4
        self.trigsBoard = [Trig_Countdown(self)]
        self.deathrattles = [Deathrattle_SummonPegasus(self)]


class Deathrattle_SummonPegasus(Deathrattle_Minion):
    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        PRINT(self.entity.Game, "Last Words: Summon a Pegasus.")
        self.entity.Game.summon([Pegasus(self.entity.Game, self.entity.ID)], (-1, "totheRightEnd"),
                                self.entity.ID)


class SnakePriestess(SVMinion):
    Class, race, name = "Havencraft", "", "Snake Priestess"
    mana, attack, health = 2, 1, 3
    index = "SV_Basic~Havencraft~Minion~2~1~3~None~Snake Priestess~Taunt"
    requireTarget, keyWord, description = False, "Taunt", "Ward."
    attackAdd, healthAdd = 2, 2


class HallowedDogma(SVSpell):
    Class, name = "Havencraft", "Hallowed Dogma"
    requireTarget, mana = True, 2
    index = "SV_Basic~Havencraft~Spell~2~Hallowed Dogma"
    description = "Subtract 2 from the Countdown of an allied amulet. Draw a card."

    def available(self):
        for amulet in self.Game.amuletsonBoard(self.ID):
            if "~Countdown" in amulet.index:
                return True
        return False

    def targetCorrect(self, target, choice=0):
        if isinstance(target, list): target = target[0]
        return target.type == "Amulet" and target.ID == self.ID and target.onBoard and "~Countdown" in target.index

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if target:
            if isinstance(target, list): target = target[0]
            target.countdown(self, 2)
            PRINT(self.Game, f"Hallowed Dogma subtracts 2 from the Countdown of {target.name} and draw a card")
            self.Game.Hand_Deck.drawCard(self.ID)
            return target


class BlackenedScripture(SVSpell):
    Class, name = "Havencraft", "Blackened Scripture"
    requireTarget, mana = True, 2
    index = "SV_Basic~Havencraft~Spell~2~Blackened Scripture"
    description = "Banish an enemy follower with 3 defense or less."

    def available(self):
        for minion in self.Game.minionsAlive(3 - self.ID):
            if minion.health <= 3:
                return True
        return False

    def targetCorrect(self, target, choice=0):
        if isinstance(target, list): target = target[0]
        return target.type == "Minion" and target.ID != self.ID and target.onBoard and target.health <= 3

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if target:
            if isinstance(target, list): target = target[0]
            PRINT(self.Game, f"Blackened Scripture let enemy {target.name} disappears")
            self.Game.banishMinion(self, target)
            return target


class BeastlyVow(Amulet):
    Class, race, name = "Havencraft", "", "Beastly Vow"
    mana = 2
    index = "SV_Basic~Havencraft~Amulet~2~None~Beastly Vow~Countdown~Last Words"
    requireTarget, description = False, "Countdown (2) Last Words: Summon a Holyflame Tiger."

    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.counter = 2
        self.trigsBoard = [Trig_Countdown(self)]
        self.deathrattles = [Deathrattle_BeastlyVow(self)]


class Deathrattle_BeastlyVow(Deathrattle_Minion):
    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        PRINT(self.entity.Game, "Last Words: Summon a Holyflame Tiger.")
        self.entity.Game.summon([HolyflameTiger(self.entity.Game, self.entity.ID)], (-1, "totheRightEnd"),
                                self.entity.ID)


class FeatherwyrmsDescent(Amulet):
    Class, race, name = "Havencraft", "", "Featherwyrm's Descent"
    mana = 3
    index = "SV_Basic~Havencraft~Amulet~3~None~Featherwyrm's Descent~Countdown~Last Words"
    requireTarget, description = False, "Countdown (3) Last Words: Summon a Holywing Dragon."

    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.counter = 3
        self.trigsBoard = [Trig_Countdown(self)]
        self.deathrattles = [Deathrattle_FeatherwyrmsDescent(self)]


class Deathrattle_FeatherwyrmsDescent(Deathrattle_Minion):
    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        PRINT(self.entity.Game, "Last Words: Summon a Holywing Dragon.")
        self.entity.Game.summon([HolywingDragon(self.entity.Game, self.entity.ID)], (-1, "totheRightEnd"),
                                self.entity.ID)


class PriestoftheCudgel(SVMinion):
    Class, race, name = "Havencraft", "", "Priest of the Cudgel"
    mana, attack, health = 4, 3, 4
    index = "SV_Basic~Havencraft~Minion~4~3~4~None~Priest of the Cudgel"
    requireTarget, keyWord, description = False, "", ""
    attackAdd, healthAdd = 1, 1

    # TODO need target

    def inHandEvolving(self, target=None):
        if isinstance(target, list): target = target[0]
        if target and target.onBoard:
            PRINT(self.Game, f"Priest of the Cudgel's banish enemy {target.name}")
            self.Game.banishMinion(self, target)


class GreaterPriestess(SVMinion):
    Class, race, name = "Havencraft", "", "Greater Priestess"
    mana, attack, health = 5, 3, 4
    index = "SV_Basic~Havencraft~Minion~5~3~4~None~Greater Priestess~Battlecry"
    requireTarget, keyWord, description = False, "", "Fanfare: Subtract 1 from the Countdown of all allied amulets."
    attackAdd, healthAdd = 2, 2

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        PRINT(self.Game, "Greater Priestess's Fanfare subtracts 1 from the Countdown of all allied amulets")
        for amulet in self.Game.amuletsonBoard(self.ID):
            if "~Countdown" in amulet.index:
                amulet.countdown(self, 1)
        return None


class AcolytesLight(SVSpell):
    Class, name = "Havencraft", "Acolyte's Light"
    requireTarget, mana = True, 5
    index = "SV_Basic~Havencraft~Spell~5~Acolyte's Light"
    description = "Banish an enemy follower. Restore X defense to your leader. X equals that follower's defense."

    def available(self):
        return self.selectableEnemyMinionExists()

    def targetCorrect(self, target, choice=0):
        if isinstance(target, list): target = target[0]
        return target.type == "Minion" and target.ID != self.ID and target.onBoard

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if target:
            if isinstance(target, list): target = target[0]
            health = target.health * (2 ** self.countHealDouble())
            PRINT(self.Game, f"Acolyte's Light banishes enemy {target.name}")
            self.Game.banishMinion(self, target)
            PRINT(self.Game, f"Acolyte's Light restores {health} to your leader")
            self.restoresHealth(self.Game.heroes[self.ID], health)
            return target


class DualFlames(Amulet):
    Class, race, name = "Havencraft", "", "Beastly Vow"
    mana = 5
    index = "SV_Basic~Havencraft~Amulet~5~None~Beastly Vow~Countdown~Last Words"
    requireTarget, description = False, "Countdown (2) Last Words: Summon 2 Holyflame Tigers."

    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.counter = 2
        self.trigsBoard = [Trig_Countdown(self)]
        self.deathrattles = [Deathrattle_DualFlames(self)]


class Deathrattle_DualFlames(Deathrattle_Minion):
    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        PRINT(self.entity.Game, "Last Words: Summon 2 Holyflame Tigers.")
        self.entity.Game.summon(
            [HolyflameTiger(self.entity.Game, self.entity.ID), HolyflameTiger(self.entity.Game, self.entity.ID)],
            (-1, "totheRightEnd"), self.entity.ID)


class Curate(SVMinion):
    Class, race, name = "Havencraft", "", "Curate"
    mana, attack, health = 7, 5, 5
    index = "SV_Basic~Havencraft~Minion~7~5~5~None~Curate~Battlecry"
    requireTarget, keyWord, description = True, "", "Fanfare: Restore 5 defense to an ally."
    attackAdd, healthAdd = 2, 2

    def targetExists(self, choice=0):
        return self.selectableFriendlyExists()

    def targetCorrect(self, target, choice=0):
        if isinstance(target, list): target = target[0]
        return target.type in ["Minion", "Hero"] and target.ID == self.ID and target.onBoard

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if isinstance(target, list): target = target[0]
        self.restoresHealth(target, 5)
        PRINT(self.Game, f"Curate restores 5 defense to {target.name}")
        return None


"""Portalcraft cards"""


class Puppet(SVMinion):
    Class, race, name = "Portalcraft", "", "Puppet"
    mana, attack, health = 0, 1, 1
    index = "SV_Basic~Portalcraft~Minion~0~1~1~None~Puppet~Rush~Uncollectible"
    requireTarget, keyWord, description = False, "Rush", "Rush. At the end of your opponent's turn, destroy this follower."
    attackAdd, healthAdd = 2, 2

    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.trigsBoard = [Trig_Puppet(self)]
        self.progress = 0


class Trig_Puppet(TrigBoard):
    def __init__(self, entity):
        self.blank_init(entity, ["TurnStarts"])

    def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.onBoard and ID == self.entity.ID

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        PRINT(self.entity.Game, "Puppet destroys itself")
        self.entity.Game.killMinion(self.entity, self.entity)


class AnalyzingArtifact(SVMinion):
    Class, race, name = "Portalcraft", "Artifact", "Analyzing Artifact"
    mana, attack, health = 1, 2, 1
    index = "SV_Basic~Portalcraft~Minion~1~2~1~Artifact~Analyzing Artifact~Deathrattle~Uncollectible"
    requireTarget, keyWord, description = False, "", "Last Words: Draw a card."
    attackAdd, healthAdd = 2, 2

    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.deathrattles = [Deathrattle_AnalyzingArtifact(self)]


class Deathrattle_AnalyzingArtifact(Deathrattle_Minion):
    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        PRINT(self.entity.Game, "Last Words: Draw a card.")
        self.entity.Game.Hand_Deck.drawCard(self.entity.ID)


class RadiantArtifact(SVMinion):
    Class, race, name = "Portalcraft", "Artifact", "Radiant Artifact"
    mana, attack, health = 5, 4, 3
    index = "SV_Basic~Portalcraft~Minion~5~4~3~Artifact~Radiant Artifact~Charge~Deathrattle~Uncollectible"
    requireTarget, keyWord, description = False, "Charge", "Storm. Last Words: If it is your turn, then put a random Artifact card from your deck into your hand. If it is your opponent's turn, draw a card."
    attackAdd, healthAdd = 2, 2

    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.deathrattles = [Deathrattle_RadiantArtifact(self)]


class Deathrattle_RadiantArtifact(Deathrattle_Minion):
    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        if self.entity.Game.turn == self.entity.ID:
            curGame = self.entity.Game
            if curGame.mode == 0:
                PRINT(self.entity.Game, "Last Words: Put a random Artifact card from your deck into your hand")
                if curGame.guides:
                    i = curGame.guides.pop(0)
                else:
                    artifacts = [i for i, card in enumerate(curGame.Hand_Deck.decks[self.entity.ID]) if
                                 card.type == "Minion" and "Artifact" in card.race]
                    i = npchoice(artifacts) if artifacts else -1
                    curGame.fixedGuides.append(i)
                if i > -1: curGame.Hand_Deck.drawCard(self.entity.ID, i)
        else:
            PRINT(self.entity.Game, "Last Words: Draw a card.")
            self.entity.Game.Hand_Deck.drawCard(self.entity.ID)


class Puppeteer(SVMinion):
    Class, race, name = "Portalcraft", "", "Puppeteer"
    mana, attack, health = 2, 2, 2
    index = "SV_Basic~Portalcraft~Minion~2~2~2~None~Puppeteer"
    requireTarget, keyWord, description = False, "", ""
    attackAdd, healthAdd = 0, 0

    def inHandEvolving(self, target=None):
        self.Game.Hand_Deck.addCardtoHand(Puppet, self.ID, "type")
        curGame = self.Game
        PRINT(curGame, "Puppeteer's Evolve add a Puppet to your hand.")
        ownHand = curGame.Hand_Deck.hands[self.ID]
        if curGame.mode == 0:
            if curGame.guides:
                i = curGame.guides.pop(0)
            else:
                puppets = [i for i, card in enumerate(ownHand) if card.type == "Minion" and card.name == "Puppet"]
                i = npchoice(puppets) if puppets else -1
                curGame.fixedGuides.append(i)
            if i > -1:
                PRINT(curGame, "Puppeteer's Evolve gives a random Puppet in your hand Bane")
                ownHand[i].getsKeyword("Bane")


class MechanizedServant(SVMinion):
    Class, race, name = "Portalcraft", "", "Mechanized Servant"
    mana, attack, health = 2, 2, 2
    index = "SV_Basic~Portalcraft~Minion~2~2~2~None~Mechanized Servant~Battlecry"
    requireTarget, keyWord, description = False, "", "Fanfare: If Resonance is active for you, gain Rush."
    attackAdd, healthAdd = 2, 2

    def effectCanTrigger(self):
        self.effectViable = self.Game.isResonance(self.ID)

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if self.Game.isResonance(self.ID):
            PRINT(self.Game, "Mechanized Servant's Fanfare gives it Rush")
            self.getsKeyword("Rush")
        return None


class MagisteelLion(SVMinion):
    Class, race, name = "Portalcraft", "", "Magisteel Lion"
    mana, attack, health = 2, 2, 2
    index = "SV_Basic~Portalcraft~Minion~2~2~2~None~Magisteel Lion~Battlecry"
    requireTarget, keyWord, description = False, "", "Fanfare: Put 2 Analyzing Artifacts into your deck."
    attackAdd, healthAdd = 2, 2

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        PRINT(self.Game, "Magisteel Lion shuffles 2 Analyzing Artifacts into player's deck")
        self.Game.Hand_Deck.shuffleCardintoDeck([AnalyzingArtifact(self.Game, self.ID) for i in range(2)], self.ID)
        return None


class MagisteelPuppet(SVMinion):
    Class, race, name = "Portalcraft", "", "Magisteel Puppet"
    mana, attack, health = 2, 2, 2
    index = "SV_Basic~Portalcraft~Minion~2~2~2~None~Magisteel Puppet"
    requireTarget, keyWord, description = False, "", ""
    attackAdd, healthAdd = 1, 1

    def inHandEvolving(self, target=None):
        self.Game.Hand_Deck.addCardtoHand([Puppet, Puppet], self.ID, "type")
        PRINT(self.Game, "Magisteel Puppet's Evolve add 2 Puppets to your hand.")


class DimensionCut(SVSpell):
    Class, name = "Portalcraft", "Dimension Cut"
    requireTarget, mana = True, 2
    index = "SV_Basic~Portalcraft~Spell~2~Dimension Cut"
    description = "Deal 3 damage to an enemy follower. If Resonance is active for you, deal 5 damage instead."

    def effectCanTrigger(self):
        self.effectViable = self.Game.isResonance(self.ID)

    def available(self):
        return self.selectableEnemyMinionExists()

    def targetCorrect(self, target, choice=0):
        if isinstance(target, list): target = target[0]
        return target.type == "Minion" and target.ID != self.ID and target.onBoard

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if target:
            if isinstance(target, list): target = target[0]
            if self.Game.isResonance(self.ID):
                damage = 5
            else:
                damage = 3
            damage = (damage + self.countSpellDamage()) * (2 ** self.countDamageDouble())
            PRINT(self.Game, f"Dimension Cut deals {damage} damage to enemy {target.name}")
            self.dealsDamage(target, damage)
        return target


class ToySoldier(SVMinion):
    Class, race, name = "Portalcraft", "", "Toy Soldier"
    mana, attack, health = 3, 2, 1
    index = "SV_Basic~Portalcraft~Minion~3~2~1~None~Toy Soldier"
    requireTarget, keyWord, description = False, "", "Fanfare: Put a Puppet into your hand."
    attackAdd, healthAdd = 2, 2

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        self.Game.Hand_Deck.addCardtoHand(Puppet, self.ID, "type")
        PRINT(self.Game, "Toy Soldier's Fanfare add a Puppet to your hand.")
        return None

    def inEvolving(self):
        trigger = Trig_ToySoldier(self)
        self.trigsBoard.append(trigger)
        if self.onBoard:
            trigger.connect()


class Trig_ToySoldier(TrigBoard):
    def __init__(self, entity):
        self.blank_init(entity, ["MinionBeenSummoned"])

    def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
        return subject.ID == self.entity.ID and self.entity.onBoard and subject.name == "Puppet"

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        PRINT(self.entity.Game, f"A friendly Puppet is summoned and Toy Soldier gives it +1/+0.")
        subject.buffDebuff(1, 0)


class AutomatonKnight(SVMinion):
    Class, race, name = "Portalcraft", "", "Automaton Knight"
    mana, attack, health = 3, 3, 2
    index = "SV_Basic~Portalcraft~Minion~3~3~2~None~Automaton Knight~Deathrattle"
    requireTarget, keyWord, description = False, "", "Last Words: Put a Puppet into your hand."
    attackAdd, healthAdd = 2, 2

    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.deathrattles = [Deathrattle_AutomatonKnight(self)]


class Deathrattle_AutomatonKnight(Deathrattle_Minion):
    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        PRINT(self.entity.Game, "Last Words: Put a Puppet into your hand.")
        self.entity.Game.Hand_Deck.addCardtoHand(Puppet, self.entity.ID, "type")


class IronforgedFighter(SVMinion):
    Class, race, name = "Portalcraft", "", "Ironforged Fighter"
    mana, attack, health = 4, 4, 3
    index = "SV_Basic~Portalcraft~Minion~4~4~3~None~Ironforged Fighter~Battlecry"
    requireTarget, keyWord, description = False, "", "Fanfare: Put 2 Radiant Artifacts into your deck."
    attackAdd, healthAdd = 2, 2

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        PRINT(self.Game, "Ironforged Fighter shuffles 2 Radiant Artifacts into player's deck")
        self.Game.Hand_Deck.shuffleCardintoDeck([RadiantArtifact(self.Game, self.ID) for i in range(2)], self.ID)
        return None


class RoanWingedNexx(SVMinion):
    Class, race, name = "Portalcraft", "", "Roan Winged Nexx"
    mana, attack, health = 4, 3, 4
    index = "SV_Basic~Portalcraft~Minion~4~3~4~None~Roan Winged Nexx"
    requireTarget, keyWord, description = False, "", ""
    attackAdd, healthAdd = 2, 2

    # TODO need target

    def inHandEvolving(self, target=None):
        if self.Game.isResonance(self.ID):
            if isinstance(target, list): target = target[0]
            if target and target.onBoard:
                PRINT(self.Game,
                      f"Roan Winged Nexx's Evolve deals 3 damage to enemy {target.name} and restore 2 defense to your leader.")
                self.dealsDamage(target, 3)


class PuppeteersStrings(SVSpell):
    Class, name = "Portalcraft", "Puppeteer's Strings"
    mana, requireTarget = 4, False,
    index = "SV_Basic~Portalcraft~Spell~4~Puppeteer's Strings"
    description = "Put 3 Puppets into your hand. Deal 1 damage to all enemy followers."

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        PRINT(self.Game, "Puppeteer's Strings puts 3 Puppets into your hand.")
        self.Game.Hand_Deck.addCardtoHand([Puppet for i in range(3)], self.ID, "type")
        damage = (1 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
        targets = self.Game.minionsonBoard(3 - self.ID)
        PRINT(self.Game, f"Puppeteer's Strings deals {damage} damage to all enemy followers.")
        self.dealsAOE(targets, [damage for minion in targets])
        return None


class BlackIronSoldier(SVMinion):
    Class, race, name = "Portalcraft", "", "Black Iron Soldier"
    mana, attack, health = 6, 5, 6
    index = "SV_Basic~Portalcraft~Minion~6~5~6~None~Black Iron Soldier~Battlecry"
    requireTarget, keyWord, description = False, "", "Fanfare: Put a random Artifact card from your deck into your hand."
    attackAdd, healthAdd = 2, 2

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        curGame = self.Game
        if curGame.mode == 0:
            PRINT(self.Game, "Black Iron Soldier's Fanfare puts a random Artifact card from your deck into your hand")
            if curGame.guides:
                i = curGame.guides.pop(0)
            else:
                artifacts = [i for i, card in enumerate(curGame.Hand_Deck.decks[self.ID]) if
                             card.type == "Minion" and "Artifact" in card.race]
                i = npchoice(artifacts) if artifacts else -1
                curGame.fixedGuides.append(i)
            if i > -1: curGame.Hand_Deck.drawCard(self.ID, i)
        return None


SV_Basic_Indices = {
    "SV_Hero: Forestcraft": Arisa,
    "SV_Hero: Swordcraft": Erika,
    "SV_Hero: Runecraft": Isabelle,
    "SV_Hero: Dragoncraft": Rowen,
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
    "SV_Basic~Swordcraft~Minion~2~2~2~Officer~Steelclad Knight~Uncollectible": SteelcladKnight,
    "SV_Basic~Swordcraft~Minion~1~1~2~Officer~Heavy Knight~Uncollectible": HeavyKnight,
    "SV_Basic~Swordcraft~Minion~1~1~1~Officer~Knight~Uncollectible": Knight,
    "SV_Basic~Swordcraft~Minion~1~1~1~Officer~Shield Guardian~Taunt~Uncollectible": ShieldGuardian,
    "SV_Basic~Swordcraft~Spell~1~Gilded Blade~Uncollectible": GildedBlade,
    "SV_Basic~Swordcraft~Spell~1~Gilded Goblet~Uncollectible": GildedGoblet,
    "SV_Basic~Swordcraft~Spell~1~Gilded Boots~Uncollectible": GildedBoots,
    "SV_Basic~Swordcraft~Spell~1~Gilded Necklace~Uncollectible": GildedNecklace,
    "SV_Basic~Swordcraft~Minion~1~1~1~Officer~Quickblader~Charge": Quickblader,
    "SV_Basic~Swordcraft~Minion~2~1~1~Officer~Oathless Knight~Battlecry": OathlessKnight,
    "SV_Basic~Swordcraft~Minion~2~2~1~Officer~Kunoichi Trainee~Stealth": KunoichiTrainee,
    "SV_Basic~Swordcraft~Minion~3~1~2~Officer~Ascetic Knight~Battlecry": AsceticKnight,
    "SV_Basic~Swordcraft~Spell~3~Forge Weaponry": ForgeWeaponry,
    "SV_Basic~Swordcraft~Minion~4~3~3~Commander~White General~Battlecry": WhiteGeneral,
    "SV_Basic~Swordcraft~Minion~4~3~4~Officer~Floral Fencer": FloralFencer,
    "SV_Basic~Swordcraft~Amulet~4~Commander~Royal Banner~Battlecry": RoyalBanner,
    "SV_Basic~Swordcraft~Minion~5~4~4~Officer~Ninja Master~Stealth": NinjaMaster,
    "SV_Basic~Swordcraft~Minion~6~4~6~Commander~Sage Commander~Battlecry": SageCommander,
    "SV_Basic~Runecraft~Minion~2~2~2~None~Clay Golem~Uncollectible": ClayGolem,
    "SV_Basic~Runecraft~Minion~1~1~1~None~Snowman~Uncollectible": Snowman,
    "SV_Basic~Runecraft~Amulet~1~Earth Sigil~Earth Essence~Uncollectible": EarthEssence,
    "SV_Basic~Runecraft~Minion~4~3~3~None~Guardian Golem~Taunt~Uncollectible": GuardianGolem,
    "SV_Basic~Runecraft~Minion~1~0~2~None~Scrap Golem~Taunt~Uncollectible": ScrapGolem,
    "SV_Basic~Runecraft~Spell~2~Conjure Guardian~Uncollectible": ConjureGuardian,
    "SV_Basic~Runecraft~Spell~1~Insight": Insight,
    "SV_Basic~Runecraft~Minion~2~2~2~None~Sammy, Wizard's Apprentice~Battlecry": SammyWizardsApprentice,
    "SV_Basic~Runecraft~Spell~2~Magic Missile": MagicMissile,
    "SV_Basic~Runecraft~Spell~2~Conjure Golem": ConjureGolem,
    "SV_Basic~Runecraft~Spell~2~Wind Blast~Spellboost": WindBlast,
    "SV_Basic~Runecraft~Spell~2~Summon Snow~Spellboost": SummonSnow,
    "SV_Basic~Runecraft~Minion~4~3~4~None~Demonflame Mage": DemonflameMage,
    "SV_Basic~Runecraft~Spell~4~Conjure Twosome": ConjureTwosome,
    "SV_Basic~Runecraft~Minion~5~3~3~None~Lightning Shooter~Battlecry~Spellboost": LightningShooter,
    "SV_Basic~Runecraft~Spell~8~Fiery Embrace~Spellboost": FieryEmbrace,
    "SV_Basic~Runecraft~Minion~10~7~7~None~Flame Destroyer~Spellboost": FlameDestroyer,
    "SV_Basic~Dragoncraft~Spell~1~Blazing Breath": BlazingBreath,
    "SV_Basic~Dragoncraft~Minion~2~2~2~None~Dragonrider": Dragonrider,
    "SV_Basic~Dragoncraft~Spell~2~Dragon Oracle": DragonOracle,
    "SV_Basic~Dragoncraft~Minion~3~2~3~None~Firstborn Dragon": FirstbornDragon,
    "SV_Basic~Dragoncraft~Minion~4~4~4~None~Death Dragon": DeathDragon,
    "SV_Basic~Dragoncraft~Spell~4~Serpent Wrath": SerpentWrath,
    "SV_Basic~Dragoncraft~Minion~5~4~5~None~Disaster Dragon": DisasterDragon,
    "SV_Basic~Dragoncraft~Minion~6~5~6~None~Dragonguard": Dragonguard,
    "SV_Basic~Dragoncraft~Minion~7~4~4~None~Dread Dragon~Battlecry": DreadDragon,
    "SV_Basic~Dragoncraft~Spell~7~Conflagration": Conflagration,
    "SV_Basic~Shadowcraft~Minion~1~1~1~None~Skeleton~Uncollectible": Skeleton,
    "SV_Basic~Shadowcraft~Minion~2~2~2~None~Zombie~Uncollectible": Zombie,
    "SV_Basic~Shadowcraft~Minion~4~4~4~None~Lich~Uncollectible": Lich,
    "SV_Basic~Shadowcraft~Minion~1~1~1~None~Ghost~Charge~Uncollectible": Ghost,
    "SV_Basic~Shadowcraft~Minion~2~2~2~None~Spartoi Sergeant~Battlecry": SpartoiSergeant,
    "SV_Basic~Shadowcraft~Minion~2~2~1~None~Spectre~Bane": Spectre,
    "SV_Basic~Shadowcraft~Spell~2~Undying Resentment~Necromancy": UndyingResentment,
    "SV_Basic~Shadowcraft~Minion~3~2~3~None~Apprentice Necromancer~Battlecry~Necromancy": ApprenticeNecromancer,
    "SV_Basic~Shadowcraft~Minion~4~4~3~None~Elder Spartoi Soldier~Battlecry": ElderSpartoiSoldier,
    "SV_Basic~Shadowcraft~Minion~4~4~3~None~Playful Necromancer": PlayfulNecromancer,
    "SV_Basic~Shadowcraft~Minion~4~1~1~None~Hell's Unleasher~Deathrattle": HellsUnleasher,
    "SV_Basic~Shadowcraft~Spell~4~Call of the Void": CalloftheVoid,
    "SV_Basic~Shadowcraft~Minion~5~3~3~None~Gravewaker~Deathrattle": Gravewaker,
    "SV_Basic~Shadowcraft~Minion~6~5~5~None~Ghostly Rider~Deathrattle": GhostlyRider,
    "SV_Basic~Shadowcraft~Minion~7~4~4~None~Undead King~Deathrattle": UndeadKing,
    "SV_Basic~Shadowcraft~Minion~1~1~1~None~Fores tBat~Uncollectible": ForestBat,
    "SV_Basic~Bloodcraft~Minion~2~2~2~None~Nightmare~Battlecry": Nightmare,
    "SV_Basic~Bloodcraft~Minion~2~1~3~None~Sweetfang Vampire~Drain": SweetfangVampire,
    "SV_Basic~Bloodcraft~Spell~2~Blood Pact": BloodPact,
    "SV_Basic~Bloodcraft~Spell~2~Razory Claw": RazoryClaw,
    "SV_Basic~Bloodcraft~Minion~3~3~3~None~Crazed Executioner~Battlecry": CrazedExecutioner,
    "SV_Basic~Bloodcraft~Minion~4~4~3~None~Dark General~Battlecry": DarkGeneral,
    "SV_Basic~Bloodcraft~Minion~4~3~4~None~Wardrobe Raider": WardrobeRaider,
    "SV_Basic~Bloodcraft~Spell~4~Crimson Purge": CrimsonPurge,
    "SV_Basic~Bloodcraft~Minion~6~3~6~None~Imp Lancer~Charge": ImpLancer,
    "SV_Basic~Bloodcraft~Spell~6~Demonic Storm": DemonicStorm,
    "SV_Basic~Bloodcraft~Minion~7~5~6~None~Abyss Beast~Battlecry": AbyssBeast,
    "SV_Basic~Havencraft~Minion~5~5~3~None~Pegasus~Uncollectible": Pegasus,
    "SV_Basic~Havencraft~Minion~4~4~4~None~Holyflame Tiger~Uncollectible": HolyflameTiger,
    "SV_Basic~Havencraft~Minion~6~6~6~None~Holywing Dragon~Uncollectible": HolywingDragon,
    "SV_Basic~Havencraft~Amulet~1~None~Summon Pegasus~Countdown~Last Words": SummonPegasus,
    "SV_Basic~Havencraft~Minion~2~1~3~None~Snake Priestess~Taunt": SnakePriestess,
    "SV_Basic~Havencraft~Spell~2~Hallowed Dogma": HallowedDogma,
    "SV_Basic~Havencraft~Spell~2~Blackened Scripture": BlackenedScripture,
    "SV_Basic~Havencraft~Amulet~2~None~Beastly Vow~Countdown~Last Words": BeastlyVow,
    "SV_Basic~Havencraft~Amulet~3~None~Featherwyrm's Descent~Countdown~Last Words": FeatherwyrmsDescent,
    "SV_Basic~Havencraft~Minion~4~3~4~None~Priest of the Cudgel": PriestoftheCudgel,
    "SV_Basic~Havencraft~Minion~5~3~4~None~Greater Priestess~Battlecry": GreaterPriestess,
    "SV_Basic~Havencraft~Spell~5~Acolyte's Light": AcolytesLight,
    "SV_Basic~Havencraft~Amulet~5~None~Beastly Vow~Countdown~Last Words": BeastlyVow,
    "SV_Basic~Havencraft~Minion~7~5~5~None~Curate~Battlecry": Curate,
    "SV_Basic~Portalcraft~Minion~0~1~1~None~Puppet~Rush~Uncollectible": Puppet,
    "SV_Basic~Portalcraft~Minion~1~2~1~Artifact~Analyzing Artifact~Deathrattle~Uncollectible": AnalyzingArtifact,
    "SV_Basic~Portalcraft~Minion~5~4~3~Artifact~Radiant Artifact~Charge~Deathrattle~Uncollectible": RadiantArtifact,
    "SV_Basic~Portalcraft~Minion~2~2~2~None~Puppeteer": Puppeteer,
    "SV_Basic~Portalcraft~Minion~2~2~2~None~Mechanized Servant~Battlecry": MechanizedServant,
    "SV_Basic~Portalcraft~Minion~2~2~2~None~Magisteel Lion~Battlecry": MagisteelLion,
    "SV_Basic~Portalcraft~Minion~2~2~2~None~Magisteel Puppet": MagisteelPuppet,
    "SV_Basic~Portalcraft~Spell~2~Dimension Cut": DimensionCut,
    "SV_Basic~Portalcraft~Minion~3~2~1~None~Toy Soldier": ToySoldier,
    "SV_Basic~Portalcraft~Minion~3~3~2~None~Automaton Knight~Deathrattle": AutomatonKnight,
    "SV_Basic~Portalcraft~Minion~4~4~3~None~Ironforged Fighter~Battlecry": IronforgedFighter,
    "SV_Basic~Portalcraft~Minion~4~3~4~None~Roan Winged Nexx": RoanWingedNexx,
    "SV_Basic~Portalcraft~Spell~4~Puppeteer's Strings": PuppeteersStrings,
    "SV_Basic~Portalcraft~Minion~6~5~6~None~Black Iron Soldier~Battlecry": BlackIronSoldier,
}
