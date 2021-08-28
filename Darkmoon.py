from CardTypes import *
from Triggers_Auras import *
from numpy.random import choice as npchoice
from numpy.random import randint as nprandint
from numpy.random import shuffle as npshuffle
from numpy import inf as npinf
from collections import Counter as cnt

from AcrossPacks import Bananas, IllidariInitiate, Huffer, Leokk, Misha, SilverHandRecruit, Pyroblast
from Outlands import Minion_Dormantfor2turns, MsshifnPrime, ZixorPrime, SolarianPrime, MurgurglePrime, ReliquaryPrime, \
					AkamaPrime, VashjPrime, KanrethadPrime, KargathPrime
from Academy import SoulFragment, Spellburst

import copy

"""Madness at the Darkmoon Faire"""

"""Mana 1 cards"""
class SafetyInspector(Minion):
	Class, race, name = "Neutral", "", "Safety Inspector"
	mana, attack, health = 1, 1, 3
	index = "DARKMOON_FAIRE~Neutral~Minion~1~1~3~~Safety Inspector~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Shuffle the lowest-Cost card from your hand into your deck. Draw a card"
	name_CN = "安全检查员"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		cards, lowestCost = [], npinf
		for i, card in enumerate(self.Game.Hand_Deck.hands[self.ID]):
			if card.mana < lowestCost: cards, lowestCost = [i], card.mana
			elif card.mana == lowestCost: cards.append(i)
		if cards: self.Game.Hand_Deck.shuffle_Hand2Deck(npchoice(cards), ID=self.ID, initiatorID=self.ID, all=False)
		#Assume that player draws even if no card is shuffled
		self.Game.Hand_Deck.drawCard(self.ID)
		return None
		
		
"""Mana 2 cards"""
class CostumedEntertainer(Minion):
	Class, race, name = "Neutral", "", "Costumed Entertainer"
	mana, attack, health = 2, 1, 2
	index = "DARKMOON_FAIRE~Neutral~Minion~2~1~2~~Costumed Entertainer~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Give a random minion in your hand +2/+2"
	name_CN = "盛装演员"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		minions = [i for i, card in enumerate(self.Game.Hand_Deck.hands[self.ID]) if card.type == "Minion"]
		if minions: npchoice(minions).buffDebuff(2, 2)
		return None
		
		
class HorrendousGrowth(Minion):
	Class, race, name = "Neutral", "", "Horrendous Growth"
	mana, attack, health = 2, 2, 2
	index = "DARKMOON_FAIRE~Neutral~Minion~2~2~2~~Horrendous Growth~ToCorrupt"
	requireTarget, keyWord, description = False, "", "Corrupt: Gain +1/+1. Can be Corrupted endlessly"
	name_CN = "恐怖增生体"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsHand = [Trig_Corrupt(self, HorrendousGrowthCorrupt)] #只有在手牌中才会升级
		
class HorrendousGrowthCorrupt(Minion):
	Class, race, name = "Neutral", "", "Horrendous Growth"
	mana, attack, health = 2, 3, 3
	index = "DARKMOON_FAIRE~Neutral~Minion~2~3~3~~Horrendous Growth~ToCorrupt~Corrupted~Uncollectible"
	requireTarget, keyWord, description = False, "", "Corrupt: Gain +1/+1. Can be Corrupted endlessly"
	name_CN = "恐怖增生体"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsHand = [Trig_EndlessCorrupt(self)] #只有在手牌中才会升级
		
class Trig_EndlessCorrupt(TrigHand):
	def __init__(self, entity):
		super().__init__(entity, ["ManaPaid"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.inHand and ID == self.entity.ID and number > self.entity.mana and subject.type != "Power"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		card = self.entity
		stat = int(type(card).__name__.split('_')[-1]) + 1
		newIndex = "DARKMOON_FAIRE~Neutral~2~%d~%d~Minion~~Horrendous Growth~Corrupted~Uncollectible"%(stat, stat)
		subclass = type("HorrendousGrowthCorrupt__"+str(stat), (HorrendousGrowthCorrupt, ),
						{"attack": stat, "health": stat, "index": newIndex}
						)
		#The buffs on the cards carry over
		newCard = subclass(card.Game, card.ID)
		#Buff and mana effects, etc, will be preserved
		#Buff to cards in hand will always be permanent or temporary, not from Auras
		#Temporary attack changes on minions are NOT included in attack_Enchant
		attBuff, healthBuff = card.attack_Enchant - card.attack_0, card.health_max - card.health_0
		newCard.buffDebuff(attBuff, healthBuff)
		for attGain, attRevertTime in card.tempAttChanges:
			newCard.buffDebuff(attGain, 0, attRevertTime)
		#Find keywords the new card doesn't have
		keyWords = newCard.keyWords.keys()
		#Since the Horrendous Growth has no predefined keywords, it can simply copy the predecessors
		newCard.keyWords, newCard.marks = copy.deepcopy(card.keyWords), copy.deepcopy(card.marks)
		newCard.trigsHand += [trig for trig in card.trigsHand if not isinstance(trig, Trig_EndlessCorrupt)]
		#There are no Corrupted cards with predefined Deathrattles
		newCard.deathrattles = [type(deathrattle)(newCard) for deathrattle in card.deathrattles]
		#Mana modifications
		newCard.manaMods = [manaMod.selfCopy(newCard) for manaMod in card.manaMods]
		
		card.Game.Hand_Deck.replaceCardinHand(card, newCard)
		
		
class ParadeLeader(Minion):
	Class, race, name = "Neutral", "", "Parade Leader"
	mana, attack, health = 2, 2, 3
	index = "DARKMOON_FAIRE~Neutral~Minion~2~2~3~~Parade Leader"
	requireTarget, keyWord, description = False, "", "After you summon a Rush minion, give it +2 Attack"
	name_CN = "巡游领队"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_ParadeLeader(self)] #只有在手牌中才会升级
		
class Trig_ParadeLeader(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["MinionBeenSummoned"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject.ID == self.entity.ID and subject != self.entity and subject.keyWords["Rush"] > 0
		
	def text(self, CHN):
		return "在你召唤一个突袭随从后，使其获得+2攻击力" if CHN else "After you summon a Rush minion, give it +2 Attack"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		subject.buffDebuff(2, 0)
		
		
class PrizeVendor(Minion):
	Class, race, name = "Neutral", "Murloc", "Prize Vendor"
	mana, attack, health = 2, 2, 3
	index = "DARKMOON_FAIRE~Neutral~Minion~2~2~3~Murloc~Prize Vendor~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Both players draw a card"
	name_CN = "奖品商贩"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.Game.Hand_Deck.drawCard(self.ID)
		self.Game.Hand_Deck.drawCard(3-self.ID)
		return None
		
		
class RockRager(Minion):
	Class, race, name = "Neutral", "Elemental", "Rock Rager"
	mana, attack, health = 2, 5, 1
	index = "DARKMOON_FAIRE~Neutral~Minion~2~5~1~Elemental~Rock Rager~Taunt"
	requireTarget, keyWord, description = False, "Taunt", "Taunt"
	name_CN = "岩石暴怒者"
	
	
class Showstopper(Minion):
	Class, race, name = "Neutral", "", "Showstopper"
	mana, attack, health = 2, 3, 2
	index = "DARKMOON_FAIRE~Neutral~Minion~2~3~2~~Showstopper~Deathrattle"
	requireTarget, keyWord, description = False, "", "Deathrattle: Silence all minions"
	name_CN = "砸场游客"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.deathrattles = [SilenceAllMinions(self)]
		
class SilenceAllMinions(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		curGame = self.entity.Game
		for minion in curGame.minionsonBoard(1) + curGame.minionsonBoard(2):
			minion.getsSilenced()
			
	def text(self, CHN):
		return "亡语：沉默所有随从" if CHN else "Deathrattle: Silence all minions"
		
		
class WrigglingHorror(Minion):
	Class, race, name = "Neutral", "", "Wriggling Horror"
	mana, attack, health = 2, 2, 1
	index = "DARKMOON_FAIRE~Neutral~Minion~2~2~1~~Wriggling Horror~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Give adjacent minions +1/+1"
	name_CN = "蠕动的恐魔"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if self.onBoard:
			for minion in self.Game.neighbors2(self)[0]:
				minion.buffDebuff(1, 1)
		return None
		
		
"""Mana 3 cards"""
class BananaVendor(Minion):
	Class, race, name = "Neutral", "", "Banana Vendor"
	mana, attack, health = 3, 2, 4
	index = "DARKMOON_FAIRE~Neutral~Minion~3~2~4~~Banana Vendor~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Add 2 Bananas to each player's hand"
	name_CN = "香蕉商贩"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.addCardtoHand([Bananas, Bananas], self.ID)
		self.addCardtoHand([Bananas, Bananas], 3-self.ID)
		return None
		
		
class DarkmoonDirigible(Minion):
	Class, race, name = "Neutral", "Mech", "Darkmoon Dirigible"
	mana, attack, health = 3, 3, 2
	index = "DARKMOON_FAIRE~Neutral~Minion~3~3~2~Mech~Darkmoon Dirigible~Divine Shield~ToCorrupt"
	requireTarget, keyWord, description = False, "Divine Shield", "Divine Shield. Corrupt: Gain Rush"
	name_CN = "暗月飞艇"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsHand = [Trig_Corrupt(self, DarkmoonDirigible_Corrupt)] #只有在手牌中才会升级
		
class DarkmoonDirigible_Corrupt(Minion):
	Class, race, name = "Paladin", "Mech", "Darkmoon Dirigible"
	mana, attack, health = 3, 3, 2
	index = "DARKMOON_FAIRE~Neutral~Minion~3~3~2~Mech~Darkmoon Dirigible~Divine Shield~Rush~Corrupted~Uncollectible"
	requireTarget, keyWord, description = False, "Divine Shield,Rush", "Corrupted. Divine Shield, Rush"
	name_CN = "暗月飞艇"
	
	
class DarkmoonStatue(Minion):
	Class, race, name = "Neutral", "", "Darkmoon Statue"
	mana, attack, health = 3, 0, 5
	index = "DARKMOON_FAIRE~Neutral~Minion~3~0~5~~Darkmoon Statue~ToCorrupt"
	requireTarget, keyWord, description = False, "", "Your other minions have +1 Attack. Corrupt: This gains +4 Attack"
	name_CN = "暗月雕像"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsHand = [Trig_Corrupt(self, DarkmoonStatue_Corrupt)] #只有在手牌中才会升级
		self.auras["Your other minions have +1 Attack"] = StatAura_Others(self, 1, 0)
		
class DarkmoonStatue_Corrupt(Minion):
	Class, race, name = "Paladin", "", "Darkmoon Statue"
	mana, attack, health = 3, 4, 5
	index = "DARKMOON_FAIRE~Neutral~Minion~3~4~5~~Darkmoon Statue~Corrupted~Uncollectible"
	requireTarget, keyWord, description = False, "", "Corrupted. Your other minions have +1 Attack"
	name_CN = "暗月雕像"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.auras["Your other minions have +1 Attack"] = StatAura_Others(self, 1, 0)
		
		
class Gyreworm(Minion):
	Class, race, name = "Neutral", "Elemental", "Gyreworm"
	mana, attack, health = 3, 3, 2
	index = "DARKMOON_FAIRE~Neutral~Minion~3~3~2~Elemental~Gyreworm~Battlecry"
	requireTarget, keyWord, description = True, "", "Battlecry: If you played an Elemental last turn, deal 3 damage"
	name_CN = "旋岩虫"
	def returnTrue(self, choice=0):
		return self.Game.Counters.numElementalsPlayedLastTurn[self.ID] > 0
		
	def effCanTrig(self):
		self.effectViable = self.Game.Counters.numElementalsPlayedLastTurn[self.ID] > 0
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target and self.Game.Counters.numElementalsPlayedLastTurn[self.ID] > 0:
			self.dealsDamage(target, 3)
		return target
		
		
class InconspicuousRider(Minion):
	Class, race, name = "Neutral", "", "Inconspicuous Rider"
	mana, attack, health = 3, 2, 2
	index = "DARKMOON_FAIRE~Neutral~Minion~3~2~2~~Inconspicuous Rider~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Cast a Secret from your deck"
	name_CN = "低调的游客"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.Game.Secrets.deploySecretsfromDeck(self.ID)
		return None
		
		
class KthirRitualist(Minion):
	Class, race, name = "Neutral", "", "K'thir Ritualist"
	mana, attack, health = 3, 4, 4
	index = "DARKMOON_FAIRE~Neutral~Minion~3~4~4~~K'thir Ritualist~Taunt~Battlecry"
	requireTarget, keyWord, description = False, "Taunt", "Taunt. Battlecry: Add a random 4-Cost minion to your opponent's hand"
	name_CN = "克熙尔祭师"
	poolIdentifier = "4-Cost Minions"
	@classmethod
	def generatePool(cls, pools):
		return "4-Cost Minions", pools.MinionsofCost[4]
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.addCardtoHand(npchoice(self.rngPool("4-Cost Minions")), 3-self.ID)
		return None
		
"""Mana 4 cards"""
class CircusAmalgam(Minion):
	Class, race, name = "Neutral", "Elemental,Mech,Demon,Murloc,Dragon,Beast,Pirate,Quilboar,Totem", "Circus Amalgam"
	mana, attack, health = 4, 4, 5
	index = "DARKMOON_FAIRE~Neutral~Minion~4~4~5~Elemental,Mech,Demon,Murloc,Dragon,Beast,Pirate,Quilboar,Totem~Circus Amalgam~Taunt"
	requireTarget, keyWord, description = False, "Taunt", "Taunt. This has all minion types"
	name_CN = "马戏团融合怪"
	
	
class CircusMedic(Minion):
	Class, race, name = "Neutral", "", "Circus Medic"
	mana, attack, health = 4, 3, 4
	index = "DARKMOON_FAIRE~Neutral~Minion~4~3~4~~Circus Medic~Battlecry~ToCorrupt"
	requireTarget, keyWord, description = True, "", "Battlecry: Restore 4 Health. Corrupt: Deal 4 damage instead"
	name_CN = "马戏团医师"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsHand = [Trig_Corrupt(self, CircusMedic_Corrupt)] #只有在手牌中才会升级
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			heal = 4 * (2 ** self.countHealDouble())
			self.restoresHealth(target, heal)
		return target
		
class CircusMedic_Corrupt(Minion):
	Class, race, name = "Neutral", "", "Circus Medic"
	mana, attack, health = 4, 3, 4
	index = "DARKMOON_FAIRE~Neutral~Minion~4~3~4~~Circus Medic~Battlecry~Corrupted~Uncollectible"
	requireTarget, keyWord, description = True, "", "Corrupted. Battlecry: Deal 4 damage"
	name_CN = "马戏团医师"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			self.dealsDamage(target, 4)
		return target
		
		
class FantasticFirebird(Minion):
	Class, race, name = "Neutral", "Elemental", "Fantastic Firebird"
	mana, attack, health = 4, 3, 5
	index = "DARKMOON_FAIRE~Neutral~Minion~4~3~5~Elemental~Fantastic Firebird~Windfury"
	requireTarget, keyWord, description = False, "Windfury", "Windfury"
	name_CN = "炫目火鸟"
	
	
class KnifeVendor(Minion):
	Class, race, name = "Neutral", "", "Knife Vendor"
	mana, attack, health = 4, 3, 4
	index = "DARKMOON_FAIRE~Neutral~Minion~4~3~4~~Knife Vendor~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Deal 4 damage to each hero"
	name_CN = "小刀商贩"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.dealsAOE([self.Game.heroes[1], self.Game.heroes[2]], [4, 4])
		return None
		
"""Mana 5 cards"""
class DerailedCoaster(Minion):
	Class, race, name = "Neutral", "", "Derailed Coaster"
	mana, attack, health = 5, 3, 2
	index = "DARKMOON_FAIRE~Neutral~Minion~5~3~2~~Derailed Coaster~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Summon a 1/1 Rider with Rush for each minion in your hand"
	name_CN = "脱轨过山车"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		num = sum(card.type == "Minion" for card in self.Game.Hand_Deck.hands[self.ID])
		if num: self.summon([DarkmoonRider(self.Game, self.ID) for i in range(num)], (self.pos, "totheRight"))
		return None
		
class DarkmoonRider(Minion):
	Class, race, name = "Neutral", "", "Darkmoon Rider"
	mana, attack, health = 1, 1, 1
	index = "DARKMOON_FAIRE~Neutral~Minion~1~1~1~~Darkmoon Rider~Rush~Uncollectible"
	requireTarget, keyWord, description = False, "Rush", "Rush"
	name_CN = "暗月乘客"
	
#Assume corrupted card don't inherit any buff/debuff
#Assume transformation happens when card is played
class FleethoofPearltusk(Minion):
	Class, race, name = "Neutral", "Beast", "Fleethoof Pearltusk"
	mana, attack, health = 5, 4, 4
	index = "DARKMOON_FAIRE~Neutral~Minion~5~4~4~Beast~Fleethoof Pearltusk~Rush~ToCorrupt"
	requireTarget, keyWord, description = False, "Rush", "Rush. Corrupt: Gain +4/+4"
	name_CN = "迅蹄珠齿象"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsHand = [Trig_Corrupt(self, FleethoofPearltusk_Corrupt)] #只有在手牌中才会升级
		
class FleethoofPearltusk_Corrupt(Minion):
	Class, race, name = "Neutral", "Beast", "Fleethoof Pearltusk"
	mana, attack, health = 5, 8, 8
	index = "DARKMOON_FAIRE~Neutral~Minion~5~8~8~Beast~Fleethoof Pearltusk~Rush~Corrupted~Uncollectible"
	requireTarget, keyWord, description = False, "Rush", "Rush"
	name_CN = "迅蹄珠齿象"
	
	
class OptimisticOgre(Minion):
	Class, race, name = "Neutral", "", "Optimistic Ogre"
	mana, attack, health = 5, 6, 7
	index = "DARKMOON_FAIRE~Neutral~Minion~5~6~7~~Optimistic Ogre"
	requireTarget, keyWord, description = False, "", "50% chance to attack the correct enemy"
	name_CN = "乐观的食人魔"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_OptimisticOgre(self)]
		
class Trig_OptimisticOgre(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["MinionAttacksMinion", "MinionAttacksHero", "BattleFinished"])
		self.trigedThisBattle = False
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		#The trigger can be reset any time by "BattleFinished".
		#Otherwise, can only trigger if there are enemies other than the target.
		#游荡怪物配合误导可能会将对英雄的攻击目标先改成对召唤的随从，然后再发回敌方英雄，说明攻击一个错误的敌人应该也是游戏现记录的目标之外的角色。
		return not signal.startswith("Minion") or (subject == self.entity and self.entity.onBoard and target[1] and not self.trigedThisBattle \
													and self.entity.Game.charsAlive(3-subject.ID, target[1]) \
													)
													
	def trig(self, signal, ID, subject, target, number, comment, choice=0):
		if self.entity.onBoard:
			if signal == "BattleFinished": #Reset the Forgetful for next battle event.
				self.trigedThisBattle = False
			elif target: #Attack signal
				game = self.entity.Game
				char, redirect = None, 0
				otherEnemies = game.charsAlive(3- self.entity.ID, target[1])
				if otherEnemies:
					char, redirect = npchoice(otherEnemies), nprandint(2)
					if char and redirect: #Redirect is 0/1, indicating whether the attack will redirect or not
						#玩家命令的一次攻击中只能有一次触发机会。只要满足进入50%判定的条件，即使没有最终生效，也不能再次触发。
						if game.GUI: game.GUI.trigBlink(self.entity)
						target[1], self.trigedThisBattle = char, True
						
"""Mana 6 cards"""
class ClawMachine(Minion):
	Class, race, name = "Neutral", "Mech", "Claw Machine"
	mana, attack, health = 6, 6, 3
	index = "DARKMOON_FAIRE~Neutral~Minion~6~6~3~Mech~Claw Machine~Rush~Deathrattle"
	requireTarget, keyWord, description = False, "Rush", "Rush. Deathrattle: Draw a minion and give it +3/+3"
	name_CN = "娃娃机"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.deathrattles = [DrawaMinion_GiveitPlus3Plus3(self)]
		
class DrawaMinion_GiveitPlus3Plus3(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		minions = [i for i, card in enumerate(self.entity.Game.Hand_Deck.decks[self.entity.ID]) if card.type == "Minion"]
		if minions:
			minion = self.entity.Game.Hand_Deck.drawCard(self.entity.ID, npchoice(minions))[0]
			if minion: minion.buffDebuff(3, 3)
				
	def text(self, CHN):
		return "亡语：抽一张随从牌并使其获得+3/+3" if CHN else "Deathrattle: Draw a minion and give it +3/+3"
		
"""Mana 7 cards"""
class SilasDarkmoon(Minion):
	Class, race, name = "Neutral", "", "Silas Darkmoon"
	mana, attack, health = 7, 4, 4
	index = "DARKMOON_FAIRE~Neutral~Minion~7~4~4~~Silas Darkmoon~Battlecry~Legendary"
	requireTarget, keyWord, description = False, "", "Battlecry: Choose a direction to rotate all minions"
	name_CN = "希拉斯暗月"
	
	def prepMinionstoSwap(self, minions):
		for minion in minions:
			if minion:
				minion.disappears(deathrattlesStayArmed=False)
				self.Game.minions[minion.ID].remove(minion)
				minion.ID = 3 - minion.ID
				
	def swappedMinionsAppear(self, minions):
		self.Game.sortPos()
		#假设归还或者是控制对方随从的时候会清空所有暂时控制的标志，并取消回合结束归还随从的扳机
		for minion in minions:
			if minion:
				minion.appears(firstTime=False) #Swapped Imprisoned minions won't go Dormant
				minion.status["Borrowed"] = 0
				for trig in reversed(minion.trigsBoard):
					if isinstance(trig, Trig_Borrow):
						trig.disconnect()
						minion.trigsBoard.remove(trig)
				minion.afterSwitchSide(activity="Permanent")
				
	def rotateAllMinions(self, perspectiveID=1, giveOwnLeft=True):
		miniontoGive, miniontoTake = None, None
		ownMinions = self.Game.minionsonBoard(perspectiveID)
		enemyMinions = self.Game.minionsonBoard(3-perspectiveID)
		if giveOwnLeft: ownIndex, enemyIndex = 0, -1  #Give your leftmost and take enemy's rightmost
		else: ownIndex, enemyIndex = -1, 0 #Give your rightmost and take enemy's leftmost
		if ownMinions: miniontoGive = self.Game.minions[perspectiveID][ownMinions[ownIndex].pos]
		if enemyMinions: miniontoTake = self.Game.minions[3-perspectiveID][enemyMinions[enemyIndex].pos]
		
		self.prepMinionstoSwap([miniontoGive, miniontoTake])
		if giveOwnLeft: #Add minions to your rightmost and enemy's leftmost
			self.Game.minions[perspectiveID].append(miniontoTake)
			self.Game.minions[3-perspectiveID].insert(0, miniontoGive)
		else: #Add minions to your leftmost and enemy's rightmost
			self.Game.minions[perspectiveID].insert(0, miniontoTake)
			self.Game.minions[3-perspectiveID].append(miniontoGive)
		self.swappedMinionsAppear([miniontoGive, miniontoTake])
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.chooseFixedOptions(SilasDarkmoon, comment,
								options=[RotateThisWay(ID=self.ID), RotateThatWay(ID=self.ID)])
		return None
	
	#RotateThisWay give your leftmost minion
	def discoverDecided(self, option, case, info_RNGSync=None, info_GUISync=None):
		optionType = type(option)
		if case != "Guided":
			self.Game.picks.append((info_RNGSync, info_GUISync, case == "Random", optionType) )
		SilasDarkmoon.rotateAllMinions(self, perspectiveID=self.ID, giveOwnLeft=optionType == RotateThisWay)
		
class RotateThisWay(Option):
	name, description = "Rotate This Way", "Give your LEFTMOST minion"
	index = ""
	mana, attack, health = 0, -1, -1
	
class RotateThatWay(Option):
	name, description = "Rotate That Way", "Give your RIGHTMOST minion"
	index = ""
	mana, attack, health = 0, -1, -1
	
		
class Strongman(Minion):
	Class, race, name = "Neutral", "", "Strongman"
	mana, attack, health = 7, 6, 6
	index = "DARKMOON_FAIRE~Neutral~Minion~7~6~6~~Strongman~Taunt~ToCorrupt"
	requireTarget, keyWord, description = False, "Taunt", "Taunt. Corrupt: This costs (0)"
	name_CN = "大力士"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsHand = [Trig_Corrupt(self, Strongman_Corrupt)] #只有在手牌中才会升级
		
class Strongman_Corrupt(Minion):
	Class, race, name = "Neutral", "", "Strongman"
	mana, attack, health = 0, 6, 6
	index = "DARKMOON_FAIRE~Neutral~Minion~0~6~6~~Strongman~Taunt~Corrupted~Uncollectible"
	requireTarget, keyWord, description = False, "Taunt", "Corrupted. Taunt"
	name_CN = "大力士"
	
	
"""Mana 9 cards"""
class CarnivalClown(Minion):
	Class, race, name = "Neutral", "", "Carnival Clown"
	mana, attack, health = 9, 4, 4
	index = "DARKMOON_FAIRE~Neutral~Minion~9~4~4~~Carnival Clown~Taunt~Battlecry~ToCorrupt"
	requireTarget, keyWord, description = False, "Taunt", "Taunt. Battlecry: Summon 2 copies of this. Corrupted: Fill your board with copies"
	name_CN = "狂欢小丑"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsHand = [Trig_Corrupt(self, CarnivalClown_Corrupt)] #只有在手牌中才会升级
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		#假设已经死亡时不会召唤复制
		if self.onBoard or self.inDeck:
			copies = [self.selfCopy(self.ID, self) for i in range(2)]
			pos = (self.pos, "leftandRight") if self.onBoard else (-1, "totheRightEnd")
			self.summon(copies, pos)
		return None
		
class CarnivalClown_Corrupt(Minion):
	Class, race, name = "Neutral", "", "Carnival Clown"
	mana, attack, health = 9, 4, 4
	index = "DARKMOON_FAIRE~Neutral~Minion~9~4~4~~Carnival Clown~Taunt~Battlecry~Corrupted~Uncollectible"
	requireTarget, keyWord, description = False, "Taunt", "Corrupted. Taunt. Battlecry: Fill your board with copies of this"
	name_CN = "狂欢小丑"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		#假设已经死亡时不会召唤复制
		if self.onBoard:
			copies = [self.selfCopy(self.ID, self) for i in range(6)]
			self.summon(copies, (self.pos, "leftandRight"))
		else:
			copies = [self.selfCopy(self.ID, self) for i in range(7)]
			self.summon(copies, (-1, "totheRightEnd"))
		return None
		
"""Mana 10 cards"""
#Assume one can get CThun as long as pieces are played, even if it didn't start in their deck
class Trig_CThun:
	def __init__(self, Game, ID):
		self.Game, self.ID = Game, ID
		self.pieces = ["Body", "Eye", "Heart", "Maw"]
		self.card = CThuntheShattered(Game, ID)
		
	def connect(self):
		try: self.Game.trigsBoard[self.ID]["CThunPiece"].append(self)
		except: self.Game.trigsBoard[self.ID]["CThunPiece"] = [self]
		
	def disconnect(self):
		try: self.Game.trigsBoard[self.ID]["CThunPiece"].remove(self)
		except: pass
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return ID == self.ID
		
	def trig(self, signal, ID, subject, target, number, comment, choice=0):
		if self.canTrig(signal, ID, subject, target, number, comment):
			GUI = self.Game.GUI
			if self.Game.GUI: self.Game.GUI.showOffBoardTrig(self.card,
										 followCurve=False, text2Show='%d/4'%(4-len(self.pieces)), textY=-2)
			self.effect(signal, ID, subject, target, number, comment)
			
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		if ID == self.ID and number not in self.pieces:
			try: self.pieces.remove(comment)
			except: pass
			if not self.pieces:
				self.Game.Hand_Deck.shuffleintoDeck(self.card)
				self.disconnect()
				
	def createCopy(self, game): #不是纯的只在回合结束时触发，需要完整的createCopy
		if self not in game.copiedObjs: #这个扳机没有被复制过
			trigCopy = type(self)(game, self.ID)
			trigCopy.pieces = [s for s in self.pieces]
			game.copiedObjs[self] = trigCopy
			return trigCopy
		else: #一个扳机被复制过了，则其携带者也被复制过了
			return game.copiedObjs[self]
			
class BodyofCThun(Spell):
	Class, school, name = "Neutral", "", "Body of C'Thun"
	requireTarget, mana = False, 5
	index = "DARKMOON_FAIRE~Neutral~Spell~5~~Body of C'Thun~Uncollectible"
	description = "Piece of C'Thun(0/4). Summon a 6/6 C'Thun's body with Taunt"
	name_CN = "克苏恩之躯"
	def available(self):
		return self.Game.space(self.ID) > 0
	
	def text(self, CHN):
		trigsBoard = self.Game.trigsBoard[self.ID]
		trig = next((trig for trig in trigsBoard if isinstance(trig, Trig_CThun)), None) if "CThunPiece" in trigsBoard else None
		num = len(trig.pieces) if trig else 0
		return "克苏恩碎片(%d/4)。召唤一个6/6并具有嘲讽的克苏恩残躯"%num if CHN \
			else "Piece of C'Thun(%d/4). Summon a 6/6 C'Thun's body with Taunt"%num
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.summon(CThunsBody(self.Game, self.ID), -1)
		#Assume the spell effect will increase the counter
		if "CThunPiece" not in self.Game.trigsBoard[self.ID]:
			Trig_CThun(self.Game, self.ID).connect()
		self.Game.sendSignal("CThunPiece", self.ID, None, None, 0, "Body")
		return None
		
class CThunsBody(Minion):
	Class, race, name = "Neutral", "", "C'Thun's Body"
	mana, attack, health = 6, 6, 6
	index = "DARKMOON_FAIRE~Neutral~Minion~6~6~6~~C'Thun's Body~Taunt~Uncollectible"
	requireTarget, keyWord, description = False, "Taunt", "Taunt"
	name_CN = "克苏恩之躯"
	
class EyeofCThun(Spell):
	Class, school, name = "Neutral", "", "Eye of C'Thun"
	requireTarget, mana = False, 5
	index = "DARKMOON_FAIRE~Neutral~Spell~5~~Eye of C'Thun~Uncollectible"
	description = "Deal 7 damage randomly split among all enemies"
	name_CN = "克苏恩之眼"
	def text(self, CHN):
		trigsBoard = self.Game.trigsBoard[self.ID]
		trig = next((trig for trig in trigsBoard if isinstance(trig, Trig_CThun)), None) if "CThunPiece" in trigsBoard else None
		num = len(trig.pieces) if trig else 0
		damage = (7 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		return "克苏恩碎片(%d/4)。造成%d点伤害，随机分配到所有敌人身上"%(num, damage) if CHN \
				else "Piece of C'Thun(%d/4). Deal %d damage randomly split among all enemies"%(num, damage)
				
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		damage = (7 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		side = 3 - self.ID
		for num in range(damage):
			objs = self.Game.charsAlive(side)
			if objs: self.dealsDamage(npchoice(objs), 1)
			else: break
		if "CThunPiece" not in self.Game.trigsBoard[self.ID]:
			Trig_CThun(self.Game, self.ID).connect()
		self.Game.sendSignal("CThunPiece", self.ID, None, None, 0, "Eye")
		return None
		
class HeartofCThun(Spell):
	Class, school, name = "Neutral", "", "Heart of C'Thun"
	requireTarget, mana = False, 5
	index = "DARKMOON_FAIRE~Neutral~Spell~5~~Heart of C'Thun~Uncollectible"
	description = "Deal 3 damage to all minions"
	name_CN = "克苏恩之心"
	def text(self, CHN):
		trigsBoard = self.Game.trigsBoard[self.ID]
		trig = next((trig for trig in trigsBoard if isinstance(trig, Trig_CThun)), None) if "CThunPiece" in trigsBoard else None
		num = len(trig.pieces) if trig else 0
		damage = (3 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		return "克苏恩碎片(%d/4)。对所有随从造成%d点伤害" % (num, damage) if CHN \
			else "Piece of C'Thun(%d/4). Deal %d damage to all minions" % (num, damage)
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		damage = (3 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		targets = self.Game.minionsonBoard(1) + self.Game.minionsonBoard(2)
		self.dealsAOE(targets, [damage] * len(targets))
		if "CThunPiece" not in self.Game.trigsBoard[self.ID]:
			Trig_CThun(self.Game, self.ID).connect()
		self.Game.sendSignal("CThunPiece", self.ID, None, None, 0, "Heart")
		return None
		
class MawofCThun(Spell):
	Class, school, name = "Neutral", "", "Maw of C'Thun"
	requireTarget, mana = True, 5
	index = "DARKMOON_FAIRE~Neutral~Spell~5~~Maw of C'Thun~Uncollectible"
	description = "Destroy a minion"
	name_CN = "克苏恩之口"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
	
	def text(self, CHN):
		trigsBoard = self.Game.trigsBoard[self.ID]
		trig = next((trig for trig in trigsBoard if isinstance(trig, Trig_CThun)), None) if "CThunPiece" in trigsBoard else None
		num = len(trig.pieces) if trig else 0
		return "克苏恩碎片(%d/4)。消灭一个随从"%num if CHN else "Piece of C'Thun(%d/4). Destroy a minion"%num
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			self.Game.killMinion(self, target)
		#Assume the counter still works even if there is no target designated
		if "CThunPiece" not in self.Game.trigsBoard[self.ID]:
			Trig_CThun(self.Game, self.ID).connect()
		self.Game.sendSignal("CThunPiece", self.ID, None, None, 0, "Maw")
		return None
		
#https://www.iyingdi.com/web/article/search/108538
#克苏恩不会出现在起手手牌中，只能在之后抽到碎片
#不在衍生池中，不能被随机发生和召唤等
#碎片是可以在第一次抽牌中抽到的，计入“开始时不在牌库中的牌”
#带克苏恩会影响巴库的触发，不影响狼王
#四张不同的碎片被打出后才会触发洗入克苏恩的效果，可以被法术反制
class CThuntheShattered(Minion):
	Class, race, name = "Neutral", "", "C'Thun, the Shattered"
	mana, attack, health = 10, 6, 6
	index = "DARKMOON_FAIRE~Neutral~Minion~10~6~6~~C'Thun, the Shattered~Battlecry~Start of Game~Legendary"
	requireTarget, keyWord, description = False, "", "Start of Game: Break into pieces. Battlecry: Deal 30 damage randomly split among all enemies"
	name_CN = "克苏恩，破碎之劫"
	#WON't show up in the starting hand
	def startofGame(self):
		#Remove the card from deck. Assume the final card WON't count as deck original card
		game, ID = self.Game, self.ID
		game.Hand_Deck.extractfromDeck(self, ID=0, all=False, enemyCanSee=True)
		self.shuffleintoDeck([BodyofCThun(game, ID), EyeofCThun(game, ID), HeartofCThun(game, ID), MawofCThun(game, ID)])
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		side, curGame = 3-self.ID, self.Game
		for num in range(30):
			objs = curGame.charsAlive(side)
			if objs: self.dealsDamage(npchoice(objs), 1)
			else: break
		return None
		
		
class DarkmoonRabbit(Minion):
	Class, race, name = "Neutral", "Beast", "Darkmoon Rabbit"
	mana, attack, health = 10, 1, 1
	index = "DARKMOON_FAIRE~Neutral~Minion~10~1~1~Beast~Darkmoon Rabbit~Rush~Poisonous"
	requireTarget, keyWord, description = False, "Rush,Poisonous", "Rush, Poisonous. Also damages the minions next to whomever this attacks"
	name_CN = "暗月兔子"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.marks["Sweep"] = 1
		
		
class NZothGodoftheDeep(Minion):
	Class, race, name = "Neutral", "", "N'Zoth, God of the Deep"
	mana, attack, health = 9, 5, 7
	index = "DARKMOON_FAIRE~Neutral~Minion~9~5~7~~N'Zoth, God of the Deep~Battlecry~Legendary"
	requireTarget, keyWord, description = False, "", "Battlecry: Resurrect a friendly minion of each minion type"
	name_CN = "恩佐斯，深渊之神"
	#A single Amalgam minion won't be resurrected multiple times
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		game, ID = self.Game, self.ID
		#First, categorize. Second, from each type, select one.
		minions, pool = [], game.Counters.minionsDiedThisGame[ID]
		types = {"Beast": [], "Pirate": [], "Elemental": [], "Mech": [], "Dragon": [], "Quilboar": [], "Totem": [], "Demon": [], "Murloc": [], "All": []}
		#假设机制如下 ，在依次决定几个种族召唤随从，融合怪的随从池和单一种族的随从池合并计算随机。这个种族下如果没有召唤出一个融合怪，则它可以继续等待，如果召唤出来了，则将其移出随从池
		for card in pool:
			race = card.race
			if race: types[race if len(race) < 10 else "All"].append(card)
		for race in ["Elemental", "Mech", "Demon", "Murloc", "Dragon", "Beast", "Pirate", "Quilboar", "Totem"]: #假设种族顺序是与融合怪的牌面描述 一致的
			a, b = len(types[race]), len(types["All"])
			if a or b:
				p1 = a / (a + b)
				isAmalgam = npchoice([0, 1], p=[p1, 1-p1])
				minions.append(types["All"].pop(nprandint(b)) if isAmalgam else types[race][nprandint(a)])
		if minions: self.summon([minion(game, ID) for minion in minions], (self.pos, "totheRight"))
		return None
		
		
class CurseofFlesh(Spell):
	Class, school, name = "Neutral", "", "Curse of Flesh"
	requireTarget, mana = False, 0
	index = "DARKMOON_FAIRE~Neutral~Spell~0~~Curse of Flesh~Uncollectible"
	description = "Fill the board with random minions, then give yours Rush"
	name_CN = "血肉诅咒"
	poolIdentifier = "Minions to Summon"
	@classmethod
	def generatePool(cls, pools):
		pool = []
		for minions in pools.MinionsofCost.values(): #value is still a dict: {index: type}
			pool += minions
		return "Minions to Summon", pool
		
	def __init__(self, Game, ID, yogg):
		super().__init__(Game, ID)
		self.yogg = yogg
		
	def cast(self, target=None, comment="", preferedTarget=None):
		game = self.Game
		minions1 = npchoice(self.rngPool("Minions to Summon"), game.space(1), replace=True)
		minions2 = npchoice(self.rngPool("Minions to Summon"), game.space(2), replace=True)
		if self.ID == 1: ownMinions, enemyMinions = minions1, minions2
		else: ownMinions, enemyMinions = minions2, minions1
		if game.GUI:
			game.GUI.showOffBoardTrig(self)
			game.GUI.subject = self
			game.GUI.target = target
		if len(ownMinions):
			ownMinions = [minion(game, self.ID) for minion in ownMinions]
			self.yogg.summon(ownMinions, (self.yogg.pos, "totheRight"))
		if len(enemyMinions):
			enemyMinions = [minion(game, 3-self.ID) for minion in enemyMinions]
			self.yogg.summon(enemyMinions, (-1, "totheRightEnd"))
		for minion in ownMinions: #Give the minion you summon Rush
			if minion.onBoard: minion.getsStatus("Rush")
				
class DevouringHunger(Spell):
	Class, school, name = "Neutral", "", "Devouring Hunger"
	requireTarget, mana = False, 0
	index = "DARKMOON_FAIRE~Neutral~Spell~0~~Devouring Hunger~Uncollectible"
	description = "Destroy all other minions. Gain their Attack and Health"
	name_CN = "吞噬之饥"
	def __init__(self, Game, ID, yogg):
		super().__init__(Game, ID)
		self.yogg = yogg
		
	def cast(self, target=None, comment="", preferedTarget=None):
		curGame = self.Game
		if curGame.GUI:
			curGame.GUI.showOffBoardTrig(self)
			curGame.GUI.subject = self
			curGame.GUI.target = target
			curGame.GUI.wait(750)
		attGain, healthGain = 0, 0
		for minion in curGame.minionsonBoard(1) + curGame.minionsonBoard(2):
			if minion != self.yogg:
				attGain += max(0, minion.attack)
				healthGain += max(0, minion.health)
				curGame.killMinion(self.yogg, minion)
		if self.yogg.onBoard or self.yogg.inHand: self.yogg.buffDebuff(attGain, healthGain)
		
class HandofFate(Spell):
	Class, school, name = "Neutral", "", "Hand of Fate"
	requireTarget, mana = False, 0
	index = "DARKMOON_FAIRE~Neutral~Spell~0~~Hand of Fate~Uncollectible"
	description = "Fill your hand with random spells. They cost (0) this turn"
	name_CN = "命运之手"
	poolIdentifier = "Spells"
	@classmethod
	def generatePool(cls, pools):
		spells = []
		for cards in pools.ClassCards.values():
			spells += [card for card in cards if card.type == "Spell"]
		return "Spells", spells
	
	def __init__(self, Game, ID, yogg):
		super().__init__(Game, ID)
		self.yogg = yogg
		
	def cast(self, target=None, comment="", preferedTarget=None):
		game = self.Game
		pool = tuple(self.rngPool("Spells"))
		if game.GUI:
			game.GUI.showOffBoardTrig(self)
			game.GUI.subject = self
			game.GUI.target = target
		spells = [spell(game, self.ID) for spell in npchoice(pool, game.Hand_Deck.spaceinHand(self.ID), replace=True)]
		self.yogg.addCardtoHand(spells, self.ID)
		for spell in spells:
			if spell.inHand: ManaMod_Cost0ThisTurn(spell).applies()
			
class MindflayerGoggles(Spell):
	Class, school, name = "Neutral", "", "Mindflayer Goggles"
	requireTarget, mana = False, 0
	index = "DARKMOON_FAIRE~Neutral~Spell~0~~Mindflayer Goggles~Uncollectible"
	description = "Take control of three random enemy minions"
	name_CN = "夺心护目镜"
	def __init__(self, Game, ID, yogg):
		super().__init__(Game, ID)
		self.yogg = yogg
		
	def cast(self, target=None, comment="", preferedTarget=None):
		game, side = self.Game, 3 - self.ID
		if game.GUI:
			game.GUI.showOffBoardTrig(self)
			game.GUI.subject = self
			game.GUI.target = target
		for num in range(3):
			minions = game.minionsAlive(side)
			if minions: game.minionSwitchSide(npchoice(minions))
		return None
		
class Mysterybox(Spell):
	Class, school, name = "Neutral", "", "Mysterybox"
	requireTarget, mana = False, 0
	index = "DARKMOON_FAIRE~Neutral~Spell~0~~Mysterybox~Uncollectible"
	description = "Cast a random spell for each spell you've cast this game(targets chosen randomly)"
	name_CN = "神秘魔盒"
	#pool already generated by the other effect
	def __init__(self, Game, ID, yogg):
		super().__init__(Game, ID)
		self.yogg = yogg
		
	def cast(self, target=None, comment="", preferedTarget=None):
		game = self.Game
		if game.GUI:
			game.GUI.showOffBoardTrig(self)
			game.GUI.subject = self
			game.GUI.target = target
		num = sum(issubclass(card, Spell) for card in game.Counters.cardsPlayedThisGame[self.ID])
		spells = [spell(game, self.ID) for spell in  npchoice(self.rngPool("Spells"), num, replace=True)]
		for spell in spells:
			spell.cast()
			game.gathertheDead(decideWinner=True)
			
#每次释放炎爆之后会进行设计胜负判定的死亡结算
class RodofRoasting(Spell):
	Class, school, name = "Neutral", "", "Rod of Roasting"
	requireTarget, mana = False, 0
	index = "DARKMOON_FAIRE~Neutral~Spell~0~~Rod of Roasting~Uncollectible"
	description = "Cast 'Pyroblast' randomly until a player dies"
	name_CN = "燃烧权杖"
	def __init__(self, Game, ID, yogg):
		super().__init__(Game, ID)
		self.yogg = yogg
		
	def cast(self, target=None, comment="", preferedTarget=None):
		game = self.Game
		if game.GUI:
			game.GUI.showOffBoardTrig(self)
			game.GUI.subject = self
			game.GUI.target = target
		i = 0
		while i < 30 and game.heroes[1].health > 0 and not game.heroes[1].dead and game.heroes[2].health > 0 and not game.heroes[2].dead:
			objs = game.charsAlive(1) + game.charsAlive(2)
			if objs:
				Pyroblast(game, self.ID).cast(target=npchoice(objs), comment="", preferedTarget=None)
				game.gathertheDead(decideWinner=True)
			else: break
		game.heroes[3-self.ID].dead = True #假设在30次循环后如果还没有人死亡的话，则直接杀死对方英雄
		return None
		
class YoggSaronMasterofFate(Minion):
	Class, race, name = "Neutral", "", "Yogg-Saron, Master of Fate"
	mana, attack, health = 10, 7, 5
	index = "DARKMOON_FAIRE~Neutral~Minion~10~7~5~~Yogg-Saron, Master of Fate~Battlecry~Legendary"
	requireTarget, keyWord, description = False, "", "Battlecry: If you've cast 10 spells this game, spin the Wheel of Yogg-Saron"
	name_CN = "尤格-萨隆，命运主宰"
	def effCanTrig(self):
		self.effectViable = sum(issubclass(card, Spell) for card in self.Game.Counters.cardsPlayedThisGame[self.ID]) > 10

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if sum(issubclass(card, Spell) for card in self.Game.Counters.cardsPlayedThisGame[self.ID]) > 10:
			#CurseofFlesh "Fill the board with random minions, then give your Rush"
			#DevouringHunger "Destroy all other minions. Gain their Attack and Health"
			#HandofFate "Fill your hand with random spells. They cost (0) this turn"
			#MindflayerGoggles "Take control of three random enemy minions"
			#Mysterybox "Cast a random spell for each spell you've cast this game(targets chosen randomly)"
			#RodofRoasting "Cast 'Pyroblast' randomly until a player dies"
			wheel = npchoice([CurseofFlesh, DevouringHunger, HandofFate, MindflayerGoggles, Mysterybox, RodofRoasting],
								p=[0.19, 0.19, 0.19, 0.19, 0.19, 0.05])
			wheel(self.Game, self.ID, self).cast()
		return None
		
		
class YShaarjtheDefiler(Minion):
	Class, race, name = "Neutral", "", "Y'Shaarj, the Defiler"
	mana, attack, health = 10, 10, 10
	index = "DARKMOON_FAIRE~Neutral~Minion~10~10~10~~Y'Shaarj, the Defiler~Battlecry~Legendary"
	requireTarget, keyWord, description = False, "", "Battlecry: Add a copy of each Corrupted card you've played this game to your hand. They cost (0) this turn"
	name_CN = "亚煞极，污染之源"
	#The mana effect should be carried by each card, since card copied to opponent should also cost (0).
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		game, ID = self.Game, self.ID
		pool = [card for card in game.Counters.cardsPlayedThisGame[ID] if "_Corrupt" in card.__name__]
		#numpy.random.choice can apply to [], as long as num=0
		cards = npchoice(pool, min(game.Hand_Deck.spaceinHand(ID), len(pool)), replace=False)
		if cards:
			cards = [card(game, ID) for card in cards]
			self.addCardtoHand(cards, ID)
			for card in cards:
				if card.inHand: ManaMod_Cost0ThisTurn(card).applies()
		return None
		
class ManaMod_Cost0ThisTurn:
	def __init__(self, card):
		self.card = card
		self.changeby, self.changeto = 0, 0
		self.source = None
		
	def handleMana(self):
		self.card.mana = 0
		
	def applies(self):
		card = self.card
		card.manaMods.append(self)
		if card in card.Game.Hand_Deck.hands[card.ID]:
			try: card.Game.trigsBoard[card.ID]["TurnEnds"].append(self)
			except: card.Game.trigsBoard[card.ID]["TurnEnds"] = [self]
			card.Game.Manas.calcMana_Single(card)
			
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.card.inHand
		
	def trig(self, signal, ID, subject, target, number, comment, choice=0):
		self.getsRemoved()
		self.card.Game.Manas.calcMana_Single(self.card)
		
	def getsRemoved(self):
		try: self.card.Game.trigsBoard[self.card.ID]["TurnEnds"].remove(self)
		except: pass
		try: self.card.manaMods.remove(self)
		except: pass
		
	def selfCopy(self, recipient):
		return ManaMod_Cost0ThisTurn(recipient)
		
		
"""Demon Hunter cards"""
class FelscreamBlast(Spell):
	Class, school, name = "Demon Hunter", "Fel", "Felscream Blast"
	requireTarget, mana = True, 1
	index = "DARKMOON_FAIRE~Demon Hunter~Spell~1~Fel~Felscream Blast~Lifesteal"
	description = "Lifesteal. Deal 1 damage to a minion and its neighbors"
	name_CN = "邪吼冲击"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.keyWords["Lifesteal"] = 1
		
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			damage = (1 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			neighbors = self.Game.neighbors2(target)[0]
			if target.onBoard and neighbors:
				self.dealsAOE([target] + neighbors, [damage] * (1 + len(neighbors)))
			else:
				self.dealsDamage(target, damage)
		return target
		
		
class ThrowGlaive(Spell):
	Class, school, name = "Demon Hunter", "", "Throw Glaive"
	requireTarget, mana = True, 1
	index = "DARKMOON_FAIRE~Demon Hunter~Spell~1~~Throw Glaive"
	description = "Deal 2 damage to a minion. If it dies, add a temporary copy of this to your hand"
	name_CN = "投掷利刃"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
		
	def text(self, CHN):
		damage = (2 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		return "对一个随从造成%d点伤害。如果该随从死亡，则此牌的一张临时复制置入你的手牌" % damage if CHN \
			else "Deal %d damage to a minion. If it dies, add a temporary copy of this to your hand" % damage
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			damage = (2 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			dmgTaker, damageActual = self.dealsDamage(target, damage)
			if dmgTaker.health < 1 or dmgTaker.dead:
				card = ThrowGlaive(self.Game, self.ID)
				card.trigsHand = [Trig_Echo(card)]
				self.addCardtoHand(card, self.ID)
		return target
		
		
class RedeemedPariah(Minion):
	Class, race, name = "Demon Hunter", "", "Redeemed Pariah"
	mana, attack, health = 2, 2, 3
	index = "DARKMOON_FAIRE~Demon Hunter~Minion~2~2~3~~Redeemed Pariah"
	requireTarget, keyWord, description = False, "", "After you play an Outcast card, gain +1/+1"
	name_CN = "获救的流民"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_RedeemedPariah(self)]
		
class Trig_RedeemedPariah(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["MinionBeenPlayed", "SpellBeenPlayed", "WeaponBeenPlayed", "HeroCardBeenPlayed"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject.ID == self.entity.ID and "~Outcast" in subject.index
		
	def text(self, CHN):
		return "在你使用一张流放牌后，获得+1/+1" if CHN else "After you play an Outcast card, gain +1/+1"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.buffDebuff(1, 1)
		
		
class Acrobatics(Spell):
	Class, school, name = "Demon Hunter", "", "Acrobatics"
	requireTarget, mana = False, 3
	index = "DARKMOON_FAIRE~Demon Hunter~Spell~3~~Acrobatics"
	description = "Draw 2 cards. If you play both this turn, draw 2 more"
	name_CN = "空翻杂技"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		card1 = self.Game.Hand_Deck.drawCard(self.ID)[0]
		card2 = self.Game.Hand_Deck.drawCard(self.ID)[0]
		if card1 and card2: Acrobatics_Effect(self.Game, self.ID, [card1, card2]).connect()
		return None
		
class Acrobatics_Effect:
	def __init__(self, Game, ID, cardsDrawn):
		self.Game, self.ID = Game, ID
		self.card = Acrobatics(Game, ID)
		#Assume the trig is after the card is played
		self.signals = ["MinionBeenPlayed", "SpellBeenPlayed", "WeaponBeenPlayed", "HeroCardBeenPlayed"]
		self.cardsDrawn = cardsDrawn
		self.counter = 2
		
	def connect(self):
		for sig in self.signals:
			try: self.Game.trigsBoard[self.ID][sig].append(self)
			except: self.Game.trigsBoard[self.ID][sig] = [self]
		self.Game.turnEndTrigger.append(self)
		if self.Game.GUI: self.Game.GUI.heroZones[self.ID].addaTrig(self.card, text='2')
	
	def disconnect(self):
		for sig in self.signals:
			try: self.Game.trigsBoard[self.ID][sig].remove(self)
			except: pass
		try: self.Game.turnEndTrigger.remove(self)
		except: pass
		if self.Game.GUI: self.Game.GUI.heroZones[self.ID].removeaTrig(self.card)
	
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject.ID == self.ID and subject in self.cardsDrawn
		
	def trig(self, signal, ID, subject, target, number, comment, choice=0):
		if self.canTrig(signal, ID, subject, target, number, comment):
			if self.Game.GUI: self.Game.GUI.showOffBoardTrig(self.card)
			self.effect(signal, ID, subject, target, number, comment)
			
	def text(self, CHN):
		return "如果你使用了空翻杂技抽到的两张牌，则可以再抽两张" if CHN else "If you use the two cards drawn by Acrobatics, draw 2 more"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		try: self.cardsDrawn.remove(subject)
		except: pass
		self.counter = len(self.cardsDrawn)
		if self.card.btn: self.card.btn.trigAni(self.counter)
		if not self.cardsDrawn:
			self.Game.Hand_Deck.drawCard(self.ID)
			self.Game.Hand_Deck.drawCard(self.ID)
		self.disconnect()
		
	def turnEndTrigger(self):
		self.disconnect()
		
	def createCopy(self, game): #不是纯的只在回合结束时触发，需要完整的createCopy
		if self not in game.copiedObjs: #这个扳机没有被复制过
			trigCopy = type(self)(game, self.ID, [])
			trigCopy.cardsDrawn = [card.createCopy(game) for card in self.cardsDrawn]
			trigCopy.counter = self.counter
			game.copiedObjs[self] = trigCopy
			return trigCopy
		else: #一个扳机被复制过了，则其携带者也被复制过了
			return game.copiedObjs[self]
			
			
class DreadlordsBite(Weapon):
	Class, name, description = "Demon Hunter", "Dreadlord's Bite", "Outcast: Deal 1 damage to all enemies"
	mana, attack, durability = 3, 2, 2
	index = "DARKMOON_FAIRE~Demon Hunter~Weapon~3~2~2~Dreadlord's Bite~Outcast"
	name_CN = "恐惧魔王之咬"
	
	def effCanTrig(self):
		self.effectViable = self.Game.Hand_Deck.outcastcanTrig(self)
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if posinHand == 0 or posinHand == -1:
			enemies = [self.Game.heroes[3-self.ID]] + self.Game.minionsonBoard(3-self.ID)
			self.dealsAOE(enemies, [1] * len(enemies))
		return None
		
		
class FelsteelExecutioner(Minion):
	Class, race, name = "Demon Hunter", "Elemental", "Felsteel Executioner"
	mana, attack, health = 3, 4, 3
	index = "DARKMOON_FAIRE~Demon Hunter~Minion~3~4~3~Elemental~Felsteel Executioner~ToCorrupt"
	requireTarget, keyWord, description = False, "", "Corrupt: Become a weapon"
	name_CN = "魔钢处决者"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsHand = [Trig_Corrupt(self, FelsteelExecutioner_Corrupt)] #只有在手牌中才会升级
		
class FelsteelExecutioner_Corrupt(Weapon):
	Class, name, description = "Demon Hunter", "Felsteel Executioner", "Corrupted"
	mana, attack, durability = 3, 4, 3
	index = "DARKMOON_FAIRE~Demon Hunter~Weapon~3~4~3~Felsteel Executioner~Corrupted~Uncollectible"
	name_CN = "魔钢处决者"
	
	
class LineHopper(Minion):
	Class, race, name = "Demon Hunter", "", "Line Hopper"
	mana, attack, health = 3, 3, 4
	index = "DARKMOON_FAIRE~Demon Hunter~Minion~3~3~4~~Line Hopper"
	requireTarget, keyWord, description = False, "", "Your Outcast cards cost (1) less"
	name_CN = "越线的游客"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.auras["Your Outcast cards cost (1) less"] = ManaAura(self, changeby=-1, changeto=-1)
		
	def manaAuraApplicable(self, subject): #ID用于判定是否是我方手中的随从
		return "~Outcast" in subject.index and subject.ID == self.ID
		
		
class InsatiableFelhound(Minion):
	Class, race, name = "Demon Hunter", "Demon", "Insatiable Felhound"
	mana, attack, health = 3, 2, 5
	index = "DARKMOON_FAIRE~Demon Hunter~Minion~3~2~5~Demon~Insatiable Felhound~Taunt~ToCorrupt"
	requireTarget, keyWord, description = False, "Taunt", "Taunt. Corrupt: Gain +1/+1 and Lifesteal"
	name_CN = "贪食地狱犬"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsHand = [Trig_Corrupt(self, InsatiableFelhound_Corrupt)] #只有在手牌中才会升级
		
class InsatiableFelhound_Corrupt(Minion):
	Class, race, name = "Demon Hunter", "Demon", "Insatiable Felhound"
	mana, attack, health = 3, 3, 6
	index = "DARKMOON_FAIRE~Demon Hunter~Minion~3~3~6~Demon~Insatiable Felhound~Taunt~Lifesteal~Corrupt~Uncollectible"
	requireTarget, keyWord, description = False, "Taunt,Lifesteal", "Taunt, Lifesteal"
	name_CN = "贪食地狱犬"
	
	
class RelentlessPursuit(Spell):
	Class, school, name = "Demon Hunter", "", "Relentless Pursuit"
	requireTarget, mana = False, 3
	index = "DARKMOON_FAIRE~Demon Hunter~Spell~3~~Relentless Pursuit"
	description = "Give your hero +4 Attack and Immune this turn"
	name_CN = "冷酷追杀"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.Game.heroes[self.ID].gainAttack(4)
		self.Game.status[self.ID]["Immune"] += 1
		self.Game.status[self.ID]["ImmuneThisTurn"] += 1
		return None
		
		
class Stiltstepper(Minion):
	Class, race, name = "Demon Hunter", "", "Stiltstepper"
	mana, attack, health = 3, 4, 1
	index = "DARKMOON_FAIRE~Demon Hunter~Minion~3~4~1~~Stiltstepper~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Draw a card. If you play it this turn, give your hero +4 Attack this turn"
	name_CN = "高跷艺人"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		card = self.Game.Hand_Deck.drawCard(self.ID)[0]
		if card: Stiltstepper_Effect(self.Game, self.ID, card).connect()
		return None
		
class Stiltstepper_Effect:
	def __init__(self, Game, ID, cardDrawn):
		self.Game, self.ID = Game, ID
		self.card = Stiltstepper(Game, ID)
		#Assume the trig is after the card is played
		self.signals = ["MinionBeenPlayed", "SpellBeenPlayed", "WeaponBeenPlayed", "HeroCardBeenPlayed"]
		self.cardMarked = cardDrawn
		
	def connect(self):
		for sig in self.signals:
			try: self.Game.trigsBoard[self.ID][sig].append(self)
			except: self.Game.trigsBoard[self.ID][sig] = [self]
		self.Game.turnEndTrigger.append(self)
		if self.Game.GUI: self.Game.GUI.heroZones[self.ID].addaTrig(self.card)
	
	def disconnect(self):
		for sig in self.signals:
			try: self.Game.trigsBoard[self.ID][sig].remove(self)
			except: pass
		try: self.Game.turnEndTrigger.remove(self)
		except: pass
		if self.Game.GUI: self.Game.GUI.heroZones[self.ID].removeaTrig(self.card)
	
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject.ID == self.ID and subject == self.cardMarked
		
	def trig(self, signal, ID, subject, target, number, comment, choice=0):
		if self.canTrig(signal, ID, subject, target, number, comment):
			if self.Game.GUI: self.Game.GUI.showOffBoardTrig(self.card)
			self.effect(signal, ID, subject, target, number, comment)
			
	def text(self, CHN):
		return "在本回合，如果你使用高跷巨人的战吼抽到的牌，则你的英雄在本回合中获得+1攻击力" if CHN \
				else "This turn, if you play the card drawn by Stiltstepper's Battlecry, your hero gains +4 Attack this turn"
				
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.Game.heroes[self.ID].gainAttack(4)
		self.disconnect()
		
	def turnEndTrigger(self):
		self.disconnect()
		
	def createCopy(self, game): #不是纯的只在回合结束时触发，需要完整的createCopy
		if self not in game.copiedObjs: #这个扳机没有被复制过
			trigCopy = type(self)(game, self.ID, None)
			trigCopy.cardMarked = self.cardMarked.createCopy(game)
			game.copiedObjs[self] = trigCopy
			return trigCopy
		else: #一个扳机被复制过了，则其携带者也被复制过了
			return game.copiedObjs[self]
			
#Even if hero is full health, the Lifesteal will still deal damage
class Ilgynoth(Minion):
	Class, race, name = "Demon Hunter", "", "Il'gynoth"
	mana, attack, health = 6, 4, 8
	index = "DARKMOON_FAIRE~Demon Hunter~Minion~6~4~8~~Il'gynoth~Lifesteal~Legendary"
	requireTarget, keyWord, description = False, "Lifesteal", "Lifesteal. Your Lifesteal damages the enemy hero instead of healing you"
	name_CN = "伊格诺斯"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.auras["Your Lifesteal damages the enemy hero instead of healing you"] = GameRuleAura_Ilgynoth(self)
		
class GameRuleAura_Ilgynoth(GameRuleAura):
	def auraAppears(self):
		self.entity.Game.status[self.entity.ID]["Lifesteal Damages Enemy"] += 1
		
	def auraDisappears(self):
		self.entity.Game.status[self.entity.ID]["Lifesteal Damages Enemy"] -= 1
		
		
class RenownedPerformer(Minion):
	Class, race, name = "Demon Hunter", "", "Renowned Performer"
	mana, attack, health = 4, 3, 3
	index = "DARKMOON_FAIRE~Demon Hunter~Minion~4~3~3~~Renowned Performer~Rush~Deathrattle"
	requireTarget, keyWord, description = False, "Rush", "Rush. Deathrattle: Summon two 1/1 Assistants with Rush"
	name_CN = "知名表演者"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.deathrattles = [Summon2Assistants(self)]
		
class Summon2Assistants(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		minion = self.entity
		pos = (minion.pos, "leftandRight") if minion in minion.Game.minions[minion.ID] else (-1, "totheRightEnd")
		minion.summon([PerformersAssistant(minion.Game, minion.ID) for i in range(2)], pos)
		
	def text(self, CHN):
		return "亡语：召唤两个1/1并具有嘲讽的助演" if CHN else "Deathrattle: Summon two 1/1 Assistants with Rush"
		
		
class PerformersAssistant(Minion):
	Class, race, name = "Demon Hunter", "", "Performer's Assistant"
	mana, attack, health = 1, 1, 1
	index = "DARKMOON_FAIRE~Demon Hunter~Minion~1~1~1~~Performer's Assistant~Taunt~Uncollectible"
	requireTarget, keyWord, description = False, "Taunt", "Taunt"
	name_CN = "演出助手"
	
	
class ZaitheIncredible(Minion):
	Class, race, name = "Demon Hunter", "", "Zai, the Incredible"
	mana, attack, health = 5, 5, 3
	index = "DARKMOON_FAIRE~Demon Hunter~Minion~5~5~3~~Zai, the Incredible~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Copy the left- and right-most cards in your hand"
	name_CN = "扎依，出彩艺人"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		ownHand = self.Game.Hand_Deck.hands[self.ID]
		if ownHand:
			#需要更多考虑
			cards = [ownHand[0].selfCopy(self.ID, self), ownHand[-1].selfCopy(self.ID, self)]
			#Assume the copied cards BOTH occupy the right most position
			self.addCardtoHand(cards, self.ID)
		return None
		
		
class BladedLady(Minion):
	Class, race, name = "Demon Hunter", "Demon", "Bladed Lady"
	mana, attack, health = 6, 6, 6
	index = "DARKMOON_FAIRE~Demon Hunter~Minion~6~6~6~Demon~Bladed Lady~Rush"
	requireTarget, keyWord, description = False, "Rush", "Rush. Costs (1) if your hero has 6 or more Attack"
	name_CN = "刀锋舞娘"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsHand = [Trig_BladedLady(self)]
		
	def selfManaChange(self):
		if self.inHand and self.Game.heroes[self.ID].attack > 5:
			self.mana = 1
			
class Trig_BladedLady(TrigHand):
	def __init__(self, entity):
		super().__init__(entity, ["HeroAttCalc"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.inHand and ID == self.entity.ID
		
	def text(self, CHN):
		return "每当你的英雄的攻击力改变，重新计算费用" if CHN else "Whenever your hero's Attack changes, recalculate the cost"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.Game.Manas.calcMana_Single(self.entity)
		
		
class ExpendablePerformers(Spell):
	Class, school, name = "Demon Hunter", "", "Expendable Performers"
	requireTarget, mana = False, 7
	index = "DARKMOON_FAIRE~Demon Hunter~Spell~7~~Expendable Performers"
	description = "Summon seven 1/1 Illidari with Rush. If they all die this turn, summon seven more"
	name_CN = "演员大接力"
	def available(self):
		return self.Game.space(self.ID) > 0
	#Don't need to all 7 Illidari to be summoned and die
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		minions = [IllidariInitiate(self.Game, self.ID) for i in range(7)]
		self.summon(minions, (-1, "totheRightEnd"))
		minions = [minion for minion in minions if minion.onBoard]
		if minions: #But there should be at least 1 Illidari summoned
			ExpendablePerformers_Effect(self.Game, self.ID, minions, self).connect()
		return None
		
class ExpendablePerformers_Effect:
	def __init__(self, Game, ID, minions, entity):
		self.entity = entity
		self.card = ExpendablePerformers(Game, ID)
		self.Game, self.ID = Game, ID
		self.minions = minions
		
	def connect(self):
		try: self.Game.trigsBoard[self.ID]["TurnEnds"].append(self)
		except: self.Game.trigsBoard[self.ID]["TurnEnds"] = [self]
		try: self.Game.trigsBoard[self.ID]["MinionDies"].append(self)
		except: self.Game.trigsBoard[self.ID]["MinionDies"] = [self]
		self.Game.turnEndTrigger.append(self)
		if self.Game.GUI: self.Game.GUI.heroZones[self.ID].addaTrig(self.card)
	
	def disconnect(self):
		try: self.Game.trigsBoard[self.ID]["TurnEnds"].remove(self)
		except: pass
		try: self.Game.trigsBoard[self.ID]["MinionDies"].remove(self)
		except: pass
		try: self.Game.turnEndTrigger.remove(self)
		except: pass
		if self.Game.GUI: self.Game.GUI.heroZones[self.ID].removeaTrig(self.card)
	
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return target.ID == self.ID and target in self.minions
		
	def trig(self, signal, ID, subject, target, number, comment, choice=0):
		if self.canTrig(signal, ID, subject, target, number, comment):
			if self.Game.GUI: self.Game.GUI.showOffBoardTrig(self.card)
			self.effect(signal, ID, subject, target, number, comment)
			
	def text(self, CHN):
		return "本回合中，当演员大接力召唤的伊利达雷全部死亡后再召唤七个" if CHN \
				else "After all Illidari summoned by Expendable Performers die within this turn, summon 7 more"
				
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		try: self.minions.remove(target)
		except: pass
		if not self.minions:
			self.disconnect()
			self.card.summon([IllidariInitiate(self.Game, self.ID) for i in range(7)], (-1, "totheRightEnd"))
			
	def turnEndTrigger(self):
		self.disconnect()
		
	def createCopy(self, game): #不是纯的只在回合结束时触发，需要完整的createCopy
		if self not in game.copiedObjs: #这个扳机没有被复制过
			trigCopy = type(self)(game, self.ID, [])
			trigCopy.minions = [minion.createCopy(game) for minion in self.minions]
			game.copiedObjs[self] = trigCopy
			return trigCopy
		else: #一个扳机被复制过了，则其携带者也被复制过了
			return game.copiedObjs[self]
			
			
"""Druid cards"""
class GuesstheWeight(Spell):
	Class, school, name = "Druid", "", "Guess the Weight"
	requireTarget, mana = False, 2
	index = "DARKMOON_FAIRE~Druid~Spell~2~~Guess the Weight"
	description = "Draw a card. Guess if your next card costs more or less to draw it"
	name_CN = "猜重量"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		game = self.Game
		card, firstCost = game.Hand_Deck.drawCard(self.ID)
		ownDeck = game.Hand_Deck.decks[self.ID]
		if card and ownDeck:
			secondCost = ownDeck[-1].mana
			self.chooseFixedOptions(GuesstheWeight, comment,
									options=[NextCostsMore(self.ID, firstCost, secondCost), 
											NextCostsLess(self.ID, firstCost, secondCost)])
			return None
			
	def discoverDecided(self, option, case, info_RNGSync=None, info_GUISync=None):
		if case != "Guided": self.Game.picks.append((info_RNGSync, info_GUISync, case == "Random", type(option)) )
		bingo = (isinstance(option, NextCostsLess) and option.firstCost > option.secondCost) \
				or (isinstance(option, NextCostsMore) and option.firstCost < option.secondCost)
		if self.Game.GUI: self.Game.GUI.revealaCardfromDeckAni(self.ID, -1, option)
		if bingo: self.Game.Hand_Deck.drawCard(self.ID)
		

class NextCostsMore(Option):
	name = "Costs More"
	index = ""
	mana, attack, health = 0, -1, -1
	def __init__(self, ID, firstCost=0, secondCost=0):
		super().__init__(ID=ID)
		self.description = "The next card costs more than %d"%firstCost
		self.firstCost, self.secondCost = firstCost, secondCost
		
class NextCostsLess(Option):
	name = "Costs Less"
	index = ""
	mana, attack, health = 0, -1, -1
	def __init__(self, ID, firstCost=0, secondCost=0):
		super().__init__()
		self.description = "The next card costs less than %d"%firstCost
		self.firstCost, self.secondCost = firstCost, secondCost
		
		
class LunarEclipse(Spell):
	Class, school, name = "Druid", "", "Lunar Eclipse"
	requireTarget, mana = True, 2
	index = "DARKMOON_FAIRE~Druid~Spell~2~~Lunar Eclipse"
	description = "Deal 3 damage to a minion. Your next spell this turn costs (2) less"
	name_CN = "月蚀"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
		
	def text(self, CHN):
		damage = (3 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		return "对一个随从造成%d点伤害。在本回合中，你施放的下一个法术的法力值消耗减少(2)点"%damage if CHN \
				else "Deal %d damage to a minion. Your next spell this turn costs (2) less"%damage
				
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			damage = (3 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			self.dealsDamage(target, damage)
			tempAura = GameManaAura_InTurnNextSpell2Less(self.Game, self.ID)
			self.Game.Manas.CardAuras.append(tempAura)
			tempAura.auraAppears()
		return target

class GameManaAura_InTurnNextSpell2Less(TempManaEffect):
	def __init__(self, Game, ID, changeby=0, changeto=-1):
		super().__init__(Game, ID, -2, -1)
	
	def applicable(self, target):
		return target.ID == self.ID and target.type == "Spell"


class SolarEclipse(Spell):
	Class, school, name = "Druid", "", "Solar Eclipse"
	requireTarget, mana = False, 2
	index = "DARKMOON_FAIRE~Druid~Spell~2~~Solar Eclipse"
	description = "Your next spell this turn casts twice"
	name_CN = "日蚀"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.Game.status[self.ID]["Spells x2"] += 1
		SolarEclipse_Effect(self.Game, self.ID, self).connect()
		return None
		
class SolarEclipse_Effect:
	def __init__(self, Game, ID, card):
		self.Game, self.ID = Game, ID
		self.card = SolarEclipse(Game, ID)
		self.caster = card
		
	def connect(self):
		try: self.Game.trigsBoard[self.ID]["SpellBeenCast"].append(self)
		except: self.Game.trigsBoard[self.ID]["SpellBeenCast"] = [self]
		self.Game.turnEndTrigger.append(self)
		if self.Game.GUI: self.Game.GUI.heroZones[self.ID].addaTrig(self.card)
	
	def disconnect(self):
		try: self.Game.trigsBoard[self.ID]["SpellBeenCast"].remove(self)
		except: pass
		try: self.Game.turnEndTrigger.remove(self)
		except: pass
		if self.Game.GUI: self.Game.GUI.heroZones[self.ID].removeaTrig(self.card)
	
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject.ID == self.ID and subject != self.caster #This won't respond to the Solar Eclipse that sends the signal
		
	def trig(self, signal, ID, subject, target, number, comment, choice=0):
		if self.canTrig(signal, ID, subject, target, number, comment):
			if self.Game.GUI: self.Game.GUI.showOffBoardTrig(self.card)
			self.effect(signal, ID, subject, target, number, comment)
			
	def text(self, CHN):
		return "在本回合结束，或你使用一张法术后，你的法术不再施放两次" if CHN \
				else "After then turn ends or you play a spell, your spells will no longer cast twice"
				
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.Game.status[self.ID]["Spells x2"] -= 1
		self.disconnect()
		
	def turnEndTrigger(self):
		self.Game.status[self.ID]["Spells x2"] -= 1
		self.disconnect()
		
	def createCopy(self, game): #不是纯的只在回合结束时触发，需要完整的createCopy
		if self not in game.copiedObjs: #这个扳机没有被复制过
			trigCopy = type(self)(game, self.ID, None)
			game.copiedObjs[self] = trigCopy
			trigCopy.card = self.card.createCopy(game)
			return trigCopy
		else: #一个扳机被复制过了，则其携带者也被复制过了
			return game.copiedObjs[self]
			
			
#The card actually summons a treant that belongs in the darkmoonk pack. But the json id for this card somehow doesn't exist in HS's index
class FaireArborist(Minion):
	Class, race, name = "Druid", "", "Faire Arborist"
	mana, attack, health = 3, 2, 2
	index = "DARKMOON_FAIRE~Druid~Minion~3~2~2~~Faire Arborist~Choose One~ToCorrupt"
	requireTarget, keyWord, description = False, "", "Choose One- Draw a card; or Summon a 2/2 Treant. Corrupt: Do both"
	name_CN = "马戏团树艺师"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		# 0: Draw a card; 1:Summon a 2/2 Treant.
		self.options = [PrunetheFruit_Option(self), DigItUp_Option(self)]
		self.trigsHand = [Trig_Corrupt(self, FaireArborist_Corrupt)] #只有在手牌中才会升级
		
	def need2Choose(self):
		return True
		
	#对于抉择随从而言，应以与战吼类似的方式处理，打出时抉择可以保持到最终结算。但是打出时，如果因为鹿盔和发掘潜力而没有选择抉择，视为到对方场上之后仍然可以而没有如果没有
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if choice != 0: #"ChooseBoth" aura gives choice of -1
			self.summon(Treant_Darkmoon(self.Game, self.ID), self.pos+1)
		if choice < 1:
			self.Game.Hand_Deck.drawCard(self.ID)
		return None
		
class FaireArborist_Corrupt(Minion):
	Class, race, name = "Druid", "", "Faire Arborist"
	mana, attack, health = 3, 2, 2
	index = "DARKMOON_FAIRE~Druid~Minion~3~2~2~~Faire Arborist~Corrupted~Uncollectible"
	requireTarget, keyWord, description = False, "", "Corrupted. Summon a 2/2 Treant. Draw a card"
	name_CN = "马戏团树艺师"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.summon(Treant_Darkmoon(self.Game, self.ID), self.pos+1)
		self.Game.Hand_Deck.drawCard(self.ID)
		return None
		
class Treant_Darkmoon(Minion):
	Class, race, name = "Druid", "", "Treant"
	mana, attack, health = 2, 2, 2
	index = "DARKMOON_FAIRE~Druid~Minion~2~2~2~~Treant~Uncollectible"
	requireTarget, keyWord, description = False, "", ""
	name_CN = "树人"
	
	
class PrunetheFruit_Option(Option):
	name, description = "Prune the Fruit", "Draw a card"
	mana, attack, health = 3, -1, -1
	
class DigItUp_Option(Option):
	name, description = "Dig It Up", "Summon a 2/2 Treant"
	mana, attack, health = 3, -1, -1
	def available(self):
		return self.entity.Game.space(self.entity.ID) > 0
		
		
class MoontouchedAmulet(Spell):
	Class, school, name = "Druid", "", "Moontouched Amulet"
	requireTarget, mana = False, 3
	index = "DARKMOON_FAIRE~Druid~Spell~3~~Moontouched Amulet~ToCorrupt"
	description = "Give your hero +4 Attack this turn. Corrupt: And gain 6 Armor"
	name_CN = "月触项链"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsHand = [Trig_Corrupt(self, MoontouchedAmulet_Corrupt)] #只有在手牌中才会升级
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.Game.heroes[self.ID].gainAttack(4)
		return None
		
class MoontouchedAmulet_Corrupt(Spell):
	Class, school, name = "Druid", "", "Moontouched Amulet"
	requireTarget, mana = False, 3
	index = "DARKMOON_FAIRE~Druid~Spell~3~~Moontouched Amulet~Corrupted~Uncollectible"
	description = "Corrupted. Give your hero +4 Attack this turn. And gain 6 Armor"
	name_CN = "月触项链"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.Game.heroes[self.ID].gainAttack(4)
		self.Game.heroes[self.ID].gainsArmor(6)
		return None
		
		
class KiriChosenofElune(Minion):
	Class, race, name = "Druid", "", "Kiri, Chosen of Elune"
	mana, attack, health = 4, 2, 2
	index = "DARKMOON_FAIRE~Druid~Minion~4~2~2~~Kiri, Chosen of Elune~Battlecry~Legendary"
	requireTarget, keyWord, description = False, "", "Battlecry: Add a Solar Eclipse and Lunar Eclipse to your hand"
	name_CN = "基利，艾露恩之眷"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.addCardtoHand([SolarEclipse, LunarEclipse], self.ID)
		return None
		
		
class Greybough(Minion):
	Class, race, name = "Druid", "", "Greybough"
	mana, attack, health = 5, 4, 6
	index = "DARKMOON_FAIRE~Druid~Minion~5~4~6~~Greybough~Taunt~Deathrattle~Legendary"
	requireTarget, keyWord, description = False, "Taunt", "Taunt. Deathrattle: Give a random friendly minion 'Deathrattle: Summon Greybough'"
	name_CN = "格雷布"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.deathrattles = [GiveaFriendlyDeathrattleSummonGreybough(self)]
		
class GiveaFriendlyDeathrattleSummonGreybough(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		minions = self.entity.Game.minionsonBoard(self.entity.ID)
		if minions:
			minion = npchoice(minions)
			minion.getsTrig(SummonGreybough(minion), trigType="Deathrattle")
				
	def text(self, CHN):
		return "亡语：随机使一个友方随从获得“亡语：召唤格雷布”" if CHN else "Deathrattle: Give a random friendly minion 'Deathrattle: Summon Greybough'"
		
class SummonGreybough(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.summon(Greybough(self.entity.Game, self.entity.ID), self.entity.pos+1)
		
	def text(self, CHN):
		return "亡语：召唤格雷布" if CHN else "Deathrattle: Summon Greybough"
		
		
class UmbralOwl(Minion):
	Class, race, name = "Druid", "Beast", "Umbral Owl"
	mana, attack, health = 7, 4, 4
	index = "DARKMOON_FAIRE~Druid~Minion~7~4~4~Beast~Umbral Owl~Rush"
	requireTarget, keyWord, description = False, "Rush", "Rush. Costs (1) less for each spell you've cast this game"
	name_CN = "幽影猫头鹰"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsHand = [Trig_UmbralOwl(self)]
		
	def selfManaChange(self):
		if self.inHand:
			self.mana -= sum(issubclass(card, Spell) for card in self.Game.Counters.cardsPlayedThisGame[self.ID])
			self.mana = max(self.mana, 0)

class Trig_UmbralOwl(TrigHand):
	def __init__(self, entity):
		#假设这个费用改变扳机在“当你使用一张法术之后”。不需要预检测
		super().__init__(entity, ["SpellBeenPlayed"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.inHand and subject.ID == self.entity.ID
		
	def text(self, CHN):
		return "每当你使用一张法术，重新计算费用" if CHN else "Whenever you cast a spell, recalculate the cost"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.Game.Manas.calcMana_Single(self.entity)
		
		
class CenarionWard(Spell):
	Class, school, name = "Druid", "Nature", "Cenarion Ward"
	requireTarget, mana = False, 8
	index = "DARKMOON_FAIRE~Druid~Spell~8~Nature~Cenarion Ward"
	description = "Gain 8 Armor. Summon a random 8-Cost minion"
	name_CN = "塞纳里奥结界"
	poolIdentifier = "8-Cost Minions to Summon"
	@classmethod
	def generatePool(cls, pools):
		return "8-Cost Minions to Summon", pools.MinionsofCost[8]
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.Game.heroes[self.ID].gainsArmor(8)
		self.summon(npchoice(self.rngPool("8-Cost Minions to Summon"))(self.Game, self.ID), -1)
		return None
		
		
class FizzyElemental(Minion):
	Class, race, name = "Druid", "Elemental", "Fizzy Elemental"
	mana, attack, health = 9, 10, 10
	index = "DARKMOON_FAIRE~Druid~Minion~9~10~10~Elemental~Fizzy Elemental~Rush~Taunt"
	requireTarget, keyWord, description = False, "Rush,Taunt", "Rush ,Taunt"
	name_CN = "泡沫元素"
	
	
"""Hunter cards"""
class MysteryWinner(Minion):
	Class, race, name = "Hunter", "", "Mystery Winner"
	mana, attack, health = 1, 1, 1
	index = "DARKMOON_FAIRE~Hunter~Minion~1~1~1~~Mystery Winner~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Discover a Secret"
	name_CN = "神秘获奖者"
	poolIdentifier = "Hunter Secrets"
	@classmethod
	def generatePool(cls, pools):
		classes, lists = [], []
		for Class in pools.Classes:
			secrets = [card for card in pools.ClassCards[Class] if card.description.startswith("Secret:")]
			if secrets:
				classes.append(Class + " Secrets")
				lists.append(secrets)
		return classes, lists

	def decideSecretPool(self):
		HeroClass = self.Game.heroes[self.ID].Class
		key = HeroClass + " Secrets" if HeroClass in ["Hunter", "Mage", "Paladin", "Rogue"] else "Mage Secrets"
		return self.rngPool(key)
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.discoverandGenerate(MysteryWinner, comment, lambda : MysteryWinner.decideSecretPool(self))
		return None
		
		
class DancingCobra(Minion):
	Class, race, name = "Hunter", "Beast", "Dancing Cobra"
	mana, attack, health = 2, 1, 5
	index = "DARKMOON_FAIRE~Hunter~Minion~2~1~5~Beast~Dancing Cobra~ToCorrupt"
	requireTarget, keyWord, description = False, "", "Corrupt: Gain Poisonous"
	name_CN = "舞动的眼镜蛇"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsHand = [Trig_Corrupt(self, DancingCobra_Corrupt)] #只有在手牌中才会升级
		
class DancingCobra_Corrupt(Minion):
	Class, race, name = "Hunter", "Beast", "Dancing Cobra"
	mana, attack, health = 2, 1, 5
	index = "DARKMOON_FAIRE~Hunter~Minion~2~1~5~Beast~Dancing Cobra~Poisonous~Corrupted~Uncollectible"
	requireTarget, keyWord, description = False, "Poisonous", "Poisonous"
	name_CN = "舞动的眼镜蛇"
	
	
class DontFeedtheAnimals(Spell):
	Class, school, name = "Hunter", "", "Don't Feed the Animals"
	requireTarget, mana = False, 2
	index = "DARKMOON_FAIRE~Hunter~Spell~2~~Don't Feed the Animals~ToCorrupt"
	description = "Give all Beasts in your hand +1/+1. Corrupt: Give them +2/+2 instead"
	name_CN = "请勿投食"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsHand = [Trig_Corrupt(self, DontFeedtheAnimals_Corrupt)] #只有在手牌中才会升级
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		for card in self.Game.Hand_Deck.hands[self.ID]:
			if card.type == "Minion" and "Beast" in card.race:
				card.buffDebuff(1, 1)
		return None
		
class DontFeedtheAnimals_Corrupt(Spell):
	Class, school, name = "Hunter", "", "Don't Feed the Animals"
	requireTarget, mana = False, 2
	index = "DARKMOON_FAIRE~Hunter~Spell~2~~Don't Feed the Animals~Corrupted~Uncollectible"
	description = "Corrupted. Give all Beasts in your hand +2/+2"
	name_CN = "请勿投食"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		for card in self.Game.Hand_Deck.hands[self.ID]:
			if card.type == "Minion" and "Beast" in card.race:
				card.buffDebuff(2, 2)
		return None
		
		
class OpentheCages(Secret):
	Class, school, name = "Hunter", "", "Open the Cages"
	requireTarget, mana = False, 2
	index = "DARKMOON_FAIRE~Hunter~Spell~2~~Open the Cages~~Secret"
	description = "Secret: When your turn starts, if you control two minions, summon an Animal Companion"
	name_CN = "打开兽笼"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_OpentheCages(self)]
		
class Trig_OpentheCages(SecretTrigger):
	def __init__(self, entity):
		super().__init__(entity, ["TurnStarts"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0): #target here holds the actual target object
		secret = self.entity
		return secret.ID == ID and len(secret.Game.minionsonBoard(secret.ID)) > 1 and secret.Game.space(secret.ID) > 0
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.summon(npchoice((Huffer, Leokk, Misha))(self.entity.Game, self.entity.ID), -1)
			
			
class PettingZoo(Spell):
	Class, school, name = "Hunter", "", "Petting Zoo"
	requireTarget, mana = False, 3
	index = "DARKMOON_FAIRE~Hunter~Spell~3~~Petting Zoo"
	description = "Summon a 3/3 Strider. Repeat for each Secret you control"
	name_CN = "宠物乐园"
	def available(self):
		return self.Game.space(self.ID) > 0
		
	def effCanTrig(self):
		self.effectViable = self.Game.Secrets.secrets[self.ID] != []
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.summon(DarkmoonStrider(self.Game, self.ID), -1)
		for i in range(len(self.Game.Secrets.secrets[self.ID])):
			self.summon(DarkmoonStrider(self.Game, self.ID), -1)
		return None
		
class DarkmoonStrider(Minion):
	Class, race, name = "Hunter", "Beast", "Darkmoon Strider"
	mana, attack, health = 3, 3, 3
	index = "DARKMOON_FAIRE~Hunter~Minion~3~3~3~Beast~Darkmoon Strider~Uncollectible"
	requireTarget, keyWord, description = False, "", ""
	name_CN = "暗月陆行鸟"
	
	
class RinlingsRifle(Weapon):
	Class, name, description = "Hunter", "Rinling's Rifle", "After your hero attacks, Discover a Secret and cast it"
	mana, attack, durability = 4, 2, 2
	index = "DARKMOON_FAIRE~Hunter~Weapon~4~2~2~Rinling's Rifle~Legendary"
	name_CN = "瑞林的步枪"
	poolIdentifier = "Hunter Secrets"
	@classmethod
	def generatePool(cls, pools):
		classes, lists = [], []
		for Class in pools.Classes:
			secrets = [card for card in pools.ClassCards[Class] if card.description.startswith("Secret:")]
			if secrets:
				classes.append(Class + " Secrets")
				lists.append(secrets)
		return classes, lists

	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_RinlingsRifle(self)]
	
	def decideSecretPool(self):
		HeroClass = self.Game.heroes[self.ID].Class
		key = HeroClass + " Secrets" if HeroClass in ["Hunter", "Mage", "Paladin", "Rogue"] else "Mage Secrets"
		pool = self.rngPool(key)
		for secret in self.Game.Secrets.secrets[self.ID]:
			try: pool.remove(type(secret))  #Deployed Secrets won't show up in the options
			except: pass
		return pool
	
	#case here must be "Discovered" or "Guided"
	def discoverDecided(self, option, case, info_RNGSync=None, info_GUISync=None):
		if case != "Guided": self.Game.picks.append((info_RNGSync, info_GUISync, case == "Random", type(option)))
		option.creator = RinlingsRifle
		option.cast()
		
class Trig_RinlingsRifle(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["HeroAttackedMinion", "HeroAttackedHero"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject == self.entity.Game.heroes[self.entity.ID] and self.entity.onBoard
		
	def text(self, CHN):
		return "在你的英雄攻击后，发现一个奥秘牌并将其施放" if CHN else "After your hero attacks, Discover a Secret and cast it"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.discoverandGenerate(RinlingsRifle, '', lambda : RinlingsRifle.decideSecretPool(self.entity))
		
				
class TramplingRhino(Minion):
	Class, race, name = "Hunter", "Beast", "Trampling Rhino"
	mana, attack, health = 5, 5, 5
	index = "DARKMOON_FAIRE~Hunter~Minion~5~5~5~Beast~Trampling Rhino~Rush"
	requireTarget, keyWord, description = False, "Rush", "Rush. Afte this attacks and kills a minion, excess damage hits the enemy hero"
	name_CN = "狂踏的犀牛"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_TramplingRhino(self)]
		
class Trig_TramplingRhino(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["MinionAttackedMinion"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject == self.entity and target.health < 0
		
	def text(self, CHN):
		return "在该随从攻击并消灭一个随从后，超过目标生命值的伤害会命中 敌方英雄" if CHN \
				else "Afte this attacks and kills a minion, excess damage hits the enemy hero"
				
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		excessDmg = -target.health
		self.entity.dealsDamage(self.entity.Game.heroes[3-self.entity.ID], excessDmg)
		
#Even minions with "Can't attack heroes" still attack hero under her command
#The battlecry alone will not kill the minion summoned.
class MaximaBlastenheimer(Minion):
	Class, race, name = "Hunter", "", "Maxima Blastenheimer"
	mana, attack, health = 6, 4, 4
	index = "DARKMOON_FAIRE~Hunter~Minion~6~4~4~~Maxima Blastenheimer~Battlecry~Legendary"
	requireTarget, keyWord, description = False, "", "Battlecry: Summon a random minion from your deck. It attacks the enemy hero, then dies"
	name_CN = "玛克希玛·雷管"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		minions = [i for i, card in enumerate(self.Game.Hand_Deck.decks[self.ID]) if card.type == "Minion"]
		if minions and self.Game.space(self.ID) > 0:
			minion = self.Game.summonfrom(npchoice(minions), self.ID, self.pos+1, self, source='D')
			if minion:
				#verifySelectable is exclusively for player ordering chars to attack
				self.Game.battle(minion, self.Game.heroes[3-self.ID], verifySelectable=False, useAttChance=True, resolveDeath=False, resetRedirTrig=True)
				if minion.onBoard: self.Game.killMinion(self, minion)
		return None
		
		
class DarkmoonTonk(Minion):
	Class, race, name = "Hunter", "Mech", "Darkmoon Tonk"
	mana, attack, health = 7, 8, 5
	index = "DARKMOON_FAIRE~Hunter~Minion~7~8~5~Mech~Darkmoon Tonk~Deathrattle"
	requireTarget, keyWord, description = False, "", "Deathrattle: Fire four missiles at random enemies that deal 2 damage each"
	name_CN = "暗月坦克"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.deathrattles = [Fire4Missiles(self)]
		
class Fire4Missiles(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		minion = self.entity
		for num in range(4):
			enemies = minion.Game.charsAlive(3-minion.ID)
			if enemies: minion.dealsDamage(npchoice(enemies), 2)
			else: break
			
	def text(self, CHN):
		return "亡语：随机对敌人发射四枚飞弹，每枚飞弹造成2点伤害" if CHN else "Deathrattle: Fire four missiles at random enemies that deal 2 damage each"
		
		
class JewelofNZoth(Spell):
	Class, school, name = "Hunter", "", "Jewel of N'Zoth"
	requireTarget, mana = False, 8
	index = "DARKMOON_FAIRE~Hunter~Spell~8~~Jewel of N'Zoth"
	description = "Summon three friendly Deathrattle minions that died this game"
	name_CN = "恩佐斯宝石"
	def available(self):
		return self.Game.space(self.ID) > 0
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		game = self.Game
		minions = [card for card in game.Counters.minionsDiedThisGame[self.ID] if "~Deathrattle" in card.index]
		if minions:
			minions = npchoice(minions, min(3, len(minions)), replace=False)
			self.summon([minion(game, self.ID) for minion in minions], (-1, "totheRightEnd"))
		return None
		
		
"""Mage cards"""
class ConfectionCyclone(Minion):
	Class, race, name = "Mage", "Elemental", "Confection Cyclone"
	mana, attack, health = 2, 3, 2
	index = "DARKMOON_FAIRE~Mage~Minion~2~3~2~Elemental~Confection Cyclone~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Add two 1/2 Sugar Elementals to your hand"
	name_CN = "甜点飓风"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.addCardtoHand([SugarElemental] * 2, self.ID)
		return None
		
class SugarElemental(Minion):
	Class, race, name = "Mage", "Elemental", "Sugar Elemental"
	mana, attack, health = 1, 1, 2
	index = "DARKMOON_FAIRE~Mage~Minion~1~1~2~Elemental~Sugar Elemental~Uncollectible"
	requireTarget, keyWord, description = False, "", ""
	name_CN = "甜蜜元素"
	
	
class DeckofLunacy(Spell):
	Class, school, name = "Mage", "", "Deck of Lunacy"
	requireTarget, mana = False, 4
	index = "DARKMOON_FAIRE~Mage~Spell~4~~Deck of Lunacy~Legendary"
	description = "Transform spells in your deck into ones that cost (3) more. (They keep their original Cost.)"
	name_CN = "愚人套牌"
	poolIdentifier = "3-Cost Spells"
	@classmethod
	def generatePool(cls, pools):
		spells = {mana: [] for mana in range(3, 11)}
		for cards in pools.ClassCards.values():
			for card in cards:
				if card.type == "Spell" and 2 < card.mana < 11:
					spells[card.mana].append(card)
		return ["%d-Cost Spells"%cost for cost in spells.keys()], spells.values()
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame, ID = self.Game, self.ID
		if curGame.mode == 0:
			if curGame.picks:
				indices, newCards, costs = curGame.picks.pop(0)
			else:
				indices, newCards, costs = [], [], []
				for i, card in enumerate(curGame.Hand_Deck.decks[ID]):
					if card.type == "Spell":
						indices.append(i)
						newCards.append(npchoice(self.rngPool("%d-Cost Spells"%min(10, card.mana+3))))
						costs.append(card.mana)
			if indices:
				newCards = [card(curGame, ID) for card in newCards]
				for card, cost in zip(newCards, costs):
					ManaMod(card, changeby=0, changeto=cost).applies()
				curGame.Hand_Deck.replacePartofDeck(ID, indices, newCards)
		return None
		
		
class GameMaster(Minion):
	Class, race, name = "Mage", "", "Game Master"
	mana, attack, health = 2, 2, 3
	index = "DARKMOON_FAIRE~Mage~Minion~2~2~3~~Game Master"
	requireTarget, keyWord, description = False, "", "The first Secret you play each turn costs (1)"
	name_CN = "游戏管理员"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.auras["The first Secret you play each turn costs (1)"] = ManaAura_1stSecret1(self)
		
class GameManaAura_InTurn1stSecret1(TempManaEffect):
	def __init__(self, Game, ID):
		super().__init__(Game, ID, 0, 1)
		
	def applicable(self, target):
		return target.ID == self.ID and target.description.startswith("Secret:")
		
class ManaAura_1stSecret1(ManaAura_1UsageEachTurn):
	def auraAppears(self):
		game, ID = self.entity.Game, self.entity.ID
		if game.turn == ID and not any(issubclass(card, Secret) for card in game.Counters.cardsPlayedEachTurn[ID][-1]):
			self.aura = GameManaAura_InTurn1stSecret1(game, ID)
			game.Manas.CardAuras.append(self.aura)
			self.aura.auraAppears()
		try: game.trigsBoard[ID]["TurnStarts"].append(self)
		except: game.trigsBoard[ID]["TurnStarts"] = [self]
		
		
class RiggedFaireGame(Secret):
	Class, school, name = "Mage", "", "Rigged Faire Game"
	requireTarget, mana = False, 3
	index = "DARKMOON_FAIRE~Mage~Spell~3~~Rigged Faire Game~~Secret"
	description = "Secret: If you didn't take any damage during your opponent's turn, draw 3 cards"
	name_CN = "非公平游戏"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_RiggedFaireGame(self)]
		
class Trig_RiggedFaireGame(SecretTrigger):
	def __init__(self, entity):
		super().__init__(entity, ["TurnEnds"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0): #target here holds the actual target object
		return self.entity.ID != ID and self.entity.Game.Counters.dmgonHeroThisTurn[self.entity.ID] == 0
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.Game.Hand_Deck.drawCard(self.entity.ID)
		self.entity.Game.Hand_Deck.drawCard(self.entity.ID)
		self.entity.Game.Hand_Deck.drawCard(self.entity.ID)

		
class OccultConjurer(Minion):
	Class, race, name = "Mage", "", "Occult Conjurer"
	mana, attack, health = 4, 4, 4
	index = "DARKMOON_FAIRE~Mage~Minion~4~4~4~~Occult Conjurer~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: If you control a Secret, summon a copy of this"
	name_CN = "隐秘咒术师"
	
	def effCanTrig(self):
		self.effectViable = self.Game.Secrets.secrets[self.ID] != []
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if self.Game.Secrets.secrets[self.ID]:
			Copy = self.selfCopy(self.ID, self) if self.onBoard else type(self)(self.Game, self.ID)
			self.summon(Copy, self.pos+1)
		return None
		
		
class RingToss(Spell):
	Class, school, name = "Mage", "", "Ring Toss"
	requireTarget, mana = False, 4
	index = "DARKMOON_FAIRE~Mage~Spell~4~~Ring Toss~ToCorrupt"
	description = "Discover a Secret and cast it. Corrupt: Discover 2 instead"
	name_CN = "套圈圈"
	poolIdentifier = "Mage Secrets"
	@classmethod
	def generatePool(cls, pools):
		classes, lists = [], []
		for Class in pools.Classes:
			secrets = [card for card in pools.ClassCards[Class] if card.description.startswith("Secret:")]
			if secrets:
				classes.append(Class + " Secrets")
				lists.append(secrets)
		return classes, lists
	
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsHand = [Trig_Corrupt(self, RingToss_Corrupt)] #只有在手牌中才会升级
	
	def decideSecretPool(self):
		HeroClass = self.Game.heroes[self.ID].Class
		key = HeroClass + " Secrets" if HeroClass in ["Hunter", "Mage", "Paladin", "Rogue"] else "Mage Secrets"
		pool = self.rngPool(key)
		for secret in self.Game.Secrets.secrets[self.ID]:
			try: pool.remove(type(secret))  #Deployed Secrets won't show up in the options
			except: pass
		return pool
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.discoverandGenerate(RingToss, comment, lambda : RingToss.decideSecretPool(self))
		return None
		
	def discoverDecided(self, option, case, info_RNGSync=None, info_GUISync=None):
		if case != "Guided": self.Game.picks.append((info_RNGSync, info_GUISync, case == "Random", type(option)))
		option.creator = RingToss
		option.cast()


class RingToss_Corrupt(Spell):
	Class, school, name = "Mage", "", "Ring Toss"
	requireTarget, mana = False, 4
	index = "DARKMOON_FAIRE~Mage~Spell~4~~Ring Toss~Corrupted~Uncollectible"
	description = "Corrupted. Discover 2 Secrets and cast them"
	name_CN = "套圈圈"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		for num in range(2):
			self.discoverandGenerate(RingToss, comment, lambda: RingToss.decideSecretPool(self))
		return None
		
		
class FireworkElemental(Minion):
	Class, race, name = "Mage", "Elemental", "Firework Elemental"
	mana, attack, health = 5, 3, 5
	index = "DARKMOON_FAIRE~Mage~Minion~5~3~5~Elemental~Firework Elemental~Battlecry~ToCorrupt"
	requireTarget, keyWord, description = True, "", "Battlecry: Deal 3 damage to a minion. Corrupt: Deal 12 damage instead"
	name_CN = "焰火元素"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsHand = [Trig_Corrupt(self, FireworkElemental_Corrupt)] #只有在手牌中才会升级
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			self.dealsDamage(target, 3)
		return target
		
class FireworkElemental_Corrupt(Minion):
	Class, race, name = "Mage", "Elemental", "Firework Elemental"
	mana, attack, health = 5, 3, 5
	index = "DARKMOON_FAIRE~Mage~Minion~5~3~5~Elemental~Firework Elemental~Battlecry~Corrupted~Uncollectible"
	requireTarget, keyWord, description = True, "", "Corrupted. Battlecry: Deal 12 damage to a minion"
	name_CN = "焰火元素"
	
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			self.dealsDamage(target, 12)
		return target
		
		
class SaygeSeerofDarkmoon(Minion):
	Class, race, name = "Mage", "", "Sayge, Seer of Darkmoon"
	mana, attack, health = 6, 5, 5
	index = "DARKMOON_FAIRE~Mage~Minion~6~5~5~~Sayge, Seer of Darkmoon~Battlecry~Legendary"
	requireTarget, keyWord, description = False, "", "Battlecry: Draw 1 card(Upgraded for each friendly Secret that has triggered this game!)"
	name_CN = "暗月先知赛格"
	
	def text(self, CHN):
		num = self.Game.Counters.numSecretsTriggeredThisGame[self.ID] + 1
		return "战吼：抽%d张牌。(在本局对战中，每触发一个友方奥秘教会升级)"%num if CHN \
				else "Battlecry: Draw %d card(Upgraded for each friendly Secret that has triggered this game!)"%num
				
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		num = curGame.Counters.numSecretsTriggeredThisGame[self.ID] + 1
		for i in range(num):
			curGame.Hand_Deck.drawCard(self.ID)
		return None
		
		
class MaskofCThun(Spell):
	Class, school, name = "Mage", "", "Mask of C'Thun"
	requireTarget, mana = False, 7
	index = "DARKMOON_FAIRE~Mage~Spell~7~~Mask of C'Thun"
	description = "Deal 10 damage randomly split among all enemies"
	name_CN = "克苏恩面具"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		damage = (10 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		side, game = 3-self.ID, self.Game
		for num in range(damage):
			objs = game.charsAlive(side)
			if objs: self.dealsDamage(npchoice(objs), 1)
			else: break
		return None
		
		
class GrandFinale(Spell):
	Class, school, name = "Mage", "Fire", "Grand Finale"
	requireTarget, mana = False, 8
	index = "DARKMOON_FAIRE~Mage~Spell~8~Fire~Grand Finale"
	description = "Summon an 8/8 Elemental. Repeat for each Elemental you played last turn"
	name_CN = "华丽谢幕"
	def effCanTrig(self):
		self.effectViable = self.Game.Counters.numElementalsPlayedLastTurn[self.ID] > 0
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		game = self.Game
		self.summon(ExplodingSparkler(game, self.ID), -1)
		for i in range(game.Counters.numElementalsPlayedLastTurn[self.ID]):
			self.summon(ExplodingSparkler(game, self.ID), -1)
		return target
		
class ExplodingSparkler(Minion):
	Class, race, name = "Mage", "Elemental", "Exploding Sparkler"
	mana, attack, health = 8, 8, 8
	index = "DARKMOON_FAIRE~Mage~Minion~8~8~8~Elemental~Exploding Sparkler~Uncollectible"
	requireTarget, keyWord, description = False, "", ""
	name_CN = "爆破烟火"
	
"""Paladin cards"""
class OhMyYogg(Secret):
	Class, school, name = "Paladin", "Shadow", "Oh My Yogg!"
	requireTarget, mana = False, 1
	index = "DARKMOON_FAIRE~Paladin~Spell~1~Shadow~Oh My Yogg!~~Secret"
	description = "Secret: When your opponent casts a spell, they instead cast a random one of the same Cost"
	name_CN = "古神在上"
	poolIdentifier = "0-Cost Spells"
	@classmethod
	def generatePool(cls, pools):
		spells = {mana: [] for mana in range(3, 11)}
		for cards in pools.ClassCards.values():
			for card in cards:
				if card.type == "Spell" and 2 < card.mana < 11:
					spells[card.mana].append(card)
		return ["%d-Cost Spells" % cost for cost in spells.keys()], spells.values()
	
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_OhMyYogg(self)]
		
class Trig_OhMyYogg(SecretTrigger):
	def __init__(self, entity):
		super().__init__(entity, ["SpellOKtoCast?"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject[0].ID != self.entity.ID and subject is not None
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		subject[0] = npchoice(self.rngPool("%d-Cost Spells"%number))(self.entity.Game, 3-self.entity.ID)
		
			
class RedscaleDragontamer(Minion):
	Class, race, name = "Paladin", "Murloc", "Redscale Dragontamer"
	mana, attack, health = 2, 2, 3
	index = "DARKMOON_FAIRE~Paladin~Minion~2~2~3~Murloc~Redscale Dragontamer~Battlecry"
	requireTarget, keyWord, description = False, "", "Deathrattle: Draw a Dragon"
	name_CN = "赤鳞驯龙者"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.deathrattles = [DrawaDragon(self)]
		
class DrawaDragon(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		minions = [i for i, card in enumerate(self.entity.Game.Hand_Deck.decks[self.entity.ID]) if card.type == "Minion" and "Dragon" in card.race]
		if minions: self.entity.Game.Hand_Deck.drawCard(self.entity.ID, npchoice(minions))
			
	def text(self, CHN):
		return "亡语：抽一张龙牌" if CHN else "Deathrattle: Draw a Dragon"
		
		
class SnackRun(Spell):
	Class, school, name = "Paladin", "", "Snack Run"
	requireTarget, mana = False, 2
	index = "DARKMOON_FAIRE~Paladin~Spell~2~~Snack Run"
	description = "Discover a spell. Restore Health to your hero equal to its Cost"
	name_CN = "零食大冲关"
	poolIdentifier = "Paladin Spells"
	@classmethod
	def generatePool(cls, pools):
		return [Class+" Spells" for Class in pools.Classes], \
				[[card for card in cards if card.type == "Spell"] for cards in pools.ClassCards.values()]

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.discoverandGenerate(SnackRun, comment, lambda : self.rngPool(classforDiscover(self) + " Spells"))
		return None
		
	def discoverDecided(self, option, case, info_RNGSync=None, info_GUISync=None):
		heal = option.mana * (2 ** self.countHealDouble())
		self.handleDiscoverGeneratedCard(option, case, info_RNGSync, info_GUISync)
		self.restoresHealth(self.Game.heroes[self.ID], heal)
		
		
class CarnivalBarker(Minion):
	Class, race, name = "Paladin", "", "Carnival Barker"
	mana, attack, health = 3, 3, 2
	index = "DARKMOON_FAIRE~Paladin~Minion~3~3~2~~Carnival Barker"
	requireTarget, keyWord, description = False, "", "Whenever you summon a 1-Health minion, give +1/+2"
	name_CN = "狂欢报幕员"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_CarnivalBarker(self)]
		
class Trig_CarnivalBarker(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["MinionSummoned"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject.ID == self.entity.ID and subject.health == 1 and subject != self.entity
		
	def text(self, CHN):
		return "每当你召唤一个生命值为1的随从，便使其获得+1/+2" if CHN else "Whenever you summon a 1-Health minion, give +1/+2"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		subject.buffDebuff(1, 2)
		
		
class DayattheFaire(Spell):
	Class, school, name = "Paladin", "", "Day at the Faire"
	requireTarget, mana = False, 3
	index = "DARKMOON_FAIRE~Paladin~Spell~3~~Day at the Faire~ToCorrupt"
	description = "Summon 3 Silver Hand Recruits. Corrupt: Summon 5"
	name_CN = "游园日"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsHand = [Trig_Corrupt(self, DayattheFaire_Corrupt)] #只有在手牌中才会升级
		
	def available(self):
		return self.Game.space(self.ID) > 0
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		self.summon([SilverHandRecruit(self.Game, self.ID) for i in range(3)], (-1, "totheRightEnd"))
		return None
		
class DayattheFaire_Corrupt(Spell):
	Class, school, name = "Paladin", "", "Day at the Faire"
	requireTarget, mana = False, 3
	index = "DARKMOON_FAIRE~Paladin~Spell~3~~Day at the Faire~Corrupted~Uncollectible"
	description = "Corrupted: Summon 5 Silver Hand Recruits"
	name_CN = "游园日"
	def available(self):
		return self.Game.space(self.ID) > 0
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		self.summon([SilverHandRecruit(self.Game, self.ID) for i in range(5)], (-1, "totheRightEnd"))
		return None
		
		
class BalloonMerchant(Minion):
	Class, race, name = "Paladin", "", "Balloon Merchant"
	mana, attack, health = 4, 3, 5
	index = "DARKMOON_FAIRE~Paladin~Minion~4~3~5~~Balloon Merchant~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Give your Silver Hand Recruits +1 Attack and Divine Shield"
	name_CN = "气球商人"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		for minion in self.Game.minionsonBoard(self.ID):
			if minion.name == "Silver Hand Recruit":
				minion.buffDebuff(1, 0)
				minion.getsStatus("Divine Shield")
		return None
		
		
class CarouselGryphon(Minion):
	Class, race, name = "Paladin", "Mech", "Carousel Gryphon"
	mana, attack, health = 5, 5, 5
	index = "DARKMOON_FAIRE~Paladin~Minion~5~5~5~Mech~Carousel Gryphon~Divine Shield~ToCorrupt"
	requireTarget, keyWord, description = False, "Divine Shield", "Divine Shield. Corrupt: Gain +3/+3 and Taunt"
	name_CN = "旋转木马"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsHand = [Trig_Corrupt(self, CarouselGryphon_Corrupt)] #只有在手牌中才会升级
		
class CarouselGryphon_Corrupt(Minion):
	Class, race, name = "Paladin", "Mech", "Carousel Gryphon"
	mana, attack, health = 5, 8, 8
	index = "DARKMOON_FAIRE~Paladin~Minion~5~8~8~Mech~Carousel Gryphon~Divine Shield~Taunt~Corrupted~Uncollectible"
	requireTarget, keyWord, description = False, "Divine Shield,Taunt", "Divine Shield, Taunt"
	name_CN = "旋转木马"
	
	
class LothraxiontheRedeemed(Minion):
	Class, race, name = "Paladin", "Demon", "Lothraxion the Redeemed"
	mana, attack, health = 5, 5, 5
	index = "DARKMOON_FAIRE~Paladin~Minion~5~5~5~Demon~Lothraxion the Redeemed~Battlecry~Legendary"
	requireTarget, keyWord, description = False, "", "Battlecry: For the rest of the game, after you summon a Silver Hand Recruit, give it Divine Shield"
	name_CN = "救赎者洛萨克森"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		LothraxiontheRedeemed_Effect(self.Game, self.ID).connect()
		return None
		
class LothraxiontheRedeemed_Effect:
	def __init__(self, Game, ID):
		self.Game, self.ID = Game, ID
		self.card = LothraxiontheRedeemed(Game, ID)
		
	def connect(self):
		try: trigs = self.Game.trigsBoard[self.ID]["MinionBeenSummoned"]
		except: trigs = self.Game.trigsBoard[self.ID]["MinionBeenSummoned"] = []
		if not any(isinstance(trig, LothraxiontheRedeemed_Effect) for trig in trigs):
			self.Game.trigAuras[self.ID].append(self)
			trigs.append(self)
			if self.Game.GUI: self.Game.GUI.heroZones[self.ID].addaTrig(self.card)
	
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject.ID == self.ID and subject.name == "Silver Hand Recruit"
		
	def trig(self, signal, ID, subject, target, number, comment, choice=0):
		if self.canTrig(signal, ID, subject, target, number, comment):
			if self.Game.GUI: self.Game.GUI.showOffBoardTrig(self.card)
			self.effect(signal, ID, subject, target, number, comment)
			
	def text(self, CHN):
		return "在本局对战的剩余时间内，在你召唤一个白银之手新兵后，使其获得圣盾" if CHN \
				else "For the rest of the game, after you summon a Silver Hand Recruit, give it Divine Shield"
				
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		subject.getsStatus("Divine Shield")
		
	def createCopy(self, game): #不是纯的只在回合结束时触发，需要完整的createCopy
		if self not in game.copiedObjs: #这个扳机没有被复制过
			trigCopy = type(self)(game, self.ID)
			game.copiedObjs[self] = trigCopy
			return trigCopy
		else: #一个扳机被复制过了，则其携带者也被复制过了
			return game.copiedObjs[self]
			
			
class HammeroftheNaaru(Weapon):
	Class, name, description = "Paladin", "Hammer of the Naaru", "Battlecry: Summon a 6/6 Holy Elemental with Taunt"
	mana, attack, durability = 6, 3, 3
	index = "DARKMOON_FAIRE~Paladin~Weapon~6~3~3~Hammer of the Naaru~Battlecry"
	name_CN = "纳鲁之锤"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.summon(HolyElemental(self.Game, self.ID), -1)
		return None
		
class HolyElemental(Minion):
	Class, race, name = "Paladin", "Elemental", "Holy Elemental"
	mana, attack, health = 6, 6, 6
	index = "DARKMOON_FAIRE~Paladin~Minion~6~6~6~Elemental~Holy Elemental~Taunt~Uncollectible"
	requireTarget, keyWord, description = False, "Taunt", "Taunt"
	name_CN = "神圣元素"
	
	
class HighExarchYrel(Minion):
	Class, race, name = "Paladin", "", "High Exarch Yrel"
	mana, attack, health = 8, 7, 5
	index = "DARKMOON_FAIRE~Paladin~Minion~8~7~5~~High Exarch Yrel~Battlecry~Legendary"
	requireTarget, keyWord, description = False, "", "Battlecry: If your deck has no Neutral cards, gain Rush, Lifesteal, Taunt, and Divine Shield"
	name_CN = "大主教伊瑞尔"
	
	def effCanTrig(self):
		self.effectViable = all(card.Class != "Neutral" for card in self.Game.Hand_Deck.decks[self.ID])
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if all(card.Class != "Neutral" for card in self.Game.Hand_Deck.decks[self.ID]):
			self.getsStatus("Rush")
			self.getsStatus("Lifesteal")
			self.getsStatus("Taunt")
			self.getsStatus("Divine Shield")
		return None
		
"""Priest cards"""
class Insight(Spell):
	Class, school, name = "Priest", "Shadow", "Insight"
	requireTarget, mana = False, 2
	index = "DARKMOON_FAIRE~Priest~Spell~2~Shadow~Insight~ToCorrupt"
	description = "Draw a minion. Corrupt: Reduce its Cost by (2)"
	name_CN = "洞察"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsHand = [Trig_Corrupt(self, Insight_Corrupt)] #只有在手牌中才会升级
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		minions = [i for i, card in enumerate(self.Game.Hand_Deck.decks[self.ID]) if card.type == "Minion"]
		if minions: self.Game.Hand_Deck.drawCard(self.ID, npchoice(minions))
		return None
		
class Insight_Corrupt(Spell):
	Class, school, name = "Priest", "Shadow", "Insight"
	requireTarget, mana = False, 2
	index = "DARKMOON_FAIRE~Priest~Spell~2~Shadow~Insight~Corrupted~Uncollectible"
	description = "Corrupted. Draw a minion. Reduce its Cost by (2)"
	name_CN = "洞察"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		minions = [i for i, card in enumerate(self.Game.Hand_Deck.decks[self.ID]) if card.type == "Minion"]
		if minions:
			minion = self.Game.Hand_Deck.drawCard(self.ID, npchoice(minions))[0]
			if minion: ManaMod(minion, changeby=-2).applies()
		return None
		
		
class FairgroundFool(Minion):
	Class, race, name = "Priest", "", "Fairground Fool"
	mana, attack, health = 3, 4, 3
	index = "DARKMOON_FAIRE~Priest~Minion~3~4~3~~Fairground Fool~Taunt~ToCorrupt"
	requireTarget, keyWord, description = False, "Taunt", "Taunt. Corrupt: Gain +4 Health"
	name_CN = "游乐园小丑"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsHand = [Trig_Corrupt(self, FairgroundFool_Corrupt)] #只有在手牌中才会升级
		
class FairgroundFool_Corrupt(Minion):
	Class, race, name = "Priest", "", "Fairground Fool"
	mana, attack, health = 3, 4, 7
	index = "DARKMOON_FAIRE~Priest~Minion~3~4~7~~Fairground Fool~Taunt~Corrupted~Uncollectible"
	requireTarget, keyWord, description = False, "Taunt", "Corrupted. Taunt"
	name_CN = "游乐园小丑"
	
	
class NazmaniBloodweaver(Minion):
	Class, race, name = "Priest", "", "Nazmani Bloodweaver"
	mana, attack, health = 3, 2, 5
	index = "DARKMOON_FAIRE~Priest~Minion~3~2~5~~Nazmani Bloodweaver"
	requireTarget, keyWord, description = False, "", "After you cast a spell, reduce the Cost of a random card in your hand by (1)"
	name_CN = "纳兹曼尼织血者"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_NazmaniBloodweaver(self)]
		
class Trig_NazmaniBloodweaver(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["SpellBeenPlayed"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject.ID == self.entity.ID
		
	def text(self, CHN):
		return "在你施放一个法术后，随机使你的一张手牌法力值消耗减少(1)点" if CHN \
				else "After you cast a spell, reduce the Cost of a random card in your hand by (1)"
				
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		curGame = self.entity.Game
		if curGame.mode == 0:
			if curGame.picks:
				i = curGame.picks.pop(0)
			else:
				num = len(curGame.Hand_Deck.hands[self.entity.ID])
				i = nprandint(num) if num else -1
			if i > -1:
				ManaMod(curGame.Hand_Deck.hands[self.entity.ID][i], changeby=-1, changeto=-1).applies()
				
				
class PalmReading(Spell):
	Class, school, name = "Priest", "Shadow", "Palm Reading"
	requireTarget, mana = False, 3
	index = "DARKMOON_FAIRE~Priest~Spell~3~Shadow~Palm Reading"
	description = "Discover a spell. Reduce the Cost of spells in your hand by (1)"
	name_CN = "解读手相"
	poolIdentifier = "Priest Spells"
	@classmethod
	def generatePool(cls, pools):
		return [Class+" Spells" for Class in pools.Classes], \
				[[card for card in cards if card.type == "Spell"] for cards in pools.ClassCards.values()]

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.discoverandGenerate(PalmReading, comment, lambda : self.rngPool(classforDiscover(self)+" Spells"))
		for card in self.Game.Hand_Deck.hands[self.ID]:
			if card.type == "Spell": ManaMod(card, changeby=-1).applies()
		return None
		
		
class AuspiciousSpirits(Spell):
	Class, school, name = "Priest", "Shadow", "Auspicious Spirits"
	requireTarget, mana = False, 4
	index = "DARKMOON_FAIRE~Priest~Spell~4~Shadow~Auspicious Spirits~ToCorrupt"
	description = "Summon a random 4-Cost minion. Corrupt: Summon a 7-Cost minion instead"
	name_CN = "吉兆"
	poolIdentifier = "4-Cost Minions to Summon"
	@classmethod
	def generatePool(cls, pools):
		return "4-Cost Minions to Summon", pools.MinionsofCost[4]
		
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsHand = [Trig_Corrupt(self, AuspiciousSpirits_Corrupt)] #只有在手牌中才会升级
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.summon(npchoice(self.rngPool("4-Cost Minions to Summon"))(self.Game, self.ID), -1)
		return None
		
class AuspiciousSpirits_Corrupt(Spell):
	Class, school, name = "Priest", "Shadow", "Auspicious Spirits"
	requireTarget, mana = False, 4
	index = "DARKMOON_FAIRE~Priest~Spell~4~Shadow~Auspicious Spirits~Corrupted~Uncollectible"
	description = "Corrupted. Summon a 7-Cost minion"
	name_CN = "吉兆"
	poolIdentifier = "7-Cost Minions to Summon"
	@classmethod
	def generatePool(cls, pools):
		return "7-Cost Minions to Summon", pools.MinionsofCost[7]
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.summon(npchoice(self.rngPool("7-Cost Minions to Summon"))(self.Game, self.ID), -1)
		return None
		
		
class TheNamelessOne(Minion):
	Class, race, name = "Priest", "", "The Nameless One"
	mana, attack, health = 4, 4, 4
	index = "DARKMOON_FAIRE~Priest~Minion~4~4~4~~The Nameless One~Battlecry~Legendary"
	requireTarget, keyWord, description = True, "", "Battlecry: Choose a minion. Become a 4/4 copy of it, then Silence it"
	name_CN = "无名者"
	
	def targetExists(self, choice=0):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target != self and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			if not self.dead and self.Game.minionPlayed == self and (self.onBoard or self.inHand): #战吼触发时自己不能死亡。
				Copy = target.selfCopy(self.ID, self, 4, 4) if target.onBoard or target.inHand else type(target)(self.Game, self.ID)
				self.transform(self, Copy)
			target.getsSilenced()
		return target
		
		
class FortuneTeller(Minion):
	Class, race, name = "Priest", "Mech", "Fortune Teller"
	mana, attack, health = 5, 3, 3
	index = "DARKMOON_FAIRE~Priest~Minion~5~3~3~Mech~Fortune Teller~Taunt~Battlecry"
	requireTarget, keyWord, description = False, "Taunt", "Taunt. Battlecry: Gain +1/+1 for each spell in your hand"
	name_CN = "占卜机"
	#For self buffing effects, being dead and removed before battlecry will prevent the battlecry resolution.
	#If this minion is returned hand before battlecry, it can still buff it self according to living friendly minions.
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if self.onBoard or self.inHand: #For now, no battlecry resolution shuffles this into deck.
			num = sum(card.type == "Spell" for card in self.Game.Hand_Deck.hands[self.ID])
			self.buffDebuff(num, num)
		return None
		
		
class IdolofYShaarj(Spell):
	Class, school, name = "Priest", "", "Idol of Y'Shaarj"
	requireTarget, mana = False, 8
	index = "DARKMOON_FAIRE~Priest~Spell~8~~Idol of Y'Shaarj"
	description = "Summon a 10/10 copy of a minion in your deck"
	name_CN = "亚煞极神像"
	def available(self):
		return self.Game.space(self.ID) > 0
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		minions = [card for card in self.Game.Hand_Deck.decks[self.ID] if card.type == "Minion"]
		if minions: self.summon(npchoice(minions).selfCopy(self.ID, self, attack=10, health=10), -1)
		return None
		
		
class GhuuntheBloodGod(Minion):
	Class, race, name = "Priest", "", "G'huun the Blood God"
	mana, attack, health = 8, 8, 8
	index = "DARKMOON_FAIRE~Priest~Minion~8~8~8~~G'huun the Blood God~Battlecry~Legendary"
	requireTarget, keyWord, description = False, "", "Draw 2 cards. They cost Health instead of Mana"
	name_CN = "戈霍恩，鲜血之神"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		card1 = self.Game.Hand_Deck.drawCard(self.ID)[0]
		card2 = self.Game.Hand_Deck.drawCard(self.ID)[0]
		if card1: card1.getsStatus("Cost Health Instead")
		if card2: card2.getsStatus("Cost Health Instead")
		return None
		
		
class BloodofGhuun(Minion):
	Class, race, name = "Priest", "Elemental", "Blood of G'huun"
	mana, attack, health = 9, 8, 8
	index = "DARKMOON_FAIRE~Priest~Minion~9~8~8~Elemental~Blood of G'huun~Taunt"
	requireTarget, keyWord, description = False, "Taunt", "Taunt. At the end of your turn, summon a 5/5 copy of a minion in your deck"
	name_CN = "戈霍恩之血"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_BloodofGhuun(self)]
		
class Trig_BloodofGhuun(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["TurnEnds"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and ID == self.entity.ID
		
	def text(self, CHN):
		return "在你的回合结束时，召唤一个你的牌库中的随从的5/5复制" if CHN else "At the end of your turn, summon a 5/5 copy of a minion in your deck"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		minion = self.entity
		minions = [card for card in minion.Game.Hand_Deck.decks[minion.ID] if card.type == "Minion"]
		if minions and minion.Game.space(self.entity.ID) > 0:
			minion.summon(npchoice(minions).selfCopy(minion.ID, minion, 5, 5), minion.pos+1)
				
"""Rogue cards"""
class PrizePlunderer(Minion):
	Class, race, name = "Rogue", "Pirate", "Prize Plunderer"
	mana, attack, health = 1, 2, 1
	index = "DARKMOON_FAIRE~Rogue~Minion~1~2~1~Pirate~Prize Plunderer~Combo"
	requireTarget, keyWord, description = True, "", "Combo: Deal 1 damage to a minion for each other card you've played this turn"
	name_CN = "奖品掠夺者"
	
	def returnTrue(self, choice=0):
		return self.Game.Counters.numCardsPlayedThisTurn[self.ID] > 0
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target != self and target.onBoard
		
	def effCanTrig(self):
		self.effectViable = self.Game.Counters.numCardsPlayedThisTurn[self.ID] > 0
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		numOtherCards = self.Game.Counters.numCardsPlayedThisTurn[self.ID]
		if target and numOtherCards > 0:
			self.dealsDamage(target, numOtherCards)
		return target
		
		
class FoxyFraud(Minion):
	Class, race, name = "Rogue", "", "Foxy Fraud"
	mana, attack, health = 2, 3, 2
	index = "DARKMOON_FAIRE~Rogue~Minion~2~3~2~~Foxy Fraud~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Your next Combo this turn costs (2) less"
	name_CN = "狐人老千"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		tempAura = GameManaAura_InTurnNextCombo2Less(self.Game, self.ID)
		self.Game.Manas.CardAuras.append(tempAura)
		tempAura.auraAppears()
		return None
		
class GameManaAura_InTurnNextCombo2Less(TempManaEffect):
	def __init__(self, Game, ID, changeby=0, changeto=-1):
		super().__init__(Game, ID, -2, -1)
		
	def applicable(self, target):
		return target.ID == self.ID and "~Combo" in target.index
		
		
class ShadowClone(Secret):
	Class, school, name = "Rogue", "Shadow", "Shadow Clone"
	requireTarget, mana = False, 2
	index = "DARKMOON_FAIRE~Rogue~Spell~2~Shadow~Shadow Clone~~Secret"
	description = "Secret: After a minion attacks your hero, summon a copy of it with Stealth"
	name_CN = "暗影克隆"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_ShadowClone(self)]
		
class Trig_ShadowClone(SecretTrigger):
	def __init__(self, entity):
		super().__init__(entity, ["MinionAttackedHero"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.ID != self.entity.Game.turn and target == self.entity.Game.heroes[self.entity.ID]
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		Copy = subject.selfCopy(self.entity.ID, self.entity)
		self.entity.summon(Copy, -1)
		
		
class SweetTooth(Minion):
	Class, race, name = "Rogue", "", "Sweet Tooth"
	mana, attack, health = 2, 3, 2
	index = "DARKMOON_FAIRE~Rogue~Minion~2~3~2~~Sweet Tooth~ToCorrupt"
	requireTarget, keyWord, description = False, "", "Corrupt: Gain +2 Attack and Stealth"
	name_CN = "甜食狂"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsHand = [Trig_Corrupt(self, SweetTooth_Corrupt)] #只有在手牌中才会升级
		
class SweetTooth_Corrupt(Minion):
	Class, race, name = "Rogue", "", "Sweet Tooth"
	mana, attack, health = 2, 5, 2
	index = "DARKMOON_FAIRE~Priest~Minion~2~5~2~~Sweet Tooth~Stealth~Corrupted~Uncollectible"
	requireTarget, keyWord, description = False, "Stealth", "Corrupted. Stealth"
	name_CN = "甜食狂"
	
	
class Swindle(Spell):
	Class, school, name = "Rogue", "", "Swindle"
	requireTarget, mana = False, 2
	index = "DARKMOON_FAIRE~Rogue~Spell~2~~Swindle~Combo"
	description = "Draw a spell. Combo: And a minion"
	name_CN = "行骗"
	def effCanTrig(self):
		self.effectViable = self.Game.Counters.numCardsPlayedThisTurn[self.ID] > 0
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		canTrig = self.Game.Counters.numCardsPlayedThisTurn[self.ID] > 0
		typeCards = ("Spell", "Minion") if canTrig else ("Spell")
		for typeCard in typeCards:
			cards = [i for i, card in enumerate(self.Game.Hand_Deck.decks[self.ID]) if card.type == typeCard]
			if cards: self.Game.Hand_Deck.drawCard(self.ID, npchoice(cards))
		return None
		
		
class TenwuoftheRedSmoke(Minion):
	Class, race, name = "Rogue", "", "Tenwu of the Red Smoke"
	mana, attack, health = 2, 3, 2
	index = "DARKMOON_FAIRE~Rogue~Minion~2~3~2~~Tenwu of the Red Smoke~Battlecry~Legendary"
	requireTarget, keyWord, description = True, "", "Battlecry: Return a friendly minion to you hand. It costs (1) less this turn"
	name_CN = "'赤烟'腾武"
	
	def targetExists(self, choice=0):
		return self.selectableFriendlyMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.ID == self.ID and target != self and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target and target.onBoard:
			self.Game.returnMiniontoHand(target)
			if target.inHand: ManaMod_Cost1LessThisTurn(target).applies()
		return target
		
class ManaMod_Cost1LessThisTurn:
	def __init__(self, card):
		self.card = card
		self.changeby, self.changeto = -1, -1
		self.source = None
		
	def handleMana(self):
		if self.card.mana > 0: self.card.mana -= 1
		
	def applies(self):
		card = self.card
		card.manaMods.append(self)
		if card in card.Game.Hand_Deck.hands[card.ID]:
			try: card.Game.trigsBoard[card.ID]["TurnEnds"].append(self)
			except: card.Game.trigsBoard[card.ID]["TurnEnds"] = [self]
			card.Game.Manas.calcMana_Single(card)
			
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.card.inHand
		
	def trig(self, signal, ID, subject, target, number, comment, choice=0):
		self.getsRemoved()
		self.card.Game.Manas.calcMana_Single(self.card)
		
	def getsRemoved(self):
		try: self.card.Game.trigsBoard[self.card.ID]["TurnEnds"].remove(self)
		except: pass
		try: self.card.manaMods.remove(self)
		except: pass
		
	def selfCopy(self, recipient):
		return ManaMod_Cost1LessThisTurn(recipient)
		
		
class CloakofShadows(Spell):
	Class, school, name = "Rogue", "Shadow", "Cloak of Shadows"
	requireTarget, mana = False, 3
	index = "DARKMOON_FAIRE~Rogue~Spell~3~Shadow~Cloak of Shadows"
	description = "Give your hero Stealth for 1 turn"
	name_CN = "暗影斗篷"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.Game.heroes[self.ID].status["Temp Stealth"] += 1
		return None
		
		
class TicketMaster(Minion):
	Class, race, name = "Rogue", "", "Ticket Master"
	mana, attack, health = 3, 4, 3
	index = "DARKMOON_FAIRE~Rogue~Minion~3~4~3~~Ticket Master~Deathrattle"
	requireTarget, keyWord, description = False, "", "Deathrattle: Shuffle 3 Tickets into your deck. When drawn, summon a 3/3 Plush Bear"
	name_CN = "奖券老板"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.deathrattles = [Shuffle3TicketsintoYourDeck(self)]
		
class Shuffle3TicketsintoYourDeck(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		game, ID = self.entity.Game, self.entity.ID
		game.Hand_Deck.shuffleintoDeck([Tickets(game, ID) for i in range(3)], creator=self.entity)
		return None
		
	def text(self, CHN):
		return "亡语：将3张奖券洗入你的牌库" if CHN else "Deathrattle: Shuffle 3 Tickets into your deck"
		
class Tickets(Spell):
	Class, school, name = "Rogue", "", "Tickets"
	requireTarget, mana = False, 3
	index = "DARKMOON_FAIRE~Rogue~Spell~3~~Tickets~Casts When Drawn~Uncollectible"
	description = "Casts When Drawn. Summon a 3/3 Plush Bear"
	name_CN = "奖券"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.summon(PlushBear(self.Game, self.ID), -1)
		return None
		
class PlushBear(Minion):
	Class, race, name = "Rogue", "", "Plush Bear"
	mana, attack, health = 3, 3, 3
	index = "DARKMOON_FAIRE~Rogue~Minion~3~3~3~~Plush Bear~Uncollectible"
	requireTarget, keyWord, description = False, "", ""
	name_CN = "玩具熊"
	
	
class MalevolentStrike(Spell):
	Class, school, name = "Rogue", "", "Malevolent Strike"
	requireTarget, mana = True, 5
	index = "DARKMOON_FAIRE~Rogue~Spell~5~~Malevolent Strike"
	description = "Destroy a minion. Costs (1) less for each card in your deck that didn't start there"
	name_CN = "致伤打击"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsHand = [Trig_MalevolentStrike(self)]
		
	def selfManaChange(self):
		if self.inHand:
			self.mana -= sum(card.creator != "" for card in self.Game.Hand_Deck.decks[self.ID])
			self.mana = max(0, self.mana)
			
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			self.Game.killMinion(self, target)
		return target
		
class Trig_MalevolentStrike(TrigHand):
	def __init__(self, entity):
		super().__init__(entity, ["DeckCheck"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.inHand and ID == self.entity.ID
		
	def text(self, CHN):
		return "牌库发生变化的时候，重新计算费用" if CHN else "When the deck changes, recalculate the cost"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.Game.Manas.calcMana_Single(self.entity)
		
		
class GrandEmpressShekzara(Minion):
	Class, race, name = "Rogue", "", "Grand Empress Shek'zara"
	mana, attack, health = 6, 5, 7
	index = "DARKMOON_FAIRE~Rogue~Minion~6~5~7~~Grand Empress Shek'zara~Battlecry~Legendary"
	requireTarget, keyWord, description = False, "", "Battlecry: Discover a card in your deck and draw all copies of it"
	name_CN = "大女皇夏柯扎拉"
	
	def drawCopiesofType(self, cardType): #info is the index of the card in player's deck
		Hand_Deck, ID, index, found = self.Game.Hand_Deck, self.ID, 0, False
		while True:
			for i, card in enumerate(Hand_Deck.decks[ID]):
				if isinstance(card, cardType):
					index, found = i, True
					break
			if found:
				found = False
				if not Hand_Deck.drawCard(ID, i)[0]: break #假设发生了疲劳和爆牌，则停止抽牌
			else: break
			
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.discoverfromList(GrandEmpressShekzara, comment, conditional=lambda card: True,
							  ls=self.Game.Hand_Deck.decks[self.ID])
		return None
		
	def discoverDecided(self, option, case, info_RNGSync=None, info_GUISync=None):
		self.handleDiscoveredCardfromList(option, case, self.Game.Hand_Deck.decks[self.ID],
										  lambda index, card: GrandEmpressShekzara.drawCopiesofType(self, type(card)),
										  info_RNGSync, info_GUISync)
		
		
"""Shaman cards"""
class Revolve(Spell):
	Class, school, name = "Shaman", "", "Revolve"
	requireTarget, mana = False, 1
	index = "DARKMOON_FAIRE~Shaman~Spell~1~~Revolve"
	description = "Transform all minions into random ones with the same Cost"
	name_CN = "异变轮转"
	poolIdentifier = "1-Cost Minions to Summon"
	@classmethod
	def generatePool(cls, pools):
		return ["%d-Cost Minions to Summon"%cost for cost in pools.MinionsofCost.keys()], \
				list(pools.MinionsofCost.values())
				
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		game = self.Game
		minions = game.minionsonBoard(1) + game.minionsonBoard(2)
		newMinions = [npchoice(self.rngPool("%d-Cost Minions to Summon"%minion.mana)) for minion in minions]
		for minion, newMinion in zip(minions, newMinions):
			self.transform(minion, newMinion(game, minion.ID))
		return None
		
		
class CagematchCustodian(Minion):
	Class, race, name = "Shaman", "Elemental", "Cagematch Custodian"
	mana, attack, health = 2, 2, 2
	index = "DARKMOON_FAIRE~Shaman~Minion~2~2~2~Elemental~Cagematch Custodian~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Draw a weapon"
	name_CN = "笼斗管理员"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		weapons = [i for i, card in enumerate(self.Game.Hand_Deck.decks[self.ID]) if card.type == "Weapon"]
		if weapons: self.Game.Hand_Deck.drawCard(self.ID, npchoice(weapons))
		return None
		
		
class DeathmatchPavilion(Spell):
	Class, school, name = "Shaman", "", "Deathmatch Pavilion"
	requireTarget, mana = False, 2
	index = "DARKMOON_FAIRE~Shaman~Spell~2~~Deathmatch Pavilion"
	description = "Summon a 3/2 Duelist. If your hero attacked this turn, summon another"
	name_CN = "死斗场帐篷"
	def available(self):
		return self.Game.space(self.ID) > 0
		
	def effCanTrig(self):
		self.effectViable = self.Game.Counters.heroAttackTimesThisTurn[self.ID] > 0
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.summon(PavilionDuelist(self.Game, self.ID), -1)
		if self.Game.Counters.heroAttackTimesThisTurn[self.ID] > 0:
			self.summon(PavilionDuelist(self.Game, self.ID), -1)
		return None
		
class PavilionDuelist(Minion):
	Class, race, name = "Shaman", "", "Pavilion Duelist"
	mana, attack, health = 2, 3, 2
	index = "DARKMOON_FAIRE~Shaman~Minion~2~3~2~~Pavilion Duelist~Uncollectible"
	requireTarget, keyWord, description = False, "", ""
	name_CN = "大帐决斗者"
	
	
class GrandTotemEysor(Minion):
	Class, race, name = "Shaman", "Totem", "Grand Totem Eys'or"
	mana, attack, health = 3, 0, 4
	index = "DARKMOON_FAIRE~Shaman~Minion~3~0~4~Totem~Grand Totem Eys'or~Legendary"
	requireTarget, keyWord, description = False, "", "At the end of your turn, give +1/+1 to all other Totems in your hand, deck and battlefield"
	name_CN = "巨型图腾埃索尔"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_GrandTotemEysor(self)]
		
class Trig_GrandTotemEysor(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["TurnEnds"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and ID == self.entity.ID
		
	def text(self, CHN):
		return "在你的回合结束时，使你手牌，牌库以及战场中的所有其他图腾获得+1/+1" if CHN \
				else "At the end of your turn, give +1/+1 to all other Totems in your hand, deck and battlefield"
				
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		curGame, side = self.entity.Game, self.entity.ID
		for obj in curGame.minionsonBoard(side):
			if "Totem" in obj.race and obj != self.entity:
				obj.buffDebuff(1, 1)
		for card in curGame.Hand_Deck.hands[side] + curGame.Hand_Deck.decks[side]:
			if card.type == "Minion" and "Totem" in card.race:
				card.buffDebuff(1, 1)
				
				
class Magicfin(Minion):
	Class, race, name = "Shaman", "Murloc", "Magicfin"
	mana, attack, health = 3, 3, 4
	index = "DARKMOON_FAIRE~Shaman~Minion~3~3~4~Murloc~Magicfin"
	requireTarget, keyWord, description = False, "", "After a friendly Murloc dies, add a random Legendary minion to your hand"
	name_CN = "鱼人魔术师"
	poolIdentifier = "Legendary Minions"
	@classmethod
	def generatePool(cls, pools):
		return "Legendary Minions", pools.LegendaryMinions
		
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_Magicfin(self)]
		
class Trig_Magicfin(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["MinionDies"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and target != self.entity and target.ID == self.entity.ID and "Murloc" in target.race
		
	def text(self, CHN):
		return "在一个友方鱼人死亡后，随机将一张传说随从牌置入你的手牌" if CHN else "After a friendly Murloc dies, add a random Legendary minion to your hand"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.addCardtoHand(npchoice(self.rngPool("Legendary Minions")), self.entity.ID)
			
			
class PitMaster(Minion):
	Class, race, name = "Shaman", "", "Pit Master"
	mana, attack, health = 3, 1, 2
	index = "DARKMOON_FAIRE~Shaman~Minion~3~1~2~~Pit Master~Battlecry~ToCorrupt"
	requireTarget, keyWord, description = False, "", "Battlecry: Summon a 3/2 Duelist. Corrupt: Summon two"
	name_CN = "死斗场管理者"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsHand = [Trig_Corrupt(self, PitMaster_Corrupt)] #只有在手牌中才会升级
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.summon(PavilionDuelist(self.Game, self.ID), self.pos+1)
		return None
		
class PitMaster_Corrupt(Minion):
	Class, race, name = "Shaman", "", "Pit Master"
	mana, attack, health = 3, 1, 2
	index = "DARKMOON_FAIRE~Shaman~Minion~3~1~2~~Pit Master~Battlecry~Corrupted~Uncollectible"
	requireTarget, keyWord, description = False, "", "Corrupted. Battlecry: Summon two 3/2 Duelists"
	name_CN = "死斗场管理者"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		pos = (self.pos, "leftandRight") if self.onBoard else (-1, "totheRightEnd")
		self.summon([PavilionDuelist(self.Game, self.ID) for i in range(2)], pos)
		return None
		
		
class Stormstrike(Spell):
	Class, school, name = "Shaman", "Nature", "Stormstrike"
	requireTarget, mana = True, 3
	index = "DARKMOON_FAIRE~Shaman~Spell~3~Nature~Stormstrike"
	description = "Deal 3 damage to a minion. Give your hero +3 Attack this turn"
	name_CN = "风暴打击"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			damage = (3 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			self.dealsDamage(target, damage)
			self.Game.heroes[self.ID].gainAttack(3)
		return target
		
		
class WhackAGnollHammer(Weapon):
	Class, name, description = "Shaman", "Whack-A-Gnoll Hammer", "After your hero attacks, give a random friendly minion +1/+1"
	mana, attack, durability = 3, 3, 2
	index = "DARKMOON_FAIRE~Shaman~Weapon~3~3~2~Whack-A-Gnoll Hammer"
	name_CN = "敲狼锤"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_WhackAGnollHammer(self)]
		
class Trig_WhackAGnollHammer(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["HeroAttackedMinion", "HeroAttackedHero"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject == self.entity.Game.heroes[self.entity.ID] and self.entity.onBoard
		
	def text(self, CHN):
		return "在你的英雄攻击后，随机使一个友方随从获得+1/+1" if CHN \
				else "After your hero attacks, give a random friendly minion +1/+1"
				
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		minions = self.entity.Game.minionsonBoard(self.entity.ID)
		if minions: npchoice(minions).buffDebuff(1, 1)
		
		
class DunkTank(Spell):
	Class, school, name = "Shaman", "Nature", "Dunk Tank"
	requireTarget, mana = True, 4
	index = "DARKMOON_FAIRE~Shaman~Spell~4~Nature~Dunk Tank~ToCorrupt"
	description = "Deal 4 damage. Corrupt: Then deal 2 damage to all enemy minions"
	name_CN = "深水炸弹"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsHand = [Trig_Corrupt(self, DunkTank_Corrupt)] #只有在手牌中才会升级
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			damage = (4 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			self.dealsDamage(target, damage)
		return target
		
class DunkTank_Corrupt(Spell):
	Class, school, name = "Shaman", "Nature", "Dunk Tank"
	requireTarget, mana = True, 4
	index = "DARKMOON_FAIRE~Shaman~Spell~4~Nature~Dunk Tank~Corrupted~Uncollectible"
	description = "Corrupted. Deal 4 damage. Then deal 2 damage to all enemy minions"
	name_CN = "深水炸弹"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			damage_4 = (4 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			self.dealsDamage(target, damage_4)
			damage_2 = (2 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			minions = self.Game.minionsonBoard(3-self.ID)
			self.dealsAOE(minions, [damage_2] * len(minions))
		return target
		
		
class InaraStormcrash(Minion):
	Class, race, name = "Shaman", "", "Inara Stormcrash"
	mana, attack, health = 5, 4, 5
	index = "DARKMOON_FAIRE~Shaman~Minion~5~4~5~~Inara Stormcrash~Legendary"
	requireTarget, keyWord, description = False, "", "On your turn, your hero has +2 Attack and Windfury"
	name_CN = "伊纳拉·碎雷"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.auras["On your turn, your hero has +2 Attack and Windfury"] = HasAura_InaraStormcrash(self)
		
class HasAura_InaraStormcrash:
	def __init__(self, entity):
		self.entity = entity
		self.auraAffected = []
		self.signals = ["HeroReplaced", "TurnStarts", "TurnEnds"]
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and (signal[0] == "T" or subject.ID == self.entity.ID)
		
	def trig(self, signal, ID, subject, target, number, comment, choice=0):
		if self.canTrig(signal, ID, subject, target, number, comment):
			minion = self.entity
			if signal[0] == "T": #
				if "E" in signal: #At the end of either player's turn, clear the affected list
					for hero, receiver in self.auraAffected[:]:
						receiver.effectClear()
					self.auraAffected = []
				elif ID == minion.ID: #Only start the effect at the start of your turn
					self.applies(minion.Game.heroes[ID])
			elif ID == minion.ID == minion.Game.turn: #New hero is on board during your turn
				self.applies(subject)
				
	def applies(self, subject):
		Stat_Receiver(subject, self, 2).effectStart()
		#随从和英雄的特效光环可以共用
		Effect_Receiver(subject, self, "Windfury").effectStart()
		
	def auraAppears(self):
		game, ID = self.entity.Game, self.entity.ID
		if game.turn == ID: self.applies(game.heroes[ID])
		trigsBoard = game.trigsBoard[ID]
		for sig in self.signals:
			try: trigsBoard[sig].append(self)
			except: trigsBoard[sig] = [self]
			
	def auraDisappears(self):
		for hero, receiver in self.auraAffected[:]:
			receiver.effectClear()
		self.auraAffected = []
		trigsBoard = self.entity.Game.trigsBoard[self.entity.ID]
		for sig in ["HeroReplaced", "TurnStarts", "TurnEnds"]:
			try: trigsBoard[sig].remove(self)
			except: pass
			
	def selfCopy(self, recipient):
		return type(self)(recipient)
		
	#这个函数会在复制场上扳机列表的时候被调用。
	def createCopy(self, game):
		#一个光环的注册可能需要注册多个扳机
		if self not in game.copiedObjs: #这个光环没有被复制过
			heroCopy = self.entity.createCopy(game)
			Copy = self.selfCopy(heroCopy)
			game.copiedObjs[self] = Copy
			for hero, receiver in self.auraAffected:
				heroCopy = hero.createCopy(game)
				index = hero.auraReceivers.index(receiver)
				receiverCopy = heroCopy.auraReceivers[index]
				receiverCopy.source = Copy #补上这个receiver的source
				Copy.auraAffected.append((heroCopy, receiverCopy))
			return Copy
		else:
			return game.copiedObjs[self]
			
			
"""Warlock cards"""
class WickedWhispers(Spell):
	Class, school, name = "Warlock", "Shadow", "Wicked Whispers"
	requireTarget, mana = False, 1
	index = "DARKMOON_FAIRE~Warlock~Spell~1~Shadow~Wicked Whispers"
	description = "Discard your lowest Cost card. Give your minions +1/+1"
	name_CN = "邪恶低语"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		cards, lowestCost = [], npinf
		for i, card in enumerate(self.Game.Hand_Deck.hands[self.ID]):
			if card.mana < lowestCost: cards, lowestCost = [i], card.mana
			elif card.mana == lowestCost: cards.append(i)
		if cards: self.Game.Hand_Deck.discard(self.ID, npchoice(cards))
		for minion in self.Game.minionsonBoard(self.ID):
			minion.buffDebuff(1, 1)
		return None
		
		
class MidwayManiac(Minion):
	Class, race, name = "Warlock", "Demon", "Midway Maniac"
	mana, attack, health = 2, 1, 5
	index = "DARKMOON_FAIRE~Warlock~Minion~2~1~5~Demon~Midway Maniac~Taunt"
	requireTarget, keyWord, description = False, "Taunt", "Taunt"
	name_CN = "癫狂的游客"
	
	
class FreeAdmission(Spell):
	Class, school, name = "Warlock", "", "Free Admission"
	requireTarget, mana = False, 3
	index = "DARKMOON_FAIRE~Warlock~Spell~3~~Free Admission"
	description = "Draw 2 minions. If they're both Demons, reduce their Cost by (2)"
	name_CN = "免票入场"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		cards = [None, None]
		ownDeck = self.Game.Hand_Deck.decks[self.ID]
		for num in range(2):
			minions = [i for i, card in enumerate(ownDeck) if card.type == "Minion"]
			if minions: cards[num] = self.Game.Hand_Deck.drawCard(self.ID, npchoice(minions))[0]
		if cards[0] and "Demon" in cards[0].race and cards[1] and "Demon" in cards[1].race:
			ManaMod(cards[0], changeby=-2, changeto=-1).applies()
			ManaMod(cards[1], changeby=-2, changeto=-1).applies()
		return None
		
		
class ManariMosher(Minion):
	Class, race, name = "Warlock", "Demon", "Man'ari Mosher"
	mana, attack, health = 3, 3, 4
	index = "DARKMOON_FAIRE~Warlock~Minion~3~3~4~Demon~Man'ari Mosher~Battlecry"
	requireTarget, keyWord, description = True, "", "Battlecry: Give a friendly Demon +3 Attack and Lifesteal this turn"
	name_CN = "摇滚堕落者"
	def targetExists(self, choice=0):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and "Demon" in target.race and target != self and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target and (target.onBoard or target.inHand):
			target.buffDebuff(3, 0, "EndofTurn")
			target.getsStatus("Lifesteal")
			trig = ManariMosher_Effect(target)
			target.trigsBoard.append(trig)
			target.trigsHand.append(trig) #The target might be in hand. Need to reset correctly even if it's in hand
			trig.connect()
		return target
		
class ManariMosher_Effect:
	def __init__(self, entity):
		self.entity, self.signals, self.inherent = entity, ["TurnStarts", "TurnEnds"], False
		
	def connect(self):
		ID = self.entity.ID
		trigs = self.entity.Game.trigsBoard[ID] if self.entity.onBoard else self.entity.Game.trigsHand[ID]
		for sig in self.signals:
			try: trigs[sig].append(self)
			except: trigs[sig] = [self]
			
	def disconnect(self):
		game, ID = self.entity.Game, self.entity.ID
		for sig in self.signals:
			try: game.trigsHand[ID][sig].remove(self)
			except: pass
			try: game.trigsBoard[ID][sig].remove(self)
			except: pass
			
	def trig(self, signal, ID, subject, target, number, comment, choice=0):
		if self.canTrig(signal, ID, subject, target, number, comment):
			if self.entity.Game.GUI: self.entity.Game.GUI.trigBlink(self.entity)
			self.effect(signal, ID, subject, target, number, comment)
			
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return True #This triggers at either player's turn end and start
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		minion = self.entity
		minion.losesStatus("Lifesteal")
		for sig in self.signals:
			try: minion.Game.trigsHand[minion.ID][sig].remove(self)
			except: pass
			try: minion.Game.trigsBoard[minion.ID][sig].remove(self)
			except: pass
		try: minion.trigsBoard.remove(self)
		except: pass
		try: minion.trigsHand.remove(self)
		except: pass
		
	def selfCopy(self, recipient):
		return type(self)(recipient)
		
	def createCopy(self, game):
		if self not in game.copiedObjs: #这个扳机没有被复制过
			entityCopy = self.entity.createCopy(game)
			trigCopy = type(self)(entityCopy)
			game.copiedObjs[self] = trigCopy
			return trigCopy
		else: #一个扳机被复制过了，则其携带者也被复制过了
			return game.copiedObjs[self]
			
			
class CascadingDisaster(Spell):
	Class, school, name = "Warlock", "", "Cascading Disaster"
	requireTarget, mana = False, 4
	index = "DARKMOON_FAIRE~Warlock~Spell~4~~Cascading Disaster~ToCorrupt"
	description = "Destroy a random enemy minion. Corrupt: Destroy 2. Corrupt Again: Destroy 3"
	name_CN = "连环灾难"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsHand = [Trig_Corrupt(self, CascadingDisaster_Corrupt)] #只有在手牌中才会升级
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		minions = self.Game.minionsAlive(3 - self.ID)
		if minions: self.Game.killMinion(self, npchoice(minions))
		return None
		
class CascadingDisaster_Corrupt(Spell):
	Class, school, name = "Warlock", "", "Cascading Disaster"
	requireTarget, mana = False, 4
	index = "DARKMOON_FAIRE~Warlock~Spell~4~~Cascading Disaster~ToCorrupt~Corrupted~Uncollectible"
	description = "Corrupted. Destroy 2 random enemy minions. Corrupt: Destroy 3"
	name_CN = "连环灾难"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsHand = [Trig_Corrupt(self, CascadingDisaster_Corrupt2)] #只有在手牌中才会升级
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		minions = self.Game.minionsAlive(3 - self.ID)
		if minions:
			for minion in npchoice(minions, min(2, len(minions)), replace=False):
				self.Game.killMinion(self, minion)
		return None
		
class CascadingDisaster_Corrupt2(Spell):
	Class, school, name = "Warlock", "", "Cascading Disaster"
	requireTarget, mana = False, 4
	index = "DARKMOON_FAIRE~Warlock~Spell~4~~Cascading Disaster~Corrupted~Uncollectible"
	description = "Corrupted. Destroy 3 random enemy minions"
	name_CN = "连环灾难"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		minions = self.Game.minionsAlive(3-self.ID)
		if minions:
			for minion in npchoice(minions, min(3, len(minions)), replace=False):
				self.Game.killMinion(self, minion)
		return None
		
		
class RevenantRascal(Minion):
	Class, race, name = "Warlock", "", "Revenant Rascal"
	mana, attack, health = 3, 3, 3
	index = "DARKMOON_FAIRE~Warlock~Minion~3~3~3~~Revenant Rascal~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Destroy a Mana Crystal for both players"
	name_CN = "怨灵捣蛋鬼"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.Game.Manas.destroyManaCrystal(1, self.ID)
		self.Game.Manas.destroyManaCrystal(1, 3-self.ID)
		return None
		
		
class FireBreather(Minion):
	Class, race, name = "Warlock", "Demon", "Fire Breather"
	mana, attack, health = 4, 4, 3
	index = "DARKMOON_FAIRE~Warlock~Minion~4~4~3~Demon~Fire Breather~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Deal 2 damage to all minions except Demons"
	name_CN = "吐火艺人"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		minions = [minion for minion in self.Game.minionsonBoard(1) + self.Game.minionsonBoard(2) if "Demon" not in minion.race]
		self.dealsAOE(minions, [2] * len(minions))
		return None
		
		
class DeckofChaos(Spell):
	Class, school, name = "Warlock", "Shadow", "Deck of Chaos"
	requireTarget, mana = False, 5
	index = "DARKMOON_FAIRE~Warlock~Spell~5~Shadow~Deck of Chaos~Legendary"
	description = "Swap the Cost and Attack of all minions in your deck"
	name_CN = "混乱套牌"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		for card in self.Game.Hand_Deck.decks[self.ID]:
			if card.type == "Minion":
				att = card.attack
				card.attack = card.mana
				for manaMod in reversed(card.manaMods): manaMod.getsRemoved()
				ManaMod(card, changeby=0, changeto=max(0, att)).applies()
		return None
		
		
class RingMatron(Minion):
	Class, race, name = "Warlock", "Demon", "Ring Matron"
	mana, attack, health = 6, 6, 4
	index = "DARKMOON_FAIRE~Warlock~Minion~6~6~4~Demon~Ring Matron~Taunt~Deathrattle"
	requireTarget, keyWord, description = False, "Taunt", "Taunt. Deathrattle: Summon two 3/2 Imps"
	name_CN = "火圈鬼母"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.deathrattles = [SummonTwo32Imps(self)]
		
class SummonTwo32Imps(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		minion = self.entity
		pos = (minion.pos, "leftandRight") if minion in minion.Game.minions[minion.ID] else (-1, "totheRightEnd")
		minion.summon([FieryImp(minion.Game, minion.ID) for i in range(2)], pos)
		
	def text(self, CHN):
		return "亡语：召唤两个3/2的小鬼" if CHN else "Deathrattle: Summon two 3/2 Imps"
		
class FieryImp(Minion):
	Class, race, name = "Warlock", "Demon", "Fiery Imp"
	mana, attack, health = 2, 3, 2
	index = "DARKMOON_FAIRE~Warlock~Minion~2~3~2~Demon~Fiery Imp~Uncollectible"
	requireTarget, keyWord, description = False, "", ""
	name_CN = "火焰小鬼"
	
	
class Tickatus(Minion):
	Class, race, name = "Warlock", "Demon", "Tickatus"
	mana, attack, health = 6, 8, 8
	index = "DARKMOON_FAIRE~Warlock~Minion~6~8~8~Demon~Tickatus~Battlecry~ToCorrupt~Legendary"
	requireTarget, keyWord, description = False, "", "Battlecry: Remove the top 5 cards from your deck. Corrupt: Your opponent's instead"
	name_CN = "提克特斯"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsHand = [Trig_Corrupt(self, Tickatus_Corrupt)] #只有在手牌中才会升级
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		self.Game.Hand_Deck.removeDeckTopCard(self.ID, num=5)
		return None
		
class Tickatus_Corrupt(Minion):
	Class, race, name = "Warlock", "Demon", "Tickatus"
	mana, attack, health = 6, 8, 8
	index = "DARKMOON_FAIRE~Warlock~Minion~6~8~8~Demon~Tickatus~Battlecry~Corrupted~Legendary~Uncollectible"
	requireTarget, keyWord, description = False, "", "Corrupted. Battlecry: Remove the top 5 cards from your opponent's deck"
	name_CN = "提克特斯"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		self.Game.Hand_Deck.removeDeckTopCard(3-self.ID, num=5)
		return None
		
"""Warrior cards"""
class StageDive(Spell):
	Class, school, name = "Warrior", "", "Stage Dive"
	requireTarget, mana = False, 1
	index = "DARKMOON_FAIRE~Warrior~Spell~1~~Stage Dive~ToCorrupt"
	description = "Draw a Rush minion. Corrupt: Give it +2/+1"
	name_CN = "舞台跳水"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsHand = [Trig_Corrupt(self, StageDive_Corrupt)] #只有在手牌中才会升级
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		minions = [i for i, card in enumerate(self.Game.Hand_Deck.decks[self.ID]) if card.type == "Minion" and card.keyWords["Rush"] > 0]
		if minions: self.Game.Hand_Deck.drawCard(self.ID, npchoice(minions))[0]
		return None
		
class StageDive_Corrupt(Spell):
	Class, school, name = "Warrior", "", "Stage Dive"
	requireTarget, mana = False, 1
	index = "DARKMOON_FAIRE~Warrior~Spell~1~~Stage Dive~Corrupted~Uncollectible"
	description = "Corrupted. Draw a Rush minion and give it +2/+1"
	name_CN = "舞台跳水"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		minions = [i for i, card in enumerate(self.Game.Hand_Deck.decks[self.ID]) if card.type == "Minion" and card.keyWords["Rush"] > 0]
		if minions:
			minion = self.Game.Hand_Deck.drawCard(self.ID, npchoice(minions))[0]
			if minion: minion.buffDebuff(2, 1)
		return None
		
		
class BumperCar(Minion):
	Class, race, name = "Warrior", "Mech", "Bumper Car"
	mana, attack, health = 2, 1, 3
	index = "DARKMOON_FAIRE~Warrior~Minion~2~1~3~Mech~Bumper Car~Rush~Deathrattle"
	requireTarget, keyWord, description = False, "Rush", "Rush. Deathrattle: Add two 1/1 Riders with Rush to your hand"
	name_CN = "碰碰车"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.deathrattles = [AddTwo11RiderstoYourHand(self)]
		
class AddTwo11RiderstoYourHand(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.addCardtoHand([DarkmoonRider, DarkmoonRider], self.entity.ID)
		
	def text(self, CHN):
		return "将两张1/1并具有突袭的乘客置入你的手牌" if CHN else "Deathrattle: Add two 1/1 Riders with Rush to your hand"
		
		
class ETCGodofMetal(Minion):
	Class, race, name = "Warrior", "", "E.T.C., God of Metal"
	mana, attack, health = 2, 1, 4
	index = "DARKMOON_FAIRE~Warrior~Minion~2~1~4~~E.T.C., God of Metal~Legendary"
	requireTarget, keyWord, description = False, "", "After a friendly Rush minion attack, deal 2 damage to the enemy hero"
	name_CN = "精英牛头人酋长，金属之神"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_ETCGodofMetal(self)]
		
class Trig_ETCGodofMetal(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["MinionAttackedMinion", "MinionAttackedHero"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject.ID == self.entity.ID and subject.keyWords["Rush"] > 0 and self.entity.onBoard
		
	def text(self, CHN):
		return "在一个友方突袭随从攻击后，对敌方英雄造成2点伤害" if CHN else "After a friendly Rush minion attack, deal 2 damage to the enemy hero"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.dealsDamage(self.entity.Game.heroes[3-self.entity.ID], 2)
		
		
class Minefield(Spell):
	Class, school, name = "Warrior", "", "Minefield"
	requireTarget, mana = False, 2
	index = "DARKMOON_FAIRE~Warrior~Spell~2~~Minefield"
	description = "Deal 5 damage randomly split among all minions"
	name_CN = "雷区挑战"
	def text(self, CHN):
		damage = (5 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		return "造成%d点伤害，随机分配到所有随从身上"%damage if CHN else "Deal %d damage randomly split among all minions"%damage
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		damage = (5 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		for num in range(damage):
			objs = self.Game.minionsAlive(1) + self.Game.minionsAlive(2)
			if objs: self.dealsDamage(npchoice(objs), 1)
			else: break
		return None
		
		
class RingmastersBaton(Weapon):
	Class, name, description = "Warrior", "Ringmaster's Baton", "After your hero attacks, give a Mech, Dragon, and Pirate in your hand +1/+1"
	mana, attack, durability = 2, 1, 3
	index = "DARKMOON_FAIRE~Warrior~Weapon~2~1~3~Ringmaster's Baton"
	name_CN = "马戏领班的节杖"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_RingmastersBaton(self)]
		
class Trig_RingmastersBaton(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["HeroAttackedMinion", "HeroAttackedHero"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject == self.entity.Game.heroes[self.entity.ID] and self.entity.onBoard
		
	def text(self, CHN):
		return "在你的英雄攻击后，使你手牌中的一张机械牌，龙牌和海盗牌获得+1/+1" if CHN \
				else "After your hero attacks, give a Mech, Dragon, and Pirate in your hand +1/+1"
				
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		ownHand = self.entity.Game.Hand_Deck.hands[self.entity.ID]
		for race in ("Mech", "Dragon", "Pirate"):
			minions = [card for card in ownHand if card.type == "Minion" and race in card.race]
			if minions: npchoice(minions).buffDebuff(1, 1)
			
				
class StageHand(Minion):
	Class, race, name = "Warrior", "Mech", "Stage Hand"
	mana, attack, health = 2, 3, 2
	index = "DARKMOON_FAIRE~Warrior~Minion~2~3~2~Mech~Stage Hand~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Give a random minion in your hand +1/+1"
	name_CN = "置景工"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		minions = [card for card in self.Game.Hand_Deck.hands[self.ID] if card.type == "Minion"]
		if minions: npchoice(minions).buffDebuff(1, 1)
		return None
		
		
class FeatofStrength(Spell):
	Class, school, name = "Warrior", "", "Feat of Strength"
	requireTarget, mana = False, 3
	index = "DARKMOON_FAIRE~Warrior~Spell~3~~Feat of Strength"
	description = "Give a random Taunt minion in your hand +5/+5"
	name_CN = "实力担当"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		minions = [card for card in self.Game.Hand_Deck.hands[self.ID] if card.type == "Minion" and card.keyWords["Taunt"] > 0]
		if minions: npchoice(minions).buffDebuff(5, 5)
		return None
		
		
class SwordEater(Minion):
	Class, race, name = "Warrior", "Pirate", "Sword Eater"
	mana, attack, health = 4, 2, 5
	index = "DARKMOON_FAIRE~Warrior~Minion~4~2~5~Pirate~Sword Eater~Taunt~Battlecry"
	requireTarget, keyWord, description = False, "Taunt", "Taunt. Battlecry: Equip a 3/2 Sword"
	name_CN = "吞剑艺人"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.equipWeapon(Jawbreaker(self.Game, self.ID))
		return None
		
class Jawbreaker(Weapon):
	Class, name, description = "Warrior", "Jawbreaker", ""
	mana, attack, durability = 3, 3, 2
	index = "DARKMOON_FAIRE~Warrior~Weapon~3~3~2~Jawbreaker~Uncollectible"
	name_CN = "断颚之刃"
	
	
class RingmasterWhatley(Minion):
	Class, race, name = "Warrior", "", "Ringmaster Whatley"
	mana, attack, health = 5, 3, 5
	index = "DARKMOON_FAIRE~Warrior~Minion~5~3~5~~Ringmaster Whatley~Battlecry~Legendary"
	requireTarget, keyWord, description = False, "", "Battlecry: Draw a Mech, Dragon, and Pirate"
	name_CN = "马戏领班威特利"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		for race in ("Mech", "Dragon", "Pirate"):
			minions = [i for i, card in enumerate(self.Game.Hand_Deck.decks[self.ID]) if card.type == "Minion" and race in card.race]
			if minions: self.Game.Hand_Deck.drawCard(self.ID, npchoice(minions))
		return None
		
#All type can only count as one of the 8 races.
class TentTrasher(Minion):
	Class, race, name = "Warrior", "Dragon", "Tent Trasher"
	mana, attack, health = 5, 5, 5
	index = "DARKMOON_FAIRE~Warrior~Minion~5~5~5~Dragon~Tent Trasher~Rush"
	requireTarget, keyWord, description = False, "Rush", "Rush. Costs (1) less for each friendly minion with a unique minion type"
	name_CN = "帐篷摧毁者"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsHand = [Trig_TentTrasher(self)]
		
	def selfManaChange(self):
		if self.inHand:
			races = cnt([minion.race for minion in self.Game.minionsonBoard(self.ID)])
			del races[""] #There are at most 7 minions on board. The "All" type can always reduce the cost by 1
			#del races["Elemental,Mech,Demon,Murloc,Dragon,Beast,Pirate,Totem"]
			num = sum(value > 0 for value in races.values())
			print("Tent trasher reduces bty", num)
			self.mana -= num
			self.mana = max(0, self.mana)
			
class Trig_TentTrasher(TrigHand):
	def __init__(self, entity):
		super().__init__(entity, ["MinionAppears", "MinionDisappears"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		if 'A' in signal: return self.entity.inHand and ID == self.entity.ID and subject.race
		else: return self.entity.inHand and ID == self.entity.ID and target.race
		
	def text(self, CHN):
		return "每当你场上的随从出现或离场，重新计算费用" if CHN else "Whenever your minions appear or disappear, recalculate the cost"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("Tent trasher calcs")
		self.entity.Game.Manas.calcMana_Single(self.entity)
		
		
		
"""Darkmoon Races mini expansion"""

"""Neutral cards"""
class ArmorVendor(Minion):
	Class, race, name = "Neutral", "", "Armor Vendor"
	mana, attack, health = 1, 1, 3
	index = "DARKMOON_FAIRE~Neutral~Minion~1~1~3~~Armor Vendor~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Give 4 Armor to each hero"
	name_CN = "护甲商贩"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.Game.heroes[1].gainsArmor(4)
		self.Game.heroes[2].gainsArmor(4)
		return None
		
		
class Crabrider(Minion):
	Class, race, name = "Neutral", "Murloc", "Crabrider"
	mana, attack, health = 2, 1, 4
	index = "DARKMOON_FAIRE~Neutral~Minion~2~1~4~Murloc~Crabrider~Rush~Windfury"
	requireTarget, keyWord, description = False, "Rush,Windfury", "Rush, Windfury"
	name_CN = "螃蟹骑士"
	
	
class Deathwarden(Minion):
	Class, race, name = "Neutral", "", "Deathwarden"
	mana, attack, health = 3, 2, 5
	index = "DARKMOON_FAIRE~Neutral~Minion~3~2~5~~Deathwarden"
	requireTarget, keyWord, description = False, "", "Deathrattles can't trigger"
	name_CN = "死亡守望者"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.auras["Deathrattles can't trigger"] = GameRuleAura_Deathwarden(self)
		
class GameRuleAura_Deathwarden(GameRuleAura):
	def auraAppears(self):
		minion = self.entity
		minion.Game.status[minion.ID]["Deathrattles X"] += 1
		minion.Game.status[3-minion.ID]["Deathrattles X"] += 1
		
	def auraDisappears(self):
		minion = self.entity
		minion.Game.status[minion.ID]["Deathrattles X"] -= 1
		minion.Game.status[3-minion.ID]["Deathrattles X"] -= 1
		
		
class Moonfang(Minion):
	Class, race, name = "Neutral", "Beast", "Moonfang"
	mana, attack, health = 5, 6, 3
	index = "DARKMOON_FAIRE~Neutral~Minion~5~6~3~Beast~Moonfang~Legendary"
	requireTarget, keyWord, description = False, "", "Can only take 1 damage at a time"
	name_CN = "明月之牙"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_MoonFang(self)]
		
class Trig_MoonFang(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["FinalDmgonMinion?"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		#Can only prevent damage if there is still durability left
		return target == self.entity and self.entity.onBoard
		
	def text(self, CHN):
		return "每次只能受到1点伤害" if CHN else "Can only take 1 damage at a time"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		number[0] = min(number[0], 1)
		
		
class RunawayBlackwing(Minion):
	Class, race, name = "Neutral", "Dragon", "Runaway Blackwing"
	mana, attack, health = 9, 9, 9
	index = "DARKMOON_FAIRE~Neutral~Minion~9~9~9~Dragon~Runaway Blackwing"
	requireTarget, keyWord, description = False, "", "At the end of your turn, deal 9 damage to a random enemy minion"
	name_CN = "窜逃的黑翼龙"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_RunawayBlackwing(self)]
		
class Trig_RunawayBlackwing(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["TurnEnds"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and ID == self.entity.ID
		
	def text(self, CHN):
		return "在你的回合结束时，随机对一个敌方随从造成9点伤害" if CHN else "At the end of your turn, deal 9 damage to a random enemy minion"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		targets = self.entity.Game.minionsAlive(3-self.entity.ID)
		if targets: self.entity.dealsDamage(npchoice(targets), 9)
		
		
"""Demon Hunter Cards"""
class IllidariStudies(Spell):
	Class, school, name = "Demon Hunter", "", "Illidari Studies"
	requireTarget, mana = False, 1
	index = "DARKMOON_FAIRE~Demon Hunter~Spell~1~~Illidari Studies"
	description = "Discover an Outcast card. Your next one costs (1) less"
	name_CN = "伊利达雷研习"
	poolIdentifier = "Outcast Cards"
	@classmethod
	def generatePool(cls, pools):
		return "Outcast Cards", [card for card in pools.ClassCards["Demon Hunter"] if "~Outcast" in card.index]
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.discoverandGenerate(IllidariStudies, comment, lambda : self.rngPool("Outcast Cards"))
		tempAura = GameManaAura_NextOutcast1Less(self.Game, self.ID)
		self.Game.Manas.CardAuras.append(tempAura)
		tempAura.auraAppears()
		return None
		
class GameManaAura_NextOutcast1Less(TempManaEffect):
	def __init__(self, Game, ID, changeby=0, changeto=-1):
		super().__init__(Game, ID, -1, -1)
		self.temporary = False
		
	def applicable(self, target):
		return target.ID == self.ID and "~Outcast" in target.index
		
	def text(self, CHN):
		return "你的下一张流放牌的法力值消耗减少(1)点" if CHN else "Your next Outcast card costs (1) less"
		
		
class FelfireDeadeye(Minion):
	Class, race, name = "Demon Hunter,Hunter", "", "Felfire Deadeye"
	mana, attack, health = 2, 2, 3
	index = "DARKMOON_FAIRE~Demon Hunter,Hunter~Minion~2~2~3~~Felfire Deadeye"
	requireTarget, keyWord, description = False, "", "Your Hero Power costs (1) less"
	name_CN = "邪火神射手"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.auras["Your Hero Power costs (1) less"] = ManaAura_Power(self, -1, -1)
		
	def manaAuraApplicable(self, subject): #ID用于判定是否是我方手中的随从
		return subject.ID == self.ID
		
		
class Felsaber(Minion):
	Class, race, name = "Demon Hunter", "Demon", "Felsaber"
	mana, attack, health = 4, 5, 6
	index = "DARKMOON_FAIRE~Demon Hunter~Minion~4~5~6~Demon~Felsaber"
	requireTarget, keyWord, description = False, "", "Can only attack if your hero attacked this turn"
	name_CN = "邪刃豹"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.marks["Can't Attack"] = 1
		
	def canAttack(self):
		return self.actionable() and self.attack > 0 and self.status["Frozen"] < 1 \
				and self.attChances_base + self.attChances_extra <= self.attTimes \
				and (self.silenced or self.Game.Counters.heroAttackTimesThisTurn[self.ID] > 0)
				
				
"""Druid Cards"""
class Guidance(Spell):
	Class, school, name = "Druid,Shaman", "", "Guidance"
	requireTarget, mana = False, 1
	index = "DARKMOON_FAIRE~Druid,Shaman~Spell~1~~Guidance"
	description = "Look at two spells. Add one to your hand or Overload: (1) to get both"
	name_CN = "灵魂指引"
	poolIdentifier = "Druid Spells"
	@classmethod
	def generatePool(cls, pools):
		return [Class + " Spells" for Class in pools.Classes], \
			   [[card for card in pools.ClassCards[Class] if card.type == "Spell"] for Class in pools.Classes]
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		game = self.Game
		if game.mode == 0:
			if game.picks:
				info_RNGSync, info_GUISync, isRandom, option = game.picks.pop(0)
				npchoice(range(info_RNGSync), 2, replace=False)
				#option is (card1, card2, choice=0/1/2)
				card1, card2, i = option
				cards_Real = [card1(game, self.ID), card2(game, self.ID)]
				if game.GUI: game.GUI.discoverDecideAni(isRandom=isRandom, numOption=info_GUISync[0], indexOption=info_GUISync[1],
														options=cards_Real + [SpiritPath(ID=self.ID)])
				Guidance.discoverDecided(self, cards_Real+[i],
									 	case="Guided", info_RNGSync=info_RNGSync, info_GUISync=info_GUISync)
			else:
				pool = self.rngPool(classforDiscover(self) + " Spells")
				options = [option(game, self.ID) for option in npchoice(pool, 2, replace=False)] + [SpiritPath(ID=self.ID)]
				if self.ID != game.turn or "byOthers" in comment:
					i = datetime.now().microsecond % 3
					if game.GUI: game.UI.discoverDecideAni(isRandom=True, numOption=3, indexOption=i, options=options)
					Guidance.discoverDecided(self, options[0:2]+[i], case="Random", info_RNGSync=len(pool), info_GUISync=(3, i))
				else:
					game.options = options
					game.Discover.startDiscover(self, effectType=Guidance, info_RNGSync=len(pool), info_GUISync=[3])
		return None
		
	def discoverDecided(self, option, case, info_RNGSync=None, info_GUISync=None):
		if case == "Discovered": #option is one of the cards or SpiritPath(self.Game, self.ID)
			card1, card2 = self.Game.options[0:2]
			i = self.Game.options.index(option)
			self.Game.picks.append((info_RNGSync, info_GUISync, False, (type(card1), type(card2), i)))
		else: #option is (card1, card2, i)
			card1, card2, i = option
			if case == "Random": self.Game.picks.append((info_RNGSync, info_GUISync, True, (type(card1), type(card2), i)) )
			
		if i == 2:
			self.addCardtoHand((card1, card2), self.ID, byDiscover=True)
			self.Game.Manas.overloadMana(1, self.ID)
		else:
			self.addCardtoHand(card2 if i else card1, self.ID, byDiscover=True)
			
class SpiritPath(Option):
	name, description = "Spirit Path", "Add both spells to your hand. Overload: (1)"
	index = ""
	mana, attack, health = 0, -1, -1
	
	
class DreamingDrake(Minion):
	Class, race, name = "Druid", "Dragon", "Dreaming Drake"
	mana, attack, health = 3, 3, 4
	index = "DARKMOON_FAIRE~Druid~Minion~3~3~4~Dragon~Dreaming Drake~Taunt~ToCorrupt"
	requireTarget, keyWord, description = False, "Taunt", "Taunt. Corrupt: Gain +2/+2"
	name_CN = "迷梦幼龙"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsHand = [Trig_Corrupt(self, DreamingDrake_Corrupt)] #只有在手牌中才会升级
		
class DreamingDrake_Corrupt(Minion):
	Class, race, name = "Druid", "Dragon", "Dreaming Drake"
	mana, attack, health = 3, 5, 6
	index = "DARKMOON_FAIRE~Druid~Minion~3~5~6~Dragon~Dreaming Drake~Taunt~Corrupted~Uncollectible"
	requireTarget, keyWord, description = False, "Taunt", "Corrupted. Taunt"
	name_CN = "迷梦幼龙"
	
	
class ArborUp(Spell):
	Class, school, name = "Druid", "Nature", "Arbor Up"
	requireTarget, mana = False, 5
	index = "DARKMOON_FAIRE~Druid~Spell~5~Nature~Arbor Up"
	description = "Summon two 2/2 Treants. Give your minions +2/+1"
	name_CN = "树木生长"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.summon([Treant_Darkmoon(self.Game, self.ID) for i in range(2)], (-1, "totheRightEnd"))
		for minion in self.Game.minionsonBoard(self.ID):
			minion.buffDebuff(2, 1)
		return None
		
		
"""Hunter Cards"""
class ResizingPouch(Spell):
	Class, school, name = "Hunter,Druid", "", "Resizing Pouch"
	requireTarget, mana = False, 1
	index = "DARKMOON_FAIRE~Hunter,Druid~Spell~1~~Resizing Pouch"
	description = "Discover a card with Cost equal to your remaining Mana Crystals"
	name_CN = "随心口袋"
	poolIdentifier = "Cards as Hunter"
	@classmethod
	def generatePool(cls, pools):
		return ["Cards as "+Class for Class in pools.Classes], [pools.ClassCards[Class]+pools.NeutralCards for Class in pools.Classes]
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.discoverandGenerate(ResizingPouch, comment, lambda : (card for card in self.rngPool("Cards as %s" % classforDiscover(self))
														if card.mana == self.Game.manas[self.ID]))
		return None
		
		
class BolaShot(Spell):
	Class, school, name = "Hunter", "", "Bola Shot"
	requireTarget, mana = True, 2
	index = "DARKMOON_FAIRE~Hunter~Spell~2~~Bola Shot"
	description = "Deal 1 damage to a minion and 2 damage to its neighbors"
	name_CN = "套索射击"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
		
	def text(self, CHN):
		damage1 = (1 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		damage2 = (2 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		return "对一个随从造成%d点伤害，并对其相邻的随从造成%d点伤害"%(damage1, damage2) \
				if CHN else "Deal %d damage to a minion and %d damage to its neighbors"%(damage1, damage2)
				
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			damage_target = (1 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			damage_adjacent = (2 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			neighbors = self.Game.neighbors2(target)[0]
			if target.onBoard and neighbors:
				targets = [target] + neighbors
				damages = [damage_target] + [damage_adjacent for minion in targets]
				self.dealsAOE(targets, damages)
			else:
				self.dealsDamage(target, damage_target)
		return target
		
		
class Saddlemaster(Minion):
	Class, race, name = "Hunter", "", "Saddlemaster"
	mana, attack, health = 3, 3, 4
	index = "DARKMOON_FAIRE~Hunter~Minion~3~3~4~~Saddlemaster"
	requireTarget, keyWord, description = False, "", "After you play a Beast, add a random Beast to your hand"
	name_CN = "鞍座大师"
	poolIdentifier = "Beasts"
	@classmethod
	def generatePool(cls, pools):
		return "Beasts", pools.MinionswithRace["Beast"]
		
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_Saddlemaster(self)]
		
class Trig_Saddlemaster(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["MinionBeenPlayed"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject.ID == self.entity.ID and "Beast" in subject.race
		
	def text(self, CHN):
		return "在你使用一张野兽牌后，随机将一张野兽牌置入你的手牌" if CHN else "After you play a Beast, add a random Beast to your hand"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.addCardtoHand(npchoice(self.rngPool("Beasts")), self.entity.ID)
			
"""Mage Cards"""
class GlacierRacer(Minion):
	Class, race, name = "Mage", "", "Glacier Racer"
	mana, attack, health = 1, 1, 3
	index = "DARKMOON_FAIRE~Mage~Minion~1~1~3~~Glacier Racer"
	requireTarget, keyWord, description = False, "", "Spellburst: Deal 3 damage to all Frozen enemies"
	name_CN = "冰川竞速者"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_GlacierRacer(self)]
		
class Trig_GlacierRacer(Spellburst):
	def text(self, CHN):
		return "法术迸发：对所有已被冻结的矮人造成3点伤害" if CHN else "Spellburst: Deal 3 damage to all Frozen enemies"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		game, ID = self.entity.Game, self.entity.ID
		targets = [obj for obj in game.minionsonBoard(ID) if obj.status["Frozen"]]
		if game.heroes[3-ID].status["Frozen"] > 0: targets.append(game.heroes[3-ID])
		if targets: self.entity.dealsAOE(targets, [3] * len(targets))
		
		
class ConjureManaBiscuit(Spell):
	Class, school, name = "Mage", "Arcane", "Conjure Mana Biscuit"
	requireTarget, mana = False, 2
	index = "DARKMOON_FAIRE~Mage~Spell~2~Arcane~Conjure Mana Biscuit"
	description = "Add a Biscuit to your hand that refreshes 2 Mana Crystals"
	name_CN = "制造法力饼干"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.addCardtoHand(ManaBiscuit, self.ID)
		return None
		
class ManaBiscuit(Spell):
	Class, school, name = "Mage", "", "Mana Biscuit"
	requireTarget, mana = False, 0
	index = "DARKMOON_FAIRE~Mage~Spell~0~~Mana Biscuit~Uncollectible"
	description = "Refresh 2 Mana Crystals"
	name_CN = "法力饼干"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.Game.Manas.restoreManaCrystal(2, self.ID, restoreAll=False)
		return None
		
		
class KeywardenIvory(Minion):
	Class, race, name = "Mage,Rogue", "", "Keywarden Ivory"
	mana, attack, health = 5, 4, 5
	index = "DARKMOON_FAIRE~Mage,Rogue~Minion~5~4~5~~Keywarden Ivory~Battlecry~Legendary"
	requireTarget, keyWord, description = False, "", "Battlecry: Discover a dual-class spell from any class. Spellburst: Get another copy"
	name_CN = "钥匙守护者艾芙瑞"
	poolIdentifier = "Dual Class Spells"
	@classmethod
	def generatePool(cls, pools):
		spells = []
		for cards in pools.ClassCards.values():
			spells += [card for card in cards if "," in card.Class and card.type == "Spell"]
		return "Dual Class Spells", spells
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.discoverandGenerate(KeywardenIvory, comment, lambda : self.rngPool("Dual Class Spells"))
		return None
		
	def discoverDecided(self, option, case, info_RNGSync=None, info_GUISync=None):
		self.handleDiscoverGeneratedCard(option, case, info_RNGSync, info_GUISync)
		if (self.onBoard or self.inHand) and option.inHand:
			self.getsTrig(Trig_KeywardenIvory(self, option), trigType="TrigBoard", connect=self.onBoard)
			
class Trig_KeywardenIvory(Spellburst):
	def __init__(self, entity, spell):
		super().__init__(entity)
		self.spell = spell
		
	def text(self, CHN):
		return "法术迸发：获得一个发现的双职业法术的复制" if CHN else "Spellburst: Get a copy of the Discovered dual-class spell"
	
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.addCardtoHand(self.spell, self.entity.ID)


"""Paladin Cards"""
class ImprisonedCelestial(Minion_Dormantfor2turns):
	Class, race, name = "Paladin", "", "Imprisoned Celestial"
	mana, attack, health = 3, 4, 5
	index = "DARKMOON_FAIRE~Paladin~Minion~3~4~5~~Imprisoned Celestial"
	requireTarget, keyWord, description = False, "", "Dormant for 2 turns. Spellburst: Give your minions Divine Shield"
	name_CN = "被禁锢的星骓"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_ImprisonedCelestial(self)]
		
class Trig_ImprisonedCelestial(Spellburst):
	def text(self, CHN):
		return "法术迸发：使你的随从获得圣盾" if CHN else "Spellburst: Give your minions Divine Shield"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		for minion in self.entity.Game.minionsonBoard(self.entity.ID):
			minion.getsStatus("Divine Shield")
			
			
class Rally(Spell):
	Class, school, name = "Paladin,Priest", "Holy", "Rally!"
	requireTarget, mana = False, 4
	index = "DARKMOON_FAIRE~Paladin,Priest~Spell~4~Holy~Rally!"
	description = "Resurrect a friendly 1-Cost, 2-Cost, and 3-Cost minion"
	name_CN = "开赛集结！"
	def available(self):
		return self.selectableMinionExists()
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		minionsDied = self.Game.Counters.minionsDiedThisTurn[self.ID]
		minions = []
		for i in ('1', '2', '3'):
			try: minions.append(npchoice((index for index in minionsDied if index.split('~')[3] == i)))
			except: pass
		minions = (self.Game.cardPool[index] for index in minions)
		if minions: self.summon([minion(self.Game, self.ID) for minion in minions], (-1, "totheRightEnd"))
		return None
		
		
class LibramofJudgment(Weapon):
	Class, name, description = "Paladin", "Libram of Judgment", "Corrupt: Gain Lifesteal"
	mana, attack, durability = 7, 5, 3
	index = "DARKMOON_FAIRE~Paladin~Weapon~7~5~3~Libram of Judgment~ToCorrupt"
	name_CN = "审判圣契"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsHand = [Trig_Corrupt(self, LibramofJudgment_Corrupt)] #只有在手牌中才会升级
		
class LibramofJudgment_Corrupt(Weapon):
	Class, name, description = "Paladin", "Libram of Judgment", "Corrupted. Lifesteal"
	mana, attack, durability = 7, 5, 3
	index = "DARKMOON_FAIRE~Paladin~Weapon~7~5~3~Libram of Judgment~Lifesteal~Corrupted~Uncollectible"
	name_CN = "审判圣契"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.keyWords["Lifesteal"] = 1
		
"""Priest Cards"""
class Hysteria(Spell):
	Class, school, name = "Priest,Warlock", "Shadow", "Hysteria"
	requireTarget, mana = True, 4
	index = "DARKMOON_FAIRE~Priest,Warlock~Spell~4~Shadow~Hysteria"
	description = "Choose a minion. It attacks random minions until it dies"
	name_CN = "狂乱"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target and target.onBoard:
			#The minion must still be onBoard and alive in order to continue the loop
			i = 0 #Assume the loop can only last 14 times
			while target.onBoard and target.health > 0 and not target.dead and i < 14:
				minions = self.Game.minionsAlive(target.ID, target) + self.Game.minionsAlive(3-target.ID)
				if minions:
					self.Game.battle(target, npchoice(minions), verifySelectable=False, useAttChance=True, resolveDeath=False, resetRedirTrig=False)
				else: break
				i += 1
		return target
		
		
class Lightsteed(Minion):
	Class, race, name = "Priest", "Elemental", "Lightsteed"
	mana, attack, health = 4, 3, 6
	index = "DARKMOON_FAIRE~Priest~Minion~4~3~6~Elemental~Lightsteed"
	requireTarget, keyWord, description = False, "", "Your healing effects also give affected minions +2 Health"
	name_CN = "圣光战马"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_Lightsteed(self)]
		
class Trig_Lightsteed(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["MinionGetsCured"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject.ID == self.entity.ID
		
	def text(self, CHN):
		return "你的治疗效果同时会使受到影响的随从获得+2生命值" if CHN else "Your healing effects also give affected minions +2 Health"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		target.buffDebuff(0, 2)
		
		
class DarkInquisitorXanesh(Minion):
	Class, race, name = "Priest", "", "Dark Inquisitor Xanesh"
	mana, attack, health = 5, 3, 5
	index = "DARKMOON_FAIRE~Priest~Minion~5~3~5~~Dark Inquisitor Xanesh~Battlecry~Legendary"
	requireTarget, keyWord, description = False, "", "Your healing effects also give affected minions +2 Health"
	name_CN = "黑暗审判官夏奈什"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		for card in self.Game.Hand_Deck.hands[self.ID]:
			if "~ToCorrupt" in card.index:
				ManaMod(card, changeby=-2, changeto=-1).applies()
		for card in self.Game.Hand_Deck.decks[self.ID]:
			if "~ToCorrupt" in card.index:
				ManaMod(card, changeby=-2, changeto=-1).applies()
		return None
		
"""Rogue Cards"""
class NitroboostPoison(Spell):
	Class, school, name = "Rogue,Warrior", "Nature", "Nitroboost Poison"
	requireTarget, mana = True, 2
	index = "DARKMOON_FAIRE~Rogue,Warrior~Spell~2~Nature~Nitroboost Poison~ToCorrupt"
	description = "Give a minion +2 Attack. Corrupt: And your weapon"
	name_CN = "氮素药膏"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsHand = [Trig_Corrupt(self, NitroboostPoison_Corrupt)] #只有在手牌中才会升级
		
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			target.buffDebuff(2, 0)
		return target
		
class NitroboostPoison_Corrupt(Spell):
	Class, school, name = "Rogue,Warrior", "Nature", "Nitroboost Poison"
	requireTarget, mana = True, 2
	index = "DARKMOON_FAIRE~Rogue,Warrior~Spell~2~Nature~Nitroboost Poison~Corrupted~Uncollectible"
	description = "Corrupted: Give a minion and your weapon +2 Attack"
	name_CN = "氮素药膏"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			target.buffDebuff(2, 0)
			weapon = self.Game.availableWeapon(self.ID)
			if weapon: weapon.gainStat(2, 0)
		return target
		
class Shenanigans(Secret):
	Class, school, name = "Rogue", "", "Shenanigans"
	requireTarget, mana = False, 2
	index = "DARKMOON_FAIRE~Rogue~Spell~2~~Shenanigans~~Secret"
	description = "Secret: When your opponent draws their second card in a turn, transform it into a Banana"
	name_CN = "蕉猾诡计"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_Shenanigans(self)]
		
class Trig_Shenanigans(SecretTrigger):
	def __init__(self, entity):
		super().__init__(entity, ["CardDrawn"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		#假设即使第二张被爆牌也会触发
		secret = self.entity
		return self.entity.ID != self.entity.Game.turn and self.entity.ID != ID and self.entity.Game.Counters.numCardsDrawnThisTurn[ID] == 1
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		card = Bananas(self.entity.Game, self.entity.ID)
		self.entity.Game.Hand_Deck.replaceCardDrawn(target, card)
		
		
class SparkjoyCheat(Minion_Dormantfor2turns):
	Class, race, name = "Rogue", "", "Sparkjoy Cheat"
	mana, attack, health = 3, 3, 3
	index = "DARKMOON_FAIRE~Rogue~Minion~3~3~3~~Sparkjoy Cheat~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: If you're holding a Secret, cast it and draw a card"
	name_CN = "欢脱的作弊选手"
	def effCanTrig(self):
		self.effectViable = any(card.description.startswith("Secret:") and not self.Game.Secrets.sameSecretExists(card, self.ID) \
									for card in self.Game.Hand_Deck.hands[self.ID])
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		secrets = [i for i, card in enumerate(self.Game.Hand_Deck.hands[self.ID]) \
				   if card.description.startswith("Secret:") and not self.Game.Secrets.sameSecretExists(card, self.ID)]
		if secrets:
			self.Game.Hand_Deck.extractfromHand(npchoice(secrets), self.ID, enemyCanSee=False)[0].whenEffective()
			self.Game.Hand_Deck.drawCard(self.ID)
		return None
		
		
"""Shaman Cards"""
class ImprisonedPhoenix(Minion_Dormantfor2turns):
	Class, race, name = "Shaman,Mage", "Elemental", "Imprisoned Phoenix"
	mana, attack, health = 2, 2, 3
	index = "DARKMOON_FAIRE~Shaman,Mage~Minion~2~2~3~Elemental~Imprisoned Phoenix~Spell Damge"
	requireTarget, keyWord, description = False, "", "Dormant for 2 turns. Spell Damage +2"
	name_CN = "被禁锢的凤凰"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.keyWords["Spell Damage"] = 2
		
		
class Landslide(Spell):
	Class, school, name = "Shaman", "Nature", "Landslide"
	requireTarget, mana = False, 2
	index = "DARKMOON_FAIRE~Shaman~Spell~2~Nature~Landslide"
	description = "Deal 1 damage to all enemy minions. If you're Overloaded, deal 1 damage again"
	name_CN = "大地崩陷"
	def text(self, CHN):
		damage = (1 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		return "对所有敌方随从造成%d点伤害。如果你有过载的法力水晶，再次造成%d点伤害"%(damage, damage) \
				if CHN else "Deal %d damage to all enemy minions. If you're Overloaded, deal %d damage again"%(damage, damage)
				
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		damage = (1 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		targets = self.Game.minionsonBoard(3-self.ID)
		if targets:
			self.dealsAOE(targets, [damage]*len(targets))
			#假设插入随从的死亡结算
			self.Game.gathertheDead()
			damage = (1 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			targets = self.Game.minionsonBoard(3-self.ID)
			self.dealsAOE(targets, [damage]*len(targets))
		return None
		
		
class Mistrunner(Minion):
	Class, race, name = "Shaman", "", "Mistrunner"
	mana, attack, health = 5, 4, 4
	index = "DARKMOON_FAIRE~Shaman~Minion~5~4~4~~Mistrunner~Battlecry~Overload"
	requireTarget, keyWord, description = True, "", "Battlecry: Give a friendly minion +3/+3. Overload: (1)"
	name_CN = "迷雾行者"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.overload = 1
		
	def targetExists(self, choice=0):
		return self.selectableFriendlyMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.ID == self.ID and target.onBoard and target != self
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			target.buffDebuff(3, 3)
		return target
		
"""Warlock Cards"""
class Backfire(Spell):
	Class, school, name = "Warlock", "Fire", "Backfire"
	requireTarget, mana = False, 3
	index = "DARKMOON_FAIRE~Warlock~Spell~3~Fire~Backfire"
	description = "Draw 3 cards. Deal 3 damage to your hero"
	name_CN = "赛车回火"
	def text(self, CHN):
		damage = (3 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		return "抽3张牌。对你的英雄造成%d点伤害"%damage if CHN else "Draw 3 cards. Deal %d damage to your hero"%damage
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		damage = (3 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		for i in range(3):
			self.Game.Hand_Deck.drawCard(self.ID)
		self.dealsDamage(self.Game.heroes[self.ID], damage)
		return None
		
		
class LuckysoulHoarder(Minion):
	Class, race, name = "Warlock,Demon Hunter", "", "Luckysoul Hoarder"
	mana, attack, health = 3, 3, 4
	index = "DARKMOON_FAIRE~Warlock,Demon Hunter~Minion~3~3~4~~Luckysoul Hoarder~Battlecry~ToCorrupt"
	requireTarget, keyWord, description = False, "", "Battlecry: Shuffle 2 Soul Fragments into your deck. Corrupt: Draw a card"
	name_CN = "幸运之魂囤积者"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsHand = [Trig_Corrupt(self, LuckysoulHoarder_Corrupt)] #只有在手牌中才会升级
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.Game.Hand_Deck.shuffleintoDeck([SoulFragment(self.Game, self.ID) for i in range(2)], creator=self)
		return None
		
class LuckysoulHoarder_Corrupt(Minion):
	Class, race, name = "Warlock,Demon Hunter", "", "Luckysoul Hoarder"
	mana, attack, health = 3, 3, 4
	index = "DARKMOON_FAIRE~Warlock,Demon Hunter~Minion~3~3~4~~Luckysoul Hoarder~Battlecry~Corrupted~Uncollectible"
	requireTarget, keyWord, description = False, "", "Corrupted. Battlecry: Shuffle 2 Soul Fragments into your deck. Draw a card"
	name_CN = "幸运之魂囤积者"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.Game.Hand_Deck.shuffleintoDeck([SoulFragment(self.Game, self.ID) for i in range(2)], creator=self)
		self.Game.Hand_Deck.drawCard(self.ID)
		return None
		
		
class EnvoyRustwix(Minion):
	Class, race, name = "Warlock", "Demon", "Envoy Rustwix"
	mana, attack, health = 5, 5, 4
	index = "DARKMOON_FAIRE~Warlock~Minion~5~5~4~Demon~Envoy Rustwix~Deathrattle~Legendary"
	requireTarget, keyWord, description = False, "", "Deathrattle: Shuffle 3 random Prime Legendary minions into your deck"
	name_CN = "铁锈特使拉斯维克斯"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.deathrattles = [Shuffle3PrimesintoYourDeck(self)]
		
class Shuffle3PrimesintoYourDeck(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		minion = self.entity
		pool = (MsshifnPrime, ZixorPrime, SolarianPrime, MurgurglePrime, ReliquaryPrime,
					AkamaPrime, VashjPrime, KanrethadPrime, KargathPrime)
		primes = npchoice(pool, 3, replace=True)
		minion.shuffleintoDeck([prime(minion.Game, minion.ID) for prime in primes])
		
	def text(self, CHN):
		return "亡语：随机将3张终极传说随从洗入你的牌库" if CHN else "Deathrattle: Shuffle 3 random Prime Legendary minions into your deck"
		
		
"""Warrior Cards"""
class SpikedWheel(Weapon):
	Class, name, description = "Warrior", "Spiked Wheel", "Has +3 Attack when your hero has Armor"
	mana, attack, durability = 1, 0, 2
	index = "DARKMOON_FAIRE~Warrior~Weapon~1~0~2~Spiked Wheel"
	name_CN = "尖刺轮盘"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.auras["Has +3 Attack when your hero has Armor"] = WeaponBuffAura_SpikedWheel(self)
		
class WeaponBuffAura_SpikedWheel:
	def __init__(self, weapon):
		self.weapon = weapon
		self.auraAffected = []
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.weapon.onBoard and ID == self.weapon.ID
		
	def trig(self, signal, ID, subject, target, number, comment, choice=0):
		if self.canTrigger(signal, ID, subject, target, number, comment):
			self.effect(signal, ID, subject, target, number, comment)
			
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		for weapon, receiver in self.auraAffected[:]:
			receiver.effectClear()
		armor = self.weapon.Game.heroes[ID].armor
		if armor > 0: Stat_Receiver(self.weapon, self, armor, 0).effectStart()
		
	def auraAppears(self):
		game, ID = self.weapon.Game, self.weapon.ID
		armor = game.heroes[ID].armor
		if armor > 0: Stat_Receiver(self.weapon, self, armor, 0).effectStart()
		
		try: game.trigsBoard[ID]["ArmorGained"].append(self)
		except: game.trigsBoard[ID]["ArmorGained"] = [self]
		try: game.trigsBoard[ID]["ArmorLost"].append(self)
		except: game.trigsBoard[ID]["ArmorLost"] = [self]
		
	def auraDisappears(self):
		game, ID = self.weapon.Game, self.weapon.ID
		for weapon, receiver in self.auraAffected[:]:
			receiver.effectClear()
		self.auraAffected = []
		try: game.trigsBoard[ID]["ArmorGained"].remove(self)
		except: pass
		try: game.trigsBoard[ID]["ArmorLost"].remove(self)
		except: pass
		
		
class Ironclad(Minion):
	Class, race, name = "Warrior", "Mech", "Ironclad"
	mana, attack, health = 3, 2, 4
	index = "DARKMOON_FAIRE~Warrior~Minion~3~2~4~Mech~Ironclad~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: If your hero has Armor, gain +2/+2"
	name_CN = "铁甲战车"
	
	def effCanTrig(self):
		self.effectViable = self.Game.heroes[self.ID].armor > 0
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if self.Game.heroes[self.ID].armor > 0:
			self.buffDebuff(2, 2)
		return None
		
		
class Barricade(Spell):
	Class, school, name = "Warrior,Paladin", "", "Barricade"
	requireTarget, mana = False, 4
	index = "DARKMOON_FAIRE~Warrior,Paladin~Spell~4~~Barricade"
	description = "Summon a 2/4 Guard with Taunt. If it's your only minion, summon another"
	name_CN = "路障"
	def available(self):
		return self.Game.space(self.ID) > 0
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.summon(RaceGuard(self.Game, self.ID), -1)
		#Note that at this stage, there won't be deaths/deathrattles resolved.
		if len(self.Game.minionsonBoard(self.ID)) == 1:
			self.summon(RaceGuard(self.Game, self.ID), -1)
		return target
		
class RaceGuard(Minion):
	Class, race, name = "Warrior,Paladin", "", "Race Guard"
	mana, attack, health = 3, 2, 4
	index = "DARKMOON_FAIRE~Warrior,Paladin~Minion~3~2~4~~Race Guard~Taunt~Uncollectible"
	requireTarget, keyWord, description = False, "Taunt", "Taunt"
	name_CN = "赛道护卫"
	
	
Darkmoon_Cards = [#Neutral cards
				SafetyInspector, CostumedEntertainer, HorrendousGrowth, HorrendousGrowthCorrupt, ParadeLeader, PrizeVendor, RockRager, Showstopper, WrigglingHorror, BananaVendor, DarkmoonDirigible, DarkmoonDirigible_Corrupt, DarkmoonStatue, DarkmoonStatue_Corrupt, Gyreworm, InconspicuousRider, KthirRitualist, CircusAmalgam, CircusMedic, CircusMedic_Corrupt, FantasticFirebird, KnifeVendor, DerailedCoaster, DarkmoonRider, FleethoofPearltusk, FleethoofPearltusk_Corrupt, OptimisticOgre, ClawMachine, SilasDarkmoon, Strongman, Strongman_Corrupt, CarnivalClown, CarnivalClown_Corrupt, BodyofCThun, CThunsBody, EyeofCThun, HeartofCThun, MawofCThun, CThuntheShattered, DarkmoonRabbit, NZothGodoftheDeep, YoggSaronMasterofFate, CurseofFlesh, HandofFate, YShaarjtheDefiler,
				#Demon Hunter cards
				FelscreamBlast, ThrowGlaive, RedeemedPariah, Acrobatics, DreadlordsBite, FelsteelExecutioner, FelsteelExecutioner_Corrupt, LineHopper, InsatiableFelhound, InsatiableFelhound_Corrupt, RelentlessPursuit, Stiltstepper, Ilgynoth, RenownedPerformer, PerformersAssistant, ZaitheIncredible, BladedLady, ExpendablePerformers, 
				#Druid cards
				GuesstheWeight, LunarEclipse, SolarEclipse, FaireArborist, FaireArborist_Corrupt, MoontouchedAmulet, MoontouchedAmulet_Corrupt, KiriChosenofElune, Greybough, UmbralOwl, CenarionWard, FizzyElemental, 
				#Hunter cards
				MysteryWinner, DancingCobra, DancingCobra_Corrupt, DontFeedtheAnimals, DontFeedtheAnimals_Corrupt, OpentheCages, PettingZoo, DarkmoonStrider, RinlingsRifle, TramplingRhino, MaximaBlastenheimer, DarkmoonTonk, JewelofNZoth, 
				#Mage cards
				ConfectionCyclone, SugarElemental, DeckofLunacy, GameMaster, RiggedFaireGame, OccultConjurer, RingToss, RingToss_Corrupt, FireworkElemental, FireworkElemental_Corrupt, SaygeSeerofDarkmoon, MaskofCThun, GrandFinale, ExplodingSparkler, 
				#Paladin cards
				OhMyYogg, RedscaleDragontamer, SnackRun, CarnivalBarker, DayattheFaire, DayattheFaire_Corrupt, BalloonMerchant, CarouselGryphon, CarouselGryphon_Corrupt, LothraxiontheRedeemed, HammeroftheNaaru, HolyElemental, HighExarchYrel, 
				#Priest cards
				Insight, Insight_Corrupt, FairgroundFool, FairgroundFool_Corrupt, NazmaniBloodweaver, PalmReading, AuspiciousSpirits, AuspiciousSpirits_Corrupt, TheNamelessOne, FortuneTeller, IdolofYShaarj, GhuuntheBloodGod, BloodofGhuun, 
				#Rogue cards
				PrizePlunderer, FoxyFraud, ShadowClone, SweetTooth, SweetTooth_Corrupt, Swindle, TenwuoftheRedSmoke, CloakofShadows, TicketMaster, Tickets, PlushBear, MalevolentStrike, GrandEmpressShekzara, 
				#Shaman cards
				Revolve, CagematchCustodian, DeathmatchPavilion, PavilionDuelist, GrandTotemEysor, Magicfin, PitMaster, PitMaster_Corrupt, Stormstrike, WhackAGnollHammer, DunkTank, DunkTank_Corrupt, InaraStormcrash, 
				#Warlock cards
				WickedWhispers, MidwayManiac, FreeAdmission, ManariMosher, CascadingDisaster, CascadingDisaster_Corrupt, CascadingDisaster_Corrupt2, RevenantRascal, FireBreather, DeckofChaos, RingMatron, FieryImp, Tickatus, Tickatus_Corrupt, 
				#Warrior cards
				StageDive, StageDive_Corrupt, BumperCar, ETCGodofMetal, Minefield, RingmastersBaton, StageHand, FeatofStrength, SwordEater, Jawbreaker, RingmasterWhatley, TentTrasher,
	
				#Race
				#Neutral
				ArmorVendor, Crabrider, Deathwarden, Moonfang, RunawayBlackwing,
				#Class cards
				IllidariStudies, FelfireDeadeye, Felsaber, Guidance, DreamingDrake, DreamingDrake_Corrupt, ArborUp, ResizingPouch, BolaShot, Saddlemaster,
				GlacierRacer, ConjureManaBiscuit, ManaBiscuit, KeywardenIvory, ImprisonedCelestial, Rally, LibramofJudgment, LibramofJudgment_Corrupt, Hysteria, Lightsteed, DarkInquisitorXanesh,
				NitroboostPoison, NitroboostPoison_Corrupt, Shenanigans, SparkjoyCheat, ImprisonedPhoenix, Landslide, Mistrunner, Backfire, LuckysoulHoarder, LuckysoulHoarder_Corrupt, EnvoyRustwix, SpikedWheel, Ironclad, Barricade, RaceGuard,
				]

Darkmoon_Cards_Collectible = [#Neutral
							SafetyInspector, CostumedEntertainer, HorrendousGrowth, ParadeLeader, PrizeVendor, RockRager, Showstopper, WrigglingHorror, BananaVendor, DarkmoonDirigible, DarkmoonStatue, Gyreworm, InconspicuousRider, KthirRitualist, CircusAmalgam, CircusMedic, FantasticFirebird, KnifeVendor, DerailedCoaster, FleethoofPearltusk, OptimisticOgre, ClawMachine, SilasDarkmoon, Strongman, CarnivalClown, CThuntheShattered, DarkmoonRabbit, NZothGodoftheDeep, YoggSaronMasterofFate, YShaarjtheDefiler,
							#Demon Hunter
							FelscreamBlast, ThrowGlaive, RedeemedPariah, Acrobatics, DreadlordsBite, FelsteelExecutioner, LineHopper, InsatiableFelhound, RelentlessPursuit, Stiltstepper, Ilgynoth, RenownedPerformer, ZaitheIncredible, BladedLady, ExpendablePerformers,
							#Druid
							GuesstheWeight, LunarEclipse, SolarEclipse, FaireArborist, MoontouchedAmulet, KiriChosenofElune, Greybough, UmbralOwl, CenarionWard, FizzyElemental,
							#Hunter
							MysteryWinner, DancingCobra, DontFeedtheAnimals, OpentheCages, PettingZoo, RinlingsRifle, TramplingRhino, MaximaBlastenheimer, DarkmoonTonk, JewelofNZoth,
							#Mage
							ConfectionCyclone, DeckofLunacy, GameMaster, RiggedFaireGame, OccultConjurer, RingToss, FireworkElemental, SaygeSeerofDarkmoon, MaskofCThun, GrandFinale,
							#Paladin
							OhMyYogg, RedscaleDragontamer, SnackRun, CarnivalBarker, DayattheFaire, BalloonMerchant, CarouselGryphon, LothraxiontheRedeemed, HammeroftheNaaru, HighExarchYrel,
							#Priest
							Insight, FairgroundFool, NazmaniBloodweaver, PalmReading, AuspiciousSpirits, TheNamelessOne, FortuneTeller, IdolofYShaarj, GhuuntheBloodGod, BloodofGhuun,
							#Rogue
							PrizePlunderer, FoxyFraud, ShadowClone, SweetTooth, Swindle, TenwuoftheRedSmoke, CloakofShadows, TicketMaster, MalevolentStrike, GrandEmpressShekzara,
							#Shaman
							Revolve, CagematchCustodian, DeathmatchPavilion, GrandTotemEysor, Magicfin, PitMaster, Stormstrike, WhackAGnollHammer, DunkTank, InaraStormcrash,
							#Warlock
							WickedWhispers, MidwayManiac, FreeAdmission, ManariMosher, CascadingDisaster, RevenantRascal, FireBreather, DeckofChaos, RingMatron, Tickatus,
							#Warrior
							StageDive, BumperCar, ETCGodofMetal, Minefield, RingmastersBaton, StageHand, FeatofStrength, SwordEater, RingmasterWhatley, TentTrasher,
							#Neutral
							ArmorVendor, Crabrider, Deathwarden, Moonfang, RunawayBlackwing,
							#Class cards
							IllidariStudies, FelfireDeadeye, Felsaber, Guidance, DreamingDrake, ArborUp, ResizingPouch, BolaShot, Saddlemaster, GlacierRacer, ConjureManaBiscuit, KeywardenIvory,
							ImprisonedCelestial, Rally, LibramofJudgment, Hysteria, Lightsteed, DarkInquisitorXanesh, NitroboostPoison, Shenanigans, SparkjoyCheat, ImprisonedPhoenix,
							Landslide, Mistrunner, Backfire, LuckysoulHoarder, EnvoyRustwix, SpikedWheel, Ironclad, Barricade,
							]