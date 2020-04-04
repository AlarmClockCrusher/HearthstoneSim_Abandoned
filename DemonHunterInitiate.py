from CardTypes import *
from Triggers_Auras import *
from VariousHandlers import *
from Basic import IllidariInitiate
def extractfrom(target, listObject):
	temp = None
	for i in range(len(listObject)):
		if listObject[i] == target:
			temp = listObject.pop(i)
			break
	return temp
	
def fixedList(listObject):
	return listObject[0:len(listObject)]
	
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
		
""""Demon Hunter Yr Dragon cards"""

"""Mana 0 cards"""
class Blur(Spell):
	Class, name = "Demon Hunter", "Blur"
	requireTarget, mana = False, 0
	index = "Shadows~Demon Hunter~Spell~0~Blur"
	description = "Your hero can't take damage this turn"
	#不知道与博尔碎盾的结算是如何进行的。
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		PRINT(self, "Blur is cast and player can't take any damage this turn")
		trigger = Trigger_Blur(self.Game, self.ID)
		trigger.connect()
		return None
		
class Trigger_Blur(TriggeronBoard):
	def __init__(self, Game, ID):
		self.Game, self.ID = Game, ID
		self.signals = ["HeroAbouttoTakeDamage"]
		self.temp = False
		#number here is a list that holds the damage to be processed
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return target.ID == self.ID and target.onBoard
		
	def connect(self):
		for signal in self.signals:
			self.Game.triggersonBoard[self.ID].append((self, signal))
		self.Game.turnEndTrigger.append(self)
		
	def disconnect(self):
		for signal in self.signals:
			extractfrom((self, signal), self.Game.triggersonBoard[self.ID])
		extractfrom(self, self.Game.turnEndTrigger)
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self, "Blur prevents the player from taking damage")
		number[0] = 0
		
	def turnEndTrigger(self):
		self.disconnect()
		
		
class TwinSlice(Spell):
	Class, name = "Demon Hunter", "Twin Slice"
	requireTarget, mana = False, 0
	index = "Shadows~Demon Hunter~Spell~0~Twin Slice"
	description = "Give your hero +1 Attack this turn. Add 'Second Slice' to your hand"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		PRINT(self, "Twin Slice is cast and gives player +1 Attack this turn")
		self.Game.heroes[self.ID].gainTempAttack(1)
		PRINT(self, "Twin Slice puts a 'Second Slice' to player's hand")
		self.Game.Hand_Deck.addCardtoHand(SecondSlice(self.Game, self.ID), self.ID)
		return None
		
class SecondSlice(Spell):
	Class, name = "Demon Hunter", "Second Slice"
	requireTarget, mana = False, 0
	index = "Shadows~Demon Hunter~Spell~0~Second Slice~Uncollectible"
	description = "Give your hero +1 Attack this turn"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		PRINT(self, "Second Slice is cast and gives player +1 Attack this turn")
		self.Game.heroes[self.ID].gainTempAttack(1)
		return None
		
		
"""Mana 1 cards"""
class Battlefiend(Minion):
	Class, race, name = "Demon Hunter", "Demon", "Battlefiend"
	mana, attack, health = 1, 2, 2
	index = "Shadows~Demon Hunter~Minion~1~2~2~Demon~Battlefiend"
	requireTarget, keyWord, description = False, "", "After your hero attacks, gain +1 Attack"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_Battlefiend(self)]
		
class Trigger_Battlefiend(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["HeroAttackedMinion", "HeroAttackedHero"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject == self.entity.Game.heroes[self.entity.ID]
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self, "After friendly hero attacks, %s gains +1 Attack"%self.entity.name)
		self.entity.buffDebuff(1, 0)
		
		
class ConsumeMagic(Spell):
	Class, name = "Demon Hunter", "Consume Magic"
	requireTarget, mana = True, 1
	index = "Shadows~Demon Hunter~Spell~1~Consume Magic~Outcast"
	description = "Silence an enemy minion. Outcast: Draw a card"
	def available(self):
		return self.selectableEnemyMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.ID != self.ID and target.onBoard
		
	def effectCanTrigger(self):
		posinHand = self.Game.Hand_Deck.hands[self.ID].index(self)
		self.effectViable = posinHand == 0 or posinHand == len(self.Game.Hand_Deck.hands[self.ID]) - 1
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if target != None:
			PRINT(self, "Consume Magic is cast and silences enemy minion %s"%target.name)
			target.getsSilenced()
		if posinHand == 0 or posinHand == -1:
			PRINT(self, "Consume Magic's Outcast triggers and lets player draw a card")
			self.Game.Hand_Deck.drawCard(self.ID)
		return target
		
		
class ManaBurn(Spell):
	Class, name = "Demon Hunter", "Mana Burn"
	requireTarget, mana = False, 1
	index = "Shadows~Demon Hunter~Spell~1~Mana Burn"
	description = "Your opponent has 2 fewer Mana Crystals next turn"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		PRINT(self, "Mana Burn is cast and the opponent has 2 fewer Mana Crystals next turn")
		self.Game.ManaHandler.manas_withheld[3-self.ID] += 2
		self.Game.turnStartTrigger.append(TwoFewerManaEffectRemoved(self.Game, 3-self.ID))
		return None
		
#不知道这个少两个法力水晶是让它们空两个还是直接少真实的水晶
class TwoFewerManaEffectRemoved:
	def __init__(self, Game, ID):
		self.Game, self.ID = Game, ID
		
	def turnStartTrigger(self):
		PRINT(self, "At the start of turn, Mana Burn's effect expires and player will no longer start a turn with two fewer Mana Crystals")
		self.Game.ManaHandler.manas_withheld[self.ID] -= 2
		extractfrom(self, self.Game.turnStartTrigger)
		
	def selfCopy(self, recipientGame):
		return type(self)(recipientGame, self.ID)
		
		
class UrzulHorror(Minion):
	Class, race, name = "Demon Hunter", "Demon", "Ur'zul Horror"
	mana, attack, health = 1, 2, 1
	index = "Shadows~Demon Hunter~Minion~1~2~1~Demon~Ur'zul Horror~Deathrattle"
	requireTarget, keyWord, description = False, "", "Deathrattle: Add a 2/1 Lost Soul to your hand"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [AddaLostSoultoYourHand(self)]
		
class AddaLostSoultoYourHand(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self, "Deathrattle: Add a 2/1 Lost Soul to your hand triggers")
		self.entity.Game.Hand_Deck.addCardtoHand(LostSoul, self.entity.ID, "CreateUsingType")
		
class LostSoul(Minion):
	Class, race, name = "Demon Hunter", "", "Lost Soul"
	mana, attack, health = 1, 2, 1
	index = "Shadows~Demon Hunter~Minion~1~2~1~None~Lost Soul~Uncollectible"
	requireTarget, keyWord, description = False, "", ""
	
	
"""Mana 2 cards"""
class BladeDance(Spell):
	Class, name = "Demon Hunter", "Blade Dance"
	requireTarget, mana = False, 2
	index = "Shadows~Demon Hunter~Spell~1~Blade Dance"
	description = "Deal damage equal to your hero's Attack to 3 random enemy minions"
	def available(self):
		return self.Game.heroes[self.ID].attack > 0
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		damage = (self.Game.heroes[self.ID].attack + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		PRINT(self, "Blade Dance is cast and deals %d damage to 3 random enemy minion"%damage)
		minions = self.Game.minionsonBoard(3-self.ID)
		if len(minions) > 1:
			targets = np.random.choice(minions, min(3, len(minions)), replace=False)
			PRINT(self, "Blade Dance deals {} damage to random minions {}".format(damage, targets))
			self.dealsAOE(targets, [damage for minion in targets])
		elif len(minions) == 1:
			PRINT(self, "Blade Dance deals %d damage to minion %s"%(damage, minions[0].name))
			self.dealsDamage(minions[0], damage)
		return None
		
		
class FeastofSouls(Spell):
	Class, name = "Demon Hunter", "Feast of Souls"
	requireTarget, mana = False, 2
	index = "Shadows~Demon Hunter~Spell~2~Feast of Souls"
	description = "Draw a card for each friendly minion that died this turn"
	def effectCanTrigger(self):
		self.effectViable = self.Game.CounterHandler.minionsDiedThisTurn[self.ID] != []
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		PRINT(self, "Feast of Souls is cast and lets player draw a card for each friendly minion that died this turn.")
		numMinionsDiedThisTurn = len(self.Game.CounterHandler.minionsDiedThisTurn[self.ID])
		for i in range(numMinionsDiedThisTurn):
			self.Game.Hand_Deck.drawCard(self.ID)
		return None
		
		
class Umberwing(Weapon):
	Class, name, description = "Demon Hunter", "Umberwing", "Battlecry: Summon two 1/1 Felwings"
	mana, attack, durability = 2, 1, 2
	index = "Shadows~Demon Hunter~Weapon~2~1~2~Umberwing~Battlecry"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		PRINT(self, "Umberwing's battlecry summons two 1/2 Felwings")
		self.Game.summonMinion([Felwing(self.Game, self.ID) for i in range(2)], (-1, "totheRightEnd"), self.ID)
		return None
		
class Felwing(Minion):
	Class, race, name = "Demon Hunter", "Demon", "Felwing"
	mana, attack, health = 1, 1, 1
	index = "Shadows~Demon Hunter~Minion~1~1~1~Demon~Felwing~Uncollectible"
	requireTarget, keyWord, description = False, "", ""
	
	
"""Mana 3 cards"""
class AltruistheOutcast(Minion):
	Class, race, name = "Demon Hunter", "", "Altruis the Outcast"
	mana, attack, health = 3, 3, 2
	index = "Shadows~Demon Hunter~Minion~3~3~2~None~Altruis the Outcast~Legendary"
	requireTarget, keyWord, description = False, "", "After you play the left- or right-most card in your hand, deal 1 damage to all enemies"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_AltruistheOutcast(self)]
		
class Trigger_AltruistheOutcast(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionBeenPlayed", "SpellBeenPlayed", "WeaponBeenPlayed", "HeroCardBeenPlayed"])
		
	#The comment passed is the position of card in hand when they are played.
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject.ID == self.entity.ID and subject != self.entity and (comment == -1 or comment == 0)
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self, "After player plays the left- or right-most card in hand, %s deals 1 damage to all enemies"%self.entity.name)
		targets = [self.entity.Game.heroes[3-self.entity.ID]] + self.entity.Game.minionsonBoard(3-self.entity.ID)
		self.entity.dealsAOE(targets, [1 for enemy in targets])
		
		
class EyeBeam(Spell):
	Class, name = "Demon Hunter", "Eye Beam"
	requireTarget, mana = True, 3
	index = "Shadows~Demon Hunter~Spell~3~Eye Beam~Outcast"
	description = "Lifesteal. Deal 3 damage to a minion. Outcast: This costs (0)"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.keyWords["Lifesteal"] = 1
		self.triggersinHand = [Trigger_EyeBeam(self)]
		
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and target.onBoard
		
	def effectCanTrigger(self):
		posinHand = self.Game.Hand_Deck.hands[self.ID].index(self)
		self.effectViable = posinHand == 0 or posinHand == len(self.Game.Hand_Deck.hands[self.ID]) - 1
		
	def selfManaChange(self):
		if self.inHand:
			posinHand = self.Game.Hand_Deck.hands[self.ID].index(self)
			if posinHand == 0 or posinHand == len(self.Game.Hand_Deck.hands[self.ID]) - 1:
				self.mana = 0
				
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if target != None:
			damage = (3 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			PRINT(self, "Eye Beam deals %d damage to minion %s"%(damage, target.name))
			self.dealsDamage(target, damage)
		return target
		
class Trigger_EyeBeam(TriggerinHand):
	def __init__(self, entity):
		self.blank_init(entity, ["CardLeavesHand", "CardEntersHand"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		if self.entity.inHand:
			card = target[0] if signal == "CardEntersHand" else target
			return card.ID == self.entity.ID
		return False
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.Game.ManaHandler.calcMana_Single(self.entity)
		
		
class WrathscaleNaga(Minion):
	Class, race, name = "Demon Hunter", "", "Wrathscale Naga"
	mana, attack, health = 3, 3, 1
	index = "Shadows~Demon Hunter~Minion~3~3~1~None~Wrathscale Naga"
	requireTarget, keyWord, description = False, "", "After a friendly minion dies, deal 3 damage to a random enemy"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_WrathscaleNaga(self)]
		
class Trigger_WrathscaleNaga(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionDied"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and target != self.entity and target.ID == self.entity.ID #Technically, minion has to disappear before dies. But just in case.
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self, "After friendly minion %s dies, %s deals 3 damage to a random enemy."%(target.name, self.entity.name))
		targets = self.entity.Game.livingObjtoTakeRandomDamage(3-self.entity.ID)
		target = np.random.choice(targets)
		PRINT(self, "%s deals 3 damage to %s"%(self.entity.name, target.name))
		self.entity.dealsDamage(target, 3)
		
"""Mana 4 cards"""
class IllidariFelblade(Minion):
	Class, race, name = "Demon Hunter", "", "Illidari Felblade"
	mana, attack, health = 4, 5, 3
	index = "Shadows~Demon Hunter~Minion~4~5~3~None~Illidari Felblade~Rush~Outcast"
	requireTarget, keyWord, description = False, "Rush", "Rush. Outcast: Gain Immune this turn"
	
	def effectCanTrigger(self):
		posinHand = self.Game.Hand_Deck.hands[self.ID].index(self)
		self.effectViable = posinHand == 0 or posinHand == len(self.Game.Hand_Deck.hands[self.ID]) - 1
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if posinHand == 0 or posinHand == -1:
			PRINT(self, "Illidari Felblade's Outcast triggers and minion gains Immune this turn")
			self.status["Immune"] = 1
		return None
		
		
class RagingFelscreamer(Minion):
	Class, race, name = "Demon Hunter", "", "Raging Felscreamer"
	mana, attack, health = 4, 4, 4
	index = "Shadows~Demon Hunter~Minion~4~4~4~None~Raging Felscreamer~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: The next Demon you play costs (2) less"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		PRINT(self, "Raging Felscreamer's battlecry makes player's next Demon cost (2) less")
		tempAura = YourNextDemonCosts2Less(self.Game, self.ID)
		self.Game.ManaHandler.CardAuras.append(tempAura)
		tempAura.auraAppears()
		return None
		
class YourNextDemonCosts2Less(TempManaEffect):
	def __init__(self, Game, ID):
		self.Game, self.ID = Game, ID
		self.changeby, self.changeto = -2, -1
		self.temporary = False #不会在回合结束后消失，直到那个恶魔被打出为止
		self.auraAffected = []
		
	def applicable(self, target):
		return target.ID == self.ID and target.cardType == "Minion" and "Demon" in target.race
		
		
class SoulSplit(Spell):
	Class, name = "Demon Hunter", "Soul Split"
	requireTarget, mana = True, 4
	index = "Shadows~Demon Hunter~Spell~4~Soul Split"
	description = "Choose a friendly Demon. Summon a copy of it"
	
	def available(self):
		return self.selectableFriendlyMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.cardType == "Minion" and "Demon" in target.race and target.ID == self.ID and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if target != None and self.Game.spaceonBoard(self.ID) > 0:
			PRINT(self, "Soul Split is cast and summons a copy of friendly demon %s"%target.name)
			Copy = target.selfCopy(self.ID) if target.onBoard else type(target)(self.Game, self.ID)
			self.Game.summonMinion(Copy, target.position+1, self.ID)
		return target
		
"""Mana 5 cards"""
class CommandtheIllidari(Spell):
	Class, name = "Demon Hunter", "Command the Illidari"
	requireTarget, mana = False, 5
	index = "Shadows~Demon Hunter~Spell~5~Command the Illidari"
	description = "Summon six 1/1 Illidari with Rush"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		PRINT(self, "Command the Illidari is cast and summons six 1/1 Illidari with Rush")
		self.Game.summonMinion([IllidariInitiate(self.Game, self.ID) for i in range(6)], (-1, "totheRightEnd"), self.ID)
		return None
		
class WrathspikeBrute(Minion):
	Class, race, name = "Demon Hunter", "Demon", "Wrathspike Brute"
	mana, attack, health = 5, 2, 6
	index = "Shadows~Demon Hunter~Minion~5~2~6~Demon~Wrathspike Brute"
	requireTarget, keyWord, description = False, "Taunt", "Taunt. After this is attacked, deal 1 damage to all enemies"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_WrathspikeBrute(self)]
		
class Trigger_WrathspikeBrute(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionAttackedMinion", "HeroAttackedMinion"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and target == self.entity
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self, "After %s is attacked, it deals 1 damage to all enemies."%self.entity.name)
		targets = [self.entity.Game.heroes[self.entity.ID]] + self.entity.Game.minionsonBoard(3-self.entity.ID)
		self.entity.dealsAOE(targets, [1 for minion in targets])
		
"""Mana 7 cards"""
class Flamereaper(Weapon):
	Class, name, description = "Demon Hunter", "Flamereaper", "Also damages the minions next to whomever your hero attacks"
	mana, attack, durability = 7, 4 ,3
	index = "Shadows~Demon Hunter~Weapon~7~4~3~Flamereaper"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.marks["Attack Adjacent Minions"] = 1
		
"""Mana 8 cards"""
class HulkingOverfiend(Minion):
	Class, race, name = "Demon Hunter", "Demon", "Hulking Overfiend"
	mana, attack, health = 8, 5, 10
	index = "Shadows~Demon Hunter~Minion~8~5~10~Demon~Hulking Overfiend~Rush"
	requireTarget, keyWord, description = False, "Rush", "Rush. After this attacks and kills a minion, it may attack again"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_HulkingOverfiend(self)]
		
class Trigger_HulkingOverfiend(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionAttackedMinion"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject == self.entity and self.entity.health > 0 and self.entity.dead == False and (target.health < 1 or target.dead == True)
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self, "After %s attacks and kills a minion %s, it gains an extra attack chance."%(self.entity.name, target.name))
		self.entity.attChances_extra += 1
		
		
class Nethrandamus(Minion):
	Class, race, name = "Demon Hunter", "Dragon", "Nethrandamus"
	mana, attack, health = 9, 8, 8
	index = "Shadows~Demon Hunter~Minion~9~8~8~Dragon~Nethrandamus~Battlecry~Legendary"
	requireTarget, keyWord, description = False, "", "Battlecry: Summon two random 0-Cost minions. (Upgrades each time a friendly minion dies!)"
	poolIdentifier = "0-Cost Minions"
	@classmethod
	def generatePool(cls, Game):
		costs, lists = [], []
		for cost in Game.MinionsofCost.keys():
			costs.append("%d-Cost Minions"%cost)
			lists.append(list(Game.MinionsofCost[cost].values()))
		return costs, lists
		
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersinHand = [Trigger_Nethrandamus(self)] #只有在手牌中才会升级
		self.progress = 0
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		PRINT(self, "Nethrandamus' battlecry summons two random %d-Cost minions."%self.progress)
		#假设计数过高，超出了费用范围，则取最高的可选费用
		cost, availableCosts = self.progress, list(self.Game.MinionsofCost.keys())
		while True:
			if cost not in availableCosts:
				cost -= 1
			else:
				break
		key = "%d-Cost Minions"%cost
		minions = np.random.choice(self.Game.RNGPools[key], 2, replace=True)
		pos = (self.position, "leftandRight") if self.onBoard else (-1, "totheRightEnd")
		self.Game.summonMinion([minion(self.Game, self.ID) for minion in minions], pos, self.ID)
		return None
		
class Trigger_Nethrandamus(TriggerinHand):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionDies"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.inHand and target.ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.progress += 1