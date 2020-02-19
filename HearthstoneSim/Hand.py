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
		self.initialDecks = {1: PaladinDeck, 2: DruidDeck}
		self.startingDeckIdentities = {1:[], 2:[]}
		self.startingHandIdentities = {1:[], 2:[]}
		self.initializeDecks()
		self.initializeHands()
		
	def initializeDecks(self):
		for ID in range(1, 3):
			for obj in self.initialDecks[ID]:
				card = obj(self.Game, ID)
				card.entersDeck()
				self.decks[ID].append(card)
				self.startingDeckIdentities[ID].append(card.identity)	
			np.random.shuffle(self.decks[ID])
			
	def initializeHands(self):
		for i in range(3):
			self.Game.mulligans[1].append(self.decks[1].pop())
			
		for i in range(4):
			self.Game.mulligans[2].append(self.decks[2].pop())
			
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
				for card in self.hands[ID]:
					card = card.entersHand()
				self.hands[ID] = self.Game.mulligans[ID]
				
				for i in range(len(indicesCards[ID])):
					self.drawCard(ID)
				self.decks[ID] += cardstoReplace
				np.random.shuffle(self.decks[ID]) #Shuffle the deck after mulligan
			else:
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
				return False
		return True
		
	def holdingDragon(self, ID, minion=None):
		if minion == None: #When card not in hand and wants to check if a Dragon is in hand
			for card in self.hands[ID]:
				if card.cardType == "Minion" and "Dragon" in card.race:
					return True
			return False
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
				if cardinHand.Class != Class:
					return True
			return False
		else:
			for cardinHand in self.hands[ID]:
				if cardinHand.Class != Class and cardinHand != card:
					return True
			return False
			
	#The card list can be empty
	#Damage taken due to running out of card will keep increasing. Refilling the deck won't reset the next damage you take.
	def drawCard(self, ID, card=None):
		#Drawing multiple cards will only be invoked if cards are confirmed to exist in deck.
		print(type(card))
		if type(card) == type([]) or type(card) == type(np.array([])):
			for obj in card:
				#Due to spells cast when drawn effects, a spell might draw the target card
				#meant for this function before it can reach it.
				obj = extractfrom(obj, self.decks[ID])
				if obj != None: #If the card is already drawn, nothing happens.
					mana = obj.mana
					obj.leavesDeck()
					if self.handNotFull(ID):
						self.Game.sendSignal("CardDrawn", ID, None, obj, mana, "")
						if obj.cardType == "Spell" and "Casts When Drawn" in obj.index:
							print(obj.name, " is drawn and cast.")
							obj.whenEffective()
							self.drawCard(ID)
							obj.afterDrawingCard()
						elif obj.cardType == "Minion" and "Triggers when Drawn" in obj.index:
							print(obj.name, " is drawn and triggers its effect.")
							for func in obj.triggers["Drawn"]:
								func()
						else:
							obj = obj.entersHand()
							self.hands[ID].append(obj)
							self.Game.sendSignal("CardEntersHand", ID, None, obj, 0, "")
			#For now, drawing multiple cards returns the same values as milling them.
			return (None, 0)
		else: #card is not a list but a single card.
			if card == None: #Draw from top of the deck.
				print("Hero %d draws from the top of the deck"%ID)
				if self.decks[ID] == []: #No cards left in deck.
					print("Hero%d's"%ID + "deck is empty, and he will take damage")
					self.noCards[ID] += 1 #如果在疲劳状态有卡洗入牌库，则疲劳值不会减少，在下次疲劳时，仍会从当前的非零疲劳值开始。
					self.Game.heroes[ID].dealsDamage(self.Game.heroes[ID], self.noCards[ID])
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
				self.Game.sendSignal("CardDrawn", ID, None, card, mana, "")
				if card.cardType == "Spell" and "Casts When Drawn" in card.index:
					print(card.name, " is drawn and cast.")
					card.whenEffective()
					self.drawCard(ID)
					card.afterDrawingCard()
				else: #抽到的牌可以加入手牌。
					if card.cardType == "Minion" and "Triggers when Drawn" in card.index:
						print(card.name, " is drawn and triggers its effect.")
						for func in card.triggers["Drawn"]:
							func()
					card = card.entersHand()
					self.hands[ID].append(card)
					self.Game.ManaHandler.calcMana_All()
					self.Game.sendSignal("CardEntersHand", ID, None, card, mana, "")
				return (card, mana)
			else:
				return (None, 0)
				
	#Will force the ID of the card to change.
	def addCardtoHand(self, obj, ID, comment="AddRealCard", index=-1):
		if type(obj) == type([]) or type(obj) == type(np.array([])):
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
					self.Game.sendSignal("CardEntersHand", ID, None, card, 0, comment)
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
				print(obj.name, " is put into player %d's hand."%ID)
				self.Game.sendSignal("CardEntersHand", ID, None, obj, 0, comment)					
			else:
				print("Player's hand is full. Can't add more cards.")
			
		self.Game.ManaHandler.calcMana_All()
		
	def replaceCardinHand(self, card, newCard):
		ID = card.ID
		for i in range(len(self.hands[ID])):
			if self.hands[ID][i] == card:
				card.leavesHand()
				self.Game.sendSignal("CardLeavesHand", ID, None, card, 0, "")
				self.addCardtoHand(newCard, ID, "AddRealCard", i)
				break
				#All the cards shuffled will be into the same deck. If necessary, invoke this function for each deck.
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
			
DruidDeck = [ElvenArcher,
			StonetuskBoar,
			RaidLeader,
			IronfurGrizzly,
			Innervate,
			Moonfire,
			Claw,
			HealingTouch,
			SavageRoar,
			WildGrowth,
			Swipe,
			Starfire,
			IronbarkProtector,
			IronbeakOwl,
			
			Wrath,
			PoweroftheWild,
			MarkofNature,
			KeeperoftheGrove,
			Nourish,
			Bite,
			Starfall,
			Starfall,
			ForceofNature,
			ForceofNature,
			SouloftheForest,
			AncientofLore,
			AncientofWar,
			DruidoftheClaw,
			DruidoftheClaw,
			MillhouseManastorm,
			MillhouseManastorm,
			FacelessManipulator,
			FacelessManipulator,
			FacelessManipulator,
			GiftoftheWild,
			Cenarius,
			Cenarius
			]
HunterDeck = [BarrensStablehand,
			BaronRivendare,
			Feugen,
			Stalagg,
			Loatheb,
			KelThuzad,
			Maexxna,
			Blingtron3000,
			HemetNesingwary,
			MimironsHead,
			Gazlowe,
			MogortheOgre,
			Toshley,
			TroggzortheEarthinator,
			FoeReaper4000,
			MekgineerThermaplugg,
			Gahzrilla,
			Malorne,
			DrBoom,
			FlameLeviathan,
			BolvarFordragon,
			
			ArcaneShot,
			TimberWolf,
			HuntersMark,
			AnimalCompanion,
			KillCommand,
			StarvingBuzzard,
			TundraRhino,
			TundraRhino,
			Tracking,
			Tracking,
			ExplosiveTrap,
			FreezingTrap,
			Misdirection,
			SnakeTrap,
			Snipe,
			Flare,
			EaglehornBow,
			UnleashtheHounds,
			ExplosiveShot,
			GladiatorsLongbow,
			KingCrush,
			ScavengingHyena,
			SavannahHighmane,
			BestialWrath,
			Houndmaster
			]
			
MageDeck = [AbusiveSergeant,
			SecretKeeper,
			AncientWatcher,
			LootHoarder,
			ManaAddict,
			NatPagle,
			PintsizedSummoner,
			PintsizedSummoner,
			YouthfulBrewmaster,
			LorewalkerCho,
			
			MirrorImage,
			MurlocTidehunter,
			Frostbolt,
			ArcaneMissiles,
			ArcaneExplosion,
			ArcaneIntellect,
			Fireball,
			WaterElemental,
			WaterElemental,
			Polymorph,
			Polymorph,
			FrostNova,
			GurubashiBerserker,
			ManaWyrm,
			SorcerersApprentice,
			Counterspell,
			IceBarrier,
			MirrorEntity,
			MirrorEntity,
			MirrorEntity,
			Spellbender,
			Vaporize,
			KirinTorMage,
			ConeofCold,
			EtherealArcanist,
			Blizzard,
			ArchmageAntonidas,
			Pyroblast
			]
			
PaladinDeck = [BlessingofMight,
			HandofProtection,
			Humility,
			LightsJustice,
			HolyLight,
			BlessingofKings,
			Consecration,
			HammerofWrath,
			TruesilverChampion,
			GuardianofKings,
			BlessingofWisdom,
			BlessingofWisdom,
			EyeforanEye,
			SacredSacrifice,
			ArgentProtector,
			Equality,
			ArdorPeacekeeper,
			BlessedChampion,
			Righteousness,
			AvengingWrath,
			TirionFordring,
			HolyWrath,
			SwordofJustice,
			SwordofJustice,
			LayonHands,
			Redemption,
			Redemption,
			Repentence,
			Skaterbot,
			Mecharoo,
			Mecharoo,
			FaithfulLumi,
			BronzeGatekeeper,
			Sn1pSn4p,
			MissileLauncher,
			SpiderBomb,
			AnnoyoModule,
			KangorsEndlessArmy,
			KangorsEndlessArmy
			]
PriestDeck = [YoungPriestess,
			BaronGeddon,
			WildPyromancer,
			FaerieDragon,
			Deathwing,
			EydisDarkbane,
			NexusChampionSaraad,
			ConfessorPaletress,
			TheMistcaller,
			Anubarak,
			VarianWrynn,
			SirFinleyMrrgglton,
			BrannBronzebeard,
			RenoJackson,
			Lucentbark,
			ArchThiefRafaam,
			
			MindVision,
			ShadowWordPain,
			NorthshireCleric,
			PowerWordShield,
			DivineSpirit,
			MindControl,
			
			CircleofHealing,
			Silence,
			InnerFire,
			Lightwell,
			Shadowform,
			Shadowform,
			Thoughtsteal,
			AuchenaiSoulpriest,
			Mindgames,
			ShadowMadness,
			Lightspawn,
			HolyFire,
			CabalShadowPriest,
			ProphetVelen
			]
			
RogueDeck = [BloodmageThalnos,
			BloodsailRaider,
			SouthseaDeckhand,
			DireWolfAlpha,
			FaerieDragon,
			IllidanStormrage,
			GadgetzanAuctioneer,
			VioletTeacher,
			Onyxia,
			SkycapnKragg,
			Icehowl,
			Aviana,
			Dreadscale,
			Acidmaw,
			Rhonin,
			
			Backstab,
			DeadlyPoison,
			SinisterStrike,
			Sap,
			Shiv,
			FanofKnives,
			Assassinate,
			AssassinsBlade,
			Sprint,
			
			Preparation,
			Shadowstep,
			Pilfer,
			Betrayal,
			ColdBlood,
			DefiasRingleader,
			Eviscerate,
			PatientAssassin,
			EdwinVancleef,
			Headcrack,
			SI7Agent,
			Plaguebringer,
			BladeFlurry,
			MasterofDisguise,
			Kidnapper
			]
			
ShamanDeck = [HarvestGolem,
			FaerieDragon,
			FacelessManipulator,
			QuestingAdventurer,
			TradePrinceGallywix,
			Neptulon,
			MalGanis,
			Voljin,
			IronJuggernaut,
			EmperorThaurissan,
			Chromaggus,
			MajordomoExecutus,
			Nefarian,
			
			CultMaster,
			DefenderofArgus,
			Abomination,
			HarrisonJones,
			StampedingKodo,
			FrostwolfWarlord,
			Hogger,
			TheBeast,
			BarrensStablehand,
			HighInquisitorWhitemane,
			Alexstrasza,
			ArcaneDevourer,
			Ysera,
			
			AncestralHealing,
			FlametongueTotem,
			FrostShock,
			RockbiterWeapon,
			Windfury,
			Hex,
			Windspeaker,
			Bloodlust,
			FireElemental,
			
			DustDevil,
			EarthShock,
			ForkedLightning,
			LightningBolt,
			AncestralSpirit,
			StormforgedAxe,
			FarSight,
			FeralSpirit,
			LavaBurst,
			LightningStorm,
			ManaTideTotem,
			UnboundElemental,
			Doomhammer,
			EarthElemental,
			AlAkirtheWindlord
			#HagathatheWitch,
			#Shudderwock,
			#Shudderwock,
			]
			
WarlockDeck = [MurlocTidehunter,
			MurlocTidecaller,
			MurlocWarleader,
			MadBomber,
			ManaWraith,
			PintsizedSummoner,
			FlesheatingGhoul,
			ImpMaster,
			TinkmasterOverspark,
			DefenderofArgus,
			Abomination,
			FacelessManipulator,
			HarrisonJones,
			
			CairneBloodhoof,
			Hogger,
			TheBeast,
			BarrensStablehand,
			BaronGeddon,
			HighInquisitorWhitemane,
			MountainGiant,
			SeaGiant,
			
			SacrificialPact,
			Corruption,
			MortalCoil,
			Corruption,
			Soulfire,
			Voidwalker,
			Felstalker,
			DrainLife,
			ShadowBolt,
			DreadInfernal,
			
			BloodImp,
			CalloftheVoid,
			FlameImp,
			Demonfire,
			SenseDemon,
			SummoningPortal,
			Felguard,
			VoidTerror,
			PitLord,
			Shadowflame,
			BaneofDoom,
			SiphonSoul,
			Siegebreaker,
			TwistingNether,
			LordJaraxxus
			]
			
WarriorDeck = [CrazedAlchemist,
				RagingWorgen,
				AmaniBerserker,
				BloodsailRaider,
				SouthseaDeckhand,
				SouthseaDeckhand,
				Spellbreaker,
				Spellbreaker,
				DreadCorsair,
				AcolyteofPain,
				DarkscaleHealer,
				CaptainGreenskin,
				LeeroyJenkins,
				ArgentCommander,
				SpitefulSmith,
				SpitefulSmith,
				
				Charge,
				Whirlwind,
				Cleave,
				Execute,
				HeroicStrike,
				FieryWarAxe,
				ShieldBlock,
				WarsongCommander,
				KorkronElite,
				ArcaniteReaper,
				
				InnerRage,
				ShieldSlam,
				Upgrade,
				Armorsmith,
				BattleRage,
				
				CommandingShout,
				BattleRage,
				BattleRage,
				CommandingShout,
				CruelTaskmaster,
				Rampage,
				Slam,
				FrothingBerserker,
				ArathiWeaponsmith,
				MortalStrike,
				Brawl,
				Gorehowl,
				GrommashHellscream
				]