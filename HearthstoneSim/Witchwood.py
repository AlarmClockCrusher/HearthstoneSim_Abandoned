from CardTypes import *
import CardIndices
from Triggers_Auras import *
from VariousHandlers import *

import numpy as np

def extractfrom(target, listObject):
	temp = None
	for i in range(len(listObject)):
		if listObject[i] == target:
			temp = listObject.pop(i)
	return temp
	
def fixedList(listObject):
	return listObject[0:len(listObject)]
	
	
class Trigger_Echo(TriggerinHand):
	def __init__(self, entity):
		self.blank_init(entity, ["TurnEnds"])
		self.temp = True
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.inHand #Echo disappearing should trigger at the end of any turn
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("At the start of turn, Echo card %s disappears."%self.entity.name)
		self.entity.Game.Hand_Deck.extractfromHand(self.entity)
		
"""mana 1 cards"""
class SwampDragonEgg(Minion):
	Class, race, name = "Neutral", "", "Swamp Dragon Egg"
	mana, attack, health = 1, 0, 3
	index = "Witchwood-Neutral-1-0-3-Minion-None-Swamp Dragon Egg-Deathrattle"
	needTarget, keyWord, description = False, "", "Deathrattle: Add a random Dragon to your hand"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [AddaDragontoHand(self)]
		
class AddaDragontoHand(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		dragons = list(self.Game.MinionswithRace["Dragon"].values())
		print("Deathrattle: Add a random Dragon to your hand triggers.")
		self.entity.Game.Hand_Deck.addCardtoHand(np.random.choice(dragons), self.entity.ID, "CreateUsingType")
		
		
class SwampLeech(Minion):
	Class, race, name = "Neutral", "Beast", "Swamp Leech"
	mana, attack, health = 1, 2, 1
	index = "Witchwood-Neutral-1-2-1-Minion-Beast-Swamp Leech-Lifesteal"
	needTarget, keyWord, description = False, "Lifesteal", "Lifesteal"
	
"""Mana 2 cards"""
class BalefulBanker(Minion):
	Class, race, name = "Neutral", "", "Baleful Banker"
	mana, attack, health = 2, 2, 2
	index = "Witchwood-Neutral-2-2-2-Minion-None-Baleful Banker-Battlecry"
	needTarget, keyWord, description = True, "", "Battlecry: Choose a friendly minion. Shuffle a copy of it into your deck"
	
	def targetExists(self, choice=0):
		return self.selectableFriendlyMinionExists(choice)
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.ID == self.ID
		
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			card = type(target)(self.Game, ID)
			self.Game.Hand_Deck.shuffleCardintoDeck(card, self.ID)
			
		return self, target
		
class LostSpirit(Minion):
	Class, race, name = "Neutral", "", "Lost Spirit"
	mana, attack, health = 2, 1, 1
	index = "Witchwood-Neutral-2-1-1-Minion-None-Lost Spirit-Deathrattle"
	needTarget, keyWord, description = False, "", "Deathrattle: Give your minions +2 Attack"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [GiveYourMinionsPlus2Attack(self)]
		
class GiveYourMinionsPlus2Attack(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("Deathrattle: Give your minions +2 Attack triggers.")
		for minion in self.entity.Game.minionsonBoard(self.entity.ID):
			minion.buffDebuff(2, 0)
			
			
class ViciousScalehide(Minion):
	Class, race, name = "Neutral", "Beast", "Vicious Scalehide"
	mana, attack, health = 2, 1, 3
	index = "Witchwood-Neutral-2-1-3-Minion-Beast-Vicious Scalehide-Lifesteal-Rush"
	needTarget, keyWord, description = False, "Rush,Lifesteal", "Rush, Lifesteal"
	
	
class SpellShifter_Human(Minion):
	Class, race, name = "Neutral", "", "Spell Shifter"
	mana, attack, health = 2, 1, 4
	index = "Witchwood-Neutral-2-1-4-Minion-None-Spell Shifter Human-Spell Damage-Shifting"
	needTarget, keyWord, description = False, "Spell Damage", "Spell Damage +1. Each turn this is in your hand, swap its Attack and Health"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersinHand = [Trigger_SpellShifter_Human(self)]
		
#假设狼人的手牌变形始终是手牌扳机
class Trigger_SpellShifter_Human(TriggerinHand):
	def __init__(self, entity):
		self.blank_init(entity, ["TurnEnds"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.inHand and ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("At the end of turn, Spellshifter transforms for into a worgen")
		worgen = SpellShifter_Worgen(self.entity.Game, self.entity.ID)
		worgen.statReset(self.entity.health_Enchant, self.entity.attack_Enchant)
		worgen.identity = self.entity.identity
		#狼人形态会复制人形态的场上扳机，但是目前没有给随从外加手牌和牌库扳机的机制。
		#目前不考虑狼人牌在变形前保有的临时攻击力buff
		worgen.triggersonBoard[0] = self.entity.triggersonBoard[1]
		self.entity.Game.Hand_Deck.replaceCardinHand(self.entity, worgen)
		
class SpellShifter_Worgen(Minion):
	Class, race, name = "Neutral", "", "Spell Shifter"
	mana, attack, health = 2, 4, 1
	index = "Witchwood-Neutral-2-4-1-Minion-None-Spell Shifter Worgen-Spell Damage-Uncollectible-Shifting"
	needTarget, keyWord, description = False, "Spell Damage", "Spell Damage +1. Each turn this is in your hand, swap its Attack and Health"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersinHand = [Trigger_SpellShifter_Worgen(self)]
		
class Trigger_SpellShifter_Worgen(TriggerinHand):
	def __init__(self, entity):
		self.blank_init(entity, ["TurnEnds"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.inHand and ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("At the end of turn, Spellshifter transforms into a human")
		human = SpellShifter_Human(self.entity.Game, self.entity.ID)
		human.statReset(self.entity.health_Enchant, self.entity.attack_Enchant)
		human.identity = self.entity.identity
		human.triggersonBoard[0] = self.entity.triggersonBoard[1]
		self.entity.Game.Hand_Deck.replaceCardinHand(self.entity, worgen)
		
"""Mana 3 cards"""
class BlackwaldPixie(Minion):
	Class, race, name = "Neutral", "", "Blackwald Pixie"
	mana, attack, health = 3, 3, 4
	index = "Witchwood-Neutral-3-3-4-Minion-None-Blackwald Pixie-Battlecry"
	needTarget, keyWord, description = False, "", "Battlecry: Refresh your Hero Power"
	
	def whenEffective(self, target=None, comment="", choice=0):
		print("Blackwald Pixie's battlecry is played and refreshes players Hero Power")
		if self.Game.heroPowers[self.ID].heroPowerTimes >= self.Game.heroPowers[self.ID].heroPowerChances_base + self.Game.heroPowers[self.ID].heroPowerChances_extra:
			self.Game.heroPowers[self.ID].heroPowerChances_extra += 1
		return self, None
		
class HenchClanThug(Minion):
	Class, race, name = "Neutral", "", "Hench-Clan Thug"
	mana, attack, health = 3, 3, 3
	index = "Witchwood-Neutral-3-3-3-Minion-None-Hench-Clan Thug"
	needTarget, keyWord, description = False, "", "After your hero attacks, give this minion +1/+1"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_HenchClanThug(self)]
		
class Trigger_HenchClanThug(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["HeroAttackedMinion", "HeroAttackedHero"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject.cardType == self.entity.Game.heroes[self.entity.ID]
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("After friendly hero attacks, %s gains +1/+1."%self.entity.name)
		self.entity.buffDebuff(1, 1)
		
		
class MarshDrake(Minion):
	Class, race, name = "Neutral", "Dragon", "Marsh Drake"
	mana, attack, health = 3, 5, 4
	index = "Witchwood-Neutral-3-5-4-Minion-Dragon-Marsh Drake-Battlecry"
	needTarget, keyWord, description = False, "", "Battlecry: Summon a 2/1 Poisonous Drakeslayer for your opponent"
	
	def whenEffective(self, target=None, comment="", choice=0):
		print("Marsh Drake's battlecry twice and summons two 2/1 Poisonous Drakeslayers for the opponent.")
		self.Game.summonMinion(Drakeslayer(self.Game, 3-self.ID), -1, self.ID)
		return self, None
		
class Drakeslayer(Minion):
	Class, race, name = "Neutral", "", "Drakeslayer"
	mana, attack, health = 1, 2, 1
	index = "Witchwood-Neutral-1-2-1-Minion-None-Drakeslayer-Poisonous-Uncollectible"
	needTarget, keyWord, description = False, "Poisonous", "Poisonous"
	
	
class NightmareAmalgam(Minion):
	Class, race, name = "Neutral", "Beast, Murloc, Pirate, Mech, Totem, Demon, Elemental, Dragon", "Nightmare Amalgam"
	mana, attack, health = 3, 3, 4
	index = "Witchwood-Neutral-3-3-4-Minion-Beast-Murloc-Pirate-Mech-Totem-Demon-Elemental-Dragon-Nightmare Amalgam"
	needTarget, keyWord, description = False, "", "This is an Elemental, Mech, Demon, Murloc, Dragon, Beast, Pirate and Totem"
	
	
class PhantomMilitia(Minion):
	Class, race, name = "Neutral", "", "Phantom Militia"
	mana, attack, health = 3, 2, 4
	index = "Witchwood-Neutral-3-2-4-Minion-None-Phantom Militia-Taunt-Echo"
	needTarget, keyWord, description = False, "Echo,Taunt", "Echo, Taunt"
	
	
class PumpkinPeasant_Human(Minion):
	Class, race, name = "Neutral", "", "Pumpkin Peasant"
	mana, attack, health = 3, 2, 4
	index = "Witchwood-Neutral-3-2-4-Minion-None-Pumpkin Peasant Human-Lifesteal-Shifting"
	needTarget, keyWord, description = False, "Lifesteal", "Lifesteal. Each turn this is in your hand, swap its Attack and Health"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersinHand = [Trigger_PumpkinPeasant_Human(self)]
		
#假设狼人的手牌变形始终是手牌扳机
class Trigger_PumpkinPeasant_Human(TriggerinHand):
	def __init__(self, entity):
		self.blank_init(entity, ["TurnEnds"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.inHand and ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("At the start of turn, Pumpkin Peasant transforms into a worgen")
		worgen = PumpkinPeasant_Worgen(self.entity.Game, self.entity.ID)
		worgen.statReset(self.entity.health_Enchant, self.entity.attack_Enchant)
		worgen.identity = self.entity.identity
		#狼人形态会复制人形态的场上扳机，但是目前没有给随从外加手牌和牌库扳机的机制。
		worgen.triggersonBoard[0] = self.entity.triggersonBoard[1]
		self.entity.Game.Hand_Deck.replaceCardinHand(self.entity, worgen)
		
class PumpkinPeasant_Worgen(Minion):
	Class, race, name = "Neutral", "", "Pumpkin Peasant"
	mana, attack, health = 3, 4, 2
	index = "Witchwood-Neutral-3-4-2-Minion-None-Pumpkin Peasant Worgen-Lifesteal-Uncollectible-Shifting"
	needTarget, keyWord, description = False, "Lifesteal", "Lifesteal. Each turn this is in your hand, swap its Attack and Health"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersinHand = [Trigger_PumpkinPeasant_Worgen(self)]
		
class Trigger_PumpkinPeasant_Worgen(TriggerinHand):
	def __init__(self, entity):
		self.blank_init(entity, ["TurnEnds"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.inHand and ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("At the start of turn, Pumpkin Peasant transforms for into a human")
		human = PumpkinPeasant_Human(self.entity.Game, self.entity.ID)
		human.statReset(self.entity.health_Enchant, self.entity.attack_Enchant)
		human.identity = self.entity.identity
		human.triggersonBoard[0] = self.entity.triggersonBoard[1]
		self.entity.Game.Hand_Deck.replaceCardinHand(self.entity, worgen)
		
		
class TanglefurMystic(Minion):
	Class, race, name = "Neutral", "", "Tanglefur Mystic"
	mana, attack, health = 3, 3, 4
	index = "Witchwood-Neutral-3-3-4-Minion-None-Tanglefur Mystic-Battlecry"
	needTarget, keyWord, description = False, "", "Battlecry: Add a random 2-Cost minion to each player's hand"
	
	def whenEffective(self, target=None, comment="", choice=0):
		minions = np.random.choice(list(self.Game.MinionswithCertainCost[2].values()), 2, replace=True)
		self.Game.Hand_Deck.addCardtoHand(minions[0], self.ID, "CreateUsingType")
		self.Game.Hand_Deck.addCardtoHand(minions[1], 3-self.ID, "CreateUsingType")
		return self, None
		
class Ravencaller(Minion):
	Class, race, name = "Neutral", "", "Ravencaller"
	mana, attack, health = 3, 3, 1
	index = "Witchwood-Neutral-3-3-1-Minion-None-Ravencaller-Battlecry"
	needTarget, keyWord, description = False, "", "Battlecry: Add two random 1-Cost minions to your hand"
	
	def whenEffective(self, target=None, comment="", choice=0):
		minions = np.random.choice(list(self.Game.MinionswithCertainCost[1].values()), 2, replace=True)
		self.Game.Hand_Deck.addCardtoHand(minions, self.ID, "CreateUsingType")
		return self, None
		
#After cursing a minion, if the minion or Voodoo Doll itself is returned to hand or deck, the curse is removed.
#It will no longer have weird interactions with Chameleos-turned cards.
#A copy of Voodoo Doll can also kill the same cursed minion.
#A copy of the Voodoo Doll's deathrattle will also kill the same minion.
#A copy of the cursed minion won't be killed by the Voodoo Doll.
class VoodooDoll(Minion):
	Class, race, name = "Neutral", "", "Voodoo Doll"
	mana, attack, health = 3, 1, 1
	index = "Witchwood-Neutral-3-1-1-Minion-None-Voodoo Doll-Deathrattle-Battlecry"
	needTarget, keyWord, description = True, "", "Battlecry: Choose a minion. Deathrattle: Destroy the chosen minion"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [KillCursedMinion(self)]
	#暂时不确定巫毒娃娃对手牌中的随从是否可以产生诅咒。假设可以
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None and (target.onBoard or target.inHand):
			print("VoodooDoll's battlecry curses minion", target.name)
			for trigger in self.deathrattles:
				if type(trigger) == KillCursedMinion:
					trigger.cursedMinion = target
					trigger.cursedIdentity = target.identity
					
		return self, target
		
class KillCursedMinion(Deathrattle_Minion):
	def __init__(self, entity):
		self.blank_init(entity)
		self.cursedIdentity = [0, 0, 0]
		self.cursedMinion = None
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return target == self.entity and self.cursedMinion != None and self.cursedIdentity != [0, 0, 0]
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("Deathrattle: Kill the cursed minion %s triggers"%self.cursedMinion.name)
		#随从的identity的前两个是用于鉴别是否是卡片生成的，第三个用于区别这个随从有没有被返回过手牌。
		if self.cursedMinion.onBoard and self.cursedIdentity == self.cursedMinion.identity:
			self.cursedMinion.dead = True
			
	#巫毒娃娃的亡语结果被复制，还会杀死同一个被诅咒的随从。
	def selfCopy(self, newMinion):
		trigger = type(self)(newMinion)
		trigger.cursedIdentity = self.cursedIdentity
		trigger.cursedMinion = self.cursedMinion
		return trigger
		
class WalnutSprite(Minion):
	Class, race, name = "Neutral", "", "Walnut Sprite"
	mana, attack, health = 3, 3, 3
	index = "Witchwood-Neutral-3-3-3-Minion-None-Walnut Sprite-Echo"
	needTarget, keyWord, description = False, "Echo", "Echo"
	
	
class WitchsCauldron(Minion):
	Class, race, name = "Neutral", "", "Witch's Cauldron"
	mana, attack, health = 3, 0, 4
	index = "Witchwood-Neutral-3-0-4-Minion-None-Witch's Cauldron"
	needTarget, keyWord, description = False, "", "After a friendly minion dies, add a random Shaman spell to your hand"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.shamanSpells = []
		for key, value in self.Game.ClassCards["Shaman"].items():
			if "-Spell-" in key:
				self.shamanSpells.append(value)
		self.triggersonBoard = [Trigger_WitchsCauldron(self)]
		
class Trigger_WitchsCauldron(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionDeathResolutionFinished"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		#Technically, minion has to disappear before dies. But just in case.
		return self.entity.onBoard and target != self.entity and target.ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("After friendly minion %s dies and %s adds a random Shaman spell to player's hand."%(target.name, self.entity.name))
		self.entity.Game.Hand_Deck.addCardtoHand(np.random.choice(self.entity.shamanSpells), self.entity.ID, "CreateUsingType")
		
"""Mana 4 cards"""
class FelsoulInquisitor(Minion):
	Class, race, name = "Neutral", "Demon", "Felsoul Inquisitor"
	mana, attack, health = 4, 1, 6
	index = "Witchwood-Neutral-4-1-6-Minion-Demon-Felsoul Inquisitor-Taunt-Lifesteal"
	needTarget, keyWord, description = False, "Taunt,Lifesteal", "Taunt, Lifesteal"
	
	
class Lifedrinker(Minion):
	Class, race, name = "Neutral", "Beast", "Lifedrinker"
	mana, attack, health = 4, 3, 3
	index = "Witchwood-Neutral-4-3-3-Minion-Beast-Lifedrinker-Battlecry"
	needTarget, keyWord, description = False, "", "Battlecry: Deal 3 damage to the enemy hero. Restore 3 health to your hero"
	
	def whenEffective(self, target=None, comment="", choice=0):
		heal = 3 * (2 ** self.countHealDouble())
		print("Lifedrinker's battlecry deals 3 damage to the enemy hero and restores %d health to player"%heal)
		self.dealsDamage(self.Game.heroes[3-self.ID], 3)
		self.restoresHealth(self.Game.heroes[self.ID], heal)
		return self, None
		
class MadHatter(Minion):
	Class, race, name = "Neutral", "", "Mad Hatter"
	mana, attack, health = 4, 3, 2
	index = "Witchwood-Neutral-4-3-2-Minion-None-Mad Hatter-Battlecry"
	needTarget, keyWord, description = False, "", "Battlecry: Randomly toss 3 hats to other minions. Each hat gives +1/+1"
	
	def whenEffective(self, target=None, comment="", choice=0):
		targets = []
		for minion in self.Game.minionsonBoard(1) + self.Game.minionsonBoard(2):
			if minion != self:
				targets.append(minion)
		if targets != []:
			print("Mad Hatter's battlecry randomly gives 3 hats to other minions.")
			for i in range(3):
				np.random.choice(targets).buffDebuff(1, 1)
				
		return self, None
			
class NightProwler(Minion):
	Class, race, name = "Neutral", "Beast", "Night Prowler"
	mana, attack, health = 4, 3, 3
	index = "Witchwood-Neutral-4-3-3-Minion-Beast-Night Prowler-Battlecry"
	needTarget, keyWord, description = False, "", "Battlecry: If this is the only minion in the battlefield, gain +3/+3"
	
	def effectCanTrigger(self):
		allMinions = self.Game.minionsonBoard(1) + self.Game.minionsonBoard(2)
		extractfrom(self, allMinions)
		return allMinions == []
		
	def whenEffective(self, target=None, comment="", choice=0):
		onlyMiniononBoard = True
		for minion in self.Game.minionsonBoard(1) + self.Game.minionsonBoard(2):
			if minion != self:
				onlyMiniononBoard = False
				break
				
		if onlyMiniononBoard:
			print("Night Prowler's battlecry gives minion +3/+3.")
			self.buffDebuff(3, 3)
		return self, None
		
		
class Sandbinder(Minion):
	Class, race, name = "Neutral", "", "Sandbinder"
	mana, attack, health = 4, 2, 4
	index = "Witchwood-Neutral-4-2-4-Minion-None-Sandbinder-Battlecry"
	needTarget, keyWord, description = False, "", "Battlecry: Draw an Elemental from your deck"
	
	def whenEffective(self, target=None, comment="", choice=0):
		elementalsinDeck = []
		for card in self.Game.Hand_Deck.decks[self.ID]:
			if card.cardType == "Minion" and "Elemental" in card.race:
				elementalsinDeck.append(card)
				
		if elementalsinDeck != []:
			print("Sandbinder's battlecry lets player draw an Elemental from deck.")
			self.Game.Hand_Deck.drawCard(self.ID, np.random.choice(elementalsinDeck))
		return self, None
		
		
class Scaleworm(Minion):
	Class, race, name = "Neutral", "Beast", "Scaleworm"
	mana, attack, health = 4, 4, 4
	index = "Witchwood-Neutral-4-4-4-Minion-Beast-Scaleworm-Battlecry"
	needTarget, keyWord, description = False, "", "Battlecry: If you're holding a Dragon, gain +1 Attack and Rush"
	
	def effectCanTrigger(self):
		return self.Game.Hand_Deck.holdingDragon(self.ID, self)
		
	def whenEffective(self, target=None, comment="", choice=0):
		if self.Game.Hand_Deck.holdingDragon(self.ID):
			print("Scaleworm's battlecry gives minion +1 attack and Rush due to Dragon in hand.")
			self.buffDebuff(1, 0)
			self.getsKeyword("Rush")
		return self, None
		
		
class SwiftMessenger_Human(Minion):
	Class, race, name = "Neutral", "", "Swift Messenger"
	mana, attack, health = 4, 2, 6
	index = "Witchwood-Neutral-4-2-6-Minion-None-Swift Messenger Human-Rush-Shifting"
	needTarget, keyWord, description = False, "Rush", "Rush. Each turn this is in your hand, swap its Attack and Health"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersinHand = [Trigger_SwiftMessenger_Human(self)]
		
#假设狼人的手牌变形始终是手牌扳机
class Trigger_SwiftMessenger_Human(TriggerinHand):
	def __init__(self, entity):
		self.blank_init(entity, ["TurnEnds"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.inHand and ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("At the start of turn, Swift Messenger transforms into a worgen")
		worgen = SwiftMessenger_Worgen(self.Game, self.entity.ID)
		worgen.statReset(self.entity.health_Enchant, self.entity.attack_Enchant)
		worgen.identity = self.entity.identity
		#狼人形态会复制人形态的场上扳机，但是目前没有给随从外加手牌和牌库扳机的机制。
		worgen.triggersonBoard[0] = self.entity.triggersonBoard[1]
		self.Game.Hand_Deck.replaceCardinHand(self.entity, worgen)
		
class SwiftMessenger_Worgen(Minion):
	Class, race, name = "Neutral", "", "Swift Messenger"
	mana, attack, health = 4, 6, 2
	index = "Witchwood-Neutral-4-6-2-Minion-None-Swift Messenger Worgen-Rush-Uncollectible-Shifting"
	needTarget, keyWord, description = False, "Rush", "Rush. Each turn this is in your hand, swap its Attack and Health"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersinHand = [Trigger_SwiftMessenger_Worgen(self)]
		
class Trigger_SwiftMessenger_Worgen(TriggerinHand):
	def __init__(self, entity):
		self.blank_init(entity, ["TurnEnds"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.inHand and ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("At the end of turn, Swift Messenger transforms for into a human")
		human = SwiftMessenger_Human(self.entity.Game, self.entity.ID)
		human.statReset(self.entity.health_Enchant, self.entity.attack_Enchant)
		human.identity = self.entity.identity
		human.triggersonBoard[0] = self.entity.triggersonBoard[1]
		self.entity.Game.Hand_Deck.replaceCardinHand(self.entity, worgen)
		
		
class UnpoweredSteambot(Minion):
	Class, race, name = "Neutral", "Mech", "Unpowered Steambot"
	mana, attack, health = 4, 0, 9
	index = "Witchwood-Neutral-4-0-9-Minion-Mech-Unpowered Steambot-Taunt"
	needTarget, keyWord, description = False, "Taunt", "Taunt"
	
	
class WitchwoodPiper(Minion):
	Class, race, name = "Neutral", "Demon", "Witchwood Piper"
	mana, attack, health = 4, 3, 3
	index = "Witchwood-Neutral-4-3-3-Minion-Demon-Witchwood Piper-Battlecry"
	needTarget, keyWord, description = False, "", "Battlecry: Draw the lowest Cost minion from your deck"
	
	def whenEffective(self, target=None, comment="", choice=0):
		minionsinDeck = []
		lowestMana = np.inf
		for card in self.Game.Hand_Deck.decks[self.ID]:
			if card.cardType == "Minion":
				if card.mana_set < lowestMana:
					minionsinDeck = [card]
					lowestMana = card.mana_set
				elif card.mana_set == lowestMana:
					minionsinDeck.append(card)
					
		if minionsinDeck != []:
			print("Witchwood Piper's battlecry lets player draw the lowest cost minion from deck")
			self.Game.Hand_Deck.drawCard(self.ID, np.random.choice(minionsinDeck))
			
		return self, None
		
"""Mana 5 cards"""
class ChiefInspector(Minion):
	Class, race, name = "Neutral", "", "Chief Inspector"
	mana, attack, health = 5, 4, 6
	index = "Witchwood-Neutral-5-4-6-Minion-None-Chief Inspector-Battlecry"
	needTarget, keyWord, description = False, "", "Battlecry: Destroy all enemy Secrets"
	
	def whenEffective(self, target=None, comment="", choice=0):
		print("Chief Inspector's battlecry destroys all enemy secrets.")
		self.Game.SecretHandler.extractSecrets(3-self.ID, all=True)
		return self, None
		
class ClockworkAutomation(Minion):
	Class, race, name = "Neutral", "Mech", "Clockwork Automation"
	mana, attack, health = 5, 4, 4
	index = "Witchwood-Neutral-5-4-4-Minion-Mech-Clockwork Automation"
	needTarget, keyWord, description = False, "", "Double the damage and healing of your Hero Power"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.marks["Hero Power Double Heal and Damage"] = 1
		
		
class DollmasterDorian(Minion):
	Class, race, name = "Neutral", "", "Dollmaster Dorian"
	mana, attack, health = 5, 2, 6
	index = "Witchwood-Neutral-5-2-6-Minion-None-Dollmaster Dorian-Legendary"
	needTarget, keyWord, description = False, "", "Whenever you draw a minion, summon a 1/1 copy of it"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_DollmasterDorian(self)]
		
class Trigger_DollmasterDorian(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["CardDrawn"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and target.cardType == "Minion" and target.ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("When player draws minion %s, %s summons a 1/1 copy of it."%(target.name, self.entity.name))
		Copy = target.selfCopy(self.entity.ID, 1, 1)
		self.entity.Game.summonMinion(Copy, self.entity.position+1, self.entity.ID)
		
		
class MuckHunter(Minion):
	Class, race, name = "Neutral", "", "Muck Hunter"
	mana, attack, health = 5, 5, 8
	index = "Witchwood-Neutral-5-5-8-Minion-None-Muck Hunter-Rush-Battlecry"
	needTarget, keyWord, description = False, "Rush", "Rush. Battlecry: Summon two 2/1 Mucklings for your opponent"
	
	def whenEffective(self, target=None, comment="", choice=0):
		print("Muck Hunter's battlecry summons two 2/1 Mucklings for enemy.")
		self.Game.summonMinion([Muckling(self.Game, 3-self.ID) for i in range(2)], (-1, "totheRightEnd"), self.ID)
		return self, None
		
class Muckling(Minion):
	Class, race, name = "Neutral", "", "Muckling"
	mana, attack, health = 1, 2, 1
	index = "Witchwood-Neutral-1-2-1-Minion-None-Muckling-Uncollectible"
	needTarget, keyWord, description = False, "", ""
	
	
class RottenApplebaum(Minion):
	Class, race, name = "Neutral", "", "Rotten Applebaum"
	mana, attack, health = 5, 4, 5
	index = "Witchwood-Neutral-5-4-5-Minion-None-Rotten Applebaum-Deathrattle-Taunt"
	needTarget, keyWord, description = False, "Taunt", "Taunt. Deathrattle: Restore 4 health to your hero"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [Restore4HealthtoHero(self)]
		
class Restore4HealthtoHero(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		heal = 4 * (2 ** self.countHealDouble())
		print("Deathrattle: Restore %d health to your hero triggers."%heal)
		self.minion.restoresHealth(self.Game.heroes[self.ID], heal)	
		
		
class WicthwoodGrizzly(Minion):
	Class, race, name = "Neutral", "Beast", "Wicthwood Grizzly"
	mana, attack, health = 5, 3, 12
	index = "Witchwood-Neutral-5-3-12-Minion-Beast-Wicthwood Grizzly-Battlecry-Taunt"
	needTarget, keyWord, description = False, "Taunt", "Taunt. Battlecry: Lose 1 Health for each card in your opponent's hand"
	
	def whenEffective(self, target=None, comment="", choice=0):
		healthLoss = len(self.Game.Hand_Deck.hands[3-self.ID])
		print("Witchwood Grizzly's battlecry deducts %d Health for cards in opponent's hand."%healthLoss)
		self.statReset(False, self.health-healthLoss)
		return self, None
		
"""Mana 6 minions"""
class MossyHorror(Minion):
	Class, race, name = "Neutral", "", "Mossy Horror"
	mana, attack, health = 6, 2, 7
	index = "Witchwood-Neutral-6-2-7-Minion-None-Mossy Horror-Battlecry"
	needTarget, keyWord, description = False, "", "Battlecry: Destroy all other minions with 2 or less Attack"
	
	def whenEffective(self, target=None, comment="", choice=0):
		for minion in self.Game.minionsonBoard(1) + self.Game.minionsonBoard(2):
			if minion.attack < 3 and minion != self:
				minion.dead = True
				
		return self, None
		
"""Mana 7 cards"""
class AzalinaSoulthief(Minion):
	Class, race, name = "Neutral", "", "Azalina Soulthief"
	mana, attack, health = 7, 3, 3
	index = "Witchwood-Neutral-7-3-3-Minion-None-Azalina Soulthief-Battlecry-Legendary"
	needTarget, keyWord, description = False, "", "Battlecry: Replace your hand with a copy of your opponent's"
	
	def whenEffective(self, target=None, comment="", choice=0):
		print("Azalina Soulthief's battlecry replaces player's hand with a copy of opponent's.")
		Copies = []
		for card in self.Game.Hand_Deck.hands[3-self.ID]:
			Copies.append(card.selfCopy(self.ID))
			
		self.Game.Hand_Deck.extractfromHand(None, all=True, ID=self.ID)
		self.Game.Hand_Deck.addCardtoHand(Copies, self.ID)
		return self, None
		
#Only Rush: 1; Only Lifesteal: 2; Only Deathrattle: 3
#Both Rush&Lifesteal: 4, Both Lifesteal&Deathrattle: 5; Both Rush&Deathrattle: 6;
#All three: 7
class CountessAshmore(Minion):
	Class, race, name = "Neutral", "", "Countess Ashmore"
	mana, attack, health = 7, 6, 6
	index = "Witchwood-Neutral-7-6-6-Minion-None-Countess Ashmore-Battlecry-Legendary"
	needTarget, keyWord, description = False, "", "Draw a Rush, Lifesteal and Deathrattle card from your deck"
	
	#The order is: Draw a random Rush card, then a Lifesteal card, finally a Deathrattle card. Cards that have more than one keyword won't make a difference.
	def whenEffective(self, target=None, comment="", choice=0):
		print("Countess Ashmore's battlecry lets player draw a Deathrattle, Lifesteal and Rush card from deck.")
		rushCards, lifestealCards, deathrattleCards = [], [], []
		for card in self.Game.Hand_Deck.decks[self.ID]:
			if card.cardType == "Minion" and "-Rush" in card.index:
				rushCards.append(card)
		if rushCards != []:
			self.Game.Hand_Deck.drawCard(self.ID, np.random.choice(rushCards))
			
		for card in self.Game.Hand_Deck.decks[self.ID]:
			if "Lifesteal" in card.index:
				lifestealCards.append(card)
		if lifestealCards != []:
			self.Game.Hand_Deck.drawCard(self.ID, np.random.choice(lifestealCards))
			
		for card in self.Game.Hand_Deck.decks[self.ID]:
			if "Deathrattle" in card.index:
				deathrattleCards.append(card)
		if deathrattleCards != []:
			self.Game.Hand_Deck.drawCard(self.ID, np.random.choice(deathrattleCards))
			
		return self, None
		
		
class DarkmireMoonkin(Minion):
	Class, race, name = "Neutral", "", "Darkmire Moonkin"
	mana, attack, health = 7, 2, 8
	index = "Witchwood-Neutral-7-2-8-Minion-None-Darkmire Moonkin-Spell Damage"
	needTarget, keyWord, description = False, "Spell Damage", "Spell Damage +1"
	
	
class FuriousEttin(Minion):
	Class, race, name = "Neutral", "", "Furious Ettin"
	mana, attack, health = 7, 5, 8
	index = "Witchwood-Neutral-7-5-9-Minion-None-Furious Ettin-Taunt"
	needTarget, keyWord, description = False, "Taunt", "Taunt"
	
	
class WorgenAbomination(Minion):
	Class, race, name = "Neutral", "", "Worgen Abomination"
	mana, attack, health = 7, 6, 6
	index = "Witchwood-Neutral-7-6-6-Minion-None-Worgen Abomination"
	needTarget, keyWord, description = False, "", "At the end of your turn, deal 2 damage to all other damaged minions"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_WorgenAbomination(self)]
		
class Trigger_WorgenAbomination(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["TurnEnds"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("At the end of turn, %s deals 2 damage to ALL other damaged minions."%self.entity.name)
		targets = []
		for minion in self.entity.Game.minionsonBoard(1) + self.entity.Game.minionsonBoard(2):
			if minion.health < minion.health_upper and minion != self:
				targets.append(minion)
				
		if targets != []:
			self.entity.dealsAOE(targets, [2 for obj in targets])
			
			
class Wyrmguard(Minion):
	Class, race, name = "Neutral", "", "Wyrmguard"
	mana, attack, health = 7, 3, 11
	index = "Witchwood-Neutral-7-3-11-Minion-None-Wyrmguard-Battlecry"
	needTarget, keyWord, description = False, "", "Battlecry: If you're holding a Dragon, gain +1 Attack and Taunt"
	
	def effectCanTrigger(self):
		return self.Game.Hand_Deck.holdingDragon(self.ID, self)
		
	def whenEffective(self, target=None, comment="", choice=0):
		if self.Game.Hand_Deck.holdingDragon(self.ID):
			print("Wyrmguard's battlecry gives minion +1 attack and Taunt due to Dragon in hand.")
			self.buffDebuff(1, 0)
			self.getsKeyword("Taunt")
		return self, None
		
"""Mana 8 cards"""
class CauldronElemental(Minion):
	Class, race, name = "Neutral", "Elemental", "Cauldron Elemental"
	mana, attack, health = 8, 7, 7
	index = "Witchwood-Neutral-8-7-7-Minion-Elemental-Cauldron Elemental"
	needTarget, keyWord, description = False, "", "Your other Elementals have +2 Attack"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.auras["Buff Aura"] = BuffAura_Dealer_All(self, self.applicable, 2, 0)
		
	def applicable(self, target):
		return "Elemental" in target.race
		
		
class DerangedDoctor(Minion):
	Class, race, name = "Neutral", "", "Deranged Doctor"
	mana, attack, health = 8, 8, 8
	index = "Witchwood-Neutral-8-8-8-Minion-None-Deranged Doctor-Deathrattle"
	needTarget, keyWord, description = False, "", "Deathrattle: Restore 8 Health to your hero"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [Restore8HealthtoHero(self)]
		
class Restore8HealthtoHero(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		heal = 8 * (2 ** self.countHealDouble())
		print("Deathrattle: Restore 8 health to your hero triggers.")
		self.entity.restoresHealth(self.Game.heroes[self.entity.ID], heal)
		
		
class GilneanRoyalGuard_Human(Minion):
	Class, race, name = "Neutral", "", "Gilnean Royal Guard"
	mana, attack, health = 8, 3, 8
	index = "Witchwood-Neutral-8-3-8-Minion-None-Gilnean Royal Guard Human-Rush-Divine Shield-Shifting"
	needTarget, keyWord, description = False, "Rush,Divine Shield", "Rush, Divine Shield. Each turn this is in your hand, swap its Attack and Health"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersinHand = [Trigger_GilneanRoyalGuard_Human(self)]
		
#假设狼人的手牌变形始终是手牌扳机
class Trigger_GilneanRoyalGuard_Human(TriggerinHand):
	def __init__(self, entity):
		self.blank_init(entity, ["TurnEnds"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.inHand and ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("At the start of turn, Gilnean Royal Guard transforms into a worgen")
		worgen = GilneanRoyalGuard_Worgen(self.entity.Game, self.entity.ID)
		worgen.statReset(self.entity.health_Enchant, self.entity.attack_Enchant)
		worgen.identity = self.entity.identity
		#狼人形态会复制人形态的场上扳机，但是目前没有给随从外加手牌和牌库扳机的机制。
		worgen.triggersonBoard[0] = self.entity.triggersonBoard[1]
		self.entity.Game.Hand_Deck.replaceCardinHand(self.entity, worgen)
		
class GilneanRoyalGuard_Worgen(Minion):
	Class, race, name = "Neutral", "", "Gilnean Royal Guard"
	mana, attack, health = 8, 8, 3
	index = "Witchwood-Neutral-8-8-3-Minion-None-Gilnean Royal Guard Worgen-Rush-Divine Shield-Uncollectible-Shifting"
	needTarget, keyWord, description = False, "Rush,Divine Shield", "Rush, Divine Shield. Each turn this is in your hand, swap its Attack and Health"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersinHand = [Trigger_GilneanRoyalGuard_Worgen(self)]
		
class Trigger_GilneanRoyalGuard_Worgen(TriggerinHand):
	def __init__(self, entity):
		self.blank_init(entity, ["TurnEnds"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.inHand and ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("At the start of turn, Swift Messenger transforms for into a human")
		human = GilneanRoyalGuard_Human(self.entity.Game, self.entity.ID)
		human.statReset(self.entity.health_Enchant, self.entity.attack_Enchant)
		human.identity = self.entity.identity
		human.triggersonBoard[0] = self.entity.triggersonBoard[1]
		self.entity.Game.Hand_Deck.replaceCardinHand(self.entity, worgen)
		
		
class SplittingFesteroot(Minion):
	Class, race, name = "Neutral", "", "Splitting Festeroot"
	mana, attack, health = 8, 4, 4
	index = "Witchwood-Neutral-8-4-4-Minion-None-Splitting Festeroot-Deathrattle"
	needTarget, keyWord, description = False, "", "Deathrattle: Summon two 2/2 Splitting Saplings"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [SummonTwoSplittingSaplings(self)]
		
class SummonTwoSplittingSaplings(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		pos = (self.entity.position, "totheRight") if self.entity in self.entity.Game.minions[self.entity.ID] else (-1, "totheRightEnd")
		print("Deathrattle: Summone two 2/2 Splitting Saplings triggers.")
		self.entity.Game.summonMinion([SplittingSapling(self.entity.Game, self.entity.ID) for i in range(2)], pos, self.entity.ID)
		
class SplittingSapling(Minion):
	Class, race, name = "Neutral", "", "Splitting Sapling"
	mana, attack, health = 3, 2, 2
	index = "Witchwood-Neutral-3-2-2-Minion-None-Splitting Sapling-Deathrattle-Uncollectible"
	needTarget, keyWord, description = False, "", "Deathrattle: Summon two 1/1 Woodchips"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [SummonTwoWoodchips(self)]
		
class SummonTwoWoodchips(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		pos = (self.entity.position, "totheRight") if self.entity in self.entity.Game.minions[self.entity.ID] else (-1, "totheRightEnd")
		print("Deathrattle: Summone two 1/1 Woodchips triggers.")
		self.entity.Game.summonMinion([Woodchip(self.entity.Game, self.entity.ID) for i in range(2)], pos, self.entity.ID)
		
class Woodchip(Minion):
	Class, race, name = "Neutral", "", "Woodchip"
	mana, attack, health = 1, 1, 1
	index = "Witchwood-Neutral-1-1-1-Minion-None-Woodchip-Uncollectible"
	needTarget, keyWord, description = False, "", ""
	
"""Druid cards"""
class WitchwoodApple(Spell):
	Class, name = "Druid", "Witchwood Apple"
	needTarget, mana = False, 2
	index = "Witchwood-Druid-2-Spell-Witchwood Apple"
	description = "Add three 2/2 Treants to your hand"
	def whenEffective(self, target=None, comment="", choice=0):
		print("Witchwood Apple is cast and adds three 2/2 Treants to player's hand.")
		self.Game.Hand_Deck.addCardtoHand([Treant_Witchwood for i in range(3)], self.ID, "CreateUsingType")
		return None
		
class Treant_Witchwood(Minion):
	Class, race, name = "Druid", "", "Treant"
	mana, attack, health = 2, 2, 2
	index = "Witchwood-Druid-2-2-2-Minion-None-Treant-Uncollectible"
	needTarget, keyWord, description = False, "", ""
	
	
class DruidoftheScythe(Minion):
	Class, race, name = "Druid", "", "Druid of the Scythe"
	mana, attack, health = 3, 2, 2
	index = "Witchwood-Druid-3-2-2-Minion-None-Druid of the Scythe-Choose One"
	needTarget, keyWord, description = False, "", "Choose One- Transform into a 4/2 with Rush; or a 2/4 with Taunt"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.chooseOne = 1
		self.options = [DirePantherForm(), DireWolfForm()]
		
	def played(self, target=None, choice=0, mana=0, comment=""):
		self.statReset(self.attack_Enchant, self.health_Enchant)
		self.appears()
		if choice == "ChooseBoth":
			minion = DruidoftheScythe_Both(self.Game, self.ID)
		elif choice == 0:
			minion = DruidoftheScythe_Rush(self.Game, self.ID)
		else:
			minion = DruidoftheScythe_Taunt(self.Game, self.ID)
		#抉择变形类随从的入场后立刻变形。
		self.Game.transform(self, minion)
		self.Game.sendSignal("MinionPlayed", self.ID, minion, None, mana, "", choice)
		self.Game.sendSignal("MinionSummoned", self.ID, minion, None, mana, "")
		self.Game.gathertheDead()
		if minion != None and minion.onBoard:
			self.Game.sendSignal("MinionBeenSummoned", self.ID, minion, None, mana, "")
			
		return minion
		
class DirePantherForm:
	def __init__(self):
		self.name = "Dire Panther Form"
		self.description = "4/2 with Rush"
		
	def available(self):
		return True
		
class DireWolfForm:
	def __init__(self):
		self.name = "Dire Wolf Form"
		self.description = "2/4 with Taunt"
		
	def available(self):
		return True
		
class DruidoftheScythe_Rush(Minion):
	Class, race, name = "Druid", "Beast", "Druid of the Scythe"
	mana, attack, health = 3, 4, 2
	index = "Witchwood-Druid-3-4-2-Minion-Beast-Druid of the Scythe-Rush-Uncollectible"
	needTarget, keyWord, description = False, "Rush", "Rush"
	
class DruidoftheScythe_Taunt(Minion):
	Class, race, name = "Druid", "Beast", "Druid of the Scythe"
	mana, attack, health = 3, 2, 4
	index = "Witchwood-Druid-3-2-4-Minion-Beast-Druid of the Scythe-Taunt-Uncollectible"
	needTarget, keyWord, description = False, "Taunt", "Taunt"
	
class DruidoftheScythe_Both(Minion):
	Class, race, name = "Druid", "Beast", "Druid of the Scythe"
	mana, attack, health = 3, 4, 4
	index = "Witchwood-Druid-3-4-4-Minion-Beast-Druid of the Scythe-Rush-Taunt-Uncollectible"
	needTarget, keyWord, description = False, "Rush,Taunt", "Rush, Taunt"
	
	
class FerociousHowl(Spell):
	Class, name = "Druid", "Ferocious Howl"
	needTarget, mana = False, 3
	index = "Witchwood-Druid-3-Spell-Ferocious Howl"
	description = "Draw a card. Gain 1 Armor for each card in your hand"
	def whenEffective(self, target=None, comment="", choice=0):
		print("Ferocious Howl is cast. Player draws a card and gains 1 armor for each card in hand.")
		self.Game.Hand_Deck.drawCard(self.ID)
		self.Game.heroes[self.ID].gainsArmor(len(self.Game.Hand_Deck.hands[self.ID]))
		return None
		
		
class WitchingHour(Spell):
	Class, name = "Druid", "Witching Hour"
	needTarget, mana = False, 3
	index = "Witchwood-Druid-3-Spell-Witching Hour"
	description = "Summon a random friendly Beast that died this game"
	def whenEffective(self, target=None, comment="", choice=0):
		print("Witching Hour is cast and summons a friendly Beast that died this game.")
		friendlyBeasts = []
		for index in self.Game.CounterHandler.minionsDiedThisGame[self.ID]:
			if "-Beast-" in index:
				friendlyBeasts.append(index)
				
		if friendlyBeasts != []:
			minion = self.Game.cardPool[np.random.choice(friendlyBeasts)]
			self.Game.summonMinion(minion(self.Game, self.ID), -1, self.ID)
		return None
		
		
class ForestGuide(Minion):
	Class, race, name = "Druid", "", "Forest Guide"
	mana, attack, health = 4, 1, 6
	index = "Witchwood-Druid-4-1-6-Minion-None-Forest Guide"
	needTarget, keyWord, description = False, "", "At the end of turn, both players draw a card"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_ForestGuide(self)]
		
class Trigger_ForestGuide(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["TurnEnds"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("At the end of turn, Forest Guide lets each player draw a card.")
		self.entity.Game.Hand_Deck.drawCard(self.entity.ID)
		self.entity.Game.Hand_Deck.drawCard(3-self.entity.ID)
		
		
class WhisperingWoods(Spell):
	Class, name = "Druid", "Whispering Woods"
	needTarget, mana = False, 4
	index = "Witchwood-Druid-4-Spell-Whispering Woods"
	description = "Summon a 1/1 Wisp for each card in your hand"
	def available(self):
		return self.Game.spaceonBoard(self.ID) > 0
		
	def whenEffective(self, target=None, comment="", choice=0):
		print("Whispering Woods is cast and summons a 1/1 Wisp for each card in player's hand.")
		handSize = len(self.Game.Hand_Deck.hands[self.ID])
		wisps = [Wisp_Witchwood(self.Game, self.ID) for i in range(handSize)]
		self.Game.summonMinion(wisps, (-1, "totheRightEnd"), self.ID)
		return None
		
class Wisp_Witchwood(Minion):
	Class, race, name = "Neutral", "", "Wisp"
	mana, attack, health = 1, 1, 1
	index = "Witchwood-Neutral-1-1-1-Minion-None-Wisp-Uncollectible"
	needTarget, keyWord, description = False, "", ""
	
	
class BewitchedGuardian(Minion):
	Class, race, name = "Druid", "", "Bewitched Guardian"
	mana, attack, health = 5, 4, 1
	index = "Witchwood-Druid-5-4-1-Minion-None-Bewitched Guardian-Taunt-Battlecry"
	needTarget, keyWord, description = False, "Taunt", "Taunt. Battlecry: Gain +1 Health for each card in your hand"
	
	def whenEffective(self, target=None, comment="", choice=0):
		if self.onBoard or self.inHand:
			num = len(self.Game.Hand_Deck.hands[self.ID])
			print(self.name, " is played and gains +1 health for each hand in player's hand.")
			self.buffDebuff(0, num)
		return self, None
		
		
class DuskfallenAviana(Minion):
	Class, race, name = "Druid", "", "Duskfallen Aviana"
	mana, attack, health = 5, 3, 7
	index = "Witchwood-Druid-5-3-7-Minion-None-Duskfallen Aviana-Legendary"
	needTarget, keyWord, description = False, "", "On each player's turn, the first card played costs (0)"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.manaAura = EachPlayersFirstCardCosts0(self)
		self.triggersonBoard = [Trigger_DuskfallenAviana(self)]
		self.appearResponse = [self.activateAura]
		self.silenceResponse = [self.deactivateAura]
		self.disappearResponse = [self.deactivateAura]
		
	#Considering the possible change of control of the minion, the minion itself should control the aura.
	def activateAura(self):
		print("Duskfallen Aviana lets each player's first card on his turn cost 0.")
		if self.Game.CounterHandler.cardsPlayedThisTurn[self.ID] == []:
			self.Game.ManaHandler.CardAuras.append(self.manaAura)
			self.Game.ManaHandler.calcMana_All()
			
	def deactivateAura(self):
		print("Duskfallen Aviana's mana aura is removed. Each player's first card no longer cost 0.")
		extractfrom(self.manaAura, self.Game.ManaHandler.CardAuras)
		self.Game.ManaHandler.calcMana_All()
		
class Trigger_DuskfallenAviana(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["TurnStarts", "ManaCostPaid"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		#不需要响应回合结束，因为光环自身被标记为temporary，会在回合结束时自行消失。
		#因为每个玩家只有可能会在自己的回合出牌，所以列表中的所有信号都可以触发扳机
		if signal == "ManaCostPaid" and subject.cardType == "Hero Power":
			return False
		return self.entity.onBoard
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		if signal == "TurnStarts":
			print("At the start of turn, %s restarts the mana aura and player's first card to play costs (0)."%self.entity.name)
			self.entity.activateAura()
		else: #signal == "ManaCostPaid"
			self.entity.deactivateAura()
			
class EachPlayersFirstCardCosts0:
	def __init__(self, minion):
		self.minion = minion
		self.temporary = True
		
	def handleMana(self, target):
		if target.ID == self.Game.turn:
			target.mana = 0
			
	def deactivate(self): #这个函数由Game.ManaHandler来调用，用于回合结束时的费用光环取消。
		extractfrom(self, self.minion.Game.ManaHandler.CardAuras)
		self.minion.Game.ManaHandler.calcMana_All()
		
		
class Splintergraft(Minion):
	Class, race, name = "Druid", "", "Splintergraft"
	mana, attack, health = 8, 8, 8
	index = "Witchwood-Druid-8-8-8-Minion-None-Splintergraft-Battlecry-Legendary"
	needTarget, keyWord, description = True, "", "Battlecry: Choose a friendly minion. Add a 10/10 copy to your hand that costs (10)"
	
	def targetExists(self, choice=0):
		return self.selectableFriendlyMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.ID == self.ID
		
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			print("Splintergraft's battlecry adds a 10/10 copy of friendly minion %s to player's hand."%target)
			copiedMinion = type(target)(self.Game, self.ID)
			copiedMinion.statReset(10, 10)
			copiedMinion.mana_set = 10
			self.Game.Hand_Deck.addCardtoHand(copiedMinion, self.ID)
		return self, target
		
"""Hunter cards"""
class HuntingMastiff(Minion):
	Class, race, name = "Hunter", "Beast", "Hunting Mastiff"
	mana, attack, health = 2, 2, 1
	index = "Witchwood-Hunter-2-2-1-Minion-Beast-Hunting Mastiff-Rush-Echo"
	needTarget, keyWord, description = False, "Echo,Rush", "Echo, Rush"
	
	
class RatTrap(Secret):
	Class, name = "Hunter", "Rat Trap"
	needTarget, mana = False, 2
	index = "Witchwood-Hunter-2-Spell-Rat Trap--Secret"
	description = "After your opponent plays three cards in a turn, summon a 6/6 Rat"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_RatTrap(self)]
		
class Trigger_RatTrap(SecretTrigger):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionBeenPlayed", "SpellBeenPlayed", "WeaponBeenPlayed", "HeroCardBeenPlayed"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.ID != self.entity.Game.turn and subject.ID != self.entity.ID and len(self.entity.Game.CounterHandler.cardsPlayedThisTurn[3-self.entity.ID]) >= 3 and self.entity.Game.spaceonBoard(self.entity.ID) > 0
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("After opponent plays three cards in a turn, Secret Rat Trap is triggered and summons a 6/6 Rat.")
		self.entity.Game.summonMinion(DoomRat(self.entity.Game, self.entity.ID), -1, self.entity.ID)
		
class DoomRat(Minion):
	Class, race, name = "Hunter", "Beast", "Doom Rat"
	mana, attack, health = 6, 6, 6
	index = "Witchwood-Hunter-6-6-6-Minion-Beast-Doom Rat-Uncollectible"
	needTarget, keyWord, description = False, "", ""
	
	
class DuskhavenHunter_Human(Minion):
	Class, race, name = "Hunter", "", "Duskhaven Hunter"
	mana, attack, health = 3, 2, 5
	index = "Witchwood-Hunter-3-2-5-Minion-None-Duskhaven Hunter Human-Stealth-Shifting"
	needTarget, keyWord, description = False, "Stealth", "Stealth. Each turn this is in your hand, swap its Attack and Health"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersinHand = [Trigger_DuskhavenHunter_Human(self)]
		
#假设狼人的手牌变形始终是手牌扳机
class Trigger_DuskhavenHunter_Human(TriggerinHand):
	def __init__(self, entity):
		self.blank_init(entity, ["TurnEnds"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.inHand and ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("At the start of turn, Duskhaven Hunter transforms into a worgen")
		worgen = DuskhavenHunter_Worgen(self.entity.Game, self.entity.ID)
		worgen.statReset(self.entity.health_Enchant, self.entity.attack_Enchant)
		worgen.identity = self.entity.identity
		#狼人形态会复制人形态的场上扳机，但是目前没有给随从外加手牌和牌库扳机的机制。
		worgen.triggersonBoard[0] = self.entity.triggersonBoard[1]
		self.entity.Game.Hand_Deck.replaceCardinHand(self.entity, worgen)
		
class DuskhavenHunter_Worgen(Minion):
	Class, race, name = "Hunter", "", "Duskhaven Hunter"
	mana, attack, health = 3, 5, 2
	index = "Witchwood-Hunter-3-5-2-Minion-None-Duskhaven Hunter Worgen-Stealth-Uncollectible-Shifting"
	needTarget, keyWord, description = False, "Stealth", "Stealth. Each turn this is in your hand, swap its Attack and Health"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersinHand = [Trigger_DuskhavenHunter_Worgen(self)]
		
class Trigger_DuskhavenHunter_Worgen(TriggerinHand):
	def __init__(self, entity):
		self.blank_init(entity, ["TurnEnds"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.inHand and ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("At the start of turn, Duskhaven Hunter transforms for into a human")
		human = DuskhavenHunter_Human(self.entity.Game, self.entity.ID)
		human.statReset(self.entity.health_Enchant, self.entity.attack_Enchant)
		human.identity = self.entity.identity
		human.triggersonBoard[0] = self.entity.triggersonBoard[1]
		self.entity.Game.Hand_Deck.replaceCardinHand(self.entity, worgen)
		
		
class DireFrenzy(Spell):
	Class, name = "Hunter", "Dire Frenzy"
	needTarget, mana = True, 4
	index = "Witchwood-Hunter-4-Spell-Dire Frenzy"
	description = "Give a Beast +3/+3. Shuffle three copies into your deck with +3/+3"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and "Beast" in target.race and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			print("Dire Frenzy gives Beast %s +3/+3 and shuffles three +3/+3 copies of it into player's deck"%target.name)
			target.buffDebuff(3, 3)
			for i in range(3):
				beast = type(target)(self.Game, self.ID)
				beast.buffDebuff(3, 3)
				self.Game.Hand_Deck.shuffleCardintoDeck(beast, self.ID)
		return target
		
		
class HoundmasterShaw(Minion):
	Class, race, name = "Hunter", "", "Houndmaster Shaw"
	mana, attack, health = 4, 3, 6
	index = "Witchwood-Hunter-4-3-6-Minion-None-Houndmaster Shaw-Legendary"
	needTarget, keyWord, description = False, "", "Your other minions have Rush"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.auras["Has Aura"] = HasAura_Dealer(self, self.applicable, "Rush")
		
	def applicable(self, target):
		return target != self
		
		
class Toxmonger(Minion):
	Class, race, name = "Hunter", "", "Toxmonger"
	mana, attack, health = 4, 2, 4
	index = "Witchwood-Hunter-4-2-4-Minion-None-Toxmonger"
	needTarget, keyWord, description = False, "", "Whenever you player a 1-Cost minion, give it Poisonous"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_Toxmonger(self)]
		
class Trigger_Toxmonger(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionPlayed"])
		
	#The number here is the mana used to play the minion
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject != self.entity and subject.ID == self.entity.ID and number == 1
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("A 1-Cost friendly minion %s is played and %s gives it Poisonous."%(subject.name, self.entity.name))
		subject.getsKeyword("Poisonous")
		
		
class WingBlast(Spell):
	Class, name = "Hunter", "Wing Blast"
	needTarget, mana = True, 4
	index = "Witchwood-Hunter-4-Spell-Wing Blast"
	description = "Deal 4 damage to a minion. If a minion died this turn, this costs (1)"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersinHand = [Trigger_WingBlast(self)]
		
	def selfManaChange(self):
		if self.Game.CounterHandler.minionsDiedThisTurn[1] != [] or self.Game.CounterHandler.minionsDiedThisTurn[2] != []:
			self.mana = 1
		#没有法术可以因其他的牌的效果获得回响。不必在普通法术的selfManaChange方法下处理回响牌的费用问题
		
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			damage = (4 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			print("Wing Blast is cast and deals %d damage to "%damage, target.name)
			self.dealsDamage(target, damage)
		return target
		
class Trigger_WingBlast(TriggerinHand):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionDies", "TurnStarts", "TurnEnds"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.inHand
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("A minion dies or turn starts/ends, Wing Blast resets its cost.")
		self.entity.Game.ManaHandler.calcMana_Single(self.entity)
		
		
class CarrionDrake(Minion):
	Class, race, name = "Hunter", "Dragon", "Carrion Drake"
	mana, attack, health = 5, 3, 7
	index = "Witchwood-Hunter-5-3-7-Minion-Dragon-Carrion Drake-Battlecry"
	needTarget, keyWord, description = False, "", "Battlecry: If a minion died this turn, gain Poisonous"
	
	def effectCanTrigger(self):
		return self.Game.CounterHandler.minionsDiedThisTurn[1] != [] or self.Game.CounterHandler.minionsDiedThisTurn[2] != []
		
	def whenEffective(self, target=None, comment="", choice=0):
		if self.Game.CounterHandler.minionsDiedThisTurn[1] != [] or self.Game.CounterHandler.minionsDiedThisTurn[2] != []:
			print("Carrion Drake's battlecry gives the minion Poisonous.")
			self.getsKeyword("Poisonous")
		return self, None
		
		
class VilebroodSkitterer(Minion):
	Class, race, name = "Hunter", "Beast", "Vilebrood Skitterer"
	mana, attack, health = 5, 1, 3
	index = "Witchwood-Hunter-5-1-3-Minion-Beast-Vilebrood Skitterer-Rush-Poisonous"
	needTarget, keyWord, description = False, "Rush,Poisonous", "Rush, Poisonous"
	
	
class Emeriss(Minion):
	Class, race, name = "Hunter", "Dragon", "Emeriss"
	mana, attack, health = 10, 8, 8
	index = "Witchwood-Hunter-10-8-8-Minion-Dragon-Emeriss-Battlecry-Legendary"
	needTarget, keyWord, description = False, "", "Battlecry: Double the Attack and Health of all minions in your hand"
	
	def whenEffective(self, target=None, comment="", choice=0):
		print("Emeriss' battlecry doubles the stats of all minions in player's hand.")
		for card in self.Game.Hand_Deck.hands[self.ID]:
			if card.cardType == "Minion":
				#Temp attack change in hand should also be considered
				card.statReset(card.attack*2, card.health_upper*2)
		return self, None
		
"""Mage cards"""
class ArchmageArugal(Minion):
	Class, race, name = "Mage", "", "Archmage Arugal"
	mana, attack, health = 2, 2, 2
	index = "Witchwood-Mage-2-2-2-Minion-None-Archmage Arugal-Legendary"
	needTarget, keyWord, description = False, "", "Whenever you draw a minion, add a copy of it to your hand"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_ArchmageArugal(self)]
		
class Trigger_ArchmageArugal(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["CardDrawn"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		#Technically, minion has to disappear before dies. But just in case.
		return self.entity.onBoard and target.cardType == "Minion" and target.ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("Whenever player draws a minion, %s adds a copy of it to player's hand."%(target.name, self.entity.name))
		self.entity.Game.Hand_Deck.addCardtoHand(target.selfCopy(self.entity.ID), self.entity.ID)
		
		
class BookofSpecters(Spell):
	Class, name = "Mage", "Book of Specters"
	needTarget, mana = False, 2
	index = "Witchwood-Mage-2-Spell-Book of Specters"
	description = "Draw 3 cards. Discard any spells drawn"
	#The spells will be discarded immediately before drawing the next card.
	#The discarding triggers triggers["Discarded"] and send signals.
	#If the hand is full, then no discard at all. The drawn cards vanish.	
	#The "cast when drawn" spells can take effect as usual
	def whenEffective(self, target=None, comment="", choice=0):
		print("Book of Specters is cast and player draws three cards and discard spells drawn.")
		for i in range(3):
			card, mana = self.Game.Hand_Deck.drawCard(self.ID)
			#If a card has "cast when drawn" effect, it won't stay in hand.
			if card != None and card.cardType == "Spell" and card.inHand:
				self.Game.Hand_Deck.discardCard(self.ID, card)
		return None
		
		
class SnapFreeze(Spell):
	Class, name = "Mage", "Snap Freeze"
	needTarget, mana = True, 2
	index = "Witchwood-Mage-2-Spell-Snap Freeze"
	description = "Freeze a minion. If it's already Frozen, destroy it"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			if target.status["Frozen"]: #It's impossible for a minion in hand to be frozen when targeted by this
				print("Snap Freeze is cast and destroys the frozen minion ", target.name)
				target.dead = True
			else:
				print("Snap Freeze is cast and freezes minion ", target.name)
				target.getsFrozen()
		return target
		
		
class CinderStorm(Spell):
	Class, name = "Mage", "Cinder Storm"
	needTarget, mana = False, 3
	index = "Witchwood-Mage-3-Spell-Cinder Storm"
	description = "Deal 5 damage randomly split among all enemies"
	def whenEffective(self, target=None, comment="", choice=0):
		num = (5 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		print("Cinder Storm is cast and launches %d missiles."%num)
		for i in range(0, num):
			targets = [self.Game.heroes[3-self.ID]]
			for minion in self.Game.minionsonBoard(3-self.ID):
				if minion.health > 0:
					targets.append(minion)
					
			self.dealsDamage(np.random.choice(targets), 1)
		return None
		
		
class ArcaneKeysmith(Minion):
	Class, race, name = "Mage", "", "Arcane Keysmith"
	mana, attack, health = 4, 2, 2
	index = "Witchwood-Mage-4-2-2-Minion-None-Arcane Keysmith-Battlecry"
	needTarget, keyWord, description = False, "", "Battlecry: Discover a Secret. Put it into the battlefield"
	
	#不确定在拥有奥秘过多的情况下，是否会出现没有奥秘可以选的情况
	def whenEffective(self, target=None, comment="", choice=0):
		Class = self.Game.heroes[self.ID].Class
		if Class == "Hunter":
			secretPool = HunterSecrets
		elif Class == "Paladin":
			secretPool = PaladinSecrets
		else:
			secretPool = MageSecrets
			
		for secret in secretPool:
			if self.Game.SecretHandler.isSecretDeployedAlready(secret, self.ID):
				extractfrom(secret, secretPool)
				
		if len(secretPool) >= 3:
			card1, card2, card3 = np.random.choice(secretPool, 3, replace=False)
			card1 = self.Game.cardPool[card1](self.Game, self.ID)
			card2 = self.Game.cardPool[card2](self.Game, self.ID)
			card3 = self.Game.cardPool[card3](self.Game, self.ID)
			self.Game.options = [card1, card2, card3]
		elif len(secretPool) == 2:
			card1 = self.Game.cardPool[secretPool[0]](self.Game, self.ID)
			card2 = self.Game.cardPool[secretPool[1]](self.Game, self.ID)
			self.Game.options = [card1, card2]
		elif len(secretPool) == 1:
			self.Game.options = [self.Game.cardPool[secretPool[0]](self.Game, self.ID)]
				
		if self.Game.playerStatus[self.ID]["Battlecry Trigger Twice"] + self.Game.playerStatus[self.ID]["Shark Battlecry Trigger Twice"] > 0 and comment != "InvokedbyOthers":
			print(self.name, " is played and discovers two secrets to put into the battlefield.")
			dispatcher.connect(self.discoverDecided_Double, "DiscoverDecided", sender=self.Game)
		else:
			print(self.name, " is played and discovers a secret to put into the battlefield.")
			dispatcher.connect(self.discoverDecided, "DiscoverDecided", sender=self.Game)
			
		print("Start the discover.")
		dispatcher.send("StartDiscover", ID=self.ID, subject=self, target=None, number=0, comment="", sender=self.Game)
		
		return self, None
		
	def discoverDecided(self, subject, target):
		if subject == self:
			print("Secret ", target.name, " is put into the battlefield.")
			target.active = False
			self.Game.SecretHandler.secrets[self.ID].append(target)
			self.Game.options = []
			dispatcher.disconnect(self.discoverDecided, "DiscoverDecided", sender=self.Game)
			
class VexCrow(Minion):
	Class, race, name = "Mage", "Beast", "Vex Crow"
	mana, attack, health = 4, 3, 3
	index = "Witchwood-Mage-4-3-3-Minion-Beast-Vex Crow"
	needTarget, keyWord, description = False, "", "Whenever you cast a spell, summon a random 2-Cost minion"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_VexCrow(self)]
		
class Trigger_VexCrow(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["SpellPlayed"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject.ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("Whenever player plays a spell, %s summons a random 2-Cost minion."%self.entity.name)
		minion = np.random.choice(list(self.entity.Game.MinionswithCertainCost[2].values()))
		self.entity.Game.summonMinion(minion(self.entity.Game, self.entity.ID), self.entity.position+1, self.entity.ID)
		
		
class BonfireElemental(Minion):
	Class, race, name = "Mage", "Elemental", "Bonfire Elemental"
	mana, attack, health = 5, 5, 5
	index = "Witchwood-Mage-5-5-5-Minion-Elemental-Bonfire Elemental-Battlecry"
	needTarget, keyWord, description = False, "", "Battlecry: If you played an Elemental last turn, draw a card"
	
	def effectCanTrigger(self):
		return self.Game.CounterHandler.numElementalsPlayedLastTurn[self.ID] > 0
		
	def whenEffective(self, target=None, comment="", choice=0):
		if self.Game.CounterHandler.numElementalsPlayedLastTurn[self.ID] > 0:
			print("Bonfire Elemental's battlecry lets player draw a card.")
			self.Game.Hand_Deck.drawCard(self.ID)
		return self, None
		
class CurioCollector(Minion):
	Class, race, name = "Mage", "", "Curio Collector"
	mana, attack, health = 5, 4, 4
	index = "Witchwood-Mage-5-4-4-Minion-None-Curio Collector"
	needTarget, keyWord, description = False, "", "Whenever your draw a card, gain +1/+1"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_CurioCollector(self)]
		
class Trigger_CurioCollector(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["CardDrawn"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("Whenever player draws a card, %s gains +1/+1."%self.entity.name)
		self.entity.buffDebuff(1, 1)
		
		
class TokiTimeTinker(Minion):
	Class, race, name = "Mage", "", "Toki. Time-Tinker"
	mana, attack, health = 6, 5, 5
	index = "Witchwood-Mage-6-5-5-Minion-None-Toki. Time-Tinker-Battlecry-Legendary"
	needTarget, keyWord, description = False, "", "Battlecry: Add a random Legendary minion from the past to your hand"
	
	def whenEffective(self, target=None, comment="", choice=0):
		print("Toki. Time-Tinker's battlecry adds a Legendary minion from the past to player's hand.")
		legendary = np.random.choice(LegendaryMinionfromPast)(self.Game, self.ID)
		self.Game.Hand_Deck.addCardtoHand(legendary, self.ID)
		return self, None
	
"""Paladin cards"""
class HiddenWisdom(Secret):
	Class, name = "Hunter", "Rat Trap"
	needTarget, mana = False, 2
	index = "Witchwood-Paladin-1-Spell-Hidden Wisdom--Secret"
	description = "After your opponent plays three cards in a turn, draw 2 cards"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_HiddenWisdom(self)]
		
class Trigger_HiddenWisdom(SecretTrigger):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionBeenPlayed", "SpellBeenPlayed", "WeaponBeenPlayed", "HeroCardBeenPlayed"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.ID != self.entity.Game.turn and subject.ID != self.entity.ID and len(self.entity.Game.CounterHandler.cardsPlayedThisTurn[3-self.entity.ID]) >= 3 and self.entity.Game.spaceonBoard(self.entity.ID) > 0
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("After opponent plays three cards in a turn, Secret Hidden Wisdom is triggered and lets player draw 2 cards.")
		self.entity.Game.Hand_Deck.drawCard(self.entity.ID)
		self.entity.Game.Hand_Deck.drawCard(self.entity.ID)
		
		
class CathedralGargoyle(Minion):
	Class, race, name = "Paladin", "", "Cathedral Gargoyle"
	mana, attack, health = 2, 2, 2
	index = "Witchwood-Paladin-2-2-2-Minion-None-Cathedral Gargoyle-Battlecry"
	needTarget, keyWord, description = False, "", "Battlecry: If you're holding a Dragon, gain Taunt and Divine Shield"
	
	def effectCanTrigger(self):
		for card in self.Game.Hand_Deck.hands[self.ID]:
			if "-Dragon-" in card.index:
				return True
		return False
		
	def whenEffective(self, target=None, comment="", choice=0):
		holdingDragon = False
		for card in self.Game.Hand_Deck.hands[self.ID]:
			if "-Dragon-" in card.index:
				holdingDragon = True
				break
				
		if holdingDragon:
			print("Cathedral Gargoyle's battlecry triggers and gives the minion Divine Shield and Taunt.")
			self.keyWords["Taunt"] = 1
			self.keyWords["Divine Shield"] = 1
		return self, None
		
		
class Rebuke(Spell):
	Class, name = "Paladin", "Rebuke"
	needTarget, mana = False, 2
	index = "Witchwood-Paladin-2-Spell-Rebuke"
	description = "Enemy spells cost (5) more next turn"
	def whenEffective(self, target=None, comment="", choice=0):
		print("Rebuke is cast and enemy spells cost 5 more next turn.")
		self.Game.ManaHandler.AuraBackupList.append(SpellsCost5MoreNextTurn(self.Game.ManaHandler, 3-self.ID))
		return None
		
class SpellsCost5MoreNextTurn(TempManaEffect):
	def __init__(self, Game, ID):
		self.ID = ID
		self.Game = Game
		self.temporary = True
		self.triggersonBoard = [(self)]
		
	def handleMana(self, target):
		if target.cardType == "Spell" and target.ID == self.ID:
			target.mana += 5
			
			
class SoundtheBells(Spell):
	Class, name = "Paladin", "Sound the Bells!"
	needTarget, mana = True, 2
	index = "Witchwood-Paladin-2-Spell-Sound the Bells!-Echo"
	description = "Echo. Give a minion +1/+2"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			print("Sound the Bells! is cast, gives %s +1/+2."%target.name)
			target.buffDebuff(1, 2)
		return target
		
		
class ParagonofLight(Minion):
	Class, race, name = "Paladin", "", "Paragon of Light"
	mana, attack, health = 3, 2, 5
	index = "Witchwood-Paladin-3-2-5-Minion-None-Paragon of Light"
	needTarget, keyWord, description = False, "", "While this minion has 3 or more Attack, it has Taunt and Lifesteal"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggers["StatChanges"] = [self.handleLifestealandTaunt]
		self.activated = False
		
	def handleLifestealandTaunt(self):
		if self.silenced == False and self.onBoard:
			if self.activated == False and self.attack > 2:
				self.activated = True
				self.getsKeyword("Taunt")
				self.getsKeyword("Lifesteal")
			elif self.activated and self.attack < 3:
				self.activated = False
				self.losesKeyword("Taunt")
				self.losesKeyword("Lifesteal")
				
				
class BellringerSentry(Minion):
	Class, race, name = "Paladin", "", "Bellringer Sentry"
	mana, attack, health = 4, 3, 4
	index = "Witchwood-Paladin-4-3-4-Minion-None-Bellringer Sentry-Deathrattle-Battlecry"
	needTarget, keyWord, description = False, "", "Battlecry and Deathrattle: Put a Secret from your decks into the battlefield"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [PutaSecretfromDecktoBoard(self)]
		
	def whenEffective(self, target=None, comment="", choice=0):
		print("Bellringer Sentry's battlecry puts a secret from deck into battlefield.")
		self.Game.SecretHandler.deploySecretsfromDeck(self.ID)
		return self, None
		
class PutaSecretfromDecktoBoard(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("Deathrattle: Put a Secret from your deck into the battlefield triggers.")
		self.entity.Game.SecretHandler.deploySecretsfromDeck(self.entity.ID)
		
		
class TheGlassKnight(Minion):
	Class, race, name = "Paladin", "", "The Glass Knight"
	mana, attack, health = 4, 4, 3
	index = "Witchwood-Paladin-4-4-3-Minion-None-The Glass Knight-Divine Shield-Legendary"
	needTarget, keyWord, description = False, "Divine Shield", "Divine Shield. Whenever your restore Health, gain Divine Shield" 
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_TheGlassKnight(self)]
		
class Trigger_TheGlassKnight(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionGetsHealed", "HeroGetsHealed"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject.ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("Whenever player restores Health, %s gains Divine Shield."%self.entity.name)
		self.entity.getsKeyword("Divine Shield")
		
		
class GhostlyCharger(Minion):
	Class, race, name = "Paladin", "", "Ghostly Charger"
	mana, attack, health = 5, 3, 4
	index = "Witchwood-Paladin-5-3-4-Minion-None-Ghostly Charger-Divine Shield-Rush"
	needTarget, keyWord, description = False, "Divine Shield,Rush", "Divine Shield, Rush" 
	
	
class PrinceLiam(Minion):
	Class, race, name = "Paladin", "", "Prince Liam"
	mana, attack, health = 5, 5, 5
	index = "Witchwood-Paladin-5-5-5-Minion-None-Prince Liam-Battlecry-Legendary"
	needTarget, keyWord, description = False, "", "Battlecry: Transform all 1-Cost cards in your deck into Legendary minions" 
	
	def whenEffective(self, target=None, comment="", choice=0):
		print(self.name, " is played and transforms all 1 cost cards into random Legendary minions.")
		numCost1CardsinDeck = 0
		deckSize = len(self.Game.Hand_Deck.decks[self.ID])
		for i in range(1, deckSize+1):
			if self.Game.Hand_Deck.decks[self.ID][deckSize-i].mana_set == 1:
				self.Game.Hand_Deck.decks[self.ID].pop(deckSize-i)
				numCost1CardsinDeck += 1
				
		legendaryMinions = np.random.choice(LegendaryMinions, numCost1CardsinDeck, replace=True)
		for i in range(len(numCost1CardsinDeck)):
			minion = legendaryMinions[i](self.Game, self.ID)
			self.Game.Hand_Deck.decks[self.ID].append(minion)
			minion.entersDeck()
			
		np.random.shuffle(self.Game.Hand_Deck.decks[self.ID])
		return self, None
		
#When Silver Sword kills a minion, the buff is triggered before the deathrattle.
#The dead minion is ignored and doesn't receive buff.
class SilverSword(Weapon):
	Class, name, description = "Paladin", "Silver Sword", "After your hero attacks, give your minions +1/+1"
	mana, attack, durability = 8, 3, 4
	index = "Witchwood-Paladin-8-3-4-Weapon-Silver Sword"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_SilverSword(self)]
		
class Trigger_SilverSword(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["BattleFinished"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return subject == self.entity.Game.heroes[self.entity.ID] and self.entity.onBoard
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("After player attacks, Silver Sword gives all friendly minions +1/+1."%self.entity.name)
		for minion in self.entity.Game.minionsonBoard(self.entity.ID):
			minion.buffDebuff(1, 1)
			
"""Priest cards"""
#When shuffled into the deck, it should be Chameleos itself.
#When copied by opponent spell, the copy should Chameleos as opponent's hand.
#If Chameleos transforms into cards that transforms every turn, then Chameleos is gone, and the card becomes that new transforming card.
#Chameleos receiving buff to itself will persist, but buff to the card it transforms into will vanish.

#Chameleos transforming to another card will remove the buff added to the minion.
#Chameleos being buffed will also have no effect on the weapon, hero cards it turns into.
#变色龙在未变形时是一个手牌扳机，而在变形之后成为一个被附加了变形状态的随从，对应的扳机是
#场上扳机。入场时间点是上次变形时。
#对方没有手牌时，变色龙不会变形，已经变形的随从也会变回变色龙。假设这个变色龙会保留它是变色龙时的buff
class Chameleos(Minion):
	Class, race, name = "Priest", "Beast", "Chameleos"
	mana, attack, health = 1, 1, 1
	index = "Witchwood-Priest-1-1-1-Minion-Beast-Chameleos-Legendary"
	needTarget, keyWord, description = False, "", "Each turn this is in your hand, transform it into a card your opponent is holding"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersinHand = [Trigger_Chameleos_PreShifting(self)]
		
class Trigger_Chameleos_PreShifting(TriggerinHand):
	def __init__(self, entity):
		self.blank_init(entity, ["TurnStarts"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.inHand and ID == self.entity.ID and self.entity.Game.Hand_Deck.hands[3-self.entity.ID] != []
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		target = np.random.choice(self.entity.Game.Hand_Deck.hands[3-self.entity.ID])
		print("At the start of turn, Chameleos transforms for the first time into a copy of card %s in opponent's hand."%target.name)
		Copy = target.selfCopy(self.entity.ID)
		trigger = Trigger_Chameleos_KeepShifting(Copy, self.entity) #新的扳机保留这个变色龙的原有reference.在对方无手牌时会变回起始的变色龙。
		trigger.connect()
		Copy.triggersonBoard.append(trigger)
		#replaceCardinHand() takes care of the disconnection of this triggerinHand
		self.entity.Game.Hand_Deck.replaceCardinHand(self.entity, Copy)
		
#这个继续变形扳机需要记录变色龙初始状态的信息，当对方没有手牌时，会变回原始状态。
class Trigger_Chameleos_KeepShifting(TriggeronBoard):
	def __init__(self, entity, original):
		self.blank_init(entity, ["TurnStarts"])
		self.originalMinion = original
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		#只要回合开始就会变形，如果对方没有手牌，只不过会变形回原来的变色龙而已。
		return self.entity.inHand and ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		if self.entity.Game.Hand_Deck.hands[3-self.entity.ID] != []:
			target = np.random.choice(self.entity.Game.Hand_Deck.hands[3-self.entity.ID])
			print("At the start of turn, Chameleos transforms for the first time into a copy of card %s in opponent's hand."%target.name)
			Copy = target.selfCopy(self.entity.ID)
			#被变形成的随从的继续变形扳机是场上扳机
			trigger = Trigger_Chameleos_KeepShifting(Copy, self.originalMinion) #新的扳机保留这个变色龙的原有reference.在对方无手牌时会变回起始的变色龙。
			trigger.connect()
			Copy.triggersonBoard.append(trigger)
			self.entity.Game.Hand_Deck.replaceCardinHand(self.entity, Copy)
		else: #If the enemy hand is empty, the card shifts into the original Chameleos
			self.entity.Game.Hand_Deck.replaceCardinHand(self.entity, self.originalMinion)
			
			
class DivineHymn(Spell):
	Class, name = "Priest", "Divine Hymn"
	needTarget, mana = False, 2
	index = "Witchwood-Priest-2-Spell-Divine Hymn"
	description = "Restore 6 Health to all friendly characters"
	def whenEffective(self, target=None, comment="", choice=0):
		heal = 6 * (2 ** self.countHealDouble())
		print("Divine Hymn is cast and restores %d Health to all friendly characters."%heal)
		targets = [self.Game.heroes[self.ID]] + self.Game.minionsonBoard(self.ID)
		self.dealsAOE([], [], targets, [heal for minion in targets])
		return None
		
		
class Squashling(Spell):
	Class, race, name = "Priest", "", "Squashling"
	mana, attack, health = 2, 2, 1
	index = "Witchwood-Priest-2-2-1-Minion-None-Squashling-Battlecry-Echo"
	needTarget, keyWord, description = True, "Echo", "Echo. Battlecry: Restore 2 Health"
	
	def whenEffective(self, target=None, comment="", choice=0):
		if target!= None:
			heal = 2 * (2 ** self.countHealDouble())
			self.restoreHealth(target, heal)
			
		return self, target
		
		
class VividNightmare(Spell):
	Class, name = "Priest", "Vivid Nightmare"
	needTarget, mana = True, 3
	index = "Witchwood-Priest-3-Spell-Vivid Nightmare"
	description = "Choose a friendly minion. Summon a copy of it with 1 Health remaining"
	
	def available(self):
		return self.selectableFriendlyMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.ID == self.ID
		
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			print("Vivid Nightmare is cast and summons a copy with 1 health of target ", target.name)
			Copy = target.selfCopy(self.ID)
			Copy.health = 1
			self.Game.summonMinion(Copy, target.position+1, self.ID)
		return target
		
		
class HolyWater(Spell):
	Class, name = "Priest", "Holy Water"
	needTarget, mana = True, 5
	index = "Witchwood-Priest-5-Spell-Holy Water"
	description = "Deal 4 damage to a minion. If that kills it, add a copy of it to your hand"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			damage = (4 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			print("Holy Water is cast and deals 4 damage to ", target.name)
			if self.dealsDamage(target, damage)[1] > 1:
				print("Holy Water kills the target and adds a copy of it to player's hand.")
				self.Game.Hand_Deck.addCardtoHand(type(target)(self.Game, self.ID), self.ID)
		return target
		
		
class QuartzElemental(Minion):
	Class, race, name = "Priest", "Elemental", "Quartz Elemental"
	mana, attack, health = 5, 5, 8
	index = "Witchwood-Priest-5-5-8-Minion-Elemental-Quartz Elemental"
	needTarget, keyWord, description = False, "", "Can't attack while damaged"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggers["StatChanges"] = [self.handleEnrage]
		self.activated = False
		
	def handleEnrage(self):
		if self.silenced == False and self.onBoard:
			if self.activated == False and self.health < self.health_upper:
				self.activated = True
				self.marks["Can't Attack"] += 1
			elif self.activated and self.health >= self.health_upper:
				self.activated = False
				self.marks["Can't Attack"] -= 1
				
				
class CoffinCrasher(Minion):
	Class, race, name = "Priest", "", "Coffin Crasher"
	mana, attack, health = 6, 6, 5
	index = "Witchwood-Priest-6-6-5-Minion-None-Coffin Crasher-Deathrattle"
	needTarget, keyWord, description = False, "", "Deathrattle: Summon a Deathrattle minion from your hand"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [SummonaDeathrattleMinionfromHand(self)]
		
class SummonaDeathrattleMinionfromHand(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("Deathrattle: Summon a Deathrattle minion from your hand triggers.")
		deathrattleMinionsinHand = []
		for card in self.entity.Game.Hand_Deck.hands[self.entity.ID]:
			if card.cardType == "Minion" and card.deathrattles != []:
				deathrattleMinionsinHand.append(card)
				
		if deathrattleMinionsinHand != []:
			self.entity.Game.summonfromHand(np.random.choice(deathrattleMinionsinHand), self.entity.position+1, self.entity.ID)
			
			
class LadyinWhite(Minion):
	Class, race, name = "Priest", "", "Lady in White"
	mana, attack, health = 6, 5, 5
	index = "Witchwood-Priest-6-5-5-Minion-None-Lady in White-Battlecry-Legendary"
	needTarget, keyWord, description = False, "", "Battlecry: Cast 'Inner Fire' on every minion in your deck(set Attack equal to Health)"
	
	def whenEffective(self, target=None, comment="", choice=0):
		print(self.name, " is played and sets all minions' attack to health in deck")
		for card in self.Game.Hand_Deck.decks[self.ID]:
			if card.cardType == "Minion":
				card.statReset(card.health_upper, False) #Set attack equal to health.
		return self, None
		
		
class NightscaleMatriarch(Minion):
	Class, race, name = "Priest", "Dragon", "Nightscale Matriarch"
	mana, attack, health = 7, 4, 9
	index = "Witchwood-Priest-7-4-9-Minion-Dragon-Nightscale Matriarch"
	needTarget, keyWord, description = False, "", "Whenever a friendly minion is healed, summon a 3/3 Whelp"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_NightscaleMatriarch(self)]
		
class Trigger_NightscaleMatriarch(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionGetsHealed"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and target.ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("Whenever a friendly minion is healed, %s summons a 3/3 Whelp."%self.entity.name)
		self.entity.Game.summonMinion(NightscaleWhelp(self.entity.Game, self.entity.ID), self.entity.position+1, self.entity.ID)
		
class NightscaleWhelp(Minion):
	Class, race, name = "Priest", "Dragon", "Nightscale Whelp"
	mana, attack, health = 3, 3, 3
	index = "Witchwood-Priest-3-3-3-Minion-Dragon-Nightscale Whelp-Uncollectible"
	needTarget, keyWord, description = False, "", ""
	
"""Rogue cards"""
class CheapShot(Spell):
	Class, name = "Rogue", "Cheap Shot"
	needTarget, mana = True, 2
	index = "Witchwood-Rogue-2-Spell-Cheap Shot-Echo"
	description = "Echo. Deal 2 damage to a minion"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			damage = (2 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			print("Cheap Shot is cast and deals %d damage to minion "%damage, target.name)
			self.dealsDamage(target, damage)
		return target
		
		
class PickPocket(Minion):
	Class, name = "Rogue", "Pick Pocket"
	needTarget, mana = False, 2
	index = "Witchwood-Rogue-2-Spell-Pick Pocket-Echo"
	description = "Echo. Add a random card to your hand(from your opponent's class)"
	def whenEffective(self, target=None, comment="", choice=0):
		Class = self.Game.heroes[3-self.ID].Class
		print("Pick Pocket is cast and adds a random card from %s class into player's hand."%Class)
		card = np.random.choice(list(self.Game.ClassCards[Class].values()))(self.Game, self.ID)
		self.Game.Hand_Deck.addCardtoHand(card, self.ID)
		return None
		
		
class BlinkFox(Minion):
	mana, attack, health = 3, 3, 3
	Class, race, name = "Rogue", "Beast", "Blink Fox"
	index = "Witchwood-Rogue-3-3-3-Minion-Beast-Blink Fox-Battlecry"
	needTarget, keyWord, description = False, "", "Battlecry: Add a random card to your hand (from your opponent's class)"
	
	def whenEffective(self, target=None, comment="", choice=0):
		if self.Game.Hand_Deck.handNotFull(self.ID):
			cards = list(self.Game.ClassCards[self.Game.heroes[3-self.ID].Class].values())
			print("Blink Fox's battlecry adds a random card from opponent's class to player's hand.")
			self.Game.Hand_Deck.addCardtoHand(np.random.choice(cards), self.ID, "CreateUsingType")
		return self, None
		
		
class CutthroatBuccaneer(Minion):
	Class, race, name = "Rogue", "Pirate", "Cutthroat Buccaneer"
	mana, attack, health = 3, 2, 4
	index = "Witchwood-Rogue-3-2-4-Minion-Pirate-Cutthroat Buccaneer-Combo"
	needTarget, keyWord, description = False, "", "Combo: Give your weapon +1 Attack"
	
	def effectCanTrigger(self):
		return self.Game.CounterHandler.cardsPlayedThisTurn[self.ID] != []
		
	def whenEffective(self, target=None, comment="", choice=0):
		if self.self.Game.CounterHandler.cardsPlayedThisTurn[self.ID] != []:
			weapon = self.Game.availableWeapon(self.ID)
			if weapon != None:
				print("Cutthroat Buccaneer's Combo triggers and gives player's weapon +1 attack.")
				weapon.gainStat(1, 0)
		return self, None
		
		
class FaceCollector(Minion):
	Class, race, name = "Rogue", "", "Face Collector"
	mana, attack, health = 3, 2, 2
	index = "Witchwood-Rogue-3-2-2-Minion-None-Face Collector-Battlecry-Echo-Legendary"
	needTarget, keyWord, description = False, "Echo", "Echo: Battlecry: Add a random Legendary minion to your hand"
	
	def whenEffective(self, target=None, comment="", choice=0):
		if self.Game.Hand_Deck.handNotFull(self.ID):
			print("Face Collector's battlecry adds a random Legendary minion to player's hand.")
			card = np.random.choice(list(LegendaryMinions.values()))
			self.Game.Hand_Deck.addCardtoHand(card, self.ID, "CreateUsingType")
		return self, None
		
		
class MistWraith(Minion):
	Class, race, name = "Rogue", "", "Mist Wraith"
	mana, attack, health = 4, 3, 5
	index = "Witchwood-Rogue-4-3-5-Minion-None-Mist Wraith"
	needTarget, keyWord, description = False, "", "Whenever you player an Echo card, gain +1/+1"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_MistWraith(self)]
		
class Trigger_MistWraith(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionPlayed", "SpellPlayed"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		if self.entity.onBoard and subject.ID == self.entity.ID:
			if subject.cardType == "Minion" and subject.keyWords["Echo"] > 0:
				return True
			if subject.carType == "Spell" and "-Echo" in subject.index:
				return True
		return False
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("Whenever player plays a card with Echo, %s gains +1/+1."%self.entity.name)
		self.entity.buffDebuff(1, 1)
		
		
class SpectralCutlass(Weapon):
	Class, name, description = "Rogue", "Spectral Cutlass", "Whenever you play a card from another class, gain +1 Durability"
	mana, attack, durability = 4, 2, 2
	index = "Witchwood-Rogue-4-2-2-Weapon-Spectral Cutlass-Lifesteal"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_SpectralCutlass(self)]
		self.keyWords["Lifesteal"] = 1
		
class Trigger_SpectralCutlass(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionPlayed", "SpellPlayed", "WeaponPlayed", "HeroCardPlayed"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return subject.ID == self.entity.ID and subject.Class != self.entity.Game.heroes[self.entity.ID].Class and self.entity.onBoard
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("Player plays a card from another class, %s gains +1 Durability."%self.entity.name)
		self.entity.gainStat(0, 1)
		
		
class WANTED(Spell):
	Class, name = "Rogue", "WANTED!"
	needTarget, mana = True, 4
	index = "Witchwood-Rogue-4-Spell-WANTED!"
	description = "Deal 3 damage to a minion. If that kills it, add a Coin to your hand"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			damage = (3 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			print("WANTED! is cast and deals %d damage to minion "%damage, target.name)
			if self.dealsDamage(target, damage) > 1:
				print("WANTED! kills the target minion and adds a Coin to player's hand.")
				self.Game.Hand_Deck.addCardtoHand(TheCoin(self.Game, self.ID), self.ID)
		return target
		
		
class CursedCastaway(Minion):
	Class, race, name = "Rogue", "Pirate", "Cursed Castaway"
	mana, attack, health = 6, 5, 3
	index = "Witchwood-Rogue-6-5-3-Minion-Pirate-Cursed Castaway-Rush-Deathrattle"
	needTarget, keyWord, description = False, "Rush", "Rush. Deathrattle: Draw a Combo card from your deck"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [DrawaComboCard(self)]
		
class DrawaComboCard(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		comboCardsinDeck = []
		for card in self.entity.Game.Hand_Deck.decks[self.entity.ID]:
			if "-Combo" in card.index:
				comboCardsinDeck.append(card)
		if comboCardsinDeck != []:
			print("Deathrattle: Draw a Combo card from your deck triggers.")
			self.entity.Game.Hand_Deck.drawCard(self.entity.ID, np.random.choice(comboCardsinDeck))
			
			
class TessGreymane(Minion):
	Class, race, name = "Rogue", "", "Tess Greymane"
	mana, attack, health = 3, 6, 6
	index = "Witchwood-Rogue-8-6-6-Minion-None-Tess Greymane-Battlecry-Legendary"
	needTarget, keyWord, description = False, "", "Battlecry: Replay every card from another class you've played this game(targets chosen randomly)"
	def whenEffective(self, target=None, comment="", choice=0):
		cardstoReplay = {1:{"Druid": [], "Hunter": [], "Mage": [],	"Paladin": [], "Priest": [],
								"Rogue": [], "Shaman": [], "Warlock": [], "Warrior": []},
							2: {"Druid": [], "Hunter": [], "Mage": [],	"Paladin": [], "Priest": [],
								"Rogue": [], "Shaman": [], "Warlock": [], "Warrior": []}
							}
		#应该是每当打出一张卡后将index从原有列表中移除。
		for ID in range(1, 3):
			for index in self.Game.CounterHandler.cardsPlayedThisGame[ID]:
				if "Neutral" not in index:
					cardstoReplay[ID][index.split("-")[1]].append(index)
			for key in cardstoReplay[ID].keys():
				np.random.shuffle(cardstoReplay[ID][key])
				
		HeroClass, HeroID, replayList = self.Game.heroes[self.ID].Class, self.ID, []
		for key in cardstoReplay[HeroID].keys():
			if key != HeroClass:
				replayList += cardstoReplay[HeroID][HeroClass]
				
		print("Tess Greymane's battlecry starts replaying cards from another class player played this game.")
		while replayList != []:
			#If the class the hero or Tess Greymane's control is changed, then will refresh the replayList
			if HeroClass != self.Game.heroes[self.ID].Class or HeroID != self.ID:
				HeroClass, HeroID, replayList = self.Game.heroes[self.ID].Class, self.ID, []
				for key in cardstoReplay[HeroID].keys():
					if key != HeroClass:
						replayList += cardstoReplay[HeroID][HeroClass]
						
			index = replayList.pop(0)
			card = self.Game.cardPool[index](self.Game, self.ID)
			extractfrom(index, cardstoReplay[card.Class])
			if card.cardType == "Minion":
				print("Tess Greymane's battlecry summons minion ", card.name)
				self.Game.summonMinion(card, self.position+1, self.ID)
			elif card.cardType == "Spell":
				print("Tess Greymane's battlecry casts spell( at random target) ", card.name)
				card.cast(None, "CastbyOthers")
			elif card.cardType == "Weapon":
				print("Tess Greymane's battlecry lets player equip weapon ", card.name)
				self.Game.equipWeapon(card)
			else: #Hero cards. And the HeroClass will change accordingly
				#Replaying Hero Cards can only replace your hero and Hero Power, no battlecry will be triggered
				print("Tess Greymane's battlecry replaces player's hero with", card.name)
				card.replaceHero()
				
		return minion, None
		
"""Shaman cards"""
class Zap(Spell):
	Class, name = "Shaman", "Zap!"
	needTarget, mana = True, 0
	index = "Witchwood-Shaman-0-Spell-Zap!-Overload"
	description = "Deal 2 damage to a minion. Overload: (1)"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.overload = 1
		
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			damage = (2 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			print("Zap! is cast and deals %d damage to "%damage, target.name)
			self.dealsDamage(target, damage)
		return target
		
		
class BlazingInvocation(Spell):
	Class, name = "Shaman", "Blazing Invocation"
	needTarget, mana = False, 1
	index = "Witchwood-Shaman-1-Spell-Blazing Invocation"
	description = "Discover a Battlecry minion"
	def whenEffective(self, target=None, comment="", choice=0):
		if self.Game.Hand_Deck.handNotFull(self.ID):
			Class = self.Game.heroes[self.ID].Class if self.Game.heroes[self.ID].Class != "Neutral" else self.Class
			for key, value in self.Game.ClassCards[Class].items():
				if "-Minion-" in key and "-Battlecry" in key:#if "Branching" in comment:
					battlecryMinions.append(value)#	index = str(comment.split('-')[1])
			for key, value in self.Game.NeutralMinions.items():#	self.discoverDecided(self.Game.options[index])
				if "-Battlecry" in key:
					battlecryMinions.append(value)
					
			if comment == "CastbyOthers": #Cast by Cards like Yogg Saron
				print("Blazing Invocation is cast and adds a random Battlecry minion to player's hand")
				self.Game.Hand_Deck.addCardtoHand(np.random.choice(battlecryMinions), self.ID, "CreateUsingType")
			else:
				minions = np.random.choice(battlecryMinions, 3, replace=False)
				self.Game.options = [minion(self.Game, self.ID) for minion in minions]
				self.Game.DiscoverHanler.startDiscover(self)
				
		return None
			#	battlecryMinions = []
			#	for key, value in self.Game.ClassCards[self.Game.heroes[self.ID].Class].items():
			#		if "-Minion-" in key and "-Battlecry" in key:
			#			battlecryMinions.append(value)
			#	for key, value in self.Game.NeutralMinions.items():
			#		if "-Minion-" in key and "-Battlecry" in key:
			#			battlecryMinions.append(value)
			#			
			#	if comment == "CastbyOthers": #Cast by Cards like Yogg Saron
			#		print("Blazing Invocation is cast and adds a random Battlecry minion to player's hand")
			#		self.Game.Hand_Deck.addCardtoHand(np.random.choice(battlecryMinions), self.ID, "CreateUsingType")
			#	else:
			#		minions = np.random.choice(battlecryMinions, 3, replace=False)
			#		self.Game.options = [minion(self.Game, self.ID) for minion in minions]
			#		if comment == "InvokedbyAI": #with branchGames storing the 3 branch game
			#			#AI玩家的本体Game被保留，用于根据发现选项个数复制新的游戏.本体Game产生被复制得到stemGame,然后stemGame中的法术被施放，推演至此。
			#			#正常情况下分出3个发现选项。根据选项数量，复制相应个数的branchingGame
			#			#当前法术属于的游戏的玩家自带了一个尚未打出这张牌的游戏，应该去复制那个游戏，并以不同选项直接释放那个法术
			#			player = self.Game.player[self.ID]
			#			scores = [] #用于记录各个不同选项的评分
			#			for i in range(len(self.Game.options)):
			#				#推演到此处的Game是从玩家的本体Game中复制出的stemGame，即self.Game
			#				#而新的branchGame需要从AI玩家的本体Game中复制得到
			#				branchGame = copy.deepcopy(self.Game)
			#				sub_branch = player.findCopiedObject_inCopiedGame(player.Game, player.Game.subject, branchGame)
			#				target_branch = player.findCopiedObject_inCopiedGame(player.Game, player.Game.target, branchGame)
			#				comment = "Branching-"+str(i) #之后branchGame中被调用的函数会直接使用这个给出的选项
			#				branchGame.playSpell(sub_branch, target_branch, choice, comment)
			#				#player.option_all AI玩家返回所有无随机结果，
			#				#AI玩家对于这个评分，打到最高的分数
			#				scores.append(score)
			#			#根据分数最高的选取发现选项
			#			self.discoverDecided(self.Game.options[i])
			#		else: #Played with GUI. Enter the discover option using terminal
			#			self.Game.DiscoverHanler.startDiscover(self)
			
	def discoverDecided(self, option):
		print("Blazing Invocation adds battlecry minion %s to player's hand."%option.name)
		self.Game.Hand_Deck.addCardtoHand(option, self.ID)
		
		
class WitchsApprentice(Minion):
	Class, race, name = "Shaman", "Beast", "Witch's Apprentice"
	mana, attack, health = 1, 0, 1
	index = "Witchwood-Shaman-1-0-1-Minion-Beast-Witch's Apprentice-Battlecry-Taunt"
	needTarget, keyWord, description = False, "Taunt", "Taunt. Battlecry: Add a random Shaman spell to your hand"
	
	def whenEffective(self, target=None, comment="", choice=0):
		print("Witch's Apprentice's battlecry adds a Shaman spell to player's hand.")
		shamanSpells = []
		for key, value in self.Game.ClassCards["Shaman"].values():
			if "-Spell-" in key:
				shamanSpells.append(value)
				
		self.Game.Hand_Deck.addCardtoHand(np.random.choice(shamanSpells), self.ID, "CreateUsingType")
		return self, None
		
		
class EarthenMight(Spell):
	Class, name = "Shaman", "Earthen Might"
	needTarget, mana = True, 2
	index = "Witchwood-Shaman-2-Spell-Earthen Might"
	description = "Give a minion +2/+2. If it's an Elemental, add a random Elemental to your hand"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			print("Earthen Might is cast and gives minion %s +2/+2."%target.name)
			target.buffDebuff(2, 2)
			if "Elemental" in target.race:
				print("The target is an Elemental, and Earthen Might adds a random Elemental card to player's hand.")
				minion = np.random.choice(self.Game.MinionswithRace["Elemental"].values())
				self.Game.Hand_Deck.addCardtoHand(minion, self.ID, "CreateUsingType")
		return target
		
		
class GhostLightAngler(Minion):
	Class, race, name = "Shaman", "Murloc", "Ghost Light Angler"
	mana, attack, health = 1, 0, 1
	index = "Witchwood-Shaman-2-2-2-Minion-Murloc-Ghost Light Angler-Echo"
	needTarget, keyWord, description = False, "Echo", "Echo"
	
	
class TotemCruncher(Minion):
	Class, race, name = "Shaman", "Beast", "Totem Cruncher"
	mana, attack, health = 4, 2, 3
	index = "Witchwood-Shaman-4-2-3-Minion-Beast-Totem Cruncher-Battlecry-Taunt"
	needTarget, keyWord, description = False, "Taunt", "Taunt. Battlecry: Destroy your Totems. Gain +2/+2 for each destroyed"
	
	def whenEffective(self, target=None, comment="", choice=0):
		totems = []
		for minion in self.Game.minions[self.ID]:
			if "-Totem-" in minion.index:
				totems.append(minion)
				
		if totems != []:
			num = len(totems)
			self.Game.AOEDestroy(self, totems)
			if self.Game.playerStatus[self.ID]["Battlecry Trigger Twice"] + self.Game.playerStatus[self.ID]["Shark Battlecry Trigger Twice"] > 0 and comment != "InvokedbyOthers":
				print(self.name, " is played, destroys all friendly totems and gains +4/+4 for each.")
				self.buffDebuff(4 * num, 4 * num)
			else:
				print(self.name, " is played, destroys all friendly totems and gains +2/+2 for each.")
				self.buffDebuff(2 * num, 2 * num)
		return self, None
		
		
class Bogshaper(Minion):
	Class, race, name = "Shaman", "Elemental", "Bogshaper"
	mana, attack, health = 7, 4, 8
	index = "Witchwood-Shaman-7-4-8-Minion-Elemental-Bogshaper"
	needTarget, keyWord, description = False, "", "Whenever you cast a spell, draw a minion from your deck"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_Bogshaper(self)]
		
class Trigger_Bogshaper(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["SpellPlayed"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject.ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("Player cast a spell and %s lets player draw a minion from deck."%self.entity.name)
		minionsinDeck = []
		for card in self.entity.Game.Hand_Deck.decks[self.entity.ID]:
			if card.cardType == "Minion":
				minionsinDeck.append(card)
				
		if minionsinDeck != []:
			print(self.name, " lets player draw a minion from deck whenever he plays a spell.")
			self.entity.Game.Hand_Deck.drawCard(self.entity.ID, np.random.choice(minionsinDeck))
			
			
class Bewitch(HeroPower):
	name, needTarget = "Bewitch", False
	index = "Shaman-0-Hero Power-Bewitch"
	description = "Passive Hero Power. After your play a minion, add a random Shaman spell to your hand"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_Bewitch(self)]
		
	def available(self, choice=0):
		return False
		
	def use(self, target=None, choice=0):
		return 0
		
	def appears(self):
		for trigger in self.triggersonBoard:
			trigger.connect() #把(obj, signal)放入Game.triggersonBoard 中
			
		shamanSpells =[]
		for key, value in self.Game.ClassCards["Shaman"].items():
			if "-Spell-" in key:
				shamanSpells.append(value)
		self.shamanSpells = shamanSpells
		self.Game.sendSignal("HeroPowerAcquired", self.ID, self, None, 0, "")
		
	def disappears(self):
		for trigger in self.triggersonBoard:
			trigger.disconnect()
			
class Trigger_Bewitch(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionBeenPlayed"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return subject.ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("A friendly minion %s is played and Hero Power Bewitch adds a random shaman spell to player's hand."%subject.name)
		self.entity.Game.Hand_Deck.addCardtoHand(np.random.choice(self.entity.shamanSpells), self.entity.ID, "CreateUsingType")
		
class HagathatheWitch(Hero):
	mana, description = 8, "Battlecry: Deal 3 damage to all minions"
	Class, name, heroPower, armor = "Shaman", "Hagatha the Witch", Bewitch, 5
	index = "Witchwood-Shaman-8-Hero Card-Hagatha the Witch-Battlecry-Legendary"
	def whenEffective(self, target=None, comment="", choice=0):
		print("Hagatha the Witch's battlecry deals 3 damage to all minions.")
		targets = self.Game.minionsonBoard(1) + self.Game.minionsonBoard(2)
		self.dealsAOE(targets, [3 for obj in targets])
		return self, None
		
		
class Shudderwock(Minion):
	Class, race, name = "Shaman", "", "Shudderwock"
	mana, attack, health = 2, 6, 6
	index = "Witchwood-Shaman-9-6-6-Minion-None-Shudderwock-Battlecry-Legendary"
	needTarget, keyWord, description = False, "", "Battlecry: Repeat all other Battlecries from cards your played this game(targets chosen randomly)"
	
	def whenEffective(self, target=None, comment="", choice=0):
		IDwhenPlayed = self.ID
		battlecryDict = {1:[], 2:[]}
		for ID in range(1, 3):
			for cardIndex in self.Game.CounterHandler.cardsPlayedThisGame[ID]:
				#Shudderwock will not repeat other Shudderwock's battlecries.
				if "-Minion-" in cardIndex and "-Battlecry" in cardIndex and "-Shudderwock-" not in cardIndex:
					battlecryDict[ID].append(cardIndex)
					
		if battlecryDict[IDwhenPlayed] != []:
			np.random.shuffle(battlecryDict[1])
			np.random.shuffle(battlecryDict[2])
			i = 0 #Can only repeat 30 battlecries at most.
			while True:
				#If Shudderwock leaves board, gets Silenced/Destroyed/Transformed, the battlecry will stop.
				if self.silenced or self.health <= 0 or self.dead or self.onBoard == False or self != minion:
					print("Shudderwock is Silenced/Destroyed/Transformed/Leaves Board and stops it battlecry.")
					break
				#Need instantiated object to acquire targets.
				#Need reference to Class to invoke methods using Shudderwock's own parameters.
				minion_obj = self.Game.cardPool[battlecryDict[self.ID][0]](self.Game, self.ID)
				print("Now repeating the battlecry of ", minion_obj.name)
				minion_type = self.Game.cardPool[battlecryDict[self.ID][0]]
				if minion_obj.needTarget(): #随从的战吼需要目标
					targets = minion_obj.returnTargets(comment="IgnoreStealthandImmune")
					extractfrom(self, targets)
					if targets != []:
						#If we invoke minion_type.returnTargets(self, comment), the correct target will be Shudderwock's own targetCorrect() method.
						print("The targets for %s's battlecry are:"%minion_obj.name)
						for target in targets:
							print(target.name)
						target = np.random.choice(targets)
						#All battlecries must be written so that Shudderwock Class doesn't need to access other minions' nonuniversal parameters.
						minion, target = minion_type.whenEffective(self, target, comment="InvokedbyOthers")
						self.Game.gathertheDead()
				else: #战吼不需要目标
					minion, target = minion_type.whenEffective(self, None, comment="InvokedbyOthers")
					self.Game.gathertheDead()
					
				battlecryDict[self.ID].pop(0)
				i += 1
				if battlecryDict[self.ID] == [] or i >= 30:
					print("Shudderwock has finished repeating the battlecries of player's minions.")
					break
					
		return minion, None
		
"""Warlock card"""
class DarkPossession(Spell):
	Class, name = "Warlock", "Dard Possession"
	needTarget, mana = True, 1
	index = "Witchwood-Warlock-1-Spell-Dark Possession"
	description = "Deal 2 damage to a friendly character. Discover a Demon"
	def available(self):
		return self.selectableFriendlyExists()
		
	def targetCorrect(self, target, choice=0):
		return (target.cardType == "Minion" or target.cardType == "Hero") and target.ID == self.ID and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0):
		if target != None:
			damage = (2 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			print("Dark Possession is cast and deals %d damage to "%damage, target.name)
			self.dealsDamage(target, damage)
			if self.Game.Hand_Deck.handNotFull(self.ID):
				Class = self.Game.heroes[self.ID].Class if self.Game.heroes[self.ID].Class != "Neutral" else self.Class
				if Class == "Warlock":
					demons = list(self.Game.MinionswithRace["Demon"].values())
				else:
					demons = []
					for key, value in self.Game.MinionswithRace["Demon"].items():
						if "-Neutral-" in key:
							demons.append(value)
							
				if comment == "CastbyOthers":
					print("Dark Possession adds a random Demon to player's hand")
					self.Game.Hand_Deck.addCardtoHand(np.random.choice(demons), self.ID, "CreateUsingType")
				else:
					print("Dark Possession lets player discover a Demon.")
					self.Game.options = [demon(self.Game, self.ID) for demon in demons]
					self.Game.DiscoverHanler.startDiscover(self)
		return target
		
	def discoverDecided(self, option):
		print("Dark Possession adds Demon %s to player's hand."%option.name)
		self.Game.Hand_Deck.addCardtoHand(option, self.ID)
		
		
class WitchwoodImp(Minion):
	Class, race, name = "Warlock", "", "Witchwood Imp"
	mana, attack, health = 1, 1, 1
	index = "Witchwood-Warlock-1-1-1-Minion-Demon-Witchwood Imp-Deathrattle"
	needTarget, keyWord, description = False, "Stealth", "Stealth. Deathrattle: Give a random friendly minion +2 Health"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [GiveaRamdomFriendlyPlus2Health(self)]
		
class GiveaRamdomFriendlyPlus2Health(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("Deathrattle: Give a random friendly minion +2 Health triggers.")
		friendlyMinions = self.entity.Game.minionsonBoard(self.entity.ID)
		if friendlyMinions != []:
			np.random.choice(friendlyMinions).buffDebuff(0, 2)
			
			
class CurseofWeakness(Spell):
	Class, name = "Warlock", "Curse of Weakness"
	needTarget, mana = False, 2
	index = "Witchwood-Warlock-2-Spell-Curse of Weakness-Echo"
	description = "Give all enemy minions -2 Attack until your next turn"
	def whenEffective(self, target=None, comment="", choice=0):
		print(self.name, " is cast and reduces enemy minions' attack by 2 until player's next turn.")		
		for minion in self.Game.minions[3-self.ID]:
			minion.buffDebuff(-2, 0, "StartofTurn %d"%self.ID)
		return None
		
		
class Duskbat(Minion):
	Class, race, name = "Warlock", "Beast", "Duskbat"
	mana, attack, health = 3, 2, 4
	index = "Witchwood-Warlock-3-2-4-Minion-Beast-Duskbat-Battlecry"
	needTarget, keyWord, description = False, "", "Battlecry: If your hero took damage this turn, summon two 1/1 Bats"
	
	def effectCanTrigger(self):
		return self.Game.playerStatus[self.ID]["Damage Taken This Turn"] > 0
		
	def whenEffective(self, target=None, comment="", choice=0):
		if self.Game.playerStatus[self.ID]["Damage Taken This Turn"] > 0:
			print("Duskbat's battlecry summons two 1/1 Bats.")
			pos = (self.position, "leftandRight") if self.onBoard else (-1, "totheRightEnd")
			self.Game.summonMinion([Bat(self.Game, self.ID) for i in range(2)], pos, self.ID)
		return self, None
		
class Bat(Minion):
	Class, race, name = "Warlock", "Beast", "Bat"
	mana, attack, health = 1, 1, 1
	index = "Witchwood-Warlock-1-1-1-Minion-Beast-Bat-Uncollectible"
	needTarget, keyWord, description = False, "", ""
	
	
class Ratcatcher(Minion):
	Class, race, name = "Warlock", "", "Ratcatcher"
	mana, attack, health = 3, 2, 2
	index = "Witchwood-Warlock-3-2-2-Minion-None-Ratcatcher-Battlecry-Rush"
	needTarget, keyWord, description = True, "Rush", "Rush. Battlecry: Destroy a friendly minoin and gain its Attack and Health"
	
	def targetExists(self, choice=0):
		return self.selectableFriendlyMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.ID == self.ID and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0):
		if target!= None:
			print("Ratcatcher's battlecry destroys friendly minion %s and lets minion its stat."%target.name)
			attack = max(target.attack, 0)
			health = max(target.health, 0)
			target.dead = True
			self.buffDebuff(attack, health)
		return self, target
		
		
class FiendishCircle(Spell):
	Class, name = "Warlock", "Fiendish Circle"
	needTarget, mana = False, 4
	index = "Witchwood-Warlock-4-Spell-Fiendish Circle"
	description = "Summon four 1/1 Imps"
	
	def whenEffective(self, target=None, comment="", choice=0):
		print("Fiendish Circle is cast and summons four 1/1 Imps")
		self.Game.summonMinion([Imp(self.Game, self.ID) for i in range(4)], (-1, "totheRightEnd"), self.ID)
		return None
		
class Imp_Witchwood(Minion):
	Class, race, name = "Warlock", "Demon", "Imp"
	mana, attack, health = 1, 1, 1
	index = "Witchwood-Warlock-1-1-1-Minion-Demon-Imp Witchwood-Uncollectible"
	needTarget, keyWord, description = False, "", ""
	
	
class BloodWitch(Minion):
	Class, race, name = "Warlock", "", "Blood Witch"
	mana, attack, health = 4, 3, 6
	index = "Witchwood-Warlock-4-3-6-Minion-None-Blood Witch"
	needTarget, keyWord, description = False, "", "At the start of your turn, deal 1 damage to your hero"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_BloodWitch(self)]
		
class Trigger_BloodWitch(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["TurnStarts"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("At the start of turn, Blood Witch deals 1 damage to player.")
		self.entity.dealsDamage(self.entity.Game.heroes[self.entity.ID], 1)
		
		
class DeathwebSpider(Minion):
	Class, race, name = "Warlock", "Beast", "Deathweb Spider"
	mana, attack, health = 5, 4, 6
	index = "Witchwood-Warlock-5-4-6-Minion-Beast-Deathweb Spider-Battlecry"
	needTarget, keyWord, description = False, "", "Battlecry: If your hero took damage this turn, gain Lifesteal"
	def effectCanTrigger(self):
		return self.Game.playerStatus[self.ID]["Damage Taken This Turn"] > 0
		
	def whenEffective(self, target=None, comment="", choice=0):
		if self.Game.playerStatus[self.ID]["Damage Taken This Turn"] > 0:
			print("Deathweb Spider's battlecry gives minion Lifesteal since player has taken damage this turn.")
			self.getsKeyword("Lifesteal")
		return self, None
		
		
class GlindaCrowskin(Minion):
	Class, race, name = "Warlock", "", "Glinda Crowskin"
	mana, attack, health = 6, 3, 7
	index = "Witchwood-Warlock-6-3-7-Minion-None-Glinda Crowskin-Legendary"
	needTarget, keyWord, description = False, "", "Minions in your hand have Echo"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_GlindaCrowskin(self)]
		self.appearResponse = [self.activateAura]
		self.disappearResponse = [self.deactivateAura]
		self.silenceResponse = [self.deactivateAura]
		
	def activateAura(self):
		print("Glinda Crowskin's aura appears and player's minions now have Echo.")
		for card in self.Game.Hand_Deck.decks[self.ID]:
			if card.cardType == "Minion":
				card.keyWords["Echo"] += 1
				
	def deactivateAura(self):
		print("Glinda Crowskin's aura is removed and player's minions no longer have Echo.")
		for card in self.Game.Hand_Deck.decks[self.ID]:
			if card.cardType == "Minion":
				if card.keyWords["Echo"] > 0:
					card.keyWords["Echo"] -= 1
					
class Trigger_GlindaCrowskin(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["CardEntersHand"])
		
	#target is the card added to hand
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.inHand and target.ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("Glinda Crowskin gives minion %s in player's hand Echo"%target.name)
		target.keyWords["Echo"] += 1
		
		
#Cycles up to 14 times. Can go up to 28 times when there is Bronzebeard, even if Bronzebeard gets killed half way.
class LordGodfrey(Minion):
	Class, race, name = "Warlock", "", "Lord Godfrey"
	mana, attack, health = 7, 4, 4
	index = "Witchwood-Warlock-7-4-4-Minion-None-Lord Godfrey-Battlecry-Legendary"
	needTarget, keyWord, description = False, "", "Battlecry: Deal 2 damage to all other minions. If any dies, repeat this Battlecry"
	
	def whenEffective(self, target=None, comment="", choice=0):
		print("Lord Godfrey's battlecry deals 2 damage to all other minions. If minions are killed, repeat it.")
		for i in range(14):
			AOEkilledMinions = False
			targets = self.Game.minionsonBoard(1) + self.Game.minionsonBoard(2)
			extractfrom(self, targets)
			targets_damaged, damagesActual, targets_Healed, healsActual, totalDamageDone, totalHealingDone, damageSurvivals = self.dealsDamage(targets, [2 for minion in targets])
			for survival in damageSurvivals:
				if survival > 1:
					AOEkilledMinions
					break
			self.Game.gathertheDead()
			if AOEkilledMinions == False:
				break
				
		return self, None
		
"""Warrior cards"""
class TownCrier(Minion):
	Class, race, name = "Warrior", "", "Town Crier"
	mana, attack, health = 1, 1, 2
	index = "Witchwood-Warrior-1-1-2-Minion-None-Town Crier-Battlecry"
	needTarget, keyWord, description = False, "", "Battlecry: Draw a Rush minion from your deck"
	
	def whenEffective(self, target=None, comment="", choice=0):
		print("Town Crier's battlecry lets player draw a Rush minion from deck.")
		rushMinionsinDeck = []
		for card in self.Game.Hand_Deck.decks[self.ID]:
			if card.cardType == "Minion" and "-Rush" in card.index:
				rushMinionsinDeck.append(card)
				
		if rushMinionsinDeck != []:
			self.Game.Hand_Deck.drawCard(self.ID, np.random.choice(rushMinionsinDeck))
			
		return self, None
		
		
class RedbandWasp(Minion):
	Class, race, name = "Warrior", "", "Redband Wasp"
	mana, attack, health = 2, 1, 3
	index = "Witchwood-Warrior-2-1-3-Minion-Beast-Redband Wasp-Rush"
	needTarget, keyWord, description = False, "Rush", "Rush. Has +3 Attack while damaged"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggers["StatChanges"] = [self.handleEnrage]
		
	def handleEnrage(self):
		if self.silenced == False and self.onBoard:
			if self.activated == False and self.health < self.health_upper:
				self.activated = True
				self.statChange(3, 0)
			elif self.activated and self.health >= self.health_upper:
				self.activated = False
				self.statChange(-3, 0)
				
				
class Warpath(Spell):
	Class, name = "Warrior", "Warpath"
	needTarget, mana = False, 2
	index = "Witchwood-Warrior-2-Spell-Warpath-Echo"
	description = "Echo. Deal 1 damage to all enemy minions"
	def whenEffective(self, target=None, comment="", choice=0):
		damage = (1 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		print("Warpath is cast and deals %d damage to all minions."%damage)
		targets = self.Game.minionsonBoard(1) + self.Game.minionsonBoard(2)
		self.Game.AOE(self, targets, [damage for obj in targets])
		return None
		
		
class WoodcuttersAxe(Weapon):
	Class, name, description = "Warrior", "Woodcutter's Axe", "Deathrattle: Give +2/+1 to a random friendly Rush minion "
	mana, attack, durability = 2, 2, 2
	index = "Witchwood-Warrior-2-2-2-Weapon-Woodcutter's Axe-Deathrattle"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [GiveaRushFriendlyPlus2Plus1(self)]
		
class GiveaRushFriendlyPlus2Plus1(Deathrattle_Weapon):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("Deathrattle: Give +2/+1 to a random friendly Rush minion triggers.")
		rushMinions = []
		for minion in self.entity.Game.minionsonBoard[self.entity.ID]:
			if minion.keyWords["Rush"] > 0:
				rushMinions.append(minion)
				
		if rushMinions != []:
			np.random.choice(rushMinions).buffDebuff(2, 1)
			
			
class RabidWorgen(Minion):
	Class, race, name = "Warrior", "", "Rabid Worgen"
	mana, attack, health = 3, 3, 3
	index = "Witchwood-Warrior-3-3-3-Minion-None-Rabid Worgen-Rush"
	needTarget, keyWord, description = False, "Rush", "Rush"
	
	
class MilitiaCommander(Minion):
	Class, race, name = "Warrior", "", "Militia Commander"
	mana, attack, health = 4, 2, 5
	index = "Witchwood-Warrior-4-2-5-Minion-None-Militia Commander-Rush-Battlecry"
	needTarget, keyWord, description = False, "Rush", "Rush. Battlecry: Gain +3 Attack this turn"
	
	def whenEffective(self, target=None, comment="", choice=0):
		print("Militia Commander's battlecry gives minion +3 Attack this turn.")
		self.buffDebuff(3, 0, "EndofTurn")
		return self, None
		
		
class DariusCrowley(Minion):
	Class, race, name = "Warrior", "", "Darius Crowley"
	mana, attack, health = 5, 4, 4
	index = "Witchwood-Warrior-5-4-4-Minion-None-Darius Crowley-Rush-Legendary"
	needTarget, keyWord, description = False, "Rush", "Rush. After this attacks and kills a minion, gain +2/+2"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_DariusCrowley(self)]
		
class Trigger_DariusCrowley(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionAttackedMinion"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return subject == self.entity and self.entity.onBoard and self.entity.health > 0 and self.entity.dead == False and (target.health < 1 or target.dead == True)
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("After %s attacks and kills a minion %s, it gains +2/+2."%(self.entity.name, target.name))
		self.entity.buffDebuff(2, 2)
		
class FesterootHulk(Spell):
	Class, race, name = "Warrior", "",  "Festeroot Hulk"
	mana, attack, health = 5, 2, 7
	index = "Witchwood-Warrior-5-2-7-Minion-None-Festeroot Hulk"
	needTarget, keyWord, description = False, "", "After a friendly minion attacks, gain +1 Attack"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_FesterootHulk(self)]
		
class Trigger_FesterootHulk(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionAttackedMinion", "MinionAttackedHero"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject.ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("After friendly minion attacks, %s gains +1 Attack."%self.entity.name)
		self.entity.buffDebuff(1, 0)
		
		
class DeadlyArsenal(Spell):
	Class, name = "Warrior", "Deadly Arsenal"
	needTarget, mana = False, 6
	index = "Witchwood-Warrior-2-Spell-Warpath-Echo"
	description = "Reveal a weapon from your deck. Deal its Attack to all minions"
	def whenEffective(self, target=None, comment="", choice=0):
		print("Deadly Arsenal is cast and reveals a weapon in player's deck to deal damage equal to its attack to all minions.")
		weaponsinDeck = []
		for card in self.Game.Hand_Deck.decks[self.ID]:
			if card.cardType == "Weapon":
				weaponsinDeck.append(card)
				
		if weapons == []:
			print("No weapon in player's deck. Nothing happens.")
		else:
			damage = (np.random.choice(weapons).attack + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			print(self.name, " deals %d damage to all minions."%damage)
			targets = self.Game.minionsonBoard(1) + self.Game.minionsonBoard(2)
			self.dealsAOE(targets, [damage for obj in targets])
		return None
		
		
class BlackhowlGunspire(Minion):
	Class, race, name = "Warrior", "", "Blackhowl Gunspire"
	mana, attack, health = 7, 3, 8
	index = "Witchwood-Warrior-7-3-8-Minion-None-Blackhowl Gunspire-Legendary"
	needTarget, keyWord, description = False, "", "Can't attack. Whenever this minion takes damage, deal 3 damage to a random enemy"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_BlackhowlGunspire(self)]
		
class Trigger_BlackhowlGunspire(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionTakesDamage"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return target == self.entity and self.entity.onBoard
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print(self.entity.name, "takes Damage and deals 3 damage to a random enemy.")
		enemies = [self.entity.Game.heroes[3-self.entity.ID]]
		for minion in self.entity.Game.minionsonBoard(3-self.entity.ID):
			if minion.health > 0 and minion.dead != True:
				enemies.append(minion)
				
		self.entity.dealsDamage(np.random.choice(enemies), 3)