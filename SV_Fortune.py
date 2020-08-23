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
                minions = curGame.minionsAlive(1) + curGame.minionsAlive(2)
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
    index = "SV_Fortune~Neutral~Minion~4~1~1~None~Fieran, Havensent Wind God~Battlecry~Invocation~Legendary"
    requireTarget, keyWord, description = True, "", "Invocation: At the start of your turn, Rally (10) - Invoke this card.------Fanfare: If you have more evolution points than your opponent, gain +0/+2 and deal 2 damage to an enemy follower. (You have 0 evolution points on turns you are unable to evolve.)At the end of your turn, give +1/+1 to all allied followers."
    attackAdd, healthAdd = 2, 2

    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.trigsBoard = [Trig_FieranHavensentWindGod(self)]
        self.trigsDeck = [Trig_InvocationFieranHavensentWindGod(self)]

    def effectCanTrigger(self):
        self.effectViable = self.Game.getEvolutionPoint(
            self.ID) > self.Game.getEvolutionPoint(3 - self.ID)

    def targetExists(self, choice=0):
        return self.selectableEnemyMinionExists() and self.Game.getEvolutionPoint(
            self.ID) > self.Game.getEvolutionPoint(3 - self.ID)

    def targetCorrect(self, target, choice=0):
        if isinstance(target, list): target = target[0]
        return target.type == "Minion" and target.ID != self.ID and target.onBoard

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if self.Game.getEvolutionPoint(self.ID) > self.Game.getEvolutionPoint(3 - self.ID):
            self.buffDebuff(0, 2)
            PRINT(self.Game, f"Fieran, Havensent Wind God's Fanfare gives itself +0/+2.")
            if target:
                if isinstance(target, list): target = target[0]
                PRINT(self.Game, f"Fieran, Havensent Wind God deals 2 damage to minion {target.name}")
                self.dealsDamage(target, 2)
        return None


class Trig_FieranHavensentWindGod(TrigBoard):
    def __init__(self, entity):
        self.blank_init(entity, ["TurnEnds"])

    def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.onBoard and ID == self.entity.ID

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        minions = self.entity.Game.minionsonBoard(self.entity.ID)
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
        if target:
            if isinstance(target, list): target = target[0]
            self.Game.killMinion(self, target)
            if self.Game.Counters.evolvedThisGame[self.ID] >= 3:
                self.Game.Manas.restoreManaCrystal(3, self.ID)
                if self.Game.Counters.evolvedThisGame[self.ID] >= 5:
                    self.Game.Hand_Deck.drawCard(self.ID)
                    self.Game.Hand_Deck.drawCard(self.ID)
        return target


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
    index = "SV_Fortune~Neutral~Minion~5~5~5~None~XXI. Zelgenea, The World~Battlecry~Invocation~Legendary"
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
            PRINT(self.Game, f"XXI. Zelgenea, The World restores 5 Health to its leader.")
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
                    PRINT(self.Game, f"XXI. Zelgenea, The World destroys {target.name}.")
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
    index = "SV_Fortune~Neutral~Amulet~6~None~Titanic Showdown~Countdown~Deathrattle"
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
        # for t in self.entity.Game.heroes[self.entity.ID].trigsBoard:
        #     if type(t) == type(trigger):
        #         return
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
    Class, name = "Neutral", "Pureshot Angel"
    requireTarget, mana = False, 2
    index = "SV_Fortune~Neutral~Spell~2~Pureshot Angel~Accelerate~Uncollectible"
    description = "Deal 3 damage to an enemy"

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
                damage = (3 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
                PRINT(self.Game,
                      f"Pureshot Angel's Fanfare deals {damage} damage to enemy minion {curGame.minions[3 - self.ID][i].name}")
                self.dealsDamage(curGame.minions[3 - self.ID][i], damage)
        return None


class PureshotAngel(SVMinion):
    Class, race, name = "Neutral", "", "Pureshot Angel"
    mana, attack, health = 8, 6, 6
    index = "SV_Fortune~Neutral~Minion~8~6~6~None~Pureshot Angel~Battlecry~Accelerate"
    requireTarget, keyWord, description = False, "", "Accelerate 2: Deal 1 damage to an enemy. Fanfare: xxx. Deal 3 damage to an enemy minion, and deal 1 damage to the enemy hero"
    accelerateSpell = PureshotAngel_Accelerate
    attackAdd, healthAdd = 2, 2

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

    def available(self):
        if self.willAccelerate():
            return len(self.Game.minionsAlive(3 - self.ID)) > 0
        return True

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


class LumberingCarapace(SVMinion):
    Class, race, name = "Forestcraft", "", "Lumbering Carapace"
    mana, attack, health = 1, 1, 1
    index = "SV_Fortune~Forestcraft~Minion~1~1~1~None~Lumbering Carapace~Battlecry"
    requireTarget, keyWord, description = False, "", "Fanfare: If at least 2 other cards were played this turn, gain +2/+2. Then, if at least 4 other cards were played this turn, gain +2/+2 more and Ward."
    attackAdd, healthAdd = 2, 2

    def effectCanTrigger(self):
        self.effectViable = self.Game.combCards(self.ID) >= 2

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        numCardsPlayed = self.Game.combCards(self.ID)
        if numCardsPlayed >= 2:
            PRINT(self.Game, "Lumbering Carapace gains +2/+2")
            self.buffDebuff(2, 2)
            if numCardsPlayed >= 4:
                PRINT(self.Game, "Lumbering Carapace gains +2/+2 and Ward")
                self.buffDebuff(2, 2)
                self.getsKeyword("Taunt")
        return None


class BlossomingArcher(SVMinion):
    Class, race, name = "Forestcraft", "", "Blossoming Archer"
    mana, attack, health = 2, 2, 2
    index = "SV_Fortune~Forestcraft~Minion~2~2~2~None~Blossoming Archer"
    requireTarget, keyWord, description = False, "", "Whenever you play a card using its Accelerate effect, deal 2 damage to a random enemy follower."
    attackAdd, healthAdd = 2, 2

    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.trigsBoard = [Trig_BlossomingArcher(self)]


class Trig_BlossomingArcher(TrigBoard):
    def __init__(self, entity):
        self.blank_init(entity, ["SpellPlayed"])

    def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
        return subject.ID == self.entity.ID and self.entity.onBoard and "~Accelerate" in subject.index

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        if "~Accelerate" in subject.index:
            curGame = self.entity.Game
            if curGame.mode == 0:
                enemy = None
                if curGame.guides:
                    i, where = curGame.guides.pop(0)
                    if where: enemy = curGame.find(i, where)
                else:
                    chars = curGame.minionsAlive(3 - self.entity.ID)
                    if chars:
                        enemy = npchoice(chars)
                        curGame.fixedGuides.append((enemy.position, enemy.type + str(enemy.ID)))
                    else:
                        curGame.fixedGuides.append((0, ''))
                if enemy:
                    PRINT(self.entity.Game, f"Blossoming Archer deals 2 damage to {enemy.name}")
                    self.entity.dealsDamage(enemy, 2)


class SoothingSpell(SVSpell):
    Class, name = "Forestcraft", "Soothing Spell"
    requireTarget, mana = True, 2
    index = "SV_Fortune~Forestcraft~Spell~2~Soothing Spell"
    description = "Restore 3 defense to an ally. If at least 2 other cards were played this turn, recover 1 evolution point."

    def effectCanTrigger(self):
        self.effectViable = self.Game.combCards(self.ID) >= 2

    def targetExists(self, choice=0):
        return self.selectableFriendlyExists()

    def targetCorrect(self, target, choice=0):
        if isinstance(target, list): target = target[0]
        return target.type in ["Minion", "Hero"] and target.onBoard and target.ID == self.ID

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if target:
            if isinstance(target, list): target = target[0]
            heal = 3 * (2 ** self.countHealDouble())
            self.restoresHealth(target, heal)
            PRINT(self.Game,
                  f"Soothing Spell restores {heal} defense to {target.name}")
            if self.Game.combCards(self.ID) >= 2:
                self.Game.restoreEvolvePoint(self.ID)
                PRINT(self.Game,
                      f"Soothing Spell restores 1 evolution point")
        return target


class XIIWolfraudHangedMan(SVMinion):
    Class, race, name = "Forestcraft", "", "XII. Wolfraud, Hanged Man"
    mana, attack, health = 3, 3, 3
    index = "SV_Fortune~Forestcraft~Minion~3~3~3~None~XII. Wolfraud, Hanged Man~Enhance~Battlecry~Legendary"
    requireTarget, keyWord, description = False, "", "Fanfare: Enhance (7) - Put a Treacherous Reversal into your hand and banish this follower. Can't be destroyed by effects. (Can be destroyed by damage from effects.)"
    attackAdd, healthAdd = 2, 2

    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.marks["Can't Break"] = 1

    def inHandEvolving(self, target=None):
        if self.Game.combCards(self.ID) >= 3:
            self.buffDebuff(3, 3)
            PRINT(self.Game,
                  "XII. Wolfraud, Hanged Man's Evolve gives it +3/+3")

    def getMana(self):
        if self.Game.Manas.manas[self.ID] >= 7:
            return 7
        else:
            return self.mana

    def willEnhance(self):
        return self.Game.Manas.manas[self.ID] >= 7

    def effectCanTrigger(self):
        self.effectViable = self.willEnhance()

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if comment == 7:
            PRINT(self.Game,
                  "XII. Wolfraud, Hanged Man's Enhanced Fanfare Put a Treacherous Reversal into your hand and banish this follower.")
            self.Game.banishMinion(self, self)
            self.Game.Hand_Deck.addCardtoHand([TreacherousReversal], self.ID, "type")
        return target


class TreacherousReversal(SVSpell):
    Class, name = "Forestcraft", "Treacherous Reversal"
    requireTarget, mana = False, 0
    index = "SV_Fortune~Forestcraft~Spell~0~Treacherous Reversal~Uncollectible"
    description = "Banish all cards in play.Banish all cards in your hand and deck.Put copies of the first 10 cards your opponent played this match (excluding XII. Wolfraud, Hanged Man and Treacherous Reversal) into your deck, in the order they were played.Transform the Reaper at the bottom of your deck into a Victory Card.Treat allied cards that have been destroyed this match as if they were banished.At the end of your opponent's next turn, put copies of each card in your opponent's hand into your hand (excluding XII. Wolfraud, Hanged Man and Treacherous Reversal)."

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        minions = self.Game.minionsandAmuletsonBoard(1) + self.Game.minionsandAmuletsonBoard(2)
        for minion in minions:
            self.Game.banishMinion(self, minion)
        PRINT(self.Game, f"Treacherous Reversal banished all cards on board")
        self.Game.Hand_Deck.extractfromHand(None, self.ID, all=True)
        self.Game.Hand_Deck.extractfromDeck(None, self.ID, all=True)
        PRINT(self.Game, f"Treacherous Reversal banished all cards in your hand and deck")
        i = 0
        cards = []
        for index in self.Game.Counters.cardsPlayedThisGame[3 - self.ID]:
            card = self.Game.cardPool[index]
            if i >= 10:
                break
            if card.name not in ["Treacherous Reversal", "XII. Wolfraud, Hanged Man"]:
                cards.append(card)
                i += 1
        for c in cards:
            self.Game.Hand_Deck.shuffleCardintoDeck([c(self.Game, self.ID)], self.ID)
        PRINT(self.Game,
              f"Treacherous Reversal Put copies of the first 10 cards your opponent played this match into your deck")
        self.Game.Counters.minionsDiedThisGame[self.ID] = []
        self.Game.heroes[self.ID].status["Draw to Win"] = 1
        trigger = Trig_TreacherousReversal(self.Game.heroes[3 - self.ID])
        # for t in self.entity.Game.heroes[self.entity.ID].trigsBoard:
        #     if type(t) == type(trigger):
        #         return
        self.Game.heroes[3 - self.ID].trigsBoard.append(trigger)
        trigger.connect()
        return None


class Trig_TreacherousReversal(TrigBoard):
    def __init__(self, entity):
        self.blank_init(entity, ["TurnEnds"])

    def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.onBoard and ID == self.entity.ID

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        cards = []
        for card in self.entity.Game.Hand_Deck.hands[self.entity.ID]:
            if card.name not in ["Treacherous Reversal", "XII. Wolfraud, Hanged Man"]:
                cards.append(card)
        for c in cards:
            self.entity.Game.Hand_Deck.addCardtoHand([type(c)], 3 - self.entity.ID, "type")
        PRINT(self.entity.Game,
              "At the end of your opponent's next turn, put copies of each card in your opponent's hand into your hand")
        for t in self.entity.trigsBoard:
            if type(t) == Trig_TreacherousReversal:
                t.disconnect()
                self.entity.trigsBoard.remove(t)
                break


class ReclusivePonderer_Accelerate(SVSpell):
    Class, name = "Forestcraft", "Reclusive Ponderer"
    requireTarget, mana = False, 1
    index = "SV_Fortune~Forestcraft~Spell~1~Reclusive Ponderer~Accelerate~Uncollectible"
    description = "Draw a card."

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        PRINT(self.Game, "Reclusive Ponderer's Accelerate let player draw a card.")
        self.Game.Hand_Deck.drawCard(self.ID)
        return None


class ReclusivePonderer(SVMinion):
    Class, race, name = "Forestcraft", "", "Reclusive Ponderer"
    mana, attack, health = 4, 3, 3
    index = "SV_Fortune~Forestcraft~Minion~4~3~3~None~Reclusive Ponderer~Stealth~Accelerate"
    requireTarget, keyWord, description = False, "Stealth", "Accelerate (1): Draw a card. Ambush."
    accelerateSpell = ReclusivePonderer_Accelerate
    attackAdd, healthAdd = 2, 2

    def getMana(self):
        if self.Game.Manas.manas[self.ID] < self.mana:
            return 1
        else:
            return self.mana

    def willAccelerate(self):
        curMana = self.Game.Manas.manas[self.ID]
        return self.mana > curMana >= 1

    def effectCanTrigger(self):
        self.effectViable = "sky blue" if self.willAccelerate() else False


class ChipperSkipper_Accelerate(SVSpell):
    Class, name = "Forestcraft", "Chipper Skipper"
    requireTarget, mana = False, 1
    index = "SV_Fortune~Forestcraft~Spell~1~Chipper Skipper~Accelerate~Uncollectible"
    description = "Summon a Fighter"

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        PRINT(self.Game, "Chipper Skipper's Accelerate Summon a Fighter.")
        self.Game.summon([Fighter(self.Game, self.ID)], (-1, "totheRightEnd"),
                         self.ID)
        return None


class ChipperSkipper(SVMinion):
    Class, race, name = "Forestcraft", "", "Chipper Skipper"
    mana, attack, health = 4, 4, 3
    index = "SV_Fortune~Forestcraft~Minion~4~4~3~None~Chipper Skipper~Accelerate"
    requireTarget, keyWord, description = False, "", "Accelerate (1): Summon a Fighter.(Can only Accelerate if a follower was played this turn.)Whenever you play a card using its Accelerate effect, summon a Fighter and evolve it."
    accelerateSpell = ChipperSkipper_Accelerate
    attackAdd, healthAdd = 2, 2

    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.trigsBoard = [Trig_ChipperSkipper(self)]

    def getMana(self):
        if self.Game.Manas.manas[self.ID] < self.mana and self.Game.Counters.numMinionsPlayedThisTurn[self.ID] > 0:
            return 1
        else:
            return self.mana

    def willAccelerate(self):
        curMana = self.Game.Manas.manas[self.ID]
        return self.mana > curMana >= 1 and self.Game.Counters.numMinionsPlayedThisTurn[self.ID] > 0

    def effectCanTrigger(self):
        self.effectViable = "sky blue" if self.willAccelerate() and self.targetExists() else False


class Trig_ChipperSkipper(TrigBoard):
    def __init__(self, entity):
        self.blank_init(entity, ["SpellPlayed"])

    def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
        return subject.ID == self.entity.ID and self.entity.onBoard and "~Accelerate" in subject.index

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        if "~Accelerate" in subject.index:
            PRINT(self.entity.Game, "Chipper Skipper summons a Fighter and let it evolve.")
            fighter = Fighter(self.entity.Game, self.entity.ID)
            self.entity.Game.summon([fighter], (-1, "totheRightEnd"),
                                    self.entity.ID)
            fighter.evolve()


class FairyAssault(SVSpell):
    Class, name = "Forestcraft", "Fairy Assault"
    requireTarget, mana = False, 4
    index = "SV_Fortune~Forestcraft~Spell~4~Fairy Assault"
    description = "Summon 4 Fairies and give them Rush. Enhance (8): Evolve them instead."

    def getMana(self):
        if self.Game.Manas.manas[self.ID] >= 8:
            return 8
        else:
            return self.mana

    def willEnhance(self):
        return self.Game.Manas.manas[self.ID] >= 8

    def effectCanTrigger(self):
        self.effectViable = self.willEnhance()

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        minions = [Fairy(self.Game, self.ID) for i in range(4)]
        self.Game.summon(minions, (-1, "totheRightEnd"), self.ID)
        PRINT(self.Game, "Fairy Assault summons 4 Fairies")
        if comment == 8:
            for minion in minions:
                if minion.onBoard:
                    minion.evolve()
                    PRINT(self.Game, "Fairy Assault let them evolves")
        else:
            for minion in minions:
                if minion.onBoard:
                    minion.getsKeyword("Rush")
                    PRINT(self.Game, "Fairy Assault give them Rush")
        return None


class OptimisticBeastmaster(SVMinion):
    Class, race, name = "Forestcraft", "", "Optimistic Beastmaster"
    mana, attack, health = 5, 4, 5
    index = "SV_Fortune~Forestcraft~Minion~5~4~5~None~Optimistic Beastmaster~Battlecry"
    requireTarget, keyWord, description = False, "", "Fanfare: Put a random follower with Accelerate from your deck into your hand. Whenever you play a card using its Accelerate effect, deal 2 damage to all enemies."
    attackAdd, healthAdd = 2, 2

    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.trigsBoard = [Trig_OptimisticBeastmaster(self)]

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        curGame = self.Game
        if curGame.mode == 0:
            PRINT(self.Game,
                  "Optimistic Beastmaster's Fanfare puts a random a random follower with Accelerate from your deck into your hand.")
            if curGame.guides:
                i = curGame.guides.pop(0)
            else:
                minions = [i for i, card in enumerate(curGame.Hand_Deck.decks[self.ID]) if
                           card.type == "Minion" and "~Accelerate" in card.index]
                i = npchoice(minions) if minions else -1
                curGame.fixedGuides.append(i)
            if i > -1: curGame.Hand_Deck.drawCard(self.ID, i)


class Trig_OptimisticBeastmaster(TrigBoard):
    def __init__(self, entity):
        self.blank_init(entity, ["SpellPlayed"])

    def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
        return subject.ID == self.entity.ID and self.entity.onBoard and "~Accelerate" in subject.index

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        if "~Accelerate" in subject.index:
            enemies = self.entity.Game.minionsonBoard(3 - self.entity.ID) + self.entity.Game.heroes[3 - self.entity.ID]
            PRINT(self.entity.Game, f"Optimistic Beastmaster deals 2 damage to all all enemies.")
            self.entity.dealsAOE(enemies, [2 for obj in enemies])


class Terrorformer(SVMinion):
    Class, race, name = "Forestcraft", "", "Terrorformer"
    mana, attack, health = 6, 4, 4
    index = "SV_Fortune~Forestcraft~Minion~6~4~4~None~Terrorformer~Battlecry~Fusion~Legendary"
    requireTarget, keyWord, description = True, "", "Fusion: Forestcraft followers that originally cost 2 play points or more. Whenever 2 or more cards are fused to this card at once, gain +2/+0 and draw a card. Fanfare: If at least 2 cards are fused to this card, gain Storm. Then, if at least 4 cards are fused to this card, destroy an enemy follower."
    attackAdd, healthAdd = 2, 2

    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.fusion = 1
        self.fusionMaterials = 0

    def targetCorrect(self, target, choice=0):
        if isinstance(target, list): target = target[0]
        return self.fusionMaterials >= 4 and target.type == "Minion" and target.ID != self.ID and target.onBoard and "Taunt" not in target.race

    def targetExists(self, choice=0):
        return self.selectableEnemyMinionExists() and self.fusionMaterials >= 4

    def findFusionMaterials(self):
        return [card for card in self.Game.Hand_Deck.hands[self.ID] if
                card.type == "Minion" and card != self and card.Class == "Forestcraft" and type(card).mana >= 2]

    def effectCanTrigger(self):
        self.effectViable = self.fusionMaterials >= 2

    def fusionDecided(self, objs):
        if objs:
            self.fusionMaterials += len(objs)
            self.Game.Hand_Deck.extractfromHand(self, enemyCanSee=True)
            for obj in objs: self.Game.Hand_Deck.extractfromHand(obj, enemyCanSee=True)
            self.Game.Hand_Deck.addCardtoHand(self, self.ID)
            if len(objs) >= 2:
                PRINT(self.Game,
                      "Terrorformer's Fusion involves more than 1 minion. It gains +2/+0 and lets player draw a card")
                self.buffDebuff(2, 0)
                self.Game.Hand_Deck.drawCard(self.ID)
            self.fusion = 0  # 一张卡每回合只有一次融合机会

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if self.fusionMaterials >= 2:
            PRINT(self.Game, "Terrorformer's Fanfare gives minion Storm as it has no less than 2 fusion materials")
            self.getsKeyword("Charge")
            if self.fusionMaterials > 4 and target:
                if isinstance(target, list): target = target[0]
                PRINT(self.Game, f"Terrorformer's Fanfare destroys enemy follower {target.name}")
                self.Game.killMinion(self, target)
        return target


class DeepwoodWolf_Accelerate(SVSpell):
    Class, name = "Forestcraft", "Deepwood Wolf"
    requireTarget, mana = True, 1
    index = "SV_Fortune~Forestcraft~Spell~1~Deepwood Wolf~Accelerate~Uncollectible"
    description = "Return an allied follower or amulet to your hand. Draw a card."

    def targetCorrect(self, target, choice=0):
        if isinstance(target, list): target = target[0]
        return target.type in ["Minion", "Amulet"] and target.ID == self.ID and target.onBoard

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if target:
            if isinstance(target, list): target = target[0]
            self.Game.returnMiniontoHand(target, deathrattlesStayArmed=False)
            self.Game.Hand_Deck.drawCard(self.ID)
            PRINT(self.Game, f"Deepwood Wolf returns {target.name} to your hand and draw a card")
        return target


class DeepwoodWolf(SVMinion):
    Class, race, name = "Forestcraft", "", "Deepwood Wolf"
    mana, attack, health = 7, 3, 3
    index = "SV_Fortune~Forestcraft~Minion~7~3~3~None~Deepwood Wolf~Charge~Accelerate"
    requireTarget, keyWord, description = True, "Charge", "Accelerate (1): Return an allied follower or amulet to your hand. Draw a card. Storm. When you play a card using its Accelerate effect, evolve this follower."
    accelerateSpell = DeepwoodWolf_Accelerate
    attackAdd, healthAdd = 3, 3

    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.trigsBoard = [Trig_DeepwoodWolf(self)]

    def getMana(self):
        if self.Game.Manas.manas[self.ID] < self.mana:
            return 1
        else:
            return self.mana

    def targetCorrect(self, target, choice=0):
        if self.willAccelerate():
            if isinstance(target, list): target = target[0]
            return target.type in ["Minion", "Amulet"] and target.ID == self.ID and target.onBoard
        return False

    def willAccelerate(self):
        curMana = self.Game.Manas.manas[self.ID]
        return self.mana > curMana >= 1

    def effectCanTrigger(self):
        self.effectViable = "sky blue" if self.willAccelerate() and self.targetExists() else False

    def returnTrue(self, choice=0):
        if self.willAccelerate():
            return not self.targets
        return False

    def available(self):
        if self.willAccelerate():
            return self.selectableFriendlyMinionExists() or self.selectableFriendlyAmuletExists()
        return True

    def targetExists(self, choice=0):
        return self.selectableFriendlyMinionExists() or self.selectableFriendlyAmuletExists()


class Trig_DeepwoodWolf(TrigBoard):
    def __init__(self, entity):
        self.blank_init(entity, ["SpellPlayed"])

    def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
        return subject.ID == self.entity.ID and self.entity.onBoard and "~Accelerate" in subject.index

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        if "~Accelerate" in subject.index:
            PRINT(self.entity.Game, f"Deepwood Wolf evolves.")
            self.entity.evolve()


class LionelWoodlandShadow_Accelerate(SVSpell):
    Class, name = "Forestcraft", "Lionel, Woodland Shadow"
    requireTarget, mana = True, 1
    index = "SV_Fortune~Forestcraft~Spell~1~Lionel, Woodland Shadow~Accelerate~Uncollectible"
    description = "Deal 5 damage to an enemy"

    def targetCorrect(self, target, choice=0):
        if isinstance(target, list): target = target[0]
        return target.type == "Minion" and target.ID != self.ID and target.onBoard

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if target:
            if isinstance(target, list): target = target[0]
            damage = (5 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
            PRINT(self.Game, f"Lionel, Woodland Shadow, as spell, deals {damage} damage to enemy {target.name}.")
            self.dealsDamage(target, damage)
        return target


class LionelWoodlandShadow(SVMinion):
    Class, race, name = "Forestcraft", "", "Lionel, Woodland Shadow"
    mana, attack, health = 7, 5, 6
    index = "SV_Fortune~Forestcraft~Minion~7~5~6~None~Lionel, Woodland Shadow~Battlecry~Accelerate"
    requireTarget, keyWord, description = True, "", "Accelerate 2: Deal 1 damage to an enemy. Fanfare: xxx. Deal 3 damage to an enemy minion, and deal 1 damage to the enemy hero"
    accelerateSpell = LionelWoodlandShadow_Accelerate
    attackAdd, healthAdd = 2, 2

    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.trigsBoard = [Trig_LionelWoodlandShadow(self)]

    def getMana(self):
        if self.Game.Manas.manas[self.ID] < self.mana and self.Game.Counters.evolvedThisTurn[self.ID] > 0:
            return 1
        else:
            return self.mana

    def willAccelerate(self):
        curMana = self.Game.Manas.manas[self.ID]
        return self.mana > curMana >= 1 and self.Game.Counters.evolvedThisTurn[self.ID] > 0

    def effectCanTrigger(self):
        self.effectViable = "sky blue" if self.willAccelerate() and self.targetExists() else False

    def available(self):
        if self.willAccelerate():
            return self.selectableEnemyMinionExists()
        return True

    def targetExists(self, choice=0):
        return self.selectableEnemyMinionExists()

    def targetCorrect(self, target, choice=0):
        if isinstance(target, list): target = target[0]
        return target.type == "Minion" and target.ID != self.ID and target.onBoard

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if target:
            if isinstance(target, list): target = target[0]
            health = target.health
            PRINT(self.Game, f"Lionel, Woodland Shadow deals 5 damage to enemy {target.name}.")
            self.dealsDamage(target, 5)
            if health <= 5:
                self.evolve()
                PRINT(self.Game, f"Lionel, Woodland Shadow evolves")
        return target

    def inEvolving(self):
        trigger = Trig_LionelWoodlandShadow(self)
        self.trigsBoard.append(trigger)
        trigger.connect()


class Trig_LionelWoodlandShadow(TrigBoard):
    def __init__(self, entity):
        self.blank_init(entity, ["MinionPlayed"])

    def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.onBoard and subject.ID != self.entity.ID

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        PRINT(self.entity.Game, f"Lionel, Woodland Shadow deals 10 damage to enemy {subject.name}.")
        self.entity.dealsDamage(subject, 10)
        for t in self.entity.trigsBoard:
            if type(t) == Trig_LionelWoodlandShadow:
                t.disconnect()
                self.entity.trigsBoard.remove(t)
                break
        trigger = Trig_EndLionelWoodlandShadow(self.entity)
        self.entity.trigsBoard.append(trigger)
        trigger.connect()


class Trig_EndLionelWoodlandShadow(TrigBoard):
    def __init__(self, entity):
        self.blank_init(entity, ["TurnEnds"])

    def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.onBoard and ID != self.entity.ID

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        for t in self.entity.trigsBoard:
            if type(t) == Trig_EndLionelWoodlandShadow:
                t.disconnect()
                self.entity.trigsBoard.remove(t)
                break
        trigger = Trig_LionelWoodlandShadow(self.entity)
        self.entity.trigsBoard.append(trigger)
        trigger.connect()


"""Swordcraft cards"""


class ErnestaWeaponsHawker(SVMinion):
    Class, race, name = "Swordcraft", "Officer", "Ernesta, Weapons Hawker"
    mana, attack, health = 1, 1, 1
    index = "SV_Fortune~Swordcraft~Minion~1~1~1~Officer~Ernesta, Weapons Hawker~Battlecry"
    requireTarget, keyWord, description = False, "", "Fanfare: Rally (10) - Put a Dread Hound into your hand."
    attackAdd, healthAdd = 2, 2

    def effectCanTrigger(self):
        self.effectViable = self.Game.Counters.numMinionsSummonedThisGame[self.ID] >= 10

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if self.Game.Counters.numMinionsSummonedThisGame[self.ID] >= 10:
            self.Game.Hand_Deck.addCardtoHand(DreadHound(self.Game, self.ID), self.ID)
        return None


class DreadHound(SVMinion):
    Class, race, name = "Swordcraft", "Officer", "Dread Hound"
    mana, attack, health = 1, 4, 4
    index = "SV_Fortune~Swordcraft~Minion~1~4~4~Officer~Dread Hound~Battlecry~Bane~Taunt~Uncollectible"
    requireTarget, keyWord, description = False, "Bane,Taunt", "Bane.Ward.Fanfare: Give a random allied Ernesta, Weapons Hawker Last Words - Deal 4 damage to a random enemy follower."
    attackAdd, healthAdd = 2, 2

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        curGame = self.Game
        if curGame.mode == 0:
            minion = None
            if curGame.guides:
                i, where = curGame.guides.pop(0)
                if where: minion = curGame.find(i, where)
            else:
                chars = self.Game.minionsAlive(self.ID)
                targets = []
                for t in chars:
                    if t.name == "Ernesta, Weapons Hawker":
                        targets.append(t)
                if targets:
                    minion = npchoice(targets)
                    curGame.fixedGuides.append((minion.position, minion.type + str(minion.ID)))
                else:
                    curGame.fixedGuides.append((0, ''))
            if minion:
                PRINT(self.Game,
                      f"Dread Hound's Fanfare gives {minion.name} Last Words - Deal 4 damage to a random enemy follower.")
                deathrattle = Deathrattle_ErnestaWeaponsHawker(minion)
                minion.deathrattles.append(deathrattle)
                if minion.onBoard:
                    deathrattle.connect()
        return None


class Deathrattle_ErnestaWeaponsHawker(Deathrattle_Minion):
    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        curGame = self.entity.Game
        if curGame.mode == 0:
            enemy = None
            if curGame.guides:
                i, where = curGame.guides.pop(0)
                if where: enemy = curGame.find(i, where)
            else:
                chars = curGame.minionsAlive(3 - self.entity.ID)
                if chars:
                    enemy = npchoice(chars)
                    curGame.fixedGuides.append((enemy.position, enemy.type + str(enemy.ID)))
                else:
                    curGame.fixedGuides.append((0, ''))
            if enemy:
                PRINT(self.entity.Game, f"Last Words: Deal 4 damage to {enemy.name}")
                self.entity.dealsDamage(enemy, 4)


class PompousSummons(SVSpell):
    Class, name = "Swordcraft", "Pompous Summons"
    requireTarget, mana = False, 1
    index = "SV_Fortune~Swordcraft~Spell~1~Pompous Summons"
    description = "Put a random Swordcraft follower from your deck into your hand.Rally (10): Put 2 random Swordcraft followers into your hand instead."

    def effectCanTrigger(self):
        self.effectViable = self.Game.Counters.numMinionsSummonedThisGame[self.ID] >= 10

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        n = 2 if self.Game.Counters.numMinionsSummonedThisGame[self.ID] >= 10 else 1
        for i in range(n):
            curGame = self.Game
            if curGame.mode == 0:
                if curGame.guides:
                    i = curGame.guides.pop(0)
                else:
                    minions = [i for i, card in enumerate(curGame.Hand_Deck.decks[self.ID]) if
                               card.type == "Minion" and card.Class == "Swordcraft"]
                    i = npchoice(minions) if minions else -1
                    curGame.fixedGuides.append(i)
                if i > -1:
                    curGame.Hand_Deck.drawCard(self.ID, i)
                    PRINT(self.Game, f"Pompous Summons let you draw a Swordcraft minion.")
        return None


class DecisiveStrike(SVSpell):
    Class, name = "Swordcraft", "Decisive Strike"
    requireTarget, mana = True, 1
    index = "SV_Fortune~Swordcraft~Spell~1~Decisive Strike~Enhance"
    description = "Deal X damage to an enemy follower. X equals the attack of the highest-attack Commander follower in your hand.Enhance (5): Deal X damage to all enemy followers instead."

    def getMana(self):
        if self.Game.Manas.manas[self.ID] >= 5:
            return 5
        else:
            return self.mana

    def willEnhance(self):
        return self.Game.Manas.manas[self.ID] >= 5

    def effectCanTrigger(self):
        self.effectViable = self.willEnhance()

    def targetExists(self, choice=0):
        if self.willEnhance():
            return False
        return self.selectableEnemyMinionExists()

    def targetCorrect(self, target, choice=0):
        if isinstance(target, list): target = target[0]
        return target.type == "Minion" and target.ID != self.ID and target.onBoard

    def available(self):
        if self.willEnhance():
            return True
        return self.selectableEnemyMinionExists()

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        damage = 0
        for card in self.Game.Hand_Deck.hands[self.ID]:
            if card.type == "Minion" and "Commander" in card.race and card.attack > damage:
                damage = card.attack
        damage = (damage + self.countSpellDamage()) * (2 ** self.countDamageDouble())
        if comment == 5:
            targets = self.Game.minionsonBoard(3 - self.ID)
            self.dealsAOE(targets, [damage for obj in targets])
            PRINT(self.Game, f"Decisive Strike deals {damage} damage to all enemies")
        else:
            if target:
                if isinstance(target, list): target = target[0]
                PRINT(self.Game, f"Decisive Strike deals {damage} damage to minion {target.name}")
                self.dealsDamage(target, damage)
        return target


class HonorableThief(SVMinion):
    Class, race, name = "Swordcraft", "Officer", "Honorable Thief"
    mana, attack, health = 2, 2, 1
    index = "SV_Fortune~Swordcraft~Minion~2~2~1~Officer~Honorable Thief~Battlecry~Deathrattle"
    requireTarget, keyWord, description = False, "", "Fanfare: Rally (7) - Evolve this follower. Last Words: Put a Gilded Boots into your hand."
    attackAdd, healthAdd = 2, 2

    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.deathrattles = [Deathrattle_HonorableThief(self)]

    def effectCanTrigger(self):
        self.effectViable = self.Game.Counters.numMinionsSummonedThisGame[self.ID] >= 7

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if self.Game.Counters.numMinionsSummonedThisGame[self.ID] >= 7:
            self.evolve()
        return None


class Deathrattle_HonorableThief(Deathrattle_Minion):
    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        PRINT(self.entity.Game, "Last Words: Add a 'GildedBoots' to your hand triggers.")
        self.entity.Game.Hand_Deck.addCardtoHand(GildedBoots, self.entity.ID, "type")


class ShieldPhalanx(SVSpell):
    Class, name = "Swordcraft", "Shield Phalanx"
    requireTarget, mana = False, 2
    index = "SV_Fortune~Swordcraft~Spell~2~Shield Phalanx"
    description = "Summon a Shield Guardian and Knight.Rally (15): Summon a Frontguard General instead of a Shield Guardian."

    def effectCanTrigger(self):
        self.effectViable = self.Game.Counters.numMinionsSummonedThisGame[self.ID] >= 15

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if self.Game.Counters.numMinionsSummonedThisGame[self.ID] >= 15:
            PRINT(self.Game, "Shield Phalanx summons a Frontguard General and Knight.")
            self.Game.summon([FrontguardGeneral(self.Game, self.ID), Knight(self.Game, self.ID)],
                             (-1, "totheRightEnd"), self.ID)
        else:
            PRINT(self.Game, "Shield Phalanx summons a Shield Guardian and Knight.")
            self.Game.summon([ShieldGuardian(self.Game, self.ID), Knight(self.Game, self.ID)],
                             (-1, "totheRightEnd"), self.ID)
        return None


class FrontguardGeneral(SVMinion):
    Class, race, name = "Swordcraft", "Commander", "Frontguard General"
    mana, attack, health = 7, 5, 6
    index = "SV_Fortune~Swordcraft~Minion~7~5~6~Commander~Frontguard General~Taunt~Deathrattle"
    requireTarget, keyWord, description = False, "Taunt", "Ward.Last Words: Summon a Fortress Guard."
    attackAdd, healthAdd = 2, 2

    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.deathrattles = [Deathrattle_FrontguardGeneral(self)]


class Deathrattle_FrontguardGeneral(Deathrattle_Minion):
    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        PRINT(self.entity.Game, "Last Words: Summon a Fortress Guard.")
        self.entity.Game.summon([FortressGuard(self.entity.Game, self.entity.ID)], (-1, "totheRightEnd"),
                                self.entity.ID)


class FortressGuard(SVMinion):
    Class, race, name = "Swordcraft", "Officer", "Fortress Guard"
    mana, attack, health = 3, 2, 3
    index = "SV_Fortune~Swordcraft~Minion~3~2~3~Officer~Fortress Guard~Taunt~Uncollectible"
    requireTarget, keyWord, description = False, "Taunt", "Ward"
    attackAdd, healthAdd = 2, 2


class EmpressofSerenity(SVMinion):
    Class, race, name = "Swordcraft", "Commander", "Empress of Serenity"
    mana, attack, health = 3, 2, 2
    index = "SV_Fortune~Swordcraft~Minion~3~2~2~Commander~Empress of Serenity~Battlecry~Enhance"
    requireTarget, keyWord, description = False, "", "Fanfare: Summon a Shield Guardian.Enhance (5): Summon 3 instead.Enhance (10): Give +3/+3 to all allied Shield Guardians."
    attackAdd, healthAdd = 2, 2

    def getMana(self):
        if self.Game.Manas.manas[self.ID] >= 10:
            return 10
        elif self.Game.Manas.manas[self.ID] >= 5:
            return 5
        else:
            return self.mana

    def willEnhance(self):
        return self.Game.Manas.manas[self.ID] >= 5

    def effectCanTrigger(self):
        self.effectViable = self.willEnhance()

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        PRINT(self.Game,
              "Empress of Serenity's Fanfare summons a 1/1 Shield Guardian with Taunt.")
        self.Game.summon([ShieldGuardian(self.Game, self.ID)], (-11, "totheRightEnd"), self.ID)
        if comment >= 5:
            PRINT(self.Game,
                  "Empress of Serenity's Fanfare summons two 1/1 Shield Guardian with Taunt.")
            self.Game.summon([ShieldGuardian(self.Game, self.ID) for i in range(2)], (-11, "totheRightEnd"),
                             self.ID)
            if comment == 10:
                for minion in self.Game.minionsonBoard(self.ID):
                    if type(minion) == ShieldGuardian:
                        minion.buffDebuff(3, 3)
                PRINT(self.Game,
                      "Empress of Serenity's Fanfare give +3/+3 to all allied Shield Guardians.")
        return None


class VIIOluonTheChariot(SVMinion):
    Class, race, name = "Swordcraft", "Commander", "VII. Oluon, The Chariot"
    mana, attack, health = 3, 3, 3
    index = "SV_Fortune~Swordcraft~Minion~3~3~3~Commander~VII. Oluon, The Chariot~Battlecry~Legendary"
    requireTarget, keyWord, description = False, "", "Fanfare: Enhance (7) - Transform this follower into a VII. Oluon, Runaway Chariot.At the end of your turn, randomly activate 1 of the following effects.-Gain Ward.-Summon a Knight.-Deal 2 damage to the enemy leader."
    attackAdd, healthAdd = 2, 2

    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.trigsBoard = [Trig_VIIOluonTheChariot(self)]

    def getMana(self):
        if self.Game.Manas.manas[self.ID] >= 7:
            return 7
        else:
            return self.mana

    def willEnhance(self):
        return self.Game.Manas.manas[self.ID] >= 7

    def effectCanTrigger(self):
        self.effectViable = self.willEnhance()

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if comment == 7:
            self.Game.transform(self, VIIOluonRunawayChariot(self.Game, self.ID))
        return None


class Trig_VIIOluonTheChariot(TrigBoard):
    def __init__(self, entity):
        self.blank_init(entity, ["TurnEnds"])

    def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.onBoard and ID == self.entity.ID

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        es = ["T", "H", "K"]
        e = "T"
        curGame = self.entity.Game
        if curGame.mode == 0:
            if curGame.guides:
                i, e = curGame.guides.pop(0)
            else:
                e = np.random.choice(es)
                curGame.fixedGuides.append((0, e))
        if e == "T":
            self.entity.getsKeyword("Taunt")
            PRINT(self.entity.Game,
                  "VII. Oluon, The Chariot get Ward")
        elif e == "H":
            self.entity.dealsDamage(self.entity.Game.heroes[3 - self.entity.ID], 2)
            PRINT(self.entity.Game,
                  "VII. Oluon, The Chariot deals 2 damage to enemy hero")
        elif e == "K":
            PRINT(self.entity.Game,
                  "VII. Oluon, The Chariot summons a 1/1 Shield Guardian with Ward.")
            self.entity.Game.summon([Knight(self.entity.Game, self.entity.ID)], (-11, "totheRightEnd"),
                                    self.entity.ID)


class VIIOluonRunawayChariot(SVMinion):
    Class, race, name = "Swordcraft", "Commander", "VII. Oluon, Runaway Chariot"
    mana, attack, health = 7, 8, 16
    index = "SV_Fortune~Swordcraft~Minion~7~8~16~Commander~VII. Oluon, Runaway Chariot~Uncollectible~Legendary"
    requireTarget, keyWord, description = False, "", "Can't attack.At the end of your turn, randomly deal X damage to an enemy or another ally and then Y damage to this follower. X equals this follower's attack and Y equals the attack of the follower or leader damaged (leaders have 0 attack). Do this 2 times."
    attackAdd, healthAdd = 2, 2

    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.marks["Can't Attack"] = 1
        self.trigsBoard = [Trig_VIIOluonRunawayChariot(self)]


class Trig_VIIOluonRunawayChariot(TrigBoard):
    def __init__(self, entity):
        self.blank_init(entity, ["TurnEnds"])

    def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.onBoard and ID == self.entity.ID

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        for i in range(2):
            if self.entity.onBoard:
                curGame = self.entity.Game
                if curGame.mode == 0:
                    char = None
                    if curGame.guides:
                        i, where = curGame.guides.pop(0)
                        if where: char = curGame.find(i, where)
                    else:
                        objs = curGame.charsAlive(1) + curGame.charsAlive(2)
                        objs.remove(self.entity)
                        if objs:
                            char = npchoice(objs)
                            curGame.fixedGuides.append(
                                (char.ID, "hero") if char.type == "Hero" else (char.position, f"minion{char.ID}"))
                        else:
                            curGame.fixedGuides.append((0, ''))
                    if char:
                        self.entity.dealsDamage(char, self.entity.attack)
                        PRINT(self.entity.Game,
                              f"VII. Oluon, Runaway Chariot deals {self.entity.attack} damage to {char.name}")
                        damage = 0
                        if char.type == "Minion":
                            damage = char.attack
                        char.dealsDamage(self.entity, damage)
                        PRINT(self.entity.Game, f"{char.name} deals {damage} damage to VII. Oluon, Runaway Chariot ")
                        self.entity.Game.gathertheDead()


class PrudentGeneral(SVMinion):
    Class, race, name = "Swordcraft", "Commander", "PrudentGeneral"
    mana, attack, health = 4, 3, 4
    index = "SV_Fortune~Swordcraft~Minion~4~3~4~Commander~Prudent General"
    requireTarget, keyWord, description = False, "", ""
    attackAdd, healthAdd = 2, 2

    def inHandEvolving(self, target=None):
        trigger = Trig_PrudentGeneral(self.Game.heroes[self.ID])
        for t in self.Game.heroes[self.ID].trigsBoard:
            if type(t) == type(trigger):
                return
        self.Game.heroes[self.ID].trigsBoard.append(trigger)
        trigger.connect()


class Trig_PrudentGeneral(TrigBoard):
    def __init__(self, entity):
        self.blank_init(entity, ["TurnEnds"])

    def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.onBoard and ID == self.entity.ID

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        PRINT(self.entity.Game, "Prudent General's ability summons a 2/2 Steelclad Knight.")
        self.entity.Game.summon([SteelcladKnight(self.entity.Game, self.entity.ID)], (-1, "totheRightEnd"),
                                self.entity.ID)


class StrikelanceKnight(SVMinion):
    Class, race, name = "Swordcraft", "Officer", "Strikelance Knight"
    mana, attack, health = 5, 4, 5
    index = "SV_Fortune~Swordcraft~Minion~5~4~5~Officer~Strikelance Knight~Battlecry"
    requireTarget, keyWord, description = False, "", "Fanfare: If an allied Commander card is in play, evolve this follower."
    attackAdd, healthAdd = 2, 2

    def effectCanTrigger(self):
        minions = self.Game.minionsonBoard(self.ID)
        for minion in minions:
            if minion.onBoard and "Commander" in minion.race:
                self.effectViable = True
                return
        self.effectViable = False

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        minions = self.Game.minionsonBoard(self.ID)
        for minion in minions:
            if minion.onBoard and "Commander" in minion.race:
                self.evolve()
                break


class DiamondPaladin(SVMinion):
    Class, race, name = "Swordcraft", "Commander", "Diamond Paladin"
    mana, attack, health = 6, 4, 5
    index = "SV_Fortune~Swordcraft~Minion~6~4~5~Commander~Diamond Paladin~Battlecry~Rush~Legendary"
    requireTarget, keyWord, description = False, "Rush", "Rush.Fanfare: Enhance (8) - Gain the ability to evolve for 0 evolution points.During your turn, whenever this follower attacks and destroys an enemy follower, if this follower is not destroyed, recover 2 play points and gain the ability to attack 2 times this turn."
    attackAdd, healthAdd = 2, 2
    evolveRequireTarget = True

    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.trigsBoard = [Trig_DiamondPaladin(self)]

    def evolveTargetExists(self, choice=0):
        return self.selectableEnemyMinionExists()

    def evolveTargetCorrect(self, target, choice=0):
        if isinstance(target, list): target = target[0]
        return target.type == "Minion" and target.onBoard and target.ID != self.ID

    def getMana(self):
        if self.Game.Manas.manas[self.ID] >= 8:
            return 8
        else:
            return self.mana

    def willEnhance(self):
        return self.Game.Manas.manas[self.ID] >= 8

    def effectCanTrigger(self):
        self.effectViable = self.willEnhance()

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if comment == 8:
            self.marks["Free Evolve"] += 1
        return None

    def inHandEvolving(self, target=None):
        if target:
            if isinstance(target, list): target = target[0]
            target.buffDebuff(-4, 0)
            PRINT(self.Game, f"Diamond Paladin's Fanfare give {target.name} -4/-0.")
        return target

    def extraTargetCorrect(self, target, affair):
        return target.type and target.type == "Minion" and target.ID != self.ID and target.onBoard


class Trig_DiamondPaladin(TrigBoard):
    def __init__(self, entity):
        self.blank_init(entity, ["MinionAttackedMinion"])

    def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
        return subject == self.entity and self.entity.onBoard and (target.health < 1 or target.dead == True) and \
               (self.entity.health > 0 and self.entity.dead == False)

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        PRINT(self.entity.Game,
              f"After {self.entity.name} attacks and kills minion {target.name}, restore 2 mana and can attack 2 times per turn")
        self.entity.getsKeyword("Windfury")
        self.entity.Game.Manas.restoreManaCrystal(2, self.entity.ID)
        trigger = Trig_EndDiamondPaladin(self.entity)
        self.entity.trigsBoard.append(trigger)
        if self.entity.onBoard:
            trigger.connect()


class Trig_EndDiamondPaladin(TrigBoard):
    def __init__(self, entity):
        self.blank_init(entity, ["TurnEnds"])

    def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.onBoard

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        self.entity.Keywords["Windfury"] = 0
        for t in self.entity.trigsBoard:
            if type(t) == Trig_EndDiamondPaladin:
                t.disconnect()
                self.entity.trigsBoard.remove(t)
                break


class SelflessNoble(SVMinion):
    Class, race, name = "Swordcraft", "Commander", "Selfless Noble"
    mana, attack, health = 9, 9, 7
    index = "SV_Fortune~Swordcraft~Minion~9~9~7~Commander~Selfless Noble~Battlecry"
    requireTarget, keyWord, description = True, "", "Fanfare: Discard a card. Gain +X/+X. X equals the original cost of the discarded card."
    attackAdd, healthAdd = 2, 2

    def targetExists(self, choice=0):
        return len(self.Game.Hand_Deck.hands[self.ID]) > 1

    def targetCorrect(self, target, choice=0):
        if isinstance(target, list): target = target[0]
        return target.ID == self.ID and target.inHand and target != self

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if target:
            if isinstance(target, list): target = target[0]
            n = type(target).mana
            self.Game.Hand_Deck.discardCard(self.ID, target)
            self.buffDebuff(n, n)
            PRINT(self.Game, f"Selfless Noble's Fanfare discard {target.name} and get +{n}/+{n}")
        return target


"""Runecraft cards"""


class JugglingMoggy(SVMinion):
    Class, race, name = "Runecraft", "", "Juggling Moggy"
    mana, attack, health = 1, 1, 1
    index = "SV_Fortune~Runecraft~Minion~1~1~1~None~Juggling Moggy~Battlecry~EarthRite"
    requireTarget, keyWord, description = False, "", "Fanfare: Earth Rite - Gain +1/+1 and Last Words: Summon 2 Earth Essences."
    attackAdd, healthAdd = 2, 2

    def effectCanTrigger(self):
        self.effectViable = len(self.Game.earthsonBoard(self.ID)) > 0

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if self.Game.earthRite(self, self.ID):
            self.buffDebuff(1, 1)
            PRINT(self.Game, "Juggling Moggy's Fanfare let it +1/+1 and get Last Word")
            deathrattle = Deathrattle_JugglingMoggy(self)
            self.deathrattles.append(deathrattle)
            if self.onBoard:
                deathrattle.connect()
        return None


class Deathrattle_JugglingMoggy(Deathrattle_Minion):
    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        PRINT(self.entity.Game, f"Last Words: Summon 2 Earth Essences.")
        self.entity.Game.summon([EarthEssence(self.entity.Game, self.entity.ID) for i in range(2)],
                                (-1, "totheRightEnd"), self.entity.ID)


class MagicalAugmentation(SVSpell):
    Class, name = "Runecraft", "Magical Augmentation"
    requireTarget, mana = True, 1
    index = "SV_Fortune~Runecraft~Spell~1~Magical Augmentation~EarthRite"
    description = "Deal 1 damage to an enemy follower. Earth Rite (2): Deal 4 damage instead. Then draw 2 cards."

    def effectCanTrigger(self):
        self.effectViable = len(self.Game.earthsonBoard(self.ID)) >= 2

    def targetExists(self, choice=0):
        return self.selectableEnemyMinionExists()

    def targetCorrect(self, target, choice=0):
        if isinstance(target, list): target = target[0]
        return target.type == "Minion" and target.ID != self.ID and target.onBoard

    def available(self):
        return self.selectableEnemyMinionExists()

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if target:
            if isinstance(target, list): target = target[0]
            if self.Game.earthRite(self, self.ID, 2):
                damage = (4 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
                PRINT(self.Game, f"Magical Augmentation deals {damage} damage to minion {target.name} and draw 2 cards")
                self.dealsDamage(target, damage)
                self.Game.Hand_Deck.drawCard(self.ID)
                self.Game.Hand_Deck.drawCard(self.ID)
            else:
                damage = (1 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
                PRINT(self.Game, f"Magical Augmentation deals {damage} damage to minion {target.name}")
                self.dealsDamage(target, damage)
        return target


class CreativeConjurer(SVMinion):
    Class, race, name = "Runecraft", "", "Creative Conjurer"
    mana, attack, health = 2, 2, 2
    index = "SV_Fortune~Runecraft~Minion~2~2~2~None~Creative Conjurer~Battlecry~EarthRite"
    requireTarget, keyWord, description = False, "", "Fanfare: If there are no allied Earth Sigil amulets in play, summon an Earth Essence. Otherwise, perform Earth Rite: Put a Golem Summoning into your hand."
    attackAdd, healthAdd = 2, 2

    def effectCanTrigger(self):
        self.effectViable = len(self.Game.earthsonBoard(self.ID)) >= 0

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if self.Game.earthRite(self, self.ID):
            PRINT(self.Game, "Creative Conjurer's Fanfare let it +1/+1 and get Last Word")
            self.Game.Hand_Deck.addCardtoHand(GolemSummoning, self.ID, "type")
        else:
            self.Game.summon([EarthEssence(self.Game, self.ID)], (-1, "totheRightEnd"), self.ID)
            PRINT(self.Game, "Creative Conjurer's Fanfare summons an Earth Essence")
        return None


class GolemSummoning(SVSpell):
    Class, name = "Runecraft", "Golem Summoning"
    requireTarget, mana = False, 2
    index = "SV_Fortune~Runecraft~Spell~2~Golem Summoning~Uncollectible"
    description = "Summon a Guardian Golem. If you have 20 cards or less in your deck, evolve it."

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        PRINT(self.Game, "Golem Summoning summons a Guardian Golem")
        minion = GuardianGolem(self.Game, self.ID)
        self.Game.summon([minion], (-1, "totheRightEnd"), self.ID)
        if len(self.Game.Hand_Deck.decks[self.ID]) <= 20:
            minion.evolve()
            PRINT(self.Game, "Golem Summoning let Guardian Golem evolved")
        return None


class LhynkalTheFool(SVMinion):
    Class, race, name = "Runecraft", "", "0. Lhynkal, The Fool"
    mana, attack, health = 2, 2, 2
    index = "SV_Fortune~Runecraft~Minion~2~2~2~None~0. Lhynkal, The Fool~Battlecry~Legendary"
    requireTarget, keyWord, description = False, "", "Fanfare: Choose - Put a Rite of the Ignorant or Scourge of the Omniscient into your hand."
    attackAdd, healthAdd = 2, 2

    def inHandEvolving(self, target=None):
        self.Game.Manas.restoreManaCrystal(2, self.ID)
        PRINT(self.Game, "0. Lhynkal, The Fool restores 2 play points")

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        self.Game.options = [RiteoftheIgnorant(self.Game, self.ID), ScourgeoftheOmniscient(self.Game, self.ID)]
        self.Game.Discover.startDiscover(self)
        return None

    def discoverDecided(self, option, info):
        self.Game.fixedGuides.append(type(option))
        self.Game.Hand_Deck.addCardtoHand(option, self.ID, byDiscover=True)
        PRINT(self.Game,
              f"0. Lhynkal, The Fool's Fanfare put {option.name} in your hand")


class RiteoftheIgnorant(SVSpell):
    Class, name = "Runecraft", "Rite of the Ignorant"
    requireTarget, mana = False, 4
    index = "SV_Fortune~Runecraft~Spell~4~Rite of the Ignorant~Uncollectible~Legendary"
    description = "Give your leader the following effect: At the start of your turn, draw a card and Spellboost it X times. X equals a random number between 1 and 10. Then give it the following effect: At the end of your turn, discard this card. (This leader effect lasts for the rest of the match.)"

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        trigger = Trig_RiteoftheIgnorant(self.Game.heroes[self.ID])
        # for t in self.Game.heroes[self.ID].trigsBoard:
        #     if type(t) == type(trigger):
        #         return
        self.Game.heroes[self.ID].trigsBoard.append(trigger)
        trigger.connect()
        return None


class Trig_RiteoftheIgnorant(TrigBoard):
    def __init__(self, entity):
        self.blank_init(entity, ["TurnStarts"])

    def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.onBoard and ID == self.entity.ID

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        card, mana = self.entity.Game.Hand_Deck.drawCard(self.entity.ID)
        curGame = self.entity.Game
        i = 0
        if curGame.mode == 0:
            if curGame.guides:
                i, e = curGame.guides.pop(0)
            else:
                i = np.random.randint(1, 11)
                curGame.fixedGuides.append((i, ""))
        if "~Spellboost" in card.index:
            card.progress += i
        trigger = Trig_EndRiteoftheIgnorant(card)
        card.trigsHand.append(trigger)
        trigger.connect()
        PRINT(self.entity.Game,
              f"At the start of your turn, draw a card and Spellboost it {i} times.")


class Trig_EndRiteoftheIgnorant(TrigHand):
    def __init__(self, entity):
        self.blank_init(entity, ["TurnEnds"])
        self.temp = True
        self.makesCardEvanescent = True

    # They will be discarded at the end of any turn
    def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.inHand

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        PRINT(self.entity.Game, f"At the end of your turn, discard this card")
        self.entity.Game.Hand_Deck.discardCard(self.entity.ID, self.entity)


class ScourgeoftheOmniscient(SVSpell):
    Class, name = "Runecraft", "Scourge of the Omniscient"
    requireTarget, mana = False, 2
    index = "SV_Fortune~Runecraft~Spell~2~Scourge of the Omniscient~Uncollectible~Legendary"
    description = "Give the enemy leader the following effect: At the end of your turn, reduce your leader's maximum defense by 1. (This effect lasts for the rest of the match.)"

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        trigger = Trig_ScourgeoftheOmniscient(self.Game.heroes[3 - self.ID])
        # for t in self.entity.Game.heroes[self.entity.ID].trigsBoard:
        #     if type(t) == type(trigger):
        #         return
        self.Game.heroes[3 - self.ID].trigsBoard.append(trigger)
        trigger.connect()
        return None


class Trig_ScourgeoftheOmniscient(TrigBoard):
    def __init__(self, entity):
        self.blank_init(entity, ["TurnEnds"])

    def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.onBoard and ID == self.entity.ID

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        PRINT(self.entity.Game,
              "At the end of your turn, reduce your leader's maximum defense by 1.")
        self.entity.health_max -= 1
        self.entity.health = min(self.entity.health, self.entity.health_max)


class AuthoringTomorrow(SVSpell):
    Class, name = "Runecraft", "Authoring Tomorrow"
    requireTarget, mana = False, 2
    index = "SV_Fortune~Runecraft~Spell~2~Authoring Tomorrow"
    description = "Give your leader the following effect: At the end of your turn, if it is your second, fourth, sixth, or eighth turn, deal 1 damage to all enemy followers. If it is your third, fifth, seventh, or ninth turn, draw a card. If it is your tenth turn or later, deal 5 damage to the enemy leader. (This effect is not stackable and is removed after activating 3 times.)"

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        trigger = Trig_AuthoringTomorrow(self.Game.heroes[self.ID])
        # for t in self.entity.Game.heroes[self.entity.ID].trigsBoard:
        #     if type(t) == type(trigger):
        #         return
        self.Game.heroes[self.ID].trigsBoard.append(trigger)
        trigger.connect()
        return None


class Trig_AuthoringTomorrow(TrigBoard):
    def __init__(self, entity):
        self.blank_init(entity, ["TurnEnds"])
        self.counter = 3

    def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.onBoard and ID == self.entity.ID

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        turn = self.entity.Game.Counters.turns[self.entity.ID]
        if turn in [2, 4, 6, 8]:
            targets = self.entity.Game.minionsonBoard(3 - self.entity.ID)
            if targets:
                self.entity.dealsAOE(targets, [1 for obj in targets])
            PRINT(self.entity.Game,
                  "At the end of your turn, deals 1 damage to all enemy followers")
        elif turn in [3, 5, 7, 9]:
            self.entity.Game.Hand_Deck.drawCard(self.entity.ID)
            PRINT(self.entity.Game,
                  "At the end of your turn, draw a card")
        elif turn >= 10:
            self.entity.dealsDamage(self.entity.Game.heroes[3 - self.entity.ID], 5)
            PRINT(self.entity.Game,
                  "At the end of your turn, deal 5 damage to enemy player")
        self.counter -= 1
        if self.counter <= 0:
            for t in self.entity.trigsBoard:
                if t == self:
                    t.disconnect()
                    self.entity.trigsBoard.remove(t)
                    break


class MadcapConjuration(SVSpell):
    Class, name = "Runecraft", "Madcap Conjuration"
    requireTarget, mana = False, 2
    index = "SV_Fortune~Runecraft~Spell~2~Madcap Conjuration"
    description = "Discard your hand.If at least 2 spells were discarded, draw 5 cards.If at least 2 followers were discarded, destroy all followers.If at least 2 amulets were discarded, summon 2 Clay Golems and deal 2 damage to the enemy leader."

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        hands = self.Game.Hand_Deck.hands[self.ID]
        types = {"Spell": 0, "Minion": 0, "Amulet": 0}
        for card in hands:
            if card.type in types:
                types[card.type] += 1
        self.Game.Hand_Deck.discardAll(self.ID)
        PRINT(self.Game, "Madcap Conjuration discards your hand")
        if types["Spell"] >= 2:
            for i in range(5):
                self.Game.Hand_Deck.drawCard(self.ID)
            PRINT(self.Game, "Madcap Conjuration let player draw 5 cards")
        if types["Minion"] >= 2:
            for minion in self.Game.minionsAlive(1) + self.Game.minionsAlive(2):
                self.Game.killMinion(self, minion)
            PRINT(self.Game, "Madcap Conjuration destroys all minions")
        if types["Amulet"] >= 2:
            self.Game.summon([ClayGolem(self.Game, self.ID) for i in range(2)], (-1, "totheRightEnd"), self.ID)
            damage = (2 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
            self.dealsDamage(self.Game.heroes[3 - self.ID], damage)
            PRINT(self.Game, f"Madcap Conjuration summons 2 Clay Golems and deals {damage} damage to enemy player")


class ArcaneAuteur(SVMinion):
    Class, race, name = "Runecraft", "", "Arcane Auteur"
    mana, attack, health = 3, 3, 3
    index = "SV_Fortune~Runecraft~Minion~3~3~3~None~Arcane Auteur~Deathrattle"
    requireTarget, keyWord, description = False, "", "Last Words: Put an Insight into your hand."
    attackAdd, healthAdd = 2, 2

    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.deathrattles = [Deathrattle_ArcaneAuteur(self)]


class Deathrattle_ArcaneAuteur(Deathrattle_Minion):
    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        PRINT(self.entity.Game, "Last Words: Put an Insight into your hand.")
        self.entity.Game.Hand_Deck.addCardtoHand(Insight, self.entity.ID, "type")


class PiquantPotioneer(SVMinion):
    Class, race, name = "Runecraft", "", "Piquant Potioneer"
    mana, attack, health = 4, 3, 3
    index = "SV_Fortune~Runecraft~Minion~4~3~3~None~Piquant Potioneer~Battlecry"
    requireTarget, keyWord, description = False, "", "Fanfare: Choose - Put a Rite of the Ignorant or Scourge of the Omniscient into your hand."
    attackAdd, healthAdd = 2, 2

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        damage = 1
        if len(self.Game.Hand_Deck.decks[self.ID]) <= 20:
            damage = 3
        targets = self.Game.minionsonBoard(3 - self.ID)
        self.dealsAOE(targets, damage)
        PRINT(self.Game, f"Piquant Potioneer's Fanfare deals {damage} damage to all enemy followers")


class ImperatorofMagic(SVMinion):
    Class, race, name = "Runecraft", "", "Imperator of Magic"
    mana, attack, health = 4, 2, 2
    index = "SV_Fortune~Runecraft~Minion~4~2~2~None~Imperator of Magic~Battlecry~Enhance~EarthRite"
    requireTarget, keyWord, description = False, "", "Fanfare: Earth Rite - Summon an Emergency Summoning. Fanfare: Enhance (6) - Recover 1 evolution point."
    attackAdd, healthAdd = 2, 2
    evolveRequireTarget = True

    def evolveTargetExists(self, choice=0):
        return self.selectableEnemyMinionExists()

    def evolveTargetCorrect(self, target, choice=0):
        if isinstance(target, list): target = target[0]
        return target.type == "Minion" and target.onBoard and target.ID != self.ID

    def getMana(self):
        if self.Game.Manas.manas[self.ID] >= 6:
            return 6
        else:
            return self.mana

    def willEnhance(self):
        return self.Game.Manas.manas[self.ID] >= 6

    def effectCanTrigger(self):
        self.effectViable = len(self.Game.earthsonBoard(self.ID)) > 0 or self.willEnhance()

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if self.Game.earthRite(self, self.ID):
            PRINT(self.Game, "Imperator of Magic's summons an Emergency Summoning")
            self.Game.summon(
                [EmergencySummoning(self.Game, self.ID)], (-1, "totheRightEnd"), self.ID)
        if comment == 6:
            self.Game.restoreEvolvePoint(self.ID)
        return None

    def inHandEvolving(self, target=None):
        if target:
            if isinstance(target, list): target = target[0]
            damage = 0
            for amulet in self.Game.Counters.amuletsDestroyedThisGame[self.ID]:
                if "Earth Sigil" in amulet.race:
                    damage += 1
            self.dealsDamage(target, damage)
            PRINT(self.Game, f"Imperator of Magic's Evolve deals {damage} damage to {target.name}")
        return target


class EmergencySummoning(Amulet):
    Class, race, name = "Runecraft", "Earth Sigil", "Emergency Summoning"
    mana = 5
    index = "SV_Fortune~Runecraft~Amulet~5~Earth Sigil~Emergency Summoning~Deathrattle~Uncollectible"
    requireTarget, description = False, "When your opponent plays a follower, destroy this amulet. Last Words: Summon a Guardian Golem and a Clay Golem."

    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.deathrattles = [Deathrattle_EmergencySummoning(self)]
        self.trigsBoard = [Trig_EmergencySummoning(self)]


class Deathrattle_EmergencySummoning(Deathrattle_Minion):
    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        PRINT(self.entity.Game, "Last Words: Summon a Guardian Golem and a Clay Golem.")
        self.entity.Game.summon(
            [GuardianGolem(self.entity.Game, self.entity.ID), ClayGolem(self.entity.Game, self.entity.ID)],
            (-1, "totheRightEnd"), self.entity.ID)


class Trig_EmergencySummoning(TrigBoard):
    def __init__(self, entity):
        self.blank_init(entity, ["MinionPlayed"])

    def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.onBoard and subject.ID != self.entity.ID

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        PRINT(self.entity.Game, f"When your opponent plays a follower, destroy this amulet.")
        self.entity.Game.killMinion(self.entity, self.entity)


class HappyPig(SVMinion):
    Class, race, name = "Neutral", "", "Happy Pig"
    mana, attack, health = 2, 2, 2
    index = "SV_Fortune~Neutral~Minion~2~2~2~None~Happy Pig~Deathrattle"
    requireTarget, keyWord, description = False, "", "Last Words: Restore 1 defense to your leader."
    attackAdd, healthAdd = 2, 2

    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.deathrattles = [Deathrattle_HappyPig(self)]

    def inEvolving(self):
        for t in self.deathrattles:
            if type(t) == Deathrattle_HappyPig:
                t.disconnect()
                self.deathrattles.remove(t)
                break
        deathrattle = Deathrattle_EvolvedHappyPig(self)
        self.deathrattles.append(deathrattle)
        if self.onBoard:
            deathrattle.connect()


class Deathrattle_HappyPig(Deathrattle_Minion):
    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        PRINT(self.entity.Game, "Last Words: Restore 1 defense to your leader.")
        self.entity.restoresHealth(self.entity.Game.heroes[self.entity.ID], 1)


class Deathrattle_EvolvedHappyPig(Deathrattle_Minion):
    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        PRINT(self.entity.Game, "Last Words: Restore 3 defense to your leader.")
        self.entity.restoresHealth(self.entity.Game.heroes[self.entity.ID], 3)


class SweetspellSorcerer(SVMinion):
    Class, race, name = "Runecraft", "", "Sweetspell Sorcerer"
    mana, attack, health = 5, 4, 4
    index = "SV_Fortune~Runecraft~Minion~5~4~4~None~Sweetspell Sorcerer"
    requireTarget, keyWord, description = False, "", "Whenever you play a spell, summon a Happy Pig."
    attackAdd, healthAdd = 2, 2

    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.trigsBoard = [Trig_SweetspellSorcerer(self)]

    def inHandEvolving(self, target=None):
        PRINT(self.Game, "Sweetspell Sorcerer let all Happy pig evolves")
        minions = self.Game.minionsAlive(self.ID)
        for minion in minions:
            if minion.name == "Happy Pig":
                minion.evolve()


class Trig_SweetspellSorcerer(TrigBoard):
    def __init__(self, entity):
        self.blank_init(entity, ["SpellPlayed"])

    def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.onBoard and subject.ID == self.entity.ID

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        PRINT(self.entity.Game, "Sweetspell Sorcerer summons a Happy pig")
        self.entity.Game.summon(
            [HappyPig(self.entity.Game, self.entity.ID)], (-1, "totheRightEnd"), self.entity.ID)


class WitchSnap(SVSpell):
    Class, name = "Runecraft", "Witch Snap"
    requireTarget, mana = True, 2
    index = "SV_Fortune~Runecraft~Spell~2~Witch Snap"
    description = "Deal 1 damage to an enemy follower. Earth Rite (2): Deal 4 damage instead. Then draw 2 cards."

    def targetExists(self, choice=0):
        return self.selectableEnemyMinionExists()

    def targetCorrect(self, target, choice=0):
        if isinstance(target, list): target = target[0]
        return target.type == "Minion" and target.ID != self.ID and target.onBoard

    def available(self):
        return self.selectableEnemyMinionExists()

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if target:
            if isinstance(target, list): target = target[0]
            damage = (3 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
            PRINT(self.Game,
                  f"Witch Snap deals {damage} damage to minion {target.name} and put an Earth Essence to your hand")
            self.dealsDamage(target, damage)
            self.Game.Hand_Deck.addCardtoHand(EarthEssence, self.ID, "type")
        return target


class AdamantineGolem(SVMinion):
    Class, race, name = "Runecraft", "", "Adamantine Golem"
    mana, attack, health = 6, 6, 6
    index = "SV_Fortune~Runecraft~Minion~6~6~6~None~Adamantine Golem~Battlecry~EarthRite~Legendary"
    requireTarget, keyWord, description = False, "", "During your turn, when this card is added to your hand from your deck, if there are 2 allied Earth Sigil amulets or less in play, reveal it and summon an Earth Essence.Fanfare: Randomly activate 1 of the following effects. Earth Rite (X): Do this X more times. X equals the number of allied Earth Sigil amulets in play.-Summon a Guardian Golem.-Put a Witch Snap into your hand and change its cost to 0.-Deal 2 damage to the enemy leader. Restore 2 defense to your leader."
    attackAdd, healthAdd = 2, 2

    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.triggers["Drawn"] = [self.drawn]

    def effectCanTrigger(self):
        self.effectViable = len(self.Game.earthsonBoard(self.ID)) > 0

    def drawn(self):
        if self.Game.turn == self.ID and len(self.Game.earthsonBoard(self.ID)) <= 2:
            self.Game.summon(
                [EarthEssence(self.Game, self.ID)], (-1, "totheRightEnd"), self.ID)
            PRINT(self.Game,
                  f"Adamantine Golem is drawn and summons an Earth Essence")

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        for i in range(len(self.Game.earthsonBoard(self.ID)) + 1):
            if i == 0 or self.Game.earthRite(self, self.ID):
                es = ["S", "P", "D"]
                e = "S"
                curGame = self.Game
                if curGame.mode == 0:
                    if curGame.guides:
                        i, e = curGame.guides.pop(0)
                    else:
                        e = np.random.choice(es)
                        curGame.fixedGuides.append((0, e))
                if e == "S":
                    self.Game.summon(
                        [GuardianGolem(self.Game, self.ID)], (-1, "totheRightEnd"), self.ID)
                    PRINT(self.Game,
                          f"Adamantine Golem's Fanfare summons an Earth Essence")
                elif e == "P":
                    card = WitchSnap(self.Game, self.ID)
                    self.Game.Hand_Deck.addCardtoHand(card, self.ID)
                    ManaMod(card, changeby=-2, changeto=0).applies()
                    PRINT(self.Game,
                          f"Adamantine Golem's Fanfare puts a Witch Snap into your hand and change its cost to 0")
                elif e == "D":
                    self.dealsDamage(self.Game.heroes[3 - self.ID], 2)
                    self.restoresHealth(self.Game.heroes[self.ID], 2)
                    PRINT(self.Game,
                          f"Adamantine Golem's Fanfare deals 2 damage to the enemy leader and restores 2 defense to your leader.")


"""Dragoncraft cards"""


class DragoncladLancer(SVMinion):
    Class, race, name = "Dragoncraft", "", "Dragonclad Lancer"
    mana, attack, health = 1, 1, 1
    index = "SV_Fortune~Dragoncraft~Minion~1~1~1~None~Dragonclad Lancer~Battlecry"
    requireTarget, keyWord, description = True, "", "Fanfare: Deal 4 damage to an enemy follower."
    attackAdd, healthAdd = 2, 2

    def targetExists(self, choice=0):
        return self.selectableFriendlyMinionExists()

    def targetCorrect(self, target, choice=0):
        if isinstance(target, list): target = target[0]
        return target.type == "Minion" and target.ID == self.ID and target.onBoard

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if target:
            if isinstance(target, list): target = target[0]
            self.dealsDamage(target, 2)
            PRINT(self.Game, f"Dragonclad Lancer deals 2 damage to {target.name}")
            self.Game.Hand_Deck.drawCard(self.ID)
            self.buffDebuff(2, 1)
            PRINT(self.Game, f"Dragonclad Lancer gets +2/+1 and draw a card")
        return target


class SpringwellDragonKeeper(SVMinion):
    Class, race, name = "Dragoncraft", "", "Springwell Dragon Keeper"
    mana, attack, health = 2, 2, 2
    index = "SV_Fortune~Dragoncraft~Minion~2~2~2~None~Springwell Dragon Keeper~Battlecry~Enhance"
    requireTarget, keyWord, description = True, "", "Fanfare: Discard a card and deal 4 damage to an enemy follower.(Activates only when both a targetable card is in your hand and a targetable enemy follower is in play.)Enhance (5): Gain +3/+3."
    attackAdd, healthAdd = 2, 2

    def getMana(self):
        if self.Game.Manas.manas[self.ID] >= 5:
            return 5
        else:
            return self.mana

    def willEnhance(self):
        return self.Game.Manas.manas[self.ID] >= 5

    def effectCanTrigger(self):
        self.effectViable = self.willEnhance()

    def returnTrue(self, choice=0):
        return len(self.targets) < 2 and self.targetExists(choice)

    def targetExists(self, choice=0):
        return len(self.Game.Hand_Deck.hands[self.ID]) > 1 and self.selectableEnemyMinionExists(choice=1)

    def targetCorrect(self, target, choice=0):
        if isinstance(target, list):
            allied, enemy = target[0], target[1]
            return allied.ID == self.ID and allied.inHand and allied != self and enemy.type == "Minion" and enemy.ID != self.ID and enemy.onBoard
        else:
            if self.targets or choice:  # When checking the 2nd target
                return target.type == "Minion" and target.ID != self.ID and target.onBoard
            else:  # When checking the 1st target
                return target.ID == self.ID and target.inHand and target != self

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if target:
            allied, enemy = target[0], target[1]
            self.dealsDamage(enemy, 4)
            PRINT(self.Game,
                  f"Springwell Dragon Keeper's Fanfare discard {allied.name} and deals 4 damage to {enemy.name}")
        if comment == 5:
            self.buffDebuff(3, 3)
            PRINT(self.Game,
                  f"Springwell Dragon Keeper's Enhance Fanfare gives it +3/+3")
        return target


class TropicalGrouper(SVMinion):
    Class, race, name = "Dragoncraft", "", "Tropical Grouper"
    mana, attack, health = 2, 2, 2
    index = "SV_Fortune~Dragoncraft~Minion~2~2~2~None~Tropical Grouper~Battlecry~Enhance"
    requireTarget, keyWord, description = False, "", "Fanfare: Enhance (4) - Summon a Tropical Grouper. During your turn, whenever another allied follower evolves, summon a Tropical Grouper."
    attackAdd, healthAdd = 2, 2

    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.trigsBoard = [Trig_TropicalGrouper(self)]

    def getMana(self):
        if self.Game.Manas.manas[self.ID] >= 4:
            return 4
        else:
            return self.mana

    def willEnhance(self):
        return self.Game.Manas.manas[self.ID] >= 4

    def effectCanTrigger(self):
        self.effectViable = self.willEnhance()

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if comment == 4:
            self.Game.summon([TropicalGrouper(self.Game, self.ID)], (-1, "totheRightEnd"),
                             self.ID)
            PRINT(self.Game,
                  f"Tropical Grouper's Enhance Fanfare summons a Tropical Grouper")


class Trig_TropicalGrouper(TrigBoard):
    def __init__(self, entity):
        self.blank_init(entity, ["MinionEvolved"])

    def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
        return subject.ID == self.entity.ID and self.entity.onBoard and subject != self.entity

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        self.entity.Game.summon([TropicalGrouper(self.entity.Game, self.entity.ID)], (-1, "totheRightEnd"),
                                self.entity.ID)
        PRINT(self.entity.Game,
              f"Tropical Grouper summons a Tropical Grouper")


class WavecrestAngler(SVMinion):
    Class, race, name = "Dragoncraft", "", "Wavecrest Angler"
    mana, attack, health = 2, 2, 2
    index = "SV_Fortune~Dragoncraft~Minion~2~2~2~None~Wavecrest Angler~Battlecry"
    requireTarget, keyWord, description = False, "", "Fanfare: Randomly put a copy of a card discarded by an effect this turn into your hand."
    attackAdd, healthAdd = 2, 2

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        curGame = self.Game
        if curGame.mode == 0:
            if curGame.guides:
                i = curGame.guides.pop(0)
            else:
                cards = [i for i, card in enumerate(curGame.Counters.cardsDiscardedThisGame[self.ID])]
                i = npchoice(cards) if cards else -1
                curGame.fixedGuides.append(i)
            if i > -1:
                card = self.Game.cardPool[curGame.Counters.cardsDiscardedThisGame[self.ID][i]]
                self.Game.Hand_Deck.addCardtoHand(card, self.ID, "type")
                PRINT(self.Game,
                      f"Wavecrest Angler's Enhance Fanfare add a {card.name} to hand")


class DraconicCall(SVSpell):
    Class, name = "Dragoncraft", "Draconic Call"
    mana, requireTarget = 2, False
    index = "SV_Fortune~Dragoncraft~Spell~2~Draconic Call"
    description = "Randomly put 1 of the highest-cost Dragoncraft followers from your deck into your hand. If Overflow is active for you, randomly put 2 of the highest-cost Dragoncraft followers into your hand instead."

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        n = 1
        if self.Game.isOverflow(self.ID):
            n = 2
        for i in range(n):
            curGame = self.Game
            highest = 0
            for card in curGame.Hand_Deck.decks[self.ID]:
                if card.mana > highest:
                    highest = card.mana
            if curGame.mode == 0:
                PRINT(self.Game,
                      "Draconic Call 1 of the highest-cost Dragoncraft followers from your deck into your hand.")
                if curGame.guides:
                    i = curGame.guides.pop(0)
                else:
                    minions = [i for i, card in enumerate(curGame.Hand_Deck.decks[self.ID]) if
                               card.type == "Minion" and card.Class == "Dragoncraft" and card.mana == highest]
                    i = npchoice(minions) if minions else -1
                    curGame.fixedGuides.append(i)
                if i > -1: curGame.Hand_Deck.drawCard(self.ID, i)
        return None


class IvoryDragon(SVMinion):
    Class, race, name = "Dragoncraft", "", "Ivory Dragon"
    mana, attack, health = 1, 1, 2
    index = "SV_Fortune~Dragoncraft~Minion~1~1~2~None~Ivory Dragon~Battlecry"
    requireTarget, keyWord, description = False, "", "Fanfare: Draw a card if Overflow is active for you."
    attackAdd, healthAdd = 2, 2

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if self.Game.isOverflow(self.ID):
            self.Game.Hand_Deck.drawCard(self.ID)
            PRINT(self.Game, f"Ivory Dragon's Fanfare draw a card")


class Heliodragon(SVMinion):
    Class, race, name = "Dragoncraft", "", "Heliodragon"
    mana, attack, health = 3, 1, 5
    index = "SV_Fortune~Dragoncraft~Minion~3~1~5~None~Heliodragon"
    requireTarget, keyWord, description = False, "", "If this card is discarded by an effect, summon an Ivory Dragon. Then, if Overflow is active for you, draw a card.During your turn, whenever you discard cards, restore X defense to your leader. X equals the number of cards discarded."
    attackAdd, healthAdd = 2, 2

    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.trigsBoard = [Trig_Heliodragon(self)]
        self.triggers["Discarded"] = [self.whenDiscard]

    def whenDiscard(self):
        self.Game.summon([IvoryDragon(self.Game, self.ID)], (-1, "totheRightEnd"),
                         self.ID)
        PRINT(self.Game,
              f"Heliodragon summons a Tropical Grouper")
        if self.Game.isOverflow(self.ID):
            self.Game.Hand_Deck.drawCard(self.ID)
            PRINT(self.Game, f"Heliodragon draw a card")


class Trig_Heliodragon(TrigBoard):
    def __init__(self, entity):
        self.blank_init(entity, ["PlayerDiscardsCard", "PlayerDiscardsHand"])

    def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
        return ID == self.entity.ID and self.entity.onBoard and number > 0

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        self.entity.restoresHealth(self.entity.Game.heroes[self.entity.ID], number)
        PRINT(self.entity.Game, f"Heliodragon restore {choice} defense to your leader.")


class SlaughteringDragonewt(SVMinion):
    Class, race, name = "Dragoncraft", "", "Slaughtering Dragonewt"
    mana, attack, health = 3, 2, 8
    index = "SV_Fortune~Dragoncraft~Minion~3~2~8~None~Slaughtering Dragonewt~Bane~Battlecry"
    requireTarget, keyWord, description = False, "Bane", "Fanfare: Draw a card if Overflow is active for you."
    attackAdd, healthAdd = 0, 0

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        cards = enumerate(self.Game.Hand_Deck.decks[self.ID])
        for i, card in cards:
            if card.mana in [1, 3, 5, 7, 9]:
                self.Game.Hand_Deck.extractfromDeck(card, self.ID)
                PRINT(self.Game,
                      f"Slaughtering Dragonewt's Fanfare banished all cards in your deck that originally cost 1, 3, 5, 7, or 9 play points.")

    def inHandEvolving(self, target=None):
        minions = self.Game.minionsonBoard(1) + self.Game.minionsonBoard(2)
        self.dealsAOE(minions, [4 for obj in minions])
        PRINT(self.Game,
              f"Slaughtering Dragonewt's Evolve deals 4 damage to all followers.")

    def canAttack(self):
        return self.actionable() and self.status["Frozen"] < 1 \
               and self.attChances_base + self.attChances_extra > self.attTimes \
               and self.marks["Can't Attack"] < 1 and self.Game.isOverflow(self.ID)


class Trig_TurncoatDragons(TrigHand):
    def __init__(self, entity):
        self.blank_init(entity, ["PlayerDiscardsCard"])

    def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.inHand and ID == self.entity.ID

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        self.entity.progress += 1
        self.entity.Game.Manas.calcMana_Single(self.entity)


class CrimsonDragonsSorrow(SVMinion):
    Class, race, name = "Dragoncraft", "", "Crimson Dragon's Sorrow"
    mana, attack, health = 5, 4, 4
    index = "SV_Fortune~Dragoncraft~Minion~5~4~4~None~Crimson Dragon's Sorrow~Taunt~Battlecry~Legendary~Uncollectible"
    requireTarget, keyWord, description = True, "Taunt", "During your turn, whenever you discard cards, subtract X from the cost of this card. X equals the number of cards discarded.Ward.Fanfare: Discard a card. Draw 2 cards."
    attackAdd, healthAdd = 2, 2

    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.trigsHand = [Trig_TurncoatDragons(self)]
        self.progress = 0

    def selfManaChange(self):
        if self.inHand:
            self.mana -= self.progress
            self.mana = max(self.mana, 0)

    def targetExists(self, choice=0):
        return len(self.Game.Hand_Deck.hands[self.ID]) > 1

    def targetCorrect(self, target, choice=0):
        if isinstance(target, list): target = target[0]
        return target.ID == self.ID and target.inHand and target != self

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if target:
            if isinstance(target, list): target = target[0]
            self.Game.Hand_Deck.discardCard(self.ID, target)
            self.Game.Hand_Deck.drawCard(self.ID)
            self.Game.Hand_Deck.drawCard(self.ID)
            PRINT(self.Game, f"Selfless Noble's Fanfare discard {target.name} and draw 2 cards")
        return target


class AzureDragonsRage(SVMinion):
    Class, race, name = "Dragoncraft", "", "Azure Dragon's Rage"
    mana, attack, health = 7, 4, 4
    index = "SV_Fortune~Dragoncraft~Minion~7~4~4~None~Azure Dragon's Rage~Charge~Legendary~Uncollectible"
    requireTarget, keyWord, description = False, "Charge", "During your turn, whenever you discard cards, subtract X from the cost of this card. X equals the number of cards discarded.Ward.Fanfare: Discard a card. Draw 2 cards."
    attackAdd, healthAdd = 2, 2

    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.trigsHand = [Trig_TurncoatDragons(self)]
        self.progress = 0

    def selfManaChange(self):
        if self.inHand:
            self.mana -= self.progress
            self.mana = max(self.mana, 0)


class TurncoatDragonSummoner(SVMinion):
    Class, race, name = "Dragoncraft", "", "Turncoat Dragon Summoner"
    mana, attack, health = 3, 2, 3
    index = "SV_Fortune~Dragoncraft~Minion~3~2~3~None~Turncoat Dragon Summoner~Battlecry~Legendary"
    requireTarget, keyWord, description = True, "", "If this card is discarded by an effect, put a Crimson Dragon's Sorrow into your hand.Ward.Fanfare: Discard a card. Put an Azure Dragon's Rage into your hand."
    attackAdd, healthAdd = 2, 2

    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.triggers["Discarded"] = [self.whenDiscard]

    def whenDiscard(self):
        self.Game.Hand_Deck.addCardtoHand(CrimsonDragonsSorrow, self.ID, "type")
        PRINT(self.Game, f"Selfless Noble's put a Crimson Dragon's Sorrow into your hand")

    def targetExists(self, choice=0):
        return len(self.Game.Hand_Deck.hands[self.ID]) > 1

    def targetCorrect(self, target, choice=0):
        if isinstance(target, list): target = target[0]
        return target.ID == self.ID and target.inHand and target != self

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if target:
            if isinstance(target, list): target = target[0]
            self.Game.Hand_Deck.discardCard(self.ID, target)
            self.Game.Hand_Deck.addCardtoHand(AzureDragonsRage, self.ID, "type")
            PRINT(self.Game,
                  f"Selfless Noble's Fanfare discard {target.name} and put a Azure Dragon's Rage into your hand")
        return target


class DragonsNest(Amulet):
    Class, race, name = "Dragoncraft", "", "Dragon's Nest"
    mana = 1
    index = "SV_Fortune~Dragoncraft~Amulet~1~None~Dragon's Nest"
    requireTarget, description = False, "At the start of your turn, restore 2 defense to your leader, draw a card, and destroy this amulet if Overflow is active for you."

    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.trigsBoard = [Trig_DragonsNest(self)]


class Trig_DragonsNest(TrigBoard):
    def __init__(self, entity):
        self.blank_init(entity, ["TurnStarts"])

    def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.onBoard and ID == self.entity.ID

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        if self.entity.Game.isOverflow(self.entity.ID):
            self.entity.restoresHealth(self.entity.Game.heroes[self.entity.ID], 2)
            self.entity.Game.Hand_Deck.drawCard(self.entity.ID)
            self.entity.Game.killMinion(self.entity, self.entity)
            PRINT(self.entity.Game,
                  f"At the start of your turn, restore 2 defense to your leader, draw a card, and destroy this amulet")


class DragonSpawning(SVSpell):
    Class, name = "Dragoncraft", "Dragon Spawning"
    mana, requireTarget = 3, False
    index = "SV_Fortune~Dragoncraft~Spell~3~Dragon Spawning"
    description = "Summon 2 Dragon's Nests. If you have 10 play point orbs, summon 5 instead."

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        n = 2
        if self.Game.Manas.manasUpper[self.ID] >= 10:
            n = 5
        self.Game.summon([DragonsNest(self.Game, self.ID) for i in range(n)], (-1, "totheRightEnd"),
                         self.ID)
        PRINT(self.Game,
              f"Dragon Spawning summons {n} Dragon's Nests")


class DragonImpact(SVSpell):
    Class, name = "Dragoncraft", "Dragon Impact"
    mana, requireTarget = 4, True
    index = "SV_Fortune~Dragoncraft~Spell~4~Dragon Impact"
    description = "Give +1/+1 and Rush to a Dragoncraft follower in your hand.Deal 5 damage to a random enemy follower.(Can be played only when a targetable card is in your hand.)"

    def available(self):
        for card in self.Game.Hand_Deck.hands[self.ID]:
            if card.inHand and card != self and card.type == "Minion" and card.Class == "Dragoncraft":
                return True
        return False

    def targetExists(self, choice=0):
        for card in self.Game.Hand_Deck.hands[self.ID]:
            if card.inHand and card != self and card.type == "Minion" and card.Class == "Dragoncraft":
                return True
        return False

    def targetCorrect(self, target, choice=0):
        if isinstance(target, list): target = target[0]
        return target.ID == self.ID and target.inHand and target != self and target.type == "Minion" and target.Class == "Dragoncraft"

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if target:
            if isinstance(target, list): target = target[0]
            target.getsKeyword("Rush")
            target.buffDebuff(1, 1)
            PRINT(self.Game,
                  f"Dragon Impact gives {target.name} +1/+1 and Rush")
            curGame = self.Game
            if curGame.mode == 0:
                enemy = None
                if curGame.guides:
                    i, where = curGame.guides.pop(0)
                    if where: enemy = curGame.find(i, where)
                else:
                    chars = curGame.minionsAlive(3 - self.ID)
                    if chars:
                        enemy = npchoice(chars)
                        curGame.fixedGuides.append((enemy.position, enemy.type + str(enemy.ID)))
                    else:
                        curGame.fixedGuides.append((0, ''))
                if enemy:
                    damage = (5 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
                    PRINT(self.Game, f"Dragon Impact deals {damage} damage to {enemy.name}")
                    self.dealsDamage(enemy, damage)
        return target


class XIErntzJustice(SVMinion):
    Class, race, name = "Dragoncraft", "", "XI. Erntz, Justice"
    mana, attack, health = 10, 11, 8
    index = "SV_Fortune~Dragoncraft~Minion~10~11~8~None~XI. Erntz, Justice~Ward~Legendary"
    requireTarget, keyWord, description = False, "Taunt", "Ward.When this follower comes into play, randomly activate 1 of the following effects.-Draw 3 cards.-Evolve this follower.When this follower leaves play, restore 8 defense to your leader. (Transformation doesn't count as leaving play.)"
    attackAdd, healthAdd = -3, 3

    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.appearResponse = [self.whenAppears]
        self.disappearResponse = [self.whenDisppears]

    def whenAppears(self):
        es = ["D", "E"]
        e = "D"
        curGame = self.Game
        if curGame.mode == 0:
            if curGame.guides:
                i, e = curGame.guides.pop(0)
            else:
                e = np.random.choice(es)
                curGame.fixedGuides.append((0, e))
        if e == "D":
            PRINT(self.Game, f"XI. Erntz, Justice appears and lets player draw 3 cards")
            for num in range(3):
                self.Game.Hand_Deck.drawCard(self.ID)
        elif e == "E":
            self.evolve()
            PRINT(self.Game, f"XI. Erntz, Justice appears and evolves")

    def whenDisppears(self):
        PRINT(self.Game, f"XI. Erntz, Justice leaves board and restores 8 health to player")
        self.restoresHealth(self.Game.heroes[self.ID], 8)

    def inEvolving(self):
        self.losesKeyword("Taunt")
        self.getsKeyword("Charge")
        self.marks["Ignore Taunt"] += 1
        self.marks["Enemy Effect Evasive"] += 1
        for f in self.disappearResponse:
            if f.__name__ == "whenDisppears":
                self.disappearResponse.remove(f)


"""Shadowcraft cards"""


class GhostlyMaid(SVMinion):
    Class, race, name = "Shadowcraft", "", "Ghostly Maid"
    mana, attack, health = 2, 2, 2
    index = "SV_Fortune~Shadowcraft~Minion~2~2~2~None~Ghostly Maid~Battlecry"
    requireTarget, keyWord, description = False, "", "Fanfare: If there are any allied amulets in play, summon a Ghost. Then, if there are at least 2 in play, evolve it."
    attackAdd, healthAdd = 2, 2

    def effectCanTrigger(self):
        self.effectViable = len(self.Game.amuletsonBoard(self.ID)) > 0

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if len(self.Game.amuletsonBoard(self.ID)) > 0:
            minion = Ghost(self.Game, self.ID)
            self.Game.summon([minion], (-1, "totheRightEnd"),
                             self.ID)
            PRINT(self.Game,
                  f"Ghostly Maid's Fanfare summons a Ghost")
            if len(self.Game.amuletsonBoard(self.ID)) >= 2:
                minion.evolve()
                PRINT(self.Game,
                      f"Ghostly Maid's Fanfare let the Ghost evolve")
        return None


class BonenanzaNecromancer(SVMinion):
    Class, race, name = "Shadowcraft", "", "Bonenanza Necromancer"
    mana, attack, health = 2, 2, 2
    index = "SV_Fortune~Shadowcraft~Minion~2~2~2~None~Bonenanza Necromancer~Enhance~Battlecry"
    requireTarget, keyWord, description = False, "", "Fanfare: Enhance (7) - Reanimate (10). Whenever you perform Burial Rite, draw a card."
    attackAdd, healthAdd = 2, 2

    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.trigsBoard = [Trig_BonenanzaNecromancer(self)]

    def getMana(self):
        if self.Game.Manas.manas[self.ID] >= 7:
            return 7
        else:
            return self.mana

    def willEnhance(self):
        return self.Game.Manas.manas[self.ID] >= 7

    def effectCanTrigger(self):
        self.effectViable = self.willEnhance()

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if comment == 7:
            minion = self.Game.reanimate(self.ID, 10)
            if minion:
                PRINT(self.Game, f"Bonenanza Necromancer's Enhanced Fanfare summons {minion.name}")
        return None


class Trig_BonenanzaNecromancer(TrigBoard):
    def __init__(self, entity):
        self.blank_init(entity, ["BurialRite"])

    def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.onBoard and ID == self.entity.ID

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        PRINT(self.entity.Game, "Bonenanza Necromancer draw a card")
        self.entity.Game.Hand_Deck.drawCard(self.entity.ID)


class SavoringSlash(SVSpell):
    Class, name = "Shadowcraft", "Savoring Slash"
    requireTarget, mana = True, 2
    index = "SV_Fortune~Shadowcraft~Spell~2~Savoring Slash"
    description = "Deal 3 damage to an enemy follower. Burial Rite: Draw a card."

    def effectCanTrigger(self):
        self.effectViable = not self.Game.Hand_Deck.noMinionsinHand(self.ID, self)

    def returnTrue(self, choice=0):
        if self.Game.Hand_Deck.noMinionsinHand(self.ID, self) or self.Game.space(self.ID) < 1:
            return not self.targets
        else:
            return len(self.targets) < 2

    def available(self):
        return self.selectableEnemyMinionExists(choice=1)

    def targetCorrect(self, target, choice=0):
        if isinstance(target, list):
            if len(target) >= 2:
                allied, enemy = target[0], target[1]
                return allied.type == "Minion" and allied.inHand and allied.ID == self.ID and enemy.type == "Minion" and enemy.ID != self.ID and enemy.onBoard
            else:
                target = target[0]
                return target.type == "Minion" and target.ID != self.ID and target.onBoard
        else:
            if self.targets or choice:  # When checking the 2nd target
                return target.type == "Minion" and target.ID != self.ID and target.onBoard
            else:  # When checking the 1st target
                return target.type == "Minion" and target.ID == self.ID and target.inHand

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if target:
            if len(target) >= 2:
                allied, enemy = target[0], target[1]
                PRINT(self.Game, f"Savoring Slash Burial Rite {allied.name} and draw a card.")
                self.Game.Hand_Deck.burialRite(self.ID, allied)
                self.Game.Hand_Deck.drawCard(self.ID)
            else:
                enemy = target[0]
            damage = (3 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
            PRINT(self.Game, f"Savoring Slash deals {damage} damage to enemy {enemy}.")
            self.dealsDamage(enemy, damage)
        return target


class CoffinoftheUnknownSoul(Amulet):
    Class, race, name = "Shadowcraft", "", "Coffin of the Unknown Soul"
    mana = 2
    index = "SV_Fortune~Shadowcraft~Amulet~2~None~Coffin of the Unknown Soul~Countdown~Battlecry~Deathrattle"
    requireTarget, description = True, "Countdown (1)Fanfare: Burial Rite - Draw a card and add X to this amulet's Countdown. X equals half the original cost of the follower destroyed by Burial Rite (rounded down).Last Words: Summon a copy of the follower destroyed by Burial Rite."

    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.counter = 1
        self.trigsBoard = [Trig_Countdown(self)]
        self.deathrattles = [Deathrattle_CoffinoftheUnknownSoul(self)]

    def effectCanTrigger(self):
        self.effectViable = not self.Game.Hand_Deck.noMinionsinHand(self.ID, self) and self.Game.space(self.ID) >= 1

    def targetExists(self, choice=0):
        return not self.Game.Hand_Deck.noMinionsinHand(self.ID, self) and self.Game.space(self.ID) >= 1

    def targetCorrect(self, target, choice=0):
        if isinstance(target, list): target = target[0]
        return target.ID == self.ID and target.inHand and target != self and target.type == "Minion"

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if target:
            if isinstance(target, list): target = target[0]
            t = type(target)
            self.Game.Hand_Deck.burialRite(self.ID, target)
            PRINT(self.Game, f"Coffin of the Unknown Soul Burial Rite {t.name}")
            for trigger in self.deathrattles:
                if type(trigger) == Deathrattle_CoffinoftheUnknownSoul:
                    trigger.chosenMinionType = t
            self.countdown(self, -int(t.mana / 2))
        return target


class Deathrattle_CoffinoftheUnknownSoul(Deathrattle_Minion):
    def __init__(self, entity):
        self.blank_init(entity)
        self.chosenMinionType = None

    def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
        return target == self.entity and self.chosenMinionType

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        PRINT(self.entity.Game, f"Last Words: Summon a chosen minion {self.chosenMinionType.name} triggers")
        self.entity.Game.summon([self.chosenMinionType(self.entity.Game, self.entity.ID)], (-1, "totheRightEnd"),
                                self.entity.ID)

    def selfCopy(self, newMinion):
        trigger = type(self)(newMinion)
        trigger.chosenMinionType = self.chosenMinionType
        return trigger


class SpiritCurator(SVMinion):
    Class, race, name = "Shadowcraft", "", "Spirit Curator"
    mana, attack, health = 3, 3, 3
    index = "SV_Fortune~Shadowcraft~Minion~3~3~3~None~Spirit Curator~Battlecry"
    requireTarget, keyWord, description = True, "", "Fanfare: Burial Rite - Draw a card."
    attackAdd, healthAdd = 2, 2

    def effectCanTrigger(self):
        self.effectViable = not self.Game.Hand_Deck.noMinionsinHand(self.ID, self) and self.Game.space(self.ID) >= 1

    def targetExists(self, choice=0):
        return not self.Game.Hand_Deck.noMinionsinHand(self.ID, self) and self.Game.space(self.ID) >= 1

    def targetCorrect(self, target, choice=0):
        if isinstance(target, list): target = target[0]
        return target.ID == self.ID and target.inHand and target != self and target.type == "Minion"

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if target:
            if isinstance(target, list): target = target[0]
            PRINT(self.Game, f"Spirit Curator's Fanfare Burial Rite {target.name} and draw a card.")
            self.Game.Hand_Deck.burialRite(self.ID, target)
            self.Game.Hand_Deck.drawCard(self.ID)
        return target


class DeathFowl_Crystallize(Amulet):
    Class, race, name = "Shadowcraft", "", "Crystallize: Death Fowl"
    mana = 1
    index = "SV_Fortune~Shadowcraft~Amulet~1~None~Death Fowl~Countdown~Crystallize~Deathrattle~Uncollectible"
    requireTarget, description = False, "Countdown (3) Last Words: Gain 4 shadows."

    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.counter = 3
        self.trigsBoard = [Trig_Countdown(self)]
        self.deathrattles = [Deathrattle_DeathFowl_Crystallize(self)]


class Deathrattle_DeathFowl_Crystallize(Deathrattle_Minion):
    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        PRINT(self.entity.Game, "Last Words: Gain 4 shadows.")
        self.entity.Game.Counters.shadows[self.entity.ID] += 4


class DeathFowl(SVMinion):
    Class, race, name = "Shadowcraft", "", "Death Fowl"
    mana, attack, health = 4, 3, 3
    index = "SV_Fortune~Shadowcraft~Minion~4~3~3~None~Death Fowl~Crystallize~Deathrattle"
    requireTarget, keyWord, description = False, "", "Crystallize (1): Countdown (3) Last Words: Gain 4 shadows. Fanfare: Gain 4 shadows.Last Words: Draw a card."
    crystallizeAmulet = DeathFowl_Crystallize
    attackAdd, healthAdd = 2, 2

    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.deathrattles = [Deathrattle_DeathFowl(self)]

    def getMana(self):
        if self.Game.Manas.manas[self.ID] < self.mana:
            return 1
        else:
            return self.mana

    def willCrystallize(self):
        curMana = self.Game.Manas.manas[self.ID]
        return self.mana > curMana >= 1

    def effectCanTrigger(self):
        self.effectViable = "sky blue" if self.willCrystallize() else False

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        PRINT(self.Game, "Death Fowl's Fanfare gains 4 shadows.")
        self.Game.Counters.shadows[self.ID] += 4


class Deathrattle_DeathFowl(Deathrattle_Minion):
    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        PRINT(self.entity.Game, "Last Words: Draw a card.")
        self.entity.Game.Hand_Deck.drawCard(self.entity.ID)


class SoulBox(SVMinion):
    Class, race, name = "Shadowcraft", "", "Soul Box"
    mana, attack, health = 5, 5, 4
    index = "SV_Fortune~Shadowcraft~Minion~2~2~2~None~Soul Box~Battlecry"
    requireTarget, keyWord, description = False, "", "Fanfare: If there are any allied amulets in play, evolve this follower."
    attackAdd, healthAdd = 2, 2

    def effectCanTrigger(self):
        self.effectViable = len(self.Game.amuletsonBoard(self.ID)) > 0

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if len(self.Game.amuletsonBoard(self.ID)) > 0:
            self.evolve()
        return None


class VIMilteoTheLovers(SVMinion):
    Class, race, name = "Shadowcraft", "", "VI. Milteo, The Lovers"
    mana, attack, health = 5, 4, 4
    index = "SV_Fortune~Shadowcraft~Minion~5~4~4~None~VI. Milteo, The Lovers~Battlecry~Enhance~Deathrattle~Legendary"
    requireTarget, keyWord, description = True, "", "Fanfare: Burial Rite (2) - Reanimate (X) and Reanimate (Y). X and Y equal 6 split randomly.(To perform Burial Rite (2), there must be at least 2 open spaces in your area after this follower comes into play.)Enhance (9): Do not perform Burial Rite. Evolve this follower instead.Can't be evolved using evolution points. (Can be evolved using card effects.)Last Words: Draw 2 cards."
    attackAdd, healthAdd = 2, 2

    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.deathrattles = [Deathrattle_VIMilteoTheLovers(self)]
        self.marks["Can't Evolve"] = 1

    def getMana(self):
        if self.Game.Manas.manas[self.ID] >= 9:
            return 9
        else:
            return self.mana

    def willEnhance(self):
        return self.Game.Manas.manas[self.ID] >= 9

    def effectCanTrigger(self):
        if self.willEnhance():
            self.effectViable = True
        else:
            minions = 0
            for card in self.Game.Hand_Deck.hands[self.ID]:
                if card.type == "Minion" and card is not self:
                    minions += 1
            self.effectViable = minions >= 2 and self.Game.space(self.ID) >= 2

    def returnTrue(self, choice=0):
        if self.willEnhance():
            return False
        return self.targetExists(choice) and len(self.targets) < 2

    def targetExists(self, choice=0):
        minions = 0
        for card in self.Game.Hand_Deck.hands[self.ID]:
            if card.type == "Minion" and card is not self:
                minions += 1
        return minions >= 2 and self.Game.space(self.ID) >= 2

    def targetCorrect(self, target, choice=0):
        if isinstance(target, list) and len(target) > 1:
            target1, target2 = target[0], target[1]
            return target1.type == "Minion" and target1.ID == self.ID and target1.inHand and target2.type == "Minion" and target2.ID == self.ID and target2.inHand and target1 != target2
        else:
            if isinstance(target, list): target = target[0]
            return target.type == "Minion" and target.ID == self.ID and target.inHand and target not in self.targets

    def inEvolving(self):
        for t in self.deathrattles:
            if type(t) == Deathrattle_VIMilteoTheLovers:
                t.disconnect()
                self.deathrattles.remove(t)
                break
        trigger = Trig_VIMilteoTheLovers(self)
        self.trigsBoard.append(trigger)
        trigger.connect()

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if comment == 9:
            self.evolve()
        else:
            if target and len(target) >= 2:
                PRINT(self.Game, f"VI. Milteo, The Lovers's Fanfare Burial Rite {target[0].name} and {target[1].name}")
                self.Game.Hand_Deck.burialRite(self.ID, [target[0], target[1]], noSignal=True)
                curGame = self.Game
                if curGame.mode == 0:
                    if curGame.guides:
                        a, b = curGame.guides.pop(0)
                    else:
                        a, b = 0, 0
                        numbers = [0, 1]
                        for i in range(6):
                            n = npchoice(numbers)
                            a += n
                            b += 1 - n
                        curGame.fixedGuides.append((a, b))
                    minions = []
                    minions.append(self.Game.reanimate(self.ID, a))
                    minions.append(self.Game.reanimate(self.ID, b))
                    for minion in minions:
                        if minion:
                            PRINT(self.Game, f"VI. Milteo, The Lovers's Fanfare reanimate {minion}")
                self.Game.Counters.numBurialRiteThisGame[self.ID] += 1
                self.Game.sendSignal("BurialRite", self.ID, None, target[0], 0, "")
                self.Game.Counters.numBurialRiteThisGame[self.ID] += 1
                self.Game.sendSignal("BurialRite", self.ID, None, target[1], 0, "")
        return target


class Deathrattle_VIMilteoTheLovers(Deathrattle_Minion):
    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        PRINT(self.entity.Game, "Last Words: Draw 2 card.")
        self.entity.Game.Hand_Deck.drawCard(self.entity.ID)
        self.entity.Game.Hand_Deck.drawCard(self.entity.ID)


class Trig_VIMilteoTheLovers(TrigBoard):
    def __init__(self, entity):
        self.blank_init(entity, ["TurnEnds"])

    def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.onBoard and ID == self.entity.ID

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        for i in range(6):
            curGame = self.entity.Game
            if curGame.mode == 0:
                if curGame.guides:
                    i, where = curGame.guides.pop(0)
                    if where:
                        minion = curGame.find(i, where)
                        curGame.killMinion(self.entity, minion)
                else:
                    minions = curGame.minionsAlive(1) + curGame.minionsAlive(2)
                    if self.entity in minions: minions.remove(self.entity)
                    if len(minions) > 0:
                        minion = npchoice(minions)
                        curGame.fixedGuides.append((minion.position, f"minion{minion.ID}"))
                        curGame.killMinion(self.entity, minion)
                    else:
                        curGame.fixedGuides.append((0, ""))
        PRINT(self.entity.Game, f"At the end of your turn,VI. Milteo, The Lovers destroy 6 other random followers. ")
        if self.entity.Game.heroes[3 - self.entity.ID].health > 6:
            damage = self.entity.Game.heroes[3 - self.entity.ID].health - 6
            self.entity.dealsDamage(self.entity.Game.heroes[3 - self.entity.ID], damage)
            PRINT(self.entity.Game, f"Then, deal {damage} damage to enemy leader.")


class CloisteredSacristan_Crystallize(Amulet):
    Class, race, name = "Shadowcraft", "", "Crystallize: Cloistered Sacristan"
    mana = 2
    index = "SV_Fortune~Shadowcraft~Amulet~2~None~Cloistered Sacristan~Countdown~Crystallize~Deathrattle~Uncollectible"
    requireTarget, description = False, "Countdown (4) Whenever you perform Burial Rite, subtract 1 from this amulet's Countdown. Last Words: Summon a Cloistered Sacristan."

    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.counter = 4
        self.trigsBoard = [Trig_Countdown(self), Trig_CloisteredSacristan_Crystallize]
        self.deathrattles = [Deathrattle_CloisteredSacristan_Crystallize(self)]


class Deathrattle_CloisteredSacristan_Crystallize(Deathrattle_Minion):
    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        self.entity.Game.summon([CloisteredSacristan(self.entity.Game, self.entity.ID)], (-1, "totheRightEnd"),
                                self.entity.ID)
        PRINT(self.entity.Game,
              f"Last Words: Summon a Cloistered Sacristan.")


class Trig_CloisteredSacristan_Crystallize(TrigBoard):
    def __init__(self, entity):
        self.blank_init(entity, ["BurialRite"])
        self.counter = self.entity.counter

    def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.onBoard and ID == self.entity.ID

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        PRINT(self.entity.Game, f"{self.entity.name}'s countdown -1")
        self.entity.countdown(self.entity, 1)
        self.counter = self.entity.counter


class CloisteredSacristan(SVMinion):
    Class, race, name = "Shadowcraft", "", "Cloistered Sacristan"
    mana, attack, health = 6, 5, 5
    index = "SV_Fortune~Shadowcraft~Minion~6~5~5~None~Cloistered Sacristan~Taunt~Crystallize"
    requireTarget, keyWord, description = False, "Taunt", "Crystallize (2): Countdown (4)Whenever you perform Burial Rite, subtract 1 from this amulet's Countdown.Last Words: Summon a Cloistered Sacristan.Ward."
    crystallizeAmulet = DeathFowl_Crystallize
    attackAdd, healthAdd = 2, 2
    evolveRequireTarget = True

    def evolveTargetExists(self, choice=0):
        return not self.Game.Hand_Deck.noMinionsinHand(self.ID, self) and self.Game.space(self.ID) >= 1

    def evolveTargetCorrect(self, target, choice=0):
        if isinstance(target, list): target = target[0]
        return target.ID == self.ID and target.inHand and target != self and target.type == "Minion"

    def getMana(self):
        if self.Game.Manas.manas[self.ID] < self.mana:
            return 2
        else:
            return self.mana

    def willCrystallize(self):
        curMana = self.Game.Manas.manas[self.ID]
        return self.mana > curMana >= 2

    def effectCanTrigger(self):
        self.effectViable = "sky blue" if self.willCrystallize() else False

    def inHandEvolving(self, target=None):
        if target:
            if isinstance(target, list): target = target[0]
            PRINT(self.Game,
                  f"Spirit Curator's Evolve Burial Rite {target.name} and restores 3 defense to your leader")
            self.Game.Hand_Deck.burialRite(self.ID, target)
            self.restoresHealth(self.Game.heroes[self.ID], 3)
        return target


class ConqueringDreadlord(SVMinion):
    Class, race, name = "Shadowcraft", "", "Conquering Dreadlord"
    mana, attack, health = 8, 6, 6
    index = "SV_Fortune~Shadowcraft~Minion~8~6~6~None~Conquering Dreadlord~Invocation~Legendary"
    requireTarget, keyWord, description = False, "", "Invocation: When you perform Burial Rite, if it is your fifth, seventh, or ninth time this match, invoke this card, then return it to your hand.When this follower leaves play, or at the end of your turn, summon a Lich. (Transformation doesn't count as leaving play.)"
    attackAdd, healthAdd = 2, 2

    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.trigsBoard = [Trig_ConqueringDreadlord(self)]
        self.trigsDeck = [Trig_InvocationConqueringDreadlord(self)]
        self.disappearResponse = [self.whenDisppears]

    def whenDisppears(self):
        self.Game.summon([Lich(self.Game, self.ID)], (-1, "totheRightEnd"), self.ID)
        PRINT(self.Game,
              f"When leave board, Conquering Dreadlord summons a Lich.")

    def afterInvocation(self, signal, ID, subject, target, number, comment):
        self.Game.returnMiniontoHand(self, deathrattlesStayArmed=False)


class Trig_ConqueringDreadlord(TrigBoard):
    def __init__(self, entity):
        self.blank_init(entity, ["TurnEnds"])

    def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.onBoard and ID == self.entity.ID

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        self.entity.Game.summon([Lich(self.entity.Game, self.entity.ID)], (-1, "totheRightEnd"),
                                self.entity.ID)
        PRINT(self.entity.Game,
              f"At the end of your turn, Conquering Dreadlord summons a Lich.")


class Trig_InvocationConqueringDreadlord(TrigInvocation):
    def __init__(self, entity):
        self.blank_init(entity, ["BurialRite"])

    def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.inDeck and ID == self.entity.ID and self.entity.Game.space(self.entity.ID) > 0 and \
               self.entity.Game.Counters.numBurialRiteThisGame[self.entity.ID] in [5, 7, 9]


class Deathbringer_Crystallize(Amulet):
    Class, race, name = "Shadowcraft", "", "Crystallize: Deathbringer"
    mana = 2
    index = "SV_Fortune~Shadowcraft~Amulet~2~None~Deathbringer~Countdown~Crystallize~Battlecry~Deathrattle~Uncollectible"
    requireTarget, description = False, "Countdown (3) Fanfare and Last Words: Transform a random enemy follower into a Skeleton."

    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.counter = 3
        self.trigsBoard = [Trig_Countdown(self)]
        self.deathrattles = [Deathrattle_Deathbringer_Crystallize(self)]

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        curGame = self.Game
        if curGame.mode == 0:
            enemy = None
            if curGame.guides:
                i, where = curGame.guides.pop(0)
                if where: enemy = curGame.find(i, where)
            else:
                chars = curGame.minionsAlive(3 - self.ID)
                if chars:
                    enemy = npchoice(chars)
                    curGame.fixedGuides.append((enemy.position, enemy.type + str(enemy.ID)))
                else:
                    curGame.fixedGuides.append((0, ''))
            if enemy:
                PRINT(self.Game,
                      f"Crystallize: Deathbringer's Fanfare transforms {enemy.name} into a Skeleton.")
                self.Game.transform(enemy, Skeleton(self.Game, 3 - self.ID))


class Deathrattle_Deathbringer_Crystallize(Deathrattle_Minion):
    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        curGame = self.entity.Game
        if curGame.mode == 0:
            PRINT(self.entity.Game, f"Last Words: Transform a random enemy follower into a Skeleton.")
            enemy = None
            if curGame.guides:
                i, where = curGame.guides.pop(0)
                if where: enemy = curGame.find(i, where)
            else:
                chars = curGame.minionsAlive(3 - self.entity.ID)
                if chars:
                    enemy = npchoice(chars)
                    curGame.fixedGuides.append((enemy.position, enemy.type + str(enemy.ID)))
                else:
                    curGame.fixedGuides.append((0, ''))
            if enemy:
                self.entity.Game.transform(enemy, Skeleton(self.entity.Game, 3 - self.entity.ID))


class Deathbringer(SVMinion):
    Class, race, name = "Shadowcraft", "", "Deathbringer"
    mana, attack, health = 9, 7, 7
    index = "SV_Fortune~Shadowcraft~Minion~9~7~7~None~Deathbringer~Crystallize"
    requireTarget, keyWord, description = False, "", "Crystallize (2): Countdown (3) Fanfare and Last Words: Transform a random enemy follower into a Skeleton.At the end of your turn, destroy 2 random enemy followers and restore 5 defense to your leader."
    crystallizeAmulet = Deathbringer_Crystallize
    attackAdd, healthAdd = 2, 2

    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.trigsBoard = [Trig_Deathbringer(self)]

    def getMana(self):
        if self.Game.Manas.manas[self.ID] < self.mana:
            return 2
        else:
            return self.mana

    def willCrystallize(self):
        curMana = self.Game.Manas.manas[self.ID]
        return self.mana > curMana >= 2

    def effectCanTrigger(self):
        self.effectViable = "sky blue" if self.willCrystallize() else False


class Trig_Deathbringer(TrigBoard):
    def __init__(self, entity):
        self.blank_init(entity, ["TurnEnds"])

    def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.onBoard and ID == self.entity.ID

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        curGame = self.entity.Game
        if curGame.mode == 0:
            for n in range(2):
                enemy = None
                if curGame.guides:
                    i, where = curGame.guides.pop(0)
                    if where: enemy = curGame.find(i, where)
                else:
                    chars = curGame.minionsAlive(3 - self.entity.ID)
                    if chars:
                        enemy = npchoice(chars)
                        curGame.fixedGuides.append((enemy.position, enemy.type + str(enemy.ID)))
                    else:
                        curGame.fixedGuides.append((0, ''))
                if enemy:
                    PRINT(self.entity.Game, f"At the end of your turn, Deathbringer destroys {enemy.name}")
                    self.entity.Game.killMinion(self.entity, enemy)
        PRINT(self.entity.Game, f"At the end of your turn, Deathbringer restore 5 defense to your leader.")
        self.entity.restoresHealth(self.entity.Game.heroes[self.entity.ID], 5)


"""Bloodcraft cards"""


class SilverboltHunter(SVMinion):
    Class, race, name = "Bloodcraft", "", "Silverbolt Hunter"
    mana, attack, health = 1, 1, 2
    index = "SV_Fortune~Bloodcraft~Minion~1~1~2~None~Silverbolt Hunter~Battlecry~Deathrattle"
    requireTarget, keyWord, description = False, "", "Fanfare: Deal 1 damage to your leader. Last Words: Give +1/+1 to a random allied follower."
    attackAdd, healthAdd = 2, 2

    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.deathrattles = [Deathrattle_SilverboltHunter(self)]

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        self.dealsDamage(self.Game.heroes[self.ID], 1)
        PRINT(self.Game, f"Silverbolt Hunter 's Fanfare deals 1 damage to your leader.")


class Deathrattle_SilverboltHunter(Deathrattle_Minion):
    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        curGame = self.entity.Game
        if curGame.mode == 0:
            PRINT(curGame, f"Last Words: Give +1/+1 to a random allied follower.")
            if curGame.guides:
                i = curGame.guides.pop(0)
            else:
                minions = [minion.position for minion in curGame.minionsAlive(self.entity.ID)]
                i = npchoice(minions) if minions else -1
                curGame.fixedGuides.append(i)
            if i > -1:
                minion = curGame.minions[self.entity.ID][i]
                PRINT(curGame, f"{minion.name} gets +1/+1")
                minion.buffDebuff(1, 1)


class MoonriseWerewolf(SVMinion):
    Class, race, name = "Bloodcraft", "", "Moonrise Werewolf"
    mana, attack, health = 2, 1, 3
    index = "SV_Fortune~Bloodcraft~Minion~2~1~3~None~Moonrise Werewolf~Battlecry~Enhance"
    requireTarget, keyWord, description = False, "", "Fanfare: If Avarice is active for you, gain +0/+2 and Ward.Fanfare: Enhance (5) - Gain +3/+3."
    attackAdd, healthAdd = 2, 2

    def getMana(self):
        if self.Game.Manas.manas[self.ID] >= 5:
            return 5
        else:
            return self.mana

    def willEnhance(self):
        return self.Game.Manas.manas[self.ID] >= 5

    def effectCanTrigger(self):
        self.effectViable = self.willEnhance() or self.Game.isAvarice(self.ID)

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if self.Game.isAvarice(self.ID):
            self.buffDebuff(0, 2)
            self.getsKeyword("Taunt")
            PRINT(self.Game,
                  "Moonrise Werewolf's Fanfare gives it +0/+2 and Taunt")
        if comment == 5:
            PRINT(self.Game,
                  "Moonrise Werewolf's Enhanced Fanfare gives it +3/+3")
            self.buffDebuff(3, 3)
        return target


class WhiplashImp(SVMinion):
    Class, race, name = "Bloodcraft", "", "Whiplash Imp"
    mana, attack, health = 2, 2, 2
    index = "SV_Fortune~Bloodcraft~Minion~2~2~2~None~Whiplash Imp~Battlecry~Enhance"
    requireTarget, keyWord, description = False, "", "Fanfare: If Wrath is active for you, gain +1/+4, Rush, and Drain. Fanfare: Enhance (6) - Summon an Imp Lancer."
    attackAdd, healthAdd = 2, 2

    def getMana(self):
        if self.Game.Manas.manas[self.ID] >= 6:
            return 6
        else:
            return self.mana

    def willEnhance(self):
        return self.Game.Manas.manas[self.ID] >= 6

    def effectCanTrigger(self):
        self.effectViable = self.willEnhance() or self.Game.isWrath(self.ID)

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if self.Game.isWrath(self.ID):
            self.buffDebuff(1, 4)
            self.getsKeyword("Rush")
            self.getsKeyword("Drain")
            PRINT(self.Game,
                  "Whiplash Imp's Fanfare gives it +1/+4, Rush and Drain")
        if comment == 6:
            PRINT(self.Game,
                  "Whiplash Imp's Enhanced Fanfare summons an Imp Lancer")
            self.Game.summon([ImpLancer(self.Game, self.ID)], (-1, "totheRightEnd"),
                             self.ID)
        return target


class ContemptousDemon(SVMinion):
    Class, race, name = "Bloodcraft", "", "Contemptous Demon"
    mana, attack, health = 2, 2, 2
    index = "SV_Fortune~Bloodcraft~Minion~2~2~2~None~Contemptous Demon~Battlecry"
    requireTarget, keyWord, description = False, "", "Fanfare: If Wrath is active for you, gain the ability to evolve for 0 evolution points.At the end of your turn, deal 1 damage to your leader.At the start of your turn, restore 2 defense to your leader."
    attackAdd, healthAdd = 2, 2

    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.trigsBoard = [Trig_StartContemptousDemon(self), Trig_EndContemptousDemon(self)]

    def effectCanTrigger(self):
        self.effectViable = self.Game.isWrath(self.ID)

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if self.Game.isWrath(self.ID):
            self.marks["Free Evolve"] += 1
            PRINT(self.Game,
                  "Contemptous Demon's Fanfare gains the ability to evolve for 0 evolution points.")
        return target

    def inEvolving(self):
        trigger = Trig_EvolvedContemptousDemon(self)
        self.trigsBoard.append(trigger)
        trigger.connect()


class Trig_StartContemptousDemon(TrigBoard):
    def __init__(self, entity):
        self.blank_init(entity, ["TurnStarts"])

    def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.onBoard and ID == self.entity.ID

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        self.entity.restoresHealth(self.entity.Game.heroes[self.entity.ID], 2)
        PRINT(self.entity.Game, "Contemptous Demon restores 2 defense to your leader.")


class Trig_EndContemptousDemon(TrigBoard):
    def __init__(self, entity):
        self.blank_init(entity, ["TurnEnds"])

    def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.onBoard and ID == self.entity.ID

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        self.entity.dealsDamage(self.entity.Game.heroes[self.entity.ID], 1)
        PRINT(self.entity.Game, "Contemptous Demon  deal 1 damage to your leader.")


class Trig_EvolvedContemptousDemon(TrigBoard):
    def __init__(self, entity):
        self.blank_init(entity, ["HeroTookDmg", "HeroTook0Dmg", "TurnEnds"])
        self.counter = 10

    def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
        if signal != "TurnEnds":
            return self.entity.onBoard and target == self.entity.Game.heroes[self.entity.ID] and ID == self.entity.ID
        else:
            return self.entity.onBoard and ID == self.entity.ID

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        if signal != "TurnEnds":
            curGame = self.entity.Game
            if curGame.mode == 0 and self.counter > 0:
                enemy = None
                if curGame.guides:
                    i, where = curGame.guides.pop(0)
                    if where: enemy = curGame.find(i, where)
                else:
                    chars = curGame.minionsAlive(3 - self.entity.ID)
                    if chars:
                        enemy = npchoice(chars)
                        curGame.fixedGuides.append((enemy.position, enemy.type + str(enemy.ID)))
                    else:
                        curGame.fixedGuides.append((0, ''))
                if enemy:
                    PRINT(self.entity.Game, f"Contemptous Demon deals 3 damage to {enemy.name}")
                    self.entity.dealsDamage(enemy, 3)
            self.counter -= 1
        else:
            self.counter = 10


class DarkSummons(SVSpell):
    Class, name = "Bloodcraft", "Dark Summons"
    requireTarget, mana = True, 2
    index = "SV_Fortune~Bloodcraft~Spell~2~Dark Summons"
    description = "Deal 3 damage to an enemy follower. If Wrath is active for you, recover 2 play points."

    def available(self):
        return self.selectableEnemyMinionExists()

    def targetCorrect(self, target, choice=0):
        if isinstance(target, list): target = target[0]
        return target.type == "Minion" and target.ID != self.ID and target.onBoard

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if target:
            if isinstance(target, list): target = target[0]
            damage = (3 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
            PRINT(self.Game, f"Dark Summons deals {damage} damage to enemy {target.name}")
            self.dealsDamage(target, damage)
            if self.Game.isWrath(self.ID):
                self.Game.Manas.restoreManaCrystal(2, self.ID)
                PRINT(self.Game, f"Dark Summons recover 2 play points.")
        return target


class TyrantofMayhem(SVMinion):
    Class, race, name = "Bloodcraft", "", "Tyrant of Mayhem"
    mana, attack, health = 3, 3, 3
    index = "SV_Fortune~Bloodcraft~Minion~3~3~3~None~Tyrant of Mayhem~Battlecry"
    requireTarget, keyWord, description = False, "", "Fanfare: Draw a card. If Vengeance is not active for you, deal 2 damage to your leader. Otherwise, deal 2 damage to the enemy leader."
    attackAdd, healthAdd = 2, 2

    def effectCanTrigger(self):
        self.effectViable = self.Game.isVengeance(self.ID)

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        self.Game.Hand_Deck.drawCard(self.ID)
        PRINT(self.Game,
              "Tyrant of Mayhem's Fanfare draw a card")
        if self.Game.isVengeance(self.ID):
            self.dealsDamage(self.Game.heroes[3 - self.ID], 2)
            PRINT(self.Game,
                  "Tyrant of Mayhem's Fanfare deals 2 damage to enemy leader")
        else:
            self.dealsDamage(self.Game.heroes[self.ID], 2)
            PRINT(self.Game,
                  "Tyrant of Mayhem's Fanfare deals 2 damage to your leader")
        return target


class CurmudgeonOgre(SVMinion):
    Class, race, name = "Bloodcraft", "", "Curmudgeon Ogre"
    mana, attack, health = 4, 4, 4
    index = "SV_Fortune~Bloodcraft~Minion~4~4~4~None~Curmudgeon Ogre~Battlecry~Enhance"
    requireTarget, keyWord, description = False, "", "Fanfare: Enhance (6) - Give +1/+1 to all allied Bloodcraft followers. If Vengeance is active for you, give +2/+2 instead."
    attackAdd, healthAdd = 2, 2

    def getMana(self):
        if self.Game.Manas.manas[self.ID] >= 6:
            return 6
        else:
            return self.mana

    def willEnhance(self):
        return self.Game.Manas.manas[self.ID] >= 6

    def effectCanTrigger(self):
        self.effectViable = self.willEnhance()

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if comment == 6:
            n = 1
            if self.Game.isVengeance(self.ID):
                n = 2
            PRINT(self.Game, f"Curmudgeon Ogre's Fanfare gives +{n}/+{n} to all allied Bloodcraft followers")
            for minion in fixedList(self.Game.minionsonBoard(self.ID, self)):
                if minion.Class == "Bloodcraft":
                    minion.buffDebuff(n, n)
        return target


class DireBond(Amulet):
    Class, race, name = "Bloodcraft", "", "Dire Bond"
    mana = 3
    index = "SV_Fortune~Bloodcraft~Amulet~3~None~Dire Bond"
    requireTarget, description = False, "Countdown (3)Fanfare: Deal 6 damage to your leader.At the start of your turn, restore 2 defense to your leader and draw a card."

    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.counter = 3
        self.trigsBoard = [Trig_Countdown(self), Trig_DireBond(self)]

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        self.dealsDamage(self.Game.heroes[self.ID], 6)
        PRINT(self.Game, f"Dire Bond 's Fanfare deals 6 damage to player")


class Trig_DireBond(TrigBoard):
    def __init__(self, entity):
        self.blank_init(entity, ["TurnStarts"])

    def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.onBoard and ID == self.entity.ID

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        self.entity.Game.Hand_Deck.drawCard(self.entity.ID)
        self.entity.restoresHealth(self.entity.Game.heroes[self.entity.ID], 2)
        PRINT(self.entity.Game, "At the start of turn, Dire Bond restore 2 defense to your leader and draw a card")


class DarholdAbyssalContract(SVMinion):
    Class, race, name = "Bloodcraft", "", "Darhold, Abyssal Contract"
    mana, attack, health = 4, 4, 3
    index = "SV_Fortune~Bloodcraft~Minion~4~4~3~None~Darhold, Abyssal Contract~Battlecry~Legendary"
    requireTarget, keyWord, description = True, "", "Fanfare: If Wrath is active for you, destroy an enemy follower, then deal 3 damage to the enemy leader."
    attackAdd, healthAdd = 2, 2

    def effectCanTrigger(self):
        self.effectViable = self.Game.isWrath(self.ID)

    def targetExists(self, choice=0):
        return self.selectableEnemyMinionExists() and self.Game.isWrath(self.ID)

    def targetCorrect(self, target, choice=0):
        if isinstance(target, list): target = target[0]
        return target.type == "Minion" and target.ID != self.ID and target.onBoard

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if target:
            if isinstance(target, list): target = target[0]
            PRINT(self.Game,
                  f"Darhold, Abyssal Contract 's Fanfare destroys {target.name}, then deal 3 damage to the enemy leader.")
            self.Game.killMinion(self, target)
            self.dealsDamage(self.Game.heroes[3 - self.ID], 3)
        return target

    def inHandEvolving(self, target=None):
        self.dealsDamage(self.Game.heroes[self.ID], 3)
        self.Game.summon([DireBond(self.Game, self.ID)], (-1, "totheRightEnd"),
                         self.ID)
        PRINT(self.Game, f"Darhold, Abyssal Contract 's Evolve deals 3 damage to your leader and summons a Dire Bond.")


class BurningConstriction(SVSpell):
    Class, name = "Bloodcraft", "Burning Constriction"
    mana, requireTarget = 5, False
    index = "SV_Fortune~Bloodcraft~Spell~5~Burning Constriction"
    description = "Deal 4 damage to all enemy followers. Then, if Vengeance is active for you, deal 4 damage to the enemy leader."

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        damage = (4 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
        targets = self.Game.minionsonBoard(3 - self.ID)
        PRINT(self.Game, f"Burning Constriction deals {damage} damage to all enemy minions.")
        self.dealsAOE(targets, [damage for minion in targets])
        if self.Game.isVengeance(self.ID):
            self.dealsDamage(self.Game.heroes[3 - self.ID], damage)
            PRINT(self.Game, f"Burning Constriction deals {damage} damage to enemy leader.")
        return None


class VampireofCalamity_Accelerate(SVSpell):
    Class, name = "Bloodcraft", "Vampire of Calamity"
    requireTarget, mana = True, 1
    index = "SV_Fortune~Bloodcraft~Spell~1~Vampire of Calamity~Accelerate~Uncollectible"
    description = "Deal 1 damage to your leader. Deal 2 damage to an enemy follower."

    def targetCorrect(self, target, choice=0):
        if isinstance(target, list): target = target[0]
        return target.type == "Minion" and target.ID != self.ID and target.onBoard

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if target:
            if isinstance(target, list): target = target[0]
            damage = (1 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
            self.dealsDamage(self.Game.heroes[self.ID], damage)
            damage1 = (2 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
            PRINT(self.Game,
                  f"Vampire of Calamity, as spell, deals {damage} damage to your leader and deals {damage1} damage to enemy {target.name}.")
            self.dealsDamage(target, damage1)
        return target


class VampireofCalamity(SVMinion):
    Class, race, name = "Bloodcraft", "", "Vampire of Calamity"
    mana, attack, health = 7, 7, 7
    index = "SV_Fortune~Bloodcraft~Minion~7~7~7~None~Vampire of Calamity~Rush~Battlecry~Accelerate"
    requireTarget, keyWord, description = True, "Rush", "Accelerate (1): Deal 1 damage to your leader. Deal 2 damage to an enemy follower.Rush.Fanfare: If Wrath is active for you, deal 4 damage to an enemy and restore 4 defense to your leader."
    accelerateSpell = VampireofCalamity_Accelerate
    attackAdd, healthAdd = 2, 2

    def getMana(self):
        if self.Game.Manas.manas[self.ID] < self.mana:
            return 1
        else:
            return self.mana

    def willAccelerate(self):
        curMana = self.Game.Manas.manas[self.ID]
        return self.mana > curMana >= 1

    def effectCanTrigger(self):
        self.effectViable = "sky blue" if self.willAccelerate() and self.targetExists() else False

    def returnTrue(self, choice=0):
        if self.willAccelerate():
            return not self.targets
        return self.Game.isWrath(self.ID) and not self.targets

    def available(self):
        if self.willAccelerate():
            return self.selectableEnemyMinionExists()
        return True

    def targetExists(self, choice=0):
        return self.selectableEnemyMinionExists()

    def targetCorrect(self, target, choice=0):
        if isinstance(target, list): target = target[0]
        return target.type == "Minion" and target.ID != self.ID and target.onBoard

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if target:
            if isinstance(target, list): target = target[0]
            PRINT(self.Game, f"Vampire of Calamity deals 4 damage to enemy {target.name}.")
            self.dealsDamage(target, 4)
        self.restoresHealth(self.Game.heroes[self.ID], 4)
        PRINT(self.Game, f"Vampire of Calamity restore 4 defense to your leader.")
        return target


class UnselfishGrace(Amulet):
    Class, race, name = "Bloodcraft", "", "Unselfish Grace"
    mana = 3
    index = "SV_Fortune~Bloodcraft~Amulet~3~None~Unselfish Grace~Uncollectible~Legendary"
    requireTarget, description = False, "Countdown (5)At the end of your turn, restore 1 defense to your leader. If you have more evolution points than your opponent, restore 2 defense instead. (You have 0 evolution points on turns you are unable to evolve.)Last Words: Summon a 4-play point 4/4 XIV. Luzen, Temperance (without Accelerate)."

    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.counter = 5
        self.trigsBoard = [Trig_Countdown(self), Trig_UnselfishGrace(self)]
        self.deathrattles = [Deathrattle_UnselfishGrace(self)]


class Trig_UnselfishGrace(TrigBoard):
    def __init__(self, entity):
        self.blank_init(entity, ["TurnEnds"])

    def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.onBoard and ID == self.entity.ID

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        health = 1
        if self.entity.Game.getEvolutionPoint(self.entity.ID) > self.entity.Game.getEvolutionPoint(3 - self.entity.ID):
            health = 2
        self.entity.restoresHealth(self.entity.Game.heroes[self.entity.ID], health)
        PRINT(self.entity.Game, f"At the end of turn, Unselfish Grace restore {health} defense to your leader")


class Deathrattle_UnselfishGrace(Deathrattle_Minion):
    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        PRINT(self.entity.Game, "Last Words: Summon a XIV. Luzen, Temperance.")
        self.entity.Game.summon([XIVLuzenTemperance_Token(self.entity.Game, self.entity.ID)], (-1, "totheRightEnd"),
                                self.entity.ID)


class InsatiableDesire(SVSpell):
    Class, name = "Bloodcraft", "Insatiable Desire"
    requireTarget, mana = False, 1
    index = "SV_Fortune~Bloodcraft~Spell~1~Insatiable Desire~Uncollectible~Legendary"
    description = "Give your leader the following effects.-At the start of your turn, draw a card.-At the start of your turn, lose 1 play point.(These effects are not stackable and last for the rest of the match.)"

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        trigger = Trig_InsatiableDesire(self.Game.heroes[self.ID])
        for t in self.Game.heroes[self.ID].trigsBoard:
            if type(t) == type(trigger):
                return
        self.Game.heroes[self.ID].trigsBoard.append(trigger)
        trigger.connect()
        return None


class Trig_InsatiableDesire(TrigBoard):
    def __init__(self, entity):
        self.blank_init(entity, ["TurnStarts"])

    def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.onBoard and ID == self.entity.ID

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        PRINT(self.entity.Game,
              "At the start of your turn, draw a card and lose 1 play point")
        self.entity.Game.Hand_Deck.drawCard(self.entity.ID)
        self.entity.Game.Manas.payManaCost(self.entity, 1)


class XIVLuzenTemperance_Accelerate(SVSpell):
    Class, name = "Bloodcraft", "XIV. Luzen, Temperance"
    requireTarget, mana = False, 0
    index = "SV_Fortune~Bloodcraft~Spell~0~XIV. Luzen, Temperance~Accelerate~Uncollectible~Legendary"
    description = "Put an Unselfish Grace into your hand. If Avarice is active for you, put an Insatiable Desire into your hand instead."

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if self.Game.isAvarice(self.ID):
            self.Game.Hand_Deck.addCardtoHand(InsatiableDesire(self.Game, self.ID), self.ID)
            PRINT(self.Game,
                  "XIV. Luzen, Temperance, as a spell, puts an Insatiable Desire into your hand.")
        else:
            self.Game.Hand_Deck.addCardtoHand(UnselfishGrace(self.Game, self.ID), self.ID)
            PRINT(self.Game,
                  "XIV. Luzen, Temperance, as a spell, puts an Unselfish Grace into your hand.")
        return None


class XIVLuzenTemperance_Token(SVMinion):
    Class, race, name = "Bloodcraft", "", "XIV. Luzen, Temperance"
    mana, attack, health = 4, 4, 4
    index = "SV_Fortune~Bloodcraft~Minion~4~4~4~None~XIV. Luzen, Temperance~Uncollectible~Legendary"
    requireTarget, keyWord, description = False, "", "Can't be targeted by enemy effects.While this follower is in play, your leader has the following effects.-Can't take more than 1 damage at a time.-Whenever your leader takes damage, reduce the enemy leader's maximum defense by 3."
    attackAdd, healthAdd = 2, 2

    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.auras["Buff Aura"] = BuffAura_XIVLuzenTemperance(self)
        self.marks["Enemy Effect Evasive"] = 1


class XIVLuzenTemperance(SVMinion):
    Class, race, name = "Bloodcraft", "", "XIV. Luzen, Temperance"
    mana, attack, health = 9, 7, 7
    index = "SV_Fortune~Bloodcraft~Minion~9~7~7~None~XIV. Luzen, Temperance~Accelerate~Legendary"
    requireTarget, keyWord, description = False, "", "Can't be targeted by enemy effects.While this follower is in play, your leader has the following effects.-Can't take more than 1 damage at a time.-Whenever your leader takes damage, reduce the enemy leader's maximum defense by 3."
    accelerateSpell = XIVLuzenTemperance_Accelerate
    attackAdd, healthAdd = 2, 2

    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.auras["Buff Aura"] = BuffAura_XIVLuzenTemperance(self)
        self.marks["Enemy Effect Evasive"] = 1

    def getMana(self):
        if self.Game.Manas.manas[self.ID] < self.mana:
            return 0
        else:
            return self.mana

    def willAccelerate(self):
        curMana = self.Game.Manas.manas[self.ID]
        return self.mana > curMana >= 0

    def effectCanTrigger(self):
        self.effectViable = "sky blue" if self.willAccelerate() else False


class BuffAura_XIVLuzenTemperance(AuraDealer_toMinion):
    def __init__(self, entity):
        self.entity = entity
        self.signals, self.auraAffected = [], []

    # Minions appearing/disappearing will let the minion reevaluate the aura.
    def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.onBoard

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        self.applies(self.entity.Game.heroes[self.entity.ID])

    def applies(self, subject):
        subject.marks["Max Damage"].append(1)
        trigger = Trig_XIVLuzenTemperance(subject)
        subject.trigsBoard.append(trigger)
        trigger.connect()

    def auraAppears(self):
        self.applies(self.entity.Game.heroes[self.entity.ID])

    def auraDisappears(self):
        if 1 in self.entity.Game.heroes[self.entity.ID].marks["Max Damage"]:
            self.entity.Game.heroes[self.entity.ID].marks["Max Damage"].remove(1)
        for trigger in self.entity.Game.heroes[self.entity.ID].trigsBoard:
            if type(trigger) == Trig_XIVLuzenTemperance:
                self.entity.Game.heroes[self.entity.ID].trigsBoard.remove(trigger)
                break

    def selfCopy(self, recipientMinion):  # The recipientMinion is the minion that deals the Aura.
        return type(self)(recipientMinion)


class Trig_XIVLuzenTemperance(TrigBoard):
    def __init__(self, entity):
        self.blank_init(entity, ["HeroTookDmg", "HeroTook0Dmg"])

    def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.onBoard and target == self.entity.Game.heroes[self.entity.ID]

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        PRINT(self.entity.Game,
              "Whenever your leader takes damage, reduce the enemy leader's maximum defense by 3.")
        self.entity.Game.heroes[3 - self.entity.ID].health_max -= 3
        self.entity.Game.heroes[3 - self.entity.ID].health = min(self.entity.Game.heroes[3 - self.entity.ID].health,
                                                                 self.entity.Game.heroes[3 - self.entity.ID].health_max)


"""Havencraft cards"""


class JeweledBrilliance(SVSpell):
    Class, name = "Havencraft", "Jeweled Brilliance"
    mana, requireTarget = 1, False,
    index = "SV_Fortune~Havencraft~Spell~1~Jeweled Brilliance"
    description = "Put a random amulet from your deck into your hand."

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        curGame = self.Game
        if curGame.mode == 0:
            PRINT(self.Game, "Jeweled Brilliance puts a random amulet from your deck into your hand")
            if curGame.guides:
                i = curGame.guides.pop(0)
            else:
                amulets = [i for i, card in enumerate(curGame.Hand_Deck.decks[self.ID]) if
                           card.type == "Amulet"]
                i = npchoice(amulets) if amulets else -1
                curGame.fixedGuides.append(i)
            if i > -1: curGame.Hand_Deck.drawCard(self.ID, i)


class StalwartFeatherfolk(SVMinion):
    Class, race, name = "Havencraft", "", "Stalwart Featherfolk"
    mana, attack, health = 2, 2, 2
    index = "SV_Fortune~Havencraft~Minion~2~2~2~None~Stalwart Featherfolk~Taunt~Battlecry"
    requireTarget, keyWord, description = False, "Taunt", "Ward. Fanfare: If any allied amulets are in play, restore X defense to your leader. X equals the number of allied amulets in play."
    attackAdd, healthAdd = 2, 2

    def effectCanTrigger(self):
        self.effectViable = len(self.Game.amuletsonBoard(self.ID)) > 0

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if len(self.Game.amuletsonBoard(self.ID)) > 0:
            self.restoresHealth(self.Game.heroes[self.ID], len(self.Game.amuletsonBoard(self.ID)))
            PRINT(self.Game,
                  f"Stalwart Featherfolk's Fanfare restore {len(self.Game.amuletsonBoard(self.ID))} defense to your leader")

        return None


class PrismaplumeBird(SVMinion):
    Class, race, name = "Havencraft", "", "Prismaplume Bird"
    mana, attack, health = 2, 3, 1
    index = "SV_Fortune~Havencraft~Minion~2~3~1~None~Prismaplume Bird~Deathrattle"
    requireTarget, keyWord, description = False, "", "Last Words: Randomly summon a Summon Pegasus or Pinion Prayer."
    attackAdd, healthAdd = 2, 2

    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.deathrattles = [Deathrattle_PrismaplumeBird(self)]


class Deathrattle_PrismaplumeBird(Deathrattle_Minion):
    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        es = ["S", "P"]
        e = "S"
        curGame = self.entity.Game
        if curGame.mode == 0:
            if curGame.guides:
                i, e = curGame.guides.pop(0)
            else:
                e = np.random.choice(es)
                curGame.fixedGuides.append((0, e))
        if e == "S":
            PRINT(self.entity.Game, "Last Words: Summon a Summon Pegasus.")
            self.entity.Game.summon([SummonPegasus(self.entity.Game, self.entity.ID)], (-1, "totheRightEnd"),
                                    self.entity.ID)
        elif e == "P":
            PRINT(self.entity.Game, "Last Words: Summon a Pinion Prayer.")
            self.entity.Game.summon([PinionPrayer(self.entity.Game, self.entity.ID)], (-1, "totheRightEnd"),
                                    self.entity.ID)


class FourPillarTortoise(SVMinion):
    Class, race, name = "Havencraft", "", "Four-Pillar Tortoise"
    mana, attack, health = 3, 1, 4
    index = "SV_Fortune~Havencraft~Minion~3~1~4~None~Four-Pillar Tortoise~Taunt~Battlecry"
    requireTarget, keyWord, description = False, "Taunt", "Ward. Fanfare: Randomly put a 4-play point Havencraft follower or amulet from your deck into your hand."
    attackAdd, healthAdd = 2, 2

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        curGame = self.Game
        if curGame.mode == 0:
            PRINT(self.Game,
                  "Four-Pillar Tortoise's Fanfare puts a 4-play point Havencraft follower or amulet from your deck into your hand.")
            if curGame.guides:
                i = curGame.guides.pop(0)
            else:
                minions = [i for i, card in enumerate(curGame.Hand_Deck.decks[self.ID]) if
                           card.type == "Minion" and card.mana == 4]
                i = npchoice(minions) if minions else -1
                curGame.fixedGuides.append(i)
            if i > -1: curGame.Hand_Deck.drawCard(self.ID, i)


class LorenasHolyWater(SVSpell):
    Class, name = "Havencraft", "Lorena's Holy Water"
    requireTarget, mana = True, 1
    index = "SV_Fortune~Havencraft~Spell~1~Lorena's Holy Water~Uncollectible"
    description = "Restore 3 defense to an ally. If at least 2 other cards were played this turn, recover 1 evolution point."

    def targetExists(self, choice=0):
        return self.selectableFriendlyExists()

    def targetCorrect(self, target, choice=0):
        if isinstance(target, list): target = target[0]
        return target.type in ["Minion", "Hero"] and target.onBoard and target.ID == self.ID

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if target:
            if isinstance(target, list): target = target[0]
            heal = 2 * (2 ** self.countHealDouble())
            self.restoresHealth(target, heal)
            PRINT(self.Game,
                  f"Lorena's Holy Water restores {heal} defense to {target.name} and draw a card")
            self.Game.Hand_Deck.drawCard(self.ID)
        return target


class LorenaIronWilledPriest(SVMinion):
    Class, race, name = "Havencraft", "", "Lorena, Iron-Willed Priest"
    mana, attack, health = 3, 2, 3
    index = "SV_Fortune~Havencraft~Minion~3~2~3~None~Lorena, Iron-Willed Priest~Battlecry"
    requireTarget, keyWord, description = False, "", "Fanfare: Put a Lorena's Holy Water into your hand. During your turn, when defense is restored to your leader, if it's the second time this turn, gain the ability to evolve for 0 evolution points."
    attackAdd, healthAdd = 2, 2
    evolveRequireTarget = True

    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.progress = 0
        self.trigsBoard = [Trig_LorenaIronWilledPriest(self)]

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        self.Game.Hand_Deck.addCardtoHand(LorenasHolyWater, self.ID, "type")
        PRINT(self.Game,
              f"Lorena, Iron-Willed Priest's Fanfare puts a Lorena's Holy Water into your hand")

    def inEvolving(self):
        for trig in self.trigsBoard:
            if type(trig) == Trig_LorenaIronWilledPriest:
                trig.disconnect()
                self.trigsBoard.remove(trig)

    def evolveTargetExists(self, choice=0):
        return self.selectableEnemyMinionExists()

    def evolveTargetCorrect(self, target, choice=0):
        if isinstance(target, list): target = target[0]
        return target.type == "Minion" and target.onBoard and target.ID != self.ID

    def inHandEvolving(self, target=None):
        if isinstance(target, list): target = target[0]
        if target and target.onBoard:
            damage = 0
            for minion in self.Game.minionsAlive(self.ID):
                if minion.attack > damage:
                    damage = minion.attack
            PRINT(self.Game,
                  f"Lorena, Iron-Willed Priest's Evolve deals {damage} damage to enemy {target.name}")
            self.dealsDamage(target, damage)
        return target


class Trig_LorenaIronWilledPriest(TrigBoard):
    def __init__(self, entity):
        self.blank_init(entity, ["HeroGetsCured", "AllCured"])

    def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
        if signal == "HeroGetsCured":
            return subject.ID == self.entity.ID and self.entity.onBoard
        else:
            return ID == self.entity.ID and self.entity.onBoard

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        self.entity.progress += 1
        if self.entity.progress == 2:
            self.entity.marks["Free Evolve"] += 1
            PRINT(self.entity.Game,
                  f"Lorena, Iron-Willed Priest's gain the ability to evolve for 0 evolution points.")


class SarissaLuxflashSpear(SVMinion):
    Class, race, name = "Havencraft", "", "Sarissa, Luxflash Spear"
    mana, attack, health = 3, 2, 2
    index = "SV_Fortune~Havencraft~Minion~3~2~2~None~Sarissa, Luxflash Spear~Battlecry~Enhance~Legendary"
    requireTarget, keyWord, description = False, "", "Fanfare: The next time this follower takes damage, reduce that damage to 0.Enhance (6): Randomly summon a copy of 1 of the highest-cost allied followers that had Ward when they were destroyed this match.Whenever an allied follower with Ward is destroyed, gain +2/+2."
    attackAdd, healthAdd = 2, 2

    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.trigsBoard = [Trig_SarissaLuxflashSpear(self)]

    def getMana(self):
        if self.Game.Manas.manas[self.ID] >= 6:
            return 6
        else:
            return self.mana

    def willEnhance(self):
        return self.Game.Manas.manas[self.ID] >= 6

    def effectCanTrigger(self):
        self.effectViable = self.willEnhance()

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        self.marks["Next Damage 0"] += 1
        PRINT(self.Game,
              f"Sarissa, Luxflash Spear gain the ability The next time this follower takes damage, reduce that damage to 0.")
        if comment == 6:
            if self.Game.mode == 0:
                type = None
                if self.Game.guides:
                    type = self.Game.guides.pop(0)
                else:
                    indices = self.Game.Counters.minionsDiedThisGame[self.ID]
                    minions = {}
                    for index in indices:
                        if "~Taunt" in index:
                            try:
                                minions[self.Game.cardPool[index].mana].append(self.Game.cardPool[index])
                            except:
                                minions[self.Game.cardPool[index].mana] = [self.Game.cardPool[index]]
                    if minions:
                        for i in range(minions.keys()[len(minions) - 1], -1, -1):
                            if i in minions:
                                type = npchoice(minions[i])
                                self.Game.fixedGuides.append(type)
                                break
                    else:
                        self.Game.fixedGuides.append(None)
                if type:
                    subject = type(self.Game, self.ID)
                    self.Game.summon([subject], (-1, "totheRightEnd"), self.ID)
                    PRINT(self.Game,
                          f"Sarissa, Luxflash Spear's Enhance Fanfare summons {subject.name}")
        return None


class Trig_SarissaLuxflashSpear(TrigBoard):
    def __init__(self, entity):
        self.blank_init(entity, ["MinionDies"])

    def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
        return target.ID == self.entity.ID and self.entity.onBoard and target.keyWords["Taunt"] > 0

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        self.entity.buffDebuff(2, 2)
        PRINT(self.entity.Game,
              f"Sarissa, Luxflash Spear gain +2/+2")


class PriestessofForesight(SVMinion):
    Class, race, name = "Havencraft", "", "Priestess of Foresight"
    mana, attack, health = 4, 2, 5
    index = "SV_Fortune~Havencraft~Minion~4~2~5~None~Priestess of Foresight~Battlecry"
    requireTarget, keyWord, description = False, "", "Fanfare: If another allied follower with Ward is in play, destroy an enemy follower. Otherwise, gain Ward."
    attackAdd, healthAdd = 2, 2

    def returnTrue(self, choice=0):
        for minion in self.Game.minionsAlive(self.ID):
            if minion != self and minion.keyWords["Taunt"] > 0:
                return self.targetExists(choice) and not self.targets
        return False

    def effectCanTrigger(self):
        for minion in self.Game.minionsAlive(self.ID):
            if minion != self and minion.keyWords["Taunt"] > 0:
                self.effectViable = True
                return

    def targetExists(self, choice=0):
        return self.selectableEnemyMinionExists()

    def targetCorrect(self, target, choice=0):
        if isinstance(target, list): target = target[0]
        return target.type == "Minion" and target.ID != self.ID and target.onBoard

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if target:
            if isinstance(target, list): target = target[0]
            self.Game.killMinion(self, target)
            PRINT(self.Game, f"Priestess of Foresight's Fanfare destroys {target.name}")
            return target
        hasTaunt = False
        for minion in self.Game.minionsAlive(self.ID):
            if minion != self and minion.keyWords["Taunt"] > 0:
                hasTaunt = True
                break
        if not hasTaunt:
            self.getsKeyword("Taunt")
            PRINT(self.Game, f"Priestess of Foresight's Fanfare gains Ward")
        return None


class HolybrightAltar(Amulet):
    Class, race, name = "Havencraft", "", "Holybright Altar"
    mana = 4
    index = "SV_Fortune~Havencraft~Amulet~4~None~Holybright Altar~Battlecry~Countdown~Deathrattle"
    requireTarget, description = False, "Countdown (1) Fanfare: If an allied follower with Ward is in play, subtract 1 from this amulet's Countdown.Last Words: Summon a Holywing Dragon."

    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.counter = 1
        self.trigsBoard = [Trig_Countdown(self)]
        self.deathrattles = [Deathrattle_HolybrightAltar(self)]

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        hasTaunt = False
        for minion in self.Game.minionsAlive(self.ID):
            if minion != self and minion.keyWords["Taunt"] > 0:
                hasTaunt = True
                break
        if hasTaunt:
            self.countdown(self, 1)
        return None


class Deathrattle_HolybrightAltar(Deathrattle_Minion):
    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        PRINT(self.entity.Game, "Last Words: Summon a Holywing Dragon.")
        self.entity.Game.summon([HolywingDragon(self.entity.Game, self.entity.ID)], (-1, "totheRightEnd"),
                                self.entity.ID)


class ReverendAdjudicator(SVMinion):
    Class, race, name = "Havencraft", "", "Reverend Adjudicator"
    mana, attack, health = 5, 2, 3
    index = "SV_Fortune~Havencraft~Minion~5~2~3~None~Reverend Adjudicator~Taunt~Battlecry"
    requireTarget, keyWord, description = False, "Taunt", "Ward.Fanfare: Restore 2 defense to your leader. Draw a card.During your turn, whenever your leader's defense is restored, summon a Snake Priestess."
    attackAdd, healthAdd = 2, 2

    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.trigsBoard = [Trig_ReverendAdjudicator(self)]

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        self.restoresHealth(self.Game.heroes[self.ID], 2)
        PRINT(self.Game,
              f"Reverend Adjudicator's Fanfare restores 2 defense to your leader and draw a card")
        self.Game.Hand_Deck.drawCard(self.ID)

    def inHandEvolving(self, target=None):
        self.restoresHealth(self.Game.heroes[self.ID], 2)
        PRINT(self.Game,
              f"Reverend Adjudicator's Evolve restores 2 defense to your leader")


class Trig_ReverendAdjudicator(TrigBoard):
    def __init__(self, entity):
        self.blank_init(entity, ["HeroGetsCured", "AllCured"])

    def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
        if signal == "HeroGetsCured":
            return subject.ID == self.entity.ID and self.entity.onBoard
        else:
            return ID == self.entity.ID and self.entity.onBoard

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        PRINT(self.entity.Game, "Reverend Adjudicator summons a Snake Priestess.")
        self.entity.Game.summon([SnakePriestess(self.entity.Game, self.entity.ID)], (-1, "totheRightEnd"),
                                self.entity.ID)


class SomnolentStrength(Amulet):
    Class, race, name = "Havencraft", "", "Somnolent Strength"
    mana = 2
    index = "SV_Fortune~Havencraft~Amulet~2~None~Somnolent Strength~Countdown~Deathrattle~Uncollectible~Legendary"
    requireTarget, description = False, "Countdown (3)At the end of your turn, give +0/+2 to a random allied follower.Last Words: Give -2/-0 to a random enemy follower."

    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.counter = 3
        self.trigsBoard = [Trig_Countdown(self), Trig_SomnolentStrength(self)]
        self.deathrattles = [Deathrattle_SomnolentStrength(self)]


class Trig_SomnolentStrength(TrigBoard):
    def __init__(self, entity):
        self.blank_init(entity, ["TurnEnds"])

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
                PRINT(self.entity.Game, "At the end of your turn, give +0/+2 to a random allied follower.")
                minion.buffDebuff(0, 2)


class Deathrattle_SomnolentStrength(Deathrattle_Minion):
    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        curGame = self.entity.Game
        if curGame.mode == 0:
            if curGame.guides:
                i = curGame.guides.pop(0)
            else:
                minions = curGame.minionsonBoard(3 - self.entity.ID)
                try:
                    minions.remove(self.entity)
                except:
                    pass
                i = npchoice(minions).position if minions else -1
                curGame.fixedGuides.append(i)
            if i > -1:
                minion = curGame.minions[3 - self.entity.ID][i]
                PRINT(self.entity.Game, "Last Words: Give -2/-0 to a random enemy follower.")
                minion.buffDebuff(-2, 0)


class VIIISofinaStrength_Accelerate(SVSpell):
    Class, name = "Havencraft", "VIII. Sofina, Strength"
    requireTarget, mana = False, 2
    index = "SV_Fortune~Havencraft~Spell~2~VIII. Sofina, Strength~Accelerate~Uncollectible~Legendary"
    description = "Summon a Somnolent Strength."

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        PRINT(self.Game, "VIII. Sofina, Strength's Accelerate Summon a Somnolent Strength.")
        self.Game.summon([SomnolentStrength(self.Game, self.ID)], (-1, "totheRightEnd"),
                         self.ID)
        return None


class VIIISofinaStrength(SVMinion):
    Class, race, name = "Havencraft", "", "VIII. Sofina, Strength"
    mana, attack, health = 5, 2, 6
    index = "SV_Fortune~Havencraft~Minion~5~2~6~None~VIII. Sofina, Strength~Accelerate~Battlecry~Legendary"
    requireTarget, keyWord, description = False, "", "Accelerate (2): Summon a Somnolent Strength.Fanfare: Give all other allied followers +1/+1 and Ward.While this follower is in play, all allied followers in play and that come into play can't take more than 3 damage at a time."
    accelerateSpell = VIIISofinaStrength_Accelerate
    attackAdd, healthAdd = 2, 2

    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.auras["Buff Aura"] = BuffAura_VIIISofinaStrength(self)

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

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        PRINT(self.Game, "VIII. Sofina, Strength's Fanfare gives +1/+1 and Ward to all allied followers")
        for minion in fixedList(self.Game.minionsonBoard(self.ID, self)):
            minion.buffDebuff(1, 1)
            minion.getsKeyword("Taunt")
        return None


class BuffAura_VIIISofinaStrength(AuraDealer_toMinion):
    def __init__(self, entity):
        self.entity = entity
        self.signals, self.auraAffected = ["MinionAppears"], []

    # All minions appearing on the same side will be subject to the buffAura.
    def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.onBoard and subject.ID == self.entity.ID

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        self.applies(signal, subject)

    def applies(self, signal, subject):
        subject.marks["Max Damage"].append(3)

    def auraAppears(self):
        for minion in self.entity.Game.minionsonBoard(self.entity.ID):
            self.applies("MinionAppears", minion)

    def auraDisappears(self):
        for minion in self.entity.Game.minionsonBoard(self.entity.ID):
            if 3 in minion.marks["Max Damage"]:
                minion.marks["Max Damage"].remove(3)

    def selfCopy(self, recipient):
        return type(self)(recipient)


class PuresongPriest_Accelerate(SVSpell):
    Class, name = "Havencraft", "Puresong Priest"
    requireTarget, mana = False, 1
    index = "SV_Fortune~Havencraft~Spell~1~Puresong Priest~Accelerate~Uncollectible"
    description = "Restore 1 defense to your leader. If an allied follower with Ward is in play, draw a card."

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        self.restoresHealth(self.Game.heroes[self.ID], 1)
        PRINT(self.Game,
              f"Puresong Priest's Accelerate restores 1 defense to your leader")
        hasTaunt = False
        for minion in self.Game.minionsAlive(self.ID):
            if minion != self and minion.keyWords["Taunt"] > 0:
                hasTaunt = True
                break
        if hasTaunt:
            self.Game.Hand_Deck.drawCard(self.ID)
            PRINT(self.Game,
                  f"Puresong Priest's Accelerate draw a card")
        return None


class PuresongPriest(SVMinion):
    Class, race, name = "Havencraft", "", "Puresong Priest"
    mana, attack, health = 6, 5, 5
    index = "SV_Fortune~Havencraft~Minion~6~5~5~None~Puresong Priest~Accelerate~Battlecry"
    requireTarget, keyWord, description = False, "", "Accelerate (1): Restore 1 defense to your leader. If an allied follower with Ward is in play, draw a card.Fanfare: Restore 4 defense to all allies."
    accelerateSpell = PuresongPriest_Accelerate
    attackAdd, healthAdd = 2, 2

    def getMana(self):
        if self.Game.Manas.manas[self.ID] < self.mana:
            return 1
        else:
            return self.mana

    def willAccelerate(self):
        curMana = self.Game.Manas.manas[self.ID]
        return self.mana > curMana >= 1

    def effectCanTrigger(self):
        self.effectViable = "sky blue" if self.willAccelerate() and self.targetExists() else False

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        chars = self.Game.charsAlive(self.ID)
        self.restoresAOE(chars, 4)
        PRINT(self.Game, "Puresong Priest's Fanfare restores 4 defense to all allies.")
        return None


"""Portalcraft cards"""

"""DLC cards"""


class ArchangelofEvocation(SVMinion):
    Class, race, name = "Neutral", "", "Archangel of Evocation"
    mana, attack, health = 5, 3, 5
    index = "SV_Fortune~Neutral~Minion~5~3~5~None~Archangel of Evocation~Taunt~Battlecry"
    requireTarget, keyWord, description = False, "Taunt", "Ward. Fanfare: Add 1 to the cost of all non-follower cards in your opponent's hand until the start of your next turn."
    attackAdd, healthAdd = 2, 2

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        PRINT(self.Game,
              "Archangel of Evocation's Fanfare adds 1 to the cost of all non-follower cards in your opponent's hand until the start of your next turn.")
        self.Game.Manas.CardAuras_Backup.append(ManaEffect_ArchangelofEvocation(self.Game, 3 - self.ID))
        return None

    def inHandEvolving(self, target=None):
        self.Game.heroes[self.ID].health_max += 5
        self.restoresHealth(self.Game.heroes[self.ID], 5)
        PRINT(self.Game,
              "Archangel of Evocation's Evolve increases your leader's maximum defense by 5 and restores 5 defense to your leader.")


class ManaEffect_ArchangelofEvocation(TempManaEffect):
    def __init__(self, Game, ID):
        self.Game, self.ID = Game, ID
        self.changeby, self.changeto = +1, -1
        self.temporary = True
        self.auraAffected = []

    def applicable(self, target):
        return target.ID == self.ID and target.type != "Minion"

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        self.applies(target[0])

    # 持续整个回合的光环可以不必注册"ManaPaid"
    def auraAppears(self):
        for card in self.Game.Hand_Deck.hands[1]: self.applies(card)
        for card in self.Game.Hand_Deck.hands[2]: self.applies(card)
        self.Game.Manas.calcMana_All()

    # auraDisappears()可以尝试移除ManaPaid，当然没有反应，所以不必专门定义
    def selfCopy(self, game):
        return type(self)(game, self.ID)


class AerinForeverBrilliant(SVMinion):
    Class, race, name = "Forestcraft", "", "Aerin, Forever Brilliant"
    mana, attack, health = 3, 1, 5
    index = "SV_Fortune~Forestcraft~Minion~3~1~5~None~Aerin, Forever Brilliant~Legendary"
    requireTarget, keyWord, description = False, "", "Fanfare: Put a random follower with Accelerate from your deck into your hand. Whenever you play a card using its Accelerate effect, deal 2 damage to all enemies."
    attackAdd, healthAdd = 2, 2

    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.trigsBoard = [Trig_AerinForeverBrilliant(self)]

    def inHandEvolving(self, target=None):
        curGame = self.Game
        if curGame.mode == 0:
            PRINT(self.Game,
                  "Aerin, Forever Brilliant's Evolve puts a random a random follower with Accelerate from your deck into your hand.")
            if curGame.guides:
                i = curGame.guides.pop(0)
            else:
                minions = [i for i, card in enumerate(curGame.Hand_Deck.decks[self.ID]) if
                           card.type == "Minion" and "~Accelerate" in card.index]
                i = npchoice(minions) if minions else -1
                curGame.fixedGuides.append(i)
            if i > -1: curGame.Hand_Deck.drawCard(self.ID, i)


class Trig_AerinForeverBrilliant(TrigBoard):
    def __init__(self, entity):
        self.blank_init(entity, ["SpellPlayed"])

    def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
        return subject.ID == self.entity.ID and self.entity.onBoard and "~Accelerate" in subject.index

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        if "~Accelerate" in subject.index:
            self.entity.restoresHealth(self.entity.Game.heroes[self.entity.ID], 2)
            self.entity.Game.restoreEvolvePoint(self.entity.ID)
            PRINT(self.entity.Game,
                  f"Aerin, Forever Brilliant restore 2 defense to your leader and recover 1 evolution point.")
            for t in self.entity.trigsBoard:
                if type(t) == Trig_AerinForeverBrilliant:
                    t.disconnect()
                    self.entity.trigsBoard.remove(t)
                    break
            trigger = Trig_EndAerinForeverBrilliant(self.entity)
            self.entity.trigsBoard.append(trigger)
            trigger.connect()


class Trig_EndAerinForeverBrilliant(TrigBoard):
    def __init__(self, entity):
        self.blank_init(entity, ["TurnEnds"])

    def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.onBoard and ID == self.entity.ID

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        for t in self.entity.trigsBoard:
            if type(t) == Trig_EndAerinForeverBrilliant:
                t.disconnect()
                self.entity.trigsBoard.remove(t)
                break
        trigger = Trig_AerinForeverBrilliant(self.entity)
        self.entity.trigsBoard.append(trigger)
        trigger.connect()


class FuriousMountainDeity(SVMinion):
    Class, race, name = "Forestcraft", "", "Furious Mountain Deity"
    mana, attack, health = 4, 3, 4
    index = "SV_Fortune~Forestcraft~Minion~4~3~4~None~Furious Mountain Deity~Enhance~Battlecry"
    requireTarget, keyWord, description = False, "", "Fanfare: Enhance (7) - Gain +2/+2 and Rush. Strike: Gain +1/+0."
    attackAdd, healthAdd = 2, 2

    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.trigsBoard = [Trig_FuriousMountainDeity(self)]

    def getMana(self):
        if self.Game.Manas.manas[self.ID] >= 7:
            return 7
        else:
            return self.mana

    def willEnhance(self):
        return self.Game.Manas.manas[self.ID] >= 7

    def effectCanTrigger(self):
        self.effectViable = self.willEnhance()

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if comment == 7:
            PRINT(self.Game,
                  "Furious Mountain Deity's Enhanced Fanfare gives it +2/+2 and Rush")
            self.buffDebuff(2, 2)
            self.getsKeyword("Rush")
        return target


class Trig_FuriousMountainDeity(TrigBoard):
    def __init__(self, entity):
        self.blank_init(entity, ["MinionAttackingMinion", "MinionAttackingHero"])

    def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.onBoard and subject.ID == self.entity.ID and subject == self.entity

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        PRINT(self.entity.Game, "Furious Mountain Deity gains +1/+0")
        self.entity.buffDebuff(1, 0)


class DeepwoodAnomaly(SVMinion):
    Class, race, name = "Forestcraft", "", "Deepwood Anomaly"
    mana, attack, health = 8, 8, 8
    index = "SV_Fortune~Forestcraft~Minion~8~8~8~None~Deepwood Anomaly~Battlecry~Legendary"
    requireTarget, keyWord, description = False, "", "Fanfare: Enhance (7) - Gain +2/+2 and Rush. Strike: Gain +1/+0."
    attackAdd, healthAdd = 2, 2

    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.trigsBoard = [Trig_DeepwoodAnomaly(self)]


class Trig_DeepwoodAnomaly(TrigBoard):
    def __init__(self, entity):
        self.blank_init(entity, ["MinionAttackingHero"])

    def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.onBoard and subject.ID == self.entity.ID and target.ID != self.entity.ID and subject == self.entity

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        hero = self.entity.Game.heroes[3 - self.entity.ID]
        PRINT(self.entity.Game, f"Deepwood Anomaly deals {hero.health} damage to enemy hero")
        self.entity.dealsDamage(hero, hero.health)


class LifeBanquet(SVSpell):
    Class, name = "Forestcraft", "Life Banquet"
    requireTarget, mana = False, 3
    index = "SV_Fortune~Forestcraft~Spell~3~Life Banquet"
    description = "Draw 2 cards. If at least 2 other cards were played this turn, summon a Furious Mountain Deity. Then, if at least 8 other cards were played this turn, summon 2 Deepwood Anomalies."

    def effectCanTrigger(self):
        self.effectViable = self.Game.combCards(self.ID) >= 2

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        self.Game.Hand_Deck.drawCard(self.ID)
        self.Game.Hand_Deck.drawCard(self.ID)
        PRINT(self.Game, f"Life Banquet let player draw 2 cards")
        if self.Game.combCards(self.ID) >= 2:
            self.Game.summon([FuriousMountainDeity(self.Game, self.ID)], (-1, "totheRightEnd"),
                             self.ID)
            if self.Game.combCards(self.ID) >= 8:
                self.Game.summon([DeepwoodAnomaly(self.Game, self.ID)], (-1, "totheRightEnd"),
                                 self.ID)
        return target


class IlmisunaDiscordHawker(SVMinion):
    Class, race, name = "Swordcraft", "Officer", "Ilmisuna, Discord Hawker"
    mana, attack, health = 2, 2, 2
    index = "SV_Fortune~Swordcraft~Minion~2~2~2~Officer~Ilmisuna, Discord Hawker~Battlecry"
    requireTarget, keyWord, description = False, "", "Fanfare: Rally (15) - Recover 1 evolution point."
    attackAdd, healthAdd = 2, 2
    evolveRequireTarget = True

    def evolveTargetExists(self, choice=0):
        return self.selectableEnemyMinionExists()

    def evolveTargetCorrect(self, target, choice=0):
        if isinstance(target, list): target = target[0]
        return target.type == "Minion" and target.onBoard and target.ID != self.ID

    def effectCanTrigger(self):
        self.effectViable = self.Game.Counters.numMinionsSummonedThisGame[self.ID] >= 15

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if self.Game.Counters.numMinionsSummonedThisGame[self.ID] >= 15:
            self.Game.restoreEvolvePoint(self.ID)
        return None

    def inHandEvolving(self, target=None):
        if target:
            if isinstance(target, list): target = target[0]
            self.dealsDamage(target, len(self.Game.minionsonBoard[self.ID]))
            PRINT(self.Game,
                  f"Ilmisuna, Discord Hawker's Evolve deals {len(self.Game.minionsonBoard[self.ID])} damage to {target.name} -4/-0.")
        return target


class AlyaskaWarHawker(SVMinion):
    Class, race, name = "Swordcraft", "Commander", "Alyaska, War Hawker"
    mana, attack, health = 4, 4, 4
    index = "SV_Fortune~Swordcraft~Minion~4~4~4~Commander~Alyaska, War Hawker~Legendary"
    requireTarget, keyWord, description = False, "", "Reduce damage from effects to 0. When an allied Officer follower comes into play, gain the ability to evolve for 0 evolution points."
    attackAdd, healthAdd = 2, 2

    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.trigsBoard = [Trig_AlyaskaWarHawker(self)]
        self.marks["Enemy Effect Damage Immune"] = 1

    def inHandEvolving(self, target=None):
        PRINT(self.Game, "Alyaska, War Hawker's Evolve put a Exterminus Weapon into your hand.")
        card = ExterminusWeapon(self.Game, self.ID)
        self.Game.Hand_Deck.addCardtoHand(card, self.ID)
        ManaMod(card, changeby=-self.Game.Counters.evolvedThisGame[self.ID], changeto=-1).applies()


class Trig_AlyaskaWarHawker(TrigBoard):
    def __init__(self, entity):
        self.blank_init(entity, ["MinionSummoned"])

    def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.onBoard and subject.ID == self.entity.ID and subject != self.entity and "Officer" in subject.race

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        self.entity.marks["Free Evolve"] += 1
        PRINT(self.entity.Game, f"Alyaska, War Hawker gain the ability to evolve for 0 evolution points.")


class ExterminusWeapon(SVMinion):
    Class, race, name = "Swordcraft", "Commander", "Exterminus Weapon"
    mana, attack, health = 8, 6, 6
    index = "SV_Fortune~Swordcraft~Minion~8~6~6~Commander~Exterminus Weapon~Battlecry~Deathrattle~Uncollectible~Legendary"
    requireTarget, keyWord, description = True, "", "Fanfare: Destroy 2 enemy followers. Last Words: Deal 4 damage to the enemy leader."
    attackAdd, healthAdd = 2, 2

    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.deathrattles = [Deathrattle_ExterminusWeapon(self)]

    def returnTrue(self, choice=0):
        n = 0
        for m in self.Game.minionsAlive(3 - self.ID):
            if self.canSelect(m):
                n += 1
        return len(self.targets) < min(2, n)

    def targetExists(self, choice=0):
        return self.selectableEnemyMinionExists()

    def targetCorrect(self, target, choice=0):
        if isinstance(target, list) and len(target) > 1:
            target1, target2 = target[0], target[1]
            return target1.type == "Minion" and target1.ID != self.ID and target1.onBoard and target2.type == "Minion" and target2.ID != self.ID and target2.onBoard
        else:
            if isinstance(target, list): target = target[0]
            return target.type == "Minion" and target.ID != self.ID and target.onBoard

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if target:
            self.Game.killMinion(self, target[0])
            if len(target) > 1:
                self.Game.killMinion(self, target[1])


class Deathrattle_ExterminusWeapon(Deathrattle_Minion):
    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        PRINT(self.entity.Game, "Last Words: Deal 4 damage to the enemy leader.")
        self.entity.dealsDamage(self.entity.Game.heroes[3 - self.entity.ID], 4)


class RunieResoluteDiviner(SVMinion):
    Class, race, name = "Runecraft", "", "Runie, Resolute Diviner"
    mana, attack, health = 2, 1, 2
    index = "SV_Fortune~Runecraft~Minion~2~1~2~None~Runie, Resolute Diviner~Spellboost~Battlecry~Legendary"
    requireTarget, keyWord, description = False, "", "Fanfare: Spellboost the cards in your hand 1 time. If this card has been Spellboosted at least 1 time, draw a card. Then, if it has been at least 4 times, deal 3 damage to a random enemy follower. Then, if it has been at least 7 times, deal 3 damage to the enemy leader and restore 3 defense to your leader. Then, if it has been at least 10 times, put 3 Runie, Resolute Diviners into your hand."
    attackAdd, healthAdd = 2, 2

    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.trigsHand = [Trig_Spellboost(self)]
        self.progress = 0

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        self.Game.sendSignal("Spellboost", self.ID, self, None, 0, "", choice)
        if self.progress >= 1:
            self.Game.Hand_Deck.drawCard(self.ID)
            PRINT(self.Game, f"Runie, Resolute Diviner's Fanfare let player draw a card")
            if self.progress >= 4:
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
                              f"Runie, Resolute Diviner's Fanfare deals 3 damage to enemy minion {curGame.minions[3 - self.ID][i].name}")
                        self.dealsDamage(curGame.minions[3 - self.ID][i], 3)
                if self.progress >= 7:
                    PRINT(self.Game,
                          f"Runie, Resolute Diviner's Fanfare deals 3 damage to enemy player and restores 3 defense to your leader")
                    self.dealsDamage(self.Game.heroes[3 - self.ID], 3)
                    self.restoresHealth(self.Game.heroes[self.ID], 3)
                    if self.progress >= 10:
                        self.Game.Hand_Deck.addCardtoHand([RunieResoluteDiviner for i in range(3)], self.ID, "type")
                        PRINT(self.Game,
                              f"Runie, Resolute Diviner's Fanfare puts 3 Runie, Resolute Diviners into your hand")


class AlchemicalCraftschief_Accelerate(SVSpell):
    Class, name = "Runecraft", "Alchemical Craftschief"
    requireTarget, mana = False, 2
    index = "SV_Fortune~Runecraft~Spell~2~Alchemical Craftschief~Accelerate~Uncollectible"
    description = "Summon an Earth Essence. Put a 7-play point Alchemical Craftschief (without Accelerate) into your hand and subtract X from its cost. X equals the number of allied Earth Sigil amulets in play."

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        self.Game.summon(
            [EarthEssence(self.Game, self.ID)], (-1, "totheRightEnd"), self.ID)
        PRINT(self.Game,
              f"Alchemical Craftschief's Accelerate summons an Earth Essence")
        n = len(self.Game.earthsonBoard(self.ID))
        card = AlchemicalCraftschief_Token(self.Game, self.ID)
        self.Game.Hand_Deck.addCardtoHand(card, self.ID)
        ManaMod(card, changeby=-n, changeto=-1).applies()
        PRINT(self.Game,
              f"Alchemical Craftschief's Accelerate Put a 7-play point Alchemical Craftschief (without Accelerate) into your hand and subtract {n} from its cost")
        return None


class AlchemicalCraftschief_Token(SVMinion):
    Class, race, name = "Runecraft", "", "Alchemical Craftschief"
    mana, attack, health = 7, 4, 4
    index = "SV_Fortune~Runecraft~Minion~7~4~4~None~Alchemical Craftschief~Taunt~Battlecry~Uncollectible"
    requireTarget, keyWord, description = True, "Taunt", "Accelerate (2): Summon an Earth Essence. Put a 7-play point Alchemical Craftschief (without Accelerate) into your hand and subtract X from its cost. X equals the number of allied Earth Sigil amulets in play.Ward.Fanfare: Deal 4 damage to an enemy."
    attackAdd, healthAdd = 2, 2

    def targetCorrect(self, target, choice=0):
        if isinstance(target, list): target = target[0]
        return target.type in ["Minion", "Hero"] and target.ID != self.ID and target.onBoard

    def targetExists(self, choice=0):
        return self.selectableEnemyExists()

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if target:
            if isinstance(target, list): target = target[0]
            self.dealsDamage(target, 4)
            PRINT(self.Game, f"Alchemical Craftschief deals 4 damage to {target.name}")
        return target


class AlchemicalCraftschief(SVMinion):
    Class, race, name = "Runecraft", "", "Alchemical Craftschief"
    mana, attack, health = 8, 4, 4
    index = "SV_Fortune~Runecraft~Minion~8~4~4~None~Alchemical Craftschief~Taunt~Battlecry~Accelerate"
    requireTarget, keyWord, description = True, "Taunt", "Accelerate (2): Summon an Earth Essence. Put a 7-play point Alchemical Craftschief (without Accelerate) into your hand and subtract X from its cost. X equals the number of allied Earth Sigil amulets in play.Ward.Fanfare: Deal 4 damage to an enemy."
    accelerateSpell = AlchemicalCraftschief_Accelerate
    attackAdd, healthAdd = 2, 2

    def getMana(self):
        if self.Game.Manas.manas[self.ID] < self.mana:
            return 2
        else:
            return self.mana

    def targetCorrect(self, target, choice=0):
        if not self.willAccelerate():
            if isinstance(target, list): target = target[0]
            return target.type in ["Minion", "Hero"] and target.ID != self.ID and target.onBoard
        return False

    def willAccelerate(self):
        curMana = self.Game.Manas.manas[self.ID]
        return self.mana > curMana >= 2

    def effectCanTrigger(self):
        self.effectViable = "sky blue" if self.willAccelerate() else False

    def returnTrue(self, choice=0):
        if not self.willAccelerate():
            return not self.targets
        return False

    def targetExists(self, choice=0):
        return self.selectableEnemyExists()

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if target:
            if isinstance(target, list): target = target[0]
            self.dealsDamage(target, 4)
            PRINT(self.Game, f"Alchemical Craftschief deals 4 damage to {target.name}")
        return target


class WhitefrostWhisper(SVSpell):
    Class, name = "Dragoncraft", "Whitefrost Whisper"
    requireTarget, mana = True, 2
    index = "SV_Fortune~Dragoncraft~Spell~2~Whitefrost Whisper~Uncollectible~Legendary"
    description = "Select an enemy follower and destroy it if it is already damaged. If it has not been damaged, deal 1 damage instead."

    def targetExists(self, choice=0):
        return self.selectableEnemyMinionExists()

    def targetCorrect(self, target, choice=0):
        if isinstance(target, list): target = target[0]
        return target.type == "Minion" and target.ID != self.ID and target.onBoard

    def available(self):
        return self.selectableEnemyMinionExists()

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if target:
            if isinstance(target, list): target = target[0]
            if target.health < target.health_max:
                self.Game.killMinion(self, target)
                PRINT(self.Game,
                      f"Whitefrost Whisper destroys minion {target.name}")
            else:
                damage = (1 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
                PRINT(self.Game,
                      f"Whitefrost Whisper deals {damage} damage to minion {target.name}")
                self.dealsDamage(target, damage)
        return target


class FileneAbsoluteZero(SVMinion):
    Class, race, name = "Dragoncraft", "", "Filene, Absolute Zero"
    mana, attack, health = 3, 1, 3
    index = "SV_Fortune~Dragoncraft~Minion~3~1~3~None~Filene, Absolute Zero~Battlecry~Legendary"
    requireTarget, keyWord, description = False, "", "Fanfare: Draw a card if Overflow is active for you."
    attackAdd, healthAdd = 2, 2

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        minions = self.Game.minionsonBoard(3 - self.ID)
        self.dealsAOE(minions, [1 for obj in minions])
        self.Game.Hand_Deck.addCardtoHand([WhitefrostWhisper], self.ID, "type")
        PRINT(self.Game,
              f"Filene, Absolute Zero's Fanfare deals 1 damage to all enemy followers and put a Whitefrost Whisper into your hand")

    def inHandEvolving(self, target=None):
        card = WhitefrostWhisper(self.Game, self.ID)
        self.Game.Hand_Deck.addCardtoHand([card], self.ID)
        ManaMod(card, changeby=0, changeto=1).applies()
        PRINT(self.Game,
              f"Filene, Absolute Zero's Evolve put a Whitefrost Whisper into your hand and change its cost to 1")


class EternalWhale(SVMinion):
    Class, race, name = "Dragoncraft", "", "Eternal Whale"
    mana, attack, health = 6, 5, 7
    index = "SV_Fortune~Dragoncraft~Minion~6~5~7~None~Eternal Whale~Taunt"
    requireTarget, keyWord, description = False, "Taunt", "Ward.When this follower comes into play, deal 2 damage to the enemy leader.When this follower leaves play, put four 1-play point Eternal Whales into your deck. (Transformation doesn't count as leaving play.)"
    attackAdd, healthAdd = 2, 2

    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.appearResponse = [self.whenAppears]
        self.disappearResponse = [self.whenDisppears]

    def whenAppears(self):
        PRINT(self.Game, f"Eternal Whale appears and deals 2 damage to the enemy leader")
        self.dealsDamage(self.Game.heroes[3 - self.ID], 2)

    def whenDisppears(self):
        PRINT(self.Game, f"Eternal Whale leaves board and put four 1-play point Eternal Whales into your deck.")
        cards = [EternalWhale_Token(self.Game, self.ID) for i in range(4)]
        self.Game.Hand_Deck.shuffleCardintoDeck(cards, self.ID)
        for card in cards:
            ManaMod(card, changeby=0, changeto=1).applies()


class EternalWhale_Token(SVMinion):
    Class, race, name = "Dragoncraft", "", "Eternal Whale"
    mana, attack, health = 1, 5, 7
    index = "SV_Fortune~Dragoncraft~Minion~1~5~7~None~Eternal Whale~Taunt~Uncollectible"
    requireTarget, keyWord, description = False, "Taunt", "Ward.When this follower comes into play, deal 2 damage to the enemy leader.When this follower leaves play, put four 1-play point Eternal Whales into your deck. (Transformation doesn't count as leaving play.)"
    attackAdd, healthAdd = 2, 2

    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.appearResponse = [self.whenAppears]
        self.disappearResponse = [self.whenDisppears]

    def whenAppears(self):
        PRINT(self.Game, f"Eternal Whale appears and deals 2 damage to the enemy leader")
        self.dealsDamage(self.Game.heroes[3 - self.ID], 2)

    def whenDisppears(self):
        PRINT(self.Game, f"Eternal Whale leaves board and put four 1-play point Eternal Whales into your deck.")
        cards = [EternalWhale_Token(self.Game, self.ID) for i in range(4)]
        self.Game.Hand_Deck.shuffleCardintoDeck(cards, self.ID)


class ForcedResurrection(SVSpell):
    Class, name = "Shadowcraft", "Forced Resurrection"
    requireTarget, mana = True, 2
    index = "SV_Fortune~Shadowcraft~Spell~2~Forced Resurrection"
    description = "Destroy a follower. Both players perform Reanimate (3)."

    def available(self):
        return self.selectableEnemyMinionExists()

    def targetCorrect(self, target, choice=0):
        if isinstance(target, list): target = target[0]
        return target.type == "Minion" and target.ID != self.ID and target.onBoard

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if target:
            if isinstance(target, list): target = target[0]
            PRINT(self.Game, f"Forced Resurrection destroys enemy {target.name}")
            self.Game.killMinion(target)
            minion = self.Game.reanimate(self.ID, 3)
            if minion:
                PRINT(self.Game, f"Forced Resurrection summons {minion.name}")
            minion = self.Game.reanimate(3 - self.ID, 3)
            if minion:
                PRINT(self.Game, f"Forced Resurrection summons {minion.name}")
        return target


class NephthysGoddessofAmenta(SVMinion):
    Class, race, name = "Shadowcraft", "", "Nephthys, Goddess of Amenta"
    mana, attack, health = 6, 5, 5
    index = "SV_Fortune~Shadowcraft~Minion~6~5~5~None~Nephthys, Goddess of Amenta~Battlecry~Enhance~Legendary"
    requireTarget, keyWord, description = False, "", "Fanfare: Put 2 random followers of different costs (excluding Nephthys, Goddess of Amenta) from your deck into play and destroy them. Enhance (10): Then, if allied followers that originally cost 1, 2, 3, 4, 5, 6, 7, 8, 9, and 10 play points have been destroyed, win the match."
    attackAdd, healthAdd = 2, 2

    def getMana(self):
        if self.Game.Manas.manas[self.ID] >= 10:
            return 10
        else:
            return self.mana

    def willEnhance(self):
        return self.Game.Manas.manas[self.ID] >= 10

    def effectCanTrigger(self):
        self.effectViable = self.willEnhance()

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        minions = []
        curGame = self.Game
        if curGame.mode == 0:
            for num in range(2):
                if curGame.guides:
                    i = curGame.guides.pop(0)
                else:
                    cards = [i for i, card in enumerate(self.Game.Hand_Deck.decks[self.ID]) if
                             card.type == "Minion"]
                    i = npchoice(cards) if cards and curGame.space(self.ID) > 0 else -1
                    curGame.fixedGuides.append(i)
                if i > -1:
                    minion = curGame.summonfromDeck(i, self.ID, -1, self.ID)
                    if minion:
                        minions.append(minion)
                else:
                    break
        for minion in minions:
            self.Game.killMinion(self, minion)
            PRINT(curGame, f"Nephthys, Goddess of Amenta summons {minion.name} and destroys it")
        self.Game.gathertheDead()
        if comment == 10:
            indices = self.Game.Counters.minionsDiedThisGame[self.ID]
            minions = {}
            for index in indices:
                try:
                    minions[self.Game.cardPool[index].mana].append(self.Game.cardPool[index])
                except:
                    minions[self.Game.cardPool[index].mana] = [self.Game.cardPool[index]]
            quest = True
            for i in range(1, 11):
                if i not in minions:
                    quest = False
            if quest:
                self.Game.heroes[3 - self.ID].dead = True
                self.Game.gathertheDead(True)
        return None


class Nightscreech(SVSpell):
    Class, name = "Bloodcraft", "Nightscreech"
    requireTarget, mana = False, 1
    index = "SV_Fortune~Bloodcraft~Spell~1~Nightscreech"
    description = "Summon a Forest Bat. If Wrath is active for you, evolve it and draw 1 card. Otherwise, deal 1 damage to your leader."

    def effectCanTrigger(self):
        self.effectViable = self.Game.isWrath(self.ID)

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        minion = ForestBat(self.Game, self.ID)
        PRINT(self.Game, f"Nightscreech summons a Forest Bat")
        self.Game.summon([minion], (-1, "totheRightEnd"), self.ID)
        if self.Game.isWrath(self.ID):
            minion.evolve()
            self.Game.Hand_Deck.drawCard(self.ID)
            PRINT(self.Game, f"Nightscreech evolves the Forest Bat and draw a card")
        else:
            damage = (1 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
            self.dealsDamage(self.Game.heroes[self.ID], damage)
            PRINT(self.Game, f"Nightscreech deals {damage} damage to you")
        return target


class Baal(SVMinion):
    Class, race, name = "Bloodcraft", "", "Baal"
    mana, attack, health = 3, 3, 3
    index = "SV_Fortune~Bloodcraft~Minion~3~3~3~None~Baal~Battlecry~Fusion~Legendary"
    requireTarget, keyWord, description = False, "", "Fusion: Bloodcraft followers that originally cost 3 play points or less Fanfare: If this card is fused with at least 3 cards, draw cards until there are 6 cards in your hand. Then, if this card is fused with at least 6 cards, deal 6 damage to all enemy followers."
    attackAdd, healthAdd = 2, 2

    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.fusion = 1
        self.fusionMaterials = 0

    def findFusionMaterials(self):
        return [card for card in self.Game.Hand_Deck.hands[self.ID] if
                card.type == "Minion" and card != self and card.Class == "Bloodcraft" and type(card).mana <= 3]

    def effectCanTrigger(self):
        self.effectViable = self.fusionMaterials >= 3

    def fusionDecided(self, objs):
        if objs:
            self.fusionMaterials += len(objs)
            self.Game.Hand_Deck.extractfromHand(self, enemyCanSee=True)
            for obj in objs: self.Game.Hand_Deck.extractfromHand(obj, enemyCanSee=True)
            self.Game.Hand_Deck.addCardtoHand(self, self.ID)
            self.fusion = 0  # 一张卡每回合只有一次融合机会

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if self.fusionMaterials >= 3:
            PRINT(self.Game, "Baal draw cards until there are 6 cards in your hand")
            n = max(0, 6 - len(self.Game.Hand_Deck.hands[self.ID]))
            for i in range(n):
                self.Game.Hand_Deck.drawCard(self.ID)
            if self.fusionMaterials > 6:
                targets = self.Game.minionsonBoard(3 - self.ID)
                PRINT(self.Game, f"Baal deals 6 damage to all enemy minions.")
                self.dealsAOE(targets, [6 for minion in targets])
        return target


class ServantofDarkness(SVMinion):
    Class, race, name = "Neutral", "", "Servant of Darkness"
    mana, attack, health = 5, 13, 13
    index = "SV_Fortune~Neutral~Minion~5~13~13~None~Servant of Darkness~Uncollectible~Legendary"
    requireTarget, keyWord, description = False, "", ""
    attackAdd, healthAdd = 2, 2


class SilentRider(SVMinion):
    Class, race, name = "Neutral", "", "Silent Rider"
    mana, attack, health = 6, 8, 8
    index = "SV_Fortune~Neutral~Minion~6~8~8~None~Silent Rider~Charge~Uncollectible~Legendary"
    requireTarget, keyWord, description = False, "Charge", "Storm."
    attackAdd, healthAdd = 2, 2


class DissDamnation(SVSpell):
    Class, name = "Neutral", "Dis's Damnation"
    requireTarget, mana = True, 7
    index = "SV_Fortune~Neutral~Spell~7~Dis's Damnation~Uncollectible~Legendary"
    description = "Deal 7 damage to an enemy. Restore 7 defense to your leader."

    def available(self):
        return self.selectableEnemyExists()

    def targetCorrect(self, target, choice=0):
        if isinstance(target, list): target = target[0]
        return (target.type == "Minion" or target.type == "Hero") and target.ID != self.ID and target.onBoard

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if target:
            if isinstance(target, list): target = target[0]
            damage = (7 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
            heal = 7 * (2 ** self.countHealDouble())
            PRINT(self.Game,
                  f"Dis's Damnation deals {damage} damage to enemy {target.name} and restore {heal} defense to your leader.")
            self.dealsDamage(target, damage)
            self.restoresHealth(self.Game.heroes[self.ID], heal)
        return target


class AstarothsReckoning(SVSpell):
    Class, name = "Neutral", "Astaroth's Reckoning"
    requireTarget, mana = False, 10
    index = "SV_Fortune~Neutral~Spell~10~Astaroth's Reckoning~Uncollectible~Legendary"
    description = "Deal 7 damage to an enemy. Restore 7 defense to your leader."

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        damage = (self.Game.heroes[3 - self.ID].health - 1 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
        PRINT(self.Game,
              f"Dis's Damnation deals {damage} damage to enemy leader.")
        self.dealsDamage(self.Game.heroes[3 - self.ID], damage)
        return False


class PrinceofDarkness(SVMinion):
    Class, race, name = "Neutral", "", "Prince of Darkness"
    mana, attack, health = 10, 6, 6
    index = "SV_Fortune~Neutral~Minion~10~6~6~None~Prince of Darkness~Battlecry~Legendary"
    requireTarget, keyWord, description = False, "", ""
    attackAdd, healthAdd = 2, 2

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        self.Game.Hand_Deck.extractfromDeck(None, self.ID, all=True)
        cards = [
            ServantofDarkness(self.Game, self.ID),
            ServantofDarkness(self.Game, self.ID),
            ServantofDarkness(self.Game, self.ID),
            SilentRider(self.Game, self.ID),
            SilentRider(self.Game, self.ID),
            SilentRider(self.Game, self.ID),
            DissDamnation(self.Game, self.ID),
            DissDamnation(self.Game, self.ID),
            DissDamnation(self.Game, self.ID),
            AstarothsReckoning(self.Game, self.ID),
        ]
        self.Game.Hand_Deck.shuffleCardintoDeck(cards, self.ID)
        PRINT(self.Game,
              f"Prince of Darkness's Fanfare replaces your deck with an Apocalypse Deck.")
        return None


class DemonofPurgatory(SVMinion):
    Class, race, name = "Neutral", "", "Demon of Purgatory"
    mana, attack, health = 6, 9, 6
    index = "SV_Fortune~Neutral~Minion~6~9~6~None~Demon of Purgatory~Battlecry~Uncollectible~Legendary"
    requireTarget, keyWord, description = False, "", "Fanfare: Give the enemy leader the following effect - At the start of your next turn, discard a random card from your hand."
    attackAdd, healthAdd = 2, 2

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        trigger = Trig_DemonofPurgatory(self.Game.heroes[3 - self.ID])
        # for t in self.entity.Game.heroes[self.entity.ID].trigsBoard:
        #     if type(t) == type(trigger):
        #         return
        self.Game.heroes[3 - self.ID].trigsBoard.append(trigger)
        trigger.connect()
        return None


class Trig_DemonofPurgatory(TrigBoard):
    def __init__(self, entity):
        self.blank_init(entity, ["TurnStarts"])

    def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.onBoard and ID == self.entity.ID

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        PRINT(self.entity.Game,
              "At the start of your turn, discard a random card from your hand.")
        curGame = self.entity.Game
        if curGame.mode == 0:
            if curGame.guides:
                i = curGame.guides.pop(0)
            else:
                ownHand = curGame.Hand_Deck.hands[self.entity.ID]
                i = nprandint(len(ownHand)) if ownHand else -1
                curGame.fixedGuides.append(i)
            if i > -1: curGame.Hand_Deck.discardCard(self.entity.ID, i)


class ScionofDesire(SVMinion):
    Class, race, name = "Neutral", "", "Servant of Darkness"
    mana, attack, health = 4, 5, 5
    index = "SV_Fortune~Neutral~Minion~4~5~5~None~Servant of Darkness~Uncollectible~Legendary"
    requireTarget, keyWord, description = False, "", "At the end of your turn, destroy a random enemy follower. Restore X defense to your leader. X equals that follower's attack."
    attackAdd, healthAdd = 2, 2

    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.trigsBoard = [Trig_ScionofDesire]


class Trig_ScionofDesire(TrigBoard):
    def __init__(self, entity):
        self.blank_init(entity, ["TurnEnds"])

    def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.onBoard and ID == self.entity.ID

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        curGame = self.entity.Game
        if curGame.mode == 0:
            enemy = None
            if curGame.guides:
                i, where = curGame.guides.pop(0)
                if where: enemy = curGame.find(i, where)
            else:
                chars = curGame.minionsAlive(3 - self.entity.ID)
                if chars:
                    enemy = npchoice(chars)
                    curGame.fixedGuides.append((enemy.position, enemy.type + str(enemy.ID)))
                else:
                    curGame.fixedGuides.append((0, ''))
            if enemy:
                heal = enemy.attack
                PRINT(self.entity.Game,
                      f"Scion of Desire destroys {enemy.name} and restores {heal} defense to your leader")
                self.entity.Game.killMinion(self.entity, enemy)
                self.entity.restoresHealth(self.entity.Game.heroes[self.entity.ID], heal)


class GluttonousBehemoth(SVMinion):
    Class, race, name = "Neutral", "", "Gluttonous Behemoth"
    mana, attack, health = 7, 7, 7
    index = "SV_Fortune~Neutral~Minion~7~7~7~None~Gluttonous Behemoth~Uncollectible~Legendary"
    requireTarget, keyWord, description = False, "", "At the end of your turn, deal 7 damage to the enemy leader."
    attackAdd, healthAdd = 2, 2

    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.trigsBoard = [Trig_GluttonousBehemoth]

    def inEvolving(self):
        for trig in self.trigsBoard:
            if type(trig) == Trig_GluttonousBehemoth:
                trig.disconnect()
                self.trigsBoard.remove(trig)
        trigger = Trig_EvolvedGluttonousBehemoth(self)
        self.trigsBoard.append(trigger)
        trigger.connect()


class Trig_GluttonousBehemoth(TrigBoard):
    def __init__(self, entity):
        self.blank_init(entity, ["TurnEnds"])

    def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.onBoard and ID == self.entity.ID

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        self.entity.dealsDamage(self.entity.Game.heroes[3 - self.entity.ID], 7)
        PRINT(self.entity.Game, f"At the end of your turn, deal 7 damage to the enemy leader.")


class Trig_EvolvedGluttonousBehemoth(TrigBoard):
    def __init__(self, entity):
        self.blank_init(entity, ["TurnEnds"])

    def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.onBoard and ID == self.entity.ID

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        self.entity.dealsDamage(self.entity.Game.heroes[3 - self.entity.ID], 9)
        PRINT(self.entity.Game, f"At the end of your turn, deal 9 damage to the enemy leader.")


class ScorpionofGreed(SVMinion):
    Class, race, name = "Neutral", "", "Scorpion of Greed"
    mana, attack, health = 6, 7, 6
    index = "SV_Fortune~Neutral~Minion~6~7~6~None~Scorpion of Greed~Charge~Bane~Drain~Uncollectible~Legendary"
    requireTarget, keyWord, description = False, "Charge,Bane,Drain", "Storm.Bane.Drain."
    attackAdd, healthAdd = 2, 2


class WrathfulIcefiend(SVMinion):
    Class, race, name = "Neutral", "", "Wrathful Icefiend"
    mana, attack, health = 2, 4, 4
    index = "SV_Fortune~Neutral~Minion~2~4~4~None~Wrathful Icefiend~Battlecry~Uncollectible~Legendary"
    requireTarget, keyWord, description = False, "", "Fanfare: Recover 2 evolution points."
    attackAdd, healthAdd = 2, 2

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        self.Game.restoreEvolvePoint(self.ID, 2)
        PRINT(self.Game, f"Wrathful Icefiend's Fanfare recovers 2 evolution points.")


class HereticalHellbeast(SVMinion):
    Class, race, name = "Neutral", "", "Heretical Hellbeast"
    mana, attack, health = 8, 8, 8
    index = "SV_Fortune~Neutral~Minion~8~8~8~None~Heretical Hellbeast~Battlecry~Taunt~Uncollectible~Legendary"
    requireTarget, keyWord, description = False, "Taunt", "Ward. Fanfare: Deal X damage to your leader. X equals the number of other followers in play. Then destroy all other followers."
    attackAdd, healthAdd = 2, 2

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        minions = self.Game.minionsAlive(self.ID, self) + self.Game.minionsAlive(3 - self.ID)
        damage = len(minions)
        self.dealsDamage(self.Game.heroes[self.ID], damage)
        self.Game.killMinion(self, minions)
        PRINT(self.Game,
              f"Heretical Hellbeast's Fanfare deals {damage} damage to your leader and destroy all other followers.")


SV_Fortune_Indices = {
    "SV_Fortune~Neutral~Minion~2~5~5~None~Cloud Gigas~Taunt": CloudGigas,
    "SV_Fortune~Neutral~Spell~2~Sudden Showers": SuddenShowers,
    "SV_Fortune~Neutral~Minion~4~4~3~None~Winged Courier~Deathrattle": WingedCourier,
    "SV_Fortune~Neutral~Minion~4~1~1~None~Fieran, Havensent Wind God~Battlecry~Invocation~Legendary": FieranHavensentWindGod,
    "SV_Fortune~Natural~Spell~4~Resolve of the Fallen": ResolveoftheFallen,
    "SV_Fortune~Natural~Minion~5~3~4~None~Starbright Deity~Battlecry": StarbrightDeity,
    "SV_Fortune~Neutral~Minion~5~5~5~None~XXI. Zelgenea, The World~Battlecry~Invocation~Legendary": XXIZelgeneaTheWorld,
    "SV_Fortune~Neutral~Amulet~6~None~Titanic Showdown~Countdown~Deathrattle": TitanicShowdown,
    "SV_Fortune~Neutral~Spell~2~Pureshot Angel~Accelerate~Uncollectible": PureshotAngel_Accelerate,
    "SV_Fortune~Neutral~Minion~8~6~6~None~Pureshot Angel~Battlecry~Accelerate": PureshotAngel,

    "SV_Fortune~Forestcraft~Minion~1~1~1~None~Lumbering Carapace~Battlecry": LumberingCarapace,
    "SV_Fortune~Forestcraft~Minion~2~2~2~None~Blossoming Archer": BlossomingArcher,
    "SV_Fortune~Forestcraft~Spell~2~Soothing Spell": SoothingSpell,
    "SV_Fortune~Forestcraft~Minion~3~3~3~None~XII. Wolfraud, Hanged Man~Enhance~Battlecry~Legendary": XIIWolfraudHangedMan,
    "SV_Fortune~Forestcraft~Spell~0~Treacherous Reversal~Uncollectible": TreacherousReversal,
    "SV_Fortune~Forestcraft~Spell~1~Reclusive Ponderer~Accelerate~Uncollectible": ReclusivePonderer_Accelerate,
    "SV_Fortune~Forestcraft~Minion~4~3~3~None~Reclusive Ponderer~Stealth~Accelerate": ReclusivePonderer,
    "SV_Fortune~Forestcraft~Spell~1~Chipper Skipper~Accelerate~Uncollectible": ChipperSkipper_Accelerate,
    "SV_Fortune~Forestcraft~Minion~4~4~3~None~Chipper Skipper~Accelerate": ChipperSkipper,
    "SV_Fortune~Forestcraft~Spell~4~Fairy Assault": FairyAssault,
    "SV_Fortune~Forestcraft~Minion~5~4~5~None~Optimistic Beastmaster~Battlecry": OptimisticBeastmaster,
    "SV_Fortune~Forestcraft~Minion~6~4~4~None~Terrorformer~Battlecry~Fusion~Legendary": Terrorformer,
    "SV_Fortune~Forestcraft~Spell~1~Deepwood Wolf~Accelerate~Uncollectible": DeepwoodWolf_Accelerate,
    "SV_Fortune~Forestcraft~Minion~7~3~3~None~Deepwood Wolf~Charge~Accelerate": DeepwoodWolf,
    "SV_Fortune~Forestcraft~Spell~1~Lionel, Woodland Shadow~Accelerate~Uncollectible": LionelWoodlandShadow_Accelerate,
    "SV_Fortune~Forestcraft~Minion~7~5~6~None~Lionel, Woodland Shadow~Battlecry~Accelerate": LionelWoodlandShadow,

    "SV_Fortune~Swordcraft~Minion~1~1~1~Officer~Ernesta, Weapons Hawker~Battlecry": ErnestaWeaponsHawker,
    "SV_Fortune~Swordcraft~Minion~1~4~4~Officer~Dread Hound~Battlecry~Bane~Taunt~Uncollectible": DreadHound,
    "SV_Fortune~Swordcraft~Spell~1~Pompous Summons": PompousSummons,
    "SV_Fortune~Swordcraft~Spell~1~Decisive Strike~Enhance": DecisiveStrike,
    "SV_Fortune~Swordcraft~Minion~2~2~1~Officer~Honorable Thief~Battlecry~Deathrattle": HonorableThief,
    "SV_Fortune~Swordcraft~Spell~2~Shield Phalanx": ShieldPhalanx,
    "SV_Fortune~Swordcraft~Minion~7~5~6~Commander~Frontguard General~Taunt~Deathrattle": FrontguardGeneral,
    "SV_Fortune~Swordcraft~Minion~3~2~3~Officer~Fortress Guard~Taunt~Uncollectible": FortressGuard,
    "SV_Fortune~Swordcraft~Minion~3~2~2~Commander~Empress of Serenity~Battlecry": EmpressofSerenity,
    "SV_Fortune~Swordcraft~Minion~3~3~3~Commander~VII. Oluon, The Chariot~Battlecry~Legendary": VIIOluonTheChariot,
    "SV_Fortune~Swordcraft~Minion~7~8~16~Commander~VII. Oluon, Runaway Chariot~Uncollectible~Legendary": VIIOluonRunawayChariot,
    "SV_Fortune~Swordcraft~Minion~4~3~4~Commander~Prudent General": PrudentGeneral,
    "SV_Fortune~Swordcraft~Minion~5~4~5~Officer~Strikelance Knight~Battlecry": StrikelanceKnight,
    "SV_Fortune~Swordcraft~Minion~6~4~5~Commander~Diamond Paladin~Battlecry~Rush~Legendary": DiamondPaladin,
    "SV_Fortune~Swordcraft~Minion~9~9~7~Commander~Selfless Noble~Battlecry": SelflessNoble,

    "SV_Fortune~Runecraft~Minion~1~1~1~None~Juggling Moggy~Battlecry~EarthRite": JugglingMoggy,
    "SV_Fortune~Runecraft~Spell~1~Magical Augmentation~EarthRite": MagicalAugmentation,
    "SV_Fortune~Runecraft~Minion~2~2~2~None~Creative Conjurer~Battlecry~EarthRite": CreativeConjurer,
    "SV_Fortune~Runecraft~Spell~2~Golem Summoning~Uncollectible": GolemSummoning,
    "SV_Fortune~Runecraft~Minion~2~2~2~None~0. Lhynkal, The Fool~Battlecry~Legendary": LhynkalTheFool,
    "SV_Fortune~Runecraft~Spell~4~Rite of the Ignorant~Uncollectible~Legendary": RiteoftheIgnorant,
    "SV_Fortune~Runecraft~Spell~2~Scourge of the Omniscient~Uncollectible~Legendary": ScourgeoftheOmniscient,
    "SV_Fortune~Runecraft~Spell~2~Authoring Tomorrow": AuthoringTomorrow,
    "SV_Fortune~Runecraft~Spell~2~Madcap Conjuration": MadcapConjuration,
    "SV_Fortune~Runecraft~Minion~3~3~3~None~Arcane Auteur~Deathrattle": ArcaneAuteur,
    "SV_Fortune~Runecraft~Minion~4~3~3~None~Piquant Potioneer~Battlecry": PiquantPotioneer,
    "SV_Fortune~Runecraft~Minion~4~2~2~None~Imperator of Magic~Battlecry~Enhance~EarthRite": ImperatorofMagic,
    "SV_Fortune~Runecraft~Amulet~5~Earth Sigil~Emergency Summoning~Deathrattle~Uncollectible": EmergencySummoning,
    "SV_Fortune~Neutral~Minion~2~2~2~None~Happy Pig~Deathrattle": HappyPig,
    "SV_Fortune~Runecraft~Minion~5~4~4~None~Sweetspell Sorcerer": SweetspellSorcerer,
    "SV_Fortune~Runecraft~Spell~2~Witch Snap": WitchSnap,
    "SV_Fortune~Runecraft~Minion~6~6~6~None~Adamantine Golem~Battlecry~EarthRite~Legendary": AdamantineGolem,

    "SV_Fortune~Dragoncraft~Minion~1~1~1~None~Dragonclad Lancer~Battlecry": DragoncladLancer,
    "SV_Fortune~Dragoncraft~Minion~2~2~2~None~Springwell Dragon Keeper~Battlecry~Enhance": SpringwellDragonKeeper,
    "SV_Fortune~Dragoncraft~Minion~2~2~2~None~Tropical Grouper~Battlecry~Enhance": TropicalGrouper,
    "SV_Fortune~Dragoncraft~Minion~2~2~2~None~Wavecrest Angler~Battlecry": WavecrestAngler,
    "SV_Fortune~Dragoncraft~Spell~2~Draconic Call": DraconicCall,
    "SV_Fortune~Dragoncraft~Minion~1~1~2~None~Ivory Dragon~Battlecry": IvoryDragon,
    "SV_Fortune~Dragoncraft~Minion~3~1~5~None~Heliodragon": Heliodragon,
    "SV_Fortune~Dragoncraft~Minion~3~2~8~None~Slaughtering Dragonewt~Bane~Battlecry": SlaughteringDragonewt,
    "SV_Fortune~Dragoncraft~Minion~5~4~4~None~Crimson Dragon's Sorrow~Taunt~Battlecry~Legendary~Uncollectible": CrimsonDragonsSorrow,
    "SV_Fortune~Dragoncraft~Minion~7~4~4~None~Azure Dragon's Rage~Charge~Legendary~Uncollectible": AzureDragonsRage,
    "SV_Fortune~Dragoncraft~Minion~3~2~3~None~Turncoat Dragon Summoner~Battlecry~Legendary": TurncoatDragonSummoner,
    "SV_Fortune~Dragoncraft~Amulet~1~None~Dragon's Nest": DragonsNest,
    "SV_Fortune~Dragoncraft~Spell~3~Dragon Spawning": DragonSpawning,
    "SV_Fortune~Dragoncraft~Spell~4~Dragon Impact": DragonImpact,
    "SV_Fortune~Dragoncraft~Minion~10~11~8~None~XI. Erntz, Justice~Taunt~Legendary": XIErntzJustice,

    "SV_Fortune~Shadowcraft~Minion~2~2~2~None~Ghostly Maid~Battlecry": GhostlyMaid,
    "SV_Fortune~Shadowcraft~Minion~2~2~2~None~Bonenanza Necromancer~Enhance~Battlecry": BonenanzaNecromancer,
    "SV_Fortune~Shadowcraft~Spell~2~Savoring Slash": SavoringSlash,
    "SV_Fortune~Shadowcraft~Amulet~2~None~Coffin of the Unknown Soul~Countdown~Battlecry~Deathrattle": CoffinoftheUnknownSoul,
    "SV_Fortune~Shadowcraft~Minion~3~3~3~None~Spirit Curator~Battlecry": SpiritCurator,
    "SV_Fortune~Shadowcraft~Amulet~1~None~Death Fowl~Countdown~Crystallize~Deathrattle~Uncollectible": DeathFowl_Crystallize,
    "SV_Fortune~Shadowcraft~Minion~4~3~3~None~Death Fowl~Crystallize~Deathrattle": DeathFowl,
    "SV_Fortune~Shadowcraft~Minion~2~2~2~None~Soul Box~Battlecry": SoulBox,
    "SV_Fortune~Shadowcraft~Minion~5~4~4~None~VI. Milteo, The Lovers~Battlecry~Enhance~Deathrattle~Legendary": VIMilteoTheLovers,
    "SV_Fortune~Shadowcraft~Amulet~2~None~Cloistered Sacristan~Countdown~Crystallize~Deathrattle~Uncollectible": CloisteredSacristan_Crystallize,
    "SV_Fortune~Shadowcraft~Minion~6~5~5~None~Cloistered Sacristan~Taunt~Crystallize": CloisteredSacristan,
    "SV_Fortune~Shadowcraft~Minion~8~6~6~None~Conquering Dreadlord~Invocation~Legendary": ConqueringDreadlord,
    "SV_Fortune~Shadowcraft~Amulet~2~None~Deathbringer~Countdown~Crystallize~Battlecry~Deathrattle~Uncollectible": Deathbringer_Crystallize,
    "SV_Fortune~Shadowcraft~Minion~9~7~7~None~Deathbringer~Crystallize": Deathbringer,

    "SV_Fortune~Bloodcraft~Minion~1~1~2~None~Silverbolt Hunter~Battlecry~Deathrattle": SilverboltHunter,
    "SV_Fortune~Bloodcraft~Minion~2~1~3~None~Moonrise Werewolf~Battlecry~Enhance": MoonriseWerewolf,
    "SV_Fortune~Bloodcraft~Minion~2~2~2~None~Whiplash Imp~Battlecry~Enhance": WhiplashImp,
    "SV_Fortune~Bloodcraft~Minion~2~2~2~None~Contemptous Demon~Battlecry": ContemptousDemon,
    "SV_Fortune~Bloodcraft~Spell~2~Dark Summons": DarkSummons,
    "SV_Fortune~Bloodcraft~Minion~3~3~3~None~Tyrant of Mayhem~Battlecry": TyrantofMayhem,
    "SV_Fortune~Bloodcraft~Minion~4~4~4~None~Curmudgeon Ogre~Battlecry~Enhance": CurmudgeonOgre,
    "SV_Fortune~Bloodcraft~Amulet~3~None~Dire Bond": DireBond,
    "SV_Fortune~Bloodcraft~Minion~4~4~3~None~Darhold, Abyssal Contract~Battlecry~Legendary": DarholdAbyssalContract,
    "SV_Fortune~Bloodcraft~Spell~5~Burning Constriction": BurningConstriction,
    "SV_Fortune~Bloodcraft~Spell~1~Vampire of Calamity~Accelerate~Uncollectible": VampireofCalamity_Accelerate,
    "SV_Fortune~Bloodcraft~Minion~7~7~7~None~Vampire of Calamity~Rush~Battlecry~Accelerate": VampireofCalamity,
    "SV_Fortune~Bloodcraft~Amulet~3~None~Unselfish Grace~Uncollectible~Legendary": UnselfishGrace,
    "SV_Fortune~Bloodcraft~Spell~1~Insatiable Desire~Uncollectible~Legendary": InsatiableDesire,
    "SV_Fortune~Bloodcraft~Spell~0~XIV. Luzen, Temperance~Accelerate~Uncollectible~Legendary": XIVLuzenTemperance_Accelerate,
    "SV_Fortune~Bloodcraft~Minion~4~4~4~None~XIV. Luzen, Temperance~Uncollectible~Legendary": XIVLuzenTemperance_Token,
    "SV_Fortune~Bloodcraft~Minion~9~7~7~None~XIV. Luzen, Temperance~Accelerate~Legendary": XIVLuzenTemperance,

    "SV_Fortune~Neutral~Minion~5~3~5~None~Archangel of Evocation~Taunt~Battlecry": ArchangelofEvocation,
    "SV_Fortune~Forestcraft~Minion~3~1~5~None~Aerin, Forever Brilliant~Legendary": AerinForeverBrilliant,
    "SV_Fortune~Forestcraft~Minion~4~3~4~None~Furious Mountain Deity~Enhance~Battlecry": FuriousMountainDeity,
    "SV_Fortune~Forestcraft~Minion~8~8~8~None~Deepwood Anomaly~Battlecry~Legendary": DeepwoodAnomaly,
    "SV_Fortune~Forestcraft~Spell~3~Life Banquet": LifeBanquet,
    "SV_Fortune~Swordcraft~Minion~2~2~2~Officer~Ilmisuna, Discord Hawker~Battlecry": IlmisunaDiscordHawker,
    "SV_Fortune~Swordcraft~Minion~4~4~4~Commander~Alyaska, War Hawker~Legendary": AlyaskaWarHawker,
    "SV_Fortune~Swordcraft~Minion~8~6~6~Commander~Exterminus Weapon~Battlecry~Deathrattle~Uncollectible~Legendary": ExterminusWeapon,
    "SV_Fortune~Runecraft~Minion~2~1~2~None~Runie, Resolute Diviner~Spellboost~Battlecry~Legendary": RunieResoluteDiviner,
    "SV_Fortune~Runecraft~Spell~2~Alchemical Craftschief~Accelerate~Uncollectible": AlchemicalCraftschief_Accelerate,
    "SV_Fortune~Runecraft~Minion~7~4~4~None~Alchemical Craftschief~Taunt~Battlecry~Uncollectible": AlchemicalCraftschief_Token,
    "SV_Fortune~Runecraft~Minion~8~4~4~None~Alchemical Craftschief~Taunt~Battlecry~Accelerate": AlchemicalCraftschief,
    "SV_Fortune~Dragoncraft~Spell~2~Whitefrost Whisper~Uncollectible~Legendary": WhitefrostWhisper,
    "SV_Fortune~Dragoncraft~Minion~3~1~3~None~Filene, Absolute Zero~Battlecry~Legendary": FileneAbsoluteZero,
    "SV_Fortune~Dragoncraft~Minion~6~5~7~None~Eternal Whale~Taunt": EternalWhale,
    "SV_Fortune~Dragoncraft~Minion~1~5~7~None~Eternal Whale~Taunt~Uncollectible": EternalWhale_Token,
    "SV_Fortune~Shadowcraft~Spell~2~Forced Resurrection": ForcedResurrection,
    "SV_Fortune~Shadowcraft~Minion~6~5~5~None~Nephthys, Goddess of Amenta~Battlecry~Enhance~Legendary": NephthysGoddessofAmenta,
    "SV_Fortune~Bloodcraft~Spell~1~Nightscreech": Nightscreech,
    "SV_Fortune~Bloodcraft~Minion~3~3~3~None~Baal~Battlecry~Fusion~Legendary": Baal,
}
