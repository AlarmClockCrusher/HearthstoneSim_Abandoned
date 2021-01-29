from CardTypes import *
from SV_Rivayle import BulletBike
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


class MasterSleuth(SVMinion):
    Class, race, name = "Neutral", "", "Master Sleuth"
    mana, attack, health = 2, 2, 2
    index = "SV_Eternal~Neutral~Minion~2~2~2~None~Master Sleuth~Battlecry~Enhance"
    requireTarget, keyWord, description = False, "", "Fanfare: Enhance (5) - Evolve this follower."
    attackAdd, healthAdd = 2, 2
    name_CN = "熟练的侦探"

    def getMana(self):
        if self.Game.Manas.manas[self.ID] >= 5:
            return 5
        else:
            return self.mana

    def willEnhance(self):
        return self.Game.Manas.manas[self.ID] >= 5

    def effCanTrig(self):
        self.effectViable = self.willEnhance()

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if comment == 5:
            self.evolve()

    def inEvolving(self):
        trig = Deathrattle_MasterSleuth(self)
        self.deathrattles.append(trig)
        trig.connect()


class Deathrattle_MasterSleuth(Deathrattle_Minion):
    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        self.entity.Game.summon([MasterSleuth(self.entity.Game, self.entity.ID)], (-1, "totheRightEnd"), self.ID)


class VyrnLilRedDragon(SVMinion):
    Class, race, name = "Neutral", "", "Vyrn, Li'l Red Dragon"
    mana, attack, health = 2, 1, 1
    index = "SV_Eternal~Neutral~Minion~2~1~1~None~Vyrn, Li'l Red Dragon~Battlecry~Enhance"
    requireTarget, keyWord, description = False, "", "Fanfare: Draw a card.Enhance (6): Evolve this follower instead. Recover 4 play points."
    attackAdd, healthAdd = 2, 2
    name_CN = "小小的红龙·碧"

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
            self.evolve()
        else:
            self.Game.Hand_Deck.drawCard(self.ID)


class AngelicMelody(SVSpell):
    Class, name = "Neutral", "Angelic Melody"
    requireTarget, mana = False, 2
    index = "SV_Eternal~Neutral~Spell~2~Angelic Melody"
    description = "Give +0/+1 to all allied followers. Draw a card."
    name_CN = "天使的旋律"

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        for minion in self.Game.minionsonBoard(self.ID):
            minion.buffDebuff(0, 1)
        self.Game.Hand_Deck.drawCard(self.ID)


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
            heal = 4 * (2 ** self.countHealDouble())
            self.restoresHealth(self.Game.heroes[self.ID], heal)
            self.buffDebuff(4, 4)
        elif comment == 5:
            if target:
                self.dealsDamage(target, 2)
            self.dealsDamage(self.Game.heroes[3 - self.ID], 2)
            heal = 2 * (2 ** self.countHealDouble())
            self.restoresHealth(self.Game.heroes[self.ID], heal)
            self.buffDebuff(2, 2)
        else:
            if target:
                self.dealsDamage(target, 1)
            self.dealsDamage(self.Game.heroes[3 - self.ID], 1)
            heal = 1 * (2 ** self.countHealDouble())
            self.restoresHealth(self.Game.heroes[self.ID], heal)
        return None


class ArchangelofRemembrance(SVMinion):
    Class, race, name = "Neutral", "", "Archangel of Remembrance"
    mana, attack, health = 2, 2, 1
    index = "SV_Eternal~Neutral~Minion~2~2~1~None~Archangel of Remembrance~Battlecry"
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


class FluffyAngel(SVMinion):
    Class, race, name = "Neutral", "", "Fluffy Angel"
    mana, attack, health = 3, 2, 3
    index = "SV_Eternal~Neutral~Minion~3~2~3~None~Fluffy Angel~Battlecry~Deathrattle"
    requireTarget, keyWord, description = False, "Taunt", "Ward.Fanfare and Last Words: Restore 2 defense to your leader."
    attackAdd, healthAdd = 2, 2
    name_CN = "飘柔天使"

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        heal = 2 * (2 ** self.countHealDouble())
        self.restoresHealth(self.Game.heroes[self.ID], heal)


class Deathrattle_FluffyAngel(Deathrattle_Minion):
    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        heal = 2 * (2 ** self.entity.countHealDouble())
        self.entity.restoresHealth(self.entity.Game.heroes[self.entity.ID], heal)


class EugenStalwartSkyfarer(SVMinion):
    Class, race, name = "Neutral", "", "Eugen, Stalwart Skyfarer"
    mana, attack, health = 4, 4, 3
    index = "SV_Eternal~Neutral~Minion~3~2~3~None~Eugen, Stalwart Skyfarer"
    requireTarget, keyWord, description = False, "", "Clash: Give +1/+0 to all allied followers.Can evolve for 0 evolution points."
    attackAdd, healthAdd = 2, 2
    name_CN = "苍烈的志士·欧根"

    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.trigsBoard = [Trig_EugenStalwartSkyfarer(self)]
        self.marks["Free Evolve"] = 1


class Trig_EugenStalwartSkyfarer(TrigBoard):
    def __init__(self, entity):
        self.blank_init(entity, ["MinionAttackingMinion"])

    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.onBoard and (subject == self.entity or target == self.entity)

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        for minion in self.entity.Game.minionsonBoard(self.entity.ID):
            minion.buffDebuff(1, 0)


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
class AgewornWeaponry(Amulet):
    Class, race, name = "Swordcraft", "", "Ageworn Weaponry"
    mana = 2
    index = "SV_Eternal~Swordcraft~Amulet~2~Battlecry~Ageworn Weaponry"
    requireTarget, description = False, ""
    name_CN = "历战的兵器"
    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.trigsBoard = [Trig_AgewornWeaponry(self)]
        self.options = [Greatshield_Option(self), Greatsword_Option(self)]
        
    def need2Choose(self):
        return self.Game.Manas.manas[self.ID] > 2 \
                and any("Swordcraft" in minion.Class for minion in self.Game.minionsonBoard(self.ID))
        
    def becomeswhenPlayed(self, choice=0):
        return (self if choice < 0 else self.options[choice]), self.getMana()
        
    def effCanTrig(self):
        self.effectViable = self.Game.Manas.manas[self.ID] > 2 \
                            and any("Swordcraft" in minion.Class for minion in self.Game.minionsonBoard(self.ID))

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if any(amulet.name == "Summit Temple" for amulet in self.Game.amuletsonBoard(self.ID, self)):
            self.Game.Hand_Deck.drawCard(self.ID)
            self.Game.killMinion(self, self)
        return None

class Trig_AgewornWeaponry(TrigBoard):
    def __init__(self, entity):
        self.blank_init(entity, ["TurnEnds"])

    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
        return ID != self.entity.ID and self.onBoard

    def text(self, CHN):
        return "" if CHN else "When an allied Havencraft follower attacks, give it 'This follower deals damage equal to its defense until the end of this turn'"

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        self.entity.Game.summon(Knight(self.entity.Game, self.entity.ID), self.entity.pos+1, self.entity)
        self.counter -= 1
        if self.counter < 1: self.entity.dead = True
        

class Greatshield_Option(ChooseOneOption):
    name, description = "Greatshield", ""
    def available(self):
        return True
        
class Greatsword_Option(ChooseOneOption):
    name, description = "Greatsword", ""
    def available(self):
        return True
        
class Greatshield(Amulet):
    Class, race, name = "Swordcraft", "", "Greatshield"
    mana = 2
    index = "SV_Eternal~Swordcraft~Amulet~2~Battlecry~Greatshield"
    requireTarget, description = False, ""
    name_CN = "坚韧之盾"
   
class Greatsword(Amulet):
    Class, race, name = "Swordcraft", "", "Greatsword"
    mana = 2
    index = "SV_Eternal~Swordcraft~Amulet~2~Battlecry~Greatsword"
    requireTarget, description = False, ""
    name_CN = "锐利之剑"
   
"""Runecraft cards"""
class WalderForestRanger(SVMinion):
    Class, race, name = "Forestcraft", "", "Walder, Forest Ranger"
    mana, attack, health = 1, 1, 1
    index = "SV_Eternal~Forestcraft~Minion~1~1~1~None~Walder, Forest Ranger~Charge~Battlecry~Enhance~Invocation"
    requireTarget, keyWord, description = False, "Charge", "Invocation: When you play a card using its Accelerate effect for the second time this turn, invoke this card.Storm.Fanfare: Enhance (6) - Gain +X/+X. X equals the number of times you've played a card using its Accelerate effect this match."
    attackAdd, healthAdd = 2, 2
    name_CN = "森之战士·维鲁达"
    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.trigsDeck = [Trig_InvocationWalderForestRanger(self)]

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
            n = self.Game.Counters.numAcceleratePlayedThisGame[self.ID]
            self.buffDebuff(n, n)


class Trig_InvocationWalderForestRanger(TrigInvocation):
    def __init__(self, entity):
        self.blank_init(entity, ["AccelerateBeenPlayed"])

    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.inDeck and ID == self.entity.ID and self.entity.Game.space(self.entity.ID) > 0 and \
               self.entity.Game.Counters.numAcceleratePlayedThisTurn[self.entity.ID] == 2


class ElfSorcerer(SVMinion):
    Class, race, name = "Forestcraft", "", "Elf Sorcerer"
    mana, attack, health = 2, 2, 2
    index = "SV_Eternal~Forestcraft~Minion~2~2~2~None~Elf Sorcerer~Battlecry"
    requireTarget, keyWord, description = False, "", "Fanfare: Put a Fairy into your hand."
    attackAdd, healthAdd = 2, 2
    name_CN = "精灵咒术师"

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        self.Game.Hand_Deck.addCardtoHand([Fairy], self.ID, byType=True, creator=type(self))
        return None

    def inHandEvolving(self, target=None):
        for card in self.Game.Hand_Deck.hands[self.ID]:
            if type(card) == Fairy:
                card.getsKeyword("Bane")


class MimlemelFreewheelingLass(SVMinion):
    Class, race, name = "Forestcraft", "", "Mimlemel, Freewheeling Lass"
    mana, attack, health = 2, 2, 2
    index = "SV_Eternal~Forestcraft~Minion~2~2~2~None~Mimlemel, Freewheeling Lass~Battlecry"
    requireTarget, keyWord, description = False, "", "Fanfare: If at least 2 other cards were played this turn, summon a Stumpeye."
    attackAdd, healthAdd = 2, 2
    name_CN = "随心所欲的吹笛人·米姆露梅莫璐"

    def effCanTrig(self):
        self.effectViable = self.Game.combCards(self.ID) >= 2

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        numCardsPlayed = self.Game.combCards(self.ID)
        if numCardsPlayed >= 2:
            self.Game.summon([Stumpeye(self.Game, self.ID)], (-1, "totheRightEnd"), self.ID)
        return None


class Stumpeye(SVMinion):
    Class, race, name = "Forestcraft", "", "Stumpeye"
    mana, attack, health = 4, 4, 1
    index = "SV_Eternal~Forestcraft~Minion~4~4~1~None~Stumpeye~Rush~Uncollectible"
    requireTarget, keyWord, description = False, "Rush", "Rush. Strike: Give +0/+1 to all allied Mimlemel, Freewheeling Lasses."
    attackAdd, healthAdd = 2, 2
    name_CN = "残株"

    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.trigsBoard = [Trig_Stumpeye(self)]


class Trig_Stumpeye(TrigBoard):
    def __init__(self, entity):
        self.blank_init(entity, ["MinionAttackingMinion", "MinionAttackingHero"])

    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
        return subject == self.entity and self.entity.onBoard

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        for minion in self.entity.Game.minionsonBoard(self.entity.ID):
            if minion.name == "Mimlemel, Freewheeling Lass":
                minion.buffDebuff(0, 1)


class BlossomTreant(SVMinion):
    Class, race, name = "Forestcraft", "", "Blossom Treant"
    mana, attack, health = 4, 1, 6
    index = "SV_Eternal~Forestcraft~Minion~4~1~6~None~Blossom Treant~Deathrattle"
    requireTarget, keyWord, description = False, "", "At the start of your turn, evolve this follower.Last Words: Draw a card."
    attackAdd, healthAdd = 4, 0
    name_CN = "盛绽树精"

    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.trigsBoard = [Trig_BlossomTreant(self)]
        self.deathrattles = [Deathrattle_BlossomTreant(self)]

    def inEvolving(self):
        self.getsKeyword("Taunt")
        for trig in self.trigsBoard:
            if type(trig) == Trig_BlossomTreant:
                self.trigsBoard.remove(trig)
                trig.disconnect()
                break


class Trig_BlossomTreant(TrigBoard):
    def __init__(self, entity):
        self.blank_init(entity, ["TurnStarts"])

    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.onBoard and ID == self.entity.ID

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        self.entity.evolve()


class Deathrattle_BlossomTreant(Deathrattle_Minion):
    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        self.entity.Game.Hand_Deck.drawCard(self.entity.ID)


class Astoreth(SVMinion):
    Class, race, name = "Forestcraft", "", "Astoreth"
    mana, attack, health = 4, 4, 4
    index = "SV_Eternal~Forestcraft~Minion~4~4~4~None~Astoreth~Taunt~Battlecry"
    requireTarget, keyWord, description = False, "Taunt", "Ward.Fanfare: If at least 2 other cards were played this turn, evolve this follower."
    attackAdd, healthAdd = 2, 2
    name_CN = "阿斯塔蒂"

    def effCanTrig(self):
        self.effectViable = self.Game.combCards(self.ID) >= 2

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        numCardsPlayed = self.Game.combCards(self.ID)
        if numCardsPlayed >= 2:
            self.evolve()
        return None

    def inEvolving(self):
        trig = Trig_Astoreth(self)
        self.trigsBoard.append(trig)
        trig.connect()


class Trig_Astoreth(TrigBoard):
    def __init__(self, entity):
        self.blank_init(entity, ["MinionAttackingMinion", "MinionAttackingHero"])

    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
        return subject == self.entity and self.entity.onBoard

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        heal = 2 * (2 ** self.entity.countHealDouble())
        self.entity.restoresHealth(self.entity.Game.heroes[self.entity.ID], heal)
        self.entity.Game.Hand_Deck.drawCard(self.entity.ID)


class TweyenDarkHuntress(SVMinion):
    Class, race, name = "Forestcraft", "", "Tweyen, Dark Huntress"
    mana, attack, health = 4, 3, 3
    index = "SV_Eternal~Forestcraft~Minion~4~3~3~None~Tweyen, Dark Huntress~Bane~Battlecry~SkyboundArt~SuperSkyboundArt~Legendary"
    requireTarget, keyWord, description = True, "Bane", "Bane.Fanfare: Select an enemy follower. It can't attack until the end of your opponent's turn.Skybound Art (10): Evolve this follower. Give +2/+0 to all other allied followers.Super Skybound Art (15): Strike - Deal X damage to all enemies. X equals this follower's attack."
    attackAdd, healthAdd = 2, 2
    name_CN = "魔眼的猎人·索恩"

    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.trigsHand = [Trig_SkyboundArt(self), Trig_SuperSkyboundArt(self)]

    def effCanTrig(self):
        for trig in self.trigsHand:
            if type(trig) == Trig_SkyboundArt and trig.progress <= self.Game.Counters.turns[self.ID]:
                self.effectViable = True
                return
            if type(trig) == Trig_SuperSkyboundArt and trig.progress <= self.Game.Counters.turns[self.ID]:
                self.effectViable = True
                return

    def returnTrue(self, choice=0):
        return self.targetExists(choice) and not self.targets

    def targetExists(self, choice=0):
        return self.selectableEnemyMinionExists()

    def targetCorrect(self, target, choice=0):
        if isinstance(target, list): target = target[0]
        return target.type == "Minion" and target.ID != self.ID and target.onBoard

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if target:
            if isinstance(target, list): target = target[0]
            target.getsFrozen()
        sa, ssa = False, False
        for trig in self.trigsHand:
            if type(trig) == Trig_SkyboundArt and trig.progress <= self.Game.Counters.turns[self.ID]:
                sa = True
            if type(trig) == Trig_SuperSkyboundArt and trig.progress <= self.Game.Counters.turns[self.ID]:
                ssa = True
        if sa:
            self.evolve()
            for minion in self.Game.minionsonBoard(self.ID, self):
                minion.buffDebuff(2, 0)
        if ssa:
            trig = Trig_TweyenDarkHuntress(self)
            self.trigsBoard.append(trig)
            trig.connect()


class Trig_TweyenDarkHuntress(TrigBoard):
    def __init__(self, entity):
        self.blank_init(entity, ["MinionAttackingMinion", "MinionAttackingHero"])

    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.onBoard and subject.ID == self.entity.ID and subject == self.entity

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        targets = self.entity.Game.minionsonBoard(3 - self.entity.ID)
        targets.append(self.entity.Game.heroes[3 - self.entity.ID])
        self.entity.dealsAOE(targets, [self.entity.attack for _ in targets])


class GreenwoodReindeer(SVMinion):
    Class, race, name = "Forestcraft", "", "Greenwood Reindeer"
    mana, attack, health = 5, 5, 5
    index = "SV_Eternal~Forestcraft~Minion~5~5~5~None~Greenwood Reindeer~Rush~Battlecry"
    requireTarget, keyWord, description = False, "Rush", "Rush.Fanfare: If at least 2 other cards were played this turn, gain +0/+5."
    attackAdd, healthAdd = 2, 2
    name_CN = "深绿驯鹿"

    def effCanTrig(self):
        self.effectViable = self.Game.combCards(self.ID) >= 2

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        numCardsPlayed = self.Game.combCards(self.ID)
        if numCardsPlayed >= 2:
            self.buffDebuff(0, 5)
        return None


class XenoSagittarius_Crystallize(Amulet):
    Class, race, name = "Forestcraft", "", "Crystallize: Xeno Sagittarius"
    mana = 1
    index = "SV_Eternal~Forestcraft~Amulet~1~None~Xeno Sagittarius~Countdown~Crystallize~Deathrattle~Legendary~Uncollectible"
    requireTarget, description = False, "Countdown (1)When this amulet is returned to your hand, draw a card.Last Words: Draw a card."
    name_CN = "结晶：异种·射手座"

    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.counter = 1
        self.trigsBoard = [Trig_Countdown(self)]
        self.returnResponse = [self.whenReturned]
        self.deathrattles = [Deathrattle_XenoSagittarius_Crystallize(self)]

    def whenReturned(self):
        self.Game.Hand_Deck.drawCard(self.ID)


class Deathrattle_XenoSagittarius_Crystallize(Deathrattle_Minion):
    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        self.entity.Game.Hand_Deck.drawCard(self.entity.ID)


class XenoSagittarius(SVMinion):
    Class, race, name = "Forestcraft", "", "Xeno Sagittarius"
    mana, attack, health = 6, 6, 4
    index = "SV_Eternal~Forestcraft~Minion~6~6~4~None~Xeno Sagittarius~Battlecry~Crystallize~Legendary"
    requireTarget, keyWord, description = False, "", "Crystallize (1): Countdown (1)When this amulet is returned to your hand, draw a card.Last Words: Draw a card.Fanfare: Change the defense of all enemy followers to 1.Strike: Deal 1 damage to all enemy followers.When this follower is returned to your hand, deal 1 damage to all enemy followers."
    crystallizeAmulet = XenoSagittarius_Crystallize
    attackAdd, healthAdd = 2, 2
    name_CN = "异种·射手座"

    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.trigsBoard = [Trig_XenoSagittarius_Attack(self)]
        self.returnResponse = [self.whenReturned]

    def whenReturned(self):
        targets = self.Game.minionsonBoard(3 - self.ID)
        self.dealsAOE(targets, [1 for minion in targets])

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        for minion in self.Game.minionsonBoard(3 - self.ID):
            minion.statReset(newHealth=1)


class Trig_XenoSagittarius_Attack(TrigBoard):
    def __init__(self, entity):
        self.blank_init(entity, ["MinionAttackingMinion", "MinionAttackingHero"])

    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.onBoard and subject.ID == self.entity.ID and subject == self.entity

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        targets = self.entity.Game.minionsonBoard(3 - self.entity.ID)
        self.entity.dealsAOE(targets, [1 for minion in targets])


class NatureConsumed(SVSpell):
    Class, name = "Forestcraft", "Nature Consumed"
    requireTarget, mana = True, 6
    index = "SV_Eternal~Forestcraft~Spell~6~Nature Consumed"
    description = "Destroy an enemy follower.Restore X defense to your leader and draw X cards. X equals half the destroyed follower's defense (rounded up)."
    name_CN = "大自然的捕食"

    def available(self):
        return self.selectableEnemyMinionExists()

    def targetCorrect(self, target, choice=0):
        if isinstance(target, list): target = target[0]
        return target.type == "Minion" and target.ID != self.ID and target.onBoard

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if target:
            if isinstance(target, list): target = target[0]
            x = int((target.health + 0.5) / 2)
            self.Game.killMinion(self, target)
            heal = x * (2 ** self.countHealDouble())
            self.restoresHealth(self.Game.heroes[self.ID], heal)
            for _ in range(x):
                self.Game.Hand_Deck.drawCard(self.ID)
        return target


class PrimordialColossus(SVMinion):
    Class, race, name = "Forestcraft", "", "Primordial Colossus"
    mana, attack, health = 7, 4, 6
    index = "SV_Eternal~Forestcraft~Minion~7~4~6~None~Primordial Colossus~Battlecry"
    requireTarget, keyWord, description = False, "", "Fanfare: Give your leader the following effect - Once on each of your turns, when you play a card, recover 2 play points and add 2 to the number of cards played this turn. (This effect is not stackable and lasts for the rest of the match.)"
    attackAdd, healthAdd = 2, 2
    name_CN = "原始的恶神"

    def inHandEvolving(self, target=None):
        self.Game.Manas.restoreManaCrystal(2, self.ID)

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        trigger = Trig_PrimordialColossus(self.Game.heroes[self.ID])
        self.Game.heroes[self.ID].trigsBoard.append(trigger)
        trigger.connect()


class Trig_PrimordialColossus(TrigBoard):
    def __init__(self, entity):
        self.blank_init(entity, ["MinionPlayed", "SpellPlayed", "WeaponPlayed", "HeroCardPlayed", "AmuletPlayed"])

    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
        return subject.Game.turn == self.entity.ID

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        for t in self.entity.trigsBoard:
            if type(t) == Trig_PrimordialColossus:
                t.disconnect()
                self.entity.trigsBoard.remove(t)
                break
        trigger = Trig_EndPrimordialColossus(self.entity)
        self.entity.trigsBoard.append(trigger)
        trigger.connect()
        self.entity.Game.Manas.restoreManaCrystal(2, self.entity.ID)
        self.entity.Game.Counters.numCardsPlayedThisTurn[self.entity.ID] += 2


class Trig_EndPrimordialColossus(TrigBoard):
    def __init__(self, entity):
        self.blank_init(entity, ["TurnEnds"])

    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.onBoard and ID == self.entity.ID

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        for t in self.entity.trigsBoard:
            if type(t) == Trig_EndPrimordialColossus:
                t.disconnect()
                self.entity.trigsBoard.remove(t)
                break
        trigger = Trig_PrimordialColossus(self.entity)
        self.entity.trigsBoard.append(trigger)
        trigger.connect()


class WindFairy_Accelerate(SVSpell):
    Class, name = "Forestcraft", "Wind Fairy"
    requireTarget, mana = True, 1
    index = "SV_Eternal~Forestcraft~Spell~1~Wind Fairy~Accelerate~Uncollectible"
    description = "Return an allied follower or amulet to your hand. Put a Fairy Wisp into your hand."
    name_CN = "迅风妖精"

    def available(self):
        return self.selectableFriendlyMinionExists() or self.selectableFriendlyAmuletExists()

    def targetCorrect(self, target, choice=0):
        if isinstance(target, list): target = target[0]
        return target.type in ["Minion", "Amulet"] and target.ID == self.ID and target.onBoard

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if target:
            if isinstance(target, list): target = target[0]
            self.Game.returnMiniontoHand(target)
            self.Game.Hand_Deck.addCardtoHand(FairyWisp, self.ID, byType=True, creator=type(self))
        return target


class WindFairy(SVMinion):
    Class, race, name = "Forestcraft", "", "Wind Fairy"
    mana, attack, health = 9, 3, 3
    index = "SV_Eternal~Forestcraft~Minion~9~3~3~None~Wind Fairy~Charge~Windfury~Accelerate"
    requireTarget, keyWord, description = True, "Charge,Windfury", "Fanfare: Give your leader the following effect - Once on each of your turns, when you play a card, recover 2 play points and add 2 to the number of cards played this turn. (This effect is not stackable and lasts for the rest of the match.)"
    accelerateSpell = WindFairy_Accelerate
    attackAdd, healthAdd = 2, 2
    name_CN = "迅风妖精"

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
        return False

    def available(self):
        if self.willAccelerate():
            return self.selectableFriendlyMinionExists() or self.selectableFriendlyAmuletExists()
        return True

    def targetExists(self, choice=0):
        if self.willAccelerate():
            return self.selectableFriendlyMinionExists() or self.selectableFriendlyAmuletExists()
        return False

    def targetCorrect(self, target, choice=0):
        if self.willAccelerate():
            if isinstance(target, list): target = target[0]
            return target.type in ["Minion", "Amulet"] and target.ID == self.ID and target.onBoard
        return False


"""Swordcraft cards"""


class ArthurSlumberingDragon(SVMinion):
    Class, race, name = "Swordcraft", "Officer", "Arthur, Slumbering Dragon"
    mana, attack, health = 2, 1, 3
    index = "SV_Eternal~Swordcraft~Minion~2~1~3~Officer~Arthur, Slumbering Dragon"
    requireTarget, keyWord, description = False, "", "At the end of your turn, Rally (10): Give your leader the following effect - The next time your leader takes damage, reduce that damage to 0."
    attackAdd, healthAdd = 2, 2
    name_CN = "沉睡的辉龙·亚瑟"

    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.trigsBoard = [Trig_ArthurSlumberingDragon(self)]

    def inHandEvolving(self, target=None):
        self.Game.summon([MordredSlumberingLion(self.Game, self.ID)], (-1, "totheRightEnd"), self.ID)


class Trig_ArthurSlumberingDragon(TrigBoard):
    def __init__(self, entity):
        self.blank_init(entity, ["TurnEnds"])

    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.onBoard and ID == self.entity.ID

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        if self.entity.Game.Counters.numMinionsSummonedThisGame[self.entity.ID] >= 10:
            self.entity.Game.heroes[self.entity.ID].marks["Next Damage 0"] = 1


class MordredSlumberingLion(SVMinion):
    Class, race, name = "Swordcraft", "Officer", "Mordred, Slumbering Lion"
    mana, attack, health = 2, 2, 1
    index = "SV_Eternal~Swordcraft~Minion~2~2~1~Officer~Mordred, Slumbering Lion"
    requireTarget, keyWord, description = False, "", "At the end of your turn, Rally (5): Deal 1 damage to all enemy followers."
    attackAdd, healthAdd = 2, 2
    name_CN = "沉睡的狮子·莫德雷德"

    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.trigsBoard = [Trig_MordredSlumberingLion(self)]

    def inHandEvolving(self, target=None):
        self.Game.summon([ArthurSlumberingDragon(self.Game, self.ID)], (-1, "totheRightEnd"), self.ID)


class Trig_MordredSlumberingLion(TrigBoard):
    def __init__(self, entity):
        self.blank_init(entity, ["TurnEnds"])

    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.onBoard and ID == self.entity.ID

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        if self.entity.Game.Counters.numMinionsSummonedThisGame[self.entity.ID] >= 5:
            targets = self.entity.Game.minionsonBoard(3 - self.entity.ID)
            self.entity.dealsAOE(targets, [1 for _ in targets])


class ProvenMethodology(SVSpell):
    Class, name = "Swordcraft", "Proven Methodology"
    requireTarget, mana = False, 2
    index = "SV_Eternal~Swordcraft~Spell~2~Proven Methodology"
    description = "Put a random Officer follower from your deck into your hand and give it +2/+2."
    name_CN = "老练的教鞭"

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        curGame = self.Game
        if curGame.mode == 0:
            if curGame.guides:
                i = curGame.guides.pop(0)
            else:
                officers = [i for i, card in enumerate(curGame.Hand_Deck.decks[self.ID]) if
                            card.type == "Minion" and "Officer" in card.race]
                i = npchoice(officers) if officers else -1
                curGame.fixedGuides.append(i)
            if i > -1:
                card = curGame.Hand_Deck.decks[self.ID][i]
                curGame.Hand_Deck.drawCard(self.ID, i)
                card.buffDebuff(2, 2)
        return None


class MirinSamuraiDreamer(SVMinion):
    Class, race, name = "Swordcraft", "Officer", "Mirin, Samurai Dreamer"
    mana, attack, health = 2, 3, 1
    index = "SV_Eternal~Swordcraft~Minion~2~3~1~Officer~Mirin, Samurai Dreamer~Battlecry~SkyboundArt~SuperSkyboundArt"
    requireTarget, keyWord, description = False, "", "Fanfare: Skybound Art (10) - Deal 3 damage to the enemy leader. Super Skybound Art (15): Deal 6 damage instead."
    attackAdd, healthAdd = 2, 2
    name_CN = "武士梦想家·米琳"

    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.trigsHand = [Trig_SkyboundArt(self), Trig_SuperSkyboundArt(self)]

    def effCanTrig(self):
        for trig in self.trigsHand:
            if type(trig) == Trig_SkyboundArt and trig.progress <= self.Game.Counters.turns[self.ID]:
                self.effectViable = True
                return
            if type(trig) == Trig_SuperSkyboundArt and trig.progress <= self.Game.Counters.turns[self.ID]:
                self.effectViable = True
                return

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        sa, ssa = False, False
        for trig in self.trigsHand:
            if type(trig) == Trig_SkyboundArt and trig.progress <= self.Game.Counters.turns[self.ID]:
                sa = True
            if type(trig) == Trig_SuperSkyboundArt and trig.progress <= self.Game.Counters.turns[self.ID]:
                ssa = True
        if ssa:
            self.dealsDamage(self.Game.heroes[3 - self.ID], 6)
        elif sa:
            self.dealsDamage(self.Game.heroes[3 - self.ID], 3)


class SwordSwingingBandit(SVMinion):
    Class, race, name = "Swordcraft", "Officer", "Sword-Swinging Bandit"
    mana, attack, health = 3, 2, 1
    index = "SV_Eternal~Swordcraft~Minion~3~2~1~Officer~Sword-Swinging Bandit~Charge~Deathrattle"
    requireTarget, keyWord, description = False, "Charge", "Storm.Last Words: Summon a Bullet Bike."
    attackAdd, healthAdd = 2, 2
    name_CN = "残刃蛮贼"

    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.deathrattles = [Deathrattle_SwordSwingingBandit(self)]


class Deathrattle_SwordSwingingBandit(Deathrattle_Minion):
    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        self.entity.Game.summon([BulletBike(self.entity.Game, self.entity.ID)], (-1, "totheRightEnd"),
                                self.entity.ID)


class GrandAuction(SVSpell):
    Class, name = "Swordcraft", "Grand Auction"
    requireTarget, mana = True, 1
    index = "SV_Eternal~Swordcraft~Spell~1~Grand Auction~Uncollectible"
    description = "Discard a card from your hand.Draw a card.Put an Ageworn Weaponry into your hand."
    name_CN = "大甩卖"

    def available(self):
        return self.Game.Hand_Deck.hands[self.ID] > 1

    def targetExists(self, choice=0):
        for card in self.Game.Hand_Deck.hands[self.ID]:
            if card.inHand and card != self:
                return True
        return False

    def targetCorrect(self, target, choice=0):
        if isinstance(target, list): target = target[0]
        return target.ID == self.ID and target.inHand and target != self

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if target:
            if isinstance(target, list): target = target[0]
            self.Game.Hand_Deck.discardCard(self.ID, target)
            self.Game.Hand_Deck.drawCard(self.ID)
            self.Game.Hand_Deck.addCardtoHand(AgewornWeaponry, self.ID, byType=True, creator=type(self))
        return target


class AgewornWeaponry(Amulet):
    Class, race, name = "Swordcraft", "", "Ageworn Weaponry"
    mana = 2
    index = "SV_Eternal~Swordcraft~Amulet~2~None~Ageworn Weaponry~Countdown~Deathrattle~Uncollectible"
    requireTarget, description = True, "If an allied Swordcraft follower is in play, and you have at least 2 play points, Choose: Play this card as a Greatshield or Greatsword.Countdown (2)At the end of your opponent's turn, summon a Knight."
    name_CN = "历战的兵器"


class Greatshield(Amulet):
    Class, race, name = "Swordcraft", "", "Greatshield"
    mana = 2
    index = "SV_Eternal~Swordcraft~Amulet~2~None~Greatshield~Countdown~Battlecry~Deathrattle~Uncollectible"
    requireTarget, description = True, "Countdown (1)Fanfare: Give an allied Swordcraft follower +0/+1.Last Words: Summon a Shield Guardian."
    name_CN = "坚韧之盾"


class Greatsword(Amulet):
    Class, race, name = "Swordcraft", "", "Greatsword"
    mana = 2
    index = "SV_Eternal~Swordcraft~Amulet~2~None~Greatsword~Countdown~Battlecry~Deathrattle~Uncollectible"
    requireTarget, description = True, "Countdown (1)Fanfare: Give an allied Swordcraft follower +1/+0.Last Words: Summon a Heavy Knight."
    name_CN = "锐利之剑"


class StoneMerchant(SVMinion):
    Class, race, name = "Swordcraft", "Officer", "Stone Merchant"
    mana, attack, health = 4, 3, 4
    index = "SV_Eternal~Swordcraft~Minion~4~3~4~Officer~Stone Merchant~Battlecry"
    requireTarget, keyWord, description = False, "", "Fanfare: Put 2 Grand Auctions into your hand."
    attackAdd, healthAdd = 2, 2
    name_CN = "奇石商贩"

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        self.Game.Hand_Deck.addCardtoHand([GrandAuction for _ in range(2)], self.ID, byType=True, creator=type(self))
        return None


class SeofonStarSwordSovereign(SVMinion):
    Class, race, name = "Swordcraft", "Commander", "Seofon, Star Sword Sovereign"
    mana, attack, health = 4, 5, 3
    index = "SV_Eternal~Swordcraft~Minion~4~5~3~Commander~Seofon, Star Sword Sovereign~Battlecry~SkyboundArt~SuperSkyboundArt~Legendary"
    requireTarget, keyWord, description = False, "", "Fanfare: Put a random card with Enhance or Super Skybound Art from your deck into your hand.Skybound Art (10): Evolve all unevolved allied Swordcraft followers. Evolve effects will not activate for them.Super Skybound Art (15): Gain the following effects.-Reduce damage to this follower to 0.-Can't be destroyed by effects."
    attackAdd, healthAdd = 2, 2
    name_CN = "天星剑王·希耶提"

    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.trigsHand = [Trig_SkyboundArt(self), Trig_SuperSkyboundArt(self)]

    def effCanTrig(self):
        for trig in self.trigsHand:
            if type(trig) == Trig_SkyboundArt and trig.progress <= self.Game.Counters.turns[self.ID]:
                self.effectViable = True
                return
            if type(trig) == Trig_SuperSkyboundArt and trig.progress <= self.Game.Counters.turns[self.ID]:
                self.effectViable = True
                return

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        curGame = self.Game
        if curGame.mode == 0:
            if curGame.guides:
                i = curGame.guides.pop(0)
            else:
                cards = [i for i, card in enumerate(curGame.Hand_Deck.decks[self.ID]) if
                         "~SuperSkyboundArt" in card.index or "~Enhance" in card.index]
                i = npchoice(cards) if cards else -1
                curGame.fixedGuides.append(i)
            if i > -1: curGame.Hand_Deck.drawCard(self.ID, i)
        sa, ssa = False, False
        for trig in self.trigsHand:
            if type(trig) == Trig_SkyboundArt and trig.progress <= self.Game.Counters.turns[self.ID]:
                sa = True
            if type(trig) == Trig_SuperSkyboundArt and trig.progress <= self.Game.Counters.turns[self.ID]:
                ssa = True
        if sa:
            for minion in self.Game.minionsonBoard(self.ID):
                if minion.Class == "Swordcraft" and minion.marks["Evolved"] < 1:
                    minion.evolve()
        if ssa:
            self.marks["Can't Break"] = 1
            trig = Trig_SeofonStarSwordSovereign(self)
            self.trigsBoard.append(trig)
            trig.connect()


class Trig_SeofonStarSwordSovereign(TrigBoard):
    def __init__(self, entity):
        self.blank_init(entity, ["BattleDmgHero", "BattleDmgMinion", "AbilityDmgHero", "AbilityDmgMinion"])

    def canTrig(self, signal, ID, subject, target, number, comment,
                choice=0):  # target here holds the actual target object
        return target == self.entity

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        number[0] = 0


class VictoriousGrappler(SVMinion):
    Class, race, name = "Swordcraft", "Commander", "Victorious Grappler"
    mana, attack, health = 5, 5, 5
    index = "SV_Eternal~Swordcraft~Minion~5~5~5~Commander~Victorious Grappler~Battlecry"
    requireTarget, keyWord, description = False, "", "Fanfare: Give all allied Officer followers the following effect - Clash: Deal 2 damage to the enemy leader.Clash: Deal 2 damage to the enemy leader."
    attackAdd, healthAdd = 2, 2
    name_CN = "武斗女兵"

    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.trigsBoard = [Trig_VictoriousGrappler(self)]

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        for minion in self.Game.minionsonBoard(self.ID):
            if "Officer" in minion.race:
                trig = Trig_VictoriousGrappler(minion)
                minion.trigsBoard.append(trig)
                trig.connect()


class Trig_VictoriousGrappler(TrigBoard):
    def __init__(self, entity):
        self.blank_init(entity, ["MinionAttackingMinion"])

    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.onBoard and (subject == self.entity or target == self.entity)

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        self.entity.dealsDamage(self.entity.Game.heroes[3 - self.entity.ID], 2)


class AverageAxeman(SVMinion):
    Class, race, name = "Swordcraft", "Officer", "Average Axeman"
    mana, attack, health = 7, 2, 7
    index = "SV_Eternal~Swordcraft~Minion~7~2~7~Officer~Average Axeman~Charge~Bane"
    requireTarget, keyWord, description = False, "Charge,Bane", "Storm.Bane.Strike: Recover X play points. X equals this follower's attack."
    attackAdd, healthAdd = 2, 2
    name_CN = "锐斧战士"

    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.trigsBoard = [Trig_AverageAxeman(self)]


class Trig_AverageAxeman(TrigBoard):
    def __init__(self, entity):
        self.blank_init(entity, ["MinionAttackingMinion", "MinionAttackingHero"])

    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.onBoard and subject.ID == self.entity.ID and subject == self.entity

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        self.entity.Game.Manas.restoreManaCrystal(self.entity.attack, self.entity.ID)


class RampagingRhino(SVMinion):
    Class, race, name = "Swordcraft", "Officer", "Rampaging Rhino"
    mana, attack, health = 8, 8, 4
    index = "SV_Eternal~Swordcraft~Minion~8~8~4~Officer~Rampaging Rhino~Rush~Battlecry"
    requireTarget, keyWord, description = False, "Rush", "Rush.Fanfare: Destroy a random enemy follower or amulet."
    attackAdd, healthAdd = 2, 2
    name_CN = "蛮冲铁犀"

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        curGame = self.Game
        if curGame.mode == 0:
            minion = None
            if curGame.guides:
                i, where = curGame.guides.pop(0)
                if where: minion = curGame.find(i, where)
            else:
                minions = curGame.minionsAlive(3 - self.ID) + curGame.amuletonBoard(3 - self.ID)
                if len(minions) > 0:
                    minion = npchoice(minions)
                    curGame.fixedGuides.append((minion.pos, "Minion%d" % minion.ID))
                else:
                    curGame.fixedGuides.append((0, ""))
            if minion: curGame.killMinion(self, minion)
        return None


class EahtaGodoftheBlade(SVMinion):
    Class, race, name = "Swordcraft", "Officer", "Eahta, God of the Blade"
    mana, attack, health = 8, 7, 6
    index = "SV_Eternal~Swordcraft~Minion~8~7~6~Officer~Eahta, God of the Blade~Rush~Battlecry~SkyboundArt~SuperSkyboundArt~Legendary"
    requireTarget, keyWord, description = False, "Rush", "Rush.Fanfare: Skybound Art (10) - Subtract 5 from the cost of all Swordcraft followers in your hand.Super Skybound Art (15): Subtract 5 from the cost of all Swordcraft followers in your deck.During your turn, when this follower attacks and destroys an enemy follower, if this follower is not destroyed, evolve it."
    attackAdd, healthAdd = 2, 2
    name_CN = "刀神·奥库托"

    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.trigsHand = [Trig_SkyboundArt(self), Trig_SuperSkyboundArt(self), Trig_EahtaGodoftheBlade(self)]

    def effCanTrig(self):
        for trig in self.trigsHand:
            if type(trig) == Trig_SkyboundArt and trig.progress <= self.Game.Counters.turns[self.ID]:
                self.effectViable = True
                return
            if type(trig) == Trig_SuperSkyboundArt and trig.progress <= self.Game.Counters.turns[self.ID]:
                self.effectViable = True
                return

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        sa, ssa = False, False
        for trig in self.trigsHand:
            if type(trig) == Trig_SkyboundArt and trig.progress <= self.Game.Counters.turns[self.ID]:
                sa = True
            if type(trig) == Trig_SuperSkyboundArt and trig.progress <= self.Game.Counters.turns[self.ID]:
                ssa = True
        if sa:
            for card in self.Game.Hand_Deck.hands[self.ID][:]:
                if card.type == "Minion" and card.Class == "Swordcraft":
                    ManaMod(card, changeby=-5, changeto=-1).applies()
        if ssa:
            for card in self.Game.Hand_Deck.decks[self.ID][:]:
                if card.type == "Spell" and card.Class == "Swordcraft":
                    ManaMod(card, changeby=-5, changeto=-1).applies()

    def inEvolving(self):
        self.getsKeyword("Windfury")
        for trig in self.trigsBoard:
            if type(trig) == Trig_EahtaGodoftheBlade:
                self.trigsBoard.remove(trig)
                trig.disconnect()
                break


class Trig_EahtaGodoftheBlade(TrigBoard):
    def __init__(self, entity):
        self.blank_init(entity, ["MinionAttackedMinion"])

    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
        return ID == self.entity.ID and self.entity.onBoard and subject == self.entity and self.entity.health > 0 \
               and self.entity.dead == False and (target.health < 1 or target.dead == True)

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        self.entity.evolve()


"""Runecraft cards"""


class AlistairTinyMagus(SVMinion):
    Class, race, name = "Runecraft", "", "Alistair, Tiny Magus"
    mana, attack, health = 1, 0, 1
    index = "SV_Eternal~Runecraft~Minion~1~0~1~None~Alistair, Tiny Magus~Battlecry~Deathrattle"
    requireTarget, keyWord, description = True, "", "Fanfare: Deal X damage to an enemy follower. X equals the last digit of your leader's defense.Last Words: Spellboost the cards in your hand."
    attackAdd, healthAdd = 2, 2
    name_CN = "小小的术士·阿里斯特拉"

    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.deathrattles = [Deathrattle_AlistairTinyMagus(self)]

    def targetExists(self, choice=0):
        return self.selectableEnemyMinionExists()

    def targetCorrect(self, target, choice=0):
        if isinstance(target, list): target = target[0]
        return target.type == "Minion" and target.ID != self.ID and target.onBoard

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if target:
            if isinstance(target, list): target = target[0]
            self.dealsDamage(target, self.Game.heroes[self.ID] % 10)
        return target


class Deathrattle_AlistairTinyMagus(Deathrattle_Minion):
    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        self.entity.Game.sendSignal("Spellboost", self.entity.ID, self, None, 0, "", choice)


class ImpalementArts(SVSpell):
    Class, name = "Runecraft", "Impalement Arts"
    requireTarget, mana = True, 1
    index = "SV_Eternal~Runecraft~Spell~1~Impalement Arts~Spellboost"
    description = "Deal 1 damage to an enemy.If this card has been Spellboosted at least 5 times, put an Impalement Arts into your hand and give it the following effect: At the end of your turn, discard this card."
    name_CN = "戏刀奇术"

    def __init__(self, Game, ID):
        super().__init__(Game, ID)
        self.blank_init(Game, ID)
        self.trigsHand = [Trig_Spellboost(self)]
        self.progress = 0

    def available(self):
        return self.selectableEnemyExists()

    def targetCorrect(self, target, choice=0):
        if isinstance(target, list): target = target[0]
        return (target.type == "Minion" or target.type == "Hero") and target.ID != self.ID and target.onBoard

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if target:
            if isinstance(target, list): target = target[0]
            damage = (1 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
            self.dealsDamage(target, damage)
            if self.progress >= 5:
                card = ImpalementArts(self.Game, self.ID)
                self.Game.Hand_Deck.addCardtoHand(card, self.ID, byType=False, creator=type(self))
                trig = Trig_ImpalementArts(card)
                card.trigsHand.append(trig)
                trig.connect()
        return target


class Trig_ImpalementArts(TrigHand):
    def __init__(self, entity):
        self.blank_init(entity, ["TurnEnds"])

    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.onBoard and ID == self.entity.ID

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        self.entity.Game.Hand_Deck.discardCard(self.entity.ID, self.entity)


class ElmottPyrestarter(SVMinion):
    Class, race, name = "Runecraft", "", "Elmott, Pyrestarter"
    mana, attack, health = 2, 3, 1
    index = "SV_Eternal~Runecraft~Minion~2~3~1~None~Elmott, Pyrestarter~Battlecry~Spellboost"
    requireTarget, keyWord, description = True, "", "Fanfare: Deal X damage to an enemy follower. X equals the number of times this card has been Spellboosted. Then, if X is at least 10, deal 4 damage to the enemy leader."
    attackAdd, healthAdd = 2, 2
    name_CN = "炎狱的葬送者·艾尔莫特"

    def __init__(self, Game, ID):
        super().__init__(Game, ID)
        self.blank_init(Game, ID)
        self.trigsHand = [Trig_Spellboost(self)]
        self.progress = 0

    def targetExists(self, choice=0):
        return self.selectableEnemyMinionExists()

    def targetCorrect(self, target, choice=0):
        if isinstance(target, list): target = target[0]
        return target.type == "Minion" and target.ID != self.ID and target.onBoard

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if target:
            if isinstance(target, list): target = target[0]
            self.dealsDamage(target, self.progress)
            if self.progress >= 10:
                self.dealsDamage(self.Game.heroes[3 - self.ID], 4)
        return target


class ElixirMixer(SVSpell):
    Class, name = "Runecraft", "Elixir Mixer"
    requireTarget, mana = True, 2
    index = "SV_Eternal~Runecraft~Spell~2~Elixir Mixer"
    description = "Give Rush, Bane, and Drain to an allied follower whose attack or defense has been increased by an effect."
    name_CN = "灵药调和"

    def available(self):
        for minion in self.Game.minionsonBoard(self.ID):
            if minion.attack > minion.attack_0 or minion.health > minion.health_0:
                return True
        return False

    def targetCorrect(self, target, choice=0):
        if isinstance(target, list): target = target[0]
        return target.type == "Minion" and target.ID == self.ID and target.onBoard and \
               (target.attack > target.attack_0 or target.health > target.health_0)

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if target:
            if isinstance(target, list): target = target[0]
            target.getsKeyword("Rush")
            target.getsKeyword("Bane")
            target.getsKeyword("Drain")


class ForceBarrier(SVSpell):
    Class, name = "Runecraft", "Force Barrier"
    requireTarget, mana = False, 2
    index = "SV_Eternal~Runecraft~Spell~2~Force Barrier"
    description = "Until the end of your opponent's turn, give all allies the following effect: Reduce damage from effects by 2."
    name_CN = "魔御结界"

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        targets = self.Game.minionsonBoard(self.ID)
        targets.append(self.Game.heroes[self.ID])
        for t in targets:
            trig = Trig_ForceBarrier(t)
            t.trigsBoard.append(trig)
            trig.connect()


class Trig_ForceBarrier(TrigBoard):
    def __init__(self, entity):
        self.blank_init(entity, ["AbilityDmgHero", "AbilityDmgMinion", "TurnEnds"])

    def canTrig(self, signal, ID, subject, target, number, comment,
                choice=0):  # target here holds the actual target object
        return signal[0] == 'T' and ID != self.entity.ID or target == self.entity

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        if signal[0] == 'T':
            try:
                self.entity.trigsBoard.remove(self)
            except:
                pass
            self.disconnect()
        else:
            number[0] -= 2


class AcademicArchmage(SVMinion):
    Class, race, name = "Runecraft", "", "Academic Archmage"
    mana, attack, health = 3, 2, 3
    index = "SV_Eternal~Runecraft~Minion~3~2~3~None~Academic Archmage~Battlecry"
    requireTarget, keyWord, description = True, "", "Fanfare: Deal 1 damage to an enemy follower and then 1 damage to the enemy leader. If you have 20 cards or less in your deck, deal 3 damage instead."
    attackAdd, healthAdd = 2, 2
    name_CN = "博学的魔导士"

    def targetExists(self, choice=0):
        return self.selectableEnemyMinionExists()

    def targetCorrect(self, target, choice=0):
        if isinstance(target, list): target = target[0]
        return target.type == "Minion" and target.ID != self.ID and target.onBoard

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        damage = 1
        if len(self.Game.Hand_Deck.hands[self.ID]) <= 20:
            damage = 3
        if target:
            if isinstance(target, list): target = target[0]
            self.dealsDamage(target, damage)
        self.dealsDamage(self.Game.heroes[3 - self.ID], damage)
        return target


class FifProdigiousSorcerer(SVMinion):
    Class, race, name = "Runecraft", "", "Fif, Prodigious Sorcerer"
    mana, attack, health = 3, 2, 3
    index = "SV_Eternal~Runecraft~Minion~3~2~3~None~Fif, Prodigious Sorcerer~Battlecry~SkyboundArt~SuperSkyboundArt~Legendary"
    requireTarget, keyWord, description = True, "", "Fanfare: Give another allied follower the following effect - Last Words: Summon a copy of this follower. Skybound Art (10): Summon copies of 2 random allied followers with different names destroyed this match that cost at least 5 play points. Super Skybound Art (15): Give +5/+5 to all allied followers. Restore 5 defense to your leader."
    attackAdd, healthAdd = 2, 2
    name_CN = "魔道之子·芬芙"

    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.trigsHand = [Trig_SkyboundArt(self), Trig_SuperSkyboundArt(self)]

    def effCanTrig(self):
        for trig in self.trigsHand:
            if type(trig) == Trig_SkyboundArt and trig.progress <= self.Game.Counters.turns[self.ID]:
                self.effectViable = True
                return
            if type(trig) == Trig_SuperSkyboundArt and trig.progress <= self.Game.Counters.turns[self.ID]:
                self.effectViable = True
                return

    def returnTrue(self, choice=0):
        return self.targetExists(choice) and not self.targets

    def targetExists(self, choice=0):
        return self.selectableFriendlyMinionExists()

    def targetCorrect(self, target, choice=0):
        if isinstance(target, list): target = target[0]
        return target.type == "Minion" and target.ID == self.ID and target.onBoard and target != self

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if target:
            if isinstance(target, list): target = target[0]
            if target.onBoard or target.inHand:
                trig = ResummonMinion(target)
                target.deathrattles.append(trig)
                if target.onBoard: trig.connect()
        sa, ssa = False, False
        for trig in self.trigsHand:
            if type(trig) == Trig_SkyboundArt and trig.progress <= self.Game.Counters.turns[self.ID]:
                sa = True
            if type(trig) == Trig_SuperSkyboundArt and trig.progress <= self.Game.Counters.turns[self.ID]:
                ssa = True
        if sa:
            curGame = self.Game
            if curGame.mode == 0:
                if curGame.guides:
                    minions = curGame.guides.pop(0)
                else:
                    minionsDied = curGame.Counters.minionsDiedThisGame[self.ID]
                    ms = []
                    for index in minionsDied:
                        if curGame.cardPool[index].mana >= 5:
                            ms.append(index)
                    indices = []
                    if ms:
                        mc = npchoice(ms)
                        indices.append(mc)
                        for m in ms:
                            if m == mc:
                                ms.remove(m)
                        if ms:
                            indices.append(npchoice(ms))
                    minions = tuple([curGame.cardPool[index] for index in indices])
                    curGame.fixedGuides.append(minions)
                if minions: curGame.summon([minion(curGame, self.ID) for minion in minions], (-1, "totheRightEnd"),
                                           self.ID)
        if ssa:
            for minion in self.Game.minionsonBoard(self.ID):
                minion.buffDebuff(5, 5)
            heal = 5 * (2 ** self.countHealDouble())
            self.restoresHealth(self.Game.heroes[self.ID], heal)


class ResummonMinion(Deathrattle_Minion):
    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        newMinion = type(self.entity)(self.entity.Game, self.entity.ID)
        self.entity.Game.summon(newMinion, self.entity.pos + 1, self.entity.ID)


class CrystalWitch(SVMinion):
    Class, race, name = "Runecraft", "", "Crystal Witch"
    mana, attack, health = 5, 2, 3
    index = "SV_Eternal~Runecraft~Minion~5~2~3~None~Crystal Witch~Battlecry~Spellboost"
    requireTarget, keyWord, description = False, "", "Spellboost: Subtract 1 from the cost of this card.Fanfare: Draw a card. Spellboost the cards in your hand."
    attackAdd, healthAdd = 2, 2
    name_CN = "石英魔女"

    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.trigsHand = [Trig_Spellboost(self)]
        self.progress = 0

    def selfManaChange(self):
        if self.inHand:
            self.mana = max(self.mana - self.progress, 0)

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        self.Game.Hand_Deck.drawCard(self.ID)
        self.Game.sendSignal("Spellboost", self.ID, self, None, 0, "", choice)


class XenoIfrit_Crystallize(Amulet):
    Class, race, name = "Runecraft", "", "Crystallize: Xeno Ifrit"
    mana = 3
    index = "SV_Eternal~Runecraft~Amulet~3~None~Xeno Ifrit~Countdown~Crystallize~Deathrattle~Legendary~Uncollectible"
    requireTarget, description = False, "Countdown (5)Once on each of your turns, when you play a follower, give it +1/+0.At the start of your turn, if you have more evolution points than your opponent, subtract 1 from this amulet's Countdown. (You have 0 evolution points on turns you are unable to evolve.)Last Words: Summon a Xeno Ifrit."
    name_CN = "结晶：异种·伊芙利特"

    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.counter = 5
        self.trigsBoard = [Trig_Countdown(self), Trig_Start_XenoIfrit_Crystallize(self),
                           Trig_XenoIfrit_Crystallize(self)]
        self.deathrattles = [Deathrattle_XenoIfrit_Crystallize(self)]


class Trig_Start_XenoIfrit_Crystallize(TrigBoard):
    def __init__(self, entity):
        self.blank_init(entity, ["TurnStarts"])

    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.onBoard and ID == self.entity.ID

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        if self.entity.Game.getEvolutionPoint(self.entity.ID) > self.entity.Game.getEvolutionPoint(3 - self.entity.ID):
            self.entity.countdown(self.entity, 1)


class Trig_XenoIfrit_Crystallize(TrigBoard):
    def __init__(self, entity):
        self.blank_init(entity, ["MinionSummoned"])

    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.onBoard and subject.ID == self.entity.ID and subject != self.entity

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        for t in self.entity.trigsBoard:
            if type(t) == Trig_XenoIfrit_Crystallize:
                t.disconnect()
                self.entity.trigsBoard.remove(t)
                break
        trigger = Trig_End_XenoIfrit_Crystallize(self.entity)
        self.entity.trigsBoard.append(trigger)
        trigger.connect()
        subject.buffDebuff(1, 0)


class Trig_End_XenoIfrit_Crystallize(TrigBoard):
    def __init__(self, entity):
        self.blank_init(entity, ["TurnEnds"])

    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.onBoard and ID == self.entity.ID

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        for t in self.entity.trigsBoard:
            if type(t) == Trig_End_XenoIfrit_Crystallize:
                t.disconnect()
                self.entity.trigsBoard.remove(t)
                break
        trigger = Trig_XenoIfrit_Crystallize(self.entity)
        self.entity.trigsBoard.append(trigger)
        trigger.connect()


class Deathrattle_XenoIfrit_Crystallize(Deathrattle_Minion):
    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        self.entity.Game.summon([XenoIfrit(self.entity.Game, self.entity.ID)], (-1, "totheRightEnd"),
                                self.entity.ID)


class XenoIfrit(SVMinion):
    Class, race, name = "Runecraft", "", "Xeno Ifrit"
    mana, attack, health = 6, 5, 4
    index = "SV_Eternal~Runecraft~Minion~6~5~4~None~Xeno Ifrit~Crystallize~Legendary"
    requireTarget, keyWord, description = False, "", "Crystallize (3): Countdown (5)Once on each of your turns, when you play a follower, give it +1/+0.At the start of your turn, if you have more evolution points than your opponent, subtract 1 from this amulet's Countdown. (You have 0 evolution points on turns you are unable to evolve.)Last Words: Summon a Xeno Ifrit.When this follower comes into play, deal 3 damage to all enemies."
    crystallizeAmulet = XenoIfrit_Crystallize
    attackAdd, healthAdd = 2, 2
    name_CN = "异种·伊芙利特"

    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.appearResponse = [self.whenAppears]

    def whenAppears(self):
        targets = self.Game.minionsonBoard(3 - self.ID)
        targets.append(self.Game.heroes[3 - self.ID])
        self.dealsAOE(targets, [3 for _ in targets])

    def getMana(self):
        if self.Game.Manas.manas[self.ID] < self.mana:
            return 3
        else:
            return self.mana

    def willCrystallize(self):
        curMana = self.Game.Manas.manas[self.ID]
        return self.mana > curMana >= 3

    def effCanTrig(self):
        if self.willCrystallize() and self.targetExists():
            self.effectViable = "sky blue"
        else:
            self.effectViable = False


class PholiaRetiredSovereign(SVMinion):
    Class, race, name = "Runecraft", "", "Pholia, Retired Sovereign"
    mana, attack, health = 7, 4, 4
    index = "SV_Eternal~Runecraft~Minion~7~4~4~None~Pholia, Retired Sovereign~Battlecry"
    requireTarget, keyWord, description = False, "", "Fanfare: The next time this follower takes damage, reduce that damage to 0. Summon a Bai Ze."
    attackAdd, healthAdd = 2, 2
    name_CN = "悠闲隐居的前国王·芙莉亚"

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        self.marks["Next Damage 0"] = 1
        self.Game.summon([BaiZe(self.Game, self.ID)], (-1, "totheRightEnd"), self.ID)

    def inHandEvolving(self, target=None):
        for minion in self.Game.minionsonBoard():
            if type(minion) == BaiZe and minion.status["Evolved"] == 0:
                minion.evolve()
                trig = Trig_PholiaRetiredSovereign(minion)
                minion.trigsBoard.append(trig)
                trig.connect()


class Trig_PholiaRetiredSovereign(TrigBoard):
    def __init__(self, entity):
        self.blank_init(entity, ["TurnEnds"])

    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.onBoard and ID == self.entity.ID

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        heal = 2 * (2 ** self.entity.countHealDouble())
        self.entity.restoresHealth(self.entity.Game.heroes[self.entity.ID], heal)
        self.entity.restoresHealth(self.entity, heal)


class BaiZe(SVMinion):
    Class, race, name = "Runecraft", "", "Bai Ze"
    mana, attack, health = 7, 4, 6
    index = "SV_Eternal~Runecraft~Minion~7~4~6~None~Bai Ze~Rush~Taunt~Uncollectible"
    requireTarget, keyWord, description = False, "Rush,Taunt", "Rush.Ward.At the end of your turn, give all allied Pholia, Retired Sovereigns the following effect: The next time this follower takes damage, reduce that damage to 0."
    attackAdd, healthAdd = 2, 2
    name_CN = "白泽"

    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.trigsBoard = [Trig_BaiZe(self)]


class Trig_BaiZe(TrigBoard):
    def __init__(self, entity):
        self.blank_init(entity, ["TurnEnds"])

    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.onBoard and ID == self.entity.ID

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        for minion in self.entity.Game.minionsonBoard():
            if type(minion) == PholiaRetiredSovereign:
                minion.marks["Next Damage 0"] = 1


class RagingGolem_Crystallize(Amulet):
    Class, race, name = "Runecraft", "", "Crystallize: Raging Golem"
    mana = 2
    index = "SV_Eternal~Runecraft~Amulet~2~Earth Sigil~Raging Golem~Crystallize~Deathrattle~Uncollectible"
    requireTarget, description = False, "Earth Sigil Last Words: Summon a Guardian Golem."
    name_CN = "结晶：暴烈巨像"

    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.deathrattles = [Deathrattle_RagingGolem_Crystallize(self)]


class Deathrattle_RagingGolem_Crystallize(Deathrattle_Minion):
    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        self.entity.Game.summon([GuardianGolem(self.entity.Game, self.entity.ID)], (-1, "totheRightEnd"),
                                self.entity.ID)


class RagingGolem(SVMinion):
    Class, race, name = "Runecraft", "", "Raging Golem"
    mana, attack, health = 8, 6, 6
    index = "SV_Eternal~Runecraft~Minion~8~6~6~None~Raging Golem~Rush~Crystallize~Deathrattle"
    requireTarget, keyWord, description = False, "Rush", "Crystallize (2): Earth SigilLast Words: Summon a Guardian Golem.Rush.Last Words: Summon 2 Guardian Golems."
    crystallizeAmulet = RagingGolem_Crystallize
    attackAdd, healthAdd = 2, 2
    name_CN = "暴烈巨像"

    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.deathrattles = [Deathrattle_RagingGolem(self)]


class Deathrattle_RagingGolem(Deathrattle_Minion):
    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        self.entity.Game.summon([GuardianGolem(self.entity.Game, self.entity.ID) for _ in range(2)],
                                (-1, "totheRightEnd"),
                                self.entity.ID)


"""Dragoncraft cards"""


class DragonRearing(SVSpell):
    Class, name = "Dragoncraft", "Dragon Rearing"
    requireTarget, mana = True, 1
    index = "SV_Eternal~Dragoncraft~Spell~1~Dragon Rearing"
    description = "Give +1/+1 to an allied Dragoncraft follower.If Overflow is active for you, give +2/+2 instead and draw a card."
    name_CN = "龙之养成"

    def effCanTrig(self):
        self.effectViable = self.Game.isOverflow(self.ID)

    def available(self):
        for minion in self.Game.minionsonBoard(self.ID):
            if minion.Class == "Dragoncraft" and self.canSelect(minion):
                return True
        return False

    def targetCorrect(self, target, choice=0):
        if isinstance(target, list): target = target[0]
        return target.type == "Minion" and target.ID == self.ID and target.onBoard and target.Class == "Dragoncraft"

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if target:
            if isinstance(target, list): target = target[0]
            if self.Game.isOverflow(self.ID):
                target.buffDebuff(2, 2)
                self.Game.Hand_Deck.drawCard(self.ID)
            else:
                target.buffDebuff(1, 1)
        return target


class SharkWarrior(SVMinion):
    Class, race, name = "Dragoncraft", "", "Shark Warrior"
    mana, attack, health = 2, 2, 2
    index = "SV_Eternal~Dragoncraft~Minion~2~2~2~None~Shark Warrior~Battlecry~Enhance"
    requireTarget, keyWord, description = True, "", "Fanfare: Discard a card. Restore 4 defense to your leader.Enhance (5): Gain +2/+2. Draw a card."
    attackAdd, healthAdd = 2, 2
    name_CN = "鲨鱼战士"

    def targetExists(self, choice=0):
        return len(self.Game.Hand_Deck.hands[self.ID]) > 1

    def targetCorrect(self, target, choice=0):
        if isinstance(target, list): target = target[0]
        return target.ID == self.ID and target.inHand and target != self

    def getMana(self):
        if self.Game.Manas.manas[self.ID] >= 5:
            return 5
        else:
            return self.mana

    def willEnhance(self):
        return self.Game.Manas.manas[self.ID] >= 5

    def effCanTrig(self):
        self.effectViable = self.willEnhance()

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if target:
            if isinstance(target, list): target = target[0]
            self.Game.Hand_Deck.discardCard(self.ID, target)
            heal = 4 * (2 ** self.countHealDouble())
            self.restoresHealth(self.Game.heroes[self.ID], heal)
        if comment == 5:
            self.buffDebuff(2, 2)
            self.Game.Hand_Deck.drawCard(self.ID)
        return target


class MermaidArcher(SVMinion):
    Class, race, name = "Dragoncraft", "", "Mermaid Archer"
    mana, attack, health = 2, 0, 5
    index = "SV_Eternal~Dragoncraft~Minion~2~0~5~None~Mermaid Archer~Battlecry~Enhance"
    requireTarget, keyWord, description = False, "", "Once each turn, when this follower takes damage, if it's not destroyed, deal 2 damage to a random enemy follower."
    attackAdd, healthAdd = 2, 2
    name_CN = "人鱼弓手"

    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.trigsBoard = [Trig_MermaidArcher(self)]


class Trig_MermaidArcher(TrigBoard):
    def __init__(self, entity):
        self.blank_init(entity, ["MinionTakesDmg"])

    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
        return target == self.entity and self.entity.onBoard and self.entity.health > 0 and not self.entity.dead

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


class HypersonicDragonewt(SVMinion):
    Class, race, name = "Dragoncraft", "", "Hypersonic Dragonewt"
    mana, attack, health = 4, 3, 2
    index = "SV_Eternal~Dragoncraft~Minion~4~3~2~None~Hypersonic Dragonewt~Charge~Battlecry"
    requireTarget, keyWord, description = False, "Charge", "Storm. Fanfare: If Overflow is active for you, gain Last Words - Summon a Hypersonic Dragonewt."
    attackAdd, healthAdd = 2, 2
    name_CN = "残影龙人"

    def effCanTrig(self):
        self.effectViable = self.Game.isOverflow(self.ID)

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if self.Game.isOverflow(self.ID):
            trig = Deathrattle_HypersonicDragonewt(self)
            self.deathrattles.append(trig)
            trig.connect()


class Deathrattle_HypersonicDragonewt(Deathrattle_Minion):
    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        self.entity.Game.summon([HypersonicDragonewt(self.entity.Game, self.entity.ID)], (-1, "totheRightEnd"),
                                self.entity.ID)


class GiantBasilisk(SVMinion):
    Class, race, name = "Dragoncraft", "", "Hypersonic Dragonewt"
    mana, attack, health = 4, 4, 4
    index = "SV_Eternal~Dragoncraft~Minion~4~4~4~None~Hypersonic Dragonewt~Bane~Battlecry"
    requireTarget, keyWord, description = False, "Bane", "Bane. Fanfare: If you discarded any cards this turn, evolve this card."
    attackAdd, healthAdd = 2, 2
    name_CN = "巨型巴西利斯克"

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if len(self.Game.Counters.cardsDiscardedThisTurn[self.ID]) > 0:
            self.evolve()


class RaziaVengefulCannonlancer(SVMinion):
    Class, race, name = "Dragoncraft", "", "Razia, Vengeful Cannonlancer"
    mana, attack, health = 4, 2, 4
    index = "SV_Eternal~Dragoncraft~Minion~4~2~4~None~Razia, Vengeful Cannonlancer~Taunt~Deathrattle"
    requireTarget, keyWord, description = False, "Taunt", "Ward.Clash: Gain +1/+0.Last Words: Deal X damage to the enemy leader. X equals this follower's attack."
    attackAdd, healthAdd = 2, 2
    name_CN = "破天的铳枪骑士·拉斯缇娜"

    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.trigsBoard = [Trig_RaziaVengefulCannonlancer(self)]
        self.deathrattles = [Deathrattle_RaziaVengefulCannonlancer(self)]


class Deathrattle_RaziaVengefulCannonlancer(Deathrattle_Minion):
    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        self.entity.dealsDamage(self.entity.Game.heroes[3 - self.entity.ID], self.entity.attack)


class Trig_RaziaVengefulCannonlancer(TrigBoard):
    def __init__(self, entity):
        self.blank_init(entity, ["MinionAttackingMinion"])

    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.onBoard and (subject == self.entity or target == self.entity)

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        self.entity.buffDebuff(1, 0)


class ThreoDivineHavoc(SVMinion):
    Class, race, name = "Dragoncraft", "", "Threo, Divine Havoc"
    mana, attack, health = 4, 4, 3
    index = "SV_Eternal~Dragoncraft~Minion~4~4~3~None~Threo, Divine Havoc~Rush~Battlecry~SkyboundArt~SuperSkyboundArt~Legendary"
    requireTarget, keyWord, description = False, "Rush", "Rush.Fanfare: If Overflow is active for you, gain the following effect until the end of your opponent's turn - Whenever this follower takes damage equal to or greater than its defense, survive on 1 defense.Skybound Art (10): Deal 2 damage to all enemies.Super Skybound Art (15): Gain the ability to attack 3 times per turn."
    attackAdd, healthAdd = 2, 2
    name_CN = "怪力乱神·萨拉萨"

    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.trigsHand = [Trig_SkyboundArt(self), Trig_SuperSkyboundArt(self)]

    def effCanTrig(self):
        for trig in self.trigsHand:
            if type(trig) == Trig_SkyboundArt and trig.progress <= self.Game.Counters.turns[self.ID]:
                self.effectViable = True
                return
            if type(trig) == Trig_SuperSkyboundArt and trig.progress <= self.Game.Counters.turns[self.ID]:
                self.effectViable = True
                return

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if self.Game.isOverflow(self.ID):
            trig = Trig_ThreoDivineHavoc(self)
            self.trigsBoard.append(trig)
            trig.connect()
        sa, ssa = False, False
        for trig in self.trigsHand:
            if type(trig) == Trig_SkyboundArt and trig.progress <= self.Game.Counters.turns[self.ID]:
                sa = True
            if type(trig) == Trig_SuperSkyboundArt and trig.progress <= self.Game.Counters.turns[self.ID]:
                ssa = True
        if sa:
            targets = self.Game.minionsonBoard(3 - self.ID)
            targets.append(self.Game.heroes[3 - self.ID])
            self.dealsAOE(targets, [2 for _ in targets])
        if ssa:
            self.marks["Can Attack 3 times"] = 1


class Trig_ThreoDivineHavoc(TrigBoard):
    def __init__(self, entity):
        self.blank_init(entity, ["BattleDmgHero", "BattleDmgMinion", "AbilityDmgHero", "AbilityDmgMinion"])

    def canTrig(self, signal, ID, subject, target, number, comment,
                choice=0):  # target here holds the actual target object
        return target == self.entity and number[0] >= self.entity.health

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        number[0] = self.entity.health - 1


class TempestDragon(SVMinion):
    Class, race, name = "Dragoncraft", "", "Tempest Dragon"
    mana, attack, health = 5, 5, 5
    index = "SV_Eternal~Dragoncraft~Minion~5~5~5~None~Tempest Dragon"
    requireTarget, keyWord, description = False, "", "At the end of your turn, put a random Dragoncraft follower that originally costs 2, 4, 6, 8, or 10 play points from your deck into your hand."
    attackAdd, healthAdd = 2, 2
    name_CN = "风霆之龙"

    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.trigsBoard = [Trig_TempestDragon(self)]

    def inHandEvolving(self, target=None):
        for card in self.Game.Hand_Deck.decks[self.ID]:
            if card.type == "Minion" and type(card).mana in [2, 4, 6, 8, 10] and card.Class == "Dragoncraft":
                card.buffDebuff(2, 2)


class Trig_TempestDragon(TrigBoard):
    def __init__(self, entity):
        self.blank_init(entity, ["TurnEnds"])

    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.onBoard and ID == self.entity.ID

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        curGame = self.entity.Game
        if curGame.mode == 0:
            if curGame.guides:
                i = curGame.guides.pop(0)
            else:
                minions = [i for i, card in enumerate(curGame.Hand_Deck.decks[self.entity.ID]) if
                           card.type == "Minion" and
                           type(card).mana in [2, 4, 6, 8, 10] and card.Class == "Dragoncraft"]
                i = npchoice(minions) if minions else -1
                curGame.fixedGuides.append(i)
            if i > -1: curGame.Hand_Deck.drawCard(self.entity.ID, i)
        return None


class LadivaChampionofLove(SVMinion):
    Class, race, name = "Dragoncraft", "", "Ladiva, Champion of Love"
    mana, attack, health = 6, 4, 6
    index = "SV_Eternal~Dragoncraft~Minion~6~4~6~None~Ladiva, Champion of Love~Battlecry"
    requireTarget, keyWord, description = False, "", "Fanfare: If any enemy followers are in play, lose 1 play point orb and evolve this follower.Clash: Give -2/-0 to the enemy follower."
    attackAdd, healthAdd = 2, 2
    name_CN = "爱之大殿堂·法斯蒂瓦"

    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.trigsBoard = [Trig_LadivaChampionofLove(self)]

    def effCanTrig(self):
        self.effectViable = len(self.Game.minionsonBoard(3 - self.ID)) > 0

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if len(self.Game.minionsonBoard(3 - self.ID)) > 0:
            self.Game.Manas.destroyManaCrystal(1, self.ID)
            self.evolve()


class Trig_LadivaChampionofLove(TrigBoard):
    def __init__(self, entity):
        self.blank_init(entity, ["MinionAttackingMinion"])

    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.onBoard and (subject == self.entity or target == self.entity)

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        if subject == self.entity:
            target.buffDebuff(-2, 0)
        else:
            subject.buffDebuff(-2, 0)


class GhandagozaFistofRage(SVMinion):
    Class, race, name = "Dragoncraft", "", "Ghandagoza, Fist of Rage"
    mana, attack, health = 9, 8, 7
    index = "SV_Eternal~Dragoncraft~Minion~9~8~7~None~Ghandagoza, Fist of Rage~Rush"
    requireTarget, keyWord, description = False, "Rush", "Rush.Strike: Deal X damage to the enemy leader. X equals this follower's attack."
    attackAdd, healthAdd = 2, 2
    name_CN = "古今独步的大拳豪·冈达葛萨"

    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.trigsBoard = [Trig_GhandagozaFistofRage(self)]


class Trig_GhandagozaFistofRage(TrigBoard):
    def __init__(self, entity):
        self.blank_init(entity, ["MinionAttackingMinion", "MinionAttackingHero"])

    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.onBoard and subject.ID == self.entity.ID and subject == self.entity

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        self.entity.dealsDamage(self.entity.Game.heroes[3 - self.entity.ID], self.entity.attack)


class DisrestanOceanHarbinger_Accelerate(SVSpell):
    Class, name = "Dragoncraft", "Disrestan, Ocean Harbinger"
    requireTarget, mana = False, 1
    index = "SV_Eternal~Dragoncraft~Spell~1~Disrestan, Ocean Harbinger~Accelerate~Legendary~Uncollectible"
    description = " Draw a card. If you have more evolution points than your opponent, summon a Megalorca. (You have 0 evolution points on turns you are unable to evolve.)"
    name_CN = "神鱼·迪斯雷斯坦"

    def effCanTrig(self):
        self.effectViable = self.Game.getEvolutionPoint(self.ID) > self.Game.getEvolutionPoint(3 - self.ID)

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        self.Game.Hand_Deck.drawCard(self.ID)
        if self.Game.getEvolutionPoint(self.ID) > self.Game.getEvolutionPoint(3 - self.ID):
            self.Game.summon([Megalorca(self.Game, self.ID)], (-1, "totheRightEnd"), self.ID)
        return None


class DisrestanOceanHarbinger(SVMinion):
    Class, race, name = "Dragoncraft", "", "Disrestan, Ocean Harbinger"
    mana, attack, health = 17, 13, 13
    index = "SV_Eternal~Dragoncraft~Minion~17~13~13~None~Disrestan, Ocean Harbinger~Battlecry~Legendary"
    requireTarget, keyWord, description = False, "", "At the end of your turn, if you have 10 play point orbs, subtract 10 from the cost of this card.Accelerate (1): Draw a card. If you have more evolution points than your opponent, summon a Megalorca. (You have 0 evolution points on turns you are unable to evolve.)Fanfare: Give -X/-X to all enemy followers. X equals your remaining play points. (Followers are destroyed when their defense drops below 1.)"
    accelerateSpell = DisrestanOceanHarbinger_Accelerate
    attackAdd, healthAdd = 2, 2
    name_CN = "神鱼·迪斯雷斯坦"

    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.trigsHand = [Trig_DisrestanOceanHarbinger(self)]

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
        x = self.Game.Manas.manas[self.ID]
        for minion in self.Game.minionsonBoard(3 - self.ID):
            minion.buffDebuff(-x, -x)


class Trig_DisrestanOceanHarbinger(TrigHand):
    def __init__(self, entity):
        self.blank_init(entity, ["TurnEnds"])

    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.inHand and ID == self.entity.ID

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        if self.entity.Game.Manas.manasUpper == 10:
            ManaMod(self.entity, changeby=-10, changeto=-1).applies()


"""Shadowcraft cards"""


class ShaoShadyApothecary(SVMinion):
    Class, race, name = "Shadowcraft", "", "Shao, Shady Apothecary"
    mana, attack, health = 1, 1, 2
    index = "SV_Eternal~Shadowcraft~Minion~1~1~2~None~Shao, Shady Apothecary~Battlecry~Necromancy"
    requireTarget, keyWord, description = False, "", "Fanfare: Necromancy (6) - Reanimate (4)."
    attackAdd, healthAdd = 2, 2
    name_CN = "妖艳的药剂师·萧"


class UndeadParade(SVSpell):
    Class, name = "Shadowcraft", "Undead Parade"
    requireTarget, mana = True, 1
    index = "SV_Eternal~Shadowcraft~Spell~1~Undead Parade"
    description = "Burial Rite: Summon 2 Skeletons.If you've performed Burial Rites at least 5 times (excluding this card) this match, summon 2 Liches instead."
    name_CN = "不死游行"


class WingedZombie(SVMinion):
    Class, race, name = "Shadowcraft", "", "Winged Zombie"
    mana, attack, health = 2, 2, 2
    index = "SV_Eternal~Shadowcraft~Minion~2~2~2~None~Winged Zombie"
    requireTarget, keyWord, description = False, "", "When you perform Necromancy, gain Storm."
    attackAdd, healthAdd = 2, 2
    name_CN = "骨翼傀儡"


class PsychopompTourGuide(SVMinion):
    Class, race, name = "Shadowcraft", "", "Psychopomp Tour Guide"
    mana, attack, health = 2, 2, 1
    index = "SV_Eternal~Shadowcraft~Minion~2~2~1~None~Psychopomp Tour Guide~Battlecry"
    requireTarget, keyWord, description = True, "", "Fanfare: If any other allied followers are in play, destroy 1 and draw 2 cards."
    attackAdd, healthAdd = 2, 2
    name_CN = "灵魂向导"


class NiyonMysticMusician(SVMinion):
    Class, race, name = "Shadowcraft", "", "Niyon, Mystic Musician"
    mana, attack, health = 2, 1, 4
    index = "SV_Eternal~Shadowcraft~Minion~2~1~4~None~Niyon, Mystic Musician~Stealth~Taunt~Battlecry~SkyboundArt~SuperSkyboundArt~Legendary"
    requireTarget, keyWord, description = False, "Stealth,Taunt", "Ambush.Ward.Fanfare: Skybound Art (10) - Give +1/+1 and Bane to all allied followers.Super Skybound Art (15): Remove Ward from all enemy followers, and give them the following effect until the end of your opponent's turn - Can't attack."
    attackAdd, healthAdd = 2, 2
    name_CN = "细致入微的魔奏者·妮欧"

    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.trigsHand = [Trig_SkyboundArt(self), Trig_SuperSkyboundArt(self)]

    def effCanTrig(self):
        for trig in self.trigsHand:
            if type(trig) == Trig_SkyboundArt and trig.progress <= self.Game.Counters.turns[self.ID]:
                self.effectViable = True
                return
            if type(trig) == Trig_SuperSkyboundArt and trig.progress <= self.Game.Counters.turns[self.ID]:
                self.effectViable = True
                return

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        sa, ssa = False, False
        for trig in self.trigsHand:
            if type(trig) == Trig_SkyboundArt and trig.progress <= self.Game.Counters.turns[self.ID]:
                sa = True
            if type(trig) == Trig_SuperSkyboundArt and trig.progress <= self.Game.Counters.turns[self.ID]:
                ssa = True
        if sa:
            for minion in self.Game.minionsonBoard(self.ID):
                minion.buffDebuff(1, 1)
                minion.getsKeyword("Bane")
        if ssa:
            for minion in self.Game.minionsonBoard(3 - self.ID):
                minion.losesKeyword("Taunt")
                minion.getsFrozen()


class Skullfish(SVMinion):
    Class, race, name = "Shadowcraft", "", "Skullfish"
    mana, attack, health = 3, 3, 2
    index = "SV_Eternal~Shadowcraft~Minion~3~3~2~None~Skullfish~Rush~Deathrattle"
    requireTarget, keyWord, description = False, "Rush", "Rush. Last Words: Necromancy (2) - Deal 2 damage to the enemy leader."
    attackAdd, healthAdd = 2, 2
    name_CN = "骸骨鱼"


class TriHeadHound(SVMinion):
    Class, race, name = "Shadowcraft", "", "Tri-Head Hound"
    mana, attack, health = 3, 1, 1
    index = "SV_Eternal~Shadowcraft~Minion~3~1~1~None~Tri-Head Hound~Deathrattle"
    requireTarget, keyWord, description = False, "", "Last Words: Summon a 5-play point, 2-attack Tri-Head Hound with the following effect - Last Words: Summon a 7-play point, 3-attack Tri-Head Hound without Last Words."
    attackAdd, healthAdd = 2, 2
    name_CN = "三头犬"


class TriHeadHound_Token(SVMinion):
    Class, race, name = "Shadowcraft", "", "Tri-Head Hound"
    mana, attack, health = 5, 2, 1
    index = "SV_Eternal~Shadowcraft~Minion~5~2~1~None~Tri-Head Hound~Deathrattle~Uncollectible"
    requireTarget, keyWord, description = False, "", "Last Words: Summon a 7-play point, 3-attack Tri-Head Hound without Last Words."
    attackAdd, healthAdd = 2, 2
    name_CN = "三头犬"


class TriHeadHound_Token2(SVMinion):
    Class, race, name = "Shadowcraft", "", "Tri-Head Hound"
    mana, attack, health = 7, 3, 1
    index = "SV_Eternal~Shadowcraft~Minion~7~3~1~None~Tri-Head Hound~Uncollectible"
    requireTarget, keyWord, description = False, "", ""
    attackAdd, healthAdd = 2, 2
    name_CN = "三头犬"


class ZajaDeliriousBerserker(SVMinion):
    Class, race, name = "Shadowcraft", "", "Zaja, Delirious Berserker"
    mana, attack, health = 4, 3, 4
    index = "SV_Eternal~Shadowcraft~Minion~4~3~4~None~Zaja, Delirious Berserker~Taunt~Battlecry"
    requireTarget, keyWord, description = True, "Taunt", "Ward.Fanfare: Burial Rite - Gain the ability to evolve for 0 evolution points."
    attackAdd, healthAdd = 2, 2
    name_CN = "打破虚妄的战士·扎扎"


class LonesomeNecromancer(SVMinion):
    Class, race, name = "Shadowcraft", "", "Lonesome Necromancer"
    mana, attack, health = 6, 4, 5
    index = "SV_Eternal~Shadowcraft~Minion~6~4~5~None~Lonesome Necromancer~Battlecry"
    requireTarget, keyWord, description = False, "", "Fanfare: Summon a Ghost. Reanimate (4)."
    attackAdd, healthAdd = 2, 2
    name_CN = "友善的唤灵师"


class VaseragaShadowedScythe(SVMinion):
    Class, race, name = "Shadowcraft", "", "Vaseraga, Shadowed Scythe"
    mana, attack, health = 7, 4, 7
    index = "SV_Eternal~Shadowcraft~Minion~7~4~7~None~Vaseraga, Shadowed Scythe~Deathrattle"
    requireTarget, keyWord, description = False, "", "Can't be targeted by enemy effects.Last Words: Summon a Vaseraga, Shadowed Scythe."
    attackAdd, healthAdd = 2, 2
    name_CN = "幽冥钢刃·巴萨拉卡"


class RuinbladeReaper(SVMinion):
    Class, race, name = "Shadowcraft", "", "Ruinblade Reaper"
    mana, attack, health = 10, 1, 7
    index = "SV_Eternal~Shadowcraft~Minion~10~1~7~None~Ruinblade Reaper~Bane~Necromancy~Legendary"
    requireTarget, keyWord, description = False, "Bane", "At the end of your turn, if you have 5 cards in play and at least 15 shadows, change the cost of this card to 0.Bane.When this card comes into play, perform Necromancy (20): Evolve this follower.Can't be evolved using evolution points. (Can be evolved using card effects.)"
    attackAdd, healthAdd = 6, 0
    name_CN = "死灭之剑皇"


"""Bloodcraft cards"""


class RougeVampire(SVMinion):
    Class, race, name = "Bloodcraft", "", "Rouge Vampire"
    mana, attack, health = 1, 1, 1
    index = "SV_Eternal~Bloodcraft~Minion~1~1~1~None~Rouge Vampire~Drain~Battlecry"
    requireTarget, keyWord, description = False, "Drain", "Drain.Fanfare: If Wrath is not active for you, deal 1 damage to your leader. Otherwise, gain +2/+2 and Rush."
    attackAdd, healthAdd = 2, 2
    name_CN = "殷红暗夜眷属"


class WickedWolf(SVMinion):
    Class, race, name = "Bloodcraft", "", "Wicked Wolf"
    mana, attack, health = 2, 2, 2
    index = "SV_Eternal~Bloodcraft~Minion~2~2~2~None~Wicked Wolf~Bane~Battlecry~Enhance"
    requireTarget, keyWord, description = False, "Bane", "Bane.Fanfare: Enhance (7) - Summon 3 Wicked Wolves. Give all allied Wicked Wolves the following effect: Reduce damage from effects to 0."
    attackAdd, healthAdd = 2, 2
    name_CN = "邪恶魔狼"


class SkullFreedomRaider(SVMinion):
    Class, race, name = "Bloodcraft", "", "Skull, Freedom Raider"
    mana, attack, health = 2, 2, 1
    index = "SV_Eternal~Bloodcraft~Minion~2~2~1~None~Skull, Freedom Raider~Rush~Battlecry"
    requireTarget, keyWord, description = False, "Rush", "Rush.Fanfare: If Vengeance is active for you, gain Storm.Fanfare: If Avarice is active for you, gain +2/+2."
    attackAdd, healthAdd = 2, 2
    name_CN = "自由飞驰的男子汉·斯卡尔"


class HallessenaCalamitysSaw(SVMinion):
    Class, race, name = "Bloodcraft", "", "Hallessena, Calamity's Saw"
    mana, attack, health = 3, 2, 1
    index = "SV_Eternal~Bloodcraft~Minion~3~2~1~None~Hallessena, Calamity's Saw~Battlecry"
    requireTarget, keyWord, description = False, "", "Fanfare: The next time this follower takes damage, reduce that damage to 0.Strike: Gain +1/+0.Can't be attacked."
    attackAdd, healthAdd = 2, 2
    name_CN = "坏天灾·哈雷泽娜"


class CorruptingBloodlust(SVSpell):
    Class, name = "Bloodcraft", "Corrupting Bloodlust"
    requireTarget, mana = False, 3
    index = "SV_Eternal~Bloodcraft~Spell~3~Corrupting Bloodlust"
    description = "Deal 1 damage to all allies and enemies. Do this twice."
    name_CN = "侵蚀的杀意"


class DiscerningDevil(SVMinion):
    Class, race, name = "Bloodcraft", "", "Discerning Devil"
    mana, attack, health = 4, 3, 3
    index = "SV_Eternal~Bloodcraft~Minion~4~3~3~None~Discerning Devil~Battlecry~Deathrattle"
    requireTarget, keyWord, description = False, "", "Fanfare: Draw a card.Last Words: At the start of your next turn, draw a card."
    attackAdd, healthAdd = 2, 2
    name_CN = "洞察的恶魔"


class GluttonousDemon(SVMinion):
    Class, race, name = "Bloodcraft", "", "Gluttonous Demon"
    mana, attack, health = 4, 2, 8
    index = "SV_Eternal~Bloodcraft~Minion~4~2~8~None~Gluttonous Demon"
    requireTarget, keyWord, description = False, "", "Can't attack.Once on each of your turns, when this follower's attack or defense is increased by an effect, destroy a random enemy follower and restore 3 defense to your leader.At the end of your turn, if Avarice is active for you, gain +2/+0."
    attackAdd, healthAdd = 0, 0
    name_CN = "暴食的恶魔"


class KnightofPurgatory(SVMinion):
    Class, race, name = "Bloodcraft", "", "Knight of Purgatory"
    mana, attack, health = 4, 4, 4
    index = "SV_Eternal~Bloodcraft~Minion~4~4~4~None~Knight of Purgatory~Taunt~Battlecry~Invocation"
    requireTarget, keyWord, description = False, "Taunt", "Invocation: At the end of your turn, if Wrath is active for you, invoke this card. Then, banish all Knights of Purgatory from your deck.Ward.Fanfare: Restore 4 defense to your leader."
    attackAdd, healthAdd = 2, 2
    name_CN = "炼狱之黑暗骑士"


class DemonicBerserker(SVMinion):
    Class, race, name = "Bloodcraft", "", "Demonic Berserker"
    mana, attack, health = 5, 5, 5
    index = "SV_Eternal~Bloodcraft~Minion~5~5~5~None~Demonic Berserker~Rush~Battlecry"
    requireTarget, keyWord, description = False, "Rush", "Rush.Fanfare: Deal 1 damage to a random leader. Do this 3 times."
    attackAdd, healthAdd = 2, 2
    name_CN = "恶魔狂战士"


class SeoxHeavenlyHowl(SVMinion):
    Class, race, name = "Bloodcraft", "", "Seox, Heavenly Howl"
    mana, attack, health = 6, 4, 2
    index = "SV_Eternal~Bloodcraft~Minion~6~4~2~None~Seox, Heavenly Howl~Rush~Windfury~Battlecry~SkyboundArt~SuperSkyboundArt~Legendary"
    requireTarget, keyWord, description = False, "Rush,Windfury", "Rush.Fanfare: Skybound Art (10) - Subtract 5 from the cost of all Swordcraft followers in your hand.Super Skybound Art (15): Subtract 5 from the cost of all Swordcraft followers in your deck.During your turn, when this follower attacks and destroys an enemy follower, if this follower is not destroyed, evolve it."
    attackAdd, healthAdd = 2, 2
    name_CN = "神狼·希斯"

    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.trigsHand = [Trig_SkyboundArt(self), Trig_SuperSkyboundArt(self), Trig_SeoxHeavenlyHowl(self)]

    def effCanTrig(self):
        for trig in self.trigsHand:
            if type(trig) == Trig_SkyboundArt and trig.progress <= self.Game.Counters.turns[self.ID]:
                self.effectViable = True
                return
            if type(trig) == Trig_SuperSkyboundArt and trig.progress <= self.Game.Counters.turns[self.ID]:
                self.effectViable = True
                return

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        sa, ssa = False, False
        for trig in self.trigsHand:
            if type(trig) == Trig_SkyboundArt and trig.progress <= self.Game.Counters.turns[self.ID]:
                sa = True
            if type(trig) == Trig_SuperSkyboundArt and trig.progress <= self.Game.Counters.turns[self.ID]:
                ssa = True
        if ssa:
            self.Game.summon([SeoxHeavenlyHowl(self.Game, self.ID), SeoxHeavenlyHowl(self.Game, self.ID)],
                             (-1, "totheRightEnd"), self.ID)
        elif sa:
            self.Game.summon([SeoxHeavenlyHowl(self.Game, self.ID)], (-1, "totheRightEnd"), self.ID)


class Trig_SeoxHeavenlyHowl(TrigBoard):
    def __init__(self, entity):
        self.blank_init(entity, ["MinionAttackedMinion", "MinionAttackedHero"])

    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.onBoard and subject == self.entity

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        self.entity.getsKeyword("Charge")
        self.entity.marks["Next Damage 0"] = 1
        for trig in self.entity.trigsBoard:
            if trig == self:
                self.entity.trigsBoard.remove(trig)
                trig.disconnect()
                break


class XenoDiablo_Crystallize(Amulet):
    Class, race, name = "Bloodcraft", "", "Crystallize: Xeno Diablo"
    mana = 3
    index = "SV_Eternal~Bloodcraft~Amulet~3~None~Xeno Diablo~Countdown~Crystallize~Deathrattle~Legendary~Uncollectible"
    requireTarget, description = False, " Countdown (7)At the start of your turn, restore 1 defense to your leader and, if you have more evolution points than your opponent, subtract 1 from this amulet's Countdown. (You have 0 evolution points on turns you are unable to evolve.)Last Words: Summon a Xeno Diablo."
    name_CN = "结晶：异种·迪亚波罗"


class XenoDiablo(SVMinion):
    Class, race, name = "Bloodcraft", "", "Xeno Diablo"
    mana, attack, health = 7, 10, 2
    index = "SV_Eternal~Bloodcraft~Minion~7~10~2~None~Xeno Diablo~Deathrattle~Crystallize~Legendary"
    requireTarget, keyWord, description = False, "", "Crystallize (3): Countdown (7)At the start of your turn, restore 1 defense to your leader and, if you have more evolution points than your opponent, subtract 1 from this amulet's Countdown. (You have 0 evolution points on turns you are unable to evolve.)Last Words: Summon a Xeno Diablo.Last Words: If Vengeance is active for you, deal 4 damage to all enemies. If Avarice is active for you, deal 4 damage to all enemies. If Wrath is active for you, deal 4 damage to all enemies."
    crystallizeAmulet = XenoDiablo_Crystallize
    attackAdd, healthAdd = 2, 2
    name_CN = "异种·迪亚波罗"


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


class WillUnderworldPriest(SVMinion):
    Class, race, name = "Havencraft", "", "Will, Underworld Priest"
    mana, attack, health = 1, 1, 2
    index = "SV_Eternal~Havencraft~Minion~1~1~2~None~Will, Underworld Priest~Battlecry"
    requireTarget, keyWord, description = False, "", "Fanfare: Restore 1 defense to all allies. If Avarice is active for you, deal 1 damage to the enemy leader."
    attackAdd, healthAdd = 2, 2
    name_CN = "宠爱魔物的暗之圣职者·威尔"


class UnicornAltar(Amulet):
    Class, race, name = "Havencraft", "", "Unicorn Altar"
    mana = 1
    index = "SV_Eternal~Havencraft~Amulet~1~None~Unicorn Altar~Countdown~Deathrattle"
    requireTarget, description = False, "Countdown (4)Fanfare: Put a Unicorn into your hand.At the end of your turn, subtract 1 from the cost of a random Unicorn in your hand.Last Words: Deal 4 damage to a random enemy follower. Restore 1 defense to your leader."
    name_CN = "独角兽祭坛"


class Unicorn(SVMinion):
    Class, race, name = "Havencraft", "", "Unicorn"
    mana, attack, health = 6, 5, 5
    index = "SV_Eternal~Havencraft~Minion~6~5~5~None~Unicorn~Battlecry~Uncollectible"
    requireTarget, keyWord, description = True, "", "Fanfare: Restore 3 defense to an ally."
    attackAdd, healthAdd = 2, 2
    name_CN = "独角兽"


class BelfrySister(SVMinion):
    Class, race, name = "Havencraft", "", "Belfry Sister"
    mana, attack, health = 2, 2, 2
    index = "SV_Eternal~Havencraft~Minion~2~2~2~None~Belfry Sister~Battlecry~Enhance"
    requireTarget, keyWord, description = False, "", "Fanfare: Enhance (5) - Gain the ability to evolve for 0 evolution points."
    attackAdd, healthAdd = 2, 2
    name_CN = "钟楼的修女"


class AnretheEnlightenedOne(SVMinion):
    Class, race, name = "Havencraft", "", "Anre, the Enlightened One"
    mana, attack, health = 2, 1, 1
    index = "SV_Eternal~Havencraft~Minion~2~1~1~None~Anre, the Enlightened One~Taunt~Battlecry~SkyboundArt~SuperSkyboundArt~Legendary"
    requireTarget, keyWord, description = True, "Taunt", "Bane.Fanfare: Select an enemy follower. It can't attack until the end of your opponent's turn.Skybound Art (10): Evolve this follower. Give +2/+0 to all other allied followers.Super Skybound Art (15): Strike - Deal X damage to all enemies. X equals this follower's attack."
    attackAdd, healthAdd = 2, 2
    name_CN = "开眼者·乌诺"

    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.trigsHand = [Trig_SkyboundArt(self), Trig_SuperSkyboundArt(self)]

    def effCanTrig(self):
        for trig in self.trigsHand:
            if type(trig) == Trig_SkyboundArt and trig.progress <= self.Game.Counters.turns[self.ID]:
                self.effectViable = True
                return
            if type(trig) == Trig_SuperSkyboundArt and trig.progress <= self.Game.Counters.turns[self.ID]:
                self.effectViable = True
                return

    def returnTrue(self, choice=0):
        sa = False
        for trig in self.trigsHand:
            if type(trig) == Trig_SkyboundArt and trig.progress <= self.Game.Counters.turns[self.ID]:
                sa = True
                break
        return sa and self.targetExists(choice) and not self.targets

    def targetExists(self, choice=0):
        sa = False
        for trig in self.trigsHand:
            if type(trig) == Trig_SkyboundArt and trig.progress <= self.Game.Counters.turns[self.ID]:
                sa = True
                break
        return sa and self.selectableEnemyMinionExists()

    def targetCorrect(self, target, choice=0):
        if isinstance(target, list): target = target[0]
        sa = False
        for trig in self.trigsHand:
            if type(trig) == Trig_SkyboundArt and trig.progress <= self.Game.Counters.turns[self.ID]:
                sa = True
                break
        return sa and target.type == "Minion" and target.ID != self.ID and target.onBoard

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        self.marks["Next Damage 0"] = 1
        sa, ssa = False, False
        for trig in self.trigsHand:
            if type(trig) == Trig_SkyboundArt and trig.progress <= self.Game.Counters.turns[self.ID]:
                sa = True
            if type(trig) == Trig_SuperSkyboundArt and trig.progress <= self.Game.Counters.turns[self.ID]:
                ssa = True
        if sa and target:
            if isinstance(target, list): target = target[0]
            self.dealsDamage(target, 11)
        if ssa:
            targets = self.Game.minionsonBoard(self.ID)
            targets.append(self.Game.heroes[self.ID])
            for t in targets:
                trig = Trig_AnretheEnlightenedOne(t)
                t.trigsBoard.append(trig)
                trig.connect()


class Trig_AnretheEnlightenedOne(TrigBoard):
    def __init__(self, entity):
        self.blank_init(entity, ["BattleDmgHero", "BattleDmgMinion", "AbilityDmgHero", "AbilityDmgMinion"])

    def canTrig(self, signal, ID, subject, target, number, comment,
                choice=0):  # target here holds the actual target object
        return target == self.entity

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        number[0] -= 1


class ZahlhamelinaSunPriestess(SVMinion):
    Class, race, name = "Havencraft", "", "Zahlhamelina, Sun Priestess"
    mana, attack, health = 3, 1, 5
    index = "SV_Eternal~Havencraft~Minion~3~1~5~None~Zahlhamelina, Sun Priestess~Taunt"
    requireTarget, keyWord, description = False, "Taunt", "Ward.If this follower has 2 defense or less, whenever an allied follower attacks, deal 2 damage to the enemy leader."
    attackAdd, healthAdd = 2, 2
    name_CN = "日轮的巫女·扎哈梅丽娜"


class RedeemersCudgel(SVSpell):
    Class, name = "Havencraft", "Redeemer's Cudgel"
    requireTarget, mana = True, 4
    index = "SV_Eternal~Havencraft~Spell~4~Redeemer's Cudgel"
    description = "Whenever you play an amulet, subtract 1 from the cost of this card.Banish an enemy follower."
    name_CN = "净化的矛锤"


class SwordAlmiraj(SVMinion):
    Class, race, name = "Havencraft", "", "Sword Al-mi'raj"
    mana, attack, health = 5, 3, 6
    index = "SV_Eternal~Havencraft~Minion~5~3~6~None~Sword Al-mi'raj~Rush"
    requireTarget, keyWord, description = False, "Rush", "Rush.At the end of your turn, restore 2 defense to your leader."
    attackAdd, healthAdd = 2, 2
    name_CN = "跃剑月兔妖"


class XenoVohuManah_Crystallize(Amulet):
    Class, race, name = "Havencraft", "", "Crystallize: Xeno Vohu Manah"
    mana = 3
    index = "SV_Eternal~Havencraft~Amulet~3~None~Xeno Vohu Manah~Countdown~Crystallize~Deathrattle~Legendary~Uncollectible"
    requireTarget, description = False, " Countdown (4)At the start of your turn, if you have more evolution points than your opponent, subtract 1 from this amulet's Countdown. (You have 0 evolution points on turns you are unable to evolve.)Last Words: Summon a Xeno Vohu Manah."
    name_CN = "结晶：异种·沃胡摩耶"


class XenoVohuManah(SVMinion):
    Class, race, name = "Havencraft", "", "Xeno Vohu Manah"
    mana, attack, health = 5, 2, 6
    index = "SV_Eternal~Havencraft~Minion~5~2~6~None~Xeno Vohu Manah~Crystallize~Legendary"
    requireTarget, keyWord, description = False, "", "Crystallize (3): Countdown (4)At the start of your turn, if you have more evolution points than your opponent, subtract 1 from this amulet's Countdown. (You have 0 evolution points on turns you are unable to evolve.)Last Words: Summon a Xeno Vohu Manah.Can evolve for 0 evolution points.At the end of your turn, restore 4 defense to this follower.Whenever this follower takes damage, if it's not destroyed, give it the following effect until the end of your opponent's turn: Can't be attacked."
    crystallizeAmulet = XenoVohuManah_Crystallize
    attackAdd, healthAdd = 2, 2
    name_CN = "异种·沃胡摩耶"


class SacredTiger_Crystallize(Amulet):
    Class, race, name = "Havencraft", "", "Crystallize: Sacred Tiger"
    mana = 3
    index = "SV_Eternal~Havencraft~Amulet~3~None~Sacred Tiger~Countdown~Crystallize~Deathrattle~Uncollectible"
    requireTarget, description = False, "Countdown (2) Last Words: Summon a White Tiger and Holyflame Tiger."
    name_CN = "结晶：圣洁之虎"


class SacredTiger(SVMinion):
    Class, race, name = "Havencraft", "", "Sacred Tiger"
    mana, attack, health = 7, 3, 3
    index = "SV_Eternal~Havencraft~Minion~7~3~3~None~Sacred Tiger~Charge~Crystallize"
    requireTarget, keyWord, description = False, "Charge", "Crystallize (3): Countdown (2)Last Words: Summon a White Tiger and Holyflame Tiger.Storm.Fanfare: Summon a White Tiger and Holyflame Tiger."
    crystallizeAmulet = SacredTiger_Crystallize
    attackAdd, healthAdd = 2, 2
    name_CN = "圣洁之虎"


class WhiteTiger(SVMinion):
    Class, race, name = "Havencraft", "", "White Tiger"
    mana, attack, health = 3, 3, 2
    index = "SV_Eternal~Havencraft~Minion~3~3~2~None~White Tiger~Taunt~Uncollectible"
    requireTarget, keyWord, description = False, "Taunt", "Ward. Can't be targeted by enemy effects."
    attackAdd, healthAdd = 2, 2
    name_CN = "圣洁之虎"


class NoaPrimalShipwright_Crystallize(Amulet):
    Class, race, name = "Havencraft", "", "Crystallize: Noa, Primal Shipwright"
    mana = 1
    index = "SV_Eternal~Havencraft~Amulet~1~None~Noa, Primal Shipwright~Countdown~Crystallize~Deathrattle~Uncollectible"
    requireTarget, description = False, " Countdown (4) Last Words: Summon a Noa, Primal Shipwright."
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
    requireTarget, keyWord, description = True, "", "Crystallize (1): Countdown (4)Last Words: Summon a Noa, Primal Shipwright.Fanfare: Remove all effects on an enemy follower except changes to its attack or defense. Then, give it -0/-5. (Followers are destroyed when their defense drops below 1.)When this follower comes into play, gain +X/+X. X equals your Rally count (excluding this card). If X is at least 10, evolve this follower."
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


class MechanizedSoldier(SVMinion):
    Class, race, name = "Portalcraft", "", "Mechanized Soldier"
    mana, attack, health = 2, 2, 2
    index = "SV_Eternal~Portalcraft~Minion~2~2~2~None~Mechanized Soldier~Battlecry~Enhance"
    requireTarget, keyWord, description = False, "", "Fanfare: Enhance (4) - Summon a Mechanized Soldier.Enhance (6): Summon 2 instead.Enhance (8): Summon 3 instead, and give all allied Mechanized Soldiers the ability to evolve for 0 evolution points."
    attackAdd, healthAdd = 2, 2
    name_CN = "机械化步兵"


class CatherineNightsmoke(SVMinion):
    Class, race, name = "Portalcraft", "", "Catherine, Nightsmoke"
    mana, attack, health = 2, 2, 1
    index = "SV_Eternal~Portalcraft~Minion~2~2~1~None~Catherine, Nightsmoke~Stealth~Battlecry"
    requireTarget, keyWord, description = False, "Stealth", "Ambush.Fanfare: Choose - Put 1 of the following cards into your hand.-Gilded Goblet-Gilded Boots-Gilded Necklace"
    attackAdd, healthAdd = 2, 2
    name_CN = "夜失的桃烟·凯瑟琳"


class SpinnahSpinArtist(SVMinion):
    Class, race, name = "Portalcraft", "", "Spinnah, Spin Artist"
    mana, attack, health = 2, 1, 3
    index = "SV_Eternal~Portalcraft~Minion~2~1~3~None~Spinnah, Spin Artist~Battlecry~Enhance"
    requireTarget, keyWord, description = False, "", "Fanfare: Enhance (4) - Evolve this follower.Strike: If Resonance is active for you, gain the ability to attack 2 times this turn."
    attackAdd, healthAdd = 2, 2
    name_CN = "回转艺术家·斯平纳"


class LunaluFangirlA(SVMinion):
    Class, race, name = "Portalcraft", "", "Lunalu, Fangirl A"
    mana, attack, health = 2, 2, 2
    index = "SV_Eternal~Portalcraft~Minion~2~2~2~None~Lunalu, Fangirl A"
    requireTarget, keyWord, description = False, "", ""
    attackAdd, healthAdd = 2, 2
    name_CN = "妄想少女A·露娜露"


class Facsimile(SVSpell):
    Class, name = "Portalcraft", "Facsimile"
    requireTarget, mana = False, 1
    index = "SV_Eternal~Portalcraft~Spell~1~Facsimile~Uncollectible"
    description = "Put a copy of a random allied follower played this turn (excluding Lunalu, Fangirl A) into your hand."
    name_CN = "临摹"


class FeowerDoubleBladeFlash(SVMinion):
    Class, race, name = "Portalcraft", "", "Feower, Double Blade Flash"
    mana, attack, health = 2, 4, 2
    index = "SV_Eternal~Portalcraft~Minion~2~4~2~None~Feower, Double Blade Flash~Battlecry~SkyboundArt~SuperSkyboundArt~Legendary"
    requireTarget, keyWord, description = False, "", "Fanfare: Until the end of your opponent's turn, give -4/-0 to a random enemy follower with the highest attack in play.Skybound Art (10): Deal 4 damage to a random enemy follower. Do this 3 times.Super Skybound Art (15): Give all allied followers the ability to attack 2 times per turn.At the end of turns you are unable to evolve, return this card to your hand."
    attackAdd, healthAdd = 2, 2
    name_CN = "闪耀的双剑·卡托尔"

    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.trigsHand = [Trig_SkyboundArt(self), Trig_SuperSkyboundArt(self), Trig_FeowerTien(self)]

    def effCanTrig(self):
        for trig in self.trigsHand:
            if type(trig) == Trig_SkyboundArt and trig.progress <= self.Game.Counters.turns[self.ID]:
                self.effectViable = True
                return
            if type(trig) == Trig_SuperSkyboundArt and trig.progress <= self.Game.Counters.turns[self.ID]:
                self.effectViable = True
                return

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
                curGame.minions[3 - self.ID][i].buffDebuff(-4, 0, "StartofTurn " + self.ID)
        sa, ssa = False, False
        for trig in self.trigsHand:
            if type(trig) == Trig_SkyboundArt and trig.progress <= self.Game.Counters.turns[self.ID]:
                sa = True
            if type(trig) == Trig_SuperSkyboundArt and trig.progress <= self.Game.Counters.turns[self.ID]:
                ssa = True
        if sa:
            for _ in range(3):
                curGame = self.Game
                if curGame.mode == 0:
                    if curGame.guides:
                        i = curGame.guides.pop(0)
                    else:
                        minions = curGame.minionsAlive(3 - self.ID)
                        i = npchoice(minions).pos if minions else -1
                        curGame.fixedGuides.append(i)
                    if i > -1:
                        self.dealsDamage(curGame.minions[3 - self.ID][i], 4)
        if ssa:
            for minion in self.Game.minionsonBoard(self.ID):
                minion.getsKeyword("Windfury")


class TienTreacherousTrigger(SVMinion):
    Class, race, name = "Portalcraft", "", "Tien, Treacherous Trigger"
    mana, attack, health = 3, 2, 4
    index = "SV_Eternal~Portalcraft~Minion~3~2~4~None~Tien, Treacherous Trigger~Battlecry~SkyboundArt~SuperSkyboundArt~Legendary"
    requireTarget, keyWord, description = False, "", "Fanfare: Draw a card.Skybound Art (10): Gain +2/+0 and Storm.Super Skybound Art (15): Give Storm to all followers in your hand.At the end of turns you are unable to evolve, return this card to your hand."
    attackAdd, healthAdd = 2, 2
    name_CN = "魔弹的射手·艾瑟尔"

    def __init__(self, Game, ID):
        self.blank_init(Game, ID)
        self.trigsHand = [Trig_SkyboundArt(self), Trig_SuperSkyboundArt(self), Trig_FeowerTien(self)]

    def effCanTrig(self):
        for trig in self.trigsHand:
            if type(trig) == Trig_SkyboundArt and trig.progress <= self.Game.Counters.turns[self.ID]:
                self.effectViable = True
                return
            if type(trig) == Trig_SuperSkyboundArt and trig.progress <= self.Game.Counters.turns[self.ID]:
                self.effectViable = True
                return

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        self.Game.Hand_Deck.drawCard(self.ID)
        sa, ssa = False, False
        for trig in self.trigsHand:
            if type(trig) == Trig_SkyboundArt and trig.progress <= self.Game.Counters.turns[self.ID]:
                sa = True
            if type(trig) == Trig_SuperSkyboundArt and trig.progress <= self.Game.Counters.turns[self.ID]:
                ssa = True
        if sa:
            self.buffDebuff(2, 0)
            self.getsKeyword("Charge")
        if ssa:
            for card in self.Game.Hand_Deck.hands[self.ID]:
                if card.type == "Minion":
                    card.getsKeyword("Charge")


class Trig_FeowerTien(TrigBoard):
    def __init__(self, entity):
        self.blank_init(entity, ["TurnEnds"])

    def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
        return self.entity.onBoard and ID == self.entity.ID and self.entity.Game.Counters.turns[self.entity.ID] < \
               self.entity.Game.Counters.numEvolutionTurn[self.entity.ID]

    def effect(self, signal, ID, subject, target, number, comment, choice=0):
        self.entity.Game.returnMiniontoHand(self.entity, deathrattlesStayArmed=False)


class SurveillanceSystem(SVMinion):
    Class, race, name = "Portalcraft", "", "Surveillance System"
    mana, attack, health = 3, 3, 3
    index = "SV_Eternal~Portalcraft~Minion~3~3~3~None~Surveillance System"
    requireTarget, keyWord, description = False, "", "Once on each of your opponent's turns, when they play a card, put a Paradigm Shift into your hand."
    attackAdd, healthAdd = 2, 2
    name_CN = "间谍装置"


class CourageousPuppeteer(SVMinion):
    Class, race, name = "Portalcraft", "", "Courageous Puppeteer"
    mana, attack, health = 3, 2, 3
    index = "SV_Eternal~Portalcraft~Minion~3~2~3~None~Courageous Puppeteer~Battlecry"
    requireTarget, keyWord, description = False, "", "Fanfare: Put a Puppet into your hand."
    attackAdd, healthAdd = 2, 2
    name_CN = "突破自我的操偶师"


class KittyCatArsenal(SVSpell):
    Class, name = "Portalcraft", "Kitty-Cat Arsenal"
    requireTarget, mana = True, 3
    index = "SV_Eternal~Portalcraft~Spell~3~Kitty-Cat Arsenal"
    description = "Deal 3 damage to an enemy follower and then 2 damage to another random enemy follower.If you have more evolution points than your opponent, summon 2 Ancient Artifacts. (You have 0 evolution points on turns you are unable to evolve.)"
    name_CN = "肉球射击"


class ToyMender(SVMinion):
    Class, race, name = "Portalcraft", "", "Toy Mender"
    mana, attack, health = 6, 2, 4
    index = "SV_Eternal~Portalcraft~Minion~6~2~4~None~Toy Mender~Battlecry"
    requireTarget, keyWord, description = False, "", "Fanfare: Summon a Barrier Artifact."
    attackAdd, healthAdd = 2, 2
    name_CN = "玩具修缮师"


class MobilizedFactory_Crystallize(Amulet):
    Class, race, name = "Portalcraft", "", "Crystallize: Mobilized Factory"
    mana = 5
    index = "SV_Eternal~Portalcraft~Amulet~5~None~Mobilized Factory~Crystallize~Uncollectible"
    requireTarget, description = False, "During your turn, whenever an allied Artifact follower comes into play, give it Rush, recover 1 play point, and draw a card."
    name_CN = "结晶：巨械工厂"


class MobilizedFactory(SVMinion):
    Class, race, name = "Portalcraft", "", "Mobilized Factory"
    mana, attack, health = 10, 6, 6
    index = "SV_Eternal~Portalcraft~Minion~10~6~6~None~Mobilized Factory~Battlecry~Crystallize"
    requireTarget, keyWord, description = True, "", "Crystallize (5): During your turn, whenever an allied Artifact follower comes into play, give it Rush, recover 1 play point, and draw a card.Fanfare: Give +X/+X and Storm to another random allied follower. X equals the number of allied Artifact cards with different names destroyed this match."
    crystallizeAmulet = MobilizedFactory_Crystallize
    attackAdd, healthAdd = 2, 2
    name_CN = "巨械工厂"


"""DLC cards"""

SV_Eternal_Indices = {
    "SV_Eternal~Neutral~Minion~2~2~2~None~Master Sleuth~Battlecry~Enhance": MasterSleuth,
    "SV_Eternal~Neutral~Minion~2~1~1~None~Vyrn, Li'l Red Dragon~Battlecry~Enhance": VyrnLilRedDragon,
    "SV_Eternal~Neutral~Spell~2~Angelic Melody": AngelicMelody,
    "SV_Eternal~Neutral~Minion~2~1~2~None~Io, Journeymage~Battlecry~Enhance": IoJourneymage,
    "SV_Eternal~Neutral~Minion~2~2~1~None~Archangel of Remembrance~Battlecry": ArchangelofRemembrance,
    "SV_Eternal~Neutral~Minion~3~2~3~None~Fluffy Angel~Battlecry~Deathrattle": FluffyAngel,
    "SV_Eternal~Neutral~Minion~3~2~3~None~Eugen, Stalwart Skyfarer": EugenStalwartSkyfarer,
    "SV_Eternal~Neutral~Spell~0~Gran's Resolve~Legendary~Uncollectible": GransResolve,
    "SV_Eternal~Neutral~Spell~0~Djeeta's Determination~Legendary~Uncollectible": DjeetasDetermination,
    "SV_Eternal~Neutral~Minion~5~5~5~None~Gran & Djeeta, Eternal Heroes~Charge~Legendary~Uncollectible": GranDjeetaEternalHeroes,
    "SV_Eternal~Neutral~Spell~5~On Wings of Tomorrow~Legendary": OnWingsofTomorrow,
    "SV_Eternal~Neutral~Spell~5~Bahamut, Primeval Dragon~Accelerate~Legendary~Uncollectible": BahamutPrimevalDragon_Accelerate,
    "SV_Eternal~Neutral~Minion~10~12~10~None~Bahamut, Primeval Dragon~Battlecry~Accelerate~Legendary": BahamutPrimevalDragon,

    "SV_Eternal~Forestcraft~Minion~1~1~1~None~Walder, Forest Ranger~Charge~Battlecry~Enhance~Invocation": WalderForestRanger,
    "SV_Eternal~Forestcraft~Minion~2~2~2~None~Elf Sorcerer~Battlecry": ElfSorcerer,
    "SV_Eternal~Forestcraft~Minion~2~2~2~None~Mimlemel, Freewheeling Lass~Battlecry": MimlemelFreewheelingLass,
    "SV_Eternal~Forestcraft~Minion~4~4~1~None~Stumpeye~Rush~Uncollectible": Stumpeye,
    "SV_Eternal~Forestcraft~Minion~4~1~6~None~Blossom Treant~Deathrattle": BlossomTreant,
    "SV_Eternal~Forestcraft~Minion~4~4~4~None~Astoreth~Taunt~Battlecry": Astoreth,
    "SV_Eternal~Forestcraft~Minion~4~3~3~None~Tweyen, Dark Huntress~Bane~Battlecry~SkyboundArt~SuperSkyboundArt~Legendary": TweyenDarkHuntress,
    "SV_Eternal~Forestcraft~Minion~5~5~5~None~Greenwood Reindeer~Rush~Battlecry": GreenwoodReindeer,
    "SV_Eternal~Forestcraft~Amulet~1~None~Xeno Sagittarius~Countdown~Crystallize~Deathrattle~Legendary~Uncollectible": XenoSagittarius_Crystallize,
    "SV_Eternal~Forestcraft~Minion~6~6~4~None~Xeno Sagittarius~Battlecry~Crystallize~Legendary": XenoSagittarius,
    "SV_Eternal~Forestcraft~Spell~6~Nature Consumed": NatureConsumed,
    "SV_Eternal~Forestcraft~Minion~7~4~6~None~Primordial Colossus~Battlecry": PrimordialColossus,
    "SV_Eternal~Forestcraft~Spell~1~Wind Fairy~Accelerate~Uncollectible": WindFairy_Accelerate,
    "SV_Eternal~Forestcraft~Minion~9~3~3~None~Wind Fairy~Charge~Windfury~Accelerate": WindFairy,

    "SV_Eternal~Swordcraft~Minion~2~1~3~Officer~Arthur, Slumbering Dragon": ArthurSlumberingDragon,
    "SV_Eternal~Swordcraft~Minion~2~2~1~Officer~Mordred, Slumbering Lion": MordredSlumberingLion,
    "SV_Eternal~Swordcraft~Spell~2~Proven Methodology": ProvenMethodology,
    "SV_Eternal~Swordcraft~Minion~2~3~1~Officer~Mirin, Samurai Dreamer~Battlecry~SkyboundArt~SuperSkyboundArt": MirinSamuraiDreamer,
    "SV_Eternal~Swordcraft~Minion~3~2~1~Officer~Sword-Swinging Bandit~Charge~Deathrattle": SwordSwingingBandit,
    "SV_Eternal~Swordcraft~Spell~1~Grand Auction~Uncollectible": GrandAuction,
    "SV_Eternal~Swordcraft~Amulet~2~None~Ageworn Weaponry~Countdown~Deathrattle~Uncollectible": AgewornWeaponry,
    "SV_Eternal~Swordcraft~Amulet~2~None~Greatshield~Countdown~Battlecry~Deathrattle~Uncollectible": Greatshield,
    "SV_Eternal~Swordcraft~Amulet~2~None~Greatsword~Countdown~Battlecry~Deathrattle~Uncollectible": Greatsword,
    "SV_Eternal~Swordcraft~Minion~4~3~4~Officer~Stone Merchant~Battlecry": StoneMerchant,
    "SV_Eternal~Swordcraft~Minion~4~5~3~Commander~Seofon, Star Sword Sovereign~Battlecry~SkyboundArt~SuperSkyboundArt~Legendary": SeofonStarSwordSovereign,
    "SV_Eternal~Swordcraft~Minion~5~5~5~Commander~Victorious Grappler~Battlecry": VictoriousGrappler,
    "SV_Eternal~Swordcraft~Minion~7~2~7~Officer~Average Axeman~Charge~Bane": AverageAxeman,
    "SV_Eternal~Swordcraft~Minion~8~8~4~Officer~Rampaging Rhino~Rush~Battlecry": RampagingRhino,
    "SV_Eternal~Swordcraft~Minion~8~7~6~Officer~Eahta, God of the Blade~Rush~Battlecry~SkyboundArt~SuperSkyboundArt~Legendary": EahtaGodoftheBlade,

    "SV_Eternal~Runecraft~Minion~1~0~1~None~Alistair, Tiny Magus~Battlecry~Deathrattle": AlistairTinyMagus,
    "SV_Eternal~Runecraft~Spell~1~Impalement Arts~Spellboost": ImpalementArts,
    "SV_Eternal~Runecraft~Minion~2~3~1~None~Elmott, Pyrestarter~Battlecry~Spellboost": ElmottPyrestarter,
    "SV_Eternal~Runecraft~Spell~2~Elixir Mixer": ElixirMixer,
    "SV_Eternal~Runecraft~Spell~2~Force Barrier": ForceBarrier,
    "SV_Eternal~Runecraft~Minion~3~2~3~None~Academic Archmage~Battlecry": AcademicArchmage,
    "SV_Eternal~Runecraft~Minion~3~2~3~None~Fif, Prodigious Sorcerer~Battlecry~SkyboundArt~SuperSkyboundArt~Legendary": FifProdigiousSorcerer,
    "SV_Eternal~Runecraft~Minion~5~2~3~None~Crystal Witch~Battlecry~Spellboost": CrystalWitch,
    "SV_Eternal~Runecraft~Amulet~3~None~Xeno Ifrit~Countdown~Crystallize~Deathrattle~Legendary~Uncollectible": XenoIfrit_Crystallize,
    "SV_Eternal~Runecraft~Minion~6~5~4~None~Xeno Ifrit~Crystallize~Legendary": XenoIfrit,
    "SV_Eternal~Runecraft~Minion~7~4~4~None~Pholia, Retired Sovereign~Battlecry": PholiaRetiredSovereign,
    "SV_Eternal~Runecraft~Minion~7~4~6~None~Bai Ze~Rush~Taunt~Uncollectible": BaiZe,
    "SV_Eternal~Runecraft~Amulet~2~Earth Sigil~Raging Golem~Crystallize~Deathrattle~Uncollectible": RagingGolem_Crystallize,
    "SV_Eternal~Runecraft~Minion~8~6~6~None~Raging Golem~Rush~Crystallize~Deathrattle": RagingGolem,

    "SV_Eternal~Dragoncraft~Spell~1~Dragon Rearing": DragonRearing,
    "SV_Eternal~Dragoncraft~Minion~2~2~2~None~Shark Warrior~Battlecry~Enhance": SharkWarrior,
    "SV_Eternal~Dragoncraft~Minion~2~0~5~None~Mermaid Archer~Battlecry~Enhance": MermaidArcher,
    "SV_Eternal~Dragoncraft~Minion~4~3~2~None~Hypersonic Dragonewt~Charge~Battlecry": HypersonicDragonewt,
    "SV_Eternal~Dragoncraft~Minion~4~4~4~None~Hypersonic Dragonewt~Bane~Battlecry": HypersonicDragonewt,
    "SV_Eternal~Dragoncraft~Minion~4~2~4~None~Razia, Vengeful Cannonlancer~Taunt~Deathrattle": RaziaVengefulCannonlancer,
    "SV_Eternal~Dragoncraft~Minion~4~4~3~None~Threo, Divine Havoc~Rush~Battlecry~SkyboundArt~SuperSkyboundArt~Legendary": ThreoDivineHavoc,
    "SV_Eternal~Dragoncraft~Minion~5~5~5~None~Tempest Dragon": TempestDragon,
    "SV_Eternal~Dragoncraft~Minion~6~4~6~None~Ladiva, Champion of Love~Battlecry": LadivaChampionofLove,
    "SV_Eternal~Dragoncraft~Minion~9~8~7~None~Ghandagoza, Fist of Rage~Rush": GhandagozaFistofRage,
    "SV_Eternal~Dragoncraft~Spell~1~Disrestan, Ocean Harbinger~Accelerate~Legendary~Uncollectible": DisrestanOceanHarbinger_Accelerate,
    "SV_Eternal~Dragoncraft~Minion~17~13~13~None~Disrestan, Ocean Harbinger~Battlecry~Legendary": DisrestanOceanHarbinger,

    "SV_Eternal~Shadowcraft~Minion~1~1~2~None~Shao, Shady Apothecary~Battlecry~Necromancy": ShaoShadyApothecary,
    "SV_Eternal~Shadowcraft~Spell~1~Undead Parade": UndeadParade,
    "SV_Eternal~Shadowcraft~Minion~2~2~2~None~Winged Zombie": WingedZombie,
    "SV_Eternal~Shadowcraft~Minion~2~2~1~None~Psychopomp Tour Guide~Battlecry": PsychopompTourGuide,
    "SV_Eternal~Shadowcraft~Minion~2~1~4~None~Niyon, Mystic Musician~Stealth~Taunt~Battlecry~SkyboundArt~SuperSkyboundArt~Legendary": NiyonMysticMusician,
    "SV_Eternal~Shadowcraft~Minion~3~3~2~None~Skullfish~Rush~Deathrattle": Skullfish,
    "SV_Eternal~Shadowcraft~Minion~3~1~1~None~Tri-Head Hound~Deathrattle": TriHeadHound,
    "SV_Eternal~Shadowcraft~Minion~5~2~1~None~Tri-Head Hound~Deathrattle~Uncollectible": TriHeadHound_Token,
    "SV_Eternal~Shadowcraft~Minion~7~3~1~None~Tri-Head Hound~Uncollectible": TriHeadHound_Token2,
    "SV_Eternal~Shadowcraft~Minion~4~3~4~None~Zaja, Delirious Berserker~Taunt~Battlecry": ZajaDeliriousBerserker,
    "SV_Eternal~Shadowcraft~Minion~6~4~5~None~Lonesome Necromancer~Battlecry": LonesomeNecromancer,
    "SV_Eternal~Shadowcraft~Minion~7~4~7~None~Vaseraga, Shadowed Scythe~Deathrattle": VaseragaShadowedScythe,
    "SV_Eternal~Shadowcraft~Minion~10~1~7~None~Ruinblade Reaper~Bane~Necromancy~Legendary": RuinbladeReaper,

    "SV_Eternal~Bloodcraft~Minion~1~1~1~None~Rouge Vampire~Drain~Battlecry": RougeVampire,
    "SV_Eternal~Bloodcraft~Minion~2~2~2~None~Wicked Wolf~Bane~Battlecry~Enhance": WickedWolf,
    "SV_Eternal~Bloodcraft~Minion~2~2~1~None~Skull, Freedom Raider~Rush~Battlecry": SkullFreedomRaider,
    "SV_Eternal~Bloodcraft~Minion~3~2~1~None~Hallessena, Calamity's Saw~Battlecry": HallessenaCalamitysSaw,
    "SV_Eternal~Bloodcraft~Spell~3~Corrupting Bloodlust": CorruptingBloodlust,
    "SV_Eternal~Bloodcraft~Minion~4~3~3~None~Discerning Devil~Battlecry~Deathrattle": DiscerningDevil,
    "SV_Eternal~Bloodcraft~Minion~4~2~8~None~Gluttonous Demon": GluttonousDemon,
    "SV_Eternal~Bloodcraft~Minion~4~4~4~None~Knight of Purgatory~Taunt~Battlecry~Invocation": KnightofPurgatory,
    "SV_Eternal~Bloodcraft~Minion~5~5~5~None~Demonic Berserker~Rush~Battlecry": DemonicBerserker,
    "SV_Eternal~Bloodcraft~Minion~6~4~2~None~Seox, Heavenly Howl~Rush~Windfury~Battlecry~SkyboundArt~SuperSkyboundArt~Legendary": SeoxHeavenlyHowl,
    "SV_Eternal~Bloodcraft~Amulet~3~None~Xeno Diablo~Countdown~Crystallize~Deathrattle~Legendary~Uncollectible": XenoDiablo_Crystallize,
    "SV_Eternal~Bloodcraft~Minion~7~10~2~None~Xeno Diablo~Deathrattle~Crystallize~Legendary": XenoDiablo,

    "SV_Eternal~Havencraft~Amulet~1~Battlecry~Summit Temple": SummitTemple,
    "SV_Eternal~Havencraft~Minion~1~1~2~None~Will, Underworld Priest~Battlecry": WillUnderworldPriest,
    "SV_Eternal~Havencraft~Amulet~1~None~Unicorn Altar~Countdown~Deathrattle": UnicornAltar,
    "SV_Eternal~Havencraft~Minion~6~5~5~None~Unicorn~Battlecry~Uncollectible": Unicorn,
    "SV_Eternal~Havencraft~Minion~2~2~2~None~Belfry Sister~Battlecry~Enhance": BelfrySister,
    "SV_Eternal~Havencraft~Minion~2~1~1~None~Anre, the Enlightened One~Taunt~Battlecry~SkyboundArt~SuperSkyboundArt~Legendary": AnretheEnlightenedOne,
    "SV_Eternal~Havencraft~Minion~3~1~5~None~Zahlhamelina, Sun Priestess~Taunt": ZahlhamelinaSunPriestess,
    "SV_Eternal~Havencraft~Spell~4~Redeemer's Cudgel": RedeemersCudgel,
    "SV_Eternal~Havencraft~Minion~5~3~6~None~Sword Al-mi'raj~Rush": SwordAlmiraj,
    "SV_Eternal~Havencraft~Amulet~3~None~Xeno Vohu Manah~Countdown~Crystallize~Deathrattle~Legendary~Uncollectible": XenoVohuManah_Crystallize,
    "SV_Eternal~Havencraft~Minion~5~2~6~None~Xeno Vohu Manah~Crystallize~Legendary": XenoVohuManah,
    "SV_Eternal~Havencraft~Amulet~3~None~Sacred Tiger~Countdown~Crystallize~Deathrattle~Uncollectible": SacredTiger_Crystallize,
    "SV_Eternal~Havencraft~Minion~7~3~3~None~Sacred Tiger~Charge~Crystallize": SacredTiger,
    "SV_Eternal~Havencraft~Minion~3~3~2~None~White Tiger~Taunt~Uncollectible": WhiteTiger,
    "SV_Eternal~Havencraft~Amulet~1~None~Noa, Primal Shipwright~Countdown~Crystallize~Deathrattle~Uncollectible": NoaPrimalShipwright_Crystallize,
    "SV_Eternal~Havencraft~Minion~7~1~1~None~Noa, Primal Shipwright~Taunt~Crystallize": NoaPrimalShipwright,

    "SV_Eternal~Portalcraft~Minion~2~2~2~None~Mechanized Soldier~Battlecry~Enhance": MechanizedSoldier,
    "SV_Eternal~Portalcraft~Minion~2~2~1~None~Catherine, Nightsmoke~Stealth~Battlecry": CatherineNightsmoke,
    "SV_Eternal~Portalcraft~Minion~2~1~3~None~Spinnah, Spin Artist~Battlecry~Enhance": SpinnahSpinArtist,
    "SV_Eternal~Portalcraft~Minion~2~2~2~None~Lunalu, Fangirl A": LunaluFangirlA,
    "SV_Eternal~Portalcraft~Spell~1~Facsimile~Uncollectible": Facsimile,
    "SV_Eternal~Portalcraft~Minion~2~4~2~None~Feower, Double Blade Flash~Battlecry~SkyboundArt~SuperSkyboundArt~Legendary": FeowerDoubleBladeFlash,
    "SV_Eternal~Portalcraft~Minion~3~2~4~None~Tien, Treacherous Trigger~Battlecry~SkyboundArt~SuperSkyboundArt~Legendary": TienTreacherousTrigger,
    "SV_Eternal~Portalcraft~Minion~3~3~3~None~Surveillance System": SurveillanceSystem,
    "SV_Eternal~Portalcraft~Minion~3~2~3~None~Courageous Puppeteer~Battlecry": CourageousPuppeteer,
    "SV_Eternal~Portalcraft~Spell~3~Kitty-Cat Arsenal": KittyCatArsenal,
    "SV_Eternal~Portalcraft~Minion~6~2~4~None~Toy Mender~Battlecry": ToyMender,
    "SV_Eternal~Portalcraft~Amulet~5~None~Mobilized Factory~Crystallize~Uncollectible": MobilizedFactory_Crystallize,
    "SV_Eternal~Portalcraft~Minion~10~6~6~None~Mobilized Factory~Battlecry~Crystallize": MobilizedFactory,
}
