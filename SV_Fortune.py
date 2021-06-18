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


class CloudGigas(SVMinion):
    Class, race, name = "Neutral", "", "Cloud Gigas"
    mana, attack, health = 2, 5, 5
    index = "SV_Fortune~Neutral~Minion~2~5~5~~Cloud Gigas~Taunt"
    requireTarget, keyWord, description = False, "Taunt", "Ward. At the start of your turn, put a Cloud Gigas into your deck and banish this follower."
    attackAdd, healthAdd = 0, 0
    name_CN = "腾云巨灵"

    def __init__(self, Game, ID):
        super().__init__(Game, ID)
        self.trigsBoard = [Trig_CloudGigas(self)]

    def inEvolving(self):
        for t in self.trigsBoard:
            if type(t) == Trig_CloudGigas:
                t.disconnect()
                self.trigsBoard.remove(t)
                break


class Trig_CloudGigas(TrigBoard):
    def __init__(self, entity):
        super().__init__(entity, ["TurnStarts"])

    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.onBoard and ID == self.entity.ID

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        self.entity.Game.banishMinion(self.entity, self.entity)
        self.entity.Game.Hand_Deck.shuffleintoDeck([CloudGigas(self.entity.Game, self.entity.ID)], creator=self.entity)


class SuddenShowers(SVSpell):
    Class, school, name = "Neutral", "", "Sudden Showers"
    mana, requireTarget = 2, False
    index = "SV_Fortune~Neutral~Spell~2~Sudden Showers"
    description = "Destroy a random follower."
    name_CN = "突坠的落石"

    def available(self):
        return len(self.Game.minionsAlive(1)) + len(self.Game.minionsAlive(2)) > 0

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        curGame = self.Game
        if curGame.mode == 0:
            minion = None
            if curGame.guides:
                i, where = curGame.guides.pop(0)
                if where: minion = curGame.find(i, where)
            else:
                minions = curGame.minionsAlive(1) + curGame.minionsAlive(2)
                if len(minions) > 0:
                    minion = npchoice(minions)
                    curGame.fixedGuides.append((minion.pos, "Minion%d" % minion.ID))
                else:
                    curGame.fixedGuides.append((0, ""))
            if minion: curGame.killMinion(self, minion)
        return None


class WingedCourier(SVMinion):
    Class, race, name = "Neutral", "", "Winged Courier"
    mana, attack, health = 4, 4, 3
    index = "SV_Fortune~Neutral~Minion~4~4~3~~Winged Courier~Deathrattle"
    requireTarget, keyWord, description = False, "", "Last Words: Draw a card."
    attackAdd, healthAdd = 2, 2
    name_CN = "翔翼信使"

    def __init__(self, Game, ID):
        super().__init__(Game, ID)
        self.deathrattles = [Deathrattle_WingedCourier(self)]


class Deathrattle_WingedCourier(Deathrattle_Minion):
    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        self.entity.Game.Hand_Deck.drawCard(self.entity.ID)


class FieranHavensentWindGod(SVMinion):
    Class, race, name = "Neutral", "", "Fieran, Havensent Wind God"
    mana, attack, health = 4, 1, 1
    index = "SV_Fortune~Neutral~Minion~4~1~1~~Fieran, Havensent Wind God~Battlecry~Invocation~Legendary"
    requireTarget, keyWord, description = True, "", "Invocation: At the start of your turn, Rally (10) - Invoke this card.------Fanfare: If you have more evolution points than your opponent, gain +0/+2 and deal 2 damage to an enemy follower. (You have 0 evolution points on turns you are unable to evolve.)At the end of your turn, give +1/+1 to all allied followers."
    attackAdd, healthAdd = 2, 2
    name_CN = "天霸风神·斐兰"

    def __init__(self, Game, ID):
        super().__init__(Game, ID)
        self.trigsBoard = [Trig_FieranHavensentWindGod(self)]
        self.trigsDeck = [Trig_InvocationFieranHavensentWindGod(self)]

    def effCanTrig(self):
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
            if target:
                if isinstance(target, list): target = target[0]
                self.dealsDamage(target, 2)
        return None


class Trig_FieranHavensentWindGod(TrigBoard):
    def __init__(self, entity):
        super().__init__(entity, ["TurnEnds"])

    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.onBoard and ID == self.entity.ID

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        minions = self.entity.Game.minionsonBoard(self.entity.ID)
        for minion in minions:
            minion.buffDebuff(1, 1)


class Trig_InvocationFieranHavensentWindGod(TrigInvocation):
    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.inDeck and ID == self.entity.ID and self.entity.Game.space(self.entity.ID) > 0 and \
               self.entity.Game.Counters.numMinionsSummonedThisGame[self.entity.ID] >= 10


class ResolveoftheFallen(SVSpell):
    Class, school, name = "Neutral", "", "Resolve of the Fallen"
    requireTarget, mana = True, 4
    index = "SV_Fortune~Neutral~Spell~4~Resolve of the Fallen"
    description = "Destroy an enemy follower or amulet.If at least 3 allied followers have evolved this match, recover 3 play points.Then, if at least 5 have evolved, draw 2 cards."
    name_CN = "堕落的决意"

    def effCanTrig(self):
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
    Class, race, name = "Neutral", "", "Starbright Deity"
    mana, attack, health = 5, 3, 4
    index = "SV_Fortune~Neutral~Minion~5~3~4~~Starbright Deity~Battlecry"
    requireTarget, keyWord, description = False, "", "Fanfare: Put into your hand copies of the 3 left-most cards in your hand, in the order they were added."
    attackAdd, healthAdd = 2, 2
    name_CN = "星辉女神"

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        for i in range(min(3, len(self.Game.Hand_Deck.hands[self.ID]))):
            card = self.Game.Hand_Deck.hands[self.ID][i]
            self.Game.Hand_Deck.addCardtoHand([type(card)], self.ID, byType=True)
        return None


class XXIZelgeneaTheWorld(SVMinion):
    Class, race, name = "Neutral", "", "XXI. Zelgenea, The World"
    mana, attack, health = 6, 5, 5
    index = "SV_Fortune~Neutral~Minion~5~5~5~~XXI. Zelgenea, The World~Battlecry~Invocation~Legendary"
    requireTarget, keyWord, description = False, "", "Invocation: At the start of your tenth turn, invoke this card. Then, evolve it.----------Fanfare: Restore 5 defense to your leader. If your leader had 14 defense or less before defense was restored, draw 2 cards and randomly destroy 1 of the enemy followers with the highest attack in play.Can't be evolved using evolution points. (Can be evolved using card effects.)"
    attackAdd, healthAdd = 2, 2
    name_CN = "《世界》·捷尔加内亚"

    def __init__(self, Game, ID):
        super().__init__(Game, ID)
        self.marks["Can't Evolve"] = 1
        self.trigsDeck = [Trig_InvocationXXIZelgeneaTheWorld(self)]

    def effCanTrig(self):
        self.effectViable = self.Game.heroes[self.ID].health < 15

    def afterInvocation(self, signal, ID, subject, target, number, comment):
        self.evolve()

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if self.Game.heroes[self.ID].health < 15:
            self.restoresHealth(self.Game.heroes[self.ID], 5)
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
            self.Game.Hand_Deck.drawCard(self.ID)
            self.Game.Hand_Deck.drawCard(self.ID)
        else:
            self.restoresHealth(self.Game.heroes[self.ID], 5)
        return None

    def inEvolving(self):
        trigger = Trig_AttackXXIZelgeneaTheWorld(self)
        self.trigsBoard.append(trigger)
        trigger.connect()


class Trig_AttackXXIZelgeneaTheWorld(TrigBoard):
    def __init__(self, entity):
        super().__init__(entity, ["MinionAttackingHero", "MinionAttackingMinion"])

    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
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
        super().__init__(entity, ["TurnEnds"])

    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.onBoard and ID == self.entity.ID

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        targets = [self.entity.Game.heroes[1], self.entity.Game.heroes[2]] + self.entity.Game.minionsonBoard(1) \
                  + self.entity.Game.minionsonBoard(2)
        self.entity.dealsAOE(targets, [4 for obj in targets])


class Trig_InvocationXXIZelgeneaTheWorld(TrigInvocation):
    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.inDeck and ID == self.entity.ID and self.entity.Game.space(self.entity.ID) > 0 and \
               self.entity.Game.Counters.turns[self.entity.ID] == 10


class TitanicShowdown(Amulet):
    Class, race, name = "Neutral", "", "Titanic Showdown"
    mana = 6
    index = "SV_Fortune~Neutral~Amulet~6~~Titanic Showdown~Countdown~Deathrattle"
    requireTarget, description = False, "Countdown (2) Fanfare: Put a random follower that originally costs at least 9 play points from your deck into your hand. If any other allied Titanic Showdowns are in play, recover 4 play points and banish this amulet. Last Words: At the start of your next turn, put 5 random followers that originally cost at least 9 play points from your hand into play."
    name_CN = "巨人的较劲"

    def __init__(self, Game, ID):
        super().__init__(Game, ID)
        self.counter = 2
        self.trigsBoard = [Trig_Countdown(self)]
        self.deathrattles = [Deathrattle_TitanicShowdown(self)]

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        curGame = self.Game
        if curGame.mode == 0:
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
        super().__init__(entity, ["TurnStarts"])

    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.onBoard and ID == self.entity.ID

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
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
            if i > -1: curGame.summonfrom(i, ID, -1, self.entity)
        for t in self.entity.trigsBoard:
            if type(t) == Trig_TitanicShowdown:
                t.disconnect()
                self.entity.trigsBoard.remove(t)
                break


class PureshotAngel_Accelerate(SVSpell):
    Class, school, name = "Neutral", "", "Pureshot Angel"
    requireTarget, mana = False, 2
    index = "SV_Fortune~Neutral~Spell~2~Pureshot Angel~Accelerate~Uncollectible"
    description = "Deal 3 damage to an enemy"
    name_CN = "圣贯天使"

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        curGame = self.Game
        if curGame.mode == 0:
            if curGame.guides:
                i = curGame.guides.pop(0)
            else:
                minions = curGame.minionsAlive(3 - self.ID)
                i = npchoice(minions).pos if minions else -1
                curGame.fixedGuides.append(i)
            if i > -1:
                damage = (3 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
                self.dealsDamage(curGame.minions[3 - self.ID][i], damage)
        return None


class PureshotAngel(SVMinion):
    Class, race, name = "Neutral", "", "Pureshot Angel"
    mana, attack, health = 8, 6, 6
    index = "SV_Fortune~Neutral~Minion~8~6~6~~Pureshot Angel~Battlecry~Accelerate"
    requireTarget, keyWord, description = False, "", "Accelerate 2: Deal 1 damage to an enemy. Fanfare: xxx. Deal 3 damage to an enemy minion, and deal 1 damage to the enemy hero"
    accelerateSpell = PureshotAngel_Accelerate
    attackAdd, healthAdd = 2, 2
    name_CN = "圣贯天使"

    def getMana(self):
        if self.Game.Manas.manas[self.ID] < self.mana:
            return 2
        else:
            return self.mana

    def willAccelerate(self):
        curMana = self.Game.Manas.manas[self.ID]
        return self.mana > curMana >= 2

    def effCanTrig(self):
        if self.willAccelerate() and self.targetExists():
            self.effectViable = "sky blue"
        else:
            self.effectViable = False

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
                i = npchoice(minions).pos if minions else -1
                curGame.fixedGuides.append(i)
            if i > -1:
                self.dealsDamage(curGame.minions[3 - self.ID][i], 3)
        self.dealsDamage(self.Game.heroes[3 - self.ID], 3)
        return None


"""Forestcraft cards"""


class LumberingCarapace(SVMinion):
    Class, race, name = "Forestcraft", "", "Lumbering Carapace"
    mana, attack, health = 1, 1, 1
    index = "SV_Fortune~Forestcraft~Minion~1~1~1~~Lumbering Carapace~Battlecry"
    requireTarget, keyWord, description = False, "", "Fanfare: If at least 2 other cards were played this turn, gain +2/+2. Then, if at least 4 other cards were played this turn, gain +2/+2 more and Ward."
    attackAdd, healthAdd = 2, 2
    name_CN = "碎击巨虫"

    def effCanTrig(self):
        self.effectViable = self.Game.combCards(self.ID) >= 2

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        numCardsPlayed = self.Game.combCards(self.ID)
        if numCardsPlayed >= 2:
            self.buffDebuff(2, 2)
            if numCardsPlayed >= 4:
                self.buffDebuff(2, 2)
                self.getsStatus("Taunt")
        return None


class BlossomingArcher(SVMinion):
    Class, race, name = "Forestcraft", "", "Blossoming Archer"
    mana, attack, health = 2, 2, 2
    index = "SV_Fortune~Forestcraft~Minion~2~2~2~~Blossoming Archer"
    requireTarget, keyWord, description = False, "", "Whenever you play a card using its Accelerate effect, deal 2 damage to a random enemy follower."
    attackAdd, healthAdd = 2, 2
    name_CN = "花绽弓箭手"

    def __init__(self, Game, ID):
        super().__init__(Game, ID)
        self.trigsBoard = [Trig_BlossomingArcher(self)]


class Trig_BlossomingArcher(TrigBoard):
    def __init__(self, entity):
        super().__init__(entity, ["AccelerateBeenPlayed"])

    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
        return subject.ID == self.entity.ID and self.entity.onBoard

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
                    curGame.fixedGuides.append((enemy.pos, enemy.type + str(enemy.ID)))
                else:
                    curGame.fixedGuides.append((0, ''))
            if enemy:
                self.entity.dealsDamage(enemy, 2)


class SoothingSpell(SVSpell):
    Class, school, name = "Forestcraft", "", "Soothing Spell"
    requireTarget, mana = True, 2
    index = "SV_Fortune~Forestcraft~Spell~2~Soothing Spell"
    description = "Restore 3 defense to an ally. If at least 2 other cards were played this turn, recover 1 evolution point."
    name_CN = "治愈的波动"

    def effCanTrig(self):
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
            if self.Game.combCards(self.ID) >= 2:
                self.Game.restoreEvolvePoint(self.ID)
        return target


class XIIWolfraudHangedMan(SVMinion):
    Class, race, name = "Forestcraft", "", "XII. Wolfraud, Hanged Man"
    mana, attack, health = 3, 3, 3
    index = "SV_Fortune~Forestcraft~Minion~3~3~3~~XII. Wolfraud, Hanged Man~Enhance~Battlecry~Legendary"
    requireTarget, keyWord, description = False, "", "Fanfare: Enhance (7) - Put a Treacherous Reversal into your hand and banish this follower. Can't be destroyed by effects. (Can be destroyed by damage from effects.)"
    attackAdd, healthAdd = 2, 2
    name_CN = "《倒吊人》·罗弗拉德"

    def __init__(self, Game, ID):
        super().__init__(Game, ID)
        self.marks["Can't Break"] = 1

    def inHandEvolving(self, target=None):
        if self.Game.combCards(self.ID) >= 3:
            self.buffDebuff(3, 3)

    def getMana(self):
        if self.Game.Manas.manas[self.ID] >= 7:
            return 7
        else:
            return self.mana

    def willEnhance(self):
        return self.Game.Manas.manas[self.ID] >= 7

    def effCanTrig(self):
        self.effectViable = self.willEnhance()

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if comment == 7:
            self.Game.banishMinion(self, self)
            self.Game.Hand_Deck.addCardtoHand([TreacherousReversal], self.ID, byType=True)
        return target


class TreacherousReversal(SVSpell):
    Class, school, name = "Forestcraft", "", "Treacherous Reversal"
    requireTarget, mana = False, 0
    index = "SV_Fortune~Forestcraft~Spell~0~Treacherous Reversal~Uncollectible"
    description = "Banish all cards in play.Banish all cards in your hand and deck.Put copies of the first 10 cards your opponent played this match (excluding XII. Wolfraud, Hanged Man and Treacherous Reversal) into your deck, in the order they were played.Transform the Reaper at the bottom of your deck into a Victory Card.Treat allied cards that have been destroyed this match as if they were banished.At the end of your opponent's next turn, put copies of each card in your opponent's hand into your hand (excluding XII. Wolfraud, Hanged Man and Treacherous Reversal)."
    name_CN = "真伪逆转"

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        self.Game.banishMinion(self, self.Game.minionsandAmuletsonBoard(1) + self.Game.minionsandAmuletsonBoard(2))
        self.Game.Hand_Deck.extractfromHand(None, self.ID, all=True)
        self.Game.Hand_Deck.extractfromDeck(None, self.ID, all=True)
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
            self.Game.Hand_Deck.shuffleintoDeck([c(self.Game, self.ID)], creator=self)
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
        super().__init__(entity, ["TurnEnds"])

    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.onBoard and ID == self.entity.ID

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        cards = []
        for card in self.entity.Game.Hand_Deck.hands[self.entity.ID]:
            if card.name not in ["Treacherous Reversal", "XII. Wolfraud, Hanged Man"]:
                cards.append(card)
        for c in cards:
            self.entity.Game.Hand_Deck.addCardtoHand([type(c)], 3 - self.entity.ID, byType=True)
        for t in self.entity.trigsBoard:
            if type(t) == Trig_TreacherousReversal:
                t.disconnect()
                self.entity.trigsBoard.remove(t)
                break


class ReclusivePonderer_Accelerate(SVSpell):
    Class, school, name = "Forestcraft", "", "Reclusive Ponderer"
    requireTarget, mana = False, 1
    index = "SV_Fortune~Forestcraft~Spell~1~Reclusive Ponderer~Accelerate~Uncollectible"
    description = "Draw a card."
    name_CN = "深谋的兽人"

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        self.Game.Hand_Deck.drawCard(self.ID)
        return None


class ReclusivePonderer(SVMinion):
    Class, race, name = "Forestcraft", "", "Reclusive Ponderer"
    mana, attack, health = 4, 3, 3
    index = "SV_Fortune~Forestcraft~Minion~4~3~3~~Reclusive Ponderer~Stealth~Accelerate"
    requireTarget, keyWord, description = False, "Stealth", "Accelerate (1): Draw a card. Ambush."
    accelerateSpell = ReclusivePonderer_Accelerate
    attackAdd, healthAdd = 2, 2
    name_CN = "深谋的兽人"

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


class ChipperSkipper_Accelerate(SVSpell):
    Class, school, name = "Forestcraft", "", "Chipper Skipper"
    requireTarget, mana = False, 1
    index = "SV_Fortune~Forestcraft~Spell~1~Chipper Skipper~Accelerate~Uncollectible"
    description = "Summon a Fighter"
    name_CN = "船娘精灵"

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        self.Game.summon([Fighter(self.Game, self.ID)], (-1, "totheRightEnd"),
                         self)
        return None


class ChipperSkipper(SVMinion):
    Class, race, name = "Forestcraft", "", "Chipper Skipper"
    mana, attack, health = 4, 4, 3
    index = "SV_Fortune~Forestcraft~Minion~4~4~3~~Chipper Skipper~Accelerate"
    requireTarget, keyWord, description = False, "", "Accelerate (1): Summon a Fighter.(Can only Accelerate if a follower was played this turn.)Whenever you play a card using its Accelerate effect, summon a Fighter and evolve it."
    accelerateSpell = ChipperSkipper_Accelerate
    attackAdd, healthAdd = 2, 2
    name_CN = "船娘精灵"

    def __init__(self, Game, ID):
        super().__init__(Game, ID)
        self.trigsBoard = [Trig_ChipperSkipper(self)]

    def getMana(self):
        if self.Game.Manas.manas[self.ID] < self.mana and self.Game.Counters.numMinionsPlayedThisTurn[self.ID] > 0:
            return 1
        else:
            return self.mana

    def willAccelerate(self):
        curMana = self.Game.Manas.manas[self.ID]
        return self.mana > curMana >= 1 and self.Game.Counters.numMinionsPlayedThisTurn[self.ID] > 0

    def effCanTrig(self):
        if self.willAccelerate() and self.targetExists():
            self.effectViable = "sky blue"
        else:
            self.effectViable = False


class Trig_ChipperSkipper(TrigBoard):
    def __init__(self, entity):
        super().__init__(entity, ["AccelerateBeenPlayed"])

    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
        return subject.ID == self.entity.ID and self.entity.onBoard

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        fighter = Fighter(self.entity.Game, self.entity.ID)
        self.entity.Game.summon([fighter], (-1, "totheRightEnd"),
                                self.entity)
        fighter.evolve()


class FairyAssault(SVSpell):
    Class, school, name = "Forestcraft", "", "Fairy Assault"
    requireTarget, mana = False, 4
    index = "SV_Fortune~Forestcraft~Spell~4~Fairy Assault"
    description = "Summon 4 Fairies and give them Rush. Enhance (8): Evolve them instead."
    name_CN = "妖精突击"

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
        minions = [Fairy(self.Game, self.ID) for i in range(4)]
        self.Game.summon(minions, (-1, "totheRightEnd"), self)
        if comment == 8:
            for minion in minions:
                if minion.onBoard:
                    minion.evolve()
        else:
            for minion in minions:
                if minion.onBoard:
                    minion.getsStatus("Rush")
        return None


class OptimisticBeastmaster(SVMinion):
    Class, race, name = "Forestcraft", "", "Optimistic Beastmaster"
    mana, attack, health = 5, 4, 5
    index = "SV_Fortune~Forestcraft~Minion~5~4~5~~Optimistic Beastmaster~Battlecry"
    requireTarget, keyWord, description = False, "", "Fanfare: Put a random follower with Accelerate from your deck into your hand. Whenever you play a card using its Accelerate effect, deal 2 damage to all enemies."
    attackAdd, healthAdd = 2, 2
    name_CN = "赞誉之驭兽使"

    def __init__(self, Game, ID):
        super().__init__(Game, ID)
        self.trigsBoard = [Trig_OptimisticBeastmaster(self)]

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        curGame = self.Game
        if curGame.mode == 0:
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
        super().__init__(entity, ["AccelerateBeenPlayed"])

    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
        return subject.ID == self.entity.ID and self.entity.onBoard

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        enemies = self.entity.Game.minionsonBoard(3 - self.entity.ID) + self.entity.Game.heroes[3 - self.entity.ID]
        self.entity.dealsAOE(enemies, [2 for obj in enemies])


class Terrorformer(SVMinion):
    Class, race, name = "Forestcraft", "", "Terrorformer"
    mana, attack, health = 6, 4, 4
    index = "SV_Fortune~Forestcraft~Minion~6~4~4~~Terrorformer~Battlecry~Fusion~Legendary"
    requireTarget, keyWord, description = True, "", "Fusion: Forestcraft followers that originally cost 2 play points or more. Whenever 2 or more cards are fused to this card at once, gain +2/+0 and draw a card. Fanfare: If at least 2 cards are fused to this card, gain Storm. Then, if at least 4 cards are fused to this card, destroy an enemy follower."
    attackAdd, healthAdd = 2, 2
    name_CN = "裂地异种"

    def __init__(self, Game, ID):
        super().__init__(Game, ID)
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

    def effCanTrig(self):
        self.effectViable = self.fusionMaterials >= 2

    def fusionDecided(self, objs):
        if objs:
            self.fusionMaterials += len(objs)
            self.Game.Hand_Deck.extractfromHand(self, enemyCanSee=True)
            for obj in objs: self.Game.Hand_Deck.extractfromHand(obj, enemyCanSee=True)
            self.Game.Hand_Deck.addCardtoHand(self, self.ID)
            if len(objs) >= 2:
                self.buffDebuff(2, 0)
                self.Game.Hand_Deck.drawCard(self.ID)
            self.fusion = 0  # 一张卡每回合只有一次融合机会

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if self.fusionMaterials >= 2:
            self.getsStatus("Charge")
            if self.fusionMaterials > 4 and target:
                if isinstance(target, list): target = target[0]
                self.Game.killMinion(self, target)
        return target


class DeepwoodWolf_Accelerate(SVSpell):
    Class, school, name = "Forestcraft", "", "Deepwood Wolf"
    requireTarget, mana = True, 1
    index = "SV_Fortune~Forestcraft~Spell~1~Deepwood Wolf~Accelerate~Uncollectible"
    description = "Return an allied follower or amulet to your hand. Draw a card."
    name_CN = "森林之狼"

    def targetCorrect(self, target, choice=0):
        if isinstance(target, list): target = target[0]
        return target.type in ["Minion", "Amulet"] and target.ID == self.ID and target.onBoard

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if target:
            if isinstance(target, list): target = target[0]
            self.Game.returnMiniontoHand(target, deathrattlesStayArmed=False)
            self.Game.Hand_Deck.drawCard(self.ID)
        return target


class DeepwoodWolf(SVMinion):
    Class, race, name = "Forestcraft", "", "Deepwood Wolf"
    mana, attack, health = 7, 3, 3
    index = "SV_Fortune~Forestcraft~Minion~7~3~3~~Deepwood Wolf~Charge~Accelerate"
    requireTarget, keyWord, description = True, "Charge", "Accelerate (1): Return an allied follower or amulet to your hand. Draw a card. Storm. When you play a card using its Accelerate effect, evolve this follower."
    accelerateSpell = DeepwoodWolf_Accelerate
    attackAdd, healthAdd = 3, 3
    name_CN = "森林之狼"

    def __init__(self, Game, ID):
        super().__init__(Game, ID)
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

    def effCanTrig(self):
        if self.willAccelerate() and self.targetExists():
            self.effectViable = "sky blue"
        else:
            self.effectViable = False

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
        super().__init__(entity, ["AccelerateBeenPlayed"])

    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
        return subject.ID == self.entity.ID and self.entity.onBoard

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        self.entity.evolve()


class LionelWoodlandShadow_Accelerate(SVSpell):
    Class, school, name = "Forestcraft", "", "Lionel, Woodland Shadow"
    requireTarget, mana = True, 1
    index = "SV_Fortune~Forestcraft~Spell~1~Lionel, Woodland Shadow~Accelerate~Uncollectible"
    description = "Deal 5 damage to an enemy"
    name_CN = "森之暗念·莱昂内尔"

    def targetCorrect(self, target, choice=0):
        if isinstance(target, list): target = target[0]
        return target.type == "Minion" and target.ID != self.ID and target.onBoard

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if target:
            if isinstance(target, list): target = target[0]
            damage = (5 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
            self.dealsDamage(target, damage)
        return target


class LionelWoodlandShadow(SVMinion):
    Class, race, name = "Forestcraft", "", "Lionel, Woodland Shadow"
    mana, attack, health = 7, 5, 6
    index = "SV_Fortune~Forestcraft~Minion~7~5~6~~Lionel, Woodland Shadow~Battlecry~Accelerate"
    requireTarget, keyWord, description = True, "", "Accelerate 2: Deal 1 damage to an enemy. Fanfare: xxx. Deal 3 damage to an enemy minion, and deal 1 damage to the enemy hero"
    accelerateSpell = LionelWoodlandShadow_Accelerate
    attackAdd, healthAdd = 2, 2
    name_CN = "森之暗念·莱昂内尔"

    def __init__(self, Game, ID):
        super().__init__(Game, ID)
        self.trigsBoard = [Trig_LionelWoodlandShadow(self)]

    def getMana(self):
        if self.Game.Manas.manas[self.ID] < self.mana and self.Game.Counters.evolvedThisTurn[self.ID] > 0:
            return 1
        else:
            return self.mana

    def willAccelerate(self):
        curMana = self.Game.Manas.manas[self.ID]
        return self.mana > curMana >= 1 and self.Game.Counters.evolvedThisTurn[self.ID] > 0

    def effCanTrig(self):
        if self.willAccelerate() and self.targetExists():
            self.effectViable = "sky blue"
        else:
            self.effectViable = False

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
            self.dealsDamage(target, 5)
            if health <= 5:
                self.evolve()
        return target

    def inEvolving(self):
        trigger = Trig_LionelWoodlandShadow(self)
        self.trigsBoard.append(trigger)
        trigger.connect()


class Trig_LionelWoodlandShadow(TrigBoard):
    def __init__(self, entity):
        super().__init__(entity, ["MinionPlayed"])

    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.onBoard and subject.ID != self.entity.ID

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
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
        super().__init__(entity, ["TurnEnds"])

    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
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
    name_CN = "武器商人·艾尔涅丝塔"

    def effCanTrig(self):
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
    name_CN = "恐惧猎犬"

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
                    curGame.fixedGuides.append((minion.pos, minion.type + str(minion.ID)))
                else:
                    curGame.fixedGuides.append((0, ''))
            if minion:
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
                    curGame.fixedGuides.append((enemy.pos, enemy.type + str(enemy.ID)))
                else:
                    curGame.fixedGuides.append((0, ''))
            if enemy:
                self.entity.dealsDamage(enemy, 4)


class PompousSummons(SVSpell):
    Class, school, name = "Swordcraft", "", "Pompous Summons"
    requireTarget, mana = False, 1
    index = "SV_Fortune~Swordcraft~Spell~1~Pompous Summons"
    description = "Put a random Swordcraft follower from your deck into your hand.Rally (10): Put 2 random Swordcraft followers into your hand instead."
    name_CN = "任性的差遣"

    def effCanTrig(self):
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
        return None


class DecisiveStrike(SVSpell):
    Class, school, name = "Swordcraft", "", "Decisive Strike"
    requireTarget, mana = True, 1
    index = "SV_Fortune~Swordcraft~Spell~1~Decisive Strike~Enhance"
    description = "Deal X damage to an enemy follower. X equals the attack of the highest-attack Commander follower in your hand.Enhance (5): Deal X damage to all enemy followers instead."
    name_CN = "所向披靡"

    def getMana(self):
        if self.Game.Manas.manas[self.ID] >= 5:
            return 5
        else:
            return self.mana

    def willEnhance(self):
        return self.Game.Manas.manas[self.ID] >= 5

    def effCanTrig(self):
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
        else:
            if target:
                if isinstance(target, list): target = target[0]
                self.dealsDamage(target, damage)
        return target


class HonorableThief(SVMinion):
    Class, race, name = "Swordcraft", "Officer", "Honorable Thief"
    mana, attack, health = 2, 2, 1
    index = "SV_Fortune~Swordcraft~Minion~2~2~1~Officer~Honorable Thief~Battlecry~Deathrattle"
    requireTarget, keyWord, description = False, "", "Fanfare: Rally (7) - Evolve this follower. Last Words: Put a Gilded Boots into your hand."
    attackAdd, healthAdd = 2, 2
    name_CN = "诚实的盗贼"

    def __init__(self, Game, ID):
        super().__init__(Game, ID)
        self.deathrattles = [Deathrattle_HonorableThief(self)]

    def effCanTrig(self):
        self.effectViable = self.Game.Counters.numMinionsSummonedThisGame[self.ID] >= 7

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if self.Game.Counters.numMinionsSummonedThisGame[self.ID] >= 7:
            self.evolve()
        return None


class Deathrattle_HonorableThief(Deathrattle_Minion):
    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        self.entity.Game.Hand_Deck.addCardtoHand(GildedBoots, self.entity.ID, byType=True)


class ShieldPhalanx(SVSpell):
    Class, school, name = "Swordcraft", "", "Shield Phalanx"
    requireTarget, mana = False, 2
    index = "SV_Fortune~Swordcraft~Spell~2~Shield Phalanx"
    description = "Summon a Shield Guardian and Knight.Rally (15): Summon a Frontguard General instead of a Shield Guardian."
    name_CN = "坚盾战阵"

    def effCanTrig(self):
        self.effectViable = self.Game.Counters.numMinionsSummonedThisGame[self.ID] >= 15

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if self.Game.Counters.numMinionsSummonedThisGame[self.ID] >= 15:
            self.Game.summon([FrontguardGeneral(self.Game, self.ID), Knight(self.Game, self.ID)],
                             (-1, "totheRightEnd"), self)
        else:
            self.Game.summon([ShieldGuardian(self.Game, self.ID), Knight(self.Game, self.ID)],
                             (-1, "totheRightEnd"), self)
        return None


class FrontguardGeneral(SVMinion):
    Class, race, name = "Swordcraft", "Commander", "Frontguard General"
    mana, attack, health = 7, 5, 6
    index = "SV_Fortune~Swordcraft~Minion~7~5~6~Commander~Frontguard General~Taunt~Deathrattle"
    requireTarget, keyWord, description = False, "Taunt", "Ward.Last Words: Summon a Fortress Guard."
    attackAdd, healthAdd = 2, 2
    name_CN = "铁卫战将"

    def __init__(self, Game, ID):
        super().__init__(Game, ID)
        self.deathrattles = [Deathrattle_FrontguardGeneral(self)]


class Deathrattle_FrontguardGeneral(Deathrattle_Minion):
    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        self.entity.Game.summon([FortressGuard(self.entity.Game, self.entity.ID)], (-1, "totheRightEnd"),
                                self.entity)


class FortressGuard(SVMinion):
    Class, race, name = "Swordcraft", "Officer", "Fortress Guard"
    mana, attack, health = 3, 2, 3
    index = "SV_Fortune~Swordcraft~Minion~3~2~3~Officer~Fortress Guard~Taunt~Uncollectible"
    requireTarget, keyWord, description = False, "Taunt", "Ward"
    attackAdd, healthAdd = 2, 2
    name_CN = "神盾卫士"


class EmpressofSerenity(SVMinion):
    Class, race, name = "Swordcraft", "Commander", "Empress of Serenity"
    mana, attack, health = 3, 2, 2
    index = "SV_Fortune~Swordcraft~Minion~3~2~2~Commander~Empress of Serenity~Battlecry~Enhance"
    requireTarget, keyWord, description = False, "", "Fanfare: Summon a Shield Guardian.Enhance (5): Summon 3 instead.Enhance (10): Give +3/+3 to all allied Shield Guardians."
    attackAdd, healthAdd = 2, 2
    name_CN = "安宁的女王"

    def getMana(self):
        if self.Game.Manas.manas[self.ID] >= 10:
            return 10
        elif self.Game.Manas.manas[self.ID] >= 5:
            return 5
        else:
            return self.mana

    def willEnhance(self):
        return self.Game.Manas.manas[self.ID] >= 5

    def effCanTrig(self):
        self.effectViable = self.willEnhance()

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        self.Game.summon([ShieldGuardian(self.Game, self.ID)], (-11, "totheRightEnd"), self)
        if comment >= 5:
            self.Game.summon([ShieldGuardian(self.Game, self.ID) for i in range(2)], (-11, "totheRightEnd"),
                             self)
            if comment == 10:
                for minion in self.Game.minionsonBoard(self.ID):
                    if type(minion) == ShieldGuardian:
                        minion.buffDebuff(3, 3)
        return None


class VIIOluonTheChariot(SVMinion):
    Class, race, name = "Swordcraft", "Commander", "VII. Oluon, The Chariot"
    mana, attack, health = 3, 3, 3
    index = "SV_Fortune~Swordcraft~Minion~3~3~3~Commander~VII. Oluon, The Chariot~Battlecry~Legendary"
    requireTarget, keyWord, description = False, "", "Fanfare: Enhance (7) - Transform this follower into a VII. Oluon, Runaway Chariot.At the end of your turn, randomly activate 1 of the following effects.-Gain Ward.-Summon a Knight.-Deal 2 damage to the enemy leader."
    attackAdd, healthAdd = 2, 2
    name_CN = "《战车》·奥辂昂"

    def __init__(self, Game, ID):
        super().__init__(Game, ID)
        self.trigsBoard = [Trig_VIIOluonTheChariot(self)]

    def getMana(self):
        if self.Game.Manas.manas[self.ID] >= 7:
            return 7
        else:
            return self.mana

    def willEnhance(self):
        return self.Game.Manas.manas[self.ID] >= 7

    def effCanTrig(self):
        self.effectViable = self.willEnhance()

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if comment == 7:
            self.Game.transform(self, VIIOluonRunawayChariot(self.Game, self.ID))
        return None


class Trig_VIIOluonTheChariot(TrigBoard):
    def __init__(self, entity):
        super().__init__(entity, ["TurnEnds"])

    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
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
            self.entity.getsStatus("Taunt")
        elif e == "H":
            self.entity.dealsDamage(self.entity.Game.heroes[3 - self.entity.ID], 2)
        elif e == "K":
            self.entity.Game.summon([Knight(self.entity.Game, self.entity.ID)], (-11, "totheRightEnd"),
                                    self.entity)


class VIIOluonRunawayChariot(SVMinion):
    Class, race, name = "Swordcraft", "Commander", "VII. Oluon, Runaway Chariot"
    mana, attack, health = 7, 8, 16
    index = "SV_Fortune~Swordcraft~Minion~7~8~16~Commander~VII. Oluon, Runaway Chariot~Uncollectible~Legendary"
    requireTarget, keyWord, description = False, "", "Can't attack.At the end of your turn, randomly deal X damage to an enemy or another ally and then Y damage to this follower. X equals this follower's attack and Y equals the attack of the follower or leader damaged (leaders have 0 attack). Do this 2 times."
    attackAdd, healthAdd = 2, 2
    name_CN = "《暴走》战车·奥辂昂"

    def __init__(self, Game, ID):
        super().__init__(Game, ID)
        self.marks["Can't Attack"] = 1
        self.trigsBoard = [Trig_VIIOluonRunawayChariot(self)]


class Trig_VIIOluonRunawayChariot(TrigBoard):
    def __init__(self, entity):
        super().__init__(entity, ["TurnEnds"])

    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
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
                            curGame.fixedGuides.append((char.pos, char.type + str(char.ID)))
                        else:
                            curGame.fixedGuides.append((0, ''))
                    if char:
                        self.entity.dealsDamage(char, self.entity.attack)
                        damage = 0
                        if char.type == "Minion":
                            damage = char.attack
                        char.dealsDamage(self.entity, damage)
                        self.entity.Game.gathertheDead()


class PrudentGeneral(SVMinion):
    Class, race, name = "Swordcraft", "Commander", "PrudentGeneral"
    mana, attack, health = 4, 3, 4
    index = "SV_Fortune~Swordcraft~Minion~4~3~4~Commander~Prudent General"
    requireTarget, keyWord, description = False, "", ""
    attackAdd, healthAdd = 2, 2
    name_CN = "静寂的元帅"

    def inHandEvolving(self, target=None):
        trigger = Trig_PrudentGeneral(self.Game.heroes[self.ID])
        for t in self.Game.heroes[self.ID].trigsBoard:
            if type(t) == type(trigger):
                return
        self.Game.heroes[self.ID].trigsBoard.append(trigger)
        trigger.connect()


class Trig_PrudentGeneral(TrigBoard):
    def __init__(self, entity):
        super().__init__(entity, ["TurnEnds"])

    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.onBoard and ID == self.entity.ID

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        self.entity.Game.summon([SteelcladKnight(self.entity.Game, self.entity.ID)], (-1, "totheRightEnd"),
                                self.entity)


class StrikelanceKnight(SVMinion):
    Class, race, name = "Swordcraft", "Officer", "Strikelance Knight"
    mana, attack, health = 5, 4, 5
    index = "SV_Fortune~Swordcraft~Minion~5~4~5~Officer~Strikelance Knight~Battlecry"
    requireTarget, keyWord, description = False, "", "Fanfare: If an allied Commander card is in play, evolve this follower."
    attackAdd, healthAdd = 2, 2
    name_CN = "冲锋骑士"

    def effCanTrig(self):
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
    name_CN = "耀钻圣骑士"

    def __init__(self, Game, ID):
        super().__init__(Game, ID)
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

    def effCanTrig(self):
        self.effectViable = self.willEnhance()

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if comment == 8:
            self.marks["Free Evolve"] += 1
        return None

    def inHandEvolving(self, target=None):
        if target:
            if isinstance(target, list): target = target[0]
            target.buffDebuff(-4, 0)
        return target

    def extraTargetCorrect(self, target, affair):
        return target.type and target.type == "Minion" and target.ID != self.ID and target.onBoard


class Trig_DiamondPaladin(TrigBoard):
    def __init__(self, entity):
        super().__init__(entity, ["MinionAttackedMinion"])

    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
        return subject == self.entity and self.entity.onBoard and (target.health < 1 or target.dead == True) and \
               (self.entity.health > 0 and self.entity.dead == False)

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        self.entity.getsStatus("Windfury")
        self.entity.Game.Manas.restoreManaCrystal(2, self.entity.ID)
        trigger = Trig_EndDiamondPaladin(self.entity)
        self.entity.trigsBoard.append(trigger)
        if self.entity.onBoard:
            trigger.connect()


class Trig_EndDiamondPaladin(TrigBoard):
    def __init__(self, entity):
        super().__init__(entity, ["TurnEnds"])

    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
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
    name_CN = "无私的贵族"

    def targetExists(self, choice=0):
        return len(self.Game.Hand_Deck.hands[self.ID]) > 1

    def targetCorrect(self, target, choice=0):
        if isinstance(target, list): target = target[0]
        return target.ID == self.ID and target.inHand and target != self

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if target:
            if isinstance(target, list): target = target[0]
            n = type(target).mana
            self.Game.Hand_Deck.discard(self.ID, target)
            self.buffDebuff(n, n)
        return target


"""Runecraft cards"""


class JugglingMoggy(SVMinion):
    Class, race, name = "Runecraft", "", "Juggling Moggy"
    mana, attack, health = 1, 1, 1
    index = "SV_Fortune~Runecraft~Minion~1~1~1~~Juggling Moggy~Battlecry~EarthRite"
    requireTarget, keyWord, description = False, "", "Fanfare: Earth Rite - Gain +1/+1 and Last Words: Summon 2 Earth Essences."
    attackAdd, healthAdd = 2, 2
    name_CN = "魔猫魔术师"

    def effCanTrig(self):
        self.effectViable = len(self.Game.earthsonBoard(self.ID)) > 0

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if self.Game.earthRite(self, self.ID):
            self.buffDebuff(1, 1)
            deathrattle = Deathrattle_JugglingMoggy(self)
            self.deathrattles.append(deathrattle)
            if self.onBoard:
                deathrattle.connect()
        return None


class Deathrattle_JugglingMoggy(Deathrattle_Minion):
    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        self.entity.Game.summon([EarthEssence(self.entity.Game, self.entity.ID) for i in range(2)],
                                (-1, "totheRightEnd"), self.entity)


class MagicalAugmentation(SVSpell):
    Class, school, name = "Runecraft", "", "Magical Augmentation"
    requireTarget, mana = True, 1
    index = "SV_Fortune~Runecraft~Spell~1~Magical Augmentation~EarthRite"
    description = "Deal 1 damage to an enemy follower. Earth Rite (2): Deal 4 damage instead. Then draw 2 cards."
    name_CN = "扩展的魔法"

    def effCanTrig(self):
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
                self.dealsDamage(target, damage)
                self.Game.Hand_Deck.drawCard(self.ID)
                self.Game.Hand_Deck.drawCard(self.ID)
            else:
                damage = (1 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
                self.dealsDamage(target, damage)
        return target


class CreativeConjurer(SVMinion):
    Class, race, name = "Runecraft", "", "Creative Conjurer"
    mana, attack, health = 2, 2, 2
    index = "SV_Fortune~Runecraft~Minion~2~2~2~~Creative Conjurer~Battlecry~EarthRite"
    requireTarget, keyWord, description = False, "", "Fanfare: If there are no allied Earth Sigil amulets in play, summon an Earth Essence. Otherwise, perform Earth Rite: Put a Golem Summoning into your hand."
    attackAdd, healthAdd = 2, 2
    name_CN = "创物魔法师"

    def effCanTrig(self):
        self.effectViable = len(self.Game.earthsonBoard(self.ID)) >= 0

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if self.Game.earthRite(self, self.ID):
            self.Game.Hand_Deck.addCardtoHand(GolemSummoning, self.ID, byType=True)
        else:
            self.Game.summon([EarthEssence(self.Game, self.ID)], (-1, "totheRightEnd"), self)
        return None


class GolemSummoning(SVSpell):
    Class, school, name = "Runecraft", "", "Golem Summoning"
    requireTarget, mana = False, 2
    index = "SV_Fortune~Runecraft~Spell~2~Golem Summoning~Uncollectible"
    description = "Summon a Guardian Golem. If you have 20 cards or less in your deck, evolve it."
    name_CN = "巨像创造"

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        minion = GuardianGolem(self.Game, self.ID)
        self.Game.summon([minion], (-1, "totheRightEnd"), self)
        if len(self.Game.Hand_Deck.decks[self.ID]) <= 20:
            minion.evolve()
        return None


class LhynkalTheFool(SVMinion):
    Class, race, name = "Runecraft", "", "0. Lhynkal, The Fool"
    mana, attack, health = 2, 2, 2
    index = "SV_Fortune~Runecraft~Minion~2~2~2~~0. Lhynkal, The Fool~Battlecry~Choose~Legendary"
    requireTarget, keyWord, description = False, "", "Fanfare: Choose - Put a Rite of the Ignorant or Scourge of the Omniscient into your hand."
    attackAdd, healthAdd = 2, 2
    name_CN = "《愚者》·琳库露"

    def inHandEvolving(self, target=None):
        self.Game.Manas.restoreManaCrystal(2, self.ID)

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        self.Game.options = [RiteoftheIgnorant(self.Game, self.ID), ScourgeoftheOmniscient(self.Game, self.ID)]
        self.Game.Discover.startDiscover(self)
        return None

    def discoverDecided(self, option, pool):
        self.Game.fixedGuides.append(type(option))
        self.Game.Hand_Deck.addCardtoHand(option, self.ID, byDiscover=True)


class RiteoftheIgnorant(SVSpell):
    Class, school, name = "Runecraft", "", "Rite of the Ignorant"
    requireTarget, mana = False, 4
    index = "SV_Fortune~Runecraft~Spell~4~Rite of the Ignorant~Uncollectible~Legendary"
    description = "Give your leader the following effect: At the start of your turn, draw a card and Spellboost it X times. X equals a random number between 1 and 10. Then give it the following effect: At the end of your turn, discard this card. (This leader effect lasts for the rest of the match.)"
    name_CN = "蒙昧的术式"

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
        super().__init__(entity, ["TurnStarts"])

    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
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


class Trig_EndRiteoftheIgnorant(TrigHand):
    def __init__(self, entity):
        super().__init__(entity, ["TurnEnds"])
        self.temp = True
        self.changesCard = True

    # They will be discarded at the end of any turn
    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.inHand

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        self.entity.Game.Hand_Deck.discard(self.entity.ID, self.entity)


class ScourgeoftheOmniscient(SVSpell):
    Class, school, name = "Runecraft", "", "Scourge of the Omniscient"
    requireTarget, mana = False, 2
    index = "SV_Fortune~Runecraft~Spell~2~Scourge of the Omniscient~Uncollectible~Legendary"
    description = "Give the enemy leader the following effect: At the end of your turn, reduce your leader's maximum defense by 1. (This effect lasts for the rest of the match.)"
    name_CN = "剥落的镇压"

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
        super().__init__(entity, ["TurnEnds"])

    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.onBoard and ID == self.entity.ID

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        self.entity.health_max -= 1
        self.entity.health = min(self.entity.health, self.entity.health_max)


class AuthoringTomorrow(SVSpell):
    Class, school, name = "Runecraft", "", "Authoring Tomorrow"
    requireTarget, mana = False, 2
    index = "SV_Fortune~Runecraft~Spell~2~Authoring Tomorrow"
    description = "Give your leader the following effect: At the end of your turn, if it is your second, fourth, sixth, or eighth turn, deal 1 damage to all enemy followers. If it is your third, fifth, seventh, or ninth turn, draw a card. If it is your tenth turn or later, deal 5 damage to the enemy leader. (This effect is not stackable and is removed after activating 3 times.)"
    name_CN = "预知未来"

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        trigger = Trig_AuthoringTomorrow(self.Game.heroes[self.ID])
        for t in self.Game.heroes[self.ID].trigsBoard:
            if type(t) == type(trigger):
                return
        self.Game.heroes[self.ID].trigsBoard.append(trigger)
        trigger.connect()
        return None


class Trig_AuthoringTomorrow(TrigBoard):
    def __init__(self, entity):
        super().__init__(entity, ["TurnEnds"])
        self.counter = 3

    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.onBoard and ID == self.entity.ID

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        turn = self.entity.Game.Counters.turns[self.entity.ID]
        if turn in [2, 4, 6, 8]:
            targets = self.entity.Game.minionsonBoard(3 - self.entity.ID)
            if targets:
                self.entity.dealsAOE(targets, [1 for obj in targets])
        elif turn in [3, 5, 7, 9]:
            self.entity.Game.Hand_Deck.drawCard(self.entity.ID)
        elif turn >= 10:
            self.entity.dealsDamage(self.entity.Game.heroes[3 - self.entity.ID], 5)
        self.counter -= 1
        if self.counter <= 0:
            for t in self.entity.trigsBoard:
                if t == self:
                    t.disconnect()
                    self.entity.trigsBoard.remove(t)
                    break


class MadcapConjuration(SVSpell):
    Class, school, name = "Runecraft", "", "Madcap Conjuration"
    requireTarget, mana = False, 2
    index = "SV_Fortune~Runecraft~Spell~2~Madcap Conjuration"
    description = "Discard your hand.If at least 2 spells were discarded, draw 5 cards.If at least 2 followers were discarded, destroy all followers.If at least 2 amulets were discarded, summon 2 Clay Golems and deal 2 damage to the enemy leader."
    name_CN = "乱无章法的嵌合"

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        hands = self.Game.Hand_Deck.hands[self.ID]
        types = {"Spell": 0, "Minion": 0, "Amulet": 0}
        for card in hands:
            if card.type in types:
                types[card.type] += 1
        self.Game.Hand_Deck.discardAll(self.ID)
        if types["Spell"] >= 2:
            for i in range(5):
                self.Game.Hand_Deck.drawCard(self.ID)
        if types["Minion"] >= 2:
            self.Game.killMinion(self, self.Game.minionsAlive(1) + self.Game.minionsAlive(2))
        if types["Amulet"] >= 2:
            self.Game.summon([ClayGolem(self.Game, self.ID) for i in range(2)], (-1, "totheRightEnd"), self)
            damage = (2 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
            self.dealsDamage(self.Game.heroes[3 - self.ID], damage)


class ArcaneAuteur(SVMinion):
    Class, race, name = "Runecraft", "", "Arcane Auteur"
    mana, attack, health = 3, 3, 3
    index = "SV_Fortune~Runecraft~Minion~3~3~3~~Arcane Auteur~Deathrattle"
    requireTarget, keyWord, description = False, "", "Last Words: Put an Insight into your hand."
    attackAdd, healthAdd = 2, 2
    name_CN = "魔导书撰写者"

    def __init__(self, Game, ID):
        super().__init__(Game, ID)
        self.deathrattles = [Deathrattle_ArcaneAuteur(self)]


class Deathrattle_ArcaneAuteur(Deathrattle_Minion):
    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        self.entity.Game.Hand_Deck.addCardtoHand(Insight, self.entity.ID, byType=True)


class PiquantPotioneer(SVMinion):
    Class, race, name = "Runecraft", "", "Piquant Potioneer"
    mana, attack, health = 4, 3, 3
    index = "SV_Fortune~Runecraft~Minion~4~3~3~~Piquant Potioneer~Battlecry"
    requireTarget, keyWord, description = False, "", "Fanfare: Deal 1 damage to all enemy followers. If you have 20 cards or less in your deck, deal 3 damage instead."
    attackAdd, healthAdd = 2, 2
    name_CN = "魔药巫师"

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        damage = 1
        if len(self.Game.Hand_Deck.decks[self.ID]) <= 20:
            damage = 3
        targets = self.Game.minionsonBoard(3 - self.ID)
        self.dealsAOE(targets, damage)


class ImperatorofMagic(SVMinion):
    Class, race, name = "Runecraft", "", "Imperator of Magic"
    mana, attack, health = 4, 2, 2
    index = "SV_Fortune~Runecraft~Minion~4~2~2~~Imperator of Magic~Battlecry~Enhance~EarthRite"
    requireTarget, keyWord, description = False, "", "Fanfare: Earth Rite - Summon an Emergency Summoning. Fanfare: Enhance (6) - Recover 1 evolution point."
    attackAdd, healthAdd = 2, 2
    evolveRequireTarget = True
    name_CN = "魔导君临者"

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

    def effCanTrig(self):
        self.effectViable = len(self.Game.earthsonBoard(self.ID)) > 0 or self.willEnhance()

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if self.Game.earthRite(self, self.ID):
            self.Game.summon(
                [EmergencySummoning(self.Game, self.ID)], (-1, "totheRightEnd"), self)
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
        return target


class EmergencySummoning(Amulet):
    Class, race, name = "Runecraft", "Earth Sigil", "Emergency Summoning"
    mana = 5
    index = "SV_Fortune~Runecraft~Amulet~5~Earth Sigil~Emergency Summoning~Deathrattle~Uncollectible"
    requireTarget, description = False, "When your opponent plays a follower, destroy this amulet. Last Words: Summon a Guardian Golem and a Clay Golem."
    name_CN = "紧急召唤"

    def __init__(self, Game, ID):
        super().__init__(Game, ID)
        self.deathrattles = [Deathrattle_EmergencySummoning(self)]
        self.trigsBoard = [Trig_EmergencySummoning(self)]


class Deathrattle_EmergencySummoning(Deathrattle_Minion):
    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        self.entity.Game.summon(
            [GuardianGolem(self.entity.Game, self.entity.ID), ClayGolem(self.entity.Game, self.entity.ID)],
            (-1, "totheRightEnd"), self.entity)


class Trig_EmergencySummoning(TrigBoard):
    def __init__(self, entity):
        super().__init__(entity, ["MinionPlayed"])

    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.onBoard and subject.ID != self.entity.ID

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        self.entity.Game.killMinion(self.entity, self.entity)


class HappyPig(SVMinion):
    Class, race, name = "Neutral", "", "Happy Pig"
    mana, attack, health = 2, 2, 2
    index = "SV_Fortune~Neutral~Minion~2~2~2~~Happy Pig~Deathrattle"
    requireTarget, keyWord, description = False, "", "Last Words: Restore 1 defense to your leader."
    attackAdd, healthAdd = 2, 2
    name_CN = "快乐小猪"

    def __init__(self, Game, ID):
        super().__init__(Game, ID)
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
        self.entity.restoresHealth(self.entity.Game.heroes[self.entity.ID], 1)


class Deathrattle_EvolvedHappyPig(Deathrattle_Minion):
    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        self.entity.restoresHealth(self.entity.Game.heroes[self.entity.ID], 3)


class SweetspellSorcerer(SVMinion):
    Class, race, name = "Runecraft", "", "Sweetspell Sorcerer"
    mana, attack, health = 5, 4, 4
    index = "SV_Fortune~Runecraft~Minion~5~4~4~~Sweetspell Sorcerer"
    requireTarget, keyWord, description = False, "", "Whenever you play a spell, summon a Happy Pig."
    attackAdd, healthAdd = 2, 2
    name_CN = "甜品魔术师"

    def __init__(self, Game, ID):
        super().__init__(Game, ID)
        self.trigsBoard = [Trig_SweetspellSorcerer(self)]

    def inHandEvolving(self, target=None):
        minions = self.Game.minionsAlive(self.ID)
        for minion in minions:
            if minion.name == "Happy Pig":
                minion.evolve()


class Trig_SweetspellSorcerer(TrigBoard):
    def __init__(self, entity):
        super().__init__(entity, ["SpellPlayed"])

    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.onBoard and subject.ID == self.entity.ID

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        self.entity.Game.summon(
            [HappyPig(self.entity.Game, self.entity.ID)], (-1, "totheRightEnd"), self.entity)


class WitchSnap(SVSpell):
    Class, school, name = "Runecraft", "", "Witch Snap"
    requireTarget, mana = True, 2
    index = "SV_Fortune~Runecraft~Spell~2~Witch Snap"
    description = "Deal 1 damage to an enemy follower. Earth Rite (2): Deal 4 damage instead. Then draw 2 cards."
    name_CN = "魔法的一击"

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
            self.dealsDamage(target, damage)
            self.Game.Hand_Deck.addCardtoHand(EarthEssence, self.ID, byType=True)
        return target


class AdamantineGolem(SVMinion):
    Class, race, name = "Runecraft", "", "Adamantine Golem"
    mana, attack, health = 6, 6, 6
    index = "SV_Fortune~Runecraft~Minion~6~6~6~~Adamantine Golem~Battlecry~EarthRite~Legendary"
    requireTarget, keyWord, description = False, "", "During your turn, when this card is added to your hand from your deck, if there are 2 allied Earth Sigil amulets or less in play, reveal it and summon an Earth Essence.Fanfare: Randomly activate 1 of the following effects. Earth Rite (X): Do this X more times. X equals the number of allied Earth Sigil amulets in play.-Summon a Guardian Golem.-Put a Witch Snap into your hand and change its cost to 0.-Deal 2 damage to the enemy leader. Restore 2 defense to your leader."
    attackAdd, healthAdd = 2, 2
    name_CN = "精金巨像"

    def __init__(self, Game, ID):
        super().__init__(Game, ID)

    def effCanTrig(self):
        self.effectViable = len(self.Game.earthsonBoard(self.ID)) > 0

    def whenDrawn(self):
        if self.Game.turn == self.ID and len(self.Game.earthsonBoard(self.ID)) <= 2:
            self.Game.summon(
                [EarthEssence(self.Game, self.ID)], (-1, "totheRightEnd"), self)

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
                        [GuardianGolem(self.Game, self.ID)], (-1, "totheRightEnd"), self)
                elif e == "P":
                    card = WitchSnap(self.Game, self.ID)
                    self.Game.Hand_Deck.addCardtoHand(card, self.ID)
                    ManaMod(card, changeby=-2, changeto=0).applies()
                elif e == "D":
                    self.dealsDamage(self.Game.heroes[3 - self.ID], 2)
                    self.restoresHealth(self.Game.heroes[self.ID], 2)


"""Dragoncraft cards"""


class DragoncladLancer(SVMinion):
    Class, race, name = "Dragoncraft", "", "Dragonclad Lancer"
    mana, attack, health = 1, 1, 1
    index = "SV_Fortune~Dragoncraft~Minion~1~1~1~~Dragonclad Lancer~Battlecry"
    requireTarget, keyWord, description = True, "", "Fanfare: Deal 4 damage to an enemy follower."
    attackAdd, healthAdd = 2, 2
    name_CN = "龙装枪术士"

    def targetExists(self, choice=0):
        return self.selectableFriendlyMinionExists()

    def targetCorrect(self, target, choice=0):
        if isinstance(target, list): target = target[0]
        return target.type == "Minion" and target.ID == self.ID and target.onBoard

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if target:
            if isinstance(target, list): target = target[0]
            self.dealsDamage(target, 2)
            self.Game.Hand_Deck.drawCard(self.ID)
            self.buffDebuff(2, 1)
        return target


class SpringwellDragonKeeper(SVMinion):
    Class, race, name = "Dragoncraft", "", "Springwell Dragon Keeper"
    mana, attack, health = 2, 2, 2
    index = "SV_Fortune~Dragoncraft~Minion~2~2~2~~Springwell Dragon Keeper~Battlecry~Enhance"
    requireTarget, keyWord, description = True, "", "Fanfare: Discard a card and deal 4 damage to an enemy follower.(Activates only when both a targetable card is in your hand and a targetable enemy follower is in play.)Enhance (5): Gain +3/+3."
    attackAdd, healthAdd = 2, 2
    name_CN = "召水驭龙使"

    def getMana(self):
        if self.Game.Manas.manas[self.ID] >= 5:
            return 5
        else:
            return self.mana

    def willEnhance(self):
        return self.Game.Manas.manas[self.ID] >= 5

    def effCanTrig(self):
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
        if comment == 5:
            self.buffDebuff(3, 3)
        return target


class TropicalGrouper(SVMinion):
    Class, race, name = "Dragoncraft", "", "Tropical Grouper"
    mana, attack, health = 2, 1, 2
    index = "SV_Fortune~Dragoncraft~Minion~2~1~2~~Tropical Grouper~Battlecry~Enhance"
    requireTarget, keyWord, description = False, "", "Fanfare: Enhance (4) - Summon a Tropical Grouper. During your turn, whenever another allied follower evolves, summon a Tropical Grouper."
    attackAdd, healthAdd = 2, 2
    name_CN = "热带铠鱼"

    def __init__(self, Game, ID):
        super().__init__(Game, ID)
        self.trigsBoard = [Trig_TropicalGrouper(self)]

    def getMana(self):
        if self.Game.Manas.manas[self.ID] >= 4:
            return 4
        else:
            return self.mana

    def willEnhance(self):
        return self.Game.Manas.manas[self.ID] >= 4

    def effCanTrig(self):
        self.effectViable = self.willEnhance()

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if comment == 4:
            self.Game.summon([TropicalGrouper(self.Game, self.ID)], (-1, "totheRightEnd"),
                             self)


class Trig_TropicalGrouper(TrigBoard):
    def __init__(self, entity):
        super().__init__(entity, ["MinionEvolved"])

    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
        return subject.ID == self.entity.ID and self.entity.onBoard and subject != self.entity

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        self.entity.Game.summon([TropicalGrouper(self.entity.Game, self.entity.ID)], (-1, "totheRightEnd"),
                                self.entity)


class WavecrestAngler(SVMinion):
    Class, race, name = "Dragoncraft", "", "Wavecrest Angler"
    mana, attack, health = 2, 2, 2
    index = "SV_Fortune~Dragoncraft~Minion~2~2~2~~Wavecrest Angler~Battlecry"
    requireTarget, keyWord, description = False, "", "Fanfare: Randomly put a copy of a card discarded by an effect this turn into your hand."
    attackAdd, healthAdd = 2, 2
    name_CN = "大洋钓手"

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        curGame = self.Game
        if curGame.mode == 0:
            if curGame.guides:
                i = curGame.guides.pop(0)
            else:
                cards = [i for i, card in enumerate(curGame.Counters.cardsDiscardedThisTurn[self.ID])]
                i = npchoice(cards) if cards else -1
                curGame.fixedGuides.append(i)
            if i > -1:
                card = self.Game.cardPool[curGame.Counters.cardsDiscardedThisGame[self.ID][i]]
                self.Game.Hand_Deck.addCardtoHand(card, self.ID, byType=True)


class DraconicCall(SVSpell):
    Class, school, name = "Dragoncraft", "", "Draconic Call"
    mana, requireTarget = 2, False
    index = "SV_Fortune~Dragoncraft~Spell~2~Draconic Call"
    description = "Randomly put 1 of the highest-cost Dragoncraft followers from your deck into your hand. If Overflow is active for you, randomly put 2 of the highest-cost Dragoncraft followers into your hand instead."
    name_CN = "聚龙之唤"

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
    index = "SV_Fortune~Dragoncraft~Minion~1~1~2~~Ivory Dragon~Battlecry"
    requireTarget, keyWord, description = False, "", "Fanfare: Draw a card if Overflow is active for you."
    attackAdd, healthAdd = 2, 2
    name_CN = "银白幼龙"

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if self.Game.isOverflow(self.ID):
            self.Game.Hand_Deck.drawCard(self.ID)


class Heliodragon(SVMinion):
    Class, race, name = "Dragoncraft", "", "Heliodragon"
    mana, attack, health = 3, 1, 5
    index = "SV_Fortune~Dragoncraft~Minion~3~1~5~~Heliodragon"
    requireTarget, keyWord, description = False, "", "If this card is discarded by an effect, summon an Ivory Dragon. Then, if Overflow is active for you, draw a card.During your turn, whenever you discard cards, restore X defense to your leader. X equals the number of cards discarded."
    attackAdd, healthAdd = 2, 2
    name_CN = "日轮之龙"

    def __init__(self, Game, ID):
        super().__init__(Game, ID)
        self.trigsBoard = [Trig_Heliodragon(self)]

    def whenDiscarded(self):
        self.Game.summon([IvoryDragon(self.Game, self.ID)], (-1, "totheRightEnd"),
                         self)
        if self.Game.isOverflow(self.ID):
            self.Game.Hand_Deck.drawCard(self.ID)


class Trig_Heliodragon(TrigBoard):
    def __init__(self, entity):
        super().__init__(entity, ["CardDiscarded", "HandDiscarded"])

    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
        return ID == self.entity.ID and self.entity.onBoard and number > 0

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        self.entity.restoresHealth(self.entity.Game.heroes[self.entity.ID], number)


class SlaughteringDragonewt(SVMinion):
    Class, race, name = "Dragoncraft", "", "Slaughtering Dragonewt"
    mana, attack, health = 3, 2, 8
    index = "SV_Fortune~Dragoncraft~Minion~3~2~8~~Slaughtering Dragonewt~Bane~Battlecry"
    requireTarget, keyWord, description = False, "Bane", "Fanfare: Draw a card if Overflow is active for you."
    attackAdd, healthAdd = 0, 0
    name_CN = "虐杀的龙人"

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        cards = enumerate(self.Game.Hand_Deck.decks[self.ID])
        for i, card in cards:
            if card.mana in [1, 3, 5, 7, 9]:
                self.Game.Hand_Deck.extractfromDeck(card, self.ID)

    def inHandEvolving(self, target=None):
        minions = self.Game.minionsonBoard(1) + self.Game.minionsonBoard(2)
        self.dealsAOE(minions, [4 for obj in minions])

    def canAttack(self):
        return self.actionable() and self.status["Frozen"] < 1 \
               and self.attChances_base + self.attChances_extra > self.attTimes \
               and self.marks["Can't Attack"] < 1 and self.Game.isOverflow(self.ID)


class Trig_TurncoatDragons(TrigHand):
    def __init__(self, entity):
        super().__init__(entity, ["CardDiscarded"])

    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.inHand and ID == self.entity.ID

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        self.entity.progress += 1
        self.entity.Game.Manas.calcMana_Single(self.entity)


class CrimsonDragonsSorrow(SVMinion):
    Class, race, name = "Dragoncraft", "", "Crimson Dragon's Sorrow"
    mana, attack, health = 5, 4, 4
    index = "SV_Fortune~Dragoncraft~Minion~5~4~4~~Crimson Dragon's Sorrow~Taunt~Battlecry~Legendary~Uncollectible"
    requireTarget, keyWord, description = True, "Taunt", "During your turn, whenever you discard cards, subtract X from the cost of this card. X equals the number of cards discarded.Ward.Fanfare: Discard a card. Draw 2 cards."
    attackAdd, healthAdd = 2, 2
    name_CN = "悲戚的赤龙"

    def __init__(self, Game, ID):
        super().__init__(Game, ID)
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
            self.Game.Hand_Deck.discard(self.ID, target)
            self.Game.Hand_Deck.drawCard(self.ID)
            self.Game.Hand_Deck.drawCard(self.ID)
        return target


class AzureDragonsRage(SVMinion):
    Class, race, name = "Dragoncraft", "", "Azure Dragon's Rage"
    mana, attack, health = 7, 4, 4
    index = "SV_Fortune~Dragoncraft~Minion~7~4~4~~Azure Dragon's Rage~Charge~Legendary~Uncollectible"
    requireTarget, keyWord, description = False, "Charge", "During your turn, whenever you discard cards, subtract X from the cost of this card. X equals the number of cards discarded.Ward.Fanfare: Discard a card. Draw 2 cards."
    attackAdd, healthAdd = 2, 2
    name_CN = "盛怒的碧龙"

    def __init__(self, Game, ID):
        super().__init__(Game, ID)
        self.trigsHand = [Trig_TurncoatDragons(self)]
        self.progress = 0

    def selfManaChange(self):
        if self.inHand:
            self.mana -= self.progress
            self.mana = max(self.mana, 0)


class TurncoatDragonSummoner(SVMinion):
    Class, race, name = "Dragoncraft", "", "Turncoat Dragon Summoner"
    mana, attack, health = 3, 2, 3
    index = "SV_Fortune~Dragoncraft~Minion~3~2~3~~Turncoat Dragon Summoner~Battlecry~Legendary"
    requireTarget, keyWord, description = True, "", "If this card is discarded by an effect, put a Crimson Dragon's Sorrow into your hand.Ward.Fanfare: Discard a card. Put an Azure Dragon's Rage into your hand."
    attackAdd, healthAdd = 2, 2
    name_CN = "恶极唤龙者"

    def __init__(self, Game, ID):
        super().__init__(Game, ID)

    def whenDiscarded(self):
        self.Game.Hand_Deck.addCardtoHand(CrimsonDragonsSorrow, self.ID, byType=True)

    def targetExists(self, choice=0):
        return len(self.Game.Hand_Deck.hands[self.ID]) > 1

    def targetCorrect(self, target, choice=0):
        if isinstance(target, list): target = target[0]
        return target.ID == self.ID and target.inHand and target != self

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if target:
            if isinstance(target, list): target = target[0]
            self.Game.Hand_Deck.discard(self.ID, target)
            self.Game.Hand_Deck.addCardtoHand(AzureDragonsRage, self.ID, byType=True)
        return target


class DragonsNest(Amulet):
    Class, race, name = "Dragoncraft", "", "Dragon's Nest"
    mana = 1
    index = "SV_Fortune~Dragoncraft~Amulet~1~~Dragon's Nest"
    requireTarget, description = False, "At the start of your turn, restore 2 defense to your leader, draw a card, and destroy this amulet if Overflow is active for you."
    name_CN = "龙之卵"

    def __init__(self, Game, ID):
        super().__init__(Game, ID)
        self.trigsBoard = [Trig_DragonsNest(self)]


class Trig_DragonsNest(TrigBoard):
    def __init__(self, entity):
        super().__init__(entity, ["TurnStarts"])

    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.onBoard and ID == self.entity.ID

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        if self.entity.Game.isOverflow(self.entity.ID):
            self.entity.restoresHealth(self.entity.Game.heroes[self.entity.ID], 2)
            self.entity.Game.Hand_Deck.drawCard(self.entity.ID)
            self.entity.Game.killMinion(self.entity, self.entity)


class DragonSpawning(SVSpell):
    Class, school, name = "Dragoncraft", "", "Dragon Spawning"
    mana, requireTarget = 3, False
    index = "SV_Fortune~Dragoncraft~Spell~3~Dragon Spawning"
    description = "Summon 2 Dragon's Nests. If you have 10 play point orbs, summon 5 instead."
    name_CN = "龙之诞生"

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        n = 2
        if self.Game.Manas.manasUpper[self.ID] >= 10:
            n = 5
        self.Game.summon([DragonsNest(self.Game, self.ID) for i in range(n)], (-1, "totheRightEnd"),
                         self)


class DragonImpact(SVSpell):
    Class, school, name = "Dragoncraft", "", "Dragon Impact"
    mana, requireTarget = 4, True
    index = "SV_Fortune~Dragoncraft~Spell~4~Dragon Impact"
    description = "Give +1/+1 and Rush to a Dragoncraft follower in your hand.Deal 5 damage to a random enemy follower.(Can be played only when a targetable card is in your hand.)"
    name_CN = "龙威迫击"

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
            target.getsStatus("Rush")
            target.buffDebuff(1, 1)
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
                        curGame.fixedGuides.append((enemy.pos, enemy.type + str(enemy.ID)))
                    else:
                        curGame.fixedGuides.append((0, ''))
                if enemy:
                    damage = (5 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
                    self.dealsDamage(enemy, damage)
        return target


class XIErntzJustice(SVMinion):
    Class, race, name = "Dragoncraft", "", "XI. Erntz, Justice"
    mana, attack, health = 10, 11, 8
    index = "SV_Fortune~Dragoncraft~Minion~10~11~8~~XI. Erntz, Justice~Ward~Legendary"
    requireTarget, keyWord, description = False, "Taunt", "Ward.When this follower comes into play, randomly activate 1 of the following effects.-Draw 3 cards.-Evolve this follower.When this follower leaves play, restore 8 defense to your leader. (Transformation doesn't count as leaving play.)"
    attackAdd, healthAdd = -3, 3
    name_CN = "《正义》·伊兰翠"

    def __init__(self, Game, ID):
        super().__init__(Game, ID)
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
            for num in range(3):
                self.Game.Hand_Deck.drawCard(self.ID)
        elif e == "E":
            self.evolve()

    def whenDisppears(self):
        self.restoresHealth(self.Game.heroes[self.ID], 8)

    def inEvolving(self):
        self.losesStatus("Taunt")
        self.getsStatus("Charge")
        self.marks["Ignore Taunt"] += 1
        self.marks["Enemy Effect Evasive"] += 1
        for f in self.disappearResponse:
            if f.__name__ == "whenDisppears":
                self.disappearResponse.remove(f)


"""Shadowcraft cards"""


class GhostlyMaid(SVMinion):
    Class, race, name = "Shadowcraft", "", "Ghostly Maid"
    mana, attack, health = 2, 2, 2
    index = "SV_Fortune~Shadowcraft~Minion~2~2~2~~Ghostly Maid~Battlecry"
    requireTarget, keyWord, description = False, "", "Fanfare: If there are any allied amulets in play, summon a Ghost. Then, if there are at least 2 in play, evolve it."
    attackAdd, healthAdd = 2, 2
    name_CN = "幽灵女仆"

    def effCanTrig(self):
        self.effectViable = len(self.Game.amuletsonBoard(self.ID)) > 0

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if len(self.Game.amuletsonBoard(self.ID)) > 0:
            minion = Ghost(self.Game, self.ID)
            self.Game.summon([minion], (-1, "totheRightEnd"),
                             self)
            if len(self.Game.amuletsonBoard(self.ID)) >= 2:
                minion.evolve()
        return None


class BonenanzaNecromancer(SVMinion):
    Class, race, name = "Shadowcraft", "", "Bonenanza Necromancer"
    mana, attack, health = 2, 2, 2
    index = "SV_Fortune~Shadowcraft~Minion~2~2~2~~Bonenanza Necromancer~Enhance~Battlecry"
    requireTarget, keyWord, description = False, "", "Fanfare: Enhance (7) - Reanimate (10). Whenever you perform Burial Rite, draw a card."
    attackAdd, healthAdd = 2, 2
    name_CN = "狂欢唤灵师"

    def __init__(self, Game, ID):
        super().__init__(Game, ID)
        self.trigsBoard = [Trig_BonenanzaNecromancer(self)]

    def getMana(self):
        if self.Game.Manas.manas[self.ID] >= 7:
            return 7
        else:
            return self.mana

    def willEnhance(self):
        return self.Game.Manas.manas[self.ID] >= 7

    def effCanTrig(self):
        self.effectViable = self.willEnhance()

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if comment == 7:
            minion = self.Game.reanimate(self.ID, 10)
        return None


class Trig_BonenanzaNecromancer(TrigBoard):
    def __init__(self, entity):
        super().__init__(entity, ["BurialRite"])

    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.onBoard and ID == self.entity.ID

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        self.entity.Game.Hand_Deck.drawCard(self.entity.ID)


class SavoringSlash(SVSpell):
    Class, school, name = "Shadowcraft", "", "Savoring Slash"
    requireTarget, mana = True, 2
    index = "SV_Fortune~Shadowcraft~Spell~2~Savoring Slash"
    description = "Deal 3 damage to an enemy follower. Burial Rite: Draw a card."
    name_CN = "饥欲斩击"

    def effCanTrig(self):
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
                self.Game.Hand_Deck.burialRite(self.ID, allied)
                self.Game.Hand_Deck.drawCard(self.ID)
            else:
                enemy = target[0]
            damage = (3 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
            self.dealsDamage(enemy, damage)
        return target


class CoffinoftheUnknownSoul(Amulet):
    Class, race, name = "Shadowcraft", "", "Coffin of the Unknown Soul"
    mana = 2
    index = "SV_Fortune~Shadowcraft~Amulet~2~~Coffin of the Unknown Soul~Countdown~Battlecry~Deathrattle"
    requireTarget, description = True, "Countdown (1)Fanfare: Burial Rite - Draw a card and add X to this amulet's Countdown. X equals half the original cost of the follower destroyed by Burial Rite (rounded down).Last Words: Summon a copy of the follower destroyed by Burial Rite."
    name_CN = "幽灵之棺"

    def __init__(self, Game, ID):
        super().__init__(Game, ID)
        self.counter = 1
        self.trigsBoard = [Trig_Countdown(self)]
        self.deathrattles = [Deathrattle_CoffinoftheUnknownSoul(self)]

    def effCanTrig(self):
        self.effectViable = not self.Game.Hand_Deck.noMinionsinHand(self.ID, self) and self.Game.space(self.ID) >= 2

    def targetExists(self, choice=0):
        return not self.Game.Hand_Deck.noMinionsinHand(self.ID, self) and self.Game.space(self.ID) >= 2

    def targetCorrect(self, target, choice=0):
        if isinstance(target, list): target = target[0]
        return target.ID == self.ID and target.inHand and target != self and target.type == "Minion"

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if target:
            if isinstance(target, list): target = target[0]
            t = type(target)
            self.Game.Hand_Deck.burialRite(self.ID, target)
            for trigger in self.deathrattles:
                if type(trigger) == Deathrattle_CoffinoftheUnknownSoul:
                    trigger.chosenMinionType = t
            self.countdown(self, -int(t.mana / 2))
        return target


class Deathrattle_CoffinoftheUnknownSoul(Deathrattle_Minion):
    def __init__(self, entity):
        super().__init__(entity)
        self.chosenMinionType = None

    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
        return target == self.entity and self.chosenMinionType

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        self.entity.Game.summon([self.chosenMinionType(self.entity.Game, self.entity.ID)], (-1, "totheRightEnd"),
                                self.entity)

    def selfCopy(self, newMinion):
        trigger = type(self)(newMinion)
        trigger.chosenMinionType = self.chosenMinionType
        return trigger


class SpiritCurator(SVMinion):
    Class, race, name = "Shadowcraft", "", "Spirit Curator"
    mana, attack, health = 3, 3, 3
    index = "SV_Fortune~Shadowcraft~Minion~3~3~3~~Spirit Curator~Battlecry"
    requireTarget, keyWord, description = True, "", "Fanfare: Burial Rite - Draw a card."
    attackAdd, healthAdd = 2, 2
    name_CN = "灵魂鉴定师"

    def effCanTrig(self):
        self.effectViable = not self.Game.Hand_Deck.noMinionsinHand(self.ID, self) and self.Game.space(self.ID) >= 2

    def targetExists(self, choice=0):
        return not self.Game.Hand_Deck.noMinionsinHand(self.ID, self) and self.Game.space(self.ID) >= 2

    def targetCorrect(self, target, choice=0):
        if isinstance(target, list): target = target[0]
        return target.ID == self.ID and target.inHand and target != self and target.type == "Minion"

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if target:
            if isinstance(target, list): target = target[0]
            self.Game.Hand_Deck.burialRite(self.ID, target)
            self.Game.Hand_Deck.drawCard(self.ID)
        return target


class DeathFowl_Crystallize(Amulet):
    Class, race, name = "Shadowcraft", "", "Crystallize: Death Fowl"
    mana = 1
    index = "SV_Fortune~Shadowcraft~Amulet~1~~Death Fowl~Countdown~Crystallize~Deathrattle~Uncollectible"
    requireTarget, description = False, "Countdown (3) Last Words: Gain 4 shadows."
    name_CN = "结晶：死之魔鸟"

    def __init__(self, Game, ID):
        super().__init__(Game, ID)
        self.counter = 3
        self.trigsBoard = [Trig_Countdown(self)]
        self.deathrattles = [Deathrattle_DeathFowl_Crystallize(self)]


class Deathrattle_DeathFowl_Crystallize(Deathrattle_Minion):
    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        self.entity.Game.Counters.shadows[self.entity.ID] += 4


class DeathFowl(SVMinion):
    Class, race, name = "Shadowcraft", "", "Death Fowl"
    mana, attack, health = 4, 3, 3
    index = "SV_Fortune~Shadowcraft~Minion~4~3~3~~Death Fowl~Crystallize~Deathrattle"
    requireTarget, keyWord, description = False, "", "Crystallize (1): Countdown (3) Last Words: Gain 4 shadows. Fanfare: Gain 4 shadows.Last Words: Draw a card."
    crystallizeAmulet = DeathFowl_Crystallize
    attackAdd, healthAdd = 2, 2
    name_CN = "死之魔鸟"

    def __init__(self, Game, ID):
        super().__init__(Game, ID)
        self.deathrattles = [Deathrattle_DeathFowl(self)]

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

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        self.Game.Counters.shadows[self.ID] += 4


class Deathrattle_DeathFowl(Deathrattle_Minion):
    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        self.entity.Game.Hand_Deck.drawCard(self.entity.ID)


class SoulBox(SVMinion):
    Class, race, name = "Shadowcraft", "", "Soul Box"
    mana, attack, health = 5, 5, 4
    index = "SV_Fortune~Shadowcraft~Minion~2~2~2~~Soul Box~Battlecry"
    requireTarget, keyWord, description = False, "", "Fanfare: If there are any allied amulets in play, evolve this follower."
    attackAdd, healthAdd = 2, 2
    name_CN = "灵魂之箱"

    def effCanTrig(self):
        self.effectViable = len(self.Game.amuletsonBoard(self.ID)) > 0

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if len(self.Game.amuletsonBoard(self.ID)) > 0:
            self.evolve()
        return None


class VIMilteoTheLovers(SVMinion):
    Class, race, name = "Shadowcraft", "", "VI. Milteo, The Lovers"
    mana, attack, health = 5, 4, 4
    index = "SV_Fortune~Shadowcraft~Minion~5~4~4~~VI. Milteo, The Lovers~Battlecry~Enhance~Deathrattle~Legendary"
    requireTarget, keyWord, description = True, "", "Fanfare: Burial Rite (2) - Reanimate (X) and Reanimate (Y). X and Y equal 6 split randomly.(To perform Burial Rite (2), there must be at least 2 open spaces in your area after this follower comes into play.)Enhance (9): Do not perform Burial Rite. Evolve this follower instead.Can't be evolved using evolution points. (Can be evolved using card effects.)Last Words: Draw 2 cards."
    attackAdd, healthAdd = 2, 2
    name_CN = "《恋人》·米路缇欧"

    def __init__(self, Game, ID):
        super().__init__(Game, ID)
        self.deathrattles = [Deathrattle_VIMilteoTheLovers(self)]
        self.marks["Can't Evolve"] = 1

    def getMana(self):
        if self.Game.Manas.manas[self.ID] >= 9:
            return 9
        else:
            return self.mana

    def willEnhance(self):
        return self.Game.Manas.manas[self.ID] >= 9

    def effCanTrig(self):
        if self.willEnhance():
            self.effectViable = True
        else:
            minions = 0
            for card in self.Game.Hand_Deck.hands[self.ID]:
                if card.type == "Minion" and card is not self:
                    minions += 1
            self.effectViable = minions >= 2 and self.Game.space(self.ID) >= 3

    def returnTrue(self, choice=0):
        if self.willEnhance():
            return False
        return self.targetExists(choice) and len(self.targets) < 2

    def targetExists(self, choice=0):
        minions = 0
        for card in self.Game.Hand_Deck.hands[self.ID]:
            if card.type == "Minion" and card is not self:
                minions += 1
        return minions >= 2 and self.Game.space(self.ID) >= 3

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
                self.Game.Counters.numBurialRiteThisGame[self.ID] += 1
                self.Game.sendSignal("BurialRite", self.ID, None, target[0], 0, "")
                self.Game.Counters.numBurialRiteThisGame[self.ID] += 1
                self.Game.sendSignal("BurialRite", self.ID, None, target[1], 0, "")
        return target


class Deathrattle_VIMilteoTheLovers(Deathrattle_Minion):
    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        self.entity.Game.Hand_Deck.drawCard(self.entity.ID)
        self.entity.Game.Hand_Deck.drawCard(self.entity.ID)


class Trig_VIMilteoTheLovers(TrigBoard):
    def __init__(self, entity):
        super().__init__(entity, ["TurnEnds"])

    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
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
                        curGame.fixedGuides.append((minion.pos, "Minion%d" % minion.ID))
                        curGame.killMinion(self.entity, minion)
                    else:
                        curGame.fixedGuides.append((0, ""))
        if self.entity.Game.heroes[3 - self.entity.ID].health > 6:
            damage = self.entity.Game.heroes[3 - self.entity.ID].health - 6
            self.entity.dealsDamage(self.entity.Game.heroes[3 - self.entity.ID], damage)


class CloisteredSacristan_Crystallize(Amulet):
    Class, race, name = "Shadowcraft", "", "Crystallize: Cloistered Sacristan"
    mana = 2
    index = "SV_Fortune~Shadowcraft~Amulet~2~~Cloistered Sacristan~Countdown~Crystallize~Deathrattle~Uncollectible"
    requireTarget, description = False, "Countdown (4) Whenever you perform Burial Rite, subtract 1 from this amulet's Countdown. Last Words: Summon a Cloistered Sacristan."
    name_CN = "结晶：幽暗守墓者"

    def __init__(self, Game, ID):
        super().__init__(Game, ID)
        self.counter = 4
        self.trigsBoard = [Trig_Countdown(self), Trig_CloisteredSacristan_Crystallize(self)]
        self.deathrattles = [Deathrattle_CloisteredSacristan_Crystallize(self)]


class Deathrattle_CloisteredSacristan_Crystallize(Deathrattle_Minion):
    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        self.entity.Game.summon([CloisteredSacristan(self.entity.Game, self.entity.ID)], (-1, "totheRightEnd"),
                                self.entity)


class Trig_CloisteredSacristan_Crystallize(TrigBoard):
    def __init__(self, entity):
        super().__init__(entity, ["BurialRite"])

    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.onBoard and ID == self.entity.ID

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        self.entity.countdown(self.entity, 1)


class CloisteredSacristan(SVMinion):
    Class, race, name = "Shadowcraft", "", "Cloistered Sacristan"
    mana, attack, health = 6, 5, 5
    index = "SV_Fortune~Shadowcraft~Minion~6~5~5~~Cloistered Sacristan~Taunt~Crystallize"
    requireTarget, keyWord, description = False, "Taunt", "Crystallize (2): Countdown (4)Whenever you perform Burial Rite, subtract 1 from this amulet's Countdown.Last Words: Summon a Cloistered Sacristan.Ward."
    crystallizeAmulet = DeathFowl_Crystallize
    attackAdd, healthAdd = 2, 2
    evolveRequireTarget = True
    name_CN = "幽暗守墓者"

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

    def effCanTrig(self):
        if self.willCrystallize() and self.targetExists():
            self.effectViable = "sky blue"
        else:
            self.effectViable = False

    def inHandEvolving(self, target=None):
        if target:
            if isinstance(target, list): target = target[0]
            self.Game.Hand_Deck.burialRite(self.ID, target)
            self.restoresHealth(self.Game.heroes[self.ID], 3)
        return target


class ConqueringDreadlord(SVMinion):
    Class, race, name = "Shadowcraft", "", "Conquering Dreadlord"
    mana, attack, health = 8, 6, 6
    index = "SV_Fortune~Shadowcraft~Minion~8~6~6~~Conquering Dreadlord~Invocation~Legendary"
    requireTarget, keyWord, description = False, "", "Invocation: When you perform Burial Rite, if it is your fifth, seventh, or ninth time this match, invoke this card, then return it to your hand.When this follower leaves play, or at the end of your turn, summon a Lich. (Transformation doesn't count as leaving play.)"
    attackAdd, healthAdd = 2, 2
    name_CN = "征伐的死帝"

    def __init__(self, Game, ID):
        super().__init__(Game, ID)
        self.trigsBoard = [Trig_ConqueringDreadlord(self)]
        self.trigsDeck = [Trig_InvocationConqueringDreadlord(self)]
        self.disappearResponse = [self.whenDisppears]

    def whenDisppears(self):
        self.Game.summon([Lich(self.Game, self.ID)], (-1, "totheRightEnd"), self)

    def afterInvocation(self, signal, ID, subject, target, number, comment):
        self.Game.returnMiniontoHand(self, deathrattlesStayArmed=False)


class Trig_ConqueringDreadlord(TrigBoard):
    def __init__(self, entity):
        super().__init__(entity, ["TurnEnds"])

    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.onBoard and ID == self.entity.ID

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        self.entity.Game.summon([Lich(self.entity.Game, self.entity.ID)], (-1, "totheRightEnd"),
                                self.entity)


class Trig_InvocationConqueringDreadlord(TrigInvocation):
    def __init__(self, entity):
        super().__init__(entity, ["BurialRite"])

    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.inDeck and ID == self.entity.ID and self.entity.Game.space(self.entity.ID) > 0 and \
               self.entity.Game.Counters.numBurialRiteThisGame[self.entity.ID] in [5, 7, 9]


class Deathbringer_Crystallize(Amulet):
    Class, race, name = "Shadowcraft", "", "Crystallize: Deathbringer"
    mana = 2
    index = "SV_Fortune~Shadowcraft~Amulet~2~~Deathbringer~Countdown~Crystallize~Battlecry~Deathrattle~Uncollectible"
    requireTarget, description = False, "Countdown (3) Fanfare and Last Words: Transform a random enemy follower into a Skeleton."
    name_CN = "结晶：死灭召来者"

    def __init__(self, Game, ID):
        super().__init__(Game, ID)
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
                    curGame.fixedGuides.append((enemy.pos, enemy.type + str(enemy.ID)))
                else:
                    curGame.fixedGuides.append((0, ''))
            if enemy:
                self.Game.transform(enemy, Skeleton(self.Game, 3 - self.ID))


class Deathrattle_Deathbringer_Crystallize(Deathrattle_Minion):
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
                    curGame.fixedGuides.append((enemy.pos, enemy.type + str(enemy.ID)))
                else:
                    curGame.fixedGuides.append((0, ''))
            if enemy:
                self.entity.Game.transform(enemy, Skeleton(self.entity.Game, 3 - self.entity.ID))


class Deathbringer(SVMinion):
    Class, race, name = "Shadowcraft", "", "Deathbringer"
    mana, attack, health = 9, 7, 7
    index = "SV_Fortune~Shadowcraft~Minion~9~7~7~~Deathbringer~Crystallize"
    requireTarget, keyWord, description = False, "", "Crystallize (2): Countdown (3) Fanfare and Last Words: Transform a random enemy follower into a Skeleton.At the end of your turn, destroy 2 random enemy followers and restore 5 defense to your leader."
    crystallizeAmulet = Deathbringer_Crystallize
    attackAdd, healthAdd = 2, 2
    name_CN = "死灭召来者"

    def __init__(self, Game, ID):
        super().__init__(Game, ID)
        self.trigsBoard = [Trig_Deathbringer(self)]

    def getMana(self):
        if self.Game.Manas.manas[self.ID] < self.mana:
            return 2
        else:
            return self.mana

    def willCrystallize(self):
        curMana = self.Game.Manas.manas[self.ID]
        return self.mana > curMana >= 2

    def effCanTrig(self):
        if self.willCrystallize() and self.targetExists():
            self.effectViable = "sky blue"
        else:
            self.effectViable = False


class Trig_Deathbringer(TrigBoard):
    def __init__(self, entity):
        super().__init__(entity, ["TurnEnds"])

    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
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
                        curGame.fixedGuides.append((enemy.pos, enemy.type + str(enemy.ID)))
                    else:
                        curGame.fixedGuides.append((0, ''))
                if enemy:
                    self.entity.Game.killMinion(self.entity, enemy)
        self.entity.restoresHealth(self.entity.Game.heroes[self.entity.ID], 5)


"""Bloodcraft cards"""


class SilverboltHunter(SVMinion):
    Class, race, name = "Bloodcraft", "", "Silverbolt Hunter"
    mana, attack, health = 1, 1, 2
    index = "SV_Fortune~Bloodcraft~Minion~1~1~2~~Silverbolt Hunter~Battlecry~Deathrattle"
    requireTarget, keyWord, description = False, "", "Fanfare: Deal 1 damage to your leader. Last Words: Give +1/+1 to a random allied follower."
    attackAdd, healthAdd = 2, 2
    name_CN = "银箭狩猎者"

    def __init__(self, Game, ID):
        super().__init__(Game, ID)
        self.deathrattles = [Deathrattle_SilverboltHunter(self)]

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        self.dealsDamage(self.Game.heroes[self.ID], 1)


class Deathrattle_SilverboltHunter(Deathrattle_Minion):
    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        curGame = self.entity.Game
        if curGame.mode == 0:
            if curGame.guides:
                i = curGame.guides.pop(0)
            else:
                minions = [minion.pos for minion in curGame.minionsAlive(self.entity.ID)]
                i = npchoice(minions) if minions else -1
                curGame.fixedGuides.append(i)
            if i > -1:
                minion = curGame.minions[self.entity.ID][i]
                minion.buffDebuff(1, 1)


class MoonriseWerewolf(SVMinion):
    Class, race, name = "Bloodcraft", "", "Moonrise Werewolf"
    mana, attack, health = 2, 1, 3
    index = "SV_Fortune~Bloodcraft~Minion~2~1~3~~Moonrise Werewolf~Battlecry~Enhance"
    requireTarget, keyWord, description = False, "", "Fanfare: If Avarice is active for you, gain +0/+2 and Ward.Fanfare: Enhance (5) - Gain +3/+3."
    attackAdd, healthAdd = 2, 2
    name_CN = "月下的狼人"

    def getMana(self):
        if self.Game.Manas.manas[self.ID] >= 5:
            return 5
        else:
            return self.mana

    def willEnhance(self):
        return self.Game.Manas.manas[self.ID] >= 5

    def effCanTrig(self):
        self.effectViable = self.willEnhance() or self.Game.isAvarice(self.ID)

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if self.Game.isAvarice(self.ID):
            self.buffDebuff(0, 2)
            self.getsStatus("Taunt")
        if comment == 5:
            self.buffDebuff(3, 3)
        return target


class WhiplashImp(SVMinion):
    Class, race, name = "Bloodcraft", "", "Whiplash Imp"
    mana, attack, health = 2, 2, 2
    index = "SV_Fortune~Bloodcraft~Minion~2~2~2~~Whiplash Imp~Battlecry~Enhance"
    requireTarget, keyWord, description = False, "", "Fanfare: If Wrath is active for you, gain +1/+4, Rush, and Drain. Fanfare: Enhance (6) - Summon an Imp Lancer."
    attackAdd, healthAdd = 2, 2
    name_CN = "迅鞭小恶魔"

    def getMana(self):
        if self.Game.Manas.manas[self.ID] >= 6:
            return 6
        else:
            return self.mana

    def willEnhance(self):
        return self.Game.Manas.manas[self.ID] >= 6

    def effCanTrig(self):
        self.effectViable = self.willEnhance() or self.Game.isWrath(self.ID)

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if self.Game.isWrath(self.ID):
            self.buffDebuff(1, 4)
            self.getsStatus("Rush")
            self.getsStatus("Drain")
        if comment == 6:
            self.Game.summon([ImpLancer(self.Game, self.ID)], (-1, "totheRightEnd"),
                             self)
        return target


class ContemptousDemon(SVMinion):
    Class, race, name = "Bloodcraft", "", "Contemptous Demon"
    mana, attack, health = 2, 2, 2
    index = "SV_Fortune~Bloodcraft~Minion~2~2~2~~Contemptous Demon~Battlecry"
    requireTarget, keyWord, description = False, "", "Fanfare: If Wrath is active for you, gain the ability to evolve for 0 evolution points.At the end of your turn, deal 1 damage to your leader.At the start of your turn, restore 2 defense to your leader."
    attackAdd, healthAdd = 2, 2
    name_CN = "讥讽的恶魔"

    def __init__(self, Game, ID):
        super().__init__(Game, ID)
        self.trigsBoard = [Trig_StartContemptousDemon(self), Trig_EndContemptousDemon(self)]

    def effCanTrig(self):
        self.effectViable = self.Game.isWrath(self.ID)

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if self.Game.isWrath(self.ID):
            self.marks["Free Evolve"] += 1
        return target

    def inEvolving(self):
        trigger = Trig_EvolvedContemptousDemon(self)
        self.trigsBoard.append(trigger)
        trigger.connect()


class Trig_StartContemptousDemon(TrigBoard):
    def __init__(self, entity):
        super().__init__(entity, ["TurnStarts"])

    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.onBoard and ID == self.entity.ID

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        heal = 2 * (2 ** self.entity.countHealDouble())
        self.entity.restoresHealth(self.entity.Game.heroes[self.entity.ID], heal)


class Trig_EndContemptousDemon(TrigBoard):
    def __init__(self, entity):
        super().__init__(entity, ["TurnEnds"])

    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.onBoard and ID == self.entity.ID

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        self.entity.dealsDamage(self.entity.Game.heroes[self.entity.ID], 1)


class Trig_EvolvedContemptousDemon(TrigBoard):
    def __init__(self, entity):
        super().__init__(entity, ["HeroTookDmg", "HeroTook0Dmg", "TurnEnds"])
        self.counter = 10

    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
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
                        curGame.fixedGuides.append((enemy.pos, enemy.type + str(enemy.ID)))
                    else:
                        curGame.fixedGuides.append((0, ''))
                if enemy:
                    self.entity.dealsDamage(enemy, 3)
            self.counter -= 1
        else:
            self.counter = 10


class DarkSummons(SVSpell):
    Class, school, name = "Bloodcraft", "", "Dark Summons"
    requireTarget, mana = True, 2
    index = "SV_Fortune~Bloodcraft~Spell~2~Dark Summons"
    description = "Deal 3 damage to an enemy follower. If Wrath is active for you, recover 2 play points."
    name_CN = "暗黑融合"

    def available(self):
        return self.selectableEnemyMinionExists()

    def targetCorrect(self, target, choice=0):
        if isinstance(target, list): target = target[0]
        return target.type == "Minion" and target.ID != self.ID and target.onBoard

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if target:
            if isinstance(target, list): target = target[0]
            damage = (3 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
            self.dealsDamage(target, damage)
            if self.Game.isWrath(self.ID):
                self.Game.Manas.restoreManaCrystal(2, self.ID)
        return target


class TyrantofMayhem(SVMinion):
    Class, race, name = "Bloodcraft", "", "Tyrant of Mayhem"
    mana, attack, health = 3, 3, 3
    index = "SV_Fortune~Bloodcraft~Minion~3~3~3~~Tyrant of Mayhem~Battlecry"
    requireTarget, keyWord, description = False, "", "Fanfare: Draw a card. If Vengeance is not active for you, deal 2 damage to your leader. Otherwise, deal 2 damage to the enemy leader."
    attackAdd, healthAdd = 2, 2
    name_CN = "暴虐的恶魔"

    def effCanTrig(self):
        self.effectViable = self.Game.isVengeance(self.ID)

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        self.Game.Hand_Deck.drawCard(self.ID)
        if self.Game.isVengeance(self.ID):
            self.dealsDamage(self.Game.heroes[3 - self.ID], 2)
        else:
            self.dealsDamage(self.Game.heroes[self.ID], 2)
        return target


class CurmudgeonOgre(SVMinion):
    Class, race, name = "Bloodcraft", "", "Curmudgeon Ogre"
    mana, attack, health = 4, 4, 4
    index = "SV_Fortune~Bloodcraft~Minion~4~4~4~~Curmudgeon Ogre~Battlecry~Enhance"
    requireTarget, keyWord, description = False, "", "Fanfare: Enhance (6) - Give +1/+1 to all allied Bloodcraft followers. If Vengeance is active for you, give +2/+2 instead."
    attackAdd, healthAdd = 2, 2
    name_CN = "蛮吼的巨魔"

    def getMana(self):
        if self.Game.Manas.manas[self.ID] >= 6:
            return 6
        else:
            return self.mana

    def willEnhance(self):
        return self.Game.Manas.manas[self.ID] >= 6

    def effCanTrig(self):
        self.effectViable = self.willEnhance()

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if comment == 6:
            n = 1
            if self.Game.isVengeance(self.ID):
                n = 2
            for minion in self.Game.minionsonBoard(self.ID, self):
                if minion.Class == "Bloodcraft":
                    minion.buffDebuff(n, n)
        return target


class DireBond(Amulet):
    Class, race, name = "Bloodcraft", "", "Dire Bond"
    mana = 3
    index = "SV_Fortune~Bloodcraft~Amulet~3~~Dire Bond"
    requireTarget, description = False, "Countdown (3)Fanfare: Deal 6 damage to your leader.At the start of your turn, restore 2 defense to your leader and draw a card."
    name_CN = "漆黑之契"

    def __init__(self, Game, ID):
        super().__init__(Game, ID)
        self.counter = 3
        self.trigsBoard = [Trig_Countdown(self), Trig_DireBond(self)]

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        self.dealsDamage(self.Game.heroes[self.ID], 6)


class Trig_DireBond(TrigBoard):
    def __init__(self, entity):
        super().__init__(entity, ["TurnStarts"])

    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.onBoard and ID == self.entity.ID

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        self.entity.Game.Hand_Deck.drawCard(self.entity.ID)
        self.entity.restoresHealth(self.entity.Game.heroes[self.entity.ID], 2)


class DarholdAbyssalContract(SVMinion):
    Class, race, name = "Bloodcraft", "", "Darhold, Abyssal Contract"
    mana, attack, health = 4, 4, 3
    index = "SV_Fortune~Bloodcraft~Minion~4~4~3~~Darhold, Abyssal Contract~Battlecry~Legendary"
    requireTarget, keyWord, description = True, "", "Fanfare: If Wrath is active for you, destroy an enemy follower, then deal 3 damage to the enemy leader."
    attackAdd, healthAdd = 2, 2
    name_CN = "深渊之契·达尔霍德"

    def effCanTrig(self):
        self.effectViable = self.Game.isWrath(self.ID)

    def targetExists(self, choice=0):
        return self.selectableEnemyMinionExists() and self.Game.isWrath(self.ID)

    def targetCorrect(self, target, choice=0):
        if isinstance(target, list): target = target[0]
        return target.type == "Minion" and target.ID != self.ID and target.onBoard

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if target:
            if isinstance(target, list): target = target[0]
            self.Game.killMinion(self, target)
            self.dealsDamage(self.Game.heroes[3 - self.ID], 3)
        return target

    def inHandEvolving(self, target=None):
        self.dealsDamage(self.Game.heroes[self.ID], 3)
        self.Game.summon([DireBond(self.Game, self.ID)], (-1, "totheRightEnd"),
                         self)


class BurningConstriction(SVSpell):
    Class, school, name = "Bloodcraft", "", "Burning Constriction"
    mana, requireTarget = 5, False
    index = "SV_Fortune~Bloodcraft~Spell~5~Burning Constriction"
    description = "Deal 4 damage to all enemy followers. Then, if Vengeance is active for you, deal 4 damage to the enemy leader."
    name_CN = "盛燃的抵抗"

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        damage = (4 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
        targets = self.Game.minionsonBoard(3 - self.ID)
        self.dealsAOE(targets, [damage for minion in targets])
        if self.Game.isVengeance(self.ID):
            self.dealsDamage(self.Game.heroes[3 - self.ID], damage)
        return None


class VampireofCalamity_Accelerate(SVSpell):
    Class, school, name = "Bloodcraft", "", "Vampire of Calamity"
    requireTarget, mana = True, 1
    index = "SV_Fortune~Bloodcraft~Spell~1~Vampire of Calamity~Accelerate~Uncollectible"
    description = "Deal 1 damage to your leader. Deal 2 damage to an enemy follower."
    name_CN = "灾祸暗夜眷属"

    def targetCorrect(self, target, choice=0):
        if isinstance(target, list): target = target[0]
        return target.type == "Minion" and target.ID != self.ID and target.onBoard

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if target:
            if isinstance(target, list): target = target[0]
            damage = (1 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
            self.dealsDamage(self.Game.heroes[self.ID], damage)
            damage1 = (2 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
            self.dealsDamage(target, damage1)
        return target


class VampireofCalamity(SVMinion):
    Class, race, name = "Bloodcraft", "", "Vampire of Calamity"
    mana, attack, health = 7, 7, 7
    index = "SV_Fortune~Bloodcraft~Minion~7~7~7~~Vampire of Calamity~Rush~Battlecry~Accelerate"
    requireTarget, keyWord, description = True, "Rush", "Accelerate (1): Deal 1 damage to your leader. Deal 2 damage to an enemy follower.Rush.Fanfare: If Wrath is active for you, deal 4 damage to an enemy and restore 4 defense to your leader."
    accelerateSpell = VampireofCalamity_Accelerate
    attackAdd, healthAdd = 2, 2
    name_CN = "灾祸暗夜眷属"

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
            self.dealsDamage(target, 4)
        self.restoresHealth(self.Game.heroes[self.ID], 4)
        return target


class UnselfishGrace(Amulet):
    Class, race, name = "Bloodcraft", "", "Unselfish Grace"
    mana = 3
    index = "SV_Fortune~Bloodcraft~Amulet~3~~Unselfish Grace~Uncollectible~Legendary"
    requireTarget, description = False, "Countdown (5)At the end of your turn, restore 1 defense to your leader. If you have more evolution points than your opponent, restore 2 defense instead. (You have 0 evolution points on turns you are unable to evolve.)Last Words: Summon a 4-play point 4/4 XIV. Luzen, Temperance (without Accelerate)."
    name_CN = "无欲之恩宠"

    def __init__(self, Game, ID):
        super().__init__(Game, ID)
        self.counter = 5
        self.trigsBoard = [Trig_Countdown(self), Trig_UnselfishGrace(self)]
        self.deathrattles = [Deathrattle_UnselfishGrace(self)]


class Trig_UnselfishGrace(TrigBoard):
    def __init__(self, entity):
        super().__init__(entity, ["TurnEnds"])

    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.onBoard and ID == self.entity.ID

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        health = 1
        if self.entity.Game.getEvolutionPoint(self.entity.ID) > self.entity.Game.getEvolutionPoint(3 - self.entity.ID):
            health = 2
        self.entity.restoresHealth(self.entity.Game.heroes[self.entity.ID], health)


class Deathrattle_UnselfishGrace(Deathrattle_Minion):
    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        self.entity.Game.summon([XIVLuzenTemperance_Token(self.entity.Game, self.entity.ID)], (-1, "totheRightEnd"),
                                self.entity)


class InsatiableDesire(SVSpell):
    Class, school, name = "Bloodcraft", "", "Insatiable Desire"
    requireTarget, mana = False, 1
    index = "SV_Fortune~Bloodcraft~Spell~1~Insatiable Desire~Uncollectible~Legendary"
    description = "Give your leader the following effects.-At the start of your turn, draw a card.-At the start of your turn, lose 1 play point.(These effects are not stackable and last for the rest of the match.)"
    name_CN = "无尽之渴望"

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
        super().__init__(entity, ["TurnStarts"])

    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.onBoard and ID == self.entity.ID

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        self.entity.Game.Hand_Deck.drawCard(self.entity.ID)
        self.entity.Game.Manas.payManaCost(self.entity, 1)


class XIVLuzenTemperance_Accelerate(SVSpell):
    Class, school, name = "Bloodcraft", "", "XIV. Luzen, Temperance"
    requireTarget, mana = False, 0
    index = "SV_Fortune~Bloodcraft~Spell~0~XIV. Luzen, Temperance~Accelerate~Uncollectible~Legendary"
    description = "Put an Unselfish Grace into your hand. If Avarice is active for you, put an Insatiable Desire into your hand instead."
    name_CN = "《节制》·卢泽"

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if self.Game.isAvarice(self.ID):
            self.Game.Hand_Deck.addCardtoHand(InsatiableDesire(self.Game, self.ID), self.ID)
        else:
            self.Game.Hand_Deck.addCardtoHand(UnselfishGrace(self.Game, self.ID), self.ID)
        return None


class XIVLuzenTemperance_Token(SVMinion):
    Class, race, name = "Bloodcraft", "", "XIV. Luzen, Temperance"
    mana, attack, health = 4, 4, 4
    index = "SV_Fortune~Bloodcraft~Minion~4~4~4~~XIV. Luzen, Temperance~Uncollectible~Legendary"
    requireTarget, keyWord, description = False, "", "Can't be targeted by enemy effects.While this follower is in play, your leader has the following effects.-Can't take more than 1 damage at a time.-Whenever your leader takes damage, reduce the enemy leader's maximum defense by 3."
    attackAdd, healthAdd = 2, 2
    name_CN = "《节制》·卢泽"

    def __init__(self, Game, ID):
        super().__init__(Game, ID)
        self.auras["Buff Aura"] = BuffAura_XIVLuzenTemperance(self)
        self.marks["Enemy Effect Evasive"] = 1


class XIVLuzenTemperance(SVMinion):
    Class, race, name = "Bloodcraft", "", "XIV. Luzen, Temperance"
    mana, attack, health = 9, 7, 7
    index = "SV_Fortune~Bloodcraft~Minion~9~7~7~~XIV. Luzen, Temperance~Accelerate~Legendary"
    requireTarget, keyWord, description = False, "", "Can't be targeted by enemy effects.While this follower is in play, your leader has the following effects.-Can't take more than 1 damage at a time.-Whenever your leader takes damage, reduce the enemy leader's maximum defense by 3."
    accelerateSpell = XIVLuzenTemperance_Accelerate
    attackAdd, healthAdd = 2, 2
    name_CN = "《节制》·卢泽"

    def __init__(self, Game, ID):
        super().__init__(Game, ID)
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

    def effCanTrig(self):
        if self.willAccelerate() and self.targetExists():
            self.effectViable = "sky blue"
        else:
            self.effectViable = False


class BuffAura_XIVLuzenTemperance(HasAura_toMinion):
    def __init__(self, entity):
        self.entity = entity
        self.signals, self.auraAffected = [], []

    # Minions appearing/disappearing will let the minion reevaluate the aura.
    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.onBoard

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        self.applies(self.entity.Game.heroes[self.entity.ID])

    def applies(self, subject):
        trigger = Trig_XIVLuzenTemperance(subject)
        subject.trigsBoard.append(trigger)
        trigger.connect()
        trigger = Trig_XIVLuzenTemperance_MaxDamage(subject)
        subject.trigsBoard.append(trigger)
        trigger.connect()

    def auraAppears(self):
        self.applies(self.entity.Game.heroes[self.entity.ID])

    def auraDisappears(self):
        for trigger in self.entity.Game.heroes[self.entity.ID].trigsBoard:
            if type(trigger) == Trig_XIVLuzenTemperance:
                self.entity.Game.heroes[self.entity.ID].trigsBoard.remove(trigger)
                break
        for trigger in self.entity.Game.heroes[self.entity.ID].trigsBoard:
            if type(trigger) == Trig_XIVLuzenTemperance_MaxDamage:
                self.entity.Game.heroes[self.entity.ID].trigsBoard.remove(trigger)
                break

    def selfCopy(self, recipientMinion):  # The recipientMinion is the minion that deals the Aura.
        return type(self)(recipientMinion)


class Trig_XIVLuzenTemperance(TrigBoard):
    def __init__(self, entity):
        super().__init__(entity, ["HeroTookDmg", "HeroTook0Dmg"])

    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.onBoard and target == self.entity.Game.heroes[self.entity.ID]

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        self.entity.Game.heroes[3 - self.entity.ID].health_max -= 3
        self.entity.Game.heroes[3 - self.entity.ID].health = min(self.entity.Game.heroes[3 - self.entity.ID].health,
                                                                 self.entity.Game.heroes[3 - self.entity.ID].health_max)


class Trig_XIVLuzenTemperance_MaxDamage(TrigBoard):
    def __init__(self, entity):
        super().__init__(entity, ["BattleDmgHero", "AbilityDmgHero"])

    def canTrig(self, signal, ID, subject, target, number, comment,
                choice=0):  # target here holds the actual target object
        return target == self.entity

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        number[0] = min(1, number[0])


"""Havencraft cards"""


class JeweledBrilliance(SVSpell):
    Class, school, name = "Havencraft", "", "Jeweled Brilliance"
    mana, requireTarget = 1, False,
    index = "SV_Fortune~Havencraft~Spell~1~Jeweled Brilliance"
    description = "Put a random amulet from your deck into your hand."
    name_CN = "宝石的光辉"

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        curGame = self.Game
        if curGame.mode == 0:
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
    index = "SV_Fortune~Havencraft~Minion~2~2~2~~Stalwart Featherfolk~Taunt~Battlecry"
    requireTarget, keyWord, description = False, "Taunt", "Ward. Fanfare: If any allied amulets are in play, restore X defense to your leader. X equals the number of allied amulets in play."
    attackAdd, healthAdd = 2, 2
    name_CN = "刚健的翼人"

    def effCanTrig(self):
        self.effectViable = len(self.Game.amuletsonBoard(self.ID)) > 0

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if len(self.Game.amuletsonBoard(self.ID)) > 0:
            self.restoresHealth(self.Game.heroes[self.ID], len(self.Game.amuletsonBoard(self.ID)))

        return None


class PrismaplumeBird(SVMinion):
    Class, race, name = "Havencraft", "", "Prismaplume Bird"
    mana, attack, health = 2, 3, 1
    index = "SV_Fortune~Havencraft~Minion~2~3~1~~Prismaplume Bird~Deathrattle"
    requireTarget, keyWord, description = False, "", "Last Words: Randomly summon a Summon Pegasus or Pinion Prayer."
    attackAdd, healthAdd = 2, 2
    name_CN = "优雅的丽鸟"

    def __init__(self, Game, ID):
        super().__init__(Game, ID)
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
            self.entity.Game.summon([SummonPegasus(self.entity.Game, self.entity.ID)], (-1, "totheRightEnd"),
                                    self.entity)
        elif e == "P":
            self.entity.Game.summon([PinionPrayer(self.entity.Game, self.entity.ID)], (-1, "totheRightEnd"),
                                    self.entity)


class FourPillarTortoise(SVMinion):
    Class, race, name = "Havencraft", "", "Four-Pillar Tortoise"
    mana, attack, health = 3, 1, 4
    index = "SV_Fortune~Havencraft~Minion~3~1~4~~Four-Pillar Tortoise~Taunt~Battlecry"
    requireTarget, keyWord, description = False, "Taunt", "Ward. Fanfare: Randomly put a 4-play point Havencraft follower or amulet from your deck into your hand."
    attackAdd, healthAdd = 2, 2
    name_CN = "圣柱巨龟"

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        curGame = self.Game
        if curGame.mode == 0:
            if curGame.guides:
                i = curGame.guides.pop(0)
            else:
                minions = [i for i, card in enumerate(curGame.Hand_Deck.decks[self.ID]) if
                           card.type == "Minion" and card.mana == 4]
                i = npchoice(minions) if minions else -1
                curGame.fixedGuides.append(i)
            if i > -1: curGame.Hand_Deck.drawCard(self.ID, i)


class LorenasHolyWater(SVSpell):
    Class, school, name = "Havencraft", "", "Lorena's Holy Water"
    requireTarget, mana = True, 1
    index = "SV_Fortune~Havencraft~Spell~1~Lorena's Holy Water~Uncollectible"
    description = "Restore 2 defense to an ally.Draw a card."
    name_CN = "萝蕾娜的圣水"

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
            self.Game.Hand_Deck.drawCard(self.ID)
        return target


class LorenaIronWilledPriest(SVMinion):
    Class, race, name = "Havencraft", "", "Lorena, Iron-Willed Priest"
    mana, attack, health = 3, 2, 3
    index = "SV_Fortune~Havencraft~Minion~3~2~3~~Lorena, Iron-Willed Priest~Battlecry"
    requireTarget, keyWord, description = False, "", "Fanfare: Put a Lorena's Holy Water into your hand. During your turn, when defense is restored to your leader, if it's the second time this turn, gain the ability to evolve for 0 evolution points."
    attackAdd, healthAdd = 2, 2
    evolveRequireTarget = True
    name_CN = "传教司祭·萝蕾娜"

    def __init__(self, Game, ID):
        super().__init__(Game, ID)
        self.progress = 0
        self.trigsBoard = [Trig_LorenaIronWilledPriest(self), Trig_EndLorenaIronWilledPriest]

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        self.Game.Hand_Deck.addCardtoHand(LorenasHolyWater, self.ID, byType=True)

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
            self.dealsDamage(target, damage)
        return target


class Trig_LorenaIronWilledPriest(TrigBoard):
    def __init__(self, entity):
        super().__init__(entity, ["HeroGetsCured", "AllCured"])

    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
        if signal == "HeroGetsCured":
            return subject.ID == self.entity.ID and self.entity.onBoard
        else:
            return ID == self.entity.ID and self.entity.onBoard

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        self.entity.progress += 1
        if self.entity.progress == 2:
            self.entity.marks["Free Evolve"] += 1


class Trig_EndLorenaIronWilledPriest(TrigBoard):
    def __init__(self, entity):
        super().__init__(entity, ["TurnEnds"])

    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.onBoard and ID == self.entity.ID

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        self.entity.progress = 0


class SarissaLuxflashSpear(SVMinion):
    Class, race, name = "Havencraft", "", "Sarissa, Luxflash Spear"
    mana, attack, health = 3, 2, 2
    index = "SV_Fortune~Havencraft~Minion~3~2~2~~Sarissa, Luxflash Spear~Battlecry~Enhance~Legendary"
    requireTarget, keyWord, description = False, "", "Fanfare: The next time this follower takes damage, reduce that damage to 0.Enhance (6): Randomly summon a copy of 1 of the highest-cost allied followers that had Ward when they were destroyed this match.Whenever an allied follower with Ward is destroyed, gain +2/+2."
    attackAdd, healthAdd = 2, 2
    name_CN = "破暗煌辉·萨莉莎"

    def __init__(self, Game, ID):
        super().__init__(Game, ID)
        self.trigsBoard = [Trig_SarissaLuxflashSpear(self)]

    def getMana(self):
        if self.Game.Manas.manas[self.ID] >= 6:
            return 6
        else:
            return self.mana

    def willEnhance(self):
        return self.Game.Manas.manas[self.ID] >= 6

    def effCanTrig(self):
        self.effectViable = self.willEnhance()

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        self.marks["Next Damage 0"] = 1
        if comment == 6:
            if self.Game.mode == 0:
                t = None
                if self.Game.guides:
                    t = self.Game.cardPool[self.Game.guides.pop(0)]
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
                        for i in range(list(minions.keys())[len(minions) - 1], -1, -1):
                            if i in minions:
                                t = npchoice(minions[i])
                                self.Game.fixedGuides.append(t.index)
                                break
                    else:
                        self.Game.fixedGuides.append(None)
                if t:
                    subject = t(self.Game, self.ID)
                    self.Game.summon([subject], (-1, "totheRightEnd"), self)
        return None


class Trig_SarissaLuxflashSpear(TrigBoard):
    def __init__(self, entity):
        super().__init__(entity, ["MinionDies"])

    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
        return target.ID == self.entity.ID and self.entity.onBoard and target.keyWords["Taunt"] > 0

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        self.entity.buffDebuff(2, 2)


class PriestessofForesight(SVMinion):
    Class, race, name = "Havencraft", "", "Priestess of Foresight"
    mana, attack, health = 4, 2, 5
    index = "SV_Fortune~Havencraft~Minion~4~2~5~~Priestess of Foresight~Battlecry"
    requireTarget, keyWord, description = False, "", "Fanfare: If another allied follower with Ward is in play, destroy an enemy follower. Otherwise, gain Ward."
    attackAdd, healthAdd = 2, 2
    name_CN = "先见的神官"

    def returnTrue(self, choice=0):
        for minion in self.Game.minionsAlive(self.ID):
            if minion != self and minion.keyWords["Taunt"] > 0:
                return self.targetExists(choice) and not self.targets
        return False

    def effCanTrig(self):
        self.effectViable = True

    def targetExists(self, choice=0):
        return self.selectableEnemyMinionExists()

    def targetCorrect(self, target, choice=0):
        if isinstance(target, list): target = target[0]
        return target.type == "Minion" and target.ID != self.ID and target.onBoard

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if target:
            if isinstance(target, list): target = target[0]
            self.Game.killMinion(self, target)
            return target
        hasTaunt = False
        for minion in self.Game.minionsAlive(self.ID):
            if minion != self and minion.keyWords["Taunt"] > 0:
                hasTaunt = True
                break
        if not hasTaunt:
            self.getsStatus("Taunt")
        return None


class HolybrightAltar(Amulet):
    Class, race, name = "Havencraft", "", "Holybright Altar"
    mana = 4
    index = "SV_Fortune~Havencraft~Amulet~4~~Holybright Altar~Battlecry~Countdown~Deathrattle"
    requireTarget, description = False, "Countdown (1) Fanfare: If an allied follower with Ward is in play, subtract 1 from this amulet's Countdown.Last Words: Summon a Holywing Dragon."
    name_CN = "咏唱：纯白祭坛"

    def __init__(self, Game, ID):
        super().__init__(Game, ID)
        self.counter = 1
        self.trigsBoard = [Trig_Countdown(self)]
        self.deathrattles = [Deathrattle_HolybrightAltar(self)]

    def effCanTrig(self):
        for minion in self.Game.minionsAlive(self.ID):
            if minion != self and minion.keyWords["Taunt"] > 0:
                self.effectViable = True
                return

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
        self.entity.Game.summon([HolywingDragon(self.entity.Game, self.entity.ID)], (-1, "totheRightEnd"),
                                self.entity)


class ReverendAdjudicator(SVMinion):
    Class, race, name = "Havencraft", "", "Reverend Adjudicator"
    mana, attack, health = 5, 2, 3
    index = "SV_Fortune~Havencraft~Minion~5~2~3~~Reverend Adjudicator~Taunt~Battlecry"
    requireTarget, keyWord, description = False, "Taunt", "Ward.Fanfare: Restore 2 defense to your leader. Draw a card.During your turn, whenever your leader's defense is restored, summon a Snake Priestess."
    attackAdd, healthAdd = 2, 2
    name_CN = "神域的法王"

    def __init__(self, Game, ID):
        super().__init__(Game, ID)
        self.trigsBoard = [Trig_ReverendAdjudicator(self)]

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        self.restoresHealth(self.Game.heroes[self.ID], 2)
        self.Game.Hand_Deck.drawCard(self.ID)

    def inHandEvolving(self, target=None):
        self.restoresHealth(self.Game.heroes[self.ID], 2)


class Trig_ReverendAdjudicator(TrigBoard):
    def __init__(self, entity):
        super().__init__(entity, ["HeroGetsCured", "AllCured"])

    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
        if signal == "HeroGetsCured":
            return subject.ID == self.entity.ID and self.entity.onBoard
        else:
            return ID == self.entity.ID and self.entity.onBoard

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        self.entity.Game.summon([SnakePriestess(self.entity.Game, self.entity.ID)], (-1, "totheRightEnd"),
                                self.entity)


class SomnolentStrength(Amulet):
    Class, race, name = "Havencraft", "", "Somnolent Strength"
    mana = 2
    index = "SV_Fortune~Havencraft~Amulet~2~~Somnolent Strength~Countdown~Deathrattle~Uncollectible~Legendary"
    requireTarget, description = False, "Countdown (3)At the end of your turn, give +0/+2 to a random allied follower.Last Words: Give -2/-0 to a random enemy follower."
    name_CN = "虚脱的刚腕"

    def __init__(self, Game, ID):
        super().__init__(Game, ID)
        self.counter = 3
        self.trigsBoard = [Trig_Countdown(self), Trig_SomnolentStrength(self)]
        self.deathrattles = [Deathrattle_SomnolentStrength(self)]


class Trig_SomnolentStrength(TrigBoard):
    def __init__(self, entity):
        super().__init__(entity, ["TurnEnds"])

    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
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
                i = npchoice(minions).pos if minions else -1
                curGame.fixedGuides.append(i)
            if i > -1:
                minion = curGame.minions[self.entity.ID][i]
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
                i = npchoice(minions).pos if minions else -1
                curGame.fixedGuides.append(i)
            if i > -1:
                minion = curGame.minions[3 - self.entity.ID][i]
                minion.buffDebuff(-2, 0)


class VIIISofinaStrength_Accelerate(SVSpell):
    Class, school, name = "Havencraft", "", "VIII. Sofina, Strength"
    requireTarget, mana = False, 2
    index = "SV_Fortune~Havencraft~Spell~2~VIII. Sofina, Strength~Accelerate~Uncollectible~Legendary"
    description = "Summon a Somnolent Strength."
    name_CN = "《力量》·索菲娜"

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        self.Game.summon([SomnolentStrength(self.Game, self.ID)], (-1, "totheRightEnd"),
                         self)
        return None


class VIIISofinaStrength(SVMinion):
    Class, race, name = "Havencraft", "", "VIII. Sofina, Strength"
    mana, attack, health = 5, 2, 6
    index = "SV_Fortune~Havencraft~Minion~5~2~6~~VIII. Sofina, Strength~Accelerate~Battlecry~Legendary"
    requireTarget, keyWord, description = False, "", "Accelerate (2): Summon a Somnolent Strength.Fanfare: Give all other allied followers +1/+1 and Ward.While this follower is in play, all allied followers in play and that come into play can't take more than 3 damage at a time."
    accelerateSpell = VIIISofinaStrength_Accelerate
    attackAdd, healthAdd = 2, 2
    name_CN = "《力量》·索菲娜"

    def __init__(self, Game, ID):
        super().__init__(Game, ID)
        self.auras["Buff Aura"] = BuffAura_VIIISofinaStrength(self)

    def getMana(self):
        if self.Game.Manas.manas[self.ID] < self.mana:
            return 2
        else:
            return self.mana

    def willAccelerate(self):
        curMana = self.Game.Manas.manas[self.ID]
        return self.mana > curMana >= 2

    def effCanTrig(self):
        if self.willAccelerate() and self.targetExists():
            self.effectViable = "sky blue"
        else:
            self.effectViable = False

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        for minion in self.Game.minionsonBoard(self.ID, self):
            minion.buffDebuff(1, 1)
            minion.getsStatus("Taunt")
        return None


class BuffAura_VIIISofinaStrength(HasAura_toMinion):
    def __init__(self, entity):
        self.entity = entity
        self.signals, self.auraAffected = ["MinionAppears"], []

    # All minions appearing on the same side will be subject to the buffAura.
    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.onBoard and subject.ID == self.entity.ID

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        self.applies(signal, subject)

    def applies(self, signal, subject):
        trigger = Trig_VIIISofinaStrength_MaxDamage(subject)
        subject.trigsBoard.append(trigger)
        trigger.connect()

    def auraAppears(self):
        for minion in self.entity.Game.minionsonBoard(self.entity.ID):
            self.applies("MinionAppears", minion)

    def auraDisappears(self):
        for minion in self.entity.Game.minionsonBoard(self.entity.ID):
            for trigger in self.entity.Game.heroes[self.entity.ID].trigsBoard:
                if type(trigger) == Trig_VIIISofinaStrength_MaxDamage:
                    self.entity.Game.heroes[self.entity.ID].trigsBoard.remove(trigger)
                    break

    def selfCopy(self, recipient):
        return type(self)(recipient)


class Trig_VIIISofinaStrength_MaxDamage(TrigBoard):
    def __init__(self, entity):
        super().__init__(entity, ["BattleDmgHero", "BattleDmgMinion", "AbilityDmgHero", "AbilityDmgMinion"])

    def canTrig(self, signal, ID, subject, target, number, comment,
                choice=0):  # target here holds the actual target object
        return target == self.entity

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        number[0] = min(3, number[0])


class PuresongPriest_Accelerate(SVSpell):
    Class, school, name = "Havencraft", "", "Puresong Priest"
    requireTarget, mana = False, 1
    index = "SV_Fortune~Havencraft~Spell~1~Puresong Priest~Accelerate~Uncollectible"
    description = "Restore 1 defense to your leader. If an allied follower with Ward is in play, draw a card."
    name_CN = "光明神父"

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        self.restoresHealth(self.Game.heroes[self.ID], 1)
        hasTaunt = False
        for minion in self.Game.minionsAlive(self.ID):
            if minion != self and minion.keyWords["Taunt"] > 0:
                hasTaunt = True
                break
        if hasTaunt:
            self.Game.Hand_Deck.drawCard(self.ID)
        return None


class PuresongPriest(SVMinion):
    Class, race, name = "Havencraft", "", "Puresong Priest"
    mana, attack, health = 6, 5, 5
    index = "SV_Fortune~Havencraft~Minion~6~5~5~~Puresong Priest~Accelerate~Battlecry"
    requireTarget, keyWord, description = False, "", "Accelerate (1): Restore 1 defense to your leader. If an allied follower with Ward is in play, draw a card.Fanfare: Restore 4 defense to all allies."
    accelerateSpell = PuresongPriest_Accelerate
    attackAdd, healthAdd = 2, 2
    name_CN = "光明神父"

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

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        chars = self.Game.charsAlive(self.ID)
        self.restoresAOE(chars, 4)
        return None


"""Portalcraft cards"""


class ArtifactScan(SVSpell):
    Class, school, name = "Portalcraft", "", "Artifact Scan"
    requireTarget, mana = False, 1
    index = "SV_Fortune~Portalcraft~Spell~0~Artifact Scan"
    description = "Put copies of 2 random allied Artifact cards with different names destroyed this match into your hand. Then, if at least 6 allied Artifact cards with different names have been destroyed this match, change their costs to 0."
    name_CN = "创造物扫描"

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if self.Game.mode == 0:
            types = None
            if self.Game.guides:
                types = self.Game.guides.pop(0)
                if types:
                    types = list(types)
            else:
                indices = self.Game.Counters.artifactsDiedThisGame[self.ID].keys()
                if len(indices) == 0:
                    self.Game.fixedGuides.append(None)
                    types = None
                elif len(indices) == 1:
                    self.Game.fixedGuides.append(tuple([indices[0]]))
                    types = [indices[0]]
                else:
                    types = []
                    while len(types) < 2:
                        t = npchoice(indices)
                        if t not in types:
                            types.append(t)
                    self.Game.fixedGuides.append(tuple(types))
            if types:
                minions = []
                for t in types:
                    minions.append(self.Game.cardPool[t](self.Game, self.ID))
                self.Game.Hand_Deck.addCardtoHand(minions, self.ID)
                if len(self.Game.Counters.artifactsDiedThisGame[self.ID]) >= 6:
                    for m in minions:
                        ManaMod(m, changeby=0, changeto=0).applies()


class RoboticEngineer(SVMinion):
    Class, race, name = "Portalcraft", "", "Robotic Engineer"
    mana, attack, health = 1, 1, 1
    index = "SV_Fortune~Portalcraft~Minion~1~1~1~~Robotic Engineer~Deathrattle"
    requireTarget, keyWord, description = False, "", "Last Words: Put a Paradigm Shift into your hand."
    attackAdd, healthAdd = 2, 2
    name_CN = "机械技师"

    def __init__(self, Game, ID):
        super().__init__(Game, ID)
        self.deathrattles = [Deathrattle_RoboticEngineer(self)]


class Deathrattle_RoboticEngineer(Deathrattle_Minion):
    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        self.entity.Game.Hand_Deck.addCardtoHand(ParadigmShift, self.entity.ID, byType=True)


class MarionetteExpert(SVMinion):
    Class, race, name = "Portalcraft", "", "Marionette Expert"
    mana, attack, health = 2, 2, 2
    index = "SV_Fortune~Portalcraft~Minion~2~2~2~~Marionette Expert~Deathrattle"
    requireTarget, keyWord, description = False, "", "Last Words: Put a Puppet into your hand."
    attackAdd, healthAdd = 2, 2
    name_CN = "持偶者"

    def __init__(self, Game, ID):
        super().__init__(Game, ID)
        self.deathrattles = [Deathrattle_MarionetteExpert(self)]


class Deathrattle_MarionetteExpert(Deathrattle_Minion):
    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        self.entity.Game.Hand_Deck.addCardtoHand(Puppet, self.entity.ID, byType=True)


class CatTuner(SVMinion):
    Class, race, name = "Portalcraft", "", "Cat Tuner"
    mana, attack, health = 2, 1, 3
    index = "SV_Fortune~Portalcraft~Minion~2~1~3~~Cat Tuner"
    requireTarget, keyWord, description = False, "", "At the end of your turn, put a copy of a random allied follower destroyed this match that costs X play points into your hand. X equals your remaining play points."
    attackAdd, healthAdd = 2, 2
    name_CN = "巧猫调律师"

    def __init__(self, Game, ID):
        super().__init__(Game, ID)
        self.trigsBoard = [Trig_CatTuner(self)]


class Trig_CatTuner(TrigBoard):
    def __init__(self, entity):
        super().__init__(entity, ["TurnEnds"])

    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.onBoard and ID == self.entity.ID

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        mana = self.entity.Game.Manas.manas[self.entity.ID]
        curGame = self.entity.Game
        if curGame.mode == 0:
            t = None
            if curGame.guides:
                t = curGame.cardPool[curGame.guides.pop(0)]
            else:
                indices = curGame.Counters.minionsDiedThisGame[ID]
                minions = {}
                for index in indices:
                    try:
                        minions[curGame.cardPool[index].mana].append(curGame.cardPool[index])
                    except:
                        minions[curGame.cardPool[index].mana] = [curGame.cardPool[index]]
                if mana in minions:
                    t = npchoice(minions[mana])
                curGame.fixedGuides.append(t.index)
            if t:
                card = t(curGame, ID)
                curGame.Hand_Deck.addCardtoHand(card, self.entity.ID)
                return subject


class SteelslashTiger(SVMinion):
    Class, race, name = "Portalcraft", "", "Steelslash Tiger"
    mana, attack, health = 3, 1, 5
    index = "SV_Fortune~Portalcraft~Minion~3~1~5~~Steelslash Tiger~Rush~Battlecry"
    requireTarget, keyWord, description = False, "Rush", "Rush. Fanfare: Gain +X/+0. X equals the number of allied Artifact cards with different names destroyed this match."
    attackAdd, healthAdd = 2, 2
    name_CN = "钢之猛虎"

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        n = len(self.Game.Counters.artifactsDiedThisGame[self.ID])
        self.buffDebuff(n, 0)


class WheelofMisfortune(Amulet):
    Class, race, name = "Portalcraft", "", "Wheel of Misfortune"
    mana = 3
    index = "SV_Fortune~Portalcraft~Amulet~3~~Wheel of Misfortune~Countdown~Uncollectible~Legendary"
    requireTarget, description = False, "Countdown (3) At the start of your turn, randomly activate 1 of the following effects.-Add 1 to the cost of all cards in your hand until the end of the turn.-Give -2/-2 to all allied followers.-Summon an enemy Analyzing Artifact.(The same effect will not activate twice.)"
    name_CN = "惨祸的圆环"

    def __init__(self, Game, ID):
        super().__init__(Game, ID)
        self.counter = 3
        self.trigsBoard = [Trig_WheelofMisfortune(self), Trig_Countdown(self)]
        self.progress = 30


class Trig_WheelofMisfortune(TrigBoard):
    def __init__(self, entity):
        super().__init__(entity, ["TurnStarts"])

    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.onBoard and ID == self.entity.ID

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        es = [2, 3, 5]
        ies = []
        for ie in es:
            if self.entity.progress % ie == 0:
                ies.append(ie)
        i = 2
        curGame = self.entity.Game
        if curGame.mode == 0:
            if curGame.guides:
                i, e = curGame.guides.pop(0)
            else:
                i = np.random.choice(ies)
                curGame.fixedGuides.append((i, ""))
                self.entity.progress /= i
        if i == 2:
            tempAura = ManaEffect_WheelofMisfortune(self.entity.Game, self.entity.ID)
            self.entity.Game.Manas.CardAuras.append(tempAura)
            tempAura.auraAppears()
        elif i == 3:
            for minion in self.entity.Game.minionsonBoard(self.entity.ID):
                minion.buffDebuff(-2, -2)
        elif i == 5:
            self.entity.Game.summon([AnalyzingArtifact(self.entity.Game, 3 - self.entity.ID)], (-11, "totheRightEnd"),
                                    self.entity)


class ManaEffect_WheelofMisfortune(TempManaEffect):
    def __init__(self, Game, ID):
        self.Game, self.ID = Game, ID
        self.changeby, self.changeto = +1, -1
        self.temporary = True
        self.auraAffected = []

    def applicable(self, target):
        return target.ID == self.ID

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


class XSlausWheelofFortune(SVMinion):
    Class, race, name = "Portalcraft", "", "X. Slaus, Wheel of Fortune"
    mana, attack, health = 3, 2, 3
    index = "SV_Fortune~Portalcraft~Minion~3~2~3~~X. Slaus, Wheel of Fortune~Battlecry~Legendary"
    requireTarget, keyWord, description = False, "", "Fanfare: If Resonance is active for you, summon an enemy Wheel of Misfortune and banish this follower. At the start of your opponent's turn, if Resonance is active for you, gain +1/+1 and destroy a random enemy follower."
    attackAdd, healthAdd = 2, 2
    name_CN = "《命运之轮》·斯洛士"

    def __init__(self, Game, ID):
        super().__init__(Game, ID)
        self.trigsBoard = [Trig_XSlausWheelofFortune(self)]

    def effCanTrig(self):
        self.effectViable = self.Game.isResonance(self.ID)

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if self.Game.isResonance(self.ID):
            self.Game.summon([WheelofMisfortune(self.Game, 3 - self.ID)], (-11, "totheRightEnd"),
                             self)
            self.Game.banishMinion(self, self)


class Trig_XSlausWheelofFortune(TrigBoard):
    def __init__(self, entity):
        super().__init__(entity, ["TurnStarts"])

    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.onBoard and ID != self.entity.ID

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        if self.entity.Game.isResonance(self.entity.ID):
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
                        curGame.fixedGuides.append((enemy.pos, enemy.type + str(enemy.ID)))
                    else:
                        curGame.fixedGuides.append((0, ''))
                if enemy:
                    self.entity.Game.banishMinion(self.entity, enemy)
            self.entity.buffDebuff(1, 1)


class InvertedManipulation(SVSpell):
    Class, school, name = "Portalcraft", "", "Inverted Manipulation"
    requireTarget, mana = False, 3
    index = "SV_Fortune~Portalcraft~Spell~3~Inverted Manipulation"
    description = "Put a Puppet into your hand.Give your leader the following effect until the end of the turn: Whenever an allied Puppet comes into play, deal 2 damage to a random enemy follower. If no enemy followers are in play, deal 2 damage to the enemy leader instead. (This effect is not stackable.)"
    name_CN = "人偶的反噬"

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        self.Game.Hand_Deck.addCardtoHand(Puppet, self.ID, byType=True)
        trigger = Trig_InvertedManipulation(self.Game.heroes[self.ID])
        for t in self.Game.heroes[self.ID].trigsBoard:
            if type(t) == type(trigger):
                return
        self.Game.heroes[self.ID].trigsBoard.append(trigger)
        trigger.connect()
        return None


class Trig_InvertedManipulation(TrigBoard):
    def __init__(self, entity):
        super().__init__(entity, ["MinionSummoned", "TurnEnds"])

    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
        if signal == "TurnEnds":
            return self.entity.onBoard and ID != self.entity.ID
        return self.entity.onBoard and subject.ID == self.entity.ID and subject.name == "Puppet"

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        if signal == "TurnEnds":
            for trig in self.entity.trigsBoard:
                if type(trig) == Trig_InvertedManipulation:
                    trig.disconnect()
                    self.entity.trigsBoard.remove(trig)
            return
        enemy = self.entity.Game.heroes[3 - self.entity.ID]
        if len(self.entity.Game.minionsonBoard(3 - self.entity.ID)) > 0:
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
                        curGame.fixedGuides.append((enemy.pos, enemy.type + str(enemy.ID)))
                    else:
                        curGame.fixedGuides.append((0, ''))
        if enemy:
            self.entity.dealsDamage(enemy, 2)


class PowerliftingPuppeteer(SVMinion):
    Class, race, name = "Portalcraft", "", "Powerlifting Puppeteer"
    mana, attack, health = 4, 3, 3
    index = "SV_Fortune~Portalcraft~Minion~4~3~3~~Powerlifting Puppeteer~Battlecry"
    requireTarget, keyWord, description = False, "", "Fanfare: Put 2 Puppets into your hand. At the end of your turn, give +1/+1 to all Puppets in your hand."
    attackAdd, healthAdd = 2, 2
    name_CN = "劲力操偶师"

    def __init__(self, Game, ID):
        super().__init__(Game, ID)
        self.trigsBoard = [Trig_PowerliftingPuppeteer(self)]

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        self.Game.Hand_Deck.addCardtoHand([Puppet for i in range(2)], self.ID, byType=True)


class Trig_PowerliftingPuppeteer(TrigBoard):
    def __init__(self, entity):
        super().__init__(entity, ["TurnEnds"])

    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.onBoard and ID == self.entity.ID

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        for card in self.entity.Game.Hand_Deck.hands[self.entity.ID]:
            if card.type == "Minion" and card.name == "Puppet":
                card.buffDebuff(1, 1)


class DimensionDominator(SVMinion):
    Class, race, name = "Portalcraft", "", "Dimension Dominator"
    mana, attack, health = 4, 4, 3
    index = "SV_Fortune~Portalcraft~Minion~4~4~3~~Dimension Dominator~Battlecry~Legendary"
    requireTarget, keyWord, description = True, "", "Fanfare: Give a follower in your hand Fanfare - Recover 2 play points."
    attackAdd, healthAdd = 2, 2
    name_CN = "次元支配者"

    def targetExists(self, choice=0):
        return not self.Game.Hand_Deck.noMinionsinHand(self.ID, self)

    def targetCorrect(self, target, choice=0):
        if isinstance(target, list): target = target[0]
        return target.ID == self.ID and target.inHand and target != self and target.type == "Minion"

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if target:
            if isinstance(target, list): target = target[0]
            target.appearResponse.append(self.whenAppears)

    def whenAppears(self):
        self.Game.Manas.restoreManaCrystal(2, self.ID)

    def inHandEvolving(self, target=None):
        trigger = Trig_DimensionDominator(self.Game.heroes[self.ID])
        for t in self.Game.heroes[self.ID].trigsBoard:
            if type(t) == type(trigger):
                return
        self.Game.heroes[self.ID].trigsBoard.append(trigger)
        trigger.connect()


class Trig_DimensionDominator(TrigBoard):
    def __init__(self, entity):
        super().__init__(entity, ["MinionSummoned", "TurnEnds"])
        self.progress = 1

    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
        if signal == "TurnEnds":
            return self.entity.onBoard and ID != self.entity.ID
        return self.entity.onBoard and subject.ID == self.entity.ID

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        if signal == "TurnEnds":
            self.progress = 1
        if self.progress > 0:
            self.entity.Game.Manas.restoreManaCrystal(1, self.entity.ID)
            self.progress -= 1


class MindSplitter(SVMinion):
    Class, race, name = "Portalcraft", "", "Mind Splitter"
    mana, attack, health = 5, 4, 4
    index = "SV_Fortune~Portalcraft~Minion~5~4~4~~Mind Splitter~Battlecry"
    requireTarget, keyWord, description = False, "", "Fanfare: Recover X play points. X equals the number of allied followers in play. At the end of your turn, if you have at least 1 play point, draw a card. Then, if you have at least 3 play points, subtract 2 from its cost."
    attackAdd, healthAdd = 2, 2
    name_CN = "神志分割者"

    def __init__(self, Game, ID):
        super().__init__(Game, ID)
        self.trigsBoard = [Trig_MindSplitter(self)]

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        n = len(self.Game.minionsonBoard(self.ID))
        self.Game.Manas.restoreManaCrystal(n, self.ID)


class Trig_MindSplitter(TrigBoard):
    def __init__(self, entity):
        super().__init__(entity, ["TurnEnds"])

    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.onBoard and ID == self.entity.ID

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        mana = self.entity.Game.Manas.manas[self.entity.ID]
        if mana >= 1:
            card = self.entity.Game.Hand_Deck.drawCard(self.entity.ID)[0]
            if mana >= 3:
                ManaMod(card, changeby=-2, changeto=-1).applies()


class PopGoesthePoppet(SVSpell):
    Class, school, name = "Portalcraft", "", "Pop Goes the Poppet"
    requireTarget, mana = True, 5
    index = "SV_Fortune~Portalcraft~Spell~5~Pop Goes the Poppet"
    description = "Destroy an enemy follower. Then deal X damage to a random enemy follower. X equals the destroyed follower's attack."
    name_CN = "人偶的闪击"

    def available(self):
        return self.selectableEnemyMinionExists()

    def targetCorrect(self, target, choice=0):
        if isinstance(target, list): target = target[0]
        return target.type == "Minion" and target.ID != self.ID and target.onBoard

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if target:
            if isinstance(target, list): target = target[0]
            damage = (target.attack + self.countSpellDamage()) * (2 ** self.countDamageDouble())
            self.Game.killMinion(self, target)
            if len(self.Game.minionsAlive(3 - self.ID)) > 0:
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
                            curGame.fixedGuides.append((enemy.pos, enemy.type + str(enemy.ID)))
                        else:
                            curGame.fixedGuides.append((0, ''))
                    if enemy:
                        self.dealsDamage(enemy, damage)
            return target


"""DLC cards"""


class ArchangelofEvocation(SVMinion):
    Class, race, name = "Neutral", "", "Archangel of Evocation"
    mana, attack, health = 5, 3, 5
    index = "SV_Fortune~Neutral~Minion~5~3~5~~Archangel of Evocation~Taunt~Battlecry"
    requireTarget, keyWord, description = False, "Taunt", "Ward. Fanfare: Add 1 to the cost of all non-follower cards in your opponent's hand until the start of your next turn."
    attackAdd, healthAdd = 2, 2
    name_CN = "降罪之大天使"

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        self.Game.Manas.CardAuras_Backup.append(ManaEffect_ArchangelofEvocation(self.Game, 3 - self.ID))
        return None

    def inHandEvolving(self, target=None):
        self.Game.heroes[self.ID].health_max += 5
        self.restoresHealth(self.Game.heroes[self.ID], 5)


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
    index = "SV_Fortune~Forestcraft~Minion~3~1~5~~Aerin, Forever Brilliant~Legendary"
    requireTarget, keyWord, description = False, "", "Fanfare: Put a random follower with Accelerate from your deck into your hand. Whenever you play a card using its Accelerate effect, deal 2 damage to all enemies."
    attackAdd, healthAdd = 2, 2
    name_CN = "恒久的光辉·艾琳"

    def __init__(self, Game, ID):
        super().__init__(Game, ID)
        self.trigsBoard = [Trig_AerinForeverBrilliant(self)]

    def inHandEvolving(self, target=None):
        curGame = self.Game
        if curGame.mode == 0:
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
        super().__init__(entity, ["AccelerateBeenPlayed"])

    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
        return subject.ID == self.entity.ID and self.entity.onBoard

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        self.entity.restoresHealth(self.entity.Game.heroes[self.entity.ID], 2)
        self.entity.Game.restoreEvolvePoint(self.entity.ID)
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
        super().__init__(entity, ["TurnEnds"])

    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
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
    index = "SV_Fortune~Forestcraft~Minion~4~3~4~~Furious Mountain Deity~Enhance~Battlecry"
    requireTarget, keyWord, description = False, "", "Fanfare: Enhance (7) - Gain +2/+2 and Rush. Strike: Gain +1/+0."
    attackAdd, healthAdd = 2, 2
    name_CN = "震怒的山神"

    def __init__(self, Game, ID):
        super().__init__(Game, ID)
        self.trigsBoard = [Trig_FuriousMountainDeity(self)]

    def getMana(self):
        if self.Game.Manas.manas[self.ID] >= 7:
            return 7
        else:
            return self.mana

    def willEnhance(self):
        return self.Game.Manas.manas[self.ID] >= 7

    def effCanTrig(self):
        self.effectViable = self.willEnhance()

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if comment == 7:
            self.buffDebuff(2, 2)
            self.getsStatus("Rush")
        return target


class Trig_FuriousMountainDeity(TrigBoard):
    def __init__(self, entity):
        super().__init__(entity, ["MinionAttackingMinion", "MinionAttackingHero"])

    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.onBoard and subject.ID == self.entity.ID and subject == self.entity

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        self.entity.buffDebuff(1, 0)


class DeepwoodAnomaly(SVMinion):
    Class, race, name = "Forestcraft", "", "Deepwood Anomaly"
    mana, attack, health = 8, 8, 8
    index = "SV_Fortune~Forestcraft~Minion~8~8~8~~Deepwood Anomaly~Battlecry~Legendary"
    requireTarget, keyWord, description = False, "", "Fanfare: Enhance (7) - Gain +2/+2 and Rush. Strike: Gain +1/+0."
    attackAdd, healthAdd = 2, 2
    name_CN = "森林深处的异种"

    def __init__(self, Game, ID):
        super().__init__(Game, ID)
        self.trigsBoard = [Trig_DeepwoodAnomaly(self)]


class Trig_DeepwoodAnomaly(TrigBoard):
    def __init__(self, entity):
        super().__init__(entity, ["MinionAttackingHero"])

    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.onBoard and subject.ID == self.entity.ID and target.ID != self.entity.ID and subject == self.entity

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        hero = self.entity.Game.heroes[3 - self.entity.ID]
        self.entity.dealsDamage(hero, hero.health)


class LifeBanquet(SVSpell):
    Class, school, name = "Forestcraft", "", "Life Banquet"
    requireTarget, mana = False, 3
    index = "SV_Fortune~Forestcraft~Spell~3~Life Banquet"
    description = "Draw 2 cards. If at least 2 other cards were played this turn, summon a Furious Mountain Deity. Then, if at least 8 other cards were played this turn, summon 2 Deepwood Anomalies."
    name_CN = "生命的盛宴"

    def effCanTrig(self):
        self.effectViable = self.Game.combCards(self.ID) >= 2

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        self.Game.Hand_Deck.drawCard(self.ID)
        self.Game.Hand_Deck.drawCard(self.ID)
        if self.Game.combCards(self.ID) >= 2:
            self.Game.summon([FuriousMountainDeity(self.Game, self.ID)], (-1, "totheRightEnd"),
                             self)
            if self.Game.combCards(self.ID) >= 8:
                self.Game.summon([DeepwoodAnomaly(self.Game, self.ID)], (-1, "totheRightEnd"),
                                 self)
        return target


class IlmisunaDiscordHawker(SVMinion):
    Class, race, name = "Swordcraft", "Officer", "Ilmisuna, Discord Hawker"
    mana, attack, health = 2, 2, 2
    index = "SV_Fortune~Swordcraft~Minion~2~2~2~Officer~Ilmisuna, Discord Hawker~Battlecry"
    requireTarget, keyWord, description = False, "", "Fanfare: Rally (15) - Recover 1 evolution point."
    attackAdd, healthAdd = 2, 2
    evolveRequireTarget = True
    name_CN = "动乱商人·伊尔米斯娜"

    def evolveTargetExists(self, choice=0):
        return self.selectableEnemyMinionExists()

    def evolveTargetCorrect(self, target, choice=0):
        if isinstance(target, list): target = target[0]
        return target.type == "Minion" and target.onBoard and target.ID != self.ID

    def effCanTrig(self):
        self.effectViable = self.Game.Counters.numMinionsSummonedThisGame[self.ID] >= 15

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if self.Game.Counters.numMinionsSummonedThisGame[self.ID] >= 15:
            self.Game.restoreEvolvePoint(self.ID)
        return None

    def inHandEvolving(self, target=None):
        if target:
            if isinstance(target, list): target = target[0]
            self.dealsDamage(target, len(self.Game.minionsonBoard[self.ID]))
        return target


class AlyaskaWarHawker(SVMinion):
    Class, race, name = "Swordcraft", "Commander", "Alyaska, War Hawker"
    mana, attack, health = 4, 4, 4
    index = "SV_Fortune~Swordcraft~Minion~4~4~4~Commander~Alyaska, War Hawker~Legendary"
    requireTarget, keyWord, description = False, "", "Reduce damage from effects to 0. When an allied Officer follower comes into play, gain the ability to evolve for 0 evolution points."
    attackAdd, healthAdd = 2, 2
    name_CN = "战争商人·阿尔亚斯卡"

    def __init__(self, Game, ID):
        super().__init__(Game, ID)
        self.trigsBoard = [Trig_AlyaskaWarHawker(self)]
        self.marks["Enemy Effect Damage Immune"] = 1

    def inHandEvolving(self, target=None):
        card = ExterminusWeapon(self.Game, self.ID)
        self.Game.Hand_Deck.addCardtoHand(card, self.ID)
        ManaMod(card, changeby=-self.Game.Counters.evolvedThisGame[self.ID], changeto=-1).applies()


class Trig_AlyaskaWarHawker(TrigBoard):
    def __init__(self, entity):
        super().__init__(entity, ["MinionSummoned"])

    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.onBoard and subject.ID == self.entity.ID and subject != self.entity and "Officer" in subject.race

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        self.entity.marks["Free Evolve"] += 1


class ExterminusWeapon(SVMinion):
    Class, race, name = "Swordcraft", "Commander", "Exterminus Weapon"
    mana, attack, health = 8, 6, 6
    index = "SV_Fortune~Swordcraft~Minion~8~6~6~Commander~Exterminus Weapon~Battlecry~Deathrattle~Uncollectible~Legendary"
    requireTarget, keyWord, description = True, "", "Fanfare: Destroy 2 enemy followers. Last Words: Deal 4 damage to the enemy leader."
    attackAdd, healthAdd = 2, 2
    name_CN = "终战兵器"

    def __init__(self, Game, ID):
        super().__init__(Game, ID)
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
        self.entity.dealsDamage(self.entity.Game.heroes[3 - self.entity.ID], 4)


class RunieResoluteDiviner(SVMinion):
    Class, race, name = "Runecraft", "", "Runie, Resolute Diviner"
    mana, attack, health = 2, 1, 2
    index = "SV_Fortune~Runecraft~Minion~2~1~2~~Runie, Resolute Diviner~Spellboost~Battlecry~Legendary"
    requireTarget, keyWord, description = False, "", "Fanfare: Spellboost the cards in your hand 1 time. If this card has been Spellboosted at least 1 time, draw a card. Then, if it has been at least 4 times, deal 3 damage to a random enemy follower. Then, if it has been at least 7 times, deal 3 damage to the enemy leader and restore 3 defense to your leader. Then, if it has been at least 10 times, put 3 Runie, Resolute Diviners into your hand."
    attackAdd, healthAdd = 2, 2
    name_CN = "决意预言者·露妮"

    def __init__(self, Game, ID):
        super().__init__(Game, ID)
        self.trigsHand = [Trig_Spellboost(self)]
        self.progress = 0

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        self.Game.sendSignal("Spellboost", self.ID, self, None, 0, "", choice)
        if self.progress >= 1:
            self.Game.Hand_Deck.drawCard(self.ID)
            if self.progress >= 4:
                curGame = self.Game
                if curGame.mode == 0:
                    if curGame.guides:
                        i = curGame.guides.pop(0)
                    else:
                        minions = curGame.minionsAlive(3 - self.ID)
                        i = npchoice(minions).pos if minions else -1
                        curGame.fixedGuides.append(i)
                    if i > -1:
                        self.dealsDamage(curGame.minions[3 - self.ID][i], 3)
                if self.progress >= 7:
                    self.dealsDamage(self.Game.heroes[3 - self.ID], 3)
                    self.restoresHealth(self.Game.heroes[self.ID], 3)
                    if self.progress >= 10:
                        self.Game.Hand_Deck.addCardtoHand([RunieResoluteDiviner] * 3, self.ID, byType=True,
                                                          creator=type(self))


class AlchemicalCraftschief_Accelerate(SVSpell):
    Class, school, name = "Runecraft", "", "Alchemical Craftschief"
    requireTarget, mana = False, 2
    index = "SV_Fortune~Runecraft~Spell~2~Alchemical Craftschief~Accelerate~Uncollectible"
    description = "Summon an Earth Essence. Put a 7-play point Alchemical Craftschief (without Accelerate) into your hand and subtract X from its cost. X equals the number of allied Earth Sigil amulets in play."
    name_CN = "矮人工房长"

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        self.Game.summon(EarthEssence(self.Game, self.ID), -1, self)
        n = len(self.Game.earthsonBoard(self.ID))
        card = AlchemicalCraftschief_Token(self.Game, self.ID)
        self.Game.Hand_Deck.addCardtoHand(card, self.ID, creator=type(self))
        ManaMod(card, changeby=-n, changeto=-1).applies()
        return None


class AlchemicalCraftschief_Token(SVMinion):
    Class, race, name = "Runecraft", "", "Alchemical Craftschief"
    mana, attack, health = 7, 4, 4
    index = "SV_Fortune~Runecraft~Minion~7~4~4~~Alchemical Craftschief~Taunt~Battlecry~Uncollectible"
    requireTarget, keyWord, description = True, "Taunt", "Accelerate (2): Summon an Earth Essence. Put a 7-play point Alchemical Craftschief (without Accelerate) into your hand and subtract X from its cost. X equals the number of allied Earth Sigil amulets in play.Ward.Fanfare: Deal 4 damage to an enemy."
    attackAdd, healthAdd = 2, 2
    name_CN = "矮人工房长"

    def targetCorrect(self, target, choice=0):
        if isinstance(target, list): target = target[0]
        return target.type in ["Minion", "Hero"] and target.ID != self.ID and target.onBoard

    def targetExists(self, choice=0):
        return self.selectableEnemyExists()

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if target:
            if isinstance(target, list): target = target[0]
            self.dealsDamage(target, 4)
        return target


class AlchemicalCraftschief(SVMinion):
    Class, race, name = "Runecraft", "", "Alchemical Craftschief"
    mana, attack, health = 8, 4, 4
    index = "SV_Fortune~Runecraft~Minion~8~4~4~~Alchemical Craftschief~Taunt~Battlecry~Accelerate"
    requireTarget, keyWord, description = True, "Taunt", "Accelerate (2): Summon an Earth Essence. Put a 7-play point Alchemical Craftschief (without Accelerate) into your hand and subtract X from its cost. X equals the number of allied Earth Sigil amulets in play.Ward.Fanfare: Deal 4 damage to an enemy."
    accelerateSpell = AlchemicalCraftschief_Accelerate
    attackAdd, healthAdd = 2, 2
    name_CN = "矮人工房长"

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

    def effCanTrig(self):
        if self.willAccelerate() and self.targetExists():
            self.effectViable = "sky blue"
        else:
            self.effectViable = False

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
        return target


class WhitefrostWhisper(SVSpell):
    Class, school, name = "Dragoncraft", "", "Whitefrost Whisper"
    requireTarget, mana = True, 2
    index = "SV_Fortune~Dragoncraft~Spell~2~Whitefrost Whisper~Uncollectible~Legendary"
    description = "Select an enemy follower and destroy it if it is already damaged. If it has not been damaged, deal 1 damage instead."
    name_CN = "银冰吐息"

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
            else:
                damage = (1 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
                self.dealsDamage(target, damage)
        return target


class FileneAbsoluteZero(SVMinion):
    Class, race, name = "Dragoncraft", "", "Filene, Absolute Zero"
    mana, attack, health = 3, 1, 3
    index = "SV_Fortune~Dragoncraft~Minion~3~1~3~~Filene, Absolute Zero~Battlecry~Legendary"
    requireTarget, keyWord, description = False, "", "Fanfare: Draw a card if Overflow is active for you."
    attackAdd, healthAdd = 2, 2
    name_CN = "绝对零度·菲琳"

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        minions = self.Game.minionsonBoard(3 - self.ID)
        self.dealsAOE(minions, [1 for obj in minions])
        self.Game.Hand_Deck.addCardtoHand(WhitefrostWhisper, self.ID, byType=True, creator=type(self))

    def inHandEvolving(self, target=None):
        card = WhitefrostWhisper(self.Game, self.ID)
        self.Game.Hand_Deck.addCardtoHand(card, self.ID)
        ManaMod(card, changeby=0, changeto=1).applies()


class EternalWhale(SVMinion):
    Class, race, name = "Dragoncraft", "", "Eternal Whale"
    mana, attack, health = 6, 5, 7
    index = "SV_Fortune~Dragoncraft~Minion~6~5~7~~Eternal Whale~Taunt"
    requireTarget, keyWord, description = False, "Taunt", "Ward.When this follower comes into play, deal 2 damage to the enemy leader.When this follower leaves play, put four 1-play point Eternal Whales into your deck. (Transformation doesn't count as leaving play.)"
    attackAdd, healthAdd = 2, 2
    name_CN = "永恒巨鲸"

    def __init__(self, Game, ID):
        super().__init__(Game, ID)
        self.appearResponse = [self.whenAppears]
        self.disappearResponse = [self.whenDisppears]

    def whenAppears(self):
        self.dealsDamage(self.Game.heroes[3 - self.ID], 2)

    def whenDisppears(self):
        cards = [EternalWhale_Token(self.Game, self.ID) for i in range(4)]
        self.Game.Hand_Deck.shuffleintoDeck(cards, creator=self)


class EternalWhale_Token(SVMinion):
    Class, race, name = "Dragoncraft", "", "Eternal Whale"
    mana, attack, health = 1, 5, 7
    index = "SV_Fortune~Dragoncraft~Minion~1~5~7~~Eternal Whale~Taunt~Uncollectible"
    requireTarget, keyWord, description = False, "Taunt", "Ward.When this follower comes into play, deal 2 damage to the enemy leader.When this follower leaves play, put four 1-play point Eternal Whales into your deck. (Transformation doesn't count as leaving play.)"
    attackAdd, healthAdd = 2, 2
    name_CN = "永恒巨鲸"

    def __init__(self, Game, ID):
        super().__init__(Game, ID)
        self.appearResponse = [self.whenAppears]
        self.disappearResponse = [self.whenDisppears]

    def whenAppears(self):
        self.dealsDamage(self.Game.heroes[3 - self.ID], 2)

    def whenDisppears(self):
        cards = [EternalWhale_Token(self.Game, self.ID) for i in range(4)]
        self.Game.Hand_Deck.shuffleintoDeck(cards, creator=self)


class ForcedResurrection(SVSpell):
    Class, school, name = "Shadowcraft", "", "Forced Resurrection"
    requireTarget, mana = True, 2
    index = "SV_Fortune~Shadowcraft~Spell~2~Forced Resurrection"
    description = "Destroy a follower. Both players perform Reanimate (3)."
    name_CN = "强制轮回"

    def available(self):
        return self.selectableEnemyMinionExists()

    def targetCorrect(self, target, choice=0):
        if isinstance(target, list): target = target[0]
        return target.type == "Minion" and target.ID != self.ID and target.onBoard

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if target:
            if isinstance(target, list): target = target[0]
            self.Game.killMinion(target)
            minion = self.Game.reanimate(self.ID, 3)
            minion = self.Game.reanimate(3 - self.ID, 3)
        return target


class NephthysGoddessofAmenta(SVMinion):
    Class, race, name = "Shadowcraft", "", "Nephthys, Goddess of Amenta"
    mana, attack, health = 6, 5, 5
    index = "SV_Fortune~Shadowcraft~Minion~6~5~5~~Nephthys, Goddess of Amenta~Battlecry~Enhance~Legendary"
    requireTarget, keyWord, description = False, "", "Fanfare: Put 2 random followers of different costs (excluding Nephthys, Goddess of Amenta) from your deck into play and destroy them. Enhance (10): Then, if allied followers that originally cost 1, 2, 3, 4, 5, 6, 7, 8, 9, and 10 play points have been destroyed, win the match."
    attackAdd, healthAdd = 2, 2
    name_CN = "冥府的女主宰·奈芙蒂斯"

    def getMana(self):
        if self.Game.Manas.manas[self.ID] >= 10:
            return 10
        else:
            return self.mana

    def willEnhance(self):
        return self.Game.Manas.manas[self.ID] >= 10

    def effCanTrig(self):
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
                    minion = curGame.summonfrom(i, self.ID, -1, self, fromHand=False)
                    if minion:
                        minions.append(minion)
                else:
                    break
        for minion in minions:
            self.Game.killMinion(self, minion)
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
    Class, school, name = "Bloodcraft", "", "Nightscreech"
    requireTarget, mana = False, 1
    index = "SV_Fortune~Bloodcraft~Spell~1~Nightscreech"
    description = "Summon a Forest Bat. If Wrath is active for you, evolve it and draw 1 card. Otherwise, deal 1 damage to your leader."
    name_CN = "蝙蝠的鸣噪"

    def effCanTrig(self):
        self.effectViable = self.Game.isWrath(self.ID)

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        minion = ForestBat(self.Game, self.ID)
        self.Game.summon([minion], (-1, "totheRightEnd"), self)
        if self.Game.isWrath(self.ID):
            minion.evolve()
            self.Game.Hand_Deck.drawCard(self.ID)
        else:
            damage = (1 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
            self.dealsDamage(self.Game.heroes[self.ID], damage)
        return target


class Baal(SVMinion):
    Class, race, name = "Bloodcraft", "", "Baal"
    mana, attack, health = 3, 3, 3
    index = "SV_Fortune~Bloodcraft~Minion~3~3~3~~Baal~Battlecry~Fusion~Legendary"
    requireTarget, keyWord, description = False, "", "Fusion: Bloodcraft followers that originally cost 3 play points or less Fanfare: If this card is fused with at least 3 cards, draw cards until there are 6 cards in your hand. Then, if this card is fused with at least 6 cards, deal 6 damage to all enemy followers."
    attackAdd, healthAdd = 2, 2
    name_CN = "芭力"

    def __init__(self, Game, ID):
        super().__init__(Game, ID)
        self.fusion = 1
        self.fusionMaterials = 0

    def findFusionMaterials(self):
        return [card for card in self.Game.Hand_Deck.hands[self.ID] if
                card.type == "Minion" and card != self and card.Class == "Bloodcraft" and type(card).mana <= 3]

    def effCanTrig(self):
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
            n = max(0, 6 - len(self.Game.Hand_Deck.hands[self.ID]))
            for i in range(n):
                self.Game.Hand_Deck.drawCard(self.ID)
            if self.fusionMaterials > 6:
                targets = self.Game.minionsonBoard(3 - self.ID)
                self.dealsAOE(targets, [6 for minion in targets])
        return target


class ServantofDarkness(SVMinion):
    Class, race, name = "Neutral", "", "Servant of Darkness"
    mana, attack, health = 5, 13, 13
    index = "SV_Fortune~Neutral~Minion~5~13~13~~Servant of Darkness~Uncollectible~Legendary"
    requireTarget, keyWord, description = False, "", ""
    attackAdd, healthAdd = 2, 2
    name_CN = "深渊之王的仆从"


class SilentRider(SVMinion):
    Class, race, name = "Neutral", "", "Silent Rider"
    mana, attack, health = 6, 8, 8
    index = "SV_Fortune~Neutral~Minion~6~8~8~~Silent Rider~Charge~Uncollectible~Legendary"
    requireTarget, keyWord, description = False, "Charge", "Storm."
    attackAdd, healthAdd = 2, 2
    name_CN = "沉默的魔将"


class DissDamnation(SVSpell):
    Class, school, name = "Neutral", "", "Dis's Damnation"
    requireTarget, mana = True, 7
    index = "SV_Fortune~Neutral~Spell~7~Dis's Damnation~Uncollectible~Legendary"
    description = "Deal 7 damage to an enemy. Restore 7 defense to your leader."
    name_CN = "狄斯的制裁"

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
            self.dealsDamage(target, damage)
            self.restoresHealth(self.Game.heroes[self.ID], heal)
        return target


class AstarothsReckoning(SVSpell):
    Class, school, name = "Neutral", "", "Astaroth's Reckoning"
    requireTarget, mana = False, 10
    index = "SV_Fortune~Neutral~Spell~10~Astaroth's Reckoning~Uncollectible~Legendary"
    description = "Deal damage to the enemy leader until their defense drops to 1."
    name_CN = "阿斯塔罗特的宣判"

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        damage = (self.Game.heroes[3 - self.ID].health - 1 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
        self.dealsDamage(self.Game.heroes[3 - self.ID], damage)
        return False


class PrinceofDarkness(SVMinion):
    Class, race, name = "Neutral", "", "Prince of Darkness"
    mana, attack, health = 10, 6, 6
    index = "SV_Fortune~Neutral~Minion~10~6~6~~Prince of Darkness~Battlecry~Legendary"
    requireTarget, keyWord, description = False, "", "Fanfare: Replace your deck with an Apocalypse Deck."
    attackAdd, healthAdd = 2, 2
    name_CN = "深渊之王"

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
        self.Game.Hand_Deck.shuffleintoDeck(cards, creator=self)
        return None


class DemonofPurgatory(SVMinion):
    Class, race, name = "Neutral", "", "Demon of Purgatory"
    mana, attack, health = 6, 9, 6
    index = "SV_Fortune~Neutral~Minion~6~9~6~~Demon of Purgatory~Battlecry~Uncollectible~Legendary"
    requireTarget, keyWord, description = False, "", "Fanfare: Give the enemy leader the following effect - At the start of your next turn, discard a random card from your hand."
    attackAdd, healthAdd = 2, 2
    name_CN = "边狱的邪祟"

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
        super().__init__(entity, ["TurnStarts"])

    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.onBoard and ID == self.entity.ID

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        curGame = self.entity.Game
        if curGame.mode == 0:
            if curGame.guides:
                i = curGame.guides.pop(0)
            else:
                ownHand = curGame.Hand_Deck.hands[self.entity.ID]
                i = nprandint(len(ownHand)) if ownHand else -1
                curGame.fixedGuides.append(i)
            if i > -1: curGame.Hand_Deck.discard(self.entity.ID, i)


class ScionofDesire(SVMinion):
    Class, race, name = "Neutral", "", "Scion of Desire"
    mana, attack, health = 4, 5, 5
    index = "SV_Fortune~Neutral~Minion~4~5~5~~Scion of Desire~Uncollectible~Legendary"
    requireTarget, keyWord, description = False, "", "At the end of your turn, destroy a random enemy follower. Restore X defense to your leader. X equals that follower's attack."
    attackAdd, healthAdd = 2, 2
    name_CN = "欲望缠身者"

    def __init__(self, Game, ID):
        super().__init__(Game, ID)
        self.trigsBoard = [Trig_ScionofDesire]


class Trig_ScionofDesire(TrigBoard):
    def __init__(self, entity):
        super().__init__(entity, ["TurnEnds"])

    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
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
                    curGame.fixedGuides.append((enemy.pos, enemy.type + str(enemy.ID)))
                else:
                    curGame.fixedGuides.append((0, ''))
            if enemy:
                heal = enemy.attack
                self.entity.Game.killMinion(self.entity, enemy)
                self.entity.restoresHealth(self.entity.Game.heroes[self.entity.ID], heal)


class GluttonousBehemoth(SVMinion):
    Class, race, name = "Neutral", "", "Gluttonous Behemoth"
    mana, attack, health = 7, 7, 7
    index = "SV_Fortune~Neutral~Minion~7~7~7~~Gluttonous Behemoth~Uncollectible~Legendary"
    requireTarget, keyWord, description = False, "", "At the end of your turn, deal 7 damage to the enemy leader."
    attackAdd, healthAdd = 2, 2
    name_CN = "贪食的贝希摩斯"

    def __init__(self, Game, ID):
        super().__init__(Game, ID)
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
        super().__init__(entity, ["TurnEnds"])

    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.onBoard and ID == self.entity.ID

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        self.entity.dealsDamage(self.entity.Game.heroes[3 - self.entity.ID], 7)


class Trig_EvolvedGluttonousBehemoth(TrigBoard):
    def __init__(self, entity):
        super().__init__(entity, ["TurnEnds"])

    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.onBoard and ID == self.entity.ID

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        self.entity.dealsDamage(self.entity.Game.heroes[3 - self.entity.ID], 9)


class ScorpionofGreed(SVMinion):
    Class, race, name = "Neutral", "", "Scorpion of Greed"
    mana, attack, health = 6, 7, 6
    index = "SV_Fortune~Neutral~Minion~6~7~6~~Scorpion of Greed~Charge~Bane~Drain~Uncollectible~Legendary"
    requireTarget, keyWord, description = False, "Charge,Bane,Drain", "Storm.Bane.Drain."
    attackAdd, healthAdd = 2, 2
    name_CN = "贪欲的毒蝎"


class WrathfulIcefiend(SVMinion):
    Class, race, name = "Neutral", "", "Wrathful Icefiend"
    mana, attack, health = 2, 4, 4
    index = "SV_Fortune~Neutral~Minion~2~4~4~~Wrathful Icefiend~Battlecry~Uncollectible~Legendary"
    requireTarget, keyWord, description = False, "", "Fanfare: Recover 2 evolution points."
    attackAdd, healthAdd = 2, 2
    name_CN = "狂怒的冰魔"

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        self.Game.restoreEvolvePoint(self.ID, 2)


class HereticalHellbeast(SVMinion):
    Class, race, name = "Neutral", "", "Heretical Hellbeast"
    mana, attack, health = 8, 8, 8
    index = "SV_Fortune~Neutral~Minion~8~8~8~~Heretical Hellbeast~Battlecry~Taunt~Uncollectible~Legendary"
    requireTarget, keyWord, description = False, "Taunt", "Ward. Fanfare: Deal X damage to your leader. X equals the number of other followers in play. Then destroy all other followers."
    attackAdd, healthAdd = 2, 2
    name_CN = "异端的冥兽"

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        minions = self.Game.minionsAlive(self.ID, self) + self.Game.minionsAlive(3 - self.ID)
        damage = len(minions)
        self.dealsDamage(self.Game.heroes[self.ID], damage)
        self.Game.killMinion(self, minions)


class ViciousCommander(SVMinion):
    Class, race, name = "Neutral", "", "Vicious Commander"
    mana, attack, health = 3, 4, 4
    index = "SV_Fortune~Neutral~Minion~3~4~4~~Vicious Commander~Battlecry~Uncollectible~Legendary"
    requireTarget, keyWord, description = True, "", "Fanfare: Deal 4 damage to an enemy follower."
    attackAdd, healthAdd = 2, 2
    evolveRequireTarget = True
    name_CN = "暴威统率者"

    def evolveTargetExists(self, choice=0):
        return self.selectableEnemyMinionExists()

    def evolveTargetCorrect(self, target, choice=0):
        if isinstance(target, list): target = target[0]
        return target.type == "Minion" and target.onBoard and target.ID != self.ID

    def inHandEvolving(self, target=None):
        if target:
            if isinstance(target, list): target = target[0]
            self.dealsDamage(target, 6)

    def targetExists(self, choice=0):
        return self.selectableEnemyMinionExists()

    def targetCorrect(self, target, choice=0):
        if isinstance(target, list): target = target[0]
        return target.type == "Minion" and target.ID != self.ID and target.onBoard

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if target:
            if isinstance(target, list): target = target[0]
            self.dealsDamage(target, 4)
        return target


class FlamelordofDeceit(SVMinion):
    Class, race, name = "Neutral", "", "Flamelord of Deceit"
    mana, attack, health = 5, 5, 5
    index = "SV_Fortune~Neutral~Minion~5~5~5~~Flamelord of Deceit~Battlecry~Charge~Uncollectible~Legendary"
    requireTarget, keyWord, description = False, "Charge", "Storm.Fanfare: Banish all enemy amulets."
    attackAdd, healthAdd = 2, 2
    name_CN = "恶意的炎帝"

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        self.Game.banishMinion(self, self.Game.amuletsonBoard(3 - self.ID))
        return None


class InfernalGaze(SVSpell):
    Class, school, name = "Neutral", "", "Infernal Gaze"
    requireTarget, mana = False, 1
    index = "SV_Fortune~Neutral~Spell~1~Infernal Gaze~Uncollectible~Legendary"
    description = "Until the start of your next turn, add 10 to the original cost of spells in your opponent's hand. (Only affects cards in hand at the time this effect is activated.)Draw a card."
    name_CN = "深渊之主的凝视"

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        self.Game.Manas.CardAuras_Backup.append(ManaEffect_InfernalGaze(self.Game, 3 - self.ID))
        self.Game.Hand_Deck.drawCard(self.ID)
        return None


class ManaEffect_InfernalGaze(TempManaEffect):
    def __init__(self, Game, ID):
        self.Game, self.ID = Game, ID
        self.changeby, self.changeto = +10, -1
        self.temporary = True
        self.auraAffected = []

    def applicable(self, target):
        return target.ID == self.ID and target.type == "Spell"

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


class InfernalSurge(SVSpell):
    Class, school, name = "Neutral", "", "Infernal Surge"
    requireTarget, mana = False, 1
    index = "SV_Fortune~Neutral~Spell~1~Infernal Surge~Uncollectible~Legendary"
    description = "Draw 3 cards."
    name_CN = "深渊之主的波动"

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        self.Game.Hand_Deck.drawCard(self.ID)
        self.Game.Hand_Deck.drawCard(self.ID)
        self.Game.Hand_Deck.drawCard(self.ID)


class Heavenfall(SVSpell):
    Class, school, name = "Neutral", "", "Heavenfall"
    requireTarget, mana = True, 2
    index = "SV_Fortune~Neutral~Spell~2~Heavenfall~Uncollectible~Legendary"
    description = "Banish an enemy follower or amulet.Draw a card."
    name_CN = "天握"

    def available(self):
        return self.selectableEnemyExists()

    def targetCorrect(self, target, choice=0):
        if isinstance(target, list): target = target[0]
        return (target.type == "Minion" or target.type == "Amulet") and target.ID != self.ID and target.onBoard

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if target:
            if isinstance(target, list): target = target[0]
            self.Game.banishMinion(self, target)
            self.Game.Hand_Deck.drawCard(self.ID)
        return target


class Earthfall(SVSpell):
    Class, school, name = "Neutral", "", "Earthfall"
    requireTarget, mana = False, 4
    index = "SV_Fortune~Neutral~Spell~4~Earthfall~Uncollectible~Legendary"
    description = "Destroy all non-Neutral followers."
    name_CN = "地坏"

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        minions = []
        for minion in self.Game.minionsAlive(1) + self.Game.minionsAlive(2):
            if minion.Class != "Neutral":
                minions.append(minion)
        self.Game.killMinion(self, minions)


class PrinceofCocytus_Accelerate(SVSpell):
    Class, school, name = "Neutral", "", "Prince of Cocytus"
    requireTarget, mana = False, 3
    index = "SV_Fortune~Neutral~Spell~3~Prince of Cocytus~Accelerate~Uncollectible~Legendary"
    description = "Randomly put 4 different Cocytus cards into your deck."
    name_CN = "冰狱之王·深渊之主"

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        cards = [
            DemonofPurgatory,
            ScionofDesire,
            GluttonousBehemoth,
            ScorpionofGreed,
            WrathfulIcefiend,
            HereticalHellbeast,
            ViciousCommander,
            FlamelordofDeceit,
            InfernalGaze,
            InfernalSurge,
            Heavenfall,
            Earthfall,
            AstarothsReckoning,
        ]
        curGame = self.Game
        if curGame.mode == 0:
            types = []
            if curGame.guides:
                types = list(curGame.guides.pop(0))
            else:
                while len(types) < 4:
                    t = npchoice(cards)
                    if t not in types:
                        types.append(t)
                curGame.fixedGuides.append(tuple(types))
            if types:
                cards = []
                for t in types:
                    cards.append(t(self.Game, self.ID))
                self.Game.Hand_Deck.shuffleintoDeck(cards, creator=self)
        return None


class PrinceofCocytus(SVMinion):
    Class, race, name = "Neutral", "", "Prince of Cocytus"
    mana, attack, health = 9, 7, 7
    index = "SV_Fortune~Neutral~Minion~9~7~7~~Prince of Cocytus~Accelerate~Battlecry~Legendary"
    requireTarget, keyWord, description = False, "", "Accelerate (3): Randomly put 4 different Cocytus cards into your deck.Fanfare: Replace your deck with a Cocytus Deck."
    accelerateSpell = PrinceofCocytus_Accelerate
    attackAdd, healthAdd = 2, 2
    name_CN = "冰狱之王·深渊之主"

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
        self.Game.Hand_Deck.extractfromDeck(None, self.ID, all=True)
        cards = [
            DemonofPurgatory(self.Game, self.ID),
            ScionofDesire(self.Game, self.ID),
            GluttonousBehemoth(self.Game, self.ID),
            ScorpionofGreed(self.Game, self.ID),
            WrathfulIcefiend(self.Game, self.ID),
            HereticalHellbeast(self.Game, self.ID),
            ViciousCommander(self.Game, self.ID),
            FlamelordofDeceit(self.Game, self.ID),
            InfernalGaze(self.Game, self.ID),
            InfernalSurge(self.Game, self.ID),
            Heavenfall(self.Game, self.ID),
            Earthfall(self.Game, self.ID),
            AstarothsReckoning(self.Game, self.ID),
        ]
        self.Game.Hand_Deck.shuffleintoDeck(cards, creator=self)
        return None


class TempleofHeresy(Amulet):
    Class, race, name = "Heavencraft", "", "Temple of Heresy"
    mana = 1
    index = "SV_Fortune~Heavencraft~Amulet~1~~Temple of Heresy~Countdown~Deathrattle"
    requireTarget, description = False, "Countdown (9)At the start of your turn, if you have more evolution points than your opponent, subtract 1 from this amulet's Countdown. (You have 0 evolution points on turns you are unable to evolve.)Last Words: Randomly put a Prince of Darkness or Prince of Cocytus into your hand and change its cost to 1."
    name_CN = "邪教神殿"

    def __init__(self, Game, ID):
        super().__init__(Game, ID)
        self.counter = 9
        self.trigsBoard = [Trig_Countdown(self), Trig_TempleofHeresy(self)]
        self.deathrattles = [Deathrattle_TempleofHeresy(self)]


class Deathrattle_TempleofHeresy(Deathrattle_Minion):
    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        curGame = self.entity.Game
        if curGame.mode == 0:
            pool = (PrinceofDarkness, PrinceofCocytus)
            if curGame.guides:
                card = curGame.guides.pop(0)
            else:
                card = np.random.choice(pool)
                curGame.fixedGuides.append(card)
            card = card(self.entity.Game, self.entity.ID)
            ManaMod(card, changeby=0, changeto=1).applies()
            self.entity.Game.Hand_Deck.addCardtoHand(card, self.entity.ID, creator=type(self.entity))


class Trig_TempleofHeresy(TrigBoard):
    def __init__(self, entity):
        super().__init__(entity, ["TurnStarts"])

    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.onBoard and ID == self.entity.ID and self.entity.Game.getEvolutionPoint(
            self.entity.ID) > self.entity.Game.getEvolutionPoint(3 - self.entity.ID)

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        self.entity.countdown(self.entity, 1)


class RaRadianceIncarnate(SVMinion):
    Class, race, name = "Havencraft", "", "Ra, Radiance Incarnate"
    mana, attack, health = 5, 5, 5
    index = "SV_Fortune~Havencraft~Minion~5~5~5~~Ra, Radiance Incarnate~Taunt~Battlecry"
    requireTarget, keyWord, description = False, "Taunt", "Ward. Fanfare: Give your leader the following effect - At the end of your turn, deal X damage to the enemy leader. X equals your current turn number minus 5 (no damage is dealt if X is less than 0). (This effect is not stackable and lasts for the rest of the match.)"
    attackAdd, healthAdd = 2, 2
    name_CN = "光辉显世·拉"

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        trigger = Trig_RaRadianceIncarnate(self.Game.heroes[self.ID])
        for t in self.Game.heroes[self.ID].trigsBoard:
            if type(t) == type(trigger):
                return
        self.Game.heroes[self.ID].trigsBoard.append(trigger)
        trigger.connect()
        return None


class Trig_RaRadianceIncarnate(TrigBoard):
    def __init__(self, entity):
        super().__init__(entity, ["TurnEnds"])

    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.onBoard and ID == self.entity.ID

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        turn = self.entity.Game.Counters.turns[self.entity.ID]
        if turn >= 5:
            self.entity.dealsDamage(self.entity.Game.heroes[3 - self.entity.ID], turn - 5)


class LazuliGatewayHomunculus(SVMinion):
    Class, race, name = "Portalcraft", "", "Lazuli, Gateway Homunculus"
    mana, attack, health = 2, 2, 2
    index = "SV_Fortune~Portalcraft~Minion~2~2~2~~Lazuli, Gateway Homunculus~Taunt~Battlecry~Enhance"
    requireTarget, keyWord, description = False, "Taunt", "Ward.Fanfare: Enhance (9) - Randomly put 1 of the highest-cost Portalcraft followers from your deck into play. Activate its Fanfare effects (excluding Choose and targeted effects)."
    attackAdd, healthAdd = 2, 2
    evolveRequireTarget = True
    name_CN = "界门的人造体·拉姿莉"

    def evolveTargetExists(self, choice=0):
        return self.selectableFriendlyMinionExists()

    def evolveTargetCorrect(self, target, choice=0):
        if isinstance(target, list): target = target[0]
        return target.type == "Minion" and target.onBoard and target.ID == self.ID

    def inHandEvolving(self, target=None):
        if target:
            if isinstance(target, list): target = target[0]
            target.marks["Next Damage 0"] = 1

    def getMana(self):
        if self.Game.Manas.manas[self.ID] >= 9:
            return 9
        else:
            return self.mana

    def willEnhance(self):
        return self.Game.Manas.manas[self.ID] >= 9

    def effCanTrig(self):
        self.effectViable = self.willEnhance()

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if comment == 9:
            curGame = self.Game
            maxi = 0
            for card in self.Game.Hand_Deck.decks[self.ID]:
                if card.mana > maxi and card.type == "Minion" and card.Class == "Portalcraft":
                    maxi = card.mana
            if curGame.mode == 0:
                for num in range(2):
                    if curGame.guides:
                        i = curGame.guides.pop(0)
                    else:
                        cards = [i for i, card in enumerate(self.Game.Hand_Deck.decks[self.ID]) if
                                 card.type == "Minion" and card.Class == "Portalcraft" and card.mana == maxi]
                        i = npchoice(cards) if cards and curGame.space(self.ID) > 0 else -1
                        curGame.fixedGuides.append(i)
                    if i > -1:
                        minion = curGame.summonfrom(i, self.ID, -1, self, fromHand=False)
                        if minion and minion.onBoard and "~Battlecry" in minion.index and not minion.requireTarget and "~Choose" not in minion.index:
                            minion.whenEffective(target=None, comment="", choice=0, posinHand=-2)


class SpinariaLucilleKeepers(SVMinion):
    Class, race, name = "Portalcraft", "Artifact", "Spinaria & Lucille, Keepers"
    mana, attack, health = 3, 3, 3
    index = "SV_Fortune~Portalcraft~Minion~3~3~3~Artifact~Spinaria & Lucille, Keepers~Uncollectible~Legendary"
    requireTarget, keyWord, description = False, "", "When this follower comes into play, if at least 6 allied Artifact cards with different names have been destroyed this match, evolve this follower.Can't be evolved using evolution points. (Can be evolved using card effects.)"
    attackAdd, healthAdd = 3, 3
    name_CN = "神秘的遗物·丝碧涅与璐契儿"

    def __init__(self, Game, ID):
        super().__init__(Game, ID)
        self.appearResponse = [self.whenAppears]
        self.marks["Can't Evolve"] = 1

    def whenAppears(self):
        if len(self.Game.Counters.artifactsDiedThisGame[self.ID]) >= 6:
            self.evolve()

    def inEvolving(self):
        trigger = Trig_SpinariaLucilleKeepers(self)
        self.trigsBoard.append(trigger)
        trigger.connect()


class Trig_SpinariaLucilleKeepers(TrigBoard):
    def __init__(self, entity):
        super().__init__(entity, ["MinionAttackingMinion", "MinionAttackingHero"])

    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
        return subject == self.entity and self.entity.onBoard

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        targets = self.entity.Game.minionsonBoard(3 - self.entity.ID)
        self.entity.dealsAOE(targets, [6 for obj in targets])
        self.entity.Game.gathertheDead()
        for trig in self.entity.trigsBoard:
            if type(trig) == Trig_SpinariaLucilleKeepers:
                trig.disconnect()
                self.entity.trigsBoard.remove(trig)


class LucilleKeeperofRelics(SVMinion):
    Class, race, name = "Portalcraft", "", "Lucille, Keeper of Relics"
    mana, attack, health = 5, 4, 4
    index = "SV_Fortune~Portalcraft~Minion~5~4~4~~Lucille, Keeper of Relics~Battlecry~Legendary"
    requireTarget, keyWord, description = False, "", "Fanfare: Put a Spinaria & Lucille, Keepers into your deck. When an allied Artifact card comes into play, gain the ability to evolve for 0 evolution points."
    attackAdd, healthAdd = 0, 0
    name_CN = "遗物守门人·璐契儿"

    def __init__(self, Game, ID):
        super().__init__(Game, ID)
        self.trigsBoard = [Trig_LucilleKeeperofRelics(self)]

    def inHandEvolving(self, target=None):
        self.Game.summon([RadiantArtifact(self.Game, self.ID)], (-1, "totheRightEnd"), self)

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        self.Game.Hand_Deck.shuffleintoDeck([SpinariaLucilleKeepers(self.Game, self.ID)], creator=self)


class Trig_LucilleKeeperofRelics(TrigBoard):
    def __init__(self, entity):
        super().__init__(entity, ["MinionSummoned"])

    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.onBoard and subject.ID == self.entity.ID and subject != self.entity and "Artifact" in subject.race

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        self.entity.marks["Free Evolve"] += 1


SV_Fortune_Indices = {
    "SV_Fortune~Neutral~Minion~2~5~5~~Cloud Gigas~Taunt": CloudGigas,
    "SV_Fortune~Neutral~Spell~2~Sudden Showers": SuddenShowers,
    "SV_Fortune~Neutral~Minion~4~4~3~~Winged Courier~Deathrattle": WingedCourier,
    "SV_Fortune~Neutral~Minion~4~1~1~~Fieran, Havensent Wind God~Battlecry~Invocation~Legendary": FieranHavensentWindGod,
    "SV_Fortune~Neutral~Spell~4~Resolve of the Fallen": ResolveoftheFallen,
    "SV_Fortune~Neutral~Minion~5~3~4~~Starbright Deity~Battlecry": StarbrightDeity,
    "SV_Fortune~Neutral~Minion~5~5~5~~XXI. Zelgenea, The World~Battlecry~Invocation~Legendary": XXIZelgeneaTheWorld,
    "SV_Fortune~Neutral~Amulet~6~~Titanic Showdown~Countdown~Deathrattle": TitanicShowdown,
    "SV_Fortune~Neutral~Spell~2~Pureshot Angel~Accelerate~Uncollectible": PureshotAngel_Accelerate,
    "SV_Fortune~Neutral~Minion~8~6~6~~Pureshot Angel~Battlecry~Accelerate": PureshotAngel,

    "SV_Fortune~Forestcraft~Minion~1~1~1~~Lumbering Carapace~Battlecry": LumberingCarapace,
    "SV_Fortune~Forestcraft~Minion~2~2~2~~Blossoming Archer": BlossomingArcher,
    "SV_Fortune~Forestcraft~Spell~2~Soothing Spell": SoothingSpell,
    "SV_Fortune~Forestcraft~Minion~3~3~3~~XII. Wolfraud, Hanged Man~Enhance~Battlecry~Legendary": XIIWolfraudHangedMan,
    "SV_Fortune~Forestcraft~Spell~0~Treacherous Reversal~Uncollectible": TreacherousReversal,
    "SV_Fortune~Forestcraft~Spell~1~Reclusive Ponderer~Accelerate~Uncollectible": ReclusivePonderer_Accelerate,
    "SV_Fortune~Forestcraft~Minion~4~3~3~~Reclusive Ponderer~Stealth~Accelerate": ReclusivePonderer,
    "SV_Fortune~Forestcraft~Spell~1~Chipper Skipper~Accelerate~Uncollectible": ChipperSkipper_Accelerate,
    "SV_Fortune~Forestcraft~Minion~4~4~3~~Chipper Skipper~Accelerate": ChipperSkipper,
    "SV_Fortune~Forestcraft~Spell~4~Fairy Assault": FairyAssault,
    "SV_Fortune~Forestcraft~Minion~5~4~5~~Optimistic Beastmaster~Battlecry": OptimisticBeastmaster,
    "SV_Fortune~Forestcraft~Minion~6~4~4~~Terrorformer~Battlecry~Fusion~Legendary": Terrorformer,
    "SV_Fortune~Forestcraft~Spell~1~Deepwood Wolf~Accelerate~Uncollectible": DeepwoodWolf_Accelerate,
    "SV_Fortune~Forestcraft~Minion~7~3~3~~Deepwood Wolf~Charge~Accelerate": DeepwoodWolf,
    "SV_Fortune~Forestcraft~Spell~1~Lionel, Woodland Shadow~Accelerate~Uncollectible": LionelWoodlandShadow_Accelerate,
    "SV_Fortune~Forestcraft~Minion~7~5~6~~Lionel, Woodland Shadow~Battlecry~Accelerate": LionelWoodlandShadow,

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

    "SV_Fortune~Runecraft~Minion~1~1~1~~Juggling Moggy~Battlecry~EarthRite": JugglingMoggy,
    "SV_Fortune~Runecraft~Spell~1~Magical Augmentation~EarthRite": MagicalAugmentation,
    "SV_Fortune~Runecraft~Minion~2~2~2~~Creative Conjurer~Battlecry~EarthRite": CreativeConjurer,
    "SV_Fortune~Runecraft~Spell~2~Golem Summoning~Uncollectible": GolemSummoning,
    "SV_Fortune~Runecraft~Minion~2~2~2~~0. Lhynkal, The Fool~Battlecry~Choose~Legendary": LhynkalTheFool,
    "SV_Fortune~Runecraft~Spell~4~Rite of the Ignorant~Uncollectible~Legendary": RiteoftheIgnorant,
    "SV_Fortune~Runecraft~Spell~2~Scourge of the Omniscient~Uncollectible~Legendary": ScourgeoftheOmniscient,
    "SV_Fortune~Runecraft~Spell~2~Authoring Tomorrow": AuthoringTomorrow,
    "SV_Fortune~Runecraft~Spell~2~Madcap Conjuration": MadcapConjuration,
    "SV_Fortune~Runecraft~Minion~3~3~3~~Arcane Auteur~Deathrattle": ArcaneAuteur,
    "SV_Fortune~Runecraft~Minion~4~3~3~~Piquant Potioneer~Battlecry": PiquantPotioneer,
    "SV_Fortune~Runecraft~Minion~4~2~2~~Imperator of Magic~Battlecry~Enhance~EarthRite": ImperatorofMagic,
    "SV_Fortune~Runecraft~Amulet~5~Earth Sigil~Emergency Summoning~Deathrattle~Uncollectible": EmergencySummoning,
    "SV_Fortune~Neutral~Minion~2~2~2~~Happy Pig~Deathrattle": HappyPig,
    "SV_Fortune~Runecraft~Minion~5~4~4~~Sweetspell Sorcerer": SweetspellSorcerer,
    "SV_Fortune~Runecraft~Spell~2~Witch Snap": WitchSnap,
    "SV_Fortune~Runecraft~Minion~6~6~6~~Adamantine Golem~Battlecry~EarthRite~Legendary": AdamantineGolem,

    "SV_Fortune~Dragoncraft~Minion~1~1~1~~Dragonclad Lancer~Battlecry": DragoncladLancer,
    "SV_Fortune~Dragoncraft~Minion~2~2~2~~Springwell Dragon Keeper~Battlecry~Enhance": SpringwellDragonKeeper,
    "SV_Fortune~Dragoncraft~Minion~2~1~2~~Tropical Grouper~Battlecry~Enhance": TropicalGrouper,
    "SV_Fortune~Dragoncraft~Minion~2~2~2~~Wavecrest Angler~Battlecry": WavecrestAngler,
    "SV_Fortune~Dragoncraft~Spell~2~Draconic Call": DraconicCall,
    "SV_Fortune~Dragoncraft~Minion~1~1~2~~Ivory Dragon~Battlecry": IvoryDragon,
    "SV_Fortune~Dragoncraft~Minion~3~1~5~~Heliodragon": Heliodragon,
    "SV_Fortune~Dragoncraft~Minion~3~2~8~~Slaughtering Dragonewt~Bane~Battlecry": SlaughteringDragonewt,
    "SV_Fortune~Dragoncraft~Minion~5~4~4~~Crimson Dragon's Sorrow~Taunt~Battlecry~Legendary~Uncollectible": CrimsonDragonsSorrow,
    "SV_Fortune~Dragoncraft~Minion~7~4~4~~Azure Dragon's Rage~Charge~Legendary~Uncollectible": AzureDragonsRage,
    "SV_Fortune~Dragoncraft~Minion~3~2~3~~Turncoat Dragon Summoner~Battlecry~Legendary": TurncoatDragonSummoner,
    "SV_Fortune~Dragoncraft~Amulet~1~~Dragon's Nest": DragonsNest,
    "SV_Fortune~Dragoncraft~Spell~3~Dragon Spawning": DragonSpawning,
    "SV_Fortune~Dragoncraft~Spell~4~Dragon Impact": DragonImpact,
    "SV_Fortune~Dragoncraft~Minion~10~11~8~~XI. Erntz, Justice~Taunt~Legendary": XIErntzJustice,

    "SV_Fortune~Shadowcraft~Minion~2~2~2~~Ghostly Maid~Battlecry": GhostlyMaid,
    "SV_Fortune~Shadowcraft~Minion~2~2~2~~Bonenanza Necromancer~Enhance~Battlecry": BonenanzaNecromancer,
    "SV_Fortune~Shadowcraft~Spell~2~Savoring Slash": SavoringSlash,
    "SV_Fortune~Shadowcraft~Amulet~2~~Coffin of the Unknown Soul~Countdown~Battlecry~Deathrattle": CoffinoftheUnknownSoul,
    "SV_Fortune~Shadowcraft~Minion~3~3~3~~Spirit Curator~Battlecry": SpiritCurator,
    "SV_Fortune~Shadowcraft~Amulet~1~~Death Fowl~Countdown~Crystallize~Deathrattle~Uncollectible": DeathFowl_Crystallize,
    "SV_Fortune~Shadowcraft~Minion~4~3~3~~Death Fowl~Crystallize~Deathrattle": DeathFowl,
    "SV_Fortune~Shadowcraft~Minion~2~2~2~~Soul Box~Battlecry": SoulBox,
    "SV_Fortune~Shadowcraft~Minion~5~4~4~~VI. Milteo, The Lovers~Battlecry~Enhance~Deathrattle~Legendary": VIMilteoTheLovers,
    "SV_Fortune~Shadowcraft~Amulet~2~~Cloistered Sacristan~Countdown~Crystallize~Deathrattle~Uncollectible": CloisteredSacristan_Crystallize,
    "SV_Fortune~Shadowcraft~Minion~6~5~5~~Cloistered Sacristan~Taunt~Crystallize": CloisteredSacristan,
    "SV_Fortune~Shadowcraft~Minion~8~6~6~~Conquering Dreadlord~Invocation~Legendary": ConqueringDreadlord,
    "SV_Fortune~Shadowcraft~Amulet~2~~Deathbringer~Countdown~Crystallize~Battlecry~Deathrattle~Uncollectible": Deathbringer_Crystallize,
    "SV_Fortune~Shadowcraft~Minion~9~7~7~~Deathbringer~Crystallize": Deathbringer,

    "SV_Fortune~Bloodcraft~Minion~1~1~2~~Silverbolt Hunter~Battlecry~Deathrattle": SilverboltHunter,
    "SV_Fortune~Bloodcraft~Minion~2~1~3~~Moonrise Werewolf~Battlecry~Enhance": MoonriseWerewolf,
    "SV_Fortune~Bloodcraft~Minion~2~2~2~~Whiplash Imp~Battlecry~Enhance": WhiplashImp,
    "SV_Fortune~Bloodcraft~Minion~2~2~2~~Contemptous Demon~Battlecry": ContemptousDemon,
    "SV_Fortune~Bloodcraft~Spell~2~Dark Summons": DarkSummons,
    "SV_Fortune~Bloodcraft~Minion~3~3~3~~Tyrant of Mayhem~Battlecry": TyrantofMayhem,
    "SV_Fortune~Bloodcraft~Minion~4~4~4~~Curmudgeon Ogre~Battlecry~Enhance": CurmudgeonOgre,
    "SV_Fortune~Bloodcraft~Amulet~3~~Dire Bond": DireBond,
    "SV_Fortune~Bloodcraft~Minion~4~4~3~~Darhold, Abyssal Contract~Battlecry~Legendary": DarholdAbyssalContract,
    "SV_Fortune~Bloodcraft~Spell~5~Burning Constriction": BurningConstriction,
    "SV_Fortune~Bloodcraft~Spell~1~Vampire of Calamity~Accelerate~Uncollectible": VampireofCalamity_Accelerate,
    "SV_Fortune~Bloodcraft~Minion~7~7~7~~Vampire of Calamity~Rush~Battlecry~Accelerate": VampireofCalamity,
    "SV_Fortune~Bloodcraft~Amulet~3~~Unselfish Grace~Uncollectible~Legendary": UnselfishGrace,
    "SV_Fortune~Bloodcraft~Spell~1~Insatiable Desire~Uncollectible~Legendary": InsatiableDesire,
    "SV_Fortune~Bloodcraft~Spell~0~XIV. Luzen, Temperance~Accelerate~Uncollectible~Legendary": XIVLuzenTemperance_Accelerate,
    "SV_Fortune~Bloodcraft~Minion~4~4~4~~XIV. Luzen, Temperance~Uncollectible~Legendary": XIVLuzenTemperance_Token,
    "SV_Fortune~Bloodcraft~Minion~9~7~7~~XIV. Luzen, Temperance~Accelerate~Legendary": XIVLuzenTemperance,

    "SV_Fortune~Havencraft~Spell~1~Jeweled Brilliance": JeweledBrilliance,
    "SV_Fortune~Havencraft~Minion~2~2~2~~Stalwart Featherfolk~Taunt~Battlecry": StalwartFeatherfolk,
    "SV_Fortune~Havencraft~Minion~2~3~1~~Prismaplume Bird~Deathrattle": PrismaplumeBird,
    "SV_Fortune~Havencraft~Minion~3~1~4~~Four-Pillar Tortoise~Taunt~Battlecry": FourPillarTortoise,
    "SV_Fortune~Havencraft~Spell~1~Lorena's Holy Water~Uncollectible": LorenasHolyWater,
    "SV_Fortune~Havencraft~Minion~3~2~3~~Lorena, Iron-Willed Priest~Battlecry": LorenaIronWilledPriest,
    "SV_Fortune~Havencraft~Minion~3~2~2~~Sarissa, Luxflash Spear~Battlecry~Enhance~Legendary": SarissaLuxflashSpear,
    "SV_Fortune~Havencraft~Minion~4~2~5~~Priestess of Foresight~Battlecry": PriestessofForesight,
    "SV_Fortune~Havencraft~Amulet~4~~Holybright Altar~Battlecry~Countdown~Deathrattle": HolybrightAltar,
    "SV_Fortune~Havencraft~Minion~5~2~3~~Reverend Adjudicator~Taunt~Battlecry": ReverendAdjudicator,
    "SV_Fortune~Havencraft~Amulet~2~~Somnolent Strength~Countdown~Deathrattle~Uncollectible~Legendary": SomnolentStrength,
    "SV_Fortune~Havencraft~Spell~2~VIII. Sofina, Strength~Accelerate~Uncollectible~Legendary": VIIISofinaStrength_Accelerate,
    "SV_Fortune~Havencraft~Minion~5~2~6~~VIII. Sofina, Strength~Accelerate~Battlecry~Legendary": VIIISofinaStrength,
    "SV_Fortune~Havencraft~Spell~1~Puresong Priest~Accelerate~Uncollectible": PuresongPriest_Accelerate,
    "SV_Fortune~Havencraft~Minion~6~5~5~~Puresong Priest~Accelerate~Battlecry": PuresongPriest,

    "SV_Fortune~Portalcraft~Spell~0~Artifact Scan": ArtifactScan,
    "SV_Fortune~Portalcraft~Minion~1~1~1~~Robotic Engineer~Deathrattle": RoboticEngineer,
    "SV_Fortune~Portalcraft~Minion~2~2~2~~Marionette Expert~Deathrattle": MarionetteExpert,
    "SV_Fortune~Portalcraft~Minion~2~1~3~~Cat Tuner": CatTuner,
    "SV_Fortune~Portalcraft~Minion~3~1~5~~Steelslash Tiger~Rush~Battlecry": SteelslashTiger,
    "SV_Fortune~Portalcraft~Amulet~3~~Wheel of Misfortune~Countdown~Uncollectible~Legendary": WheelofMisfortune,
    "SV_Fortune~Portalcraft~Minion~3~2~3~~X. Slaus, Wheel of Fortune~Battlecry~Legendary": XSlausWheelofFortune,
    "SV_Fortune~Portalcraft~Spell~3~Inverted Manipulation": InvertedManipulation,
    "SV_Fortune~Portalcraft~Minion~4~3~3~~Powerlifting Puppeteer~Battlecry": PowerliftingPuppeteer,
    "SV_Fortune~Portalcraft~Minion~4~4~3~~Dimension Dominator~Battlecry~Legendary": DimensionDominator,
    "SV_Fortune~Portalcraft~Minion~5~4~4~~Mind Splitter~Battlecry": MindSplitter,
    "SV_Fortune~Portalcraft~Spell~5~Pop Goes the Poppet": PopGoesthePoppet,

    "SV_Fortune~Neutral~Minion~5~3~5~~Archangel of Evocation~Taunt~Battlecry": ArchangelofEvocation,
    "SV_Fortune~Forestcraft~Minion~3~1~5~~Aerin, Forever Brilliant~Legendary": AerinForeverBrilliant,
    "SV_Fortune~Forestcraft~Minion~4~3~4~~Furious Mountain Deity~Enhance~Battlecry": FuriousMountainDeity,
    "SV_Fortune~Forestcraft~Minion~8~8~8~~Deepwood Anomaly~Battlecry~Legendary": DeepwoodAnomaly,
    "SV_Fortune~Forestcraft~Spell~3~Life Banquet": LifeBanquet,
    "SV_Fortune~Swordcraft~Minion~2~2~2~Officer~Ilmisuna, Discord Hawker~Battlecry": IlmisunaDiscordHawker,
    "SV_Fortune~Swordcraft~Minion~4~4~4~Commander~Alyaska, War Hawker~Legendary": AlyaskaWarHawker,
    "SV_Fortune~Swordcraft~Minion~8~6~6~Commander~Exterminus Weapon~Battlecry~Deathrattle~Uncollectible~Legendary": ExterminusWeapon,
    "SV_Fortune~Runecraft~Minion~2~1~2~~Runie, Resolute Diviner~Spellboost~Battlecry~Legendary": RunieResoluteDiviner,
    "SV_Fortune~Runecraft~Spell~2~Alchemical Craftschief~Accelerate~Uncollectible": AlchemicalCraftschief_Accelerate,
    "SV_Fortune~Runecraft~Minion~7~4~4~~Alchemical Craftschief~Taunt~Battlecry~Uncollectible": AlchemicalCraftschief_Token,
    "SV_Fortune~Runecraft~Minion~8~4~4~~Alchemical Craftschief~Taunt~Battlecry~Accelerate": AlchemicalCraftschief,
    "SV_Fortune~Dragoncraft~Spell~2~Whitefrost Whisper~Uncollectible~Legendary": WhitefrostWhisper,
    "SV_Fortune~Dragoncraft~Minion~3~1~3~~Filene, Absolute Zero~Battlecry~Legendary": FileneAbsoluteZero,
    "SV_Fortune~Dragoncraft~Minion~6~5~7~~Eternal Whale~Taunt": EternalWhale,
    "SV_Fortune~Dragoncraft~Minion~1~5~7~~Eternal Whale~Taunt~Uncollectible": EternalWhale_Token,
    "SV_Fortune~Shadowcraft~Spell~2~Forced Resurrection": ForcedResurrection,
    "SV_Fortune~Shadowcraft~Minion~6~5~5~~Nephthys, Goddess of Amenta~Battlecry~Enhance~Legendary": NephthysGoddessofAmenta,
    "SV_Fortune~Bloodcraft~Spell~1~Nightscreech": Nightscreech,
    "SV_Fortune~Bloodcraft~Minion~3~3~3~~Baal~Battlecry~Fusion~Legendary": Baal,
    "SV_Fortune~Neutral~Minion~5~13~13~~Servant of Darkness~Uncollectible~Legendary": ServantofDarkness,
    "SV_Fortune~Neutral~Minion~6~8~8~~Silent Rider~Charge~Uncollectible~Legendary": SilentRider,
    "SV_Fortune~Neutral~Spell~7~Dis's Damnation~Uncollectible~Legendary": DissDamnation,
    "SV_Fortune~Neutral~Spell~10~Astaroth's Reckoning~Uncollectible~Legendary": AstarothsReckoning,
    "SV_Fortune~Neutral~Minion~10~6~6~~Prince of Darkness~Battlecry~Legendary": PrinceofDarkness,
    "SV_Fortune~Neutral~Minion~6~9~6~~Demon of Purgatory~Battlecry~Uncollectible~Legendary": DemonofPurgatory,
    "SV_Fortune~Neutral~Minion~4~5~5~~Scion of Desire~Uncollectible~Legendary": ScionofDesire,
    "SV_Fortune~Neutral~Minion~7~7~7~~Gluttonous Behemoth~Uncollectible~Legendary": GluttonousBehemoth,
    "SV_Fortune~Neutral~Minion~6~7~6~~Scorpion of Greed~Charge~Bane~Drain~Uncollectible~Legendary": ScorpionofGreed,
    "SV_Fortune~Neutral~Minion~2~4~4~~Wrathful Icefiend~Battlecry~Uncollectible~Legendary": WrathfulIcefiend,
    "SV_Fortune~Neutral~Minion~8~8~8~~Heretical Hellbeast~Battlecry~Taunt~Uncollectible~Legendary": HereticalHellbeast,
    "SV_Fortune~Neutral~Minion~3~4~4~~Vicious Commander~Battlecry~Uncollectible~Legendary": ViciousCommander,
    "SV_Fortune~Neutral~Minion~5~5~5~~Flamelord of Deceit~Battlecry~Charge~Uncollectible~Legendary": FlamelordofDeceit,
    "SV_Fortune~Neutral~Spell~1~Infernal Gaze~Uncollectible~Legendary": InfernalGaze,
    "SV_Fortune~Neutral~Spell~1~Infernal Surge~Uncollectible~Legendary": InfernalSurge,
    "SV_Fortune~Neutral~Spell~2~Heavenfall~Uncollectible~Legendary": Heavenfall,
    "SV_Fortune~Neutral~Spell~4~Earthfall~Uncollectible~Legendary": Earthfall,
    "SV_Fortune~Neutral~Spell~3~Prince of Cocytus~Accelerate~Uncollectible~Legendary": PrinceofCocytus_Accelerate,
    "SV_Fortune~Neutral~Minion~9~7~7~~Prince of Cocytus~Accelerate~Battlecry~Legendary": PrinceofCocytus,
    "SV_Fortune~Heavencraft~Amulet~1~~Temple of Heresy~Countdown~Deathrattle": TempleofHeresy,
    "SV_Fortune~Havencraft~Minion~5~5~5~~Ra, Radiance Incarnate~Taunt~Battlecry": RaRadianceIncarnate,
    "SV_Fortune~Portalcraft~Minion~2~2~2~~Lazuli, Gateway Homunculus~Taunt~Battlecry~Enhance": LazuliGatewayHomunculus,
    "SV_Fortune~Portalcraft~Minion~3~3~3~Artifact~Spinaria & Lucille, Keepers~Uncollectible~Legendary": SpinariaLucilleKeepers,
    "SV_Fortune~Portalcraft~Minion~5~4~4~~Lucille, Keeper of Relics~Battlecry~Legendary": LucilleKeeperofRelics,

}
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


class CloudGigas(SVMinion):
    Class, race, name = "Neutral", "", "Cloud Gigas"
    mana, attack, health = 2, 5, 5
    index = "SV_Fortune~Neutral~Minion~2~5~5~~Cloud Gigas~Taunt"
    requireTarget, keyWord, description = False, "Taunt", "Ward. At the start of your turn, put a Cloud Gigas into your deck and banish this follower."
    attackAdd, healthAdd = 0, 0
    name_CN = "腾云巨灵"

    def __init__(self, Game, ID):
        super().__init__(Game, ID)
        self.trigsBoard = [Trig_CloudGigas(self)]

    def inEvolving(self):
        for t in self.trigsBoard:
            if type(t) == Trig_CloudGigas:
                t.disconnect()
                self.trigsBoard.remove(t)
                break


class Trig_CloudGigas(TrigBoard):
    def __init__(self, entity):
        super().__init__(entity, ["TurnStarts"])

    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.onBoard and ID == self.entity.ID

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        self.entity.Game.banishMinion(self.entity, self.entity)
        self.entity.Game.Hand_Deck.shuffleintoDeck([CloudGigas(self.entity.Game, self.entity.ID)], creator=self.entity)


class SuddenShowers(SVSpell):
    Class, school, name = "Neutral", "", "Sudden Showers"
    mana, requireTarget = 2, False
    index = "SV_Fortune~Neutral~Spell~2~~Sudden Showers"
    description = "Destroy a random follower."
    name_CN = "突坠的落石"

    def available(self):
        return len(self.Game.minionsAlive(1)) + len(self.Game.minionsAlive(2)) > 0

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        curGame = self.Game
        if curGame.mode == 0:
            minion = None
            if curGame.guides:
                i, where = curGame.guides.pop(0)
                if where: minion = curGame.find(i, where)
            else:
                minions = curGame.minionsAlive(1) + curGame.minionsAlive(2)
                if len(minions) > 0:
                    minion = npchoice(minions)
                    curGame.fixedGuides.append((minion.pos, "Minion%d" % minion.ID))
                else:
                    curGame.fixedGuides.append((0, ""))
            if minion: curGame.killMinion(self, minion)
        return None


class WingedCourier(SVMinion):
    Class, race, name = "Neutral", "", "Winged Courier"
    mana, attack, health = 4, 4, 3
    index = "SV_Fortune~Neutral~Minion~4~4~3~~Winged Courier~Deathrattle"
    requireTarget, keyWord, description = False, "", "Last Words: Draw a card."
    attackAdd, healthAdd = 2, 2
    name_CN = "翔翼信使"

    def __init__(self, Game, ID):
        super().__init__(Game, ID)
        self.deathrattles = [Deathrattle_WingedCourier(self)]


class Deathrattle_WingedCourier(Deathrattle_Minion):
    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        self.entity.Game.Hand_Deck.drawCard(self.entity.ID)


class FieranHavensentWindGod(SVMinion):
    Class, race, name = "Neutral", "", "Fieran, Havensent Wind God"
    mana, attack, health = 4, 1, 1
    index = "SV_Fortune~Neutral~Minion~4~1~1~~Fieran, Havensent Wind God~Battlecry~Invocation~Legendary"
    requireTarget, keyWord, description = True, "", "Invocation: At the start of your turn, Rally (10) - Invoke this card.------Fanfare: If you have more evolution points than your opponent, gain +0/+2 and deal 2 damage to an enemy follower. (You have 0 evolution points on turns you are unable to evolve.)At the end of your turn, give +1/+1 to all allied followers."
    attackAdd, healthAdd = 2, 2
    name_CN = "天霸风神·斐兰"

    def __init__(self, Game, ID):
        super().__init__(Game, ID)
        self.trigsBoard = [Trig_FieranHavensentWindGod(self)]
        self.trigsDeck = [Trig_InvocationFieranHavensentWindGod(self)]

    def effCanTrig(self):
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
            if target:
                if isinstance(target, list): target = target[0]
                self.dealsDamage(target, 2)
        return None


class Trig_FieranHavensentWindGod(TrigBoard):
    def __init__(self, entity):
        super().__init__(entity, ["TurnEnds"])

    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.onBoard and ID == self.entity.ID

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        minions = self.entity.Game.minionsonBoard(self.entity.ID)
        for minion in minions:
            minion.buffDebuff(1, 1)


class Trig_InvocationFieranHavensentWindGod(TrigInvocation):
    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.inDeck and ID == self.entity.ID and self.entity.Game.space(self.entity.ID) > 0 and \
               self.entity.Game.Counters.numMinionsSummonedThisGame[self.entity.ID] >= 10


class ResolveoftheFallen(SVSpell):
    Class, school, name = "Neutral", "", "Resolve of the Fallen"
    requireTarget, mana = True, 4
    index = "SV_Fortune~Neutral~Spell~4~~Resolve of the Fallen"
    description = "Destroy an enemy follower or amulet.If at least 3 allied followers have evolved this match, recover 3 play points.Then, if at least 5 have evolved, draw 2 cards."
    name_CN = "堕落的决意"

    def effCanTrig(self):
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
    Class, race, name = "Neutral", "", "Starbright Deity"
    mana, attack, health = 5, 3, 4
    index = "SV_Fortune~Neutral~Minion~5~3~4~~Starbright Deity~Battlecry"
    requireTarget, keyWord, description = False, "", "Fanfare: Put into your hand copies of the 3 left-most cards in your hand, in the order they were added."
    attackAdd, healthAdd = 2, 2
    name_CN = "星辉女神"

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        for i in range(min(3, len(self.Game.Hand_Deck.hands[self.ID]))):
            card = self.Game.Hand_Deck.hands[self.ID][i]
            self.Game.Hand_Deck.addCardtoHand([type(card)], self.ID, byType=True)
        return None


class XXIZelgeneaTheWorld(SVMinion):
    Class, race, name = "Neutral", "", "XXI. Zelgenea, The World"
    mana, attack, health = 6, 5, 5
    index = "SV_Fortune~Neutral~Minion~5~5~5~~XXI. Zelgenea, The World~Battlecry~Invocation~Legendary"
    requireTarget, keyWord, description = False, "", "Invocation: At the start of your tenth turn, invoke this card. Then, evolve it.----------Fanfare: Restore 5 defense to your leader. If your leader had 14 defense or less before defense was restored, draw 2 cards and randomly destroy 1 of the enemy followers with the highest attack in play.Can't be evolved using evolution points. (Can be evolved using card effects.)"
    attackAdd, healthAdd = 2, 2
    name_CN = "《世界》·捷尔加内亚"

    def __init__(self, Game, ID):
        super().__init__(Game, ID)
        self.marks["Can't Evolve"] = 1
        self.trigsDeck = [Trig_InvocationXXIZelgeneaTheWorld(self)]

    def effCanTrig(self):
        self.effectViable = self.Game.heroes[self.ID].health < 15

    def afterInvocation(self, signal, ID, subject, target, number, comment):
        self.evolve()

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if self.Game.heroes[self.ID].health < 15:
            self.restoresHealth(self.Game.heroes[self.ID], 5)
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
            self.Game.Hand_Deck.drawCard(self.ID)
            self.Game.Hand_Deck.drawCard(self.ID)
        else:
            self.restoresHealth(self.Game.heroes[self.ID], 5)
        return None

    def inEvolving(self):
        trigger = Trig_AttackXXIZelgeneaTheWorld(self)
        self.trigsBoard.append(trigger)
        trigger.connect()


class Trig_AttackXXIZelgeneaTheWorld(TrigBoard):
    def __init__(self, entity):
        super().__init__(entity, ["MinionAttackingHero", "MinionAttackingMinion"])

    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
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
        super().__init__(entity, ["TurnEnds"])

    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.onBoard and ID == self.entity.ID

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        targets = [self.entity.Game.heroes[1], self.entity.Game.heroes[2]] + self.entity.Game.minionsonBoard(1) \
                  + self.entity.Game.minionsonBoard(2)
        self.entity.dealsAOE(targets, [4 for obj in targets])


class Trig_InvocationXXIZelgeneaTheWorld(TrigInvocation):
    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.inDeck and ID == self.entity.ID and self.entity.Game.space(self.entity.ID) > 0 and \
               self.entity.Game.Counters.turns[self.entity.ID] == 10


class TitanicShowdown(Amulet):
    Class, race, name = "Neutral", "", "Titanic Showdown"
    mana = 6
    index = "SV_Fortune~Neutral~Amulet~6~~Titanic Showdown~Countdown~Deathrattle"
    requireTarget, description = False, "Countdown (2) Fanfare: Put a random follower that originally costs at least 9 play points from your deck into your hand. If any other allied Titanic Showdowns are in play, recover 4 play points and banish this amulet. Last Words: At the start of your next turn, put 5 random followers that originally cost at least 9 play points from your hand into play."
    name_CN = "巨人的较劲"

    def __init__(self, Game, ID):
        super().__init__(Game, ID)
        self.counter = 2
        self.trigsBoard = [Trig_Countdown(self)]
        self.deathrattles = [Deathrattle_TitanicShowdown(self)]

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        curGame = self.Game
        if curGame.mode == 0:
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
        super().__init__(entity, ["TurnStarts"])

    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.onBoard and ID == self.entity.ID

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
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
            if i > -1: curGame.summonfrom(i, ID, -1, self.entity)
        for t in self.entity.trigsBoard:
            if type(t) == Trig_TitanicShowdown:
                t.disconnect()
                self.entity.trigsBoard.remove(t)
                break


class PureshotAngel_Accelerate(SVSpell):
    Class, school, name = "Neutral", "", "Pureshot Angel"
    requireTarget, mana = False, 2
    index = "SV_Fortune~Neutral~Spell~2~~Pureshot Angel~Accelerate~Uncollectible"
    description = "Deal 3 damage to an enemy"
    name_CN = "圣贯天使"

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        curGame = self.Game
        if curGame.mode == 0:
            if curGame.guides:
                i = curGame.guides.pop(0)
            else:
                minions = curGame.minionsAlive(3 - self.ID)
                i = npchoice(minions).pos if minions else -1
                curGame.fixedGuides.append(i)
            if i > -1:
                damage = (3 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
                self.dealsDamage(curGame.minions[3 - self.ID][i], damage)
        return None


class PureshotAngel(SVMinion):
    Class, race, name = "Neutral", "", "Pureshot Angel"
    mana, attack, health = 8, 6, 6
    index = "SV_Fortune~Neutral~Minion~8~6~6~~Pureshot Angel~Battlecry~Accelerate"
    requireTarget, keyWord, description = False, "", "Accelerate 2: Deal 1 damage to an enemy. Fanfare: xxx. Deal 3 damage to an enemy minion, and deal 1 damage to the enemy hero"
    accelerateSpell = PureshotAngel_Accelerate
    attackAdd, healthAdd = 2, 2
    name_CN = "圣贯天使"

    def getMana(self):
        if self.Game.Manas.manas[self.ID] < self.mana:
            return 2
        else:
            return self.mana

    def willAccelerate(self):
        curMana = self.Game.Manas.manas[self.ID]
        return self.mana > curMana >= 2

    def effCanTrig(self):
        if self.willAccelerate() and self.targetExists():
            self.effectViable = "sky blue"
        else:
            self.effectViable = False

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
                i = npchoice(minions).pos if minions else -1
                curGame.fixedGuides.append(i)
            if i > -1:
                self.dealsDamage(curGame.minions[3 - self.ID][i], 3)
        self.dealsDamage(self.Game.heroes[3 - self.ID], 3)
        return None


"""Forestcraft cards"""


class LumberingCarapace(SVMinion):
    Class, race, name = "Forestcraft", "", "Lumbering Carapace"
    mana, attack, health = 1, 1, 1
    index = "SV_Fortune~Forestcraft~Minion~1~1~1~~Lumbering Carapace~Battlecry"
    requireTarget, keyWord, description = False, "", "Fanfare: If at least 2 other cards were played this turn, gain +2/+2. Then, if at least 4 other cards were played this turn, gain +2/+2 more and Ward."
    attackAdd, healthAdd = 2, 2
    name_CN = "碎击巨虫"

    def effCanTrig(self):
        self.effectViable = self.Game.combCards(self.ID) >= 2

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        numCardsPlayed = self.Game.combCards(self.ID)
        if numCardsPlayed >= 2:
            self.buffDebuff(2, 2)
            if numCardsPlayed >= 4:
                self.buffDebuff(2, 2)
                self.getsStatus("Taunt")
        return None


class BlossomingArcher(SVMinion):
    Class, race, name = "Forestcraft", "", "Blossoming Archer"
    mana, attack, health = 2, 2, 2
    index = "SV_Fortune~Forestcraft~Minion~2~2~2~~Blossoming Archer"
    requireTarget, keyWord, description = False, "", "Whenever you play a card using its Accelerate effect, deal 2 damage to a random enemy follower."
    attackAdd, healthAdd = 2, 2
    name_CN = "花绽弓箭手"

    def __init__(self, Game, ID):
        super().__init__(Game, ID)
        self.trigsBoard = [Trig_BlossomingArcher(self)]


class Trig_BlossomingArcher(TrigBoard):
    def __init__(self, entity):
        super().__init__(entity, ["AccelerateBeenPlayed"])

    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
        return subject.ID == self.entity.ID and self.entity.onBoard

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
                    curGame.fixedGuides.append((enemy.pos, enemy.type + str(enemy.ID)))
                else:
                    curGame.fixedGuides.append((0, ''))
            if enemy:
                self.entity.dealsDamage(enemy, 2)


class SoothingSpell(SVSpell):
    Class, school, name = "Forestcraft", "", "Soothing Spell"
    requireTarget, mana = True, 2
    index = "SV_Fortune~Forestcraft~Spell~2~~Soothing Spell"
    description = "Restore 3 defense to an ally. If at least 2 other cards were played this turn, recover 1 evolution point."
    name_CN = "治愈的波动"

    def effCanTrig(self):
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
            if self.Game.combCards(self.ID) >= 2:
                self.Game.restoreEvolvePoint(self.ID)
        return target


class XIIWolfraudHangedMan(SVMinion):
    Class, race, name = "Forestcraft", "", "XII. Wolfraud, Hanged Man"
    mana, attack, health = 3, 3, 3
    index = "SV_Fortune~Forestcraft~Minion~3~3~3~~XII. Wolfraud, Hanged Man~Enhance~Battlecry~Legendary"
    requireTarget, keyWord, description = False, "", "Fanfare: Enhance (7) - Put a Treacherous Reversal into your hand and banish this follower. Can't be destroyed by effects. (Can be destroyed by damage from effects.)"
    attackAdd, healthAdd = 2, 2
    name_CN = "《倒吊人》·罗弗拉德"

    def __init__(self, Game, ID):
        super().__init__(Game, ID)
        self.marks["Can't Break"] = 1

    def inHandEvolving(self, target=None):
        if self.Game.combCards(self.ID) >= 3:
            self.buffDebuff(3, 3)

    def getMana(self):
        if self.Game.Manas.manas[self.ID] >= 7:
            return 7
        else:
            return self.mana

    def willEnhance(self):
        return self.Game.Manas.manas[self.ID] >= 7

    def effCanTrig(self):
        self.effectViable = self.willEnhance()

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if comment == 7:
            self.Game.banishMinion(self, self)
            self.Game.Hand_Deck.addCardtoHand([TreacherousReversal], self.ID, byType=True)
        return target


class TreacherousReversal(SVSpell):
    Class, school, name = "Forestcraft", "", "Treacherous Reversal"
    requireTarget, mana = False, 0
    index = "SV_Fortune~Forestcraft~Spell~0~~Treacherous Reversal~Uncollectible"
    description = "Banish all cards in play.Banish all cards in your hand and deck.Put copies of the first 10 cards your opponent played this match (excluding XII. Wolfraud, Hanged Man and Treacherous Reversal) into your deck, in the order they were played.Transform the Reaper at the bottom of your deck into a Victory Card.Treat allied cards that have been destroyed this match as if they were banished.At the end of your opponent's next turn, put copies of each card in your opponent's hand into your hand (excluding XII. Wolfraud, Hanged Man and Treacherous Reversal)."
    name_CN = "真伪逆转"

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        self.Game.banishMinion(self, self.Game.minionsandAmuletsonBoard(1) + self.Game.minionsandAmuletsonBoard(2))
        self.Game.Hand_Deck.extractfromHand(None, self.ID, all=True)
        self.Game.Hand_Deck.extractfromDeck(None, self.ID, all=True)
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
            self.Game.Hand_Deck.shuffleintoDeck([c(self.Game, self.ID)], creator=self)
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
        super().__init__(entity, ["TurnEnds"])

    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.onBoard and ID == self.entity.ID

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        cards = []
        for card in self.entity.Game.Hand_Deck.hands[self.entity.ID]:
            if card.name not in ["Treacherous Reversal", "XII. Wolfraud, Hanged Man"]:
                cards.append(card)
        for c in cards:
            self.entity.Game.Hand_Deck.addCardtoHand([type(c)], 3 - self.entity.ID, byType=True)
        for t in self.entity.trigsBoard:
            if type(t) == Trig_TreacherousReversal:
                t.disconnect()
                self.entity.trigsBoard.remove(t)
                break


class ReclusivePonderer_Accelerate(SVSpell):
    Class, school, name = "Forestcraft", "", "Reclusive Ponderer"
    requireTarget, mana = False, 1
    index = "SV_Fortune~Forestcraft~Spell~1~~Reclusive Ponderer~Accelerate~Uncollectible"
    description = "Draw a card."
    name_CN = "深谋的兽人"

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        self.Game.Hand_Deck.drawCard(self.ID)
        return None


class ReclusivePonderer(SVMinion):
    Class, race, name = "Forestcraft", "", "Reclusive Ponderer"
    mana, attack, health = 4, 3, 3
    index = "SV_Fortune~Forestcraft~Minion~4~3~3~~Reclusive Ponderer~Stealth~Accelerate"
    requireTarget, keyWord, description = False, "Stealth", "Accelerate (1): Draw a card. Ambush."
    accelerateSpell = ReclusivePonderer_Accelerate
    attackAdd, healthAdd = 2, 2
    name_CN = "深谋的兽人"

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


class ChipperSkipper_Accelerate(SVSpell):
    Class, school, name = "Forestcraft", "", "Chipper Skipper"
    requireTarget, mana = False, 1
    index = "SV_Fortune~Forestcraft~Spell~1~~Chipper Skipper~Accelerate~Uncollectible"
    description = "Summon a Fighter"
    name_CN = "船娘精灵"

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        self.Game.summon([Fighter(self.Game, self.ID)], (-1, "totheRightEnd"),
                         self)
        return None


class ChipperSkipper(SVMinion):
    Class, race, name = "Forestcraft", "", "Chipper Skipper"
    mana, attack, health = 4, 4, 3
    index = "SV_Fortune~Forestcraft~Minion~4~4~3~~Chipper Skipper~Accelerate"
    requireTarget, keyWord, description = False, "", "Accelerate (1): Summon a Fighter.(Can only Accelerate if a follower was played this turn.)Whenever you play a card using its Accelerate effect, summon a Fighter and evolve it."
    accelerateSpell = ChipperSkipper_Accelerate
    attackAdd, healthAdd = 2, 2
    name_CN = "船娘精灵"

    def __init__(self, Game, ID):
        super().__init__(Game, ID)
        self.trigsBoard = [Trig_ChipperSkipper(self)]

    def getMana(self):
        if self.Game.Manas.manas[self.ID] < self.mana and self.Game.Counters.numMinionsPlayedThisTurn[self.ID] > 0:
            return 1
        else:
            return self.mana

    def willAccelerate(self):
        curMana = self.Game.Manas.manas[self.ID]
        return self.mana > curMana >= 1 and self.Game.Counters.numMinionsPlayedThisTurn[self.ID] > 0

    def effCanTrig(self):
        if self.willAccelerate() and self.targetExists():
            self.effectViable = "sky blue"
        else:
            self.effectViable = False


class Trig_ChipperSkipper(TrigBoard):
    def __init__(self, entity):
        super().__init__(entity, ["AccelerateBeenPlayed"])

    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
        return subject.ID == self.entity.ID and self.entity.onBoard

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        fighter = Fighter(self.entity.Game, self.entity.ID)
        self.entity.Game.summon([fighter], (-1, "totheRightEnd"),
                                self.entity)
        fighter.evolve()


class FairyAssault(SVSpell):
    Class, school, name = "Forestcraft", "", "Fairy Assault"
    requireTarget, mana = False, 4
    index = "SV_Fortune~Forestcraft~Spell~4~~Fairy Assault"
    description = "Summon 4 Fairies and give them Rush. Enhance (8): Evolve them instead."
    name_CN = "妖精突击"

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
        minions = [Fairy(self.Game, self.ID) for i in range(4)]
        self.Game.summon(minions, (-1, "totheRightEnd"), self)
        if comment == 8:
            for minion in minions:
                if minion.onBoard:
                    minion.evolve()
        else:
            for minion in minions:
                if minion.onBoard:
                    minion.getsStatus("Rush")
        return None


class OptimisticBeastmaster(SVMinion):
    Class, race, name = "Forestcraft", "", "Optimistic Beastmaster"
    mana, attack, health = 5, 4, 5
    index = "SV_Fortune~Forestcraft~Minion~5~4~5~~Optimistic Beastmaster~Battlecry"
    requireTarget, keyWord, description = False, "", "Fanfare: Put a random follower with Accelerate from your deck into your hand. Whenever you play a card using its Accelerate effect, deal 2 damage to all enemies."
    attackAdd, healthAdd = 2, 2
    name_CN = "赞誉之驭兽使"

    def __init__(self, Game, ID):
        super().__init__(Game, ID)
        self.trigsBoard = [Trig_OptimisticBeastmaster(self)]

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        curGame = self.Game
        if curGame.mode == 0:
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
        super().__init__(entity, ["AccelerateBeenPlayed"])

    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
        return subject.ID == self.entity.ID and self.entity.onBoard

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        enemies = self.entity.Game.minionsonBoard(3 - self.entity.ID) + self.entity.Game.heroes[3 - self.entity.ID]
        self.entity.dealsAOE(enemies, [2 for obj in enemies])


class Terrorformer(SVMinion):
    Class, race, name = "Forestcraft", "", "Terrorformer"
    mana, attack, health = 6, 4, 4
    index = "SV_Fortune~Forestcraft~Minion~6~4~4~~Terrorformer~Battlecry~Fusion~Legendary"
    requireTarget, keyWord, description = True, "", "Fusion: Forestcraft followers that originally cost 2 play points or more. Whenever 2 or more cards are fused to this card at once, gain +2/+0 and draw a card. Fanfare: If at least 2 cards are fused to this card, gain Storm. Then, if at least 4 cards are fused to this card, destroy an enemy follower."
    attackAdd, healthAdd = 2, 2
    name_CN = "裂地异种"

    def __init__(self, Game, ID):
        super().__init__(Game, ID)
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

    def effCanTrig(self):
        self.effectViable = self.fusionMaterials >= 2

    def fusionDecided(self, objs):
        if objs:
            self.fusionMaterials += len(objs)
            self.Game.Hand_Deck.extractfromHand(self, enemyCanSee=True)
            for obj in objs: self.Game.Hand_Deck.extractfromHand(obj, enemyCanSee=True)
            self.Game.Hand_Deck.addCardtoHand(self, self.ID)
            if len(objs) >= 2:
                self.buffDebuff(2, 0)
                self.Game.Hand_Deck.drawCard(self.ID)
            self.fusion = 0  # 一张卡每回合只有一次融合机会

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if self.fusionMaterials >= 2:
            self.getsStatus("Charge")
            if self.fusionMaterials > 4 and target:
                if isinstance(target, list): target = target[0]
                self.Game.killMinion(self, target)
        return target


class DeepwoodWolf_Accelerate(SVSpell):
    Class, school, name = "Forestcraft", "", "Deepwood Wolf"
    requireTarget, mana = True, 1
    index = "SV_Fortune~Forestcraft~Spell~1~~Deepwood Wolf~Accelerate~Uncollectible"
    description = "Return an allied follower or amulet to your hand. Draw a card."
    name_CN = "森林之狼"

    def targetCorrect(self, target, choice=0):
        if isinstance(target, list): target = target[0]
        return target.type in ["Minion", "Amulet"] and target.ID == self.ID and target.onBoard

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if target:
            if isinstance(target, list): target = target[0]
            self.Game.returnMiniontoHand(target, deathrattlesStayArmed=False)
            self.Game.Hand_Deck.drawCard(self.ID)
        return target


class DeepwoodWolf(SVMinion):
    Class, race, name = "Forestcraft", "", "Deepwood Wolf"
    mana, attack, health = 7, 3, 3
    index = "SV_Fortune~Forestcraft~Minion~7~3~3~~Deepwood Wolf~Charge~Accelerate"
    requireTarget, keyWord, description = True, "Charge", "Accelerate (1): Return an allied follower or amulet to your hand. Draw a card. Storm. When you play a card using its Accelerate effect, evolve this follower."
    accelerateSpell = DeepwoodWolf_Accelerate
    attackAdd, healthAdd = 3, 3
    name_CN = "森林之狼"

    def __init__(self, Game, ID):
        super().__init__(Game, ID)
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

    def effCanTrig(self):
        if self.willAccelerate() and self.targetExists():
            self.effectViable = "sky blue"
        else:
            self.effectViable = False

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
        super().__init__(entity, ["AccelerateBeenPlayed"])

    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
        return subject.ID == self.entity.ID and self.entity.onBoard

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        self.entity.evolve()


class LionelWoodlandShadow_Accelerate(SVSpell):
    Class, school, name = "Forestcraft", "", "Lionel, Woodland Shadow"
    requireTarget, mana = True, 1
    index = "SV_Fortune~Forestcraft~Spell~1~~Lionel, Woodland Shadow~Accelerate~Uncollectible"
    description = "Deal 5 damage to an enemy"
    name_CN = "森之暗念·莱昂内尔"

    def targetCorrect(self, target, choice=0):
        if isinstance(target, list): target = target[0]
        return target.type == "Minion" and target.ID != self.ID and target.onBoard

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if target:
            if isinstance(target, list): target = target[0]
            damage = (5 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
            self.dealsDamage(target, damage)
        return target


class LionelWoodlandShadow(SVMinion):
    Class, race, name = "Forestcraft", "", "Lionel, Woodland Shadow"
    mana, attack, health = 7, 5, 6
    index = "SV_Fortune~Forestcraft~Minion~7~5~6~~Lionel, Woodland Shadow~Battlecry~Accelerate"
    requireTarget, keyWord, description = True, "", "Accelerate 2: Deal 1 damage to an enemy. Fanfare: xxx. Deal 3 damage to an enemy minion, and deal 1 damage to the enemy hero"
    accelerateSpell = LionelWoodlandShadow_Accelerate
    attackAdd, healthAdd = 2, 2
    name_CN = "森之暗念·莱昂内尔"

    def __init__(self, Game, ID):
        super().__init__(Game, ID)
        self.trigsBoard = [Trig_LionelWoodlandShadow(self)]

    def getMana(self):
        if self.Game.Manas.manas[self.ID] < self.mana and self.Game.Counters.evolvedThisTurn[self.ID] > 0:
            return 1
        else:
            return self.mana

    def willAccelerate(self):
        curMana = self.Game.Manas.manas[self.ID]
        return self.mana > curMana >= 1 and self.Game.Counters.evolvedThisTurn[self.ID] > 0

    def effCanTrig(self):
        if self.willAccelerate() and self.targetExists():
            self.effectViable = "sky blue"
        else:
            self.effectViable = False

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
            self.dealsDamage(target, 5)
            if health <= 5:
                self.evolve()
        return target

    def inEvolving(self):
        trigger = Trig_LionelWoodlandShadow(self)
        self.trigsBoard.append(trigger)
        trigger.connect()


class Trig_LionelWoodlandShadow(TrigBoard):
    def __init__(self, entity):
        super().__init__(entity, ["MinionPlayed"])

    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.onBoard and subject.ID != self.entity.ID

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
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
        super().__init__(entity, ["TurnEnds"])

    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
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
    name_CN = "武器商人·艾尔涅丝塔"

    def effCanTrig(self):
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
    name_CN = "恐惧猎犬"

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
                    curGame.fixedGuides.append((minion.pos, minion.type + str(minion.ID)))
                else:
                    curGame.fixedGuides.append((0, ''))
            if minion:
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
                    curGame.fixedGuides.append((enemy.pos, enemy.type + str(enemy.ID)))
                else:
                    curGame.fixedGuides.append((0, ''))
            if enemy:
                self.entity.dealsDamage(enemy, 4)


class PompousSummons(SVSpell):
    Class, school, name = "Swordcraft", "", "Pompous Summons"
    requireTarget, mana = False, 1
    index = "SV_Fortune~Swordcraft~Spell~1~~Pompous Summons"
    description = "Put a random Swordcraft follower from your deck into your hand.Rally (10): Put 2 random Swordcraft followers into your hand instead."
    name_CN = "任性的差遣"

    def effCanTrig(self):
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
        return None


class DecisiveStrike(SVSpell):
    Class, school, name = "Swordcraft", "", "Decisive Strike"
    requireTarget, mana = True, 1
    index = "SV_Fortune~Swordcraft~Spell~1~~Decisive Strike~Enhance"
    description = "Deal X damage to an enemy follower. X equals the attack of the highest-attack Commander follower in your hand.Enhance (5): Deal X damage to all enemy followers instead."
    name_CN = "所向披靡"

    def getMana(self):
        if self.Game.Manas.manas[self.ID] >= 5:
            return 5
        else:
            return self.mana

    def willEnhance(self):
        return self.Game.Manas.manas[self.ID] >= 5

    def effCanTrig(self):
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
        else:
            if target:
                if isinstance(target, list): target = target[0]
                self.dealsDamage(target, damage)
        return target


class HonorableThief(SVMinion):
    Class, race, name = "Swordcraft", "Officer", "Honorable Thief"
    mana, attack, health = 2, 2, 1
    index = "SV_Fortune~Swordcraft~Minion~2~2~1~Officer~Honorable Thief~Battlecry~Deathrattle"
    requireTarget, keyWord, description = False, "", "Fanfare: Rally (7) - Evolve this follower. Last Words: Put a Gilded Boots into your hand."
    attackAdd, healthAdd = 2, 2
    name_CN = "诚实的盗贼"

    def __init__(self, Game, ID):
        super().__init__(Game, ID)
        self.deathrattles = [Deathrattle_HonorableThief(self)]

    def effCanTrig(self):
        self.effectViable = self.Game.Counters.numMinionsSummonedThisGame[self.ID] >= 7

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if self.Game.Counters.numMinionsSummonedThisGame[self.ID] >= 7:
            self.evolve()
        return None


class Deathrattle_HonorableThief(Deathrattle_Minion):
    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        self.entity.Game.Hand_Deck.addCardtoHand(GildedBoots, self.entity.ID, byType=True)


class ShieldPhalanx(SVSpell):
    Class, school, name = "Swordcraft", "", "Shield Phalanx"
    requireTarget, mana = False, 2
    index = "SV_Fortune~Swordcraft~Spell~2~~Shield Phalanx"
    description = "Summon a Shield Guardian and Knight.Rally (15): Summon a Frontguard General instead of a Shield Guardian."
    name_CN = "坚盾战阵"

    def effCanTrig(self):
        self.effectViable = self.Game.Counters.numMinionsSummonedThisGame[self.ID] >= 15

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if self.Game.Counters.numMinionsSummonedThisGame[self.ID] >= 15:
            self.Game.summon([FrontguardGeneral(self.Game, self.ID), Knight(self.Game, self.ID)],
                             (-1, "totheRightEnd"), self)
        else:
            self.Game.summon([ShieldGuardian(self.Game, self.ID), Knight(self.Game, self.ID)],
                             (-1, "totheRightEnd"), self)
        return None


class FrontguardGeneral(SVMinion):
    Class, race, name = "Swordcraft", "Commander", "Frontguard General"
    mana, attack, health = 7, 5, 6
    index = "SV_Fortune~Swordcraft~Minion~7~5~6~Commander~Frontguard General~Taunt~Deathrattle"
    requireTarget, keyWord, description = False, "Taunt", "Ward.Last Words: Summon a Fortress Guard."
    attackAdd, healthAdd = 2, 2
    name_CN = "铁卫战将"

    def __init__(self, Game, ID):
        super().__init__(Game, ID)
        self.deathrattles = [Deathrattle_FrontguardGeneral(self)]


class Deathrattle_FrontguardGeneral(Deathrattle_Minion):
    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        self.entity.Game.summon([FortressGuard(self.entity.Game, self.entity.ID)], (-1, "totheRightEnd"),
                                self.entity)


class FortressGuard(SVMinion):
    Class, race, name = "Swordcraft", "Officer", "Fortress Guard"
    mana, attack, health = 3, 2, 3
    index = "SV_Fortune~Swordcraft~Minion~3~2~3~Officer~Fortress Guard~Taunt~Uncollectible"
    requireTarget, keyWord, description = False, "Taunt", "Ward"
    attackAdd, healthAdd = 2, 2
    name_CN = "神盾卫士"


class EmpressofSerenity(SVMinion):
    Class, race, name = "Swordcraft", "Commander", "Empress of Serenity"
    mana, attack, health = 3, 2, 2
    index = "SV_Fortune~Swordcraft~Minion~3~2~2~Commander~Empress of Serenity~Battlecry~Enhance"
    requireTarget, keyWord, description = False, "", "Fanfare: Summon a Shield Guardian.Enhance (5): Summon 3 instead.Enhance (10): Give +3/+3 to all allied Shield Guardians."
    attackAdd, healthAdd = 2, 2
    name_CN = "安宁的女王"

    def getMana(self):
        if self.Game.Manas.manas[self.ID] >= 10:
            return 10
        elif self.Game.Manas.manas[self.ID] >= 5:
            return 5
        else:
            return self.mana

    def willEnhance(self):
        return self.Game.Manas.manas[self.ID] >= 5

    def effCanTrig(self):
        self.effectViable = self.willEnhance()

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        self.Game.summon([ShieldGuardian(self.Game, self.ID)], (-11, "totheRightEnd"), self)
        if comment >= 5:
            self.Game.summon([ShieldGuardian(self.Game, self.ID) for i in range(2)], (-11, "totheRightEnd"),
                             self)
            if comment == 10:
                for minion in self.Game.minionsonBoard(self.ID):
                    if type(minion) == ShieldGuardian:
                        minion.buffDebuff(3, 3)
        return None


class VIIOluonTheChariot(SVMinion):
    Class, race, name = "Swordcraft", "Commander", "VII. Oluon, The Chariot"
    mana, attack, health = 3, 3, 3
    index = "SV_Fortune~Swordcraft~Minion~3~3~3~Commander~VII. Oluon, The Chariot~Battlecry~Legendary"
    requireTarget, keyWord, description = False, "", "Fanfare: Enhance (7) - Transform this follower into a VII. Oluon, Runaway Chariot.At the end of your turn, randomly activate 1 of the following effects.-Gain Ward.-Summon a Knight.-Deal 2 damage to the enemy leader."
    attackAdd, healthAdd = 2, 2
    name_CN = "《战车》·奥辂昂"

    def __init__(self, Game, ID):
        super().__init__(Game, ID)
        self.trigsBoard = [Trig_VIIOluonTheChariot(self)]

    def getMana(self):
        if self.Game.Manas.manas[self.ID] >= 7:
            return 7
        else:
            return self.mana

    def willEnhance(self):
        return self.Game.Manas.manas[self.ID] >= 7

    def effCanTrig(self):
        self.effectViable = self.willEnhance()

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if comment == 7:
            self.Game.transform(self, VIIOluonRunawayChariot(self.Game, self.ID))
        return None


class Trig_VIIOluonTheChariot(TrigBoard):
    def __init__(self, entity):
        super().__init__(entity, ["TurnEnds"])

    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
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
            self.entity.getsStatus("Taunt")
        elif e == "H":
            self.entity.dealsDamage(self.entity.Game.heroes[3 - self.entity.ID], 2)
        elif e == "K":
            self.entity.Game.summon([Knight(self.entity.Game, self.entity.ID)], (-11, "totheRightEnd"),
                                    self.entity)


class VIIOluonRunawayChariot(SVMinion):
    Class, race, name = "Swordcraft", "Commander", "VII. Oluon, Runaway Chariot"
    mana, attack, health = 7, 8, 16
    index = "SV_Fortune~Swordcraft~Minion~7~8~16~Commander~VII. Oluon, Runaway Chariot~Uncollectible~Legendary"
    requireTarget, keyWord, description = False, "", "Can't attack.At the end of your turn, randomly deal X damage to an enemy or another ally and then Y damage to this follower. X equals this follower's attack and Y equals the attack of the follower or leader damaged (leaders have 0 attack). Do this 2 times."
    attackAdd, healthAdd = 2, 2
    name_CN = "《暴走》战车·奥辂昂"

    def __init__(self, Game, ID):
        super().__init__(Game, ID)
        self.marks["Can't Attack"] = 1
        self.trigsBoard = [Trig_VIIOluonRunawayChariot(self)]


class Trig_VIIOluonRunawayChariot(TrigBoard):
    def __init__(self, entity):
        super().__init__(entity, ["TurnEnds"])

    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
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
                            curGame.fixedGuides.append((char.pos, char.type + str(char.ID)))
                        else:
                            curGame.fixedGuides.append((0, ''))
                    if char:
                        self.entity.dealsDamage(char, self.entity.attack)
                        damage = 0
                        if char.type == "Minion":
                            damage = char.attack
                        char.dealsDamage(self.entity, damage)
                        self.entity.Game.gathertheDead()


class PrudentGeneral(SVMinion):
    Class, race, name = "Swordcraft", "Commander", "PrudentGeneral"
    mana, attack, health = 4, 3, 4
    index = "SV_Fortune~Swordcraft~Minion~4~3~4~Commander~Prudent General"
    requireTarget, keyWord, description = False, "", ""
    attackAdd, healthAdd = 2, 2
    name_CN = "静寂的元帅"

    def inHandEvolving(self, target=None):
        trigger = Trig_PrudentGeneral(self.Game.heroes[self.ID])
        for t in self.Game.heroes[self.ID].trigsBoard:
            if type(t) == type(trigger):
                return
        self.Game.heroes[self.ID].trigsBoard.append(trigger)
        trigger.connect()


class Trig_PrudentGeneral(TrigBoard):
    def __init__(self, entity):
        super().__init__(entity, ["TurnEnds"])

    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.onBoard and ID == self.entity.ID

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        self.entity.Game.summon([SteelcladKnight(self.entity.Game, self.entity.ID)], (-1, "totheRightEnd"),
                                self.entity)


class StrikelanceKnight(SVMinion):
    Class, race, name = "Swordcraft", "Officer", "Strikelance Knight"
    mana, attack, health = 5, 4, 5
    index = "SV_Fortune~Swordcraft~Minion~5~4~5~Officer~Strikelance Knight~Battlecry"
    requireTarget, keyWord, description = False, "", "Fanfare: If an allied Commander card is in play, evolve this follower."
    attackAdd, healthAdd = 2, 2
    name_CN = "冲锋骑士"

    def effCanTrig(self):
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
    name_CN = "耀钻圣骑士"

    def __init__(self, Game, ID):
        super().__init__(Game, ID)
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

    def effCanTrig(self):
        self.effectViable = self.willEnhance()

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if comment == 8:
            self.marks["Free Evolve"] += 1
        return None

    def inHandEvolving(self, target=None):
        if target:
            if isinstance(target, list): target = target[0]
            target.buffDebuff(-4, 0)
        return target

    def extraTargetCorrect(self, target, affair):
        return target.type and target.type == "Minion" and target.ID != self.ID and target.onBoard


class Trig_DiamondPaladin(TrigBoard):
    def __init__(self, entity):
        super().__init__(entity, ["MinionAttackedMinion"])

    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
        return subject == self.entity and self.entity.onBoard and (target.health < 1 or target.dead == True) and \
               (self.entity.health > 0 and self.entity.dead == False)

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        self.entity.getsStatus("Windfury")
        self.entity.Game.Manas.restoreManaCrystal(2, self.entity.ID)
        trigger = Trig_EndDiamondPaladin(self.entity)
        self.entity.trigsBoard.append(trigger)
        if self.entity.onBoard:
            trigger.connect()


class Trig_EndDiamondPaladin(TrigBoard):
    def __init__(self, entity):
        super().__init__(entity, ["TurnEnds"])

    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
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
    name_CN = "无私的贵族"

    def targetExists(self, choice=0):
        return len(self.Game.Hand_Deck.hands[self.ID]) > 1

    def targetCorrect(self, target, choice=0):
        if isinstance(target, list): target = target[0]
        return target.ID == self.ID and target.inHand and target != self

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if target:
            if isinstance(target, list): target = target[0]
            n = type(target).mana
            self.Game.Hand_Deck.discard(self.ID, target)
            self.buffDebuff(n, n)
        return target


"""Runecraft cards"""


class JugglingMoggy(SVMinion):
    Class, race, name = "Runecraft", "", "Juggling Moggy"
    mana, attack, health = 1, 1, 1
    index = "SV_Fortune~Runecraft~Minion~1~1~1~~Juggling Moggy~Battlecry~EarthRite"
    requireTarget, keyWord, description = False, "", "Fanfare: Earth Rite - Gain +1/+1 and Last Words: Summon 2 Earth Essences."
    attackAdd, healthAdd = 2, 2
    name_CN = "魔猫魔术师"

    def effCanTrig(self):
        self.effectViable = len(self.Game.earthsonBoard(self.ID)) > 0

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if self.Game.earthRite(self, self.ID):
            self.buffDebuff(1, 1)
            deathrattle = Deathrattle_JugglingMoggy(self)
            self.deathrattles.append(deathrattle)
            if self.onBoard:
                deathrattle.connect()
        return None


class Deathrattle_JugglingMoggy(Deathrattle_Minion):
    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        self.entity.Game.summon([EarthEssence(self.entity.Game, self.entity.ID) for i in range(2)],
                                (-1, "totheRightEnd"), self.entity)


class MagicalAugmentation(SVSpell):
    Class, school, name = "Runecraft", "", "Magical Augmentation"
    requireTarget, mana = True, 1
    index = "SV_Fortune~Runecraft~Spell~1~~Magical Augmentation~EarthRite"
    description = "Deal 1 damage to an enemy follower. Earth Rite (2): Deal 4 damage instead. Then draw 2 cards."
    name_CN = "扩展的魔法"

    def effCanTrig(self):
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
                self.dealsDamage(target, damage)
                self.Game.Hand_Deck.drawCard(self.ID)
                self.Game.Hand_Deck.drawCard(self.ID)
            else:
                damage = (1 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
                self.dealsDamage(target, damage)
        return target


class CreativeConjurer(SVMinion):
    Class, race, name = "Runecraft", "", "Creative Conjurer"
    mana, attack, health = 2, 2, 2
    index = "SV_Fortune~Runecraft~Minion~2~2~2~~Creative Conjurer~Battlecry~EarthRite"
    requireTarget, keyWord, description = False, "", "Fanfare: If there are no allied Earth Sigil amulets in play, summon an Earth Essence. Otherwise, perform Earth Rite: Put a Golem Summoning into your hand."
    attackAdd, healthAdd = 2, 2
    name_CN = "创物魔法师"

    def effCanTrig(self):
        self.effectViable = len(self.Game.earthsonBoard(self.ID)) >= 0

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if self.Game.earthRite(self, self.ID):
            self.Game.Hand_Deck.addCardtoHand(GolemSummoning, self.ID, byType=True)
        else:
            self.Game.summon([EarthEssence(self.Game, self.ID)], (-1, "totheRightEnd"), self)
        return None


class GolemSummoning(SVSpell):
    Class, school, name = "Runecraft", "", "Golem Summoning"
    requireTarget, mana = False, 2
    index = "SV_Fortune~Runecraft~Spell~2~~Golem Summoning~Uncollectible"
    description = "Summon a Guardian Golem. If you have 20 cards or less in your deck, evolve it."
    name_CN = "巨像创造"

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        minion = GuardianGolem(self.Game, self.ID)
        self.Game.summon([minion], (-1, "totheRightEnd"), self)
        if len(self.Game.Hand_Deck.decks[self.ID]) <= 20:
            minion.evolve()
        return None


class LhynkalTheFool(SVMinion):
    Class, race, name = "Runecraft", "", "0. Lhynkal, The Fool"
    mana, attack, health = 2, 2, 2
    index = "SV_Fortune~Runecraft~Minion~2~2~2~~0. Lhynkal, The Fool~Battlecry~Choose~Legendary"
    requireTarget, keyWord, description = False, "", "Fanfare: Choose - Put a Rite of the Ignorant or Scourge of the Omniscient into your hand."
    attackAdd, healthAdd = 2, 2
    name_CN = "《愚者》·琳库露"

    def inHandEvolving(self, target=None):
        self.Game.Manas.restoreManaCrystal(2, self.ID)

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        self.Game.options = [RiteoftheIgnorant(self.Game, self.ID), ScourgeoftheOmniscient(self.Game, self.ID)]
        self.Game.Discover.startDiscover(self)
        return None

    def discoverDecided(self, option, pool):
        self.Game.fixedGuides.append(type(option))
        self.Game.Hand_Deck.addCardtoHand(option, self.ID, byDiscover=True)


class RiteoftheIgnorant(SVSpell):
    Class, school, name = "Runecraft", "", "Rite of the Ignorant"
    requireTarget, mana = False, 4
    index = "SV_Fortune~Runecraft~Spell~4~~Rite of the Ignorant~Uncollectible~Legendary"
    description = "Give your leader the following effect: At the start of your turn, draw a card and Spellboost it X times. X equals a random number between 1 and 10. Then give it the following effect: At the end of your turn, discard this card. (This leader effect lasts for the rest of the match.)"
    name_CN = "蒙昧的术式"

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
        super().__init__(entity, ["TurnStarts"])

    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
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


class Trig_EndRiteoftheIgnorant(TrigHand):
    def __init__(self, entity):
        super().__init__(entity, ["TurnEnds"])
        self.temp = True
        self.changesCard = True

    # They will be discarded at the end of any turn
    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.inHand

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        self.entity.Game.Hand_Deck.discard(self.entity.ID, self.entity)


class ScourgeoftheOmniscient(SVSpell):
    Class, school, name = "Runecraft", "", "Scourge of the Omniscient"
    requireTarget, mana = False, 2
    index = "SV_Fortune~Runecraft~Spell~2~~Scourge of the Omniscient~Uncollectible~Legendary"
    description = "Give the enemy leader the following effect: At the end of your turn, reduce your leader's maximum defense by 1. (This effect lasts for the rest of the match.)"
    name_CN = "剥落的镇压"

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
        super().__init__(entity, ["TurnEnds"])

    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.onBoard and ID == self.entity.ID

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        self.entity.health_max -= 1
        self.entity.health = min(self.entity.health, self.entity.health_max)


class AuthoringTomorrow(SVSpell):
    Class, school, name = "Runecraft", "", "Authoring Tomorrow"
    requireTarget, mana = False, 2
    index = "SV_Fortune~Runecraft~Spell~2~~Authoring Tomorrow"
    description = "Give your leader the following effect: At the end of your turn, if it is your second, fourth, sixth, or eighth turn, deal 1 damage to all enemy followers. If it is your third, fifth, seventh, or ninth turn, draw a card. If it is your tenth turn or later, deal 5 damage to the enemy leader. (This effect is not stackable and is removed after activating 3 times.)"
    name_CN = "预知未来"

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        trigger = Trig_AuthoringTomorrow(self.Game.heroes[self.ID])
        for t in self.Game.heroes[self.ID].trigsBoard:
            if type(t) == type(trigger):
                return
        self.Game.heroes[self.ID].trigsBoard.append(trigger)
        trigger.connect()
        return None


class Trig_AuthoringTomorrow(TrigBoard):
    def __init__(self, entity):
        super().__init__(entity, ["TurnEnds"])
        self.counter = 3

    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.onBoard and ID == self.entity.ID

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        turn = self.entity.Game.Counters.turns[self.entity.ID]
        if turn in [2, 4, 6, 8]:
            targets = self.entity.Game.minionsonBoard(3 - self.entity.ID)
            if targets:
                self.entity.dealsAOE(targets, [1 for obj in targets])
        elif turn in [3, 5, 7, 9]:
            self.entity.Game.Hand_Deck.drawCard(self.entity.ID)
        elif turn >= 10:
            self.entity.dealsDamage(self.entity.Game.heroes[3 - self.entity.ID], 5)
        self.counter -= 1
        if self.counter <= 0:
            for t in self.entity.trigsBoard:
                if t == self:
                    t.disconnect()
                    self.entity.trigsBoard.remove(t)
                    break


class MadcapConjuration(SVSpell):
    Class, school, name = "Runecraft", "", "Madcap Conjuration"
    requireTarget, mana = False, 2
    index = "SV_Fortune~Runecraft~Spell~2~~Madcap Conjuration"
    description = "Discard your hand.If at least 2 spells were discarded, draw 5 cards.If at least 2 followers were discarded, destroy all followers.If at least 2 amulets were discarded, summon 2 Clay Golems and deal 2 damage to the enemy leader."
    name_CN = "乱无章法的嵌合"

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        hands = self.Game.Hand_Deck.hands[self.ID]
        types = {"Spell": 0, "Minion": 0, "Amulet": 0}
        for card in hands:
            if card.type in types:
                types[card.type] += 1
        self.Game.Hand_Deck.discardAll(self.ID)
        if types["Spell"] >= 2:
            for i in range(5):
                self.Game.Hand_Deck.drawCard(self.ID)
        if types["Minion"] >= 2:
            self.Game.killMinion(self, self.Game.minionsAlive(1) + self.Game.minionsAlive(2))
        if types["Amulet"] >= 2:
            self.Game.summon([ClayGolem(self.Game, self.ID) for i in range(2)], (-1, "totheRightEnd"), self)
            damage = (2 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
            self.dealsDamage(self.Game.heroes[3 - self.ID], damage)


class ArcaneAuteur(SVMinion):
    Class, race, name = "Runecraft", "", "Arcane Auteur"
    mana, attack, health = 3, 3, 3
    index = "SV_Fortune~Runecraft~Minion~3~3~3~~Arcane Auteur~Deathrattle"
    requireTarget, keyWord, description = False, "", "Last Words: Put an Insight into your hand."
    attackAdd, healthAdd = 2, 2
    name_CN = "魔导书撰写者"

    def __init__(self, Game, ID):
        super().__init__(Game, ID)
        self.deathrattles = [Deathrattle_ArcaneAuteur(self)]


class Deathrattle_ArcaneAuteur(Deathrattle_Minion):
    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        self.entity.Game.Hand_Deck.addCardtoHand(Insight, self.entity.ID, byType=True)


class PiquantPotioneer(SVMinion):
    Class, race, name = "Runecraft", "", "Piquant Potioneer"
    mana, attack, health = 4, 3, 3
    index = "SV_Fortune~Runecraft~Minion~4~3~3~~Piquant Potioneer~Battlecry"
    requireTarget, keyWord, description = False, "", "Fanfare: Deal 1 damage to all enemy followers. If you have 20 cards or less in your deck, deal 3 damage instead."
    attackAdd, healthAdd = 2, 2
    name_CN = "魔药巫师"

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        damage = 1
        if len(self.Game.Hand_Deck.decks[self.ID]) <= 20:
            damage = 3
        targets = self.Game.minionsonBoard(3 - self.ID)
        self.dealsAOE(targets, damage)


class ImperatorofMagic(SVMinion):
    Class, race, name = "Runecraft", "", "Imperator of Magic"
    mana, attack, health = 4, 2, 2
    index = "SV_Fortune~Runecraft~Minion~4~2~2~~Imperator of Magic~Battlecry~Enhance~EarthRite"
    requireTarget, keyWord, description = False, "", "Fanfare: Earth Rite - Summon an Emergency Summoning. Fanfare: Enhance (6) - Recover 1 evolution point."
    attackAdd, healthAdd = 2, 2
    evolveRequireTarget = True
    name_CN = "魔导君临者"

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

    def effCanTrig(self):
        self.effectViable = len(self.Game.earthsonBoard(self.ID)) > 0 or self.willEnhance()

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if self.Game.earthRite(self, self.ID):
            self.Game.summon(
                [EmergencySummoning(self.Game, self.ID)], (-1, "totheRightEnd"), self)
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
        return target


class EmergencySummoning(Amulet):
    Class, race, name = "Runecraft", "Earth Sigil", "Emergency Summoning"
    mana = 5
    index = "SV_Fortune~Runecraft~Amulet~5~Earth Sigil~Emergency Summoning~Deathrattle~Uncollectible"
    requireTarget, description = False, "When your opponent plays a follower, destroy this amulet. Last Words: Summon a Guardian Golem and a Clay Golem."
    name_CN = "紧急召唤"

    def __init__(self, Game, ID):
        super().__init__(Game, ID)
        self.deathrattles = [Deathrattle_EmergencySummoning(self)]
        self.trigsBoard = [Trig_EmergencySummoning(self)]


class Deathrattle_EmergencySummoning(Deathrattle_Minion):
    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        self.entity.Game.summon(
            [GuardianGolem(self.entity.Game, self.entity.ID), ClayGolem(self.entity.Game, self.entity.ID)],
            (-1, "totheRightEnd"), self.entity)


class Trig_EmergencySummoning(TrigBoard):
    def __init__(self, entity):
        super().__init__(entity, ["MinionPlayed"])

    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.onBoard and subject.ID != self.entity.ID

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        self.entity.Game.killMinion(self.entity, self.entity)


class HappyPig(SVMinion):
    Class, race, name = "Neutral", "", "Happy Pig"
    mana, attack, health = 2, 2, 2
    index = "SV_Fortune~Neutral~Minion~2~2~2~~Happy Pig~Deathrattle"
    requireTarget, keyWord, description = False, "", "Last Words: Restore 1 defense to your leader."
    attackAdd, healthAdd = 2, 2
    name_CN = "快乐小猪"

    def __init__(self, Game, ID):
        super().__init__(Game, ID)
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
        self.entity.restoresHealth(self.entity.Game.heroes[self.entity.ID], 1)


class Deathrattle_EvolvedHappyPig(Deathrattle_Minion):
    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        self.entity.restoresHealth(self.entity.Game.heroes[self.entity.ID], 3)


class SweetspellSorcerer(SVMinion):
    Class, race, name = "Runecraft", "", "Sweetspell Sorcerer"
    mana, attack, health = 5, 4, 4
    index = "SV_Fortune~Runecraft~Minion~5~4~4~~Sweetspell Sorcerer"
    requireTarget, keyWord, description = False, "", "Whenever you play a spell, summon a Happy Pig."
    attackAdd, healthAdd = 2, 2
    name_CN = "甜品魔术师"

    def __init__(self, Game, ID):
        super().__init__(Game, ID)
        self.trigsBoard = [Trig_SweetspellSorcerer(self)]

    def inHandEvolving(self, target=None):
        minions = self.Game.minionsAlive(self.ID)
        for minion in minions:
            if minion.name == "Happy Pig":
                minion.evolve()


class Trig_SweetspellSorcerer(TrigBoard):
    def __init__(self, entity):
        super().__init__(entity, ["SpellPlayed"])

    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.onBoard and subject.ID == self.entity.ID

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        self.entity.Game.summon(
            [HappyPig(self.entity.Game, self.entity.ID)], (-1, "totheRightEnd"), self.entity)


class WitchSnap(SVSpell):
    Class, school, name = "Runecraft", "", "Witch Snap"
    requireTarget, mana = True, 2
    index = "SV_Fortune~Runecraft~Spell~2~~Witch Snap"
    description = "Deal 1 damage to an enemy follower. Earth Rite (2): Deal 4 damage instead. Then draw 2 cards."
    name_CN = "魔法的一击"

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
            self.dealsDamage(target, damage)
            self.Game.Hand_Deck.addCardtoHand(EarthEssence, self.ID, byType=True)
        return target


class AdamantineGolem(SVMinion):
    Class, race, name = "Runecraft", "", "Adamantine Golem"
    mana, attack, health = 6, 6, 6
    index = "SV_Fortune~Runecraft~Minion~6~6~6~~Adamantine Golem~Battlecry~EarthRite~Legendary"
    requireTarget, keyWord, description = False, "", "During your turn, when this card is added to your hand from your deck, if there are 2 allied Earth Sigil amulets or less in play, reveal it and summon an Earth Essence.Fanfare: Randomly activate 1 of the following effects. Earth Rite (X): Do this X more times. X equals the number of allied Earth Sigil amulets in play.-Summon a Guardian Golem.-Put a Witch Snap into your hand and change its cost to 0.-Deal 2 damage to the enemy leader. Restore 2 defense to your leader."
    attackAdd, healthAdd = 2, 2
    name_CN = "精金巨像"

    def __init__(self, Game, ID):
        super().__init__(Game, ID)

    def effCanTrig(self):
        self.effectViable = len(self.Game.earthsonBoard(self.ID)) > 0

    def whenDrawn(self):
        if self.Game.turn == self.ID and len(self.Game.earthsonBoard(self.ID)) <= 2:
            self.Game.summon(
                [EarthEssence(self.Game, self.ID)], (-1, "totheRightEnd"), self)

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
                        [GuardianGolem(self.Game, self.ID)], (-1, "totheRightEnd"), self)
                elif e == "P":
                    card = WitchSnap(self.Game, self.ID)
                    self.Game.Hand_Deck.addCardtoHand(card, self.ID)
                    ManaMod(card, changeby=-2, changeto=0).applies()
                elif e == "D":
                    self.dealsDamage(self.Game.heroes[3 - self.ID], 2)
                    self.restoresHealth(self.Game.heroes[self.ID], 2)


"""Dragoncraft cards"""


class DragoncladLancer(SVMinion):
    Class, race, name = "Dragoncraft", "", "Dragonclad Lancer"
    mana, attack, health = 1, 1, 1
    index = "SV_Fortune~Dragoncraft~Minion~1~1~1~~Dragonclad Lancer~Battlecry"
    requireTarget, keyWord, description = True, "", "Fanfare: Deal 4 damage to an enemy follower."
    attackAdd, healthAdd = 2, 2
    name_CN = "龙装枪术士"

    def targetExists(self, choice=0):
        return self.selectableFriendlyMinionExists()

    def targetCorrect(self, target, choice=0):
        if isinstance(target, list): target = target[0]
        return target.type == "Minion" and target.ID == self.ID and target.onBoard

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if target:
            if isinstance(target, list): target = target[0]
            self.dealsDamage(target, 2)
            self.Game.Hand_Deck.drawCard(self.ID)
            self.buffDebuff(2, 1)
        return target


class SpringwellDragonKeeper(SVMinion):
    Class, race, name = "Dragoncraft", "", "Springwell Dragon Keeper"
    mana, attack, health = 2, 2, 2
    index = "SV_Fortune~Dragoncraft~Minion~2~2~2~~Springwell Dragon Keeper~Battlecry~Enhance"
    requireTarget, keyWord, description = True, "", "Fanfare: Discard a card and deal 4 damage to an enemy follower.(Activates only when both a targetable card is in your hand and a targetable enemy follower is in play.)Enhance (5): Gain +3/+3."
    attackAdd, healthAdd = 2, 2
    name_CN = "召水驭龙使"

    def getMana(self):
        if self.Game.Manas.manas[self.ID] >= 5:
            return 5
        else:
            return self.mana

    def willEnhance(self):
        return self.Game.Manas.manas[self.ID] >= 5

    def effCanTrig(self):
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
        if comment == 5:
            self.buffDebuff(3, 3)
        return target


class TropicalGrouper(SVMinion):
    Class, race, name = "Dragoncraft", "", "Tropical Grouper"
    mana, attack, health = 2, 1, 2
    index = "SV_Fortune~Dragoncraft~Minion~2~1~2~~Tropical Grouper~Battlecry~Enhance"
    requireTarget, keyWord, description = False, "", "Fanfare: Enhance (4) - Summon a Tropical Grouper. During your turn, whenever another allied follower evolves, summon a Tropical Grouper."
    attackAdd, healthAdd = 2, 2
    name_CN = "热带铠鱼"

    def __init__(self, Game, ID):
        super().__init__(Game, ID)
        self.trigsBoard = [Trig_TropicalGrouper(self)]

    def getMana(self):
        if self.Game.Manas.manas[self.ID] >= 4:
            return 4
        else:
            return self.mana

    def willEnhance(self):
        return self.Game.Manas.manas[self.ID] >= 4

    def effCanTrig(self):
        self.effectViable = self.willEnhance()

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if comment == 4:
            self.Game.summon([TropicalGrouper(self.Game, self.ID)], (-1, "totheRightEnd"),
                             self)


class Trig_TropicalGrouper(TrigBoard):
    def __init__(self, entity):
        super().__init__(entity, ["MinionEvolved"])

    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
        return subject.ID == self.entity.ID and self.entity.onBoard and subject != self.entity

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        self.entity.Game.summon([TropicalGrouper(self.entity.Game, self.entity.ID)], (-1, "totheRightEnd"),
                                self.entity)


class WavecrestAngler(SVMinion):
    Class, race, name = "Dragoncraft", "", "Wavecrest Angler"
    mana, attack, health = 2, 2, 2
    index = "SV_Fortune~Dragoncraft~Minion~2~2~2~~Wavecrest Angler~Battlecry"
    requireTarget, keyWord, description = False, "", "Fanfare: Randomly put a copy of a card discarded by an effect this turn into your hand."
    attackAdd, healthAdd = 2, 2
    name_CN = "大洋钓手"

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        curGame = self.Game
        if curGame.mode == 0:
            if curGame.guides:
                i = curGame.guides.pop(0)
            else:
                cards = [i for i, card in enumerate(curGame.Counters.cardsDiscardedThisTurn[self.ID])]
                i = npchoice(cards) if cards else -1
                curGame.fixedGuides.append(i)
            if i > -1:
                card = self.Game.cardPool[curGame.Counters.cardsDiscardedThisGame[self.ID][i]]
                self.Game.Hand_Deck.addCardtoHand(card, self.ID, byType=True)


class DraconicCall(SVSpell):
    Class, school, name = "Dragoncraft", "", "Draconic Call"
    mana, requireTarget = 2, False
    index = "SV_Fortune~Dragoncraft~Spell~2~~Draconic Call"
    description = "Randomly put 1 of the highest-cost Dragoncraft followers from your deck into your hand. If Overflow is active for you, randomly put 2 of the highest-cost Dragoncraft followers into your hand instead."
    name_CN = "聚龙之唤"

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
    index = "SV_Fortune~Dragoncraft~Minion~1~1~2~~Ivory Dragon~Battlecry"
    requireTarget, keyWord, description = False, "", "Fanfare: Draw a card if Overflow is active for you."
    attackAdd, healthAdd = 2, 2
    name_CN = "银白幼龙"

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if self.Game.isOverflow(self.ID):
            self.Game.Hand_Deck.drawCard(self.ID)


class Heliodragon(SVMinion):
    Class, race, name = "Dragoncraft", "", "Heliodragon"
    mana, attack, health = 3, 1, 5
    index = "SV_Fortune~Dragoncraft~Minion~3~1~5~~Heliodragon"
    requireTarget, keyWord, description = False, "", "If this card is discarded by an effect, summon an Ivory Dragon. Then, if Overflow is active for you, draw a card.During your turn, whenever you discard cards, restore X defense to your leader. X equals the number of cards discarded."
    attackAdd, healthAdd = 2, 2
    name_CN = "日轮之龙"

    def __init__(self, Game, ID):
        super().__init__(Game, ID)
        self.trigsBoard = [Trig_Heliodragon(self)]

    def whenDiscarded(self):
        self.Game.summon([IvoryDragon(self.Game, self.ID)], (-1, "totheRightEnd"),
                         self)
        if self.Game.isOverflow(self.ID):
            self.Game.Hand_Deck.drawCard(self.ID)


class Trig_Heliodragon(TrigBoard):
    def __init__(self, entity):
        super().__init__(entity, ["CardDiscarded", "HandDiscarded"])

    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
        return ID == self.entity.ID and self.entity.onBoard and number > 0

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        self.entity.restoresHealth(self.entity.Game.heroes[self.entity.ID], number)


class SlaughteringDragonewt(SVMinion):
    Class, race, name = "Dragoncraft", "", "Slaughtering Dragonewt"
    mana, attack, health = 3, 2, 8
    index = "SV_Fortune~Dragoncraft~Minion~3~2~8~~Slaughtering Dragonewt~Bane~Battlecry"
    requireTarget, keyWord, description = False, "Bane", "Fanfare: Draw a card if Overflow is active for you."
    attackAdd, healthAdd = 0, 0
    name_CN = "虐杀的龙人"

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        cards = enumerate(self.Game.Hand_Deck.decks[self.ID])
        for i, card in cards:
            if card.mana in [1, 3, 5, 7, 9]:
                self.Game.Hand_Deck.extractfromDeck(card, self.ID)

    def inHandEvolving(self, target=None):
        minions = self.Game.minionsonBoard(1) + self.Game.minionsonBoard(2)
        self.dealsAOE(minions, [4 for obj in minions])

    def canAttack(self):
        return self.actionable() and self.status["Frozen"] < 1 \
               and self.attChances_base + self.attChances_extra > self.attTimes \
               and self.marks["Can't Attack"] < 1 and self.Game.isOverflow(self.ID)


class Trig_TurncoatDragons(TrigHand):
    def __init__(self, entity):
        super().__init__(entity, ["CardDiscarded"])

    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.inHand and ID == self.entity.ID

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        self.entity.progress += 1
        self.entity.Game.Manas.calcMana_Single(self.entity)


class CrimsonDragonsSorrow(SVMinion):
    Class, race, name = "Dragoncraft", "", "Crimson Dragon's Sorrow"
    mana, attack, health = 5, 4, 4
    index = "SV_Fortune~Dragoncraft~Minion~5~4~4~~Crimson Dragon's Sorrow~Taunt~Battlecry~Legendary~Uncollectible"
    requireTarget, keyWord, description = True, "Taunt", "During your turn, whenever you discard cards, subtract X from the cost of this card. X equals the number of cards discarded.Ward.Fanfare: Discard a card. Draw 2 cards."
    attackAdd, healthAdd = 2, 2
    name_CN = "悲戚的赤龙"

    def __init__(self, Game, ID):
        super().__init__(Game, ID)
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
            self.Game.Hand_Deck.discard(self.ID, target)
            self.Game.Hand_Deck.drawCard(self.ID)
            self.Game.Hand_Deck.drawCard(self.ID)
        return target


class AzureDragonsRage(SVMinion):
    Class, race, name = "Dragoncraft", "", "Azure Dragon's Rage"
    mana, attack, health = 7, 4, 4
    index = "SV_Fortune~Dragoncraft~Minion~7~4~4~~Azure Dragon's Rage~Charge~Legendary~Uncollectible"
    requireTarget, keyWord, description = False, "Charge", "During your turn, whenever you discard cards, subtract X from the cost of this card. X equals the number of cards discarded.Ward.Fanfare: Discard a card. Draw 2 cards."
    attackAdd, healthAdd = 2, 2
    name_CN = "盛怒的碧龙"

    def __init__(self, Game, ID):
        super().__init__(Game, ID)
        self.trigsHand = [Trig_TurncoatDragons(self)]
        self.progress = 0

    def selfManaChange(self):
        if self.inHand:
            self.mana -= self.progress
            self.mana = max(self.mana, 0)


class TurncoatDragonSummoner(SVMinion):
    Class, race, name = "Dragoncraft", "", "Turncoat Dragon Summoner"
    mana, attack, health = 3, 2, 3
    index = "SV_Fortune~Dragoncraft~Minion~3~2~3~~Turncoat Dragon Summoner~Battlecry~Legendary"
    requireTarget, keyWord, description = True, "", "If this card is discarded by an effect, put a Crimson Dragon's Sorrow into your hand.Ward.Fanfare: Discard a card. Put an Azure Dragon's Rage into your hand."
    attackAdd, healthAdd = 2, 2
    name_CN = "恶极唤龙者"

    def __init__(self, Game, ID):
        super().__init__(Game, ID)

    def whenDiscarded(self):
        self.Game.Hand_Deck.addCardtoHand(CrimsonDragonsSorrow, self.ID, byType=True)

    def targetExists(self, choice=0):
        return len(self.Game.Hand_Deck.hands[self.ID]) > 1

    def targetCorrect(self, target, choice=0):
        if isinstance(target, list): target = target[0]
        return target.ID == self.ID and target.inHand and target != self

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if target:
            if isinstance(target, list): target = target[0]
            self.Game.Hand_Deck.discard(self.ID, target)
            self.Game.Hand_Deck.addCardtoHand(AzureDragonsRage, self.ID, byType=True)
        return target


class DragonsNest(Amulet):
    Class, race, name = "Dragoncraft", "", "Dragon's Nest"
    mana = 1
    index = "SV_Fortune~Dragoncraft~Amulet~1~~Dragon's Nest"
    requireTarget, description = False, "At the start of your turn, restore 2 defense to your leader, draw a card, and destroy this amulet if Overflow is active for you."
    name_CN = "龙之卵"

    def __init__(self, Game, ID):
        super().__init__(Game, ID)
        self.trigsBoard = [Trig_DragonsNest(self)]


class Trig_DragonsNest(TrigBoard):
    def __init__(self, entity):
        super().__init__(entity, ["TurnStarts"])

    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.onBoard and ID == self.entity.ID

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        if self.entity.Game.isOverflow(self.entity.ID):
            self.entity.restoresHealth(self.entity.Game.heroes[self.entity.ID], 2)
            self.entity.Game.Hand_Deck.drawCard(self.entity.ID)
            self.entity.Game.killMinion(self.entity, self.entity)


class DragonSpawning(SVSpell):
    Class, school, name = "Dragoncraft", "", "Dragon Spawning"
    mana, requireTarget = 3, False
    index = "SV_Fortune~Dragoncraft~Spell~3~~Dragon Spawning"
    description = "Summon 2 Dragon's Nests. If you have 10 play point orbs, summon 5 instead."
    name_CN = "龙之诞生"

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        n = 2
        if self.Game.Manas.manasUpper[self.ID] >= 10:
            n = 5
        self.Game.summon([DragonsNest(self.Game, self.ID) for i in range(n)], (-1, "totheRightEnd"),
                         self)


class DragonImpact(SVSpell):
    Class, school, name = "Dragoncraft", "", "Dragon Impact"
    mana, requireTarget = 4, True
    index = "SV_Fortune~Dragoncraft~Spell~4~~Dragon Impact"
    description = "Give +1/+1 and Rush to a Dragoncraft follower in your hand.Deal 5 damage to a random enemy follower.(Can be played only when a targetable card is in your hand.)"
    name_CN = "龙威迫击"

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
            target.getsStatus("Rush")
            target.buffDebuff(1, 1)
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
                        curGame.fixedGuides.append((enemy.pos, enemy.type + str(enemy.ID)))
                    else:
                        curGame.fixedGuides.append((0, ''))
                if enemy:
                    damage = (5 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
                    self.dealsDamage(enemy, damage)
        return target


class XIErntzJustice(SVMinion):
    Class, race, name = "Dragoncraft", "", "XI. Erntz, Justice"
    mana, attack, health = 10, 11, 8
    index = "SV_Fortune~Dragoncraft~Minion~10~11~8~~XI. Erntz, Justice~Ward~Legendary"
    requireTarget, keyWord, description = False, "Taunt", "Ward.When this follower comes into play, randomly activate 1 of the following effects.-Draw 3 cards.-Evolve this follower.When this follower leaves play, restore 8 defense to your leader. (Transformation doesn't count as leaving play.)"
    attackAdd, healthAdd = -3, 3
    name_CN = "《正义》·伊兰翠"

    def __init__(self, Game, ID):
        super().__init__(Game, ID)
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
            for num in range(3):
                self.Game.Hand_Deck.drawCard(self.ID)
        elif e == "E":
            self.evolve()

    def whenDisppears(self):
        self.restoresHealth(self.Game.heroes[self.ID], 8)

    def inEvolving(self):
        self.losesStatus("Taunt")
        self.getsStatus("Charge")
        self.marks["Ignore Taunt"] += 1
        self.marks["Enemy Effect Evasive"] += 1
        for f in self.disappearResponse:
            if f.__name__ == "whenDisppears":
                self.disappearResponse.remove(f)


"""Shadowcraft cards"""


class GhostlyMaid(SVMinion):
    Class, race, name = "Shadowcraft", "", "Ghostly Maid"
    mana, attack, health = 2, 2, 2
    index = "SV_Fortune~Shadowcraft~Minion~2~2~2~~Ghostly Maid~Battlecry"
    requireTarget, keyWord, description = False, "", "Fanfare: If there are any allied amulets in play, summon a Ghost. Then, if there are at least 2 in play, evolve it."
    attackAdd, healthAdd = 2, 2
    name_CN = "幽灵女仆"

    def effCanTrig(self):
        self.effectViable = len(self.Game.amuletsonBoard(self.ID)) > 0

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if len(self.Game.amuletsonBoard(self.ID)) > 0:
            minion = Ghost(self.Game, self.ID)
            self.Game.summon([minion], (-1, "totheRightEnd"),
                             self)
            if len(self.Game.amuletsonBoard(self.ID)) >= 2:
                minion.evolve()
        return None


class BonenanzaNecromancer(SVMinion):
    Class, race, name = "Shadowcraft", "", "Bonenanza Necromancer"
    mana, attack, health = 2, 2, 2
    index = "SV_Fortune~Shadowcraft~Minion~2~2~2~~Bonenanza Necromancer~Enhance~Battlecry"
    requireTarget, keyWord, description = False, "", "Fanfare: Enhance (7) - Reanimate (10). Whenever you perform Burial Rite, draw a card."
    attackAdd, healthAdd = 2, 2
    name_CN = "狂欢唤灵师"

    def __init__(self, Game, ID):
        super().__init__(Game, ID)
        self.trigsBoard = [Trig_BonenanzaNecromancer(self)]

    def getMana(self):
        if self.Game.Manas.manas[self.ID] >= 7:
            return 7
        else:
            return self.mana

    def willEnhance(self):
        return self.Game.Manas.manas[self.ID] >= 7

    def effCanTrig(self):
        self.effectViable = self.willEnhance()

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if comment == 7:
            minion = self.Game.reanimate(self.ID, 10)
        return None


class Trig_BonenanzaNecromancer(TrigBoard):
    def __init__(self, entity):
        super().__init__(entity, ["BurialRite"])

    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.onBoard and ID == self.entity.ID

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        self.entity.Game.Hand_Deck.drawCard(self.entity.ID)


class SavoringSlash(SVSpell):
    Class, school, name = "Shadowcraft", "", "Savoring Slash"
    requireTarget, mana = True, 2
    index = "SV_Fortune~Shadowcraft~Spell~2~~Savoring Slash"
    description = "Deal 3 damage to an enemy follower. Burial Rite: Draw a card."
    name_CN = "饥欲斩击"

    def effCanTrig(self):
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
                self.Game.Hand_Deck.burialRite(self.ID, allied)
                self.Game.Hand_Deck.drawCard(self.ID)
            else:
                enemy = target[0]
            damage = (3 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
            self.dealsDamage(enemy, damage)
        return target


class CoffinoftheUnknownSoul(Amulet):
    Class, race, name = "Shadowcraft", "", "Coffin of the Unknown Soul"
    mana = 2
    index = "SV_Fortune~Shadowcraft~Amulet~2~~Coffin of the Unknown Soul~Countdown~Battlecry~Deathrattle"
    requireTarget, description = True, "Countdown (1)Fanfare: Burial Rite - Draw a card and add X to this amulet's Countdown. X equals half the original cost of the follower destroyed by Burial Rite (rounded down).Last Words: Summon a copy of the follower destroyed by Burial Rite."
    name_CN = "幽灵之棺"

    def __init__(self, Game, ID):
        super().__init__(Game, ID)
        self.counter = 1
        self.trigsBoard = [Trig_Countdown(self)]
        self.deathrattles = [Deathrattle_CoffinoftheUnknownSoul(self)]

    def effCanTrig(self):
        self.effectViable = not self.Game.Hand_Deck.noMinionsinHand(self.ID, self) and self.Game.space(self.ID) >= 2

    def targetExists(self, choice=0):
        return not self.Game.Hand_Deck.noMinionsinHand(self.ID, self) and self.Game.space(self.ID) >= 2

    def targetCorrect(self, target, choice=0):
        if isinstance(target, list): target = target[0]
        return target.ID == self.ID and target.inHand and target != self and target.type == "Minion"

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if target:
            if isinstance(target, list): target = target[0]
            t = type(target)
            self.Game.Hand_Deck.burialRite(self.ID, target)
            for trigger in self.deathrattles:
                if type(trigger) == Deathrattle_CoffinoftheUnknownSoul:
                    trigger.chosenMinionType = t
            self.countdown(self, -int(t.mana / 2))
        return target


class Deathrattle_CoffinoftheUnknownSoul(Deathrattle_Minion):
    def __init__(self, entity):
        super().__init__(entity)
        self.chosenMinionType = None

    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
        return target == self.entity and self.chosenMinionType

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        self.entity.Game.summon([self.chosenMinionType(self.entity.Game, self.entity.ID)], (-1, "totheRightEnd"),
                                self.entity)

    def selfCopy(self, newMinion):
        trigger = type(self)(newMinion)
        trigger.chosenMinionType = self.chosenMinionType
        return trigger


class SpiritCurator(SVMinion):
    Class, race, name = "Shadowcraft", "", "Spirit Curator"
    mana, attack, health = 3, 3, 3
    index = "SV_Fortune~Shadowcraft~Minion~3~3~3~~Spirit Curator~Battlecry"
    requireTarget, keyWord, description = True, "", "Fanfare: Burial Rite - Draw a card."
    attackAdd, healthAdd = 2, 2
    name_CN = "灵魂鉴定师"

    def effCanTrig(self):
        self.effectViable = not self.Game.Hand_Deck.noMinionsinHand(self.ID, self) and self.Game.space(self.ID) >= 2

    def targetExists(self, choice=0):
        return not self.Game.Hand_Deck.noMinionsinHand(self.ID, self) and self.Game.space(self.ID) >= 2

    def targetCorrect(self, target, choice=0):
        if isinstance(target, list): target = target[0]
        return target.ID == self.ID and target.inHand and target != self and target.type == "Minion"

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if target:
            if isinstance(target, list): target = target[0]
            self.Game.Hand_Deck.burialRite(self.ID, target)
            self.Game.Hand_Deck.drawCard(self.ID)
        return target


class DeathFowl_Crystallize(Amulet):
    Class, race, name = "Shadowcraft", "", "Crystallize: Death Fowl"
    mana = 1
    index = "SV_Fortune~Shadowcraft~Amulet~1~~Death Fowl~Countdown~Crystallize~Deathrattle~Uncollectible"
    requireTarget, description = False, "Countdown (3) Last Words: Gain 4 shadows."
    name_CN = "结晶：死之魔鸟"

    def __init__(self, Game, ID):
        super().__init__(Game, ID)
        self.counter = 3
        self.trigsBoard = [Trig_Countdown(self)]
        self.deathrattles = [Deathrattle_DeathFowl_Crystallize(self)]


class Deathrattle_DeathFowl_Crystallize(Deathrattle_Minion):
    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        self.entity.Game.Counters.shadows[self.entity.ID] += 4


class DeathFowl(SVMinion):
    Class, race, name = "Shadowcraft", "", "Death Fowl"
    mana, attack, health = 4, 3, 3
    index = "SV_Fortune~Shadowcraft~Minion~4~3~3~~Death Fowl~Crystallize~Deathrattle"
    requireTarget, keyWord, description = False, "", "Crystallize (1): Countdown (3) Last Words: Gain 4 shadows. Fanfare: Gain 4 shadows.Last Words: Draw a card."
    crystallizeAmulet = DeathFowl_Crystallize
    attackAdd, healthAdd = 2, 2
    name_CN = "死之魔鸟"

    def __init__(self, Game, ID):
        super().__init__(Game, ID)
        self.deathrattles = [Deathrattle_DeathFowl(self)]

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

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        self.Game.Counters.shadows[self.ID] += 4


class Deathrattle_DeathFowl(Deathrattle_Minion):
    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        self.entity.Game.Hand_Deck.drawCard(self.entity.ID)


class SoulBox(SVMinion):
    Class, race, name = "Shadowcraft", "", "Soul Box"
    mana, attack, health = 5, 5, 4
    index = "SV_Fortune~Shadowcraft~Minion~2~2~2~~Soul Box~Battlecry"
    requireTarget, keyWord, description = False, "", "Fanfare: If there are any allied amulets in play, evolve this follower."
    attackAdd, healthAdd = 2, 2
    name_CN = "灵魂之箱"

    def effCanTrig(self):
        self.effectViable = len(self.Game.amuletsonBoard(self.ID)) > 0

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if len(self.Game.amuletsonBoard(self.ID)) > 0:
            self.evolve()
        return None


class VIMilteoTheLovers(SVMinion):
    Class, race, name = "Shadowcraft", "", "VI. Milteo, The Lovers"
    mana, attack, health = 5, 4, 4
    index = "SV_Fortune~Shadowcraft~Minion~5~4~4~~VI. Milteo, The Lovers~Battlecry~Enhance~Deathrattle~Legendary"
    requireTarget, keyWord, description = True, "", "Fanfare: Burial Rite (2) - Reanimate (X) and Reanimate (Y). X and Y equal 6 split randomly.(To perform Burial Rite (2), there must be at least 2 open spaces in your area after this follower comes into play.)Enhance (9): Do not perform Burial Rite. Evolve this follower instead.Can't be evolved using evolution points. (Can be evolved using card effects.)Last Words: Draw 2 cards."
    attackAdd, healthAdd = 2, 2
    name_CN = "《恋人》·米路缇欧"

    def __init__(self, Game, ID):
        super().__init__(Game, ID)
        self.deathrattles = [Deathrattle_VIMilteoTheLovers(self)]
        self.marks["Can't Evolve"] = 1

    def getMana(self):
        if self.Game.Manas.manas[self.ID] >= 9:
            return 9
        else:
            return self.mana

    def willEnhance(self):
        return self.Game.Manas.manas[self.ID] >= 9

    def effCanTrig(self):
        if self.willEnhance():
            self.effectViable = True
        else:
            minions = 0
            for card in self.Game.Hand_Deck.hands[self.ID]:
                if card.type == "Minion" and card is not self:
                    minions += 1
            self.effectViable = minions >= 2 and self.Game.space(self.ID) >= 3

    def returnTrue(self, choice=0):
        if self.willEnhance():
            return False
        return self.targetExists(choice) and len(self.targets) < 2

    def targetExists(self, choice=0):
        minions = 0
        for card in self.Game.Hand_Deck.hands[self.ID]:
            if card.type == "Minion" and card is not self:
                minions += 1
        return minions >= 2 and self.Game.space(self.ID) >= 3

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
                self.Game.Counters.numBurialRiteThisGame[self.ID] += 1
                self.Game.sendSignal("BurialRite", self.ID, None, target[0], 0, "")
                self.Game.Counters.numBurialRiteThisGame[self.ID] += 1
                self.Game.sendSignal("BurialRite", self.ID, None, target[1], 0, "")
        return target


class Deathrattle_VIMilteoTheLovers(Deathrattle_Minion):
    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        self.entity.Game.Hand_Deck.drawCard(self.entity.ID)
        self.entity.Game.Hand_Deck.drawCard(self.entity.ID)


class Trig_VIMilteoTheLovers(TrigBoard):
    def __init__(self, entity):
        super().__init__(entity, ["TurnEnds"])

    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
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
                        curGame.fixedGuides.append((minion.pos, "Minion%d" % minion.ID))
                        curGame.killMinion(self.entity, minion)
                    else:
                        curGame.fixedGuides.append((0, ""))
        if self.entity.Game.heroes[3 - self.entity.ID].health > 6:
            damage = self.entity.Game.heroes[3 - self.entity.ID].health - 6
            self.entity.dealsDamage(self.entity.Game.heroes[3 - self.entity.ID], damage)


class CloisteredSacristan_Crystallize(Amulet):
    Class, race, name = "Shadowcraft", "", "Crystallize: Cloistered Sacristan"
    mana = 2
    index = "SV_Fortune~Shadowcraft~Amulet~2~~Cloistered Sacristan~Countdown~Crystallize~Deathrattle~Uncollectible"
    requireTarget, description = False, "Countdown (4) Whenever you perform Burial Rite, subtract 1 from this amulet's Countdown. Last Words: Summon a Cloistered Sacristan."
    name_CN = "结晶：幽暗守墓者"

    def __init__(self, Game, ID):
        super().__init__(Game, ID)
        self.counter = 4
        self.trigsBoard = [Trig_Countdown(self), Trig_CloisteredSacristan_Crystallize(self)]
        self.deathrattles = [Deathrattle_CloisteredSacristan_Crystallize(self)]


class Deathrattle_CloisteredSacristan_Crystallize(Deathrattle_Minion):
    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        self.entity.Game.summon([CloisteredSacristan(self.entity.Game, self.entity.ID)], (-1, "totheRightEnd"),
                                self.entity)


class Trig_CloisteredSacristan_Crystallize(TrigBoard):
    def __init__(self, entity):
        super().__init__(entity, ["BurialRite"])

    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.onBoard and ID == self.entity.ID

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        self.entity.countdown(self.entity, 1)


class CloisteredSacristan(SVMinion):
    Class, race, name = "Shadowcraft", "", "Cloistered Sacristan"
    mana, attack, health = 6, 5, 5
    index = "SV_Fortune~Shadowcraft~Minion~6~5~5~~Cloistered Sacristan~Taunt~Crystallize"
    requireTarget, keyWord, description = False, "Taunt", "Crystallize (2): Countdown (4)Whenever you perform Burial Rite, subtract 1 from this amulet's Countdown.Last Words: Summon a Cloistered Sacristan.Ward."
    crystallizeAmulet = DeathFowl_Crystallize
    attackAdd, healthAdd = 2, 2
    evolveRequireTarget = True
    name_CN = "幽暗守墓者"

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

    def effCanTrig(self):
        if self.willCrystallize() and self.targetExists():
            self.effectViable = "sky blue"
        else:
            self.effectViable = False

    def inHandEvolving(self, target=None):
        if target:
            if isinstance(target, list): target = target[0]
            self.Game.Hand_Deck.burialRite(self.ID, target)
            self.restoresHealth(self.Game.heroes[self.ID], 3)
        return target


class ConqueringDreadlord(SVMinion):
    Class, race, name = "Shadowcraft", "", "Conquering Dreadlord"
    mana, attack, health = 8, 6, 6
    index = "SV_Fortune~Shadowcraft~Minion~8~6~6~~Conquering Dreadlord~Invocation~Legendary"
    requireTarget, keyWord, description = False, "", "Invocation: When you perform Burial Rite, if it is your fifth, seventh, or ninth time this match, invoke this card, then return it to your hand.When this follower leaves play, or at the end of your turn, summon a Lich. (Transformation doesn't count as leaving play.)"
    attackAdd, healthAdd = 2, 2
    name_CN = "征伐的死帝"

    def __init__(self, Game, ID):
        super().__init__(Game, ID)
        self.trigsBoard = [Trig_ConqueringDreadlord(self)]
        self.trigsDeck = [Trig_InvocationConqueringDreadlord(self)]
        self.disappearResponse = [self.whenDisppears]

    def whenDisppears(self):
        self.Game.summon([Lich(self.Game, self.ID)], (-1, "totheRightEnd"), self)

    def afterInvocation(self, signal, ID, subject, target, number, comment):
        self.Game.returnMiniontoHand(self, deathrattlesStayArmed=False)


class Trig_ConqueringDreadlord(TrigBoard):
    def __init__(self, entity):
        super().__init__(entity, ["TurnEnds"])

    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.onBoard and ID == self.entity.ID

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        self.entity.Game.summon([Lich(self.entity.Game, self.entity.ID)], (-1, "totheRightEnd"),
                                self.entity)


class Trig_InvocationConqueringDreadlord(TrigInvocation):
    def __init__(self, entity):
        super().__init__(entity, ["BurialRite"])

    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.inDeck and ID == self.entity.ID and self.entity.Game.space(self.entity.ID) > 0 and \
               self.entity.Game.Counters.numBurialRiteThisGame[self.entity.ID] in [5, 7, 9]


class Deathbringer_Crystallize(Amulet):
    Class, race, name = "Shadowcraft", "", "Crystallize: Deathbringer"
    mana = 2
    index = "SV_Fortune~Shadowcraft~Amulet~2~~Deathbringer~Countdown~Crystallize~Battlecry~Deathrattle~Uncollectible"
    requireTarget, description = False, "Countdown (3) Fanfare and Last Words: Transform a random enemy follower into a Skeleton."
    name_CN = "结晶：死灭召来者"

    def __init__(self, Game, ID):
        super().__init__(Game, ID)
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
                    curGame.fixedGuides.append((enemy.pos, enemy.type + str(enemy.ID)))
                else:
                    curGame.fixedGuides.append((0, ''))
            if enemy:
                self.Game.transform(enemy, Skeleton(self.Game, 3 - self.ID))


class Deathrattle_Deathbringer_Crystallize(Deathrattle_Minion):
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
                    curGame.fixedGuides.append((enemy.pos, enemy.type + str(enemy.ID)))
                else:
                    curGame.fixedGuides.append((0, ''))
            if enemy:
                self.entity.Game.transform(enemy, Skeleton(self.entity.Game, 3 - self.entity.ID))


class Deathbringer(SVMinion):
    Class, race, name = "Shadowcraft", "", "Deathbringer"
    mana, attack, health = 9, 7, 7
    index = "SV_Fortune~Shadowcraft~Minion~9~7~7~~Deathbringer~Crystallize"
    requireTarget, keyWord, description = False, "", "Crystallize (2): Countdown (3) Fanfare and Last Words: Transform a random enemy follower into a Skeleton.At the end of your turn, destroy 2 random enemy followers and restore 5 defense to your leader."
    crystallizeAmulet = Deathbringer_Crystallize
    attackAdd, healthAdd = 2, 2
    name_CN = "死灭召来者"

    def __init__(self, Game, ID):
        super().__init__(Game, ID)
        self.trigsBoard = [Trig_Deathbringer(self)]

    def getMana(self):
        if self.Game.Manas.manas[self.ID] < self.mana:
            return 2
        else:
            return self.mana

    def willCrystallize(self):
        curMana = self.Game.Manas.manas[self.ID]
        return self.mana > curMana >= 2

    def effCanTrig(self):
        if self.willCrystallize() and self.targetExists():
            self.effectViable = "sky blue"
        else:
            self.effectViable = False


class Trig_Deathbringer(TrigBoard):
    def __init__(self, entity):
        super().__init__(entity, ["TurnEnds"])

    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
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
                        curGame.fixedGuides.append((enemy.pos, enemy.type + str(enemy.ID)))
                    else:
                        curGame.fixedGuides.append((0, ''))
                if enemy:
                    self.entity.Game.killMinion(self.entity, enemy)
        self.entity.restoresHealth(self.entity.Game.heroes[self.entity.ID], 5)


"""Bloodcraft cards"""


class SilverboltHunter(SVMinion):
    Class, race, name = "Bloodcraft", "", "Silverbolt Hunter"
    mana, attack, health = 1, 1, 2
    index = "SV_Fortune~Bloodcraft~Minion~1~1~2~~Silverbolt Hunter~Battlecry~Deathrattle"
    requireTarget, keyWord, description = False, "", "Fanfare: Deal 1 damage to your leader. Last Words: Give +1/+1 to a random allied follower."
    attackAdd, healthAdd = 2, 2
    name_CN = "银箭狩猎者"

    def __init__(self, Game, ID):
        super().__init__(Game, ID)
        self.deathrattles = [Deathrattle_SilverboltHunter(self)]

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        self.dealsDamage(self.Game.heroes[self.ID], 1)


class Deathrattle_SilverboltHunter(Deathrattle_Minion):
    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        curGame = self.entity.Game
        if curGame.mode == 0:
            if curGame.guides:
                i = curGame.guides.pop(0)
            else:
                minions = [minion.pos for minion in curGame.minionsAlive(self.entity.ID)]
                i = npchoice(minions) if minions else -1
                curGame.fixedGuides.append(i)
            if i > -1:
                minion = curGame.minions[self.entity.ID][i]
                minion.buffDebuff(1, 1)


class MoonriseWerewolf(SVMinion):
    Class, race, name = "Bloodcraft", "", "Moonrise Werewolf"
    mana, attack, health = 2, 1, 3
    index = "SV_Fortune~Bloodcraft~Minion~2~1~3~~Moonrise Werewolf~Battlecry~Enhance"
    requireTarget, keyWord, description = False, "", "Fanfare: If Avarice is active for you, gain +0/+2 and Ward.Fanfare: Enhance (5) - Gain +3/+3."
    attackAdd, healthAdd = 2, 2
    name_CN = "月下的狼人"

    def getMana(self):
        if self.Game.Manas.manas[self.ID] >= 5:
            return 5
        else:
            return self.mana

    def willEnhance(self):
        return self.Game.Manas.manas[self.ID] >= 5

    def effCanTrig(self):
        self.effectViable = self.willEnhance() or self.Game.isAvarice(self.ID)

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if self.Game.isAvarice(self.ID):
            self.buffDebuff(0, 2)
            self.getsStatus("Taunt")
        if comment == 5:
            self.buffDebuff(3, 3)
        return target


class WhiplashImp(SVMinion):
    Class, race, name = "Bloodcraft", "", "Whiplash Imp"
    mana, attack, health = 2, 2, 2
    index = "SV_Fortune~Bloodcraft~Minion~2~2~2~~Whiplash Imp~Battlecry~Enhance"
    requireTarget, keyWord, description = False, "", "Fanfare: If Wrath is active for you, gain +1/+4, Rush, and Drain. Fanfare: Enhance (6) - Summon an Imp Lancer."
    attackAdd, healthAdd = 2, 2
    name_CN = "迅鞭小恶魔"

    def getMana(self):
        if self.Game.Manas.manas[self.ID] >= 6:
            return 6
        else:
            return self.mana

    def willEnhance(self):
        return self.Game.Manas.manas[self.ID] >= 6

    def effCanTrig(self):
        self.effectViable = self.willEnhance() or self.Game.isWrath(self.ID)

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if self.Game.isWrath(self.ID):
            self.buffDebuff(1, 4)
            self.getsStatus("Rush")
            self.getsStatus("Drain")
        if comment == 6:
            self.Game.summon([ImpLancer(self.Game, self.ID)], (-1, "totheRightEnd"),
                             self)
        return target


class ContemptousDemon(SVMinion):
    Class, race, name = "Bloodcraft", "", "Contemptous Demon"
    mana, attack, health = 2, 2, 2
    index = "SV_Fortune~Bloodcraft~Minion~2~2~2~~Contemptous Demon~Battlecry"
    requireTarget, keyWord, description = False, "", "Fanfare: If Wrath is active for you, gain the ability to evolve for 0 evolution points.At the end of your turn, deal 1 damage to your leader.At the start of your turn, restore 2 defense to your leader."
    attackAdd, healthAdd = 2, 2
    name_CN = "讥讽的恶魔"

    def __init__(self, Game, ID):
        super().__init__(Game, ID)
        self.trigsBoard = [Trig_StartContemptousDemon(self), Trig_EndContemptousDemon(self)]

    def effCanTrig(self):
        self.effectViable = self.Game.isWrath(self.ID)

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if self.Game.isWrath(self.ID):
            self.marks["Free Evolve"] += 1
        return target

    def inEvolving(self):
        trigger = Trig_EvolvedContemptousDemon(self)
        self.trigsBoard.append(trigger)
        trigger.connect()


class Trig_StartContemptousDemon(TrigBoard):
    def __init__(self, entity):
        super().__init__(entity, ["TurnStarts"])

    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.onBoard and ID == self.entity.ID

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        heal = 2 * (2 ** self.entity.countHealDouble())
        self.entity.restoresHealth(self.entity.Game.heroes[self.entity.ID], heal)


class Trig_EndContemptousDemon(TrigBoard):
    def __init__(self, entity):
        super().__init__(entity, ["TurnEnds"])

    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.onBoard and ID == self.entity.ID

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        self.entity.dealsDamage(self.entity.Game.heroes[self.entity.ID], 1)


class Trig_EvolvedContemptousDemon(TrigBoard):
    def __init__(self, entity):
        super().__init__(entity, ["HeroTookDmg", "HeroTook0Dmg", "TurnEnds"])
        self.counter = 10

    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
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
                        curGame.fixedGuides.append((enemy.pos, enemy.type + str(enemy.ID)))
                    else:
                        curGame.fixedGuides.append((0, ''))
                if enemy:
                    self.entity.dealsDamage(enemy, 3)
            self.counter -= 1
        else:
            self.counter = 10


class DarkSummons(SVSpell):
    Class, school, name = "Bloodcraft", "", "Dark Summons"
    requireTarget, mana = True, 2
    index = "SV_Fortune~Bloodcraft~Spell~2~~Dark Summons"
    description = "Deal 3 damage to an enemy follower. If Wrath is active for you, recover 2 play points."
    name_CN = "暗黑融合"

    def available(self):
        return self.selectableEnemyMinionExists()

    def targetCorrect(self, target, choice=0):
        if isinstance(target, list): target = target[0]
        return target.type == "Minion" and target.ID != self.ID and target.onBoard

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if target:
            if isinstance(target, list): target = target[0]
            damage = (3 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
            self.dealsDamage(target, damage)
            if self.Game.isWrath(self.ID):
                self.Game.Manas.restoreManaCrystal(2, self.ID)
        return target


class TyrantofMayhem(SVMinion):
    Class, race, name = "Bloodcraft", "", "Tyrant of Mayhem"
    mana, attack, health = 3, 3, 3
    index = "SV_Fortune~Bloodcraft~Minion~3~3~3~~Tyrant of Mayhem~Battlecry"
    requireTarget, keyWord, description = False, "", "Fanfare: Draw a card. If Vengeance is not active for you, deal 2 damage to your leader. Otherwise, deal 2 damage to the enemy leader."
    attackAdd, healthAdd = 2, 2
    name_CN = "暴虐的恶魔"

    def effCanTrig(self):
        self.effectViable = self.Game.isVengeance(self.ID)

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        self.Game.Hand_Deck.drawCard(self.ID)
        if self.Game.isVengeance(self.ID):
            self.dealsDamage(self.Game.heroes[3 - self.ID], 2)
        else:
            self.dealsDamage(self.Game.heroes[self.ID], 2)
        return target


class CurmudgeonOgre(SVMinion):
    Class, race, name = "Bloodcraft", "", "Curmudgeon Ogre"
    mana, attack, health = 4, 4, 4
    index = "SV_Fortune~Bloodcraft~Minion~4~4~4~~Curmudgeon Ogre~Battlecry~Enhance"
    requireTarget, keyWord, description = False, "", "Fanfare: Enhance (6) - Give +1/+1 to all allied Bloodcraft followers. If Vengeance is active for you, give +2/+2 instead."
    attackAdd, healthAdd = 2, 2
    name_CN = "蛮吼的巨魔"

    def getMana(self):
        if self.Game.Manas.manas[self.ID] >= 6:
            return 6
        else:
            return self.mana

    def willEnhance(self):
        return self.Game.Manas.manas[self.ID] >= 6

    def effCanTrig(self):
        self.effectViable = self.willEnhance()

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if comment == 6:
            n = 1
            if self.Game.isVengeance(self.ID):
                n = 2
            for minion in self.Game.minionsonBoard(self.ID, self):
                if minion.Class == "Bloodcraft":
                    minion.buffDebuff(n, n)
        return target


class DireBond(Amulet):
    Class, race, name = "Bloodcraft", "", "Dire Bond"
    mana = 3
    index = "SV_Fortune~Bloodcraft~Amulet~3~~Dire Bond"
    requireTarget, description = False, "Countdown (3)Fanfare: Deal 6 damage to your leader.At the start of your turn, restore 2 defense to your leader and draw a card."
    name_CN = "漆黑之契"

    def __init__(self, Game, ID):
        super().__init__(Game, ID)
        self.counter = 3
        self.trigsBoard = [Trig_Countdown(self), Trig_DireBond(self)]

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        self.dealsDamage(self.Game.heroes[self.ID], 6)


class Trig_DireBond(TrigBoard):
    def __init__(self, entity):
        super().__init__(entity, ["TurnStarts"])

    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.onBoard and ID == self.entity.ID

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        self.entity.Game.Hand_Deck.drawCard(self.entity.ID)
        self.entity.restoresHealth(self.entity.Game.heroes[self.entity.ID], 2)


class DarholdAbyssalContract(SVMinion):
    Class, race, name = "Bloodcraft", "", "Darhold, Abyssal Contract"
    mana, attack, health = 4, 4, 3
    index = "SV_Fortune~Bloodcraft~Minion~4~4~3~~Darhold, Abyssal Contract~Battlecry~Legendary"
    requireTarget, keyWord, description = True, "", "Fanfare: If Wrath is active for you, destroy an enemy follower, then deal 3 damage to the enemy leader."
    attackAdd, healthAdd = 2, 2
    name_CN = "深渊之契·达尔霍德"

    def effCanTrig(self):
        self.effectViable = self.Game.isWrath(self.ID)

    def targetExists(self, choice=0):
        return self.selectableEnemyMinionExists() and self.Game.isWrath(self.ID)

    def targetCorrect(self, target, choice=0):
        if isinstance(target, list): target = target[0]
        return target.type == "Minion" and target.ID != self.ID and target.onBoard

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if target:
            if isinstance(target, list): target = target[0]
            self.Game.killMinion(self, target)
            self.dealsDamage(self.Game.heroes[3 - self.ID], 3)
        return target

    def inHandEvolving(self, target=None):
        self.dealsDamage(self.Game.heroes[self.ID], 3)
        self.Game.summon([DireBond(self.Game, self.ID)], (-1, "totheRightEnd"),
                         self)


class BurningConstriction(SVSpell):
    Class, school, name = "Bloodcraft", "", "Burning Constriction"
    mana, requireTarget = 5, False
    index = "SV_Fortune~Bloodcraft~Spell~5~~Burning Constriction"
    description = "Deal 4 damage to all enemy followers. Then, if Vengeance is active for you, deal 4 damage to the enemy leader."
    name_CN = "盛燃的抵抗"

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        damage = (4 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
        targets = self.Game.minionsonBoard(3 - self.ID)
        self.dealsAOE(targets, [damage for minion in targets])
        if self.Game.isVengeance(self.ID):
            self.dealsDamage(self.Game.heroes[3 - self.ID], damage)
        return None


class VampireofCalamity_Accelerate(SVSpell):
    Class, school, name = "Bloodcraft", "", "Vampire of Calamity"
    requireTarget, mana = True, 1
    index = "SV_Fortune~Bloodcraft~Spell~1~~Vampire of Calamity~Accelerate~Uncollectible"
    description = "Deal 1 damage to your leader. Deal 2 damage to an enemy follower."
    name_CN = "灾祸暗夜眷属"

    def targetCorrect(self, target, choice=0):
        if isinstance(target, list): target = target[0]
        return target.type == "Minion" and target.ID != self.ID and target.onBoard

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if target:
            if isinstance(target, list): target = target[0]
            damage = (1 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
            self.dealsDamage(self.Game.heroes[self.ID], damage)
            damage1 = (2 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
            self.dealsDamage(target, damage1)
        return target


class VampireofCalamity(SVMinion):
    Class, race, name = "Bloodcraft", "", "Vampire of Calamity"
    mana, attack, health = 7, 7, 7
    index = "SV_Fortune~Bloodcraft~Minion~7~7~7~~Vampire of Calamity~Rush~Battlecry~Accelerate"
    requireTarget, keyWord, description = True, "Rush", "Accelerate (1): Deal 1 damage to your leader. Deal 2 damage to an enemy follower.Rush.Fanfare: If Wrath is active for you, deal 4 damage to an enemy and restore 4 defense to your leader."
    accelerateSpell = VampireofCalamity_Accelerate
    attackAdd, healthAdd = 2, 2
    name_CN = "灾祸暗夜眷属"

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
            self.dealsDamage(target, 4)
        self.restoresHealth(self.Game.heroes[self.ID], 4)
        return target


class UnselfishGrace(Amulet):
    Class, race, name = "Bloodcraft", "", "Unselfish Grace"
    mana = 3
    index = "SV_Fortune~Bloodcraft~Amulet~3~~Unselfish Grace~Uncollectible~Legendary"
    requireTarget, description = False, "Countdown (5)At the end of your turn, restore 1 defense to your leader. If you have more evolution points than your opponent, restore 2 defense instead. (You have 0 evolution points on turns you are unable to evolve.)Last Words: Summon a 4-play point 4/4 XIV. Luzen, Temperance (without Accelerate)."
    name_CN = "无欲之恩宠"

    def __init__(self, Game, ID):
        super().__init__(Game, ID)
        self.counter = 5
        self.trigsBoard = [Trig_Countdown(self), Trig_UnselfishGrace(self)]
        self.deathrattles = [Deathrattle_UnselfishGrace(self)]


class Trig_UnselfishGrace(TrigBoard):
    def __init__(self, entity):
        super().__init__(entity, ["TurnEnds"])

    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.onBoard and ID == self.entity.ID

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        health = 1
        if self.entity.Game.getEvolutionPoint(self.entity.ID) > self.entity.Game.getEvolutionPoint(3 - self.entity.ID):
            health = 2
        self.entity.restoresHealth(self.entity.Game.heroes[self.entity.ID], health)


class Deathrattle_UnselfishGrace(Deathrattle_Minion):
    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        self.entity.Game.summon([XIVLuzenTemperance_Token(self.entity.Game, self.entity.ID)], (-1, "totheRightEnd"),
                                self.entity)


class InsatiableDesire(SVSpell):
    Class, school, name = "Bloodcraft", "", "Insatiable Desire"
    requireTarget, mana = False, 1
    index = "SV_Fortune~Bloodcraft~Spell~1~~Insatiable Desire~Uncollectible~Legendary"
    description = "Give your leader the following effects.-At the start of your turn, draw a card.-At the start of your turn, lose 1 play point.(These effects are not stackable and last for the rest of the match.)"
    name_CN = "无尽之渴望"

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
        super().__init__(entity, ["TurnStarts"])

    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.onBoard and ID == self.entity.ID

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        self.entity.Game.Hand_Deck.drawCard(self.entity.ID)
        self.entity.Game.Manas.payManaCost(self.entity, 1)


class XIVLuzenTemperance_Accelerate(SVSpell):
    Class, school, name = "Bloodcraft", "", "XIV. Luzen, Temperance"
    requireTarget, mana = False, 0
    index = "SV_Fortune~Bloodcraft~Spell~0~~XIV. Luzen, Temperance~Accelerate~Uncollectible~Legendary"
    description = "Put an Unselfish Grace into your hand. If Avarice is active for you, put an Insatiable Desire into your hand instead."
    name_CN = "《节制》·卢泽"

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if self.Game.isAvarice(self.ID):
            self.Game.Hand_Deck.addCardtoHand(InsatiableDesire(self.Game, self.ID), self.ID)
        else:
            self.Game.Hand_Deck.addCardtoHand(UnselfishGrace(self.Game, self.ID), self.ID)
        return None


class XIVLuzenTemperance_Token(SVMinion):
    Class, race, name = "Bloodcraft", "", "XIV. Luzen, Temperance"
    mana, attack, health = 4, 4, 4
    index = "SV_Fortune~Bloodcraft~Minion~4~4~4~~XIV. Luzen, Temperance~Uncollectible~Legendary"
    requireTarget, keyWord, description = False, "", "Can't be targeted by enemy effects.While this follower is in play, your leader has the following effects.-Can't take more than 1 damage at a time.-Whenever your leader takes damage, reduce the enemy leader's maximum defense by 3."
    attackAdd, healthAdd = 2, 2
    name_CN = "《节制》·卢泽"

    def __init__(self, Game, ID):
        super().__init__(Game, ID)
        self.auras["Buff Aura"] = BuffAura_XIVLuzenTemperance(self)
        self.marks["Enemy Effect Evasive"] = 1


class XIVLuzenTemperance(SVMinion):
    Class, race, name = "Bloodcraft", "", "XIV. Luzen, Temperance"
    mana, attack, health = 9, 7, 7
    index = "SV_Fortune~Bloodcraft~Minion~9~7~7~~XIV. Luzen, Temperance~Accelerate~Legendary"
    requireTarget, keyWord, description = False, "", "Can't be targeted by enemy effects.While this follower is in play, your leader has the following effects.-Can't take more than 1 damage at a time.-Whenever your leader takes damage, reduce the enemy leader's maximum defense by 3."
    accelerateSpell = XIVLuzenTemperance_Accelerate
    attackAdd, healthAdd = 2, 2
    name_CN = "《节制》·卢泽"

    def __init__(self, Game, ID):
        super().__init__(Game, ID)
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

    def effCanTrig(self):
        if self.willAccelerate() and self.targetExists():
            self.effectViable = "sky blue"
        else:
            self.effectViable = False


class BuffAura_XIVLuzenTemperance(HasAura_toMinion):
    def __init__(self, entity):
        self.entity = entity
        self.signals, self.auraAffected = [], []

    # Minions appearing/disappearing will let the minion reevaluate the aura.
    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.onBoard

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        self.applies(self.entity.Game.heroes[self.entity.ID])

    def applies(self, subject):
        trigger = Trig_XIVLuzenTemperance(subject)
        subject.trigsBoard.append(trigger)
        trigger.connect()
        trigger = Trig_XIVLuzenTemperance_MaxDamage(subject)
        subject.trigsBoard.append(trigger)
        trigger.connect()

    def auraAppears(self):
        self.applies(self.entity.Game.heroes[self.entity.ID])

    def auraDisappears(self):
        for trigger in self.entity.Game.heroes[self.entity.ID].trigsBoard:
            if type(trigger) == Trig_XIVLuzenTemperance:
                self.entity.Game.heroes[self.entity.ID].trigsBoard.remove(trigger)
                break
        for trigger in self.entity.Game.heroes[self.entity.ID].trigsBoard:
            if type(trigger) == Trig_XIVLuzenTemperance_MaxDamage:
                self.entity.Game.heroes[self.entity.ID].trigsBoard.remove(trigger)
                break

    def selfCopy(self, recipientMinion):  # The recipientMinion is the minion that deals the Aura.
        return type(self)(recipientMinion)


class Trig_XIVLuzenTemperance(TrigBoard):
    def __init__(self, entity):
        super().__init__(entity, ["HeroTookDmg", "HeroTook0Dmg"])

    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.onBoard and target == self.entity.Game.heroes[self.entity.ID]

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        self.entity.Game.heroes[3 - self.entity.ID].health_max -= 3
        self.entity.Game.heroes[3 - self.entity.ID].health = min(self.entity.Game.heroes[3 - self.entity.ID].health,
                                                                 self.entity.Game.heroes[3 - self.entity.ID].health_max)


class Trig_XIVLuzenTemperance_MaxDamage(TrigBoard):
    def __init__(self, entity):
        super().__init__(entity, ["BattleDmgHero", "AbilityDmgHero"])

    def canTrig(self, signal, ID, subject, target, number, comment,
                choice=0):  # target here holds the actual target object
        return target == self.entity

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        number[0] = min(1, number[0])


"""Havencraft cards"""


class JeweledBrilliance(SVSpell):
    Class, school, name = "Havencraft", "", "Jeweled Brilliance"
    mana, requireTarget = 1, False,
    index = "SV_Fortune~Havencraft~Spell~1~~Jeweled Brilliance"
    description = "Put a random amulet from your deck into your hand."
    name_CN = "宝石的光辉"

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        curGame = self.Game
        if curGame.mode == 0:
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
    index = "SV_Fortune~Havencraft~Minion~2~2~2~~Stalwart Featherfolk~Taunt~Battlecry"
    requireTarget, keyWord, description = False, "Taunt", "Ward. Fanfare: If any allied amulets are in play, restore X defense to your leader. X equals the number of allied amulets in play."
    attackAdd, healthAdd = 2, 2
    name_CN = "刚健的翼人"

    def effCanTrig(self):
        self.effectViable = len(self.Game.amuletsonBoard(self.ID)) > 0

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if len(self.Game.amuletsonBoard(self.ID)) > 0:
            self.restoresHealth(self.Game.heroes[self.ID], len(self.Game.amuletsonBoard(self.ID)))

        return None


class PrismaplumeBird(SVMinion):
    Class, race, name = "Havencraft", "", "Prismaplume Bird"
    mana, attack, health = 2, 3, 1
    index = "SV_Fortune~Havencraft~Minion~2~3~1~~Prismaplume Bird~Deathrattle"
    requireTarget, keyWord, description = False, "", "Last Words: Randomly summon a Summon Pegasus or Pinion Prayer."
    attackAdd, healthAdd = 2, 2
    name_CN = "优雅的丽鸟"

    def __init__(self, Game, ID):
        super().__init__(Game, ID)
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
            self.entity.Game.summon([SummonPegasus(self.entity.Game, self.entity.ID)], (-1, "totheRightEnd"),
                                    self.entity)
        elif e == "P":
            self.entity.Game.summon([PinionPrayer(self.entity.Game, self.entity.ID)], (-1, "totheRightEnd"),
                                    self.entity)


class FourPillarTortoise(SVMinion):
    Class, race, name = "Havencraft", "", "Four-Pillar Tortoise"
    mana, attack, health = 3, 1, 4
    index = "SV_Fortune~Havencraft~Minion~3~1~4~~Four-Pillar Tortoise~Taunt~Battlecry"
    requireTarget, keyWord, description = False, "Taunt", "Ward. Fanfare: Randomly put a 4-play point Havencraft follower or amulet from your deck into your hand."
    attackAdd, healthAdd = 2, 2
    name_CN = "圣柱巨龟"

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        curGame = self.Game
        if curGame.mode == 0:
            if curGame.guides:
                i = curGame.guides.pop(0)
            else:
                minions = [i for i, card in enumerate(curGame.Hand_Deck.decks[self.ID]) if
                           card.type == "Minion" and card.mana == 4]
                i = npchoice(minions) if minions else -1
                curGame.fixedGuides.append(i)
            if i > -1: curGame.Hand_Deck.drawCard(self.ID, i)


class LorenasHolyWater(SVSpell):
    Class, school, name = "Havencraft", "", "Lorena's Holy Water"
    requireTarget, mana = True, 1
    index = "SV_Fortune~Havencraft~Spell~1~~Lorena's Holy Water~Uncollectible"
    description = "Restore 2 defense to an ally.Draw a card."
    name_CN = "萝蕾娜的圣水"

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
            self.Game.Hand_Deck.drawCard(self.ID)
        return target


class LorenaIronWilledPriest(SVMinion):
    Class, race, name = "Havencraft", "", "Lorena, Iron-Willed Priest"
    mana, attack, health = 3, 2, 3
    index = "SV_Fortune~Havencraft~Minion~3~2~3~~Lorena, Iron-Willed Priest~Battlecry"
    requireTarget, keyWord, description = False, "", "Fanfare: Put a Lorena's Holy Water into your hand. During your turn, when defense is restored to your leader, if it's the second time this turn, gain the ability to evolve for 0 evolution points."
    attackAdd, healthAdd = 2, 2
    evolveRequireTarget = True
    name_CN = "传教司祭·萝蕾娜"

    def __init__(self, Game, ID):
        super().__init__(Game, ID)
        self.progress = 0
        self.trigsBoard = [Trig_LorenaIronWilledPriest(self), Trig_EndLorenaIronWilledPriest]

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        self.Game.Hand_Deck.addCardtoHand(LorenasHolyWater, self.ID, byType=True)

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
            self.dealsDamage(target, damage)
        return target


class Trig_LorenaIronWilledPriest(TrigBoard):
    def __init__(self, entity):
        super().__init__(entity, ["HeroGetsCured", "AllCured"])

    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
        if signal == "HeroGetsCured":
            return subject.ID == self.entity.ID and self.entity.onBoard
        else:
            return ID == self.entity.ID and self.entity.onBoard

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        self.entity.progress += 1
        if self.entity.progress == 2:
            self.entity.marks["Free Evolve"] += 1


class Trig_EndLorenaIronWilledPriest(TrigBoard):
    def __init__(self, entity):
        super().__init__(entity, ["TurnEnds"])

    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.onBoard and ID == self.entity.ID

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        self.entity.progress = 0


class SarissaLuxflashSpear(SVMinion):
    Class, race, name = "Havencraft", "", "Sarissa, Luxflash Spear"
    mana, attack, health = 3, 2, 2
    index = "SV_Fortune~Havencraft~Minion~3~2~2~~Sarissa, Luxflash Spear~Battlecry~Enhance~Legendary"
    requireTarget, keyWord, description = False, "", "Fanfare: The next time this follower takes damage, reduce that damage to 0.Enhance (6): Randomly summon a copy of 1 of the highest-cost allied followers that had Ward when they were destroyed this match.Whenever an allied follower with Ward is destroyed, gain +2/+2."
    attackAdd, healthAdd = 2, 2
    name_CN = "破暗煌辉·萨莉莎"

    def __init__(self, Game, ID):
        super().__init__(Game, ID)
        self.trigsBoard = [Trig_SarissaLuxflashSpear(self)]

    def getMana(self):
        if self.Game.Manas.manas[self.ID] >= 6:
            return 6
        else:
            return self.mana

    def willEnhance(self):
        return self.Game.Manas.manas[self.ID] >= 6

    def effCanTrig(self):
        self.effectViable = self.willEnhance()

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        self.marks["Next Damage 0"] = 1
        if comment == 6:
            if self.Game.mode == 0:
                t = None
                if self.Game.guides:
                    t = self.Game.cardPool[self.Game.guides.pop(0)]
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
                        for i in range(list(minions.keys())[len(minions) - 1], -1, -1):
                            if i in minions:
                                t = npchoice(minions[i])
                                self.Game.fixedGuides.append(t.index)
                                break
                    else:
                        self.Game.fixedGuides.append(None)
                if t:
                    subject = t(self.Game, self.ID)
                    self.Game.summon([subject], (-1, "totheRightEnd"), self)
        return None


class Trig_SarissaLuxflashSpear(TrigBoard):
    def __init__(self, entity):
        super().__init__(entity, ["MinionDies"])

    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
        return target.ID == self.entity.ID and self.entity.onBoard and target.keyWords["Taunt"] > 0

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        self.entity.buffDebuff(2, 2)


class PriestessofForesight(SVMinion):
    Class, race, name = "Havencraft", "", "Priestess of Foresight"
    mana, attack, health = 4, 2, 5
    index = "SV_Fortune~Havencraft~Minion~4~2~5~~Priestess of Foresight~Battlecry"
    requireTarget, keyWord, description = False, "", "Fanfare: If another allied follower with Ward is in play, destroy an enemy follower. Otherwise, gain Ward."
    attackAdd, healthAdd = 2, 2
    name_CN = "先见的神官"

    def returnTrue(self, choice=0):
        for minion in self.Game.minionsAlive(self.ID):
            if minion != self and minion.keyWords["Taunt"] > 0:
                return self.targetExists(choice) and not self.targets
        return False

    def effCanTrig(self):
        self.effectViable = True

    def targetExists(self, choice=0):
        return self.selectableEnemyMinionExists()

    def targetCorrect(self, target, choice=0):
        if isinstance(target, list): target = target[0]
        return target.type == "Minion" and target.ID != self.ID and target.onBoard

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if target:
            if isinstance(target, list): target = target[0]
            self.Game.killMinion(self, target)
            return target
        hasTaunt = False
        for minion in self.Game.minionsAlive(self.ID):
            if minion != self and minion.keyWords["Taunt"] > 0:
                hasTaunt = True
                break
        if not hasTaunt:
            self.getsStatus("Taunt")
        return None


class HolybrightAltar(Amulet):
    Class, race, name = "Havencraft", "", "Holybright Altar"
    mana = 4
    index = "SV_Fortune~Havencraft~Amulet~4~~Holybright Altar~Battlecry~Countdown~Deathrattle"
    requireTarget, description = False, "Countdown (1) Fanfare: If an allied follower with Ward is in play, subtract 1 from this amulet's Countdown.Last Words: Summon a Holywing Dragon."
    name_CN = "咏唱：纯白祭坛"

    def __init__(self, Game, ID):
        super().__init__(Game, ID)
        self.counter = 1
        self.trigsBoard = [Trig_Countdown(self)]
        self.deathrattles = [Deathrattle_HolybrightAltar(self)]

    def effCanTrig(self):
        for minion in self.Game.minionsAlive(self.ID):
            if minion != self and minion.keyWords["Taunt"] > 0:
                self.effectViable = True
                return

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
        self.entity.Game.summon([HolywingDragon(self.entity.Game, self.entity.ID)], (-1, "totheRightEnd"),
                                self.entity)


class ReverendAdjudicator(SVMinion):
    Class, race, name = "Havencraft", "", "Reverend Adjudicator"
    mana, attack, health = 5, 2, 3
    index = "SV_Fortune~Havencraft~Minion~5~2~3~~Reverend Adjudicator~Taunt~Battlecry"
    requireTarget, keyWord, description = False, "Taunt", "Ward.Fanfare: Restore 2 defense to your leader. Draw a card.During your turn, whenever your leader's defense is restored, summon a Snake Priestess."
    attackAdd, healthAdd = 2, 2
    name_CN = "神域的法王"

    def __init__(self, Game, ID):
        super().__init__(Game, ID)
        self.trigsBoard = [Trig_ReverendAdjudicator(self)]

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        self.restoresHealth(self.Game.heroes[self.ID], 2)
        self.Game.Hand_Deck.drawCard(self.ID)

    def inHandEvolving(self, target=None):
        self.restoresHealth(self.Game.heroes[self.ID], 2)


class Trig_ReverendAdjudicator(TrigBoard):
    def __init__(self, entity):
        super().__init__(entity, ["HeroGetsCured", "AllCured"])

    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
        if signal == "HeroGetsCured":
            return subject.ID == self.entity.ID and self.entity.onBoard
        else:
            return ID == self.entity.ID and self.entity.onBoard

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        self.entity.Game.summon([SnakePriestess(self.entity.Game, self.entity.ID)], (-1, "totheRightEnd"),
                                self.entity)


class SomnolentStrength(Amulet):
    Class, race, name = "Havencraft", "", "Somnolent Strength"
    mana = 2
    index = "SV_Fortune~Havencraft~Amulet~2~~Somnolent Strength~Countdown~Deathrattle~Uncollectible~Legendary"
    requireTarget, description = False, "Countdown (3)At the end of your turn, give +0/+2 to a random allied follower.Last Words: Give -2/-0 to a random enemy follower."
    name_CN = "虚脱的刚腕"

    def __init__(self, Game, ID):
        super().__init__(Game, ID)
        self.counter = 3
        self.trigsBoard = [Trig_Countdown(self), Trig_SomnolentStrength(self)]
        self.deathrattles = [Deathrattle_SomnolentStrength(self)]


class Trig_SomnolentStrength(TrigBoard):
    def __init__(self, entity):
        super().__init__(entity, ["TurnEnds"])

    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
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
                i = npchoice(minions).pos if minions else -1
                curGame.fixedGuides.append(i)
            if i > -1:
                minion = curGame.minions[self.entity.ID][i]
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
                i = npchoice(minions).pos if minions else -1
                curGame.fixedGuides.append(i)
            if i > -1:
                minion = curGame.minions[3 - self.entity.ID][i]
                minion.buffDebuff(-2, 0)


class VIIISofinaStrength_Accelerate(SVSpell):
    Class, school, name = "Havencraft", "", "VIII. Sofina, Strength"
    requireTarget, mana = False, 2
    index = "SV_Fortune~Havencraft~Spell~2~~VIII. Sofina, Strength~Accelerate~Uncollectible~Legendary"
    description = "Summon a Somnolent Strength."
    name_CN = "《力量》·索菲娜"

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        self.Game.summon([SomnolentStrength(self.Game, self.ID)], (-1, "totheRightEnd"),
                         self)
        return None


class VIIISofinaStrength(SVMinion):
    Class, race, name = "Havencraft", "", "VIII. Sofina, Strength"
    mana, attack, health = 5, 2, 6
    index = "SV_Fortune~Havencraft~Minion~5~2~6~~VIII. Sofina, Strength~Accelerate~Battlecry~Legendary"
    requireTarget, keyWord, description = False, "", "Accelerate (2): Summon a Somnolent Strength.Fanfare: Give all other allied followers +1/+1 and Ward.While this follower is in play, all allied followers in play and that come into play can't take more than 3 damage at a time."
    accelerateSpell = VIIISofinaStrength_Accelerate
    attackAdd, healthAdd = 2, 2
    name_CN = "《力量》·索菲娜"

    def __init__(self, Game, ID):
        super().__init__(Game, ID)
        self.auras["Buff Aura"] = BuffAura_VIIISofinaStrength(self)

    def getMana(self):
        if self.Game.Manas.manas[self.ID] < self.mana:
            return 2
        else:
            return self.mana

    def willAccelerate(self):
        curMana = self.Game.Manas.manas[self.ID]
        return self.mana > curMana >= 2

    def effCanTrig(self):
        if self.willAccelerate() and self.targetExists():
            self.effectViable = "sky blue"
        else:
            self.effectViable = False

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        for minion in self.Game.minionsonBoard(self.ID, self):
            minion.buffDebuff(1, 1)
            minion.getsStatus("Taunt")
        return None


class BuffAura_VIIISofinaStrength(HasAura_toMinion):
    def __init__(self, entity):
        self.entity = entity
        self.signals, self.auraAffected = ["MinionAppears"], []

    # All minions appearing on the same side will be subject to the buffAura.
    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.onBoard and subject.ID == self.entity.ID

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        self.applies(signal, subject)

    def applies(self, signal, subject):
        trigger = Trig_VIIISofinaStrength_MaxDamage(subject)
        subject.trigsBoard.append(trigger)
        trigger.connect()

    def auraAppears(self):
        for minion in self.entity.Game.minionsonBoard(self.entity.ID):
            self.applies("MinionAppears", minion)

    def auraDisappears(self):
        for minion in self.entity.Game.minionsonBoard(self.entity.ID):
            for trigger in self.entity.Game.heroes[self.entity.ID].trigsBoard:
                if type(trigger) == Trig_VIIISofinaStrength_MaxDamage:
                    self.entity.Game.heroes[self.entity.ID].trigsBoard.remove(trigger)
                    break

    def selfCopy(self, recipient):
        return type(self)(recipient)


class Trig_VIIISofinaStrength_MaxDamage(TrigBoard):
    def __init__(self, entity):
        super().__init__(entity, ["BattleDmgHero", "BattleDmgMinion", "AbilityDmgHero", "AbilityDmgMinion"])

    def canTrig(self, signal, ID, subject, target, number, comment,
                choice=0):  # target here holds the actual target object
        return target == self.entity

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        number[0] = min(3, number[0])


class PuresongPriest_Accelerate(SVSpell):
    Class, school, name = "Havencraft", "", "Puresong Priest"
    requireTarget, mana = False, 1
    index = "SV_Fortune~Havencraft~Spell~1~~Puresong Priest~Accelerate~Uncollectible"
    description = "Restore 1 defense to your leader. If an allied follower with Ward is in play, draw a card."
    name_CN = "光明神父"

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        self.restoresHealth(self.Game.heroes[self.ID], 1)
        hasTaunt = False
        for minion in self.Game.minionsAlive(self.ID):
            if minion != self and minion.keyWords["Taunt"] > 0:
                hasTaunt = True
                break
        if hasTaunt:
            self.Game.Hand_Deck.drawCard(self.ID)
        return None


class PuresongPriest(SVMinion):
    Class, race, name = "Havencraft", "", "Puresong Priest"
    mana, attack, health = 6, 5, 5
    index = "SV_Fortune~Havencraft~Minion~6~5~5~~Puresong Priest~Accelerate~Battlecry"
    requireTarget, keyWord, description = False, "", "Accelerate (1): Restore 1 defense to your leader. If an allied follower with Ward is in play, draw a card.Fanfare: Restore 4 defense to all allies."
    accelerateSpell = PuresongPriest_Accelerate
    attackAdd, healthAdd = 2, 2
    name_CN = "光明神父"

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

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        chars = self.Game.charsAlive(self.ID)
        self.restoresAOE(chars, 4)
        return None


"""Portalcraft cards"""


class ArtifactScan(SVSpell):
    Class, school, name = "Portalcraft", "", "Artifact Scan"
    requireTarget, mana = False, 1
    index = "SV_Fortune~Portalcraft~Spell~0~~Artifact Scan"
    description = "Put copies of 2 random allied Artifact cards with different names destroyed this match into your hand. Then, if at least 6 allied Artifact cards with different names have been destroyed this match, change their costs to 0."
    name_CN = "创造物扫描"

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if self.Game.mode == 0:
            types = None
            if self.Game.guides:
                types = self.Game.guides.pop(0)
                if types:
                    types = list(types)
            else:
                indices = self.Game.Counters.artifactsDiedThisGame[self.ID].keys()
                if len(indices) == 0:
                    self.Game.fixedGuides.append(None)
                    types = None
                elif len(indices) == 1:
                    self.Game.fixedGuides.append(tuple([indices[0]]))
                    types = [indices[0]]
                else:
                    types = []
                    while len(types) < 2:
                        t = npchoice(indices)
                        if t not in types:
                            types.append(t)
                    self.Game.fixedGuides.append(tuple(types))
            if types:
                minions = []
                for t in types:
                    minions.append(self.Game.cardPool[t](self.Game, self.ID))
                self.Game.Hand_Deck.addCardtoHand(minions, self.ID)
                if len(self.Game.Counters.artifactsDiedThisGame[self.ID]) >= 6:
                    for m in minions:
                        ManaMod(m, changeby=0, changeto=0).applies()


class RoboticEngineer(SVMinion):
    Class, race, name = "Portalcraft", "", "Robotic Engineer"
    mana, attack, health = 1, 1, 1
    index = "SV_Fortune~Portalcraft~Minion~1~1~1~~Robotic Engineer~Deathrattle"
    requireTarget, keyWord, description = False, "", "Last Words: Put a Paradigm Shift into your hand."
    attackAdd, healthAdd = 2, 2
    name_CN = "机械技师"

    def __init__(self, Game, ID):
        super().__init__(Game, ID)
        self.deathrattles = [Deathrattle_RoboticEngineer(self)]


class Deathrattle_RoboticEngineer(Deathrattle_Minion):
    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        self.entity.Game.Hand_Deck.addCardtoHand(ParadigmShift, self.entity.ID, byType=True)


class MarionetteExpert(SVMinion):
    Class, race, name = "Portalcraft", "", "Marionette Expert"
    mana, attack, health = 2, 2, 2
    index = "SV_Fortune~Portalcraft~Minion~2~2~2~~Marionette Expert~Deathrattle"
    requireTarget, keyWord, description = False, "", "Last Words: Put a Puppet into your hand."
    attackAdd, healthAdd = 2, 2
    name_CN = "持偶者"

    def __init__(self, Game, ID):
        super().__init__(Game, ID)
        self.deathrattles = [Deathrattle_MarionetteExpert(self)]


class Deathrattle_MarionetteExpert(Deathrattle_Minion):
    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        self.entity.Game.Hand_Deck.addCardtoHand(Puppet, self.entity.ID, byType=True)


class CatTuner(SVMinion):
    Class, race, name = "Portalcraft", "", "Cat Tuner"
    mana, attack, health = 2, 1, 3
    index = "SV_Fortune~Portalcraft~Minion~2~1~3~~Cat Tuner"
    requireTarget, keyWord, description = False, "", "At the end of your turn, put a copy of a random allied follower destroyed this match that costs X play points into your hand. X equals your remaining play points."
    attackAdd, healthAdd = 2, 2
    name_CN = "巧猫调律师"

    def __init__(self, Game, ID):
        super().__init__(Game, ID)
        self.trigsBoard = [Trig_CatTuner(self)]


class Trig_CatTuner(TrigBoard):
    def __init__(self, entity):
        super().__init__(entity, ["TurnEnds"])

    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.onBoard and ID == self.entity.ID

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        mana = self.entity.Game.Manas.manas[self.entity.ID]
        curGame = self.entity.Game
        if curGame.mode == 0:
            t = None
            if curGame.guides:
                t = curGame.cardPool[curGame.guides.pop(0)]
            else:
                indices = curGame.Counters.minionsDiedThisGame[ID]
                minions = {}
                for index in indices:
                    try:
                        minions[curGame.cardPool[index].mana].append(curGame.cardPool[index])
                    except:
                        minions[curGame.cardPool[index].mana] = [curGame.cardPool[index]]
                if mana in minions:
                    t = npchoice(minions[mana])
                curGame.fixedGuides.append(t.index)
            if t:
                card = t(curGame, ID)
                curGame.Hand_Deck.addCardtoHand(card, self.entity.ID)
                return subject


class SteelslashTiger(SVMinion):
    Class, race, name = "Portalcraft", "", "Steelslash Tiger"
    mana, attack, health = 3, 1, 5
    index = "SV_Fortune~Portalcraft~Minion~3~1~5~~Steelslash Tiger~Rush~Battlecry"
    requireTarget, keyWord, description = False, "Rush", "Rush. Fanfare: Gain +X/+0. X equals the number of allied Artifact cards with different names destroyed this match."
    attackAdd, healthAdd = 2, 2
    name_CN = "钢之猛虎"

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        n = len(self.Game.Counters.artifactsDiedThisGame[self.ID])
        self.buffDebuff(n, 0)


class WheelofMisfortune(Amulet):
    Class, race, name = "Portalcraft", "", "Wheel of Misfortune"
    mana = 3
    index = "SV_Fortune~Portalcraft~Amulet~3~~Wheel of Misfortune~Countdown~Uncollectible~Legendary"
    requireTarget, description = False, "Countdown (3) At the start of your turn, randomly activate 1 of the following effects.-Add 1 to the cost of all cards in your hand until the end of the turn.-Give -2/-2 to all allied followers.-Summon an enemy Analyzing Artifact.(The same effect will not activate twice.)"
    name_CN = "惨祸的圆环"

    def __init__(self, Game, ID):
        super().__init__(Game, ID)
        self.counter = 3
        self.trigsBoard = [Trig_WheelofMisfortune(self), Trig_Countdown(self)]
        self.progress = 30


class Trig_WheelofMisfortune(TrigBoard):
    def __init__(self, entity):
        super().__init__(entity, ["TurnStarts"])

    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.onBoard and ID == self.entity.ID

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        es = [2, 3, 5]
        ies = []
        for ie in es:
            if self.entity.progress % ie == 0:
                ies.append(ie)
        i = 2
        curGame = self.entity.Game
        if curGame.mode == 0:
            if curGame.guides:
                i, e = curGame.guides.pop(0)
            else:
                i = np.random.choice(ies)
                curGame.fixedGuides.append((i, ""))
                self.entity.progress /= i
        if i == 2:
            tempAura = ManaEffect_WheelofMisfortune(self.entity.Game, self.entity.ID)
            self.entity.Game.Manas.CardAuras.append(tempAura)
            tempAura.auraAppears()
        elif i == 3:
            for minion in self.entity.Game.minionsonBoard(self.entity.ID):
                minion.buffDebuff(-2, -2)
        elif i == 5:
            self.entity.Game.summon([AnalyzingArtifact(self.entity.Game, 3 - self.entity.ID)], (-11, "totheRightEnd"),
                                    self.entity)


class ManaEffect_WheelofMisfortune(TempManaEffect):
    def __init__(self, Game, ID):
        self.Game, self.ID = Game, ID
        self.changeby, self.changeto = +1, -1
        self.temporary = True
        self.auraAffected = []

    def applicable(self, target):
        return target.ID == self.ID

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


class XSlausWheelofFortune(SVMinion):
    Class, race, name = "Portalcraft", "", "X. Slaus, Wheel of Fortune"
    mana, attack, health = 3, 2, 3
    index = "SV_Fortune~Portalcraft~Minion~3~2~3~~X. Slaus, Wheel of Fortune~Battlecry~Legendary"
    requireTarget, keyWord, description = False, "", "Fanfare: If Resonance is active for you, summon an enemy Wheel of Misfortune and banish this follower. At the start of your opponent's turn, if Resonance is active for you, gain +1/+1 and destroy a random enemy follower."
    attackAdd, healthAdd = 2, 2
    name_CN = "《命运之轮》·斯洛士"

    def __init__(self, Game, ID):
        super().__init__(Game, ID)
        self.trigsBoard = [Trig_XSlausWheelofFortune(self)]

    def effCanTrig(self):
        self.effectViable = self.Game.isResonance(self.ID)

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if self.Game.isResonance(self.ID):
            self.Game.summon([WheelofMisfortune(self.Game, 3 - self.ID)], (-11, "totheRightEnd"),
                             self)
            self.Game.banishMinion(self, self)


class Trig_XSlausWheelofFortune(TrigBoard):
    def __init__(self, entity):
        super().__init__(entity, ["TurnStarts"])

    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.onBoard and ID != self.entity.ID

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        if self.entity.Game.isResonance(self.entity.ID):
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
                        curGame.fixedGuides.append((enemy.pos, enemy.type + str(enemy.ID)))
                    else:
                        curGame.fixedGuides.append((0, ''))
                if enemy:
                    self.entity.Game.banishMinion(self.entity, enemy)
            self.entity.buffDebuff(1, 1)


class InvertedManipulation(SVSpell):
    Class, school, name = "Portalcraft", "", "Inverted Manipulation"
    requireTarget, mana = False, 3
    index = "SV_Fortune~Portalcraft~Spell~3~~Inverted Manipulation"
    description = "Put a Puppet into your hand.Give your leader the following effect until the end of the turn: Whenever an allied Puppet comes into play, deal 2 damage to a random enemy follower. If no enemy followers are in play, deal 2 damage to the enemy leader instead. (This effect is not stackable.)"
    name_CN = "人偶的反噬"

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        self.Game.Hand_Deck.addCardtoHand(Puppet, self.ID, byType=True)
        trigger = Trig_InvertedManipulation(self.Game.heroes[self.ID])
        for t in self.Game.heroes[self.ID].trigsBoard:
            if type(t) == type(trigger):
                return
        self.Game.heroes[self.ID].trigsBoard.append(trigger)
        trigger.connect()
        return None


class Trig_InvertedManipulation(TrigBoard):
    def __init__(self, entity):
        super().__init__(entity, ["MinionSummoned", "TurnEnds"])

    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
        if signal == "TurnEnds":
            return self.entity.onBoard and ID != self.entity.ID
        return self.entity.onBoard and subject.ID == self.entity.ID and subject.name == "Puppet"

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        if signal == "TurnEnds":
            for trig in self.entity.trigsBoard:
                if type(trig) == Trig_InvertedManipulation:
                    trig.disconnect()
                    self.entity.trigsBoard.remove(trig)
            return
        enemy = self.entity.Game.heroes[3 - self.entity.ID]
        if len(self.entity.Game.minionsonBoard(3 - self.entity.ID)) > 0:
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
                        curGame.fixedGuides.append((enemy.pos, enemy.type + str(enemy.ID)))
                    else:
                        curGame.fixedGuides.append((0, ''))
        if enemy:
            self.entity.dealsDamage(enemy, 2)


class PowerliftingPuppeteer(SVMinion):
    Class, race, name = "Portalcraft", "", "Powerlifting Puppeteer"
    mana, attack, health = 4, 3, 3
    index = "SV_Fortune~Portalcraft~Minion~4~3~3~~Powerlifting Puppeteer~Battlecry"
    requireTarget, keyWord, description = False, "", "Fanfare: Put 2 Puppets into your hand. At the end of your turn, give +1/+1 to all Puppets in your hand."
    attackAdd, healthAdd = 2, 2
    name_CN = "劲力操偶师"

    def __init__(self, Game, ID):
        super().__init__(Game, ID)
        self.trigsBoard = [Trig_PowerliftingPuppeteer(self)]

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        self.Game.Hand_Deck.addCardtoHand([Puppet for i in range(2)], self.ID, byType=True)


class Trig_PowerliftingPuppeteer(TrigBoard):
    def __init__(self, entity):
        super().__init__(entity, ["TurnEnds"])

    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.onBoard and ID == self.entity.ID

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        for card in self.entity.Game.Hand_Deck.hands[self.entity.ID]:
            if card.type == "Minion" and card.name == "Puppet":
                card.buffDebuff(1, 1)


class DimensionDominator(SVMinion):
    Class, race, name = "Portalcraft", "", "Dimension Dominator"
    mana, attack, health = 4, 4, 3
    index = "SV_Fortune~Portalcraft~Minion~4~4~3~~Dimension Dominator~Battlecry~Legendary"
    requireTarget, keyWord, description = True, "", "Fanfare: Give a follower in your hand Fanfare - Recover 2 play points."
    attackAdd, healthAdd = 2, 2
    name_CN = "次元支配者"

    def targetExists(self, choice=0):
        return not self.Game.Hand_Deck.noMinionsinHand(self.ID, self)

    def targetCorrect(self, target, choice=0):
        if isinstance(target, list): target = target[0]
        return target.ID == self.ID and target.inHand and target != self and target.type == "Minion"

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if target:
            if isinstance(target, list): target = target[0]
            target.appearResponse.append(self.whenAppears)

    def whenAppears(self):
        self.Game.Manas.restoreManaCrystal(2, self.ID)

    def inHandEvolving(self, target=None):
        trigger = Trig_DimensionDominator(self.Game.heroes[self.ID])
        for t in self.Game.heroes[self.ID].trigsBoard:
            if type(t) == type(trigger):
                return
        self.Game.heroes[self.ID].trigsBoard.append(trigger)
        trigger.connect()


class Trig_DimensionDominator(TrigBoard):
    def __init__(self, entity):
        super().__init__(entity, ["MinionSummoned", "TurnEnds"])
        self.progress = 1

    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
        if signal == "TurnEnds":
            return self.entity.onBoard and ID != self.entity.ID
        return self.entity.onBoard and subject.ID == self.entity.ID

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        if signal == "TurnEnds":
            self.progress = 1
        if self.progress > 0:
            self.entity.Game.Manas.restoreManaCrystal(1, self.entity.ID)
            self.progress -= 1


class MindSplitter(SVMinion):
    Class, race, name = "Portalcraft", "", "Mind Splitter"
    mana, attack, health = 5, 4, 4
    index = "SV_Fortune~Portalcraft~Minion~5~4~4~~Mind Splitter~Battlecry"
    requireTarget, keyWord, description = False, "", "Fanfare: Recover X play points. X equals the number of allied followers in play. At the end of your turn, if you have at least 1 play point, draw a card. Then, if you have at least 3 play points, subtract 2 from its cost."
    attackAdd, healthAdd = 2, 2
    name_CN = "神志分割者"

    def __init__(self, Game, ID):
        super().__init__(Game, ID)
        self.trigsBoard = [Trig_MindSplitter(self)]

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        n = len(self.Game.minionsonBoard(self.ID))
        self.Game.Manas.restoreManaCrystal(n, self.ID)


class Trig_MindSplitter(TrigBoard):
    def __init__(self, entity):
        super().__init__(entity, ["TurnEnds"])

    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.onBoard and ID == self.entity.ID

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        mana = self.entity.Game.Manas.manas[self.entity.ID]
        if mana >= 1:
            card = self.entity.Game.Hand_Deck.drawCard(self.entity.ID)[0]
            if mana >= 3:
                ManaMod(card, changeby=-2, changeto=-1).applies()


class PopGoesthePoppet(SVSpell):
    Class, school, name = "Portalcraft", "", "Pop Goes the Poppet"
    requireTarget, mana = True, 5
    index = "SV_Fortune~Portalcraft~Spell~5~~Pop Goes the Poppet"
    description = "Destroy an enemy follower. Then deal X damage to a random enemy follower. X equals the destroyed follower's attack."
    name_CN = "人偶的闪击"

    def available(self):
        return self.selectableEnemyMinionExists()

    def targetCorrect(self, target, choice=0):
        if isinstance(target, list): target = target[0]
        return target.type == "Minion" and target.ID != self.ID and target.onBoard

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if target:
            if isinstance(target, list): target = target[0]
            damage = (target.attack + self.countSpellDamage()) * (2 ** self.countDamageDouble())
            self.Game.killMinion(self, target)
            if len(self.Game.minionsAlive(3 - self.ID)) > 0:
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
                            curGame.fixedGuides.append((enemy.pos, enemy.type + str(enemy.ID)))
                        else:
                            curGame.fixedGuides.append((0, ''))
                    if enemy:
                        self.dealsDamage(enemy, damage)
            return target


"""DLC cards"""


class ArchangelofEvocation(SVMinion):
    Class, race, name = "Neutral", "", "Archangel of Evocation"
    mana, attack, health = 5, 3, 5
    index = "SV_Fortune~Neutral~Minion~5~3~5~~Archangel of Evocation~Taunt~Battlecry"
    requireTarget, keyWord, description = False, "Taunt", "Ward. Fanfare: Add 1 to the cost of all non-follower cards in your opponent's hand until the start of your next turn."
    attackAdd, healthAdd = 2, 2
    name_CN = "降罪之大天使"

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        self.Game.Manas.CardAuras_Backup.append(ManaEffect_ArchangelofEvocation(self.Game, 3 - self.ID))
        return None

    def inHandEvolving(self, target=None):
        self.Game.heroes[self.ID].health_max += 5
        self.restoresHealth(self.Game.heroes[self.ID], 5)


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
    index = "SV_Fortune~Forestcraft~Minion~3~1~5~~Aerin, Forever Brilliant~Legendary"
    requireTarget, keyWord, description = False, "", "Fanfare: Put a random follower with Accelerate from your deck into your hand. Whenever you play a card using its Accelerate effect, deal 2 damage to all enemies."
    attackAdd, healthAdd = 2, 2
    name_CN = "恒久的光辉·艾琳"

    def __init__(self, Game, ID):
        super().__init__(Game, ID)
        self.trigsBoard = [Trig_AerinForeverBrilliant(self)]

    def inHandEvolving(self, target=None):
        curGame = self.Game
        if curGame.mode == 0:
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
        super().__init__(entity, ["AccelerateBeenPlayed"])

    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
        return subject.ID == self.entity.ID and self.entity.onBoard

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        self.entity.restoresHealth(self.entity.Game.heroes[self.entity.ID], 2)
        self.entity.Game.restoreEvolvePoint(self.entity.ID)
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
        super().__init__(entity, ["TurnEnds"])

    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
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
    index = "SV_Fortune~Forestcraft~Minion~4~3~4~~Furious Mountain Deity~Enhance~Battlecry"
    requireTarget, keyWord, description = False, "", "Fanfare: Enhance (7) - Gain +2/+2 and Rush. Strike: Gain +1/+0."
    attackAdd, healthAdd = 2, 2
    name_CN = "震怒的山神"

    def __init__(self, Game, ID):
        super().__init__(Game, ID)
        self.trigsBoard = [Trig_FuriousMountainDeity(self)]

    def getMana(self):
        if self.Game.Manas.manas[self.ID] >= 7:
            return 7
        else:
            return self.mana

    def willEnhance(self):
        return self.Game.Manas.manas[self.ID] >= 7

    def effCanTrig(self):
        self.effectViable = self.willEnhance()

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if comment == 7:
            self.buffDebuff(2, 2)
            self.getsStatus("Rush")
        return target


class Trig_FuriousMountainDeity(TrigBoard):
    def __init__(self, entity):
        super().__init__(entity, ["MinionAttackingMinion", "MinionAttackingHero"])

    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.onBoard and subject.ID == self.entity.ID and subject == self.entity

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        self.entity.buffDebuff(1, 0)


class DeepwoodAnomaly(SVMinion):
    Class, race, name = "Forestcraft", "", "Deepwood Anomaly"
    mana, attack, health = 8, 8, 8
    index = "SV_Fortune~Forestcraft~Minion~8~8~8~~Deepwood Anomaly~Battlecry~Legendary"
    requireTarget, keyWord, description = False, "", "Fanfare: Enhance (7) - Gain +2/+2 and Rush. Strike: Gain +1/+0."
    attackAdd, healthAdd = 2, 2
    name_CN = "森林深处的异种"

    def __init__(self, Game, ID):
        super().__init__(Game, ID)
        self.trigsBoard = [Trig_DeepwoodAnomaly(self)]


class Trig_DeepwoodAnomaly(TrigBoard):
    def __init__(self, entity):
        super().__init__(entity, ["MinionAttackingHero"])

    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.onBoard and subject.ID == self.entity.ID and target.ID != self.entity.ID and subject == self.entity

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        hero = self.entity.Game.heroes[3 - self.entity.ID]
        self.entity.dealsDamage(hero, hero.health)


class LifeBanquet(SVSpell):
    Class, school, name = "Forestcraft", "", "Life Banquet"
    requireTarget, mana = False, 3
    index = "SV_Fortune~Forestcraft~Spell~3~~Life Banquet"
    description = "Draw 2 cards. If at least 2 other cards were played this turn, summon a Furious Mountain Deity. Then, if at least 8 other cards were played this turn, summon 2 Deepwood Anomalies."
    name_CN = "生命的盛宴"

    def effCanTrig(self):
        self.effectViable = self.Game.combCards(self.ID) >= 2

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        self.Game.Hand_Deck.drawCard(self.ID)
        self.Game.Hand_Deck.drawCard(self.ID)
        if self.Game.combCards(self.ID) >= 2:
            self.Game.summon([FuriousMountainDeity(self.Game, self.ID)], (-1, "totheRightEnd"),
                             self)
            if self.Game.combCards(self.ID) >= 8:
                self.Game.summon([DeepwoodAnomaly(self.Game, self.ID)], (-1, "totheRightEnd"),
                                 self)
        return target


class IlmisunaDiscordHawker(SVMinion):
    Class, race, name = "Swordcraft", "Officer", "Ilmisuna, Discord Hawker"
    mana, attack, health = 2, 2, 2
    index = "SV_Fortune~Swordcraft~Minion~2~2~2~Officer~Ilmisuna, Discord Hawker~Battlecry"
    requireTarget, keyWord, description = False, "", "Fanfare: Rally (15) - Recover 1 evolution point."
    attackAdd, healthAdd = 2, 2
    evolveRequireTarget = True
    name_CN = "动乱商人·伊尔米斯娜"

    def evolveTargetExists(self, choice=0):
        return self.selectableEnemyMinionExists()

    def evolveTargetCorrect(self, target, choice=0):
        if isinstance(target, list): target = target[0]
        return target.type == "Minion" and target.onBoard and target.ID != self.ID

    def effCanTrig(self):
        self.effectViable = self.Game.Counters.numMinionsSummonedThisGame[self.ID] >= 15

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if self.Game.Counters.numMinionsSummonedThisGame[self.ID] >= 15:
            self.Game.restoreEvolvePoint(self.ID)
        return None

    def inHandEvolving(self, target=None):
        if target:
            if isinstance(target, list): target = target[0]
            self.dealsDamage(target, len(self.Game.minionsonBoard[self.ID]))
        return target


class AlyaskaWarHawker(SVMinion):
    Class, race, name = "Swordcraft", "Commander", "Alyaska, War Hawker"
    mana, attack, health = 4, 4, 4
    index = "SV_Fortune~Swordcraft~Minion~4~4~4~Commander~Alyaska, War Hawker~Legendary"
    requireTarget, keyWord, description = False, "", "Reduce damage from effects to 0. When an allied Officer follower comes into play, gain the ability to evolve for 0 evolution points."
    attackAdd, healthAdd = 2, 2
    name_CN = "战争商人·阿尔亚斯卡"

    def __init__(self, Game, ID):
        super().__init__(Game, ID)
        self.trigsBoard = [Trig_AlyaskaWarHawker(self)]
        self.marks["Enemy Effect Damage Immune"] = 1

    def inHandEvolving(self, target=None):
        card = ExterminusWeapon(self.Game, self.ID)
        self.Game.Hand_Deck.addCardtoHand(card, self.ID)
        ManaMod(card, changeby=-self.Game.Counters.evolvedThisGame[self.ID], changeto=-1).applies()


class Trig_AlyaskaWarHawker(TrigBoard):
    def __init__(self, entity):
        super().__init__(entity, ["MinionSummoned"])

    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.onBoard and subject.ID == self.entity.ID and subject != self.entity and "Officer" in subject.race

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        self.entity.marks["Free Evolve"] += 1


class ExterminusWeapon(SVMinion):
    Class, race, name = "Swordcraft", "Commander", "Exterminus Weapon"
    mana, attack, health = 8, 6, 6
    index = "SV_Fortune~Swordcraft~Minion~8~6~6~Commander~Exterminus Weapon~Battlecry~Deathrattle~Uncollectible~Legendary"
    requireTarget, keyWord, description = True, "", "Fanfare: Destroy 2 enemy followers. Last Words: Deal 4 damage to the enemy leader."
    attackAdd, healthAdd = 2, 2
    name_CN = "终战兵器"

    def __init__(self, Game, ID):
        super().__init__(Game, ID)
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
        self.entity.dealsDamage(self.entity.Game.heroes[3 - self.entity.ID], 4)


class RunieResoluteDiviner(SVMinion):
    Class, race, name = "Runecraft", "", "Runie, Resolute Diviner"
    mana, attack, health = 2, 1, 2
    index = "SV_Fortune~Runecraft~Minion~2~1~2~~Runie, Resolute Diviner~Spellboost~Battlecry~Legendary"
    requireTarget, keyWord, description = False, "", "Fanfare: Spellboost the cards in your hand 1 time. If this card has been Spellboosted at least 1 time, draw a card. Then, if it has been at least 4 times, deal 3 damage to a random enemy follower. Then, if it has been at least 7 times, deal 3 damage to the enemy leader and restore 3 defense to your leader. Then, if it has been at least 10 times, put 3 Runie, Resolute Diviners into your hand."
    attackAdd, healthAdd = 2, 2
    name_CN = "决意预言者·露妮"

    def __init__(self, Game, ID):
        super().__init__(Game, ID)
        self.trigsHand = [Trig_Spellboost(self)]
        self.progress = 0

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        self.Game.sendSignal("Spellboost", self.ID, self, None, 0, "", choice)
        if self.progress >= 1:
            self.Game.Hand_Deck.drawCard(self.ID)
            if self.progress >= 4:
                curGame = self.Game
                if curGame.mode == 0:
                    if curGame.guides:
                        i = curGame.guides.pop(0)
                    else:
                        minions = curGame.minionsAlive(3 - self.ID)
                        i = npchoice(minions).pos if minions else -1
                        curGame.fixedGuides.append(i)
                    if i > -1:
                        self.dealsDamage(curGame.minions[3 - self.ID][i], 3)
                if self.progress >= 7:
                    self.dealsDamage(self.Game.heroes[3 - self.ID], 3)
                    self.restoresHealth(self.Game.heroes[self.ID], 3)
                    if self.progress >= 10:
                        self.Game.Hand_Deck.addCardtoHand([RunieResoluteDiviner] * 3, self.ID, byType=True,
                                                          creator=type(self))


class AlchemicalCraftschief_Accelerate(SVSpell):
    Class, school, name = "Runecraft", "", "Alchemical Craftschief"
    requireTarget, mana = False, 2
    index = "SV_Fortune~Runecraft~Spell~2~~Alchemical Craftschief~Accelerate~Uncollectible"
    description = "Summon an Earth Essence. Put a 7-play point Alchemical Craftschief (without Accelerate) into your hand and subtract X from its cost. X equals the number of allied Earth Sigil amulets in play."
    name_CN = "矮人工房长"

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        self.Game.summon(EarthEssence(self.Game, self.ID), -1, self)
        n = len(self.Game.earthsonBoard(self.ID))
        card = AlchemicalCraftschief_Token(self.Game, self.ID)
        self.Game.Hand_Deck.addCardtoHand(card, self.ID, creator=type(self))
        ManaMod(card, changeby=-n, changeto=-1).applies()
        return None


class AlchemicalCraftschief_Token(SVMinion):
    Class, race, name = "Runecraft", "", "Alchemical Craftschief"
    mana, attack, health = 7, 4, 4
    index = "SV_Fortune~Runecraft~Minion~7~4~4~~Alchemical Craftschief~Taunt~Battlecry~Uncollectible"
    requireTarget, keyWord, description = True, "Taunt", "Accelerate (2): Summon an Earth Essence. Put a 7-play point Alchemical Craftschief (without Accelerate) into your hand and subtract X from its cost. X equals the number of allied Earth Sigil amulets in play.Ward.Fanfare: Deal 4 damage to an enemy."
    attackAdd, healthAdd = 2, 2
    name_CN = "矮人工房长"

    def targetCorrect(self, target, choice=0):
        if isinstance(target, list): target = target[0]
        return target.type in ["Minion", "Hero"] and target.ID != self.ID and target.onBoard

    def targetExists(self, choice=0):
        return self.selectableEnemyExists()

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if target:
            if isinstance(target, list): target = target[0]
            self.dealsDamage(target, 4)
        return target


class AlchemicalCraftschief(SVMinion):
    Class, race, name = "Runecraft", "", "Alchemical Craftschief"
    mana, attack, health = 8, 4, 4
    index = "SV_Fortune~Runecraft~Minion~8~4~4~~Alchemical Craftschief~Taunt~Battlecry~Accelerate"
    requireTarget, keyWord, description = True, "Taunt", "Accelerate (2): Summon an Earth Essence. Put a 7-play point Alchemical Craftschief (without Accelerate) into your hand and subtract X from its cost. X equals the number of allied Earth Sigil amulets in play.Ward.Fanfare: Deal 4 damage to an enemy."
    accelerateSpell = AlchemicalCraftschief_Accelerate
    attackAdd, healthAdd = 2, 2
    name_CN = "矮人工房长"

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

    def effCanTrig(self):
        if self.willAccelerate() and self.targetExists():
            self.effectViable = "sky blue"
        else:
            self.effectViable = False

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
        return target


class WhitefrostWhisper(SVSpell):
    Class, school, name = "Dragoncraft", "", "Whitefrost Whisper"
    requireTarget, mana = True, 2
    index = "SV_Fortune~Dragoncraft~Spell~2~~Whitefrost Whisper~Uncollectible~Legendary"
    description = "Select an enemy follower and destroy it if it is already damaged. If it has not been damaged, deal 1 damage instead."
    name_CN = "银冰吐息"

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
            else:
                damage = (1 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
                self.dealsDamage(target, damage)
        return target


class FileneAbsoluteZero(SVMinion):
    Class, race, name = "Dragoncraft", "", "Filene, Absolute Zero"
    mana, attack, health = 3, 1, 3
    index = "SV_Fortune~Dragoncraft~Minion~3~1~3~~Filene, Absolute Zero~Battlecry~Legendary"
    requireTarget, keyWord, description = False, "", "Fanfare: Draw a card if Overflow is active for you."
    attackAdd, healthAdd = 2, 2
    name_CN = "绝对零度·菲琳"

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        minions = self.Game.minionsonBoard(3 - self.ID)
        self.dealsAOE(minions, [1 for obj in minions])
        self.Game.Hand_Deck.addCardtoHand(WhitefrostWhisper, self.ID, byType=True, creator=type(self))

    def inHandEvolving(self, target=None):
        card = WhitefrostWhisper(self.Game, self.ID)
        self.Game.Hand_Deck.addCardtoHand(card, self.ID)
        ManaMod(card, changeby=0, changeto=1).applies()


class EternalWhale(SVMinion):
    Class, race, name = "Dragoncraft", "", "Eternal Whale"
    mana, attack, health = 6, 5, 7
    index = "SV_Fortune~Dragoncraft~Minion~6~5~7~~Eternal Whale~Taunt"
    requireTarget, keyWord, description = False, "Taunt", "Ward.When this follower comes into play, deal 2 damage to the enemy leader.When this follower leaves play, put four 1-play point Eternal Whales into your deck. (Transformation doesn't count as leaving play.)"
    attackAdd, healthAdd = 2, 2
    name_CN = "永恒巨鲸"

    def __init__(self, Game, ID):
        super().__init__(Game, ID)
        self.appearResponse = [self.whenAppears]
        self.disappearResponse = [self.whenDisppears]

    def whenAppears(self):
        self.dealsDamage(self.Game.heroes[3 - self.ID], 2)

    def whenDisppears(self):
        cards = [EternalWhale_Token(self.Game, self.ID) for i in range(4)]
        self.Game.Hand_Deck.shuffleintoDeck(cards, creator=self)


class EternalWhale_Token(SVMinion):
    Class, race, name = "Dragoncraft", "", "Eternal Whale"
    mana, attack, health = 1, 5, 7
    index = "SV_Fortune~Dragoncraft~Minion~1~5~7~~Eternal Whale~Taunt~Uncollectible"
    requireTarget, keyWord, description = False, "Taunt", "Ward.When this follower comes into play, deal 2 damage to the enemy leader.When this follower leaves play, put four 1-play point Eternal Whales into your deck. (Transformation doesn't count as leaving play.)"
    attackAdd, healthAdd = 2, 2
    name_CN = "永恒巨鲸"

    def __init__(self, Game, ID):
        super().__init__(Game, ID)
        self.appearResponse = [self.whenAppears]
        self.disappearResponse = [self.whenDisppears]

    def whenAppears(self):
        self.dealsDamage(self.Game.heroes[3 - self.ID], 2)

    def whenDisppears(self):
        cards = [EternalWhale_Token(self.Game, self.ID) for i in range(4)]
        self.Game.Hand_Deck.shuffleintoDeck(cards, creator=self)


class ForcedResurrection(SVSpell):
    Class, school, name = "Shadowcraft", "", "Forced Resurrection"
    requireTarget, mana = True, 2
    index = "SV_Fortune~Shadowcraft~Spell~2~~Forced Resurrection"
    description = "Destroy a follower. Both players perform Reanimate (3)."
    name_CN = "强制轮回"

    def available(self):
        return self.selectableEnemyMinionExists()

    def targetCorrect(self, target, choice=0):
        if isinstance(target, list): target = target[0]
        return target.type == "Minion" and target.ID != self.ID and target.onBoard

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if target:
            if isinstance(target, list): target = target[0]
            self.Game.killMinion(target)
            minion = self.Game.reanimate(self.ID, 3)
            minion = self.Game.reanimate(3 - self.ID, 3)
        return target


class NephthysGoddessofAmenta(SVMinion):
    Class, race, name = "Shadowcraft", "", "Nephthys, Goddess of Amenta"
    mana, attack, health = 6, 5, 5
    index = "SV_Fortune~Shadowcraft~Minion~6~5~5~~Nephthys, Goddess of Amenta~Battlecry~Enhance~Legendary"
    requireTarget, keyWord, description = False, "", "Fanfare: Put 2 random followers of different costs (excluding Nephthys, Goddess of Amenta) from your deck into play and destroy them. Enhance (10): Then, if allied followers that originally cost 1, 2, 3, 4, 5, 6, 7, 8, 9, and 10 play points have been destroyed, win the match."
    attackAdd, healthAdd = 2, 2
    name_CN = "冥府的女主宰·奈芙蒂斯"

    def getMana(self):
        if self.Game.Manas.manas[self.ID] >= 10:
            return 10
        else:
            return self.mana

    def willEnhance(self):
        return self.Game.Manas.manas[self.ID] >= 10

    def effCanTrig(self):
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
                    minion = curGame.summonfrom(i, self.ID, -1, self, fromHand=False)
                    if minion:
                        minions.append(minion)
                else:
                    break
        for minion in minions:
            self.Game.killMinion(self, minion)
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
    Class, school, name = "Bloodcraft", "", "Nightscreech"
    requireTarget, mana = False, 1
    index = "SV_Fortune~Bloodcraft~Spell~1~~Nightscreech"
    description = "Summon a Forest Bat. If Wrath is active for you, evolve it and draw 1 card. Otherwise, deal 1 damage to your leader."
    name_CN = "蝙蝠的鸣噪"

    def effCanTrig(self):
        self.effectViable = self.Game.isWrath(self.ID)

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        minion = ForestBat(self.Game, self.ID)
        self.Game.summon([minion], (-1, "totheRightEnd"), self)
        if self.Game.isWrath(self.ID):
            minion.evolve()
            self.Game.Hand_Deck.drawCard(self.ID)
        else:
            damage = (1 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
            self.dealsDamage(self.Game.heroes[self.ID], damage)
        return target


class Baal(SVMinion):
    Class, race, name = "Bloodcraft", "", "Baal"
    mana, attack, health = 3, 3, 3
    index = "SV_Fortune~Bloodcraft~Minion~3~3~3~~Baal~Battlecry~Fusion~Legendary"
    requireTarget, keyWord, description = False, "", "Fusion: Bloodcraft followers that originally cost 3 play points or less Fanfare: If this card is fused with at least 3 cards, draw cards until there are 6 cards in your hand. Then, if this card is fused with at least 6 cards, deal 6 damage to all enemy followers."
    attackAdd, healthAdd = 2, 2
    name_CN = "芭力"

    def __init__(self, Game, ID):
        super().__init__(Game, ID)
        self.fusion = 1
        self.fusionMaterials = 0

    def findFusionMaterials(self):
        return [card for card in self.Game.Hand_Deck.hands[self.ID] if
                card.type == "Minion" and card != self and card.Class == "Bloodcraft" and type(card).mana <= 3]

    def effCanTrig(self):
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
            n = max(0, 6 - len(self.Game.Hand_Deck.hands[self.ID]))
            for i in range(n):
                self.Game.Hand_Deck.drawCard(self.ID)
            if self.fusionMaterials > 6:
                targets = self.Game.minionsonBoard(3 - self.ID)
                self.dealsAOE(targets, [6 for minion in targets])
        return target


class ServantofDarkness(SVMinion):
    Class, race, name = "Neutral", "", "Servant of Darkness"
    mana, attack, health = 5, 13, 13
    index = "SV_Fortune~Neutral~Minion~5~13~13~~Servant of Darkness~Uncollectible~Legendary"
    requireTarget, keyWord, description = False, "", ""
    attackAdd, healthAdd = 2, 2
    name_CN = "深渊之王的仆从"


class SilentRider(SVMinion):
    Class, race, name = "Neutral", "", "Silent Rider"
    mana, attack, health = 6, 8, 8
    index = "SV_Fortune~Neutral~Minion~6~8~8~~Silent Rider~Charge~Uncollectible~Legendary"
    requireTarget, keyWord, description = False, "Charge", "Storm."
    attackAdd, healthAdd = 2, 2
    name_CN = "沉默的魔将"


class DissDamnation(SVSpell):
    Class, school, name = "Neutral", "", "Dis's Damnation"
    requireTarget, mana = True, 7
    index = "SV_Fortune~Neutral~Spell~7~~Dis's Damnation~Uncollectible~Legendary"
    description = "Deal 7 damage to an enemy. Restore 7 defense to your leader."
    name_CN = "狄斯的制裁"

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
            self.dealsDamage(target, damage)
            self.restoresHealth(self.Game.heroes[self.ID], heal)
        return target


class AstarothsReckoning(SVSpell):
    Class, school, name = "Neutral", "", "Astaroth's Reckoning"
    requireTarget, mana = False, 10
    index = "SV_Fortune~Neutral~Spell~10~~Astaroth's Reckoning~Uncollectible~Legendary"
    description = "Deal damage to the enemy leader until their defense drops to 1."
    name_CN = "阿斯塔罗特的宣判"

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        damage = (self.Game.heroes[3 - self.ID].health - 1 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
        self.dealsDamage(self.Game.heroes[3 - self.ID], damage)
        return False


class PrinceofDarkness(SVMinion):
    Class, race, name = "Neutral", "", "Prince of Darkness"
    mana, attack, health = 10, 6, 6
    index = "SV_Fortune~Neutral~Minion~10~6~6~~Prince of Darkness~Battlecry~Legendary"
    requireTarget, keyWord, description = False, "", "Fanfare: Replace your deck with an Apocalypse Deck."
    attackAdd, healthAdd = 2, 2
    name_CN = "深渊之王"

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
        self.Game.Hand_Deck.shuffleintoDeck(cards, creator=self)
        return None


class DemonofPurgatory(SVMinion):
    Class, race, name = "Neutral", "", "Demon of Purgatory"
    mana, attack, health = 6, 9, 6
    index = "SV_Fortune~Neutral~Minion~6~9~6~~Demon of Purgatory~Battlecry~Uncollectible~Legendary"
    requireTarget, keyWord, description = False, "", "Fanfare: Give the enemy leader the following effect - At the start of your next turn, discard a random card from your hand."
    attackAdd, healthAdd = 2, 2
    name_CN = "边狱的邪祟"

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
        super().__init__(entity, ["TurnStarts"])

    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.onBoard and ID == self.entity.ID

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        curGame = self.entity.Game
        if curGame.mode == 0:
            if curGame.guides:
                i = curGame.guides.pop(0)
            else:
                ownHand = curGame.Hand_Deck.hands[self.entity.ID]
                i = nprandint(len(ownHand)) if ownHand else -1
                curGame.fixedGuides.append(i)
            if i > -1: curGame.Hand_Deck.discard(self.entity.ID, i)


class ScionofDesire(SVMinion):
    Class, race, name = "Neutral", "", "Scion of Desire"
    mana, attack, health = 4, 5, 5
    index = "SV_Fortune~Neutral~Minion~4~5~5~~Scion of Desire~Uncollectible~Legendary"
    requireTarget, keyWord, description = False, "", "At the end of your turn, destroy a random enemy follower. Restore X defense to your leader. X equals that follower's attack."
    attackAdd, healthAdd = 2, 2
    name_CN = "欲望缠身者"

    def __init__(self, Game, ID):
        super().__init__(Game, ID)
        self.trigsBoard = [Trig_ScionofDesire]


class Trig_ScionofDesire(TrigBoard):
    def __init__(self, entity):
        super().__init__(entity, ["TurnEnds"])

    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
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
                    curGame.fixedGuides.append((enemy.pos, enemy.type + str(enemy.ID)))
                else:
                    curGame.fixedGuides.append((0, ''))
            if enemy:
                heal = enemy.attack
                self.entity.Game.killMinion(self.entity, enemy)
                self.entity.restoresHealth(self.entity.Game.heroes[self.entity.ID], heal)


class GluttonousBehemoth(SVMinion):
    Class, race, name = "Neutral", "", "Gluttonous Behemoth"
    mana, attack, health = 7, 7, 7
    index = "SV_Fortune~Neutral~Minion~7~7~7~~Gluttonous Behemoth~Uncollectible~Legendary"
    requireTarget, keyWord, description = False, "", "At the end of your turn, deal 7 damage to the enemy leader."
    attackAdd, healthAdd = 2, 2
    name_CN = "贪食的贝希摩斯"

    def __init__(self, Game, ID):
        super().__init__(Game, ID)
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
        super().__init__(entity, ["TurnEnds"])

    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.onBoard and ID == self.entity.ID

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        self.entity.dealsDamage(self.entity.Game.heroes[3 - self.entity.ID], 7)


class Trig_EvolvedGluttonousBehemoth(TrigBoard):
    def __init__(self, entity):
        super().__init__(entity, ["TurnEnds"])

    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.onBoard and ID == self.entity.ID

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        self.entity.dealsDamage(self.entity.Game.heroes[3 - self.entity.ID], 9)


class ScorpionofGreed(SVMinion):
    Class, race, name = "Neutral", "", "Scorpion of Greed"
    mana, attack, health = 6, 7, 6
    index = "SV_Fortune~Neutral~Minion~6~7~6~~Scorpion of Greed~Charge~Bane~Drain~Uncollectible~Legendary"
    requireTarget, keyWord, description = False, "Charge,Bane,Drain", "Storm.Bane.Drain."
    attackAdd, healthAdd = 2, 2
    name_CN = "贪欲的毒蝎"


class WrathfulIcefiend(SVMinion):
    Class, race, name = "Neutral", "", "Wrathful Icefiend"
    mana, attack, health = 2, 4, 4
    index = "SV_Fortune~Neutral~Minion~2~4~4~~Wrathful Icefiend~Battlecry~Uncollectible~Legendary"
    requireTarget, keyWord, description = False, "", "Fanfare: Recover 2 evolution points."
    attackAdd, healthAdd = 2, 2
    name_CN = "狂怒的冰魔"

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        self.Game.restoreEvolvePoint(self.ID, 2)


class HereticalHellbeast(SVMinion):
    Class, race, name = "Neutral", "", "Heretical Hellbeast"
    mana, attack, health = 8, 8, 8
    index = "SV_Fortune~Neutral~Minion~8~8~8~~Heretical Hellbeast~Battlecry~Taunt~Uncollectible~Legendary"
    requireTarget, keyWord, description = False, "Taunt", "Ward. Fanfare: Deal X damage to your leader. X equals the number of other followers in play. Then destroy all other followers."
    attackAdd, healthAdd = 2, 2
    name_CN = "异端的冥兽"

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        minions = self.Game.minionsAlive(self.ID, self) + self.Game.minionsAlive(3 - self.ID)
        damage = len(minions)
        self.dealsDamage(self.Game.heroes[self.ID], damage)
        self.Game.killMinion(self, minions)


class ViciousCommander(SVMinion):
    Class, race, name = "Neutral", "", "Vicious Commander"
    mana, attack, health = 3, 4, 4
    index = "SV_Fortune~Neutral~Minion~3~4~4~~Vicious Commander~Battlecry~Uncollectible~Legendary"
    requireTarget, keyWord, description = True, "", "Fanfare: Deal 4 damage to an enemy follower."
    attackAdd, healthAdd = 2, 2
    evolveRequireTarget = True
    name_CN = "暴威统率者"

    def evolveTargetExists(self, choice=0):
        return self.selectableEnemyMinionExists()

    def evolveTargetCorrect(self, target, choice=0):
        if isinstance(target, list): target = target[0]
        return target.type == "Minion" and target.onBoard and target.ID != self.ID

    def inHandEvolving(self, target=None):
        if target:
            if isinstance(target, list): target = target[0]
            self.dealsDamage(target, 6)

    def targetExists(self, choice=0):
        return self.selectableEnemyMinionExists()

    def targetCorrect(self, target, choice=0):
        if isinstance(target, list): target = target[0]
        return target.type == "Minion" and target.ID != self.ID and target.onBoard

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if target:
            if isinstance(target, list): target = target[0]
            self.dealsDamage(target, 4)
        return target


class FlamelordofDeceit(SVMinion):
    Class, race, name = "Neutral", "", "Flamelord of Deceit"
    mana, attack, health = 5, 5, 5
    index = "SV_Fortune~Neutral~Minion~5~5~5~~Flamelord of Deceit~Battlecry~Charge~Uncollectible~Legendary"
    requireTarget, keyWord, description = False, "Charge", "Storm.Fanfare: Banish all enemy amulets."
    attackAdd, healthAdd = 2, 2
    name_CN = "恶意的炎帝"

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        self.Game.banishMinion(self, self.Game.amuletsonBoard(3 - self.ID))
        return None


class InfernalGaze(SVSpell):
    Class, school, name = "Neutral", "", "Infernal Gaze"
    requireTarget, mana = False, 1
    index = "SV_Fortune~Neutral~Spell~1~~Infernal Gaze~Uncollectible~Legendary"
    description = "Until the start of your next turn, add 10 to the original cost of spells in your opponent's hand. (Only affects cards in hand at the time this effect is activated.)Draw a card."
    name_CN = "深渊之主的凝视"

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        self.Game.Manas.CardAuras_Backup.append(ManaEffect_InfernalGaze(self.Game, 3 - self.ID))
        self.Game.Hand_Deck.drawCard(self.ID)
        return None


class ManaEffect_InfernalGaze(TempManaEffect):
    def __init__(self, Game, ID):
        self.Game, self.ID = Game, ID
        self.changeby, self.changeto = +10, -1
        self.temporary = True
        self.auraAffected = []

    def applicable(self, target):
        return target.ID == self.ID and target.type == "Spell"

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


class InfernalSurge(SVSpell):
    Class, school, name = "Neutral", "", "Infernal Surge"
    requireTarget, mana = False, 1
    index = "SV_Fortune~Neutral~Spell~1~~Infernal Surge~Uncollectible~Legendary"
    description = "Draw 3 cards."
    name_CN = "深渊之主的波动"

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        self.Game.Hand_Deck.drawCard(self.ID)
        self.Game.Hand_Deck.drawCard(self.ID)
        self.Game.Hand_Deck.drawCard(self.ID)


class Heavenfall(SVSpell):
    Class, school, name = "Neutral", "", "Heavenfall"
    requireTarget, mana = True, 2
    index = "SV_Fortune~Neutral~Spell~2~~Heavenfall~Uncollectible~Legendary"
    description = "Banish an enemy follower or amulet.Draw a card."
    name_CN = "天握"

    def available(self):
        return self.selectableEnemyExists()

    def targetCorrect(self, target, choice=0):
        if isinstance(target, list): target = target[0]
        return (target.type == "Minion" or target.type == "Amulet") and target.ID != self.ID and target.onBoard

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if target:
            if isinstance(target, list): target = target[0]
            self.Game.banishMinion(self, target)
            self.Game.Hand_Deck.drawCard(self.ID)
        return target


class Earthfall(SVSpell):
    Class, school, name = "Neutral", "", "Earthfall"
    requireTarget, mana = False, 4
    index = "SV_Fortune~Neutral~Spell~4~~Earthfall~Uncollectible~Legendary"
    description = "Destroy all non-Neutral followers."
    name_CN = "地坏"

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        minions = []
        for minion in self.Game.minionsAlive(1) + self.Game.minionsAlive(2):
            if minion.Class != "Neutral":
                minions.append(minion)
        self.Game.killMinion(self, minions)


class PrinceofCocytus_Accelerate(SVSpell):
    Class, school, name = "Neutral", "", "Prince of Cocytus"
    requireTarget, mana = False, 3
    index = "SV_Fortune~Neutral~Spell~3~~Prince of Cocytus~Accelerate~Uncollectible~Legendary"
    description = "Randomly put 4 different Cocytus cards into your deck."
    name_CN = "冰狱之王·深渊之主"

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        cards = [
            DemonofPurgatory,
            ScionofDesire,
            GluttonousBehemoth,
            ScorpionofGreed,
            WrathfulIcefiend,
            HereticalHellbeast,
            ViciousCommander,
            FlamelordofDeceit,
            InfernalGaze,
            InfernalSurge,
            Heavenfall,
            Earthfall,
            AstarothsReckoning,
        ]
        curGame = self.Game
        if curGame.mode == 0:
            types = []
            if curGame.guides:
                types = list(curGame.guides.pop(0))
            else:
                while len(types) < 4:
                    t = npchoice(cards)
                    if t not in types:
                        types.append(t)
                curGame.fixedGuides.append(tuple(types))
            if types:
                cards = []
                for t in types:
                    cards.append(t(self.Game, self.ID))
                self.Game.Hand_Deck.shuffleintoDeck(cards, creator=self)
        return None


class PrinceofCocytus(SVMinion):
    Class, race, name = "Neutral", "", "Prince of Cocytus"
    mana, attack, health = 9, 7, 7
    index = "SV_Fortune~Neutral~Minion~9~7~7~~Prince of Cocytus~Accelerate~Battlecry~Legendary"
    requireTarget, keyWord, description = False, "", "Accelerate (3): Randomly put 4 different Cocytus cards into your deck.Fanfare: Replace your deck with a Cocytus Deck."
    accelerateSpell = PrinceofCocytus_Accelerate
    attackAdd, healthAdd = 2, 2
    name_CN = "冰狱之王·深渊之主"

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
        self.Game.Hand_Deck.extractfromDeck(None, self.ID, all=True)
        cards = [
            DemonofPurgatory(self.Game, self.ID),
            ScionofDesire(self.Game, self.ID),
            GluttonousBehemoth(self.Game, self.ID),
            ScorpionofGreed(self.Game, self.ID),
            WrathfulIcefiend(self.Game, self.ID),
            HereticalHellbeast(self.Game, self.ID),
            ViciousCommander(self.Game, self.ID),
            FlamelordofDeceit(self.Game, self.ID),
            InfernalGaze(self.Game, self.ID),
            InfernalSurge(self.Game, self.ID),
            Heavenfall(self.Game, self.ID),
            Earthfall(self.Game, self.ID),
            AstarothsReckoning(self.Game, self.ID),
        ]
        self.Game.Hand_Deck.shuffleintoDeck(cards, creator=self)
        return None


class TempleofHeresy(Amulet):
    Class, race, name = "Heavencraft", "", "Temple of Heresy"
    mana = 1
    index = "SV_Fortune~Heavencraft~Amulet~1~~Temple of Heresy~Countdown~Deathrattle"
    requireTarget, description = False, "Countdown (9)At the start of your turn, if you have more evolution points than your opponent, subtract 1 from this amulet's Countdown. (You have 0 evolution points on turns you are unable to evolve.)Last Words: Randomly put a Prince of Darkness or Prince of Cocytus into your hand and change its cost to 1."
    name_CN = "邪教神殿"

    def __init__(self, Game, ID):
        super().__init__(Game, ID)
        self.counter = 9
        self.trigsBoard = [Trig_Countdown(self), Trig_TempleofHeresy(self)]
        self.deathrattles = [Deathrattle_TempleofHeresy(self)]


class Deathrattle_TempleofHeresy(Deathrattle_Minion):
    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        curGame = self.entity.Game
        if curGame.mode == 0:
            pool = (PrinceofDarkness, PrinceofCocytus)
            if curGame.guides:
                card = curGame.guides.pop(0)
            else:
                card = np.random.choice(pool)
                curGame.fixedGuides.append(card)
            card = card(self.entity.Game, self.entity.ID)
            ManaMod(card, changeby=0, changeto=1).applies()
            self.entity.Game.Hand_Deck.addCardtoHand(card, self.entity.ID, creator=type(self.entity))


class Trig_TempleofHeresy(TrigBoard):
    def __init__(self, entity):
        super().__init__(entity, ["TurnStarts"])

    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.onBoard and ID == self.entity.ID and self.entity.Game.getEvolutionPoint(
            self.entity.ID) > self.entity.Game.getEvolutionPoint(3 - self.entity.ID)

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        self.entity.countdown(self.entity, 1)


class RaRadianceIncarnate(SVMinion):
    Class, race, name = "Havencraft", "", "Ra, Radiance Incarnate"
    mana, attack, health = 5, 5, 5
    index = "SV_Fortune~Havencraft~Minion~5~5~5~~Ra, Radiance Incarnate~Taunt~Battlecry"
    requireTarget, keyWord, description = False, "Taunt", "Ward. Fanfare: Give your leader the following effect - At the end of your turn, deal X damage to the enemy leader. X equals your current turn number minus 5 (no damage is dealt if X is less than 0). (This effect is not stackable and lasts for the rest of the match.)"
    attackAdd, healthAdd = 2, 2
    name_CN = "光辉显世·拉"

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        trigger = Trig_RaRadianceIncarnate(self.Game.heroes[self.ID])
        for t in self.Game.heroes[self.ID].trigsBoard:
            if type(t) == type(trigger):
                return
        self.Game.heroes[self.ID].trigsBoard.append(trigger)
        trigger.connect()
        return None


class Trig_RaRadianceIncarnate(TrigBoard):
    def __init__(self, entity):
        super().__init__(entity, ["TurnEnds"])

    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.onBoard and ID == self.entity.ID

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        turn = self.entity.Game.Counters.turns[self.entity.ID]
        if turn >= 5:
            self.entity.dealsDamage(self.entity.Game.heroes[3 - self.entity.ID], turn - 5)


class LazuliGatewayHomunculus(SVMinion):
    Class, race, name = "Portalcraft", "", "Lazuli, Gateway Homunculus"
    mana, attack, health = 2, 2, 2
    index = "SV_Fortune~Portalcraft~Minion~2~2~2~~Lazuli, Gateway Homunculus~Taunt~Battlecry~Enhance"
    requireTarget, keyWord, description = False, "Taunt", "Ward.Fanfare: Enhance (9) - Randomly put 1 of the highest-cost Portalcraft followers from your deck into play. Activate its Fanfare effects (excluding Choose and targeted effects)."
    attackAdd, healthAdd = 2, 2
    evolveRequireTarget = True
    name_CN = "界门的人造体·拉姿莉"

    def evolveTargetExists(self, choice=0):
        return self.selectableFriendlyMinionExists()

    def evolveTargetCorrect(self, target, choice=0):
        if isinstance(target, list): target = target[0]
        return target.type == "Minion" and target.onBoard and target.ID == self.ID

    def inHandEvolving(self, target=None):
        if target:
            if isinstance(target, list): target = target[0]
            target.marks["Next Damage 0"] = 1

    def getMana(self):
        if self.Game.Manas.manas[self.ID] >= 9:
            return 9
        else:
            return self.mana

    def willEnhance(self):
        return self.Game.Manas.manas[self.ID] >= 9

    def effCanTrig(self):
        self.effectViable = self.willEnhance()

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if comment == 9:
            curGame = self.Game
            maxi = 0
            for card in self.Game.Hand_Deck.decks[self.ID]:
                if card.mana > maxi and card.type == "Minion" and card.Class == "Portalcraft":
                    maxi = card.mana
            if curGame.mode == 0:
                for num in range(2):
                    if curGame.guides:
                        i = curGame.guides.pop(0)
                    else:
                        cards = [i for i, card in enumerate(self.Game.Hand_Deck.decks[self.ID]) if
                                 card.type == "Minion" and card.Class == "Portalcraft" and card.mana == maxi]
                        i = npchoice(cards) if cards and curGame.space(self.ID) > 0 else -1
                        curGame.fixedGuides.append(i)
                    if i > -1:
                        minion = curGame.summonfrom(i, self.ID, -1, self, fromHand=False)
                        if minion and minion.onBoard and "~Battlecry" in minion.index and not minion.requireTarget and "~Choose" not in minion.index:
                            minion.whenEffective(target=None, comment="", choice=0, posinHand=-2)


class SpinariaLucilleKeepers(SVMinion):
    Class, race, name = "Portalcraft", "Artifact", "Spinaria & Lucille, Keepers"
    mana, attack, health = 3, 3, 3
    index = "SV_Fortune~Portalcraft~Minion~3~3~3~Artifact~Spinaria & Lucille, Keepers~Uncollectible~Legendary"
    requireTarget, keyWord, description = False, "", "When this follower comes into play, if at least 6 allied Artifact cards with different names have been destroyed this match, evolve this follower.Can't be evolved using evolution points. (Can be evolved using card effects.)"
    attackAdd, healthAdd = 3, 3
    name_CN = "神秘的遗物·丝碧涅与璐契儿"

    def __init__(self, Game, ID):
        super().__init__(Game, ID)
        self.appearResponse = [self.whenAppears]
        self.marks["Can't Evolve"] = 1

    def whenAppears(self):
        if len(self.Game.Counters.artifactsDiedThisGame[self.ID]) >= 6:
            self.evolve()

    def inEvolving(self):
        trigger = Trig_SpinariaLucilleKeepers(self)
        self.trigsBoard.append(trigger)
        trigger.connect()


class Trig_SpinariaLucilleKeepers(TrigBoard):
    def __init__(self, entity):
        super().__init__(entity, ["MinionAttackingMinion", "MinionAttackingHero"])

    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
        return subject == self.entity and self.entity.onBoard

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        targets = self.entity.Game.minionsonBoard(3 - self.entity.ID)
        self.entity.dealsAOE(targets, [6 for obj in targets])
        self.entity.Game.gathertheDead()
        for trig in self.entity.trigsBoard:
            if type(trig) == Trig_SpinariaLucilleKeepers:
                trig.disconnect()
                self.entity.trigsBoard.remove(trig)


class LucilleKeeperofRelics(SVMinion):
    Class, race, name = "Portalcraft", "", "Lucille, Keeper of Relics"
    mana, attack, health = 5, 4, 4
    index = "SV_Fortune~Portalcraft~Minion~5~4~4~~Lucille, Keeper of Relics~Battlecry~Legendary"
    requireTarget, keyWord, description = False, "", "Fanfare: Put a Spinaria & Lucille, Keepers into your deck. When an allied Artifact card comes into play, gain the ability to evolve for 0 evolution points."
    attackAdd, healthAdd = 0, 0
    name_CN = "遗物守门人·璐契儿"

    def __init__(self, Game, ID):
        super().__init__(Game, ID)
        self.trigsBoard = [Trig_LucilleKeeperofRelics(self)]

    def inHandEvolving(self, target=None):
        self.Game.summon([RadiantArtifact(self.Game, self.ID)], (-1, "totheRightEnd"), self)

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        self.Game.Hand_Deck.shuffleintoDeck([SpinariaLucilleKeepers(self.Game, self.ID)], creator=self)


class Trig_LucilleKeeperofRelics(TrigBoard):
    def __init__(self, entity):
        super().__init__(entity, ["MinionSummoned"])

    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.onBoard and subject.ID == self.entity.ID and subject != self.entity and "Artifact" in subject.race

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        self.entity.marks["Free Evolve"] += 1


SV_Fortune_Indices = {
    "SV_Fortune~Neutral~Minion~2~5~5~~Cloud Gigas~Taunt": CloudGigas,
    "SV_Fortune~Neutral~Spell~2~~Sudden Showers": SuddenShowers,
    "SV_Fortune~Neutral~Minion~4~4~3~~Winged Courier~Deathrattle": WingedCourier,
    "SV_Fortune~Neutral~Minion~4~1~1~~Fieran, Havensent Wind God~Battlecry~Invocation~Legendary": FieranHavensentWindGod,
    "SV_Fortune~Neutral~Spell~4~~Resolve of the Fallen": ResolveoftheFallen,
    "SV_Fortune~Neutral~Minion~5~3~4~~Starbright Deity~Battlecry": StarbrightDeity,
    "SV_Fortune~Neutral~Minion~5~5~5~~XXI. Zelgenea, The World~Battlecry~Invocation~Legendary": XXIZelgeneaTheWorld,
    "SV_Fortune~Neutral~Amulet~6~~Titanic Showdown~Countdown~Deathrattle": TitanicShowdown,
    "SV_Fortune~Neutral~Spell~2~~Pureshot Angel~Accelerate~Uncollectible": PureshotAngel_Accelerate,
    "SV_Fortune~Neutral~Minion~8~6~6~~Pureshot Angel~Battlecry~Accelerate": PureshotAngel,

    "SV_Fortune~Forestcraft~Minion~1~1~1~~Lumbering Carapace~Battlecry": LumberingCarapace,
    "SV_Fortune~Forestcraft~Minion~2~2~2~~Blossoming Archer": BlossomingArcher,
    "SV_Fortune~Forestcraft~Spell~2~~Soothing Spell": SoothingSpell,
    "SV_Fortune~Forestcraft~Minion~3~3~3~~XII. Wolfraud, Hanged Man~Enhance~Battlecry~Legendary": XIIWolfraudHangedMan,
    "SV_Fortune~Forestcraft~Spell~0~~Treacherous Reversal~Uncollectible": TreacherousReversal,
    "SV_Fortune~Forestcraft~Spell~1~~Reclusive Ponderer~Accelerate~Uncollectible": ReclusivePonderer_Accelerate,
    "SV_Fortune~Forestcraft~Minion~4~3~3~~Reclusive Ponderer~Stealth~Accelerate": ReclusivePonderer,
    "SV_Fortune~Forestcraft~Spell~1~~Chipper Skipper~Accelerate~Uncollectible": ChipperSkipper_Accelerate,
    "SV_Fortune~Forestcraft~Minion~4~4~3~~Chipper Skipper~Accelerate": ChipperSkipper,
    "SV_Fortune~Forestcraft~Spell~4~~Fairy Assault": FairyAssault,
    "SV_Fortune~Forestcraft~Minion~5~4~5~~Optimistic Beastmaster~Battlecry": OptimisticBeastmaster,
    "SV_Fortune~Forestcraft~Minion~6~4~4~~Terrorformer~Battlecry~Fusion~Legendary": Terrorformer,
    "SV_Fortune~Forestcraft~Spell~1~~Deepwood Wolf~Accelerate~Uncollectible": DeepwoodWolf_Accelerate,
    "SV_Fortune~Forestcraft~Minion~7~3~3~~Deepwood Wolf~Charge~Accelerate": DeepwoodWolf,
    "SV_Fortune~Forestcraft~Spell~1~~Lionel, Woodland Shadow~Accelerate~Uncollectible": LionelWoodlandShadow_Accelerate,
    "SV_Fortune~Forestcraft~Minion~7~5~6~~Lionel, Woodland Shadow~Battlecry~Accelerate": LionelWoodlandShadow,

    "SV_Fortune~Swordcraft~Minion~1~1~1~Officer~Ernesta, Weapons Hawker~Battlecry": ErnestaWeaponsHawker,
    "SV_Fortune~Swordcraft~Minion~1~4~4~Officer~Dread Hound~Battlecry~Bane~Taunt~Uncollectible": DreadHound,
    "SV_Fortune~Swordcraft~Spell~1~~Pompous Summons": PompousSummons,
    "SV_Fortune~Swordcraft~Spell~1~~Decisive Strike~Enhance": DecisiveStrike,
    "SV_Fortune~Swordcraft~Minion~2~2~1~Officer~Honorable Thief~Battlecry~Deathrattle": HonorableThief,
    "SV_Fortune~Swordcraft~Spell~2~~Shield Phalanx": ShieldPhalanx,
    "SV_Fortune~Swordcraft~Minion~7~5~6~Commander~Frontguard General~Taunt~Deathrattle": FrontguardGeneral,
    "SV_Fortune~Swordcraft~Minion~3~2~3~Officer~Fortress Guard~Taunt~Uncollectible": FortressGuard,
    "SV_Fortune~Swordcraft~Minion~3~2~2~Commander~Empress of Serenity~Battlecry": EmpressofSerenity,
    "SV_Fortune~Swordcraft~Minion~3~3~3~Commander~VII. Oluon, The Chariot~Battlecry~Legendary": VIIOluonTheChariot,
    "SV_Fortune~Swordcraft~Minion~7~8~16~Commander~VII. Oluon, Runaway Chariot~Uncollectible~Legendary": VIIOluonRunawayChariot,
    "SV_Fortune~Swordcraft~Minion~4~3~4~Commander~Prudent General": PrudentGeneral,
    "SV_Fortune~Swordcraft~Minion~5~4~5~Officer~Strikelance Knight~Battlecry": StrikelanceKnight,
    "SV_Fortune~Swordcraft~Minion~6~4~5~Commander~Diamond Paladin~Battlecry~Rush~Legendary": DiamondPaladin,
    "SV_Fortune~Swordcraft~Minion~9~9~7~Commander~Selfless Noble~Battlecry": SelflessNoble,

    "SV_Fortune~Runecraft~Minion~1~1~1~~Juggling Moggy~Battlecry~EarthRite": JugglingMoggy,
    "SV_Fortune~Runecraft~Spell~1~~Magical Augmentation~EarthRite": MagicalAugmentation,
    "SV_Fortune~Runecraft~Minion~2~2~2~~Creative Conjurer~Battlecry~EarthRite": CreativeConjurer,
    "SV_Fortune~Runecraft~Spell~2~~Golem Summoning~Uncollectible": GolemSummoning,
    "SV_Fortune~Runecraft~Minion~2~2~2~~0. Lhynkal, The Fool~Battlecry~Choose~Legendary": LhynkalTheFool,
    "SV_Fortune~Runecraft~Spell~4~~Rite of the Ignorant~Uncollectible~Legendary": RiteoftheIgnorant,
    "SV_Fortune~Runecraft~Spell~2~~Scourge of the Omniscient~Uncollectible~Legendary": ScourgeoftheOmniscient,
    "SV_Fortune~Runecraft~Spell~2~~Authoring Tomorrow": AuthoringTomorrow,
    "SV_Fortune~Runecraft~Spell~2~~Madcap Conjuration": MadcapConjuration,
    "SV_Fortune~Runecraft~Minion~3~3~3~~Arcane Auteur~Deathrattle": ArcaneAuteur,
    "SV_Fortune~Runecraft~Minion~4~3~3~~Piquant Potioneer~Battlecry": PiquantPotioneer,
    "SV_Fortune~Runecraft~Minion~4~2~2~~Imperator of Magic~Battlecry~Enhance~EarthRite": ImperatorofMagic,
    "SV_Fortune~Runecraft~Amulet~5~Earth Sigil~Emergency Summoning~Deathrattle~Uncollectible": EmergencySummoning,
    "SV_Fortune~Neutral~Minion~2~2~2~~Happy Pig~Deathrattle": HappyPig,
    "SV_Fortune~Runecraft~Minion~5~4~4~~Sweetspell Sorcerer": SweetspellSorcerer,
    "SV_Fortune~Runecraft~Spell~2~~Witch Snap": WitchSnap,
    "SV_Fortune~Runecraft~Minion~6~6~6~~Adamantine Golem~Battlecry~EarthRite~Legendary": AdamantineGolem,

    "SV_Fortune~Dragoncraft~Minion~1~1~1~~Dragonclad Lancer~Battlecry": DragoncladLancer,
    "SV_Fortune~Dragoncraft~Minion~2~2~2~~Springwell Dragon Keeper~Battlecry~Enhance": SpringwellDragonKeeper,
    "SV_Fortune~Dragoncraft~Minion~2~1~2~~Tropical Grouper~Battlecry~Enhance": TropicalGrouper,
    "SV_Fortune~Dragoncraft~Minion~2~2~2~~Wavecrest Angler~Battlecry": WavecrestAngler,
    "SV_Fortune~Dragoncraft~Spell~2~~Draconic Call": DraconicCall,
    "SV_Fortune~Dragoncraft~Minion~1~1~2~~Ivory Dragon~Battlecry": IvoryDragon,
    "SV_Fortune~Dragoncraft~Minion~3~1~5~~Heliodragon": Heliodragon,
    "SV_Fortune~Dragoncraft~Minion~3~2~8~~Slaughtering Dragonewt~Bane~Battlecry": SlaughteringDragonewt,
    "SV_Fortune~Dragoncraft~Minion~5~4~4~~Crimson Dragon's Sorrow~Taunt~Battlecry~Legendary~Uncollectible": CrimsonDragonsSorrow,
    "SV_Fortune~Dragoncraft~Minion~7~4~4~~Azure Dragon's Rage~Charge~Legendary~Uncollectible": AzureDragonsRage,
    "SV_Fortune~Dragoncraft~Minion~3~2~3~~Turncoat Dragon Summoner~Battlecry~Legendary": TurncoatDragonSummoner,
    "SV_Fortune~Dragoncraft~Amulet~1~~Dragon's Nest": DragonsNest,
    "SV_Fortune~Dragoncraft~Spell~3~~Dragon Spawning": DragonSpawning,
    "SV_Fortune~Dragoncraft~Spell~4~~Dragon Impact": DragonImpact,
    "SV_Fortune~Dragoncraft~Minion~10~11~8~~XI. Erntz, Justice~Taunt~Legendary": XIErntzJustice,

    "SV_Fortune~Shadowcraft~Minion~2~2~2~~Ghostly Maid~Battlecry": GhostlyMaid,
    "SV_Fortune~Shadowcraft~Minion~2~2~2~~Bonenanza Necromancer~Enhance~Battlecry": BonenanzaNecromancer,
    "SV_Fortune~Shadowcraft~Spell~2~~Savoring Slash": SavoringSlash,
    "SV_Fortune~Shadowcraft~Amulet~2~~Coffin of the Unknown Soul~Countdown~Battlecry~Deathrattle": CoffinoftheUnknownSoul,
    "SV_Fortune~Shadowcraft~Minion~3~3~3~~Spirit Curator~Battlecry": SpiritCurator,
    "SV_Fortune~Shadowcraft~Amulet~1~~Death Fowl~Countdown~Crystallize~Deathrattle~Uncollectible": DeathFowl_Crystallize,
    "SV_Fortune~Shadowcraft~Minion~4~3~3~~Death Fowl~Crystallize~Deathrattle": DeathFowl,
    "SV_Fortune~Shadowcraft~Minion~2~2~2~~Soul Box~Battlecry": SoulBox,
    "SV_Fortune~Shadowcraft~Minion~5~4~4~~VI. Milteo, The Lovers~Battlecry~Enhance~Deathrattle~Legendary": VIMilteoTheLovers,
    "SV_Fortune~Shadowcraft~Amulet~2~~Cloistered Sacristan~Countdown~Crystallize~Deathrattle~Uncollectible": CloisteredSacristan_Crystallize,
    "SV_Fortune~Shadowcraft~Minion~6~5~5~~Cloistered Sacristan~Taunt~Crystallize": CloisteredSacristan,
    "SV_Fortune~Shadowcraft~Minion~8~6~6~~Conquering Dreadlord~Invocation~Legendary": ConqueringDreadlord,
    "SV_Fortune~Shadowcraft~Amulet~2~~Deathbringer~Countdown~Crystallize~Battlecry~Deathrattle~Uncollectible": Deathbringer_Crystallize,
    "SV_Fortune~Shadowcraft~Minion~9~7~7~~Deathbringer~Crystallize": Deathbringer,

    "SV_Fortune~Bloodcraft~Minion~1~1~2~~Silverbolt Hunter~Battlecry~Deathrattle": SilverboltHunter,
    "SV_Fortune~Bloodcraft~Minion~2~1~3~~Moonrise Werewolf~Battlecry~Enhance": MoonriseWerewolf,
    "SV_Fortune~Bloodcraft~Minion~2~2~2~~Whiplash Imp~Battlecry~Enhance": WhiplashImp,
    "SV_Fortune~Bloodcraft~Minion~2~2~2~~Contemptous Demon~Battlecry": ContemptousDemon,
    "SV_Fortune~Bloodcraft~Spell~2~~Dark Summons": DarkSummons,
    "SV_Fortune~Bloodcraft~Minion~3~3~3~~Tyrant of Mayhem~Battlecry": TyrantofMayhem,
    "SV_Fortune~Bloodcraft~Minion~4~4~4~~Curmudgeon Ogre~Battlecry~Enhance": CurmudgeonOgre,
    "SV_Fortune~Bloodcraft~Amulet~3~~Dire Bond": DireBond,
    "SV_Fortune~Bloodcraft~Minion~4~4~3~~Darhold, Abyssal Contract~Battlecry~Legendary": DarholdAbyssalContract,
    "SV_Fortune~Bloodcraft~Spell~5~~Burning Constriction": BurningConstriction,
    "SV_Fortune~Bloodcraft~Spell~1~~Vampire of Calamity~Accelerate~Uncollectible": VampireofCalamity_Accelerate,
    "SV_Fortune~Bloodcraft~Minion~7~7~7~~Vampire of Calamity~Rush~Battlecry~Accelerate": VampireofCalamity,
    "SV_Fortune~Bloodcraft~Amulet~3~~Unselfish Grace~Uncollectible~Legendary": UnselfishGrace,
    "SV_Fortune~Bloodcraft~Spell~1~~Insatiable Desire~Uncollectible~Legendary": InsatiableDesire,
    "SV_Fortune~Bloodcraft~Spell~0~~XIV. Luzen, Temperance~Accelerate~Uncollectible~Legendary": XIVLuzenTemperance_Accelerate,
    "SV_Fortune~Bloodcraft~Minion~4~4~4~~XIV. Luzen, Temperance~Uncollectible~Legendary": XIVLuzenTemperance_Token,
    "SV_Fortune~Bloodcraft~Minion~9~7~7~~XIV. Luzen, Temperance~Accelerate~Legendary": XIVLuzenTemperance,

    "SV_Fortune~Havencraft~Spell~1~~Jeweled Brilliance": JeweledBrilliance,
    "SV_Fortune~Havencraft~Minion~2~2~2~~Stalwart Featherfolk~Taunt~Battlecry": StalwartFeatherfolk,
    "SV_Fortune~Havencraft~Minion~2~3~1~~Prismaplume Bird~Deathrattle": PrismaplumeBird,
    "SV_Fortune~Havencraft~Minion~3~1~4~~Four-Pillar Tortoise~Taunt~Battlecry": FourPillarTortoise,
    "SV_Fortune~Havencraft~Spell~1~~Lorena's Holy Water~Uncollectible": LorenasHolyWater,
    "SV_Fortune~Havencraft~Minion~3~2~3~~Lorena, Iron-Willed Priest~Battlecry": LorenaIronWilledPriest,
    "SV_Fortune~Havencraft~Minion~3~2~2~~Sarissa, Luxflash Spear~Battlecry~Enhance~Legendary": SarissaLuxflashSpear,
    "SV_Fortune~Havencraft~Minion~4~2~5~~Priestess of Foresight~Battlecry": PriestessofForesight,
    "SV_Fortune~Havencraft~Amulet~4~~Holybright Altar~Battlecry~Countdown~Deathrattle": HolybrightAltar,
    "SV_Fortune~Havencraft~Minion~5~2~3~~Reverend Adjudicator~Taunt~Battlecry": ReverendAdjudicator,
    "SV_Fortune~Havencraft~Amulet~2~~Somnolent Strength~Countdown~Deathrattle~Uncollectible~Legendary": SomnolentStrength,
    "SV_Fortune~Havencraft~Spell~2~~VIII. Sofina, Strength~Accelerate~Uncollectible~Legendary": VIIISofinaStrength_Accelerate,
    "SV_Fortune~Havencraft~Minion~5~2~6~~VIII. Sofina, Strength~Accelerate~Battlecry~Legendary": VIIISofinaStrength,
    "SV_Fortune~Havencraft~Spell~1~~Puresong Priest~Accelerate~Uncollectible": PuresongPriest_Accelerate,
    "SV_Fortune~Havencraft~Minion~6~5~5~~Puresong Priest~Accelerate~Battlecry": PuresongPriest,

    "SV_Fortune~Portalcraft~Spell~0~~Artifact Scan": ArtifactScan,
    "SV_Fortune~Portalcraft~Minion~1~1~1~~Robotic Engineer~Deathrattle": RoboticEngineer,
    "SV_Fortune~Portalcraft~Minion~2~2~2~~Marionette Expert~Deathrattle": MarionetteExpert,
    "SV_Fortune~Portalcraft~Minion~2~1~3~~Cat Tuner": CatTuner,
    "SV_Fortune~Portalcraft~Minion~3~1~5~~Steelslash Tiger~Rush~Battlecry": SteelslashTiger,
    "SV_Fortune~Portalcraft~Amulet~3~~Wheel of Misfortune~Countdown~Uncollectible~Legendary": WheelofMisfortune,
    "SV_Fortune~Portalcraft~Minion~3~2~3~~X. Slaus, Wheel of Fortune~Battlecry~Legendary": XSlausWheelofFortune,
    "SV_Fortune~Portalcraft~Spell~3~~Inverted Manipulation": InvertedManipulation,
    "SV_Fortune~Portalcraft~Minion~4~3~3~~Powerlifting Puppeteer~Battlecry": PowerliftingPuppeteer,
    "SV_Fortune~Portalcraft~Minion~4~4~3~~Dimension Dominator~Battlecry~Legendary": DimensionDominator,
    "SV_Fortune~Portalcraft~Minion~5~4~4~~Mind Splitter~Battlecry": MindSplitter,
    "SV_Fortune~Portalcraft~Spell~5~~Pop Goes the Poppet": PopGoesthePoppet,

    "SV_Fortune~Neutral~Minion~5~3~5~~Archangel of Evocation~Taunt~Battlecry": ArchangelofEvocation,
    "SV_Fortune~Forestcraft~Minion~3~1~5~~Aerin, Forever Brilliant~Legendary": AerinForeverBrilliant,
    "SV_Fortune~Forestcraft~Minion~4~3~4~~Furious Mountain Deity~Enhance~Battlecry": FuriousMountainDeity,
    "SV_Fortune~Forestcraft~Minion~8~8~8~~Deepwood Anomaly~Battlecry~Legendary": DeepwoodAnomaly,
    "SV_Fortune~Forestcraft~Spell~3~~Life Banquet": LifeBanquet,
    "SV_Fortune~Swordcraft~Minion~2~2~2~Officer~Ilmisuna, Discord Hawker~Battlecry": IlmisunaDiscordHawker,
    "SV_Fortune~Swordcraft~Minion~4~4~4~Commander~Alyaska, War Hawker~Legendary": AlyaskaWarHawker,
    "SV_Fortune~Swordcraft~Minion~8~6~6~Commander~Exterminus Weapon~Battlecry~Deathrattle~Uncollectible~Legendary": ExterminusWeapon,
    "SV_Fortune~Runecraft~Minion~2~1~2~~Runie, Resolute Diviner~Spellboost~Battlecry~Legendary": RunieResoluteDiviner,
    "SV_Fortune~Runecraft~Spell~2~~Alchemical Craftschief~Accelerate~Uncollectible": AlchemicalCraftschief_Accelerate,
    "SV_Fortune~Runecraft~Minion~7~4~4~~Alchemical Craftschief~Taunt~Battlecry~Uncollectible": AlchemicalCraftschief_Token,
    "SV_Fortune~Runecraft~Minion~8~4~4~~Alchemical Craftschief~Taunt~Battlecry~Accelerate": AlchemicalCraftschief,
    "SV_Fortune~Dragoncraft~Spell~2~~Whitefrost Whisper~Uncollectible~Legendary": WhitefrostWhisper,
    "SV_Fortune~Dragoncraft~Minion~3~1~3~~Filene, Absolute Zero~Battlecry~Legendary": FileneAbsoluteZero,
    "SV_Fortune~Dragoncraft~Minion~6~5~7~~Eternal Whale~Taunt": EternalWhale,
    "SV_Fortune~Dragoncraft~Minion~1~5~7~~Eternal Whale~Taunt~Uncollectible": EternalWhale_Token,
    "SV_Fortune~Shadowcraft~Spell~2~~Forced Resurrection": ForcedResurrection,
    "SV_Fortune~Shadowcraft~Minion~6~5~5~~Nephthys, Goddess of Amenta~Battlecry~Enhance~Legendary": NephthysGoddessofAmenta,
    "SV_Fortune~Bloodcraft~Spell~1~~Nightscreech": Nightscreech,
    "SV_Fortune~Bloodcraft~Minion~3~3~3~~Baal~Battlecry~Fusion~Legendary": Baal,
    "SV_Fortune~Neutral~Minion~5~13~13~~Servant of Darkness~Uncollectible~Legendary": ServantofDarkness,
    "SV_Fortune~Neutral~Minion~6~8~8~~Silent Rider~Charge~Uncollectible~Legendary": SilentRider,
    "SV_Fortune~Neutral~Spell~7~~Dis's Damnation~Uncollectible~Legendary": DissDamnation,
    "SV_Fortune~Neutral~Spell~10~~Astaroth's Reckoning~Uncollectible~Legendary": AstarothsReckoning,
    "SV_Fortune~Neutral~Minion~10~6~6~~Prince of Darkness~Battlecry~Legendary": PrinceofDarkness,
    "SV_Fortune~Neutral~Minion~6~9~6~~Demon of Purgatory~Battlecry~Uncollectible~Legendary": DemonofPurgatory,
    "SV_Fortune~Neutral~Minion~4~5~5~~Scion of Desire~Uncollectible~Legendary": ScionofDesire,
    "SV_Fortune~Neutral~Minion~7~7~7~~Gluttonous Behemoth~Uncollectible~Legendary": GluttonousBehemoth,
    "SV_Fortune~Neutral~Minion~6~7~6~~Scorpion of Greed~Charge~Bane~Drain~Uncollectible~Legendary": ScorpionofGreed,
    "SV_Fortune~Neutral~Minion~2~4~4~~Wrathful Icefiend~Battlecry~Uncollectible~Legendary": WrathfulIcefiend,
    "SV_Fortune~Neutral~Minion~8~8~8~~Heretical Hellbeast~Battlecry~Taunt~Uncollectible~Legendary": HereticalHellbeast,
    "SV_Fortune~Neutral~Minion~3~4~4~~Vicious Commander~Battlecry~Uncollectible~Legendary": ViciousCommander,
    "SV_Fortune~Neutral~Minion~5~5~5~~Flamelord of Deceit~Battlecry~Charge~Uncollectible~Legendary": FlamelordofDeceit,
    "SV_Fortune~Neutral~Spell~1~~Infernal Gaze~Uncollectible~Legendary": InfernalGaze,
    "SV_Fortune~Neutral~Spell~1~~Infernal Surge~Uncollectible~Legendary": InfernalSurge,
    "SV_Fortune~Neutral~Spell~2~~Heavenfall~Uncollectible~Legendary": Heavenfall,
    "SV_Fortune~Neutral~Spell~4~~Earthfall~Uncollectible~Legendary": Earthfall,
    "SV_Fortune~Neutral~Spell~3~~Prince of Cocytus~Accelerate~Uncollectible~Legendary": PrinceofCocytus_Accelerate,
    "SV_Fortune~Neutral~Minion~9~7~7~~Prince of Cocytus~Accelerate~Battlecry~Legendary": PrinceofCocytus,
    "SV_Fortune~Heavencraft~Amulet~1~~Temple of Heresy~Countdown~Deathrattle": TempleofHeresy,
    "SV_Fortune~Havencraft~Minion~5~5~5~~Ra, Radiance Incarnate~Taunt~Battlecry": RaRadianceIncarnate,
    "SV_Fortune~Portalcraft~Minion~2~2~2~~Lazuli, Gateway Homunculus~Taunt~Battlecry~Enhance": LazuliGatewayHomunculus,
    "SV_Fortune~Portalcraft~Minion~3~3~3~Artifact~Spinaria & Lucille, Keepers~Uncollectible~Legendary": SpinariaLucilleKeepers,
    "SV_Fortune~Portalcraft~Minion~5~4~4~~Lucille, Keeper of Relics~Battlecry~Legendary": LucilleKeeperofRelics,

}
