from CardTypes import *
from VariousHandlers import *
from Triggers_Auras import *
from Basic import FieryWarAxe, ExcessMana

import numpy as np
import copy

def extractfrom(target, listObject):
	temp = None
	for i in range(len(listObject)):
		if listObject[i] == target:
			temp = listObject.pop(i)
			break
	return temp
	
def fixedList(listObject):
	return listObject[0:len(listObject)]
	
def classforDiscover(initiator):
	Class = initiator.Game.heroes[initiator.ID].Class
	if Class != "Neutral": #如果发现的发起者的职业不是中立，则返回那个职业
		return Class
	elif initiator.Class != "Neutral": #如果玩家职业是中立，但卡牌职业不是中立，则发现以那个卡牌的职业进行
		return initiator.Class
	else: #如果玩家职业和卡牌职业都是中立，则随机选取一个职业进行发现。
		return np.random.choice(Classes)
		
def PRINT(obj, string, *args):
	if hasattr(obj, "GUI"):
		GUI = obj.GUI
	elif hasattr(obj, "Game"):
		GUI = obj.Game.GUI
	elif hasattr(obj, "entity"):
		GUI = obj.entity.Game.GUI
	else:
		GUI = None
	if GUI != None:
		GUI.printInfo(string)
	else:
		print(string)
		
Classes = ["Demon Hunter", "Druid", "Hunter", "Mage", "Paladin", "Priest", "Rogue", "Shaman", "Warlock", "Warrior"]
ClassesandNeutral = ["Demon Hunter", "Druid", "Hunter", "Mage", "Paladin", "Priest", "Rogue", "Shaman", "Warlock", "Warrior", "Neutral"]

"""Ashes of Outlands expansion"""
#休眠的随从在打出之后2回合本来时会触发你“召唤一张随从”
class Minion_Dormantfor2turns(Minion):
	Class, race, name = "Neutral", "", "Imprisoned Vanilla"
	mana, attack, health = 5, 5, 5
	index = "Vanilla~Neutral~Minion~5~5~5~None~Imprisoned Vanilla"
	requireTarget, keyWord, description = False, "", "Dormant for 2 turns. When this awakens, do something"
	
	def appears(self):
		PRINT(self, "%s appears on board"%self.name)
		self.newonthisSide = True
		self.onBoard, self.inHand, self.inDeck = True, False, False
		self.dead = False
		self.mana = type(self).mana #Restore the minion's mana to original value.
		self.decideAttChances_base() #Decide base att chances, given Windfury and Mega Windfury
		#没有光环，目前炉石没有给随从人为添加光环的效果, 不可能在把手牌中获得的扳机带入场上，因为会在变形中丢失
		#The buffAuras/hasAuras will react to this signal.
		if self.firstTimeonBoard: #用activated来标记随从能否出现在场上而不休眠，第一次出现时，activated为False
			#假设第一次出现时，会进入休眠状态，生成的Permanent不保存这个初始随从
			PRINT(self, "%a starts as a Permanent"%self.name)
			self.Game.transform(self, ImprisonedDormantForm(self.Game, self.ID, self))
		else: #只有不是第一次出现在场上时才会执行这些函数
			for value in self.auras.values():
				value.auraAppears()
			#随从入场时将注册其场上扳机和亡语扳机
			for trigger in self.triggersonBoard + self.deathrattles:
				trigger.connect() #把(obj, signal)放入Game.triggersonBoard中
			#Mainly mana aura minions, e.g. Sorcerer's Apprentice.
			for func in self.appearResponse:
				func()
			#The buffAuras/hasAuras will react to this signal.
			self.Game.sendSignal("MinionAppears", self.ID, self, None, 0, "")
			for func in self.triggers["StatChanges"]: #For Lightspawn and Paragon of Light
				func()
				
	def awakenEffect(self):
		pass
		
class ImprisonedDormantForm(Permanent):
	Class, name = "Neutral", "Imprisoned Vanilla"
	description = "Awakens after 2 turns"
	def __init__(self, Game, ID, originalMinion):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_ImprisonedDormantForm(self)]
		self.originalMinion = originalMinion
		self.progress = 0
		self.Class = self.originalMinion.Class
		self.name = "Dormant " + self.originalMinion.name
		self.description = self.originalMinion.description
		
class Trigger_ImprisonedDormantForm(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["TurnStarts"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and ID == self.entity.ID #会在我方回合开始时进行苏醒
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.progress += 1
		PRINT(self, "At the start of turn, %s records the turns that have passed %d"%(self.entity.name, self.entity.progress))
		if self.entity.progress > 1:
			PRINT(self, "%s awakens and triggers its effect"%self.entity.name)
			#假设唤醒的Imprisoned Vanilla可以携带buff
			originalMinion = self.entity.originalMinion
			originalMinion.firstTimeonBoard = False
			self.entity.Game.transform(self.entity, originalMinion)
			if hasattr(originalMinion, "awakenEffect"):
				originalMinion.awakenEffect()
				
				
				
class Minion_DormantuntilTrig(Minion):
	Class, race, name = "Neutral", "", "Dormant to be awakened"
	mana, attack, health = 4, 4, 4
	index = "Vanilla~Neutral~Minion~5~5~5~None~Dormant to be awakened"
	requireTarget, keyWord, description = False, "", "Dormant to be awakened by something"
	
	def appears(self):
		PRINT(self, "%s appears on board."%self.name)
		self.newonthisSide = True
		self.onBoard, self.inHand, self.inDeck = True, False, False
		self.dead = False
		self.mana = type(self).mana #Restore the minion's mana to original value.
		self.decideAttChances_base() #Decide base att chances, given Windfury and Mega Windfury
		#没有光环，目前炉石没有给随从人为添加光环的效果, 不可能在把手牌中获得的扳机带入场上，因为会在变形中丢失
		#The buffAuras/hasAuras will react to this signal.
		if self.firstTimeonBoard: #用activated来标记随从能否出现在场上而不休眠，第一次出现时，activated为False
			#假设第一次出现时，会进入休眠状态，生成的Permanent不会保存这个初始随从
			PRINT(self, "%s starts as a Permanent"%self.name)
			#pos, identity = self.position, self.identity
			#self.__init__(self.Game, self.ID)
			#self.position = pos
			#self.identity[0], self.identity[1] = identity[0], identity[1]
			self.Game.transform(self, self.dormantForm(self.Game, self.ID))
		else: #只有不是第一次出现在场上时才会执行这些函数
			for value in self.auras.values():
				value.auraAppears()
			#随从入场时将注册其场上扳机和亡语扳机
			for trigger in self.triggersonBoard + self.deathrattles:
				trigger.connect() #把(obj, signal)放入Game.triggersonBoard中
			#Mainly mana aura minions, e.g. Sorcerer's Apprentice.
			for func in self.appearResponse:
				func()
			#The buffAuras/hasAuras will react to this signal.
			self.Game.sendSignal("MinionAppears", self.ID, self, None, 0, "")
			for func in self.triggers["StatChanges"]: #For Lightspawn and Paragon of Light
				func()
				
				
"""Mana 1 cards"""
class EtherealAugmerchant(Minion):
	Class, race, name = "Neutral", "", "Ethereal Augmerchant"
	mana, attack, health = 1, 2, 1
	index = "Outlands~Neutral~Minion~1~2~1~None~Ethereal Augmerchant~Battlecry"
	requireTarget, keyWord, description = True, "", "Battlecry: Deal 1 damage to a minion and give it Spell Damage +1"
	def targetExists(self, choice=0):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target != self and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		#需要随从在场并且还是随从形态
		if target != None and (target.onBoard or target.inHand):
			PRINT(self, "Ethereal Augmerchant's battlecry deals 1 damage to minion %s and gives it Spell Damage +1"%target.name)
			self.dealsDamage(target, 1)
			target.getsKeyword("Spell Damage")
		return target
		
		
class GuardianAugmerchant(Minion):
	Class, race, name = "Neutral", "", "Guardian Augmerchant"
	mana, attack, health = 1, 2, 1
	index = "Outlands~Neutral~Minion~1~2~1~None~Guardian Augmerchant~Battlecry"
	requireTarget, keyWord, description = True, "", "Battlecry: Deal 1 damage to a minion and give it Divine Shield"
	def targetExists(self, choice=0):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target != self and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if target != None and (target.onBoard or target.inHand):
			PRINT(self, "Guardian Augmerchant's battlecry deals 1 damage to minion %s and gives it Divine Shield"%target.name)
			self.dealsDamage(target, 1)
			target.getsKeyword("Divine Shield")
		return target
		
		
class InfectiousSporeling(Minion):
	Class, race, name = "Neutral", "", "Infectious Sporeling"
	mana, attack, health = 1, 1, 2
	index = "Outlands~Neutral~Minion~1~1~2~None~Infectious Sporeling"
	requireTarget, keyWord, description = False, "", "After this damages a minion, turn it into an Infectious Sporeling"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_InfectiousSporeling(self)]
		
class Trigger_InfectiousSporeling(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionTookDamage"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject == self.entity and target.onBoard and target.health > 0 and target.dead == False
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self, "%s damaged minion %s and turns it into an Infectious Sporeling"%(self.entity.name, target.name))
		self.entity.Game.transform(target, InfectiousSporeling(self.entity.Game, target.ID))
		
		
class RocketAugmerchant(Minion):
	Class, race, name = "Neutral", "", "Rocket Augmerchant"
	mana, attack, health = 1, 2, 1
	index = "Outlands~Neutral~Minion~1~2~1~None~Rocket Augmerchant~Battlecry"
	requireTarget, keyWord, description = True, "", "Battlecry: Deal 1 damage to a minion and give it Rush"
	def targetExists(self, choice=0):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target != self and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if target != None and (target.onBoard or target.inHand):
			PRINT(self, "Rocket Augmerchant's battlecry deals 1 damage to minion %s and gives it Divine Shield"%target.name)
			self.dealsDamage(target, 1)
			target.getsKeyword("Rush")
		return target
		
		
class SoulboundAshtongue(Minion):
	Class, race, name = "Neutral", "", "Soulbound Ashtongue"
	mana, attack, health = 1, 1, 4
	index = "Outlands~Neutral~Minion~1~1~4~None~Soulbound Ashtongue"
	requireTarget, keyWord, description = False, "", "Whenever this minion takes damage, also deal that amount to your hero"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_SoulboundAshtongue(self)]
		
class Trigger_SoulboundAshtongue(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionTakesDamage"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return target == self.entity
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self, "%s takes %d damage and deals equal amount of damage to the player"%(self.entity.name, number))
		self.entity.dealsDamage(self.entity.Game.heroes[self.entity.ID], number)
		
		
"""Mana 2 cards"""
class BonechewerBrawler(Minion):
	Class, race, name = "Neutral", "", "Bonechewer Brawler"
	mana, attack, health = 2, 2, 3
	index = "Outlands~Neutral~Minion~2~2~3~None~Bonechewer Brawler~Taunt"
	requireTarget, keyWord, description = False, "Taunt", "Taunt. Whenever this minion takes damage, gain +2 Attack"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_BonechewerBrawler(self)]
		
class Trigger_BonechewerBrawler(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionTakesDamage"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return target == self.entity and self.entity.onBoard
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self, "%s takes Damage and gains +2 Attack."%self.entity.name)
		self.entity.buffDebuff(2, 0)
		
		
class ImprisonedVilefiend(Minion_Dormantfor2turns):
	Class, race, name = "Neutral", "Demon", "Imprisoned Vilefiend"
	mana, attack, health = 2, 3, 5
	index = "Outlands~Neutral~Minion~2~3~5~Demon~Imprisoned Vilefiend~Rush"
	requireTarget, keyWord, description = False, "Rush", "Dormant for 2 turns. Rush"
	
	
class MoargArtificer(Minion):
	Class, race, name = "Neutral", "Demon", "Mo'arg Artificer"
	mana, attack, health = 2, 2, 4
	index = "Outlands~Neutral~Minion~2~2~4~Demon~Mo'arg Artificer"
	requireTarget, keyWord, description = False, "", "All minions take double damage from spells"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_MoargArtificer(self)]
		
class Trigger_MoargArtificer(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionAbouttoTakeDamage"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and target.cardType == "Minion" and subject.cardType == "Spell" and number[0] > 0
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self, "The %d damage dealt by spell %s on minion %s is doubled by %s"%(number[0], subject.name, target.name, self.entity.name))
		number[0] += number[0]
		
		
class RustswornInitiate(Minion):
	Class, race, name = "Neutral", "", "Rustsworn Initiate"
	mana, attack, health = 2, 2, 2
	index = "Outlands~Neutral~Minion~2~2~2~None~Rustsworn Initiate~Deathrattle"
	requireTarget, keyWord, description = False, "", "Deathrattle: Summon a 1/1 Impcaster with Spell Damage +1"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [SummonanImpcastwithSpellDamagePlus1(self)]
		
class SummonanImpcastwithSpellDamagePlus1(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self, "Deathrattle: Summon a 1/1 Impcaster with Spell Damage +1 triggers")
		self.entity.Game.summonMinion(Impcaster(self.entity.Game, self.entity.ID), self.entity.position+1, self.entity.ID)	
		
class Impcaster(Minion):
	Class, race, name = "Neutral", "Demon", "Impcaster"
	mana, attack, health = 1, 1, 1
	index = "Outlands~Neutral~Minion~1~1~1~Demon~Impcaster~Spell Damage~Uncollectible"
	requireTarget, keyWord, description = False, "Spell Damage", "Spell Damage +1"
	
"""Mana 3 cards"""
class BlisteringRot(Minion):
	Class, race, name = "Neutral", "", "Blistering Rot"
	mana, attack, health = 3, 1, 2
	index = "Outlands~Neutral~Minion~3~1~2~None~Blistering Rot"
	requireTarget, keyWord, description = False, "", "At the end of your turn, summon a Rot with stats equal to this minion's"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_BlisteringRot(self)]
		
class Trigger_BlisteringRot(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["TurnEnds"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and ID == self.entity.ID and self.entity.health > 0
	#假设召唤的Rot只是一个1/1，然后接受buff.而且该随从生命值低于1时不能触发
	#假设攻击力为负数时，召唤物的攻击力为0
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self, "At the start of turn, %s summons a Rot with equal stats"%self.entity.name)
		minion = LivingRot(self.entity.Game, self.entity.ID)
		if self.entity.Game.summonMinion(minion, self.entity.position+1, self.entity.ID):
			minion.statReset(max(0, self.entity.attack), self.entity.health)
			
class LivingRot(Minion):
	Class, race, name = "Neutral", "", "Living Rot"
	mana, attack, health = 1, 1, 1
	index = "Outlands~Neutral~Minion~1~1~1~None~Living Rot~Uncollectible"
	requireTarget, keyWord, description = False, "", ""
	
	
class FrozenShadoweaver(Minion):
	Class, race, name = "Neutral", "", "Frozen Shadoweaver"
	mana, attack, health = 3, 4, 3
	index = "Outlands~Neutral~Minion~3~4~3~None~Frozen Shadoweaver~Battlecry"
	requireTarget, keyWord, description = True, "", "Battlecry: Freeze an enemy"
	def targetExists(self, choice=0):
		return self.selectableEnemyMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return (target.cardType == "Minion" or target.cardType == "Hero") and target.ID != self.ID and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if target != None:
			PRINT(self, "Frozen Shadoweaver's battlecry Freezes enemy %s"%target.name)
			target.getsFrozen()
		return target
		
		
class OverconfidentOrc(Minion):
	Class, race, name = "Neutral", "", "Overconfident Orc"
	mana, attack, health = 3, 1, 6
	index = "Outlands~Neutral~Minion~3~1~6~None~Overconfident Orc~Taunt"
	requireTarget, keyWord, description = False, "Taunt", "Taunt. While at full Health, this has +2 Attack"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggers["StatChanges"] = [self.handleAttack]
		self.activated = False
		
	def handleAttack(self):
		if self.silenced == False and self.onBoard:
			if self.activated == False and self.health >= self.health_upper:
				self.activated = True
				self.statChange(2, 0)
				self.stat_AuraAffected[0] += 2
			elif self.activated and self.health < self.health_upper:
				self.activated = False
				self.statChange(-2, 0)
				self.stat_AuraAffected[0] -= 2
				
				
class TerrorguardEscapee(Minion):
	Class, race, name = "Neutral", "Demon", "Terrorguard Escapee"
	mana, attack, health = 3, 3, 7
	index = "Outlands~Neutral~Minion~3~3~7~Demon~Terrorguard Escapee~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Summon three 1/1 Huntresses for your opponent"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		PRINT(self, "Terrorguard Escapee's battlecry summons three 1/1 Huntresses for the opponent")
		self.Game.summonMinion([Huntress(self.Game, 3-self.ID) for i in range(3)], (-1, "totheRightEnd"), self.ID)
		return None
		
class Huntress(Minion):
	Class, race, name = "Neutral", "", "Huntress"
	mana, attack, health = 1, 1, 1
	index = "Outlands~Neutral~Minion~1~1~1~None~Huntress~Uncollectible"
	requireTarget, keyWord, description = False, "", ""
	
	
class TeronGorefiend(Minion):
	Class, race, name = "Neutral", "", "Teron Gorefiend"
	mana, attack, health = 3, 3, 4
	index = "Outlands~Neutral~Minion~3~3~4~None~Teron Gorefiend~Battlecry~Deathrattle~Legendary"
	requireTarget, keyWord, description = False, "", "Battlecry: Destroy all friendly minions. Deathrattle: Resummon all of them with +1/+1"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [ResummonDestroyedMinionwithPlus1Plus1(self)]
	#不知道两次触发战吼时亡语是否会记录两份，假设会
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		PRINT(self, "Teron Gorefiend's battlecry destroys all friendly minions.")
		minionsDestroyed = []
		for minion in self.Game.minionsonBoard(self.ID):
			if minion != self:
				minion.dead = True
				minionsDestroyed.append(type(minion))
		if minionsDestroyed != []:
			for trigger in self.deathrattles:
				if type(trigger) == ResummonDestroyedMinionwithPlus1Plus1:
					trigger.minionsDestroyed += minionsDestroyed
		return None
		
class ResummonDestroyedMinionwithPlus1Plus1(Deathrattle_Minion):
	def __init__(self, entity):
		self.blank_init(entity)
		self.minionsDestroyed = []
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		if self.minionsDestroyed != []:
			PRINT(self, "Deathrattle: Resummon all destroyed minions with +1/+1 triggers")
			pos = (self.entity.position, "totheRight") if self.entity in self.entity.Game.minions[self.entity.ID] else (-1, "totheRightEnd")
			minions = [minion(self.entity.Game, self.entity.ID) for minion in self.minionsDestroyed]
			#假设给予+1/+1是在召唤之前
			for minion in minions:
				minion.attack += 1
				minion.attack_Enchant += 1
				minion.health += 1
				minion.health_Enchant += 1
			self.entity.Game.summonMinion(minions, pos, self.entity.ID)
			
	def selfCopy(self, recipientMinion):
		trigger = type(self)(recipientMinion)
		trigger.minionsDestroyed = self.minionsDestroyed
		return trigger
		
		
"""Mana 4 cards"""
class BurrowingScorpid(Minion):
	Class, race, name = "Neutral", "Beast", "Burrowing Scorpid"
	mana, attack, health = 4, 5, 2
	index = "Outlands~Neutral~Minion~4~5~2~Beast~Burrowing Scorpid~Battlecry"
	requireTarget, keyWord, description = True, "", "Battlecry: Deal 2 damage. If that kills the target, gain Stealth"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if target != None:
			PRINT(self, "Burrowing Scorpid's battlecry deals 2 damage to %s"%target.name)
			self.dealsDamage(target, 2)
			if target.health < 1 or target.dead == True:
				PRINT(self, "Burrowing Scorpid's battlecry kills the target and gives the minion Stealth")
				self.getsKeyword("Stealth")
		return target
		
		
class DisguisedWanderer(Minion):
	Class, race, name = "Neutral", "Demon", "Disguised Wanderer"
	mana, attack, health = 4, 3, 3
	index = "Outlands~Neutral~Minion~4~3~3~Demon~Disguised Wanderer~Deathrattle"
	requireTarget, keyWord, description = False, "", "Deathrattle: Summon a 9/1 Inquisitor"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [SummonanInquisitor(self)]
		
class SummonanInquisitor(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self, "Deathrattle: Summon a 9/1 Inquisitor triggers")
		self.entity.Game.summonMinion(RustswornInquisitor(self.entity.Game, self.entity.ID), self.entity.position+1, self.entity.ID)	
		
class RustswornInquisitor(Minion):
	Class, race, name = "Neutral", "Demon", "Rustsworn Inquisitor"
	mana, attack, health = 4, 9, 1
	index = "Outlands~Neutral~Minion~4~9~1~Demon~Rustsworn Inquisitor~Uncollectible"
	requireTarget, keyWord, description = False, "", ""
	
	
class FelfinNavigator(Minion):
	Class, race, name = "Neutral", "Murloc", "Felfin Navigator"
	mana, attack, health = 4, 4, 4
	index = "Outlands~Neutral~Minion~4~4~4~Murloc~Felfin Navigator~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Give your other Murlocs +1/+1"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		PRINT(self, "Felfin Navigator's battlecry gives all other friendly Murlocs +1/+1")
		for minion in fixedList(self.Game.minionsonBoard(self.ID)):
			if minion != self and "Murloc" in minion.race:
				minion.buffDebuff(1, 1)
		return None
		
		
class Magtheridon(Minion_DormantuntilTrig):
	Class, race, name = "Neutral", "Demon", "Magtheridon"
	mana, attack, health = 4, 12, 12
	index = "Outlands~Neutral~Minion~4~12~12~Demon~Magtheridon~Battlecry~Legendary"
	requireTarget, keyWord, description = False, "", "Dormant. Battlecry: Summon three 1/3 enemy Warders. When they die, destroy all minions and awaken"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.dormantForm = Magtheridon_Dormant
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		PRINT(self, "Magtheridon's battlecry summons three 1/3 enemy Warders")
		self.Game.summonMinion([HellfireWarder(self.Game, 3-self.ID) for i in range(3)], (-1, "totheRightEnd"), self.ID)
		return None
		
class Magtheridon_Dormant(Permanent):
	Class, name = "Neutral", "Dormant Magtheridon"
	description = "Destroy 3 Warders to destroy all minions and awaken this"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.progress = 0
		self.triggersonBoard = [Trigger_Magtheridon_Dormant(self)]
		self.originalMinion = Magtheridon
		
class Trigger_Magtheridon_Dormant(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionDies"]) #假设是死亡时扳机，而还是死亡后扳机
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and type(target) == HellfireWarder and target.ID != self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self, "A Warder summoned dies. Magtheridon awakening progress: %d"%self.entity.progress)
		self.entity.progress += 1
		if self.entity.progress > 2:
			PRINT(self, "3 Warders died. Dormant Magtheridon destroys all minions and awakens")
			for minion in self.entity.Game.minionsonBoard(1) + self.entity.Game.minionsonBoard(2):
				minion.dead = True
			#假设不进行强制死亡
			minion = Magtheridon(self.entity.Game, self.entity.ID)
			minion.firstTimeonBoard = False
			self.entity.Game.transform(self.entity, minion)
			
class HellfireWarder(Minion):
	Class, race, name = "Neutral", "", "Hellfire Warder"
	mana, attack, health = 1, 1, 3
	index = "Outlands~Neutral~Minion~1~1~3~None~Hellfire Warder~Uncollectible"
	requireTarget, keyWord, description = False, "", "(Magtheridon will destroy all minions and awaken after 3 Warders die)"
	
	
class MaievShadowsong(Minion):
	Class, race, name = "Neutral", "", "Maiev Shadowsong"
	mana, attack, health = 4, 4, 3
	index = "Outlands~Neutral~Minion~4~4~3~None~Maiev Shadowsong~Battlecry~Legendary"
	requireTarget, keyWord, description = True, "", "Battlecry: Choose a minion. It goes Dormant for 2 turns"
	def targetExists(self, choice=0):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target != self and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		#需要随从在场并且还是随从形态
		if target != None and target.onBoard and target.cardType == "Minion":
			PRINT(self, "Maiev Shadowsong's battlecry lets minion %s go Dormant for 2 turns"%target.name)
			dormantForm = ImprisonedDormantForm(self.Game, target.ID, target) #假设让随从休眠可以保留其初始状态
			self.Game.transform(target, dormantForm)
		return dormantForm
		
		
class Replicatotron(Minion):
	Class, race, name = "Neutral", "Mech", "Replicat-o-tron"
	mana, attack, health = 4, 3, 3
	index = "Outlands~Neutral~Minion~4~3~3~Mech~Replicat-o-tron"
	requireTarget, keyWord, description = False, "", "At the end of your turn, transform a neighbor into a copy of this"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_Replicatotron(self)]
		
class Trigger_Replicatotron(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["TurnEnds"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		adjacentMinions, distribution = self.entity.Game.findAdjacentMinions(self.entity)
		if adjacentMinions != []:
			minion = np.random.choice(adjacentMinions)
			Copy = self.entity.selfCopy(self.entity.ID)
			PRINT(self, "At the start of turn, %s transforms its neighbor %s into a copy of it"%(self.entity.name, minion.name))
			self.entity.Game.transform(minion, Copy)
			
			
class RustswornCultist(Minion):
	Class, race, name = "Neutral", "", "Rustsworn Cultist"
	mana, attack, health = 4, 3, 3
	index = "Outlands~Neutral~Minion~4~3~3~None~Rustsworn Cultist~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Give your other minions 'Deathrattle: Summon a 1/1 Demon'"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		PRINT(self, "Rustsworn Cultist's battlecry gives all other friendly minions 'Deathrattle: Summon a 1/1 Demon'")
		for minion in self.Game.minionsonBoard(self.ID):
			trigger = SummonaRustedDevil(minion)
			minion.deathrattles.append(trigger)
			trigger.connect()
		return None
		
class SummonaRustedDevil(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		#This Deathrattle can't possibly be triggered in hand
		PRINT(self, "Deathrattle: Resummon a 1/1 Demon triggers.")
		self.entity.Game.summonMinion(RustedDevil(self.entity.Game, self.entity.ID), self.entity.position+1, self.entity.ID)
		
class RustedDevil(Minion):
	Class, race, name = "Neutral", "", "Rusted Devil"
	mana, attack, health = 1, 1, 1
	index = "Outlands~Neutral~Minion~1~1~1~None~Rusted Devil~Uncollectible"
	requireTarget, keyWord, description = False, "", ""
	
	
"""Mana 5 cards"""
class Alar(Minion):
	Class, race, name = "Neutral", "Elemental", "Al'ar"
	mana, attack, health = 5, 7, 3
	index = "Outlands~Neutral~Minion~5~7~3~Elemental~Al'ar~Deathrattle~Legendary"
	requireTarget, keyWord, description = False, "", "Deathrattle: Summon a 0/3 Ashes of Al'ar that resurrects this minion on your next turn"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [SummonAshesofAlar(self)]
		
class SummonAshesofAlar(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self, "Deathrattle: Summon a 0/3 Ashes of Al'ar that resurrects Al'ar on player's next turn triggers")
		self.entity.Game.summonMinion(AshesofAlar(self.entity.Game, self.entity.ID), self.entity.position+1, self.entity.ID)
		
class AshesofAlar(Minion):
	Class, race, name = "Neutral", "", "Ashes of Al'ar"
	mana, attack, health = 1, 0, 3
	index = "Outlands~Neutral~Minion~1~0~3~None~Ashes of Al'ar~Legendary~Uncollectible"
	requireTarget, keyWord, description = False, "", "At the start of your turn, transform this into Al'ar"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_AshesofAlar(self)]
		
class Trigger_AshesofAlar(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["TurnStarts"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self, "At the start of turn, %s transforms into Al'ar"%self.entity.name)
		self.entity.Game.transform(self.entity, Alar(self.entity.Game, self.entity.ID))
		
		
class RuststeedRaider(Minion):
	Class, race, name = "Neutral", "", "Ruststeed Raider"
	mana, attack, health = 5, 1, 8
	index = "Outlands~Neutral~Minion~5~1~8~None~Ruststeed Raider~Taunt~Rush~Battlecry"
	requireTarget, keyWord, description = False, "Taunt,Rush", "Taunt, Rush. Battlecry: Gain +4 Attack this turn"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		PRINT(self, "Ruststeed Raider's battlecry gives the minion +4 Attack this turn")
		self.buffDebuff(4, 0, "EndofTurn")
		return None
		
		
class WasteWarden(Minion):
	Class, race, name = "Neutral", "", "Waste Warden"
	mana, attack, health = 5, 3, 3
	index = "Outlands~Neutral~Minion~5~3~3~None~Waste Warden~Battlecry"
	requireTarget, keyWord, description = True, "", "Battlecry: Deal 3 damage to a minion and all others of the same minion type"
	
	def targetExists(self, choice=0):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.race != "" and target.onBoard
		
	#假设指定梦魇融合怪的时候会把场上所有有种族的随从都打一遍
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if target != None:
			PRINT(self, "Waste Warden's battlecry deals 3 damage to %s"%target.name)
			if target.race == "":
				self.dealsDamage(target, 3)
			else: #Minion has type
				minionsoftheSameType = [target] #不重复计算目标和对一个随从的伤害
				for race in target.race.split(','):
					for minion in self.Game.minionsonBoard(1) + self.Game.minionsonBoard(2):
						if race in minion.race and minion != target and minion not in minionsoftheSameType:
							minionsoftheSameType.append(minion)
				self.dealsAOE(minionsoftheSameType, [3 for minion in minionsoftheSameType])
		return target
		
		
"""Mana 6 cards"""
class DragonmawSkyStalker(Minion):
	Class, race, name = "Neutral", "Dragon", "Dragonmaw Sky Stalker"
	mana, attack, health = 6, 5, 6
	index = "Outlands~Neutral~Minion~6~5~6~Dragon~Dragonmaw Sky Stalker~Deathrattle"
	requireTarget, keyWord, description = False, "", "Deathrattle: Summon a 3/4 Dragonrider"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [SummonaDragonrider(self)]
		
class SummonaDragonrider(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self, "Deathrattle: Summon a 3/4 Dragonrider triggers")
		self.entity.Game.summonMinion(Dragonrider(self.entity.Game, self.entity.ID), self.entity.position+1, self.entity.ID)
		
class Dragonrider(Minion):
	Class, race, name = "Neutral", "", "Dragonrider"
	mana, attack, health = 3, 3, 4
	index = "Outlands~Neutral~Minion~3~3~4~Dragon~Dragonrider~Uncollectible"
	requireTarget, keyWord, description = False, "", ""
	
	
class KaelthasSunstrider(Minion):
	Class, race, name = "Neutral", "", "Kael'thas Sunstrider"
	mana, attack, health = 6, 4, 7
	index = "Outlands~Neutral~Minion~6~4~7~None~Kael'thas Sunstrider~Legendary"
	requireTarget, keyWord, description = False, "", "Every third spell you cast each turn costs (0)"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.auras["Mana Aura"] = ManaAura_Dealer(self, self.manaAuraApplicable, changeby=0, changeto=0)
		self.triggersonBoard = [Trigger_KaelthasSunstrider(self)]
		#随从的光环启动在顺序上早于appearResponse,关闭同样早于disappearResponse
		self.appearResponse = [self.checkAuraCorrectness]
		self.disappearResponse = [self.deactivateAura]
		self.silenceResponse = [self.deactivateAura]
		
	def manaAuraApplicable(self, subject):
		return subject.ID == self.ID and subject.cardType == "Spell"
		
	def checkAuraCorrectness(self): #负责光环在随从登场时无条件启动之后的检测。如果光环的启动条件并没有达成，则关掉光环
		if self.Game.turn != self.ID or self.Game.CounterHandler.numSpellsPlayedThisTurn[self.ID] % 3 != 2:
			PRINT(self, "Kael'thas Sunstrider's mana aura is incorrectly activated. It will be shut down")
			self.auras["Mana Aura"].auraDisappears()
			
	def deactivateAura(self):
		PRINT(self, "Kael'thas Sunstrider's mana aura is removed. Player's third spell each turn no longer costs (0).")
		self.auras["Mana Aura"].auraDisappears()
		
#不知道之前法术被反制之后是否会计为打出的牌.假设不会计入计数器中
class Trigger_KaelthasSunstrider(TriggeronBoard):
	def __init__(self, entity): #以我方打出一张法术之后来启动给每回合第三张法术的光环
		self.blank_init(entity, ["SpellBeenPlayed", "TurnEnds", "ManaCostPaid"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		if signal == "TurnEnds" and self.entity.onBoard:
			return True
		if (signal == "ManaCostPaid" or signal == "SpellBeenPlayed") and self.entity.onBoard and subject.cardType == "Spell" and subject.ID == self.entity.ID:
			return True
		return False
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		if signal == "TurnEnds":
			PRINT(self, "At the end of turn, %s shuts its Mana Aura down."%self.entity.name)
			self.entity.auras["Mana Aura"].auraDisappears()
		elif signal == "SpellBeenPlayed":
			if self.entity.Game.CounterHandler.numSpellsPlayedThisTurn[self.entity.ID] % 3 == 2:
				self.entity.auras["Mana Aura"].auraAppears()
		else: #signal == "ManaCostPaid"
			self.entity.auras["Mana Aura"].auraDisappears()
			
			
class ScavengingShivarra(Minion):
	Class, race, name = "Neutral", "Demon", "Scavenging Shivarra"
	mana, attack, health = 6, 6, 3
	index = "Outlands~Neutral~Minion~6~6~3~Demon~Scavenging Shivarra~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Deal 6 damage randomly split among all other minions"
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		PRINT(self, "Scavenging Shivarra's battlecry deals 6 damage randomly split among other minions.")
		for i in range(6):
			targets = self.Game.minionsAlive(1, self) + self.Game.minionsAlive(2, self)
			if targets != []:
				target = np.random.choice(targets)
				PRINT(self, "Scavenging Shivarra's battlecry deals 1 damage to %s"%target.name)
				self.dealsDamage(target, 1)
			else:
				break
		return None
		
		
class BonechewerVanguard(Minion):
	Class, race, name = "Neutral", "", "Bonechewer Vanguard"
	mana, attack, health = 7, 4, 10
	index = "Outlands~Neutral~Minion~7~4~10~None~Bonechewer Vanguard~Taunt"
	requireTarget, keyWord, description = False, "Taunt", "Taunt. Whenever this minion takes damage, gain +2 Attack"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_BonechewerVanguard(self)]
		
class Trigger_BonechewerVanguard(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionTakesDamage"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return target == self.entity and self.entity.onBoard
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self, "%s takes Damage and gains +2 Attack."%self.entity.name)
		self.entity.buffDebuff(2, 0)
		
		
class SupremeAbyssal(Minion):
	Class, race, name = "Neutral", "Demon", "Supreme Abyssal"
	mana, attack, health = 8, 12, 12
	index = "Outlands~Neutral~Minion~8~12~12~Demon~Supreme Abyssal"
	requireTarget, keyWord, description = False, "", "Can't attack heroes"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.marks["Can't Attack Hero"] = 1
		
		
class ScrapyardColossus(Minion):
	Class, race, name = "Neutral", "Elemental", "Scrapyard Colossus"
	mana, attack, health = 10, 7, 7
	index = "Outlands~Neutral~Minion~10~7~7~Elemental~Scrapyard Colossus~Taunt~Deathrattle"
	requireTarget, keyWord, description = False, "Taunt", "Taunt. Deathrattle: Summon a 7/7 Felcracked Colossus with Taunt"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [SummonaFelcrackedColossuswithTaunt(self)]
		
class SummonaFelcrackedColossuswithTaunt(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self, "Deathrattle: Summon a 7/7 Felcracked Colossus with Taunt triggers")
		self.entity.Game.summonMinion(FelcrackedColossus(self.entity.Game, self.entity.ID), self.entity.position+1, self.entity.ID)
		
class FelcrackedColossus(Minion):
	Class, race, name = "Neutral", "Elemental", "Felcracked Colossus"
	mana, attack, health = 7, 7, 7
	index = "Outlands~Neutral~Minion~10~7~7~Elemental~Felcracked Colossus~Taunt~Uncollectible"
	requireTarget, keyWord, description = False, "Taunt", "Taunt"
	
"""Demon Hunter cards"""
class CrimsonSigilRunner(Minion):
	Class, race, name = "Demon Hunter", "", "Crimson Sigil Runner"
	mana, attack, health = 1, 2, 1
	index = "Outlands~Demon Hunter~Minion~1~2~1~None~Crimson Sigil Runner~Outcast"
	requireTarget, keyWord, description = False, "", "Outcast: Draw a card"
	
	def effectCanTrigger(self):
		posinHand = self.Game.Hand_Deck.hands[self.ID].index(self)
		self.effectViable = posinHand == 0 or posinHand == len(self.Game.Hand_Deck.hands[self.ID]) - 1
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if posinHand == 0 or posinHand == -1:
			PRINT(self, "Crimson Sigil Runner's Outcast triggers and player draws a card")
			self.Game.Hand_Deck.drawCard(self.ID)
		return None
		
		
class FuriousFelfin(Minion):
	Class, race, name = "Demon Hunter", "Murloc", "Furious Felfin"
	mana, attack, health = 2, 3, 2
	index = "Outlands~Demon Hunter~Minion~2~3~2~Murloc~Furious Felfin~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: If your hero attacked this turn, gain +1 Attack and Rush"
	
	def effectCanTrigger(self):
		self.effectViable = self.Game.CounterHandler.heroAttackTimesThisTurn[self.ID] > 0
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if self.Game.CounterHandler.heroAttackTimesThisTurn[self.ID] > 0:
			PRINT(self, "Furious Felfin's battlecry lets minion gain +1 Attack and Rush")
			self.buffDebuff(1, 0)
			self.getsKeyword("Rush")
		return None
		
		
class ImmolationAura(Spell):
	Class, name = "Demon Hunter", "Immolation Aura"
	requireTarget, mana = False, 2
	index = "Outlands~Demon Hunter~Spell~2~Immolation Aura"
	description = "Deal 1 damage to all minions twice"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		#不知道法强随从中途死亡是否会影响伤害，假设不会
		damage = (1 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		PRINT(self, "Immolation Aura deals %d damage to all minions twice"%damage)
		#中间会结算强制死亡
		targets = self.Game.minionsonBoard(1) + self.Game.minionsonBoard(2)
		self.dealsAOE(targets, [damage for minion in targets])
		self.Game.gathertheDead()
		targets = self.Game.minionsonBoard(1) + self.Game.minionsonBoard(2)
		self.dealsAOE(targets, [damage for minion in targets])
		return None
		
		
class Netherwalker(Minion):
	Class, race, name = "Demon Hunter", "", "Netherwalker"
	mana, attack, health = 2, 2, 2
	index = "Outlands~Demon Hunter~Minion~2~2~2~None~Netherwalker~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Discover a Demon"
	poolIdentifier = "Demons as Demon Hunter"
	@classmethod
	def generatePool(cls, Game):
		classes, lists, neutralCards = [], [], []
		classCards = {"Neutral": [], "Demon Hunter":[], "Druid":[], "Mage":[], "Hunter":[], "Paladin":[],
						"Priest":[], "Rogue":[], "Shaman":[], "Warlock":[], "Warrior":[]}
		for key, value in Game.MinionswithRace["Demon"].items():
			classCards[key.split('~')[1]].append(value)
			
		for Class in Classes:
			classes.append("Demons as "+Class)
			lists.append(classCards[Class]+classCards["Neutral"])
		return classes, lists
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if self.ID == self.Game.turn and self.Game.Hand_Deck.handNotFull(self.ID):
			key = "Demons as "+classforDiscover(self)
			if "InvokedbyOthers" in comment:
				PRINT(self, "Netherwalker's battlecry adds a random Demon to player's hand.")
				self.Game.Hand_Deck.addCardtoHand(np.random.choice(self.Game.RNGPools[key]), self.ID, "CreateUsingType")
			else:
				PRINT(self, "Netherwalker's battlecry lets player Discover a Demon")
				demons = np.random.choice(self.Game.RNGPools[key], 3, replace=False)
				self.Game.options = [demon(self.Game, self.ID) for demon in demons]
				self.Game.DiscoverHandler.startDiscover(self)
				
		return None
		
	def discoverDecided(self, option):
		PRINT(self, "Demon %s is put into player's hand."%option.name)
		self.Game.Hand_Deck.addCardtoHand(option, self.ID)
		self.Game.sendSignal("DiscoveredCardPutintoHand", self.ID, self, option, 0, "")
		
		
class SpectralSight(Spell):
	Class, name = "Demon Hunter", "Spectral Sight"
	requireTarget, mana = False, 2
	index = "Outlands~Demon Hunter~Spell~2~Spectral Sight~Outcast"
	description = "Draw a cards. Outscast: Draw another"
	def effectCanTrigger(self):
		posinHand = self.Game.Hand_Deck.hands[self.ID].index(self)
		self.effectViable = posinHand == 0 or posinHand == len(self.Game.Hand_Deck.hands[self.ID]) - 1
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		PRINT(self, "Spectral Sight is cast and player draws a card")
		self.Game.Hand_Deck.drawCard(self.ID)
		if posinHand == 0 or posinHand == -1:
			PRINT(self, "Spectral Sight's Outcast triggers and lets player draw another card")
			self.Game.Hand_Deck.drawCard(self.ID)
		return None
		
		
class AshtongueBattlelord(Minion):
	Class, race, name = "Demon Hunter", "", "Ashtongue Battlelord"
	mana, attack, health = 4, 3, 5
	index = "Outlands~Demon Hunter~Minion~4~3~5~None~Ashtongue Battlelord~Taunt~Lifesteal"
	requireTarget, keyWord, description = False, "Taunt,Lifesteal", "Taunt, Lifesteal"
	
	
class FelSummoner(Minion):
	Class, race, name = "Demon Hunter", "", "Fel Summoner"
	mana, attack, health = 6, 8, 3
	index = "Outlands~Demon Hunter~Minion~6~8~3~None~Fel Summoner~Deathrattle"
	requireTarget, keyWord, description = False, "", "Deathrattle: Summon a random Demon from your hand"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [SummonaRandomDemonfromYourHand(self)]
		
class SummonaRandomDemonfromYourHand(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self, "Deathrattle: Summon a random Demon from your hand triggers")
		demonsinHand = []
		for card in self.entity.Game.Hand_Deck.hands[self.entity.ID]:
			if card.cardType == "Minion" and "Demon" in card.race:
				demonsinHand.append(card)
				
		if demonsinHand != [] and self.entity.Game.spaceonBoard(self.entity.ID) > 0:
			self.entity.Game.summonfromHand(np.random.choice(demonsinHand), self.entity.position+1, self.entity.ID)
			
			
class KaynSunfury(Minion):
	Class, race, name = "Demon Hunter", "", "Kayn Sunfury"
	mana, attack, health = 4, 3, 5
	index = "Outlands~Demon Hunter~Minion~4~3~5~None~Kayn Sunfury~Charge~Legendary"
	requireTarget, keyWord, description = False, "Charge", "Charge. All friendly attacks ignore Taunt"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.appearResponse = [self.activateAura]
		self.disappearResponse = [self.deactivateAura]
		self.silenceResponse = [self.deactivateAura]
		
	def activateAura(self):
		PRINT(self, "Kayn Sunfury's aura is registered. Player %d's attacks now ignore Taunt."%self.ID)
		self.Game.playerStatus[self.ID]["Attacks Ignore Taunt"] += 1
		
	def deactivateAura(self):
		PRINT(self, "Kayn Sunfury's aura is removed. Player %d's attacks no longer ignore Taunt."%self.ID)
		self.Game.playerStatus[self.ID]["Attacks Ignore Taunt"] -= 1
		
		
class ImprisonedAntaen(Minion_Dormantfor2turns):
	Class, race, name = "Demon Hunter", "Demon", "Imprisoned Antaen"
	mana, attack, health = 5, 10, 6
	index = "Outlands~Demon Hunter~Minion~5~10~6~Demon~Imprisoned Antaen"
	requireTarget, keyWord, description = False, "", "Dormant for 2 turns. When this awakens, deal 10 damage randomly split among all enemies"
	
	def awakenEffect(self):
		PRINT(self, "Imprisoned Antaen awakens and deals 10 damage randomly split among all enemies")
		for i in range(10):
			targets = self.Game.livingObjtoTakeRandomDamage(3-self.ID)
			target = np.random.choice(targets)
			PRINT(self, "Imprisoned Antaen deals 1 damage to %s"%target.name)
			self.dealsDamage(target, 1)
			
			
class Metamorphosis(Spell):
	Class, name = "Demon Hunter", "Metamorphosis"
	requireTarget, mana = False, 5
	index = "Outlands~Demon Hunter~Spell~5~Metamorphosis~Legendary"
	description = "Swap your Hero Power to 'Deal 5 damage'. After 2 uses, swap it back"
	#不知道是否只是对使用两次英雄技能计数，而不一定要是那个特定的英雄技能
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		PRINT(self, "Metamorphosis is cast and swaps player's Hero Power to 'Deal 5 damage'. After 2 uses, swap it back")
		DemonicBlast(self.Game, self.ID).replaceHeroPower()
		return None
		
class DemonicBlast(HeroPower):
	mana, name, requireTarget = 1, "Demonic Blast", True
	index = "Demon Hunter~Hero Power~1~Demonic Blast"
	description = "Deal 5 damage"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_DemonicBlast(self)]
		self.progress = 0
		self.heroPowerReplaced = None
		
	def effect(self, target, choice=0):
		damage = (5 + self.Game.playerStatus[self.ID]["Hero Power Damage Boost"]) * (2 ** self.countDamageDouble())
		PRINT(self, "Hero Power Demonic Blast deals %d damage to %s"%(damage, target.name))
		objtoTakeDamage, damageActual = self.dealsDamage(target, damage)
		if objtoTakeDamage.health < 1 or objtoTakeDamage.dead:
			return 1
		return 0
		
	def replaceHeroPower(self):
		self.heroPowerReplaced = type(self.Game.heroPowers[self.ID])
		if self.Game.heroPowers[self.ID] != None:
			self.Game.heroPowers[self.ID].disappears()
			self.Game.heroPowers[self.ID] = None
		self.Game.heroPowers[self.ID] = self
		self.appears()
		
class Trigger_DemonicBlast(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["HeroUsedAbility"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return subject == self.entity
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.progress += 1
		PRINT(self, "Player uses Hero Power and Demonic Blast has been used for %d times"%self.entity.progress)
		if self.entity.progress > 1:
			PRINT(self, "Player has used Hero Power Demonic Blast twice and the Hero Power changes back to the original one it replaced")
			if self.entity.heroPowerReplaced != None:
				self.entity.heroPowerReplaced(self.entity.Game, self.entity.ID).replaceHeroPower()
				self.disconnect()
				
				
class SkullofGuldan(Spell):
	Class, name = "Demon Hunter", "Skull of Gul'dan"
	requireTarget, mana = False, 5
	index = "Outlands~Demon Hunter~Spell~5~Skull of Gul'dan~Outcast"
	description = "Draw 3 cards. Outscast: Reduce their Cost by (3)"
	def effectCanTrigger(self):
		posinHand = self.Game.Hand_Deck.hands[self.ID].index(self)
		self.effectViable = posinHand == 0 or posinHand == len(self.Game.Hand_Deck.hands[self.ID]) - 1
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		PRINT(self, "Skull of Gul'dan is cast and player draws 3 card")
		outcastCanTrigger = posinHand == 0 or posinHand == -1
		for i in range(3):
			card, mana = self.Game.Hand_Deck.drawCard(self.ID)
			if outcastCanTrigger and card != None:
				PRINT(self, "Skull of Gul'dan's Outcast triggers and reduces the Cost of the drawn card by (3)")
				ManaModification(card, changeby=-3, changeto=-1).applies()
		return None
		
		
class WarglaivesofAzzinoth(Weapon):
	Class, name, description = "Demon Hunter", "Warglaives of Azzinoth", "After attacking a minion, your hero may attack again"
	mana, attack, durability = 5, 3, 4
	index = "Outlands~Demon Hunter~Weapon~5~3~4~Warglaives of Azzinoth"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_WarglaivesofAzzinoth(self)]
		
class Trigger_WarglaivesofAzzinoth(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["HeroAttackedMinion"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return subject == self.entity.Game.heroes[self.entity.ID] and target.cardType == "Minion" and self.entity.onBoard
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self, "Player's weapon Warglaives of Azzinoth allows player to attack again after attacking minion.")
		self.entity.Game.heroes[self.entity.ID].attChances_extra +=1
		
		
class PriestessofFury(Minion):
	Class, race, name = "Demon Hunter", "Demon", "Priestess of Fury"
	mana, attack, health = 7, 6, 7
	index = "Outlands~Demon Hunter~Minion~7~6~7~Demon~Priestess of Fury"
	requireTarget, keyWord, description = False, "", "At the end of your turn, deal 6 damage randomly split among all enemies"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_PriestessofFury(self)]
		
class Trigger_PriestessofFury(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["TurnEnds"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self, "At the end of turn, %s deals 6 damage randomly split among all emenies"%self.entity.name)
		for i in range(6):
			targets = self.entity.Game.livingObjtoTakeRandomDamage(3-self.entity.ID)
			if targets != []:
				target = np.random.choice(targets)
				PRINT(self, "%s deals 1 damage to %s"%(self.entity.name, target.name))
				self.entity.dealsDamage(target, 1)
				
				
class CoilfangWarlord(Minion):
	Class, race, name = "Demon Hunter", "", "Coilfang Warlord"
	mana, attack, health = 8, 9, 5
	index = "Outlands~Demon Hunter~Minion~8~9~5~None~Coilfang Warlord~Rush~Deathrattle"
	requireTarget, keyWord, description = False, "Rush", "Rush. Deathrattle: Summon a 5/9 Warlord with Taunt"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [SummonaWarlordwithTaunt(self)]
		
class SummonaWarlordwithTaunt(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self, "Deathrattle: Summon a 5/9 Warlord with Taunt triggers")
		self.entity.Game.summonMinion(ConchguardWarlord(self.entity.Game, self.entity.ID), self.entity.position+1, self.entity.ID)
		
class ConchguardWarlord(Minion):
	Class, race, name = "Demon Hunter", "", "Conchguard Warlord"
	mana, attack, health = 8, 5, 9
	index = "Outlands~Demon Hunter~Minion~8~5~9~None~Conchguard Warlord~Taunt~Uncollectible"
	requireTarget, keyWord, description = False, "Taunt", "Taunt"
	
	
class PitCommander(Minion):
	Class, race, name = "Demon Hunter", "Demon", "Pit Commander"
	mana, attack, health = 9, 7, 9
	index = "Outlands~Demon Hunter~Minion~9~7~9~Demon~Pit Commander~Taunt"
	requireTarget, keyWord, description = False, "Taunt", "Taunt. At the end of your turn, summon a Demon from your deck"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_PitCommander(self)]
		
class Trigger_PitCommander(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["TurnEnds"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self, "At the end of turn, %s summons a Demon from player's deck"%self.entity.name)
		demonsinDeck = []
		for card in self.entity.Game.Hand_Deck.decks[self.entity.ID]:
			if card.cardType == "Minion" and "Demon" in card.race:
				demonsinDeck.append(card)
				
		if demonsinDeck != [] and self.entity.Game.spaceonBoard(self.entity.ID) > 0:
			demon = self.entity.Game.Hand_Deck.extractfromDeck(np.random.choice(demonsinDeck))[0]
			self.entity.Game.summonMinion(demon, self.entity.position+1, self.entity.ID)
			
			
"""Druid cards"""
class FungalFortunes(Spell):
	Class, name = "Druid", "Fungal Fortunes"
	requireTarget, mana = False, 2
	index = "Outlands~Druid~Spell~2~Fungal Fortunes"
	description = "Draw 3 cards. Discard any minions drawn"
	#The minions will be discarded immediately before drawing the next card.
	#The discarding triggers triggers["Discarded"] and send signals.
	#If the hand is full, then no discard at all. The drawn cards vanish.	
	#The "cast when drawn" spells can take effect as usual
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		PRINT(self, "Fungal Fortunes is cast and player draws three cards and discard minions drawn.")
		for i in range(3):
			card, mana = self.Game.Hand_Deck.drawCard(self.ID)
			#If a card has "cast when drawn" effect, it won't stay in hand.
			if card != None and card.cardType == "Minion" and card.inHand:
				self.Game.Hand_Deck.discardCard(self.ID, card)
		return None
		
		
class Ironbark(Spell):
	Class, name = "Druid", "Ironbark"
	requireTarget, mana = True, 2
	index = "Outlands~Druid~Spell~2~Ironbark"
	description = "Give a minion +1/+3 and Taunt. Costs (0) if you have at least 7 Mana Crystals"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersinHand = [Trigger_Ironbark(self)]
		
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.onBoard
		
	def selfManaChange(self):
		#假设需要的是空水晶，暂时获得的水晶不算
		if self.inHand and self.Game.ManaHandler.manasUpper[self.ID] > 6:
			self.mana = 0
			
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if target != None:
			PRINT(self, "Ironbark is cast and gives minion %s +1/+3 and Taunt"%target.name)
			target.buffDebuff(1, 3)
			target.getsKeyword("Taunt")
		return target
		
class Trigger_Ironbark(TriggerinHand):
	def __init__(self, entity):
		self.blank_init(entity, ["EmptyManaCrystalCheck"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.inHand and ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.Game.ManaHandler.calcMana_Single(self.entity)
		
		
class ArchsporeMsshifn(Minion):
	Class, race, name = "Druid", "", "Archspore Msshi'fn"
	mana, attack, health = 3, 3, 4
	index = "Outlands~Druid~Minion~3~3~4~None~Archspore Msshi'fn~Taunt~Deathrattle~Legendary"
	requireTarget, keyWord, description = False, "Taunt", "Taunt. Deathrattle: Shuffle 'Msshi'fn Prime' into your deck"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [ShuffleMsshifnPrimeintoYourDeck(self)]
		
class ShuffleMsshifnPrimeintoYourDeck(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self, "Deathrattle: Shuffle 'Msshi'fn Prime' into your deck triggers")
		self.entity.Game.Hand_Deck.shuffleCardintoDeck(MsshifnPrime(self.entity.Game, self.entity.ID), self.entity.ID)
		
class MsshifnPrime(Minion):
	Class, race, name = "Druid", "", "Msshi'fn Prime"
	mana, attack, health = 10, 9, 9
	index = "Outlands~Druid~Minion~10~9~9~None~Msshi'fn Prime~Taunt~Choose One~Legendary~Uncollectible"
	requireTarget, keyWord, description = False, "Taunt", "Taunt. Choose One- Summon a 9/9 Fungal Giant with Taunt; or Rush"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.chooseOne = 1
		# 0: Give other minion +2/+2; 1:Summon two Treants with Taunt.
		self.options = [MsshifnAttac(self), MsshifnProtec(self)]
		
	#如果有全选光环，只有一个9/9，其同时拥有突袭和嘲讽
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if choice == 0:
			PRINT(self, "Msshi'fn Prime summons a 9/9 Fungal Giant with Taunt")
			self.Game.summonMinion(FungalGuardian(self.Game, self.ID), self.position+1, self.ID)
		elif choice == 1:
			PRINT(self, "Msshi'fn Prime summons a 9/9 Fungal Giant with Rush")
			self.Game.summonMinion(FungalBruiser(self.Game, self.ID), self.position+1, self.ID)
		elif choice == "ChooseBoth":
			PRINT(self, "Msshi'fn Prime summons a 9/9 Fungal Giant with Taunt and Rush")
			self.Game.summonMinion(FungalGargantuan(self.Game, self.ID), self.position+1, self.ID)
		return None
		
class FungalGuardian(Minion):
	Class, race, name = "Druid", "", "Fungal Guardian"
	mana, attack, health = 9, 9, 9
	index = "Outlands~Druid~Minion~9~9~9~None~Fungal Guardian~Taunt~Uncollectible"
	requireTarget, keyWord, description = False, "Taunt", "Taunt"
	
class FungalBruiser(Minion):
	Class, race, name = "Druid", "", "Fungal Bruiser"
	mana, attack, health = 9, 9, 9
	index = "Outlands~Druid~Minion~9~9~9~None~Fungal Bruiser~Rush~Uncollectible"
	requireTarget, keyWord, description = False, "Rush", "Rush"
	
class FungalGargantuan(Minion):
	Class, race, name = "Druid", "", "Fungal Gargantuan"
	mana, attack, health = 9, 9, 9
	index = "Outlands~Druid~Minion~9~9~9~None~Fungal Gargantuan~Taunt~Rush~Uncollectible"
	requireTarget, keyWord, description = False, "Taunt,Rush", "Taunt, Rush"
	
class MsshifnAttac:
	def __init__(self, minion):
		self.minion = minion
		self.name = "Msshi'fn At'tac"
		self.description = "Summon a 9/9 with Taunt"
		
	def available(self):
		return self.minion.Game.spaceonBoard(self.minion.ID) > 0
		
	def selfCopy(self, recipientMinion):
		return type(self)(recipientMinion)
		
class MsshifnProtec:
	def __init__(self, minion):
		self.minion = minion
		self.name = "Msshi'fn Pro'tec"
		self.description = "Summon a 9/9 with Rush"
		
	def available(self):
		return self.minion.Game.spaceonBoard(self.minion.ID) > 0
		
	def selfCopy(self, recipientMinion):
		return type(self)(recipientMinion)
		
		
class Bogbeam(Spell):
	Class, name = "Druid", "Bogbeam"
	requireTarget, mana = True, 3
	index = "Outlands~Druid~Spell~3~Bogbeam"
	description = "Deal 3 damage to a minion. Costs (0) if you have at least 7 Mana Crystals"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersinHand = [Trigger_Bogbeam(self)]
		
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.onBoard
		
	def selfManaChange(self):
		#假设需要的是空水晶，暂时获得的水晶不算
		if self.inHand and self.Game.ManaHandler.manasUpper[self.ID] > 6:
			self.mana = 0
			
	def effectCanTrigger(self):
		self.effectViable = self.Game.ManaHandler.manasUpper[self.ID] > 6
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if target != None:
			damage = (3 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			PRINT(self, "Bogbeam is cast and deals %d damage to minion %s"%(damage, target.name))
			self.dealsDamage(target, damage)
		return target
		
class Trigger_Bogbeam(TriggerinHand):
	def __init__(self, entity):
		self.blank_init(entity, ["EmptyManaCrystalCheck"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.inHand and ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.Game.ManaHandler.calcMana_Single(self.entity)
		
		
class ImprisonedSatyr(Minion_Dormantfor2turns):
	Class, race, name = "Druid", "Demon", "Imprisoned Satyr"
	mana, attack, health = 3, 3, 3
	index = "Outlands~Druid~Minion~3~3~3~Demon~Imprisoned Satyr"
	requireTarget, keyWord, description = False, "", "Dormant for 2 turns. When this awakens, reduce the Cost of a random minion in your hand by (5)"
	
	def awakenEffect(self):
		PRINT(self, "Imprisoned Satyr awakens and reduces the Cost of a random minion in player's hand by (5)")
		minionsinHand = []
		for card in self.Game.Hand_Deck.hands[self.ID]:
			if card.cardType == "Minion":
				minionsinHand.append(card)
		if minionsinHand != []:
			minion = np.random.choice(minionsinHand)
			PRINT(self, "The Cost of minion %s in player's hand is reduced by (5)"%minion.name)
			ManaModification(minion, changeby=-5, changeto=-1).applies()
			
			
class Germination(Spell):
	Class, name = "Druid", "Germination"
	requireTarget, mana = True, 4
	index = "Outlands~Druid~Spell~4~Germination"
	description = "Summon a copy of a friendly minion. Give the copy Taunt"
	def available(self):
		return self.selectableFriendlyMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.ID == self.ID and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if target != None:
			PRINT(self, "Germination summons a copy of friendly minion %s and gives the copy Taunt."%target.name)
			Copy = target.selfCopy(target.ID)
			self.Game.summonMinion(Copy, target.position+1, self.ID)
			Copy.getsKeyword("Taunt")
		return target
		
		
class Overgrowth(Spell):
	Class, name = "Druid", "Overgrowth"
	requireTarget, mana = False, 4
	index = "Outlands~Druid~Spell~4~Overgrowth"
	description = "Gain two empty Mana Crystals"
	#不知道满费用和9费时如何结算,假设不会给抽牌的衍生物
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		PRINT(self, "Overgrowth gives player two empty Mana Crystals.")
		if self.Game.ManaHandler.gainEmptyManaCrystal(2, self.ID) == False:
			PRINT(self, "Player's mana at upper limit already. Overgrowth gives player an Excess Mana instead.")
			self.Game.Hand_Deck.addCardtoHand(ExcessMana(self.Game, self.ID), self.ID)
		return None
		
		
class GlowflySwarm(Spell):
	Class, name = "Druid", "Glowfly Swarm"
	requireTarget, mana = False, 5
	index = "Outlands~Druid~Spell~5~Glowfly Swarm"
	description = "Summon a 2/2 Glowfly for each spell in your hand"
	def available(self):
		return self.Game.spaceonBoard(self.ID) > 0
		
	def effectCanTrigger(self):
		self.effectViable = False
		for card in self.Game.Hand_Deck.hands[self.ID]:
			if card.cardType == "Spell" and card != self:
				self.effectViable = True
				break
				
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		PRINT(self, "Glowfly Swarm is cast and summons a 2/2 Glowfly for each spell in player's hand")
		numSpellsinHand = 0
		for card in self.Game.Hand_Deck.hands[self.ID]:
			if card.cardType == "Spell":
				numSpellsinHand += 1
		if numSpellsinHand > 0:
			self.Game.summonMinion([Glowfly(self.Game, self.ID) for i in range(numSpellsinHand)], (-1, "totheRightEnd"), self.ID)
		return None
		
class Glowfly(Minion):
	Class, race, name = "Druid", "Beast", "Glowfly"
	mana, attack, health = 2, 2, 2
	index = "Outlands~Druid~Minion~2~2~2~Beast~Glowfly~Uncollectible"
	requireTarget, keyWord, description = False, "", ""
	
	
class MarshHydra(Minion):
	Class, race, name = "Druid", "Beast", "Marsh Hydra"
	mana, attack, health = 7, 7, 7
	index = "Outlands~Druid~Minion~7~7~7~Beast~Marsh Hydra~Rush"
	requireTarget, keyWord, description = False, "Rush", "Rush. After this attacks, add a random 8-Cost minion to your hand"
	poolIdentifier = "8-Cost Minions"
	@classmethod
	def generatePool(cls, Game):
		return "8-Cost Minions", list(Game.MinionsofCost[8].values())
		
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_HulkingOverfiend(self)]
		
class Trigger_HulkingOverfiend(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionAttackedMinion", "MinionAttackedHero"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject == self.entity
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self, "After %s attacks, it adds a random 8-Cost minion into player's hand"%self.entity.name)
		self.entity.Game.Hand_Deck.addCardtoHand(np.random.choice(self.entity.Game.RNGPools["8-Cost Minions"]), self.entity.ID, "CreateUsingType")
		
		
class YsielWindsinger(Minion):
	Class, race, name = "Druid", "", "Ysiel Windsinger"
	mana, attack, health = 9, 5, 5
	index = "Outlands~Druid~Minion~9~5~5~None~Ysiel Windsinger~Legendary"
	requireTarget, keyWord, description = False, "", "Your spells cost (1)"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.auras["Mana Aura"] = ManaAura_Dealer(self, self.manaAuraApplicable, changeby=0, changeto=1)
		
	def manaAuraApplicable(self, subject): #ID用于判定是否是我方手中的随从
		return subject.cardType == "Spell" and subject.ID == self.ID
		
"""Hunter cards"""
class Helboar(Minion):
	Class, race, name = "Hunter", "Beast", "Helboar"
	mana, attack, health = 1, 2, 1
	index = "Outlands~Hunter~Minion~1~2~1~Beast~Helboar~Deathrattle"
	requireTarget, keyWord, description = False, "", "Deathrattle: Give a random Beast in your hand +1/+1"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [GiveaRandomBeastinYourHandPlus1Plus1(self)]
		
class GiveaRandomBeastinYourHandPlus1Plus1(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self, "Deathrattle: Give a random Beast in your hand +1/+1 triggers")
		beastsinHand = []
		for card in self.entity.Game.Hand_Deck.hands[self.entity.ID]:
			if card.cardType == "Minion" and "Beast" in card.race:
				beastsinHand.append(card)
		if beastsinHand != []:
			np.random.choice(beastsinHand).buffDebuff(1, 1)
			
			
class ImprisonedFelmaw(Minion_Dormantfor2turns):
	Class, race, name = "Hunter", "Demon", "Imprisoned Felmaw"
	mana, attack, health = 2, 5, 4
	index = "Outlands~Hunter~Minion~2~5~4~Demon~Imprisoned Felmaw"
	requireTarget, keyWord, description = False, "", "Dormant for 2 turns. When this awakens, attack a random enemy"
	#假设这个攻击不会消耗随从的攻击机会
	def awakenEffect(self):
		PRINT(self, "Imprisoned Felmaw awakens and attacks a random enemy")
		targets = self.Game.livingObjtoTakeRandomDamage(3-self.ID)
		if targets != []:
			target = np.random.choice(targets)
			PRINT(self, "Imprisoned Felmaw attacks random enemy %s"%target.name)
			self.Game.battleRequest(self, target, False, False)
			
			
class PackTactics(Secret):
	Class, name = "Hunter", "Pack Tactics"
	requireTarget, mana = False, 2
	index = "Outlands~Hunter~Spell~2~Pack Tactics~~Secret"
	description = "When a friendly minion is attacked, summon a 3/3 copy"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_PackTactics(self)]
		
class Trigger_PackTactics(SecretTrigger):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionAttacksMinion", "HeroAttacksMinion"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.ID != self.entity.Game.turn and target[0].ID == self.entity.ID and self.entity.Game.spaceonBoard(self.entity.ID) > 0
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.Game.summonMinion(target[0].selfCopy(self.entity.ID, 3, 3), target[0].position+1, self.entity.ID)
		PRINT(self, "When friendly minion %s is attacked, Secret Pack Tactics triggers and summons a 3/3 Copy of it"%target[0].name)
		
		
class ScavengersIngenuity(Spell):
	Class, name = "Hunter", "Scavenger's Ingenuity"
	requireTarget, mana = False, 2
	index = "Outlands~Hunter~Spell~2~Scavenger's Ingenuity"
	description = "Draw a Beast. Give it +3/+3"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		PRINT(self, "Scavenger's Ingenuity is cast, lets player draw a Beast and gives it +3/+3")
		beastsinDeck = []
		for card in self.Game.Hand_Deck.decks[self.ID]:
			if card.cardType == "Minion" and "Beast" in card.race:
				beastsinDeck.append(card)
				
		if beastsinDeck != []:
			beast, mana = self.Game.Hand_Deck.drawCard(self.ID, np.random.choice(beastsinDeck))
			if beast != None:
				PRINT(self, "Beast %s is drawn and gains +3/+3"%beast.name)
				beast.buffDebuff(3, 3)
		return None
		
		
class AugmentedPorcupine(Minion):
	Class, race, name = "Hunter", "Beast", "Augmented Porcupine"
	mana, attack, health = 3, 2, 4
	index = "Outlands~Hunter~Minion~3~2~4~Beast~Augmented Porcupine~Deathrattle"
	requireTarget, keyWord, description = False, "", "Deathrattle: Deals this minion's Attack damage randomly split among all enemies"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [DealDamageEqualtoAttack(self)]
		
class DealDamageEqualtoAttack(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self, "Deathrattle: Deal this minion's Attack damage randomly split among all enemies triggers")
		for i in range(number):
			enemies = self.entity.Game.livingObjtoTakeRandomDamage(3-self.entity.ID)
			if enemies != []:
				target = np.random.choice(enemies)
				PRINT(self, "Deathrattle deals 1 damage to random enemy %s"%target.name)
				self.entity.dealsDamage(target, 1)
				
				
class ZixorApexPredator(Minion):
	Class, race, name = "Hunter", "Beast", "Zixor, Apex Predator"
	mana, attack, health = 3, 2, 4
	index = "Outlands~Hunter~Minion~3~2~4~Beast~Zixor, Apex Predator~Rush~Deathrattle~Legendary"
	requireTarget, keyWord, description = False, "Rush", "Rush. Deathrattle: Shuffle 'Zixor Prime' into your deck"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [ShuffleZixorPrimeintoYourDeck(self)]
		
class ShuffleZixorPrimeintoYourDeck(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self, "Deathrattle: Shuffle 'Zixor Prime' into your deck triggers")
		self.entity.Game.Hand_Deck.shuffleCardintoDeck(ZixorPrime(self.entity.Game, self.entity.ID), self.entity.ID)
		
class ZixorPrime(Minion):
	Class, race, name = "Hunter", "Beast", "Zixor Prime"
	mana, attack, health = 8, 4, 4
	index = "Outlands~Hunter~Minion~8~4~4~Beast~Zixor Prime~Rush~Battlecry~Legendary~Uncollectible"
	requireTarget, keyWord, description = False, "Rush", "Rush. Battlecry: Summon 3 copies of this minion"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		#假设已经死亡时不会召唤复制
		if self.onBoard or self.inDeck:
			PRINT(self, "Zixor Prime's battlecry summons 3 copies of the minion")
			copies = [self.selfCopy(self.ID) for i in range(3)]
			self.Game.summonMinion(copies, (self.position, "totheRight"), self.ID)
		return None
		
		
class MokNathalLion(Minion):
	Class, race, name = "Hunter", "Beast", "Mok'Nathal Lion"
	mana, attack, health = 4, 5, 2
	index = "Outlands~Hunter~Minion~4~5~2~Beast~Mok'Nathal Lion~Rush~Battlecry"
	requireTarget, keyWord, description = True, "Rush", "Rush. Battlecry: Choose a friendly minion. Gain a copy of its Deathrattle"
	def effectCanTrigger(self):
		self.effectViable = self.targetExists()
		
	def targetExists(self, choice=0):
		return self.selectableFriendlyMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.ID == self.ID and target != self and target.onBoard and target.deathrattles != []
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if target != None and target.deathrattles != []:
			PRINT(self, "Mok'Nathal Lion's battlecry gives minion a copy of friendly minion %s's Deathrattle"%target.name)
			for trigger in target.deathrattles:
				trigCopy = trigger.selfCopy(self)
				self.deathrattles.append(trigCopy)
				if self.onBoard:
					trigCopy.connect()
		return target
		
		
class ScrapShot(Spell):
	Class, name = "Hunter", "Scrap Shot"
	requireTarget, mana = True, 4
	index = "Outlands~Hunter~Spell~4~Scrap Shot"
	description = "Deal 3 damage. Give a random Beast in your hand +3/+3"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if target != None:
			damage = (3 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			PRINT(self, "Scrap Shot deals %d damage to %s"%(damage, target.name))
			self.dealsDamage(target, damage)
		PRINT(self, "Scrap Shot gives a random Beast in player's hand +3/+3")
		beastsinHand = []
		for card in self.Game.Hand_Deck.hands[self.ID]:
			if card.cardType == "Minion" and "Beast" in card.race:
				beastsinHand.append(card)
		if beastsinHand != []:
			np.random.choice(beastsinHand).buffDebuff(3, 3)
		return target
		
		
class BeastmasterLeoroxx(Minion):
	Class, race, name = "Hunter", "", "Beastmaster Leoroxx"
	mana, attack, health = 8, 5, 5
	index = "Outlands~Hunter~Minion~8~5~5~None~Beastmaster Leoroxx~Battlecry~Legendary"
	requireTarget, keyWord, description = False, "", "Battlecry: Summon 3 Beasts from your hand"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		PRINT(self, "Beastmaster Leoroxx's battlecry summons 3 Beasts from player's hand")
		#假设从手牌中最左边向右检索，然后召唤
		for i in range(3):
			for card in self.Game.Hand_Deck.hands[self.ID]:
				beast = None
				if card.cardType == "Minion" and "Beast" in card.race:
					beast = card
					break
			if beast != None: #手牌中有野兽
				if self.Game.summonfromHand(beast, self.position+1, self.ID) == False:
					break #如果场上没有空位了
			else: #手牌中没有野兽，则直接结束循环
				break
		return None
		
		
class NagrandSlam(Spell):
	Class, name = "Hunter", "Nagrand Slam"
	requireTarget, mana = False, 10
	index = "Outlands~Hunter~Spell~10~Nagrand Slam"
	description = "Summon four 3/5 Clefthoofs that attack random enemies"
	def available(self):
		return self.Game.spaceonBoard(self.ID) > 0
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		PRINT(self, "Nagrand Slam is cast and summons four 3/5 Clefthoofs that attack random enemies")
		#不知道卡德加翻倍召唤出的随从是否会攻击那个随从，假设不会
		clefthoofs = [Clefthoof(self.Game, self.ID) for i in range(4)]
		self.Game.summonMinion(clefthoofs, (-1, "totheRightEnd"), self.ID)
		for clefthoof in clefthoofs:
			#Clefthoofs must be living to initiate attacks
			if clefthoof.onBoard and clefthoof.health > 0 and clefthoof.dead == False:
				targets = self.Game.livingObjtoTakeRandomDamage(3-self.ID)
				if targets != []:
					enemy = np.random.choice(targets)
					PRINT(self, "Summoned Clefthoof attacks random enemy %s"%enemy.name)
					#攻击会消耗攻击机会
					self.Game.battleRequest(clefthoof, enemy, False, True)
		return None
		
class Clefthoof(Minion):
	Class, race, name = "Hunter", "Beast", "Clefthoofs"
	mana, attack, health = 4, 3, 5
	index = "Outlands~Hunter~Minion~4~3~5~Beast~Clefthoof~Uncollectible"
	requireTarget, keyWord, description = False, "", ""
	
"""Mage cards"""
class Evocation(Spell):
	Class, name = "Mage", "Evocation"
	requireTarget, mana = False, 1
	index = "Outlands~Mage~Spell~1~Evocation~Legendary"
	description = "Fill your hand with random Mage spells. At the end of your turn, discard them"
	poolIdentifier = "Mage Spells"
	@classmethod
	def generatePool(cls, Game):
		mageSpells = []
		for key, value in Game.ClassCards["Mage"].items():
			if "~Spell~" in key:
				mageSpells.append(value)
		return "Mage Spells", mageSpells
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		PRINT(self, "Evocation is cast and fills players hand with random Mage spells. They will be discarded at the end of turn")
		while self.Game.Hand_Deck.handNotFull(self.ID):
			spell = np.random.choice(self.Game.RNGPools["Mage Spells"])(self.Game, self.ID)
			trigger = Trigger_Evocation(spell)
			spell.triggersinHand.append(trigger)
			self.Game.Hand_Deck.addCardtoHand(spell, self.ID)
		return None
		
class Trigger_Evocation(TriggerinHand):
	def __init__(self, entity):
		self.blank_init(entity, ["TurnEnds"])
		self.temp = True
		self.makesCardEvanescent = True
		
	#They will be discarded at the end of any turn
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.inHand
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self, "At the end of turn, spell %s created by Evocation is discarded"%self.entity.name)
		#The discard() func takes care of disconnecting the TriggerinHand
		self.entity.Game.Hand_Deck.discardCard(self.entity.ID, self.entity)
		
		
class FontofPower(Spell):
	Class, name = "Mage", "Font of Power"
	requireTarget, mana = False, 1
	index = "Outlands~Mage~Spell~1~Font of Power"
	description = "Discover a Mage minion. If your deck has no minions, keep all 3"
	poolIdentifier = "Mage Minions"
	@classmethod
	def generatePool(cls, Game):
		druidMinions = []
		for key, value in Game.ClassCards["Mage"].items():
			if "~Minion~" in key:
				druidMinions.append(value)
		return "Mage Minions", druidMinions
		
	def effectCanTrigger(self):
		self.effectViable = self.Game.Hand_Deck.noMinionsinDeck(self.ID)
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if self.Game.Hand_Deck.handNotFull(self.ID):
			if self.Game.Hand_Deck.noMinionsinDeck(self.ID):
				PRINT(self, "Font of Power is cast and adds all 3 Mage minions to player's hand.")
				minions = np.random.choice(self.Game.RNGPools["Mage Minions"], 3, replace=False)
				self.Game.Hand_Deck.addCardtoHand(minions, self.ID, "CreateUsingType")
			else:
				if "CastbyOthers" in comment:
					PRINT(self, "Font of Power is cast and adds a random Mage minion to player's hand")
					minion = np.random.choice(self.Game.RNGPools["Mage Minions"])
					self.Game.Hand_Deck.addCardtoHand(minion, self.ID, "CreateUsingType")
				else:
					PRINT(self, "Font of Power is cast and lets player discover a Mage Minion.")
					minions = np.random.choice(self.Game.RNGPools["Mage Minions"], 3, replace=False)
					self.Game.options = [minion(self.Game, self.ID) for minion in minions]
					self.Game.DiscoverHandler.startDiscover(self)
		return None
		
	def discoverDecided(self, option):
		PRINT(self, "Mage Minion %s is put into player's hand."%option.name)
		self.Game.Hand_Deck.addCardtoHand(option, self.ID)
		self.Game.sendSignal("DiscoveredCardPutintoHand", self.ID, self, option, 0, "")
		
		
class ApexisSmuggler(Minion):
	Class, race, name = "Mage", "", "Apexis Smuggler"
	mana, attack, health = 2, 2, 3
	index = "Outlands~Mage~Minion~2~2~3~None~Apexis Smuggler"
	requireTarget, keyWord, description = False, "", "After you play a Secret, Discover a spell"
	poolIdentifier = "Mage Spells"
	@classmethod
	def generatePool(cls, Game):
		classes, lists = [], []
		for Class in Classes:
			classes.append(Class+" Spells")
			spellsinClass = []
			for key, value in Game.ClassCards[Class].items():
				if "~Spell~" in key:
					spellsinClass.append(value)
			lists.append(spellsinClass)
		return classes, lists
		
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_ApexisSmuggler(self)]
		
	def discoverDecided(self, option):
		PRINT(self, "Spell %s is put into player's hand"%option.name)
		self.Game.Hand_Deck.addCardtoHand(option, self.ID)
		self.Game.sendSignal("DiscoveredCardPutintoHand", self.ID, self, option, 0, "")
		
class Trigger_ApexisSmuggler(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["SpellBeenPlayed"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject.ID == self.entity.ID and "~~Secret" in subject.index
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self, "After player plays a Secret, %s lets player Discover a spell"%self.entity.name)
		key = classforDiscover(self.entity)+" Spells"
		spells = np.random.choice(self.entity.Game.RNGPools[key], 3, replace=False)
		self.entity.Game.options = [spell(self.entity.Game, self.entity.ID) for spell in spells]
		self.entity.Game.DiscoverHandler.startDiscover(self.entity)
		
		
class AstromancerSolarian(Minion):
	Class, race, name = "Mage", "", "Astromancer Solarian"
	mana, attack, health = 2, 3, 2
	index = "Outlands~Mage~Minion~2~3~2~None~Astromancer Solarian~Spell Damage~Deathrattle~Legendary"
	requireTarget, keyWord, description = False, "Spell Damage", "Spell Damage +1. Deathrattle: Shuffle 'Solarian Prime' into your deck"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [ShuffleSolarianPrimeintoYourDeck(self)]
		
class ShuffleSolarianPrimeintoYourDeck(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self, "Deathrattle: Shuffle 'Solarian Prime' into your deck triggers")
		self.entity.Game.Hand_Deck.shuffleCardintoDeck(SolarianPrime(self.entity.Game, self.entity.ID), self.entity.ID)
		
class SolarianPrime(Minion):
	Class, race, name = "Mage", "Demon", "Solarian Prime"
	mana, attack, health = 7, 7, 7
	index = "Outlands~Mage~Minion~7~7~7~Demon~Solarian Prime~Spell Damage~Battlecry~Legendary~Uncollectible"
	requireTarget, keyWord, description = False, "Spell Damage", "Spell Damage +1. Battlecry: Cast 5 random Mage spells (target enemies if possible)"
	poolIdentifier = "Mage Spells"
	@classmethod
	def generatePool(cls, Game):
		spells = []
		for key, value in Game.ClassCards["Mage"].items():
			if "~Spell~" in key:
				spells.append(value)
		return "Mage Spells", spells
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		PRINT(self, "Solarian Prime's battlecry casts 5 random Mage spells, which target enemies if possible")
		for i in range(5):
			spell = np.random.choice(self.Game.RNGPools["Mage Spells"])(self.Game, self.ID)
			PRINT(self, "******Solarian Prime's battlecry casts spell %s"%spell.name)
			if spell.needTarget():
				targets = spell.returnTargets("IgnoreStealthandImmune", 0)
				enemies = []
				for obj in targets:
					if obj.ID != self.ID:
						enemies.append(obj)
				if enemies != []:
					enemyTarget = np.random.choice(enemies)
					PRINT(self, "%s is cast upon enemy target %s"%(spell.name, enemyTarget.name))
					spell.cast(enemyTarget)
				else:
					PRINT(self, "No available enemy target found. Spell must be cast upon friendly characters")
					spell.cast()
			else:
				spell.cast()
			self.Game.gathertheDead()
		return None
		
		
class IncantersFlow(Spell):
	Class, name = "Mage", "Incanter's Flow"
	requireTarget, mana = False, 2
	index = "Outlands~Mage~Spell~2~Incanter's Flow"
	description = "Reduce the Cost of spells in your deck by (1)"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		PRINT(self, "Incanter's Flow is cast and reduces the Cost of spells in your deck by (1)")
		for card in fixedList(self.Game.Hand_Deck.decks[self.ID]):
			if card.cardType == "Spell":
				ManaModification(card, changeby=-1, changeto=-1).applies()
		return None
		
		
class Starscryer(Minion):
	Class, race, name = "Mage", "", "Starscryer"
	mana, attack, health = 2, 3, 1
	index = "Outlands~Mage~Minion~2~3~1~None~Starscryer~Deathrattle"
	requireTarget, keyWord, description = False, "", "Deathrattle: Draw a spell"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [DrawaSpell(self)]
		
class DrawaSpell(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self, "Deathrattle: Draw a spell triggers")
		spellsinDeck = []
		for card in self.entity.Game.Hand_Deck.decks[self.entity.ID]:
			if card.cardType == "Spell":
				spellsinDeck.append(card)
		if spellsinDeck != []:
			self.entity.Game.Hand_Deck.drawCard(self.entity.ID, np.random.choice(spellsinDeck))
			
			
class ImprisonedObserver(Minion_Dormantfor2turns):
	Class, race, name = "Mage", "Demon", "Imprisoned Observer"
	mana, attack, health = 3, 4, 5
	index = "Outlands~Mage~Minion~3~4~5~Demon~Imprisoned Observer"
	requireTarget, keyWord, description = False, "", "Dormant for 2 turns. When this awakens, deal 2 damage to all enemy minions"
	
	def awakenEffect(self):
		PRINT(self, "Imprisoned Observer awakens and deals 2 damage to all enemy minions")
		targets = self.Game.minionsonBoard(3-self.ID)
		self.dealsAOE(targets, [2 for minion in targets])
		
		
class NetherwindPortal(Secret):
	Class, name = "Mage", "Netherwind Portal"
	requireTarget, mana = False, 3
	index = "Outlands~Mage~Spell~3~Netherwind Portal~~Secret"
	description = "After your opponent casts a spell, summon a random 4-Cost minion"
	poolIdentifier = "4-Cost Minions to Summon"
	@classmethod
	def generatePool(cls, Game):
		return "4-Cost Minions to Summon", list(Game.MinionsofCost[4].values())
		
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_NetherwindPortal(self)]
		
class Trigger_NetherwindPortal(SecretTrigger):
	def __init__(self, entity):
		self.blank_init(entity, ["SpellBeenPlayed"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.ID != self.entity.Game.turn and subject.ID != self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self, "After the opponent casts a spell, Secret Netherwind Portal is triggered and summons a random 4-Cost minion")
		minion = np.random.choice(self.entity.Game.RNGPools["4-Cost Minions to Summon"])
		self.entity.Game.summonMinion(minion(self.entity.Game, self.entity.ID), -1, self.entity.ID)
		
		
class ApexisBlast(Spell):
	Class, name = "Mage", "Apexis Blast"
	requireTarget, mana = True, 5
	index = "Outlands~Mage~Spell~5~Apexis Blast"
	description = "Deal 5 damage. If your deck has no minions, summon a random 5-Cost minion"
	poolIdentifier = "5-Cost Minions to Summon"
	@classmethod
	def generatePool(cls, Game):
		return "5-Cost Minions to Summon", list(Game.MinionsofCost[5].values())
		
	def effectCanTrigger(self):
		self.effectViable = self.Game.Hand_Deck.noMinionsinDeck(self.ID)
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if target != None:
			damage = (5 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			PRINT(self, "Apexis Blast is cast and deals %d damage to %s"%(damage, target.name))
			self.dealsDamage(target, damage)
			if self.Game.Hand_Deck.noMinionsinDeck(self.ID):
				PRINT(self, "Because player has no minions in deck, Apexis Blast summons a random 5-Cost minion")
				minion = np.random.choice(self.Game.RNGPools["5-Cost Minions to Summon"])(self.Game, self.ID)
				self.Game.summonMinion(minion, -1, self.ID)
		return target
		
		
class DeepFreeze(Spell):
	Class, name = "Mage", "Deep Freeze"
	requireTarget, mana = True, 8
	index = "Outlands~Mage~Spell~8~Deep Freeze"
	description = "Freeze an enemy. Summon two 3/6 Water Elementals"
	def available(self):
		return self.selectableEnemyExists()
		
	def targetCorrect(self, target, choice=0):
		return (target.cardType == "Minion" or target.cardType == "Hero") and target.ID != self.ID and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if target != None:
			PRINT(self, "Deep Freeze is cast and Freezes enemy %s"%target.name)
			target.getsFrozen()
		PRINT(self, "Deep Freeze summons two 3/6 Water Elementals")
		self.Game.summonMinion([WaterElemental_Outlands(self.Game, self.ID) for i in range(2)], (-1, "totheRightEnd"), self.ID)
		return target
		
class WaterElemental_Outlands(Minion):
	Class, race, name = "Mage", "Elemental", "Water Elemental"
	mana, attack, health = 4, 3, 6
	index = "Outlands~Mage~Minion~4~3~6~Elemental~Water Elemental~Uncollectible"
	requireTarget, keyWord, description = False, "", "Freeze any character damaged by this minion"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_WaterElemental(self)]
		
class Trigger_WaterElemental(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionTakesDamage", "HeroTakesDamage"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return subject == self.entity
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self, "%s deals damage to %s and freezes it."%(self.entity.name, target.name))
		target.getsFrozen()
		
		
"""Paladin cards"""
class ImprisonedSungill(Minion_Dormantfor2turns):
	Class, race, name = "Paladin", "Murloc", "Imprisoned Sungill"
	mana, attack, health = 1, 2, 1
	index = "Outlands~Paladin~Minion~1~2~1~Murloc~Imprisoned Sungill"
	requireTarget, keyWord, description = False, "", "Dormant for 2 turns. When this awakens, Summon two 1/1 Murlocs"
	
	def awakenEffect(self):
		PRINT(self, "Imprisoned Sungill awakens and summons two 1/1 Murlocs")
		self.Game.summonMinion([SungillStreamrunner(self.Game, self.ID) for i in range(2)], (self.position, "leftandRight"), self.ID)
		
class SungillStreamrunner(Minion):
	Class, race, name = "Paladin", "Murloc", "Sungill Streamrunner"
	mana, attack, health = 1, 1, 1
	index = "Outlands~Paladin~Minion~1~1~1~Murloc~Sungill Streamrunner~Uncollectible"
	requireTarget, keyWord, description = False, "", ""
	
	
class LibramManaAura:
	def __init__(self, Game, ID, changeby=0, changeto=-1):
		self.blank_init(Game, ID, changeby, changeto)
		
	def blank_init(self, Game, ID, changeby, changeto):
		self.Game, self.ID = Game, ID
		self.changeby, self.changeto = changeby, changeto
		self.auraAffected = [] #A list of (minion, aura_Receiver)
		
	def applicable(self, target):
		return target.ID == self.ID and target.name.startswith("Libram of")
		
	#只要是有满足条件的卡牌进入手牌，就会触发这个光环。target是承载这个牌的列表。
	#applicable不需要询问一张牌是否在手牌中。光环只会处理在手牌中的卡牌
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.applicable(target[0])
		
	def trigger(self, signal, ID, subject, target, number, comment, choice=0):
		if self.canTrigger(signal, ID, subject, target, number, comment):
			self.effect(signal, ID, subject, target, number, comment)
			
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.applies(target[0])
		
	def applies(self, target): #This target is NOT holder.
		if self.applicable(target):
			PRINT(self, "Card %s gains the Changeby %d/Changeto %d mana change"%(target.name, self.changeby, self.changeto))
			manaMod = ManaModification(target, self.changeby, self.changeto, self)
			manaMod.applies()
			self.auraAffected.append((target, manaMod))
			
	def auraAppears(self):
		PRINT(self, "Aura", self, "starts")
		for card in self.Game.Hand_Deck.hands[1] + self.Game.Hand_Deck.hands[2]:
			self.applies(card)
			
		#Only need to handle minions that appear. Them leaving/silenced will be handled by the BuffAura_Receiver object.
		#We want this Trigger_MinionAppears can handle everything including registration and buff and removing.
		self.Game.triggersonBoard[self.ID].append((self, "CardEntersHand"))
		self.Game.ManaHandler.calcMana_All()
		
	#Aura is permanent and doesn't have auraDisappears()
	def selfCopy(self, recipientGame): #The recipient is the entity that deals the Aura.
		return type(self)(recipientGame, self.ID, self.changeby, self.changeto)
		
		
class AldorAttendant(Minion):
	Class, race, name = "Paladin", "", "Aldor Attendant"
	mana, attack, health = 2, 2, 3
	index = "Outlands~Paladin~Minion~2~2~3~None~Aldor Attendant~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Reduce the Cost of your Librams by (1) this game"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		PRINT(self, "Aldor Attendant's battlecry reduces the Cost of player's Librams by (1) this game")
		aura = LibramManaAura(self.Game, self.ID, -1, -1)
		self.Game.auras.append(aura)
		aura.auraAppears()
		return None
		
		
class HandofAdal(Spell):
	Class, name = "Paladin",  "Hand of A'dal"
	requireTarget, mana = True, 2
	index = "Outlands~Paladin~Spell~2~Hand of A'dal"
	description = "Give a minion +2/+2. Draw a card"
	def targetExists(self, choice=0):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if target != None:
			PRINT(self, "Hand of A'dal gives minion %s +2/+2 and lets player draw a card")
			target.buffDebuff(2, 2)
		self.Game.Hand_Deck.drawCard(self.ID)
		return target
		
		
class MurgurMurgurgle(Minion):
	Class, race, name = "Paladin", "Murloc", "Murgur Murgurgle"
	mana, attack, health = 2, 2, 1
	index = "Outlands~Paladin~Minion~2~2~1~Murloc~Murgur Murgurgle~Divine Shield~Deathrattle~Legendary"
	requireTarget, keyWord, description = False, "Divine Shield", "Divine Shield. Deathrattle: Shuffle 'Murgurgle Prime' into your deck"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [ShuffleMurgurglePrimeintoYourDeck(self)]
		
class ShuffleMurgurglePrimeintoYourDeck(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self, "Deathrattle: Shuffle 'Murgurgle Prime' into your deck triggers")
		self.entity.Game.Hand_Deck.shuffleCardintoDeck(MurgurglePrime(self.entity.Game, self.entity.ID), self.entity.ID)
		
class MurgurglePrime(Minion):
	Class, race, name = "Paladin", "Murloc", "Murgurgle Prime"
	mana, attack, health = 8, 6, 3
	index = "Outlands~Paladin~Minion~8~6~3~Murloc~Murgurgle Prime~Divine Shield~Battlecry~Legendary~Uncollectible"
	requireTarget, keyWord, description = False, "Divine Shield", "Divine Shield. Battlecry: Summon 4 random Murlocs. Give them Divine Shield"
	poolIdentifier = "Murlocs to Summon"
	@classmethod
	def generatePool(cls, Game):
		return "Murlocs to Summon", list(Game.MinionswithRace["Murloc"].values())
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		PRINT(self, "Murgurgle Prime's battlecry summons 4 random Murlocs and gives them Divine Shield")
		murlocs = [murloc(self.Game, self.ID) for murloc in np.random.choice(self.Game.RNGPools["Murlocs to Summon"], 4, replace=True)]
		#假设召唤位置是在右边，而非左右各两个
		self.Game.summonMinion(murlocs, (self.position, "totheRight"), self.ID)
		for i in range(4): #假设是召唤完全部4个之后给予它们圣盾
			if murlocs[i].onBoard:
				murlocs[i].getsKeyword("Divine Shield")
		return None
		
		
class LibramofWisdom(Spell):
	Class, name = "Paladin",  "Libram of Wisdom"
	requireTarget, mana = True, 2
	index = "Outlands~Paladin~Spell~2~Libram of Wisdom"
	description = "Give a minion +1/+1 and 'Deathrattle: Add a 'Libram of Wisdom' spell to your hand'"
	def targetExists(self, choice=0):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if target != None and (target.onBoard or target.inHand):
			PRINT(self, "Libram of Wisdom gives minion %s +1/+1 and Deathrattle: Add a 'Libram of Wisdom' to your hand."%target.name)
			target.buffDebuff(1, 1)
			trigger = AddaLibramofWisdomtoYourHand(target)
			target.deathrattles.append(trigger)
			if target.onBoard:
				trigger.connect()
		return target
		
class AddaLibramofWisdomtoYourHand(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self, "Deathrattle: Add a 'Libram of Wisdom' to your hand triggers.")
		self.entity.Game.Hand_Deck.addCardtoHand(LibramofWisdom, self.entity.ID, "CreateUsingType")
		
		
class UnderlightAnglingRod(Weapon):
	Class, name, description = "Paladin", "Underlight Angling Rod", "After your hero attacks, add a random Murloc to your hand"
	mana, attack, durability = 3, 3, 2
	index = "Outlands~Paladin~Weapon~3~3~2~Underlight Angling Rod"
	poolIdentifier = "Murlocs"
	@classmethod
	def generatePool(cls, Game):
		return "Murlocs", list(Game.MinionswithRace["Murloc"].values())
		
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_UnderlightAnglingRod(self)]
		
class Trigger_UnderlightAnglingRod(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["HeroAttackedMinion", "HeroAttackedHero"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return subject == self.entity.Game.heroes[self.entity.ID] and self.entity.onBoard
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self, "After player attacks, weapon %s adds a random Murloc to player's hand."%self.entity.name)
		self.entity.Game.Hand_Deck.addCardtoHand(np.random.choice(self.entity.Game.RNGPools["Murlocs"]), self.entity.ID, "CreateUsingType")
		
		
class AldorTruthseeker(Minion):
	Class, race, name = "Paladin", "", "Aldor Truthseeker"
	mana, attack, health = 5, 4, 6
	index = "Outlands~Paladin~Minion~5~4~6~None~Aldor Truthseeker~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Reduce the Cost of your Librams by (2) this game"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		PRINT(self, "Aldor Truthseeker's battlecry reduces the Cost of player's Librams by (2) this game")
		aura = LibramManaAura(self.Game, self.ID, -2, -1)
		self.Game.auras.append(aura)
		aura.auraAppears()
		return None
		
		
class LibramofJustice(Spell):
	Class, name = "Paladin",  "Libram of Justice"
	requireTarget, mana = False, 6
	index = "Outlands~Paladin~Spell~6~Libram of Justice"
	description = "Equip a 1/4 weapon. Change the Health of all enemy minions to 1"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		PRINT(self, "Libram of Justice is cast. Player equips a 1/4 Weapon and the Health of all enemy minions is changed to 1")
		self.Game.equipWeapon(OverdueJustice(self.Game, self.ID))
		for minion in fixedList(self.Game.minionsonBoard(3-self.ID)):
			minion.statReset(False, 1)
		return None
		
class OverdueJustice(Weapon):
	Class, name, description = "Paladin", "UnOverdue Justiceknown", ""
	mana, attack, durability = 1, 1, 4
	index = "Outlands~Paladin~Weapon~1~1~4~Overdue Justice~Uncollectible"
	
class LadyLiadrin(Minion):
	Class, race, name = "Paladin", "", "Lady Liadrin"
	mana, attack, health = 7, 4, 6
	index = "Outlands~Paladin~Minion~7~4~6~None~Lady Liadrin~Battlecry~Legendary"
	requireTarget, keyWord, description = False, "", "Battlecry: Add a copy of each spell you cast on friendly characters this game to your hand"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		PRINT(self, "Lady Liadrin's battlecry adds a copy of each spell player cast on friendly characters this game")
		spellsCastonFriendlies = copy.deepcopy(self.Game.CounterHandler.spellsCastonFriendliesThisGame[self.ID])
		np.random.shuffle(spellsCastonFriendlies)
		for index in spellsCastonFriendlies:
			if self.Game.Hand_Deck.handNotFull(self.ID):
				self.Game.Hand_Deck.addCardtoHand(index, self.ID, "CreateUsingIndex")
		return None
		
		
class LibramofHope(Spell):
	Class, name = "Paladin", "Libram of Hope"
	requireTarget, mana = True, 9
	index = "Outlands~Paladin~Spell~9~Libram of Hope"
	description = "Reestore 8 Health. Summon an 8/8 with Guardian with Taunt and Divine Shield"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if target != None:
			heal = 8 * (2 ** self.countHealDouble())
			PRINT(self, "Libram of Hope is cast, restores %d Health to %s and summons an 8/8 Guardian with Taunt and Divine Shield"%(heal, target.name))
			self.restoresHealth(target, heal)
			self.Game.summonMinion(AncientGuardian(self.Game, self.ID), -1, self.ID)
		return target
		
class AncientGuardian(Minion):
	Class, race, name = "Paladin", "", "Ancient Guardian"
	mana, attack, health = 8, 8, 8
	index = "Outlands~Paladin~Minion~8~8~8~None~Ancient Guardian~Taunt~Divine Shield~Uncollectible"
	requireTarget, keyWord, description = False, "Taunt,Divine Shield", "Taunt, Divine Shield"
	
"""Priest cards"""
class ImprisonedHomunculus(Minion_Dormantfor2turns):
	Class, race, name = "Priest", "Demon", "Imprisoned Homunculus"
	mana, attack, health = 1, 2, 5
	index = "Outlands~Priest~Minion~1~2~5~Demon~Imprisoned Homunculus~Taunt"
	requireTarget, keyWord, description = False, "Taunt", "Dormant for 2 turns. Taunt"
	
	
class ReliquaryofSouls(Minion):
	Class, race, name = "Priest", "", "Reliquary of Souls"
	mana, attack, health = 1, 1, 3
	index = "Outlands~Priest~Minion~1~1~3~None~Reliquary of Souls~Lifesteal~Deathrattle~Legendary"
	requireTarget, keyWord, description = False, "Lifesteal", "Lifesteal. Deathrattle: Shuffle 'Leliquary Prime' into your deck"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [ShuffleReliquaryPrimeintoYourDeck(self)]
		
class ShuffleReliquaryPrimeintoYourDeck(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self, "Deathrattle: Shuffle 'Reliquary Prime' into your deck triggers")
		self.entity.Game.Hand_Deck.shuffleCardintoDeck(ReliquaryPrime(self.entity.Game, self.entity.ID), self.entity.ID)
		
class ReliquaryPrime(Minion):
	Class, race, name = "Priest", "", "Reliquary Prime"
	mana, attack, health = 7, 6, 8
	index = "Outlands~Paladin~Minion~7~6~8~None~Reliquary Prime~Taunt~Lifesteal~Legendary~Uncollectible"
	requireTarget, keyWord, description = False, "Taunt,Lifesteal", "Taunt, Lifesteal. Only you can target this with spells and Hero Powers"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.marks["Enemy Evasive"] = 1
		
		
class Renew(Spell):
	Class, name = "Priest", "Renew"
	requireTarget, mana = True, 1
	index = "Outlands~Priest~Spell~1~Renew"
	description = "Restore 3 Health. Discover a spell"
	poolIdentifier = "Priest Spells"
	@classmethod
	def generatePool(cls, Game):
		classes, lists = [], []
		for Class in Classes:
			classes.append(Class+" Spells")
			spellsinClass = []
			for key, value in Game.ClassCards[Class].items():
				if "~Spell~" in key:
					spellsinClass.append(value)
			lists.append(spellsinClass)
		return classes, lists
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if target != None:
			heal = 3 * (2 ** self.countHealDouble())
			PRINT(self, "Renew restores %d Health to"%heal)
			self.restoresHealth(target, heal)
		if self.Game.Hand_Deck.handNotFull(self.ID):
			key = classforDiscover(self)+" Spells"
			if "InvokedbyOthers" in comment:
				PRINT(self, "Renew adds a random spell to player's hand")
				self.Game.Hand_Deck.addCardtoHand(np.random.choice(self.Game.RNGPools[key]), self.ID, "CreateUsingType")
			else:
				PRINT(self, "Renew lets player discover a spell")
				spells = np.random.choice(self.Game.RNGPools[key], 3, replace=False)
				self.Game.options = [spell(self.Game, self.ID) for spell in spells]
				self.Game.DiscoverHandler.startDiscover(self)
		return target
		
	def discoverDecided(self, option):
		PRINT(self, "Spell %s is put into player's hand."%option.name)
		self.Game.Hand_Deck.addCardtoHand(option, self.ID)
		self.Game.sendSignal("DiscoveredCardPutintoHand", self.ID, self, option, 0, "")
		
		
class DragonmawSentinel(Minion):
	Class, race, name = "Priest", "", "Dragonmaw Sentinel"
	mana, attack, health = 2, 1, 4
	index = "Outlands~Priest~Minion~2~1~4~None~Dragonmaw Sentinel~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: If you're holding a Dragon, gain +1 Attack and Lifesteal"
	
	def effectCanTrigger(self): #Friendly characters are always selectable.
		self.effectViable = self.Game.Hand_Deck.holdingDragon(self.ID)
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if self.Game.Hand_Deck.holdingDragon(self.ID):
			PRINT(self, "Dragonmaw Sentinel's battlecry gives minion +1 Attack and Lifesteal")
			self.buffDebuff(1, 0)
			self.getsKeyword("Lifesteal")
		return None
		
		
class SethekkVeilweaver(Minion):
	Class, race, name = "Priest", "", "Sethekk Veilweaver"
	mana, attack, health = 2, 2, 3
	index = "Outlands~Priest~Minion~2~2~3~None~Sethekk Veilweaver"
	requireTarget, keyWord, description = False, "", "After you cast a spell on a minion, add a Priest spell to your hand"
	poolIdentifier = "Priest Spells"
	@classmethod
	def generatePool(cls, Game):
		priestSpells = []
		for key, value in Game.ClassCards["Priest"].items():
			if "~Spell~" in key:
				priestSpells.append(value)
		return "Priest Spells", priestSpells
		
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_SethekkVeilweaver(self)]
		
class Trigger_SethekkVeilweaver(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["SpellBeenPlayed"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject.ID == self.entity.ID and target != None and target.cardType == "Minion"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self, "After player casts spell %s on minion %s, %s adds a random Priest spell to player's hand"%(subject.name, target.name, self.entity.name))
		self.entity.Game.Hand_Deck.addCardtoHand(np.random.choice(self.entity.Game.RNGPools["Priest Spells"]), self.entity.ID, "CreateUsingType")
		
		
class Apotheosis(Spell):
	Class, name = "Priest", "Apotheosis"
	requireTarget, mana = True, 3
	index = "Outlands~Priest~Spell~3~Apotheosis"
	description = "Give a minion +2/+3 and Lifesteal"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.onBoard
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if target != None:
			PRINT(self, "Apotheosis is cast and gives minion %s +2/+3 and Lifesteal"%target.name)
			target.buffDebuff(2, 3)
			target.getsKeyword("Lifesteal")
		return target
		
		
class DragonmawOverseer(Minion):
	Class, race, name = "Priest", "", "Dragonmaw Overseer"
	mana, attack, health = 3, 2, 2
	index = "Outlands~Priest~Minion~3~2~2~None~Dragonmaw Overseer"
	requireTarget, keyWord, description = False, "", "At the end of your turn, give another friendly minion +2/+2"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_DragonmawOverseer(self)]
		
class Trigger_DragonmawOverseer(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["TurnEnds"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		targets = self.entity.Game.minionsonBoard(self.entity.ID)
		extractfrom(self.entity, targets)
		if targets != []:
			target = np.random.choice(targets)
			PRINT(self, "At the end of turn, %s gives friendly minion %s +2/+2"%(self.entity.name, target.name))
			target.buffDebuff(2, 2)
			
			
class PsycheSplit(Spell):
	Class, name = "Priest", "Psyche Split"
	requireTarget, mana = True, 5
	index = "Outlands~Priest~Spell~5~Psyche Split"
	description = "Give a minion +1/+2. Summon a copy of it"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if target != None:
			PRINT(self, "Psyche Split is cast, gives minion %s +1/+2 and summons a copy of it"%target.name)
			target.buffDebuff(1, 2)
			Copy = target.selfCopy(target.ID)
			self.Game.summonMinion(Copy, target.position+1, self.ID)
		return target
		
		
class SkeletalDragon(Minion):
	Class, race, name = "Priest", "Dragon", "Skeletal Dragon"
	mana, attack, health = 7, 4, 9
	index = "Outlands~Priest~Minion~7~4~9~Dragon~Skeletal Dragon~Taunt"
	requireTarget, keyWord, description = False, "Taunt", "Taunt. At the end of your turn, add a Dragon to your hand"
	poolIdentifier = "Dragons"
	@classmethod
	def generatePool(cls, Game):
		return "Dragons", list(Game.MinionswithRace["Dragon"].values())
		
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_SkeletalDragon(self)]
		
class Trigger_SkeletalDragon(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["TurnEnds"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self, "At the end of turn, %s adds a random Dragon to player's hand"%self.entity.name)
		dragon = np.random.choice(self.entity.Game.RNGPools["Dragons"])
		self.entity.Game.Hand_Deck.addCardtoHand(dragon, self.entity.ID, "CreateUsingType")
		
		
class SoulMirror(Spell):
	Class, name = "Priest", "Soul Mirror"
	requireTarget, mana = False, 7
	index = "Outlands~Priest~Spell~7~Soul Mirror~Legendary"
	description = "Summon copies of enemy minions. They attack their copies"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		PRINT(self, "Soul Mirror is cast, summons copies of enemy minions and make them attack their copies")
		pairs, copies = [], []
		for minion in self.Game.minionsonBoard(3-self.ID):
			Copy = minion.selfCopy(self.ID)
			copies.append(Copy)
			pairs.append((minion, Copy))
		if copies != []:
			if self.Game.summonMinion(copies, (-1, "totheRightEnd"), self.ID):
				for minion, Copy in pairs:
					if minion.onBoard and minion.health > 0 and minion.dead == False and Copy.onBoard and Copy.health > 0 and Copy.dead == False:
						PRINT(self, "%s is forced to attack its copy"%minion.name)
						#假设不消耗攻击机会，那些随从在攻击之后被我方拐走仍然可以攻击
						self.Game.battleRequest(minion, Copy, False, False)
		return None
		
		
"""Rogue cards"""
class BlackjackStunner(Minion):
	Class, race, name = "Rogue", "", "Blackjack Stunner"
	mana, attack, health = 1, 1, 2
	index = "Outlands~Rogue~Minion~1~1~2~None~Blackjack Stunner~Battlecry"
	requireTarget, keyWord, description = True, "", "Battlecry: If you control a Secret, return a minion to its owner's hand. It costs (2) more"
	def effectCanTrigger(self):
		self.effectViable = self.Game.SecretHandler.secrets[self.ID] != []
		
	def returnTrue(self, choice=0):
		return self.Game.SecretHandler.secrets[self.ID] != []
		
	def targetExists(self, choice=0):
		return self.selectableMinionExists(choice)
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target != self and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		#假设第二次生效时不会不在场上的随从生效
		if target != None and target.onBoard:
			PRINT(self, "Blackjack Stunner's battlecry returns %s to owner's hand."%target.name)
			#假设那张随从在进入手牌前接受-2费效果。可以被娜迦海巫覆盖。
			manaMod = ManaModification(target, changeby=+2, changeto=-1)
			self.Game.returnMiniontoHand(target, keepDeathrattlesRegistered=False, manaModification=manaMod)
		return target
		
		
class Spymistress(Minion):
	Class, race, name = "Rogue", "", "Spymistress"
	mana, attack, health = 1, 3, 1
	index = "Outlands~Rogue~Minion~1~3~1~None~Spymistress~Stealth"
	requireTarget, keyWord, description = False, "Stealth", "Stealth"
	
	
class Ambush(Secret):
	Class, name = "Rogue", "Ambush"
	requireTarget, mana = False, 2
	index = "Outlands~Rogue~Spell~2~Ambush~~Secret"
	description = "After your opponent plays a minion, summon a 2/3 Ambusher with Poisonous"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_Ambush(self)]
		
class Trigger_Ambush(SecretTrigger):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionBeenPlayed"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.ID != self.entity.Game.turn and subject.ID != self.entity.ID and self.entity.Game.spaceonBoard(self.entity.ID) > 0
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self, "After enemy minion %s is played, Secret Ambush is triggered and summons a 2/3 Ambusher with Poisonous."%subject.name)
		self.entity.Game.summonMinion(BrokenAmbusher(self.entity.Game, self.entity.ID), -1, self.entity.ID)
		
class BrokenAmbusher(Minion):
	Class, race, name = "Rogue", "", "Broken Ambusher"
	mana, attack, health = 2, 2, 3
	index = "Outlands~Rogue~Minion~2~2~3~None~Broken Ambusher~Poisonous~Uncollectible"
	requireTarget, keyWord, description = False, "Poisonous", "Poisonous"
	
	
class AshtongueSlayer(Minion):
	Class, race, name = "Rogue", "", "Ashtongue Slayer"
	mana, attack, health = 2, 3, 2
	index = "Outlands~Rogue~Minion~2~3~2~None~Ashtongue Slayer~Battlecry"
	requireTarget, keyWord, description = True, "", "Battlecry: Give a Stealthed minion +3 Attack and Immune this turn"
	def targetExists(self, choice=0):
		return self.selectableFriendlyMinionExists(choice)
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target != self and (target.keyWords["Stealth"] > 0 or target.status["Temp Stealth"] > 0) and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if target != None:
			PRINT(self, "Ashtongue Slayer's battlecry gives Stealthed minion %s +3 Attack and Immune this turn"%target.name)
			target.buffDebuff(3, 0, "EndofTurn")
			target.status["Immune"] += 1
		return target
		
		
class Bamboozle(Secret):
	Class, name = "Rogue", "Bamboozle"
	requireTarget, mana = False, 2
	index = "Outlands~Rogue~Spell~2~Bamboozle~~Secret"
	description = "When one of your minions is attacked, transform it into a random one that costs (3) more"
	poolIdentifier = "3-Cost Minions to Summon"
	@classmethod
	def generatePool(cls, Game):
		costs, lists = [], []
		for cost in Game.MinionsofCost.keys():
			costs.append("%d-Cost Minions to Summon"%cost)
			lists.append(list(Game.MinionsofCost[cost].values()))
		return costs, lists
		
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_Bamboozle(self)]
		
class Trigger_Bamboozle(SecretTrigger):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionAttacksMinion", "HeroAttacksMinion"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.ID != self.entity.Game.turn and target[0].ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self, "When friendly minion %s is attacked, Secret Bamboozle triggers and transforms it into a random one that costs (3) more"%target[0].name)
		#不知道如果攻击目标已经被导离这个目标随从之后是否会把目标重导向回它，假设不会
		newMinion = self.entity.Game.mutate(target[0], +3)
		if target[0] == target[1]:
			target[0], target[1] = newMinion, newMinion
		else:
			target[0] = newMinion
			
			
class DirtyTricks(Secret):
	Class, name = "Rogue", "Dirty Tricks"
	requireTarget, mana = False, 2
	index = "Outlands~Rogue~Spell~2~Dirty Tricks~~Secret"
	description = "After your opponent casts a spell, draw 2 cards"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_DirtyTricks(self)]
		
class Trigger_DirtyTricks(SecretTrigger):
	def __init__(self, entity):
		self.blank_init(entity, ["SpellBeenPlayed"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.ID != self.entity.Game.turn and subject.ID != self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self, "After the opponent casts a spell, Secret Dirty Tricks is triggered and lets player draw 2 cards")
		self.entity.Game.Hand_Deck.drawCard(self.entity.ID)
		self.entity.Game.Hand_Deck.drawCard(self.entity.ID)
		
		
class ShadowjewelerHanar(Minion):
	Class, race, name = "Rogue", "", "Shadowjeweler Hanar"
	mana, attack, health = 2, 1, 5
	index = "Outlands~Rogue~Minion~2~1~5~None~Shadowjeweler Hanar~Legendary"
	requireTarget, keyWord, description = False, "", "After you play a Secret, Discover a Secret from a different class"
	poolIdentifier = "Rogue Secrets"
	@classmethod
	def generatePool(cls, Game):
		classes, lists = [], []
		secrets = {}
		for Class in Classes:
			for key, value in Game.ClassCards[Class].items():
				if "~~Secret" in key:
					if Class not in secrets.keys():
						secrets[Class] = [value]
					else:
						secrets[Class].append(value)
		for key, value in secrets.items():
			classes.append(key+" Secrets")
			lists.append(value)
		return classes, lists
		
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_ShadowjewelerHanar(self)]
		
	def discoverDecided(self, option):
		PRINT(self, "Secret %s is put into player's hand"%option.name)
		self.Game.Hand_Deck.addCardtoHand(option, self.ID)
		self.Game.sendSignal("DiscoveredCardPutintoHand", self.ID, self, option, 0, "")
		
class Trigger_ShadowjewelerHanar(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["SpellBeenPlayed"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject.ID == self.entity.ID and "~~Secret" in subject.index
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		if self.entity.ID == self.entity.Game.turn and self.entity.Game.Hand_Deck.handNotFull(self.entity.ID):
			PRINT(self, "After player plays a Secret, %s lets player Discover a Secret from a different class"%self.entity.name)
			ClasseswithSecrets = ["Hunter", "Mage", "Paladin", "Rogue"]
			extractfrom(subject.Class, ClasseswithSecrets)
			Classes = np.random.choice(ClasseswithSecrets, 3, replace=False)
			secrets = []
			for Class in Classes:
				secrets.append(np.random.choice(self.entity.Game.RNGPools[Class+" Secrets"]))
			self.entity.Game.options = [secret(self.entity.Game, self.entity.ID) for secret in secrets]
			self.entity.Game.DiscoverHandler.startDiscover(self.entity)
			
			
class Akama(Minion):
	Class, race, name = "Rogue", "", "Akama"
	mana, attack, health = 3, 3, 4
	index = "Outlands~Rogue~Minion~3~3~4~None~Akama~Stealth~Deathrattle~Legendary"
	requireTarget, keyWord, description = False, "Stealth", "Stealth. Deathrattle: Shuffle 'Akama Prime' into your deck"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [ShuffleAkamaPrimeintoYourDeck(self)]
		
class ShuffleAkamaPrimeintoYourDeck(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self, "Deathrattle: Shuffle 'Akama Prime' into your deck triggers")
		self.entity.Game.Hand_Deck.shuffleCardintoDeck(AkamaPrime(self.entity.Game, self.entity.ID), self.entity.ID)
		
class AkamaPrime(Minion):
	Class, race, name = "Rogue", "", "Akama Prime"
	mana, attack, health =6, 6, 5
	index = "Outlands~Rogue~Minion~6~6~5~None~Akama Prime~Stealth~Legendary~Uncollectible"
	requireTarget, keyWord, description = False, "Stealth", "Permanently Stealthed"
	
	def losesKeyword(self, keyWord):
		if self.onBoard or self.inHand:
			if keyWord == "Stealth":
				if self.silenced: #只有在被沉默的时候才会失去潜行
					self.keyWords["Stealth"] = 0
				else:
					PRINT(self, "Akama Prime can't lose Stealth without being Silenced.")
			elif keyWord == "Divine Shield":
				self.keyWords["Divine Shield"] = 0
				self.Game.sendSignal("MinionLosesDivineShield", self.Game.turn, None, self, 0, "")
			else:
				if self.keyWords[keyWord] > 0:
					self.keyWords[keyWord] -= 1
			if self.onBoard:
				self.decideAttChances_base()
				if keyWord == "Charge":
					self.Game.sendSignal("MinionChargeKeywordChange", self.Game.turn, self, None, 0, "")
				self.STATUSPRINT()
				
				
class GreyheartSage(Minion):
	Class, race, name = "Rogue", "", "Greyheart Sage"
	mana, attack, health = 3, 3, 3
	index = "Outlands~Rogue~Minion~3~3~3~None~Greyheart Sage~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: If you control a Stealth minion, draw 2 cards"
	def effectCanTrigger(self):
		self.effectViable = False
		for minion in self.Game.minionsonBoard(self.ID):
			if minion.keyWords["Stealth"] > 0 or minion.status["Temp Stealth"] > 0:
				self.effectViable = True
				break
				
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		controlStealthMinion = False
		for minion in self.Game.minionsonBoard(self.ID):
			if minion.keyWords["Stealth"] > 0 or minion.status["Temp Stealth"] > 0:
				controlStealthMinion = True
				break
		if controlStealthMinion:
			PRINT(self, "Greyheart Sage's battlecry lets player draw 2 cards")
			self.Game.Hand_Deck.drawCard(self.ID)
			self.Game.Hand_Deck.drawCard(self.ID)
		return None
		
		
class CursedVagrant(Minion):
	Class, race, name = "Rogue", "", "Cursed Vagrant"
	mana, attack, health = 7, 7, 5
	index = "Outlands~Rogue~Minion~7~7~5~None~Cursed Vagrant~Deathrattle"
	requireTarget, keyWord, description = False, "", "Deathrattle: Summon a 7/5 Shadow with Stealth"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [SummonaShadowwithTaunt(self)]
		
class SummonaShadowwithTaunt(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self, "Deathrattle: Summon a 7/5 Shadow with Stealth triggers")
		self.entity.Game.summonMinion(CursedShadow(self.entity.Game, self.entity.ID), self.entity.position+1, self.entity.ID)
		
class CursedShadow(Minion):
	Class, race, name = "Rogue", "", "Cursed Shadow"
	mana, attack, health = 7, 7, 5
	index = "Outlands~Rogue~Minion~7~7~5~None~Cursed Shadow~Stealth~Uncollectible"
	requireTarget, keyWord, description = False, "Stealth", "Stealth"
	
	
"""Shaman cards"""
class BogstrokClacker(Minion):
	Class, race, name = "Shaman", "", "Bogstrok Clacker"
	mana, attack, health = 3, 3, 3
	index = "Outlands~Shaman~Minion~3~3~3~None~Bogstrok Clacker~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Transform adjacent minions into random minions that cost (1) more"
	poolIdentifier = "1-Cost Minions to Summon"
	@classmethod
	def generatePool(cls, Game):
		costs, lists = [], []
		for cost in Game.MinionsofCost.keys():
			costs.append("%d-Cost Minions to Summon"%cost)
			lists.append(list(Game.MinionsofCost[cost].values()))
		return costs, lists
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if self.onBoard:
			PRINT(self, "Bogstrok Clacker's battlecry transforms adjacent minions into ones that cost (1) more")
			for minion in self.Game.findAdjacentMinions(self)[0]:
				self.Game.mutate(minion, +1)
		return None
		
		
class LadyVashj(Minion):
	Class, race, name = "Shaman", "", "Lady Vashj"
	mana, attack, health = 3, 4, 3
	index = "Outlands~Shaman~Minion~3~4~3~None~Lady Vashj~Spell Damage~Deathrattle~Legendary"
	requireTarget, keyWord, description = False, "Spell Damage", "Spell Damage +1. Deathrattle: Shuffle 'Vashj Prime' into your deck"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [ShuffleVashjPrimeintoYourDeck(self)]
		
class ShuffleVashjPrimeintoYourDeck(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self, "Deathrattle: Shuffle Vashj Prime into your deck triggers")
		self.entity.Game.Hand_Deck.shuffleCardintoDeck(VashjPrime(self.entity.Game, self.entity.ID), self.entity.ID)
		
class VashjPrime(Minion):
	Class, race, name = "Shaman", "", "Vashj Prime"
	mana, attack, health = 7, 5, 4
	index = "Outlands~Shaman~Minion~7~5~4~None~Vashj Prime~Spell Damage~Battlecry~Legendary~Uncollectible"
	requireTarget, keyWord, description = False, "Spell Damage", "Spell Damage +1. Battlecry: Draw 3 spells. Reduce their Cost by (3)"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		for i in range(3):
			spellsinDeck = []
			for card in self.Game.Hand_Deck.decks[self.ID]:
				if card.cardType == "Spell":
					spellsinDeck.append(card)
					
			if spellsinDeck != []:
				spell, mana = self.Game.Hand_Deck.drawCard(self.ID, np.random.choice(spellsinDeck))
				if spell != None:
					ManaModification(spell, changeby=-3, changeto=-1).applies()
		return None
		
		
class Marshspawn(Minion):
	Class, race, name = "Shaman", "Elemental", "Marshspawn"
	mana, attack, health = 3, 3, 4
	index = "Outlands~Shaman~Minion~3~3~4~Elemental~Marshspawn~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: If you cast a spell last turn, Discover a spell"
	poolIdentifier = "Shaman Spells"
	@classmethod
	def generatePool(cls, Game):
		classes, lists = [], []
		for Class in Classes:
			classes.append(Class+" Spells")
			spellsinClass = []
			for key, value in Game.ClassCards[Class].items():
				if "~Spell~" in key:
					spellsinClass.append(value)
			lists.append(spellsinClass)
		return classes, lists
		
	def effectCanTrigger(self):
		self.effectViable = self.Game.CounterHandler.spellsPlayedLastTurn[self.ID] != []
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if self.Game.CounterHandler.spellsPlayedLastTurn[self.ID] != []:
			if self.ID == self.Game.turn and self.Game.Hand_Deck.handNotFull(self.ID):
				key = classforDiscover(self)+" Spells"
				if "InvokedbyOthers" in comment:
					PRINT(self, "Marshspawn's battlecry adds a random spell to player's hand")
					self.Game.Hand_Deck.addCardtoHand(np.random.choice(self.Game.RNGPools[key]), self.ID, "CreateUsingType")
				else:
					PRINT(self, "Marshspawn's battlecry lets player discover a spell")
					spells = np.random.choice(self.Game.RNGPools[key], 3, replace=False)
					self.Game.options = [spell(self.Game, self.ID) for spell in spells]
					self.Game.DiscoverHandler.startDiscover(self)
					
		return None
		
	def discoverDecided(self, option):
		PRINT(self, "Spell %s is put into player's hand."%option.name)
		self.Game.Hand_Deck.addCardtoHand(option, self.ID)
		self.Game.sendSignal("DiscoveredCardPutintoHand", self.ID, self, option, 0, "")
		
		
class SerpentshrinePortal(Spell):
	Class, name = "Shaman", "Serpentshrine Portal"
	requireTarget, mana = True, 3
	index = "Outlands~Shaman~Spell~3~Serpentshrine Portal~Overload"
	description = "Deal 3 damage. Summon a random 3-Cost minion. Overload: (1)"
	poolIdentifier = "3-Cost Minions"
	@classmethod
	def generatePool(cls, Game):
		return "3-Cost Minions", list(Game.MinionsofCost[3].values())
		
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.overload = 1
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if target != None:
			damage = (3 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			PRINT(self, "Serpentshrine Portal is cast and deals %d damage to %s"%(damage, target.name))
			self.dealsDamage(target, damage)
		PRINT(self, "Serpentshrine Portal summons a random 3-Cost minion")
		minion = np.random.choice(self.Game.RNGPools["3-Cost Minions"])
		self.Game.summonMinion(minion(self.Game, self.ID), -1, self.ID)
		return target
		
		
class TotemicReflection(Spell):
	Class, name = "Shaman", "Totemic Reflection"
	requireTarget, mana = True, 3
	index = "Outlands~Shaman~Spell~3~Totemic Reflection"
	description = "Give a minion +2/2. If it's a Totem, summon a copy of it"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.onBoard
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if target != None:
			PRINT(self, "Totemic Reflection is cast and gives minion %s +2/+2"%target.name)
			target.buffDebuff(2, 2)
			if "Totem" in target.race:
				PRINT(self, "The target is Totem and Totemic Reflection summons a copy of it")
				Copy = target.selfCopy(target.ID)
				self.Game.summonMinion(Copy, target.position+1, self.ID)
		return target
		
		
class VividSpores(Spell):
	Class, name = "Shaman", "Vivid Spores"
	requireTarget, mana = False, 4
	index = "Outlands~Shaman~Spell~4~Vivid Spores"
	description = "Give your minions 'Deathrattle: Resummon this minion'"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		PRINT(self, "Vivid Spores is cast and gives friendly minions 'Deathrattle: Resummon this minion'")
		for minion in self.Game.minionsonBoard(self.ID):
			trigger = ResummonThisMinion_VividSpores(minion)
			minion.deathrattles.append(trigger)
			trigger.connect()
		return None
		
class ResummonThisMinion_VividSpores(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		#This Deathrattle can't possibly be triggered in hand
		PRINT(self, "Deathrattle: Resummon this minion %s triggers"%self.entity.name)
		self.entity.Game.summonMinion(type(self.entity)(self.entity.Game, self.entity.ID), self.entity.position+1, self.entity.ID)
		
		
class BoggspineKnuckles(Weapon):
	Class, name, description = "Shaman", "Boggspine Knuckles", "After your hero attacks, transform your minions into ones that cost (1) more"
	mana, attack, durability = 5, 4, 2
	index = "Outlands~Shaman~Weapon~5~4~2~Boggspine Knuckles"
	poolIdentifier = "1-Cost Minions"
	@classmethod
	def generatePool(cls, Game):
		costs, lists = [], []
		for cost in Game.MinionsofCost.keys():
			costs.append("%d-Cost Minions"%cost)
			lists.append(list(Game.MinionsofCost[cost].values()))
		return costs, lists
		
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_BoggspineKnuckles(self)]
		
class Trigger_BoggspineKnuckles(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["HeroAttackedMinion", "HeroAttackedHero"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return subject == self.entity.Game.heroes[self.entity.ID] and self.entity.onBoard
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self, "After player attacks, weapon %s transforms friendly minions into ones that cost (1) more."%self.entity.name)
		for minion in fixedList(self.entity.Game.minionsonBoard(self.entity.ID)):
			self.entity.Game.mutate(minion, +1)
			
			
class ShatteredRumbler(Minion):
	Class, race, name = "Shaman", "Elemental", "Shattered Rumbler"
	mana, attack, health = 5, 4, 6
	index = "Outlands~Shaman~Minion~5~4~6~Elemental~Shattered Rumbler~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: If you cast a spell last turn, deal 2 damage to all other minions"
	def effectCanTrigger(self):
		self.effectViable = self.Game.CounterHandler.spellsPlayedLastTurn[self.ID] != []
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if self.Game.CounterHandler.spellsPlayedLastTurn[self.ID] != []:
			PRINT(self, "Shattered Rumbler's battlecry deals 2 damage to all other minions")
			targets = self.Game.minionsonBoard(1) + self.Game.minionsonBoard(2)
			extractfrom(self, targets)
			self.dealsAOE(targets, [2 for minion in targets])
		return None
		
		
class Torrent(Spell):
	Class, name = "Shaman", "Torrent"
	requireTarget, mana = True, 5
	index = "Outlands~Shaman~Spell~5~Torrent"
	description = "Deal 8 damage to a minion. Costs (3) less if you cast a spell last turn"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.onBoard
		
	def effectCanTrigger(self):
		self.effectViable = self.Game.CounterHandler.spellsPlayedLastTurn[self.ID] != []
		
	def selfManaChange(self):
		if self.inHand and self.Game.CounterHandler.spellsPlayedLastTurn[self.ID] != []:
			self.mana -= 3
			self.mana = max(self.mana, 0)
			
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if target != None:
			damage = (8 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			PRINT(self, "Torrent deals %d damage to minion %s"%(damage, target.name))
			self.dealsDamage(target, damage)
		return target
		
		
class TheLurkerBelow(Minion):
	Class, race, name = "Shaman", "Beast", "The Lurker Below"
	mana, attack, health = 6, 6, 3
	index = "Outlands~Shaman~Minion~6~6~3~Beast~The Lurker Below~Battlecry~Legendary"
	requireTarget, keyWord, description = True, "", "Battlecry: Deal 3 damage to an enemy minion, it dies, repeat on one of its neighbors"
	def targetExists(self, choice=0):
		return self.selectableEnemyMinionExists(choice)
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.ID != self.ID and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		#假设战吼触发时目标随从已经死亡并离场，则不会触发接下来的伤害
		#假设不涉及强制死亡
		if target != None:
			PRINT(self, "The Lurker Below's battlecry deals 3 damage to enemy minion %s"%target.name)
			self.dealsDamage(target, 3)
			if target.onBoard and (target.health < 1 or target.dead):
				adjacentMinions, distribution = self.Game.findAdjacentMinions(target)
				nextMinion = None
				if distribution == "Minions on Both Sides":
					if np.random.randint(2) == 1:
						nextMinion, direction = adjacentMinions[1], "right"
					else:
						nextMinion, direction = adjacentMinions[0], "left"
				elif distribution == "Minions Only on the Left":
					nextMinion, direction = adjacentMinions[0], "left"
				elif distribution == "Minions Only on the Right":
					nextMinion, direction = adjacentMinions[0], "right"
					
				#当已经决定了要往哪个方向走之后
				while True:
					if nextMinion == None: #如果下个目标没有随从了，则停止循环
						break
					else: #还有下个随从
						self.dealsDamage(nextMinion, 3)
						if target.health < 1 or target.dead:
							adjacentMinions, distribution = self.Game.findAdjacentMinions(nextMinion)
							nextMinion = None
							if direction == "right":
								if distribution == "Minions on Both Sides":
									nextMinion = adjacentMinions[1]
								elif distribution == "Minions Only on the Right":
									nextMinion = adjacentMinions[0]
								else:
									break
							elif direction == "left":
								if distribution == "Minions on Both Sides" or distribution == "Minions Only on the Right":
									nextMinion = adjacentMinions[0]
								else:
									break
		return target
		
		
"""Warlock cards"""
class ShadowCouncil(Spell):
	Class, name = "Warlock", "Shadow Council"
	requireTarget, mana = False, 1
	index = "Outlands~Warlock~Spell~1~Shadow Council"
	description = "Replace your hand with random Demons. Give them +2/+2"
	poolIdentifier = "Demons"
	@classmethod
	def generatePool(cls, Game):
		return "Demons", list(Game.MinionswithRace["Demon"].values())
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		handSize = len(self.Game.Hand_Deck.hands[self.ID])
		self.Game.Hand_Deck.extractfromHand(None, True, self.ID)
		#choice will return empty lists if handSize/deckSize == 0
		minionstoHand = np.random.choice(self.Game.RNGPools["Demons"], handSize, replace=True)
		self.Game.Hand_Deck.addCardtoHand(minionstoHand, self.ID, "CreateUsingType")
		for minion in minionstoHand:
			minion.buffDebuff(2, 2)
		return None
		
		
class UnstableFelbolt(Spell):
	Class, name = "Warlock", "Unstable Felbolt"
	requireTarget, mana = True, 1
	index = "Outlands~Warlock~Spell~1~Unstable Felbolt"
	description = "Deal 3 damage to an enemy minion and a random friendly one"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		damage = (3 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		if target != None:
			PRINT(self, "Unstable Felbolt is cast and deals %d damage to enemy minion %s"%(damage, target.name))
			self.dealsDamage(target, damage)
		friendlyMinions = self.Game.minionsonBoard(self.ID)
		if friendlyMinions != []:
			minion = np.random.choice(friendlyMinions)
			PRINT(self, "Unstable Felbolt also deals %d damage to random friendly minion"%damage, minion.name)
			self.dealsDamage(minion, damage)
		return target
		
		
class ImprisonedScrapImp(Minion_Dormantfor2turns):
	Class, race, name = "Warlock", "Demon", "Imprisoned Scrap Imp"
	mana, attack, health = 2, 3, 3
	index = "Outlands~Warlock~Minion~2~3~3~Demon~Imprisoned Scrap Imp"
	requireTarget, keyWord, description = False, "", "Dormant for 2 turns. When this awakens, give all minions in your hand +2/+2"
	
	def awakenEffect(self):
		PRINT(self, "Imprisoned Scrap Imp awakens and gives all minion in player's hand +2/+2")
		for card in fixedList(self.Game.Hand_Deck.hands[self.ID]):
			if card.cardType == "Minion":
				card.buffDebuff(2, 2)
				
				
class KanrethadEbonlocke(Minion):
	Class, race, name = "Warlock", "", "Kanrethad Ebonlocke"
	mana, attack, health = 2, 3, 2
	index = "Outlands~Warlock~Minion~2~3~2~None~Kanrethad Ebonlocke~Deathrattle~Legendary"
	requireTarget, keyWord, description = False, "", "Your Demons cost (1) less. Deathrattle: Shuffle 'Kanrethad Prime' into your deck"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.auras["Mana Aura"] = ManaAura_Dealer(self, self.manaAuraApplicable, changeby=-1, changeto=-1)
		self.deathrattles = [ShuffleKanrethadPrimeintoYourDeck(self)]
		
	def manaAuraApplicable(self, subject): #ID用于判定是否是我方手中的随从
		return subject.ID == self.ID and subject.cardType == "Minion" and "Demon" in subject.race
		
class ShuffleKanrethadPrimeintoYourDeck(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self, "Deathrattle: Shuffle 'Kanrethad Prime' into your deck triggers")
		self.entity.Game.Hand_Deck.shuffleCardintoDeck(KanrethadPrime(self.entity.Game, self.entity.ID), self.entity.ID)
		
class KanrethadPrime(Minion):
	Class, race, name = "Warlock", "Demon", "Kanrethad Prime"
	mana, attack, health = 8, 7, 6
	index = "Outlands~Warlock~Minion~8~7~6~Demon~Kanrethad Prime~Battlecry~Legendary~Uncollectible"
	requireTarget, keyWord, description = False, "", "Battlecry: Summon 3 friendly Demons that died this game"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		PRINT(self, "Kanrethad Prime's battlecry summons 3 friendly Demons that died this game")
		friendlyDemonsDiedThisGame = []
		for index in self.Game.CounterHandler.minionsDiedThisTurn[self.ID]:
			if "~Demon~" in index:
				friendlyDemonsDiedThisGame.append(index)
		numDemonsDied = len(friendlyDemonsDiedThisGame)
		numSummon = min(self.Game.spaceonBoard(self.ID), numDemonsDied)
		if numSummon > 0:
			indices = np.random.choice(friendlyDemonsDiedThisGame, numSummon, replace=False)
			pos = (self.position, "totheRight") if self in self.Game.minions[self.ID] else (-1, "totheRightEnd")
			self.Game.summonMinion([self.Game.cardPool[index](self.Game, self.ID) for index in indices], pos, self.ID)		
		return None
		
		
class Darkglare(Minion):
	Class, race, name = "Warlock", "Demon", "Darkglare"
	mana, attack, health = 3, 3, 4
	index = "Outlands~Warlock~Minion~3~3~4~Demon~Darkglare"
	requireTarget, keyWord, description = False, "", "After your hero takes damage, refresh 2 Mana Crystals"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_Darkglare(self)]
		
class Trigger_Darkglare(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["HeroTookDamage"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return target == self.entity.Game.heroes[self.entity.ID]
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self, "After player takes damage, %s refreshes 2 of player's Mana Crystals"%self.entity.name)
		self.entity.Game.ManaHandler.restoreManaCrystal(2, self.entity.ID)
		
		
class NightshadeMatron(Minion):
	Class, race, name = "Warlock", "Demon", "Nightshade Matron"
	mana, attack, health = 4, 5, 5
	index = "Outlands~Warlock~Minion~4~5~5~Demon~Nightshade Matron~Rush~Battlecry"
	requireTarget, keyWord, description = False, "Rush", "Rush. Battlecry: Discard your highest Cost card"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		PRINT(self, "Nightshade Matron's battlecry discards the highest Cost card in player's hand.")
		highestMana, cardsinHand = -np.inf, []
		for card in self.Game.Hand_Deck.hands[self.ID]:
			if card.mana > highestMana:
				cardsinHand = [card]
				highestMana = card.mana
			elif card.mana == highestMana:
				cardsinHand.append(card)
		if cardsinHand != []:
			self.Game.Hand_Deck.discardCard(self.ID, np.random.choice(cardsinHand))
		return None
		
		
class TheDarkPortal(Spell):
	Class, name = "Warlock", "The Dark Portal"
	requireTarget, mana = False, 4
	index = "Outlands~Warlock~Spell~4~The Dark Portal"
	description = "Draw a minion. If you have at least 8 cards in hand, it costs (5) less"
	def effectCanTrigger(self):
		self.effectViable = len(self.Game.Hand_Deck.hands[self.ID]) > 7
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		PRINT(self, "The Dark Portal and lets player draw a minion.")
		minionsinDeck = []
		for card in self.Game.Hand_Deck.decks[self.ID]:
			if card.cardType == "Minion":
				minionsinDeck.append(card)
				
		if minionsinDeck != []:
			minion, mana = self.Game.Hand_Deck.drawCard(self.ID, np.random.choice(minionsinDeck))
			if minion != None and len(self.Game.Hand_Deck.hands[self.ID]) > 7:
				PRINT(self, "Player has at least 8 cards in hand and The Dark Portal reduces the Cost of the drawn minion by (5)")
				ManaModification(minion, changeby=-5, changeto=-1).applies()
		return None
		
		
class HandofGuldan(Spell):
	Class, name = "Warlock", "Hand of Gul'dan"
	requireTarget, mana = False, 6
	index = "Outlands~Warlock~Spell~6~Hand of Gul'dan"
	description = "When you play or discard this, draw 3 cards"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggers["Discarded"] = [self.whenEffective]
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		PRINT(self, "Hand of Gul'dan is cast/discarded and lets player draw 3 cards.")
		for i in range(3):
			self.Game.Hand_Deck.drawCard(self.ID)
		return None
		
		
class KelidantheBreaker(Minion):
	Class, race, name = "Warlock", "", "Keli'dan the Breaker"
	mana, attack, health = 6, 3, 3
	index = "Outlands~Warlock~Minion~6~3~3~None~Keli'dan the Breaker~Battlecry~Legendary"
	requireTarget, keyWord, description = True, "", "Battlecry: Destroy a minion. If drawn this turn, instead destroy all minions except this one"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.justDrawn = False
		self.triggers["Drawn"] = [self.setJustDrawntoTrue]
		self.triggersinHand = [Trigger_KelidantheBreaker(self)]
		
	def setJustDrawntoTrue(self):
		self.justDrawn = True
		
	def returnTrue(self, choice=0):
		return self.justDrawn == False
		
	def targetExists(self, choice=0):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target != self and target.onBoard
		
	def effectCanTrigger(self):
		self.effectViable = self.justDrawn
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if self.justDrawn:
			PRINT(self, "Keli'dan the Breaker's battlecry destroys all other minions")
			for minion in self.Game.minionsonBoard(1) + self.Game.minionsonBoard(2):
				if minion != self:
					minion.dead = True
		elif target != None: #Not just drawn this turn and target is designated
			PRINT(self, "Keli'dan the Breaker's battlecry destroys minion %s"%target.name)
			self.Game.destroyMinion(target)
		return target
		
class Trigger_KelidantheBreaker(TriggerinHand):
	def __init__(self, entity):
		self.blank_init(entity, ["TurnEnds"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.inHand and self.entity.justDrawn and ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.justDrawn = False
		self.disconnect() #只需要触发一次
		
		
class EnhancedDreadlord(Minion):
	Class, race, name = "Warlock", "Demon", "Enhanced Dreadlord"
	mana, attack, health = 8, 5, 7
	index = "Outlands~Warlock~Minion~8~5~7~Demon~Enhanced Dreadlord~Taunt~Deathrattle"
	requireTarget, keyWord, description = False, "Taunt", "Taunt. Deathrattle: Summon a 5/5 Dreadlord with Lifesteal"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [SummonaDreadlordwithLifesteal(self)]
		
class SummonaDreadlordwithLifesteal(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self, "Deathrattle: Summon a 5/5 Dreadlord with Lifesteal triggers")
		self.entity.Game.summonMinion(DesperateDreadlord(self.entity.Game, self.entity.ID), self.entity.position+1, self.entity.ID)\
		
class DesperateDreadlord(Minion):
	Class, race, name = "Warlock", "Demon", "Desperate Dreadlord"
	mana, attack, health = 5, 5, 5
	index = "Outlands~Warlock~Minion~5~5~5~Demon~Desperate Dreadlord~Lifesteal~Uncollectible"
	requireTarget, keyWord, description = False, "Lifesteal", "Lifesteal"
	
"""Warrior cards"""
class ImprisonedGanarg(Minion_Dormantfor2turns):
	Class, race, name = "Warrior", "Demon", "Imprisoned Gan'arg"
	mana, attack, health = 1, 2, 2
	index = "Outlands~Warrior~Minion~1~2~2~Demon~Imprisoned Gan'arg"
	requireTarget, keyWord, description = False, "", "Dormant for 2 turns. When this awakens, equip a 3/2 Axe"
	
	def awakenEffect(self):
		PRINT(self, "Imprisoned Gan'arg awakens and lets player equip a 3/2 Axe")
		self.Game.equipWeapon(FieryWarAxe(self.Game, self.ID))
		
	
class SwordandBoard(Spell):
	Class, name = "Warrior", "Sword and Board"
	requireTarget, mana = True, 1
	index = "Outlands~Warrior~Spell~1~Sword and Board"
	description = "Deal 2 damage to a minion. Gain 2 Armor"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if target != None:
			damage = (2 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			PRINT(self, "Sword and Board deals %d damage to minion %s"%(damage, target.name))
			self.dealsDamage(target, damage)
		PRINT(self, "Sword and Board lets player gain 2 Armor")
		self.Game.heroes[self.ID].gainsArmor(2)
		return target
		
		
class CorsairCache(Spell):
	Class, name = "Warrior", "Corsair Cache"
	requireTarget, mana = False, 2
	index = "Outlands~Warrior~Spell~2~Corsair Cache"
	description = "Draw a weapon. Give it +1/+1"
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		PRINT(self, "Corsair Cache lets player draw a weapon and gives it +1/+1")
		weaponsinDeck = []
		for card in self.Game.Hand_Deck.decks[self.ID]:
			if card.cardType == "Weapon":
				weaponsinDeck.append(card)
		if weaponsinDeck != []:
			weapon = np.random.choice(weaponsinDeck)
			PRINT(self, "Corsair Cache draws weapon %s from player's deck"%weapon.name)
			card, mana = self.Game.Hand_Deck.drawCard(self.ID, weapon)
			if card != None:
				card.gainStat(1, 1)
		return None
		
		
class Bladestorm(Spell):
	Class, name = "Warrior", "Bladestorm"
	requireTarget, mana = False, 3
	index = "Outlands~Warrior~Spell~3~Bladestorm"
	description = "Deal 1 damage to all minions. Repeat until one dies"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		damage = (1 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		PRINT(self, "Bladestorm deals %d damage to all minions and will repeat until one dies"%damage)
		while True:
			targets = self.Game.minionsonBoard(1) + self.Game.minionsonBoard(2)
			if targets == []:
				break
			else:
				targets_damaged, damagesConnected, totalDamageDone = self.dealsAOE(targets, [damage for minion in targets])
				noMinionsDied = True
				for minion in targets_damaged:
					if minion.health < 1 or minion.dead:
						noMinionsDied = False
						break
				if noMinionsDied == False:
					break
		return None
		
		
class BonechewerRaider(Minion):
	Class, race, name = "Warrior", "", "Bonechewer Raider"
	mana, attack, health = 3, 3, 3
	index = "Outlands~Warrior~Minion~3~3~3~None~Bonechewer Raider~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: If there is a damaged minion, gain +1/+1 and Rush"
	
	def effectCanTrigger(self):
		self.effectViable = False
		for minion in self.Game.minionsonBoard(1) + self.Game.minionsonBoard(2):
			if minion.health < minion.health_upper:
				self.effectViable = True
				break
				
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		damagedMinionExists = False
		for minion in self.Game.minionsonBoard(1) + self.Game.minionsonBoard(2):
			if minion.health < minion.health_upper:
				damagedMinionExists = True
				break
		if damagedMinionExists:
			PRINT(self, "Bonechewer Raider's battlecry gives the minion +1/+1 and Rush")
			self.buffDebuff(1, 1)
			self.getsKeyword("Rush")
		return False
		
		
#不知道与博尔夫碎盾和Blur的结算顺序
class BulwarkofAzzinoth(Weapon):
	Class, name, description = "Warrior", "Bulwark of Azzinoth", "Whenever your hero would take damage, this loses 1 Durability instead"
	mana, attack, durability = 3, 1, 4
	index = "Outlands~Warrior~Weapon~3~1~4~Bulwark of Azzinoth~Legendary"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_BulwarkofAzzinoth(self)]
		
class Trigger_BulwarkofAzzinoth(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["HeroAbouttoTakeDamage"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		#Can only prevent damage if there is still durability left
		return target == self.entity.Game.heroes[self.entity.ID] and self.entity.onBoard and self.entity.durability > 0
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self, "Player is about to take damage and %s prevents it at the cost of losing 1 Durability."%self.entity.name)
		number[0] = 0
		self.entity.loseDurability()
		
		
class WarmaulChallenger(Minion):
	Class, race, name = "Warrior", "", "Warmaul Challenger"
	mana, attack, health = 3, 1, 10
	index = "Outlands~Warrior~Minion~3~1~10~None~Warmaul Challenger~Battlecry"
	requireTarget, keyWord, description = True, "", "Battlecry: Choose an enemy minion. Battle it to the death!"
	
	def targetExists(self, choice=0):
		return self.selectableEnemyMinionExists(choice)
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.ID != self.ID and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if target != None:
			PRINT(self, "Warmaul Challenger's battlecry lets the minion battle enemy minion %s to the death"%target.name)
			#假设双方轮流攻击，该随从先攻击.假设不消耗攻击机会
			whoAttacks = 0
			#def battleRequest(self, subject, target, verifySelectable=True, consumeAttackChance=True, resolveDeath=True, resetRedirectionTriggers=True)
			while self.onBoard and self.health > 0 and self.dead == False and target.onBoard and target.health > 0 and target.dead == False:
				if whoAttacks == 0: #Warmaul Challenger attacks first
					self.Game.battleRequest(self, target, verifySelectable=False, consumeAttackChance=False, resolveDeath=False, resetRedirectionTriggers=False)
				else:
					self.Game.battleRequest(target, self, verifySelectable=False, consumeAttackChance=False, resolveDeath=False, resetRedirectionTriggers=False)
				whoAttacks = 1 - whoAttacks
		return target
		
		
class KargathBladefist(Minion):
	Class, race, name = "Warrior", "", "Kargath Bladefist"
	mana, attack, health = 4, 4, 4
	index = "Outlands~Warrior~Minion~4~4~4~None~Kargath Bladefist~Rush~Deathrattle~Legendary"
	requireTarget, keyWord, description = False, "Rush", "Rush. Deathrattle: Shuffle 'Kargath Prime' into your deck"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [ShuffleKargathPrimeintoYourDeck(self)]
		
class ShuffleKargathPrimeintoYourDeck(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self, "Deathrattle: Shuffle Kargath Prime into your deck triggers")
		self.entity.Game.Hand_Deck.shuffleCardintoDeck(KargathPrime(self.entity.Game, self.entity.ID), self.entity.ID)
		
class KargathPrime(Minion):
	Class, race, name = "Warrior", "", "Kargath Prime"
	mana, attack, health = 8, 10, 10
	index = "Outlands~Warrior~Minion~8~10~10~None~Kargath Prime~Rush~Legendary~Uncollectible"
	requireTarget, keyWord, description = False, "Rush", "Rush. Whenever this attacks and kills a minion, gain 10 Armor"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_KargathPrime(self)]
		
class Trigger_KargathPrime(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionAttackedMinion"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return subject == self.entity and self.entity.onBoard and (target.health < 1 or target.dead == True)
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self, "After %s attacks and kills minion %s, the player gains 10 Armor."%(self.entity.name, target.name))
		self.entity.Game.heroes[self.entity.ID].gainsArmor(10)
		
		
class ScrapGolem(Minion):
	Class, race, name = "Warrior", "Mech", "Scrap Golem"
	mana, attack, health = 5, 4, 5
	index = "Outlands~Warrior~Minion~5~4~5~Mech~Scrap Golem~Taunt~Deathrattle"
	requireTarget, keyWord, description = False, "Taunt", "Taunt. Deathrattle: Gain Armor equal to this minion's Attack"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [GainArmorEqualtoAttack(self)]
		
class GainArmorEqualtoAttack(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self, "Deathrattle: Gain Armor equal to this minion's Attack triggers")
		self.entity.Game.heroes[self.entity.ID].gainsArmor(number)
		
		
class BloodboilBrute(Minion):
	Class, race, name = "Warrior", "", "Bloodboil Brute"
	mana, attack, health = 7, 6, 8
	index = "Outlands~Warrior~Minion~7~6~8~None~Bloodboil Brute~Rush"
	requireTarget, keyWord, description = False, "Rush", "Rush. Costs (1) less for each damaged minion"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersinHand = [Trigger_BloodboilBrute(self)]
		
	def selfManaChange(self):
		if self.inHand:
			numDamagedMinion = 0
			for minion in self.Game.minionsonBoard(1) + self.Game.minionsonBoard(2):
				if minion.health < minion.health_upper:
					numDamagedMinion += 1
			self.mana -= numDamagedMinion
			self.mana = max(0, self.mana)
			
class Trigger_BloodboilBrute(TriggerinHand):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionAppears", "MinionDisappears", "MinionTakesDamage"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.inHand
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.Game.ManaHandler.calcMana_Single(self.entity)
		