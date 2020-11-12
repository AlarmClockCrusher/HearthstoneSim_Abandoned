from CardTypes import *
from Triggers_Auras import *

from Basic import IllidariInitiate

from numpy.random import choice as npchoice
from numpy.random import randint as nprandint
from numpy.random import shuffle as npshuffle

def extractfrom(target, listObj):
	try: return listObj.pop(listObj.index(target))
	except: return None
	
def fixedList(listObj):
	return listObj[0:len(listObj)]
	
def PRINT(game, string, *args):
	if game.GUI:
		if not game.mode: game.GUI.printInfo(string)
	elif not game.mode: print("game's guide mode is 0\n", string)

""""Demon Hunter Yr Dragon cards"""

"""Mana 0 cards"""
class Blur(Spell):
	Class, name = "Demon Hunter", "Blur"
	requireTarget, mana = False, 0
	index = "Shadows~Demon Hunter~Spell~0~Blur"
	description = "Your hero can't take damage this turn"
	#不知道与博尔碎盾的结算是如何进行的。
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		PRINT(self.Game, "Blur is cast and player can't take any damage this turn")
		trig = BlurEffect(self.Game, self.ID)
		trig.connect()
		return None
		
class BlurEffect:
	def __init__(self, Game, ID):
		self.Game, self.ID = Game, ID
		self.signals = ["FinalDmgonHero?"]
		self.temp = False
		
	def connect(self):
		try: self.Game.trigsBoard[self.ID]["FinalDmgonHero?"].append(self)
		except: self.Game.trigsBoard[self.ID]["FinalDmgonHero?"] = [self]
		self.Game.turnEndTrigger.append(self)
		
	def disconnect(self):
		try: self.Game.trigsBoard[self.ID]["FinalDmgonHero?"].remove(self)
		except: pass
		try: self.Game.turnEndTrigger.remove(self)
		except: pass
		#number here is a list that holds the damage to be processed
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return target.ID == self.ID and target.onBoard
		
	def trigger(self, signal, ID, subject, target, number, comment, choice=0):
		if self.canTrigger(signal, ID, subject, target, number, comment):
			if self.Game.GUI: self.Game.GUI.showOffBoardTrig(Blur(self.Game, self.ID), linger=False)
			self.effect(signal, ID, subject, target, number, comment)
			
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		print("Blur prevents the player from taking damage")
		number[0] = 0
		
	def turnEndTrigger(self):
		self.disconnect()
		
	def createCopy(self, game): #不是纯的只在回合结束时触发，需要完整的createCopy
		if self not in game.copiedObjs: #这个扳机没有被复制过
			trigCopy = type(self)(game, self.ID)
			game.copiedObjs[self] = trigCopy
			return trigCopy
		else: #一个扳机被复制过了，则其携带者也被复制过了
			return game.copiedObjs[self]
			
			
class TwinSlice(Spell):
	Class, name = "Demon Hunter", "Twin Slice"
	requireTarget, mana = False, 1
	index = "Shadows~Demon Hunter~Spell~1~Twin Slice"
	description = "Give your hero +2 Attack this turn. Add 'Second Slice' to your hand"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		PRINT(self.Game, "Twin Slice is cast and gives player +2 Attack this turn")
		self.Game.heroes[self.ID].gainAttack(2)
		PRINT(self.Game, "Twin Slice puts a 'Second Slice' to player's hand")
		self.Game.Hand_Deck.addCardtoHand(SecondSlice(self.Game, self.ID), self.ID)
		return None
		
class SecondSlice(Spell):
	Class, name = "Demon Hunter", "Second Slice"
	requireTarget, mana = False, 1
	index = "Shadows~Demon Hunter~Spell~1~Second Slice~Uncollectible"
	description = "Give your hero +2 Attack this turn"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		PRINT(self.Game, "Second Slice is cast and gives player +2 Attack this turn")
		self.Game.heroes[self.ID].gainAttack(2)
		return None
		
		
"""Mana 1 cards"""
class Battlefiend(Minion):
	Class, race, name = "Demon Hunter", "Demon", "Battlefiend"
	mana, attack, health = 1, 1, 2
	index = "Shadows~Demon Hunter~Minion~1~1~2~Demon~Battlefiend"
	requireTarget, keyWord, description = False, "", "After your hero attacks, gain +1 Attack"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_Battlefiend(self)]
		
class Trig_Battlefiend(TrigBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["HeroAttackedMinion", "HeroAttackedHero"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject == self.entity.Game.heroes[self.entity.ID]
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self.entity.Game, "After friendly hero attacks, %s gains +1 Attack"%self.entity.name)
		self.entity.buffDebuff(1, 0)
		
		
class ConsumeMagic(Spell):
	Class, name = "Demon Hunter", "Consume Magic"
	requireTarget, mana = True, 1
	index = "Shadows~Demon Hunter~Spell~1~Consume Magic~Outcast"
	description = "Silence an enemy minion. Outcast: Draw a card"
	def available(self):
		return self.selectableEnemyMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.ID != self.ID and target.onBoard
		
	def effectCanTrigger(self):
		self.effectViable = self.Game.Hand_Deck.outcastcanTrigger(self)
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			PRINT(self.Game, "Consume Magic is cast and silences enemy minion %s"%target.name)
			target.getsSilenced()
		if posinHand == 0 or posinHand == -1:
			PRINT(self.Game, "Consume Magic's Outcast triggers and lets player draw a card")
			self.Game.Hand_Deck.drawCard(self.ID)
		return target
		
		
class ManaBurn(Spell):
	Class, name = "Demon Hunter", "Mana Burn"
	requireTarget, mana = False, 1
	index = "Shadows~Demon Hunter~Spell~1~Mana Burn"
	description = "Your opponent has 2 fewer Mana Crystals next turn"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		PRINT(self.Game, "Mana Burn is cast and the opponent has 2 fewer Mana Crystals next turn")
		self.Game.Manas.manas_withheld[3-self.ID] += 2
		self.Game.turnStartTrigger.append(TwoFewerManaEffectRemoved(self.Game, 3-self.ID))
		return None
		
#不知道这个少两个法力水晶是让它们空两个还是直接少真实的水晶
class TwoFewerManaEffectRemoved:
	def __init__(self, Game, ID):
		self.Game, self.ID = Game, ID
		
	def turnStartTrigger(self):
		PRINT(self.Game, "At the start of turn, Mana Burn's effect expires and player will no longer start a turn with two fewer Mana Crystals")
		self.Game.Manas.manas_withheld[self.ID] -= 2
		try: self.Game.turnStartTrigger.remove(self)
		except: pass
		
	def createCopy(self, game):
		return type(self)(game, self.ID)
		
		
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
		PRINT(self.entity.Game, "Deathrattle: Add a 2/1 Lost Soul to your hand triggers")
		self.entity.Game.Hand_Deck.addCardtoHand(LostSoul, self.entity.ID, "type")
		
class LostSoul(Minion):
	Class, race, name = "Demon Hunter", "", "Lost Soul"
	mana, attack, health = 1, 2, 1
	index = "Shadows~Demon Hunter~Minion~1~2~1~None~Lost Soul~Uncollectible"
	requireTarget, keyWord, description = False, "", ""
	
	
"""Mana 2 cards"""
class BladeDance(Spell):
	Class, name = "Demon Hunter", "Blade Dance"
	requireTarget, mana = False, 2
	index = "Shadows~Demon Hunter~Spell~2~Blade Dance"
	description = "Deal damage equal to your hero's Attack to 3 random enemy minions"
	def available(self):
		return self.Game.heroes[self.ID].attack > 0
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		damage = (self.Game.heroes[self.ID].attack + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		curGame = self.Game
		minions = curGame.minionsAlive(3-self.ID)
		if damage > 0 and minions:
			if curGame.mode == 0:
				if curGame.guides:
					minions = [curGame.minions[3-self.ID][i] for i in curGame.guides.pop(0)]
				else:
					minions = list(npchoice(minions, min(3, len(minions)), replace=False))
					curGame.fixedGuides.append(tuple([minion.position for minion in minions]))
				PRINT(curGame, "Blade Dance is cast and deals {} damage to enemy minions {}".format(damage, minions))
				self.dealsAOE(minions, [damage]*len(minions))
		return None
		
		
class FeastofSouls(Spell):
	Class, name = "Demon Hunter", "Feast of Souls"
	requireTarget, mana = False, 2
	index = "Shadows~Demon Hunter~Spell~2~Feast of Souls"
	description = "Draw a card for each friendly minion that died this turn"
	def effectCanTrigger(self):
		self.effectViable = self.Game.Counters.minionsDiedThisTurn[self.ID] != []
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		PRINT(self.Game, "Feast of Souls is cast and lets player draw a card for each friendly minion that died this turn.")
		num = len(self.Game.Counters.minionsDiedThisTurn[self.ID])
		for i in range(num): self.Game.Hand_Deck.drawCard(self.ID)
		return None
		
		
class Umberwing(Weapon):
	Class, name, description = "Demon Hunter", "Umberwing", "Battlecry: Summon two 1/1 Felwings"
	mana, attack, durability = 2, 1, 2
	index = "Shadows~Demon Hunter~Weapon~2~1~2~Umberwing~Battlecry"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		PRINT(self.Game, "Umberwing's battlecry summons two 1/2 Felwings")
		self.Game.summon([Felwing(self.Game, self.ID) for i in range(2)], (-1, "totheRightEnd"), self.ID)
		return None
		
class Felwing(Minion):
	Class, race, name = "Demon Hunter", "Demon", "Felwing"
	mana, attack, health = 1, 1, 1
	index = "Shadows~Demon Hunter~Minion~1~1~1~Demon~Felwing~Uncollectible"
	requireTarget, keyWord, description = False, "", ""
	
	
"""Mana 3 cards"""
class AltruistheOutcast(Minion):
	Class, race, name = "Demon Hunter", "", "Altruis the Outcast"
	mana, attack, health = 4, 4, 2
	index = "Shadows~Demon Hunter~Minion~4~4~2~None~Altruis the Outcast~Legendary"
	requireTarget, keyWord, description = False, "", "After you play the left- or right-most card in your hand, deal 1 damage to all enemies"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_AltruistheOutcast(self)]
		
class Trig_AltruistheOutcast(TrigBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionBeenPlayed", "SpellBeenPlayed", "WeaponBeenPlayed", "HeroCardBeenPlayed"])
		
	#The comment passed is the position of card in hand when they are played.
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject.ID == self.entity.ID and subject != self.entity and (comment == -1 or comment == 0)
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self.entity.Game, "After player plays the left- or right-most card in hand, %s deals 1 damage to all enemies"%self.entity.name)
		targets = [self.entity.Game.heroes[3-self.entity.ID]] + self.entity.Game.minionsonBoard(3-self.entity.ID)
		self.entity.dealsAOE(targets, [1 for enemy in targets])
		
		
class EyeBeam(Spell):
	Class, name = "Demon Hunter", "Eye Beam"
	requireTarget, mana = True, 3
	index = "Shadows~Demon Hunter~Spell~3~Eye Beam~Outcast"
	description = "Lifesteal. Deal 3 damage to a minion. Outcast: This costs (1)"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.keyWords["Lifesteal"] = 1
		self.trigsHand = [Trig_EyeBeam(self)]
		
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
		
	def effectCanTrigger(self):
		self.effectViable = self.Game.Hand_Deck.outcastcanTrigger(self)
		
	def selfManaChange(self):
		if self.inHand:
			posinHand = self.Game.Hand_Deck.hands[self.ID].index(self)
			if posinHand == 0 or posinHand == len(self.Game.Hand_Deck.hands[self.ID]) - 1:
				self.mana = 1
				
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			damage = (3 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			PRINT(self.Game, "Eye Beam deals %d damage to minion %s"%(damage, target.name))
			self.dealsDamage(target, damage)
		return target
		
class Trig_EyeBeam(TrigHand):
	def __init__(self, entity):
		self.blank_init(entity, ["CardLeavesHand", "CardEntersHand"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		if self.entity.inHand:
			card = target[0] if signal == "CardEntersHand" else target
			return card.ID == self.entity.ID
		return False
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.Game.Manas.calcMana_Single(self.entity)
		
		
class WrathscaleNaga(Minion):
	Class, race, name = "Demon Hunter", "", "Wrathscale Naga"
	mana, attack, health = 3, 3, 1
	index = "Shadows~Demon Hunter~Minion~3~3~1~None~Wrathscale Naga"
	requireTarget, keyWord, description = False, "", "After a friendly minion dies, deal 3 damage to a random enemy"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_WrathscaleNaga(self)]
		
class Trig_WrathscaleNaga(TrigBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionDied"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and target != self.entity and target.ID == self.entity.ID #Technically, minion has to disappear before dies. But just in case.
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		curGame = self.entity.Game
		if curGame.mode == 0:
			enemy = None
			if curGame.guides:
				i, where = curGame.guides.pop(0)
				if where: enemy = curGame.find(i, where)
			else:
				targets = curGame.charsAlive(3-self.entity.ID)
				if targets:
					enemy = npchoice(targets)
					curGame.fixedGuides.append((enemy.position, "minion%d"%enemy.ID) if enemy.type == "Minion" else (enemy.ID, "hero"))
				else: curGame.fixedGuides.append((0, ""))
			if enemy:
				PRINT(curGame, "After a friendly minion dies, Wrathscale Naga deals 3 damage to random enemy %s"%enemy.name)
				self.entity.dealsDamage(enemy, 1)
				
"""Mana 4 cards"""
class IllidariFelblade(Minion):
	Class, race, name = "Demon Hunter", "", "Illidari Felblade"
	mana, attack, health = 4, 5, 3
	index = "Shadows~Demon Hunter~Minion~4~5~3~None~Illidari Felblade~Rush~Outcast"
	requireTarget, keyWord, description = False, "Rush", "Rush. Outcast: Gain Immune this turn"
	
	def effectCanTrigger(self):
		self.effectViable = self.Game.Hand_Deck.outcastcanTrigger(self)
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if posinHand == 0 or posinHand == -1:
			PRINT(self.Game, "Illidari Felblade's Outcast triggers and minion gains Immune this turn")
			self.status["Immune"] = 1
		return None
		
		
class RagingFelscreamer(Minion):
	Class, race, name = "Demon Hunter", "", "Raging Felscreamer"
	mana, attack, health = 4, 4, 4
	index = "Shadows~Demon Hunter~Minion~4~4~4~None~Raging Felscreamer~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: The next Demon you play costs (2) less"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		PRINT(self.Game, "Raging Felscreamer's battlecry makes player's next Demon cost (2) less")
		tempAura = YourNextDemonCosts2Less(self.Game, self.ID)
		self.Game.Manas.CardAuras.append(tempAura)
		tempAura.auraAppears()
		return None
		
class YourNextDemonCosts2Less(TempManaEffect):
	def __init__(self, Game, ID):
		self.Game, self.ID = Game, ID
		self.changeby, self.changeto = -2, -1
		self.temporary = False #不会在回合结束后消失，直到那个恶魔被打出为止
		self.auraAffected = []
		
	def applicable(self, target):
		return target.ID == self.ID and target.type == "Minion" and "Demon" in target.race
		
	def selfCopy(self, game):
		return type(self)(game, self.ID)
		
		
class SoulSplit(Spell):
	Class, name = "Demon Hunter", "Soul Split"
	requireTarget, mana = True, 4
	index = "Shadows~Demon Hunter~Spell~4~Soul Split"
	description = "Choose a friendly Demon. Summon a copy of it"
	
	def available(self):
		return self.selectableFriendlyMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and "Demon" in target.race and target.ID == self.ID and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target and self.Game.space(self.ID) > 0:
			PRINT(self.Game, "Soul Split is cast and summons a copy of friendly demon %s"%target.name)
			Copy = target.selfCopy(self.ID) if target.onBoard else type(target)(self.Game, self.ID)
			self.Game.summon(Copy, target.position+1, self.ID)
		return target
		
"""Mana 5 cards"""
class CommandtheIllidari(Spell):
	Class, name = "Demon Hunter", "Command the Illidari"
	requireTarget, mana = False, 5
	index = "Shadows~Demon Hunter~Spell~5~Command the Illidari"
	description = "Summon six 1/1 Illidari with Rush"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		PRINT(self.Game, "Command the Illidari is cast and summons six 1/1 Illidari with Rush")
		self.Game.summon([IllidariInitiate(self.Game, self.ID) for i in range(6)], (-1, "totheRightEnd"), self.ID)
		return None
		
class WrathspikeBrute(Minion):
	Class, race, name = "Demon Hunter", "Demon", "Wrathspike Brute"
	mana, attack, health = 5, 2, 6
	index = "Shadows~Demon Hunter~Minion~5~2~6~Demon~Wrathspike Brute"
	requireTarget, keyWord, description = False, "Taunt", "Taunt. After this is attacked, deal 1 damage to all enemies"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_WrathspikeBrute(self)]
		
class Trig_WrathspikeBrute(TrigBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionAttackedMinion", "HeroAttackedMinion"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and target == self.entity
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self.entity.Game, "After %s is attacked, it deals 1 damage to all enemies."%self.entity.name)
		targets = [self.entity.Game.heroes[3-self.entity.ID]] + self.entity.Game.minionsonBoard(3-self.entity.ID)
		self.entity.dealsAOE(targets, [1 for minion in targets])
		
"""Mana 7 cards"""
class Flamereaper(Weapon):
	Class, name, description = "Demon Hunter", "Flamereaper", "Also damages the minions next to whomever your hero attacks"
	mana, attack, durability = 7, 4 ,3
	index = "Shadows~Demon Hunter~Weapon~7~4~3~Flamereaper"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.marks["Sweep"] = 1
		
"""Mana 8 cards"""
class HulkingOverfiend(Minion):
	Class, race, name = "Demon Hunter", "Demon", "Hulking Overfiend"
	mana, attack, health = 8, 5, 10
	index = "Shadows~Demon Hunter~Minion~8~5~10~Demon~Hulking Overfiend~Rush"
	requireTarget, keyWord, description = False, "Rush", "Rush. After this attacks and kills a minion, it may attack again"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_HulkingOverfiend(self)]
		
class Trig_HulkingOverfiend(TrigBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionAttackedMinion"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject == self.entity and self.entity.health > 0 and self.entity.dead == False and (target.health < 1 or target.dead == True)
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self.entity.Game, "After %s attacks and kills a minion %s, it gains an extra attack chance."%(self.entity.name, target.name))
		self.entity.attChances_extra += 1
		
		
class Nethrandamus(Minion):
	Class, race, name = "Demon Hunter", "Dragon", "Nethrandamus"
	mana, attack, health = 9, 8, 8
	index = "Shadows~Demon Hunter~Minion~9~8~8~Dragon~Nethrandamus~Battlecry~Legendary"
	requireTarget, keyWord, description = False, "", "Battlecry: Summon two random 0-Cost minions. (Upgrades each time a friendly minion dies!)"
	poolIdentifier = "0-Cost Minions to Summon"
	@classmethod
	def generatePool(cls, Game):
		return ["%d-Cost Minions to Summon"%cost for cost in Game.MinionsofCost.keys()], \
				[list(Game.MinionsofCost[cost].values()) for cost in Game.MinionsofCost.keys()]
				
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsHand = [Trig_Nethrandamus(self)] #只有在手牌中才会升级
		self.progress = 0
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if curGame.mode == 0:
			if curGame.guides:
				minions = curGame.guides.pop(0)
			else:
				cost = self.progress
				while cost not in curGame.MinionsofCost: #假设计数过高，超出了费用范围，则取最高的可选费用
					cost -= 1
				minions = npchoice(curGame.RNGPools["%d-Cost Minions to Summon"%cost], 2, replace=True)
				curGame.fixedGuides.append(tuple(minions))
			PRINT(curGame, "Nethrandamus' battlecry summons two random %d-Cost minions."%self.progress)
			pos = (self.position, "leftandRight") if self.onBoard else (-1, "totheRightEnd")
			curGame.summon([minion(curGame, self.ID) for minion in minions], pos, self.ID)
		return None
		
class Trig_Nethrandamus(TrigHand):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionDies"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.inHand and target.ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.progress += 1
		
		
DemonHunterInit_Indices = {"Shadows~Demon Hunter~Spell~0~Blur": Blur,
							"Shadows~Demon Hunter~Spell~1~Twin Slice": TwinSlice,
							"Shadows~Demon Hunter~Spell~1~Second Slice~Uncollectible": SecondSlice,
							"Shadows~Demon Hunter~Minion~1~1~2~Demon~Battlefiend": Battlefiend,
							"Shadows~Demon Hunter~Spell~1~Consume Magic~Outcast": ConsumeMagic,
							"Shadows~Demon Hunter~Spell~1~Mana Burn": ManaBurn,
							"Shadows~Demon Hunter~Minion~1~2~1~Demon~Ur'zul Horror~Deathrattle": UrzulHorror,
							"Shadows~Demon Hunter~Minion~1~2~1~None~Lost Soul~Uncollectible": LostSoul,
							"Shadows~Demon Hunter~Spell~2~Blade Dance": BladeDance,
							"Shadows~Demon Hunter~Spell~2~Feast of Souls": FeastofSouls,
							"Shadows~Demon Hunter~Weapon~2~1~2~Umberwing~Battlecry": Umberwing,
							"Shadows~Demon Hunter~Minion~1~1~1~Demon~Felwing~Uncollectible": Felwing,
							"Shadows~Demon Hunter~Minion~4~4~2~None~Altruis the Outcast~Legendary": AltruistheOutcast,
							"Shadows~Demon Hunter~Spell~3~Eye Beam~Outcast": EyeBeam,
							"Shadows~Demon Hunter~Minion~3~3~1~None~Wrathscale Naga": WrathscaleNaga,
							"Shadows~Demon Hunter~Minion~4~5~3~None~Illidari Felblade~Rush~Outcast": IllidariFelblade,
							"Shadows~Demon Hunter~Minion~4~4~4~None~Raging Felscreamer~Battlecry": RagingFelscreamer,
							"Shadows~Demon Hunter~Spell~4~Soul Split": SoulSplit,
							"Shadows~Demon Hunter~Spell~5~Command the Illidari": CommandtheIllidari,
							"Shadows~Demon Hunter~Minion~5~2~6~Demon~Wrathspike Brute": WrathspikeBrute,
							"Shadows~Demon Hunter~Weapon~7~4~3~Flamereaper": Flamereaper,
							"Shadows~Demon Hunter~Minion~8~5~10~Demon~Hulking Overfiend~Rush": HulkingOverfiend,
							"Shadows~Demon Hunter~Minion~9~8~8~Dragon~Nethrandamus~Battlecry~Legendary": Nethrandamus,
							}
							