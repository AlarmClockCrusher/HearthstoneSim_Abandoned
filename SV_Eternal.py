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

    def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
        if any(amulet.name == "Summit Temple" for amulet in self.Game.amuletsonBoard(self.ID, self)):
			self.Game.killMinion(self, self)
		return None
		
class Trig_SummitTemple(TrigBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionAttacksHero", "MinionAttacksMinion"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0): #target here holds the actual target object
		return subject.ID == self.entity.ID and subject.Class == "Havencraft"
		
	def text(self, CHN):
		return "" if CHN else "When an allied Havencraft follower attacks, give it 'This follower deals damage equal to its defense until the end of this turn'"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		trig = Trig_AttUsesHealth(subject)
		subject.trigsBoard.append(trig)
		trig.connect()
		
class Trig_AttUsesHealth(TrigBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["BattleDmg?", "TurnEnds"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0): #target here holds the actual target object
		return signal[0] == 'T' or subject == self.entity
		
	def text(self, CHN):
		return "该从者给予的战斗伤害等于其生命值" if CHN else "During this turn, this follower deals damage equal to its defense when attacks"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		if signal[0] == 'T':
			try: self.entity.trigsBoard.remove(self)
			except: pass
			self.disconnect()
		else:
			number[0] = max(0, self.entity.health)
			
"""Portalcraft cards"""

"""DLC cards"""

SV_Eternal_Indices = {

}
