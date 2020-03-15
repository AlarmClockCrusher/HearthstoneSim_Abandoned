from CardTypes import *
from Triggers_Auras import *
from VariousHandlers import *
from Basic import BasicTotems
import numpy as np

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
		return np.random.choice(["Druid", "Hunter", "Mage", "Paladin", "Priest", "Rogue", "Shaman", "Warlock", "Warrior"])
		
"""Mana 1 cards"""
class GurubashiChicken(Minion):
	Class, race, name = "Neutral", "Beast", "Gurubashi Chicken"
	mana, attack, health = 1, 1, 1
	index = "Rumble~Neutral~Minion~1~1~1~Beast~Gurubashi Chicken~Overkill"
	needTarget, keyWord, description = False, "", "Overkill: Gain +5 Attack"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_GurubashiChicken(self)]
		
class Trigger_GurubashiChicken(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionTookDamage", "HeroTookDamage"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and target.health < 0 and self.entity.ID == self.entity.Game.turn
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("Gurubashi Chicken overkills %s and gains +5 Attack."%target.name)
		self.entity.buffDebuff(5, 0)
		
		
class GurubashiOffering(Minion):
	Class, race, name = "Neutral", "", "Gurubashi Offering"
	mana, attack, health = 1, 0, 2
	index = "Rumble~Neutral~Minion~1~0~2~None~Gurubashi Offering"
	needTarget, keyWord, description = False, "", "At the start of your turn, destroy this and gain 8 Armor"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_GurubashiOffering(self)]
		
class Trigger_GurubashiOffering(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["TurnStarts"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("At the start of turn, Gurubashi Offering destroys itself and lets player gain 8 Armor.")
		self.entity.dead = True
		self.entity.Game.heroes[self.entity.ID].gainsArmor(8)
		
		
class HelplessHatchling(Minion):
	Class, race, name = "Neutral", "Beast", "Helpless Hatchling"
	mana, attack, health = 1, 1, 1
	index = "Rumble~Neutral~Minion~1~1~1~Beast~Helpless Hatchling~Deathrattle"
	needTarget, keyWord, description = False, "", "Deathrattle: Reduced the Cost of a random Beast in your hand"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [ReduceCostofRandomBeastinHandby1(self)]
		
class ReduceCostofRandomBeastinHandby1(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		beastsinHand = []
		for card in self.entity.Game.Hand_Deck.hands[self.entity.ID]:
			if "~Beast~" in card.index:
				beastsinHand.append(card)
				
		if beastsinHand != []:
			print("Deathrattle: Reduce the cost of a random Beast in your hand by (1) triggers")
			beast = np.random.choice(beastsinHand)
			ManaModification(beast, changeby=-1, changeto=-1).applies()
			self.entity.Game.ManaHandler.calcMana_Single(beast)
			
			
class SaroniteTaskmaster(Minion):
	Class, race, name = "Neutral", "", "Saronite Taskmaster"
	mana, attack, health = 1, 2, 3
	index = "Rumble~Neutral~Minion~1~2~3~None~Saronite Taskmaster~Deathrattle"
	needTarget, keyWord, description = False, "", "Deathrattle: Summon a 0/3 Free Agent with Taunt for your opponent"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [SummonaFreeAgentforOpponent(self)]
		
class SummonaFreeAgentforOpponent(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("Deathrattle: Summon a 0/3 Free Agent with Taunt for your opponent triggers")
		self.entity.Game.summonMinion(FreeAgent(self.entity.Game, 3-self.entity.ID), -1, self.entity.ID)
		
class FreeAgent(Minion):
	Class, race, name = "Neutral", "", "Free Agent"
	mana, attack, health = 1, 0, 3
	index = "Rumble~Neutral~Minion~1~0~3~None~Free Agent~Taunt~Uncollectible"
	needTarget, keyWord, description = False, "Taunt", "Taunt"
	
"""Mana 2 cards"""
class BelligerentGnome(Minion):
	Class, race, name = "Neutral", "", "Belligerent Gnome"
	mana, attack, health = 2, 1, 4
	index = "Rumble~Neutral~Minion~2~1~4~None~Belligerent Gnome~Taunt~Battlecry"
	needTarget, keyWord, description = False, "Taunt", "Taunt. Battlecry: If your opponent has 2 or more minions, gain +1 Attack"
	def effectCanTrigger(self):
		self.effectViable = len(self.Game.minionsonBoard(3-self.ID)) > 1
		
	def whenEffective(self, target=None, comment="", choice=0):
		if len(self.Game.minionsonBoard(3-self.ID)) > 1:
			print("Belligerent Gnome's battlecry gives minion +1 attack")
			self.buffDebuff(1, 0)
		return None
		
		
class BootyBayBookie(Minion):
	Class, race, name = "Neutral", "", "Booty Bay Bookie"
	mana, attack, health = 2, 3, 3
	index = "Rumble~Neutral~Minion~2~3~3~None~Booty Bay Bookie~Battlecry"
	needTarget, keyWord, description = False, "", "Battlecry: Give your opponent a coin"
	
	def whenEffective(self, target=None, comment="", choice=0):
		print("Booty Bay Bookie's battlecry gives opponent a Coin.")
		self.Game.Hand_Deck.addCardtoHand(Coin(self.Game, 3-self.ID), 3-self.ID)
		return None
		
		
class CheatyAnklebiter(Minion):
	Class, race, name = "Neutral", "", "Cheaty Anklebiter"
	mana, attack, health = 2, 2, 1
	index = "Rumble~Neutral~Minion~2~2~1~None~Cheaty Anklebiter~Lifesteal~Battlecry"
	needTarget, keyWord, description = True, "Lifesteal", "Lifesteal. Battlecry: Deal 1 damage"
	
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			print("Cheaty Anklebiter's battlecry deals 1 damage to ", target.name)
			self.dealsDamage(target, 1)
		return target
		
		
class DozingMarksman(Minion):
	Class, race, name = "Neutral", "", "Dozing Marksman"
	mana, attack, health = 2, 0, 4
	index = "Rumble~Neutral~Minion~2~0~4~None~Dozing Marksman"
	needTarget, keyWord, description = False, "", "Has +4 Attach while damage"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggers["StatChanges"] = [self.handleEnrage]
		
	def handleEnrage(self):
		if self.silenced == False and self.onBoard:
			if self.activated == False and self.health < self.health_upper:
				self.activated = True
				self.statChange(4, 0)
			elif self.activated and self.health >= self.health_upper:
				self.activated = False
				self.statChange(-4, 0)
				
				
class FiretreeWitchdoctor(Minion):
	Class, race, name = "Neutral", "", "Firetree Witchdoctor"
	mana, attack, health = 2, 2, 2
	index = "Rumble~Neutral~Minion~2~2~2~None~Firetree Witchdoctor~Battlecry"
	needTarget, keyWord, description = False, "", "Battlecry: If you're holding a Dragon, Discover a spell"
	poolIdentifier = "Spells as Druid"
	@classmethod
	def generatePool(cls, Game):
		classes, lists = [], []
		#职业为中立时，视为一个随机职业打出此牌
		for Class in ["Druid", "Mage", "Hunter", "Paladin", "Priest", "Rogue", "Shaman", "Warlock", "Warrior"]:
			classes.append("Spells as " + Class)
			spellsinClass = []
			for key, value in Game.ClassCards[Class].items():
				if "~Spell~" in key:
					spellsinClass.append(value)
			lists.append(spellsinClass)
			
		return classes, lists #返回的包含“Class Cards except Hunter”等identifier的列表和其他职业卡表
		
	def randomorDiscover(self):
		if self.Game.Hand_Deck.holdingDragon(self.ID):
			return "Discover"
		return "No RNG"
		
	def effectCanTrigger(self):
		self.effectViable = self.Game.Hand_Deck.holdingDragon(self.ID)
		
	def whenEffective(self, target=None, comment="", choice=0):
		if self.Game.Hand_Deck.holdingDragon(self.ID):		
			key = "Spells as "+classforDiscover(self)
			if comment == "InvokedbyOthers":
				print("Firetree Witchdoctor's battlecry adds a random spell to player's hand.")
				self.Game.Hand_Deck.addCardtoHand(np.random.choice(self.Game.RNGPools[key]), self.ID, "CreateUsingType")
			else:
				spells = np.random.choice(self.Game.RNGPools[key], 3, replace=False)
				self.Game.options = [spell(self.Game, self.ID) for spell in spells]
				self.Game.DiscoverHandler.startDiscover(self)
		return None
		
	def discoverDecided(self, option):
		print("Spell ", option.name, " is put into player's hand")
		self.Game.Hand_Deck.addCardtoHand(option, self.ID)
		self.Game.sendSignal("DiscoveredCardPutintoHand", self.ID, self, option, 0, "")
		
		
class ScarabEgg(Minion):
	Class, race, name = "Neutral", "", "Scarab Egg"
	mana, attack, health = 2, 0, 2
	index = "Rumble~Neutral~Minion~2~0~2~None~Scarab Egg~Deathrattle"
	needTarget, keyWord, description = False, "", "Deathrattle: Summon three 1/1 Scarabs"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [SummonThreeScarabs(self)]
		
class SummonThreeScarabs(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		pos = (self.entity.position, "totheRight") if self.entity in self.entity.Game.minions[self.entity.ID] else (-1, "totheRightEnd")
		print("Deathrattle: Summon three 1/1 Scarabs triggers")
		self.entity.Game.summonMinion([Scarab(self.entity.Game, self.entity.ID) for i in range(3)], pos, self.entity.ID)
		
class Scarab(Minion):
	Class, race, name = "Neutral", "Beast", "Scarab"
	mana, attack, health = 1, 1, 1
	index = "Rumble~Neutral~Minion~1~1~1~Beast~Scarab~Uncollectible"
	needTarget, keyWord, description = False, "", ""
	
	
class SerpentWard(Minion):
	Class, race, name = "Neutral", "Totem", "Serpent Ward"
	mana, attack, health = 2, 0, 3
	index = "Rumble~Neutral~Minion~2~0~3~Totem~Serpent Ward"
	needTarget, keyWord, description = False, "", "At the end of your turn, deal 2 damage to the enemy hero"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_SerpentWard(self)]
		
class Trigger_SerpentWard(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["TurnEnds"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("At the end of turn, %s deals 2 damage to the enemy hero"%self.entity.name)
		self.entity.dealsDamage(self.entity.Game.heroes[3-self.entity.ID], 2)
		
		
class SharkfinFan(Minion):
	Class, race, name = "Neutral", "Pirate", "Sharkfin Fan"
	mana, attack, health = 2, 2, 2
	index = "Rumble~Neutral~Minion~2~2~2~Pirate~Sharkfin Fan"
	needTarget, keyWord, description = False, "", "After your hero attacks, summon a 1/1 Pirate"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_SharkfinFan(self)]
		
class Trigger_SharkfinFan(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["HeroAttackedMinion", "HeroAttackedHero"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject.cardType == self.entity.Game.heroes[self.entity.ID]
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("After friendly hero attacks, %s summons a 1/1 Pirate."%self.entity.name)
		self.entity.Game.summonMinion(Swabbie(self.entity.Game, self.entity.ID), self.entity.position+1, self.entity.ID)
		
class Swabbie(Minion):
	Class, race, name = "Neutral", "Pirate", "Swabbie"
	mana, attack, health = 1, 1, 1
	index = "Rumble~Neutral~Minion~1~1~1~Pirate~Swabbie~Uncollectible"
	needTarget, keyWord, description = False, "", ""
	
	
class Shieldbreaker(Minion):
	Class, race, name = "Neutral", "", "Shieldbreaker"
	mana, attack, health = 2, 2, 1
	index = "Rumble~Neutral~Minion~2~2~1~None~Shieldbreaker~Battlecry"
	needTarget, keyWord, description = True, "", "Battlecry: Silence a minion with Taunt"
	def effectCanTrigger(self):
		self.effectViable = self.targetExists()
		
	def targetExists(self, choice=0):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and minion.keyWords["Taunt"] > 0 and target != self and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			print("Shieldbreaker's battlecry silences minion %s with Taunt."%target.name)
			target.getsSilenced()
		return target
		
		
class SoupVendor(Minion):
	Class, race, name = "Neutral", "", "Soup Vendor"
	mana, attack, health = 2, 1, 4
	index = "Rumble~Neutral~Minion~2~1~4~None~Soup Vendor"
	needTarget, keyWord, description = False, "", "Whenever you restore 3 or more Health to your hero, draw a card"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_SoupVendor(self)]
		
class Trigger_SoupVendor(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionGetsHealed", "HeroGetsHealed"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject.ID == self.entity.ID and number > 2
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("Player restores 3 or more Health, and %s lets player draw a card."%self.entity.name)
		self.entity.Game.Hand_Deck.drawCard(self.entity.ID)
		
		
class Spellzerker(Minion):
	Class, race, name = "Neutral", "", "Spellzerker"
	mana, attack, health = 2, 2, 3
	index = "Rumble~Neutral~Minion~2~2~3~None~Spellzerker"
	needTarget, keyWord, description = False, "", "Has Spell Damage +2 while damaged"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggers["StatChanges"] = [self.handleEnrage]
		
	def handleEnrage(self):
		if self.silenced == False and self.onBoard:
			if self.activated == False and self.health < self.health_upper:
				self.activated = True
				self.getsKeyword("Spell Damage")
				self.getsKeyword("Spell Damage")
			elif self.activated and self.health >= self.health_upper:
				self.activated = False
				self.losesKeyword("Spell Damage")
				self.losesKeyword("Spell Damage")
				
class Waterboy(Minion):
	Class, race, name = "Neutral", "", "Waterboy"
	mana, attack, health = 2, 2, 1
	index = "Rumble~Neutral~Minion~2~2~1~None~Waterboy~Battlecry"
	needTarget, keyWord, description = False, "", "Battlecry: You next Hero Power this turn costs (0)"
	
	def whenEffective(self, target=None, comment="", choice=0):
		print("Waterboy's battlecry player's next hero power this turn costs 0.")
		tempAura = YourNextHeroPowerThisTurnCosts0(self.Game, self.ID)
		self.Game.ManaHandler.PowerAuras.append(tempAura)
		tempAura.auraAppears()
		return None
		
class YourNextHeroPowerThisTurnCosts0(TempManaEffect_Power):
	def __init__(self, Game, ID):
		self.Game, self.ID = Game, ID
		self.changeby, self.changeto = 0, 0
		self.temporary = True
		
	def applicable(self, target):
		return target.ID == self.ID
		
"""Mana 3 cards"""
class BananaBuffoon(Minion):
	Class, race, name = "Neutral", "", "Banana Buffoon"
	mana, attack, health = 3, 2, 2
	index = "Rumble~Neutral~Minion~3~2~2~None~Banana Buffoon~Battlecry"
	needTarget, keyWord, description = False, "", "Battlecry: Add two Bananas to your hand"
	
	def whenEffective(self, target=None, comment="", choice=0):
		print("Banana Buffoon's battlecry adds two Bananas to player's hand")
		self.Game.Hand_Deck.addCardtoHand([Banana_Rumble, Banana_Rumble], self.ID, "CreateUsingType")
		return None
		
class Banana_Rumble(Spell):
	Class, name = "Neutral", "Banana"
	needTarget, mana = True, 1
	index = "Rumble~Neutral~Spell~1~Banana"
	description = "Give a minion +1/+1"
	
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			print("Banana is cast and gives minion %s +1/+1."%target.name)
			target.buffDebuff(1, 1)
		return target
		
		
class MaskedContender(Minion):
	Class, race, name = "Neutral", "", "Masked Contender"
	mana, attack, health = 3, 2, 4
	index = "Rumble~Neutral~Minion~3~2~4~None~Masked Contender~Battlecry"
	needTarget, keyWord, description = False, "", "Battlecry: If you control a Secret, cast a Secret from your deck"
	def effectViable(self):
		self.effectViable = self.Game.SecretHandler.secrets[self.ID] != []
		
	def whenEffective(self, target=None, comment="", choice=0):
		if self.Game.SecretHandler.secrets[self.ID] != []:
			print("Masked Contender's battlecry puts a secret from player's deck into battlefield.")
			self.Game.SecretHandler.deploySecretsfromDeck(self.ID, 1)
		return None
		
		
class DrakkariTrickster(Minion):
	Class, race, name = "Neutral", "", "Drakkari Trickster"
	mana, attack, health = 3, 3, 4
	index = "Rumble~Neutral~Minion~3~3~4~None~Drakkari Trickster~Battlecry"
	needTarget, keyWord, description = False, "", "Battlecry: Give each player a copy of a random card in the opponent's deck"
	
	def randomorDiscover(self):
		return "Random"
		
	def whenEffective(self, target=None, comment="", choice=0):
		print("Drakkari Trickster's battlecry gives each player a copy of random cards from each other's deck.")
		for ID in range(1, 3):
			if self.Game.Hand_Deck.decks[ID] != []:
				#不知道这个复制是否会保留buff等enchantment
				card = np.random.choice(self.Game.Hand_Deck.decks[ID])
				self.Game.Hand_Deck.addCardtoHand(type(card)(self.Game, 3-ID), 3-ID)
		return None
		
		
class OrneryTortoise(Minion):
	Class, race, name = "Neutral", "Beast", "Ornery Tortoise"
	mana, attack, health = 3, 3, 5
	index = "Rumble~Neutral~Minion~3~3~5~Beast~Ornery Tortoise~Battlecry"
	needTarget, keyWord, description = False, "", "Battlecry: Deal 5 damage to your hero"
	
	def whenEffective(self, target=None, comment="", choice=0):
		print("Ornery Tortoise's battlecry deals 5 damage to hero.")
		self.dealsDamage(self.Game.heroes[self.ID], 5)
		return None
		
		
class UntamedBeastmaster(Minion):
	Class, race, name = "Neutral", "", "Untamed BeastMaster"
	mana, attack, health = 3, 3, 4
	index = "Rumble~Neutral~Minion~3~3~4~None~Untamed Beastmaster"
	needTarget, keyWord, description = False, "", "Whenever you draw a Beast, give it +2/+2"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_UntamedBeastmaster(self)]
		
class Trigger_UntamedBeastmaster(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["CardDrawn"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and target[0].cardType == "Minion" and "Beast" in target[0].race and target[0].ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("Whenever player draws a Beast %s, %s gives it +2/+2."%(target.name, self.entity.name))
		target[0].buffDebuff(2, 2)
		
"""Mana 4 cards"""
class ArenaFanatic(Minion):
	Class, race, name = "Neutral", "", "Arena Fanatic"
	mana, attack, health = 4, 2, 3
	index = "Rumble~Neutral~Minion~4~2~3~None~Arena Fanatic~Battlecry"
	needTarget, keyWord, description = False, "", "Battlecry: Give all minions in your hand +1/+1"
	
	def whenEffective(self, target=None, comment="", choice=0):
		print("Arena Fanatic's battlecry gives all minions in player's hand +1/+1.")
		for card in self.Game.Hand_Deck.hands[self.ID]:
			if card.cardType == "Minion":
				card.buffDebuff(1, 1)
		return None
		
		
class ArenaTreasureChest(Minion):
	Class, race, name = "Neutral", "", "Arena Treasure Chest"
	mana, attack, health = 4, 0, 4
	index = "Rumble~Neutral~Minion~4~0~4~None~Arena Treasure Chest~Deathrattle"
	needTarget, keyWord, description = False, "", "Deathrattle: Draw 2 cards"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [DrawTwoCards(self)]
	
class DrawTwoCards(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("Deathrattle: Draw 2 cards triggers")
		self.entity.Game.Hand_Deck.drawCard(self.entity.ID)
		self.entity.Game.Hand_Deck.drawCard(self.entity.ID)
		
		
class Griftah(Minion):
	Class, race, name = "Neutral", "", "Griftah"
	mana, attack, health = 4, 4, 5
	index = "Rumble~Neutral~Minion~4~4~5~None~Griftah~Battlecry~Legendary"
	needTarget, keyWord, description = False, "", "Battlecry: Discover two cards. Give one to your opponent at random"
	poolIdentifier = "Cards as Druid"
	@classmethod
	def generatePool(cls, Game):
		classes, lists, neutralCards = [], [], list(Game.NeutralMinions.values())
		for Class in ["Druid", "Mage", "Hunter", "Paladin", "Priest", "Rogue", "Shaman", "Warlock", "Warrior"]:
			classes.append("Cards as "+Class)
			lists.append(list(Game.ClassCards[Class].values())+neutralCards)
		return classes, lists
		
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.discoverProgress = 0
		self.cardstoGive = []
		
	def randomorDiscover(self):
		return "Discover"
		
	def whenEffective(self, target=None, comment="", choice=0):
		key = "Cards as "+classforDiscover(self)
		self.cardstoGive = []
		if comment == "InvokedbyOthers":
			print("Griftah's battlecry gives each player a random card.")
			card1, card2 = np.random.choice(self.Game.RNGPools[key], 2, replace=True)
			self.Game.Hand_Deck.addCardtoHand(card1(self.Game, self.ID), self.ID)
			self.Game.Hand_Deck.addCardtoHand(card2(self.Game, 3-self.ID), 3-self.ID)
		else:
			for i in range(2):
				cards = np.random.choice(self.Game.RNGPools[key], 3, replace=False)
				self.Game.options = [card(self.Game, self.ID) for card in cards]
				self.Game.DiscoverHandler.startDiscover(self)
				
			order = np.random.randint(2)
			self.Game.Hand_Deck.addCardtoHand(self.cards.pop(0), order) #addCardtoHand会强制改变卡的ID
			self.Game.Hand_Deck.addCardtoHand(self.cards.pop(0), 3 - order)
			self.cards = []
		return None
		
	def discoverDecided(self, option):
		print("Card ", option.name, " is decided.")
		self.cards.append(option)
		#不知道这个发现所置入玩家手牌中的牌是否计为发现得到的牌。
		
		
class HalfTimeScavenger(Minion):
	Class, race, name = "Neutral", "", "Half-Time Scavenger"
	mana, attack, health = 4, 3, 5
	index = "Rumble~Neutral~Minion~4~3~5~None~Half-Time Scavenger~Stealth~Overkill"
	needTarget, keyWord, description = False, "Stealth", "Stealth. Overkill: Gain 3 Armor"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_HalfTimeScavenger(self)]
		
class Trigger_HalfTimeScavenger(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionTookDamage", "HeroTookDamage"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and target.health < 0 and self.entity.ID == self.entity.Game.turn
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("Half-Time Scavenger overkills %s and lets player gain 3 Armor."%target.name)
		self.entity.Game.heroes[self.entity.ID].gainsArmor(3)
		
		
class IceCreamPeddler(Minion):
	Class, race, name = "Neutral", "", "Ice Cream Peddler"
	mana, attack, health = 4, 3, 5
	index = "Rumble~Neutral~Minion~4~3~5~None~Ice Cream Peddler~Battlecry"
	needTarget, keyWord, description = False, "", "Battlecry: If you control a Frozen minion, gain 8 Armor"
	def effectCanTrigger(self):
		self.effectViable = False
		for minion in self.Game.minionsonBoard(self.ID):
			if minion.status["Frozen"] > 0:
				self.effectViable = True
				break
				
	def whenEffective(self, target=None, comment="", choice=0):
		controlFrozenMinion = False
		for minion in self.Game.minionsonBoard(self.ID):
			if minion.status["Frozen"] > 0:
				controlFrozenMinion = True
				break
				
		if controlFrozenMinion:
			print("Ice Cream Peddler's battlecry player gains +8 armor.")
			self.Game.heroes[self.ID].gainsArmor(8)
		return None
		
		
class MurlocTastyfin(Minion):
	Class, race, name = "Neutral", "Murloc", "Murloc Tastyfin"
	mana, attack, health = 4, 3, 2
	index = "Rumble~Neutral~Minion~4~3~2~Murloc~Murloc Tastyfin~Deathrattle"
	needTarget, keyWord, description = False, "", "Deathrattle: Draw 2 Murlocs from your deck"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [DrawTwoMurlocs(self)]
		
class DrawTwoMurlocs(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		murlocsinDeck = []
		for card in self.entity.Game.Hand_Deck.hands[self.entity.ID]:
			if card.cardType == "Minion" and "Murloc" in card.race:
				murlocsinDeck.append(card)
				
		if murlocsinDeck != []:
			print("Deathrattle: Draw 2 Murlocs from your deck triggers")
			self.entity.Game.Hand_Deck.drawCard(self.entity.ID, np.random.choice(murlocsinDeck, min(2, len(murlocsinDeck), replace=False)))
			
			
class RegeneratinThug(Minion):
	Class, race, name = "Neutral", "", "Regeneratin' Thug"
	mana, attack, health = 4, 3, 5
	index = "Rumble~Neutral~Minion~4~3~5~None~Regeneratin' Thug"
	needTarget, keyWord, description = False, "", "At the start of your turn, restore 2 Health to this minion"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_RegeneratinThug(self)]
		
class Trigger_RegeneratinThug(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["TurnStarts"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		heal = 2 * (2 ** self.entity.countHealDouble())
		print("At the start of turn, Regeneratin' Thug restores %d Health to itself")
		self.entity.restoresHealth(self.entity, heal)
		
		
class RumbletuskShaker(Minion):
	Class, race, name = "Neutral", "", "Rumbletusk Shaker"
	mana, attack, health = 4, 3, 2
	index = "Rumble~Neutral~Minion~4~3~2~None~Rumbletusk Shaker~Deathrattle"
	needTarget, keyWord, description = False, "", "Deathrattle: Summon a 3/2 Rumbletusk Breaker"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [SummonaRumbletuskBreaker(self)]
		
class SummonaRumbletuskBreaker(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("Deathrattle: Summon a 3/2 Rumbletusk Breaker")
		self.entity.Game.summonMinion(RumbletuskBreaker(self.entity.Game, self.entity.ID), self.entity.position+1, self.entity.ID)
		
class RumbletuskBreaker(Minion):
	Class, race, name = "Neutral", "", "Rumbletusk Breaker"
	mana, attack, health = 4, 3, 2
	index = "Rumble~Neutral~Minion~4~3~2~None~Rumbletusk Breaker~Uncollectible"
	needTarget, keyWord, description = False, "", ""
	
	
class TicketScalper(Minion):
	Class, race, name = "Neutral", "", "Ticket Scalper"
	mana, attack, health = 4, 5, 3
	index = "Rumble~Neutral~Minion~4~5~3~Pirate~Ticket Scalper~Overkill"
	needTarget, keyWord, description = False, "", "Overkill: Draw two cards"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_TicketScalper(self)]
		
class Trigger_TicketScalper(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionTookDamage", "HeroTookDamage"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and target.health < 0 and self.entity.ID == self.entity.Game.turn
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("Ticket Scalper overkills %s and lets player draw 2 cards."%target.name)
		self.entity.Game.Hand_Deck.drawCard(self.entity.ID)
		self.entity.Game.Hand_Deck.drawCard(self.entity.ID)
		
"""Mana 5 cards"""
class ArenaPatron(Minion):
	Class, race, name = "Neutral", "", "Arena Patron"
	mana, attack, health = 5, 3, 3
	index = "Rumble~Neutral~Minion~5~3~3~None~Arena Patron~Overkill"
	needTarget, keyWord, description = False, "", "Overkill: Summon another Arena Patron"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_ArenaPatron(self)]
		
class Trigger_ArenaPatron(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionTookDamage", "HeroTookDamage"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and target.health < 0 and self.entity.ID == self.entity.Game.turn
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("Arena Patron overkills %s and lets player draw 2 cards."%target.name)
		self.entity.Game.summonMinion(ArenaPatron(self.entity.Game, self.entity.ID), self.entity.position+1, self.entity.ID)
		
		
class DragonmawScorcher(Minion):
	Class, race, name = "Neutral", "Dragon", "Dragonmaw Scorcher"
	mana, attack, health = 5, 3, 6
	index = "Rumble~Neutral~Minion~5~3~6~Dragon~Dragonmaw Scorcher~Battlecry"
	needTarget, keyWord, description = False, "", "Battlecry: Deal 1 damage to all other minions"
	
	def whenEffective(self, target=None, comment="", choice=0):
		targets = self.Game.minionsonBoard(1) + self.Game.minionsonBoard(2)
		extractfrom(self, targets)
		print("Dragonmaw Scorcher's battlecry deals 1 damage to all other minions.")
		self.dealsAOE(targets, [1 for minion in targets])
		return None
		
		
class FormerChamp(Minion):
	Class, race, name = "Neutral", "", "Former Champ"
	mana, attack, health = 5, 1, 1
	index = "Rumble~Neutral~Minion~5~1~1~None~Former Champ~Battlecry"
	needTarget, keyWord, description = False, "", "Battlecry: Summon a 5/5 Hotshot"
	
	def whenEffective(self, target=None, comment="", choice=0):
		print("Former Champ's battlecry summons a 5/5 Hotshot.")
		self.Game.summonMinion(Hotshot(self.Game, self.ID), self.position+1, self.ID)
		return None
		
		
class MoshOggAnnouncer(Minion):
	Class, race, name = "Neutral", "", "Mosh'Ogg Announcer"
	mana, attack, health = 5, 6, 5
	index = "Rumble~Neutral~Minion~5~6~5~None~Mosh'Ogg Announcer"
	needTarget, keyWord, description = False, "", "Enemies attacking this have a 50% chance to attack someone else"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_MoshOggAnnouncer(self)]
		
class Trigger_MoshOggAnnouncer(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["HeroAttacksMinion", "MinionAttacksMinion",
								"BattleFinished"])
		self.triggeredDuringBattle = False
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		if self.entity.onBoard:
			if signal != "BattleFinished":
				#假设只会引导实际目标是自己的攻击,如果初始目标是自己但是已经被其他扳机偏离，则不会触发
				if target[1] == self.entity and subject.ID != self.entity.ID and self.triggeredDuringBattle == False:
					otherFriendlies = self.entity.Game.livingObjtoTakeRandomDamage(self.entity.ID)
					extractfrom(self.entity, otherFriendlies)
					if otherFriendlies != []:
						return True
			else: #Reset the label that only allows it to trigger once during a single battle
				return True
		return False
		
	def trigger(self, signal, ID, subject, target, number, comment, choice=0):
		if self.entity.onBoard:
			if signal == "BattleFinished": #Reset the Forgetful for next battle event.
				self.triggeredDuringBattle = False
			else:
				otherFriendlies = self.entity.Game.livingObjtoTakeRandomDamage(self.entity.ID)
				extractfrom(self.entity, otherFriendlies)
				if otherFriendlies != []:
					self.triggeredDuringBattle = True #玩家命令的一次攻击中只能有一次触发机会
					if np.random.randint(2) == 1:
						target[1] = np.random.choice(otherFriendlies)
						print("The target of attack is diverted by Mosh'Ogg Announce to another random friendly character ",target[1].name)
						
#Will the minion divert the AOE damage that kills itself as well?
class SnapjawShellfighter(Minion):
	Class, race, name = "Neutral", "", "Snapjaw Shellfighter"
	mana, attack, health = 5, 3, 8
	index = "Rumble~Neutral~Minion~5~3~8~None~Snapjaw Shellfighter"
	needTarget, keyWord, description = False, "", "Whenever an adjacent minion takes damage, this minion takes it instead"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.appearResponse = [self.activateAura]
		self.disappearResponse = [self.deactivateAura]
		self.silenceResponse = [self.deactivateAura]
		
	def activateAura(self):
		self.Game.DamageHandler.ShellfighterExists[self.ID] += 1
		print("Snapjaw Shellfighter appears and starts taking potential damage for adjacent friendly minions.")
		
	def deactivateAura(self):
		if self.Game.DamageHandler.ShellfighterExists[self.ID] > 0:
			print("Snapjaw Shellfighter no longer takes potential damage for adjacent friendly minions.")
			self.Game.DamageHandler.ShellfighterExists[self.ID] -= 1
			
			
class SightlessRanger(Minion):
	Class, race, name = "Neutral", "", "Sightless Ranger"
	mana, attack, health = 5, 3, 4
	index = "Rumble~Neutral~Minion~5~3~4~None~Sightless Ranger~Rush~Overkill"
	needTarget, keyWord, description = False, "Rush", "Rush. Overkill: Summon two 1/1 Bats"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_SightlessRanger(self)]
		
class Trigger_SightlessRanger(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionTookDamage", "HeroTookDamage"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and target.health < 0 and self.entity.ID == self.entity.Game.turn
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("Sightless Ranger overkills %s and summons two 1/1 Bats."%target.name)
		self.entity.Game.summonMinion([Bat_Rumble(self.entity.Game, self.entity.ID) for i in range(2)], (self.entity.position, "leftandRight"), self.entity.ID)
		
class Bat_Rumble(Minion):
	Class, race, name = "Neutral", "", "Bat"
	mana, attack, health = 1, 1, 1
	index = "Rumble~Neutral~Minion~1~1~1~Beast~Bat~Uncollectible"
	needTarget, keyWord, description = False, "", ""
	
"""Mana 6 cards"""
#After Mojomaster's battlecry, it's the empty mana crystals that will change.
class MojomasterZihi(Minion):
	Class, race, name = "Neutral", "", "Mojomaster Zihi"
	mana, attack, health = 6, 5, 5
	index = "Rumble~Neutral~Minion~6~5~5~None~Mojomaster Zihi~Battlecry~Legendary"
	needTarget, keyWord, description = False, "", "Battlecry: Set each player to 5 Mana Crystals"
	#不知道战吼是否会改变过载锁定的水晶
	def whenEffective(self, target=None, comment="", choice=0):
		print("Mojomaster Zihi's battlecry sets both players' mana crystals to 5.")
		self.Game.ManaHandler.manasUpper[1] = 5
		self.Game.ManaHandler.manasUpper[2] = 5
		self.Game.ManaHandler.manas[self.ID] = min(5, self.Game.ManaHandler.manas[self.ID])
		return None
		
"""Mana 7 cards"""
class AmaniWarBear(Minion):
	Class, race, name = "Neutral", "Beast", "Amani War Bear"
	mana, attack, health = 7, 5, 7
	index = "Rumble~Neutral~Minion~7~5~7~Beast~Amani War Bear~Rush~Taunt"
	needTarget, keyWord, description = False, "Rush,Taunt", "Rush, Taunt"
	
	
class CrowdRoaster(Minion):
	Class, race, name = "Neutral", "Dragon", "Crowd Roaster"
	mana, attack, health = 7, 7, 4
	index = "Rumble~Neutral~Minion~7~7~4~Dragon~Crowd Roaster~Battlecry"
	needTarget, keyWord, description = True, "", "Battlecry: If you're holding a Dragon, deal 7 damage to a minion"
	def effectCanTrigger(self):
		self.effectViable = self.Game.Hand_Deck.holdingDragon(self.ID, self) and self.Game.targetExists()
		
	def returnTrue(self, choice=0):
		return self.Game.Hand_Deck.holdingDragon(self.ID, self)
		
	def targetExists(self, choice=0):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target != self and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None and self.Game.Hand_Deck.holdingDragon(self.ID, self):
			print("Crowd Roaster's battlecry deals 7 damage to minion ", target.name)
			self.dealsDamage(target, 7)
		return target
		
		
class Linecracker(Minion):
	Class, race, name = "Neutral", "", "Linecracker"
	mana, attack, health = 7, 5, 10
	index = "Rumble~Neutral~Minion~7~5~10~None~Linecracker~Overkill"
	needTarget, keyWord, description = False, "", "Overkill: Double this minion's Attack"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_Linecracker(self)]
		
class Trigger_Linecracker(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionTookDamage", "HeroTookDamage"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and target.health < 0 and self.entity.ID == self.entity.Game.turn
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("Linecracker overkills %s and doubles its attack."%target.name)
		self.entity.statReset(self.entity.attack*2, False)
		
"""Mana 8 cards"""
class DaUndatakah(Minion):
	Class, race, name = "Neutral", "", "Da Undatakah"
	mana, attack, health = 8, 8, 5
	index = "Rumble~Neutral~Minion~8~8~5~None~Da Undatakah~Battlecry~Legendary"
	needTarget, keyWord, description = False, "", "Battlecry: Gain the Deathrattle effects of 3 friendly minions that died this game"
	
	def whenEffective(self, target=None, comment="", choice=0):
		print("Da Undatakah's battlecry lets the minion gain the Deathrattle effects of three friendly minions that died this game.")
		deathrattleMinions = []
		for index in self.Game.CounterHandler.minionsDiedThisGame[self.ID]:
			if "~Minion~" in index and "~Deathrattle" in index:
				deathrattleMinions.append(index)
				
		if deathrattleMinions != []:
			indices = np.random.choice(deathrattleMinions, min(3, len(deathrattleMinions)), replace=False)
			for index in indices:
				minion = self.Game.cardPool[index](self.Game, self.ID)
				print("Da Undatakah's battlecry gives minion %s's Deathrattle"%minion.name)
				for trigger in minion.deathrattles:
					self.deathrattles.append(type(trigger)(self))
					if self.onBoard:
						trigger.connect()
		return None
		
"""Mana 9 cards"""
class Oondasta(Minion):
	Class, race, name = "Neutral", "Beast", "Oondasta"
	mana, attack, health = 9, 7, 7
	index = "Rumble~Neutral~Minion~9~7~7~Beast~Oondasta~Rush~Overkill~Legendary"
	needTarget, keyWord, description = False, "Rush", "Rush. Overkill: Summon a Beast from your hand"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_Oondasta(self)]
		
class Trigger_Oondasta(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionTookDamage", "HeroTookDamage"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and target.health < 0 and self.entity.ID == self.entity.Game.turn
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		if self.entity.Game.spaceonBoard(self.entity.ID) > 0:
			print("Oondasta overkills %s and summons a Beast from player's hand."%target.name)
			beastsinHand = []
			for card in self.entity.Game.Hand_Deck.hands[self.entity.ID]:
				if card.cardType == "Minion" and "Beast" in card.race:
					beastsinHand.append(card)
			if beastsinHand != []:
				self.entity.Game.summonMinion(np.random.choice(beastsinHand), self.entity.position+1, self.entity.ID)
				
"""Mana 10 cards"""
class HakkartheSoulflayer(Minion):
	Class, race, name = "Neutral", "", "Hakkar. the Soulflayer"
	mana, attack, health = 10, 9, 6
	index = "Rumble~Neutral~Minion~10~9~6~None~Hakkar. the Soulflayer~Deathrattle_Legendary"
	needTarget, keyWord, description = False, "", "Deathrattle: Shuffle a Corrupted Blood into each player's deck"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [ShuffleCorruptedBlood(self)]
		
class ShuffleCorruptedBlood(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("Deathrattle: Shuffle a Corrupted Blood into each player's deck triggers")
		self.entity.Game.Hand_Deck.shuffleCardintoDeck(CorruptedBlood(self.entity.Game, self.entity.ID), self.entity.ID)
		self.entity.Game.Hand_Deck.shuffleCardintoDeck(CorruptedBlood(self.entity.Game, 3-self.entity.ID), 3-self.entity.ID)
		
class CorruptedBlood(Spell):
	Class, name = "Neutral", "Corrupted Blood"
	needTarget, mana = False, 1
	index = 	description = "Casts When Drawn. Take 3 damage. After you draw, shuffle two copies of this into your deck"
	
	def whenEffective(self, target=None, comment="", choice=0):
		#Corrupted Blood doesn't get boosted by Spell Damage	
		print("Corrupted Blood is cast and deals 3 damage to player. After drawing card, it will shuffle two copies of itself into player's deck.")
		self.dealsDamage(self.Game.heroes[self.ID], 3)
		return None
		
	#Hand_Deck.drawCard方法中应该先抽牌，然后调用抽牌后的本牌的函数
	def afterDrawingCard(self):
		print("Corrupted Blood shuffled two copies of itself into player's deck after drawing a card")
		self.Game.Hand_Deck.shuffleCardintoDeck(CorruptedBlood(self.Game, self.ID), self.ID)
		self.Game.Hand_Deck.shuffleCardintoDeck(CorruptedBlood(self.Game, self.ID), self.ID)
		
"""Druid cards"""
class Pounce(Spell):
	Class, name = "Druid", "Pounce"
	needTarget, mana = False, 0
	index = "Rumble~Druid~Spell~0~Pounce"
	description = "Give your hero +2 Attack this turn"
	
	def whenEffective(self, target=None, comment="", choice=0):
		print("Pounce is cast and gives player +2 attack this turn.")
		self.Game.heroes[self.ID].gainTempAttack(2)
		return None
		
#The triggering is before the death resolution of minions.
class SpiritoftheRaptor(Minion):
	Class, race, name = "Druid", "", "Spirit of the Raptor"
	mana, attack, health = 1, 0 ,3
	index = "Rumble~Druid~Minion~1~0~3~None~Spirit of the Raptor"
	needTarget, keyWord, description = False, "", "Stealth for 1 turn. After your hero attacks and kills a minion, draw a card"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.marks["Temp Stealth"] = 1
		self.triggersonBoard = [Trigger_SpiritoftheRaptor(self)]
		
class Trigger_SpiritoftheRaptor(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["HeroAttackedMinion"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject == self.entity.Game.heroes[self.entity.ID] and (target.health < 1 or target.dead == True)
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("After friendly hero attacks and kills minion %s, %s lets player draw a card"%(target.name, self.entity.name))
		self.entity.Game.Hand_Deck.drawCard(self.entity.ID)
		
		
class SavageStriker(Minion):
	Class, race, name = "Druid", "", "Savage Striker"
	mana, attack, health = 2, 2, 3
	index = "Rumble~Druid~Minion~2~2~3~None~Savage Striker~Battlecry"
	needTarget, keyWord, description = True, "", "Battlecry: Deal damage to an enemy minion equal to your hero's Attack"
	def effectCanTrigger(self):
		self.effectViable = self.Game.heroes[self.ID].attack > 0
		
	def returnTrue(self, choice=0):
		return self.Game.heroes[self.ID].attack > 0
		
	def targetExists(self, choice=0):
		return self.Game.heroes[self.ID].attack > 0 and self.selectableEnemyMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.ID != self.ID and target != self and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			heroAttack = self.heroes[self.ID].attack
			if heroAttack > 0:
				print("Savage Striker's battlecry deals %d damage to enemy minion"%heroAttack, target.name)
				self.dealsDamage(target, heroAttack)
		return target
		
		
class WardruidLoti(Minion):
	Class, race, name = "Druid", "", "Wardruid Loti"
	mana, attack, health = 3, 1, 2
	index = "Rumble~Druid~Minion~3~1~2~None~Wardruid Loti~Choose One~Legendary"
	needTarget, keyWord, description = False, "", "Choose One- Transform into one of Loti's four dinosaur froms"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.chooseOne = 1
		self.options = [Ankylodon_Option(), Pterrordax_Option(), Pterrordax_Option(), Sabertusk_Option()]
		
	def played(self, target=None, choice=0, mana=0, comment=""):
		self.statReset(self.attack_Enchant, self.health_Enchant)
		self.appears()
		if choice == "ChooseBoth":
			minion = WardruidLoti_Ultimate(self.Game, self.ID)
		elif choice == 0:
			minion = WardruidLoti_Taunt(self.Game, self.ID)
		elif choice == 1:
			minion = WardruidLoti_SpellDamage(self.Game, self.ID)
		elif choice == 2:
			minion = WardruidLoti_PoisonousStealth(self.Game, self.ID)
		else:
			minion = WardruidLoti_Rush(self.Game, self.ID)
		#抉择变形类随从的入场后立刻变形。
		self.Game.transform(self, minion)
		#在此之后就要引用self.Game.minionPlayed
		self.Game.sendSignal("MinionPlayed", self.ID, self.Game.minionPlayed, None, mana, "", choice)
		self.Game.sendSignal("MinionSummoned", self.ID, self.Game.minionPlayed, None, mana, "")
		self.Game.gathertheDead()
		return None
		
class Ankylodon_Option:
	def __init__(self):
		self.needTarget = False
		self.name = "Ankylodon"
		self.description = "Taunt 1/6"
		
	def available(self):
		return True
		
	def selfCopy(self, recipient):
		return type(self)()
		
class Pterrordax_Option:
	def __init__(self):
		self.needTarget = False
		self.name = "Pterrordax"
		self.description = "Spell Damage +1 1/4"
		
	def available(self):
		return True
		
	def selfCopy(self, recipient):
		return type(self)()
		
class Ravasaur_Option:
	def __init__(self):
		self.needTarget = False
		self.name = "Ravasaur"
		self.description = "Poisonous, Steath 1/2"
		
	def available(self):
		return True
		
	def selfCopy(self, recipient):
		return type(self)()
		
class Sabertusk_Option:
	def __init__(self):
		self.needTarget = False
		self.name = "Sabertusk"
		self.description = "Rush 4/2"
		
	def available(self):
		return True
		
	def selfCopy(self, recipient):
		return type(self)()
		
class WardruidLoti_Taunt(Minion):
	Class, race, name = "Druid", "Beast", "Wardruid Loti"
	mana, attack, health = 3, 1, 6
	index = "Rumble~Druid~Minion~3~1~6~Beast~Wardruid Loti~Taunt~Legendary~Uncollectible"
	needTarget, keyWord, description = False, "Taunt", "Taunt"
	
class WardruidLoti_SpellDamage(Minion):
	Class, race, name = "Druid", "Beast", "Wardruid Loti"
	mana, attack, health = 3, 1, 4
	index = "Rumble~Druid~Minion~3~1~4~Beast~Wardruid Loti~Spell Damage~Legendary~Uncollectible" 
	needTarget, keyWord, description = False, "Spell Damage", "Spell Damage +1"
	
class WardruidLoti_PoisonousStealth(Minion):
	Class, race, name = "Druid", "Beast", "Wardruid Loti"
	mana, attack, health = 3, 1, 2
	index = "Rumble~Druid~Minion~3~1~2~Beast~Wardruid Loti~Stealth~Poisonous~Legendary~Uncollectible" 
	needTarget, keyWord, description = False, "Poisonous,Stealth", "Poisonous, Stealth"
	
class WardruidLoti_Rush(Minion):
	Class, race, name = "Druid", "Beast", "Wardruid Loti"
	mana, attack, health = 3, 4, 2
	index = "Rumble~Druid~Minion~3~4~2~Beast~Wardruid Loti~Rush~Legendary~Uncollectible" 
	needTarget, keyWord, description = False, "Rush", "Rush"
	
class WardruidLoti_Ultimate(Minion):
	Class, race, name = "Druid", "Beast", "Wardruid Loti"
	mana, attack, health = 3, 4, 6
	index = "Rumble~Druid~Minion~3~4~6~Beast~Wardruid Loti~Taunt~Rush~Poisonous~Stealth~Spell Damage~Legendary~Uncollectible" 
	needTarget, keyWord, description = False, "Taunt,Rush,Poisonous,Stealth,Spell Damage", "Taunt, Rush, Poisonous, Stealth, Spell Damage +1"
	
	
class MarkoftheLoa(Spell):
	Class, name = "Druid", "Mark of the Loa"
	needTarget, mana = True, 4
	index = "Rumble~Druid~Spell~4~Mark of the Loa~Choose One"
	description = "Choose One- Give a minion +2/+4 and Taunt; or Summon two 3/2 Raptors"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.chooseOne = 1
		self.options = [GonksResilience_Option(self), RaptorPack_Option(self)]
		
	def returnTrue(self, choice=0):
		return choice == "ChooseBoth" or choice == 0
		
	def available(self):
		#当场上有全选光环时，变成了一个指向性法术，必须要有一个目标可以施放。
		if self.Game.playerStatus[self.ID]["Choose Both"] > 0:
			return self.selectableMinionExists()
		else:
			return self.Game.spaceonBoard(self.ID) > 0 or self.selectableMinionExists()
			
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0):
		if choice == "ChooseBoth" or choice == 0:
			if target != None:
				print("Mark of the Loa gives minion %s +2/+4 and Taunt."%target.name)
				target.buffDebuff(2, 4)
				target.getsKeyword("Taunt")
		if choice == "ChooseBoth" or choice == 1:
			print("Mark of the Loa summon two 3/2 Raptors.")
			self.summonMinion([Raptor_Rumble(self.Game, self.ID) for i in range(2)], (-1, "totheRightEnd"), self.ID)
		return target
		
class GonksResilience_Option:
	def __init__(self, spell):
		self.spell = spell
		self.name = "Gonk's Resilience"
		self.description = "+2/+4, Taunt"
		self.index = "Rumble~Druid~4~Spell~Gonk's Resilience~Uncollectible"
		
	def available(self):
		return self.spell.selectableMinionExists()
		
	def selfCopy(self, recipient):
		return type(self)(recipient)
		
class RaptorPack_Option:
	def __init__(self, spell):
		self.spell = spell
		self.name = "Raptor Pack"
		self.description = "Two 3/2 Raptors"
		self.index = "Rumble~Druid~4~Spell~Raptor Pack~Uncollectible"
		
	def available(self):
		return self.spell.Game.spaceonBoard(self.spell.ID)
		
	def selfCopy(self, recipient):
		return type(self)(recipient)
		
class GonksResilience(Spell):
	Class, name = "Druid", "Gonk's Resilience"
	needTarget, mana = True, 4
	index = "Rumble~Druid~Spell~4~Gonk's Resilience~Uncollectible"
	description = "Give a minion +2/+4 and Taunt"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			print("Gonk's Resilience is cast and gives minion %s +2/+4 and Taunt."%target.name)
			target.buffDebuff(2, 4)
			target.getsKeyword("Taunt")
		return target
		
class RaptorPack(Spell):
	Class, name = "Druid", "Raptor Pack"
	needTarget, mana = False, 4
	index = "Rumble~Druid~Spell~4~Raptor Pack~Uncollectible"
	description = "Summon two 3/2 Raptors"
	def whenEffective(self, target=None, comment="", choice=0):
		print("Ratpor Pack is cast and summon two 3/2 Raptors.")
		self.summonMinion([Raptor_Rumble(self.Game, self.ID) for i in range(2)], (-1, "totheRightEnd"), self.ID)
		return None
		
		
class PredatoryInstincts(Spell):
	Class, name = "Druid", "Predatory Instincts"
	needTarget, mana = False, 4
	index = "Rumble~Druid~Spell~4~Predatory Instincts"
	description = "Draw a Beast from your deck. Double its Health"
	
	def whenEffective(self, target=None, comment="", choice=0):
		print("Predatory Instincts is cast. Player draws a Beast from deck and doubles its health.")
		beastsinDeck = []
		for card in self.Game.Hand_Deck.decks[self.ID]:
			if card.cardType == "Minion" and "Beast" in card.race:
				beastsinDeck.append(card)
				
		if beastsinDeck != []:
			beast = np.random.choice(beastsinDeck)
			beast.statReset(False, beast.health_upper * 2)
			self.Game.Hand_Deck.drawCard(self.ID, beast)
		return None
		
		
class Treespeaker(Minion):
	Class, race, name = "Druid", "", "Treespeaker"
	mana, attack, health = 5, 4, 4
	index = "Rumble~Druid~Minion~5~4~4~None~Treespeaker~Battlecry"
	needTarget, keyWord, description = False, "", "Battlecry: Transform your Treants into 5/5 Ancients"
	def effectCanTrigger(self):
		self.effectViable = False
		for minion in self.Game.minionsonBoard(self.ID):
			if minion.name == "Treant":
				self.effectViable = True
				break
				
	def whenEffective(self, target=None, comment="", choice=0):
		print("Treespeaker's battlecry transforms player's Treants into 5/5 Ancients.")
		for minion in fixedList(self.Game.minionsonBoard(self.ID)):
			if minion.name == "Treant":
				self.Game.transform(minion, Ancient(self.Game, self.ID))
		return None
		
		
class StampedingRoar(Spell):
	Class, name = "Druid", "Stampeding Roar"
	needTarget, mana = False, 6
	index = "Rumble~Druid~Spell~6~Stampeding Roar"
	description = "Summon a random Beast from your hand and give it Rush"
	
	def whenEffective(self, target=None, comment="", choice=0):
		print("Stampeding Roar is cast and summons a Beast from player's hand. It gains Rush.")
		beastsinHand = []
		for card in self.Game.Hand_Deck.hands[self.ID]:
			if card.cardType == "Minion" and "Beast" in card.race:
				beastsinHand.append(card)
				
		if beastsinDeck != [] and self.Game.spaceonBoard(self.ID) > 0:
			beast = np.random.choice(beastsinDeck)
			beast.getsKeyword("Rush")
			self.Game.summonfromHand(beast, -1, self.ID)
		return None
		
#Don't know if the attack chance gain will disappear or not after Gonk dies.
#Is Gonk's effect an aura or a listener.
class GonktheRaptor(Minion):
	Class, race, name = "Druid", "Beast", "Gonk. the Raptor"
	mana, attack, health = 7, 4, 9
	index = "Rumble~Druid~Minion~7~4~9~Beast~Gonk. the Raptor~Legendary"
	needTarget, keyWord, description = False, "", "After your hero attacks and kills a minion, it may attack again"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_GonktheRaptor(self)]
		
class Trigger_GonktheRaptor(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["HeroAttackedMinion"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject == self.entity.Game.heroes[self.entity.ID] and (target.health < 1 or target.dead == True)
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("After friendly hero attacks and kills minion %s, %s gives it another attack chance"%(target.name, self.entity.name))
		self.entity.Game.heroes[self.entity.ID].attChances_extra += 1
		
		
class IronhideDirehorn(Minion):
	Class, race, name = "Druid", "Beast", "Ironhide Direhorn"
	mana, attack, health = 7, 7, 7
	index = "Rumble~Druid~Minion~7~7~7~Beast~Ironhide Direhorn~Overkill"
	needTarget, keyWord, description = False, "", "Overkill: Summon a 5/5 Ironhide Runt"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_IronhideDirehorn(self)]
		
class Trigger_IronhideDirehorn(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionTookDamage", "HeroTookDamage"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and target.health < 0 and self.entity.ID == self.entity.Game.turn
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("Ironhide Direhorn overkills %s and summons 1 5/5 Ironhide Runt."%target.name)
		self.entity.Game.summonMinion(IronhideRunt(self.entity.Game, self.entity.ID), self.entity.position+1, self.entity.ID)
		
class IronhideRunt(Minion):
	Class, race, name = "Druid", "Beast", "Ironhide Runt"
	mana, attack, health = 5, 5, 5
	index = "Rumble~Druid~Minion~5~5~5~Beast~Ironhide Runt~Uncollectible"
	needTarget, keyWord, description = False, "", ""
	
"""Hunter cards"""
class Springpaw(Minion):
	Class, race, name = "Hunter", "Beast", "Springpaw"
	mana, attack, health = 1, 1, 1
	index = "Rumble~Hunter~Minion~1~1~1~Beast~Springpaw~Rush~Battlecry"
	needTarget, keyWord, description = False, "Rush", "Rush. Battlecry: Add a 1/1 Lynx with Rush to your hand"
	
	def whenEffective(self, target=None, comment="", choice=0):
		print("Springpaw's battlecry adds a 1/1 Lynx into player's hand.")
		self.Game.Hand_Deck.addCardtoHand(Lynx(self.Game, self.ID), self.ID)
		return None
		
class Lynx(Minion):
	Class, race, name = "Hunter", "Beast", "Lynx"
	mana, attack, health = 1, 1, 1
	index = "Rumble~Hunter~Minion~1~1~1~Beast~Lynx~Rush~Uncollectible"
	needTarget, keyWord, description = False, "Rush", "Rush"
	
	
class HeadhuntersHatchet(Weapon):
	Class, name, description = "Hunter", "Headhunter's Hatchet", "Battlecry: If you control a Beast, gain +1 Durability"
	mana, attack, durability = 2, 2, 2
	index = "Rumble~Hunter~Weapon~2~2~2~Headhunter's Hatchet~Battlecry"
	def effectCanTrigger(self):
		self.effectViable = False
		for minion in self.Game.minionsonBoard(self.ID):
			if "Beast" in minion.race:
				self.effectViable = True
				break
				
	def whenEffective(self, target=None, comment="", choice=0):
		controlBeast = False
		for minion in self.Game.minionsonBoard(self.ID):
			if "Beast" in minion.race:
				controlBeast = True
				break
		if controlBeast and self.cardType == "Weapon": #Can't be invoked by Shudderwock.
			print("Headhunter's Hatchet's battlecry effect and gains 1 durability since player controls a Beast.")
			self.gainStat(0, 1)
		return None
		
		
class RevengeoftheWild(Spell):
	Class, name = "Hunter", "Revenge of the Wild"
	needTarget, mana = False, 2
	index = "Rumble~Hunter~Spell~2~Revenge of the Wild"
	description = "Summon your Beasts that died this turn"
	def effectCanTrigger(self):
		friendlyBeastDiedThisTurn = []
		for index in self.Game.CounterHandler.minionsDiedThisTurn[self.ID]:
			if "~Beast~" in index:
				friendlyBeastDiedThisTurn.append(index)
		self.effectViable = friendlyBeastDiedThisTurn != [] and self.Game.spaceonBoard(self.ID) > 0
		
	def whenEffective(self, target=None, comment="", choice=0):
		print("Revenge of the Wild is cast and summons all friendly Beasts that died this turn.")
		friendlyBeastDiedThisTurn = []
		for index in self.Game.CounterHandler.minionsDiedThisTurn[self.ID]:
			if "~Beast~" in index:
				friendlyBeastDiedThisTurn.append(index)
				
		numSummon = min(self.Game.spaceonBoard(self.ID), len(friendlyBeastDiedThisTurn))
		if numSummon > 0:
			np.random.shuffle(friendlyBeastDiedThisTurn)
			minionstoSummon = np.random.choice(friendlyBeastDiedThisTurn, numSummon, replace=False)
			for index in minionstoSummon:
				self.Game.summonMinion(self.Game.cardPool[index](self.Game, self.ID), -1, self.ID)
		return None
		
		
class BaitedArrow(Spell):
	Class, name = "Hunter", "Baited Arrow"
	needTarget, mana = True, 5
	index = "Rumble~Hunter~Spell~5~Baited Arrow~Overkill"
	description = "Deal 3 damage. Overkill: Summon a 5/5 Devilsaur"
	
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			damage = (3 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			print("Baited Arrow is cast and deals %d damage to "%damage, target.name)
			objtoTakeDamage, targetSurvival = self.dealsDamage(target, damage)
			if objtoTakeDamage.health < 0:
				print("Baited Arrow overkills a minion and summons a 5/5 Devilsaur.")
				self.Game.summonMinion(Devilsaur(self.Game, self.ID), -1, self.ID)
		return target
		
		
class BloodscalpStrategist(Minion):
	Class, race, name = "Hunter", "", "Bloodscalp Strategist"
	mana, attack, health = 3, 2, 4
	index = "Rumble~Hunter~Minion~3~2~4~None~Bloodscalp Strategist~Battlecry"
	needTarget, keyWord, description = False, "", "Battlecry: If you have a weapon equipped, Discover a spell"
	poolIdentifier = "Hunter Spells"
	@classmethod
	def generatePool(cls, Game):
		classes, lists = [], []
		for Class in ["Druid", "Mage", "Hunter", "Paladin", "Priest", "Rogue", "Shaman", "Warlock", "Warrior"]:
			classes.append(Class+" Spells")
			spellsinClass = []
			for key, value in Game.ClassCards[Class].items():
				if "~Spell~" in key:
					spellsinClass.append(value)
			lists.append(spellsinClass)
		return classes, lists
		
	def effectCanTrigger(self):
		self.effectViable = self.Game.availableWeapon(self.ID) != None
		
	def whenEffective(self, target=None, comment="", choice=0):
		if self.Game.availableWeapon(self.ID) != None and self.Game.Hand_Deck.handNotFull(self.ID) and self.ID == self.Game.turn:
			key = classforDiscover(self) + " Spells"
			if comment == "InvokedbyOthers":
				print("Bloodscalp Strategist's battlecry adds a random spell into player's hand.")
				self.Game.Hand_Deck.addCardtoHand(np.random.choice(self.Game.RNGPools[key])(self.Game, self.ID), self.ID)
			else:
				spells = np.random.choice(self.Game.RNGPools[key], 3, replace=False)
				self.Game.options = [spell(self.Game, self.ID) for spell in spells]
				self.Game.DiscoverHandler.startDiscover(self)
		return None
		
	def discoverDecided(self, option):
		print("Spell ", option.name, " is put into player's hand.")
		self.Game.Hand_Deck.addCardtoHand(option, self.ID)
		self.Game.sendSignal("DiscoveredCardPutintoHand", self.ID, self, option, 0, "")
		
		
class SpiritoftheLynx(Minion):
	Class, race, name = "Hunter", "", "Spirit of the Lynx"
	mana, attack, health = 3, 0, 3
	index = "Rumble~Hunter~Minion~3~0~3~None~Spirit of the Lynx"
	needTarget, keyWord, description = False, "", "Stealth for 1 turn. Whenever you summon a Beast, give it +1/+1"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.marks["Temp Stealth"] = 1
		self.triggersonBoard = [Trigger_SpiritoftheLynx(self)]
		
class Trigger_SpiritoftheLynx(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionSummoned"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject.ID == self.entity.ID and "Beast" in subject.race
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("Friendly Beast %s is summoned and Spirit of the Lynx gives it +1/+1."%subject.name)
		subject.buffDebuff(1, 1)
		
		
class TheBeastWithin(Spell):
	Class, name = "Hunter", "The Beast Within"
	needTarget, mana = True, 1
	index = "Rumble~Hunter~Spell~1~The Beast Within"
	description = "Give a friendly Beast +1/+1, then it attacks a random enemy minion"
	
	def available(self):
		return self.selectableFriendlyMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and "Beast" in target.race and target.ID == self.ID and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			print("The Beast Within is cast and gives %s +1/+1. It then attacks a random enemy minion.")
			target.buffDebuff(1, 1)
			#假设目标被对方控制后，会攻击我方随从
			enemyMinions = self.Game.minionsonBoard(3-target.ID)
			if target.onBoard and enemyMinions != []:
				self.Game.battleRequest(target, np.random.choice(enemyMinions), verifySelectable=False, consumeAttackChance=False)
		return target
		
		
class MastersCall(Spell):
	Class, name = "Hunter", "Master's Call"
	needTarget, mana = False, 3
	index = "Rumble~Hunter~Spell~3~Master's Call"
	description = "Discover a minion in your deck. If all 3 are Beasts, draw them all"
	
	def whenEffective(self, target=None, comment="", choice=0):
		print("Master's Call is cast and lets player discover a minion and draw it from deck.")
		allMinionsinDeck = []
		minionIndices = []
		for card in self.Game.Hand_Deck.decks[self.ID]:
			if card.cardType == "Minion" and card.index not in minionIndices:
				allMinionsinDeck.append(card)
				minionIndices.append(card.index)
				
		numMinionsinDeck = len(allMinionsinDeck)
		num = min(3, numMinionsinDeck)
		if num > 1:
			minions = np.random.choice(allMinionsinDeck, num, replace=False)
			allAreBeasts = True
			for minion in minions:
				if "Beast" not in minion.race:
					allAreBeasts = False
					break
			if allAreBeasts:
				print("All minions are Beasts and Master's Call draws all of them.")
				self.Game.Hand_Deck.drawCard(self.ID, minions)
			else:
				if comment == "CastbyOthers":
					print("Master's Call is cast and randomly picks a minion to for player to draw from deck.")
					self.Game.Hand_Deck.drawCard(self.ID, np.random.choice(minions))
				else:
					print("Master's Call lets player start discovering a minion to draw from deck.")
					self.Game.options = minions
					self.Game.DiscoverHandler.startDiscover(self)
		elif num == 1:
			print("There is only one kind of minion left in deck. And it's drawn.")
			self.Game.Hand_Deck.drawCard(self.ID, minionsinDeck[0])
			
		return None
		
	def discoverDecided(self, option):
		print("Master's Call lets player draw discovered minion from deck.")
		self.Game.Hand_Deck.drawCard(self.ID, option)
		
		
class HalazzitheLynx(Minion):
	Class, race, name = "Hunter", "", "Halazzi. the Lynx"
	mana, attack, health = 5, 3, 2
	index = "Rumble~Hunter~Minion~5~3~2~Beast~Halazzi. the Lynx~Battlecry~Legendary"
	needTarget, keyWord, description = False, "", "Battlecry: Fill your hand with 1/1 Lynxes that have Rush"
	
	def whenEffective(self, target=None, comment="", choice=0):
		print("Halazzi. the Lynx's battlecry fills plyer's hand with 1/1 Lnyx with Rush.")
		while self.Game.Hand_Deck.handNotFull(self.ID):
			self.Game.Hand_Deck.addCardtoHand(Lynx, self.ID, "CreateUsingType")
		return None
		
		
class BerserkerThrow(HeroPower):
	name, needTarget = "Berserker Throw", True
	index = "Hunter~Hero Power~2~Berserker Throw"
	description = "Deal 2 damage"
	def effect(self, target, choice=0):
		damage = (2 + self.Game.playerStatus[self.ID]["Hero Power Damage Boost"]) * (2 ** self.countDamageDouble())
		print("Hero Power Berserker Throw deals %d damage to"%damage, target.name)
		objtoTakeDamage, targetSurvival = self.dealsDamage(target, damage)
		if targetSurvival > 1:
			return 1
		return 0
		
class Zuljin(Hero):
	mana, description = 10, "Battlecry: Cast all spells you've played this game (targets chosen randomly)"
	Class, name, heroPower, armor = "Hunter", "Zul'jin", BerserkerThrow, 5
	index = "Rumble~Hunter~Hero~10~Zul'jin~Battlecry~Legendary"
	def whenEffective(self, target=None, comment="", choice=0):
		spellsCastbyPlayer = []
		for index in self.Game.CounterHandler.cardsPlayedThisGame[self.ID]:
			if "~Spell~" in index:
				spellsCastbyPlayer.append(index)
		if spellsCastbyPlayer != []:
			print("Zul'jin's battlecry repeats the spells cast by player previously this Game.")
			np.random.shuffle(spellsCastbyPlayer)
			for index in spellsCastbyPlayer:
				spell = self.Game.cardPool[index](self.Game, self.ID)
				spell.cast(target=None, comment="CastbyOthers")
		return None
		
"""Mage cards"""
class ElementalEvocation(Spell):
	Class, name = "Mage", "Elemental Evocation"
	needTarget, mana = False, 0
	index = "Rumble~Mage~Spell~0~Elemental Evocation"
	description = "The next Elemental you play this turn costs (2) less"
	
	def whenEffective(self, target=None, comment="", choice=0):
		print("Preparation is cast and next spell this turn costs 2 less.")
		tempAura = YourNextElementalCosts2LessThisTurn(self.Game, self.ID)
		self.Game.ManaHandler.CardAuras.append(tempAura)
		tempAura.auraAppears()
		return None
		
class YourNextElementalCosts2LessThisTurn(TempManaEffect):
	def __init__(self, Game, ID):
		self.Game, self.ID = Game, ID
		self.changeby, self.changeto = -2, -1
		self.temporary = True
		self.auraAffected = []
		
	def applicable(self, subject):
		return subject.ID == self.ID and subject.cardType == "Minion" and "Elemental" in subject.race
		
		
class DaringFireEater(Minion):
	Class, race, name = "Mage", "", "Daring Fire-Eater"
	mana, attack, health = 1, 1, 1
	index = "Rumble~Mage~Minion~1~1~1~None~Daring Fire-Eater~Battlecry"
	needTarget, keyWord, description = False, "", "Battlecry: Your next Hero Power this turn deal 2 more damage"
	
	def whenEffective(self, target=None, comment="", choice=0):
		print("Daring Fire-Eater's battlecry twice and player's next Hero Power this turn deals 4 more damage.")
		self.Game.playerStatus[self.ID]["Hero Power Damage Boost"] += 2
		trigger = Trigger_DaringFireEater(self)
		trigger.ID = self.ID
		trigger.connect()
		return None
		
class Trigger_DaringFireEater(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["HeroUsedAbility"])
		self.ID = 1
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return subject.ID == self.ID
		
	def connect(self):
		for signal in self.signals:
			self.entity.Game.triggersonBoard[self.ID].append((self, signal))
		self.entity.Game.turnEndTrigger.append(self)
		
	def disconnect(self):
		for signal in self.signals:
			extractfrom((self, signal), self.entity.Game.triggersonBoard[self.ID])
		extractfrom(self, self.entity.Game.turnEndTrigger)
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("Player uses Hero Power %s and Daring Fire-Eater's Hero Power Damage Boost expires.")
		if self.entity.Game.playerStatus[self.ID]["Hero Power Damage Boost"] > 1:
			self.entity.Game.playerStatus[self.ID]["Hero Power Damage Boost"] -= 2
		self.disconnect()
		
	def turnEndTrigger(self):
		self.disconnect()
		
#The targeting Hero Power takes effect for adjacent minions even if the Power itself doesn't apply to the minion.
#恐龙学可以给相邻的非野兽随从非野兽随从+2/+2
class SpiritoftheDragonhawk(Minion):
	Class, race, name = "Mage", "", "Spirit of the Dragonhawk"
	mana, attack, health = 3, 0, 3
	index = "Rumble~Mage~Minion~2~0~3~None~Spirit of the Dragonhawk"
	needTarget, keyWord, description = False, "", "Stealth for 1 turn. Your Hero Power also targets adjacent minions"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.marks["Temp Stealth"] = 1
		self.appearResponse = [self.activateAura]
		self.disappearResponse = [self.deactivateAura]
		self.silenceResponse = [self.deactivateAura]
		
	def activateAura(self):
		print("Spirit of the Dragonhawk's aura is registered. Player %d's Hero Power also targets adjacent minions now."%self.minion.ID)
		self.Game.playerStatus[self.minion.ID]["Hero Power Targets Adjacent Minions"] += 1
		
	def deactivateAura(self):
		print("Spirit of the Dragonhawk's aura is removed. Player %d's Hero Power no longer targets adjacent minions."%self.minion.ID)
		if self.Game.playerStatus[self.minion.ID]["Hero Power Targets Adjacent Minions"] > 0:
			self.Game.playerStatus[self.minion.ID]["Hero Power Targets Adjacent Minions"] -= 1
			
#Figure out if pyromaniac triggers before the minion leaves board or after.
class Pyromaniac(Minion):
	Class, race, name = "Mage", "", "Pyromaniac"
	mana, attack, health = 3, 3, 4
	index = "Rumble~Mage~Minion~3~3~4~None~Pyromaniac"
	needTarget, keyWord, description = False, "", "Whenever your Hero Power kills a minion, draw a card"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_Pyromaniac(self)]
		
class Trigger_Pyromaniac(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["HeroPowerKilledMinion"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject.cardType == self.entity.Game.heroPowers[self.entity.ID]
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("When player's Hero Power kills minion, %s lets player draw a card."%self.entity.name)
		for i in range(number):
			self.entity.Game.Hand_Deck.drawCard(self.entity.ID)
			
			
class SplittingImage(Secret):
	Class, name = "Mage", "Splitting Image"
	needTarget, mana = False, 3
	index = "Rumble~Mage~Spell~3~Splitting Image~~Secret"
	description = "When one of your minions is attacked, summon a copy of it"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_SplittingImage(self)]
		
class Trigger_SplittingImage(SecretTrigger):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionAttacksMinion", "HeroAttacksMinion"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		#The target has to a friendly minion and there is space on board to summon minions.
		return self.entity.ID != self.entity.Game.turn and target[0].cardType == "Minion" and target[0].ID == self.entity.ID and self.entity.Game.spaceonBoard(self.entity.ID) > 0
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("When a friendly minion %s is attacked, Secret Splitting Image is triggered and summons a copy of it."%target.name)
		self.entity.Game.summonMinion(target[0].selfCopy(self.entity.ID), target[0].position+1, self.entity.ID)
		
#The resolution is: deal damage to targets, then collect all the targets that take the damage.
	#Check their survivals. Overkills is determined by targets that count as negative health.
	#If the multiple targets reference one single object and it has negative health, then overkill triggers multiple times.
class BlastWave(Spell):
	Class, name = "Mage", "Blast Wave"
	needTarget, mana = False, 5
	index = "Rumble~Mage~Spell~5~Blast Wave~Overkill"
	description = "Deal 2 damage to all minions. Overkill: Add a random Mage spell to your hand"
	poolIdentifier = "Mage Spells"
	@classmethod
	def generatePool(cls, Game):
		mageSpells = []
		for key, value in Game.ClassCards["Mage"].items():
			if "Spell" in key:
				mageSpells.append(value)
		return "Mage Spells", mageSpells
		
	def whenEffective(self, target=None, comment="", choice=0):
		damage = (2 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		print("Blast Wave is cast and deals %d damage to all minions."%damage)
		targets = self.Game.minionsonBoard(1) + self.Game.minionsonBoard(2)
		targets_damaged, damagesActual, targets_Healed, healsActual, totalDamageDone, totalHealingDone, damageSurvivals = self.dealsAOE(targets, [damage for minion in targets])
		overkills = 0
		for target in targets_damaged:
			if target.onBoard and target.health < 0:
				overkills += 1
		if overkills > 0:
			print("Blast Wave overkills %d minions and adds equal numbers of random Mage spells to player's hand"%overkills)		
			spells = np.random.choice(self.Game.RNGPools["Mage Spells"], overkills, replace=True)
			self.Game.Hand_Deck.addCardtoHand(spells, self.ID, "CreateUsingType")
		return None
		
		
class Scorch(Spell):
	Class, name = "Mage", "Scorch"
	needTarget, mana = True, 4
	index = "Rumble~Mage~Spell~4~Scorch"
	description = "Deal 4 damage to a minion. Costs (1) if you played an Elemental last turn"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_Scorch(self)]
		
	def selfManaChange(self):
		if self.inHand and self.Game.CounterHandler.numElementalsPlayedLastTurn[self.ID] > 0:
			self.mana = 1
			
	def effectCanTrigger(self):
		self.effectViable = self.Game.CounterHandler.numElementalsPlayedLastTurn[self.ID] > 0
		
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			damage = (4 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			print("Scorch is cast and deals %d damage to "%damage, target.name)
			self.dealsDamage(target, damage)
		return target
		
class Trigger_Scorch(TriggerinHand):
	def __init__(self, entity):
		self.blank_init(entity, ["TurnStarts", "TurnEnds"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.inHand
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("Player played an Elemental last turn, Scorch resets its Cost.")
		self.entity.Game.ManaHandler.calcMana_Single(self.entity)
		
		
class Arcanosaur(Minion):
	Class, race, name = "Mage", "Elemental", "Arcanosaur"
	mana, attack, health = 6, 3, 3
	index = "Rumble~Mage~Minion~6~3~3~Elemental~Arcanosaur~Battlecry"
	needTarget, keyWord, description = False, "", "Battlecry: If you played an Elemental last turn, deal 3 damage to all other minions"
	def effectCanTrigger(self):
		self.effectViable = self.Game.CounterHandler.numElementalsPlayedLastTurn[self.ID] > 0
		
	def whenEffective(self, target=None, comment="", choice=0):
		if self.Game.CounterHandler.numElementalsPlayedLastTurn[self.ID] > 0:
			targets = self.Game.minionsonBoard(1) + self.Game.minionsonBoard(2)
			extractfrom(self, targets)
			print("Arcanosaur's battlecry deals 3 damage to all other minions.")
			self.dealsDamage(targets, [3 for minion in targets])
		return None	
		
		
class JanalaitheDragonhawk(Minion):
	Class, race, name = "Mage", "Beast", "Jan'alai. the Dragonhawk"
	mana, attack, health = 7, 4, 4
	index = "Rumble~Mage~Minion~7~4~4~Beast~Jan'alai. the Dragonhawk~Battlecry~Legendary"
	needTarget, keyWord, description = False, "", "Battlecry: If your Hero Power dealt 8 damage this game, summon Ragnaros, the Firelord"
	def effectCanTrigger(self):
		self.effectViable = self.Game.damageDealtbyHeroPower[self.ID] > 7
		
	def whenEffective(self, target=None, comment="", choice=0):
		if self.Game.damageDealtbyHeroPower[self.ID] > 7:
			print("Jan'alai. the Dragonhawk's battlecry summons a Ragnaros the Firelord.")
			self.Game.summonMinion(RagnarostheFirelord_Rumble(self.Game, self.ID), self.position+1, self.ID)
		return None
		
class RagnarostheFirelord_Rumble(Minion):
	Class, race, name = "Neutral", "Elemental", "Ragnaros the Firelord"
	mana, attack, health = 8, 8, 8
	index = "Rumble~Neutral~Minion~8~8~8~Elemental~Ragnaros the Firelord~Uncollectible~Legendary"
	needTarget, keyWord, description = False, "", "Can't Attack. At the end of your turn, deal 8 damage to a random enemy"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.marks["Can't Attack"] = 1
		self.triggersonBoard = [Trigger_RagnarostheFirelord(self)]
		
class Trigger_RagnarostheFirelord(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["TurnEnds"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("At the end of turn, %s deals 8 damage to a random enemy"%self.entity.name)
		enemies = [self.entity.Game.heroes[3-self.entity.ID]] + self.entity.Game.minionsonBoard(3-self.entity.ID)
		self.entity.dealsDamage(np.random.choice(enemies), 8)
		
		
class HexLordMalacrass(Minion):
	Class, race, name = "Neutral", "", "Hex Lord Malacrass"
	mana, attack, health = 8, 5, 5
	index = "Rumble~Mage~Minion~8~5~5~None~Hex Lord Malacrass~Battlecry~Legendary"
	needTarget, keyWord, description = False, "", "Battlecry: Add a copy of your opening hand to your hand (except this card)"
	
	def whenEffective(self, target=None, comment="", choice=0):
		print("Hex Lord Malacrass's battlecry adds a copy of starting hand to player's hand.")
		self.Game.Hand_Deck.addCardtoHand(self.Game.Hand_Deck.startingHand[self.ID], self.ID, "CreateUsingIndex")
		return None
		
"""Paladin cards"""
class Bloodclaw(Weapon):
	Class, name, description = "Paladin", "Bloodclaw", "Battlecry: Deal 5 damage to your hero"
	mana, attack, durability = 1, 2, 2
	index = "Rumble~Paladin~Weapon~1~2~2~Bloodclaw~Battlecry"
	
	def whenEffective(self, target=None, comment="", choice=0):
		print("Bloodclaw's battlecry deals 5 damage to player.")
		self.dealsDamage(self.Game.heroes[self.ID], 5)
		return None
		
		
class FlashofLight(Spell):
	Class, name = "Paladin", "Flash of Light"
	needTarget, mana = True, 2
	index = "Rumble~Paladin~Spell~2~Flash of Light"
	description = "Restore 4 Health. Draw a card"
	
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			heal = 4 * (2 ** self.countHealDouble())
			print("Flash of Light is cast and restores %d health to %s. Player draws a card."%(health, target.name))
			self.restoresHealth(target, heal)
			self.Game.Hand_Deck.drawCard(self.ID)
		return target
		
#Will keep all stat setting effects/buffDebuffs, such as Humility or Sunkeeper Tarim.
#Deathrattles 
#Don't know if Temp Stealth will be kept.

#Won't keep Potion of Heroism(Give Divine Shield)

#Will keep enchantment from AOE buff/reset. (Never Surrender)
#Won't keep enchantments such as Corruption.
#Will keep enchantments such as Deathrattle: Return this minion to life with health 1.
#Give minion Divine Shield also counts as Enchantment as long as the minion still has it when dies.
#The Taunt given by On a Stegdon is preserved.
#Immune. Will temp Immune be kept?
class ImmortalPrelate(Minion):
	Class, race, name = "Paladin", "", "Immortal Prelate"
	mana, attack, health = 2, 1, 3
	index = "Rumble~Paladin~Minion~2~1~3~None~Immortal Prelate~Deathrattle"
	needTarget, keyWord, description = False, "", "Battlecry: Shuffle this into your deck. It keeps any enchantments"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [ShuffleintoDeckwithAnyEnchantment(self)]
		
class ShuffleintoDeckwithAnyEnchantment(Deathrattle_Weapon):
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		#如果随从已经被提前离场，则不能触发区域移动扳机。
		return target == self.entity.ID and self.entity in self.entity.Game.minions[self.entity.ID]
		
	def trigger(self, signal, ID, subject, target, number, comment, choice=0):
		print("Deathrattle: Shuffle this into your deck and keep any enchantment triggers")
		#Create the base minion that will be enchanted.
		baseMinion = type(self.entity)(self.entity.Game, self.entity.ID)
		#Reset the attack and health of the copy.
		baseMinion.statReset(self.entity.attack_Enchant, self.entity.health_Enchant)
		for key, value in self.entity.keyWords.items():
			if value > 0:
				baseMinion.keyWords[key] += value
		for key, value in self.entity.marks.items():
			if value > 0:
				baseMinion.marks[key] += value
		for trigger in self.entity.triggersonBoard:
			if trigger.temp == False:
				baseMinion.triggersonBoard.append(type(trigger)(baseMinion))
		baseMinion.deathrattles += [type(deathrattle)(baseMinion) for deathrattle in self.entity.deathrattles]
		print("A copy of %s with all enchantments will be shuffled in to player's deck.")
		baseMinion.statusPrint()
		#Shuffle the copy into player's deck
		self.entity.Game.Hand_Deck.shuffleCardintoDeck(baseMinion, self.entity.ID)
		
		
class HighPriestThekal(Minion):
	Class, race, name = "Paladin", "", "High Priest Thekal"
	mana, attack, health = 3, 3, 4
	index = "Rumble~Paladin~Minion~3~3~4~None~High Priest Thekal~Battlecry~Legendary"
	needTarget, keyWord, description = False, "", "Battlecry: Convert all but 1 of your Hero's Health into Armor"
	
	def whenEffective(self, target=None, comment="", choice=0):
		print("High Priest Thekal's battlecry converts all but 1 of player's health to armor.")
		numHealth = self.Game.heroes[self.ID].health - 1
		self.Game.heroes[self.ID].health = 1
		self.Game.heroes[self.ID].gainsArmor(numHealth)
		return None
		
		
class TimeOut(Spell):
	Class, name = "Paladin", "Time Out!"
	needTarget, mana = False, 3
	index = "Rumble~Paladin~Spell~3~Time Out!"
	description = "Your hero is Immune until your next turn"
	
	def whenEffective(self, target=None, comment="", choice=0):
		print("Time Out! is cast and player is Immune until the start of his next turn.")
		self.Game.playerStatus[self.ID]["Immune"] += 1
		self.Game.playerStatus[self.ID]["ImmuneTillYourNextTurn"] += 1
		return None
		
#Tigers with different stats count as same cards for Reno Jackson.
#Identical name and expansion pack will make cards to be treated as same.
#Uncollectible minions that might have issues for highlander cards: Imp, Treant, Tiger, 
#Combo with Cho'gall, you can cast spells costing more than 10. Need to dynamically create a subclass.
class SpiritoftheTiger(Minion):
	Class, race, name = "Paladin", "", "Spirit of the Tiger"
	mana, attack, health = 4, 0, 3
	index = "Rumble~Paladin~Minion~4~0~3~None~Spirit of the Tiger"
	needTarget, keyWord, description = False, "", "After your cast a spell, summon a Tiger with stats equal to its cost"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.marks["Temp Stealth"] = 1
		self.triggersonBoard = [Trigger_SpiritoftheTiger(self)]
		
class Trigger_SpiritoftheTiger(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["SpellBeenPlayed"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		#费用值为0的法术不会触发
		return self.entity.onBoard and subject.ID == self.entity.ID and number > 0 and self.entity.Game.spaceonBoard(self.entity.ID) > 0
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("After player casts a spell, %s summons a Tiger with stats equal to its cost."%self.entity.name)
		if number > 1:
			cost = min(10, number)
			newIndex = "Rumble~Paladin~%d~%d~%d~Minion~Beast~Tiger~Uncollectible"%(cost, number, number)
			subclass = type("Tiger"+str(number), (Tiger1, ),
							{"mana": cost, "attack": number, "health": number,
							"index": newIndex}
							)
			self.entity.Game.cardPool[newIndex] = subclass
			self.entity.Game.summonMinion(subclass(self.entity.Game, self.entity.ID), self.entity.position+1, self.entity.ID)
		else: #If the mana is 1, no need to create subclass.
			self.entity.Game.summonMinion(Tiger1(self.entity.Game, self.entity.ID), self.entity.position+1, self.entity.ID)
			
class Tiger1(Minion):
	Class, race, name = "Paladin", "Beast", "Tiger"
	mana, attack, health = 1, 1, 1
	index = "Rumble~Paladin~Minion~1~1~1~Beast~Tiger~Uncollectible"
	needTarget, keyWord, description = False, "", ""
	
	
class ZandalariTemplar(Minion):
	Class, race, name = "Paladin", "", "Zandalari Templar"
	mana, attack, health = 4, 4, 4
	index = "Rumble~Paladin~Minion~4~4~4~None~Zandalari Templar~Battlecry"
	needTarget, keyWord, description = False, "", "Battlecry: If you've restored 10 Health this game, gain +4/+4 and Taunt"
	def effectCanTrigger(self):
		self.effectViable = self.Game.CounterHandler.healthRestoredThisGame[self.ID] > 9
		
	def whenEffective(self, target=None, comment="", choice=0):
		if (self.inHand or self.onBoard) and self.Game.CounterHandler.healthRestoredThisGame[self.ID] > 9:
			print("Zandalari Templar's battlecry gives the minion gains +4/+4 and Taunt.")
			self.buffDebuff(4, 4)
			self.getsKeyword("Taunt")
		return None
		
#Weapon's overkill can be triggered by Doomrange(which returns the weapon to hand.)
class FarrakiBattleaxe(Weapon):
	Class, name = "Paladin", "Farraki Battleaxe"
	mana, attack, durability = 5, 3, 3
	index = "Rumble~Paladin~Weapon~5~3~3~Farraki Battleaxe~Overkill"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_FarrakiBattleaxe(self)]
		
class Trigger_FarrakiBattleaxe(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionTookDamage", "HeroTookDamage"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and target.health < 0 and self.entity.ID == self.entity.Game.turn
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("Farraki Battleaxe overkills %s and gives a random minion in player's hand +2/+2."%target.name)
		minionsinHand = []
		for card in self.entity.Game.Hand_Deck.hands[self.entity.ID]:
			if card.cardType == "Minion":
				minionsinHand.append(card)
				
		if minionsinHand != []:
			np.random.choice(minionsinHand).buffDebuff(2, 2)
			
			
class ANewChallenger(Spell):
	Class, name = "Paladin", "A New Challenger..."
	needTarget, mana = False, 7
	index = "Rumble~Paladin~Spell~7~A New Challenger..."
	description = "Discover 6-Cost minion. Summon it with Taunt and Divine Shield"
	poolIdentifier = "6-Cost Minions as Paladin"
	@classmethod
	def generatePool(cls, Game):
		classes, lists, neutralCards = [], [], []
		classCards = {"Neutral": [], "Druid":[], "Mage":[], "Hunter":[], "Paladin":[],
						"Priest":[], "Rogue":[], "Shaman":[], "Warlock":[], "Warrior":[]}
		for key, value in Game.MinionsofCost[6].items():
			classCards[key.split('~')[1]].append(value)
			
		for Class in ["Druid", "Hunter", "Mage", "Paladin", "Priest", "Rogue", "Shaman", "Warlock", "Warrior"]:
			classes.append("6-Cost Minions as "+Class)
			lists.append(classCards[Class]+classCards["Neutral"])
		return classes, lists #返回的包含“Class Cards except Hunter”等identifier的列表和其他职业卡表
		
	def available(self):
		return self.Game.spaceonBoard(self.ID) > 0
		
	def whenEffective(self, target=None, comment="", choice=0):
		if self.Game.spaceonBoard(self.ID) > 0:
			key = "6-Cost Minions as " + classforDiscover(self)
			if comment == "CastbyOthers":
				minion = np.random.choice(self.Game.RNGPools[key])(self.Game, self.ID)
				minion.getsKeyword("Taunt")
				minion.getsKeyword("Divine Shield")
				print("A New Challenger... is cast and summons a random 6-Cost minion %s with Taunt and Divine Shield."%minion.name)
				self.Game.summonMinion(minion, -1, self.ID)
			else:
				minions = np.random.choice(self.Game.RNGPools[key], 3, replace=False)
				self.Game.options = [obj(self.Game, self.ID) for obj in minions]
				print("A New Challenger... is cast and start the discover.")
				self.Game.DiscoverHandler.startDiscover(self)
		return None
		
	def discoverDecided(self, option):
		print(option.name, " is summoned and given Taunt and Divine Shield.")
		option.getsKeyword("Taunt")
		option.getsKeyword("Divine Shield")
		self.Game.summonMinion(option, -1, self.ID)
		
		
class ShirvallahtheTiger(Minion):
	Class, race, name = "Paladin", "Beast", "Shirvallah. the Tiger"
	mana, attack, health = 25, 7, 5
	index = "Rumble~Paladin~Minion~25~7~5~Beast~Shirvallah. the Tiger~Divine Shield~Rush~Lifesteal~Legendary"
	needTarget, keyWord, description = False, "Divine Shield,Rush,Lifesteal", "Divine Shield, Rush, Lifesteal. Costs(1) less for each Mana you've spent on spells"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersinHand = [Trigger_ShirvallahtheTiger(self)]
		
	def spellPlayed(self):
		if self.inHand:
			self.Game.ManaHandler.calcMana_Single(self)
			
	def selfManaChange(self):
		if self.inHand:
			self.mana -= self.Game.CounterHandler.manaSpentonSpells[self.ID]
			self.mana = max(self.mana, 0)
			
class Trigger_ShirvallahtheTiger(TriggerinHand):
	def __init__(self, entity):
		self.blank_init(entity, ["ManaCostPaid"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.inHand and subject.ID == self.entity.ID and subject.cardType == "Spell" and number > 0
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.Game.ManaHandler.calcMana_Single(self.entity)
		
"""Priest cards"""
class Regenerate(Spell):
	Class, name = "Priest", "Regenerate"
	needTarget, mana = True, 0
	index = "Rumble~Priest~Spell~0~Regenerate"
	description = "Restore 3 Health"
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			heal = 3 * (2 ** self.countHealDouble())
			print("Regenerate is cast, restores %d health to "%heal, target.name)
			self.restoresHealth(target, heal)
		return target
		
#Doesn't keep the enchantment of the minion.(Only the base stats.)
#If minion in hand or deck, still generates a base copy to your hand.
class Seance(Spell):
	Class, name = "Priest", "Seance"
	needTarget, mana = True, 2
	index = "Rumble~Priest~Spell~2~Seance"
	description = "Choose a minion. Add a copy of it to your hand"
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			print("Seance is cast and add a copy of minion %s to player's hand."%target.name)
			self.Game.Hand_Deck.addCardtoHand(type(target)(self.Game, self.ID), self.ID)
		return target
		
class SandDrudge(Minion):
	Class, race, name = "Priest", "", "Sand Drudge"
	mana, attack, health = 3, 3, 3
	index = "Rumble~Priest~Minion~3~3~3~None~Sand Drudge"
	needTarget, keyWord, description = False, "", "Whenever you cast a spell, summon a 1/1 Zombie with Taunt"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_SandDrudge(self)]
	
class Trigger_SandDrudge(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["SpellPlayed"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject.ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("Player casts a spell and %s summons a 1/1 Zombie with Taunt."%self.entity.name)
		self.entity.Game.summonMinion(Zombie(self.entity.Game, self.entity.ID), self.entity.position+1, self.entity.ID)
		
class Zombie(Minion):
	Class, race, name = "Priest", "", "Zombie"
	mana, attack, health = 1, 1, 1
	index = "Rumble~Priest~Minion~1~1~1~None~Zombie~Taunt~Uncollectible"
	needTarget, keyWord, description = False, "Taunt", "Taunt"
	
	
class SpiritoftheDead(Minion):
	Class, race, name = "Priest", "", "Spirit of the Dead"
	mana, attack, health = 1, 0, 3
	index = "Rumble~Priest~Minion~1~0~3~None~Spirit of the Dead"
	needTarget, keyWord, description = False, "", "Stealth for 1 turn. After a friendly minion dies, shuffle a 1-Cost copy of it into your hand"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.status["Temp Stealth"] = 1
		self.triggersonBoard = [Trigger_SpiritoftheDead(self)]
		
class Trigger_SpiritoftheDead(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionDeathResolutionFinished"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		#Technically, minion has to disappear before dies. But just in case.
		return self.entity.onBoard and target != self.entity and target.ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("After friendly minion %s dies and %s shuffles a copy of it to player's hand."%(target.name, self.entity.name))
		Copy = type(target)(self.entity.Game, self.entity.ID)
		self.entity.Game.Hand_Deck.shuffleCardintoDeck(Copy, self.entity.ID)
		
#Frozen minions and minions with 0 attacks will still attack.
class MassHysteria(Spell):
	Class, name = "Priest", "Mass Hysteria"
	needTarget, mana = False, 5
	index = "Rumble~Priest~Spell~5~Mass Hysteria"
	description = "Force each minion to attack another random minion"
	def whenEffective(self, target=None, comment="", choice=0):
		self.Game.skipDeathCalc = True
		print("Mass Hysteria is cast and forces all minions to attack another random minion.")
		minionstoAttack = []
		for minion in self.Game.minionsonBoard(1) + self.Game.minionsonBoard(2):
			if minion.health > 0:
				minionstoAttack.append(minion)
				
		for minionAffected in minionstoAttack:
			if minionAffected.health > 0:
				targets = []
				for minion in self.Game.minionsonBoard(1) + self.Game.minionsonBoard(2):
					if minion.health > 0 and minion != minionAffected:
						targets.append(minion)
				if targets == []:
					print("No other minions standing.")
					break
				else:
					target = np.random.choice(targets)
					print(minionAffected.name, " will now attack another random minion ", target.name)
					self.Game.battleRequest(minionAffected, target, False, False)
		self.Game.skipDeathCalc = False			
		print("Now after the Mass Hysteria, the death resolution starts.")
		return None
		
class GraveHorror(Minion):
	Class, race, name = "Priest", "", "Grave Horror"
	mana, attack, health = 12, 7, 8
	index = "Rumble~Priest~Minion~12~7~8~None~Grave Horror~Taunt"
	needTarget, keyWord, description = False, "Taunt", "Taunt. Costs (1) less for each spell you've cast this game"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersinHand = [Trigger_GraveHorror(self)]
		
	def selfManaChange(self):
		if self.inHand:
			num = 0
			for index in self.Game.CounterHandler.cardsPlayedThisGame[self.ID]:
				if "~Spell~" in index:
					num += 1
			self.mana -= num
			self.mana = max(self.mana, 0)
			
class Trigger_GraveHorror(TriggerinHand):
	def __init__(self, entity):
		#假设这个费用改变扳机在“当你使用一张法术之后”。不需要预检测
		self.blank_init(entity, ["SpellBeenPlayed"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.inHand and subject.ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.Game.ManaHandler.calcMana_Single(self.entity)
		
		
class AuchenaiPhantasm(Minion):
	Class, race, name = "Priest", "", "Auchenai Phantasm"
	mana, attack, health = 2, 3, 2
	index = "Rumble~Priest~Minion~2~3~2~None~Auchenai Phantasm~Battlecry"
	needTarget, keyWord, description = False, "", "Battlecry: This turn, your healing effects deal damage instead"
	
	def whenEffective(self, target=None, comment="", choice=0):
		self.Game.playerStatus[self.ID]["Heal to Damage"] += 1
		print("Auchenai Phantasm's battlecry player's heals deal damage instead this turn.")
		self.Game.turnEndTrigger.append(AuchenaiEffectDisappears(self.Game, self.ID))
		return None
		
class AuchenaiEffectDisappears:
	def __init__(self, Game, ID):
		self.Game = Game
		self.ID = ID
		
	def turnEndTrigger(self):
		print("At the end of turn, Auchenai Phantasm's effect expires and player's healing no longer does damage")
		if self.Game.playerStatus[self.ID]["Heal to Damage"] > 0:
			self.Game.playerStatus[self.ID]["Heal to Damage"] -= 1
		extractfrom(self, self.Game.turnEndTrigger)
		
		
class SurrendertoMadness(Spell):
	Class, name = "Priest", "Surrender to Madness"
	needTarget, mana = False, 3
	index = "Rumble~Priest~Spell~3~Surrender to Madness"
	description = "Destroy 3 of your Mana Crystals. Give all minions in your deck +2/+2"
	def whenEffective(self, target=None, comment="", choice=0):
		print("Surrender to Madness is cast, destroys 3 of player's mana crystals and all minions in player's deck gain +2/+2.")
		self.Game.ManaHandler.manasUpper[self.ID] -= 3
		self.Game.ManaHandler.manas[self.ID] = min(self.Game.ManaHandler.manas[self.ID], self.Game.ManaHandler.manasUpper[self.ID])
		for card in self.Game.Hand_Deck.decks[self.ID]:
			if card.cardType == "Minion":
				card.buffDebuff(2, 2)
		return None
		
#Assume Bwonsamdi's battlecry won't trigger twice.
class BwonsamditheDead(Minion):
	Class, race, name = "Priest", "", "Bwonsamdi. the Dead"
	mana, attack, health = 7, 7, 7
	index = "Rumble~Priest~Minion~7~7~7~None~Bwonsamdi. the Dead~Battlecry~Legendary"
	needTarget, keyWord, description = False, "", "Battlecry: Draw 1-Cost minions from your deck until your hand is full"
	
	def whenEffective(self, target=None, comment="", choice=0):
		print("Bwonsamdi. the Dead's battlecry player draws 1-Cost minion from deck until his hand is full.")
		while True:
			oneCostMinionsinDeck = []
			for card in self.Game.Hand_Deck.decks[self.ID]:
				if card.cardType == "Minion" and card.mana == 1:
					oneCostMinionsinDeck.append(card)
			if oneCostMinionsinDeck != [] and self.Game.Hand_Deck.handNotFull(self.ID):
				self.Game.Hand_Deck.drawCard(self.ID, np.random.choice(oneCostMinionsinDeck))
			else:
				break
		return None
		
		
class PrincessTalanji(Minion):
	Class, race, name = "Priest", "", "Princess Talanji"
	mana, attack, health = 8, 7, 5
	index = "Rumble~Priest~Minion~8~7~5~None~Princess Talanji~Battlecry~Legendary"
	needTarget, keyWord, description = False, "", "Battlecry: Summon all minions from you hand that didn't start in your deck"
	def effectCanTrigger(self):
		self.effectViable = False
		for card in self.Game.Hand_Deck.hands[self.ID]:
			if card.cardType == "Minion" and card.identity not in self.Game.startingDeckIdenties[self.ID] and card != self:
				self.effectViable = True
				break
				
	#不知道战吼召唤手牌中随从时是一次性选定所有目标还是在循环里把手牌中从左到右的合法目标依次召唤上场。
	#后者可能会因为召唤过程中发生的抽牌事件而把新抽到的随从也召唤上场
	#暂时假定是一次性选定目标来进行召唤。
	def whenEffective(self, target=None, comment="", choice=0):
		print("Princess Talanji's battlecry summons all minions in player's hand that didn't start in player's deck.")
		minionsCreated = []
		for card in self.Game.Hand_Deck.hands[self.ID]:
			if card.cardType == "Minion" and card.identity not in self.Game.startingDeckIdenties[self.ID]:
				minionsCreated.append(card)
				
		if minionsCreated != []:
			self.Game.summonMinion(minionsCreated, (self.position+1, "totheRight"), self.ID)
		return None
		
"""Rogue cards"""
class SerratedTooth(Weapon):
	Class, name = "Rogue", "Serrated Tooth"
	mana, attack, durability = 1, 1, 3
	index = "Rumble~Rogue~Weapon~1~1~3~Serrated Tooth~Deathrattle"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [GiveFriendlyMinionsRush(self)]
		
class GiveFriendlyMinionsRush(Deathrattle_Weapon):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("Deathrattle: Give your minions Rush triggers")
		for minion in self.entity.Game.minionsonBoard(self.entity.ID):
			minion.getsKeyword("Rush")
			
			
class StolenSteel(Spell):
	Class, name = "Rogue", "Stolen Steel"
	needTarget, mana = False, 2
	index = "Rumble~Rogue~Spell~2~Stolen Steel"
	description = "Discover a weapon (from another class)"
	poolIdentifier = "Weapons except Rogue"
	@classmethod
	def generatePool(cls, Game):
		classes, lists = [], []
		for Class in ["Druid", "Mage", "Hunter", "Paladin", "Priest", "Rogue", "Shaman", "Warlock", "Warrior", "Neutral"]:
			classes.append("Weapons except "+Class)
			Classes = ["Druid", "Mage", "Hunter", "Paladin", "Priest", "Rogue", "Shaman", "Warlock", "Warrior"]
			extractfrom(Class, Classes)
			weapons = []
			for ele in Classes:
				for key, value in Game.ClassCards[ele].items():
					if "~Weapon~" in key:
						weapons.append(value)
			lists.append(weapons)
		return classes, lists
		
	def whenEffective(self, target=None, comment="", choice=0):
		if self.Game.Hand_Deck.handNotFull(self.ID):
			key = "Weapons except "+self.Game.heroes[self.ID].Class
			if comment == "CastbyOthers":
				print("Stolen Steel is cast and adds a random weapon from another class to player's hand")
				self.Game.Hand_Deck.addCardtoHand(np.random.choice(self.Game.RNGPools[key]), self.ID)
			else:
				weapons = np.random.choice(self.Game.RNGPools[key], 3, replace=False)
				self.Game.options = [weapon(self.Game, self.ID) for weapon in weapons]
				print("Stolen Steel is cast and lets player discover a Weapon from another class")
				self.Game.DiscoverHandler.startDiscover(self)
				
		return None
		
	def discoverDecided(self, option):
		print("Weapon %s added to player %d's hand."%option.name)
		self.Game.Hand_Deck.addCardtoHand(option, self.ID)
		self.Game.sendSignal("DiscoveredCardPutintoHand", self.ID, self, option, 0, "")
		
		
class BloodsailHowler(Minion):
	Class, race, name = "Rogue", "", "Bloodsail Howler"
	mana, attack, health = 2, 1, 1
	needTarget, keyWord = False, "Rush"
	index = "Rumble~Rogue~Minion~2~1~1~Pirate~Bloodsail Howler~Rush~Battlecry"
	def effectCanTrigger(self):
		self.effectViable = False
		for minion in self.Game.minionsonBoard(self.ID):
			if "Pirate" in minion.race:
				self.effectViable = True
				break
				
	def whenEffective(self, target=None, comment="", choice=0):
		if self.onBoard or self.inHand:
			numPirate = 0
			for minion in self.Game.minionsonBoard(self.ID):
				if "Pirate" in minion.race and minion != self:
					numPirate += 1
			print("Bloodsail Howler's battlecry twice and minion gains +2/+2 for each other Pirate player controls.")
			self.buffDebuff(numPirate, numPirate)
		return None
		
		
class RaidingParty(Spell):
	Class, name = "Rogue", "Raiding Party"
	needTarget, mana = False, 4
	index = "Rumble~Rogue~Spell~4~Raiding Party"
	description = "Draw 2 Pirates from your deck. Combo: And a weapon"
	def effectCanTrigger(self):
		self.effectViable = self.Game.CounterHandler.cardsPlayedThisTurn[self.ID]["Indices"] != []
		
	def whenEffective(self, target=None, comment="", choice=0):
		print("Raiding Party is cast and player draws two Pirates from deck.")
		piratesinDeck = []
		for card in self.Game.Hand_Deck.decks[self.ID]:
			if card.cardType == "Minion" and "Pirate" in card.race:
				piratesinDeck.append(card)
				
		if len(piratesinDeck) > 1:
			pirates = np.random.choice(piratesinDeck, 2, replace=False)
			self.Game.Hand_Deck.drawCard(self.ID, pirates)
		elif len(piratesinDeck) == 1:
			pirate = np.random.choice(piratesinDeck)
			self.Game.Hand_Deck.drawCard(self.ID, pirate)
			
		if self.Game.CounterHandler.cardsPlayedThisTurn[self.ID]["Indices"] != []:
			print("Raiding Party's combo effect triggers and player also draws a weapon from deck.")
			weaponsinDeck = []
			for card in self.Game.Hand_Deck.decks[self.ID]:
				if card.cardType == "Weapon":
					weaponsinDeck.append(card)
					
			if weaponsinDeck != []:
				weapon = np.random.choice(weaponsinDeck)
				self.Game.Hand_Deck.drawCard(self.ID, weapon)
		return None
		
		
class SpiritoftheShark(Minion):
	Class, race, name = "Rogue", "", "Spirit of the Shark"
	mana, attack, health = 4, 0, 3
	index = "Rumble~Rogue~Minion~4~0~3~None~Spirit of the Shark"
	needTarget, keyWord, description = False, "", "Stealth for 1 turn. Your minions' Battlecries and Combos trigger twice"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.marks["Temp Stealth"] = 1
		self.appearResponse = [self.activateAura]
		self.disappearResponse = [self.deactivateAura]
		self.silenceResponse = [self.deactivateAura]
		
	def activateAura(self):
		print("Spirit of the Shark's aura appears and player's minions' Battlecries and Combos trigger twice.")
		self.Game.playerStatus[self.ID]["Shark Battlecry Trigger Twice"] += 1
		
	def deactivateAura(self):
		print("Spirit of the Shark's aura is removed and player's minions' Battlecries and Combos no longer trigger twice.")
		self.Game.playerStatus[self.ID]["Shark Battlecry Trigger Twice"] -= 1
		
		
class WalkthePlank(Spell):
	Class, name = "Rogue", "Walk the Plank"
	needTarget, mana = True, 4
	index = "Rumble~Rogue~Spell~4~Walk the Plank"
	description = "Destroy an undamaged minion"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.health == target.health_upper and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			print("Walk the Plank is cast and destroys undamaged minion "%target.name)
			target.dead = True
		return target
		
		
class CannonBarrage(Spell):
	Class, name = "Rogue", "Cannon Barrage"
	needTarget, mana = False, 6
	index = "Rumble~Rogue~Spell~6~Cannon Barrage"
	description = "Deal 3 damage to a enemy. Repeat for each Pirate you control"
	def effectCanTrigger(self):
		self.effectViable = False
		for minion in self.Game.minionsonBoard(self.ID):
			if "Pirate" in minion.race:
				self.effectViable = True
				break
				
	def whenEffective(self, target=None, comment="", choice=0):
		damage = (3 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		print("Cannon Barrage is cast and deals %d damage to a random minion. Repeats for each Pirate player controls.")
		numPirates = 0
		for minion in self.Game.minionsonBoard(self.ID):
			if "Pirate" in minion.race:
				numPirates += 1
				
		for i in range(numPirates + 1):
			targets = self.Game.heroes[3-self.ID]
			for minion in self.Game.minionsonBoard(3-self.ID):
				if minion.health > 0:
					targets.append(minion)
					
			self.dealsDamage(np.random.choice(targets), damage)
		return None
		
		
class GurubashiHypemon(Minion):
	Class, race, name = "Rogue", "", "Gurubashi Hypemon"
	mana, attack, health = 7, 5, 7
	index = "Rumble~Rogue~Minion~7~5~7~None~Gurubashi Hypemon~Battlecry"
	needTarget, keyWord, description = False, "", "Battlecry: Discover a 1/1 copy of a Battlecry minion. It costs (1)"
	poolIdentifier = "Battlecry Minions as Rogue"
	@classmethod
	def generatePool(cls, Game):
		classes, lists, neutralMinions = [], [], []
		#确定中立的战吼随从列表
		for key, value in Game.NeutralMinions.items():
			if "~Minion~" in key and "~Battlecry~" in key:
				neutralMinions.append(value)
		#职业为中立时，视为作为盗贼打出此牌
		for Class in ["Druid", "Mage", "Hunter", "Paladin", "Priest", "Rogue", "Shaman", "Warlock", "Warrior"]:
			classes.append("Battlecry Minions as " + Class)
			battlecryMinionsinClass = []
			for key, value in Game.ClassCards[Class].items():
				if "~Minion~" in key and "~Battlecry~" in key:
					battlecryMinionsinClass.append(value)
			#包含职业牌中的战吼随从和中立战吼随从
			lists.append(battlecryMinionsinClass+neutralMinions)
		return classes, lists
		
	def whenEffective(self, target=None, comment="", choice=0):
		if self.ID == self.Game.turn and self.Game.Hand_Deck.handNotFull(self.ID):
			key = "Battlecry Minions as "+classforDiscover(self)
			if comment == "InvokedbyOthers":
				print("Gurubashi Hypemon's battlecry adds the 1/1 copy of a random Battlecy minion to player's hand.")
				minion = np.random.choice(self.Game.RNGPools[key])(self.Game, self.ID)
				minion.statReset(1, 1)
				ManaModification(minion, changeby=0, changeto=1).applies()
				self.Game.Hand_Deck.addCardtoHand(minion, self.ID)
			else:
				minions = np.random.choice(self.Game.RNGPools[key], 3, replace=False)
				self.Game.options = [minion(self.Game, self.ID) for minion in minions]
				self.Game.DiscoverHandler.startDiscover(self)
				
		return None
		
	def discoverDecided(self, option):
		print("1-Cost 1/1 copy of battlecry minion ", option.name, " is put into player's hand.")
		option.statReset(1, 1)
		ManaModification(option, changeby=0, changeto=1).applies()
		self.Game.Hand_Deck.addCardtoHand(option, self.ID)
		self.Game.sendSignal("DiscoveredCardPutintoHand", self.ID, self, option, 0, "")
		
		
class GraltheShark(Minion):
	Class, race, name = "Rogue", "Beast", "Gral. the Shark"
	mana, attack, health = 5, 2, 2
	index = "Rumble~Rogue~Minion~5~2~2~Beast~Gral. the Shark~Battlecry~Deathrattle_Legendary"
	needTarget, keyWord, description = False, "", "Battlecry: Eat a minion in your deck and gains its stats. Deathrattle: Add it to your hand"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [AddEatenMiniontoHand(self)]
		
	def whenEffective(self, target=None, comment="", choice=0):
		minionsinDeck = []
		for card in self.Game.Hand_Deck.decks[self.ID]:
			if card.cardType == "Minion":
				minionsinDeck.append(card)
		#鲨鱼之神只会记录最后一次被吃掉的随从，第二次的会覆盖第一次吃掉的
		if minionsinDeck != []:
			minion = extractfrom(np.random.choice(minionsinDeck), self.Game.Hand_Deck.decks[self.ID])
			print("Gral. the Shark's battlecry Eats minion %s in player's deck to gains its stat."%minion.name)
			self.Game.Hand_Deck.extractfromDeck(minion)
			self.buffDebuff(minion.attack, minion.health)
			for trigger in self.deathrattles:
				if type(trigger) == AddEatenMiniontoHand:
					trigger.eatenMinion = type(minion)
		return None
		
class AddEatenMiniontoHand(Deathrattle_Minion):
	def __init__(self, entity):
		self.blank_init(entity)
		self.eatenMinion = None
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		if self.eatenMinion != None:
			print("Deathrattle: Add a copy of the eaten minion to your hand triggers")
			self.entity.Game.Hand_Deck.addCardtoHand(self.entity.eatenMinion, self.entity.ID, "CreateUsingType")
			
			
class CaptainHooktusk(Minion):
	Class, race, name = "Rogue", "Pirate", "Captain Hooktusk"
	mana, attack, health = 8, 6, 3
	index = "Rumble~Rogue~Minion~8~6~3~Pirate~Captain Hooktusk~Battlecry~Legendary"
	needTarget, keyWord, description = False, "", "Battlecry: Summon 3 Pirates from your deck. Give them Rush"
	
	def whenEffective(self, target=None, comment="", choice=0):
		piratesinDeck = []
		for card in self.Game.Hand_Deck.decks[self.ID]:
			if card.cardType == "Minion" and "Pirate" in card.race:
				piratesinDeck.append(card)
				
		numSummon = min(3, len(piratesinDeck), self.Game.countAvailableSpots(self.ID))
		if numSummon > 0:
			minions = np.random.choice(minionsinDeck, numSummon, replace=False)
			for minion in fixedList(minions):
				if self.Game.spaceonBoard(self.ID) > 0:
					minion.getsKeyword("Rush")
					self.Game.summonfromHand(minion, self.position+1, self.ID)
		return None
		
"""Shaman cards"""
class TotemicSmash(Spell):
	Class, name = "Shaman", "Totemic Smash"
	needTarget, mana = True, 1
	index = "Rumble~Shaman~Spell~1~Totemic Smash~Overkill"
	description = "Deal 2 damage. Overkill: Summon a basic totem"
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			damage = (2 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			print("Totemic Smash is cast and deals %d damage to "%damage, target.name)
			objtoTakeDamage, targetSurvival = self.dealsDamage(target, damage)
			if objtoTakeDamage.health < 0:
				basicTotem = np.random.choice(BasicTotems)
				self.Game.summonMinion(basicTotem(self.Game, self.ID), -1, self.ID)
		return target
		
		
class Wartbringer(Minion):
	Class, race, name = "Shaman", "", "Wartbringer"
	mana, attack, health = 1, 2, 1
	index = "Rumble~Shaman~Minion~1~2~1~None~Wartbringer~Battlecry"
	needTarget, keyWord, description = True, "", "Battlecry: If you played 2 spells this turn, deal 2 damage"
	
	def effectCanTrigger(self):
		self.effectViable = self.Game.CounterHandler.numSpellsPlayedThisTurn[self.ID] > 1
		
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None and self.Game.CounterHandler.numSpellsPlayedThisTurn[self.ID] > 1:
			print("Wartbringer's battlecry deals 2 damage to ", target.name)
			self.dealsDamage(target, 2)
		return target
		
		
class BigBadVoodoo(Spell):
	Class, name = "Shaman", "Big Bad Voodoo"
	needTarget, mana = True, 2
	index = "Rumble~Shaman~Spell~2~Big Bad Voodoo"
	description = "Give a friendly minion 'Deathrattle: Summon a random minion that costs (1) more'"
	def available(self):
		return self.selectableFriendlyMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.ID == self.ID and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			print("Big Bad Voodoo is cast and gives friendly minion %s Deathrattle: Summon a random minion that costs 1 more.")
			trigger = SummonaMinionCosting1More(target)
			target.deathrattles.append(trigger)
			if target.onBoard:
				trigger.connect()
		return target
		
def SummonaMinionCosting1More(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		cost = type(self.entity).mana
		if cost + 1 in self.entity.Game.MinionsofCost.keys():
			cost += 1
		minion = np.random.choice(list(self.entity.Game.MinionsofCost[cost].values()))
		print("Deathrattle: Summon a minion that costs (1) more triggers.")
		self.entity.Game.summonMinion(minion(self.entity.Game, self.entity.ID), self.entity.position+1, self.entity.ID)
		
		
class Likkim(Weapon):
	Class, name = "Shaman", "Likkim"
	mana, attack, durability = 2, 1, 3
	index = "Rumble~Shaman~Weapon~2~1~3~Likkim"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.auras["Self Aura"] = WeaponBuffAura_Likkim(self)
		self.activated = True
		
class WeaponBuffAura_Likkim:
	def __init__(self, weapon):
		self.weapon = weapon
		self.auraAffected = []
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.weapon.onBoard and ID == self.weapon.ID
		
	def trigger(self, signal, ID, subject, target, number, comment, choice=0):
		if self.canTrigger(signal, ID, subject, target, number, comment):
			self.effect(signal, ID, subject, target, number, comment)
			
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		isOverloaded = self.weapon.Game.ManaHandler.manasOverloaded[self.weapon.ID] > 0 or self.weapon.Game.ManaHandler.manasLocked[self.weapon.ID] > 0
		if isOverloaded == False and self.weapon.activated:
			self.weapon.activated = False
			for weapon, aura_Receiver in fixedList(self.auraAffected):
				aura_Receiver.effectClear()
		elif isOverloaded and self.weapon.activated == False:
			self.weapon.activated = True
			aura_Receiver = WeaponBuffAura_Receiver(self.weapon, self)
			aura_Receiver.effectStart()
			
	def applies(self, subject):
		if subject == self.weapon:
			aura_Receiver = WeaponBuffAura_Receiver(subject, self, 2, 0)
			aura_Receiver.effectStart()
			
	def auraAppears(self):
		isOverloaded = self.weapon.Game.ManaHandler.manasOverloaded[self.weapon.ID] > 0 or self.weapon.Game.ManaHandler.manasLocked[self.weapon.ID] > 0
		if isOverloaded:
			self.weapon.activated = True
			self.applies(self.weapon)
			
		self.weapon.Game.triggersonBoard[self.weapon.ID].append((self, "OverloadStatusCheck"))
		
	def auraDisappears(self):
		for weapon, aura_Receiver in fixedList(self.auraAffected):
			aura_Receiver.effectClear()
			
		self.auraAffected = []
		self.activated = False
		extractfrom((self, "OverloadStatusCheck"), self.weapon.Game.triggersonBoard[self.weapon.ID])
		
		
class BogSlosher(Minion):
	Class, race, name = "Shaman", "", "Bog Slosher"
	mana, attack, health = 3, 3, 3
	index = "Rumble~Shaman~Minion~3~3~3~None~Bog Slosher~Battlecry"
	needTarget, keyWord, description = True, "", "Battlecry: Return a friendly minion to your hand and give +2/+2"
	def targetExists(self, choice=0):
		return self.selectableFriendlyMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.ID == self.ID and target.onBoard and target != self 
		
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			print("Bog Slosher's battlecry returns friendly minion %s to player's hand."%target.name)
			target = self.Game.returnMiniontoHand(target)
			if target != None:
				print("Bog Slosher's battlecry gives returned minion %s +2/+2."%target.name)
				target.buffDebuff(2, 2)
				
		return target
		
		
class HauntingVisions(Spell):
	Class, name = "Shaman", "Haunting Visions"
	needTarget, mana = False, 3
	index = "Rumble~Shaman~Spell~3~Haunting Visions"
	description = "The next spell you cast this turn costs (3) less. Discover a spell"
	poolIdentifier = "Shaman Spells"
	@classmethod
	def generatePool(cls, Game):
		classes, lists = [], []
		for Class in ["Druid", "Mage", "Hunter", "Paladin", "Priest", "Rogue", "Shaman", "Warlock", "Warrior"]:
			classes.append(Class+" Spells")
			spellsinClass = []
			for key, value in Game.ClassCards[Class].items():
				if "~Spell~" in key:
					spellsinClass.append(value)
			lists.append(spellsinClass)
		return classes, lists
		
	def whenEffective(self, target=None, comment="", choice=0):
		print("Haunting Visions is cast and next spell this turn costs 3 less.")
		tempAura = YourNextSpellCosts3LessThisTurn(self.Game, self.ID)
		self.Game.ManaHandler.CardAuras.append(tempAura)
		tempAura.auraAppears()
		if self.Game.Hand_Deck.handNotFull(self.ID):
			key = classforDiscover(self)+" Spells"
			if comment == "CastbyOthers":
				print("Haunting Visions is cast and adds a random spell to player's hand.")
				self.Game.Hand_Deck.addCardtoHand(np.random.choice(self.Game.RNGPools[key]), self.ID, "CreateUsingType")
			else:
				spells = np.random.choice(self.Game.RNGPools[key], 3, replace=False)
				self.Game.options = [spell(self.Game, self.ID) for spell in spells]
				print("Haunting Visions is cast and lets player Discover a spell.")
				self.Game.DiscoverHandler.startDiscover(self)
		return None
		
	def discoverDecided(self, option):
		print("Spell %s is added to player's hand"%option.name)
		self.Game.Hand_Deck.addCardtoHand(option, self.ID)
		self.Game.sendSignal("DiscoveredCardPutintoHand", self.ID, self, option, 0, "")
		
class YourNextSpellCosts3LessThisTurn(TempManaEffect):
	def __init__(self, Game, ID):
		self.Game, self.ID = Game, ID
		self.changeby, self.changeto = -3, -1
		self.temporary = True
		self.auraAffected = []
		
	def applicable(self, target):
		return target.ID == self.ID and target.cardType == "Spell"
		
		
class SpiritoftheFrog(Minion):
	Class, race, name = "Shaman", "", "Spirit of the Frog"
	mana, attack, health = 3, 0, 3
	index = "Rumble~Shaman~Minion~3~0~3~None~Spirit of the Frog"
	needTarget, keyWord, description = False, "", "Stealth for 1 turn. Whenever you cast a spell, draw a spell from your deck that costs (1) more"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.status["Temp Stealth"] = 1
		self.triggersonBoard = [Trigger_SpiritoftheFrog(self)]
		
class Trigger_SpiritoftheFrog(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["SpellPlayed"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject.ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("Player casts a spell and Spirit of the Frog lets player draw a spell from deck that costs (1) more.")
		cardstoDraw = []
		for card in self.entity.Game.Hand_Deck.decks[self.entity.ID]:
			if card.cardType == "Spell" and card.mana == number + 1:
				cardstoDraw.append(card)
				
		if cardstoDraw != []:
			self.entity.Game.Hand_Deck.drawCard(self.entity.ID, np.random.choice(cardstoDraw))
			
#Spells repeated by Electra Stormsurge will also target adjacent minions.
#Spells repeated other cards, such as Archmage Vargoth won't target adjacent minions.
#Djinni of Zephyrs will only respond to the spell cast on the center of the three targets, instead of all three of them.
#如果打出了有抉择全选选项的法术，那么重复施放的法术也会有抉择全选。
class Zentimo(Minion):
	Class, race, name = "Shaman", "", "Zentimo"
	mana, attack, health = 3, 1, 3
	index = "Rumble~Shaman~Minion~3~1~3~None~Zentimo~Legendary"
	needTarget, keyWord, description = False, "", "Whenever you cast a spell, cast it again on its neighbors"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.appearResponse = [self.activateAura]
		self.disappearResponse = [self.deactivateAura]
		self.silenceResponse = [self.deactivateAura]
		
	def activateAura(self):
		print("Zentimo's aura is registered. Spells cast by player will also target adjacent minions.")
		self.Game.playerStatus[self.ID]["Spells Target Adjacent Minions"] += 1
		
	def deactivateAura(self):
		print("Zentimo's aura is removed. Spells cast by player no longer target adjacent minions.")
		if self.Game.playerStatus[self.ID]["Spells Target Adjacent Minions"] > 0:
			self.Game.playerStatus[self.ID]["Spells Target Adjacent Minions"] -= 1
			
			
class KragwatheFrog(Minion):
	Class, race, name = "Shaman", "Beast", "Krag'wa. the Frog"
	mana, attack, health = 6, 4, 6
	index = "Rumble~Shaman~Minion~6~4~6~Beast~Krag'wa. the Frog~Battlecry~Legendary"
	needTarget, keyWord, description = False, "", "Battlecry: Return all spells you played last turn to your hand"
	def effectCanTrigger(self):
		self.effectViable = self.Game.CounterHandler.spellsPlayedLastTurn[self.ID] != []
		
	def whenEffective(self, target=None, comment="", choice=0):
		numSpell = min(self.Game.Hand_Deck.spaceinHand(self.ID), len(self.Game.CounterHandler.spellsPlayedLastTurn[self.ID]))
		if numSpell > 0:
			spells = np.random.choice(self.Game.CounterHandler.spellsPlayedLastTurn[self.ID], numSpell, replace=False)
			print("Krag'wa. the Frog's battlecry returns spells player played last turn to player's hand.")
			self.Game.Hand_Deck.addCardtoHand(spell, self.ID, comment="CreateUsingIndex")
			if self.Game.playerStatus[self.ID]["Battlecry Trigger Twice"] + self.Game.playerStatus[self.ID]["Shark Battlecry Trigger Twice"] > 0 and comment == "InvokedbyOthers":
				numSpell = min(self.Game.Hand_Deck.spaceinHand(self.ID), len(self.Game.CounterHandler.spellsPlayedLastTurn[self.ID]))
				if numSpell > 0:
					spells = np.random.choice(self.Game.CounterHandler.spellsPlayedLastTurn[self.ID], numSpell, replace=False)
					print("Krag'wa. the Frog's battlecry again and and returns all spells player played last turn to player's hand.")
					self.Game.Hand_Deck.addCardtoHand(spell, self.ID, comment="CreateUsingIndex")
		return None
		
		
class RainofToads(Spell):
	Class, name = "Shaman", "Rain of Toads"
	needTarget, mana = False, 6
	index = "Rumble~Shaman~Spell~6~Rain of Toads~Overload"
	description = "Summon three 2/4 Toads with Taunt. Overload: (3)"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.overload = 3
		
	def available(self):
		return self.Game.spaceonBoard(self.ID) > 0
		
	def whenEffective(self, target=None, comment="", choice=0):
		print("Rain of Toads is cast and summons three 2/4 Toads with Taunt.")
		self.Game.summonMinion([Toad(self.Game, self.ID) for i in range(3)], (-1, "totheRightEnd"), self.ID)
		return None
		
class Toad(Minion):
	Class, race, name = "Shaman", "Beast", "Toad"
	mana, attack, health = 3, 2, 4
	index = "Rumble~Shaman~Minion~3~2~4~Beast~Toad~Taunt~Uncollectible"
	needTarget, keyWord, description = False, "Taunt", "Taunt"
	
	
"""Warlock cards"""
class RecklessDiretroll(Minion):
	Class, race, name = "Warlock", "", "Reckless Diretroll"
	mana, attack, health = 3, 2, 6
	index = "Rumble~Warlock~Minion~3~2~6~None~Reckless Diretroll~Taunt~Battlecry"
	needTarget, keyWord, description = False, "Taunt", "Taunt. Battlecry: Discard the lowest Cost card"
	
	def whenEffective(self, target=None, comment="", choice=0):
		if self.Game.Hand_Deck.hands[self.ID] != []:
			cardsandMana = [self.Game.Hand_Deck.hands[self.ID][0].mana, []]
			for card in self.Game.Hand_Deck.hands[self.ID]:
				if card.mana < cardsandMana[0]:
					cardsandMana[0] = card.mana
					cardsandMana[1] = [card]
				elif card.mana == cardsandMana[0]:
					cardsandMana[1].append(card)
					
			cardtoDiscard = np.random.choice(cardsandMana[1])
			self.Game.Hand_Deck.discardCard(self.ID, cardtoDiscard)
		return None
		
		
class BloodTrollSapper(Minion):
	Class, race, name = "Warlock", "", "Blood Troll Sapper"
	mana, attack, health = 7, 5, 8
	index = "Rumble~Warlock~Minion~7~5~8~None~Blood Troll Sapper"
	needTarget, keyWord, description = False, "", "After a friendly minion dies, deal 2 damage to the enemy hero"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [(self)]
		
	def deal2DamagetoEnemyHero(self, target):
		if self.onBoard and self.health > 0 and target.ID == self.ID and target != self:
			print("A friendly minion dies and Blood Troll Sapper deals 2 damage to the enemy hero.")
			self.dealsDamage(self.Game.heroes[3-self.ID], 2)
			
			
class Demonbolt(Spell):
	Class, name = "Warlock", "Demonbolt"
	needTarget, mana = True, 8
	index = "Rumble~Warlock~Spell~8~Demonbolt"
	description = "Destroy a minion. Costs (1) less for each minion you control"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		
	def selfManaChange(self):
		if self.inHand:
			self.mana -= len(self.Game.minionsonBoard(self.ID))
			self.mana = max(self.mana, 0)
			
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			print("Demonbolt is cast and destroys a minion.")
			target.dead = True
		return target
		
#Don't know if the dead minion will be removed from board before the buff or not.
class GrimRally(Spell):
	Class, name = "Warlock", "Grim Rally"
	needTarget, mana = True, 1
	index = "Rumble~Warlock~Spell~1~Grim Rally"
	description = "Destroy a friendly minion. Give your minions +1/+1"
	def available(self):
		return self.selectableFriendlyMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.ID == self.ID and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			print("Grim Rally is cast, destroys friendly minion %s and gives other friendly minions +1/+1."%target.name)
			target.dead = True
			for minion in self.Game.minionsonBoard(self.ID):
				if minion != target:
					minion.buffDebuff(1, 1)
		return target
		
#Don't know if SilverwareGolem will be summoned before or after the AOE damage.
#For now, assume it's after the AOE damage.
class Shriek(Spell):
	Class, name = "Warlock", "Shriek"
	needTarget, mana = False, 1
	index = "Rumble~Warlock~Spell~1~Shriek"
	description = "Discard your lowest Cost card. Deal 2 damage to all minions"
	def whenEffective(self, target=None, comment="", choice=0):
		print("Shriek is cast, discards the lowest Cost card in player's hand and deals %d damage to all minions."%damage)
		damage = (2 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		targets = self.Game.minionsonBoard(1) + self.Game.minionsonBoard(2)
		if self.Game.Hand_Deck.hands[self.ID] != []:
			cardsandMana = [self.Game.Hand_Deck.hands[self.ID][0].mana, []]
			for card in self.Game.Hand_Deck.hands[self.ID]:
				if card.mana < cardsandMana[0]:
					cardsandMana[0] = card.mana
					cardsandMana[1] = [card]
				elif card.mana == cardsandMana[0]:
					cardsandMana[1].append(card)
					
			cardtoDiscard = np.random.choice(cardsandMana[1])
			self.Game.Hand_Deck.discardCard(self.ID, cardtoDiscard)
		self.dealsDamage(targets, [damage for minion in targets])
		return None
		
		
class SpiritoftheBat(Minion):
	Class, race, name = "Warlock", "", "Spirit of the Bat"
	mana, attack, health = 2, 0, 3
	index = "Rumble~Warlock~Minion~2~0~3~None~Spirit of the Bat"
	needTarget, keyWord, description = False, "", "Stealth for 1 turn. After a friendly minion dies, give a minion in your hand +1/+1"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.marks["Temp Stealth"] = 1
		self.triggersonBoard = [(self)]
		
	def giveaMinioninHandPlus1Plus1(self, target):
		if self.onBoard and self.health > 0 and target.ID == self.ID and target != self:
			print("A friendly minion dies and Spirit of the Bat gives a random minion in player's hand +1/+1.")
			minionsinHand = []
			for card in self.Game.Hand_Deck.hands[self.ID]:
				if card.cardType == "Minion":
					minionsinHand.append(card)
					
			if minionsinHand != []:
				np.random.choice(minionsinHand).buffDebuff(1, 1)
				
		
class Soulwarden(Minion):
	Class, race, name = "Warlock", "", "Soulwarden"
	mana, attack, health = 6, 6, 6
	index = "Rumble~Warlock~Minion~6~6~6~None~Soulwarden~Battlecry"
	needTarget, keyWord, description = False, "", "Battlecry: Add 3 random cards you discarded this game to your hand"
	def effectCanTrigger(self):
		self.effectViable = self.Game.CounterHandler.cardsDiscardedThisGame[self.ID] != []
		
	def whenEffective(self, target=None, comment="", choice=0):
		numAdd = min(3, self.Game.Hand_Deck.spaceinHand(self.ID), len(self.Game.CounterHandler.cardsDiscardedThisGame[self.ID]))
		if numAdd > 0:
			cardstoAdd = np.random.choice(self.Game.CounterHandler.cardsDiscardedThisGame[self.ID], numAdd, replace=False)
			self.Game.Hand_Deck.addCardtoHand(cardstoAdd, numAdd, comment="CreateUsingIndex")
		return None
		
#For now, assume half of the decks is rounded down.
class VoidContract(Spell):
	Class, name = "Warlock", "Void Contract"
	needTarget, mana = False, 8
	index = "Rumble~Warlock~Spell~8~Void Contract"
	description = "Destroy half of each player's deck"
	def whenEffective(self, target=None, comment="", choice=0):
		print("Void Contract is cast and destroys half of each player's deck.")
		for ID in range(1, 3):
			deckSize = len(self.Game.Hand_Deck.decks[ID])
			numDestroy = int(deckSize / 2)
			if numDestroy > 0:
				cardstoRemove = np.random.choice(self.Game.Hand_Deck.decks[ID], numDestroy, replace=False)
				self.Game.Hand_Deck.extractfromDeck(cardstoRemove)
		return None
		
		
class HighPriestessJeklik(Minion):
	Class, race, name = "Warlock", "", "High Priestess Jeklik"
	mana, attack, health = 4, 3, 4
	index = "Rumble~Warlock~Minion~4~3~4~None~High Priestess Jeklik~Taunt~Lifesteal~Legendary"
	needTarget, keyWord, description = False, "Taunt,Lifesteal", "Taunt, Lifesteal. When you discard this, add 2 copies of it to your hand"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggers["Discarded"] = [self.addTwoHighPriestessJeklikstoHand]
		
	def addTwoHighPriestessJeklikstoHand(self):
		Copy1 = self.selfCopy(self.ID)
		Copy2 = self.selfCopy(self.ID)
		print("When discarded, High Priestess Jeklik adds two copies of itself into player's hand.")
		self.Game.Hand_Deck.addCardtoHand([Copy1, Copy2], self.ID)
		
		
class HireektheBat(Minion):
	Class, race, name = "Warlock", "Beast", "Hir'eek. the Bat"
	mana, attack, health = 8, 1, 1
	index = "Rumble~Warlock~Minion~8~1~1~Beast~Hir'eek. the Bat~Battlecries~Legendary"
	needTarget, keyWord, description = False, "", "Battlecry: Fill your board wit copies of this minion"
	
	def whenEffective(self, target=None, comment="", choice=0):
		print("Hir'eek. the Bat's battlecry fills the board with the minion's copies.")
		copies = [self.selfCopy(self.ID) for i in range(self.Game.spaceonBoard(self.ID))]
		if self.onBoard:
			self.Game.summonMinion(copies, (self.position, "totheRight"), self.ID)
		else:
			self.Game.summonMinion(copies, (-1, "totheRightEnd"), self.ID)
		return None
		
"""Warrior cards"""
class Devastate(Spell):
	Class, name = "Warrior", "Devastate"
	needTarget, mana = True, 1
	index = "Rumble~Warrior~Spell~1~Devastate"
	description = "Deal 4 damage to a damaged minion"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.health < target.health_upper and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			damage = (4 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			print("Devastate is cast and deals %d damage to damaged minion "%damage, target.name)
			self.dealsDamage(target, damage)
		return target
		
		
class DragonRoar(Spell):
	Class, name = "Warrior", "Dragon Roar"
	needTarget, mana = False, 2
	index = "Rumble~Warrior~Spell~2~Dragon Roar"
	description = "Add two random Dragons to your hand"
	poolIdentifier = "Dragons"
	@classmethod
	def generatePool(cls, Game):
		return "Dragons", list(Game.MinionswithRace["Dragon"].values())
		
	def whenEffective(self, target=None, comment="", choice=0):
		print("Dragon Roar is cast and adds two random Dragons to player's hand.")
		dragons = np.random.choice(self.Game.RNGPools["Dragons"], 2, replace=True)
		self.Game.Hand_Deck.addCardtoHand(dragons, self.ID, "CreateUsingType")
		return None
		
		
class OverlordsWhip(Weapon):
	Class, name, description = "Warrior", "Overlord's Whip", "After you play a minion, deal 1 damage to it"
	mana, attack, durability = 3, 2, 4
	index = "Rumble~Warrior~Weapon~3~2~4~Overlord's Whip"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_OverlordsWhip(self)]
		
class Trigger_OverlordsWhip(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionBeenPlayed"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		#Can only buff if there is still durability left
		return subject.ID == self.entity.ID and self.entity.onBoard
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("After player plays minion %s, %s deals 1 damage to it."%(subject.name, self.entity.name))
		self.entity.dealsDamage(subject, 1)
		
		
#This minion has aura. The Rush minion summoned before this minion can also have Immune.
class SpiritoftheRhino(Minion):
	Class, race, name = "Warrior", "", "Spirit of the Rhino"
	mana, attack, health = 1, 0, 3
	index = "Rumble~Warrior~Minion~1~0~3~None~Spirit of the Rhino"
	needTarget, keyWord, description = False, "", "Stealth for 1 turn. You Rush minions are Immune the turn they are summoned"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.marks["Temp Stealth"] = 1
	#	self.appearResponse = [self.activateAura]
	#	self.disappearResponse = [self.deactivateAura]
	#	self.silenceResponse = [self.removeEffect]
	#	
	#def giveSummonFriendlyRushMinionsImmuneThisTurn(self, subject):
	#	if self.onBoard and self.health > 0 and subject.ID == self.ID and "Beast" in subject.race:
	#		print("Player summons a Beast and Spirit of the Lynx gives it +1/+1.")
	#		subject.buffDebuff(1, 1)
	#		
	#def activateAura(self):
	#	print("Spirit of the Rhino appears and connects listener for player summoning a Beast.")
	#	dispatcher.connect(self.giveSummonedBeastPlus1Plus1, "MinionSummoned", sender=self.Game)
	#	dispatcher.connect(self.giveSummonedBeastPlus1Plus1, "MinionPlayed", sender=self.Game)
	#	
	#def deactivateAura(self):
	#	print("Spirit of the Rhino disconnects listener for player summoning a Beast.")
	#	dispatcher.disconnect(self.giveSummonedBeastPlus1Plus1, "MinionSummoned", sender=self.Game)
	#	dispatcher.disconnect(self.giveSummonedBeastPlus1Plus1, "MinionPlayed", sender=self.Game)
		
	#def removeEffect(self):
	#	self.disconnectListeners()
	#	extractfrom(self.connectListeners, self.appearResponse)
	#	extractfrom(self.disconnectListeners, self.disappearResponse)
	#	extractfrom(self.removeEffect, self.silenceResponse)
		
		
class EmberscaleDrake(Minion):
	Class, race, name = "Warrior", "Dragon", "Emberscale Drake"
	mana, attack, health = 5, 5, 5
	index = "Rumble~Warrior~Minion~5~5~5~Dragon~Emberscale Drake~Battlecry"
	needTarget, keyWord, description = False, "", "Battlecry: If you're holding a Dragon, gain 5 Armor"
	
	def effectCanTrigger(self):
		self.effectViable = self.Game.Hand_Deck.holdingDragon(self.ID, self)
		
	def whenEffective(self, target=None, comment="", choice=0):
		if self.Game.Hand_Deck.holdingDragon(self.ID):
			print("Emberscale Drake's battlecry player gains 5 armor.")
			self.Game.heroes[self.ID].gainsArmor(5)
		return None
		
		
class HeavyMetal(Spell):
	Class, name = "Warrior", "Heavy Metal!"
	needTarget, mana = False, 6
	index = "Rumble~Warrior~Spell~6~Heavy Metal!"
	description = "Summon a random minion with Cost equal to your Armor (up to 10)"
	poolIdentifier = "1-Cost Minions"
	@classmethod
	def generatePool(cls, Game):
		costs, lists = [], []
		for cost in Game.MinionsofCost.keys():
			costs.append("%d-Cost Minions"%cost)
			lists.append(list(Game.MinionsofCost[cost].values()))
		return costs, lists
		
	def whenEffective(self, target=None, comment="", choice=0):
		print("Heavy Metal! is cast and summons a random minion with cost equal to player's armor.(Up to 10)")
		key = "%d-Cost Minions"%min(10, self.Game.heroes[self.ID].armor)
		self.Game.summonMinion(np.random.choice(self.Game.RNGPools[key])(self.Game, self.ID), -1, self.ID)
		return None
		
		
class SmolderthornLancer(Minion):
	Class, race, name = "Warrior", "", "Smolderthorn Lancer"
	mana, attack, health = 3, 3, 2
	index = "Rumble~Warrior~Minion~3~3~2~None~Smolderthorn Lancer~Battlecry"
	needTarget, keyWord, description = True, "", "Battlecry: If you are holding a Dragon, destroy a damaged enemy minion"
	
	def effectCanTrigger(self):
		self.effectViable = self.Game.Hand_Deck.holdingDragon(self.ID)
		
	def targetExists(self, choice=0):
		return self.selectableEnemyMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.ID != self.ID and target.health < target.health_upper and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None and self.Game.Hand_Deck.holdingDragon(self.ID):
			print("Smolderthorn Lancer's battlecry destroys damaged minion", target.name)
			target.dead = True
		return target
		
#Need to test if this can triggered by minion killed by attack its owner because of Misdirection
#Need to test if this is compatible with Windfury weapon
#Need to test if this effect goes away if switch weapon.
class Sulthraze(Weapon):
	Class, name = "Warrior", "Sul'thraze"
	mana, attack, durability = 6, 4, 4
	index = "Rumble~Warrior~Weapon~6~4~4~Sul'thraze~Overkill"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggers["Damage"] = [self.giveHeroAnotherAttackChance]
		
	#def giveHeroAnotherAttackChance(self, target, damage, targetSurvival):
	#	if targetSurvival > 2:
	#		self.Game.heroes[self.ID].attackChances += 1
		
		
class WarMasterVoone(Minion):
	Class, race, name = "Warrior", "", "War Master Voone"
	mana, attack, health = 4, 4, 3
	index = "Rumble~Warrior~Minion~4~4~3~None~War Master Voone~Battlecry~Legendary"
	needTarget, keyWord, description = False, "", "Battlecry: Copy all Dragons in your hand"
	def effectCanTrigger(self):
		self.effectViable = self.Game.Hand_Deck.holdingDragon(self.ID)
		
	def whenEffective(self, target=None, comment="", choice=0):
		if self.Game.Hand_Deck.handNotFull(self.ID):
			dragonsinHand = []
			for card in self.Game.Hand_Deck.hands[self.ID]:
				if card.cardType == "Minion" and "Dragon" in card.race:
					dragonsinHand.append(card)
					
			for dragon in dragonsinHand:
				if self.Game.Hand_Deck.handNotFull(self.ID):
					self.Game.Hand_Deck.addCardtoHand(dragon.selfCopy(self.ID), self.ID)
				else:
					break
		return None
		
		
class AkalitheRhino(Minion):
	Class, race, name = "Warrior", "Beast", "Akali. the Rhino"
	mana, attack, health = 8, 5, 5
	index = "Rumble~Warrior~Minion~8~5~5~Beast~Akali. the Rhino~Rush~Overkill~Legendary"
	needTarget, keyWord, description = False, "Rush", "Rush. Overkill: Draw a Rush minion from your deck. Give it +5/+5"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [(self)]
		
	def drawaRushMinionfromDeckGiveitPlus5Plus5(self, targets, damagesDone, survivals):
		if type(targets) == type([]):
			numOverkills = 0
			for survival in survivals:
				if survival > 2:
					numOverkills += 1
					
			for i in range(numOverkills):
				RushMinionsinDeck = []
				for card in self.Game.Hand_Deck.decks[self.ID]:
					if card.cardType == "Minion" and card.keyWords["Rush"] > 0:
						RushMinionsinDeck.append(card)
						
				if RushMinionsinDeck != []:
					card = self.Game.Hand_Deck.drawCard(self.ID, np.random.choice(RushMinionsinDeck))
					if card != None:
						card.buffDebuff(5, 5)
				else: #Stop the cycle if there is no Rush minions left.
					break
		else: #Killing a single target
			if survivals > 2:
				RushMinionsinDeck = []
				for card in self.Game.Hand_Deck.decks[self.ID]:
					if card.cardType == "Minion" and card.keyWords["Rush"] > 0:
						RushMinionsinDeck.append(card)
						
				if RushMinionsinDeck != []:
					card = self.Game.Hand_Deck.drawCard(self.ID, np.random.choice(RushMinionsinDeck))
					if card != None:
						card.buffDebuff(5, 5)