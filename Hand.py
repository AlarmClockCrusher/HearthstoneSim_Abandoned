from CardPools import *
from Academy import TransferStudent
import copy
from numpy.random import choice as npchoice
from numpy.random import randint as nprandint
from numpy.random import shuffle as npshuffle
import numpy as np

import inspect


def extractfrom(target, listObj):
	try: return listObj.pop(listObj.index(target))
	except: return None
	
def fixedList(listObj):
	return listObj[0:len(listObj)]
	
def PRINT(game, string, *args):
	if game.GUI:
		if not game.mode: game.GUI.printInfo(string)
	elif not game.mode: print("game's guide mode is 0\n", string)
	
	
class Hand_Deck:
	def __init__(self, Game, deck1=[], deck2=[]):  # 通过卡组列表加载卡组
		self.Game = Game
		self.hands = {1: [], 2: []}
		self.decks = {1: [], 2: []}
		self.noCards = {1: 0, 2: 0}
		self.handUpperLimit = {1: 10, 2: 10}
		if self.Game.heroes[1].Calss in SVClasses:
			self.handUpperLimit[1] = 9
		if self.Game.heroes[2].Calss in SVClasses:
			self.handUpperLimit[2] = 9
		self.initialDecks = {1: deck1 if deck1 else Default1,
							 2: deck2 if deck2 else Default2}
		self.startingDeckIdentities = {1: [], 2: []}
		self.startingHandIdentities = {1: [], 2: []}
		
	def initialize(self):
		self.initializeDecks()
		self.initializeHands()
		
	def initializeDecks(self):
		for ID in range(1, 3):
			Class = self.Game.heroes[ID].Class  # Hero's class
			for obj in self.initialDecks[ID]:
				if obj.name == "Transfer Student": obj = self.Game.transferStudentType
				card = obj(self.Game, ID)
				if "Galakrond, " in card.name:
					# 检测过程中，如果目前没有主迦拉克隆或者与之前检测到的迦拉克隆与玩家的职业不符合，则把检测到的迦拉克隆定为主迦拉克隆
					if self.Game.Counters.primaryGalakronds[ID] is None or (
							self.Game.Counters.primaryGalakronds[ID].Class != Class and card.Class == Class):
						self.Game.Counters.primaryGalakronds[ID] = card
				self.decks[ID].append(card)
				self.startingDeckIdentities[ID].append(card.identity)
			npshuffle(self.decks[ID])

	def initializeHands(self):  # 起手要换的牌都已经从牌库中移出到mulligan列表中，
		# 如果卡组有双传说任务，则起手时都会上手
		mainQuests = {1: [], 2: []}
		mulliganSize = {1: 3, 2: 4}
		for ID in range(1, 3):
			mainQuests[ID] = [card for card in self.decks[ID] if card.description.startswith("Quest")]
			numQueststoDraw = min(len(mainQuests[ID]), mulliganSize[ID])
			if numQueststoDraw > 0:
				queststoDraw = npchoice(mainQuests[ID], numQueststoDraw, replace=False)
				for quest in queststoDraw:
					self.Game.mulligans[ID].append(extractfrom(quest, self.decks[ID]))
			for i in range(mulliganSize[ID] - numQueststoDraw):
				self.Game.mulligans[ID].append(self.decks[ID].pop())

	def mulligan(self, indices1, indices2):
		indices = {1: indices1, 2: indices2}  # indicesCards是要替换的手牌的列表序号，如[1, 3]
		for ID in range(1, 3):
			cardstoReplace = []
			# self.Game.mulligans is the cards currently in players' hands.
			if indices[ID]:
				for num in range(1, len(indices[ID]) + 1):
					# 起手换牌的列表mulligans中根据要换掉的牌的序号从大到小摘掉，然后在原处补充新手牌
					cardstoReplace.append(self.Game.mulligans[ID].pop(indices[ID][-num]))
					self.Game.mulligans[ID].insert(indices[ID][-num], self.decks[ID].pop())
			self.decks[ID] += cardstoReplace
			for card in self.decks[ID]: card.entersDeck()  # Cards in deck arm their possible trigDeck
			npshuffle(self.decks[ID])  # Shuffle the deck after mulligan
			# 手牌和牌库中的牌调用entersHand和entersDeck,注册手牌和牌库扳机
			self.hands[ID] = [card.entersHand() for card in self.Game.mulligans[ID]]
			self.Game.mulligans[ID] = []
			self.startingHandIdentities[ID] = [card.identity for card in self.hands[ID]]  # Record starting hand
			for card in self.hands[1] + self.hands[2]:
				card.effectCanTrigger()
				card.checkEvanescent()

		if self.Game.GUI: self.Game.GUI.update()
		self.addCardtoHand(TheCoin(self.Game, 2), 2)
		self.Game.Manas.calcMana_All()
		for ID in range(1, 3):
			for card in self.hands[ID] + self.decks[ID]:
				if "Start of Game" in card.index:
					card.startofGame()
		self.drawCard(1)
		for card in self.hands[1] + self.hands[2]:
			card.effectCanTrigger()
			card.checkEvanescent()
		if self.Game.GUI: self.Game.GUI.update()

	# 双人游戏中一方很多控制自己的换牌，之后两个游戏中复制对方的手牌和牌库信息
	def mulligan1Side(self, ID, indices):
		cardstoReplace = []
		if indices:
			for num in range(1, len(indices) + 1):
				cardstoReplace.append(self.Game.mulligans[ID].pop(indices[-num]))
				self.Game.mulligans[ID].insert(indices[-num], self.decks[ID].pop())
		self.hands[ID] = self.Game.mulligans[ID]
		self.decks[ID] += cardstoReplace
		for card in self.decks[ID]: card.entersDeck()
		npshuffle(self.decks[ID])

	# 在双方给予了自己的手牌和牌库信息之后把它们注册同时触发游戏开始时的效果
	def startGame(self):  # This ID is the opponent's ID
		for ID in range(1, 3):  # 直接拿着mulligans开始
			self.hands[ID] = [card.entersHand() for card in self.hands[ID]]
			for card in self.decks[ID]: card.entersDeck()
			self.Game.mulligans[ID] = []
		for ID in range(1, 3):
			for card in self.hands[ID]:
				self.startingHandIdentities[ID].append(card.identity)
				for card in self.hands[1] + self.hands[2]:
					card.effectCanTrigger()
					card.checkEvanescent()

		self.addCardtoHand(TheCoin(self.Game, 2), 2)
		self.Game.Manas.calcMana_All()
		for ID in range(1, 3):
			for card in self.hands[ID] + self.decks[ID]:
				if "Start of Game" in card.index: card.startofGame()
		self.drawCard(1)
		for card in self.hands[1] + self.hands[2]:
			card.effectCanTrigger()
			card.checkEvanescent()
		if self.Game.GUI: self.Game.GUI.update()

	def handNotFull(self, ID):
		return len(self.hands[ID]) < self.handUpperLimit[ID]

	def spaceinHand(self, ID):
		return self.handUpperLimit[ID] - len(self.hands[ID])

	def outcastcanTrigger(self, card):
		posinHand = self.hands[card.ID].index(card)
		return posinHand == 0 or posinHand == len(self.hands[card.ID]) - 1

	def noDuplicatesinDeck(self, ID):
		record = []
		for card in self.decks[ID]:
			if type(card) not in record:
				record.append(type(card))
			else:
				return False
		return True

	def noMinionsinDeck(self, ID):
		for card in self.decks[ID]:
			if card.type == "Minion":
				return False
		return True

	def holdingDragon(self, ID, minion=None):
		if minion == None:  # When card not in hand and wants to check if a Dragon is in hand
			for card in self.hands[ID]:
				if card.type == "Minion" and "Dragon" in card.race:
					return True
		else:  # When the minion is inHand and wants to know if it can trigger after being played.
			for card in self.hands[ID]:
				if card.type == "Minion" and "Dragon" in card.race and card != minion:
					return True
		return False

	def holdingSpellwith5CostorMore(self, ID):
		for card in self.hands[ID]:
			if card.type == "Spell" and card.mana >= 5:
				return True
		return False

	def holdingCardfromAnotherClass(self, ID, card=None):
		Class = self.Game.heroes[ID].Class
		if card:
			for cardinHand in self.hands[ID]:
				if Class not in cardinHand.Class and cardinHand.Class != "Neutral" and cardinHand != card:
					return True
		else:
			for cardinHand in self.hands[ID]:
				if Class not in cardinHand.Class and cardinHand.Class != "Neutral":
					return True
		return False

	# 抽牌一次只能一张，需要废除一次抽多张牌的功能，因为这个功能都是用于抽效果指定的牌。但是这些牌中如果有抽到时触发的技能，可能会导致马上抽牌把列表后面的牌提前抽上来
	# 现在规则为如果要连续抽2张法术，则分两次检测牌库中的法术牌，然后随机抽一张。
	# 如果这个规则是正确的，则在牌库只有一张夺灵者哈卡的堕落之血时，抽到这个法术之后会立即额外抽牌，然后再塞进去两张堕落之血，那么第二次抽法术可能会抽到新洗进去的堕落之血。
	# Damage taken due to running out of card will keep increasing. Refilling the deck won't reset the damage you take next time you draw from empty deck
	def drawCard(self, ID, card=None):
		game, GUI = self.Game, self.Game.GUI
		if card is None:  # Draw from top of the deck.
			PRINT(game, "Hero %d draws from the top of the deck" % ID)
			if self.decks[ID]:  # Still have cards left in deck.
				card = self.decks[ID].pop()
				mana = card.mana
			else:
				PRINT(game, "Hero%d's deck is empty and will take damage" % ID)
				self.noCards[ID] += 1  # 如果在疲劳状态有卡洗入牌库，则疲劳值不会减少，在下次疲劳时，仍会从当前的非零疲劳值开始。
				damage = self.noCards[ID]
				if GUI: GUI.fatigueAni(ID, damage)
				dmgTaker = game.scapegoat4(game.heroes[ID])
				dmgTaker.takesDamage(None, damage, damageType="Ability")  # 疲劳伤害没有来源
				return (None, 0)
		else:
			if isinstance(card, (int, np.int32, np.int64)):
				card = self.decks[ID].pop(card)
			else:
				card = extractfrom(card, self.decks[ID])
			PRINT(game, "Hero %d draws %s from the deck" % (ID, card.name))
			mana = card.mana
		card.leavesDeck()
		if self.handNotFull(ID):
			if GUI: btn = GUI.drawCardAni_1(card)
			cardTracker = [card]  # 把这张卡放入一个列表，然后抽牌扳机可以对这个列表进行处理同时传递给其他抽牌扳机
			game.sendSignal("CardDrawn", ID, None, cardTracker, mana, "")
			if cardTracker[0].type == "Spell" and "Casts When Drawn" in cardTracker[0].index:
				PRINT(game, "%s is drawn and cast." % cardTracker[0].name)
				if GUI: btn.remove()
				cardTracker[0].whenEffective()
				self.drawCard(ID)
				cardTracker[0].afterDrawingCard()
			else:  # 抽到的牌可以加入手牌。
				if cardTracker[0].type == "Minion" and cardTracker[0].triggers["Drawn"] != []:
					PRINT(game, "%s is drawn and triggers its effect." % cardTracker[0].name)
					for func in cardTracker[0].triggers["Drawn"]: func()
				cardTracker[0] = cardTracker[0].entersHand()
				self.hands[ID].append(cardTracker[0])
				if GUI: GUI.drawCardAni_2(btn, cardTracker[0])
				game.sendSignal("CardEntersHand", ID, None, cardTracker, mana, "")
				game.Manas.calcMana_All()
			return (cardTracker[0], mana)
		else:
			PRINT(game, "Player's hand is full. The drawn card %s is milled" % card.name)
			if GUI: GUI.millCardAni(card)
			return (None, 0)
			
	# Will force the ID of the card to change.
	def addCardtoHand(self, obj, ID, comment="", byDiscover=False, i=-1):
		game, GUI = self.Game, self.Game.GUI
		if not isinstance(obj, (list, np.ndarray, tuple)):  # if the obj is not a list, turn it into a single-element list
			obj = [obj]
		morethan3 = len(obj) > 2
		for card in obj:
			if self.handNotFull(ID):
				if comment == "type":
					card = card(game, ID)
				elif comment == "index":
					card = game.cardPool[card](game, ID)
				card.ID = ID
				if GUI: btn = GUI.cardEntersHandAni_1(card)
				self.hands[ID].insert(i + 100 * (i < 0), card)
				if GUI: GUI.cardEntersHandAni_2(btn, i, steps=5 if morethan3 else 10)
				card = card.entersHand()
				game.sendSignal("CardEntersHand", ID, None, [card], 0, comment)
				if byDiscover: game.sendSignal("PutinHandbyDiscover", ID, None, obj, 0, '')
			else:
				break
		game.Manas.calcMana_All()
		
	def replaceCardDrawn(self, targetHolder, newCard):
		ID = targetHolder[0].ID
		isPrimaryGalakrond = targetHolder[0] == self.Game.Counters.primaryGalakronds[ID]
		targetHolder[0] = newCard
		if isPrimaryGalakrond: self.Game.Counters.primaryGalakronds[ID] = newCard

	def replaceCardinHand(self, card, newCard):
		ID = card.ID
		for i in range(len(self.hands[ID])):
			if self.hands[ID][i] == card:
				card.leavesHand()
				self.hands[ID].pop(i)
				self.Game.sendSignal("CardLeavesHand", ID, None, card, 0, "")
				self.addCardtoHand(newCard, ID, "card", i)
				break

	def replaceCardinDeck(self, card, newCard):
		ID = card.ID
		try:
			i = self.decks[ID].index(card)
			card.leavesDeck()
			self.decks[ID].pop(i)
			self.decks[ID].insert(i, newCard)
		except:
			pass

	# All the cards shuffled will be into the same deck. If necessary, invoke this function for each deck.
	# PlotTwist把手牌洗入牌库的时候，手牌中buff的随从两次被抽上来时buff没有了。
	# 假设洗入牌库这个动作会把一张牌初始化
	def shuffleCardintoDeck(self, obj, initiatorID, enemyCanSee=True, sendSig=True):
		if obj:
			curGame = self.Game
			if curGame.GUI: curGame.GUI.shuffleCardintoDeckAni(obj, enemyCanSee)
			if isinstance(obj, (list, np.ndarray)):
				ID = obj[0].ID
				newDeck = self.decks[ID] + obj
				for card in obj: card.entersDeck()
			else:  # Shuffle a single card
				ID = obj.ID
				newDeck = self.decks[ID] + [obj]
				obj.entersDeck()

			if curGame.mode == 0:
				if curGame.guides:
					order = curGame.guides.pop(0)
				else:
					order = list(range(len(newDeck)))
					npshuffle(order)
					curGame.fixedGuides.append(tuple(order))
				self.decks[ID] = [newDeck[i] for i in order]
			if sendSig: curGame.sendSignal("CardShuffled", initiatorID, None, obj, 0, "")
			
	def burialRite(self, ID, minion):
		self.Game.summonfromHand(minion, ID, -1, ID)
		minion.getsSilenced()
		minion.dead = True
		self.Game.sendSignal("BurialRite", ID, None, minion, 0, "")

	def discardAll(self, ID):
		if self.hands[ID]:
			cards, cost, isRightmostCardinHand = self.extractfromHand(None, ID=ID, all=True, enemyCanSee=True)
			for card in cards:
				PRINT(self.Game, "Card %s in player's hand is discarded:" % card.name)
				for func in card.triggers["Discarded"]: func()
				self.Game.Counters.cardsDiscardedThisGame[ID].append(card.index)
				self.Game.Counters.shadows[card.ID] += 1
				self.Game.sendSignal("PlayerDiscardsCard", card.ID, None, card, 0, "")
			self.Game.Manas.calcMana_All()
			
	def discardCard(self, ID, card=None):
		if card is None:  # Discard a random card.
			if self.hands[ID]:
				card = npchoice(self.hands[ID])
				card, cost, isRightmostCardinHand = self.extractfromHand(card, enemyCanSee=True)
				PRINT(self.Game, "Card %s in player's hand is discarded:" % card.name)
				for func in card.triggers["Discarded"]: func()
				self.Game.Manas.calcMana_All()
				self.Game.Counters.cardsDiscardedThisGame[ID].append(card.index)
				self.Game.Counters.shadows[card.ID] += 1
				self.Game.sendSignal("CardLeavesHand", card.ID, None, card, 0, "")
				self.Game.sendSignal("PlayerDiscardsCard", card.ID, None, card, 0, "")
		else:  # Discard a chosen card.
			i = card if isinstance(card, (int, np.int32, np.int64)) else self.hands[ID].index(card)
			card = self.hands[ID].pop(i)
			card.leavesHand()
			if self.Game.GUI: self.Game.GUI.cardsLeaveHandAni(card, enemyCanSee=True)
			PRINT(self.Game, "Card %s in player's hand is discarded:" % card.name)
			for func in card.triggers["Discarded"]: func()
			self.Game.Manas.calcMana_All()
			self.Game.Counters.cardsDiscardedThisGame[ID].append(card.index)
			self.Game.Counters.shadows[card.ID] += 1
			self.Game.sendSignal("CardLeavesHand", card.ID, None, card, 0, "")
			self.Game.sendSignal("PlayerDiscardsCard", card.ID, None, card, 0, "")
			
	# 只能全部拿出手牌中的所有牌或者拿出一个张，不能一次拿出多张指定的牌
	def extractfromHand(self, card, ID=0, all=False, enemyCanSee=False):
		if all:  # Extract the entire hand.
			temp = self.hands[ID]
			if temp:
				self.hands[ID] = []
				for card in temp:
					card.leavesHand()
					self.Game.sendSignal("CardLeavesHand", card.ID, None, card, 0, '')
				# 一般全部取出手牌的时候都是直接洗入牌库，一般都不可见
				if self.Game.GUI: self.Game.GUI.cardsLeaveHandAni(temp, False)
			return temp, 0, -2  # -2 means the posinHand doesn't have real meaning.
		else:
			if not isinstance(card, (int, np.int32, np.int64)):
				# Need to keep track of the card's location in hand.
				index, cost = self.hands[card.ID].index(card), card.getMana()
				posinHand = index if index < len(self.hands[card.ID]) - 1 else -1
				card = self.hands[card.ID].pop(index)
			else:  # card is a number
				posinHand = card if card < len(self.hands[ID]) - 1 else -1
				card = self.hands[ID].pop(card)
				cost = card.getMana()
			card.leavesHand()
			if self.Game.GUI: self.Game.GUI.cardsLeaveHandAni(card, enemyCanSee)
			self.Game.sendSignal("CardLeavesHand", card.ID, None, card, 0, '')
			return card, cost, posinHand
			
	# 只能全部拿牌库中的所有牌或者拿出一个张，不能一次拿出多张指定的牌
	def extractfromDeck(self, card, ID=0, all=False, enemyCanSee=True):
		if all:  # For replacing the entire deck or throwing it away.
			temp = self.decks[ID]
			self.decks[ID] = []
			for card in temp: card.leavesDeck()
			return temp, 0, False
		else:
			if not isinstance(card, (int, np.int32, np.int64)):
				card = extractfrom(card, self.decks[card.ID])
			else:
				card = self.decks[ID].pop(card)
			card.leavesDeck()
			if self.Game.GUI: self.Game.GUI.cardLeavesDeckAni(card, enemyCanSee=enemyCanSee)
			return card, 0, False
			
	def removeDeckTopCard(self, ID):
		try:  # Should have card most of the time.
			card = self.decks[ID].pop(0)
			card.leavesDeck()
			PRINT(self.Game, "The top card %s in player %d's deck is removed" % (card.name, ID))
			return card
		except:
			return None
			
	def createCopy(self, game):
		if self not in game.copiedObjs:
			Copy = type(self)(game)
			game.copiedObjs[self] = Copy
			Copy.startingDeckIdentities, Copy.startingHandIdentities = self.startingDeckIdentities, self.startingHandIdentities
			Copy.initialDecks = self.initialDecks
			Copy.hands, Copy.decks = {1: [], 2: []}, {1: [], 2: []}
			Copy.knownDecks = {1: {"to self": []}, 2: {"to self": []}}
			Copy.noCards, Copy.handUpperLimit = copy.deepcopy(self.noCards), copy.deepcopy(self.handUpperLimit)
			Copy.decks = {1: [card.createCopy(game) for card in self.decks[1]],
						  2: [card.createCopy(game) for card in self.decks[2]]}
			Copy.hands = {1: [card.createCopy(game) for card in self.hands[1]],
						  2: [card.createCopy(game) for card in self.hands[2]]}
			return Copy
		else:
			return game.copiedObjs[self]
			
			
Default1 = [OathlessKnight, OathlessKnight, OathlessKnight, EntrancingBlow, EntrancingBlow, ElvenArcher, ElvenArcher, ElvenArcher, ElvenArcher, ElvenArcher, ElvenArcher,
			]
			
Default2 = [EntrancingBlow, EntrancingBlow, EntrancingBlow, EntrancingBlow, PotionofIllusion, PotionofIllusion, Bamboozle, Bamboozle, ShadowjewelerHanar, ShadowjewelerHanar, TheLurkerBelow, TheLurkerBelow, RollingFireball, RollingFireball, SorcerersApprentice, HighAbbessAlura, CommandingShout, PuzzleBoxofYoggSaron, PuzzleBoxofYoggSaron, PuzzleBoxofYoggSaron
			]