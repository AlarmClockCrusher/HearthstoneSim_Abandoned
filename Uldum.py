from CardTypes import *
from Triggers_Auras import *
from numpy.random import choice as npchoice
from numpy.random import randint as nprandint
from numpy.random import shuffle as npshuffle
from numpy import inf as npinf

from AcrossPacks import Lackeys

import copy

"""Saviors of Uldum"""

"""Mana 1 cards"""
class BeamingSidekick(Minion):
	Class, race, name = "Neutral", "", "Beaming Sidekick"
	mana, attack, health = 1, 1, 2
	index = "Uldum~Neutral~Minion~1~1~2~None~Beaming Sidekick~Battlecry"
	requireTarget, keyWord, description = True, "", "Battlecry: Give a friendly minion +2 Health"
	
	def targetExists(self, choice=0):
		return self.selectableFriendlyMinionExists(choice)
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.ID == self.ID and target != self and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			target.buffDebuff(0, 2)
		return target
		
		
class JarDealer(Minion):
	Class, race, name = "Neutral", "", "Jar Dealer"
	mana, attack, health = 1, 1, 1
	index = "Uldum~Neutral~Minion~1~1~1~None~Jar Dealer~Deathrattle"
	requireTarget, keyWord, description = False, "", "Deathrattle: Add a random 1-cost minion to your hand"
	poolIdentifier = "1-Cost Minions"
	@classmethod
	def generatePool(cls, Game):
		return "1-Cost Minions", list(Game.MinionsofCost[1].values())
		
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [Adda1CostMiniontoYourHand(self)]
		
class Adda1CostMiniontoYourHand(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		curGame = self.entity.Game
		if curGame.mode == 0:
			if curGame.guides:
				minion = curGame.guides.pop(0)
			else:
				minion = npchoice(self.rngPool("1-Cost Minions"))
				curGame.fixedGuides.append(minion)
			curGame.Hand_Deck.addCardtoHand(minion, self.entity.ID, "type")
			
	def text(self, CHN):
		return "亡语：随机将一张法力值消耗为(1)的随从牌置入你的手牌" if CHN else "Deathrattle: Add a random 1-cost minion to your hand"
		
		
class MoguCultist(Minion):
	Class, race, name = "Neutral", "", "Mogu Cultist"
	mana, attack, health = 1, 1, 1
	index = "Uldum~Neutral~Minion~1~1~1~None~Mogu Cultist~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: If your board is full of Mogu Cultists, sacrifice them all and summon Highkeeper Ra"
	#强制要求场上有总共有7个魔古信徒，休眠物会让其效果无法触发
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		minions = self.Game.minionsonBoard(self.ID)
		if len(minions) == 7 and all(minion.name == "Mogu Cultist" for minion in minions):
			self.Game.killMinion(None, minions)
			self.Game.gathertheDead()
			self.Game.summon(HighkeeperRa(self.Game, self.ID), -1, self.ID)
		return None
		
class HighkeeperRa(Minion):
	Class, race, name = "Neutral", "", "Highkeeper Ra"
	mana, attack, health = 10, 20, 20
	index = "Uldum~Neutral~Minion~10~20~20~None~Highkeeper Ra~Legendary~Uncollectible"
	requireTarget, keyWord, description = False, "", "At the end of your turn, deal 20 damage to all enemies"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_HighkeeperRa(self)]
		
class Trig_HighkeeperRa(TrigBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["TurnEnds"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and ID == self.entity.ID
		
	def text(self, CHN):
		return "在你的回合结束时，对所有敌人造成20点伤害" if CHN else "At the end of your turn, deal 20 damage to all enemies"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		targets = [self.entity.Game.heroes[3-self.entity.ID]] + self.entity.Game.minionsonBoard(3-self.entity.ID)
		self.entity.dealsAOE(targets, [20 for obj in targets])
		
		
class Murmy(Minion):
	Class, race, name = "Neutral", "Murloc", "Murmy"
	mana, attack, health = 1, 1, 1
	index = "Uldum~Neutral~Minion~1~1~1~Murloc~Murmy~Reborn"
	requireTarget, keyWord, description = False, "Reborn", "Reborn"
	
	
"""Mana 2 cards"""
class BugCollector(Minion):
	Class, race, name = "Neutral", "", "Bug Collector"
	mana, attack, health = 2, 2, 1
	index = "Uldum~Neutral~Minion~2~2~1~None~Bug Collector~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Summon a 1/1 Locust with Rush"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.Game.summon(Locust(self.Game, self.ID), self.pos+1, self.ID)
		return None
		
class Locust(Minion):
	Class, race, name = "Neutral", "Beast", "Locust"
	mana, attack, health = 1, 1, 1
	index = "Uldum~Neutral~Minion~1~1~1~Beast~Locust~Rush~Uncollectible"
	requireTarget, keyWord, description = False, "Rush", "Rush"
	
	
class DwarvenArchaeologist(Minion):
	Class, race, name = "Neutral", "", "Dwarven Archaeologist"
	mana, attack, health = 2, 2, 3
	index = "Uldum~Neutral~Minion~2~2~3~None~Dwarven Archaeologist"
	requireTarget, keyWord, description = False, "", "After you Discover a card, reduce its cost by (1)"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_DwarvenArchaeologist(self)]
		
class Trig_DwarvenArchaeologist(TrigBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["PutinHandbyDiscover"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		#不知道被发现的牌如果来自对手，是否会享受减费。如Griftah
		return self.entity.onBoard and ID == self.entity.ID and target.ID == self.entity.ID
		
	def text(self, CHN):
		return "在你发现一张卡牌后，使其法力值消耗减少(1)点" if CHN else "After you Discover a card, reduce its cost by (1)"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		ManaMod(target, changeby=-1, changeto=-1).applies()
		self.entity.Game.Manas.calcMana_Single(target)
		
		
class Fishflinger(Minion):
	Class, race, name = "Neutral", "Murloc", "Fishflinger"
	mana, attack, health = 2, 3, 2
	index = "Uldum~Neutral~Minion~2~3~2~Murloc~Fishflinger~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Add a random Murloc to each player's hand"
	poolIdentifier = "Murlocs"
	@classmethod
	def generatePool(cls, Game):
		return "Murlocs", list(Game.MinionswithRace["Murloc"].values())
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if curGame.mode == 0:
			if curGame.guides:
				murloc1, murloc2 = curGame.guides.pop(0)
			else:
				murloc1, murloc2 = npchoice(self.rngPool("Murlocs"), 2, replace=False)
				curGame.fixedGuides.append((murloc1, murloc2))
			curGame.Hand_Deck.addCardtoHand(murloc1, self.ID, "type")
			curGame.Hand_Deck.addCardtoHand(murloc2, 3-self.ID, "type")
		return None
		
		
class InjuredTolvir(Minion):
	Class, race, name = "Neutral", "", "Injured Tol'vir"
	mana, attack, health = 2, 2, 6
	index = "Uldum~Neutral~Minion~2~2~6~None~Injured Tol'vir~Taunt~Battlecry"
	requireTarget, keyWord, description = False, "Taunt", "Taunt. Battlecry: Deal 3 damage to this minion"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.dealsDamage(self, 3)
		return None
		
		
class KoboldSandtrooper(Minion):
	Class, race, name = "Neutral", "", "Kobold Sandtrooper"
	mana, attack, health = 2, 2, 1
	index = "Uldum~Neutral~Minion~2~2~1~None~Kobold Sandtrooper~Deathrattle"
	requireTarget, keyWord, description = False, "", "Deathrattle: Deal 3 damage to the enemy hero"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [Deal3DamagetoEnemyHero(self)]
		
class Deal3DamagetoEnemyHero(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.dealsDamage(self.entity.Game.heroes[3-self.entity.ID], 3)
		
	def text(self, CHN):
		return "亡语：对敌方英雄造成3点伤害" if CHN else "Deathrattle: Deal 3 damage to the enemy hero"
		
		
class NefersetRitualist(Minion):
	Class, race, name = "Neutral", "", "Neferset Ritualist"
	mana, attack, health = 2, 2, 3
	index = "Uldum~Neutral~Minion~2~2~3~None~Neferset Ritualist~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Restore adjacent minions to full Health"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if self.onBoard:
			for minion in self.Game.neighbors2(self)[0]:
				heal = minion.health_max * (2 ** self.countHealDouble())
				self.restoresHealth(minion, heal)
		return None
		
		
class QuestingExplorer(Minion):
	Class, race, name = "Neutral", "", "Questing Explorer"
	mana, attack, health = 2, 2, 3
	index = "Uldum~Neutral~Minion~2~2~3~None~Questing Explorer~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: If you control a Quest, draw a card"
	def effCanTrig(self):
		self.effectViable = self.Game.Secrets.mainQuests[self.ID] != [] or self.Game.Secrets.sideQuests[self.ID] != []
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if self.Game.Secrets.mainQuests[self.ID] != [] or self.Game.Secrets.sideQuests[self.ID] != []:
			self.Game.Hand_Deck.drawCard(self.ID)
		return None
		
		
class QuicksandElemental(Minion):
	Class, race, name = "Neutral", "Elemental", "Quicksand Elemental"
	mana, attack, health = 2, 3, 2
	index = "Uldum~Neutral~Minion~2~3~2~Elemental~Quicksand Elemental~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Give all enemy minions -2 Attack this turn"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		for minion in self.Game.minionsonBoard(3-self.ID):
			minion.buffDebuff(-2, 0, "EndofTurn")
		return None
		
		
class SerpentEgg(Minion):
	Class, race, name = "Neutral", "", "Serpent Egg"
	mana, attack, health = 2, 0, 3
	index = "Uldum~Neutral~Minion~2~0~3~None~Serpent Egg~Deathrattle"
	requireTarget, keyWord, description = False, "", "Deathrattle: Summon a 3/4 Sea Serpent"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [SummonaSeaSerpent(self)]
		
class SummonaSeaSerpent(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.Game.summon(SeaSerpent(self.entity.Game, self.entity.ID), self.entity.pos+1, self.entity.ID)
		
	def text(self, CHN):
		return "召唤一条3/4的海蛇" if CHN else "Deathrattle: Summon a 3/4 Sea Serpent"
		
class SeaSerpent(Minion):
	Class, race, name = "Neutral", "Beast", "Sea Serpent"
	mana, attack, health = 3, 3, 4
	index = "Uldum~Neutral~Minion~3~3~4~Beast~Sea Serpent~Uncollectible"
	requireTarget, keyWord, description = False, "", ""
	
	
class SpittingCamel(Minion):
	Class, race, name = "Neutral", "Beast", "Spitting Camel"
	mana, attack, health = 2, 2, 4
	index = "Uldum~Neutral~Minion~2~2~4~Beast~Spitting Camel"
	requireTarget, keyWord, description = False, "", "At the end of your turn, deal 1 damage to another random friendly minion"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_SpittingCamel(self)]
		
class Trig_SpittingCamel(TrigBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["TurnEnds"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and ID == self.entity.ID
		
	def text(self, CHN):
		return "在你的回合结束时，随机对另一个友方随从造成1点伤害" if CHN else "At the end of your turn, deal 1 damage to another random friendly minion"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		curGame = self.entity.Game
		if curGame.mode == 0:
			if curGame.guides:
				i = curGame.guides.pop(0)
			else:
				minions = curGame.minionsAlive(self.entity.ID, self.entity)
				i = npchoice(minions).pos if minions else -1
				curGame.fixedGuides.append(-1)
			if i > -1: self.entity.dealsDamage(curGame.minions[self.entity.ID][i], 1)
			
			
class TempleBerserker(Minion):
	Class, race, name = "Neutral", "", "Temple Berserker"
	mana, attack, health = 2, 1, 2
	index = "Uldum~Neutral~Minion~2~1~2~None~Temple Berserker~Reborn"
	requireTarget, keyWord, description = False, "Reborn", "Reborn. Has +2 Attack while damaged"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.auras["Enrage"] = StatAura_Enrage(self, 2)
		
		
class Vilefiend(Minion):
	Class, race, name = "Neutral", "Demon", "Vilefiend"
	mana, attack, health = 2, 2, 2
	index = "Uldum~Neutral~Minion~2~2~2~Demon~Vilefiend~Lifesteal"
	requireTarget, keyWord, description = False, "Lifesteal", "Lifesteal"
	
	
class ZephrystheGreat(Minion):
	Class, race, name = "Neutral", "Elemental", "Zephrys the Great"
	mana, attack, health = 2, 3, 2
	index = "Uldum~Neutral~Minion~2~3~2~Elemental~Zephrys the Great~Battlecry~Legendary"
	requireTarget, keyWord, description = False, "", "Battlecry: If your deck has no duplicates, wish for the perfect card"
	name_CN = "了不起的 杰弗里斯"
	poolIdentifier = "Basic and Classic Cards"
	@classmethod
	def generatePool(cls, Game):
		basicandClassicCards = [value for key, value in Game.cardPool.items() if (key.startswith("Basic") or key.startswith("Classic")) and "~Uncollectible" not in key]
		return "Basic and Classic Cards", basicandClassicCards
		
	def effCanTrig(self):
		self.effectViable = self.Game.Hand_Deck.noDuplicatesinDeck(self.ID)
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		HD = curGame.Hand_Deck
		if HD.noDuplicatesinDeck(self.ID) and self.ID == curGame.turn:
			if curGame.mode == 0:
				if curGame.guides:
					HD.addCardtoHand(curGame.guides.pop(0), self.ID, "type")
				else:
					if "byOthers" in comment:
						card = npchoice(self.rngPool("Basic and Classic Cards"))
						curGame.fixedGuides.append(card)
						curGame.Hand_Deck.addCardtoHand(card, self.ID, "type")
					else:
						curGame.Discover.typeCardName(self)
		return None
		
"""Mana 3 cards"""
class Candletaker(Minion):
	Class, race, name = "Neutral", "", "Candletaker"
	mana, attack, health = 3, 3, 2
	index = "Uldum~Neutral~Minion~3~3~2~None~Candletaker~Reborn"
	requireTarget, keyWord, description = False, "Reborn", "Reborn"
	
	
class DesertHare(Minion):
	Class, race, name = "Neutral", "Beast", "Desert Hare"
	mana, attack, health = 3, 1, 1
	index = "Uldum~Neutral~Minion~3~1~1~Beast~Desert Hare~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Summon two 1/1 Desert Hares"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		pos = (self.pos, "leftandRight") if self.onBoard else (-1, "totheRightEnd")
		self.Game.summon([DesertHare(self.Game, self.ID) for i in range(2)], pos, self.ID)
		return None
		
		
class GenerousMummy(Minion):
	Class, race, name = "Neutral", "", "Generous Mummy"
	mana, attack, health = 3, 5, 4
	index = "Uldum~Neutral~Minion~3~5~4~None~Generous Mummy~Reborn"
	requireTarget, keyWord, description = False, "Reborn", "Reborn. Your opponent's cards cost (1) less"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.auras["Your opponent's cards cost (1) less"] = ManaAura(self, changeby=-1, changeto=-1)
		
	def manaAuraApplicable(self, subject):
		return subject.ID != self.ID
		
		
class GoldenScarab(Minion):
	Class, race, name = "Neutral", "Beast", "Golden Scarab"
	mana, attack, health = 3, 2, 2
	index = "Uldum~Neutral~Minion~3~2~2~Beast~Golden Scarab~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Discover a 4-cost card"
	poolIdentifier = "4-Cost Cards as Druid"
	@classmethod
	def generatePool(cls, Game):
		classCards = {s : [value for key, value in Game.ClassCards[s].items() if key.split('~')[3] == '4'] for s in Game.Classes}
		classCards["Neutral"] = [value for key, value in Game.NeutralCards.items() if key.split('~')[3] == '4']
		return ["4-Cost Cards as %s"%Class for Class in Game.Classes], \
			[classCards[Class]+classCards["Neutral"] for Class in Game.Classes]
			
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if self.ID == curGame.turn:
			if curGame.mode == 0:
				if curGame.guides:
					curGame.Hand_Deck.addCardtoHand(curGame.guides.pop(0), self.ID, "type", byDiscover=True)
				else:
					key = "4-Cost Cards as "+classforDiscover(self)
					if "byOthers" in comment:
						card = npchoice(self.rngPool(key))
						curGame.fixedGuides.append(card)
						curGame.Hand_Deck.addCardtoHand(card, self.ID, "type", byDiscover=True)
					else:
						cards = npchoice(self.rngPool(key), 3, replace=False)
						curGame.options = [card(curGame, self.ID) for card in cards]
						curGame.Discover.startDiscover(self)
		return None
		
	def discoverDecided(self, option, info):
		self.Game.fixedGuides.append(type(option))
		self.Game.Hand_Deck.addCardtoHand(option, self.ID, byDiscover=True)
		
		
class HistoryBuff(Minion):
	Class, race, name = "Neutral", "", "History Buff"
	mana, attack, health = 3, 3, 4
	index = "Uldum~Neutral~Minion~3~3~4~None~History Buff"
	requireTarget, keyWord, description = False, "", "Whenever you play a minion, give a random minion in your hand +1/+1"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_HistoryBuff(self)]
		
class Trig_HistoryBuff(TrigBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionPlayed"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject.ID == self.entity.ID and subject != self.entity
		
	def text(self, CHN):
		return "每当你使用一张随从牌，随机使你手牌中的一张随从牌获得+1/+1" if CHN else "Whenever you play a minion, give a random minion in your hand +1/+1"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		curGame = self.entity.Game
		if curGame.mode == 0:
			if curGame.guides:
				i = curGame.guides.pop(0)
			else:
				minions = [i for i, card in enumerate(curGame.Hand_Deck.hands[self.entity.ID]) if card.type == "Minion"]
				i = npchoice(minions) if minions else -1
				curGame.fixedGuides.append(i)
			if i > -1: curGame.Hand_Deck.hands[self.entity.ID][i].buffDebuff(1, 1)
			
			
class InfestedGoblin(Minion):
	Class, race, name = "Neutral", "", "Infested Goblin"
	mana, attack, health = 3, 2, 3
	index = "Uldum~Neutral~Minion~3~2~3~None~Infested Goblin~Taunt~Deathrattle"
	requireTarget, keyWord, description = False, "Taunt", "Taunt. Deathrattle: Add two 1/1 Scarabs with Taunt to your hand"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [AddtwoScarabswithTaunttoYourHand(self)]
		
class AddtwoScarabswithTaunttoYourHand(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.Game.Hand_Deck.addCardtoHand([Scarab_Uldum, Scarab_Uldum], self.entity.ID, "type")
		
	def text(self, CHN):
		return "亡语：将两张1/1并具有嘲讽的甲虫置入你的手牌" if CHN else "Deathrattle: Add two 1/1 Scarabs with Taunt to your hand"
		
class Scarab_Uldum(Minion):
	Class, race, name = "Neutral", "Beast", "Scarab"
	mana, attack, health = 1, 1, 1
	index = "Uldum~Neutral~Minion~1~1~1~Beast~Scarab~Taunt~Uncollectible"
	requireTarget, keyWord, description = False, "Taunt", "Taunt"
	
	
class MischiefMaker(Minion):
	Class, race, name = "Neutral", "", "Mischief Maker"
	mana, attack, health = 3, 3, 3
	index = "Uldum~Neutral~Minion~3~3~3~None~Mischief Maker~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Swap the top deck of your deck with your opponent's"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		#不知道如果一方牌库为空时会如何,假设一方牌库为空时不触发效果
		if self.Game.Hand_Deck.decks[1] != [] and self.Game.Hand_Deck.decks[2] != []:
			card1 = self.Game.Hand_Deck.removeDeckTopCard(1)
			card2 = self.Game.Hand_Deck.removeDeckTopCard(2)
			card1.ID, card2.ID = 2, 1
			self.Game.Hand_Deck.decks[1].append(card2)
			self.Game.Hand_Deck.decks[2].append(card1)
			card1.entersDeck()
			card2.entersDeck()
		return None
		
		
class VulperaScoundrel(Minion):
	Class, race, name = "Neutral", "", "Vulpera Scoundrel"
	mana, attack, health = 3, 2, 3
	index = "Uldum~Neutral~Minion~3~2~3~None~Vulpera Scoundrel~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Discover a spell or pick a mystery choice"
	poolIdentifier = "Druid Spells"
	@classmethod
	def generatePool(cls, Game):
		return [Class+" Spells" for Class in Game.Classes], \
				[[value for key, value in Game.ClassCards[Class].items() if "~Spell~" in key] for Class in Game.Classes]
				
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if self.ID == curGame.turn:
			if curGame.mode == 0:
				if curGame.guides:
					spell = curGame.guides.pop(0)
					curGame.Hand_Deck.addCardtoHand(spell, self.ID, "type", byDiscover=True)
				else:
					key = classforDiscover(self)+" Spells"
					if "byOthers" in comment:
						spell = npchoice(self.rngPool(key))
						curGame.fixedGuides.append(spell)
						curGame.Hand_Deck.addCardtoHand(spell, self.ID, "type", byDiscover=True)
					else:
						spells = npchoice(self.rngPool(key), 3, replace=False)
						curGame.options = [spell(curGame, self.ID) for spell in spells]
						curGame.options.append(MysteryChoice())
						curGame.Discover.startDiscover(self)
		return None
		
	def discoverDecided(self, option, info):
		curGame = self.Game
		if option.name != "Mystery Choice!":
			curGame.fixedGuides.append(type(option))
			curGame.Hand_Deck.addCardtoHand(option, self.ID, byDiscover=True)
		else:
			spell = npchoice(self.rngPool(classforDiscover(self)+" Spells"))
			curGame.fixedGuides.append(spell)
			curGame.Hand_Deck.addCardtoHand(spell, self.ID, "type")
			
class MysteryChoice:
	name = "Mystery Choice!"
	description = "Add a random spell to your hand"
	def __init__(self):
		self.name = type(self).name
		self.description = type(self).description
		
		
"""Mana 4 cards"""
class BoneWraith(Minion):
	Class, race, name = "Neutral", "", "Bone Wraith"
	mana, attack, health = 4, 2, 5
	index = "Uldum~Neutral~Minion~4~2~5~None~Bone Wraith~Reborn~Taunt"
	requireTarget, keyWord, description = False, "Reborn,Taunt", "Reborn, Taunt"
	
	
class BodyWrapper(Minion):
	Class, race, name = "Neutral", "", "Body Wrapper"
	mana, attack, health = 4, 4, 4
	index = "Uldum~Neutral~Minion~4~4~4~None~Body Wrapper~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Discover a friendly minion that died this game. Shuffle it into your deck"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if self.ID == curGame.turn:
			if curGame.mode == 0:
				if curGame.guides:
					minion = curGame.guides.pop(0)
					if minion:
						curGame.Hand_Deck.shuffleCardintoDeck(minion(curGame, self.ID), self.ID)
				else:
					indices, p = discoverProb(curGame.Counters.minionsDiedThisGame[self.ID])
					if indices:
						if "byOthers" in comment:
							minion = curGame.cardPool[npchoice(indices, p=p)]
							curGame.fixedGuides.append(minion)
							curGame.Hand_Deck.shuffleCardintoDeck(minion(curGame, self.ID), self.ID)
						else:
							indices = npchoice(indices, min(len(indices), 3), p=p, replace=False)
							minions = [curGame.cardPool[index] for index in indices]
							curGame.options = [minion(curGame, self.ID) for minion in minions]
							curGame.Discover.startDiscover(self)
					else: curGame.fixedGuides.append(None)
		return None
		
	def discoverDecided(self, option, info):
		self.Game.fixedGuides.append(type(option))
		self.Game.Hand_Deck.shuffleCardintoDeck(option, self.ID)
		
		
class ConjuredMirage(Minion):
	Class, race, name = "Neutral", "", "Conjured Mirage"
	mana, attack, health = 4, 3, 10
	index = "Uldum~Neutral~Minion~4~3~10~None~Conjured Mirage~Taunt"
	requireTarget, keyWord, description = False, "Taunt", "Taunt. At the start of your turn, shuffle this minion into your deck"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_ConjuredMirage(self)]
		
class Trig_ConjuredMirage(TrigBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["TurnStarts"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and ID == self.entity.ID
		
	def text(self, CHN):
		return "在你的回合开始时，将该随从洗入你的牌库" if CHN else "At the start of your turn, shuffle this minion into your deck"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		#随从在可以触发回合开始扳机的时机一定是不结算其亡语的。可以安全地注销其死亡扳机
		self.entity.Game.returnMiniontoDeck(self.entity, self.entity.ID, self.entity.ID, deathrattlesStayArmed=False)
		
		
class SunstruckHenchman(Minion):
	Class, race, name = "Neutral", "", "Sunstruck Henchman"
	mana, attack, health = 4, 6, 5
	index = "Uldum~Neutral~Minion~4~6~5~None~Sunstruck Henchman"
	requireTarget, keyWord, description = False, "", "At the start of your turn, this has a 50% chance to fall asleep"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_SunstruckHenchman(self)]
		
class Trig_SunstruckHenchman(TrigBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["TurnStarts", "TurnEnds"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and ID == self.entity.ID
		
	def text(self, CHN):
		return "在你的回合开始时，该随从有50%的几率陷入沉睡" if CHN else "At the start of your turn, this has a 50% chance to fall asleep"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		if signal == "TurnStarts":
			curGame = self.entity.Game
			if curGame.mode == 0:
				if curGame.guides:
					sleeps = curGame.guides.pop(0)
				else:
					sleeps = nprandint(2)
					curGame.fixedGuides.append(sleeps)
				if sleeps:
					self.entity.marks["Can't Attack"] += 1
		else: self.entity.marks["Can't Attack"] -= 1 #signal == "TurnEnds"
		
		
"""Mana 5 cards"""
class FacelessLurker(Minion):
	Class, race, name = "Neutral", "", "Faceless Lurker"
	mana, attack, health = 5, 3, 3
	index = "Uldum~Neutral~Minion~5~3~3~None~Faceless Lurker~Taunt~Battlecry"
	requireTarget, keyWord, description = False, "Taunt", "Taunt. Battlecry: Double this minion's Health"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.statReset(False, self.health * 2)
		return None
		
		
class DesertObelisk(Minion):
	Class, race, name = "Neutral", "", "Desert Obelisk"
	mana, attack, health = 5, 0, 5
	index = "Uldum~Neutral~Minion~5~0~5~None~Desert Obelisk"
	requireTarget, keyWord, description = False, "", "If your control 3 of these at the end of your turn, deal 5 damage to a random enemy"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_DesertObelisk(self)]
		
class Trig_DesertObelisk(TrigBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["TurnEnds"])
		
	def checkDesertObelisk(self):
		return sum(minion.name == "Desert Obelisk" for minion in self.entity.Game.minionsonBoard(self.entity.ID)) > 2
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and ID == self.entity.ID and self.checkDesertObelisk()
		
	def text(self, CHN):
		return "如果你在你的回合结束时控制3座沙漠方尖碑，则随机对一个敌人造成5点伤害" if CHN \
				else "If your control 3 of these at the end of your turn, deal 5 damage to a random enemy"
				
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		curGame = self.entity.Game
		if curGame.mode == 0:
			enemy = None
			if curGame.guides:
				i, where = curGame.guides.pop(0)
				if where: enemy = curGame.find(i, where)
			else:
				enemies = curGame.charsAlive(3-self.entity.ID)
				if enemies:
					enemy = npchoice(enemies)
					curGame.fixedGuides.append((enemy.pos, enemy.type+str(enemy.ID)))
				else:
					curGame.fixedGuides.append((0, ''))
			if enemy: self.entity.dealsDamage(enemy, 5)
			
			
class MortuaryMachine(Minion):
	Class, race, name = "Neutral", "Mech", "Mortuary Machine"
	mana, attack, health = 5, 8, 8
	index = "Uldum~Neutral~Minion~5~8~8~Mech~Mortuary Machine"
	requireTarget, keyWord, description = False, "", "After your opponent plays a minion, give it Reborn"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_MortuaryMachine(self)]
		
class Trig_MortuaryMachine(TrigBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionBeenPlayed"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject.ID != self.entity.ID
		
	def text(self, CHN):
		return "在你的对手使用一张随从牌后，使其获得复生" if CHN else "After your opponent plays a minion, give it Reborn"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		subject.getsKeyword("Reborn")
		
		
class PhalanxCommander(Minion):
	Class, race, name = "Neutral", "", "Phalanx Commander"
	mana, attack, health = 5, 4, 5
	index = "Uldum~Neutral~Minion~5~4~5~None~Phalanx Commander"
	requireTarget, keyWord, description = False, "", "Your Taunt minions have +2 Attack"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.auras["Your Taunt minions have +2 Attack"] = BuffAura_PhalanxCommander(self)
		
#Refer to Warsong Commander's aura
class BuffAura_PhalanxCommander(HasAura_toMinion):
	def __init__(self, minion):
		self.minion = minion
		self.signals, self.auraAffected = ["MinionAppears", "MinionTauntKeywordChange"], []
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.minion.onBoard and subject.ID == self.minion.ID \
				and ((signal == "MinionAppears" and subject.keyWords["Charge"] > 0) or signal == "MinionTauntKeywordChange")
				
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.applies(signal, subject)
		
	def applies(self, signal, subject):
		if signal == "MinionAppears":
			if subject.keyWords["Taunt"] > 0:
				Stat_Receiver(subject, self, 2, 0).effectStart()
		else: #signal == "MinionTauntKeywordChange"
			if subject.keyWords["Taunt"] > 0:
				notAffectedPreviously = True
				for receiver, receiver in self.auraAffected[:]:
					if subject == receiver:
						notAffectedPreviously = False
						break
				if notAffectedPreviously:
					Stat_Receiver(subject, self, 1, 0).effectStart()
			elif subject.keyWords["Taunt"] < 1:
				for receiver, receiver in self.auraAffected[:]:
					if subject == receiver:
						receiver.effectClear()
						break
						
	def auraAppears(self):
		for minion in self.minion.Game.minionsonBoard(self.minion.ID):
			self.applies("MinionAppears", minion) #The signal here is a placeholder and directs the function to first time aura applicatioin
			
		try: self.minion.Game.trigsBoard[self.minion.ID]["MinionAppears"].append(self)
		except: self.minion.Game.trigsBoard[self.minion.ID]["MinionAppears"] = [self]
		try: self.minion.Game.trigsBoard[self.minion.ID]["MinionTauntKeywordChange"].append(self)
		except: self.minion.Game.trigsBoard[self.minion.ID]["MinionTauntKeywordChange"] = [self]
		
	def selfCopy(self, recipient): #The recipientMinion is the minion that deals the Aura.
		return type(self)(recipient)
	#可以通过HasAura_toMinion的createCopy方法复制
	
	
class WastelandAssassin(Minion):
	Class, race, name = "Neutral", "", "Wasteland Assassin"
	mana, attack, health = 5, 4, 2
	index = "Uldum~Neutral~Minion~5~4~2~None~Wasteland Assassin~Stealth~Reborn"
	requireTarget, keyWord, description = False, "Stealth,Reborn", "Stealth, Reborn"
	
"""Mana 6 cards"""
class BlatantDecoy(Minion):
	Class, race, name = "Neutral", "", "Blatant Decoy"
	mana, attack, health = 6, 5, 5
	index = "Uldum~Neutral~Minion~6~5~5~None~Blatant Decoy~Deathrattle"
	requireTarget, keyWord, description = False, "", "Deathrattle: Each player summons the lowest Cost minion from their hand"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [BothPlayersSummonLowestCostMinionfromHand(self)]
		
class BothPlayersSummonLowestCostMinionfromHand(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		curGame = self.entity.Game
		if curGame.mode == 0:
			for ID in range(1, 3):
				if curGame.guides:
					i = curGame.guides.pop(0)
				else: #假设是依次召唤，如果召唤前一个随从时进行了某些结算，则后面的召唤可能受之影响
					minions, highestCost = [], npinf
					for i, card in enumerate(curGame.Hand_Deck.hands[ID]):
						if card.type == "Minion":
							if card.mana < highestCost: minions, highestCost = [i], card.mana
							elif card.mana == highestCost: minions.append(i)
					i = npchoice(minions) if minions and curGame.space(ID) > 0 else -1
					curGame.fixedGuides.append(i)
				if i > -1: curGame.summonfromHand(i, ID, -1, self.entity.ID)
				
	def text(self, CHN):
		return "亡语：每个玩家从手牌中召唤法力值消耗最低的随从" if CHN \
				else "Deathrattle: Each player summons the lowest Cost minion from their hand"
				
				
class KhartutDefender(Minion):
	Class, race, name = "Neutral", "", "Khartut Defender"
	mana, attack, health = 6, 3, 4
	index = "Uldum~Neutral~Minion~6~3~4~None~Khartut Defender~Taunt~Reborn~Deathrattle"
	requireTarget, keyWord, description = False, "Taunt,Reborn", "Taunt, Reborn. Deathrattle: Restore 4 Health to your hero"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [Restore4HealthtoHero(self)]
		
class Restore4HealthtoHero(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		heal = 4 * (2 ** self.entity.countHealDouble())
		self.entity.restoresHealth(self.entity.Game.heroes[self.entity.ID], heal)	
		
	def text(self, CHN):
		heal = 4 * (2 ** self.entity.countHealDouble())
		return "亡语：为你的英雄恢复%d点生命值"%heal if CHN else "Deathrattle: Restore %d Health to your hero"%heal
		
		
"""Mana 7 cards"""
class Siamat(Minion):
	Class, race, name = "Neutral", "Elemental", "Siamat"
	mana, attack, health = 7, 6, 6
	index = "Uldum~Neutral~Minion~7~6~6~Elemental~Siamat~Battlecry~Legendary"
	requireTarget, keyWord, description = False, "", "Battlecry: Gain 2 of Rush, Taunt, Divine Shield, or Windfury (your choice)"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.choices = []
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if self.ID == curGame.turn:
			self.choices = [SiamatsHeart(), SiamatsShield(), SiamatsSpeed(), SiamatsWind()]
			for num in range(2):
				if curGame.mode == 0:
					if curGame.guides:
						option = curGame.guides.pop(0)()
						self.getsKeyword(option.keyWord)
					else:
						if "byOthers" in comment:
							choices = npchoice(self.choices, 2, replace=True)
							curGame.fixedGuides.append(type(choices[0]))
							curGame.fixedGuides.append(type(choices[1]))
							self.getsKeyword(choices[0].keyWord)
							self.getsKeyword(choices[1].keyWord)
							break
						else:
							curGame.options = self.choices
							curGame.Discover.startDiscover(self)
		return None
		
	def discoverDecided(self, option, info):
		self.Game.fixedGuides.append(type(option))
		self.getsKeyword(option.keyWord)
		try: self.choices.remove(option)
		except: pass
		
class SiamatsHeart:
	def __init__(self):
		self.name = "Siamat's Heart"
		self.description = "Give Siamat Taunt"
		self.keyWord = "Taunt"
		
class SiamatsShield:
	def __init__(self):
		self.name = "Siamat's Shield"
		self.description = "Give Siamat Divined Shield"
		self.keyWord = "Divine Shield"
		
class SiamatsSpeed:
	def __init__(self):
		self.name = "Siamat's Speed"
		self.description = "Give Siamat Rush"
		self.keyWord = "Rush"
		
class SiamatsWind:
	def __init__(self):
		self.name = "Siamat's Wind"
		self.description = "Give Siamat Windfury"
		self.keyWord = "Windfury"
		
		
class WastelandScorpid(Minion):
	Class, race, name = "Neutral", "Beast", "Wasteland Scorpid"
	mana, attack, health = 7, 3, 9
	index = "Uldum~Neutral~Minion~7~3~9~Beast~Wasteland Scorpid~Poisonous"
	requireTarget, keyWord, description = False, "Poisonous", "Poisonous"
	
	
class WrappedGolem(Minion):
	Class, race, name = "Neutral", "", "Wrapped Golem"
	mana, attack, health = 7, 7, 5
	index = "Uldum~Neutral~Minion~7~7~5~None~Wrapped Golem~Reborn"
	requireTarget, keyWord, description = False, "Reborn", "Reborn. At the end of your turn, summon a 1/1 Scarab with Taunt"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_WrappedGolem(self)]
		
class Trig_WrappedGolem(TrigBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["TurnEnds"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and ID == self.entity.ID
		
	def text(self, CHN):
		return "在你的回合结束时，召唤一只1/1并具有嘲讽的甲虫" if CHN else "At the end of your turn, summon a 1/1 Scarab with Taunt"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.Game.summon(Scarab_Uldum(self.entity.Game, self.entity.ID), self.entity.pos+1, self.entity.ID)
		
		
"""Mana 8 cards"""
class Octosari(Minion):
	Class, race, name = "Neutral", "Beast", "Octosari"
	mana, attack, health = 8, 8, 8
	index = "Uldum~Neutral~Minion~8~8~8~Beast~Octosari~Deathrattle~Legendary"
	requireTarget, keyWord, description = False, "", "Deathrattle: Draw 8 cards"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [Draw8Cards(self)]
		
class Draw8Cards(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		for i in range(8): self.entity.Game.Hand_Deck.drawCard(self.entity.ID)
		
	def text(self, CHN):
		return "亡语：抽八张牌" if CHN else "Deathrattle: Draw 8 cards"
		
		
class PitCrocolisk(Minion):
	Class, race, name = "Neutral", "Beast", "Pit Crocolisk"
	mana, attack, health = 8, 5, 6
	index = "Uldum~Neutral~Minion~8~5~6~Beast~Pit Crocolisk~Battlecry"
	requireTarget, keyWord, description = True, "", "Battlecry: Deal 5 damage"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			self.dealsDamage(target, 5) #dealsDamage() on targets in grave/deck will simply pass.
		return target
		
		
"""Mana 9 cards"""
class AnubisathWarbringer(Minion):
	Class, race, name = "Neutral", "", "Anubisath Warbringer"
	mana, attack, health = 9, 9, 6
	index = "Uldum~Neutral~Minion~9~9~6~None~Anubisath Warbringer~Deathrattle"
	requireTarget, keyWord, description = False, "", "Deathrattle: Give all minions in your hand +3/+3"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [GiveAllMinionsinHandPlus3Plus3(self)]
		
class GiveAllMinionsinHandPlus3Plus3(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		for card in self.entity.Game.Hand_Deck.hands[self.entity.ID]:
			if card.type == "Minion":
				card.buffDebuff(3, 3)
				
	def text(self, CHN):
		return "亡语：使你手牌中的所有随从牌获得+3/+3" if CHN else "Deathrattle: Give all minions in your hand +3/+3"
		
"""Mana 10 cards"""
class ColossusoftheMoon(Minion):
	Class, race, name = "Neutral", "", "Colossus of the Moon"
	mana, attack, health = 10, 10, 10
	index = "Uldum~Neutral~Minion~10~10~10~None~Colossus of the Moon~Divine Shield~Reborn~Legendary"
	requireTarget, keyWord, description = False, "Divine Shield,Reborn", "Divine Shield, Reborn"
	
	
class KingPhaoris(Minion):
	Class, race, name = "Neutral", "", "King Phaoris"
	mana, attack, health = 10, 5, 5
	index = "Uldum~Neutral~Minion~10~5~5~None~King Phaoris~Battlecry~Legendary"
	requireTarget, keyWord, description = False, "", "Battlecry: For each spell in your hand, summon a minion of the same Cost"
	poolIdentifier = "0-Cost Minions to Summon"
	@classmethod
	def generatePool(cls, Game):
		return ["%d-Cost Minions to Summon"%cost for cost in Game.MinionsofCost.keys()], \
				[list(Game.MinionsofCost[cost].values()) for cost in Game.MinionsofCost.keys()]
	#不知道如果手中法术的法力值没有对应随从时会如何
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if curGame.mode == 0:
			if curGame.guides:
				minions = curGame.guides.pop(0)
			else:
				minions = []
				for card in curGame.Hand_Deck.hands[self.ID]:
					if card.type == "Spell":
						cost = card.mana
						while cost not in self.Game.MinionsofCost:
							cost -= 1
						minions.append(npchoice(self.rngPool("%d-Cost Minions to Summon"%cost)))
				curGame.fixedGuides.append(tuple(minions))
			if minions:
				curGame.summon([minion(curGame, self.ID) for minion in minions], (self.pos+1, "totheRight"), self.ID)
		return None
		
		
class LivingMonument(Minion):
	Class, race, name = "Neutral", "", "Living Monument"
	mana, attack, health = 10, 10, 10
	index = "Uldum~Neutral~Minion~10~10~10~None~Living Monument~Taunt"
	requireTarget, keyWord, description = False, "Taunt", "Taunt"
	
	
"""Druid cards"""
class UntappedPotential(Quest):
	Class, name = "Druid", "Untapped Potential"
	requireTarget, mana = False, 1
	index = "Uldum~Druid~Spell~1~Untapped Potential~~Quest~Legendary"
	description = "Quest: End 4 turns with any unspent Mana. Reward: Orissian Tear"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_UntappedPotential(self)]
		
class Trig_UntappedPotential(QuestTrigger):
	def __init__(self, entity):
		self.blank_init(entity, ["TurnEnds"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		if self.entity.Game.Manas.manas[self.entity.ID] > 0:
			self.counter += 1
			if self.counter > 3:
				self.disconnect()
				try: self.entity.Game.Secrets.mainQuests[self.entity.ID].remove(self.entity)
				except: pass
				OssirianTear(self.entity.Game, self.entity.ID).replaceHeroPower()
				
class OssirianTear(HeroPower):
	mana, name, requireTarget = 0, "Ossirian Tear", False
	index = "Druid~Hero Power~0~Ossirian Tear"
	description = "Passive Hero Power. Your Choose One cards have both effects combined"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		
	def available(self, choice=0):
		return False
		
	def use(self, target=None, choice=0):
		return 0
		
	def appears(self):
		self.Game.status[self.ID]["Choose Both"] += 1
		
	def disappears(self):
		if self.Game.status[self.ID]["Choose Both"] > 0:
			self.Game.status[self.ID]["Choose Both"] -= 1
			
			
class WorthyExpedition(Spell):
	Class, name = "Druid", "Worthy Expedition"
	requireTarget, mana = False, 1
	index = "Uldum~Druid~Spell~1~Worthy Expedition"
	description = "Discover a Choose One card"
	poolIdentifier = "Choose One Cards"
	@classmethod
	def generatePool(cls, Game):
		return "Choose One Cards", [value for key, value in Game.ClassCards["Druid"].items() if "~Choose One" in key]
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if curGame.mode == 0:
			if curGame.guides:
				curGame.Hand_Deck.addCardtoHand(curGame.guides.pop(0), self.ID, "type", byDiscover=True)
			else:
				if self.ID != curGame.turn or "byOthers" in comment:
					card = npchoice(self.rngPool("Choose One Cards"))
					curGame.fixedGuides.append(card)
					curGame.Hand_Deck.addCardtoHand(card, self.ID, "type", byDiscover=True)
				else:
					cards = npchoice(self.rngPool("Choose One Cards"), 3, replace=False)
					curGame.options = [card(curGame, self.ID) for card in cards]
					curGame.Discover.startDiscover(self)
		return None
		
	def discoverDecided(self, option, info):
		self.Game.fixedGuides.append(type(option))
		self.Game.Hand_Deck.addCardtoHand(option, self.ID, byDiscover=True)
		
		
class CrystalMerchant(Minion):
	Class, race, name = "Druid", "", "Crystal Merchant"
	mana, attack, health = 2, 1, 4
	index = "Uldum~Druid~Minion~2~1~4~None~Crystal Merchant"
	requireTarget, keyWord, description = False, "", "If you have any unspent Mana at the end of your turn, draw a card"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_CrystalMerchant(self)]
		
class Trig_CrystalMerchant(TrigBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["TurnEnds"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and ID == self.entity.ID
		
	def text(self, CHN):
		return "在你的回合结束时，如果你有未使用的法力水晶，抽一张牌" if CHN \
				else "If you have any unspent Mana at the end of your turn, draw a card"
				
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		if self.entity.Game.Manas.manas[self.entity.ID] > 0:
			self.entity.Game.Hand_Deck.drawCard(self.entity.ID)
			
			
class BEEEES(Spell):
	Class, name = "Druid", "BEEEES!!!"
	requireTarget, mana = True, 3
	index = "Uldum~Druid~Spell~3~BEEEES!!!"
	description = "Choose a minion. Summon four 1/1 Bees that attack it"
	def available(self):
		return self.selectableMinionExists() and self.Game.space(self.ID) > 0
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		#假设没有目标时也会生效，只是召唤的蜜蜂不会攻击
		#不知道卡德加翻倍召唤出的随从是否会攻击那个随从，假设不会
		bees = [Bee_Uldum(self.Game, self.ID) for i in range(4)]
		self.Game.summon(bees, (-1, "totheRightEnd"), self.ID)
		if target:
			for bee in bees:
				#召唤的蜜蜂需要在场上且存活，同时目标也需要在场且存活
				if bee.onBoard and bee.health > 0 and bee.dead == False and target.onBoard and target.health > 0 and target.dead == False:
					self.Game.battle(bee, target, verifySelectable=False, useAttChance=False, resolveDeath=False)
		return target
		
class Bee_Uldum(Minion):
	Class, race, name = "Druid", "Beast", "Bee"
	mana, attack, health = 1, 1, 1
	index = "Uldum~Druid~Minion~1~1~1~Beast~Bee~Uncollectible"
	requireTarget, keyWord, description = False, "", ""
	
	
class GardenGnome(Minion):
	Class, race, name = "Druid", "", "Garden Gnome"
	mana, attack, health = 4, 2, 3
	index = "Uldum~Druid~Minion~4~2~3~None~Garden Gnome~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: If you're holding a spell that costs (5) or more, summon two 2/2 Treants"
	
	def effCanTrig(self):
		self.effectViable = self.Game.Hand_Deck.holdingSpellwith5CostorMore(self.ID)
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if self.Game.Hand_Deck.holdingSpellwith5CostorMore(self.ID):
			pos = (self.pos, "leftandRight") if self.onBoard else (-1, "totheRightEnd")
			self.Game.summon([Treant_Uldum(self.Game, self.ID) for i in range(2)], pos, self.ID)
		return None
		
		
class Treant_Uldum(Minion):
	Class, race, name = "Druid", "", "Treant"
	mana, attack, health = 2, 2, 2
	index = "Uldum~Druid~Minion~2~2~2~None~Treant~Uncollectible"
	requireTarget, keyWord, description = False, "", ""
	
	
class AnubisathDefender(Minion):
	Class, race, name = "Druid", "", "Anubisath Defender"
	mana, attack, health = 5, 3, 5
	index = "Uldum~Druid~Minion~5~3~5~None~Anubisath Defender~Taunt"
	requireTarget, keyWord, description = False, "Taunt", "Taunt. Costs (0) if you've cast a spell this turn that costs (5) or more"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsHand = [Trig_AnubisathDefender(self)]
		
	def selfManaChange(self):
		cardsThisTurn = self.Game.Counters.cardsPlayedThisTurn[self.ID]
		if self.inHand and any("~Spell~" in index and mana > 4 \
								for index, mana in zip(cardsThisTurn["Indices"], cardsThisTurn["ManasPaid"])):
			self.mana = 0
			
class Trig_AnubisathDefender(TrigHand):
	def __init__(self, entity):
		self.blank_init(entity, ["SpellBeenPlayed", "TurnStarts", "TurnEnds"]) #不需要预检测
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.inHand and (signal[0] == 'T' or (number > 4 and subject.ID == self.entity.ID))
		
	def text(self, CHN):
		return "在本回合中，如果你施放过法力值消耗大于或等于(5)的法术，则这张牌的法力值消耗为(0)点" if CHN \
				else "Costs (0) if you've cast a spell this turn that costs (5) or more"
				
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.Game.Manas.calcMana_Single(self.entity)
		
		
class ElisetheEnlightened(Minion):
	Class, race, name = "Druid", "", "Elise the Enlightened"
	mana, attack, health = 5, 5, 5
	index = "Uldum~Druid~Minion~5~5~5~None~Elise the Enlightened~Battlecry~Legendary"
	requireTarget, keyWord, description = False, "", "Battlecry: If your deck has no duplicates, duplicate your hand"
	
	def effCanTrig(self):
		self.effectViable = self.Game.Hand_Deck.noDuplicatesinDeck(self.ID)
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		HD = self.Game.Hand_Deck
		if HD.noDuplicatesinDeck(self.ID):
			for card in HD.hands[self.ID][:]:
				HD.addCardtoHand(card.selfCopy(self.ID), self.ID)
		return None
		
		
class OasisSurger(Minion):
	Class, race, name = "Druid", "Elemental", "Oasis Surger"
	mana, attack, health = 5, 3, 3
	index = "Uldum~Druid~Minion~5~3~3~Elemental~Oasis Surger~Rush~Choose One"
	requireTarget, keyWord, description = False, "Rush", "Rush. Choose One: Gain +2/+2; or Summon a copy of this minion"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.chooseOne = 1
		# 0: Gain +2/+2; 1: Summon a copy.
		self.options = [FocusedBurst_Option(self), DivideandConquer_Option(self)]
		
	#对于抉择随从而言，应以与战吼类似的方式处理，打出时抉择可以保持到最终结算。但是打出时，如果因为鹿盔和发掘潜力而没有选择抉择，视为到对方场上之后仍然可以而没有如果没有
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if choice < 1:
			self.buffDebuff(2, 2)
		if choice != 0:
			Copy = self.selfCopy(self.ID) if self.onBoard else type(self)(self.Game, self.ID)
			self.Game.summon(Copy, self.pos+1, self.ID)
		return None
		
class FocusedBurst_Option(ChooseOneOption):
	name, description = "Focused Burst", "Gain +2/+2"
	
class DivideandConquer_Option(ChooseOneOption):
	name, description = "Divide and Conquer", "Summon a copy of this minion"
	def available(self):
		return self.entity.Game.space(self.entity.ID) > 0
		
		
class HiddenOasis(Spell):
	Class, name = "Druid", "Hidden Oasis"
	requireTarget, mana = True, 6
	index = "Uldum~Druid~Spell~6~Hidden Oasis~Choose One"
	description = "Choose One: Summon a 6/6 Ancient with Taunt; or Restore 12 Health"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.chooseOne = 1
		self.options = [BefriendtheAncient_Option(self), DrinktheWater_Option(self)]
		
	def returnTrue(self, choice=0):
		return choice != 0
		
	def available(self):
		#当场上有全选光环时，变成了一个指向性法术，必须要有一个目标可以施放。
		if self.Game.status[self.ID]["Choose Both"] > 0:
			return self.selectableCharacterExists(1)
		else:
			return self.Game.space(self.ID) > 0 or self.selectableCharacterExists(1)
			
	def text(self, CHN):
		heal = 12 * (2 ** self.countHealDouble())
		return "抉择：召唤一个6/6并具有嘲讽的古树； 或者恢复%d点生命值"%heal if CHN \
				else "Choose One: Summon a 6/6 Ancient with Taunt; or Restore %d Health"%heal
				
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if choice != 0:
			if target:
				heal = 12 * (2 ** self.countHealDouble())
				self.restoresHealth(target, heal)
		if choice < 1:
			self.Game.summon(VirnaalAncient(self.Game, self.ID), -1, self.ID)
		return target
		
class BefriendtheAncient_Option(ChooseOneOption):
	name, description = "Befriend the Ancient", "Summon a 6/6 Ancient with Taunt"
	index = "Uldum~Druid~Spell~6~Befriend the Ancient~Uncollectible"
	def available(self):
		return self.entity.Game.space(self.entity.ID) > 0
		
class DrinktheWater_Option(ChooseOneOption):
	name, description = "Drink the Water", "Restore 12 Health"
	index = "Uldum~Druid~Spell~6~Drink the Water~Uncollectible"
	def available(self):
		return self.entity.selectableCharacterExists(1)
		
class BefriendtheAncient(Spell):
	Class, name = "Druid", "Befriend the Ancient"
	requireTarget, mana = False, 6
	index = "Uldum~Druid~Spell~6~Befriend the Ancient~Uncollectible"
	description = "Summon a 6/6 Ancient with Taunt"
	def available(self):
		return self.Game.space(self.ID)
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.Game.summon(VirnaalAncient(self.Game, self.ID), -1, self.ID)
		return None
		
class DrinktheWater(Spell):
	Class, name = "Druid", "Drink the Water"
	requireTarget, mana = True, 6
	index = "Uldum~Druid~Spell~6~Drink the Water~Uncollectible"
	description = "Restore 12 Health"
	def text(self, CHN):
		heal = 12 * (2 ** self.countHealDouble())
		return "恢复%d点生命值"%heal if CHN else "Restore %d Health"%heal
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			heal = 12 * (2 ** self.countHealDouble())
			self.restoresHealth(target, heal)
		return target
		
class VirnaalAncient(Minion):
	Class, race, name = "Druid", "", "Vir'naal Ancient"
	mana, attack, health = 6, 6, 6
	index = "Uldum~Druid~Minion~6~6~6~None~Vir'naal Ancient~Taunt~Uncollectible"
	requireTarget, keyWord, description = False, "Taunt", "Taunt"
	
	
class Overflow(Spell):
	Class, name = "Druid", "Overflow"
	requireTarget, mana = False, 7
	index = "Uldum~Druid~Spell~7~Overflow"
	description = "Restore 5 Health to all characters. Draw 5 cards"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		heal = 5 * (2 ** self.countHealDouble())
		targets = [self.Game.heroes[self.ID], self.Game.heroes[3-self.ID]] + self.Game.minionsonBoard(self.ID) + self.Game.minionsonBoard(3-self.ID)
		self.restoresAOE(targets, [heal for obj in targets])
		for i in range(5): self.Game.Hand_Deck.drawCard(self.ID)
		return None
		
"""Hunter cards"""
class UnsealtheVault(Quest):
	Class, name = "Hunter", "Unseal the Vault"
	requireTarget, mana = False, 1
	index = "Uldum~Hunter~Spell~1~Unseal the Vault~~Quest~Legendary"
	description = "Quest: Summon 20 minions. Reward: Ramkahen Roar"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_UnsealtheVault(self)]
		
class Trig_UnsealtheVault(QuestTrigger):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionBeenSummoned"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject.ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.counter += 1
		if self.counter > 19:
			self.disconnect()
			try: self.entity.Game.Secrets.mainQuests[self.entity.ID].remove(self.entity)
			except: pass
			PharaohsWarmask(self.entity.Game, self.entity.ID).replaceHeroPower()
			
class PharaohsWarmask(HeroPower):
	mana, name, requireTarget = 2, "Pharaoh's Warmask", False
	index = "Hunter~Hero Power~2~Pharaoh's Warmask"
	description = "Give your minions +2 Attack"
	def effect(self, target=None, choice=0):
		for minion in self.Game.minionsonBoard(self.ID):
			minion.buffDebuff(2, 0)
		return 0
		
		
class PressurePlate(Secret):
	Class, name = "Hunter", "Pressure Plate"
	requireTarget, mana = False, 2
	index = "Uldum~Hunter~Spell~2~Pressure Plate~~Secret"
	description = "Secret: After your opponent casts a spell, destroy a random enemy minion"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_PressurePlate(self)]
		
class Trig_PressurePlate(SecretTrigger):
	def __init__(self, entity):
		self.blank_init(entity, ["SpellBeenPlayed"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.ID != self.entity.Game.turn and subject.ID != self.entity.ID and self.entity.Game.minionsAlive(3-self.entity.ID)
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		curGame = self.entity.Game
		if curGame.mode == 0:
			if curGame.guides:
				i = curGame.guides.pop(0)
			else:
				minions = curGame.minionsAlive(3-self.entity.ID)
				i = npchoice(minions).pos if minions else -1
				curGame.fixedGuides.append(i)
			if i > -1: curGame.killMinion(self.entity, curGame.minions[3-self.entity.ID][i])
			
			
class DesertSpear(Weapon):
	Class, name, description = "Hunter", "Desert Spear", "After your hero Attacks, summon a 1/1 Locust with Rush"
	mana, attack, durability = 3, 1, 3
	index = "Uldum~Hunter~Weapon~3~1~3~Desert Spear"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_DesertSpear(self)]
		
class Trig_DesertSpear(TrigBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["HeroAttackedMinion", "HeroAttackedHero"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		#The target can't be dying to trigger this
		return subject == self.entity.Game.heroes[self.entity.ID] and self.entity.onBoard
		
	def text(self, CHN):
		return "在你的英雄攻击后，召唤一个1/1并具有突袭的蝗虫" if CHN \
				else "After your hero Attacks, summon a 1/1 Locust with Rush"
				
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.Game.summon(Locust(self.entity.Game, self.entity.ID), -1, self.entity.ID)
		
		
class HuntersPack(Spell):
	Class, name = "Hunter", "Hunter's Pack"
	requireTarget, mana = False, 3
	index = "Uldum~Hunter~Spell~3~Hunter's Pack"
	description = "Add a random Hunter Beast, Secret, and Weapon to your hand"
	poolIdentifier = "Hunter Beasts"
	@classmethod
	def generatePool(cls, Game):
		beasts, secrets, weapons = [], [], []
		for key, value in Game.ClassCards["Hunter"].items():
			if "~Beast~" in key: beasts.append(value)
			elif value.description.startswith("Secret:"): secrets.append(value)
			elif "~Weapon~" in key: weapons.append(value)
		return ["Hunter Beasts", "Hunter Secrets", "Hunter Weapons"], [beasts, secrets, weapons]
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if curGame.mode == 0:
			if curGame.guides:
				cards = list(curGame.guides.pop(0))
			else:
				cards = (npchoice(self.rngPool("Hunter Beasts")), npchoice(self.rngPool("Hunter Secrets")), npchoice(self.rngPool("Hunter Weapons")))
				curGame.fixedGuides.append(cards)
			curGame.Hand_Deck.addCardtoHand(cards, self.ID, "type")
		return None
		
		
class HyenaAlpha(Minion):
	Class, race, name = "Hunter", "Beast", "Hyena Alpha"
	mana, attack, health = 4, 3, 3
	index = "Uldum~Hunter~Minion~4~3~3~Beast~Hyena Alpha~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: If you control a Secret, summon two 2/2 Hyenas"
	
	def effCanTrig(self):
		self.effectViable = self.Game.Secrets.secrets[self.ID] != []
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if self.Game.Secrets.secrets[self.ID] != []:
			pos = (self.pos, "leftandRight") if self.onBoard else (-1, "totheRightEnd")
			self.Game.summon([Hyena_Uldum(self.Game, self.ID) for i in range(2)], pos, self.ID)
		return None
		
class Hyena_Uldum(Minion):
	Class, race, name = "Hunter", "Beast", "Hyena"
	mana, attack, health = 2, 2, 2
	index = "Uldum~Hunter~Minion~2~2~2~Beast~Hyena~Uncollectible"
	requireTarget, keyWord, description = False, "", ""
	
	
class RamkahenWildtamer(Minion):
	Class, race, name = "Hunter", "", "Ramkahen Wildtamer"
	mana, attack, health = 3, 4, 3
	index = "Uldum~Hunter~Minion~3~4~3~None~Ramkahen Wildtamer~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Copy a random Beast in your hand"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if curGame.mode == 0:
			if curGame.guides:
				i = curGame.guides.pop(0)
			else:
				beasts = [i for i, card in enumerate(curGame.Hand_Deck.hands[self.ID]) if card.type == "Minion" and "Beast" in card.race]
				i = npchoice(beasts) if beasts else -1
				curGame.fixedGuides.append(i)
			if i > -1:
				beast = curGame.Hand_Deck.hands[self.ID][i].selfCopy(self.ID)
				curGame.Hand_Deck.addCardtoHand(beast, self.ID)
		return None
		
		
class SwarmofLocusts(Spell):
	Class, name = "Hunter", "Swarm of Locusts"
	requireTarget, mana = False, 6
	index = "Uldum~Hunter~Spell~6~Swarm of Locusts"
	description = "Summon seven 1/1 Locusts with Rush"
	def available(self):
		return self.Game.space(self.ID) > 0
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.Game.summon([Locust(self.Game, self.ID) for i in range(7)], (-1, "totheRightEnd"), self.ID)
		return None
		
		
class ScarletWebweaver(Minion):
	Class, race, name = "Hunter", "Beast", "Scarlet Webweaver"
	mana, attack, health = 6, 5, 5
	index = "Uldum~Hunter~Minion~6~5~5~Beast~Scarlet Webweaver~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Reduce the Cost of a random Beast in your hand by (5)"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if curGame.mode == 0:
			if curGame.guides:
				i = curGame.guides.pop(0)
			else:
				beasts = [i for i, card in enumerate(curGame.Hand_Deck.hands[self.ID]) if card.type == "Minion" and "Beast" in card.race]
				i = npchoice(beasts) if beasts else -1
				curGame.fixedGuides.append(i)
			if i > -1:
				beast = curGame.Hand_Deck.hands[self.ID][i]
				ManaMod(beast, changeby=-5, changeto=-1).applies()
				curGame.Manas.calcMana_Single(beast)
		return None
		
		
class WildBloodstinger(Minion):
	Class, race, name = "Hunter", "Beast", "Wild Bloodstinger"
	mana, attack, health = 6, 6, 9
	index = "Uldum~Hunter~Minion~6~6~9~Beast~Wild Bloodstinger~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Summon a minion from your opponent's hand. Attack it"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if curGame.mode == 0:
			if curGame.guides:
				i = curGame.guides.pop(0)
			else:
				minions = [i for i, card in enumerate(curGame.Hand_Deck.hands[3-self.ID]) if card.type == "Minion"]
				i = npchoice(minions) if minions and curGame.space(3-self.ID) > 0 else -1
				curGame.fixedGuides.append(i)
			if i > -1:
				minion = curGame.summonfromHand(i, 3-self.ID, -1, self.ID)
				if minion.onBoard: curGame.battle(self, minion, verifySelectable=False, useAttChance=False, resolveDeath=False)
		return None
		
		
class DinotamerBrann(Minion):
	Class, race, name = "Hunter", "", "Dinotamer Brann"
	mana, attack, health = 7, 2, 4
	index = "Uldum~Hunter~Minion~7~2~4~None~Dinotamer Brann~Battlecry~Legendary"
	requireTarget, keyWord, description = False, "", "Battlecry: If your deck has no duplicates, summon King Krush"
	
	def effCanTrig(self):
		self.effectViable = self.Game.Hand_Deck.noDuplicatesinDeck(self.ID)
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if self.Game.Hand_Deck.noDuplicatesinDeck(self.ID):
			self.Game.summon(KingKrush_Uldum(self.Game, self.ID), self.pos+1, self.ID)
		return None
		
class KingKrush_Uldum(Minion):
	Class, race, name = "Hunter", "Beast", "King Krush"
	mana, attack, health = 9, 8, 8
	index = "Uldum~Hunter~Minion~9~8~8~Beast~King Krush~Charge~Legendary~Uncollectible"
	requireTarget, keyWord, description = False, "Charge", "Charge"
	
	
"""Mage cards"""
class RaidtheSkyTemple(Quest):
	Class, name = "Mage", "Raid the Sky Temple"
	requireTarget, mana = False, 1
	index = "Uldum~Mage~Spell~1~Raid the Sky Temple~~Quest~Legendary"
	description = "Quest: Cast 10 spell. Reward: Ascendant Scroll"
	poolIdentifier = "Mage Spells"
	@classmethod
	def generatePool(cls, Game):
		return "Mage Spells", [value for key, value in Game.ClassCards["Mage"].items() if "~Spell~" in key]
		
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_RaidtheSkyTemple(self)]
		
class Trig_RaidtheSkyTemple(QuestTrigger):
	def __init__(self, entity):
		self.blank_init(entity, ["SpellPlayed"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject.ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.counter += 1
		if self.counter > 9:
			self.disconnect()
			try: self.entity.Game.Secrets.mainQuests[self.entity.ID].remove(self.entity)
			except: pass
			AscendantScroll(self.entity.Game, self.entity.ID).replaceHeroPower()
			
class AscendantScroll(HeroPower):
	mana, name, requireTarget = 2, "Ascendant Scroll", False
	index = "Mage~Hero Power~2~Ascendant Scroll"
	description = "Add a random Mage spell to your hand. It costs (2) less"
	def effect(self, target=None, choice=0):
		curGame = self.Game
		if curGame.mode == 0:
			if curGame.guides:
				spell = curGame.guides.pop(0)
			else:
				spell = npchoice(self.rngPool("Mage Spells"))
				curGame.fixedGuides.append(spell)
			spell = spell(curGame, self.ID)
			ManaMod(spell, changeby=-2, changeto=-1).applies()
			curGame.Hand_Deck.addCardtoHand(spell, self.ID)
		return 0
		
		
class AncientMysteries(Spell):
	Class, name = "Mage", "Ancient Mysteries"
	requireTarget, mana = False, 2
	index = "Uldum~Mage~Spell~2~Ancient Mysteries"
	description = "Draw a Secret from your deck. It costs (0)"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		ownDeck = curGame.Hand_Deck.decks[self.ID]
		if curGame.mode == 0:
			if curGame.guides:
				i = curGame.guides.pop(0)
			else:
				secrets = [i for i, card in enumerate(ownDeck) if card.description.startswith("Secret:")]
				i = npchoice(secrets) if secrets else -1
				curGame.fixedGuides.append(i)
			if i > -1:
				secret = curGame.Hand_Deck.drawCard(self.ID, i)[0]
				if secret: ManaMod(secret, changeby=0, changeto=0).applies()
		return None
		
		
class FlameWard(Secret):
	Class, name = "Mage", "Flame Ward"
	requireTarget, mana = False, 3
	index = "Uldum~Mage~Spell~3~Flame Ward~~Secret"
	description = "Secret: After a minion attacks your hero, deal 3 damage to all enemy minions"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_FlameWard(self)]
		
class Trig_FlameWard(SecretTrigger):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionAttackedHero"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.ID != self.entity.Game.turn and target == self.entity.Game.heroes[self.entity.ID]
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		damage = (3 + self.entity.countSpellDamage()) * (2 ** self.entity.countDamageDouble())
		targets = self.entity.Game.minionsonBoard(3-self.entity.ID)
		self.entity.dealsAOE(targets, [damage for minion in targets])
		
		
class CloudPrince(Minion):
	Class, race, name = "Mage", "Elemental", "Cloud Prince"
	mana, attack, health = 5, 4, 4
	index = "Uldum~Mage~Minion~5~4~4~Elemental~Cloud Prince~Battlecry"
	requireTarget, keyWord, description = True, "", "Battlecry: If you control a Secret, deal 6 damage"
	
	def returnTrue(self, choice=0):
		return self.Game.Secrets.secrets[self.ID] != []
		
	def effCanTrig(self):
		self.effectViable = self.Game.Secrets.secrets[self.ID] != []
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target and self.Game.Secrets.secrets[self.ID] != []:
			self.dealsDamage(target, 6)
		return target
		
	
class ArcaneFlakmage(Minion):
	Class, race, name = "Mage", "", "Arcane Flakmage"
	mana, attack, health = 2, 3, 2
	index = "Uldum~Mage~Minion~2~3~2~None~Arcane Flakmage"
	requireTarget, keyWord, description = False, "", "After you play a Secret, deal 2 damage to all enemy minions"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_ArcaneFlakmage(self)]
		
class Trig_ArcaneFlakmage(TrigBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["SpellBeenPlayed"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject.ID == self.entity.ID and subject.description.startswith("Secret:")
		
	def text(self, CHN):
		return "在你使用一张奥秘牌后，对所有敌方随从造成2点伤害" if CHN else "After you play a Secret, deal 2 damage to all enemy minions"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		targets = self.entity.Game.minionsonBoard(3-self.entity.ID)
		self.entity.dealsAOE(targets, [2 for minion in targets])
		
		
class DuneSculptor(Minion):
	Class, race, name = "Mage", "", "Dune Sculptor"
	mana, attack, health = 3, 3, 3
	index = "Uldum~Mage~Minion~3~3~3~None~Dune Sculptor"
	requireTarget, keyWord, description = False, "", "After you cast a spell, add a random Mage minion to your hand"
	poolIdentifier = "Mage Minions"
	@classmethod
	def generatePool(cls, Game):
		return "Mage Minions", [value for key, value in Game.ClassCards["Mage"].items() if "~Minion~" in key]
		
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_DuneSculptor(self)]
		
class Trig_DuneSculptor(TrigBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["SpellPlayed"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject.ID == self.entity.ID
		
	def text(self, CHN):
		return "在你施放一个法术后，随机将一张法师随从牌置入你的手牌" if CHN \
				else "After you cast a spell, add a random Mage minion to your hand"
				
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		curGame = self.entity.Game
		if curGame.mode == 0:
			if curGame.guides:
				minion = curGame.guides.pop(0)
			else:
				minion = npchoice(self.rngPool("Mage Minions"))
				curGame.fixedGuides.append(minion)
			curGame.Hand_Deck.addCardtoHand(minion, self.entity.ID, "type")
			
			
class NagaSandWitch(Minion):
	Class, race, name = "Mage", "", "Naga Sand Witch"
	mana, attack, health = 5, 5, 5
	index = "Uldum~Mage~Minion~5~5~5~None~Naga Sand Witch~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Change the Cost of spells in your hand to (5)"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		for spell in [card for card in self.Game.Hand_Deck.hands[self.ID] if card.type == "Spell"]:
			ManaMod(spell, changeby=0, changeto=5).applies()
		self.Game.Manas.calcMana_All()
		return None
		
		
class TortollanPilgrim(Minion):
	Class, race, name = "Mage", "", "Tortollan Pilgrim"
	mana, attack, health = 8, 5, 5
	index = "Uldum~Mage~Minion~8~5~5~None~Tortollan Pilgrim~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Discover a spell in your deck and cast it with random targets"
	def castSpellfromDeck(self, spellType, ownDeck):
		for i, card in enumerate(ownDeck):
			if isinstance(card, spellType):
				index = i
				break
		self.Game.Hand_Deck.extractfromHand(index, ID=0, all=False, enemyCanSee=True)[0].cast()
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame, ID = self.Game, self.ID
		ownDeck = curGame.Hand_Deck.decks[ID]
		if ID == curGame.turn:
			if curGame.mode == 0:
				if curGame.guides:
					i = curGame.guides.pop(0)
					if i > -1:
						curGame.Hand_Deck.extractfromHand(i, ID=ID, all=False, enemyCanSee=True)[0].cast()
				else:
					types, p = discoverProb([type(card) for card in ownDeck if card.type == "Spell"])
					if types:
						if "byOthers" in comment:
							spellType = npchoice(types, p=p)
							index = types.index(spellType)
							curGame.fixedGuides.append(index)
							curGame.Hand_Deck.extractfromHand(index, ID=ID, all=False, enemyCanSee=True)[0].cast()
						else:
							types = npchoice(types, min(3, len(types)), p=p, replace=False)
							curGame.options = [spellType(curGame, ID) for spellType in types]
							curGame.Discover.startDiscover(self)
					else: curGame.fixedGuides.append(None)
		return None
		
	def discoverDecided(self, option, info):
		spellType = type(option)
		for i, card in enumerate(self.Game.Hand_Deck.decks[self.ID]):
			if isinstance(card, spellType):
				index = i
		self.Game.fixedGuides.append(index)
		self.Game.Hand_Deck.extractfromHand(index, ID=self.ID, all=False, enemyCanSee=True)[0].cast()
		
		
class RenotheRelicologist(Minion):
	Class, race, name = "Mage", "", "Reno the Relicologist"
	mana, attack, health = 6, 4, 6
	index = "Uldum~Mage~Minion~6~4~6~None~Reno the Relicologist~Battlecry~Legendary"
	requireTarget, keyWord, description = False, "", "Battlecry: If your deck has no duplicates, deal 10 damage randomly split among all enemy minions"
	
	def effCanTrig(self):
		self.effectViable = self.Game.Hand_Deck.noDuplicatesinDeck(self.ID)
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if curGame.Hand_Deck.noDuplicatesinDeck(self.ID):
			if curGame.mode == 0:
				for num in range(10):
					if curGame.guides:
						i = curGame.guides.pop(0)
					else:
						minions = curGame.minionsAlive(3-self.ID)
						i = npchoice(minions).pos if minions else -1
						curGame.fixedGuides.append(i)
					if i > -1: self.dealsDamage(curGame.minions[3-self.ID][i], 1)
		return None
		
		
class PuzzleBoxofYoggSaron(Spell):
	Class, name = "Mage", "Puzzle Box of Yogg-Saron"
	requireTarget, mana = False, 10
	index = "Uldum~Mage~Spell~10~Puzzle Box of Yogg-Saron"
	description = "Cast 10 random spells (targets chosen randomly)"
	poolIdentifier = "Spells"
	@classmethod
	def generatePool(cls, Game):
		spells = []
		for Class in Game.Classes:
			spells += [value for key, value in Game.ClassCards[Class].items() if "~Spell~" in key]
		return "Spells", spells
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if curGame.mode == 0:
			curGame.sendSignal("SpellBeenCast", self.ID, self, None, 0, "", choice)
			for i in range(10):
				if curGame.guides:
					spell = curGame.guides.pop(0)
				else:
					spell = npchoice(self.rngPool("Spells"))
					curGame.fixedGuides.append(spell)
				spell(curGame, self.ID).cast()
				curGame.gathertheDead(decideWinner=True)
		return None
		
		
"""Paladin cards"""
class MakingMummies(Quest):
	Class, name = "Paladin", "Making Mummies"
	requireTarget, mana = False, 1
	index = "Uldum~Paladin~Spell~1~Making Mummies~~Quest~Legendary"
	description = "Quest: Play 5 Reborn minions. Reward: Emperor Wraps"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_MakingMummies(self)]
		
class Trig_MakingMummies(QuestTrigger):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionBeenPlayed"]) #扳机是使用后扳机
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		#假设扳机的判定条件是打出的随从在检测时有复生就可以，如果在打出过程中获得复生，则依然算作任务进度
		return subject.ID == self.entity.ID and subject.keyWords["Reborn"] > 0
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.counter += 1
		if self.counter > 4:
			self.disconnect()
			try: self.entity.Game.Secrets.mainQuests[self.entity.ID].remove(self.entity)
			except: pass
			EmperorWraps(self.entity.Game, self.entity.ID).replaceHeroPower()
			
class EmperorWraps(HeroPower):
	mana, name, requireTarget = 2, "Emperor Wraps", True
	index = "Paladin~Hero Power~2~Emperor Wraps"
	description = "Summon a 2/2 copy of a friendly minion"
	def available(self, choice=0):
		if self.heroPowerTimes >= self.heroPowerChances_base + self.heroPowerChances_extra:
			return False
		if self.Game.space(self.ID) < 1 or self.selectableFriendlyMinionExists() == False:
			return False
		return True
		
	def effect(self, target=None, choice=0):
		if target:
			self.Game.summon(target.selfCopy(self.ID, 2, 2), -1, self.ID, "")
		return 0
		
		
class BrazenZealot(Minion):
	Class, race, name = "Paladin", "", "Brazen Zealot"
	mana, attack, health = 1, 2, 1
	index = "Uldum~Paladin~Minion~1~2~1~None~Brazen Zealot"
	requireTarget, keyWord, description = False, "", "Whenever you summon a minion, gain +1 Attack"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_BrazenZealot(self)]
		
class Trig_BrazenZealot(TrigBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionSummoned"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject.ID == self.entity.ID and subject != self.entity
		
	def text(self, CHN):
		return "每当你召唤一个随从，获得+1攻击力" if CHN else "Whenever you summon a minion, gain +1 Attack"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.buffDebuff(1, 0)
		
		
class MicroMummy(Minion):
	Class, race, name = "Paladin", "Mech", "Micro Mummy"
	mana, attack, health = 2, 1, 2
	index = "Uldum~Paladin~Minion~2~1~2~Mech~Micro Mummy~Reborn"
	requireTarget, keyWord, description = False, "Reborn", "Reborn. At the end of your turn, give another random friendly minion +1 Attack"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_MicroMummy(self)]
		
class Trig_MicroMummy(TrigBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["TurnEnds"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and ID == self.entity.ID
		
	def text(self, CHN):
		return "在你的回合结束时，随从使一个友方随从获得+1攻击力" if CHN else "At the end of your turn, give another random friendly minion +1 Attack"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		curGame = self.entity.Game
		if curGame.mode == 0:
			if curGame.guides:
				i = curGame.guides.pop(0)
			else:
				minions = curGame.minionsonBoard(self.entity.ID, self.entity)
				i = npchoice(minions).pos if minions else -1
				curGame.fixedGuides.append(i)
			if i > -1: curGame.minions[self.entity.ID][i].buffDebuff(1, 0)
			
			
class SandwaspQueen(Minion):
	Class, race, name = "Paladin", "Beast", "Sandwasp Queen"
	mana, attack, health = 2, 3, 1
	index = "Uldum~Paladin~Minion~2~3~1~Beast~Sandwasp Queen~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Add two 2/1 Sandwasps to your hand"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.Game.Hand_Deck.addCardtoHand([Sandwasp, Sandwasp], self.ID, "type")
		return None
		
class Sandwasp(Minion):
	Class, race, name = "Paladin", "Beast", "Sandwasp"
	mana, attack, health = 1, 2, 1
	index = "Uldum~Paladin~Minion~1~2~1~Beast~Sandwasp~Uncollectible"
	requireTarget, keyWord, description = False, "", ""
	
	
class SirFinleyoftheSands(Minion):
	Class, race, name = "Paladin", "Murloc", "Sir Finley of the Sands"
	mana, attack, health = 2, 2, 3
	index = "Uldum~Paladin~Minion~2~2~3~Murloc~Sir Finley of the Sands~Battlecry~Legendary"
	requireTarget, keyWord, description = False, "", "Battlecry: If your deck has no duplicates, Discover an upgraded Hero Power"
	poolIdentifier = "Upgraded Powers"
	@classmethod
	def generatePool(cls, Game):
		return "Upgraded Powers", Game.upgradedPowers
		
	def effCanTrig(self):
		self.effectViable = self.Game.Hand_Deck.noDuplicatesinDeck(self.ID)
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if curGame.Hand_Deck.noDuplicatesinDeck(self.ID) and self.ID == curGame.turn:
			if curGame.mode == 0:
				if curGame.guides:
					curGame.guides.pop(0)(curGame, self.ID).replaceHeroPower()
				else:
					heroPowerPool = curGame.upgradedPowers[:]
					try: heroPowerPool.remove(type(curGame.powers[self.ID]))
					except: pass
					if "byOthers" in comment:
						power = npchoice(heroPowerPool)
						curGame.fixedGuides.append(power)
						power(curGame, self.ID).replaceHeroPower()
					else:
						newpowers = npchoice(heroPowerPool, 3, replace=False)
						curGame.options = [power(curGame, self.ID) for power in newpowers]
						curGame.Discover.startDiscover(self)
		return None
		
	def discoverDecided(self, option, info):
		self.Game.fixedGuides.append(type(option))
		option.replaceHeroPower()
		
		
class Subdue(Spell):
	Class, name = "Paladin", "Subdue"
	requireTarget, mana = True, 2
	index = "Uldum~Paladin~Spell~2~Subdue"
	description = "Change a minion's Attack and Health to 1"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			target.statReset(1, 1)
		return target
		
		
class SalhetsPride(Minion):
	Class, race, name = "Paladin", "Beast", "Salhet's Pride"
	mana, attack, health = 3, 3, 1
	index = "Uldum~Paladin~Minion~3~3~1~Beast~Salhet's Pride~Deathrattle"
	requireTarget, keyWord, description = False, "", "Deathrattle: Draw two 1-Health minions from your deck"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [DrawTwo1HealthMinions(self)]
		
class DrawTwo1HealthMinions(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		curGame = self.entity.Game
		if curGame.mode == 0:
			for num in range(2):
				if curGame.guides:
					i = curGame.guides.pop(0)
				else:
					minions = [i for i, card in enumerate(curGame.Hand_Deck.decks[self.entity.ID]) if card.type == "Minion" and card.health == 1]
					i = npchoice(minions) if minions else -1
					curGame.fixedGuides.append(i)
				if i > -1: curGame.Hand_Deck.drawCard(self.entity.ID, i)
				else: break
				
	def text(self, CHN):
		return "亡语：从你的牌库中抽两张生命值为1的随从牌" if CHN else "Deathrattle: Draw two 1-Health minions from your deck"
		
				
class AncestralGuardian(Minion):
	Class, race, name = "Paladin", "", "Ancestral Guardian"
	mana, attack, health = 4, 4, 2
	index = "Uldum~Paladin~Minion~4~4~2~None~Ancestral Guardian~Lifesteal~Reborn"
	requireTarget, keyWord, description = False, "Lifesteal,Reborn", "Lifesteal, Reborn"
	
	
class PharaohsBlessing(Spell):
	Class, name = "Paladin", "Pharaoh's Blessing"
	requireTarget, mana = True, 6
	index = "Uldum~Paladin~Spell~6~Pharaoh's Blessing"
	description = "Give a minion +4/+4, Divine Shield, and Taunt"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			target.buffDebuff(4, 4)
			target.getsKeyword("Divine Shield")
			target.getsKeyword("Taunt")
		return target
		
		
class TiptheScales(Spell):
	Class, name = "Paladin", "Tip the Scales"
	requireTarget, mana = False, 8
	index = "Uldum~Paladin~Spell~8~Tip the Scales"
	description = "Summon 7 Murlocs from your deck"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		ownDeck = curGame.Hand_Deck.decks[self.ID]
		if curGame.mode == 0:
			for num in range(7):
				if curGame.guides:
					i = curGame.guides.pop(0)
				else:
					murlocs = [i for i, card in enumerate(ownDeck) if card.type == "Minion" and "Murloc" in card.race]
					i = npchoice(murlocs) if murlocs and curGame.space(self.ID) > 0 else -1
					curGame.fixedGuides.append(i)
				if i > -1: curGame.summonfromDeck(i, self.ID, -1, self.ID)
				else: break
		return None
		
		
"""Priest cards"""
class ActivatetheObelisk(Quest):
	Class, name = "Priest", "Activate the Obelisk"
	requireTarget, mana = False, 1
	index = "Uldum~Priest~Spell~1~Activate the Obelisk~~Quest~Legendary"
	description = "Quest: Restore 15 Health. Reward: Obelisk's Eye"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_ActivatetheObelisk(self)]
		
class Trig_ActivatetheObelisk(QuestTrigger):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionGetsHealed", "HeroGetsHealed"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject.ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.counter += number
		if self.counter > 14:
			self.disconnect()
			try: self.entity.Game.Secrets.mainQuests[self.entity.ID].remove(self.entity)
			except: pass
			ObelisksEye(self.entity.Game, self.entity.ID).replaceHeroPower()
			
class ObelisksEye(HeroPower):
	mana, name, requireTarget = 2, "Obelisk's Eye", True
	index = "Priest~Hero Power~2~Obelisk's Eye"
	description = "Restore 3 Health. If you target a minion, also give it +3/+3"
	def text(self, CHN):
		heal = 3 * (2 ** self.countHealDouble())
		return "恢复%d点生命值。如果你的目标是一个随从，则同时使其获得+3/+3"%heal if CHN \
				else "Restore %d Health. If you target a minion, also give it +3/+3"%heal
				
	def effect(self, target, choice=0):
		heal = 3 * (2 ** self.countHealDouble())
		self.restoresHealth(target, heal)
		if target.type == "Minion":
			target.buffDebuff(3, 3)
		if target.health < 1 or target.dead:
			return 1
		return 0
		
		
class EmbalmingRitual(Spell):
	Class, name = "Priest", "Embalming Ritual"
	requireTarget, mana = True, 1
	index = "Uldum~Priest~Spell~1~Embalming Ritual"
	description = "Give a minion Reborn"
	def targetExists(self, choice=0):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			target.getsKeyword("Reborn")
		return target
		
		
class Penance(Spell):
	Class, name = "Priest", "Penance"
	requireTarget, mana = True, 2
	index = "Uldum~Priest~Spell~2~Penance"
	description = "Lifesteal. Deal 3 damage to a minion"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.keyWords["Lifesteal"] = 1
		
	def targetExists(self, choice=0):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			damage = (3 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			self.dealsDamage(target, damage)
		return target
		
		
class SandhoofWaterbearer(Minion):
	Class, race, name = "Priest", "", "Sandhoof Waterbearer"
	mana, attack, health = 5, 5, 5
	index = "Uldum~Priest~Minion~5~5~5~None~Sandhoof Waterbearer"
	requireTarget, keyWord, description = False, "", "At the end of your turn, restore 5 Health to a damaged friendly character"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_SandhoofWaterbearer(self)]
		
class Trig_SandhoofWaterbearer(TrigBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["TurnEnds"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and ID == self.entity.ID
		
	def text(self, CHN):
		heal = 5 * (2 ** self.entity.countHealDouble())
		return "在你的回合结束时， 为一个受伤的友方角色恢复%d点生命值"%heal if CHN \
				else "At the end of your turn, restore %d Health to a damaged friendly character"%heal
				
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		curGame = self.entity.Game
		if curGame.mode == 0:
			char = None
			if curGame.guides:
				i, where = curGame.guides.pop(0)
				if where: char = curGame.find(i, where)
			else:
				chars = [char for char in curGame.charsAlive(self.entity.ID) if char.health < char.health_max]
				if chars:
					char = npchoice(chars)
					curGame.fixedGuides.append((char.pos, char.type+str(char.ID)))
				else:
					curGame.fixedGuides.append((0, ''))
			if char: self.entity.restoresHealth(char, 5 * (2 ** self.entity.countHealDouble()))
			
			
class Grandmummy(Minion):
	Class, race, name = "Priest", "", "Grandmummy"
	mana, attack, health = 2, 1, 2
	index = "Uldum~Priest~Minion~2~1~2~None~Grandmummy~Reborn~Deathrattle"
	requireTarget, keyWord, description = False, "Reborn", "Reborn. Deathrattle: Give a random friendly minion +1/+1"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [GiveRandomFriendlyMinionPlus1Plus1(self)]
		
class GiveRandomFriendlyMinionPlus1Plus1(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		curGame = self.entity.Game
		if curGame.mode == 0:
			if curGame.guides:
				i = curGame.guides.pop(0)
			else:
				minions = curGame.minionsonBoard(self.entity.ID)
				i = npchoice(minions).pos if minions else -1
				curGame.fixedGuides.append(i)
			if i > -1: curGame.minions[self.entity.ID][i].buffDebuff(1, 1)
			
	def text(self, CHN):
		return "亡语：随机使一个友方随从获得+1/+1" if CHN else "Deathrattle: Give a random friendly minion +1/+1"
		
		
class HolyRipple(Spell):
	Class, name = "Priest", "Holy Ripple"
	requireTarget, mana = False, 2
	index = "Uldum~Priest~Spell~2~Holy Ripple"
	description = "Deal 1 damage to all enemies. Restore 1 Health to all friendly characters"
	def text(self, CHN):
		damage = (1 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		heal = 1 * (2 ** self.countHealDouble())
		return "对所有敌人造成%d点伤害，为所有友方角色恢复%d点生命值"%(damage, heal) if CHN \
				else "Deal %d damage to all enemies. Restore %d Health to all friendly characters"%(damage, heal)
				
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		damage = (1 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		heal = 1 * (2 ** self.countHealDouble())
		enemies = [self.Game.heroes[3-self.ID]] + self.Game.minionsonBoard(3-self.ID)
		friendlies = [self.Game.heroes[self.ID]] + self.Game.minionsonBoard(self.ID)
		self.dealsAOE(enemies, [damage for obj in enemies])
		self.restoresAOE(friendlies, [heal for obj in friendlies])
		return None
		
		
class WretchedReclaimer(Minion):
	Class, race, name = "Priest", "", "Wretched Reclaimer"
	mana, attack, health = 3, 3, 3
	index = "Uldum~Priest~Minion~3~3~3~None~Wretched Reclaimer~Battlecry"
	requireTarget, keyWord, description = True, "", "Battlecry: Destroy a friendly minion, then return it to life with full Health"
	
	def targetExists(self, choice=0):
		return self.selectableFriendlyMinionExists(choice)
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target != self and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			minion = type(target)(self.Game, target.ID)
			targetID, position = target.ID, target.pos
			self.Game.killMinion(self, target)
			self.Game.gathertheDead() #强制死亡需要在此插入死亡结算，并让随从离场
			#如果目标之前是第4个(position=3)，则场上最后只要有3个随从或者以下，就会召唤到最右边。
			#如果目标不在场上或者是第二次生效时已经死亡等被初始化，则position=-2会让新召唤的随从在场上最右边。
			pos = position if position >= 0 else -1
			self.Game.summon(minion, pos, self.ID)
		return target
		
		
class Psychopomp(Minion):
	Class, race, name = "Priest", "", "Psychopomp"
	mana, attack, health = 4, 3, 1
	index = "Uldum~Priest~Minion~4~3~1~None~Psychopomp~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Summon a random friendly minion that died this game. Give it Reborn"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if curGame.mode == 0:
			if curGame.guides:
				minion = curGame.guides.pop(0)
			else:
				minionsDied = curGame.Counters.minionsDiedThisGame[self.ID]
				minion = curGame.cardPool[npchoice(minionsDied)] if minionsDied else None
				curGame.fixedGuides.append(minion)
			if minion:
				minion = minion(curGame, self.ID)
				minion.getsKeyword("Reborn") #不知道卡德加翻倍召唤出的随从是否也会获得复生，假设会。
				curGame.summon(minion, self.pos+1, self.ID)
		return None
		
		
class HighPriestAmet(Minion):
	Class, race, name = "Priest", "", "High Priest Amet"
	mana, attack, health = 4, 2, 7
	index = "Uldum~Priest~Minion~4~2~7~None~High Priest Amet~Legendary"
	requireTarget, keyWord, description = False, "", "Whenever you summon a minion, set its Health equal to this minion's"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_HighPriestAmet(self)]
		
class Trig_HighPriestAmet(TrigBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionSummoned"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject.ID == self.entity.ID and subject != self.entity and self.entity.health > 0
		
	def text(self, CHN):
		return "每当你召唤一个随从，将其生命设置为与本随从相同" if CHN else "Whenever you summon a minion, set its Health equal to this minion's"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		subject.statReset(False, self.entity.health)
		
		
class PlagueofDeath(Spell):
	Class, name = "Priest", "Plague of Death"
	requireTarget, mana = False, 9
	index = "Uldum~Priest~Spell~9~Plague of Death"
	description = "Silence and destroy all minions"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		minions = self.Game.minionsonBoard(1) + self.Game.minionsonBoard(2)
		for minion in minions:
			minion.getsSilenced()
		self.Game.killMinion(self, minions)
		return None
		
		
"""Rogue cards"""
class BazaarBurglary(Quest):
	Class, name = "Rogue", "Bazaar Burglary"
	requireTarget, mana = False, 1
	index = "Uldum~Rogue~Spell~1~Bazaar Burglary~~Quest~Legendary"
	description = "Quest: Add 4 cards from other classes to your hand. Reward: Ancient Blades"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_BazaarBurglary(self)]
		
class Trig_BazaarBurglary(QuestTrigger):
	def __init__(self, entity):
		#置入手牌扳机。抽到不同职业牌，回响牌，抽到时施放的法术都可以触发扳机。
		self.blank_init(entity, ["CardEntersHand", "SpellCastWhenDrawn"]) #抽到时施放的法术没有被处理成置入手牌
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return target[0].ID == self.entity.ID and target[0].Class != "Neutral" and self.entity.Game.heroes[self.entity.ID].Class not in target[0].Class
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.counter += 1
		if self.counter > 3:
			self.disconnect()
			try: self.entity.Game.Secrets.mainQuests[self.entity.ID].remove(self.entity)
			except: pass
			AncientBlades(self.entity.Game, self.entity.ID).replaceHeroPower()
				
class AncientBlades(HeroPower):
	mana, name, requireTarget = 2, "Ancient Blades", False
	index = "Rogue~Hero Power~2~Ancient Blades"
	description = "Equip a 3/2 Blade with Immune while attacking"
	def effect(self, target=None, choice=0):
		self.Game.equipWeapon(MirageBlade(self.Game, self.ID))
		return 0
	
class MirageBlade(Weapon):
	Class, name, description = "Rogue", "Mirage Blade", "Your hero is Immune while attacking"
	mana, attack, durability = 2, 3, 2
	index = "Uldum~Rogue~Weapon~2~3~2~Mirage Blade~Uncollectible"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_MirageBlade(self)]
		
class Trig_MirageBlade(TrigBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["BattleStarted", "BattleFinished"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject == self.entity.Game.heroes[self.entity.ID] and self.entity.onBoard
		
	def text(self, CHN):
		return "你的英雄在攻击时具有免疫" if CHN else "Your hero is Immune while attacking"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		if signal == "BattleStarted":
			self.entity.Game.status[self.entity.ID]["Immune"] += 1
		else:
			self.entity.Game.status[self.entity.ID]["Immune"] -= 1
			
			
class PharaohCat(Minion):
	Class, race, name = "Rogue", "Beast", "Pharaoh Cat"
	mana, attack, health = 1, 1, 2
	index = "Uldum~Rogue~Minion~1~1~2~Beast~Pharaoh Cat~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Add a random Reborn minion to your hand"
	poolIdentifier = "Reborn Minions"
	@classmethod
	def generatePool(cls, Game):
		minions = []
		for Cost in Game.MinionsofCost.keys():
			minions += [value for key, value in Game.MinionsofCost[Cost].items() if "~Reborn" in key]
		return "Reborn Minions", minions
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if curGame.mode == 0:
			if curGame.guides:
				minion = curGame.guides.pop(0)
			else:
				minion = npchoice(self.rngPool("Reborn Minions"))
				curGame.fixedGuides.append(minion)
			curGame.Hand_Deck.addCardtoHand(minion, self.ID, "type")
		return None
		
		
class PlagueofMadness(Spell):
	Class, name = "Rogue", "Plague of Madness"
	requireTarget, mana = False, 1
	index = "Uldum~Rogue~Spell~1~Plague of Madness"
	description = "Each player equips a 2/2 Knife with Poisonous"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.Game.equipWeapon(PlaguedKnife(self.Game, self.ID))
		self.Game.equipWeapon(PlaguedKnife(self.Game, 3-self.ID))
		return None
		
class PlaguedKnife(Weapon):
	Class, name, description = "Rogue", "Plagued Knife", "Poisonous"
	mana, attack, durability = 1, 2, 2
	index = "Uldum~Rogue~Weapon~1~2~2~Plagued Knife~Poisonous~Uncollectible"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.keyWords["Poisonous"] = 1
		
		
class CleverDisguise(Spell):
	Class, name = "Rogue", "Clever Disguise"
	requireTarget, mana = False, 2
	index = "Uldum~Rogue~Spell~2~Clever Disguise"
	description = "Add 2 random spells from another Class to your hand"
	poolIdentifier = "Druid Spells"
	@classmethod
	def generatePool(cls, Game):
		return [Class+" Spells" for Class in Game.Classes], \
				[[value for key, value in Game.ClassCards[Class].items() if "~Spell~" in key] for Class in Game.Classes]
				
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if curGame.mode == 0:
			if curGame.guides:
				spells = curGame.guides.pop(0)
			else:
				classes = self.rngPool("Classes")[:]
				try: classes.remove(curGame.heroes[self.ID].Class)
				except: pass
				pool = self.rngPool("%s Spells"%npchoice(classes))
				spells = [npchoice(pool) for i in range(2)]
				curGame.fixedGuides.append(tuple(spells))
			curGame.Hand_Deck.addCardtoHand(spells, self.ID, "type")
		return None
		
		
class WhirlkickMaster(Minion):
	Class, race, name = "Rogue", "", "Whirlkick Master"
	mana, attack, health = 2, 1, 2
	index = "Uldum~Rogue~Minion~2~1~2~None~Whirlkick Master"
	requireTarget, keyWord, description = False, "", "Whenever you play a Combo card, add a random Combo card to your hand"
	poolIdentifier = "Combo Cards"
	@classmethod
	def generatePool(cls, Game):
		return "Combo Cards", [value for key, value in Game.ClassCards["Rogue"].items() if "~Combo~" in key or key.endswith("~Combo")]
		
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_WhirlkickMaster(self)]
		
class Trig_WhirlkickMaster(TrigBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionPlayed", "SpellPlayed", "WeaponPlayed", "HeroCardPlayed"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		#这个随从本身是没有连击的。同时目前没有名字中带有Combo的牌。
		return self.entity.onBoard and subject.ID == self.entity.ID and "~Combo" in subject.index
		
	def text(self, CHN):
		return "每当你使用一张连击牌时，随机将一张连击牌置入你的手牌" if CHN else "Whenever you play a Combo card, add a random Combo card to your hand"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		curGame = self.entity.Game
		if curGame.mode == 0:
			if curGame.guides:
				card = curGame.guides.pop(0)
			else:
				card = npchoice(self.rngPool("Combo Cards"))
				curGame.fixedGuides.append(card)
			curGame.Hand_Deck.addCardtoHand(card, self.entity.ID, "type")
			
			
class HookedScimitar(Weapon):
	Class, name, description = "Rogue", "Hooked Scimitar", "Combo: Gain +2 Attack"
	mana, attack, durability = 3, 2, 2
	index = "Uldum~Rogue~Weapon~3~2~2~Hooked Scimitar~Combo"
	
	def effCanTrig(self):
		self.effectViable = self.Game.Counters.numCardsPlayedThisTurn[self.ID] > 0
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if self.Game.Counters.numCardsPlayedThisTurn[self.ID] > 0:
			self.gainStat(2, 0)
		return None
		
		
class SahketSapper(Minion):
	Class, race, name = "Rogue", "Pirate", "Sahket Sapper"
	mana, attack, health = 4, 4, 4
	index = "Uldum~Rogue~Minion~4~4~4~Pirate~Sahket Sapper~Deathrattle"
	requireTarget, keyWord, description = False, "", "Deathrattle: Return a random enemy minion to your opponent's hand"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [ReturnaRandomEnemyMiniontoHand(self)]
		
class ReturnaRandomEnemyMiniontoHand(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		curGame = self.entity.Game
		if curGame.mode == 0:
			if curGame.guides:
				i = curGame.guides.pop(0)
			else:
				minions = curGame.minionsonBoard(3-self.entity.ID)
				i = npchoice(minions).pos if minions else -1
				curGame.fixedGuides.append(i)
			if i > -1:
				curGame.returnMiniontoHand(curGame.minions[3-self.entity.ID][i]) #minion是在场上的，所以不需要询问是否保留亡语注册
				
	def text(self, CHN):
		return "亡语：随机将一张敌方随从移回对手的手牌" if CHN else "Deathrattle: Return a random enemy minion to your opponent's hand"
		
		
class BazaarMugger(Minion):
	Class, race, name = "Rogue", "", "Bazaar Mugger"
	mana, attack, health = 5, 3, 5
	index = "Uldum~Rogue~Minion~5~3~5~None~Bazaar Mugger~Rush~Battlecry"
	requireTarget, keyWord, description = False, "Rush", "Rush. Battlecry: Add a random minion from another class to your hand"
	poolIdentifier = "Druid Minions"
	@classmethod
	def generatePool(cls, Game):
		return list(Game.Classes), [[value for key, value in Game.ClassCards[Class].items() if "~Minion~" in key] for Class in Game.Classes]
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if curGame.mode == 0:
			if curGame.guides:
				minion = curGame.guides.pop(0)
			else:
				classes = self.rngPool("Classes")[:]
				try: classes.remove(self.Game.heroes[self.ID].Class)
				except: pass
				minion = npchoice(self.rngPool(npchoice(classes)+" Minions"))
				curGame.fixedGuides.append(minion)
			curGame.Hand_Deck.addCardtoHand(minion, self.ID, "type")
		return None
		
		
class ShadowofDeath(Spell):
	Class, name = "Rogue", "Shadow of Death"
	requireTarget, mana = True, 4
	index = "Uldum~Rogue~Spell~4~Shadow of Death"
	description = "Choose a minion. Shuffle 3 'Shadows' into your deck that summon a copy when drawn"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			typeName = type(target).__name__
			newIndex = "Uldum~Rogue~4~Spell~Shadow~Casts When Drawn~Summon %s~Uncollectible"%typeName
			subclass = type("Shadow_Mutable_"+typeName, (Shadow_Mutable, ),
							{"index": newIndex, "description": "Casts When Drawn. Summon a "+typeName,
							"miniontoSummon": type(target)}
							)
			self.Game.cardPool[newIndex] = subclass #Create the subclass and add it to the game's cardPool.
			self.Game.Hand_Deck.shuffleCardintoDeck([subclass(self.Game, self.ID) for i in range(3)], self.ID)
		return target
		
class Shadow_Mutable(Spell):
	Class, name = "Rogue", "Shadow"
	requireTarget, mana = False, 4
	index = "Uldum~Rogue~Spell~4~Shadow~Casts When Drawn~Uncollectible"
	description = "Casts When Drawn. Summon a (0)"
	miniontoSummon = None
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.miniontoSummon = type(self).miniontoSummon
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if self.miniontoSummon:
			minion = self.miniontoSummon(self.Game, self.ID)
			self.Game.summon(minion, -1, self.ID)
		return None
		
		
class AnkatheBuried(Minion):
	Class, race, name = "Rogue", "", "Anka, the Buried"
	mana, attack, health = 5, 5, 5
	index = "Uldum~Rogue~Minion~5~5~5~None~Anka, the Buried~Battlecry~Legendary"
	requireTarget, keyWord, description = False, "", "Battlecry: Change each Deathrattle minion in your hand into a 1/1 that costs (1)"
	#不知道安卡的战吼是否会把手牌中的亡语随从变成新的牌还是只会修改它们的身材
	def effCanTrig(self):
		return any(card.type == "Minion" and card.deathrattles and card != self for card in self.Game.Hand_Deck.hands[self.ID])
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		for card in self.Game.Hand_Deck.hands[self.ID][:]:
			if card.type == "Minion" and card.deathrattles != []:
				card.statReset(1, 1)
				ManaMod(card, changeby=0, changeto=1).applies()
		return None
		
"""Shaman cards"""
class CorrupttheWaters(Quest):
	Class, name = "Shaman", "Corrupt the Waters"
	requireTarget, mana = False, 1
	index = "Uldum~Shaman~Spell~1~Corrupt the Waters~~Quest~Legendary"
	description = "Quest: Play 6 Battlecry cards. Reward: Heart of Vir'naal"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_CorrupttheWaters(self)]
		
class Trig_CorrupttheWaters(QuestTrigger):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionBeenPlayed", "WeaponBeenPlayed", "HeroCardBeenPlayed"]) #扳机是使用后扳机
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject.ID == self.entity.ID and "~Battlecry" in subject.index
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.counter += 1
		if self.counter > 5:
			self.disconnect()
			try: self.entity.Game.Secrets.mainQuests[self.entity.ID].remove(self.entity)
			except: pass
			HeartofVirnaal(self.entity.Game, self.entity.ID).replaceHeroPower()
			
class HeartofVirnaal(HeroPower):
	mana, name, requireTarget = 2, "Heart of Vir'naal", False
	index = "Shaman~Hero Power~2~Heart of Vir'naal"
	description = "Your Battlecries trigger twice this turn"
	def effect(self, target=None, choice=0):
		self.Game.status[self.ID]["Battlecry x2"] += 1
		self.Game.turnEndTrigger.append(HeartofVirnaal_Effect(self.Game, self.ID))
		return 0
		
class HeartofVirnaal_Effect:
	def __init__(self, Game, ID):
		self.Game, self.ID = Game, ID
		
	def turnEndTrigger(self):
		self.Game.status[self.ID]["Battlecry x2"] -= 1
		try: self.Game.turnEndTrigger.remove(self)
		except: pass
		
	def createCopy(self, game): #TurnEndTrigger
		return type(self)(game, self.ID)
		
		
class TotemicSurge(Spell):
	Class, name = "Shaman", "Totemic Surge"
	requireTarget, mana = False, 0
	index = "Uldum~Shaman~Spell~0~Totemic Surge"
	description = "Give your Totems +2 Attack"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		for minion in self.Game.minionsonBoard(self.ID):
			if "Totem" in minion.race: minion.buffDebuff(2, 0)
		return None
		
		
class EVILTotem(Minion):
	Class, race, name = "Shaman", "Totem", "EVIL Totem"
	mana, attack, health = 2, 0, 2
	index = "Uldum~Shaman~Minion~2~0~2~Totem~EVIL Totem"
	requireTarget, keyWord, description = False, "", "At the end of your turn, add a Lackey to your hand"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_EVILTotem(self)]
		
class Trig_EVILTotem(TrigBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["TurnEnds"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and ID == self.entity.ID
		
	def text(self, CHN):
		return "在你的回合结束时，将一张跟班牌置入你的手牌" if CHN else "At the end of your turn, add a Lackey to your hand"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		curGame = self.entity.Game
		if curGame.mode == 0:
			if curGame.guides:
				lackey = curGame.guides.pop(0)
			else:
				lackey = npchoice(Lackeys)
				curGame.fixedGuides.append(lackey)
			curGame.Hand_Deck.addCardtoHand(lackey, self.entity.ID, "type")
			
			
class SandstormElemental(Minion):
	Class, race, name = "Shaman", "Elemental", "Sandstorm Elemental"
	mana, attack, health = 2, 2, 2
	index = "Uldum~Shaman~Minion~2~2~2~Elemental~Sandstorm Elemental~Overload~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Deal 1 damage to all enemy minions. Overload: (1)"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.overload = 1
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		targets = self.Game.minionsonBoard(3-self.ID)
		self.dealsAOE(targets, [1 for minion in targets])
		return None
		
		
class PlagueofMurlocs(Spell):
	Class, name = "Shaman", "Plague of Murlocs"
	requireTarget, mana = False, 3
	index = "Uldum~Shaman~Spell~3~Plague of Murlocs"
	description = "Transform all minions into random Murlocs"
	poolIdentifier = "Murlocs"
	@classmethod
	def generatePool(cls, Game):
		return "Murlocs", list(Game.MinionswithRace["Murloc"].values())
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if curGame.mode == 0:
			minions = curGame.minionsonBoard(1) + curGame.minionsonBoard(2)
			if curGame.guides:
				murlocs = curGame.guides.pop(0)
			else:
				murlocs = tuple(npchoice(self.rngPool("Murlocs"), len(minions), replace=True))
				curGame.fixedGuides.append(murlocs)
			for minion, murloc in zip(minions, murlocs):
				curGame.transform(minion, murloc(curGame, minion.ID))
		return None
		
		
class WeaponizedWasp(Minion):
	Class, race, name = "Shaman", "Beast", "Weaponized Wasp"
	mana, attack, health = 3, 3, 3
	index = "Uldum~Shaman~Minion~3~3~3~Beast~Weaponized Wasp~Battlecry"
	requireTarget, keyWord, description = True, "", "Battlecry: If you control a Lackey, deal 3 damage"
	def returnTrue(self, choice=0):
		for minion in self.Game.minionsonBoard(self.ID):
			if "Lackey" in minion.name and "~Uncollectible" in minion.index:
				return True
		return False
		
	def effCanTrig(self):
		self.effectViable = False
		if self.targetExists():
			for minion in self.Game.minionsonBoard(self.ID):
				if minion.name.endswith("Lackey"):
					self.effectViable = True
					
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		controlsLackey = False
		for minion in self.Game.minionsonBoard(self.ID):
			if "Lackey" in minion.name and "~Uncollectible" in minion.index:
				controlsLackey = True
				
		if target and controlsLackey:
			self.dealsDamage(target, 3)
		return target
		
		
class SplittingAxe(Weapon):
	Class, name, description = "Shaman", "Splitting Axe", "Battlecry: Summon copies of your Totems"
	mana, attack, durability = 4, 3, 2
	index = "Uldum~Shaman~Weapon~4~3~2~Splitting Axe~Battlecry"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		for minion in self.Game.minionsonBoard(self.ID):
			if "Totem" in minion.race:
				self.Game.summon(minion.selfCopy(minion.ID), minion.pos+1, self.ID)
		return None
		
		
class Vessina(Minion):
	Class, race, name = "Shaman", "", "Vessina"
	mana, attack, health = 4, 2, 6
	index = "Uldum~Shaman~Minion~4~2~6~None~Vessina~Legendary"
	requireTarget, keyWord, description = False, "", "While you're Overloaded, your other minions have +2 Attack"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.auras["While you're Overloaded, your other minions have +2 Attack"] = BuffAura_Vessina(self)
		self.activated = False
		
class BuffAura_Vessina(HasAura_toMinion):
	def __init__(self, entity):
		self.entity = entity
		self.signals, self.auraAffected = ["MinionAppears", "OverloadCheck"], []
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		if signal == "MinionAppears":
			return self.entity.onBoard and subject.ID == self.entity.ID and subject != self.entity and self.entity.activated
		else:
			return self.entity.onBoard and ID == self.entity.ID
			
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		if signal == "MinionAppears":
			if self.entity.activated:
				self.applies(subject)
		else: #signal == "OverloadCheck"
			isOverloaded = self.entity.Game.Manas.manasOverloaded[self.entity.ID] > 0 or self.entity.Game.Manas.manasLocked[self.entity.ID] > 0
			if isOverloaded == False and self.entity.activated:
				self.entity.activated = False
				for minion, receiver in self.auraAffected[:]:
					receiver.effectClear()
				self.auraAffected = []
			elif isOverloaded and self.entity.activated == False:
				self.entity.activated = True
				for minion in self.entity.Game.minionsonBoard(self.entity.ID):
					self.applies(minion)
					
	def applies(self, subject):
		if subject != self.entity:
			Stat_Receiver(subject, self, 2, 0).effectStart()
			
	def auraAppears(self):
		game = self.entity.Game
		isOverloaded = game.Manas.manasOverloaded[self.entity.ID] > 0 or game.Manas.manasLocked[self.entity.ID] > 0
		if isOverloaded:
			self.entity.activated = True
			for minion in game.minionsonBoard(self.entity.ID):
				self.applies(minion)
				
		try: game.trigsBoard[self.entity.ID]["MinionAppears"].append(self)
		except: game.trigsBoard[self.entity.ID]["MinionAppears"] = [self]
		try: game.trigsBoard[self.entity.ID]["OverloadCheck"].append(self)
		except: game.trigsBoard[self.entity.ID]["OverloadCheck"] = [self]
		
	def selfCopy(self, recipient):
		return type(self)(recipient)
	#可以通过HasAura_toMinion的createCopy方法复制
	
	
class Earthquake(Spell):
	Class, name = "Shaman", "Earthquake"
	requireTarget, mana = False, 7
	index = "Uldum~Shaman~Spell~7~Earthquake"
	description = "Deal 5 damage to all minions, then deal 2 damage to all minions"
	def text(self, CHN):
		damage5 = (5 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		damage2 = (2 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		return "对所有随从造成%d点伤害，再对所有随从造成%d点伤害"%(damage5, damage2) if CHN \
				else "Deal %d damage to all minions, then deal %d damage to all minions"%(damage5, damage2)
				
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		damage5 = (5 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		targets = self.Game.minionsonBoard(self.ID) + self.Game.minionsonBoard(3-self.ID)
		self.dealsAOE(targets, [damage5]*len(targets))
		#地震术在第一次AOE后会让所有随从结算死亡事件，然后再次对全场随从打2.
		self.Game.gathertheDead()
		#假设法强随从如果在这个过程中死亡并被移除，则法强等数值会随之变化。
		damage2 = (2 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		targets = self.Game.minionsonBoard(self.ID) + self.Game.minionsonBoard(3-self.ID)
		self.dealsAOE(targets, [damage2]*len(targets))
		return None
		
		
class MoguFleshshaper(Minion):
	Class, race, name = "Shaman", "", "Mogu Fleshshaper"
	mana, attack, health = 9, 3, 4
	index = "Uldum~Shaman~Minion~9~3~4~None~Mogu Fleshshaper~Rush"
	requireTarget, keyWord, description = False, "Rush", "Rush. Costs (1) less for each minion on the battlefield"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsHand = [Trig_MoguFleshshaper(self)]
		
	def selfManaChange(self):
		if self.inHand:
			num = len(self.Game.minionsonBoard(1)) + len(self.Game.minionsonBoard(2))
			self.mana -= num
			self.mana = max(0, self.mana)
			
class Trig_MoguFleshshaper(TrigHand):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionAppears", "MinionDisappears"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.inHand
		
	def text(self, CHN):
		return "每当场上有随从出现或离场时，重新计算费用" if CHN else "Whenever a minion appears/disappears, recalculate the cost"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.Game.Manas.calcMana_Single(self.entity)
		
		
"""Warlock cards"""
class PlagueofFlames(Spell):
	Class, name = "Warlock", "Plague of Flames"
	requireTarget, mana = False, 1
	index = "Uldum~Warlock~Spell~1~Plague of Flames"
	description = "Destroy all your minions. For each one, destroy a random enemy minion"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if curGame.mode == 0:
			if curGame.guides:
				curGame.killMinion(self, curGame.minionsonBoard(self.ID))
				enemyMinions = curGame.minions[3-self.ID]
				curGame.killMinion(self, [enemyMinions[i] for i in curGame.guides.pop(0)])
			else:
				ownMinions = curGame.minionsonBoard(self.ID)
				num = len(ownMinions)
				curGame.killMinion(self, ownMinions)
				enemyMinions = curGame.minionsonBoard(3-self.ID)
				if num > 0 and enemyMinions:
					minions = npchoice(enemyMinions, min(num, len(enemyMinions)), replace=True)
					indices = [minion.pos for minion in minions]
					curGame.fixedGuides.append(tuple(indices))
					curGame.killMinion(self, minions)
				else:
					curGame.fixedGuides.append(())
		return None
		
		
class SinisterDeal(Spell):
	Class, name = "Warlock", "Sinister Deal"
	requireTarget, mana = False, 1
	index = "Uldum~Warlock~Spell~1~Sinister Deal"
	description = "Discover a Lackey"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if curGame.mode == 0:
			if curGame.guides:
				curGame.Hand_Deck.addCardtoHand(curGame.guides.pop(0), self.ID, "type", byDiscover=True)
			else:
				if self.ID != curGame.turn or "byOthers" in comment:
					lackey = npchoice(Lackeys)
					curGame.fixedGuides.append(lackey)
					curGame.Hand_Deck.addCardtoHand(lackey, self.ID, "type", byDiscover=True)
				else:
					lackeys = npchoice(Lackeys, 3, replace=False)
					curGame.options = [lackey(curGame, self.ID) for lackey in lackeys]
					curGame.Discover.startDiscover(self)
		return None
		
	def discoverDecided(self, option, info):
		self.Game.fixedGuides.append(type(option))
		self.Game.Hand_Deck.addCardtoHand(option, self.ID, byDiscover=True)
		
		
class SupremeArchaeology(Quest):
	Class, name = "Warlock", "Supreme Archaeology"
	requireTarget, mana = False, 1
	index = "Uldum~Warlock~Spell~1~Supreme Archaeology~~Quest~Legendary"
	description = "Quest: Draw 20 cards. Reward: Tome of Origination"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_SupremeArchaeology(self)]
		
class Trig_SupremeArchaeology(QuestTrigger):
	def __init__(self, entity):
		self.blank_init(entity, ["CardDrawn"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.counter += 1
		if self.counter > 19:
			self.disconnect()
			try: self.entity.Game.Secrets.mainQuests[self.entity.ID].remove(self.entity)
			except: pass
			TomeofOrigination(self.entity.Game, self.entity.ID).replaceHeroPower()
			
class TomeofOrigination(HeroPower):
	mana, name, requireTarget = 2, "Tome of Origination", False
	index = "Warlock~Hero Power~2~Tome of Origination"
	description = "Draw a card. It costs (0)"
	def effect(self, target=None, choice=0):
		card, mana = self.Game.Hand_Deck.drawCard(self.ID)
		if card:
			self.Game.sendSignal("CardDrawnfromHeroPower", self.ID, self, card, mana, "")
			ManaMod(card, changeby=0, changeto=0).applies()
		return 0
		
		
class ExpiredMerchant(Minion):
	Class, race, name = "Warlock", "", "Expired Merchant"
	mana, attack, health = 2, 2, 1
	index = "Uldum~Warlock~Minion~2~2~1~None~Expired Merchant~Battlecry~Deathrattle"
	requireTarget, keyWord, description = False, "", "Battlecry: Discard your highest Cost card. Deathrattle: Add 2 copies of it to your hand"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [Return2CopiesofDiscardedCard(self)]
		
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
			if i > -1:
				card = curGame.Hand_Deck.hands[self.ID][i]
				curGame.Hand_Deck.discardCard(self.ID, i)
				for trig in self.deathrattles:
					if isinstance(trig, Return2CopiesofDiscardedCard):
						trig.discardedCard = type(card)
		return None
		
class Return2CopiesofDiscardedCard(Deathrattle_Minion):
	def __init__(self, entity):
		self.blank_init(entity)
		self.discardedCard = None
		
	def text(self, CHN):
		return "亡语：将两张%s加入你的手牌"%self.discardedCard.name if CHN \
				else "Deathrattle: Add 2 copies of %s to your hand"%self.discardedCard.name
				
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		if self.discardedCard:
			self.entity.Game.Hand_Deck.addCardtoHand([self.discardedCard, self.discardedCard], self.entity.ID, "type")
			
	def selfCopy(self, recipient):
		trig = type(self)(recipient)
		trig.discardedCard = self.discardedCard
		return trig
		
class EVILRecruiter(Minion):
	Class, race, name = "Warlock", "", "EVIL Recruiter"
	mana, attack, health = 3, 3, 3
	index = "Uldum~Warlock~Minion~3~3~3~None~EVIL Recruiter~Battlecry"
	requireTarget, keyWord, description = True, "", "Battlecry: Destroy a friendly Lackey to summon a 5/5 Demon"
	
	def targetExists(self, choice=0):
		return self.selectableFriendlyMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.ID == self.ID and "Lackey" in target.name and "~Uncollectible" in target.index and target.onBoard
		
	def effCanTrig(self): #Friendly minions are always selectable.
		self.effectViable = False
		for minion in self.Game.minionsonBoard(self.ID):
			if minion.name.endswith("Lackey"):
				self.effectViable = True
				
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			#假设消灭跟班之后会进行强制死亡结算，把跟班移除之后才召唤
			#假设召唤的恶魔是在EVIL Recruiter的右边，而非死亡的跟班的原有位置
			self.Game.killMinion(self, target)
			self.Game.gathertheDead()
			self.Game.summon(EVILDemon(self.Game, self.ID), self.pos+1, self.ID)
		return target
		
class EVILDemon(Minion):
	Class, race, name = "Warlock", "Demon", "EVIL Demon"
	mana, attack, health = 5, 5, 5
	index = "Uldum~Warlock~Minion~5~5~5~Demon~EVIL Demon~Uncollectible"
	requireTarget, keyWord, description = False, "", ""
	
	
class NefersetThrasher(Minion):
	Class, race, name = "Warlock", "", "Neferset Thrasher"
	mana, attack, health = 3, 4, 5
	index = "Uldum~Warlock~Minion~3~4~5~None~Neferset Thrasher"
	requireTarget, keyWord, description = False, "", "Whenever this attacks, deal 3 damage to your hero"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_NefersetThrasher(self)]
		
class Trig_NefersetThrasher(TrigBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionAttackingMinion", "MinionAttackingHero"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject == self.entity and self.entity.onBoard
		
	def text(self, CHN):
		return "每当该随从进行攻击，对你的英雄造成3点伤害" if CHN else "Whenever this attacks, deal 3 damage to your hero"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.dealsDamage(self.entity.Game.heroes[self.entity.ID], 3)
		
		
class Impbalming(Spell):
	Class, name = "Warlock", "Impbalming"
	requireTarget, mana = True, 4
	index = "Uldum~Warlock~Spell~4~Impbalming"
	description = "Destroy a minion. Shuffle 3 Worthless Imps into your deck"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			self.Game.killMinion(self, target)
			self.Game.Hand_Deck.shuffleCardintoDeck([WorthlessImp_Uldum(self.Game, self.ID) for i in range(3)], self.ID)
		return target
		
class WorthlessImp_Uldum(Minion):
	Class, race, name = "Warlock", "Demon", "Worthless Imp"
	mana, attack, health = 1, 1, 1
	index = "Uldum~Warlock~Minion~1~1~1~Demon~Worthless Imp~Uncollectible"
	requireTarget, keyWord, description = False, "", ""
	
	
class DiseasedVulture(Minion):
	Class, race, name = "Warlock", "Beast", "Diseased Vulture"
	mana, attack, health = 4, 3, 5
	index = "Uldum~Warlock~Minion~4~3~5~Beast~Diseased Vulture"
	requireTarget, keyWord, description = False, "", "After your hero takes damage on your turn, summon a random 3-Cost minion"
	poolIdentifier = "3-Cost Minions to Summon"
	@classmethod
	def generatePool(cls, Game):
		return "3-Cost Minions to Summon", list(Game.MinionsofCost[3].values())
		
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_DiseasedVulture(self)]
		
class Trig_DiseasedVulture(TrigBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["HeroTookDmg"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return target == self.entity.Game.heroes[self.entity.ID] and self.entity.ID == self.entity.Game.turn
		
	def text(self, CHN):
		return "每当你的英雄在自己的回合受到伤害后，随机召唤一个法力值消耗为(3)的随从" if CHN \
				else "After your hero takes damage on your turn, summon a random 3-Cost minion"
				
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		curGame = self.entity.Game
		if curGame.mode == 0:
			if curGame.guides:
				minion = curGame.guides.pop(0)
			else:
				minion = npchoice(self.rngPool("3-Cost Minions to Summon"))
				curGame.fixedGuides.append(minion)
			curGame.summon(minion(curGame, self.entity.ID), self.entity.pos+1, self.entity.ID)
			
			
class Riftcleaver(Minion):
	Class, race, name = "Warlock", "Demon", "Riftcleaver"
	mana, attack, health = 6, 7, 5
	index = "Uldum~Warlock~Minion~6~7~5~Demon~Riftcleaver~Battlecry"
	requireTarget, keyWord, description = True, "", "Battlecry: Destroy a minion. Your hero takes damage equal to its health"
	
	def targetExists(self, choice=0):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target != self and target.onBoard
		#不知道连续触发战吼时，第二次是否还会让玩家受到伤害
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target and not target.dead == False:
			damage, target.dead = max(0, target.health), True
			#不知道这个对于英雄的伤害有无伤害来源。假设没有，和抽牌疲劳伤害类似
			dmgTaker = self.Game.scapegoat4(self.Game.heroes[self.ID])
			dmgTaker.takesDamage(None, damage, damageType="Ability") #假设伤害没有来源
		return target
		
#光环生效时跟班变成白字的4/4，可以在之后被buff，reset和光环buff。返回手牌中时也会是4/4的身材。沉默之后仍为4/4
#无面操纵者复制对方的4/4跟班也会得到4/4的跟班
#光环生效时的非光环buff会消失，然后成为4/4白字
class DarkPharaohTekahn(Minion):
	Class, race, name = "Warlock", "", "Dark Pharaoh Tekahn"
	mana, attack, health = 5, 4, 4
	index = "Uldum~Warlock~Minion~5~4~4~None~Dark Pharaoh Tekahn~Battlecry~Legendary"
	requireTarget, keyWord, description = False, "", "Battlecry: For the rest of the game, your Lackeys are 4/4"
	name_CN = "黑暗法老 塔卡恒"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		YourLackeysareAlways44(self.Game, self.ID).auraAppears()
		return None
		
class YourLackeysareAlways44(HasAura_toMinion):
	def __init__(self, Game, ID):
		self.Game, self.ID = Game, ID
		self.signals, self.auraAffected = ["MinionAppears", "CardEntersHand"], []
		
	def applicable(self, target):
		return target.ID == self.ID and target.name.endswith("Lackey")
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		if signal[0] == 'M': #"MinionAppears" #只有随从在从其他位置进入场上的时候可以进行修改，而从休眠中苏醒或者控制权改变不会触发改变
			return comment and self.applicable(subject)
		elif signal[0] == 'C':
			return self.applicable(target[0]) #The target here is a holder
		#else: #signal == "CardShuffled"
		#	if isinstance(target, (list, ndarray)):
		#		for card in target:
		#			self.applicable(card)
		#	else: #Shuffling a single card
		#		return self.applicable(target)
				
	def text(self, CHN):
		return "在本局对战的剩余时间内，你的跟班变为4/4" if CHN \
				else "For the rest of the game, your Lackeys are 4/4"
				
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		if signal == "MinionAppears":
			self.applies(subject)
		elif signal == "CardEntersHand":
			self.applies(target[0])
		#else: #signal == "CardShuffled"
		#	self.applies(target)
			
	def applies(self, subject):
		if self.applicable(subject) and (subject.attack_0 != 4 or subject.health_0 != 4):
			subject.attack_0, subject.health_0 = 4, 4 #需要先把随从的白字身材变为4/4
			subject.statReset(4, 4)
			#暂时假设跟班被对方控制后仍为4/4
	def auraAppears(self):
		game = self.Game
		for i, obj in enumerate(game.trigAuras[self.ID]):
			if isinstance(obj, YourLackeysareAlways44):
				return
		game.trigAuras[self.ID].append(self)
		for card in game.minionsonBoard(self.ID) + game.Hand_Deck.hands[self.ID] + game.Hand_Deck.decks[self.ID]:
			self.applies(card)
		for sig in self.signals:
			try: game.trigsBoard[self.ID][sig].insert(0, self) #假设这种光环总是添加到最前面，保证它可以在其他的普通光环生效之前作用
			except: game.trigsBoard[self.ID][sig] = [self]
			
"""Warrior cards"""
class HacktheSystem(Quest):
	Class, name = "Warrior", "Hack the System"
	requireTarget, mana = False, 1
	index = "Uldum~Warrior~Spell~1~Hack the System~~Quest~Legendary"
	description = "Quest: Attack 5 times with your hero. Reward: Anraphet's Core"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_HacktheSystem(self)]
		
class Trig_HacktheSystem(QuestTrigger):
	def __init__(self, entity):
		self.blank_init(entity, ["HeroAttackedHero", "HeroAttackedMinion"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject == self.entity.Game.heroes[self.entity.ID]
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.counter += 1
		if self.counter > 4:
			self.disconnect()
			try: self.entity.Game.Secrets.mainQuests[self.entity.ID].remove(self.entity)
			except: pass
			AnraphetsCore(self.entity.Game, self.entity.ID).replaceHeroPower()
			
class AnraphetsCore(HeroPower):
	mana, name, requireTarget = 2, "Anraphet's Core", False
	index = "Warrior~Hero Power~2~Anraphet's Core"
	description = "Summon a 4/3 Golem. After your hero attacks, refresh this"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_AnraphetsCore(self)]
		
	def available(self, choice=0):
		if self.heroPowerTimes >= self.heroPowerChances_base + self.heroPowerChances_extra:
			return False
		if self.Game.space(self.ID) < 1:
			return False
		return True
		
	def effect(self, target=None, choice=0):
		#Hero Power summoning won't be doubled by Khadgar.
		self.Game.summon(StoneGolem(self.Game, self.ID), -1, self.ID, "")
		return 0
		
class Trig_AnraphetsCore(TrigBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["HeroAttackedHero", "HeroAttackedMinion"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject == self.entity.Game.heroes[self.entity.ID] and self.entity.heroPowerTimes >= self.entity.heroPowerChances_base + self.entity.heroPowerChances_extra
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.heroPowerChances_extra += 1
		
class StoneGolem(Minion):
	Class, race, name = "Warrior", "", "Stone Golem"
	mana, attack, health = 3, 4, 3
	index = "Uldum~Warrior~Minion~3~4~3~None~Stone Golem~Uncollectible"
	requireTarget, keyWord, description = False, "", ""
	
	
class IntotheFray(Spell):
	Class, name = "Warrior", "Into the Fray"
	requireTarget, mana = False, 1
	index = "Uldum~Warrior~Spell~1~Into the Fray"
	description = "Give all Taunt minions in your hand +2/+2"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		for card in self.Game.Hand_Deck.hands[self.ID][:]:
			if card.type == "Minion" and card.keyWords["Taunt"] > 0:
				card.buffDebuff(2, 2)
		return None
		
		
class FrightenedFlunky(Minion):
	Class, race, name = "Warrior", "", "Frightened Flunky"
	mana, attack, health = 2, 2, 2
	index = "Uldum~Warrior~Minion~2~2~2~None~Frightened Flunky~Taunt~Battlecry"
	requireTarget, keyWord, description = False, "Taunt", "Taunt. Battlecry: Discover a Taunt minion"
	poolIdentifier = "Taunt Minions as Warrior"
	@classmethod
	def generatePool(cls, Game):
		classCards = {s : [value for key, value in Game.ClassCards[s].items() if "~Minion~" in key and "~Taunt" in key] for s in Game.Classes}
		classCards["Neutral"] = [value for key, value in Game.NeutralCards.items() if "~Minion~" in key and "~Taunt" in key]
		return ["Taunt Minions as %s"%Class for Class in Game.Classes], \
				[classCards[Class]+classCards["Neutral"] for Class in Game.Classes]
				
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if self.ID == curGame.turn:
			if curGame.guides:
				curGame.Hand_Deck.addCardtoHand(curGame.guides.pop(0), self.ID, "type", byDiscover=True)
			else:
				key = "Taunt Minions as " + classforDiscover(self)
				if "byOthers" in comment:
					minion = npchoice(self.rngPool(key))
					curGame.fixedGuides.append(minion)
					curGame.Hand_Deck.addCardtoHand(minion, self.ID, "type", byDiscover=True)
				else:
					minions = npchoice(self.rngPool(key), 3, replace=False)
					curGame.options = [minion(curGame, self.ID) for minion in minions]
					curGame.Discover.startDiscover(self)
		return None
		
	def discoverDecided(self, option, info):
		self.Game.fixedGuides.append(type(option))
		self.Game.Hand_Deck.addCardtoHand(option, self.ID, byDiscover=True)
		
		
class BloodswornMercenary(Minion):
	Class, race, name = "Warrior", "", "Bloodsworn Mercenary"
	mana, attack, health = 3, 2, 2
	index = "Uldum~Warrior~Minion~3~2~2~None~Bloodsworn Mercenary~Battlecry"
	requireTarget, keyWord, description = True, "", "Battlecry: Choose a damaged friendly minion. Summon a copy of it"
	
	def targetExists(self, choice=0):
		return self.selectableFriendlyMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.ID == self.ID and target != self and target.onBoard and target.health < target.health_max
		
	def effCanTrig(self):
		self.effectViable = False
		for minion in self.Game.minionsonBoard(self.ID):
			if minion.health < minion.health_max:
				self.effectViable = True
				break
				
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			Copy = target.selfCopy(self.ID) if target.onBoard else type(target)(self.Game, self.ID)
			self.Game.summon(Copy, target.pos+1, self.ID)
		return target
		
		
class LivewireLance(Weapon):
	Class, name, description = "Warrior", "Livewire Lance", "After your hero attacks, add a Lackey to your hand"
	mana, attack, durability = 3, 2, 2
	index = "Uldum~Warrior~Weapon~3~2~2~Livewire Lance"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_LivewireLance(self)]
		
class Trig_LivewireLance(TrigBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["HeroAttackedMinion", "HeroAttackedHero"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		#The target can't be dying to trigger this
		return subject == self.entity.Game.heroes[self.entity.ID] and self.entity.onBoard
		
	def text(self, CHN):
		return "在你的英雄攻击后，将一张跟班牌置入你的手牌" if CHN else "After your hero attacks, add a Lackey to your hand"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		curGame = self.entity.Game
		if curGame.mode == 0:
			if curGame.guides:
				lackey = curGame.guides.pop(0)
			else:
				lackey = npchoice(Lackeys)
				curGame.fixedGuides.append(lackey)
			curGame.Hand_Deck.addCardtoHand(lackey, self.entity.ID, "type")
			
			
class RestlessMummy(Minion):
	Class, race, name = "Warrior", "", "Restless Mummy"
	mana, attack, health = 4, 3, 2
	index = "Uldum~Warrior~Minion~4~3~2~None~Restless Mummy~Rush~Reborn"
	requireTarget, keyWord, description = False, "Rush,Reborn", "Rush, Reborn"
	
	
class PlagueofWrath(Spell):
	Class, name = "Warrior", "Plague of Wrath"
	requireTarget, mana = False, 5
	index = "Uldum~Warrior~Spell~5~Plague of Wrath"
	description = "Destroy all damaged minions"
	def available(self):
		for minion in self.Game.minionsonBoard(1) + self.Game.minionsonBoard(2):
			if minion.health < minion.health_max:
				return True
		return False
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.Game.killMinion(self, [minion for minion in self.Game.minionsonBoard(1) + self.Game.minionsonBoard(2) if minion.health < minion.health_max])
		return None
		
		
class Armagedillo(Minion):
	Class, race, name = "Warrior", "Beast", "Armagedillo"
	mana, attack, health = 6, 4, 7
	index = "Uldum~Warrior~Minion~6~4~7~Beast~Armagedillo~Taunt~Legendary"
	requireTarget, keyWord, description = False, "Taunt", "Taunt. At the end of your turn, give all Taunt minions in your hand +2/+2"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_Armagedillo(self)]
		
class Trig_Armagedillo(TrigBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["TurnEnds"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and ID == self.entity.ID
		
	def text(self, CHN):
		return "在你的回合结束时，使手牌中所有嘲讽随从牌获得+2/+2" if CHN else "At the end of your turn, give all Taunt minions in your hand +2/+2"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		for card in self.entity.Game.Hand_Deck.hands[self.entity.ID]:
			if card.type == "Minion" and card.keyWords["Taunt"] > 0:
				card.buffDebuff(2, 2)
				
				
class ArmoredGoon(Minion):
	Class, race, name = "Warrior", "", "Armored Goon"
	mana, attack, health = 6, 6, 7
	index = "Uldum~Warrior~Minion~6~6~7~None~Armored Goon"
	requireTarget, keyWord, description = False, "", "Whenever your hero attacks, gain 5 Armor"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_ArmoredGoon(self)]
		
class Trig_ArmoredGoon(TrigBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["HeroAttackingHero", "HeroAttackingMinion"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject == self.entity.Game.heroes[self.entity.ID]
		
	def text(self, CHN):
		return "每当你的英雄攻击时，便获得5点护甲值" if CHN else "Whenever your hero attacks, gain 5 Armor"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.Game.heroes[self.entity.ID].gainsArmor(5)
		
		
class TombWarden(Minion):
	Class, race, name = "Warrior", "Mech", "Tomb Warden"
	mana, attack, health = 8, 3, 6
	index = "Uldum~Warrior~Minion~8~3~6~Mech~Tomb Warden~Taunt~Battlecry"
	requireTarget, keyWord, description = False, "Taunt", "Taunt. Battlecry: Summon a copy of this minion"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		minion = self.selfCopy(self.ID) if self.onBoard else type(self)(self.Game, self.ID)
		self.Game.summon(minion, self.pos+1, self.ID)
		return None
		
		
		
Uldum_Indices = {"Uldum~Neutral~Minion~1~1~2~None~Beaming Sidekick~Battlecry": BeamingSidekick,
				"Uldum~Neutral~Minion~1~1~1~None~Jar Dealer~Deathrattle": JarDealer,
				"Uldum~Neutral~Minion~1~1~1~None~Mogu Cultist~Battlecry": MoguCultist,
				"Uldum~Neutral~Minion~10~20~20~None~Highkeeper Ra~Legendary~Uncollectible": HighkeeperRa,
				"Uldum~Neutral~Minion~1~1~1~Murloc~Murmy~Reborn": Murmy,
				"Uldum~Neutral~Minion~2~2~1~None~Bug Collector~Battlecry": BugCollector,
				"Uldum~Neutral~Minion~1~1~1~Beast~Locust~Rush~Uncollectible": Locust,
				"Uldum~Neutral~Minion~2~2~3~None~Dwarven Archaeologist": DwarvenArchaeologist,
				"Uldum~Neutral~Minion~2~3~2~Murloc~Fishflinger~Battlecry": Fishflinger,
				"Uldum~Neutral~Minion~2~2~6~None~Injured Tol'vir~Taunt~Battlecry": InjuredTolvir,
				"Uldum~Neutral~Minion~2~2~1~None~Kobold Sandtrooper~Deathrattle": KoboldSandtrooper,
				"Uldum~Neutral~Minion~2~2~3~None~Neferset Ritualist~Battlecry": NefersetRitualist,
				"Uldum~Neutral~Minion~2~2~3~None~Questing Explorer~Battlecry": QuestingExplorer,
				"Uldum~Neutral~Minion~2~3~2~Elemental~Quicksand Elemental~Battlecry": QuicksandElemental,
				"Uldum~Neutral~Minion~2~0~3~None~Serpent Egg~Deathrattle": SerpentEgg,
				"Uldum~Neutral~Minion~3~3~4~Beast~Sea Serpent~Uncollectible": SeaSerpent,
				"Uldum~Neutral~Minion~2~2~4~Beast~Spitting Camel": SpittingCamel,
				"Uldum~Neutral~Minion~2~1~2~None~Temple Berserker~Reborn": TempleBerserker,
				"Uldum~Neutral~Minion~2~2~2~Demon~Vilefiend~Lifesteal": Vilefiend,
				"Uldum~Neutral~Minion~2~3~2~Elemental~Zephrys the Great~Battlecry~Legendary": ZephrystheGreat,
				"Uldum~Neutral~Minion~3~3~2~None~Candletaker~Reborn": Candletaker,
				"Uldum~Neutral~Minion~3~1~1~Beast~Desert Hare~Battlecry": DesertHare,
				"Uldum~Neutral~Minion~3~5~4~None~Generous Mummy~Reborn": GenerousMummy,
				"Uldum~Neutral~Minion~3~2~2~Beast~Golden Scarab~Battlecry": GoldenScarab,
				"Uldum~Neutral~Minion~3~3~4~None~History Buff": HistoryBuff,
				"Uldum~Neutral~Minion~3~2~3~None~Infested Goblin~Taunt~Deathrattle": InfestedGoblin,
				"Uldum~Neutral~Minion~1~1~1~Beast~Scarab~Taunt~Uncollectible": Scarab_Uldum,
				"Uldum~Neutral~Minion~3~3~3~None~Mischief Maker~Battlecry": MischiefMaker,
				"Uldum~Neutral~Minion~3~2~3~None~Vulpera Scoundrel~Battlecry": VulperaScoundrel,
				"Uldum~Neutral~Minion~4~2~5~None~Bone Wraith~Reborn~Taunt": BoneWraith,
				"Uldum~Neutral~Minion~4~4~4~None~Body Wrapper~Battlecry": BodyWrapper,
				"Uldum~Neutral~Minion~4~3~10~None~Conjured Mirage~Taunt": ConjuredMirage,
				"Uldum~Neutral~Minion~4~6~5~None~Sunstruck Henchman": SunstruckHenchman,
				"Uldum~Neutral~Minion~5~3~3~None~Faceless Lurker~Taunt~Battlecry": FacelessLurker,
				"Uldum~Neutral~Minion~5~0~5~None~Desert Obelisk": DesertObelisk,
				"Uldum~Neutral~Minion~5~8~8~Mech~Mortuary Machine": MortuaryMachine,
				"Uldum~Neutral~Minion~5~4~5~None~Phalanx Commander": PhalanxCommander,
				"Uldum~Neutral~Minion~5~4~2~None~Wasteland Assassin~Stealth~Reborn": WastelandAssassin,
				"Uldum~Neutral~Minion~6~5~5~None~Blatant Decoy~Deathrattle": BlatantDecoy,
				"Uldum~Neutral~Minion~6~3~4~None~Khartut Defender~Taunt~Reborn~Deathrattle": KhartutDefender,
				"Uldum~Neutral~Minion~7~6~6~Elemental~Siamat~Battlecry~Legendary": Siamat,
				"Uldum~Neutral~Minion~7~3~9~Beast~Wasteland Scorpid~Poisonous": WastelandScorpid,
				"Uldum~Neutral~Minion~7~7~5~None~Wrapped Golem~Reborn": WrappedGolem,
				"Uldum~Neutral~Minion~8~8~8~Beast~Octosari~Deathrattle~Legendary": Octosari,
				"Uldum~Neutral~Minion~8~5~6~Beast~Pit Crocolisk~Battlecry": PitCrocolisk,
				"Uldum~Neutral~Minion~9~9~6~None~Anubisath Warbringer~Deathrattle": AnubisathWarbringer,
				"Uldum~Neutral~Minion~10~10~10~None~Colossus of the Moon~Divine Shield~Reborn~Legendary": ColossusoftheMoon,
				"Uldum~Neutral~Minion~10~5~5~None~King Phaoris~Battlecry~Legendary": KingPhaoris,
				"Uldum~Neutral~Minion~10~10~10~None~Living Monument~Taunt": LivingMonument,
				"Uldum~Druid~Spell~1~Untapped Potential~~Quest~Legendary": UntappedPotential,
				"Uldum~Druid~Spell~1~Worthy Expedition": WorthyExpedition,
				"Uldum~Druid~Minion~2~1~4~None~Crystal Merchant": CrystalMerchant,
				"Uldum~Druid~Spell~3~BEEEES!!!": BEEEES,
				"Uldum~Druid~Minion~1~1~1~Beast~Bee~Uncollectible": Bee_Uldum,
				"Uldum~Druid~Minion~4~2~3~None~Garden Gnome~Battlecry": GardenGnome,
				"Uldum~Druid~Minion~2~2~2~None~Treant~Uncollectible": Treant_Uldum,
				"Uldum~Druid~Minion~5~3~5~None~Anubisath Defender~Taunt": AnubisathDefender,
				"Uldum~Druid~Minion~5~5~5~None~Elise the Enlightened~Battlecry~Legendary": ElisetheEnlightened,
				"Uldum~Druid~Minion~5~3~3~Elemental~Oasis Surger~Rush~Choose One": OasisSurger,
				"Uldum~Druid~Spell~6~Hidden Oasis~Choose One": HiddenOasis,
				"Uldum~Druid~Spell~6~Befriend the Ancient~Uncollectible": BefriendtheAncient,
				"Uldum~Druid~Spell~6~Drink the Water~Uncollectible": DrinktheWater,
				"Uldum~Druid~Minion~6~6~6~None~Vir'naal Ancient~Taunt~Uncollectible": VirnaalAncient,
				"Uldum~Druid~Spell~7~Overflow": Overflow,
				"Uldum~Hunter~Spell~1~Unseal the Vault~~Quest~Legendary": UnsealtheVault,
				
				"Uldum~Hunter~Spell~2~Pressure Plate~~Secret": PressurePlate,
				"Uldum~Hunter~Weapon~3~1~3~Desert Spear": DesertSpear,
				"Uldum~Hunter~Spell~3~Hunter's Pack": HuntersPack,
				"Uldum~Hunter~Minion~4~3~3~Beast~Hyena Alpha~Battlecry": HyenaAlpha,
				"Uldum~Hunter~Minion~2~2~2~Beast~Hyena~Uncollectible": Hyena_Uldum,
				"Uldum~Hunter~Minion~3~4~3~None~Ramkahen Wildtamer~Battlecry": RamkahenWildtamer,
				"Uldum~Hunter~Spell~6~Swarm of Locusts": SwarmofLocusts,
				"Uldum~Hunter~Minion~6~5~5~Beast~Scarlet Webweaver~Battlecry": ScarletWebweaver,
				"Uldum~Hunter~Minion~6~6~9~Beast~Wild Bloodstinger~Battlecry": WildBloodstinger,
				"Uldum~Hunter~Minion~7~2~4~None~Dinotamer Brann~Battlecry~Legendary": DinotamerBrann,
				"Uldum~Hunter~Minion~9~8~8~Beast~King Krush~Charge~Legendary~Uncollectible": KingKrush_Uldum,
				
				"Uldum~Mage~Spell~1~Raid the Sky Temple~~Quest~Legendary": RaidtheSkyTemple,
				"Uldum~Mage~Spell~2~Ancient Mysteries": AncientMysteries,
				"Uldum~Mage~Spell~3~Flame Ward~~Secret": FlameWard,
				"Uldum~Mage~Minion~5~4~4~Elemental~Cloud Prince~Battlecry": CloudPrince,
				"Uldum~Mage~Minion~2~3~2~None~Arcane Flakmage": ArcaneFlakmage,
				"Uldum~Mage~Minion~3~3~3~None~Dune Sculptor": DuneSculptor,
				"Uldum~Mage~Minion~5~5~5~None~Naga Sand Witch~Battlecry": NagaSandWitch,
				"Uldum~Mage~Minion~8~5~5~None~Tortollan Pilgrim~Battlecry": TortollanPilgrim,
				"Uldum~Mage~Minion~6~4~6~None~Reno the Relicologist~Battlecry~Legendary": RenotheRelicologist,
				"Uldum~Mage~Spell~10~Puzzle Box of Yogg-Saron": PuzzleBoxofYoggSaron,
				
				"Uldum~Paladin~Spell~1~Making Mummies~~Quest~Legendary": MakingMummies,
				"Uldum~Paladin~Minion~1~2~1~None~Brazen Zealot": BrazenZealot,
				"Uldum~Paladin~Minion~2~1~2~Mech~Micro Mummy~Reborn": MicroMummy,
				"Uldum~Paladin~Minion~2~3~1~Beast~Sandwasp Queen~Battlecry": SandwaspQueen,
				"Uldum~Paladin~Minion~1~2~1~Beast~Sandwasp~Uncollectible": Sandwasp,
				"Uldum~Paladin~Minion~2~2~3~Murloc~Sir Finley of the Sands~Battlecry~Legendary": SirFinleyoftheSands,
				"Uldum~Paladin~Spell~2~Subdue": Subdue,
				"Uldum~Paladin~Minion~3~3~1~Beast~Salhet's Pride~Deathrattle": SalhetsPride,
				"Uldum~Paladin~Minion~4~4~2~None~Ancestral Guardian~Lifesteal~Reborn": AncestralGuardian,
				"Uldum~Paladin~Spell~6~Pharaoh's Blessing": PharaohsBlessing,
				"Uldum~Paladin~Spell~8~Tip the Scales": TiptheScales,
				
				"Uldum~Priest~Spell~1~Activate the Obelisk~~Quest~Legendary": ActivatetheObelisk,
				"Uldum~Priest~Spell~1~Embalming Ritual": EmbalmingRitual,
				"Uldum~Priest~Spell~2~Penance": Penance,
				"Uldum~Priest~Minion~5~5~5~None~Sandhoof Waterbearer": SandhoofWaterbearer,
				"Uldum~Priest~Minion~2~1~2~None~Grandmummy~Reborn~Deathrattle": Grandmummy,
				"Uldum~Priest~Spell~2~Holy Ripple": HolyRipple,
				"Uldum~Priest~Minion~3~3~3~None~Wretched Reclaimer~Battlecry": WretchedReclaimer,
				"Uldum~Priest~Minion~4~3~1~None~Psychopomp~Battlecry": Psychopomp,
				"Uldum~Priest~Minion~4~2~7~None~High Priest Amet~Legendary": HighPriestAmet,
				"Uldum~Priest~Spell~9~Plague of Death": PlagueofDeath,
				
				"Uldum~Rogue~Spell~1~Bazaar Burglary~~Quest~Legendary": BazaarBurglary,
				"Uldum~Rogue~Weapon~2~3~2~Mirage Blade~Uncollectible": MirageBlade,
				"Uldum~Rogue~Minion~1~1~2~Beast~Pharaoh Cat~Battlecry": PharaohCat,
				"Uldum~Rogue~Spell~1~Plague of Madness": PlagueofMadness,
				"Uldum~Rogue~Weapon~1~2~2~Plagued Knife~Poisonous~Uncollectible": PlaguedKnife,
				"Uldum~Rogue~Spell~2~Clever Disguise": CleverDisguise,
				"Uldum~Rogue~Minion~2~1~2~None~Whirlkick Master": WhirlkickMaster,
				"Uldum~Rogue~Weapon~3~2~2~Hooked Scimitar~Combo": HookedScimitar,
				"Uldum~Rogue~Minion~4~4~4~Pirate~Sahket Sapper~Deathrattle": SahketSapper,
				"Uldum~Rogue~Minion~5~3~5~None~Bazaar Mugger~Rush~Battlecry": BazaarMugger,
				"Uldum~Rogue~Spell~4~Shadow of Death": ShadowofDeath,
				"Uldum~Rogue~Minion~5~5~5~None~Anka, the Buried~Battlecry~Legendary": AnkatheBuried,
				
				"Uldum~Shaman~Spell~1~Corrupt the Waters~~Quest~Legendary": CorrupttheWaters,
				"Uldum~Shaman~Spell~0~Totemic Surge": TotemicSurge,
				"Uldum~Shaman~Minion~2~0~2~Totem~EVIL Totem": EVILTotem,
				"Uldum~Shaman~Minion~2~2~2~Elemental~Sandstorm Elemental~Overload~Battlecry": SandstormElemental,
				"Uldum~Shaman~Spell~3~Plague of Murlocs": PlagueofMurlocs,
				"Uldum~Shaman~Minion~3~3~3~Beast~Weaponized Wasp~Battlecry": WeaponizedWasp,
				"Uldum~Shaman~Weapon~4~3~2~Splitting Axe~Battlecry": SplittingAxe,
				"Uldum~Shaman~Minion~4~2~6~None~Vessina~Legendary": Vessina,
				"Uldum~Shaman~Spell~7~Earthquake": Earthquake,
				"Uldum~Shaman~Minion~9~3~4~None~Mogu Fleshshaper~Rush": MoguFleshshaper,
				
				"Uldum~Warlock~Spell~1~Supreme Archaeology~~Quest~Legendary": SupremeArchaeology,
				"Uldum~Warlock~Spell~1~Plague of Flames": PlagueofFlames,
				"Uldum~Warlock~Spell~1~Sinister Deal": SinisterDeal,
				"Uldum~Warlock~Minion~2~2~1~None~Expired Merchant~Battlecry~Deathrattle": ExpiredMerchant,
				"Uldum~Warlock~Minion~3~3~3~None~EVIL Recruiter~Battlecry": EVILRecruiter,
				"Uldum~Warlock~Minion~5~5~5~Demon~EVIL Demon~Uncollectible": EVILDemon,
				"Uldum~Warlock~Minion~3~4~5~None~Neferset Thrasher": NefersetThrasher,
				"Uldum~Warlock~Spell~4~Impbalming": Impbalming,
				"Uldum~Warlock~Minion~1~1~1~Demon~Worthless Imp~Uncollectible": WorthlessImp_Uldum,
				"Uldum~Warlock~Minion~4~3~5~Beast~Diseased Vulture": DiseasedVulture,
				"Uldum~Warlock~Minion~6~7~5~Demon~Riftcleaver~Battlecry": Riftcleaver,
				"Uldum~Warlock~Minion~5~4~4~None~Dark Pharaoh Tekahn~Battlecry~Legendary": DarkPharaohTekahn,
				
				"Uldum~Warrior~Spell~1~Hack the System~~Quest~Legendary": HacktheSystem,
				"Uldum~Warrior~Minion~3~4~3~None~Stone Golem~Uncollectible": StoneGolem,
				"Uldum~Warrior~Spell~1~Into the Fray": IntotheFray,
				"Uldum~Warrior~Minion~2~2~2~None~Frightened Flunky~Taunt~Battlecry": FrightenedFlunky,
				"Uldum~Warrior~Minion~3~2~2~None~Bloodsworn Mercenary~Battlecry": BloodswornMercenary,
				"Uldum~Warrior~Weapon~3~2~2~Livewire Lance": LivewireLance,
				"Uldum~Warrior~Minion~4~3~2~None~Restless Mummy~Rush~Reborn": RestlessMummy,
				"Uldum~Warrior~Spell~5~Plague of Wrath": PlagueofWrath,
				"Uldum~Warrior~Minion~6~4~7~Beast~Armagedillo~Taunt~Legendary": Armagedillo,
				"Uldum~Warrior~Minion~6~6~7~None~Armored Goon": ArmoredGoon,
				"Uldum~Warrior~Minion~8~3~6~Mech~Tomb Warden~Taunt~Battlecry": TombWarden
				}