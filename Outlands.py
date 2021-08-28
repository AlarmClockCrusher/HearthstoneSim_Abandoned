from CardTypes import *
from Triggers_Auras import *
from numpy.random import choice as npchoice
from numpy.random import randint as nprandint
from numpy.random import shuffle as npshuffle
from numpy import inf as npinf

from AcrossPacks import ExcessMana, WaterElemental_Basic, FieryWarAxe_Basic

"""Ashes of Outlands"""
#休眠的随从在打出之后2回合本来时会触发你“召唤一张随从”
class Minion_Dormantfor2turns(Minion):
	Class, race, name = "Neutral", "", "Imprisoned Vanilla"
	mana, attack, health = 5, 5, 5
	index = "Vanilla~Neutral~Minion~5~5~5~~Imprisoned Vanilla"
	requireTarget, keyWord, description = False, "", "Dormant for 2 turns. When this awakens, do something"
	#出现即休眠的随从的played过程非常简单
	def played(self, target=None, choice=0, mana=0, posinHand=-2, comment=""):
		self.statReset(self.attack_Enchant, self.health_max)
		self.appears(firstTime=True) #打出时一定会休眠，同时会把Game.minionPlayed变为None
		return None #没有目标可以返回
		
	def appears(self, firstTime=True):
		self.onBoard = True
		self.inHand = self.inDeck = self.dead = False
		self.enterBoardTurn = self.Game.numTurn
		self.mana = type(self).mana #Restore the minion's mana to original value.
		self.decideAttChances_base() #Decide base att chances, given Windfury and Mega Windfury
		#没有光环，目前炉石没有给随从人为添加光环的效果, 不可能在把手牌中获得的扳机带入场上，因为会在变形中丢失
		#The buffAuras/hasAuras will react to this signal.
		if firstTime: #首次出场时会进行休眠，而且休眠状态会保持之前的随从buff
			self.Game.transform(self, ImprisonedDormantForm(self.Game, self.ID, self), firstTime=True)
		else: #只有不是第一次出现在场上时才会执行这些函数
			if self.btn:
				self.btn.isPlayed, self.btn.card = True, self
				self.btn.placeIcons()
				self.btn.statChangeAni()
				self.btn.statusChangeAni()
			for aura in self.auras.values(): aura.auraAppears()
			for trig in self.trigsBoard + self.deathrattles: trig.connect()
			self.Game.sendSignal("MinionAppears", self.ID, self, None, 0, comment=firstTime)
			
	def awakenEffect(self):
		pass
		
class ImprisonedDormantForm(Dormant):
	Class, school, name = "Neutral", "", "Imprisoned Vanilla"
	description = "Awakens after 2 turns"
	def __init__(self, Game, ID, minionInside=None):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_ImprisonedDormantForm(self)]
		self.minionInside = minionInside
		if minionInside: #When creating a copy, this is left blank temporarily
			self.Class = minionInside.Class
			self.name = "Dormant " + minionInside.name
			self.description = minionInside.description
			self.index = minionInside.index
			
	def assistCreateCopy(self, Copy):
		Copy.minionInside = self.minionInside.createCopy(Copy.Game)
		Copy.name, Copy.Class, Copy.description = self.name, self.Class, self.description
		
class Trig_ImprisonedDormantForm(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["TurnStarts"])
		self.counter = 2
		self.nextAniWait = True
				
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and ID == self.entity.ID #会在我方回合开始时进行苏醒
	
	def trig(self, signal, ID, subject, target, number, comment, choice=0):
		if self.canTrig(signal, ID, subject, target, number, comment):
			self.effect(signal, ID, subject, target, number, comment)
	
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.counter -= 1
		if self.entity.btn:
			icon, GUI = self.entity.btn.icons["Trigger"], self.entity.Game.GUI
			GUI.seqHolder[-1].append(GUI.PARALLEL(GUI.FUNC(icon.trigAni), GUI.WAIT(1.8),
												GUI.FUNC(icon.updateText)
												  )
									 )
			
		if self.counter < 1:
			#假设唤醒的Imprisoned Vanilla可以携带buff
			self.entity.Game.transform(self.entity, self.entity.minionInside, firstTime=False)
			if hasattr(self.entity.minionInside, "awakenEffect"):
				self.entity.minionInside.awakenEffect()
				
"""Mana 1 cards"""
class EtherealAugmerchant(Minion):
	Class, race, name = "Neutral", "", "Ethereal Augmerchant"
	mana, attack, health = 1, 2, 1
	index = "BLACK_TEMPLE~Neutral~Minion~1~2~1~~Ethereal Augmerchant~Battlecry"
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
			target.getsStatus("Spell Damage")
		return target
		
		
class GuardianAugmerchant(Minion):
	Class, race, name = "Neutral", "", "Guardian Augmerchant"
	mana, attack, health = 1, 2, 1
	index = "BLACK_TEMPLE~Neutral~Minion~1~2~1~~Guardian Augmerchant~Battlecry"
	requireTarget, keyWord, description = True, "", "Battlecry: Deal 1 damage to a minion and give it Divine Shield"
	name_CN = "防护改装师"
	def targetExists(self, choice=0):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target != self and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target and (target.onBoard or target.inHand):
			self.dealsDamage(target, 1)
			target.getsStatus("Divine Shield")
		return target
		
		
class InfectiousSporeling(Minion):
	Class, race, name = "Neutral", "", "Infectious Sporeling"
	mana, attack, health = 1, 1, 2
	index = "BLACK_TEMPLE~Neutral~Minion~1~1~2~~Infectious Sporeling"
	requireTarget, keyWord, description = False, "", "After this damages a minion, turn it into an Infectious Sporeling"
	name_CN = "传染孢子"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_InfectiousSporeling(self)]
		
class Trig_InfectiousSporeling(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["MinionTookDamage"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject == self.entity and target.onBoard and target.health > 0 and target.dead == False
		
	def text(self, CHN):
		return "在对随从造成伤害后，将其变为传染孢子" if CHN else "After this damages a minion, turn it into an Infectious Sporeling"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.transform(target, InfectiousSporeling(self.entity.Game, target.ID))
		
		
class RocketAugmerchant(Minion):
	Class, race, name = "Neutral", "", "Rocket Augmerchant"
	mana, attack, health = 1, 2, 1
	index = "BLACK_TEMPLE~Neutral~Minion~1~2~1~~Rocket Augmerchant~Battlecry"
	requireTarget, keyWord, description = True, "", "Battlecry: Deal 1 damage to a minion and give it Rush"
	name_CN = "火箭改装师"
	def targetExists(self, choice=0):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target != self and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target and (target.onBoard or target.inHand):
			self.dealsDamage(target, 1)
			target.getsStatus("Rush")
		return target
		
		
class SoulboundAshtongue(Minion):
	Class, race, name = "Neutral", "", "Soulbound Ashtongue"
	mana, attack, health = 1, 1, 4
	index = "BLACK_TEMPLE~Neutral~Minion~1~1~4~~Soulbound Ashtongue"
	requireTarget, keyWord, description = False, "", "Whenever this minion takes damage, also deal that amount to your hero"
	name_CN = "魂缚灰舌"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_SoulboundAshtongue(self)]
		
class Trig_SoulboundAshtongue(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["MinionTakesDmg"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return target == self.entity
		
	def text(self, CHN):
		return "每当该随从受到伤害时，对你的英雄造成等量的伤害" if CHN \
				else "Whenever this minion takes damage, also deal that amount to your hero"
				
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.dealsDamage(self.entity.Game.heroes[self.entity.ID], number)
		
		
"""Mana 2 cards"""
class BonechewerBrawler(Minion):
	Class, race, name = "Neutral", "", "Bonechewer Brawler"
	mana, attack, health = 2, 2, 3
	index = "BLACK_TEMPLE~Neutral~Minion~2~2~3~~Bonechewer Brawler~Taunt"
	requireTarget, keyWord, description = False, "Taunt", "Taunt. Whenever this minion takes damage, gain +2 Attack"
	name_CN = "噬骨殴斗者"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_BonechewerBrawler(self)]
		
class Trig_BonechewerBrawler(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["MinionTakesDmg"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return target == self.entity and self.entity.onBoard
		
	def text(self, CHN):
		return "每当该随从受到伤害，便获得+2攻击力" if CHN else "Whenever this minion takes damage, gain +2 Attack"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.buffDebuff(2, 0)
		
		
class ImprisonedVilefiend(Minion_Dormantfor2turns):
	Class, race, name = "Neutral", "Demon", "Imprisoned Vilefiend"
	mana, attack, health = 2, 3, 5
	index = "BLACK_TEMPLE~Neutral~Minion~2~3~5~Demon~Imprisoned Vilefiend~Rush"
	requireTarget, keyWord, description = False, "Rush", "Dormant for 2 turns. Rush"
	name_CN = "被禁锢的邪犬"
	
	
class MoargArtificer(Minion):
	Class, race, name = "Neutral", "Demon", "Mo'arg Artificer"
	mana, attack, health = 2, 2, 4
	index = "BLACK_TEMPLE~Neutral~Minion~2~2~4~Demon~Mo'arg Artificer"
	requireTarget, keyWord, description = False, "", "All minions take double damage from spells"
	name_CN = "莫尔葛工匠"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_MoargArtificer(self)]
		
class Trig_MoargArtificer(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["FinalDmgonMinion?"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and target.type == "Minion" and subject.type == "Spell" and number[0] > 0
		
	def text(self, CHN):
		return "所有随从受到的法术伤害翻倍" if CHN else "All minions take double damage from spells"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		number[0] += number[0]
		
		
class RustswornInitiate(Minion):
	Class, race, name = "Neutral", "", "Rustsworn Initiate"
	mana, attack, health = 2, 2, 2
	index = "BLACK_TEMPLE~Neutral~Minion~2~2~2~~Rustsworn Initiate~Deathrattle"
	requireTarget, keyWord, description = False, "", "Deathrattle: Summon a 1/1 Impcaster with Spell Damage +1"
	name_CN = "锈誓新兵"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.deathrattles = [SummonanImpcastwithSpellDamagePlus1(self)]
		
class SummonanImpcastwithSpellDamagePlus1(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.summon(Impcaster(self.entity.Game, self.entity.ID), self.entity.pos+1)
		
	def text(self, CHN):
		return "亡语：召唤一个1/1并具有法术伤害+1的小鬼施法者" if CHN else "Deathrattle: Summon a 1/1 Impcaster with Spell Damage +1"
		
class Impcaster(Minion):
	Class, race, name = "Neutral", "Demon", "Impcaster"
	mana, attack, health = 1, 1, 1
	index = "BLACK_TEMPLE~Neutral~Minion~1~1~1~Demon~Impcaster~Spell Damage~Uncollectible"
	requireTarget, keyWord, description = False, "Spell Damage", "Spell Damage +1"
	name_CN = "小鬼施法者"
	
"""Mana 3 cards"""
class BlisteringRot(Minion):
	Class, race, name = "Neutral", "", "Blistering Rot"
	mana, attack, health = 3, 1, 2
	index = "BLACK_TEMPLE~Neutral~Minion~3~1~2~~Blistering Rot"
	requireTarget, keyWord, description = False, "", "At the end of your turn, summon a Rot with stats equal to this minion's"
	name_CN = "起泡的腐泥怪"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_BlisteringRot(self)]
		
class Trig_BlisteringRot(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["TurnEnds"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and ID == self.entity.ID and self.entity.health > 0
	#假设召唤的Rot只是一个1/1，然后接受buff.而且该随从生命值低于1时不能触发
	#假设攻击力为负数时，召唤物的攻击力为0
	def text(self, CHN):
		return "在你的回合结束时，召唤一个属性值等同于该随从的腐质" if CHN \
				else "At the end of your turn, summon a Rot with stats equal to this minion's"
				
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		minion = LivingRot(self.entity.Game, self.entity.ID)
		if self.entity.summon(minion, self.entity.pos+1):
			minion.statReset(max(0, self.entity.attack), self.entity.health)
			
class LivingRot(Minion):
	Class, race, name = "Neutral", "", "Living Rot"
	mana, attack, health = 1, 1, 1
	index = "BLACK_TEMPLE~Neutral~Minion~1~1~1~~Living Rot~Uncollectible"
	requireTarget, keyWord, description = False, "", ""
	name_CN = "生命腐质"
	
	
class FrozenShadoweaver(Minion):
	Class, race, name = "Neutral", "", "Frozen Shadoweaver"
	mana, attack, health = 3, 4, 3
	index = "BLACK_TEMPLE~Neutral~Minion~3~4~3~~Frozen Shadoweaver~Battlecry"
	requireTarget, keyWord, description = True, "", "Battlecry: Freeze an enemy"
	name_CN = "冰霜织影者"
	def targetExists(self, choice=0):
		return self.selectableEnemyExists()
		
	def targetCorrect(self, target, choice=0):
		return (target.type == "Minion" or target.type == "Hero") and target.ID != self.ID and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			target.getsStatus("Frozen")
		return target
		
		
class OverconfidentOrc(Minion):
	Class, race, name = "Neutral", "", "Overconfident Orc"
	mana, attack, health = 3, 1, 6
	index = "BLACK_TEMPLE~Neutral~Minion~3~1~6~~Overconfident Orc~Taunt"
	requireTarget, keyWord, description = False, "Taunt", "Taunt. While at full Health, this has +2 Attack"
	name_CN = "狂傲的兽人"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.auras["While at full Health, this has +2 Attack"] = StatAura_OverconfidentOrc(self)
		
class StatAura_OverconfidentOrc(HasAura_toMinion):
	def __init__(self, entity):
		self.entity = entity
		self.on = False
		self.auraAffected = []
		
	#光环开启和关闭都取消，因为要依靠随从自己的handleEnrage来触发
	def auraAppears(self):
		minion = self.entity
		try: minion.Game.trigsBoard[minion.ID]["MinionStatCheck"].append(self)
		except: minion.Game.trigsBoard[minion.ID]["MinionStatCheck"] = [self]
		if minion.onBoard and minion.health == minion.health_max and not self.on:
			self.on = True
			Stat_Receiver(minion, self, 2, 0).effectStart()
			
	def auraDisappears(self):
		self.on = False
		try: self.entity.Game.trigsBoard[self.entity.ID]["MinionStatCheck"].append(self)
		except: pass
		for minion, receiver in self.auraAffected[:]:
			receiver.effectClear()
		self.auraAffected = []
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return target == self.entity and target.onBoard
		
	def trig(self, signal, ID, subject, target, number, comment, choice=0):
		if self.canTrig(signal, ID, subject, target, number, comment):
			self.effect(signal, ID, subject, target, number, comment)
			
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		minion = self.entity
		if minion.health == minion.health_max and not self.on:
			self.on = True
			Stat_Receiver(minion, self, 2, 0).effectStart()
		elif minion.health < minion.health_max and self.on:
			self.on = False
			for minion, receiver in self.auraAffected[:]:
				receiver.effectClear()
				
	def selfCopy(self, recipient): #The recipientMinion is the entity that deals the Aura.
		#func that checks if subject is applicable will be the new copy's function
		return type(self)(recipient)
	#激怒的光环仍然可以通过HasAura_toMinion的createCopy复制
	
	
class TerrorguardEscapee(Minion):
	Class, race, name = "Neutral", "Demon", "Terrorguard Escapee"
	mana, attack, health = 3, 3, 7
	index = "BLACK_TEMPLE~Neutral~Minion~3~3~7~Demon~Terrorguard Escapee~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Summon three 1/1 Huntresses for your opponent"
	name_CN = "逃脱的恐惧卫士"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.summon([Huntress(self.Game, 3-self.ID) for i in range(3)], (-1, "totheRightEnd"))
		return None
		
class Huntress(Minion):
	Class, race, name = "Neutral", "", "Huntress"
	mana, attack, health = 1, 1, 1
	index = "BLACK_TEMPLE~Neutral~Minion~1~1~1~~Huntress~Uncollectible"
	requireTarget, keyWord, description = False, "", ""
	name_CN = "女猎手"
	
	
class TeronGorefiend(Minion):
	Class, race, name = "Neutral", "", "Teron Gorefiend"
	mana, attack, health = 3, 3, 4
	index = "BLACK_TEMPLE~Neutral~Minion~3~3~4~~Teron Gorefiend~Battlecry~Deathrattle~Legendary"
	requireTarget, keyWord, description = False, "", "Battlecry: Destroy all friendly minions. Deathrattle: Resummon all of them with +1/+1"
	name_CN = "塔隆血魔"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
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
		super().__init__(entity)
		self.minionsDestroyed = []
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		if self.minionsDestroyed != []:
			pos = (self.entity.pos, "totheRight") if self.entity in self.entity.Game.minions[self.entity.ID] else (-1, "totheRightEnd")
			minions = [minion(self.entity.Game, self.entity.ID) for minion in self.minionsDestroyed]
			#假设给予+1/+1是在召唤之前
			for minion in minions: minion.buffDebuff(1, 1)
			self.entity.summon(minions, pos)
			
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
	index = "BLACK_TEMPLE~Neutral~Minion~4~5~2~Beast~Burrowing Scorpid~Battlecry"
	requireTarget, keyWord, description = True, "", "Battlecry: Deal 2 damage. If that kills the target, gain Stealth"
	name_CN = "潜地蝎"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			self.dealsDamage(target, 2)
			if target.health < 1 or target.dead == True:
				self.getsStatus("Stealth")
		return target
		
		
class DisguisedWanderer(Minion):
	Class, race, name = "Neutral", "Demon", "Disguised Wanderer"
	mana, attack, health = 4, 3, 3
	index = "BLACK_TEMPLE~Neutral~Minion~4~3~3~Demon~Disguised Wanderer~Deathrattle"
	requireTarget, keyWord, description = False, "", "Deathrattle: Summon a 9/1 Inquisitor"
	name_CN = "变装游荡者"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.deathrattles = [SummonanInquisitor(self)]
		
class SummonanInquisitor(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.summon(RustswornInquisitor(self.entity.Game, self.entity.ID), self.entity.pos+1)
		
	def text(self, CHN):
		return "亡语：召唤一个9/1的审判官" if CHN else "Deathrattle: Summon a 9/1 Inquisitor"
		
class RustswornInquisitor(Minion):
	Class, race, name = "Neutral", "Demon", "Rustsworn Inquisitor"
	mana, attack, health = 4, 9, 1
	index = "BLACK_TEMPLE~Neutral~Minion~4~9~1~Demon~Rustsworn Inquisitor~Uncollectible"
	requireTarget, keyWord, description = False, "", ""
	name_CN = "锈誓审判官"
	
	
class FelfinNavigator(Minion):
	Class, race, name = "Neutral", "Murloc", "Felfin Navigator"
	mana, attack, health = 4, 4, 4
	index = "BLACK_TEMPLE~Neutral~Minion~4~4~4~Murloc~Felfin Navigator~Battlecry"
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
	index = "BLACK_TEMPLE~Neutral~Minion~4~12~12~Demon~Magtheridon~Battlecry~Legendary"
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
		self.onBoard = True
		self.inHand = self.inDeck = self.dead = False
		self.enterBoardTurn = self.Game.numTurn
		self.mana = type(self).mana #Restore the minion's mana to original value.
		self.decideAttChances_base() #Decide base att chances, given Windfury and Mega Windfury
		if firstTime: #首次出场时会进行休眠，而且休眠状态会保持之前的随从buff。休眠体由每个不同的随从自己定义
			self.Game.transform(self, Magtheridon_Dormant(self.Game, self.ID, self), firstTime=True)
		else: #只有不是第一次出现在场上时才会执行这些函数
			if self.btn:
				self.btn.isPlayed, self.btn.card = True, self
				self.btn.placeIcons()
				self.btn.statChangeAni()
				self.btn.statusChangeAni()
			for trig in self.trigsBoard + self.deathrattles:
				trig.connect() #把(obj, signal)放入Game.trigsBoard中
			self.Game.sendSignal("MinionAppears", self.ID, self, None, 0, comment=firstTime)
			
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.summon([HellfireWarder(self.Game, 3-self.ID) for i in range(3)], (-1, "totheRightEnd"))
		return None
		
class Magtheridon_Dormant(Dormant):
	Class, school, name = "Neutral", "", "Dormant Magtheridon"
	description = "Destroy 3 Warders to destroy all minions and awaken this"
	def __init__(self, Game, ID, minionInside=None):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_Magtheridon_Dormant(self)]
		self.minionInside = minionInside
		
	def assistCreateCopy(self, Copy):
		Copy.minionInside = self.minionInside.createCopy(Copy.Game)
		Copy.name, Copy.Class, Copy.description = self.name, self.Class, self.description
		
class Trig_Magtheridon_Dormant(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["MinionDies"]) #假设是死亡时扳机，而还是死亡后扳机
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
			game.transform(self.entity, self.entity.minionInside, firstTime=False)
			
class HellfireWarder(Minion):
	Class, race, name = "Neutral", "", "Hellfire Warder"
	mana, attack, health = 1, 1, 3
	index = "BLACK_TEMPLE~Neutral~Minion~1~1~3~~Hellfire Warder~Uncollectible"
	requireTarget, keyWord, description = False, "", "(Magtheridon will destroy all minions and awaken after 3 Warders die)"
	name_CN = "地狱火典狱官"
	
	
class MaievShadowsong(Minion):
	Class, race, name = "Neutral", "", "Maiev Shadowsong"
	mana, attack, health = 4, 4, 3
	index = "BLACK_TEMPLE~Neutral~Minion~4~4~3~~Maiev Shadowsong~Battlecry~Legendary"
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
	index = "BLACK_TEMPLE~Neutral~Minion~4~3~3~Mech~Replicat-o-tron"
	requireTarget, keyWord, description = False, "", "At the end of your turn, transform a neighbor into a copy of this"
	name_CN = "复制机器人"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_Replicatotron(self)]
		
class Trig_Replicatotron(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["TurnEnds"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and ID == self.entity.ID
		
	def text(self, CHN):
		return "在你的回合结时，将一个相邻的随从变形成为该随从的复制" if CHN else "At the end of your turn, transform a neighbor into a copy of this"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		neighbors = self.entity.Game.neighbors2(self.entity)[0]
		if neighbors: self.entity.transform(npchoice(neighbors), self.entity.selfCopy(self.entity.ID, self.entity))
		
		
class RustswornCultist(Minion):
	Class, race, name = "Neutral", "", "Rustsworn Cultist"
	mana, attack, health = 4, 3, 3
	index = "BLACK_TEMPLE~Neutral~Minion~4~3~3~~Rustsworn Cultist~Battlecry"
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
		self.entity.summon(RustedDevil(self.entity.Game, self.entity.ID), self.entity.pos+1)
		
class RustedDevil(Minion):
	Class, race, name = "Neutral", "Demon", "Rusted Devil"
	mana, attack, health = 1, 1, 1
	index = "BLACK_TEMPLE~Neutral~Minion~1~1~1~Demon~Rusted Devil~Uncollectible"
	requireTarget, keyWord, description = False, "", ""
	name_CN = "铁锈恶鬼"
	
	
"""Mana 5 cards"""
class Alar(Minion):
	Class, race, name = "Neutral", "Elemental", "Al'ar"
	mana, attack, health = 5, 7, 3
	index = "BLACK_TEMPLE~Neutral~Minion~5~7~3~Elemental~Al'ar~Deathrattle~Legendary"
	requireTarget, keyWord, description = False, "", "Deathrattle: Summon a 0/3 Ashes of Al'ar that resurrects this minion on your next turn"
	name_CN = "奥"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.deathrattles = [SummonAshesofAlar(self)]
		
class SummonAshesofAlar(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.summon(AshesofAlar(self.entity.Game, self.entity.ID), self.entity.pos+1)
		
	def text(self, CHN):
		return "亡语：召唤一个0/3的可以在你的下个回合复活该随从的“奥的灰烬”" if CHN \
				else "Deathrattle: Summon a 0/3 Ashes of Al'ar that resurrects this minion on your next turn"
				
class AshesofAlar(Minion):
	Class, race, name = "Neutral", "", "Ashes of Al'ar"
	mana, attack, health = 1, 0, 3
	index = "BLACK_TEMPLE~Neutral~Minion~1~0~3~~Ashes of Al'ar~Legendary~Uncollectible"
	requireTarget, keyWord, description = False, "", "At the start of your turn, transform this into Al'ar"
	name_CN = "奥的灰烬”"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_AshesofAlar(self)]
		
class Trig_AshesofAlar(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["TurnStarts"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and ID == self.entity.ID
		
	def text(self, CHN):
		return "在你的回合开始时，该随从变形成为奥" if CHN else "At the start of your turn, transform this into Al'ar"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.transform(self.entity, Alar(self.entity.Game, self.entity.ID))
		
		
class RuststeedRaider(Minion):
	Class, race, name = "Neutral", "", "Ruststeed Raider"
	mana, attack, health = 5, 1, 8
	index = "BLACK_TEMPLE~Neutral~Minion~5~1~8~~Ruststeed Raider~Taunt~Rush~Battlecry"
	requireTarget, keyWord, description = False, "Taunt,Rush", "Taunt, Rush. Battlecry: Gain +4 Attack this turn"
	name_CN = "锈骑劫匪"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.buffDebuff(4, 0, "EndofTurn")
		return None
		
		
class WasteWarden(Minion):
	Class, race, name = "Neutral", "", "Waste Warden"
	mana, attack, health = 5, 3, 3
	index = "BLACK_TEMPLE~Neutral~Minion~5~3~3~~Waste Warden~Battlecry"
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
	index = "BLACK_TEMPLE~Neutral~Minion~6~5~6~Dragon~Dragonmaw Sky Stalker~Deathrattle"
	requireTarget, keyWord, description = False, "", "Deathrattle: Summon a 3/4 Dragonrider"
	name_CN = "龙喉巡天者"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.deathrattles = [SummonaDragonrider(self)]
		
class SummonaDragonrider(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.summon(Dragonrider(self.entity.Game, self.entity.ID), self.entity.pos+1)
		
	def text(self, CHN):
		return "亡语：召唤一个3/4的龙骑士" if CHN else "Deathrattle: Summon a 3/4 Dragonrider"
		
class Dragonrider(Minion):
	Class, race, name = "Neutral", "", "Dragonrider"
	mana, attack, health = 3, 3, 4
	index = "BLACK_TEMPLE~Neutral~Minion~3~3~4~~Dragonrider~Uncollectible"
	requireTarget, keyWord, description = False, "", ""
	name_CN = "龙骑士"
	
	
class KaelthasSunstrider(Minion):
	Class, race, name = "Neutral", "", "Kael'thas Sunstrider"
	mana, attack, health = 7, 4, 7
	index = "BLACK_TEMPLE~Neutral~Minion~7~4~7~~Kael'thas Sunstrider~Legendary"
	requireTarget, keyWord, description = False, "", "Every third spell you cast each turn costs (1)"
	name_CN = "凯尔萨斯·逐日者"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
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
	index = "BLACK_TEMPLE~Neutral~Minion~6~6~3~Demon~Scavenging Shivarra~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Deal 6 damage randomly split among all other minions"
	name_CN = "食腐破坏魔"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		for i in range(6):
			minions = self.Game.minionsAlive(1, exclude=self) + self.Game.minionsAlive(2, exclude=self)
			if minions: self.dealsDamage(npchoice(minions), 1)
			else: break
		return None
		
		
class BonechewerVanguard(Minion):
	Class, race, name = "Neutral", "", "Bonechewer Vanguard"
	mana, attack, health = 7, 4, 10
	index = "BLACK_TEMPLE~Neutral~Minion~7~4~10~~Bonechewer Vanguard~Taunt"
	requireTarget, keyWord, description = False, "Taunt", "Taunt. Whenever this minion takes damage, gain +2 Attack"
	name_CN = "噬骨先锋"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_BonechewerVanguard(self)]
		
class Trig_BonechewerVanguard(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["MinionTakesDmg"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return target == self.entity and self.entity.onBoard
		
	def text(self, CHN):
		return "每当该随从受到伤害，便获得+2攻击力" if CHN else "Whenever this minion takes damage, gain +2 Attack"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.buffDebuff(2, 0)
		
		
class SupremeAbyssal(Minion):
	Class, race, name = "Neutral", "Demon", "Supreme Abyssal"
	mana, attack, health = 8, 12, 12
	index = "BLACK_TEMPLE~Neutral~Minion~8~12~12~Demon~Supreme Abyssal"
	requireTarget, keyWord, description = False, "", "Can't attack heroes"
	name_CN = "深渊至尊"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.marks["Can't Attack Hero"] = 1
		
		
class ScrapyardColossus(Minion):
	Class, race, name = "Neutral", "Elemental", "Scrapyard Colossus"
	mana, attack, health = 10, 7, 7
	index = "BLACK_TEMPLE~Neutral~Minion~10~7~7~Elemental~Scrapyard Colossus~Taunt~Deathrattle"
	requireTarget, keyWord, description = False, "Taunt", "Taunt. Deathrattle: Summon a 7/7 Felcracked Colossus with Taunt"
	name_CN = "废料场巨像"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.deathrattles = [SummonaColossuswithTaunt(self)]
		
class SummonaColossuswithTaunt(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.summon(FelcrackedColossus(self.entity.Game, self.entity.ID), self.entity.pos+1)
		
	def text(self, CHN):
		return "亡语：召唤一个7/7并具有嘲讽的邪爆巨像" if CHN else "Deathrattle: Summon a 7/7 Felcracked Colossus with Taunt"
		
class FelcrackedColossus(Minion):
	Class, race, name = "Neutral", "Elemental", "Felcracked Colossus"
	mana, attack, health = 7, 7, 7
	index = "BLACK_TEMPLE~Neutral~Minion~7~7~7~Elemental~Felcracked Colossus~Taunt~Uncollectible"
	requireTarget, keyWord, description = False, "Taunt", "Taunt"
	name_CN = "邪爆巨像"
	
"""Demon Hunter cards"""
class FuriousFelfin(Minion):
	Class, race, name = "Demon Hunter", "Murloc", "Furious Felfin"
	mana, attack, health = 2, 3, 2
	index = "BLACK_TEMPLE~Demon Hunter~Minion~2~3~2~Murloc~Furious Felfin~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: If your hero attacked this turn, gain +1 Attack and Rush"
	name_CN = "暴怒的邪鳍"
	
	def effCanTrig(self):
		self.effectViable = self.Game.Counters.heroAttackTimesThisTurn[self.ID] > 0
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if self.Game.Counters.heroAttackTimesThisTurn[self.ID] > 0:
			self.buffDebuff(1, 0)
			self.getsStatus("Rush")
		return None
		
		
class ImmolationAura(Spell):
	Class, school, name = "Demon Hunter", "Fel", "Immolation Aura"
	requireTarget, mana = False, 2
	index = "BLACK_TEMPLE~Demon Hunter~Spell~2~Fel~Immolation Aura"
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
	index = "BLACK_TEMPLE~Demon Hunter~Minion~2~2~2~~Netherwalker~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Discover a Demon"
	name_CN = "虚无行者"
	poolIdentifier = "Demons as Demon Hunter"
	@classmethod
	def generatePool(cls, pools):
		classCards = {s : [] for s in pools.ClassesandNeutral}
		for card in pools.MinionswithRace["Demon"]:
			for Class in card.Class.split(','):
				classCards[Class].append(card)
		return ["Demons as "+Class for Class in pools.Classes], \
				[classCards[Class]+classCards["Neutral"] for Class in pools.Classes]
				
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.discoverandGenerate(Netherwalker, comment, lambda : self.rngPool("Demons as " + classforDiscover(self)))
		return None
		
	
class FelSummoner(Minion):
	Class, race, name = "Demon Hunter", "", "Fel Summoner"
	mana, attack, health = 6, 8, 3
	index = "BLACK_TEMPLE~Demon Hunter~Minion~6~8~3~~Fel Summoner~Deathrattle"
	requireTarget, keyWord, description = False, "", "Deathrattle: Summon a random Demon from your hand"
	name_CN = "邪能召唤师"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.deathrattles = [SummonaRandomDemonfromYourHand(self)]
		
class SummonaRandomDemonfromYourHand(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		minion = self.entity
		demons = [i for i, card in enumerate(minion.Game.Hand_Deck.hands[minion.ID]) \
				  if card.type == "Minion" and "Demon" in card.race]
		if demons and minion.Game.space(minion.ID) > 0: minion.Game.summonfrom(npchoice(demons), minion.ID, minion.pos+1, minion, source='H')
		
	def text(self, CHN):
		return "亡语：随机从你的手牌中召唤一个恶魔" if CHN else "Deathrattle: Summon a random Demon from your hand"
		
		
class KaynSunfury(Minion):
	Class, race, name = "Demon Hunter", "", "Kayn Sunfury"
	mana, attack, health = 4, 3, 4
	index = "BLACK_TEMPLE~Demon Hunter~Minion~4~3~4~~Kayn Sunfury~Charge~Legendary"
	requireTarget, keyWord, description = False, "Charge", "Charge. All friendly attacks ignore Taunt"
	name_CN = "凯恩日怒"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.auras["All friendly attacks ignore Taunt"] = GameRuleAura_KaynSunfury(self)
		
class GameRuleAura_KaynSunfury(GameRuleAura):
	def auraAppears(self):
		self.entity.Game.status[self.entity.ID]["Ignore Taunt"] += 1
		
	def auraDisappears(self):
		self.entity.Game.status[self.entity.ID]["Ignore Taunt"] -= 1
		
		
class Metamorphosis(Spell):
	Class, school, name = "Demon Hunter", "Fel", "Metamorphosis"
	requireTarget, mana = False, 5
	index = "BLACK_TEMPLE~Demon Hunter~Spell~5~Fel~Metamorphosis~Legendary"
	description = "Swap your Hero Power to 'Deal 4 damage'. After 2 uses, swap it back"
	name_CN = "恶魔变形"
	#不知道是否只是对使用两次英雄技能计数，而不一定要是那个特定的英雄技能
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		power = DemonicBlast(self.Game, self.ID)
		power.powerReplaced = self.Game.powers[self.ID]
		power.replaceHeroPower()
		return None
		
class DemonicBlast(Power):
	mana, name, requireTarget = 1, "Demonic Blast", True
	index = "Demon Hunter~Hero Power~1~Demonic Blast"
	description = "Deal 4 damage. (Two uses left!)"
	name_CN = "恶魔冲击"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_DemonicBlast(self)]
		self.powerReplaced = None
		
	def text(self, CHN):
		damage = (4 + self.marks["Damage Boost"] + self.Game.status[self.ID]["Power Damage"]) * (2 ** self.countDamageDouble())
		return "造成%d点伤害。（还可使用两次！） 替换的原技能是%s"%(damage, self.powerReplaced.name) if CHN \
				else "Deal %d damage. (Two uses left!) Original Hero Power is %s"%(damage, self.powerReplaced.name)
				
	def effect(self, target, choice=0):
		damage = (4 + self.Game.status[self.ID]["Power Damage"]) * (2 ** self.countDamageDouble())
		dmgTaker, damageActual = self.dealsDamage(target, damage)
		if dmgTaker.health < 1 or dmgTaker.dead: return 1
		return 0
		
class Trig_DemonicBlast(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["HeroUsedAbility"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject == self.entity
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		power = DemonicBlast1(self.entity.Game, self.entity.ID)
		power.powerReplaced = self.entity.powerReplaced
		power.replaceHeroPower()
		
class DemonicBlast1(Power):
	mana, name, requireTarget = 1, "Demonic Blast", True
	index = "Demon Hunter~Hero Power~1~Demonic Blast"
	description = "Deal 4 damage. (Last use!)"
	name_CN = "恶魔冲击"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_DemonicBlast1(self)]
		self.powerReplaced = None
		
	def text(self, CHN):
		damage = (4 + self.marks["Damage Boost"] + self.Game.status[self.ID]["Power Damage"]) * (2 ** self.countDamageDouble())
		return "造成%d点伤害。（还可使用一次！） 替换的原技能是%s"%(damage, self.powerReplaced.name) if CHN \
				else "Deal %d damage. (Last use!) Original Hero Power is %s"%(damage, self.powerReplaced.name)
				
	def effect(self, target, choice=0):
		damage = (4 + self.Game.status[self.ID]["Power Damage"]) * (2 ** self.countDamageDouble())
		dmgTaker, damageActual = self.dealsDamage(target, damage)
		if dmgTaker.health < 1 or dmgTaker.dead: return 1
		return 0
		
class Trig_DemonicBlast1(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["HeroUsedAbility"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject == self.entity
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		power = self.entity.powerReplaced
		power.ID = self.entity.ID
		power.replaceHeroPower()
		
		
class ImprisonedAntaen(Minion_Dormantfor2turns):
	Class, race, name = "Demon Hunter", "Demon", "Imprisoned Antaen"
	mana, attack, health = 6, 10, 6
	index = "BLACK_TEMPLE~Demon Hunter~Minion~6~10~6~Demon~Imprisoned Antaen"
	requireTarget, keyWord, description = False, "", "Dormant for 2 turns. When this awakens, deal 10 damage randomly split among all enemies"
	name_CN = "被禁锢的安塔恩"
	
	def awakenEffect(self):
		for num in range(10):
			objs = self.Game.charsAlive(3-self.ID)
			if objs: self.dealsDamage(npchoice(objs), 1)
			else: break
				
				
class SkullofGuldan(Spell):
	Class, school, name = "Demon Hunter", "", "Skull of Gul'dan"
	requireTarget, mana = False, 6
	index = "BLACK_TEMPLE~Demon Hunter~Spell~6~~Skull of Gul'dan~Outcast"
	description = "Draw 3 cards. Outscast: Reduce their Cost by (3)"
	name_CN = "古尔丹之颅"
	def effCanTrig(self):
		self.effectViable = self.Game.Hand_Deck.outcastcanTrig(self)
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		outcastcanTrig = posinHand == 0 or posinHand == -1
		for i in range(3):
			card, mana = self.Game.Hand_Deck.drawCard(self.ID)
			if outcastcanTrig and card:
				ManaMod(card, changeby=-3, changeto=-1).applies()
		return None
		
		
		

class PriestessofFury(Minion):
	Class, race, name = "Demon Hunter", "Demon", "Priestess of Fury"
	mana, attack, health = 7, 6, 5
	index = "BLACK_TEMPLE~Demon Hunter~Minion~7~6~5~Demon~Priestess of Fury"
	requireTarget, keyWord, description = False, "", "At the end of your turn, deal 6 damage randomly split among all enemies"
	name_CN = "愤怒的女祭司"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_PriestessofFury(self)]
		
class Trig_PriestessofFury(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["TurnEnds"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and ID == self.entity.ID
		
	def text(self, CHN):
		return "在你的回合结束时，造成6点伤害，随机分配到所有敌人身上" if CHN else "At the end of your turn, deal 6 damage randomly split among all enemies"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		minion = self.entity
		for num in range(6):
			objs = minion.Game.charsAlive(3-minion.ID)
			if objs: minion.dealsDamage(npchoice(objs, 1))
			else: break
				
				
class CoilfangWarlord(Minion):
	Class, race, name = "Demon Hunter", "", "Coilfang Warlord"
	mana, attack, health = 8, 9, 5
	index = "BLACK_TEMPLE~Demon Hunter~Minion~8~9~5~~Coilfang Warlord~Rush~Deathrattle"
	requireTarget, keyWord, description = False, "Rush", "Rush. Deathrattle: Summon a 5/9 Warlord with Taunt"
	name_CN = "盘牙督军"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.deathrattles = [SummonaWarlordwithTaunt(self)]
		
class SummonaWarlordwithTaunt(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.summon(ConchguardWarlord(self.entity.Game, self.entity.ID), self.entity.pos+1)
		
	def text(self, CHN):
		return "亡语：召唤一个5/9并具有嘲讽的督军" if CHN else "Deathrattle: Summon a 5/9 Warlord with Taunt"
		
class ConchguardWarlord(Minion):
	Class, race, name = "Demon Hunter", "", "Conchguard Warlord"
	mana, attack, health = 8, 5, 9
	index = "BLACK_TEMPLE~Demon Hunter~Minion~8~5~9~~Conchguard Warlord~Taunt~Uncollectible"
	requireTarget, keyWord, description = False, "Taunt", "Taunt"
	name_CN = "螺盾督军"
	
	
class PitCommander(Minion):
	Class, race, name = "Demon Hunter", "Demon", "Pit Commander"
	mana, attack, health = 9, 7, 9
	index = "BLACK_TEMPLE~Demon Hunter~Minion~9~7~9~Demon~Pit Commander~Taunt"
	requireTarget, keyWord, description = False, "Taunt", "Taunt. At the end of your turn, summon a Demon from your deck"
	name_CN = "深渊指挥官"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_PitCommander(self)]
		
class Trig_PitCommander(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["TurnEnds"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and ID == self.entity.ID
		
	def text(self, CHN):
		return "在你的回合结束时，从你的牌库中召唤一个恶魔" if CHN else "At the end of your turn, summon a Demon from your deck"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		minion = self.entity
		demons = [i for i, card in enumerate(minion.Game.Hand_Deck.decks[minion.ID]) if card.type == "Minion" and "Demon" in card.race]
		if demons and minion.Game.space(minion.ID):
			minion.Game.summonfrom(npchoice(demons), minion.ID, minion.pos+1, minion, source='D')
			
			
"""Druid cards"""
class FungalFortunes(Spell):
	Class, school, name = "Druid", "Nature", "Fungal Fortunes"
	requireTarget, mana = False, 3
	index = "BLACK_TEMPLE~Druid~Spell~3~Nature~Fungal Fortunes"
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
				self.Game.Hand_Deck.discard(self.ID, card)
		return None
		
		
class Ironbark(Spell):
	Class, school, name = "Druid", "Nature", "Ironbark"
	requireTarget, mana = True, 2
	index = "BLACK_TEMPLE~Druid~Spell~2~Nature~Ironbark"
	description = "Give a minion +1/+3 and Taunt. Costs (0) if you have at least 7 Mana Crystals"
	name_CN = "铁木树皮"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
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
			target.getsStatus("Taunt")
		return target
		
class Trig_Ironbark(TrigHand):
	def __init__(self, entity):
		super().__init__(entity, ["ManaXtlsCheck"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.inHand and ID == self.entity.ID
		
	def text(self, CHN):
		return "每当玩家的法力水晶上限变化，便得重新计算法力值消耗" if CHN else "Whenever player's Mana Crystals change, recalculate the cost"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.Game.Manas.calcMana_Single(self.entity)
		
		
class ArchsporeMsshifn(Minion):
	Class, race, name = "Druid", "", "Archspore Msshi'fn"
	mana, attack, health = 3, 3, 4
	index = "BLACK_TEMPLE~Druid~Minion~3~3~4~~Archspore Msshi'fn~Taunt~Deathrattle~Legendary"
	requireTarget, keyWord, description = False, "Taunt", "Taunt. Deathrattle: Shuffle 'Msshi'fn Prime' into your deck"
	name_CN = "孢子首领姆希菲"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.deathrattles = [ShuffleMsshifnPrimeintoYourDeck(self)]
		
class ShuffleMsshifnPrimeintoYourDeck(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		minion = self.entity
		minion.Game.Hand_Deck.shuffleintoDeck(MsshifnPrime(minion.Game, minion.ID), creator=minion)
		
	def text(self, CHN):
		return "亡语：将“终极姆希菲”洗入你的牌库" if CHN else "Deathrattle: Shuffle 'Msshi'fn Prime' into your deck"
		
class MsshifnPrime(Minion):
	Class, race, name = "Druid", "", "Msshi'fn Prime"
	mana, attack, health = 10, 9, 9
	index = "BLACK_TEMPLE~Druid~Minion~10~9~9~~Msshi'fn Prime~Taunt~Choose One~Legendary~Uncollectible"
	requireTarget, keyWord, description = False, "Taunt", "Taunt. Choose One- Summon a 9/9 Fungal Giant with Taunt; or Rush"
	name_CN = "终极姆希菲"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		# 0: Give other minion +2/+2; 1:Summon two Treants with Taunt.
		self.options = [MsshifnAttac_Option(self), MsshifnProtec_Option(self)]
		
	def need2Choose(self):
		return True
		
	#如果有全选光环，只有一个9/9，其同时拥有突袭和嘲讽
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if choice == 0:
			self.summon(FungalGuardian(self.Game, self.ID), self.pos+1)
		elif choice == 1:
			self.summon(FungalBruiser(self.Game, self.ID), self.pos+1)
		elif choice < 0:
			self.summon(FungalGargantuan(self.Game, self.ID), self.pos+1)
		return None
		
class FungalGuardian(Minion):
	Class, race, name = "Druid", "", "Fungal Guardian"
	mana, attack, health = 10, 9, 9
	index = "BLACK_TEMPLE~Druid~Minion~10~9~9~~Fungal Guardian~Taunt~Uncollectible"
	requireTarget, keyWord, description = False, "Taunt", "Taunt"
	
class FungalBruiser(Minion):
	Class, race, name = "Druid", "", "Fungal Bruiser"
	mana, attack, health = 10, 9, 9
	index = "BLACK_TEMPLE~Druid~Minion~10~9~9~~Fungal Bruiser~Rush~Uncollectible"
	requireTarget, keyWord, description = False, "Rush", "Rush"
	
class FungalGargantuan(Minion):
	Class, race, name = "Druid", "", "Fungal Gargantuan"
	mana, attack, health = 10, 9, 9
	index = "BLACK_TEMPLE~Druid~Minion~10~9~9~~Fungal Gargantuan~Taunt~Rush~Uncollectible"
	requireTarget, keyWord, description = False, "Taunt,Rush", "Taunt, Rush"
	
class MsshifnAttac_Option(Option):
	name, description = "Msshi'fn At'tac", "Summon a 9/9 with Taunt"
	mana, attack, health = 10, -1, -1
	isLegendary = True
	def available(self):
		return self.entity.Game.space(self.entity.ID) > 0
		
class MsshifnProtec_Option(Option):
	name, description = "Msshi'fn Pro'tec", "Summon a 9/9 with Rush"
	mana, attack, health = 10, -1, -1
	isLegendary = True
	def available(self):
		return self.entity.Game.space(self.entity.ID) > 0
		
		
class Bogbeam(Spell):
	Class, school, name = "Druid", "", "Bogbeam"
	requireTarget, mana = True, 3
	index = "BLACK_TEMPLE~Druid~Spell~3~~Bogbeam"
	description = "Deal 3 damage to a minion. Costs (0) if you have at least 7 Mana Crystals"
	name_CN = "沼泽射线"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
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
		super().__init__(entity, ["ManaXtlsCheck"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.inHand and ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.Game.Manas.calcMana_Single(self.entity)
		
		
class ImprisonedSatyr(Minion_Dormantfor2turns):
	Class, race, name = "Druid", "Demon", "Imprisoned Satyr"
	mana, attack, health = 3, 3, 3
	index = "BLACK_TEMPLE~Druid~Minion~3~3~3~Demon~Imprisoned Satyr"
	requireTarget, keyWord, description = False, "", "Dormant for 2 turns. When this awakens, reduce the Cost of a random minion in your hand by (5)"
	name_CN = "被禁锢的萨特"
	
	def awakenEffect(self):
		minions = [card for card in self.Game.Hand_Deck.hands[self.ID] if card.type == "Minion"]
		if minions: ManaMod(npchoice(minions), changeby=-5).applies()
		
		
class Germination(Spell):
	Class, school, name = "Druid", "Nature", "Germination"
	requireTarget, mana = True, 4
	index = "BLACK_TEMPLE~Druid~Spell~4~Nature~Germination"
	description = "Summon a copy of a friendly minion. Give the copy Taunt"
	name_CN = "萌芽分裂"
	def available(self):
		return self.selectableFriendlyMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.ID == self.ID and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			Copy = target.selfCopy(target.ID, self)
			self.summon(Copy, target.pos+1)
			Copy.getsStatus("Taunt")
		return target
		
		
class Overgrowth(Spell):
	Class, school, name = "Druid", "Nature", "Overgrowth"
	requireTarget, mana = False, 4
	index = "BLACK_TEMPLE~Druid~Spell~4~Nature~Overgrowth"
	description = "Gain two empty Mana Crystals"
	name_CN = "过度生长"
	#不知道满费用和9费时如何结算,假设不会给抽牌的衍生物
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if not self.Game.Manas.gainEmptyManaCrystal(2, self.ID):
			self.addCardtoHand(ExcessMana, self.ID)
		return None
		
		
class GlowflySwarm(Spell):
	Class, school, name = "Druid", "", "Glowfly Swarm"
	requireTarget, mana = False, 5
	index = "BLACK_TEMPLE~Druid~Spell~5~~Glowfly Swarm"
	description = "Summon a 2/2 Glowfly for each spell in your hand"
	name_CN = "萤火成群"
	def available(self):
		return self.Game.space(self.ID) > 0
		
	def effCanTrig(self):
		self.effectViable = any(card.type == "Spell" and card != self for card in self.Game.Hand_Deck.hands[self.ID])
			
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		num = sum(card.type == "Spell" for card in self.Game.Hand_Deck.hands[self.ID])
		if num > 0:
			self.summon([Glowfly(self.Game, self.ID) for i in range(num)], (-1, "totheRightEnd"))
		return None
		
class Glowfly(Minion):
	Class, race, name = "Druid", "Beast", "Glowfly"
	mana, attack, health = 2, 2, 2
	index = "BLACK_TEMPLE~Druid~Minion~2~2~2~Beast~Glowfly~Uncollectible"
	requireTarget, keyWord, description = False, "", ""
	name_CN = "萤火虫"
	
	
class MarshHydra(Minion):
	Class, race, name = "Druid", "Beast", "Marsh Hydra"
	mana, attack, health = 7, 7, 7
	index = "BLACK_TEMPLE~Druid~Minion~7~7~7~Beast~Marsh Hydra~Rush"
	requireTarget, keyWord, description = False, "Rush", "Rush. After this attacks, add a random 8-Cost minion to your hand"
	name_CN = "沼泽多头蛇"
	poolIdentifier = "8-Cost Minions"
	@classmethod
	def generatePool(cls, pools):
		return "8-Cost Minions", pools.MinionsofCost[8]
		
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_MarshHydra(self)]
		
class Trig_MarshHydra(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["MinionAttackedMinion", "MinionAttackedHero"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject == self.entity
		
	def text(self, CHN):
		return "在该随从攻击后，随机将一张法力值消耗为(8)的随从置入你的手牌" if CHN \
				else "After this attacks, add a random 8-Cost minion to your hand"
				
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.addCardtoHand(npchoice(self.rngPool("8-Cost Minions")), self.entity.ID)
			
			
class YsielWindsinger(Minion):
	Class, race, name = "Druid", "", "Ysiel Windsinger"
	mana, attack, health = 9, 5, 5
	index = "BLACK_TEMPLE~Druid~Minion~9~5~5~~Ysiel Windsinger~Legendary"
	requireTarget, keyWord, description = False, "", "Your spells cost (1)"
	name_CN = "伊谢尔风歌"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.auras["Your spells cost (1)"] = ManaAura(self, changeby=0, changeto=1)
		
	def manaAuraApplicable(self, subject): #ID用于判定是否是我方手中的随从
		return subject.type == "Spell" and subject.ID == self.ID
		
"""Hunter cards"""
class Helboar(Minion):
	Class, race, name = "Hunter", "Beast", "Helboar"
	mana, attack, health = 1, 2, 1
	index = "BLACK_TEMPLE~Hunter~Minion~1~2~1~Beast~Helboar~Deathrattle"
	requireTarget, keyWord, description = False, "", "Deathrattle: Give a random Beast in your hand +1/+1"
	name_CN = "地狱野猪"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.deathrattles = [GiveaRandomBeastinYourHandPlus1Plus1(self)]
		
class GiveaRandomBeastinYourHandPlus1Plus1(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		beasts = [card for card in self.entity.Game.Hand_Deck.hands[self.entity.ID] \
				  if card.type == "Minion" and "Beast" in card.race and card.mana > 0]
		if beasts: npchoice(beasts).buffDebuff(1, 1)
		
	def text(self, CHN):
		return "亡语：随机使你手牌中的一张野兽获得+1/+1" if CHN else "Deathrattle: Give a random Beast in your hand +1/+1"
		
		
class ImprisonedFelmaw(Minion_Dormantfor2turns):
	Class, race, name = "Hunter", "Demon", "Imprisoned Felmaw"
	mana, attack, health = 2, 5, 4
	index = "BLACK_TEMPLE~Hunter~Minion~2~5~4~Demon~Imprisoned Felmaw"
	requireTarget, keyWord, description = False, "", "Dormant for 2 turns. When this awakens, attack a random enemy"
	name_CN = "被禁锢的魔喉"
	#假设这个攻击不会消耗随从的攻击机会
	def awakenEffect(self):
		targets = self.Game.charsAlive(3-self.ID)
		if targets: self.Game.battle(self, npchoice(targets), verifySelectable=False, useAttChance=False, resolveDeath=False)
		
		
class PackTactics(Secret):
	Class, school, name = "Hunter", "", "Pack Tactics"
	requireTarget, mana = False, 2
	index = "BLACK_TEMPLE~Hunter~Spell~2~~Pack Tactics~~Secret"
	description = "Secret: When a friendly minion is attacked, summon a 3/3 copy"
	name_CN = "集群战术"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_PackTactics(self)]
		
class Trig_PackTactics(SecretTrigger):
	def __init__(self, entity):
		super().__init__(entity, ["MinionAttacksMinion", "HeroAttacksMinion"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.ID != self.entity.Game.turn and target[0].ID == self.entity.ID and self.entity.Game.space(self.entity.ID) > 0
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.summon(target[0].selfCopy(self.entity.ID, self.entity, 3, 3), target[0].pos+1)
		
		
class ScavengersIngenuity(Spell):
	Class, school, name = "Hunter", "", "Scavenger's Ingenuity"
	requireTarget, mana = False, 2
	index = "BLACK_TEMPLE~Hunter~Spell~2~~Scavenger's Ingenuity"
	description = "Draw a Beast. Give it +2/+2"
	name_CN = "拾荒者的智慧"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		beasts = [i for i, card in enumerate(self.Game.Hand_Deck.decks[self.ID]) if card.type == "Minion" and "Beast" in card.race]
		if beasts:
			beast = self.Game.Hand_Deck.drawCard(self.ID, npchoice(beasts))[0]
			if beast: beast.buffDebuff(2, 2)
		return None
		
		
class AugmentedPorcupine(Minion):
	Class, race, name = "Hunter", "Beast", "Augmented Porcupine"
	mana, attack, health = 3, 2, 4
	index = "BLACK_TEMPLE~Hunter~Minion~3~2~4~Beast~Augmented Porcupine~Deathrattle"
	requireTarget, keyWord, description = False, "", "Deathrattle: Deals this minion's Attack damage randomly split among all enemies"
	name_CN = "强能箭猪"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.deathrattles = [DealDamageEqualtoAttack(self)]
		
class DealDamageEqualtoAttack(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		minion = self.entity
		for num in range(number):
			enemies = self.entity.Game.charsAlive(3-minion.ID)
			if enemies: minion.dealsDamage(npchoice(enemies), 1)
			else: break
				
	def text(self, CHN):
		return "亡语：造成等同于该随从攻击力的伤害，随机分配到所有敌人身上" if CHN \
				else "Deathrattle: Deal this minion's Attack damage randomly split among all enemies"
				
				
class ZixorApexPredator(Minion):
	Class, race, name = "Hunter", "Beast", "Zixor, Apex Predator"
	mana, attack, health = 3, 2, 4
	index = "BLACK_TEMPLE~Hunter~Minion~3~2~4~Beast~Zixor, Apex Predator~Rush~Deathrattle~Legendary"
	requireTarget, keyWord, description = False, "Rush", "Rush. Deathrattle: Shuffle 'Zixor Prime' into your deck"
	name_CN = "顶级捕食者兹克索尔"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.deathrattles = [ShuffleZixorPrimeintoYourDeck(self)]
		
class ShuffleZixorPrimeintoYourDeck(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		minion = self.entity
		minion.Game.Hand_Deck.shuffleintoDeck(ZixorPrime(minion.Game, minion.ID), creator=minion)
		
	def text(self, CHN):
		return "亡语：将“终极兹克索尔”洗入你的牌库" if CHN else "Deathrattle: Shuffle 'Zixor Prime' into your deck"
		
class ZixorPrime(Minion):
	Class, race, name = "Hunter", "Beast", "Zixor Prime"
	mana, attack, health = 8, 4, 4
	index = "BLACK_TEMPLE~Hunter~Minion~8~4~4~Beast~Zixor Prime~Rush~Battlecry~Legendary~Uncollectible"
	requireTarget, keyWord, description = False, "Rush", "Rush. Battlecry: Summon 3 copies of this minion"
	name_CN = "终极兹克索尔"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		#假设已经死亡时不会召唤复制
		if self.onBoard or self.inHand:
			copies = [self.selfCopy(self.ID, self) for i in range(3)]
			self.summon(copies, (self.pos, "totheRight"))
		return None
		
		
class MokNathalLion(Minion):
	Class, race, name = "Hunter", "Beast", "Mok'Nathal Lion"
	mana, attack, health = 4, 5, 2
	index = "BLACK_TEMPLE~Hunter~Minion~4~5~2~Beast~Mok'Nathal Lion~Rush~Battlecry"
	requireTarget, keyWord, description = True, "Rush", "Rush. Battlecry: Choose a friendly minion. Gain a copy of its Deathrattle"
	name_CN = "莫克纳萨将狮"
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
	Class, school, name = "Hunter", "", "Scrap Shot"
	requireTarget, mana = True, 4
	index = "BLACK_TEMPLE~Hunter~Spell~4~~Scrap Shot"
	description = "Deal 3 damage. Give a random Beast in your hand +3/+3"
	name_CN = "废铁射击"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			damage = (3 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			self.dealsDamage(target, damage)
			beasts = [card for card in self.Game.Hand_Deck.hands[self.ID] if card.type == "Minion" and "Beast" in card.race]
			if beasts: npchoice(beasts).buffDebuff(3, 3)
		return target
		
		
class BeastmasterLeoroxx(Minion):
	Class, race, name = "Hunter", "", "Beastmaster Leoroxx"
	mana, attack, health = 8, 5, 5
	index = "BLACK_TEMPLE~Hunter~Minion~8~5~5~~Beastmaster Leoroxx~Battlecry~Legendary"
	requireTarget, keyWord, description = False, "", "Battlecry: Summon 3 Beasts from your hand"
	name_CN = "兽王莱欧洛克斯"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		refMinion = self
		for num in range(3):
			beasts = [i for i, card in enumerate(self.Game.Hand_Deck.hands[self.ID]) if card.type == "Minion" and "Beast" in card.race]
			if beasts and self.Game.space(self.ID) > 0:
				refMinion = self.Game.summonfrom(beasts, self.ID, refMinion.pos+1, self, source='H')
			else: break
		return None
		
		
class NagrandSlam(Spell):
	Class, school, name = "Hunter", "", "Nagrand Slam"
	requireTarget, mana = False, 10
	index = "BLACK_TEMPLE~Hunter~Spell~10~~Nagrand Slam"
	description = "Summon four 3/5 Clefthoofs that attack random enemies"
	name_CN = "纳格兰大冲撞"
	def available(self):
		return self.Game.space(self.ID) > 0
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		clefthoofs = [Clefthoof(curGame, self.ID) for i in range(4)]
		self.summon(clefthoofs, (-1, "totheRightEnd"))
		#不知道卡德加翻倍召唤出的随从是否会攻击那个随从，假设不会
		for clefthoof in clefthoofs:
			#Clefthoofs must be living to initiate attacks
			if clefthoof.onBoard and clefthoof.health > 0 and not clefthoof.dead:
				targets = curGame.charsAlive(3-self.ID)
				if targets:
					curGame.battle(clefthoof, npchoice(targets), verifySelectable=False, useAttChance=True, resolveDeath=False) #攻击会消耗攻击机会
				else: break
		return None
		
class Clefthoof(Minion):
	Class, race, name = "Hunter", "Beast", "Clefthoof"
	mana, attack, health = 4, 3, 5
	index = "BLACK_TEMPLE~Hunter~Minion~4~3~5~Beast~Clefthoof~Uncollectible"
	requireTarget, keyWord, description = False, "", ""
	name_CN = "裂蹄牛"
	
"""Mage cards"""
class Evocation(Spell):
	Class, school, name = "Mage", "Arcane", "Evocation"
	requireTarget, mana = False, 2
	index = "BLACK_TEMPLE~Mage~Spell~2~Arcane~Evocation~Legendary"
	description = "Fill your hand with random Mage spells. At the end of your turn, discard them"
	name_CN = "唤醒"
	poolIdentifier = "Mage Spells"
	@classmethod
	def generatePool(cls, pools):
		return "Mage Spells", [card for card in pools.ClassCards["Mage"] if card.type == "Spell"]
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		pool = tuple(self.rngPool("Mage Spells"))
		while curGame.Hand_Deck.handNotFull(self.ID):
			spell = npchoice(pool)(curGame, self.ID)
			spell.getsTrig(Trig_Evocation(spell), trigType="TrigHand")
			self.addCardtoHand(spell, self.ID)
		return None
		
class Trig_Evocation(TrigHand):
	def __init__(self, entity):
		super().__init__(entity, ["TurnEnds"])
		self.inherent = False
		self.changesCard = True
		
	#They will be discarded at the end of any turn
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.inHand
		
	def text(self, CHN):
		return "在你的回合结束时，弃掉这张牌" if CHN else "At the end of your turn, discard this card"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.Game.Hand_Deck.discard(self.entity.ID, self.entity)
		
		
class FontofPower(Spell):
	Class, school, name = "Mage", "Arcane", "Font of Power"
	requireTarget, mana = False, 1
	index = "BLACK_TEMPLE~Mage~Spell~1~Arcane~Font of Power"
	description = "Discover a Mage minion. If your deck has no minions, keep all 3"
	name_CN = "能量之泉"
	poolIdentifier = "Mage Minions"
	@classmethod
	def generatePool(cls, pools):
		return "Mage Minions", [card for card in pools.ClassCards["Mage"] if card.type == "Minion"]
		
	def effCanTrig(self):
		self.effectViable = self.Game.Hand_Deck.noMinionsinDeck(self.ID)
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		pool = self.rngPool("Mage Minions")
		if curGame.Hand_Deck.noMinionsinDeck(self.ID):
			self.addCardtoHand(npchoice(pool, 3, replace=False), self.ID, byDiscover=True)
		else:
			self.discoverandGenerate(FontofPower, comment, lambda : pool)
		return None
		
		
class ApexisSmuggler(Minion):
	Class, race, name = "Mage", "", "Apexis Smuggler"
	mana, attack, health = 2, 2, 3
	index = "BLACK_TEMPLE~Mage~Minion~2~2~3~~Apexis Smuggler"
	requireTarget, keyWord, description = False, "", "After you play a Secret, Discover a spell"
	name_CN = "埃匹希斯走私犯"
	poolIdentifier = "Mage Spells"
	@classmethod
	def generatePool(cls, pools):
		return [Class + " Spells" for Class in pools.Classes], \
			   [[card for card in pools.ClassCards[Class] if card.type == "Spell"] for Class in pools.Classes]
	
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_ApexisSmuggler(self)]
		
class Trig_ApexisSmuggler(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["SpellBeenPlayed"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject.ID == self.entity.ID and subject.description.startswith("Secret:")
		
	def text(self, CHN):
		return "在你使用一张奥秘牌后，发现一张法术牌" if CHN else "After you play a Secret, Discover a spell"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.discoverandGenerate(ApexisSmuggler, '', lambda : self.rngPool(classforDiscover(self.entity) + " Spells"))
		
		
class AstromancerSolarian(Minion):
	Class, race, name = "Mage", "", "Astromancer Solarian"
	mana, attack, health = 2, 3, 2
	index = "BLACK_TEMPLE~Mage~Minion~2~3~2~~Astromancer Solarian~Spell Damage~Deathrattle~Legendary"
	requireTarget, keyWord, description = False, "Spell Damage", "Spell Damage +1. Deathrattle: Shuffle 'Solarian Prime' into your deck"
	name_CN = "星术师索兰莉安"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.deathrattles = [ShuffleSolarianPrimeintoYourDeck(self)]
		
class ShuffleSolarianPrimeintoYourDeck(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		minion = self.entity
		minion.Game.Hand_Deck.shuffleintoDeck(SolarianPrime(minion.Game, minion.ID), creator=minion)
		
	def text(self, CHN):
		return "亡语：将“终极索兰莉安”洗入你的牌库" if CHN else "Deathrattle: Shuffle 'Solarian Prime' into your deck"
		
class SolarianPrime(Minion):
	Class, race, name = "Mage", "Demon", "Solarian Prime"
	mana, attack, health = 9, 7, 7
	index = "BLACK_TEMPLE~Mage~Minion~9~7~7~Demon~Solarian Prime~Spell Damage~Battlecry~Legendary~Uncollectible"
	requireTarget, keyWord, description = False, "Spell Damage", "Spell Damage +1. Battlecry: Cast 5 random Mage spells (target enemies if possible)"
	name_CN = "终极索兰莉安"
	poolIdentifier = "Mage Spells"
	@classmethod
	def generatePool(cls, pools):
		return "Mage Spells", [card for card in pools.ClassCards["Mage"] if card.type == "Spell"]
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		for i in range(5):
			npchoice(self.rngPool("Mage Spells"))(self.Game, self.ID).cast(None, "enemy1st")
			self.Game.gathertheDead(decideWinner=True)
		return None
		
		
class IncantersFlow(Spell):
	Class, school, name = "Mage", "Arcane", "Incanter's Flow"
	requireTarget, mana = False, 3
	index = "BLACK_TEMPLE~Mage~Spell~3~Arcane~Incanter's Flow"
	description = "Reduce the Cost of spells in your deck by (1)"
	name_CN = "咒术洪流"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		for card in self.Game.Hand_Deck.decks[self.ID][:]:
			if card.type == "Spell": ManaMod(card, changeby=-1).applies()
		return None
		
		
class Starscryer(Minion):
	Class, race, name = "Mage", "", "Starscryer"
	mana, attack, health = 2, 3, 1
	index = "BLACK_TEMPLE~Mage~Minion~2~3~1~~Starscryer~Deathrattle"
	requireTarget, keyWord, description = False, "", "Deathrattle: Draw a spell"
	name_CN = "星占师"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.deathrattles = [DrawaSpell(self)]
		
class DrawaSpell(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		spells = [i for i, card in enumerate(self.entity.Game.Hand_Deck.decks[self.entity.ID]) if card.type == "Spell"]
		if spells: self.entity.Game.Hand_Deck.drawCard(self.entity.ID, npchoice(spells))
		
	def text(self, CHN):
		return "亡语：抽一张法术牌" if CHN else "Deathrattle: Draw a spell"
		
		
class ImprisonedObserver(Minion_Dormantfor2turns):
	Class, race, name = "Mage", "Demon", "Imprisoned Observer"
	mana, attack, health = 3, 4, 5
	index = "BLACK_TEMPLE~Mage~Minion~3~4~5~Demon~Imprisoned Observer"
	requireTarget, keyWord, description = False, "", "Dormant for 2 turns. When this awakens, deal 2 damage to all enemy minions"
	name_CN = "被禁锢的眼魔"
	
	def awakenEffect(self):
		targets = self.Game.minionsonBoard(3-self.ID)
		self.dealsAOE(targets, [2]*len(targets))
		
		
class NetherwindPortal(Secret):
	Class, school, name = "Mage", "Arcane", "Netherwind Portal"
	requireTarget, mana = False, 3
	index = "BLACK_TEMPLE~Mage~Spell~3~Arcane~Netherwind Portal~~Secret"
	description = "Secret: After your opponent casts a spell, summon a random 4-Cost minion"
	name_CN = "虚空之风传送门"
	poolIdentifier = "4-Cost Minions to Summon"
	@classmethod
	def generatePool(cls, pools):
		return "4-Cost Minions to Summon", pools.MinionsofCost[4]
		
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_NetherwindPortal(self)]
		
class Trig_NetherwindPortal(SecretTrigger):
	def __init__(self, entity):
		super().__init__(entity, ["SpellBeenPlayed"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.ID != self.entity.Game.turn and subject.ID != self.entity.ID and self.entity.Game.space(self.entity.ID) > 0
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.summon(npchoice(self.rngPool("4-Cost Minions to Summon"))(self.entity.Game, self.entity.ID), -1)
		
		
class ApexisBlast(Spell):
	Class, school, name = "Mage", "", "Apexis Blast"
	requireTarget, mana = True, 5
	index = "BLACK_TEMPLE~Mage~Spell~5~~Apexis Blast"
	description = "Deal 5 damage. If your deck has no minions, summon a random 5-Cost minion"
	name_CN = "埃匹希斯冲击"
	poolIdentifier = "5-Cost Minions to Summon"
	@classmethod
	def generatePool(cls, pools):
		return "5-Cost Minions to Summon", pools.MinionsofCost[5]
		
	def effCanTrig(self):
		self.effectViable = self.Game.Hand_Deck.noMinionsinDeck(self.ID)
		
	def text(self, CHN):
		damage = (5 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		return "造成%d点伤害。如果你的牌库中没有随从牌，随机召唤一个法力消耗为(5)的随从"%damage if CHN \
				else "Deal %d damage. If your deck has no minions, summon a random 5-Cost minion"%damage
				
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			damage = (5 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			self.dealsDamage(target, damage)
			if self.Game.Hand_Deck.noMinionsinDeck(self.ID):
				self.summon(npchoice(self.rngPool("5-Cost Minions to Summon"))(self.Game, self.ID), -1)
		return target
		
		
class DeepFreeze(Spell):
	Class, school, name = "Mage", "Frost", "Deep Freeze"
	requireTarget, mana = True, 8
	index = "BLACK_TEMPLE~Mage~Spell~8~Frost~Deep Freeze"
	description = "Freeze an enemy. Summon two 3/6 Water Elementals"
	name_CN = "深度冻结"
	def available(self):
		return self.selectableEnemyExists()
		
	def targetCorrect(self, target, choice=0):
		return (target.type == "Minion" or target.type == "Hero") and target.ID != self.ID and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			target.getsStatus("Frozen")
		self.summon([WaterElemental_Basic(self.Game, self.ID) for i in range(2)], (-1, "totheRightEnd"))
		return target
		
"""Paladin cards"""
class ImprisonedSungill(Minion_Dormantfor2turns):
	Class, race, name = "Paladin", "Murloc", "Imprisoned Sungill"
	mana, attack, health = 1, 2, 1
	index = "BLACK_TEMPLE~Paladin~Minion~1~2~1~Murloc~Imprisoned Sungill"
	requireTarget, keyWord, description = False, "", "Dormant for 2 turns. When this awakens, Summon two 1/1 Murlocs"
	name_CN = "被禁锢的阳鳃鱼人"
	
	def awakenEffect(self):
		self.summon([SungillStreamrunner(self.Game, self.ID) for i in range(2)], (self.pos, "leftandRight"))
		
class SungillStreamrunner(Minion):
	Class, race, name = "Paladin", "Murloc", "Sungill Streamrunner"
	mana, attack, health = 1, 1, 1
	index = "BLACK_TEMPLE~Paladin~Minion~1~1~1~Murloc~Sungill Streamrunner~Uncollectible"
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
			#def ManaMod.selfCopy(self, recipientCard):
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
	index = "BLACK_TEMPLE~Paladin~Minion~1~1~3~~Aldor Attendant~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Reduce the Cost of your Librams by (1) this game"
	name_CN = "奥尔多侍从"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		GameManaAura_Libram(self.Game, self.ID, -1, -1).auraAppears()
		return None
		
		
class HandofAdal(Spell):
	Class, school, name = "Paladin", "Holy",  "Hand of A'dal"
	requireTarget, mana = True, 2
	index = "BLACK_TEMPLE~Paladin~Spell~2~Holy~Hand of A'dal"
	description = "Give a minion +2/+1. Draw a card"
	name_CN = "阿达尔之手"
	def targetExists(self, choice=0):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target: target.buffDebuff(2, 1)
		self.Game.Hand_Deck.drawCard(self.ID)
		return target
		
		
class MurgurMurgurgle(Minion):
	Class, race, name = "Paladin", "Murloc", "Murgur Murgurgle"
	mana, attack, health = 2, 2, 1
	index = "BLACK_TEMPLE~Paladin~Minion~2~2~1~Murloc~Murgur Murgurgle~Divine Shield~Deathrattle~Legendary"
	requireTarget, keyWord, description = False, "Divine Shield", "Divine Shield. Deathrattle: Shuffle 'Murgurgle Prime' into your deck"
	name_CN = "莫戈尔·莫戈尔格"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.deathrattles = [ShuffleMurgurglePrimeintoYourDeck(self)]
		
class ShuffleMurgurglePrimeintoYourDeck(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		minion = self.entity
		minion.Game.Hand_Deck.shuffleintoDeck(MurgurglePrime(minion.Game, minion.ID), creator=minion)
		
	def text(self, CHN):
		return "亡语：将“终极莫戈尔格”洗入你的牌库" if CHN else "Deathrattle: Shuffle 'Murgurgle Prime' into your deck"
		
class MurgurglePrime(Minion):
	Class, race, name = "Paladin", "Murloc", "Murgurgle Prime"
	mana, attack, health = 8, 6, 3
	index = "BLACK_TEMPLE~Paladin~Minion~8~6~3~Murloc~Murgurgle Prime~Divine Shield~Battlecry~Legendary~Uncollectible"
	requireTarget, keyWord, description = False, "Divine Shield", "Divine Shield. Battlecry: Summon 4 random Murlocs. Give them Divine Shield"
	name_CN = "终极莫戈尔格"
	poolIdentifier = "Murlocs to Summon"
	@classmethod
	def generatePool(cls, pools):
		return "Murlocs to Summon", pools.MinionswithRace["Murloc"]
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		murlocs = [murloc(self.Game, self.ID) for murloc in npchoice(self.rngPool("Murlocs to Summon"), 4, replace=True)]
		pos = (self.pos, "leftandRight") if self.onBoard else (-1, "totheRightEnd")
		self.summon(murlocs, pos)
		for murloc in murlocs:
			if murloc.onBoard: murloc.getsStatus("Divine Shield")
		return None
		
		
class LibramofWisdom(Spell):
	Class, school, name = "Paladin", "Holy",  "Libram of Wisdom"
	requireTarget, mana = True, 2
	index = "BLACK_TEMPLE~Paladin~Spell~2~Holy~Libram of Wisdom"
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
		self.entity.addCardtoHand(LibramofWisdom, self.entity.ID, byType=True)
		
		
class UnderlightAnglingRod(Weapon):
	Class, name, description = "Paladin", "Underlight Angling Rod", "After your hero attacks, add a random Murloc to your hand"
	mana, attack, durability = 3, 3, 2
	index = "BLACK_TEMPLE~Paladin~Weapon~3~3~2~Underlight Angling Rod"
	name_CN = "幽光鱼竿"
	poolIdentifier = "Murlocs"
	@classmethod
	def generatePool(cls, pools):
		return "Murlocs", pools.MinionswithRace["Murloc"]
		
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_UnderlightAnglingRod(self)]
		
class Trig_UnderlightAnglingRod(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["HeroAttackedMinion", "HeroAttackedHero"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject == self.entity.Game.heroes[self.entity.ID] and self.entity.onBoard
		
	def text(self, CHN):
		return "在你的英雄攻击后，随机将一张鱼人牌置入你的手牌" if CHN \
				else "After your hero attacks, add a random Murloc to your hand"
				
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.addCardtoHand(npchoice(self.rngPool("Murlocs")), self.entity.ID)
			
			
class AldorTruthseeker(Minion):
	Class, race, name = "Paladin", "", "Aldor Truthseeker"
	mana, attack, health = 5, 4, 6
	index = "BLACK_TEMPLE~Paladin~Minion~5~4~6~~Aldor Truthseeker~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Reduce the Cost of your Librams by (2) this game"
	name_CN = "奥尔多真理追寻者"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		GameManaAura_Libram(self.Game, self.ID, -2, -1).auraAppears()
		return None
		
		
class LibramofJustice(Spell):
	Class, school, name = "Paladin", "Holy",  "Libram of Justice"
	requireTarget, mana = False, 5
	index = "BLACK_TEMPLE~Paladin~Spell~5~Holy~Libram of Justice"
	description = "Equip a 1/4 weapon. Change the Health of all enemy minions to 1"
	name_CN = "正义圣契"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.equipWeapon(OverdueJustice(self.Game, self.ID))
		for minion in self.Game.minionsonBoard(3-self.ID):
			minion.statReset(False, 1)
		return None
		
class OverdueJustice(Weapon):
	Class, name, description = "Paladin", "Overdue Justice", ""
	mana, attack, durability = 1, 1, 4
	index = "BLACK_TEMPLE~Paladin~Weapon~1~1~4~Overdue Justice~Uncollectible"
	name_CN = "迟到的正义"
	
class LadyLiadrin(Minion):
	Class, race, name = "Paladin", "", "Lady Liadrin"
	mana, attack, health = 7, 4, 6
	index = "BLACK_TEMPLE~Paladin~Minion~7~4~6~~Lady Liadrin~Battlecry~Legendary"
	requireTarget, keyWord, description = False, "", "Battlecry: Add a copy of each spell you cast on friendly characters this game to your hand"
	name_CN = "女伯爵莉亚德琳"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		pool = tuple([self.Game.cardPool[index] for index in self.Game.Counters.spellsonFriendliesThisGame[self.ID]])
		spells = npchoice(pool, min(self.Game.Hand_Deck.spaceinHand(self.ID), len(pool)), replace=False)
		if spells: self.addCardtoHand(spells, self.ID)
		return None
		
		
class LibramofHope(Spell):
	Class, school, name = "Paladin", "Holy", "Libram of Hope"
	requireTarget, mana = True, 9
	index = "BLACK_TEMPLE~Paladin~Spell~9~Holy~Libram of Hope"
	description = "Restore 8 Health. Summon an 8/8 with Guardian with Taunt and Divine Shield"
	name_CN = "希望圣契"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			heal = 8 * (2 ** self.countHealDouble())
			self.restoresHealth(target, heal)
			self.summon(AncientGuardian(self.Game, self.ID), -1)
		return target
		
class AncientGuardian(Minion):
	Class, race, name = "Paladin", "", "Ancient Guardian"
	mana, attack, health = 8, 8, 8
	index = "BLACK_TEMPLE~Paladin~Minion~8~8~8~~Ancient Guardian~Taunt~Divine Shield~Uncollectible"
	requireTarget, keyWord, description = False, "Taunt,Divine Shield", "Taunt, Divine Shield"
	name_CN = "远古守卫"
	
"""Priest cards"""
class ImprisonedHomunculus(Minion_Dormantfor2turns):
	Class, race, name = "Priest", "Demon", "Imprisoned Homunculus"
	mana, attack, health = 1, 2, 5
	index = "BLACK_TEMPLE~Priest~Minion~1~2~5~Demon~Imprisoned Homunculus~Taunt"
	requireTarget, keyWord, description = False, "Taunt", "Dormant for 2 turns. Taunt"
	name_CN = "被禁锢的矮劣魔"
	
	
class ReliquaryofSouls(Minion):
	Class, race, name = "Priest", "", "Reliquary of Souls"
	mana, attack, health = 1, 1, 3
	index = "BLACK_TEMPLE~Priest~Minion~1~1~3~~Reliquary of Souls~Lifesteal~Deathrattle~Legendary"
	requireTarget, keyWord, description = False, "Lifesteal", "Lifesteal. Deathrattle: Shuffle 'Leliquary Prime' into your deck"
	name_CN = "灵魂之匣"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.deathrattles = [ShuffleReliquaryPrimeintoYourDeck(self)]
		
class ShuffleReliquaryPrimeintoYourDeck(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		minion = self.entity
		minion.Game.Hand_Deck.shuffleintoDeck(ReliquaryPrime(minion.Game, minion.ID), creator=minion)
		
	def text(self, CHN):
		return "亡语：将“终极魂匣”洗入你的牌库" if CHN else "Deathrattle: Shuffle 'Reliquary Prime' into your deck"
		
class ReliquaryPrime(Minion):
	Class, race, name = "Priest", "", "Reliquary Prime"
	mana, attack, health = 7, 6, 8
	index = "BLACK_TEMPLE~Priest~Minion~7~6~8~~Reliquary Prime~Taunt~Lifesteal~Legendary~Uncollectible"
	requireTarget, keyWord, description = False, "Taunt,Lifesteal", "Taunt, Lifesteal. Only you can target this with spells and Hero Powers"
	name_CN = "终极魂匣"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.marks["Enemy Evasive"] = 1
		
		
class Renew(Spell):
	Class, school, name = "Priest", "Holy", "Renew"
	requireTarget, mana = True, 2
	index = "BLACK_TEMPLE~Priest~Spell~2~Holy~Renew"
	description = "Restore 3 Health. Discover a spell"
	name_CN = "复苏"
	poolIdentifier = "Priest Spells"
	@classmethod
	def generatePool(cls, pools):
		return [Class+" Spells" for Class in pools.Classes], \
				[[card for card in pools.ClassCards[Class] if card.type == "Spell"] for Class in pools.Classes]
				
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if target:
			heal = 3 * (2 ** self.countHealDouble())
			self.restoresHealth(target, heal)
			self.discoverandGenerate(Renew, comment, lambda : self.rngPool(classforDiscover(self) + " Spells"))
		return target
		
		
class DragonmawSentinel(Minion):
	Class, race, name = "Priest", "", "Dragonmaw Sentinel"
	mana, attack, health = 2, 1, 4
	index = "BLACK_TEMPLE~Priest~Minion~2~1~4~~Dragonmaw Sentinel~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: If you're holding a Dragon, gain +1 Attack and Lifesteal"
	name_CN = "龙喉哨兵"
	
	def effCanTrig(self): #Friendly characters are always selectable.
		self.effectViable = self.Game.Hand_Deck.holdingDragon(self.ID)
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if self.Game.Hand_Deck.holdingDragon(self.ID):
			self.buffDebuff(1, 0)
			self.getsStatus("Lifesteal")
		return None
		
		
class SethekkVeilweaver(Minion):
	Class, race, name = "Priest", "", "Sethekk Veilweaver"
	mana, attack, health = 2, 2, 3
	index = "BLACK_TEMPLE~Priest~Minion~2~2~3~~Sethekk Veilweaver"
	requireTarget, keyWord, description = False, "", "After you cast a spell on a minion, add a Priest spell to your hand"
	name_CN = "塞泰克织巢者"
	poolIdentifier = "Priest Spells"
	@classmethod
	def generatePool(cls, pools):
		return "Priest Spells", [card for card in pools.ClassCards["Priest"] if card.type == "Spell"]
		
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_SethekkVeilweaver(self)]
		
class Trig_SethekkVeilweaver(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["SpellBeenPlayed"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject.ID == self.entity.ID and target and target.type == "Minion"
		
	def text(self, CHN):
		return "在你对一个随从施放法术后，随机将一张牧师法术牌置入你的手牌" if CHN \
				else "After you cast a spell on a minion, add a Priest spell to your hand"
				
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.addCardtoHand(npchoice(self.rngPool("Priest Spells")), self.entity.ID)
			
			
class Apotheosis(Spell):
	Class, school, name = "Priest", "Holy", "Apotheosis"
	requireTarget, mana = True, 3
	index = "BLACK_TEMPLE~Priest~Spell~3~Holy~Apotheosis"
	description = "Give a minion +2/+3 and Lifesteal"
	name_CN = "神圣化身"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			target.buffDebuff(2, 3)
			target.getsStatus("Lifesteal")
		return target
		
		
class DragonmawOverseer(Minion):
	Class, race, name = "Priest", "", "Dragonmaw Overseer"
	mana, attack, health = 3, 2, 2
	index = "BLACK_TEMPLE~Priest~Minion~3~2~2~~Dragonmaw Overseer"
	requireTarget, keyWord, description = False, "", "At the end of your turn, give another friendly minion +2/+2"
	name_CN = "龙喉监工"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_DragonmawOverseer(self)]
		
class Trig_DragonmawOverseer(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["TurnEnds"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and ID == self.entity.ID
		
	def text(self, CHN):
		return "在你的回合结束时，使另一个友方随从获得+2/+2" if CHN \
				else "At the end of your turn, give another friendly minion +2/+2"
				
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		minions = self.entity.Game.minionsonBoard(self.entity.ID, exclude=self.entity)
		if minions:	npchoice(minions).buffDebuff(2, 2)
		
				
class PsycheSplit(Spell):
	Class, school, name = "Priest", "Shadow", "Psyche Split"
	requireTarget, mana = True, 5
	index = "BLACK_TEMPLE~Priest~Spell~5~Shadow~Psyche Split"
	description = "Give a minion +1/+2. Summon a copy of it"
	name_CN = "心灵分裂"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			target.buffDebuff(1, 2)
			Copy = target.selfCopy(target.ID, self)
			self.summon(Copy, target.pos+1)
		return target
		
		
class SkeletalDragon(Minion):
	Class, race, name = "Priest", "Dragon", "Skeletal Dragon"
	mana, attack, health = 7, 4, 9
	index = "BLACK_TEMPLE~Priest~Minion~7~4~9~Dragon~Skeletal Dragon~Taunt"
	requireTarget, keyWord, description = False, "Taunt", "Taunt. At the end of your turn, add a Dragon to your hand"
	name_CN = "骸骨巨龙"
	poolIdentifier = "Dragons"
	@classmethod
	def generatePool(cls, pools):
		return "Dragons", pools.MinionswithRace["Dragon"]
		
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_SkeletalDragon(self)]
		
class Trig_SkeletalDragon(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["TurnEnds"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and ID == self.entity.ID
		
	def text(self, CHN):
		return "在你的回合结束时，将一张龙牌置入你的手牌" if CHN \
				else "At the end of your turn, add a Dragon to your hand"
				
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.addCardtoHand(npchoice(self.rngPool("Dragons")), self.entity.ID)
			
			
class SoulMirror(Spell):
	Class, school, name = "Priest", "Shadow", "Soul Mirror"
	requireTarget, mana = False, 7
	index = "BLACK_TEMPLE~Priest~Spell~7~Shadow~Soul Mirror~Legendary"
	description = "Summon copies of enemy minions. They attack their copies"
	name_CN = "灵魂之镜"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		minions = self.Game.minionsonBoard(3-self.ID)
		if minions:
			pairs = [minions, [minion.selfCopy(self.ID, self) for minion in minions]]
			if self.summon(pairs[1], (-1, "totheRightEnd")):
				for minion, Copy in zip(pairs[0], pairs[1]):
					if minion.onBoard and minion.health > 0 and minion.dead == False and Copy.onBoard and Copy.health > 0 and Copy.dead == False:
						#假设不消耗攻击机会，那些随从在攻击之后被我方拐走仍然可以攻击
						#def battle(self, subject, target, verifySelectable=True, useAttChance=True, resolveDeath=True, resetRedirTrig=True)
						self.Game.battle(minion, Copy, verifySelectable=False, useAttChance=False, resolveDeath=False, resetRedirTrig=True)
		return None
		
		
"""Rogue cards"""
class BlackjackStunner(Minion):
	Class, race, name = "Rogue", "", "Blackjack Stunner"
	mana, attack, health = 1, 1, 2
	index = "BLACK_TEMPLE~Rogue~Minion~1~1~2~~Blackjack Stunner~Battlecry"
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
	index = "BLACK_TEMPLE~Rogue~Minion~1~3~1~~Spymistress~Stealth"
	requireTarget, keyWord, description = False, "Stealth", "Stealth"
	name_CN = "间谍女郎"
	
	
class Ambush(Secret):
	Class, school, name = "Rogue", "", "Ambush"
	requireTarget, mana = False, 2
	index = "BLACK_TEMPLE~Rogue~Spell~2~~Ambush~~Secret"
	description = "Secret: After your opponent plays a minion, summon a 2/3 Ambusher with Poisonous"
	name_CN = "伏击"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_Ambush(self)]
		
class Trig_Ambush(SecretTrigger):
	def __init__(self, entity):
		super().__init__(entity, ["MinionBeenPlayed"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.ID != self.entity.Game.turn and subject.ID != self.entity.ID and self.entity.Game.space(self.entity.ID) > 0
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.summon(BrokenAmbusher(self.entity.Game, self.entity.ID), -1)
		
class BrokenAmbusher(Minion):
	Class, race, name = "Rogue", "", "Broken Ambusher"
	mana, attack, health = 2, 2, 3
	index = "BLACK_TEMPLE~Rogue~Minion~2~2~3~~Broken Ambusher~Poisonous~Uncollectible"
	requireTarget, keyWord, description = False, "Poisonous", "Poisonous"
	name_CN = "破碎者伏兵"
	
	
class AshtongueSlayer(Minion):
	Class, race, name = "Rogue", "", "Ashtongue Slayer"
	mana, attack, health = 2, 3, 2
	index = "BLACK_TEMPLE~Rogue~Minion~2~3~2~~Ashtongue Slayer~Battlecry"
	requireTarget, keyWord, description = True, "", "Battlecry: Give a Stealthed minion +3 Attack and Immune this turn"
	name_CN = "灰舌杀手"
	def targetExists(self, choice=0):
		return self.selectableFriendlyMinionExists(choice)
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target != self and (target.keyWords["Stealth"] > 0 or target.status["Temp Stealth"] > 0) and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			target.buffDebuff(3, 0, "EndofTurn")
			target.getsStatus("Immune")
		return target
		
		
class Bamboozle(Secret):
	Class, school, name = "Rogue", "", "Bamboozle"
	requireTarget, mana = False, 2
	index = "BLACK_TEMPLE~Rogue~Spell~2~~Bamboozle~~Secret"
	description = "Secret: When one of your minions is attacked, transform it into a random one that costs (3) more"
	name_CN = "偷天换日"
	poolIdentifier = "3-Cost Minions to Summon"
	@classmethod
	def generatePool(cls, pools):
		return ["%d-Cost Minions to Summon" % cost for cost in pools.MinionsofCost.keys()], \
			   list(pools.MinionsofCost.values())
	
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_Bamboozle(self)]
		
class Trig_Bamboozle(SecretTrigger):
	def __init__(self, entity):
		super().__init__(entity, ["MinionAttacksMinion", "HeroAttacksMinion"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.ID != self.entity.Game.turn and target[0].ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		cost = type(target[0]).mana + 3
		while "%d-Cost Minions to Summon" % cost not in self.entity.Game.RNGPools:
			cost -= 1
		#不知道如果攻击目标已经被导离这个目标随从之后是否会把目标重导向回它，假设不会
		newMinion = npchoice(self.rngPool("%d-Cost Minions to Summon" % cost))(self.entity.Game, self.entity.ID)
		self.entity.transform(target[0], newMinion)
		if target[0] == target[1]: target[0], target[1] = newMinion, newMinion
		else: target[0] = newMinion
		
			
class DirtyTricks(Secret):
	Class, school, name = "Rogue", "", "Dirty Tricks"
	requireTarget, mana = False, 2
	index = "BLACK_TEMPLE~Rogue~Spell~2~~Dirty Tricks~~Secret"
	description = "Secret: After your opponent casts a spell, draw 2 cards"
	name_CN = "邪恶计谋"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_DirtyTricks(self)]
		
class Trig_DirtyTricks(SecretTrigger):
	def __init__(self, entity):
		super().__init__(entity, ["SpellBeenPlayed"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.ID != self.entity.Game.turn and subject.ID != self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.Game.Hand_Deck.drawCard(self.entity.ID)
		self.entity.Game.Hand_Deck.drawCard(self.entity.ID)
		
		
class ShadowjewelerHanar(Minion):
	Class, race, name = "Rogue", "", "Shadowjeweler Hanar"
	mana, attack, health = 2, 1, 4
	index = "BLACK_TEMPLE~Rogue~Minion~2~1~4~~Shadowjeweler Hanar~Legendary"
	requireTarget, keyWord, description = False, "", "After you play a Secret, Discover a Secret from a different class"
	name_CN = "暗影珠宝师汉纳尔"
	poolIdentifier = "Rogue Secrets"
	@classmethod
	def generatePool(cls, pools):
		classes, lists = [], []
		for Class in pools.Classes:
			secrets = [card for card in pools.ClassCards[Class] if card.description.startswith("Secret:")]
			if secrets:
				classes.append(Class+" Secrets")
				lists.append(secrets)
		return classes, lists
		
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_ShadowjewelerHanar(self)]
		
class Trig_ShadowjewelerHanar(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["SpellBeenPlayed"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject.ID == self.entity.ID and subject.description.startswith("Secret:")
		
	def text(self, CHN):
		return "在你使用一张奥秘牌后，发现一张不同职业的奥秘牌" if CHN \
				else "After you play a Secret, Discover a Secret from a different class"
				
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		Classes = ["Hunter", "Mage", "Paladin", "Rogue"]
		try: Classes.remove(subject.Class) #The played secrets has a restricted Class pool
		except: pass
		self.entity.discoverandGenerate_MultiplePools(ShadowjewelerHanar, '',
													  poolFuncs=[lambda : self.rngPool(Class+" Secrets") for Class in Classes])
		
					
class Akama(Minion):
	Class, race, name = "Rogue", "", "Akama"
	mana, attack, health = 3, 3, 4
	index = "BLACK_TEMPLE~Rogue~Minion~3~3~4~~Akama~Stealth~Deathrattle~Legendary"
	requireTarget, keyWord, description = False, "Stealth", "Stealth. Deathrattle: Shuffle 'Akama Prime' into your deck"
	name_CN = "阿卡玛"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.deathrattles = [ShuffleAkamaPrimeintoYourDeck(self)]
		
class ShuffleAkamaPrimeintoYourDeck(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		minion = self.entity
		minion.Game.Hand_Deck.shuffleintoDeck(AkamaPrime(minion.Game, minion.ID), creator=minion)
		
	def text(self, CHN):
		return "亡语：将“终极阿卡玛”洗入你的牌库" if CHN else "Deathrattle: Shuffle 'Akama Prime' into your deck"
				
class AkamaPrime(Minion):
	Class, race, name = "Rogue", "", "Akama Prime"
	mana, attack, health = 6, 6, 5
	index = "BLACK_TEMPLE~Rogue~Minion~6~6~5~~Akama Prime~Stealth~Legendary~Uncollectible"
	requireTarget, keyWord, description = False, "Stealth", "Permanently Stealthed"
	name_CN = "终极阿卡玛"
	
	def losesStatus(self, keyWord):
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
	index = "BLACK_TEMPLE~Rogue~Minion~3~3~3~~Greyheart Sage~Battlecry"
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
	index = "BLACK_TEMPLE~Rogue~Minion~7~7~5~~Cursed Vagrant~Deathrattle"
	requireTarget, keyWord, description = False, "", "Deathrattle: Summon a 7/5 Shadow with Stealth"
	name_CN = "被诅咒的 流浪者"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.deathrattles = [SummonaShadowwithTaunt(self)]
		
class SummonaShadowwithTaunt(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.summon(CursedShadow(self.entity.Game, self.entity.ID), self.entity.pos+1)
		
	def text(self, CHN):
		return "亡语：召唤一个7/5并具有潜行的阴影" if CHN else "Deathrattle: Summon a 7/5 Shadow with Stealth"
		
class CursedShadow(Minion):
	Class, race, name = "Rogue", "", "Cursed Shadow"
	mana, attack, health = 7, 7, 5
	index = "BLACK_TEMPLE~Rogue~Minion~7~7~5~~Cursed Shadow~Stealth~Uncollectible"
	requireTarget, keyWord, description = False, "Stealth", "Stealth"
	name_CN = "被诅咒的阴影"
	
	
"""Shaman cards"""
class BogstrokClacker(Minion):
	Class, race, name = "Shaman", "", "Bogstrok Clacker"
	mana, attack, health = 3, 3, 3
	index = "BLACK_TEMPLE~Shaman~Minion~3~3~3~~Bogstrok Clacker~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Transform adjacent minions into random minions that cost (1) more"
	name_CN = "泥泽巨拳龙虾人"
	poolIdentifier = "1-Cost Minions to Summon"
	@classmethod
	def generatePool(cls, pools):
		return ["%d-Cost Minions to Summon" % cost for cost in pools.MinionsofCost.keys()], \
			   list(pools.MinionsofCost.values())
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if self.onBoard:
			minions, newMinions = self.Game.neighbors2(self)[0], []
			for minion in minions:
				cost = type(minion).mana + 3
				while "%d-Cost Minions to Summon" % cost not in self.Game.RNGPools:
					cost -= 1
				newMinions.append(npchoice(self.rngPool("%d-Cost Minions to Summon" % cost)))
			for minion, newMinion in zip(minions, newMinions):
				self.transform(minion, newMinion(self.Game, self.ID))
		return None
		
		
class LadyVashj(Minion):
	Class, race, name = "Shaman", "", "Lady Vashj"
	mana, attack, health = 3, 4, 3
	index = "BLACK_TEMPLE~Shaman~Minion~3~4~3~~Lady Vashj~Spell Damage~Deathrattle~Legendary"
	requireTarget, keyWord, description = False, "Spell Damage", "Spell Damage +1. Deathrattle: Shuffle 'Vashj Prime' into your deck"
	name_CN = "瓦斯琪女士"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.deathrattles = [ShuffleVashjPrimeintoYourDeck(self)]
		
class ShuffleVashjPrimeintoYourDeck(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		minion = self.entity
		minion.Game.Hand_Deck.shuffleintoDeck(VashjPrime(minion.Game, minion.ID), creator=minion)
		
	def text(self, CHN):
		return "亡语：将“终极瓦斯琪”洗入你的牌库" if CHN else "Deathrattle: Shuffle 'Vashj Prime' into your deck"
		
class VashjPrime(Minion):
	Class, race, name = "Shaman", "", "Vashj Prime"
	mana, attack, health = 7, 5, 4
	index = "BLACK_TEMPLE~Shaman~Minion~7~5~4~~Vashj Prime~Spell Damage~Battlecry~Legendary~Uncollectible"
	requireTarget, keyWord, description = False, "Spell Damage", "Spell Damage +1. Battlecry: Draw 3 spells. Reduce their Cost by (3)"
	name_CN = "终极瓦斯琪"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		ownDeck = self.Game.Hand_Deck.decks[self.ID]
		for num in range(3):
			spells = [i for i, card in enumerate(ownDeck) if card.type == "Spell"]
			if spells:
				spell = self.Game.Hand_Deck.drawCard(self.ID, npchoice(spells))[0]
				if spell: ManaMod(spell, changeby=-3, changeto=-1).applies()
				else: break
		return None
		
		
class Marshspawn(Minion):
	Class, race, name = "Shaman", "Elemental", "Marshspawn"
	mana, attack, health = 3, 3, 4
	index = "BLACK_TEMPLE~Shaman~Minion~3~3~4~Elemental~Marshspawn~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: If you cast a spell last turn, Discover a spell"
	name_CN = "沼泽之子"
	poolIdentifier = "Shaman Spells"
	@classmethod
	def generatePool(cls, pools):
		return [Class+" Spells" for Class in pools.Classes], \
				[[card for card in pools.ClassCards[Class] if card.type == "Spell"] for Class in pools.Classes]
				
	def effCanTrig(self):
		cardsEachTurn = any(card.type == "Spell" for card in self.Game.Counters.cardsPlayedEachTurn[self.ID][-2])
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if any(card.type == "Spell" for card in self.Game.Counters.cardsPlayedEachTurn[self.ID][-2]):
			self.discoverandGenerate(Marshspawn, comment, lambda : self.rngPool(classforDiscover(self) + " Spells"))
		return None
		
		
class SerpentshrinePortal(Spell):
	Class, school, name = "Shaman", "Nature", "Serpentshrine Portal"
	requireTarget, mana = True, 3
	index = "BLACK_TEMPLE~Shaman~Spell~3~Nature~Serpentshrine Portal~Overload"
	description = "Deal 3 damage. Summon a random 3-Cost minion. Overload: (1)"
	name_CN = "毒蛇神殿传送门"
	poolIdentifier = "3-Cost Minions to Summon"
	@classmethod
	def generatePool(cls, pools):
		return "3-Cost Minions to Summon", pools.MinionsofCost[3]
		
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.overload = 1
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			damage = (3 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			self.dealsDamage(target, damage)
			self.summon(npchoice(self.rngPool("3-Cost Minions to Summon"))(self.Game, self.ID), -1)
		return target
		
		
class TotemicReflection(Spell):
	Class, school, name = "Shaman", "", "Totemic Reflection"
	requireTarget, mana = True, 3
	index = "BLACK_TEMPLE~Shaman~Spell~3~~Totemic Reflection"
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
				self.summon(target.selfCopy(target.ID, self), target.pos+1)
		return target
		
		
class Torrent(Spell):
	Class, school, name = "Shaman", "Nature", "Torrent"
	requireTarget, mana = True, 4
	index = "BLACK_TEMPLE~Shaman~Spell~4~Nature~Torrent"
	description = "Deal 8 damage to a minion. Costs (3) less if you cast a spell last turn"
	name_CN = "洪流"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
		
	def effCanTrig(self):
		self.effectViable = any(card.type == "Spell" for card in self.Game.Counters.cardsPlayedEachTurn[self.ID][-2])
		
	def selfManaChange(self):
		if self.inHand and any(card.type == "Spell" for card in self.Game.Counters.cardsPlayedEachTurn[self.ID][-2]):
			self.mana -= 3
			self.mana = max(self.mana, 0)
			
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			damage = (8 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			self.dealsDamage(target, damage)
		return target
		
		
class VividSpores(Spell):
	Class, school, name = "Shaman", "Nature", "Vivid Spores"
	requireTarget, mana = False, 4
	index = "BLACK_TEMPLE~Shaman~Spell~4~Nature~Vivid Spores"
	description = "Give your minions 'Deathrattle: Resummon this minion'"
	name_CN = "鲜活孢子"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		for minion in self.Game.minionsonBoard(self.ID):
			minion.getsTrig(ResummonThisMinion_VividSpores(minion), trigType="Deathrattle")
		return None
		
class ResummonThisMinion_VividSpores(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		#This Deathrattle can't possibly be triggered in hand
		self.entity.summon(type(self.entity)(self.entity.Game, self.entity.ID), self.entity.pos+1)
		
		
class BoggspineKnuckles(Weapon):
	Class, name, description = "Shaman", "Boggspine Knuckles", "After your hero attacks, transform your minions into ones that cost (1) more"
	mana, attack, durability = 5, 3, 2
	index = "BLACK_TEMPLE~Shaman~Weapon~5~3~2~Boggspine Knuckles"
	name_CN = "沼泽拳刺"
	poolIdentifier = "1-Cost Minions to Summon"
	@classmethod
	def generatePool(cls, pools):
		return ["%d-Cost Minions to Summon"%cost for cost in pools.MinionsofCost.keys()], \
				list(pools.MinionsofCost.values())
				
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_BoggspineKnuckles(self)]
		
class Trig_BoggspineKnuckles(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["HeroAttackedMinion", "HeroAttackedHero"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject == self.entity.Game.heroes[self.entity.ID] and self.entity.onBoard
		
	def text(self, CHN):
		return "在你的英雄攻击后，随机将你的所有随从变形成为法力值消耗增加(1)点的随从" if CHN \
				else "After your hero attacks, transform your minions into ones that cost (1) more"
				
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		weapon = self.entity
		for minion in self.entity.minionsonBoard(weapon.ID):
			cost = type(minion).mana + 1
			while "%d-Cost Minions to Summon"%cost not in weapon.Game.RNGPools:
				cost -= 1
			newMinion = npchoice(self.rngPool("%d-Cost Minions to Summon"%cost))
			weapon.transform(minion, newMinion(weapon, minion.ID))
			
			
class ShatteredRumbler(Minion):
	Class, race, name = "Shaman", "Elemental", "Shattered Rumbler"
	mana, attack, health = 5, 5, 6
	index = "BLACK_TEMPLE~Shaman~Minion~5~5~6~Elemental~Shattered Rumbler~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: If you cast a spell last turn, deal 2 damage to all other minions"
	name_CN = "破碎奔行者"
	
	def effCanTrig(self):
		cardsEachTurn = any(card.type == "Spell" for card in self.Game.Counters.cardsPlayedEachTurn[self.ID][-2])
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if any(card.type == "Spell" for card in self.Game.Counters.cardsPlayedEachTurn[self.ID][-2]):
			targets = self.Game.minionsonBoard(self.ID, self) + self.Game.minionsonBoard(3-self.ID)
			self.dealsAOE(targets, [2]*len(targets))
		return None
		
		
class TheLurkerBelow(Minion):
	Class, race, name = "Shaman", "Beast", "The Lurker Below"
	mana, attack, health = 6, 6, 5
	index = "BLACK_TEMPLE~Shaman~Minion~6~6~5~Beast~The Lurker Below~Battlecry~Legendary"
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
			self.dealsDamage(target, 3)
			minion, direction = None, ''
			if target.onBoard and (target.health < 1 or target.dead):
				neighbors, dist = self.Game.neighbors2(target)
				if dist == 1:
					if nprandint(2): minion, direction = neighbors[1], 1
					else: minion, direction = neighbors[0], 0
				elif dist < 0: minion, direction = neighbors[0], 0
				elif dist == 2: minion, direction = neighbors[0], 1
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
				else: break
		return target
		
		
"""Warlock cards"""
class ShadowCouncil(Spell):
	Class, school, name = "Warlock", "Fel", "Shadow Council"
	requireTarget, mana = False, 1
	index = "BLACK_TEMPLE~Warlock~Spell~1~Fel~Shadow Council"
	description = "Replace your hand with random Demons. Give them +2/+2"
	name_CN = "暗影议会"
	poolIdentifier = "Demons"
	@classmethod
	def generatePool(cls, pools):
		return "Demons", pools.MinionswithRace["Demon"]
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		pool = self.rngPool("Demons")
		demons = npchoice(pool, len(self.Game.Hand_Deck.hands[self.ID]), replace=True)
		self.Game.Hand_Deck.extractfromHand(None, self.ID, all=True, enemyCanSee=False)
		self.addCardtoHand(demons, self.ID)
		for demon in demons: demon.buffDebuff(2, 2)
		return None
		
		
class UnstableFelbolt(Spell):
	Class, school, name = "Warlock", "Fel", "Unstable Felbolt"
	requireTarget, mana = True, 1
	index = "BLACK_TEMPLE~Warlock~Spell~1~Fel~Unstable Felbolt"
	description = "Deal 3 damage to an enemy minion and a random friendly one"
	name_CN = "不稳定的邪能箭"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			damage = (3 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			self.dealsDamage(target, damage)
			ownMinions = self.Game.minionsonBoard(self.ID)
			if ownMinions: self.dealsDamage(npchoice(ownMinions), damage)
		return target
		
		
class ImprisonedScrapImp(Minion_Dormantfor2turns):
	Class, race, name = "Warlock", "Demon", "Imprisoned Scrap Imp"
	mana, attack, health = 2, 3, 3
	index = "BLACK_TEMPLE~Warlock~Minion~2~3~3~Demon~Imprisoned Scrap Imp"
	requireTarget, keyWord, description = False, "", "Dormant for 2 turns. When this awakens, give all minions in your hand +2/+1"
	name_CN = "被禁锢的拾荒小鬼"
	
	def awakenEffect(self):
		for card in self.Game.Hand_Deck.hands[self.ID][:]:
			if card.type == "Minion": card.buffDebuff(2, 1)
			
			
class KanrethadEbonlocke(Minion):
	Class, race, name = "Warlock", "", "Kanrethad Ebonlocke"
	mana, attack, health = 2, 3, 2
	index = "BLACK_TEMPLE~Warlock~Minion~2~3~2~~Kanrethad Ebonlocke~Deathrattle~Legendary"
	requireTarget, keyWord, description = False, "", "Your Demons cost (1) less. Deathrattle: Shuffle 'Kanrethad Prime' into your deck"
	name_CN = "坎雷萨德·埃伯洛克"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.auras["Your Demons cost (1) less"] = ManaAura(self, changeby=-1, changeto=-1)
		self.deathrattles = [ShuffleKanrethadPrimeintoYourDeck(self)]
		
	def manaAuraApplicable(self, subject): #ID用于判定是否是我方手中的随从
		return subject.ID == self.ID and subject.type == "Minion" and "Demon" in subject.race
		
class ShuffleKanrethadPrimeintoYourDeck(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		minion = self.entity
		minion.Game.Hand_Deck.shuffleintoDeck(KanrethadPrime(minion.Game, minion.ID), creator=minion)
		
	def text(self, CHN):
		return "亡语：将“终极坎雷萨德”洗入你的牌库" if CHN else "Deathrattle: Shuffle 'Kanrethad Prime' into your deck"
		
		
class KanrethadPrime(Minion):
	Class, race, name = "Warlock", "Demon", "Kanrethad Prime"
	mana, attack, health = 8, 7, 6
	index = "BLACK_TEMPLE~Warlock~Minion~8~7~6~Demon~Kanrethad Prime~Battlecry~Legendary~Uncollectible"
	requireTarget, keyWord, description = False, "", "Battlecry: Summon 3 friendly Demons that died this game"
	name_CN = "终极坎雷萨德"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		demonsDied = [card for card in self.Game.Counters.minionsDiedThisGame[self.ID] if "Demon" in card.race]
		numSummon = min(len(demonsDied), 3)	
		if numSummon:
			pos = (self.pos, "totheRight") if self.onBoard else (-1, "totheRightEnd")
			demons = npchoice(demonsDied, numSummon, replace=True)
			self.summon([demon(self.Game, self.ID) for demon in demons], pos)
		return None
		
		
class Darkglare(Minion):
	Class, race, name = "Warlock", "Demon", "Darkglare"
	mana, attack, health = 3, 3, 4
	index = "BLACK_TEMPLE~Warlock~Minion~3~3~4~Demon~Darkglare"
	requireTarget, keyWord, description = False, "", "After your hero takes damage, refresh a Mana Crystals"
	name_CN = "黑眼"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_Darkglare(self)]
		
class Trig_Darkglare(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["HeroTookDmg"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return target == self.entity.Game.heroes[self.entity.ID]
		
	def text(self, CHN):
		return "在你的英雄受到伤害后，复原一个法力水晶" if CHN else "After your hero takes damage, refresh a Mana Crystals"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.Game.Manas.restoreManaCrystal(1, self.entity.ID)
		
		
class NightshadeMatron(Minion):
	Class, race, name = "Warlock", "Demon", "Nightshade Matron"
	mana, attack, health = 4, 5, 5
	index = "BLACK_TEMPLE~Warlock~Minion~4~5~5~Demon~Nightshade Matron~Rush~Battlecry"
	requireTarget, keyWord, description = False, "Rush", "Rush. Battlecry: Discard your highest Cost card"
	name_CN = "夜影主母"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		cards, highestCost = [], -1
		for i, card in enumerate(self.Game.Hand_Deck.hands[self.ID]):
			if card.mana > highestCost: cards, highestCost = [i], card.mana
			elif card.mana == highestCost: cards.append(i)
		if cards: self.Game.Hand_Deck.discard(self.ID, npchoice(cards))
		return None
		
		
class TheDarkPortal(Spell):
	Class, school, name = "Warlock", "Fel", "The Dark Portal"
	requireTarget, mana = False, 4
	index = "BLACK_TEMPLE~Warlock~Spell~4~Fel~The Dark Portal"
	description = "Draw a minion. If you have at least 8 cards in hand, it costs (5) less"
	name_CN = "黑暗之门"
	def effCanTrig(self):
		self.effectViable = len(self.Game.Hand_Deck.hands[self.ID]) > 7
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		minions = [i for i, card in enumerate(self.Game.Hand_Deck.decks[self.ID]) if card.type == "Minion"]
		if minions:
			minion = self.Game.Hand_Deck.drawCard(self.ID, npchoice(minions))[0]
			if minion and len(self.Game.Hand_Deck.hands[self.ID]) > 7:
				ManaMod(minion, changeby=-5).applies()
		return None
		
		
class HandofGuldan(Spell):
	Class, school, name = "Warlock", "Shadow", "Hand of Gul'dan"
	requireTarget, mana = False, 6
	index = "BLACK_TEMPLE~Warlock~Spell~6~Shadow~Hand of Gul'dan"
	description = "When you play or discard this, draw 3 cards"
	name_CN = "古尔丹之手"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)

	def whenDiscarded(self):
		for i in range(3): self.Game.Hand_Deck.drawCard(self.ID)
		return None

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		for i in range(3): self.Game.Hand_Deck.drawCard(self.ID)
		return None
		
		
class KelidantheBreaker(Minion):
	Class, race, name = "Warlock", "", "Keli'dan the Breaker"
	mana, attack, health = 6, 3, 3
	index = "BLACK_TEMPLE~Warlock~Minion~6~3~3~~Keli'dan the Breaker~Battlecry~Legendary"
	requireTarget, keyWord, description = True, "", "Battlecry: Destroy a minion. If drawn this turn, instead destroy all minions except this one"
	name_CN = "击碎者克里丹"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
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
		super().__init__(entity, ["TurnEnds"])
		
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
	index = "BLACK_TEMPLE~Warlock~Minion~8~5~7~Demon~Enhanced Dreadlord~Taunt~Deathrattle"
	requireTarget, keyWord, description = False, "Taunt", "Taunt. Deathrattle: Summon a 5/5 Dreadlord with Lifesteal"
	name_CN = "改进型恐惧魔王"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.deathrattles = [SummonaDreadlordwithLifesteal(self)]
		
class SummonaDreadlordwithLifesteal(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.summon(DesperateDreadlord(self.entity.Game, self.entity.ID), self.entity.pos+1)
		
	def text(self, CHN):
		return "亡语：召唤一个5/5并具有吸血的恐惧魔王" if CHN else "Deathrattle: Summon a 5/5 Dreadlord with Lifesteal"
		
class DesperateDreadlord(Minion):
	Class, race, name = "Warlock", "Demon", "Desperate Dreadlord"
	mana, attack, health = 5, 5, 5
	index = "BLACK_TEMPLE~Warlock~Minion~5~5~5~Demon~Desperate Dreadlord~Lifesteal~Uncollectible"
	requireTarget, keyWord, description = False, "Lifesteal", "Lifesteal"
	name_CN = "绝望的恐惧魔王"
	
"""Warrior cards"""
class ImprisonedGanarg(Minion_Dormantfor2turns):
	Class, race, name = "Warrior", "Demon", "Imprisoned Gan'arg"
	mana, attack, health = 1, 2, 2
	index = "BLACK_TEMPLE~Warrior~Minion~1~2~2~Demon~Imprisoned Gan'arg"
	requireTarget, keyWord, description = False, "", "Dormant for 2 turns. When this awakens, equip a 3/2 Axe"
	name_CN = "被禁锢的 甘尔葛"
	
	def awakenEffect(self):
		self.equipWeapon(FieryWarAxe_Basic(self.Game, self.ID))
		
		
class SwordandBoard(Spell):
	Class, school, name = "Warrior", "", "Sword and Board"
	requireTarget, mana = True, 1
	index = "BLACK_TEMPLE~Warrior~Spell~1~~Sword and Board"
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
	Class, school, name = "Warrior", "", "Corsair Cache"
	requireTarget, mana = False, 2
	index = "BLACK_TEMPLE~Warrior~Spell~2~~Corsair Cache"
	description = "Draw a weapon. Give it +1 Durability"
	name_CN = "海盗藏品"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		weapons = [i for i, card in enumerate(self.Game.Hand_Deck.decks[self.ID]) if card.type == "Weapon"]
		if weapons:
			weapon = self.Game.Hand_Deck.drawCard(self.ID, npchoice(weapons))[0]
			if weapon: weapon.gainStat(0, 1)
		return None
		
		
class Bladestorm(Spell):
	Class, school, name = "Warrior", "", "Bladestorm"
	requireTarget, mana = False, 3
	index = "BLACK_TEMPLE~Warrior~Spell~3~~Bladestorm"
	description = "Deal 1 damage to all minions. Repeat until one dies"
	name_CN = "剑刃风暴"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		damage = (1 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		for i in range(14):
			targets = self.Game.minionsonBoard(1) + self.Game.minionsonBoard(2)
			if not targets: break
			else:
				targets_damaged = self.dealsAOE(targets, [damage] * len(targets))[0]
				if any(minion.health < 0 or minion.dead for minion in targets_damaged):
					break
		return None
		
		
class BonechewerRaider(Minion):
	Class, race, name = "Warrior", "", "Bonechewer Raider"
	mana, attack, health = 3, 3, 3
	index = "BLACK_TEMPLE~Warrior~Minion~3~3~3~~Bonechewer Raider~Battlecry"
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
			self.getsStatus("Rush")
		return False
		
		
#不知道与博尔夫碎盾和Blur的结算顺序
class BulwarkofAzzinoth(Weapon):
	Class, name, description = "Warrior", "Bulwark of Azzinoth", "Whenever your hero would take damage, this loses 1 Durability instead"
	mana, attack, durability = 3, 1, 4
	index = "BLACK_TEMPLE~Warrior~Weapon~3~1~4~Bulwark of Azzinoth~Legendary"
	name_CN = "埃辛诺斯壁垒"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_BulwarkofAzzinoth(self)]
		
class Trig_BulwarkofAzzinoth(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["FinalDmgonHero?"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		#Can only prevent damage if there is still durability left
		print("Testing the Bulwark of Azzinoth",  target == self.entity.Game.heroes[self.entity.ID] and self.entity.onBoard)
		print(target == self.entity.Game.heroes[self.entity.ID], self.entity.onBoard)
		return target == self.entity.Game.heroes[self.entity.ID] and self.entity.onBoard
		
	def text(self, CHN):
		return "每当你的英雄即将受到伤害，改为埃辛诺斯壁垒失去1点耐久度" if CHN \
				else "Whenever your hero would take damage, this loses 1 Durability instead"
				
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		number[0] = 0
		self.entity.loseDurability()
		
		
class WarmaulChallenger(Minion):
	Class, race, name = "Warrior", "", "Warmaul Challenger"
	mana, attack, health = 3, 1, 10
	index = "BLACK_TEMPLE~Warrior~Minion~3~1~10~~Warmaul Challenger~Battlecry"
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
				self.Game.battle(self, target, verifySelectable=False, useAttChance=False, resolveDeath=False, resetRedirTrig=False)
		return target
		
		
class KargathBladefist(Minion):
	Class, race, name = "Warrior", "", "Kargath Bladefist"
	mana, attack, health = 4, 4, 4
	index = "BLACK_TEMPLE~Warrior~Minion~4~4~4~~Kargath Bladefist~Rush~Deathrattle~Legendary"
	requireTarget, keyWord, description = False, "Rush", "Rush. Deathrattle: Shuffle 'Kargath Prime' into your deck"
	name_CN = "卡加斯刃拳"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.deathrattles = [ShuffleKargathPrimeintoYourDeck(self)]
		
class ShuffleKargathPrimeintoYourDeck(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		minion = self.entity
		minion.Game.Hand_Deck.shuffleintoDeck(KargathPrime(minion.Game, minion.ID), creator=minion)
		
	def text(self, CHN):
		return "亡语：将“终极卡加斯”洗入你的牌库" if CHN else "Deathrattle: Shuffle 'Kargath Prime' into your deck"
		
class KargathPrime(Minion):
	Class, race, name = "Warrior", "", "Kargath Prime"
	mana, attack, health = 8, 10, 10
	index = "BLACK_TEMPLE~Warrior~Minion~8~10~10~~Kargath Prime~Rush~Legendary~Uncollectible"
	requireTarget, keyWord, description = False, "Rush", "Rush. Whenever this attacks and kills a minion, gain 10 Armor"
	name_CN = "终极卡加斯"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_KargathPrime(self)]
		
class Trig_KargathPrime(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["MinionAttackedMinion"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject == self.entity and self.entity.onBoard and (target.health < 1 or target.dead == True)
		
	def text(self, CHN):
		return "每当该随从攻击并消灭一个随从时，获得10点护甲值" if CHN else "Whenever this attacks and kills a minion, gain 10 Armor"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.Game.heroes[self.entity.ID].gainsArmor(10)
		
		
class ScrapGolem(Minion):
	Class, race, name = "Warrior", "Mech", "Scrap Golem"
	mana, attack, health = 5, 4, 5
	index = "BLACK_TEMPLE~Warrior~Minion~5~4~5~Mech~Scrap Golem~Taunt~Deathrattle"
	requireTarget, keyWord, description = False, "Taunt", "Taunt. Deathrattle: Gain Armor equal to this minion's Attack"
	name_CN = "废铁魔像"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.deathrattles = [GainArmorEqualtoAttack(self)]
		
class GainArmorEqualtoAttack(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.Game.heroes[self.entity.ID].gainsArmor(number)
		
	def text(self, CHN):
		return "亡语：获得等同于该随从攻击力的护甲值" if CHN else "Deathrattle: Gain Armor equal to this minion's Attack"
		
		
class BloodboilBrute(Minion):
	Class, race, name = "Warrior", "", "Bloodboil Brute"
	mana, attack, health = 7, 5, 8
	index = "BLACK_TEMPLE~Warrior~Minion~7~5~8~~Bloodboil Brute~Rush"
	requireTarget, keyWord, description = False, "Rush", "Rush. Costs (1) less for each damaged minion"
	name_CN = "沸血蛮兵"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
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
		super().__init__(entity, ["MinionAppears", "MinionDisappears", "MinionTakesDmg"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.inHand
		
	def text(self, CHN):
		return "每当受伤随从的数量变化，重新计算该随从的费用" if CHN \
				else "When number of damaged minions change, recalculate mana"
				
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.Game.Manas.calcMana_Single(self.entity)
		
		
		
		
Outlands_Cards = [#Neutral cards
				EtherealAugmerchant, GuardianAugmerchant, InfectiousSporeling, RocketAugmerchant, SoulboundAshtongue, BonechewerBrawler, ImprisonedVilefiend, MoargArtificer, RustswornInitiate, Impcaster, BlisteringRot, LivingRot, 
				FrozenShadoweaver, OverconfidentOrc, TerrorguardEscapee, Huntress, TeronGorefiend, BurrowingScorpid, DisguisedWanderer, RustswornInquisitor, FelfinNavigator, Magtheridon, HellfireWarder, MaievShadowsong, Replicatotron, 
				RustswornCultist, RustedDevil, Alar, AshesofAlar, RuststeedRaider, WasteWarden, DragonmawSkyStalker, Dragonrider, ScavengingShivarra, BonechewerVanguard, KaelthasSunstrider, SupremeAbyssal, ScrapyardColossus, FelcrackedColossus, 
				#Demon Hunter cards
				FuriousFelfin, ImmolationAura, Netherwalker, FelSummoner, KaynSunfury, Metamorphosis, ImprisonedAntaen, SkullofGuldan, PriestessofFury, CoilfangWarlord, ConchguardWarlord, PitCommander, 
				#Druid cards
				FungalFortunes, Ironbark, ArchsporeMsshifn, MsshifnPrime, FungalGuardian, FungalBruiser, FungalGargantuan, Bogbeam, ImprisonedSatyr, Germination, Overgrowth, GlowflySwarm, Glowfly, MarshHydra, YsielWindsinger, 
				#Hunter cards
				Helboar, ImprisonedFelmaw, PackTactics, ScavengersIngenuity, AugmentedPorcupine, ZixorApexPredator, ZixorPrime, MokNathalLion, ScrapShot, BeastmasterLeoroxx, NagrandSlam, Clefthoof, 
				#Mage cards
				Evocation, FontofPower, ApexisSmuggler, AstromancerSolarian, SolarianPrime, IncantersFlow, Starscryer, ImprisonedObserver, NetherwindPortal, ApexisBlast, DeepFreeze, 
				#Paladin cards
				ImprisonedSungill, SungillStreamrunner, AldorAttendant, HandofAdal, MurgurMurgurgle, MurgurglePrime, LibramofWisdom, UnderlightAnglingRod, AldorTruthseeker, LibramofJustice, OverdueJustice, LadyLiadrin, LibramofHope, AncientGuardian, 
				#Priest cards
				ImprisonedHomunculus, ReliquaryofSouls, ReliquaryPrime, Renew, DragonmawSentinel, SethekkVeilweaver, Apotheosis, DragonmawOverseer, PsycheSplit, SkeletalDragon, SoulMirror, 
				#Rogue cards
				BlackjackStunner, Spymistress, Ambush, BrokenAmbusher, AshtongueSlayer, Bamboozle, DirtyTricks, ShadowjewelerHanar, Akama, AkamaPrime, GreyheartSage, CursedVagrant, CursedShadow, 
				#Shaman cards
				BogstrokClacker, LadyVashj, VashjPrime, Marshspawn, SerpentshrinePortal, TotemicReflection, VividSpores, BoggspineKnuckles, ShatteredRumbler, Torrent, TheLurkerBelow, 
				#Warlock cards
				ShadowCouncil, UnstableFelbolt, ImprisonedScrapImp, KanrethadEbonlocke, KanrethadPrime, Darkglare, NightshadeMatron, TheDarkPortal, HandofGuldan, KelidantheBreaker, EnhancedDreadlord, DesperateDreadlord, 
				#Warrior cards
				ImprisonedGanarg, SwordandBoard, CorsairCache, Bladestorm, BonechewerRaider, BulwarkofAzzinoth, WarmaulChallenger, KargathBladefist, KargathPrime, ScrapGolem, BloodboilBrute,
				]
				
Outlands_Cards_Collectible = [#Neutral
							EtherealAugmerchant, GuardianAugmerchant, InfectiousSporeling, RocketAugmerchant, SoulboundAshtongue, BonechewerBrawler, ImprisonedVilefiend, MoargArtificer, RustswornInitiate, BlisteringRot, FrozenShadoweaver,
							OverconfidentOrc, TerrorguardEscapee, TeronGorefiend, BurrowingScorpid, DisguisedWanderer, FelfinNavigator, Magtheridon, MaievShadowsong, Replicatotron, RustswornCultist, Alar, RuststeedRaider, WasteWarden,
							DragonmawSkyStalker, ScavengingShivarra, BonechewerVanguard, KaelthasSunstrider, SupremeAbyssal, ScrapyardColossus,
							#Demon Hunter
							FuriousFelfin, ImmolationAura, Netherwalker, FelSummoner, KaynSunfury, Metamorphosis, ImprisonedAntaen, SkullofGuldan, PriestessofFury, CoilfangWarlord, PitCommander,
							#Druid
							FungalFortunes, Ironbark, ArchsporeMsshifn, Bogbeam, ImprisonedSatyr, Germination, Overgrowth, GlowflySwarm, MarshHydra, YsielWindsinger,
							#Hunter
							Helboar, ImprisonedFelmaw, PackTactics, ScavengersIngenuity, AugmentedPorcupine, ZixorApexPredator, MokNathalLion, ScrapShot, BeastmasterLeoroxx, NagrandSlam,
							#Mage
							Evocation, FontofPower, ApexisSmuggler, AstromancerSolarian, IncantersFlow, Starscryer, ImprisonedObserver, NetherwindPortal, ApexisBlast, DeepFreeze,
							#Paladin
							ImprisonedSungill, AldorAttendant, HandofAdal, MurgurMurgurgle, LibramofWisdom, UnderlightAnglingRod, AldorTruthseeker, LibramofJustice, LadyLiadrin, LibramofHope,
							#Priest
							ImprisonedHomunculus, ReliquaryofSouls, Renew, DragonmawSentinel, SethekkVeilweaver, Apotheosis, DragonmawOverseer, PsycheSplit, SkeletalDragon, SoulMirror,
							#Rogue
							BlackjackStunner, Spymistress, Ambush, AshtongueSlayer, Bamboozle, DirtyTricks, ShadowjewelerHanar, Akama, GreyheartSage, CursedVagrant,
							#Shaman
							BogstrokClacker, LadyVashj, Marshspawn, SerpentshrinePortal, TotemicReflection, VividSpores, BoggspineKnuckles, ShatteredRumbler, Torrent, TheLurkerBelow,
							#Warlock
							ShadowCouncil, UnstableFelbolt, ImprisonedScrapImp, KanrethadEbonlocke, Darkglare, NightshadeMatron, TheDarkPortal, HandofGuldan, KelidantheBreaker, EnhancedDreadlord,
							#Warrior
							ImprisonedGanarg, SwordandBoard, CorsairCache, Bladestorm, BonechewerRaider, BulwarkofAzzinoth, WarmaulChallenger, KargathBladefist, ScrapGolem, BloodboilBrute,
							]