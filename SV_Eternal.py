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


class WalderForestRanger(SVMinion):
    Class, race, name = "Forestcraft", "", "Walder, Forest Ranger"
    mana, attack, health = 1, 1, 1
    index = "SV_Eternal~Forestcraft~Minion~1~1~1~None~Walder, Forest Ranger~Charge~Battlecry~Enhance~Invocation"
    requireTarget, keyWord, description = False, "Charge", "Invocation: When you play a card using its Accelerate effect for the second time this turn, invoke this card.Storm.Fanfare: Enhance (6) - Gain +X/+X. X equals the number of times you've played a card using its Accelerate effect this match."
    attackAdd, healthAdd = 2, 2
    name_CN = "森之战士·维鲁达"


class ElfSorcerer(SVMinion):
    Class, race, name = "Forestcraft", "", "Elf Sorcerer"
    mana, attack, health = 2, 2, 2
    index = "SV_Eternal~Forestcraft~Minion~2~2~2~None~Elf Sorcerer~Battlecry"
    requireTarget, keyWord, description = False, "", "Fanfare: Put a Fairy into your hand."
    attackAdd, healthAdd = 2, 2
    name_CN = "精灵咒术师"


class MimlemelFreewheelingLass(SVMinion):
    Class, race, name = "Forestcraft", "", "Mimlemel, Freewheeling Lass"
    mana, attack, health = 2, 2, 2
    index = "SV_Eternal~Forestcraft~Minion~2~2~2~None~Mimlemel, Freewheeling Lass~Battlecry"
    requireTarget, keyWord, description = False, "", "Fanfare: If at least 2 other cards were played this turn, summon a Stumpeye."
    attackAdd, healthAdd = 2, 2
    name_CN = "随心所欲的吹笛人·米姆露梅莫璐"


class Stumpeye(SVMinion):
    Class, race, name = "Forestcraft", "", "Stumpeye"
    mana, attack, health = 4, 4, 1
    index = "SV_Eternal~Forestcraft~Minion~4~4~1~None~Stumpeye~Rush~Uncollectible"
    requireTarget, keyWord, description = False, "Rush", "Rush. Strike: Give +0/+1 to all allied Mimlemel, Freewheeling Lasses."
    attackAdd, healthAdd = 2, 2
    name_CN = "残株"


class BlossomTreant(SVMinion):
    Class, race, name = "Forestcraft", "", "Blossom Treant"
    mana, attack, health = 4, 1, 6
    index = "SV_Eternal~Forestcraft~Minion~4~1~6~None~Blossom Treant~Deathrattle"
    requireTarget, keyWord, description = False, "", "At the start of your turn, evolve this follower.Last Words: Draw a card."
    attackAdd, healthAdd = 4, 0
    name_CN = "盛绽树精"


class Astoreth(SVMinion):
    Class, race, name = "Forestcraft", "", "Astoreth"
    mana, attack, health = 4, 4, 4
    index = "SV_Eternal~Forestcraft~Minion~4~4~4~None~Astoreth~Taunt~Battlecry"
    requireTarget, keyWord, description = False, "Taunt", "Ward.Fanfare: If at least 2 other cards were played this turn, evolve this follower."
    attackAdd, healthAdd = 2, 2
    name_CN = "阿斯塔蒂"


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


class XenoSagittarius_Crystallize(Amulet):
    Class, race, name = "Forestcraft", "", "Crystallize: Xeno Sagittarius"
    mana = 1
    index = "SV_Eternal~Forestcraft~Amulet~1~None~Xeno Sagittarius~Countdown~Crystallize~Deathrattle~Legendary~Uncollectible"
    requireTarget, description = False, "Countdown (1)When this amulet is returned to your hand, draw a card.Last Words: Draw a card."
    name_CN = "结晶：异种·射手座"


class XenoSagittarius(SVMinion):
    Class, race, name = "Forestcraft", "", "Xeno Sagittarius"
    mana, attack, health = 6, 6, 4
    index = "SV_Eternal~Forestcraft~Minion~6~6~4~None~Xeno Sagittarius~Battlecry~Crystallize~Legendary"
    requireTarget, keyWord, description = False, "", "Crystallize (1): Countdown (1)When this amulet is returned to your hand, draw a card.Last Words: Draw a card.Fanfare: Change the defense of all enemy followers to 1.Strike: Deal 1 damage to all enemy followers.When this follower is returned to your hand, deal 1 damage to all enemy followers."
    crystallizeAmulet = XenoSagittarius_Crystallize
    attackAdd, healthAdd = 2, 2
    name_CN = "异种·射手座"


class NatureConsumed(SVSpell):
    Class, name = "Forestcraft", "Nature Consumed"
    requireTarget, mana = True, 6
    index = "SV_Eternal~Forestcraft~Spell~6~Nature Consumed"
    description = "Destroy an enemy follower.Restore X defense to your leader and draw X cards. X equals half the destroyed follower's defense (rounded up)."
    name_CN = "大自然的捕食"


class PrimordialColossus(SVMinion):
    Class, race, name = "Forestcraft", "", "Primordial Colossus"
    mana, attack, health = 7, 4, 6
    index = "SV_Eternal~Forestcraft~Minion~7~4~6~None~Primordial Colossus~Battlecry"
    requireTarget, keyWord, description = False, "", "Fanfare: Give your leader the following effect - Once on each of your turns, when you play a card, recover 2 play points and add 2 to the number of cards played this turn. (This effect is not stackable and lasts for the rest of the match.)"
    attackAdd, healthAdd = 2, 2
    name_CN = "原始的恶神"


class WindFairy_Accelerate(SVSpell):
    Class, name = "Forestcraft", "Wind Fairy"
    requireTarget, mana = True, 1
    index = "SV_Eternal~Forestcraft~Spell~1~Wind Fairy~Accelerate~Uncollectible"
    description = "Return an allied follower or amulet to your hand. Put a Fairy Wisp into your hand."
    name_CN = "迅风妖精"


class WindFairy(SVMinion):
    Class, race, name = "Forestcraft", "", "Wind Fairy"
    mana, attack, health = 9, 3, 3
    index = "SV_Eternal~Forestcraft~Minion~9~3~3~None~Wind Fairy~Charge~Windfury~Accelerate"
    requireTarget, keyWord, description = True, "Charge,Windfury", "Fanfare: Give your leader the following effect - Once on each of your turns, when you play a card, recover 2 play points and add 2 to the number of cards played this turn. (This effect is not stackable and lasts for the rest of the match.)"
    accelerateSpell = WindFairy_Accelerate
    attackAdd, healthAdd = 2, 2
    name_CN = "迅风妖精"


"""Swordcraft cards"""


class ArthurSlumberingDragon(SVMinion):
    Class, race, name = "Swordcraft", "Officer", "Arthur, Slumbering Dragon"
    mana, attack, health = 2, 1, 3
    index = "SV_Eternal~Swordcraft~Minion~2~1~3~Officer~Arthur, Slumbering Dragon"
    requireTarget, keyWord, description = False, "", "At the end of your turn, Rally (10): Give your leader the following effect - The next time your leader takes damage, reduce that damage to 0."
    attackAdd, healthAdd = 2, 2
    name_CN = "沉睡的辉龙·亚瑟"


class MordredSlumberingLion(SVMinion):
    Class, race, name = "Swordcraft", "Officer", "Mordred, Slumbering Lion"
    mana, attack, health = 2, 2, 1
    index = "SV_Eternal~Swordcraft~Minion~2~2~1~Officer~Mordred, Slumbering Lion"
    requireTarget, keyWord, description = False, "", "At the end of your turn, Rally (5): Deal 1 damage to all enemy followers."
    attackAdd, healthAdd = 2, 2
    name_CN = "沉睡的狮子·莫德雷德"


class ProvenMethodology(SVSpell):
    Class, name = "Swordcraft", "Proven Methodology"
    requireTarget, mana = False, 2
    index = "SV_Eternal~Swordcraft~Spell~2~Proven Methodology"
    description = "Put a random Officer follower from your deck into your hand and give it +2/+2."
    name_CN = "老练的教鞭"


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


class GrandAuction(SVSpell):
    Class, name = "Swordcraft", "Grand Auction"
    requireTarget, mana = True, 1
    index = "SV_Eternal~Swordcraft~Spell~1~Grand Auction~Uncollectible"
    description = "Discard a card from your hand.Draw a card.Put an Ageworn Weaponry into your hand."
    name_CN = "大甩卖"


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
    requireTarget, description = False, "Countdown (1)Fanfare: Give an allied Swordcraft follower +0/+1.Last Words: Summon a Shield Guardian."
    name_CN = "坚韧之盾"


class Greatsword(Amulet):
    Class, race, name = "Swordcraft", "", "Greatsword"
    mana = 2
    index = "SV_Eternal~Swordcraft~Amulet~2~None~Greatsword~Countdown~Battlecry~Deathrattle~Uncollectible"
    requireTarget, description = False, "Countdown (1)Fanfare: Give an allied Swordcraft follower +1/+0.Last Words: Summon a Heavy Knight."
    name_CN = "锐利之剑"


class StoneMerchant(SVMinion):
    Class, race, name = "Swordcraft", "Officer", "Stone Merchant"
    mana, attack, health = 4, 3, 4
    index = "SV_Eternal~Swordcraft~Minion~4~3~4~Officer~Stone Merchant~Battlecry"
    requireTarget, keyWord, description = False, "", "Fanfare: Put 2 Grand Auctions into your hand."
    attackAdd, healthAdd = 2, 2
    name_CN = "奇石商贩"


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


class AverageAxeman(SVMinion):
    Class, race, name = "Swordcraft", "Officer", "Average Axeman"
    mana, attack, health = 7, 2, 7
    index = "SV_Eternal~Swordcraft~Minion~7~2~7~Officer~Average Axeman~Charge~Bane"
    requireTarget, keyWord, description = False, "Charge,Bane", "Storm.Bane.Strike: Recover X play points. X equals this follower's attack."
    attackAdd, healthAdd = 2, 2
    name_CN = "锐斧战士"


class RampagingRhino(SVMinion):
    Class, race, name = "Swordcraft", "Officer", "Rampaging Rhino"
    mana, attack, health = 8, 8, 4
    index = "SV_Eternal~Swordcraft~Minion~8~8~4~Officer~Rampaging Rhino~Rush~Battlecry"
    requireTarget, keyWord, description = False, "Rush", "Rush.Fanfare: Destroy a random enemy follower or amulet."
    attackAdd, healthAdd = 2, 2
    name_CN = "蛮冲铁犀"


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


class ImpalementArts(SVSpell):
    Class, name = "Runecraft", "Impalement Arts"
    requireTarget, mana = True, 1
    index = "SV_Eternal~Runecraft~Spell~1~Impalement Arts~Spellboost"
    description = "Deal 1 damage to an enemy.If this card has been Spellboosted at least 5 times, put an Impalement Arts into your hand and give it the following effect: At the end of your turn, discard this card."
    name_CN = "戏刀奇术"


class ElmottPyrestarter(SVMinion):
    Class, race, name = "Runecraft", "", "Elmott, Pyrestarter"
    mana, attack, health = 2, 3, 1
    index = "SV_Eternal~Runecraft~Minion~2~3~1~None~Elmott, Pyrestarter~Battlecry~Spellboost"
    requireTarget, keyWord, description = True, "", "Fanfare: Deal X damage to an enemy follower. X equals the number of times this card has been Spellboosted. Then, if X is at least 10, deal 4 damage to the enemy leader."
    attackAdd, healthAdd = 2, 2
    name_CN = "炎狱的葬送者·艾尔莫特"


class ElixirMixer(SVSpell):
    Class, name = "Runecraft", "Elixir Mixer"
    requireTarget, mana = True, 2
    index = "SV_Eternal~Runecraft~Spell~2~Elixir Mixer"
    description = "Give Rush, Bane, and Drain to an allied follower whose attack or defense has been increased by an effect."
    name_CN = "灵药调和"


class ForceBarrier(SVSpell):
    Class, name = "Runecraft", "Force Barrier"
    requireTarget, mana = False, 2
    index = "SV_Eternal~Runecraft~Spell~2~Force Barrier"
    description = "Until the end of your opponent's turn, give all allies the following effect: Reduce damage from effects by 2."
    name_CN = "魔御结界"


class AcademicArchmage(SVMinion):
    Class, race, name = "Runecraft", "", "Academic Archmage"
    mana, attack, health = 3, 2, 3
    index = "SV_Eternal~Runecraft~Minion~3~2~3~None~Academic Archmage~Battlecry"
    requireTarget, keyWord, description = True, "", "Fanfare: Deal 1 damage to an enemy follower and then 1 damage to the enemy leader. If you have 20 cards or less in your deck, deal 3 damage instead."
    attackAdd, healthAdd = 2, 2
    name_CN = "博学的魔导士"


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


class XenoIfrit_Crystallize(Amulet):
    Class, race, name = "Runecraft", "", "Crystallize: Xeno Ifrit"
    mana = 3
    index = "SV_Eternal~Runecraft~Amulet~3~None~Xeno Ifrit~Countdown~Crystallize~Deathrattle~Legendary~Uncollectible"
    requireTarget, description = False, "Countdown (5)Once on each of your turns, when you play a follower, give it +1/+0.At the start of your turn, if you have more evolution points than your opponent, subtract 1 from this amulet's Countdown. (You have 0 evolution points on turns you are unable to evolve.)Last Words: Summon a Xeno Ifrit."
    name_CN = "结晶：异种·伊芙利特"


class XenoIfrit(SVMinion):
    Class, race, name = "Runecraft", "", "Xeno Ifrit"
    mana, attack, health = 6, 5, 4
    index = "SV_Eternal~Runecraft~Minion~6~5~4~None~Xeno Ifrit~Crystallize~Legendary"
    requireTarget, keyWord, description = False, "", "Crystallize (3): Countdown (5)Once on each of your turns, when you play a follower, give it +1/+0.At the start of your turn, if you have more evolution points than your opponent, subtract 1 from this amulet's Countdown. (You have 0 evolution points on turns you are unable to evolve.)Last Words: Summon a Xeno Ifrit.When this follower comes into play, deal 3 damage to all enemies."
    crystallizeAmulet = XenoIfrit_Crystallize
    attackAdd, healthAdd = 2, 2
    name_CN = "异种·伊芙利特"


class PholiaRetiredSovereign(SVMinion):
    Class, race, name = "Runecraft", "", "Pholia, Retired Sovereign"
    mana, attack, health = 7, 4, 4
    index = "SV_Eternal~Runecraft~Minion~7~4~4~None~Pholia, Retired Sovereign~Battlecry"
    requireTarget, keyWord, description = False, "", "Fanfare: The next time this follower takes damage, reduce that damage to 0. Summon a Bai Ze."
    attackAdd, healthAdd = 2, 2
    name_CN = "悠闲隐居的前国王·芙莉亚"


class BaiZe(SVMinion):
    Class, race, name = "Runecraft", "", "Bai Ze"
    mana, attack, health = 7, 4, 6
    index = "SV_Eternal~Runecraft~Minion~7~4~6~None~Bai Ze~Rush~Taunt~Uncollectible"
    requireTarget, keyWord, description = False, "Rush,Taunt", "Rush.Ward.At the end of your turn, give all allied Pholia, Retired Sovereigns the following effect: The next time this follower takes damage, reduce that damage to 0."
    attackAdd, healthAdd = 2, 2
    name_CN = "白泽"


class RagingGolem_Crystallize(Amulet):
    Class, race, name = "Runecraft", "", "Crystallize: Raging Golem"
    mana = 2
    index = "SV_Eternal~Runecraft~Amulet~2~Earth Sigil~Raging Golem~Crystallize~Deathrattle~Uncollectible"
    requireTarget, description = False, "Earth Sigil Last Words: Summon a Guardian Golem."
    name_CN = "结晶：暴烈巨像"


class RagingGolem(SVMinion):
    Class, race, name = "Runecraft", "", "Raging Golem"
    mana, attack, health = 8, 6, 6
    index = "SV_Eternal~Runecraft~Minion~8~6~6~None~Raging Golem~Rush~Deathrattle"
    requireTarget, keyWord, description = False, "Rush", "Crystallize (2): Earth SigilLast Words: Summon a Guardian Golem.Rush.Last Words: Summon 2 Guardian Golems."
    crystallizeAmulet = RagingGolem_Crystallize
    attackAdd, healthAdd = 2, 2
    name_CN = "暴烈巨像"


"""Dragoncraft cards"""


class DragonRearing(SVSpell):
    Class, name = "Dragoncraft", "Dragon Rearing"
    requireTarget, mana = True, 1
    index = "SV_Eternal~Dragoncraft~Spell~1~Dragon Rearing"
    description = "Give +1/+1 to an allied Dragoncraft follower.If Overflow is active for you, give +2/+2 instead and draw a card."
    name_CN = "龙之养成"


class SharkWarrior(SVMinion):
    Class, race, name = "Dragoncraft", "", "Shark Warrior"
    mana, attack, health = 2, 2, 2
    index = "SV_Eternal~Dragoncraft~Minion~2~2~2~None~Shark Warrior~Battlecry~Enhance"
    requireTarget, keyWord, description = True, "", "Fanfare: Discard a card. Restore 4 defense to your leader.Enhance (5): Gain +2/+2. Draw a card."
    attackAdd, healthAdd = 2, 2
    name_CN = "鲨鱼战士"


class MermaidArcher(SVMinion):
    Class, race, name = "Dragoncraft", "", "Mermaid Archer"
    mana, attack, health = 2, 0, 5
    index = "SV_Eternal~Dragoncraft~Minion~2~0~5~None~Mermaid Archer~Battlecry~Enhance"
    requireTarget, keyWord, description = False, "", "Once each turn, when this follower takes damage, if it's not destroyed, deal 2 damage to a random enemy follower."
    attackAdd, healthAdd = 2, 2
    name_CN = "人鱼弓手"


class HypersonicDragonewt(SVMinion):
    Class, race, name = "Dragoncraft", "", "Hypersonic Dragonewt"
    mana, attack, health = 4, 3, 2
    index = "SV_Eternal~Dragoncraft~Minion~4~3~2~None~Hypersonic Dragonewt~Charge~Battlecry"
    requireTarget, keyWord, description = False, "Charge", "Storm. Fanfare: If Overflow is active for you, gain Last Words - Summon a Hypersonic Dragonewt."
    attackAdd, healthAdd = 2, 2
    name_CN = "残影龙人"


class GiantBasilisk(SVMinion):
    Class, race, name = "Dragoncraft", "", "Hypersonic Dragonewt"
    mana, attack, health = 4, 4, 4
    index = "SV_Eternal~Dragoncraft~Minion~4~4~4~None~Hypersonic Dragonewt~Bane~Battlecry"
    requireTarget, keyWord, description = False, "Bane", "Bane. Fanfare: If you discarded any cards this turn, evolve this card."
    attackAdd, healthAdd = 2, 2
    name_CN = "巨型巴西利斯克"


class RaziaVengefulCannonlancer(SVMinion):
    Class, race, name = "Dragoncraft", "", "Razia, Vengeful Cannonlancer"
    mana, attack, health = 4, 2, 4
    index = "SV_Eternal~Dragoncraft~Minion~4~2~4~None~Razia, Vengeful Cannonlancer~Taunt~Deathrattle"
    requireTarget, keyWord, description = False, "Taunt", "Ward.Clash: Gain +1/+0.Last Words: Deal X damage to the enemy leader. X equals this follower's attack."
    attackAdd, healthAdd = 2, 2
    name_CN = "破天的铳枪骑士·拉斯缇娜"


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


class LadivaChampionofLove(SVMinion):
    Class, race, name = "Dragoncraft", "", "Ladiva, Champion of Love"
    mana, attack, health = 6, 4, 6
    index = "SV_Eternal~Dragoncraft~Minion~6~4~6~None~Ladiva, Champion of Love~Battlecry"
    requireTarget, keyWord, description = False, "", "Fanfare: If any enemy followers are in play, lose 1 play point orb and evolve this follower.Clash: Give -2/-0 to the enemy follower."
    attackAdd, healthAdd = 2, 2
    name_CN = "爱之大殿堂·法斯蒂瓦"


class GhandagozaFistofRage(SVMinion):
    Class, race, name = "Dragoncraft", "", "Ghandagoza, Fist of Rage"
    mana, attack, health = 9, 8, 7
    index = "SV_Eternal~Dragoncraft~Minion~9~8~7~None~Ghandagoza, Fist of Rage~Rush"
    requireTarget, keyWord, description = False, "Rush", "Rush.Strike: Deal X damage to the enemy leader. X equals this follower's attack."
    attackAdd, healthAdd = 2, 2
    name_CN = "古今独步的大拳豪·冈达葛萨"


class DisrestanOceanHarbinger_Accelerate(SVSpell):
    Class, name = "Dragoncraft", "Disrestan, Ocean Harbinger"
    requireTarget, mana = False, 1
    index = "SV_Eternal~Dragoncraft~Spell~1~Disrestan, Ocean Harbinger~Accelerate~Legendary~Uncollectible"
    description = " Draw a card. If you have more evolution points than your opponent, summon a Megalorca. (You have 0 evolution points on turns you are unable to evolve.)"
    name_CN = "神鱼·迪斯雷斯坦"


class DisrestanOceanHarbinger(SVMinion):
    Class, race, name = "Dragoncraft", "", "Disrestan, Ocean Harbinger"
    mana, attack, health = 17, 13, 13
    index = "SV_Eternal~Dragoncraft~Minion~17~13~13~None~Disrestan, Ocean Harbinger~Battlecry~Legendary"
    requireTarget, keyWord, description = False, "", "At the end of your turn, if you have 10 play point orbs, subtract 10 from the cost of this card.Accelerate (1): Draw a card. If you have more evolution points than your opponent, summon a Megalorca. (You have 0 evolution points on turns you are unable to evolve.)Fanfare: Give -X/-X to all enemy followers. X equals your remaining play points. (Followers are destroyed when their defense drops below 1.)"
    accelerateSpell = DisrestanOceanHarbinger_Accelerate
    attackAdd, healthAdd = 2, 2
    name_CN = "神鱼·迪斯雷斯坦"


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
    "SV_Eternal~Neutral~Minion~2~2~1~None~Archangel of Remembrance~Battlecry~Enhance": ArchangelofRemembrance,
    "SV_Eternal~Neutral~Minion~3~2~3~None~Fluffy Angel~Battlecry~Deathrattle": FluffyAngel,
    "SV_Eternal~Neutral~Minion~3~2~3~None~Eugen, Stalwart Skyfarer": EugenStalwartSkyfarer,
    "SV_Eternal~Neutral~Spell~0~Gran's Resolve~Legendary~Uncollectible": GransResolve,
    "SV_Eternal~Neutral~Spell~0~Djeeta's Determination~Legendary~Uncollectible": DjeetasDetermination,
    "SV_Eternal~Neutral~Minion~5~5~5~None~Gran & Djeeta, Eternal Heroes~Charge~Legendary~Uncollectible": GranDjeetaEternalHeroes,
    "SV_Eternal~Neutral~Spell~5~On Wings of Tomorrow~Legendary": OnWingsofTomorrow,
    "SV_Eternal~Neutral~Spell~5~Bahamut, Primeval Dragon~Accelerate~Legendary~Uncollectible": BahamutPrimevalDragon_Accelerate,
    "SV_Eternal~Neutral~Minion~10~12~10~None~Bahamut, Primeval Dragon~Battlecry~Accelerate~Legendary": BahamutPrimevalDragon,

    "SV_Eternal~Forestcraft~Minion~4~3~3~None~Tweyen, Dark Huntress~Bane~Battlecry~SkyboundArt~SuperSkyboundArt~Legendary": TweyenDarkHuntress,

    "SV_Eternal~Swordcraft~Minion~2~3~1~Officer~Mirin, Samurai Dreamer~Battlecry~SkyboundArt~SuperSkyboundArt": MirinSamuraiDreamer,
    "SV_Eternal~Swordcraft~Minion~4~5~3~Commander~Seofon, Star Sword Sovereign~Battlecry~SkyboundArt~SuperSkyboundArt~Legendary": SeofonStarSwordSovereign,
    "SV_Eternal~Swordcraft~Minion~8~7~6~Officer~Eahta, God of the Blade~Rush~Battlecry~SkyboundArt~SuperSkyboundArt~Legendary": EahtaGodoftheBlade,

    "SV_Eternal~Runecraft~Minion~3~2~3~None~Fif, Prodigious Sorcerer~Battlecry~SkyboundArt~SuperSkyboundArt~Legendary": FifProdigiousSorcerer,

    "SV_Eternal~Dragoncraft~Minion~4~4~3~None~Threo, Divine Havoc~Rush~Battlecry~SkyboundArt~SuperSkyboundArt~Legendary": ThreoDivineHavoc,

    "SV_Eternal~Shadowcraft~Minion~2~1~4~None~Niyon, Mystic Musician~Stealth~Taunt~Battlecry~SkyboundArt~SuperSkyboundArt~Legendary": NiyonMysticMusician,

    "SV_Eternal~Bloodcraft~Minion~6~4~2~None~Seox, Heavenly Howl~Rush~Windfury~Battlecry~SkyboundArt~SuperSkyboundArt~Legendary": SeoxHeavenlyHowl,

    "SV_Eternal~Havencraft~Amulet~1~Battlecry~Summit Temple": SummitTemple,
    "SV_Eternal~Havencraft~Minion~2~1~1~None~Anre, the Enlightened One~Taunt~Battlecry~SkyboundArt~SuperSkyboundArt~Legendary": AnretheEnlightenedOne,
    "SV_Eternal~Havencraft~Amulet~1~None~Noa, Primal Shipwright~Countdown~Crystallize~Deathrattle~Uncollectible": NoaPrimalShipwright_Crystallize,
    "SV_Eternal~Havencraft~Minion~7~1~1~None~Noa, Primal Shipwright~Taunt~Crystallize": NoaPrimalShipwright,

    "SV_Eternal~Portalcraft~Minion~2~4~2~None~Feower, Double Blade Flash~Battlecry~SkyboundArt~SuperSkyboundArt~Legendary": FeowerDoubleBladeFlash,
    "SV_Eternal~Portalcraft~Minion~3~2~4~None~Tien, Treacherous Trigger~Battlecry~SkyboundArt~SuperSkyboundArt~Legendary": TienTreacherousTrigger,
}
