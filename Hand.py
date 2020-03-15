from Basic import TheCoin
from CardIndices import *
import numpy as np

def extractfrom(target, listObject):
	temp = None
	for i in range(len(listObject)):
		if listObject[i] == target:
			temp = listObject.pop(i)
			break #Need this break, so that the iteration won't continue down the shortened list.
	return temp
	
def fixedList(listObject):
	return listObject[0:len(listObject)]
	
	
class Hand_Deck:
	def __init__(self, Game):
		self.Game = Game
		self.hands = {1:[], 2:[]}
		self.decks = {1:[], 2:[]}
		self.noCards = {1:0, 2:0}
		self.handUpperLimit = {1: 10, 2: 10}
		self.initialDecks = {1: WarriorDeck, 2: MageDeck}
		self.startingDeckIdentities = {1:[], 2:[]}
		self.startingHandIdentities = {1:[], 2:[]}
		self.initializeDecks()
		self.initializeHands()
		
	def initializeDecks(self):
		for ID in range(1, 3):
			Class = self.Game.heroes[ID].Class
			for obj in self.initialDecks[ID]:
				card = obj(self.Game, ID)
				if "Galakrond. " in card.name:
					#检测过程中，如果目前没有主迦拉克隆或者与之前检测到的迦拉克隆与玩家的职业不符合，则把检测到的迦拉克隆定为主迦拉克隆
					if self.Game.CounterHandler.primaryGalakronds[ID] == None:
						self.Game.CounterHandler.primaryGalakronds[ID] = card
					elif self.Game.CounterHandler.primaryGalakronds[ID].Class != Class and card.Class == Class:
						self.Game.CounterHandler.primaryGalakronds[ID] = card
				card.entersDeck()
				self.decks[ID].append(card)
				self.startingDeckIdentities[ID].append(card.identity)	
			np.random.shuffle(self.decks[ID])
			
	def initializeHands(self):
		#如果卡组有双传说任务，则起手时都会上手
		mainQuests = {1:[], 2:[]}
		mulliganSize = {1:3, 2:4}
		for ID in range(1, 3):
			for card in self.decks[ID]:
				if card.description.startswith("Quest: "):
					mainQuests[ID].append(card)
			numQueststoDraw = min(len(mainQuests[ID]), mulliganSize[ID])
			if numQueststoDraw > 0:
				queststoDraw = self.extractfromDeck(np.random.choice(mainQuests[ID], numQueststoDraw, replace=False))[0]
				for quest in queststoDraw:
					self.Game.mulligans[ID].append(quest)
			for i in range(mulliganSize[ID]-numQueststoDraw):
				self.Game.mulligans[ID].append(self.extractfromDeck(self.decks[ID][-1])[0])
				
	def mulligan(self, indicesCards1, indicesCards2):
		indicesCards = {1:indicesCards1, 2:indicesCards2}
		print("Player 1's cards to replace are", indicesCards[1], "Player 2's cards to replace are", indicesCards[2])
		for ID in range(1, 3):
			cardstoReplace = []
			#self.Game.mulligans is the cards currently in players' hands.
			if indicesCards[ID] != []:
				for num in range(1, len(indicesCards[ID])+1):
					cardstoReplace.append(self.Game.mulligans[ID].pop(indicesCards[ID][-num]))
				#调用手牌中没有被替代的卡的entersHand()
				for card in self.Game.mulligans[ID]:
					card = card.entersHand()
				self.hands[ID] = self.Game.mulligans[ID]
				
				for i in range(len(indicesCards[ID])):
					self.drawCard(ID)
				self.decks[ID] += cardstoReplace
				np.random.shuffle(self.decks[ID]) #Shuffle the deck after mulligan
			else: #No card replaced
				for card in self.Game.mulligans[ID]:
					card.leavesDeck()
					card = card.entersHand()
				self.hands[ID] = self.Game.mulligans[ID]
				
			#Record the starting hand identities.
			for card in self.hands[ID]:
				self.startingHandIdentities[ID].append(card.identity)
				
			print("Player's starting hand:", self.hands[ID])
			
		self.addCardtoHand(TheCoin(self.Game, 2), 2)
		self.Game.ManaHandler.calcMana_All()
		for ID in range(1, 3):
			for card in self.hands[ID] + self.decks[ID]:
				if "Start of Game" in card.index:
					card.startofGame()
					
	def handNotFull(self, ID):
		if len(self.hands[ID]) < self.handUpperLimit[ID]:
			return True
		return False
		
	def spaceinHand(self, ID):
		return self.handUpperLimit[ID] - len(self.hands[ID])
		
	def noDuplicatesinDeck(self, ID):
		record = []
		for card in self.decks[ID]:
			if type(card) not in record:
				record.append(type(card))
			else:
				print("The record is ", record)
				return False
		return True
		
	def holdingDragon(self, ID, minion=None):
		if minion == None: #When card not in hand and wants to check if a Dragon is in hand
			for card in self.hands[ID]:
				if card.cardType == "Minion" and "Dragon" in card.race:
					return True
		else: #When the minion is inHand and wants to know if it can trigger after being played.
			for card in self.hands[ID]:
				if card.cardType == "Minion" and "Dragon" in card.race and card != minion:
					return True
		return False
		
	def holdingSpellwith5CostorMore(self, ID):
		for card in self.hands[ID]:
			if card.cardType == "Spell" and card.mana >= 5:
				return True
		return False
		
	def holdingCardfromAnotherClass(self, ID, card=None):
		Class = self.Game.heroes[ID].Class
		if card == None:
			for cardinHand in self.hands[ID]:
				if Class not in cardinHand.Class and cardinHand.Class != "Neutral":
					return True
			return False
		else:
			for cardinHand in self.hands[ID]:
				if Class not in cardinHand.Class and cardinHand.Class != "Neutral" and cardinHand != card:
					return True
			return False
			
	#抽牌一次只能一张，需要废除一次抽多张牌的功能，因为这个功能都是用于抽效果指定的牌。但是这些牌中如果有抽到时触发的技能，可能会导致马上抽牌把列表后面的牌提前抽上来
	#现在规则为如果要连续抽2张法术，则分两次检测牌库中的法术牌，然后随机抽一张。
	#如果这个规则是正确的，则在牌库只有一张夺灵者哈卡的堕落之血时，抽到这个法术之后会立即额外抽牌，然后再塞进去两张堕落之血，那么第二次抽法术可能会抽到新洗进去的堕落之血。
	#Damage taken due to running out of card will keep increasing. Refilling the deck won't reset the damage you take next time you draw from empty deck
	def drawCard(self, ID, card=None):
		if card == None: #Draw from top of the deck.
			print("Hero %d draws from the top of the deck"%ID)
			if self.decks[ID] == []: #No cards left in deck.
				print("Hero%d's"%ID + "deck is empty and will take damage")
				self.noCards[ID] += 1 #如果在疲劳状态有卡洗入牌库，则疲劳值不会减少，在下次疲劳时，仍会从当前的非零疲劳值开始。
				damage = self.noCards[ID]
				objtoTakeDamage = self.Game.DamageHandler.damageTransfer(self.Game.heroes[ID])
				targetSurvival = objtoTakeDamage.damageRequest(None, damage)
				if targetSurvival > 0:
					damageActual, survival = objtoTakeDamage.takesDamage(None, damage) #疲劳伤害没有来源
				return (None, 0)
			else:
				card = self.decks[ID].pop()
				mana = card.mana
		else:
			print("Hero %d draws %s from the deck"%(ID, card.name))
			card = extractfrom(card, self.decks[ID])
			mana = card.mana
		card.leavesDeck()
		if self.handNotFull(ID):
			cardTracker = [card] #把这张卡放入一个列表，然后抽牌扳机可以对这个列表进行处理同时传递给其他抽牌扳机
			self.Game.sendSignal("CardDrawn", ID, None, cardTracker, mana, "")
			if cardTracker[0].cardType == "Spell" and "Casts When Drawn" in cardTracker[0].index:
				print(cardTracker[0].name, " is drawn and cast.")
				cardTracker[0].whenEffective()
				self.drawCard(ID)
				cardTracker[0].afterDrawingCard()
			else: #抽到的牌可以加入手牌。
				if cardTracker[0].cardType == "Minion" and "Triggers when Drawn" in cardTracker[0].index:
					print(cardTracker[0].name, " is drawn and triggers its effect.")
					for func in cardTracker[0].triggers["Drawn"]:
						func()
				cardTracker[0] = cardTracker[0].entersHand()
				self.hands[ID].append(cardTracker[0])
				self.Game.sendSignal("CardEntersHand", ID, None, cardTracker, mana, "")
				self.Game.ManaHandler.calcMana_All()
			return (cardTracker[0], mana)
		else:
			print("Player's hand is full. The drawn card %s is milled"%card.name)
			return (None, 0)
			
	#Will force the ID of the card to change.
	def addCardtoHand(self, obj, ID, comment="AddRealCard", index=-1):
		if type(obj) == type([]) or type(obj) == type(np.array([])): #Multiple cards at a time
			for card in obj:
				if self.handNotFull(ID):
					if comment == "CreateUsingIndex":
						card = self.Game.cardPool[card](self.Game, ID)
					elif comment == "CreateUsingType":
						card = card(self.Game, ID)
						
					card.ID = ID
					card = card.entersHand()
					#Add the card to hand.
					if index == -1:
						self.hands[ID].append(card)
					else:
						self.hands[ID].insert(index, card)
					print(card.name, " is put into player %d's hand."%ID)
					self.Game.sendSignal("CardEntersHand", ID, None, [card], 0, comment)
				else:
					print("Player's hand is full. Can't add more cards.")
					break
		else: #If the obj is a single card/index/type.
			if self.handNotFull(ID):
				if comment == "CreateUsingIndex":
					obj = self.Game.cardPool[obj](self.Game, ID)
				elif comment == "CreateUsingType":
					obj = obj(self.Game, ID)
				obj.ID = ID
				obj = obj.entersHand()
				#Add card into hand.
				if index == -1:
					self.hands[ID].append(obj)
				else:
					self.hands[ID].insert(index, obj)
				#Process the card's entersHand() method.
				print(obj.name, " is added into player %d's hand."%ID)
				self.Game.sendSignal("CardEntersHand", ID, None, [obj], 0, comment)					
			else:
				print("Player's hand is full. Can't add more cards.")
				
		self.Game.ManaHandler.calcMana_All()
		
	def replaceCardDrawn(self, targetHolder, newCard):
		ID = targetHolder[0].ID
		isPrimaryGalakrond = targetHolder[0] == self.Game.CounterHandler.primaryGalakronds[ID]
		targetHolder[0] = newCard
		if isPrimaryGalakrond:
			self.Game.CounterHandler.primaryGalakronds[ID] = newCard
			
	def replaceCardinHand(self, card, newCard):
		ID = card.ID
		for i in range(len(self.hands[ID])):
			if self.hands[ID][i] == card:
				card.leavesHand()
				self.hands[ID].pop(i)
				self.Game.sendSignal("CardLeavesHand", ID, None, card, 0, "")
				self.addCardtoHand(newCard, ID, "AddRealCard", i)
				break
				
	def replaceCardinDeck(self, card, newCard):
		ID = card.ID
		for i in range(len(self.decks[ID])):
			if self.decks[ID][i] == card:
				card.leavesDeck()
				self.decks[ID].pop(i)
				newCard.entersDeck()
				self.decks[ID].insert(i, newCard)
				break
				
	#All the cards shuffled will be into the same deck. If necessary, invoke this function for each deck.
	#PlotTwist把手牌洗入牌库的时候，手牌中buff的随从两次被抽上来时buff没有了。
	#假设洗入牌库这个动作会把一张牌初始化
	def shuffleCardintoDeck(self, obj, InitiatorID):
		if type(obj) == type([]) or type(obj) == type(np.array([])):
			ID = obj[0].ID
			for card in obj:
				self.decks[ID].append(card)
				card.entersDeck()
		else: #Shuffle a single card
			ID = obj.ID
			self.decks[ID].append(obj)
			obj.entersDeck()
			
		self.Game.sendSignal("CardShuffled", InitiatorID, None, obj, 0, "")
		np.random.shuffle(self.decks[ID])
		
	def discardCard(self, ID, card=None, discardAll=False):
		if discardAll: #Discard all hand.
			if self.hands[ID] != []:
				cards, cost, isRightmostCardinHand = self.extractfromHand(None, all=True, ID=ID)
				for card in cards:
					print("Card %s in player's hand is discarded:"%card.name)
					for func in card.triggers["Discarded"]:
						func()
					self.Game.CounterHandler.cardsDiscardedThisGame[ID].append(card.index)
					self.Game.sendSignal("PlayerDiscardsCard", card.ID, None, card, 0, "")					
				self.Game.ManaHandler.calcMana_All()
		else: #Discard a single card.
			if card == None: #Discard a random card.
				if self.hands[ID] != []:
					card = np.random.choice(self.hands[ID])
					card, cost, isRightmostCardinHand = self.extractfromHand(card)
					print("Card %s in player's hand is discarded:"%card.name)
					for func in card.triggers["Discarded"]:
						func()
					self.Game.ManaHandler.calcMana_All()
					self.Game.CounterHandler.cardsDiscardedThisGame[ID].append(card.index)
					self.Game.sendSignal("CardLeavesHand", card.ID, None, card, 0, "")
					self.Game.sendSignal("PlayerDiscardsCard", card.ID, None, card, 0, "")
			else: #Discard a chosen card.
				card, cost, isRightmostCardinHand = self.extractfromHand(card)
				print("Card %s in player's hand is discarded:"%card.name)
				for func in card.triggers["Discarded"]:
					func()
				self.Game.ManaHandler.calcMana_All()
				self.Game.CounterHandler.cardsDiscardedThisGame[ID].append(card.index)
				self.Game.sendSignal("CardLeavesHand", card.ID, None, card, 0, "")
				self.Game.sendSignal("PlayerDiscardsCard", card.ID, None, card, 0, "")					
				
	def extractfromHand(self, card, all=False, ID=0):
		if all: #Extract the entire hand.
			temp = self.hands[ID]
			self.hands[ID] = []
			for card in temp:
				card.leavesHand()
				self.Game.sendSignal("CardLeavesHand", card.ID, None, card, 0, '')
			return temp, 0, False
		else:
			if type(card) != type([]) and type(card) != type(np.array([])): #Extracting a single card from hand.
				#Need to keep track of the card's location in hand.
				for i in range(len(self.hands[card.ID])):
					if self.hands[card.ID][i] == card:
						index, cost = i, card.mana
						isRightmostCardinHand = True if i == len(self.hands[card.ID]) - 1 else False
						break
				card = self.hands[card.ID].pop(index)
				card.leavesHand()
				self.Game.sendSignal("CardLeavesHand", card.ID, None, card, 0, '')
				return card, cost, isRightmostCardinHand
			else: #Extracting multiple cards from hand.
				ID = card[0].ID #Will only invoke this function for one side. If necessary, invoke once for each hand.
				cards = []
				for obj in card:
					result = extractfrom(obj, self.hands[ID])
					if result != None:
						result.leavesHand()
						cards.append(result)
						self.Game.sendSignal("CardLeavesHand", card.ID, None, card, 0, '')
				return cards, 0, False
				
	def extractfromDeck(self, card, all=False, ID=0):
		if all: #For replacing the entire deck or throwing it away.
			temp = self.decks[ID]
			self.decks[ID] = []
			for card in temp:
				card.leavesDeck()
			return temp, 0, False
		else:
			if type(card) != type([]) and type(card) != type(np.array([])): #Extracting a single card from deck.
				card = extractfrom(card, self.decks[card.ID])
				card.leavesDeck()
				return card, 0, False
			else: #Extracting multiple cards from hand.
				ID = card[0].ID
				cards = []
				for obj in card:
					result = extractfrom(obj, self.decks[ID])
					result.leavesDeck()
					cards.append(result)
				return cards, 0, False
				
	def removeDeckTopCard(self, ID):
		if self.decks[ID] != []:
			card = self.decks[ID].pop(0)
			card.leavesDeck()
			print("The top card %s in player %d's deck is removed"%(card.name, ID))
			return card
		else:
			return None
			
DruidDeck = [Cenarius, PoweroftheWild, WardruidLoti, FlobbidinousFloop, UntappedPotential, YseraUnleashed, Swipe, Swipe, Starfall, Starfall, Nourish, Nourish, Innervate, Innervate, Wrath, Wrath, CrystalMerchant, CrystalMerchant, HiddenOasis, HiddenOasis, WorthyExpedition, WorthyExpedition, AnubisathDefender, AnubisathDefender, OasisSurger, OasisSurger, RisingWinds, RisingWinds, SteelBeetle, SteelBeetle, ]

HunterDeck = [LeeroyJenkins, CultMaster, BoommasterFlark, Zilliax, HalazzitheLynx, UnsealtheVault, BoneWraith, FacelessCorruptor, Veranus, SN1PSN4P, Tracking, Tracking, UnleashtheHounds, UnleashtheHounds, Springpaw, Springpaw, HenchClanHogsteed, HenchClanHogsteed, DesertSpear, DesertSpear, QuestingExplorer, QuestingExplorer, SwarmofLocusts, SwarmofLocusts, DivingGryphon, DivingGryphon, CleartheWay, CleartheWay, LicensedAdventurer, LicensedAdventurer, ]

MageDeck = [Doomsayer, Blizzard, ArcaneIntellect, Alexstrasza, FrostNova, MountainGiant, TwilightDrake, ArcaneKeysmith, BookofSpecters, StargazerLuna, LunasPocketGalaxy, Zilliax, FiretreeWitchdoctor, ConjurersCalling, RayofFrost, PowerofCreation, Kalecgos, KhartutDefender, ZephrystheGreat, TortollanPilgrim, RenotheRelicologist, BoneWraith, Siamat, ArcaneBreath, Dragoncaster, DragonqueenAlexstrasza, EscapedManasaber, TheAmazingReno, MalygosAspectofMagic, SN1PSN4P, ]

PaladinDeck = [LeeroyJenkins, BlessingofKings, Zilliax, SN1PSN4P, TruesilverChampion, TruesilverChampion, ReplicatingMenace, ReplicatingMenace, Mecharoo, Mecharoo, GlowTron, GlowTron, Galvanizer, Galvanizer, Crystology, Crystology, AnnoyoModule, AnnoyoModule, Wargear, Wargear, MicroMummy, MicroMummy, SkyClaw, SkyClaw, HotAirBalloon, HotAirBalloon, GoboglideTech, GoboglideTech, Shotbot, Shotbot, ]

PriestDeck = [WildPyromancer, Silence, AcolyteofPain, ExtraArms, TopsyTurvy, BwonsamditheDead, HighPriestAmet, DarkProphecy, InnerFire, InnerFire, PowerWordShield, PowerWordShield, InjuredBlademaster, InjuredBlademaster, DivineSpirit, DivineSpirit, CircleofHealing, CircleofHealing, NorthshireCleric, NorthshireCleric, Lightwarden, Lightwarden, Psychopomp, Psychopomp, InjuredTolvir, InjuredTolvir, BeamingSidekick, BeamingSidekick, NefersetRitualist, NefersetRitualist, ]

RogueDeck = [Backstab, EdwinVanCleef, Shadowstep, Sap, LeeroyJenkins, Eviscerate, SI7Agent, Zilliax, EVILMiscreant, HeistbaronTogwaggle, UnderbellyFence, Vendetta, ZephrystheGreat, BoneWraith, Siamat, PharaohCat, DragonsHoard, PraiseGalakrond, BloodsailFlybooter, FlikSkyshiv, ShieldofGalakrond, DevotedManiac, SealFate, FacelessCorruptor, DragonqueenAlexstrasza, KronxDragonhoof, EscapedManasaber, BoompistolBully, SN1PSN4P, GalakrondtheNightmare, ]

ShamanDeck = [EarthShock, EarthenMight, Shudderwock, ElectraStormsurge, HauntingVisions, Zentimo, KronxDragonhoof, GalakrondtheTempest, Hex, Hex, FarSight, FarSight, TotemicSmash, TotemicSmash, SpiritoftheFrog, SpiritoftheFrog, Mutate, Mutate, MoguFleshshaper, MoguFleshshaper, DragonsPack, DragonsPack, CorruptElementalist, CorruptElementalist, ShieldofGalakrond, ShieldofGalakrond, DevotedManiac, DevotedManiac, InvocationofFrost, InvocationofFrost, ]

WarlockDeck = [Alexstrasza, LordGodfrey, Zilliax, ZephrystheGreat, DragonqueenAlexstrasza, KronxDragonhoof, SN1PSN4P, GalakrondtheWretched, SacrificialPact, SacrificialPact, MortalCoil, MortalCoil, PlagueofFlames, PlagueofFlames, CrazedNetherwing, CrazedNetherwing, DragonblightCultist, DragonblightCultist, VeiledWorshipper, VeiledWorshipper, DarkSkies, DarkSkies, NetherBreath, NetherBreath, ShieldofGalakrond, ShieldofGalakrond, DevotedManiac, DevotedManiac, BadLuckAlbatross, BadLuckAlbatross, ]

WarriorDeck = [BattleRage, LeeroyJenkins, KronxDragonhoof, BombWrangler, SN1PSN4P, GalakrondtheUnbreakable, InnerRage, InnerRage, Armorsmith, Armorsmith, AcolyteofPain, AcolyteofPain, TownCrier, TownCrier, EterniumRover, EterniumRover, BloodswornMercenary, BloodswornMercenary, ScionofRuin, ScionofRuin, RitualChopper, RitualChopper, ShieldofGalakrond, ShieldofGalakrond, DevotedManiac, DevotedManiac, Awaken, Awaken, RiskySkipper, RiskySkipper, ]