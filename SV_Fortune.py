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


"""Neutral cards"""


class CloudGigas(SVMinion):
    Class, race, name = "Neutral", "", "Cloud Gigas"
    mana, attack, health = 2, 5, 5
    index = "SV_Fortune~Neutral~Minion~2~5~5~None~Cloud Gigas~Taunt"
    requireTarget, keyWord, description = False, "Taunt", "Ward. At the start of your turn, put a Cloud Gigas into your deck and banish this follower."
    attackAdd, healthAdd = 0, 0

    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.trigsBoard = [Trig_CloudGigas(self)]

    def inEvolving(self):
        for t in self.trigsBoard:
            if type(t) == Trig_CloudGigas:
                t.disconnect()
                self.trigsBoard.remove(t)
                break


class Trig_CloudGigas(TrigBoard):
    def __init__(self, entity):
        self.blank_init(entity, ["TurnStarts"])

    def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.onBoard and ID == self.entity.ID

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        self.entity.Game.banishMinion(self.entity, self.entity)
        PRINT(self.entity.Game, "Cloud Gigas shuffles a Cloud Gigas into player's deck")
        self.entity.Game.Hand_Deck.shuffleCardintoDeck([CloudGigas(self.entity.Game, self.entity.ID)], self.entity.ID)


class SuddenShowers(SVSpell):
    Class, name = "Neutral", "Sudden Showers"
    mana, requireTarget = 2, False
    index = "SV_Fortune~Neutral~Spell~2~Sudden Showers"
    description = "Destroy a random follower."

    def available(self):
        return len(self.Game.minionsAlive(1)) + len(self.Game.minionsAlive(2)) > 0

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        curGame = self.Game
        if curGame.mode == 0:
            PRINT(curGame, "Sudden Showers destroys a random follower.")
            if curGame.guides:
                i, where = curGame.guides.pop(0)
                if where:
                    minion = curGame.find(i, where)
                    curGame.killMinion(self, minion)
            else:
                minions = curGame.minionsonBoard(1) + curGame.minionsonBoard(2)
                if len(minions) > 0:
                    minion = npchoice(minions)
                    curGame.fixedGuides.append((minion.position, f"minion{minion.ID}"))
                    curGame.killMinion(self, minion)
                else:
                    curGame.fixedGuides.append((0, ""))
        return None


class WingedCourier(SVMinion):
    Class, race, name = "Neutral", "", "Winged Courier"
    mana, attack, health = 4, 4, 3
    index = "SV_Fortune~Neutral~Minion~4~4~3~None~Winged Courier~Deathrattle"
    requireTarget, keyWord, description = False, "", "Last Words: Draw a card."
    attackAdd, healthAdd = 2, 2

    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.deathrattles = [Deathrattle_WingedCourier(self)]


class Deathrattle_WingedCourier(Deathrattle_Minion):
    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        PRINT(self.entity.Game, "Last Words: Draw a card.")
        self.entity.Game.Hand_Deck.drawCard(self.entity.ID)


class FieranHavensentWindGod(SVMinion):
    Class, race, name = "Neutral", "", "Fieran, Havensent Wind God"
    mana, attack, health = 4, 1, 1
    index = "SV_Fortune~Neutral~Minion~4~1~1~None~Fieran, Havensent Wind God~Battlecry~Invocation"
    requireTarget, keyWord, description = True, "", "Invocation: At the start of your turn, Rally (10) - Invoke this card.------Fanfare: If you have more evolution points than your opponent, gain +0/+2 and deal 2 damage to an enemy follower. (You have 0 evolution points on turns you are unable to evolve.)At the end of your turn, give +1/+1 to all allied followers."
    attackAdd, healthAdd = 2, 2

    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.trigsBoard = [Trig_FieranHavensentWindGod(self)]
        self.trigsDeck = [Trig_InvocationFieranHavensentWindGod(self)]

    def returnTrue(self, choice=0):
        return self.Game.getEvolutionPoint(
            self.ID) > self.Game.getEvolutionPoint(3 - self.ID) and not self.targets

    def effectCanTrigger(self):
        self.effectViable = self.Game.getEvolutionPoint(
            self.ID) > self.Game.getEvolutionPoint(3 - self.ID)

    def targetExists(self, choice=0):
        return self.selectableEnemyMinionExists() and self.Game.getEvolutionPoint(
            self.ID) > self.Game.getEvolutionPoint(3 - self.ID)

    def targetCorrect(self, target, choice=0):
        return target.type == "Minion" and target.ID != self.ID and target.onBoard

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if self.Game.getEvolutionPoint(self.ID) > self.Game.getEvolutionPoint(3 - self.ID):
            self.buffDebuff(0, 2)
            PRINT(self, f"Fieran, Havensent Wind God's Fanfare gives itself +0/+2.")
            if target:
                PRINT(self, f"Fieran, Havensent Wind God deals 2 damage to minion {target.name}")
                self.dealsDamage(target, 2)
        return None


class Trig_FieranHavensentWindGod(TrigBoard):
    def __init__(self, entity):
        self.blank_init(entity, ["TurnEnds"])

    def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.onBoard and ID == self.entity.ID

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        minions = self.entity.Game.minionsAlive(self.entity.ID)
        PRINT(self.entity.Game, "At the end of turn, Fieran, Havensent Wind God gives all friendly minions +1/+1")
        for minion in minions:
            minion.buffDebuff(1, 1)


class Trig_InvocationFieranHavensentWindGod(TrigInvocation):
    def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.inDeck and ID == self.entity.ID and self.entity.Game.space(self.entity.ID) > 0 and \
               self.entity.Game.Counters.numMinionsSummonedThisGame[self.entity.ID] >= 10


class ResolveoftheFallen(SVSpell):
    Class, name = "Natural", "Resolve of the Fallen"
    requireTarget, mana = True, 4
    index = "SV_Fortune~Natural~Spell~4~Resolve of the Fallen"
    description = "Destroy an enemy follower or amulet.If at least 3 allied followers have evolved this match, recover 3 play points.Then, if at least 5 have evolved, draw 2 cards."

    def effectCanTrigger(self):
        self.effectViable = self.Game.Counters.evolvedThisGame[self.ID] > 3

    def available(self):
        return self.selectableEnemyMinionExists() or self.selectableEnemyAmuletExists()

    def targetCorrect(self, target, choice=0):
        if isinstance(target, list): target = target[0]
        return target.type in ["Minion", "Amulet"] and target.ID != self.ID and target.onBoard

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if isinstance(target, list): target = target[0]
        self.Game.killMinion(self, target)
        if self.Game.Counters.evolvedThisGame[self.ID] >= 3:
            self.Game.Manas.restoreManaCrystal(3, self.ID)
            if self.Game.Counters.evolvedThisGame[self.ID] >= 5:
                self.Game.Hand_Deck.drawCard(self.ID)
                self.Game.Hand_Deck.drawCard(self.ID)
        return None


class StarbrightDeity(SVMinion):
    Class, race, name = "Natural", "", "Starbright Deity"
    mana, attack, health = 5, 3, 4
    index = "SV_Fortune~Natural~Minion~5~3~4~None~Starbright Deity~Battlecry"
    requireTarget, keyWord, description = False, "", "Fanfare: Put into your hand copies of the 3 left-most cards in your hand, in the order they were added."
    attackAdd, healthAdd = 2, 2

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        for i in range(min(3, len(self.Game.Hand_Deck.hands[self.ID]))):
            card = self.Game.Hand_Deck.hands[self.ID][i]
            self.Game.Hand_Deck.addCardtoHand([type(card)], self.ID, "type")
            PRINT(self.Game, f"Starbright Deity's Fanfare put {card.name} into your hand.")
        return None


class XXIZelgeneaTheWorld(SVMinion):
    Class, race, name = "Neutral", "", "XXI. Zelgenea, The World"
    mana, attack, health = 5, 5, 5
    index = "SV_Fortune~Neutral~Minion~5~5~5~None~XXI. Zelgenea, The World~Battlecry~Invocation"
    requireTarget, keyWord, description = False, "", "Invocation: At the start of your tenth turn, invoke this card. Then, evolve it.----------Fanfare: Restore 5 defense to your leader. If your leader had 14 defense or less before defense was restored, draw 2 cards and randomly destroy 1 of the enemy followers with the highest attack in play.Can't be evolved using evolution points. (Can be evolved using card effects.)"
    attackAdd, healthAdd = 5, 5

    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.marks["Can't Evolve"] = 1
        self.trigsDeck = [Trig_InvocationXXIZelgeneaTheWorld(self)]

    def effectCanTrigger(self):
        self.effectViable = self.Game.heroes[self.ID].health < 15

    def afterInvocation(self, signal, ID, subject, target, number, comment):
        self.evolve()

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if self.Game.heroes[self.ID].health < 15:
            self.restoresHealth(self.Game.heroes[self.ID], 5)
            PRINT(self, f"XXI. Zelgenea, The World restores 5 Health to its leader.")
            curGame = self.Game
            if curGame.mode == 0:
                if curGame.guides:
                    i = curGame.guides.pop(0)
                else:
                    minions = curGame.minionsAlive(3 - self.ID)
                    maxAttack = 0
                    for minion in minions:
                        maxAttack = max(maxAttack, minion.attack)
                    targets = []
                    for minion in minions:
                        if minion.attack == maxAttack:
                            targets.append(minion)
                    i = npchoice(targets) if targets else -1
                    curGame.fixedGuides.append(i)
                if i > -1:
                    self.Game.killMinion(self, curGame.minions[3 - self.ID][i])
                    PRINT(self, f"XXI. Zelgenea, The World destroys {target.name}.")
            self.Game.Hand_Deck.drawCard(self.ID)
            self.Game.Hand_Deck.drawCard(self.ID)
            PRINT(self.Game, f"XXI. Zelgenea, The World draw two cards.")
        else:
            self.restoresHealth(self.Game.heroes[self.ID], 5)
            PRINT(self.Game, f"XXI. Zelgenea, The World restores 5 Health to its leader.")
        return None

    def inEvolving(self):
        trigger = Trig_AttackXXIZelgeneaTheWorld(self)
        self.trigsBoard.append(trigger)
        trigger.connect()


class Trig_AttackXXIZelgeneaTheWorld(TrigBoard):
    def __init__(self, entity):
        self.blank_init(entity, ["MinionAttackingHero", "MinionAttackingMinion"])

    def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.onBoard and subject == self.entity

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        trigger = Trig_EndXXIZelgeneaTheWorld(self.entity.Game.heroes[self.entity.ID])
        for t in self.entity.Game.heroes[self.entity.ID].trigsBoard:
            if type(t) == type(trigger):
                return
        self.entity.Game.heroes[self.entity.ID].trigsBoard.append(trigger)
        trigger.connect()


class Trig_EndXXIZelgeneaTheWorld(TrigBoard):
    def __init__(self, entity):
        self.blank_init(entity, ["TurnEnds"])

    def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.onBoard and ID == self.entity.ID

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        targets = [self.entity.Game.heroes[1], self.entity.Game.heroes[2]] + self.entity.Game.minionsonBoard(1) \
                  + self.entity.Game.minionsonBoard(2)
        PRINT(self.entity.Game, "XXI. Zelgenea, The World's ability deals 4 damage to all characters.")
        self.entity.dealsAOE(targets, [4 for obj in targets])


class Trig_InvocationXXIZelgeneaTheWorld(TrigInvocation):
    def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.inDeck and ID == self.entity.ID and self.entity.Game.space(self.entity.ID) > 0 and \
               self.entity.Game.Counters.turns[self.entity.ID] == 10

class TitanicShowdown(Amulet):
    Class, race, name = "Neutral", "", "Titanic Showdown"
    mana = 6
    index = "SV_Fortune~Neutral~Amulet~6~None~Titanic Showdown~Countdown~Last Words"
    requireTarget, description = False, "Countdown (2) Fanfare: Put a random follower that originally costs at least 9 play points from your deck into your hand. If any other allied Titanic Showdowns are in play, recover 4 play points and banish this amulet. Last Words: At the start of your next turn, put 5 random followers that originally cost at least 9 play points from your hand into play."

    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.counter = 2
        self.trigsBoard = [Trig_Countdown(self)]
        self.deathrattles = [Deathrattle_TitanicShowdown(self)]

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        curGame = self.Game
        if curGame.mode == 0:
            PRINT(self.Game,
                  "Titanic Showdown's Fanfare puts a random follower that originally costs at least 9 play points from your deck into your hand.")
            if curGame.guides:
                i = curGame.guides.pop(0)
            else:
                minions = [i for i, card in enumerate(curGame.Hand_Deck.decks[self.ID]) if
                           card.type == "Minion" and type(card).mana >= 9]
                i = npchoice(minions) if minions else -1
                curGame.fixedGuides.append(i)
            if i > -1: curGame.Hand_Deck.drawCard(self.ID, i)
        amulets = self.Game.amuletsonBoard(self.ID)
        for amulet in amulets:
            if amulet.name == "Titanic Showdown" and amulet is not self:
                self.Game.banishMinion(self, self)
                self.Game.Manas.restoreManaCrystal(4, self)
                break
        return None


class Deathrattle_TitanicShowdown(Deathrattle_Minion):
    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        trigger = Trig_TitanicShowdown(self.entity.Game.heroes[self.entity.ID])
        for t in self.entity.Game.heroes[self.entity.ID].trigsBoard:
            if type(t) == type(trigger):
                return
        self.entity.Game.heroes[self.entity.ID].trigsBoard.append(trigger)
        trigger.connect()


class Trig_TitanicShowdown(TrigBoard):
    def __init__(self, entity):
        self.blank_init(entity, ["TurnStarts"])

    def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.onBoard and ID == self.entity.ID

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        PRINT(self.entity.Game, "Last Words: Summon a Holywing Dragon.")
        curGame = self.entity.Game
        for n in range(5):
            if curGame.guides:
                i = curGame.guides.pop(0)
            else:  # 假设是依次召唤，如果召唤前一个随从时进行了某些结算，则后面的召唤可能受之影响
                minions = []
                for i, card in enumerate(curGame.Hand_Deck.hands[ID]):
                    if card.type == "Minion" and type(card).mana >= 9:
                        minions.append(i)
                i = npchoice(minions) if minions and curGame.space(ID) > 0 else -1
                curGame.fixedGuides.append(i)
            if i > -1: curGame.summonfromHand(i, ID, -1, self.entity.ID)
        for t in self.entity.trigsBoard:
            if type(t) == Trig_TitanicShowdown:
                t.disconnect()
                self.entity.trigsBoard.remove(t)
                break


class PureshotAngel_Accelerate(SVSpell):
    Class, name = "Runecraft", "Pureshot Angel"
    requireTarget, mana = True, 2
    index = "SV_Fortune~Neutral~Spell~2~Pureshot Angel~Accelerate~Uncollectible"
    description = "Deal 1 damage to an enemy"

    def targetCorrect(self, target, choice=0):
        if isinstance(target, list): target = target[0]
        return target.type == "Minion" and target.ID != self.ID and target.onBoard

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if target:
            if isinstance(target, list): target = target[0]
            damage = (3 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
            PRINT(self.Game, f"Pureshot Angel, as spell, deals {damage} damage to enemy {target.name}.")
            self.dealsDamage(target, damage)
        return target


class PureshotAngel(SVMinion):
    Class, race, name = "Runecraft", "", "Pureshot Angel"
    mana, attack, health = 8, 6, 6
    index = "SV_Fortune~Neutral~Minion~5~5~5~None~Pureshot Angel~Battlecry~Accelerate"
    requireTarget, keyWord, description = True, "", "Accelerate 2: Deal 1 damage to an enemy. Fanfare: xxx. Deal 3 damage to an enemy minion, and deal 1 damage to the enemy hero"
    accelerateSpell = PureshotAngel_Accelerate

    def getMana(self):
        if self.Game.Manas.manas[self.ID] < self.mana:
            return 2
        else:
            return self.mana

    def willAccelerate(self):
        curMana = self.Game.Manas.manas[self.ID]
        return self.mana > curMana >= 2

    def effectCanTrigger(self):
        self.effectViable = "sky blue" if self.willAccelerate() and self.targetExists() else False

    def returnTrue(self, choice=0):
        if self.willAccelerate():
            return not self.targets
        return False

    def available(self):
        if self.willAccelerate():
            return self.selectableEnemyMinionExists()
        return True

    def targetExists(self, choice=0):
        return self.selectableEnemyMinionExists()

    def targetCorrect(self, target, choice=0):
        if isinstance(target, list): target = target[0]
        return (self.willAccelerate() and target.type == "Minion") and target.ID != self.ID and target.onBoard

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        curGame = self.Game
        if curGame.mode == 0:
            if curGame.guides:
                i = curGame.guides.pop(0)
            else:
                minions = curGame.minionsAlive(3 - self.ID)
                i = npchoice(minions).position if minions else -1
                curGame.fixedGuides.append(i)
            if i > -1:
                PRINT(self.Game,
                      f"Pureshot Angel's Fanfare deals 3 damage to enemy minion {curGame.minions[3 - self.ID][i].name}")
                self.dealsDamage(curGame.minions[3 - self.ID][i], 3)
        PRINT(self.Game,
              f"Pureshot Angel's Fanfare deals 3 damage to enemy player")
        self.dealsDamage(self.Game.heroes[3 - self.ID], 3)
        return None


"""Forestcraft cards"""

"""Swordcraft cards"""

"""Runecraft cards"""

"""Dragoncraft cards"""

"""Shadowcraft cards"""

"""Bloodcraft cards"""

"""Havencraft cards"""

"""Portalcraft cards"""

"""DLC cards"""

SV_Fortune_Indices = {
    "SV_Fortune~Neutral~Minion~2~5~5~None~Cloud Gigas~Taunt": CloudGigas,
    "SV_Fortune~Neutral~Spell~2~Sudden Showers": SuddenShowers,
    "SV_Fortune~Neutral~Minion~4~4~3~None~Winged Courier~Deathrattle": WingedCourier,
    "SV_Fortune~Neutral~Minion~4~1~1~None~Fieran, Havensent Wind God~Battlecry~Invocation": FieranHavensentWindGod,
    "SV_Fortune~Natural~Spell~4~Resolve of the Fallen": ResolveoftheFallen,
    "SV_Fortune~Natural~Minion~5~3~4~None~Starbright Deity~Battlecry": StarbrightDeity,
    "SV_Fortune~Neutral~Minion~5~5~5~None~XXI. Zelgenea, The World~Battlecry~Invocation": XXIZelgeneaTheWorld,
    "SV_Fortune~Neutral~Amulet~6~None~Titanic Showdown~Countdown~Last Words": TitanicShowdown,
    "SV_Fortune~Neutral~Spell~2~Pureshot Angel~Accelerate~Uncollectible": PureshotAngel,
    "SV_Fortune~Neutral~Minion~5~5~5~None~Pureshot Angel~Battlecry~Accelerate": PureshotAngel,
}
