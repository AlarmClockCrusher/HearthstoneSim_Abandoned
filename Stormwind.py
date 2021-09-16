from CardTypes import *
from Triggers_Auras import *
from numpy.random import choice as npchoice
from numpy.random import randint as nprandint
from numpy.random import shuffle as npshuffle
from numpy import inf as npinf

from AcrossPacks import TheCoin, Adventurers, Voidwalker, LightsJustice, Basicpowers, Upgradedpowers, SpiritWolf, DamagedGolem
from Core import MindSpike, Fireball

class Questline(Spell):
	Class, name = "Neutral", "Vanilla"
	requireTarget, mana, effects = False, 1, ""
	index = "Neutral~1~Spell~~Vanilla~~Quest"
	description = ""
	#Upper limit of secrets and quests is 5.
	#Not sure if Questlines and Quests can coexist
	def available(self):
		return not self.Game.Secrets.mainQuests[self.ID]
		
	def selectionLegit(self, target, choice=0):
		return target is None
	
	def cast(self, target=None, comment="", preferedTarget=None):
		if self.Game.GUI:
			self.Game.GUI.showOffBoardTrig(self)
		self.whenEffective(None, "byOthers", choice=0, posinHand=-2)
		# 使用后步骤，但是此时的扳机只会触发星界密使和风潮的状态移除，因为其他的使用后步骤都要求是玩家亲自打出。
		self.Game.sendSignal("SpellBeenCast", self.ID, self, None, 0, "byOthers")
	
	def played(self, target=None, choice=0, mana=0, posinHand=-2, comment=""):
		if self.Game.GUI:
			self.Game.GUI.showOffBoardTrig(self)
		self.Game.sendSignal("SpellPlayed", self.ID, self, None, mana, "", choice)
		self.Game.sendSignal("Spellboost", self.ID, self, None, mana, "", choice)
		self.Game.gathertheDead()  # At this point, the minion might be removed/controlled by Illidan/Juggler combo.
		self.whenEffective(None, '', choice, posinHand)
		self.Game.sendSignal("SpellBeenCast", self.ID, self, None, 0, "")
		self.Game.Counters.hasPlayedQuestThisGame[self.ID] = True
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		secretZone = self.Game.Secrets
		if secretZone.areaNotFull(self.ID):
			if not secretZone.mainQuests[self.ID]:
				secretZone.mainQuests[self.ID] = [self]
				for trig in self.trigsBoard: trig.connect()
				if self.Game.GUI: self.Game.GUI.heroZones[self.ID].placeSecrets()
		return None


"""Neutral Cards"""
"""Mana 1 Cards"""
class ElwynnBoar(Minion):
	Class, race, name = "Neutral", "Beast", "Elwynn Boar"
	mana, attack, health = 1, 1, 1
	index = "STORMWIND~Neutral~Minion~1~1~1~Beast~Elwynn Boar~Deathrattle"
	requireTarget, effects, description = False, "", "Deathrattle: If you had 7 Elwynn Boars die this game, equip a 15/3 Sword of Thousand Truth"
	name_CN = "埃尔文野猪"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.deathrattles = [CheckforSword(self)]

	def effCanTrig(self):
		self.effectViable = self.Game.Counters.minionsDiedThisGame[self.ID].count(ElwynnBoar) > 5
		
class CheckforSword(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		minion = self.entity
		if minion.Game.Counters.minionsDiedThisGame[minion.ID].count(ElwynnBoar) > 6:
			minion.equipWeapon(SwordofaThousandTruth(minion.Game, minion.ID))
		
	def text(self, CHN):
		return "亡语：进入休眠状态。在5个友方随从死亡后复活" if CHN \
			else "Deathrattle: Go dormant. Revive after 5 friendly minions die"

class SwordofaThousandTruth(Weapon):
	Class, name, description = "Neutral", "Sword of a Thousand Truths", "After your hero attacks, destroy your opponent's Mana Crystals"
	mana, attack, durability, effects = 10, 15, 3, ""
	index = "STORMWIND~Neutral~Weapon~10~15~3~Sword of a Thousand Truths~Legendary~Uncollectible"
	name_CN = "万千箴言之剑"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_SwordofaThousandTruth(self)]

class Trig_SwordofaThousandTruth(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["HeroAttackedMinion", "HeroAttackedHero"])
	
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject == self.entity.Game.heroes[self.entity.ID] and self.entity.onBoard
	
	def text(self, CHN):
		return "在你的英雄攻击后，摧毁你对手的法力水晶" if CHN \
			else "After your hero attacks, destroy your opponent's Mana Crystals"
	
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.Game.Manas.destroyManaCrystal(10, 3-self.entity.ID)


class Peasant(Minion):
	Class, race, name = "Neutral", "", "Peasant"
	mana, attack, health = 1, 2, 1
	index = "STORMWIND~Neutral~Minion~1~2~1~~Peasant"
	requireTarget, effects, description = False, "", "At the start of your turn, draw a card"
	name_CN = "农夫"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_Peasant(self)]

class Trig_Peasant(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["TurnStarts"])
	
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return ID == self.entity.ID and self.entity.onBoard
	
	def text(self, CHN):
		return "在你的回合开始时，抽一张牌" if CHN else "At the start of your turn, draw a card"
	
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.Game.Hand_Deck.drawCard(self.entity.ID)


class StockadesGuard(Minion):
	Class, race, name = "Neutral", "", "Stockades Guard"
	mana, attack, health = 1, 1, 3
	index = "STORMWIND~Neutral~Minion~1~1~3~~Stockades Guard~Battlecry"
	requireTarget, effects, description = True, "", "Battlecry: Give a friendly minion Taunt"
	name_CN = "监狱守卫"
	
	def targetExists(self, choice=0):
		return self.selectableFriendlyMinionExists(choice)
	
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.ID == self.ID and target != self and target.onBoard
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			target.getsEffect("Taunt")
		return target
	
"""Mana 2 Cards"""
class AuctioneerJaxon(Minion):
	Class, race, name = "Neutral", "", "Auctioneer Jaxon"
	mana, attack, health = 2, 2, 3
	index = "STORMWIND~Neutral~Minion~2~2~3~~Auctioneer Jaxon~Legendary"
	requireTarget, effects, description = False, "", "Whenever you Trade, Discover a card from your deck to draw instead"
	name_CN = "拍卖师亚克森"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.auras["Your Trade Discovers Instead"] = GameRuleAura_AuctioneerJaxon(self)
	
	def discoverDecided(self, option, case, info_RNGSync=None, info_GUISync=None):
		self.handleDiscoveredCardfromList(option, case, ls=self.Game.Hand_Deck.decks[self.ID],
										  func=lambda index, card: self.Game.Hand_Deck.drawCard(self.ID, index),
										  info_RNGSync=info_RNGSync, info_GUISync=info_GUISync)
		
class GameRuleAura_AuctioneerJaxon(GameRuleAura):
	def auraAppears(self):
		self.entity.Game.effects[self.entity.ID]["Trade Discovers Instead"] += 1
	
	def auraDisappears(self):
		self.entity.Game.effects[self.entity.ID]["Trade Discovers Instead"] -= 1


class DeeprunEngineer(Minion):
	Class, race, name = "Neutral", "", "Deeprun Engineer"
	mana, attack, health = 2, 1, 2
	index = "STORMWIND~Neutral~Minion~2~1~2~~Deeprun Engineer~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Discover a Mech. It costs (1) less"
	name_CN = "矿道工程师"
	poolIdentifier = "Mechs as Druid"
	@classmethod
	def generatePool(cls, pools):
		classCards = {s: [card for card in pools.ClassCards[s] if card.type == "Minion" and "Mech" in card.race] for s in pools.Classes}
		classCards["Neutral"] = [card for card in pools.NeutralCards if card.type == "Minion" and "Mech" in card.race]
		return ["Mechs as " + Class for Class in pools.Classes], \
			   [classCards[Class] + classCards["Neutral"] for Class in pools.Classes]
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.discoverandGenerate(DeeprunEngineer, comment, lambda : self.rngPool("Mechs as " + classforDiscover(self)))
		return None
	
	def discoverDecided(self, option, case, info_RNGSync=None, info_GUISync=None):
		self.handleDiscoverGeneratedCard(option, case, info_RNGSync, info_GUISync)
		ManaMod(option, changeby=-1).applies()


class EncumberedPackMule(Minion):
	Class, race, name = "Neutral", "Beast", "Encumbered Pack Mule"
	mana, attack, health = 2, 2, 3
	index = "STORMWIND~Neutral~Minion~2~2~3~Beast~Encumbered Pack Mule~Taunt"
	requireTarget, effects, description = False, "Taunt", "Taunt. When you draw this, add a copy of it to your hand"
	name_CN = "劳累的驮骡"
	
	def whenDrawn(self):
		self.addCardtoHand(self.selfCopy(self.ID, self), self.ID)


class Florist(Minion):
	Class, race, name = "Neutral", "", "Florist"
	mana, attack, health = 2, 2, 3
	index = "STORMWIND~Neutral~Minion~2~2~3~~Florist"
	requireTarget, effects, description = False, "", "At the end of your turn, reduce the Cost of a Nature spell in your hand by (1)"
	name_CN = "卖花女郎"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_Florist(self)]

class Trig_Florist(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["TurnEnds"])
	
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and ID == self.entity.ID
	
	def text(self, CHN):
		return "在你的回合结束时，使你手牌中的一张自然法术牌法力值消耗减少(1)点" if CHN \
			else "At the end of your turn, reduce the Cost of a Nature spell in your hand by (1)"
	
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		curGame = self.entity.Game
		ownHand = curGame.Hand_Deck.hands[self.entity.ID]
		if curGame.mode == 0:
			if curGame.picks:
				i = curGame.picks.pop(0)
			else:
				spells = [i for i, card in curGame.Hand_Deck.hands[ownHand] if card.type == "Spell" and card.school == "Nature"]
				i = npchoice(spells) if spells else -1
			if i > -1: ManaMod(ownHand[i], changeby=-1).applies()


class PandarenImporter(Minion):
	Class, race, name = "Neutral", "", "Pandaren Importer"
	mana, attack, health = 2, 1, 3
	index = "STORMWIND~Neutral~Minion~2~1~3~~Pandaren Importer~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Discover a spell that didn't start in your deck"
	name_CN = "熊猫人进口商"
	poolIdentifier = "Demons as Demon Hunter"
	@classmethod
	def generatePool(cls, pools):
		classCards = {s: [] for s in pools.ClassesandNeutral}
		for key, value in pools.MinionswithRace["Demon"].items():
			for Class in key.split('~')[1].split(','):
				classCards[Class].append(value)
		return ["Demons as " + Class for Class in pools.Classes], \
			   [classCards[Class] + classCards["Neutral"] for Class in pools.Classes]
	
	def decideSpellPool(self):
		pool = self.rngPool("Demons as " + classforDiscover(self))
		for card in self.Game.Hand_Deck.initialDecks[self.ID]:
			if card.type == "Spell":
				try: pool.remove(card)
				except: pass
		return pool
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.discoverandGenerate(PandarenImporter, comment, lambda : PandarenImporter.decideSpellPool())
		return None
	
	
class MailboxDancer(Minion):
	Class, race, name = "Neutral", "", "Mailbox Dancer"
	mana, attack, health = 2, 3, 2
	index = "STORMWIND~Neutral~Minion~2~3~2~~Mailbox Dancer~Battlecry~Deathrattle"
	requireTarget, effects, description = False, "", "Battlecry: Add a Coin to your hand. Deathrattle: Give your opponent one"
	name_CN = "邮箱舞者"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.deathrattles = [GiveOppoaCoin(self)]

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.addCardtoHand(TheCoin, self.ID)
		return None

class GiveOppoaCoin(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.addCardtoHand(TheCoin, 3-self.entity.ID)
		
	def text(self, CHN):
		return "亡语：你的对手获得一个幸运币" if CHN else "Deathrattle: Add a Coin to your opponent's hand"
	
	
class SI7Skulker(Minion):
	Class, race, name = "Neutral", "", "SI:7 Skulker"
	mana, attack, health = 2, 2, 2
	index = "STORMWIND~Neutral~Minion~2~2~2~~SI:7 Skulker~Stealth~Battlecry"
	requireTarget, effects, description = False, "Stealth", "Stealth. Battlecry: The next card you draw costs (1) less"
	name_CN = "军情七处潜伏者"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		#假设只有最终进入手牌的卡会享受减费
		SI7Skulker_Effect(self.Game, self.ID).connect()
		return None
	
class SI7Skulker_Effect:
	def __init__(self, Game, ID):
		self.Game, self.ID = Game, ID
		self.card = SI7Skulker(Game, ID)
		
	def connect(self):
		try: self.Game.trigsBoard[self.ID]["CardEntersHand"].append(self)
		except: self.Game.trigsBoard[self.ID]["CardEntersHand"] = [self]
		if self.Game.GUI: self.Game.GUI.heroZones[self.ID].addaTrig(self.card)
	
	def disconnect(self):
		try: self.Game.trigsBoard[self.ID]["CardEntersHand"].remove(self)
		except: pass
		if self.Game.GUI: self.Game.GUI.heroZones[self.ID].removeaTrig(self.card.btn)
	
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return target[0].ID == self.ID and comment == "byDrawing"
	
	def trig(self, signal, ID, subject, target, number, comment, choice=0):
		if self.canTrig(signal, ID, subject, target, number, comment):
			if self.Game.GUI: self.Game.GUI.showOffBoardTrig(self.card)
			self.effect(signal, ID, subject, target, number, comment)
	
	def text(self, CHN):
		return "抽牌后，下一张抽到的牌不再费用减(1)点" if CHN \
			else "After you draw a card, the next one won't have its Cost reduced"
	
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		ManaMod(target[0], changeby=-1).applies()
		self.disconnect()
	
	def createCopy(self, game):  #不是纯的只在回合结束时触发，需要完整的createCopy
		if self not in game.copiedObjs:  #这个扳机没有被复制过
			trigCopy = type(self)(game, self.ID)
			game.copiedObjs[self] = trigCopy
			return trigCopy
		else:  #一个扳机被复制过了，则其携带者也被复制过了
			return game.copiedObjs[self]


class StockadesPrisoner(Minion):
	Class, race, name = "Neutral", "", "Stockades Prisoner"
	mana, attack, health = 2, 5, 4
	index = "STORMWIND~Neutral~Minion~2~5~4~~Stockades Prisoner"
	requireTarget, effects, description = False, "", "Starts Dormant. After you play 3 cards, this awakens"
	name_CN = "监狱囚徒"
	#出现即休眠的随从的played过程非常简单
	def played(self, target=None, choice=0, mana=0, posinHand=-2, comment=""):
		self.statReset(self.attack_Enchant, self.health_max)
		self.appears(firstTime=True)  #打出时一定会休眠，同时会把Game.minionPlayed变为None
		return None  #没有目标可以返回
	
	def appears(self, firstTime=True):
		self.onBoard = True
		self.inHand = self.inDeck = self.dead = False
		self.enterBoardTurn = self.Game.numTurn
		self.mana = type(self).mana  #Restore the minion's mana to original value.
		self.decideAttChances_base()  #Decide base att chances, given Windfury and Mega Windfury
		#没有光环，目前炉石没有给随从人为添加光环的效果, 不可能在把手牌中获得的扳机带入场上，因为会在变形中丢失
		#The buffAuras/hasAuras will react to this signal.
		if firstTime:  #首次出场时会进行休眠，而且休眠状态会保持之前的随从buff
			self.Game.transform(self, ImprisonedStockadesPrisoner(self.Game, self.ID, self), firstTime=True)
		else:  #只有不是第一次出现在场上时才会执行这些函数
			if self.btn:
				self.btn.isPlayed, self.btn.card = True, self
				self.btn.placeIcons()
				self.btn.statChangeAni()
				self.btn.effectChangeAni()
			for aura in self.auras.values(): aura.auraAppears()
			for trig in self.trigsBoard + self.deathrattles: trig.connect()
			self.Game.sendSignal("MinionAppears", self.ID, self, None, 0, comment=firstTime)
	
	def awakenEffect(self):
		pass

class ImprisonedStockadesPrisoner(Dormant):
	Class, school, name = "Neutral", "", "Imprisoned Stockades Prisoner"
	description = "Awakens after you play 3 cards"
	def __init__(self, Game, ID, minionInside=None):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_ImprisonedStockadesPrisoner(self)]
		self.minionInside = minionInside
		if minionInside:  #When creating a copy, this is left blank temporarily
			self.index = minionInside.index
	
	def assistCreateCopy(self, Copy):
		Copy.minionInside = self.minionInside.createCopy(Copy.Game)
		Copy.name, Copy.Class, Copy.description = self.name, self.Class, self.description

class Trig_ImprisonedStockadesPrisoner(Trig_Countdown):
	def __init__(self, entity):
		super().__init__(entity, ["MinionBeenPlayed", "SpellBeenPlayed", "WeaponBeenPlayed", "HeroBeenPlayed"])
		self.counter = 3
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject.ID == self.entity.ID  #会在我方回合开始时进行苏醒
	
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		if self.counter < 1:
			#假设唤醒的Imprisoned Vanilla可以携带buff
			self.entity.Game.transform(self.entity, self.entity.minionInside, firstTime=False)
			

"""Mana 3 Cards"""
class EntrappedSorceress(Minion):
	Class, race, name = "Neutral", "", "Entrapped Sorceress"
	mana, attack, health = 3, 3, 4
	index = "STORMWIND~Neutral~Minion~3~3~4~~Entrapped Sorceress~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: If you control a Quest, Discover a spell"
	name_CN = "被困的女巫"
	poolIdentifier = "Druid Spells"
	@classmethod
	def generatePool(cls, pools):
		return [Class + " Spells" for Class in pools.Classes], \
			   [[card for card in cards if card.type == "Spell"] for cards in pools.ClassCards.values()]
	
	def effCanTrig(self):
		self.effectViable = self.Game.Secrets.mainQuests[self.ID] != []
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if self.Game.Secrets.mainQuests[self.ID] or self.Game.Secrets.sideQuests[self.ID]:
			self.discoverandGenerate(EntrappedSorceress, comment, lambda : self.rngPool(classforDiscover(self) + " Spells"))
		return None
	

class EnthusiasticBanker(Minion):
	Class, race, name = "Neutral", "", "Enthusiastic Banker"
	mana, attack, health = 3, 2, 3
	index = "STORMWIND~Neutral~Minion~3~2~3~~Enthusiastic Banker"
	requireTarget, effects, description = False, "", "At the end of your turn, store a card from your deck. Deathrattle: Add the stored cards to your hand"
	name_CN = "热情的柜员"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_EnthusiasticBanker(self)]
		self.deathrattles = [AddStoredCardstoHand(self)]

class Trig_EnthusiasticBanker(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["TurnEnds"])
	
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and ID == self.entity.ID
	
	def text(self, CHN):
		return "在你的回合结束时，储存一张你牌库中的牌" if CHN else "At the end of your turn, store a card from your deck"
	
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		deckSize = len(self.entity.Game.Hand_Deck.decks[self.entity.ID])
		if deckSize:
			card = self.entity.Game.Hand_Deck.extractfromDeck(nprandint(deckSize), self.entity.ID)[0]
			for trig in self.entity.deathrattles:
				if isinstance(trig, AddStoredCardstoHand):
					trig.cardsStored.append(card)
					
class AddStoredCardstoHand(Deathrattle_Minion):
	def __init__(self, entity):
		super().__init__(entity)
		self.cardsStored = []
	
	def text(self, CHN):
		return "亡语：将储存的牌置入你的手牌" if CHN else "Deathrattle: Add the stored cards to your hand"
	
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		if self.cardsStored: self.entity.addCardtoHand(self.cardsStored, self.entity.ID)
	
	def selfCopy(self, recipient):
		trig = type(self)(recipient)
		trig.cardsStored = [card.selfCopy(recipient.ID, recipient) for card in self.cardsStored]
		return trig

	def createCopy(self, game):
		if self not in game.copiedObjs:  #这个扳机没有被复制过
			entityCopy = self.entity.createCopy(game)
			trigCopy = type(self)(entityCopy)
			trigCopy.cardsStored = [card.createCopy(game) for card in self.cardsStored]
			game.copiedObjs[self] = trigCopy
			return trigCopy
		else:  #一个扳机被复制过了，则其携带者也被复制过了
			return game.copiedObjs[self]


class ImpatientShopkeep(Minion):
	Class, race, name = "Neutral", "", "Impatient Shopkeep"
	mana, attack, health = 3, 3, 3
	index = "STORMWIND~Neutral~Minion~3~3~3~~Impatient Shopkeep~Rush~Tradeable"
	requireTarget, effects, description = False, "Rush", "Tradeable, Rush"
	name_CN = "不耐烦的店长"


class NorthshireFarmer(Minion):
	Class, race, name = "Neutral", "", "Northshire Farmer"
	mana, attack, health = 3, 3, 3
	index = "STORMWIND~Neutral~Minion~3~3~3~~Northshire Farmer~Battlecry"
	requireTarget, effects, description = True, "", "Battlecry: Choose a friendly Beast. Shuffle three 3/3 copies into your deck"
	name_CN = "北郡农民"
	
	def targetExists(self, choice=0):
		return self.selectableFriendlyMinionExists()
	
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard and target.ID == self.ID and "Beast" in target.race
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			self.Game.Hand_Deck.shuffleintoDeck([target.selfCopy(self.ID, self, attack=3, health=3) for i in range(3)], initiatorID=self.ID)
		return target


class PackageRunner(Minion):
	Class, race, name = "Neutral", "", "Package Runner"
	mana, attack, health = 3, 5, 6
	index = "STORMWIND~Neutral~Minion~3~5~6~~Package Runner"
	requireTarget, effects, description = False, "Can't Attack", "Can only attack if you have at least 8 cards in hand"
	name_CN = "包裹速递员"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.auras["Toggle Actionable"] = EffectAura_PackageRunner(self)

class EffectAura_PackageRunner:
	def __init__(self, entity):
		self.entity = entity
		self.signals = ["CardLeavesHand", "CardEntersHand"]
		self.on = False
	
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and ID == self.entity.ID
	
	def trig(self, signal, ID, subject, target, number, comment, choice=0):
		minion = self.entity
		if minion.onBoard and ID == minion.ID:
			eightCardsinHand = len(minion.Game.Hand_Deck.hands[minion.ID]) > 7
			if not eightCardsinHand and self.on:
				self.on = False
				minion.effects["Can't Attack"] += 1
			elif eightCardsinHand and not self.on:
				self.on = True
				minion.effects["Can't Attack"] -= 1
	
	def auraAppears(self):
		minion = self.entity
		if len(minion.Game.Hand_Deck.hands[minion.ID]) > 7:
			self.on = True
			minion.effects["Can't Attack"] -= 1
		for sig in self.signals:
			try: minion.Game.trigsBoard[minion.ID][sig].append(self)
			except: minion.Game.trigsBoard[minion.ID][sig] = [self]
	
	def auraDisappears(self):
		if self.on: self.entity.effects["Can't Attack"] += 1
		for sig in self.signals:
			try: self.entity.Game.trigsBoard[self.entity.ID][sig].remove(self)
			except: pass
	
	def selfCopy(self, recipient):  #The recipientMinion is the minion that deals the Aura.
		return type(self)(recipient)
	
	def createCopy(self, game):
		if self not in game.copiedObjs:  #这个光环没有被复制过
			entityCopy = self.entity.createCopy(game)
			Copy = self.selfCopy(entityCopy)
			game.copiedObjs[self] = Copy
			Copy.on = self.on
			return Copy
		else:
			return game.copiedObjs[self]


class RustrotViper(Minion):
	Class, race, name = "Neutral", "Beast", "Rustrot Viper"
	mana, attack, health = 3, 3, 4
	index = "STORMWIND~Neutral~Minion~3~3~4~Beast~Rustrot Viper~Battlecry~Tradeable"
	requireTarget, effects, description = False, "", "Tradeable. Battlecry: Destroy your opponent's weapon"
	name_CN = "锈烂蝰蛇"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		for weapon in self.Game.weapons[3 - self.ID]:
			weapon.destroyed()
		return None


class TravelingMerchant(Minion):
	Class, race, name = "Neutral", "", "Traveling Merchant"
	mana, attack, health = 3, 2, 3
	index = "STORMWIND~Neutral~Minion~3~2~3~~Traveling Merchant~Battlecry~Tradeable"
	requireTarget, effects, description = False, "", "Tradeable. Battlecry: Gain +1/+1 for each other friendly minion you control"
	name_CN = "旅行商人"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if not self.dead and (self.onBoard or self.inHand):
			num = len(self.Game.minionsonBoard(self.ID, exclude=self))
			if num: self.buffDebuff(num, num)
		return None


class TwoFacedInvestor(Minion):
	Class, race, name = "Neutral", "", "Two-Faced Investor"
	mana, attack, health = 3, 2, 4
	index = "STORMWIND~Neutral~Minion~3~2~4~~Two-Faced Investor"
	requireTarget, effects, description = False, "", "At the end of your turn, reduce the Cost of a card in your hand by (1). (50% chance to increase)"
	name_CN = "双面投资者"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_TwoFacedInvestor(self)]

class Trig_TwoFacedInvestor(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["TurnEnds"])
	
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and ID == self.entity.ID
	
	def text(self, CHN):
		return "在你的回合结束时，使你的一张手牌的法力值消耗减少(1)点。(50%的几率改为消耗增加)" if CHN \
			else "At the end of your turn, reduce the Cost of a card in your hand by (1). (50% chance to increase)"
	
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		ownHand = self.entity.Game.Hand_Deck.hands[self.entity.ID]
		if ownHand:
			ManaMod(npchoice(ownHand), changeby=2*nprandint(2)-1).applies()
		

class FlightmasterDungar(Minion):
	Class, race, name = "Neutral", "", "Flightmaster Dungar"
	mana, attack, health = 3, 3, 3
	index = "STORMWIND~Neutral~Minion~3~3~3~~Flightmaster Dungar~Battlecry~Legendary"
	requireTarget, effects, description = False, "", "Battlecry: Choose a flightpath and go Dormant. Awaken with a bonus when you complete it!"
	name_CN = "飞行管理员杜加尔"
	
	def goDormant(self, flightpath):
		newMinion = FlightmasterDungar_Dormant(self.Game, self.ID, self) if flightpath else None
		if newMinion:
			if flightpath == Westfall:
				newMinion.trigsBoard.append(Trig_FlightmasterDungar_Westfall(newMinion))
			elif flightpath == Ironforge:
				newMinion.trigsBoard.append(Trig_FlightmasterDungar_Ironforge(newMinion))
			elif flightpath == EasternPlaguelands:
				newMinion.trigsBoard.append(Trig_FlightmasterDungar_EasternPlaguelands(newMinion))
			self.Game.transform(self, newMinion)
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		self.chooseFixedOptions(FlightmasterDungar, comment,
								options=[Westfall(ID=self.ID), Ironforge(ID=self.ID), EasternPlaguelands(ID=self.ID)])
		return None
	
	def discoverDecided(self, option, case, info_RNGSync=None, info_GUISync=None):
		optionType = type(option)
		if case != "Guided": self.Game.picks_Backup.append((info_RNGSync, info_GUISync, case == "Random", optionType))
		FlightmasterDungar.goDormant(self, optionType)
		
class Westfall(Option):
	name, type = "Westfall", "Option_Spell"
	mana, attack, health = 0, -1, -1

class Ironforge(Option):
	name, type = "Ironforge", "Option_Spell"
	mana, attack, health = 0, -1, -1
	
class EasternPlaguelands(Option):
	name, type = "Eastern Plaguelands", "Option_Spell"
	mana, attack, health = 0, -1, -1
	
class FlightmasterDungar_Dormant(Dormant):
	Class, school, name = "Neutral", "", "Sleeping Naralex"
	description = "Dormant. Awaken with bonus!"
	def __init__(self, Game, ID, minionInside=None):
		super().__init__(Game, ID)
		#self.trigsBoard = [Trig_FlightmasterDungar_Westfall(self)]
		self.minionInside = minionInside
		if minionInside:  #When creating a copy, this is left blank temporarily
			self.Class = minionInside.Class
			self.name = "Dormant " + minionInside.name
			self.description = minionInside.description
			self.index = minionInside.index
	
	def assistCreateCopy(self, Copy):
		Copy.minionInside = self.minionInside.createCopy(Copy.Game)
		Copy.name, Copy.Class, Copy.description = self.name, self.Class, self.description

class Trig_FlightmasterDungar_Westfall(Trig_Countdown):
	def __init__(self, entity):
		super().__init__(entity, ["TurnStarts"])
		self.counter = 1
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and ID == self.entity.ID  #会在我方回合开始时进行苏醒
	
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		if self.counter < 1:
			self.entity.Game.transform(self.entity, self.entity.minionInside)
			self.entity.summon(npchoice(Adventurers)(self.entity.Game, self.entity.ID), self.entity.pos+1)

class Trig_FlightmasterDungar_Ironforge(Trig_Countdown):
	def __init__(self, entity):
		super().__init__(entity, ["TurnStarts"])
		self.counter = 3
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and ID == self.entity.ID  #会在我方回合开始时进行苏醒
	
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		if self.counter < 1:
			heal = 10 * (2 ** self.entity.countHealDouble())
			self.entity.restoresHealth(self.entity.Game.heroes[self.entity.ID], heal)
		
class Trig_FlightmasterDungar_EasternPlaguelands(Trig_Countdown):
	def __init__(self, entity):
		super().__init__(entity, ["TurnStarts"])
		self.counter = 5
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and ID == self.entity.ID  #会在我方回合开始时进行苏醒
	
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		if self.counter < 1:
			side, game = 3 - self.entity.ID, self.entity.Game
			for num in range(12):
				objs = game.charsAlive(side)
				if objs: self.entity.dealsDamage(npchoice(objs), 1)
				else: break


class Nobleman(Minion):
	Class, race, name = "Neutral", "", "Nobleman"
	mana, attack, health = 3, 2, 3
	index = "STORMWIND~Neutral~Minion~3~2~3~~Nobleman~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Create a Golden copy of a random card in your hand"
	name_CN = "贵族"

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		ownHand = self.Game.Hand_Deck.hands[self.ID]
		if ownHand: self.addCardtoHand(npchoice(ownHand).selfCopy(self.ID, self), self.ID)
		return None
	
	
"""Mana 4 Cards"""
class Cheesemonger(Minion):
	Class, race, name = "Neutral", "", "Cheesemonger"
	mana, attack, health = 4, 3, 6
	index = "STORMWIND~Neutral~Minion~4~3~6~~Cheesemonger"
	requireTarget, effects, description = False, "", "Whenever your opponent casts a spell, add a spell with the same Cost to your hand"
	name_CN = "奶酪商贩"
	poolIdentifier = "0-Cost Spells"
	@classmethod
	def generatePool(cls, pools):
		spells = {}
		for Class in pools.Classes:
			for card in pools.ClassCards[Class]:
				if card.type == "Spell":
					try: spells[card.mana].append(card)
					except: spells[card.mana] = [card]
		return ["%d-Cost Spells" % cost for cost in spells.keys()], list(spells.values())
	
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_Cheesemonger(self)]

class Trig_Cheesemonger(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["SpellBeenPlayed"])
	
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and ID != self.entity.ID
	
	def text(self, CHN):
		return "每当你的对手施放一个法术，随机将一张法力值消耗相同的法术牌置入你的手牌" if CHN \
			else "Whenever your opponent casts a spell, add a spell with the same Cost to your hand"
	
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		try: spell = npchoice(self.rngPool("%d-Cost Spells" % number))
		except: spell = None
		if spell: self.entity.addCardtoHand(spell, self.entity.ID)


class GuildTrader(Minion):
	Class, race, name = "Neutral", "", "Guild Trader"
	mana, attack, health = 4, 3, 4
	index = "STORMWIND~Neutral~Minion~4~3~4~~Guild Trader~Spell Damage~Tradeable"
	requireTarget, effects, description = False, "Spell Damage_2", "Tradeable, Spell Damage +2"
	name_CN = "工会商人"
		

class RoyalLibrarian(Minion):
	Class, race, name = "Neutral", "", "Royal Librarian"
	mana, attack, health = 4, 3, 4
	index = "STORMWIND~Neutral~Minion~4~3~4~~Royal Librarian~Battlecry~Tradeable"
	requireTarget, effects, description = True, "", "Tradeable. Battlecry: Silence a minion"
	name_CN = "王室图书管理员"

	def targetExists(self, choice=0):
		return self.selectableMinionExists()
	
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard and target != self
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target: target.getsSilenced()
		return target
	
	
class SpiceBreadBaker(Minion):
	Class, race, name = "Neutral", "", "Spice Bread Baker"
	mana, attack, health = 4, 3, 2
	index = "STORMWIND~Neutral~Minion~4~3~2~~Spice Bread Baker~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Restore Health to your hero equal to your hand size"
	name_CN = "香料面包师"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		heal = len(self.Game.Hand_Deck.hands[self.ID]) * (2 ** self.countHealDouble())
		if heal: self.restoresHealth(self.Game.heroes[self.ID], heal)
		return None


class StubbornSuspect(Minion):
	Class, race, name = "Neutral", "", "Stubborn Suspect"
	mana, attack, health = 4, 3, 3
	index = "STORMWIND~Neutral~Minion~4~3~3~~Stubborn Suspect~Deathrattle"
	requireTarget, effects, description = False, "", "Deathrattle: Summon a random 3-Cost minion"
	name_CN = "顽固的嫌疑人"
	poolIdentifier = "3-Cost Minions to Summon"
	@classmethod
	def generatePool(cls, pools):
		return "3-Cost Minions to Summon", pools.MinionsofCost[3]
	
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.deathrattles = [SummonaRandom3Cost(self)]

class SummonaRandom3Cost(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.summon(npchoice(self.rngPool("3-Cost Minions to Summon"))(self.entity.Game, self.entity.ID), self.entity.pos+1)
		
	def text(self, CHN):
		return "亡语：随机召唤一个法力值消耗为(3)的随从" if CHN else "Deathrattle: Summon a random 3-Cost minion"


""""Mana 5 Cards"""
class LionsGuard(Minion):
	Class, race, name = "Neutral", "", "Lion's Guard"
	mana, attack, health = 5, 4, 6
	index = "STORMWIND~Neutral~Minion~5~4~6~~Lion's Guard~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: If you have 15 or less Health, gain +2/+4 and Taunt"
	name_CN = "暴风城卫兵"
	
	def effCanTrig(self):
		self.effectViable = self.Game.heroes[self.ID].health < 16
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if self.onBoard and self.Game.heroes[self.ID].health < 16:
			self.buffDebuff(2, 4)
			self.getsEffect("Taunt")
		return None


class StormwindGuard(Minion):
	Class, race, name = "Neutral", "", "Stormwind Guard"
	mana, attack, health = 5, 4, 5
	index = "STORMWIND~Neutral~Minion~5~4~5~~Stormwind Guard~Taunt~Battlecry"
	requireTarget, effects, description = False, "Taunt", "Taunt. Battlecry: Give adjacent minions +1/+1"
	name_CN = "暴风城卫兵"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if self.onBoard:
			neighbors = self.Game.neighbors2(self)[0]
			for minion in neighbors: minion.buffDebuff(1, 1)
		return None


class BattlegroundBattlemaster(Minion):
	Class, race, name = "Neutral", "", "Battleground Battlemaster"
	mana, attack, health = 6, 5, 5
	index = "STORMWIND~Neutral~Minion~6~5~5~~Battleground Battlemaster"
	requireTarget, effects, description = False, "", "Adjacent minions have Windfury"
	name_CN = "战场军官"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.auras["Adjacent minions have Windfury"] = EffectAura_Adjacent(self, "Windfury")


class CityArchitect(Minion):
	Class, race, name = "Neutral", "", "City Architect"
	mana, attack, health = 6, 4, 4
	index = "STORMWIND~Neutral~Minion~6~4~4~~City Architect~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Summon two 0/5 Castle Walls with Taunt"
	name_CN = "城市建筑师"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		pos = (self.pos, "leftandRight") if self.onBoard else (-1, "totheRightEnd")
		self.summon([CastleWall(self.Game, self.ID) for i in range(2)], pos)
		return None

class CastleWall(Minion):
	Class, race, name = "Neutral", "", "Castle Wall"
	mana, attack, health = 2, 0, 5
	index = "STORMWIND~Neutral~Minion~2~0~5~~Castle Wall~Taunt~Uncollectible"
	requireTarget, effects, description = False, "Taunt", "Taunt"
	name_CN = "城堡石墙"


class CorneliusRoame(Minion):
	Class, race, name = "Neutral", "", "Cornelius Roame"
	mana, attack, health = 6, 4, 5
	index = "STORMWIND~Neutral~Minion~6~4~5~~Cornelius Roame~Legendary"
	requireTarget, effects, description = False, "", "At the start and end of each player's turn, draw a card"
	name_CN = "考内留斯·罗姆"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_CorneliusRoame(self)]

class Trig_CorneliusRoame(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["TurnStarts", "TurnEnds"])
	
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard
	
	def text(self, CHN):
		return "在每个玩家的回合开始和结束时，抽一张牌" if CHN \
			else "At the start and end of each player's turn, draw a card"
	
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.Game.Hand_Deck.drawCard(self.entity.ID)
		
		
class LadyPrestor(Minion):
	Class, race, name = "Neutral", "", "Lady Prestor"
	mana, attack, health = 6, 6, 7
	index = "STORMWIND~Neutral~Minion~6~6~7~~Lady Prestor~Battlecry~Legendary"
	requireTarget, effects, description = False, "", "Battlecry: Transform minions in your deck into random Dragons. (They keep their original stats and Cost)"
	name_CN = "普瑞斯托女士"
	poolIdentifier = "Dragons"
	@classmethod
	def generatePool(cls, pools):
		return "Dragons", pools.MinionswithRace["Dragon"]
	
	#不知道拉法姆的替换手牌、牌库和迦拉克隆会有什么互动。假设不影响主迦拉克隆。
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		game = self.Game
		ownDeck = game.Hand_Deck.decks[self.ID]
		minions = [i for i, card in enumerate(ownDeck) if card.type == "Minion"]
		if minions:
			dragons = npchoice(self.rngPool("Dragons"), len(minions), replace=True)
			for i, newCard in zip(minions, dragons):
				game.Hand_Deck.extractfromDeck(i, self.ID)
				card = newCard(game, self.ID)
				ownDeck.insert(i, card)
				card.entersDeck()
		return None
		

"""Mana 7+ cards"""
class MoargForgefiend(Minion):
	Class, race, name = "Neutral", "Demon", "Mo'arg Forgefiend"
	mana, attack, health = 8, 8, 8
	index = "STORMWIND~Neutral~Minion~8~8~8~Demon~Mo'arg Forgefiend~Taunt~Deatthrattle"
	requireTarget, effects, description = False, "Taunt", "Taunt. Deathrattle: Gain 8 Armor"
	name_CN = "莫尔葛熔魔"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.deathrattles = [Gain8Armor(self)]

class Gain8Armor(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.Game.heroes[self.entity.ID].gainsArmor(8)
		
	def text(self, CHN):
		return "亡语：获得8点护甲值" if CHN else "Deathrattle: 获得8点护甲值"


class VarianKingofStormwind(Minion):
	Class, race, name = "Neutral", "", "Varian, King of Stormwind"
	mana, attack, health = 8, 7, 7
	index = "STORMWIND~Neutral~Minion~8~7~7~~Varian, King of Stormwind~Battlecry~Legendary"
	requireTarget, effects, description = False, "", "Battlecry: Draw a Rush minion to gain Rush. Repeat for Taunt and Divine Shield"
	name_CN = "瓦里安，暴风城国王"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if curGame.mode == 0:
			"""Draw the Rush minion"""
			#在挑选Rush的时候需要先把有Rush，Taunt和Divine Shield的都找到（三个列表可以有交集）
			#挑Rush的时候随意，但是需要把挑出来的这个随从从三个列表之路移除。之后挑Taunt的时候，如果列表里还有Taunt，则直接挑；否则检测Rush的那个随从是否有Taunt
			#如果这个Rush随从有Taunt，则说明该随从是唯一拥有Taunt的，只是先一步被Rush挑走了。如果Rush还有的选，则Rush可以重新挑选（同样在3个列表之中移除），并把这个既有Rush也有Taunt的随从让给Taunt
			#在前面两个都挑完之后，看Divine是否存在，如果有，则在Divine中挑选；如果Divine没有，则检测Rush和Taunt选中的随从是否有Divine（它们是唯二可能有Divine的随从了）
			#如果Rush和Taunt的随从都有Divine，则随机一个给Divine，然后自己再选。如果只有一个有，则给Divine之后自己再重新选。如果都没有再随意。
			#然后就可以确定第一个Rush的挑选序号
			ownDeck = curGame.Hand_Deck.decks[self.ID]
			pool_Rush = [card for card in ownDeck if card.type == "Minion" and card.effects["Rush"] > 0]
			pool_Taunt = [card for card in ownDeck if card.type == "Minion" and card.effects["Taunt"] > 0]
			pool_Divine = [card for card in ownDeck if card.type == "Minion" and card.effects["Divine Shield"] > 0]
			#When first picking a Rush minion, the choice is not restricted
			minion_Rush = npchoice(pool_Rush) if pool_Rush else None
			if minion_Rush: #The Rush minion picked must be excluded from the the remaining Rush, Taunt and Divine pool
				pool_Rush.remove(minion_Rush)
				if minion_Rush in pool_Taunt: pool_Taunt.remove(minion_Rush)
				if minion_Rush in pool_Divine: pool_Divine.remove(minion_Rush)
			#When picking the Taunt minion, if there is still a pool of Taunt minion, nothing happens; if the remain pool is empty,
			# and the Rush minion has Taunt and there is a remaining pool of Rush, then the Taunt will take the chosen Rush minion.
			# The Rush minion will need to pick another from the remaining Rush pool
			minion_Taunt = npchoice(pool_Taunt) if pool_Taunt else None
			if minion_Taunt:
				pool_Taunt.remove(minion_Taunt)
				if minion_Taunt in pool_Rush: pool_Rush.remove(minion_Taunt)
				if minion_Taunt in pool_Divine: pool_Divine.remove(minion_Taunt)
			elif minion_Rush and minion_Rush.effects["Taunt"] > 0 and pool_Rush:
				minion_Taunt = minion_Rush
				minion_Rush = npchoice(pool_Rush)
				pool_Rush.remove(minion_Rush)
				if minion_Rush in pool_Taunt: pool_Taunt.remove(minion_Rush)
				if minion_Rush in pool_Divine: pool_Divine.remove(minion_Rush)
			
			#If there isn't a remaining pool of Divine minions, and the picked Rush minion has Divine Shield,
			# and the picked Taunt minion could also have Taunt.
			if not pool_Divine:
				divineCanTakeRush = minion_Rush and minion_Rush.effects["Divine Shield"] > 0 and pool_Rush
				divineCanTakeTaunt = minion_Taunt and minion_Taunt.effects["Divine Shield"] > 0 and pool_Taunt
				if divineCanTakeRush and (not divineCanTakeTaunt or nprandint(2)):
					pool_Divine.append(minion_Rush)
					minion_Rush = npchoice(pool_Rush)
					
			if minion_Rush:
				self.Game.Hand_Deck.drawCard(self.ID, ownDeck.index(minion_Rush))
				self.getsEffect("Rush")
				
			"""Draw the Taunt minion"""
			#在挑选Taunt的时候把有Taunt和Divine Shield的都找到（两份个列表可以有交集）
			#挑Taunt的时候随意，但是需要把挑出来的这个随从从三个列表之路移除。之后挑Divine的时候，如果列表里还有Divine，则直接挑；否则检测Taunt的那个随从是否有Divine
			#如果这个Taunt随从有Divine，则说明该随从是唯一拥有Divine的，只是先一步被Taunt挑走了。如果Rush还有的选，则Rush可以重新挑选（同样在3个列表之中移除），并把这个既有Rush也有Taunt的随从让给Taunt
			pool_Taunt = [card for card in ownDeck if card.type == "Minion" and card.effects["Taunt"] > 0]
			pool_Divine = [card for card in ownDeck if card.type == "Minion" and card.effects["Divine Shield"] > 0]
			#When first picking a Rush minion, the choice is not restricted
			minion_Taunt = npchoice(pool_Taunt) if pool_Taunt else None
			if minion_Taunt:  #The Rush minion picked must be excluded from the the remaining Rush, Taunt and Divine pool
				pool_Taunt.remove(minion_Taunt)
				if minion_Taunt in pool_Divine: pool_Divine.remove(minion_Taunt)
			minion_Divine = npchoice(pool_Divine) if pool_Divine else None
			if not minion_Divine and minion_Taunt and minion_Taunt.effects["Divine Shield"] > 0 and pool_Taunt:
				minion_Taunt = npchoice(pool_Taunt)
				
			if minion_Taunt:
				self.Game.Hand_Deck.drawCard(self.ID, ownDeck.index(minion_Taunt))
				self.getsEffect("Taunt")
			
			pool_Divine = [i for i, card in enumerate(ownDeck) if card.type == "Minion" and card.effects["Divine Shield"] > 0]
			if pool_Divine:
				self.Game.Hand_Deck.drawCard(self.ID, npchoice(pool_Divine))
				self.getsEffect("Divine Shield")
		return None


class GoldshireGnoll(Minion):
	Class, race, name = "Neutral", "", "Goldshire Gnoll"
	mana, attack, health = 10, 5, 4
	index = "STORMWIND~Neutral~Minion~10~5~4~~Goldshire Gnoll~Rush"
	requireTarget, effects, description = False, "Rush", "Rush. Costs (1) less for each other card in your hand"
	name_CN = "闪金镇豺狼人"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsHand = [Trig_GoldshireGnoll(self)]
	
	def selfManaChange(self):
		if self.inHand:
			self.mana -= len(self.Game.Hand_Deck.hands[self.ID]) - 1
			self.mana = max(0, self.mana)

class Trig_GoldshireGnoll(TrigHand):
	def __init__(self, entity):
		super().__init__(entity, ["CardLeavesHand", "CardEntersHand"])
	
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.inHand and ID == self.entity.ID
	
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.Game.ManaHandler.calcMana_Single(self.entity)


"""Demon Hunter Cards"""
class Trig_FinalShowdown(Trig_Quest):
	def __init__(self, entity):
		super().__init__(entity, ["CardDrawn", "CardEntersHand", "NewTurnStarts"])
		self.numNeeded, self.newQuest, self.reward = 4, GainMomentum, None
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return signal.startswith('N') or (ID == self.entity.ID and
										  ((signal == "CardDrawn" and "Casts When Drawn" in target[0].index)
										   or (signal == "CardEntersHand" and comment == "byDrawing")))
	
	def handleCounter(self, signal, ID, subject, target, number, comment, choice=0):
		if signal.startswith('N'): self.counter = 0
		else: self.counter += 1
	
	def questEffect(self, quest, game, ID):
		for card in game.Hand_Deck.hands[ID]:
			ManaMod(card, changeby=-1).applies()

class Trig_GainMomentum(Trig_FinalShowdown):
	def __init__(self, entity):
		super().__init__(entity)
		self.numNeeded, self.newQuest, self.reward = 5, ClosethePortal, None
		
class Trig_ClosethePortal(Trig_FinalShowdown):
	def __init__(self, entity):
		super().__init__(entity)
		self.numNeeded, self.newQuest, self.reward = 5, None, DemonslayerKurtrus
		
class FinalShowdown(Questline):
	Class, name = "Demon Hunter", "Final Showdown"
	requireTarget, mana, effects = False, 1, ""
	index = "STORMWIND~Demon Hunter~Spell~1~~Final Showdown~~Questline~Legendary"
	description = "Questline: Draw 4 cards in one turn. Reward: Reduce the Cost of the cards in your hand by (1)"
	name_CN = "一决胜负"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_FinalShowdown(self)]

class GainMomentum(Questline):
	Class, name = "Demon Hunter", "Gain Momentum"
	requireTarget, mana, effects = False, -1, ""
	index = "STORMWIND~Demon Hunter~Spell~0~~Gain Momentum~~Questline~Legendary~Uncollectible"
	description = "Questline: Draw 5 cards in one turn. Reward: Reduce the Cost of the cards in your hand by (1)"
	name_CN = "汲取动力"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_GainMomentum(self)]

class ClosethePortal(Questline):
	Class, name = "Demon Hunter", "Close the Portal"
	requireTarget, mana, effects = False, -1, ""
	index = "STORMWIND~Demon Hunter~Spell~0~~Close the Portal~~Questline~Legendary~Uncollectible"
	description = "Questline: Draw 5 cards in one turn. Reward: Demonslayer Kurtrus"
	name_CN = "关闭传送门"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_ClosethePortal(self)]

class DemonslayerKurtrus(Minion):
	Class, race, name = "Demon Hunter", "", "Demonslayer Kurtrus"
	mana, attack, health = 5, 7, 7
	index = "STORMWIND~Demon Hunter~Minion~5~7~7~~Demonslayer Kurtrus~Battlecry~Legendary~Uncollectible"
	requireTarget, effects, description = False, "", "Battlecry: For the rest of the game, cards you draw cost (2) less"
	name_CN = "屠魔者库尔特鲁斯"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		DemonslayerKurtrus_Effect(self.Game, self.ID).connect()
		return None

class DemonslayerKurtrus_Effect:
	def __init__(self, Game, ID):
		self.Game, self.ID = Game, ID
		self.card = DemonslayerKurtrus(Game, ID)
		self.counter = 2
		
	def connect(self):
		try: trigs = self.Game.trigsBoard[self.ID]["CardEntersHand"]
		except: trigs = self.Game.trigsBoard[self.ID]["CardEntersHand"] = []
		trig = next((trig for trig in trigs if isinstance(trig, DemonslayerKurtrus_Effect)), None)
		if trig:
			trig.counter += 2
			if trig.card.btn: trig.card.btn.trigAni(trig.counter)
		else:
			self.Game.trigAuras[self.ID].append(self)
			trigs.append(self)
			if self.Game.GUI: self.Game.GUI.heroZones[self.ID].addaTrig(self.card, text='2')
	
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return target[0].ID == self.ID
	
	def trig(self, signal, ID, subject, target, number, comment, choice=0):
		if self.canTrig(signal, ID, subject, target, number, comment):
			if self.Game.GUI: self.Game.GUI.showOffBoardTrig(self.card, animationType='')
			self.effect(signal, ID, subject, target, number, comment)
			
	def text(self, CHN):
		return "在本局对战的剩余时间内，在你召唤一个白银之手新兵后，使其获得圣盾" if CHN \
			else "For the rest of the game, after you summon a Silver Hand Recruit, give it Divine Shield"
	
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		ManaMod(target[0], changeby=-self.counter).applies()
	
	def createCopy(self, game):  #不是纯的只在回合结束时触发，需要完整的createCopy
		if self not in game.copiedObjs:  #这个扳机没有被复制过
			trigCopy = type(self)(game, self.ID)
			game.copiedObjs[self] = trigCopy
			trigCopy.counter = self.counter
			return trigCopy
		else:  #一个扳机被复制过了，则其携带者也被复制过了
			return game.copiedObjs[self]


class Metamorfin(Minion):
	Class, race, name = "Demon Hunter", "Murloc", "Metamorfin"
	mana, attack, health = 1, 1, 2
	index = "STORMWIND~Demon Hunter~Minion~1~1~2~Murloc~Metamorfin~Taunt~Battlecry"
	requireTarget, effects, description = False, "Taunt", "Taunt. Battlecry: If you've cast a Fel spell this turn, gain +2/+2"
	name_CN = "魔变鱼人"

	def effCanTrig(self):
		self.effectViable = any(card.school == "Fel" for card in self.Game.Counters.cardsPlayedEachTurn[self.ID][-1])
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if any(card.school == "Fel" for card in self.Game.Counters.cardsPlayedEachTurn[self.ID][-1]):
			self.buffDebuff(2, 2)
		return None
		
		
class SigilofAlacrity(Spell):
	Class, school, name = "Demon Hunter", "Shadow", "Sigil of Alacrity"
	requireTarget, mana, effects = False, 1, ""
	index = "STORMWIND~Demon Hunter~Spell~1~Shadow~Sigil of Alacrity"
	description = "At the start of your next turn, draw a card and reduce its Cost by (1)"
	name_CN = "敏捷咒符"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		SigilofAlacrity_Effect(self.Game, self.ID).connect()
		return None

class SigilofAlacrity_Effect:
	def __init__(self, Game, ID):
		self.Game, self.ID = Game, ID
		self.card = SigilofAlacrity(self.Game, self.ID)
	
	def connect(self):
		if all(not isinstance(trig, SigilofAlacrity_Effect) or trig.ID != self.ID for trig in self.Game.turnStartTrigger):
			self.Game.turnStartTrigger.append(self)
			if self.Game.GUI: self.Game.GUI.heroZones[self.ID].addaTrig(self.card)
			
	def turnStartTrigger(self):
		if self.Game.GUI: self.Game.GUI.showOffBoardTrig(self.card)
		card = self.Game.Hand_Deck.drawCard(self.ID)[0]
		if card: ManaMod(card, changeby=-1).applies()
		try: self.Game.turnStartTrigger.remove(self)
		except: pass
		if self.Game.GUI: self.Game.GUI.heroZones[self.ID].removeaTrig(self.card)
	
	def createCopy(self, game):
		if self not in game.copiedObjs:
			trigCopy = type(self)(game, self.ID)
			game.copiedObjs[self] = trigCopy
			return trigCopy
		else:
			return game.copiedObjs[self]


class FelBarrage(Spell):
	Class, school, name = "Demon Hunter", "Fel", "Fel Barrage"
	requireTarget, mana, effects = False, 2, ""
	index = "STORMWIND~Demon Hunter~Spell~2~Fel~Fel Barrage"
	description = "Deal 2 damage to the low Health enemy, twice"
	name_CN = "邪能弹幕"
	
	def text(self, CHN):
		return (2 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		damage = (2 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		objs = self.Game.charsAlive(3-self.ID)
		chars, lowestHealth = [], np.inf
		for obj in objs:
			if obj.health < lowestHealth: chars, lowestHealth = [obj], obj.health
			elif obj.health == lowestHealth: chars.append(obj)
		if chars:
			char = npchoice(chars)
			self.dealsDamage(char, damage)
			self.dealsDamage(char, damage)
		return None
	
	
class ChaosLeech(Spell):
	Class, school, name = "Demon Hunter", "Fel", "Chaos Leech"
	requireTarget, mana, effects = True, 3, "Lifesteal"
	index = "STORMWIND~Demon Hunter~Spell~3~Fel~Chaos Leech~Lifesteal~Outcast"
	description = "Lifesteal. Deal 3 damage to a minion. Outcast: Deal 5 instead"
	name_CN = "混乱吸取"
	def available(self):
		return self.selectableMinionExists()
	
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
	
	def effCanTrig(self):
		self.effectViable = self.Game.Hand_Deck.outcastcanTrig(self)
	
	def text(self, CHN):
		return "%d, %d"%( (3 + self.countSpellDamage()) * (2 ** self.countDamageDouble()),
						(5 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
						)
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			baseDamage = 5 if posinHand == 0 or posinHand == -1 else 3
			damage = (baseDamage+ self.countSpellDamage()) * (2 ** self.countDamageDouble())
			self.dealsDamage(target, damage)
		return target


class LionsFrenzy(Weapon):
	Class, name, description = "Demon Hunter", "Lion's Frenzy", "Has Attack equal to the number of cards you've drawn this turn"
	mana, attack, durability, effects = 3, 0, 2, ""
	index = "STORMWIND~Demon Hunter~Weapon~3~0~2~Lion's Frenzy"
	name_CN = "雄狮之怒"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.auras["Attack = Num Cards Drawn This Turn"] = StatAura_LionsFrenzy(self)

class StatAura_LionsFrenzy:
	def __init__(self, entity):
		self.entity = entity
		self.signals = ["NewTurnStarts", "CardDrawn"]
	
	def auraAppears(self):
		weapon = self.entity
		for sig in self.signals:
			try: weapon.Game.trigsBoard[weapon.ID][sig].append(self)
			except: weapon.Game.trigsBoard[weapon.ID][sig] = [self]
		stat_Receivers = [receiver for receiver in weapon.auraReceivers if isinstance(receiver, Aura_Receiver)]
		# 将随从上的全部buffAura清除，因为部分光环的适用条件可能会因为随从被沉默而变化，如战歌指挥官
		for receiver in stat_Receivers: receiver.effectClear()
		weapon.attack = weapon.Game.Counters.numCardsDrawnThisTurn[weapon.ID]
		if weapon.btn: weapon.btn.statChangeAni(action="set")
	
	def auraDisappears(self):
		for sig in self.signals:
			try: self.entity.Game.trigsBoard[self.entity.ID][sig].remove(self)
			except: pass
		self.entity.attack = self.entity.attack_Enchant
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return target == self.entity and target.onBoard
	
	def trig(self, signal, ID, subject, target, number, comment, choice=0):
		if self.canTrig(signal, ID, subject, target, number, comment):
			self.entity.attack = self.entity.Game.Counters.numCardsDrawnThisTurn[self.entity.ID]
	
	def selfCopy(self, recipient):  #The recipientMinion is the entity that deals the Aura.
		return type(self)(recipient)


class Felgorger(Minion):
	Class, race, name = "Demon Hunter", "Demon", "Felgorger"
	mana, attack, health = 4, 4, 3
	index = "STORMWIND~Demon Hunter~Minion~4~4~3~Demon~Felgorger~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Draw a Fel spell. Reduce its Cost by (2)"
	name_CN = "邪能吞食者"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		spells = [i for i, card in enumerate(self.Game.Hand_Deck.decks[self.ID]) if card.type == "Spell" and card.school == 'Fel']
		if spells:
			spell = self.Game.Hand_Deck.drawCard(self.ID, npchoice(spells))[0]
			if spell: ManaMod(spell, changeby=-2).applies()
		return None
	

class PersistentPeddler(Minion):
	Class, race, name = "Demon Hunter", "", "Persistent Peddler"
	mana, attack, health = 4, 4, 3
	index = "STORMWIND~Demon Hunter~Minion~4~4~3~~Persistent Peddler~Deathrattle~Tradeable"
	requireTarget, effects, description = False, "", "Tradeable. Deathrattle: Summon a Persistent Peddler from your deck"
	name_CN = "固执的商贩"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.deathrattles = [SummonaPersistentPeddlerfromDeck(self)]

class SummonaPersistentPeddlerfromDeck(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		curGame = self.entity.Game
		if curGame.mode == 0:
			if curGame.picks:
				i = curGame.picks.pop(0)
			else:
				minions = [i for i, card in enumerate(curGame.Hand_Deck.decks[self.entity.ID]) if card.name == "Persistent Peddler"]
				i = npchoice(minions) if minions else -1
			if i > -1: curGame.summonfrom(i, self.entity.ID, self.entity.pos+1, summoner=self.entity, source='D')
		
	def text(self, CHN):
		return "亡语：从你的牌库中召唤一个固执的商贩" if CHN else "Deathrattle: Summon a Persistent Peddler from your deck"


class IreboundBrute(Minion):
	Class, race, name = "Demon Hunter", "Demon", "Irebound Brute"
	mana, attack, health = 7, 6, 7
	index = "STORMWIND~Demon Hunter~Minion~7~6~7~Demon~Irebound Brute~Taunt"
	requireTarget, effects, description = False, "Taunt", "Taunt. Costs (1) less for each card drawn this turn"
	name_CN = "怒缚蛮兵"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsHand = [Trig_IreboundBrute(self)]
	
	def selfManaChange(self):
		if self.inHand:
			self.mana -= self.Game.Counters.numCardsDrawnThisTurn[self.ID]
			self.mana = max(self.mana, 0)

class Trig_IreboundBrute(TrigHand):
	def __init__(self, entity):
		super().__init__(entity, ["CardDrawn"])
	
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.inHand and ID == self.entity.ID
	
	def text(self, CHN):
		return "每当你抽一张牌，重新计算费用" if CHN else "Whenever you draw a card, recalculate the cost"
	
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.Game.Manas.calcMana_Single(self.entity)


class JaceDarkweaver(Minion):
	Class, race, name = "Demon Hunter", "", "Jace Darkweaver"
	mana, attack, health = 8, 7, 5
	index = "STORMWIND~Demon Hunter~Minion~8~7~5~~Jace Darkweaver~Battlecry~Legendary"
	requireTarget, effects, description = False, "", "Battlecry: Cast all Fel spells you've played this game(targets enemies if possible)"
	name_CN = "杰斯·织暗"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		game = self.Game
		spells = [card for card in game.Counters.cardsPlayedThisGame[self.ID] \
						  								if "~Fel~" in card.index]
		npshuffle(spells)
		if spells:
			for spell in spells:
				spell(game, self.ID).cast(None, "enemy1st")
				game.gathertheDead(decideWinner=True)
		return None


"""Druid Cards"""
class Trig_LostinthePark(Trig_Quest):
	def __init__(self, entity):
		super().__init__(entity, ["HeroAttGained"])
		self.numNeeded, self.newQuest, self.reward = 4, DefendtheSquirrels, None
	
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return ID == self.entity.ID
	
	def handleCounter(self, signal, ID, subject, target, number, comment, choice=0):
		self.counter += number
	
	def questEffect(self, quest, game, ID):
		quest.Game.heroes[ID].gainsArmor(5)

class Trig_DefendtheSquirrels(Trig_LostinthePark):
	def __init__(self, entity):
		super().__init__(entity)
		self.numNeeded, self.newQuest, self.reward = 5, FeralFriendsy, None

	def questEffect(self, quest, game, ID):
		quest.Game.heroes[ID].gainsArmor(5)
		quest.Game.Hand_Deck.drawCard(ID)

class Trig_FeralFriendsy(Trig_LostinthePark):
	def __init__(self, entity):
		super().__init__(entity)
		self.numNeeded, self.newQuest, self.reward = 6, None, GufftheTough

class LostinthePark(Questline):
	Class, name = "Druid", "Lost in the Park"
	requireTarget, mana, effects = False, 1, ""
	index = "STORMWIND~Druid~Spell~1~~Lost in the Park~~Questline~Legendary"
	description = "Questline: Gain 4 Attack with your hero. Reward: Gain 5 Armor"
	name_CN = "游园迷梦"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_LostinthePark(self)]

class DefendtheSquirrels(Questline):
	Class, name = "Druid", "Defend the Squirrels"
	requireTarget, mana, effects = False, -1, ""
	index = "STORMWIND~Druid~Spell~0~~Defend the Squirrels~~Questline~Legendary~Uncollectible"
	description = "Questline: Gain 5 Attack with your hero. Reward: Gain 5 Armor and draw a card"
	name_CN = "保护松鼠"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_DefendtheSquirrels(self)]

class FeralFriendsy(Questline):
	Class, name = "Druid", "Feral Friendsy"
	requireTarget, mana, effects = False, -1, ""
	index = "STORMWIND~Druid~Spell~0~~Feral Friendsy~~Questline~Legendary~Uncollectible"
	description = "Questline: Gain 6 Attack with your hero. Reward: Guff the Tough"
	name_CN = "野性暴朋"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_FeralFriendsy(self)]

class GufftheTough(Minion):
	Class, race, name = "Druid", "Beast", "Guff the Tough"
	mana, attack, health = 5, 8, 8
	index = "STORMWIND~Druid~Minion~5~8~8~Beast~Guff the Tough~Battlecry~Legendary~Uncollectible"
	requireTarget, effects, description = False, "", "Taunt. Battlecry: Give your hero +8 Attack this turn. Gain 8 Armor"
	name_CN = "铁肤古夫"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		hero = self.Game.heroes[self.ID]
		hero.gainAttack(8)
		hero.gainsArmor(8)
		return None


class SowtheSoil(Spell):
	Class, school, name = "Druid", "Nature", "Sow the Soil"
	requireTarget, mana, effects = False, 1, ""
	index = "STORMWIND~Druid~Spell~1~Nature~Sow the Soil~Choose One"
	description = "Choose One - Give your minions +1 Attack; or Summon a 2/2 Treant"
	name_CN = "播种施肥"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.options = [Fertilizer_Option(self), NewGrowth_Option(self)]
	
	def need2Choose(self):
		return True
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if choice != 0:
			self.summon(Treant_Stormwind(self.Game, self.ID), -1)
		if choice < 1:
			for minion in self.Game.minionsonBoard(self.ID):
				minion.buffDebuff(1, 0)
		return target


class Fertilizer_Option(Option):
	name, description = "Fertilizer", "Give your minions +1 Attack"
	index = "STORMWIND~Druid~Spell~1~Nature~Fertilizer~Uncollectible"
	mana, attack, health = 1, -1, -1
	
class NewGrowth_Option(Option):
	name, description = "New Growth", "Summon a 2/2 Treant"
	index = "STORMWIND~Druid~Spell~1~Nature~New Growth~Uncollectible"
	mana, attack, health = 1, -1, -1
	
	def available(self):
		return self.entity.Game.space(self.entity.ID)


class Fertilizer(Spell):
	Class, school, name = "Druid", "Nature", "Fertilizer"
	requireTarget, mana, effects = False, 1, ""
	index = "STORMWIND~Druid~Spell~1~Nature~Fertilizer~Uncollectible"
	description = "Give your minions +1 Attack"
	name_CN = "肥料滋养"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		for minion in self.Game.minionsonBoard(self.ID):
			minion.buffDebuff(1, 0)
		return None


class NewGrowth(Spell):
	Class, school, name = "Druid", "Nature", "New Growth"
	requireTarget, mana, effects = False, 1, ""
	index = "STORMWIND~Druid~Spell~1~Nature~New Growth~Uncollectible"
	description = "Summon a 2/2 Treant"
	name_CN = "新生细苗"
	
	def available(self):
		return self.Game.space(self.ID) > 0
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.summon(Treant_Stormwind(self.Game, self.ID), -1)
		return None

class Treant_Stormwind(Minion):
	Class, race, name = "Neutral", "", "Treant"
	mana, attack, health = 2, 2, 2
	index = "STORMWIND~Neutral~Minion~2~2~2~~Treant~Uncollectible"
	requireTarget, effects, description = False, "", ""
	name_CN = "树人"
	
	
class VibrantSquirrel(Minion):
	Class, race, name = "Druid", "Beast", "Vibrant Squirrel"
	mana, attack, health = 1, 2, 1
	index = "STORMWIND~Druid~Minion~1~2~1~Beast~Vibrant Squirrel"
	requireTarget, effects, description = False, "", "Deathrattle: Shuffle 4 Acorns into your deck. When drawn, summon a 2/1 Squirrel"
	name_CN = "活泼的松鼠"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.deathrattles = [Shuffle4AcornsintoYourDeck(self)]

class Shuffle4AcornsintoYourDeck(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		minion = self.entity
		minion.Game.Hand_Deck.shuffleintoDeck([Acorn(minion.Game, minion.ID) for i in range(4)], initiatorID=minion.ID, creator=minion)
	
	def text(self, CHN):
		return "亡语：将4张橡果洗入你的牌库" if CHN else "Deathrattle: Shuffle 4 Acorns into your deck"

class Acorn(Spell):
	Class, school, name = "Druid", "", "Acorn"
	requireTarget, mana, effects = False, 1, ""
	index = "STORMWIND~Druid~Spell~1~~Acorn~Casts When Drawn~Uncollectible"
	description = "Casts When Drawn. Summon a 2/1 Squirrel"
	name_CN = "橡果"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.summon(SatisfiedSquirrel(self.Game, self.ID), -1)
		return None

class SatisfiedSquirrel(Minion):
	Class, race, name = "Druid", "Beast", "Satisfied Squirrel"
	mana, attack, health = 1, 2, 1
	index = "STORMWIND~Druid~Minion~1~2~1~Beast~Satisfied Squirrel~Uncollectible"
	requireTarget, effects, description = False, "", ""
	name_CN = "满足的松鼠"


class Composting(Spell):
	Class, school, name = "Druid", "Nature", "Composting"
	requireTarget, mana, effects = False, 2, ""
	index = "STORMWIND~Druid~Spell~2~Nature~Composting"
	description = "Give your minions 'Deathrattle: Draw a card'"
	name_CN = "施肥"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		for minion in self.Game.minionsonBoard(self.ID):
			minion.getsTrig(DrawaCard_Composting(minion), trigType="Deathrattle", connect=True)
		return target

class DrawaCard_Composting(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.Game.Hand_Deck.drawCard(self.entity.ID)
		
	def text(self, CHN):
		return "亡语：抽一张牌" if CHN else "Deathrattle: Draw a card"
		
		
class Wickerclaw(Minion):
	Class, race, name = "Druid", "Beast", "Wickerclaw"
	mana, attack, health = 2, 1, 4
	index = "STORMWIND~Druid~Minion~2~1~4~Beast~Wickerclaw"
	requireTarget, effects, description = False, "", "After your hero gains Attack, this minion gain +2 Attack"
	name_CN = "柳魔锐爪兽"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_Wickerclaw(self)]

class Trig_Wickerclaw(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["HeroAttGained"])
	
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and ID == self.entity.ID
	
	def text(self, CHN):
		return "在你的英雄获得攻击力后，该随从获得+2攻击力" if CHN \
			else "After your hero gains Attack, this minion gain +2 Attack"
	
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.buffDebuff(2, 0)


class OracleofElune(Minion):
	Class, race, name = "Druid", "", "Oracle of Elune"
	mana, attack, health = 3, 2, 4
	index = "STORMWIND~Druid~Minion~3~2~4~~Oracle of Elune"
	requireTarget, effects, description = False, "", "After you play a minion that costs (2) or less, summon a copy of it"
	name_CN = "艾露恩神谕者"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_OracleofElune(self)]

class Trig_OracleofElune(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["MinionBeenPlayed"])
	
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject.ID == self.entity.ID and number < 3
	
	def text(self, CHN):
		return "在你使用一张法力值消耗小于或等于(2)点的随从牌后，召唤一个它的复制" if CHN \
			else "After you play a minion that costs (2) or less, summon a copy of it"
	
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.summon(subject.selfCopy(self.entity.ID, self.entity), self.entity.pos+1)


class KodoMount(Spell):
	Class, school, name = "Druid", "", "Kodo Mount"
	requireTarget, mana, effects = True, 4, ""
	index = "STORMWIND~Druid~Spell~4~~Kodo Mount"
	description = "Give a minion +4/+2 and Rush. When it dies, summon a Kodo"
	name_CN = "科多兽坐骑"
	
	def available(self):
		return self.selectableMinionExists()
	
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			target.buffDebuff(4, 2)
			target.getsEffect("Rush")
			target.getsTrig(SummonaKodo(target), trigType="Deathrattle", connect=target.onBoard)
		return target

class SummonaKodo(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		minion = self.entity
		minion.summon(GuffsKodo(minion.Game, minion.ID), minion.pos+1)
	
	def text(self, CHN):
		return "亡语：召唤一只4/2的科多兽" if CHN else "Deathrattle: Summon a 4/2 Kodo"

class GuffsKodo(Minion):
	Class, race, name = "Druid", "Beast", "Guff's Kodo"
	mana, attack, health = 3, 4, 2
	index = "STORMWIND~Druid~Minion~3~4~2~Beast~Guff's Kodo~Rush~Uncollectible"
	requireTarget, effects, description = False, "Rush", "Rush"
	name_CN = "古夫的科多兽"
	

class ParkPanther(Minion):
	Class, race, name = "Druid", "Beast", "Park Panther"
	mana, attack, health = 4, 4, 4
	index = "STORMWIND~Druid~Minion~4~4~4~Beast~Park Panther~Rush"
	requireTarget, effects, description = False, "Rush", "Rush. Whenever this minion attacks, give your hero +3 Attack this turn"
	name_CN = "花园猎豹"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_ParkPanther(self)]

class Trig_ParkPanther(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["MinionAttackingMinion", "MinionAttackingHero"])
	
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject.ID == self.entity.ID
	
	def text(self, CHN):
		return "每当该随从攻击时，在本回合中使你的英雄获得+3攻击力" if CHN \
			else "Whenever this minion attacks, give your hero +3 Attack this turn"
	
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.Game.heroes[self.entity.ID].gainAttack(3)


class BestinShell(Spell):
	Class, school, name = "Druid", "", "Best in Shell"
	requireTarget, mana, effects = False, 6, ""
	index = "STORMWIND~Druid~Spell~6~~Best in Shell~Tradeable"
	description = "Tradeable. Summon two 2/7 Turtles with Taunt"
	name_CN = "紧壳商品"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.summon([GoldshellTurtle(self.Game, self.ID) for i in range(2)], (-1, "totheRightEnd"))
		return None

class GoldshellTurtle(Minion):
	Class, race, name = "Druid", "Beast", "Goldshell Turtle"
	mana, attack, health = 4, 2, 7
	index = "STORMWIND~Druid~Minion~4~2~7~Beast~Goldshell Turtle~Taunt~Uncollectible"
	requireTarget, effects, description = False, "Taunt", "Taunt"
	name_CN = "金壳龟"


class SheldrasMoontree(Minion):
	Class, race, name = "Druid", "", "Sheldras Moontree"
	mana, attack, health = 8, 5, 5
	index = "STORMWIND~Druid~Minion~8~5~5~~Sheldras Moontree~Battlecry~Legendary"
	requireTarget, effects, description = False, "", "Battlecry: The next 3 spells you draw are Cast When Drawn"
	name_CN = "沙德拉斯·月树"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		SheldrasMoontree_Effect(self.Game, self.ID).connect()
		return None

class SheldrasMoontree_Effect:
	def __init__(self, Game, ID):
		self.Game, self.ID = Game, ID
		self.counter = 3
		self.card = SheldrasMoontree(Game, ID)
		
	def connect(self):
		try: trigs = self.Game.trigsBoard[self.ID]["CardDrawn"]
		except: trigs = self.Game.trigsBoard[self.ID]["CardDrawn"] = []
		trig = next((trig for trig in trigs if isinstance(trig, SheldrasMoontree_Effect)), None)
		if trig:
			trig.counter = 3
			if trig.card.btn: trig.card.btn.trigAni(trig.counter)
		else:
			trigs.append(self)
			if self.Game.GUI: self.Game.GUI.heroZones[self.ID].addaTrig(self.card, text='3')
		
	def disconnect(self):
		try: self.Game.trigsBoard[self.ID]["CardDrawn"].remove(self)
		except: pass
		if self.Game.GUI: self.Game.GUI.heroZones[self.ID].removeaTrig(self.card)
	
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return target[0].ID == self.ID
	
	def trig(self, signal, ID, subject, target, number, comment, choice=0):
		if self.canTrig(signal, ID, subject, target, number, comment):
			if self.Game.GUI: self.Game.GUI.showOffBoardTrig(self.card)
			self.effect(signal, ID, subject, target, number, comment)
	
	def text(self, CHN):
		return "你接下来抽到的%d张法术牌获得抽到时施放效果"%self.counter if CHN \
			else "The next %d spells you draw are Cast When Drawn"%self.counter
	
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.counter -= 1
		if self.card.btn: self.card.btn.trigAni(self.counter)
		target[0].index += "Casts When Drawn"
		if self.counter < 1: self.disconnect()
	
	def createCopy(self, game):  #不是纯的只在回合结束时触发，需要完整的createCopy
		if self not in game.copiedObjs:  #这个扳机没有被复制过
			trigCopy = type(self)(game, self.ID, None)
			game.copiedObjs[self] = trigCopy
			trigCopy.counter = self.counter
			return trigCopy
		else:  #一个扳机被复制过了，则其携带者也被复制过了
			return game.copiedObjs[self]



"""Hunter Cards"""
class DevouringSwarm(Spell):
	Class, school, name = "Hunter", "", "Devouring Swarm"
	requireTarget, mana, effects = True, 0, ""
	index = "STORMWIND~Hunter~Spell~0~~Devouring Swarm"
	description = "Choose an enemy minion. Your minions attack it, then return any that die to your hand"
	name_CN = "集群撕咬"
	def available(self):
		return self.selectableEnemyMinionExists()
	
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard and target.ID != self.ID

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		game = self.Game
		minions = game.minionsAlive(self.ID)
		if target and minions:
			minions = [minions[i] for i in np.array([minion.seq for minion in minions]).argsort()]
			for minion in minions:
				if target.onBoard and target.health > 0 and not target.dead:
					self.Game.battle(minion, target, verifySelectable=False, useAttChance=False, resolveDeath=False, resetRedirTrig=True)
			for minion in minions:
				if minion.dead or minion.health < 1: self.addCardtoHand(type(minion), self.ID)
		return target


class Trig_DefendtheDwarvenDistrict(Trig_Quest):
	def __init__(self, entity):
		super().__init__(entity, ["MinionTookDmg", "HeroTookDmg"])
		self.numNeeded, self.newQuest, self.reward = 2, TaketheHighGround, None
		self.spells = []
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject and subject.ID == self.entity.ID and subject.type == "Spell" and subject not in self.spells
	
	def handleCounter(self, signal, ID, subject, target, number, comment, choice=0):
		self.spells.append(subject)
		self.counter += 1
	
	def questEffect(self, quest, game, ID):
		quest.Game.powers[quest.ID].getsEffect("Can Target Minions")
		
	def createCopy(self, game):
		if self not in game.copiedObjs: #这个扳机没有被复制过
			entityCopy = self.entity.createCopy(game)
			trigCopy = self.selfCopy(entityCopy)
			trigCopy.spells = [spell.createCopy(game) for spell in self.spells]
			trigCopy.counter = self.counter
			game.copiedObjs[self] = trigCopy
			return trigCopy
		else: #一个扳机被复制过了，则其携带者也被复制过了
			return game.copiedObjs[self]

class Trig_TaketheHighGround(Trig_DefendtheDwarvenDistrict):
	def __init__(self, entity):
		super().__init__(entity)
		self.numNeeded, self.newQuest, self.reward = 2, KnockEmDown, None
	
	def questEffect(self, quest, game, ID):
		ManaMod(quest.Game.powers[quest.ID], changeto=0).applies()

class Trig_KnockEmDown(Trig_DefendtheDwarvenDistrict):
	def __init__(self, entity):
		super().__init__(entity)
		self.numNeeded, self.newQuest, self.reward = 2, None, TavishMasterMarksman

class DefendtheDwarvenDistrict(Questline):
	Class, name = "Hunter", "Defend the Dwarven District"
	requireTarget, mana, effects = False, 1, ""
	index = "STORMWIND~Hunter~Spell~1~~Defend the Dwarven District~~Questline~Legendary"
	description = "Questline: Deal damage with 2 spells. Reward: Your Hero Power can target minions"
	name_CN = "保卫敌人区"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_DefendtheDwarvenDistrict(self)]
		
class TaketheHighGround(Questline):
	Class, name = "Hunter", "Take the High Ground"
	requireTarget, mana, effects = False, -1, ""
	index = "STORMWIND~Hunter~Spell~0~~Take the High Ground~~Questline~Legendary"
	description = "Questline: Deal damage with 2 spells. Reward: Set the Cost of your Hero Power to (0)"
	name_CN = "占据高地"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_TaketheHighGround(self)]

class KnockEmDown(Questline):
	Class, name = "Hunter", "Knock 'Em Down"
	requireTarget, mana, effects = False, -1, ""
	index = "STORMWIND~Hunter~Spell~0~~Knock 'Em Down~~Questline~Legendary~Uncollectible"
	description = "Questline: Deal damage with 2 spells. Reward: Tavish, Master Marksman"
	name_CN = "干掉他们"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_KnockEmDown(self)]

class TavishMasterMarksman(Minion):
	Class, race, name = "Hunter", "", "Tavish, Master Marksman"
	mana, attack, health = 5, 7, 7
	index = "STORMWIND~Hunter~Minion~5~7~7~~Tavish, Master Marksman~Battlecry~Legendary~Uncollectible"
	requireTarget, effects, description = False, "", "Battlecry: For the rest of the game, spells you cast refresh your Hero Power"
	name_CN = "射击大师塔维什"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		TavishMasterMarksman_Effect(self.Game, self.ID).connect()
		return None

class TavishMasterMarksman_Effect:
	def __init__(self, Game, ID):
		self.Game, self.ID = Game, ID
		self.card = TavishMasterMarksman(Game, ID)
		
	def connect(self):
		try: trigs = self.Game.trigsBoard[self.ID]["SpellBeenPlayed"]
		except: trigs = self.Game.trigsBoard[self.ID]["SpellBeenPlayed"] = []
		if not any(isinstance(trig, TavishMasterMarksman_Effect) for trig in trigs):
			self.Game.trigAuras[self.ID].append(self)
			trigs.append(self)
			if self.Game.GUI: self.Game.GUI.heroZones[self.ID].addaTrig(self.card)
	
	#number here is a list that holds the damage to be processed
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject.ID == self.ID
	
	def trig(self, signal, ID, subject, target, number, comment, choice=0):
		if self.canTrig(signal, ID, subject, target, number, comment):
			if self.Game.GUI: self.Game.GUI.showOffBoardTrig(self.card, animationType='')
			self.Game.powers[self.ID].usageCount = 0
			self.Game.powers[self.ID].btn.checkHpr()
			
	def createCopy(self, game):  #不是纯的只在回合结束时触发，需要完整的createCopy
		if self not in game.copiedObjs:  #这个扳机没有被复制过
			trigCopy = type(self)(game, self.ID)
			game.copiedObjs[self] = trigCopy
			return trigCopy
		else:  #一个扳机被复制过了，则其携带者也被复制过了
			return game.copiedObjs[self]


class LeatherworkingKit(Weapon):
	Class, name, description = "Hunter", "Leatherworking Kit", "After three friendly Beasts die, draw a Beast and give it +1/+1. Lose 1 Durability"
	mana, attack, durability, effects = 2, 0, 3, ""
	index = "STORMWIND~Hunter~Weapon~2~0~3~Leatherworking Kit"
	name_CN = "制皮工具"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_LeatherworkingKit(self)]

class Trig_LeatherworkingKit(Trig_Countdown):
	def __init__(self, entity):
		super().__init__(entity, ["MinionDied"])
		self.counter = 3
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return target.ID == self.entity.ID and self.entity.onBoard and self.entity.health > 0 and "Beast" in target.race
	
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		if self.counter < 1:
			self.counter = 3
			weapon = self.entity
			indices = [i for i, card in enumerate(weapon.Game.Hand_Deck.decks[weapon.ID]) if "Beast" in card.race]
			if indices:
				beast = weapon.Game.Hand_Deck.drawCard(weapon.ID, npchoice(indices))[0]
				if beast: beast.buffDebuff(1, 1)
				weapon.loseDurability()


class AimedShot(Spell):
	Class, school, name = "Hunter", "", "Aimed Shot"
	requireTarget, mana, effects = True, 3, ""
	index = "STORMWIND~Hunter~Spell~3~~Aimed Shot"
	description = "Deal 3 damage. Your next Hero Power deals two more damage"
	name_CN = "瞄准射击"
	
	def text(self, CHN):
		return (3 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			damage = (3 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			self.dealsDamage(target, damage)
			self.Game.powers[self.ID].getsEffect("Power Damage", amount=2)
			AimedShot_Effect(self.Game, self.ID).connect()
		return target

class AimedShot_Effect:
	def __init__(self, Game, ID):
		self.Game, self.ID = Game, ID
		self.card = AimedShot(Game, ID)
		self.counter = 2
		
	def connect(self):
		try: trigs = self.Game.trigsBoard[self.ID]["HeroUsedAbility"]
		except: trigs = self.Game.trigsBoard[self.ID]["HeroUsedAbility"] = []
		trig = next((trig for trig in trigs if isinstance(trig, AimedShot_Effect)), None)
		if trig:
			trig.counter += 2
			if trig.card.btn: trig.card.btn.trigAni(trig.counter)
		else:
			trigs.append(self)
			if self.Game.GUI: self.Game.GUI.heroZones[self.ID].addaTrig(self.card, text='2')
	
	def disconnect(self):
		try: self.Game.trigsBoard[self.ID]["HeroUsedAbility"].remove(self)
		except: pass
		if self.Game.GUI: self.Game.GUI.heroZones[self.ID].removeaTrig(self.card)
	
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject.ID == self.ID
	
	def trig(self, signal, ID, subject, target, number, comment, choice=0):
		if self.canTrig(signal, ID, subject, target, number, comment):
			if self.Game.GUI: self.Game.GUI.showOffBoardTrig(self.card)
			self.effect(signal, ID, subject, target, number, comment)
	
	def text(self, CHN):
		return "你使用英雄技能后，你的英雄技能不再额外造成2点伤害" if CHN \
			else "After you use Hero Power, it no longer deals 2 extra damage"
	
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.Game.powers[self.ID].losesEffect("Power Damage", amount=self.counter)
		self.disconnect()
	
	def createCopy(self, game):  #不是纯的只在回合结束时触发，需要完整的createCopy
		if self not in game.copiedObjs:  #这个扳机没有被复制过
			trigCopy = type(self)(game, self.ID)
			game.copiedObjs[self] = trigCopy
			trigCopy.counter = self.counter
			return trigCopy
		else:  #一个扳机被复制过了，则其携带者也被复制过了
			return game.copiedObjs[self]


class RammingMount(Spell):
	Class, school, name = "Hunter", "", "Ramming Mount"
	requireTarget, mana, effects = True, 3, ""
	index = "STORMWIND~Hunter~Spell~3~~Ramming Mount"
	description = "Give a minion +2/+2 and Immune while attacking. When it dies, summon a Ram"
	name_CN = "山羊坐骑"
	def available(self):
		return self.selectableMinionExists()
	
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			target.buffDebuff(2, 2)
			target.getsTrig(Trig_TavishsRam(target), trigType="TrigBoard", connect=target.onBoard)
			target.getsTrig(SummonaRam(target), trigType="Deathrattle", connect=target.onBoard)
		return target

class SummonaRam(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.summon(TavishsRam(self.entity.Game, self.entity.ID), self.entity.pos + 1)
	
	def text(self, CHN):
		return "亡语：召唤一只2/2的山羊" if CHN else "Deathrattle: Summon a 2/2 Ram"

class TavishsRam(Minion):
	Class, race, name = "Hunter", "Beast", "Tavish's Ram"
	mana, attack, health = 2, 2, 2
	index = "STORMWIND~Hunter~Minion~2~2~2~Beast~Tavish's Ram~Uncollectible"
	requireTarget, effects, description = False, "", "Immune while attacking"
	name_CN = "塔维什的山羊"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_TavishsRam(self)]

class Trig_TavishsRam(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["BattleStarted", "BattleFinished"])
	
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject == self.entity and self.entity.onBoard
	
	def text(self, CHN):
		return "在攻击时具有免疫" if CHN else "Immune while attacking"
	
	#不知道攻击具有受伤时召唤一个随从的扳机的随从时，飞刀能否对这个友方角色造成伤害
	#目前的写法是这个战斗结束信号触发在受伤之后
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		if signal == "BattleStarted": subject.getsEffect("Immune")
		else: subject.losesEffect("Immune")


class StormwindPiper(Minion):
	Class, race, name = "Hunter", "Demon", "Stormwind Piper"
	mana, attack, health = 3, 1, 6
	index = "STORMWIND~Hunter~Minion~3~1~6~Demon~Stormwind Piper"
	requireTarget, effects, description = False, "", "After this minion attacks, give your Beasts +1/+1"
	name_CN = "暴风城吹笛人"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_StormwindPiper(self)]

class Trig_StormwindPiper(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["MinionAttackedMinion", "MinionAttackedHero"])
	
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject == self.entity and self.entity.onBoard
	
	def text(self, CHN):
		return "在该随从攻击后，使你的野兽获得+1/+1" if CHN else "After this minion attacks, give your Beasts +1/+1"
	
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		for minion in self.entity.Game.minionsonBoard(self.entity.ID):
			if "Beast" in minion.race: minion.buffDebuff(1, 1)


class RodentNest(Minion):
	Class, race, name = "Hunter", "", "Rodent Nest"
	mana, attack, health = 4, 2, 2
	index = "STORMWIND~Hunter~Minion~4~2~2~~Rodent Nest~Deathrattle"
	requireTarget, effects, description = False, "", "Deathrattle: Summon five 1/1 Rats"
	name_CN = "老鼠窝"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.deathrattles = [SumonFiveRats(self)]

class SumonFiveRats(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		minion = self.entity
		minion.summon([Rat(minion.Game, minion.ID) for i in range(5)], (minion.pos, "totheRight"))
	
	def text(self, CHN):
		return "亡语：召唤五个1/1的老鼠" if CHN else "Deathrattle: Summon five 1/1 Rats"


class ImportedTarantula(Minion):
	Class, race, name = "Hunter", "Beast", "Imported Tarantula"
	mana, attack, health = 5, 4, 5
	index = "STORMWIND~Hunter~Minion~5~4~5~Beast~Imported Tarantula~Deathrattle~Tradeable"
	requireTarget, effects, description = False, "", "Tradeable. Deathrattle: Summon two 1/1 Spiders with Poisonous and Rush"
	name_CN = "进口狼蛛"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.deathrattles = [SumonTwoSpiders_PoisonousRush(self)]

class SumonTwoSpiders_PoisonousRush(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		pos = (self.entity.pos, "leftandRight") if self.entity in self.entity.Game.minions[self.entity.ID] else (-1, "totheRightEnd")
		self.entity.Game.summon([InvasiveSpiderling(self.entity.Game, self.entity.ID) for i in range(2)], pos, self.entity)
	
	def text(self, CHN):
		return "亡语：召唤两个1/1并具有剧毒和突袭的蜘蛛" if CHN else "Deathrattle: Summon two 1/1 Spiders with Poisonous and Rush"

class InvasiveSpiderling(Minion):
	Class, race, name = "Hunter", "Beast", "Invasive Spiderling"
	mana, attack, health = 2, 1, 1
	index = "STORMWIND~Hunter~Minion~2~1~1~Beast~Invasive Spiderling~Poisonous~Rush~Uncollectible"
	requireTarget, effects, description = False, "Poisonous,Rush", "Poisonous, Rush"
	name_CN = "入侵的蜘蛛"


class TheRatKing(Minion):
	Class, race, name = "Hunter", "Beast", "The Rat King"
	mana, attack, health = 5, 5, 5
	index = "STORMWIND~Hunter~Minion~5~5~5~Beast~The Rat King~Rush~Deathrattle~Legendary"
	requireTarget, effects, description = False, "Rush", "Rush. Deathrattle: Go Dormant. Revive after 5 friendly minions die"
	name_CN = "鼠王"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.deathrattles = [RatKingGoesDormant(self)]
		
class RatKingGoesDormant(Deathrattle_Minion):
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return target == self.entity and self.entity.Game.space(self.entity.ID) > 0
	
	#这个变形亡语只能触发一次。
	def trig(self, signal, ID, subject, target, number, comment, choice=0):
		if self.canTrig(signal, ID, subject, target, number, comment):
			minion = self.entity
			if minion.Game.GUI:
				minion.Game.GUI.deathrattleAni(minion)
			minion.Game.Counters.deathrattlesTriggered[minion.ID].append(RatKingGoesDormant)
			dormant = DormantRatKing(minion.Game, minion.ID, TheRatKing(minion.Game, minion.ID))
			minion.Game.transform(minion, dormant)
	
	def text(self, CHN):
		return "亡语：进入休眠状态。在5个友方随从死亡后复活" if CHN \
			else "Deathrattle: Go dormant. Revive after 5 friendly minions die"

class DormantRatKing(Dormant):
	Class, school, name = "Hunter", "", "Dormant Rat King"
	description = "Restore 5 Health to awaken"
	name_CN = "沉睡的鼠王"
	def __init__(self, Game, ID, minionInside):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_DormantRatKing(self)]
		self.minionInside = minionInside

class Trig_DormantRatKing(Trig_Countdown):
	def __init__(self, entity):
		super().__init__(entity, ["MinionDied"])
		self.counter = 5
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and target.ID == self.entity.ID
	
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		if self.counter < 1:
			self.entity.Game.transform(self.entity, self.entity.minionInside)


class RatsofExtraordinarySize(Spell):
	Class, school, name = "Hunter", "", "Rats of Extraordinary Size"
	requireTarget, mana, effects = False, 6, ""
	index = "STORMWIND~Hunter~Spell~6~~Rats of Extraordinary Size"
	description = "Summon seven 1/1 Rats. Any that can't fit on the battlefield go to your hand with +4/+4"
	name_CN = "硕鼠成群"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		size = self.Game.space(self.ID)
		minions2Board = [Rat(self.Game, self.ID) for i in range(size)]
		minions2Hand = [Rat(self.Game, self.ID) for i in range(7-size)]
		if minions2Board:
			self.Game.summon(minions2Board, (-1, "totheRightEnd"), summoner=self)
		if minions2Hand:
			for minion in minions2Hand: minion.buffDebuff(4, 4)
			self.addCardtoHand(minions2Hand, self.ID)
		return None

class Rat(Minion):
	Class, race, name = "Hunter", "Beast", "Rat"
	mana, attack, health = 1, 1, 1
	index = "STORMWIND~Hunter~Minion~1~1~1~Beast~Rat~Uncollectible"
	requireTarget, effects, description = False, "", ""
	name_CN = "老鼠"


"""Mage Cards"""
class HotStreak(Spell):
	Class, school, name = "Mage", "Fire", "Hot Streak"
	requireTarget, mana, effects = False, 0, ""
	index = "STORMWIND~Mage~Spell~0~Fire~Hot Streak"
	description = "Your next Fire spell costs (2) less"
	name_CN = "炽热连击"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		tempAura = GameManaAura_InTurnNextFireSpell2Less(self.Game, self.ID)
		self.Game.Manas.CardAuras.append(tempAura)
		tempAura.auraAppears()
		return None

class GameManaAura_InTurnNextFireSpell2Less(TempManaEffect):
	def __init__(self, Game, ID, changeby=0, changeto=-1):
		super().__init__(Game, ID, -2, -1)
	
	def applicable(self, target):
		return target.ID == self.ID and target.type == "Spell" and target.school == "Fire"


class FirstFlame(Spell):
	Class, school, name = "Mage", "Fire", "First Flame"
	requireTarget, mana, effects = True, 1, ""
	index = "STORMWIND~Mage~Spell~1~Fire~First Flame"
	description = "Deal 2 damage to a minion. Add a Second Flame to your hand"
	name_CN = "初始之火"
	
	def available(self):
		return self.selectableMinionExists()
	
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
	
	def text(self, CHN):
		return (2 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			damage = (2 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			self.dealsDamage(target, damage)
			self.addCardtoHand(SecondFlame, self.ID)
		return target

class SecondFlame(Spell):
	Class, school, name = "Mage", "Fire", "Second Flame"
	requireTarget, mana, effects = True, 1, ""
	index = "STORMWIND~Mage~Spell~1~Fire~Second Flame~Uncollectible"
	description = "Deal 2 damage to a minion"
	name_CN = "传承之火"
	
	def available(self):
		return self.selectableMinionExists()
	
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
	
	def text(self, CHN):
		return (2 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			damage = (2 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			self.dealsDamage(target, damage)
		return target


class Trig_SorcerersGambit(Trig_Quest):
	def __init__(self, entity):
		super().__init__(entity, ["SpellBeenPlayed"])
		self.numNeeded, self.newQuest, self.reward = 3, StallforTime, None
		self.spellsLeft = ["Arcane", "Fire", "Frost"]
	
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject.ID == self.entity.ID and subject.school in self.spellsLeft
	
	def handleCounter(self, signal, ID, subject, target, number, comment, choice=0):
		self.spellsLeft.remove(subject.school)
		self.counter += 1

	def questEffect(self, quest, game, ID):
		spells = [i for i, card in enumerate(quest.Game.Hand_Deck.hands[ID]) if card.type == "Spell"]
		if spells: quest.Game.Hand_Deck.drawCard(ID, npchoice(spells))
	
	def createCopy(self, game):
		if self not in game.copiedObjs:  #这个扳机没有被复制过
			entityCopy = self.entity.createCopy(game)
			trigCopy = self.selfCopy(entityCopy)
			trigCopy.spellsLeft = self.spellsLeft[:]
			trigCopy.counter = self.counter
			game.copiedObjs[self] = trigCopy
			return trigCopy
		else:  #一个扳机被复制过了，则其携带者也被复制过了
			return game.copiedObjs[self]

class Trig_StallforTime(Trig_SorcerersGambit):
	def __init__(self, entity):
		super().__init__(entity)
		self.numNeeded, self.newQuest, self.reward = 3, ReachthePortalRoom, None
	
	def questEffect(self, quest, game, ID):
		quest.discoverandGenerate_MultiplePools(StallforTime, '',
												poolsFunc=lambda: SorcerersGambit.decidePools(quest))

class Trig_ReachthePortalRoom(Trig_SorcerersGambit):
	def __init__(self, entity):
		super().__init__(entity)
		self.numNeeded, self.newQuest, self.reward = 3, None, ArcanistDawngrasp

class SorcerersGambit(Questline):
	Class, school, name = "Mage", "", "Sorcerer's Gambit"
	requireTarget, mana, effects = False, 1, ""
	index = "STORMWIND~Mage~Spell~1~~Sorcerer's Gambit~~Questline~Legendary"
	description = "Questline: Cast a Fire, Frost and Arcane spell. Reward: Draw a spell"
	name_CN = "巫师的计策"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_SorcerersGambit(self)]

	def decidePools(self):
		Class = classforDiscover(self)
		return [self.rngPool("Fire Spells as " + Class),
		 		self.rngPool("Frost Spells as " + Class),
		 		self.rngPool("Arcane Spells as " + Class)]
	

class StallforTime(Questline):
	Class, name = "Mage", "Stall for Time"
	requireTarget, mana, effects = False, -1, ""
	index = "STORMWIND~Mage~Spell~0~~Stall for Time~~Questline~Legendary~Uncollectible"
	description = "Questline: Cast a Fire, Frost and Arcane spell. Reward: Discover one"
	name_CN = "拖延时间"
	poolIdentifier = "Fire Spells as Mage"
	@classmethod
	def generatePool(cls, pools):
		classes, lists = [], []
		for Class in pools.Classes:
			fire, frost, arcane = [], [], []
			for card in pools.ClassCards[Class]:
				if card.type == "Spell":
					if card.school == "Fire": fire.append(card)
					elif card.school == "Frost": frost.append(card)
					elif card.school == "Arcane": arcane.append(card)
			classes += ["Fire Spells as %s"%Class, "Frost Spells as %s"%Class, "Arcane Spells as %s"%Class]
			lists += [fire, frost, arcane]
		return classes, lists
	
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_StallforTime(self)]
	
class ReachthePortalRoom(Questline):
	Class, name = "Mage", "Reach the Portal Room"
	requireTarget, mana, effects = False, -1, ""
	index = "STORMWIND~Mage~Spell~0~~Reach the Portal Room~~Questline~Legendary~Uncollectible"
	description = "Questline: Cast a Fire, Frost and Arcane spell. Reward: Arcanist Dawngrasp"
	name_CN = "抵达传送大厅"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_ReachthePortalRoom(self)]

class ArcanistDawngrasp(Minion):
	Class, race, name = "Mage", "", "Arcanist Dawngrasp"
	mana, attack, health = 5, 7, 7
	index = "STORMWIND~Mage~Minion~5~7~7~~Arcanist Dawngrasp~Battlecry~Legendary~Uncollectible"
	requireTarget, effects, description = False, "", "Battlecry: For the rest of the game, you have Spell Damage +3"
	name_CN = "奥术师晨拥"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.Game.heroes[self.ID].getsEffect("Spell Damage", amount=3)
		return None


class CelestialInkSet(Weapon):
	Class, name, description = "Mage", "Celestial Ink Set", "After you spend 5 Mana on spells, reduce the Cost of a spell in your hand by (5)"
	mana, attack, durability, effects = 2, 0, 2, ""
	index = "STORMWIND~Mage~Weapon~2~0~2~Celestial Ink Set"
	name_CN = "星空墨水套装"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_CelestialInkSet(self)]
		
class Trig_CelestialInkSet(Trig_Countdown):
	def __init__(self, entity):
		super().__init__(entity, ["ManaPaid"])
		self.counter = 5
		
	def increment(self, number):
		return number
	
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return ID == self.entity.ID and self.entity.onBoard and number > 0 and self.entity.health > 0
	
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		if self.counter < 1:
			self.counter = 5
			spells = [card for card in self.entity.Game.Hand_Deck.hands[self.entity.ID] if card.type == "Spell"]
			if spells:
				ManaMod(npchoice(spells), changeby=-5).applies()
				self.entity.loseDurability()
				

class Ignite(Spell):
	Class, school, name = "Mage", "Fire", "Ignite"
	requireTarget, mana, effects = True, 2, ""
	index = "STORMWIND~Mage~Spell~2~Fire~Ignite~2"
	description = "Deal 2 damgae. Shuffle an Ignite into your deck that deals one more damage"
	name_CN = "点燃"
	baseDamage = 2
	def text(self, CHN):
		return (type(self).baseDamage + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			base = type(self).baseDamage
			damage = (base + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			self.dealsDamage(target, damage)
			newBaseDamage = base + 1
			newIndex = "STORMWIND~Mage~2~Spell~Fire~Ignite~%d~Uncollectible"%newBaseDamage
			subclass = type("Ignite__%d"%newBaseDamage, (Ignite, ),
							{"index": newIndex, "description": "Deal %d damgae. Shuffle an Ignite into your deck that deals one more damage"%newBaseDamage,
							"baseDamage": newBaseDamage}
							)
			self.Game.Hand_Deck.shuffleintoDeck(subclass(self.Game, self.ID), initiatorID=self.ID, creator=self)
		return target
	
	
class PrestorsPyromancer(Minion):
	Class, race, name = "Mage", "", "Prestor's Pyromancer"
	mana, attack, health = 2, 2, 3
	index = "STORMWIND~Paladin~Minion~2~2~3~~Prestor's Pyromancer~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Your next Fire spell has Spell Damage +2"
	name_CN = "普瑞斯托的炎术师"

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.Game.effects[self.ID]["Fire Spell Damage"] += 2
		PrestorsPyromancer_Effect(self.Game, self.ID).connect()
		return None

class PrestorsPyromancer_Effect:
	def __init__(self, Game, ID):
		self.Game, self.ID = Game, ID
		self.card = PrestorsPyromancer(Game, ID)
		self.counter = 2
	
	def connect(self):
		try: trigs = self.Game.trigsBoard[self.ID]["SpellBeenCast"]
		except: trigs = self.Game.trigsBoard[self.ID]["SpellBeenCast"] = []
		trig = next((trig for trig in trigs if isinstance(trig, PrestorsPyromancer_Effect)), None)
		if trig:
			trig.counter += 2
			if trig.card.btn: trig.card.btn.trigAni(trig.counter)
		else:
			trigs.append(self)
			if self.Game.GUI: self.Game.GUI.heroZones[self.ID].addaTrig(self.card, text='2')
	
	def disconnect(self):
		try: self.Game.trigsBoard[self.ID]["SpellBeenCast"].remove(self)
		except: pass
		if self.Game.GUI: self.Game.GUI.heroZones[self.ID].removeaTrig(self.card)
	
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject.ID == self.ID and subject.school == "Fire"
	
	def trig(self, signal, ID, subject, target, number, comment, choice=0):
		if self.canTrig(signal, ID, subject, target, number, comment):
			if self.Game.GUI: self.Game.GUI.showOffBoardTrig(self.card)
			self.effect(signal, ID, subject, target, number, comment)
	
	def text(self, CHN):
		return "你使用一张火焰法术后，你的火焰法术不再拥有法术伤害+2" if CHN \
			else "After you play a Fire spell, it no longer has Spell Damge +2"
	
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.Game.effects[self.ID]["Fire Spell Damage"] -= self.counter
		self.disconnect()
	
	def createCopy(self, game):  #不是纯的只在回合结束时触发，需要完整的createCopy
		if self not in game.copiedObjs:  #这个扳机没有被复制过
			trigCopy = type(self)(game, self.ID)
			game.copiedObjs[self] = trigCopy
			trigCopy.counter = self.counter
			return trigCopy
		else:  #一个扳机被复制过了，则其携带者也被复制过了
			return game.copiedObjs[self]


class FireSale(Spell):
	Class, school, name = "Mage", "Fire", "Fire Sale"
	requireTarget, mana, effects = False, 4, ""
	index = "STORMWIND~Mage~Spell~4~Fire~Fire Sale~Tradeable"
	description = "Tradeable. Deal 3 damage to all minions"
	name_CN = "火热促销"
	def text(self, CHN):
		return (3 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		damage = (3 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		targets = self.Game.minionsonBoard(1) + self.Game.minionsonBoard(2)
		self.dealsAOE(targets, [damage] * len(targets))
		return None


class SanctumChandler(Minion):
	Class, race, name = "Mage", "Elemental", "Sanctum Chandler"
	mana, attack, health = 5, 4, 5
	index = "STORMWIND~Mage~Minion~5~4~5~Elemental~Sanctum Chandler"
	requireTarget, effects, description = False, "", "After you cast a Fire spell, draw a spell"
	name_CN = "圣殿蜡烛商"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_SanctumChandler(self)]

class Trig_SanctumChandler(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["SpellBeenPlayed"])
	
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject.ID == self.entity.ID and self.entity.onBoard and subject.school == "Fire"
	
	def text(self, CHN):
		return "在你施放一个火焰法术后，抽一张法术牌" if CHN else "After you cast a Fire spell, draw a spell"
	
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		spells = [i for i, card in enumerate(self.entity.Game.Hand_Deck.decks[self.entity.ID]) if card.type == "Spell"]
		if spells: self.entity.Game.Hand_Deck.drawCard(self.entity.ID, npchoice(spells))
		

class ClumsyCourier(Minion):
	Class, race, name = "Mage", "", "Clumsy Courier"
	mana, attack, health = 7, 4, 5
	index = "STORMWIND~Mage~Minion~7~4~5~~Clumsy Courier~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Cast the highest Cost spell from your hand"
	name_CN = "笨拙的信使"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		spells, highestCost = [], -1
		for i, card in enumerate(self.Game.Hand_Deck.hands[self.ID]):
			if card.type == "Spell":
				if card.mana > highestCost: spells, highestCost = [i], card.mana
				elif card.mana == highestCost: spells.append(i)
		if spells: self.Game.Hand_Deck.extractfromHand(npchoice(spells), self.ID)[0].cast()
		return None


class GrandMagusAntonidas(Minion):
	Class, race, name = "Mage", "", "Grand Magus Antonidas"
	mana, attack, health = 8, 6, 6
	index = "STORMWIND~Mage~Minion~8~6~6~~Grand Magus Antonidas~Battlecry~Legendary"
	requireTarget, effects, description = False, "", "Battlecry: If you've cast a Fire spell on each of your last three turns, cast 3 Fireballs at random enemies. (0/3)"
	name_CN = "大魔导师安东尼达斯"
	
	def effCanTrig(self):
		cardsEachTurn = self.Game.Counters.cardsPlayedEachTurn[self.ID]
		self.effectViable = len(cardsEachTurn) > 3 and all(any(card.school == "Fire" for card in cardsEachTurn[i]) for i in (-2, -3, -4))
	
	def	text(self, CHN):
		cardsEachTurn = self.Game.Counters.cardsPlayedEachTurn[self.ID]
		turns_Indices = [-i for i in range(2, min(4, len(cardsEachTurn)))]
		return "%d/3"%sum(any(card.school == "Fire" for card in cardsEachTurn[i]) for i in turns_Indices)
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		cardsEachTurn = self.Game.Counters.cardsPlayedEachTurn[self.ID]
		if len(cardsEachTurn) > 3 and all(any(card.school == "Fire" for card in cardsEachTurn[i]) for i in (-2, -3, -4)):
			for num in range(3):
				objs = self.Game.charsAlive(3-self.ID)
				if objs: Fireball(self.Game, self.ID).cast(target=npchoice(objs))
				else: break
		return None
	
	
"""Paladin Cards"""
class BlessedGoods(Spell):
	Class, school, name = "Paladin", "Holy", "Blessed Goods"
	requireTarget, mana, effects = False, 1, ""
	index = "STORMWIND~Paladin~Spell~1~Holy~Blessed Goods"
	description = "Discover a Secret, Weapon, or Divine Shield minion"
	name_CN = "受祝福的货物"
	poolIdentifier = "Divine Shield Minions as Paladin"
	@classmethod
	def generatePool(cls, pools):
		classes, lists = [], []
		for Class in pools.Classes:
			secrets = [card for card in pools.ClassCards[Class] if card.description.startswith("Secret:")]
			if secrets:
				classes.append(Class + " Secrets")
				lists.append(secrets)
		neutralWeapons = [card for card in pools.NeutralCards if card.type == "Weapon"]
		for Class in pools.Classes:
			weapons = neutralWeapons + [card for card in pools.ClassCards[Class] if card.type == "Weapon"]
			classes.append("Weapons as "+Class)
			lists.append(weapons)
		neutralDivineShields = [card for card in pools.NeutralCards if "~Divine Shield~" in card.index]
		for Class in pools.Classes:
			minions = neutralDivineShields + [card for card in pools.ClassCards[Class] if "~Divine Shield~" in card.index]
			classes.append("Divine Shield as " + Class)
			lists.append(minions)
		return classes, lists
	
	def decidePool(self):
		Class = classforDiscover(self)
		HeroClass = self.Game.heroes[self.ID].Class
		key = HeroClass + " Secrets" if HeroClass in ["Hunter", "Mage", "Paladin", "Rogue"] else "Paladin Secrets"
		return [self.rngPool(key), self.rngPool("Weapons as " + Class), self.rngPool("Divine Shield as " + Class)]
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.discoverandGenerate_MultiplePools(BlessedGoods, comment, poolsFunc=lambda : BlessedGoods.decidePool(self))
		return None
	

class PrismaticJewelKit(Weapon):
	Class, name, description = "Paladin", "Prismatic Jewel Kit", "After a friendly minion loses Divine Shield, give minions in your hand +1/+1. Lose 1 Durability"
	mana, attack, durability, effects = 1, 0, 3, ""
	index = "STORMWIND~Paladin~Weapon~1~0~3~Prismatic Jewel Kit"
	name_CN = "棱彩珠宝工具"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_PrismaticJewelKit(self)]

class Trig_PrismaticJewelKit(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["CharLoses_Divine Shield"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject.ID == self.entity.ID and self.entity.onBoard
	
	def text(self, CHN):
		return "在一个友方随从失去圣盾后，使你手牌中的随从牌获得+1/+1。失去1点耐久度" if CHN \
			else "After a friendly minion loses Divine Shield, give minions in your hand +1/+1. Lose 1 Durability"
	
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		for card in self.entity.Game.Hand_Deck.hands[self.entity.ID]:
			if card.type == "Minion": card.getsEffect("Divine Shield")
		self.entity.loseDurability()


class Trig_RisetotheOccasion(Trig_Quest):
	def __init__(self, entity):
		super().__init__(entity, ["MinionBeenPlayed", "SpellBeenPlayed", "WeaponBeenPlayed", "HeroBeenPlayed"])
		self.numNeeded, self.newQuest, self.reward = 3, PavetheWay, None
		self.cardsPlayed = []
	
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject.ID == self.entity.ID and number == 1 and type(subject) not in self.cardsPlayed
	
	def handleCounter(self, signal, ID, subject, target, number, comment, choice=0):
		self.cardsPlayed.append(type(subject))
		self.counter += 1

	def questEffect(self, quest, game, ID):
		quest.equipWeapon(LightsJustice(game, ID))

	def createCopy(self, game):
		if self not in game.copiedObjs:  #这个扳机没有被复制过
			entityCopy = self.entity.createCopy(game)
			trigCopy = self.selfCopy(entityCopy)
			trigCopy.cardsPlayed = self.cardsPlayed[:]
			trigCopy.counter = self.counter
			game.copiedObjs[self] = trigCopy
			return trigCopy
		else:  #一个扳机被复制过了，则其携带者也被复制过了
			return game.copiedObjs[self]

class Trig_PavetheWay(Trig_RisetotheOccasion):
	def __init__(self, entity):
		super().__init__(entity)
		self.numNeeded, self.newQuest, self.reward = 3, AvengetheFallen, None
	
	def questEffect(self, quest, game, ID):
		power = game.powers[ID]
		if type(power) in Basicpowers:
			Upgradedpowers[Basicpowers.index(type(power))](game, ID).replaceHeroPower()
			
class Trig_AvengetheFallen(Trig_RisetotheOccasion):
	def __init__(self, entity):
		super().__init__(entity)
		self.numNeeded, self.newQuest, self.reward = 3, None, LightbornCariel


class RisetotheOccasion(Questline):
	Class, name = "Paladin", "Rise to the Occasion"
	requireTarget, mana, effects = False, 1, ""
	index = "STORMWIND~Paladin~Spell~1~~Rise to the Occasion~~Questline~Legendary"
	description = "Questline: Play 3 different 1-Cost cards. Reward: Equip a 1/4 Light's Justice"
	name_CN = "挺身而出"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_RisetotheOccasion(self)]
		
class PavetheWay(Questline):
	Class, name = "Paladin", "Pave the Way"
	requireTarget, mana, effects = False, -1, ""
	index = "STORMWIND~Paladin~Spell~0~~Pave the Way~~Questline~Legendary~Uncollectible"
	description = "Questline: Play 3 different 1-Cost cards. Reward: Upgrade your Hero Power"
	name_CN = "荡平道路"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_PavetheWay(self)]

class AvengetheFallen(Questline):
	Class, name = "Paladin", "Pave the Way"
	requireTarget, mana, effects = False, -1, ""
	index = "STORMWIND~Paladin~Spell~0~~Pave the Way~~Questline~Legendary~Uncollectible"
	description = "Questline: Play 3 different 1-Cost cards. Reward: Upgrade your Hero Power"
	name_CN = "为逝者复仇"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_AvengetheFallen(self)]

class LightbornCariel(Minion):
	Class, race, name = "Paladin", "", "Lightborn Cariel"
	mana, attack, health = 5, 7, 7
	index = "STORMWIND~Paladin~Minion~5~7~7~~Lightborn Cariel~Battlecry~Legendary~Uncollectible"
	requireTarget, effects, description = False, "", "Battlecry: For the rest of the game, your Silver Hand Recruits have +2/+2"
	name_CN = "圣光化身凯瑞尔"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		GameTrigAura_BuffYourRecruits(self.Game, self.ID).auraAppears()
		return None


class GameTrigAura_BuffYourRecruits(HasAura_toMinion):
	def __init__(self, Game, ID):
		self.Game, self.ID = Game, ID
		self.auraAffected = []
		self.buff = 2
		
	#All minions appearing on the same side will be subject to the buffAura.
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject.ID == self.ID and subject.name == "Silver Hand Recruit"
	
	def trig(self, signal, ID, subject, target, number, comment, choice=0):
		if self.canTrig(signal, ID, subject, target, number, comment):
			Aura_Receiver(subject, self, self.buff, self.buff).effectStart()
	
	def text(self, CHN):
		return "在本局对战的剩余时间内，你的白银之手新兵获得+%d/+%d" % (self.buff, self.buff) if CHN \
			else "For the rest of the game, your Silver Hand Recruits have +%d/+%d" % (self.buff, self.buff)
	
	def auraAppears(self):
		trigAuras = self.Game.trigAuras[self.ID]
		for obj in trigAuras:
			if isinstance(obj, GameTrigAura_BuffYourRecruits):
				obj.improve()
				return
		trigAuras.append(self)
		for minion in self.Game.minionsonBoard(self.ID):
			if minion.name == "Silver Hand Recruit": Aura_Receiver(minion, self, self.buff, self.buff).effectStart()
		try: self.Game.trigsBoard[self.ID]["MinionAppears"].append(self)
		except: pass
	
	#没有auraDisappear方法
	#可以通过HasAura_toMinion的createCopy方法复制
	def improve(self):
		self.buff += 2
		for minion, receiver in self.auraAffected[:]:
			receiver.effectClear()
		self.auraAffected = []
		for minion in self.Game.minionsonBoard(self.ID):
			if minion.name == "Silver Hand Recruit": Aura_Receiver(minion, self, self.buff, self.buff).effectStart()
	
	#这个函数会在复制场上扳机列表的时候被调用。
	def createCopy(self, game):
		#一个光环的注册可能需要注册多个扳机
		if self not in game.copiedObjs:  #这个光环没有被复制过
			entityCopy = self.entity.createCopy(game)
			Copy = self.selfCopy(entityCopy)
			game.copiedObjs[self] = Copy
			Copy.buff = self.buff
			for minion, receiver in self.auraAffected:
				minionCopy = minion.createCopy(game)
				index = minion.auraReceivers.index(receiver)
				receiverCopy = minionCopy.auraReceivers[index]
				receiverCopy.source = Copy  #补上这个receiver的source
				Copy.auraAffected.append((minionCopy, receiverCopy))
			return Copy
		else:
			return game.copiedObjs[self]


class NobleMount(Spell):
	Class, school, name = "Paladin", "", "Noble Mount"
	requireTarget, mana, effects = True, 2, ""
	index = "STORMWIND~Paladin~Spell~2~~Noble Mount"
	description = "Give a minion +1/+1 and Divine Shield. When it dies, summon a Warhorse"
	name_CN = "神圣坐骑"
	
	def available(self):
		return self.selectableMinionExists()
	
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			target.buffDebuff(1, 1)
			target.getsEffect("Divine Shield")
			target.getsTrig(SummonaWarhorse(target), trigType="Deathrattle", connect=target.onBoard)
		return target

class SummonaWarhorse(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		minion = self.entity
		minion.Game.summon(CarielsWarhorse(minion.Game, minion.ID), minion.pos + 1, summoner=minion)
	
	def text(self, CHN):
		return "亡语：召唤一只1/1的战马" if CHN else "Deathrattle: Summon a 1/1 Warhorse"

class CarielsWarhorse(Minion):
	Class, race, name = "Paladin", "Beast", "Cariel's Warhorse"
	mana, attack, health = 1, 1, 1
	index = "STORMWIND~Paladin~Minion~1~1~1~Beast~Cariel's Warhorse~Divine Shield~Uncollectible"
	requireTarget, effects, description = False, "Divine Shield", "Divine Shield"
	name_CN = "卡瑞尔的战马"
	
	
class CityTax(Spell):
	Class, school, name = "Paladin", "", "City Tax"
	requireTarget, mana, effects = False, 2, "Lifesteal"
	index = "STORMWIND~Paladin~Spell~2~~City Tax~Lifesteal~Tradeable"
	description = "Tradeable. Lifesteal. Deal 1 damage to all enemy minions"
	name_CN = "城建税"
	def text(self, CHN):
		return (1 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		damage = (1 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		targets = self.Game.minionsonBoard(3-self.ID)
		self.dealsAOE(targets, [damage] * len(targets))
		return None
	
	
class AllianceBannerman(Minion):
	Class, race, name = "Paladin", "", "Alliance Bannerman"
	mana, attack, health = 3, 2, 2
	index = "STORMWIND~Paladin~Minion~3~2~2~~Alliance Bannerman~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Draw a minion. Give minions in your hand +1/+1"
	name_CN = "联盟旗手"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		minions = [i for i, card in enumerate(self.Game.Hand_Deck.decks[self.ID]) if card.type == "Minion"]
		if minions:
			self.Game.Hand_Deck.drawCard(self.ID, npchoice(minions))
			for card in self.Game.Hand_Deck.hands[self.ID]:
				if card.type == "Minion": card.buffDebuff(1, 1)
		return None


class CatacombGuard(Minion):
	Class, race, name = "Paladin", "", "Catacomb Guard"
	mana, attack, health = 3, 1, 4
	index = "STORMWIND~Paladin~Minion~3~1~4~~Catacomb Guard~Lifesteal~Battlecry"
	requireTarget, effects, description = True, "Lifesteal", "Lifesteal. Battlecry: Deal damage equal to this minin's Attack to an enemy minion"
	name_CN = "古墓卫士"
	
	def targetExists(self, choice=0):
		return self.selectableEnemyMinionExists()
	
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.ID != self.ID and target.onBoard
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target and self.attack > 0:
			self.dealsDamage(target, self.attack)
		return None


class LightbringersHammer(Weapon):
	Class, name, description = "Paladin", "Lightbringer's Hammer", "Lifesteal. Can't attack heroes"
	mana, attack, durability, effects = 3, 3, 2, "Lifesteal,Can't Attack Heroes"
	index = "STORMWIND~Paladin~Weapon~3~3~2~Lightbringer's Hammer~Lifesteal"
	name_CN = "光明使者之锤"
	
	
class FirstBladeofWrynn(Minion):
	Class, race, name = "Paladin", "", "First Blade of Wrynn"
	mana, attack, health = 4, 3, 5
	index = "STORMWIND~Paladin~Minion~4~3~5~~First Blade of Wrynn~Divine Shield~Battlecry"
	requireTarget, effects, description = False, "Divine Shield", "Divine Shield. Battlecry: Gain Rush if this has at least 4 Attack"
	name_CN = "乌瑞恩首席剑士"
	
	def effCanTrig(self):
		self.effectViable = self.attack > 3
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if self.attack > 3: self.getsEffect("Rush")
		return None


class HighlordFordragon(Minion):
	Class, race, name = "Paladin", "", "Highlord Fordragon"
	mana, attack, health = 6, 5, 5
	index = "STORMWIND~Paladin~Minion~6~5~5~~Highlord Fordragon~Divine Shield~Legendary"
	requireTarget, effects, description = False, "Divine Shield", "Divine Shield. After a friendly minion loses Divine Shield, give a minion in your hand +5/+5"
	name_CN = "大领主弗塔根"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_HighlordFordragon(self)]

class Trig_HighlordFordragon(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["CharLoses_Divine Shield"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject.ID == self.entity.ID
	
	def text(self, CHN):
		return "在一个友方随从失去圣盾后，使你手牌中的一张随从牌获得+5/+5" if CHN \
				else "After a friendly minion loses Divine Shield, give a minion in your hand +5/+5"
	
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		minions = [card for card in self.entity.Game.Hand_Deck.hands[self.entity.ID] if card.type == "Minion"]
		if minions: npchoice(minions).buffDebuff(5, 5)
		
		
"""Priest Cards"""
class CalloftheGrave(Spell):
	Class, school, name = "Priest", "Shadow", "Call of the Grave"
	requireTarget, mana, effects = False, 1, ""
	index = "STORMWIND~Priest~Spell~1~Shadow~Call of the Grave"
	description = "Discover a Deathrattle minion. If you have enough Mana to play it, trigger its Deathrattle"
	name_CN = "墓园召唤"
	poolIdentifier = "Deathrattle Minions as Priest"
	@classmethod
	def generatePool(cls, pools):
		classCards = {s: [card for card in pools.ClassCards[s] if card.type == "Minion" and "~Deathrattle" in card.index] for s in pools.Classes}
		classCards["Neutral"] = [card for card in pools.NeutralCards if card.type == "Minion" and "~Deathrattle" in card.index]
		return ["Deathrattle Minions as " + Class for Class in pools.Classes], \
			   [classCards[Class] + classCards["Neutral"] for Class in pools.Classes]
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.discoverandGenerate(CalloftheGrave, comment, lambda : self.rngPool("Deathrattle Minions as " + classforDiscover(self)))
		return None
	
	def discoverDecided(self, option, case, info_RNGSync=None, info_GUISync=None):
		self.handleDiscoverGeneratedCard(option, case, info_RNGSync, info_GUISync)
		if option.mana <= self.Game.Manas.manas[self.ID]:
			for trig in option.deathrattles:
				trig.trig("TrigDeathrattle", self.ID, None, option, option.attack, "")


class Trig_SeekGuidance(Trig_Quest):
	def __init__(self, entity):
		super().__init__(entity, ["MinionBeenPlayed", "SpellBeenPlayed", "WeaponBeenPlayed", "HeroBeenPlayed"])
		self.numNeeded, self.newQuest, self.reward = 3, DiscovertheVoidShard, None
		self.costs = [2, 3, 4]
	
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject.ID == self.entity.ID and number in self.costs
	
	def handleCounter(self, signal, ID, subject, target, number, comment, choice=0):
		self.costs.remove(number)
		self.counter += 1
	
	def questEffect(self, quest, game, ID):
		quest.discoverfromList(SeekGuidance, '', conditional=lambda card: True)
	
	def createCopy(self, game):
		if self not in game.copiedObjs:  #这个扳机没有被复制过
			entityCopy = self.entity.createCopy(game)
			trigCopy = self.selfCopy(entityCopy)
			trigCopy.costs = self.costs[:]
			trigCopy.counter = self.counter
			game.copiedObjs[self] = trigCopy
			return trigCopy
		else:  #一个扳机被复制过了，则其携带者也被复制过了
			return game.copiedObjs[self]

class Trig_DiscovertheVoidShard(Trig_SeekGuidance):
	def __init__(self, entity):
		super().__init__(entity)
		self.numNeeded, self.newQuest, self.reward = 2, IlluminatetheVoid, None
		self.costs = [5, 6]

class Trig_IlluminatetheVoid(Trig_SeekGuidance):
	def __init__(self, entity):
		super().__init__(entity)
		self.numNeeded, self.newQuest, self.reward = 2, None, XyrellatheSanctified
		self.costs = [7, 8]

class SeekGuidance(Questline):
	Class, name = "Priest", "Seek Guidance"
	requireTarget, mana, effects = False, 1, ""
	index = "STORMWIND~Priest~Spell~1~~Seek Guidance~~Questline~Legendary"
	description = "Questline: Play a 2, 3, and 4-Cost card. Reward: Discover a card from your deck"
	name_CN = "寻求指引"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_SeekGuidance(self)]
	
	def discoverDecided(self, option, case, info_RNGSync=None, info_GUISync=None):
		self.handleDiscoveredCardfromList(option, case, ls=self.Game.Hand_Deck.decks[self.ID],
										  func=lambda index, card: self.Game.Hand_Deck.drawCard(self.ID, index),
										  info_RNGSync=info_RNGSync, info_GUISync=info_GUISync)

class DiscovertheVoidShard(Questline):
	Class, name = "Priest", "Discover the Void Shard"
	requireTarget, mana, effects = False, -1, ""
	index = "STORMWIND~Priest~Spell~0~~Discover the Void Shard~~Questline~Legendary~Uncollectible"
	description = "Questline: Play a 5, and 6-Cost card. Reward: Discover a card from your deck"
	name_CN = "发现虚空碎片"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_DiscovertheVoidShard(self)]
	
class IlluminatetheVoid(Questline):
	Class, name = "Priest", "Illuminate the Void"
	requireTarget, mana, effects = False, -1, ""
	index = "STORMWIND~Priest~Spell~0~~Illuminate the Void~~Questline~Legendary~Uncollectible"
	description = "Questline: Play a 7, and 8-Cost card. Reward: Xyrella, the Sanctified"
	name_CN = "照亮虚空"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_IlluminatetheVoid(self)]
	
class XyrellatheSanctified(Minion):
	Class, race, name = "Priest", "", "Xyrella, the Sanctified"
	mana, attack, health = 5, 7, 7
	index = "STORMWIND~Priest~Minion~5~7~7~~Xyrella, the Sanctified~Battlecry~Legendary~Uncollectible"
	requireTarget, effects, description = False, "", "Battlecry: Shuffle the Purifid Shard into your deck"
	name_CN = "圣徒泽瑞拉"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.Game.Hand_Deck.shuffleintoDeck(PurifiedShard(self.Game, self.ID), initiatorID=self.ID, creator=self)
		return None

class PurifiedShard(Spell):
	Class, school, name = "Priest", "Holy", "Purified Shard"
	requireTarget, mana, effects = False, 10, ""
	index = "STORMWIND~Priest~Spell~10~Holy~Purified Shard~Legendary~Uncollectible"
	description = "Destroy the enemy hero"
	name_CN = "净化的碎片"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.Game.killMinion(self, self.Game.heroes[3-self.ID])
		return None


class ShardoftheNaaru(Spell):
	Class, school, name = "Priest", "Holy", "Shard of the Naaru"
	requireTarget, mana, effects = False, 1, ""
	index = "STORMWIND~Priest~Spell~1~Holy~Shard of the Naaru~Tradeable"
	description = "Tradeable. Silence all enemy minions"
	name_CN = "纳鲁碎片"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		for minion in self.Game.minionsonBoard(3-self.ID):
			minion.getsSilenced()
		return None


class VoidtouchedAttendant(Minion):
	Class, race, name = "Priest", "", "Voidtouched Attendant"
	mana, attack, health = 1, 1, 3
	index = "STORMWIND~Priest~Minion~1~1~3~~Voidtouched Attendant"
	requireTarget, effects, description = False, "", "Both heroes take one extra damage from all source"
	name_CN = "虚触侍从"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_VoidtouchedAttendant(self)]

class Trig_VoidtouchedAttendant(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["FinalDmgonHero?"])
	
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and target.type == "Hero"
	
	def text(self, CHN):
		return "双方英雄受到的所有伤害提高一点" if CHN else "Both heroes take one extra damage from all source"
	
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		number[0] += 1


class ShadowclothNeedle(Weapon):
	Class, name, description = "Priest", "Shadowcloth Needle", "After you cast a Shadow spell, deal 1 damage to all enemies. Lose 1 Durability"
	mana, attack, durability, effects = 2, 0, 3, ""
	index = "STORMWIND~Priest~Weapon~2~0~3~Shadowcloth Needle"
	name_CN = "暗影布缝针"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_ShadowclothNeedle(self)]

class Trig_ShadowclothNeedle(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["SpellBeenPlayed"])
	
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject.ID == self.entity.ID and self.entity.health > 0 and self.entity.onBoard and subject.school == "Shadow"
	
	def text(self, CHN):
		return "在你释放一个暗影法术之后，对所有敌人造成1点伤害。失去1点耐久度" if CHN \
			else "After you cast a Shadow spell, deal 1 damage to all enemies. Lose 1 Durability"
	
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		weapon = self.entity
		targets = weapon.Game.minionsonBoard(3-weapon.ID) + [weapon.Game.heroes[3-weapon.ID]]
		weapon.dealsAOE(targets, [1] * len(targets))
		weapon.loseDurability()


class TwilightDeceptor(Minion):
	Class, race, name = "Priest", "", "Twilight Deceptor"
	mana, attack, health = 2, 2, 3
	index = "STORMWIND~Priest~Minion~2~2~3~~Twilight Deceptor~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: If any hero took damage this turn, draw a Shadow spell"
	name_CN = "暮光欺诈者"
	
	def effCanTrig(self):
		self.effectViable = self.Game.Counters.dmgonHeroThisTurn[1] + self.Game.Counters.dmgonHeroThisTurn[2] > 0
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if self.Game.Counters.dmgonHeroThisTurn[1] + self.Game.Counters.dmgonHeroThisTurn[2] > 0:
			spells = [i for i, card in enumerate(self.Game.Hand_Deck.decks[self.ID]) if card.type == "Spell" and card.school == "Shadow"]
			if spells: self.Game.Hand_Deck.drawCard(self.ID, npchoice(spells))
		return None


class Psyfiend(Minion):
	Class, race, name = "Priest", "", "Psyfiend"
	mana, attack, health = 3, 3, 4
	index = "STORMWIND~Priest~Minion~3~3~4~~Psyfiend"
	requireTarget, effects, description = False, "", "After you cast a Shadow spell, dead 2 damage to each hero"
	name_CN = "灵能魔"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_Psyfiend(self)]

class Trig_Psyfiend(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["SpellBeenPlayed"])
	
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject.ID == self.entity.ID and subject.school == "Shadow"
	
	def text(self, CHN):
		return "在你释放一个暗影法术之后，对双方英雄造成2点伤害" if CHN \
			else "After you cast a Shadow spell, dead 2 damage to each hero"
	
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.dealsAOE(list(self.entity.Game.heroes.values()), [2, 2])


class VoidShard(Spell):
	Class, school, name = "Priest", "Shadow", "Void Shard"
	requireTarget, mana, effects = True, 4, "Lifesteal"
	index = "STORMWIND~Priest~Spell~4~Shadow~Void Shard~Lifesteal"
	description = "Lifesteal. Deal 4 damage"
	name_CN = "虚空碎片"
	def text(self, CHN):
		return (4 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			damage = (4 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			self.dealsDamage(target, damage)
		return target
	
	
class DarkbishopBenedictus(Minion):
	Class, race, name = "Priest", "", "Darkbishop Benedictus"
	mana, attack, health = 5, 5, 6
	index = "STORMWIND~Druid~Minion~5~5~6~~Darkbishop Benedictus~Legendary~Start of Game"
	requireTarget, effects, description = False, "", "Start of Game: If the spells in your deck are all Shadow, enter Shadowform"
	name_CN = "黑暗主教本尼迪塔斯"
	def startofGame(self):
		#all([]) returns True
		print("Darkbishop test", all(card.school == "Shadow" for card in self.Game.Hand_Deck.initialDecks[self.ID] if card.type == "Spell"))
		if all(card.school == "Shadow" for card in self.Game.Hand_Deck.initialDecks[self.ID] if card.type == "Spell"):
			MindSpike(self.Game, self.ID).replaceHeroPower()
			
			
class ElekkMount(Spell):
	Class, school, name = "Priest", "", "Elekk Mount"
	requireTarget, mana, effects = True, 7, ""
	index = "STORMWIND~Priest~Spell~7~~Elekk Mount"
	description = "Give a minion +4/+7 and Taunt. When it dies, summon an Elekk"
	name_CN = "雷象坐骑"
	def available(self):
		return self.selectableMinionExists()
	
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			target.buffDebuff(4, 7)
			target.getsEffect("Taunt")
			target.getsTrig(SummonanElekk(target), trigType="Deathrattle", connect=target.onBoard)
		return target

class SummonanElekk(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		minion = self.entity
		minion.Game.summon(XyrellasElekk(minion.Game, minion.ID), minion.pos+1, summoner=minion)
	
	def text(self, CHN):
		return "亡语：召唤一只4/7的雷象" if CHN else "Deathrattle: Summon a 4/7 Elekk"

class XyrellasElekk(Minion):
	Class, race, name = "Priest", "Beast", "Xyrella's Elekk"
	mana, attack, health = 6, 4, 7
	index = "STORMWIND~Priest~Minion~6~4~7~Beast~Xyrella's Elekk~Taunt~Uncollectible"
	requireTarget, effects, description = False, "Taunt", "Taunt"
	name_CN = "泽瑞拉的雷象"


"""Rogue Cards"""
class FizzflashDistractor(Spell):
	Class, school, name = "Rogue", "", "Fizzflash Distractor"
	requireTarget, mana, effects = True, 1, ""
	index = "STORMWIND~Rogue~Spell~1~~Fizzflash Distractor~Uncollectible"
	description = "Return a minion to its owner's hand. They can't play it next turn"
	name_CN = "声光干扰器"
	
	def available(self):
		return self.selectableEnemyMinionExists()
	
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard and target.ID != self.ID
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target and target.onBoard:
			self.Game.returnObj2Hand(target)
			FizzflashDistractor_Effect(self.Game, self.ID, target)
		return target

class FizzflashDistractor_Effect:
	def __init__(self, Game, ID, card):
		self.Game, self.ID = Game, ID
		self.signals = ["TurnStarts", "TurnEnds", "CardEntersHand", "CardLeavesHand"]
		self.card = FizzflashDistractor(Game, ID)
		self.cardBanned = card
		self.on = False
		
	def connect(self):
		trigs = self.Game.trigsBoard[self.ID]
		if not any(any(isinstance(trig, FizzflashDistractor_Effect) and trig.cardBanned == self.cardBanned
					   for trig in trigs[sig])
				   for sig in self.signals):
			for sig in self.signals:
				try: trigs[sig].append(self)
				except: trigs[sig] = [self]
			if self.Game.GUI: self.Game.GUI.heroZones[self.ID].addaTrig(self.card)
	
	def disconnect(self):
		trigs = self.Game.trigsBoard[self.ID]
		for sig in self.signals:
			try: trigs[sig].remove(self)
			except: pass
		if self.cardBanned.inHand and self.cardBanned.btn: panda_CardPlayableAgain(self.cardBanned)
		if self.Game.GUI: self.Game.GUI.heroZones[self.ID].removeaTrig(self.card)
	
	#number here is a list that holds the damage to be processed
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		if signal == "TurnStarts": return True
		elif signal == "TurnEnds": return self.on
		elif signal == "CardEntersHand": return self.on and target[0] == self.cardBanned
		else: return self.on and subject == self.cardBanned
		
	def trig(self, signal, ID, subject, target, number, comment, choice=0):
		if self.canTrig(signal, ID, subject, target, number, comment):
			self.effect(signal, ID, subject, target, number, comment)
	
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		if signal == "TurnStarts":
			self.on = True
			if self.cardBanned.inHand:
				self.cardBanned.effects["Can't be Played"] += 1
				if self.cardBanned.btn: panda_CardBecomesNotPlayable(self.cardBanned)
		elif signal == "TurnEnds" and self.on:
			self.on = False
			self.disconnect()
		elif signal == "CardEntersHand" and self.on:
			self.cardBanned.effects["Can't be Played"] += 1
			if self.cardBanned.btn: panda_CardBecomesNotPlayable(self.cardBanned)
		elif signal == "CardLeavesHand" and self.on:
			self.cardBanned.effects["Can't be Played"] -= 1
			if self.cardBanned.btn: panda_CardPlayableAgain(self.cardBanned)
		
	def createCopy(self, game):  #不是纯的只在回合结束时触发，需要完整的createCopy
		if self not in game.copiedObjs:  #这个扳机没有被复制过
			trigCopy = type(self)(game, self.ID, self.cardBanned)
			trigCopy.on = self.on
			game.copiedObjs[self] = trigCopy
			return trigCopy
		else:  #一个扳机被复制过了，则其携带者也被复制过了
			return game.copiedObjs[self]


def panda_CardBecomesNotPlayable(card):
	texCard = card.Game.GUI.loader.load("TexCards\\Shared\\Crossed.egg")
	texCard.name = "Crossed_Img"
	texCard.find("+SequenceNode").node().pose(0)
	card.btn.np.attachNewNode(texCard)
	
def panda_CardPlayableAgain(card):
	try: card.btn.np.find("Crossed_Img").removeNode()
	except: pass


class Spyomatic(Minion):
	Class, race, name = "Rogue", "Mech", "Spy-o-matic"
	mana, attack, health = 1, 3, 2
	index = "STORMWIND~Rogue~Minion~1~3~2~Mech~Spy-o-matic~Battlecry~Uncollectible"
	requireTarget, effects, description = False, "", "Battlecry: Look at 3 cards in your opponent's deck. Choose one to put on top"
	name_CN = "间谍机器人"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.discoverfromList(Spyomatic, comment, conditional=lambda card: True,
							  ls=self.Game.Hand_Deck.decks[3-self.ID])
		return None
	
	def discoverDecided(self, option, case, info_RNGSync=None, info_GUISync=None):
		deck = self.Game.Hand_Deck.decks[3-self.ID]
		self.handleDiscoveredCardfromList(option, case, ls=deck,
										  func=lambda index, card: deck.append(deck.pop(index)),
										  info_RNGSync=info_RNGSync, info_GUISync=info_GUISync)
		

class NoggenFogGenerator(Spell):
	Class, school, name = "Rogue", "", "Noggen-Fog Generator"
	requireTarget, mana, effects = True, 1, ""
	index = "STORMWIND~Rogue~Spell~1~~Noggen-Fog Generator~Uncollectible"
	description = "Give a minion +2 Attack and Stealth"
	name_CN = "迷雾发生器"
	
	def available(self):
		return self.selectableMinionExists()
	
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			target.buffDebuff(2, 0)
			target.getsEffect("Stealth")
		return target
	
	
class HiddenGyroblade(Weapon):
	Class, name, description = "Rogue", "Hidden Gyroblade", "Deathrattle: Throw this at a random enemy minion"
	mana, attack, durability, effects = 1, 3, 2, ""
	index = "STORMWIND~Rogue~Weapon~1~3~2~Hidden Gyroblade~Deathrattle~Uncollectible"
	name_CN = "隐蔽式旋刃"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.deathrattles = [ThrowThisatanEnemyMinion(self)]

class ThrowThisatanEnemyMinion(Deathrattle_Weapon):
	def text(self, CHN):
		return "亡语：随机将武器投向一个敌方随从" if CHN else "Deathrattle: Throw this at a random enemy minion"
	
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		minions = self.entity.Game.minionsAlive(3-self.entity.ID)
		if minions:
			print("Dealing damage to minion", self.entity, minions, number)
			self.entity.dealsDamage(npchoice(minions), number)


class UndercoverMole(Minion):
	Class, race, name = "Rogue", "Beast", "Undercover Mole"
	mana, attack, health = 1, 2, 3
	index = "STORMWIND~Rogue~Minion~1~2~3~Beast~Undercover Mole~Stealth~Uncollectible"
	requireTarget, effects, description = False, "Stealth", "Stealth. After this attacks, add a random card to your hand. (From your opponent's class)"
	name_CN = "潜藏的鼹鼠"
	poolIdentifier = "Rogue Cards"
	@classmethod
	def generatePool(cls, pools):
		return ["%s Cards" % Class for Class in pools.Classes], \
			   [pools.ClassCards[Class] for Class in pools.Classes]
	
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_UndercoverMole(self)]

class Trig_UndercoverMole(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["MinionAttackedMinion", "MinionAttackedHero"])
	
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject == self.entity and self.entity.onBoard
	
	def text(self, CHN):
		return "在该随从攻击后，随机将一张(你对手职业的卡牌置入你的手牌)" if CHN else "Whenever this attacks a minion, Silence it"
	
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.addCardtoHand(npchoice(self.rngPool(self.entity.Game.heroes[3-self.entity.ID].Class+" Cards"), self.entity.ID))


SpyGizmos = [FizzflashDistractor, Spyomatic, NoggenFogGenerator, HiddenGyroblade, UndercoverMole]

class Trig_FindtheImposter(Trig_Quest):
	def __init__(self, entity):
		super().__init__(entity, ["MinionBeenPlayed", "SpellBeenPlayed", "WeaponBeenPlayed", "HeroBeenPlayed"])
		self.numNeeded, self.newQuest, self.reward = 2, LearntheTruth, None
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject.ID == self.entity.ID and "SI:7" in subject.name
	
	def questEffect(self, quest, game, ID):
		quest.addCardtoHand(npchoice(SpyGizmos), ID)
	
class Trig_LearntheTruth(Trig_FindtheImposter):
	def __init__(self, entity):
		super().__init__(entity)
		self.numNeeded, self.newQuest, self.reward = 2, MarkedaTraitor, None
		
class Trig_MarkedaTraitor(Trig_FindtheImposter):
	def __init__(self, entity):
		super().__init__(entity)
		self.numNeeded, self.newQuest, self.reward = 2, None, SpymasterScabbs
		
class FindtheImposter(Questline):
	Class, name = "Rogue", "Find the Imposter"
	requireTarget, mana, effects = False, 1, ""
	index = "STORMWIND~Rogue~Spell~1~~Find the Imposter~~Questline~Legendary"
	description = "Questline: Play 2 SI:7 cards. Reward: Add a Spy Gizmo to your hand"
	name_CN = "探查内鬼"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_FindtheImposter(self)]
		
class LearntheTruth(Questline):
	Class, name = "Rogue", "Learn the Truth"
	requireTarget, mana, effects = False, -1, ""
	index = "STORMWIND~Rogue~Spell~0~~Learn the Truth~~Questline~Legendary~Uncollectible"
	description = "Questline: Play 2 SI:7 cards. Reward: Add a Spy Gizmo to your hand"
	name_CN = "了解真相"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_LearntheTruth(self)]

class MarkedaTraitor(Questline):
	Class, name = "Rogue", "Marked a Traitor"
	requireTarget, mana, effects = False, -1, ""
	index = "STORMWIND~Rogue~Spell~0~~Marked a Traitor~~Questline~Legendary~Uncollectible"
	description = "Questline: Play 2 SI:7 cards. Reward: Spymaster Scabbs"
	name_CN = "标出叛徒"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_MarkedaTraitor(self)]

class SpymasterScabbs(Minion):
	Class, race, name = "Rogue", "", "Spymaster Scabbs"
	mana, attack, health = 1, 7, 7
	index = "STORMWIND~Rogue~Minion~5~7~7~~Spymaster Scabbs~Battlecry~Legendary~Uncollectible"
	requireTarget, effects, description = False, "", "Battlecry: Add one of each Spy Gizmo to your hand"
	name_CN = "间谍大师卡布斯"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.addCardtoHand(SpyGizmos, self.ID)
		return None


class SI7Extortion(Spell):
	Class, school, name = "Rogue", "", "SI:7 Extortion"
	requireTarget, mana, effects = True, 1, ""
	index = "STORMWIND~Rogue~Spell~1~~SI:7 Extortion~Tradeable"
	description = "Tradeable. Deal 3 damage to an undamage character"
	name_CN = "军情七处的要挟"
	
	def available(self):
		return self.selectableMinionExists()
	
	def targetCorrect(self, target, choice=0):
		return (target.type == "Minion" or target.type == "Hero") and target.health == target.health_max and target.onBoard
	
	def text(self, CHN):
		return (3 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			damage = (3 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			self.dealsDamage(target, damage)
		return target



class Garrote(Spell):
	Class, school, name = "Rogue", "", "Garrote"
	requireTarget, mana, effects = False, 2, ""
	index = "STORMWIND~Rogue~Spell~2~~Garrote"
	description = "Deal 2 damage to the enemy hero. Shuffle 3 Bleeds into your deck that deal 2 more when drawn"
	name_CN = "锁喉"
	
	def text(self, CHN):
		return (2 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		damage = (2 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		self.dealsDamage(self.Game.heroes[3-self.ID], damage)
		self.Game.Hand_Deck.shuffleintoDeck([Bleed(self.Game, self.ID) for i in range(3)], initiatorID=self.ID)
		return None

class Bleed(Spell):
	Class, school, name = "Rogue", "", "Bleed"
	requireTarget, mana, effects = False, 1, ""
	index = "STORMWIND~Rogue~Spell~1~~Bleed~Casts When Drawn~Uncollectible"
	description = "Casts When Drawn. Deal 2 damage to the enemy hero"
	name_CN = "流血"
	
	def text(self, CHN):
		return (2 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		damage = (2 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		self.dealsDamage(self.Game.heroes[3 - self.ID], damage)
		return None

 
class MaestraoftheMasquerade(Minion):
	Class, race, name = "Rogue", "", "Maestra of the Masquerade"
	mana, attack, health = 2, 3, 2
	index = "STORMWIND~Rogue~Minion~2~3~2~~Maestra of the Masquerade~Legendary"
	requireTarget, effects, description = False, "", "You start the game as different class until you play a Rogue card"
	name_CN = "变装大师"


class CounterfeitBlade(Weapon):
	Class, name, description = "Rogue", "Counterfeit Blade", "Gain a random friendly Deathrattle that triggered this game"
	mana, attack, durability, effects = 4, 4, 2, ""
	index = "STORMWIND~Rogue~Weapon~4~4~2~Counterfeit Blade~Battlecry"
	name_CN = "伪造的匕首"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		deathrattles = self.Game.Counters.deathrattlesTriggered[self.ID]
		if deathrattles:
			#if self.Game.GUI: self.Game.GUI.showOffBoardTrig()
			self.getsTrig(npchoice(deathrattles)(self), trigType="Deathrattle", connect=self.onBoard)
		return None
	

class LoanShark(Minion):
	Class, race, name = "Rogue", "Beast", "Loan Shark"
	mana, attack, health = 3, 3, 4
	index = "STORMWIND~Rogue~Minion~3~3~4~Beast~Loan Shark~Battlecry~Deathrattle"
	requireTarget, effects, description = False, "", "Battlecry: Give your opponent a Coin. Deathrattle: You get two"
	name_CN = "放贷的鲨鱼"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.deathrattles = [GetTwoCoins(self)]

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.addCardtoHand(TheCoin, 3-self.ID)
		return None
	
class GetTwoCoins(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.addCardtoHand([TheCoin, TheCoin], self.entity.ID)
		
	def text(self, CHN):
		return "亡语：将两张幸运币置入你的手牌" if CHN else "Deathrattle: Add two Coins to your hand"


class SI7Operative(Minion):
	Class, race, name = "Rogue", "", "SI:7 Operative"
	mana, attack, health = 3, 2, 4
	index = "STORMWIND~Rogue~Minion~3~2~4~~SI:7 Operative~Rush"
	requireTarget, effects, description = False, "Rush", "Rush. After this minion attacks a minion, gain Stealth"
	name_CN = "军情七处探员"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_SI7Operative(self)]

class Trig_SI7Operative(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["MinionAttackedMinion"])
	
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject == self.entity and self.entity.onBoard
	
	def text(self, CHN):
		return "在该随从攻击一个随从后，获得潜行" if CHN else "After this minion attacks a minion, gain Stealth"
	
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.getsEffect("Stealth")
		

class SketchyInformation(Spell):
	Class, school, name = "Rogue", "", "Sketchy Information"
	requireTarget, mana, effects = False, 3, ""
	index = "STORMWIND~Rogue~Spell~3~~Sketchy Information"
	description = "Draw a Deathrattle card that costs (4) or less. Trigger its effect"
	name_CN = "简略情报"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		cards = [i for i, card in enumerate(self.Game.Hand_Deck.decks[self.ID]) if hasattr(card, "deathrattles") and card.deathrattles and card.mana < 5]
		if cards:
			card = self.Game.Hand_Deck.drawCard(self.ID, npchoice(cards))[0]
			if card:
				for trig in card.deathrattles:
					trig.trig("TrigDeathrattle", self.ID, None, card, card.attack, "")
		return None


class SI7Informant(Minion):
	Class, race, name = "Rogue", "", "SI:7 Informant"
	mana, attack, health = 4, 3, 3
	index = "STORMWIND~Rogue~Minion~4~3~3~~SI:7 Informant~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Gain +1/+1 for each SI:7 card you've played this game"
	name_CN = "军情七处线人"
	
	def effCanTrig(self):
		self.effectViable = any("SI:7" in card.index for card in self.Game.Counters.cardsPlayedThisGame[self.ID])
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		num = sum("SI:7" in card.index for card in self.Game.Counters.cardsPlayedThisGame[self.ID])
		if num > 0: self.buffDebuff(num, num)
		return None


class SI7Assassin(Minion):
	Class, race, name = "Rogue", "", "SI:7 Assassin"
	mana, attack, health = 7, 4, 4
	index = "STORMWIND~Rogue~Minion~7~4~4~~SI:7 Assassin~Combo"
	requireTarget, effects, description = True, "", "Costs (1) less for each SI:7 card you've played this game. Combo: Destroy an enemy minion"
	name_CN = "军情七处刺客"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsHand = [Trig_SI7Assassin(self)]
	
	def selfManaChange(self):
		if self.inHand:
			self.mana -= sum("SI:7" in card.index for card in self.Game.Counters.cardsPlayedThisGame[self.ID])
			self.mana = max(self.mana, 0)
	
	def returnTrue(self, choice=0):
		return self.Game.Counters.numCardsPlayedThisTurn[self.ID] > 0
	
	def targetExists(self, choice=0):
		return self.selectableEnemyMinionExists()
	
	def effCanTrig(self):
		self.effectViable = self.Game.Counters.numCardsPlayedThisTurn[self.ID] > 0
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target and self.Game.Counters.numCardsPlayedThisTurn[self.ID] > 0:
			self.Game.killMinion(self, target)
		return target

class Trig_SI7Assassin(TrigHand):
	def __init__(self, entity):
		super().__init__(entity, ["MinionBeenPlayed", "SpellBeenPlayed", "WeaponBeenPlayed", "HeroBeenPlayed"])
	
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.inHand and subject.ID == self.entity.ID and subject.name.startswith("SI:7")
	
	def text(self, CHN):
		return "每当你使用一张军情七处牌，重新计算费用" if CHN \
			else "Whenever you play a SI:7 card, recalculate the cost"
	
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.Game.Manas.calcMana_Single(self.entity)


"""Shaman Cards"""
class Trig_CommandtheElements(Trig_Quest):
	def __init__(self, entity):
		super().__init__(entity, ["MinionBeenPlayed", "SpellBeenPlayed", "WeaponBeenPlayed", "HeroBeenPlayed"])
		self.numNeeded, self.newQuest, self.reward = 3, StirtheStones, None
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject.ID == self.entity.ID and subject.overload > 0
	
	def questEffect(self, quest, game, ID):
		quest.Game.Manas.unlockOverloadedMana(ID)
	
class Trig_StirtheStones(Trig_CommandtheElements):
	def __init__(self, entity):
		super().__init__(entity)
		self.numNeeded, self.newQuest, self.reward = 3, TametheFlames, None
	
	def questEffect(self, quest, game, ID):
		quest.summon(LivingEarth(game, ID), -1)

class Trig_TametheFlames(Trig_CommandtheElements):
	def __init__(self, entity):
		super().__init__(entity)
		self.numNeeded, self.newQuest, self.reward = 3, None, StormcallerBrukan
		

class CommandtheElements(Questline):
	Class, name = "Shaman", "Command the Elements"
	requireTarget, mana, effects = False, 1, ""
	index = "STORMWIND~Shaman~Spell~1~~Command the Elements~~Questline~Legendary"
	description = "Questline: Play 3 cards with Overload. Reward: Unlock your Overloaded Mana Crystals"
	name_CN = "号令元素"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_CommandtheElements(self)]

class StirtheStones(Questline):
	Class, name = "Shaman", "Stir the Stones"
	requireTarget, mana, effects = False, -1, ""
	index = "STORMWIND~Shaman~Spell~0~~Stir the Stones~~Questline~Legendary~Uncollectible"
	description = "Questline: Play 3 cards with Overload. Reward: Summon a 3/3 Elemental with Taunt"
	name_CN = "搬移磐石"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_StirtheStones(self)]

class LivingEarth(Minion):
	Class, race, name = "Shaman", "Elemental", "Living Earth"
	mana, attack, health = 3, 3, 3
	index = "STORMWIND~Shaman~Minion~3~3~3~Elemental~Living Earth~Taunt~Uncollectible"
	requireTarget, effects, description = False, "Taunt", "Taunt"
	name_CN = "活体土石"
	
class TametheFlames(Questline):
	Class, name = "Shaman", "Tame the Flames"
	requireTarget, mana, effects = False, -1, ""
	index = "STORMWIND~Shaman~Spell~0~~Tame the Flames~~Questline~Legendary~Uncollectible"
	description = "Questline: Play 3 cards with Overload. Reward: Stormcaller Bru'kan"
	name_CN = "驯服火焰"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_TametheFlames(self)]

class StormcallerBrukan(Minion):
	Class, race, name = "Shaman", "", "Stormcaller Bru'kan"
	mana, attack, health = 5, 7, 7
	index = "STORMWIND~Shaman~Minion~5~7~7~~Stormcaller Bru'kan~Battlecry~Legendary~Uncollectible"
	requireTarget, effects, description = False, "", "Battlecry: For the rest of the game, your spells cast twice"
	name_CN = "风暴召唤者布鲁坎"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.Game.effects[self.ID]["Spells x2"] += 1
		return None


class InvestmentOpportunity(Spell):
	Class, school, name = "Shaman", "", "Investment Opportunity"
	requireTarget, mana, effects = False, 1, ""
	index = "STORMWIND~Shaman~Spell~1~~Investment Opportunity"
	description = "Draw an Overload card"
	name_CN = "投资良机"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		cards = [i for i, card in enumerate(self.Game.Hand_Deck.decks[self.ID]) if "~Overload" in card.index]
		if cards: self.Game.Hand_Deck.drawCard(self.ID, npchoice(cards))
		return False


class Overdraft(Spell):
	Class, school, name = "Shaman", "", "Overdraft"
	requireTarget, mana, effects = True, 1, ""
	index = "STORMWIND~Shaman~Spell~1~~Overdraft~Tradeable"
	description = "Tradeable. Unlock your Overloaded Mana Crystals to deal that much damage"
	name_CN = "强行透支"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			base = self.Game.Manas.manasOverloaded[self.ID] + self.Game.Manas.manasLocked[self.ID]
			damage = (base + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			self.Game.Manas.unlockOverloadedMana(self.ID)
			self.dealsDamage(target, damage)
		return target


class BolnerHammerbeak(Minion):
	Class, race, name = "Shaman", "", "Bolner Hammerbeak"
	mana, attack, health = 2, 1, 4
	index = "STORMWIND~Shaman~Minion~2~1~4~~Bolner Hammerbeak~Legendary"
	requireTarget, effects, description = False, "", "After you play a Battlecry minion, repeat the first Battlecry played this turn"
	name_CN = "伯纳尔·锤喙"
	#发布录像说明打出的第一个战吼随从也可以享受这个重复。
	#假设所重复也是一个随从的战吼，重复时的战吼发出者为这个随从,如果是指向性战吼，则目标随机
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_BolnerHammerbeak(self)]
	
class Trig_BolnerHammerbeak(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["MinionBeenPlayed"])
	
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject.ID == self.entity.ID and self.entity.onBoard and "~Battlecry" in subject.index
	
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		minion = next((card for card in self.entity.Game.Counters.cardsPlayedEachTurn[self.entity.ID][-1] \
			  							if card.type == "Minion" and "~Battlecry" in card.index), None)
		target = npchoice(minion.findTargets(self.entity)) if minion.requireTarget else None
		minion.whenEffective(self.entity, target, comment="byOthers")
		
		
class AuctionhouseGavel(Weapon):
	Class, name, description = "Shaman", "Auctionhouse Gavel", "After your hero attacks, reduce the Cost of a Battlecry minion in your hand by (1)"
	mana, attack, durability, effects = 2, 2, 2, ""
	index = "STORMWIND~Shaman~Weapon~2~2~2~Auctionhouse Gavel"
	name_CN = "拍卖行木槌"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_AuctionhouseGavel(self)]

class Trig_AuctionhouseGavel(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["HeroAttackedMinion", "HeroAttackedHero"])
	
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject == self.entity.Game.heroes[self.entity.ID] and self.entity.onBoard
	
	def text(self, CHN):
		return "在你的英雄攻击后，使你手牌中一张战吼随从的法力值消耗减少(1)点" if CHN \
			else "After your hero attacks, reduce the Cost of a Battlecry minion in your hand by (1)"
	
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		minions = [card for card in self.entity.Game.Hand_Deck.hands[self.entity.ID] if card.type == "Minion" and "~Battlecry" in card.index]
		if minions: ManaMod(npchoice(minions), changeby=-1).applies()


class ChargedCall(Spell):
	Class, school, name = "Shaman", "", "Charged Call"
	requireTarget, mana, effects = False, 3, ""
	index = "STORMWIND~Shaman~Spell~3~~Charged Call"
	description = "Discover a 1-Cost minion and summon it. (Upgrade it for each Overload card you played this game)"
	name_CN = "充能召唤"
	poolIdentifier = "Minions as Mage to Summon"
	@classmethod
	def generatePool(cls, pools):
		neutralMinions = [card for card in pools.NeutralCards if card.type == "Minion"]
		classCards = {}
		for Class, cards in pools.ClassCards.items():
			classCards[Class] = [card for card in cards if card.type == "Minion"]
		return ["Minions as %s to Summon"%Class for Class in classCards], \
			   [minions+neutralMinions for minions in classCards.values()]

	def text(self, CHN):
		return 1 + min(10, sum("~Overload" in card.index for card in self.Game.Counters.cardsPlayedThisGame[self.ID]))
		
	def decideMinionPool(self, num):
		return self.rngPool("%d-Cost Minions as %s to Summon"%(min(0, num), classforDiscover(self)))
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		num = 1 + sum("~Overload" in card.index for card in self.Game.Counters.cardsPlayedThisGame[self.ID])
		self.discoverandGenerate(ChargedCall, comment, lambda : ChargedCall.decideMinionPool(self, num))
		return target
	
	def discoverDecided(self, option, case, info_RNGSync=None, info_GUISync=None):
		self.handleDiscoverGeneratedCard(option, case, info_RNGSync, info_GUISync,
										 func=lambda cardType, card: self.summon(cardType(self.Game, self.ID), -1))
		

class SpiritAlpha(Minion):
	Class, race, name = "Shaman", "", "Spirit Alpha"
	mana, attack, health = 4, 2, 5
	index = "STORMWIND~Shaman~Minion~4~2~5~~Spirit Alpha"
	requireTarget, effects, description = False, "", "After you play a card with Overload, summon a 2/3 Spirit Wolf with Taunt"
	name_CN = "幽灵狼前锋"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_SpiritAlpha(self)]

class Trig_SpiritAlpha(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["MinionBeenPlayed", "SpellBeenPlayed", "WeaponBeenPlayed", "HeroBeenPlayed"])
	
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject.ID == self.entity.ID and self.entity.onBoard and "~Overload" in subject.index
	
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.summon(SpiritWolf(self.entity.Game, self.entity.ID), self.entity.pos+1)


class GraniteForgeborn(Minion):
	Class, race, name = "Shaman", "Elemental", "Granite Forgeborn"
	mana, attack, health = 4, 4, 4
	index = "STORMWIND~Shaman~Minion~4~4~4~Elemental~Granite Forgeborn~Rush~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Reduce the Cost of Elementals in your hand and deck by (1)"
	name_CN = "花岗岩熔铸体"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		for card in self.Game.Hand_Deck.hands[self.ID]:
			if card.type == "Minion" and "Elemental" in card.race:
				ManaMod(card, changeby=-1).applies()
		for card in self.Game.Hand_Deck.decks[self.ID]:
			if card.type == "Minion" and "Elemental" in card.race:
				ManaMod(card, changeby=-1).applies()
		return None


class CanalSlogger(Minion):
	Class, race, name = "Shaman", "Elemental", "Canal Slogger"
	mana, attack, health = 4, 6, 4
	index = "STORMWIND~Shaman~Minion~4~6~4~Elemental~Canal Slogger~Rush~Lifesteal~Overload"
	requireTarget, effects, description = False, "Rush,Lifesteal", "Rush, Lifesteal, Overload: (1)"
	name_CN = "运河慢步者"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.overload = 1


class TinyToys(Spell):
	Class, school, name = "Shaman", "", "Tiny Toys"
	requireTarget, mana, effects = False, 6, ""
	index = "STORMWIND~Shaman~Spell~6~~Tiny Toys"
	description = "Summon four random 5-Cost minions. Make them 2/2"
	name_CN = "小巧玩具"
	poolIdentifier = "5-Cost Minions to Summon"
	@classmethod
	def generatePool(cls, pools):
		return "5-Cost Minions to Summon", pools.MinionsofCost[5]
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		minions = [minion(self.Game, self.ID) for minion in npchoice(self.rngPool("5-Cost Minions to Summon"), 4, replace=True)]
		self.summon(minions, (-1, "totheRightEnd"))
		for minion in minions:
			if minion.onBoard: minion.statReset(2, 2)
		return None


"""Warlock Cards"""
class Trig_TheDemonSeed(Trig_Quest):
	def __init__(self, entity):
		super().__init__(entity, ["HeroTookDmg"])
		self.numNeeded, self.newQuest, self.reward = 6, EstablishtheLink, None
	
	def handleCounter(self, signal, ID, subject, target, number, comment, choice=0):
		self.counter += number
	
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject.ID == self.entity.ID == subject.Game.turn
	
	def questEffect(self, quest, game, ID):
		damage = (3 + quest.countquestDamage()) * (2 ** quest.countDamageDouble())
		quest.dealsDamage(quest.Game.heroes[3 - quest.ID], damage)

class Trig_EstablishtheLink(Trig_TheDemonSeed):
	def __init__(self, entity):
		super().__init__(entity)
		self.numNeeded, self.newQuest, self.reward = 7, CompletetheRitual, None
	
class Trig_CompletetheRitual(Trig_TheDemonSeed):
	def __init__(self, entity):
		super().__init__(entity)
		self.numNeeded, self.newQuest, self.reward = 8, None, BlightbornTamsin


class TheDemonSeed(Questline):
	Class, name = "Warlock", "The Demon Seed"
	requireTarget, mana, effects = False, 1, "Lifesteal"
	index = "STORMWIND~Warlock~Spell~1~~The Demon Seed~~Questline~Legendary"
	description = "Questline: Take 6 damage on your turns. Reward: Lifesteal. Deal 3 damage to the enemy hero"
	name_CN = "恶魔之种"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_TheDemonSeed(self)]

class EstablishtheLink(Questline):
	Class, name = "Warlock", "Establish the Link"
	requireTarget, mana, effects = False, -1, "Lifesteal"
	index = "STORMWIND~Warlock~Spell~0~~Establish the Link~~Questline~Legendary~Uncollectible"
	description = "Questline: Take 7 damage on your turns. Reward: Lifesteal. Deal 3 damage to the enemy hero"
	name_CN = "建立连接"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_EstablishtheLink(self)]

class CompletetheRitual(Questline):
	Class, name = "Warlock", "Complete the Ritual"
	requireTarget, mana, effects = False, -1, ""
	index = "STORMWIND~Warlock~Spell~0~~Complete the Ritual~~Questline~Legendary~Uncollectible"
	description = "Questline: Take 8 damage on your turns. Reward: Blightborn Tamsin"
	name_CN = "完成仪式"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_CompletetheRitual(self)]

class BlightbornTamsin(Minion):
	Class, race, name = "Warlock", "", "Blightborn Tamsin"
	mana, attack, health = 5, 7, 7
	index = "STORMWIND~Warlock~Minion~5~7~7~~Blightborn Tamsin~Battlecry~Legendary~Uncollectible"
	requireTarget, effects, description = False, "", "Battlecry: For the rest of the game, damage you take on your turns damages your opponent instead"
	name_CN = "枯萎化身塔姆辛"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		BlightbornTamsin_Effect(self.Game, self.ID).connect()
		return None

class BlightbornTamsin_Effect:
	def __init__(self, Game, ID):
		self.Game, self.ID = Game, ID
		self.card = BlightbornTamsin(Game, ID)
		self.signals = ["DmgTaker?"]
		self.on = True
		
	def connect(self):
		trigs = self.Game.trigsBoard[self.ID]
		if not any(isinstance(trig, BlightbornTamsin_Effect) for trig in trigs["DmgTaker?"]):
			try: trigs["DmgTaker?"].append(self)
			except: trigs["DmgTaker?"] = [self]
		
	#number here is a list that holds the damage to be processed
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		if comment == "Reset": #Assume this can't trigger multiple times in a chain
			self.on = True
			return False
		else:
			return target[0] == self.Game.heroes[self.ID] and target.onBoard and self.Game.turn == self.ID
	
	def trig(self, signal, ID, subject, target, number, comment, choice=0):
		if self.canTrig(signal, ID, subject, target, number, comment):
			if self.Game.GUI: self.Game.GUI.showOffBoardTrig(self.card)
			self.effect(signal, ID, subject, target, number, comment)
	
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		target[0] = self.Game.heroes[3-self.ID]
		self.on = False
		
	def createCopy(self, game):  #不是纯的只在回合结束时触发，需要完整的createCopy
		if self not in game.copiedObjs:  #这个扳机没有被复制过
			trigCopy = type(self)(game, self.ID)
			trigCopy.on = self.on
			game.copiedObjs[self] = trigCopy
			return trigCopy
		else:  #一个扳机被复制过了，则其携带者也被复制过了
			return game.copiedObjs[self]


class TouchoftheNathrezim(Spell):
	Class, school, name = "Warlock", "Shadow", "Touch of the Nathrezim"
	requireTarget, mana, effects = True, 1, ""
	index = "STORMWIND~Warlock~Spell~1~Shadow~Touch of the Nathrezim"
	description = "Deal 2 damage to a minion. If it dies, restore 4 Health to your hero"
	name_CN = "纳斯雷兹姆之触"
	
	def available(self):
		return self.selectableMinionExists()
	
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
	
	def text(self, CHN):
		return "%d, %d"%((2 + self.countSpellDamage()) * (2 ** self.countDamageDouble()), 
						4 * (2 ** self.countHealDouble()))
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			damage = (2 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			self.dealsDamage(target, damage)
			if target.health <=0 or target.dead:
				heal = 4 * (2 ** self.countHealDouble())
				self.restoresHealth(self.Game.heroes[self.ID], heal)
		return target
	
	
class BloodboundImp(Minion):
	Class, race, name = "Warlock", "Demon", "Bloodbound Imp"
	mana, attack, health = 2, 2, 5
	index = "STORMWIND~Warlock~Minion~2~2~5~Demon~Bloodbound Imp"
	requireTarget, effects, description = False, "", "Whenever this attacks, deal 2 damage to your hero"
	name_CN = "血缚小鬼"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_BloodboundImp(self)]

class Trig_BloodboundImp(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["MinionAttackingMinion", "MinionAttackingHero"])
	
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject == self.entity and self.entity.onBoard
	
	def text(self, CHN):
		return "每当该随从进行攻击，对你的英雄造成2点伤害" if CHN else "Whenever this attacks, deal 2 damage to your hero"
	
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.dealsDamage(self.entity.Game.heroes[self.entity.ID], 2)


class DreadedMount(Spell):
	Class, school, name = "Warlock", "", "Dreaded Mount"
	requireTarget, mana, effects = True, 3, ""
	index = "STORMWIND~Warlock~Spell~3~~Dreaded Mount"
	description = "Give a minion +1/+1. When it dies, summon an endless Dreadsteed"
	name_CN = "恐惧坐骑"
	
	def available(self):
		return self.selectableMinionExists()
	
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			target.buffDebuff(1, 1)
			target.getsTrig(SummonaDreadsteed(target), trigType="Deathrattle", connect=target.onBoard)
		return target

class SummonaDreadsteed(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.summon(TamsinsDreadsteed(self.entity.Game, self.entity.ID), self.entity.pos+1)
	
	def text(self, CHN):
		return "亡语：召唤一只2/2的山羊" if CHN else "Deathrattle: Summon a 2/2 Ram"

class TamsinsDreadsteed(Spell):
	Class, race, name = "Warlock", "Demon", "Tamsin's Dreadsteed"
	mana, attack, health = 4, 1, 1
	index = "STORMWIND~Warlock~Minion~4~1~1~Demon~Tamsin's Dreadsteed~Deathrattle~Uncollectible"
	requireTarget, effects, description = False, "", "Deathrattle: At the end of the turn, summon Tamsin's Dreadsteed"
	name_CN = "塔姆辛的恐惧战马"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.deathrattles = [SummonaDreadsteed_EndofTurn(self)]

class SummonaDreadsteed_EndofTurn(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		DreadSteed_Effect(self.entity.Game, self.entity.ID).connect()
		
	def text(self, CHN):
		return "亡语：在你的回合结束时，召唤塔姆辛的恐惧战马" if CHN else "Deathrattle: At the end of the turn, summon Tamsin's Dreadsteed"

class DreadSteed_Effect:
	def __init__(self, Game, ID):
		self.Game, self.ID = Game, ID
		self.card = TamsinsDreadsteed(Game, ID)
		
	def connect(self):
		try: self.Game.trigsBoard[self.ID]["TurnEnds"].append(self)
		except: self.Game.trigsBoard[self.ID]["TurnEnds"] = [self]
		
	def disconnect(self):
		try: self.Game.trigsBoard[self.ID]["TurnEnds"].remove(self)
		except: pass
	
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return True
	
	def trig(self, signal, ID, subject, target, number, comment, choice=0):
		if self.canTrig(signal, ID, subject, target, number, comment):
			if self.Game.GUI: self.Game.GUI.showOffBoardTrig(self.card)
			self.effect(signal, ID, subject, target, number, comment)
	
	def text(self, CHN):
		return "在回合结束时，召唤一匹无尽的恐惧战马" if CHN \
			else "At the end of the turn, summon an enless Dreadsteed"
	
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.card.summon(TamsinsDreadsteed(self.Game, self.ID), -1)
		self.disconnect()
	
	def createCopy(self, game):  #不是纯的只在回合结束时触发，需要完整的createCopy
		if self not in game.copiedObjs:  #这个扳机没有被复制过
			trigCopy = type(self)(game, self.ID)
			game.copiedObjs[self] = trigCopy
			return trigCopy
		else:  #一个扳机被复制过了，则其携带者也被复制过了
			return game.copiedObjs[self]


class RunedMithrilRod(Weapon):
	Class, name, description = "Warlock", "Runed Mithril Rod", "After you draw 4 cards, reduce the Cost of cards in your hand by (1). Lose 1 Durability"
	mana, attack, durability, effects = 3, 0, 2, ""
	index = "STORMWIND~Warlock~Weapon~3~0~2~Runed Mithril Rod"
	name_CN = "符文秘银杖"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_RunedMithrilRod(self)]

class Trig_RunedMithrilRod(Trig_Countdown):
	def __init__(self, entity):
		super().__init__(entity, ["CardEntersHand"]) #There needs to be comment="byDrawing"
		self.counter = 4
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return target[0].ID == self.entity.ID and self.entity.onBoard and comment == "byDrawing"
	
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		if self.counter < 1:
			self.counter = 4
			for card in self.entity.Game.Hand_Deck.hands[self.entity.ID]:
				ManaMod(card, changeby=-1, changeto=-1).applies()
			self.entity.loseDurability()
		
		
class DarkAlleyPact(Spell):
	Class, school, name = "Warlock", "Shadow", "Dark Alley Pact"
	requireTarget, mana, effects = False, 4, ""
	index = "STORMWIND~Warlock~Spell~4~Shadow~Dark Alley Pact"
	description = "Summon a Fiend with stat equal to your hand size"
	name_CN = "暗巷交易"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		handSize = len(self.Game.Hand_Deck.hands[self.ID])
		if handSize == 1: self.summon(Fiend(self.Game, self.ID), -1)
		elif handSize > 1:
			cost = min(handSize, 10)
			newIndex = "STORMWIND~Warlock~Minion~%d~%d~%d~Demon~Fiend~Uncollectible" % (cost, handSize, handSize)
			subclass = type("Fiend__" + str(handSize), (Fiend,),
							{"mana": cost, "attack": handSize, "health": handSize,
							 "index": newIndex}
							)
			self.summon(subclass(self.Game, self.ID), -1)
		return None

class Fiend(Minion):
	Class, race, name = "Warlock", "Demon", "Fiend"
	mana, attack, health = 1, 1, 1
	index = "STORMWIND~Warlock~Minion~1~1~1~Demon~Fiend~Uncollectible"
	requireTarget, effects, description = False, "", ""
	name_CN = "邪魔"


class DemonicAssault(Spell):
	Class, school, name = "Warlock", "Fel", "Demonic Assault"
	requireTarget, mana, effects = True, 4, ""
	index = "STORMWIND~Warlock~Spell~4~Fel~Demonic Assault"
	description = "Deal 3 damage. Summon two 1/3 Voidwalkers with Taunt"
	name_CN = "恶魔来袭"
	
	def text(self, CHN):
		return (3 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			damage = (3 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			self.dealsDamage(target, damage)
			self.summon([Voidwalker(self.Game, self.ID) for i in range(2)], (-1, "totheRightEnd"))
		return target


class ShadyBartender(Minion):
	Class, race, name = "Warlock", "", "Shady Bartender"
	mana, attack, health = 5, 4, 4
	index = "STORMWIND~Warlock~Minion~5~4~4~~Shady Bartender~Battlecry~Tradeable"
	requireTarget, effects, description = False, "", "Tradeable. Battlecry: Give your Demons +2/+2"
	name_CN = "阴暗的酒保"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		for minion in self.Game.minionsonBoard(self.ID):
			if "Demon" in minion.race: minion.buffDebuff(2, 2)
		return None
	
	
class Anetheron(Minion):
	Class, race, name = "Warlock", "Demon", "Anetheron"
	mana, attack, health = 6, 8, 6
	index = "STORMWIND~Warlock~Minion~6~8~6~Demon~Anetheron~Legendary"
	requireTarget, effects, description = False, "", "Costs (1) if your hand is full"
	name_CN = "安纳塞隆"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsHand = [Trig_Anetheron(self)]
	
	def selfManaChange(self):
		if self.inHand and len(self.Game.Hand_Deck.hands[self.ID]) == self.Game.Hand_Deck.handUpperLimit[self.ID]:
			self.mana = 1

class Trig_Anetheron(TrigHand):
	def __init__(self, entity):
		super().__init__(entity, ["CardEntersHand", "CardLeavesHand", "HandUpperLimitChange"])
	
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.inHand and ID == self.entity.ID
	
	def text(self, CHN):
		return "每当你的手牌数发生变化时，重新计算费用" if CHN else "Whenever your handSize changes, recalculate the cost"
	
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.Game.Manas.calcMana_Single(self.entity)


class EntitledCustomer(Minion):
	Class, race, name = "Warlock", "", "Entitled Customer"
	mana, attack, health = 6, 3, 2
	index = "STORMWIND~Warlock~Minion~6~3~2~~Entitled Customer~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Deal damage equal to your hand size to all other minions"
	name_CN = "资深顾客"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		damage = len(self.Game.Hand_Deck.hands[self.ID])
		targets = self.Game.minionsonBoard(1, exclude=self) + self.Game.minionsonBoard(2, exclude=self)
		if targets: self.dealsAOE(targets, [damage] * len(targets))
		return None


"""Warrior Cards"""
class Provoke(Spell):
	Class, school, name = "Warrior", "", "Provoke"
	requireTarget, mana, effects = True, 0, ""
	index = "STORMWIND~Warrior~Spell~0~~Provoke~Tradeable"
	description = "Tradeable. Choose a friendly minion. Enemy minions attack it"
	name_CN = "挑衅"
	def available(self):
		return self.selectableFriendlyMinionExists()
	
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.ID == self.ID and target.onBoard
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target and target.onBoard and target.health > 0 and not target.dead:
			#假设依登场顺序来进行攻击
			minions = self.Game.sortSeq(self.Game.minionsAlive(3-self.ID, target))[0]
			for minion in minions:
				if minion.onBoard and minion.health > 0 and not minion.dead:
					self.Game.battle(minion, target, verifySelectable=False, useAttChance=False, resolveDeath=False, resetRedirTrig=True)
		return target


class Trig_RaidtheDocks(Trig_Quest):
	def __init__(self, entity):
		super().__init__(entity, ["MinionBeenPlayed"])
		self.numNeeded, self.newQuest, self.reward = 3, CreateaDistraction, None
	
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject.ID == self.entity.ID and "Pirate" in subject.race
	
	def questEffect(self, quest, game, ID):
		indices = [i for i, card in quest.Game.Hand_Deck[quest.ID] if card.type == "Weapon"]
		if indices: quest.Game.Hand_Deck.drawCard(quest.ID, npchoice(indices))

class Trig_CreateaDistraction(Trig_RaidtheDocks):
	def __init__(self, entity):
		super().__init__(entity)
		self.numNeeded, self.newQuest, self.reward = 2, SecuretheSupplies, None

	def questEffect(self, quest, game, ID):
		damage = (2 + quest.countSpellDamage()) * (2 ** quest.countDamageDouble())
		for num in range(2):
			objs = quest.Game.charsAlive(3-quest.ID)
			if objs: quest.dealsDamage(npchoice(objs), damage)
			else: break
			
class Trig_SecuretheSupplies(Trig_RaidtheDocks):
	def __init__(self, entity):
		super().__init__(entity)
		self.numNeeded, self.newQuest, self.reward = 2, None, CapnRokara

class RaidtheDocks(Questline):
	Class, name = "Warrior", "Raid the Docks"
	requireTarget, mana, effects = False, 1, ""
	index = "STORMWIND~Warrior~Spell~1~~Raid the Docks~~Questline~Legendary"
	description = "Questline: Play 3 Pirates. Reward: Draw a weapon"
	name_CN = "开进码头"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_RaidtheDocks(self)]

class CreateaDistraction(Questline):
	Class, name = "Warrior", "Create a Distraction"
	requireTarget, mana, effects = False, -1, ""
	index = "STORMWIND~Warrior~Spell~0~~Create a Distraction~~Questline~Legendary"
	description = "Questline: Play 2 Pirates. Reward: Deal 2 damage to a random enemy twice"
	name_CN = "制造混乱"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_CreateaDistraction(self)]
		
class SecuretheSupplies(Questline):
	Class, name = "Warrior", "Secure the Supplies"
	requireTarget, mana, effects = False, -1, ""
	index = "STORMWIND~Warrior~Spell~0~~Secure the Supplies~~Questline~Legendary~Uncollectible"
	description = "Questline: Play 2 Pirates. Reward: Cap'n Rokara"
	name_CN = "保证补给"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_SecuretheSupplies(self)]

class CapnRokara(Minion):
	Class, race, name = "Warrior", "Pirate", "Cap'n Rokara"
	mana, attack, health = 5, 7, 7
	index = "STORMWIND~Warrior~Minion~5~7~7~Pirate~Cap'n Rokara~Battlecry~Legendary~Uncollectible"
	requireTarget, effects, description = False, "", "Battlecry: Summon The Juggernaut"
	name_CN = "船长洛卡拉"
	poolIdentifier = "Pirates"
	@classmethod
	def generatePool(cls, pools):
		return ["Pirates", "Warrior Weapons"], [pools.MinionswithRace["Pirate"],
												[card for card in pools.ClassCards["Warrior"] if card.type == "Weapon"]]

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.Game.summonSingle(TheJuggernaut(self.Game, self.ID), self.pos + 1, self)
		return None

class TheJuggernaut(Dormant):
	Class, name = "Warlock", "The Juggernaut"
	description = "At the start of your turn, summon a Pirate, equip a Warrior weapon and fire two cannons that deal 2 damage!"
	index = "STORMWIND~Dormant~The Juggernaut~Legendary"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_TheJuggernaut(self)]

class Trig_TheJuggernaut(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["TurnStarts"])  #假设是死亡时扳机，而还是死亡后扳机
	
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and ID == self.entity.ID
	
	def text(self, CHN):
		return "在你的回合开始时，召唤一个海盗，装备一把战士武器，并向敌人发射两发炮弹，每发造成2点伤害" if CHN \
			else "At the start of your turn, summon a Pirate, equip a Warrior weapon and fire two cannons that deal 2 damage!"
	
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		dormant = self.entity
		dormant.summon(npchoice(self.rngPool("Pirates"))(dormant.Game, dormant.ID), dormant.pos+1)
		dormant.equipWeapon(npchoice(self.rngPool("Warrior Weapons"))(dormant.Game, dormant.ID))
		for num in range(2):
			objs = dormant.Game.charsAlive(3-dormant.ID)
			if objs: dormant.dealsDamage(npchoice(objs), 2)
			else: break


class ShiverTheirTimbers(Spell):
	Class, school, name = "Warrior", "", "Shiver Their Timbers!"
	requireTarget, mana, effects = True, 1, ""
	index = "STORMWIND~Warrior~Spell~1~~Shiver Their Timbers!"
	description = "Deal 2 damage to a minion. If you control a Pirate, deal 5 instead"
	name_CN = "海上威胁"
	
	def available(self):
		return self.selectableMinionExists()
	
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
	
	def text(self, CHN):
		return "%d, %d"%( (2 + self.countSpellDamage()) * (2 ** self.countDamageDouble()),
							(5 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
							)
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			base = 5 if any("Pirate" in minion.race for minion in self.Game.minionsonBoard(self.ID)) else 2
			damage = (base + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			self.dealsDamage(target, damage)
		return target


class HarborScamp(Minion):
	Class, race, name = "Warrior", "Pirate", "Harbor Scamp"
	mana, attack, health = 2, 2, 2
	index = "STORMWIND~Warrior~Minion~2~2~2~Pirate~Harbor Scamp~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Draw a Pirate"
	name_CN = "港口匪徒"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		pirates = [i for i, card in enumerate(self.Game.Hand_Deck.decks[self.ID]) if card.type == "Minion" and "Pirate" in card.race]
		if pirates: self.Game.Hand_Deck.drawCard(self.ID, npchoice(pirates))
		return None


class CargoGuard(Minion):
	Class, race, name = "Warrior", "Pirate", "Cargo Guard"
	mana, attack, health = 3, 2, 4
	index = "STORMWIND~Warrior~Minion~3~2~4~Pirate~Cargo Guard"
	requireTarget, effects, description = False, "", "At the end of your turn, gain 3 Armor"
	name_CN = "货物保镖"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_CargoGuard(self)]

class Trig_CargoGuard(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["TurnEnds"])
	
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and ID == self.entity.ID
	
	def text(self, CHN):
		return "在你的回合结束时，获得3点护甲值" if CHN else "At the end of your turn, gain 3 Armor"
	
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.Game.heroes[self.entity.ID].gainsArmor(3)


class HeavyPlate(Spell):
	Class, school, name = "Warrior", "", "Heavy Plate"
	requireTarget, mana, effects = False, 3, ""
	index = "STORMWIND~Warrior~Spell~3~~Heavy Plate~Tradeable"
	description = "Tredeable. Gain 8 Armor"
	name_CN = "厚重板甲"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.Game.heroes[self.ID].gainsArmor(8)
		return None


class StormwindFreebooter(Minion):
	Class, race, name = "Warrior", "Pirate", "Stormwind Freebooter"
	mana, attack, health = 3, 3, 3
	index = "STORMWIND~Warrior~Minion~3~3~3~Pirate~Stormwind Freebooter~Battlecry"
	requireTarget, effects, description = False, "", "Battlecry: Give your hero +2 Attack this turn"
	name_CN = "暴风城海盗"

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.Game.heroes[self.ID].gainAttack(2)
		return None
	
	
class RemoteControlledGolem(Minion):
	Class, race, name = "Warrior", "Mech", "Remote-Controlled Golem"
	mana, attack, health = 4, 3, 6
	index = "STORMWIND~Warrior~Minion~4~3~6~Mech~Remote-Controlled Golem"
	requireTarget, effects, description = False, "", "After this minion takes damage, shuffle two Golem Parts into your deck. When drawn, summon a 2/1 Mech"
	name_CN = "遥控傀儡"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_RemoteControlledGolem(self)]

class Trig_RemoteControlledGolem(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["MinionTookDmg"])
	
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and target == self.entity
	
	def text(self, CHN):
		return "在该随从受到伤害后，将两张傀儡部件洗入你的牌库。当抽到傀儡部件时，召唤一个2/1的机械" if CHN \
			else "After this minion takes damage, shuffle two Golem Parts into your deck. When drawn, summon a 2/1 Mech"
	
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.Game.Hand_Deck.shuffleintoDeck([GolemParts for i in range(2)], initiatorID=self.entity.ID, creator=self.entity)

class GolemParts(Spell):
	Class, school, name = "Warrior", "", "Golem Parts"
	requireTarget, mana, effects = False, 1, ""
	index = "STORMWIND~Warrior~Spell~1~~Golem Parts~Casts When Drawn~Uncollectible"
	description = "Casts When Drawn. Summon a 2/1 Mech"
	name_CN = "傀儡部件"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.summon(DamagedGolem(self.Game, self.ID), -1)
		return None


class CowardlyGrunt(Minion):
	Class, race, name = "Warrior", "", "Cowardly Grunt"
	mana, attack, health = 6, 6, 2
	index = "STORMWIND~Warrior~Minion~6~6~2~~Cowardly Grunt~Deathrattle"
	requireTarget, effects, description = False, "", "Deathrattle: Summon a minion from your deck"
	name_CN = "怯懦的步兵"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.deathrattles = [SumonaMinionfromDeck(self)]

class SumonaMinionfromDeck(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		minion = self.entity
		minions = [i for i, card in enumerate(minion.Game.Hand_Deck.hands[minion.ID]) if card.type == "Minion"]
		if minions and minion.Game: minion.Game.summonfrom(npchoice(minions), minion.ID, minion.pos + 1, minion, source='D')
		
	def text(self, CHN):
		return "亡语：从你的牌库中召唤一个随从" if CHN else "Deathrattle: Summon a minion from your deck"


class Lothar(Minion):
	Class, race, name = "Warrior", "", "Lothar"
	mana, attack, health = 7, 7, 7
	index = "STORMWIND~Warrior~Minion~7~7~7~~Lothar~Legendary"
	requireTarget, effects, description = False, "", "At the end of your turn, attack a random enemy minion. If it dies, gain +3/+3"
	name_CN = "洛萨"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_Lothar(self)]

class Trig_Lothar(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["TurnEnds"])
	
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return ID == self.entity.ID and self.entity.onBoard and not self.entity.dead
	
	def text(self, CHN):
		return "在你的回合结束时，随机攻击一个敌方随从。如果目标死亡，获得+3/+3" if CHN \
			else "At the end of your turn, attack a random enemy minion. If it dies, gain +3/+3"
	
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		minions = self.entity.Game.minionsAlive(3 - self.entity.ID)
		if minions:
			minion = npchoice(minions)
			self.entity.Game.battle(self.entity, minion, verifySelectable=False, resolveDeath=False)
			if minion.health < 1 or minion.dead: self.entity.buffDebuff(3, 3)
			
				
Stormwind_Cards = [ElwynnBoar, SwordofaThousandTruth, Peasant, StockadesGuard, AuctioneerJaxon, DeeprunEngineer, EncumberedPackMule, Florist, MailboxDancer, SI7Skulker,
				   StockadesPrisoner, EnthusiasticBanker, ImpatientShopkeep, NorthshireFarmer, PackageRunner, RustrotViper, TravelingMerchant, TwoFacedInvestor, FlightmasterDungar,
				   Nobleman, Cheesemonger, GuildTrader, RoyalLibrarian, SpiceBreadBaker, StubbornSuspect, LionsGuard, StormwindGuard, BattlegroundBattlemaster,
				   CityArchitect, CastleWall, CorneliusRoame, LadyPrestor, MoargForgefiend, VarianKingofStormwind, GoldshireGnoll,
				   #Demon Hunter
				   FinalShowdown, DemonslayerKurtrus, Metamorfin, SigilofAlacrity, FelBarrage, ChaosLeech, LionsFrenzy, Felgorger, PersistentPeddler, IreboundBrute, JaceDarkweaver,
				   #Druid
				   LostinthePark, GufftheTough, SowtheSoil, Fertilizer, NewGrowth, Treant_Stormwind, VibrantSquirrel, Acorn, SatisfiedSquirrel, Composting, Wickerclaw, OracleofElune, KodoMount, GuffsKodo, ParkPanther, BestinShell, GoldshellTurtle, SheldrasMoontree,
				   #Hunter
				   DevouringSwarm, DefendtheDwarvenDistrict, TavishMasterMarksman, LeatherworkingKit, AimedShot, RammingMount, TavishsRam, StormwindPiper, RodentNest, ImportedTarantula, InvasiveSpiderling, TheRatKing,  RatsofExtraordinarySize, Rat,
				   #Mage
				   HotStreak, FirstFlame, SecondFlame, SorcerersGambit, ArcanistDawngrasp, CelestialInkSet, Ignite, PrestorsPyromancer, FireSale, SanctumChandler, ClumsyCourier, GrandMagusAntonidas,
				   #Paladin
				   BlessedGoods, PrismaticJewelKit, RisetotheOccasion, LightbornCariel, NobleMount, CarielsWarhorse, CityTax, AllianceBannerman, CatacombGuard, LightbringersHammer, FirstBladeofWrynn, HighlordFordragon,
				   #Priest
				   CalloftheGrave, SeekGuidance, XyrellatheSanctified, PurifiedShard, ShardoftheNaaru, VoidtouchedAttendant, ShadowclothNeedle, TwilightDeceptor, Psyfiend, VoidShard, DarkbishopBenedictus, ElekkMount, XyrellasElekk,
				   #Rogue
				   FizzflashDistractor, Spyomatic, NoggenFogGenerator, HiddenGyroblade, UndercoverMole,
				   FindtheImposter, SpymasterScabbs, SI7Extortion, Garrote, Bleed, MaestraoftheMasquerade, CounterfeitBlade, LoanShark, SI7Operative, SketchyInformation, SI7Informant, SI7Assassin,
				   #Shaman
				   CommandtheElements, LivingEarth, StormcallerBrukan, InvestmentOpportunity, Overdraft, BolnerHammerbeak, AuctionhouseGavel, ChargedCall, SpiritAlpha, GraniteForgeborn, CanalSlogger, TinyToys,
				   #Warlock
				   TheDemonSeed, BlightbornTamsin, TouchoftheNathrezim, BloodboundImp, DreadedMount, TamsinsDreadsteed, RunedMithrilRod, DarkAlleyPact, Fiend, DemonicAssault, ShadyBartender, Anetheron, EntitledCustomer,
				   #Warrior
				   Provoke, RaidtheDocks, CapnRokara, ShiverTheirTimbers, HarborScamp, CargoGuard, HeavyPlate, StormwindFreebooter, RemoteControlledGolem, GolemParts, CowardlyGrunt, Lothar,
				   ]

Stormwind_Cards_Collectible = [#Neutral
								ElwynnBoar, Peasant, StockadesGuard, AuctioneerJaxon, DeeprunEngineer, EncumberedPackMule, Florist, MailboxDancer, SI7Skulker, StockadesPrisoner,
								EnthusiasticBanker, ImpatientShopkeep, NorthshireFarmer, PackageRunner, RustrotViper, TravelingMerchant, TwoFacedInvestor, FlightmasterDungar, Nobleman,
								Cheesemonger, GuildTrader, RoyalLibrarian, SpiceBreadBaker, StubbornSuspect, LionsGuard, StormwindGuard, BattlegroundBattlemaster,
								CityArchitect, CorneliusRoame, LadyPrestor, MoargForgefiend, VarianKingofStormwind, GoldshireGnoll,
								#Demon hunter
								FinalShowdown, Metamorfin, SigilofAlacrity, FelBarrage, ChaosLeech, LionsFrenzy, Felgorger, PersistentPeddler, IreboundBrute, JaceDarkweaver,
								#Druid
								LostinthePark, SowtheSoil, VibrantSquirrel, Composting, Wickerclaw, OracleofElune, KodoMount, ParkPanther, BestinShell, SheldrasMoontree,
								#Hunter
								DevouringSwarm, DefendtheDwarvenDistrict, LeatherworkingKit, AimedShot, RammingMount, StormwindPiper, RodentNest, ImportedTarantula, TheRatKing, RatsofExtraordinarySize,
								#Mage
								HotStreak, FirstFlame, SorcerersGambit, CelestialInkSet, Ignite, PrestorsPyromancer, FireSale, SanctumChandler, ClumsyCourier, GrandMagusAntonidas,
								#Paladin
								BlessedGoods, PrismaticJewelKit, RisetotheOccasion, NobleMount, CityTax, AllianceBannerman, CatacombGuard, LightbringersHammer, FirstBladeofWrynn, HighlordFordragon,
								#Priest
								CalloftheGrave, SeekGuidance, ShardoftheNaaru, VoidtouchedAttendant, ShadowclothNeedle, TwilightDeceptor, Psyfiend, VoidShard, DarkbishopBenedictus, ElekkMount,
								#Rogue
								FindtheImposter, SI7Extortion, Garrote, MaestraoftheMasquerade, CounterfeitBlade, LoanShark, SI7Operative, SketchyInformation, SI7Informant, SI7Assassin,
								#Shaman
								CommandtheElements, InvestmentOpportunity, Overdraft, BolnerHammerbeak, AuctionhouseGavel, ChargedCall, SpiritAlpha, GraniteForgeborn, CanalSlogger, TinyToys,
								#Warlock
								TheDemonSeed, TouchoftheNathrezim, BloodboundImp, DreadedMount, RunedMithrilRod, DarkAlleyPact, DemonicAssault, ShadyBartender, Anetheron, EntitledCustomer,
								#Warrior
								Provoke, RaidtheDocks, ShiverTheirTimbers, HarborScamp, CargoGuard, HeavyPlate, StormwindFreebooter, RemoteControlledGolem, CowardlyGrunt, Lothar,
								]