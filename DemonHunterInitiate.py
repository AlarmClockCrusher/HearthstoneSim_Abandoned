from CardTypes import *
from Triggers_Auras import *
from numpy.random import choice as npchoice
from numpy.random import randint as nprandint
from numpy.random import shuffle as npshuffle
from numpy import inf as npinf

from AcrossPacks import IllidariInitiate

""""Demon Hunter Yr Dragon cards"""

"""Mana 0 cards"""
class Blur(Spell):
	Class, school, name = "Demon Hunter", "", "Blur"
	requireTarget, mana = False, 0
	index = "DEMON_HUNTER_INITIATE~Demon Hunter~Spell~0~~Blur"
	description = "Your hero can't take damage this turn"
	name_CN = "疾影"
	#不知道与博尔碎盾的结算是如何进行的。
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		Blur_Effect(self.Game, self.ID).connect()
		return None
		
class Blur_Effect:
	def __init__(self, Game, ID):
		self.Game, self.ID = Game, ID
		self.signals = ["FinalDmgonHero?"]
		self.temp = False
		
	def connect(self):
		try: self.Game.trigsBoard[self.ID]["FinalDmgonHero?"].append(self)
		except: self.Game.trigsBoard[self.ID]["FinalDmgonHero?"] = [self]
		self.Game.turnEndTrigger.append(self)
		
	def disconnect(self):
		try: self.Game.trigsBoard[self.ID]["FinalDmgonHero?"].remove(self)
		except: pass
		try: self.Game.turnEndTrigger.remove(self)
		except: pass
		#number here is a list that holds the damage to be processed
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return target.ID == self.ID and target.onBoard
		
	def trig(self, signal, ID, subject, target, number, comment, choice=0):
		if self.canTrig(signal, ID, subject, target, number, comment):
			if self.Game.GUI: self.Game.GUI.showOffBoardTrig(Blur(self.Game, self.ID))
			self.effect(signal, ID, subject, target, number, comment)
			
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		number[0] = 0
		
	def turnEndTrigger(self):
		self.disconnect()
		
	def createCopy(self, game): #不是纯的只在回合结束时触发，需要完整的createCopy
		if self not in game.copiedObjs: #这个扳机没有被复制过
			trigCopy = type(self)(game, self.ID)
			game.copiedObjs[self] = trigCopy
			return trigCopy
		else: #一个扳机被复制过了，则其携带者也被复制过了
			return game.copiedObjs[self]
			
			
class TwinSlice(Spell):
	Class, school, name = "Demon Hunter", "", "Twin Slice"
	requireTarget, mana = False, 1
	index = "DEMON_HUNTER_INITIATE~Demon Hunter~Spell~1~~Twin Slice"
	description = "Give your hero +2 Attack this turn. Add 'Second Slice' to your hand"
	name_CN = "双刃斩击"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.Game.heroes[self.ID].gainAttack(2)
		self.Game.Hand_Deck.addCardtoHand(SecondSlice(self.Game, self.ID), self.ID)
		return None
		
class SecondSlice(Spell):
	Class, school, name = "Demon Hunter", "", "Second Slice"
	requireTarget, mana = False, 1
	index = "DEMON_HUNTER_INITIATE~Demon Hunter~Spell~1~~Second Slice~Uncollectible"
	description = "Give your hero +2 Attack this turn"
	name_CN = "二次斩击"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.Game.heroes[self.ID].gainAttack(2)
		return None
		
		
"""Mana 1 cards"""
class Battlefiend(Minion):
	Class, race, name = "Demon Hunter", "Demon", "Battlefiend"
	mana, attack, health = 1, 1, 2
	index = "DEMON_HUNTER_INITIATE~Demon Hunter~Minion~1~1~2~Demon~Battlefiend"
	requireTarget, keyWord, description = False, "", "After your hero attacks, gain +1 Attack"
	name_CN = "战斗邪犬"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_Battlefiend(self)]
		
class Trig_Battlefiend(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["HeroAttackedMinion", "HeroAttackedHero"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject == self.entity.Game.heroes[self.entity.ID]
		
	def text(self, CHN):
		return "在你的英雄攻击后，获得+1攻击力" if CHN else "After your hero attacks, gain +1 Attack"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.buffDebuff(1, 0)
		
		
class ConsumeMagic(Spell):
	Class, school, name = "Demon Hunter", "Shadow", "Consume Magic"
	requireTarget, mana = True, 1
	index = "DEMON_HUNTER_INITIATE~Demon Hunter~Spell~1~Shadow~Consume Magic~Outcast"
	description = "Silence an enemy minion. Outcast: Draw a card"
	name_CN = "吞噬魔法"
	def available(self):
		return self.selectableEnemyMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.ID != self.ID and target.onBoard
		
	def effCanTrig(self):
		self.effectViable = self.Game.Hand_Deck.outcastcanTrig(self)
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			target.getsSilenced()
		if posinHand == 0 or posinHand == -1:
			self.Game.Hand_Deck.drawCard(self.ID)
		return target
		
		
class ManaBurn(Spell):
	Class, school, name = "Demon Hunter", "Fel", "Mana Burn"
	requireTarget, mana = False, 1
	index = "DEMON_HUNTER_INITIATE~Demon Hunter~Spell~1~Fel~Mana Burn"
	description = "Your opponent has 2 fewer Mana Crystals next turn"
	name_CN = "法力燃烧"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.Game.Manas.manas_withheld[3-self.ID] += 2
		self.Game.turnStartTrigger.append(TwoFewerManaEffectRemoved(self.Game, 3-self.ID))
		return None
		
#不知道这个少两个法力水晶是让它们空两个还是直接少真实的水晶
class TwoFewerManaEffectRemoved:
	def __init__(self, Game, ID):
		self.Game, self.ID = Game, ID
		
	def text(self, CHN):
		return "玩家%d的下个回合减少2个法力水晶"%self.ID if CHN \
				else "Player %d's next turn has 2 fewer Mana Crystals"%self.ID
				
	def turnStartTrigger(self):
		self.Game.Manas.manas_withheld[self.ID] -= 2
		try: self.Game.turnStartTrigger.remove(self)
		except: pass
		
	def createCopy(self, game):
		return type(self)(game, self.ID)
		
		
class UrzulHorror(Minion):
	Class, race, name = "Demon Hunter", "Demon", "Ur'zul Horror"
	mana, attack, health = 1, 2, 1
	index = "DEMON_HUNTER_INITIATE~Demon Hunter~Minion~1~2~1~Demon~Ur'zul Horror~Deathrattle"
	requireTarget, keyWord, description = False, "", "Deathrattle: Add a 2/1 Lost Soul to your hand"
	name_CN = "乌祖尔恐魔"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.deathrattles = [AddaLostSoultoYourHand(self)]
		
class AddaLostSoultoYourHand(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.Game.Hand_Deck.addCardtoHand(LostSoul, self.entity.ID, "type")
		
	def text(self, CHN):
		return "亡语：将一张2/1的“迷失之魂”置入你的手牌" if CHN else "Deathrattle: Add a 2/1 Lost Soul to your hand"
		
class LostSoul(Minion):
	Class, race, name = "Demon Hunter", "", "Lost Soul"
	mana, attack, health = 1, 2, 1
	index = "DEMON_HUNTER_INITIATE~Demon Hunter~Minion~1~2~1~~Lost Soul~Uncollectible"
	requireTarget, keyWord, description = False, "", ""
	name_CN = "迷失之魂"
	
	
"""Mana 2 cards"""
class BladeDance(Spell):
	Class, school, name = "Demon Hunter", "", "Blade Dance"
	requireTarget, mana = False, 3
	index = "DEMON_HUNTER_INITIATE~Demon Hunter~Spell~3~~Blade Dance"
	description = "Deal damage equal to your hero's Attack to 3 random enemy minions"
	name_CN = "刃舞"
	def available(self):
		return self.Game.heroes[self.ID].attack > 0
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		damage = (self.Game.heroes[self.ID].attack + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		curGame = self.Game
		minions = curGame.minionsAlive(3-self.ID)
		if damage > 0 and minions:
			if curGame.mode == 0:
				if curGame.picks:
					minions = [curGame.minions[3-self.ID][i] for i in curGame.picks.pop(0)]
				else:
					minions = list(npchoice(minions, min(3, len(minions)), replace=False))
					curGame.picks.append(tuple([minion.pos for minion in minions]))
				self.dealsAOE(minions, [damage]*len(minions))
		return None
		
		
class FeastofSouls(Spell):
	Class, school, name = "Demon Hunter", "Shadow", "Feast of Souls"
	requireTarget, mana = False, 2
	index = "DEMON_HUNTER_INITIATE~Demon Hunter~Spell~2~Shadow~Feast of Souls"
	description = "Draw a card for each friendly minion that died this turn"
	name_CN = "灵魂盛宴"
	def effCanTrig(self):
		self.effectViable = self.Game.Counters.minionsDiedThisTurn[self.ID] != []
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		num = len(self.Game.Counters.minionsDiedThisTurn[self.ID])
		for i in range(num): self.Game.Hand_Deck.drawCard(self.ID)
		return None
		
		
class Umberwing(Weapon):
	Class, name, description = "Demon Hunter", "Umberwing", "Battlecry: Summon two 1/1 Felwings"
	mana, attack, durability = 2, 1, 2
	index = "DEMON_HUNTER_INITIATE~Demon Hunter~Weapon~2~1~2~Umberwing~Battlecry"
	name_CN = "棕红之翼"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.Game.summon([Felwing(self.Game, self.ID) for i in range(2)], (-1, "totheRightEnd"), self)
		return None
		
class Felwing(Minion):
	Class, race, name = "Demon Hunter", "Demon", "Felwing"
	mana, attack, health = 1, 1, 1
	index = "DEMON_HUNTER_INITIATE~Demon Hunter~Minion~1~1~1~Demon~Felwing~Uncollectible"
	requireTarget, keyWord, description = False, "", ""
	name_CN = "邪翼蝠"
	
	
"""Mana 3 cards"""
class AltruistheOutcast(Minion):
	Class, race, name = "Demon Hunter", "", "Altruis the Outcast"
	mana, attack, health = 4, 4, 2
	index = "DEMON_HUNTER_INITIATE~Demon Hunter~Minion~4~4~2~~Altruis the Outcast~Legendary"
	requireTarget, keyWord, description = False, "", "After you play the left- or right-most card in your hand, deal 1 damage to all enemies"
	name_CN = "流放者奥图里斯"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_AltruistheOutcast(self)]
		
class Trig_AltruistheOutcast(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["MinionBeenPlayed", "SpellBeenPlayed", "WeaponBeenPlayed", "HeroCardBeenPlayed"])
		
	#The comment passed is the position of card in hand when they are played.
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject.ID == self.entity.ID and subject != self.entity and (comment == -1 or comment == 0)
		
	def text(self, CHN):
		return "在你使用最左或最右的一张手牌后，对所有敌人造成1点伤害" if CHN \
				else "After you play the left- or right-most card in your hand, deal 1 damage to all enemies"
				
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		targets = [self.entity.Game.heroes[3-self.entity.ID]] + self.entity.Game.minionsonBoard(3-self.entity.ID)
		self.entity.dealsAOE(targets, [1] * len(targets))
		
		
class EyeBeam(Spell):
	Class, school, name = "Demon Hunter", "Fel", "Eye Beam"
	requireTarget, mana = True, 3
	index = "DEMON_HUNTER_INITIATE~Demon Hunter~Spell~3~Fel~Eye Beam~Outcast"
	description = "Lifesteal. Deal 3 damage to a minion. Outcast: This costs (1)"
	name_CN = "眼棱"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.keyWords["Lifesteal"] = 1
		self.trigsHand = [Trig_EyeBeam(self)]
		
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
		
	def effCanTrig(self):
		self.effectViable = self.Game.Hand_Deck.outcastcanTrig(self)
		
	def selfManaChange(self):
		if self.inHand:
			posinHand = self.Game.Hand_Deck.hands[self.ID].index(self)
			if posinHand == 0 or posinHand == len(self.Game.Hand_Deck.hands[self.ID]) - 1:
				self.mana = 1
				
	def text(self, CHN):
		damage = (3 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		return "吸血。对一个随从造成%d点伤害。流放：法力值消耗为(1)点"%damage if CHN \
				else "Lifesteal. Deal %d damage to a minion. Outcast: This costs (1)"%damage
				
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			damage = (3 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			self.dealsDamage(target, damage)
		return target
		
class Trig_EyeBeam(TrigHand):
	def __init__(self, entity):
		super().__init__(entity, ["CardLeavesHand", "CardEntersHand"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		if self.entity.inHand:
			card = target[0] if signal == "CardEntersHand" else target
			return card.ID == self.entity.ID
		return False
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.Game.Manas.calcMana_Single(self.entity)
		
		
class WrathscaleNaga(Minion):
	Class, race, name = "Demon Hunter", "", "Wrathscale Naga"
	mana, attack, health = 3, 3, 1
	index = "DEMON_HUNTER_INITIATE~Demon Hunter~Minion~3~3~1~~Wrathscale Naga"
	requireTarget, keyWord, description = False, "", "After a friendly minion dies, deal 3 damage to a random enemy"
	name_CN = "怒鳞纳迦"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_WrathscaleNaga(self)]
		
class Trig_WrathscaleNaga(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["MinionDied"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and target != self.entity and target.ID == self.entity.ID #Technically, minion has to disappear before dies. But just in case.
		
	def text(self, CHN):
		return "在一个友方随从死亡后，随从对一个敌人造成3点伤害" if CHN else "After a friendly minion dies, deal 3 damage to a random enemy"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		curGame = self.entity.Game
		if curGame.mode == 0:
			enemy = None
			if curGame.picks:
				i, where = curGame.picks.pop(0)
				if where: enemy = curGame.find(i, where)
			else:
				targets = curGame.charsAlive(3-self.entity.ID)
				if targets:
					enemy = npchoice(targets)
					curGame.picks.append((enemy.pos, enemy.type+str(enemy.ID)))
				else: curGame.picks.append((0, ""))
			if enemy:
				self.entity.dealsDamage(enemy, 1)
				
"""Mana 4 cards"""
class IllidariFelblade(Minion):
	Class, race, name = "Demon Hunter", "", "Illidari Felblade"
	mana, attack, health = 4, 5, 3
	index = "DEMON_HUNTER_INITIATE~Demon Hunter~Minion~4~5~3~~Illidari Felblade~Rush~Outcast"
	requireTarget, keyWord, description = False, "Rush", "Rush. Outcast: Gain Immune this turn"
	name_CN = "伊利达雷邪刃武士"
	
	def effCanTrig(self):
		self.effectViable = self.Game.Hand_Deck.outcastcanTrig(self)
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if posinHand == 0 or posinHand == -1:
			self.getsStatus("Immune")
		return None
		
		
class SoulSplit(Spell):
	Class, school, name = "Demon Hunter", "Shadow~", "Soul Split"
	requireTarget, mana = True, 4
	index = "DEMON_HUNTER_INITIATE~Demon Hunter~Spell~4~Shadow~Soul Split"
	description = "Choose a friendly Demon. Summon a copy of it"
	name_CN = "灵魂分裂"
	
	def available(self):
		return self.selectableFriendlyMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and "Demon" in target.race and target.ID == self.ID and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target and self.Game.space(self.ID) > 0:
			Copy = target.selfCopy(self.ID, self) if target.onBoard else type(target)(self.Game, self.ID)
			self.Game.summon(Copy, target.pos+1, self)
		return target
		
"""Mana 5 cards"""
class CommandtheIllidari(Spell):
	Class, school, name = "Demon Hunter", "", "Command the Illidari"
	requireTarget, mana = False, 5
	index = "DEMON_HUNTER_INITIATE~Demon Hunter~Spell~5~~Command the Illidari"
	description = "Summon six 1/1 Illidari with Rush"
	name_CN = "统率伊利达雷"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.Game.summon([IllidariInitiate(self.Game, self.ID) for i in range(6)], (-1, "totheRightEnd"), self)
		return None
		
class WrathspikeBrute(Minion):
	Class, race, name = "Demon Hunter", "Demon", "Wrathspike Brute"
	mana, attack, health = 5, 2, 6
	index = "DEMON_HUNTER_INITIATE~Demon Hunter~Minion~5~2~6~Demon~Wrathspike Brute~Taunt"
	requireTarget, keyWord, description = False, "Taunt", "Taunt. After this is attacked, deal 1 damage to all enemies"
	name_CN = "怒刺蛮兵"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_WrathspikeBrute(self)]
		
class Trig_WrathspikeBrute(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["MinionAttackedMinion", "HeroAttackedMinion"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and target == self.entity
		
	def text(self, CHN):
		return "在该随从被攻击后，对所有敌人造成1点伤害" if CHN else "After this is attacked, deal 1 damage to all enemies"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		targets = [self.entity.Game.heroes[3-self.entity.ID]] + self.entity.Game.minionsonBoard(3-self.entity.ID)
		self.entity.dealsAOE(targets, [1] * len(targets))
		
"""Mana 7 cards"""
class Flamereaper(Weapon):
	Class, name, description = "Demon Hunter", "Flamereaper", "Also damages the minions next to whomever your hero attacks"
	mana, attack, durability = 7, 4 ,3
	index = "DEMON_HUNTER_INITIATE~Demon Hunter~Weapon~7~4~3~Flamereaper"
	name_CN = "斩炎"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.marks["Sweep"] = 1
		
"""Mana 8 cards"""
class HulkingOverfiend(Minion):
	Class, race, name = "Demon Hunter", "Demon", "Hulking Overfiend"
	mana, attack, health = 8, 5, 10
	index = "DEMON_HUNTER_INITIATE~Demon Hunter~Minion~8~5~10~Demon~Hulking Overfiend~Rush"
	requireTarget, keyWord, description = False, "Rush", "Rush. After this attacks and kills a minion, it may attack again"
	name_CN = "巨型大恶魔"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_HulkingOverfiend(self)]
		
class Trig_HulkingOverfiend(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["MinionAttackedMinion"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject == self.entity and self.entity.health > 0 \
				and self.entity.dead == False and (target.health < 1 or target.dead == True)
				
	def text(self, CHN):
		return "在该随从攻击并消灭一个随从后，可再次攻击" if CHN \
				else "After this attacks and kills a minion, it may attack again"
				
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.attChances_extra += 1
		
		
class Nethrandamus(Minion):
	Class, race, name = "Demon Hunter", "Dragon", "Nethrandamus"
	mana, attack, health = 9, 8, 8
	index = "DEMON_HUNTER_INITIATE~Demon Hunter~Minion~9~8~8~Dragon~Nethrandamus~Battlecry~Legendary"
	requireTarget, keyWord, description = False, "", "Battlecry: Summon two random 0-Cost minions. (Upgrades each time a friendly minion dies!)"
	name_CN = "奈瑟兰达姆斯"
	poolIdentifier = "0-Cost Minions to Summon"
	@classmethod
	def generatePool(cls, pools):
		return ["%d-Cost Minions to Summon"%cost for cost in pools.MinionsofCost.keys()], \
				[list(pools.MinionsofCost[cost].values()) for cost in pools.MinionsofCost.keys()]
				
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsHand = [Trig_Nethrandamus(self)] #只有在手牌中才会升级
		self.progress = 0
		
	def text(self, CHN):
		return "战吼：随机召唤两个法力值消耗为(%d)的随从"%self.progress if CHN \
				else "Battlecry: Summon two random %d-Cost minions"%self.progress
				
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if curGame.mode == 0:
			if curGame.picks:
				minions = curGame.picks.pop(0)
			else:
				cost = self.progress
				while "%d-Cost Minions to Summon"%cost not in curGame.RNGPools: #假设计数过高，超出了费用范围，则取最高的可选费用
					cost -= 1
				minions = npchoice(self.rngPool("%d-Cost Minions to Summon"%cost), 2, replace=False)
				curGame.picks.append(tuple(minions))
			pos = (self.pos, "leftandRight") if self.onBoard else (-1, "totheRightEnd")
			curGame.summon([minion(curGame, self.ID) for minion in minions], pos, self)
		return None
		
class Trig_Nethrandamus(TrigHand):
	def __init__(self, entity):
		super().__init__(entity, ["MinionDies"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.inHand and target.ID == self.entity.ID
		
	def text(self, CHN):
		return "该随从在手牌中时，每有一个友方随从死亡便升级" if CHN \
				else "Upgrades in hand each time a friendly minions dies"
				
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.progress += 1
		
		
DemonHunterInit_Cards = []
							