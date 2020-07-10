from CardTypes import *
from Triggers_Auras import *
from VariousHandlers import *
from Basic import Trigger_Corruption

from numpy.random import choice as npchoice
from numpy.random import randint as nprandint
from numpy.random import shuffle as npshuffle

def extractfrom(target, listObject):
	try: return listObject.pop(listObject.index(target))
	except: return None
	
def fixedList(listObject):
	return listObject[0:len(listObject)]
	
def PRINT(game, string, *args):
	if game.GUI:
		if not game.mode: game.GUI.printInfo(string)
	elif not game.mode: print("game's guide mode is 0\n", string)
	
"""mana 0 minion"""
class Wisp(Minion):
	Class, race, name = "Neutral", "", "Wisp"
	mana, attack, health = 0, 1, 1
	index = "Classic~Neutral~Minion~0~1~1~None~Wisp"
	requireTarget, keyWord, description = False, "", ""
	
"""mana 1 minions"""
class AbusiveSergeant(Minion):
	Class, race, name = "Neutral", "", "Abusive Sergeant"
	mana, attack, health = 1, 1, 1
	index = "Classic~Neutral~Minion~1~1~1~None~Abusive Sergeant~Battlecry"
	requireTarget, keyWord, description = True, "", "Give a minion +2 Attack this turn"
	
	def targetExists(self, choice=0):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target != self and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			PRINT(self.Game, "Abusive Sergeant's battlecry gives minion %s +2 attack this turn."%target.name)
			target.buffDebuff(2, 0, "EndofTurn")
		return target
		
		
class ArgentSquire(Minion):
	Class, race, name = "Neutral", "", "Argent Squire"
	mana, attack, health = 1, 1, 1
	index = "Classic~Neutral~Minion~1~1~1~None~Argent Squire~Divine Shield"
	requireTarget, keyWord, description = False, "Divine Shield", "Divine Shield"
	
	
class AngryChicken(Minion):
	Class, race, name = "Neutral", "Beast", "Angry Chicken"
	mana, attack, health = 1, 1, 1
	index = "Classic~Neutral~Minion~1~1~1~Beast~Angry Chicken"
	requireTarget, keyWord, description = False, "", "Has +5 Attack while damaged"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.auras["Enrage"] = BuffAura_Dealer_Enrage(self, 5)
		self.triggers["StatChanges"] = [self.handleEnrage]
		self.activated = False
		
	def handleEnrage(self):
		self.auras["Enrage"].handleEnrage()
		
		
class BloodsailCorsair(Minion):
	Class, race, name = "Neutral", "Pirate", "Bloodsail Corsair"
	mana, attack, health = 1, 1, 2
	index = "Classic~Neutral~Minion~1~1~2~Pirate~Bloodsail Corsair~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Remove 1 Durability from your opponent's weapon"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		weapon = self.Game.availableWeapon(3-self.ID)
		if weapon:
			PRINT(self.Game, "Bloodsail Corsair's battlecry removes 1 Durability from opponent's weapon.")
			weapon.loseDurability()
		return None
		
		
class HungryCrab(Minion):
	Class, race, name = "Neutral", "Beast", "Hungry Crab"
	mana, attack, health = 1, 1, 2
	index = "Classic~Neutral~Minion~1~1~2~Beast~Hungry Crab~Battlecry"
	requireTarget, keyWord, description = True, "", "Battlecry: Destroy a Murloc and gain +2/+2"
	
	def targetExists(self, choice=0):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and "Murloc" in target.race and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			PRINT(self.Game, "Hungry Crab's battlecry destroys Murloc %s and gives minion +2/+2."%target.name)
			if target.onBoard:
				target.dead = True
				self.buffDebuff(2, 2)
			elif target.inHand:
				self.Game.Hand_Deck.discardCard(target.ID, target)
				self.buffDebuff(2, 2)
			elif target.dead:
				self.buffDebuff(2, 2)
		return target
		
		
class LeperGnome(Minion):
	Class, race, name = "Neutral", "", "Leper Gnome"
	mana, attack, health = 1, 1, 1
	index = "Classic~Neutral~Minion~1~1~1~None~Leper Gnome~Deathrattle"
	requireTarget, keyWord, description = False, "", "Deathrattle: Deal 2 damage to the enemy hero"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [Deal2DamagetoEnemyHero(self)]
		
class Deal2DamagetoEnemyHero(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self.entity.Game, "Deathrattle: Deal 2 damage to the enemy hero triggers")
		self.entity.dealsDamage(self.entity.Game.heroes[3-self.entity.ID], 2)
		
		
class Lightwarden(Minion):
	Class, race, name = "Neutral", "", "Lightwarden"
	mana, attack, health = 1, 1, 2
	index = "Classic~Neutral~Minion~1~1~2~None~Lightwarden"
	requireTarget, keyWord, description = False, "", "Whenever a character is healed, gain +2 Attack"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_LightWarden(self)]
		
class Trigger_LightWarden(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionGetsHealed", "HeroGetsHealed"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self.entity.Game, "A character is healed and %s gains +2 attack."%self.entity.name)
		self.entity.buffDebuff(2, 0)
		
		
class MurlocTidecaller(Minion):
	Class, race, name = "Neutral", "Murloc", "Murloc Tidecaller"
	mana, attack, health = 1, 1, 2
	index = "Classic~Neutral~Minion~1~1~2~Murloc~Murloc Tidecaller"
	requireTarget, keyWord, description = False, "", "Whenever you summon a Murloc, gain +1 Attack"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_MurlocTidecaller(self)]
		
class Trigger_MurlocTidecaller(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionSummoned"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject.ID == self.entity.ID and "Murloc" in subject.race and subject != self.entity
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self.entity.Game, "A friendly Murloc %s is summoned and %s gains +1 attack."%(subject.name, self.entity.name))
		self.entity.buffDebuff(1, 0)
		
#When the secret is countered by the Couterspell, Secretkeeper doesn't respond.
#Neither does Questing Adventurer.
class Secretkeeper(Minion):
	Class, race, name = "Neutral", "", "Secretkeeper"
	mana, attack, health = 1, 1, 2
	index = "Classic~Neutral~Minion~1~1~2~None~Secretkeeper"
	requireTarget, keyWord, description = False, "", "Whenever a Secret is played, gain +1/+1"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_Secretkeeper(self)]
		
class Trigger_Secretkeeper(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["SpellPlayed"])
		
	#Assume Secretkeeper and trigger while dying.
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and "~~Secret" in subject.index
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self.entity.Game, "A Secret is played and %s gains 1/+1."%self.entity.name)
		self.entity.buffDebuff(1, 1)
		
		
class Shieldbearer(Minion):
	Class, race, name = "Neutral", "", "Shieldbearer"
	mana, attack, health = 1, 0, 4
	index = "Classic~Neutral~Minion~1~0~4~None~Shieldbearer~Taunt"
	requireTarget, keyWord, description = False, "Taunt", "Taunt"
	
	
class SouthseaDeckhand(Minion):
	Class, race, name = "Neutral", "Pirate", "Southsea Deckhand"
	mana, attack, health = 1, 2, 1
	index = "Classic~Neutral~Minion~1~2~1~Pirate~Southsea Deckhand"
	requireTarget, keyWord, description = False, "", "Has Charge while you have a weapon equipped"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.auras["Self Charge"] = SouthseaDeckhand_Dealer(self)
		
class SouthseaDeckhand_Dealer(AuraDealer_toMinion):
	def __init__(self, entity):
		self.entity = entity #For now, there are only three minions that provide this kind aura: Tundra Rhino, Houndmaster Shaw, Whirlwind Tempest
		self.signals, self.auraAffected = ["WeaponEquipped", "WeaponRemoved"], []
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		if self.entity.onBoard:
			return (signal == "WeaponEquipped" and subject.ID == self.entity.ID) or (signal == "WeaponRemoved" and target.ID == self.entity.ID)
		return False
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.applies(self.entity)
		
	def applies(self, subject):
		if subject.Game.availableWeapon(subject.ID):
			aura_Receiver = HasAura_Receiver(subject, self, "Charge")
			aura_Receiver.effectStart()
		else:
			for minion, aura_Receiver in self.auraAffected:
				aura_Receiver.effectClear()
				
	def auraAppears(self):
		self.applies(self.entity)
		for signal in self.signals:
			self.entity.Game.triggersonBoard[self.entity.ID].append((self, signal))
			
	def selfCopy(self, recipientMinion):
		return type(self)(recipientMinion)
	#可以通过AuraDealer_toMinion的createCopy方法复制
	
	
class WorgenInfiltrator(Minion):
	Class, race, name = "Neutral", "", "Worgen Infiltrator"
	mana, attack, health = 1, 2, 1
	index = "Classic~Neutral~Minion~1~2~1~None~Worgen Infiltrator~Stealth"
	requireTarget, keyWord, description = False, "Stealth", "Stealth"
	
	
class YoungDragonhawk(Minion):
	Class, race, name = "Neutral", "Beast", "Young Dragonhawk"
	mana, attack, health = 1, 1, 1
	index = "Classic~Neutral~Minion~1~1~1~Beast~Young Dragonhawk~Windfury"
	requireTarget, keyWord, description = False, "Windfury", "Windfury"
	
	
class YoungPriestess(Minion):
	Class, race, name = "Neutral", "", "Young Priestess"
	mana, attack, health = 1, 2, 1
	index = "Classic~Neutral~Minion~1~2~1~None~Young Priestess"
	requireTarget, keyWord, description = False, "", "At the end of your turn, give another random friendly minion +1 Health"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_YoungPriestess(self)]
		
class Trigger_YoungPriestess(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["TurnEnds"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		curGame = self.entity.Game
		if curGame.mode == 0:
			if curGame.guides:
				i = curGame.guides.pop(0)
				if i < 0: return
				else: minion = curGame.minions[self.entity.ID][i]
			else:
				minions = curGame.minionsonBoard(self.entity.ID)
				extractfrom(self.entity, minions)
				if minions:
					minion = npchoice(minions)
					curGame.fixedGuides.append(minion.position)
				else:
					curGame.fixedGuides.append(-1)
					return
			PRINT(curGame, "At the end of turn, Young Priestess gvies another random friendly minion %s +1 Health."%minion.name)
			minion.buffDebuff(0, 1)
			
"""mana 2 minions"""
class AmaniBerserker(Minion):
	Class, race, name = "Neutral", "", "Amani Berserker"
	mana, attack, health = 2, 2, 3
	index = "Classic~Neutral~Minion~2~2~3~None~Amani Berserker"
	requireTarget, keyWord, description = False, "", "Has +3 Attack while damaged"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.auras["Enrage"] = BuffAura_Dealer_Enrage(self, 3)
		self.triggers["StatChanges"] = [self.handleEnrage]
		self.activated = False
		
	def handleEnrage(self):
		self.auras["Enrage"].handleEnrage()
		
		
class AncientWatcher(Minion):
	Class, race, name = "Neutral", "", "Ancient Watcher"
	mana, attack, health = 2, 4, 5
	index = "Classic~Neutral~Minion~2~4~5~None~Ancient Watcher"
	requireTarget, keyWord, description = False, "", "Can't Attack"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.marks["Can't Attack"] = 1
		
		
class BloodmageThalnos(Minion):
	Class, race, name = "Neutral", "", "Bloodmage Thalnos"
	mana, attack, health = 2, 1, 1
	index = "Classic~Neutral~Minion~2~1~1~None~Bloodmage Thalnos~Deathrattle~Spell Damage~Legendary"
	requireTarget, keyWord, description = False, "Spell Damage", "Spell Damage +1. Deathrattle: Draw a card"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [DrawaCard(self)]
		
class DrawaCard(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self.entity.Game, "Deathrattle: Draw a card triggers.")
		self.entity.Game.Hand_Deck.drawCard(self.entity.ID)
		
		
class BloodsailRaider(Minion):
	Class, race, name = "Neutral", "Pirate", "Bloodsail Raider"
	mana, attack, health = 2, 2, 3
	index = "Classic~Neutral~Minion~2~2~3~Pirate~Bloodsail Raider~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Gain Attack equal to the Attack of your weapon"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		weapon = self.Game.availableWeapon(self.ID)
		if weapon:
			PRINT(self.Game, "Bloodsail Raider's battlecry lets minion gain the Attack equal to the Attack of player's weapon.")
			self.buffDebuff(weapon.attack, 0)
		return None
		
		
class CrazedAlchemist(Minion):
	Class, race, name = "Neutral", "", "Crazed Alchemist"
	mana, attack, health = 2, 2, 2
	index = "Classic~Neutral~Minion~2~2~2~None~Crazed Alchemist~Battlecry"
	requireTarget, keyWord, description = True, "", "Battlecry: Swap the Attack and Health of a minion"
	
	def targetExists(self, choice=0):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target != self and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			PRINT(self.Game, "Crazed Alchemist's battlecry swaps minion %s's attack/health."%target.name)
			target.statReset(target.health, target.attack)
		return target
		
		
class DireWolfAlpha(Minion):
	Class, race, name = "Neutral", "Beast", "Dire Wolf Alpha"
	mana, attack, health = 2, 2, 2
	index = "Classic~Neutral~Minion~2~2~2~Beast~Dire Wolf Alpha"
	requireTarget, keyWord, description = False, "", "Adjacent minions have +1 Attack"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.auras["Buff Aura"] = BuffAura_Dealer_Adjacent(self, 1, 0)
		
		
class Doomsayer(Minion):
	Class, race, name = "Neutral", "", "Doomsayer"
	mana, attack, health = 2, 0, 7
	index = "Classic~Neutral~Minion~2~0~7~None~Doomsayer"
	requireTarget, keyWord, description = False, "", "At the start of your turn, destroy ALL minions"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_Doomsayer(self)]
		
class Trigger_Doomsayer(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["TurnStarts"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self.entity.Game, "At the start of turn, %s destroys all minions"%self.entity.name)
		for minion in self.entity.Game.minionsonBoard(1) + self.entity.Game.minionsonBoard(2):
			minion.dead = True
			
			
class FaerieDragon(Minion):
	Class, race, name = "Neutral", "Dragon", "Faerie Dragon"
	mana, attack, health = 2, 3, 2
	index = "Classic~Neutral~Minion~2~3~2~Dragon~Faerie Dragon"
	requireTarget, keyWord, description = False, "", "Can't be targeted by spells or Hero Powers"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.marks["Evasive"] = 1
		
		
#For a target spell/battlecry, if the above resolution kills the minion before it can take effect, the targeting part is simply wasted and 
#the following effect will still trigger.
#For example, if the minion before Mortal Coil is cast on it. The Mortal Coil still lets player draw a card.
#Another example, if the spell is Dire Frenzy, there will still be 3 copes to be shuffled..
class KnifeJuggler(Minion):
	Class, race, name = "Neutral", "", "Knife Juggler"
	mana, attack, health = 2, 2, 2
	index = "Classic~Neutral~Minion~2~2~2~None~Knife Juggler"
	requireTarget, keyWord, description = False, "", "After you summon a minion, deal 1 damage to a random enemy"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_KnifeJuggler(self)]
		
class Trigger_KnifeJuggler(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionBeenSummoned"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject.ID == self.entity.ID and subject != self.entity
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		curGame = self.entity.Game
		if curGame.mode == 0:
			if curGame.guides:
				i, where = curGame.guides.pop(0)
				if where: target = curGame.find(i, where)
				else: return
			else:
				chars = curGame.charsAlive(3-self.entity.ID)
				if chars:
					char = npchoice(chars)
					curGame.fixedGuides.append((char.position, "minion%d"%char.ID) if char.type == "Minion" else (char.ID, "hero"))
				else:
					curGame.fixedGuides.append((0, ''))
					return
			PRINT(curGame, "A friendly minion %s is summoned and Knife Juggler deals 1 damage to random enemy %s"%(subject.name, target.name))
			self.entity.dealsDamage(target, 1)
			
			
class LootHoarder(Minion):
	Class, race, name = "Neutral", "", "Loot Hoarder"
	mana, attack, health = 2, 2, 1
	index = "Classic~Neutral~Minion~2~2~1~None~Loot Hoarder~Deathrattle"
	requireTarget, keyWord, description = False, "", "Deathrattle: Draw a card"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [DrawaCard(self)] #This deathrattle obj defined in Bloodmage Thalnos.
		
		
class LorewalkerCho(Minion):
	Class, race, name = "Neutral", "", "Lorewalker Cho"
	mana, attack, health = 2, 0, 4
	index = "Classic~Neutral~Minion~2~0~4~None~Lorewalker Cho~Legendary"
	requireTarget, keyWord = False, ""
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_LorewalkerCho(self)]
		
class Trigger_LorewalkerCho(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["SpellPlayed"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self.entity.Game, "Spell %s is cast and Lorewalker Cho gives the other player a copy of it"%subject.name)
		card = type(subject)(self.entity.Game, 3-subject.ID)
		self.entity.Game.Hand_Deck.addCardtoHand(card, 3-subject.ID)
		
		
class MadBomber(Minion):
	Class, race, name = "Neutral", "", "Mad Bomber"
	mana, attack, health = 2, 3, 2
	index = "Classic~Neutral~Minion~2~3~2~None~Mad Bomber~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Deal 3 damage randomly split among all other characters"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if curGame.mode == 0:
			PRINT(curGame, "Mad Bomber's battlecry deals 3 damage randomly split among other characters.")
			for i in range(3):
				if curGame.guides:
					i, where = curGame.guides.pop(0)
					if where: char = curGame.find(i, where)					
					else: break
				else:
					objs = curGame.charsAlive(self.ID, self) + curGame.charsAlive(3-self.ID)
					if objs:
						char = npchoice(objs)
						curGame.fixedGuides.append((char.ID, "hero") if char.type == "Hero" else (char.position, "minion%d"%char.ID))
					else:
						curGame.fixedGuides.append((0, ''))
						return None
				PRINT(curGame, "Mad Bomber deals 1 damage to %s"%char.name)
				self.dealsDamage(char, 1)
		return None
		
		
class ManaAddict(Minion):
	Class, race, name = "Neutral", "", "Mana Addict"
	mana, attack, health = 2, 1, 3
	index = "Classic~Neutral~Minion~2~1~3~None~Mana Addict"
	requireTarget, keyWord, description = False, "", "Whenever you cast a spell, gain +2 Attack this turn"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_ManaAddict(self)]
		
class Trigger_ManaAddict(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["SpellPlayed"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject.ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self.entity.Game, "Player casts a spell and Mana Addict gains +2 attack this turn.")
		self.entity.buffDebuff(2, 0, "EndofTurn")
		
		
class ManaWraith(Minion):
	Class, race, name = "Neutral", "", "Mana Wraith"
	mana, attack, health = 2, 2, 2
	index = "Classic~Neutral~Minion~2~2~2~None~Mana Wraith"
	requireTarget, keyWord, description = False, "", "ALL minions cost (1) more"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.auras["Mana Aura"] = ManaAura_Dealer(self, changeby=+1, changeto=-1)
		
	def manaAuraApplicable(self, subject):
		return subject.type == "Minion"
		
		
class MasterSwordsmith(Minion):
	Class, race, name = "Neutral", "", "Master Swordsmith"
	mana, attack, health = 2, 1, 3
	index = "Classic~Neutral~Minion~2~1~3~None~Master Swordsmith"
	requireTarget, keyWord, description = False, "", "At the end of your turn, give another random friendly minion +1 Attack"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_MasterSwordsmith(self)]
		
class Trigger_MasterSwordsmith(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["TurnEnds"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		curGame = self.entity.Game
		if curGame.mode == 0:
			if curGame.guides:
				i = curGame.guides.pop(0)
				if i < 0: return
				else: minion = curGame.minions[self.entity.ID][i]
			else:
				minions = curGame.minionsonBoard(self.entity.ID)
				extractfrom(self.entity, minions)
				if minions:
					minion = npchoice(minions)
					curGame.fixedGuides.append(minion.position)
				else:
					curGame.fixedGuides.append(-1)
					return
			PRINT(curGame, "At the end of turn, Master Swordsmith gvies another random friendly minion %s +1 Attack."%minion.name)
			minion.buffDebuff(1, 0)
				
				
#不同于洛欧塞布，米尔豪斯的法力值会在战吼之后马上生效。
class MillhouseManastorm(Minion):
	Class, race, name = "Neutral", "", "Millhouse Manastorm"
	mana, attack, health = 2, 4, 4
	index = "Classic~Neutral~Minion~2~4~4~None~Millhouse Manastorm~Battlecry~Legendary"
	requireTarget, keyWord, description = False, "", "Battlecry: Your opponent's spells cost (0) next turn"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		PRINT(self.Game, "Millhouse Manastorm's battlecry makes enemy spells cost 0 next turn.")
		tempAura = SpellsCost0NextTurn(self.Game, 3-self.ID)
		self.Game.Manas.CardAuras.append(tempAura)
		tempAura.auraAppears()
		return None
		
class SpellsCost0NextTurn(TempManaEffect):
	def __init__(self, Game, ID):
		self.Game, self.ID = Game, ID
		self.changeby, self.changeto = 0, 0
		self.temporary = True
		self.auraAffected = []
		
	def applicable(self, target):
		return target.ID == self.ID and target.type == "Spell"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.applies(target[0])
	#持续整个回合的光环可以不必注册"ManaCostPaid"
	def auraAppears(self):
		for card in self.Game.Hand_Deck.hands[1] + self.Game.Hand_Deck.hands[2]:
			self.applies(card)
		self.Game.triggersonBoard[self.ID].append((self, "CardEntersHand"))
		self.Game.Manas.calcMana_All()
	#auraDisappears()可以尝试移除ManaCostPaid，当然没有反应，所以不必专门定义
	def selfCopy(self, recipientGame):
		return type(self)(recipientGame, self.ID)
		
	
class NatPagle(Minion):
	Class, race, name = "Neutral", "", "Nat Pagle"
	mana, attack, health = 2, 0, 4
	index = "Classic~Neutral~Minion~2~0~4~None~Nat Pagle~Legendary"
	requireTarget, keyWord, description = False, "", "At the start of your turn, you have a 50% chance to draw an extra card"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_NatPagle(self)]
		
class Trigger_NatPagle(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["TurnStarts"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and ID == self.entity.ID
		
	#不确定纳特帕格是直接让玩家摸一张牌还是确定多摸之后在后续的抽牌阶段摸一张。
	#暂时假设是直接摸一张牌。
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		curGame = self.entity.Game
		if curGame.mode == 0:
			PRINT(self.entity.Game, "At the start of turn, Nat Pagle has 50% chance to lets player draw a card.")
			if curGame.guides:
				bitBait = curGame.guides.pop(0)
			else:
				bitBait = nprandint(2)
				curGame.fixedGuides.append(bitBait)
			if bitBait:
				PRINT(curGame, "Nat Pagle lets player draw a card.")
				curGame.Hand_Deck.drawCard(self.entity.ID)
				
				
class PintSizedSummoner(Minion):
	Class, race, name = "Neutral", "", "Pint-Sized Summoner"
	mana, attack, health = 2, 2, 2
	index = "Classic~Neutral~Minion~2~2~2~None~Pint-Sized Summoner"
	requireTarget, keyWord, description = False, "", "The first minion you play each turn costs (1) less"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.auras["Mana Aura"] = ManaAura_Dealer(self, changeby=-1, changeto=-1)
		self.triggersonBoard = [Trigger_PintsizedSummoner(self)]
		#随从的光环启动在顺序上早于appearResponse,关闭同样早于disappearResponse
		self.appearResponse = [self.checkAuraCorrectness]
		self.disappearResponse = [self.deactivateAura]
		self.silenceResponse = [self.deactivateAura]
		
	def manaAuraApplicable(self, target):
		return target.ID == self.ID and target.type == "Minion"
		
	def checkAuraCorrectness(self): #负责光环在随从登场时无条件启动之后的检测。如果光环的启动条件并没有达成，则关掉光环
		if self.Game.turn != self.ID or self.Game.Counters.numMinionsPlayedThisTurn[self.ID] != 0:
			PRINT(self.Game, "Pint-Sized Summoner's mana aura is incorrectly activated. It will be shut down")
			self.auras["Mana Aura"].auraDisappears()
			
	def deactivateAura(self): #随从被沉默时优先触发disappearResponse,提前关闭光环，之后auraDisappears可以再调用一次，但是没有作用而已
		PRINT(self.Game, "Pint-Sized Summoner's mana aura is removed. Player's first minion each turn no longer costs 1 less.")
		self.auras["Mana Aura"].auraDisappears()
		
class Trigger_PintsizedSummoner(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["TurnStarts", "TurnEnds", "ManaCostPaid"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		if "Turn" in signal and self.entity.onBoard and ID == self.entity.ID:
			return True
		if signal == "ManaCostPaid" and self.entity.onBoard and subject.type == "Minion" and subject.ID == self.entity.ID:
			return True
		return False
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		if "Turn" in signal: #回合开始结束时总会强制关闭然后启动一次光环。这样，即使回合开始或者结束发生了随从的控制变更等情况，依然可以保证光环的正确
			PRINT(self.entity.Game, "At the start of turn, %s restarts the mana aura and reduces the cost of the first minion by (1)."%self.entity.name)
			self.entity.auras["Mana Aura"].auraDisappears()
			self.entity.auras["Mana Aura"].auraAppears()
			self.entity.checkAuraCorrectness()
		else: #signal == "ManaCostPaid"
			self.entity.auras["Mana Aura"].auraDisappears()
			
			
class SunfuryProtector(Minion):
	Class, race, name = "Neutral", "", "Sunfury Protector"
	mana, attack, health = 2, 2, 2
	index = "Classic~Neutral~Minion~2~2~3~None~Sunfury Protector~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Give adjacent minions Taunt"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if self.onBoard: #只有在场的随从拥有相邻随从。
			targets, distribution = self.Game.adjacentMinions2(self)
			if targets != []:
				PRINT(self.Game, "Sunfury Protector's battlecry gives adjacent friendly minions Taunt.")
				for target in targets:
					target.getsKeyword("Taunt")
		return None
		
#Look into Electra Stormsurge and Casting spell on adjacent minions.
class WildPyromancer(Minion):
	Class, race, name = "Neutral", "", "Wild Pyromancer"
	mana, attack, health = 2, 3, 2
	index = "Classic~Neutral~Minion~2~3~2~None~Wild Pyromancer"
	requireTarget, keyWord, description = False, "", "After you cast a spell, deal 1 damage to ALL minions"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_WildPyromancer(self)]
		
class Trigger_WildPyromancer(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["SpellBeenPlayed"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject.ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self.entity.Game, "After player casts a spell, %s deals 1 damage to all minions."%self.entity.name)
		targets = self.entity.Game.minionsonBoard(1) + self.entity.Game.minionsonBoard(2)
		self.entity.dealsAOE(targets, [1 for minion in targets])
		
		
class YouthfulBrewmaster(Minion):
	Class, race, name = "Neutral", "", "Youthful Brewmaster"
	mana, attack, health = 2, 3, 2
	index = "Classic~Neutral~Minion~2~3~2~None~Youthful Brewmaster~Battlecry"
	requireTarget, keyWord, description = True, "", "Battlecry: Return a friendly minion from the battlefield to you hand"
	
	def targetExists(self, choice=0):
		return self.selectableFriendlyMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.ID == self.ID and target != self and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target and target.onBoard:
			PRINT(self.Game, "Youthful Brewmaster's battlecry returns friendly minion %s to player's hand."%target.name)
			self.Game.returnMiniontoHand(target)
		return target
		
"""mana 3 minions"""
class AlarmoBot(Minion):
	Class, race, name = "Neutral", "Mech", "Alarm-o-Bot"
	mana, attack, health = 3, 0, 3
	index = "Classic~Neutral~Minion~3~0~3~Mech~Alarm-o-Bot"
	requireTarget, keyWord, description = False, "", "At the start of your turn, swap this minion with a random one in your hand"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_AlarmoBot(self)]
		
class Trigger_AlarmoBot(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["TurnStarts"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		minion, curGame = self.entity, self.entity.Game
		ownHand = curGame.Hand_Deck.hands[self.entity.ID]
		if curGame.mode == 0:
			if curGame.guides:
				i = curGame.guides.pop(0)
				if i < 0: return
			else:
				minions = [i for i, card in enumerate(ownHand) if card.type == "Minion"]
				if minions:
					i = npchoice(minions)
					curGame.fixedGuides.append(i)
				else:
					curGame.fixedGuides.append(-1)
					return
			PRINT(curGame, "At the start of turn, Alarm-o-Bot swaps with random minion in player's hand")
			#需要先把报警机器人自己从场上移回手牌
			ID, identity, pos = minion.ID, minion.identity, minion.position
			minion.disappears(keepDeathrattlesRegistered=False)
			self.removeMinionorWeapon(minion)
			minion.__init__(self, ID)
			PRINT(curGame, "%s has been reset after returned to owner's hand. All enchantments lost."%minion.name)
			minion.identity[0], minion.identity[1] = identity[0], identity[1]
			#下面节选自Hand.py的addCardtoHand方法，但是要跳过手牌已满的检测
			ownHand.append(minion)
			minion.entersHand()
			curGame.sendSignal("CardEntersHand", minion, None, [minion], 0, "")
			#假设先发送牌进入手牌的信号，然后召唤随从
			curGame.summonfromHand(i, ID, pos, ID)
			
			
class ArcaneGolem(Minion):
	Class, race, name = "Neutral", "", "Arcane Golem"
	mana, attack, health = 3, 4, 4
	index = "Classic~Neutral~Minion~3~4~4~None~Arcane Golem~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Give your opponent a Mana Crystal"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		PRINT(self.Game, "Arcane Golem's battlecry gives opponent 1 mana crystal.")
		self.Game.Manas.gainManaCrystal(1, 3-self.ID)
		return None
		
		
class BloodKnight(Minion):
	Class, race, name = "Neutral", "", "Blood Knight"
	mana, attack, health = 3, 3, 3
	index = "Classic~Neutral~Minion~3~3~3~None~Blood Knight~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: All minions lose Divine Shield. Gain +3/+3 for each Shield lost"
	#仍视为随从连续两次施放战吼，但是第二次由于各随从的圣盾已经消失，所以可以在每一次战吼触发时检测是否有铜须光环的存在。
	#如果有铜须光环，则每一次战吼触发的时候就获得双倍buff
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		num = 0
		for minion in self.Game.minionsonBoard(1) + self.Game.minionsonBoard(2):
			if minion.keyWords["Divine Shield"] > 0:
				minion.losesKeyword("Divine Shield")
				num += 1
				
		if self.Game.status[self.ID]["Battlecry x2"] + self.Game.status[self.ID]["Shark Battlecry x2"] > 0 and comment != "byOthers":
			PRINT(self.Game, "Blood Knight's battlecry removes all Divine Shields and minion gains +6/+6 for each.")
			self.buffDebuff(6*num, 6*num)
		else:
			PRINT(self.Game, "Blood Knight's battlecry removes all Divine Shields and minion gains +3/+3 for each.")
			self.buffDebuff(3*num, 3*num)
		return None
		
		
class Brightwing(Minion):
	Class, race, name = "Neutral", "Dragon", "Brightwing"
	mana, attack, health = 3, 3, 2
	index = "Classic~Neutral~Minion~3~3~2~Dragon~Brightwing~Battlecry~Legendary"
	requireTarget, keyWord, description = False, "", "Battlecry: Add a random Legendary minion to your hand"
	poolIdentifier = "Legendary Minions"
	@classmethod
	def generatePool(cls, Game):
		return "Legendary Minions", list(Game.LegendaryMinions.values())
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if curGame.mode == 0:
			if curGame.guides:
				minion = curGame.guides.pop(0)
			else:
				minion = npchoice(curGame.RNGPools["Legendary Minions"])
				curGame.fixedGuides.append(minion)
			PRINT(curGame, "Brightwing's battlecry adds random Legendary minion to player's hand.")
			curGame.Hand_Deck.addCardtoHand(minion, self.ID, "CreateUsingType")
		return None
		
		
class ColdlightSeer(Minion):
	Class, race, name = "Neutral", "Murloc", "Coldlight Seer"
	mana, attack, health = 3, 2, 3
	index = "Classic~Neutral~Minion~3~2~3~Murloc~Coldlight Seer~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Give your other Murlocs +2 Health"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		PRINT(self.Game, "Coldlight Seer's battlecry gives all friendly murlocs +2 health.")
		for minion in self.Game.minionsonBoard(self.ID):
			if "Murloc" in minion.race: minion.buffDebuff(0, 2)
		return None
		
		
class Demolisher(Minion):
	Class, race, name = "Neutral", "Mech", "Demolisher"
	mana, attack, health = 3, 1, 4
	index = "Classic~Neutral~Minion~3~1~4~Mech~Demolisher"
	requireTarget, keyWord, description = False, "", "At the start of your turn, deal 2 damage to a random enemy"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_Demolisher(self)]
		
class Trigger_Demolisher(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["TurnStarts"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		curGame = self.entity.Game
		if curGame.mode == 0:
			if curGame.guides:
				i, where = curGame.guides.pop(0)
				if where: target = curGame.find(i, where)
				else: return
			else:
				targets = curGame.charsAlive(3-self.entity.ID)
				if targets:
					target = npchoice(targets)
					if target.type == "Minion": i, where = target.position, "minion%d"%target.ID
					else: i, where = target.ID, "hero"
					curGame.fixedGuides.append((i, where))
				else:
					curGame.fixedGuides.append((0, ''))
					return
			PRINT(curGame, "At the start of turn, Demolisher deals 1 damage to random enemy %s"%target.name)
			self.entity.dealsDamage(target, 2)
			
			
class EarthenRingFarseer(Minion):
	Class, race, name = "Neutral", "", "Earthen Ring Farseer"
	mana, attack, health = 3, 3, 3
	index = "Classic~Neutral~Minion~3~3~3~None~Earthen Ring Farseer~Battlecry"
	requireTarget, keyWord, description = True, "", "Battlecry: Restore 3 health"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			heal = 3 * (2 ** self.countHealDouble())
			PRINT(self.Game, "Earthen Ring Farseer's battlecry restores %d health to %s"%(heal, target.name))
			self.restoresHealth(target, heal)
		return target
		
		
class EmperorCobra(Minion):
	Class, race, name = "Neutral", "Beast", "Emperor Cobra"
	mana, attack, health = 3, 2, 3
	index = "Classic~Neutral~Minion~3~2~3~Beast~Emperor Cobra~Poisonous"
	requireTarget, keyWord, description = False, "Poisonous", "Poisonous"
	
	
class FlesheatingGhoul(Minion):
	Class, race, name = "Neutral", "", "Flesheating Ghoul"
	mana, attack, health = 3, 2, 3
	index = "Classic~Neutral~Minion~3~2~3~None~Flesheating Ghoul"
	requireTarget, keyWord, description = False, "", "Whenever a minion dies, gain +1 Attack"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_FlesheatingGhoul(self)]
		
class Trigger_FlesheatingGhoul(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionDies"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and target != self.entity #Technically, minion has to disappear before dies. But just in case.
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self.entity.Game, "A minion %s dies and %s gains +1 attack."%(target.name, self.entity.name))
		self.entity.buffDebuff(1, 0)
		
		
class HarvestGolem(Minion):
	Class, race, name = "Neutral", "Mech", "Harvest Golem"
	mana, attack, health = 3, 2, 3
	index = "Classic~Neutral~Minion~3~2~3~Mech~Harvest Golem~Deathrattle"
	requireTarget, keyWord, description = False, "", "Deathrattle: Summon a 2/1 Damaged Golem"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [SummonaDamagedGolem(self)]
		
class SummonaDamagedGolem(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self.entity.Game, "Deathrattle: Summon a 2/1 Damaged Golem triggers.")
		self.entity.Game.summon(DamagedGolem(self.entity.Game, self.entity.ID), self.entity.position+1, self.entity.ID)
		
class DamagedGolem(Minion):
	Class, race, name = "Neutral", "Mech", "Damaged Golem"
	mana, attack, health = 1, 2, 1
	index = "Classic~Neutral~Minion~1~2~1~Mech~Damaged Golem~Uncollectible"
	requireTarget, keyWord, description = False, "", ""
	
	
class ImpMaster(Minion):
	Class, race, name = "Neutral", "", "Imp Master"
	mana, attack, health = 3, 1, 5
	index = "Classic~Neutral~Minion~3~1~5~None~Imp Master"
	requireTarget, keyWord, description = False, "", "At the end of your turn, deal 1 damage to this minion and summon a 1/1 Imp"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_ImpMaster(self)]
		
class Trigger_ImpMaster(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["TurnEnds"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self.entity.Game, "At the end of turn, %s deals 1 damage to itself and summons a 1/1 Imp."%self.entity.name)
		self.entity.dealsDamage(self.entity, 1)
		self.entity.Game.summon(Imp(self.entity.Game, self.entity.ID), self.entity.position+1, self.entity.ID)
		
class Imp(Minion):
	Class, race, name = "Neutral", "Demon", "Imp"
	mana, attack, health = 1, 1, 1
	index = "Classic~Neutral~Minion~1~1~1~Demon~Imp~Uncollectible"
	requireTarget, keyWord, description = False, "", ""
	
	
class InjuredBlademaster(Minion):
	Class, race, name = "Neutral", "", "Injured Blademaster"
	mana, attack, health = 3, 4, 7
	index = "Classic~Neutral~Minion~3~4~7~None~Injured Blademaster~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Deal 4 damage to HIMSELF"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		PRINT(self.Game, "Injured Blademaster's battlecry deals 4 damage to the minion.")
		self.dealsDamage(self, 4)
		return None
		
		
class IronbeakOwl(Minion):
	Class, race, name = "Neutral", "Beast", "Ironbeak Owl"
	mana, attack, health = 3, 2, 1
	index = "Classic~Neutral~Minion~3~2~1~Beast~Ironbeak Owl~Battlecry"
	requireTarget, keyWord, description = True, "", "Battlecry: Silence a minion"
	
	def targetExists(self, choice=0):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target != self and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			PRINT(self.Game, "Ironbeak Owl's battlecry silences minion %s"%target.name)
			target.getsSilenced()
		return target
		
		
class JunglePanther(Minion):
	Class, race, name = "Neutral", "Beast", "Jungle Panther"
	mana, attack, health = 3, 4, 2
	index = "Classic~Neutral~Minion~3~4~2~Beast~Jungle Panther~Stealth"
	requireTarget, keyWord, description = False, "Stealth", "Stealth"
	
	
class KingMukla(Minion):
	Class, race, name = "Neutral", "Beast", "King Mukla"
	mana, attack, health = 3, 5, 5
	index = "Classic~Neutral~Minion~3~5~5~Beast~King Mukla~Battlecry~Legendary"
	requireTarget, keyWord, description = False, "", "Battlecry: Give your opponent 2 Bananas"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		PRINT(self.Game, "King Mukla's battlecry gives opponent two Bananas.")
		if self.Game.Hand_Deck.handNotFull(3-self.ID):
			self.Game.Hand_Deck.addCardtoHand([Bananas, Bananas], 3-self.ID, comment="CreateUsingType")
		return None
		
class Bananas(Spell):
	Class, name = "Neutral", "Bananas"
	requireTarget, mana = True, 1
	index = "Classic~Neutral~Spell~1~Bananas~Uncollectible"
	description = "Give a minion +1/+1"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			PRINT(self.Game, "Bananas is cast and gives minion %s +1/+1."%target.name)
			target.buffDebuff(1, 1)
		return target
		
		
class MurlocWarleader(Minion):
	Class, race, name = "Neutral", "Murloc", "Murloc Warleader"
	mana, attack, health = 3, 3, 3
	index = "Classic~Neutral~Minion~3~3~3~Murloc~Murloc Warleader"
	requireTarget, keyWord, description = False, "", "Your others Murlocs have +2 Attack"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.auras["Buff Aura"] = BuffAura_Dealer_All(self, 2, 0)
		
	def applicable(self, target):
		return "Murloc" in target.race
		
#Gains +1/+1 before friendly AOE takes effect.
class QuestingAdventurer(Minion):
	Class, race, name = "Neutral", "", "Questing Adventurer"
	mana, attack, health = 3, 2, 2
	index = "Classic~Neutral~Minion~3~2~2~None~Questing Adventurer"
	requireTarget, keyWord, description = False, "", "Whenever your play a card, gain +1/+1"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_QuestingAdventurer(self)]
		
class Trigger_QuestingAdventurer(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionPlayed", "SpellPlayed", "WeaponPlayed", "HeroCardPlayed"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject.ID == self.entity.ID and subject != self.entity
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self.entity.Game, "Player plays a card and %s gains +1/+1."%self.entity.name)
		self.entity.buffDebuff(1, 1)
		
		
class RagingWorgen(Minion):
	Class, race, name = "Neutral", "", "Raging Worgen"
	mana, attack, health = 3, 3, 3
	index = "Classic~Neutral~Minion~3~3~3~None~Raging Worgen"
	requireTarget, keyWord, description = False, "", "Has +1 Attack and Windfury while damaged"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.auras["Enrage"] = EnrageAura_RaginWorgen(self)
		self.triggers["StatChanges"] = [self.handleEnrage]
		self.activated = False
		
	def handleEnrage(self):
		self.auras["Enrage"].handleEnrage()
		
class EnrageAura_RaginWorgen(AuraDealer_toMinion):
	def __init__(self, entity):
		self.entity = entity
		signals, self.auraAffected = [], []
		
	def auraAppears(self):
		pass
		
	def auraDisappears(self):
		pass
		
	def handleEnrage(self):
		if self.entity.onBoard:
			if self.entity.activated == False and self.entity.health < self.entity.health_upper:
				self.entity.activated = True
				BuffAura_Receiver(self.entity, self, 1, 0).effectStart()
				HasAura_Receiver(self.entity, self, "Windfury").effectStart()
			elif self.entity.activated and self.entity.health >= self.entity.health_upper:
				self.entity.activated = False
				for entity, aura_Receiver in fixedList(self.auraAffected):
					aura_Receiver.effectClear()
					
	def selfCopy(self, recipientMinion): #The recipientMinion is the minion that deals the Aura.
		#func that checks if subject is applicable will be the new copy's function
		return type(self)(recipientMinion)
		
	def createCopy(self, recipientGame):
		#一个光环的注册可能需要注册多个扳机
		if self not in recipientGame.copiedObjs: #这个光环没有被复制过
			entityCopy = self.entity.createCopy(recipientGame)
			Copy = self.selfCopy(entityCopy)
			recipientGame.copiedObjs[self] = Copy
			for minion, aura_Receiver in self.auraAffected:
				minionCopy = minion.createCopy(recipientGame)
				if hasattr(aura_Receiver, "keyWord"):
					receiverIndex = minion.keyWordbyAura["Auras"].index(aura_Receiver)
					receiverCopy = minionCopy.keyWordbyAura["Auras"][receiverIndex]
				else: #不是关键字光环，而是buff光环
					receiverIndex = minion.statbyAura[2].index(aura_Receiver)
					receiverCopy = minionCopy.statbyAura[2][receiverIndex]
				receiverCopy.source = Copy #补上这个receiver的source
				Copy.auraAffected.append((minionCopy, receiverCopy))
			return Copy
		else:
			return recipientGame.copiedObjs[self]
			
			
class ScarletCrusader(Minion):
	Class, race, name = "Neutral", "", "Scarlet Crusader"
	mana, attack, health = 3, 3, 1
	index = "Classic~Neutral~Minion~3~3~1~None~Scarlet Crusader~Divine Shield"
	requireTarget, keyWord, description = False, "Divine Shield", "Divine Shield"
	
	
class SouthseaCaptain(Minion):
	Class, race, name = "Neutral", "Pirate", "Southsea Captain"
	mana, attack, health = 3, 3, 3
	index = "Classic~Neutral~Minion~3~3~3~Pirate~Southsea Captain"
	requireTarget, keyWord, description = False, "", "Your other Pirates have +1/+1"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.auras["Buff Aura"] = BuffAura_Dealer_All(self, 1, 1)
		
	def applicable(self, target):
		return "Pirate" in target.race
		
		
class TaurenWarrior(Minion):
	Class, race, name = "Neutral", "", "Tauren Warrior"
	mana, attack, health = 3, 2, 3
	index = "Classic~Neutral~Minion~3~2~3~None~Tauren Warrior~Taunt"
	requireTarget, keyWord, description = False, "Taunt", "Taunt. Has +3 attack while damaged"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.auras["Enrage"] = BuffAura_Dealer_Enrage(self, 3)
		self.triggers["StatChanges"] = [self.handleEnrage]
		self.activated = False
		
	def handleEnrage(self):
		self.auras["Enrage"].handleEnrage()
		
				
				
class ThrallmarFarseer(Minion):
	Class, race, name = "Neutral", "", "Thrallmar Farseer"
	mana, attack, health = 3, 2, 3
	index = "Classic~Neutral~Minion~3~2~3~None~Thrallmar Farseer~Windfury"
	requireTarget, keyWord, description = False, "Windfury", "Windfury"
	
	
class TinkmasterOverspark(Minion):
	Class, race, name = "Neutral", "", "Tinkmaster Overspark"
	mana, attack, health = 3, 3, 3
	index = "Classic~Neutral~Minion~3~3~3~None~Tinkmaster Overspark~Battlecry~Legendary"
	requireTarget, keyWord, description = False, "", "Battlecry: Transform another random minion into a 5/5 Devilsaur or 1/1 Squirrel"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if curGame.mode == 0:
			PRINT(curGame, "Tinkmaster Overspark's battlecry transforms minion into a 1/1 Squirrel or 5/5 Devilsaur.")
			if curGame.guides:
				i, where, squirrel = curGame.guides.pop(0)
				if not where: return None
			else:
				minions = curGame.minionsonBoard(1) + curGame.minionsonBoard(2)
				extractfrom(self, minions)
				if minions:
					minion = npchoice(minions)
					i, where, squirrel = minion.position, "minion%d"%minion.ID, nprandint(2)
					curGame.fixedGuides.append((i, where, squirrel))
				else:
					curGame.fixedGuides.append((0, '', 0))
					return None
			minion = curGame.find(i, where)
			curGame.transform(minion, (Squirrel if squirrel else Devilsaur)(curGame, minion.ID))
		return None
		
class Devilsaur(Minion):
	Class, race, name = "Neutral", "Beast", "Devilsaur"
	mana, attack, health = 5, 5, 5
	index = "Classic~Neutral~Minion~5~5~5~Beast~Devilsaur~Uncollectible"
	requireTarget, keyWord, description = False, "", ""
	
class Squirrel(Minion):
	Class, race, name = "Neutral", "Beast", "Squirrel"
	mana, attack, health = 1, 1, 1
	index = "Classic~Neutral~Minion~1~1~1~Beast~Squirrel~Uncollectible"
	requireTarget, keyWord, description = False, "", ""
	
"""Mana 4 minion"""
class AncientBrewmaster(Minion):
	Class, race, name = "Neutral", "", "Ancient Brewmaster"
	mana, attack, health = 4, 5, 4
	index = "Classic~Neutral~Minion~4~5~4~None~Ancient Brewmaster~Battlecry"
	requireTarget, keyWord, description = True, "", "Battlecry: Return a friendly minion from battlefield to your hand"
	
	def targetExists(self, choice=0):
		return self.selectableFriendlyMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.ID == self.ID and target != self and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target and target.onBoard:
			PRINT(self.Game, "Ancient Brewmaster's battlecry returns friendly minion %s to player's hand."%target.name)
			self.Game.returnMiniontoHand(target)
		return target
		
		
class AncientMage(Minion):
	Class, race, name = "Neutral", "", "Ancient Mage"
	mana, attack, health = 4, 2, 5
	index = "Classic~Neutral~Minion~4~2~5~None~Ancient Mage~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Give adjacent minions Spell Damage +1"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if self.onBoard:
			PRINT(self.Game, "Ancient Mage's battlecry gives adjacent friendly minions Spell Damage +1.")
			targets, distribution = self.Game.adjacentMinions2(self)
			for target in targets:
				target.keyWords["Spell Damage"] += 1
		return None
		
#When die from an AOE, no card is drawn.
class CultMaster(Minion):
	Class, race, name = "Neutral", "", "Cult Master"
	mana, attack, health = 4, 4, 2
	index = "Classic~Neutral~Minion~4~4~2~None~Cult Master"
	requireTarget, keyWord, description = False, "", "Whenever one of your other minion dies, draw a card"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_CultMaster(self)]
		
class Trigger_CultMaster(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionDies"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and target != self.entity and target.ID == self.entity.ID#Technically, minion has to disappear before dies. But just in case.
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self.entity.Game, "A friendly minion %s dies and %s lets player draw a card."%(target.name, self.entity.name))
		self.entity.Game.Hand_Deck.drawCard(self.entity.ID)
		
		
class DarkIronDwarf(Minion):
	Class, race, name = "Neutral", "", "Dark Iron Dwarf"
	mana, attack, health = 4, 4, 4
	index = "Classic~Neutral~Minion~4~4~4~None~Dark Iron Dwarf~Battlecry"
	requireTarget, keyWord, description = True, "", "Battlecry: Give a minion +2 Attack"
	
	def targetExists(self, choice=0):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target != self and target.onBoard
		
	#手牌中的随从也会受到临时一回合的加攻，回合结束时消失。
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			PRINT(self.Game, "Dard Iron Dwarf's battlecry gives minion %s +2 attack this turn."%target.name)
			target.buffDebuff(2, 0, "EndofTurn")
		return target
		
		
class DefenderofArgus(Minion):
	Class, race, name = "Neutral", "", "Defender of Argus"
	mana, attack, health = 4, 2, 3
	index = "Classic~Neutral~Minion~4~2~3~None~Defender of Argus~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Given adjacent minions +1/+1 and Taunt"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if self.onBoard:
			PRINT(self.Game, "Defender of Argus's battlecry gives adjacent friendly minions +1/+1 and Taunt.")
			for minion in self.Game.adjacentMinions2(self)[0]:
				minion.buffDebuff(1, 1)
				minion.getsKeyword("Taunt")
		return None
		
		
class DreadCorsair(Minion):
	Class, race, name = "Neutral", "Pirate", "Dread Corsair"
	mana, attack, health = 4, 3, 3
	index = "Classic~Neutral~Minion~4~3~3~Pirate~Dread Corsair~Taunt"
	requireTarget, keyWord, description = False, "Taunt", "Taunt. Costs (1) less per Attack your weapon"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersinHand = [Trigger_DreadCorsair(self)]
		
	def selfManaChange(self):
		if self.inHand:
			weapon = self.Game.availableWeapon(self.ID)
			if weapon:
				self.mana -= weapon.attack
				self.mana = max(0, self.mana)
				
class Trigger_DreadCorsair(TriggerinHand):
	def __init__(self, entity):
		self.blank_init(entity, ["WeaponEquipped", "WeaponRemoved"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.inHand and ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.Game.Manas.calcMana_Single(self.entity)
		
		
class MogushanWarden(Minion):
	Class, race, name = "Neutral", "", "Mogu'shan Warden"
	mana, attack, health = 4, 1, 7
	index = "Classic~Neutral~Minion~4~1~7~None~Mogu'shan Warden~Taunt"
	requireTarget, keyWord, description = False, "Taunt", "Taunt"
	
	
class SilvermoonGuardian(Minion):
	Class, race, name = "Neutral", "", "Silvermoon Guardian"
	mana, attack, health = 4, 3, 3
	index = "Classic~Neutral~Minion~4~3~3~None~Silvermoon Guardian~Divine Shield"
	requireTarget, keyWord, description = False, "Divine Shield", "Divine Shield"
	
	
class SI7Infiltrator(Minion):
	Class, race, name = "Neutral", "", "SI: 7 Infiltrator"
	mana, attack, health = 4, 5, 4
	index = "Classic~Neutral~Minion~4~5~4~None~SI:7 Infiltrator~Battlecry"
	requireTarget, keyWord, description = False, "", "Destroy a random enemy secret"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		enemySecrets = curGame.Secrets.secrets[3-self.ID]
		if curGame.mode == 0:
			PRINT(curGame, "SI:7 Infiltrator's battlecry destroys a random enemy secret.")
			if curGame.guides:
				i = curGame.guides.pop(0)
				if i < 0: return None
			else:
				if enemySecrets:
					i = nprandint(len(enemySecrets))
					curGame.fixedGuides.append(i)
				else:
					curGame.fixedGuides.append(-1)
					return None
			curGame.Secrets.extractSecrets(3-self.ID, i)
		return None
		
		
class TwilightDrake(Minion):
	Class, race, name = "Neutral", "Dragon", "Twilight Drake"
	mana, attack, health = 4, 4, 1
	index = "Classic~Neutral~Minion~4~4~1~Dragon~Twilight Drake~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Gain +1 Health for each card in your hand"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		num = len(self.Game.Hand_Deck.hands[self.ID])
		PRINT(self.Game, "Twilight Drake's battlecry gives minion +1 health for every card in player's hand.")
		self.buffDebuff(0, num)
		return None
		
		
class VioletTeacher(Minion):
	Class, race, name = "Neutral", "", "Violet Teacher"
	mana, attack, health = 4, 3, 5
	index = "Classic~Neutral~Minion~4~3~5~None~Violet Teacher"
	requireTarget, keyWord, description = False, "", "Whenever you cast a spell, summon a 1/1 Violet Apperentice"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_VioletTeacher(self)]
		
class Trigger_VioletTeacher(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["SpellPlayed"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject.ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self.entity.Game, "Player casts a spell and %s summons a 1/1 Violet Apprentice."%self.entity.name)
		self.entity.Game.summon(VioletApprentice(self.entity.Game, self.entity.ID), self.entity.position+1, self.entity.ID)
		
class VioletApprentice(Minion):
	Class, race, name = "Neutral", "", "Violet Apprentice"
	mana, attack, health = 1, 1, 1
	index = "Classic~Neutral~Minion~1~1~1~None~Violet Apprentice~Uncollectible"
	requireTarget, keyWord, description = False, "", ""
	
"""Mana 5 minions"""
class Abomination(Minion):
	Class, race, name = "Neutral", "", "Abomination"
	mana, attack, health = 5, 4, 4
	index = "Classic~Neutral~Minion~5~4~4~None~Abomination~Taunt~Deathrattle"
	requireTarget, keyWord, description = False, "Taunt", "Taunt. Deathrattle: Deal 2 damage to ALL characters"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [Deal2DamagetoAllCharacters(self)]
		
class Deal2DamagetoAllCharacters(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		targets = [self.entity.Game.heroes[1], self.entity.Game.heroes[2]] + self.entity.Game.minionsonBoard(1) + self.entity.Game.minionsonBoard(2)
		damages = [2 for obj in targets]
		PRINT(self.entity.Game, "Deathrattle: Deal 2 damage to all characters triggers.")
		self.entity.dealsAOE(targets, damages)
		
		
class BigGameHunter(Minion):
	Class, race, name = "Neutral", "", "Big Game Hunter"
	mana, attack, health = 5, 4, 2
	index = "Classic~Neutral~Minion~5~4~2~None~Big Game Hunter~Battlecry"
	requireTarget, keyWord, description = True, "", "Battlecry: Destroy a minion with 7 or more Attack"
	
	def targetExists(self, choice=0):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target != self and target.attack > 6 and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			PRINT(self.Game, "Big Game Hunter's battlecry destroys minion %s with 7 or more attack."%target.name)
			self.destroyMinion(target)
		return target
		
		
class CaptainGreenskin(Minion):
	Class, race, name = "Neutral", "Pirate", "Captain Greenskin"
	mana, attack, health = 5, 5, 4
	index = "Classic~Neutral~Minion~5~5~4~Pirate~Captain Greenskin~Battlecry~Legendary"
	requireTarget, keyWord, description = False, "", "Battlecry: Give your weapon +1/+1"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if self.Game.availableWeapon(self.ID):
			PRINT(self.Game, "Captain Greenskin's battlecry gives player's weapon +1/+1.")
			self.Game.availableWeapon(self.ID).gainStat(1, 1)
		return None
		
		
class FacelessManipulator(Minion):
	Class, race, name = "Neutral", "", "Faceless Manipulator"
	mana, attack, health = 5, 3, 3
	index = "Classic~Neutral~Minion~5~3~3~None~Faceless Manipulator~Battlecry"
	requireTarget, keyWord, description = True, "", "Battlecry: Choose a minion and become a copy of it"
	
	def targetExists(self, choice=0):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target != self and target.onBoard
		
	#无面上场时，先不变形，正常触发Illidan的召唤，以及飞刀。之后进行判定。如果无面在战吼触发前死亡，则没有变形发生。
	#之后无面开始进行变形，即使被返回到时我方手牌中，在手牌中的无面会变形成为base copy。
	#如果那个目标随从被返回手牌，则变形成base copy
	#Faceless Manipulator can't trigger its battlecry twice.
	#If there is Mayor Noggenfogger randomizing two selections, the minion is already transformed into the first copy
	#Randomizing twice is no different than randomizing only once.
	#不需要另写played方法了
	#如果自己死亡，不触发战吼。
	#没有死亡的情况下，有一方不在场的话，则变形为base copy（即使自己在手牌中）
	#双方都在场的时候，则自己在场，目标不在场（死亡，回手，进牌库）： base copy
	#自己在场，目标在场： Accurate copy
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		#目前只有打随从从手牌打出或者被沙德沃克调用可以触发随从的战吼。这些手段都要涉及self.Game.minionPlayed
		#如果self.Game.minionPlayed不再等于自己，说明这个随从的已经触发了变形而不会再继续变形。
		if target and self.dead == False and self.Game.minionPlayed == self: #战吼触发时自己不能死亡。
			if self.onBoard or self.inHand:
				if target.onBoard:
					Copy = target.selfCopy(self.ID)
					PRINT(self.Game, "Faceless Manipulator's battlecry transforms minion into a copy of %s"%target.name)
				else: #target not on board. This Faceless Manipulator becomes a base copy of it.
					Copy = type(target)(self.Game, self.ID)
					PRINT(self.Game, "Faceless Manipulator's battlecry transforms minion into a base copy of %s"%target.name)
				self.Game.transform(self, Copy)
		return target
		
		
class FenCreeper(Minion):
	Class, race, name = "Neutral", "", "Fen Creeper"
	mana, attack, health = 5, 3, 6
	index = "Classic~Neutral~Minion~5~3~6~None~Fen Creeper~Taunt"
	requireTarget, keyWord, description = False, "Taunt", "Taunt"
	
	
class HarrisonJones(Minion):
	Class, race, name = "Neutral", "", "Harrison Jones"
	mana, attack, health = 5, 5, 4
	index = "Classic~Neutral~Minion~5~5~4~None~Harrison Jones~Battlecry~Legendary"
	requireTarget, keyWord, description = False, "", "Battlecry: Destroy your opponent's weapon and draw cards equal to its Durability"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		weapon = self.Game.availableWeapon(3-self.ID)
		if weapon:
			num = weapon.durability
			weapon.destroyed()
			if self.Game.status[self.ID]["Battlecry x2"] + self.Game.status[self.ID]["Shark Battlecry x2"] > 0 and comment != "byOthers":
				PRINT(self.Game, "Harrison Jones's battlecry destroys enemy weapon and player draws two cards for each of its durability")
				for i in range(2 * num):
					self.Game.Hand_Deck.drawCard(self.ID)
			else:
				PRINT(self.Game, "Harrison Jones's battlecry destroys enemy weapon and player draws a card for each of its durability")
				for i in range(num):
					self.Game.Hand_Deck.drawCard(self.ID)
		return None
		
		
class SilverHandKnight(Minion):
	Class, race, name = "Neutral", "", "Silver Hand Knight"
	mana, attack, health = 5, 4, 4
	index = "Classic~Neutral~Minion~5~4~4~None~Silver Hand Knight~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Summon a 2/2 Squire"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		PRINT(self.Game, "Silver Hand Knight's battlecry summons a 2/2 Squire.")
		self.Game.summon(Squire(self.Game, self.ID), self.position+1, self.ID)
		return None
		
class Squire(Minion):
	Class, race, name = "Neutral", "", "Squire"
	mana, attack, health = 1, 2, 2
	index = "Classic~Neutral~Minion~2~2~2~None~Squire~Uncollectible"
	requireTarget, keyWord, description = False, "", ""
	
	
class SpitefulSmith(Minion):
	Class, race, name = "Neutral", "", "Spiteful Smith"
	mana, attack, health = 5, 4, 6
	index = "Classic~Neutral~Minion~5~4~6~None~Spiteful Smith"
	requireTarget, keyWord, description = False, "", "Your weapon has +2 Attack while this is damaged"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.auras["Spiteful Smith Aura"] = WeaponBuffAura_SpitefulSmith(self)
		self.triggers["StatChanges"] = [self.handleEnrage]
		self.activated = False
		
	#随从出场时，就会根据是否有受伤来决定是否启动光环。
	#激怒开启，启动光环。激怒消失，关闭光环。
	#如果在激怒状态下被转移控制权，光环经历正常的消失和再启动。
	#如果是在非激怒状态下转移，应该没有任何区别。
	#将这个光环编为Aura_Dealer之后，其消失和转移都由光环的控制来操控。
	def handleEnrage(self):
		if self.silenced == False and self.onBoard:
			if self.activated == False and self.health < self.health_upper:
				self.activated = True
				#在随从登场之后，当出现激怒之后再次尝试建立光环。应该可以成功。
				self.auras["Spiteful Smith Aura"].auraAppears()
			elif self.activated and self.health >= self.health_upper:
				self.activated = False
				#随从不再处于激怒状态时，取消光环，无论此时有无武器装备。
				self.auras["Spiteful Smith Aura"].auraDisappears()
				

class WeaponBuffAura_SpitefulSmith:
	def __init__(self, entity):
		self.entity = entity
		self.auraAffected = []
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject.ID == self.entity.ID
		
	def trigger(self, signal, ID, subject, target, number, comment, choice=0):
		if self.canTrigger(signal, ID, subject, target, number, comment):
			self.effect(signal, ID, subject, target, number, comment)
			
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.applies(subject)
		
	def applies(self, subject):
		aura_Receiver = WeaponBuffAura_Receiver(subject, self)
		aura_Receiver.effectStart()
		
	def auraAppears(self):
		#在随从自己登场时，就会尝试开始这个光环，但是如果没有激怒，则无事发生。
		if self.entity.health < self.entity.health_upper:
			self.entity.activated = True
			weapon = self.entity.Game.availableWeapon(self.entity.ID)
			#这个Aura_Dealer可以由激怒和出场两个方式来控制。
			if weapon and weapon not in self.auraAffected:
				self.applies(weapon)
				
			self.entity.Game.triggersonBoard[self.entity.ID].append((self, "WeaponEquipped"))
			
	def auraDisappears(self):
		for weapon, aura_Receiver in fixedList(self.auraAffected):
			aura_Receiver.effectClear()
			
		self.auraAffected = []
		extractfrom((self, "WeaponEquipped"), self.entity.Game.triggersonBoard[self.entity.ID])
		
	def selfCopy(self, recipiententity):
		return type(self)(recipiententity)
		
	#这个函数会在复制场上扳机列表的时候被调用。
	def createCopy(self, recipientGame):
		#一个光环的注册可能需要注册多个扳机
		if self not in recipientGame.copiedObjs: #这个光环没有被复制过
			entityCopy = self.entity.createCopy(recipientGame)
			Copy = self.selfCopy(entityCopy)
			recipientGame.copiedObjs[self] = Copy
			for entity, aura_Receiver in self.auraAffected:
				entityCopy = entity.createCopy(recipientGame)
				#武器光环的statbyAura是[0, []]
				receiverIndex = entity.statbyAura[1].index(aura_Receiver)
				receiverCopy = entityCopy.statbyAura[1][receiverIndex]
				receiverCopy.source = Copy #补上这个receiver的source
				Copy.auraAffected.append((entityCopy, receiverCopy))
			return Copy
		else:
			return recipientGame.copiedObjs[self]
			
			
class StampedingKodo(Minion):
	Class, race, name = "Neutral", "Beast", "Stampeding Kodo"
	mana, attack, health = 5, 3, 5
	index = "Classic~Neutral~Minion~5~3~5~Beast~Stampeding Kodo~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Destroy a random enemy minion with 2 or less Attack"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if curGame.mode == 0:
			if curGame.guides:
				i = curGame.guides.pop(0)
				if i < 0: return None
				else: minion = curGame.minions[3-self.ID][i]
			else:
				targets = [i for i, minion in enumerate(curGame.minionsAlive(3-self.ID)) if minion.attack < 3]
				if targets:
					i = npchoice(targets)
					minion = curGame.minions[3-self.ID][i]
					curGame.fixedGuides.append(i)
				else:
					curGame.fixedGuides.append(-1)
					return None
			PRINT(curGame, "Stampeding Kodo's battlecry destroys random enemy minion %s"%minion.name)
			minion.dead = True
		return None
		
		
class StranglethornTiger(Minion):
	Class, race, name = "Neutral", "Beast", "Stranglethorn Tiger"
	mana, attack, health = 5, 5, 5
	index = "Classic~Neutral~Minion~5~5~5~Beast~Stranglethorn Tiger~Stealth"
	requireTarget, keyWord, description = False, "Stealth", "Stealth"
	
	
class VentureCoMercenary(Minion):
	Class, race, name = "Neutral", "", "Venture Co. Mercenary"
	mana, attack, health = 5, 7, 6
	index = "Classic~Neutral~Minion~5~7~6~None~Venture Co. Mercenary"
	requireTarget, keyWord, description = False, "", "Your minions cost (3) more"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.auras["Mana Aura"] = ManaAura_Dealer(self, changeby=+3, changeto=-1)
		
	def manaAuraApplicable(self, subject): #ID用于判定是否是我方手中的随从
		return subject.type == "Minion" and subject.ID == self.ID
		
"""Mana 6 minions"""
class ArgentCommander(Minion):
	Class, race, name = "Neutral", "", "Argent Commander"
	mana, attack, health = 6, 4, 2
	index = "Classic~Neutral~Minion~6~4~2~None~Argent Commander~Divine Shield~Charge"
	requireTarget, keyWord, description = False, "Charge,Divine Shield", "Charge, Divine Shield"
	
	
class CairneBloodhoof(Minion):
	Class, race, name = "Neutral", "", "Cairne Bloodhoof"
	mana, attack, health = 6, 4, 5
	index = "Classic~Neutral~Minion~6~4~5~None~Cairne Bloodhoof~Deathrattle~Legendary"
	requireTarget, keyWord, description = False, "", "Deathrattle: Summon a 4/5 Baine Bloodhoof"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [SummonBaineBloodhoof(self)]
		
class SummonBaineBloodhoof(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self.entity.Game, "Deathrattle: Summone a 4/5 Baine Bloodhoof triggers.")
		self.entity.Game.summon(BaineBloodhoof(self.entity.Game, self.entity.ID), self.entity.position+1, self.entity.ID)
		
class BaineBloodhoof(Minion):
	Class, race, name = "Neutral", "", "Baine Bloodhoof"
	mana, attack, health = 6, 4, 5
	index = "Classic~Neutral~Minion~6~4~5~None~Baine Bloodhoof~Uncollectible~Legendary"
	requireTarget, keyWord, description = False, "", ""
	
	
class FrostElemental(Minion):
	Class, race, name = "Neutral", "Elemental", "Frost Elemental"
	mana, attack, health = 6, 5, 5
	index = "Classic~Neutral~Minion~6~5~5~Elemental~Frost Elemental~Battlecry"
	requireTarget, keyWord, description = True, "", "Battlecry: Freeze a character"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			PRINT(self.Game, "Frost Elemental's battlecry freezes minion %s"%target.name)
			target.getsFrozen()
		return target
		
		
class GadgetzanAuctioneer(Minion):
	Class, race, name = "Neutral", "", "Gadgetzan Auctioneer"
	mana, attack, health = 6, 4, 4
	index = "Classic~Neutral~Minion~6~4~4~None~Gadgetzan Auctioneer"
	requireTarget, keyWord, description = False, "", "Whenever you cast a spell, draw a card"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_GadgetzanAuctioneer(self)]
		
class Trigger_GadgetzanAuctioneer(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["SpellPlayed"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject.ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self.entity.Game, "Player casts a spell and %s lets player draw a card."%self.entity.name)
		self.entity.Game.Hand_Deck.drawCard(self.entity.ID)
		
		
class Hogger(Minion):
	Class, race, name = "Neutral", "", "Hogger"
	mana, attack, health = 6, 4, 4
	index = "Classic~Neutral~Minion~6~4~4~None~Hogger~Legendary"
	requireTarget, keyWord, description = False, "", "At the end of your turn, summon a 2/2 Gnoll with Taunt"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_Hogger(self)]
		
class Trigger_Hogger(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["TurnEnds"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self.entity.Game, "At the end of turn, %s summons a 2/2 Gnoll with Taunt."%self.entity.name)
		self.entity.Game.summon(Gnoll(self.entity.Game, self.entity.ID), self.entity.position+1, self.entity.ID)
		
class Gnoll(Minion):
	Class, race, name = "Neutral", "", "Gnoll"
	mana, attack, health = 2, 2, 2
	index = "Classic~Neutral~Minion~2~2~2~None~Gnoll~Taunt~Uncollectible"
	requireTarget, keyWord, description = False, "Taunt", "Taunt"
	
#Lady Goya can swap a friendly minion with a minion in deck.
#When Illidan and Knife Juggler are present, Lady Goya selects a friendly minion, then before the battlecry triggers,
#the Illidan/KnifeJuggler combo kills Sylvanas, which takes control of the target friendly minion
#Lady Goya's battlecry triggers and can still return the minion to our deck.
#Once battlecry locks on the target, it wants to finish no matter what.
class Xavius(Minion):
	Class, race, name = "Neutral", "Demon", "Xavius"
	mana, attack, health = 6, 7, 5
	index = "Classic~Neutral~Minion~6~7~5~Demon~Xavius~Legendary"
	requireTarget, keyWord, description = False, "", "Whenever you play a card, summon a 2/1 Satyr"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_Xavius(self)]
		
class Trigger_Xavius(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionPlayed", "SpellPlayed", "WeaponPlayed", "HeroCardPlayed"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject.ID == self.entity.ID and subject != self.entity
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self.entity.Game, "Player plays a card and %s summons a 2/1 XavianSatyr."%self.entity.name)
		self.entity.Game.summon(XavianSatyr(self.entity.Game, self.entity.ID), self.entity.position+1, self.entity.ID)		
		
class XavianSatyr(Minion):
	Class, race, name = "Neutral", "Elemental", "Xavian Satyr"
	mana, attack, health = 1, 2, 1
	index = "Classic~Neutral~Minion~1~2~1~Elemental~Xavian Satyr~Uncollectible"
	requireTarget, keyWord, description = False, "", ""
	
	
class PriestessofElune(Minion):
	Class, race, name = "Neutral", "", "Priestess of Elune"
	mana, attack, health = 6, 5, 4
	index = "Classic~Neutral~Minion~6~5~4~None~Priestess of Elune~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Restore 4 health to your hero"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		heal = 4 * (2 ** self.countHealDouble())
		PRINT(self.Game, "Priestess of Elune's battlecry restores %d health to player."%heal)
		self.restoresHealth(self.Game.heroes[self.ID], heal)
		return None
		
		
class Sunwalker(Minion):
	Class, race, name = "Neutral", "", "Sunwalker"
	mana, attack, health = 6, 4, 5
	index = "Classic~Neutral~Minion~6~4~5~None~Sunwalker~Divine Shield~Taunt"
	requireTarget, keyWord, description = False, "Taunt,Divine Shield", "Taunt, Divine Shield"
	
	
class TheBeast(Minion):
	Class, race, name = "Neutral", "Beast", "The Beast"
	mana, attack, health = 6, 9, 7
	index = "Classic~Neutral~Minion~6~9~7~Beast~The Beast~Deathrattle~Legendary"
	requireTarget, keyWord, description = False, "", "Deathrattle: Summon a 3/3 Finkle Einhorn for your opponent"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [SummonFinkleEinhornsforOpponent(self)]
		
class SummonFinkleEinhornsforOpponent(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self.entity.Game, "Deathrattle: Summon a 3/3 Finkle Einhorn for opponent triggers.")
		self.entity.Game.summon(FinkleEinhorn(self.entity.Game, 3-self.entity.ID), -1, self.entity.ID)
		
class FinkleEinhorn(Minion):
	Class, race, name = "Neutral", "", "Finkle Einhorn"
	mana, attack, health = 3, 3, 3
	index = "Classic~Neutral~Minion~3~3~3~None~Finkle Einhorn~Uncollectible~Legendary"
	requireTarget, keyWord, description = False, "", ""
	
	
class TheBlackKnight(Minion):
	Class, race, name = "Neutral", "", "The Black Knight"
	mana, attack, health = 6, 4, 5
	index = "Classic~Neutral~Minion~6~4~5~None~The Black Knight~Battlecry~Legendary"
	requireTarget, keyWord, description = True, "", "Battlecry: Destroy a minion with Taunt"
	
	def targetExists(self, choice=0):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.keyWords["Taunt"] > 0 and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			PRINT(self.Game, "The Black Knight's battlecry destroys minion %s with Taunt."%target.name)
			self.destroyMinion(target)
		return target
		
class WindfuryHarpy(Minion):
	Class, race, name = "Neutral", "", "Windfury Harpy"
	mana, attack, health = 6, 4, 5
	index = "Classic~Neutral~Minion~6~4~5~None~Windfury Harpy~Windfury"
	requireTarget, keyWord, description = False, "Windfury", "Windfury"
	
"""Mana 7 minions"""
class BarrensStablehand(Minion):
	Class, race, name = "Neutral", "", "Barrens Stablehand"
	mana, attack, health = 7, 4, 4
	index = "Classic~Neutral~Minion~7~4~4~None~Barrens Stablehand~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Summon a random Beast"
	poolIdentifier = "Beasts to Summon"
	@classmethod
	def generatePool(cls, Game):
		return "Beasts to Summon", list(Game.MinionswithRace["Beast"].values())
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if curGame.mode == 0:
			if curGame.guides:
				beast = curGame.guides.pop(0)
			else:
				beast = npchoice(curGame.RNGPools["Beasts to Summon"])
				curGame.fixedGuides.append(beast)
			PRINT(curGame, "Barrens Stablehand's battlecry summons random Beast %s"%beast.name)
			curGame.summon(beast(curGame, self.ID), self.position+1, self.ID)
		return None
		
		
class BaronGeddon(Minion):
	Class, race, name = "Neutral", "Elemental", "Baron Geddon"
	mana, attack, health = 7, 7, 5
	index = "Classic~Neutral~Minion~7~7~5~Elemental~Baron Geddon~Legendary"
	requireTarget, keyWord, description = False, "", "At the end of turn, deal 2 damage to ALL other characters"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_BaronGeddon(self)]
		
class Trigger_BaronGeddon(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["TurnEnds"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self.entity.Game, "At the end of turn, %s deals 2 damage to ALL other characters."%self.entity.name)
		targets = [self.entity.Game.heroes[1], self.entity.Game.heroes[2]] + self.entity.Game.minionsonBoard(1) + self.entity.Game.minionsonBoard(2)
		extractfrom(self.entity, targets)
		self.entity.dealsAOE(targets, [2 for obj in targets])
		
		
class HighInquisitorWhitemane(Minion):
	Class, race, name = "Neutral", "", "High Inquisitor Whitemane"
	mana, attack, health = 7, 6, 8
	index = "Classic~Neutral~Minion~7~6~8~None~High Inquisitor Whitemane~Battlecry~Legendary"
	requireTarget, keyWord, description = False, "", "Battlecry: Summon all friendly minions that died this turn"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if curGame.mode == 0:
			PRINT(curGame, "High Inquisitor Whitemane's battlecry summons friendly minions that died this turn.")
			if curGame.guides:
				minions = curGame.guides.pop(0)
				if not minions:
					PRINT(curGame, "No friendly minions have died this turn.")
					return None
			else:
				minionsDied = curGame.Counters.minionsDiedThisTurn[self.ID]
				numSummon = min(curGame.space(self.ID), len(minionsDied))
				if numSummon: #假设召唤顺序是随机的
					indices = npchoice(minionsDied, numSummon, replace=False)
					minions = [curGame.cardPool[index] for index in indices]
					curGame.fixedGuides.append(tuple(minions))
				else:
					PRINT(curGame, "No friendly minions have died this turn.")
					curGame.fixedGuides.append(())
					return None
			pos = (self.position, "totheRight") if self.onBoard else (-1, "totheRightEnd")
			curGame.summon([minion(curGame, self.ID) for minion in minions], pos, self.ID)
		return None
		
		
class RavenholdtAssassin(Minion):
	Class, race, name = "Neutral", "", "Ravenholdt Assassin"
	mana, attack, health = 7, 7, 5
	index = "Classic~Neutral~Minion~7~7~5~None~Ravenholdt Assassin~Stealth"
	requireTarget, keyWord, description = False, "Stealth", "Stealth"
	
"""Mana 8 Minions"""
class ArcaneDevourer(Minion):
	Class, race, name = "Neutral", "Elemental", "Arcane Devourer"
	mana, attack, health = 8, 5 ,5
	index = "Classic~Neutral~Minion~8~5~5~Elemental~Arcane Devourer"
	requireTarget, keyWord, description = False, "", "Whenever you cast a spell, gain +2/+2"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_ArcaneDevourer(self)]
		
class Trigger_ArcaneDevourer(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["SpellPlayed"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject.ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self.entity.Game, "Player casts a spell and %s gains +2/+2."%self.entity.name)
		self.entity.buffDebuff(2, 2)
		
		
class Gruul(Minion):
	Class, race, name = "Neutral", "", "Gruul"
	mana, attack, health = 8, 7, 7
	index = "Classic~Neutral~Minion~8~7~7~None~Gruul~Legendary"
	requireTarget, keyWord, description = False, "", "At the end of each turn, gain +1/+1"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_Gruul(self)]
		
class Trigger_Gruul(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["TurnEnds"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self.entity.Game, "At the end of each turn, %s gains +1/+1."%self.entity.name)
		self.entity.buffDebuff(1, 1)
		
"""Mana 9 minions"""
class Alexstrasza(Minion):
	Class, race, name = "Neutral", "Dragon", "Alexstrasza"
	mana, attack, health = 9, 8, 8
	index = "Classic~Neutral~Minion~9~8~8~Dragon~Alexstrasza~Battlecry~Legendary"
	requireTarget, keyWord, description = True, "", "Battlecry: Set a hero's remaining Health to 15"
	
	def targetCorrect(self, target, choice=0):
		return target.type == "Hero" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			PRINT(self.Game, "Alexstrasza's battlecry sets hero %s's health to 15."%target.name)
			if target.health_upper < 15:
				target.health_upper = 15
			target.health = 15
		return target
		
		
class Malygos(Minion):
	Class, race, name = "Neutral", "Dragon", "Malygos"
	mana, attack, health = 9, 4, 12
	index = "Classic~Neutral~Minion~9~4~12~Dragon~Malygos~Spell Damage~Legendary"
	requireTarget, keyWord, description = False, "", "Spell Damage +5"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.keyWords["Spell Damage"] = 5
		
		
class Nozdormu(Minion):
	Class, race, name = "Neutral", "Dragon", "Nozdormu"
	mana, attack, health = 9, 8, 8
	index = "Classic~Neutral~Minion~9~8~8~Dragon~Nozdormu~Legendary"
	requireTarget, keyWord, description = False, "", ""
	
	
class Onyxia(Minion):
	Class, race, name = "Neutral", "Dragon", "Onyxia"
	mana, attack, health = 9, 8, 8
	index = "Classic~Neutral~Minion~9~8~8~Dragon~Onyxia~Battlecry~Legendary"
	requireTarget, keyWord, description = False, "", "Battlecry: Summon 1/1 Whelps until your side of the battlefield is full"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		PRINT(self.Game, "Onyxia's battlecry fills the board with 1/1 Whelps.")
		if self.onBoard: self.Game.summon([Whelp(self.Game, self.ID) for i in range(6)], (self.position, "leftandRight"), self.ID)
		else: self.Game.summon([Whelp(self.Game, self.ID) for i in range(7)], (-1, "totheRightEnd"), self.ID)
		return None
		
class Whelp(Minion):
	Class, race, name = "Neutral", "Dragon", "Whelp"
	mana, attack, health = 1, 1, 1
	index = "Classic~Neutral~Minion~1~1~1~Dragon~Whelp~Uncollectible"
	requireTarget, keyWord, description = False, "", ""
	
	
class Ysera(Minion):
	Class, race, name = "Neutral", "Dragon", "Ysera"
	mana, attack, health = 9, 4, 12
	index = "Classic~Neutral~Minion~9~4~12~Dragon~Ysera~Legendary"
	requireTarget, keyWord, description = False, "", "At the end of your turn, add a Dream Card to your hand"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_Ysera(self)]
		
class Trigger_Ysera(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["TurnEnds"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		curGame = self.entity.Game
		if curGame.mode == 0:
			if curGame.guides:
				card = curGame.guides.pop(0)
			else:
				card = npchoice([Dream, Nightmare, YseraAwakens, LaughingSister, EmeraldDrake])
				curGame.fixedGuides.append(card)
			PRINT(curGame, "At the end of turn, Ysera adds a Dream Card into player's hand.")
			curGame.Hand_Deck.addCardtoHand(card, self.entity.ID, "CreateUsingType")
			
class Dream(Spell):
	Class, name = "DreamCard", "Dream"
	requireTarget, mana = True, 0
	index = "Classic~DreamCard~Spell~0~Dream~Uncollectible"
	description = "Return a minion to its owner's hand"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			PRINT(self.Game, "Dream is cast and returns minion %s to its owner's hand."%target.name)
			self.Game.returnMiniontoHand(target)
		return target
		
class Nightmare(Spell):
	Class, name = "DreamCard", "Nightmare"
	requireTarget, mana = True, 0
	index = "Classic~DreamCard~Spell~0~Nightmare~Uncollectible"
	description = "Give a minion +5/+5. At the start of your next turn, destroy it."
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target and target.onBoard:
			PRINT(self.Game, "Nightmare is cast and gives minion %s +5/+5. It dies at the start of player's turn."%target.name)
			target.buffDebuff(5, 5)
			trigger = Trigger_Corruption(target)
			trigger.ID = self.ID
			target.triggersonBoard.append(trigger)
			trigger.connect()
		return target
		
class YseraAwakens(Spell):
	Class, name = "DreamCard", "Ysera Awakens"
	requireTarget, mana = False, 2
	index = "Classic~DreamCard~Spell~2~Ysera Awakens~Uncollectible"
	description = "Deal 5 damage to all characters except Ysera"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		damage = (5 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		PRINT(self.Game, "Ysera Awakens is cast and deals %d damage to all characters except Ysera."%damage)
		targets = [self.Game.heroes[1], self.Game.heroes[2]]
		for minion in self.Game.minionsonBoard(1) + self.Game.minionsonBoard(2):
			if minion.name != "Ysera" and minion.name != "Ysera, Unleashed":
				targets.append(minion)
				
		self.dealsAOE(targets, [damage for obj in targets])
		return None
		
class LaughingSister(Minion):
	Class, race, name = "DreamCard", "", "Laughing Sister"
	mana, attack, health = 3, 3, 5
	index = "Classic~DreamCard~Minion~3~3~5~None~Laughing Sister~Uncollectible"
	requireTarget, keyWord, description = False, "", "Can't targeted by spells or Hero Powers"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.marks["Evasive"] = 1
		
class EmeraldDrake(Minion):
	Class, race, name = "DreamCard", "Dragon", "Emerald Drake"
	mana, attack, health = 4, 7, 6
	index = "Classic~DreamCard~Minion~4~7~6~Dragon~Emerald Drake~Uncollectible"
	requireTarget, keyWord, description = False, "", ""
	
"""Mana 10 minions"""
class Deathwing(Minion):
	Class, race, name = "Neutral", "Dragon", "Deathwing"
	mana, attack, health = 10, 12, 12
	index = "Classic~Neutral~Minion~10~12~12~Dragon~Deathwing~Battlecry~Legendary"
	requireTarget, keyWord, description = False, "", "Battlecry: Destroy all other minions and discard your hands"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		PRINT(self.Game, "Deahtwing's battlecry destroys all other minions and discard all of player's hand.")
		for minion in self.Game.minionsonBoard(1) + self.Game.minionsonBoard(2):
			if minion != self: minion.dead = True
		self.Game.Hand_Deck.discardAll(self.ID)
		return None
		
		
class SeaGiant(Minion):
	Class, race, name = "Neutral", "", "Sea Giant"
	mana, attack, health = 10, 8, 8
	index = "Classic~Neutral~Minion~10~8~8~None~Sea Giant"
	requireTarget, keyWord, description = False, "", "Costs (1) less for each other minion on the battlefield"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersinHand = [Trigger_SeaGiant(self)]
		
	def selfManaChange(self):
		if self.inHand:
			num = len(self.Game.minionsonBoard(1)) + len(self.Game.minionsonBoard(2))
			self.mana -= num
			self.mana = max(0, self.mana)
		
class Trigger_SeaGiant(TriggerinHand):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionAppears", "MinionDisappears"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.inHand
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.Game.Manas.calcMana_Single(self.entity)
		
"""Druid Cards"""
class Savagery(Spell):
	Class, name = "Druid", "Savagery"
	requireTarget, mana = True, 1
	index = "Classic~Druid~Spell~1~Savagery"
	description = "Deal equal to your hero's Attack to a minion"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			damage = (self.Game.heroes[self.ID].attack + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			PRINT(self.Game, "Savagery is cast and deals %d damage to minion %s"%(damage, target.name))
			self.dealsDamage(target, damage)
		return target
		
		
class PoweroftheWild(Spell):
	Class, name = "Druid", "Power of the Wild"
	requireTarget, mana = False, 2
	index = "Classic~Druid~Spell~2~Power of the Wild~Choose One"
	description = "Choose One - Give your minions +1/+1; or Summon a 3/2 Panther"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.chooseOne = 1
		self.options = [LeaderofthePack_Option(self), SummonaPanther_Option(self)]
	#needTarget() always returns False
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if choice == "ChooseBoth" or choice == 1:
			PRINT(self.Game, "Power of the Wild summons a 3/2 Panther.")
			self.Game.summon(Panther(self.Game, self.ID), -1, self.ID)
		if choice == "ChooseBoth" or choice == 0:
			PRINT(self.Game, "Power of the Wild gives all friendly minions +1/+1.")
			for minion in self.Game.minionsonBoard(self.ID):
				minion.buffDebuff(1, 1)
		return None
		
class LeaderofthePack_Option(ChooseOneOption):
	name, description = "Leader of the Pack", "Give your minions +1/+1"
	index = "Classic~Druid~Spell~2~Leader of the Pack~Uncollectible"
	
class SummonaPanther_Option(ChooseOneOption):
	name, description = "Summon a Panther", "Summon a 3/2 Panther"
	index = "Classic~Druid~Spell~2~Summon a Panther~Uncollectible"
	def available(self):
		return self.entity.Game.space(self.entity.ID) > 0
		
class LeaderofthePack(Spell):
	Class, name = "Druid", "Leader of the Pack"
	requireTarget, mana = False, 2
	index = "Classic~Druid~Spell~2~Leader of the Pack~Uncollectible"
	description = "Give your minions +1/+1"
	def available(self):
		return True
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		PRINT(self.Game, "Leader of the Pack is cast and gives friendly minions +1/+1.")
		for minion in self.Game.minionsonBoard(self.ID):
			minion.buffDebuff(1, 1)
		return None
		
class SummonaPanther(Spell):
	Class, name = "Druid", "Summon a Panther"
	requireTarget, mana = False, 2
	index = "Classic~Druid~Spell~2~Summon a Panther~Uncollectible"
	description = "Summon a 3/2 Panther"
	def available(self):
		return self.Game.space(self.ID) > 0
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		PRINT(self.Game, "Summon a Panther is cast and summons a 3/2 Panther")
		self.Game.summon(Panther(self.Game, self.ID), -1, self.ID)
		return None
		
class Panther(Minion):
	Class, race, name = "Druid", "Beast", "Panther"
	mana, attack, health = 2, 3, 2
	index = "Classic~Druid~Minion~2~3~2~Beast~Panther~Uncollectible"
	requireTarget, keyWord, description = False, "", ""
	
	
class Wrath(Spell):
	Class, name = "Druid", "Wrath"
	requireTarget, mana = True, 2
	index = "Classic~Druid~Spell~2~Wrath~Choose One"
	description = "Choose One - Deal 3 damage to a minion; or Deal 1 damage and draw a card"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.chooseOne = 1
		self.options = [SolarWrath_Option(self), NaturesWrath_Option(self)]
		
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			damage_3 = (3 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			damage_1 = (1 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			if choice == "ChooseBoth" or choice == 0:
				PRINT(self.Game, "Wrath deals %d damage to minion %s"%(damage_3, target.name))
				self.dealsDamage(target, damage_3)
			if choice == "ChooseBoth" or choice == 1:
				PRINT(self.Game, "Wrath deals %d damage to minion %s and lets player draw a card."%(damage_1, target.name))
				self.dealsDamage(target, damage_1)
				self.Game.Hand_Deck.drawCard(self.ID)
		return target
		
class SolarWrath_Option(ChooseOneOption):
	name, description = "Solar Wrath", "Deal 3 damage to a minion"
	index = "Classic~Druid~Spell~2~Solar Wrath~Uncollectible"
	def available(self):
		return self.entity.selectableMinionExists(0)
		
class NaturesWrath_Option(ChooseOneOption):
	name, description = "Nature's Wrath", "Deal 1 damage to a minion. Draw card."
	index = "Classic~Druid~Spell~2~Nature's Wrath~Uncollectible"
	def available(self):
		return self.entity.selectableMinionExists(1)
		
class SolarWrath(Spell):
	Class, name = "Druid", "Solar Wrath"
	requireTarget, mana = True, 2
	index = "Classic~Druid~Spell~2~Solar Wrath~Uncollectible"
	description = "Deal 3 damage to a minion"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			damage = (3 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			PRINT(self.Game, "Solar Wrath is cast and deals %d damage to minion %s"%(damage, target.name))
			self.dealsDamage(target, damage)
		return target
		
class NaturesWrath(Spell):
	Class, name = "Druid", "Nature's Wrath"
	requireTarget, mana = True, 2
	index = "Classic~Druid~Spell~2~Nature's Wrath~Uncollectible"
	description = "Deal 1 damage to a minion. Draw a card"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			damage = (1 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			PRINT(self.Game, "Nature's Wrath is cast, deals %d damage to minion %s and lets player draw a card."%(damage, target.name))
			self.dealsDamage(target, damage)
			self.Game.Hand_Deck.drawCard(self.ID)
		return target
		
class MarkofNature(Spell):
	Class, name = "Druid", "Mark of Nature"
	requireTarget, mana = True, 3
	index = "Classic~Druid~Spell~3~Mark of Nature~Choose One"
	description = "Choose One - Give a minion +4 Attack; or +4 Health and Taunt"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.chooseOne = 1
		self.options = [TigersFury_Option(self), ThickHide_Option(self)]
		
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			if choice == "ChooseBoth" or choice == 0:
				PRINT(self.Game, "Mark of Nature gives minion %s +4 attack."%target.name)
				target.buffDebuff(4, 0)
			if choice == "ChooseBoth" or choice == 1:
				PRINT(self.Game, "Mark of Nature gives minion %s +4 health and Taunt."%target.name)
				target.buffDebuff(0, 4)
				target.getsKeyword("Taunt")
		return target
		
class TigersFury_Option(ChooseOneOption):
	name, description = "Tiger's Fury", "+4 attack"
	index = "Classic~Druid~Spell~3~Tiger's Fury~Uncollectible"
	def available(self):
		return self.entity.selectableMinionExists(0)
		
class ThickHide_Option(ChooseOneOption):
	name, description = "Thick Hide", "+4 Health and Taunt"
	index = "Classic~Druid~Spell~3~Thick Hide~Uncollectible"
	def available(self):
		return self.entity.selectableMinionExists(1)
		
class TigersFury(Spell):
	Class, name = "Druid", "Tiger's Fury"
	requireTarget, mana = True, 3
	index = "Classic~Druid~Spell~3~Tiger's Fury~Uncollectible"
	description = "Give a minion +4 Attack"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			PRINT(self.Game, "Tiger's Fury is cast and gives minion %s +4 attack."%target.name)
			target.buffDebuff(4, 0)
		return target
		
class ThickHide(Spell):
	Class, name = "Druid", "Thick Hide"
	requireTarget, mana = True, 3
	index = "Classic~Druid~Spell~3~Thick Hide~Uncollectible"
	description = "Give a minion +4 Health and Taunt"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			PRINT(self.Game, "Thick Hide is cast and gives minion %s +4 health and Taunt."%target.name)
			target.buffDebuff(0, 4)
			target.getsKeyword("Taunt")
		return target
		
		
class Bite(Spell):
	Class, name = "Druid", "Bite"
	requireTarget, mana = False, 4
	index = "Classic~Druid~Spell~4~Bite"
	description = "Give your hero +4 Attack this turn. Gain 4 Armor"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		PRINT(self.Game, "Bite is cast and gives player +4 armor and +4 attack this turn.")
		self.Game.heroes[self.ID].gainTempAttack(4)
		self.Game.heroes[self.ID].gainsArmor(4)
		return None
		
		
class KeeperoftheGrove(Minion):
	Class, race, name = "Druid", "", "Keeper of the Grove"
	mana, attack, health = 4, 2, 2
	index = "Classic~Druid~Minion~4~2~2~None~Keeper of the Grove~Choose One"
	requireTarget, keyWord, description = True, "", "Choose One - Deal 2 damage; or Silence a minion"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.chooseOne = 1
		self.options = [Moonfire_Option(self), Dispel_Option(self)]
		
	def targetExists(self, choice=0):
		if choice == "ChooseBoth" or choice == 0: #Deal 2 damage
			return self.selectableCharacterExists(choice)
		else:
			return self.selectableMinionExists()
			
	def targetCorrect(self, target, choice=0):
		if choice == "ChooseBoth" or choice == 0:
			if (target.type == "Minion" or target.type == "Hero") and target.onBoard:
				return True
		else:
			if target.type == "Minion" and target.onBoard:
				return True
		return False
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			if (choice == "ChooseBoth" or choice == 1) and target.type == "Minion":
				PRINT(self.Game, "Keeper of the Grove silences minion %s"%target.name)
				target.getsSilenced()
			if choice == "ChooseBoth" or choice == 0:
				PRINT(self.Game, "Keeper of the Grove deals 2 damage to %s"%target.name)
				self.dealsDamage(target, 2)
		return target
		
class Moonfire_Option(ChooseOneOption):
	name, description = "Moonfire", "Deal 2 damage"
	
class Dispel_Option(ChooseOneOption):
	name, description = "Dispel", "Silence a minion"
	def available(self):
		return self.entity.selectableMinionExists(1)
		
		
class SouloftheForest(Spell):
	Class, name = "Druid", "Soul of the Forest"
	requireTarget, mana = False, 4
	index = "Classic~Druid~Spell~4~Soul of the Forest"
	description = "Give your minions 'Deathrattle: Summon a 2/2 Treant'"
	def available(self):
		return self.Game.minionsonBoard(self.ID) != []
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		PRINT(self.Game, "Soul of the Forest is cast and gives all friendly minions Deathrattle: Summon a 2/2 Treant.")
		for minion in self.Game.minionsonBoard(self.ID):
			trigger = SummonaTreant(minion)
			minion.deathrattles.append(trigger)
			trigger.connect()
		return None
		
class SummonaTreant(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		#This Deathrattle can't possibly be triggered in hand
		PRINT(self.entity.Game, "Deathrattle: Resummon a 2/2 Treant triggers.")
		self.entity.Game.summon(Treant_Classic(self.entity.Game, self.entity.ID), self.entity.position+1, self.entity.ID)
		
class Treant_Classic(Minion):
	Class, race, name = "Druid", "", "Treant"
	mana, attack, health = 2, 2, 2
	index = "Classic~Druid~Minion~2~2~2~None~Treant Classic~Uncollectible"
	requireTarget, keyWord, description = False, "", ""
	
	
class DruidoftheClaw(Minion):
	Class, race, name = "Druid", "", "Druid of the Claw"
	mana, attack, health = 5, 4, 4
	index = "Classic~Druid~Minion~5~4~4~None~Druid of the Claw~Choose One"
	requireTarget, keyWord, description = False, "", "Choose One - Transform into a 4/4 with Charge; or a 4/6 with Taunt"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.chooseOne = 1
		self.options = [CatForm_Option(self), BearForm_Option(self)]
		
	def played(self, target=None, choice=0, mana=0, posinHand=0, comment=""):
		self.statReset(self.attack_Enchant, self.health_max)
		self.appears()
		if choice == "ChooseBoth":
			minion = DruidoftheClaw_Both(self.Game, self.ID)
		elif choice == 0:
			minion = DruidoftheClaw_Charge(self.Game, self.ID)
		else:
			minion = DruidoftheClaw_Taunt(self.Game, self.ID)
		#抉择变形类随从的入场后立刻变形。
		self.Game.transform(self, minion)
		#在此之后就要引用self.Game.minionPlayed
		self.Game.sendSignal("MinionPlayed", self.ID, self.Game.minionPlayed, None, mana, "", choice)
		self.Game.sendSignal("MinionSummoned", self.ID, self.Game.minionPlayed, None, mana, "")
		self.Game.gathertheDead()
		return None
		
class CatForm_Option(ChooseOneOption):
	name, description = "Cat Form", "Charge"
	
class BearForm_Option(ChooseOneOption):
	name, description = "Bear Form", "+2 health and Taunt"
	
class DruidoftheClaw_Charge(Minion):
	Class, race, name = "Druid", "Beast", "Druid of the Claw"
	mana, attack, health = 5, 4, 4
	index = "Classic~Druid~Minion~5~4~4~Beast~Druid of the Claw~Charge~Uncollectible"
	requireTarget, keyWord, description = False, "Charge", "Charge"
	
class DruidoftheClaw_Taunt(Minion):
	Class, race, name = "Druid", "Beast", "Druid of the Claw"
	mana, attack, health = 5, 4, 6
	index = "Classic~Druid~Minion~5~4~6~Beast~Druid of the Claw~Taunt~Uncollectible" 
	requireTarget, keyWord, description = False, "Taunt", "Taunt"
	
class DruidoftheClaw_Both(Minion):
	Class, race, name = "Druid", "Beast", "Druid of the Claw"
	mana, attack, health = 5, 4, 6
	index = "Classic~Druid~Minion~5~4~6~Beast~Druid of the Claw~Taunt~Charge~Uncollectible" 
	requireTarget, keyWord, description = False, "Taunt,Charge", "Taunt, Charge"
	
	
class ForceofNature(Spell):
	Class, name = "Druid", "Force of Nature"
	requireTarget, mana = False, 5
	index = "Classic~Druid~Spell~5~Force of Nature"
	description = "Summon three 2/2 Treants"
	def available(self):
		return self.Game.space(self.ID) > 0
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		PRINT(self.Game, "Force of Nature is cast and summons three 2/2 Treants")
		self.Game.summon([Treant_Classic(self.Game, self.ID) for i in range(3)], (-1, "totheRightEnd"), self.ID)
		return None
		
	
class Starfall(Spell):
	Class, name = "Druid", "Starfall"
	requireTarget, mana = True, 5
	index = "Classic~Druid~Spell~5~Starfall~Choose One"
	description = "Choose One - Deal 5 damage to a minion; or Deal 2 damage to all enemy minions"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.chooseOne = 1
		self.options = [Starlord_Option(self), StellarDrift_Option(self)]
		
	def returnTrue(self, choice=0):
		return choice == "ChooseBoth" or choice == 0
		
	def available(self):
		#当场上有全选光环时，变成了一个指向性法术，必须要有一个目标可以施放。
		if self.Game.status[self.ID]["Choose Both"] > 0:
			return self.selectableMinionExists("ChooseBoth")
		else: #Deal 2 AOE damage.
			return True
			
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		damage_5 = (5 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		damage_2 = (2 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		if choice == "ChooseBoth" or choice == 0:
			if target:
				PRINT(self.Game, "Starfall deals %d damage to minion %s"%(damage_5, target.name))
				self.dealsDamage(target, damage_5)
		if choice == "ChooseBoth" or choice == 1:
			PRINT(self.Game, "Starfall deals %d damage to all enemy minions."%damage_2)
			targets = self.Game.minionsonBoard(3-self.ID)
			self.dealsAOE(targets, [damage_2 for minion in targets])	
		return target
		
class Starlord_Option(ChooseOneOption):
	name, description = "Starlord", "Deal 5 damage to a minion"
	index = "Classic~Druid~Spell~5~Starlord~Uncollectible"
	def available(self):
		return self.entity.selectableMinionExists(0)
		
class StellarDrift_Option(ChooseOneOption):
	name, description = "Stellar Drift", "Deal 2 damage to all enemy minions"
	index = "Classic~Druid~Spell~5~Stellar Drift~Uncollectible"
	
class Starlord(Spell):
	Class, name = "Druid", "Starlord"
	requireTarget, mana = True, 5
	index = "Classic~Druid~Spell~5~Starlord~Uncollectible"
	description = "Deal 5 damage to a minion"
	def available(self):
		return self.selectableMinionExists(0)
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			damage = (5 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			PRINT(self.Game, "Starlord is cast and deals %d damage to minion %s"%(damage, target.name))
			self.dealsDamage(target, damage)
		return target
		
class StellarDrift(Spell):
	Class, name = "Druid", "Stellar Drift"
	requireTarget, mana = False, 5
	index = "Classic~Druid~Spell~5~Stellar Drift~Uncollectible"
	description = "Deal 2 damage to all enemy minions"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		damage = (2 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		PRINT(self.Game, "Stellar Drift is cast and deals %d damage to emeny minions."%damage)
		targets = self.Game.minionsonBoard(3-self.ID)
		self.dealsAOE(targets, [damage for minion in targets])
		return None
		
		
class Nourish(Spell):
	Class, name = "Druid", "Nourish"
	requireTarget, mana = False, 6
	index = "Classic~Druid~Spell~6~Nourish~Choose One"
	description = "Choose One - Gain 2 Mana Crystals; or Draw 3 cards"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.chooseOne = 1
		self.options = [RampantGrowth_Option(self), Enrich_Option(self)]
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if choice == "ChooseBoth" or choice == 0:
			PRINT(self.Game, "Nourish gives player 2 mana crystals.")
			self.Game.Manas.gainManaCrystal(2, self.ID)
		if choice == "ChooseBoth" or choice == 1:
			PRINT(self.Game, "Nourish lets player draw 3 cards.")
			self.Game.Hand_Deck.drawCard(self.ID)
			self.Game.Hand_Deck.drawCard(self.ID)
			self.Game.Hand_Deck.drawCard(self.ID)
		return None
		
class RampantGrowth_Option(ChooseOneOption):
	name, description = "Rampant Growth", "Gain 2 Mana Crystals"
	index = "Classic~Druid~Spell~6~Rampant Growth~Uncollectible"
	
class Enrich_Option(ChooseOneOption):
	name, description = "Enrich", "Draw 3 cards"
	index = "Classic~Druid~Spell~6~Enrich~Uncollectible"
	
class RampantGrowth(Spell):
	Class, name = "Druid", "Rampant Growth"
	requireTarget, mana = False, 6
	index = "Classic~Druid~Spell~6~Rampant Growth~Uncollectible"
	description = "Gain 2 Mana Crystals"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		PRINT(self.Game, "Rampant Growth is cast and gives player 2 mana crystals.")
		self.Game.Manas.gainManaCrystal(2, self.ID)
		return None
		
class Enrich(Spell):
	Class, name = "Druid", "Enrich"
	requireTarget, mana = False, 6
	index = "Classic~Druid~Spell~6~Enrich~Uncollectible"
	description = "Draw 3 cards"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		PRINT(self.Game, "Enrich is cast and lets player draw 3 cards.")
		self.Game.Hand_Deck.drawCard(self.ID)
		self.Game.Hand_Deck.drawCard(self.ID)
		self.Game.Hand_Deck.drawCard(self.ID)
		return None
		
#Maybe need to rewrite.			
class AncientofLore(Minion):
	Class, race, name = "Druid", "", "Ancient of Lore"
	mana, attack, health = 7, 5, 5
	index = "Classic~Druid~Minion~7~5~5~None~Ancient of Lore~Choose One"
	requireTarget, keyWord, description = True, "", "Choose One - Draw a card; or Restore 5 Health"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.chooseOne = 1
		self.options = [AncientTeachings_Option(self), AncientSecrets_Option(self)]
		
	def returnTrue(self, choice=0):
		return choice == "ChooseBoth" or choice == 1
		
	def targetExists(self, choice=1):
		return True
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if choice == "ChooseBoth" or choice == 1:
			if target:
				heal = 5 * (2 ** self.countHealDouble())
				PRINT(self.Game, "Ancient of Lore restores %d health to %s"%(heal, target.name))
				self.restoresHealth(target, heal)
		if choice == "ChooseBoth" or choice == 0:
			PRINT(self.Game, "Ancient of Lore lets player draw a card.")
			self.Game.Hand_Deck.drawCard(self.ID)
		return target
		
class AncientTeachings_Option(ChooseOneOption):
	name, description = "Ancient Teachings", "Draw a card"
	
class AncientSecrets_Option(ChooseOneOption):
	name, description = "Ancient Secrets", "Restore 5 health"
	
	
class AncientofWar(Minion):
	Class, race, name = "Druid", "", "Ancient of War"
	mana, attack, health = 7, 5, 5
	index = "Classic~Druid~Minion~7~5~5~None~Ancient of War~Choose One"
	requireTarget, keyWord, description = False, "", "Choose One - +5 Attack; or +5 Health and Taunt"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.chooseOne = 1
		self.options = [Uproot_Option(self), Rooted_Option(self)]
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if choice == "ChooseBoth" or choice == 0:
			PRINT(self.Game, "Ancient of War gains +5 attack.")
			self.buffDebuff(5, 0)
		if choice == "ChooseBoth" or comment == 1:
			PRINT(self.Game, "Ancient of War gains +5 health and Taunt.")
			self.buffDebuff(0, 5)
			self.getsKeyword("Taunt")
		return None
		
class Uproot_Option(ChooseOneOption):
	name, description = "Uproot", "+5 attack"
	
class Rooted_Option(ChooseOneOption):
	name, description = "Rooted", "+5 health and Taunt"
	
	
class GiftoftheWild(Spell):
	Class, name = "Druid", "Gift of the Wild"
	requireTarget, mana = False, 8
	index = "Classic~Druid~Spell~8~Gift of the Wild"
	description = "Give your minions +2/+2 and Taunt"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		PRINT(self.Game, "Gift of the Wild is cast and gives all friendly minions +2/+2 and Taunt.")
		for minion in self.Game.minionsonBoard(self.ID):
			minion.buffDebuff(2, 2)
			minion.getsKeyword("Taunt")
		return None
		
		
class Cenarius(Minion):
	Class, race, name = "Druid", "", "Cenarius"
	mana, attack, health = 9, 5, 8
	index = "Classic~Druid~Minion~9~5~8~None~Cenarius~Choose One~Legendary"
	requireTarget, keyWord, description = False, "", "Choose One- Give your other minions +2/+2; or Summon two 2/2 Treants with Taunt"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.chooseOne = 1
		# 0: Give other minion +2/+2; 1:Summon two Treants with Taunt.
		self.options = [DemigodsFavor_Option(self), ShandosLesson_Option(self)]
		
	#对于抉择随从而言，应以与战吼类似的方式处理，打出时抉择可以保持到最终结算。但是打出时，如果因为鹿盔和发掘潜力而没有选择抉择，视为到对方场上之后仍然可以而没有如果没有
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if choice == "ChooseBoth" or choice == 1:
			PRINT(self.Game, "Cenarius summons two 2/2 Treants with Taunt")
			pos = (self.position, "leftandRight") if self.onBoard else (-1, "totheRightEnd")
			self.Game.summon([Treant_Classic_Taunt(self.Game, self.ID) for i in range(2)], pos, self.ID)
			
		if choice == "ChooseBoth" or choice == 0:
			PRINT(self.Game, "Cenarius gives all other friendly minions +2/+2.")
			for minion in self.Game.minionsonBoard(self.ID):
				if minion != self:
					minion.buffDebuff(2, 2)
					
		return None
		
class Treant_Classic_Taunt(Minion):
	Class, race, name = "Druid", "", "Treant"
	mana, attack, health = 2, 2, 2
	index = "Classic~Druid~Minion~2~2~2~None~Treant~Taunt~Uncollectible"
	requireTarget, keyWord, description = False, "Taunt", "Taunt"
	
class DemigodsFavor_Option(ChooseOneOption):
	name, description = "Demigod's Favor", "Give your other minions +2/+2"
	
class ShandosLesson_Option(ChooseOneOption):
	name, description = "Shan'do's Lesson", "Summon two 2/2 Treants with Taunt"
	def available(self):
		return self.entity.Game.space(self.entity.ID) > 0
		
"""Hunter Cards"""
class BestialWrath(Spell):
	Class, name = "Hunter", "Bestial Wrath"
	requireTarget, mana = True, 1
	index = "Classic~Hunter~Spell~1~Bestial Wrath"
	description = "Give a friendly Beast +2 Attack and Immune this turn"
	def available(self):
		return self.selectableFriendlyMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and "Beast" in target.race and target.ID == self.ID and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target and (target.inHand or target.onBoard):
			#Assume the Immune status of the minion will vanish in hand at the end of turn, too.
			PRINT(self.Game, "Bestial Wrath is cast and gives %s +2 attack and Immune this turn.")
			target.status["Immune"] += 1
			target.buffDebuff(2, 0, "EndofTurn")
		return target
		
		
class ExplosiveTrap(Secret):
	Class, name = "Hunter", "Explosive Trap"
	requireTarget, mana = False, 2
	index = "Classic~Hunter~Spell~2~Explosive Trap~~Secret"
	description = "When your hero is attacked, deal 2 damage to all enemies"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_ExplosiveTrap(self)]
		
class Trigger_ExplosiveTrap(SecretTrigger):
	def __init__(self, entity):
		self.blank_init(entity, ["HeroAttacksHero", "MinionAttacksHero"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0): #target here holds the actual target object
		return self.entity.ID != self.entity.Game.turn and target[0] == self.entity.Game.heroes[self.entity.ID]
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		damage = (2 + self.entity.countSpellDamage()) * (2 ** self.entity.countDamageDouble())
		PRINT(self.entity.Game, "When player is attacked, Secret Explosive Trap is triggered and deals %d damage to all enemies."%damage)
		enemies = [self.entity.Game.heroes[3-self.entity.ID]] + self.entity.Game.minionsonBoard(3-self.entity.ID)
		self.entity.dealsAOE(enemies, [damage for obj in enemies])
		
		
class FreezingTrap(Secret):
	Class, name = "Hunter", "Freezing Trap"
	requireTarget, mana = False, 2
	index = "Classic~Hunter~Spell~2~Freezing Trap~~Secret"
	description = "When an enemy minion attacks, return it to its owner's hand. It costs (2) more."
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_FreezingTrap(self)]
		
class Trigger_FreezingTrap(SecretTrigger):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionAttacksMinion", "MinionAttacksHero"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.ID != self.entity.Game.turn and subject.type == "Minion" and subject.ID != self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self.entity.Game, "When enemy minion %s attacks, Secret Freezing Trap is triggered and returns it to its owner's hand."%subject.name)
		#假设那张随从在进入手牌前接受-2费效果。可以被娜迦海巫覆盖。
		manaMod = ManaModification(subject, changeby=+2, changeto=-1)
		self.entity.Game.returnMiniontoHand(subject, keepDeathrattlesRegistered=False, manaModification=manaMod)
		
		
class Misdirection(Secret):
	Class, name = "Hunter", "Misdirection"
	requireTarget, mana = False, 2
	index = "Classic~Hunter~Spell~2~Misdirection~~Secret"
	description = "When an enemy attacks your hero, instead it attacks another random character"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_Misdirection(self)]
		
class Trigger_Misdirection(SecretTrigger):
	def __init__(self, entity):
		self.blank_init(entity, ["HeroAttacksHero", "MinionAttacksHero"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0): #target here holds the actual target object
		#The target needs to be your hero
		if self.entity.ID != self.entity.Game.turn and target[0].type == "Hero" and target[0].ID == self.entity.ID:
			targets = self.entity.Game.charsAlive(1) + self.entity.Game.charsAlive(2)
			extractfrom(subject, targets)
			extractfrom(target[1], targets)
			if targets: return True
		return False
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		curGame = self.entity.Game
		if curGame.mode == 0:
			if curGame.guides:
				i, where = curGame.guides.pop(0)
				if where: target[1] = curGame.find(i, where)
				else: return
			else:
				targets = self.entity.Game.charsAlive(1) + self.entity.Game.charsAlive(2)
				extractfrom(subject, targets)
				extractfrom(target[1], targets) #误导始终是根据当前的真实攻击目标进行响应。即使本轮中初始的的攻击目标不与当前的目标一致。
				if targets:
					target[1] = npchoice(targets)
					if target[1].type == "Minion": i, where = target[1].position, "minion%d"%target[1].ID
					else: i, where = target[1].ID, "hero"
					curGame.fixedGuides.append((i, where))
				else:
					curGame.fixedGuides.append((0, ''))
					return
			PRINT(curGame, "When player is attacked, Secret Misdirection is triggered and redirects the attack to another target %s"%target[1].name)
			
			
class SnakeTrap(Secret):
	Class, name = "Hunter", "Snake Trap"
	requireTarget, mana = False, 2
	index = "Classic~Hunter~Spell~2~Snake Trap~~Secret"
	description = "When one of your minions is attacked, summon three 1/1 Snakes"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_SnakeTrap(self)]
		
class Trigger_SnakeTrap(SecretTrigger):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionAttacksMinion", "HeroAttacksMinion"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0): #target here holds the actual target object
		#The target has to a friendly minion and there is space on board to summon minions.
		return self.entity.ID != self.entity.Game.turn and target[0].type == "Minion" and target[0].ID == self.entity.ID and self.entity.Game.space(self.entity.ID) > 0
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self.entity.Game, "When a friendly minion %s is attacked, Secret Snake Trap is triggered and summons three 1/1 Snakes."%target[0].name)
		self.entity.Game.summon([Snake(self.entity.Game, self.entity.ID) for i in range(3)], (-1, "totheRightEnd"), self.entity.ID)
		
class Snake(Minion):
	Class, race, name = "Hunter", "Beast", "Snake"
	mana, attack, health = 1, 1, 1
	index = "Classic~Hunter~Minion~1~1~1~Beast~Snake~Uncollectible"
	requireTarget, keyWord, description = False, "", ""
	
	
class Snipe(Secret):
	Class, name = "Hunter", "Snipe"
	requireTarget, mana = False, 2
	index = "Classic~Hunter~Spell~2~Snipe~~Secret"
	description = "After your opponent plays a minion, deal 4 damage to it"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_Snipe(self)]
		
class Trigger_Snipe(SecretTrigger):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionBeenPlayed"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		#不确定是否只会对生命值大于1的随从触发。一般在"MinionBeenPlayed"信号发出的时候随从都是处于非濒死状态的。
		return self.entity.ID != self.entity.Game.turn and subject.ID != self.entity.ID and subject.health > 0 and subject.dead == False
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		damage = (4 + self.entity.countSpellDamage()) * (2 ** self.entity.countDamageDouble())
		PRINT(self.entity.Game, "After enemy minion %s is played, Secret Snipe is triggered and deals %d damage to it."%(subject.name, damage))
		self.entity.dealsDamage(subject, damage)
		
		
class Flare(Spell):
	Class, name = "Hunter", "Flare"
	requireTarget, mana = False, 2
	index = "Classic~Hunter~Spell~2~Flare"
	description = "All minions lose Stealth. Destroy all enemy secrets. Draw a card"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		PRINT(self.Game, "Flare is cast. All minions lose Stealth. All enemy secrets are destroyed and player draws a card.")
		for minion in self.Game.minionsonBoard(1) + self.Game.minionsonBoard(2):
			minion.keyWords["Stealth"] = 0
			minion.status["Temp Stealth"] = 0
		self.Game.Secrets.extractSecrets(3-self.ID, True)
		self.Game.Hand_Deck.drawCard(self.ID)
		return None
		
		
class ScavengingHyena(Minion):
	Class, race, name = "Hunter", "Beast", "Scavenging Hyena"
	mana, attack, health = 2, 2, 2
	index = "Classic~Hunter~Minion~2~2~2~Beast~Scavenging Hyena"
	requireTarget, keyWord, description = False, "", "Whenever a friendly Beast dies, gain +2/+1"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_ScavengingHyena(self)]
		
class Trigger_ScavengingHyena(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionDies"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		#Technically, minion has to disappear before dies. But just in case.
		return self.entity.onBoard and target != self.entity and target.ID == self.entity.ID and "Beast" in target.race
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self.entity.Game, "A friendly Beast %s dies and %s gains +2/+1."%(target.name, self.entity.name))
		self.entity.buffDebuff(2, 1)
		
		
class DeadlyShot(Spell):
	Class, name = "Hunter", "Deadly Shot"
	requireTarget, mana = False, 3
	index = "Classic~Hunter~Spell~3~Deadly Shot"
	description = "Destroy a random enemy minion"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if curGame.mode == 0:
			if curGame.guides:
				i = curGame.guides.pop(0)
				if i < 0: return None
				else: minion = curGame.minions[3-self.ID][i]
			else:
				minions = curGame.minionsAlive(3-self.ID)
				if minions:
					minion = npchoice(minions)
					curGame.fixedGuides.append(minion.position)
				else:
					curGame.fixedGuides.append(-1)
					return None
			PRINT(curGame, "Deadly shot is cast and kills enemy minion %s"%minion.name)
			minion.dead = True
		return None
		
		
class EaglehornBow(Weapon):
	Class, name, description = "Hunter", "Eaglehorn Bow", "Whenever a friendly Secret is revealed, gain +1 Durability"
	mana, attack, durability = 3, 3, 2
	index = "Classic~Hunter~Weapon~3~3~2~Eaglehorn Bow"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_EaglehornBow(self)]
		
class Trigger_EaglehornBow(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["SecretRevealed"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return subject.ID == self.entity.ID and self.entity.onBoard
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self.entity.Game, "A friendly Secret is revealed and %s gains +1 Durability."%self.entity.name)
		self.entity.gainStat(0, 1)
		
		
class UnleashtheHounds(Spell):
	Class, name = "Hunter", "Unleash the Hounds"
	requireTarget, mana = False, 3
	index = "Classic~Hunter~Spell~3~Unleash the Hounds"
	description = "For each enemy minion, summon a 1/1 Hound with Charge"
	def available(self):
		return self.Game.space(self.ID) > 0 and self.Game.minionsonBoard(3-self.ID) != []
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		PRINT(self.Game, "Unleash the Hounds is cast and summons a 1/1 Hound with Charge for each enemy minion.")
		numHounds = min(self.Game.space(self.ID), len(self.Game.minionsonBoard(3-self.ID)))
		self.Game.summon([Hound(self.Game, self.ID) for i in range(numHounds)], (-1, "totheRightEnd"), self.ID)
		return None
		
class Hound(Minion):
	Class, race, name = "Hunter", "Beast", "Hound"
	mana, attack, health = 1, 1, 1
	index = "Classic~Hunter~Minion~1~1~1~Beast~Hound~Charge~Uncollectible"
	requireTarget, keyWord, description = False, "Charge", ""
	
	
class ExplosiveShot(Spell):
	Class, name = "Hunter", "Explosive Shot"
	requireTarget, mana = True, 5
	index = "Classic~Hunter~Spell~5~Explosive Shot"
	description = "Deal 5 damage to a minion and 2 damage to adjacent ones"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			damage_target = (5 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			damage_adjacent = (3 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			PRINT(self.Game, "Explosive Shot is cast and deals %d damage to %s and %d damage to minions adjacent to it."%(damage_target, target.name, damage_adjacent))
			if target.onBoard and self.Game.adjacentMinions2(target)[0] != []:
				targets = [target] + self.Game.adjacentMinions2(target)[0]
				damages = [damage_target] + [damage_adjacent for minion in targets]
				self.dealsAOE(targets, damages)
			else:
				self.dealsDamage(target, damage_target)
		return target
		
		
class SavannahHighmane(Minion):
	Class, race, name = "Hunter", "Beast", "Savannah Highmane"
	mana, attack, health = 6, 6, 5
	index = "Classic~Hunter~Minion~6~6~5~Beast~Savannah Highmane~Deathrattle"
	requireTarget, keyWord, description = False, "", "Deathrattle: Summon two 2/2 Hyenas"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [SummonTwoHyenas(self)]
		
class SummonTwoHyenas(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		pos = (self.entity.position, "totheRight") if self.entity in self.entity.Game.minions[self.entity.ID] else (-1, "totheRightEnd")
		PRINT(self.entity, "Deathrattle: Summon two 2/2 Hyenas triggers.")
		self.entity.Game.summon([Hyena_Classic(self.entity.Game, self.entity.ID) for i in range(2)], pos, self.entity.ID)
		
class Hyena_Classic(Minion):
	Class, race, name = "Hunter", "Beast", "Hyena"
	mana, attack, health = 2, 2, 2
	index = "Classic~Hunter~Minion~2~2~2~Beast~Hyena~Uncollectible"
	requireTarget, keyWord, description = False, "", ""
	
	
class GladiatorsLongbow(Weapon):
	Class, name, description = "Hunter", "Gladiator's Longbow", "Your hero is Immune while attacking"
	mana, attack, durability = 7, 5, 2
	index = "Classic~Hunter~Weapon~7~5~2~Gladiator's Longbow"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_GladiatorsLongbow(self)]
		
class Trigger_GladiatorsLongbow(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["BattleStarted", "BattleFinished"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return subject == self.entity.Game.heroes[self.entity.ID] and self.entity.onBoard
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		if signal == "BattleStarted":
			PRINT(self.entity.Game, "Before attack begins, %s gives the attacking hero Immune"%self.entity.name)
			self.entity.Game.status[self.entity.ID]["Immune"] += 1
		else:
			PRINT(self.entity.Game, "After attack finished, %s removes the Immune from the attacking hero."%self.entity.name)
			self.entity.Game.status[self.entity.ID]["Immune"] -= 1
				
				
class KingKrush(Minion):
	Class, race, name = "Hunter", "Beast", "King Krush"
	mana, attack, health = 9, 8, 8
	index = "Classic~Hunter~Minion~9~8~8~Beast~King Krush~Charge~Legendary"
	requireTarget, keyWord, description = False, "Charge", "Charge"
	
	
"""Mage cards"""
class TomeofIntellect(Spell):
	Class, name = "Mage", "Tome of Intellect"
	requireTarget, mana = False, 1
	index = "Classic~Mage~Spell~1~Tome of Intellect"
	description = "Add a random Mage spell to your hand"
	poolIdentifier = "Mage Spells"
	@classmethod
	def generatePool(cls, Game):
		mageSpells = []
		for key, value in Game.ClassCards["Mage"].items():
			if "~Spell~" in key:
				mageSpells.append(value)
		return "Mage Spells", mageSpells
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if curGame.mode == 0:
			if curGame.guides:
				mageSpell = curGame.guides.pop(0)
			else:
				mageSpell = npchoice(curGame.RNGPools["Mage Spells"])
				curGame.fixedGuides.append(mageSpell)
			PRINT(curGame, "Tome of Intellect is cast and adds a random Mage card to player's hand.")	
			curGame.Hand_Deck.addCardtoHand(mageSpell, self.ID, "CreateUsingType")
		return None
		
		
class Icicle(Spell):
	Class, name = "Mage", "Icicle"
	requireTarget, mana = True, 2
	index = "Classic~Mage~Spell~2~Icicle"
	description = "Deal 2 damage to a minion. If it's Frozen, draw a card"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			damage = (2 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			PRINT(self.Game, "Icicle is cast and deals %d damage to %s"%(damage, target.name))
			self.dealsDamage(target, damage)
			if target.status["Frozen"]:
				PRINT(self.Game, "Icicle targets a Frozen minion and lets player draws a card.")
				self.Game.Hand_Deck.drawCard(self.ID)
		return target
		
		
class ManaWyrm(Minion):
	Class, race, name = "Mage", "", "Mana Wyrm"
	mana, attack, health = 2, 1, 3
	index = "Classic~Mage~Minion~2~1~3~None~Mana Wyrm"
	requireTarget, keyWord, description = False, "", "Whenever you cast a spell, gain 1 Attack"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_ManaWyrm(self)]
		
class Trigger_ManaWyrm(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["SpellPlayed"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject.ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self.entity.Game, "Player cast a spell and %s gains +1 Attack."%self.entity.name)
		self.entity.buffDebuff(1, 0)
		
		
class SorcerersApprentice(Minion):
	Class, race, name = "Mage", "", "Sorcerer's Apprentice"
	mana, attack, health = 2, 3, 2
	index = "Classic~Mage~Minion~2~3~2~None~Sorcerer's Apprentice"
	requireTarget, keyWord, description = False, "", "Your spells cost (1) less"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.auras["Mana Aura"] = ManaAura_Dealer(self, changeby=-1, changeto=-1)
		
	def manaAuraApplicable(self, subject): #ID用于判定是否是我方手中的随从
		return subject.type == "Spell" and subject.ID == self.ID
		
#Counterspell is special, it doesn't need a trigger. All spells played by player will directly
#check if this Secret is onBoard.
class Counterspell(Secret):
	Class, name = "Mage", "Counterspell"
	requireTarget, mana = False, 3
	index = "Classic~Mage~Spell~3~Counterspell~~Secret"
	description = "When your opponent casts a spell, Counter it."
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_Counterspell(self)]
		
class Trigger_Counterspell(SecretTrigger):
	def __init__(self, entity):
		self.blank_init(entity, ["TriggerCounterspell"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return subject.ID != self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self.entity.Game, "Secret Counterspell Counters player's attempt to cast spell %s"%subject.name)
		#But actually nothing happens in this trigger. The Game will simply skip all the resolution at the playSpell() function.
		
		
class IceBarrier(Secret):
	Class, name = "Mage", "Ice Barrier"
	requireTarget, mana = False, 3
	index = "Classic~Mage~Spell~3~Ice Barrier~~Secret"
	description = "When your hero is attacked, gain 8 Armor"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_IceBarrier(self)]
		
class Trigger_IceBarrier(SecretTrigger):
	def __init__(self, entity):
		self.blank_init(entity, ["HeroAttacksHero", "MinionAttacksHero"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0): #target here holds the actual target object
		return self.entity.ID != self.entity.Game.turn and target[0] == self.entity.Game.heroes[self.entity.ID]
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self.entity.Game, "When hero %s is attack, Secret Ice Barrier is triggered and player gains 8 Armor."%target[0].name)
		self.entity.Game.heroes[self.entity.ID].gainsArmor(8)
		
		
class MirrorEntity(Secret):
	Class, name = "Mage", "Mirror Entity"
	requireTarget, mana = False, 3
	index = "Classic~Mage~Spell~3~Mirror Entity~~Secret"
	description = "After your opponent plays a minion, summon a copy of it"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_MirrorEntity(self)]
		
class Trigger_MirrorEntity(SecretTrigger):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionBeenPlayed"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.ID != self.entity.Game.turn and subject.ID != self.entity.ID and self.entity.Game.space(self.entity.ID) > 0 and subject.health > 0 and subject.dead == False
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self.entity.Game, "After enemy minion %s is played, Secret Mirro Entity is triggered and summons a copy of it."%subject.name)
		Copy = subject.selfCopy(self.entity.ID)
		self.entity.Game.summon(Copy, -1, self.entity.ID)
		
		
class Spellbender(Secret):
	Class, name = "Mage", "Spellbender"
	requireTarget, mana = False, 3
	index = "Classic~Mage~Spell~3~Spellbender~~Secret"
	description = "When an enemy casts a spell on a minion, summon a 1/3 as the new target"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_Spellbender(self)]
		
class Trigger_Spellbender(SecretTrigger):
	def __init__(self, entity):
		self.blank_init(entity, ["SpellTargetDecision"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.ID != self.entity.Game.turn and subject.ID != self.entity.ID and target[0] and self.entity.Game.space(self.entity.ID) > 0
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self.entity.Game, "When enemy cast spell %s on a minion, Secret Spellbender summons a 1/3 as the new target."%subject.name)
		spellbender = Spellbender_Minion(self.entity.Game, self.entity.ID)
		self.entity.Game.summon(spellbender, -1, self.entity.ID)
		target[0] = spellbender
		
class Spellbender_Minion(Minion):
	Class, race, name = "Mage", "", "Spellbender"
	mana, attack, health = 1, 1, 3
	index = "Classic~Mage~Minion~1~1~3~None~Spellbender~Uncollectible"
	requireTarget, keyWord, description = False, "", ""
	
	
class Vaporize(Secret):
	Class, name = "Mage", "Vaporize"
	requireTarget, mana = False, 3
	index = "Classic~Mage~Spell~3~Vaporize~~Secret"
	description = "When a minion attacks your hero, destroy it"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_Vaporize(self)]
		
class Trigger_Vaporize(SecretTrigger):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionAttacksHero"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0): #target here holds the target object for the attack.
		return self.entity.ID != self.entity.Game.turn and target[0] == self.entity.Game.heroes[self.entity.ID] and subject.type == "Minion" and subject.health > 0 and subject.dead == False
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self.entity.Game, "When minion %s attacks player, Secret Vaporize is triggered and destroys it"%subject.name)
		subject.dead = True
		
		
class KirinTorMage(Minion):
	Class, race, name = "Mage", "", "Kirin Tor Mage"
	mana, attack, health = 3, 4, 3
	index = "Classic~Mage~Minion~3~4~3~None~Kirin Tor Mage~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Your next Secret this turn costs (0)"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		PRINT(self.Game, "Kirin Tor Mage's battlecry makes player's next secret this turn cost 0.")
		tempAura = YourNextSecretCosts0ThisTurn(self.Game, self.ID)
		self.Game.Manas.CardAuras.append(tempAura)
		tempAura.auraAppears()
		return None
		
class YourNextSecretCosts0ThisTurn(TempManaEffect):
	def __init__(self, Game, ID):
		self.Game, self.ID = Game, ID
		self.changeby, self.changeto = 0, 0
		self.temporary = True
		self.auraAffected = []
		
	def applicable(self, target):
		return target.ID == self.ID and "~~Secret" in target.index
		
	def selfCopy(self, recipientGame):
		return type(self)(recipientGame, self.ID)
		
		
class ConeofCold(Spell):
	Class, name = "Mage", "Cone of Cold"
	requireTarget, mana = True, 4
	index = "Classic~Mage~Spell~4~Cone of Cold"
	description = "Freeze a minion and the minions next to it, and deal 1 damage to them"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			damage = (1 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			PRINT(self.Game, "Cone of Cold is cast and deals %d damage to %s and minions adjacent to it."%(damage, target.name))
			adjacentMinions, distribution = self.Game.adjacentMinions2(target)
			if adjacentMinions == []:
				self.dealsDamage(target, damage)
				target.getsFrozen()
			else:
				targets = [target] + adjacentMinions
				self.dealsAOE(targets, [damage for minion in targets])
				for minion in targets:
					minion.getsFrozen()
		return target
		
		
class EtherealArcanist(Minion):
	Class, race, name = "Mage", "", "Ethereal Arcanist"
	mana, attack, health = 4, 3, 3
	index = "Classic~Mage~Minion~4~3~3~None~Ethereal Arcanist"
	requireTarget, keyWord, description = False, "", "If you control a Secret at the end of your turn, gain +2/+2"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_EtherealArcanist(self)]
		
class Trigger_EtherealArcanist(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["TurnEnds"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and ID == self.entity.ID and self.entity.Game.Secrets.secrets[self.entity.ID] != []
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self.entity.Game, "At the end of turn, player controls a Secret and %s gain +2/+2."%self.entity.name)
		self.entity.buffDebuff(2, 2)
		
		
class Blizzard(Spell):
	Class, name = "Mage", "Blizzard"
	requireTarget, mana = False, 6
	index = "Classic~Mage~Spell~6~Blizzard"
	description = "Deal 2 damage to all enemy minions and Freeze them"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		damage = (2 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		PRINT(self.Game, "Blizzard deals %d damage to all enemy minions and freezes them."%damage)
		targets = self.Game.minionsonBoard(3-self.ID)
		#Spell AOE can only be take effect before deathrattle triggering. Don't need to make sure 
		self.dealsAOE(targets, [damage for minion in targets])
		for minion in self.Game.minionsonBoard(3-self.ID):
			minion.getsFrozen()
		return None
		
		
class ArchmageAntonidas(Minion):
	Class, race, name = "Mage", "", "Archmage Antonidas"
	mana, attack, health = 7, 5, 7
	index = "Classic~Mage~Minion~7~5~7~None~Archmage Antonidas~Legendary"
	requireTarget, keyWord, description = False, "", "Whenever you cast a spell, add a 'Fireball' spell to your hand"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_ArchmageAntonidas(self)]
		
class Trigger_ArchmageAntonidas(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["SpellPlayed"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject.ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self.entity.Game, "Player cast a spell and %s add a 'Fireball' spell to player's hand."%self.entity.name)
		self.entity.Game.Hand_Deck.addCardtoHand(Fireball, self.entity.ID, "CreateUsingType")
		
class Fireball(Spell):
	Class, name = "Mage", "Fireball"
	requireTarget, mana = True, 4
	index = "Basic~Mage~Spell~4~Fireball"
	description = "Deal 6 damage"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			damage = (6 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			PRINT(self.Game, "Fireball deals %d damage to %s"%(damage, target.name))
			self.dealsDamage(target, damage)
		return target
		
		
class Pyroblast(Spell):
	Class, name = "Mage", "Pyroblast"
	requireTarget, mana = True, 10
	index = "Classic~Mage~Spell~10~Pyroblast"
	description = "Deal 10 damage"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			damage = (10 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			PRINT(self.Game, "Pyroblast is cast and deals %d damage to %s"%(damage, target.name))
			self.dealsDamage(target, damage)
		return target
		
		
"""Paladin cards"""
#If minion attacks and triggers this, drawing card from empty deck kills the hero. Then the attack will be stopped early.
class AldorPeacekeeper(Minion):
	Class, race, name = "Paladin", "", "Aldor Peacekeeper"
	mana, attack, health = 3, 3, 3
	index = "Classic~Paladin~Minion~3~3~3~None~Aldor Peacekeeper~Battlecry"
	requireTarget, keyWord, description = True, "", "Battlecry: Change an enemy minion's Attack to 1"
	
	def targetExists(self, choice=0):
		return self.selectableEnemyMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.ID != self.ID and target.onBoard and target != self
		
	#Infer from Houndmaster: Buff can apply on targets on board, in hand, in deck.
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			PRINT(self.Game, "Aldor Peacekeeper's battlecry changes enemy minion %s's Attack to 1."%target.name)
			target.statReset(1, False)
		return target
		
		
class BlessingofWisdom(Spell):
	Class, name = "Paladin", "Blessing of Wisdom"
	requireTarget, mana = True, 1
	index = "Classic~Paladin~Spell~1~Blessing of Wisdom"
	description = "Choose a minion. Whenever it attacks, draw a card"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target and (target.inHand or target.onBoard):
			PRINT(self.Game, "Blessing of Wisdom is cast on target %s. Whenever it attacks, player draws a card."%target.name)
			trigger = Trigger_BlessingofWisdom(target)
			target.triggersonBoard.append(trigger)
			if target.onBoard:
				trigger.connect()
		return target
		
class Trigger_BlessingofWisdom(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionAttackingHero", "MinionAttackingMinion"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject == self.entity
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self.entity.Game, "Minion %s attacks and Blessing of Wisdom lets its owner draw a card."%self.entity.name)
		self.entity.Game.Hand_Deck.drawCard(self.entity.ID)
		
		
class EyeforanEye(Secret):
	Class, name = "Paladin", "Eye for an Eye"
	requireTarget, mana = False, 1
	index = "Classic~Paladin~Spell~1~Eye for an Eye~~Secret"
	description = "When your hero takes damage, deal that much damage to the enemy hero"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_EyeforanEye(self)]
		
class Trigger_EyeforanEye(SecretTrigger):
	def __init__(self, entity):
		self.blank_init(entity, ["HeroTakesDamage"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.ID != self.entity.Game.turn and target.ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		damage = (number + self.entity.countSpellDamage()) * (2 ** self.entity.countDamageDouble())
		PRINT(self.entity.Game, "When player takes %d damage, Secret Eye for an Eye is triggered and deals %d damage to the enemy hero."%(number, damage))
		self.entity.dealsDamage(self.entity.Game.heroes[3-self.entity.ID], damage)
		
		
class NobleSacrifice(Secret):
	Class, name = "Paladin", "Noble Sacrifice"
	requireTarget, mana = False, 1
	index = "Classic~Paladin~Spell~1~Noble Sacrifice~~Secret"
	description = "When an enemy attacks, summon a 2/1 Defender as the new target"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_NobleSacrifice(self)]
		
class Trigger_NobleSacrifice(SecretTrigger):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionAttacksHero", "MinionAttacksMinion", "HeroAttacksHero", "HeroAttacksMinion"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.ID != self.entity.Game.turn and subject.ID != self.entity.ID and self.entity.Game.space(self.entity.ID) > 0
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self.entity.Game, "When enemy minion %s attacks, Secret Noble Sacrifice triggers and summons a 2/1 Defender as new target."%subject.name)
		newTarget = Defender(self.entity.Game, self.entity.ID)
		self.entity.Game.summon(newTarget, -1, self.entity.ID)
		target[1] = newTarget
		
		
class Defender(Minion):
	Class, race, name = "Paladin", "", "Defender"
	mana, attack, health = 1, 2, 1
	index = "Classic~Paladin~Minion~1~2~1~None~Defender~Uncollectible"
	requireTarget, keyWord, description = False, "", ""
	
	
class Redemption(Secret):
	Class, name = "Paladin", "Redemption"
	requireTarget, mana = False, 1
	index = "Classic~Paladin~Spell~1~Redemption~~Secret"
	description = "When an enemy attacks, summon a 2/1 Defender as the new target"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_Redemption(self)]
		
class Trigger_Redemption(SecretTrigger):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionDies"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.ID != self.entity.Game.turn and target.ID == self.entity.ID and self.entity.Game.space(self.entity.ID) > 0
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self.entity.Game, "When friendly minion %s dies, Secret Redemption returns it to life with 1 Health."%target.name)
		minion = type(target)(self.entity.Game, self.entity.ID)
		minion.health = 1
		self.entity.Game.summon(minion, -1, self.entity.ID)
		
		
class Repentance(Secret):
	Class, name = "Paladin", "Repentance"
	requireTarget, mana = False, 1
	index = "Classic~Paladin~Spell~1~Repentance~~Secret"
	description = "After your opponent plays a minion, reduce its Health to 1"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_Repentance(self)]
		
class Trigger_Repentance(SecretTrigger):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionBeenPlayed"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.ID != self.entity.Game.turn and subject.ID != self.entity
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self.entity.Game, "After enemy minion %s is played, Secret Repentance is triggered and reduces its Health to 1."%subject.name)
		subject.statReset(False, 1)
		
		
class ArgentProtector(Minion):
	Class, race, name = "Paladin", "", "Argent Protector"
	mana, attack, health = 2, 2, 2
	index = "Classic~Paladin~Minion~2~2~2~None~Argent Protector~Battlecry"
	requireTarget, keyWord, description = True, "", "Battlecry: Give a friendly minion Divine Shield"
	
	def targetExists(self, choice=0):
		return self.selectableFriendlyMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.ID == self.ID and target != self and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target: #The minion's getsKeyword() is only effective if minion is onBoard or inHand
			PRINT(self.Game, "Argent Protector's battlecry gives friendly minion %s Divine Shield."%target.name)
			target.getsKeyword("Divine Shield")
		return target
		
		
class Equality(Spell):
	Class, name = "Paladin", "Equality"
	requireTarget, mana = False, 4
	index = "Classic~Paladin~Spell~4~Equality"
	description = "Change the Health of ALL minions to 1"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		PRINT(self.Game, "Equality is cast and sets all minions' health to 1.")
		for minion in self.Game.minionsonBoard(1) + self.Game.minionsonBoard(2):
			minion.statReset(False, 1)
		return None
		
		
class ArdorPeacekeeper(Minion):
	Class, race, name = "Paladin", "", "Ardor Peacekeeper"
	mana, attack, health = 3, 3, 3
	index = "Classic~Paladin~Minion~3~3~3~None~Ardor Peacekeeper~Battlecry"
	requireTarget, keyWord, description = True, "", "Battlecry: Change an enemy minion's Attack to 1"
	
	def targetExists(self, choice=0):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target != self and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target and (target.inHand or target.onBoard):
			PRINT(self.Game, "Ardor Peacekeeper's battlecry sets minion %s's attack to 1."%target.name)
			target.statReset(1, False)
		return target
		
		
class SwordofJustice(Weapon):
	Class, name, description = "Paladin", "Sword of Justice", "After you summon a minion, give it +1/+1 and this loses 1 Durability"
	mana, attack, durability = 3, 1, 5
	index = "Classic~Paladin~Weapon~3~1~5~Sword of Justice"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_SwordofJustice(self)]
		
class Trigger_SwordofJustice(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionBeenSummoned"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		#Can only buff if there is still durability left
		return subject.ID == self.entity.ID and self.entity.onBoard and self.entity.durability > 0
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self.entity.Game, "A friendly minion %s is summoned and %s gives it +1/+1 and loses 1 Durability."%(subject.name, self.entity.name))
		subject.buffDebuff(1, 1)
		self.entity.loseDurability()
		
		
class BlessedChampion(Spell):
	Class, name = "Paladin", "Blessed Champion"
	requireTarget, mana = True, 5
	index = "Classic~Paladin~Spell~5~Blessed Champion"
	description = "Double a minion's Attack"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			PRINT(self.Game, "Blessed Champion is cast and doubles %s's attack."%target.name)
			target.statReset(2*target.attack, False)
		return target
		
		
class HolyWrath(Spell):
	Class, name = "Paladin", "Holy Wrath"
	requireTarget, mana = True, 5
	index = "Classic~Paladin~Spell~5~Holy Wrath"
	description = "Draw a card and deal damage equal to its cost"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		#drawCard() method returns a tuple (card, mana)
		card = self.Game.Hand_Deck.drawCard(self.ID)
		if card[0] == None:
			PRINT(self.Game, "Holy Wrath lets player draw a card but it can't deal damage.")
		else:
			if target:
				damage = (card[1] + self.countSpellDamage()) * (2 ** self.countDamageDouble())
				PRINT(self.Game, "Holy Wrath lets player draw a card and deals %d damage equal to its cost to %s"%(damage, target.name))
				self.dealsDamage(target, damage)
		return target
		
		
class Righteousness(Spell):
	Class, name = "Paladin", "Righteousness"
	requireTarget, mana = False, 5
	index = "Classic~Paladin~Spell~5~Righteousness"
	description = "Give your minions Divine Shield"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		PRINT(self.Game, "Righteousness is cast and gives all friendly minions Divine Shield.")
		for minion in self.Game.minionsonBoard(self.ID):
			minion.getsKeyword("Divine Shield")
		return None
		
		
class AvengingWrath(Spell):
	Class, name = "Paladin", "Avenging Wrath"
	requireTarget, mana = False, 6
	index = "Classic~Paladin~Spell~6~Avenging Wrath"
	description = "Deal 8 damage randomly split among all enemies"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		num = (8 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		side, curGame = 3-self.ID, self.Game
		if curGame.mode == 0:
			PRINT(curGame, "Avenging Wrath deals %d damage randomly split among enemies."%num)
			for i in range(num):
				if curGame.guides:
					i, where = curGame.guides.pop(0)
					if where: char = curGame.find(i, where)
					else: break
				else:
					objs = curGame.charsAlive(side)
					if objs:
						char = npchoice(objs)
						curGame.fixedGuides.append((side, "hero") if char.type == "Hero" else (char.position, "minion%d"%side))
					else:
						curGame.fixedGuides.append((0, ''))
						break #If no enemy character is alive, stop the cycle
				PRINT(curGame, "Avenging Wrath deals 1 damage to %s"%char.name)
				self.dealsDamage(char, 1)
		return None
		
		
class LayonHands(Spell):
	Class, name = "Paladin", "Lay on Hands"
	requireTarget, mana = True, 8
	index = "Classic~Paladin~Spell~8~Lay on Hands"
	description = "Restore 8 Health. Draw 3 cards"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			heal = 8 * (2 ** self.countHealDouble())
			PRINT(self.Game, "Lay on Hands restores %d health to %s"%(heal, target.name))
			self.restoresHealth(target, heal)
		PRINT(self.Game, "Lay on Hands lets player draw 3 cards.")
		self.Game.Hand_Deck.drawCard(self.ID)
		self.Game.Hand_Deck.drawCard(self.ID)
		self.Game.Hand_Deck.drawCard(self.ID)
		return target
		
		
class TirionFordring(Minion):
	Class, race, name = "Paladin", "", "Tirion Fordring"
	mana, attack, health = 8, 6, 6
	index = "Classic~Paladin~Minion~8~6~6~None~Tirion Fordring~Taunt~Divine Shield~Deathrattle~Legendary"
	requireTarget, keyWord, description = False, "Divine Shield,Taunt", "Divine Shield, Taunt. Deathrattle: Equip a 5/3 Ashbringer"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [EquipAshbringer(self)]
		
class EquipAshbringer(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self.entity.Game, "Deathrattle: Equip an Ashbringer triggers.")
		self.entity.Game.equipWeapon(Ashbringer(self.entity.Game, self.entity.ID))
		
class Ashbringer(Weapon):
	Class, name, description = "Paladin", "Ashbringer", ""
	mana, attack, durability = 5, 5, 3
	index = "Classic~Paladin~Weapon~5~5~3~Ashbringer~Uncollectible~Legendary"
	
	
"""Priest cards"""
class CircleofHealing(Spell):
	Class, name = "Priest", "Circle of Healing"
	requireTarget, mana = False, 0
	index = "Classic~Priest~Spell~0~Circle of Healing"
	description = "Restore 4 health to ALL minions"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		heal = 4 * (2 ** self.countHealDouble())
		targets = self.Game.minionsonBoard(1) + self.Game.minionsonBoard(2)
		PRINT(self.Game, "Circle of Healing is cast and restores %d heal to all minions."%heal)
		self.restoresAOE(targets, [heal for minion in targets])
		return None
		
		
class Silence(Spell):
	Class, name = "Priest", "Silence"
	requireTarget, mana = True, 0
	index = "Classic~Priest~Spell~0~Silence"
	description = "Silence a minion"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			PRINT(self.Game, "Silence is cast and silences minion %s"%target.name)
			target.getsSilenced()
		return target
		
		
class InnerFire(Spell):
	Class, name = "Priest", "Inner Fire"
	requireTarget, mana = True, 1
	index = "Classic~Priest~Spell~1~Inner Fire"
	description = "Change a minion's Attack to be equal to its Health"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			PRINT(self.Game, "Inner Fire is cast and changes %s's attack equal to its health."%target.name)
			target.statReset(target.health, False)
		return target
		
		
class ScarletSubjugator(Minion):
	Class, race, name = "Priest", "", "Scarlet Subjugator"
	mana, attack, health = 1, 2, 1
	index = "Classic~Priest~Minion~1~2~1~None~Scarlet Subjugator~Battlecry"
	requireTarget, keyWord, description = True, "", "Battlecry: Give an enemy minion -2 Attack until your next turn"
	def targetExists(self, choice=0):
		return self.selectableEnemyMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.ID != self.ID and target != self and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			PRINT(self.Game, "Scarlet Subjugator's battlecry gives enemy minion %s -2 Attack until player's next turn"%target.name)
			target.buffDebuff(-2, 0, "StartofTurn %d"%self.ID)
		return target
		
		
class KulTiranChaplain(Minion):
	Class, race, name = "Priest", "", "Kul Tiran Chaplain"
	mana, attack, health = 2, 2, 3
	index = "Classic~Priest~Minion~2~2~3~None~Kul Tiran Chaplain~Battlecry"
	requireTarget, keyWord, description = True, "", "Battlecry: Give a friendly minion +2 Health"
	
	def targetExists(self, choice=0):
		return self.selectableFriendlyMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.ID == self.ID and target != self and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			PRINT(self.Game, "Kul Tiran Chaplain's battlecry gives friendly minion %s +2 Health"%target.name)
			target.buffDebuff(0, 2)
		return target
		
		
class Lightwell(Minion):
	Class, race, name = "Priest", "", "Lightwell"
	mana, attack, health = 2, 0, 5
	index = "Classic~Priest~Minion~2~0~5~None~Lightwell"
	requireTarget, keyWord, description = False, "", "At the start of your turn, restore 3 health to a damaged friendly character"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_Lightwell(self)]
		
class Trigger_Lightwell(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["TurnStarts"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		curGame = self.entity.Game
		if curGame.mode == 0:
			if curGame.guides:
				i, where = curGame.guides.pop(0)
				if where: char = curGame.find(i, where)
				else: return
			else:
				chars = [char for char in curGame.charsAlive(self.entity.ID) if char.health < char.health_upper]
				if chars:
					char = npchoice(chars)
					curGame.fixedGuides.append((char.position, "minion%d"%char.ID) if char.type == "Minion" else (char.ID, "hero"))
				else:
					curGame.fixedGuides.append((0, ''))
					return
			heal = 3 * (2 ** self.entity.countHealDouble())
			PRINT(curGame, "At the start of turn, Lightwell restores %d health to damaged friendly character %s"%(heal, char.name))
			self.entity.restoresHealth(char, heal)
			
			
class Thoughtsteal(Spell):
	Class, name = "Priest", "Thoughtsteal"
	requireTarget, mana = False, 2
	index = "Classic~Priest~Spell~2~Thoughtsteal"
	description = "Copy 2 card in your opponent's hand and add them to your hand"
	#Thoughtsteal can copy all enchanements of a card in enemy deck. (Buffed Immortal Prelate)
	#MindVision can also copy the enchanements of a card in enemy hand.
	#If enemy deck is empty, nothing happens
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		enemyDeck = curGame.Hand_Deck.decks[3-self.ID]
		if enemyDeck:
			if curGame.mode == 0:
				PRINT(curGame, "Thoughtsteal is cast and adds copies of 2 random cards from opponent's deck to player's hand")
				if curGame.guides:
					cards = [enemyDeck[i] for i in curGame.guides.pop(0)]
				else:
					num = min(len(enemyDeck), 2)
					indices = npchoice(list(range(len(enemyDeck))), num, replace=False)
					cards = [enemyDeck[i] for i in indices]
					curGame.fixedGuides.append(tuple(indices))
				copies = [card.selfCopy(self.ID) for card in cards]
				self.Game.Hand_Deck.addCardtoHand(copies, self.ID)
		return None
		
		
#被控制的随从会在回合结束效果触发之后立刻返还原有控制者，之后其他随从的回合结束触发会生效
#若我方可以进攻的随从被对方在我方回合暂时夺走，则沉默该随从后，该随从返回我方场上且仍可攻击。

#当一个随从被连续两次使用暗影狂乱更改控制权时，第二次的控制会擦除第一次的原控制者记录。
#我方本回合召唤的随从被暗中破坏者触发的敌方暗影狂乱夺走时，如果再用暗影狂乱把那个随从夺回，那个随从会可以攻击，然后回合结束时归对方所有。

#控制一个对方机械后然后磁力贴上飞弹机器人，那个机械会首先回到对方场上，但不触发飞弹机器人的特效
#暂时控制+永久控制 = 永久控制
#暂时控制 + 暂时控制 = 每一次暂时控制者得到
class ShadowMadness(Spell):
	Class, name = "Priest", "Shadow Madness"
	requireTarget, mana = True, 3
	index = "Classic~Priest~Spell~3~Shadow Madness"
	description = "Gain control of an enemy minion with 3 or less Attack until end of turn"
	def available(self):
		return self.selectableEnemyMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.ID != self.ID and target.attack < 4 and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target and target.onBoard and target.ID != self.ID:
			PRINT(self.Game, "Shadow Madness is cast and gains control of enemy minion %s this turn."%target.name)
			self.Game.minionSwitchSide(target, activity="Borrow")
		return target
		
#这个扳机的目标：当随从在回合结束时有多个同类扳机，只会触发第一个，这个可以通过回合ID和自身ID是否符合来决定
class Trigger_ShadowMadness(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["TurnEnds"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		#只有当前要结束的回合的ID与自身ID相同的时候可以触发，于是即使有多个同类扳机也只有一个会触发。
		return self.entity.onBoard and ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self.entity.Game, "At the end of turn, temporarily controlled minion %s is returned to the other side."%self.entity.name)
		#Game的minionSwitchSide方法会自行移除所有的此类扳机。
		self.entity.Game.minionSwitchSide(self.entity, activity="Return")
		for trigger in self.entity.triggersonBoard:
			if type(trigger) == Trigger_ShadowMadness:
				trigger.disconnect()
				
				
class Lightspawn(Minion):
	Class, race, name = "Priest", "", "Lightspawn"
	mana, attack, health = 4, 0, 5
	index = "Classic~Priest~Minion~4~0~5~None~Lightspawn"
	requireTarget, keyWord, description = False, "", "This minion's Attack is always equal to its Health"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.appearResponse.append(self.setAttackEqualtoHealth)
		self.triggers["StatChanges"] = [self.setAttackEqualtoHealth]
		
	def setAttackEqualtoHealth(self):
		if self.silenced == False and self.onBoard:
			self.attack = self.health
			
			
class MassDispel(Spell):
	Class, name = "Priest", "Mass Dispel"
	requireTarget, mana = False, 4
	index = "Classic~Priest~Spell~4~Mass Dispel"
	description = "Silence all enemy minions. Draw a card"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		PRINT(self.Game, "Mass Dispel is cast, silences all enemy minions and draws a card")
		for minion in self.Game.minionsonBoard(3-self.ID):
			minion.getsSilenced()
			
		self.Game.Hand_Deck.drawCard(self.ID)
		return None
		
		
class Mindgames(Spell):
	Class, name = "Priest", "Mindgames"
	requireTarget, mana = False, 4
	index = "Classic~Priest~Spell~4~Mindgames"
	description = "Put a copy of a random minion from your opponent's deck into the battlefield"
	def available(self):
		return self.Game.space(self.ID) > 0
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		enemyDeck = curGame.Hand_Deck.decks[3-self.ID]
		if curGame.mode == 0:
			if curGame.guides:
				i = curGame.guides.pop(0)
				if i < 0:
					PRINT(curGame, "Mindgames is cast but can only summon a 0/1 Shadow of Nothing")
					curGame.summon(ShadowofNothing(curGame, self.ID), -1, self.ID)
					return None
				else: minion = enemyDeck[i]
			else:
				minionsinDeck = [i for i, card in enumerate(enemyDeck) if card.type == "Minion"]
				if minionsinDeck:
					i = npchoice(minionsinDeck)
					minion = enemyDeck[i]
					curGame.fixedGuides.append(i)
				else:
					PRINT(curGame, "Mindgames is cast but can only summon a 0/1 Shadow of Nothing")
					curGame.fixedGuides.append(-1)
					curGame.summon(ShadowofNothing(curGame, self.ID), -1, self.ID)
					return None
			PRINT(curGame, "Mindgames is cast and copies minion %s from the opponent's deck."%minion.name)
			curGame.summon(minion.selfCopy(self.ID), -1, self.ID)
		return None
		
class ShadowofNothing(Minion):
	Class, race, name = "Priest", "", "Shadow of Nothing"
	mana, attack, health = 1, 0, 1
	index = "Classic~Priest~Minion~1~0~1~None~Shadow of Nothing~Uncollectible"
	requireTarget, keyWord, description = False, "", "Mindgames whiffed! Your opponent had no minions!"
	
	
class ShadowWordRuin(Spell):
	Class, name = "Priest", "Shadow Word: Ruin"
	requireTarget, mana = False, 4
	index = "Classic~Priest~Spell~4~Shadow Word: Ruin"
	description = "Destroy all minions with 5 or more Attack"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		PRINT(self.Game, "Shadow Word: Ruin is cast and destroys all minions with 5 or more Attack")
		for minion in self.Game.minionsonBoard(1) + self.Game.minionsonBoard(2):
			if minion.attack > 4:
				minion.dead = True
		return None
		
		
class TempleEnforcer(Minion):
	Class, race, name = "Priest", "", "Temple Enforcer"
	mana, attack, health = 5, 5, 6
	index = "Classic~Priest~Minion~5~5~6~None~Temple Enforcer~Battlecry"
	requireTarget, keyWord, description = True, "", "Battlecry: Give a friendly minion +3 health"
	
	def targetExists(self, choice=0):
		return self.selectableFriendlyMinionExists(choice)
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.ID == self.ID and target != self and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			PRINT(self.Game, "Temple Enforcer's battlecry gives friendly minion %s +3 health."%target.name)
			target.buffDebuff(0, 3)
		return target
		
		
class CabalShadowPriest(Minion):
	Class, race, name = "Priest", "", "Cabal Shadow Priest"
	mana, attack, health = 6, 4, 5
	index = "Classic~Priest~Minion~6~4~5~None~Cabal Shadow Priest~Battlecry"
	requireTarget, keyWord, description = True, "", "Battlecry: Take control of an enemy minion with 2 or less Attack"
	
	def targetExists(self, choice=0):
		return self.selectableEnemyMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.ID != self.ID and target.attack < 3 and target != self and target.onBoard
		
	#If the minion is shuffled into deck already, then nothing happens.
	#If the minion is returned to hand, move it from enemy hand into our hand.
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target and target.ID != self.ID:
			PRINT(self.Game, "Cabal Shadow Priest's battlecry gains control of enemy minion %s with 2 or less attack."%target.name)
			self.Game.minionSwitchSide(target)
		return target
		
		
class NatalieSeline(Minion):
	Class, race, name = "Priest", "", "Natalie Seline"
	mana, attack, health = 8, 8, 1
	index = "Classic~Priest~Minion~8~8~1~None~Natalie Seline~Battlecry"
	requireTarget, keyWord, description = True, "", "Battlecry: Destroy a minion and gain its Health"
	
	def targetExists(self, choice=0):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target != self and target.onBoard
		
	#If the minion is shuffled into deck already, then nothing happens.
	#If the minion is returned to hand, move it from enemy hand into our hand.
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			PRINT(self.Game, "Natalie Seline's battlecry destroys minion %s and lets the minion gain its Health"%target.name)
			healthGain = max(0, target.health)
			self.Game.destroyMinion(target)
			self.buffDebuff(0, healthGain)
		return target
		
	
"""Rogue cards"""
class Preparation(Spell):
	Class, name = "Rogue", "Preparation"
	requireTarget, mana = False, 0
	index = "Classic~Rogue~Spell~0~Preparation"
	description = "The next spell you cast this turn costs (2) less"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		PRINT(self.Game, "Preparation is cast and next spell this turn costs 2 less.")
		tempAura = YourNextSpellCosts2LessThisTurn(self.Game, self.ID)
		self.Game.Manas.CardAuras.append(tempAura)
		tempAura.auraAppears()
		return None
		
class YourNextSpellCosts2LessThisTurn(TempManaEffect):
	def __init__(self, Game, ID):
		self.Game, self.ID = Game, ID
		self.changeby, self.changeto = -2, -1
		self.temporary = True
		self.auraAffected = []
		
	def applicable(self, target):
		return target.ID == self.ID and target.type == "Spell"
		
	def selfCopy(self, recipientGame):
		return type(self)(recipientGame, self.ID)
		
		
class Shadowstep(Spell):
	Class, name = "Rogue", "Shadowstep"
	requireTarget, mana = True, 0
	index = "Classic~Rogue~Spell~0~Shadowstep"
	description = "Return a friendly minion to your hand. It costs (2) less"
	def targetExists(self, choice=0):
		return self.selectableFriendlyMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.ID == self.ID and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		#假设暗影步第二次生效时不会不在场上的随从生效
		if target and target.onBoard:
			PRINT(self.Game, "Shadowstep is cast and returns %s to owner's hand."%target.name)
			#假设那张随从在进入手牌前接受-2费效果。可以被娜迦海巫覆盖。
			manaMod = ManaModification(target, changeby=-2, changeto=-1)
			self.Game.returnMiniontoHand(target, keepDeathrattlesRegistered=False, manaModification=manaMod)
		return target
		
		
class Pilfer(Spell):
	Class, name = "Rogue", "Pilfer"
	requireTarget, mana = False, 1
	index = "Classic~Rogue~Spell~1~Pilfer"
	description = "Add a random card from another class to your hand"
	poolIdentifier = "Class Cards except Rogue"
	@classmethod
	def generatePool(cls, Game):
		classes, lists = [], []
		#考虑职业为中立的可能（拉格纳罗斯）
		for Class in Game.ClassesandNeutral:
			classes.append("Class Cards except " + Class)
			classPool = fixedList(Game.Classes)
			extractfrom(Class, classPool)
			for ele in classPool:
				lists.append(list(Game.ClassCards[ele].values()))
		return classes, lists #返回的包含“Class Cards except Hunter”等identifier的列表和其他职业卡表
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if curGame.mode == 0:
			if curGame.guides:
				card = curGame.guides.pop(0)
			else:
				key = "Class Cards except "+curGame.heroes[self.ID].Class
				card = npchoice(curGame.RNGPools[key])
				curGame.fixedGuides.append(card)
			PRINT(curGame, "Pilfer is cast and adds a random card from another class to player's hand.")
			curGame.Hand_Deck.addCardtoHand(card, self.ID, "CreateUsingType")
		return None
		
#Betrayal lets target deal damage to adjacent minions.
#Therefore, the overkill and lifesteal can be triggered.
class Betrayal(Spell):
	Class, name = "Rogue", "Betrayal"
	requireTarget, mana = True, 2
	index = "Classic~Rogue~Spell~2~Betrayal"
	description = "Force a minion to deal its damage to minions next to it"
	def available(self):
		return self.selectableEnemyMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.ID != self.ID and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			PRINT(self.Game, "Betrayal is cast and lets target minion %s deals damage equal to its attack to adjacent minions."%target.name)
			adjacentMinions, distribution = self.Game.adjacentMinions2(target)
			attack = target.attack
			target.dealsAOE(adjacentMinions, [attack for minion in adjacentMinions])
		return target
		
		
class ColdBlood(Spell):
	Class, name = "Rogue", "Cold Blood"
	requireTarget, mana = True, 2
	index = "Classic~Rogue~Spell~2~Cold Blood~Combo"
	description = "Give a minion +2 Attack. Combo: +4 Attack instead"
	def effectCanTrigger(self):
		self.effectViable = self.Game.Counters.numCardsPlayedThisTurn[self.ID] > 0
		
	def targetExists(self, choice=0):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			if self.Game.Counters.numCardsPlayedThisTurn[self.ID] > 0:
				PRINT(self.Game, "Cold Blood is cast and gives %s +4 attack"%target.name)
				target.buffDebuff(4, 0)
			else:
				PRINT(self.Game, "Cold Blood is cast and gives %s +2 attack"%target.name)
				target.buffDebuff(2, 0)
		return target
		
		
class DefiasRingleader(Minion):
	Class, race, name = "Rogue", "", "Defias Ringleader"
	mana, attack, health = 2, 2, 2
	index = "Classic~Rogue~Minion~2~2~2~None~Defias Ringleader~Combo"
	requireTarget, keyWord, description = False, "", "Combo: Summon a 2/1 Defias Bandit"
	
	def effectCanTrigger(self):
		self.effectViable = self.Game.Counters.numCardsPlayedThisTurn[self.ID] > 0
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if self.Game.Counters.numCardsPlayedThisTurn[self.ID] > 0:
			PRINT(self.Game, "Defias Ringleader' Combo triggers and summons a 2/1 Defias Bandit.")
			pos = self.position + 1 if self.onBoard else -1
			self.Game.summon(DefiasBandit(self.Game, self.ID), pos, self.ID)
		return None
		
class DefiasBandit(Minion):
	Class, race, name = "Rogue", "", "Defias Bandit"
	mana, attack, health = 1, 2, 1
	index = "Classic~Rogue~Minion~1~2~1~None~Defias Bandit~Uncollectible"
	requireTarget, keyWord, description = False, "", ""
	
	
class Eviscerate(Spell):
	Class, name = "Rogue", "Eviscerate"
	requireTarget, mana = True, 2
	index = "Classic~Rogue~Spell~2~Eviscerate~Combo"
	description = "Deal 2 damage. Combo: Deal 4 instead"
	def effectCanTrigger(self):
		self.effectViable = self.Game.Counters.numCardsPlayedThisTurn[self.ID] > 0
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			if self.Game.Counters.numCardsPlayedThisTurn[self.ID] > 0:
				damage = (4 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			else:
				damage = (2 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
				
			PRINT(self.Game, "Eviscerate is cast and deals %d damage to %s"%(damage, target.name))
			self.dealsDamage(target, damage)
		return target
		
		
class PatientAssassin(Minion):
	Class, race, name = "Rogue", "", "Patient Assassin"
	mana, attack, health = 2, 1, 1
	index = "Classic~Rogue~Minion~2~1~1~None~Patient Assassin~Poisonous~Stealth"
	requireTarget, keyWord, description = False, "Stealth,Poisonous", "Stealth, Poisonous"
	
	
class EdwinVanCleef(Minion):
	Class, race, name = "Rogue", "", "Edwin VanCleef"
	mana, attack, health = 3, 2, 2
	index = "Classic~Rogue~Minion~3~2~2~None~Edwin VanCleef~Combo~Legendary"
	requireTarget, keyWord, description = False, "", "Combo: Gain +2/+2 for each other card you've played this turn"
	
	def effectCanTrigger(self):
		self.effectViable = self.Game.Counters.numCardsPlayedThisTurn[self.ID] > 0
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		#Dead minions or minions in deck can't be buffed or reset.
		if self.Game.Counters.numCardsPlayedThisTurn[self.ID] > 0:
			numCardsPlayed = len(self.Game.Counters.cardsPlayedThisTurn[self.ID]["Indices"])
			PRINT(self.Game, "Edwin VanCleef's Combo triggers and gains +2/+2 for each card player played this turn.")
			statGain = 2 * numCardsPlayed
			self.buffDebuff(statGain, statGain)
		return None
		
		
class Headcrack(Spell):
	Class, name = "Rogue", "Headcrack"
	requireTarget, mana = False, 3
	index = "Classic~Rogue~Spell~3~Headcrack~Combo"
	description = "Deal 2 damage to the enemy hero. Combo: Return this to your hand next turn."
	
	def effectCanTrigger(self):
		self.effectViable = self.Game.Counters.numCardsPlayedThisTurn[self.ID] > 0
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		damage = (2 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		PRINT(self.Game, "Headcrack is cast and deals %d damage to the enemy hero."%damage)
		self.dealsDamage(self.Game.heroes[3-self.ID], damage)
		if self.Game.Counters.numCardsPlayedThisTurn[self.ID] > 0:
			trigger = Trigger_HeadCrack(self)
			trigger.ID = self.ID
			trigger.connect()
		return None
		
class Trigger_HeadCrack(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["TurnStarts"])
		self.ID = 1
		
	def connect(self):
		for signal in self.signals:
			self.entity.Game.triggersonBoard[self.ID].append((self, signal))
			
	def disconnect(self):
		for signal in self.signals:
			extractfrom((self, signal), self.entity.Game.triggersonBoard[self.ID])
			
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return ID == self.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self.entity.Game, "At the start of turn, Headcrack is added to players hand.")
		self.entity.Game.Hand_Deck.addCardtoHand(Headcrack, self.ID, "CreateUsingType")
		self.disconnect()
		
		
class PerditionsBlade(Weapon):
	Class, name, description = "Rogue", "Perdition's Blade", "Battlecry: Deal 1 damage. Combo: Deal 2 instead"
	mana, attack, durability = 3, 2, 2
	index = "Classic~Rogue~Weapon~3~2~2~Perdition's Blade~Combo~Battlecry"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.requireTarget = True
		
	def effectCanTrigger(self):
		self.effectViable = self.Game.Counters.numCardsPlayedThisTurn[self.ID] > 0
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			if self.Game.Counters.numCardsPlayedThisTurn[self.ID] > 0:
				damage = 2
			else:
				damage = 1
			PRINT(self.Game, "Perdition's Blade's battlecry deals %d damage to %s"%(damage, target.name))
			self.dealsDamage(target, damage)
		#For the sake of Shudderwock	
		return target
		
		
class SI7Agent(Minion):
	Class, race, name = "Rogue", "", "SI:7 Agent"
	mana, attack, health = 3, 3, 3
	index = "Classic~Rogue~Minion~3~3~3~None~SI:7 Agent~Combo"
	requireTarget, keyWord, description = True, "", "Combo: Deal 2 damage"
	
	def returnTrue(self, choice=0):
		return self.Game.Counters.numCardsPlayedThisTurn[self.ID] > 0
		
	def effectCanTrigger(self):
		self.effectViable = self.Game.Counters.numCardsPlayedThisTurn[self.ID] > 0
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target and self.Game.Counters.numCardsPlayedThisTurn[self.ID] > 0:
			PRINT(self.Game, "SI:7 Agent's Combo triggers and deals 2 damage to %s"%target.name)
			self.dealsDamage(target, 2)
		return target
		
#This spell is the subject that deals damage, can be boosted by Spell Damage, and the destroyed weapon won't respond to dealing damage.
#Therefore, Lifesteal and Overkill won't be triggered by this spell.
#However, Doomerang let weapon deal the damage and won't be boosted by Spell Damage.
class BladeFlurry(Spell):
	Class, name = "Rogue",  "Blade Flurry"
	requireTarget, mana = False, 4
	index = "Classic~Rogue~Spell~4~Blade Flurry"
	description = "Destroy your weapon and deal its damage to all enemy minions"
	def available(self):
		return self.Game.availableWeapon(self.ID) is not None
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		weapon = self.Game.availableWeapon(self.ID)
		if weapon:
			damage = (weapon.attack + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			weapon.destroyed()
			PRINT(self.Game, "Blade Flurry is cast, destroys player's weapon and deals %d damage to all enemy minions."%damage)
			targets = self.Game.minionsonBoard(3-self.ID)
			self.dealsAOE(targets, [damage for minion in targets])
		return None
		
		
class MasterofDisguise(Minion):
	Class, race, name = "Rogue", "", "Master of Disguise"
	mana, attack, health = 4, 4, 4
	index = "Classic~Rogue~Minion~4~4~4~None~Master of Disguise~Battlecry"
	requireTarget, keyWord, description = True, "", "Battlecry: Give a friendly minion Stealth until your next turn"
	
	def targetExists(self, choice=0):
		return self.selectableFriendlyMinionExists(choice)
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.ID == self.ID and target != self and target.onBoard
		
	#Only onBoard or inHand minions can be given keywords.
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target and (target.onBoard or target.inHand):
			PRINT(self.Game, "Master of Disguise's battlecry gives friendly minion %s Stealth until next turn."%target.name)
			target.status["Temp Stealth"] = 1
		return target
		
		
class Kidnapper(Minion):
	Class, race, name = "Rogue", "", "Kidnapper"
	mana, attack, health = 6, 5, 3
	index = "Classic~Rogue~Minion~6~5~3~None~Kidnapper~Combo"
	requireTarget, keyWord, description = True, "", "Combo: Return a minion to its owner's hand"
	
	def returnTrue(self, choice=0):
		return self.Game.Counters.numCardsPlayedThisTurn[self.ID] > 0
		
	def effectCanTrigger(self):
		self.effectViable = self.Game.Counters.numCardsPlayedThisTurn[self.ID] > 0
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
		
	def targetExists(self, choice=0):
		return self.selectableMinionExists(choice)
	#测试洗回牌库的随从是否会加入手牌。
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target and self.Game.Counters.numCardsPlayedThisTurn[self.ID] > 0:
			PRINT(self.Game, "Kidnapper's Combo effect returns minion %s to its owner's hand"%target.name)
			self.Game.returnMiniontoHand(target)
		return target
		
		
"""Shaman cards"""
#Overload minions' played() don't invoke the effectwhenPlayed()
#Overload is not part of the effectwhenPlayed(). Shudderwock repeating Sandstorm Elemental's battlecry won't overload the mana.
class DustDevil(Minion):
	Class, race, name = "Shaman", "Elemental", "Dust Devil"
	mana, attack, health = 1, 3, 1
	index = "Classic~Shaman~Minion~1~3~1~Elemental~Dust Devil~Overload~Windfury"
	requireTarget, keyWord, description = False, "Windfury", "Windfury. Overload: (2)"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.overload = 2
		
		
class EarthShock(Spell):
	Class, name = "Shaman", "Earth Shock"
	requireTarget, mana = True, 1
	index = "Classic~Shaman~Spell~1~Earth Shock"
	description = "Silence a minion. Then deal 1 damage to it."
	
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			damage = (1 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			PRINT(self.Game, "EarthShock is cast and silences %s before dealing %d damage to it."%(target.name, damage))
			target.getsSilenced()
			self.dealsDamage(target, damage)
		return target
		
		
class ForkedLightning(Spell):
	Class, name = "Shaman", "Forked Lightning"
	requireTarget, mana = False, 1
	index = "Classic~Shaman~Spell~1~Forked Lightning~Overload"
	description = "Deal 2 damage to 2 random enemy minions. Overload: (2)"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.overload = 2
		
	def available(self):
		return self.Game.minionsonBoard(3-self.ID) != []
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		damage = (2 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
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
				PRINT(curGame, "Forked Lightning is cast and deals {} damage to enemy minions {}".format(damage, minions))
				self.dealsAOE(minions, [damage]*len(minions))
		return None
		
		
class LightningBolt(Spell):
	Class, name = "Shaman", "Lightning Bolt"
	requireTarget, mana = True, 1
	index = "Classic~Shaman~Spell~1~Lightning Bolt~Overload"
	description = "Deal 3 damage. Overload: (1)"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.overload = 1
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			damage = (3 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			PRINT(self.Game, "Lightning Bolt is cast and deals %d damage to %s"%(damage, target.name))
			self.dealsDamage(target, damage)
		return target
		
		
class AncestralSpirit(Spell):
	Class, name = "Shaman",  "Ancestral Spirit"
	requireTarget, mana = True, 2
	index = "Classic~Shaman~Spell~2~Ancestral Spirit"
	description = "Give a minion 'Deathrattle: Resummon this minion.'"
	def targetExists(self, choice=0):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target and (target.onBoard or target.inHand):
			PRINT(self.Game, "Ancestral Spirit gives minion %s deathrattle: Summon this minion again."%target.name)
			trigger = ResummonMinion(target)
			target.deathrattles.append(trigger)
			if target.onBoard:
				trigger.connect()
		return target
		
class ResummonMinion(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self.entity.Game, "Deathrattle: Resummon the minion %s triggers."%self.entity.name)
		newMinion = type(self.entity)(self.entity.Game, self.entity.ID)
		self.entity.Game.summon(newMinion, self.entity.position+1, self.entity.ID)
		
		
class StormforgedAxe(Weapon):
	Class, name, description = "Shaman", "Stormforged Axe", "Overload: (1)"
	mana, attack, durability = 2, 2, 3
	index = "Classic~Shaman~Weapon~2~2~3~Stormforged Axe~Overload"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.overload = 1
		
		
class FarSight(Spell):
	Class, name = "Shaman", "Far Sight"
	requireTarget, mana = False, 3
	index = "Classic~Shaman~Spell~3~Far Sight"
	description = "Draw a card. That card costs (3) less"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		PRINT(self.Game, "Far Sight is cast and draws a card. It costs 3 less.")
		card, mana = self.Game.Hand_Deck.drawCard(self.ID)
		if card:
			ManaModification(card, changeby=-3, changeto=-1).applies()
			self.Game.Manas.calcMana_Single(card)
		return None
		
		
class FeralSpirit(Spell):
	Class, name = "Shaman", "Feral Spirit"
	requireTarget, mana = False, 3
	index = "Classic~Shaman~Spell~3~Feral Spirit~Overload"
	description = "Summon two 2/3 Spirit Wolves with Taunt. Overload: (2)"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.overload = 2
		
	def available(self):
		return self.Game.space(self.ID) > 0
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		PRINT(self.Game, "Feral Spirit is cast and summons two 2/3 Spirit Wolf with Taunt.")
		self.Game.summon([SpiritWolf(self.Game, self.ID) for i in range(2)], (-1, "totheRightEnd"), self.ID)
		return None
		
class SpiritWolf(Minion):
	Class, race, name = "Shaman", "", "Spirit Wolf"
	mana, attack, health = 2, 2, 3
	index = "Classic~Shaman~Minion~2~2~3~None~Spirit Wolf~Taunt~Uncollectible"
	requireTarget, keyWord, description = False, "Taunt", "Taunt"
	
#Overload spells targeting adjacent minions will overload multiple times.
#Overload spells repeated by Electra Stormsurge will also overload twice.
class LavaBurst(Spell):
	Class, name = "Shaman", "Lava Burst"
	requireTarget, mana = True, 3
	index = "Classic~Shaman~Spell~3~Lava Burst~Overload"
	description = "Deal 5 damage. Overload: (2)"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.overload = 2
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			damage = (5 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			PRINT(self.Game, "Lava Burst is cast and deals %d damage to %s"%(damage, target.name))
			self.dealsDamage(target, damage)
		return target
		
		
class LightningStorm(Spell):
	Class, name = "Shaman", "Lightning Storm"
	requireTarget, mana = False, 3
	index = "Classic~Shaman~Spell~3~Lightning Storm~Overload"
	description = "Deal 2~3 damage to all enemy minions. Overload: (2)"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.overload = 2
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		targets = curGame.minionsonBoard(3-self.ID)
		if targets:
			if curGame.mode == 0:
				if curGame.guides:
					damages = list(curGame.guides.pop(0))
				else:
					damage2 = (2 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
					damage3 = (3 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
					damages = [npchoice([damage2, damage3]) for minion in targets]
					curGame.fixedGuides.append(tuple(damages))
				PRINT(curGame, "Lightning Storm is cast and randomly deals 2~3 damage to enemy minions.")
				self.dealsAOE(targets, damages)
		return None
		
		
class ManaTideTotem(Minion):
	Class, race, name = "Shaman", "Totem", "Mana Tide Totem"
	mana, attack, health = 3, 0, 3
	index = "Classic~Shaman~Minion~3~0~3~Totem~Mana Tide Totem"
	requireTarget, keyWord, description = False, "", "At the end of your turn, draw a card"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_ManaTideTotem(self)]
		
class Trigger_ManaTideTotem(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["TurnEnds"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self.entity.Game, "At the end of turn, Mana Tide Totem lets player draw a card.")
		self.entity.Game.Hand_Deck.drawCard(self.entity.ID)
		
		
class UnboundElemental(Minion):
	Class, race, name = "Shaman", "Elemental", "Unbound Elemental"
	mana, attack, health = 3, 2, 4
	index = "Classic~Shaman~Minion~3~2~4~Elemental~Unbound Elemental"
	requireTarget, keyWord, description = False, "", "Whenever you play a card with Overload, gain +1/+1"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_UnboundElemental(self)]
		
class Trigger_UnboundElemental(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionPlayed", "SpellPlayed", "WeaponPlayed", "HeroCardPlayed"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject.ID == self.entity.ID and subject.overload > 0
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self.entity.Game, "Player plays a card %s with Overload and %s gains +1/+1."%(subject.name, self.entity.name))
		self.entity.buffDebuff(1, 1)
		
		
class Doomhammer(Weapon):
	Class, name, description = "Shaman", "Doomhammer", "Windfury, Overload: (2)"
	mana, attack, durability = 5, 2, 8
	index = "Classic~Shaman~Weapon~5~2~8~Doomhammer~Windfury~Overload"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.keyWords["Windfury"] = 1
		self.overload = 2
		
		
class EarthElemental(Minion):
	Class, race, name = "Shaman", "Elemental", "Earth Elemental"
	mana, attack, health = 5, 7, 8
	index = "Classic~Shaman~Minion~5~7~8~Elemental~Earth Elemental~Taunt~Overload"
	requireTarget, keyWord, description = False, "Taunt", "Taunt. Overload: (3)"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.overload = 3
		
		
class AlAkirtheWindlord(Minion):
	Class, race, name = "Shaman", "Elemental", "Al'Akir the Windlord"
	mana, attack, health = 8, 3, 5
	index = "Classic~Shaman~Minion~8~3~5~Elemental~Al'Akir the Windlord~Taunt~Charge~Windfury~Divine Shield~Legendary"
	requireTarget, keyWord, description = False, "Taunt,Charge,Divine Shield,Windfury", "Taunt,Charge,Divine Shield,Windfury"
	
	
"""Warlock cards"""
class BloodImp(Minion):
	Class, race, name = "Warlock", "Demon", "Blood Imp"
	mana, attack, health = 1, 0, 1
	index = "Classic~Warlock~Minion~1~0~1~Demon~Blood Imp~Stealth"
	requireTarget, keyWord, description = False, "Stealth", "At the end of your turn, give another random friendly minion +1 Health"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_BloodImp(self)]
		
class Trigger_BloodImp(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["TurnEnds"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		curGame = self.entity.Game
		if curGame.mode == 0:
			if curGame.guides:
				i = curGame.guides.pop(0)
				if i < 0: return
				else: target = curGame.minions[self.entity.ID][i]
			else:
				targets = curGame.minionsonBoard(self.entity.ID)
				extractfrom(self.entity, targets)
				if targets:
					target = npchoice(targets)
					curGame.fixedGuides.append(target.position)
				else:
					curGame.fixedGuides.append(-1)
					return
			PRINT(curGame, "At the end of turn, Blood Imp gvies another random friendly minion %s +1 Health."%target.name)
			target.buffDebuff(0, 1)
				
				
class CalloftheVoid(Spell):
	Class, name = "Warlock", "Call of the Void"
	requireTarget, mana = False, 1
	index = "Classic~Warlock~Spell~1~Call of the Void"
	description = "Add a random Demon to your hand"
	poolIdentifier = "Demons"
	@classmethod
	def generatePool(cls, Game):
		return "Demons", list(Game.MinionswithRace["Demon"].values())
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if curGame.mode == 0:
			if curGame.guides:
				demon = curGame.guides.pop(0)
			else:
				demon = npchoice(curGame.RNGPools["Demons"])
				curGame.fixedGuides.append(demon)
			PRINT(curGame, "Call of the Void is cast and adds a random Demon to player's hand.")	
			curGame.Hand_Deck.addCardtoHand(demon, self.ID, "CreateUsingType")
		return None
		
		
class FlameImp(Minion):
	Class, race, name = "Warlock", "Demon", "Flame Imp"
	mana, attack, health = 1, 3, 2
	index = "Classic~Warlock~Minion~1~3~2~Demon~Flame Imp~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Deal 3 damage to your hero"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		PRINT(self.Game, "Flame Imp's battlecry deals 3 damage to the player.")
		self.dealsDamage(self.Game.heroes[self.ID], 3)
		return None
		
		
class Demonfire(Spell):
	Class, name = "Warlock", "Demonfire"
	requireTarget, mana = True, 2
	index = "Classic~Warlock~Spell~2~Demonfire"
	description = "Deal 2 damage to a minion. If it's friendly Demon, give it +2/+2 instead"
	def targetExists(self, choice=0):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			if "Demon" in target.race and target.ID == self.ID:
				PRINT(self.Game, "Demonfire gives friendly demon %s +2/+2"%target.name)
				target.buffDebuff(2, 2)
			else:
				damage = (2 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
				PRINT(self.Game, "Demonfire is cast and deals %d damage to %s"%(damage, target.name))
				self.dealsDamage(target, damage)
		return target
		
#If the hands are full, both of the cards will be milled. Tested with Archmage Vargoth.
class SenseDemons(Spell):
	Class, name = "Warlock", "Sense Demons"
	requireTarget, mana = False, 3
	index = "Classic~Warlock~Spell~3~Sense Demons"
	description = "Draw 2 Demons from your deck"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		ownDeck = curGame.Hand_Deck.decks[self.ID]
		for num in range(2):
			if curGame.mode == 0:
				if curGame.guides:
					i = curGame.guides.pop(0)
					if i < 0:
						curGame.Hand_Deck.addCardtoHand(WorthlessImp, self.ID, "CreateUsingType")
						continue
				else:
					demonsinDeck = [i for i, card in enumerate(ownDeck) if card.type == "Minion" and "Demon" in card.race]
					if demonsinDeck:
						i = npchoice(demonsinDeck)
						curGame.fixedGuides.append(i)
					else:
						curGame.fixedGuides.append(-1)
						curGame.Hand_Deck.addCardtoHand(WorthlessImp, self.ID, "CreateUsingType")
						continue
				PRINT(curGame, "Sense Demons lets player draw a Demon from deck")
				curGame.Hand_Deck.drawCard(self.ID, i)
		return None
		
class WorthlessImp(Minion):
	Class, race, name = "Warlock", "", "Worthless Imp"
	mana, attack, health = 1, 1, 1
	index = "Classic~Warlock~Minion~1~1~1~Demon~Worthless Imp~Uncollectible"
	requireTarget, keyWord, description = False, "", ""
	
	
class SummoningPortal(Minion):
	Class, race, name = "Warlock", "", "Summoning Portal"
	mana, attack, health = 4, 0, 4
	index = "Classic~Warlock~Minion~4~0~4~None~Summoning Portal"
	requireTarget, keyWord, description = False, "", "Your minions cost (2) less, but not less than (1)"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.auras["Mana Aura"] = ManaAura_Dealer(self, changeby=-2, changeto=-1, lowerbound=1)
		
	def manaAuraApplicable(self, subject): #ID用于判定是否是我方手中的随从
		return subject.type == "Minion" and subject.ID == self.ID
		
		
class Felguard(Minion):
	Class, race, name = "Warlock", "Demon", "Felguard"
	mana, attack, health = 3, 3, 5
	index = "Classic~Warlock~Minion~3~3~5~Demon~Felguard~Taunt~Battlecry"
	requireTarget, keyWord, description = False, "Taunt", "Taunt. Battlecry: Destroy one of your Mana Crystals"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		PRINT(self.Game, "Felguard's battlecry destroys a mana crystal.")
		self.Game.Manas.destroyManaCrystal(1, self.ID)
		return None
		
		
class VoidTerror(Minion):
	Class, race, name = "Warlock", "Demon", "Void Terror"
	mana, attack, health = 3, 3, 3
	index = "Classic~Warlock~Minion~3~3~3~Demon~Void Terror~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Destroy both adjacent minions and gain their Attack and Health"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if self.onBoard: #Can't trigger if returned to hand already, since cards in hand don't have adjacent minions on board.
			adjacentMinions, distribution = self.Game.adjacentMinions2(self)
			if adjacentMinions != []:
				attackGain = 0
				healthGain = 0
				for minion in adjacentMinions:
					attackGain += max(0, minion.attack)
					healthGain += max(0, minion.health)
					minion.dead = True
					
				PRINT(self.Game, "Void Terror's battlecry lets minion destroy adjacent minions and gain their stats.")
				self.buffDebuff(attackGain, healthGain)
		return None
		
		
class PitLord(Minion):
	Class, race, name = "Warlock", "Demon", "Pit Lord"
	mana, attack, health = 4, 5, 6
	index = "Classic~Warlock~Minion~4~5~6~Demon~Pit Lord~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Deal 5 damage to your hero"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		PRINT(self.Game, "Pit Lord's battlecry deals 5 damage to player.")
		self.dealsDamage(self.Game.heroes[self.ID], 5)
		return None
		
		
class Shadowflame(Spell):
	Class, name = "Warlock", "Shadowflame"
	requireTarget, mana = True, 4
	index = "Classic~Warlock~Spell~4~Shadowflame"
	description = "Destroy a friendly minion and deals its Attack damage to all enemy minions"
	def targetExists(self, choice=0):
		return self.selectableFriendlyMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.ID == self.ID and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			damage = (max(0, target.attack) + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			target.dead = True
			PRINT(self.Game, "Shadowflame is cast, destroys friendly minion %s and deals %d damage to all enemy minions"%(target.name, damage))
			targets = self.Game.minionsonBoard(3-self.ID)
			self.dealsAOE(targets, [damage for minion in targets])
		return target
		
		
class BaneofDoom(Spell):
	Class, name = "Warlock", "Bane of Doom"
	requireTarget, mana = True, 5
	index = "Classic~Warlock~Spell~5~Bane of Doom"
	description = "Deal 2 damage to a character. It that kills it, summon a random Demon"
	poolIdentifier = "Demons to Summon"
	@classmethod
	def generatePool(cls, Game):
		return "Demons to Summon", list(Game.MinionswithRace["Demon"].values())
		
	def targetExists(self, choice=0):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			curGame = self.Game
			damage = (2 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			PRINT(curGame, "Bane of Doom is cast and deals %d damage to %s"%(damage, target.name))
			objtoTakeDamage, damageActual = self.dealsDamage(target, damage)
			if (objtoTakeDamage.health < 1 or objtoTakeDamage.dead) and curGame.space(self.ID) > 0:
				if curGame.mode == 0:
					if curGame.guides:
						demon = curGame.guides.pop(0)
					else:
						demon = npchoice(curGame.RNGPools["Demons to Summon"])
						curGame.fixedGuides.append(demon)
					PRINT(curGame, "Bane of Doom kills the target minion and summons random demon %s."%demon.name)
					curGame.summon(demon(curGame, self.ID), -1, self.ID)
		return target
		
		
class SiphonSoul(Spell):
	Class, name = "Warlock", "Siphon Soul"
	requireTarget, mana = True, 6
	index = "Classic~Warlock~Spell~6~Siphon Soul"
	description = "Destroy a minion. Restore 3 Health to your hero"
	def targetExists(self, choice=0):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			heal = 3 * (2 ** self.countHealDouble())
			PRINT(self.Game, "Siphon Soul is cast and destroys minion %s. Then restores %d health to player."%(target.name, heal))
			target.dead = True
			self.restoresHealth(self.Game.heroes[self.ID], heal)
		return target
		
		
class Siegebreaker(Minion):
	Class, race, name = "Warlock", "Demon", "Siegebreaker"
	mana, attack, health = 7, 5, 8
	index = "Classic~Warlock~Minion~7~5~8~Demon~Siegebreaker~Taunt"
	requireTarget, keyWord, description = False, "Taunt", "Your other Demons have +1 Attack"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.auras["Buff Aura"] = BuffAura_Dealer_All(self, 1, 0)
		
	def applicable(self, target):
		return "Demon" in target.race
		
		
class TwistingNether(Spell):
	Class, name = "Warlock", "Twisting Nether"
	requireTarget, mana = False, 8
	index = "Classic~Warlock~Spell~8~Twisting Nether"
	description = "Destroy all minions"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		PRINT(self.Game, "Twisting Nether is cast and destroys all minions.")
		for minion in self.Game.minionsonBoard(1) + self.Game.minionsonBoard(2):
			minion.dead = True
		return None
		
#Won't trigger Knife Juggler, but will trigger Illidan Stormrage
#Will trigger Mirror Entity, however.
class LordJaraxxus(Minion):
	Class, race, name = "Warlock", "Demon", "Lord Jaraxxus"
	mana, attack, health = 9, 3, 15
	index = "Classic~Warlock~Minion~9~3~15~Demon~Lord Jaraxxus~Battlecry~Legendary"
	requireTarget, keyWord, description = False, "", "Battlecry: Destroy your hero and replace it with Lord Jaraxxus"
	
	#打出过程：如果大王被提前消灭了，则不会触发变身过程。此时应该返回self，成为一个普通的早夭随从。、
	#如果大王留在场上或者被返回手牌，则此时应该会变身成为英雄，返回应该是None
	
	#If invoked by Shudderwock, then Shudderwock will transform and replace your hero with Jaraxxus.
	#Then Shudderwock's battlecry is stopped.
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		PRINT(self.Game, "Lord Jaraxxus' battlecry replaces player's hero with Lord Jaraxxus.")
		if self.inHand: #Returned to hand. Assume the card in hand is gone and then hero still gets replaced.
			self.Game.Hand_Deck.extractfromHand(self)
			LordJaraxxus_Hero(self.Game, self.ID).replaceHero()
		elif self.onBoard:
			self.disappears()
			self.Game.removeMinionorWeapon(self)
			LordJaraxxus_Hero(self.Game, self.ID).replaceHero()
			PRINT(self.Game, "The weapon is ", self.Game.availableWeapon(self.ID))
		if self.Game.minionPlayed == self:
			self.Game.minionPlayed = None
		return None #If Jaraxxus is killed before battlecry, it won't trigger
		
class Infernal(Minion):
	Class, race, name = "Warlock", "Demon", "Infernal"
	mana, attack, health = 6, 6, 6
	index = "Classic~Warlock~Minion~6~6~6~Demon~Infernal~Uncollectible"
	requireTarget, keyWord, description = False, "", ""
	
class INFERNO(HeroPower):
	mana, name, requireTarget = 2, "INFERNO!", False
	index = "Warlock~Hero Power~2~INFERNO!"
	description = "Summon a 6/6 Infernal"
	def available(self, choice=0):
		if self.heroPowerTimes >= self.heroPowerChances_base + self.heroPowerChances_extra:
			return False
		if self.Game.space(self.ID) < 1:
			return False
		return True
		
	def effect(self, target=None, choice=0):
		PRINT(self.Game, "Hero Power INFERNO! summons a 6/6 Infernal")
		self.Game.summon(Infernal(self.Game, self.ID), -1, self.ID, "")
		return 0
		
class BloodFury(Weapon):
	Class, name, description = "Warlock", "Blood Fury", ""
	mana, attack, durability = 3, 3, 8
	index = "Classic~Warlock~Weapon~3~3~8~Blood Fury~Uncollectible"
	
class LordJaraxxus_Hero(Hero):
	mana, weapon, description = 0, BloodFury, ""
	Class, name, heroPower, armor = "Warlock", "Lord Jaraxxus", INFERNO, 0
	index = "Classic~Warlock~Hero Card~9~Lord Jaraxxus~Battlecry~Uncollectible"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.health, self.health_upper, self.armor = 15, 15, 0
		
		
"""Warrior cards"""
class InnerRage(Spell):
	Class, name = "Warrior", "Inner Rage"
	requireTarget, mana = True, 0
	index = "Classic~Warrior~Spell~0~Inner Rage"
	description = "Deal 1 damage to a minion and give it +2 Attack"
	def targetExists(self, choice=0):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			damage = (1 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			PRINT(self.Game, "Inner Rage is cast and deals %d damage to %s and gives it +2 attack."%(damage, target.name))
			self.dealsDamage(target, damage)
			target.buffDebuff(2, 0)
		return target
		
		
class ShieldSlam(Spell):
	Class, name = "Warrior", "Shield Slam"
	requireTarget, mana = True, 1
	index = "Classic~Warrior~Spell~1~Shield Slam"
	description = "Deal 1 damage to a minion for each Armor you have"
	
	def targetExists(self, choice=0):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			damage = (self.Game.heroes[self.ID].armor + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			PRINT(self.Game, "Shield Slam is cast and deals %d damage to %s"%(damage, target.name))
			self.dealsDamage(target, damage)
		return target
		
		
class Upgrade(Spell):
	Class, name = "Warrior", "Upgrade!"
	requireTarget, mana = False, 1
	index = "Classic~Warrior~Spell~1~Upgrade!"
	description = "If your have a weapon, give it +1/+1. Otherwise, equip a 1/3 weapon"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		weapon = self.Game.availableWeapon(self.ID)
		if weapon == None:
			PRINT(self.Game, "Upgrade! is cast and player equips a 1/3 weapon.")
			self.Game.equipWeapon(HeavyAxe(self.Game, self.ID))
		else:
			PRINT(self.Game, "Upgrade! is cast and player's weapon gains +1/+1.")
			weapon.gainStat(1, 1)
		return None
		
class HeavyAxe(Weapon):
	Class, name, description = "Warrior", "Heavy Axe", ""
	mana, attack, durability = 1, 1, 3
	index = "Classic~Warrior~Weapon~1~1~3~Heavy Axe~Uncollectible"
	
	
class Armorsmith(Minion):
	Class, race, name = "Warrior", "", "Armorsmith"
	mana, attack, health = 2, 1, 4
	index = "Classic~Warrior~Minion~2~1~4~None~Armorsmith"
	requireTarget, keyWord, description = False, "", "Whenever a friendly minion takes damage, gain +1 Armor"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_Armorsmith(self)]
		
class Trigger_Armorsmith(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionTakesDamage"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and target.ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self.entity.Game, "Friendly minion %s takes damage and %s lets player gain 1 Armor."%(target.name, self.entity.name))
		self.entity.Game.heroes[self.entity.ID].gainsArmor(1)
		
		
class BattleRage(Spell):
	Class, name = "Warrior", "Battle Rage"
	requireTarget, mana = False, 2
	index = "Classic~Warrior~Spell~2~Battle Rage"
	description = "Draw a card for each damaged friendly character"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		PRINT(self.Game, "Battle Rage is cast and player draws a card for each damaged friendly.")
		numDamagedCharacters = 0
		for minion in self.Game.minionsonBoard(self.ID):
			if minion.health < minion.health_upper:
				numDamagedCharacters += 1
		if self.Game.heroes[self.ID].health < self.Game.heroes[self.ID].health_upper:
			numDamagedCharacters += 1
			
		for i in range(numDamagedCharacters):
			self.Game.Hand_Deck.drawCard(self.ID)
		return None
#Creates an ongoing effect(Aura) that affects your minions. Prevents damage when minion at 1 Health already.
#Reduces damage so that it can only reduce the Health to 1
#与Snapjaw Shellfighter的结算顺序: Shellfighter先上场，然后是命令怒吼，1血生物攻击与剧毒随从，Shellfighter先结算，承担伤害，因为剧毒死亡。
#先命令怒吼，然后Shellfighter，1血生物攻击与剧毒随从，仍然是Shellfighter先结算，无关先后顺序
#先执行Shellfighter的预伤害扳机结算，然后随从自己的takesDamage会开始伤害量预判定。
class CommandingShout(Spell):
	Class, name = "Warrior", "Commanding Shout"
	requireTarget, mana = False, 2
	index = "Classic~Warrior~Spell~2~Commanding Shout"
	description = "Your minions can't be reduced below 1 Health this turn. Draw a card"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		PRINT(self.Game, "Commanding Shout will prevent player's minions' health be reduced below 1 this turn. Player draws a card.")
		trigger = Trigger_CommandingShout(self.Game, self.ID)
		trigger.connect()
		self.Game.Hand_Deck.drawCard(self.ID)
		return None
		
class Trigger_CommandingShout(TriggeronBoard):
	def __init__(self, Game, ID):
		self.Game, self.ID = Game, ID
		self.signals = ["MinionAbouttoTakeDamage"]
		self.temp = False
		#number here is a list that holds the damage to be processed
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return target.ID == self.ID and target.onBoard and number[0] > 0
		
	def connect(self):
		for signal in self.signals:
			self.Game.triggersonBoard[self.ID].append((self, signal))
		self.Game.turnEndTrigger.append(self)
		
	def disconnect(self):
		for signal in self.signals:
			extractfrom((self, signal), self.Game.triggersonBoard[self.ID])
		extractfrom(self, self.Game.turnEndTrigger)
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self.entity.Game, "Commandin Shout prevents the minion's health from being reduced to below 1")
		if target.health > 1: number[0] = min(number[0], target.health - 1)
		else: number[0] = 0
		
	def turnEndTrigger(self):
		self.disconnect()
		
		
class CruelTaskmaster(Minion):
	Class, race, name = "Warrior", "", "Cruel Taskmaster"
	mana, attack, health = 2, 2, 2
	index = "Classic~Warrior~Minion~2~2~2~None~Cruel Taskmaster~Battlecry"
	requireTarget, keyWord, description = True, "", "Battlecry: Deal 1 damage to a minion and give it +2 Attack"
	
	def targetExists(self, choice=0):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
		
	#Minion in deck can't get buff/reset.
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			PRINT(self.Game, "Cruel Taskmaster's battlecry deals 1 damage to minion %s and gives it +2 attack."%target.name)
			self.dealsDamage(target, 1)
			target.buffDebuff(2, 0)
		return target
		
		
class Rampage(Spell):
	Class, name = "Warrior", "Rampage"
	requireTarget, mana = True, 2
	index = "Classic~Warrior~Spell~2~Rampage"
	description = "Give a damaged minion +3/+3"
	def targetExists(self, choice=0):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.health < target.health_upper and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			PRINT(self.Game, "Rampage is cast and gives damaged minion %s +3/+3."%target.name)
			target.buffDebuff(3, 3)
		return target
		
#Deals 2 damage to Frothing Berserker, Berserker gains +1 attack then this draws card.
class Slam(Spell):
	Class, name = "Warrior", "Slam"
	requireTarget, mana = True, 2
	index = "Classic~Warrior~Spell~2~Slam"
	description = "Deal 2 damage to a minion. If it survives, draw a card"
	def targetExists(self, choice=0):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			damage = (2 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			PRINT(self.Game, "Slam is cast and deals %d damage to %s"%(damage, target.name))
			self.dealsDamage(target, damage)
			if target.health > 0 and target.dead == False:
				PRINT(self.Game, "The minion survives and Slam lets player draws a card.")
				self.Game.Hand_Deck.drawCard(self.ID)
		return target
		
		
class FrothingBerserker(Minion):
	Class, race, name = "Warrior", "", "Frothing Berserker"
	mana, attack, health = 3, 2, 4
	index = "Classic~Warrior~Minion~3~2~4~None~Frothing Berserker"
	requireTarget, keyWord, description = False, "", "Whenever a minion takes damage, gain +1 Attack"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_FrothingBerserker(self)]
		
class Trigger_FrothingBerserker(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionTakesDamage"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self.entity.Game, "Minion %s takes damage and %s gains +1 Attack."%(target.name, self.entity.name))
		self.entity.buffDebuff(1, 0)
		
		
class ArathiWeaponsmith(Minion):
	Class, race, name = "Warrior", "", "Arathi Weaponsmith"
	mana, attack, health = 4, 3, 3
	index = "Classic~Warrior~Minion~4~3~3~None~Arathi Weaponsmith~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Equip a 2/2 weapon"
	#Triggers regardless of minion's status.
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		PRINT(self.Game, "Arathi Weaponsmith's battlecry lets player equip a 2/2 weapon.")
		self.Game.equipWeapon(BattleAxe(self.Game, self.ID))
		return None
		
class BattleAxe(Weapon):
	Class, name, description = "Warrior", "Battle Axe", ""
	mana, attack, durability = 1, 2, 2
	index = "Classic~Warrior~Weapon~1~2~2~Battle Axe~Uncollectible"
	
	
class MortalStrike(Spell):
	Class, name = "Warrior", "Mortal Strike"
	requireTarget, mana = True, 4
	index = "Classic~Warrior~Spell~4~Mortal Strike"
	description = "Deal 4 damage. If your have 12 or less Health, deal 6 instead"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			if self.Game.heroes[self.ID].health < 13:
				damage = (6 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			else:
				damage = (4 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
				
			PRINT(self.Game, "Mortal Strike is cast and deals %d damage to %s"%(damage, target.name))
			self.dealsDamage(target, damage)
		return target
		
		
class Brawl(Spell):
	Class, name = "Warrior", "Brawl"
	requireTarget, mana = False, 5
	index = "Classic~Warrior~Spell~5~Brawl"
	description = "Destroy all minions except one. (Chosen randomly)"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if curGame.mode == 0:
			PRINT(curGame, "Brawl is cast and only one random minion survives.")
			if curGame.guides:
				i, where = curGame.guides.pop(0)
				if where:
					minions = curGame.minionsonBoard(1) + curGame.minionsonBoard(2)
					survivor = curGame.find(i, where)
				else: return None
			else:
				minions = curGame.minionsonBoard(1) + curGame.minionsonBoard(2)
				if len(minions) > 1:
					survivor = npchoice(minions)
					curGame.fixedGuides.append((survivor.position, "minion%d"%survivor.ID))
				else:
					curGame.fixedGuides.append((0, ""))
					return None
			for minion in minions:
				if minion != survivor: minion.dead = True
		return None
		
		
class Gorehowl(Weapon):
	Class, name, description = "Warrior", "Gorehowl", "Attacking a minion costs 1 Attack instead of 1 Durability"
	mana, attack, durability = 7, 7, 1
	index = "Classic~Warrior~Weapon~7~7~1~Gorehowl"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_Gorehowl(self)]
		self.canLoseDurability = True
		
	def loseDurability(self):
		if self.canLoseDurability:
			PRINT(self.Game, "Weapon %s loses 1 Durability"%self.name)
			self.durability -= 1
		else:
			PRINT(self.Game, "Weapon %s loses 1 Attack instead of Durability"%self.name)
			self.attack -= 1
			self.Game.heroes[self.ID].attack = self.Game.heroes[self.ID].attack_bare + max(0, self.attack)
			self.canLoseDurability = True #把武器的可以失去耐久度恢复为True
			if self.attack < 1:
				self.dead = True
				
class Trigger_Gorehowl(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["HeroAttackingMinion"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return subject == self.entity.Game.heroes[self.entity.ID] and target.type == "Minion" and self.entity.onBoard
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self.entity.Game, "Player's weapon Gorehowl won't lose Durability when attacking minion.")
		self.entity.canLoseDurability = False
		
		
class GrommashHellscream(Minion):
	Class, race, name = "Warrior", "", "Grommash Hellscream"
	mana, attack, health = 8, 4, 9
	index = "Classic~Warrior~Minion~8~4~9~None~Grommash Hellscream~Charge~Legendary"
	requireTarget, keyWord, description = False, "Charge", "Charge. Has +6 attack while damaged"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.auras["Enrage"] = BuffAura_Dealer_Enrage(self, 6)
		self.triggers["StatChanges"] = [self.handleEnrage]
		self.activated = False
		
	def handleEnrage(self):
		self.auras["Enrage"].handleEnrage()
		
		
		
Classic_Indices = {"Classic~Neutral~Minion~0~1~1~None~Wisp": Wisp,
					"Classic~Neutral~Minion~1~1~1~None~Abusive Sergeant~Battlecry": AbusiveSergeant,
					"Classic~Neutral~Minion~1~1~1~None~Argent Squire~Divine Shield": ArgentSquire,
					"Classic~Neutral~Minion~1~1~1~Beast~Angry Chicken": AngryChicken,
					"Classic~Neutral~Minion~1~1~2~Pirate~Bloodsail Corsair~Battlecry": BloodsailCorsair,
					"Classic~Neutral~Minion~1~1~2~Beast~Hungry Crab~Battlecry": HungryCrab,
					"Classic~Neutral~Minion~1~1~1~None~Leper Gnome~Deathrattle": LeperGnome,
					"Classic~Neutral~Minion~1~1~2~None~Lightwarden": Lightwarden,
					"Classic~Neutral~Minion~1~1~2~Murloc~Murloc Tidecaller": MurlocTidecaller,
					"Classic~Neutral~Minion~1~1~2~None~Secretkeeper": Secretkeeper,
					"Classic~Neutral~Minion~1~0~4~None~Shieldbearer~Taunt": Shieldbearer,
					"Classic~Neutral~Minion~1~2~1~Pirate~Southsea Deckhand": SouthseaDeckhand,
					"Classic~Neutral~Minion~1~2~1~None~Worgen Infiltrator~Stealth": WorgenInfiltrator,
					"Classic~Neutral~Minion~1~1~1~Beast~Young Dragonhawk~Windfury": YoungDragonhawk,
					"Classic~Neutral~Minion~1~2~1~None~Young Priestess": YoungPriestess,
					"Classic~Neutral~Minion~2~2~3~None~Amani Berserker": AmaniBerserker,
					"Classic~Neutral~Minion~2~4~5~None~Ancient Watcher": AncientWatcher,
					"Classic~Neutral~Minion~2~1~1~None~Bloodmage Thalnos~Deathrattle~Spell Damage~Legendary": BloodmageThalnos,
					"Classic~Neutral~Minion~2~2~3~Pirate~Bloodsail Raider~Battlecry": BloodsailRaider,
					"Classic~Neutral~Minion~2~2~2~None~Crazed Alchemist~Battlecry": CrazedAlchemist,
					"Classic~Neutral~Minion~2~2~2~Beast~Dire Wolf Alpha": DireWolfAlpha,
					"Classic~Neutral~Minion~2~0~7~None~Doomsayer": Doomsayer,
					"Classic~Neutral~Minion~2~3~2~Dragon~Faerie Dragon": FaerieDragon,
					"Classic~Neutral~Minion~2~2~2~None~Knife Juggler": KnifeJuggler,
					"Classic~Neutral~Minion~2~2~1~None~Loot Hoarder~Deathrattle": LootHoarder,
					"Classic~Neutral~Minion~2~0~4~None~Lorewalker Cho~Legendary": LorewalkerCho,
					"Classic~Neutral~Minion~2~3~2~None~Mad Bomber~Battlecry": MadBomber,
					"Classic~Neutral~Minion~2~1~3~None~Mana Addict": ManaAddict,
					"Classic~Neutral~Minion~2~2~2~None~Mana Wraith": ManaWraith,
					"Classic~Neutral~Minion~2~1~3~None~Master Swordsmith": MasterSwordsmith,
					"Classic~Neutral~Minion~2~4~4~None~Millhouse Manastorm~Battlecry~Legendary": MillhouseManastorm,
					"Classic~Neutral~Minion~2~0~4~None~Nat Pagle~Legendary": NatPagle,
					"Classic~Neutral~Minion~2~2~2~None~Pint-Sized Summoner": PintSizedSummoner,
					"Classic~Neutral~Minion~2~2~3~None~Sunfury Protector~Battlecry": SunfuryProtector,
					"Classic~Neutral~Minion~2~3~2~None~Wild Pyromancer": WildPyromancer,
					"Classic~Neutral~Minion~2~3~2~None~Youthful Brewmaster~Battlecry": YouthfulBrewmaster,
					"Classic~Neutral~Minion~3~0~3~Mech~Alarm-o-Bot": AlarmoBot,
					"Classic~Neutral~Minion~3~4~4~None~Arcane Golem~Battlecry": ArcaneGolem,
					"Classic~Neutral~Minion~3~3~3~None~Blood Knight~Battlecry": BloodKnight,
					"Classic~Neutral~Minion~3~3~2~Dragon~Brightwing~Battlecry~Legendary": Brightwing,
					"Classic~Neutral~Minion~3~2~3~Murloc~Coldlight Seer~Battlecry": ColdlightSeer,
					"Classic~Neutral~Minion~3~1~4~Mech~Demolisher": Demolisher,
					"Classic~Neutral~Minion~3~3~3~None~Earthen Ring Farseer~Battlecry": EarthenRingFarseer,
					"Classic~Neutral~Minion~3~2~3~Beast~Emperor Cobra~Poisonous": EmperorCobra,
					"Classic~Neutral~Minion~3~2~3~None~Flesheating Ghoul": FlesheatingGhoul,
					"Classic~Neutral~Minion~3~2~3~Mech~Harvest Golem~Deathrattle": HarvestGolem,
					"Classic~Neutral~Minion~1~2~1~Mech~Damaged Golem~Uncollectible": DamagedGolem,
					"Classic~Neutral~Minion~3~1~5~None~Imp Master": ImpMaster,
					"Classic~Neutral~Minion~1~1~1~Demon~Imp~Uncollectible": Imp,
					"Classic~Neutral~Minion~3~4~7~None~Injured Blademaster~Battlecry": InjuredBlademaster,
					"Classic~Neutral~Minion~3~2~1~Beast~Ironbeak Owl~Battlecry": IronbeakOwl,
					"Classic~Neutral~Minion~3~4~2~Beast~Jungle Panther~Stealth": JunglePanther,
					"Classic~Neutral~Minion~3~5~5~Beast~King Mukla~Battlecry~Legendary": KingMukla,
					"Classic~Neutral~Spell~1~Bananas~Uncollectible": Bananas,
					"Classic~Neutral~Minion~3~3~3~Murloc~Murloc Warleader": MurlocWarleader,
					"Classic~Neutral~Minion~3~2~2~None~Questing Adventurer": QuestingAdventurer,
					"Classic~Neutral~Minion~3~3~3~None~Raging Worgen": RagingWorgen,
					"Classic~Neutral~Minion~3~3~1~None~Scarlet Crusader~Divine Shield": ScarletCrusader,
					"Classic~Neutral~Minion~3~3~3~Pirate~Southsea Captain": SouthseaCaptain,
					"Classic~Neutral~Minion~3~2~3~None~Tauren Warrior~Taunt": TaurenWarrior,
					"Classic~Neutral~Minion~3~2~3~None~Thrallmar Farseer~Windfury": ThrallmarFarseer,
					"Classic~Neutral~Minion~3~3~3~None~Tinkmaster Overspark~Battlecry~Legendary": TinkmasterOverspark,
					"Classic~Neutral~Minion~5~5~5~Beast~Devilsaur~Uncollectible": Devilsaur,
					"Classic~Neutral~Minion~1~1~1~Beast~Squirrel~Uncollectible": Squirrel,
					"Classic~Neutral~Minion~4~5~4~None~Ancient Brewmaster~Battlecry": AncientBrewmaster,
					"Classic~Neutral~Minion~4~2~5~None~Ancient Mage~Battlecry": AncientMage,
					"Classic~Neutral~Minion~4~4~2~None~Cult Master": CultMaster,
					"Classic~Neutral~Minion~4~4~4~None~Dark Iron Dwarf~Battlecry": DarkIronDwarf,
					"Classic~Neutral~Minion~4~2~3~None~Defender of Argus~Battlecry": DefenderofArgus,
					"Classic~Neutral~Minion~4~3~3~Pirate~Dread Corsair~Taunt": DreadCorsair,
					"Classic~Neutral~Minion~4~1~7~None~Mogu'shan Warden~Taunt": MogushanWarden,
					"Classic~Neutral~Minion~4~3~3~None~Silvermoon Guardian~Divine Shield": SilvermoonGuardian,
					"Classic~Neutral~Minion~4~5~4~None~SI:7 Infiltrator~Battlecry": SI7Infiltrator,
					"Classic~Neutral~Minion~4~4~1~Dragon~Twilight Drake~Battlecry": TwilightDrake,
					"Classic~Neutral~Minion~4~3~5~None~Violet Teacher": VioletTeacher,
					"Classic~Neutral~Minion~1~1~1~None~Violet Apprentice~Uncollectible": VioletApprentice,
					"Classic~Neutral~Minion~5~4~4~None~Abomination~Taunt~Deathrattle": Abomination,
					"Classic~Neutral~Minion~5~4~2~None~Big Game Hunter~Battlecry": BigGameHunter,
					"Classic~Neutral~Minion~5~5~4~Pirate~Captain Greenskin~Battlecry~Legendary": CaptainGreenskin,
					"Classic~Neutral~Minion~5~3~3~None~Faceless Manipulator~Battlecry": FacelessManipulator,
					"Classic~Neutral~Minion~5~3~6~None~Fen Creeper~Taunt": FenCreeper,
					"Classic~Neutral~Minion~5~5~4~None~Harrison Jones~Battlecry~Legendary": HarrisonJones,
					"Classic~Neutral~Minion~5~4~4~None~Silver Hand Knight~Battlecry": SilverHandKnight,
					"Classic~Neutral~Minion~2~2~2~None~Squire~Uncollectible": Squire,
					"Classic~Neutral~Minion~5~4~6~None~Spiteful Smith": SpitefulSmith,
					"Classic~Neutral~Minion~5~3~5~Beast~Stampeding Kodo~Battlecry": StampedingKodo,
					"Classic~Neutral~Minion~5~5~5~Beast~Stranglethorn Tiger~Stealth": StranglethornTiger,
					"Classic~Neutral~Minion~5~7~6~None~Venture Co. Mercenary": VentureCoMercenary,
					"Classic~Neutral~Minion~6~4~2~None~Argent Commander~Divine Shield~Charge": ArgentCommander,
					"Classic~Neutral~Minion~6~4~5~None~Cairne Bloodhoof~Deathrattle~Legendary": CairneBloodhoof,
					"Classic~Neutral~Minion~6~4~5~None~Baine Bloodhoof~Uncollectible~Legendary": BaineBloodhoof,
					"Classic~Neutral~Minion~6~5~5~Elemental~Frost Elemental~Battlecry": FrostElemental,
					"Classic~Neutral~Minion~6~4~4~None~Gadgetzan Auctioneer": GadgetzanAuctioneer,
					"Classic~Neutral~Minion~6~4~4~None~Hogger~Legendary": Hogger,
					"Classic~Neutral~Minion~2~2~2~None~Gnoll~Taunt~Uncollectible": Gnoll,
					"Classic~Neutral~Minion~6~7~5~Demon~Illidan Stormrage~Legendary": Xavius,
					"Classic~Neutral~Minion~1~2~1~Elemental~Xavian Satyr~Uncollectible": XavianSatyr,
					"Classic~Neutral~Minion~6~5~4~None~Priestess of Elune~Battlecry": PriestessofElune,
					"Classic~Neutral~Minion~6~4~5~None~Sunwalker~Divine Shield~Taunt": Sunwalker,
					"Classic~Neutral~Minion~6~9~7~Beast~The Beast~Deathrattle~Legendary": TheBeast,
					"Classic~Neutral~Minion~3~3~3~None~Finkle Einhorn~Uncollectible~Legendary": FinkleEinhorn,
					"Classic~Neutral~Minion~6~4~5~None~The Black Knight~Battlecry~Legendary": TheBlackKnight,
					"Classic~Neutral~Minion~6~4~5~None~Windfury Harpy~Windfury": WindfuryHarpy,
					"Classic~Neutral~Minion~7~4~4~None~Barrens Stablehand~Battlecry": BarrensStablehand,
					"Classic~Neutral~Minion~7~7~5~Elemental~Baron Geddon~Legendary": BaronGeddon,
					"Classic~Neutral~Minion~7~6~8~None~High Inquisitor Whitemane~Battlecry~Legendary": HighInquisitorWhitemane,
					"Classic~Neutral~Minion~7~7~5~None~Ravenholdt Assassin~Stealth": RavenholdtAssassin,
					"Classic~Neutral~Minion~8~5~5~Elemental~Arcane Devourer": ArcaneDevourer,
					"Classic~Neutral~Minion~8~7~7~None~Gruul~Legendary": Gruul,
					"Classic~Neutral~Minion~9~8~8~Dragon~Alexstrasza~Battlecry~Legendary": Alexstrasza,
					"Classic~Neutral~Minion~9~4~12~Dragon~Malygos~Spell Damage~Legendary": Malygos,
					"Classic~Neutral~Minion~9~8~8~Dragon~Nozdormu~Legendary": Nozdormu,
					"Classic~Neutral~Minion~9~8~8~Dragon~Onyxia~Battlecry~Legendary": Onyxia,
					"Classic~Neutral~Minion~1~1~1~Dragon~Whelp~Uncollectible": Whelp,
					"Classic~Neutral~Minion~9~4~12~Dragon~Ysera~Legendary": Ysera,
					"Classic~DreamCard~Spell~0~Dream~Uncollectible": Dream,
					"Classic~DreamCard~Spell~0~Nightmare~Uncollectible": Nightmare,
					"Classic~DreamCard~Spell~2~Ysera Awakens~Uncollectible": YseraAwakens,
					"Classic~DreamCard~Minion~3~3~5~None~Laughing Sister~Uncollectible": LaughingSister,
					"Classic~DreamCard~Minion~4~7~6~Dragon~Emerald Drake~Uncollectible": EmeraldDrake,
					"Classic~Neutral~Minion~10~12~12~Dragon~Deathwing~Battlecry~Legendary": Deathwing,
					"Classic~Neutral~Minion~10~8~8~None~Sea Giant": SeaGiant,
					"Classic~Druid~Spell~1~Savagery": Savagery,
					"Classic~Druid~Spell~2~Power of the Wild~Choose One": PoweroftheWild,
					"Classic~Druid~Spell~2~Leader of the Pack~Uncollectible": LeaderofthePack,
					"Classic~Druid~Spell~2~Summon a Panther~Uncollectible": SummonaPanther,
					"Classic~Druid~Minion~2~3~2~Beast~Panther~Uncollectible": Panther,
					"Classic~Druid~Spell~2~Wrath~Choose One": Wrath,
					"Classic~Druid~Spell~2~Solar Wrath~Uncollectible": SolarWrath,
					"Classic~Druid~Spell~2~Nature's Wrath~Uncollectible": NaturesWrath,
					"Classic~Druid~Spell~3~Mark of Nature~Choose One": MarkofNature,
					"Classic~Druid~Spell~3~Tiger's Fury~Uncollectible": TigersFury,
					"Classic~Druid~Spell~3~Thick Hide~Uncollectible": ThickHide,
					"Classic~Druid~Spell~4~Bite": Bite,
					"Classic~Druid~Minion~4~2~2~None~Keeper of the Grove~Choose One": KeeperoftheGrove,
					"Classic~Druid~Spell~4~Soul of the Forest": SouloftheForest,
					"Classic~Druid~Minion~5~4~4~None~Druid of the Claw~Choose One": DruidoftheClaw,
					"Classic~Druid~Minion~5~4~4~Beast~Druid of the Claw~Charge~Uncollectible": DruidoftheClaw_Charge,
					"Classic~Druid~Minion~5~4~6~Beast~Druid of the Claw~Taunt~Uncollectible ": DruidoftheClaw_Taunt,
					"Classic~Druid~Minion~5~4~6~Beast~Druid of the Claw~Taunt~Charge~Uncollectible ": DruidoftheClaw_Both,
					"Classic~Druid~Spell~5~Force of Nature": ForceofNature,
					"Classic~Druid~Minion~2~2~2~None~Treant Classic~Uncollectible": Treant_Classic,
					"Classic~Druid~Spell~5~Starfall~Choose One": Starfall,
					"Classic~Druid~Spell~5~Starlord~Uncollectible": Starlord,
					"Classic~Druid~Spell~5~Stellar Drift~Uncollectible": StellarDrift,
					"Classic~Druid~Spell~6~Nourish~Choose One": Nourish,
					"Classic~Druid~Spell~6~Rampant Growth~Uncollectible": RampantGrowth,
					"Classic~Druid~Spell~6~Enrich~Uncollectible": Enrich,
					"Classic~Druid~Minion~7~5~5~None~Ancient of Lore~Choose One": AncientofLore,
					"Classic~Druid~Minion~7~5~5~None~Ancient of War~Choose One": AncientofWar,
					"Classic~Druid~Spell~8~Gift of the Wild": GiftoftheWild,
					"Classic~Druid~Minion~9~5~8~None~Cenarius~Choose One~Legendary": Cenarius,
					"Classic~Druid~Minion~2~2~2~None~Treant~Taunt~Uncollectible": Treant_Classic_Taunt,
					"Classic~Hunter~Spell~1~Bestial Wrath": BestialWrath,
					"Classic~Hunter~Spell~2~Explosive Trap~~Secret": ExplosiveTrap,
					"Classic~Hunter~Spell~2~Freezing Trap~~Secret": FreezingTrap,
					"Classic~Hunter~Spell~2~Misdirection~~Secret": Misdirection,
					"Classic~Hunter~Spell~2~Snake Trap~~Secret": SnakeTrap,
					"Classic~Hunter~Minion~1~1~1~Beast~Snake~Uncollectible": Snake,
					"Classic~Hunter~Spell~2~Snipe~~Secret": Snipe,
					"Classic~Hunter~Spell~2~Flare": Flare,
					"Classic~Hunter~Minion~2~2~2~Beast~Scavenging Hyena": ScavengingHyena,
					"Classic~Hunter~Spell~3~Deadly Shot": DeadlyShot,
					"Classic~Hunter~Weapon~3~3~2~Eaglehorn Bow": EaglehornBow,
					"Classic~Hunter~Spell~3~Unleash the Hounds": UnleashtheHounds,
					"Classic~Hunter~Minion~1~1~1~Beast~Hound~Charge~Uncollectible": Hound,
					"Classic~Hunter~Spell~5~Explosive Shot": ExplosiveShot,
					"Classic~Hunter~Minion~6~6~5~Beast~Savannah Highmane~Deathrattle": SavannahHighmane,
					"Classic~Hunter~Minion~2~2~2~Beast~Hyena~Uncollectible": Hyena_Classic,
					"Classic~Hunter~Weapon~7~5~2~Gladiator's Longbow": GladiatorsLongbow,
					"Classic~Hunter~Minion~9~8~8~Beast~King Krush~Charge~Legendary": KingKrush,
					"Classic~Mage~Spell~1~Tome of Intellect": TomeofIntellect,
					"Classic~Mage~Spell~2~Icicle": Icicle,
					"Classic~Mage~Minion~2~1~3~None~Mana Wyrm": ManaWyrm,
					"Classic~Mage~Minion~2~3~2~None~Sorcerer's Apprentice": SorcerersApprentice,
					"Classic~Mage~Spell~3~Counterspell~~Secret": Counterspell,
					"Classic~Mage~Spell~3~Ice Barrier~~Secret": IceBarrier,
					"Classic~Mage~Spell~3~Mirror Entity~~Secret": MirrorEntity,
					"Classic~Mage~Spell~3~Spellbender~~Secret": Spellbender,
					"Classic~Mage~Minion~1~1~3~None~Spellbender~Uncollectible": Spellbender_Minion,
					"Classic~Mage~Spell~3~Vaporize~~Secret": Vaporize,
					"Classic~Mage~Minion~3~4~3~None~Kirin Tor Mage~Battlecry": KirinTorMage,
					"Classic~Mage~Spell~4~Cone of Cold": ConeofCold,
					"Classic~Mage~Minion~4~3~3~None~Ethereal Arcanist": EtherealArcanist,
					"Classic~Mage~Spell~6~Blizzard": Blizzard,
					"Classic~Mage~Minion~7~5~7~None~Archmage Antonidas~Legendary": ArchmageAntonidas,
					"Classic~Mage~Spell~10~Pyroblast": Pyroblast,
					
					"Classic~Paladin~Spell~1~Blessing of Wisdom": BlessingofWisdom,
					"Classic~Paladin~Spell~1~Eye for an Eye~~Secret": EyeforanEye,
					"Classic~Paladin~Spell~1~Noble Sacrifice~~Secret": NobleSacrifice,
					"Classic~Paladin~Minion~1~2~1~None~Defender~Uncollectible": Defender,
					"Classic~Paladin~Spell~1~Redemption~~Secret": Redemption,
					"Classic~Paladin~Spell~1~Repentance~~Secret": Repentance,
					"Classic~Paladin~Minion~2~2~2~None~Argent Protector~Battlecry": ArgentProtector,
					"Classic~Paladin~Spell~4~Equality": Equality,
					"Classic~Paladin~Minion~3~3~3~None~Ardor Peacekeeper~Battlecry": AldorPeacekeeper,
					"Classic~Paladin~Weapon~3~1~5~Sword of Justice": SwordofJustice,
					"Classic~Paladin~Spell~5~Blessed Champion": BlessedChampion,
					"Classic~Paladin~Spell~5~Holy Wrath": HolyWrath,
					"Classic~Paladin~Spell~5~Righteousness": Righteousness,
					"Classic~Paladin~Spell~6~Avenging Wrath": AvengingWrath,
					"Classic~Paladin~Spell~8~Lay on Hands": LayonHands,
					"Classic~Paladin~Minion~8~6~6~None~Tirion Fordring~Taunt~Divine Shield~Deathrattle~Legendary": TirionFordring,
					"Classic~Paladin~Weapon~5~5~3~Ashbringer~Uncollectible~Legendary": Ashbringer,
					"Classic~Priest~Spell~0~Circle of Healing": CircleofHealing,
					"Classic~Priest~Spell~0~Silence": Silence,
					"Classic~Priest~Spell~1~Inner Fire": InnerFire,
					"Classic~Priest~Minion~1~2~1~None~Scarlet Subjugator~Battlecry": ScarletSubjugator,
					"Classic~Priest~Minion~2~2~3~None~Kul Tiran Chaplain~Battlecry": KulTiranChaplain,
					"Classic~Priest~Minion~2~0~5~None~Lightwell": Lightwell,
					"Classic~Priest~Spell~2~Thoughtsteal": Thoughtsteal,
					"Classic~Priest~Spell~3~Shadow Madness": ShadowMadness,
					"Classic~Priest~Minion~4~0~5~None~Lightspawn": Lightspawn,
					"Classic~Priest~Spell~4~Mass Dispel": MassDispel,
					"Classic~Priest~Spell~4~Mindgames": Mindgames,
					"Classic~Priest~Spell~4~Shadow Word: Ruin": ShadowWordRuin,
					"Classic~Priest~Minion~1~0~1~None~Shadow of Nothing~Uncollectible": ShadowofNothing,
					"Classic~Priest~Minion~6~4~5~None~Cabal Shadow Priest~Battlecry": CabalShadowPriest,
					"Classic~Priest~Minion~5~5~6~None~Temple Enforcer~Battlecry": TempleEnforcer,
					"Classic~Priest~Minion~8~8~1~None~Natalie Seline~Battlecry": NatalieSeline,
					"Classic~Rogue~Spell~0~Preparation": Preparation,
					"Classic~Rogue~Spell~0~Shadowstep": Shadowstep,
					"Classic~Rogue~Spell~1~Pilfer": Pilfer,
					"Classic~Rogue~Spell~2~Betrayal": Betrayal,
					"Classic~Rogue~Spell~2~Cold Blood~Combo": ColdBlood,
					"Classic~Rogue~Minion~2~2~2~None~Defias Ringleader~Combo": DefiasRingleader,
					"Classic~Rogue~Minion~1~2~1~None~Defias Bandit~Uncollectible": DefiasBandit,
					"Classic~Rogue~Spell~2~Eviscerate~Combo": Eviscerate,
					"Classic~Rogue~Minion~2~1~1~None~Patient Assassin~Poisonous~Stealth": PatientAssassin,
					"Classic~Rogue~Minion~3~2~2~None~Edwin VanCleef~Combo~Legendary": EdwinVanCleef,
					"Classic~Rogue~Spell~3~Headcrack~Combo": Headcrack,
					"Classic~Rogue~Weapon~3~2~2~Perdition's Blade~Combo~Battlecry": PerditionsBlade,
					"Classic~Rogue~Minion~3~3~3~None~SI:7 Agent~Combo": SI7Agent,
					"Classic~Rogue~Spell~4~Blade Flurry": BladeFlurry,
					"Classic~Rogue~Minion~4~4~4~None~Master of Disguise~Battlecry": MasterofDisguise,
					"Classic~Rogue~Minion~6~5~3~None~Kidnapper~Combo": Kidnapper,
					"Classic~Shaman~Minion~1~3~1~Elemental~Dust Devil~Overload~Windfury": DustDevil,
					"Classic~Shaman~Spell~1~Earth Shock": EarthShock,
					"Classic~Shaman~Spell~1~Forked Lightning~Overload": ForkedLightning,
					"Classic~Shaman~Spell~1~Lightning Bolt~Overload": LightningBolt,
					"Classic~Shaman~Spell~2~Ancestral Spirit": AncestralSpirit,
					"Classic~Shaman~Weapon~2~2~3~Stormforged Axe~Overload": StormforgedAxe,
					"Classic~Shaman~Spell~3~Far Sight": FarSight,
					"Classic~Shaman~Spell~3~Feral Spirit~Overload": FeralSpirit,
					"Classic~Shaman~Minion~2~2~3~None~Spirit Wolf~Taunt~Uncollectible": SpiritWolf,
					"Classic~Shaman~Spell~3~Lava Burst~Overload": LavaBurst,
					"Classic~Shaman~Spell~3~Lightning Storm~Overload": LightningStorm,
					"Classic~Shaman~Minion~3~0~3~Totem~Mana Tide Totem": ManaTideTotem,
					"Classic~Shaman~Minion~3~2~4~Elemental~Unbound Elemental": UnboundElemental,
					"Classic~Shaman~Weapon~5~2~8~Doomhammer~Windfury~Overload": Doomhammer,
					"Classic~Shaman~Minion~5~7~8~Elemental~Earth Elemental~Taunt~Overload": EarthElemental,
					"Classic~Shaman~Minion~8~3~5~Elemental~Al'Akir the Windlord~Taunt~Charge~Windfury~Divine Shield~Legendary": AlAkirtheWindlord,
					"Classic~Warlock~Minion~1~0~1~Demon~Blood Imp~Stealth": BloodImp,
					"Classic~Warlock~Spell~1~Call of the Void": CalloftheVoid,
					"Classic~Warlock~Minion~1~3~2~Demon~Flame Imp~Battlecry": FlameImp,
					"Classic~Warlock~Spell~2~Demonfire": Demonfire,
					"Classic~Warlock~Spell~3~Sense Demons": SenseDemons,
					"Classic~Warlock~Minion~1~1~1~Demon~Worthless Imp~Uncollectible": WorthlessImp,
					"Classic~Warlock~Minion~4~0~4~None~Summoning Portal": SummoningPortal,
					"Classic~Warlock~Minion~3~3~5~Demon~Felguard~Taunt~Battlecry": Felguard,
					"Classic~Warlock~Minion~3~3~3~Demon~Void Terror~Battlecry": VoidTerror,
					"Classic~Warlock~Minion~4~5~6~Demon~Pit Lord~Battlecry": PitLord,
					"Classic~Warlock~Spell~4~Shadowflame": Shadowflame,
					"Classic~Warlock~Spell~5~Bane of Doom": BaneofDoom,
					"Classic~Warlock~Spell~6~Siphon Soul": SiphonSoul,
					"Classic~Warlock~Minion~7~5~8~Demon~Siegebreaker~Taunt": Siegebreaker,
					"Classic~Warlock~Spell~8~Twisting Nether": TwistingNether,
					"Classic~Warlock~Minion~9~3~15~Demon~Lord Jaraxxus~Battlecry~Legendary": LordJaraxxus,
					"Classic~Warlock~Minion~6~6~6~Demon~Infernal~Uncollectible": Infernal,
					"Classic~Warlock~Weapon~3~3~8~Blood Fury~Uncollectible": BloodFury,
					"Classic~Warrior~Spell~0~Inner Rage": InnerRage,
					"Classic~Warrior~Spell~1~Shield Slam": ShieldSlam,
					"Classic~Warrior~Spell~1~Upgrade!": Upgrade,
					"Classic~Warrior~Weapon~1~1~3~Heavy Axe~Uncollectible": HeavyAxe,
					"Classic~Warrior~Minion~2~1~4~None~Armorsmith": Armorsmith,
					"Classic~Warrior~Spell~2~Battle Rage": BattleRage,
					"Classic~Warrior~Spell~2~Commanding Shout": CommandingShout,
					"Classic~Warrior~Minion~2~2~2~None~Cruel Taskmaster~Battlecry": CruelTaskmaster,
					"Classic~Warrior~Spell~2~Rampage": Rampage,
					"Classic~Warrior~Spell~2~Slam": Slam,
					"Classic~Warrior~Minion~3~2~4~None~Frothing Berserker": FrothingBerserker,
					"Classic~Warrior~Minion~4~3~3~None~Arathi Weaponsmith~Battlecry": ArathiWeaponsmith,
					"Classic~Warrior~Weapon~1~2~2~Battle Axe~Uncollectible": BattleAxe,
					"Classic~Warrior~Spell~4~Mortal Strike": MortalStrike,
					"Classic~Warrior~Spell~5~Brawl": Brawl,
					"Classic~Warrior~Weapon~7~7~1~Gorehowl": Gorehowl,
					"Classic~Warrior~Minion~8~4~9~None~Grommash Hellscream~Charge~Legendary": GrommashHellscream
					}