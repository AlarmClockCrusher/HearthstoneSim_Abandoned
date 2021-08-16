from CardTypes import *
from Triggers_Auras import *
from numpy.random import choice as npchoice
from numpy.random import randint as nprandint
from numpy.random import shuffle as npshuffle
from numpy import inf as npinf

from AcrossPacks import Lackeys, HealingTotem, SearingTotem, StoneclawTotem, StrengthTotem, ManaWyrm
from Uldum import PlagueofDeath, PlagueofMadness, PlagueofMurlocs, PlagueofFlames, PlagueofWrath
from Outlands import Minion_Dormantfor2turns

from Panda_CustomWidgets import posHandsTable, hprHandsTable, HandZone1_Y, HandZone2_Y, HandZone_Z

"""Scholomance Academy"""
#可以通过宣传牌确认是施放法术之后触发
class Spellburst(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["SpellBeenPlayed"])
		self.oneTime = True
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject.ID == self.entity.ID
		
	def trig(self, signal, ID, subject, target, number, comment, choice=0):
		if self.canTrig(signal, ID, subject, target, number, comment):
			btn, GUI = self.entity.btn, self.entity.Game.GUI
			if btn and "SpecTrig" in btn.icons:
				icon = btn.icons["SpecTrig"]
				GUI.seqHolder[-1].append(GUI.PARALLEL(GUI.FUNC(icon.trigAni_1stHalf), GUI.WAIT(0.5)))
				GUI.seqHolder[-1].append(GUI.FUNC(icon.np.setColor, 1, 1, 1, 0))  #
				GUI.seqHolder[-1].append(GUI.PARALLEL(GUI.FUNC(icon.trigAni_2ndHalf), GUI.WAIT(0.5)))
			self.entity.losesTrig(self)
			self.effect(signal, ID, subject, target, number, comment)


"""
经典-奥格瑞玛	战吼：造成2点伤害
经典-暴风城	圣盾
经典-荆棘谷	潜行，剧毒
经典-潘达利亚四风谷	战吼：使一个友方随从获得+1/+2
纳克萨玛斯的诅咒	亡语：随机将一个具有亡语的随从置入你的手牌
地精大战侏儒	战吼,亡语：将一张零件牌置入你的手牌
黑石山的火焰	在你的回合结束 时随机使你的一张手牌法力值消耗减少(2)点
冠军的试炼	激励：抽一张牌
探险者协会-博物馆		战吼：发现一个新的基础英雄技能
探险者协会-废墟之城	战吼：随机将一张武器牌置入你的手牌
上古之神的低语-腐化的暴风城	战吼：消耗你所有的法力值，随机召唤一个法力值消耗相同的随从
卡拉赞之夜	战吼：随机将一张卡拉赞传送六法术牌置入你的手牌（大漩涡传送门，银月城传送门，铁炉堡传送门，月光林地传送门，火焰之地传送门
）
龙争虎斗加基森 战吼：随机使你手牌中的一张随从牌获得+2/+2
勇闯安戈洛	战吼：进化
冰封王府的骑士	亡语：随机将一张死亡骑士牌置入你的手牌
狗头人与地下世界	战吼：招募一个法力值消耗小于或等于（2）点的随从
女巫森林	回响，突袭
砰砰计划	嘲讽，战吼：如果你有十个法力水晶，获得+5/+5
拉斯塔哈大乱斗	突袭，超杀：抽一张牌
暗影崛起	战吼：将一张跟班牌置入你的手牌

奥丹姆奇兵-沙漠	复生
奥丹姆奇兵-绿洲	战吼：将一张奥丹姆灾祸法术牌置入你的手牌
巨龙降临	战吼：发现一张龙牌
外域的灰烬	休眠两回合。唤醒时，随机对两个敌方随从造成3点伤害。
通灵学园	战吼：将一张双职业卡牌置入你的手牌
暗月马戏团 腐蚀： 获得+2/+2
"""
class TransferStudent(Minion):
	Class, race, name = "Neutral", "", "Transfer Student"
	mana, attack, health = 2, 2, 2
	index = "SCHOLOMANCE~Neutral~Minion~2~2~2~~Transfer Student~Vanilla"
	requireTarget, keyWord, description = False, "", "This has different effects based on which game board you're on"
	name_CN = "转校生"
	
class TransferStudent_Ogrimmar(Minion):
	Class, race, name = "Neutral", "", "Transfer Student"
	mana, attack, health = 2, 2, 2
	index = "SCHOLOMANCE~Neutral~Minion~2~2~2~~Transfer Student~Ogrimmar~Battlecry"
	requireTarget, keyWord, description = True, "", "Battlecry: Deal 2 damage"
	name_CN = "转校生"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			self.dealsDamage(target, 2)
		return target
		
class TransferStudent_Stormwind(Minion):
	Class, race, name = "Neutral", "", "Transfer Student"
	mana, attack, health = 2, 2, 2
	index = "SCHOLOMANCE~Neutral~Minion~2~2~2~~Transfer Student~Stormwind~Divine Shield"
	requireTarget, keyWord, description = False, "Divine Shield", "Divine Shield"
	name_CN = "转校生"


class TransferStudent_Stranglethorn(Minion):
	Class, race, name = "Neutral", "", "Transfer Student"
	mana, attack, health = 2, 2, 2
	index = "SCHOLOMANCE~Neutral~Minion~2~2~2~~Transfer Student~Stranglethorn~Stealth~Poisonous"
	requireTarget, keyWord, description = False, "Stealth,Poisonous", "Stealth, Poisonous"
	name_CN = "转校生"


class TransferStudent_FourWindValley(Minion):
	Class, race, name = "Neutral", "", "Transfer Student"
	mana, attack, health = 2, 2, 2
	index = "SCHOLOMANCE~Neutral~Minion~2~2~2~~Transfer Student~Pandaria~Battlecry"
	requireTarget, keyWord, description = True, "", "Battlecry: Give a friendly minion +1/+2"
	name_CN = "转校生"
	
	def targetExists(self, choice=0):
		return self.selectableFriendlyMinionExists(choice)
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.ID == self.ID and target != self and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			target.buffDebuff(1, 2)
		return target

class TransferStudent_Shadows(Minion):
	Class, race, name = "Neutral", "", "Transfer Student"
	mana, attack, health = 2, 2, 2
	index = "SCHOLOMANCE~Neutral~Minion~2~2~2~~Transfer Student~Shadows~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Add a Lackey to your hand"
	name_CN = "转校生"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.addCardtoHand(npchoice(Lackeys), self.ID)
		return None
		
class TransferStudent_UldumDesert(Minion):
	Class, race, name = "Neutral", "", "Transfer Student"
	mana, attack, health = 2, 2, 2
	index = "SCHOLOMANCE~Neutral~Minion~2~2~2~~Transfer Student~Uldum~Reborn"
	requireTarget, keyWord, description = False, "Reborn", "Reborn"
	name_CN = "转校生"


class TransferStudent_UldumOasis(Minion):
	Class, race, name = "Neutral", "", "Transfer Student"
	mana, attack, health = 2, 2, 2
	index = "SCHOLOMANCE~Neutral~Minion~2~2~2~~Transfer Student~Uldum~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Add a Uldum plague card to your hand"
	name_CN = "转校生"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.addCardtoHand(npchoice((PlagueofDeath, PlagueofMadness, PlagueofMurlocs, PlagueofFlames, PlagueofWrath)), self.ID)
		return None
		
class TransferStudent_Dragons(Minion):
	Class, race, name = "Neutral", "", "Transfer Student"
	mana, attack, health = 2, 2, 2
	index = "SCHOLOMANCE~Neutral~Minion~2~2~2~~Transfer Student~Dragons~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Discover a Dragon"
	name_CN = "转校生"
	poolIdentifier = "Dragons as Druid"
	@classmethod
	def generatePool(cls, pools):
		classCards = {s: [] for s in pools.ClassesandNeutral}
		for card in pools.MinionswithRace["Dragon"]:
			for Class in card.Class.split(','):
				classCards[Class].append(card)
		return ["Dragons as " + Class for Class in pools.Classes], \
			   [classCards[Class] + classCards["Neutral"] for Class in pools.Classes]
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if self.ID == curGame.turn:
			if curGame.mode == 0:
				pool = tuple(self.rngPool("Dragons as "+classforDiscover(self)))
				if curGame.guides:
					self.addCardtoHand(curGame.guides.pop(0), self.ID, byDiscover=True)
				else:
					if "byOthers" in comment:
						self.addCardtoHand(npchoice(pool), self.ID, byDiscover=True)
					else:
						dragons = npchoice(pool, 3, replace=False)
						curGame.options = [dragon(curGame, self.ID) for dragon in dragons]
						curGame.Discover.startDiscover(self, pool)
		return None
		
	def discoverDecided(self, option, pool):
		self.Game.fixedGuides.append(type(option))
		self.addCardtoHand(option, self.ID, byDiscover=True)
		
class TransferStudent_Outlands(Minion_Dormantfor2turns):
	Class, race, name = "Neutral", "", "Transfer Student"
	mana, attack, health = 2, 2, 2
	index = "SCHOLOMANCE~Neutral~Minion~2~2~2~~Transfer Student~Outlands"
	requireTarget, keyWord, description = False, "", "Dormant for 2 turns. When this awakens, deal 3 damage to 2 random enemy minions"
	name_CN = "转校生"
	
	def awakenEffect(self):
		minions = self.Game.minionsAlive(3-self.ID)
		if minions:
			self.dealsAOE(npchoice(minions, min(len(minions), 2), replace=False), [3] * len(minions))
			
			
class TransferStudent_Academy(Minion):
	Class, race, name = "Neutral", "", "Transfer Student"
	mana, attack, health = 2, 2, 2
	index = "SCHOLOMANCE~Neutral~Minion~2~2~2~~Transfer Student~Academy~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Add a random Dual Class card to your hand"
	name_CN = "转校生"
	poolIdentifier = "Dual Class Cards"
	@classmethod
	def generatePool(cls, pools):
		cards = []
		for Class in pools.Classes:
			cards += [card for card in pools.ClassCards[Class] if "," in card.Class]
		return "Dual Class Cards", cards
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.addCardtoHand(np.choice(self.rngPool("Dual Class Cards")), self.ID)
		return None
		
class TransferStudent_Darkmoon(Minion):
	Class, race, name = "Neutral", "", "Transfer Student"
	mana, attack, health = 2, 2, 2
	index = "SCHOLOMANCE~Neutral~Minion~2~2~2~~Transfer Student~Darkmoon~ToCorrupt"
	requireTarget, keyWord, description = False, "", "Corrupt: Gain +2/+2"
	name_CN = "转校生"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsHand = [Trig_Corrupt(self, TransferStudent_Darkmoon_Corrupt)] #只有在手牌中才会升级
		
class TransferStudent_Darkmoon_Corrupt(Minion):
	Class, race, name = "Neutral", "", "Transfer Student"
	mana, attack, health = 2, 4, 4
	index = "SCHOLOMANCE~Neutral~Minion~2~4~4~~Transfer Student~Darkmoon~Corrupted~Uncollectible"
	requireTarget, keyWord, description = False, "", ""
	name_CN = "转校生"


transferStudentPool = {"1 Classic Ogrimmar": TransferStudent_Ogrimmar,
						"2 Classic Stormwind": TransferStudent_Stormwind,
						"3 Classic Stranglethorn": TransferStudent_Stranglethorn,
						"4 Classic Four Wind Valley": TransferStudent_FourWindValley,
						#"5 Naxxramas": TransferStudent_Naxxramas,
						#"6 Goblins vs Gnomes": TransferStudent_GvG,
						#"7 Black Rock Mountain": TransferStudent_BlackRockM,
						#"8 The Grand Tournament": TransferStudent_Tournament,
						#"9 League of Explorers Museum": TransferStudent_LOEMuseum,
						#"10 League of Explorers Ruins": TransferStudent_LOERuins,
						#"11 Corrupted Stormwind": TransferStudent_OldGods,
						#"12 Karazhan": TransferStudent_Karazhan,
						#"13 Gadgetzan": TransferStudent_Gadgetzan,
						#"14 Un'Goro": TransferStudent_UnGoro,
						#"15 Frozen Throne": TransferStudent_FrozenThrone,
						#"16 Kobolds": TransferStudent_Kobold,
						#"17 Witchwood": TransferStudent_Witchwood,
						#"18 Boomsday Lab": TransferStudent_Boomsday,
						#"19 Rumble": TransferStudent_Rumble,
						#"20 Dalaran": TransferStudent_Shadows,
						#"21 Uldum Desert": TransferStudent_UldumDesert,
						#"22 Uldum Oasis": TransferStudent_UldumOasis,
						#"23 Dragons": TransferStudent_Dragons,
						"24 Outlands": TransferStudent_Outlands,
						"25 Scholomance Academy": TransferStudent_Academy,
						"26 Darkmoon Faire": TransferStudent_Darkmoon,
						}
"""Mana 0 cards"""
class DeskImp(Minion):
	Class, race, name = "Neutral", "Demon", "Desk Imp"
	mana, attack, health = 0, 1, 1
	index = "SCHOLOMANCE~Neutral~Minion~0~1~1~Demon~Desk Imp"
	requireTarget, keyWord, description = False, "", ""
	name_CN = "课桌小鬼"
	
"""Mana 1 cards"""
class AnimatedBroomstick(Minion):
	Class, race, name = "Neutral", "", "Animated Broomstick"
	mana, attack, health = 1, 1, 1
	index = "SCHOLOMANCE~Neutral~Minion~1~1~1~~Animated Broomstick~Rush~Battlecry"
	requireTarget, keyWord, description = False, "Rush", "Rush. Battlecry: Give your other minions Rush"
	name_CN = "活化扫帚"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		for minion in self.Game.minionsonBoard(self.ID, self):
			minion.getsStatus("Rush")
		return None
		
		
class IntrepidInitiate(Minion):
	Class, race, name = "Neutral", "", "Intrepid Initiate"
	mana, attack, health = 1, 1, 2
	index = "SCHOLOMANCE~Neutral~Minion~1~1~2~~Intrepid Initiate~Battlecry"
	requireTarget, keyWord, description = False, "", "Spellburst: Gain +2 Attack"
	name_CN = "新生刺头"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_IntrepidInitiate(self)]
		
class Trig_IntrepidInitiate(Spellburst):
	def text(self, CHN):
		return "法术迸发：获得+2攻击力" if CHN else "Spellburst: Gain +2 Attack"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.buffDebuff(2, 0)
		
		
class PenFlinger(Minion):
	Class, race, name = "Neutral", "", "Pen Flinger"
	mana, attack, health = 1, 1, 1
	index = "SCHOLOMANCE~Neutral~Minion~1~1~1~~Pen Flinger~Battlecry"
	requireTarget, keyWord, description = True, "", "Battlecry: Deal 1 damage. Spellburst: Return this to your hand"
	name_CN = "甩笔侏儒"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_PenFlinger(self)]
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			self.dealsDamage(target, 1)
		return target
		
class Trig_PenFlinger(Spellburst):
	def text(self, CHN):
		return "将该随从移回你的手牌" if CHN else "Spellburst: Return this to your hand"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.Game.returnMiniontoHand(self.entity, deathrattlesStayArmed=False)
		
		
class SphereofSapience(Weapon):
	Class, name, description = "Neutral", "Sphere of Sapience", "At the start of your turn, look at your top card. You can put it on the bottom and lose 1 Durability"
	mana, attack, durability = 1, 0, 4
	index = "SCHOLOMANCE~Neutral~Weapon~1~0~4~Sphere of Sapience~Neutral~Legendary"
	name_CN = "感知宝珠"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_SphereofSapience(self)]
		
	def discoverDecided(self, option, pool):
		if isinstance(option, NewFate):
			self.Game.fixedGuides.append(True)
			ownDeck = self.Game.Hand_Deck.decks[self.ID]
			ownDeck.insert(0, ownDeck.pop())
			self.loseDurability()
		else:
			self.Game.fixedGuides.append(False)
			
class Trig_SphereofSapience(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["TurnStarts"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return ID == self.entity.ID and self.entity.onBoard and self.entity.durability > 0
		
	def text(self, CHN):
		return "在你的回合开始时，检视你牌库顶的卡牌。你可以将其置于牌库底，并失去1点耐久度" if CHN \
				else "At the start of your turn, look at your top card. You can put it on the bottom and lose 1 Durability"
				
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		curGame = self.entity.Game
		ownDeck = curGame.Hand_Deck.decks[self.entity.ID]
		if curGame.mode == 0:
			if curGame.guides:
				drawNewCard = curGame.guides.pop(0)
				if drawNewCard:
					ownDeck.insert(0, ownDeck.pop())
					self.entity.loseDurability()
			else:
				if curGame.Hand_Deck.decks[self.entity.ID]:
					curGame.options = [ownDeck[-1], NewFate()]
					curGame.Discover.startDiscover(self.entity)
				else: curGame.fixedGuides.append(False)
				
class NewFate:
	def __init__(self):
		self.name = "New Fate"
		self.description = "Draw a new card"
		
		
class TourGuide(Minion):
	Class, race, name = "Neutral", "", "Tour Guide"
	mana, attack, health = 1, 1, 1
	index = "SCHOLOMANCE~Neutral~Minion~1~1~1~~Tour Guide~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Your next Hero Power costs (0)"
	name_CN = "巡游向导"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		tempAura = GameManaAura_NextHeroPower0(self.Game, self.ID)
		self.Game.Manas.PowerAuras.append(tempAura)
		tempAura.auraAppears()
		return None
		
class GameManaAura_NextHeroPower0(TempManaEffect_Power):
	def __init__(self, Game, ID, changeby=0, changeto=-1):
		super().__init__(Game, ID, 0, 0)
		self.temporary = False
		
	def applicable(self, target):
		return target.ID == self.ID
		
"""Mana 2 Cards"""
class CultNeophyte(Minion):
	Class, race, name = "Neutral", "", "Cult Neophyte"
	mana, attack, health = 2, 3, 2
	index = "SCHOLOMANCE~Neutral~Minion~2~3~2~~Cult Neophyte~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Your opponent's spells cost (1) more next turn"
	name_CN = "异教低阶牧师"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.Game.Manas.CardAuras_Backup.append(GameManaAura_InTurnSpell1More(self.Game, 3-self.ID))
		return None
		
class GameManaAura_InTurnSpell1More(TempManaEffect):
	def __init__(self, Game, ID, changeby=0, changeto=-1):
		super().__init__(Game, ID, +1, -1)
		self.signals = ["CardEntersHand"]
		
	def applicable(self, target):
		return target.ID == self.ID and target.type == "Spell"
		
		
class ManafeederPanthara(Minion):
	Class, race, name = "Neutral", "Beast", "Manafeeder Panthara"
	mana, attack, health = 2, 2, 3
	index = "SCHOLOMANCE~Neutral~Minion~2~2~3~Beast~Manafeeder Panthara~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: If you've used your Hero Power this turn, draw a card"
	name_CN = "食魔影豹"
	
	def effCanTrig(self):
		self.effectViable = self.Game.Counters.powerUsedThisTurn > 0
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if self.Game.Counters.powerUsedThisTurn > 0:
			self.Game.Hand_Deck.drawCard(self.ID)
		return None
		
		
class SneakyDelinquent(Minion):
	Class, race, name = "Neutral", "", "Sneaky Delinquent"
	mana, attack, health = 2, 3, 1
	index = "SCHOLOMANCE~Neutral~Minion~2~3~1~~Sneaky Delinquent~Stealth~Deathrattle"
	requireTarget, keyWord, description = False, "Stealth", "Stealth. Deathrattle: Add a 3/1 Ghost with Stealth to your hand"
	name_CN = "少年惯偷"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.deathrattles = [AddaSpectralDelinquent2YourHand(self)]
		
class AddaSpectralDelinquent2YourHand(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.addCardtoHand(SpectralDelinquent, self.entity.ID)
		
	def text(self, CHN):
		return "亡语：将一个3/1并具有潜行的幽灵置入你的手牌" if CHN else "Deathrattle: Add a 3/1 Ghost with Stealth to your hand"
		
class SpectralDelinquent(Minion):
	Class, race, name = "Neutral", "", "Spectral Delinquent"
	mana, attack, health = 2, 3, 1
	index = "SCHOLOMANCE~Neutral~Minion~2~3~1~~Spectral Delinquent~Stealth~Uncollectible"
	requireTarget, keyWord, description = False, "Stealth", "Stealth"
	name_CN = "鬼灵惯偷"
	
	
class VoraciousReader(Minion):
	Class, race, name = "Neutral", "", "Voracious Reader"
	mana, attack, health = 3, 1, 3
	index = "SCHOLOMANCE~Neutral~Minion~3~1~3~~Voracious Reader"
	requireTarget, keyWord, description = False, "", "At the end of your turn, draw until you have 3 cards"
	name_CN = "贪婪的书虫"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_VoraciousReader(self)]
		
#不知道疲劳的时候是否会一直抽牌，假设不会
class Trig_VoraciousReader(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["TurnEnds"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and ID == self.entity.ID
		
	def text(self, CHN):
		return "在你的回合结束时，抽若干牌，直至手牌数量达到3张" if CHN else "At the end of your turn, draw until you have 3 cards"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		HD = self.entity.Game.Hand_Deck
		while len(HD.hands[self.entity.ID]) < 3:
			if HD.drawCard(self.entity.ID)[0] is None: #假设疲劳1次的时候会停止抽牌
				break
				
				
class Wandmaker(Minion):
	Class, race, name = "Neutral", "", "Wandmaker"
	mana, attack, health = 2, 2, 2
	index = "SCHOLOMANCE~Neutral~Minion~2~2~2~~Wandmaker~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Add a 1-Cost spell from your class to your hand"
	name_CN = "魔杖工匠"
	poolIdentifier = "1-Cost Spells as Druid"
	@classmethod
	def generatePool(cls, pools):
		return ["1-Cost Spells as %s"%Class for Class in pools.Classes], \
				[[card for card in pools.ClassCards[Class] if card.type == "Spell" and card.mana == 1] for Class in pools.Classes]
				
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.addCardtoHand(npchoice(self.rngPool("1-Cost Spells as "+self.Game.heroes[self.ID].Class)), self.ID)
		return None
		
		
"""Mana 3 Cards"""
class EducatedElekk(Minion):
	Class, race, name = "Neutral", "Beast", "Educated Elekk"
	mana, attack, health = 3, 3, 4
	index = "SCHOLOMANCE~Neutral~Minion~3~3~4~Beast~Educated Elekk~Deathrattle"
	requireTarget, keyWord, description = False, "", "Whenever a spell is played, this minion remembers it. Deathrattle: Shuffle the spells into your deck"
	name_CN = "驯化的雷象"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_EducatedElekk(self)]
		self.deathrattles = [ShuffleRememberedSpells(self)]
		
class Trig_EducatedElekk(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["SpellPlayed"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard
		
	def text(self, CHN):
		return "每当双方玩家使用一张法术牌，该随从会记住它" if CHN else "Whenever a player plays a spell, this minion remembers it"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		minion = self.entity
		for trig in self.entity.deathrattles:
			if isinstance(trig, ShuffleRememberedSpells):
				trig.spellsRemembered.append(type(subject))
				
class ShuffleRememberedSpells(Deathrattle_Minion):
	def __init__(self, entity):
		super().__init__(entity)
		self.spellsRemembered = []
		
	def text(self, CHN):
		return "亡语：将记住的法术牌洗入你的牌库" if CHN else "Deathrattle: Shuffle remembered spells into your deck"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		minion = self.entity
		spells = [spell(minion.Game, minion.ID) for spell in self.spellsRemembered]
		minion.Game.Hand_Deck.shuffleintoDeck(spells, creator=minion)
		
	def selfCopy(self, recipient):
		trig = type(self)(recipient)
		trig.spellsRemembered = self.spellsRemembered[:]
		return trig
		
		
class EnchantedCauldron(Minion):
	Class, race, name = "Neutral", "", "Enchanted Cauldron"
	mana, attack, health = 3, 1, 6
	index = "SCHOLOMANCE~Neutral~Minion~3~1~6~~Enchanted Cauldron"
	requireTarget, keyWord, description = False, "", "Spellburst: Cast a random spell of the same Cost"
	name_CN = "魔化大锅"
	poolIdentifier = "0-Cost Spells"
	@classmethod
	def generatePool(cls, pools):
		spells = {}
		for Class in pools.Classes:
			for card in pools.ClassCards[Class]:
				if card.type == "Spell":
					try: spells[card.mana].append(card)
					except: spells[card.mana] = [card]
		return ["%d-Cost Spells"%cost for cost in spells.keys()], list(spells.values())
		
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_EnchantedCauldron(self)]
		
class Trig_EnchantedCauldron(Spellburst):
	def text(self, CHN):
		return "法术迸发：随机施放一个法力值消耗相同的法术" if CHN else "Spellburst: Cast a random spell of the same Cost"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		try: spell = npchoice(self.rngPool("%d-Cost Spells"%number))
		except: spell = None
		if spell: spell(self.entity.Game, self.entity.ID).cast()
		
		
class RobesofProtection(Minion):
	Class, race, name = "Neutral", "", "Robes of Protection"
	mana, attack, health = 3, 2, 4
	index = "SCHOLOMANCE~Neutral~Minion~3~2~4~~Robes of Protection"
	requireTarget, keyWord, description = False, "", "Your minions have 'Can't be targeted by spells or Hero Powers'"
	name_CN = "防护长袍"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.auras["Your minions have 'Can't be targeted by spells or Hero Powers'"] = EffectAura(self, "Evasive")
		
	def applicable(self, target):
		return True
		
"""Mana 4 Cards"""
class CrimsonHothead(Minion):
	Class, race, name = "Neutral", "Dragon", "Crimson Hothead"
	mana, attack, health = 4, 3, 6
	index = "SCHOLOMANCE~Neutral~Minion~4~3~6~Dragon~Crimson Hothead"
	requireTarget, keyWord, description = False, "", "Spellburst: Gain +1 Attack and Taunt"
	name_CN = "赤红急先锋"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_CrimsonHothead(self)]
		
class Trig_CrimsonHothead(Spellburst):
	def text(self, CHN):
		return "法术迸发：获得+1攻击力和嘲讽" if CHN else "Spellburst: Gain +1 Attack and Taunt"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.buffDebuff(1, 0)
		self.entity.getsStatus("Taunt")
		
		
class DivineRager(Minion):
	Class, race, name = "Neutral", "Elemental", "Divine Rager"
	mana, attack, health = 4, 5, 1
	index = "SCHOLOMANCE~Neutral~Minion~4~5~1~Elemental~Divine Rager~Divine Shield"
	requireTarget, keyWord, description = False, "Divine Shield", "Divine Shield"
	name_CN = "神圣暴怒者"
	
	
class FishyFlyer(Minion):
	Class, race, name = "Neutral", "Murloc", "Fishy Flyer"
	mana, attack, health = 4, 4, 3
	index = "SCHOLOMANCE~Neutral~Minion~4~4~3~Murloc~Fishy Flyer~Rush~Deathrattle"
	requireTarget, keyWord, description = False, "Rush", "Rush. Deathrattle: Add a 4/3 Ghost with Rush to your hand"
	name_CN = "鱼人飞骑"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.deathrattles = [AddaSpectralFlyer2YourHand(self)]
		
class AddaSpectralFlyer2YourHand(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.addCardtoHand(SpectralFlyer, self.entity.ID)
		
	def text(self, CHN):
		return "亡语：将一个4/3并具有突袭的幽灵置入你的手牌" if CHN else "Deathrattle: Add a 4/3 Ghost with Rush to your hand"
		
class SpectralFlyer(Minion):
	Class, race, name = "Neutral", "Murloc", "Spectral Flyer"
	mana, attack, health = 4, 4, 3
	index = "SCHOLOMANCE~Neutral~Minion~4~4~3~Murloc~Spectral Flyer~Rush~Uncollectible"
	requireTarget, keyWord, description = False, "Rush", "Rush"
	name_CN = "鬼灵飞骑"
	
	
class LorekeeperPolkelt(Minion):
	Class, race, name = "Neutral", "", "Lorekeeper Polkelt"
	mana, attack, health = 5, 4, 5
	index = "SCHOLOMANCE~Neutral~Minion~5~4~5~~Lorekeeper Polkelt~Battlecry~Legendary"
	requireTarget, keyWord, description = False, "", "Battlecry: Reorder your deck from the highest Cost card to the lowest Cost card"
	name_CN = "博学者普克尔特"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		cardDict = {}
		for card in self.Game.Hand_Deck.decks[self.ID]:
			try: cardDict[type(card).mana].append(card)
			except: cardDict[type(card).mana] = [card]
		self.Game.Hand_Deck.decks[self.ID] = [] #After sorting using np, the 1st mana is the lowest
		for mana in np.sort(list(cardDict.keys())): #Doesn't reorder the card of same Cost
			self.Game.Hand_Deck.decks[self.ID] += cardDict[mana]
		return None
		
		
class WretchedTutor(Minion):
	Class, race, name = "Neutral", "", "Wretched Tutor"
	mana, attack, health = 4, 2, 5
	index = "SCHOLOMANCE~Neutral~Minion~4~2~5~~Wretched Tutor"
	requireTarget, keyWord, description = False, "", "Spellburst: Deal 2 damage to all other minions"
	name_CN = "失心辅导员"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_WretchedTutor(self)]
		
#可以通过宣传牌确认是施放法术之后触发
class Trig_WretchedTutor(Spellburst):
	def text(self, CHN):
		return "法术迸发：对所有其他随从造成2点伤害" if CHN else "Spellburst: Deal 2 damage to all other minions"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		minion = self.entity
		targets = minion.Game.minionsonBoard(minion.ID, minion) + minion.Game.minionsonBoard(3-minion.ID)
		minion.dealsAOE(targets, [2 for minion in targets])
		
		
"""Mana 5 Cards"""
class HeadmasterKelThuzad(Minion):
	Class, race, name = "Neutral", "", "Headmaster Kel'Thuzad"
	mana, attack, health = 5, 4, 6
	index = "SCHOLOMANCE~Neutral~Minion~5~4~6~~Headmaster Kel'Thuzad~Legendary"
	requireTarget, keyWord, description = False, "", "Spellburst: If the spell destroys any minions, summon them"
	name_CN = "校长克尔苏加德"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_HeadmasterKelThuzad(self)]
		
#假设检测方式是在一张法术打出时开始记录直到可以触发法术迸发之前的两次死亡结算中所有死亡随从
class Trig_HeadmasterKelThuzad(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["SpellPlayed", "SpellBeenPlayed", "MinionDied"])
		self.minionsKilled = []
		self.enabled = False
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		if signal == "MinionDied": return self.enabled
		else: return self.entity.onBoard and subject.ID == self.entity.ID
		
	def text(self, CHN):
		return "法术迸发：如果法术消灭了任何随从，召唤被消灭的随从" if CHN \
				else "Spellburst: If the spell destroys any minions, summon them"
				
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		if signal == "SpellPlayed": self.enabled = True
		elif signal == "MinionDied": self.minionsKilled.append(type(target))
		else:
			self.disconnect()
			try: self.entity.trigsBoard.remove(self)
			except: pass
			minion = self.entity
			if self.minionsKilled:
				minion.summon([minionKilled(minion.Game, minion.ID) for minionKilled in self.minionsKilled], (minion.pos, "totheRight"))
				
			
class LakeThresher(Minion):
	Class, race, name = "Neutral", "Beast", "Lake Thresher"
	mana, attack, health = 5, 4, 6
	index = "SCHOLOMANCE~Neutral~Minion~5~4~6~Beast~Lake Thresher"
	requireTarget, keyWord, description = False, "", "Also damages the minions next to whomever this attacks"
	name_CN = "止水湖蛇颈龙"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.marks["Sweep"] = 1
		
		
class Ogremancer(Minion):
	Class, race, name = "Neutral", "", "Ogremancer"
	mana, attack, health = 5, 3, 7
	index = "SCHOLOMANCE~Neutral~Minion~5~3~7~~Ogremancer"
	requireTarget, keyWord, description = False, "", "Whenever your opponent casts a spell, summon a 2/2 Skeleton with Taunt"
	name_CN = "食人魔巫术师"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_Ogremancer(self)]
		
class Trig_Ogremancer(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["SpellPlayed"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject.ID != self.entity.ID
		
	def text(self, CHN):
		return "每当你的对手施放一个法术，召唤一个2/2并具有嘲讽的骷髅" if CHN \
				else "Whenever your opponent casts a spell, summon a 2/2 Skeleton with Taunt"
				
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.summon(RisenSkeleton(self.entity.Game, self.entity.ID), self.entity.pos+1)
		
class RisenSkeleton(Minion):
	Class, race, name = "Neutral", "", "Risen Skeleton"
	mana, attack, health = 2, 2, 2
	index = "SCHOLOMANCE~Neutral~Minion~2~2~2~~Risen Skeleton~Taunt~Uncollectible"
	requireTarget, keyWord, description = False, "Taunt", "Taunt"
	name_CN = "复活的骷髅"
	
	
class StewardofScrolls(Minion):
	Class, race, name = "Neutral", "Elemental", "Steward of Scrolls"
	mana, attack, health = 5, 4, 4
	index = "SCHOLOMANCE~Neutral~Minion~5~4~4~Elemental~Steward of Scrolls~Spell Damage~Battlecry"
	requireTarget, keyWord, description = False, "Spell Damage", "Spell Damage +1. Battlecry: Discover a spell"
	name_CN = "卷轴管理者"
	poolIdentifier = "Demon Hunter Spells"
	@classmethod
	def generatePool(cls, pools):
		return [Class+" Spells" for Class in pools.Classes], \
				[[card for card in pools.ClassCards[Class] if card.type == "Spell"] for Class in pools.Classes]
				
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if self.ID == curGame.turn:
			if curGame.mode == 0:
				pool = tuple(self.rngPool(classforDiscover(self)+" Spells"))
				if curGame.guides:
					self.addCardtoHand(curGame.guides.pop(0), self.ID, byDiscover=True)
				else:
					if "byOthers" in comment:
						self.addCardtoHand(npchoice(pool), self.ID, byDiscover=True)
					else:
						spells = npchoice(pool, 3, replace=False)
						curGame.options = [spell(curGame, self.ID) for spell in spells]
						curGame.Discover.startDiscover(self, pool)
		return target
		
	def discoverDecided(self, option, pool):
		self.Game.fixedGuides.append(type(option))
		self.addCardtoHand(option, self.ID, byDiscover=True)
		
		
class Vectus(Minion):
	Class, race, name = "Neutral", "", "Vectus"
	mana, attack, health = 5, 4, 4
	index = "SCHOLOMANCE~Neutral~Minion~5~4~4~~Vectus~Battlecry~Legendary"
	requireTarget, keyWord, description = False, "", "Battlecry: Summon two 1/1 Whelps. Each gains a Deathrattle from your minions that died this game"
	name_CN = "维克图斯"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		minions = [card for card in self.Game.Counters.minionsDiedThisGame[self.ID] if "~Deathrattle" in card.index]
		minions = [npchoice(minions), npchoice(minions)] if minions else [None, None]
		whelps = [PlaguedHatchling(self.Game, self.ID) for i in range(2)]
		pos = (self.pos, "leftandRight") if self.onBoard else (-1, "totheRightEnd")
		self.summon(whelps, pos)
		for minion, whelp in zip(minions, whelps):
			if minion and whelp.onBoard:
				for trig in minion(self.Game, self.ID).deathrattles:
					whelp.getsTrig(type(trig)(whelp), trigType="Deathrattle")
			else: break
		return None
		
class PlaguedHatchling(Minion):
	Class, race, name = "Neutral", "Dragon", "Plagued Hatchling"
	mana, attack, health = 1, 1, 1
	index = "SCHOLOMANCE~Neutral~Minion~1~1~1~Dragon~Plagued Hatchling~Uncollectible"
	requireTarget, keyWord, description = False, "", ""
	name_CN = "魔药龙崽"
	
	
"""Mana 6 Cards"""
class OnyxMagescribe(Minion):
	Class, race, name = "Neutral", "Dragon", "Onyx Magescribe"
	mana, attack, health = 6, 4, 9
	index = "SCHOLOMANCE~Neutral~Minion~6~4~9~Dragon~Onyx Magescribe"
	requireTarget, keyWord, description = False, "", "Spellburst: Add 2 random spells from your class to your hand"
	name_CN = "黑岩法术抄写员"
	poolIdentifier = "Druid Spells"
	@classmethod
	def generatePool(cls, pools):
		return [Class + " Spells" for Class in pools.Classes], \
			   [[card for card in pools.ClassCards[Class] if card.type == "Spell"] for Class in pools.Classes]
	
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_OnyxMagescribe(self)]
		
class Trig_OnyxMagescribe(Spellburst):
	def text(self, CHN):
		return "法术迸发：随机将两张你职业的法术牌置入你的手牌" if CHN \
				else "Spellburst: Add 2 random spells from your class to your hand"
				
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		pool = self.rngPool(self.entity.Game.heroes[self.entity.ID].Class + " Spells")
		self.entity.addCardtoHand(npchoice(pool, 2, replace=True), self.entity.ID)
		
			
class SmugSenior(Minion):
	Class, race, name = "Neutral", "", "Smug Senior"
	mana, attack, health = 6, 5, 7
	index = "SCHOLOMANCE~Neutral~Minion~6~5~7~~Smug Senior~Taunt~Deathrattle"
	requireTarget, keyWord, description = False, "Taunt", "Taunt. Deathrattle: Add a 5/7 Ghost with Taunt to your hand"
	name_CN = "浮夸的大四学长"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.deathrattles = [AddaSpectralSenior2YourHand(self)]
		
class AddaSpectralSenior2YourHand(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.addCardtoHand(SpectralSenior, self.entity.ID)
		
	def text(self, CHN):
		return "亡语：将一个5/7并具有嘲讽的幽灵置入你的手牌" if CHN else "Deathrattle: Add a 5/7 Ghost with Taunt to your hand"
		
class SpectralSenior(Minion):
	Class, race, name = "Neutral", "", "Spectral Senior"
	mana, attack, health = 6, 5, 7
	index = "SCHOLOMANCE~Neutral~Minion~6~5~7~~Spectral Senior~Taunt~Uncollectible"
	requireTarget, keyWord, description = False, "Taunt", "Taunt"
	name_CN = "鬼灵学长"
	
	
class SorcerousSubstitute(Minion):
	Class, race, name = "Neutral", "", "Sorcerous Substitute"
	mana, attack, health = 6, 6, 6
	index = "SCHOLOMANCE~Neutral~Minion~6~6~6~~Sorcerous Substitute~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: If you have Spell Damage, summon a copy of this"
	name_CN = "巫术替身"
	
	def effCanTrig(self):
		self.effectViable =  self.countSpellDamage() > 0
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if self.countSpellDamage() > 0:
			Copy = self.selfCopy(self.ID, self) if self.onBoard else type(self)(self.Game, self.ID)
			self.summon(Copy, self.pos+1)
		return None
		
		
"""Mana 7 cards or higher"""
class KeymasterAlabaster(Minion):
	Class, race, name = "Neutral", "", "Keymaster Alabaster"
	mana, attack, health = 7, 6, 8
	index = "SCHOLOMANCE~Neutral~Minion~7~6~8~~Keymaster Alabaster~Legendary"
	requireTarget, keyWord, description = False, "", "Whenever your opponent draws a card, add a copy to your hand that costs (1)"
	name_CN = "钥匙专家阿拉巴斯特"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_KeymasterAlabaster(self)]
		
class Trig_KeymasterAlabaster(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["CardDrawn"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and target[0].ID != self.entity.ID
		
	def text(self, CHN):
		return "每当你的对手抽一张牌时，将一张复制置入你的手牌，其法力值消耗变为(1)点" if CHN \
				else "Whenever your opponent draws a card, add a copy to your hand that costs (1)"
				
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		Copy = target[0].selfCopy(self.entity.ID, self.entity)
		ManaMod(Copy, changeby=0, changeto=1).applies()
		self.entity.addCardtoHand(Copy, self.entity.ID)
		
		
class PlaguedProtodrake(Minion):
	Class, race, name = "Neutral", "Dragon", "Plagued Protodrake"
	mana, attack, health = 8, 8, 8
	index = "SCHOLOMANCE~Neutral~Minion~8~8~8~Dragon~Plagued Protodrake~Deathrattle"
	requireTarget, keyWord, description = False, "", "Deathrattle: Summon a random 7-Cost minion"
	name_CN = "魔药始祖龙"
	poolIdentifier = "7-Cost Minions to Summon"
	@classmethod
	def generatePool(cls, pools):
		return "7-Cost Minions to Summon", pools.MinionsofCost[7]
		
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.deathrattles = [SummonaRandom7CostMinion(self)]
		
class SummonaRandom7CostMinion(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.summon(npchoice(self.rngPool("7-Cost Minions to Summon"))(self.entity.Game, self.entity.ID), self.entity.pos+1)
			
	def text(self, CHN):
		return "亡语：随机召唤一个法力值消耗为(7)的随从" if CHN else "Deathrattle: Summon a random 7-Cost minion"
		
"""Demon Hunter Cards"""
class DemonCompanion(Spell):
	Class, school, name = "Demon Hunter,Hunter", "", "Demon Companion"
	requireTarget, mana = False, 1
	index = "SCHOLOMANCE~Demon Hunter,Hunter~Spell~1~~Demon Companion"
	description = "Summon a random Demon Companion"
	name_CN = "恶魔伙伴"
	def available(self):
		return self.Game.space(self.ID) > 0
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.summon(npchoice((Reffuh, Kolek, Shima))(self.Game, self.ID), -1)
		return None
		
class Reffuh(Minion):
	Class, race, name = "Demon Hunter,Hunter", "Demon", "Reffuh"
	mana, attack, health = 1, 2, 1
	index = "SCHOLOMANCE~Demon Hunter,Hunter~Minion~1~2~1~Demon~Reffuh~Charge~Uncollectible"
	requireTarget, keyWord, description = False, "Charge", "Charge"
	name_CN = "弗霍"
	
class Kolek(Minion):
	Class, race, name = "Demon Hunter,Hunter", "Demon", "Kolek"
	mana, attack, health = 1, 1, 2
	index = "SCHOLOMANCE~Demon Hunter,Hunter~Minion~1~1~2~Demon~Kolek~Uncollectible"
	requireTarget, keyWord, description = False, "", "Your other minions have +1 Attack"
	name_CN = "克欧雷"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.auras["Your other minions have +1 Attack"] = StatAura_Others(self, 1, 0)
		
class Shima(Minion):
	Class, race, name = "Demon Hunter,Hunter", "Demon", "Shima"
	mana, attack, health = 1, 2, 2
	index = "SCHOLOMANCE~Demon Hunter,Hunter~Minion~1~2~2~Demon~Shima~Taunt~Uncollectible"
	requireTarget, keyWord, description = False, "Taunt", "Taunt"
	name_CN = "莎米"
	
	
class DoubleJump(Spell):
	Class, school, name = "Demon Hunter", "", "Double Jump"
	requireTarget, mana = False, 1
	index = "SCHOLOMANCE~Demon Hunter~Spell~1~~Double Jump"
	description = "Draw an Outcast card from your deck"
	name_CN = "二段跳"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		cards = [i for i, card in enumerate(self.Game.Hand_Deck.decks[self.ID]) if "~Outcast" in card.index]
		if cards: self.Game.Hand_Deck.drawCard(self.ID, npchoice(cards))
		return None
		
		
class TrueaimCrescent(Weapon):
	Class, name, description = "Demon Hunter,Hunter", "Trueaim Crescent", "After your hero attacks a minion, your minions attack it too"
	mana, attack, durability = 1, 1, 4
	index = "SCHOLOMANCE~Demon Hunter,Hunter~Weapon~1~1~4~Trueaim Crescent"
	name_CN = "引月长弓"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_TrueaimCrescent(self)]
		
#即使是被冰冻的随从也可以因为这个效果进行攻击，同时攻击不浪费攻击机会，同时可以触发巨型沙虫等随从的获得额外的攻击机会
class Trig_TrueaimCrescent(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["HeroAttackedMinion"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		#The target can't be dying to trigger this
		return subject.ID == self.entity.ID and self.entity.onBoard and not target.dead and target.health > 0
		
	def text(self, CHN):
		return "在你的英雄攻击一个随从后，你的所有随从也会攻击该随从" if CHN \
				else "After your hero attacks a minion, your minions attack it too"
				
	#随从的攻击顺序与它们的登场顺序一致
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		game = self.entity.Game
		minions = game.sortSeq(game.minionsAlive(self.entity.ID))[0]
		for minion in minions:
			if target.onBoard and target.health > 0 and not target.dead:
				game.battle(minion, target, verifySelectable=False, useAttChance=False, resolveDeath=False, resetRedirTrig=True)
				
				
class AceHunterKreen(Minion):
	Class, race, name = "Demon Hunter,Hunter", "", "Ace Hunter Kreen"
	mana, attack, health = 3, 2, 4
	index = "SCHOLOMANCE~Demon Hunter,Hunter~Minion~3~2~4~~Ace Hunter Kreen~Legendary"
	requireTarget, keyWord, description = False, "", "Your other characters are Immune while attacking"
	name_CN = "金牌猎手克里"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_AceHunterKreen(self)]
		
class Trig_AceHunterKreen(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["BattleStarted", "BattleFinished"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject.ID == self.entity.ID and subject != self.entity and self.entity.onBoard
		
	def text(self, CHN):
		return "你的其他角色在攻击时具有免疫" if CHN else "Your other characters are Immune while attacking"
		
	#不知道攻击具有受伤时召唤一个随从的扳机的随从时，飞刀能否对这个友方角色造成伤害
	#目前的写法是这个战斗结束信号触发在受伤之后
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		if signal == "BattleStarted": subject.getsStatus("Immune")
		else: subject.losesStatus("Immune")
		
class Magehunter(Minion):
	Class, race, name = "Demon Hunter", "", "Magehunter"
	mana, attack, health = 3, 2, 3
	index = "SCHOLOMANCE~Demon Hunter~Minion~3~2~3~~Magehunter~Rush"
	requireTarget, keyWord, description = False, "Rush", "Rush. Whenever this attacks a minion, Silence it"
	name_CN = "法师猎手"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_Magehunter(self)]
		
class Trig_Magehunter(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["MinionAttackingMinion"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject == self.entity and self.entity.onBoard
		
	def text(self, CHN):
		return "每当该随从攻击一个随从时，将其沉默" if CHN else "Whenever this attacks a minion, Silence it"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		target.getsSilenced()
		
		
class ShardshatterMystic(Minion):
	Class, race, name = "Demon Hunter", "", "Shardshatter Mystic"
	mana, attack, health = 4, 3, 2
	index = "SCHOLOMANCE~Demon Hunter~Minion~4~3~2~~Shardshatter Mystic~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Destroy a Soul Fragment in your deck to deal 3 damage to all other minions"
	name_CN = "残片震爆秘术师"
	
	def effCanTrig(self):
		self.effectViable = False
		for card in self.Game.Hand_Deck.decks[self.ID]:
			if isinstance(card, SoulFragment):
				self.effectViable = True
				break
				
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		for i, card in enumerate(self.Game.Hand_Deck.decks[self.ID]):
			if isinstance(card, SoulFragment):
				self.Game.Hand_Deck.extractfromDeck(i, self.ID)
				minions = self.Game.minionsonBoard(self.ID, self) + self.Game.minionsonBoard(3-self.ID)
				self.dealsAOE(minions, [3]*len(minions))
				break
		return None
		
		
class Glide(Spell):
	Class, school, name = "Demon Hunter", "", "Glide"
	requireTarget, mana = False, 4
	index = "SCHOLOMANCE~Demon Hunter~Spell~4~~Glide~Outcast"
	description = "Shuffle your hand into your deck. Draw 4 cards. Outcast: Your opponent does the same"
	name_CN = "滑翔"
	def effCanTrig(self):
		self.effectViable = self.Game.Hand_Deck.outcastcanTrig(self)
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.Game.Hand_Deck.shuffle_Hand2Deck(0, self.ID, initiatorID=self.ID, all=True)
		for i in range(4): self.Game.Hand_Deck.drawCard(self.ID)
		if posinHand == 0 or posinHand == -1:
			self.Game.Hand_Deck.shuffle_Hand2Deck(0, 3-self.ID, initiatorID=self.ID, all=True)
			for i in range(4): self.Game.Hand_Deck.drawCard(3-self.ID)
		return None
		
		
class Marrowslicer(Weapon):
	Class, name, description = "Demon Hunter", "Marrowslicer", "Battlecry: Shuffle 2 Soul Fragments into your deck"
	mana, attack, durability = 4, 4, 2
	index = "SCHOLOMANCE~Demon Hunter~Weapon~4~4~2~Marrowslicer~Battlecry"
	name_CN = "切髓之刃"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.Game.Hand_Deck.shuffleintoDeck([SoulFragment(self.Game, self.ID) for i in range(2)], creator=self)
		return None
		
class SoulFragment(Spell):
	Class, school, name = "Warlock,Demon Hunter", "", "Soul Fragment"
	requireTarget, mana = False, 0
	index = "SCHOLOMANCE~Warlock,Demon Hunter~Spell~0~~Soul Fragment~Casts When Drawn~Uncollectible"
	description = "Restore 2 Health to your hero"
	name_CN = "灵魂残片"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		heal = 2 * (2 ** self.countHealDouble())
		self.restoresHealth(self.Game.heroes[self.ID], heal)
		return None
		
		
class StarStudentStelina(Minion):
	Class, race, name = "Demon Hunter", "", "Star Student Stelina"
	mana, attack, health = 4, 4, 3
	index = "SCHOLOMANCE~Demon Hunter~Minion~4~4~3~~Star Student Stelina~Outcast~Legendary"
	requireTarget, keyWord, description = False, "", "Outcast: Look at 3 cards in your opponent's hand. Shuffle one of them into their deck"
	name_CN = "明星学员斯特里娜"
	
	def effCanTrig(self):
		self.effectViable = self.Game.Hand_Deck.outcastcanTrig(self)
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if posinHand == 0 or posinHand == -1:
			curGame = self.Game
			if curGame.mode == 0:
				if curGame.guides:
					i = curGame.guides.pop(0)
					if i > -1:
						self.Game.Hand_Deck.shuffle_Hand2Deck(i, 3-self.ID, initiatorID=self.ID, all=False)
				else:
					enemyHand = curGame.Hand_Deck.hands[3-self.ID]
					if enemyHand:
						hands = []
						for card in npchoice(enemyHand, min(3, len(enemyHand)), replace=False):
							cardCopy = card.selfCopy(3-self.ID)
							cardCopy.cardinHand = card
							hands.append(cardCopy)
						curGame.options = hands
						curGame.Discover.startDiscover(self)
					else: curGame.fixedGuides.append(-1)
		return None
		
	def discoverDecided(self, option, pool):
		i = self.Game.Hand_Deck.hands[3-self.ID].index(option.cardinHand)
		self.Game.fixedGuides.append(i)
		self.Game.Hand_Deck.shuffle_Hand2Deck(i, 3-self.ID, initiatorID=self.ID, all=False)
		
		
class VilefiendTrainer(Minion):
	Class, race, name = "Demon Hunter", "", "Vilefiend Trainer"
	mana, attack, health = 4, 5, 4
	index = "SCHOLOMANCE~Demon Hunter~Minion~4~5~4~~Vilefiend Trainer~Outcast"
	requireTarget, keyWord, description = False, "", "Outcast: Summon two 1/1 Demons"
	name_CN = "邪犬训练师"
	
	def effCanTrig(self):
		self.effectViable = self.Game.Hand_Deck.outcastcanTrig(self)
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if posinHand == 0 or posinHand == -1:
			pos = (self.pos, "leftandRight") if self.onBoard else (-1, "totheRightEnd")
			self.summon([SnarlingVilefiend(self.Game, self.ID) for i in range(2)], pos)
		return None
		
class SnarlingVilefiend(Minion):
	Class, race, name = "Demon Hunter", "Demon", "Snarling Vilefiend"
	mana, attack, health = 1, 1, 1
	index = "SCHOLOMANCE~Demon Hunter~Minion~1~1~1~Demon~Snarling Vilefiend~Uncollectible"
	requireTarget, keyWord, description = False, "", ""
	name_CN = "咆哮的邪犬"
	
	
class BloodHerald(Minion):
	Class, race, name = "Demon Hunter,Hunter", "", "Blood Herald"
	mana, attack, health = 5, 1, 1
	index = "SCHOLOMANCE~Demon Hunter,Hunter~Minion~5~1~1~~Blood Herald"
	requireTarget, keyWord, description = False, "", "Whenever a friendly minion dies while this is in your hand, gain +1/+1"
	name_CN = "嗜血传令官"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsHand = [Trig_BloodHerald(self)]
		
class Trig_BloodHerald(TrigHand):
	def __init__(self, entity):
		super().__init__(entity, ["MinionDies"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.inHand and target.ID == self.entity.ID
		
	def text(self, CHN):
		return "如果这张牌在你的手牌中，每当一个友方随从死亡，便获得+1/+1" if CHN else "Whenever a friendly minion dies while this is in your hand, gain +1/+1"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.buffDebuff(1, 1)
		
		
class SoulshardLapidary(Minion):
	Class, race, name = "Demon Hunter", "", "Soulshard Lapidary"
	mana, attack, health = 5, 5, 5
	index = "SCHOLOMANCE~Demon Hunter~Minion~5~5~5~~Soulshard Lapidary~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Destroy a Soul Fragment in your deck to give your hero +5 Attack this turn"
	name_CN = "铸魂宝石匠"
	
	def effCanTrig(self):
		self.effectViable = False
		for card in self.Game.Hand_Deck.decks[self.ID]:
			if isinstance(card, SoulFragment):
				self.effectViable = True
				break
				
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		for i, card in enumerate(self.Game.Hand_Deck.decks[self.ID]):
			if isinstance(card, SoulFragment):
				self.Game.Hand_Deck.extractfromDeck(i, self.ID)
				self.Game.heroes[self.ID].gainAttack(5)
				break
		return None
		
		
class CycleofHatred(Spell):
	Class, school, name = "Demon Hunter", "", "Cycle of Hatred"
	requireTarget, mana = False, 7
	index = "SCHOLOMANCE~Demon Hunter~Spell~7~~Cycle of Hatred"
	description = "Deal 3 damage to all minions. Summon a 3/3 Spirit for every minion killed"
	name_CN = "仇恨之轮"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		damage = (3 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		targets = self.Game.minionsonBoard(1) + self.Game.minionsonBoard(2)
		dmgTakers = self.dealsAOE(targets, [damage]*len(targets))[0]
		num = 0
		for dmgTaker in dmgTakers:
			if dmgTaker.dead or dmgTaker.health < 1: num += 1
		if num > 0:
			self.summon([SpiritofVengeance(self.Game, self.ID) for i in range(num)], (-1, "totheRightEnd"))
		return None
		
class SpiritofVengeance(Minion):
	Class, race, name = "Demon Hunter", "", "Spirit of Vengeance"
	mana, attack, health = 3, 3, 3
	index = "SCHOLOMANCE~Demon Hunter~Minion~3~3~3~~Spirit of Vengeance~Uncollectible"
	requireTarget, keyWord, description = False, "", ""
	name_CN = "复仇之魂"
	
	
class FelGuardians(Spell):
	Class, school, name = "Demon Hunter", "Fel", "Fel Guardians"
	requireTarget, mana = False, 7
	index = "SCHOLOMANCE~Demon Hunter~Spell~7~Fel~Fel Guardians"
	description = "Summon three 1/2 Demons with Taunt. Costs (1) less whenever a friendly minion dies"
	name_CN = "邪能护卫"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsHand = [Trig_FelGuardians(self)]
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.summon([SoulfedFelhound(self.Game, self.ID) for i in range(3)], (-1, "totheRightEnd"))
		return None
		
class Trig_FelGuardians(TrigHand):
	def __init__(self, entity):
		super().__init__(entity, ["MinionDies"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.inHand and target.ID == self.entity.ID
		
	def text(self, CHN):
		return "当这张牌在你的手牌中时，每当一个友方随从死亡，法力值消耗便减少(1)点" if CHN else "Costs (1) less whenever a friendly minion dies"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		ManaMod(self.entity, -1, -1).applies()
		
class SoulfedFelhound(Minion):
	Class, race, name = "Demon Hunter", "Demon", "Soulfed Felhound"
	mana, attack, health = 1, 1, 2
	index = "SCHOLOMANCE~Demon Hunter~Minion~1~1~2~Demon~Soulfed Felhound~Taunt~Uncollectible"
	requireTarget, keyWord, description = False, "Taunt", "Taunt"
	name_CN = "食魂地狱犬"
	
	
class AncientVoidHound(Minion):
	Class, race, name = "Demon Hunter", "Demon", "Ancient Void Hound"
	mana, attack, health = 9, 10, 10
	index = "SCHOLOMANCE~Demon Hunter~Minion~9~10~10~Demon~Ancient Void Hound"
	requireTarget, keyWord, description = False, "", "At the end of your turn, steal 1 Attack and Health from all enemy minions"
	name_CN = "上古虚空恶犬"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_AncientVoidHound(self)]
		
class Trig_AncientVoidHound(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["TurnEnds"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return ID == self.entity.ID and self.entity.onBoard
		
	def text(self, CHN):
		return "在你的回合结束时，从所有敌方随从处偷取1点攻击力和生命值" if CHN \
				else "At the end of your turn, steal 1 Attack and Health from all enemy minions"
				
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		enemyMinions = self.entity.Game.minionsonBoard(3-self.entity.ID)
		num = len(enemyMinions)
		for minion in enemyMinions:
			minion.attack -= 1
			minion.health -= 1
			minion.attack_Enchant -= 1
			for func in minion.triggers["StatChanges"]: func()
		if num: self.entity.buffDebuff(num, num)
		
		
"""Druid Cards"""
class LightningBloom(Spell):
	Class, school, name = "Druid,Shaman", "Nature", "Lightning Bloom"
	requireTarget, mana = False, 0
	index = "SCHOLOMANCE~Druid,Shaman~Spell~0~Nature~Lightning Bloom~Overload"
	description = "Gain 2 Mana Crystals this turn only. Overload: (2)"
	name_CN = "雷霆绽放"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.overload = 2
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.Game.Manas.gainTempManaCrystal(2, ID=self.ID)
		return None
		
		
class Gibberling(Minion):
	Class, race, name = "Druid", "", "Gibberling"
	mana, attack, health = 2, 1, 1
	index = "SCHOLOMANCE~Druid~Minion~2~1~1~~Gibberling"
	requireTarget, keyWord, description = False, "", "Spellburst: Summon a Gibberling"
	name_CN = "聒噪怪"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_Gibberling(self)]
		
class Trig_Gibberling(Spellburst):
	def text(self, CHN):
		return "法术迸发：召唤一个聒噪怪" if CHN else "Spellburst: Summon a Gibberling"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		minion = self.entity
		minion.summon(Gibberling(minion.Game, minion.ID), minion.pos+1)
		
		
class NatureStudies(Spell):
	Class, school, name = "Druid", "Nature", "Nature Studies"
	requireTarget, mana = False, 1
	index = "SCHOLOMANCE~Druid~Spell~1~Nature~Nature Studies"
	description = "Discover a spell. Your next one costs (1) less"
	name_CN = "自然研习"
	poolIdentifier = "Druid Spells"
	@classmethod
	def generatePool(cls, pools):
		return [Class + " Spells" for Class in pools.Classes], \
			   [[card for card in pools.ClassCards[Class] if card.type == "Spell"] for Class in pools.Classes]
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if curGame.mode == 0:
			pool = tuple(self.rngPool(classforDiscover(self)+" Spells"))
			if curGame.guides:
				self.addCardtoHand(curGame.guides.pop(0), self.ID, byDiscover=True)
			else:
				if self.ID != curGame.turn or "byOthers" in comment:
					self.addCardtoHand(npchoice(pool), self.ID, byDiscover=True)
				else:
					spells = npchoice(pool, 3, replace=False)
					curGame.options = [spell(curGame, self.ID) for spell in spells]
					curGame.Discover.startDiscover(self, pool)
		tempAura = GameManaAura_NextSpell1Less(self.Game, self.ID)
		self.Game.Manas.CardAuras.append(tempAura)
		tempAura.auraAppears()
		return None
		
	def discoverDecided(self, option, pool):
		self.Game.fixedGuides.append(type(option))
		self.addCardtoHand(option, self.ID, byDiscover=True)
		
class GameManaAura_NextSpell1Less(TempManaEffect):
	def __init__(self, Game, ID, changeby=0, changeto=-1):
		super().__init__(Game, ID, -1, -1)
		self.temporary = False
		
	def applicable(self, target):
		return target.ID == self.ID and target.type == "Spell"
		
	def text(self, CHN):
		return "你的下一张法术牌的法力值消耗减少(1)点" if CHN else "Your next spell costs (1) less"
		
		
class PartnerAssignment(Spell):
	Class, school, name = "Druid", "", "Partner Assignment"
	requireTarget, mana = False, 1
	index = "SCHOLOMANCE~Druid~Spell~1~~Partner Assignment"
	description = "Add a random 2-Cost and 3-Cost Beast to your hand"
	name_CN = "分配组员"
	poolIdentifier = "2-Cost Beasts"
	@classmethod
	def generatePool(cls, pools):
		return ["2-Cost Beasts", "3-Cost Beasts"], \
				[[card for card in pools.MinionswithRace["Beast"] if card.mana == 2],
					[card for card in pools.MinionswithRace["Beast"] if card.mana == 3]]
					
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		beasts = [npchoice(self.rngPool("2-Cost Beasts")), npchoice(self.rngPool("3-Cost Beasts"))]
		self.addCardtoHand(beasts, self.ID)
		return None
		
		
class SpeakerGidra(Minion):
	Class, race, name = "Druid", "", "Speaker Gidra"
	mana, attack, health = 3, 1, 4
	index = "SCHOLOMANCE~Druid~Minion~3~1~4~~Speaker Gidra~Rush~Windfury"
	requireTarget, keyWord, description = False, "Rush,Windfury", "Rush, Windfury. Spellburst: Gain Attack and Health equal to the spell's Cost"
	name_CN = "演讲者吉德拉"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_SpeakerGidra(self)]
		
class Trig_SpeakerGidra(Spellburst):
	def text(self, CHN):
		return "法术迸发：获得等同于法术法力值消耗的攻击力和生命值" if CHN else "Spellburst: Gain Attack and Health equal to the spell's Cost"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.buffDebuff(number, number)
		
		
class Groundskeeper(Minion):
	Class, race, name = "Druid,Shaman", "", "Groundskeeper"
	mana, attack, health = 4, 4, 5
	index = "SCHOLOMANCE~Druid,Shaman~Minion~4~4~5~~Groundskeeper~Taunt~Battlecry"
	requireTarget, keyWord, description = True, "Taunt", "Taunt. Battlecry: If you're holding a spell that costs (5) or more, restore 5 Health"
	name_CN = "园地管理员"
	
	def returnTrue(self, choice=0):
		return self.Game.Hand_Deck.holdingSpellwith5CostorMore(self.ID)
		
	def effCanTrig(self):
		self.effectViable = self.Game.Hand_Deck.holdingSpellwith5CostorMore(self.ID)
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target and self.Game.Hand_Deck.holdingSpellwith5CostorMore(self.ID):
			heal = 5 * (2 ** self.countHealDouble())
			self.restoresHealth(target, heal)
		return target
		
		
class TwilightRunner(Minion):
	Class, race, name = "Druid", "Beast", "Twilight Runner"
	mana, attack, health = 5, 5, 4
	index = "SCHOLOMANCE~Druid~Minion~5~5~4~Beast~Twilight Runner~Stealth"
	requireTarget, keyWord, description = False, "Stealth", "Stealth. Whenever this attacks, draw 2 cards"
	name_CN = "夜行虎"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_TwilightRunner(self)]
		
class Trig_TwilightRunner(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["MinionAttackingMinion", "MinionAttackingHero"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject == self.entity
		
	def text(self, CHN):
		return "每当该随从攻击，抽两张牌" if CHN else "Whenever this attacks, draw 2 cards"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.Game.Hand_Deck.drawCard(self.entity.ID)
		self.entity.Game.Hand_Deck.drawCard(self.entity.ID)
		
		
class ForestWardenOmu(Minion):
	Class, race, name = "Druid", "", "Forest Warden Omu"
	mana, attack, health = 6, 5, 4
	index = "SCHOLOMANCE~Druid~Minion~6~5~4~~Forest Warden Omu~Legendary"
	requireTarget, keyWord, description = False, "", "Spellburst: Refresh your Mana Crystals"
	name_CN = "林地守护者欧穆"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_ForestWardenOmu(self)]
		
class Trig_ForestWardenOmu(Spellburst):
	def text(self, CHN):
		return "法术迸发：复原你的法力水晶" if CHN else "Spellburst: Refresh your Mana Crystals"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.Game.Manas.restoreManaCrystal(0, self.entity.ID, restoreAll=True)
		
		
class RunicCarvings(Spell):
	Class, school, name = "Druid,Shaman", "Nature", "Runic Carvings"
	requireTarget, mana = False, 6
	index = "SCHOLOMANCE~Druid,Shaman~Spell~6~Nature~Runic Carvings~Choose One"
	description = "Choose One - Summon four 2/2 Treant Totems; or Overload: (2) to given them Rush"
	name_CN = "雕琢符文"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.chooseOne = 1
		self.options = [CalltoAid_Option(self), AlarmtheForest_Option(self)]
		
	def available(self):
		return self.Game.space(self.ID) > 0
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		minions = [TreantTotem(self.Game, self.ID) for i in range(4)]
		self.summon(minions, (-1, "totheRightEnd"))
		if choice != 0:
			self.Game.Manas.overloadMana(2, self.ID)
			for minion in minions:
				if minion.onBoard: minion.getsStatus("Rush")
		return None
		
class CalltoAid_Option(Option):
	name, description = "Call to Aid", "Summon four 2/2 Treant Totems"
	index = "SCHOLOMANCE~Druid,Shaman~Spell~6~Nature~Call to Aid~Uncollectible"
	mana, attack, health = 6, -1, -1
	def available(self):
		return self.entity.Game.space(self.entity.ID) > 0
		
class AlarmtheForest_Option(Option):
	name, description = "Alarm the Forest", "Summon four 2/2 Treant Totems with Rush. Overload: (2)"
	index = "SCHOLOMANCE~Druid,Shaman~Spell~6~Nature~Alarm the Forest~Overload~Uncollectible"
	def available(self):
		return self.entity.Game.space(self.entity.ID) > 0
		
class TreantTotem(Minion):
	Class, race, name = "Druid,Shaman", "Totem", "Treant Totem"
	mana, attack, health = 2, 2, 2
	index = "SCHOLOMANCE~Druid,Shaman~Minion~2~2~2~Totem~Treant Totem~Uncollectible"
	requireTarget, keyWord, description = False, "", ""
	name_CN = "树人图腾"
	
class CalltoAid(Spell):
	Class, school, name = "Druid,Shaman", "Nature", "Call to Aid"
	requireTarget, mana = False, 6
	index = "SCHOLOMANCE~Druid,Shaman~Spell~6~Nature~Call to Aid~Uncollectible"
	description = "Summon four 2/2 Treant Totems"
	name_CN = "呼叫增援"
	def available(self):
		return self.Game.space(self.ID) > 0
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.summon([TreantTotem(self.Game, self.ID) for i in range(4)], (-1, "totheRightEnd"))
		return None
		
class AlarmtheForest(Spell):
	Class, school, name = "Druid,Shaman", "Nature", "Alarm the Forest"
	requireTarget, mana = False, 6
	index = "SCHOLOMANCE~Druid,Shaman~Spell~6~Nature~Alarm the Forest~Overload~Uncollectible"
	description = "Summon four 2/2 Treant Totems with Rush. Overload: (2)"
	name_CN = "警醒森林"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.overload = 2
	
	def available(self):
		return self.Game.space(self.ID) > 0
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		minions = [TreantTotem(self.Game, self.ID) for i in range(4)]
		self.summon(minions, (-1, "totheRightEnd"))
		for minion in minions:
			if minion.onBoard: minion.getsStatus("Rush")
		return None
		
		
class SurvivaloftheFittest(Spell):
	Class, school, name = "Druid", "", "Survival of the Fittest"
	requireTarget, mana = False, 10
	index = "SCHOLOMANCE~Druid~Spell~10~~Survival of the Fittest"
	description = "Give +4/+4 to all minions in your hand, deck, and battlefield"
	name_CN = "优胜劣汰"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		for card in self.Game.Hand_Deck.hands[self.ID]:
			if card.type == "Minion": card.buffDebuff(4, 4)
		for card in self.Game.Hand_Deck.decks[self.ID]:
			if card.type == "Minion":
				card.attack += 4
				card.attack_Enchant += 4
				card.health += 4
				card.health_max += 4
		for minion in self.Game.minionsonBoard(self.ID):
			minion.buffDebuff(4, 4)
		return None
		
		
"""Hunter Cards"""
class AdorableInfestation(Spell):
	Class, school, name = "Hunter,Druid", "", "Adorable Infestation"
	requireTarget, mana = True, 1
	index = "SCHOLOMANCE~Hunter,Druid~Spell~1~~Adorable Infestation"
	description = "Give a minion +1/+1. Summon a 1/1 Cub. Add a Cub to your hand"
	name_CN = "萌物来袭"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			target.buffDebuff(1, 1)
			self.summon(MarsuulCub(self.Game, self.ID), -1)
			self.addCardtoHand(MarsuulCub, self.ID)
		return target
		
class MarsuulCub(Minion):
	Class, race, name = "Hunter,Druid", "Beast", "Marsuul Cub"
	mana, attack, health = 1, 1, 1
	index = "SCHOLOMANCE~Hunter,Druid~Minion~1~1~1~Beast~Marsuul Cub~Uncollectible"
	requireTarget, keyWord, description = False, "", ""
	name_CN = "魔鼠宝宝"
	
	
class CarrionStudies(Spell):
	Class, school, name = "Hunter", "", "Carrion Studies"
	requireTarget, mana = False, 1
	index = "SCHOLOMANCE~Hunter~Spell~1~~Carrion Studies"
	description = "Discover a Deathrattle minion. Your next one costs (1) less"
	name_CN = "腐食研习"
	poolIdentifier = "Deathrattle Minions as Hunter"
	@classmethod
	def generatePool(cls, pools):
		classCards = {s: [card for card in pools.ClassCards[s] if card.type == "Minion" and "~Deathrattle" in card.index] for s in pools.Classes}
		classCards["Neutral"] = [card for card in pools.NeutralCards if card.type == "Minion" and "~Deathrattle" in card.index]
		return ["Deathrattle Minions as "+Class for Class in pools.Classes], \
				[classCards[Class]+classCards["Neutral"] for Class in pools.Classes]
				
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if curGame.mode == 0:
			pool = tuple(self.rngPool("Deathrattle Minions as " + classforDiscover(self)))
			if curGame.guides:
				self.addCardtoHand(curGame.guides.pop(0), self.ID, byDiscover=True)
			else:
				if self.ID != self.Game.turn or "byOthers" in comment:
					self.addCardtoHand(npchoice(pool), self.ID, byDiscover=True)
				else:
					minions = npchoice(pool, 3, replace=False)
					curGame.options = [minion(curGame, self.ID) for minion in minions]
					curGame.Discover.startDiscover(self, pool)
		tempAura = GameManaAura_NextDeathrattleMinion1Less(self.Game, self.ID)
		self.Game.Manas.CardAuras.append(tempAura)
		tempAura.auraAppears()
		return None
		
	def discoverDecided(self, option, pool):
		self.Game.fixedGuides.append(type(option))
		self.addCardtoHand(option, self.ID, byDiscover=True)
		
class GameManaAura_NextDeathrattleMinion1Less(TempManaEffect):
	def __init__(self, Game, ID, changeby=0, changeto=-1):
		super().__init__(Game, ID, -1, -1)
		self.temporary = False
		
	def applicable(self, target):
		return target.ID == self.ID and target.type == "Minion" and target.deathrattles
		
	def text(self, CHN):
		return "你的下一张亡语随从牌法力值 消耗减少(1)点" if CHN \
				else "Your next Deathrattle minion costs (1) less"
				
				
class Overwhelm(Spell):
	Class, school, name = "Hunter", "", "Overwhelm"
	requireTarget, mana = True, 1
	index = "SCHOLOMANCE~Hunter~Spell~1~~Overwhelm"
	description = "Deal 2 damage to a minion. Deal one more damage for each Beast you control"
	name_CN = "数量压制"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
		
	def text(self, CHN):
		base = 2 + sum("Beast" in minion.race for minion in self.Game.minionsonBoard(self.ID))
		damage = (base + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		return "造成%d点伤害。你每控制一只野兽，便多造成一点伤害"%damage if CHN \
				else "Deal %d damage. Deal one more damage for each Beast you control"%damage
				
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			base = 2 + sum("Beast" in minion.race for minion in self.Game.minionsonBoard(self.ID))
			damage = (base + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			self.dealsDamage(target, damage)
		return target
		
class Wolpertinger(Minion):
	Class, race, name = "Hunter", "Beast", "Wolpertinger"
	mana, attack, health = 1, 1, 1
	index = "SCHOLOMANCE~Hunter~Minion~1~1~1~Beast~Wolpertinger~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Summon a copy of this"
	name_CN = "鹿角小飞兔"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		Copy = self.selfCopy(self.ID, self) if self.onBoard else type(self)(self.Game, self.ID)
		self.summon(Copy, self.pos+1)
		return None
		
		
class BloatedPython(Minion):
	Class, race, name = "Hunter", "Beast", "Bloated Python"
	mana, attack, health = 3, 1, 2
	index = "SCHOLOMANCE~Hunter~Minion~3~1~2~Beast~Bloated Python~Deathrattle"
	requireTarget, keyWord, description = False, "", "Deathrattle: Summon a 4/4 Hapless Handler"
	name_CN = "饱腹巨蟒"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.deathrattles = [SummonaHaplessHandler(self)]
		
class SummonaHaplessHandler(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.summon(HaplessHandler(self.entity.Game, self.entity.ID), self.entity.pos+1)
		
	def text(self, CHN):
		return "亡语：召唤一个4/4的倒霉的管理员" if CHN else "Deathrattle: Summon a 4/4 Hapless Handler"
		
class HaplessHandler(Minion):
	Class, race, name = "Hunter", "", "Hapless Handler"
	mana, attack, health = 4, 4, 4
	index = "SCHOLOMANCE~Hunter~Minion~4~4~4~~Hapless Handler~Uncollectible"
	requireTarget, keyWord, description = False, "", ""
	name_CN = "倒霉的管理员"
	
	
class ProfessorSlate(Minion):
	Class, race, name = "Hunter", "", "Professor Slate"
	mana, attack, health = 3, 3, 4
	index = "SCHOLOMANCE~Hunter~Minion~3~3~4~~Professor Slate~Legendary"
	requireTarget, keyWord, description = False, "", "Your spells are Poisonous"
	name_CN = "斯雷特教授"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.auras["Your spells are Poisonous"] = GameRuleAura_ProfessorSlate(self)
		
class GameRuleAura_ProfessorSlate(GameRuleAura):
	def auraAppears(self):
		self.entity.Game.status[self.entity.ID]["Spells Poisonous"] += 1
		
	def auraDisappears(self):
		self.entity.Game.status[self.entity.ID]["Spells Poisonous"] -= 1
		
		
class ShandoWildclaw(Minion):
	Class, race, name = "Hunter,Druid", "", "Shan'do Wildclaw"
	mana, attack, health = 3, 3, 3
	index = "SCHOLOMANCE~Hunter,Druid~Minion~3~3~3~~Shan'do Wildclaw~Choose One~Legendary"
	requireTarget, keyWord, description = True, "", "Choose One- Give Beasts in your deck +1/+1; or Transform into a copy of a friendly Beast"
	name_CN = "大导师野爪"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.options = [RiletheHerd_Option(self), Transfiguration_Option(self)]
		
	def need2Choose(self):
		return True
		
	def returnTrue(self, choice=0):
		return choice != 0
		
	def targetExists(self, choice=1):
		return self.selectableFriendlyMinionExists()
		
	def targetCorrect(self, target, choice=1):
		return target.type == "Minion" and "Beast" in target.race and target.ID == self.ID and target != self and target.onBoard
		
	#对于抉择随从而言，应以与战吼类似的方式处理，打出时抉择可以保持到最终结算。但是打出时，如果因为鹿盔和发掘潜力而没有选择抉择，视为到对方场上之后仍然可以而没有如果没有
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if choice < 1: #Choose Both aura on or choice == 0
			for card in self.Game.Hand_Deck.decks[self.ID]:
				if card.type == "Minion" and "Beast" in card.race:
					card.attack += 1
					card.attack_Enchant += 1
					card.health += 1
					card.health_max += 1 #By default, this healthGain has to be non-negative.
		if choice != 0 and target:
			if target and self.dead == False and self.Game.minionPlayed == self and (self.onBoard or self.inHand): #战吼触发时自己不能死亡。
				Copy = target.selfCopy(self.ID, self) if target.onBoard else type(target)(self.Game, self.ID)
				self.transform(self, Copy)
		return target
		
class RiletheHerd_Option(Option):
	name, description = "", "Give Beasts in your deck +1/+1"
	
class Transfiguration_Option(Option):
	name, description = "", "Transform into a copy of a friendly Beast"
	def available(self):
		return self.entity.targetExists(1)
		
		
class KroluskBarkstripper(Minion):
	Class, race, name = "Hunter", "Beast", "Krolusk Barkstripper"
	mana, attack, health = 4, 3, 5
	index = "SCHOLOMANCE~Hunter~Minion~4~3~5~Beast~Krolusk Barkstripper"
	requireTarget, keyWord, description = False, "", "Spellburst: Destroy a random enemy minion"
	name_CN = "裂树三叶虫"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_KroluskBarkstripper(self)]
		
class Trig_KroluskBarkstripper(Spellburst):
	def text(self, CHN):
		return "法术迸发：随机消灭一个敌方随从" if CHN else "Spellburst: Destroy a random enemy minion"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		minions = self.entity.Game.minionsAlive(3-self.entity.ID)
		if minions: self.entity.Game.killMinion(self.entity, npchoice(minions))
		
		
class TeachersPet(Minion):
	Class, race, name = "Hunter,Druid", "Beast", "Teacher's Pet"
	mana, attack, health = 5, 4, 5
	index = "SCHOLOMANCE~Hunter,Druid~Minion~5~4~5~Beast~Teacher's Pet~Taunt~Deathrattle"
	requireTarget, keyWord, description = False, "Taunt", "Taunt. Deathrattle: Summon a 3-Cost Beast"
	name_CN = "教师的爱宠"
	poolIdentifier = "3-Cost Beasts to Summon"
	@classmethod
	def generatePool(cls, pools):
		return "3-Cost Beasts to Summon", [card for card in pools.MinionswithRace["Beast"] if card.mana == 3]
		
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.deathrattles = [Summona3CostBeast(self)]
		
class Summona3CostBeast(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.summon(npchoice(self.rngPool("3-Cost Beasts to Summon"))(self.entity, self.entity.ID), self.entity.pos+1)
		
	def text(self, CHN):
		return "亡语：随机召唤一个法力值消耗为(3)的随从" if CHN else "Deathrattle: Summon a random 3-Cost Beast"
		
		
class GuardianAnimals(Spell):
	Class, school, name = "Hunter,Druid", "", "Guardian Animals"
	requireTarget, mana = False, 8
	index = "SCHOLOMANCE~Hunter,Druid~Spell~8~~Guardian Animals"
	description = "Summon two Beasts that cost (5) or less from your deck. Give them Rush"
	name_CN = "动物保镖"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		for num in range(2):
			beasts = [i for i, card in enumerate(self.Game.Hand_Deck.decks[self.ID]) if card.type == "Minion" and "Beast" in card.race and card.mana < 6]
			if beasts:
				beast = self.Game.summonfrom(npchoice(beasts), self.ID, -1, self, source='D')
				beast.getsStatus("Rush")
			else: break
		return None
		
		
"""Mage Cards"""
class BrainFreeze(Spell):
	Class, school, name = "Mage,Rogue", "Frost", "Brain Freeze"
	requireTarget, mana = True, 1
	index = "SCHOLOMANCE~Mage,Rogue~Spell~1~Frost~Brain Freeze~Combo"
	description = "Freeze a minion. Combo: Also deal 3 damage to it"
	name_CN = "冰冷智慧"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
		
	def effCanTrig(self):
		self.effectViable = self.Game.Counters.numCardsPlayedThisTurn[self.ID] > 0
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			if self.Game.Counters.numCardsPlayedThisTurn[self.ID] > 0:
				damage = (3 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
				target.getsStatus("Frozen")
				self.dealsDamage(target, damage)
			else:
				target.getsStatus("Frozen")
		return target
		
		
class DevolvingMissiles(Spell):
	Class, school, name = "Shaman,Mage", "Arcane~", "Devolving Missiles"
	requireTarget, mana = False, 1
	index = "SCHOLOMANCE~Shaman,Mage~Spell~1~Arcane~Devolving Missiles"
	description = "Shoot three missiles at random enemy minions that transform them into ones that cost (1) less"
	name_CN = "衰变飞弹"
	poolIdentifier = "0-Cost Minions to summon"
	@classmethod
	def generatePool(cls, pools):
		return ["%d-Cost Minions to Summon" % cost for cost in pools.MinionsofCost.keys()], \
			   list(pools.MinionsofCost.values())
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		side, game = 3 - self.ID, self.Game
		for num in range(3):
			minions = game.minionsonBoard(side)
			if minions: minion = npchoice(minions)
			else: break
			cost = type(minion).mana - 1
			while "%d-Cost Minions to Summon"%cost not in game.RNGPools:
				cost += 1
			newMinion = npchoice(self.rngPool("%d-Cost Minions to Summon"%cost))(game, side)
			self.transform(minion, newMinion)
		return None
		
		
class LabPartner(Minion):
	Class, race, name = "Mage", "", "Lab Partner"
	mana, attack, health = 1, 1, 3
	index = "SCHOLOMANCE~Mage~Minion~1~1~3~~Lab Partner~Spell Damage"
	requireTarget, keyWord, description = False, "Spell Damage", "Spell Damage +1"
	name_CN = "研究伙伴"
	
	
class WandThief(Minion):
	Class, race, name = "Mage,Rogue", "", "Wand Thief"
	mana, attack, health = 1, 1, 2
	index = "SCHOLOMANCE~Mage,Rogue~Minion~1~1~2~~Wand Thief~Combo"
	requireTarget, keyWord, description = False, "", "Combo: Discover a Mage spell"
	name_CN = "魔杖窃贼"
	poolIdentifier = "Mage Spells"
	@classmethod
	def generatePool(cls, pools):
		return "Mage Spells", [card for card in pools.ClassCards["Mage"] if card.type == "Spell"]
		
	def effCanTrig(self):
		self.effectViable = self.Game.Counters.numCardsPlayedThisTurn[self.ID] > 0
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if curGame.mode == 0:
			pool = tuple(self.rngPool("Mage Spells"))
			if curGame.guides:
				spell = curGame.guides.pop(0)
				if spell: self.addCardtoHand(spell, self.ID, byDiscover=True)
			else:
				if self.Game.Counters.numCardsPlayedThisTurn[self.ID] > 0 and self.ID == curGame.turn:
					spells = npchoice(pool, 3, replace=False)
					curGame.options = [spell(curGame, self.ID) for spell in spells]
					curGame.Discover.startDiscover(self, pool)
				else: curGame.fixedGuides.append(None)
		return None
		
	def discoverDecided(self, option, pool):
		self.Game.fixedGuides.append(type(option))
		self.addCardtoHand(option, self.ID, byDiscover=True)
		
		
class CramSession(Spell):
	Class, school, name = "Mage", "Arcane", "Cram Session"
	requireTarget, mana = False, 2
	index = "SCHOLOMANCE~Mage~Spell~2~Arcane~Cram Session"
	description = "Draw 1 card (improved by Spell Damage)"
	name_CN = "考前刷夜"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		num = 1 + self.countSpellDamage()
		for i in range(num): self.Game.Hand_Deck.drawCard(self.ID)
		return None
		
		
class Combustion(Spell):
	Class, school, name = "Mage", "Fire", "Combustion"
	requireTarget, mana = True, 3
	index = "SCHOLOMANCE~Mage~Spell~3~Fire~Combustion"
	description = "Deal 4 damage to a minion. Any excess damages both neighbors"
	name_CN = "燃烧"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			damage = (4 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			damageUsed = max(0, min(target.health, damage))
			damageLeft = damage - damageUsed
			if target.onBoard and damageLeft:
				neighbors = self.Game.neighbors2(target)[0]
				targets = [target] + neighbors
				damages = [damageUsed] + [damageLeft] * len(neighbors)
				self.dealsAOE(targets, damages)
			elif damageUsed:
				self.dealsDamage(target, damageUsed)
		return target
		
		
class Firebrand(Minion):
	Class, race, name = "Mage", "", "Firebrand"
	mana, attack, health = 3, 3, 4
	index = "SCHOLOMANCE~Mage~Minion~3~3~4~~Firebrand"
	requireTarget, keyWord, description = False, "", "Spellburst: Deal 4 damage randomly split among all enemy minions"
	name_CN = "火印火妖"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_Firebrand(self)]
		
class Trig_Firebrand(Spellburst):
	def text(self, CHN):
		return "法术迸发：造成4点伤害，随机分配到所有敌人身上" if CHN else "Spellburst: Deal 4 damage randomly split among all enemy minions"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		minion = self.entity
		for num in range(4):
			minions = minion.Game.minionsAlive(3-minion.ID)
			if minions: minion.dealsDamage(npchoice(minions), 1)
			else: break
				
				
class PotionofIllusion(Spell):
	Class, school, name = "Mage,Rogue", "Arcane", "Potion of Illusion"
	requireTarget, mana = False, 4
	index = "SCHOLOMANCE~Mage,Rogue~Spell~4~Arcane~Potion of Illusion"
	description = "Add 1/1 copies of your minions to your hand. They cost (1)"
	name_CN = "幻觉药水"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.addCardtoHand([minion.selfCopy(self.ID, self, 1, 1, 1) for minion in self.Game.minionsonBoard(self.ID)], self.ID)
		return None
		
		
class JandiceBarov(Minion):
	Class, race, name = "Mage,Rogue", "", "Jandice Barov"
	mana, attack, health = 6, 2, 1
	index = "SCHOLOMANCE~Mage,Rogue~Minion~6~2~1~~Jandice Barov~Battlecry~Legendary"
	requireTarget, keyWord, description = False, "", "Battlecry: Summon two random 5-Cost minions. Secretly pick one that dies when it takes damage"
	name_CN = "詹迪斯·巴罗夫"
	poolIdentifier = "5-Cost Minions to Summon"
	@classmethod
	def generatePool(cls, pools):
		return "5-Cost Minions to Summon", pools.MinionsofCost[5]
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		minion1, minion2 = [minion(curGame, self.ID) for minion in npchoice(self.rngPool("5-Cost Minions to Summon"), 2, replace=False)]
		pos = (self.pos, "leftandRight") if self.onBoard else (-1, "totheRightEnd")
		self.summon([minion1, minion2], pos)
		if minion1.onBoard and minion2.onBoard:
			if curGame.mode == 0:
				if curGame.guides:
					minion = [minion1, minion2][curGame.guides.pop(0)]
					minion.getsTrig(Trig_JandiceBarov(minion), trigType="TrigBoard")
				else: #假设只有两个召唤的随从都在场的时候才会让你选择
					if minion1.onBoard and minion2.onBoard and self.ID == curGame.turn:
						if "byOthers" in comment:
							minion = [minion1, minion2][nprandint(2)]
							
						else:
							curGame.options = [minion1, minion2]
							curGame.Discover.startDiscover(self)
					else: i = -1
		return None
		
	def discoverDecided(self, option, pool):
		for i, minion in enumerate(self.Game.options):
			if minion == option:
				self.Game.fixedGuides.append(i)
				minion.getsTrig(Trig_JandiceBarov(minion), trigType="TrigBoard")
				break
				
class Trig_JandiceBarov(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["MinionTakesDmg"])
		self.hide = True
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and target == self.entity
		
	def text(self, CHN):
		return "该随从受到伤害时死亡" if CHN else "This minion dies when taking damage"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.Game.killMinion(None, self.entity)
		
		
class MozakiMasterDuelist(Minion):
	Class, race, name = "Mage", "", "Mozaki, Master Duelist"
	mana, attack, health = 5, 3, 8
	index = "SCHOLOMANCE~Mage~Minion~5~3~8~~Mozaki, Master Duelist~Legendary"
	requireTarget, keyWord, description = False, "", "After you cast a spell, gain Spell Damage +1"
	name_CN = "决斗大师 莫扎奇"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_MozakiMasterDuelist(self)]
		
class Trig_MozakiMasterDuelist(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["SpellBeenPlayed"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject.ID == self.entity.ID
		
	def text(self, CHN):
		return "在你施放一个法术后，获得法术伤害+1" if CHN else "After you cast a spell, gain Spell Damage +1"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.getsStatus("Spell Damage")
		
		
class WyrmWeaver(Minion):
	Class, race, name = "Mage", "", "Wyrm Weaver"
	mana, attack, health = 4, 3, 5
	index = "SCHOLOMANCE~Mage~Minion~4~3~5~~Wyrm Weaver"
	requireTarget, keyWord, description = False, "", "Spellburst: Summon two 1/2 Mana Wyrms"
	name_CN = "浮龙培养师"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_WyrmWeaver(self)]
		
class Trig_WyrmWeaver(Spellburst):
	def text(self, CHN):
		return "法术迸发：召唤两个1/2的法力浮龙" if CHN else "Spellburst: Summon two 1/2 Mana Wyrms"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		minion = self.entity
		pos = (minion.pos, "leftandRight") if minion.onBoard else (-1, "totheRightEnd")
		minion.summon([ManaWyrm(minion.Game, minion.ID) for i in range(2)], pos)


"""Paladin Cards"""
class FirstDayofSchool(Spell):
	Class, school, name = "Paladin", "", "First Day of School"
	requireTarget, mana = False, 1
	index = "SCHOLOMANCE~Paladin~Spell~1~~First Day of School"
	description = "Add 2 random 1-Cost minions to your hand"
	name_CN = "新生入学"
	poolIdentifier = "1-Cost Minions"
	@classmethod
	def generatePool(cls, pools):
		return "1-Cost Minions", pools.MinionsofCost[1]
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.addCardtoHand(npchoice(self.rngPool("1-Cost Minions"), 2, replace=False), self.ID)
		return None
		
		
class WaveofApathy(Spell):
	Class, school, name = "Paladin,Priest", "", "Wave of Apathy"
	requireTarget, mana = False, 1
	index = "SCHOLOMANCE~Paladin,Priest~Spell~1~~Wave of Apathy"
	description = "Set the Attack of all enemy minions to 1 until your next turn"
	name_CN = "倦怠光波"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		s = "StartofTurn %d"%self.ID
		for minion in self.Game.minionsonBoard(3-self.ID):
			minion.statReset(1, False, attRevertTime=s)
		return None
		
		
class ArgentBraggart(Minion):
	Class, race, name = "Paladin", "", "Argent Braggart"
	mana, attack, health = 2, 1, 1
	index = "SCHOLOMANCE~Paladin~Minion~2~1~1~~Argent Braggart~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Gain Attack and Health to match the highest in the battlefield"
	name_CN = "银色自大狂"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		highestAtt, highestHealth = 0, 0
		for minion in self.Game.minionsonBoard(self.ID) + self.Game.minionsonBoard(3-self.ID):
			highestAtt, highestHealth = max(highestAtt, minion.attack), max(highestHealth, minion.health)
		attChange, healthChange = highestAtt - self.attack, highestHealth - self.health
		if attChange or healthChange: self.buffDebuff(attChange, healthChange)
		return None
		
		
class GiftofLuminance(Spell):
	Class, school, name = "Paladin,Priest", "Holy", "Gift of Luminance"
	requireTarget, mana = True, 3
	index = "SCHOLOMANCE~Paladin,Priest~Spell~3~Holy~Gift of Luminance"
	description = "Give a minion Divine Shield, then summon a 1/1 copy of it"
	name_CN = "流光之赐"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			target.getsStatus("Divine Shield")
			Copy = target.selfCopy(target.ID, self) if target.onBoard or target.inHand else type(target)(self.Game, target.ID)
			Copy.statReset(1, 1)
			self.summon(Copy, target.pos+1)
		return target
		
		
class GoodyTwoShields(Minion):
	Class, race, name = "Paladin", "", "Goody Two-Shields"
	mana, attack, health = 3, 4, 2
	index = "SCHOLOMANCE~Paladin~Minion~3~4~2~~Goody Two-Shields~Divine Shield"
	requireTarget, keyWord, description = False, "Divine Shield", "Spellburst: Gain Divine Shield"
	name_CN = "双盾优等生"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_GoodyTwoShields(self)]
		
class Trig_GoodyTwoShields(Spellburst):
	def text(self, CHN):
		return "法术迸发：获得圣盾" if CHN else "Spellburst: Gain Divine Shield"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.getsStatus("Divine Shield")
		
		
class HighAbbessAlura(Minion):
	Class, race, name = "Paladin,Priest", "", "High Abbess Alura"
	mana, attack, health = 5, 3, 6
	index = "SCHOLOMANCE~Paladin,Priest~Minion~5~3~6~~High Abbess Alura"
	requireTarget, keyWord, description = False, "", "Spellburst: Cast a spell from your deck (targets this if possible)"
	name_CN = "高阶修士奥露拉"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_HighAbbessAlura(self)]
		
class Trig_HighAbbessAlura(Spellburst):
	def text(self, CHN):
		return "法术迸发：从你的牌库中施放一张法术牌(尽可能以该随从为目标)" if CHN else "Spellburst: Cast a spell from your deck (targets this if possible)"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		spells = [i for i, card in enumerate(self.entity.Game.Hand_Deck.decks[self.entity.ID]) if card.type == "Spell"]
		if spells:
			spell = self.entity.Game.Hand_Deck.extractfromDeck(npchoice(spells), self.entity.ID)[0]
			spell.cast(None, comment="targetPrefered", preferedTarget=self.entity)
			self.entity.Game.gathertheDead()
			
			
class BlessingofAuthority(Spell):
	Class, school, name = "Paladin", "Holy", "Blessing of Authority"
	requireTarget, mana = True, 5
	index = "SCHOLOMANCE~Paladin~Spell~5~Holy~Blessing of Authority"
	description = "Give a minion +8/+8. It can't attack heroes this turn"
	name_CN = "威能祝福"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			target.buffDebuff(8, 8)
			trig = Trig_BlessingofAuthority(target)
			target.trigsBoard.append(trig)
			trig.connect()
		return target

class Trig_BlessingofAuthority(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["TurnEnds"])
		self.inherent = False
	
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard  #Even if the current turn is not minion's owner's turn
	
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.marks["Can't Attack Hero"] -= 1
		self.disconnect()
		try:
			self.entity.trigsBoard.remove(self)
		except:
			pass
	
	def text(self, CHN):
		return "随从重新可以攻击英雄" if CHN else "Minion can attack heroes again"


class DevoutPupil(Minion):
	Class, race, name = "Paladin,Priest", "", "Devout Pupil"
	mana, attack, health = 6, 4, 5
	index = "SCHOLOMANCE~Paladin,Priest~Minion~6~4~5~~Devout Pupil~Divine Shield~Taunt"
	requireTarget, keyWord, description = False, "Divine Shield,Taunt", "Divine Shield,Taunt. Costs (1) less for each spell you've cast on friendly characters this game"
	name_CN = "虔诚的学徒"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsHand = [Trig_DevoutPupil(self)]
		
	def selfManaChange(self):
		if self.inHand:
			self.mana -= len(self.Game.Counters.spellsonFriendliesThisGame[self.ID])
			self.mana = max(self.mana, 0)
			
class Trig_DevoutPupil(TrigHand):
	def __init__(self, entity):
		super().__init__(entity, ["SpellBeenPlayed"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.inHand and target and subject.ID == target.ID and subject.ID == self.entity.ID
		
	def text(self, CHN):
		return "每当你对一个友方角色施放法术，重新计算费用" if CHN else "Whenever you cast a spell on a friendly character, recalculate the cost"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.Game.Manas.calcMana_Single(self.entity)
		
		
class JudiciousJunior(Minion):
	Class, race, name = "Paladin", "", "Judicious Junior"
	mana, attack, health = 6, 4, 9
	index = "SCHOLOMANCE~Paladin~Minion~6~4~9~~Judicious Junior~Lifesteal"
	requireTarget, keyWord, description = False, "Lifesteal", "Lifesteal"
	name_CN = "踏实的大三学姐"
	
	
class TuralyontheTenured(Minion):
	Class, race, name = "Paladin", "", "Turalyon, the Tenured"
	mana, attack, health = 8, 3, 12
	index = "SCHOLOMANCE~Paladin~Minion~8~3~12~~Turalyon, the Tenured~Rush~Legendary"
	requireTarget, keyWord, description = False, "Rush", "Rush. Whenever this attacks a minion, set the defender's Attack and Health to 3"
	name_CN = "终身教授图拉扬"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_TuralyontheTenured(self)]
		
#可以通过宣传牌确认是施放法术之后触发
class Trig_TuralyontheTenured(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["MinionAttackingMinion"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject == self.entity
		
	def text(self, CHN):
		return "每当其攻击一个随从，将目标的攻击力和生命值变为3" if CHN \
				else "Whenever this attacks a minion, set the defender's Attack and Health to 3"
				
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		target.statReset(3, 3)
		
"""Priest cards"""
class RaiseDead(Spell):
	Class, school, name = "Priest,Warlock", "Shadow", "Raise Dead"
	requireTarget, mana = False, 0
	index = "SCHOLOMANCE~Priest,Warlock~Spell~0~Shadow~Raise Dead"
	description = "Deal 3 damage to your hero. Return two friendly minions that died this game to your hand"
	name_CN = "亡者复生"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		damage = (3 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		self.dealsDamage(self.Game.heroes[self.ID], damage)
		pool = self.Game.Counters.minionsDiedThisGame[self.ID]
		if pool: self.addCardtoHand(npchoice(pool, min(2, len(pool)), replace=False), self.ID)
		return None
		
		
class DraconicStudies(Spell):
	Class, school, name = "Priest", "", "Draconic Studies"
	requireTarget, mana = False, 1
	index = "SCHOLOMANCE~Priest~Spell~1~~Draconic Studies"
	description = "Discover a Dragon. Your next one costs (1) less"
	name_CN = "龙族研习"
	poolIdentifier = "Dragons as Priest"
	@classmethod
	def generatePool(cls, pools):
		classCards = {s: [] for s in pools.ClassesandNeutral}
		for card in pools.MinionswithRace["Dragon"]:
			for Class in card.Class.split(','):
				classCards[Class].append(card)
		return ["Dragons as " + Class for Class in pools.Classes], \
			   [classCards[Class] + classCards["Neutral"] for Class in pools.Classes]
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if curGame.mode == 0:
			pool = tuple(self.rngPool("Dragons as " + classforDiscover(self)))
			if curGame.guides:
				self.addCardtoHand(curGame.guides.pop(0), self.ID, byDiscover=True)
			else:
				if self.ID != self.Game.turn or "byOthers" in comment:
					self.addCardtoHand(npchoice(pool), self.ID, byDiscover=True)
				else:
					minions = npchoice(pool, 3, replace=False)
					curGame.options = [minion(curGame, self.ID) for minion in minions]
					curGame.Discover.startDiscover(self, pool)
		tempAura = GameManaAura_NextDragon1Less(self.Game, self.ID)
		self.Game.Manas.CardAuras.append(tempAura)
		tempAura.auraAppears()
		return None
		
	def discoverDecided(self, option, pool):
		self.Game.fixedGuides.append(type(option))
		self.addCardtoHand(option, self.ID, byDiscover=True)
		
class GameManaAura_NextDragon1Less(TempManaEffect):
	def __init__(self, Game, ID, changeby=0, changeto=-1):
		super().__init__(Game, ID, -1, -1)
		self.temporary = False
		
	def applicable(self, target):
		return target.ID == self.ID and target.type == "Minion" and "Dragon" in target.race
		
	def text(self, CHN):
		return "你的下一张龙牌的法力值消耗减少(1)点" if CHN else "Your next Dragon costs (1) less"
		
		
class FrazzledFreshman(Minion):
	Class, race, name = "Priest", "", "Frazzled Freshman"
	mana, attack, health = 1, 1, 4
	index = "SCHOLOMANCE~Priest~Minion~1~1~4~~Frazzled Freshman"
	requireTarget, keyWord, description = False, "", ""
	name_CN = "疲倦的大一新生"
	
	
class MindrenderIllucia(Minion):
	Class, race, name = "Priest", "", "Mindrender Illucia"
	mana, attack, health = 3, 1, 3
	index = "SCHOLOMANCE~Priest~Minion~3~1~3~~Mindrender Illucia~Battlecry~Legendary"
	requireTarget, keyWord, description = False, "", "Battlecry: Swap hands and decks with your opponent until your next turn"
	name_CN = "裂心者伊露希亚"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		HD = self.Game.Hand_Deck
		hand1, hand2 = HD.extractfromHand(None, 1, all=True)[0], HD.extractfromHand(None, 2, all=True)[0]
		deck1, deck2 = HD.extractfromDeck(None, 1, all=True)[0], HD.extractfromDeck(None, 2, all=True)[0]
		HD.decks[1], HD.decks[2] = deck2, deck1
		for ID in range(1, 3):
			for card in HD.decks[ID]:
				card.ID = ID
				card.entersDeck()
		HD.addCardtoHand(hand2, 1)
		HD.addCardtoHand(hand1, 2)
		trigSwap = SwapHandsandDecksBack(self.Game, self.ID)
		#假设连续释放该效果会覆盖之前的效果（移除同类同ID的trig）
		trigs = self.Game.turnStartTrigger
		for i in reversed(range(len(trigs))):
			if isinstance(trigs[i], SwapHandsandDecksBack):
				trigs.pop(i)
		trigs.append(trigSwap)
		return None
		
class SwapHandsandDecksBack:
	def __init__(self, Game, ID):
		self.Game, self.ID = Game, ID
		
	def turnStartTrigger(self):
		HD = self.Game.Hand_Deck
		hand1, hand2 = HD.extractfromHand(None, 1, all=True)[0], HD.extractfromHand(None, 2, all=True)[0]
		deck1, deck2 = HD.extractfromDeck(None, 1, all=True)[0], HD.extractfromDeck(None, 2, all=True)[0]
		HD.decks[1], HD.decks[2] = deck2, deck1
		for ID in range(1, 3):
			for card in HD.decks[ID]:
				card.ID = ID
				card.entersDeck()
		HD.addCardtoHand(hand2, 1)
		HD.addCardtoHand(hand1, 2)
		
		try: self.Game.turnStartTrigger.remove(self)
		except: pass
		
	def createCopy(self, game):
		return type(self)(game, self.ID)
		
		
class PowerWordFeast(Spell):
	Class, school, name = "Priest", "", "Power Word: Feast"
	requireTarget, mana = True, 2
	index = "SCHOLOMANCE~Priest~Spell~2~~Power Word: Feast"
	description = "Give a minion +2/+2. Restore it to full health at the end of this turn"
	name_CN = "真言术：宴"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			target.buffDebuff(2, 2)
			trig = Trig_PowerWordFeast(target)
			target.trigsBoard.append(trig)
			trig.connect()
		return target
		
class Trig_PowerWordFeast(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["TurnEnds"])
		self.inherent = False
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard #Even if the current turn is not minion's owner's turn
		
	def text(self, CHN):
		return "在本回合结束时，真言术：宴为该随从恢复所有生命值" if CHN else "At the end of this turn, Power Word: Feast restores this minion to full Health"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.disconnect()
		try: self.entity.trigsBoard.remove(self)
		except: pass
		heal = self.entity.health_max * (2 ** self.entity.countHealDouble())
		PowerWordFeast(self.entity.Game, self.entity.ID).restoresHealth(self.entity, heal)
		
		
class BrittleboneDestroyer(Minion):
	Class, race, name = "Priest,Warlock", "", "Brittlebone Destroyer"
	mana, attack, health = 4, 3, 3
	index = "SCHOLOMANCE~Priest,Warlock~Minion~4~3~3~~Brittlebone Destroyer~Battlecry"
	requireTarget, keyWord, description = True, "", "Battlecry: If your hero's Health changed this turn, destroy a minion"
	name_CN = "脆骨破坏者"
	
	def returnTrue(self, choice=0):
		return self.Game.Counters.heroChangedHealthThisTurn[self.ID]
		
	def effCanTrig(self):
		self.effectViable = self.Game.Counters.heroChangedHealthThisTurn[self.ID]
		
	def targetExists(self, choice=0):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target != self and target.onBoard
		
	#If the minion is shuffled into deck already, then nothing happens.
	#If the minion is returned to hand, move it from enemy hand into our hand.
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target and self.Game.Counters.heroChangedHealthThisTurn[self.ID]:
			self.Game.killMinion(self, target)
		return target
		
		
class CabalAcolyte(Minion):
	Class, race, name = "Priest", "", "Cabal Acolyte"
	mana, attack, health = 4, 2, 4
	index = "SCHOLOMANCE~Priest~Minion~4~2~4~~Cabal Acolyte~Taunt"
	requireTarget, keyWord, description = False, "Taunt", "Taunt. Spellburst: Gain control of a random enemy minion with 2 or less Attack"
	name_CN = "秘教侍僧"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_CabalAcolyte(self)]
		
class Trig_CabalAcolyte(Spellburst):
	def text(self, CHN):
		return "法术迸发：随机获得一个攻击力小于或等于2的敌方随从的控制权" if CHN \
				else "Spellburst: Gain control of a random enemy minion with 2 or less Attack"
				
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		minions = self.entity.Game.minionsAlive(3-self.entity.ID)
		if minions: self.entity.Game.minionSwitchSide(npchoice(minions))
		
		
class DisciplinarianGandling(Minion):
	Class, race, name = "Priest,Warlock", "", "Disciplinarian Gandling"
	mana, attack, health = 4, 3, 6
	index = "SCHOLOMANCE~Priest,Warlock~Minion~4~3~6~~Disciplinarian Gandling~Legendary"
	requireTarget, keyWord, description = False, "", "After you play a minion, destroy it and summon a 4/4 Failed Student"
	name_CN = "教导主任加丁"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_DisciplinarianGandling(self)]
		
class Trig_DisciplinarianGandling(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["MinionBeenPlayed"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject.ID == self.entity.ID and subject.onBoard
		
	def text(self, CHN):
		return "在你使用一张随从牌后，将其消灭并召唤一个4/4的挂掉的学生" if CHN \
				else "After you play a minion, destroy it and summon a 4/4 Failed Student"
				
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		ID, game = self.entity.ID, self.entity.Game
		position, subject.dead = subject.pos, True
		game.gathertheDead()
		#Rule copied from Conjurer's Calling(Rise of Shadows)
		if position == 0: pos = -1 #Summon to the leftmost
		elif position < len(game.minionsonBoard(ID)): pos = position + 1
		else: pos = -1
		self.entity.summon(FailedStudent(game, ID), pos)
		
class FailedStudent(Minion):
	Class, race, name = "Priest,Warlock", "", "Failed Student"
	mana, attack, health = 4, 4, 4
	index = "SCHOLOMANCE~Priest,Warlock~Minion~4~4~4~~Failed Student~Uncollectible"
	requireTarget, keyWord, description = False, "", ""
	name_CN = "挂掉的学生"
	
	
class Initiation(Spell):
	Class, school, name = "Priest", "Shadow~", "Initiation"
	requireTarget, mana = True, 6
	index = "SCHOLOMANCE~Priest~Spell~6~Shadow~Initiation"
	description = "Deal 4 damage to a minion. If that kills it, summons a new copy"
	name_CN = "通窍"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			damage = (4 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			dmgTaker, damageActual = self.dealsDamage(target, damage)
			if dmgTaker.health < 1 or dmgTaker.dead:
				self.summon(type(dmgTaker)(self.Game, self.ID), -1)
		return target
		
		
class FleshGiant(Minion):
	Class, race, name = "Priest,Warlock", "", "Flesh Giant"
	mana, attack, health = 8, 8, 8
	index = "SCHOLOMANCE~Priest,Warlock~Minion~8~8~8~~Flesh Giant"
	requireTarget, keyWord, description = False, "", "Costs (1) less for each time your Hero's Health changed during your turn"
	name_CN = "血肉巨人"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsHand = [Trig_FleshGiant(self)]
		
	def selfManaChange(self):
		if self.inHand:
			self.mana -= self.Game.Counters.timesHeroChangedHealth_inOwnTurn[self.ID]
			self.mana = max(self.mana, 0)
			
class Trig_FleshGiant(TrigHand):
	def __init__(self, entity):
		#假设这个费用改变扳机在“当你使用一张法术之后”。不需要预检测
		super().__init__(entity, ["HeroChangedHealthinTurn"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.inHand and ID == self.entity.ID
		
	def text(self, CHN):
		return "每当你的英雄的生命值在你的回合发生变化，重新计算费用" if CHN \
				else "Whenever your hero's Health changes during your turn, recalculate the cost"
				
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.Game.Manas.calcMana_Single(self.entity)
		
		
"""Rogue Cards"""
class SecretPassage(Spell):
	Class, school, name = "Rogue", "", "Secret Passage"
	requireTarget, mana = False, 1
	index = "SCHOLOMANCE~Rogue~Spell~1~~Secret Passage"
	description = "Replace your hand with 4 cards from your deck. Swap back next turn"
	name_CN = "秘密通道"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		deck = self.Game.Hand_Deck.decks[self.ID]
		deckSize = len(deck)
		indices = list(npchoice(range(deckSize), min(deckSize, 4), replace=False))
		indices.sort() #Smallest index becomes first element
		if indices:
			cardsfromHand = self.Game.Hand_Deck.extractfromHand(None, self.ID, all=True, enemyCanSee=False, animate=False)[0]
			cardsfromDeck = [self.Game.Hand_Deck.extractfromDeck(i, self.ID, enemyCanSee=False, animate=False)[0] for i in reversed(indices)]
			if self.Game.GUI:
				panda_SecretPassage_LeaveHand(self.Game, self.Game.GUI, cardsfromHand)
				
			SecretPassage_Effect(self.Game, self.ID, cardsfromHand, cardsfromDeck).connect()
			self.Game.Hand_Deck.addCardtoHand(cardsfromDeck, self.ID)
		return None
		
def panda_SecretPassage_LeaveHand(game, GUI, cards):
	para = GUI.PARALLEL()
	for i, card in zip(range(len(cards)), reversed(cards)):
		btn, nodepath = card.btn, card.btn.np
		x, y, z = nodepath.getPos()
		para.append(GUI.SEQUENCE(GUI.WAIT(0.4*i), btn.genLerpInterval(pos=(x, 1.5, z), hpr=(0, 0, 0), duration=0.4),
								 GUI.WAIT(0.2), btn.genLerpInterval(pos=(30, 1.5, z), duration=0.3))
					)
	GUI.seqHolder[-1].append(para)
	
def panda_SecretPassage_BackfromPassage(game, GUI, cards, poses, hprs):
	para = GUI.PARALLEL()
	spaceinHand = game.Hand_Deck.spaceinHand(cards[0].ID)
	for i, card, pos, hpr in zip(range(len(cards)), cards, poses, hprs):
		nodepath, btn = card.btn.np, card.btn
		if i + 1 > spaceinHand: para.append(GUI.FUNC(btn.np.removeNode))
		else:
			para.append(GUI.SEQUENCE(GUI.FUNC(nodepath.setPos, -30, 1.5, HandZone_Z), GUI.WAIT(i*0.3),
									 btn.genLerpInterval(pos=(0, 1.5, 2.5)), GUI.WAIT(0.2),
									btn.genLerpInterval(pos=pos, hpr=hpr, duration=0.3)))
	GUI.seqHolder[-1].append(para)
	
class SecretPassage_Effect:
	def __init__(self, Game, ID, cardsfromHand, cardsfromDeck):
		self.Game, self.ID = Game, ID
		self.card = SecretPassage(Game, ID)
		self.cardsfromHand, self.cardsfromDeck = cardsfromHand, cardsfromDeck
		
	def connect(self):
		self.Game.turnEndTrigger.append(self)
		if self.Game.GUI: self.Game.GUI.heroZones[self.ID].addaTrig(self.card)
		
	def turnEndTrigger(self):
		HD = self.Game.Hand_Deck
		cards2Return2Deck = [card for card in HD.hands[self.ID] if card in self.cardsfromDeck]
		for card in cards2Return2Deck:
			HD.extractfromHand(card, self.ID, all=False, enemyCanSee=False, animate=False)
			card.reset(self.ID)
		GUI = self.Game.GUI
		if GUI:
			panda_SecretPassage_LeaveHand(self.Game, GUI, cards2Return2Deck)
			Y = HandZone1_Y if self.ID == self.Game.GUI.ID else HandZone2_Y
			poses, hprs = posHandsTable[Y][len(cards2Return2Deck)], hprHandsTable[Y][len(cards2Return2Deck)]
			panda_SecretPassage_BackfromPassage(self.Game, GUI, self.cardsfromHand, poses, hprs)
		
		HD.decks[self.ID] += cards2Return2Deck
		for card in cards2Return2Deck:
			card.entersDeck()
		npshuffle(HD.decks[self.ID])
		HD.addCardtoHand(self.cardsfromHand, self.ID)
		
		self.Game.turnEndTrigger.remove(self)
		if GUI: GUI.heroZones[self.ID].removeaTrig(self.card)
		
	def createCopy(self, game): #TurnStartTrigger
		return type(self)(game, self.ID, [card.createCopy(game) for card in self.cardsfromHand],
							  			[card.createCopy(game) for card in self.cardsfromDeck])
		
		
class Plagiarize(Secret):
	Class, school, name = "Rogue", "", "Plagiarize"
	requireTarget, mana = False, 2
	index = "SCHOLOMANCE~Rogue~Spell~2~~Plagiarize~~Secret"
	description = "Secret: At the end of your opponent's turn, add copies of the cards they played this turn"
	name_CN = "抄袭"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_Plagiarize(self)]
		
class Trig_Plagiarize(SecretTrigger):
	def __init__(self, entity):
		super().__init__(entity, ["TurnEnds"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.ID != ID and self.entity.Game.Counters.cardsPlayedEachTurn[3-self.entity.ID][-1]
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		cards = self.entity.Game.Counters.cardsPlayedEachTurn[3-self.entity.ID][-1]
		self.entity.addCardtoHand(cards, self.entity.ID)
		
		
class Coerce(Spell):
	Class, school, name = "Rogue,Warrior", "", "Coerce"
	requireTarget, mana = True, 3
	index = "SCHOLOMANCE~Rogue,Warrior~Spell~3~~Coerce~Combo"
	description = "Destroy a damaged minion. Combo: Destroy any minion"
	name_CN = "胁迫"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard and \
				(target.health < target.health_max or self.Game.Counters.numCardsPlayedThisTurn[self.ID] > 0)
				
	def effCanTrig(self):
		self.effectViable = self.Game.Counters.numCardsPlayedThisTurn[self.ID] > 0
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			self.Game.killMinion(self, target)
		return target
		
		
class SelfSharpeningSword(Weapon):
	Class, name, description = "Rogue", "Self-Sharpening Sword", "After your hero attacks, gain +1 Attack"
	mana, attack, durability = 3, 1, 4
	index = "SCHOLOMANCE~Rogue~Weapon~3~1~4~Self-Sharpening Sword"
	name_CN = "自砺之锋"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_SelfSharpeningSword(self)]
		
class Trig_SelfSharpeningSword(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["HeroAttackedMinion", "HeroAttackedHero"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject.ID == self.entity.ID and self.entity.onBoard
		
	def text(self, CHN):
		return "在你的英雄攻击后，获得+1攻击力" if CHN else "After your hero attacks, gain +1 Attack"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.gainStat(1, 0)
		
		
class VulperaToxinblade(Minion):
	Class, race, name = "Rogue", "", "Vulpera Toxinblade"
	mana, attack, health = 3, 3, 3
	index = "SCHOLOMANCE~Rogue~Minion~3~3~3~~Vulpera Toxinblade"
	requireTarget, keyWord, description = False, "", "Your weapon has +2 Attack"
	name_CN = "狐人淬毒师"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.auras["Your weapon has +2 Attack"] = StatAura_VulperaToxinblade(self)
		
class StatAura_VulperaToxinblade:
	def __init__(self, entity):
		self.entity = entity
		self.auraAffected = []
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject.ID == self.entity.ID
		
	def trig(self, signal, ID, subject, target, number, comment, choice=0):
		if self.canTrig(signal, ID, subject, target, number, comment):
			self.effect(signal, ID, subject, target, number, comment)
			
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.applies(subject)
		
	def applies(self, subject):
		Stat_Receiver(subject, self, 2).effectStart()
		
	def auraAppears(self):
		weapon = self.entity.Game.availableWeapon(self.entity.ID)
		if weapon: self.applies(weapon)
		try: self.entity.Game.trigsBoard[self.entity.ID]["WeaponEquipped"].append(self)
		except: self.entity.Game.trigsBoard[self.entity.ID]["WeaponEquipped"] = [self]
		
	def auraDisappears(self):
		for weapon, receiver in self.auraAffected[:]:
			receiver.effectClear()
		self.auraAffected = []
		try: self.entity.Game.trigsBoard[self.entity.ID]["WeaponEquipped"].remove(self)
		except: pass
		
	def selfCopy(self, recipient):
		return type(self)(recipient)
		
	#这个函数会在复制场上扳机列表的时候被调用。
	def createCopy(self, game):
		#一个光环的注册可能需要注册多个扳机
		if self not in game.copiedObjs: #这个光环没有被复制过
			entityCopy = self.entity.createCopy(game)
			Copy = self.selfCopy(entityCopy)
			game.copiedObjs[self] = Copy
			for entity, receiver in self.auraAffected:
				entityCopy = entity.createCopy(game)
				index = entity.auraReceivers.index(receiver)
				receiverCopy = entityCopy.auraReceivers[index]
				receiverCopy.source = Copy #补上这个receiver的source
				Copy.auraAffected.append((entityCopy, receiverCopy))
			return Copy
		else:
			return game.copiedObjs[self]
			
			
class InfiltratorLilian(Minion):
	Class, race, name = "Rogue", "", "Infiltrator Lilian"
	mana, attack, health = 4, 4, 2
	index = "SCHOLOMANCE~Rogue~Minion~4~4~2~~Infiltrator Lilian~Stealth~Deathrattle~Legendary"
	requireTarget, keyWord, description = False, "Stealth", "Stealth. Deathrattle: Summon a 4/2 Forsaken Lilian that attacks a random enemy"
	name_CN = "渗透者莉莉安"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.deathrattles = [SummonForsakenLilian(self)]
		
class SummonForsakenLilian(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		minion = ForsakenLilian(self.entity.Game, self.entity.ID)
		self.entity.summon(minion, self.entity.pos+1)
		objs = self.entity.Game.charsAlive(3-self.entity.ID)
		if minion.onBoard and minion.health > 0 and not minion.dead and objs:
			self.entity.Game.battle(minion, npchoice(objs), verifySelectable=False, resolveDeath=False)
			
	def text(self, CHN):
		return "亡语：召唤一个4/2的被遗忘者莉莉安，并使其随机攻击一个敌人" if CHN else "Deathrattle: Summon a 4/2 Forsaken Lilian that attacks a random enemy"
		
class ForsakenLilian(Minion):
	Class, race, name = "Rogue", "", "Forsaken Lilian"
	mana, attack, health = 4, 4, 2
	index = "SCHOLOMANCE~Rogue~Minion~4~4~2~~Forsaken Lilian~Legendary~Uncollectible"
	requireTarget, keyWord, description = False, "", ""
	name_CN = "被遗忘者莉莉安"
	
	
class ShiftySophomore(Minion):
	Class, race, name = "Rogue", "", "Shifty Sophomore"
	mana, attack, health = 4, 4, 4
	index = "SCHOLOMANCE~Rogue~Minion~4~4~4~~Shifty Sophomore~Stealth"
	requireTarget, keyWord, description = False, "Stealth", "Stealth. Spellburst: Add a Combo card to your hand"
	name_CN = "调皮的大二学妹"
	poolIdentifier = "Combo Cards"
	@classmethod
	def generatePool(cls, pools):
		return "Combo Cards", [card for card in pools.ClassCards["Rogue"] if "~Combo~" in card.index]
		
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_ShiftySophomore(self)]
		
class Trig_ShiftySophomore(Spellburst):
	def text(self, CHN):
		return "法术迸发：将一张连击牌置入你的手牌" if CHN else "Spellburst: Add a Combo card to your hand"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.addCardtoHand(npchoice(self.rngPool("Combo Cards")), self.entity.ID)
		
			
class Steeldancer(Minion):
	Class, race, name = "Rogue,Warrior", "", "Steeldancer"
	mana, attack, health = 4, 4, 4
	index = "SCHOLOMANCE~Rogue,Warrior~Minion~4~4~4~~Steeldancer~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Summon a random minion with Cost equal to your weapons's Attack"
	name_CN = "钢铁舞者"
	poolIdentifier = "0-Cost Minions to summon"
	@classmethod
	def generatePool(cls, pools):
		return ["%d-Cost Minions to Summon" % cost for cost in pools.MinionsofCost.keys()], \
			   list(pools.MinionsofCost.values())
	
	def effCanTrig(self):
		self.effectViable = self.Game.availableWeapon(self.ID) is not None
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		weapon = self.Game.availableWeapon(self.ID)
		if weapon:
			cost = max(weapon.attack, 0) #假设计数过高，超出了费用范围，则取最高的可选费用
			while "%d-Cost Minions to Summon"%cost not in self.Game.RNGPools:
				cost -= 1
			self.summon(npchoice(self.rngPool("%d-Cost Minions to Summon"%cost))(self.Game, self.ID), self.pos+1)
		return None
		
		
class CuttingClass(Spell):
	Class, school, name = "Rogue,Warrior", "", "Cutting Class"
	requireTarget, mana = False, 5
	index = "SCHOLOMANCE~Rogue,Warrior~Spell~5~~Cutting Class"
	description = "Draw 2 cards. Costs (1) less per Attack of your weapon"
	name_CN = "劈砍课程"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsHand = [Trig_CuttingClass(self)]
		
	def selfManaChange(self):
		weapon = self.Game.availableWeapon(self.ID)
		if self.inHand and weapon:
			self.mana -= max(0, weapon.attack)
			self.mana = max(0, self.mana)
			
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.Game.Hand_Deck.drawCard(self.ID)
		self.Game.Hand_Deck.drawCard(self.ID)
		return None
		
class Trig_CuttingClass(TrigHand):
	def __init__(self, entity):
		super().__init__(entity, ["WeaponEquipped", "WeaponRemoved", "WeaponAttChanges"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.inHand and ID == self.entity.ID
		
	def text(self, CHN):
		return "当你的武器装备、失去或攻击力变化时，重新计算费用" if CHN else "Whenever you weapon equips, is lost, or change attack, recalculate the cost"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.Game.Manas.calcMana_Single(self.entity)
		
		
class DoctorKrastinov(Minion):
	Class, race, name = "Rogue,Warrior", "", "Doctor Krastinov"
	mana, attack, health = 5, 4, 4
	index = "SCHOLOMANCE~Rogue,Warrior~Minion~5~4~4~~Doctor Krastinov~Rush~Legendary"
	requireTarget, keyWord, description = False, "Rush", "Rush. Whenever this attacks, give your weapon +1/+1"
	name_CN = "卡斯迪诺夫教授"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_DoctorKrastinov(self)]
		
class Trig_DoctorKrastinov(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["MinionAttackingMinion", "MinionAttackingHero"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject == self.entity and self.entity.onBoard
		
	def text(self, CHN):
		return "每当该随从攻击时，使你的武器获得+1/+1" if CHN else "Whenever this attacks, give your weapon +1/+1"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		weapon = self.entity.Game.availableWeapon(self.entity.ID)
		if weapon: weapon.gainStat(1, 1)
		
"""Shaman Cards"""
class PrimordialStudies(Spell):
	Class, school, name = "Shaman,Mage", "Arcane", "Primordial Studies"
	requireTarget, mana = False, 1
	index = "SCHOLOMANCE~Shaman,Mage~Spell~1~Arcane~Primordial Studies"
	description = "Discover a Spell Damage minion. Your next one costs (1) less"
	name_CN = "始生研习"
	poolIdentifier = "Spell Damage Minions as Mage"
	@classmethod
	def generatePool(cls, pools):
		classCards = {s: [card for card in pools.ClassCards[s] if "~Spell Damage" in card.index] for s in pools.Classes}
		classCards["Neutral"] = [card for card in pools.NeutralCards if "~Spell Damage" in card.index]
		return ["Spell Damage Minions as "+Class for Class in pools.Classes], \
				[classCards[Class]+classCards["Neutral"] for Class in pools.Classes]
				
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if curGame.mode == 0:
			pool = tuple(self.rngPool("Spell Damage Minions as " + classforDiscover(self)))
			if curGame.guides:
				self.addCardtoHand(curGame.guides.pop(0), self.ID, byDiscover=True)
			else:
				if self.ID != self.Game.turn or "byOthers" in comment:
					self.addCardtoHand(npchoice(pool), self.ID, byDiscover=True)
				else:
					minions = npchoice(pool, 3, replace=False)
					curGame.options = [minion(curGame, self.ID) for minion in minions]
					curGame.Discover.startDiscover(self, pool)
		tempAura = GameManaAura_NextSpellDamageMinion1Less(self.Game, self.ID)
		self.Game.Manas.CardAuras.append(tempAura)
		tempAura.auraAppears()
		return None
		
	def discoverDecided(self, option, pool):
		self.Game.fixedGuides.append(type(option))
		self.addCardtoHand(option, self.ID, byDiscover=True)
		
class GameManaAura_NextSpellDamageMinion1Less(TempManaEffect):
	def __init__(self, Game, ID, changeby=0, changeto=-1):
		super().__init__(Game, ID, -1, -1)
		self.temporary = False
		
	def applicable(self, target):
		return target.ID == self.ID and target.type == "Minion" and target.keyWords["Spell Damage"] > 0
		
	def text(self, CHN):
		return "你的下一张法术伤害随从牌法力值消耗减少(1)点" if CHN else "Your next Spelldamage minion costs (1) less"
		
		
class DiligentNotetaker(Minion):
	Class, race, name = "Shaman", "", "Diligent Notetaker"
	mana, attack, health = 2, 2, 3
	index = "SCHOLOMANCE~Shaman~Minion~2~2~3~~Diligent Notetaker"
	requireTarget, keyWord, description = False, "", "Spellburst: Return the spell to your hand"
	name_CN = "笔记能手"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_DiligentNotetaker(self)]
		
#可以通过宣传牌确认是施放法术之后触发
class Trig_DiligentNotetaker(Spellburst):
	def text(self, CHN):
		return "法术迸发：将法术牌移回你的手牌" if CHN \
				else "Spellburst: Return the spell to your hand"
				
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.addCardtoHand(type(subject), self.entity.ID)
		
		
class RuneDagger(Weapon):
	Class, name, description = "Shaman", "Rune Dagger", "After your hero attacks, gain Spell Damage +1 this turn"
	mana, attack, durability = 2, 1, 3
	index = "SCHOLOMANCE~Shaman~Weapon~2~1~3~Rune Dagger"
	name_CN = "符文匕首"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_RuneDagger(self)]
		
class Trig_RuneDagger(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["HeroAttackedHero", "HeroAttackedMinion"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject == self.entity.Game.heroes[self.entity.ID] and self.entity.onBoard
		
	def text(self, CHN):
		return "在你的英雄攻击后，在本回合中获得法术伤害+1" if CHN \
				else "After your hero attacks, gain Spell Damage +1 this turn"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.Game.status[self.entity.ID]["Spell Damage"] += 1
		RuneDagger_Effect(self.entity.Game, self.entity.ID).connect()
		
class RuneDagger_Effect:
	def __init__(self, Game, ID):
		self.Game, self.ID = Game, ID
		self.card = RuneDagger(Game, ID)
		self.boost = 1
		
	def connect(self):
		trig = next((trig for trig in self.Game.turnEndTrigger if isinstance(trig, RuneDagger_Effect)), None)
		if trig:
			trig.boost += 1
			if trig.card.btn: trig.card.btn.trigAni(trig.boost)
		else:
			self.Game.turnEndTrigger.append(self)
			if self.Game.GUI: self.Game.GUI.heroZones[self.ID].addaTrig(self.card, text='1')
		
	def text(self, CHN):
		return "在本回合结束时，符文匕首的效果(法术伤害+1)消失" if CHN else "At the end of turn, Rune Dagger's effect(Spelldamage +2) expires"
		
	def turnEndTrigger(self):
		#Don't need to show the trig, as this is simply an effect expiring
		self.Game.status[self.ID]["Spell Damage"] -= 1
		try: self.Game.turnEndTrigger.remove(self)
		except: pass
		if self.Game.GUI: self.Game.GUI.heroZones[self.ID].removeaTrig(self.card)
	
	def createCopy(self, game):
		return type(self)(game, self.ID)
		
		
class TrickTotem(Minion):
	Class, race, name = "Shaman,Mage", "Totem", "Trick Totem"
	mana, attack, health = 2, 0, 3
	index = "SCHOLOMANCE~Shaman,Mage~Minion~2~0~3~Totem~Trick Totem"
	requireTarget, keyWord, description = False, "", "At the end of your turn, cast a random spell that costs (3) or less"
	name_CN = "戏法图腾"
	poolIdentifier = "Spells of <=3 Cost"
	@classmethod
	def generatePool(cls, pools):
		spells = []
		for Class in pools.Classes:
			spells += [card for card in pools.ClassCards[Class] if card.type == "Spell" and card.mana < 4]
		return "Spells of <=3 Cost", spells
		
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_TrickTotem(self)]
		
class Trig_TrickTotem(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["TurnEnds"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and ID == self.entity.ID
		
	def text(self, CHN):
		return "在你的回合结束时，随机施放一个法力值消耗小于或等于(3)的法术" if CHN \
				else "At the end of your turn, cast a random spell that costs (3) or less"
				
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		npchoice(self.rngPool("Spells of <=3 Cost"))(self.entity.Game, self.entity.ID).cast()
			
			
class InstructorFireheart(Minion):
	Class, race, name = "Shaman", "", "Instructor Fireheart"
	mana, attack, health = 3, 3, 3
	index = "SCHOLOMANCE~Shaman~Minion~3~3~3~~Instructor Fireheart~Battlecry~Legendary"
	requireTarget, keyWord, description = False, "", "Battlecry: Discover a spell that costs (1) or more. If you play it this turn, repeat this effect"
	name_CN = "导师火心"
	poolIdentifier = "Shaman Spells with 1 or more Cost"
	@classmethod
	def generatePool(cls, pools):
		return [Class+" Spells with 1 or more Cost" for Class in pools.Classes], \
				[[card for card in pools.ClassCards[Class] if card.type == "Spell" and card.mana > 0] for Class in pools.Classes]
				
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if self.ID == self.Game.turn:
			trig = InstructorFireheart_Effect(self.Game, self.ID)
			trig.connect()
			trig.effect(signal='', ID=0, subject=None, target=None, number=0, comment=comment, choice=0)
		return None
		
class InstructorFireheart_Effect:
	def __init__(self, Game, ID):
		self.Game, self.ID = Game, ID
		self.card = InstructorFireheart(Game, ID)
		self.spellDiscovered = None
		
	def connect(self):
		try: self.Game.trigsBoard[self.ID]["SpellBeenPlayed"].append(self)
		except: self.Game.trigsBoard[self.ID]["SpellBeenPlayed"] = [self]
		self.Game.turnEndTrigger.append(self)
		if self.Game.GUI: self.Game.GUI.heroZones[self.ID].addaTrig(self.card)
	
	def disconnect(self):
		try: self.Game.trigsBoard[self.ID]["SpellBeenPlayed"].remove(self)
		except: pass
		try: self.Game.turnEndTrigger.remove(self)
		except: pass
		if self.Game.GUI: self.Game.GUI.heroZones[self.ID].removeaTrig(self.card)
	
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject.ID == self.ID and subject == self.spellDiscovered
		
	def trig(self, signal, ID, subject, target, number, comment, choice=0):
		if self.canTrig(signal, ID, subject, target, number, comment):
			if self.Game.GUI: self.Game.GUI.showOffBoardTrig(self.card)
			self.effect(signal, ID, subject, target, number, comment)
			
	def text(self, CHN):
		return "本回合，每当你使用导师火心发现的法术，可再发现一张" if CHN \
				else "If you use the spell Discovered by Instructor Fireheart, Discover another"
				
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		curGame = self.Game
		if curGame.mode == 0:
			hero = curGame.heroes[self.ID]
			Class = hero.Class if hero.Class != "Neutral" else "Shaman"
			pool = tuple(self.rngPool("%s Spells with 1 or more Cost"%Class))
			if curGame.guides:
				spell = curGame.guides.pop(0)(curGame, self.ID)
				self.spellDiscovered = spell
				self.card.addCardtoHand(spell, self.ID, byDiscover=True)
			else:
				if isinstance(comment, str) and "byOthers" in comment:
					self.spellDiscovered = spell = npchoice(pool)(curGame, self.ID)
					self.card.addCardtoHand(spell, self.ID, byDiscover=True)
				else:
					spells = npchoice(pool, 3, replace=False)
					curGame.options = [spell(curGame, self.ID) for spell in spells]
					curGame.Discover.startDiscover(self, pool)
					
	def rngPool(self, identifier):
		return self.Game.RNGPools[identifier]
		
	def turnEndTrigger(self):
		self.disconnect()
		
	def discoverDecided(self, option, pool):
		self.spellDiscovered = option
		self.Game.fixedGuides.append(type(option))
		self.card.addCardtoHand(option, self.ID, byDiscover=True)
		
	def createCopy(self, game): #不是纯的只在回合结束时触发，需要完整的createCopy
		if self not in game.copiedObjs: #这个扳机没有被复制过
			trigCopy = type(self)(game, self.ID)
			if self.spellDiscovered:
				trigCopy.spellDiscovered = self.spellDiscovered.createCopy(game)
			game.copiedObjs[self] = trigCopy
			return trigCopy
		else: #一个扳机被复制过了，则其携带者也被复制过了
			return game.copiedObjs[self]
			
			
class MoltenBlast(Spell):
	Class, school, name = "Shaman", "Fire", "Molten Blast"
	requireTarget, mana = True, 3
	index = "SCHOLOMANCE~Shaman~Spell~3~Fire~Molten Blast"
	description = "Deal 2 damage. Summon that many 1/1 Elementals"
	name_CN = "岩浆爆裂"
	def text(self, CHN):
		damage = (2 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		return "造成%d点伤害，召唤相同数量 的1/1的元素"%damage if CHN \
				else "Deal %d damage. Summon that many 1/1 Elementals"%damage
				
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			damage = (2 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			self.dealsDamage(target, damage)
			self.summon([MoltenElemental(self.Game, self.ID) for i in range(damage)], (-1, "totheRightEnd"))
		return target
		
class MoltenElemental(Minion):
	Class, race, name = "Shaman", "Elemental", "Molten Elemental"
	mana, attack, health = 1, 1, 1
	index = "SCHOLOMANCE~Shaman~Minion~1~1~1~Elemental~Molten Elemental~Uncollectible"
	requireTarget, keyWord, description = False, "", ""
	name_CN = "熔岩元素"
	
	
class RasFrostwhisper(Minion):
	Class, race, name = "Shaman,Mage", "", "Ras Frostwhisper"
	mana, attack, health = 5, 3, 6
	index = "SCHOLOMANCE~Shaman,Mage~Minion~5~3~6~~Ras Frostwhisper~Legendary"
	requireTarget, keyWord, description = False, "", "At the end of turn, deal 1 damage to all enemies (improved by Spell Damage)"
	name_CN = "莱斯霜语"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_RasFrostwhisper(self)]
		
class Trig_RasFrostwhisper(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["TurnEnds"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and ID == self.entity.ID
		
	def text(self, CHN):
		damage = 1 + self.entity.countSpellDamage()
		return "在你的回合结束时，对所有敌人造成%d点伤害（受法术伤害加成影响）"%damage if CHN \
				else "At the end of turn, deal %d damage to all enemies (improved by Spell Damage)"%damage
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		minion = self.entity
		damage = 1 + minion.countSpellDamage()
		targets = [minion.Game.heroes[3-minion.ID]] + minion.Game.minionsonBoard(3-minion.ID)
		minion.dealsAOE(targets, [damage] * len(targets))
		
		
class TotemGoliath(Minion):
	Class, race, name = "Shaman", "Totem", "Totem Goliath"
	mana, attack, health = 5, 5, 5
	index = "SCHOLOMANCE~Shaman~Minion~5~5~5~Totem~Totem Goliath~Deathrattle"
	requireTarget, keyWord, description = False, "", "Deathrattle: Summon all four basic totems. Overload: (1)"
	name_CN = "图腾巨像"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.overload = 1
		self.deathrattles = [SummonAllBasicTotems(self)]
		
class SummonAllBasicTotems(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		minion, game = self.entity, self.entity.Game
		totems = [HealingTotem(game, minion.ID), SearingTotem(game, minion.ID), StoneclawTotem(game, minion.ID), StrengthTotem(game, minion.ID)]
		pos = (minion.pos, "totheRight") if minion in game.minions[minion.ID] else (-1, "totheRightEnd")
		minion.summon(totems, pos)
		
	def text(self, CHN):
		return "亡语：召唤全部四种基础图腾" if CHN else "Deathrattle: Summon all four basic totems"
		
		
class TidalWave(Spell):
	Class, school, name = "Shaman", "Nature", "Tidal Wave"
	requireTarget, mana = False, 8
	index = "SCHOLOMANCE~Shaman~Spell~8~Nature~Tidal Wave"
	description = "Lifesteal. Deal 3 damage to all minions"
	name_CN = "潮汐奔涌"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.keyWords["Lifesteal"] = 1
		
	def text(self, CHN):
		damage = (2 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		return "吸血。对所有随从造成%d点伤害"%damage if CHN else "Lifesteal. Deal %d damage to all minions"%damage
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		damage = (3 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		minions = self.Game.minionsonBoard(1) + self.Game.minionsonBoard(2)
		self.dealsAOE(minions, [damage]*len(minions))
		return None
		
		
"""Warlock Cards"""
class DemonicStudies(Spell):
	Class, school, name = "Warlock", "Shadow", "Demonic Studies"
	requireTarget, mana = False, 1
	index = "SCHOLOMANCE~Warlock~Spell~1~Shadow~Demonic Studies"
	description = "Discover a Demon. Your next one costs (1) less"
	name_CN = "恶魔研习"
	poolIdentifier = "Demons as Warlock"
	@classmethod
	def generatePool(cls, pools):
		classCards = {s: [] for s in pools.ClassesandNeutral}
		for card in pools.MinionswithRace["Demon"]:
			for Class in card.Class.split(','):
				classCards[Class].append(card)
		return ["Demons as " + Class for Class in pools.Classes], \
			   [classCards[Class] + classCards["Neutral"] for Class in pools.Classes]
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if curGame.mode == 0:
			pool = tuple(self.rngPool("Demons as " + classforDiscover(self)))
			if curGame.guides:
				self.addCardtoHand(curGame.guides.pop(0), self.ID, byDiscover=True)
			else:
				if self.ID != self.Game.turn or "byOthers" in comment:
					self.addCardtoHand(npchoice(pool), self.ID, byDiscover=True)
				else:
					minions = npchoice(pool, 3, replace=False)
					curGame.options = [minion(curGame, self.ID) for minion in minions]
					curGame.Discover.startDiscover(self, pool)
		tempAura = GameManaAura_NextDemon1Less(self.Game, self.ID)
		self.Game.Manas.CardAuras.append(tempAura)
		tempAura.auraAppears()
		return None
		
	def discoverDecided(self, option, pool):
		self.Game.fixedGuides.append(type(option))
		self.addCardtoHand(option, self.ID, byDiscover=True)
		
class GameManaAura_NextDemon1Less(TempManaEffect):
	def __init__(self, Game, ID, changeby=0, changeto=-1):
		super().__init__(Game, ID, -1, -1)
		self.temporary = False
		
	def applicable(self, target):
		return target.ID == self.ID and target.type == "Minion" and "Demon" in target.race
		
	def text(self, CHN):
		return "你的下一张恶魔牌的法力值消耗减少(1)点" if CHN else "Your next Demon costs (1) less"
		
class Felosophy(Spell):
	Class, school, name = "Warlock,Demon Hunter", "Fel", "Felosophy"
	requireTarget, mana = False, 1
	index = "SCHOLOMANCE~Warlock,Demon Hunter~Spell~1~Fel~Felosophy~Outcast"
	description = "Copy the lowest Cost Demon in your hand. Outcast: Give both +1/+1"
	name_CN = "邪能学说"
	def effCanTrig(self):
		self.effectViable = self.Game.Hand_Deck.outcastcanTrig(self)
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		demons, highestCost = [], npinf
		for i, card in enumerate(self.Game.Hand_Deck.hands[self.ID]):
			if card.type == "Minion" and "Demon" in card.race:
				if card.mana < highestCost: demons, highestCost = [i], card.mana
				elif card.mana == highestCost: demons.append(i)
		if demons:
			demon = npchoice(demons)
			Copy = demon.selfCopy(self.ID, self)
			self.addCardtoHand(Copy, self.ID)
			if posinHand == 0 or posinHand == -1:
				demon.buffDebuff(1, 1)
				Copy.buffDebuff(1, 1)
		return None
		
		
class SpiritJailer(Minion):
	Class, race, name = "Warlock,Demon Hunter", "Demon", "Spirit Jailer"
	mana, attack, health = 1, 1, 3
	index = "SCHOLOMANCE~Warlock,Demon Hunter~Minion~1~1~3~Demon~Spirit Jailer~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Shuffle 2 Soul Fragments into your deck"
	name_CN = "精魂狱卒"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.Game.Hand_Deck.shuffleintoDeck([SoulFragment(self.Game, self.ID) for i in range(2)], creator=self)
		return None
		
		
class BonewebEgg(Minion):
	Class, race, name = "Warlock", "", "Boneweb Egg"
	mana, attack, health = 2, 0, 2
	index = "SCHOLOMANCE~Warlock~Minion~2~0~2~~Boneweb Egg~Deathrattle"
	requireTarget, keyWord, description = False, "", "Deathrattle: Summon two 2/1 Spiders. If you discard this, trigger it Deathrattle"
	name_CN = "骨网之卵"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.deathrattles = [Summon2Spiders(self)]

	def whenDiscarded(self):
		for trig in self.deathrattles:
			trig.trig("TrigDeathrattle", self.ID, None, self, self.attack, "")
		
	def trigDeathrattles(self):
		for trig in self.deathrattles:
			trig.trig("TrigDeathrattle", self.ID, None, self, self.attack, "")
			
class Summon2Spiders(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		minion = self.entity
		pos = (minion.pos, "totheRight") if minion in minion.Game.minions[minion.ID] else (-1, "totheRightEnd")
		minion.summon([BonewebSpider(minion.Game, minion.ID) for i in range(2)], pos)
		
	def text(self, CHN):
		return "亡语：召唤两个2/1的蜘蛛" if CHN else "Deathrattle: Summon two 2/1 Spiders"
		
class BonewebSpider(Minion):
	Class, race, name = "Warlock", "Beast", "Boneweb Spider"
	mana, attack, health = 1, 2, 1
	index = "SCHOLOMANCE~Warlock~Minion~1~2~1~Beast~Boneweb Spider~Uncollectible"
	requireTarget, keyWord, description = False, "", ""
	name_CN = "骨网蜘蛛"
	
	
class SoulShear(Spell):
	Class, school, name = "Warlock,Demon Hunter", "Shadow", "Soul Shear"
	requireTarget, mana = True, 2
	index = "SCHOLOMANCE~Warlock,Demon Hunter~Spell~2~Shadow~Soul Shear"
	description = "Deal 3 damage to a minion. Shuffle 2 Soul Fragments into your deck"
	name_CN = "灵魂剥离"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			damage = (3 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			self.dealsDamage(target, damage)
			self.Game.Hand_Deck.shuffleintoDeck([SoulFragment(self.Game, self.ID) for i in range(2)], creator=self)
		return target
		
		
class SchoolSpirits(Spell):
	Class, school, name = "Warlock", "Shadow", "School Spirits"
	requireTarget, mana = False, 3
	index = "SCHOLOMANCE~Warlock~Spell~3~Shadow~School Spirits"
	description = "Deal 2 damage to all minions. Shuffle 2 Soul Fragments into your deck"
	name_CN = "校园精魂"
	def text(self, CHN):
		damage = (2 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		return "对所有随从造成%d点伤害。将两张灵魂残片洗入你的牌库"%damage if CHN \
				else "Deal %d damage to all minions. Shuffle 2 Soul Fragments into your deck"%damage
				
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		damage = (2 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		minions = self.Game.minionsonBoard(1) + self.Game.minionsonBoard(2)
		self.dealsAOE(minions, [damage]*len(minions))
		self.Game.Hand_Deck.shuffleintoDeck([SoulFragment(self.Game, self.ID) for i in range(2)], creator=self)
		return None
		
		
class ShadowlightScholar(Minion):
	Class, race, name = "Warlock", "", "Shadowlight Scholar"
	mana, attack, health = 3, 3, 4
	index = "SCHOLOMANCE~Warlock~Minion~3~3~4~~Shadowlight Scholar~Battlecry"
	requireTarget, keyWord, description = True, "", "Battlecry: Destroy a Soul Fragment in your deck to deal 3 damage"
	name_CN = "影光学者"
	
	def returnTrue(self, choice=0):
		for card in self.Game.Hand_Deck.decks[self.ID]:
			if isinstance(card, SoulFragment): return True
		return False
		
	def effCanTrig(self):
		self.effectViable = False
		for card in self.Game.Hand_Deck.decks[self.ID]:
			if isinstance(card, SoulFragment):
				self.effectViable = True
				break
				
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		for i, card in enumerate(self.Game.Hand_Deck.decks[self.ID]):
			if isinstance(card, SoulFragment) and target:
				self.Game.Hand_Deck.extractfromDeck(i, self.ID)
				self.dealsDamage(target, 3)
				break
		return target
		
		
class VoidDrinker(Minion):
	Class, race, name = "Warlock", "Demon", "Void Drinker"
	mana, attack, health = 5, 4, 5
	index = "SCHOLOMANCE~Warlock~Minion~5~4~5~Demon~Void Drinker~Taunt~Battlecry"
	requireTarget, keyWord, description = False, "Taunt", "Taunt. Battlecry: Destroy a Soul Fragment in your deck to gain +3/+3"
	name_CN = "虚空吸食者"
	
	def effCanTrig(self):
		self.effectViable = False
		for card in self.Game.Hand_Deck.decks[self.ID]:
			if isinstance(card, SoulFragment):
				self.effectViable = True
				break
				
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		for i, card in enumerate(self.Game.Hand_Deck.decks[self.ID]):
			if isinstance(card, SoulFragment):
				self.Game.Hand_Deck.extractfromDeck(i, self.ID)
				self.buffDebuff(3, 3)
				break
		return None
		
		
class SoulciologistMalicia(Minion):
	Class, race, name = "Warlock,Demon Hunter", "", "Soulciologist Malicia"
	mana, attack, health = 7, 5, 5
	index = "SCHOLOMANCE~Warlock,Demon Hunter~Minion~7~5~5~~Soulciologist Malicia~Battlecry~Legendary"
	requireTarget, keyWord, description = False, "", "Battlecry: For each Soul Fragment in your deck, summon a 3/3 Soul with Rush"
	name_CN = "灵魂学家玛丽希亚"
	
	def effCanTrig(self):
		self.effectViable = False
		for card in self.Game.Hand_Deck.decks[self.ID]:
			if isinstance(card, SoulFragment): self.effectViable = True
			
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		num = 0
		for card in self.Game.Hand_Deck.decks[self.ID]:
			if isinstance(card, SoulFragment): num += 1
		minions = [ReleasedSoul(self.Game, self.ID) for i in range(num)]
		#假设召唤的衍生物都在右侧
		self.summon(minions, (self.pos, "totheRight"))
		return None
	
class ReleasedSoul(Minion):
	Class, race, name = "Warlock,Demon Hunter", "", "Released Soul"
	mana, attack, health = 3, 3, 3
	index = "SCHOLOMANCE~Warlock,Demon Hunter~Minion~3~3~3~~Released Soul~Rush~Uncollectible"
	requireTarget, keyWord, description = False, "Rush", "Rush"
	name_CN = "被释放的灵魂"
	
	
class ArchwitchWillow(Minion):
	Class, race, name = "Warlock", "", "Archwitch Willow"
	mana, attack, health = 8, 5, 5
	index = "SCHOLOMANCE~Warlock~Minion~8~5~5~~Archwitch Willow~Battlecry~Legendary"
	requireTarget, keyWord, description = False, "", "Battlecry: Summon a random Demon from your hand and deck"
	name_CN = "高阶女巫维洛"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		refMinion = self
		demonsfromHand = [i for i, card in enumerate(self.Game.Hand_Deck.hands[self.ID]) if card.type == "Minion" and "Demon" in card.race]
		if demonsfromHand and self.Game.space(self.ID) > 0:
			refMinion = self.Game.summonfrom(npchoice(demonsfromHand), self.ID, refMinion.pos+1, self, source='H')
		
		demonsfromDeck = [i for i, card in enumerate(self.Game.Hand_Deck.decks[self.ID]) if card.type == "Minion" and "Demon" in card.race]
		if demonsfromDeck and self.Game.space(self.ID) > 0:
			self.Game.summonfrom(npchoice(demonsfromDeck), self.ID, refMinion.pos+1, self, source='D')
		return None
		
		
"""Warrior Cards"""
class AthleticStudies(Spell):
	Class, school, name = "Warrior", "", "Athletic Studies"
	requireTarget, mana = False, 1
	index = "SCHOLOMANCE~Warrior~Spell~1~~Athletic Studies"
	description = "Discover a Rush minion. Your next one costs (1) less"
	name_CN = "体能研习"
	poolIdentifier = "Rush Minions as Warrior"
	@classmethod
	def generatePool(cls, pools):
		classCards = {s: [card for card in pools.ClassCards[s] if "~Rush" in card.index] for s in pools.Classes}
		classCards["Neutral"] = [card for card in pools.NeutralCards if "~Rush" in card.index]
		return ["Rush Minions as "+Class for Class in pools.Classes], \
				[classCards[Class]+classCards["Neutral"] for Class in pools.Classes]
				
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if curGame.mode == 0:
			pool = tuple(self.rngPool("Rush Minions as "+classforDiscover(self)))
			if curGame.guides:
				self.addCardtoHand(curGame.guides.pop(0), self.ID, byDiscover=True)
			else:
				if self.ID != self.Game.turn or "byOthers" in comment:
					self.addCardtoHand(npchoice(pool), self.ID, byDiscover=True)
				else:
					minions = npchoice(pool, 3, replace=False)
					curGame.options = [minion(curGame, self.ID) for minion in minions]
					curGame.Discover.startDiscover(self, pool)
		tempAura = GameManaAura_NextRushMinion1Less(self.Game, self.ID)
		self.Game.Manas.CardAuras.append(tempAura)
		tempAura.auraAppears()
		return None
		
	def discoverDecided(self, option, pool):
		self.Game.fixedGuides.append(type(option))
		self.addCardtoHand(option, self.ID, byDiscover=True)
		
class GameManaAura_NextRushMinion1Less(TempManaEffect):
	def __init__(self, Game, ID, changeby=0, changeto=-1):
		super().__init__(Game, ID, -1, -1)
		self.temporary = False
		
	def applicable(self, target):
		return target.ID == self.ID and target.type == "Minion" and target.keyWords["Rush"] > 0
		
		
class ShieldofHonor(Spell):
	Class, school, name = "Warrior,Paladin", "Holy", "Shield of Honor"
	requireTarget, mana = True, 1
	index = "SCHOLOMANCE~Warrior,Paladin~Spell~1~Holy~Shield of Honor"
	description = "Give a damaged minion +3 Attack and Divine Shield"
	name_CN = "荣誉护盾"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard and target.health < target.health_max
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			target.buffDebuff(3, 0)
			target.getsStatus("Divine Shield")
		return target
		
		
class InFormation(Spell):
	Class, school, name = "Warrior", "", "In Formation!"
	requireTarget, mana = False, 2
	index = "SCHOLOMANCE~Warrior~Spell~2~~In Formation!"
	description = "Add 2 random Taunt minions to your hand"
	name_CN = "保持阵型"
	poolIdentifier = "Taunt Minions"
	@classmethod
	def generatePool(cls, pools):
		minions = [card for card in pools.NeutralCards if "~Taunt" in card.index]
		for Class in pools.Classes:
			minions += [card for card in pools.ClassCards[Class] if "~Taunt" in card.index]
		return "Taunt Minions", minions
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.addCardtoHand(npchoice(self.rngPool("Taunt Minions"), 2, replace=True), self.ID)
		return None
		
		
class CeremonialMaul(Weapon):
	Class, name, description = "Warrior,Paladin", "Ceremonial Maul", "Spellburst: Summon a student with Taunt and stats equal to the spell's Cost"
	mana, attack, durability = 3, 2, 2
	index = "SCHOLOMANCE~Warrior,Paladin~Weapon~3~2~2~Ceremonial Maul"
	name_CN = "仪式重槌"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_CeremonialMaul(self)]
		
class Trig_CeremonialMaul(Spellburst):
	def text(self, CHN):
		return "法术迸发：召唤一个属性值等同于法术法力值消耗的并具有嘲讽的学生" if CHN \
				else "Spellburst: Summon a student with Taunt and stats equal to the spell's Cost"
				
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		game, stat = self.entity.Game, number
		if stat and game.space(self.entity.ID):
			cost = min(stat, 10)
			newIndex = "SCHOLOMANCE~Warrior,Paladin~%d~%d~%d~Minion~~Honor Student~Taunt~Uncollectible"%(cost, stat, stat)
			subclass = type("HonorStudent__%d"%stat, (HonorStudent, ),
							{"mana": cost, "attack": stat, "health": stat,
							"index": newIndex}
							)
			self.entity.summon(subclass(game, self.entity.ID), -1)
			
class HonorStudent(Minion):
	Class, race, name = "Warrior,Paladin", "", "Honor Student"
	mana, attack, health = 1, 1, 1
	index = "SCHOLOMANCE~Warrior,Paladin~Minion~1~1~1~~Honor Student~Taunt~Uncollectible"
	requireTarget, keyWord, description = False, "Taunt", "Taunt"
	name_CN = "仪仗学员"
	
	
class LordBarov(Minion):
	Class, race, name = "Warrior,Paladin", "", "Lord Barov"
	mana, attack, health = 3, 3, 2
	index = "SCHOLOMANCE~Warrior,Paladin~Minion~3~3~2~~Lord Barov~Battlecry~Deathrattle"
	requireTarget, keyWord, description = False, "", "Battlecry: Set the Health of all other minions to 1. Deathrattle: Deal 1 damage to all other minions"
	name_CN = "巴罗夫领主"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.deathrattles = [Deal1DamagetoAllMinions(self)]
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		for minion in self.Game.minionsonBoard(self.ID, self) + self.Game.minionsonBoard(3-self.ID):
			minion.statReset(False, 1)
		return None
		
class Deal1DamagetoAllMinions(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		minions = self.entity.Game.minionsonBoard(self.entity.ID) + self.entity.Game.minionsonBoard(3-self.entity.ID)
		self.entity.dealsAOE(minions, [1 for i in range(len(minions))])
		
	def text(self, CHN):
		return "亡语：对所有随从造成1点伤害" if CHN else "Deathrattle: Deal 1 damage to all minions"
		
		
class Playmaker(Minion):
	Class, race, name = "Warrior", "", "Playmaker"
	mana, attack, health = 3, 4, 3
	index = "SCHOLOMANCE~Warrior~Minion~3~4~3~~Playmaker"
	requireTarget, keyWord, description = False, "", "After you play a Rush minion, summon a copy with 1 Health remaining"
	name_CN = "团队核心"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_Playmaker(self)]
		
class Trig_Playmaker(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["MinionBeenPlayed"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject.ID == self.entity.ID and subject.keyWords["Rush"] > 0
		
	def text(self, CHN):
		return "在你使用一张突袭随从牌后，召唤一个剩余生命值为1的复制" if CHN else "After you play a Rush minion, summon a copy with 1 Health remaining"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		Copy = subject.selfCopy(self.entity.ID, self.entity)
		Copy.health = 1
		self.entity.summon(Copy, self.entity.pos+1)
		
		
class ReapersScythe(Weapon):
	Class, name, description = "Warrior", "Reaper's Scythe", "Spellburst: Also damages adjacent minions this turn"
	mana, attack, durability = 4, 4, 2
	index = "SCHOLOMANCE~Warrior~Weapon~4~4~2~Reaper's Scythe"
	name_CN = "收割之镰"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_ReapersScythe(self)]
		
class Trig_ReapersScythe(Spellburst):
	def text(self, CHN):
		return "法术迸发：在本回合中同时对攻击目标相邻的随从造成伤害" if CHN else "Spellburst: Also damages adjacent minions this turn"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.marks["Sweep"] += 1
		trig = Trig_SweepThisTurn(self.entity)
		self.entity.trigsBoard.append(trig)
		trig.connect()
		
class Trig_SweepThisTurn(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["TurnEnds"])
		self.inherent = False
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard #Even if the current turn is not minion's owner's turn
		
	def text(self, CHN):
		return "回合结束时，失去“同时对攻击目标相邻的随从造成伤害”" if CHN \
				else "At the end of turn, lose 'Also damages adjacent minions'"
				
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.disconnect()
		try: self.entity.trigsBoard.remove(self)
		except: pass
		self.entity.marks["Sweep"] -= 1
		
		
class Commencement(Spell):
	Class, school, name = "Warrior,Paladin", "", "Commencement"
	requireTarget, mana = False, 7
	index = "SCHOLOMANCE~Warrior,Paladin~Spell~7~~Commencement"
	description = "Summon a minion from your deck. Give it Taunt and Divine Shield"
	name_CN = "毕业仪式"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		minions = [i for i, card in enumerate(self.Game.Hand_Deck.decks[self.ID]) if card.type == "Minion"]
		if minions:
			minion = self.Game.summonfrom(npchoice(minions), self.ID, -1, self, source='D')
			minion.getsStatus("Taunt")
			minion.getsStatus("Divine Shield")
		return None
		
		
class Troublemaker(Minion):
	Class, race, name = "Warrior", "", "Troublemaker"
	mana, attack, health = 8, 6, 8
	index = "SCHOLOMANCE~Warrior~Minion~8~6~8~~Troublemaker"
	requireTarget, keyWord, description = False, "", "At the end of your turn, summon two 3/3 Ruffians that attack random enemies"
	name_CN = "问题学生"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_Troublemaker(self)]
		
class Trig_Troublemaker(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["TurnEnds"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and ID == self.entity.ID
		
	def text(self, CHN):
		return "在你的回合结束时，召唤两个3/3的无赖并使其攻击随机敌人" if CHN \
				else "At the end of your turn, summon two 3/3 Ruffians that attack random enemies"
				
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		curGame = self.entity.Game
		ruffians = [Ruffian(curGame, self.entity.ID) for i in range(2)]
		self.entity.summon(ruffians, (self.entity.pos, "leftandRight"))
		for num in range(2):
			objs = curGame.charsAlive(3-self.entity.ID)
			if ruffians[num].onBoard and not ruffians[num].dead and ruffians[num].health > 0 and objs:
				curGame.battle(ruffians[num], npchoice(objs), verifySelectable=False, resolveDeath=False)
				
class Ruffian(Minion):
	Class, race, name = "Warrior", "", "Ruffian"
	mana, attack, health = 3, 3, 3
	index = "SCHOLOMANCE~Warrior~Minion~3~3~3~~Ruffian~Uncollectible"
	requireTarget, keyWord, description = False, "", ""
	name_CN = "无赖"
	
#https://www.bilibili.com/video/BV1Uy4y1C73o 机制测试
#血骨傀儡的亡语的实质是在随从死亡并进行了身材重置之后检测其身材，然后召唤一个相同的身材的随从。之后再把这个随从的身材白字改为检测 到的身材的-1/-1
#召唤的3/3血骨傀儡在场上有卡德加的时候会召唤2/2和3/3（卡德加复制得到的那个随从没有来得及再执行-1/-1）
#buff得到的身材在进入墓地时会清除，但是场上的随从因为装死等效果直接触发时是可以直接检测到buff的身材的，比如20/19的血骨傀儡可以因为装死召唤一个19/18
#其他随从获得了血骨傀儡的身材之后可以召唤自身而不是血骨傀儡，如送葬者
#与水晶核心的互动：4/4的血骨傀儡在死亡后先召唤4/4的血骨傀儡，与水晶核心作用，然后被这个亡语-1/-1,形成一个3/3。这个3/3死亡后被检测，预定最终 被变成2/2先召唤3/3
	#这个3/3被水晶核心变成4/4然后再被调成2/2
#血骨傀儡的亡语只会处理第一个召唤出来的随从的身材，如果有翻倍召唤，则其他复制是原身材
#在场上触发亡语时，检测的是满状态的生命值，即使受伤也是从最大生命值计算
class Rattlegore(Minion):
	Class, race, name = "Warrior", "", "Rattlegore"
	mana, attack, health = 9, 9, 9
	index = "SCHOLOMANCE~Warrior~Minion~9~9~9~~Rattlegore~Deathrattle~Legendary"
	requireTarget, keyWord, description = False, "", "Deathrattle: Resummon this with -1/-1"
	name_CN = "血骨傀儡"
	
#	def __init__(self, Game, ID):
#		super().__init__(Game, ID)
#		self.deathrattles = [ResummonSmallerSelf(self)]
#
#"""死亡歌者安布拉的扳机会在血骨傀儡的亡语把召唤的随从的身材-1/-1之前触发，所以这个-1/-1过程应当在"MinionSummoned"之后进行 """
#class ResummonSmallerSelf(Deathrattle_Minion):
#	def effect(self, signal, ID, subject, target, number, comment, choice=0):
#		minion, ID = self.entity, self.entity.ID
#		if minion.Game.space(ID) > 0: #如果场上空间不足则直接跳过
#			cardType = type(minion)
#			newMinion = cardType(minion.Game, ID)
#			if signal[0] == 'M': #"MinionDies"
#				att_0, health_0 = minion.attack, minion.health #随从死亡后召唤随从时，读取其白字
#				if health_0 > 1:
#					newAtt_0, newHealth_0 = max(att_0 - 1, 0), health_0 - 1
#					words = newMinion.index.split('~')
#					words[4], words[5] = newAtt_0, newHealth_0
#					if "Uncollectible" not in words:
#						words.append("Uncollectible")
#					newIndex = [words[0]]
#					for word in words: newIndex += '~'+words
#					if "Mutable" in cardType.__name__:
#						newTypeName =
#
#					subclass = type(cardType.__name__+str(handSize), (cardType, ),
#									{"mana": cost, "attack": handSize, "health": handSize,
#									"index": newIndex}
#									)
#					newMinion.attack_0 = newMinion.attack = newMinion.attack_Enchant = att_0
#					newMinion.health_0 = newMinion.health = newMinion.health_max = health_0
#					minion.Game.summon(newMinion, minion.pos+1, minion)
#					delta_Att_0, delta_Health_0 = newMinion.attack_0 - newAtt_0, newMinion.health_0 - newHealth_0
#					#白字需要变化，然后根据目标白字与当前白字之间的差值加减攻击力和生命值
#					newMinion.attack_0, newMinion.health_0 = newAtt_0, newHealth_0 #白字仍然可以直接设置
#					newMinion.attack -= delta_Att_0
#					newMinion.attack_Enchant -= delta_Att_0
#					newMinion.health -= delta_Health_0
#					newMinion.health_max -= delta_Health_0
#
#			elif minion.health > 1: #"TrigDeathrattle"
#				#假设在场上触发的亡语会直接确定下一个随从的-1/-1身材，而不再进行后续的-1/-1
#				newMinion.attack_0 = newMinion.attack = newMinion.attack_Enchant = max(minion.attack - 1, 0)
#				newMinion.health_0 = newMinion.health = newMinion.health_max = minion.health - 1
#				newMinion = minion.Game.summon(newMinion, minion.pos+1, minion)
#

Academy_Cards = [#Neutral cards
				TransferStudent, TransferStudent_Ogrimmar, TransferStudent_Stormwind, TransferStudent_FourWindValley, TransferStudent_Stranglethorn,
				TransferStudent_Outlands, TransferStudent_Academy, TransferStudent_Darkmoon, TransferStudent_Darkmoon_Corrupt,
				DeskImp, AnimatedBroomstick, IntrepidInitiate, PenFlinger, SphereofSapience, TourGuide, CultNeophyte, ManafeederPanthara, SneakyDelinquent, SpectralDelinquent, VoraciousReader,
				Wandmaker, EducatedElekk, EnchantedCauldron, RobesofProtection, CrimsonHothead, DivineRager, FishyFlyer, SpectralFlyer, LorekeeperPolkelt, WretchedTutor, HeadmasterKelThuzad, LakeThresher, Ogremancer,
				RisenSkeleton, StewardofScrolls, Vectus, PlaguedHatchling, OnyxMagescribe, SmugSenior, SpectralSenior, SorcerousSubstitute, KeymasterAlabaster, PlaguedProtodrake,
				#Demon Hunter Cards
				DemonCompanion, Reffuh, Kolek, Shima, DoubleJump, TrueaimCrescent, AceHunterKreen, Magehunter, ShardshatterMystic, Glide, Marrowslicer, StarStudentStelina, VilefiendTrainer, SnarlingVilefiend,
				BloodHerald, SoulshardLapidary, CycleofHatred, SpiritofVengeance, FelGuardians, SoulfedFelhound, AncientVoidHound,
				#Druid cards
				LightningBloom, Gibberling, NatureStudies, PartnerAssignment, SpeakerGidra, Groundskeeper, TwilightRunner, ForestWardenOmu, RunicCarvings, TreantTotem, SurvivaloftheFittest, 
				#Hunter cards
				AdorableInfestation, MarsuulCub, CarrionStudies, Overwhelm, Wolpertinger, BloatedPython, HaplessHandler, ProfessorSlate, ShandoWildclaw, KroluskBarkstripper, TeachersPet, GuardianAnimals, 
				#Mage cards
				BrainFreeze, LabPartner, WandThief, CramSession, Combustion, Firebrand, PotionofIllusion, JandiceBarov, MozakiMasterDuelist, WyrmWeaver, 
				#Paladin cards
				FirstDayofSchool, WaveofApathy, ArgentBraggart, GiftofLuminance, GoodyTwoShields, HighAbbessAlura, BlessingofAuthority, DevoutPupil, JudiciousJunior, TuralyontheTenured,
				#Priest cards
				RaiseDead, DraconicStudies, FrazzledFreshman, MindrenderIllucia, PowerWordFeast, BrittleboneDestroyer, CabalAcolyte, DisciplinarianGandling, FailedStudent, Initiation, FleshGiant, 
				#Rogue cards
				SecretPassage, Plagiarize, Coerce, SelfSharpeningSword, VulperaToxinblade, InfiltratorLilian, ForsakenLilian, ShiftySophomore, Steeldancer, CuttingClass, DoctorKrastinov, 
				#Shaman cards
				DevolvingMissiles, PrimordialStudies, DiligentNotetaker, RuneDagger, TrickTotem, InstructorFireheart, MoltenBlast, MoltenElemental, RasFrostwhisper, TotemGoliath, TidalWave, 
				#Warlock cards
				SoulFragment, DemonicStudies, Felosophy, SpiritJailer, BonewebEgg, BonewebSpider, SoulShear, SchoolSpirits, ShadowlightScholar, VoidDrinker, SoulciologistMalicia, ReleasedSoul, ArchwitchWillow, 
				#Warrior cards
				AthleticStudies, ShieldofHonor, InFormation, CeremonialMaul, HonorStudent, LordBarov, Playmaker, ReapersScythe, Commencement, Troublemaker, Ruffian, Rattlegore,
				]
				
Academy_Cards_Collectible = [
							TransferStudent, DeskImp, AnimatedBroomstick, IntrepidInitiate, PenFlinger, SphereofSapience, TourGuide, CultNeophyte, ManafeederPanthara, SneakyDelinquent, VoraciousReader, Wandmaker, EducatedElekk,
							EnchantedCauldron, RobesofProtection, CrimsonHothead, DivineRager, FishyFlyer, LorekeeperPolkelt, WretchedTutor, HeadmasterKelThuzad, LakeThresher, Ogremancer, StewardofScrolls, Vectus,
							OnyxMagescribe, SmugSenior, SorcerousSubstitute, KeymasterAlabaster, PlaguedProtodrake,
							#Demon Hunter
							DemonCompanion, DoubleJump, TrueaimCrescent, AceHunterKreen, Magehunter, ShardshatterMystic, Glide, Marrowslicer, StarStudentStelina, VilefiendTrainer,
							BloodHerald, SoulshardLapidary, CycleofHatred, FelGuardians, AncientVoidHound,
							#Druid
							LightningBloom, Gibberling, NatureStudies, PartnerAssignment, SpeakerGidra, Groundskeeper, TwilightRunner, ForestWardenOmu, RunicCarvings, SurvivaloftheFittest,
							#Hunter
							AdorableInfestation, CarrionStudies, Overwhelm, Wolpertinger, BloatedPython, ProfessorSlate, ShandoWildclaw, KroluskBarkstripper, TeachersPet, GuardianAnimals,
							#Mage
							BrainFreeze, LabPartner, WandThief, CramSession, Combustion, Firebrand, PotionofIllusion, JandiceBarov, MozakiMasterDuelist, WyrmWeaver,
							#Paladin
							FirstDayofSchool, WaveofApathy, ArgentBraggart, GiftofLuminance, GoodyTwoShields, HighAbbessAlura, BlessingofAuthority, DevoutPupil, JudiciousJunior, TuralyontheTenured,
							#Priest
							RaiseDead, DraconicStudies, FrazzledFreshman, MindrenderIllucia, PowerWordFeast, BrittleboneDestroyer, CabalAcolyte, DisciplinarianGandling, Initiation, FleshGiant,
							#Rogue
							SecretPassage, Plagiarize, Coerce, SelfSharpeningSword, VulperaToxinblade, InfiltratorLilian, ShiftySophomore, Steeldancer, CuttingClass, DoctorKrastinov,
							#Shaman
							DevolvingMissiles, PrimordialStudies, DiligentNotetaker, RuneDagger, TrickTotem, InstructorFireheart, MoltenBlast, RasFrostwhisper, TotemGoliath, TidalWave,
							#Warlock
							DemonicStudies, Felosophy, SpiritJailer, BonewebEgg, SoulShear, SchoolSpirits, ShadowlightScholar, VoidDrinker, SoulciologistMalicia, ArchwitchWillow,
							#Warrior
							AthleticStudies, ShieldofHonor, InFormation, CeremonialMaul, LordBarov, Playmaker, ReapersScythe, Commencement, Troublemaker, Rattlegore,
							]