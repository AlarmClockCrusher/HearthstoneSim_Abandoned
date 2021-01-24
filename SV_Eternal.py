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


class IoJourneymage(SVMinion):
    Class, race, name = "Neutral", "", "Io, Journeymage"
    mana, attack, health = 2, 1, 2
    index = "SV_Eternal~Neutral~Minion~2~1~2~None~Io, Journeymage~Battlecry~Enhance"
    requireTarget, keyWord, description = True, "", "Fanfare: Deal 1 damage to an enemy follower and then 1 damage to the enemy leader. Restore 1 defense to your leader.Enhance (5): Deal 2 damage, restore 2 defense, and gain +2/+2 instead.Enhance (8): Deal 4 damage, restore 4 defense, and gain +4/+4 instead."
    attackAdd, healthAdd = 2, 2
    name_CN = "苍心的少女·伊欧"

    def returnTrue(self, choice=0):
        return self.targetExists(choice) and not self.targets

    def getMana(self):
        if self.Game.Manas.manas[self.ID] >= 8:
            return 8
        else:
            if self.Game.Manas.manas[self.ID] >= 5:
                return 5
            else:
                return self.mana

    def willEnhance(self):
        return self.Game.Manas.manas[self.ID] >= 5

    def effCanTrig(self):
        self.effectViable = self.willEnhance()

    def targetExists(self, choice=0):
        return self.selectableEnemyMinionExists()

    def targetCorrect(self, target, choice=0):
        if isinstance(target, list): target = target[0]
        return target.type == "Minion" and target.ID != self.ID and target.onBoard

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if target:
            if isinstance(target, list): target = target[0]
        if comment == 8:
            if target:
                self.dealsDamage(target, 4)
            self.dealsDamage(self.Game.heroes[3 - self.ID], 4)
            self.restoresHealth(self.Game.heroes[self.ID], 4)
            self.buffDebuff(4, 4)
        elif comment == 5:
            if target:
                self.dealsDamage(target, 2)
            self.dealsDamage(self.Game.heroes[3 - self.ID], 2)
            self.restoresHealth(self.Game.heroes[self.ID], 2)
            self.buffDebuff(2, 2)
        else:
            if target:
                self.dealsDamage(target, 1)
            self.dealsDamage(self.Game.heroes[3 - self.ID], 1)
            self.restoresHealth(self.Game.heroes[self.ID], 1)
        return None


class ArchangelofRemembrance(SVMinion):
    Class, race, name = "Neutral", "", "Archangel of Remembrance"
    mana, attack, health = 2, 2, 1
    index = "SV_Eternal~Neutral~Minion~2~2~1~None~Archangel of Remembrance~Battlecry~Enhance"
    requireTarget, keyWord, description = True, "", "Fanfare: Banish an enemy follower with 1 defense."
    attackAdd, healthAdd = 2, 2
    evolveRequireTarget = True
    name_CN = "追忆的大天使"

    def returnTrue(self, choice=0):
        return self.targetExists(choice) and not self.targets

    def targetExists(self, choice=0):
        minions = self.Game.minionsonBoard(3 - self.ID)
        for minion in minions:
            if self.canSelect(minion) and minion.health == 1:
                return True
        return False

    def targetCorrect(self, target, choice=0):
        if isinstance(target, list): target = target[0]
        return target.type == "Minion" and target.ID != self.ID and target.onBoard and target.health == 1

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if target:
            if isinstance(target, list): target = target[0]
            self.Game.banishMinion(self, target)
        return None

    def evolveTargetExists(self, choice=0):
        return len(self.Game.Hand_Deck.hands[self.ID]) > 0

    def evolveTargetCorrect(self, target, choice=0):
        if isinstance(target, list): target = target[0]
        return target.ID == self.ID and target.inHand and target != self

    def inHandEvolving(self, target=None):
        if target:
            if isinstance(target, list): target = target[0]
            self.Game.Hand_Deck.extractfromHand(target, self.ID)
            self.Game.Hand_Deck.shuffleintoDeck([type(target)(self.Game, self.ID)], self.ID)
            self.Game.Hand_Deck.drawCard(self.ID)
            self.Game.Hand_Deck.drawCard(self.ID)
        return target


class GransResolve(SVSpell):
    Class, name = "Neutral", "Gran's Resolve"
    requireTarget, mana = False, 0
    index = "SV_Eternal~Neutral~Spell~0~Gran's Resolve~Legendary~Uncollectible"
    description = "Deal 5 damage to 2 random enemy followers. Put 2 random followers from your deck into your hand."
    name_CN = "古兰的觉悟"

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        curGame = self.Game
        if curGame.mode == 0:
            if curGame.guides:
                i, j = curGame.guides.pop(0)
            else:
                minions = curGame.minionsAlive(3 - self.ID)
                i = npchoice(minions).pos if minions else -1
                curGame.fixedGuides.append(i)
                if len(minions) > 1:
                    minions.remove(minions[i])
                    j = npchoice(minions).pos
                else:
                    j = -1
                curGame.fixedGuides.append(j)
            if i > -1:
                damage = (5 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
                self.dealsDamage(curGame.minions[3 - self.ID][i], damage)
            if j > -1:
                damage = (5 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
                self.dealsDamage(curGame.minions[3 - self.ID][j], damage)
        if curGame.mode == 0:
            if curGame.guides:
                i, j = curGame.guides.pop(0)
            else:
                minions = [i for i, card in enumerate(curGame.Hand_Deck.decks[self.ID]) if
                           card.type == "Minion"]
                i = npchoice(minions) if minions else -1
                curGame.fixedGuides.append(i)
                if len(minions) > 1:
                    minions.remove(minions[i])
                    j = npchoice(minions).pos
                else:
                    j = -1
                curGame.fixedGuides.append(j)
            if i > -1: curGame.Hand_Deck.drawCard(self.ID, i)
            if j > -1: curGame.Hand_Deck.drawCard(self.ID, i)
        return None


class DjeetasDetermination(SVSpell):
    Class, name = "Neutral", "Djeeta's Determination"
    requireTarget, mana = False, 0
    index = "SV_Eternal~Neutral~Spell~0~Djeeta's Determination~Legendary~Uncollectible"
    description = "Deal 10 damage to a random enemy follower.Recover 1 evolution point.Recover 2 play points."
    name_CN = "姬塔的决心"

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
                damage = (10 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
                self.dealsDamage(curGame.minions[3 - self.ID][i], damage)
            self.Game.restoreEvolvePoint(self.ID, 1)
            self.Game.Manas.restoreManaCrystal(2, self.ID)
        return None


class GranDjeetaEternalHeroes(SVMinion):
    Class, race, name = "Neutral", "", "Gran & Djeeta, Eternal Heroes"
    mana, attack, health = 5, 5, 5
    index = "SV_Eternal~Neutral~Minion~5~5~5~None~Gran & Djeeta, Eternal Heroes~Charge~Legendary~Uncollectible"
    requireTarget, keyWord, description = False, "Charge", "Storm.Strike: The next time this follower takes damage, reduce that damage to 0. Rally (20): Gain the following effect - Can attack 2 times per turn. Rally (40): Evolve this follower.Can't be evolved using evolution points. (Can be evolved using card effects.)"
    attackAdd, healthAdd = 5, 5
    name_CN = "统率十天众之人·古兰和姬塔"

    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.trigsBoard = [Trig_GranDjeetaEternalHeroes(self)]
        self.marks["Can't Evolve"] = 1


class Trig_GranDjeetaEternalHeroes(TrigBoard):
    def __init__(self, entity):
        self.blank_init(entity, ["MinionAttackingMinion", "MinionAttackingHero"])

    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.onBoard and subject.ID == self.entity.ID and subject == self.entity

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        self.entity.marks["Next Damage 0"] = 1
        if self.entity.Game.Counters.numMinionsSummonedThisGame[self.entity.ID] >= 20:
            self.entity.getsKeyword("Windfury")
            if self.entity.Game.Counters.numMinionsSummonedThisGame[self.entity.ID] >= 40:
                self.entity.evolve()


class OnWingsofTomorrow(SVSpell):
    Class, name = "Neutral", "On Wings of Tomorrow"
    requireTarget, mana = False, 5
    index = "SV_Eternal~Neutral~Spell~5~On Wings of Tomorrow~Legendary"
    description = "Choose: Use play points equal to this card's cost and play this card as a Gran's Resolve or Djeeta's Determination. Super Skybound Art (15): Summon a Gran & Djeeta, Eternal Heroes instead."
    name_CN = "飞向未来"

    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.card = None
        self.trigsHand = [Trig_SuperSkyboundArt(self)]

    def becomeswhenPlayed(self):
        if self.card is not None:
            return type(self.card)(self.Game, self.ID), self.getMana()
        else:
            return self, self.getMana()

    def effCanTrig(self):
        for trig in self.trigsHand:
            if type(trig) == Trig_SuperSkyboundArt and trig.progress <= self.Game.Counters.turns[self.ID]:
                self.effectViable = True
                return

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        ssa = False
        for trig in self.trigsHand:
            if type(trig) == Trig_SuperSkyboundArt and trig.progress <= self.Game.Counters.turns[self.ID]:
                ssa = True
                break
        if ssa:
            self.Game.summon([GranDjeetaEternalHeroes(self.Game, self.ID)], (-1, "totheRightEnd"), self.ID)
        else:
            curGame = self.Game
            if curGame.mode == 0:
                if curGame.guides:
                    self.card = curGame.guides.pop(0)
                else:
                    curGame.options = [GransResolve(self.Game, self.ID), DjeetasDetermination(self.Game, self.ID)]
                    curGame.Discover.startDiscover(self)
        return None

    def discoverDecided(self, option, pool):
        self.card = option


class Trig_SkyboundArt(TrigHand):
    def __init__(self, entity):
        self.blank_init(entity, ["MinionEvolved"])
        self.progress = 10

    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.inHand and subject.ID == self.entity.ID

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        self.entity.progress -= 1

    def selfCopy(self, recipient):
        trigCopy = type(self)(recipient)
        trigCopy.progress = self.progress
        return trigCopy

    def createCopy(self, game):
        if self not in game.copiedObjs:  # 这个扳机没有被复制过
            entityCopy = self.entity.createCopy(game)
            trigCopy = type(self)(entityCopy)
            trigCopy.progress = self.progress
            game.copiedObjs[self] = trigCopy
            return trigCopy
        else:  # 一个扳机被复制过了，则其携带者也被复制过了
            return game.copiedObjs[self]


class Trig_SuperSkyboundArt(TrigHand):
    def __init__(self, entity):
        self.blank_init(entity, ["MinionEvolved"])
        self.progress = 15

    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.inHand and subject.ID == self.entity.ID

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        self.entity.progress -= 1

    def selfCopy(self, recipient):
        trigCopy = type(self)(recipient)
        trigCopy.progress = self.progress
        return trigCopy

    def createCopy(self, game):
        if self not in game.copiedObjs:  # 这个扳机没有被复制过
            entityCopy = self.entity.createCopy(game)
            trigCopy = type(self)(entityCopy)
            trigCopy.progress = self.progress
            game.copiedObjs[self] = trigCopy
            return trigCopy
        else:  # 一个扳机被复制过了，则其携带者也被复制过了
            return game.copiedObjs[self]


class BahamutPrimevalDragon_Accelerate(SVSpell):
    Class, name = "Neutral", "Bahamut, Primeval Dragon"
    requireTarget, mana = False, 5
    index = "SV_Eternal~Neutral~Spell~5~Bahamut, Primeval Dragon~Accelerate~Legendary~Uncollectible"
    description = "Deal 4 damage to all followers. Give your leader the following effect until the end of the turn: Allied followers, spells, and effects deal +1 damage."
    name_CN = "原初之龙·巴哈姆特"

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        targets = self.Game.minionsonBoard(1) + self.Game.minionsonBoard(2)
        damage = (4 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
        self.dealsAOE(targets, [damage for minion in targets])
        trigger = Trig_BahamutPrimevalDragon_Accelerate(self.Game.heroes[self.ID])
        self.Game.heroes[self.ID].trigsBoard.append(trigger)
        trigger.connect()
        return None


class Trig_BahamutPrimevalDragon_Accelerate(TrigBoard):
    def __init__(self, entity):
        self.blank_init(entity, ["BattleDmgHero", "BattleDmgMinion", "AbilityDmgHero", "AbilityDmgMinion", "TurnEnds"])

    def canTrig(self, signal, ID, subject, target, number, comment,
                choice=0):  # target here holds the actual target object
        return signal[0] == 'T' and ID == self.entity.ID or subject.ID == self.entity.ID

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        if signal[0] == 'T':
            try:
                self.entity.trigsBoard.remove(self)
            except:
                pass
            self.disconnect()
        else:
            number[0] += 1


class BahamutPrimevalDragon(SVMinion):
    Class, race, name = "Neutral", "", "Bahamut, Primeval Dragon"
    mana, attack, health = 10, 12, 10
    index = "SV_Eternal~Neutral~Minion~10~12~10~None~Bahamut, Primeval Dragon~Battlecry~Accelerate~Legendary"
    requireTarget, keyWord, description = False, "", "Accelerate (5): Deal 4 damage to all followers. Give your leader the following effect until the end of the turn: Allied followers, spells, and effects deal +1 damage.Fanfare: Deal a pool of 12 damage divided between all other followers and the enemy leader. First deal damage to allied followers equal to their defense in the order they came into play. Then do the same for enemy followers. If any damage is left in the pool afterward, deal it to the enemy leader."
    attackAdd, healthAdd = 2, 2
    accelerateSpell = BahamutPrimevalDragon_Accelerate
    name_CN = "原初之龙·巴哈姆特"

    def getMana(self):
        if self.Game.Manas.manas[self.ID] < self.mana:
            return 5
        else:
            return self.mana

    def willAccelerate(self):
        curMana = self.Game.Manas.manas[self.ID]
        return self.mana > curMana >= 5

    def effCanTrig(self):
        if self.willAccelerate() and self.targetExists():
            self.effectViable = "sky blue"
        else:
            self.effectViable = False

    def available(self):
        if self.willAccelerate():
            return True
        return True

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        damage = 12
        targets = []
        targets.extend(self.Game.minionsonBoard(self.ID, self))
        targets.extend(self.Game.minionsonBoard(3 - self.ID))
        targets.append(self.Game.heroes[3 - self.ID])
        for t in targets:
            health = t.health
            if damage <= health:
                self.dealsDamage(t, damage)
                break
            else:
                self.dealsDamage(t, health)
                damage -= health
        return None


"""Forestcraft cards"""

"""Swordcraft cards"""

"""Runecraft cards"""

"""Dragoncraft cards"""

"""Shadowcraft cards"""

"""Bloodcraft cards"""

"""Havencraft cards"""


class SummitTemple(Amulet):
    Class, race, name = "Havencraft", "", "Summit Temple"
    mana = 1
    index = "SV_Eternal~Havencraft~Amulet~1~Battlecry~Summit Temple"
    requireTarget, description = False, "Fanfare: If any other allied Summit Temples are in play, draw a card and then destroy this amulet.Whenever an allied Havencraft follower attacks, give it the following effect until the end of the turn: This follower deals damage equal to its defense."
    name_CN = "峰顶的教会"

    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.trigsBoard = [Trig_SummitTemple(self)]

    def effCanTrig(self):
        self.effectViable = any(amulet.name == "Summit Temple" for amulet in self.Game.amuletsonBoard(self.ID, self))

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if any(amulet.name == "Summit Temple" for amulet in self.Game.amuletsonBoard(self.ID, self)):
            self.Game.Hand_Deck.drawCard(self.ID)
            self.Game.killMinion(self, self)
        return None


class Trig_SummitTemple(TrigBoard):
    def __init__(self, entity):
        self.blank_init(entity, ["MinionAttacksHero", "MinionAttacksMinion"])

    def canTrig(self, signal, ID, subject, target, number, comment,
                choice=0):  # target here holds the actual target object
        return subject.ID == self.entity.ID and subject.Class == "Havencraft"

    def text(self, CHN):
        return "" if CHN else "When an allied Havencraft follower attacks, give it 'This follower deals damage equal to its defense until the end of this turn'"

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        trig = Trig_AttUsesHealth(subject)
        subject.trigsBoard.append(trig)
        trig.connect()


class Trig_AttUsesHealth(TrigBoard):
    def __init__(self, entity):
        self.blank_init(entity, ["BattleDmgHero", "BattleDmgMinion", "TurnEnds"])

    def canTrig(self, signal, ID, subject, target, number, comment,
                choice=0):  # target here holds the actual target object
        return signal[0] == 'T' or subject == self.entity

    def text(self, CHN):
        return "该从者给予的战斗伤害等于其生命值" if CHN else "During this turn, this follower deals damage equal to its defense when attacks"

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        if signal[0] == 'T':
            try:
                self.entity.trigsBoard.remove(self)
            except:
                pass
            self.disconnect()
        else:
            number[0] = max(0, self.entity.health)


class NoaPrimalShipwright_Crystallize(Amulet):
    Class, race, name = "Havencraft", "", "Crystallize: Noa, Primal Shipwright"
    mana = 1
    index = "SV_Eternal~Havencraft~Amulet~1~None~Noa, Primal Shipwright~Countdown~Crystallize~Deathrattle~Uncollectible"
    requireTarget, description = False, "Countdown (10) At the end of your turn, subtract X from this amulet's Countdown. X equals the number of allied followers with Ward in play. Last Words: Summon an Anvelt, Judgment's Cannon."
    name_CN = "结晶：星界的艇人·诺亚"

    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.counter = 4
        self.trigsBoard = [Trig_Countdown(self)]
        self.deathrattles = [Deathrattle_NoaPrimalShipwright_Crystallize(self)]


class Deathrattle_NoaPrimalShipwright_Crystallize(Deathrattle_Minion):
    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        self.entity.Game.summon([NoaPrimalShipwright(self.entity.Game, self.entity.ID)], (-1, "totheRightEnd"),
                                self.entity.ID)


class NoaPrimalShipwright(SVMinion):
    Class, race, name = "Havencraft", "", "Noa, Primal Shipwright"
    mana, attack, health = 7, 1, 1
    index = "SV_Eternal~Havencraft~Minion~7~1~1~None~Noa, Primal Shipwright~Taunt~Crystallize"
    requireTarget, keyWord, description = True, "", "Crystallize (1): Countdown (10) At the end of your turn, subtract X from this amulet's Countdown. X equals the number of allied followers with Ward in play.Last Words: Summon an Anvelt, Judgment's Cannon.Ward.When this follower comes into play, deal 4 damage to all enemy followers and then 2 damage to the enemy leader."
    crystallizeAmulet = NoaPrimalShipwright_Crystallize
    attackAdd, healthAdd = 2, 2
    name_CN = "星界的艇人·诺亚"

    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.appearResponse = [self.whenAppears]

    def whenAppears(self):
        link = self.Game.Counters.numMinionsSummonedThisGame[self.ID]
        self.buffDebuff(link, link)
        if link >= 10:
            self.evolve()

    def returnTrue(self, choice=0):
        return self.targetExists(choice) and not self.targets

    def targetExists(self, choice=0):
        if self.willCrystallize():
            return False
        return self.selectableEnemyMinionExists()

    def targetCorrect(self, target, choice=0):
        if isinstance(target, list): target = target[0]
        return not self.willCrystallize() and target.type == "Minion" and target.ID != self.ID and target.onBoard

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if target:
            if isinstance(target, list): target = target[0]
            target.loseAbility()
            target.buffDebuff(0, -5)
        return target

    def getMana(self):
        if self.Game.Manas.manas[self.ID] < self.mana:
            return 1
        else:
            return self.mana

    def willCrystallize(self):
        curMana = self.Game.Manas.manas[self.ID]
        return self.mana > curMana >= 1

    def effCanTrig(self):
        if self.willCrystallize():
            self.effectViable = "sky blue"
        else:
            self.effectViable = False


"""Portalcraft cards"""

"""DLC cards"""

SV_Eternal_Indices = {
    "SV_Eternal~Neutral~Minion~2~1~2~None~Io, Journeymage~Battlecry~Enhance": IoJourneymage,
    "SV_Eternal~Neutral~Minion~2~2~1~None~Archangel of Remembrance~Battlecry~Enhance": ArchangelofRemembrance,
    "SV_Eternal~Neutral~Spell~0~Gran's Resolve~Legendary~Uncollectible": GransResolve,
    "SV_Eternal~Neutral~Spell~0~Djeeta's Determination~Legendary~Uncollectible": DjeetasDetermination,
    "SV_Eternal~Neutral~Minion~5~5~5~None~Gran & Djeeta, Eternal Heroes~Charge~Legendary~Uncollectible": GranDjeetaEternalHeroes,
    "SV_Eternal~Neutral~Spell~5~On Wings of Tomorrow~Legendary": OnWingsofTomorrow,
    "SV_Eternal~Neutral~Spell~5~Bahamut, Primeval Dragon~Accelerate~Legendary~Uncollectible": BahamutPrimevalDragon_Accelerate,
    "SV_Eternal~Neutral~Minion~10~12~10~None~Bahamut, Primeval Dragon~Battlecry~Accelerate~Legendary": BahamutPrimevalDragon,

    "SV_Eternal~Havencraft~Amulet~1~Battlecry~Summit Temple": SummitTemple,
    "SV_Eternal~Havencraft~Amulet~1~None~Noa, Primal Shipwright~Countdown~Crystallize~Deathrattle~Uncollectible": NoaPrimalShipwright_Crystallize,
    "SV_Eternal~Havencraft~Minion~7~1~1~None~Noa, Primal Shipwright~Taunt~Crystallize": NoaPrimalShipwright
}
