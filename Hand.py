from Academy import TransferStudent
from SV_Basic import SVClasses
from AcrossPacks import TheCoin

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
	def __init__(self, Game, deck1=None, deck2=None):  # 通过卡组列表加载卡组
		self.Game = Game
		self.hands = {1: [], 2: []}
		self.decks = {1: [], 2: []}
		self.noCards = {1: 0, 2: 0}
		self.handUpperLimit = {1: 10, 2: 10}
		if self.Game.heroes[1].Class in SVClasses:
			self.handUpperLimit[1] = 9
		if self.Game.heroes[2].Class in SVClasses:
			self.handUpperLimit[2] = 9
		self.type = ''
		self.initialDecks = {1: deck1 if deck1 else Default1, 2: deck2 if deck2 else Default2}
		self.cards_1Possi = {1:[], 2:[]} #可以明确知道是哪一张的全部资源牌
		self.cards_XPossi = {1:[], 2:[]} #只知道这张牌可能是什么的资源牌
		self.trackedHands = {1:[], 2:[]} #可以追踪的手牌，但是它们可能明确知道是哪一张，也可能是只知道可能是什么的手牌
		
	def initialize(self):
		self.initializeDecks()
		self.initializeHands()
		
	#InitializeDecks需要处理很多特殊的卡牌，比如转校生和迦拉克隆等。
	def initializeDecks(self):
		for ID in range(1, 3):
			Class = self.Game.heroes[ID].Class  # Hero's class
			for obj in self.initialDecks[ID]:
				if obj.name == "Transfer Student" and hasattr(obj, "transferStudentPool"): obj = obj.transferStudentPool[self.Game.boardID]
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
			#The legendary Quests and Questlines both have description starting with Quest
			mainQuests[ID] = [card for card in self.decks[ID] if card.description.startswith("Quest")]
			numQueststoDraw = min(len(mainQuests[ID]), mulliganSize[ID])
			if numQueststoDraw > 0:
				queststoDraw = npchoice(mainQuests[ID], numQueststoDraw, replace=False)
				for quest in queststoDraw:
					self.Game.mulligans[ID].append(extractfrom(quest, self.decks[ID]))
			for i in range(mulliganSize[ID] - numQueststoDraw):
				self.Game.mulligans[ID].append(self.decks[ID].pop())
	
	#Mulligan for 1P GUIs, where a single player controls all the plays.
	def mulliganBoth(self, indices1, indices2):
		#不涉及GUI的部分
		indices = {1: indices1, 2: indices2}  # indicesCards是要替换的手牌的列表序号，如[1, 3]
		GUI = self.Game.GUI
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
		
		#决定是否将硬币置入玩家手牌，同时如果手牌中有进入时会变形的牌，则需要改变
		addCoin = False
		if not self.Game.heroes[2].Class in SVClasses:
			self.Game.mulligans[2].append(TheCoin(self.Game, 2))
			addCoin = True
		if GUI:
			#在这里生成Sequence，然后存储在seqHolder[-1]里面
			GUI.mulligan_NewCardsfromDeckAni(addCoin)
			#The cards are added into hands and the sequence is further extended
			GUI.mulligan_MoveCards2Hand()
			self.Game.Manas.calcMana_All() #Mana change will be animated
			for ID in range(1, 3):
				for card in self.hands[ID] + self.decks[ID]:
					if "Start of Game" in card.index:
						GUI.seqHolder[-1].append(GUI.FUNC(GUI.showOffBoardTrig, card, "Appear"))
						card.startofGame()
			
			GUI.turnStartAni()
			self.drawCard(1)
			self.decideCardColors()
			GUI.seqHolder.pop(0).start()
		else: pass
		
	def decideCardColors(self):
		for card in self.hands[1] + self.hands[2]:
			card.effCanTrig()
			card.checkEvanescent()
		GUI = self.Game.GUI
		if GUI:
			curTurn = self.Game.turn
			for ID in range(1, 3):
				for card in self.hands[ID] + self.Game.minions[ID]:
					card.btn.setBoxColor(card.btn.decideColor() if ID == curTurn == GUI.ID else (1, 1, 1, 0))
				hero, power = self.Game.heroes[ID], self.Game.powers[ID]
				if hero.btn: hero.btn.setBoxColor(hero.btn.decideColor() if ID == curTurn == GUI.ID else (1, 1, 1, 0))
				if power.btn: power.btn.setBoxColor(power.btn.decideColor() if ID == curTurn == GUI.ID else (1, 1, 1, 0))
			
			if curTurn == GUI.ID and not self.Game.morePlaysPossible():
				if not GUI.btnTurnEnd.jobDone: GUI.btnTurnEnd.changeDisplay(jobDone=True)
			elif GUI.btnTurnEnd.jobDone: GUI.btnTurnEnd.changeDisplay(jobDone=False)
			
	# 双人游戏中一方很多控制自己的换牌，之后两个游戏中复制对方的手牌和牌库信息
	def mulligan1Side(self, ID, indices):
		GUI = self.Game.GUI
		cardstoReplace = []
		if indices:
			for num in range(1, len(indices) + 1):
				cardstoReplace.append(self.Game.mulligans[ID].pop(indices[-num]))
				self.Game.mulligans[ID].insert(indices[-num], self.decks[ID].pop())
		#self.hands[ID] = self.Game.mulligans[ID]
		self.decks[ID] += cardstoReplace
		npshuffle(self.decks[ID])

		addCoin = False
		#如果玩家操纵的是2号的话，则把硬币置入手牌中
		if ID == 2 and not self.Game.heroes[2].Class in SVClasses:
			self.Game.mulligans[2].append(TheCoin(self.Game, 2))
			addCoin = True
		if GUI:
			GUI.mulligan_NewCardsfromDeckAni(ID, addCoin)
			#调度得到的牌已经被 移入手牌Hand_Deck.hands里面，mulligans也被清空
		else: pass
		
	# 在双方给予了自己的手牌和牌库信息之后把它们注册同时触发游戏开始时的效果
	def finalizeHandDeck_StartGame(self):  # This ID is the opponent's ID
		for ID in range(1, 3):  # 直接拿着mulligans开始
			self.hands[ID] = [card.entersHand() for card in self.hands[ID]]
			for card in self.decks[ID]: card.entersDeck()
			self.Game.mulligans[ID] = []
		
		GUI = self.Game.GUI
		if GUI:
			GUI.seqHolder = [GUI.SEQUENCE(GUI.FUNC(GUI.deckZones[1].draw, len(self.decks[1]), len(self.hands[1])),
										  GUI.FUNC(GUI.deckZones[2].draw, len(self.decks[2]), len(self.hands[2])),
										  )]
			GUI.seqHolder[-1].append(GUI.PARALLEL(GUI.handZones[1].placeCards(False), GUI.handZones[2].placeCards(False))
									 )
			GUI.turnEndButtonAni_Flip2RightPitch()
			
		self.Game.Manas.calcMana_All()
		for ID in range(1, 3):
			for card in self.hands[ID] + self.decks[ID]:
				if "Start of Game" in card.index:
					GUI.seqHolder[-1].append(GUI.FUNC(GUI.showOffBoardTrig, card, "Appear"))
					card.startofGame()
		if GUI.ID == 1: GUI.turnStartAni()
		self.drawCard(1)
		self.decideCardColors()
		GUI.seqHolder.pop(0).start()
		
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
					if GUI: GUI.deckZones[ID].fatigueAni(damage)
					dmgTaker = game.scapegoat4(game.heroes[ID])
					dmgTaker.takesDamage(None, damage, damageType="Ability")  # 疲劳伤害没有来源
					return None, -1 #假设疲劳时返回的数值是负数，从而可以区分爆牌（爆牌时仍然返回那个牌的法力值）和疲劳
		else:
			if isinstance(card, (int, np.int32, np.int64)): card = self.decks[ID].pop(card)
			else: card = extractfrom(card, self.decks[ID])
			mana = card.mana
		card.leavesDeck()
		game.sendSignal("DeckCheck", ID, None, None, 0, "")
		if self.handNotFull(ID):
			#Draw a card at the deckZone and move it to the pausePos
			if GUI: GUI.drawCardAni_LeaveDeck(card)
			cardTracker = [card]  # 把这张卡放入一个列表，然后抽牌扳机可以对这个列表进行处理同时传递给其他抽牌扳机
			game.sendSignal("CardDrawn", ID, None, cardTracker, mana, "")
			self.Game.Counters.numCardsDrawnThisTurn[ID] += 1
			if cardTracker[0].type == "Spell" and "Casts When Drawn" in cardTracker[0].index:
				card2Cast = cardTracker[0]
				if GUI: GUI.seqHolder[-1].append(GUI.FUNC(card2Cast.btn.np.removeNode))
				card2Cast.whenEffective()
				game.sendSignal("SpellCastWhenDrawn", ID, None, card2Cast, mana, "")
				#抽到之后施放的法术如果检测到玩家处于濒死状态，则不会再抽一张。如果玩家有连续抽牌的过程，则执行下次抽牌
				if game.heroes[ID].health > 0 and not game.heroes[ID].dead:
					self.drawCard(ID)
				cardTracker[0].afterDrawingCard()
			else:  # 抽到的牌可以加入手牌。
				if cardTracker[0].type == "Minion" or cardTracker[0].type == "Amulet":
					cardTracker[0].whenDrawn()
				cardTracker[0] = cardTracker[0].entersHand()
				self.hands[ID].append(cardTracker[0])
				if GUI: GUI.drawCardAni_IntoHand(card, cardTracker[0])
				game.sendSignal("CardEntersHand", ID, None, cardTracker, mana, "byDrawing")
				game.Manas.calcMana_All()
			return cardTracker[0], mana
		else:
			if GUI: GUI.millCardAni(card)
			return None, mana #假设即使爆牌也可以得到要抽的那个牌的费用，用于神圣愤怒
			
	# def createCard(self, obj, ID, comment)
	# Will force the ID of the card to change. obj can be an empty list/tuple
	#Creator是这张/些牌的创建者，creator=None，则它们的creator继承原来的。
	#possi是这张/些牌的可能性，possi=()说明它们都是确定的牌
	def addCardtoHand(self, obj, ID, byDiscover=False, pos=-1, ani="fromCenter", creator=None):
		game, GUI = self.Game, self.Game.GUI
		if not isinstance(obj, (list, np.ndarray, tuple)):  # if the obj is not a list, turn it into a single-element list
			obj = [obj]
		for card in obj:
			if self.handNotFull(ID):
				if inspect.isclass(card): card = card(game, ID)
				card.ID = ID
				self.hands[ID].insert(pos + 100 * (pos < 0), card)
				if GUI:
					if ani == "fromCenter":
						if card.btn:
							GUI.seqHolder[-1].append(GUI.FUNC(print, "Starting animation of adding card to hand"))
							GUI.seqHolder[-1].append(GUI.handZones[card.ID].placeCards(add2Queue=False))
						else: GUI.putaNewCardinHandAni(card)
					elif ani == "Twinspell":
						if GUI: GUI.cardReplacedinHand_Refresh(card)
				#None will simply pass
				card = card.entersHand()
				#只有已经提前定义了instance的卡牌会使用creator is None的选项
				if creator: card.creator = creator
				game.sendSignal("CardEntersHand", ID, None, [card], 0, "")
				if byDiscover: game.sendSignal("PutinHandbyDiscover", ID, None, obj, 0, '')
			else:
				self.Game.Counters.shadows[ID] += 1
		game.Manas.calcMana_All()
		#if GUI:
		#	print("After adding card to hand:")
		#	GUI.checkCardsDisplays(checkHand=True)
			
	def replaceCardDrawn(self, targetHolder, newCard, creator=None):
		ID = targetHolder[0].ID
		isPrimaryGalakrond = targetHolder[0] == self.Game.Counters.primaryGalakronds[ID]
		newCard.creator = creator
		targetHolder[0] = newCard
		if isPrimaryGalakrond: self.Game.Counters.primaryGalakronds[ID] = newCard
		
	def replaceCardinHand(self, card, newCard, creator=None): #替换单张卡牌，用于在手牌中发生变形时
		ID = card.ID
		i = self.hands[ID].index(card)
		card.leavesHand()
		self.hands[ID].pop(i)
		self.addCardtoHand(newCard, ID, byDiscover=False, pos=i, ani="Twinspell", creator=creator)
		
	#目前只有牌库中的迦拉克隆升级时会调用，对方是可以知道的
	def replaceCardinDeck(self, card, newCard, creator=None):
		ID = card.ID
		try:
			i = self.decks[ID].index(card)
			card.leavesDeck()
			self.decks[ID][i] = newCard
			newCard.creator = creator
			self.Game.sendSignal("DeckCheck", ID, None, None, 0, "")
		except: pass
		
	def replaceWholeDeck(self, ID, newCards, creator=None):
		self.extractfromDeck(0, ID, all=True)
		self.decks[ID] = newCards
		for card in newCards:
			card.entersDeck()
			card.creator = creator
		self.Game.sendSignal("DeckCheck", ID, None, None, 0, "")
		
	def replacePartofDeck(self, ID, indices, newCards, creator=None):
		for card in newCards: card.leavesDeck()
		deck = self.decks[ID]
		for i, oldCard, newCard in zip(indices, deck, newCards):
			oldCard.leavesDeck()
			deck[i] = newCard
			newCard.creator = creator
			newCard.entersDeck()
		self.Game.sendSignal("DeckCheck", ID, None, None, 0, "")
		
	# All the cards shuffled will be into the same deck. If necessary, invoke this function for each deck.
	# PlotTwist把手牌洗入牌库的时候，手牌中buff的随从两次被抽上来时buff没有了。
	# 假设洗入牌库这个动作会把一张牌初始化
	def shuffleintoDeck(self, obj, initiatorID=0, enemyCanSee=True, sendSig=True, creator=None):
		if obj:
			curGame = self.Game
			#如果obj不是一个Iterable，则将其变成一个列表
			if not isinstance(obj, (list, tuple, np.ndarray)):
				obj = [obj]
			ID = obj[0].ID
			if curGame.GUI: curGame.GUI.shuffleintoDeckAni(obj, enemyCanSee)
			self.decks[ID] += obj
			for card in obj:
				card.entersDeck()
				card.creator = creator
			npshuffle(self.decks[ID])
			if sendSig: curGame.sendSignal("CardShuffled", initiatorID, None, obj, 0, "")
			curGame.sendSignal("DeckCheck", ID, None, None, 0, "")
	
	#Given the index in hand. Can't shuffle multiple cards except for whole hand
	#ID here is the target deck ID, it can be initiated by cards from a different side 
	def shuffle_Hand2Deck(self, i, ID, initiatorID, all=True):
		if all:
			hand = self.extractfromHand(None, ID, all, enemyCanSee=False)[0]
			for card in hand:
				card.reset(ID, isKnown=False)
				self.shuffleintoDeck(card, initiatorID=initiatorID, enemyCanSee=False, sendSig=True, possi=card.possi)
		elif i:
			card = self.extractfromHand(i, ID, all, enemyCanSee=False)[0]
			card.reset(ID, isKnown=False)
			self.shuffleintoDeck(card, initiatorID=initiatorID, enemyCanSee=False, sendSig=True, possi=card.possi)
			
	def burialRite(self, ID, minions, noSignal=False):
		if not isinstance(minions, list):
			minions = [minions]
		for minion in minions:
			self.Game.summonfrom(minion, ID, -1, None, source='H')
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
			for card in cards:
				card.whenDiscarded()
				self.Game.Counters.cardsDiscardedThisGame[ID].append(card.index)
				self.Game.Counters.cardsDiscardedThisTurn[ID].append(card.index)
				self.Game.Counters.shadows[card.ID] += 1
				self.Game.sendSignal("CardDiscarded", card.ID, None, card, -1, "")
			self.Game.sendSignal("HandDiscarded", ID, None, None, len(cards), "")
			self.Game.Manas.calcMana_All()

	#card can be a list(for discarding multiple cards), or can be a single int or card entity
	def discard(self, ID, card, all=False):
		if all or isinstance(card, (list, tuple, np.ndarray)):
			if self.hands[ID]:
				if all: cards = self.extractfromHand(None, ID=ID, all=True, enemyCanSee=True, linger=True)[0]
				else: cards = [self.extractfromHand(i, ID=ID, enemyCanSee=True, linger=True)[0] for i in card]
				for card in cards:
					self.Game.sendSignal("CardDiscarded", card.ID, None, card, 1, "")
					card.whenDiscarded()
					self.Game.Counters.cardsDiscardedThisGame[ID].append(card.index)
					self.Game.Counters.cardsDiscardedThisTurn[ID].append(card.index)
					self.Game.Counters.shadows[card.ID] += 1
					self.Game.sendSignal("CardLeavesHand", card.ID, None, card, 0, "")
				self.Game.sendSignal("HandDiscarded", ID, None, None, len(cards), "")
				self.Game.Manas.calcMana_All()
		else:  # Discard a chosen card.
			i = card if isinstance(card, (int, np.int32, np.int64)) else self.hands[ID].index(card)
			card = self.hands[ID].pop(i)
			card.leavesHand()
			if self.Game.GUI: self.Game.GUI.cardsLeaveHandAni([card], enemyCanSee=True, linger=True)
			self.Game.sendSignal("CardDiscarded", card.ID, None, card, 1, "")
			card.whenDiscarded()
			self.Game.Counters.cardsDiscardedThisGame[ID].append(card.index)
			self.Game.Counters.cardsDiscardedThisTurn[ID].append(card.index)
			self.Game.Counters.shadows[card.ID] += 1
			self.Game.sendSignal("CardLeavesHand", card.ID, None, card, 0, "")
			self.Game.Manas.calcMana_All()
			
	# 只能全部拿出手牌中的所有牌或者拿出一个张，不能一次拿出多张指定的牌
	#丢弃手牌要用discardAll
	def extractfromHand(self, card, ID=0, all=False, enemyCanSee=False, linger=False, animate=True):
		if all:  # Extract the entire hand.
			cardsOut = self.hands[ID][:]
			if cardsOut:
				#一般全部取出手牌的时候都是直接洗入牌库，一般都不可见
				if animate and self.Game.GUI:
					self.Game.GUI.cardsLeaveHandAni(list(range(len(cardsOut))), ID=ID, enemyCanSee=True, linger=linger)
				self.hands[ID] = []
				for card in cardsOut:
					card.leavesHand()
					self.Game.sendSignal("CardLeavesHand", card.ID, None, card, 0, '')
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
			if animate and self.Game.GUI: self.Game.GUI.cardsLeaveHandAni([card], card.ID, enemyCanSee, linger=linger)
			self.Game.sendSignal("CardLeavesHand", card.ID, None, card, 0, '')
			return card, cost, posinHand

	# 只能全部拿牌库中的所有牌或者拿出一个张，不能一次拿出多张指定的牌
	def extractfromDeck(self, card, ID=0, all=False, enemyCanSee=True, animate=True):
		if all:  # For replacing the entire deck or throwing it away.
			cardsOut = self.decks[ID]
			self.decks[ID] = []
			for card in cardsOut: card.leavesDeck()
			self.cards_1Possi, self.cards_XPossi = [], []
			self.Game.sendSignal("DeckCheck", ID, None, None, 0, "")
			return cardsOut, 0, False
		else:
			if not isinstance(card, (int, np.int32, np.int64)):
				card = extractfrom(card, self.decks[card.ID])
			else:
				if not self.decks[ID]: return None, 0, False
				card = self.decks[ID].pop(card)
			card.leavesDeck()
			if animate and self.Game.GUI: self.Game.GUI.cardLeavesDeckAni(card, enemyCanSee=enemyCanSee)
			self.Game.sendSignal("DeckCheck", ID, None, None, 0, "")
			return card, 0, False
			
	#所有被移除的卡牌都会被展示
	def removeDeckTopCard(self, ID, num=1):
		cards = []
		for i in range(num):
			card = self.extractfromDeck(-1, ID)[0] #The cards removed from deck top can always be seen by opponent
			if card: cards.append(card)
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

Default1 = [LightningBolt, SightlessWatcher, Tracking, SelectiveBreeder, ThriveintheShadows,
			SphereofSapience, SphereofSapience, ApexisSmuggler, RiggedFaireGame, ShadowjewelerHanar,
			Marshspawn, OhMyYogg, PrimordialStudies, WandThief, JandiceBarov,
			InstructorFireheart, SilasDarkmoon, MysteryWinner, RinlingsRifle, GuesstheWeight, RingToss, SnackRun,
			#PalmReading, GrandEmpressShekzara, Guidance, ResizingPouch,
			#KeywardenIvory, VenomousScorpid, KazakusGolemShaper, SouthseaScoundrel,
			#PackKodo, WarsongWrangler, RuneOrb, Yoink, ClericofAnshe
			]

Default2 = [LightningBolt, SightlessWatcher, Tracking, SelectiveBreeder, ThriveintheShadows,
			SphereofSapience, ApexisSmuggler, RiggedFaireGame, Renew, ShadowjewelerHanar,
			
			]