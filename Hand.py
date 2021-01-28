from Academy import TransferStudent
from SV_Basic import SVClasses
from Basic import TheCoin

import copy
from numpy.random import choice as npchoice
from numpy.random import randint as nprandint
from numpy.random import shuffle as npshuffle
import numpy as np
from collections import Counter as cnt

import inspect

def extractfrom(target, listObj):
	try: return listObj.pop(listObj.index(target))
	except: return None

class Hand_Deck:
	def __init__(self, Game, deck1=[], deck2=[]):  # 通过卡组列表加载卡组
		self.Game = Game
		self.hands = {1: [], 2: []}
		self.decks = {1: [], 2: []}
		self.noCards = {1: 0, 2: 0}
		self.handUpperLimit = {1: 10, 2: 10}
		if self.Game.heroes[1].Class in SVClasses:
			self.handUpperLimit[1] = 9
		if self.Game.heroes[2].Class in SVClasses:
			self.handUpperLimit[2] = 9
		self.initialDecks = {1: deck1 if deck1 else Default1, 2: deck2 if deck2 else Default2}
		self.cards_1Possi = {1:[], 2:[]} #可以明确知道是哪一张的全部资源牌
		self.cards_XPossi = {1:[], 2:[]} #只知道这张牌可能是什么的资源牌
		self.trackedHands = {1:[], 2:[]} #可以追踪的手牌，但是它们可能明确知道是哪一张，也可能是只知道可能是什么的手牌
		
	def initialize(self):
		self.initializeDecks()
		self.initializeHands()
		
	def initializeDecks(self):
		for ID in range(1, 3):
			Class = self.Game.heroes[ID].Class  # Hero's class
			for obj in self.initialDecks[ID]:
				if obj.name == "Transfer Student": obj = self.Game.transferStudentType
				self.cards_1Possi[ID].append((None, (obj, )))
				card = obj(self.Game, ID)
				if "Galakrond, " in card.name:
					# 检测过程中，如果目前没有主迦拉克隆或者与之前检测到的迦拉克隆与玩家的职业不符合，则把检测到的迦拉克隆定为主迦拉克隆
					if self.Game.Counters.primaryGalakronds[ID] is None or (
							self.Game.Counters.primaryGalakronds[ID].Class != Class and card.Class == Class):
						self.Game.Counters.primaryGalakronds[ID] = card
				self.decks[ID].append(card)
			npshuffle(self.decks[ID])
			for i, card in enumerate(self.decks[ID]): #克苏恩一定不会出现在起始手牌中，只会沉在牌库底，然后等待效果触发后的洗牌
				if card.name == "C'Thun, the Shattered":
					self.decks[ID].insert(0, self.decks[ID].pop(i))
					break
					
	def initializeHands(self):  # 起手要换的牌都已经从牌库中移出到mulligan列表中，
		# 如果卡组有双传说任务，则起手时都会上手
		mainQuests = {1: [], 2: []}
		mulliganSize = {1: 3, 2: 4}
		if self.Game.heroes[2].Class in SVClasses:
			mulliganSize[2] = 3
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
			for card in self.hands[1] + self.hands[2]:
				card.effCanTrig()
				card.checkEvanescent()

		if self.Game.GUI: self.Game.GUI.update()
		if not self.Game.heroes[2].Class in SVClasses:
			self.addCardtoHand(TheCoin(self.Game, 2), 2)
		self.Game.Manas.calcMana_All()
		for ID in range(1, 3):
			for card in self.hands[ID] + self.decks[ID]:
				if "Start of Game" in card.index:
					card.startofGame()
		self.drawCard(1)
		for card in self.hands[1] + self.hands[2]:
			card.effCanTrig()
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
			for card in self.hands[1] + self.hands[2]:
				card.effCanTrig()
				card.checkEvanescent()
		if not self.Game.heroes[2].Class in SVClasses:
			self.addCardtoHand(TheCoin(self.Game, 2), 2)
		self.Game.Manas.calcMana_All()
		for ID in range(1, 3):
			for card in self.hands[ID] + self.decks[ID]:
				if "Start of Game" in card.index: card.startofGame()
		self.drawCard(1)
		for card in self.hands[1] + self.hands[2]:
			card.effCanTrig()
			card.checkEvanescent()
		if self.Game.GUI: self.Game.GUI.update()

	#intoHD=0: include in hand
	#intoHD=1: include in deck
	#intoHD=other: include in both
	def includePossi(self, card, intoHD): #intoHD == 0, 1, other integers
		tup, ID = (card.creator, card.possi), card.ID
		if intoHD != 1: self.trackedHands[ID].append(tup) #possi is added to hand
		if intoHD != 0: #possi is added to the decks
			if len(tup[1]) == 1: self.cards_1Possi[ID].append(tup)
			else: self.cards_XPossi[ID].append(tup)
			
	#fromHD=0: only rule out from hand
	#fromHD=1: only rule out from deck
	#fromHD=other: rule out from both
	def ruleOut(self, card, fromHD): #fromHD = 0, 1, other integers
		tup = (card.creator, card.possi)
		ID = card.ID
		if fromHD != 1: #Rule out from hand
			try: self.trackedHands[ID].remove(tup)
			except: pass
		if fromHD != 0: #Also rule out from deck
			try: self.cards_1Possi[ID].remove(tup)
			except:
				try: self.cards_1Possi[ID].remove(tup)
				except: pass
				
	def handNotFull(self, ID):
		return len(self.hands[ID]) < self.handUpperLimit[ID]

	def spaceinHand(self, ID):
		return self.handUpperLimit[ID] - len(self.hands[ID])

	def outcastcanTrig(self, card):
		posinHand = self.hands[card.ID].index(card)
		return posinHand == 0 or posinHand == len(self.hands[card.ID]) - 1

	def noDuplicatesinDeck(self, ID):
		#typeCounter = cnt((type(card) for card in self.decks[ID]))
		#return all(typeCounter.values())
		record = []
		for card in self.decks[ID]:
			if type(card) not in record: record.append(type(card))
			else: return False
		return True
		
	def noMinionsinDeck(self, ID):
		return not any(card.type == "Minion" for card in self.decks[ID])
		
	def noMinionsinHand(self, ID, minion=None):
		return not any(card.type == "Minion" and card is not minion for card in self.hands[ID])
		
	def holdingDragon(self, ID, minion=None):
		return any(card.type == "Minion" and "Dragon" in card.race and card is not minion \
				for card in self.hands[ID])
				
	def holdingSpellwith5CostorMore(self, ID):
		return any(card.type == "Spell" and card.mana >= 5 for card in self.hands[ID])
		
	def holdingCardfromAnotherClass(self, ID, card=None):
		Class = self.Game.heroes[ID].Class
		return any(Class not in cardinHand.Class and cardinHand.Class != "Neutral" and cardinHand is not card \
						for cardinHand in self.hands[ID])
						
	# 抽牌一次只能一张，需要废除一次抽多张牌的功能，因为这个功能都是用于抽效果指定的牌。但是这些牌中如果有抽到时触发的技能，可能会导致马上抽牌把列表后面的牌提前抽上来
	# 现在规则为如果要连续抽2张法术，则分两次检测牌库中的法术牌，然后随机抽一张。
	# 如果这个规则是正确的，则在牌库只有一张夺灵者哈卡的堕落之血时，抽到这个法术之后会立即额外抽牌，然后再塞进去两张堕落之血，那么第二次抽法术可能会抽到新洗进去的堕落之血。
	# Damage taken due to running out of card will keep increasing. Refilling the deck won't reset the damage you take next time you draw from empty deck
	def drawCard(self, ID, card=None):
		game, GUI = self.Game, self.Game.GUI
		if card is None:  # Draw from top of the deck.
			if self.decks[ID]:  # Still have cards left in deck.
				card = self.decks[ID].pop()
				mana = card.mana
			else:
				if game.heroes[ID].Class in SVClasses:
					whoDies = ID if game.heroes[ID].status["Draw to Win"] < 1 else 3 - ID
					game.heroes[whoDies].dead = True
					game.gathertheDead(True)
					return
				else:
					self.noCards[ID] += 1  # 如果在疲劳状态有卡洗入牌库，则疲劳值不会减少，在下次疲劳时，仍会从当前的非零疲劳值开始。
					damage = self.noCards[ID]
					if GUI: GUI.fatigueAni(ID, damage)
					dmgTaker = game.scapegoat4(game.heroes[ID])
					dmgTaker.takesDamage(None, damage, damageType="Ability")  # 疲劳伤害没有来源
					return None, -1 #假设疲劳时返回的数值是负数，从而可以区分爆牌（爆牌时仍然返回那个牌的法力值）和疲劳
		else:
			if isinstance(card, (int, np.int32, np.int64)): card = self.decks[ID].pop(card)
			else: card = extractfrom(card, self.decks[ID])
			mana = card.mana
		card.leavesDeck()
		if self.handNotFull(ID):
			if GUI: btn = GUI.drawCardAni_1(card)
			cardTracker = [card]  # 把这张卡放入一个列表，然后抽牌扳机可以对这个列表进行处理同时传递给其他抽牌扳机
			game.sendSignal("CardDrawn", ID, None, cardTracker, mana, "")
			self.Game.Counters.numCardsDrawnThisTurn[ID] += 1
			if cardTracker[0].type == "Spell" and "Casts When Drawn" in cardTracker[0].index:
				if GUI: btn.remove()
				cardTracker[0].whenEffective()
				game.sendSignal("SpellCastWhenDrawn", ID, None, cardTracker[0], mana, "")
				#抽到之后施放的法术如果检测到玩家处于濒死状态，则不会再抽一张。如果玩家有连续抽牌的过程，则执行下次抽牌
				if game.heroes[ID].health > 0 and not game.heroes[ID].dead:
					self.drawCard(ID)
				cardTracker[0].afterDrawingCard()
			else:  # 抽到的牌可以加入手牌。
				if cardTracker[0].type == "Minion" or cardTracker[0].type == "Amulet":
					cardTracker[0].whenDrawn()
				cardTracker[0] = cardTracker[0].entersHand()
				self.hands[ID].append(cardTracker[0])
				if GUI: GUI.drawCardAni_2(btn, cardTracker[0])
				game.sendSignal("CardEntersHand", ID, None, cardTracker, mana, "")
				game.Manas.calcMana_All()
			return cardTracker[0], mana
		else:
			if GUI: GUI.millCardAni(card)
			return None, mana #假设即使爆牌也可以得到要抽的那个牌的费用，用于神圣愤怒
			
	# def createCard(self, obj, ID, comment)
	# Will force the ID of the card to change. obj can be an empty list/tuple
	#Creator是这张/些牌的创建者，creator=None，则它们的creator继承原来的。
	#possi是这张/些牌的可能性，possi=()说明它们都是确定的牌
	def addCardtoHand(self, obj, ID, byType=False, byDiscover=False, pos=-1, 
									showAni=True, creator=None, possi=()):
		game, GUI = self.Game, self.Game.GUI
		if not isinstance(obj, (list, np.ndarray, tuple)):  # if the obj is not a list, turn it into a single-element list
			obj = [obj]
		morethan3 = len(obj) > 2
		for card in obj:
			if self.handNotFull(ID):
				if byType: card = card(game, ID)
				card.ID = ID
				if showAni:
					if GUI: btn = GUI.cardEntersHandAni_1(card)
					self.hands[ID].insert(pos + 100 * (pos < 0), card)
					if GUI: GUI.cardEntersHandAni_2(btn, pos, steps=5 if morethan3 else 10)
				else:
					self.hands[ID].insert(pos + 100 * (pos < 0), card)
					if GUI: GUI.cardReplacedinHand_Refresh(ID)
				card = card.entersHand()
				#只有已经提前定义了instance的卡牌会使用creator is None的选项
				if creator: card.creator = creator
				card.possi = possi if possi else (type(card), ) #possi=()说明这张牌的可能性是确定的
				card.tracked = True
				self.includePossi(card, intoHD=2)
				game.sendSignal("CardEntersHand", ID, None, [card], 0, "")
				if byDiscover: game.sendSignal("PutinHandbyDiscover", ID, None, obj, 0, '')
			else:
				self.Game.Counters.shadows[ID] += 1
		game.Manas.calcMana_All()
		
	def replaceCardDrawn(self, targetHolder, newCard, possi):
		ID = targetHolder[0].ID
		isPrimaryGalakrond = targetHolder[0] == self.Game.Counters.primaryGalakronds[ID]
		newCard.tracked, newCard.possi = True, possi
		targetHolder[0] = newCard
		if isPrimaryGalakrond: self.Game.Counters.primaryGalakronds[ID] = newCard
		
	def replaceCardinHand(self, card, newCard): #替换单张卡牌，用于在手牌中发生变形时
		ID = card.ID
		i = self.hands[ID].index(card)
		card.leavesHand()
		if card.tracked: self.ruleOut(card, fromHD=2)
		self.hands[ID].pop(i)
		self.addCardtoHand(newCard, ID, "", byDiscover=False, pos=i, showAni=False, possi=(newCard.creator, newCard.possi))
		
	#目前只有牌库中的迦拉克隆升级时会调用，对方是可以知道的
	def replaceCardinDeck(self, card, newCard):
		ID = card.ID
		try:
			i = self.decks[ID].index(card)
			card.leavesDeck()
			self.ruleOut(card, fromHD=1)
			self.decks[ID][i] = newCard
			self.Game.sendSignal("DeckCheck", ID, None, None, 0, "")
		except: pass
		
	def replaceWholeDeck(self, ID, newCards):
		self.extractfromDeck(0, ID, all=True)
		self.decks[ID] = newCards
		for card in newCards: card.entersDeck()
		self.Game.sendSignal("DeckCheck", ID, None, None, 0, "")
		
	def replacePartofDeck(self, ID, indices, newCards):
		for card in newCards: card.leavesDeck()
		deck = self.decks[ID]
		for i, oldCard, newCard in zip(indices, deck, newCards):
			oldCard.leavesDeck()
			deck[i] = newCard
			newCard.entersDeck()
		self.Game.sendSignal("DeckCheck", ID, None, None, 0, "")
		
	# All the cards shuffled will be into the same deck. If necessary, invoke this function for each deck.
	# PlotTwist把手牌洗入牌库的时候，手牌中buff的随从两次被抽上来时buff没有了。
	# 假设洗入牌库这个动作会把一张牌初始化
	def shuffleintoDeck(self, obj, initiatorID,
							enemyCanSee=True, sendSig=True, creator=None, possi=()):
		if obj:
			curGame = self.Game
			if curGame.GUI: curGame.GUI.shuffleintoDeckAni(obj, enemyCanSee)
			#如果obj不是一个Iterable，则将其变成一个列表
			if not isinstance(obj, (list, tuple, np.ndarray)):
				obj = [obj]
			ID = obj[0].ID
			newDeck = self.decks[ID] + obj
			for card in obj:
				card.entersDeck()
				card.possi = possi if possi else (type(card), )
				if creator: card.creator
				self.includePossi(card, intoHD=1)
			if curGame.mode == 0:
				if curGame.guides:
					order = curGame.guides.pop(0)
				else:
					order = list(range(len(newDeck)))
					npshuffle(order)
					curGame.fixedGuides.append(tuple(order))
				self.decks[ID] = [newDeck[i] for i in order]
			if sendSig: curGame.sendSignal("CardShuffled", initiatorID, None, obj, 0, "")
			curGame.sendSignal("DeckCheck", ID, None, None, 0, "")
	
	#Given the index in hand. Can't shuffle multiple cards except for whole hand
	def shuffle_Hand2Deck(self, i, ID, initiatorID, all=True):
		if all:
			hand = self.extractfromHand(None, ID, all, enemyCanSee=False)[0]
			for card in hand:
				card.reset(ID, isKnown=False)
				self.shuffleintoDeck(card, initiatorID, enemyCanSee=False, sendSig=True, possi=card.possi)
		elif i:
			card = self.extractfromHand(i, ID, all, enemyCanSee=False)[0]
			card.reset(ID, isKnown=False)
			self.shuffleintoDeck(card, initiatorID, enemyCanSee=False, sendSig=True, possi=card.possi)
			
	def burialRite(self, ID, minions, noSignal=False):
		if not isinstance(minions, list):
			minions = [minions]
		for minion in minions:
			self.Game.summonfrom(minion, ID, -1, None, fromHand=True)
			minion.loseAbilityInhand()
		for minion in minions:
			self.Game.killMinion(minion, minion)
		self.Game.gathertheDead()
		if not noSignal:
			for minion in minions:
				self.Game.Counters.numBurialRiteThisGame[ID] += 1
				self.Game.sendSignal("BurialRite", ID, None, minion, 0, "")
				
	def discardAll(self, ID):
		if self.hands[ID]:
			cards, cost, isRightmostCardinHand = self.extractfromHand(None, ID=ID, all=True, enemyCanSee=True)
			n = len(cards)
			for card in cards:
				self.ruleOut(card, fromHD=2)
				card.whenDiscarded()
				self.Game.Counters.cardsDiscardedThisGame[ID].append(card.index)
				self.Game.Counters.cardsDiscardedThisTurn[ID].append(card.index)
				self.Game.Counters.shadows[card.ID] += 1
				self.Game.sendSignal("PlayerDiscardsCard", card.ID, None, card, -1, "")
			self.Game.sendSignal("PlayerDiscardsHand", ID, None, None, n, "")
			self.Game.Manas.calcMana_All()

	def discardCard(self, ID, card=None):
		if card is None:  # Discard a random card. Deprecated
			if self.hands[ID]:
				card = npchoice(self.hands[ID])
				card, cost, isRightmostCardinHand = self.extractfromHand(card, enemyCanSee=True)
				self.Game.sendSignal("PlayerDiscardsCard", card.ID, None, card, 1, "")
				card.whenDiscarded()
				self.Game.Manas.calcMana_All()
				self.Game.Counters.cardsDiscardedThisGame[ID].append(card.index)
				self.Game.Counters.cardsDiscardedThisTurn[ID].append(card.index)
				self.Game.Counters.shadows[card.ID] += 1
				self.Game.sendSignal("CardLeavesHand", card.ID, None, card, 0, "")
		else:  # Discard a chosen card.
			i = card if isinstance(card, (int, np.int32, np.int64)) else self.hands[ID].index(card)
			card = self.hands[ID].pop(i)
			card.leavesHand()
			self.ruleOut(card, fromHD=2) #rule out from both hand and deck
			if self.Game.GUI: self.Game.GUI.cardsLeaveHandAni(card, enemyCanSee=True)
			self.Game.sendSignal("PlayerDiscardsCard", card.ID, None, card, 1, "")
			card.whenDiscarded()
			self.Game.Manas.calcMana_All()
			self.Game.Counters.cardsDiscardedThisGame[ID].append(card.index)
			self.Game.Counters.cardsDiscardedThisTurn[ID].append(card.index)
			self.Game.Counters.shadows[card.ID] += 1
			self.Game.sendSignal("CardLeavesHand", card.ID, None, card, 0, "")
			
	# 只能全部拿出手牌中的所有牌或者拿出一个张，不能一次拿出多张指定的牌
	def extractfromHand(self, card, ID=0, all=False, enemyCanSee=False):
		if all:  # Extract the entire hand.
			cardsOut = self.hands[ID]
			if cardsOut:
				self.hands[ID] = []
				for card in cardsOut:
					card.leavesHand()
					if card.tracked:
						#洗牌的时候一般都不会涉及修改资源牌的可能选项
						self.ruleOut(card, fromHD=0)
					self.Game.sendSignal("CardLeavesHand", card.ID, None, card, 0, '')
				# 一般全部取出手牌的时候都是直接洗入牌库，一般都不可见
				if self.Game.GUI: self.Game.GUI.cardsLeaveHandAni(cardsOut, False)
			return cardsOut, 0, -2  # -2 means the posinHand doesn't have real meaning.
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
			#取出单张手牌的时候，如果其可以追踪，则需要从cards_1Possi或者cards_XPossi里面排除
			if enemyCanSee:
				#If the card is tracked, rule out from both hand and deck; otherwise only rule out from deck
				self.ruleOut(card, fromHD=1+card.tracked)
				
			if self.Game.GUI: self.Game.GUI.cardsLeaveHandAni(card, enemyCanSee)
			self.Game.sendSignal("CardLeavesHand", card.ID, None, card, 0, '')
			return card, cost, posinHand

	# 只能全部拿牌库中的所有牌或者拿出一个张，不能一次拿出多张指定的牌
	def extractfromDeck(self, card, ID=0, all=False, enemyCanSee=True):
		if all:  # For replacing the entire deck or throwing it away.
			cardsOut = self.decks[ID]
			self.decks[ID] = []
			for card in cardsOut: card.leavesDeck()
			self.cards_1Possi, self.cards_XPossi = [], []
			return cardsOut, 0, False
		else:
			if not isinstance(card, (int, np.int32, np.int64)):
				card = extractfrom(card, self.decks[card.ID])
			else:
				if not self.decks[ID]: return None, 0, False
				card = self.decks[ID].pop(card)
			card.leavesDeck()
			if enemyCanSee: self.ruleOut(card, fromHD=1)
			if self.Game.GUI: self.Game.GUI.cardLeavesDeckAni(card, enemyCanSee=enemyCanSee)
			return card, 0, False
			
	#所有被移除的卡牌都会被展示
	def removeDeckTopCard(self, ID, num=1):
		cards = []
		for i in range(num):
			card = self.extractfromDeck(-1, ID)[0] #The cards removed from deck top can always be seen by opponent
			if card: cards.append(card)
			else: None
		return cards
		
	def createCopy(self, game):
		if self not in game.copiedObjs:
			Copy = type(self)(game)
			game.copiedObjs[self] = Copy
			Copy.initialDecks = self.initialDecks
			Copy.hands, Copy.decks = {1: [], 2: []}, {1: [], 2: []}
			Copy.noCards, Copy.handUpperLimit = copy.deepcopy(self.noCards), copy.deepcopy(self.handUpperLimit)
			Copy.decks = {1: [card.createCopy(game) for card in self.decks[1]],
						  2: [card.createCopy(game) for card in self.decks[2]]}
			Copy.hands = {1: [card.createCopy(game) for card in self.hands[1]],
						  2: [card.createCopy(game) for card in self.hands[2]]}
			return Copy
		else:
			return game.copiedObjs[self]

from CardPools import *

#from CardPools import RivaylianBandit, RivaylianBandit,\
#			QuixoticAdventurer, QuixoticAdventurer, QuixoticAdventurer,\
#			WanderingChef, WanderingChef, WanderingChef,\
#			Ramiel, Ramiel, Ramiel,\
#			IoJourneymage, IoJourneymage, IoJourneymage,\
#			ArchangelofRemembrance, ArchangelofRemembrance, ArchangelofRemembrance,\
#			GabrielHeavenlyVoice, GabrielHeavenlyVoice, GabrielHeavenlyVoice,\
#			GoblinQueen, GoblinQueen, GoblinQueen,\
#			FieranHavensentWindGod,\
#			RaRadianceIncarnate, RaRadianceIncarnate,\
#			WilbertGrandKnight, WilbertGrandKnight, WilbertGrandKnight,\
#			GoddessoftheWestWind, GoddessoftheWestWind, GoddessoftheWestWind,\
#			Set, Set, Set,\
#			AnveltJudgmentsCannon, AnveltJudgmentsCannon,\
#			NoaPrimalShipwright, NoaPrimalShipwright, NoaPrimalShipwright,\
#			FreezingTrap, ExplosiveTrap, IceBarrier, NeverSurrenderProfessorSlate, OhMyYogg, Counterspell, KirinTorMage, NatureStudies,\
#			RingToss, RingToss, RingToss_Corrupt, RingToss_Corrupt, MysteryWinner, MysteryWinner, BumperCar, BumperCar
			
			
#Default1 = [RivaylianBandit, RivaylianBandit,
#			QuixoticAdventurer, QuixoticAdventurer, QuixoticAdventurer,
#			WanderingChef, WanderingChef, WanderingChef,
#			Ramiel, Ramiel, Ramiel,
#			IoJourneymage, IoJourneymage, IoJourneymage,
#			ArchangelofRemembrance, ArchangelofRemembrance, ArchangelofRemembrance,
#			GabrielHeavenlyVoice, GabrielHeavenlyVoice, GabrielHeavenlyVoice,
#			GoblinQueen, GoblinQueen, GoblinQueen,
#			FieranHavensentWindGod,
#			RaRadianceIncarnate, RaRadianceIncarnate,
#			WilbertGrandKnight, WilbertGrandKnight, WilbertGrandKnight,
#			GoddessoftheWestWind, GoddessoftheWestWind, GoddessoftheWestWind,
#			Set, Set, Set,
#			AnveltJudgmentsCannon, AnveltJudgmentsCannon,
#			NoaPrimalShipwright, NoaPrimalShipwright, NoaPrimalShipwright
#			]
Default1 = [FreezingTrap, ExplosiveTrap, IceBarrier, RiggedFaireGame, ProfessorSlate, OhMyYogg, Counterspell, KirinTorMage, NatureStudies,
			RinlingsRifle, RingToss_Corrupt, RinlingsRifle, RingToss_Corrupt, MysteryWinner, MysteryWinner, BumperCar, BumperCar, NetherwindPortal, PackTactics, MysteryWinner,
			
			]

Default2 = [FreezingTrap, ExplosiveTrap, IceBarrier, RiggedFaireGame, ProfessorSlate, OhMyYogg, Counterspell, KirinTorMage, NatureStudies,
			RingToss, RingToss, RingToss_Corrupt, RingToss_Corrupt, MysteryWinner, MysteryWinner, BumperCar, BumperCar
			
			]