from CardTypes import *
from Triggers_Auras import *
from numpy.random import choice as npchoice
from numpy.random import randint as nprandint
from numpy.random import shuffle as npshuffle
from numpy import inf as npinf

from Basic import FieryWarAxe, ExcessMana, WaterElemental

"""Ashes of Outlands"""
#休眠的随从在打出之后2回合本来时会触发你“召唤一张随从”
class Minion_Dormantfor2turns(Minion):
	Class, race, name = "Neutral", "", "Imprisoned Vanilla"
	mana, attack, health = 5, 5, 5
	index = "Vanilla~Neutral~Minion~5~5~5~None~Imprisoned Vanilla"
	requireTarget, keyWord, description = False, "", "Dormant for 2 turns. When this awakens, do something"
	#出现即休眠的随从的played过程非常简单
	def played(self, target=None, choice=0, mana=0, posinHand=-2, comment=""):
		self.statReset(self.attack_Enchant, self.health_max)
		self.appears(firstTime=True) #打出时一定会休眠，同时会把Game.minionPlayed变为None
		return None #没有目标可以返回
		
	def appears(self, firstTime=True):
		self.onBoard, self.inHand, self.inDeck = True, False, False
		self.newonthisSide, self.dead = True, False
		self.mana = type(self).mana #Restore the minion's mana to original value.
		self.decideAttChances_base() #Decide base att chances, given Windfury and Mega Windfury
		#没有光环，目前炉石没有给随从人为添加光环的效果, 不可能在把手牌中获得的扳机带入场上，因为会在变形中丢失
		#The buffAuras/hasAuras will react to this signal.
		if firstTime: #首次出场时会进行休眠，而且休眠状态会保持之前的随从buff
			self.Game.transform(self, ImprisonedDormantForm(self.Game, self.ID, self), firstTime=True)
		else: #只有不是第一次出现在场上时才会执行这些函数
			for aura in self.auras.values(): aura.auraAppears()
			for trig in self.trigsBoard + self.deathrattles: trig.connect()
			self.Game.sendSignal("MinionAppears", self.ID, self, None, 0, comment=firstTime)
			
	def awakenEffect(self):
		pass
		
class ImprisonedDormantForm(Dormant):
	Class, name = "Neutral", "Imprisoned Vanilla"
	description = "Awakens after 2 turns"
	def __init__(self, Game, ID, prisoner=None):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_ImprisonedDormantForm(self)]
		self.prisoner = prisoner
		if prisoner: #When creating a copy, this is left blank temporarily
			self.Class = prisoner.Class
			self.name = "Dormant " + prisoner.name
			self.description = prisoner.description
			self.index = prisoner.index
			
	def assistCreateCopy(self, Copy):
		Copy.prisoner = self.prisoner.createCopy(Copy.Game)
		Copy.name, Copy.Class, Copy.description = self.name, self.Class, self.description
		
class Trig_ImprisonedDormantForm(TrigBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["TurnStarts"])
		self.counter = 2
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and ID == self.entity.ID #会在我方回合开始时进行苏醒
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.counter -= 1
		if self.counter < 1:
			#假设唤醒的Imprisoned Vanilla可以携带buff
			self.entity.Game.transform(self.entity, self.entity.prisoner, firstTime=False)
			if hasattr(self.entity.prisoner, "awakenEffect"):
				self.entity.prisoner.awakenEffect()
				
"""Mana 1 cards"""
class EtherealAugmerchant(Minion):
	Class, race, name = "Neutral", "", "Ethereal Augmerchant"
	mana, attack, health = 1, 2, 1
	index = "Outlands~Neutral~Minion~1~2~1~None~Ethereal Augmerchant~Battlecry"
	requireTarget, keyWord, description = True, "", "Battlecry: Deal 1 damage to a minion and give it Spell Damage +1"
	name_CN = "虚灵改装师"
	def targetExists(self, choice=0):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target != self and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		#需要随从在场并且还是随从形态
		if target and (target.onBoard or target.inHand):
			self.dealsDamage(target, 1)
			target.getsKeyword("Spell Damage")
		return target
		
		
class GuardianAugmerchant(Minion):
	Class, race, name = "Neutral", "", "Guardian Augmerchant"
	mana, attack, health = 1, 2, 1
	index = "Outlands~Neutral~Minion~1~2~1~None~Guardian Augmerchant~Battlecry"
	requireTarget, keyWord, description = True, "", "Battlecry: Deal 1 damage to a minion and give it Divine Shield"
	name_CN = "防护改装师"
	def targetExists(self, choice=0):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target != self and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target and (target.onBoard or target.inHand):
			self.dealsDamage(target, 1)
			target.getsKeyword("Divine Shield")
		return target
		
		
class InfectiousSporeling(Minion):
	Class, race, name = "Neutral", "", "Infectious Sporeling"
	mana, attack, health = 1, 1, 2
	index = "Outlands~Neutral~Minion~1~1~2~None~Infectious Sporeling"
	requireTarget, keyWord, description = False, "", "After this damages a minion, turn it into an Infectious Sporeling"
	name_CN = "传染孢子"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_InfectiousSporeling(self)]
		
class Trig_InfectiousSporeling(TrigBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionTookDamage"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject == self.entity and target.onBoard and target.health > 0 and target.dead == False
		
	def text(self, CHN):
		return "在对随从造成伤害后，将其变为传染孢子" if CHN else "After this damages a minion, turn it into an Infectious Sporeling"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.Game.transform(target, InfectiousSporeling(self.entity.Game, target.ID))
		
		
class RocketAugmerchant(Minion):
	Class, race, name = "Neutral", "", "Rocket Augmerchant"
	mana, attack, health = 1, 2, 1
	index = "Outlands~Neutral~Minion~1~2~1~None~Rocket Augmerchant~Battlecry"
	requireTarget, keyWord, description = True, "", "Battlecry: Deal 1 damage to a minion and give it Rush"
	name_CN = "火箭改装师"
	def targetExists(self, choice=0):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target != self and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target and (target.onBoard or target.inHand):
			self.dealsDamage(target, 1)
			target.getsKeyword("Rush")
		return target
		
		
class SoulboundAshtongue(Minion):
	Class, race, name = "Neutral", "", "Soulbound Ashtongue"
	mana, attack, health = 1, 1, 4
	index = "Outlands~Neutral~Minion~1~1~4~None~Soulbound Ashtongue"
	requireTarget, keyWord, description = False, "", "Whenever this minion takes damage, also deal that amount to your hero"
	name_CN = "魂缚灰舌"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_SoulboundAshtongue(self)]
		
class Trig_SoulboundAshtongue(TrigBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionTakesDmg"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return target == self.entity
		
	def text(self, CHN):
		return "每当该随从受到伤害时，对你的英雄造成先是的伤害" if CHN \
				else "Whenever this minion takes damage, also deal that amount to your hero"
				
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.dealsDamage(self.entity.Game.heroes[self.entity.ID], number)
		
		
"""Mana 2 cards"""
class BonechewerBrawler(Minion):
	Class, race, name = "Neutral", "", "Bonechewer Brawler"
	mana, attack, health = 2, 2, 3
	index = "Outlands~Neutral~Minion~2~2~3~None~Bonechewer Brawler~Taunt"
	requireTarget, keyWord, description = False, "Taunt", "Taunt. Whenever this minion takes damage, gain +2 Attack"
	name_CN = "噬骨殴斗者"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_BonechewerBrawler(self)]
		
class Trig_BonechewerBrawler(TrigBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionTakesDmg"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return target == self.entity and self.entity.onBoard
		
	def text(self, CHN):
		return "每当该随从受到伤害，便获得+2攻击力" if CHN else "Whenever this minion takes damage, gain +2 Attack"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.buffDebuff(2, 0)
		
		
class ImprisonedVilefiend(Minion_Dormantfor2turns):
	Class, race, name = "Neutral", "Demon", "Imprisoned Vilefiend"
	mana, attack, health = 2, 3, 5
	index = "Outlands~Neutral~Minion~2~3~5~Demon~Imprisoned Vilefiend~Rush"
	requireTarget, keyWord, description = False, "Rush", "Dormant for 2 turns. Rush"
	name_CN = "被禁锢的 邪犬"
	
	
class MoargArtificer(Minion):
	Class, race, name = "Neutral", "Demon", "Mo'arg Artificer"
	mana, attack, health = 2, 2, 4
	index = "Outlands~Neutral~Minion~2~2~4~Demon~Mo'arg Artificer"
	requireTarget, keyWord, description = False, "", "All minions take double damage from spells"
	name_CN = "莫尔葛工匠"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_MoargArtificer(self)]
		
class Trig_MoargArtificer(TrigBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["FinalDmgonMinion?"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and target.type == "Minion" and subject.type == "Spell" and number[0] > 0
		
	def text(self, CHN):
		return "所有随从受到的法术伤害翻倍" if CHN else "All minions take double damage from spells"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		number[0] += number[0]
		
		
class RustswornInitiate(Minion):
	Class, race, name = "Neutral", "", "Rustsworn Initiate"
	mana, attack, health = 2, 2, 2
	index = "Outlands~Neutral~Minion~2~2~2~None~Rustsworn Initiate~Deathrattle"
	requireTarget, keyWord, description = False, "", "Deathrattle: Summon a 1/1 Impcaster with Spell Damage +1"
	name_CN = "锈誓新兵"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [SummonanImpcastwithSpellDamagePlus1(self)]
		
class SummonanImpcastwithSpellDamagePlus1(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.Game.summon(Impcaster(self.entity.Game, self.entity.ID), self.entity.pos+1, self.entity.ID)	
		
	def text(self, CHN):
		return "亡语：召唤一个1/1并具有法术伤害+1的小鬼施法者" if CHN else "Deathrattle: Summon a 1/1 Impcaster with Spell Damage +1"
		
class Impcaster(Minion):
	Class, race, name = "Neutral", "Demon", "Impcaster"
	mana, attack, health = 1, 1, 1
	index = "Outlands~Neutral~Minion~1~1~1~Demon~Impcaster~Spell Damage~Uncollectible"
	requireTarget, keyWord, description = False, "Spell Damage", "Spell Damage +1"
	name_CN = "小鬼施法者"
	
"""Mana 3 cards"""
class BlisteringRot(Minion):
	Class, race, name = "Neutral", "", "Blistering Rot"
	mana, attack, health = 3, 1, 2
	index = "Outlands~Neutral~Minion~3~1~2~None~Blistering Rot"
	requireTarget, keyWord, description = False, "", "At the end of your turn, summon a Rot with stats equal to this minion's"
	name_CN = "起泡的 腐泥怪"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_BlisteringRot(self)]
		
class Trig_BlisteringRot(TrigBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["TurnEnds"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and ID == self.entity.ID and self.entity.health > 0
	#假设召唤的Rot只是一个1/1，然后接受buff.而且该随从生命值低于1时不能触发
	#假设攻击力为负数时，召唤物的攻击力为0
	def text(self, CHN):
		return "在你的回合结束时，召唤一个属性值等同于该随从的腐质" if CHN \
				else "At the end of your turn, summon a Rot with stats equal to this minion's"
				
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		minion = LivingRot(self.entity.Game, self.entity.ID)
		if self.entity.Game.summon(minion, self.entity.pos+1, self.entity.ID):
			minion.statReset(max(0, self.entity.attack), self.entity.health)
			
class LivingRot(Minion):
	Class, race, name = "Neutral", "", "Living Rot"
	mana, attack, health = 1, 1, 1
	index = "Outlands~Neutral~Minion~1~1~1~None~Living Rot~Uncollectible"
	requireTarget, keyWord, description = False, "", ""
	name_CN = "生命腐质"
	
	
class FrozenShadoweaver(Minion):
	Class, race, name = "Neutral", "", "Frozen Shadoweaver"
	mana, attack, health = 3, 4, 3
	index = "Outlands~Neutral~Minion~3~4~3~None~Frozen Shadoweaver~Battlecry"
	requireTarget, keyWord, description = True, "", "Battlecry: Freeze an enemy"
	name_CN = "冰霜织影者"
	def targetExists(self, choice=0):
		return self.selectableEnemyExists()
		
	def targetCorrect(self, target, choice=0):
		return (target.type == "Minion" or target.type == "Hero") and target.ID != self.ID and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			target.getsFrozen()
		return target
		
		
class OverconfidentOrc(Minion):
	Class, race, name = "Neutral", "", "Overconfident Orc"
	mana, attack, health = 3, 1, 6
	index = "Outlands~Neutral~Minion~3~1~6~None~Overconfident Orc~Taunt"
	requireTarget, keyWord, description = False, "Taunt", "Taunt. While at full Health, this has +2 Attack"
	name_CN = "狂傲的兽人"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.auras["While at full Health, this has +2 Attack"] = StatAura_OverconfidentOrc(self)
		
class StatAura_OverconfidentOrc(HasAura_toMinion):
	def __init__(self, entity):
		self.entity = entity
		self.signals = ["MinionStatCheck"]
		self.activated = False
		self.auraAffected = []
		
	#光环开启和关闭都取消，因为要依靠随从自己的handleEnrage来触发
	def auraAppears(self):
		minion = self.entity
		for sig in self.signals:
			try: minion.Game.trigsBoard[minion.ID][sig].append(self)
			except: minion.Game.trigsBoard[minion.ID][sig] = [self]
		if minion.onBoard:
			if minion.health == minion.health_max and not self.activated:
				self.activated = True
				self.applies(minion)
				
	def auraDisappears(self):
		self.activated = False
		for sig in self.signals:
			try: self.entity.Game.trigsBoard[self.entity.ID][sig].append(self)
			except: pass
		for minion, receiver in self.auraAffected[:]:
			receiver.effectClear()
		self.auraAffected = []
		
	def applies(self, target):
		Stat_Receiver(target, self, 2, 0).effectStart()
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return target == self.entity and target.onBoard
		
	def trig(self, signal, ID, subject, target, number, comment, choice=0):
		if self.canTrig(signal, ID, subject, target, number, comment):
			self.effect(signal, ID, subject, target, number, comment)
			
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		minion = self.entity
		if minion.health == minion.health_max and not self.activated:
			self.activated = True
			self.applies(minion)
		elif minion.health < minion.health_max and self.activated:
			self.activated = False
			for minion, receiver in self.auraAffected[:]:
				receiver.effectClear()
				
	def selfCopy(self, recipient): #The recipientMinion is the entity that deals the Aura.
		#func that checks if subject is applicable will be the new copy's function
		return type(self)(recipient)
	#激怒的光环仍然可以通过HasAura_toMinion的createCopy复制
	
	
class TerrorguardEscapee(Minion):
	Class, race, name = "Neutral", "Demon", "Terrorguard Escapee"
	mana, attack, health = 3, 3, 7
	index = "Outlands~Neutral~Minion~3~3~7~Demon~Terrorguard Escapee~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Summon three 1/1 Huntresses for your opponent"
	name_CN = "逃脱的 恐惧卫士"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.Game.summon([Huntress(self.Game, 3-self.ID) for i in range(3)], (-1, "totheRightEnd"), self.ID)
		return None
		
class Huntress(Minion):
	Class, race, name = "Neutral", "", "Huntress"
	mana, attack, health = 1, 1, 1
	index = "Outlands~Neutral~Minion~1~1~1~None~Huntress~Uncollectible"
	requireTarget, keyWord, description = False, "", ""
	name_CN = "女猎手"
	
	
class TeronGorefiend(Minion):
	Class, race, name = "Neutral", "", "Teron Gorefiend"
	mana, attack, health = 3, 3, 4
	index = "Outlands~Neutral~Minion~3~3~4~None~Teron Gorefiend~Battlecry~Deathrattle~Legendary"
	requireTarget, keyWord, description = False, "", "Battlecry: Destroy all friendly minions. Deathrattle: Resummon all of them with +1/+1"
	name_CN = "塔隆血魔"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [ResummonDestroyedMinionwithPlus1Plus1(self)]
	#不知道两次触发战吼时亡语是否会记录两份，假设会
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		minionsDestroyed = [minion for minion in self.Game.minionsonBoard(self.ID) if minion != self]
		if minionsDestroyed:
			self.Game.killMinion(self, minionsDestroyed)
			minionsDestroyed = [type(minion) for minion in minionsDestroyed]
			for trig in self.deathrattles:
				if type(trig) == ResummonDestroyedMinionwithPlus1Plus1:
					trig.minionsDestroyed += minionsDestroyed
		return None
		
class ResummonDestroyedMinionwithPlus1Plus1(Deathrattle_Minion):
	def __init__(self, entity):
		self.blank_init(entity)
		self.minionsDestroyed = []
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		if self.minionsDestroyed != []:
			pos = (self.entity.pos, "totheRight") if self.entity in self.entity.Game.minions[self.entity.ID] else (-1, "totheRightEnd")
			minions = [minion(self.entity.Game, self.entity.ID) for minion in self.minionsDestroyed]
			#假设给予+1/+1是在召唤之前
			for minion in minions: minion.buffDebuff(1, 1)
			self.entity.Game.summon(minions, pos, self.entity.ID)
			
	def text(self, CHN):
		return "亡语：再次召唤被战吼消灭的随从并使它们获得+1/+1" if CHN else "Deathrattle: Resummon all destroyed minions with +1/+1"
		
	def selfCopy(self, recipient):
		trig = type(self)(recipient)
		trig.minionsDestroyed = self.minionsDestroyed[:]
		return trig
		
		
"""Mana 4 cards"""
class BurrowingScorpid(Minion):
	Class, race, name = "Neutral", "Beast", "Burrowing Scorpid"
	mana, attack, health = 4, 5, 2
	index = "Outlands~Neutral~Minion~4~5~2~Beast~Burrowing Scorpid~Battlecry"
	requireTarget, keyWord, description = True, "", "Battlecry: Deal 2 damage. If that kills the target, gain Stealth"
	name_CN = "潜地蝎"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			self.dealsDamage(target, 2)
			if target.health < 1 or target.dead == True:
				self.getsKeyword("Stealth")
		return target
		
		
class DisguisedWanderer(Minion):
	Class, race, name = "Neutral", "Demon", "Disguised Wanderer"
	mana, attack, health = 4, 3, 3
	index = "Outlands~Neutral~Minion~4~3~3~Demon~Disguised Wanderer~Deathrattle"
	requireTarget, keyWord, description = False, "", "Deathrattle: Summon a 9/1 Inquisitor"
	name_CN = "变装游荡者"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [SummonanInquisitor(self)]
		
class SummonanInquisitor(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.Game.summon(RustswornInquisitor(self.entity.Game, self.entity.ID), self.entity.pos+1, self.entity.ID)	
		
	def text(self, CHN):
		return "亡语：召唤一个9/1的审判官" if CHN else "Deathrattle: Summon a 9/1 Inquisitor"
		
class RustswornInquisitor(Minion):
	Class, race, name = "Neutral", "Demon", "Rustsworn Inquisitor"
	mana, attack, health = 4, 9, 1
	index = "Outlands~Neutral~Minion~4~9~1~Demon~Rustsworn Inquisitor~Uncollectible"
	requireTarget, keyWord, description = False, "", ""
	name_CN = "锈誓审判官"
	
	
class FelfinNavigator(Minion):
	Class, race, name = "Neutral", "Murloc", "Felfin Navigator"
	mana, attack, health = 4, 4, 4
	index = "Outlands~Neutral~Minion~4~4~4~Murloc~Felfin Navigator~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Give your other Murlocs +1/+1"
	name_CN = "邪鳍导航员"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		for minion in self.Game.minionsonBoard(self.ID):
			if minion != self and "Murloc" in minion.race:
				minion.buffDebuff(1, 1)
		return None
		
		
class Magtheridon(Minion):
	Class, race, name = "Neutral", "Demon", "Magtheridon"
	mana, attack, health = 4, 12, 12
	index = "Outlands~Neutral~Minion~4~12~12~Demon~Magtheridon~Battlecry~Legendary"
	requireTarget, keyWord, description = False, "", "Dormant. Battlecry: Summon three 1/3 enemy Warders. When they die, destroy all minions and awaken"
	name_CN = "玛瑟里顿"
	
	def played(self, target=None, choice=0, mana=0, posinHand=-2, comment=""):
		self.statReset(self.attack_Enchant, self.health_max)
		self.appears(firstTime=True)
		#理论上不会有任何角色死亡,可以跳过死亡结算
		num, status = 1, self.Game.status[self.ID]
		if "~Battlecry" in self.index and ["Battlecry x2"] + status["Shark Battlecry x2"] > 0:
			num = 2
		for i in range(num):
			self.whenEffective(target, "", choice, posinHand)
		self.Game.gathertheDead()
		return None
		
	def appears(self, firstTime=True):
		self.newonthisSide, self.dead = True, False
		self.onBoard, self.inHand, self.inDeck = True, False, False
		self.mana = type(self).mana #Restore the minion's mana to original value.
		self.decideAttChances_base() #Decide base att chances, given Windfury and Mega Windfury
		if firstTime: #首次出场时会进行休眠，而且休眠状态会保持之前的随从buff。休眠体由每个不同的随从自己定义
			self.Game.transform(self, self.dormantForm(self.Game, self.ID, self), firstTime=True)
		else: #只有不是第一次出现在场上时才会执行这些函数
			for trig in self.trigsBoard + self.deathrattles:
				trig.connect() #把(obj, signal)放入Game.trigsBoard中
			self.Game.sendSignal("MinionAppears", self.ID, self, None, 0, comment=firstTime)
			for func in self.triggers["StatChanges"]: func()
			
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.Game.summon([HellfireWarder(self.Game, 3-self.ID) for i in range(3)], (-1, "totheRightEnd"), self.ID)
		return None
		
class Magtheridon_Dormant(Dormant):
	Class, name = "Neutral", "Dormant Magtheridon"
	description = "Destroy 3 Warders to destroy all minions and awaken this"
	def __init__(self, Game, ID, prisoner=None):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_Magtheridon_Dormant(self)]
		self.prisoner = prisoner
		
	def assistCreateCopy(self, Copy):
		Copy.prisoner = self.prisoner.createCopy(Copy.Game)
		Copy.name, Copy.Class, Copy.description = self.name, self.Class, self.description
		
class Trig_Magtheridon_Dormant(TrigBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionDies"]) #假设是死亡时扳机，而还是死亡后扳机
		self.counter = 0
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and type(target) == HellfireWarder and target.ID != self.entity.ID
		
	def text(self, CHN):
		return "对手的三个典狱官全部死亡时，消灭所有随从并唤醒玛瑟里顿。还剩余%d个"%self.counter if CHN \
				else "When all three of your opponent's Warders die, destroy all minions and awaken. Warders left: %d"%self.counter
				
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		game = self.entity.Game
		self.counter += 1
		if self.counter > 2:
			game.killMinion(self.entity, game.minionsonBoard(1) + game.minionsonBoard(2))
			#假设不进行强制死亡
			game.transform(self.entity, self.entity.prisoner, firstTime=False)
			
class HellfireWarder(Minion):
	Class, race, name = "Neutral", "", "Hellfire Warder"
	mana, attack, health = 1, 1, 3
	index = "Outlands~Neutral~Minion~1~1~3~None~Hellfire Warder~Uncollectible"
	requireTarget, keyWord, description = False, "", "(Magtheridon will destroy all minions and awaken after 3 Warders die)"
	name_CN = "地狱火 典狱官"
	
	
class MaievShadowsong(Minion):
	Class, race, name = "Neutral", "", "Maiev Shadowsong"
	mana, attack, health = 4, 4, 3
	index = "Outlands~Neutral~Minion~4~4~3~None~Maiev Shadowsong~Battlecry~Legendary"
	requireTarget, keyWord, description = True, "", "Battlecry: Choose a minion. It goes Dormant for 2 turns"
	name_CN = "玛维影歌"
	def targetExists(self, choice=0):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target != self and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		#需要随从在场并且还是随从形态
		if target and target.onBoard and target.type == "Minion":
			dormantForm = ImprisonedDormantForm(self.Game, target.ID, target) #假设让随从休眠可以保留其初始状态
			self.Game.transform(target, dormantForm, firstTime=True)
		return dormantForm
		
		
class Replicatotron(Minion):
	Class, race, name = "Neutral", "Mech", "Replicat-o-tron"
	mana, attack, health = 4, 3, 3
	index = "Outlands~Neutral~Minion~4~3~3~Mech~Replicat-o-tron"
	requireTarget, keyWord, description = False, "", "At the end of your turn, transform a neighbor into a copy of this"
	name_CN = "复制机器人"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_Replicatotron(self)]
		
class Trig_Replicatotron(TrigBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["TurnEnds"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and ID == self.entity.ID
		
	def text(self, CHN):
		return "在你的回合结时，将一个相邻的随从变形成为该随从的复制" if CHN else "At the end of your turn, transform a neighbor into a copy of this"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		minion = self.entity
		curGame = minion.Game
		if curGame.mode == 0:
			if curGame.guides:
				i = curGame.guides.pop(0)
			else:
				neighbors = self.entity.Game.neighbors2(minion)[0]
				i = npchoice(neighbors).pos if neighbors else -1
				curGame.fixedGuides.append(i)
			if i > -1:
				neighbor = curGame.minions[minion.ID][i]
				curGame.transform(neighbor, minion.selfCopy(minion.ID))
				
				
class RustswornCultist(Minion):
	Class, race, name = "Neutral", "", "Rustsworn Cultist"
	mana, attack, health = 4, 3, 3
	index = "Outlands~Neutral~Minion~4~3~3~None~Rustsworn Cultist~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Give your other minions 'Deathrattle: Summon a 1/1 Demon'"
	name_CN = "锈誓信徒"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		for minion in self.Game.minionsonBoard(self.ID):
			trig = SummonaRustedDevil(minion)
			minion.deathrattles.append(trig)
			trig.connect()
		return None
		
class SummonaRustedDevil(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		#This Deathrattle can't possibly be triggered in hand
		self.entity.Game.summon(RustedDevil(self.entity.Game, self.entity.ID), self.entity.pos+1, self.entity.ID)
		
class RustedDevil(Minion):
	Class, race, name = "Neutral", "Demon", "Rusted Devil"
	mana, attack, health = 1, 1, 1
	index = "Outlands~Neutral~Minion~1~1~1~Demon~Rusted Devil~Uncollectible"
	requireTarget, keyWord, description = False, "", ""
	name_CN = "铁锈恶鬼"
	
	
"""Mana 5 cards"""
class Alar(Minion):
	Class, race, name = "Neutral", "Elemental", "Al'ar"
	mana, attack, health = 5, 7, 3
	index = "Outlands~Neutral~Minion~5~7~3~Elemental~Al'ar~Deathrattle~Legendary"
	requireTarget, keyWord, description = False, "", "Deathrattle: Summon a 0/3 Ashes of Al'ar that resurrects this minion on your next turn"
	name_CN = "奥"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [SummonAshesofAlar(self)]
		
class SummonAshesofAlar(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.Game.summon(AshesofAlar(self.entity.Game, self.entity.ID), self.entity.pos+1, self.entity.ID)
		
	def text(self, CHN):
		return "亡语：召唤一个0/3的可以在你的下个回合复活该随从的“奥的灰烬”" if CHN \
				else "Deathrattle: Summon a 0/3 Ashes of Al'ar that resurrects this minion on your next turn"
				
class AshesofAlar(Minion):
	Class, race, name = "Neutral", "", "Ashes of Al'ar"
	mana, attack, health = 1, 0, 3
	index = "Outlands~Neutral~Minion~1~0~3~None~Ashes of Al'ar~Legendary~Uncollectible"
	requireTarget, keyWord, description = False, "", "At the start of your turn, transform this into Al'ar"
	name_CN = "奥的灰烬”"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_AshesofAlar(self)]
		
class Trig_AshesofAlar(TrigBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["TurnStarts"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and ID == self.entity.ID
		
	def text(self, CHN):
		return "在你的回合开始时，该随从变形成为奥" if CHN else "At the start of your turn, transform this into Al'ar"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.Game.transform(self.entity, Alar(self.entity.Game, self.entity.ID))
		
		
class RuststeedRaider(Minion):
	Class, race, name = "Neutral", "", "Ruststeed Raider"
	mana, attack, health = 5, 1, 8
	index = "Outlands~Neutral~Minion~5~1~8~None~Ruststeed Raider~Taunt~Rush~Battlecry"
	requireTarget, keyWord, description = False, "Taunt,Rush", "Taunt, Rush. Battlecry: Gain +4 Attack this turn"
	name_CN = "锈骑劫匪"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.buffDebuff(4, 0, "EndofTurn")
		return None
		
		
class WasteWarden(Minion):
	Class, race, name = "Neutral", "", "Waste Warden"
	mana, attack, health = 5, 3, 3
	index = "Outlands~Neutral~Minion~5~3~3~None~Waste Warden~Battlecry"
	requireTarget, keyWord, description = True, "", "Battlecry: Deal 3 damage to a minion and all others of the same minion type"
	name_CN = "废土守望者"
	
	def targetExists(self, choice=0):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.race != "" and target.onBoard
		
	#假设指定梦魇融合怪的时候会把场上所有有种族的随从都打一遍
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			if target.race == "":
				self.dealsDamage(target, 3)
			else: #Minion has type
				minionsoftheSameType = [target] #不重复计算目标和对一个随从的伤害
				for race in target.race.split(','): #A bunch of All type minions should be considered 
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
	name_CN = "龙喉巡天者"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [SummonaDragonrider(self)]
		
class SummonaDragonrider(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.Game.summon(Dragonrider(self.entity.Game, self.entity.ID), self.entity.pos+1, self.entity.ID)
		
	def text(self, CHN):
		return "亡语：召唤一个3/4的龙骑士" if CHN else "Deathrattle: Summon a 3/4 Dragonrider"
		
class Dragonrider(Minion):
	Class, race, name = "Neutral", "", "Dragonrider"
	mana, attack, health = 3, 3, 4
	index = "Outlands~Neutral~Minion~3~3~4~None~Dragonrider~Uncollectible"
	requireTarget, keyWord, description = False, "", ""
	name_CN = "龙骑士"
	
	
class KaelthasSunstrider(Minion):
	Class, race, name = "Neutral", "", "Kael'thas Sunstrider"
	mana, attack, health = 7, 4, 7
	index = "Outlands~Neutral~Minion~7~4~7~None~Kael'thas Sunstrider~Legendary"
	requireTarget, keyWord, description = False, "", "Every third spell you cast each turn costs (1)"
	name_CN = "凯尔萨斯 逐日者"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.auras["Every third spell you cast each turn costs (1)"] = ManaAura_Every3rdSpell0(self)
		
#Assume spells countered by Counterspell still count as spells played
class ManaAura_Every3rdSpell0:
	def __init__(self, entity):
		self.entity = entity
		self.auraAffected = []
		self.signals = ["CardEntersHand", "ManaPaid", "TurnEnds"]
		self.counter = 0
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and ID == self.entity.ID
		
	def trig(self, signal, ID, subject, target, number, comment, choice=0):
		if self.canTrig(signal, ID, subject, target, number, comment):
			self.effect(signal, ID, subject, target, number, comment)
			
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		minionID, game = self.entity.ID, self.entity.Game
		if signal[0] == 'T':
			for card, manaMod in self.auraAffected[:]:
				manaMod.getsRemoved()
			self.auraAffected, self.counter = [], 0
		elif signal[0] == 'M': #我方回合中第三张法术打出的时候会产生光环，取消这个光环中所有登记的manaMod
			self.counter = game.Counters.numSpellsPlayedThisTurn[minionID] % 3
			if self.counter == 2:
				for card in game.Hand_Deck.hands[minionID]: self.applies(card)
			elif self.counter == 0:
				for card, manaMod in self.auraAffected[:]:
					manaMod.getsRemoved()
				self.auraAffected = []
		elif self.counter == 2: self.applies(target[0])
		
	def applies(self, target): #This target is NOT holder.
		if target.type == "Spell":
			manaMod = ManaMod(target, 0, 1, self)
			manaMod.applies()
			self.auraAffected.append((target, manaMod))
			
	def auraAppears(self):
		game, ID = self.entity.Game, self.entity.ID
		self.counter = game.Counters.numSpellsPlayedThisTurn[ID] % 3
		if game.turn == ID and self.counter == 2:
			for card in game.Hand_Deck.hands[ID]: self.applies(card)
		for sig in self.signals:
			try: game.trigsBoard[ID][sig].append(self)
			except: game.trigsBoard[ID][sig] = [self]
		game.Manas.calcMana_All()
		
	def auraDisappears(self):
		game, ID = self.entity.Game, self.entity.ID
		for card, manaMod in self.auraAffected[:]:
			manaMod.getsRemoved()
		self.auraAffected, self.counter = [], 0
		for sig in self.signals:
			try: game.trigsBoard[ID][sig].remove(self)
			except: pass
		game.Manas.calcMana_All()
		
	def selfCopy(self, recipient): #The recipient is the entity that deals the Aura.
		return type(self)(recipient)
		
	def createCopy(self, game):
		if self not in game.copiedObjs:
			entityCopy = self.entity.createCopy(game)
			Copy = self.selfCopy(entityCopy)
			game.copiedObjs[self] = Copy
			Copy.counter = self.counter
			for card, manaMod in self.auraAffected:
				cardCopy = card.createCopy(game)
				manaModIndex = card.manaMods.index(manaMod)
				manaModCopy = cardCopy.manaMods[manaModIndex]
				manaModCopy.source = Copy
				Copy.auraAffected.append((cardCopy, manaModCopy))
			return Copy
		else:
			return game.copiedObjs[self]
			
			
class ScavengingShivarra(Minion):
	Class, race, name = "Neutral", "Demon", "Scavenging Shivarra"
	mana, attack, health = 6, 6, 3
	index = "Outlands~Neutral~Minion~6~6~3~Demon~Scavenging Shivarra~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Deal 6 damage randomly split among all other minions"
	name_CN = "食腐破坏魔"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if curGame.mode == 0:
			for num in range(6):
				minion = None
				if curGame.guides:
					i, where = curGame.guides.pop(0)
					if where: minion = curGame.find(i, where)					
				else:
					minions = curGame.minionsAlive(self.ID, self) + curGame.minionsAlive(3-self.ID)
					if minions:
						minion = npchoice(minions)
						curGame.fixedGuides.append((minion.pos, "Minion%d"%minion.ID))
					else:
						curGame.fixedGuides.append((0, ''))
				if minion:
					self.dealsDamage(minion, 1)
				else: break
		return None
		
		
class BonechewerVanguard(Minion):
	Class, race, name = "Neutral", "", "Bonechewer Vanguard"
	mana, attack, health = 7, 4, 10
	index = "Outlands~Neutral~Minion~7~4~10~None~Bonechewer Vanguard~Taunt"
	requireTarget, keyWord, description = False, "Taunt", "Taunt. Whenever this minion takes damage, gain +2 Attack"
	name_CN = "噬骨先锋"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_BonechewerVanguard(self)]
		
class Trig_BonechewerVanguard(TrigBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionTakesDmg"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return target == self.entity and self.entity.onBoard
		
	def text(self, CHN):
		return "每当该随从受到伤害，便获得+2攻击力" if CHN else "Whenever this minion takes damage, gain +2 Attack"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.buffDebuff(2, 0)
		
		
class SupremeAbyssal(Minion):
	Class, race, name = "Neutral", "Demon", "Supreme Abyssal"
	mana, attack, health = 8, 12, 12
	index = "Outlands~Neutral~Minion~8~12~12~Demon~Supreme Abyssal"
	requireTarget, keyWord, description = False, "", "Can't attack heroes"
	name_CN = "深渊至尊"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.marks["Can't Attack Hero"] = 1
		
		
class ScrapyardColossus(Minion):
	Class, race, name = "Neutral", "Elemental", "Scrapyard Colossus"
	mana, attack, health = 10, 7, 7
	index = "Outlands~Neutral~Minion~10~7~7~Elemental~Scrapyard Colossus~Taunt~Deathrattle"
	requireTarget, keyWord, description = False, "Taunt", "Taunt. Deathrattle: Summon a 7/7 Felcracked Colossus with Taunt"
	name_CN = "废料场巨像"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [SummonaFelcrackedColossuswithTaunt(self)]
		
class SummonaFelcrackedColossuswithTaunt(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.Game.summon(FelcrackedColossus(self.entity.Game, self.entity.ID), self.entity.pos+1, self.entity.ID)
		
	def text(self, CHN):
		return "亡语：召唤一个7/7并具有嘲讽的邪爆巨像" if CHN else "Deathrattle: Summon a 7/7 Felcracked Colossus with Taunt"
		
class FelcrackedColossus(Minion):
	Class, race, name = "Neutral", "Elemental", "Felcracked Colossus"
	mana, attack, health = 7, 7, 7
	index = "Outlands~Neutral~Minion~7~7~7~Elemental~Felcracked Colossus~Taunt~Uncollectible"
	requireTarget, keyWord, description = False, "Taunt", "Taunt"
	name_CN = "邪爆巨像"
	
"""Demon Hunter cards"""
class CrimsonSigilRunner(Minion):
	Class, race, name = "Demon Hunter", "", "Crimson Sigil Runner"
	mana, attack, health = 1, 1, 1
	index = "Outlands~Demon Hunter~Minion~1~1~1~None~Crimson Sigil Runner~Outcast"
	requireTarget, keyWord, description = False, "", "Outcast: Draw a card"
	name_CN = "火色魔印 奔行者"
	
	def effCanTrig(self):
		self.effectViable = self.Game.Hand_Deck.outcastcanTrigger(self)
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if posinHand == 0 or posinHand == -1:
			self.Game.Hand_Deck.drawCard(self.ID)
		return None
		
		
class FuriousFelfin(Minion):
	Class, race, name = "Demon Hunter", "Murloc", "Furious Felfin"
	mana, attack, health = 2, 3, 2
	index = "Outlands~Demon Hunter~Minion~2~3~2~Murloc~Furious Felfin~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: If your hero attacked this turn, gain +1 Attack and Rush"
	name_CN = "暴怒的邪鳍"
	
	def effCanTrig(self):
		self.effectViable = self.Game.Counters.heroAttackTimesThisTurn[self.ID] > 0
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if self.Game.Counters.heroAttackTimesThisTurn[self.ID] > 0:
			self.buffDebuff(1, 0)
			self.getsKeyword("Rush")
		return None
		
		
class ImmolationAura(Spell):
	Class, name = "Demon Hunter", "Immolation Aura"
	requireTarget, mana = False, 2
	index = "Outlands~Demon Hunter~Spell~2~Immolation Aura"
	description = "Deal 1 damage to all minions twice"
	name_CN = "献祭光环"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		#不知道法强随从中途死亡是否会影响伤害，假设不会
		damage = (1 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
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
	name_CN = "虚无行者"
	poolIdentifier = "Demons as Demon Hunter"
	@classmethod
	def generatePool(cls, Game):
		classCards = {s : [] for s in Game.ClassesandNeutral}
		for key, value in Game.MinionswithRace["Demon"].items():
			for Class in key.split('~')[1].split(','):
				classCards[Class].append(value)
		return ["Demons as "+Class for Class in Game.Classes], \
				[classCards[Class]+classCards["Neutral"] for Class in Game.Classes]
				
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if self.ID == curGame.turn:
			if curGame.mode == 0:
				if curGame.guides:
					curGame.Hand_Deck.addCardtoHand(curGame.guides.pop(0), self.ID, "type", byDiscover=True)
				else:
					key = "Demons as "+classforDiscover(self)
					if "byOthers" in comment:
						demon = npchoice(self.rngPool(key))
						curGame.fixedGuides.append(demon)
						curGame.Hand_Deck.addCardtoHand(demon, self.ID, "type", byDiscover=True)
					else:
						demons = npchoice(self.rngPool(key), 3, replace=False)
						curGame.options = [demon(curGame, self.ID) for demon in demons]
						curGame.Discover.startDiscover(self)
		return None
		
	def discoverDecided(self, option, info):
		self.Game.fixedGuides.append(type(option))
		self.Game.Hand_Deck.addCardtoHand(option, self.ID, byDiscover=True)
		
		
class SpectralSight(Spell):
	Class, name = "Demon Hunter", "Spectral Sight"
	requireTarget, mana = False, 2
	index = "Outlands~Demon Hunter~Spell~2~Spectral Sight~Outcast"
	description = "Draw a cards. Outscast: Draw another"
	name_CN = "幽灵视觉"
	def effCanTrig(self):
		self.effectViable = self.Game.Hand_Deck.outcastcanTrigger(self)
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.Game.Hand_Deck.drawCard(self.ID)
		if posinHand == 0 or posinHand == -1:
			self.Game.Hand_Deck.drawCard(self.ID)
		return None
		
		
class AshtongueBattlelord(Minion):
	Class, race, name = "Demon Hunter", "", "Ashtongue Battlelord"
	mana, attack, health = 4, 3, 5
	index = "Outlands~Demon Hunter~Minion~4~3~5~None~Ashtongue Battlelord~Taunt~Lifesteal"
	requireTarget, keyWord, description = False, "Taunt,Lifesteal", "Taunt, Lifesteal"
	name_CN = "灰舌将领"
	
	
class FelSummoner(Minion):
	Class, race, name = "Demon Hunter", "", "Fel Summoner"
	mana, attack, health = 6, 8, 3
	index = "Outlands~Demon Hunter~Minion~6~8~3~None~Fel Summoner~Deathrattle"
	requireTarget, keyWord, description = False, "", "Deathrattle: Summon a random Demon from your hand"
	name_CN = "邪能召唤师"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [SummonaRandomDemonfromYourHand(self)]
		
class SummonaRandomDemonfromYourHand(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		curGame = self.entity.Game
		ownHand = curGame.Hand_Deck.hands[self.entity.ID]
		if curGame.mode == 0:
			if curGame.guides:
				i = curGame.guides.pop(0)
			else:
				demons = [i for i, card in enumerate(ownHand) if card.type == "Minion" and "Demon" in card.race]
				i = npchoice(demons) if demons and curGame.space(self.entity.ID) > 0 else -1
				curGame.fixedGuides.append(i)
			if i > -1: curGame.summonfromHand(i, self.entity.ID, self.entity.pos+1, self.entity.ID)
			
	def text(self, CHN):
		return "亡语：随机从你的手牌中召唤一个恶魔" if CHN else "Deathrattle: Summon a random Demon from your hand"
		
		
class KaynSunfury(Minion):
	Class, race, name = "Demon Hunter", "", "Kayn Sunfury"
	mana, attack, health = 4, 3, 4
	index = "Outlands~Demon Hunter~Minion~4~3~4~None~Kayn Sunfury~Charge~Legendary"
	requireTarget, keyWord, description = False, "Charge", "Charge. All friendly attacks ignore Taunt"
	name_CN = "凯恩日怒"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.auras["All friendly attacks ignore Taunt"] = GameRuleAura_KaynSunfury(self)
		
class GameRuleAura_KaynSunfury(GameRuleAura):
	def auraAppears(self):
		self.entity.Game.status[self.entity.ID]["Ignore Taunt"] += 1
		
	def auraDisappears(self):
		self.entity.Game.status[self.entity.ID]["Ignore Taunt"] -= 1
		
		
class Metamorphosis(Spell):
	Class, name = "Demon Hunter", "Metamorphosis"
	requireTarget, mana = False, 5
	index = "Outlands~Demon Hunter~Spell~5~Metamorphosis~Legendary"
	description = "Swap your Hero Power to 'Deal 4 damage'. After 2 uses, swap it back"
	name_CN = "恶魔变形"
	#不知道是否只是对使用两次英雄技能计数，而不一定要是那个特定的英雄技能
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		power = DemonicBlast(self.Game, self.ID)
		power.powerReplaced = self.Game.powers[self.ID]
		power.replaceHeroPower()
		return None
		
class DemonicBlast(HeroPower):
	mana, name, requireTarget = 1, "Demonic Blast", True
	index = "Demon Hunter~Hero Power~1~Demonic Blast"
	description = "Deal 4 damage. (Two uses left!)"
	name_CN = "恶魔冲击"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_DemonicBlast(self)]
		self.powerReplaced = None
		
	def text(self, CHN):
		damage = (4 + self.Game.status[self.ID]["Power Damage"]) * (2 ** self.countDamageDouble())
		return "造成%d点伤害。（还可使用两次！） 替换的原技能是%s"%(damage, self.powerReplaced.name) if CHN \
				else "Deal %d damage. (Two uses left!) Original Hero Power is %s"%(damage, self.powerReplaced.name)
				
	def effect(self, target, choice=0):
		damage = (4 + self.Game.status[self.ID]["Power Damage"]) * (2 ** self.countDamageDouble())
		dmgTaker, damageActual = self.dealsDamage(target, damage)
		if dmgTaker.health < 1 or dmgTaker.dead: return 1
		return 0
		
class Trig_DemonicBlast(TrigBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["HeroUsedAbility"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject == self.entity
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		power = DemonicBlast1(self.Game, self.ID)
		power.powerReplaced = self.entity.powerReplaced
		power.replaceHeroPower()
		
class DemonicBlast1(HeroPower):
	mana, name, requireTarget = 1, "Demonic Blast", True
	index = "Demon Hunter~Hero Power~1~Demonic Blast"
	description = "Deal 4 damage. (Last use!)"
	name_CN = "恶魔冲击"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_DemonicBlast1(self)]
		self.powerReplaced = None
		
	def text(self, CHN):
		damage = (4 + self.Game.status[self.ID]["Power Damage"]) * (2 ** self.countDamageDouble())
		return "造成%d点伤害。（还可使用一次！） 替换的原技能是%s"%(damage, self.powerReplaced.name) if CHN \
				else "Deal %d damage. (Last use!) Original Hero Power is %s"%(damage, self.powerReplaced.name)
				
	def effect(self, target, choice=0):
		damage = (4 + self.Game.status[self.ID]["Power Damage"]) * (2 ** self.countDamageDouble())
		dmgTaker, damageActual = self.dealsDamage(target, damage)
		if dmgTaker.health < 1 or dmgTaker.dead: return 1
		return 0
		
class Trig_DemonicBlast1(TrigBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["HeroUsedAbility"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject == self.entity
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		power = self.entity.powerReplaced
		power.ID = self.entity.ID
		power.replaceHeroPower()
		
		
class ImprisonedAntaen(Minion_Dormantfor2turns):
	Class, race, name = "Demon Hunter", "Demon", "Imprisoned Antaen"
	mana, attack, health = 6, 10, 6
	index = "Outlands~Demon Hunter~Minion~6~10~6~Demon~Imprisoned Antaen"
	requireTarget, keyWord, description = False, "", "Dormant for 2 turns. When this awakens, deal 10 damage randomly split among all enemies"
	name_CN = "被禁锢的 安塔恩"
	
	def awakenEffect(self):
		curGame = self.Game
		if curGame.mode == 0:
			for num in range(10):
				char = None
				if curGame.guides:
					i, where = curGame.guides.pop(0)
					if where: char = curGame.find(i, where)
				else:
					objs = curGame.charsAlive(3-self.ID)
					if objs:
						char = npchoice(objs)
						curGame.fixedGuides.append((char.pos, char.type+str(char.ID)))
					else:
						curGame.fixedGuides.append((0, ''))
				if char:
					self.dealsDamage(char, 1)
				else: break
				
				
class SkullofGuldan(Spell):
	Class, name = "Demon Hunter", "Skull of Gul'dan"
	requireTarget, mana = False, 6
	index = "Outlands~Demon Hunter~Spell~6~Skull of Gul'dan~Outcast"
	description = "Draw 3 cards. Outscast: Reduce their Cost by (3)"
	name_CN = "古尔丹之颅"
	def effCanTrig(self):
		self.effectViable = self.Game.Hand_Deck.outcastcanTrigger(self)
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		outcastCanTrigger = posinHand == 0 or posinHand == -1
		for i in range(3):
			card, mana = self.Game.Hand_Deck.drawCard(self.ID)
			if outcastCanTrigger and card:
				ManaMod(card, changeby=-3, changeto=-1).applies()
		return None
		
		
class WarglaivesofAzzinoth(Weapon):
	Class, name, description = "Demon Hunter", "Warglaives of Azzinoth", "After attacking a minion, your hero may attack again"
	mana, attack, durability = 6, 3, 4
	index = "Outlands~Demon Hunter~Weapon~6~3~4~Warglaives of Azzinoth"
	name_CN = "埃辛诺斯 战刃"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_WarglaivesofAzzinoth(self)]
		
class Trig_WarglaivesofAzzinoth(TrigBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["HeroAttackedMinion"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject == self.entity.Game.heroes[self.entity.ID] and target.type == "Minion" and self.entity.onBoard
		
	def text(self, CHN):
		return "在攻击一个随从后，你的英雄可以再次攻击" if CHN else "After attacking a minion, your hero may attack again"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.Game.heroes[self.entity.ID].attChances_extra +=1
		
		
class PriestessofFury(Minion):
	Class, race, name = "Demon Hunter", "Demon", "Priestess of Fury"
	mana, attack, health = 7, 6, 5
	index = "Outlands~Demon Hunter~Minion~7~6~5~Demon~Priestess of Fury"
	requireTarget, keyWord, description = False, "", "At the end of your turn, deal 6 damage randomly split among all enemies"
	name_CN = "愤怒的 女祭司"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_PriestessofFury(self)]
		
class Trig_PriestessofFury(TrigBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["TurnEnds"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and ID == self.entity.ID
		
	def text(self, CHN):
		return "在你的回合结束时，造成6点伤害，随机分配到所有敌人身上" if CHN else "At the end of your turn, deal 6 damage randomly split among all enemies"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		curGame = self.entity.Game
		if curGame.mode == 0:
			for num in range(6):
				char = None
				if curGame.guides:
					i, where = curGame.guides.pop(0)
					if where: char = curGame.find(i, where)
				else:
					targets = curGame.charsAlive(3-self.entity.ID)
					if targets:
						char = npchoice(targets)
						curGame.fixedGuides.append((char.pos, char.type+str(char.ID)))
					else:
						curGame.fixedGuides.append((0, ''))
				if char:
					self.entity.dealsDamage(char, 1)
				else: break
				
				
class CoilfangWarlord(Minion):
	Class, race, name = "Demon Hunter", "", "Coilfang Warlord"
	mana, attack, health = 8, 9, 5
	index = "Outlands~Demon Hunter~Minion~8~9~5~None~Coilfang Warlord~Rush~Deathrattle"
	requireTarget, keyWord, description = False, "Rush", "Rush. Deathrattle: Summon a 5/9 Warlord with Taunt"
	name_CN = "盘牙督军"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [SummonaWarlordwithTaunt(self)]
		
class SummonaWarlordwithTaunt(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.Game.summon(ConchguardWarlord(self.entity.Game, self.entity.ID), self.entity.pos+1, self.entity.ID)
		
	def text(self, CHN):
		return "亡语：召唤一个5/9并具有嘲讽的督军" if CHN else "Deathrattle: Summon a 5/9 Warlord with Taunt"
		
class ConchguardWarlord(Minion):
	Class, race, name = "Demon Hunter", "", "Conchguard Warlord"
	mana, attack, health = 8, 5, 9
	index = "Outlands~Demon Hunter~Minion~8~5~9~None~Conchguard Warlord~Taunt~Uncollectible"
	requireTarget, keyWord, description = False, "Taunt", "Taunt"
	name_CN = "螺盾督军"
	
	
class PitCommander(Minion):
	Class, race, name = "Demon Hunter", "Demon", "Pit Commander"
	mana, attack, health = 9, 7, 9
	index = "Outlands~Demon Hunter~Minion~9~7~9~Demon~Pit Commander~Taunt"
	requireTarget, keyWord, description = False, "Taunt", "Taunt. At the end of your turn, summon a Demon from your deck"
	name_CN = "深渊指挥官"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_PitCommander(self)]
		
class Trig_PitCommander(TrigBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["TurnEnds"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and ID == self.entity.ID
		
	def text(self, CHN):
		return "在你的回合结束时，从你的牌库中召唤一个恶魔" if CHN else "At the end of your turn, summon a Demon from your deck"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		minion = self.entity
		curGame = minion.Game
		if curGame.mode == 0:
			if curGame.guides:
				i = curGame.guides.pop(0)
			else:
				demons = [i for i, card in enumerate(curGame.Hand_Deck.decks[minion.ID]) if card.type == "Minion" and "Demon" in card.race]
				i = npchoice(demons) if demons and curGame.space(minion.ID) > 0 else -1
				curGame.fixedGuides.append(i)
			if i > -1: curGame.summonfromDeck(i, minion.ID, minion.pos+1, minion.ID)
			
			
"""Druid cards"""
class FungalFortunes(Spell):
	Class, name = "Druid", "Fungal Fortunes"
	requireTarget, mana = False, 3
	index = "Outlands~Druid~Spell~3~Fungal Fortunes"
	description = "Draw 3 cards. Discard any minions drawn"
	name_CN = "真菌宝藏"
	#The minions will be discarded immediately before drawing the next card.
	#The discarding triggers triggers["Discarded"] and send signals.
	#If the hand is full, then no discard at all. The drawn cards vanish.	
	#The "cast when drawn" spells can take effect as usual
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		for i in range(3):
			card, mana = self.Game.Hand_Deck.drawCard(self.ID)
			#If a card has "cast when drawn" effect, it won't stay in hand.
			if card and card.type == "Minion" and card.inHand:
				self.Game.Hand_Deck.discardCard(self.ID, card)
		return None
		
		
class Ironbark(Spell):
	Class, name = "Druid", "Ironbark"
	requireTarget, mana = True, 2
	index = "Outlands~Druid~Spell~2~Ironbark"
	description = "Give a minion +1/+3 and Taunt. Costs (0) if you have at least 7 Mana Crystals"
	name_CN = "铁木树皮"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsHand = [Trig_Ironbark(self)]
		
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
		
	def selfManaChange(self):
		#假设需要的是空水晶，暂时获得的水晶不算
		if self.inHand and self.Game.Manas.manasUpper[self.ID] > 6:
			self.mana = 0
			
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			target.buffDebuff(1, 3)
			target.getsKeyword("Taunt")
		return target
		
class Trig_Ironbark(TrigHand):
	def __init__(self, entity):
		self.blank_init(entity, ["ManaXtlsCheck"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.inHand and ID == self.entity.ID
		
	def text(self, CHN):
		return "每当玩家的法力水晶上限变化，便得重新计算法力值消耗" if CHN else "Whenever player's Mana Crystals change, recalculate the cost"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.Game.Manas.calcMana_Single(self.entity)
		
		
class ArchsporeMsshifn(Minion):
	Class, race, name = "Druid", "", "Archspore Msshi'fn"
	mana, attack, health = 3, 3, 4
	index = "Outlands~Druid~Minion~3~3~4~None~Archspore Msshi'fn~Taunt~Deathrattle~Legendary"
	requireTarget, keyWord, description = False, "Taunt", "Taunt. Deathrattle: Shuffle 'Msshi'fn Prime' into your deck"
	name_CN = "孢子首领 姆希菲"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [ShuffleMsshifnPrimeintoYourDeck(self)]
		
class ShuffleMsshifnPrimeintoYourDeck(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.Game.Hand_Deck.shuffleCardintoDeck(MsshifnPrime(self.entity.Game, self.entity.ID), self.entity.ID)
		
	def text(self, CHN):
		return "亡语：将“终极姆希菲”洗入你的牌库" if CHN else "Deathrattle: Shuffle 'Msshi'fn Prime' into your deck"
		
class MsshifnPrime(Minion):
	Class, race, name = "Druid", "", "Msshi'fn Prime"
	mana, attack, health = 10, 9, 9
	index = "Outlands~Druid~Minion~10~9~9~None~Msshi'fn Prime~Taunt~Choose One~Legendary~Uncollectible"
	requireTarget, keyWord, description = False, "Taunt", "Taunt. Choose One- Summon a 9/9 Fungal Giant with Taunt; or Rush"
	name_CN = "终极姆希菲"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.chooseOne = 1
		# 0: Give other minion +2/+2; 1:Summon two Treants with Taunt.
		self.options = [MsshifnAttac_Option(self), MsshifnProtec_Option(self)]
		
	#如果有全选光环，只有一个9/9，其同时拥有突袭和嘲讽
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if choice == 0:
			self.Game.summon(FungalGuardian(self.Game, self.ID), self.pos+1, self.ID)
		elif choice == 1:
			self.Game.summon(FungalBruiser(self.Game, self.ID), self.pos+1, self.ID)
		elif choice < 0:
			self.Game.summon(FungalGargantuan(self.Game, self.ID), self.pos+1, self.ID)
		return None
		
class FungalGuardian(Minion):
	Class, race, name = "Druid", "", "Fungal Guardian"
	mana, attack, health = 10, 9, 9
	index = "Outlands~Druid~Minion~10~9~9~None~Fungal Guardian~Taunt~Uncollectible"
	requireTarget, keyWord, description = False, "Taunt", "Taunt"
	
class FungalBruiser(Minion):
	Class, race, name = "Druid", "", "Fungal Bruiser"
	mana, attack, health = 10, 9, 9
	index = "Outlands~Druid~Minion~10~9~9~None~Fungal Bruiser~Rush~Uncollectible"
	requireTarget, keyWord, description = False, "Rush", "Rush"
	
class FungalGargantuan(Minion):
	Class, race, name = "Druid", "", "Fungal Gargantuan"
	mana, attack, health = 10, 9, 9
	index = "Outlands~Druid~Minion~10~9~9~None~Fungal Gargantuan~Taunt~Rush~Uncollectible"
	requireTarget, keyWord, description = False, "Taunt,Rush", "Taunt, Rush"
	
class MsshifnAttac_Option(ChooseOneOption):
	name, description = "Msshi'fn At'tac", "Summon a 9/9 with Taunt"
	def available(self):
		return self.entity.Game.space(self.entity.ID) > 0
		
class MsshifnProtec_Option(ChooseOneOption):
	name, description = "Msshi'fn Pro'tec", "Summon a 9/9 with Rush"
	def available(self):
		return self.entity.Game.space(self.entity.ID) > 0
		
		
class Bogbeam(Spell):
	Class, name = "Druid", "Bogbeam"
	requireTarget, mana = True, 3
	index = "Outlands~Druid~Spell~3~Bogbeam"
	description = "Deal 3 damage to a minion. Costs (0) if you have at least 7 Mana Crystals"
	name_CN = "沼泽射线"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsHand = [Trig_Bogbeam(self)]
		
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
		
	def selfManaChange(self):
		#假设需要的是空水晶，暂时获得的水晶不算
		if self.inHand and self.Game.Manas.manasUpper[self.ID] > 6:
			self.mana = 0
			
	def effCanTrig(self):
		self.effectViable = self.Game.Manas.manasUpper[self.ID] > 6
		
	def text(self, CHN):
		damage = (3 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		return "对一个随从造成%d点伤害。如果你拥有至少七个法力水晶，则法力值消耗为(0)点"%damage if CHN \
				else "Deal %d damage to a minion. Costs (0) if you have at least 7 Mana Crystals"%damage
				
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			damage = (3 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			self.dealsDamage(target, damage)
		return target
		
class Trig_Bogbeam(TrigHand):
	def __init__(self, entity):
		self.blank_init(entity, ["ManaXtlsCheck"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.inHand and ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.Game.Manas.calcMana_Single(self.entity)
		
		
class ImprisonedSatyr(Minion_Dormantfor2turns):
	Class, race, name = "Druid", "Demon", "Imprisoned Satyr"
	mana, attack, health = 3, 3, 3
	index = "Outlands~Druid~Minion~3~3~3~Demon~Imprisoned Satyr"
	requireTarget, keyWord, description = False, "", "Dormant for 2 turns. When this awakens, reduce the Cost of a random minion in your hand by (5)"
	name_CN = "被禁锢的 萨特"
	
	def awakenEffect(self):
		curGame = self.Game
		ownHand = curGame.Hand_Deck.hands[self.ID]
		if curGame.mode == 0:
			if curGame.guides:
				i = curGame.guides.pop(0)
			else:
				minions = [i for i, card in enumerate(ownHand) if card.type == "Minion"]
				i = npchoice(minions) if minions else -1
				curGame.fixedGuides.append(i)
			if i > -1:
				ManaMod(ownHand[i], changeby=-5, changeto=-1).applies()
				
				
class Germination(Spell):
	Class, name = "Druid", "Germination"
	requireTarget, mana = True, 4
	index = "Outlands~Druid~Spell~4~Germination"
	description = "Summon a copy of a friendly minion. Give the copy Taunt"
	name_CN = "萌芽分裂"
	def available(self):
		return self.selectableFriendlyMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.ID == self.ID and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			Copy = target.selfCopy(target.ID)
			self.Game.summon(Copy, target.pos+1, self.ID)
			Copy.getsKeyword("Taunt")
		return target
		
		
class Overgrowth(Spell):
	Class, name = "Druid", "Overgrowth"
	requireTarget, mana = False, 4
	index = "Outlands~Druid~Spell~4~Overgrowth"
	description = "Gain two empty Mana Crystals"
	name_CN = "过度生长"
	#不知道满费用和9费时如何结算,假设不会给抽牌的衍生物
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if self.Game.Manas.gainEmptyManaCrystal(2, self.ID) == False:
			self.Game.Hand_Deck.addCardtoHand(ExcessMana(self.Game, self.ID), self.ID)
		return None
		
		
class GlowflySwarm(Spell):
	Class, name = "Druid", "Glowfly Swarm"
	requireTarget, mana = False, 5
	index = "Outlands~Druid~Spell~5~Glowfly Swarm"
	description = "Summon a 2/2 Glowfly for each spell in your hand"
	name_CN = "萤火成群"
	def available(self):
		return self.Game.space(self.ID) > 0
		
	def effCanTrig(self):
		self.effectViable = any(card.type == "Spell" and card != self for card in self.Game.Hand_Deck.hands[self.ID])
			
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		num = sum(card.type == "Spell" for card in self.Game.Hand_Deck.hands[self.ID])
		if num > 0:
			self.Game.summon([Glowfly(self.Game, self.ID) for i in range(num)], (-1, "totheRightEnd"), self.ID)
		return None
		
class Glowfly(Minion):
	Class, race, name = "Druid", "Beast", "Glowfly"
	mana, attack, health = 2, 2, 2
	index = "Outlands~Druid~Minion~2~2~2~Beast~Glowfly~Uncollectible"
	requireTarget, keyWord, description = False, "", ""
	name_CN = "萤火虫"
	
	
class MarshHydra(Minion):
	Class, race, name = "Druid", "Beast", "Marsh Hydra"
	mana, attack, health = 7, 7, 7
	index = "Outlands~Druid~Minion~7~7~7~Beast~Marsh Hydra~Rush"
	requireTarget, keyWord, description = False, "Rush", "Rush. After this attacks, add a random 8-Cost minion to your hand"
	name_CN = "沼泽多头蛇"
	poolIdentifier = "8-Cost Minions"
	@classmethod
	def generatePool(cls, Game):
		return "8-Cost Minions", list(Game.MinionsofCost[8].values())
		
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_MarshHydra(self)]
		
class Trig_MarshHydra(TrigBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionAttackedMinion", "MinionAttackedHero"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject == self.entity
		
	def text(self, CHN):
		return "在该随从攻击后，随机将一张法力值消耗为(8)的随从置入你的手牌" if CHN \
				else "After this attacks, add a random 8-Cost minion to your hand"
				
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		curGame = self.entity.Game
		if curGame.mode == 0:
			if curGame.guides:
				minion = curGame.guides.pop(0)
			else:
				minion = npchoice(self.rngPool("8-Cost Minions"))
				curGame.fixedGuides.append(minion)
			curGame.Hand_Deck.addCardtoHand(minion, self.entity.ID, "type")
			
			
class YsielWindsinger(Minion):
	Class, race, name = "Druid", "", "Ysiel Windsinger"
	mana, attack, health = 9, 5, 5
	index = "Outlands~Druid~Minion~9~5~5~None~Ysiel Windsinger~Legendary"
	requireTarget, keyWord, description = False, "", "Your spells cost (1)"
	name_CN = "伊谢尔风歌"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.auras["Your spells cost (1)"] = ManaAura(self, changeby=0, changeto=1)
		
	def manaAuraApplicable(self, subject): #ID用于判定是否是我方手中的随从
		return subject.type == "Spell" and subject.ID == self.ID
		
"""Hunter cards"""
class Helboar(Minion):
	Class, race, name = "Hunter", "Beast", "Helboar"
	mana, attack, health = 1, 2, 1
	index = "Outlands~Hunter~Minion~1~2~1~Beast~Helboar~Deathrattle"
	requireTarget, keyWord, description = False, "", "Deathrattle: Give a random Beast in your hand +1/+1"
	name_CN = "地狱野猪"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [GiveaRandomBeastinYourHandPlus1Plus1(self)]
		
class GiveaRandomBeastinYourHandPlus1Plus1(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		curGame = self.entity.Game
		ownHand = curGame.Hand_Deck.hands[self.entity.ID]
		if curGame.mode == 0:
			if curGame.guides:
				i = curGame.guides.pop(0)
			else:
				beasts = [i for i, card in enumerate(ownHand) if card.type == "Minion" and "Beast" in card.race]
				i = npchoice(beasts) if beasts else -1
				curGame.fixedGuides.append(i)
			if i > -1:
				ownHand[i].buffDebuff(1, 1)
				
	def text(self, CHN):
		return "亡语：随机使你手牌中的一张野兽获得+1/+1" if CHN else "Deathrattle: Give a random Beast in your hand +1/+1"
		
		
class ImprisonedFelmaw(Minion_Dormantfor2turns):
	Class, race, name = "Hunter", "Demon", "Imprisoned Felmaw"
	mana, attack, health = 2, 5, 4
	index = "Outlands~Hunter~Minion~2~5~4~Demon~Imprisoned Felmaw"
	requireTarget, keyWord, description = False, "", "Dormant for 2 turns. When this awakens, attack a random enemy"
	name_CN = "被禁锢的 魔喉"
	#假设这个攻击不会消耗随从的攻击机会
	def awakenEffect(self):
		curGame = self.Game
		if curGame.mode == 0:
			enemy = None
			if curGame.guides:
				i, where = curGame.guides.pop(0)
				if where: enemy = curGame.find(i, where)
			else:
				targets = curGame.charsAlive(3-self.ID)
				if targets:
					enemy = npchoice(targets)
					curGame.fixedGuides.append((enemy.pos, enemy.type+str(enemy.ID)))
				else:
					curGame.fixedGuides.append((0, ''))
			if enemy:
				curGame.battle(self, enemy, verifySelectable=False, useAttChance=False, resolveDeath=False)
				
				
class PackTactics(Secret):
	Class, name = "Hunter", "Pack Tactics"
	requireTarget, mana = False, 2
	index = "Outlands~Hunter~Spell~2~Pack Tactics~~Secret"
	description = "Secret: When a friendly minion is attacked, summon a 3/3 copy"
	name_CN = "集群战术"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_PackTactics(self)]
		
class Trig_PackTactics(SecretTrigger):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionAttacksMinion", "HeroAttacksMinion"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.ID != self.entity.Game.turn and target[0].ID == self.entity.ID and self.entity.Game.space(self.entity.ID) > 0
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.Game.summon(target[0].selfCopy(self.entity.ID, 3, 3), target[0].pos+1, self.entity.ID)
		
		
class ScavengersIngenuity(Spell):
	Class, name = "Hunter", "Scavenger's Ingenuity"
	requireTarget, mana = False, 2
	index = "Outlands~Hunter~Spell~2~Scavenger's Ingenuity"
	description = "Draw a Beast. Give it +2/+2"
	name_CN = "拾荒者的 智慧"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		ownDeck = curGame.Hand_Deck.decks[self.ID]
		if curGame.mode == 0:
			if curGame.guides:
				i = curGame.guides.pop(0)
			else:
				beasts = [i for i, card in enumerate(ownDeck) if card.type == "Minion" and "Beast" in card.race]
				i = npchoice(beasts) if beasts else -1
				curGame.fixedGuides.append(i)
			if i > -1:
				beast = curGame.Hand_Deck.drawCard(self.ID, i)[0]
				if beast:
					beast.buffDebuff(2, 2)
		return None
		
		
class AugmentedPorcupine(Minion):
	Class, race, name = "Hunter", "Beast", "Augmented Porcupine"
	mana, attack, health = 3, 2, 4
	index = "Outlands~Hunter~Minion~3~2~4~Beast~Augmented Porcupine~Deathrattle"
	requireTarget, keyWord, description = False, "", "Deathrattle: Deals this minion's Attack damage randomly split among all enemies"
	name_CN = "强能箭猪"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [DealDamageEqualtoAttack(self)]
		
class DealDamageEqualtoAttack(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		minion = self.entity
		curGame = minion.Game
		if curGame.mode == 0:
			for num in range(number):
				enemy = None
				if curGame.guides:
					i, where = curGame.guides.pop(0)
					if where: enemy = curGame.find(i, where)
				else:
					enemies = curGame.charsAlive(3-minion.ID)
					if enemies:
						enemy = npchoice(enemies)
						curGame.fixedGuides.append((enemy.pos, enemy.type+str(enemy.ID)))
					else:
						curGame.fixedGuides.append((0, ''))
				if enemy:
					minion.dealsDamage(enemy, 1)
				else: break
				
	def text(self, CHN):
		return "亡语：造成等同于该随从攻击力的伤害，随机分配到所有敌人身上" if CHN \
				else "Deathrattle: Deal this minion's Attack damage randomly split among all enemies"
				
				
class ZixorApexPredator(Minion):
	Class, race, name = "Hunter", "Beast", "Zixor, Apex Predator"
	mana, attack, health = 3, 2, 4
	index = "Outlands~Hunter~Minion~3~2~4~Beast~Zixor, Apex Predator~Rush~Deathrattle~Legendary"
	requireTarget, keyWord, description = False, "Rush", "Rush. Deathrattle: Shuffle 'Zixor Prime' into your deck"
	name_CN = "顶级捕食者 兹克索尔"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [ShuffleZixorPrimeintoYourDeck(self)]
		
class ShuffleZixorPrimeintoYourDeck(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.Game.Hand_Deck.shuffleCardintoDeck(ZixorPrime(self.entity.Game, self.entity.ID), self.entity.ID)
		
	def text(self, CHN):
		return "亡语：将“终极兹克索尔”洗入你的牌库" if CHN else "Deathrattle: Shuffle 'Zixor Prime' into your deck"
		
class ZixorPrime(Minion):
	Class, race, name = "Hunter", "Beast", "Zixor Prime"
	mana, attack, health = 8, 4, 4
	index = "Outlands~Hunter~Minion~8~4~4~Beast~Zixor Prime~Rush~Battlecry~Legendary~Uncollectible"
	requireTarget, keyWord, description = False, "Rush", "Rush. Battlecry: Summon 3 copies of this minion"
	name_CN = "终极 兹克索尔"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		#假设已经死亡时不会召唤复制
		if self.onBoard or self.inHand:
			copies = [self.selfCopy(self.ID) for i in range(3)]
			self.Game.summon(copies, (self.pos, "totheRight"), self.ID)
		return None
		
		
class MokNathalLion(Minion):
	Class, race, name = "Hunter", "Beast", "Mok'Nathal Lion"
	mana, attack, health = 4, 5, 2
	index = "Outlands~Hunter~Minion~4~5~2~Beast~Mok'Nathal Lion~Rush~Battlecry"
	requireTarget, keyWord, description = True, "Rush", "Rush. Battlecry: Choose a friendly minion. Gain a copy of its Deathrattle"
	name_CN = "莫克纳萨 将狮"
	def effCanTrig(self):
		self.effectViable = self.targetExists()
		
	def targetExists(self, choice=0):
		return self.selectableFriendlyMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.ID == self.ID and target != self and target.onBoard and target.deathrattles != []
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target and target.deathrattles != []:
			for trig in target.deathrattles:
				trigCopy = trig.selfCopy(self)
				self.deathrattles.append(trigCopy)
				if self.onBoard:
					trigCopy.connect()
		return target
		
		
class ScrapShot(Spell):
	Class, name = "Hunter", "Scrap Shot"
	requireTarget, mana = True, 4
	index = "Outlands~Hunter~Spell~4~Scrap Shot"
	description = "Deal 3 damage. Give a random Beast in your hand +3/+3"
	name_CN = "废铁射击"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if target:
			damage = (3 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			self.dealsDamage(target, damage)
			ownHand = curGame.Hand_Deck.hands[self.ID]
			if curGame.mode == 0:
				if curGame.guides:
					i = curGame.guides.pop(0)
				else:
					beasts = [i for i, card in enumerate(ownHand) if card.type == "Minion" and "Beast" in card.race]
					i = npchoice(beasts) if beasts else -1
					curGame.fixedGuides.append(i)
				if i > -1:
					ownHand[i].buffDebuff(3, 3)
		return target
		
		
class BeastmasterLeoroxx(Minion):
	Class, race, name = "Hunter", "", "Beastmaster Leoroxx"
	mana, attack, health = 8, 5, 5
	index = "Outlands~Hunter~Minion~8~5~5~None~Beastmaster Leoroxx~Battlecry~Legendary"
	requireTarget, keyWord, description = False, "", "Battlecry: Summon 3 Beasts from your hand"
	name_CN = "兽王 莱欧洛克斯"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		#假设从手牌中最左边向右检索，然后召唤
		if curGame.mode == 0:
			refMinion = self
			for num in range(3):
				if curGame.guides:
					i = curGame.guides.pop(0)
				else:
					beasts = [i for i, card in enumerate(curGame.Hand_Deck.hands[self.ID]) if card.type == "Minion" and "Beast" in card.race]
					i = npchoice(beasts) if beasts and curGame.space(self.ID) > 0 else -1
					curGame.fixedGuides.append(i)
				if i > -1: refMinion = curGame.summonfromHand(i, self.ID, refMinion.pos+1, self.ID)
				else: break
		return None
		
		
class NagrandSlam(Spell):
	Class, name = "Hunter", "Nagrand Slam"
	requireTarget, mana = False, 10
	index = "Outlands~Hunter~Spell~10~Nagrand Slam"
	description = "Summon four 3/5 Clefthoofs that attack random enemies"
	name_CN = "纳格兰 大冲撞"
	def available(self):
		return self.Game.space(self.ID) > 0
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		clefthoofs = [Clefthoof(curGame, self.ID) for i in range(4)]
		curGame.summon(clefthoofs, (-1, "totheRightEnd"), self.ID)
		if curGame.mode == 0:
			#不知道卡德加翻倍召唤出的随从是否会攻击那个随从，假设不会
			for clefthoof in clefthoofs:
				#Clefthoofs must be living to initiate attacks
				if clefthoof.onBoard and clefthoof.health > 0 and not clefthoof.dead:
					enemy = None
					if curGame.guides:
						i, where = curGame.guides.pop(0)
						if where: enemy = curGame.find(i, where)
					else:
						targets = curGame.charsAlive(3-self.ID)
						if targets:
							enemy = npchoice(targets)
							curGame.fixedGuides.append((enemy.pos, enemy.type+str(enemy.ID)))
						else:
							curGame.fixedGuides.append((0, ''))
					if enemy:
						curGame.battle(clefthoof, enemy, verifySelectable=False, useAttChance=True, resolveDeath=False) #攻击会消耗攻击机会
					else: break
		return None
		
class Clefthoof(Minion):
	Class, race, name = "Hunter", "Beast", "Clefthoof"
	mana, attack, health = 4, 3, 5
	index = "Outlands~Hunter~Minion~4~3~5~Beast~Clefthoof~Uncollectible"
	requireTarget, keyWord, description = False, "", ""
	name_CN = "裂蹄牛"
	
"""Mage cards"""
class Evocation(Spell):
	Class, name = "Mage", "Evocation"
	requireTarget, mana = False, 2
	index = "Outlands~Mage~Spell~2~Evocation~Legendary"
	description = "Fill your hand with random Mage spells. At the end of your turn, discard them"
	name_CN = "唤醒"
	poolIdentifier = "Mage Spells"
	@classmethod
	def generatePool(cls, Game):
		return "Mage Spells", [value for key, value in Game.ClassCards["Mage"].items() if "~Spell~" in key]
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		while curGame.Hand_Deck.handNotFull(self.ID):
			if curGame.mode == 0:
				if curGame.guides:
					spell = curGame.guides.pop(0)
				else:
					spell = npchoice(self.rngPool("Mage Spells"))
					curGame.fixedGuides.append(spell)
				spell = spell(curGame, self.ID)
				trig = Trig_Evocation(spell)
				spell.trigsHand.append(trig)
				trig.connect()
				curGame.Hand_Deck.addCardtoHand(spell, self.ID)
		return None
		
class Trig_Evocation(TrigHand):
	def __init__(self, entity):
		self.blank_init(entity, ["TurnEnds"])
		self.inherent = False
		self.makesCardEvanescent = True
		
	#They will be discarded at the end of any turn
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.inHand
		
	def text(self, CHN):
		return "在你的回合结束时，弃掉这张牌" if CHN else "At the end of your turn, discard this card"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.Game.Hand_Deck.discardCard(self.entity.ID, self.entity)
		
		
class FontofPower(Spell):
	Class, name = "Mage", "Font of Power"
	requireTarget, mana = False, 1
	index = "Outlands~Mage~Spell~1~Font of Power"
	description = "Discover a Mage minion. If your deck has no minions, keep all 3"
	name_CN = "能量之泉"
	poolIdentifier = "Mage Minions"
	@classmethod
	def generatePool(cls, Game):
		return "Mage Minions", [value for key, value in Game.ClassCards["Mage"].items() if "~Minion~" in key]
		
	def effCanTrig(self):
		self.effectViable = self.Game.Hand_Deck.noMinionsinDeck(self.ID)
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if curGame.Hand_Deck.noMinionsinDeck(self.ID):
			if curGame.mode == 0:
				if curGame.guides:
					minions = list(curGame.guides.pop(0))
				else:
					minions = npchoice(self.rngPool("Mage Minions"), 3, replace=False)
					curGame.fixedGuides.append(tuple(minions))
				curGame.Hand_Deck.addCardtoHand(minions, self.ID, "type")
		else:
			if curGame.mode == 0:
				if curGame.guides:
					minion = curGame.guides.pop(0)
					curGame.fixedGuides.append(minion)
					curGame.Hand_Deck.addCardtoHand(minion, self.ID, "type", byDiscover=True)
				else:
					if self.ID != curGame.turn or "byOthers" in comment:
						minion = npchoice(self.rngPool("Mage Minions"))
						curGame.fixedGuides.append(minion)
						curGame.Hand_Deck.addCardtoHand(minion, self.ID, "type", byDiscover=True)
					else:
						minions = npchoice(self.rngPool("Mage Minions"), 3, replace=False)
						curGame.options = [minion(curGame, self.ID) for minion in minions]
						curGame.Discover.startDiscover(self)
		return None
		
	def discoverDecided(self, option, info):
		self.Game.fixedGuides.append(type(option))
		self.Game.Hand_Deck.addCardtoHand(option, self.ID, byDiscover=True)
		
		
class ApexisSmuggler(Minion):
	Class, race, name = "Mage", "", "Apexis Smuggler"
	mana, attack, health = 2, 2, 3
	index = "Outlands~Mage~Minion~2~2~3~None~Apexis Smuggler"
	requireTarget, keyWord, description = False, "", "After you play a Secret, Discover a spell"
	name_CN = "埃匹希斯 走私犯"
	poolIdentifier = "Mage Spells"
	@classmethod
	def generatePool(cls, Game):
		return [Class+" Spells" for Class in Game.Classes], \
				[[value for key, value in Game.ClassCards[Class].items() if "~Spell~" in key] for Class in Game.Classes]
				
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_ApexisSmuggler(self)]
		
	def discoverDecided(self, option, info):
		self.Game.fixedGuides.append(type(option))
		self.Game.Hand_Deck.addCardtoHand(option, self.ID, byDiscover=True)
		
class Trig_ApexisSmuggler(TrigBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["SpellBeenPlayed"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject.ID == self.entity.ID and subject.description.startswith("Secret:")
		
	def text(self, CHN):
		return "在你使用一张奥秘牌后，发现一张法术牌" if CHN else "After you play a Secret, Discover a spell"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		minion, curGame = self.entity, self.entity.Game
		if curGame.mode == 0:
			if curGame.guides:
				curGame.Hand_Deck.addCardtoHand(curGame.guides.pop(0), minion.ID, "type", byDiscover=True)
			else:
				key = classforDiscover(minion)+" Spells"
				spells = npchoice(self.rngPool(key), 3, replace=False)
				curGame.options = [spell(curGame, minion.ID) for spell in spells]
				curGame.Discover.startDiscover(minion)
				
				
class AstromancerSolarian(Minion):
	Class, race, name = "Mage", "", "Astromancer Solarian"
	mana, attack, health = 2, 3, 2
	index = "Outlands~Mage~Minion~2~3~2~None~Astromancer Solarian~Spell Damage~Deathrattle~Legendary"
	requireTarget, keyWord, description = False, "Spell Damage", "Spell Damage +1. Deathrattle: Shuffle 'Solarian Prime' into your deck"
	name_CN = "星术师 索兰莉安"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [ShuffleSolarianPrimeintoYourDeck(self)]
		
class ShuffleSolarianPrimeintoYourDeck(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.Game.Hand_Deck.shuffleCardintoDeck(SolarianPrime(self.entity.Game, self.entity.ID), self.entity.ID)
		
	def text(self, CHN):
		return "亡语：将“终极索兰莉安”洗入你的牌库" if CHN else "Deathrattle: Shuffle 'Solarian Prime' into your deck"
		
class SolarianPrime(Minion):
	Class, race, name = "Mage", "Demon", "Solarian Prime"
	mana, attack, health = 9, 7, 7
	index = "Outlands~Mage~Minion~9~7~7~Demon~Solarian Prime~Spell Damage~Battlecry~Legendary~Uncollectible"
	requireTarget, keyWord, description = False, "Spell Damage", "Spell Damage +1. Battlecry: Cast 5 random Mage spells (target enemies if possible)"
	name_CN = "终极索兰莉安"
	poolIdentifier = "Mage Spells"
	@classmethod
	def generatePool(cls, Game):
		return "Mage Spells", [value for key, value in Game.ClassCards["Mage"].items() if "~Spell~" in key]
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if curGame.mode == 0:
			for i in range(5):
				if curGame.guides:
					mageSpell = curGame.guides.pop(0)
				else:
					mageSpell = npchoice(self.rngPool("Mage Spells"))
					curGame.fixedGuides.append(mageSpell)
				mageSpell(curGame, self.ID).cast(None, "enemy1st")
				curGame.gathertheDead(decideWinner=True)
		return None
		
		
class IncantersFlow(Spell):
	Class, name = "Mage", "Incanter's Flow"
	requireTarget, mana = False, 2
	index = "Outlands~Mage~Spell~2~Incanter's Flow"
	description = "Reduce the Cost of spells in your deck by (1)"
	name_CN = "咒术洪流"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		for card in self.Game.Hand_Deck.decks[self.ID][:]:
			if card.type == "Spell":
				ManaMod(card, changeby=-1, changeto=-1).applies()
		return None
		
		
class Starscryer(Minion):
	Class, race, name = "Mage", "", "Starscryer"
	mana, attack, health = 2, 3, 1
	index = "Outlands~Mage~Minion~2~3~1~None~Starscryer~Deathrattle"
	requireTarget, keyWord, description = False, "", "Deathrattle: Draw a spell"
	name_CN = "星占师"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [DrawaSpell(self)]
		
class DrawaSpell(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		curGame = self.entity.Game
		if curGame.mode == 0:
			if curGame.guides:
				i = curGame.guides.pop(0)
			else:
				spells = [i for i, card in enumerate(curGame.Hand_Deck.decks[self.entity.ID]) if card.type == "Spell"]
				i = npchoice(spells) if spells else -1
				curGame.fixedGuides.append(i)
			if i > -1: curGame.Hand_Deck.drawCard(self.entity.ID, i)
			
	def text(self, CHN):
		return "亡语：抽一张法术牌" if CHN else "Deathrattle: Draw a spell"
		
		
class ImprisonedObserver(Minion_Dormantfor2turns):
	Class, race, name = "Mage", "Demon", "Imprisoned Observer"
	mana, attack, health = 3, 4, 5
	index = "Outlands~Mage~Minion~3~4~5~Demon~Imprisoned Observer"
	requireTarget, keyWord, description = False, "", "Dormant for 2 turns. When this awakens, deal 2 damage to all enemy minions"
	name_CN = "被禁锢的 眼魔"
	
	def awakenEffect(self):
		targets = self.Game.minionsonBoard(3-self.ID)
		self.dealsAOE(targets, [2]*len(targets))
		
		
class NetherwindPortal(Secret):
	Class, name = "Mage", "Netherwind Portal"
	requireTarget, mana = False, 3
	index = "Outlands~Mage~Spell~3~Netherwind Portal~~Secret"
	description = "Secret: After your opponent casts a spell, summon a random 4-Cost minion"
	name_CN = "虚空之风 传送门"
	poolIdentifier = "4-Cost Minions to Summon"
	@classmethod
	def generatePool(cls, Game):
		return "4-Cost Minions to Summon", list(Game.MinionsofCost[4].values())
		
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_NetherwindPortal(self)]
		
class Trig_NetherwindPortal(SecretTrigger):
	def __init__(self, entity):
		self.blank_init(entity, ["SpellBeenPlayed"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.ID != self.entity.Game.turn and subject.ID != self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		curGame = self.entity.Game
		if curGame.mode == 0:
			if curGame.guides:
				minion = curGame.guides.pop(0)
			else:
				minion = npchoice(self.rngPool("4-Cost Minions to Summon"))
				curGame.fixedGuides.append(minion)
			curGame.summon(minion(curGame, self.entity.ID), -1, self.entity.ID)
		
		
class ApexisBlast(Spell):
	Class, name = "Mage", "Apexis Blast"
	requireTarget, mana = True, 5
	index = "Outlands~Mage~Spell~5~Apexis Blast"
	description = "Deal 5 damage. If your deck has no minions, summon a random 5-Cost minion"
	name_CN = "埃匹希斯 冲击"
	poolIdentifier = "5-Cost Minions to Summon"
	@classmethod
	def generatePool(cls, Game):
		return "5-Cost Minions to Summon", list(Game.MinionsofCost[5].values())
		
	def effCanTrig(self):
		self.effectViable = self.Game.Hand_Deck.noMinionsinDeck(self.ID)
		
	def text(self, CHN):
		damage = (5 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		return "造成%d点伤害。如果你的牌库中没有随从牌，随机召唤一个法力消耗为(5)的随从"%damage if CHN \
				else "Deal %d damage. If your deck has no minions, summon a random 5-Cost minion"%damage
				
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if target:
			damage = (5 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			self.dealsDamage(target, damage)
			if curGame.mode == 0:
				if curGame.guides:
					minion = curGame.guides.pop(0)
				else:
					minion = npchoice(self.rngPool("5-Cost Minions to Summon")) if curGame.Hand_Deck.noMinionsinDeck(self.ID) else None
					curGame.fixedGuides.append(minion)
				if minion:
					curGame.summon(minion(curGame, self.ID), -1, self.ID)
		return target
		
		
class DeepFreeze(Spell):
	Class, name = "Mage", "Deep Freeze"
	requireTarget, mana = True, 8
	index = "Outlands~Mage~Spell~8~Deep Freeze"
	description = "Freeze an enemy. Summon two 3/6 Water Elementals"
	name_CN = "深度冻结"
	def available(self):
		return self.selectableEnemyExists()
		
	def targetCorrect(self, target, choice=0):
		return (target.type == "Minion" or target.type == "Hero") and target.ID != self.ID and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			target.getsFrozen()
		self.Game.summon([WaterElemental(self.Game, self.ID) for i in range(2)], (-1, "totheRightEnd"), self.ID)
		return target
		
"""Paladin cards"""
class ImprisonedSungill(Minion_Dormantfor2turns):
	Class, race, name = "Paladin", "Murloc", "Imprisoned Sungill"
	mana, attack, health = 1, 2, 1
	index = "Outlands~Paladin~Minion~1~2~1~Murloc~Imprisoned Sungill"
	requireTarget, keyWord, description = False, "", "Dormant for 2 turns. When this awakens, Summon two 1/1 Murlocs"
	name_CN = "被禁锢的 阳鳃鱼人"
	
	def awakenEffect(self):
		self.Game.summon([SungillStreamrunner(self.Game, self.ID) for i in range(2)], (self.pos, "leftandRight"), self.ID)
		
class SungillStreamrunner(Minion):
	Class, race, name = "Paladin", "Murloc", "Sungill Streamrunner"
	mana, attack, health = 1, 1, 1
	index = "Outlands~Paladin~Minion~1~1~1~Murloc~Sungill Streamrunner~Uncollectible"
	requireTarget, keyWord, description = False, "", ""
	name_CN = "阳鳃士兵"
	
	
class GameManaAura_Libram:
	def __init__(self, Game, ID, changeby=0, changeto=-1):
		self.Game, self.ID = Game, ID
		self.changeby, self.changeto = changeby, changeto
		self.auraAffected = [] #A list of (minion, receiver)
		
	#只要是有满足条件的卡牌进入手牌，就会触发这个光环。target是承载这个牌的列表。
	#applicable不需要询问一张牌是否在手牌中。光环只会处理在手牌中的卡牌
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return target[0].ID == self.ID and target[0].name.startswith("Libram of")
		
	def trig(self, signal, ID, subject, target, number, comment, choice=0):
		if self.canTrig(signal, ID, subject, target, number, comment):
			self.applies(target[0])
			
	def applies(self, target): #This target is NOT holder.
		if target.ID == self.ID and target.name.startswith("Libram of"):
			manaMod = ManaMod(target, self.changeby, self.changeto, self)
			manaMod.applies()
			self.auraAffected.append((target, manaMod))
			
	def text(self, CHN):
		return "在本局对战中，你的圣契的法力值消耗减少(%d)点"%(-self.changeby) if CHN \
				else "Reduce the cost of your Librams by (%d) this game"%(-self.changeby)
				
	def auraAppears(self):
		game = self.Game
		game.trigAuras[self.ID].append(self)
		for card in game.Hand_Deck.hands[1]: self.applies(card)
		for card in game.Hand_Deck.hands[2]: self.applies(card)
		#Only need to handle minions that appear. Them leaving/silenced will be handled by the Stat_Receiver object.
		#We want this Trig_MinionAppears can handle everything including registration and buff and removing.
		try: game.trigsBoard[self.ID]["CardEntersHand"].append(self)
		except: game.trigsBoard[self.ID]["CardEntersHand"] = [self]
		game.Manas.calcMana_All()
	#Aura is permanent and doesn't have auraDisappears()
	#可以在复制场上扳机列表的时候被调用
	#可以调用这个函数的时候，一定是因为要复制一个随从的费用光环，那个随从的复制已经创建完毕，可以在复制字典中查到
	def createCopy(self, game):
		if self not in game.copiedObjs:
			Copy = type(self)(game, self.ID, self.changeby, self.changeto)
			game.copiedObjs[self] = Copy
			#ManaMod.selfCopy(self, recipientCard):
			#	return ManaMod(recipientCard, self.changeby, self.changeto, self.source, self.lowerbound)
			for card, manaMod in self.auraAffected: #从自己的auraAffected里面复制内容出去
				cardCopy = card.createCopy(game)
				#重点是复制一个随从是，它自己会携带一个费用改变，这个费用改变怎么追踪到
					#用序号看行不行
				manaModIndex = card.manaMods.index(manaMod)
				manaModCopy = cardCopy.manaMods[manaModIndex]
				manaModCopy.source = Copy #在处理函数之前，所有的费用状态都已经被一次性复制完毕，它们的来源被迫留为None,需要在这里补上
				Copy.auraAffected.append((cardCopy, manaModCopy))
			return Copy
		else:
			return game.copiedObjs[self]
			
			
class AldorAttendant(Minion):
	Class, race, name = "Paladin", "", "Aldor Attendant"
	mana, attack, health = 1, 1, 3
	index = "Outlands~Paladin~Minion~1~1~3~None~Aldor Attendant~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Reduce the Cost of your Librams by (1) this game"
	name_CN = "奥尔多 侍从"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		GameManaAura_Libram(self.Game, self.ID, -1, -1).auraAppears()
		return None
		
		
class HandofAdal(Spell):
	Class, name = "Paladin",  "Hand of A'dal"
	requireTarget, mana = True, 2
	index = "Outlands~Paladin~Spell~2~Hand of A'dal"
	description = "Give a minion +2/+2. Draw a card"
	name_CN = "阿达尔之手"
	def targetExists(self, choice=0):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			target.buffDebuff(2, 2)
		self.Game.Hand_Deck.drawCard(self.ID)
		return target
		
		
class MurgurMurgurgle(Minion):
	Class, race, name = "Paladin", "Murloc", "Murgur Murgurgle"
	mana, attack, health = 2, 2, 1
	index = "Outlands~Paladin~Minion~2~2~1~Murloc~Murgur Murgurgle~Divine Shield~Deathrattle~Legendary"
	requireTarget, keyWord, description = False, "Divine Shield", "Divine Shield. Deathrattle: Shuffle 'Murgurgle Prime' into your deck"
	name_CN = "莫戈尔 莫戈尔格"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [ShuffleMurgurglePrimeintoYourDeck(self)]
		
class ShuffleMurgurglePrimeintoYourDeck(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.Game.Hand_Deck.shuffleCardintoDeck(MurgurglePrime(self.entity.Game, self.entity.ID), self.entity.ID)
		
	def text(self, CHN):
		return "亡语：将“终极莫戈尔格”洗入你的牌库" if CHN else "Deathrattle: Shuffle 'Murgurgle Prime' into your deck"
		
class MurgurglePrime(Minion):
	Class, race, name = "Paladin", "Murloc", "Murgurgle Prime"
	mana, attack, health = 8, 6, 3
	index = "Outlands~Paladin~Minion~8~6~3~Murloc~Murgurgle Prime~Divine Shield~Battlecry~Legendary~Uncollectible"
	requireTarget, keyWord, description = False, "Divine Shield", "Divine Shield. Battlecry: Summon 4 random Murlocs. Give them Divine Shield"
	name_CN = "终极莫戈尔格"
	poolIdentifier = "Murlocs to Summon"
	@classmethod
	def generatePool(cls, Game):
		return "Murlocs to Summon", list(Game.MinionswithRace["Murloc"].values())
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if curGame.mode == 0:
			if curGame.guides:
				murlocs = list(curGame.guides.pop(0))
			else:
				murlocs = tuple(npchoice(self.rngPool("Murlocs to Summon"), 4, replace=True))
				curGame.fixedGuides.append(murlocs)
			murlocs = [murloc(curGame, self.ID) for murloc in murlocs]
			pos = (self.pos, "leftandRight") if self.onBoard else (-1, "totheRightEnd")
			curGame.summon(murlocs, pos, self.ID)
			for murloc in murlocs:
				if murloc.onBoard: murloc.getsKeyword("Divine Shield")
		return None
		
		
class LibramofWisdom(Spell):
	Class, name = "Paladin",  "Libram of Wisdom"
	requireTarget, mana = True, 2
	index = "Outlands~Paladin~Spell~2~Libram of Wisdom"
	description = "Give a minion +1/+1 and 'Deathrattle: Add a 'Libram of Wisdom' spell to your hand'"
	name_CN = "智慧圣契"
	def targetExists(self, choice=0):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target and (target.onBoard or target.inHand):
			target.buffDebuff(1, 1)
			trig = AddaLibramofWisdomtoYourHand(target)
			target.deathrattles.append(trig)
			if target.onBoard: trig.connect()
		return target
		
class AddaLibramofWisdomtoYourHand(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.Game.Hand_Deck.addCardtoHand(LibramofWisdom, self.entity.ID, "type")
		
		
class UnderlightAnglingRod(Weapon):
	Class, name, description = "Paladin", "Underlight Angling Rod", "After your hero attacks, add a random Murloc to your hand"
	mana, attack, durability = 3, 3, 2
	index = "Outlands~Paladin~Weapon~3~3~2~Underlight Angling Rod"
	name_CN = "幽光鱼竿"
	poolIdentifier = "Murlocs"
	@classmethod
	def generatePool(cls, Game):
		return "Murlocs", list(Game.MinionswithRace["Murloc"].values())
		
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_UnderlightAnglingRod(self)]
		
class Trig_UnderlightAnglingRod(TrigBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["HeroAttackedMinion", "HeroAttackedHero"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject == self.entity.Game.heroes[self.entity.ID] and self.entity.onBoard
		
	def text(self, CHN):
		return "在你的英雄攻击后，随机将一张鱼人牌置入你的手牌" if CHN \
				else "After your hero attacks, add a random Murloc to your hand"
				
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		curGame = self.entity.Game
		if curGame.mode == 0:
			if curGame.guides:
				murloc = curGame.guides.pop(0)
			else:
				murloc = npchoice(self.rngPool("Murlocs"))
				curGame.fixedGuides.append(murloc)
			curGame.Hand_Deck.addCardtoHand(murloc, self.entity.ID, "type")
			
			
class AldorTruthseeker(Minion):
	Class, race, name = "Paladin", "", "Aldor Truthseeker"
	mana, attack, health = 5, 4, 6
	index = "Outlands~Paladin~Minion~5~4~6~None~Aldor Truthseeker~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Reduce the Cost of your Librams by (2) this game"
	name_CN = "奥尔多 真理追寻者"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		GameManaAura_Libram(self.Game, self.ID, -2, -1).auraAppears().auraAppears()
		return None
		
		
class LibramofJustice(Spell):
	Class, name = "Paladin",  "Libram of Justice"
	requireTarget, mana = False, 5
	index = "Outlands~Paladin~Spell~5~Libram of Justice"
	description = "Equip a 1/4 weapon. Change the Health of all enemy minions to 1"
	name_CN = "正义圣契"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.Game.equipWeapon(OverdueJustice(self.Game, self.ID))
		for minion in self.Game.minionsonBoard(3-self.ID):
			minion.statReset(False, 1)
		return None
		
class OverdueJustice(Weapon):
	Class, name, description = "Paladin", "Overdue Justice", ""
	mana, attack, durability = 1, 1, 4
	index = "Outlands~Paladin~Weapon~1~1~4~Overdue Justice~Uncollectible"
	name_CN = "迟到的正义"
	
class LadyLiadrin(Minion):
	Class, race, name = "Paladin", "", "Lady Liadrin"
	mana, attack, health = 7, 4, 6
	index = "Outlands~Paladin~Minion~7~4~6~None~Lady Liadrin~Battlecry~Legendary"
	requireTarget, keyWord, description = False, "", "Battlecry: Add a copy of each spell you cast on friendly characters this game to your hand"
	name_CN = "女伯爵 莉亚德琳"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if curGame.mode == 0:
			if curGame.guides:
				spells = curGame.guides.pop(0)
			else:
				spells = curGame.Counters.spellsonFriendliesThisGame[self.ID]
				spells = npchoice(spells, min(curGame.Hand_Deck.spaceinHand(self.ID), len(spells)), replace=False)
				spells = tuple([curGame.cardPool[index] for index in spells])
				curGame.fixedGuides.append(spells) #Can be empty, and the empty tuple will simply add nothing to hand
			curGame.Hand_Deck.addCardtoHand(spells, self.ID, "type")
		return None
		
		
class LibramofHope(Spell):
	Class, name = "Paladin", "Libram of Hope"
	requireTarget, mana = True, 9
	index = "Outlands~Paladin~Spell~9~Libram of Hope"
	description = "Restore 8 Health. Summon an 8/8 with Guardian with Taunt and Divine Shield"
	name_CN = "希望圣契"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			heal = 8 * (2 ** self.countHealDouble())
			self.restoresHealth(target, heal)
			self.Game.summon(AncientGuardian(self.Game, self.ID), -1, self.ID)
		return target
		
class AncientGuardian(Minion):
	Class, race, name = "Paladin", "", "Ancient Guardian"
	mana, attack, health = 8, 8, 8
	index = "Outlands~Paladin~Minion~8~8~8~None~Ancient Guardian~Taunt~Divine Shield~Uncollectible"
	requireTarget, keyWord, description = False, "Taunt,Divine Shield", "Taunt, Divine Shield"
	name_CN = "远古守卫"
	
"""Priest cards"""
class ImprisonedHomunculus(Minion_Dormantfor2turns):
	Class, race, name = "Priest", "Demon", "Imprisoned Homunculus"
	mana, attack, health = 1, 2, 5
	index = "Outlands~Priest~Minion~1~2~5~Demon~Imprisoned Homunculus~Taunt"
	requireTarget, keyWord, description = False, "Taunt", "Dormant for 2 turns. Taunt"
	name_CN = "被禁锢的 矮劣魔"
	
	
class ReliquaryofSouls(Minion):
	Class, race, name = "Priest", "", "Reliquary of Souls"
	mana, attack, health = 1, 1, 3
	index = "Outlands~Priest~Minion~1~1~3~None~Reliquary of Souls~Lifesteal~Deathrattle~Legendary"
	requireTarget, keyWord, description = False, "Lifesteal", "Lifesteal. Deathrattle: Shuffle 'Leliquary Prime' into your deck"
	name_CN = "灵魂之匣"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [ShuffleReliquaryPrimeintoYourDeck(self)]
		
class ShuffleReliquaryPrimeintoYourDeck(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.Game.Hand_Deck.shuffleCardintoDeck(ReliquaryPrime(self.entity.Game, self.entity.ID), self.entity.ID)
		
	def text(self, CHN):
		return "亡语：将“终极魂匣”洗入你的牌库" if CHN else "Deathrattle: Shuffle 'Reliquary Prime' into your deck"
		
class ReliquaryPrime(Minion):
	Class, race, name = "Priest", "", "Reliquary Prime"
	mana, attack, health = 7, 6, 8
	index = "Outlands~Priest~Minion~7~6~8~None~Reliquary Prime~Taunt~Lifesteal~Legendary~Uncollectible"
	requireTarget, keyWord, description = False, "Taunt,Lifesteal", "Taunt, Lifesteal. Only you can target this with spells and Hero Powers"
	name_CN = "终极魂匣"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.marks["Enemy Evasive"] = 1
		
		
class Renew(Spell):
	Class, name = "Priest", "Renew"
	requireTarget, mana = True, 1
	index = "Outlands~Priest~Spell~1~Renew"
	description = "Restore 3 Health. Discover a spell"
	name_CN = "复苏"
	poolIdentifier = "Priest Spells"
	@classmethod
	def generatePool(cls, Game):
		return [Class+" Spells" for Class in Game.Classes], \
				[[value for key, value in Game.ClassCards[Class].items() if "~Spell~" in key] for Class in Game.Classes]
				
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if target:
			heal = 3 * (2 ** self.countHealDouble())
			self.restoresHealth(target, heal)
			if curGame.mode == 0:
				if curGame.guides:
					curGame.Hand_Deck.addCardtoHand(curGame.guides.pop(0), self.ID, "type", byDiscover=True)
				else:
					key = classforDiscover(self)+" Spells"
					if self.ID != curGame.turn or "byOthers" in comment:
						spell = npchoice(self.rngPool(key))
						curGame.fixedGuides.append(spell)
						curGame.Hand_Deck.addCardtoHand(spell, self.ID, "type", byDiscover=True)
					else:
						spells = npchoice(self.rngPool(key), 3, replace=False)
						curGame.options = [spell(curGame, self.ID) for spell in spells]
						curGame.Discover.startDiscover(self)
		return target
		
	def discoverDecided(self, option, info):
		self.Game.fixedGuides.append(type(option))
		self.Game.Hand_Deck.addCardtoHand(option, self.ID, byDiscover=True)
		
		
class DragonmawSentinel(Minion):
	Class, race, name = "Priest", "", "Dragonmaw Sentinel"
	mana, attack, health = 2, 1, 4
	index = "Outlands~Priest~Minion~2~1~4~None~Dragonmaw Sentinel~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: If you're holding a Dragon, gain +1 Attack and Lifesteal"
	name_CN = "龙喉哨兵"
	
	def effCanTrig(self): #Friendly characters are always selectable.
		self.effectViable = self.Game.Hand_Deck.holdingDragon(self.ID)
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if self.Game.Hand_Deck.holdingDragon(self.ID):
			self.buffDebuff(1, 0)
			self.getsKeyword("Lifesteal")
		return None
		
		
class SethekkVeilweaver(Minion):
	Class, race, name = "Priest", "", "Sethekk Veilweaver"
	mana, attack, health = 2, 2, 3
	index = "Outlands~Priest~Minion~2~2~3~None~Sethekk Veilweaver"
	requireTarget, keyWord, description = False, "", "After you cast a spell on a minion, add a Priest spell to your hand"
	name_CN = "塞泰克 织巢者"
	poolIdentifier = "Priest Spells"
	@classmethod
	def generatePool(cls, Game):
		return "Priest Spells", [value for key, value in Game.ClassCards["Priest"].items() if "~Spell~" in key]
		
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_SethekkVeilweaver(self)]
		
class Trig_SethekkVeilweaver(TrigBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["SpellBeenPlayed"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject.ID == self.entity.ID and target and target.type == "Minion"
		
	def text(self, CHN):
		return "在你对一个随从施放法术后，随机将一张牧师法术牌置入你的手牌" if CHN \
				else "After you cast a spell on a minion, add a Priest spell to your hand"
				
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		curGame = self.entity.Game
		if curGame.mode == 0:
			if curGame.guides:
				spell = curGame.guides.pop(0)
			else:
				spell = npchoice(self.rngPool("Priest Spells"))
				curGame.fixedGuides.append(spell)
			curGame.Hand_Deck.addCardtoHand(spell, self.entity.ID, "type")
			
			
class Apotheosis(Spell):
	Class, name = "Priest", "Apotheosis"
	requireTarget, mana = True, 3
	index = "Outlands~Priest~Spell~3~Apotheosis"
	description = "Give a minion +2/+3 and Lifesteal"
	name_CN = "神圣化身"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			target.buffDebuff(2, 3)
			target.getsKeyword("Lifesteal")
		return target
		
		
class DragonmawOverseer(Minion):
	Class, race, name = "Priest", "", "Dragonmaw Overseer"
	mana, attack, health = 3, 2, 2
	index = "Outlands~Priest~Minion~3~2~2~None~Dragonmaw Overseer"
	requireTarget, keyWord, description = False, "", "At the end of your turn, give another friendly minion +2/+2"
	name_CN = "龙喉监工"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_DragonmawOverseer(self)]
		
class Trig_DragonmawOverseer(TrigBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["TurnEnds"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and ID == self.entity.ID
		
	def text(self, CHN):
		return "在你的回合结束时，使另一个友方随从获得+2/+2" if CHN \
				else "At the end of your turn, give another friendly minion +2/+2"
				
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		curGame = self.entity.Game
		if curGame.mode == 0:
			if curGame.guides:
				i = curGame.guides.pop(0)
			else:
				minions = curGame.minionsonBoard(self.entity.ID)
				try: minions.remove(self.entity)
				except: pass
				i = npchoice(minions).pos if minions else -1
				curGame.fixedGuides.append(i)
			if i > -1:
				minion = curGame.minions[self.entity.ID][i]
				minion.buffDebuff(2, 2)
				
				
class PsycheSplit(Spell):
	Class, name = "Priest", "Psyche Split"
	requireTarget, mana = True, 5
	index = "Outlands~Priest~Spell~5~Psyche Split"
	description = "Give a minion +1/+2. Summon a copy of it"
	name_CN = "心灵分裂"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			target.buffDebuff(1, 2)
			Copy = target.selfCopy(target.ID)
			self.Game.summon(Copy, target.pos+1, self.ID)
		return target
		
		
class SkeletalDragon(Minion):
	Class, race, name = "Priest", "Dragon", "Skeletal Dragon"
	mana, attack, health = 7, 4, 9
	index = "Outlands~Priest~Minion~7~4~9~Dragon~Skeletal Dragon~Taunt"
	requireTarget, keyWord, description = False, "Taunt", "Taunt. At the end of your turn, add a Dragon to your hand"
	name_CN = "骸骨巨龙"
	poolIdentifier = "Dragons"
	@classmethod
	def generatePool(cls, Game):
		return "Dragons", list(Game.MinionswithRace["Dragon"].values())
		
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_SkeletalDragon(self)]
		
class Trig_SkeletalDragon(TrigBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["TurnEnds"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and ID == self.entity.ID
		
	def text(self, CHN):
		return "在你的回合结束时，将一张龙牌置入你的手牌" if CHN \
				else "At the end of your turn, add a Dragon to your hand"
				
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		curGame = self.entity.Game
		if curGame.mode == 0:
			if curGame.guides:
				dragon = curGame.guides.pop(0)
			else:
				dragon = npchoice(self.rngPool("Dragons"))
				curGame.fixedGuides.append(dragon)
			curGame.Hand_Deck.addCardtoHand(dragon, self.entity.ID, "type")
			
			
class SoulMirror(Spell):
	Class, name = "Priest", "Soul Mirror"
	requireTarget, mana = False, 7
	index = "Outlands~Priest~Spell~7~Soul Mirror~Legendary"
	description = "Summon copies of enemy minions. They attack their copies"
	name_CN = "灵魂之镜"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		pairs = [[], []]
		for minion in self.Game.minionsonBoard(3-self.ID):
			Copy = minion.selfCopy(self.ID)
			pairs[0].append(minion)
			pairs[1].append(Copy)
		if pairs[1] != []:
			if self.Game.summon(pairs[1], (-1, "totheRightEnd"), self.ID):
				for minion, Copy in zip(pairs[0], pairs[1]):
					if minion.onBoard and minion.health > 0 and minion.dead == False and Copy.onBoard and Copy.health > 0 and Copy.dead == False:
						#假设不消耗攻击机会，那些随从在攻击之后被我方拐走仍然可以攻击
						#def battle(self, subject, target, verifySelectable=True, useAttChance=True, resolveDeath=True, resetRedirectionTriggers=True)
						self.Game.battle(minion, Copy, verifySelectable=False, useAttChance=False, resolveDeath=False, resetRedirectionTriggers=True)
		return None
		
		
"""Rogue cards"""
class BlackjackStunner(Minion):
	Class, race, name = "Rogue", "", "Blackjack Stunner"
	mana, attack, health = 1, 1, 2
	index = "Outlands~Rogue~Minion~1~1~2~None~Blackjack Stunner~Battlecry"
	requireTarget, keyWord, description = True, "", "Battlecry: If you control a Secret, return a minion to its owner's hand. It costs (1) more"
	name_CN = "钉棍终结者"
	def effCanTrig(self):
		self.effectViable = self.Game.Secrets.secrets[self.ID] != []
		
	def returnTrue(self, choice=0):
		return self.Game.Secrets.secrets[self.ID] != []
		
	def targetExists(self, choice=0):
		return self.selectableMinionExists(choice)
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target != self and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		#假设第二次生效时不会不在场上的随从生效
		if target and target.onBoard:
			#假设那张随从在进入手牌前接受-2费效果。可以被娜迦海巫覆盖。
			manaMod = ManaMod(target, changeby=+1, changeto=-1)
			self.Game.returnMiniontoHand(target, deathrattlesStayArmed=False, manaMod=manaMod)
		return target
		
		
class Spymistress(Minion):
	Class, race, name = "Rogue", "", "Spymistress"
	mana, attack, health = 1, 3, 1
	index = "Outlands~Rogue~Minion~1~3~1~None~Spymistress~Stealth"
	requireTarget, keyWord, description = False, "Stealth", "Stealth"
	name_CN = "间谍女郎"
	
	
class Ambush(Secret):
	Class, name = "Rogue", "Ambush"
	requireTarget, mana = False, 2
	index = "Outlands~Rogue~Spell~2~Ambush~~Secret"
	description = "Secret: After your opponent plays a minion, summon a 2/3 Ambusher with Poisonous"
	name_CN = "伏击"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_Ambush(self)]
		
class Trig_Ambush(SecretTrigger):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionBeenPlayed"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.ID != self.entity.Game.turn and subject.ID != self.entity.ID and self.entity.Game.space(self.entity.ID) > 0
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.Game.summon(BrokenAmbusher(self.entity.Game, self.entity.ID), -1, self.entity.ID)
		
class BrokenAmbusher(Minion):
	Class, race, name = "Rogue", "", "Broken Ambusher"
	mana, attack, health = 2, 2, 3
	index = "Outlands~Rogue~Minion~2~2~3~None~Broken Ambusher~Poisonous~Uncollectible"
	requireTarget, keyWord, description = False, "Poisonous", "Poisonous"
	name_CN = "破碎者伏兵"
	
	
class AshtongueSlayer(Minion):
	Class, race, name = "Rogue", "", "Ashtongue Slayer"
	mana, attack, health = 2, 3, 2
	index = "Outlands~Rogue~Minion~2~3~2~None~Ashtongue Slayer~Battlecry"
	requireTarget, keyWord, description = True, "", "Battlecry: Give a Stealthed minion +3 Attack and Immune this turn"
	name_CN = "灰舌杀手"
	def targetExists(self, choice=0):
		return self.selectableFriendlyMinionExists(choice)
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target != self and (target.keyWords["Stealth"] > 0 or target.status["Temp Stealth"] > 0) and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			target.buffDebuff(3, 0, "EndofTurn")
			target.status["Immune"] += 1
		return target
		
		
class Bamboozle(Secret):
	Class, name = "Rogue", "Bamboozle"
	requireTarget, mana = False, 2
	index = "Outlands~Rogue~Spell~2~Bamboozle~~Secret"
	description = "Secret: When one of your minions is attacked, transform it into a random one that costs (3) more"
	name_CN = "偷天换日"
	poolIdentifier = "3-Cost Minions to Summon"
	@classmethod
	def generatePool(cls, Game):
		return ["%d-Cost Minions to Summon"%cost for cost in Game.MinionsofCost.keys()], \
				[list(Game.MinionsofCost[cost].values()) for cost in Game.MinionsofCost.keys()]
				
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_Bamboozle(self)]
		
class Trig_Bamboozle(SecretTrigger):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionAttacksMinion", "HeroAttacksMinion"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.ID != self.entity.Game.turn and target[0].ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		curGame = self.entity.Game
		if curGame.mode == 0:
			if curGame.guides:
				newMinion = curGame.guides.pop(0)
			else:
				cost = type(target[0]).mana + 3
				while cost not in curGame.MinionsofCost:
					cost -= 1
				newMinion = npchoice(self.rngPool("%d-Cost Minions to Summon"%cost))
				curGame.fixedGuides.append(newMinion)
			#不知道如果攻击目标已经被导离这个目标随从之后是否会把目标重导向回它，假设不会
			newMinion = newMinion(curGame, self.entity.ID)
			curGame.transform(target[0], newMinion)
			if target[0] == target[1]: target[0], target[1] = newMinion, newMinion
			else: target[0] = newMinion
			
			
class DirtyTricks(Secret):
	Class, name = "Rogue", "Dirty Tricks"
	requireTarget, mana = False, 2
	index = "Outlands~Rogue~Spell~2~Dirty Tricks~~Secret"
	description = "Secret: After your opponent casts a spell, draw 2 cards"
	name_CN = "邪恶计谋"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_DirtyTricks(self)]
		
class Trig_DirtyTricks(SecretTrigger):
	def __init__(self, entity):
		self.blank_init(entity, ["SpellBeenPlayed"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.ID != self.entity.Game.turn and subject.ID != self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.Game.Hand_Deck.drawCard(self.entity.ID)
		self.entity.Game.Hand_Deck.drawCard(self.entity.ID)
		
		
class ShadowjewelerHanar(Minion):
	Class, race, name = "Rogue", "", "Shadowjeweler Hanar"
	mana, attack, health = 2, 1, 4
	index = "Outlands~Rogue~Minion~2~1~4~None~Shadowjeweler Hanar~Legendary"
	requireTarget, keyWord, description = False, "", "After you play a Secret, Discover a Secret from a different class"
	name_CN = "暗影珠宝师 汉纳尔"
	poolIdentifier = "Rogue Secrets"
	@classmethod
	def generatePool(cls, Game):
		classes, lists = [], []
		for Class in Game.Classes:
			secrets = [value for key, value in Game.ClassCards[Class].items() if value.description.startswith("Secret:")]
			if secrets:
				classes.append(Class+" Secrets")
				lists.append(secrets)
		return classes, lists
		
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_ShadowjewelerHanar(self)]
		
	def discoverDecided(self, option, info):
		self.Game.fixedGuides.append(type(option))
		self.Game.Hand_Deck.addCardtoHand(option, self.ID, byDiscover=True)
		
class Trig_ShadowjewelerHanar(TrigBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["SpellBeenPlayed"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject.ID == self.entity.ID and subject.description.startswith("Secret:")
		
	def text(self, CHN):
		return "在你使用一张奥秘牌后，发现一张不同职业的奥秘牌" if CHN \
				else "After you play a Secret, Discover a Secret from a different class"
				
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		minion, curGame = self.entity, self.entity.Game
		if minion.ID == curGame.turn:
			if curGame.mode == 0:
				if curGame.guides:
					curGame.Hand_Deck.addCardtoHand(curGame.guides.pop(0), minion.ID, "type")
				else:
					ClasseswithSecrets = ["Hunter", "Mage", "Paladin", "Rogue"]
					try: ClasseswithSecrets.remove(subject.Class)
					except: pass
					Classes = npchoice(ClasseswithSecrets, 3, replace=False)
					secrets = [npchoice(self.rngPool(Class+" Secrets")) for Class in Classes]
					curGame.options = [secret(curGame, minion.ID) for secret in secrets]
					curGame.Discover.startDiscover(minion)
					
					
class Akama(Minion):
	Class, race, name = "Rogue", "", "Akama"
	mana, attack, health = 3, 3, 4
	index = "Outlands~Rogue~Minion~3~3~4~None~Akama~Stealth~Deathrattle~Legendary"
	requireTarget, keyWord, description = False, "Stealth", "Stealth. Deathrattle: Shuffle 'Akama Prime' into your deck"
	name_CN = "阿卡玛"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [ShuffleAkamaPrimeintoYourDeck(self)]
		
class ShuffleAkamaPrimeintoYourDeck(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.Game.Hand_Deck.shuffleCardintoDeck(AkamaPrime(self.entity.Game, self.entity.ID), self.entity.ID)
		
	def text(self, CHN):
		return "亡语：将“终极阿卡玛”洗入你的牌库" if CHN else "Deathrattle: Shuffle 'Akama Prime' into your deck"
				
class AkamaPrime(Minion):
	Class, race, name = "Rogue", "", "Akama Prime"
	mana, attack, health = 6, 6, 5
	index = "Outlands~Rogue~Minion~6~6~5~None~Akama Prime~Stealth~Legendary~Uncollectible"
	requireTarget, keyWord, description = False, "Stealth", "Permanently Stealthed"
	name_CN = "终极阿卡玛"
	
	def losesKeyword(self, keyWord):
		if self.onBoard or self.inHand:
			if keyWord == "Stealth":
				if self.silenced: #只有在被沉默的时候才会失去潜行
					self.keyWords["Stealth"] = 0
			elif keyWord == "Divine Shield":
				self.keyWords["Divine Shield"] = 0
				self.Game.sendSignal("MinionLosesDivineShield", self.Game.turn, None, self, 0, "")
			else:
				if self.keyWords[keyWord] > 0:
					self.keyWords[keyWord] -= 1
			if self.onBoard:
				self.decideAttChances_base()
				if keyWord == "Charge":
					self.Game.sendSignal("MinionChargeChanged", self.Game.turn, self, None, 0, "")
					
					
class GreyheartSage(Minion):
	Class, race, name = "Rogue", "", "Greyheart Sage"
	mana, attack, health = 3, 3, 3
	index = "Outlands~Rogue~Minion~3~3~3~None~Greyheart Sage~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: If you control a Stealth minion, draw 2 cards"
	def effCanTrig(self):
		self.effectViable = False
		for minion in self.Game.minionsonBoard(self.ID):
			if minion.keyWords["Stealth"] > 0 or minion.status["Temp Stealth"] > 0:
				self.effectViable = True
				break
				
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		controlStealthMinion = False
		for minion in self.Game.minionsonBoard(self.ID):
			if minion.keyWords["Stealth"] > 0 or minion.status["Temp Stealth"] > 0:
				controlStealthMinion = True
				break
		if controlStealthMinion:
			self.Game.Hand_Deck.drawCard(self.ID)
			self.Game.Hand_Deck.drawCard(self.ID)
		return None
		
		
class CursedVagrant(Minion):
	Class, race, name = "Rogue", "", "Cursed Vagrant"
	mana, attack, health = 7, 7, 5
	index = "Outlands~Rogue~Minion~7~7~5~None~Cursed Vagrant~Deathrattle"
	requireTarget, keyWord, description = False, "", "Deathrattle: Summon a 7/5 Shadow with Stealth"
	name_CN = "被诅咒的 流浪者"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [SummonaShadowwithTaunt(self)]
		
class SummonaShadowwithTaunt(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.Game.summon(CursedShadow(self.entity.Game, self.entity.ID), self.entity.pos+1, self.entity.ID)
		
	def text(self, CHN):
		return "亡语：召唤一个7/5并具有潜行的阴影" if CHN else "Deathrattle: Summon a 7/5 Shadow with Stealth"
		
class CursedShadow(Minion):
	Class, race, name = "Rogue", "", "Cursed Shadow"
	mana, attack, health = 7, 7, 5
	index = "Outlands~Rogue~Minion~7~7~5~None~Cursed Shadow~Stealth~Uncollectible"
	requireTarget, keyWord, description = False, "Stealth", "Stealth"
	name_CN = "被诅咒的 阴影"
	
	
"""Shaman cards"""
class BogstrokClacker(Minion):
	Class, race, name = "Shaman", "", "Bogstrok Clacker"
	mana, attack, health = 3, 3, 3
	index = "Outlands~Shaman~Minion~3~3~3~None~Bogstrok Clacker~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Transform adjacent minions into random minions that cost (1) more"
	name_CN = "泥泽巨拳 龙虾人"
	poolIdentifier = "1-Cost Minions to Summon"
	@classmethod
	def generatePool(cls, Game):
		return ["%d-Cost Minions to Summon"%cost for cost in Game.MinionsofCost.keys()], \
				[list(Game.MinionsofCost[cost].values()) for cost in Game.MinionsofCost.keys()]
				
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if self.onBoard:
			curGame = self.Game
			if curGame.mode == 0:
				minions = self.Game.neighbors2(self)[0]
				if curGame.guides:
					newMinions = curGame.guides.pop(0)
				else:
					newMinions = []
					for minion in minions:
						cost = type(minion).mana + 3
						while cost not in curGame.MinionsofCost:
							cost -= 1
						newMinions.append(npchoice(self.rngPool("%d-Cost Minions to Summon"%cost)))
					curGame.fixedGuides.append(tuple(newMinions))
				for minion, newMinion in zip(minions, newMinions):
					curGame.transform(minion, newMinion(curGame, self.ID))
		return None
		
		
class LadyVashj(Minion):
	Class, race, name = "Shaman", "", "Lady Vashj"
	mana, attack, health = 3, 4, 3
	index = "Outlands~Shaman~Minion~3~4~3~None~Lady Vashj~Spell Damage~Deathrattle~Legendary"
	requireTarget, keyWord, description = False, "Spell Damage", "Spell Damage +1. Deathrattle: Shuffle 'Vashj Prime' into your deck"
	name_CN = "瓦斯琪女士"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [ShuffleVashjPrimeintoYourDeck(self)]
		
class ShuffleVashjPrimeintoYourDeck(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.Game.Hand_Deck.shuffleCardintoDeck(VashjPrime(self.entity.Game, self.entity.ID), self.entity.ID)
		
	def text(self, CHN):
		return "亡语：将“终极瓦斯琪”洗入你的牌库" if CHN else "Deathrattle: Shuffle 'Vashj Prime' into your deck"
		
class VashjPrime(Minion):
	Class, race, name = "Shaman", "", "Vashj Prime"
	mana, attack, health = 7, 5, 4
	index = "Outlands~Shaman~Minion~7~5~4~None~Vashj Prime~Spell Damage~Battlecry~Legendary~Uncollectible"
	requireTarget, keyWord, description = False, "Spell Damage", "Spell Damage +1. Battlecry: Draw 3 spells. Reduce their Cost by (3)"
	name_CN = "终极瓦斯琪"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		ownDeck = curGame.Hand_Deck.decks[self.ID]
		if curGame.mode == 0:
			for num in range(3):
				if curGame.guides:
					i = curGame.guides.pop(0)
				else:
					spells = [i for i, card in enumerate(ownDeck) if card.type == "Spell"]
					i = npchoice(spells) if spells else -1
					curGame.fixedGuides.append(i)
				if i > -1:
					spell = curGame.Hand_Deck.drawCard(self.ID, i)[0]
					if spell: ManaMod(spell, changeby=-3, changeto=-1).applies()
				else: break
		return None
		
		
class Marshspawn(Minion):
	Class, race, name = "Shaman", "Elemental", "Marshspawn"
	mana, attack, health = 3, 3, 4
	index = "Outlands~Shaman~Minion~3~3~4~Elemental~Marshspawn~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: If you cast a spell last turn, Discover a spell"
	name_CN = "沼泽之子"
	poolIdentifier = "Shaman Spells"
	@classmethod
	def generatePool(cls, Game):
		return [Class+" Spells" for Class in Game.Classes], \
				[[value for key, value in Game.ClassCards[Class].items() if "~Spell~" in key] for Class in Game.Classes]
				
	def effCanTrig(self):
		self.effectViable = self.Game.Counters.spellsPlayedLastTurn[self.ID] != []
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if curGame.Counters.spellsPlayedLastTurn[self.ID] and self.ID == curGame.turn:
			if curGame.mode == 0:
				if curGame.guides:
					curGame.Hand_Deck.addCardtoHand(curGame.guides.pop(0), self.ID, "type", byDiscover=True)
				else:
					key = classforDiscover(self)+" Spells"
					if "byOthers" in comment:
						spell = npchoice(self.rngPool(key))
						curGame.fixedGuides.append(spell)
						curGame.Hand_Deck.addCardtoHand(spell, self.ID, "type", byDiscover=True)
					else:
						spells = npchoice(self.rngPool(key), 3, replace=False)
						curGame.options = [spell(curGame, self.ID) for spell in spells]
						curGame.Discover.startDiscover(self)
		return None
		
	def discoverDecided(self, option, info):
		self.Game.fixedGuides.append(type(option))
		self.Game.Hand_Deck.addCardtoHand(option, self.ID, byDiscover=True)
		
		
class SerpentshrinePortal(Spell):
	Class, name = "Shaman", "Serpentshrine Portal"
	requireTarget, mana = True, 3
	index = "Outlands~Shaman~Spell~3~Serpentshrine Portal~Overload"
	description = "Deal 3 damage. Summon a random 3-Cost minion. Overload: (1)"
	name_CN = "毒蛇神殿 传送门"
	poolIdentifier = "3-Cost Minions to Summon"
	@classmethod
	def generatePool(cls, Game):
		return "3-Cost Minions to Summon", list(Game.MinionsofCost[3].values())
		
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.overload = 1
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if target:
			damage = (3 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			self.dealsDamage(target, damage)
			if curGame.mode == 0:
				if curGame.guides:
					minion = curGame.guides.pop(0)
				else:
					minion = npchoice(self.rngPool("3-Cost Minions to Summon"))
					curGame.fixedGuides.append(minion)
				curGame.summon(minion(curGame, self.ID), -1, self.ID)
		return target
		
		
class TotemicReflection(Spell):
	Class, name = "Shaman", "Totemic Reflection"
	requireTarget, mana = True, 3
	index = "Outlands~Shaman~Spell~3~Totemic Reflection"
	description = "Give a minion +2/2. If it's a Totem, summon a copy of it"
	name_CN = "图腾映像"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			target.buffDebuff(2, 2)
			if "Totem" in target.race:
				Copy = target.selfCopy(target.ID)
				self.Game.summon(Copy, target.pos+1, self.ID)
		return target
		
		
class Torrent(Spell):
	Class, name = "Shaman", "Torrent"
	requireTarget, mana = True, 4
	index = "Outlands~Shaman~Spell~4~Torrent"
	description = "Deal 8 damage to a minion. Costs (3) less if you cast a spell last turn"
	name_CN = "洪流"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
		
	def effCanTrig(self):
		self.effectViable = self.Game.Counters.spellsPlayedLastTurn[self.ID] != []
		
	def selfManaChange(self):
		if self.inHand and self.Game.Counters.spellsPlayedLastTurn[self.ID] != []:
			self.mana -= 3
			self.mana = max(self.mana, 0)
			
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			damage = (8 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			self.dealsDamage(target, damage)
		return target
		
		
class VividSpores(Spell):
	Class, name = "Shaman", "Vivid Spores"
	requireTarget, mana = False, 4
	index = "Outlands~Shaman~Spell~4~Vivid Spores"
	description = "Give your minions 'Deathrattle: Resummon this minion'"
	name_CN = "鲜活孢子"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		for minion in self.Game.minionsonBoard(self.ID):
			trig = ResummonThisMinion_VividSpores(minion)
			minion.deathrattles.append(trig)
			trig.connect()
		return None
		
class ResummonThisMinion_VividSpores(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		#This Deathrattle can't possibly be triggered in hand
		self.entity.Game.summon(type(self.entity)(self.entity.Game, self.entity.ID), self.entity.pos+1, self.entity.ID)
		
		
class BoggspineKnuckles(Weapon):
	Class, name, description = "Shaman", "Boggspine Knuckles", "After your hero attacks, transform your minions into ones that cost (1) more"
	mana, attack, durability = 5, 3, 2
	index = "Outlands~Shaman~Weapon~5~3~2~Boggspine Knuckles"
	name_CN = "沼泽拳刺"
	poolIdentifier = "1-Cost Minions to Summon"
	@classmethod
	def generatePool(cls, Game):
		return ["%d-Cost Minions to Summon"%cost for cost in Game.MinionsofCost.keys()], \
				[list(Game.MinionsofCost[cost].values()) for cost in Game.MinionsofCost.keys()]
				
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_BoggspineKnuckles(self)]
		
class Trig_BoggspineKnuckles(TrigBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["HeroAttackedMinion", "HeroAttackedHero"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject == self.entity.Game.heroes[self.entity.ID] and self.entity.onBoard
		
	def text(self, CHN):
		return "在你的英雄攻击后，随机将你的所有随从变形成为法力值消耗增加(1)点的随从" if CHN \
				else "After your hero attacks, transform your minions into ones that cost (1) more"
				
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		curGame = self.entity.Game
		if curGame.mode == 0:
			for minion in curGame.minionsonBoard(self.entity.ID):
				if curGame.guides:
					newMinion = curGame.guides.pop(0)
				else:
					cost = type(minion).mana + 1
					while cost not in curGame.MinionsofCost:
						cost -= 1
					newMinion = npchoice(self.rngPool("%d-Cost Minions to Summon"%cost))
					curGame.fixedGuides.append(newMinion)
				curGame.transform(minion, newMinion(curGame, minion.ID))
				
				
class ShatteredRumbler(Minion):
	Class, race, name = "Shaman", "Elemental", "Shattered Rumbler"
	mana, attack, health = 5, 5, 6
	index = "Outlands~Shaman~Minion~5~5~6~Elemental~Shattered Rumbler~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: If you cast a spell last turn, deal 2 damage to all other minions"
	name_CN = "破碎奔行者"
	def effCanTrig(self):
		self.effectViable = self.Game.Counters.spellsPlayedLastTurn[self.ID] != []
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if self.Game.Counters.spellsPlayedLastTurn[self.ID] != []:
			targets = self.Game.minionsonBoard(self.ID, self) + self.Game.minionsonBoard(3-self.ID)
			self.dealsAOE(targets, [2]*len(targets))
		return None
		
		
class TheLurkerBelow(Minion):
	Class, race, name = "Shaman", "Beast", "The Lurker Below"
	mana, attack, health = 6, 6, 5
	index = "Outlands~Shaman~Minion~6~6~5~Beast~The Lurker Below~Battlecry~Legendary"
	requireTarget, keyWord, description = True, "", "Battlecry: Deal 3 damage to an enemy minion, it dies, repeat on one of its neighbors"
	name_CN = "鱼斯拉"
	def targetExists(self, choice=0):
		return self.selectableEnemyMinionExists(choice)
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.ID != self.ID and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		#假设战吼触发时目标随从已经死亡并离场，则不会触发接下来的伤害
		#假设不涉及强制死亡
		if target:
			curGame = self.Game
			self.dealsDamage(target, 3)
			if curGame.mode == 0:
				minion = None
				if curGame.guides:
					i, where, direction = curGame.guides.pop(0)
					if where: minion = curGame.find(i, where)
				else:
					direction = ''
					if target.onBoard and (target.health < 1 or target.dead):
						neighbors, dist = self.Game.neighbors2(target)
						if dist == 1:
							if nprandint(2): minion, direction = neighbors[1], 1
							else: minion, direction = neighbors[0], 0
						elif dist < 0: minion, direction = neighbors[0], 0
						elif dist == 2: minion, direction = neighbors[0], 1
					if minion: curGame.fixedGuides.append((minion.pos, "Minion%d"%minion.ID, direction))
					else: curGame.fixedGuides.append((0, '', ''))
				#开始循环
				while minion: #如果下个目标没有随从了，则停止循环
					self.dealsDamage(minion, 3)
					if minion.health < 1 or minion.dead:
						neighbors, dist = self.Game.neighbors2(minion)
						minion = None
						if direction:
							if dist > 0: minion = neighbors[2-dist]
							else: break
						else:
							if dist == 1 or dist == -1: minion = neighbors[0]
							else: break
					else:
						break
		return target
		
		
"""Warlock cards"""
class ShadowCouncil(Spell):
	Class, name = "Warlock", "Shadow Council"
	requireTarget, mana = False, 1
	index = "Outlands~Warlock~Spell~1~Shadow Council"
	description = "Replace your hand with random Demons. Give them +2/+2"
	name_CN = "暗影议会"
	poolIdentifier = "Demons"
	@classmethod
	def generatePool(cls, Game):
		return "Demons", list(Game.MinionswithRace["Demon"].values())
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if curGame.mode == 0:
			if curGame.guides:
				demons = curGame.guides.pop(0)
			else:
				demons = tuple(npchoice(self.rngPool("Demons"), len(curGame.Hand_Deck.hands[self.ID]), replace=True))
				curGame.fixedGuides.append(demons)
			if demons:
				demons = [demon(curGame, self.ID) for demon in demons]
				curGame.Hand_Deck.extractfromHand(None, self.ID, all=True, enemyCanSee=False)
				curGame.Hand_Deck.addCardtoHand(demons, self.ID)
				for demon in demons: demon.buffDebuff(2, 2)
		return None
		
		
class UnstableFelbolt(Spell):
	Class, name = "Warlock", "Unstable Felbolt"
	requireTarget, mana = True, 1
	index = "Outlands~Warlock~Spell~1~Unstable Felbolt"
	description = "Deal 3 damage to an enemy minion and a random friendly one"
	name_CN = "不稳定的 邪能箭"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		damage = (3 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		if target:
			self.dealsDamage(target, damage)
		if curGame.mode == 0:
			minion = None
			if curGame.guides:
				i, where = curGame.guides.pop(0)
				if where: minion = curGame.find(i, where)
			else:
				ownMinions = curGame.minionsonBoard(self.ID)
				if ownMinions:
					minion = npchoice(ownMinions)
					curGame.fixedGuides.append((minion.pos, "Minion%d"%minion.ID))
				else:
					curGame.fixedGuides.append((0, ''))
			if minion:
				self.dealsDamage(minion, damage)
		return target
		
		
class ImprisonedScrapImp(Minion_Dormantfor2turns):
	Class, race, name = "Warlock", "Demon", "Imprisoned Scrap Imp"
	mana, attack, health = 2, 3, 3
	index = "Outlands~Warlock~Minion~2~3~3~Demon~Imprisoned Scrap Imp"
	requireTarget, keyWord, description = False, "", "Dormant for 2 turns. When this awakens, give all minions in your hand +2/+1"
	name_CN = "被禁锢的 拾荒小鬼"
	
	def awakenEffect(self):
		for card in self.Game.Hand_Deck.hands[self.ID][:]:
			if card.type == "Minion": card.buffDebuff(2, 1)
			
			
class KanrethadEbonlocke(Minion):
	Class, race, name = "Warlock", "", "Kanrethad Ebonlocke"
	mana, attack, health = 2, 3, 2
	index = "Outlands~Warlock~Minion~2~3~2~None~Kanrethad Ebonlocke~Deathrattle~Legendary"
	requireTarget, keyWord, description = False, "", "Your Demons cost (1) less. Deathrattle: Shuffle 'Kanrethad Prime' into your deck"
	name_CN = "坎雷萨德 埃伯洛克"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.auras["Your Demons cost (1) less"] = ManaAura(self, changeby=-1, changeto=-1)
		self.deathrattles = [ShuffleKanrethadPrimeintoYourDeck(self)]
		
	def manaAuraApplicable(self, subject): #ID用于判定是否是我方手中的随从
		return subject.ID == self.ID and subject.type == "Minion" and "Demon" in subject.race
		
class ShuffleKanrethadPrimeintoYourDeck(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.Game.Hand_Deck.shuffleCardintoDeck(KanrethadPrime(self.entity.Game, self.entity.ID), self.entity.ID)
		
	def text(self, CHN):
		return "亡语：将“终极坎雷萨德”洗入你的牌库" if CHN else "Deathrattle: Shuffle 'Kanrethad Prime' into your deck"
		
		
class KanrethadPrime(Minion):
	Class, race, name = "Warlock", "Demon", "Kanrethad Prime"
	mana, attack, health = 8, 7, 6
	index = "Outlands~Warlock~Minion~8~7~6~Demon~Kanrethad Prime~Battlecry~Legendary~Uncollectible"
	requireTarget, keyWord, description = False, "", "Battlecry: Summon 3 friendly Demons that died this game"
	name_CN = "终极 坎雷萨德"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if curGame.mode == 0:
			if curGame.guides:
				demons = curGame.guides.pop(0)
			else:
				demonsDied = [curGame.cardPool[index] for index in curGame.Counters.minionsDiedThisGame[self.ID] if "~Demon~" in index]
				numSummon = min(len(demonsDied), 3)
				demons = tuple(npchoice(demonsDied, numSummon, replace=True)) if numSummon else ()
				curGame.fixedGuides.append(demons)
			if demons:
				pos = (self.pos, "totheRight") if self.onBoard else (-1, "totheRightEnd")
				curGame.summon([demon(curGame, self.ID) for demon in demons], pos, self.ID)		
		return None
		
		
class Darkglare(Minion):
	Class, race, name = "Warlock", "Demon", "Darkglare"
	mana, attack, health = 2, 2, 3
	index = "Outlands~Warlock~Minion~2~2~3~Demon~Darkglare"
	requireTarget, keyWord, description = False, "", "After your hero takes damage, refresh a Mana Crystals"
	name_CN = "黑眼"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_Darkglare(self)]
		
class Trig_Darkglare(TrigBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["HeroTookDmg"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return target == self.entity.Game.heroes[self.entity.ID]
		
	def text(self, CHN):
		return "在你的英雄受到伤害后，复原一个法力水晶" if CHN else "After your hero takes damage, refresh a Mana Crystals"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.Game.Manas.restoreManaCrystal(1, self.entity.ID)
		
		
class NightshadeMatron(Minion):
	Class, race, name = "Warlock", "Demon", "Nightshade Matron"
	mana, attack, health = 4, 5, 5
	index = "Outlands~Warlock~Minion~4~5~5~Demon~Nightshade Matron~Rush~Battlecry"
	requireTarget, keyWord, description = False, "Rush", "Rush. Battlecry: Discard your highest Cost card"
	name_CN = "夜影主母"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if curGame.mode == 0:
			if curGame.guides:
				i = curGame.guides.pop(0)
			else:
				cards, highestCost = [], -npinf
				for i, card in enumerate(curGame.Hand_Deck.hands[self.ID]):
					if card.mana > highestCost: cards, highestCost = [i], card.mana
					elif card.mana == highestCost: cards.append(i)
				i = npchoice(cards) if cards else -1
				curGame.fixedGuides.append(i)
			if i > -1: curGame.Hand_Deck.discardCard(self.ID, i)
		return None
		
		
class TheDarkPortal(Spell):
	Class, name = "Warlock", "The Dark Portal"
	requireTarget, mana = False, 4
	index = "Outlands~Warlock~Spell~4~The Dark Portal"
	description = "Draw a minion. If you have at least 8 cards in hand, it costs (5) less"
	name_CN = "黑暗之门"
	def effCanTrig(self):
		self.effectViable = len(self.Game.Hand_Deck.hands[self.ID]) > 7
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if curGame.mode == 0:
			if curGame.guides:
				i = curGame.guides.pop(0)
			else:
				minions = [i for i, card in enumerate(curGame.Hand_Deck.decks[self.ID]) if card.type == "Minion"]
				i = npchoice(minions) if minions else -1
				curGame.fixedGuides.append(i)
			if i > -1:
				minion = curGame.Hand_Deck.drawCard(self.ID, i)[0]
				if minion and len(curGame.Hand_Deck.hands[self.ID]) > 7:
					ManaMod(minion, changeby=-5, changeto=-1).applies()
		return None
		
		
class HandofGuldan(Spell):
	Class, name = "Warlock", "Hand of Gul'dan"
	requireTarget, mana = False, 6
	index = "Outlands~Warlock~Spell~6~Hand of Gul'dan"
	description = "When you play or discard this, draw 3 cards"
	name_CN = "古尔丹之手"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggers["Discarded"] = [self.whenEffective]
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		for i in range(3): self.Game.Hand_Deck.drawCard(self.ID)
		return None
		
		
class KelidantheBreaker(Minion):
	Class, race, name = "Warlock", "", "Keli'dan the Breaker"
	mana, attack, health = 6, 3, 3
	index = "Outlands~Warlock~Minion~6~3~3~None~Keli'dan the Breaker~Battlecry~Legendary"
	requireTarget, keyWord, description = True, "", "Battlecry: Destroy a minion. If drawn this turn, instead destroy all minions except this one"
	name_CN = "击碎者克里丹"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.justDrawn = False
		self.trigsHand = [Trig_KelidantheBreaker(self)]
		
	def whenDrawn(self):
		self.justDrawn = True
		
	def returnTrue(self, choice=0):
		return self.justDrawn == False
		
	def targetExists(self, choice=0):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target != self and target.onBoard
		
	def effCanTrig(self):
		self.effectViable = self.justDrawn
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if self.justDrawn:
			self.Game.killMinion(self, [minion for minion in self.Game.minionsonBoard(1) + self.Game.minionsonBoard(2) if minion != self])
		elif target: #Not just drawn this turn and target is designated
			self.Game.killMinion(self, target)
		return target
		
	def assistCreateCopy(self, recipient):
		recipient.justDrawn = self.justDrawn
		
class Trig_KelidantheBreaker(TrigHand):
	def __init__(self, entity):
		self.blank_init(entity, ["TurnEnds"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.inHand and self.entity.justDrawn and ID == self.entity.ID
		
	def text(self, CHN):
		return "在你的回合结束时，效果变为消灭一个随从" if CHN else "At the end of your turn, the Battlecry becomes 'Destroy a minion'"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.justDrawn = False
		self.disconnect() #只需要触发一次
		
		
class EnhancedDreadlord(Minion):
	Class, race, name = "Warlock", "Demon", "Enhanced Dreadlord"
	mana, attack, health = 8, 5, 7
	index = "Outlands~Warlock~Minion~8~5~7~Demon~Enhanced Dreadlord~Taunt~Deathrattle"
	requireTarget, keyWord, description = False, "Taunt", "Taunt. Deathrattle: Summon a 5/5 Dreadlord with Lifesteal"
	name_CN = "改进型 恐惧魔王"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [SummonaDreadlordwithLifesteal(self)]
		
class SummonaDreadlordwithLifesteal(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.Game.summon(DesperateDreadlord(self.entity.Game, self.entity.ID), self.entity.pos+1, self.entity.ID)\
		
	def text(self, CHN):
		return "亡语：召唤一个5/5并具有吸血的恐惧魔王" if CHN else "Deathrattle: Summon a 5/5 Dreadlord with Lifesteal"
		
class DesperateDreadlord(Minion):
	Class, race, name = "Warlock", "Demon", "Desperate Dreadlord"
	mana, attack, health = 5, 5, 5
	index = "Outlands~Warlock~Minion~5~5~5~Demon~Desperate Dreadlord~Lifesteal~Uncollectible"
	requireTarget, keyWord, description = False, "Lifesteal", "Lifesteal"
	name_CN = "绝望的 恐惧魔王"
	
"""Warrior cards"""
class ImprisonedGanarg(Minion_Dormantfor2turns):
	Class, race, name = "Warrior", "Demon", "Imprisoned Gan'arg"
	mana, attack, health = 1, 2, 2
	index = "Outlands~Warrior~Minion~1~2~2~Demon~Imprisoned Gan'arg"
	requireTarget, keyWord, description = False, "", "Dormant for 2 turns. When this awakens, equip a 3/2 Axe"
	name_CN = "被禁锢的 甘尔葛"
	
	def awakenEffect(self):
		self.Game.equipWeapon(FieryWarAxe(self.Game, self.ID))
		
		
class SwordandBoard(Spell):
	Class, name = "Warrior", "Sword and Board"
	requireTarget, mana = True, 1
	index = "Outlands~Warrior~Spell~1~Sword and Board"
	description = "Deal 2 damage to a minion. Gain 2 Armor"
	name_CN = "剑盾猛攻"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			damage = (2 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			self.dealsDamage(target, damage)
		self.Game.heroes[self.ID].gainsArmor(2)
		return target
		
		
class CorsairCache(Spell):
	Class, name = "Warrior", "Corsair Cache"
	requireTarget, mana = False, 2
	index = "Outlands~Warrior~Spell~2~Corsair Cache"
	description = "Draw a weapon. Give it +1 Durability"
	name_CN = "海盗藏品"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		ownDeck = curGame.Hand_Deck.decks[self.ID]
		if curGame.mode == 0:
			if curGame.guides:
				i = curGame.guides.pop(0)
			else:
				weapons = [i for i, card in enumerate(ownDeck) if card.type == "Weapon"]
				i = npchoice(weapons) if weapons else -1
				curGame.fixedGuides.append(i)
			if i > -1:
				weapon = curGame.Hand_Deck.drawCard(self.ID, i)[0]
				if weapon:
					weapon.gainStat(0, 1)
		return None
		
		
class Bladestorm(Spell):
	Class, name = "Warrior", "Bladestorm"
	requireTarget, mana = False, 3
	index = "Outlands~Warrior~Spell~3~Bladestorm"
	description = "Deal 1 damage to all minions. Repeat until one dies"
	name_CN = "剑刃风暴"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		damage = (1 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		while True:
			targets = self.Game.minionsonBoard(1) + self.Game.minionsonBoard(2)
			if targets == []:
				break
			else:
				targets_damaged, damagesConnected, totalDamageDone = self.dealsAOE(targets, [damage] * len(targets))
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
	name_CN = "噬骨骑兵"
	
	def effCanTrig(self):
		self.effectViable = False
		for minion in self.Game.minionsonBoard(1) + self.Game.minionsonBoard(2):
			if minion.health < minion.health_max:
				self.effectViable = True
				break
				
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		damagedMinionExists = False
		for minion in self.Game.minionsonBoard(1) + self.Game.minionsonBoard(2):
			if minion.health < minion.health_max:
				damagedMinionExists = True
				break
		if damagedMinionExists:
			self.buffDebuff(1, 1)
			self.getsKeyword("Rush")
		return False
		
		
#不知道与博尔夫碎盾和Blur的结算顺序
class BulwarkofAzzinoth(Weapon):
	Class, name, description = "Warrior", "Bulwark of Azzinoth", "Whenever your hero would take damage, this loses 1 Durability instead"
	mana, attack, durability = 3, 1, 4
	index = "Outlands~Warrior~Weapon~3~1~4~Bulwark of Azzinoth~Legendary"
	name_CN = "埃辛诺斯 壁垒"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_BulwarkofAzzinoth(self)]
		
class Trig_BulwarkofAzzinoth(TrigBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["FinalDmgonHero?"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		#Can only prevent damage if there is still durability left
		return target == self.entity.Game.heroes[self.entity.ID] and self.entity.onBoard and self.entity.durability > 0
		
	def text(self, CHN):
		return "每当你的英雄即将受到伤害，改为埃辛诺斯壁垒失去1点耐久度" if CHN \
				else "Whenever your hero would take damage, this loses 1 Durability instead"
				
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		number[0] = 0
		self.entity.loseDurability()
		
		
class WarmaulChallenger(Minion):
	Class, race, name = "Warrior", "", "Warmaul Challenger"
	mana, attack, health = 3, 1, 10
	index = "Outlands~Warrior~Minion~3~1~10~None~Warmaul Challenger~Battlecry"
	requireTarget, keyWord, description = True, "", "Battlecry: Choose an enemy minion. Battle it to the death!"
	name_CN = "战槌挑战者"
	
	def targetExists(self, choice=0):
		return self.selectableEnemyMinionExists(choice)
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.ID != self.ID and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			#该随从会连续攻击那个目标直到一方死亡
			while self.onBoard and self.health > 0 and not self.dead and target.onBoard and target.health > 0 and not target.dead:
				self.Game.battle(self, target, verifySelectable=False, useAttChance=False, resolveDeath=False, resetRedirectionTriggers=False)
		return target
		
		
class KargathBladefist(Minion):
	Class, race, name = "Warrior", "", "Kargath Bladefist"
	mana, attack, health = 4, 4, 4
	index = "Outlands~Warrior~Minion~4~4~4~None~Kargath Bladefist~Rush~Deathrattle~Legendary"
	requireTarget, keyWord, description = False, "Rush", "Rush. Deathrattle: Shuffle 'Kargath Prime' into your deck"
	name_CN = "卡加斯刃拳"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [ShuffleKargathPrimeintoYourDeck(self)]
		
class ShuffleKargathPrimeintoYourDeck(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.Game.Hand_Deck.shuffleCardintoDeck(KargathPrime(self.entity.Game, self.entity.ID), self.entity.ID)
		
	def text(self, CHN):
		return "亡语：将“终极卡加斯”洗入你的牌库" if CHN else "Deathrattle: Shuffle 'Kargath Prime' into your deck"
		
class KargathPrime(Minion):
	Class, race, name = "Warrior", "", "Kargath Prime"
	mana, attack, health = 8, 10, 10
	index = "Outlands~Warrior~Minion~8~10~10~None~Kargath Prime~Rush~Legendary~Uncollectible"
	requireTarget, keyWord, description = False, "Rush", "Rush. Whenever this attacks and kills a minion, gain 10 Armor"
	name_CN = "终极卡加斯"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_KargathPrime(self)]
		
class Trig_KargathPrime(TrigBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionAttackedMinion"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject == self.entity and self.entity.onBoard and (target.health < 1 or target.dead == True)
		
	def text(self, CHN):
		return "每当该随从攻击并消灭一个随从时，获得10点护甲值" if CHN else "Whenever this attacks and kills a minion, gain 10 Armor"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.Game.heroes[self.entity.ID].gainsArmor(10)
		
		
class ScrapGolem(Minion):
	Class, race, name = "Warrior", "Mech", "Scrap Golem"
	mana, attack, health = 5, 4, 5
	index = "Outlands~Warrior~Minion~5~4~5~Mech~Scrap Golem~Taunt~Deathrattle"
	requireTarget, keyWord, description = False, "Taunt", "Taunt. Deathrattle: Gain Armor equal to this minion's Attack"
	name_CN = "废铁魔像"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [GainArmorEqualtoAttack(self)]
		
class GainArmorEqualtoAttack(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.Game.heroes[self.entity.ID].gainsArmor(number)
		
	def text(self, CHN):
		return "亡语：获得等同于该随从攻击力的护甲值" if CHN else "Deathrattle: Gain Armor equal to this minion's Attack"
		
		
class BloodboilBrute(Minion):
	Class, race, name = "Warrior", "", "Bloodboil Brute"
	mana, attack, health = 7, 5, 8
	index = "Outlands~Warrior~Minion~7~5~8~None~Bloodboil Brute~Rush"
	requireTarget, keyWord, description = False, "Rush", "Rush. Costs (1) less for each damaged minion"
	name_CN = "沸血蛮兵"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsHand = [Trig_BloodboilBrute(self)]
		
	def selfManaChange(self):
		if self.inHand:
			numDamagedMinion = 0
			for minion in self.Game.minionsonBoard(1) + self.Game.minionsonBoard(2):
				if minion.health < minion.health_max:
					numDamagedMinion += 1
			self.mana -= numDamagedMinion
			self.mana = max(0, self.mana)
			
class Trig_BloodboilBrute(TrigHand):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionAppears", "MinionDisappears", "MinionTakesDmg"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.inHand
		
	def text(self, CHN):
		return "每当受伤随从的数量变化，重新计算该随从的费用" if CHN \
				else "When number of damaged minions change, recalculate mana"
				
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.Game.Manas.calcMana_Single(self.entity)
		
		
		
		
Outlands_Indices = {"Outlands~Neutral~Minion~1~2~1~None~Ethereal Augmerchant~Battlecry": EtherealAugmerchant,
					"Outlands~Neutral~Minion~1~2~1~None~Guardian Augmerchant~Battlecry": GuardianAugmerchant,
					"Outlands~Neutral~Minion~1~1~2~None~Infectious Sporeling": InfectiousSporeling,
					"Outlands~Neutral~Minion~1~2~1~None~Rocket Augmerchant~Battlecry": RocketAugmerchant,
					"Outlands~Neutral~Minion~1~1~4~None~Soulbound Ashtongue": SoulboundAshtongue,
					"Outlands~Neutral~Minion~2~2~3~None~Bonechewer Brawler~Taunt": BonechewerBrawler,
					"Outlands~Neutral~Minion~2~3~5~Demon~Imprisoned Vilefiend~Rush": ImprisonedVilefiend,
					"Outlands~Neutral~Minion~2~2~4~Demon~Mo'arg Artificer": MoargArtificer,
					"Outlands~Neutral~Minion~2~2~2~None~Rustsworn Initiate~Deathrattle": RustswornInitiate,
					"Outlands~Neutral~Minion~1~1~1~Demon~Impcaster~Spell Damage~Uncollectible": Impcaster,
					"Outlands~Neutral~Minion~3~1~2~None~Blistering Rot": BlisteringRot,
					"Outlands~Neutral~Minion~1~1~1~None~Living Rot~Uncollectible": LivingRot,
					"Outlands~Neutral~Minion~3~4~3~None~Frozen Shadoweaver~Battlecry": FrozenShadoweaver,
					"Outlands~Neutral~Minion~3~1~6~None~Overconfident Orc~Taunt": OverconfidentOrc,
					"Outlands~Neutral~Minion~3~3~7~Demon~Terrorguard Escapee~Battlecry": TerrorguardEscapee,
					"Outlands~Neutral~Minion~1~1~1~None~Huntress~Uncollectible": Huntress,
					"Outlands~Neutral~Minion~3~3~4~None~Teron Gorefiend~Battlecry~Deathrattle~Legendary": TeronGorefiend,
					"Outlands~Neutral~Minion~4~5~2~Beast~Burrowing Scorpid~Battlecry": BurrowingScorpid,
					"Outlands~Neutral~Minion~4~3~3~Demon~Disguised Wanderer~Deathrattle": DisguisedWanderer,
					"Outlands~Neutral~Minion~4~9~1~Demon~Rustsworn Inquisitor~Uncollectible": RustswornInquisitor,
					"Outlands~Neutral~Minion~4~4~4~Murloc~Felfin Navigator~Battlecry": FelfinNavigator,
					"Outlands~Neutral~Minion~4~12~12~Demon~Magtheridon~Battlecry~Legendary": Magtheridon,
					"Outlands~Neutral~Minion~1~1~3~None~Hellfire Warder~Uncollectible": HellfireWarder,
					"Outlands~Neutral~Minion~4~4~3~None~Maiev Shadowsong~Battlecry~Legendary": MaievShadowsong,
					"Outlands~Neutral~Minion~4~3~3~Mech~Replicat-o-tron": Replicatotron,
					"Outlands~Neutral~Minion~4~3~3~None~Rustsworn Cultist~Battlecry": RustswornCultist,
					"Outlands~Neutral~Minion~1~1~1~Demon~Rusted Devil~Uncollectible": RustedDevil,
					"Outlands~Neutral~Minion~5~7~3~Elemental~Al'ar~Deathrattle~Legendary": Alar,
					"Outlands~Neutral~Minion~1~0~3~None~Ashes of Al'ar~Legendary~Uncollectible": AshesofAlar,
					"Outlands~Neutral~Minion~5~1~8~None~Ruststeed Raider~Taunt~Rush~Battlecry": RuststeedRaider,
					"Outlands~Neutral~Minion~5~3~3~None~Waste Warden~Battlecry": WasteWarden,
					"Outlands~Neutral~Minion~6~5~6~Dragon~Dragonmaw Sky Stalker~Deathrattle": DragonmawSkyStalker,
					"Outlands~Neutral~Minion~3~3~4~None~Dragonrider~Uncollectible": Dragonrider,
					"Outlands~Neutral~Minion~6~6~3~Demon~Scavenging Shivarra~Battlecry": ScavengingShivarra,
					"Outlands~Neutral~Minion~7~4~10~None~Bonechewer Vanguard~Taunt": BonechewerVanguard,
					"Outlands~Neutral~Minion~7~4~7~None~Kael'thas Sunstrider~Legendary": KaelthasSunstrider,
					"Outlands~Neutral~Minion~8~12~12~Demon~Supreme Abyssal": SupremeAbyssal,
					"Outlands~Neutral~Minion~10~7~7~Elemental~Scrapyard Colossus~Taunt~Deathrattle": ScrapyardColossus,
					"Outlands~Neutral~Minion~7~7~7~Elemental~Felcracked Colossus~Taunt~Uncollectible": FelcrackedColossus,
					"Outlands~Demon Hunter~Minion~1~1~1~None~Crimson Sigil Runner~Outcast": CrimsonSigilRunner,
					"Outlands~Demon Hunter~Minion~2~3~2~Murloc~Furious Felfin~Battlecry": FuriousFelfin,
					"Outlands~Demon Hunter~Spell~2~Immolation Aura": ImmolationAura,
					"Outlands~Demon Hunter~Minion~2~2~2~None~Netherwalker~Battlecry": Netherwalker,
					"Outlands~Demon Hunter~Spell~2~Spectral Sight~Outcast": SpectralSight,
					"Outlands~Demon Hunter~Minion~4~3~5~None~Ashtongue Battlelord~Taunt~Lifesteal": AshtongueBattlelord,
					"Outlands~Demon Hunter~Minion~6~8~3~None~Fel Summoner~Deathrattle": FelSummoner,
					"Outlands~Demon Hunter~Minion~4~3~4~None~Kayn Sunfury~Charge~Legendary": KaynSunfury,
					"Outlands~Demon Hunter~Spell~5~Metamorphosis~Legendary": Metamorphosis,
					"Outlands~Demon Hunter~Weapon~6~3~4~Warglaives of Azzinoth": WarglaivesofAzzinoth,
					"Outlands~Demon Hunter~Minion~6~10~6~Demon~Imprisoned Antaen": ImprisonedAntaen,
					"Outlands~Demon Hunter~Spell~6~Skull of Gul'dan~Outcast": SkullofGuldan,
					"Outlands~Demon Hunter~Minion~7~6~5~Demon~Priestess of Fury": PriestessofFury,
					"Outlands~Demon Hunter~Minion~8~9~5~None~Coilfang Warlord~Rush~Deathrattle": CoilfangWarlord,
					"Outlands~Demon Hunter~Minion~8~5~9~None~Conchguard Warlord~Taunt~Uncollectible": ConchguardWarlord,
					"Outlands~Demon Hunter~Minion~9~7~9~Demon~Pit Commander~Taunt": PitCommander,
					"Outlands~Druid~Spell~3~Fungal Fortunes": FungalFortunes,
					"Outlands~Druid~Spell~2~Ironbark": Ironbark,
					"Outlands~Druid~Minion~3~3~4~None~Archspore Msshi'fn~Taunt~Deathrattle~Legendary": ArchsporeMsshifn,
					"Outlands~Druid~Minion~10~9~9~None~Msshi'fn Prime~Taunt~Choose One~Legendary~Uncollectible": MsshifnPrime,
					"Outlands~Druid~Minion~10~9~9~None~Fungal Guardian~Taunt~Uncollectible": FungalGuardian,
					"Outlands~Druid~Minion~10~9~9~None~Fungal Bruiser~Rush~Uncollectible": FungalBruiser,
					"Outlands~Druid~Minion~10~9~9~None~Fungal Gargantuan~Taunt~Rush~Uncollectible": FungalGargantuan,
					"Outlands~Druid~Spell~3~Bogbeam": Bogbeam,
					"Outlands~Druid~Minion~3~3~3~Demon~Imprisoned Satyr": ImprisonedSatyr,
					"Outlands~Druid~Spell~4~Germination": Germination,
					"Outlands~Druid~Spell~4~Overgrowth": Overgrowth,
					"Outlands~Druid~Spell~5~Glowfly Swarm": GlowflySwarm,
					"Outlands~Druid~Minion~2~2~2~Beast~Glowfly~Uncollectible": Glowfly,
					"Outlands~Druid~Minion~7~7~7~Beast~Marsh Hydra~Rush": MarshHydra,
					"Outlands~Druid~Minion~9~5~5~None~Ysiel Windsinger~Legendary": YsielWindsinger,
					"Outlands~Hunter~Minion~1~2~1~Beast~Helboar~Deathrattle": Helboar,
					"Outlands~Hunter~Minion~2~5~4~Demon~Imprisoned Felmaw": ImprisonedFelmaw,
					"Outlands~Hunter~Spell~2~Pack Tactics~~Secret": PackTactics,
					"Outlands~Hunter~Spell~2~Scavenger's Ingenuity": ScavengersIngenuity,
					"Outlands~Hunter~Minion~3~2~4~Beast~Augmented Porcupine~Deathrattle": AugmentedPorcupine,
					"Outlands~Hunter~Minion~3~2~4~Beast~Zixor, Apex Predator~Rush~Deathrattle~Legendary": ZixorApexPredator,
					"Outlands~Hunter~Minion~8~4~4~Beast~Zixor Prime~Rush~Battlecry~Legendary~Uncollectible": ZixorPrime,
					"Outlands~Hunter~Minion~4~5~2~Beast~Mok'Nathal Lion~Rush~Battlecry": MokNathalLion,
					"Outlands~Hunter~Spell~4~Scrap Shot": ScrapShot,
					"Outlands~Hunter~Minion~8~5~5~None~Beastmaster Leoroxx~Battlecry~Legendary": BeastmasterLeoroxx,
					"Outlands~Hunter~Spell~10~Nagrand Slam": NagrandSlam,
					"Outlands~Hunter~Minion~4~3~5~Beast~Clefthoof~Uncollectible": Clefthoof,
					"Outlands~Mage~Spell~2~Evocation~Legendary": Evocation,
					"Outlands~Mage~Spell~1~Font of Power": FontofPower,
					"Outlands~Mage~Minion~2~2~3~None~Apexis Smuggler": ApexisSmuggler,
					"Outlands~Mage~Minion~2~3~2~None~Astromancer Solarian~Spell Damage~Deathrattle~Legendary": AstromancerSolarian,
					"Outlands~Mage~Minion~9~7~7~Demon~Solarian Prime~Spell Damage~Battlecry~Legendary~Uncollectible": SolarianPrime,
					"Outlands~Mage~Spell~2~Incanter's Flow": IncantersFlow,
					"Outlands~Mage~Minion~2~3~1~None~Starscryer~Deathrattle": Starscryer,
					"Outlands~Mage~Minion~3~4~5~Demon~Imprisoned Observer": ImprisonedObserver,
					"Outlands~Mage~Spell~3~Netherwind Portal~~Secret": NetherwindPortal,
					"Outlands~Mage~Spell~5~Apexis Blast": ApexisBlast,
					"Outlands~Mage~Spell~8~Deep Freeze": DeepFreeze,
					"Outlands~Paladin~Minion~1~2~1~Murloc~Imprisoned Sungill": ImprisonedSungill,
					"Outlands~Paladin~Minion~1~1~1~Murloc~Sungill Streamrunner~Uncollectible": SungillStreamrunner,
					"Outlands~Paladin~Minion~1~1~3~None~Aldor Attendant~Battlecry": AldorAttendant,
					"Outlands~Paladin~Spell~2~Hand of A'dal": HandofAdal,
					"Outlands~Paladin~Minion~2~2~1~Murloc~Murgur Murgurgle~Divine Shield~Deathrattle~Legendary": MurgurMurgurgle,
					"Outlands~Paladin~Minion~8~6~3~Murloc~Murgurgle Prime~Divine Shield~Battlecry~Legendary~Uncollectible": MurgurglePrime,
					"Outlands~Paladin~Spell~2~Libram of Wisdom": LibramofWisdom,
					"Outlands~Paladin~Weapon~3~3~2~Underlight Angling Rod": UnderlightAnglingRod,
					"Outlands~Paladin~Minion~5~4~6~None~Aldor Truthseeker~Battlecry": AldorTruthseeker,
					"Outlands~Paladin~Spell~5~Libram of Justice": LibramofJustice,
					"Outlands~Paladin~Weapon~1~1~4~Overdue Justice~Uncollectible": OverdueJustice,
					"Outlands~Paladin~Minion~7~4~6~None~Lady Liadrin~Battlecry~Legendary": LadyLiadrin,
					"Outlands~Paladin~Spell~9~Libram of Hope": LibramofHope,
					"Outlands~Paladin~Minion~8~8~8~None~Ancient Guardian~Taunt~Divine Shield~Uncollectible": AncientGuardian,
					"Outlands~Priest~Minion~1~2~5~Demon~Imprisoned Homunculus~Taunt": ImprisonedHomunculus,
					"Outlands~Priest~Minion~1~1~3~None~Reliquary of Souls~Lifesteal~Deathrattle~Legendary": ReliquaryofSouls,
					"Outlands~Priest~Minion~7~6~8~None~Reliquary Prime~Taunt~Lifesteal~Legendary~Uncollectible": ReliquaryPrime,
					"Outlands~Priest~Spell~1~Renew": Renew,
					"Outlands~Priest~Minion~2~1~4~None~Dragonmaw Sentinel~Battlecry": DragonmawSentinel,
					"Outlands~Priest~Minion~2~2~3~None~Sethekk Veilweaver": SethekkVeilweaver,
					"Outlands~Priest~Spell~3~Apotheosis": Apotheosis,
					"Outlands~Priest~Minion~3~2~2~None~Dragonmaw Overseer": DragonmawOverseer,
					"Outlands~Priest~Spell~5~Psyche Split": PsycheSplit,
					"Outlands~Priest~Minion~7~4~9~Dragon~Skeletal Dragon~Taunt": SkeletalDragon,
					"Outlands~Priest~Spell~7~Soul Mirror~Legendary": SoulMirror,
					"Outlands~Rogue~Minion~1~1~2~None~Blackjack Stunner~Battlecry": BlackjackStunner,
					"Outlands~Rogue~Minion~1~3~1~None~Spymistress~Stealth": Spymistress,
					"Outlands~Rogue~Spell~2~Ambush~~Secret": Ambush,
					"Outlands~Rogue~Minion~2~2~3~None~Broken Ambusher~Poisonous~Uncollectible": BrokenAmbusher,
					"Outlands~Rogue~Minion~2~3~2~None~Ashtongue Slayer~Battlecry": AshtongueSlayer,
					"Outlands~Rogue~Spell~2~Bamboozle~~Secret": Bamboozle,
					"Outlands~Rogue~Spell~2~Dirty Tricks~~Secret": DirtyTricks,
					"Outlands~Rogue~Minion~2~1~4~None~Shadowjeweler Hanar~Legendary": ShadowjewelerHanar,
					"Outlands~Rogue~Minion~3~3~4~None~Akama~Stealth~Deathrattle~Legendary": Akama,
					"Outlands~Rogue~Minion~6~6~5~None~Akama Prime~Stealth~Legendary~Uncollectible": AkamaPrime,
					"Outlands~Rogue~Minion~3~3~3~None~Greyheart Sage~Battlecry": GreyheartSage,
					"Outlands~Rogue~Minion~7~7~5~None~Cursed Vagrant~Deathrattle": CursedVagrant,
					"Outlands~Rogue~Minion~7~7~5~None~Cursed Shadow~Stealth~Uncollectible": CursedShadow,
					"Outlands~Shaman~Minion~3~3~3~None~Bogstrok Clacker~Battlecry": BogstrokClacker,
					"Outlands~Shaman~Minion~3~4~3~None~Lady Vashj~Spell Damage~Deathrattle~Legendary": LadyVashj,
					"Outlands~Shaman~Minion~7~5~4~None~Vashj Prime~Spell Damage~Battlecry~Legendary~Uncollectible": VashjPrime,
					"Outlands~Shaman~Minion~3~3~4~Elemental~Marshspawn~Battlecry": Marshspawn,
					"Outlands~Shaman~Spell~3~Serpentshrine Portal~Overload": SerpentshrinePortal,
					"Outlands~Shaman~Spell~3~Totemic Reflection": TotemicReflection,
					"Outlands~Shaman~Spell~4~Vivid Spores": VividSpores,
					"Outlands~Shaman~Weapon~5~3~2~Boggspine Knuckles": BoggspineKnuckles,
					"Outlands~Shaman~Minion~5~5~6~Elemental~Shattered Rumbler~Battlecry": ShatteredRumbler,
					"Outlands~Shaman~Spell~4~Torrent": Torrent,
					"Outlands~Shaman~Minion~6~6~5~Beast~The Lurker Below~Battlecry~Legendary": TheLurkerBelow,
					"Outlands~Warlock~Spell~1~Shadow Council": ShadowCouncil,
					"Outlands~Warlock~Spell~1~Unstable Felbolt": UnstableFelbolt,
					"Outlands~Warlock~Minion~2~3~3~Demon~Imprisoned Scrap Imp": ImprisonedScrapImp,
					"Outlands~Warlock~Minion~2~3~2~None~Kanrethad Ebonlocke~Deathrattle~Legendary": KanrethadEbonlocke,
					"Outlands~Warlock~Minion~8~7~6~Demon~Kanrethad Prime~Battlecry~Legendary~Uncollectible": KanrethadPrime,
					"Outlands~Warlock~Minion~2~2~3~Demon~Darkglare": Darkglare,
					"Outlands~Warlock~Minion~4~5~5~Demon~Nightshade Matron~Rush~Battlecry": NightshadeMatron,
					"Outlands~Warlock~Spell~4~The Dark Portal": TheDarkPortal,
					"Outlands~Warlock~Spell~6~Hand of Gul'dan": HandofGuldan,
					"Outlands~Warlock~Minion~6~3~3~None~Keli'dan the Breaker~Battlecry~Legendary": KelidantheBreaker,
					"Outlands~Warlock~Minion~8~5~7~Demon~Enhanced Dreadlord~Taunt~Deathrattle": EnhancedDreadlord,
					"Outlands~Warlock~Minion~5~5~5~Demon~Desperate Dreadlord~Lifesteal~Uncollectible": DesperateDreadlord,
					"Outlands~Warrior~Minion~1~2~2~Demon~Imprisoned Gan'arg": ImprisonedGanarg,
					"Outlands~Warrior~Spell~1~Sword and Board": SwordandBoard,
					"Outlands~Warrior~Spell~2~Corsair Cache": CorsairCache,
					"Outlands~Warrior~Spell~3~Bladestorm": Bladestorm,
					"Outlands~Warrior~Minion~3~3~3~None~Bonechewer Raider~Battlecry": BonechewerRaider,
					"Outlands~Warrior~Weapon~3~1~4~Bulwark of Azzinoth~Legendary": BulwarkofAzzinoth,
					"Outlands~Warrior~Minion~3~1~10~None~Warmaul Challenger~Battlecry": WarmaulChallenger,
					"Outlands~Warrior~Minion~4~4~4~None~Kargath Bladefist~Rush~Deathrattle~Legendary": KargathBladefist,
					"Outlands~Warrior~Minion~8~10~10~None~Kargath Prime~Rush~Legendary~Uncollectible": KargathPrime,
					"Outlands~Warrior~Minion~5~4~5~Mech~Scrap Golem~Taunt~Deathrattle": ScrapGolem,
					"Outlands~Warrior~Minion~7~5~8~None~Bloodboil Brute~Rush": BloodboilBrute,
					}