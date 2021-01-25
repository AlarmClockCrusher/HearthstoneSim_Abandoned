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
    index = "SV_Eternal~Forestcraft~Minion~1~1~1~None~Walder, Forest Ranger~Charge~Battlecry~Enhance"
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


"""Dragoncraft cards"""


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


"""Shadowcraft cards"""


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


"""Bloodcraft cards"""


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
