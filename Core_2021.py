from CardTypes import *
from Triggers_Auras import *
from numpy.random import choice as npchoice
from numpy.random import randint as nprandint
from numpy.random import shuffle as npshuffle
from numpy import inf as npinf
import numpy as np

from Core import TheCoin

"""Core_2021"""

"""Neutral Cards"""
"""Mana 2 Cards"""
class AnnoyoTron(Minion):
	Class, race, name = "Neutral", "Mech", "Annoy-o-Tron"
	mana, attack, health = 2, 1, 2
	index = "Core_2021~Neutral~Minion~2~1~2~Mech~Annoy-o-Tron~Taunt~Divine Shield"
	requireTarget, keyWord, description = False, "Taunt,Divine Shield", "Taunt. Divine Shield"
	name_CN = "吵吵机器人"
	
	
"""Mana 5 Cards"""
class OverlordRunthak(Minion):
	Class, race, name = "Neutral", "", "Overlord Runthak"
	mana, attack, health = 5, 3, 6
	index = "Core_2021~Neutral~Minion~5~3~6~~Overlord Runthak~Rush~Legendary"
	requireTarget, keyWord, description = False, "Rush", "Rush. Whenever this minion attacks, give +1/+1 to all minions in your hand"
	name_CN = "伦萨克大王"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_OverlordRunthak(self)]
		
class Trig_OverlordRunthak(TrigBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionAttackingMinion", "MinionAttackingHero"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject == self.entity and self.entity.onBoard
		
	def text(self, CHN):
		return "每当该随从攻击时，使你手牌中的所有随从获得+1/+1" if CHN \
				else "Whenever this minion attacks, give +1/+1 to all minions in your hand"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		for card in self.entity.Game.Hand_Deck.hands[self.entity.ID]:
			if card.type == "Minion": card.buffDebuff(1, 1)
			
"""Mana 9 Cards"""
class MalygostheSpellweaver(Minion):
	Class, race, name = "Neutral", "Dragon", "Malygos, the Spellweaver"
	mana, attack, health = 9, 4, 12
	index = "Core_2021~Neutral~Minion~9~4~12~Dragon~Malygos, the Spellweaver~Battlecry~Legendary"
	requireTarget, keyWord, description = False, "", "Battlecry: Draw spells until your hand is full"
	name_CN = "沉睡者伊瑟拉"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame, ID = self.Game, self.ID
		ownDeck = curGame.Hand_Deck.decks[ID]
		if curGame.mode == 0:
			while curGame.Hand_Deck.handNotFull(ID):
				if curGame.guides:
					i = curGame.guides.pop(0)
				else:
					spells = [i for i, card in enumerate(ownDeck) if card.type == "Spell"]
					i = npchoice(spells) if spells else -1
					curGame.fixedGuides.append(i)
				if i > -1: curGame.Hand_Deck.drawCard(ID, i)
				else: break
		return None
		
		
class YseratheDreamer(Minion):
	Class, race, name = "Neutral", "Dragon", "Ysera, the Dreamer"
	mana, attack, health = 9, 4, 12
	index = "Core_2021~Neutral~Minion~9~4~12~Dragon~Ysera, the Dreamer~Battlecry~Legendary"
	requireTarget, keyWord, description = False, "", "Battlecry: Add one of each Dream card to your hand"
	name_CN = "沉睡者伊瑟拉"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.Game.Hand_Deck.addCardtoHand([Dream, Nightmare, YseraAwakens, LaughingSister, EmeraldDrake], self.ID, byType=True, creator=type(self))
		return None
		
class Dream(Spell):
	Class, school, name = "DreamCard", "", "Dream"
	requireTarget, mana = True, 0
	index = "Classic~DreamCard~Spell~0~Dream~Uncollectible"
	description = "Return a minion to its owner's hand"
	name_CN = "梦境"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			self.Game.returnMiniontoHand(target)
		return target
		
class Nightmare(Spell):
	Class, school, name = "DreamCard", "", "Nightmare"
	requireTarget, mana = True, 0
	index = "Classic~DreamCard~Spell~0~Nightmare~Uncollectible"
	description = "Give a minion +5/+5. At the start of your next turn, destroy it."
	name_CN = "噩梦"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target and target.onBoard:
			target.buffDebuff(5, 5)
			trig = Trig_Corruption(target)
			trig.ID = self.ID
			target.trigsBoard.append(trig)
			trig.connect()
		return target
		
class YseraAwakens(Spell):
	Class, school, name = "DreamCard", "", "Ysera Awakens"
	requireTarget, mana = False, 2
	index = "Classic~DreamCard~Spell~2~Ysera Awakens~Uncollectible"
	description = "Deal 5 damage to all characters except Ysera"
	name_CN = "伊瑟拉苏醒"
	def text(self, CHN):
		damage = (5 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		return "对除了伊瑟拉之外的所有角色造成%d点伤害"%damage if CHN else "Deal %d damage to all characters except Ysera"%damage
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		damage = (5 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		targets = [self.Game.heroes[1], self.Game.heroes[2]]
		for minion in self.Game.minionsonBoard(1) + self.Game.minionsonBoard(2):
			if minion.name != "Ysera" and minion.name != "Ysera, Unleashed":
				targets.append(minion)
				
		self.dealsAOE(targets, [damage for obj in targets])
		return None
		
class LaughingSister(Minion):
	Class, race, name = "DreamCard", "", "Laughing Sister"
	mana, attack, health = 3, 3, 5
	index = "Classic~DreamCard~Minion~3~3~5~~Laughing Sister~Uncollectible"
	requireTarget, keyWord, description = False, "", "Can't targeted by spells or Hero Powers"
	name_CN = "欢笑的姐妹"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.marks["Evasive"] = 1
		
class EmeraldDrake(Minion):
	Class, race, name = "DreamCard", "Dragon", "Emerald Drake"
	mana, attack, health = 4, 7, 6
	index = "Classic~DreamCard~Minion~4~7~6~Dragon~Emerald Drake~Uncollectible"
	requireTarget, keyWord, description = False, "", ""
	name_CN = "翡翠幼龙"
	
	
"""Mana 10 Cards"""
class DeathwingtheDestroyer(Minion):
	Class, race, name = "Neutral", "Dragon", "Deathwing, the Destroyer"
	mana, attack, health = 10, 12, 12
	index = "Core_2021~Neutral~Minion~10~12~12~Dragon~Deathwing, the Destroyer~Battlecry~Legendary"
	requireTarget, keyWord, description = False, "", "Battlecry: Destroy all other minions. Discard a card for each destroyed"
	name_CN = "灭世者 死亡之翼"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		minions = curGame.minionsAlive(self.ID, self) + curGame.minionsAlive(3-self.ID)
		curGame.killMinion(self, minions)
		if curGame.mode == 0:
			for num in range(len(minions)):
				if curGame.guides:
					i = curGame.guides.pop(0)
				else:
					ownHand = curGame.Hand_Deck.hands[self.ID]
					i = nprandint(len(ownHand)) if ownHand else -1
					curGame.fixedGuides.append(i)
				if i > -1: curGame.Hand_Deck.discardCard(self.ID, i)
				else: break
		return None
		
"""Demon Hunter Cards"""
"""Druid Cards"""
class MenagerieWarden(Minion):
	Class, race, name = "Druid", "", "Menagerie Warden"
	mana, attack, health = 6, 5, 5
	index = "Core_2021~Druid~Minion~6~5~5~~Menagerie Warden~Battlecry"
	requireTarget, keyWord, description = True, "", "Battlecry: Choose a friendly Beast. Summon a copy of it"
	name_CN = "展览馆守卫"
	
	def targetExists(self, choice=0):
		return self.selectableFriendlyMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.ID == self.ID and "Beast" in target.race and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target: #战吼触发时自己不能死亡。
			Copy = target.selfCopy(self.ID) if target.onBoard else type(target)(self.Game, self.ID)
			self.Game.summon(Copy, target.pos+1, creator=self)
		return target
		
		
"""Hunter Cards"""
"""Mage Cards"""
class Fireball(Spell):
	Class, school, name = "Mage", "Fire", "Fireball"
	requireTarget, mana = True, 4
	index = "Core_2021~Mage~Spell~4~Fire~Fireball"
	description = "Deal 6 damage"
	name_CN = "火球术"
	def text(self, CHN):
		damage = (6 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		return "造成%d点伤害"%damage if CHN else "Deal %d damage"%damage
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			damage = (6 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			self.dealsDamage(target, damage)
		return target
		
		
"""Paladin Cards"""
class TirionFordring(Minion):
	Class, race, name = "Paladin", "", "Tirion Fordring"
	mana, attack, health = 8, 6, 6
	index = "Core_2021~Paladin~Minion~8~6~6~~Tirion Fordring~Taunt~Divine Shield~Deathrattle~Legendary"
	requireTarget, keyWord, description = False, "Divine Shield,Taunt", "Divine Shield, Taunt. Deathrattle: Equip a 5/3 Ashbringer"
	name_CN = "提里昂弗丁"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [EquipAshbringer(self)]
		
class EquipAshbringer(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.Game.equipWeapon(Ashbringer(self.entity.Game, self.entity.ID))
		
	def text(self, CHN):
		return "亡语：装备一把5/3的灰烬使者" if CHN else "Deathrattle: Equip a 5/3 Ashbringer"
		
class Ashbringer(Weapon):
	Class, name, description = "Paladin", "Ashbringer", ""
	mana, attack, durability = 5, 5, 3
	index = "Core_2021~Paladin~Weapon~5~5~3~Ashbringer~Legendary~Uncollectible"
	name_CN = "灰烬使者"
	
	
"""Priest Cards"""
class ThriveintheShadows(Spell):
	Class, school, name = "Priest", "Shadow", "Thrive in the Shadows"
	requireTarget, mana = False, 2
	index = "Core_2021~Priest~Spell~2~Shadow~Thrive in the Shadows"
	description = "Discover a spell from your deck"
	name_CN = "暗中生长"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		ownDeck = curGame.Hand_Deck.decks[self.ID]
		if curGame.mode == 0:
			if curGame.guides:
				i = curGame.guides.pop(0)
				if i > -1: curGame.Hand_Deck.drawCard(self.ID, i)
			else:
				types, inds = [], []
				for i, card in enumerate(ownDeck):
					if card.type == "Spell":
						types.append(type(card))
						inds.append(i)
				if "byOthers" in comment:
					inds = npChoice_inds(types, inds, 1)
					i = inds[0] if inds else -1
					curGame.fixedGuides.append(i)
					if i > -1: curGame.Hand_Deck.drawCard(self.ID, i)
				else:
					inds = npChoice_inds(types, inds, 3)
					if len(ins) > 1:
						curGame.options = [ownDeck[i] for i in ins]
						curGame.Discover.startDiscover(self)
					else:
						i = inds[0] if ins else -1
						curGame.fixedGuides.append(i)
						if i > -1: curGame.Hand_Deck.drawCard(self.ID, i)
		return None
		
	def discoverDecided(self, option, pool):
		i = self.Game.Hand_Deck.decks[self.ID].index(option)
		self.Game.fixedGuides.append(i)
		curGame.Hand_Deck.drawCard(self.ID, i)
		
	
class Shadowform(Spell):
	Class, school, name = "Priest", "", "Shadowform"
	needTarget, mana = False, 3
	index = "Classic~Priest~Spell~3~~Shadowform"
	description = "Your Hero Power becomes 'Deal 2 damage'. If already in Shadowform: 3 damage"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		name = self.Game.heroPowers[self.ID].name
		power = MindShatter if name == "Mind Spike" or name == "Mind Shatter" else MindSpike
		power.replaceHeroPower()
		return None
		
class MindSpike(HeroPower):
	mana, name, needTarget = 2, "Mind Spike", True
	index = "Priest~Hero Power~2~Mind Spike"
	description = "Deal 2 damage"
	name_CN = "心灵尖刺"
	def text(self, CHN):
		damage = (2 + self.Game.status[self.ID]["Power Damage"]) * (2 ** self.countDamageDouble())
		return "造成%d点伤害"%damage if CHN else "Deal %d damage"%damage
		
	def effect(self, target, choice=0):
		damage = (2 + self.Game.playerStatus[self.ID]["Hero Power Damage Boost"]) * (2 ** self.countDamageDouble())
		dmgTaker, damageActual = self.dealsDamage(target, damage)
		if dmgTaker.health < 1 or dmgTaker.dead: return 1
		return 0
		
class MindShatter(HeroPower):
	mana, name, needTarget = 2, "Mind Shatter", True
	index = "Priest~Hero Power~2~Mind Shatter"
	description = "Deal 3 damage"
	name_CN = "心灵碎裂"
	def text(self, CHN):
		damage = (3 + self.Game.status[self.ID]["Power Damage"]) * (2 ** self.countDamageDouble())
		return "造成%d点伤害"%damage if CHN else "Deal %d damage"%damage
		
	def effect(self, target, choice=0):
		damage = (3 + self.Game.playerStatus[self.ID]["Hero Power Damage Boost"]) * (2 ** self.countDamageDouble())
		dmgTaker, damageActual = self.dealsDamage(target, damage)
		if dmgTaker.health < 1 or dmgTaker.dead: return 1
		return 0
		
"""Rogue Cards"""
class VanessaVanCleef(Minion):
	Class, race, name = "Rogue", "", "Vanessa VanCleef"
	mana, attack, health = 2, 2, 3
	index = "Core_2021~Rogue~Minion~2~2~3~~Vanessa VanCleef~Combo~Legendary"
	requireTarget, keyWord, description = False, "", "Combo: Add a copy of the last card your opponent played to your hand"
	name_CN = "梵妮莎 范克里夫"
	
	def effCanTrig(self):
		self.effectViable = self.Game.Counters.numCardsPlayedThisTurn[self.ID] > 0
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if self.Game.Counters.numCardsPlayedThisTurn[self.ID] > 0:
			try:
				index = self.Game.Counters.cardsPlayedThisGame[3-self.ID][-1]
				self.Game.Hand_Deck.addCardtoHand(self.Game.cardPool[index], self.ID, byType=True, creator=type(self))
			except: pass
		return None
		
		
class Assassinate(Spell):
	Class, school, name = "Rogue", "", "Assassinate"
	requireTarget, mana = True, 4
	index = "Core_2021~Rogue~Spell~4~~Assassinate"
	description = "Destroy an enemy minion"
	name_CN = "刺杀"
	def available(self):
		return self.selectableEnemyMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.ID != self.ID and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			self.Game.killMinion(self, target)
		return target
		
		
class TombPillager(Minion):
	Class, race, name = "Rogue", "", "Tomb Pillager"
	mana, attack, health = 4, 5, 4
	index = "Core_2021~Rogue~Minion~4~5~4~~Tomb Pillager~Deathrattle"
	requireTarget, keyWord, description = False, "", "Deathrattle: Add a Coin to your hand"
	name_CN = "盗墓匪贼"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [AddaCointoHand(self)]
		
class AddaCointoHand(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.Game.Hand_Deck.addCardtoHand(TheCoin, self.entity.ID, byType=True, creator=type(self.entity))
		
	def text(self, CHN):
		return "亡语：将一个幸运币置入你的手牌" if CHN else "Deathrattle: Add a Coin to your hand"
		
"""Shaman Cards"""
class NoviceZapper(Minion):
	Class, race, name = "Shaman", "", "Novice Zapper"
	mana, attack, health = 1, 3, 2
	index = "Core_2021~Shaman~Minion~1~3~2~~Novice Zapper~Spell Damage~Overload"
	requireTarget, keyWord, description = False, "Spell Damage", "Spell Damage +1. Overload: (1)"
	name_CN = "电击学徒"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.overload = 1
		
	
class FeralSpirit(Spell):
	Class, school, name = "Shaman", "", "Feral Spirit"
	requireTarget, mana = False, 3
	index = "Core_2021~Shaman~Spell~3~~Feral Spirit~Overload"
	description = "Summon two 2/3 Spirit Wolves with Taunt. Overload: (1)"
	name_CN = "野性狼魂"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.overload = 1
		
	def available(self):
		return self.Game.space(self.ID) > 0
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.Game.summon([SpiritWolf(self.Game, self.ID) for i in range(2)], (-1, "totheRightEnd"), self.ID)
		return None
		
class SpiritWolf(Minion):
	Class, race, name = "Shaman", "", "Spirit Wolf"
	mana, attack, health = 2, 2, 3
	index = "Core_2021~Shaman~Minion~2~2~3~~Spirit Wolf~Taunt~Uncollectible"
	requireTarget, keyWord, description = False, "Taunt", "Taunt"
	name_CN = "幽灵狼"
	
	
class LightningStorm(Spell):
	Class, school, name = "Shaman", "", "Lightning Storm"
	requireTarget, mana = False, 3
	index = "Classic~Shaman~Spell~3~Lightning Storm~Overload"
	description = "Deal 3 damage to all enemy minions. Overload: (2)"
	name_CN = "闪电风暴"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.overload = 2
		
	def text(self, CHN):
		damage = (3 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		return "对所有敌方随从造成%d点伤害。过载： (2)"%damage if CHN \
				else "Deal %d damage to all enemy minions. Overload: (2)"%damage
				
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		damage = (3 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		targets = self.Game.minionsonBoard(3-self.ID)
		self.dealsAOE(targets, [damage]*len(targets))
		return None
		
		
class EarthElemental(Minion):
	Class, race, name = "Shaman", "Elemental", "Earth Elemental"
	mana, attack, health = 5, 7, 8
	index = "Classic~Shaman~Minion~5~7~8~Elemental~Earth Elemental~Taunt~Overload"
	requireTarget, keyWord, description = False, "Taunt", "Taunt. Overload: (2)"
	name_CN = "土元素"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.overload = 2
		
"""Warlock Cards"""
class FelsoulJailer(Minion):
	Class, race, name = "Warlock", "Demon", "Felsoul Jailer"
	mana, attack, health = 5, 4, 6
	index = "Core_2021~Shaman~Minion~5~4~6~Demon~Felsoul Jailer~Battlecry~Deathrattle"
	requireTarget, keyWord, description = False, "", "Battlecry: Your opponent discards a minion. Deathrattle: Return it"
	name_CN = "邪魂狱卒"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [ReturnDiscardedEnemyMinion(self)]
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if curGame.mode == 0:
			if curGame.guides:
				i = curGame.guides.pop(0)
			else:
				minions = [i for i, card in enumerate(curGame.Hand_Deck.hands[3-self.ID]) if card.type == "Minion"]
				i = npchoice(minions) if minions else -1
				curGame.fixedGuides.append(i)
			if i > -1:
				minion = curGame.Hand_Deck.hands[3-self.ID][i]
				curGame.Hand_Deck.discardCard(3-self.ID, i)
				for trig in self.deathrattles:
					if isinstance(trig, ReturnDiscardedEnemyMinion):
						trig.discardedCard = type(minion)
		return None
		
class ReturnDiscardedEnemyMinion(Deathrattle_Minion):
	def __init__(self, entity):
		self.blank_init(entity)
		self.discardedCard = None
		
	def text(self, CHN):
		return "亡语：将%s返回对方手牌"%self.discardedCard.name if CHN \
				else "Deathrattle: Return the discarded card %s to opponent's hand"%self.discardedCard.name
				
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		if self.discardedCard:
			self.entity.Game.Hand_Deck.addCardtoHand(self.discardedCard, self.entity.ID, byType=True)
			
	def selfCopy(self, recipient):
		trig = type(self)(recipient)
		trig.discardedCard = self.discardedCard
		return trig
		
		