from CardTypes import *
from Triggers_Auras import *
from numpy.random import choice as npchoice
from numpy.random import randint as nprandint
from numpy.random import shuffle as npshuffle
from numpy import inf as npinf

from Basic import Claw, ArcaneMissiles, TruesilverChampion, Trig_Charge, HealingTotem, SearingTotem, StoneclawTotem, WrathofAirTotem
from Classic import ManaWyrm
from AcrossPacks import Lackeys
from Uldum import PlagueofDeath, PlagueofMadness, PlagueofMurlocs, PlagueofFlames, PlagueofWrath
from Outlands import Minion_Dormantfor2turns

"""Scholomance Academy"""
#可以通过宣传牌确认是施放法术之后触发
class Spellburst(TrigBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["SpellBeenPlayed"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject.ID == self.entity.ID
		
	def trig(self, signal, ID, subject, target, number, comment, choice=0):
		if self.canTrig(signal, ID, subject, target, number, comment):
			if self.entity.Game.GUI:
				self.entity.Game.GUI.trigBlink(self.entity)
			self.disconnect()
			try: self.entity.trigsBoard.remove(self)
			except: pass
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
	index = "Academy~Neutral~Minion~2~2~2~None~Transfer Student"
	requireTarget, keyWord, description = False, "", "This has different effects based on which game board you're on"
	
class TransferStudent_Ogrimmar(Minion):
	Class, race, name = "Neutral", "", "Transfer Student"
	mana, attack, health = 2, 2, 2
	index = "Academy~Neutral~Minion~2~2~2~None~Transfer Student~Battlecry"
	requireTarget, keyWord, description = True, "", "Battlecry: Deal 2 damage"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			self.dealsDamage(target, 2)
		return target
		
class TransferStudent_Stormwind(Minion):
	Class, race, name = "Neutral", "", "Transfer Student"
	mana, attack, health = 2, 2, 2
	index = "Academy~Neutral~Minion~2~2~2~None~Transfer Student~Divine Shield"
	requireTarget, keyWord, description = False, "Divine Shield", "Divine Shield"
	
class TransferStudent_Stranglethorn(Minion):
	Class, race, name = "Neutral", "", "Transfer Student"
	mana, attack, health = 2, 2, 2
	index = "Academy~Neutral~Minion~2~2~2~None~Transfer Student~Stealth~Poisonous"
	requireTarget, keyWord, description = False, "Stealth,Poisonous", "Stealth, Poisonous"
	
class TransferStudent_FourWindValley(Minion):
	Class, race, name = "Neutral", "", "Transfer Student"
	mana, attack, health = 2, 2, 2
	index = "Academy~Neutral~Minion~2~2~2~None~Transfer Student~Battlecry"
	requireTarget, keyWord, description = True, "", "Battlecry: Give a friendly minion +1/+2"
	
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
	index = "Academy~Neutral~Minion~2~2~2~None~Transfer Student~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Add a Lackey to your hand"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if curGame.mode == 0:
			if curGame.guides:
				lackey = curGame.guides.pop(0)
			else:
				lackey = npchoice(Lackeys)
				curGame.fixedGuides.append(lackey)
			curGame.Hand_Deck.addCardtoHand(lackey, self.ID, "type")
		return None
		
class TransferStudent_UldumDesert(Minion):
	Class, race, name = "Neutral", "", "Transfer Student"
	mana, attack, health = 2, 2, 2
	index = "Academy~Neutral~Minion~2~2~2~None~Transfer Student~Reborn"
	requireTarget, keyWord, description = False, "Reborn", "Reborn"
	
Plagues = [PlagueofDeath, PlagueofMadness, PlagueofMurlocs, PlagueofFlames, PlagueofWrath]

class TransferStudent_UldumOasis(Minion):
	Class, race, name = "Neutral", "", "Transfer Student"
	mana, attack, health = 2, 2, 2
	index = "Academy~Neutral~Minion~2~2~2~None~Transfer Student~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Add a Uldum plague card to your hand"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if curGame.mode == 0:
			if curGame.guides:
				card = curGame.guides.pop(0)
			else:
				card = npchoice(Plagues)
				curGame.fixedGuides.append(Plagues)
			curGame.Hand_Deck.addCardtoHand(card, self.ID, "type")
		return None
		
class TransferStudent_Dragons(Minion):
	Class, race, name = "Neutral", "", "Transfer Student"
	mana, attack, health = 2, 2, 2
	index = "Academy~Neutral~Minion~2~2~2~None~Transfer Student~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Discover a Dragon"
	poolIdentifier = "Dragons as Druid"
	@classmethod
	def generatePool(cls, Game):
		classCards = {s : [] for s in Game.ClassesandNeutral}
		for key, value in Game.MinionswithRace["Dragon"].items():
			classCards[key.split('~')[1]].append(value)
		return ["Dragons as "+Class for Class in Game.Classes], \
				[classCards[Class]+classCards["Neutral"] for Class in Game.Classes]
				
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if self.ID == curGame.turn:
			if curGame.mode == 0:
				if curGame.guides:
					curGame.Hand_Deck.addCardtoHand(curGame.guides.pop(0), self.ID, "type", byDiscover=True)
				else:
					key = "Dragons as "+classforDiscover(self)
					if "byOthers" in comment:
						dragon = npchoice(self.rngPool(key))
						curGame.fixedGuides.append(dragon)
						curGame.Hand_Deck.addCardtoHand(dragon, self.ID, "type", byDiscover=True)
					else:
						dragons = npchoice(self.rngPool(key), 3, replace=False)
						curGame.options = [dragon(curGame, self.ID) for dragon in dragons]
						curGame.Discover.startDiscover(self)
		return None
		
	def discoverDecided(self, option, info):
		self.Game.fixedGuides.append(type(option))
		self.Game.Hand_Deck.addCardtoHand(option, self.ID, byDiscover=True)
		
class TransferStudent_Outlands(Minion_Dormantfor2turns):
	Class, race, name = "Neutral", "", "Transfer Student"
	mana, attack, health = 2, 2, 2
	index = "Academy~Neutral~Minion~2~2~2~None~Transfer Student~Battlecry"
	requireTarget, keyWord, description = False, "", "Dormant for 2 turns. When this awakens, deal 3 damage to 2 random enemy minions"
	
	def awakenEffect(self):
		curGame = self.Game
		minions = curGame.minionsAlive(3-self.ID)
		if minions:
			if curGame.mode == 0:
				if curGame.guides:
					minions = [curGame.minions[3-self.ID][i] for i in curGame.guides.pop(0)]
				else:
					minions = list(npchoice(minions, min(2, len(minions)), replace=False))
					curGame.fixedGuides.append(tuple([minion.pos for minion in minions]))
				self.dealsAOE(minions, [3]*len(minions))
				
class TransferStudent_Academy(Minion):
	Class, race, name = "Neutral", "", "Transfer Student"
	mana, attack, health = 2, 2, 2
	index = "Academy~Neutral~Minion~2~2~2~None~Transfer Student~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Add a random Dual Class card to your hand"
	poolIdentifier = "Dual Class Cards"
	@classmethod
	def generatePool(cls, Game):
		cards = []
		for Class in Game.Classes:
			cards += [value for key, value in Game.ClassCards[Class].items() if "," in key.split('~')[1]]
		return "Dual Class Cards", cards
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if curGame.mode == 0:
			if curGame.guides:
				card = curGame.guides.pop(0)
			else:
				card = npchoice(self.rngPool("Dual Class Cards"))
				curGame.fixedGuides.append(card)
			curGame.Hand_Deck.addCardtoHand(card, self.ID, "type")
		return None
		
class TransferStudent_Darkmoon(Minion):
	Class, race, name = "Neutral", "", "Transfer Student"
	mana, attack, health = 2, 2, 2
	index = "Academy~Neutral~Minion~2~2~2~None~Transfer Student"
	requireTarget, keyWord, description = False, "", "Corrupt: Gain +2/+2"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsHand = [Trig_Corrupt(self, TransferStudent_Darkmoon_Corrupt)] #只有在手牌中才会升级
		
class TransferStudent_Darkmoon_Corrupt(Minion):
	Class, race, name = "Neutral", "", "Transfer Student"
	mana, attack, health = 2, 4, 4
	index = "Academy~Neutral~Minion~2~4~4~None~Transfer Student~Corrupted~Uncollectible"
	requireTarget, keyWord, description = False, "", ""
	
	
"""Mana 0 cards"""
class DeskImp(Minion):
	Class, race, name = "Neutral", "Demon", "Desk Imp"
	mana, attack, health = 0, 1, 1
	index = "Academy~Neutral~Minion~0~1~1~Demon~Desk Imp"
	requireTarget, keyWord, description = False, "", ""
	name_CN = "课桌小鬼"
	
"""Mana 1 cards"""
class AnimatedBroomstick(Minion):
	Class, race, name = "Neutral", "", "Animated Broomstick"
	mana, attack, health = 1, 1, 1
	index = "Academy~Neutral~Minion~1~1~1~None~Animated Broomstick~Rush~Battlecry"
	requireTarget, keyWord, description = False, "Rush", "Rush. Battlecry: Give your other minions Rush"
	name_CN = "活化扫帚"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		for minion in self.Game.minionsonBoard(self.ID, self):
			minion.getsKeyword("Rush")
		return None
		
		
class IntrepidInitiate(Minion):
	Class, race, name = "Neutral", "", "Intrepid Initiate"
	mana, attack, health = 1, 1, 2
	index = "Academy~Neutral~Minion~1~1~2~None~Intrepid Initiate~Battlecry"
	requireTarget, keyWord, description = False, "", "Spellburst: Gain +2 Attack"
	name_CN = "新生刺头"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_IntrepidInitiate(self)]
		
class Trig_IntrepidInitiate(Spellburst):
	def text(self, CHN):
		return "法术迸发：获得+2攻击力" if CHN else "Spellburst: Gain +2 Attack"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.buffDebuff(2, 0)
		
		
class PenFlinger(Minion):
	Class, race, name = "Neutral", "", "Pen Flinger"
	mana, attack, health = 1, 1, 1
	index = "Academy~Neutral~Minion~1~1~1~None~Pen Flinger~Battlecry"
	requireTarget, keyWord, description = True, "", "Battlecry: Deal 1 damage. Spellburst: Return this to your hand"
	name_CN = "甩笔侏儒"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
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
	index = "Academy~Neutral~Weapon~1~0~4~Sphere of Sapience~Neutral"
	name_CN = "感知宝珠"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_SphereofSapience(self)]
		
	def discoverDecided(self, option, info):
		if isinstance(option, NewFate):
			self.Game.fixedGuides.append(True)
			ownDeck = self.Game.Hand_Deck.decks[self.ID]
			ownDeck.insert(0, ownDeck.pop())
			self.loseDurability()
		else:
			self.Game.fixedGuides.append(False)
			
class Trig_SphereofSapience(TrigBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["TurnStarts"])
		
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
	index = "Academy~Neutral~Minion~1~1~1~None~Tour Guide~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Your next Hero Power costs (0)"
	name_CN = "巡游向导"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		tempAura = GameManaAura_NextHeroPower0(self.Game, self.ID)
		self.Game.Manas.PowerAuras.append(tempAura)
		tempAura.auraAppears()
		return None
		
class GameManaAura_NextHeroPower0(TempManaEffect_Power):
	def __init__(self, Game, ID, changeby=0, changeto=-1):
		self.blank_init(Game, ID, 0, 0)
		self.temporary = False
		
	def applicable(self, target):
		return target.ID == self.ID
		
"""Mana 2 Cards"""
class CultNeophyte(Minion):
	Class, race, name = "Neutral", "", "Cult Neophyte"
	mana, attack, health = 2, 3, 2
	index = "Academy~Neutral~Minion~2~3~2~None~Cult Neophyte~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Your opponent's spells cost (1) more next turn"
	name_CN = "异教 低阶牧师"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.Game.Manas.CardAuras_Backup.append(GameManaAura_InTurnSpell1More(self.Game, 3-self.ID))
		return None
		
class GameManaAura_InTurnSpell1More(TempManaEffect):
	def __init__(self, Game, ID, changeby=0, changeto=-1):
		self.blank_init(Game, ID, +1, -1)
		self.signals = ["CardEntersHand"]
		
	def applicable(self, target):
		return target.ID == self.ID and target.type == "Spell"
		
		
class ManafeederPanthara(Minion):
	Class, race, name = "Neutral", "Beast", "Manafeeder Panthara"
	mana, attack, health = 2, 2, 3
	index = "Academy~Neutral~Minion~2~2~3~Beast~Manafeeder Panthara~Battlecry"
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
	index = "Academy~Neutral~Minion~2~3~1~None~Sneaky Delinquent~Stealth~Deathrattle"
	requireTarget, keyWord, description = False, "Stealth", "Stealth. Deathrattle: Add a 3/1 Ghost with Stealth to your hand"
	name_CN = "少年惯偷"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [AddaSpectralDelinquent2YourHand(self)]
		
class AddaSpectralDelinquent2YourHand(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.Game.Hand_Deck.addCardtoHand(SpectralDelinquent, self.entity.ID, "type")
		
	def text(self, CHN):
		return "亡语：将一个3/1并具有潜行的幽灵置入你的手牌" if CHN else "Deathrattle: Add a 3/1 Ghost with Stealth to your hand"
		
class SpectralDelinquent(Minion):
	Class, race, name = "Neutral", "", "Spectral Delinquent"
	mana, attack, health = 2, 3, 1
	index = "Academy~Neutral~Minion~2~3~1~None~Spectral Delinquent~Stealth~Uncollectible"
	requireTarget, keyWord, description = False, "Stealth", "Stealth"
	name_CN = "鬼灵惯偷"
	
	
class VoraciousReader(Minion):
	Class, race, name = "Neutral", "", "Voracious Reader"
	mana, attack, health = 2, 1, 3
	index = "Academy~Neutral~Minion~2~1~3~None~Voracious Reader"
	requireTarget, keyWord, description = False, "", "At the end of your turn, draw until you have 3 cards"
	name_CN = "贪婪的书虫"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_VoraciousReader(self)]
		
#不知道疲劳的时候是否会一直抽牌，假设不会
class Trig_VoraciousReader(TrigBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["TurnEnds"])
		
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
	index = "Academy~Neutral~Minion~2~2~2~None~Wandmaker~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Add a 1-Cost spell from your class to your hand"
	name_CN = "魔杖工匠"
	poolIdentifier = "1-Cost Spells as Druid"
	@classmethod
	def generatePool(cls, Game):
		return ["1-Cost Spells as %s"%Class for Class in Game.Classes], \
				[[value for key, value in Game.ClassCards[Class].items() if "~Spell~" in key and key.split('~')[3] == '1'] for Class in Game.Classes]
				
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if curGame.mode == 0:
			if curGame.guides:
				spell = curGame.guides.pop(0)
			else:
				key = "1-Cost Spells as "+self.Game.heroes[self.ID].Class
				spell = npchoice(self.rngPool(key))
				curGame.fixedGuides.append(spell)
			curGame.Hand_Deck.addCardtoHand(spell, self.ID, "type")
		return None
		
"""Mana 3 Cards"""
class EducatedElekk(Minion):
	Class, race, name = "Neutral", "Beast", "Educated Elekk"
	mana, attack, health = 3, 3, 4
	index = "Academy~Neutral~Minion~3~3~4~Beast~Educated Elekk~Deathrattle"
	requireTarget, keyWord, description = False, "", "Whenever a spell is played, this minion remembers it. Deathrattle: Shuffle the spells into your deck"
	name_CN = "驯化的雷象"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_EducatedElekk(self)]
		self.deathrattles = [ShuffleRememberedSpells(self)]
		
class Trig_EducatedElekk(TrigBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["SpellPlayed"])
		
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
		self.blank_init(entity)
		self.spellsRemembered = []
		
	def text(self, CHN):
		return "亡语：将记住的法术牌洗入你的牌库" if CHN else "Deathrattle: Shuffle remembered spells into your deck"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		spells = [spell(self.entity.Game, self.entity.ID) for spell in self.spellsRemembered]
		self.entity.Game.Hand_Deck.shuffleintoDeck(spells, self.entity.ID)
		
	def selfCopy(self, recipient):
		trig = type(self)(recipient)
		trig.spellsRemembered = self.spellsRemembered[:]
		return trig
		
		
class EnchantedCauldron(Minion):
	Class, race, name = "Neutral", "", "Enchanted Cauldron"
	mana, attack, health = 3, 1, 6
	index = "Academy~Neutral~Minion~3~1~6~None~Enchanted Cauldron"
	requireTarget, keyWord, description = False, "", "Spellburst: Cast a random spell of the same Cost"
	name_CN = "魔化大锅"
	poolIdentifier = "0-Cost Spells"
	@classmethod
	def generatePool(cls, Game):
		spells = {}
		for Class in Game.Classes:
			for key, value in Game.ClassCards[Class].items():
				if "~Spell~" in key:
					cost = int(key.split('~')[3])
					try: spells[cost].append(value)
					except: spells[cost] = [value]
		return ["%d-Cost Spells"%cost for cost in spells.keys()], list(spells.values())
		
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_EnchantedCauldron(self)]
		
class Trig_EnchantedCauldron(Spellburst):
	def text(self, CHN):
		return "法术迸发：随机施放一个法力值消耗相同的法术" if CHN else "Spellburst: Cast a random spell of the same Cost"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		curGame = self.entity.Game
		if curGame.mode == 0:
			if curGame.guides:
				spell = curGame.guides.pop(0)
			else:
				try: spell = npchoice(self.rngPool("%d-Cost Spells"%number))
				except: spell = None
				curGame.fixedGuides.append(spell)
			if spell:
				spell(curGame, self.entity.ID).cast()
				
				
class RobesofProtection(Minion):
	Class, race, name = "Neutral", "", "Robes of Protection"
	mana, attack, health = 3, 2, 4
	index = "Academy~Neutral~Minion~3~2~4~None~Robes of Protection"
	requireTarget, keyWord, description = False, "", "Your minions have 'Can't be targeted by spells or Hero Powers'"
	name_CN = "防护长袍"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.auras["Your minions have 'Can't be targeted by spells or Hero Powers'"] = EffectAura(self, "Evasive")
		
	def applicable(self, target):
		return True
		
"""Mana 4 Cards"""
class CrimsonHothead(Minion):
	Class, race, name = "Neutral", "Dragon", "Crimson Hothead"
	mana, attack, health = 4, 3, 6
	index = "Academy~Neutral~Minion~4~3~6~Dragon~Crimson Hothead"
	requireTarget, keyWord, description = False, "", "Spellburst: Gain +1 Attack and Taunt"
	name_CN = "赤红急先锋"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_CrimsonHothead(self)]
		
class Trig_CrimsonHothead(Spellburst):
	def text(self, CHN):
		return "法术迸发：获得+1攻击力和嘲讽" if CHN else "Spellburst: Gain +1 Attack and Taunt"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.buffDebuff(1, 0)
		self.entity.getsKeyword("Taunt")
		
		
class DivineRager(Minion):
	Class, race, name = "Neutral", "Elemental", "Divine Rager"
	mana, attack, health = 4, 5, 1
	index = "Academy~Neutral~Minion~4~5~1~Elemental~Divine Rager~Divine Shield"
	requireTarget, keyWord, description = False, "Divine Shield", "Divine Shield"
	name_CN = "神圣暴怒者"
	
	
class FishyFlyer(Minion):
	Class, race, name = "Neutral", "Murloc", "Fishy Flyer"
	mana, attack, health = 4, 4, 3
	index = "Academy~Neutral~Minion~4~4~3~Murloc~Fishy Flyer~Rush~Deathrattle"
	requireTarget, keyWord, description = False, "Rush", "Rush. Deathrattle: Add a 4/3 Ghost with Rush to your hand"
	name_CN = "鱼人飞骑"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [AddaSpectralFlyer2YourHand(self)]
		
class AddaSpectralFlyer2YourHand(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.Game.Hand_Deck.addCardtoHand(SpectralFlyer, self.entity.ID, "type")
		
	def text(self, CHN):
		return "亡语：将一个4/3并具有突袭的幽灵置入你的手牌" if CHN else "Deathrattle: Add a 4/3 Ghost with Rush to your hand"
		
class SpectralFlyer(Minion):
	Class, race, name = "Neutral", "Murloc", "Spectral Flyer"
	mana, attack, health = 4, 4, 3
	index = "Academy~Neutral~Minion~4~4~3~Murloc~Spectral Flyer~Rush~Uncollectible"
	requireTarget, keyWord, description = False, "Rush", "Rush"
	name_CN = "鬼灵飞骑"
	
	
class LorekeeperPolkelt(Minion):
	Class, race, name = "Neutral", "", "Lorekeeper Polkelt"
	mana, attack, health = 4, 4, 5
	index = "Academy~Neutral~Minion~4~4~5~None~Lorekeeper Polkelt~Battlecry~Legendary"
	requireTarget, keyWord, description = False, "", "Battlecry: Reorder your deck from the highest Cost card to the lowest Cost card"
	name_CN = "博学者 普克尔特"
	
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
	index = "Academy~Neutral~Minion~4~2~5~None~Wretched Tutor"
	requireTarget, keyWord, description = False, "", "Spellburst: Deal 2 damage to all other minions"
	name_CN = "失心辅导员"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
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
	index = "Academy~Neutral~Minion~5~4~6~None~Headmaster Kel'Thuzad~Legendary"
	requireTarget, keyWord, description = False, "", "Spellburst: If the spell destroys any minions, summon them"
	name_CN = "校长 克尔苏加德"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_HeadmasterKelThuzad(self)]
		
#假设检测方式是在一张法术打出时开始记录直到可以触发法术迸发之前的两次死亡结算中所有死亡随从
class Trig_HeadmasterKelThuzad(TrigBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["SpellPlayed", "SpellBeenPlayed", "MinionDied"])
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
				minion.Game.summon([minionKilled(minion.Game, minion.ID) for minionKilled in self.minionsKilled], (minion.pos, "totheRight"), minion.ID)
				
	def createCopy(self, game):
		if self not in game.copiedObjs: #这个扳机没有被复制过
			entityCopy = self.entity.createCopy(game)
			trigCopy = self.selfCopy(entityCopy)
			trigCopy.enabled = self.enabled
			trigCopy.minionsKilled = self.minionsKilled[:]
			game.copiedObjs[self] = trigCopy
			return trigCopy
		else: #一个扳机被复制过了，则其携带者也被复制过了
			return game.copiedObjs[self]
			
			
class LakeThresher(Minion):
	Class, race, name = "Neutral", "Beast", "Lake Thresher"
	mana, attack, health = 5, 4, 6
	index = "Academy~Neutral~Minion~5~4~6~Beast~Lake Thresher"
	requireTarget, keyWord, description = False, "", "Also damages the minions next to whomever this attacks"
	name_CN = "止水湖 蛇颈龙"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.marks["Sweep"] = 1
		
		
class Ogremancer(Minion):
	Class, race, name = "Neutral", "", "Ogremancer"
	mana, attack, health = 5, 3, 7
	index = "Academy~Neutral~Minion~5~3~7~None~Ogremancer"
	requireTarget, keyWord, description = False, "", "Whenever your opponent casts a spell, summon a 2/2 Skeleton with Taunt"
	name_CN = "食人魔 巫术师"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_Ogremancer(self)]
		
class Trig_Ogremancer(TrigBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["SpellPlayed"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject.ID != self.entity.ID
		
	def text(self, CHN):
		return "每当你的对手施放一个法术，召唤一个2/2并具有嘲讽的骷髅" if CHN \
				else "Whenever your opponent casts a spell, summon a 2/2 Skeleton with Taunt"
				
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.Game.summon(RisenSkeleton(self.entity.Game, self.entity.ID), self.entity.pos+1, self.entity.ID)
		
class RisenSkeleton(Minion):
	Class, race, name = "Neutral", "", "Risen Skeleton"
	mana, attack, health = 2, 2, 2
	index = "Academy~Neutral~Minion~2~2~2~None~Risen Skeleton~Taunt~Uncollectible"
	requireTarget, keyWord, description = False, "Taunt", "Taunt"
	name_CN = "复活的骷髅"
	
	
class StewardofScrolls(Minion):
	Class, race, name = "Neutral", "Elemental", "Steward of Scrolls"
	mana, attack, health = 5, 4, 4
	index = "Academy~Neutral~Minion~5~4~4~Elemental~Steward of Scrolls~Spell Damage~Battlecry"
	requireTarget, keyWord, description = False, "Spell Damage", "Spell Damage +1. Battlecry: Discover a spell"
	name_CN = "卷轴管理者"
	poolIdentifier = "Demon Hunter Spells"
	@classmethod
	def generatePool(cls, Game):
		return [Class+" Spells" for Class in Game.Classes], \
				[[value for key, value in Game.ClassCards[Class].items() if "~Spell~" in key] for Class in Game.Classes]
				
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if self.ID == curGame.turn:
			if curGame.mode == 0:
				if curGame.guides:
					curGame.Hand_Deck.addCardtoHand(curGame.guides.pop(0), self.ID, "type")
				else:
					key = classforDiscover(self)+" Spells"
					if "byOthers" in comment:
						spell = npchoice(self.rngPool(key))
						curGame.fixedGuides.append(spell)
						curGame.Hand_Deck.addCardtoHand(spell, self.ID, "type")
					else:
						spells = npchoice(self.rngPool(key), 3, replace=False)
						curGame.options = [spell(curGame, self.ID) for spell in spells]
						curGame.Discover.startDiscover(self)
		return target
		
	def discoverDecided(self, option, info):
		self.Game.fixedGuides.append(type(option))
		self.Game.Hand_Deck.addCardtoHand(option, self.ID, byDiscover=True)
		
		
class Vectus(Minion):
	Class, race, name = "Neutral", "", "Vectus"
	mana, attack, health = 5, 4, 4
	index = "Academy~Neutral~Minion~5~4~4~None~Vectus~Battlecry~Legendary"
	requireTarget, keyWord, description = False, "", "Battlecry: Summon two 1/1 Whelps. Each gains a Deathrattle from your minions that died this game"
	name_CN = "维克图斯"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if curGame.mode == 0:
			if curGame.guides:
				minions = curGame.guides.pop(0)
			else:
				minions = [curGame.cardPool[index] for index in curGame.Counters.minionsDiedThisGame[self.ID] if "~Deathrattle" in index]
				minions = [npchoice(minions), npchoice(minions)] if minions else [None, None]
				curGame.fixedGuides.append(tuple(minions))
			whelps = [PlaguedHatchling(curGame, self.ID) for i in range(2)]
			pos = (self.pos, "leftandRight") if self.onBoard else (-1, "totheRightEnd")
			curGame.summon(whelps, pos, self.ID)
			for minion, whelp in zip(minions, whelps):
				if minion and whelp.onBoard:
					for trig in minion(curGame, self.ID).deathrattles:
						trig = type(trig)(whelp)
						whelp.deathrattles.append(trig)
						trig.connect()
				else: break
		return None
		
class PlaguedHatchling(Minion):
	Class, race, name = "Neutral", "Dragon", "Plagued Hatchling"
	mana, attack, health = 1, 1, 1
	index = "Academy~Neutral~Minion~1~1~1~Dragon~Plagued Hatchling~Uncollectible"
	requireTarget, keyWord, description = False, "", ""
	name_CN = "魔药龙崽"
	
	
"""Mana 6 Cards"""
class OnyxMagescribe(Minion):
	Class, race, name = "Neutral", "Dragon", "Onyx Magescribe"
	mana, attack, health = 6, 4, 9
	index = "Academy~Neutral~Minion~6~4~9~Dragon~Onyx Magescribe"
	requireTarget, keyWord, description = False, "", "Spellburst: Add 2 random spells from your class to your hand"
	name_CN = "黑岩 法术抄写员"
	poolIdentifier = "Druid Spells"
	@classmethod
	def generatePool(cls, Game):
		return [Class+" Spells" for Class in Game.Classes], \
				[[value for key, value in Game.ClassCards[Class].items() if "~Spell~" in key] for Class in Game.Classes]
				
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_OnyxMagescribe(self)]
		
class Trig_OnyxMagescribe(Spellburst):
	def text(self, CHN):
		return "法术迸发：随机将两张你职业的法术牌置入你的手牌" if CHN \
				else "Spellburst: Add 2 random spells from your class to your hand"
				
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		curGame = self.entity.Game
		if curGame.mode == 0:
			if curGame.guides:
				spells = curGame.guides.pop(0)
			else:
				key = curGame.heroes[self.entity.ID].Class + " Spells"
				spells = npchoice(self.rngPool(key), 2, replace=True)
				curGame.fixedGuides.append(tuple(spells))
			curGame.Hand_Deck.addCardtoHand(spells, self.entity.ID, "type")
			
			
class SmugSenior(Minion):
	Class, race, name = "Neutral", "", "Smug Senior"
	mana, attack, health = 6, 5, 7
	index = "Academy~Neutral~Minion~6~5~7~None~Smug Senior~Taunt~Deathrattle"
	requireTarget, keyWord, description = False, "Taunt", "Taunt. Deathrattle: Add a 5/7 Ghost with Taunt to your hand"
	name_CN = "浮夸的 大四学长"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [AddaSpectralSenior2YourHand(self)]
		
class AddaSpectralSenior2YourHand(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.Game.Hand_Deck.addCardtoHand(SpectralSenior, self.entity.ID, "type")
		
	def text(self, CHN):
		return "亡语：将一个5/7并具有嘲讽的幽灵置入你的手牌" if CHN else "Deathrattle: Add a 5/7 Ghost with Taunt to your hand"
		
class SpectralSenior(Minion):
	Class, race, name = "Neutral", "", "Spectral Senior"
	mana, attack, health = 6, 5, 7
	index = "Academy~Neutral~Minion~6~5~7~None~Spectral Senior~Taunt~Uncollectible"
	requireTarget, keyWord, description = False, "Taunt", "Taunt"
	name_CN = "鬼灵学长"
	
	
class SorcerousSubstitute(Minion):
	Class, race, name = "Neutral", "", "Sorcerous Substitute"
	mana, attack, health = 6, 6, 6
	index = "Academy~Neutral~Minion~6~6~6~None~Sorcerous Substitute~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: If you have Spell Damage, summon a copy of this"
	name_CN = "巫术替身"
	
	def effCanTrig(self):
		self.effectViable =  self.countSpellDamage() > 0
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if self.countSpellDamage() > 0:
			Copy = self.selfCopy(self.ID) if self.onBoard else type(self)(self.Game, self.ID)
			self.Game.summon(Copy, self.pos+1, self.ID)
		return None
		
		
"""Mana 7 cards or higher"""
class KeymasterAlabaster(Minion):
	Class, race, name = "Neutral", "", "Keymaster Alabaster"
	mana, attack, health = 7, 6, 8
	index = "Academy~Neutral~Minion~7~6~8~None~Keymaster Alabaster~Legendary"
	requireTarget, keyWord, description = False, "", "Whenever your opponent draws a card, add a copy to your hand that costs (1)"
	name_CN = "钥匙专家 阿拉巴斯特"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_KeymasterAlabaster(self)]
		
class Trig_KeymasterAlabaster(TrigBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["CardDrawn"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and target[0].ID != self.entity.ID
		
	def text(self, CHN):
		return "每当你的对手抽一张牌时，将一张复制置入你的手牌，其法力值消耗变为(1)点" if CHN \
				else "Whenever your opponent draws a card, add a copy to your hand that costs (1)"
				
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		Copy = target[0].selfCopy(self.entity.ID)
		ManaMod(Copy, changeby=0, changeto=1).applies()
		self.entity.Game.Hand_Deck.addCardtoHand(Copy, self.entity.ID)
		
		
class PlaguedProtodrake(Minion):
	Class, race, name = "Neutral", "Dragon", "Plagued Protodrake"
	mana, attack, health = 8, 8, 8
	index = "Academy~Neutral~Minion~8~8~8~Dragon~Plagued Protodrake~Deathrattle"
	requireTarget, keyWord, description = False, "", "Deathrattle: Summon a random 7-Cost minion"
	name_CN = "魔药始祖龙"
	poolIdentifier = "7-Cost Minions to Summon"
	@classmethod
	def generatePool(cls, Game):
		return "7-Cost Minions to Summon", list(Game.MinionsofCost[7].values())
		
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [SummonaRandom7CostMinion(self)]
		
class SummonaRandom7CostMinion(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		curGame = self.entity.Game
		if curGame.mode == 0:
			if curGame.guides:
				minion = curGame.guides.pop(0)
			else:
				minion = npchoice(self.rngPool("7-Cost Minions to Summon"))
				curGame.fixedGuides.append(minion)
			curGame.summon(minion(curGame, self.entity.ID), self.entity.pos+1, self.entity.ID)
			
	def text(self, CHN):
		return "亡语：随机召唤一个法力值消耗为(7)的随从" if CHN else "Deathrattle: Summon a random 7-Cost minion"
		
"""Demon Hunter Cards"""
class DemonCompanion(Spell):
	Class, name = "Demon Hunter,Hunter", "Demon Companion"
	requireTarget, mana = False, 1
	index = "Academy~Demon Hunter,Hunter~Spell~1~Demon Companion"
	description = "Summon a random Demon Companion"
	name_CN = "恶魔伙伴"
	def available(self):
		return self.Game.space(self.ID) > 0
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if curGame.space(self.ID) > 0:
			if curGame.mode == 0:
				if curGame.guides:
					companion = curGame.guides.pop(0)
				else:
					companion = npchoice([Reffuh, Kolek, Shima])
					curGame.fixedGuides.append(companion)
				curGame.summon(companion(curGame, self.ID), -1, self.ID)
		return None
		
class Reffuh(Minion):
	Class, race, name = "Demon Hunter,Hunter", "Demon", "Reffuh"
	mana, attack, health = 1, 2, 1
	index = "Academy~Demon Hunter,Hunter~Minion~1~2~1~Demon~Reffuh~Charge~Uncollectible"
	requireTarget, keyWord, description = False, "Charge", "Charge"
	name_CN = "弗霍"
	
class Kolek(Minion):
	Class, race, name = "Demon Hunter,Hunter", "Demon", "Kolek"
	mana, attack, health = 1, 1, 2
	index = "Academy~Demon Hunter,Hunter~Minion~1~1~2~Demon~Kolek~Uncollectible"
	requireTarget, keyWord, description = False, "", "Your other minions have +1 Attack"
	name_CN = "克欧雷"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.auras["Your other minions have +1 Attack"] = StatAura_Others(self, 1, 0)
		
class Shima(Minion):
	Class, race, name = "Demon Hunter,Hunter", "Demon", "Shima"
	mana, attack, health = 1, 2, 2
	index = "Academy~Demon Hunter,Hunter~Minion~1~2~2~Demon~Shima~Taunt~Uncollectible"
	requireTarget, keyWord, description = False, "Taunt", "Taunt"
	name_CN = "莎米"
	
	
class DoubleJump(Spell):
	Class, name = "Demon Hunter", "Double Jump"
	requireTarget, mana = False, 1
	index = "Academy~Demon Hunter~Spell~1~Double Jump"
	description = "Draw an Outcast card from your deck"
	name_CN = "二段跳"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if curGame.mode == 0:
			if curGame.guides:
				i = curGame.guides.pop(0)
			else:
				cards = [i for i, card in enumerate(curGame.Hand_Deck.decks[self.ID]) if "~Outcast" in card.index]
				i = npchoice(cards) if cards else -1
				curGame.fixedGuides.append(i)
			if i > -1:
				curGame.Hand_Deck.drawCard(self.ID, i)
		return None
		
		
class TrueaimCrescent(Weapon):
	Class, name, description = "Demon Hunter,Hunter", "Trueaim Crescent", "After your hero attacks a minion, your minions attack it too"
	mana, attack, durability = 1, 1, 4
	index = "Academy~Demon Hunter,Hunter~Weapon~1~1~4~Trueaim Crescent"
	name_CN = "引月长弓"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_TrueaimCrescent(self)]
		
#即使是被冰冻的随从也可以因为这个效果进行攻击，同时攻击不浪费攻击机会，同时可以触发巨型沙虫等随从的获得额外的攻击机会
class Trig_TrueaimCrescent(TrigBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["HeroAttackedMinion"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		#The target can't be dying to trigger this
		return subject.ID == self.entity.ID and self.entity.onBoard and not target.dead and target.health > 0
		
	def text(self, CHN):
		return "在你的英雄攻击一个随从后，你的所有随从也会攻击该随从" if CHN \
				else "After your hero attacks a minion, your minions attack it too"
				
	#随从的攻击顺序与它们的登场顺序一致
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		game = self.entity.Game
		minions = game.sort_Sequence(game.minionsAlive(self.entity.ID))[0]
		for minion in minions:
			if target.onBoard and target.health > 0 and not target.dead:
				game.battle(minion, target, verifySelectable=False, useAttChance=True, resolveDeath=False, resetRedirectionTriggers=True)
				
				
class AceHunterKreen(Minion):
	Class, race, name = "Demon Hunter,Hunter", "", "Ace Hunter Kreen"
	mana, attack, health = 3, 2, 4
	index = "Academy~Demon Hunter,Hunter~Minion~3~2~4~None~Ace Hunter Kreen~Legendary"
	requireTarget, keyWord, description = False, "", "Your other characters are Immune while attacking"
	name_CN = "金牌猎手克里"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_AceHunterKreen(self)]
		
class Trig_AceHunterKreen(TrigBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["BattleStarted", "BattleFinished"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject.ID == self.entity.ID and subject != self.entity and self.entity.onBoard
		
	def text(self, CHN):
		return "你的其他角色在攻击时具有免疫" if CHN else "Your other characters are Immune while attacking"
		
	#不知道攻击具有受伤时召唤一个随从的扳机的随从时，飞刀能否对这个友方角色造成伤害
	#目前的写法是这个战斗结束信号触发在受伤之后
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		if signal == "BattleStarted":
			if subject.type == "Minion": subject.status["Immune"] += 1
			else: self.entity.Game.status[self.entity.ID]["Immune"] += 1
		else:
			if subject.type == "Minion": subject.status["Immune"] -= 1
			else: self.entity.Game.status[self.entity.ID]["Immune"] -= 1
			
class Magehunter(Minion):
	Class, race, name = "Demon Hunter", "", "Magehunter"
	mana, attack, health = 3, 2, 3
	index = "Academy~Demon Hunter~Minion~3~2~3~None~Magehunter~Rush"
	requireTarget, keyWord, description = False, "Rush", "Rush. Whenever this attacks a minion, Silence it"
	name_CN = "法师猎手"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_Magehunter(self)]
		
class Trig_Magehunter(TrigBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionAttackingMinion"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject == self.entity and self.entity.onBoard
		
	def text(self, CHN):
		return "每当该随从攻击一个随从时，将其沉默" if CHN else "Whenever this attacks a minion, Silence it"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		target.getsSilenced()
		
		
class ShardshatterMystic(Minion):
	Class, race, name = "Demon Hunter", "", "Shardshatter Mystic"
	mana, attack, health = 3, 3, 2
	index = "Academy~Demon Hunter~Minion~3~3~2~None~Shardshatter Mystic~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Destroy a Soul Fragment in your deck to deal 3 damage to all other minions"
	name_CN = "残片震爆 秘术师"
	
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
	Class, name = "Demon Hunter", "Glide"
	requireTarget, mana = False, 4
	index = "Academy~Demon Hunter~Spell~4~Glide~Outcast"
	description = "Shuffle your hand into your deck. Draw 4 cards. Outcast: Your opponent does the same"
	name_CN = "滑翔"
	def effCanTrig(self):
		self.effectViable = self.Game.Hand_Deck.outcastcanTrigger(self)
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.Game.Hand_Deck.shufflefromHand2Deck(0, self.ID, self.ID, all=True)
		for i in range(4): self.Game.Hand_Deck.drawCard(self.ID)
		if posinHand == 0 or posinHand == -1:
			self.Game.Hand_Deck.shufflefromHand2Deck(0, 3-self.ID, self.ID, all=True)
			for i in range(4): self.Game.Hand_Deck.drawCard(3-self.ID)
		return None
		
		
class Marrowslicer(Weapon):
	Class, name, description = "Demon Hunter", "Marrowslicer", "Battlecry: Shuffle 2 Soul Fragments into your deck"
	mana, attack, durability = 4, 4, 2
	index = "Academy~Demon Hunter~Weapon~4~4~2~Marrowslicer~Battlecry"
	name_CN = "切髓之刃"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.Game.Hand_Deck.shuffleintoDeck([SoulFragment(self.Game, self.ID) for i in range(2)], self.ID)
		return None
		
class SoulFragment(Spell):
	Class, name = "Warlock,Demon Hunter", "Soul Fragment"
	requireTarget, mana = False, 0
	index = "Academy~Warlock,Demon Hunter~Spell~0~Soul Fragment~Casts When Drawn~Uncollectible"
	description = "Restore 2 Health to your hero"
	name_CN = "灵魂残片"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		heal = 2 * (2 ** self.countHealDouble())
		self.restoresHealth(self.Game.heroes[self.ID], heal)
		return None
		
		
class StarStudentStelina(Minion):
	Class, race, name = "Demon Hunter", "", "Star Student Stelina"
	mana, attack, health = 4, 4, 3
	index = "Academy~Demon Hunter~Minion~4~4~3~None~Star Student Stelina~Outcast~Legendary"
	requireTarget, keyWord, description = False, "", "Outcast: Look at 3 cards in your opponent's hand. Shuffle one of them into their deck"
	name_CN = "明星演员 斯特里娜"
	
	def effCanTrig(self):
		self.effectViable = self.Game.Hand_Deck.outcastcanTrigger(self)
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if posinHand == 0 or posinHand == -1:
			curGame = self.Game
			if curGame.mode == 0:
				if curGame.guides:
					i = curGame.guides.pop(0)
					if i > -1:
						self.Game.Hand_Deck.shufflefromHand2Deck(i, 3-self.ID, self.ID, all=False)
				else:
					enemyHand = curGame.Hand_Deck.hands[3-self.ID]
					if enemyHand:
						curGame.options = npchoice(enemyHand, min(3, len(enemyHand)), replace=False)
						curGame.Discover.startDiscover(self)
					else: curGame.fixedGuides.append(-1)
		return None
		
	def discoverDecided(self, option, info):
		i = self.Game.Hand_Deck.hands[3-self.ID].index(option)
		self.Game.fixedGuides.append(i)
		self.Game.Hand_Deck.shufflefromHand2Deck(i, 3-self.ID, self.ID, all=False)
		
		
class VilefiendTrainer(Minion):
	Class, race, name = "Demon Hunter", "", "Vilefiend Trainer"
	mana, attack, health = 4, 5, 4
	index = "Academy~Demon Hunter~Minion~4~5~4~None~Vilefiend Trainer~Outcast"
	requireTarget, keyWord, description = False, "", "Outcast: Summon two 1/1 Demons"
	name_CN = "邪犬训练师"
	
	def effCanTrig(self):
		self.effectViable = self.Game.Hand_Deck.outcastcanTrigger(self)
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if posinHand == 0 or posinHand == -1:
			pos = (self.pos, "leftandRight") if self.onBoard else (-1, "totheRightEnd")
			self.Game.summon([SnarlingVilefiend(self.Game, self.ID) for i in range(2)], pos, self.ID)
		return None
		
class SnarlingVilefiend(Minion):
	Class, race, name = "Demon Hunter", "Demon", "Snarling Vilefiend"
	mana, attack, health = 1, 1, 1
	index = "Academy~Demon Hunter~Minion~1~1~1~Demon~Snarling Vilefiend~Uncollectible"
	requireTarget, keyWord, description = False, "", ""
	name_CN = "咆哮的邪犬"
	
	
class BloodHerald(Minion):
	Class, race, name = "Demon Hunter,Hunter", "", "Blood Herald"
	mana, attack, health = 5, 1, 1
	index = "Academy~Demon Hunter,Hunter~Minion~5~1~1~None~Blood Herald"
	requireTarget, keyWord, description = False, "", "Whenever a friendly minion dies while this is in your hand, gain +1/+1"
	name_CN = "嗜血传令官"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsHand = [Trig_BloodHerald(self)]
		
class Trig_BloodHerald(TrigHand):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionDies"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.inHand and target.ID == self.entity.ID
		
	def text(self, CHN):
		return "如果这张牌在你的手牌中，每当一个友方随从死亡，便获得+1/+1" if CHN else "Whenever a friendly minion dies while this is in your hand, gain +1/+1"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.buffDebuff(1, 1)
		
		
class SoulshardLapidary(Minion):
	Class, race, name = "Demon Hunter", "", "Soulshard Lapidary"
	mana, attack, health = 5, 5, 5
	index = "Academy~Demon Hunter~Minion~5~5~5~None~Soulshard Lapidary~Battlecry"
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
	Class, name = "Demon Hunter", "Cycle of Hatred"
	requireTarget, mana = False, 7
	index = "Academy~Demon Hunter~Spell~7~Cycle of Hatred"
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
			self.Game.summon([SpiritofVengeance(self.Game, self.ID) for i in range(num)], (-1, "totheRightEnd"), self.ID)
		return None
		
class SpiritofVengeance(Minion):
	Class, race, name = "Demon Hunter", "", "Spirit of Vengeance"
	mana, attack, health = 3, 3, 3
	index = "Academy~Demon Hunter~Minion~3~3~3~None~Spirit of Vengeance~Uncollectible"
	requireTarget, keyWord, description = False, "", ""
	name_CN = "复仇之魂"
	
	
class FelGuardians(Spell):
	Class, name = "Demon Hunter", "Fel Guardians"
	requireTarget, mana = False, 7
	index = "Academy~Demon Hunter~Spell~7~Fel Guardians"
	description = "Summon three 1/2 Demons with Taunt. Costs (1) less whenever a friendly minion dies"
	name_CN = "邪能护卫"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsHand = [Trig_FelGuardians(self)]
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.Game.summon([SoulfedFelhound(self.Game, self.ID) for i in range(3)], (-1, "totheRightEnd"), self.ID)
		return None
		
class Trig_FelGuardians(TrigHand):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionDies"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.inHand and target.ID == self.entity.ID
		
	def text(self, CHN):
		return "当这张牌在你的手牌中时，每当一个友方随从死亡，法力值消耗便减少(1)点" if CHN else "Costs (1) less whenever a friendly minion dies"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		ManaMod(self.entity, -1, -1).applies()
		
class SoulfedFelhound(Minion):
	Class, race, name = "Demon Hunter", "Demon", "Soulfed Felhound"
	mana, attack, health = 1, 1, 2
	index = "Academy~Demon Hunter~Minion~1~1~2~Demon~Soulfed Felhound~Taunt~Uncollectible"
	requireTarget, keyWord, description = False, "Taunt", "Taunt"
	name_CN = "食魂地狱犬"
	
	
class AncientVoidHound(Minion):
	Class, race, name = "Demon Hunter", "Demon", "Ancient Void Hound"
	mana, attack, health = 9, 10, 10
	index = "Academy~Demon Hunter~Minion~9~10~10~Demon~Ancient Void Hound"
	requireTarget, keyWord, description = False, "", "At the end of your turn, steal 1 Attack and Health from all enemy minions"
	name_CN = "上古 虚空恶犬"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_AncientVoidHound(self)]
		
class Trig_AncientVoidHound(TrigBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["TurnEnds"])
		
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
	Class, name = "Druid,Shaman", "Lightning Bloom"
	requireTarget, mana = False, 0
	index = "Academy~Druid,Shaman~Spell~0~Lightning Bloom~Overload"
	description = "Gain 2 Mana Crystals this turn only. Overload: (2)"
	name_CN = "雷霆绽放"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.overload = 2
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if self.Game.Manas.manas[self.ID] < 10:
			self.Game.Manas.manas[self.ID] += 2
		return None
		
		
class Gibberling(Minion):
	Class, race, name = "Druid", "", "Gibberling"
	mana, attack, health = 1, 1, 1
	index = "Academy~Druid~Minion~1~1~1~None~Gibberling"
	requireTarget, keyWord, description = False, "", "Spellburst: Summon a Gibberling"
	name_CN = "聒噪怪"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_Gibberling(self)]
		
class Trig_Gibberling(Spellburst):
	def text(self, CHN):
		return "法术迸发：召唤一个聒噪怪" if CHN else "Spellburst: Summon a Gibberling"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		minion = self.entity
		minion.Game.summon(Gibberling(minion.Game, minion.ID), minion.pos+1, minion.ID)
		
		
class NatureStudies(Spell):
	Class, name = "Druid", "Nature Studies"
	requireTarget, mana = False, 1
	index = "Academy~Druid~Spell~1~Nature Studies"
	description = "Discover a spell. Your next one costs (1) less"
	name_CN = "自然研习"
	poolIdentifier = "Druid Spells"
	@classmethod
	def generatePool(cls, Game):
		return [Class+" Spells" for Class in Game.Classes], \
				[[value for key, value in Game.ClassCards[Class].items() if "~Spell~" in key] for Class in Game.Classes]
				
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if curGame.mode == 0:
			if curGame.guides:
				spell, possi = curGame.guides.pop(0)
				curGame.Hand_Deck.addCardtoHand(spell, self.ID, "type", byDiscover=True, possi=possi)
			else:
				key = classforDiscover(self)+" Spells"
				pool = self.rngPool(key)
				if self.ID != curGame.turn or "byOthers" in comment:
					spell = npchoice(pool)
					curGame.fixedGuides.append(spell)
					curGame.Hand_Deck.addCardtoHand(spell, self.ID, "type", byDiscover=True, possi=tuple(pool))
				else:
					spells = npchoice(pool, 3, replace=False)
					curGame.options = [spell(curGame, self.ID) for spell in spells]
					curGame.Discover.startDiscover(self, info=pool)
		tempAura = GameManaAura_NextSpell1Less(self.Game, self.ID)
		self.Game.Manas.CardAuras.append(tempAura)
		tempAura.auraAppears()
		return None
		
	def discoverDecided(self, option, info):
		self.Game.fixedGuides.append(type(option))
		self.Game.Hand_Deck.addCardtoHand(option, self.ID, byDiscover=True, possi=tuple(info))
		
class GameManaAura_NextSpell1Less(TempManaEffect):
	def __init__(self, Game, ID, changeby=0, changeto=-1):
		self.blank_init(Game, ID, -1, -1)
		self.temporary = False
		
	def applicable(self, target):
		return target.ID == self.ID and target.type == "Spell"
		
	def text(self, CHN):
		return "你的下一张法术牌的法力值消耗减少(1)点" if CHN else "Your next spell costs (1) less"
		
		
class PartnerAssignment(Spell):
	Class, name = "Druid", "Partner Assignment"
	requireTarget, mana = False, 1
	index = "Academy~Druid~Spell~1~Partner Assignment"
	description = "Add a random 2-Cost and 3-Cost Beast to your hand"
	name_CN = "分配组员"
	poolIdentifier = "2-Cost Beasts"
	@classmethod
	def generatePool(cls, Game):
		return ["2-Cost Beasts", "3-Cost Beasts"], \
				[[value for key, value in Game.MinionswithRace["Beast"].items() if key.split('~')[3] == '2'], \
					[value for key, value in Game.MinionswithRace["Beast"].items() if key.split('~')[3] == '3']]
					
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if curGame.mode == 0:
			if curGame.guides:
				beasts = curGame.guides.pop(0)
			else:
				beasts = [npchoice(self.rngPool("2-Cost Beasts")), npchoice(self.rngPool("3-Cost Beasts"))]
				curGame.fixedGuides.append(beasts)
			curGame.Hand_Deck.addCardtoHand(beasts, self.ID, "type")
		return None
		
		
class SpeakerGidra(Minion):
	Class, race, name = "Druid", "", "Speaker Gidra"
	mana, attack, health = 3, 1, 4
	index = "Academy~Druid~Minion~3~1~4~None~Speaker Gidra~Rush~Windfury"
	requireTarget, keyWord, description = False, "Rush,Windfury", "Rush, Windfury. Spellburst: Gain Attack and Health equal to the spell's Cost"
	name_CN = "演讲者 吉德拉"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_SpeakerGidra(self)]
		
class Trig_SpeakerGidra(Spellburst):
	def text(self, CHN):
		return "法术迸发：获得等同于法术法力值消耗的攻击力和生命值" if CHN else "Spellburst: Gain Attack and Health equal to the spell's Cost"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.buffDebuff(number, number)
		
		
class Groundskeeper(Minion):
	Class, race, name = "Druid,Shaman", "", "Groundskeeper"
	mana, attack, health = 4, 4, 5
	index = "Academy~Druid,Shaman~Minion~4~4~5~None~Groundskeeper~Taunt~Battlecry"
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
	index = "Academy~Druid~Minion~5~5~4~Beast~Twilight Runner~Stealth"
	requireTarget, keyWord, description = False, "Stealth", "Stealth. Whenever this attacks, draw 2 cards"
	name_CN = "夜行虎"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_TwilightRunner(self)]
		
class Trig_TwilightRunner(TrigBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionAttackingMinion", "MinionAttackingHero"])
		
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
	index = "Academy~Druid~Minion~6~5~4~None~Forest Warden Omu~Legendary"
	requireTarget, keyWord, description = False, "", "Spellburst: Refresh your Mana Crystals"
	name_CN = "林地守护者 欧穆"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_ForestWardenOmu(self)]
		
class Trig_ForestWardenOmu(Spellburst):
	def text(self, CHN):
		return "法术迸发：复原你的法力水晶" if CHN else "Spellburst: Refresh your Mana Crystals"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.Game.Manas.restoreManaCrystal(0, self.entity.ID, restoreAll=True)
		
		
class RunicCarvings(Spell):
	Class, name = "Druid,Shaman", "Runic Carvings"
	requireTarget, mana = False, 6
	index = "Academy~Druid,Shaman~Spell~6~Runic Carvings~Choose One"
	description = "Choose One - Summon four 2/2 Treant Totems; or Overload: (2) to given them Rush"
	name_CN = "雕琢符文"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.chooseOne = 1
		self.options = [Normal_Option(self), OverloadRush_Option(self)]
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		minions = [TreantTotem(self.Game, self.ID) for i in range(4)]
		self.Game.summon(minions, (-1, "totheRightEnd"), self.ID)
		if choice != 0:
			self.Game.Manas.overloadMana(2, self.ID)
			for minion in minions:
				if minion.onBoard: minion.getsKeyword("Rush")
		return None
		
class Normal_Option(ChooseOneOption):
	name, description = "Normal", "Summon four 2/2 Treant Totems"
	index = ""
	
class OverloadRush_Option(ChooseOneOption):
	name, description = "OverloadRush", "Summon four 2/2 Treant Totems with Rush. Overload: (2)"
	index = ""
	def available(self):
		return self.entity.Game.space(self.entity.ID) > 0
		
class TreantTotem(Minion):
	Class, race, name = "Druid,Shaman", "Totem", "Treant Totem"
	mana, attack, health = 2, 2, 2
	index = "Academy~Druid,Shaman~Minion~2~2~2~Totem~Treant Totem~Uncollectible"
	requireTarget, keyWord, description = False, "", ""
	name_CN = "树人图腾"
	
	
class SurvivaloftheFittest(Spell):
	Class, name = "Druid", "Survival of the Fittest"
	requireTarget, mana = False, 10
	index = "Academy~Druid~Spell~10~Survival of the Fittest"
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
	Class, name = "Hunter,Druid", "Adorable Infestation"
	requireTarget, mana = True, 1
	index = "Academy~Hunter,Druid~Spell~1~Adorable Infestation"
	description = "Give a minion +1/+1. Summon a 1/1 Cub. Add a Cub to your hand"
	name_CN = "萌物来袭"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			target.buffDebuff(1, 1)
			self.Game.summon(MarsuulCub(self.Game, self.ID), -1, self.ID)
			self.Game.Hand_Deck.addCardtoHand(MarsuulCub, self.ID, "type")
		return target
		
class MarsuulCub(Minion):
	Class, race, name = "Hunter,Druid", "Beast", "Marsuul Cub"
	mana, attack, health = 1, 1, 1
	index = "Academy~Hunter,Druid~Minion~1~1~1~Beast~Marsuul Cub~Uncollectible"
	requireTarget, keyWord, description = False, "", ""
	name_CN = "魔鼠宝宝"
	
	
class CarrionStudies(Spell):
	Class, name = "Hunter", "Carrion Studies"
	requireTarget, mana = False, 1
	index = "Academy~Hunter~Spell~1~Carrion Studies"
	description = "Discover a Deathrattle minion. Your next one costs (1) less"
	name_CN = "腐食研习"
	poolIdentifier = "Deathrattle Minions as Hunter"
	@classmethod
	def generatePool(cls, Game):
		classCards = {s: [value for key, value in Game.ClassCards[s].items() if "~Minion~" in key and "~Deathrattle" in key] for s in Game.Classes}
		classCards["Neutral"] = [value for key, value in Game.NeutralCards.items() if "~Minion~" in key and "~Deathrattle" in key]
		return ["Deathrattle Minions as "+Class for Class in Game.Classes], \
				[classCards[Class]+classCards["Neutral"] for Class in Game.Classes]
				
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if curGame.mode == 0:
			if curGame.guides:
				curGame.Hand_Deck.addCardtoHand(curGame.guides.pop(0), self.ID, "type", byDiscover=True)
			else:
				key = "Deathrattle Minions as " + classforDiscover(self)
				if self.ID != self.Game.turn or "byOthers" in comment:
					minion = npchoice(self.rngPool(key))
					curGame.fixedGuides.append(minion)
					curGame.Hand_Deck.addCardtoHand(minion, self.ID, "type", byDiscover=True)
				else:
					minions = npchoice(self.rngPool(key), 3, replace=False)
					curGame.options = [minion(curGame, self.ID) for minion in minions]
					curGame.Discover.startDiscover(self)
		tempAura = GameManaAura_NextDeathrattleMinion1Less(self.Game, self.ID)
		self.Game.Manas.CardAuras.append(tempAura)
		tempAura.auraAppears()
		return None
		
	def discoverDecided(self, option, info):
		self.Game.fixedGuides.append(type(option))
		self.Game.Hand_Deck.addCardtoHand(option, self.ID, byDiscover=True)
		
class GameManaAura_NextDeathrattleMinion1Less(TempManaEffect):
	def __init__(self, Game, ID, changeby=0, changeto=-1):
		self.blank_init(Game, ID, -1, -1)
		self.temporary = False
		
	def applicable(self, target):
		return target.ID == self.ID and target.type == "Minion" and target.deathrattles
		
	def text(self, CHN):
		return "你的下一张亡语随从牌法力值 消耗减少(1)点" if CHN \
				else "Your next Deathrattle minion costs (1) less"
				
				
class Overwhelm(Spell):
	Class, name = "Hunter", "Overwhelm"
	requireTarget, mana = True, 1
	index = "Academy~Hunter~Spell~1~Overwhelm"
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
	index = "Academy~Hunter~Minion~1~1~1~Beast~Wolpertinger~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Summon a copy of this"
	name_CN = "鹿角小飞兔"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		Copy = self.selfCopy(self.ID) if self.onBoard else type(self)(self.Game, self.ID)
		self.Game.summon(Copy, self.pos+1, self.ID)
		return None
		
		
class BloatedPython(Minion):
	Class, race, name = "Hunter", "Beast", "Bloated Python"
	mana, attack, health = 3, 1, 2
	index = "Academy~Hunter~Minion~3~1~2~Beast~Bloated Python~Deathrattle"
	requireTarget, keyWord, description = False, "", "Deathrattle: Summon a 4/4 Hapless Handler"
	name_CN = "饱腹巨蟒"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [SummonaHaplessHandler(self)]
		
class SummonaHaplessHandler(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.Game.summon(HaplessHandler(self.entity.Game, self.entity.ID), self.entity.pos+1, self.entity.ID)
		
	def text(self, CHN):
		return "亡语：召唤一个4/4的倒霉的管理员" if CHN else "Deathrattle: Summon a 4/4 Hapless Handler"
		
class HaplessHandler(Minion):
	Class, race, name = "Hunter", "", "Hapless Handler"
	mana, attack, health = 4, 4, 4
	index = "Academy~Hunter~Minion~4~4~4~None~Hapless Handler~Uncollectible"
	requireTarget, keyWord, description = False, "", ""
	name_CN = "倒霉的 管理员"
	
	
class ProfessorSlate(Minion):
	Class, race, name = "Hunter", "", "Professor Slate"
	mana, attack, health = 3, 3, 4
	index = "Academy~Hunter~Minion~3~3~4~None~Professor Slate~Legendary"
	requireTarget, keyWord, description = False, "", "Your spells are Poisonous"
	name_CN = "斯雷特教授"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.auras["Your spells are Poisonous"] = GameRuleAura_ProfessorSlate(self)
		
class GameRuleAura_ProfessorSlate(GameRuleAura):
	def auraAppears(self):
		self.entity.Game.status[self.entity.ID]["Spells Poisonous"] += 1
		
	def auraDisappears(self):
		self.entity.Game.status[self.entity.ID]["Spells Poisonous"] -= 1
		
		
class ShandoWildclaw(Minion):
	Class, race, name = "Hunter,Druid", "", "Shan'do Wildclaw"
	mana, attack, health = 3, 3, 3
	index = "Academy~Hunter,Druid~Minion~3~3~3~None~Shan'do Wildclaw~Choose One~Legendary"
	requireTarget, keyWord, description = True, "", "Choose One- Give Beasts in your deck +1/+1; or Transform into a copy of a friendly Beast"
	name_CN = "大导师野爪"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.chooseOne = 1
		self.options = [BuffBeastinDeck_Option(self), BecomeaCopyofBeast_Option(self)]
		
	def returnTrue(self, choice=0):
		return choice != 0
		
	def targetExists(self, choice=1):
		for minion in self.Game.minionsonBoard(self.ID):
			if "Beast" in minion.race: return True
		return False
		
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
				Copy = target.selfCopy(self.ID) if target.onBoard else type(target)(self.Game, self.ID)
				self.Game.transform(self, Copy)
		return target
		
class BuffBeastinDeck_Option(ChooseOneOption):
	name, description = "", "Give Beasts in your deck +1/+1"
	
class BecomeaCopyofBeast_Option(ChooseOneOption):
	name, description = "", "Transform into a copy of a friendly Beast"
	def available(self):
		return self.entity.targetExists(1)
		
		
class KroluskBarkstripper(Minion):
	Class, race, name = "Hunter", "Beast", "Krolusk Barkstripper"
	mana, attack, health = 4, 3, 5
	index = "Academy~Hunter~Minion~4~3~5~Beast~Krolusk Barkstripper"
	requireTarget, keyWord, description = False, "", "Spellburst: Destroy a random enemy minion"
	name_CN = "裂树三叶虫"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_KroluskBarkstripper(self)]
		
class Trig_KroluskBarkstripper(Spellburst):
	def text(self, CHN):
		return "法术迸发：随机消灭一个敌方随从" if CHN else "Spellburst: Destroy a random enemy minion"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		curGame = self.entity.Game
		if curGame.mode == 0:
			if curGame.guides:
				i = curGame.guides.pop(0)
			else:
				minions = curGame.minionsAlive(3-self.entity.ID)
				i = npchoice(minions).pos if minions else -1
				curGame.fixedGuides.append(i)
			if i > -1:
				curGame.killMinion(self.entity, curGame.minions[3-self.entity.ID][i])
				
				
class TeachersPet(Minion):
	Class, race, name = "Hunter,Druid", "Beast", "Teacher's Pet"
	mana, attack, health = 5, 4, 5
	index = "Academy~Hunter,Druid~Minion~5~4~5~Beast~Teacher's Pet~Taunt~Deathrattle"
	requireTarget, keyWord, description = False, "Taunt", "Taunt. Deathrattle: Summon a 3-Cost Beast"
	name_CN = "教师的爱宠"
	@classmethod
	def generatePool(cls, Game):
		return "3-Cost Beasts to Summon", [value for key, value in Game.MinionswithRace["Beast"].items() if key.split('~')[3] == '3']
		
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [Summona3CostBeast(self)]
		
class Summona3CostBeast(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		curGame = self.entity.Game
		if curGame.mode == 0:
			if curGame.guides:
				beast = curGame.guides.pop(0)
			else:
				beast = npchoice(self.rngPool("3-Cost Beasts to Summon"))
				curGame.fixedGuides.append(beast)
			curGame.summon(beast(curGame, self.entity.ID), self.entity.pos+1, self.entity.ID)
			
	def text(self, CHN):
		return "亡语：随机召唤一个法力值消耗为(3)的随从" if CHN else "Deathrattle: Summon a random 3-Cost Beast"
		
		
class GuardianAnimals(Spell):
	Class, name = "Hunter,Druid", "Guardian Animals"
	requireTarget, mana = False, 8
	index = "Academy~Hunter,Druid~Spell~8~Guardian Animals"
	description = "Summon two Beasts that cost (5) or less from your deck. Give them Rush"
	name_CN = "动物保镖"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if curGame.mode == 0:
			for num in range(2):
				if curGame.guides:
					i = curGame.guides.pop(0)
				else:
					beasts = [i for i, card in enumerate(self.Game.Hand_Deck.decks[self.ID]) if card.type == "Minion" and "Beast" in card.race and card.mana < 6]
					i = npchoice(beasts) if beasts and curGame.space(self.ID) > 0 else -1
					curGame.fixedGuides.append(i)
				if i > -1:
					beast = curGame.summonfromDeck(i, self.ID, -1, self.ID)
					beast.getsKeyword("Rush")
				else: break
		return None
		
		
"""Mage Cards"""
class BrainFreeze(Spell):
	Class, name = "Mage,Rogue", "Brain Freeze"
	requireTarget, mana = True, 1
	index = "Academy~Mage,Rogue~Spell~1~Brain Freeze~Combo"
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
				target.getsFrozen()
				self.dealsDamage(target, damage)
			else:
				target.getsFrozen()
		return target
		
		
class DevolvingMissiles(Spell):
	Class, name = "Shaman,Mage", "Devolving Missiles"
	requireTarget, mana = False, 1
	index = "Academy~Shaman,Mage~Spell~1~Devolving Missiles"
	description = "Shoot three missiles at random enemy minions that transform them into ones that cost (1) less"
	name_CN = "衰变飞弹"
	poolIdentifier = "0-Cost Minions to summon"
	@classmethod
	def generatePool(cls, Game):
		return ["%d-Cost Minions to Summon"%cost for cost in Game.MinionsofCost.keys()], \
				[list(Game.MinionsofCost[cost].values()) for cost in Game.MinionsofCost.keys()]
				
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		side, curGame = 3 - self.ID, self.Game
		if curGame.mode == 0:
			for num in range(3):
				if curGame.guides:
					i = curGame.guides.pop(0)
				else:
					objs = curGame.minionsonBoard(side)
					i = npchoice(objs).pos if objs else -1
					curGame.fixedGuides.append(i)
				if i > -1: minion = curGame.minions[side][i]
				else: break
				if curGame.guides:
					newMinion = curGame.guides.pop(0)
				else:
					cost = type(minion).mana - 1
					while cost not in curGame.MinionsofCost:
						cost += 1
					newMinion = npchoice(self.rngPool("%d-Cost Minions to Summon"%cost))
					curGame.fixedGuides.append(newMinion)
				newMinion = newMinion(curGame, side)
				curGame.transform(minion, newMinion)
		return None
		
		
class LabPartner(Minion):
	Class, race, name = "Mage", "", "Lab Partner"
	mana, attack, health = 1, 1, 3
	index = "Academy~Mage~Minion~1~1~3~None~Lab Partner~Spell Damage"
	requireTarget, keyWord, description = False, "Spell Damage", "Spell Damage +1"
	name_CN = "研究伙伴"
	
	
class WandThief(Minion):
	Class, race, name = "Mage,Rogue", "", "Wand Thief"
	mana, attack, health = 1, 1, 2
	index = "Academy~Mage,Rogue~Minion~1~1~2~None~Wand Thief~Combo"
	requireTarget, keyWord, description = False, "", "Combo: Discover a Mage spell"
	name_CN = "魔杖窃贼"
	poolIdentifier = "Mage Spells"
	@classmethod
	def generatePool(cls, Game):
		return "Mage Spells", [value for key, value in Game.ClassCards["Mage"].items() if "~Spell~" in key]
		
	def effCanTrig(self):
		self.effectViable = self.Game.Counters.numCardsPlayedThisTurn[self.ID] > 0
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if curGame.mode == 0:
			if curGame.guides:
				spell = curGame.guides.pop(0)
				if spell: curGame.Hand_Deck.addCardtoHand(spell, self.ID, "type")
			else:
				if self.Game.Counters.numCardsPlayedThisTurn[self.ID] > 0:
					spells = npchoice(self.rngPool("Mage Spells"), 3, replace=False)
					curGame.options = [spell(curGame, self.ID) for spell in spells]
					curGame.Discover.startDiscover(self)
				else: curGame.fixedGuides.append(None)
		return None
		
	def discoverDecided(self, option, info):
		self.Game.fixedGuides.append(type(option))
		self.Game.Hand_Deck.addCardtoHand(option, self.ID, byDiscover=True)
		
		
class CramSession(Spell):
	Class, name = "Mage", "Cram Session"
	requireTarget, mana = False, 2
	index = "Academy~Mage~Spell~2~Cram Session"
	description = "Draw 1 card (improved by Spell Damage)"
	name_CN = "考前刷夜"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		num = 1 + self.countSpellDamage()
		for i in range(num): self.Game.Hand_Deck.drawCard(self.ID)
		return None
		
		
class Combustion(Spell):
	Class, name = "Mage", "Combustion"
	requireTarget, mana = True, 3
	index = "Academy~Mage~Spell~3~Combustion"
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
	index = "Academy~Mage~Minion~3~3~4~None~Firebrand"
	requireTarget, keyWord, description = False, "", "Spellburst: Deal 4 damage randomly split among all enemy minions"
	name_CN = "火印火妖"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_Firebrand(self)]
		
class Trig_Firebrand(Spellburst):
	def text(self, CHN):
		return "法术迸发：造成4点伤害，随机分配到所有敌人身上" if CHN else "Spellburst: Deal 4 damage randomly split among all enemy minions"
			
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		curGame = self.entity.Game
		if curGame.mode == 0:
			for num in range(4):
				if curGame.guides:
					i = curGame.guides.pop(0)
				else:
					minions = curGame.minionsAlive(3-self.entity.ID)
					i = npchoice(minions).pos if minions else -1
					curGame.fixedGuides.append(i)
				if i > -1:
					minion = curGame.minions[3-self.entity.ID][i]
					self.entity.dealsDamage(minion, 1)
				else: break
				
				
class PotionofIllusion(Spell):
	Class, name = "Mage,Rogue", "Potion of Illusion"
	requireTarget, mana = False, 4
	index = "Academy~Mage,Rogue~Spell~4~Potion of Illusion"
	description = "Add 1/1 copies of your minions to your hand. They cost (1)"
	name_CN = "幻觉药水"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		copies = [minion.selfCopy(self.ID, 1, 1, 1) for minion in self.Game.minionsonBoard(self.ID)]
		self.Game.Hand_Deck.addCardtoHand(copies, self.ID)
		return None
		
		
class JandiceBarov(Minion):
	Class, race, name = "Mage,Rogue", "", "Jandice Barov"
	mana, attack, health = 5, 2, 1
	index = "Academy~Mage,Rogue~Minion~5~2~1~None~Jandice Barov~Battlecry~Legendary"
	requireTarget, keyWord, description = False, "", "Battlecry: Summon two random 5-Cost minions. Secretly pick one that dies when it takes damage"
	name_CN = "詹迪斯 巴罗夫"
	poolIdentifier = "5-Cost Minions to Summon"
	@classmethod
	def generatePool(cls, Game):
		return "5-Cost Minions to Summon", list(Game.MinionsofCost[5].values())
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if curGame.mode == 0:
			if curGame.guides:
				minion1, minion2 = curGame.guides.pop(0)
				pos = (self.pos, "leftandRight") if self.onBoard else (-1, "totheRightEnd")
				minion1, minion2 = minion1(curGame, self.ID), minion2(curGame, self.ID)
				curGame.summon([minion1, minion2], pos, self.ID)
				i = curGame.guides.pop(0)
				if i == 1: minion = minion2
				elif i == 0: minion = minion1
				else: return None
				trig = Trig_JandiceBarov(minion)
				minion.trigsBoard.append(trig)
				trig.connect()
			else: #假设只有两个召唤的随从都在场的时候才会让你选择
				minion1, minion2 = [minion(curGame, self.ID) for minion in npchoice(self.rngPool("5-Cost Minions to Summon"), 2, replace=False)]
				curGame.fixedGuides.append((type(minion1), type(minion2) ))
				pos = (self.pos, "leftandRight") if self.onBoard else (-1, "totheRightEnd")
				curGame.summon([minion1, minion2], pos, self.ID)
				if minion1.onBoard and minion2.onBoard and self.ID == curGame.turn:
					if "byOthers" in comment:
						i = nprandint(2)
						minion = minion2 if i else minion1
						trig = Trig_JandiceBarov(minion2)
						minion2.trigsBoard.append(trig)
						trig.connect()
						curGame.fixedGuides.append(i)
					else:
						curGame.options = [minion1, minion2]
						curGame.Discover.startDiscover(self)
				else: i = -1
		return None
		
	def discoverDecided(self, option, info):
		for i, minion in enumerate(self.Game.options):
			if minion == option:
				self.Game.fixedGuides.append(i)
				trig = Trig_JandiceBarov(minion)
				minion.trigsBoard.append(trig)
				trig.connect()
				break
				
class Trig_JandiceBarov(TrigBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionTakesDmg"])
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
	index = "Academy~Mage~Minion~5~3~8~None~Mozaki, Master Duelist~Legendary"
	requireTarget, keyWord, description = False, "", "After you cast a spell, gain Spell Damage +1"
	name_CN = "决斗大师 莫扎奇"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_MozakiMasterDuelist(self)]
		
class Trig_MozakiMasterDuelist(TrigBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["SpellBeenPlayed"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject.ID == self.entity.ID
		
	def text(self, CHN):
		return "在你施放一个法术后，获得法术伤害+1" if CHN else "After you cast a spell, gain Spell Damage +1"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.getsKeyword("Spell Damage")
		
		
class WyrmWeaver(Minion):
	Class, race, name = "Mage", "", "Wyrm Weaver"
	mana, attack, health = 5, 3, 6
	index = "Academy~Mage~Minion~5~3~6~None~Wyrm Weaver"
	requireTarget, keyWord, description = False, "", "Spellburst: Summon two 1/3 Mana Wyrms"
	name_CN = "浮龙培养师"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_WyrmWeaver(self)]
		
class Trig_WyrmWeaver(Spellburst):
	def text(self, CHN):
		return "法术迸发：召唤两个1/3的法力浮龙" if CHN else "Spellburst: Summon two 1/3 Mana Wyrms"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		minion = self.entity
		pos = (minion.pos, "leftandRight") if minion.onBoard else (-1, "totheRightEnd")
		minion.Game.summon([ManaWyrm(minion.Game, minion.ID) for i in range(2)], pos, minion.ID)
		
		
"""Paladin Cards"""
class FirstDayofSchool(Spell):
	Class, name = "Paladin", "First Day of School"
	requireTarget, mana = False, 0
	index = "Academy~Paladin~Spell~0~First Day of School"
	description = "Add 2 random 1-Cost minions to your hand"
	name_CN = "新生入学"
	poolIdentifier = "1-Cost Minions"
	@classmethod
	def generatePool(cls, Game):
		return "1-Cost Minions", list(Game.MinionsofCost[1].values())
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if curGame.mode == 0:
			if curGame.guides:
				minions = curGame.guides.pop(0)
			else:
				minions = npchoice(self.rngPool("1-Cost Minions"), 2, replace=False)
				curGame.fixedGuides.append(tuple(minions))
			curGame.Hand_Deck.addCardtoHand(minions, self.ID, "type")
		return None
		
		
class WaveofApathy(Spell):
	Class, name = "Paladin,Priest", "Wave of Apathy"
	requireTarget, mana = False, 1
	index = "Academy~Paladin,Priest~Spell~1~Wave of Apathy"
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
	index = "Academy~Paladin~Minion~2~1~1~None~Argent Braggart~Battlecry"
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
	Class, name = "Paladin,Priest", "Gift of Luminance"
	requireTarget, mana = True, 3
	index = "Academy~Paladin,Priest~Spell~3~Gift of Luminance"
	description = "Give a minion Divine Shield, then summon a 1/1 copy of it"
	name_CN = "流光之赐"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			target.getsKeyword("Divine Shield")
			Copy = target.selfCopy(target.ID) if target.onBoard or target.inHand else type(target)(self.Game, target.ID)
			Copy.statReset(1, 1)
			self.Game.summon(Copy, target.pos+1, self.ID)
		return target
		
		
class GoodyTwoShields(Minion):
	Class, race, name = "Paladin", "", "Goody Two-Shields"
	mana, attack, health = 3, 4, 2
	index = "Academy~Paladin~Minion~3~4~2~None~Goody Two-Shields~Divine Shield"
	requireTarget, keyWord, description = False, "Divine Shield", "Spellburst: Gain Divine Shield"
	name_CN = "双盾优等生"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_GoodyTwoShields(self)]
		
class Trig_GoodyTwoShields(Spellburst):
	def text(self, CHN):
		return "法术迸发：获得圣盾" if CHN else "Spellburst: Gain Divine Shield"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.getsKeyword("Divine Shield")
		
		
class HighAbbessAlura(Minion):
	Class, race, name = "Paladin,Priest", "", "High Abbess Alura"
	mana, attack, health = 4, 3, 6
	index = "Academy~Paladin,Priest~Minion~4~3~6~None~High Abbess Alura"
	requireTarget, keyWord, description = False, "", "Spellburst: Cast a spell from your deck (targets this if possible)"
	name_CN = "高阶修士 奥露拉"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_HighAbbessAlura(self)]
		
class Trig_HighAbbessAlura(Spellburst):
	def text(self, CHN):
		return "法术迸发：从你的牌库中施放一张法术牌(尽可能以该随从为目标)" if CHN else "Spellburst: Cast a spell from your deck (targets this if possible)"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		curGame = self.entity.Game
		if curGame.mode == 0:
			if curGame.guides:
				i = curGame.guides.pop(0)
			else:
				spells = [i for i, card in enumerate(curGame.Hand_Deck.decks[self.entity.ID]) if card.type == "Spell"]
				i = npchoice(spells) if spells else -1
				curGame.fixedGuides.append(i)
			if i > -1:
				spell = curGame.Hand_Deck.extractfromDeck(i, self.entity.ID)[0]
				spell.cast(None, comment="targetPrefered", preferedTarget=self.entity)
				curGame.gathertheDead()
				
				
class BlessingofAuthority(Spell):
	Class, name = "Paladin", "Blessing of Authority"
	requireTarget, mana = True, 5
	index = "Academy~Paladin~Spell~5~Blessing of Authority"
	description = "Give a minion +8/+8. It can't attack heroes this turn"
	name_CN = "威能祝福"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			target.buffDebuff(8, 8)
			trig = Trig_Charge(target)
			target.trigsBoard.append(trig)
			trig.connect()
		return target
		
		
class DevoutPupil(Minion):
	Class, race, name = "Paladin,Priest", "", "Devout Pupil"
	mana, attack, health = 6, 4, 5
	index = "Academy~Paladin,Priest~Minion~6~4~5~None~Devout Pupil~Divine Shield~Taunt"
	requireTarget, keyWord, description = False, "Divine Shield,Taunt", "Divine Shield,Taunt. Costs (1) less for each spell you've cast on friendly characters this game"
	name_CN = "虔诚的学徒"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsHand = [Trig_DevoutPupil(self)]
		
	def selfManaChange(self):
		if self.inHand:
			self.mana -= len(self.Game.Counters.spellsonFriendliesThisGame[self.ID])
			self.mana = max(self.mana, 0)
			
class Trig_DevoutPupil(TrigHand):
	def __init__(self, entity):
		self.blank_init(entity, ["SpellBeenPlayed"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.inHand and target and subject.ID == target.ID and subject.ID == self.entity.ID
		
	def text(self, CHN):
		return "每当你对一个友方角色施放法术，重新计算费用" if CHN else "Whenever you cast a spell on a friendly character, recalculate the cost"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.Game.Manas.calcMana_Single(self.entity)
		
		
class JudiciousJunior(Minion):
	Class, race, name = "Paladin", "", "Judicious Junior"
	mana, attack, health = 6, 4, 9
	index = "Academy~Paladin~Minion~6~4~9~None~Judicious Junior~Lifesteal"
	requireTarget, keyWord, description = False, "Lifesteal", "Lifesteal"
	name_CN = "踏实的 大三学姐"
	
	
class TuralyontheTenured(Minion):
	Class, race, name = "Paladin", "", "Turalyon, the Tenured"
	mana, attack, health = 8, 3, 12
	index = "Academy~Paladin~Minion~8~3~12~None~Turalyon, the Tenured~Rush~Legendary"
	requireTarget, keyWord, description = False, "Rush", "Rush. Whenever this attacks a minion, set the defender's Attack and Health to 3"
	name_CN = "终身教授 图拉扬"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_TuralyontheTenured(self)]
		
#可以通过宣传牌确认是施放法术之后触发
class Trig_TuralyontheTenured(TrigBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionAttackingMinion"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject == self.entity
		
	def text(self, CHN):
		return "每当其攻击一个随从，将目标的攻击力和生命值变为3" if CHN \
				else "Whenever this attacks a minion, set the defender's Attack and Health to 3"
				
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		target.statReset(3, 3)
		
"""Priest cards"""
class RaiseDead(Spell):
	Class, name = "Priest,Warlock", "Raise Dead"
	requireTarget, mana = False, 0
	index = "Academy~Priest,Warlock~Spell~0~Raise Dead"
	description = "Deal 3 damage to your hero. Return two friendly minions that died this game to your hand"
	name_CN = "亡者复生"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		damage = (3 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		self.dealsDamage(curGame.heroes[self.ID], damage)
		if curGame.mode == 0:
			if curGame.guides:
				minions = curGame.guides.pop(0)
			else:
				deadMinions = [curGame.cardPool[index] for index in curGame.Counters.minionsDiedThisGame[self.ID]]
				minions = tuple(npchoice(deadMinions, min(2, len(deadMinions)), replace=False) if deadMinions else [])
				curGame.fixedGuides.append(minions)
			if minions:
				curGame.Hand_Deck.addCardtoHand(minions, self.ID, "type")
		return None
		
		
class DraconicStudies(Spell):
	Class, name = "Priest", "Draconic Studies"
	requireTarget, mana = False, 1
	index = "Academy~Priest~Spell~1~Draconic Studies"
	description = "Discover a Dragon. Your next one costs (1) less"
	name_CN = "龙族研习"
	poolIdentifier = "Dragons as Priest"
	@classmethod
	def generatePool(cls, Game):
		classCards = {s : [] for s in Game.ClassesandNeutral}
		for key, value in Game.MinionswithRace["Dragon"].items():
			classCards[key.split('~')[1]].append(value)
		return ["Dragons as "+Class for Class in Game.Classes], \
				[classCards[Class]+classCards["Neutral"] for Class in Game.Classes]
				
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if curGame.mode == 0:
			if curGame.guides:
				curGame.Hand_Deck.addCardtoHand(curGame.guides.pop(0), self.ID, "type", byDiscover=True)
			else:
				key = "Dragons as " + classforDiscover(self)
				if self.ID != self.Game.turn or "byOthers" in comment:
					minion = npchoice(self.rngPool(key))
					curGame.fixedGuides.append(minion)
					curGame.Hand_Deck.addCardtoHand(minion, self.ID, "type", byDiscover=True)
				else:
					minions = npchoice(self.rngPool(key), 3, replace=False)
					curGame.options = [minion(curGame, self.ID) for minion in minions]
					curGame.Discover.startDiscover(self)
		tempAura = GameManaAura_NextDragon1Less(self.Game, self.ID)
		self.Game.Manas.CardAuras.append(tempAura)
		tempAura.auraAppears()
		return None
		
	def discoverDecided(self, option, info):
		self.Game.fixedGuides.append(type(option))
		self.Game.Hand_Deck.addCardtoHand(option, self.ID, byDiscover=True)
		
class GameManaAura_NextDragon1Less(TempManaEffect):
	def __init__(self, Game, ID, changeby=0, changeto=-1):
		self.blank_init(Game, ID, -1, -1)
		self.temporary = False
		
	def applicable(self, target):
		return target.ID == self.ID and target.type == "Minion" and "Dragon" in target.race
		
	def text(self, CHN):
		return "你的下一张龙牌的法力值消耗减少(1)点" if CHN else "Your next Dragon costs (1) less"
		
		
class FrazzledFreshman(Minion):
	Class, race, name = "Priest", "", "Frazzled Freshman"
	mana, attack, health = 1, 1, 4
	index = "Academy~Priest~Minion~1~1~4~None~Frazzled Freshman"
	requireTarget, keyWord, description = False, "", ""
	name_CN = "疲倦的 大一新生"
	
	
class MindrenderIllucia(Minion):
	Class, race, name = "Priest", "", "Mindrender Illucia"
	mana, attack, health = 3, 1, 3
	index = "Academy~Priest~Minion~3~1~3~None~Mindrender Illucia~Battlecry~Legendary"
	requireTarget, keyWord, description = False, "", "Battlecry: Swap hands and decks with your opponent until your next turn"
	name_CN = "裂心者 伊露希亚"
	
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
	Class, name = "Priest", "Power Word: Feast"
	requireTarget, mana = True, 2
	index = "Academy~Priest~Spell~2~Power Word: Feast"
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
		self.blank_init(entity, ["TurnEnds"])
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
	index = "Academy~Priest,Warlock~Minion~4~3~3~None~Brittlebone Destroyer~Battlecry"
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
	index = "Academy~Priest~Minion~4~2~4~None~Cabal Acolyte~Taunt"
	requireTarget, keyWord, description = False, "Taunt", "Taunt. Spellburst: Gain control of a random enemy minion with 2 or less Attack"
	name_CN = "秘教侍僧"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_CabalAcolyte(self)]
		
class Trig_CabalAcolyte(Spellburst):
	def text(self, CHN):
		return "法术迸发：随机获得一个攻击力小于或等于2的敌方随从的控制权" if CHN \
				else "Spellburst: Gain control of a random enemy minion with 2 or less Attack"
				
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		curGame = self.entity.Game
		if curGame.mode == 0:
			if curGame.guides:
				i = curGame.guides.pop(0)
			else:
				#假设这个是临时控制，与暗影狂乱一致
				minions = [minion.pos for minion in curGame.minionsAlive(3-self.entity.ID) if minion.attack < 3]
				i = npchoice(minions) if minions else -1
				curGame.fixedGuides.append(i)
			if i > -1: curGame.minionSwitchSide(curGame.minions[3-self.entity.ID][i])
			
			
class DisciplinarianGandling(Minion):
	Class, race, name = "Priest,Warlock", "", "Disciplinarian Gandling"
	mana, attack, health = 4, 3, 6
	index = "Academy~Priest,Warlock~Minion~4~3~6~None~Disciplinarian Gandling~Legendary"
	requireTarget, keyWord, description = False, "", "After you play a minion, destroy it and summon a 4/4 Failed Student"
	name_CN = "教导主任 加丁"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_DisciplinarianGandling(self)]
		
class Trig_DisciplinarianGandling(TrigBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionBeenPlayed"])
		
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
		game.summon(FailedStudent(game, ID), pos, ID)
		
class FailedStudent(Minion):
	Class, race, name = "Priest,Warlock", "", "Failed Student"
	mana, attack, health = 4, 4, 4
	index = "Academy~Priest,Warlock~Minion~4~4~4~None~Failed Student~Uncollectible"
	requireTarget, keyWord, description = False, "", ""
	name_CN = "挂掉的学生"
	
	
class Initiation(Spell):
	Class, name = "Priest", "Initiation"
	requireTarget, mana = True, 6
	index = "Academy~Priest~Spell~6~Initiation"
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
				copy = type(dmgTaker)(self.Game, self.ID)
				self.Game.summon(copy, -1, self.ID)
		return target
		
		
class FleshGiant(Minion):
	Class, race, name = "Priest,Warlock", "", "Flesh Giant"
	mana, attack, health = 8, 8, 8
	index = "Academy~Priest,Warlock~Minion~8~8~8~None~Flesh Giant"
	requireTarget, keyWord, description = False, "", "Costs (1) less for each time your Hero's Health changed during your turn"
	name_CN = "血肉巨人"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsHand = [Trig_FleshGiant(self)]
		
	def selfManaChange(self):
		if self.inHand:
			self.mana -= self.Game.Counters.timesHeroChangedHealth_inOwnTurn[self.ID]
			self.mana = max(self.mana, 0)
			
class Trig_FleshGiant(TrigHand):
	def __init__(self, entity):
		#假设这个费用改变扳机在“当你使用一张法术之后”。不需要预检测
		self.blank_init(entity, ["HeroChangedHealthinTurn"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.inHand and ID == self.entity.ID
		
	def text(self, CHN):
		return "每当你的英雄的生命值在你的回合发生变化，重新计算费用" if CHN \
				else "Whenever your hero's Health changes during your turn, recalculate the cost"
				
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.Game.Manas.calcMana_Single(self.entity)
		
		
"""Rogue Cards"""
class SecretPassage(Spell):
	Class, name = "Rogue", "Secret Passage"
	requireTarget, mana = False, 1
	index = "Academy~Rogue~Spell~1~Secret Passage"
	description = "Replace your hand with 4 cards from your deck. Swap back next turn"
	name_CN = "秘密通道"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		HD = curGame.Hand_Deck
		if curGame.mode == 0:
			if curGame.guides:
				indices = list(curGame.guides.pop(0))
			else:
				deckSize = len(HD.decks[self.ID])
				cards = list(range(deckSize))
				indices = tuple(npchoice(cards, min(deckSize, 4), replace=False) if cards else [])
				curGame.fixedGuides.append(indices)
			if indices:
				cardsfromDeck = []
				for i in reversed(np.sort(indices)):
					cardsfromDeck.append(HD.extractfromDeck(i, self.ID, all=False, enemyCanSee=False)[0])
				hand = HD.extractfromHand(None, self.ID, all=True, enemyCanSee=False)[0]
				for card in hand:
					for trig in card.trigsBoard + card.trigsHand + card.trigsDeck:
						trig.disconnect()
					card.reset(self.ID)
				#Create a turnStartTrigger, it remembers all the current cards in hand.
				trigSwap = SecretPassageEffect(self.Game, self.ID)
				trigSwap.cardsHand2Deck = hand
				trigSwap.cardsDeck2Hand = cardsfromDeck
				HD.shuffleintoDeck(hand, self.ID, enemyCanSee=False, sendSig=False)
				HD.addCardtoHand(cardsfromDeck, self.ID)
				self.Game.turnStartTrigger.insert(0, trigSwap)
		return None
		
class SecretPassageEffect:
	def __init__(self, Game, playerID):
		self.Game, self.playerID = Game, playerID
		self.cardsHand2Deck, self.cardsDeck2Hand = [], []
		
	def turnStartTrigger(self):
		cardstoReturn2Deck = [card for card in self.cardsDeck2Hand if card.inHand and card.ID == self.playerID]
		cardstoReturn2Hand = [card for card in self.cardsHand2Deck if card.inDeck and card.ID == self.playerID]
		HD = self.Game.Hand_Deck
		for card in cardstoReturn2Hand:
			HD.extractfromDeck(card, self.playerID, all=False, enemyCanSee=False)
		for card in cardstoReturn2Deck:
			HD.extractfromHand(card, self.playerID, all=False, enemyCanSee=False)
		for card in cardstoReturn2Deck:
			for trig in card.trigsBoard + card.trigsHand + card.trigsDeck:
				trig.disconnect()
			card.reset(self.playerID)
		HD.shuffleintoDeck(cardstoReturn2Deck, self.playerID, enemyCanSee=False, sendSig=False)
		HD.addCardtoHand(cardstoReturn2Hand, self.playerID)
		
		try: self.Game.turnStartTrigger.remove(self)
		except: pass
		
	def createCopy(self, game): #TurnStartTrigger
		trigCopy = type(self)(game, self.playerID)
		trigCopy.cardsHand2Deck = [card.createCopy(game) for card in self.cardsHand2Deck]
		trigCopy.cardsDeck2Hand = [card.createCopy(game) for card in self.cardsDeck2Hand]
		return trigCopy
		
		
class Plagiarize(Secret):
	Class, name = "Rogue", "Plagiarize"
	requireTarget, mana = False, 2
	index = "Academy~Rogue~Spell~2~Plagiarize~~Secret"
	description = "Secret: At the end of your opponent's turn, add copies of the cards they played this turn"
	name_CN = "抄袭"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_Plagiarize(self)]
		
class Trig_Plagiarize(SecretTrigger):
	def __init__(self, entity):
		self.blank_init(entity, ["TurnEnds"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.ID != ID and self.entity.Game.Counters.cardsPlayedThisTurn[3-self.entity.ID]["Indices"]
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		game = self.entity.Game
		cards = [game.cardPool[index] for index in game.Counters.cardsPlayedThisTurn[3-self.entity.ID]["Indices"]]
		game.Hand_Deck.addCardtoHand(cards, self.entity.ID, "type")
		
		
class Coerce(Spell):
	Class, name = "Rogue,Warrior", "Coerce"
	requireTarget, mana = True, 3
	index = "Academy~Rogue,Warrior~Spell~3~Coerce~Combo"
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
	index = "Academy~Rogue~Weapon~3~1~4~Self-Sharpening Sword"
	name_CN = "自砺之锋"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_SelfSharpeningSword(self)]
		
class Trig_SelfSharpeningSword(TrigBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["HeroAttackedMinion", "HeroAttackedHero"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject.ID == self.entity.ID and self.entity.onBoard
		
	def text(self, CHN):
		return "在你的英雄攻击后，获得+1攻击力" if CHN else "After your hero attacks, gain +1 Attack"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.gainStat(1, 0)
		
		
class VulperaToxinblade(Minion):
	Class, race, name = "Rogue", "", "Vulpera Toxinblade"
	mana, attack, health = 3, 3, 3
	index = "Academy~Rogue~Minion~3~3~3~None~Vulpera Toxinblade"
	requireTarget, keyWord, description = False, "", "Your weapon has +2 Attack"
	name_CN = "狐人淬毒师"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
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
	index = "Academy~Rogue~Minion~4~4~2~None~Infiltrator Lilian~Stealth~Deathrattle~Legendary"
	requireTarget, keyWord, description = False, "Stealth", "Stealth. Deathrattle: Summon a 4/2 Forsaken Lilian that attacks a random enemy"
	name_CN = "渗透者 莉莉安"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [SummonForsakenLilian(self)]
		
class SummonForsakenLilian(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		curGame = self.entity.Game
		minion = ForsakenLilian(curGame, self.entity.ID)
		curGame.summon(minion, self.entity.pos+1, self.entity.ID)
		if curGame.mode == 0:
			enemy = None
			if curGame.guides:
				i, where = curGame.guides.pop(0)
				if where: enemy = curGame.find(i, where)
			else:
				enemies = curGame.charsAlive(3-self.entity.ID)
				if minion.onBoard and minion.health > 0 and not minion.dead and enemies:
					enemy = npchoice(enemies)
					curGame.fixedGuides.append((enemy.pos, enemy.type+str(enemy.ID)))
				else:
					curGame.fixedGuides.append((0, ''))
			if enemy: #假设攻击会消耗攻击机会
				curGame.battle(minion, enemy, verifySelectable=False, resolveDeath=False)
				
	def text(self, CHN):
		return "亡语：召唤一个4/2的被遗忘者莉莉安，并使其随机攻击一个敌人" if CHN else "Deathrattle: Summon a 4/2 Forsaken Lilian that attacks a random enemy"
		
class ForsakenLilian(Minion):
	Class, race, name = "Rogue", "", "Forsaken Lilian"
	mana, attack, health = 4, 4, 2
	index = "Academy~Rogue~Minion~4~4~2~None~Forsaken Lilian~Legendary~Uncollectible"
	requireTarget, keyWord, description = False, "", ""
	name_CN = "被遗忘者 莉莉安"
	
	
class ShiftySophomore(Minion):
	Class, race, name = "Rogue", "", "Shifty Sophomore"
	mana, attack, health = 4, 4, 4
	index = "Academy~Rogue~Minion~4~4~4~None~Shifty Sophomore~Stealth"
	requireTarget, keyWord, description = False, "Stealth", "Stealth. Spellburst: Add a Combo card to your hand"
	name_CN = "调皮的 大二学妹"
	poolIdentifier = "Combo Cards"
	@classmethod
	def generatePool(cls, Game):
		return "Combo Cards", [value for key, value in Game.ClassCards["Rogue"].items() if "~Combo~" in key or key.endswith("~Combo")]
		
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_ShiftySophomore(self)]
		
class Trig_ShiftySophomore(Spellburst):
	def text(self, CHN):
		return "法术迸发：将一张连击牌置入你的手牌" if CHN else "Spellburst: Add a Combo card to your hand"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		curGame = self.entity.Game
		if curGame.mode == 0:
			if curGame.guides:
				card = curGame.guides.pop(0)
			else:
				card = npchoice(self.rngPool("Combo Cards"))
				curGame.fixedGuides.append(card)
			curGame.Hand_Deck.addCardtoHand(card, self.entity.ID, "type")
			
			
class Steeldancer(Minion):
	Class, race, name = "Rogue,Warrior", "", "Steeldancer"
	mana, attack, health = 4, 4, 4
	index = "Academy~Rogue,Warrior~Minion~4~4~4~None~Steeldancer~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Summon a random minion with Cost equal to your weapons's Attack"
	name_CN = "钢铁舞者"
	poolIdentifier = "0-Cost Minions to summon"
	@classmethod
	def generatePool(cls, Game):
		return ["%d-Cost Minions to Summon"%cost for cost in Game.MinionsofCost.keys()], \
				[list(Game.MinionsofCost[cost].values()) for cost in Game.MinionsofCost.keys()]
				
	def effCanTrig(self):
		self.effectViable = self.Game.availableWeapon(self.ID) is not None
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if curGame.mode == 0:
			if curGame.guides:
				minion = curGame.guides.pop(0)
			else:
				weapon = self.Game.availableWeapon(self.ID)
				if weapon:
					cost = max(weapon.attack, 0) #假设计数过高，超出了费用范围，则取最高的可选费用
					while cost not in curGame.MinionsofCost:
						cost -= 1
					minion = npchoice(self.rngPool("%d-Cost Minions to Summon"%cost))
				else: minion = None
				curGame.fixedGuides.append(minion)
			if minion: curGame.summon(minion(curGame, self.ID), self.pos+1, self.ID)
		return None
		
		
class CuttingClass(Spell):
	Class, name = "Rogue,Warrior", "Cutting Class"
	requireTarget, mana = False, 5
	index = "Academy~Rogue,Warrior~Spell~5~Cutting Class"
	description = "Draw 2 cards. Costs (1) less per Attack of your weapon"
	name_CN = "劈砍课程"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
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
		self.blank_init(entity, ["WeaponEquipped", "WeaponRemoved", "WeaponAttChanges"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.inHand and ID == self.entity.ID
		
	def text(self, CHN):
		return "当你的武器装备、失去或攻击力变化时，重新计算费用" if CHN else "Whenever you weapon equips, is lost, or change attack, recalculate the cost"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.Game.Manas.calcMana_Single(self.entity)
		
		
class DoctorKrastinov(Minion):
	Class, race, name = "Rogue,Warrior", "", "Doctor Krastinov"
	mana, attack, health = 5, 4, 4
	index = "Academy~Rogue,Warrior~Minion~5~4~4~None~Doctor Krastinov~Rush~Legendary"
	requireTarget, keyWord, description = False, "Rush", "Rush. Whenever this attacks, give your weapon +1/+1"
	name_CN = "卡斯迪诺夫 教授"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_DoctorKrastinov(self)]
		
class Trig_DoctorKrastinov(TrigBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionAttackingMinion", "MinionAttackingHero"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject == self.entity and self.entity.onBoard
		
	def text(self, CHN):
		return "每当该随从攻击时，使你的武器获得+1/+1" if CHN else "Whenever this attacks, give your weapon +1/+1"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		weapon = self.entity.Game.availableWeapon(self.entity.ID)
		if weapon: weapon.gainStat(1, 1)
		
"""Shaman Cards"""
class PrimordialStudies(Spell):
	Class, name = "Shaman,Mage", "Primordial Studies"
	requireTarget, mana = False, 1
	index = "Academy~Shaman,Mage~Spell~1~Primordial Studies"
	description = "Discover a Spell Damage minion. Your next one costs (1) less"
	name_CN = "始生研习"
	poolIdentifier = "Spell Damage Minions as Mage"
	@classmethod
	def generatePool(cls, Game):
		classCards = {s: [value for key, value in Game.ClassCards[s].items() if "~Spell Damage" in key] for s in Game.Classes}
		classCards["Neutral"] = [value for key, value in Game.NeutralCards.items() if "~Minion~" in key and "~Spell Damage" in key]
		return ["Spell Damage Minions as "+Class for Class in Game.Classes], \
				[classCards[Class]+classCards["Neutral"] for Class in Game.Classes]
				
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if curGame.mode == 0:
			if curGame.guides:
				curGame.Hand_Deck.addCardtoHand(curGame.guides.pop(0), self.ID, "type", byDiscover=True)
			else:
				key = "Spell Damage Minions as " + classforDiscover(self)
				if self.ID != self.Game.turn or "byOthers" in comment:
					minion = npchoice(self.rngPool(key))
					curGame.fixedGuides.append(minion)
					curGame.Hand_Deck.addCardtoHand(minion, self.ID, "type", byDiscover=True)
				else:
					minions = npchoice(self.rngPool(key), 3, replace=False)
					curGame.options = [minion(curGame, self.ID) for minion in minions]
					curGame.Discover.startDiscover(self)
		tempAura = GameManaAura_NextSpellDamageMinion1Less(self.Game, self.ID)
		self.Game.Manas.CardAuras.append(tempAura)
		tempAura.auraAppears()
		return None
		
	def discoverDecided(self, option, info):
		self.Game.fixedGuides.append(type(option))
		self.Game.Hand_Deck.addCardtoHand(option, self.ID, byDiscover=True)
		
class GameManaAura_NextSpellDamageMinion1Less(TempManaEffect):
	def __init__(self, Game, ID, changeby=0, changeto=-1):
		self.blank_init(Game, ID, -1, -1)
		self.temporary = False
		
	def applicable(self, target):
		return target.ID == self.ID and target.type == "Minion" and target.keyWords["Spell Damage"] > 0
		
	def text(self, CHN):
		return "你的下一张法术伤害随从牌法力值消耗减少(1)点" if CHN else "Your next Spelldamage minion costs (1) less"
		
		
class DiligentNotetaker(Minion):
	Class, race, name = "Shaman", "", "Diligent Notetaker"
	mana, attack, health = 2, 2, 3
	index = "Academy~Shaman~Minion~2~2~3~None~Diligent Notetaker"
	requireTarget, keyWord, description = False, "", "Spellburst: Return the spell to your hand"
	name_CN = "笔记能手"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_DiligentNotetaker(self)]
		
#可以通过宣传牌确认是施放法术之后触发
class Trig_DiligentNotetaker(Spellburst):
	def text(self, CHN):
		return "法术迸发：将法术牌移回你的手牌" if CHN \
				else "Spellburst: Return the spell to your hand"
				
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.Game.Hand_Deck.addCardtoHand(type(subject), self.entity.ID, "type")
		
		
class RuneDagger(Weapon):
	Class, name, description = "Shaman", "Rune Dagger", "After your hero attacks, gain Spell Damage +1 this turn"
	mana, attack, durability = 2, 1, 3
	index = "Academy~Shaman~Weapon~2~1~3~Rune Dagger"
	name_CN = "符文匕首"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_RuneDagger(self)]
		
class Trig_RuneDagger(TrigBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["HeroAttackedHero", "HeroAttackedMinion"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject == self.entity.Game.heroes[self.entity.ID] and self.entity.onBoard
		
	def text(self, CHN):
		return "在你的英雄攻击后，在本回合中获得法术伤害+1" if CHN \
				else "After your hero attacks, gain Spell Damage +1 this turn"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.Game.status[self.entity.ID]["Spell Damage"] += 1
		self.entity.Game.turnEndTrigger.append(RuneDagger_Effect(self.entity.Game, self.entity.ID))
		
class RuneDagger_Effect:
	def __init__(self, Game, ID):
		self.Game, self.ID = Game, ID
		
	def text(self, CHN):
		return "在本回合结束时，符文匕首的效果(法术伤害+1)消失" if CHN else "At the end of turn, Rune Dagger's effect(Spelldamage +2) expires"
		
	def turnEndTrigger(self):
		self.Game.status[self.ID]["Spell Damage"] -= 1
		try: self.Game.turnEndTrigger.remove(self)
		except: pass
		
	def createCopy(self, game):
		return type(self)(game, self.ID)
		
		
class TrickTotem(Minion):
	Class, race, name = "Shaman,Mage", "Totem", "Trick Totem"
	mana, attack, health = 2, 0, 3
	index = "Academy~Shaman,Mage~Minion~2~0~3~Totem~Trick Totem"
	requireTarget, keyWord, description = False, "", "At the end of your turn, cast a random spell that costs (3) or less"
	name_CN = "戏法图腾"
	poolIdentifier = "Spells of <=3 Cost"
	@classmethod
	def generatePool(cls, Game):
		spells = []
		for Class in Game.Classes:
			spells += [value for key, value in Game.ClassCards[Class].items() if "~Spell~" in key and int(key.split('~')[3]) < 4]
		return "Spells of <=3 Cost", spells
		
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_TrickTotem(self)]
		
class Trig_TrickTotem(TrigBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["TurnEnds"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and ID == self.entity.ID
		
	def text(self, CHN):
		return "在你的回合结束时，随机施放一个法力值消耗小于或等于(3)的法术" if CHN \
				else "At the end of your turn, cast a random spell that costs (3) or less"
				
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		curGame = self.entity.Game
		if curGame.mode == 0:
			if curGame.guides:
				spell = curGame.guides.pop(0)
			else:
				spell = npchoice(self.rngPool("Spells of <=3 Cost"))
				curGame.fixedGuides.append(spell)
			spell(curGame, self.entity.ID).cast()
			
			
class InstructorFireheart(Minion):
	Class, race, name = "Shaman", "", "Instructor Fireheart"
	mana, attack, health = 3, 3, 3
	index = "Academy~Shaman~Minion~3~3~3~None~Instructor Fireheart~Battlecry~Legendary"
	requireTarget, keyWord, description = False, "", "Battlecry: Discover a spell that costs (1) or more. If you play it this turn, repeat this effect"
	name_CN = "导师火心"
	poolIdentifier = "Shaman Spells with 1 or more Cost"
	@classmethod
	def generatePool(cls, Game):
		return [Class+" Spells with 1 or more Cost" for Class in Game.Classes], \
				[[value for key, value in Game.ClassCards[Class].items() if "~Spell~" in key and int(key.split('~')[3]) > 0] for Class in Game.Classes]
				
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if self.ID == self.Game.turn:
			trig = Fireheart_Effect(self.Game, self.ID)
			trig.connect()
			trig.effect(signal='', ID=0, subject=None, target=None, number=0, comment=comment, choice=0)
		return None
		
class Fireheart_Effect:
	def __init__(self, Game, ID):
		self.Game, self.ID = Game, ID
		self.spellDiscovered = None
		
	def connect(self):
		try: self.Game.trigsBoard[self.ID]["SpellBeenPlayed"].append(self)
		except: self.Game.trigsBoard[self.ID]["SpellBeenPlayed"] = [self]
		self.Game.turnEndTrigger.append(self)
		
	def disconnect(self):
		try: self.Game.trigsBoard[self.ID]["SpellBeenPlayed"].remove(self)
		except: pass
		try: self.Game.turnEndTrigger.remove(self)
		except: pass
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject.ID == self.ID and subject == self.spellDiscovered
		
	def trig(self, signal, ID, subject, target, number, comment, choice=0):
		if self.canTrig(signal, ID, subject, target, number, comment):
			if self.Game.GUI: self.Game.GUI.showOffBoardTrig(InstructorFireheart(self.Game, self.ID), linger=False)
			self.effect(signal, ID, subject, target, number, comment)
			
	def text(self, CHN):
		return "本回合，每当你使用导师火心发现的法术，可再发现一张" if CHN \
				else "If you use the spell Discovered by Instructor Fireheart, Discover another"
				
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		curGame = self.Game
		if curGame.mode == 0:
			if curGame.guides:
				spell = curGame.guides.pop(0)(curGame, self.ID)
				self.spellDiscovered = spell
				curGame.Hand_Deck.addCardtoHand(spell, self.ID, byDiscover=True)
			else:
				Class = curGame.heroes[self.ID].Class if curGame.heroes[self.ID].Class != "Neutral" else "Shaman"
				key = "%s Spells with 1 or more Cost"%Class
				if isinstance(comment, str) and "byOthers" in comment:
					spell = npchoice(self.rngPool(key))
					curGame.fixedGuides.append(spell)
					spell = spell(curGame, self.ID)
					self.spellDiscovered = spell
					curGame.Hand_Deck.addCardtoHand(spell, self.ID, byDiscover=True)
				else:
					spells = npchoice(self.rngPool(key), 3, replace=False)
					curGame.options = [spell(curGame, self.ID) for spell in spells]
					curGame.Discover.startDiscover(self)
					
	def rngPool(self, identifier):
		return self.Game.RNGPools[identifier]
		
	def turnEndTrigger(self):
		self.disconnect()
		
	def discoverDecided(self, option, info):
		self.spellDiscovered = option
		self.Game.fixedGuides.append(type(option))
		self.Game.Hand_Deck.addCardtoHand(option, self.ID, byDiscover=True)
		
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
	Class, name = "Shaman", "Molten Blast"
	requireTarget, mana = True, 3
	index = "Academy~Shaman~Spell~3~Molten Blast"
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
			self.Game.summon([MoltenElemental(self.Game, self.ID) for i in range(damage)], (-1, "totheRightEnd"), self.ID)
		return target
		
class MoltenElemental(Minion):
	Class, race, name = "Shaman", "Elemental", "Molten Elemental"
	mana, attack, health = 1, 1, 1
	index = "Academy~Shaman~Minion~1~1~1~Elemental~Molten Elemental~Uncollectible"
	requireTarget, keyWord, description = False, "", ""
	name_CN = "熔岩元素"
	
	
class RasFrostwhisper(Minion):
	Class, race, name = "Shaman,Mage", "", "Ras Frostwhisper"
	mana, attack, health = 5, 3, 6
	index = "Academy~Shaman,Mage~Minion~5~3~6~None~Ras Frostwhisper~Legendary"
	requireTarget, keyWord, description = False, "", "At the end of turn, deal 1 damage to all enemies (improved by Spell Damage)"
	name_CN = "莱斯霜语"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_RasFrostwhisper(self)]
		
class Trig_RasFrostwhisper(TrigBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["TurnEnds"])
		
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
	index = "Academy~Shaman~Minion~5~5~5~Totem~Totem Goliath~Deathrattle"
	requireTarget, keyWord, description = False, "", "Deathrattle: Summon all four basic totems. Overload: (1)"
	name_CN = "图腾巨像"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.overload = 1
		self.deathrattles = [SummonAllBasicTotems(self)]
		
class SummonAllBasicTotems(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		minion, game = self.entity, self.entity.Game
		totems = [HealingTotem(game, minion.ID), SearingTotem(game, minion.ID), StoneclawTotem(game, minion.ID), WrathofAirTotem(game, minion.ID)]
		pos = (minion.pos, "totheRight") if minion in game.minions[minion.ID] else (-1, "totheRightEnd")
		game.summon(totems, pos, minion.ID)
		
	def text(self, CHN):
		return "亡语：召唤全部四种基础图腾" if CHN else "Deathrattle: Summon all four basic totems"
		
		
class TidalWave(Spell):
	Class, name = "Shaman", "Tidal Wave"
	requireTarget, mana = False, 8
	index = "Academy~Shaman~Spell~8~Tidal Wave"
	description = "Lifesteal. Deal 3 damage to all minions"
	name_CN = "潮汐奔涌"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.keyWords["Lifesteal"] = 1
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		damage = (3 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		minions = self.Game.minionsonBoard(1) + self.Game.minionsonBoard(2)
		self.dealsAOE(minions, [damage]*len(minions))
		return None
		
		
"""Warlock Cards"""
class DemonicStudies(Spell):
	Class, name = "Warlock", "Demonic Studies"
	requireTarget, mana = False, 1
	index = "Academy~Warlock~Spell~1~Demonic Studies"
	description = "Discover a Demon. Your next one costs (1) less"
	name_CN = "恶魔研习"
	poolIdentifier = "Demons as Warlock"
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
		if curGame.mode == 0:
			if curGame.guides:
				curGame.Hand_Deck.addCardtoHand(curGame.guides.pop(0), self.ID, "type", byDiscover=True)
			else:
				key = "Demons as " + classforDiscover(self)
				if self.ID != self.Game.turn or "byOthers" in comment:
					minion = npchoice(self.rngPool(key))
					curGame.fixedGuides.append(minion)
					curGame.Hand_Deck.addCardtoHand(minion, self.ID, "type", byDiscover=True)
				else:
					minions = npchoice(self.rngPool(key), 3, replace=False)
					curGame.options = [minion(curGame, self.ID) for minion in minions]
					curGame.Discover.startDiscover(self)
		tempAura = GameManaAura_NextDemon1Less(self.Game, self.ID)
		self.Game.Manas.CardAuras.append(tempAura)
		tempAura.auraAppears()
		return None
		
	def discoverDecided(self, option, info):
		self.Game.fixedGuides.append(type(option))
		self.Game.Hand_Deck.addCardtoHand(option, self.ID, byDiscover=True)
		
class GameManaAura_NextDemon1Less(TempManaEffect):
	def __init__(self, Game, ID, changeby=0, changeto=-1):
		self.blank_init(Game, ID, -1, -1)
		self.temporary = False
		
	def applicable(self, target):
		return target.ID == self.ID and target.type == "Minion" and "Demon" in target.race
		
	def text(self, CHN):
		return "你的下一张恶魔牌的法力值消耗减少(1)点" if CHN else "Your next Demon costs (1) less"
		
class Felosophy(Spell):
	Class, name = "Warlock,Demon Hunter", "Felosophy"
	requireTarget, mana = False, 1
	index = "Academy~Warlock,Demon Hunter~Spell~1~Felosophy~Outcast"
	description = "Copy the lowest Cost Demon in your hand. Outcast: Give both +1/+1"
	name_CN = "邪能学说"
	def effCanTrig(self):
		self.effectViable = self.Game.Hand_Deck.outcastcanTrigger(self)
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if curGame.mode == 0:
			if curGame.guides:
				i = curGame.guides.pop(0)
			else:
				demons, highestCost = [], npinf
				for i, card in enumerate(curGame.Hand_Deck.hands[self.ID]):
					if card.type == "Minion" and "Demon" in card.race:
						if card.mana < highestCost: demons, highestCost = [i], card.mana
						elif card.mana == highestCost: demons.append(i)
				i = npchoice(demons) if demons else -1
				curGame.fixedGuides.append(i)
			if i > -1:
				demon = curGame.Hand_Deck.hands[self.ID][i]
				Copy = demon.selfCopy(self.ID)
				curGame.Hand_Deck.addCardtoHand(Copy, self.ID)
				if posinHand == 0 or posinHand == -1:
					demon.buffDebuff(1, 1)
					Copy.buffDebuff(1, 1)
		return None
		
		
class SpiritJailer(Minion):
	Class, race, name = "Warlock,Demon Hunter", "Demon", "Spirit Jailer"
	mana, attack, health = 1, 1, 3
	index = "Academy~Warlock,Demon Hunter~Minion~1~1~3~Demon~Spirit Jailer~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Shuffle 2 Soul Fragments into your deck"
	name_CN = "精魂狱卒"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.Game.Hand_Deck.shuffleintoDeck([SoulFragment(self.Game, self.ID) for i in range(2)], self.ID)
		return None
		
		
class BonewebEgg(Minion):
	Class, race, name = "Warlock", "", "Boneweb Egg"
	mana, attack, health = 2, 0, 2
	index = "Academy~Warlock~Minion~2~0~2~None~Boneweb Egg~Deathrattle"
	requireTarget, keyWord, description = False, "", "Deathrattle: Summon two 2/1 Spiders"
	name_CN = "骨网之卵"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
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
		minion.Game.summon([BonewebSpider(minion.Game, minion.ID) for i in range(2)], pos, minion.ID)
		
	def text(self, CHN):
		return "亡语：召唤两个2/1的蜘蛛" if CHN else "Deathrattle: Summon two 2/1 Spiders"
		
class BonewebSpider(Minion):
	Class, race, name = "Warlock", "Beast", "Boneweb Spider"
	mana, attack, health = 1, 2, 1
	index = "Academy~Warlock~Minion~1~2~1~Beast~Boneweb Spider~Uncollectible"
	requireTarget, keyWord, description = False, "", ""
	name_CN = "骨网蜘蛛"
	
	
class SoulShear(Spell):
	Class, name = "Warlock,Demon Hunter", "Soul Shear"
	requireTarget, mana = True, 2
	index = "Academy~Warlock,Demon Hunter~Spell~2~Soul Shear"
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
			self.Game.Hand_Deck.shuffleintoDeck([SoulFragment(self.Game, self.ID) for i in range(2)], self.ID)
		return target
		
		
class SchoolSpirits(Spell):
	Class, name = "Warlock", "School Spirits"
	requireTarget, mana = False, 3
	index = "Academy~Warlock~Spell~3~School Spirits"
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
		self.Game.Hand_Deck.shuffleintoDeck([SoulFragment(self.Game, self.ID) for i in range(2)], self.ID)
		return None
		
		
class ShadowlightScholar(Minion):
	Class, race, name = "Warlock", "", "Shadowlight Scholar"
	mana, attack, health = 3, 3, 4
	index = "Academy~Warlock~Minion~3~3~4~None~Shadowlight Scholar~Battlecry"
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
	index = "Academy~Warlock~Minion~5~4~5~Demon~Void Drinker~Taunt~Battlecry"
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
	index = "Academy~Warlock,Demon Hunter~Minion~7~5~5~None~Soulciologist Malicia~Battlecry~Legendary"
	requireTarget, keyWord, description = False, "", "Battlecry: For each Soul Fragment in your deck, summon a 3/3 Soul with Rush"
	name_CN = "灵魂学家 玛丽希亚"
	
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
		self.Game.summon(minions, (self.pos, "totheRight"), self.ID)
		return None
	
class ReleasedSoul(Minion):
	Class, race, name = "Warlock,Demon Hunter", "", "Released Soul"
	mana, attack, health = 3, 3, 3
	index = "Academy~Warlock,Demon Hunter~Minion~3~3~3~None~Released Soul~Rush~Uncollectible"
	requireTarget, keyWord, description = False, "Rush", "Rush"
	name_CN = "被释放的 灵魂"
	
	
class ArchwitchWillow(Minion):
	Class, race, name = "Warlock", "", "Archwitch Willow"
	mana, attack, health = 8, 5, 5
	index = "Academy~Warlock~Minion~8~5~5~None~Archwitch Willow~Battlecry~Legendary"
	requireTarget, keyWord, description = False, "", "Battlecry: Summon a random Demon from your hand and deck"
	name_CN = "高阶女巫 维洛"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		#假设从手牌中最左边向右检索，然后召唤
		if curGame.mode == 0:
			refMinion = self
			if curGame.guides: #Summon a demon from deck
				i = curGame.guides.pop(0)
			else: #Find demons in hand
				demonsfromHand = [i for i, card in enumerate(curGame.Hand_Deck.hands[self.ID]) if card.type == "Minion" and "Demon" in card.race]
				i = npchoice(demonsfromHand) if demonsfromHand and curGame.space(self.ID) > 0 else -1
				curGame.fixedGuides.append(i)
			if i > -1: refMinion = curGame.summonfromHand(i, self.ID, refMinion.pos+1, self.ID)	
			if curGame.guides: #Summon a demon from deck
				i = curGame.guides.pop(0)
			else:
				demonsfromDeck = [i for i, card in enumerate(curGame.Hand_Deck.decks[self.ID]) if card.type == "Minion" and "Demon" in card.race]
				i = npchoice(demonsfromDeck) if demonsfromDeck and curGame.space(self.ID) > 0 else -1
				curGame.fixedGuides.append(i)
			if i > -1: refMinion = curGame.summonfromDeck(i, self.ID, refMinion.pos+1, self.ID)	
		return None
		
		
"""Warrior Cards"""
class AthleticStudies(Spell):
	Class, name = "Warrior", "Athletic Studies"
	requireTarget, mana = False, 1
	index = "Academy~Warrior~Spell~1~Athletic Studies"
	description = "Discover a Rush minion. Your next one costs (1) less"
	name_CN = "体能研习"
	poolIdentifier = "Rush Minions as Warrior"
	@classmethod
	def generatePool(cls, Game):
		classCards = {s: [value for key, value in Game.ClassCards[s].items() if "~Minion~" in key and "~Rush" in key] for s in Game.Classes}
		classCards["Neutral"] = [value for key, value in Game.NeutralCards.items() if "~Minion~" in key and "~Rush" in key]
		return ["Rush Minions as "+Class for Class in Game.Classes], \
				[classCards[Class]+classCards["Neutral"] for Class in Game.Classes]
				
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if curGame.mode == 0:
			if curGame.guides:
				curGame.Hand_Deck.addCardtoHand(curGame.guides.pop(0), self.ID, "type", byDiscover=True)
			else:
				key = "Rush Minions as " + classforDiscover(self)
				if self.ID != self.Game.turn or "byOthers" in comment:
					minion = npchoice(self.rngPool(key))
					curGame.fixedGuides.append(minion)
					curGame.Hand_Deck.addCardtoHand(minion, self.ID, "type", byDiscover=True)
				else:
					minions = npchoice(self.rngPool(key), 3, replace=False)
					curGame.options = [minion(curGame, self.ID) for minion in minions]
					curGame.Discover.startDiscover(self)
		tempAura = GameManaAura_NextRushMinion1Less(self.Game, self.ID)
		self.Game.Manas.CardAuras.append(tempAura)
		tempAura.auraAppears()
		return None
		
	def discoverDecided(self, option, info):
		self.Game.fixedGuides.append(type(option))
		self.Game.Hand_Deck.addCardtoHand(option, self.ID, byDiscover=True)
		
class GameManaAura_NextRushMinion1Less(TempManaEffect):
	def __init__(self, Game, ID, changeby=0, changeto=-1):
		self.blank_init(Game, ID, -1, -1)
		self.temporary = False
		
	def applicable(self, target):
		return target.ID == self.ID and target.type == "Minion" and target.keyWords["Rush"] > 0
		
		
class ShieldofHonor(Spell):
	Class, name = "Warrior,Paladin", "Shield of Honor"
	requireTarget, mana = True, 1
	index = "Academy~Warrior,Paladin~Spell~1~Shield of Honor"
	description = "Give a damaged minion +3 Attack and Divine Shield"
	name_CN = "荣誉护盾"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard and target.health < target.health_max
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			target.buffDebuff(3, 0)
			target.getsKeyword("Divine Shield")
		return target
		
		
class InFormation(Spell):
	Class, name = "Warrior", "In Formation!"
	requireTarget, mana = False, 2
	index = "Academy~Warrior~Spell~2~In Formation!"
	description = "Add 2 random Taunt minions to your hand"
	name_CN = "保持阵型"
	poolIdentifier = "Taunt Minions"
	@classmethod
	def generatePool(cls, Game):
		minions = [value for key, value in Game.NeutralCards.items() if "~Minion~" in key and "~Taunt~" in key]
		for Class in Game.Classes:
			minions += [value for key, value in Game.ClassCards[Class].items() if "~Minion~" in key and "~Taunt~" in key]
		return "Taunt Minions", minions
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if curGame.mode == 0:
			if curGame.guides:
				minions = curGame.guides.pop(0)
			else:
				minions = tuple(npchoice(self.rngPool("Taunt Minions"), 2, replace=False))
				curGame.fixedGuides.append(minions)
			curGame.Hand_Deck.addCardtoHand(minions, self.ID, "type")
		return None
		
		
class CeremonialMaul(Weapon):
	Class, name, description = "Warrior,Paladin", "Ceremonial Maul", "Spellburst: Summon a student with Taunt and stats equal to the spell's Cost"
	mana, attack, durability = 3, 2, 2
	index = "Academy~Warrior,Paladin~Weapon~3~2~2~Ceremonial Maul"
	name_CN = "仪式重槌"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_CeremonialMaul(self)]
		
class Trig_CeremonialMaul(Spellburst):
	def text(self, CHN):
		return "法术迸发：召唤一个属性值等同于法术法力值消耗的并具有嘲讽的学生" if CHN \
				else "Spellburst: Summon a student with Taunt and stats equal to the spell's Cost"
				
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		game, stat = self.entity.Game, number
		if stat and game.space(self.entity.ID):
			cost = min(stat, 10)
			newIndex = "Academy~Warrior,Paladin~%d~%d~%d~Minion~None~Honor Student~Taunt~Uncollectible"%(cost, stat, stat)
			subclass = type("HonorStudent_Mutable_%d"%stat, (HonorStudent_Mutable_1, ),
							{"mana": cost, "attack": stat, "health": stat,
							"index": newIndex}
							)
			game.cardPool[newIndex] = subclass
			game.summon(subclass(game, self.entity.ID), -1, self.entity.ID)
			
class HonorStudent_Mutable_1(Minion):
	Class, race, name = "Warrior,Paladin", "", "Honor Student"
	mana, attack, health = 1, 1, 1
	index = "Academy~Warrior,Paladin~Minion~1~1~1~None~Honor Student~Taunt~Uncollectible"
	requireTarget, keyWord, description = False, "Taunt", "Taunt"
	name_CN = "仪仗学员"
	
	
class LordBarov(Minion):
	Class, race, name = "Warrior,Paladin", "", "Lord Barov"
	mana, attack, health = 3, 3, 2
	index = "Academy~Warrior,Paladin~Minion~3~3~2~None~Lord Barov~Battlecry~Deathrattle"
	requireTarget, keyWord, description = False, "", "Battlecry: Set the Health of all other minions to 1. Deathrattle: Deal 1 damage to all other minions"
	name_CN = "巴罗夫领主"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
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
	index = "Academy~Warrior~Minion~3~4~3~None~Playmaker"
	requireTarget, keyWord, description = False, "", "After you play a Rush minion, summon a copy with 1 Health remaining"
	name_CN = "团队核心"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_Playmaker(self)]
		
class Trig_Playmaker(TrigBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionBeenPlayed"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject.ID == self.entity.ID and subject.keyWords["Rush"] > 0
		
	def text(self, CHN):
		return "在你使用一张突袭随从牌后，召唤一个剩余生命值为1的复制" if CHN else "After you play a Rush minion, summon a copy with 1 Health remaining"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		Copy = subject.selfCopy(self.entity.ID)
		Copy.health = 1
		self.entity.Game.summon(Copy, self.entity.pos+1, self.entity.ID)
		
		
class ReapersScythe(Weapon):
	Class, name, description = "Warrior", "Reaper's Scythe", "Spellburst: Also damages adjacent minions this turn"
	mana, attack, durability = 4, 4, 2
	index = "Academy~Warrior~Weapon~4~4~2~Reaper's Scythe"
	name_CN = "收割之镰"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
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
		self.blank_init(entity, ["TurnEnds"])
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
	Class, name = "Warrior,Paladin", "Commencement"
	requireTarget, mana = False, 7
	index = "Academy~Warrior,Paladin~Spell~7~Commencement"
	description = "Summon a minion from your deck. Give it Taunt and Divine Shield"
	name_CN = "毕业仪式"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if curGame.mode == 0:
			if curGame.guides:
				i = curGame.guides.pop(0)
			else:
				minions = [i for i, card in enumerate(curGame.Hand_Deck.decks[self.ID]) if card.type == "Minion"]
				i = npchoice(minions) if minions and curGame.space(self.ID) > 0 else -1
				curGame.fixedGuides.append(i)
			if i > -1:
				minion = curGame.summonfromDeck(i, self.ID, -1, self.ID)
				minion.getsKeyword("Taunt")
				minion.getsKeyword("Divine Shield")
		return None
		
		
class Troublemaker(Minion):
	Class, race, name = "Warrior", "", "Troublemaker"
	mana, attack, health = 8, 6, 8
	index = "Academy~Warrior~Minion~8~6~8~None~Troublemaker"
	requireTarget, keyWord, description = False, "", "At the end of your turn, summon two 3/3 Ruffians that attack random enemies"
	name_CN = "问题学生"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_Troublemaker(self)]
		
class Trig_Troublemaker(TrigBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["TurnEnds"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and ID == self.entity.ID
		
	def text(self, CHN):
		return "在你的回合结束时，召唤两个3/3的无赖并使其攻击随机敌人" if CHN \
				else "At the end of your turn, summon two 3/3 Ruffians that attack random enemies"
				
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		curGame = self.entity.Game
		ruffians = [Ruffian(curGame, self.entity.ID) for i in range(2)]
		curGame.summon(ruffians, (self.entity.pos, "leftandRight"), self.entity.ID)
		if curGame.mode == 0:
			for num in range(2):
				enemy = None
				if curGame.guides:
					i, where = curGame.guides.pop(0)
					if where: enemy = curGame.find(i, where)
				else:
					targets = curGame.charsAlive(3-self.entity.ID)
					if ruffians[num].onBoard and not ruffians[num].dead and ruffians[num].health > 0 and targets:
						enemy = npchoice(targets)
						curGame.fixedGuides.append((enemy.pos, enemy.type+str(enemy.ID)))
					else:
						curGame.fixedGuides.append((0, ''))
				if enemy: curGame.battle(ruffians[num], enemy, verifySelectable=False, resolveDeath=False)
				
class Ruffian(Minion):
	Class, race, name = "Warrior", "", "Ruffian"
	mana, attack, health = 3, 3, 3
	index = "Academy~Warrior~Minion~3~3~3~None~Ruffian~Uncollectible"
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
	index = "Academy~Warrior~Minion~9~9~9~None~Rattlegore~Deathrattle~Legendary"
	requireTarget, keyWord, description = False, "", "Deathrattle: Resummon this with -1/-1"
	name_CN = "血骨傀儡"
	
#	def __init__(self, Game, ID):
#		self.blank_init(Game, ID)
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
#					minion.Game.summon(newMinion, minion.pos+1, minion.ID)
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
#				newMinion = minion.Game.summon(newMinion, minion.pos+1, minion.ID)
#		
	
Academy_Indices = {"Academy~Neutral~Minion~2~2~2~None~Transfer Student": TransferStudent,
					"Academy~Neutral~Minion~0~1~1~Demon~Desk Imp": DeskImp,
					"Academy~Neutral~Minion~1~1~1~None~Animated Broomstick~Rush~Battlecry": AnimatedBroomstick,
					"Academy~Neutral~Minion~1~1~2~None~Intrepid Initiate~Battlecry": IntrepidInitiate,
					"Academy~Neutral~Minion~1~1~1~None~Pen Flinger~Battlecry": PenFlinger,
					"Academy~Neutral~Weapon~1~0~4~Sphere of Sapience~Neutral": SphereofSapience,
					"Academy~Neutral~Minion~1~1~1~None~Tour Guide~Battlecry": TourGuide,
					"Academy~Neutral~Minion~2~3~2~None~Cult Neophyte~Battlecry": CultNeophyte,
					"Academy~Neutral~Minion~2~2~3~Beast~Manafeeder Panthara~Battlecry": ManafeederPanthara,
					"Academy~Neutral~Minion~2~3~1~None~Sneaky Delinquent~Stealth~Deathrattle": SneakyDelinquent,
					"Academy~Neutral~Minion~2~3~1~None~Spectral Delinquent~Stealth~Uncollectible": SpectralDelinquent,
					"Academy~Neutral~Minion~2~1~3~None~Voracious Reader": VoraciousReader,
					"Academy~Neutral~Minion~2~2~2~None~Wandmaker~Battlecry": Wandmaker,
					"Academy~Neutral~Minion~3~3~4~Beast~Educated Elekk~Deathrattle": EducatedElekk,
					"Academy~Neutral~Minion~3~1~6~None~Enchanted Cauldron": EnchantedCauldron,
					"Academy~Neutral~Minion~3~2~4~None~Robes of Protection": RobesofProtection,
					"Academy~Neutral~Minion~4~3~6~Dragon~Crimson Hothead": CrimsonHothead,
					"Academy~Neutral~Minion~4~5~1~Elemental~Divine Rager~Divine Shield": DivineRager,
					"Academy~Neutral~Minion~4~4~3~Murloc~Fishy Flyer~Rush~Deathrattle": FishyFlyer,
					"Academy~Neutral~Minion~4~4~3~Murloc~Spectral Flyer~Rush~Uncollectible": SpectralFlyer,
					"Academy~Neutral~Minion~4~4~5~None~Lorekeeper Polkelt~Battlecry~Legendary": LorekeeperPolkelt,
					"Academy~Neutral~Minion~4~2~5~None~Wretched Tutor": WretchedTutor,
					"Academy~Neutral~Minion~5~4~6~None~Headmaster Kel'Thuzad~Legendary": HeadmasterKelThuzad,
					"Academy~Neutral~Minion~5~4~6~Beast~Lake Thresher": LakeThresher,
					"Academy~Neutral~Minion~5~3~7~None~Ogremancer": Ogremancer,
					"Academy~Neutral~Minion~2~2~2~None~Risen Skeleton~Taunt~Uncollectible": RisenSkeleton,
					"Academy~Neutral~Minion~5~4~4~Elemental~Steward of Scrolls~Spell Damage~Battlecry": StewardofScrolls,
					"Academy~Neutral~Minion~5~4~4~None~Vectus~Battlecry~Legendary": Vectus,
					"Academy~Neutral~Minion~1~1~1~Dragon~Plagued Hatchling~Uncollectible": PlaguedHatchling,
					"Academy~Neutral~Minion~6~4~9~Dragon~Onyx Magescribe": OnyxMagescribe,
					"Academy~Neutral~Minion~6~5~7~None~Smug Senior~Taunt~Deathrattle": SmugSenior,
					"Academy~Neutral~Minion~6~5~7~None~Spectral Senior~Taunt~Uncollectible": SpectralSenior,
					"Academy~Neutral~Minion~6~6~6~None~Sorcerous Substitute~Battlecry": SorcerousSubstitute,
					"Academy~Neutral~Minion~7~6~8~None~Keymaster Alabaster~Legendary": KeymasterAlabaster,
					"Academy~Neutral~Minion~8~8~8~Dragon~Plagued Protodrake~Deathrattle": PlaguedProtodrake,
					
					"Academy~Demon Hunter,Hunter~Spell~1~Demon Companion": DemonCompanion,
					"Academy~Demon Hunter,Hunter~Minion~1~2~1~Demon~Reffuh~Charge~Uncollectible": Reffuh,
					"Academy~Demon Hunter,Hunter~Minion~1~1~2~Demon~Kolek~Uncollectible": Kolek,
					"Academy~Demon Hunter,Hunter~Minion~1~2~2~Demon~Shima~Taunt~Uncollectible": Shima,
					"Academy~Demon Hunter~Spell~1~Double Jump": DoubleJump,
					"Academy~Demon Hunter,Hunter~Weapon~1~1~4~Trueaim Crescent": TrueaimCrescent,
					"Academy~Demon Hunter,Hunter~Minion~3~2~4~None~Ace Hunter Kreen~Legendary": AceHunterKreen,
					"Academy~Demon Hunter~Minion~3~2~3~None~Magehunter~Rush": Magehunter,
					"Academy~Demon Hunter~Minion~3~3~2~None~Shardshatter Mystic~Battlecry": ShardshatterMystic,
					"Academy~Demon Hunter~Spell~4~Glide~Outcast": Glide,
					"Academy~Demon Hunter~Weapon~4~4~2~Marrowslicer~Battlecry": Marrowslicer,
					"Academy~Demon Hunter~Minion~4~4~3~None~Star Student Stelina~Outcast~Legendary": StarStudentStelina,
					"Academy~Demon Hunter~Minion~4~5~4~None~Vilefiend Trainer~Outcast": VilefiendTrainer,
					"Academy~Demon Hunter~Minion~1~1~1~Demon~Snarling Vilefiend~Uncollectible": SnarlingVilefiend,
					"Academy~Demon Hunter,Hunter~Minion~5~1~1~None~Blood Herald": BloodHerald,
					"Academy~Demon Hunter~Minion~5~5~5~None~Soulshard Lapidary~Battlecry": SoulshardLapidary,
					"Academy~Demon Hunter~Spell~7~Cycle of Hatred": CycleofHatred,
					"Academy~Demon Hunter~Minion~3~3~3~None~Spirit of Vengeance~Uncollectible": SpiritofVengeance,
					"Academy~Demon Hunter~Spell~7~Fel Guardians": FelGuardians,
					"Academy~Demon Hunter~Minion~1~1~2~Demon~Soulfed Felhound~Taunt~Uncollectible": SoulfedFelhound,
					"Academy~Demon Hunter~Minion~9~10~10~Demon~Ancient Void Hound": AncientVoidHound,
					
					"Academy~Druid,Shaman~Spell~0~Lightning Bloom~Overload": LightningBloom,
					"Academy~Druid~Minion~1~1~1~None~Gibberling": Gibberling,
					"Academy~Druid~Spell~1~Nature Studies": NatureStudies,
					"Academy~Druid~Spell~1~Partner Assignment": PartnerAssignment,
					"Academy~Druid~Minion~3~1~4~None~Speaker Gidra~Rush~Windfury": SpeakerGidra,
					"Academy~Druid,Shaman~Minion~4~4~5~None~Groundskeeper~Taunt~Battlecry": Groundskeeper,
					"Academy~Druid~Minion~5~5~4~Beast~Twilight Runner~Stealth": TwilightRunner,
					"Academy~Druid~Minion~6~5~4~None~Forest Warden Omu~Legendary": ForestWardenOmu,
					"Academy~Druid,Shaman~Spell~6~Runic Carvings~Choose One": RunicCarvings,
					"Academy~Druid,Shaman~Minion~2~2~2~Totem~Treant Totem~Uncollectible": TreantTotem,
					"Academy~Druid~Spell~10~Survival of the Fittest": SurvivaloftheFittest,
					
					"Academy~Hunter,Druid~Spell~1~Adorable Infestation": AdorableInfestation,
					"Academy~Hunter,Druid~Minion~1~1~1~Beast~Marsuul Cub~Uncollectible": MarsuulCub,
					"Academy~Hunter~Spell~1~Carrion Studies": CarrionStudies,
					"Academy~Hunter~Spell~1~Overwhelm": Overwhelm,
					"Academy~Hunter~Minion~1~1~1~Beast~Wolpertinger~Battlecry": Wolpertinger,
					"Academy~Hunter~Minion~3~1~2~Beast~Bloated Python~Deathrattle": BloatedPython,
					"Academy~Hunter~Minion~4~4~4~None~Hapless Handler~Uncollectible": HaplessHandler,
					"Academy~Hunter~Minion~3~3~4~None~Professor Slate~Legendary": ProfessorSlate,
					"Academy~Hunter,Druid~Minion~3~3~3~None~Shan'do Wildclaw~Choose One~Legendary": ShandoWildclaw,
					"Academy~Hunter~Minion~4~3~5~Beast~Krolusk Barkstripper": KroluskBarkstripper,
					"Academy~Hunter,Druid~Minion~5~4~5~Beast~Teacher's Pet~Taunt~Deathrattle": TeachersPet,
					"Academy~Hunter,Druid~Spell~8~Guardian Animals": GuardianAnimals,
					
					"Academy~Mage,Rogue~Spell~1~Brain Freeze~Combo": BrainFreeze,
					"Academy~Mage~Minion~1~1~3~None~Lab Partner~Spell Damage": LabPartner,
					"Academy~Mage,Rogue~Minion~1~1~2~None~Wand Thief~Combo": WandThief,
					"Academy~Mage~Spell~2~Cram Session": CramSession,
					"Academy~Mage~Spell~3~Combustion": Combustion,
					"Academy~Mage~Minion~3~3~4~None~Firebrand": Firebrand,
					"Academy~Mage,Rogue~Spell~4~Potion of Illusion": PotionofIllusion,
					"Academy~Mage,Rogue~Minion~5~2~1~None~Jandice Barov~Battlecry~Legendary": JandiceBarov,
					"Academy~Mage~Minion~5~3~8~None~Mozaki, Master Duelist~Legendary": MozakiMasterDuelist,
					"Academy~Mage~Minion~5~3~6~None~Wyrm Weaver": WyrmWeaver,
					
					"Academy~Paladin~Spell~0~First Day of School": FirstDayofSchool,
					"Academy~Paladin,Priest~Spell~1~Wave of Apathy": WaveofApathy,
					"Academy~Paladin~Minion~2~1~1~None~Argent Braggart~Battlecry": ArgentBraggart,
					"Academy~Paladin,Priest~Spell~3~Gift of Luminance": GiftofLuminance,
					"Academy~Paladin~Minion~3~4~2~None~Goody Two-Shields~Divine Shield": GoodyTwoShields,
					"Academy~Paladin,Priest~Minion~4~3~6~None~High Abbess Alura": HighAbbessAlura,
					"Academy~Paladin~Spell~5~Blessing of Authority": BlessingofAuthority,
					"Academy~Paladin,Priest~Minion~6~4~5~None~Devout Pupil~Divine Shield~Taunt": DevoutPupil,
					"Academy~Paladin~Minion~6~4~9~None~Judicious Junior~Lifesteal": JudiciousJunior,
					"Academy~Paladin~Minion~8~3~12~None~Turalyon, the Tenured~Rush~Legendary": TuralyontheTenured,
					
					"Academy~Priest,Warlock~Spell~0~Raise Dead": RaiseDead,
					"Academy~Priest~Spell~1~Draconic Studies": DraconicStudies,
					"Academy~Priest~Minion~1~1~4~None~Frazzled Freshman": FrazzledFreshman,
					"Academy~Priest~Minion~3~1~3~None~Mindrender Illucia~Battlecry~Legendary": MindrenderIllucia,
					"Academy~Priest~Spell~2~Power Word: Feast": PowerWordFeast,
					"Academy~Priest,Warlock~Minion~4~3~3~None~Brittlebone Destroyer~Battlecry": BrittleboneDestroyer,
					"Academy~Priest~Minion~4~2~4~None~Cabal Acolyte~Taunt": CabalAcolyte,
					"Academy~Priest,Warlock~Minion~4~3~6~None~Disciplinarian Gandling~Legendary": DisciplinarianGandling,
					"Academy~Priest,Warlock~Minion~4~4~4~None~Failed Student~Uncollectible": FailedStudent,
					"Academy~Priest~Spell~6~Initiation": Initiation,
					"Academy~Priest,Warlock~Minion~8~8~8~None~Flesh Giant": FleshGiant,
					
					"Academy~Rogue~Spell~1~Secret Passage": SecretPassage,
					"Academy~Rogue~Spell~2~Plagiarize~~Secret": Plagiarize,
					"Academy~Rogue,Warrior~Spell~3~Coerce~Combo": Coerce,
					"Academy~Rogue~Weapon~3~1~4~Self-Sharpening Sword": SelfSharpeningSword,
					"Academy~Rogue~Minion~3~3~3~None~Vulpera Toxinblade": VulperaToxinblade,
					"Academy~Rogue~Minion~4~4~2~None~Infiltrator Lilian~Stealth~Deathrattle~Legendary": InfiltratorLilian,
					"Academy~Rogue~Minion~4~4~2~None~Forsaken Lilian~Legendary~Uncollectible": ForsakenLilian,
					"Academy~Rogue~Minion~4~4~4~None~Shifty Sophomore~Stealth": ShiftySophomore,
					"Academy~Rogue,Warrior~Minion~4~4~4~None~Steeldancer~Battlecry": Steeldancer,
					"Academy~Rogue,Warrior~Spell~5~Cutting Class": CuttingClass,
					"Academy~Rogue,Warrior~Minion~5~4~4~None~Doctor Krastinov~Rush~Legendary": DoctorKrastinov,
					
					"Academy~Shaman,Mage~Spell~1~Devolving Missiles": DevolvingMissiles,
					"Academy~Shaman,Mage~Spell~1~Primordial Studies": PrimordialStudies,
					"Academy~Shaman~Minion~2~2~3~None~Diligent Notetaker": DiligentNotetaker,
					"Academy~Shaman~Weapon~2~1~3~Rune Dagger": RuneDagger,
					"Academy~Shaman,Mage~Minion~2~0~3~Totem~Trick Totem": TrickTotem,
					"Academy~Shaman~Minion~3~3~3~None~Instructor Fireheart~Battlecry~Legendary": InstructorFireheart,
					"Academy~Shaman~Spell~3~Molten Blast": MoltenBlast,
					"Academy~Shaman~Minion~1~1~1~Elemental~Molten Elemental~Uncollectible": MoltenElemental,
					"Academy~Shaman,Mage~Minion~5~3~6~None~Ras Frostwhisper~Legendary": RasFrostwhisper,
					"Academy~Shaman~Minion~5~5~5~Totem~Totem Goliath~Deathrattle": TotemGoliath,
					"Academy~Shaman~Spell~8~Tidal Wave": TidalWave,
					
					"Academy~Warlock,Demon Hunter~Spell~0~Soul Fragment~Casts When Drawn~Uncollectible": SoulFragment,
					"Academy~Warlock~Spell~1~Demonic Studies": DemonicStudies,
					"Academy~Warlock,Demon Hunter~Spell~1~Felosophy~Outcast": Felosophy,
					"Academy~Warlock,Demon Hunter~Minion~1~1~3~Demon~Spirit Jailer~Battlecry": SpiritJailer,
					"Academy~Warlock~Minion~2~0~2~None~Boneweb Egg~Deathrattle": BonewebEgg,
					"Academy~Warlock~Minion~1~2~1~Beast~Boneweb Spider~Uncollectible": BonewebSpider,
					"Academy~Warlock,Demon Hunter~Spell~2~Soul Shear": SoulShear,
					"Academy~Warlock~Spell~3~School Spirits": SchoolSpirits,
					"Academy~Warlock~Minion~3~3~4~None~Shadowlight Scholar~Battlecry": ShadowlightScholar,
					"Academy~Warlock~Minion~5~4~5~Demon~Void Drinker~Taunt~Battlecry": VoidDrinker,
					"Academy~Warlock,Demon Hunter~Minion~7~5~5~None~Soulciologist Malicia~Battlecry~Legendary": SoulciologistMalicia,
					"Academy~Warlock,Demon Hunter~Minion~3~3~3~None~Released Soul~Rush~Uncollectible": ReleasedSoul,
					"Academy~Warlock~Minion~8~5~5~None~Archwitch Willow~Battlecry~Legendary": ArchwitchWillow,
					
					"Academy~Warrior~Spell~1~Athletic Studies": AthleticStudies,
					"Academy~Warrior,Paladin~Spell~1~Shield of Honor": ShieldofHonor,
					"Academy~Warrior~Spell~2~In Formation!": InFormation,
					"Academy~Warrior,Paladin~Weapon~3~2~2~Ceremonial Maul": CeremonialMaul,
					"Academy~Warrior,Paladin~Minion~1~1~1~None~Honor Student~Taunt~Uncollectible": HonorStudent_Mutable_1,
					"Academy~Warrior,Paladin~Minion~3~3~2~None~Lord Barov~Battlecry~Deathrattle": LordBarov,
					"Academy~Warrior~Minion~3~4~3~None~Playmaker": Playmaker,
					"Academy~Warrior~Weapon~4~4~2~Reaper's Scythe": ReapersScythe,
					"Academy~Warrior,Paladin~Spell~7~Commencement": Commencement,
					"Academy~Warrior~Minion~8~6~8~None~Troublemaker": Troublemaker,
					"Academy~Warrior~Minion~3~3~3~None~Ruffian~Uncollectible": Ruffian,
					"Academy~Warrior~Minion~9~9~9~None~Rattlegore~Deathrattle~Legendary": Rattlegore,
					
					}