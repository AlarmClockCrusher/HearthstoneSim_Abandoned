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
    index = "SV_Fortune~Neutral~Minion~4~1~1~None~Fieran, Havensent Wind God~Battlecry~Invocation~Legendary"
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
        if isinstance(target, list): target = target[0]
        return target.type == "Minion" and target.ID != self.ID and target.onBoard

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if self.Game.getEvolutionPoint(self.ID) > self.Game.getEvolutionPoint(3 - self.ID):
            self.buffDebuff(0, 2)
            PRINT(self, f"Fieran, Havensent Wind God's Fanfare gives itself +0/+2.")
            if target:
                if isinstance(target, list): target = target[0]
                PRINT(self, f"Fieran, Havensent Wind God deals 2 damage to minion {target.name}")
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
            return self.Game.minionsAlive(3 - self.ID) > 0
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
            self.entity.dealsAOE(enemies, 2)


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

    def returnTrue(self, choice=0):  # 需要targets里面没有目标，且有3个融合素材
        return not self.targets and self.fusionMaterials >= 4

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

    def returnTrue(self, choice=0):
        return not self.targets

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

    def returnTrue(self, choice=0):
        if self.willEnhance():
            return True
        return not self.targets

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
            self.dealsAOE(targets, damage)
            PRINT(self.Game, f"Decisive Strike deals {damage} damage to all enemies")
        else:
            if isinstance(target, list): target = target[0]
            PRINT(self.Game, f"Decisive Strike deals {damage} damage to minion {target.name}")
            self.dealsDamage(target, damage)
        return None


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
        PRINT(self, "Last Words: Summon a Fortress Guard.")
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
    index = "SV_Fortune~Swordcraft~Minion~3~2~2~Commander~Empress of Serenity~Battlecry"
    requireTarget, keyWord, description = False, "", "Fanfare: Summon a Shield Guardian.Enhance (5): Summon 3 instead.Enhance (10): Give +3/+3 to all allied Shield Guardians."
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
                    print(char)
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

    # TODO require target

    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.trigsBoard = [Trig_DiamondPaladin(self)]

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
            target.buffDebuff(-4, 0)
            PRINT(self, f"Diamond Paladin's Fanfare give {target.name} -4/-0.")
        return

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

    def returnTrue(self, choice=0):
        return len(self.Game.Hand_Deck.hands[self.ID]) > 0 and not self.targets

    def targetExists(self, choice=0):
        return len(self.Game.Hand_Deck.hands[self.ID]) > 0

    def targetCorrect(self, target, choice=0):
        if isinstance(target, list): target = target[0]
        return target.ID == self.ID and target.inHand and target != self

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if isinstance(target, list): target = target[0]
        n = type(target).mana
        self.Game.Hand_Deck.discardCard(self.ID, target)
        self.buffDebuff(n, n)
        PRINT(self.Game, f"Selfless Noble's Fanfare discard {target.name} and get +{n}/+{n}")


"""Runecraft cards"""

"""Dragoncraft cards"""

"""Shadowcraft cards"""

"""Bloodcraft cards"""

"""Havencraft cards"""

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

    # TODO require target

    def effectCanTrigger(self):
        self.effectViable = self.Game.Counters.numMinionsSummonedThisGame[self.ID] >= 15

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if self.Game.Counters.numMinionsSummonedThisGame[self.ID] >= 15:
            self.Game.restoreEvolvePoint(self.ID)
        return None

    def inHandEvolving(self, target=None):
        if target:
            self.dealsDamage(target, len(self.Game.minionsonBoard[self.ID]))
            PRINT(self,
                  f"Ilmisuna, Discord Hawker's Evolve deals {len(self.Game.minionsonBoard[self.ID])} damage to {target.name} -4/-0.")
        return


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


SV_Fortune_Indices = {
    "SV_Fortune~Neutral~Minion~2~5~5~None~Cloud Gigas~Taunt": CloudGigas,
    "SV_Fortune~Neutral~Spell~2~Sudden Showers": SuddenShowers,
    "SV_Fortune~Neutral~Minion~4~4~3~None~Winged Courier~Deathrattle": WingedCourier,
    "SV_Fortune~Neutral~Minion~4~1~1~None~Fieran, Havensent Wind God~Battlecry~Invocation~Legendary": FieranHavensentWindGod,
    "SV_Fortune~Natural~Spell~4~Resolve of the Fallen": ResolveoftheFallen,
    "SV_Fortune~Natural~Minion~5~3~4~None~Starbright Deity~Battlecry": StarbrightDeity,
    "SV_Fortune~Neutral~Minion~5~5~5~None~XXI. Zelgenea, The World~Battlecry~Invocation~Legendary": XXIZelgeneaTheWorld,
    "SV_Fortune~Neutral~Amulet~6~None~Titanic Showdown~Countdown~Last Words": TitanicShowdown,
    "SV_Fortune~Neutral~Spell~2~Pureshot Angel~Accelerate~Uncollectible": PureshotAngel,
    "SV_Fortune~Neutral~Minion~8~6~6~None~Pureshot Angel~Battlecry~Accelerate": PureshotAngel,

    "SV_Fortune~Forestcraft~Minion~1~1~1~None~Lumbering Carapace~Battlecry": LumberingCarapace,
    "SV_Fortune~Forestcraft~Minion~2~2~2~None~Blossoming Archer": BlossomingArcher,
    "SV_Fortune~Forestcraft~Spell~2~Soothing Spell": SoothingSpell,
    "SV_Fortune~Forestcraft~Minion~3~3~3~None~XII. Wolfraud, Hanged Man~Enhance~Battlecry~Legendary": XIIWolfraudHangedMan,
    "SV_Fortune~Forestcraft~Spell~0~Treacherous Reversal~Uncollectible": TreacherousReversal,
    "SV_Fortune~Forestcraft~Spell~1~Reclusive Ponderer~Accelerate~Uncollectible": ReclusivePonderer,
    "SV_Fortune~Forestcraft~Minion~4~3~3~None~Reclusive Ponderer~Stealth~Accelerate": ReclusivePonderer,
    "SV_Fortune~Forestcraft~Spell~1~Chipper Skipper~Accelerate~Uncollectible": ChipperSkipper,
    "SV_Fortune~Forestcraft~Minion~4~4~3~None~Chipper Skipper~Accelerate": ChipperSkipper,
    "SV_Fortune~Forestcraft~Spell~4~Fairy Assault": FairyAssault,
    "SV_Fortune~Forestcraft~Minion~5~4~5~None~Optimistic Beastmaster~Battlecry": OptimisticBeastmaster,
    "SV_Fortune~Forestcraft~Minion~6~4~4~None~Terrorformer~Battlecry~Fusion~Legendary": Terrorformer,
    "SV_Fortune~Forestcraft~Spell~1~Deepwood Wolf~Accelerate~Uncollectible": DeepwoodWolf,
    "SV_Fortune~Forestcraft~Minion~7~3~3~None~Deepwood Wolf~Charge~Accelerate": DeepwoodWolf,
    "SV_Fortune~Forestcraft~Spell~1~Lionel, Woodland Shadow~Accelerate~Uncollectible": LionelWoodlandShadow,
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

    "SV_Fortune~Neutral~Minion~5~3~5~None~Archangel of Evocation~Taunt~Battlecry": ArchangelofEvocation,
    "SV_Fortune~Forestcraft~Minion~3~1~5~None~Aerin, Forever Brilliant~Legendary": AerinForeverBrilliant,
    "SV_Fortune~Forestcraft~Minion~4~3~4~None~Furious Mountain Deity~Enhance~Battlecry": FuriousMountainDeity,
    "SV_Fortune~Forestcraft~Minion~8~8~8~None~Deepwood Anomaly~Battlecry~Legendary": DeepwoodAnomaly,
    "SV_Fortune~Forestcraft~Spell~3~Life Banquet": LifeBanquet,
    "SV_Fortune~Swordcraft~Minion~2~2~2~Officer~Ilmisuna, Discord Hawker~Battlecry": IlmisunaDiscordHawker,
    "SV_Fortune~Swordcraft~Minion~4~4~4~Commander~Alyaska, War Hawker~Legendary": AlyaskaWarHawker,
    "SV_Fortune~Swordcraft~Minion~8~6~6~Commander~Exterminus Weapon~Battlecry~Deathrattle~Uncollectible~Legendary": ExterminusWeapon,

}
