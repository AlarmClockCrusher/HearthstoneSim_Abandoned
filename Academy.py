from CardTypes import *
from Triggers_Auras import *

from Basic import Claw, ArcaneMissiles, TruesilverChampion
from Shadows import EtherealLackey, FacelessLackey, GoblinLackey, KoboldLackey, WitchyLackey
from Uldum import TitanicLackey, PlagueofDeath, PlagueofMadness, PlagueofMurlocs, PlagueofFlames, PlagueofWrath
from Dragons import DraconicLackey
from Outlands import Minion_Dormantfor2turns

from numpy.random import choice as npchoice
from numpy.random import randint as nprandint
from numpy.random import shuffle as npshuffle

#Scholomance Academy

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
"""
class TransferStudent_Ogrimmar(Minion):
	Class, race, name = "Neutral", "", "Transfer Student"
	mana, attack, health = 2, 2, 2
	index = "Academy~Neutral~Minion~2~2~2~None~Transfer Student~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Deal 2 damage"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			PRINT(self.Game, "Transfer Student's battlecry deals 2 damage to %s"%target.name)
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
	requireTarget, keyWord, description = False, "", "Battlecry: Give a friendly minion +1/+2"
	
	def targetExists(self, choice=0):
		return self.selectableFriendlyMinionExists(choice)
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.ID == self.ID and target != self and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			PRINT(self.Game, "Transfer Student's battlecry gives friendly minion %s +1/+2"%target.name)
			target.buffDebuff(1, 2)
		return target
		
Lackeys = [EtherealLackey, FacelessLackey, GoblinLackey, KoboldLackey, WitchyLackey, TitanicLackey, DraconicLackey]
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
			PRINT(curGame, "Transfer Student's battlecry adds a random Lackey to player's hand")
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
			PRINT(curGame, "Transfer Student's battlecry adds a Uldum plague card to player's hand")
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
		classes, lists, neutralCards = [], [], []
		classCards = {s : [] for s in Game.ClassesandNeutral}
		for key, value in Game.MinionswithRace["Dragon"].items():
			classCards[key.split('~')[1]].append(value)
			
		for Class in Game.Classes:
			classes.append("Dragons as "+Class)
			lists.append(classCards[Class]+classCards["Neutral"])
		return classes, lists #返回的包含“Class Cards except Hunter”等identifier的列表和其他职业卡表
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if self.ID == curGame.turn and curGame.Hand_Deck.handNotFull(self.ID):
			if curGame.mode == 0:
				if curGame.guides:
					PRINT(curGame, "Transfer Student's battlecry adds a Dragon to player's hand")
					curGame.Hand_Deck.addCardtoHand(curGame.guides.pop(0), self.ID, "type")
				else:
					key = "Dragons as "+classforDiscover(self)
					if "byOthers" in comment:
						dragon = npchoice(self.Game.RNGPools[key])
						curGame.fixedGuides.append(dragon)
						PRINT(curGame, "Transfer Student's battlecry adds a random Dragon to player's hand")
						curGame.Hand_Deck.addCardtoHand(dragon, self.ID, "type")
					else:
						dragons = npchoice(self.Game.RNGPools[key], 3, replace=False)
						curGame.options = [dragon(curGame, self.ID) for dragon in dragons]
						PRINT(curGame, "Transfer Student's battlecry lets player discover a Dragon")
						curGame.Discover.startDiscover(self)
		return None
		
	def discoverDecided(self, option, info):
		self.Game.fixedGuides.append(type(option))
		PRINT(self.Game, "Dragon %s is put into player's hand."%option.name)
		self.Game.Hand_Deck.addCardtoHand(option, self.ID)
		self.Game.sendSignal("DiscoveredCardPutintoHand", self.ID, self, option, 0, "")
		
class TransferStudent_Outlands(Minion_Dormantfor2turns):
	Class, race, name = "Neutral", "", "Transfer Student"
	mana, attack, health = 2, 2, 2
	index = "Academy~Neutral~Minion~2~2~2~None~Transfer Student~Battlecry"
	requireTarget, keyWord, description = False, "", "Dormant for 2 turns. When this awakens, deal 2 damage to 2 random enemy minions"
	
	def awakenEffect(self):
		curGame = self.Game
		minions = curGame.minionsAlive(3-self.ID)
		if minions:
			if curGame.mode == 0:
				if curGame.guides:
					minions = [curGame.minions[3-self.ID][i] for i in curGame.guides.pop(0)]
				else:
					num = min(2, len(minions))
					minions = npchoice(minions, num, replace=False)
					curGame.fixedGuides.append(tuple([minion.position for minion in minions]))
				PRINT(curGame, "Transfer Student awakens and deals {} damage to enemy minions {}".format(damage, minions))
				self.dealsAOE(minions, [damage]*len(minions))
				
class TransferStudent_Academy(Minion_Dormantfor2turns):
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
				card = npchoice(curGame.RNGPools["Dual Class Cards"])
				curGame.fixedGuides.append(card)
			PRINT(curGame, "Transfer Student's battlecry adds a random Dual Class card to player's hand")
			curGame.Hand_Deck.addCardtoHand(card, self.ID, "type")
		return None
		
		
"""Mana 1 cards"""
class PenFlinger(Minion):
	Class, race, name = "Neutral", "", "Pen Flinger"
	mana, attack, health = 1, 1, 1
	index = "Academy~Neutral~Minion~1~1~1~None~Pen Flinger~Battlecry"
	requireTarget, keyWord, description = True, "", "Battlecry: Deal 1 damamge. Spellburst: Return this to your hand"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trigger_PenFlinger(self)]
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			PRINT(self.Game, "Pen Flinger's battlecry deals 1 damage to %s"%target.name)
			self.dealsDamage(target, 1)
		return target
		
class Trigger_PenFlinger(TrigBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["SpellBeenPlayed"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject.ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		minion = self.entity
		PRINT(minion.entity.Game, "After player plays a spell, Pen Flinger returns itself to player's hand.")
		minion.Game.returnMiniontoHand(minion, deathrattlesStayArmed=False)
		self.disconnect()
		try: minion.trigsBoard.remove(self)
		except: pass
		
		
class SphereofSapience(Minion):
	Class, name, description = "Neutral", "Sphere of Sapience", "At the start of your turn, look at your top card. You can put it on the bottom and lose 1 Durability"
	mana, attack, durability = 1, 0, 4
	index = "Academy~Neutral~Weapon~1~0~4~Sphere of Sapience~Neutral"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trigger_SphereofSapience(self)]
		
	def discoverDecided(self, option, info):
		if isinstance(option, MoveTopDeckCardtoBottom):
			self.Game.fixedGuides.append(False)
		else:
			self.Game.fixedGuides.append(True)
			PRINT(self.Game, "Sphere of Sapience moves player's top card in deck to the bottom")
			ownDeck = self.Game.Hand_Deck.decks[self.ID]
			ownDeck.insert(0, ownDeck.pop())
			self.entity.loseDurability()
			
class Trigger_SphereofSapience(TrigBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["TurnStarts"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return ID == self.entity.ID and self.entity.onBoard
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		curGame = self.entity.Game
		ownDeck = curGame.Hand_Deck.decks[self.entity.ID]
		if curGame.mode == 0:
			if curGame.guides:
				putatBottom = curGame.guides.pop(0)
				if putatBottom:
					PRINT(curGame, "At the start of turn, Sphere of Sapience allows player to move the top card in deck to the bottom")
					ownDeck.insert(0, ownDeck.pop())
					self.entity.loseDurability()
			else:
				if curGame.Hand_Deck.decks[self.entity.ID]:
					curGame.options = [ownDeck[-1], MoveTopDeckCardtoBottom()]
					curGame.Discover.startDiscover(self.entity)
				else:
					curGame.fixedGuides.append(False)
					return
					
class MoveTopDeckCardtoBottom:
	def __init__(self):
		self.name = "Move card to bottome"
		self.description = "Put this shown card to the bottom of your deck"
		
		
"""Mana 2 Cards"""
class CultNeophyte(Minion):
	Class, race, name = "Neutral", "", "Cult Neophyte"
	mana, attack, health = 2, 3, 2
	index = "Academy~Neutral~Minion~2~3~2~None~Cult Neophyte"
	requireTarget, keyWord, description = False, "", "Battlecry: Your opponent's spells cost (1) more next turn"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		PRINT(self.Game, "Cult Neophyte's battlecry makes enemy spell cards cost (1) more next turn.")
		self.Game.Manas.CardAuras_Backup.append(YourSpellsCost1MoreThisTurn(self.Game, 3-self.ID))
		return None
		
class YourSpellsCost1MoreThisTurn(TempManaEffect):
	def __init__(self, Game, ID):
		self.Game, self.ID = Game, ID
		self.changeby, self.changeto = +1, -1
		self.temporary = True
		self.auraAffected = []
		
	def applicable(self, target):
		return target.ID == self.ID and target.type == "Spell"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.applies(target[0])
		
	#持续整个回合的光环可以不必注册"ManaPaid"
	def auraAppears(self):
		for card in self.Game.Hand_Deck.hands[1]: self.applies(card)
		for card in self.Game.Hand_Deck.hands[2]: self.applies(card)
		
		try: self.Game.trigsBoard[self.ID]["CardEntersHand"].append(self)
		except: self.Game.trigsBoard[self.ID]["CardEntersHand"] = [self]
		self.Game.Manas.calcMana_All()
		
	#auraDisappears()可以尝试移除ManaPaid，当然没有反应，所以不必专门定义
	def selfCopy(self, game):
		return type(self)(game, self.ID)
		
		
"""Mana 4 Cards"""
class LorekeeperPolkelt(Minion):
	Class, race, name = "Neutral", "", "Lorekeeper Polkelt"
	mana, attack, health = 4, 4, 5
	index = "Academy~Neutral~Minion~4~4~5~None~Lorekeeper Polkelt~Battlecry~Legendary"
	requireTarget, keyWord, description = False, "", "Battlecry: Reorder your deck from the highest Cost card to the lowest Cost card"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		PRINT(self.Game, "Lorekeeper Polkelt's battlecry reorders player's deck from the highest Cost card to the lowest Cost card")
		ownDeck, cardDict = self.Game.Hand_Deck.decks[self.ID], {}
		for card in ownDeck:
			mana_0 = type(card).mana
			try: cardDict[mana_0].append(card)
			except: cardDict[mana_0] = [card]
		ownDeck = [] #After sorting using numpy, the 1st mana is the lowest
		for mana in np.sort(list(cardDict.keys())): #Doesn't reorder the card of same Cost
			ownDeck += cardDict[mana]
		return None
		
		
class WretchedTutor(Minion):
	Class, race, name = "Neutral", "", "Wretched Tutor"
	mana, attack, health = 4, 2, 5
	index = "Academy~Neutral~Minion~4~2~5~None~Wretched Tutor"
	requireTarget, keyWord, description = False, "", "Spellburst: Deal 2 damage to all other minions"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trigger_WretchedTutor(self)]
		
#可以通过宣传牌确认是施放法术之后触发
class Trigger_WretchedTutor(TrigBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["SpellBeenPlayed"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject.ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		minion = self.entity
		PRINT(minion.Game, "After player casts a spell, Wretched Tutor deals 2 damage to all other minions.")
		targets = minion.Game.minionsonBoard(minion.ID, minion) + minion.Game.minionsonBoard(3-minion.ID)
		minion.dealsAOE(targets, [2 for minion in targets])
		self.disconnect()
		try: self.entity.trigsBoard.remove(self)
		except: pass
		
		
"""Mana 5 Cards"""
class HeadmasterKelThuzad(Minion):
	Class, race, name = "Neutral", "", "Headmaster Kel'Thuzad"
	mana, attack, health = 5, 4, 6
	index = "Academy~Neutral~Minion~5~4~6~None~Headmaster Kel'Thuzad~Legendary"
	requireTarget, keyWord, description = False, "", "Spellburst: If the spell destroys any minions, summon them"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trigger_HeadmasterKelThuzad(self)]
		
#假设检测方式是在一张法术打出时开始记录直到可以触发法术迸发之前的两次死亡结算中所有死亡随从
class Trigger_HeadmasterKelThuzad(TrigBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["SpellBeenPlayed"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject.ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self.entity.Game, "After player casts a spell, Goody Two-Shields gains Divine Shield.")
		self.entity.getsKeyword("Divine Shield")
		self.disconnect()
		try: self.entity.trigsBoard.remove(self)
		except: pass
		
		
"""Mana 6 Cards"""
class OnyxMagescribe(Minion):
	Class, race, name = "Neutral", "Dragon", "Onyx Magescribe"
	mana, attack, health = 6, 4, 9
	index = "Academy~Neutral~Minion~6~4~9~Dragon~Onyx Magescribe"
	requireTarget, keyWord, description = False, "", "Spellburst: Add 2 random spells from your class to your hand"
	poolIdentifier = "Druid Spells"
	@classmethod
	def generatePool(cls, Game):
		classes, lists = [], []
		for Class in Game.Classes:
			lists.append([value for key, value in Game.ClassCards[Class].items() if "~Spell~" in key])
			classes.append(Class+" Spells")
		return classes, lists
		
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trigger_OnyxMagescribe(self)]
		
class Trigger_OnyxMagescribe(TrigBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["SpellBeenPlayed"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject.ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		curGame = self.entity.Game
		PRINT(curGame, "After player casts a spell, Onyx Magescribe adds 2 random spells from player's class to hand.")
		if curGame.mode == 0:
			if curGame.guides:
				spells = curGame.guides.pop(0)
			else:
				key = curGame.heroes[self.entity.ID].Class + " Spells"
				spells = npchoice(curGame.RNGPools[key], 2, replace=True)
				curGame.fixedGuides.append(tuple(spells))
			curGame.Hand_Deck.addCardtoHand(spells, self.entity.ID, "type")
		self.disconnect()
		try: self.entity.trigsBoard.remove(self)
		except: pass
		
		
"""Demon Hunter Cards"""
class AceHunterKreen(Minion):
	Class, race, name = "Demon Hunter,Hunter", "", "Ace Hunter Kreen"
	mana, attack, health = 3, 2, 4
	index = "Academy~Demon Hunter,Hunter~Minion~3~2~4~None~Ace Hunter Kreen~Legendary"
	requireTarget, keyWord, description = False, "", "Your other characters are Immune while attacking"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trigger_AceHunterKreen(self)]
		
class Trigger_AceHunterKreen(TrigBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["BattleStarted", "BattleFinished"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return subject.ID == self.entity.ID and subject != self.entity and self.entity.onBoard
		
	#不知道攻击具有受伤时召唤一个随从的扳机的随从时，飞刀能否对这个友方角色造成伤害
	#目前的写法是这个战斗结束信号触发在受伤之后
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		if signal == "BattleStarted":
			PRINT(self.entity.Game, "Before attack begins, Ace Hunter Kreen gives the attacking friendly character %s Immune"%subject.name)
			subject.status["Immune"] += 1
		else:
			PRINT(self.entity.Game, "After attack finished, Ace Hunter Kreen removes the Immune from the character %s."%subject.name)
			subject.status["Immune"] -= 1
			
			
class Magehunter(Minion):
	Class, race, name = "Demon Hunter", "", "Magehunter"
	mana, attack, health = 3, 2, 3
	index = "Academy~Demon Hunter~Minion~3~2~3~None~Magehunter~Rush"
	requireTarget, keyWord, description = False, "Rush", "Rush. Whenever this attacks a minion, Silence it"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trigger_Magehunter(self)]
		
class Trigger_Magehunter(TrigBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionAttackingMinion"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return subject == self.entity and self.entity.onBoard
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self.entity.Game, "When Magehunter attacks minion %s, it gets Silenced"%target.name)
		target.getsSilenced()
		
		
class Glide(Spell):
	Class, name = "Demon Hunter", "Glide"
	requireTarget, mana = False, 4
	index = "Academy~Demon Hunter~Spell~4~Glide~Outcast"
	description = "Shuffle your hand into your deck. Draw 4 cards. Outcast: Your opponent does the same"
	def effectCanTrigger(self):
		self.effectViable = self.Game.Hand_Deck.outcastcanTrigger(self)
		
	def shuffleHandintoDeck_Draw4(self, ID):
		HD = self.Game.Hand_Deck
		cards = HD.extractfromHand(None, True, ID)[0] #Extract all cards.
		for card in cards: #Cards will lose all status when shuffled into hand
			for trig in card.trigsBoard + card.trigsHand + card.trigsDeck:
				trig.disconnect()
			identity = card.identity
			card.__init__(self.Game, ID)
			card.identity = identity
		HD.shuffleCardintoDeck(cards, ID) #Initiated by self.
		for i in range(4): HD.drawCard(ID)
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		PRINT("Glide shuffles player's hand into deck and then let player draw 4 cards")
		Glide.shuffleHandintoDeck_Draw4(self, self.ID)
		if posinHand == 0 or posinHand == -1:
			PRINT("Glide's Outcast triggers and does the same for the opponent")
			Glide.shuffleHandintoDeck_Draw4(self, 3-self.ID)
		return None
		
		
class StarStudentStelina(Minion):
	Class, race, name = "Demon Hunter", "", "Star Student Stelina"
	mana, attack, health = 4, 4, 3
	index = "Academy~Demon Hunter~Minion~4~4~3~None~Star Student Stelina~Outcast~Legendary"
	requireTarget, keyWord, description = False, "", "Outcast: Look at 3 cards in your opponent's hand. Shuffle one of them into their deck"
	def shuffleOneHandintoDeck(self, i):
		card = self.Game.Hand_Deck.hands[3-self.ID][i]
		for trig in card.trigsBoard + card.trigsHand + card.trigsDeck:
			trig.disconnect()
		identity = card.identity
		card.__init__(self.Game, self.ID)
		card.identity = identity
		self.Game.Hand_Deck.shuffleCardintoDeck(card, 3-self.ID)
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if posinHand == 0 or posinHand == -1:
			curGame = self.Game
			if curGame.mode == 0:
				if curGame.guides:
					i = curGame.guides.pop(0)
					if i < 0: return None
					else:
						PRINT(curGame, "Star Student Stelina's Outcast triggers and shuffle an opponent's card into their deck")
						StarStudentStelina.shuffleOneHandintoDeck(self, i)
				else:
					enemyHand = curGame.Hand_Deck.hands[3-self.ID]
					if enemyHand:
						curGame.options = npchoice(enemyHand, min(3, len(enemyHand)), replace=False)
						curGame.Discover.startDiscover(self)
					else:
						curGame.fixedGuides.append(-1)
						return None
			return None
			
	def discoverDecided(self, option, info):
		for i, card in enumerate(self.Game.Hand_Deck.hands[3-self.ID]):
			if card == option:
				index = i
				self.Game.fixedGuides.append(i)
				break
		PRINT(self.Game, "Card from enemy hand is shuffled into their deck.")
		StarStudentStelina.shuffleOneHandintoDeck(self, index)
		
		
class CycleofHatred(Spell):
	Class, name = "Demon Hunter", "Cycle of Hatred"
	requireTarget, mana = False, 7
	index = "Academy~Demon Hunter~Spell~7~Cycle of Hatred"
	description = "Deal 3 damage to all minions. Summon a 3/3 Spirit for every minion killed"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		damage = (3 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		targets = self.Game.minionsonBoard(1) + self.Game.minionsonBoard(2)
		PRINT(self.Game, "Cycle of Hatred deals %d damage to all minions."%damage)
		dmgTakers = self.dealsAOE(targets, [damage]*len(targets))[0]
		num = 0
		for dmgTaker in dmgTakers:
			if dmgTaker.dead or dmgTaker.health < 1: num += 1
		if num > 0:
			PRINT(self.Game, "Cycle of Hatred summons %d 3/3 Spirits"%num)
			self.Game.summon([SpiritofVengeance(self.Game, self.ID)] * num, (-1, "totheRightEnd"), self.ID)
		return None
		
class SpiritofVengeance(Minion):
	Class, race, name = "Demon Hunter", "", "Spirit of Vengeance"
	mana, attack, health = 3, 3, 3
	index = "Academy~Demon Hunter~Minion~3~3~3~None~Spirit of Vengeance~Uncollectible"
	requireTarget, keyWord, description = False, "", ""
	
	
"""Druid Cards"""
class LightningBloom(Spell):
	Class, name = "Druid,Shaman", "Lightning Bloom"
	requireTarget, mana = False, 0
	index = "Academy~Druid,Shaman~Spell~0~Lightning Bloom~Overload"
	description = "Gain 2 Mana Crystals this turn only. Overload: (2)"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.overload = 2
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		PRINT(self.Game, "Lightning Bloom is cast and hero gains 2 Mana Crystals for this turn.")
		if self.Game.Manas.manas[self.ID] < 10:
			self.Game.Manas.manas[self.ID] += 1
		return None
		
class NatureStudies(Spell):
	Class, name = "Druid", "Nature Studies"
	requireTarget, mana = False, 1
	index = "Academy~Druid~Spell~1~Nature Studies"
	description = "Discover a spell. Your next one costs (1) less"
	poolIdentifier = "Druid Spells"
	@classmethod
	def generatePool(cls, Game):
		classes, lists = [], []
		for Class in Game.Classes:
			classes.append(Class+" Spells")
			lists.append([value for key, value in Game.ClassCards[Class].items() if "~Spell~" in key])
		return classes, lists
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if curGame.mode == 0:
			if curGame.guides:
				PRINT(curGame, "Nature Studies adds a spell to player's hand")
				curGame.Hand_Deck.addCardtoHand(curGame.guides.pop(0), self.ID, "type")
			else:
				key = classforDiscover(self)+" Spells"
				if "byOthers" in comment:
					spell = npchoice(curGame.RNGPools[key])
					curGame.fixedGuides.append(spell)
					PRINT(curGame, "Nature Studies is cast and adds a random spell to player's hand")
					curGame.Hand_Deck.addCardtoHand(spell, self.ID, "type")
				else:
					PRINT(curGame, "Nature Studies lets player discover a spell")
					spells = npchoice(curGame.RNGPools[key], 3, replace=False)
					curGame.options = [spell(curGame, self.ID) for spell in spells]
					curGame.Discover.startDiscover(self)
		PRINT(curGame, "Nature Studies makes player's next spell cost (1) less")
		tempAura = YourNextSpellCosts1Less(self.Game, self.ID)
		self.Game.Manas.CardAuras.append(tempAura)
		tempAura.auraAppears()
		return None
		
	def discoverDecided(self, option, info):
		self.Game.fixedGuides.append(type(option))
		PRINT(self.Game, "Spell %s is put into player's hand."%option.name)
		self.Game.Hand_Deck.addCardtoHand(option, self.ID)
		self.Game.sendSignal("DiscoveredCardPutintoHand", self.ID, self, option, 0, "")
		
class YourNextSpellCosts1Less(TempManaEffect):
	def __init__(self, Game, ID):
		self.Game, self.ID = Game, ID
		self.changeby, self.changeto = -1, -1
		#研习法术的光环都是跨回合的，所以没有temporary
		self.auraAffected = []
		
	def applicable(self, target):
		return target.ID == self.ID and target.type == "Spell"
		
	def selfCopy(self, game):
		return type(self)(game, self.ID)
		
		
#class ShandoWildclaw(Minion):
#	Class, race, name = "Hunter,Druid", "", "Shan'do Wildclaw"
#	mana, attack, health = 3, 3, 3
#	index = "Academy~Hunter,Druid~Minion~3~3~3~None~Shan'do Wildclaw~Choose One~Legendary"
#	requireTarget, keyWord, description = True, "", "Choose One- Give Beasts in your deck +1/+1; or Transform into a copy of a friendly Beast"
#	def __init__(self, Game, ID):
#		self.blank_init(Game, ID)
#		self.chooseOne = 1
#		self.options = [DemigodsFavor_Option(self), ShandosLesson_Option(self)]
#		
#	def returnTrue(self, choice=0):
#		return choice != 0
#		
#	def targetExists(self, choice=1):
#		for minion in self.Game.minionsonBoard(self.ID):
#			if "Beast" in minion.race: return True
#		return False
#		
#	def targetCorrect(self, target, choice=1):
#		return target.type == "Minion" and "Beast" in target.race and target != self and target.onBoard
#		
#	#对于抉择随从而言，应以与战吼类似的方式处理，打出时抉择可以保持到最终结算。但是打出时，如果因为鹿盔和发掘潜力而没有选择抉择，视为到对方场上之后仍然可以而没有如果没有
#	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
#		if choice < 1: #Choose Both aura on or choice == 0
#			PRINT(self.Game, "Shan'do Wildclaw gives all Beasts in player's deck +1/+1")
#			for card in self.Game.Hand_Deck.decks[self.ID]:
#				if card.type == "Minion" and "Beast" in card.race:
#					card.attack += 1
#					card.attack_Enchant += 1
#					card.health += 1
#					card.health_max += 1 #By default, this healthGain has to be non-negative.
#		if choice != 0 and target:
#			if target and self.dead == False and self.Game.minionPlayed == self and (self.onBoard or self.inHand): #战吼触发时自己不能死亡。
#				Copy = target.selfCopy(self.ID) if target.onBoard else type(target)(self.Game, self.ID)
#				PRINT(self.Game, "Shan'do Wildclaw transforms into a copy of friendly Beast %s"%target.name)
#				self.Game.transform(self, Copy)
#		return target
#		
#class (ChooseOneOption):
#	name, description = "", "Give Beasts in your deck +1/+1"
#	
#class (ChooseOneOption):
#	name, description = "", "Transform into a copy of a friendly Beast"
#	def available(self):
#		return self.entity.targetExists(1)
		
		
"""Hunter Cards"""


"""Mage Cards"""
class DevolvingMissiles(Spell):
	Class, name = "Mage,Shaman", "Devolving Missiles"
	requireTarget, mana = False, 1
	index = "Academy~Mage,Shaman~Spell~1~Devolving Missiles"
	description = "Shoot three missiles at random enemy minions that transform them into ones that cost (1) less"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		side, curGame = 3 - self.ID, self.Game
		if curGame.mode == 0:
			PRINT(curGame, "Devolving Missiles is cast and launches 3 missiles.")
			for i in range(3):
				if curGame.guides:
					i = curGame.guides.pop(0)
					if i < 0: minion = curGame.minions[side][i]
					else: break
				else:
					objs = curGame.minionsonBoard(side)
					if objs:
						minion = npchoice(objs)
						curGame.fixedGuides.append(minion.position)
					else:
						curGame.fixedGuides.append(-1)
						break #If no enemy character is alive, stop the cycle
				PRINT(curGame, "Devolving Missiles hits %s"%minion.name)
				if curGame.guides:
					newMinion = curGame.guides.pop(0)
				else:
					newMinion = npchoice(curGame.RNGPools["%d-Cost Minions to Summon"%max(0, type(minion).mana-1)])
					curGame.fixedGuides.append(newMinion)
				newMinion = newMinion(curGame, side)
				curGame.transform(minion, newMinion)
		return None
		
class WandThief(Minion):
	Class, race, name = "Mage,Rogue", "", "Wand Thief"
	mana, attack, health = 1, 1, 2
	index = "Academy~Mage,Rogue~Minion~1~1~2~None~Wand Thief~Combo"
	requireTarget, keyWord, description = False, "", "Combo: Discover a Mage spell"
	@classmethod
	def generatePool(cls, Game):
		return "Mage Spells", [value for key, value in Game.ClassCards["Mage"].items() if "~Spell~" in key]
		
	def effectCanTrigger(self):
		self.effectViable = self.Game.Counters.numCardsPlayedThisTurn[self.ID] > 0
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if curGame.mode == 0:
			if curGame.guides:
				spell = curGame.guides.pop(0)
				if spell: curGame.Hand_Deck.addCardtoHand(spell, self.ID, "type")
				else: return None
			else:
				if self.Game.Counters.numCardsPlayedThisTurn[self.ID] > 0:
					PRINT(self.Game, "Wand Thief' Combo triggers and lets player discover a Mage spell.")
					spells = npchoice(curGame.RNGPools["Mage Spells"], 3, replace=False)
					curGame.options = [spell(curGame, self.ID) for spell in spells]
					curGame.Discover.startDiscover(self)
				else:
					curGame.fixedGuides.append(None)
					return None
		return None
		
	def discoverDecided(self, option, info):
		self.Game.fixedGuides.append(type(option))
		PRINT(self.Game, "Mage spell %s is put into player's hand."%option.name)
		self.Game.Hand_Deck.addCardtoHand(option, self.ID)
		self.Game.sendSignal("DiscoveredCardPutintoHand", self.ID, self, option, 0, "")
		
		
class Combustion(Spell):
	Class, name = "Mage", "Combustion"
	requireTarget, mana = True, 3
	index = "Academy~Mage~Spell~3~Combustion"
	description = "Deal 4 damage to a minion. Any excess damages both neighbors"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			damage = (4 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			damageUsed = min(target.health, damage) if target.health > 0 else 0
			damageLeft = damage - damageUsed
			if target.onBoard and damageLeft:
				neighbors = self.Game.neighbors2(target)[0]
				targets = [target] + neighbors
				damages = [damageUsed] + [damageLeft] * len(neighbors)
				PRINT(self.Game, "Combustion deals %d damage to minion %s and %d damage to its neighbors"%(damageUsed, target.name, damageLeft))
				self.dealsAOE(targets, damages)
			elif damageLeft:
				PRINT(self.Game, "Combustion deals %d damage to minion %s"%(damageUsed, target.name))
				self.dealsDamage(target, damageUsed)
		return target
		
		
class MozakiMasterDuelist(Minion):
	Class, race, name = "Mage", "", "Mozaki, Master Duelist"
	mana, attack, health = 5, 3, 8
	index = "Academy~Mage~Minion~5~3~8~None~Mozaki, Master Duelist~Legendary"
	requireTarget, keyWord, description = False, "", "After you cast a spell, gain Spell Damage +1"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trigger_MozakiMasterDuelist(self)]
		
class Trigger_MozakiMasterDuelist(TrigBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["SpellBeenPlayed"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject.ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self.entity.Game, "After player casts a spell, Mozaki, Master Duelist gains Spell Damage +1")
		self.entity.getsKeyword("Spell Damage")
		
		
"""Paladin Cards"""
class FirstDayofSchool(Spell):
	Class, name = "Paladin", "First Day of School"
	requireTarget, mana = False, 0
	index = "Academy~Paladin~Spell~0~First Day of School"
	description = "Add 2 random 1-Cost minions to your hand"
	@classmethod
	def generatePool(cls, Game):
		return "1-Cost Minions", list(Game.MinionsofCost[1].values())
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if curGame.mode == 0:
			PRINT(curGame, "First Day of School adds 2 random 1-Cost minions to player's hand")
			if curGame.guides:
				minions = curGame.guides.pop(0)
			else:
				minions = npchoice(curGame.RNGPools["1-Cost Minions"], 2, replace=True)
				curGame.fixedGuides.append(tuple(minions))
			curGame.Hand_Deck.addCardtoHand(minions, self.ID, "type")
		return None
		
		
class GoodyTwoShields(Minion):
	Class, race, name = "Paladin", "", "Goody Two-Shields"
	mana, attack, health = 3, 4, 2
	index = "Academy~Paladin~Minion~3~4~2~None~Goody Two-Shields~Divine Shield"
	requireTarget, keyWord, description = False, "Divine Shield", "Spellburst: Gain Divine Shield"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trigger_GoodyTwoShields(self)]
		
#可以通过宣传牌确认是施放法术之后触发
class Trigger_DiligentNotetaker(TrigBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["SpellBeenPlayed"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject.ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self.entity.Game, "After player casts a spell, Goody Two-Shields gains Divine Shield.")
		self.entity.getsKeyword("Divine Shield")
		self.disconnect()
		try: self.entity.trigsBoard.remove(self)
		except: pass
		
		
"""Priest cards"""
class FrazzledFreshman(Minion):
	Class, race, name = "Priest", "", "Frazzled Freshman"
	mana, attack, health = 1, 1, 4
	index = "Academy~Priest~Minion~1~1~4~None~Frazzled Freshman"
	requireTarget, keyWord, description = False, "", ""
	
	
class BrittleboneDestroyer(Minion):
	Class, race, name = "Priest,Warlock", "", "Brittlebone Destroyer"
	mana, attack, health = 4, 3, 3
	index = "Academy~Priest,Warlock~Minion~4~3~3~None~Brittlebone Destroyer~Battlecry"
	requireTarget, keyWord, description = True, "", "Battlecry: If your hero's Health changed this turn, destroy a minion"
	
	def returnTrue(self, choice=0):
		return self.Game.Counters.heroChangedHealthThisTurn[self.ID]
		
	def effectCanTrigger(self):
		self.effectViable = self.Game.Counters.heroChangedHealthThisTurn[self.ID]
		
	def targetExists(self, choice=0):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target != self and target.onBoard
		
	#If the minion is shuffled into deck already, then nothing happens.
	#If the minion is returned to hand, move it from enemy hand into our hand.
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target and self.Game.Counters.heroChangedHealthThisTurn[self.ID]:
			PRINT(self.Game, "Brittlebone Destroyer's battlecry destroys minion %s"%target.name)
			if target.onBoard: target.dead = True
			elif target.inHand: self.Game.Hand_Deck.discardCard(target) #如果随从在手牌中则将其丢弃
		return target
		
		
class CabalAcolyte(Minion):
	Class, race, name = "Priest", "", "Cabal Acolyte"
	mana, attack, health = 4, 2, 6
	index = "Academy~Priest~Minion~4~2~6~None~Cabal Acolyte~Taunt"
	requireTarget, keyWord, description = False, "Taunt", "Taunt. Spellburst: Gain control of a random enemy minion with 2 or less Attack"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trigger_CabalAcolyte(self)]
		
class Trigger_CabalAcolyte(TrigBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["SpellBeenPlayed"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject.ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		curGame = self.entity.Game
		if curGame.mode == 0:
			PRINT(curGame, "After player casts a spell, Cabal Acolyte gains control of a random enemy minion with 2 or less Attack.")
			if curGame.guides:
				i = curGame.guides.pop(0)
			else:
				#假设这个是临时控制，与暗影狂乱一致
				minions = [minion.position for minion in curGame.minionsAlive(3-self.entity.ID) if minion.attack < 3]
				i = npchoice(minions) if minions else -1
				curGame.fixedGuides.append(i)
			if i > -1: curGame.minionSwitchSide(curGame.minions[3-self.entity.ID][i])
		self.disconnect()
		try: self.entity.trigsBoard.remove(self)
		except: pass
		
		
class DisciplinarianGandling(Minion):
	Class, race, name = "Priest,Warlock", "", "Disciplinarian Gandling"
	mana, attack, health = 4, 3, 6
	index = "Academy~Priest,Warlock~Minion~4~3~6~None~Disciplinarian Gandling~Legendary"
	requireTarget, keyWord, description = False, "", "After you play a minion, destroy it and summon a 4/4 Failed Student"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trigger_DisciplinarianGandling(self)]
		
class Trigger_DisciplinarianGandling(TrigBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionBeenPlayed"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject.ID == self.entity.ID and subject.onBoard
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		ID, game = self.entity.ID, self.entity.Game
		PRINT(game, "After player plays minion %s, Disciplinarian Gandling destroys it and summons a 4/4 Failed Student."%subject)
		game.Hand_Deck.addCardtoHand(type(subject), ID, "type")
		position, subject.dead = position, True
		game.gathertheDead()
		#Rule copied from Conjurer's Calling(Rise of Shadows)
		if position == 0: pos = -1 #Summon to the leftmost
		elif position < len(curGame.minionsonBoard(ID)): pos = position + 1
		else: pos = -1
		game.summon(FailedStudent(game, ID), pos, ID)
		
class FailedStudent(Minion):
	Class, race, name = "Priest,Warlock", "", "Failed Student"
	mana, attack, health = 4, 4, 4
	index = "Academy~Priest,Warlock~Minion~4~4~4~None~Failed Student~Uncollectible"
	requireTarget, keyWord, description = False, "", ""
	
	
class FleshGiant(Minion):
	Class, race, name = "Priest,Warlock", "", "Flesh Giant"
	mana, attack, health = 8, 8, 8
	index = "Academy~Priest,Warlock~Minion~8~8~8~None~Flesh Giant"
	requireTarget, keyWord, description = False, "", "Costs (1) less for each time your Hero's Health changed during your turn"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsHand = [Trigger_FleshGiant(self)]
		
	def selfManaChange(self):
		if self.inHand:
			self.mana -= self.Game.Counters.timesHeroChangedHealth_inOwnTurn[self.ID]
			self.mana = max(self.mana, 0)
			
class Trigger_FleshGiant(TrigHand):
	def __init__(self, entity):
		#假设这个费用改变扳机在“当你使用一张法术之后”。不需要预检测
		self.blank_init(entity, ["HeroChangedHealthinTurn"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.inHand and ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.Game.Manas.calcMana_Single(self.entity)
		
		
"""Rogue Cards"""
class InfiltratorLilian(Minion):
	Class, race, name = "Rogue", "", "Infiltrator Lilian"
	mana, attack, health = 4, 4, 2
	index = "Academy~Rogue~Minion~4~4~2~None~Infiltrator Lilian~Stealth~Deathrattle~Legendary"
	requireTarget, keyWord, description = False, "Stealth", "Stealth. Deathrattle: Summon a 4/2 Forsaken Lilian that attacks a random enemy"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [SummonForsakenLilian(self)]
		
class SummonForsakenLilian(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		curGame = self.entity.Game
		PRINT(curGame, "Deathrattle: Summon 4/2 Forsaken Lilian triggers.")
		minion = ForsakenLilian(curGame, self.entity.ID)
		curGame.summon(minion, self.entity.position+1, self.entity.ID)
		if curGame.mode == 0:
			enemy = None
			if curGame.guides:
				i, where = curGame.guides.pop(0)
				if where: enemy = curGame.find(i, where)
			else:
				enemies = curGame.charsAlive(3-self.entity.ID)
				if minion.onBoard and minion.health > 0 and not minion.dead and enemies:
					enemy = npchoice(enemies)
					curGame.fixedGuides.append((enemy.position, "minion%d"%minion.ID) if minion.type == "Minion" else (enemy.ID, "hero"))
				else:
					curGame.fixedGuides.append((0, ''))
			if enemy: #假设攻击会消耗攻击机会
				curGame.battle(minion, enemy, verifySelectable=False, resolveDeath=False)
				
class ForsakenLilian(Minion):
	Class, race, name = "Rogue", "", "Forsaken Lilian"
	mana, attack, health = 4, 4, 2
	index = "Academy~Rogue~Minion~4~4~2~None~Forsaken Lilian~Legendary~Uncollectible"
	requireTarget, keyWord, description = False, "", ""
	
	
class Steeldancer(Minion):
	Class, race, name = "Rogue,Warrior", "", "Steeldancer"
	mana, attack, health = 4, 4, 4
	index = "Academy~Rogue,Warrior~Minion~4~4~4~None~Steeldancer~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Summon a random minion with Cost equal to your weapons's Attack"
	poolIdentifier = "0-Cost Minions"
	@classmethod
	def generatePool(cls, Game):
		costs, lists = [], []
		for cost in Game.MinionsofCost.keys():
			costs.append("%d-Cost Minions"%cost)
			lists.append(list(Game.MinionsofCost[cost].values()))
		return costs, lists
		
	def effectCanTrigger(self):
		self.effectViable = self.Game.availableWeapon(self.ID) is not None
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		PRINT(curGame, "Steeldancer' battlecry summons a random minion with Cost equal to the attack of player's weapon")
		if curGame.mode == 0:
			if curGame.guides:
				minion = curGame.guides.pop(0)
			else:
				weapon = self.Game.availableWeapon(self.ID)
				if weapon:
					cost = max(weapon.attack, 0) #假设计数过高，超出了费用范围，则取最高的可选费用
					while True:
						if cost not in curGame.MinionsofCost: cost -= 1
						else: break
					minion = npchoice(curGame.RNGPools["%d-Cost Minions"%cost])
				else: minion = None
				curGame.fixedGuides.append(minion)
			if minion: curGame.summon(minion(curGame, self.ID), self.position+1, self.ID)
		return None
		
		
class DoctorKrastinov(Minion):
	Class, race, name = "Rogue", "", "Doctor Krastinov"
	mana, attack, health = 5, 4, 4
	index = "Academy~Rogue~Minion~5~4~4~None~Doctor Krastinov~Rush~Legendary"
	requireTarget, keyWord, description = False, "Rush", "Rush. Whenever this attacks, give your weapon +1/+1"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trigger_DoctorKrastinov(self)]
		
class Trigger_DoctorKrastinov(TrigBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionAttackingMinion", "MinionAttackingHero"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return subject == self.entity and self.entity.onBoard
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self.entity.Game, "When Doctor Krastinov attacks, player's weapon gain +1/+1")
		weapon = self.entity.Game.availableWeapon(self.entity.ID)
		if weapon: weapon.gainStat(1, 1)
		
"""Shaman Cards"""
class DiligentNotetaker(Minion):
	Class, race, name = "Shaman", "", "Diligent Notetaker"
	mana, attack, health = 2, 2, 3
	index = "Academy~Shaman~Minion~2~2~3~None~Diligent Notetaker"
	requireTarget, keyWord, description = False, "", "Spellburst: Return the spell to your hand"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trigger_DiligentNotetaker(self)]
		
#可以通过宣传牌确认是施放法术之后触发
class Trigger_DiligentNotetaker(TrigBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["SpellBeenPlayed"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject.ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self.entity.Game, "After player casts a spell, Diligent Notetaker returns it to player's hand.")
		self.entity.Game.Hand_Deck.addCardtoHand(type(subject), self.entity.ID, "type")
		self.disconnect()
		try: self.entity.trigsBoard.remove(self)
		except: pass
		
		
class TotemGoliath(Minion):
	Class, race, name = "Shaman", "Totem", "Totem Goliath"
	mana, attack, health = 5, 4, 5
	index = "Academy~Shaman~Minion~5~4~5~Totem~Totem Goliath~Deathrattle"
	requireTarget, keyWord, description = False, "", "Deathrattle: Summon all four basic totems. Overload: (2)"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.overload = 2
		self.deathrattles = [SummonAllBasicTotems(self)]
		
class SummonAllBasicTotems(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		minion, game = self.entity, self.entity.Game
		PRINT(game, "Deathrattle: Summon all four basic totems triggers")
		totems = [HealingTotem(game, minion.ID), SearingTotem(game, minion.ID), StoneclawTotem(game, minion.ID), WrathofAirTotem(game, minion.ID)]
		pos = (minion.position, "totheRight") if minion in game.minions[minion.ID] else (-1, "totheRightEnd")
		game.summon(totems, pos, minion.ID)
		
		
"""Warlock Cards"""
class Felosophy(Spell):
	Class, name = "Warlock,Demon Hunter", "Felosophy"
	requireTarget, mana = False, 1
	index = "Academy~Warlock,Demon Hunter~Spell~1~Felosophy~Outcast"
	description = "Copy the lowest Cost Demon in your hand. Outcast: Give both +1/+1"
	def effectCanTrigger(self):
		self.effectViable = self.Game.Hand_Deck.outcastcanTrigger(self)
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if curGame.mode == 0:
			PRINT(curGame, "Felosophy copies the lowest Cost Demon in player's hand")
			if curGame.guides:
				i = curGame.guides.pop(0)
			else:
				demons, highestCost = [], -np.inf
				for i, card in enumerate(curGame.Hand_Deck.hands[self.ID]):
					if card.type == "Minion" and "Demon" in card.race:
						if card.mana < highestCost: demons = [i], card.mana
						elif card.mana == highestCost: demons.append(i)
				i = npchoice(demons) if demons else -1
				curGame.fixedGuides.append(i)
			if i > -1:
				demon = curGame.Hand_Deck.hands[self.ID][i]
				Copy = demon.selfCopy(self.ID)
				curGame.Hand_Deck.addCardtoHand(Copy, self.ID)
				if posinHand == 0 or posinHand == -1:
					PRINT(curGame, "Felosophy's Outcast triggers and gives both of the Demons +1/+1")
					demon.buffDebuff(1, 1)
					Copy.buffDebuff(1, 1)
		return None
		
		
class BonewebEgg(Minion):
	Class, race, name = "Warlock", "", "Boneweb Egg"
	mana, attack, health = 2, 0, 2
	index = "Academy~Warlock~Minion~2~0~2~None~Boneweb Egg~Deathrattle"
	requireTarget, keyWord, description = False, "", "Deathrattle: Summon two 2/2 Hyenas"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [Summon2Spiders(self)]
		self.triggers["Discarded"] = [self.trigDeathrattles]
		
	def trigDeathrattles(self):
		PRINT(self.Game, "Boneweb Egg is discarded and triggers its Deathrattle")
		for trig in self.deathrattles:
			trig.trigger("TrigDeathrattle", self.ID, None, self, self.attack, "")
			
class Summon2Spiders(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		minion = self.entity
		pos = (minion.position, "totheRight") if minion in minion.Game.minions[minion.ID] else (-1, "totheRightEnd")
		PRINT(minion, "Deathrattle: Summon two 2/1 Spiders triggers.")
		minion.Game.summon([BonewebSpider(minion.Game, minion.ID)] * 2, pos, minion.ID)
		
class BonewebSpider(Minion):
	Class, race, name = "Warlock", "Beast", "Boneweb Spider"
	mana, attack, health = 1, 2, 1
	index = "Academy~Warlock~Minion~1~2~1~Beast~Boneweb Spider~Uncollectible"
	requireTarget, keyWord, description = False, "", ""
	
class ArchwitchWillow(Minion):
	Class, race, name = "Warlock", "", "Archwitch Willow"
	mana, attack, health = 9, 7, 7
	index = "Academy~Warlock~Minion~9~7~7~None~Archwitch Willow~Battlecry~Legendary"
	requireTarget, keyWord, description = False, "", "Battlecry: Summon a random Demon from your hand and deck"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		#假设从手牌中最左边向右检索，然后召唤
		PRINT(curGame, "Archwitch Willow's battlecry summons a random Demon from player's hand and deck")
		if curGame.mode == 0:
			ref = self
			#Summon a demon from deck
			if curGame.guides:
				i = curGame.guides.pop(0)
			else: #Find demons in hand
				demonsfromHand = [i for i, card in curGame.Hand_Deck.hands[self.ID] if card.type == "Minion" and "Demon" in card.race]
				i = npchoice(demonsfromHand) if demons and curGame.space(self.ID) else -1
				curGame.fixedGuides.append(i)
			if i > -1: ref = curGame.summonfromHand(i, self.ID, ref.position+1, self.ID)	
			#Summon a demon from deck
			if curGame.guides:
				i = curGame.guides.pop(0)
			else:
				demonsfromDeck = [i for i, card in curGame.Hand_Deck.decks[self.ID] if card.type == "Minion" and "Demon" in card.race]
				i = npchoice(demonsfromDeck) if demons and curGame.space(self.ID) else -1
				curGame.fixedGuides.append(i)
			if i > -1: ref = curGame.summonfromDeck(i, self.ID, ref.position+1, self.ID)	
		return None
		
		
"""Warrior Cards"""
class CeremonialMaul(Weapon):
	Class, name, description = "Warrior,Paladin", "Ceremonial Maul", "Spellburst: Summon a student with Taunt and stats equal to the spell's Cost"
	mana, attack, durability = 3, 2, 2
	index = "Academy~Warrior,Paladin~Weapon~3~2~2~Ceremonial Maul"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trigger_CeremonialMaul(self)]
		
class Trigger_CeremonialMaul(TrigBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["SpellBeenPlayed"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return subject.ID == self.entity.ID and self.entity.onBoard
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		game, stat = self.entity.Game, number
		PRINT(game, "After player casts a spell %s, Ceremonial Maul summons a Student with Taunt and stat equal to its Cost."%subject.name)
		if stat and game.space(self.entity.ID):
			cost = min(stat, 10)
			newIndex = "Academy~Warrior,Paladin~%d~%d~%d~Minion~None~Honor Student~Taunt~Uncollectible"%(cost, stat, stat)
			subclass = type("HonorStudent_Mutable_%d"%stat, (HonorStudent_Mutable_1, ),
							{"mana": cost, "attack": stat, "health": stat,
							"index": newIndex}
							)
			game.cardPool[newIndex] = subclass
			game.summon(subclass(game, self.entity.ID), -1, self.entity.ID)
		self.disconnect()
		try: self.entity.trigsBoard.remove(self)
		except: pass
		
class HonorStudent_Mutable_1(Minion):
	Class, race, name = "Warrior,Paladin", "", "Honor Student"
	mana, attack, health = 1, 1, 1
	index = "Academy~Warrior,Paladin~Minion~1~1~1~None~Honor Student~Taunt~Uncollectible"
	requireTarget, keyWord, description = False, "Taunt", "Taunt"
	
	
class Playmaker(Minion):
	Class, race, name = "Warrior", "", "Playmaker"
	mana, attack, health = 3, 4, 3
	index = "Academy~Warrior~Minion~3~4~3~None~Playmaker"
	requireTarget, keyWord, description = False, "", "After you play a Rush minion, summon a copy with 1 Health remaining"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trigger_Playmaker(self)]
		
class Trigger_Playmaker(TrigBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionBeenPlayed"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject.ID == self.entity.ID and subject.keyWords["Rush"] > 0
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self.entity.Game, "After player plays minion, Playmaker summons a 1 Health copy of it")
		Copy = subject.selfCopy(self.entity.ID)
		Copy.health = 1
		self.entity.Game.summon(Copy, self.entity.position+1, self.entity.ID)
		
		
class Troublemaker(Minion):
	Class, race, name = "Warrior", "", "Troublemaker"
	mana, attack, health = 8, 6, 8
	index = "Academy~Warrior~Minion~8~6~8~None~Troublemaker"
	requireTarget, keyWord, description = False, "", "At the end of your turn, summon two 3/3 Ruffians that attack random enemies"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trigger_Troublemaker(self)]
		
class Trigger_Troublemaker(TrigBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["TurnEnds"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		curGame = self.entity.Game
		PRINT(curGame, "At the end of turn, Troublemaker summons two 3/3 Ruffians that attack random enemies")
		ruffians = [Ruffian(curGame, self.entity.ID)] * 2
		curGame.summon(ruffians, (self.entity.position, "leftandRight"), self.entity.ID)
		if curGame.mode == 0:
			for i in range(2):
				enemy = None
				if curGame.guides:
					i, where = curGame.guides.pop(0)
					if where: enemy = curGame.find(i, where)
				else:
					targets = curGame.charsAlive(3-self.entity.ID)
					if ruffians[i].onBoard and not ruffians[i].dead and ruffians[i].health > 0 and targets:
						enemy = npchoice(targets)
						curGame.fixedGuides.append((enemy.position, "minion%d"%target1.ID) if target1.type == "Minion" else (target1.ID, "hero"))
					else:
						curGame.fixedGuides.append((0, ''))
				if enemy: curGame.battle(ruffians[i], enemy, verifySelectable=False, resolveDeath=False)
				
class Ruffian(Minion):
	Class, race, name = "Warrior", "", "Ruffian"
	mana, attack, health = 3, 3, 3
	index = "Academy~Warrior~Minion~3~3~3~None~Ruffian~Uncollectible"
	requireTarget, keyWord, description = False, "", ""
	
	
class Rattlegore(Minion):
	Class, race, name = "Warrior", "", "Rattlegore"
	mana, attack, health = 9, 9, 9
	index = "Academy~Warrior~Minion~9~9~9~None~Rattlegore~Deathrattle~Legendary"
	requireTarget, keyWord, description = False, "", "Deathrattle: Resummon this with -1/-1"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [ResummonwithMinus1Minus1(self)]
		
#假设一个随从以白字为准
class ResummonwithMinus1Minus1(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		#假设在手牌中会直接召唤一个复制。而且任何随从如果继承这个亡语都会生成各自对应的-1-1-1
		minion = self.entity
		if minion.health_0 > 1:
			minionType = type(minion)
			cost, attack, health = max(0, minionType.mana - 1), minion.attack_0 - 1, minion.health_0 - 1
			indices = minion.index.split('~')
			newIndex = "%s~%s~%d~%d~%d"%(indices[0], indices[1], cost, attack, health)
			length = len(indices) if not indices[-1] == "Uncollectible" else len(indices) - 1
			for i in range(len(5, indices)): newIndex += "~%s"%indices[i]
			newIndex += "~Uncollectible" #The new index will always be uncollectible
			subclass = type(minionType.__name__+"_Mutable_"+str(health), (minionType, ),
							{"mana": cost, "attack": attack, "health": health,
							"index": newIndex}
							)
						
		newMinion = subclass(minion.Game, minion.ID)
		pos = minion.position + 1 if minion in minion.Game.minions[minion.ID] else -1
		minion.Game.summon(newMinion, pos, minion.ID)
		
		
		
Academy_Indices = {"Academy~Neutral~Minion~1~1~1~None~Pen Flinger~Battlecry": PenFlinger,
					"Academy~Neutral~Weapon~1~0~4~Sphere of Sapience~Neutral": SphereofSapience,
					"Academy~Neutral~Minion~2~3~2~None~Cult Neophyte": CultNeophyte,
					"Academy~Neutral~Minion~4~4~5~None~Lorekeeper Polkelt~Battlecry~Legendary": LorekeeperPolkelt,
					"Academy~Neutral~Minion~4~2~5~None~Wretched Tutor": WretchedTutor,
					"Academy~Neutral~Minion~5~4~6~None~Headmaster Kel'Thuzad~Legendary": HeadmasterKelThuzad,
					"Academy~Neutral~Minion~6~4~9~Dragon~Onyx Magescribe": OnyxMagescribe,
					"Academy~Demon Hunter,Hunter~Minion~3~2~4~None~Ace Hunter Kreen~Legendary": AceHunterKreen,
					"Academy~Demon Hunter~Minion~3~2~3~None~Magehunter~Rush": Magehunter,
					"Academy~Demon Hunter~Spell~4~Glide~Outcast": Glide,
					"Academy~Demon Hunter~Minion~4~4~3~None~Star Student Stelina~Outcast~Legendary": StarStudentStelina,
					"Academy~Demon Hunter~Spell~7~Cycle of Hatred": CycleofHatred,
					"Academy~Demon Hunter~Minion~3~3~3~None~Spirit of Vengeance~Uncollectible": SpiritofVengeance,
					"Academy~Druid,Shaman~Spell~0~Lightning Bloom~Overload": LightningBloom,
					"Academy~Druid~Spell~1~Nature Studies": NatureStudies,
					#"Academy~Hunter,Druid~Minion~3~3~3~None~Shan'do Wildclaw~Choose One~Legendary": ShandoWildclaw
					"Academy~Mage,Shaman~Spell~1~Devolving Missiles": DevolvingMissiles,
					"Academy~Mage,Rogue~Minion~1~1~2~None~Wand Thief~Combo": WandThief,
					"Academy~Mage~Spell~3~Combustion": Combustion,
					"Academy~Mage~Minion~5~3~8~None~Mozaki, Master Duelist~Legendary": MozakiMasterDuelist,
					"Academy~Paladin~Spell~0~First Day of School": FirstDayofSchool,
					"Academy~Paladin~Minion~3~4~2~None~Goody Two-Shields~Divine Shield": GoodyTwoShields,
					"Academy~Priest~Minion~1~1~4~None~Frazzled Freshman": FrazzledFreshman,
					"Academy~Priest,Warlock~Minion~4~3~3~None~Brittlebone Destroyer~Battlecry": BrittleboneDestroyer,
					"Academy~Priest~Minion~4~2~6~None~Cabal Acolyte~Taunt": CabalAcolyte,
					"Academy~Priest,Warlock~Minion~4~3~6~None~Disciplinarian Gandling~Legendary": DisciplinarianGandling,
					"Academy~Priest,Warlock~Minion~4~4~4~None~Failed Student~Uncollectible": FailedStudent,
					"Academy~Priest,Warlock~Minion~8~8~8~None~Flesh Giant": FleshGiant,
					"Academy~Rogue~Minion~4~4~2~None~Infiltrator Lilian~Stealth~Deathrattle~Legendary": InfiltratorLilian,
					"Academy~Rogue~Minion~4~4~2~None~Forsaken Lilian~Legendary~Uncollectible": ForsakenLilian,
					"Academy~Rogue,Warrior~Minion~4~4~4~None~Steeldancer~Battlecry": Steeldancer,
					"Academy~Rogue~Minion~5~4~4~None~Doctor Krastinov~Rush~Legendary": DoctorKrastinov,
					"Academy~Shaman~Minion~2~2~3~None~Diligent Notetaker": DiligentNotetaker,
					"Academy~Shaman~Minion~5~4~5~Totem~Totem Goliath~Deathrattle": TotemGoliath,
					"Academy~Warlock,Demon Hunter~Spell~1~Felosophy~Outcast": Felosophy,
					"Academy~Warlock~Minion~2~0~2~None~Boneweb Egg~Deathrattle": BonewebEgg,
					"Academy~Warlock~Minion~1~2~1~Beast~Boneweb Spider~Uncollectible": BonewebSpider,
					"Academy~Warlock~Minion~9~7~7~None~Archwitch Willow~Battlecry~Legendary": ArchwitchWillow,
					"Academy~Warrior,Paladin~Weapon~3~2~2~Ceremonial Maul": CeremonialMaul,
					"Academy~Warrior,Paladin~Minion~1~1~1~None~Honor Student~Taunt~Uncollectible": HonorStudent_Mutable_1,
					"Academy~Warrior~Minion~3~4~3~None~Playmaker": Playmaker,
					"Academy~Warrior~Minion~8~6~8~None~Troublemaker": Troublemaker,
					"Academy~Warrior~Minion~3~3~3~None~Ruffian~Uncollectible": Ruffian,
					"Academy~Warrior~Minion~9~9~9~None~Rattlegore~Deathrattle~Legendary": Rattlegore,
					
					}