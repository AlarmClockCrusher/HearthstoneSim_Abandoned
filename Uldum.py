from CardTypes import *
from Triggers_Auras import *
from VariousHandlers import *

from Basic import Trigger_Corruption, Fireball, UpgradedHeroPowers
from Shadows import EtherealLackey, FacelessLackey, GoblinLackey, KoboldLackey, WitchyLackey
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
ClassesandNeutral = ["Neutral", "Demon Hunter", "Druid", "Hunter", "Mage", "Paladin", "Priest", "Rogue", "Shaman", "Warlock", "Warrior"]

"""Mana 1 cards"""
class BeamingSidekick(Minion):
	Class, race, name = "Neutral", "", "Beaming Sidekick"
	mana, attack, health = 1, 1, 2
	index = "Uldum~Neutral~Minion~1~1~2~None~Beaming Sidekick~Battlecry"
	requireTarget, keyWord, description = True, "", "Battlecry: Give a friendly minion +2 Health"
	
	def targetExists(self, choice=0):
		return self.selectableFriendlyMinionExists(choice)
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.ID == self.ID and target != self and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if target != None:
			PRINT(self, "Beaming Sidekick's battlecry gives friendly minion %s +2 Health"%target.name)
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
		PRINT(self, "Deathrattle: Add a random 1-cost minion to your hand triggers.")
		self.entity.Game.Hand_Deck.addCardtoHand(np.random.choice(self.entity.Game.RNGPools["1-Cost Minions"]), self.entity.ID, "CreateUsingType")
		
		
class MoguCultist(Minion):
	Class, race, name = "Neutral", "", "Mogu Cultist"
	mana, attack, health = 1, 1, 1
	index = "Uldum~Neutral~Minion~1~1~1~None~Mogu Cultist~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: If your board is full of Mogu Cultists, sacrifice them all and summon Highkeeper Ra"
	#强制要求场上有总共有7个魔古信徒，休眠物会让其效果无法触发
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		minions = self.Game.minionsonBoard(self.ID)
		if len(minions) == 7:
			allareMoguCultists = True
			for minion in minions:
				if minion.name != "Mogu Cultist":
					allareMoguCultists = False
					
			if allareMoguCultists:
				for minion in minions:
					minion.dead = True
				self.Game.gathertheDead()
				self.Game.summonMinion(HighkeeperRa(self.Game, self.ID), -1, self.ID)
		return None
		
class HighkeeperRa(Minion):
	Class, race, name = "Neutral", "", "Highkeeper Ra"
	mana, attack, health = 10, 20, 20
	index = "Uldum~Neutral~Minion~10~20~20~None~Highkeeper Ra~Legendary~Uncollectible"
	requireTarget, keyWord, description = False, "", "At the end of your turn, deal 20 damage to all enemies"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_HighkeeperRa(self)]
		
class Trigger_HighkeeperRa(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["TurnEnds"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self, "At the end of turn, %s deals 20 damage to all enemies."%self.entity.name)
		targets = [self.entity.Game.heroes[3-self.entity.ID]] + self.entity.Game.minionsonBoard(3-self.entity.ID)
		self.entity.dealsAOE(targets, [20 for obj in targets])
		
		
class Murmy(Minion):
	Class, race, name = "Neutral", "Murloc", "Murmy"
	mana, attack, health = 1, 1, 1
	index = "Uldum~Neutral~Minion~1~1~1~Murloc~Murmy~Reborn"
	requireTarget, keyWord, description = False, "Reborn", "Reborn"
	
	
class DraconicLackey(Minion):
	Class, race, name = "Neutral", "", "Draconic Lackey"
	mana, attack, health = 1, 1, 1
	index = "Dragons~Neutral~Minion~1~1~1~None~Draconic Lackey~Battlecry~Uncollectible"
	requireTarget, keyWord, description = False, "", "Battlecry: Discover a Dragon"
	poolIdentifier = "Dragons as Druid"
	@classmethod
	def generatePool(cls, Game):
		classes, lists, neutralCards = [], [], []
		classCards = {"Neutral": [], "Demon Hunter":[], "Druid":[], "Mage":[], "Hunter":[], "Paladin":[],
						"Priest":[], "Rogue":[], "Shaman":[], "Warlock":[], "Warrior":[]}
		for key, value in Game.MinionswithRace["Dragon"].items():
			classCards[key.split('~')[1]].append(value)
			
		for Class in Classes:
			classes.append("Dragons as "+Class)
			lists.append(classCards[Class]+classCards["Neutral"])
		return classes, lists #返回的包含“Class Cards except Hunter”等identifier的列表和其他职业卡表
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if self.Game.Hand_Deck.handNotFull(self.ID) and self.ID == self.Game.turn:
			key = "Dragons as "+classforDiscover(self)
			if "InvokedbyOthers" in comment:
				PRINT(self, "Draconic Lackey's battlecry adds a random Dragon to player's hand")
				self.Game.Hand_Deck.addCardtoHand(np.random.choice(self.Game.RNGPools[key]), self.ID, "CreateUsingType")
			else:
				dragons = np.random.choice(self.Game.RNGPools[key], 3, replace=False)
				self.Game.options = [dragon(self.Game, self.ID) for dragon in dragons]
				PRINT(self, "Draconic Lackey's battlecry lets player discover a Dragon")
				self.Game.DiscoverHandler.startDiscover(self)
				
		return None
		
	def discoverDecided(self, option):
		PRINT(self, "Dragon %s is put into player's hand."%option.name)
		self.Game.Hand_Deck.addCardtoHand(option, self.ID)
		self.Game.sendSignal("DiscoveredCardPutintoHand", self.ID, self, option, 0, "")
		
class TitanicLackey(Minion):
	Class, race, name = "Neutral", "", "Titanic Lackey"
	mana, attack, health = 1, 1, 1
	index = "Uldum~Neutral~Minion~1~1~1~None~Titanic Lackey~Battlecry~Uncollectible"
	requireTarget, keyWord, description = True, "", "Battlecry: Give a friendly minion +2 Health"
	
	def targetExists(self, choice=0):
		return self.selectableFriendlyMinionExists(choice)
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.ID == self.ID and target != self and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if target != None:
			PRINT(self, "Titanic Lackey's battlecry gives friendly minion %s +2 Health and Taunt"%target.name)
			target.buffDebuff(0, 2)
			target.getsKeyword("Taunt")
		return target
		
Lackeys = [DraconicLackey, EtherealLackey, FacelessLackey, GoblinLackey, KoboldLackey, TitanicLackey, WitchyLackey]

"""Mana 2 cards"""
class BugCollector(Minion):
	Class, race, name = "Neutral", "", "Bug Collector"
	mana, attack, health = 2, 2, 1
	index = "Uldum~Neutral~Minion~2~2~1~None~Bug Collector~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Summon a 1/1 Locust with Rush"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		PRINT(self, "Bug Collector's battlecry summons a 1/1 Locust with Rush")
		self.Game.summonMinion(Locust(self.Game, self.ID), self.position+1, self.ID)
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
		self.triggersonBoard = [Trigger_DwarvenArchaeologist(self)]
		
class Trigger_DwarvenArchaeologist(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["DiscoveredCardPutintoHand"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		#不知道被发现的牌如果来自对手，是否会享受减费。如Griftah
		return self.entity.onBoard and ID == self.entity.ID and target.ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self, "A card %s is Discovered and put into player's hand, it now costs (1) less."%target.name)
		ManaModification(target, changeby=-1, changeto=-1).applies()
		self.entity.Game.ManaHandler.calcMana_Single(target)
		
		
class Fishflinger(Minion):
	Class, race, name = "Neutral", "Murloc", "Fishflinger"
	mana, attack, health = 2, 3, 2
	index = "Uldum~Neutral~Minion~2~3~2~Murloc~Fishflinger~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Add a random Murloc to each player's hand"
	poolIdentifier = "Murlocs"
	@classmethod
	def generatePool(cls, Game):
		return "Murlocs", list(Game.MinionswithRace["Murloc"].values())
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		PRINT(self, "Fishflinger's battlecry adds a random Murloc to each player's hand.")
		murloc1, murloc2 = np.random.choice(self.Game.RNGPools["Murlocs"], 2, replace=True)
		self.Game.Hand_Deck.addCardtoHand(murloc1, self.ID, "CreateUsingType")
		self.Game.Hand_Deck.addCardtoHand(murloc2, 3-self.ID, "CreateUsingType")
		return None
		
		
class InjuredTolvir(Minion):
	Class, race, name = "Neutral", "", "Injured Tol'vir"
	mana, attack, health = 2, 2, 6
	index = "Uldum~Neutral~Minion~2~2~6~None~Injured Tol'vir~Battlecry"
	requireTarget, keyWord, description = False, "Taunt", "Taunt. Battlecry: Deal 3 damage to this minion"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		PRINT(self, "Injured Tol'vir's battlecry deals 3 damage to the minion")
		self.dealsDamage(self, 3)
		return None
		
		
class KoboldSandtrooper(Minion):
	Class, race, name = "Neutral", "", "Kobold Sandtrooper"
	mana, attack, health = 2, 3, 1
	index = "Uldum~Neutral~Minion~2~3~1~None~Kobold Sandtrooper~Deathrattle"
	requireTarget, keyWord, description = False, "", "Deathrattle: Deal 3 damage to the enemy hero"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [Deal3DamagetoEnemyHero(self)]
		
class Deal3DamagetoEnemyHero(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self, "Deathrattle: Deal 3 damage to the enemy hero triggers.")
		self.entity.dealsDamage(self.entity.Game.heroes[3-self.entity.ID], 3)
		
		
class NefersetRitualist(Minion):
	Class, race, name = "Neutral", "", "Neferset Ritualist"
	mana, attack, health = 2, 2, 3
	index = "Uldum~Neutral~Minion~2~2~3~None~Neferset Ritualist~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Restore adjacent minions to full Health"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if self.onBoard:
			PRINT(self, "Neferset Ritualist's battlecry restores adjacent friendly minions to full Health.")
			for minion in self.Game.findAdjacentMinions(self)[0]:
				heal = minion.health_upper * (2 ** self.countHealDouble())
				self.restoresHealth(minion, heal)
		return None
		
		
class QuestingExplorer(Minion):
	Class, race, name = "Neutral", "", "Questing Explorer"
	mana, attack, health = 2, 2, 3
	index = "Uldum~Neutral~Minion~2~2~3~None~Questing Explorer~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: If you control a Quest, draw a card"
	def effectCanTrigger(self):
		self.effectViable = self.Game.SecretHandler.mainQuests[self.ID] != [] or self.Game.SecretHandler.sideQuests[self.ID] != []
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if self.Game.SecretHandler.mainQuests[self.ID] != [] or self.Game.SecretHandler.sideQuests[self.ID] != []:
			PRINT(self, "Questing Explorer's battlecry lets player draw a card as player controls a Quest")
			self.Game.Hand_Deck.drawCard(self.ID)
		return None
		
		
class QuicksandElemental(Minion):
	Class, race, name = "Neutral", "Elemental", "Quicksand Elemental"
	mana, attack, health = 2, 3, 2
	index = "Uldum~Neutral~Minion~2~3~2~Elemental~Quicksand Elemental~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Give all enemy minions -2 Attack this turn"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		PRINT(self, "Quicksand Elemental's battlecry gives all enemy minions -2 Attack this turn")
		for minion in fixedList(self.Game.minionsonBoard(3-self.ID)):
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
		PRINT(self, "Deathrattle: Summon a 3/4 Sea Serpent triggers.")
		self.entity.Game.summonMinion(SeaSerpent(self.entity.Game, self.entity.ID), self.entity.position+1, self.entity.ID)
		
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
		self.triggersonBoard = [Trigger_SpittingCamel(self)]
		
class Trigger_SpittingCamel(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["TurnEnds"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self, "At the end of turn, %s deals 1 damage to another random friendly minion."%self.entity.name)
		friendlyMinions = self.entity.Game.minionsAlive(self.entity.ID)
		extractfrom(self.entity, friendlyMinions)
		if friendlyMinions != []:
			minion = np.random.choice(friendlyMinions)
			PRINT(self, "%s deals 1 damage to friendly minion %s"%(self.entity.name, minion.name))
			self.entity.dealsDamage(minion, 1)
			
	
class TempleBerserker(Minion):
	Class, race, name = "Neutral", "", "Temple Berserker"
	mana, attack, health = 2, 1, 2
	index = "Uldum~Neutral~Minion~2~1~2~None~Temple Berserker~Reborn"
	requireTarget, keyWord, description = False, "Reborn", "Reborn. Has +2 Attack while damaged"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.auras["Enrage"] = BuffAura_Dealer_Enrage(self, 2)
		self.triggers["StatChanges"] = [self.handleEnrage]
		self.activated = False
		
	def handleEnrage(self):
		self.auras["Enrage"].handleEnrage()
		
		
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
	poolIdentifier = "Basic and Classic Cards"
	@classmethod
	def generatePool(cls, Game):
		basicandClassicCards, basicandClassicNameObjs = [], {}
		basicandClassicClassCards = {"Neutral": [], "Demon Hunter": [], "Druid": [], "Mage": [], "Hunter": [], "Paladin": [], "Priest": [],
									"Rogue": [], "Shaman": [], "Warlock": [], "Warrior": []}
		classes = ["Basic and Classic %s Cards"%Class for Class in ClassesandNeutral]
		for key, value in Game.cardPool.items():
			if (key.startswith("Basic") or key.startswith("Classic")) and "~Uncollectible" not in key:
				basicandClassicCards.append(value)
				basicandClassicNameObjs[value.name] = value
				basicandClassicClassCards[key.split('~')[1]].append(value)
		return ["Basic and Classic Cards", "Basic and Classic Card Index"]+classes, [basicandClassicCards, basicandClassicNameObjs]+list(basicandClassicClassCards.values())
		
	def effectCanTrigger(self):
		self.effectViable = self.Game.Hand_Deck.noDuplicatesinDeck(self.ID)
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		PRINT(self, "Zephrys the Great tests if the deck has duplicates.")
		if self.Game.Hand_Deck.noDuplicatesinDeck(self.ID):
			PRINT(self, "Zephrys the Great will give player a wish.")
			if self.ID == self.Game.turn and self.Game.Hand_Deck.handNotFull(self.ID):
				if "InvokedbyOthers" in comment:
					PRINT(self, "Zephrys the Great's battlecry adds a random Basic or Classic card to player's hand")
					card = np.random.choice(self.Game.RNGPools["Basic and Classic Cards"])
					self.Game.Hand_Deck.addCardtoHand(card, self.ID, "CreateUsingType")
				else:
					PRINT(self, "Zephrys the Great's battlecry lets player enter the name of a card they want")
					self.Game.DiscoverHandler.typeCardName(self)
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
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		PRINT(self, "Desert Hare 's battlecry summons two 1/1 Desert Hares.")
		pos = (self.position, "leftandRight") if self.onBoard else (-1, "totheRightEnd")
		self.Game.summonMinion([DesertHare(self.Game, self.ID) for i in range(2)], pos, self.ID)
		return None
		
		
class GenerousMummy(Minion):
	Class, race, name = "Neutral", "", "Generous Mummy"
	mana, attack, health = 3, 5, 4
	index = "Uldum~Neutral~Minion~3~5~4~None~Generous Mummy~Reborn"
	requireTarget, keyWord, description = False, "Reborn", "Reborn. Your opponent's cards cost (1) less"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.auras["Mana Aura"] = ManaAura_Dealer(self, self.manaAuraApplicable, changeby=-1, changeto=-1)
		
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
		classes, lists, neutralMinions= [], [], []
		for key, value in Game.NeutralMinions.items():
			if key.split('~')[3] == '4':
				neutralMinions.append(value)
		#职业为中立时，视为作为萨满打出此牌
		for Class in Classes:
			classes.append("4-Cost Cards as " + Class)
			fourCostCardsinClass = []
			for key, value in Game.ClassCards[Class].items():
				if key.split('~')[3] == '4':
					fourCostCardsinClass.append(value)
			lists.append(fourCostCardsinClass+neutralMinions)
			
		return classes, lists
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if self.Game.Hand_Deck.handNotFull(self.ID) and self.ID == self.Game.turn:
			key = "4-Cost Cards as "+classforDiscover(self)
			if "InvokedbyOthers" in comment:
				PRINT(self, "Golden Scarab's battlecry adds a random 4-cost card to player's hand")
				self.Game.Hand_Deck.addCardtoHand(np.random.choice(self.Game.RNGPools[key]), self.ID, "CreateUsingType")
			else:
				cards = np.random.choice(self.Game.RNGPools[key], 3, replace=False)
				self.Game.options = [card(self.Game, self.ID) for card in cards]
				PRINT(self, "Golden Scarab's battlecry lets player discover a 4-cost cards")
				self.Game.DiscoverHandler.startDiscover(self)
				
		return None
		
	def discoverDecided(self, option):
		PRINT(self, "4-cost card %s is put into player's hand."%option.name)
		self.Game.Hand_Deck.addCardtoHand(option, self.ID)
		self.Game.sendSignal("DiscoveredCardPutintoHand", self.ID, self, option, 0, "")
		
		
class HistoryBuff(Minion):
	Class, race, name = "Neutral", "", "History Buff"
	mana, attack, health = 3, 3, 4
	index = "Uldum~Neutral~Minion~3~3~4~None~History Buff"
	requireTarget, keyWord, description = False, "", "Whenever you play a minion, give a random minion in your hand +1/+1"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_HistoryBuff(self)]
		
class Trigger_HistoryBuff(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionPlayed"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject.ID == self.entity.ID and subject != self.entity
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self, "Player plays a minion and %s gives a random minion in hand +1/+1"%self.entity.name)
		minionsinHand = []
		for card in self.entity.Game.Hand_Deck.hands[self.entity.ID]:
			if card.cardType == "Minion":
				minionsinHand.append(card)
				
		if minionsinHand != []:
			np.random.choice(minionsinHand).buffDebuff(1, 1)
			
			
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
		PRINT(self, "Deathrattle: Add two 1/1 Scarabs with Taunt to your hand triggers.")
		self.entity.Game.Hand_Deck.addCardtoHand([Scarab_Uldum, Scarab_Uldum], self.entity.ID, "CreateUsingType")
		
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
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		PRINT(self, "Mischief Maker's battlecry swaps the top card of player's deck with the opponent's")
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
		classes, lists, spells = [], [], []
		for Class in Classes:
			ClassSpells = []
			for key, value in Game.ClassCards[Class].items():
				if "~Spell~" in key:
					ClassSpells.append(value)
					spells.append(value)
			classes.append(Class+" Spells")
			lists.append(ClassSpells)
		lists.append(spells)
		return classes + ["Spells"], lists
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if self.Game.Hand_Deck.handNotFull(self.ID) and self.ID == self.Game.turn:
			key = classforDiscover(self)+" Spells"
			if "InvokedbyOthers" in comment:
				PRINT(self, "Vulpera Scoundrel's battlecry adds a random spell to player's hand")
				if np.random.randint(4) == 3:
					self.Game.Hand_Deck.addCardtoHand(np.random.choice(self.Game.RNGPools["Spells"]), self.ID, "CreateUsingType")
				else:
					self.Game.Hand_Deck.addCardtoHand(np.random.choice(self.Game.RNGPools[key]), self.ID, "CreateUsingType")
			else:
				spells = np.random.choice(self.Game.RNGPools[key], 3, replace=False)
				self.Game.options = [spell(self.Game, self.ID) for spell in spells]
				self.Game.options.append(MysteryChoice())
				PRINT(self, "Vulpera Scoundrel's battlecry lets player Discover a spell or a Mystery Choice")
				self.Game.DiscoverHandler.startDiscover(self)
				
		return None
		
	def discoverDecided(self, option):
		if option.name != "Mystery Choice!":
			PRINT(self, "Spell %s is put into player's hand"%option.name)
			self.Game.Hand_Deck.addCardtoHand(option, self.ID)
			self.Game.sendSignal("DiscoveredCardPutintoHand", self.ID, self, option, 0, "")
		else:
			self.Game.Hand_Deck.addCardtoHand(np.random.choice(self.Game.RNGPools["Spells"]), self.ID, "CreateUsingType")
			
class MysteryChoice:
	Class, name = "Neutral", "Mystery Choice!"
	requireTarget, mana = False, 0
	index = "Uldum~Neutral~Spell~0~Mystery Choice!~Uncollectible"
	description = "Add a random spell to your hand"
	
	
"""Mana 4 cards"""
class BoneWraith(Minion):
	Class, race, name = "Neutral", "", "Bone Wraith"
	mana, attack, health = 4, 2, 5
	index = "Uldum~Neutral~Minion~4~2~5~None~Bone Wraith~Reborn"
	requireTarget, keyWord, description = False, "Reborn", "Reborn"
	
	
class BodyWrapper(Minion):
	Class, race, name = "Neutral", "", "Body Wrapper"
	mana, attack, health = 4, 4, 4
	index = "Uldum~Neutral~Minion~4~4~4~None~Body Wrapper~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Discover a friendly minion that died this game. Shuffle it into your deck"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		minionsDiedThisGame = self.Game.CounterHandler.minionsDiedThisGame[self.ID]
		if minionsDiedThisGame != [] and self.ID == self.Game.turn:
			if len(minionsDiedThisGame) == 1:
				PRINT(self, "Body Wrapper's battlecry shuffles the only friendly minion %s that died this game into player's deck")
				minion = self.Game.cardPool[minionsDiedThisGame[0]](self.Game, self.ID)
				self.Game.Hand_Deck.shuffleCardintoDeck(minion, self.ID)
			else:
				if "InvokedbyOthers" in comment:
					PRINT(self, "Body Wrapper's battlecry shuffles a random friendly minion that died this game into player's deck")
					minion = self.Game.cardPool[np.random.choice(minionsDiedThisGame)](self.Game, self.ID)
					self.Game.Hand_Deck.shuffleCardintoDeck(minion, self.ID)
				else:
					num = min(len(minionsDiedThisGame), 3)
					indices = np.random.choice(minionsDiedThisGame, num, replace=False)
					self.Game.options = [self.Game.cardPool[index](self.Game, self.ID) for index in indices]
					PRINT(self, "Body Wrapper's battlecry lets player Discover a friendly minion that died this game and shuffle into deck")
					self.Game.DiscoverHandler.startDiscover(self)
					
		return None
		
	def discoverDecided(self, option):
		PRINT(self, "Minion %s is shuffled into player's deck."%option.name)
		self.Game.Hand_Deck.shuffleCardintoDeck(option, self.ID)
		
		
class ConjuredMirage(Minion):
	Class, race, name = "Neutral", "", "Conjured Mirage"
	mana, attack, health = 4, 3, 10
	index = "Uldum~Neutral~Minion~4~3~10~None~Conjured Mirage~Taunt"
	requireTarget, keyWord, description = False, "Taunt", "Taunt. At the start of your turn, shuffle this minion into your deck"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_ConjuredMirage(self)]
		
class Trigger_ConjuredMirage(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["TurnStarts"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self, "At the start of turn, %s shuffles itself into player's deck"%self.entity.name)
		#随从在可以触发回合开始扳机的时机一定是不结算其亡语的。可以安全地注销其死亡扳机
		self.entity.Game.returnMiniontoDeck(self.entity, self.entity.ID, self.entity.ID, keepDeathrattlesRegistered=False)
		
		
class SunstruckHenchman(Minion):
	Class, race, name = "Neutral", "", "Sunstruck Henchman"
	mana, attack, health = 4, 6, 5
	index = "Uldum~Neutral~Minion~4~6~5~None~Sunstruck Henchman"
	requireTarget, keyWord, description = False, "", "At the start of your turn, this has a 50% chance to fall asleep"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_SunstruckHenchman(self)]
		
class Trigger_SunstruckHenchman(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["TurnStarts", "TurnEnds"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		if signal == "TurnStarts":
			PRINT(self, "At the start of turn, %s has 50|50 chance to fall asleep"%self.entity.name)
			if np.random.randint(2) == 1:
				PRINT(self, "%s falls asleep"%self.entity.Game)
				self.entity.marks["Can't Attack"] += 1
			else:
				PRINT(self, "%s stays awake"%self.entity.Game)
		else: #signal == "TurnEnds"
			if self.entity.marks["Can't Attack"] > 0:
				self.entity.marks["Can't Attack"] -= 1
				
"""Mana 5 cards"""
class FacelessLurker(Minion):
	Class, race, name = "Neutral", "", "Faceless Lurker"
	mana, attack, health = 5, 3, 3
	index = "Uldum~Neutral~Minion~5~3~3~None~Faceless Lurker~Taunt~Battlecry"
	requireTarget, keyWord, description = False, "Taunt", "Taunt. Battlecry: Double this minion's Health"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		PRINT(self, "Faceless Lurker's battlecry doubles minion's Health")
		self.statReset(False, self.health * 2)
		return None
		
		
class DesertObelisk(Minion):
	Class, race, name = "Neutral", "", "Desert Obelisk"
	mana, attack, health = 5, 0, 5
	index = "Uldum~Neutral~Minion~5~0~5~None~Desert Obelisk"
	requireTarget, keyWord, description = False, "", "If your control 3 of these at the end of your turn, deal 5 damage to a random enemy"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_DesertObelisk(self)]
		
class Trigger_DesertObelisk(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["TurnEnds"])
		
	def checkDesertObelisk(self):
		numObelisks = 0
		for minion in self.entity.Game.minionsonBoard(self.entity.ID):
			if minion.name == "Desert Obelisk":
				numObelisks += 1
				
		return numObelisks > 2
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and ID == self.entity.ID and self.checkDesertObelisk()
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self, "At the end of turn, as the player controls 3 or more Desert Obelisk, %s deals 5 damage to a random enemy."%self.entity.name)
		targets = self.entity.Game.livingObjtoTakeRandomDamage(3-self.entity.ID)
		if targets != []:
			target = np.random.choice(targets)
			PRINT(self, "%s deals 5 damage to %s"%(self.entity.name, target.name))
			self.entity.dealsDamage(target, 5)
			
			
class MortuaryMachine(Minion):
	Class, race, name = "Neutral", "Mech", "Mortuary Machine"
	mana, attack, health = 5, 8, 8
	index = "Uldum~Neutral~Minion~5~8~8~Mech~Mortuary Machine"
	requireTarget, keyWord, description = False, "", "After your opponent plays a minion, give it Reborn"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_MortuaryMachine(self)]
		
class Trigger_MortuaryMachine(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionBeenPlayed"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject.ID != self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self, "After the opponent plays minion %s, %s gives it Reborn"%(subject.name, self.entity.name))
		subject.getsKeyword("Reborn")
		
		
class PhalanxCommander(Minion):
	Class, race, name = "Neutral", "", "Phalanx Commander"
	mana, attack, health = 5, 4, 5
	index = "Uldum~Neutral~Minion~5~4~5~None~Phalanx Commander"
	requireTarget, keyWord, description = False, "", "Your Taunt minions have +2 Attack"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.auras["Buff Aura"] = BuffAura_PhalanxCommander(self)
		
#Refer to Warsong Commander's aura
class BuffAura_PhalanxCommander:
	def __init__(self, minion):
		self.minion = minion
		self.auraAffected = [] #A list of (minion, aura_Receiver)
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		if self.minion.onBoard and subject.ID == self.minion.ID:
			if signal == "MinionAppears" and subject.keyWords["Charge"] > 0:
				return True
			if signal == "MinionTauntKeywordChange":
				return True
		return False
		
	def trigger(self, signal, ID, subject, target, number, comment, choice=0):
		if self.canTrigger(signal, ID, subject, target, number, comment):
			self.effect(signal, ID, subject, target, number, comment)
			
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.applies(signal, subject)
		
	def applies(self, signal, subject):
		if signal == "MinionAppears":
			if subject.keyWords["Taunt"] > 0:
				PRINT(self, "Minion %s gains the +2 Attack aura from Phalanx Commander"%subject.name)
				aura_Receiver = BuffAura_Receiver(subject, self, 2, 0)
				aura_Receiver.effectStart()
		else: #signal == "MinionTauntKeywordChange"
			if subject.keyWords["Taunt"] > 0:
				notAffectedPreviously = True
				for receiver, aura_Receiver in fixedList(self.auraAffected):
					if subject == receiver:
						notAffectedPreviously = False
						break
				if notAffectedPreviously:
					aura_Receiver = BuffAura_Receiver(subject, self, 1, 0)
					aura_Receiver.effectStart()
			elif subject.keyWords["Taunt"] < 1:
				for receiver, aura_Receiver in fixedList(self.auraAffected):
					if subject == receiver:
						aura_Receiver.effectClear()
						break
						
	def auraAppears(self):
		for minion in self.minion.Game.minionsonBoard(self.minion.ID):
			self.applies("MinionAppears", minion) #The signal here is a placeholder and directs the function to first time aura applicatioin
			
		self.minion.Game.triggersonBoard[self.minion.ID].append((self, "MinionAppears"))
		self.minion.Game.triggersonBoard[self.minion.ID].append((self, "MinionTauntKeywordChange"))
		
	#When the aura object is no longer referenced, it vanishes automatically.
	def auraDisappears(self):
		for minion, aura_Receiver in fixedList(self.auraAffected):
			aura_Receiver.effectClear()
			
		self.auraAffected = []
		extractfrom((self, "MinionAppears"), self.minion.Game.triggersonBoard[self.minion.ID])
		extractfrom((self, "MinionTauntKeywordChange"), self.minion.Game.triggersonBoard[self.minion.ID])
		
	def selfCopy(self, recipientMinion): #The recipientMinion is the minion that deals the Aura.
		#func that checks if subject is applicable will be the new copy's function
		return type(self)(recipientMinion)
		
		
class WastelandAssassin(Minion):
	Class, race, name = "Neutral", "", "Wasteland Assassin"
	mana, attack, health = 5, 4, 2
	index = "Uldum~Neutral~Minion~5~4~2~None~Wasteland Assassin~Stealth~Reborn"
	requireTarget, keyWord, description = False, "Stealth,Reborn", "Stealth, Reborn"
	
"""Mana 6 cards"""
class BlatantDecoy(Minion):
	Class, race, name = "Neutral", "Mech", "Blatant Decoy"
	mana, attack, health = 6, 5, 5
	index = "Uldum~Neutral~Minion~6~5~5~Mech~Blatant Decoy~Deathrattle"
	requireTarget, keyWord, description = False, "", "Deathrattle: Each player summons the lowest Cost minion from their hand"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [BothPlayersSummonLowestCostMinionfromHand(self)]
		
class BothPlayersSummonLowestCostMinionfromHand(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self, "Deathrattle: Each player summons the lowest Cost minion from their hand")
		for ID in range(1, 3):
			minionswithLowestCost, highestCost = [], np.inf
			for card in self.entity.Game.Hand_Deck.hands[ID]:
				if card.cardType == "Minion":
					if card.mana < highestCost:
						minionswithLowestCost, highestCost = [card], card.mana
					elif card.mana == highestCost:
						minionswithLowestCost.append(card)
						
			if minionswithLowestCost != [] and self.entity.Game.spaceonBoard(ID) > 0:
				pos = self.entity.position + 1 if ID == self.entity.ID else -1
				self.entity.Game.summonfromHand(np.random.choice(minionswithLowestCost), self.entity.position+1, ID)
				
				
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
		PRINT(self, "Deathrattle: Restore %d health to your hero triggers."%heal)
		self.entity.restoresHealth(self.entity.Game.heroes[self.entity.ID], heal)	
		
		
"""Mana 7 cards"""
class Siamat(Minion):
	Class, race, name = "Neutral", "Elemental", "Siamat"
	mana, attack, health = 7, 6, 6
	index = "Uldum~Neutral~Minion~7~6~6~Elemental~Siamat~Battlecry~Legendary"
	requireTarget, keyWord, description = False, "", "Battlecry: Gain 2 of Rush, Taunt, Divine Shield, or Windfury (your choice)"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.choices = []
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if self.ID == self.Game.turn:
			self.choices = [SiamatsHeart(), SiamatsShield(), SiamatsSpeed(), SiamatsWind()]
			if "InvokedbyOthers" in comment:
				PRINT(self, "Siamat's battlecry gives minion 2 of Rush, Taunt, Divine Shield, or Windfury (randomly chosen)")
				keywords = np.random.choice(["Rush", "Taunt", "Divine Shield", "Windfury"], 2, replace=False)
				self.getsKeyword(keyWords[0])
				self.getsKeyword(keyWords[1])
			else:
				self.Game.options = self.choices
				PRINT(self, "Siamat's battlecry lets player 2 of Rush, Taunt, Divine Shield, and Windfury for Siamat")
				self.Game.DiscoverHandler.startDiscover(self)
				self.Game.options = self.choices
				self.Game.DiscoverHandler.startDiscover(self)
				
		return None
		
	def discoverDecided(self, option):
		PRINT(self, "Siamat gets %s"%option.keyWord)
		self.getsKeyword(option.keyWord)
		extractfrom(option, self.choices)
		
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
		self.triggersonBoard = [Trigger_WrappedGolem(self)]
		
class Trigger_WrappedGolem(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["TurnEnds"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self, "At the end of turn, %s summons a 1/1 Scarab with Taunt"%self.entity.name)
		self.entity.Game.summonMinion(Scarab_Uldum(self.entity.Game, self.entity.ID), self.entity.position+1, self.entity.ID)
		
		
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
		PRINT(self, "Deathrattle: Draw 8 cards triggers")
		for i in range(8):
			self.entity.Game.Hand_Deck.drawCard(self.entity.ID)
			
			
class PitCrocolisk(Minion):
	Class, race, name = "Neutral", "Beast", "Pit Crocolisk"
	mana, attack, health = 8, 5, 6
	index = "Uldum~Neutral~Minion~8~5~6~Beast~Pit Crocolisk~Battlecry"
	requireTarget, keyWord, description = True, "", "Battlecry: Deal 5 damage"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if target != None:
			PRINT(self, "Pit Crocolisk's battlecry deals 5 damage to %s"%target.name)
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
		PRINT(self, "Deathrattle: Give all minions in your hand +3/+3 triggers")
		for card in self.entity.Game.Hand_Deck.hands[self.entity.ID]:
			if card.cardType == "Minion":
				card.buffDebuff(3, 3)
				
"""Mana 10 cards"""
class ColossusoftheMoon(Minion):
	Class, race, name = "Neutral", "", "Colossus of the Moon"
	mana, attack, health = 10, 10, 10
	index = "Uldum~Neutral~Minion~10~10~10~None~Colossus of the Moon~Devine Shield~Reborn~Legendary"
	requireTarget, keyWord, description = False, "Divine Shield,Reborn", "Divine Shield, Reborn"
	
	
class KingPhaoris(Minion):
	Class, race, name = "Neutral", "", "King Phaoris"
	mana, attack, health = 10, 5, 5
	index = "Uldum~Neutral~Minion~10~5~5~None~King Phaoris~Battlecry~Legendary"
	requireTarget, keyWord, description = False, "", "Battlecry: For each spell in your hand, summon a minion of the same Cost"
	poolIdentifier = "1-Cost Minions to Summon"
	@classmethod
	def generatePool(cls, Game):
		costs, lists = [], []
		for cost in Game.MinionsofCost.keys():
			costs.append("%d-Cost Minions to Summon"%cost)
			lists.append(list(Game.MinionsofCost[cost].values()))
		return costs, lists
	#不知道如果手中法术的法力值没有对应随从时会如何
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		PRINT(self, "King Phaoris's battlecry summons a random minion with Cost equal to each spell in player's hand")
		manasofSpellsinHand = []
		for card in self.Game.Hand_Deck.hands[self.ID]:
			if card.cardType == "Spell":
				cost = card.mana
				while True:
					if cost not in self.Game.MinionsofCost.keys():
						cost -= 1
					else:
						break
				manasofSpellsinHand.append(cost)
				
		if manasofSpellsinHand != []:
			minions = []
			for cost in manasofSpellsinHand:
				minions.append(np.random.choice(self.Game.RNGPools["%d-Cost Minions to Summon"%cost])(self.Game, self.ID))
			self.Game.summonMinion(minions, (self.position+1, "totheRight"), self.ID)
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
		self.triggersonBoard = [Trigger_UntappedPotential(self)]
		
class Trigger_UntappedPotential(QuestTrigger):
	def __init__(self, entity):
		self.blank_init(entity, ["TurnEnds"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		if self.entity.Game.ManaHandler.manas[self.entity.ID] > 0:
			self.entity.progress += 1
			PRINT(self, "Player ends turn with unspent mana. Quest Untapped Potential progresses by 1. Current progress: %d"%self.entity.progress)
			if self.entity.progress > 3:
				PRINT(self, "Player ends turn with unspent mana for the 4th time and gains Reward: Orissian Tear.")
				self.disconnect()
				extractfrom(self.entity, self.entity.Game.SecretHandler.mainQuests[self.entity.ID])
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
		PRINT(self, "Player's Choose One cards now have both effects combined")
		self.Game.playerStatus[self.ID]["Choose Both"] += 1
		
	def disappears(self):
		PRINT(self, "Player's Choose One cards no longer have both effects combined")
		if self.Game.playerStatus[self.ID]["Choose Both"] > 0:
			self.Game.playerStatus[self.ID]["Choose Both"] -= 1
			
			
class WorthyExpedition(Spell):
	Class, name = "Druid", "Worthy Expedition"
	requireTarget, mana = False, 1
	index = "Uldum~Druid~Spell~1~Worth Expedition"
	description = "Discover a Choose One card"
	poolIdentifier = "Choose One Cards"
	@classmethod
	def generatePool(cls, Game):
		chooseOneCards = []
		for key, value in Game.ClassCards["Druid"].items():
			if "~Choose One" in key:
				chooseOneCards.append(value)
		return "Choose One Cards", chooseOneCards
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if self.Game.Hand_Deck.handNotFull(self.ID):
			if "CastbyOthers" in comment:
				PRINT(self, "Worthy Expedition is cast and adds a random Choose One card to player's hand")
				self.Game.Hand_Deck.addCardtoHand(np.random.choice(self.Game.RNGPools["Choose One Cards"]), self.ID, "CreateUsingType")
			else:
				cards = np.random.choice(self.Game.RNGPools["Choose One Cards"], 3, replace=False)
				self.Game.options = [card(self.Game, self.ID) for card in cards]
				self.Game.DiscoverHandler.startDiscover(self)
				
		return None
		
	def discoverDecided(self, option):
		PRINT(self, "Choose One card %s is added to player's hand."%option.name)
		self.Game.Hand_Deck.addCardtoHand(option, self.ID)
		self.Game.sendSignal("DiscoveredCardPutintoHand", self.ID, self, option, 0, "")
		
		
class CrystalMerchant(Minion):
	Class, race, name = "Druid", "", "Crystal Merchant"
	mana, attack, health = 2, 1, 4
	index = "Uldum~Druid~Minion~2~1~4~None~Crystal Merchant"
	requireTarget, keyWord, description = False, "", "If you have any unspent Mana at the end of your turn, draw a card"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_CrystalMerchant(self)]
		
class Trigger_CrystalMerchant(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["TurnEnds"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		if self.entity.Game.ManaHandler.manas[self.entity.ID] > 0:
			PRINT(self, "Player ends turn with unspent Mana, and %s lets player draw a card"%self.entity.name)
			self.entity.Game.Hand_Deck.drawCard(self.entity.ID)
			
			
class BEEEES(Spell):
	Class, name = "Druid", "BEEES!"
	requireTarget, mana = True, 3
	index = "Uldum~Druid~Spell~3~BEEEES!"
	description = "Choose a minion. Summon four 1/1 Bees that attack it"
	def available(self):
		return self.selectableMinionExists() and self.Game.spaceonBoard(self.ID) > 0
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		#假设没有目标时也会生效，只是召唤的蜜蜂不会攻击
		PRINT(self, "BEEES! is cast and summons four 1/1 Bees to attack it")
		#不知道卡德加翻倍召唤出的随从是否会攻击那个随从，假设不会
		bees = [Bee_Uldum(self.Game, self.ID) for i in range(4)]
		self.Game.summonMinion(bees, (-1, "totheRightEnd"), self.ID)
		if target != None:
			for bee in bees:
				#召唤的蜜蜂需要在场上且存活，同时目标也需要在场且存活
				if bee.onBoard and bee.health > 0 and bee.dead == False and target.onBoard and target.health > 0 and target.dead == False:
					self.Game.battleRequest(bee, target, False, False)
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
	
	def effectCanTrigger(self):
		self.effectViable = self.Game.Hand_Deck.holdingSpellwith5CostorMore(self.ID)
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if self.Game.Hand_Deck.holdingSpellwith5CostorMore(self.ID):
			PRINT(self, "Garden Gnome's battlecry summons two 2/2 Treants")
			pos = (self.position, "leftandRight") if self.onBoard else (-1, "totheRightEnd")
			self.Game.summonMinion([Treant_Uldum(self.Game, self.ID) for i in range(2)], pos, self.ID)
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
		self.triggersinHand = [Trigger_AnubisathDefender(self)]
		
	def selfManaChange(self):
		if self.inHand:
			for index, mana in zip(self.Game.CounterHandler.cardsPlayedThisTurn[self.ID]["Indices"], self.Game.CounterHandler.cardsPlayedThisTurn[self.ID]["ManasPaid"]):
				if "~Spell~" in index and mana > 4:
					self.mana = 0
					break
					
					
class Trigger_AnubisathDefender(TriggerinHand):
	def __init__(self, entity):
		self.blank_init(entity, ["SpellBeenPlayed", "TurnStarts", "TurnEnds"]) #不需要预检测
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		if self.entity.inHand:
			if signal == "TurnStarts" or signal == "TurnEnds":
				return True
			else:
				return number > 4 and subject.ID == self.entity.ID
		return False
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self, "Player plays or turn starts/ends, Anubisath Defender resets its cost.")
		self.entity.Game.ManaHandler.calcMana_Single(self.entity)
		
		
class ElisetheEnlightened(Minion):
	Class, race, name = "Druid", "", "Elise the Enlightened"
	mana, attack, health = 5, 5, 5
	index = "Uldum~Druid~Minion~5~5~5~None~Elise the Enlightened~Battlecry~Legendary"
	requireTarget, keyWord, description = False, "", "Battlecry: If your deck has no duplicates, duplicate your hand"
	
	def effectCanTrigger(self):
		self.effectViable = self.Game.Hand_Deck.noDuplicatesinDeck(self.ID)
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if self.Game.Hand_Deck.noDuplicatesinDeck(self.ID):
			PRINT(self, "Elise the Enlightened's battlecry duplicates player's hand")
			for card in fixedList(self.Game.Hand_Deck.hands[self.ID]):
				self.Game.Hand_Deck.addCardtoHand(card.selfCopy(self.ID), self.ID)
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
		self.options = [FocusedBurst_Option(), DivideandConquer_Option(self)]
		
	#对于抉择随从而言，应以与战吼类似的方式处理，打出时抉择可以保持到最终结算。但是打出时，如果因为鹿盔和发掘潜力而没有选择抉择，视为到对方场上之后仍然可以而没有如果没有
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if choice == "ChooseBoth" or choice == 0:
			PRINT(self, "Oasis Surger gains +2/+2.")
			self.buffDebuff(2, 2)
		if choice == "ChooseBoth" or choice == 1:
			PRINT(self, "Oasis Surger summons a copy of itself")
			self.Game.summonMinion(self.selfCopy(self.ID), self.position+1, self.ID)
		return None
		
class FocusedBurst_Option:
	def __init__(self):
		self.name = "Focused Burst"
		self.description = "Gain +2/+2"
		
	def available(self):
		return True
		
	def selfCopy(self, recipient):
		return type(self)()
		
class DivideandConquer_Option:
	def __init__(self, minion):
		self.minion = minion
		self.name = "Divide and Conquer"
		self.description = "Summon a copy"
		
	def available(self):
		return self.minion.Game.spaceonBoard(self.minion.ID) > 0
		
	def selfCopy(self, recipient):
		return type(self)(recipient)
		
		
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
		return choice == "ChooseBoth" or choice == 1
		
	def available(self):
		#当场上有全选光环时，变成了一个指向性法术，必须要有一个目标可以施放。
		if self.Game.playerStatus[self.ID]["Choose Both"] > 0:
			return self.selectableCharacterExists(1)
		else:
			return self.Game.spaceonBoard(self.ID) > 0 or self.selectableCharacterExists(1)
			
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if choice == "ChooseBoth" or choice == 1:
			if target != None:
				heal = 12 * (2 ** self.countHealDouble())
				PRINT(self, "Hidden Oasis restore %d Health to %s"%(heal, target.name))
				self.restoresHealth(target, heal)
		if choice == "ChooseBoth" or choice == 0:
			PRINT(self, "Hidden Oasis summons a 6/6 Vir'naal Ancient with Taunt")
			self.Game.summonMinion(VirnaalAncient(self.Game, self.ID), -1, self.ID)
		return target
		
class BefriendtheAncient_Option:
	def __init__(self, spell):
		self.spell = spell
		self.name = "Befriend the Ancient"
		self.description = "6/6 with Taunt"
		self.index = "Uldum~Druid~Spell~6~Befriend the Ancient~Uncollectible"
		
	def available(self):
		return self.spell.Game.spaceonBoard(self.spell.ID) > 0
		
	def selfCopy(self, recipient):
		return type(self)(recipient)
		
class DrinktheWater_Option:
	def __init__(self, spell):
		self.spell = spell
		self.name = "Drink the Water"
		self.description = "Heal 12"
		self.index = "Uldum~Druid~Spell~6~Drink the Water~Uncollectible"
		
	def available(self):
		return self.spell.selectableCharacterExists(1)
		
	def selfCopy(self, recipient):
		return type(self)(recipient)
		
class BefriendtheAncient(Spell):
	Class, name = "Druid", "Befriend the Ancient"
	requireTarget, mana = False, 6
	index = "Uldum~Druid~Spell~6~Befriend the Ancient~Uncollectible"
	description = "Summon a 6/6 Ancient with Taunt"
	def available(self):
		return self.Game.spaceonBoard(self.ID)
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		PRINT(self, "Befriend the Ancient is cast and summons a 6/6 Vir'naal Ancient with Taunt")
		self.Game.summonMinion(VirnaalAncient(self.Game, self.ID), -1, self.ID)
		return None
		
class DrinktheWater(Spell):
	Class, name = "Druid", "Drink the Water"
	requireTarget, mana = True, 6
	index = "Uldum~Druid~Spell~6~Drink the Water~Uncollectible"
	description = "Restore 12 Health"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if target != None:
			heal = 12 * (2 ** self.countHealDouble())
			PRINT(self, "Drink the Water is cast and restores %d Health to %s"%(heal, target.name))
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
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		heal = 5 * (2 ** self.countHealDouble())
		PRINT(self, "Overflow is cast and restores %d Health to all characters. The player draws 5 cards"%heal)
		targets = [self.Game.heroes[self.ID], self.Game.heroes[3-self.ID]] + self.Game.minionsonBoard(self.ID) + self.Game.minionsonBoard(3-self.ID)
		self.restoresAOE(targets, [heal for obj in targets])
		for i in range(5):
			self.Game.Hand_Deck.drawCard(self.ID)
		return None
		
"""Hunter cards"""
class UnsealtheVault(Quest):
	Class, name = "Hunter", "Unseal the Vault"
	requireTarget, mana = False, 1
	index = "Uldum~Hunter~Spell~1~Unseal the Vault~~Quest~Legendary"
	description = "Quest: Summon 20 minions. Reward: Ramkahen Roar"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_UnsealtheVault(self)]
		
class Trigger_UnsealtheVault(QuestTrigger):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionBeenSummoned"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return subject.ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.progress += 1
		PRINT(self, "After player summons minion %s, Quest Unseal the Vault progresses by 1. Current progress: %d"%(subject.name, self.entity.progress))
		if self.entity.progress > 19:
			PRINT(self, "Player summons the 20th minion and gains Reward: Ramkahen Roar.")
			self.disconnect()
			extractfrom(self.entity, self.entity.Game.SecretHandler.mainQuests[self.entity.ID])
			RamkahenRoar(self.entity.Game, self.entity.ID).replaceHeroPower()
			
class RamkahenRoar(HeroPower):
	mana, name, requireTarget = 2, "Ramkahen Roar", False
	index = "Hunter~Hero Power~2~Ramkahen Roar"
	description = "Give your minions +2 Attack"
	def effect(self, target=None, choice=0):
		PRINT(self, "Hero Power Ramkahen Roar gives all friendly minions +2 Attack")
		for minion in fixedList(self.Game.minionsonBoard(self.ID)):
			minion.buffDebuff(2, 0)
		return 0
		
		
class PressurePlate(Secret):
	Class, name = "Hunter", "Pressure Plate"
	requireTarget, mana = False, 2
	index = "Uldum~Hunter~Spell~2~Pressure Plate~~Secret"
	description = "After your opponent casts a spell, destroy a random enemy minion"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_PressurePlate(self)]
		
class Trigger_PressurePlate(SecretTrigger):
	def __init__(self, entity):
		self.blank_init(entity, ["SpellBeenPlayed"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.ID != self.entity.Game.turn and subject.ID != self.entity.ID and self.entity.Game.minionsAlive(3-self.entity.ID) != []
			
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		minions = self.entity.Game.minionsAlive(3-self.entity.ID)
		if minions != []:
			minion = np.random.choice(minions)
			PRINT(self, "After the opponent casts a spell, Secret Pressure Plate is triggered and destroys random enemy minion %s"%minion.name)
			self.entity.Game.destroyMinion(minion)
			
			
class DesertSpear(Weapon):
	Class, name, description = "Hunter", "Desert Spear", "After your hero Attacks, summon a 1/1 Locust with Rush"
	mana, attack, durability = 3, 1, 3
	index = "Uldum~Hunter~Weapon~3~1~3~Desert Spear"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_DesertSpear(self)]
		
class Trigger_DesertSpear(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["HeroAttackedMinion", "HeroAttackedHero"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		#The target can't be dying to trigger this
		return subject == self.entity.Game.heroes[self.entity.ID] and self.entity.onBoard
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self, "After hero attacks, weapon %s summons a 1/1 Locust with Rush"%self.entity.name)
		self.entity.Game.summonMinion(Locust(self.entity.Game, self.entity.ID), -1, self.entity.ID)
		
		
class HuntersPack(Spell):
	Class, name = "Hunter", "Hunter's Pack"
	requireTarget, mana = False, 3
	index = "Uldum~Hunter~Spell~3~Hunter's Pack"
	description = "Add a random Hunter Beast, Secret, and Weapon to your hand"
	poolIdentifier = "Hunter Beasts"
	@classmethod
	def generatePool(cls, Game):
		hunterBeasts, hunterSecrets, hunterWeapons = [], [], []
		for key, value in Game.ClassCards["Hunter"].items():
			if "~Beast~" in key:
				hunterBeasts.append(value)
			elif "~~Secret" in key:
				hunterSecrets.append(value)
			elif "~Weapon~" in key:
				hunterWeapons.append(value)
		return ["Hunter Beasts", "Hunter Secrets", "Hunter Weapons"], [hunterBeasts, hunterSecrets, hunterWeapons]
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		PRINT(self, "Hunter's Pack is cast and adds a random Hunter Beast, Secret, and Weapon to player's hand")
		if self.Game.Hand_Deck.handNotFull(self.ID):
			self.Game.Hand_Deck.addCardtoHand(np.random.choice(self.Game.RNGPools["Hunter Beasts"]), self.ID, "CreateUsingType")
		if self.Game.Hand_Deck.handNotFull(self.ID):
			self.Game.Hand_Deck.addCardtoHand(np.random.choice(self.Game.RNGPools["Hunter Secrets"]), self.ID, "CreateUsingType")
		if self.Game.Hand_Deck.handNotFull(self.ID):
			self.Game.Hand_Deck.addCardtoHand(np.random.choice(self.Game.RNGPools["Hunter Weapons"]), self.ID, "CreateUsingType")
		return None
		
		
class HyenaAlpha(Minion):
	Class, race, name = "Hunter", "Beast", "Hyena Alpha"
	mana, attack, health = 4, 2, 3
	index = "Uldum~Hunter~Minion~4~2~3~Beast~Hyena Alpha~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: If you control a Secret, summon two 2/2 Hyenas"
	
	def effectCanTrigger(self):
		self.effectViable = self.Game.SecretHandler.secrets[self.ID] != []
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if self.Game.SecretHandler.secrets[self.ID] != []:
			PRINT(self, "Hyena Alpha's battlecry summons two 2/2 Hyenas")
			pos = (self.position, "leftandRight") if self.onBoard else (-1, "totheRightEnd")
			self.Game.summonMinion([Hyena_Uldum(self.Game, self.ID) for i in range(2)], pos, self.ID)
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
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		PRINT(self, "Ramkahen Wildtamer's battlecry copies a Beast in player's hand")
		beastsinHand = []
		for card in self.Game.Hand_Deck.hands[self.ID]:
			if card.cardType == "Minion" and "Beast" in card.race:
				beastsinHand.append(card)
				
		if beastsinHand != [] and self.Game.Hand_Deck.handNotFull(self.ID):
			beast = np.random.choice(beastsinHand).selfCopy(self.ID)
			self.Game.Hand_Deck.addCardtoHand(beast, self.ID)
		return None
		
		
class SwarmofLocusts(Spell):
	Class, name = "Hunter", "Swarm of Locusts"
	requireTarget, mana = False, 6
	index = "Uldum~Hunter~Spell~6~Swarm of Locusts"
	description = "Summon seven 1/1 Locusts with Rush"
	def available(self):
		return self.Game.spaceonBoard(self.ID) > 0
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		PRINT(self, "Swarm of Locusts is cast and summons seven 1/1 Locusts with Rush")
		self.Game.summonMinion([Locust(self.Game, self.ID) for i in range(7)], (-1, "totheRightEnd"), self.ID)
		return None
		
		
class ScarletWebweaver(Minion):
	Class, race, name = "Hunter", "Beast", "Scarlet Webweaver"
	mana, attack, health = 6, 5, 5
	index = "Uldum~Hunter~Minion~6~5~5~Beast~Scarlet Webweaver~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Reduce the Cost of a random Beast in your hand by (5)"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		PRINT(self, "Scarlet Webweaver's battlecry reduces the Cost of a random Beast in player's hand by (5)")
		beastsinHand = []
		for card in self.Game.Hand_Deck.hands[self.ID]:
			if card.cardType == "Minion" and "Beast" in card.race:
				beastsinHand.append(card)
				
		if beastsinHand != []:
			beast = np.random.choice(beastsinHand)
			ManaModification(beast, changeby=-5, changeto=-1).applies()
			PRINT(self, "Scarlet Webweaver's battlecry reduces the Cost of %s by (5)"%beast.name)
			self.Game.ManaHandler.calcMana_Single(beast)
		return None
		
		
class WildBloodstinger(Minion):
	Class, race, name = "Hunter", "Beast", "Wild Bloodstinger"
	mana, attack, health = 6, 6, 9
	index = "Uldum~Hunter~Minion~6~6~9~Beast~Wild Bloodstinger~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Summon a minion from your opponent's hand. Attack it"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		PRINT(self, "Wild Bloodstinger's battlecry summons a minion from opponent's hand. Then it attacks it.")
		minionsinHand = []
		for card in self.Game.Hand_Deck.hands[3-self.ID]:
			if card.cardType == "Minion":
				minionsinHand.append(card)
				
		minion = None
		if minionsinHand != [] and self.Game.spaceonBoard(3-self.ID):
			minion = np.random.choice(minionsinHand)
			self.Game.summonMinion(minion, -1, self.ID)
		if minion != None and self.onBoard and self.health > 0 and self.dead == False:
			PRINT(self, "Wild Bloodstinger's summons %s from opponent's hand and attacks it"%minion.name)
			self.Game.battleRequest(self, minion, False, False)
		return None
		
		
class DinotamerBrann(Minion):
	Class, race, name = "Hunter", "", "Dinotamer Brann"
	mana, attack, health = 7, 2, 4
	index = "Uldum~Hunter~Minion~7~2~4~None~Dinotamer Brann~Battlecry~Legendary"
	requireTarget, keyWord, description = False, "", "Battlecry: If your deck has no duplicates, summon King Krush"
	
	def effectCanTrigger(self):
		self.effectViable = self.Game.Hand_Deck.noDuplicatesinDeck(self.ID)
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if self.Game.Hand_Deck.noDuplicatesinDeck(self.ID):
			PRINT(self, "Dinotamer Brann's battlecry summons King Krush")
			self.Game.summonMinion(KingKrush_Uldum(self.Game, self.ID), self.position+1, self.ID)
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
		mageSpells = []
		for key, value in Game.ClassCards["Mage"].items():
			if "~Spell~" in key:
				mageSpells.append(value)
		return "Mage Spells", mageSpells
		
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_RaidtheSkyTemple(self)]
		
class Trigger_RaidtheSkyTemple(QuestTrigger):
	def __init__(self, entity):
		self.blank_init(entity, ["SpellPlayed"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return subject.ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.progress += 1
		PRINT(self, "Player plays spell and Quest Raid the Sky Temple progresses by 1. Current progress: %d"%self.entity.progress)
		if self.entity.progress > 9:
			PRINT(self, "Player plays the 10th spell and gains Reward: Ascendant Scroll.")
			self.disconnect()
			extractfrom(self.entity, self.entity.Game.SecretHandler.mainQuests[self.entity.ID])
			AscendantScroll(self.entity.Game, self.entity.ID).replaceHeroPower()
			
class AscendantScroll(HeroPower):
	mana, name, requireTarget = 2, "Ascendant Scroll", False
	index = "Mage~Hero Power~2~Ascendant Scroll"
	description = "Add a random Mage spell to your hand. It costs (2) less"
	def effect(self, target=None, choice=0):
		PRINT(self, "Hero Power Ascendant Scroll adds a random Mage spell to player's hand. It costs (2) less")
		if self.Game.Hand_Deck.handNotFull(self.ID):
			spell = np.random.choice(self.Game.RNGPools["Mage Spells"])(self.Game, self.ID)
			self.Game.Hand_Deck.addCardtoHand(spell, self.ID)
			ManaModification(spell, changeby=-2, changeto=-1).applies()
			self.Game.ManaHandler.calcMana_Single(spell)
		return 0
		
		
class AncientMysteries(Spell):
	Class, name = "Mage", "Ancient Mysteries"
	requireTarget, mana = False, 2
	index = "Uldum~Mage~Spell~2~Ancient Mysteries"
	description = "Draw a Secret from your deck. It costs (0)"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		PRINT(self, "Ancient Mysteries is cast and player draws a Secret from deck. It costs (0).")
		secretsinDeck = []
		for card in self.Game.Hand_Deck.decks[self.ID]:
			if card.cardType == "Spell" and "~~Secret" in card.index:
				secretsinDeck.append(card)
				
		if secretsinDeck != []:
			secret, mana = self.Game.Hand_Deck.drawCard(self.ID, np.random.choice(secretsinDeck))
			if secret != None:
				ManaModification(secret, changeby=0, changeto=0).applies()
		return None
		
		
class FlameWard(Secret):
	Class, name = "Mage", "Flame Ward"
	requireTarget, mana = False, 3
	index = "Uldum~Mage~Spell~3~Flame Ward~~Secret"
	description = "After a minion attacks your hero, deal 3 damage to all enemy minions"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_FlameWard(self)]
		
class Trigger_FlameWard(SecretTrigger):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionAttackedHero"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.ID != self.entity.Game.turn and target == self.entity.Game.heroes[self.entity.ID]
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		damage = (3 + self.entity.countSpellDamage()) * (2 ** self.entity.countDamageDouble())
		PRINT(self, "After a minion attacks player, Secret Flame Ward is triggered and deals %d damage to all enemy minions."%damage)
		targets = self.entity.Game.minionsonBoard(3-self.entity.ID)
		self.entity.dealsAOE(targets, [damage for minion in targets])
		
		
class CloudPrince(Minion):
	Class, race, name = "Mage", "Elemental", "Cloud Prince"
	mana, attack, health = 5, 4, 4
	index = "Uldum~Mage~Minion~5~4~4~Elemental~Cloud Prince~Battlecry"
	requireTarget, keyWord, description = True, "", "Battlecry: If you control a Secret, deal 6 damage"
	
	def returnTrue(self, choice=0):
		return self.Game.SecretHandler.secrets[self.ID] != []
		
	def effectCanTrigger(self):
		self.effectViable = self.Game.SecretHandler.secrets[self.ID] != []
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if target != None and self.Game.SecretHandler.secrets[self.ID] != []:
			PRINT(self, "Cloud Prince's battlecry deals 6 damage to %s"%target.name)
			self.dealsDamage(target, 6)
		return target
		
	
class ArcaneFlakmage(Minion):
	Class, race, name = "Mage", "", "Arcane Flakmage"
	mana, attack, health = 2, 3, 2
	index = "Uldum~Mage~Minion~2~3~2~None~Arcane Flakmage"
	requireTarget, keyWord, description = False, "", "After you play a Secret, deal 2 damage to all enemy minions"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_ArcaneFlakmage(self)]
		
class Trigger_ArcaneFlakmage(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["SpellBeenPlayed"])
		
	#Assume Secretkeeper and trigger while dying.
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject.ID == self.entity.ID and "~~Secret" in subject.index
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self, "Player plays a Secret and %s deals 2 damage to all enemy minions"%self.entity.name)
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
		mageMinions = []
		for key, value in Game.ClassCards["Mage"].items():
			if "~Minion~" in key:
				mageMinions.append(value)
		return "Mage Minions", mageMinions
		
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_DuneSculptor(self)]
		
class Trigger_DuneSculptor(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["SpellPlayed"])
		
	#Assume Secretkeeper and trigger while dying.
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject.ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self, "Player plays a spell and %s adds a random Mage minion to player's hand."%self.entity.name)
		self.entity.Game.Hand_Deck.addCardtoHand(np.random.choice(self.entity.Game.RNGPools["Mage Minions"]), self.entity.ID, "CreateUsingType")
		
		
class NagaSandWitch(Minion):
	Class, race, name = "Mage", "", "Naga Sand Witch"
	mana, attack, health = 5, 5, 5
	index = "Uldum~Mage~Minion~5~5~5~None~Naga Sand Witch~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Change the Cost of spells in your hand to (5)"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		PRINT(self, "Naga Sand Witch's battlecry changes the Cost of all spells in player's hand to (5)")
		spellsinHand = []
		for card in self.Game.Hand_Deck.hands[self.ID]:
			if card.cardType == "Spell":
				spellsinHand.append(card)
				
		for spell in fixedList(spellsinHand):
			ManaModification(spell, changeby=0, changeto=5).applies()
		self.Game.ManaHandler.calcMana_All()
		return None
		
		
class TortollanPilgrim(Minion):
	Class, race, name = "Mage", "", "Tortollan Pilgrim"
	mana, attack, health = 8, 5, 5
	index = "Uldum~Mage~Minion~8~5~5~None~Tortollan Pilgrim~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Discover a Copy of a spell in your deck and cast it with random targets"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if self.ID == self.Game.turn:
			spellsinDeck = []
			for card in self.Game.Hand_Deck.decks[self.ID]:
				if card.cardType == "Spell":
					spellsinDeck.append(card)
					
			if spellsinDeck != []:
				if len(spellsinDeck) == 1:
					Copy = spellsinDeck.selfCopy(self.ID)
					PRINT(self, "There is only one spell %s in player's deck. Tortollan Pilgrim casts a copy of it."%Copy.name)
					Copy.cast()
				else:
					if "InvokedbyOthers" in comment:
						Copy = np.random.choice(spellsinDeck).selfCopy(self.ID)
						PRINT(self, "Tortollan Pilgrim casts a copy of a random spell in player's deck: %s"%Copy.name)
						Copy.cast()
					else:
						num = min(3, len(spellsinDeck))
						Copies = np.random.choice(spellsinDeck, num, replace=False)
						self.Game.options = [Copy.selfCopy(self.ID) for Copy in Copies]
						PRINT(self, "Tortollan Pilgrim's battlecry lets player Discover a copy of a spell in player's deck and cast it")
						self.Game.DiscoverHandler.startDiscover(self)
						
		return None
		
	def discoverDecided(self, option):
		PRINT(self, "Copy of spell %s is cast"%option.name)
		option.cast()
		
		
class RenotheRelicologist(Minion):
	Class, race, name = "Mage", "", "Reno the Relicologist"
	mana, attack, health = 6, 4, 6
	index = "Uldum~Mage~Minion~6~4~6~None~Reno the Relicologist~Battlecry~Legendary"
	requireTarget, keyWord, description = False, "", "Battlecry: If your deck has no duplicates, deal 10 damage randomly split among all enemy minions"
	
	def effectCanTrigger(self):
		self.effectViable = self.Game.Hand_Deck.noDuplicatesinDeck(self.ID)
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if self.Game.Hand_Deck.noDuplicatesinDeck(self.ID):
			PRINT(self, "Reno the Relicologist's battlecry deals 10 damage randomly split among enemy minions")
			for i in range(10):
				enemyMinions = self.Game.minionsAlive(3-self.ID)
				if enemyMinions != []:
					minion = np.random.choice(enemyMinions)
					PRINT(self, "Reno the Relicologist's battlecry deals 1 damage to enemy minion %s"%minion.name)
					self.dealsDamage(minion, 1)
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
		for Class in Classes:
			for key, value in Game.ClassCards[Class].items():
				if "~Spell~" in key:
					spells.append(value)
		return "Spells", spells
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		PRINT(self, "Puzzle Box of Yogg-Saron casts 10 random spells (targets chosen randomly)")
		#这个信号仅用于触发风潮，星界密使等。它们对于一般法术而言等到法术结算完毕之后再失效。
		#但是对于谜之匣而言，只有谜之匣自己会触发两次，其引发的10张法术都不会生效两次和享受法术伤害加成。
		self.Game.sendSignal("SpellBeenCast", self.ID, self, None, 0, "", choice)
		for i in range(10):
			spell = np.random.choice(self.Game.RNGPools["Spells"])(self.Game, self.ID)
			PRINT(self, "*********Puzzle Box of Yogg-Saron is cast and casts random spell %s"%spell.name)
			spell.cast()
			self.Game.gathertheDead()
		return None
		
		
"""Paladin cards"""
class MakingMummies(Quest):
	Class, name = "Paladin", "Making Mummies"
	requireTarget, mana = False, 1
	index = "Uldum~Paladin~Spell~1~Making Mummies~~Quest~Legendary"
	description = "Quest: Play 5 Reborn minions. Reward: Emperor Wraps"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_MakingMummies(self)]
		
class Trigger_MakingMummies(QuestTrigger):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionBeenPlayed"]) #扳机是使用后扳机
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		#假设扳机的判定条件是打出的随从在检测时有复生就可以，如果在打出过程中获得复生，则依然算作任务进度
		return subject.ID == self.entity.ID and subject.keyWords["Reborn"] > 0
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.progress += 1
		PRINT(self, "Player plays Reborn minion %s and Quest Making Mummies progresses by 1. Current progress: %d"%(subject.name, self.entity.progress))
		if self.entity.progress > 4:
			PRINT(self, "Player plays the 5th spell and gains Reward: Emperor Wraps.")
			self.disconnect()
			extractfrom(self.entity, self.entity.Game.SecretHandler.mainQuests[self.entity.ID])
			EmperorWraps(self.entity.Game, self.entity.ID).replaceHeroPower()
			
class EmperorWraps(HeroPower):
	mana, name, requireTarget = 2, "Emperor Wraps", True
	index = "Paladin~Hero Power~2~Emperor Wraps"
	description = "Summon a 2/2 copy of a friendly minion"
	def available(self, choice=0):
		if self.heroPowerTimes >= self.heroPowerChances_base + self.heroPowerChances_extra:
			return False
		if self.Game.spaceonBoard(self.ID) < 1 or self.selectableFriendlyMinionExists() == False:
			return False
		return True
		
	def effect(self, target=None, choice=0):
		if target != None:
			PRINT(self, "Hero Power Emperor Wraps summons a copy of friendly minion %s"%target.name)
			self.Game.summonMinion(target.selfCopy(self.ID, 2, 2), -1, self.ID, "")
		return 0
		
		
class BrazenZealot(Minion):
	Class, race, name = "Paladin", "", "Brazen Zealot"
	mana, attack, health = 1, 2, 1
	index = "Uldum~Paladin~Minion~1~2~1~None~Brazen Zealot"
	requireTarget, keyWord, description = False, "", "Whenever you summon a minion, gain +1 Attack"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_BrazenZealot(self)]
		
class Trigger_BrazenZealot(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionSummoned"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject.ID == self.entity.ID and subject != self.entity
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self, "A friendly minion %s is summoned and %s gains +1 attack."%(subject.name, self.entity.name))
		self.entity.buffDebuff(1, 0)
		
		
class MicroMummy(Minion):
	Class, race, name = "Paladin", "Mech", "Micro Mummy"
	mana, attack, health = 2, 1, 2
	index = "Uldum~Paladin~Minion~2~1~2~Mech~Micro Mummy~Reborn"
	requireTarget, keyWord, description = False, "Reborn", "Reborn. At the end of your turn, give another random friendly minion +1 Attack"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_MicroMummy(self)]
		
class Trigger_MicroMummy(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["TurnEnds"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		targets = self.entity.Game.minionsonBoard(self.entity.ID)
		extractfrom(self.entity, targets)
		if targets != []:
			target = np.random.choice(targets)
			PRINT(self, "At the end of turn, %s gives friendly minion %s +1 attack"%(self.entity.name, target.name))
			target.buffDebuff(1, 0)
			
			
class SandwaspQueen(Minion):
	Class, race, name = "Paladin", "Beast", "Sandwasp Queen"
	mana, attack, health = 2, 3, 1
	index = "Uldum~Paladin~Minion~2~3~1~Beast~Sandwasp Queen~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Add two 2/1 Sandwasps to your hand"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		PRINT(self, "Sandwasp Queen's battlecry adds two 2/1 Sandwasps to player's hand")
		self.Game.Hand_Deck.addCardtoHand([Sandwasp, Sandwasp], self.ID, "CreateUsingType")
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
	
	def effectCanTrigger(self):
		self.effectViable = self.Game.Hand_Deck.noDuplicatesinDeck(self.ID)
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if self.Game.Hand_Deck.noDuplicatesinDeck(self.ID):
			heroPowerPool = copy.deepcopy(UpgradedHeroPowers)
			currentHeroPower = type(self.Game.heroPowers[self.ID])
			extractfrom(currentHeroPower, heroPowerPool)
			if "InvokedbyOthers" in comment:
				newHeroPower = np.random.choice(heroPowerPool)(self.Game, self.ID)
				PRINT(self, "Sir Finley of the Sands's battlecry changes player's Hero Power to %s"%newHeroPower.name)
				newHeroPower.replaceHeroPower()
			elif self.ID == self.Game.turn:
				newHeroPowers = np.random.choice(heroPowerPool, 3, replace=False)
				self.Game.options = [heroPower(self.Game, self.ID) for heroPower in newHeroPowers]
				self.Game.DiscoverHandler.startDiscover(self)
		return None
		
	def discoverDecided(self, option):
		PRINT(self, "New Upgraded Hero Power %s replaces the current Hero Power"%option.name)
		option.replaceHeroPower()
		
		
class Subdue(Spell):
	Class, name = "Paladin", "Subdue"
	requireTarget, mana = True, 2
	index = "Uldum~Paladin~Spell~2~Subdue"
	description = "Change a minion's Attack and Health to 1"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if target != None:
			PRINT(self, "Subdue sets minion %s's Attack and Health to 1."%target.name)
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
		PRINT(self, "Deathrattle: Draw two 1-Health minions from your deck triggers")
		for i in range(2):
			oneHealthMinionsinDeck = []
			for card in self.entity.Game.Hand_Deck.decks[self.entity.ID]:
				if card.cardType == "Minion" and card.health == 1:
					oneHealthMinionsinDeck.append(card)
			if oneHealthMinionsinDeck != []:
				self.entity.Game.Hand_Deck.drawCard(self.entity.ID, np.random.choice(oneHealthMinionsinDeck))
				
				
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
		return target.cardType == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if target != None:
			PRINT(self, "Pharaoh's Blessing gives %s +4/+4, Divine Shield, and Taunt."%target.name)
			target.buffDebuff(4, 4)
			target.getsKeyword("Divine Shield")
			target.getsKeyword("Taunt")
		return target
		
		
class TiptheScales(Spell):
	Class, name = "Paladin", "Tip the Scales"
	requireTarget, mana = False, 8
	index = "Uldum~Paladin~Spell~8~Tip the Scales"
	description = "Summon 7 Murlocs from your deck"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		PRINT(self, "Tip the Scales is cast and summon 7 Murlocs from player's deck")
		murlocsinDeck = []
		for card in self.Game.Hand_Deck.hands[self.ID]:
			if card.cardType == "Minion" and "Murloc" in card.race:
				murlocsinDeck.append(card)
				
		space = self.Game.spaceonBoard(self.ID)
		if murlocsinDeck != [] and space > 0:
			num = min(len(murlocsinDeck), space)
			murlocs = np.random.choice(murlocsinDeck, num, replace=False)
			self.Game.summonfromDeck(murlocs, -1, self.ID)
		return None
		
		
"""Priest cards"""
class ActivatetheObelisk(Quest):
	Class, name = "Priest", "Activate the Obelisk"
	requireTarget, mana = False, 1
	index = "Uldum~Priest~Spell~1~Activate the Obelisk~~Quest~Legendary"
	description = "Quest: Restore 15 Health. Reward: Obelisk's Eye"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_ActivatetheObelisk(self)]
		
class Trigger_ActivatetheObelisk(QuestTrigger):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionGetsHealed", "HeroGetsHealed"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return subject.ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.progress += number
		PRINT(self, "Player restores %d Health and Quest Activate the Obelisk progresses. Current progress: %d"%self.entity.progress)
		if self.entity.progress > 14:
			PRINT(self, "Player has restored 15 or more Health and gains Reward: Obelisk's Eye.")
			self.disconnect()
			extractfrom(self.entity, self.entity.Game.SecretHandler.mainQuests[self.entity.ID])
			ObelisksEye(self.entity.Game, self.entity.ID).replaceHeroPower()
			
class ObelisksEye(HeroPower):
	mana, name, requireTarget = 2, "Obelisk's Eye", True
	index = "Priest~Hero Power~2~Obelisk's Eye"
	description = "Restore 3 Health. If you target a minion, also give it +3/+3"
	def effect(self, target, choice=0):
		heal = 3 * (2 ** self.countHealDouble())
		PRINT(self, "Hero Power Obelisk's Eye restores %d Health to %s"%(heal, target.name))
		self.restoresHealth(target, heal)
		if target.cardType == "Minion":
			PRINT(self, "%s is a minion. Obelisk's Eye also gives it +3/+3"%target.name)
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
		return target.cardType == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if target != None:
			PRINT(self, "Embalming Ritual is cast and gives minion %s Reborn."%target.name)
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
		return target.cardType == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if target != None:
			damage = (3 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			PRINT(self, "Penance is cast and deals %d damage to minion %s"%(damage, target.name))
			self.dealsDamage(target, damage)
		return target
		
		
class SandhoofWaterbearer(Minion):
	Class, race, name = "Priest", "", "Sandhoof Waterbearer"
	mana, attack, health = 5, 5, 5
	index = "Uldum~Priest~Minion~5~5~5~None~Sandhoof Waterbearer"
	requireTarget, keyWord, description = False, "", "At the end of your turn, restore 5 Health to a damaged friendly character"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_SandhoofWaterbearer(self)]
		
class Trigger_SandhoofWaterbearer(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["TurnEnds"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		targets = []
		if self.entity.Game.heroes[self.entity.ID].health < self.entity.Game.heroes[self.entity.ID].health_upper:
			targets.append(self.entity.Game.heroes[self.entity.ID])
		for minion in self.entity.Game.minionsonBoard(self.entity.ID):
			if minion.health < minion.health_upper:
				targets.append(minion)
				
		if targets != []:
			target = np.random.choice(targets)
			heal = 5 * (2 ** self.entity.countHealDouble())
			PRINT(self, "At the end of turn, %s restores %d health to damaged friendly character %s"%(self.entity.name, heal, target.name))
			self.entity.restoresHealth(target, heal)
			
			
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
		PRINT(self, "Deathrattle: Give a random friendly minion +1/+1 triggers")
		minions = self.entity.Game.minionsonBoard(self.entity.ID)
		if minions != []:
			np.random.choice(minions).buffDebuff(1, 1)
			
			
class HolyRipple(Spell):
	Class, name = "Priest", "Holy Ripple"
	requireTarget, mana = False, 2
	index = "Uldum~Priest~Spell~2~Holy Ripple"
	description = "Deal 1 damage to all enemies. Restore 1 Health to all friendly characters"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		damage = (1 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		heal = 1 * (2 ** self.countHealDouble())
		enemies = [self.Game.heroes[3-self.ID]] + self.Game.minionsonBoard(3-self.ID)
		friendlies = [self.Game.heroes[self.ID]] + self.Game.minionsonBoard(self.ID)
		PRINT(self, "Holy Ripple deals %d damage to all enemies and restores %d health to all friendlies."%(damage, heal))
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
		return target.cardType == "Minion" and target != self and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if target != None:
			minion = type(target)(self.Game, target.ID)
			PRINT(self, "Wretched Reclaimer's battlecry destroys friendly minion %s and summons a copy of it"%target.name)
			targetID, position = target.ID, target.position
			self.Game.destroyMinion(target)
			self.Game.gathertheDead() #强制死亡需要在此插入死亡结算，并让随从离场
			#如果目标之前是第4个(position=3)，则场上最后只要有3个随从或者以下，就会召唤到最右边。
			#如果目标不在场上或者是第二次生效时已经死亡等被初始化，则position=-2会让新召唤的随从在场上最右边。
			pos = position if position >= 0 else -1
			self.Game.summonMinion(minion, pos, self.ID)
		return target
		
		
class Psychopomp(Minion):
	Class, race, name = "Priest", "", "Psychopomp"
	mana, attack, health = 4, 3, 1
	index = "Uldum~Priest~Minion~4~3~1~None~Psychopomp~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Summon a random friendly minion that died this game. Give it Reborn"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		PRINT(self, "Psychopomp's battlecry summons a random friendly minion that died this game and gives it Reborn.")
		minionsDied = self.Game.CounterHandler.minionsDiedThisGame[self.ID]
		numSummon = min(self.Game.spaceonBoard(self.ID), len(minionsDied))
		if numSummon > 0:
			minion = self.Game.cardPool[np.random.choice(minionsDied)](self.Game, self.ID)
			#不知道卡德加翻倍召唤出的随从是否也会获得复生，假设会。
			minion.getsKeyword("Reborn")
			PRINT(self, "Psychopomp's battlecry summons %s with Reborn"%minion.name)
			self.Game.summonMinion(minion, self.position+1, self.ID)
		return None
		
		
class HighPriestAmet(Minion):
	Class, race, name = "Priest", "", "High Priest Amet"
	mana, attack, health = 4, 1, 7
	index = "Uldum~Priest~Minion~4~1~7~None~High Priest Amet~Legendary"
	requireTarget, keyWord, description = False, "", "Whenever you summon a minion, set its Health equal to this minion's"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_HighPriestAmet(self)]
		
class Trigger_HighPriestAmet(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionSummoned"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject.ID == self.entity.ID and subject != self.entity and self.entity.health > 0
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self, "A friendly minion %s is summoned and %s applies its own Health on the minion."%(subject.name, self.entity.name))
		subject.statReset(False, self.entity.health)
		
		
class PlagueofDeath(Spell):
	Class, name = "Priest", "Plague of Death"
	requireTarget, mana = False, 9
	index = "Uldum~Priest~Spell~9~Plague of Death"
	description = "Silence and destroy all minions"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		PRINT(self, "Plague of Death is cast, Silences all minions and destroy them.")
		minions = self.Game.minionsonBoard(1) + self.Game.minionsonBoard(2)
		for minion in minions:
			minion.getsSilenced()
			minion.dead = True
		return None
		
		
"""Rogue cards"""
class BazaarBurglary(Quest):
	Class, name = "Rogue", "Bazaar Burglary"
	requireTarget, mana = False, 1
	index = "Uldum~Rogue~Spell~1~Bazaar Burglary~~Quest~Legendary"
	description = "Quest: Add 4 cards from other classes to your hand. Reward: Ancient Blades"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.cardsfromOtherClasses = [] #存放置入手牌的来自其他职业的牌的identity
		self.triggersonBoard = [Trigger_BazaarBurglary(self)]
		
class Trigger_BazaarBurglary(QuestTrigger):
	def __init__(self, entity):
		#置入手牌扳机。抽到不同职业牌，回响牌，抽到时施放的法术都可以触发扳机。
		self.blank_init(entity, ["CardEntersHand", "CardDrawn"]) #抽到时施放的法术没有被处理成置入手牌
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return target[0].ID == self.entity.ID and target[0].Class != "Neutral" and target[0].Class != self.entity.Game.heroes[self.entity.ID].Class
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		if target[0].identity not in self.entity.cardsfromOtherClasses:
			#之所以用牌的identity来作为标识的原因是随从在下场后被闷棍返回手牌之后仍然可以视为作为进度。所以需要用不同的identity加以区分
			self.entity.cardsfromOtherClasses.append(target[0].identity)
			self.entity.progress += 1
			PRINT(self, "A card from another Class %s is put into player's hand, Quest Bazaar Burglary progresses by 1. Current progress: %d"%(target[0].name, self.entity.progress))
			if self.entity.progress > 3:
				PRINT(self, "The 4th card from another Class is put into player's hand. Player gains Reward: Ancient Blades.")
				self.disconnect()
				extractfrom(self.entity, self.entity.Game.SecretHandler.mainQuests[self.entity.ID])
				AncientBlades(self.entity.Game, self.entity.ID).replaceHeroPower()
				
class AncientBlades(HeroPower):
	mana, name, requireTarget = 2, "Ancient Blades", False
	index = "Rogue~Hero Power~2~Ancient Blades"
	description = "Equip a 3/2 Blade with Immune while attacking"
	def effect(self, target=None, choice=0):
		PRINT(self, "Hero Power Ancient Blades equips a 3/2 Mirage Blade with Immune while attacking")
		self.Game.equipWeapon(MirageBlade(self.Game, self.ID))
		return 0
	
class MirageBlade(Weapon):
	Class, name, description = "Rogue", "Mirage Blade", "Your hero is Immune while attacking"
	mana, attack, durability = 2, 3, 2
	index = "Uldum~Rogue~Weapon~2~3~2~Mirage Blade~Uncollectible"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_MirageBlade(self)]
		
class Trigger_MirageBlade(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["BattleStarted", "BattleFinished"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return subject == self.entity.Game.heroes[self.entity.ID] and self.entity.onBoard
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		if signal == "BattleStarted":
			PRINT(self, "Before attack begins, %s gives the attacking hero Immune"%self.entity.name)
			self.entity.Game.playerStatus[self.entity.ID]["Immune"] += 1
		else:
			PRINT(self, "After attack finished, %s removes the Immune from the attacking hero."%self.entity.name)
			if self.entity.Game.playerStatus[self.entity.ID]["Immune"] > 0:
				self.entity.Game.playerStatus[self.entity.ID]["Immune"] -= 1
				
				
class PharaohCat(Minion):
	Class, race, name = "Rogue", "Beast", "Pharaoh Cat"
	mana, attack, health = 1, 1, 2
	index = "Uldum~Rogue~Minion~1~1~2~Beast~Pharaoh Cat~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Add a random Reborn minion to your hand"
	poolIdentifier = "Reborn Minions"
	@classmethod
	def generatePool(cls, Game):
		rebornMinions = []
		for Cost in Game.MinionsofCost.keys():
			for key, value in Game.MinionsofCost[Cost].items():
				if "~Reborn" in key:
					rebornMinions.append(value)
		return "Reborn Minions", rebornMinions
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		PRINT(self, "Pharaoh Cat's battlecry adds a random Reborn minion to player's hand")
		if self.Game.Hand_Deck.handNotFull(self.ID):
			self.Game.Hand_Deck.addCardtoHand(np.random.choice(self.Game.RNGPools["Reborn Minions"]), self.ID, "CreateUsingType")
		return None
		
		
class PlagueofMadness(Spell):
	Class, name = "Rogue", "Plague of Madness"
	requireTarget, mana = False, 1
	index = "Uldum~Rogue~Spell~1~Plague of Madness"
	description = "Each player equips a 2/2 Knife with Poisonous"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		PRINT(self, "Plague of Madness is cast and both players equips a 2/2 Knife with Poisonous")
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
	poolIdentifier = "Spells except Rogue"
	@classmethod
	def generatePool(cls, Game):
		classes, lists = [], []
		for Class in Classes:
			classes.append("Spells except "+Class)
			classPool = copy.deepcopy(Classes)
			extractfrom(Class, classPool)
			spells = []
			for ele in classPool:
				for key, value in Game.ClassCards[ele].items():
					if "~Spell~" in key:
						spells.append(value)
			lists.append(spells)
		return classes, lists
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		PRINT(self, "Clever Disguise is cast and adds 2 random spells from another Class to player's hand")
		if self.Game.Hand_Deck.handNotFull(self.ID):
			Class = self.Game.heroes[self.ID].Class
			key = "Spells except "+Class if Class != "Neutral" else "Spells"
			spells = np.random.choice(self.Game.RNGPools[key], 2, replace=True)
			self.Game.Hand_Deck.addCardtoHand(spells, self.ID, "CreateUsingType")
		return None
		
		
class WhirlkickMaster(Minion):
	Class, race, name = "Rogue", "", "Whirlkick Master"
	mana, attack, health = 2, 1, 2
	index = "Uldum~Rogue~Minion~2~1~2~None~Whirlkick Master"
	requireTarget, keyWord, description = False, "", "Whenever you play a Combo card, add a random Combo card to your hand"
	poolIdentifier = "Combo Cards"
	@classmethod
	def generatePool(cls, Game):
		comboCards = []
		for key, value in Game.ClassCards["Rogue"].items():
			if "~Combo~" in key or key.endswith("~Combo"):
				comboCards.append(value)
		return "Combo Cards", comboCards
		
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_WhirlkickMaster(self)]
		
class Trigger_WhirlkickMaster(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionPlayed", "SpellPlayed", "WeaponPlayed", "HeroCardPlayed"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		#这个随从本身是没有连击的。同时目前没有名字中带有Combo的牌。
		return self.entity.onBoard and subject.ID == self.entity.ID and "~Combo" in subject.index
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self, "Player plays a Combo card and %s adds random Combo card to player's hand."%self.entity.name)
		self.entity.Game.Hand_Deck.addCardtoHand(np.random.choice(self.entity.Game.RNGPools["Combo Cards"]), self.entity.ID, "CreateUsingType")
		
		
class HookedScimitar(Weapon):
	Class, name, description = "Rogue", "Hooked Scimitar", "Combo: Gain +2 Attack"
	mana, attack, durability = 3, 2, 2
	index = "Uldum~Rogue~Weapon~3~2~2~Hooked Scimitar~Combo"
	
	def effectCanTrigger(self):
		self.effectViable = self.Game.CounterHandler.numCardsPlayedThisTurn[self.ID] > 0
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if self.Game.CounterHandler.numCardsPlayedThisTurn[self.ID] > 0:
			PRINT(self, "Hooked Scimitar's Combo triggers and gives weapon +2 Attack")
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
		PRINT(self, "Deathrattle: Return a random enemy minion to its owner's hand triggers.")
		if self.entity.Game.minionsonBoard(3-self.entity.ID) != []:
			minion = np.random.choice(self.entity.Game.minionsonBoard(3-self.entity.ID))
			PRINT(self, "Deathrattle returns enemy minion %s to its owner's hand"%minion.name)
			#这个亡语的触发对象一定是还在场上的触发，即将触发死亡扳机的随从不在minionsonBoard里面
			self.entity.Game.returnMiniontoHand(minion)
			
			
class BazaarMugger(Minion):
	Class, race, name = "Rogue", "", "Bazaar Mugger"
	mana, attack, health = 5, 3, 5
	index = "Uldum~Rogue~Minion~5~3~5~None~Bazaar Mugger~Rush~Battlecry"
	requireTarget, keyWord, description = False, "Rush", "Rush. Battlecry: Add a random minion from another class to your hand"
	poolIdentifier = "Minions except Rogue"
	@classmethod
	def generatePool(cls, Game):
		classes, lists = [], []
		for Class in Classes:
			classes.append("Minions except "+Class)
			classPool = copy.deepcopy(Classes)
			extractfrom(Class, classPool)
			minions = []
			for ele in classPool:
				for key, value in Game.ClassCards[ele].items():
					if "~Minion~" in key:
						minions.append(value)
			lists.append(minions)
		return classes, lists
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		PRINT(self, "Bazaar Mugger's battlecry adds a random minion from another Class to player's hand")
		if self.Game.Hand_Deck.handNotFull(self.ID):
			Class = self.Game.heroes[self.ID].Class
			key = "Minions except "+Class if Class != "Neutral" else "Minions except "+np.random.choice(Classes)
			self.Game.Hand_Deck.addCardtoHand(np.random.choice(self.Game.RNGPools[key]), self.ID, "CreateUsingType")
		return None
		
		
class ShadowofDeath(Spell):
	Class, name = "Rogue", "Shadow of Death"
	requireTarget, mana = True, 4
	index = "Uldum~Rogue~Spell~4~Shadow of Death"
	description = "Choose a minion. Shuffle 3 'Shadows' into your deck that summon a copy when drawn"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if target != None:
			PRINT(self, "Shadow of Death shuffles 3 'Shadows' into player's deck. When drawn, they summon a copy of the chosen minion %s"%target.name)
			for i in range(3):
				typeName = type(target).__name__
				newIndex = "Uldum~Rogue~4~Spell~Shadow~Casts When Drawn~Summon %s~Uncollectible"%typeName
				subclass = type("Shadow_"+typeName, (Shadow_Mutable, ),
								{"index": newIndex, "description": "Casts When Drawn. Summon a "+typeName,
								"miniontoSummon": type(target)}
								)
				self.Game.cardPool[newIndex] = subclass #Create the subclass and add it to the game's cardPool.
				self.Game.Hand_Deck.shuffleCardintoDeck(subclass(self.Game, self.ID), self.ID)
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
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if self.miniontoSummon != None:
			minion = self.miniontoSummon(self.Game, self.ID)
			PRINT(self, "Shadow is cast and summons %s"%minion.name)
			self.Game.summonMinion(minion, -1, self.ID)
		return None
		
		
class AnkatheBuried(Minion):
	Class, race, name = "Rogue", "", "Anka, the Buried"
	mana, attack, health = 5, 5, 5
	index = "Uldum~Rogue~Minion~5~5~5~None~Anka, the Buried~Battlecry~Legendary"
	requireTarget, keyWord, description = False, "", "Battlecry: Change each Deathrattle minion in your hand into a 1/1 that costs (1)"
	#不知道安卡的战吼是否会把手牌中的亡语随从变成新的牌还是只会修改它们的身材
	def effectCanTrigger(self):
		self.effectViable = False
		for card in self.Game.Hand_Deck.hands[self.ID]:
			if card.cardType == "Minion" and card.deathrattles != [] and card != self:
				self.effectViable = True
				break
				
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		PRINT(self, "Anka, the Buried's battlecry changes all Deathrattle minions in player's hands to 1/1 copies that cost (1)")
		for card in fixedList(self.Game.Hand_Deck.hands[self.ID]):
			if card.cardType == "Minion" and card.deathrattles != []:
				card.statReset(1, 1)
				ManaModification(card, changeby=0, changeto=1).applies()
		return None
		
"""Shaman cards"""
class CorrupttheWaters(Quest):
	Class, name = "Shaman", "Corrupt the Waters"
	requireTarget, mana = False, 1
	index = "Uldum~Shaman~Spell~1~Corrupt the Waters~~Quest~Legendary"
	description = "Quest: Play 6 Battlecry cards. Reward: Heart of Vir'naal"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_CorrupttheWaters(self)]
		
class Trigger_CorrupttheWaters(QuestTrigger):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionBeenPlayed", "WeaponBeenPlayed", "HeroCardBeenPlayed"]) #扳机是使用后扳机
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return subject.ID == self.entity.ID and "~Battlecry" in subject.index
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.progress += 1
		PRINT(self, "After player plays Battlecry card %s, Quest Corrupt the Waters progresses by 1. Current progress: %d"%(subject.name, self.entity.progress))
		if self.entity.progress > 5:
			PRINT(self, "Player plays the 6th Battlecry card and gains Reward: Heart of Vir'naal.")
			self.disconnect()
			extractfrom(self.entity, self.entity.Game.SecretHandler.mainQuests[self.entity.ID])
			HeartofVirnaal(self.entity.Game, self.entity.ID).replaceHeroPower()
			
class HeartofVirnaal(HeroPower):
	mana, name, requireTarget = 2, "Heart of Vir'naal", False
	index = "Shaman~Hero Power~2~Heart of Vir'naal"
	description = "Your Battlecries trigger twice this turn"
	def effect(self, target=None, choice=0):
		PRINT(self, "Hero Power Heart of Vir'naal makes player's Battlecries trigger twice this turn.")
		self.Game.playerStatus[self.ID]["Battlecry Trigger Twice"] += 1
		self.Game.turnEndTrigger.append(BattlecryTriggerTwiceEffectDisappears(self.Game, self.ID))
		return 0
		
class BattlecryTriggerTwiceEffectDisappears:
	def __init__(self, Game, ID):
		self.Game, self.ID = Game, ID
		
	def turnEndTrigger(self):
		PRINT(self, "At the end of turn, Heart of Vir'naal's effect expires and player's Battlecries no longer trigger twice")
		self.Game.playerStatus[self.ID]["Battlecry Trigger Twice"] -= 1
		extractfrom(self, self.Game.turnEndTrigger)
		
	def selfCopy(self, recipientGame):
		return type(self)(recipientGame, self.ID)
		
		
class TotemicSurge(Spell):
	Class, name = "Shaman", "Totemic Surge"
	requireTarget, mana = False, 0
	index = "Uldum~Shaman~Spell~0~Totemic Surge"
	description = "Give your Totems +2 Attack"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		PRINT(self, "Totemic Surge gives all friendly totems +2 Attack")
		for minion in fixedList(self.Game.minionsonBoard(self.ID)):
			if "Totem" in minion.race:
				minion.buffDebuff(2, 0)
		return None
		
		
class EVILTotem(Minion):
	Class, race, name = "Shaman", "Totem", "EVIL Totem"
	mana, attack, health = 2, 0, 2
	index = "Uldum~Shaman~Minion~2~0~2~Totem~EVIL Totem"
	requireTarget, keyWord, description = False, "", "At the end of your turn, add a Lackey to your hand"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_EVILTotem(self)]
		
class Trigger_EVILTotem(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["TurnEnds"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self, "At the end of turn, %s adds a Lackey to player's hand"%self.entity.name)
		self.entity.Game.Hand_Deck.addCardtoHand(np.random.choice(Lackeys), self.entity.ID, "CreateUsingType")
		
		
class SandstormElemental(Minion):
	Class, race, name = "Shaman", "Elemental", "Sandstorm Elemental"
	mana, attack, health = 2, 2, 2
	index = "Uldum~Shaman~Minion~2~2~2~Elemental~Sandstorm Elemental~Overload~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Deal 1 damage to all enemy minions. Overload: (1)"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.overload = 1
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		PRINT(self, "Sandstorm Elemental's battlecry deals 1 damage to all enemy minions")
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
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		PRINT(self, "Plague of Murlocs is cast and transforms all minions into random Murlocs")
		for minion in fixedList(self.Game.minionsonBoard(1) + self.Game.minionsonBoard(2)):
			self.Game.transform(minion, np.random.choice(self.Game.RNGPools["Murlocs"])(self.Game, minion.ID))
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
		
	def effectCanTrigger(self):
		self.effectViable = False
		if self.targetExists():
			for minion in self.Game.minionsonBoard(self.ID):
				if minion.name.endswith("Lackey"):
					self.effectViable = True
					
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		controlsLackey = False
		for minion in self.Game.minionsonBoard(self.ID):
			if "Lackey" in minion.name and "~Uncollectible" in minion.index:
				controlsLackey = True
				
		if target != None and controlsLackey:
			PRINT(self, "Weaponized Wasp's battlecry deals 3 damage to %s"%target.name)
			self.dealsDamage(target, 3)
		return target
		
		
class SplittingAxe(Weapon):
	Class, name, description = "Shaman", "Splitting Axe", "Battlecry: Summon copies of your Totems"
	mana, attack, durability = 4, 3, 2
	index = "Uldum~Shaman~Weapon~4~3~2~Splitting Axe~Battlecry"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		PRINT(self, "Splitting Axe's battlecry summons copies of all friendly Totem")
		for minion in fixedList(self.Game.minionsonBoard(self.ID)):
			if "Totem" in minion.race:
				self.Game.summonMinion(minion.selfCopy(minion.ID), minion.position+1, self.ID)
		return None
		
		
class Vessina(Minion):
	Class, race, name = "Shaman", "", "Vessina"
	mana, attack, health = 4, 2, 6
	index = "Uldum~Shaman~Minion~4~2~6~None~Vessina~Legendary"
	requireTarget, keyWord, description = False, "", "While you're Overloaded, your other minions have +2 Attack"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.auras["Buff Aura"] = BuffAura_Vessina(self)
		self.activated = False
		
class BuffAura_Vessina:
	def __init__(self, minion):
		self.minion = minion
		self.auraAffected = []
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		if signal == "MinionAppears":
			return self.minion.onBoard and subject.ID == self.minion.ID and subject != self.minion and self.minion.activated
		else:
			return self.minion.onBoard and ID == self.minion.ID
			
	def trigger(self, signal, ID, subject, target, number, comment, choice=0):
		if self.canTrigger(signal, ID, subject, target, number, comment):
			self.effect(signal, ID, subject, target, number, comment)
			
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		if signal == "MinionAppears":
			if self.minion.activated:
				self.applies(subject)
		else: #signal == "OverloadStatusCheck"
			isOverloaded = self.minion.Game.ManaHandler.manasOverloaded[self.minion.ID] > 0 or self.minion.Game.ManaHandler.manasLocked[self.minion.ID] > 0
			if isOverloaded == False and self.minion.activated:
				self.minion.activated = False
				PRINT(self.minion, "Vessina's Buff Aura: Your other minions have +2 Attack is shut down.")
				for minion, aura_Receiver in fixedList(self.auraAffected):
					aura_Receiver.effectClear()
				self.auraAffected = []
			elif isOverloaded and self.minion.activated == False:
				self.minion.activated = True
				PRINT(self.minion, "Vessina's Buff Aura: Your other minions have +2 Attack is activated.")
				for minion in self.minion.Game.minionsonBoard(self.minion.ID):
					self.applies(minion)
				
	def applies(self, subject):
		if subject != self.minion:
			PRINT(self.minion, "Minion %s gains the %d/%d aura from %s"%(subject.name, 2, 0, self.minion))
			aura_Receiver = BuffAura_Receiver(subject, self, 2, 0)
			aura_Receiver.effectStart()
			
	def auraAppears(self):
		isOverloaded = self.minion.Game.ManaHandler.manasOverloaded[self.minion.ID] > 0 or self.minion.Game.ManaHandler.manasLocked[self.minion.ID] > 0
		if isOverloaded:
			self.minion.activated = True
			PRINT(self.minion, "Vessina's Buff Aura: Your other minions have +2 Attack is activated.")
			for minion in self.minion.Game.minionsonBoard(self.minion.ID):
				self.applies(minion)
				
		self.minion.Game.triggersonBoard[self.minion.ID].append((self, "MinionAppears"))
		self.minion.Game.triggersonBoard[self.minion.ID].append((self, "OverloadStatusCheck"))
		
	def auraDisappears(self):
		PRINT(self.minion, "Vessina's Buff Aura: Your other minions have +2 Attack is shut down.")
		for minion, aura_Receiver in fixedList(self.auraAffected):
			aura_Receiver.effectClear()
			
		self.auraAffected = []
		self.minion.activated = False
		extractfrom((self, "OverloadStatusCheck"), self.minion.Game.triggersonBoard[self.minion.ID])
		extractfrom((self, "MinionAppears"), self.minion.Game.triggersonBoard[self.minion.ID])
		
	def selfCopy(self, recipientMinion):
		return type(self)(recipientMinion)
		
		
class Earthquake(Spell):
	Class, name = "Shaman", "Earthquake"
	requireTarget, mana = False, 7
	index = "Uldum~Shaman~Spell~7~Earthquake"
	description = "Deal 5 damage to all minions, then deal 2 damage to all minions"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		damage5 = (5 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		PRINT(self, "Earthquake deals %d damage to all minions"%damage5)
		targets = self.Game.minionsonBoard(self.ID) + self.Game.minionsonBoard(3-self.ID)
		self.dealsAOE(targets, [damage5 for minion in targets])
		#地震术在第一次AOE后会让所有随从结算死亡事件，然后再次对全场随从打2.
		self.Game.gathertheDead()
		#假设法强随从如果在这个过程中死亡并被移除，则法强等数值会随之变化。
		damage2 = (2 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		PRINT(self, "Earthquake deals %d damage to all minions"%damage2)
		targets = self.Game.minionsonBoard(self.ID) + self.Game.minionsonBoard(3-self.ID)
		self.dealsAOE(targets, [damage2 for minion in targets])
		return None
		
		
class MoguFleshshaper(Minion):
	Class, race, name = "Shaman", "", "Mogu Fleshshaper"
	mana, attack, health = 9, 3, 4
	index = "Uldum~Shaman~Minion~9~3~4~None~Mogu Fleshshaper~Rush"
	requireTarget, keyWord, description = False, "Rush", "Rush. Costs (1) less for each minion on the battlefield"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersinHand = [Trigger_MoguFleshshaper(self)]
		
	def selfManaChange(self):
		if self.inHand:
			num = len(self.Game.minionsonBoard(1)) + len(self.Game.minionsonBoard(2))
			PRINT(self, "Mogu Fleshshaper reduces its own cost by %d"%num)
			self.mana -= num
			self.mana = max(0, self.mana)
			
class Trigger_MoguFleshshaper(TriggerinHand):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionAppears", "MinionDisappears"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.inHand
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.Game.ManaHandler.calcMana_Single(self.entity)
		
		
"""Warlock cards"""
class PlagueofFlames(Spell):
	Class, name = "Warlock", "Plague of Flames"
	requireTarget, mana = False, 1
	index = "Uldum~Warlock~Spell~1~Plagues of Flames"
	description = "Destroy all your minions. For each one, destroy a random enemy minion"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		#不知道是否涉及强制死亡，还是只用把随从们设为dead即可
		PRINT(self, "Plague of Flames destroys all friendly minions and destroys a random enemy minion for each friendly minion destroyed.")
		num = 0
		for minion in self.Game.minionsonBoard(self.ID):
			minion.dead = True
			num += 1
		for i in range(num):
			targets = []
			for minion in self.Game.minionsonBoard(3-self.ID):
				if minion.dead == False and minion.health > 0:
					targets.append(minion)
					
			if targets != []:
				minion = np.random.choice(targets)
				PRINT(self, "Plague of Flames kills random enemy minion %s"%minion.name)
				minion.dead = True
			else:
				break
		return None
		
		
class SinisterDeal(Spell):
	Class, name = "Warlock", "Sinister Deal"
	requireTarget, mana = False, 1
	index = "Uldum~Warlock~Spell~1~Sinister Deal"
	description = "Discover a Lackey"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if "InvokedbyOthers" in comment:
			PRINT(self, "Sinister Deal is cast and adds random Lackey to player's hand")
			self.Game.Hand_Deck.addCardtoHand(np.random.choice(Lackeys), self.ID, "CreateUsingType")
		else:
			lackeys = np.random.choice(Lackeys, 3, replace=False)
			self.Game.options = [lackey(self.Game, self.ID) for lackey in lackeys]
			PRINT(self, "Sinister Deal is cast and lets player discover a Lackey")
			self.Game.DiscoverHandler.startDiscover(self)
		return None
		
	def discoverDecided(self, option):
		PRINT(self, "Lackey %s is put into player's hand."%option.name)
		self.Game.Hand_Deck.addCardtoHand(option, self.ID)
		self.Game.sendSignal("DiscoveredCardPutintoHand", self.ID, self, option, 0, "")
		
		
class SupremeArchaeology(Quest):
	Class, name = "Warlock", "Supreme Archaeology"
	requireTarget, mana = False, 1
	index = "Uldum~Warlock~Spell~1~Supreme Archaeology~~Quest~Legendary"
	description = "Quest: Draw 20 cards. Reward: Tome of Origination"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_SupremeArchaeology(self)]
		
class Trigger_SupremeArchaeology(QuestTrigger):
	def __init__(self, entity):
		self.blank_init(entity, ["CardDrawn"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.progress += 1
		PRINT(self, "Player draws a card. Quest Supreme Archaeologist progresses by 1. Current progress: %d"%self.entity.progress)
		if self.entity.progress > 19:
			PRINT(self, "Player draws the 20th card and gains Reward: Tome of Origination.")
			self.disconnect()
			extractfrom(self.entity, self.entity.Game.SecretHandler.mainQuests[self.entity.ID])
			TomeofOrigination(self.entity.Game, self.entity.ID).replaceHeroPower()
			
class TomeofOrigination(HeroPower):
	mana, name, requireTarget = 2, "Tome of Origination", False
	index = "Warlock~Hero Power~2~Tome of Origination"
	description = "Draw a card. It costs (0)"
	def effect(self, target=None, choice=0):
		PRINT(self, "Hero Power Tome of Origination lets player draw a card. It costs (0)")
		card, mana = self.Game.Hand_Deck.drawCard(self.ID)
		if card != None:
			self.Game.sendSignal("CardDrawnfromHeroPower", self.ID, self, card, mana, "")
			ManaModification(card, changeby=0, changeto=0).applies()
		return 0
		
		
class ExpiredMerchant(Minion):
	Class, race, name = "Warlock", "", "Expired Merchant"
	mana, attack, health = 2, 2, 1
	index = "Uldum~Warlock~Minion~2~2~1~None~Expired Merchant~Battlecry~Deathrattle"
	requireTarget, keyWord, description = False, "", "Battlecry: Discard your highest Cost card. Deathrattle: Add 2 copies of it to your hand"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [Return2CopiesofDiscardedCard(self)]
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		cardswithHighestCost, highestCost = [], -np.inf
		for card in self.Game.Hand_Deck.hands[self.ID]:
			if card.mana > highestCost:
				cardswithHighestCost = [card]
				highestCost = card.mana
			elif card.mana == highestCost:
				cardswithHighestCost.append(card)
				
		#假设Expired Merchant和鲨鱼之神类似，只会记录最后一次被弃掉的牌，第二次的会覆盖第一次弃掉的
		if cardswithHighestCost != []:
			card = np.random.choice(cardswithHighestCost)
			self.Game.Hand_Deck.discardCard(self.ID, card)
			PRINT(self, "Expired Merchant discards %s"%card.name)
			for trigger in self.deathrattles:
				if type(trigger) == Return2CopiesofDiscardedCard:
					trigger.discardedCard = type(card)
		return None
		
class Return2CopiesofDiscardedCard(Deathrattle_Minion):
	def __init__(self, entity):
		self.blank_init(entity)
		self.discardedCard = None
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		if self.discardedCard != None:
			PRINT(self, "Deathrattle: Add 2 copies of the discarded card %s to player's hand triggers"%self.discardedCard.name)
			self.entity.Game.Hand_Deck.addCardtoHand([self.discardedCard, self.discardedCard], self.entity.ID, "CreateUsingType")
			
	def selfCopy(self, recipientMinion):
		trigger = type(self)(recipientMinion)
		trigger.discardedCard = self.discardedCard
		return trigger
		
class EVILRecruiter(Minion):
	Class, race, name = "Warlock", "", "EVIL Recruiter"
	mana, attack, health = 3, 3, 3
	index = "Uldum~Warlock~Minion~3~3~3~None~EVIL Recruiter~Battlecry"
	requireTarget, keyWord, description = True, "", "Battlecry: Destroy a friendly Lackey to summon a 5/5 Demon"
	
	def targetExists(self, choice=0):
		return self.selectableFriendlyMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.ID == self.ID and "Lackey" in target.name and "~Uncollectible" in target.index and target.onBoard
		
	def effectCanTrigger(self): #Friendly minions are always selectable.
		self.effectViable = False
		for minion in self.Game.minionsonBoard(self.ID):
			if minion.name.endswith("Lackey"):
				self.effectViable = True
				
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if target != None:
			#假设消灭跟班之后会进行强制死亡结算，把跟班移除之后才召唤
			#假设召唤的恶魔是在EVIL Recruiter的右边，而非死亡的跟班的原有位置
			PRINT(self, "EVIL Recruiter's battlecry destroys friendly Lackey %s to summon a 5/5 Demon"%target.name)
			target.dead = True
			self.Game.gathertheDead()
			self.Game.summonMinion(EVILDemon(self.Game, self.ID), self.position+1, self.ID)
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
		self.triggersonBoard = [Trigger_NefersetThrasher(self)]
		
class Trigger_NefersetThrasher(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionAttackingMinion", "MinionAttackingHero"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return subject == self.entity and self.entity.onBoard
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self, "Whenever it attacks, %s deals 3 damage to hero"%self.entity.name)
		self.entity.dealsDamage(self.entity.Game.heroes[self.entity.ID], 3)
		
		
class Impbalming(Spell):
	Class, name = "Warlock", "Impbalming"
	requireTarget, mana = True, 4
	index = "Uldum~Warlock~Spell~4~Impbalming"
	description = "Destroy a minion. Shuffle 3 Worthless Imps into your deck"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if target != None:
			PRINT(self, "Impbalming destroys minion %s and shuffles three 1/1 Imps into player's deck"%target.name)
			target.dead = True
			self.Game.Hand_Deck.shuffleCardintoDeck([WorthlessImp(self.Game, self.ID) for i in range(3)], self.ID)
		return target
		
class WorthlessImp(Minion):
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
		self.triggersonBoard = [Trigger_DiseasedVulture(self)]
		
class Trigger_DiseasedVulture(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["HeroTookDamage"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return target == self.entity.Game.heroes[self.entity.ID] and self.entity.ID == self.entity.Game.turn
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self, "After player takes damage on their own turn, %s summons a random 3-Cost minion"%self.entity.name)
		self.entity.Game.summonMinion(np.random.choice(self.entity.Game.RNGPools["3-Cost Minions to Summon"])(self.entity.Game, self.entity.ID), self.entity.position+1, self.entity.ID)
		
		
class Riftcleaver(Minion):
	Class, race, name = "Warlock", "Demon", "Riftcleaver"
	mana, attack, health = 6, 7, 5
	index = "Uldum~Warlock~Minion~6~7~5~Demon~Riftcleaver~Battlecry"
	requireTarget, keyWord, description = True, "", "Battlecry: Destroy a minion. Your hero takes damage equal to its health"
	
	def targetExists(self, choice=0):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target != self and target.onBoard
		#不知道连续触发战吼时，第二次是否还会让玩家受到伤害
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if target != None and target.dead == False:
			PRINT(self, "Riftcleaver's battlecry destroys minion %s and player takes damage equal to its Health"%target.name)
			target.dead = True
			damage = target.health
			#不知道这个对于英雄的伤害有无伤害来源。假设没有，和抽牌疲劳伤害类似
			objtoTakeDamage = self.Game.DamageHandler.damageTransfer(self.Game.heroes[self.ID])
			objtoTakeDamage.takesDamage(None, damage) #假设伤害没有来源
		return target
		
#光环生效时跟班变成白字的4/4，可以在之后被buff，reset和光环buff。返回手牌中时也会是4/4的身材。沉默之后仍为4/4
#无面操纵者复制对方的4/4跟班也会得到4/4的跟班
#光环生效时的非光环buff会消失，然后成为4/4白字
class DarkPharaohTekahn(Minion):
	Class, race, name = "Warlock", "", "Dark Pharaoh Tekahn"
	mana, attack, health = 5, 4, 4
	index = "Uldum~Warlock~Minion~5~4~4~None~Dark Pharaoh Tekahn~Battlecry~Legendary"
	requireTarget, keyWord, description = False, "", "Battlecry: For the rest of the game, your Lackeys are 4/4"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		PRINT(self, "Dark Pharaoh Tekahn's battlecry makes player's Lackeys 4/4 for the rest of the game")
		aura = YourLackeysareAlways44(self.Game, self.ID)
		self.Game.auras.append(aura)
		aura.auraAppears()
		return None
		
class YourLackeysareAlways44:
	def __init__(self, Game, ID):
		self.Game, self.ID = Game, ID
		self.auraAffected = [] #A list of (minion, aura_Receiver)
		
	def applicable(self, target):
		return target.ID == self.ID and target.name.endswith("Lackey")
	#All minions appearing on the same side will be subject to the buffAura.
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		if signal == "MinionAppears":
			return self.applicable(subject)
		elif signal == "CardEntersHand":
			return self.applicable(target[0]) #The target here is a holder
		#else: #signal == "CardShuffled"
		#	if type(target) == type([]) or type(target) == type(np.array([])):
		#		for card in target:
		#			self.applicable(card)
		#	else: #Shuffling a single card
		#		return self.applicable(target)
			
	def trigger(self, signal, ID, subject, target, number, comment, choice=0):
		if self.canTrigger(signal, ID, subject, target, number, comment):
			self.effect(signal, ID, subject, target, number, comment)
			
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
			PRINT(self, "Minion {} becomes a 4/4 due to the effect of {}".format(subject.name, self))
			#暂时假设跟班被对方控制后仍为4/4
	def auraAppears(self):
		PRINT(self, "{} appears and starts its buff aura".format(self))
		for card in self.Game.minionsonBoard(self.ID) + self.Game.Hand_Deck.hands[self.ID] + self.Game.Hand_Deck.decks[self.ID]:
			self.applies(card)
			
		#Only need to handle minions that appear. Them leaving/silenced will be handled by the BuffAura_Receiver object.
		#We want this Trigger_MinionAppears can handle everything including registration and buff and removing.
		self.Game.triggersonBoard[self.ID].append((self, "MinionAppears")) #Minions entering the board
		self.Game.triggersonBoard[self.ID].append((self, "CardEntersHand")) #Minions entering the hand
		#self.Game.triggersonBoard[self.ID].append((self, "CardShuffled")) #Minions entering the deck
		
	#Doesn't have auraDisappears func, since this aura is permanent
	def selfCopy(self, recipientGame): #The recipientMinion is the minion that deals the Aura.
		#func that checks if subject is applicable will be the new copy's function
		return type(self)(recipientGame, self.ID)
		
		
"""Warrior cards"""
class HacktheSystem(Quest):
	Class, name = "Warrior", "Hack the System"
	requireTarget, mana = False, 1
	index = "Uldum~Warrior~Spell~1~Hack the System~~Quest~Legendary"
	description = "Quest: Attack 5 times with your hero. Reward: Anraphet's Core"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_HacktheSystem(self)]
		
class Trigger_HacktheSystem(QuestTrigger):
	def __init__(self, entity):
		self.blank_init(entity, ["HeroAttackedHero", "HeroAttackedMinion"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return subject == self.entity.Game.heroes[self.entity.ID]
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.progress += 1
		PRINT(self, "After player attacks. Quest Hack the System progresses by 1. Current progress: %d"%self.entity.progress)
		if self.entity.progress > 4:
			PRINT(self, "Player has attacked the 5th time and gains Reward: Anraphet's Core.")
			self.disconnect()
			extractfrom(self.entity, self.entity.Game.SecretHandler.mainQuests[self.entity.ID])
			AnraphetsCore(self.entity.Game, self.entity.ID).replaceHeroPower()
			
class AnraphetsCore(HeroPower):
	mana, name, requireTarget = 2, "Anraphet's Core", False
	index = "Warrior~Hero Power~2~Anraphet's Core"
	description = "Summon a 4/3 Golem. After your hero attacks, refresh this"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_AnraphetsCore(self)]
		
	def available(self, choice=0):
		if self.heroPowerTimes >= self.heroPowerChances_base + self.heroPowerChances_extra:
			return False
		if self.Game.spaceonBoard(self.ID) < 1:
			return False
		return True
		
	def effect(self, target=None, choice=0):
		#Hero Power summoning won't be doubled by Khadgar.
		PRINT(self, "Hero Power Anraphet's Core summons a 4/3 Golem")
		self.Game.summonMinion(StoneGolem(self.Game, self.ID), -1, self.ID, "")
		return 0
		
class Trigger_AnraphetsCore(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["HeroAttackedHero", "HeroAttackedMinion"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return subject == self.entity.Game.heroes[self.entity.ID] and self.entity.heroPowerTimes >= self.entity.heroPowerChances_base + self.entity.heroPowerChances_extra
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self, "Player attacks and Hero Power Anraphet's Core is refreshed.")
		self.entity.heroPowerChances_extra += 1
		
class StoneGolem(Minion):
	Class, race, name = "Warrior", "", "Stone Golem"
	mana, attack, health = 3, 4, 3
	index = "Uldum~Warrior~Minion~3~4~3~None~Stone Golden~Uncollectible"
	requireTarget, keyWord, description = False, "", ""
	
	
class IntotheFray(Spell):
	Class, name = "Warrior", "Into the Fray"
	requireTarget, mana = False, 1
	index = "Uldum~Warrior~Spell~1~Into the Fray"
	description = "Give all Taunt minions in your hand +2/+2"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		PRINT(self, "Into the Fray is cast and gives all Taunt minions in player's hand +2/+2")
		for card in fixedList(self.Game.Hand_Deck.hands[self.ID]):
			if card.cardType == "Minion" and card.keyWords["Taunt"] > 0:
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
		classes, lists, neutralMinions = [], [], []
		#确定中立的战吼随从列表
		for key, value in Game.NeutralMinions.items():
			if "~Minion~" in key and "~Taunt~" in key:
				neutralMinions.append(value)
		for Class in Classes:
			classes.append("Taunt Minions as " + Class)
			tauntMinionsinClass = []
			for key, value in Game.ClassCards[Class].items():
				if "~Minion~" in key and "~Taunt~" in key:
					tauntMinionsinClass.append(value)
			#包含职业牌中的战吼随从和中立战吼随从
			lists.append(tauntMinionsinClass+neutralMinions)
		return classes, lists #返回的包含“Class Cards except Hunter”等identifier的列表和其他职业卡表
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if self.Game.Hand_Deck.handNotFull(self.ID) and self.ID == self.Game.turn:
			key = "Taunt Minions as "+classforDiscover(self)
			if "InvokedbyOthers" in comment:
				PRINT(self, "Frightened Flunky's battlecry adds a random Taunt minion to player's hand")
				self.Game.Hand_Deck.addCardtoHand(np.random.choice(self.Game.RNGPools[key]), self.ID, "CreateUsingType")
			else:
				minions = np.random.choice(self.Game.RNGPools[key], 3, replace=False)
				self.Game.options = [minion(self.Game, self.ID) for minion in minions]
				PRINT(self, "Frightened Flunky's battlecry lets player discover a Taunt minion")
				self.Game.DiscoverHandler.startDiscover(self)
				
		return None
		
	def discoverDecided(self, option):
		PRINT(self, "Taunt minion %s is put into player's hand."%option.name)
		self.Game.Hand_Deck.addCardtoHand(option, self.ID)
		self.Game.sendSignal("DiscoveredCardPutintoHand", self.ID, self, option, 0, "")
		
		
class BloodswornMercenary(Minion):
	Class, race, name = "Warrior", "", "Bloodsworn Mercenary"
	mana, attack, health = 3, 3, 3
	index = "Uldum~Warrior~Minion~3~3~3~None~Bloodsworn Mercenary~Battlecry"
	requireTarget, keyWord, description = True, "", "Battlecry: Choose a damaged friendly minion. Summon a copy of it"
	
	def targetExists(self, choice=0):
		return self.selectableFriendlyMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.ID == self.ID and target != self and target.onBoard and target.health < target.health_upper
		
	def effectCanTrigger(self):
		self.effectViable = False
		for minion in self.Game.minionsonBoard(self.ID):
			if minion.health < minion.health_upper:
				self.effectViable = True
				break
				
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if target != None:
			PRINT(self, "Bloodsworn Mercenary's summons a copy of damaged friendly minion %s"%target.name)
			minion = target.selfCopy(self.ID) if target.onBoard else type(target)(self.Game, self.ID)
			self.Game.summonMinion(minion, target.position+1, self.ID)
		return target
		
		
class LivewireLance(Weapon):
	Class, name, description = "Warrior", "Livewire Lance", "After your hero attacks, add a Lackey to your hand"
	mana, attack, durability = 3, 2, 2
	index = "Uldum~Warrior~Weapon~3~2~2~Livewire Lance"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_LivewireLance(self)]
		
class Trigger_LivewireLance(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["HeroAttackedMinion", "HeroAttackedHero"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		#The target can't be dying to trigger this
		return subject == self.entity.Game.heroes[self.entity.ID] and self.entity.onBoard
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self, "After hero attacks, weapon %s adds a Lackey to player's hand"%self.entity.name)
		self.entity.Game.Hand_Deck.addCardtoHand(np.random.choice(Lackeys), self.entity.ID, "CreateUsingType")
		
		
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
			if minion.health < minion.health_upper:
				return True
		return False
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		PRINT(self, "Plague of Wrath destroys all damaged minions.")
		for minion in self.Game.minionsonBoard(1) + self.Game.minionsonBoard(2):
			if minion.health < minion.health_upper:
				minion.dead = True
		return None
		
		
class Armagedillo(Minion):
	Class, race, name = "Warrior", "Beast", "Armagedillo"
	mana, attack, health = 6, 4, 7
	index = "Uldum~Warrior~Minion~6~4~7~Beast~Armagedillo~Taunt~Legendary"
	requireTarget, keyWord, description = False, "Taunt", "Taunt. At the end of your turn, give all Taunt minions in your hand +2/+2"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_Armagedillo(self)]
		
class Trigger_Armagedillo(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["TurnEnds"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self, "At the end of turn, %s gives all Taunt minions in player's hand +2/+2"%self.entity.name)
		for card in self.entity.Game.Hand_Deck.hands[self.entity.ID]:
			if card.cardType == "Minion" and card.keyWords["Taunt"] > 0:
				card.buffDebuff(2, 2)
				
				
class ArmoredGoon(Minion):
	Class, race, name = "Warrior", "", "Armored Goon"
	mana, attack, health = 6, 6, 7
	index = "Uldum~Warrior~Minion~6~6~7~None~Armored Goon"
	requireTarget, keyWord, description = False, "", "Whenever your hero attacks, gain 5 Armor"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_ArmoredGoon(self)]
		
class Trigger_ArmoredGoon(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["HeroAttackingHero", "HeroAttackingMinion"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject == self.entity.Game.heroes[self.entity.ID]
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self, "Whenever player attacks, %s lets player gain +5 Armor"%self.entity.name)
		self.entity.Game.heroes[self.entity.ID].gainsArmor(5)
		
		
class TombWarden(Minion):
	Class, race, name = "Warrior", "Mech", "Tomb Warden"
	mana, attack, health = 8, 3, 6
	index = "Uldum~Warrior~Minion~8~3~6~Mech~Tomb Warden~Taunt~Battlecry"
	requireTarget, keyWord, description = False, "Taunt", "Taunt. Battlecry: Summon a copy of this minion"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		PRINT(self, "Tomb Warden's summons a copy of the minion itself")
		minion = self.selfCopy(self.ID) if self.onBoard else TombWarden(self.Game, self.ID)
		self.Game.summonMinion(minion, self.position+1, self.ID)
		return None