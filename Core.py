from CardTypes import *
from Triggers_Auras import *
from numpy.random import choice as npchoice
from numpy.random import randint as nprandint
from numpy.random import shuffle as npshuffle
from numpy import inf as npinf


from AcrossPacks import TheCoin, SilverHandRecruit, Treant_Classic, Treant_Classic_Taunt, \
						Frog, SpiritWolf, BloodFury, Infernal, Panther, \
						Snake, IllidariInitiate, ExcessMana, Bananas, Nerubian, \
						VioletApprentice, Imp, Hyena_Classic, BaineBloodhoof, Whelp, DruidoftheClaw_Charge, \
						DruidoftheClaw_Taunt, DruidoftheClaw_Both, Skeleton, Shadowbeast, Defender, Ashbringer, \
						Dream, Nightmare, YseraAwakens, LaughingSister, EmeraldDrake, Trig_WaterElemental


"""Neutral Cards"""

class MurlocTinyfin(Minion):
	Class, race, name = "Neutral", "Murloc", "Murloc Tinyfin"
	mana, attack, health = 0, 1, 1
	index = "CORE~Neutral~Minion~0~1~1~Murloc~Murloc Tinyfin"
	requireTarget, keyWord, description = False, "", ""
	name_CN = "鱼人宝宝"
	
"""Mana 1 Cards"""
class AbusiveSergeant(Minion):
	Class, race, name = "Neutral", "", "Abusive Sergeant"
	mana, attack, health = 1, 1, 1
	index = "CORE~Neutral~Minion~1~1~1~~Abusive Sergeant~Battlecry"
	requireTarget, keyWord, description = True, "", "Battlecry: Give a minion +2 Attack this turn"
	name_CN = "叫嚣的中士"
	
	def targetExists(self, choice=0):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target != self and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			target.buffDebuff(2, 0, "EndofTurn")
		return target
		
		
class ArcaneAnomaly(Minion):
	Class, race, name = "Neutral", "Elemental", "Arcane Anomaly"
	mana, attack, health = 1, 2, 1
	index = "CORE~Neutral~Minion~1~2~1~Elemental~Arcane Anomaly"
	requireTarget, keyWord, description = False, "", "After you cast a spell, give this minion +1 Health"
	name_CN = "狂野炎术师"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_ArcaneAnomaly(self)]
		
class Trig_ArcaneAnomaly(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["SpellBeenPlayed"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject.ID == self.entity.ID
		
	def text(self, CHN):
		return "在你施放一个法术后，该随从便获得+1生命值" if CHN else "After you cast a spell, give this minion +1 Health"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.buffDebuff(0, 1)
		
		
class ArgentSquire(Minion):
	Class, race, name = "Neutral", "", "Argent Squire"
	mana, attack, health = 1, 1, 1
	index = "CORE~Neutral~Minion~1~1~1~~Argent Squire~Divine Shield"
	requireTarget, keyWord, description = False, "Divine Shield", "Divine Shield"
	name_CN = "银色侍从"
	

class Cogmaster(Minion):
	Class, race, name = "Neutral", "", "Cogmaster"
	mana, attack, health = 1, 1, 2
	index = "CORE~Neutral~Minion~1~1~2~~Cogmaster"
	requireTarget, keyWord, description = False, "", "Has +2 Attack while you have a Mech"
	name_CN = "齿轮大师"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.auras["Buff Aura"] = StatAura_Cogmaster(self)
		
class StatAura_Cogmaster(HasAura_toMinion):
	def __init__(self, entity):
		self.entity = entity
		self.signals, self.auraAffected = ["MinionAppears", "MinionDisappears"], []
		self.on = False
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		obj = subject if signal == "MinionAppears" else target
		return self.entity.onBoard and obj.ID == self.entity.ID and obj.name == "Dread Raven" and obj != self.entity
		
	def trig(self, signal, ID, subject, target, number, comment, choice=0):
		minion = self.entity
		hasMech = any("Mech" in obj.race for obj in minion.Game.minionsonBoard(minion.ID))
		if not hasMech and self.on:
			self.on = False
			for recipient, receiver in self.auraAffected[:]:
				receiver.effectClear()
			self.auraAffected = []
		elif hasMech and not self.on:
			self.on = True
			Stat_Receiver(minion, self, 2, 0).effectStart()
			
	def auraAppears(self):
		minion = self.entity
		hasMech = any("Mech" in obj.race for obj in minion.Game.minionsonBoard(minion.ID))
		if hasMech:
			self.on = True
			Stat_Receiver(minion, self, 2, 0).effectStart()
		for sig in self.signals:
			try: minion.Game.trigsBoard[minion.ID][sig].append(self)
			except: minion.Game.trigsBoard[minion.ID][sig] = [self]
			
	def auraDisappears(self):
		for minion, receiver in self.auraAffected[:]:
			receiver.effectClear()
		self.auraAffected = []
		for sig in self.signals:
			try: self.entity.Game.trigsBoard[self.entity.ID][sig].remove(self)
			except: pass
			
	def selfCopy(self, recipient): #The recipientMinion is the minion that deals the Aura.
		#func that checks if subject is applicable will be the new copy's function
		return type(self)(recipient)
		
	def createCopy(self, game):
		if self not in game.copiedObjs: #这个光环没有被复制过
			entityCopy = self.entity.createCopy(game)
			Copy = self.selfCopy(entityCopy)
			game.copiedObjs[self] = Copy
			Copy.on = self.on
			for minion, receiver in self.auraAffected:
				minionCopy = minion.createCopy(game)
				index = minion.auraReceivers.index(receiver)
				receiverCopy = minionCopy.auraReceivers[index]
				receiverCopy.source = Copy #补上这个receiver的source
				Copy.auraAffected.append((minionCopy, receiverCopy))
			return Copy
		else:
			return game.copiedObjs[self]
			
			
class ElvenArcher(Minion):
	Class, race, name = "Neutral", "", "Elven Archer"
	mana, attack, health = 1, 1, 1
	index = "CORE~Neutral~Minion~1~1~1~~Elven Archer~Battlecry"
	requireTarget, keyWord, description = True, "", "Battlecry: Deal 1 damamge"
	name_CN = "精灵弓箭手"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			self.dealsDamage(target, 1) #dealsDamage() on targets in grave/deck will simply pass.
		return target
		
		
class MurlocTidecaller(Minion):
	Class, race, name = "Neutral", "Murloc", "Murloc Tidecaller"
	mana, attack, health = 1, 1, 2
	index = "CORE~Neutral~Minion~1~1~2~Murloc~Murloc Tidecaller"
	requireTarget, keyWord, description = False, "", "Whenever you summon a Murloc, gain +1 Attack"
	name_CN = "鱼人招潮者"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_MurlocTidecaller(self)]
		
class Trig_MurlocTidecaller(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["MinionSummoned"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject.ID == self.entity.ID and "Murloc" in subject.race and subject != self.entity
		
	def text(self, CHN):
		return "每当你召唤一个鱼人时，便获得+1攻击力" if CHN else "Whenever you summon a Murloc, gain +1 Attack"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.buffDebuff(1, 0)
		
		
class EmeraldSkytalon(Minion):
	Class, race, name = "Neutral", "Beast", "Emerald Skytalon"
	mana, attack, health = 1, 2, 1
	index = "CORE~Neutral~Minion~1~2~1~Beast~Emerald Skytalon~Rush"
	requireTarget, keyWord, description = False, "Rush", "Rush"
	name_CN = "翡翠天爪枭"
	
	
class VoodooDoctor(Minion):
	Class, race, name = "Neutral", "", "Voodoo Doctor"
	mana, attack, health = 1, 2, 1
	index = "CORE~Neutral~Minion~1~2~1~~Voodoo Doctor~Battlecry"
	requireTarget, keyWord, description = True, "", "Battlecry: Restore 2 health"
	name_CN = "巫医"
	
	def text(self, CHN):
		heal = 2 * (2 ** self.countHealDouble())
		return "战吼：恢复%d点生命值"%heal if CHN else "Battlecry: Restore %d health"%heal
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			heal = 2 * (2 ** self.countHealDouble())
			self.restoresHealth(target, heal)
		return target
		
		
class WorgenInfiltrator(Minion):
	Class, race, name = "Neutral", "", "Worgen Infiltrator"
	mana, attack, health = 1, 2, 1
	index = "CORE~Neutral~Minion~1~2~1~~Worgen Infiltrator~Stealth"
	requireTarget, keyWord, description = False, "Stealth", "Stealth"
	name_CN = "狼人渗透者"
	
	
class YoungPriestess(Minion):
	Class, race, name = "Neutral", "", "Young Priestess"
	mana, attack, health = 1, 2, 1
	index = "CORE~Neutral~Minion~1~2~1~~Young Priestess"
	requireTarget, keyWord, description = False, "", "At the end of your turn, give another random friendly minion +1 Health"
	name_CN = "年轻的女祭司"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_YoungPriestess(self)]
		
class Trig_YoungPriestess(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["TurnEnds"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and ID == self.entity.ID
		
	def text(self, CHN):
		return "在你的回合结束时，随机使另一个友方随从获得+1生命值" if CHN else "At the end of your turn, give another random friendly minion +1 Health"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		curGame = self.entity.Game
		if curGame.mode == 0:
			if curGame.guides:
				i = curGame.guides.pop(0)
			else:
				minions = curGame.minionsonBoard(self.entity.ID)
				try: minions.remove(self.entity)
				except: pass
				i = npchoice(minions).pos if minions else -1
				curGame.fixedGuides.append(i)
			if i > -1:
				minion = curGame.minions[self.entity.ID][i]
				minion.buffDebuff(0, 1)
				
"""Mana 2 Cards"""
class AcidicSwampOoze(Minion):
	Class, race, name = "Neutral", "", "Acidic Swamp Ooze"
	mana, attack, health = 2, 3, 2
	index = "CORE~Neutral~Minion~2~3~2~~Acidic Swamp Ooze~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Destroy you opponent's weapon"
	name_CN = "酸性沼泽软泥怪"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		for weapon in self.Game.weapons[3-self.ID]:
			weapon.destroyed()
		return None
		
		
class AnnoyoTron(Minion):
	Class, race, name = "Neutral", "Mech", "Annoy-o-Tron"
	mana, attack, health = 2, 1, 2
	index = "CORE~Neutral~Minion~2~1~2~Mech~Annoy-o-Tron~Taunt~Divine Shield"
	requireTarget, keyWord, description = False, "Taunt,Divine Shield", "Taunt. Divine Shield"
	name_CN = "吵吵机器人"
	
	
class BloodmageThalnos(Minion):
	Class, race, name = "Neutral", "", "Bloodmage Thalnos"
	mana, attack, health = 2, 1, 1
	index = "CORE~Neutral~Minion~2~1~1~~Bloodmage Thalnos~Deathrattle~Spell Damage~Legendary"
	requireTarget, keyWord, description = False, "Spell Damage", "Spell Damage +1. Deathrattle: Draw a card"
	name_CN = "血法师萨尔诺斯"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.deathrattles = [DrawaCard(self)]
		
class DrawaCard(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.Game.Hand_Deck.drawCard(self.entity.ID)
		
	def text(self, CHN):
		return "亡语：抽一张牌" if CHN else "Deathrattle: Draw a card"
		
		

class BloodsailRaider(Minion):
	Class, race, name = "Neutral", "Pirate", "Bloodsail Raider"
	mana, attack, health = 2, 2, 3
	index = "CORE~Neutral~Minion~2~2~3~Pirate~Bloodsail Raider~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Gain Attack equal to the Attack of your weapon"
	name_CN = "血帆袭击者"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		weapon = self.Game.availableWeapon(self.ID)
		if weapon:
			self.buffDebuff(weapon.attack, 0)
		return None
		
		
class RedgillRazorjaw(Minion):
	Class, race, name = "Neutral", "Murloc", "Redgill Razorjaw"
	mana, attack, health = 2, 3, 1
	index = "CORE~Neutral~Minion~2~3~1~Murloc~Redgill Razorjaw~Rush"
	requireTarget, keyWord, description = False, "Rush", "Rush"
	name_CN = "红鳃锋颚战士"
	
	
class CrazedAlchemist(Minion):
	Class, race, name = "Neutral", "", "Crazed Alchemist"
	mana, attack, health = 2, 2, 2
	index = "CORE~Neutral~Minion~2~2~2~~Crazed Alchemist~Battlecry"
	requireTarget, keyWord, description = True, "", "Battlecry: Swap the Attack and Health of a minion"
	name_CN = "疯狂的炼金师"
	
	def targetExists(self, choice=0):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target != self and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			target.statReset(target.health, target.attack)
		return target
		
		
class DireWolfAlpha(Minion):
	Class, race, name = "Neutral", "Beast", "Dire Wolf Alpha"
	mana, attack, health = 2, 2, 2
	index = "CORE~Neutral~Minion~2~2~2~Beast~Dire Wolf Alpha"
	requireTarget, keyWord, description = False, "", "Adjacent minions have +1 Attack"
	name_CN = "恐狼先锋"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.auras["Adjacent minions have +1 Attack"] = StatAura_Adjacent(self, 1, 0)
		
		
class ExplosiveSheep(Minion):
	Class, race, name = "Neutral", "Mech", "Explosive Sheep"
	mana, attack, health = 2, 1, 1
	index = "CORE~Neutral~Minion~2~1~1~Mech~Explosive Sheep~Deathrattle"
	requireTarget, keyWord, description = False, "", "Deathrattle: Deal 2 damage to all minions"
	name_CN = "自爆绵羊"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.deathrattles = [Deal2DamagetoAllMinions(self)]
		
class Deal2DamagetoAllMinions(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		targets = self.entity.Game.minionsonBoard(1) + self.entity.Game.minionsonBoard(2)
		self.entity.dealsAOE(targets, [2]*len(targets))
		
	def text(self, CHN):
		return "亡语：对所有随从造成2点伤害" if CHN else "Deathrattle: Deal 2 damage to all minions"
		
		
class FogsailFreebooter(Minion):
	Class, race, name = "Neutral", "Pirate", "Fogsail Freebooter"
	mana, attack, health = 2, 2, 2
	index = "CORE~Neutral~Minion~2~2~2~Pirate~Fogsail Freebooter~Battlecry"
	requireTarget, keyWord, description = True, "", "Battlecry: If you have a weapon equipped, deal 2 damage"
	name_CN = "雾帆劫掠者"
	
	def returnTrue(self, choice=0):
		return self.Game.availableWeapon(self.ID) is not None
		
	def effCanTrig(self):
		self.effectViable = self.Game.availableWeapon(self.ID) is not None
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target and self.Game.availableWeapon(self.ID) is not None:
			self.dealsDamage(target, 2)
		return target
		
		
class NerubianEgg(Minion):
	Class, race, name = "Neutral", "", "Nerubian Egg"
	mana, attack, health = 2, 0, 2
	index = "CORE~Neutral~Minion~2~0~2~~Nerubian Egg~Deathrattle"
	requireTarget, keyWord, description = False, "", "Deathrattle: Summon a 4/4 Nerubian"
	name_CN = "蛛魔之卵"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.deathrattles = [Summona44Nerubian(self)]
		
class Summona44Nerubian(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		minion = self.entity
		minion.Game.summon(Nerubian(minion.Game, minion.ID), minion.pos+1, minion)
		
	def text(self, CHN):
		return "亡语：召唤一个4/4的蛛魔" if CHN else "Deathrattle: Summon a 4/4 Nerubian"
		
	
class RiverCrocolisk(Minion):
	Class, race, name = "Neutral", "Beast", "River Crocolisk"
	mana, attack, health = 2, 2, 3
	index = "CORE~Neutral~Minion~2~2~3~Beast~River Crocolisk"
	requireTarget, keyWord, description = False, "", ""
	name_CN = "淡水鳄"
	
	
class SunreaverSpy(Minion):
	Class, race, name = "Neutral", "", "Sunreaver Spy"
	mana, attack, health = 2, 2, 3
	index = "CORE~Neutral~Minion~2~2~3~~Sunreaver Spy~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: If you control a Secret, gain +1/+1"
	name_CN = "夺日者间谍"
	
	def effCanTrig(self):
		self.effectViable = self.Game.Secrets.secrets[self.ID] != []
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if self.Game.Secrets.secrets[self.ID] != []:
			self.buffDebuff(1, 1)
		return None
		
		
class Toxicologist(Minion):
	Class, race, name = "Neutral", "", "Toxicologist"
	mana, attack, health = 2, 2, 2
	index = "CORE~Neutral~Minion~2~2~2~~Toxicologist~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Give your weapon +1 Attack"
	name_CN = "毒物学家"
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		weapon = self.Game.availableWeapon(self.ID)
		if weapon: weapon.gainStat(1, 0)
		return None
		
		
class YouthfulBrewmaster(Minion):
	Class, race, name = "Neutral", "", "Youthful Brewmaster"
	mana, attack, health = 2, 3, 2
	index = "CORE~Neutral~Minion~2~3~2~~Youthful Brewmaster~Battlecry"
	requireTarget, keyWord, description = True, "", "Battlecry: Return a friendly minion from the battlefield to you hand"
	name_CN = "年轻的酒仙"
	
	def targetExists(self, choice=0):
		return self.selectableFriendlyMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.ID == self.ID and target != self and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target and target.onBoard:
			self.Game.returnMiniontoHand(target)
		return target
		
		
"""Mana 3 Cards"""
class Brightwing(Minion):
	Class, race, name = "Neutral", "Dragon", "Brightwing"
	mana, attack, health = 3, 3, 2
	index = "CORE~Neutral~Minion~3~3~2~Dragon~Brightwing~Battlecry~Legendary"
	requireTarget, keyWord, description = False, "", "Battlecry: Add a random Legendary minion to your hand"
	name_CN = "光明之翼"
	poolIdentifier = "Legendary Minions"
	@classmethod
	def generatePool(cls, pools):
		return "Legendary Minions", list(pools.LegendaryMinions.values())
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if curGame.mode == 0:
			pool = tuple(self.rngPool("Legendary Minions"))
			if curGame.guides:
				minion = curGame.guides.pop(0)
			else:
				minion = npchoice(pool)
				curGame.fixedGuides.append(minion)
			curGame.Hand_Deck.addCardtoHand(minion, self.ID, byType=True, creator=type(self), possi=pool)
		return None
		
		
class ColdlightSeer(Minion):
	Class, race, name = "Neutral", "Murloc", "Coldlight Seer"
	mana, attack, health = 3, 2, 3
	index = "CORE~Neutral~Minion~3~2~3~Murloc~Coldlight Seer~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Give your other Murlocs +2 Health"
	name_CN = "寒光先知"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		for minion in self.Game.minionsonBoard(self.ID):
			if "Murloc" in minion.race: minion.buffDebuff(0, 2)
		return None
		
		
class EarthenRingFarseer(Minion):
	Class, race, name = "Neutral", "", "Earthen Ring Farseer"
	mana, attack, health = 3, 3, 3
	index = "CORE~Neutral~Minion~3~3~3~~Earthen Ring Farseer~Battlecry"
	requireTarget, keyWord, description = True, "", "Battlecry: Restore 3 health"
	name_CN = "大地之环先知"
	
	def text(self, CHN):
		heal = 3 * (2 ** self.countHealDouble())
		return "战吼：恢复%d点生命值"%heal if CHN else "Battlecry: Restore %d health"%heal
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			heal = 3 * (2 ** self.countHealDouble())
			self.restoresHealth(target, heal)
		return target
		
		
class FlesheatingGhoul(Minion):
	Class, race, name = "Neutral", "", "Flesheating Ghoul"
	mana, attack, health = 3, 3, 3
	index = "CORE~Neutral~Minion~3~3~3~~Flesheating Ghoul"
	requireTarget, keyWord, description = False, "", "Whenever a minion dies, gain +1 Attack"
	name_CN = "腐肉食尸鬼"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_FlesheatingGhoul(self)]
		
class Trig_FlesheatingGhoul(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["MinionDies"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and target != self.entity #Technically, minion has to disappear before dies. But just in case.
		
	def text(self, CHN):
		return "每当一个随从死亡，便获得+1攻击力" if CHN else "Whenever a minion dies, gain +1 Attack"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.buffDebuff(1, 0)
		
		
class HumongousRazorleaf(Minion):
	Class, race, name = "Neutral", "", "Humongous Razorleaf"
	mana, attack, health = 3, 4, 8
	index = "CORE~Neutral~Minion~3~4~8~~Humongous Razorleaf"
	requireTarget, keyWord, description = False, "", "Can't Attack"
	name_CN = "巨齿刀叶"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.marks["Can't Attack"] = 1
		
		
class IceRager(Minion):
	Class, race, name = "Neutral", "Elemental", "Ice Rager"
	mana, attack, health = 3, 5, 2
	index = "CORE~Neutral~Minion~3~5~2~Elemental~Ice Rager"
	requireTarget, keyWord, description = False, "", ""
	name_CN = "冰霜暴怒者"
	
	
class InjuredBlademaster(Minion):
	Class, race, name = "Neutral", "", "Injured Blademaster"
	mana, attack, health = 3, 4, 7
	index = "CORE~Neutral~Minion~3~4~7~~Injured Blademaster~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Deal 4 damage to HIMSELF"
	name_CN = "负伤剑圣"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.dealsDamage(self, 4)
		return None
		
		

class IronbeakOwl(Minion):
	Class, race, name = "Neutral", "Beast", "Ironbeak Owl"
	mana, attack, health = 3, 2, 1
	index = "CORE~Neutral~Minion~3~2~1~Beast~Ironbeak Owl~Battlecry"
	requireTarget, keyWord, description = True, "", "Battlecry: Silence a minion"
	name_CN = "铁喙猫头鹰"
	
	def targetExists(self, choice=0):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target != self and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			target.getsSilenced()
		return target
		
		
class JunglePanther(Minion):
	Class, race, name = "Neutral", "Beast", "Jungle Panther"
	mana, attack, health = 3, 4, 2
	index = "CORE~Neutral~Minion~3~4~2~Beast~Jungle Panther~Stealth"
	requireTarget, keyWord, description = False, "Stealth", "Stealth"
	name_CN = "丛林猎豹"
	
	
class KingMukla(Minion):
	Class, race, name = "Neutral", "Beast", "King Mukla"
	mana, attack, health = 3, 5, 5
	index = "CORE~Neutral~Minion~3~5~5~Beast~King Mukla~Battlecry~Legendary"
	requireTarget, keyWord, description = False, "", "Battlecry: Give your opponent 2 Bananas"
	name_CN = "穆克拉"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if self.Game.Hand_Deck.handNotFull(3-self.ID):
			self.Game.Hand_Deck.addCardtoHand([Bananas, Bananas], 3-self.ID, byType=True, creator=type(self))
		return None
		
		
class LoneChampion(Minion):
	Class, race, name = "Neutral", "", "Lone Champion"
	mana, attack, health = 3, 2, 4
	index = "CORE~Neutral~Minion~3~2~4~~Lone Champion~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: If you control no other minions, gain Taunt and Divine Shield"
	name_CN = "孤胆英雄"
	
	def effCanTrig(self):
		self.effectViable = self.Game.minionsonBoard(self.ID) == []
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if len(self.Game.minionsonBoard(self.ID)) < 2:
			self.getsStatus("Taunt")
			self.getsStatus("Divine Shield")
		return None
		
		
class MiniMage(Minion):
	Class, race, name = "Neutral", "", "Mini-Mage"
	mana, attack, health = 3, 3, 1
	index = "CORE~Neutral~Minion~3~3~1~~Mini-Mage~Stealth~Spell Damage"
	requireTarget, keyWord, description = False, "Stealth,Spell Damage", "Stealth, Spell Damage +1"
	name_CN = "小个子法师"
	
	
class RaidLeader(Minion):
	Class, race, name = "Neutral", "", "Raid Leader"
	mana, attack, health = 3, 2, 3
	index = "CORE~Neutral~Minion~3~2~3~~Raid Leader"
	requireTarget, keyWord, description = False, "", "Your other minions have +1 Attack"
	name_CN = "团队领袖"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.auras["Your other minions have +1 Attack"] = StatAura_Others(self, 1, 0)
		
		
class SouthseaCaptain(Minion):
	Class, race, name = "Neutral", "Pirate", "Southsea Captain"
	mana, attack, health = 3, 3, 3
	index = "CORE~Neutral~Minion~3~3~3~Pirate~Southsea Captain"
	requireTarget, keyWord, description = False, "", "Your other Pirates have +1/+1"
	name_CN = "南海船长"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.auras["Your other Pirates have +1/+1"] = StatAura_Others(self, 1, 1)
		
	def applicable(self, target):
		return "Pirate" in target.race
		
		
class SpiderTank(Minion):
	Class, race, name = "Neutral", "Mech", "Spider Tank"
	mana, attack, health = 3, 3, 4
	index = "CORE~Neutral~Minion~3~3~4~Mech~Spider Tank"
	requireTarget, keyWord, description = False, "", ""
	name_CN = "蜘蛛坦克"
	
	
class StoneskinBasilisk(Minion):
	Class, race, name = "Neutral", "Beast", "Stoneskin Basilisk"
	mana, attack, health = 3, 1, 1
	index = "CORE~Neutral~Minion~3~1~1~Beast~Stoneskin Basilisk~Divine Shield~Poisonous"
	requireTarget, keyWord, description = False, "Divine Shield,Poisonous", "Divine Shield, Poisonous"
	name_CN = "石皮蜥蜴"
	
"""Mana 4 Cards"""
class BaronRivendare(Minion):
	Class, race, name = "Neutral", "", "Baron Rivendare"
	mana, attack, health = 4, 1, 7
	index = "CORE~Neutral~Minion~4~1~7~~Baron Rivendare~Legendary"
	requireTarget, keyWord, description = False, "", "Your minions trigger their Deathrattles twice"
	name_CN = "矮人神射手"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.auras["Your minions trigger their Deathrattles twice"] = GameRuleAura_BaronRivendare(self)
		
class GameRuleAura_BaronRivendare(GameRuleAura):
	def auraAppears(self):
		self.entity.Game.status[self.entity.ID]["Deathrattle x2"] += 1
		
	def auraDisappears(self):
		self.entity.Game.status[self.entity.ID]["Deathrattle x2"] -= 1
		
		
class BigGameHunter(Minion):
	Class, race, name = "Neutral", "", "Big Game Hunter"
	mana, attack, health = 4, 4, 2
	index = "CORE~Neutral~Minion~4~4~2~~Big Game Hunter~Battlecry"
	requireTarget, keyWord, description = True, "", "Battlecry: Destroy a minion with 7 or more Attack"
	name_CN = "王牌猎人"
	
	def targetExists(self, choice=0):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target != self and target.attack > 6 and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			self.Game.killMinion(self, target)
		return target
		
		
class ChillwindYeti(Minion):
	Class, race, name = "Neutral", "", "Chillwind Yeti"
	mana, attack, health = 4, 4, 5
	index = "CORE~Neutral~Minion~4~4~5~~Chillwind Yeti"
	requireTarget, keyWord, description = False, "", ""
	name_CN = "冰风雪人"
	
	
class DarkIronDwarf(Minion):
	Class, race, name = "Neutral", "", "Dark Iron Dwarf"
	mana, attack, health = 4, 4, 4
	index = "CORE~Neutral~Minion~4~4~4~~Dark Iron Dwarf~Battlecry"
	requireTarget, keyWord, description = True, "", "Battlecry: Give a minion +2 Attack"
	name_CN = "黑铁矮人"
	
	def targetExists(self, choice=0):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target != self and target.onBoard
		
	#手牌中的随从也会受到临时一回合的加攻，回合结束时消失。
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			target.buffDebuff(2, 0, "EndofTurn")
		return target
		
		
class DefenderofArgus(Minion):
	Class, race, name = "Neutral", "", "Defender of Argus"
	mana, attack, health = 4, 3, 3
	index = "CORE~Neutral~Minion~4~3~3~~Defender of Argus~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Given adjacent minions +1/+1 and Taunt"
	name_CN = "阿古斯防御者"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if self.onBoard:
			for minion in self.Game.neighbors2(self)[0]:
				minion.buffDebuff(1, 1)
				minion.getsStatus("Taunt")
		return None
		
		
class GrimNecromancer(Minion):
	Class, race, name = "Neutral", "", "Grim Necromancer"
	mana, attack, health = 4, 2, 4
	index = "CORE~Neutral~Minion~4~2~4~~Grim Necromancer~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Summon two 1/1 Skeletons"
	name_CN = "冷酷的死灵法师"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		pos = (self.pos, "leftandRight") if self.onBoard else (-1, "totheRightEnd")
		self.Game.summon([Skeleton(self.Game, self.ID) for i in range(2)], pos, self)
		return None
		
	
class SenjinShieldmasta(Minion):
	Class, race, name = "Neutral", "", "Sen'jin Shieldmasta"
	mana, attack, health = 4, 3, 5
	index = "CORE~Neutral~Minion~4~3~5~~Sen'jin Shieldmasta~Taunt"
	requireTarget, keyWord, description = False, "Taunt", "Taunt"
	name_CN = "森金持盾卫士"
	
	
class VioletTeacher(Minion):
	Class, race, name = "Neutral", "", "Violet Teacher"
	mana, attack, health = 4, 3, 5
	index = "CORE~Neutral~Minion~4~3~5~~Violet Teacher"
	requireTarget, keyWord, description = False, "", "Whenever you cast a spell, summon a 1/1 Violet Apperentice"
	name_CN = "紫罗兰教师"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_VioletTeacher(self)]
		
class Trig_VioletTeacher(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["SpellPlayed"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject.ID == self.entity.ID
		
	def text(self, CHN):
		return "每当你施放一个法术，召唤一个1/1的紫罗兰学徒" if CHN else "Whenever you cast a spell, summon a 1/1 Violet Apperentice"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.Game.summon(VioletApprentice(self.entity.Game, self.entity.ID), self.entity.pos+1, self.entity)
		

class FacelessManipulator(Minion):
	Class, race, name = "Neutral", "", "Faceless Manipulator"
	mana, attack, health = 5, 3, 3
	index = "CORE~Neutral~Minion~5~3~3~~Faceless Manipulator~Battlecry"
	requireTarget, keyWord, description = True, "", "Battlecry: Choose a minion and become a copy of it"
	name_CN = "无面操纵者"
	
	def targetExists(self, choice=0):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target != self and target.onBoard
		
	#无面上场时，先不变形，正常触发Illidan的召唤，以及飞刀。之后进行判定。如果无面在战吼触发前死亡，则没有变形发生。
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		#目前只有打随从从手牌打出或者被沙德沃克调用可以触发随从的战吼。这些手段都要涉及self.Game.minionPlayed
		#如果self.Game.minionPlayed不再等于自己，说明这个随从的已经触发了变形而不会再继续变形。
		if target and not self.dead and self.Game.minionPlayed == self and (self.onBoard or self.inHand): #战吼触发时自己不能死亡。
			Copy = target.selfCopy(self.ID, self) if (target.onBoard or target.inHand) and self.onBoard else type(target)(self.Game, self.ID)
			self.Game.transform(self, Copy)
		return target
		
		
"""Mana 5 Cards"""
class GurubashiBerserker(Minion):
	Class, race, name = "Neutral", "", "Gurubashi Berserker"
	mana, attack, health = 5, 2, 8
	index = "CORE~Neutral~Minion~5~2~8~~Gurubashi Berserker"
	requireTarget, keyWord, description = False, "", "Whenever this minion takes damage, gain +3 Attack"
	name_CN = "古拉巴什狂暴者"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_GurubashiBerserker(self)]
		
class Trig_GurubashiBerserker(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["MinionTakesDmg"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return target == self.entity and self.entity.onBoard
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.buffDebuff(3, 0)
		
	def text(self, CHN):
		return "每当该随从受到伤害，便获得+3攻击力" if CHN else "Whenever this minion takes damage, gain +3 Attack"
		
		
class OverlordRunthak(Minion):
	Class, race, name = "Neutral", "", "Overlord Runthak"
	mana, attack, health = 5, 3, 6
	index = "CORE~Neutral~Minion~5~3~6~~Overlord Runthak~Rush~Legendary"
	requireTarget, keyWord, description = False, "Rush", "Rush. Whenever this minion attacks, give +1/+1 to all minions in your hand"
	name_CN = "伦萨克大王"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_OverlordRunthak(self)]
		
class Trig_OverlordRunthak(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["MinionAttackingMinion", "MinionAttackingHero"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject == self.entity and self.entity.onBoard
		
	def text(self, CHN):
		return "每当该随从攻击时，使你手牌中的所有随从获得+1/+1" if CHN \
				else "Whenever this minion attacks, give +1/+1 to all minions in your hand"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		for card in self.entity.Game.Hand_Deck.hands[self.entity.ID]:
			if card.type == "Minion": card.buffDebuff(1, 1)
			
			
class StranglethornTiger(Minion):
	Class, race, name = "Neutral", "Beast", "Stranglethorn Tiger"
	mana, attack, health = 5, 5, 5
	index = "CORE~Neutral~Minion~5~5~5~Beast~Stranglethorn Tiger~Stealth"
	requireTarget, keyWord, description = False, "Stealth", "Stealth"
	name_CN = "荆棘谷猛虎"
	
	
class TaelanFordring(Minion):
	Class, race, name = "Neutral", "", "Taelan Fordring"
	mana, attack, health = 5, 3, 3
	index = "CORE~Neutral~Minion~5~3~3~~Taelan Fordring~Taunt~Divine Shield~Deathrattle~Legendary"
	requireTarget, keyWord, description = False, "Taunt,Divine Shield", "Taunt, Divine Shield. Deathrattle: Draw your hightest-Cost minion"
	name_CN = "泰兰·弗丁"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.deathrattles = [DrawYourHighestCostMinion(self)]
		
class DrawYourHighestCostMinion(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		curGame = self.entity.Game
		if curGame.mode == 0:
			if curGame.guides:
				i = curGame.guides.pop(0)
			else:
				cards, highestCost = [], -npinf
				for i, card in enumerate(curGame.Hand_Deck.decks[self.entity.ID]):
					if card.mana > highestCost: cards, highestCost = [i], card.mana
					elif card.mana == highestCost: cards.append(i)
				i = npchoice(cards) if cards else -1
				curGame.fixedGuides.append(i)
			if i > -1:
				curGame.Hand_Deck.drawCard(self.entity.ID, i)
		return None
		
	def text(self, CHN):
		return "亡语：抽取你的法力值消耗最高的随从牌" if CHN else "Deathrattle: Draw your hightest-Cost minion"
		
"""Mana 6 Cards"""
class CairneBloodhoof(Minion):
	Class, race, name = "Neutral", "", "Cairne Bloodhoof"
	mana, attack, health = 6, 5, 5
	index = "CORE~Neutral~Minion~6~5~5~~Cairne Bloodhoof~Deathrattle~Legendary"
	requireTarget, keyWord, description = False, "", "Deathrattle: Summon a 4/5 Baine Bloodhoof"
	name_CN = "凯恩·血蹄"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.deathrattles = [SummonBaineBloodhoof(self)]
		
class SummonBaineBloodhoof(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.Game.summon(BaineBloodhoof(self.entity.Game, self.entity.ID), self.entity.pos+1, self.entity)
		
	def text(self, CHN):
		return "亡语：召唤一个4/5的贝恩·血蹄" if CHN else "Deathrattle: Summon a 4/5 Baine Bloodhoof"
		
		
class HighInquisitorWhitemane(Minion):
	Class, race, name = "Neutral", "", "High Inquisitor Whitemane"
	mana, attack, health = 6, 5, 7
	index = "CORE~Neutral~Minion~6~5~7~~High Inquisitor Whitemane~Battlecry~Legendary"
	requireTarget, keyWord, description = False, "", "Battlecry: Summon all friendly minions that died this turn"
	name_CN = "大检察官怀特迈恩"
	
	def effCanTrig(self):
		self.effectViable = self.Game.Counters.minionsDiedThisTurn[self.ID] != []
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if curGame.mode == 0:
			if curGame.guides:
				minions = curGame.guides.pop(0)
			else:
				minionsDied = curGame.Counters.minionsDiedThisTurn[self.ID]
				numSummon = min(curGame.space(self.ID), len(minionsDied))
				if numSummon: #假设召唤顺序是随机的
					minions = [curGame.cardPool[index] for index in npchoice(minionsDied, numSummon, replace=False)]
				else:
					minions = []
				curGame.fixedGuides.append(tuple(minions))
			if minions:
				pos = (self.pos, "totheRight") if self.onBoard else (-1, "totheRightEnd")
				curGame.summon([minion(curGame, self.ID) for minion in minions], pos, self)
		return None
		
"""Mana 7 Cards"""
class BaronGeddon(Minion):
	Class, race, name = "Neutral", "Elemental", "Baron Geddon"
	mana, attack, health = 7, 7, 7
	index = "CORE~Neutral~Minion~7~7~7~Elemental~Baron Geddon~Legendary"
	requireTarget, keyWord, description = False, "", "At the end of turn, deal 2 damage to ALL other characters"
	name_CN = "迦顿男爵"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_BaronGeddon(self)]
		
class Trig_BaronGeddon(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["TurnEnds"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and ID == self.entity.ID
		
	def text(self, CHN):
		return "在你的回合结束时，对所有其他角色造成2点伤害" if CHN else "At the end of turn, deal 2 damage to ALL other characters"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		minion = self.entity
		targets = [minion.Game.heroes[1], minion.Game.heroes[2]] + minion.Game.minionsonBoard(minion.ID, minion) + minion.Game.minionsonBoard(3-minion.ID)
		minion.dealsAOE(targets, [2]*len(targets))
		
		
class BarrensStablehand(Minion):
	Class, race, name = "Neutral", "", "Barrens Stablehand"
	mana, attack, health = 7, 5, 5
	index = "CORE~Neutral~Minion~7~5~5~~Barrens Stablehand~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Summon a random Beast"
	name_CN = "贫瘠之地饲养员"
	poolIdentifier = "Beasts to Summon"
	@classmethod
	def generatePool(cls, pools):
		return "Beasts to Summon", list(pools.MinionswithRace["Beast"].values())
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if curGame.mode == 0:
			if curGame.guides:
				beast = curGame.guides.pop(0)
			else:
				beast = npchoice(self.rngPool("Beasts to Summon"))
				curGame.fixedGuides.append(beast)
			curGame.summon(beast(curGame, self.ID), self.pos+1, self)
		return None
		
		
class NozdormutheEternal(Minion):
	Class, race, name = "Neutral", "Dragon", "Nozdormu the Eternal"
	mana, attack, health = 7, 8, 8
	index = "CORE~Neutral~Minion~7~8~8~Dragon~Nozdormu the Eternal~Legendary"
	requireTarget, keyWord, description = False, "", "Start of Game: If this is in BOTH players' decks, turns are only 15 seconds long"
	name_CN = "永恒者诺兹多姆"
	
	
class Stormwatcher(Minion):
	Class, race, name = "Neutral", "Elemental", "Stormwatcher"
	mana, attack, health = 7, 4, 8
	index = "CORE~Neutral~Minion~7~4~8~Elemental~Stormwatcher~Windfury"
	requireTarget, keyWord, description = False, "Windfury", "Windfury"
	name_CN = "风暴看守"
	
	
class StormwindChampion(Minion):
	Class, race, name = "Neutral", "", "Stormwind Champion"
	mana, attack, health = 7, 7, 7
	index = "CORE~Neutral~Minion~7~7~7~~Stormwind Champion"
	requireTarget, keyWord, description = False, "", "Your other minions have +1/+1"
	name_CN = "暴风城勇士"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.auras["Your other minions have +1/+1"] = StatAura_Others(self, 1, 1)
		
"""Mana +8 Cards"""
class ArcaneDevourer(Minion):
	Class, race, name = "Neutral", "Elemental", "Arcane Devourer"
	mana, attack, health = 8, 4, 8
	index = "CORE~Neutral~Minion~8~4~8~Elemental~Arcane Devourer"
	requireTarget, keyWord, description = False, "", "Whenever you cast a spell, gain +2/+2"
	name_CN = "奥术吞噬者"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_ArcaneDevourer(self)]
		
class Trig_ArcaneDevourer(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["SpellPlayed"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject.ID == self.entity.ID
		
	def text(self, CHN):
		return "每当你施放一个法术便获得+2/+2" if CHN else "Whenever you cast a spell, gain +2/+2"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.buffDebuff(2, 2)
		
		
class MalygostheSpellweaver(Minion):
	Class, race, name = "Neutral", "Dragon", "Malygos the Spellweaver"
	mana, attack, health = 9, 4, 12
	index = "CORE~Neutral~Minion~9~4~12~Dragon~Malygos the Spellweaver~Battlecry~Legendary"
	requireTarget, keyWord, description = False, "", "Battlecry: Draw spells until your hand is full"
	name_CN = "织法者玛里苟斯"
	
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
		
		
class OnyxiatheBroodmother(Minion):
	Class, race, name = "Neutral", "Dragon", "Onyxia the Broodmother"
	mana, attack, health = 9, 8, 8
	index = "CORE~Neutral~Minion~9~8~8~Dragon~Onyxia the Broodmother~Legendary"
	requireTarget, keyWord, description = False, "", "At the end of your turn, fill your board with 1/1 Whelps"
	name_CN = "龙巢之母奥妮克希亚"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_OnyxiatheBroodmother(self)]
		
class Trig_OnyxiatheBroodmother(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["TurnEnds"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and ID == self.entity.ID
		
	def text(self, CHN):
		return "在你的回合结束时，召唤数条1/1的雏龙，直到你的随从数量达到上限" if CHN \
				else "At the end of your turn, fill your board with 1/1 Whelps"
				
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		minion = self.entity
		minion.Game.summon([Whelp(minion.Game, minion.ID) for i in range(6)], (minion.pos, "leftandRight"), minion)


class SleepyDragon(Minion):
	Class, race, name = "Neutral", "Dragon", "Sleepy Dragon"
	mana, attack, health = 9, 4, 12
	index = "CORE~Neutral~Minion~9~4~12~Dragon~Sleepy Dragon~Taunt"
	requireTarget, keyWord, description = False, "Taunt", "Taunt"
	name_CN = "贪睡巨龙"
	
	
class YseratheDreamer(Minion):
	Class, race, name = "Neutral", "Dragon", "Ysera the Dreamer"
	mana, attack, health = 9, 4, 12
	index = "CORE~Neutral~Minion~9~4~12~Dragon~Ysera the Dreamer~Battlecry~Legendary"
	requireTarget, keyWord, description = False, "", "Battlecry: Add one of each Dream card to your hand"
	name_CN = "沉睡者伊瑟拉"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.Game.Hand_Deck.addCardtoHand([Dream, Nightmare, YseraAwakens, LaughingSister, EmeraldDrake], self.ID, byType=True, creator=type(self))
		return None
		

"""Mana 10 Cards"""
class DeathwingtheDestroyer(Minion):
	Class, race, name = "Neutral", "Dragon", "Deathwing the Destroyer"
	mana, attack, health = 10, 12, 12
	index = "CORE~Neutral~Minion~10~12~12~Dragon~Deathwing the Destroyer~Battlecry~Legendary"
	requireTarget, keyWord, description = False, "", "Battlecry: Destroy all other minions. Discard a card for each destroyed"
	name_CN = "灭世者死亡之翼"
	
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
				if i > -1: curGame.Hand_Deck.discard(self.ID, i)
				else: break
		return None
		
		
class ClockworkGiant(Minion):
	Class, race, name = "Neutral", "Mech", "Clockwork Giant"
	mana, attack, health = 12, 8, 8
	index = "CORE~Neutral~Minion~12~8~8~Mech~Clockwork Giant"
	needTarget, keyWord, description = False, "", "Costs (1) less for each other card in your opponent's hand"
	name_CN = "发条巨人"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsHand = [Trigger_ClockworkGiant(self)]
		
	def selfManaChange(self):
		if self.inHand:
			self.mana -= len(self.Game.Hand_Deck.hands[3-self.ID])
			self.mana = max(0, self.mana)
			
class Trigger_ClockworkGiant(TrigHand):
	def __init__(self, entity):
		super().__init__(entity, ["CardLeavesHand", "CardEntersHand"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.inHand and ((target[0] if signal == "CardEntersHand" else target).ID == self.entity.ID)
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.Game.ManaHandler.calcMana_Single(self.entity)
		
		
"""Demon Hunter Cards"""
class Battlefiend(Minion):
	Class, race, name = "Demon Hunter", "Demon", "Battlefiend"
	mana, attack, health = 1, 1, 2
	index = "CORE~Demon Hunter~Minion~1~1~2~Demon~Battlefiend"
	requireTarget, keyWord, description = False, "", "After your hero attacks, gain +1 Attack"
	name_CN = "战斗邪犬"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_Battlefiend(self)]
		
class Trig_Battlefiend(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["HeroAttackedMinion", "HeroAttackedHero"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject == self.entity.Game.heroes[self.entity.ID]
		
	def text(self, CHN):
		return "在你的英雄攻击后，获得+1攻击力" if CHN else "After your hero attacks, gain +1 Attack"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.buffDebuff(1, 0)
		
		
class ChaosStrike(Spell):
	Class, school, name = "Demon Hunter", "Fel", "Chaos Strike"
	requireTarget, mana = False, 2
	index = "CORE~Demon Hunter~Spell~2~Fel~Chaos Strike"
	description = "Give your hero +2 Attack this turn. Draw a card"
	name_CN = "混乱打击"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.Game.heroes[self.ID].gainAttack(2)
		self.Game.Hand_Deck.drawCard(self.ID)
		return None
		
		
class CrimsonSigilRunner(Minion):
	Class, race, name = "Demon Hunter", "", "Crimson Sigil Runner"
	mana, attack, health = 1, 1, 1
	index = "CORE~Demon Hunter~Minion~1~1~1~~Crimson Sigil Runner~Outcast"
	requireTarget, keyWord, description = False, "", "Outcast: Draw a card"
	name_CN = "火色魔印奔行者"
	
	def effCanTrig(self):
		self.effectViable = self.Game.Hand_Deck.outcastcanTrig(self)
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if posinHand == 0 or posinHand == -1:
			self.Game.Hand_Deck.drawCard(self.ID)
		return None
		
		
class FeastofSouls(Spell):
	Class, school, name = "Demon Hunter", "Shadow", "Feast of Souls"
	requireTarget, mana = False, 2
	index = "CORE~Demon Hunter~Spell~2~Shadow~Feast of Souls"
	description = "Draw a card for each friendly minion that died this turn"
	name_CN = "灵魂盛宴"
	def effCanTrig(self):
		self.effectViable = self.Game.Counters.minionsDiedThisTurn[self.ID] != []
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		num = len(self.Game.Counters.minionsDiedThisTurn[self.ID])
		for i in range(num): self.Game.Hand_Deck.drawCard(self.ID)
		return None
		
		
class KorvasBloodthorn(Minion):
	Class, race, name = "Demon Hunter", "", "Kor'vas Bloodthorn"
	mana, attack, health = 2, 2, 2
	index = "CORE~Demon Hunter~Minion~2~2~2~~Kor'vas Bloodthorn~Charge~Lifesteal~Legendary"
	requireTarget, keyWord, description = False, "Charge,Lifesteal", "Charge, Lifesteal. After you play a card with Outcast, return this to your hand"
	name_CN = "考瓦斯·血棘"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_KorvasBloodthorn(self)]
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			self.dealsDamage(target, 1)
		return target
		
class Trig_KorvasBloodthorn(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["MinionBeenPlayed", "SpellBeenPlayed", "WeaponBeenPlayed", "HeroBeenPlayed"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject.ID == self.entity.ID and "~Outcast" in subject.index and not self.entity.dead and self.entity.health > 0
		
	def text(self, CHN):
		return "在你使用一张流放牌后，将该随从移回你的手牌" if CHN else "After you play a card with Outcast, return this to your hand"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.Game.returnMiniontoHand(self.entity, deathrattlesStayArmed=False)
		
		
class SightlessWatcher(Minion):
	Class, race, name = "Demon Hunter", "Demon", "Sightless Watcher"
	mana, attack, health = 2, 3, 2
	index = "CORE~Demon Hunter~Minion~2~3~2~Demon~Sightless Watcher~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Look at 3 cards in your deck. Choose one to put on top"
	name_CN = "盲眼观察者"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		ownDeck = curGame.Hand_Deck.decks[self.ID]
		if curGame.turn == self.ID and ownDeck:
			if curGame.mode == 0:
				if curGame.guides:
					ownDeck.append(ownDeck.pop(curGame.guides.pop(0)))
				else:
					if "byOthers" in comment:
						i = nprandint(len(ownDeck))
						curGame.fixedGuides.append(i)
						ownDeck.append(ownDeck.pop(i))
					else:
						curGame.options = npchoice(ownDeck, min(3, len(ownDeck)), replace=False)
						curGame.Discover.startDiscover(self)
		return None
		
	def discoverDecided(self, option, pool):
		ownDeck = self.Game.Hand_Deck.decks[self.ID]
		i = ownDeck.index(option)
		self.Game.fixedGuides.append(i)
		ownDeck.append(ownDeck.pop(i))
		
		
class SpectralSight(Spell):
	Class, school, name = "Demon Hunter", "", "Spectral Sight"
	requireTarget, mana = False, 2
	index = "CORE~Demon Hunter~Spell~2~~Spectral Sight~Outcast"
	description = "Draw a cards. Outscast: Draw another"
	name_CN = "幽灵视觉"
	def effCanTrig(self):
		self.effectViable = self.Game.Hand_Deck.outcastcanTrig(self)
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.Game.Hand_Deck.drawCard(self.ID)
		if posinHand == 0 or posinHand == -1:
			self.Game.Hand_Deck.drawCard(self.ID)
		return None
		
		
class AldrachiWarblades(Weapon):
	Class, name, description = "Demon Hunter", "Aldrachi Warblades", "Lifesteal"
	mana, attack, durability = 3, 2, 2
	index = "CORE~Demon Hunter~Weapon~3~2~2~Aldrachi Warblades~Lifesteal"
	name_CN = "奥达奇战刃"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.keyWords["Lifesteal"] = 1
		
		
class CoordinatedStrike(Spell):
	Class, school, name = "Demon Hunter", "", "Coordinated Strike"
	requireTarget, mana = False, 3
	index = "CORE~Demon Hunter~Spell~3~Coordinated Strike"
	description = "Summon three 1/1 Illidari with Rush"
	name_CN = "协同打击"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.Game.summon([IllidariInitiate(self.Game, self.ID) for i in range(3)], (-1, "totheRightEnd"), self)
		return None

		
class EyeBeam(Spell):
	Class, school, name = "Demon Hunter", "Fel", "Eye Beam"
	requireTarget, mana = True, 3
	index = "CORE~Demon Hunter~Spell~3~Fel~Eye Beam~Outcast"
	description = "Lifesteal. Deal 3 damage to a minion. Outcast: This costs (1)"
	name_CN = "眼棱"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.keyWords["Lifesteal"] = 1
		self.trigsHand = [Trig_EyeBeam(self)]
		
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
		
	def effCanTrig(self):
		self.effectViable = self.Game.Hand_Deck.outcastcanTrig(self)
		
	def selfManaChange(self):
		if self.inHand:
			posinHand = self.Game.Hand_Deck.hands[self.ID].index(self)
			if posinHand == 0 or posinHand == len(self.Game.Hand_Deck.hands[self.ID]) - 1:
				self.mana = 1
				
	def text(self, CHN):
		damage = (3 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		return "吸血。对一个随从造成%d点伤害。流放：法力值消耗为(1)点"%damage if CHN \
				else "Lifesteal. Deal %d damage to a minion. Outcast: This costs (1)"%damage
				
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			damage = (3 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			self.dealsDamage(target, damage)
		return target
		
class Trig_EyeBeam(TrigHand):
	def __init__(self, entity):
		super().__init__(entity, ["CardLeavesHand", "CardEntersHand"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		if self.entity.inHand:
			card = target[0] if signal == "CardEntersHand" else target
			return card.ID == self.entity.ID
		return False
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.Game.Manas.calcMana_Single(self.entity)
		
		
class GanargGlaivesmith(Minion):
	Class, race, name = "Demon Hunter", "Demon", "Gan'arg Glaivesmith"
	mana, attack, health = 3, 3, 2
	index = "CORE~Demon Hunter~Minion~3~3~2~Demon~Gan'arg Glaivesmith~Outcast"
	requireTarget, keyWord, description = False, "", "Outcast: Give your hero +3 Attack this turn"
	name_CN = "甘尔葛战刃铸造师"
	
	def effCanTrig(self):
		self.effectViable = self.Game.Hand_Deck.outcastcanTrig(self)
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if posinHand == 0 or posinHand == -1:
			self.Game.heroes[self.ID].gainAttack(3)
		return None
		
		
class AshtongueBattlelord(Minion):
	Class, race, name = "Demon Hunter", "", "Ashtongue Battlelord"
	mana, attack, health = 4, 3, 5
	index = "CORE~Demon Hunter~Minion~4~3~5~~Ashtongue Battlelord~Taunt~Lifesteal"
	requireTarget, keyWord, description = False, "Taunt,Lifesteal", "Taunt, Lifesteal"
	name_CN = "灰舌将领"
	
	
class RagingFelscreamer(Minion):
	Class, race, name = "Demon Hunter", "", "Raging Felscreamer"
	mana, attack, health = 4, 4, 4
	index = "CORE~Demon Hunter~Minion~4~4~4~~Raging Felscreamer~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: The next Demon you play costs (2) less"
	name_CN = "暴怒邪吼者"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		tempAura = YourNextDemonCosts2Less(self.Game, self.ID)
		self.Game.Manas.CardAuras.append(tempAura)
		tempAura.auraAppears()
		return None
		
class YourNextDemonCosts2Less(TempManaEffect):
	def __init__(self, Game, ID):
		super().__init__(Game, ID, -2, -1)
		self.temporary = False #不会在回合结束后消失，直到那个恶魔被打出为止
		self.auraAffected = []
		
	def applicable(self, target):
		return target.ID == self.ID and target.type == "Minion" and "Demon" in target.race
		
	def selfCopy(self, game):
		return type(self)(game, self.ID)
		
		
class ChaosNova(Spell):
	Class, school, name = "Demon Hunter", "Fel", "Chaos Nova"
	requireTarget, mana = False, 5
	index = "CORE~Demon Hunter~Spell~5~Fel~Chaos Nova"
	description = "Deal 4 damage to all minions"
	name_CN = "混乱新星"
	def text(self, CHN):
		damage = (4 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		return "对所有随从造成%d点伤害"%damage if CHN else "Deal %d damage to all minions"%damage
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		damage = (4 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		targets = self.Game.minionsonBoard(1) + self.Game.minionsonBoard(2)
		self.dealsAOE(targets, [damage for obj in targets])
		return None
		

class WarglaivesofAzzinoth(Weapon):
	Class, name, description = "Demon Hunter", "Warglaives of Azzinoth", "After attacking a minion, your hero may attack again"
	mana, attack, durability = 5, 3, 3
	index = "CORE~Demon Hunter~Weapon~5~3~3~Warglaives of Azzinoth"
	name_CN = "埃辛诺斯战刃"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_WarglaivesofAzzinoth(self)]
		
class Trig_WarglaivesofAzzinoth(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["HeroAttackedMinion"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject == self.entity.Game.heroes[self.entity.ID] and target.type == "Minion" and self.entity.onBoard
		
	def text(self, CHN):
		return "在攻击一个随从后，你的英雄可以再次攻击" if CHN else "After attacking a minion, your hero may attack again"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.Game.heroes[self.entity.ID].attChances_extra +=1
		
		
class IllidariInquisitor(Minion):
	Class, race, name = "Demon Hunter", "Demon", "Illidari Inquisitor"
	mana, attack, health = 8, 8, 8
	index = "CORE~Demon Hunter~Minion~8~8~8~Demon~Illidari Inquisitor~Rush"
	requireTarget, keyWord, description = False, "Rush", "Rush. After your hero attacks an enemy, this attacks it too"
	name_CN = "伊利达雷审判官"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_IllidariInquisitor(self)]
		
#效果参考引月长弓
class Trig_IllidariInquisitor(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["HeroAttackedMinion", "HeroAttackedHero"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		#The target and this minion can't be dying to trigger this
		minion = self.entity
		print("Can illidari inquisitor trig?", subject.ID == minion.ID and minion.onBoard and not minion.dead and minion.health > 0 and not target.dead and target.health > 0)
		return subject.ID == minion.ID and minion.onBoard and not minion.dead and minion.health > 0 and not target.dead and target.health > 0
		
	def text(self, CHN):
		return "在你的英雄攻击一个随从后，你的所有随从也会攻击该随从" if CHN \
				else "After your hero attacks a minion, your minions attack it too"
				
	#随从的攻击顺序与它们的登场顺序一致
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.Game.battle(self.entity, target, verifySelectable=False, useAttChance=False, resolveDeath=False, resetRedirTrig=True)
		
"""Druid Cards"""
class Innervate(Spell):
	Class, school, name = "Druid", "Nature", "Innervate"
	requireTarget, mana = False, 0
	index = "CORE~Druid~Spell~0~Nature~Innervate"
	description = "Gain 1 Mana Crystal this turn only"
	description_CN = "在本回合中，获得一个法力水晶。"
	name_CN = "激活"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if self.Game.Manas.manas[self.ID] < 10:
			self.Game.Manas.manas[self.ID] += 1
		return None
		
		
class Pounce(Spell):
	Class, school, name = "Druid", "", "Pounce"
	requireTarget, mana = False, 0
	index = "CORE~Druid~Spell~0~~Pounce"
	description = "Give your hero +2 Attack this turn"
	description_CN = "在本回合中，使你的英雄获得+2攻击力"
	name_CN = "飞扑"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		self.Game.heroes[self.ID].gainAttack(2)
		return None
		
		
class EnchantedRaven(Minion):
	Class, race, name = "Druid", "Beast", "Enchanted Raven"
	mana, attack, health = 1, 2, 2
	index = "CORE~Druid~Minion~1~2~2~Beast~Enchanted Raven"
	requireTarget, keyWord, description = False, "", ""
	description_CN = ""
	name_CN = "魔法乌鸦"
	
	
class MarkoftheWild(Spell):
	Class, school, name = "Druid", "Nature", "Mark of the Wild"
	requireTarget, mana = True, 2
	index = "CORE~Druid~Spell~2~Nature~Mark of the Wild"
	description = "Give a minion +2/+3 and Taunt"
	name_CN = "野性印记"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			target.buffDebuff(2, 3) #buffDebuff() and getsStatus() will check if the minion is onBoard or inHand.
			target.getsStatus("Taunt")
		return target
		
		
class PoweroftheWild(Spell):
	Class, school, name = "Druid", "", "Power of the Wild"
	requireTarget, mana = False, 2
	index = "CORE~Druid~Spell~2~~Power of the Wild~Choose One"
	description = "Choose One - Give your minions +1/+1; or Summon a 3/2 Panther"
	name_CN = "野性之力"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.options = [LeaderofthePack_Option(self), SummonaPanther_Option(self)]
		
	def need2Choose(self):
		return True
		
	#needTarget() always returns False
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if choice != 0:
			self.Game.summon(Panther(self.Game, self.ID), -1, self)
		if choice < 1:
			for minion in self.Game.minionsonBoard(self.ID):
				minion.buffDebuff(1, 1)
		return None
		
class LeaderofthePack_Option(Option):
	name, description = "Leader of the Pack", "Give your minions +1/+1"
	index = "EXPERT1~Druid~Spell~2~~Leader of the Pack~Uncollectible"
	mana, attack, health = 2, -1, -1
	
class SummonaPanther_Option(Option):
	name, description = "Summon a Panther", "Summon a 3/2 Panther"
	index = "EXPERT1~Druid~Spell~2~~Summon a Panther~Uncollectible"
	mana, attack, health = 2, -1, -1
	def available(self):
		return self.entity.Game.space(self.entity.ID) > 0
		
	
class FeralRage(Spell):
	Class, school, name = "Druid", "", "Feral Rage"
	requireTarget, mana = False, 3
	index = "CORE~Druid~Spell~3~~Feral Rage~Choose One"
	description = "Choose One - Give your minions +1/+1; or Summon a 3/2 Panther"
	name_CN = "野性之怒"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.options = [EvolveSpines_Option(self), EvolveScales_Option(self)]
		
	def need2Choose(self):
		return True
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if choice != 0:
			self.Game.heroes[self.ID].gainsArmor(8)
		if choice < 1:
			self.Game.heroes[self.ID].gainAttack(4)
		return None
		
class EvolveSpines_Option(Option):
	name, description = "Evolve Spines", "Give your hero +4 Attack this turn"
	index = "CORE~Druid~Spell~3~~EvolveSpines~Uncollectible"
	mana, attack, health = 3, -1, -1
	
class EvolveScales_Option(Option):
	name, description = "Evolve Scales", "Gain 8 Armor"
	index = "CORE~Druid~Spell~3~~Evolve Scales~Uncollectible"
	mana, attack, health = 3, -1, -1
	
	
class Landscaping(Spell):
	Class, school, name = "Druid", "Nature", "Landscaping"
	requireTarget, mana = False, 3
	index = "CORE~Druid~Spell~3~Nature~Landscaping"
	description = "Summon two 2/2 Treants"
	name_CN = "植树造林"
	def available(self):
		return self.Game.space(self.ID) > 0
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.Game.summon([Treant_Classic(self.Game, self.ID) for i in range(2)], (-1, "totheRightEnd"), self)
		return None
		
	
class WildGrowth(Spell):
	Class, school, name = "Druid", "Nature", "Wild Growth"
	requireTarget, mana = False, 3
	index = "CORE~Druid~Spell~3~Nature~Wild Growth"
	description = "Gain an empty Mana Crystal"
	name_CN = "野性成长"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if self.Game.Manas.gainEmptyManaCrystal(1, self.ID) == False:
			self.Game.Hand_Deck.addCardtoHand(ExcessMana(self.Game, self.ID), self.ID, creator=type(self))
		return None
		
		
class NordrassilDruid(Minion):
	Class, race, name = "Druid", "", "Nordrassil Druid"
	mana, attack, health = 4, 3, 5
	index = "CORE~Druid~Minion~4~3~5~~Nordrassil Druid~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Your next spell this turn costs (3) less"
	name_CN = "诺达希尔德鲁伊"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		tempAura = GameManaAura_InTurnNextSpell3Less(self.Game, self.ID)
		self.Game.Manas.CardAuras.append(tempAura)
		tempAura.auraAppears()
		return None
		
class GameManaAura_InTurnNextSpell3Less(TempManaEffect):
	def __init__(self, Game, ID, changeby=0, changeto=-1):
		super().__init__(Game, ID, -3, -1)
		
	def applicable(self, target):
		return target.ID == self.ID and target.type == "Spell"
		
		
class SouloftheForest(Spell):
	Class, school, name = "Druid", "Nature", "Soul of the Forest"
	requireTarget, mana = False, 4
	index = "CORE~Druid~Spell~4~Nature~Soul of the Forest"
	description = "Give your minions 'Deathrattle: Summon a 2/2 Treant'"
	name_CN = "丛林之魂"
	def available(self):
		return self.Game.minionsonBoard(self.ID) != []
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		for minion in self.Game.minionsonBoard(self.ID):
			trig = SummonaTreant(minion)
			minion.deathrattles.append(trig)
			trig.connect()
		return None
		
class SummonaTreant(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		#This Deathrattle can't possibly be triggered in hand
		self.entity.Game.summon(Treant_Classic(self.entity.Game, self.entity.ID), self.entity.pos+1, self.entity)
		
	def text(self, CHN):
		return "亡语：召唤一个2/2的树人" if CHN else "Deathrattle: Summon a 2/2 Treant"
		
		
class DruidoftheClaw(Minion):
	Class, race, name = "Druid", "", "Druid of the Claw"
	mana, attack, health = 5, 5, 4
	index = "CORE~Druid~Minion~5~5~4~~Druid of the Claw~Choose One"
	requireTarget, keyWord, description = False, "", "Choose One - Transform into a 5/4 with Rush; or a 5/6 with Taunt"
	name_CN = "利爪德鲁伊"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.options = [CatForm_Option(self), BearForm_Option(self)]
		
	def need2Choose(self):
		return True
		
	def played(self, target=None, choice=0, mana=0, posinHand=0, comment=""):
		self.statReset(self.attack_Enchant, self.health_max)
		self.appears(firstTime=True)
		if choice < 0: minion = DruidoftheClaw_Both(self.Game, self.ID)
		elif choice == 0: minion = DruidoftheClaw_Charge(self.Game, self.ID)
		else: minion = DruidoftheClaw_Taunt(self.Game, self.ID)
		#抉择变形类随从的入场后立刻变形。
		self.Game.transform(self, minion)
		#在此之后就要引用self.Game.minionPlayed
		self.Game.sendSignal("MinionPlayed", self.ID, self.Game.minionPlayed, None, mana, "", choice)
		self.Game.sendSignal("MinionSummoned", self.ID, self.Game.minionPlayed, None, mana, "")
		self.Game.gathertheDead()
		return None
		
class CatForm_Option(Option):
	name, type, description = "Cat Form", "Option_Minion", "Rush"
	mana, attack, health = 5, 5, 4
	
class BearForm_Option(Option):
	name, type, description = "Bear Form", "Option_Minion", "+2 health and Taunt"
	mana, attack, health = 5, 5, 6
	
class ForceofNature(Spell):
	Class, school, name = "Druid", "Nature", "Force of Nature"
	requireTarget, mana = False, 5
	index = "CORE~Druid~Spell~5~Nature~Force of Nature"
	description = "Summon three 2/2 Treants"
	name_CN = "自然之力"
	def available(self):
		return self.Game.space(self.ID) > 0
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.Game.summon([Treant_Classic(self.Game, self.ID) for i in range(3)], (-1, "totheRightEnd"), self)
		return None
		
	
class MenagerieWarden(Minion):
	Class, race, name = "Druid", "", "Menagerie Warden"
	mana, attack, health = 5, 4, 4
	index = "CORE~Druid~Minion~5~4~4~~Menagerie Warden~Battlecry"
	requireTarget, keyWord, description = True, "", "Battlecry: Choose a friendly Beast. Summon a copy of it"
	description_CN = "在本回合中，获得一个法力水晶。"
	name_CN = "展览馆守卫"
	
	def targetExists(self, choice=0):
		return self.selectableFriendlyMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.ID == self.ID and "Beast" in target.race and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			Copy = target.selfCopy(self.ID, self) if target.onBoard else type(target)(self.Game, self.ID)
			self.Game.summon(Copy, target.pos+1, creator=self)
		return target
		
		
class Nourish(Spell):
	Class, school, name = "Druid", "Nature", "Nourish"
	requireTarget, mana = False, 6
	index = "CORE~Druid~Spell~6~Nature~Nourish~Choose One"
	description = "Choose One - Gain 2 Mana Crystals; or Draw 3 cards"
	name_CN = "滋养"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.options = [RampantGrowth_Option(self), Enrich_Option(self)]
		
	def need2Choose(self):
		return True
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if choice < 1:
			self.Game.Manas.gainManaCrystal(2, self.ID)
		if choice != 0:
			self.Game.Hand_Deck.drawCard(self.ID)
			self.Game.Hand_Deck.drawCard(self.ID)
			self.Game.Hand_Deck.drawCard(self.ID)
		return None
		
class RampantGrowth_Option(Option):
	name, description = "Rampant Growth", "Gain 2 Mana Crystals"
	index = "EXPERT1~Druid~Spell~6~Nature~Rampant Growth~Uncollectible"
	mana, attack, health = 6, -1, -1
	
class Enrich_Option(Option):
	name, description = "Enrich", "Draw 3 cards"
	index = "EXPERT1~Druid~Spell~6~Nature~Enrich~Uncollectible"
	mana, attack, health = 6, -1, -1
	
	
class AncientofWar(Minion):
	Class, race, name = "Druid", "", "Ancient of War"
	mana, attack, health = 7, 5, 5
	index = "CORE~Druid~Minion~7~5~5~~Ancient of War~Choose One"
	requireTarget, keyWord, description = False, "", "Choose One - +5 Attack; or +5 Health and Taunt"
	name_CN = "战争古树"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.options = [Uproot_Option(self), Rooted_Option(self)]
		
	def need2Choose(self):
		return True
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if choice < 1:
			self.buffDebuff(5, 0)
		if choice != 0:
			self.buffDebuff(0, 5)
			self.getsStatus("Taunt")
		return None
		
class Uproot_Option(Option):
	name, description = "Uproot", "+5 attack"
	mana, attack, health = 7, -1, -1
	
class Rooted_Option(Option):
	name, description = "Rooted", "+5 health and Taunt"
	mana, attack, health = 7, -1, -1
	
	
class Cenarius(Minion):
	Class, race, name = "Druid", "", "Cenarius"
	mana, attack, health = 8, 5, 8
	index = "CORE~Druid~Minion~8~5~8~~Cenarius~Choose One~Legendary"
	requireTarget, keyWord, description = False, "", "Choose One- Give your other minions +2/+2; or Summon two 2/2 Treants with Taunt"
	name_CN = "塞纳留斯"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		# 0: Give other minion +2/+2; 1:Summon two Treants with Taunt.
		self.options = [DemigodsFavor_Option(self), ShandosLesson_Option(self)]
		
	def need2Choose(self):
		return True
		
	#对于抉择随从而言，应以与战吼类似的方式处理，打出时抉择可以保持到最终结算。但是打出时，如果因为鹿盔和发掘潜力而没有选择抉择，视为到对方场上之后仍然可以而没有如果没有
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if choice != 0:
			pos = (self.pos, "leftandRight") if self.onBoard else (-1, "totheRightEnd")
			self.Game.summon([Treant_Classic_Taunt(self.Game, self.ID) for i in range(2)], pos, self)
		if choice < 1:
			for minion in self.Game.minionsonBoard(self.ID):
				if minion != self:
					minion.buffDebuff(2, 2)
		return None
		
class DemigodsFavor_Option(Option):
	name, description = "Demigod's Favor", "Give your other minions +2/+2"
	mana, attack, health = 9, -1, -1
	
class ShandosLesson_Option(Option):
	name, description = "Shan'do's Lesson", "Summon two 2/2 Treants with Taunt"
	mana, attack, health = 9, -1, -1
	def available(self):
		return self.entity.Game.space(self.entity.ID) > 0
		
"""Hunter Cards"""
class ArcaneShot(Spell):
	Class, school, name = "Hunter", "Arcane", "Arcane Shot"
	requireTarget, mana = True, 1
	index = "CORE~Hunter~Spell~1~Arcane~Arcane Shot"
	description = "Deal 2 damage"
	name_CN = "奥术射击"
	def text(self, CHN):
		damage = (2 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		return "造成%d点伤害"%damage if CHN else "Deal %d damage"%damage
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			damage = (2 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			self.dealsDamage(target, damage)
		return target
		
		
class Tracking(Spell):
	Class, school, name = "Hunter", "", "Tracking"
	requireTarget, mana = False, 1
	index = "CORE~Hunter~Spell~1~Tracking"
	description = "Discover a card from your deck"
	name_CN = "追踪术"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		ownDeck = curGame.Hand_Deck.decks[self.ID]
		if curGame.mode == 0:
			if curGame.guides:
				i = curGame.guides.pop(0)
				if i > -1: curGame.Hand_Deck.drawCard(self.ID, i)
			else:
				types, inds = [type(card) for card in ownDeck], list(range(len(ownDeck)))
				if "byOthers" in comment:
					inds = npChoice_inds(types, inds, 1)
					i = inds[0] if inds else -1
					curGame.fixedGuides.append(i)
					if i > -1: curGame.Hand_Deck.drawCard(self.ID, i)
				else:
					inds = npChoice_inds(types, inds, 3)
					print("Tracking, ", inds)
					if len(inds) > 1:
						curGame.options = [ownDeck[i] for i in inds]
						curGame.Discover.startDiscover(self)
					else:
						i = inds[0] if inds else -1 #牌库 中没有牌的时候会返回一个空的inds列表
						curGame.fixedGuides.append(i)
						if i > -1: curGame.Hand_Deck.drawCard(self.ID, i)
		return None
		
	def discoverDecided(self, option, pool):
		i = self.Game.Hand_Deck.decks[self.ID].index(option)
		self.Game.fixedGuides.append(i)
		self.Game.Hand_Deck.drawCard(self.ID, i)
		
		
class Webspinner(Minion):
	Class, race, name = "Neutral", "Beast", "Webspinner"
	mana, attack, health = 1, 1, 1
	index = "CORE~Neutral~Minion~1~1~1~Beast~Webspinner~Deathrattle"
	requireTarget, keyWord, description = False, "", "Deathrattle: Add a random Beast to your hand"
	name_CN = "结网蛛"
	poolIdentifier = "Beasts"
	@classmethod
	def generatePool(cls, pools):
		return "Beasts", list(pools.MinionswithRace["Beast"].values())
		
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.deathrattles = [AddaBeasttoYourHand(self)]
		
class AddaBeasttoYourHand(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		curGame = self.entity.Game
		if curGame.mode == 0:
			if curGame.guides:
				minion = curGame.guides.pop(0)
			else:
				minion = npchoice(self.rngPool("Beasts"))
				curGame.fixedGuides.append(minion)
			curGame.Hand_Deck.addCardtoHand(minion, self.entity.ID, byType=True)
			
	def text(self, CHN):
		return "亡语：随机将一张野兽牌置入你的手牌" if CHN else "Deathrattle: Add a random Beast to your hand"
		
		
class ExplosiveTrap(Secret):
	Class, school, name = "Hunter", "Fire", "Explosive Trap"
	requireTarget, mana = False, 2
	index = "CORE~Hunter~Spell~2~Fire~Explosive Trap~~Secret"
	description = "Secret: When your hero is attacked, deal 2 damage to all enemies"
	name_CN = "爆炸陷阱"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_ExplosiveTrap(self)]
		
	def text(self, CHN):
		damage = (2 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		return "奥秘：当你的英雄受到攻击，对所有敌人造成%d点伤害"%damage if CHN else "Secret: When your hero is attacked, deal %d damage to all enemies"%damage
		
class Trig_ExplosiveTrap(SecretTrigger):
	def __init__(self, entity):
		super().__init__(entity, ["HeroAttacksHero", "MinionAttacksHero"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0): #target here holds the actual target object
		return self.entity.ID != self.entity.Game.turn and target[0] == self.entity.Game.heroes[self.entity.ID]
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		damage = (2 + self.entity.countSpellDamage()) * (2 ** self.entity.countDamageDouble())
		enemies = [self.entity.Game.heroes[3-self.entity.ID]] + self.entity.Game.minionsonBoard(3-self.entity.ID)
		self.entity.dealsAOE(enemies, [damage for obj in enemies])
		
		
class FreezingTrap(Secret):
	Class, school, name = "Hunter", "Frost", "Freezing Trap"
	requireTarget, mana = False, 2
	index = "CORE~Hunter~Spell~2~Frost~Freezing Trap~~Secret"
	description = "Secret: When an enemy minion attacks, return it to its owner's hand. It costs (2) more."
	name_CN = "冰冻陷阱"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_FreezingTrap(self)]
		
class Trig_FreezingTrap(SecretTrigger):
	def __init__(self, entity):
		super().__init__(entity, ["MinionAttacksMinion", "MinionAttacksHero"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		print("Check if secret can respond to attacking", signal, ID, subject, target, number, comment)
		return self.entity.ID != self.entity.Game.turn and subject.type == "Minion" and subject.ID != self.entity.ID \
				and subject.onBoard and subject.health > 0 and not subject.dead #The attacker must be onBoard and alive to be returned to hand
				
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		#假设那张随从在进入手牌前接受-2费效果。可以被娜迦海巫覆盖。
		manaMod = ManaMod(subject, changeby=+2, changeto=-1)
		self.entity.Game.returnMiniontoHand(subject, deathrattlesStayArmed=False, manaMod=manaMod)
		
		
class HeadhuntersHatchet(Weapon):
	Class, name, description = "Hunter", "Headhunter's Hatchet", "Battlecry: If you control a Beast, gain +1 Durability"
	mana, attack, durability = 2, 2, 2
	index = "CORE~Hunter~Weapon~2~2~2~Headhunter's Hatchet~Battlecry"
	name_CN = "猎头者之斧"
	def effectCanTrigger(self):
		self.effectViable = any("Beast" in minion.race for minion in self.Game.minionsonBoard(self.ID))
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		#Can't be invoked by Shudderwock.
		if any("Beast" in minion.race for minion in self.Game.minionsonBoard(self.ID)) and self.type == "Weapon":
			self.gainStat(0, 1)
		return None
		
		
class QuickShot(Spell):
	Class, school, name = "Hunter", "", "Quick Shot"
	requireTarget, mana = True, 2
	index = "CORE~Hunter~Spell~2~~Quick Shot"
	description = "Deal 3 damage. If your hand is empty, draw a card"
	name_CN = "快速射击"
	def effectCanTrigger(self):
		return len(self.Game.Hand_Deck.hands[self.ID]) < 2
		
	def text(self, CHN):
		damage = (3 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		return "造成%d点伤害。如果你没有手牌，抽一张牌"%damage if CHN else "Deal %d damage. If your hand is empty, draw a card"%damage
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			damage = (3 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			self.dealsDamage(target, damage)
			if not self.Game.Hand_Deck.hands[self.ID]:
				self.Game.Hand_Deck.drawCard(self.ID)
		return target
		
		
class ScavengingHyena(Minion):
	Class, race, name = "Hunter", "Beast", "Scavenging Hyena"
	mana, attack, health = 2, 2, 2
	index = "CORE~Hunter~Minion~2~2~2~Beast~Scavenging Hyena"
	requireTarget, keyWord, description = False, "", "Whenever a friendly Beast dies, gain +2/+1"
	name_CN = "食腐土狼"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_ScavengingHyena(self)]
		
class Trig_ScavengingHyena(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["MinionDies"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		#Technically, minion has to disappear before dies. But just in case.
		return self.entity.onBoard and target != self.entity and target.ID == self.entity.ID and "Beast" in target.race
		
	def text(self, CHN):
		return "每当一个友方野兽死亡，便获得+2/+1" if CHN else "Whenever a friendly Beast dies, gain +2/+1"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.buffDebuff(2, 1)
		
		
class SelectiveBreeder(Minion):
	Class, race, name = "Hunter", "", "Selective Breeder"
	mana, attack, health = 2, 1, 1
	index = "CORE~Hunter~Minion~2~1~1~~Selective Breeder~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Discover a copy of a Beast in your deck"
	name_CN = "选种饲养员"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		ownDeck = curGame.Hand_Deck.decks[self.ID]
		if curGame.mode == 0:
			if curGame.guides:
				i = curGame.guides.pop(0)
				if i > -1: curGame.Hand_Deck.addCardtoHand(ownDeck[i].selfCopy(self.ID, self), self.ID, creator=type(self))
			else:
				types, inds = [], []
				for i, card in enumerate(ownDeck):
					if card.type == "Minion" and "Beast" in card.race:
						types.append(type(card))
						inds.append(i)
				if "byOthers" in comment:
					inds = npChoice_inds(types, inds, 1)
					i = inds[0] if inds else -1
					curGame.fixedGuides.append(i)
					if i > -1: curGame.Hand_Deck.addCardtoHand(ownDeck[i].selfCopy(self.ID, self), self.ID, creator=type(self))
				else:
					inds = npChoice_inds(types, inds, 3)
					if len(inds) > 1:
						curGame.options = [ownDeck[i] for i in inds]
						curGame.Discover.startDiscover(self)
					else:
						i = inds[0] if inds else -1
						curGame.fixedGuides.append(i)
						if i > -1: curGame.Hand_Deck.addCardtoHand(ownDeck[i].selfCopy(self.ID, self), self.ID, creator=type(self))
		return None
		
	def discoverDecided(self, option, pool):
		ownDeck = self.Game.Hand_Deck.decks[self.ID]
		i = ownDeck.index(option)
		self.Game.fixedGuides.append(i)
		self.Game.Hand_Deck.addCardtoHand(ownDeck[i].selfCopy(self.ID, self), self.ID, creator=type(self))
		
		
class SnakeTrap(Secret):
	Class, school, name = "Hunter", "", "Snake Trap"
	requireTarget, mana = False, 2
	index = "CORE~Hunter~Spell~2~~Snake Trap~~Secret"
	description = "Secret: When one of your minions is attacked, summon three 1/1 Snakes"
	name_CN = "毒蛇陷阱"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_SnakeTrap(self)]
		
class Trig_SnakeTrap(SecretTrigger):
	def __init__(self, entity):
		super().__init__(entity, ["MinionAttacksMinion", "HeroAttacksMinion"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0): #target here holds the actual target object
		#The target has to a friendly minion and there is space on board to summon minions.
		return self.entity.ID != self.entity.Game.turn and target[0].type == "Minion" and target[0].ID == self.entity.ID and self.entity.Game.space(self.entity.ID) > 0
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.Game.summon([Snake(self.entity.Game, self.entity.ID) for i in range(3)], (-1, "totheRightEnd"), self.entity)
		
	
class Bearshark(Minion):
	Class, race, name = "Hunter", "Beast", "Bearshark"
	mana, attack, health = 3, 4, 3
	index = "CORE~Hunter~Minion~3~4~3~Beast~Bearshark"
	requireTarget, keyWord, description = False, "", "Can't be targeted by spells or Hero Powers"
	name_CN = "熊鲨"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.marks["Evasive"] = 1
		
		
class DeadlyShot(Spell):
	Class, school, name = "Hunter", "", "Deadly Shot"
	requireTarget, mana = False, 3
	index = "CORE~Hunter~Spell~3~Deadly Shot"
	description = "Destroy a random enemy minion"
	name_CN = "致命射击"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if curGame.mode == 0:
			if curGame.guides:
				i = curGame.guides.pop(0)
			else:
				minions = curGame.minionsAlive(3-self.ID)
				i = npchoice(minions).pos if minions else -1
				curGame.fixedGuides.append(i)
			if i > -1:
				self.Game.killMinion(self, curGame.minions[3-self.ID][i])
		return None
		
		
class DireFrenzy(Spell):
	Class, school, name = "Hunter", "", "Dire Frenzy"
	requireTarget, mana = True, 4
	index = "CORE~Hunter~Spell~4~~Dire Frenzy"
	description = "Give a Beast +3/+3. Shuffle three copies into your deck with +3/+3"
	name_CN = "凶猛狂暴"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and "Beast" in target.race and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if target:
			target.buffDebuff(3, 3)
			beast, cards = type(target), []
			for i in range(3):
				card = beast(self.Game, self.ID)
				card.buffDebuff(3, 3)
				cards.append(card)
			self.Game.Hand_Deck.shuffleintoDeck(cards, self.ID, creator=self)
		return target
		
		
class SavannahHighmane(Minion):
	Class, race, name = "Hunter", "Beast", "Savannah Highmane"
	mana, attack, health = 6, 6, 5
	index = "CORE~Hunter~Minion~6~6~5~Beast~Savannah Highmane~Deathrattle"
	requireTarget, keyWord, description = False, "", "Deathrattle: Summon two 2/2 Hyenas"
	name_CN = "长鬃草原狮"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.deathrattles = [Summon2Hyenas(self)]
		
class Summon2Hyenas(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		pos = (self.entity.pos, "leftandRight") if self.entity in self.entity.Game.minions[self.entity.ID] else (-1, "totheRightEnd")
		self.entity.Game.summon([Hyena_Classic(self.entity.Game, self.entity.ID) for i in range(2)], pos, self.entity)
		
	def text(self, CHN):
		return "亡语：召唤两个2/2的土狼" if CHN else "Deathrattle: Summon two 2/2 Hyenas"
		
		
class KingKrush(Minion):
	Class, race, name = "Hunter", "Beast", "King Krush"
	mana, attack, health = 9, 8, 8
	index = "CORE~Hunter~Minion~9~8~8~Beast~King Krush~Charge~Legendary"
	requireTarget, keyWord, description = False, "Charge", "Charge"
	name_CN = "暴龙王克鲁什"
	
"""Mage Cards"""
class BabblingBook(Minion):
	Class, race, name = "Mage", "", "Babbling Book"
	mana, attack, health = 1, 1, 1
	index = "CORE~Mage~Minion~1~1~1~~Babbling Book~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Add a random Mage spell to your hand"
	name_CN = "呓语魔典"
	poolIdentifier = "Mage Spells"
	@classmethod
	def generatePool(cls, pools):
		return "Mage Spells", [value for key, value in pools.ClassCards["Mage"].items() if "~Spell~" in key]
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if curGame.mode == 0:
			pool = tuple(self.rngPool("Mage Spells"))
			if curGame.guides:
				spell = curGame.guides.pop(0)
			else:
				spell = npchoice(pool)
				curGame.fixedGuides.append(spell)
			curGame.Hand_Deck.addCardtoHand(spell, self.ID, byType=True, creator=type(self), possi=pool)
		return None
		
		
class ShootingStar(Spell):
	Class, school, name = "Mage", "Arcane", "Shooting Star"
	requireTarget, mana = True, 1
	index = "CORE~Mage~Spell~1~Arcane~Shooting Star"
	description = "Deal 1 damage to a minion and its neighbors"
	name_CN = "迸射流星"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
	
	def text(self, CHN):
		damage = (1 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		return "对一个随从及其相邻的随从造成%d点伤害" % damage if CHN else "Deal %d damage to a minion and its neighbors" % damage
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			damage = (1 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			neighbors = self.Game.neighbors2(target)[0]
			if target.onBoard and neighbors:
				self.dealsAOE([target] + neighbors, [damage] * (1 + len(neighbors)))
			else:
				self.dealsDamage(target, damage)
		return target
		
		
class SnapFreeze(Spell):
	Class, school, name = "Mage", "Frost", "Snap Freeze"
	requireTarget, mana = True, 1
	index = "CORE~Mage~Spell~1~Frost~Snap Freeze"
	description = "Freeze a minion. If it's already Frozen, destroy it"
	name_CN = "急速冷冻"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			target.getsStatus("Frozen")
			if target.status["Frozen"] > 1: self.Game.killMinion(self, target)
		return target
		
		
class Arcanologist(Minion):
	Class, race, name = "Mage", "", "Arcanologist"
	mana, attack, health = 2, 2, 3
	index = "CORE~Mage~Minion~2~2~3~~Arcanologist~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Draw a Secret"
	name_CN = "秘法学家"
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		ownDeck = curGame.Hand_Deck.decks[self.ID]
		if curGame.mode == 0:
			if curGame.guides:
				i = curGame.guides.pop(0)
			else:
				secrets = [i for i, card in enumerate(ownDeck) if card.description.startswith("Secret:")]
				i = npchoice(secrets) if secrets else -1
				curGame.fixedGuides.append(i)
			if i > -1: curGame.Hand_Deck.drawCard(self.ID, i)
		return None
		
		
class FallenHero(Minion):
	Class, race, name = "Mage", "", "Fallen Hero"
	mana, attack, health = 2, 3, 2
	index = "CORE~Mage~Minion~2~3~2~~Fallen Hero"
	requireTarget, keyWord, description = False, "", "Your Hero Power deals 1 extra damage"
	name_CN = "英雄之魂"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.auras["Your Hero Power deals 1 extra damage"] = GameRuleAura_FallenHero(self)
		
class GameRuleAura_FallenHero(GameRuleAura):
	def auraAppears(self):
		self.entity.Game.status[self.entity.ID]["Power Damage"] += 1
		
	def auraDisappears(self):
		self.entity.Game.status[self.entity.ID]["Power Damage"] -= 1
		
		
class ArcaneIntellect(Spell):
	Class, school, name = "Mage", "Arcane", "Arcane Intellect"
	requireTarget, mana = False, 3
	index = "CORE~Mage~Spell~3~Arcane~Arcane Intellect"
	description = "Draw 2 cards"
	name_CN = "奥术智慧"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.Game.Hand_Deck.drawCard(self.ID)
		self.Game.Hand_Deck.drawCard(self.ID)
		return None
		
		
class ConeofCold(Spell):
	Class, school, name = "Mage", "Frost", "Cone of Cold"
	requireTarget, mana = True, 3
	index = "CORE~Mage~Spell~3~Frost~Cone of Cold"
	description = "Freeze a minion and the minions next to it, and deal 1 damage to them"
	name_CN = "冰锥术"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
		
	def text(self, CHN):
		damage = (1 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		return "冻结一个随从和其相邻的随从，并对接它们造成%d点伤害"%damage if CHN \
				else "Freeze a minion and the minions next to it, and deal %d damage to them"%damage
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			damage = (1 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			neighbors = self.Game.neighbors2(target)[0]
			if target.onBoard and neighbors:
				targets = [target] + neighbors
				self.dealsAOE(targets, [damage] * len(targets))
				for minion in targets: minion.getsStatus("Frozen")
			else:
				self.dealsDamage(target, damage)
				target.getsStatus("Frozen")
		return target
		
		
class Counterspell(Secret):
	Class, school, name = "Mage", "Arcane", "Counterspell"
	requireTarget, mana = False, 3
	index = "CORE~Mage~Spell~3~Arcane~Counterspell~~Secret"
	description = "Secret: When your opponent casts a spell, Counter it."
	name_CN = "法术反制"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_Counterspell(self)]
		
class Trig_Counterspell(SecretTrigger):
	def __init__(self, entity):
		super().__init__(entity, ["SpellOKtoCast?"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return ID != self.entity.ID and subject
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		subject.pop()
		
		
class IceBarrier(Secret):
	Class, school, name = "Mage", "Frost", "Ice Barrier"
	requireTarget, mana = False, 3
	index = "CORE~Mage~Spell~3~Frost~Ice Barrier~~Secret"
	description = "Secret: When your hero is attacked, gain 8 Armor"
	name_CN = "寒冰护体"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_IceBarrier(self)]

class Trig_IceBarrier(SecretTrigger):
	def __init__(self, entity):
		super().__init__(entity, ["HeroAttacksHero", "MinionAttacksHero"])
	
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):  #target here holds the actual target object
		print("Check if secret can respond to attacking", signal, ID, subject, target, number, comment)
		return self.entity.ID != self.entity.Game.turn and target[0] == self.entity.Game.heroes[self.entity.ID]
	
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.Game.heroes[self.entity.ID].gainsArmor(8)
		
		
class MirrorEntity(Secret):
	Class, school, name = "Mage", "Arcane", "Mirror Entity"
	requireTarget, mana = False, 3
	index = "CORE~Mage~Spell~3~Arcane~Mirror Entity~~Secret"
	description = "Secret: After your opponent plays a minion, summon a copy of it"
	name_CN = "镜像实体"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_MirrorEntity(self)]
		
class Trig_MirrorEntity(SecretTrigger):
	def __init__(self, entity):
		super().__init__(entity, ["MinionBeenPlayed"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.ID != self.entity.Game.turn and subject.ID != self.entity.ID and self.entity.Game.space(self.entity.ID) > 0 and subject.health > 0 and subject.dead == False
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		Copy = subject.selfCopy(self.entity.ID, self.entity)
		self.entity.Game.summon(Copy, -1, self.entity)
		
		
class Fireball(Spell):
	Class, school, name = "Mage", "Fire", "Fireball"
	requireTarget, mana = True, 4
	index = "CORE~Mage~Spell~4~Fire~Fireball"
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
		
		
class WaterElemental_Core(Minion):
	Class, race, name = "Mage", "Elemental", "Water Elemental"
	mana, attack, health = 4, 3, 6
	index = "CORE~Mage~Minion~4~3~6~Elemental~Water Elemental"
	requireTarget, keyWord, description = False, "", "Freeze any character damaged by this minion"
	name_CN = "水元素"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_WaterElemental(self)]
		
		
class AegwynntheGuardian(Minion):
	Class, race, name = "Neutral", "", "Aegwynn, the Guardian"
	mana, attack, health = 5, 5, 5
	index = "CORE~Neutral~Minion~5~5~5~~Aegwynn, the Guardian~Spell Damage~Deathrattle~Legendary"
	requireTarget, keyWord, description = False, "", "Spell Damage +2. Deathrattle: The next minion your draw inherits these powers"
	name_CN = "守护者艾格文"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.keyWords["Spell Damage"] = 2
		self.deathrattles = [PassonGuadiansPower(self)]
		
class PassonGuadiansPower(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		AegwynntheGuardian_Effect(self.entity.Game, self.entity.ID).connect()
		
	def text(self, CHN):
		return "亡语：你抽到的下一张随从会继承这些能力" if CHN else "Deathrattle: The next minion your draw inherits these powers"
		
class AegwynntheGuardian_Effect:
	def __init__(self, Game, ID):
		self.Game, self.ID = Game, ID
		self.card = AegwynntheGuardian(Game, ID)
		
	def text(self, CHN):
		return "当你抽到下一张随从牌时，它将继承守护者的能力" if CHN \
				else "When you draw the next minion, it inherits the power of the Guardian"
				
	def connect(self):
		try: self.Game.trigsBoard[self.ID]["CardDrawn"].append(self)
		except: self.Game.trigsBoard[self.ID]["CardDrawn"] = [self]
		if self.Game.GUI: self.Game.GUI.heroZones[self.ID].addaTrig(self.card)
	
	def disconnect(self):
		try: self.Game.trigsBoard[self.ID]["CardDrawn"].remove(self)
		except: pass
		if self.Game.GUI: self.Game.GUI.heroZones[self.ID].removeaTrig(self.card.btn)
	
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return target[0].ID == self.ID and target[0].type == "Minion"
		
	def trig(self, signal, ID, subject, target, number, comment, choice=0):
		if self.canTrig(signal, ID, subject, target, number, comment):
			if self.Game.GUI: self.Game.GUI.showOffBoardTrig(self.card)
			self.effect(signal, ID, subject, target, number, comment)
			
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.disconnect()
		target[0].getsStatus("Spell Damage", 2)
		target[0].deathrattles.append(PassonGuadiansPower(target[0]))
		
	def createCopy(self, game):
		if self not in game.copiedObjs:
			trigCopy = type(self)(game, self.ID)
			game.copiedObjs[self] = trigCopy
			return trigCopy
		else:
			return game.copiedObjs[self]
			
			
class EtherealConjurer(Minion):
	Class, race, name = "Mage", "", "Ethereal Conjurer"
	mana, attack, health = 5, 6, 4
	index = "CORE~Mage~Minion~5~6~4~~Ethereal Conjurer~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Discover a spell"
	name_CN = "虚灵巫师"
	poolIdentifier = "Mage Spells"
	@classmethod
	def generatePool(cls, pools):
		return [Class+" Spells" for Class in pools.Classes], \
				[[value for key, value in pools.ClassCards[Class].items() if "~Spell~" in key] for Class in pools.Classes]
				
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if curGame.mode == 0:
			if curGame.guides:
				curGame.Hand_Deck.addCardtoHand(curGame.guides.pop(0), self.ID, byType=True, byDiscover=True)
			else:
				key = classforDiscover(self)+" Spells"
				if self.ID != curGame.turn or "byOthers" in comment:
					spell = npchoice(self.rngPool(key))
					curGame.fixedGuides.append(spell)
					curGame.Hand_Deck.addCardtoHand(spell, self.ID, byType=True, byDiscover=True)
				else:
					spells = npchoice(self.rngPool(key), 3, replace=False)
					curGame.options = [spell(curGame, self.ID) for spell in spells]
					curGame.Discover.startDiscover(self)
		return target
		
	def discoverDecided(self, option, pool):
		self.Game.fixedGuides.append(type(option))
		self.Game.Hand_Deck.addCardtoHand(option, self.ID, byDiscover=True)
		
		
class ColdarraDrake(Minion):
	Class, race, name = "Mage", "Dragon", "Coldarra Drake"
	mana, attack, health = 6, 6, 7
	index = "CORE~Mage~Minion~6~6~7~Dragon~Coldarra Drake"
	requireTarget, keyWord, description = False, "", "You can use your Hero Power any number of times"
	name_CN = "考达拉幼龙"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.auras["You can use your Hero Power any number of times"] = GameRuleAura_ColdarraDrake(self)
		
class GameRuleAura_ColdarraDrake(GameRuleAura):
	def auraAppears(self):
		self.entity.Game.status[self.entity.ID]["Power Chance Inf"] += 1
		try: self.entity.Game.powers[self.entity.ID].btn.refresh()
		except: pass
		
	def auraDisappears(self):
		self.entity.Game.status[self.entity.ID]["Power Chance Inf"] -= 1
		try: self.entity.Game.powers[self.entity.ID].btn.refresh()
		except: pass


class Flamestrike(Spell):
	Class, school, name = "Mage", "Fire", "Flamestrike"
	requireTarget, mana = False, 7
	index = "CORE~Mage~Spell~7~Fire~Flamestrike"
	description = "Deal 5 damage to all enemy minions"
	name_CN = "烈焰风暴"
	def text(self, CHN):
		damage = (5 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		return "对所有敌方随从造成%d点伤害"%damage if CHN else "Deal %d damage to all enemy minions"%damage
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		damage = (5 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		targets = self.Game.minionsonBoard(3-self.ID)
		self.dealsAOE(targets, [damage for minion in targets])
		return None
		
"""Paladin Cards"""
class Avenge(Secret):
	Class, school, name = "Paladin", "Holy", "Avenge"
	requireTarget, mana = False, 1
	index = "CORE~Paladin~Spell~1~Holy~Avenge~~Secret"
	description = "Secret: When one of your minion dies, give a random friendly minion +3/+2"
	name_CN = "复仇"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_Avenge(self)]
		
class Trig_Avenge(SecretTrigger):
	def __init__(self, entity):
		super().__init__(entity, ["MinionDies"])
		self.triggered = False
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.ID != self.entity.Game.turn and target.ID == self.entity.ID and self.entity.Game.space(self.entity.ID) > 0 and not self.triggered
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		curGame = self.entity.Game
		if curGame.mode == 0:
			if curGame.guides:
				i = curGame.guides.pop(0)
			else:
				minions = curGame.minionsonBoard(self.entity.ID)
				i = npchoice(minions).pos if minions else -1
				curGame.fixedGuides.append(i)
			if i > -1: curGame.minions[self.entity.ID][i].buffDebuff(3, 2)
			
			
class NobleSacrifice(Secret):
	Class, school, name = "Paladin", "", "Noble Sacrifice"
	requireTarget, mana = False, 1
	index = "CORE~Paladin~Spell~1~~Noble Sacrifice~~Secret"
	description = "Secret: When an enemy attacks, summon a 2/1 Defender as the new target"
	name_CN = "崇高牺牲"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_NobleSacrifice(self)]
		
class Trig_NobleSacrifice(SecretTrigger):
	def __init__(self, entity):
		super().__init__(entity, ["MinionAttacksHero", "MinionAttacksMinion", "HeroAttacksHero", "HeroAttacksMinion"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.ID != self.entity.Game.turn and subject.ID != self.entity.ID and self.entity.Game.space(self.entity.ID) > 0
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		newTarget = Defender(self.entity.Game, self.entity.ID)
		self.entity.Game.summon(newTarget, -1, self.entity)
		target[1] = newTarget
		
	
class Reckoning(Secret):
	Class, school, name = "Paladin", "Holy", "Reckoning"
	requireTarget, mana = False, 1
	index = "CORE~Paladin~Spell~1~Holy~Reckoning~~Secret"
	description = "Secret: When an enemy minion deals 3 or more damage, destroy it"
	name_CN = "清算"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_Reckoning(self)]
		
#假设是被随从一次性造成3点或以上的伤害触发，单发或者AOE伤害均可
class Trig_Reckoning(SecretTrigger):
	def __init__(self, entity):
		super().__init__(entity, ["DealtDmg"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.ID != self.entity.Game.turn and number > 2 \
			and subject.ID != self.entity.ID and subject.type == "Minion" and not subject.dead and subject.health > 0
			
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.Game.killMinion(self.entity, subject)
		
		
class RighteousProtector(Minion):
	Class, race, name = "Paladin", "", "Righteous Protector"
	mana, attack, health = 1, 1, 1
	index = "CORE~Paladin~Minion~1~1~1~~Righteous Protector~Taunt~Divine Shield"
	requireTarget, keyWord, description = False, "Taunt,Divine Shield", "Taunt, Divine Shield"
	name_CN = "正义保护者"
	
	
class ArgentProtector(Minion):
	Class, race, name = "Paladin", "", "Argent Protector"
	mana, attack, health = 2, 3, 2
	index = "CORE~Paladin~Minion~2~3~2~~Argent Protector~Battlecry"
	requireTarget, keyWord, description = True, "", "Battlecry: Give a friendly minion Divine Shield"
	name_CN = "银色保卫者"
	
	def targetExists(self, choice=0):
		return self.selectableFriendlyMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.ID == self.ID and target != self and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target: #The minion's getsStatus() is only effective if minion is onBoard or inHand
			target.getsStatus("Divine Shield")
		return target
		
		
class HolyLight(Spell):
	Class, school, name = "Paladin", "Holy", "Holy Light"
	requireTarget, mana = True, 2
	index = "CORE~Paladin~Spell~2~Holy~Holy Light"
	description = "Restore 8 health"
	name_CN = "圣光术"
	def text(self, CHN):
		heal = 8 * (2 ** self.countHealDouble())
		return "恢复%d点生命值"%heal if CHN else "Restore %d health"%heal
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			heal = 8 * (2 ** self.countHealDouble())
			self.restoresHealth(target, heal)
		return target
		
		
class PursuitofJustice(Spell):
	Class, school, name = "Paladin", "Holy", "Pursuit of Justice"
	requireTarget, mana = False, 2
	index = "CORE~Paladin~Spell~2~Holy~Pursuit of Justice"
	description = "Give +1 Attack to Silver Hand Recruits you summon this game"
	name_CN = "正义追击"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		GameTrigAura_BuffYourRecruits(self.Game, self.ID).auraAppears()
		return None
		
class GameTrigAura_BuffYourRecruits(HasAura_toMinion):
	def __init__(self, Game, ID):
		self.Game, self.ID = Game, ID
		self.auraAffected = []
		self.buff = 1
		
	#All minions appearing on the same side will be subject to the buffAura.
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject.ID == self.ID and subject.name == "Silver Hand Recruit"
		
	def trig(self, signal, ID, subject, target, number, comment, choice=0):
		if self.canTrig(signal, ID, subject, target, number, comment):
			Stat_Receiver(subject, self, self.buff, 0).effectStart()
			
	def text(self, CHN):
		return "在本局对战的剩余时间内，你的白银之手新兵获得+%d攻击力"%self.buff if CHN \
				else "For the rest of the game, your Silver Hand Recruits have +%d Attack"%self.buff
				
	def auraAppears(self):
		trigAuras = self.Game.trigAuras[self.ID]
		for obj in trigAuras:
			if isinstance(obj, GameTrigAura_BuffYourRecruits):
				obj.improve()
				return
		trigAuras.append(self)
		for minion in self.Game.minionsonBoard(self.ID):
			if minion.name == "Silver Hand Recruit": Stat_Receiver(minion, self, self.buff, 0).effectStart()
		try: self.Game.trigsBoard[self.ID]["MinionAppears"].append(self)
		except: pass
	#没有auraDisappear方法
	#可以通过HasAura_toMinion的createCopy方法复制
	def improve(self):
		self.buff += 1
		for minion, receiver in self.auraAffected[:]:
			receiver.effectClear()
		self.auraAffected = []
		for minion in self.Game.minionsonBoard(self.ID):
			if minion.name == "Silver Hand Recruit": Stat_Receiver(minion, self, self.buff, 0).effectStart()
	#这个函数会在复制场上扳机列表的时候被调用。
	def createCopy(self, game):
		#一个光环的注册可能需要注册多个扳机
		if self not in game.copiedObjs: #这个光环没有被复制过
			Copy = GameTrigAura_BuffYourRecruits(self.Game, self.ID)
			game.copiedObjs[self] = Copy
			Copy.buff = self.buff
			for minion, receiver in self.auraAffected:
				minionCopy = minion.createCopy(game)
				index = minion.auraReceivers.index(receiver)
				receiverCopy = minionCopy.auraReceivers[index]
				receiverCopy.source = Copy #补上这个receiver的source
				Copy.auraAffected.append((minionCopy, receiverCopy))
			return Copy
		else:
			return game.copiedObjs[self]
			
			
class AldorPeacekeeper(Minion):
	Class, race, name = "Paladin", "", "Aldor Peacekeeper"
	mana, attack, health = 3, 3, 3
	index = "CORE~Paladin~Minion~3~3~3~~Aldor Peacekeeper~Battlecry"
	requireTarget, keyWord, description = True, "", "Battlecry: Change an enemy minion's Attack to 1"
	name_CN = "奥尔多卫士"
	
	def targetExists(self, choice=0):
		return self.selectableEnemyMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.ID != self.ID and target.onBoard and target != self
		
	#Infer from Houndmaster: Buff can apply on targets on board, in hand, in deck.
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			target.statReset(1, False)
		return target
		
		
class Equality(Spell):
	Class, school, name = "Paladin", "Holy", "Equality"
	requireTarget, mana = False, 3
	index = "CORE~Paladin~Spell~3~Holy~Equality"
	description = "Change the Health of ALL minions to 1"
	name_CN = "生而平等"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		for minion in self.Game.minionsonBoard(1) + self.Game.minionsonBoard(2):
			minion.statReset(False, 1)
		return None
		
		
class WarhorseTrainer(Minion):
	Class, race, name = "Paladin", "", "Warhorse Trainer"
	mana, attack, health = 3, 3, 4
	index = "CORE~Paladin~Minion~3~3~4~~Warhorse Trainer"
	requireTarget, keyWord, description = False, "", "Your Silver Hand Recruits have +1 Attack"
	name_CN = "战马训练师"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.auras["Your other Silver Hand Recruits have +1 Attack"] = StatAura_Others(self, 1, 0)
		
	def applicable(self, target):
		return target.name == "Silver Hand Recruits"
		
		
class BlessingofKings(Spell):
	Class, school, name = "Paladin", "Holy", "Blessing of Kings"
	requireTarget, mana = True, 4
	index = "CORE~Paladin~Spell~4~Holy~Blessing of Kings"
	description = "Give a minion +4/+4"
	name_CN = "王者祝福"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			target.buffDebuff(4, 4)
		return target
		
		
class Consecration(Spell):
	Class, school, name = "Paladin", "Holy", "Consecration"
	requireTarget, mana = False, 4
	index = "CORE~Paladin~Spell~4~Holy~Consecration"
	description = "Deal 2 damage to all enemies"
	name_CN = "奉献"
	def text(self, CHN):
		damage = (2 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		return "对所有敌人造成%d点伤害"%damage if CHN else "Deal %d damage to all enemies"%damage
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		damage = (2 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		targets = [self.Game.heroes[3-self.ID]] + self.Game.minionsonBoard(3-self.ID)
		self.dealsAOE(targets, [damage for obj in targets])
		return None
		
		
class TruesilverChampion(Weapon):
	Class, name, description = "Paladin", "Truesilver Champion", "Whenever your hero attacks, restore 2 Health to it"
	mana, attack, durability = 4, 4, 2
	index = "CORE~Paladin~Weapon~4~4~2~Truesilver Champion"
	name_CN = "真银圣剑"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_TruesilverChampion(self)]
		
class Trig_TruesilverChampion(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["HeroAttackingMinion", "HeroAttackingHero"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject == self.entity.Game.heroes[self.entity.ID] and self.entity.onBoard
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		heal = 2 * (2 ** self.entity.countHealDouble())
		self.entity.restoresHealth(self.entity.Game.heroes[self.entity.ID], heal)
		
	def text(self, CHN):
		heal = 2 * (2 ** self.entity.countHealDouble())
		return "每当你的英雄进攻，便为其恢复%d点生命值"%heal if CHN else "Whenever your hero attacks, restore %d Health to it"%heal
		
		
class StandAgainstDarkness(Spell):
	Class, school, name = "Paladin", "", "Stand Against Darkness"
	requireTarget, mana = False, 5
	index = "CORE~Paladin~Spell~5~~Stand Against Darkness"
	description = "Summon five 1/1 Silver Hand Recruits"
	name_CN = "惩黑除恶"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.Game.summon([SilverHandRecruit(self.Game, self.ID) for i in range(5)], (-1, "totheRightEnd"), self)
		return None
		
		
class GuardianofKings(Minion):
	Class, race, name = "Paladin", "", "Guardian of Kings"
	mana, attack, health = 7, 5, 7
	index = "CORE~Paladin~Minion~7~5~7~~Guardian of Kings~Taunt~Battlecry"
	requireTarget, keyWord, description = False, "Taunt", "Taunt. Battlecry: Restore 6 health to your hero"
	name_CN = "列王守卫"
	
	def text(self, CHN):
		heal = 6 * (2 ** self.countHealDouble())
		return "战吼：为你的英雄恢复%d点生命值"%heal if CHN else "Battlecry: Restore %d health to your hero"%heal
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		heal = 6 * (2 ** self.countHealDouble())
		self.restoresHealth(self.Game.heroes[self.ID], heal)
		return None
		
		
class TirionFordring(Minion):
	Class, race, name = "Paladin", "", "Tirion Fordring"
	mana, attack, health = 8, 6, 6
	index = "CORE~Paladin~Minion~8~6~6~~Tirion Fordring~Taunt~Divine Shield~Deathrattle~Legendary"
	requireTarget, keyWord, description = False, "Divine Shield,Taunt", "Divine Shield, Taunt. Deathrattle: Equip a 5/3 Ashbringer"
	name_CN = "提里昂弗丁"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.deathrattles = [EquipAshbringer(self)]
		
class EquipAshbringer(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.Game.equipWeapon(Ashbringer(self.entity.Game, self.entity.ID))
		
	def text(self, CHN):
		return "亡语：装备一把5/3的灰烬使者" if CHN else "Deathrattle: Equip a 5/3 Ashbringer"
		
	
"""Priest Cards"""
class CrimsonClergy(Minion):
	Class, race, name = "Priest", "", "Crimson Clergy"
	mana, attack, health = 1, 1 ,3
	index = "CORE~Priest~Minion~1~1~3~~Crimson Clergy"
	requireTarget, keyWord, description = False, "", "After a friendly character is healed, gain +1 Attack"
	name_CN = "赤红教士"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_LightWarden(self)]
		
class Trig_LightWarden(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["MinionGotHealed", "HeroGotHealed"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject.ID == self.entity.ID
		
	def text(self, CHN):
		return "在一个友方角色获得治疗后，便获得+1攻击力" if CHN else "After a friendly character is healed, gain +1 Attack"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.buffDebuff(1, 0)
		
		
class FlashHeal(Spell):
	Class, school, name = "Priest", "Holy", "Flash Heal"
	requireTarget, mana = True, 1
	index = "CORE~Priest~Spell~1~Holy~Flash Heal"
	description = "Restore 5 Health"
	name_CN = "快速治疗"
	def text(self, CHN):
		heal = 5 * (2 ** self.countHealDouble())
		return "恢复%d生命值"%heal if CHN else "Restore %d Health"%heal
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			self.restoresHealth(target, 5 * (2 ** self.countHealDouble()))
		return target
		
		
class FocusedWill(Spell):
	Class, school, name = "Priest", "", "Focused Will"
	requireTarget, mana = True, 1
	index = "CORE~Priest~Spell~1~~Focused Will"
	description = "Silence a minion, then give it +3 Health"
	name_CN = "专注意志"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			target.getsSilenced()
			target.buffDebuff(0, 3)
		return target
		
		
class HolySmite(Spell):
	Class, school, name = "Priest", "Holy", "Holy Smite"
	requireTarget, mana = True, 1
	index = "CORE~Priest~Spell~1~Holy~Holy Smite"
	description = "Deal 3 damage to a minion"
	name_CN = "神圣惩击"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
		
	def text(self, CHN):
		damage = (3 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		return "对一个随从造成%d点伤害"%damage if CHN else "Deal %d damage to a minion"%damage
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			damage = (3 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			self.dealsDamage(target, damage)
		return target
		
		
class PsychicConjurer(Minion):
	Class, race, name = "Priest", "", "Psychic Conjurer"
	mana, attack, health = 1, 1, 1
	index = "CORE~Priest~Minion~1~1~1~~Psychic Conjurer~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Copy a card in your opponent's deck and add it to your hand"
	name_CN = "心灵咒术师"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		enemyDeck = curGame.Hand_Deck.decks[3-self.ID]
		if curGame.mode == 0:
			pool = tuple(possi[1][0] for possi in curGame.Hand_Deck.cards_1Possi[3-self.ID] if len(possi) == 1)
			if curGame.guides:
				i = curGame.guides.pop(0)
			else:
				i = nprandint(len(enemyDeck)) if enemyDeck else -1
				curGame.fixedGuides.append(i)
			if i > -1: curGame.Hand_Deck.addCardtoHand(enemyDeck[i].selfCopy(self.ID, self), self.ID, creator=type(self), possi=pool)
		return None
		
		
class ShadowWordDeath(Spell):
	Class, school, name = "Priest", "Shadow", "Shadow Word: Death"
	requireTarget, mana = True, 2
	index = "CORE~Priest~Spell~2~Shadow~Shadow Word: Death"
	description = "Destroy a minion with 5 or more Attack"
	name_CN = "暗言术：灭"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.attack > 4 and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			self.Game.killMinion(self, target)
		return target
		
		
class ThriveintheShadows(Spell):
	Class, school, name = "Priest", "Shadow", "Thrive in the Shadows"
	requireTarget, mana = False, 2
	index = "CORE~Priest~Spell~2~Shadow~Thrive in the Shadows"
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
					if len(inds) > 1:
						curGame.options = [ownDeck[i] for i in inds]
						curGame.Discover.startDiscover(self)
					else:
						i = inds[0] if inds else -1
						curGame.fixedGuides.append(i)
						if i > -1: curGame.Hand_Deck.drawCard(self.ID, i)
		return None
		
	def discoverDecided(self, option, pool):
		i = self.Game.Hand_Deck.decks[self.ID].index(option)
		self.Game.fixedGuides.append(i)
		self.Game.Hand_Deck.drawCard(self.ID, i)
		
		
class Lightspawn(Minion):
	Class, race, name = "Priest", "Elemental", "Lightspawn"
	mana, attack, health = 3, 0, 4
	index = "CORE~Priest~Minion~3~0~4~Elemental~Lightspawn"
	requireTarget, keyWord, description = False, "", "This minion's Attack is always equal to its Health"
	name_CN = "光耀之子"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.auras["This minion's Attack is always equal to its Health"] = StatAura_Lightspawn(self)
		
class StatAura_Lightspawn:
	def __init__(self, entity):
		self.entity = entity
		
	#光环开启和关闭都取消，因为要依靠随从自己的handleEnrage来触发
	def auraAppears(self):
		minion = self.entity
		try: minion.Game.trigsBoard[minion.ID]["MinionStatCheck"].append(self)
		except: minion.Game.trigsBoard[minion.ID]["MinionStatCheck"] = [self]
		stat_Receivers = [receiver for receiver in minion.auraReceivers if isinstance(receiver, Stat_Receiver)]
		# 将随从上的全部buffAura清除，因为部分光环的适用条件可能会因为随从被沉默而变化，如战歌指挥官
		for receiver in stat_Receivers: receiver.effectClear()
		self.tempAttChanges = []  # Clear the temp attack changes on the minion.
		self.attack = self.attack_Enchant = minion.health
		for receiver in stat_Receivers:
			receiver.source.applies(self)
		if minion.btn: minion.btn.statChangeAni(action="set")
		
	def auraDisappears(self):
		try: self.entity.Game.trigsBoard[self.entity.ID]["MinionStatCheck"].remove(self)
		except: pass
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return target == self.entity and target.onBoard
	
	def trig(self, signal, ID, subject, target, number, comment, choice=0):
		if self.canTrig(signal, ID, subject, target, number, comment):
			self.entity.attack = self.entity.health
			
	def selfCopy(self, recipient):  #The recipientMinion is the entity that deals the Aura.
		return type(self)(recipient)
		
		
class ShadowedSpirit(Minion):
	Class, race, name = "Priest", "", "Shadowed Spirit"
	mana, attack, health = 3, 4, 3
	index = "CORE~Priest~Minion~3~4~3~~Shadowed Spirit~Deathrattle"
	requireTarget, keyWord, description = False, "", "Deathrattle: Deal 3 damage to the enemy hero"
	name_CN = "暗影之灵"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.deathrattles = [Deal3DamagetoEnemyHero(self)]

class Deal3DamagetoEnemyHero(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.dealsDamage(self.entity.Game.heroes[self.entity.ID], 3)
	
	def text(self, CHN):
		return "亡语：对敌方英雄造成3点伤害" if CHN else "Deathrattle: Deal 3 damage to the enemy hero"


class Shadowform(Spell):
	Class, school, name = "Priest", "Shadow", "Shadowform"
	needTarget, mana = False, 2
	index = "CORE~Priest~Spell~2~Shadow~Shadowform"
	description = "Your Hero Power becomes 'Deal 2 damage'"
	name_CN = "暗影形态"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		MindSpike(self.Game, self.ID).replaceHeroPower()
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
		damage = (2 + self.marks["Damage Boost"] + self.Game.status[self.ID]["Power Damage"]) * (2 ** self.countDamageDouble())
		dmgTaker, damageActual = self.dealsDamage(target, damage)
		if dmgTaker.health < 1 or dmgTaker.dead: return 1
		return 0
		
		
class HolyNova(Spell):
	Class, school, name = "Priest", "Holy", "Holy Nova"
	requireTarget, mana = False, 4
	index = "CORE~Priest~Spell~4~Holy~Holy Nova"
	description = "Deal 2 damage to all enemy minions. Restore 2 Health to all friendly characters"
	name_CN = "神圣新星"
	def text(self, CHN):
		damage = (2 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		heal = 2 * (2 ** self.countHealDouble())
		return "对所有敌方随从造成%d点伤害，为所有友方角色恢复%d生命值"%(damage, heal) if CHN \
				else "Deal %d damage to all enemy minions. Restore %d Health to all friendly characters"%(damage, heal)
				
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		damage = (2 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		heal = 2 * (2 ** self.countHealDouble())
		enemies = self.Game.minionsonBoard(3-self.ID)
		friendlies = [self.Game.heroes[self.ID]] + self.Game.minionsonBoard(self.ID)
		self.dealsAOE(enemies, [damage]*len(enemies))
		self.restoresAOE(friendlies, [heal]*len(friendlies))
		return None
		
		
class PowerInfusion(Spell):
	Class, school, name = "Priest", "Holy", "Power Infusion"
	requireTarget, mana = True, 4
	index = "CORE~Priest~Spell~4~Holy~Power Infusion"
	description = "Give a minion +2/+6"
	name_CN = "能量灌注"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			target.buffDebuff(2, 6)
		return target
		
		
class ShadowWordRuin(Spell):
	Class, school, name = "Priest", "Shadow", "Shadow Word: Ruin"
	requireTarget, mana = False, 4
	index = "CORE~Priest~Spell~4~Shadow~Shadow Word: Ruin"
	description = "Destroy all minions with 5 or more Attack"
	name_CN = "暗言术：毁"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.Game.killMinion(self, [minion for minion in self.Game.minionsonBoard(1) + self.Game.minionsonBoard(2) if minion.attack > 4])
		return None
		
		
class TempleEnforcer(Minion):
	Class, race, name = "Priest", "", "Temple Enforcer"
	mana, attack, health = 5, 5, 6
	index = "CORE~Priest~Minion~5~5~6~~Temple Enforcer~Battlecry"
	requireTarget, keyWord, description = True, "", "Battlecry: Give a friendly minion +3 health"
	name_CN = "圣殿执行者"
	
	def targetExists(self, choice=0):
		return self.selectableFriendlyMinionExists(choice)
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.ID == self.ID and target != self and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			target.buffDebuff(0, 3)
		return target
		
		
class NatalieSeline(Minion):
	Class, race, name = "Priest", "", "Natalie Seline"
	mana, attack, health = 8, 8, 1
	index = "CORE~Priest~Minion~8~8~1~~Natalie Seline~Battlecry~Legendary"
	requireTarget, keyWord, description = True, "", "Battlecry: Destroy a minion and gain its Health"
	name_CN = "娜塔莉塞林"
	
	def targetExists(self, choice=0):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target != self and target.onBoard
		
	#If the minion is shuffled into deck already, then nothing happens.
	#If the minion is returned to hand, move it from enemy hand into our hand.
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			healthGain = max(0, target.health)
			self.Game.killMinion(self, target)
			self.buffDebuff(0, healthGain)
		return target
		
"""Rogue Cards"""
class Backstab(Spell):
	Class, school, name = "Rogue", "", "Backstab"
	requireTarget, mana = True, 0
	index = "CORE~Rogue~Spell~0~~Backstab"
	description = "Deal 2 damage to an undamage minion"
	name_CN = "背刺"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.health == target.health_max and target.onBoard
		
	def text(self, CHN):
		damage = (2 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		return "对一个未受伤的随从造成%d点伤害"%damage if CHN else "Deal %d damage to an undamage minion"%damage
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			damage = (2 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			self.dealsDamage(target, damage)
		return target
		
		
class Preparation(Spell):
	Class, school, name = "Rogue", "", "Preparation"
	requireTarget, mana = False, 0
	index = "CORE~Rogue~Spell~0~Preparation"
	description = "The next spell you cast this turn costs (2) less"
	name_CN = "伺机待发"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		tempAura = GameManaAura_InTurnNextSpell2Less(self.Game, self.ID)
		self.Game.Manas.CardAuras.append(tempAura)
		tempAura.auraAppears()
		return None
		
class GameManaAura_InTurnNextSpell2Less(TempManaEffect):
	def __init__(self, Game, ID, changeby=0, changeto=-1):
		super().__init__(Game, ID, -2, -1)
		
	def applicable(self, target):
		return target.ID == self.ID and target.type == "Spell"
		
		
class Shadowstep(Spell):
	Class, school, name = "Rogue", "Shadow", "Shadowstep"
	requireTarget, mana = True, 0
	index = "CORE~Rogue~Spell~0~Shadow~Shadowstep"
	description = "Return a friendly minion to your hand. It costs (2) less"
	name_CN = "暗影步"
	def targetExists(self, choice=0):
		return self.selectableFriendlyMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.ID == self.ID and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		#假设暗影步第二次生效时不会不在场上的随从生效
		if target and target.onBoard:
			#假设那张随从在进入手牌前接受-2费效果。可以被娜迦海巫覆盖。
			manaMod = ManaMod(target, changeby=-2, changeto=-1)
			self.Game.returnMiniontoHand(target, deathrattlesStayArmed=False, manaMod=manaMod)
		return target
		
		
class BladedCultist(Minion):
	Class, race, name = "Rogue", "", "Bladed Cultist"
	mana, attack, health = 1, 1, 2
	index = "CORE~Rogue~Minion~1~1~2~~Bladed Cultist~Combo"
	requireTarget, keyWord, description = False, "", "Combo: Gain +1/+1"
	name_CN = "执刃教徒"
	
	def effCanTrig(self):
		self.effectViable = self.Game.Counters.numCardsPlayedThisTurn[self.ID] > 0
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		#Dead minions or minions in deck can't be buffed or reset.
		if self.Game.Counters.numCardsPlayedThisTurn[self.ID] > 0:
			self.buffDebuff(1, 1)
		return None
		
		
class DeadlyPoison(Spell):
	Class, school, name = "Rogue", "Nature", "Deadly Poison"
	requireTarget, mana = False, 1
	index = "CORE~Rogue~Spell~1~Nature~Deadly Poison"
	description = "Give your weapon +2 Attack"
	name_CN = "致命药膏"
	def available(self):
		return self.Game.availableWeapon(self.ID) is not None
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		weapon = self.Game.availableWeapon(self.ID)
		if weapon:
			weapon.gainStat(2, 0)
		return None
		
		
class SinisterStrike(Spell):
	Class, school, name = "Rogue", "", "Sinister Strike"
	requireTarget, mana = False, 1
	index = "CORE~Rogue~Spell~1~Sinister Strike"
	description = "Deal 3 damage to the enemy hero"
	name_CN = "影袭"
	def text(self, CHN):
		damage = (3 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		return "对敌方英雄造成%d点伤害"%damage if CHN else "Deal %d damage to the enemy hero"%damage
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		damage = (3 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		self.dealsDamage(self.Game.heroes[3-self.ID], damage)
		return None
		
		
class Swashburglar(Minion):
	Class, race, name = "Rogue", "Pirate", "Swashburglar"
	mana, attack, health = 1, 1, 1
	index = "CORE~Rogue~Minion~1~1~1~Pirate~Swashburglar~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Add a random card from another class to your hand"
	name_CN = "吹嘘海盗"
	poolIdentifier = "Rogue Cards"
	@classmethod
	def generatePool(cls, pools):
		return ["%s Cards"%Class for Class in pools.Classes]+["Classes"], \
				[list(pools.ClassCards[Class].values()) for Class in pools.Classes]+[pools.Classes]
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if curGame.mode == 0:
			classes = self.rngPool("Classes")[:]
			try: classes.remove(curGame.heroes[self.ID].Class)
			except: pass
			pool = []
			for Class in classes:
				pool += self.rngPool("%s Cards"%Class)
			pool = tuple(pool)
			if curGame.guides:
				card = curGame.guides.pop(0)
			else:
				card = npchoice(self.rngPool("%s Cards"%npchoice(classes)))
				curGame.fixedGuides.append(card)
			curGame.Hand_Deck.addCardtoHand(card, self.ID, byType=True, creator=type(self), possi=pool)
		return None
		
		
class ColdBlood(Spell):
	Class, school, name = "Rogue", "", "Cold Blood"
	requireTarget, mana = True, 2
	index = "CORE~Rogue~Spell~2~~Cold Blood~Combo"
	description = "Give a minion +2 Attack. Combo: +4 Attack instead"
	name_CN = "冷血"
	def effCanTrig(self):
		self.effectViable = self.Game.Counters.numCardsPlayedThisTurn[self.ID] > 0
		
	def targetExists(self, choice=0):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			if self.Game.Counters.numCardsPlayedThisTurn[self.ID] > 0:
				target.buffDebuff(4, 0)
			else:
				target.buffDebuff(2, 0)
		return target
		
		
class PatientAssassin(Minion):
	Class, race, name = "Rogue", "", "Patient Assassin"
	mana, attack, health = 2, 1, 2
	index = "CORE~Rogue~Minion~2~1~2~~Patient Assassin~Poisonous~Stealth"
	requireTarget, keyWord, description = False, "Stealth,Poisonous", "Stealth, Poisonous"
	name_CN = "耐心的刺客"
	
	
class VanessaVanCleef(Minion):
	Class, race, name = "Rogue", "", "Vanessa VanCleef"
	mana, attack, health = 2, 2, 3
	index = "CORE~Rogue~Minion~2~2~3~~Vanessa VanCleef~Combo~Legendary"
	requireTarget, keyWord, description = False, "", "Combo: Add a copy of the last card your opponent played to your hand"
	name_CN = "梵妮莎·范克里夫"
	
	def effCanTrig(self):
		self.effectViable = self.Game.Counters.numCardsPlayedThisTurn[self.ID] > 0
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if self.Game.Counters.numCardsPlayedThisTurn[self.ID] > 0:
			try:
				index = self.Game.Counters.cardsPlayedThisGame[3-self.ID][-1]
				self.Game.Hand_Deck.addCardtoHand(self.Game.cardPool[index], self.ID, byType=True, creator=type(self))
			except: pass
		return None
		
		
class PlagueScientist(Minion):
	Class, race, name = "Rogue", "", "Plague Scientist"
	mana, attack, health = 3, 2, 3
	index = "CORE~Rogue~Minion~3~2~3~~Plague Scientist~Combo"
	requireTarget, keyWord, description = True, "", "Combo: Give a friendly minion Poisonous"
	name_CN = "瘟疫科学家"
	
	def returnTrue(self, choice=0):
		return self.Game.Counters.numCardsPlayedThisTurn[self.ID] > 0
		
	def effCanTrig(self):
		self.effectViable = self.Game.Counters.numCardsPlayedThisTurn[self.ID] > 0
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.ID == self.ID and target != self and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target and self.Game.Counters.numCardsPlayedThisTurn[self.ID] > 0:
			target.getsStatus("Poisonous")
		return target
		
		

class SI7Agent(Minion):
	Class, race, name = "Rogue", "", "SI:7 Agent"
	mana, attack, health = 3, 3, 3
	index = "CORE~Rogue~Minion~3~3~3~~SI:7 Agent~Combo"
	requireTarget, keyWord, description = True, "", "Combo: Deal 2 damage"
	name_CN = "军情七处特工"
	
	def returnTrue(self, choice=0):
		return self.Game.Counters.numCardsPlayedThisTurn[self.ID] > 0
		
	def effCanTrig(self):
		self.effectViable = self.Game.Counters.numCardsPlayedThisTurn[self.ID] > 0
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target and self.Game.Counters.numCardsPlayedThisTurn[self.ID] > 0:
			self.dealsDamage(target, 2)
		return target
		
		
class Assassinate(Spell):
	Class, school, name = "Rogue", "", "Assassinate"
	requireTarget, mana = True, 4
	index = "CORE~Rogue~Spell~4~~Assassinate"
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
		
		
class AssassinsBlade(Weapon):
	Class, name, description = "Rogue", "Assassin's Blade", ""
	mana, attack, durability = 4, 2, 5
	index = "CORE~Rogue~Weapon~4~2~5~Assassin's Blade"
	name_CN = "刺客之刃"
	
	
class TombPillager(Minion):
	Class, race, name = "Rogue", "", "Tomb Pillager"
	mana, attack, health = 4, 5, 4
	index = "CORE~Rogue~Minion~4~5~4~~Tomb Pillager~Deathrattle"
	requireTarget, keyWord, description = False, "", "Deathrattle: Add a Coin to your hand"
	name_CN = "盗墓匪贼"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.deathrattles = [AddaCointoHand(self)]
		
class AddaCointoHand(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.Game.Hand_Deck.addCardtoHand(TheCoin, self.entity.ID, byType=True, creator=type(self.entity))
		
	def text(self, CHN):
		return "亡语：将一个幸运币置入你的手牌" if CHN else "Deathrattle: Add a Coin to your hand"
		
		
class Sprint(Spell):
	Class, school, name = "Rogue", "", "Sprint"
	requireTarget, mana = False, 6
	index = "CORE~Rogue~Spell~6~~Sprint"
	description = "Draw 4 cards"
	name_CN = "疾跑"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		for num in range(4):
			self.Game.Hand_Deck.drawCard(self.ID)
		return None
		
		
"""Shaman Cards"""
class LightningBolt(Spell):
	Class, school, name = "Shaman", "Nature", "Lightning Bolt"
	requireTarget, mana = True, 1
	index = "CORE~Shaman~Spell~1~Nature~Lightning Bolt~Overload"
	description = "Deal 3 damage. Overload: (1)"
	name_CN = "闪电箭"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.overload = 1
		
	def text(self, CHN):
		damage = (3 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		return "造成%d点伤害。过载： (1)"%damage if CHN else "Deal %d damage. Overload: (1)"%damage
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			damage = (3 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			self.dealsDamage(target, damage)
		return target
		
		
class MenacingNimbus(Minion):
	Class, race, name = "Shaman", "Elemental", "Menacing Nimbus"
	mana, attack, health = 2, 2, 2
	index = "CORE~Shaman~Minion~2~2~2~Elemental~Menacing Nimbus~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Add a random Elemental minion to your hand"
	name_CN = "凶恶的雨云"
	poolIdentifier = "Elementals"
	@classmethod
	def generatePool(cls, pools):
		return "Elementals", list(pools.MinionswithRace["Elemental"].values())
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if curGame.mode == 0:
			pool = tuple(self.rngPool("Elementals"))
			if curGame.guides:
				minion = curGame.guides.pop(0)
			else:
				minion = npchoice(pool)
				curGame.fixedGuides.append(minion)
			curGame.Hand_Deck.addCardtoHand(minion, self.ID, byType=True, creator=type(self), possi=pool)
		return None
		
		
class NoviceZapper(Minion):
	Class, race, name = "Shaman", "", "Novice Zapper"
	mana, attack, health = 1, 3, 2
	index = "CORE~Shaman~Minion~1~3~2~~Novice Zapper~Spell Damage~Overload"
	requireTarget, keyWord, description = False, "Spell Damage", "Spell Damage +1. Overload: (1)"
	name_CN = "电击学徒"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.overload = 1
		
		
class RockbiterWeapon(Spell):
	Class, school, name = "Shaman", "Nature", "Rockbiter Weapon"
	requireTarget, mana = True, 2
	index = "CORE~Shaman~Spell~2~Nature~Rockbiter Weapon"
	description = "Give a friendly character +3 Attack this turn"
	name_CN = "石化武器"
	def available(self):
		return self.selectableFriendlyExists()
		
	def targetCorrect(self, target, choice=0):
		return (target.type == "Minion" or target.type == "Hero") and target.ID == self.ID and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			if target.type == "Hero":
				target.gainAttack(3)
			else:
				target.buffDebuff(3, 0, "EndofTurn")
		return target
		
		
class Windfury(Spell):
	Class, school, name = "Shaman", "Nature", "Windfury"
	requireTarget, mana = True, 2
	index = "CORE~Shaman~Spell~2~Nature~Windfury"
	description = "Give a minion Windfury"
	name_CN = "风怒"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			target.getsStatus("Windfury")
		return target
		
		

class FeralSpirit(Spell):
	Class, school, name = "Shaman", "", "Feral Spirit"
	requireTarget, mana = False, 3
	index = "CORE~Shaman~Spell~3~~Feral Spirit~Overload"
	description = "Summon two 2/3 Spirit Wolves with Taunt. Overload: (1)"
	name_CN = "野性狼魂"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.overload = 1
		
	def available(self):
		return self.Game.space(self.ID) > 0
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.Game.summon([SpiritWolf(self.Game, self.ID) for i in range(2)], (-1, "totheRightEnd"), self)
		return None
		
	
class LightningStorm(Spell):
	Class, school, name = "Shaman", "Nature", "Lightning Storm"
	requireTarget, mana = False, 3
	index = "CORE~Shaman~Spell~3~Nature~Lightning Storm~Overload"
	description = "Deal 3 damage to all enemy minions. Overload: (2)"
	name_CN = "闪电风暴"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
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
		
		
class ManaTideTotem(Minion):
	Class, race, name = "Shaman", "Totem", "Mana Tide Totem"
	mana, attack, health = 3, 0, 3
	index = "CORE~Shaman~Minion~3~0~3~Totem~Mana Tide Totem"
	requireTarget, keyWord, description = False, "", "At the end of your turn, draw a card"
	name_CN = "法力之潮图腾"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_ManaTideTotem(self)]
		
class Trig_ManaTideTotem(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["TurnEnds"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and ID == self.entity.ID
		
	def text(self, CHN):
		return "在你的回合结束时，抽一张牌" if CHN else "At the end of your turn, draw a card"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.Game.Hand_Deck.drawCard(self.entity.ID)
		
		
class UnboundElemental(Minion):
	Class, race, name = "Shaman", "Elemental", "Unbound Elemental"
	mana, attack, health = 3, 2, 4
	index = "CORE~Shaman~Minion~3~2~4~Elemental~Unbound Elemental"
	requireTarget, keyWord, description = False, "", "Whenever you play a card with Overload, gain +1/+1"
	name_CN = "无羁元素"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_UnboundElemental(self)]
		
class Trig_UnboundElemental(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["MinionPlayed", "SpellPlayed", "WeaponPlayed", "HeroCardPlayed"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject.ID == self.entity.ID and subject.overload > 0
		
	def text(self, CHN):
		return "每当你使用一张具有过载的牌，便获得+1/+1" if CHN else "Whenever you play a card with Overload, gain +1/+1"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.buffDebuff(1, 1)
		
		
class DraeneiTotemcarver(Minion):
	Class, race, name = "Shaman", "", "Draenei Totemcarver"
	mana, attack, health = 4, 4, 5
	index = "CORE~Shaman~Minion~4~4~5~~Draenei Totemcarver~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Gain +1/+1 for each friendly Totem"
	name_CN = "德莱尼图腾师"
	
	#For self buffing effects, being dead and removed before battlecry will prevent the battlecry resolution.
	#If this minion is returned hand before battlecry, it can still buff it self according to living friendly minions.
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if self.onBoard or self.inHand: #For now, no battlecry resolution shuffles this into deck.
			num = sum("Totem" in minion.race for minion in self.Game.minionsonBoard(self.ID))
			self.buffDebuff(num, num)
		return None
		
		
class Hex(Spell):
	Class, school, name = "Shaman", "Nature", "Hex"
	requireTarget, mana = True, 4
	index = "CORE~Shaman~Spell~4~Nature~Hex"
	description = "Transform a minion into a 0/1 Frog with Taunt"
	name_CN = "妖术"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			newMinion = Frog(self.Game, target.ID)
			self.Game.transform(target, newMinion)
			target = newMinion
		return target
		

class TidalSurge(Spell):
	Class, school, name = "Shaman", "Nature", "Tidal Surge"
	requireTarget, mana = True, 4
	index = "CORE~Shaman~Spell~4~Nature~Tidal Surge"
	description = "Lifesteal. Deal 4 damage to a minion"
	name_CN = "海潮涌动"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.keyWords["Lifesteal"] = 1
		
	def targetExists(self, choice=0):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
		
	def text(self, CHN):
		damage = (4 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		return "吸血。 对一个随从造成%d点伤害"%damage if CHN else "Lifesteal. Deal %d damage to a minion"%damage
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			damage = (4 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			self.dealsDamage(target, damage)
		return target
		
		
class Doomhammer(Weapon):
	Class, name, description = "Shaman", "Doomhammer", "Windfury, Overload: (2)"
	mana, attack, durability = 5, 2, 8
	index = "CORE~Shaman~Weapon~5~2~8~Doomhammer~Windfury~Overload"
	name_CN = "毁灭之锤"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.keyWords["Windfury"] = 1
		self.overload = 2
		
		
class EarthElemental(Minion):
	Class, race, name = "Shaman", "Elemental", "Earth Elemental"
	mana, attack, health = 5, 7, 8
	index = "CORE~Shaman~Minion~5~7~8~Elemental~Earth Elemental~Taunt~Overload"
	requireTarget, keyWord, description = False, "Taunt", "Taunt. Overload: (2)"
	name_CN = "土元素"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.overload = 2
		
		
class FireElemental(Minion):
	Class, race, name = "Shaman", "Elemental", "Fire Elemental"
	mana, attack, health = 6, 6, 5
	index = "CORE~Shaman~Minion~6~6~5~Elemental~Fire Elemental~Battlecry"
	requireTarget, keyWord, description = True, "", "Battlecry: Deal 4 damage"
	name_CN = "火元素"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			self.dealsDamage(target, 4)
		return target
		
		
class AlAkirtheWindlord(Minion):
	Class, race, name = "Shaman", "Elemental", "Al'Akir the Windlord"
	mana, attack, health = 8, 3, 6
	index = "CORE~Shaman~Minion~8~3~6~Elemental~Al'Akir the Windlord~Taunt~Charge~Windfury~Divine Shield~Legendary"
	requireTarget, keyWord, description = False, "Taunt,Charge,Divine Shield,Windfury", "Taunt,Charge,Divine Shield,Windfury"
	name_CN = "风领主奥拉基尔"
	
	
"""Warlock Cards"""
class RitualofDoom(Spell):
	Class, school, name = "Warlock", "Shadow", "Ritual of Doom"
	requireTarget, mana = True, 0
	index = "CORE~Warlock~Spell~0~Shadow~Ritual of Doom"
	description = "Destroy a friendly minion. If you had 5 or more, summon a 5/5 Demon"
	name_CN = "末日仪式"
	def available(self):
		return self.selectableFriendlyMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.ID == self.ID
		
	def effCanTrig(self):
		self.effectViable = len(self.Game.minionsonBoard(self.ID)) > 4
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			hadEnoughMinions = len(self.Game.minionsonBoard(self.ID)) > 4
			self.Game.killMinion(self, target)
			self.Game.gathertheDead()
			if hadEnoughMinions:
				self.Game.summon(DemonicTyrant(self.Game, self.ID), -1, self)
		return target
		
class DemonicTyrant(Minion):
	Class, race, name = "Warlock", "Demon", "Demonic Tyrant"
	mana, attack, health = 5, 5, 5
	index = "CORE~Warlock~Minion~5~5~5~Demon~Demonic Tyrant~Uncollectible"
	requireTarget, keyWord, description = False, "", ""
	name_CN = "恶魔暴君"
	
	
class FlameImp(Minion):
	Class, race, name = "Warlock", "Demon", "Flame Imp"
	mana, attack, health = 1, 3, 2
	index = "CORE~Warlock~Minion~1~3~2~Demon~Flame Imp~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Deal 3 damage to your hero"
	name_CN = "烈焰小鬼"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.dealsDamage(self.Game.heroes[self.ID], 3)
		return None
		
		
class MortalCoil(Spell):
	Class, school, name = "Warlock", "Shadow", "Mortal Coil"
	requireTarget, mana = True, 1
	index = "CORE~Warlock~Spell~1~Shadow~Mortal Coil"
	description = "Deal 1 damage to a minion. If that kills it, draw a card"
	name_CN = "死亡缠绕"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
		
	def text(self, CHN):
		damage = (1 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		return "对一个随从造成%d点伤害。如果‘死亡缠绕’消灭该随从，抽一张牌"%damage if CHN else "Deal %d damage to a minion. If that kills it, draw a card"%damage
		
	#When cast by Archmage Vargoth, this spell can target minions with health <=0 and automatically meet the requirement of killing.
	#If the target minion dies before this spell takes effect, due to being killed by Violet Teacher/Knife Juggler, Mortal Coil still lets
	#player draw a card.
	#If the target is None due to Mayor Noggenfogger's randomization, nothing happens.
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			damage = (1 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			dmgTaker, damageActual = self.dealsDamage(target, damage)
			if dmgTaker.health < 1 or dmgTaker.dead:
				self.Game.Hand_Deck.drawCard(self.ID)
		return target
		
		
class PossessedVillager(Minion):
	Class, race, name = "Warlock", "", "Possessed Villager"
	mana, attack, health = 1, 1, 1
	index = "CORE~Warlock~Minion~1~1~1~~Possessed Villager~Deathrattle"
	requireTarget, keyWord, description = False, "", "Deathrattle: Summon a 1/1 Shadow Beast"
	name_CN = "着魔村民"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.deathrattles = [SummonaShadowbeast(self)]
		
class SummonaShadowbeast(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.Game.summon(Shadowbeast(self.entity.Game, self.entity.ID), self.entity.pos+1, self.entity)
		
	def text(self, CHN):
		return "亡语：召唤一个1/1的暗影兽" if CHN else "Deathrattle: Summon a 1/1 Shadow Beast"
		
	
class DrainSoul(Spell):
	Class, school, name = "Warlock", "Shadow", "Drain Soul"
	requireTarget, mana = True, 2
	index = "CORE~Warlock~Spell~2~Shadow~Drain Soul"
	description = "Lifesteal. Deal 3 damage to a minion"
	name_CN = "吸取灵魂"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.keyWords["Lifesteal"] = 1
		
	def targetExists(self, choice=0):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
		
	def text(self, CHN):
		damage = (3 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		return "吸血。 对一个随从造成%d点伤害"%damage if CHN else "Lifesteal. Deal %d damage to a minion"%damage
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			damage = (3 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			self.dealsDamage(target, damage)
		return target
		
		
class TinyKnightofEvil(Minion):
	Class, race, name = "Warlock", "Demon", "Tiny Knight of Evil"
	mana, attack, health = 2, 3, 2
	index = "CORE~Warlock~Minion~2~3~2~Demon~Tiny Knight of Evil"
	requireTarget, keyWord, description = False, "", "Whenever your discard a card, gain +1/+1"
	name_CN = "小鬼骑士"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_TinyKnightofEvil(self)]
		
class Trig_TinyKnightofEvil(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["CardDiscarded"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and ID == self.entity.ID
		
	def text(self, CHN):
		return "每当你弃掉一张牌时，便获得+1/+1" if CHN else "Whenever your discard a card, gain +1/+1"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.buffDebuff(1, 1)
		
		
class VoidTerror(Minion):
	Class, race, name = "Warlock", "Demon", "Void Terror"
	mana, attack, health = 3, 3, 4
	index = "CORE~Warlock~Minion~3~3~4~Demon~Void Terror~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Destroy both adjacent minions and gain their Attack and Health"
	name_CN = "虚空恐魔"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if self.onBoard: #Can't trigger if returned to hand already, since cards in hand don't have adjacent minions on board.
			neighbors, distribution = self.Game.neighbors2(self)
			if neighbors:
				attackGain, healthGain = 0, 0
				for minion in neighbors:
					attackGain += max(0, minion.attack)
					healthGain += max(0, minion.health)
				self.Game.killMinion(self, neighbors)
				self.buffDebuff(attackGain, healthGain)
		return None
		
		
class FiendishCircle(Spell):
	Class, school, name = "Warlock", "Fel", "Fiendish Circle"
	requireTarget, mana = False, 4
	index = "CORE~Warlock~Spell~4~Fel~Fiendish Circle"
	description = "Summon four 1/1 Imps"
	name_CN = "恶魔法阵"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.Game.summon([Imp(self.Game, self.ID) for i in range(4)], (-1, "totheRightEnd"), self)
		return None

	
class Hellfire(Spell):
	Class, school, name = "Warlock", "Fire", "Hellfire"
	requireTarget, mana = False, 4
	index = "CORE~Warlock~Spell~4~Fire~Hellfire"
	description = "Deal 3 damage to ALL characters"
	name_CN = "地狱烈焰"
	def text(self, CHN):
		damage = (3 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		return "对所有角色造成%d点伤害"%damage if CHN else "Deal %d damage to ALL characters"%damage
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		damage = (3 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		targets = [self.Game.heroes[1], self.Game.heroes[2]] + self.Game.minionsonBoard(1) + self.Game.minionsonBoard(2)
		self.dealsAOE(targets, [damage for obj in targets])
		return None
		
		
class LakkariFelhound(Minion):
	Class, race, name = "Warlock", "Demon", "Lakkari Felhound"
	mana, attack, health = 4, 3, 8
	index = "CORE~Warlock~Minion~4~3~8~Demon~Lakkari Felhound~Taunt~Battlecry"
	requireTarget, keyWord, description = False, "Taunt", "Taunt. Battlecry: Discard your two lowest-Cost cards"
	name_CN = "拉卡利地狱犬"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if curGame.mode == 0:
			if curGame.guides:
				i, j = curGame.guides.pop(0)
			else:
				inds = {}
				for i, card in enumerate(curGame.Hand_Deck.hands[self.ID]):
					if card.mana in inds: inds[card.mana].append(i)
					else: inds[card.mana] = [i]
				manas = sorted(list(inds.keys()))
				if not manas: #No card in hand
					i = j = -1
				elif len(inds[manas[0]]) > 1: #Two cards share the same lowest cost
					i, j = npchoice(inds[manas[0]], 2, replace=False)
				else: #Only one card with the lowest cost
					#If there is a 2nd card in hand with a higher cost, then pick as j, else pick -2 as j
					i, j  = npchoice(inds[manas[0]]), npchoice(inds[manas[1]]) if len(manas) > 1 else -1
				curGame.fixedGuides.append((i, j))
			if i > -1 and j > -1:
				curGame.Hand_Deck.discard(self.ID, (i, j))
			elif i > -1:
				curGame.Hand_Deck.discard(self.ID, i)
		return None
		
		

class FelsoulJailer(Minion):
	Class, race, name = "Warlock", "Demon", "Felsoul Jailer"
	mana, attack, health = 5, 4, 6
	index = "CORE~Shaman~Minion~5~4~6~Demon~Felsoul Jailer~Battlecry~Deathrattle"
	requireTarget, keyWord, description = False, "", "Battlecry: Your opponent discards a minion. Deathrattle: Return it"
	name_CN = "邪魂狱卒"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
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
				curGame.Hand_Deck.discard(3-self.ID, i)
				for trig in self.deathrattles:
					if isinstance(trig, ReturnDiscardedEnemyMinion):
						trig.discardedCard = type(minion)
		return None
		
class ReturnDiscardedEnemyMinion(Deathrattle_Minion):
	def __init__(self, entity):
		super().__init__(entity)
		self.discardedCard = None #Assume the original copy is lost
		
	def text(self, CHN):
		return "亡语：将%s返回对方手牌"%self.discardedCard.name if CHN \
				else "Deathrattle: Return the discarded card %s to opponent's hand"%self.discardedCard.name
				
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		if self.discardedCard:
			self.entity.Game.Hand_Deck.addCardtoHand(self.discardedCard, 3-self.entity.ID, byType=True)
			
	def selfCopy(self, recipient):
		trig = type(self)(recipient)
		trig.discardedCard = self.discardedCard
		return trig
		
		
class SiphonSoul(Spell):
	Class, school, name = "Warlock", "Shadow", "Siphon Soul"
	requireTarget, mana = True, 5
	index = "CORE~Warlock~Spell~5~Shadow~Siphon Soul"
	description = "Destroy a minion. Restore 3 Health to your hero"
	name_CN = "灵魂虹吸"
	def targetExists(self, choice=0):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
		
	def text(self, CHN):
		heal = 3 * (2 ** self.countHealDouble())
		return "消灭一个随从，为你的英雄恢复%d点生命值"%heal if CHN else "Destroy a minion. Restore %d health to your hero"%heal
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			heal = 3 * (2 ** self.countHealDouble())
			self.Game.killMinion(self, target)
			self.restoresHealth(self.Game.heroes[self.ID], heal)
		return target
		
		
class DreadInfernal(Minion):
	Class, race, name = "Warlock", "Demon", "Dread Infernal"
	mana, attack, health = 6, 6, 6
	index = "CORE~Warlock~Minion~6~6~6~Demon~Dread Infernal~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Deal 1 damage to ALL other characters"
	name_CN = "恐惧地狱火"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		targets = [self.Game.heroes[1], self.Game.heroes[2]] + self.Game.minionsonBoard(self.ID, self) + self.Game.minionsonBoard(3-self.ID)
		self.dealsAOE(targets, [1]*len(targets))
		return None
		
		
class EnslavedFelLord(Minion):
	Class, race, name = "Warlock", "Demon", "Enslaved Fel Lord"
	mana, attack, health = 7, 4, 10
	index = "CORE~Warlock~Minion~7~4~10~Demon~Enslaved Fel Lord~Taunt"
	requireTarget, keyWord, description = False, "Taunt", "Taunt. Also damages the minions next to whomever this attacks"
	name_CN = "被奴役的邪能领主"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.marks["Sweep"] = 1
		
		
class TwistingNether(Spell):
	Class, school, name = "Warlock", "Shadow", "Twisting Nether"
	requireTarget, mana = False, 8
	index = "CORE~Warlock~Spell~8~Shadow~Twisting Nether"
	description = "Destroy all minions"
	name_CN = "扭曲虚空"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.Game.killMinion(self, self.Game.minionsonBoard(1) + self.Game.minionsonBoard(2))
		return None
	
	
class INFERNO(HeroPower):
	mana, name, requireTarget = 2, "INFERNO!", False
	index = "Warlock~Hero Power~2~INFERNO!"
	description = "Summon a 6/6 Infernal"
	name_CN = "地狱火！"
	def available(self, choice=0):
		return not self.chancesUsedUp() and self.Game.space(self.ID) 
		
	def effect(self, target=None, choice=0):
		self.Game.summon(Infernal(self.Game, self.ID), -1, self.ID, "")
		return 0
		
class LordJaraxxus(Hero):
	mana, weapon, description = 9, None, "Battlecry: Equip a 3/8 Bloodfury"
	Class, name, heroPower, armor = "Warlock", "Lord Jaraxxus", INFERNO, 5
	index = "CORE~Warlock~Hero Card~9~Lord Jaraxxus~Battlecry~Legendary"
	name_CN = "加拉克苏斯大王"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.Game.equipWeapon(BloodFury(self.Game, self.ID))
		return None
		
		
"""Warrior Cards"""
class BloodsailDeckhand(Minion):
	Class, race, name = "Warrior", "Pirate", "Bloodsail Deckhand"
	mana, attack, health = 1, 2, 1
	index = "CORE~Warrior~Minion~1~2~1~Pirate~Bloodsail Deckhand~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: The next weapon you play costs (1) less"
	name_CN = "血帆桨手"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		tempAura = GameManaAura_NextWeapon1Less(self.Game, self.ID)
		self.Game.Manas.CardAuras.append(tempAura)
		tempAura.auraAppears()
		return None
		
class GameManaAura_NextWeapon1Less(TempManaEffect):
	def __init__(self, Game, ID, changeby=0, changeto=-1):
		super().__init__(Game, ID, -1, -1)
		self.temporary = False
	
	def applicable(self, target):
		return target.ID == self.ID and target.type == "Weapon"
	
	def text(self, CHN):
		return "你的下一张武器牌的法力值消耗减少(1)点" if CHN else "The next weapon you play costs (1) less"


class Whirlwind(Spell):
	Class, school, name = "Warrior", "", "Whirlwind"
	requireTarget, mana = False, 1
	index = "CORE~Warrior~Spell~1~~Whirlwind"
	description = "Deal 1 damage to ALL minions"
	name_CN = "旋风斩"
	
	def text(self, CHN):
		damage = (1 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		return "对所有随从造成%d点伤害" % damage if CHN else "Deal %d damage to ALL minions" % damage
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		damage = (1 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		targets = self.Game.minionsonBoard(1) + self.Game.minionsonBoard(2)
		self.dealsAOE(targets, [damage for minion in targets])
		return None


class CruelTaskmaster(Minion):
	Class, race, name = "Warrior", "", "Cruel Taskmaster"
	mana, attack, health = 2, 2, 2
	index = "CORE~Warrior~Minion~2~2~2~~Cruel Taskmaster~Battlecry"
	requireTarget, keyWord, description = True, "", "Battlecry: Deal 1 damage to a minion and give it +2 Attack"
	name_CN = "严酷的监工"
	
	def targetExists(self, choice=0):
		return self.selectableMinionExists()
	
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
	
	#Minion in deck can't get buff/reset.
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			self.dealsDamage(target, 1)
			target.buffDebuff(2, 0)
		return target


class Execute(Spell):
	Class, school, name = "Warrior", "", "Execute"
	requireTarget, mana = True, 2
	index = "CORE~Warrior~Spell~2~~Execute"
	description = "Destroy a damaged enemy minion"
	name_CN = "斩杀"
	
	def available(self):
		return self.selectableEnemyMinionExists()
	
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.ID != self.ID and target.health < target.health_max and target.onBoard
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			self.Game.killMinion(self, target)
		return target


class FieryWarAxe_Core(Weapon):
	Class, name, description = "Warrior", "Fiery War Axe", ""
	mana, attack, durability = 3, 3, 2
	index = "CORE~Warrior~Weapon~3~3~2~Fiery War Axe"
	name_CN = "炽炎战斧"


#Charge gained by enchantment and aura can also be buffed by this Aura.
class WarsongCommander(Minion):
	Class, race, name = "Warrior", "", "Warsong Commander"
	mana, attack, health = 3, 2, 3
	index = "CORE~Warrior~Minion~3~2~3~~Warsong Commander"
	requireTarget, keyWord, description = False, "", "After you summon another minion, give it Rush"
	name_CN = "战歌指挥官"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_WarsongCommander(self)]


class Trig_WarsongCommander(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["MinionSummoned"])
	
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject.ID == self.entity.ID and subject != self.entity
	
	def text(self, CHN):
		return "在你召唤另一个随从后，使其获得突袭" if CHN else "After you summon another minion, give it Rush"
	
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		subject.getsStatus("Rush")


class Armorsmith(Minion):
	Class, race, name = "Warrior", "", "Armorsmith"
	mana, attack, health = 2, 1, 4
	index = "CORE~Warrior~Minion~2~1~4~~Armorsmith"
	requireTarget, keyWord, description = False, "", "Whenever a friendly minion takes damage, gain +1 Armor"
	name_CN = "铸甲师"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_Armorsmith(self)]

class Trig_Armorsmith(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["MinionTakesDmg"])
	
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and target.ID == self.entity.ID
	
	def text(self, CHN):
		return "每当一个友方随从受到伤害，便获得1点护甲值" if CHN else "Whenever a friendly minion takes damage, gain +1 Armor"
	
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.Game.heroes[self.entity.ID].gainsArmor(1)


class FrothingBerserker(Minion):
	Class, race, name = "Warrior", "", "Frothing Berserker"
	mana, attack, health = 3, 2, 4
	index = "CORE~Warrior~Minion~3~2~4~~Frothing Berserker"
	requireTarget, keyWord, description = False, "", "Whenever a minion takes damage, gain +1 Attack"
	name_CN = "暴乱狂战士"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_FrothingBerserker(self)]

class Trig_FrothingBerserker(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["MinionTakesDmg"])
	
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard
	
	def text(self, CHN):
		return "每当一个随从受到伤害，便获得+1攻击力" if CHN else "Whenever a minion takes damage, gain +1 Attack"
	
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.buffDebuff(1, 0)


class WarCache(Spell):
	Class, school, name = "Warrior", "", "War Cache"
	requireTarget, mana = False, 3
	index = "CORE~Warrior~Spell~3~~War Cache"
	description = "Add a random Hunter Minion, Spell, and Weapon to your hand"
	name_CN = "战争储备箱"
	poolIdentifier = "Warrior Minions"
	@classmethod
	def generatePool(cls, pools):
		minions, spells, weapons = [], [], []
		for key, value in pools.ClassCards["Warrior"].items():
			if "~Minion~" in key:
				minions.append(value)
			elif "~Spell~" in key:
				spells.append(value)
			elif "~Weapon~" in key:
				weapons.append(value)
		return ["Warrior Minions", "Warrior Spells", "Warrior Weapons"], [minions, spells, weapons]
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if curGame.mode == 0:
			for identifier in ("Warrior Minions", "Warrior Spells", "Warrior Weapons"):
				pool = tuple(self.rngPool(identifier))
				if curGame.guides:
					card = list(curGame.guides.pop(0))
				else:
					card = npchoice(self.rngPool(identifier))
					curGame.fixedGuides.append(card)
				curGame.Hand_Deck.addCardtoHand(card, self.ID, byType=True, creator=type(self), possi=pool)
		return None
		
		
class WarsongOutrider(Minion):
	Class, race, name = "Warrior", "", "Warsong Outrider"
	mana, attack, health = 4, 5, 4
	index = "CORE~Warrior~Minion~4~5~4~~Warsong Outrider"
	requireTarget, keyWord, description = False, "", ""
	name_CN = "战歌侦察骑兵"


class Brawl(Spell):
	Class, school, name = "Warrior", "", "Brawl"
	requireTarget, mana = False, 5
	index = "CORE~Warrior~Spell~5~Brawl"
	description = "Destroy all minions except one. (Chosen randomly)"
	name_CN = "绝命乱斗"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if curGame.mode == 0:
			if curGame.guides:
				i, where = curGame.guides.pop(0)
				if where:
					survivor = curGame.find(i, where)
					curGame.killMinion(self, [minion for minion in curGame.minionsonBoard(1) + curGame.minionsonBoard(2) if minion != survivor])
			else:
				minions = curGame.minionsonBoard(1) + curGame.minionsonBoard(2)
				if len(minions) > 1:
					survivor = npchoice(minions)
					curGame.fixedGuides.append((survivor.pos, "Minion%d"%survivor.ID))
					curGame.killMinion(self, [minion for minion in minions if minion != survivor])
				else:
					curGame.fixedGuides.append((0, ""))
		return None
		
		
class Shieldmaiden(Minion):
	Class, race, name = "Warrior", "", "Shieldmaiden"
	mana, attack, health = 6, 5, 5
	index = "CORE~Warrior~Minion~6~5~5~~Shieldmaiden~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Gain 5 Armor"
	name_CN = "盾甲侍女"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.Game.heroes[self.ID].gainsArmor(5)
		return None
		
		
class Gorehowl(Weapon):
	Class, name, description = "Warrior", "Gorehowl", "Attacking a minion costs 1 Attack instead of 1 Durability"
	mana, attack, durability = 7, 7, 1
	index = "CORE~Warrior~Weapon~7~7~1~Gorehowl"
	name_CN = "血吼"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_Gorehowl(self)]
		self.canLoseDurability = True
		
	def loseDurability(self):
		if self.canLoseDurability:
			self.durability -= 1
		else:
			self.attack -= 1
			self.Game.heroes[self.ID].attack = self.Game.heroes[self.ID].attack_bare + max(0, self.attack)
			self.canLoseDurability = True #把武器的可以失去耐久度恢复为True
			if self.attack < 1:
				self.dead = True
				
class Trig_Gorehowl(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["HeroAttackingMinion"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject == self.entity.Game.heroes[self.entity.ID] and target.type == "Minion" and self.entity.onBoard
		
	def text(self, CHN):
		return "攻击随从不会消耗耐久度，改为降低1点攻击力" if CHN else "Attacking a minion costs 1 Attack instead of 1 Durability"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.canLoseDurability = False
		
		
class GrommashHellscream(Minion):
	Class, race, name = "Warrior", "", "Grommash Hellscream"
	mana, attack, health = 8, 4, 9
	index = "CORE~Warrior~Minion~8~4~9~~Grommash Hellscream~Charge~Legendary"
	requireTarget, keyWord, description = False, "Charge", "Charge. Has +6 attack while damaged"
	name_CN = "格罗玛什·地狱咆哮"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.auras["Has +6 attack while damaged"] = StatAura_Enrage(self, 6)
		
		
		
Core_Cards = [#Mana 1 cards
					MurlocTinyfin, AbusiveSergeant, ArcaneAnomaly, ArgentSquire, Cogmaster, ElvenArcher, MurlocTidecaller, EmeraldSkytalon, VoodooDoctor, WorgenInfiltrator, YoungPriestess,
					#Mana 2 cards
					AcidicSwampOoze, AnnoyoTron, BloodmageThalnos, BloodsailRaider, RedgillRazorjaw, CrazedAlchemist, DireWolfAlpha, ExplosiveSheep, FogsailFreebooter, NerubianEgg, RiverCrocolisk, SunreaverSpy, Toxicologist, YouthfulBrewmaster,
					#Mana 3 cards
					Brightwing, ColdlightSeer, EarthenRingFarseer, FlesheatingGhoul, HumongousRazorleaf, IceRager, InjuredBlademaster, IronbeakOwl, JunglePanther, KingMukla, LoneChampion, MiniMage, RaidLeader, SouthseaCaptain, SpiderTank, StoneskinBasilisk, 
					#Mana 4 cards
					BaronRivendare, BigGameHunter, ChillwindYeti, DarkIronDwarf, DefenderofArgus, GrimNecromancer, SenjinShieldmasta, VioletTeacher, 
					#Mana 5 cards
					FacelessManipulator, GurubashiBerserker, OverlordRunthak, StranglethornTiger, TaelanFordring, CairneBloodhoof, HighInquisitorWhitemane, BaronGeddon, BarrensStablehand, NozdormutheEternal, Stormwatcher, StormwindChampion, ArcaneDevourer, 
					#Mana 6~8 cards
					MalygostheSpellweaver, OnyxiatheBroodmother, SleepyDragon, YseratheDreamer, DeathwingtheDestroyer, ClockworkGiant, 
					#Demon hunter cards
					Battlefiend, ChaosStrike, CrimsonSigilRunner, FeastofSouls, KorvasBloodthorn, SightlessWatcher, SpectralSight, AldrachiWarblades, CoordinatedStrike, EyeBeam, GanargGlaivesmith, AshtongueBattlelord, RagingFelscreamer, ChaosNova, WarglaivesofAzzinoth, IllidariInquisitor, 
					#Druid cards
					Innervate, Pounce, EnchantedRaven, MarkoftheWild, PoweroftheWild, FeralRage, Landscaping, WildGrowth, NordrassilDruid, SouloftheForest, DruidoftheClaw, ForceofNature, MenagerieWarden, Nourish, AncientofWar, Cenarius, 
					#Hunter cardds
					ArcaneShot, Tracking, Webspinner, ExplosiveTrap, FreezingTrap, HeadhuntersHatchet, QuickShot, ScavengingHyena, SelectiveBreeder, SnakeTrap, Bearshark, DeadlyShot, DireFrenzy, SavannahHighmane, KingKrush, 
					#Mage cards
					BabblingBook, ShootingStar, SnapFreeze, Arcanologist, FallenHero, ArcaneIntellect, ConeofCold, Counterspell, IceBarrier, MirrorEntity, Fireball, WaterElemental_Core, AegwynntheGuardian, EtherealConjurer, ColdarraDrake, Flamestrike, 
					#Paladin cards
					Avenge, NobleSacrifice, Reckoning, RighteousProtector, ArgentProtector, HolyLight, PursuitofJustice, AldorPeacekeeper, Equality, WarhorseTrainer, BlessingofKings, Consecration, TruesilverChampion, StandAgainstDarkness, GuardianofKings, TirionFordring, 
					#Priest cards
					CrimsonClergy, FlashHeal, FocusedWill, HolySmite, PsychicConjurer, ShadowWordDeath, ThriveintheShadows, Lightspawn, Shadowform, ShadowedSpirit, HolyNova, PowerInfusion, ShadowWordRuin, TempleEnforcer, NatalieSeline,
					#Rogue cards
					Backstab, Preparation, Shadowstep, BladedCultist, DeadlyPoison, SinisterStrike, Swashburglar, ColdBlood, PatientAssassin, VanessaVanCleef, PlagueScientist, SI7Agent, Assassinate, AssassinsBlade, TombPillager, Sprint, 
					#Shaman cards
					LightningBolt, MenacingNimbus, NoviceZapper, RockbiterWeapon, Windfury, FeralSpirit, LightningStorm, ManaTideTotem, UnboundElemental, DraeneiTotemcarver, Hex, TidalSurge, Doomhammer, EarthElemental, FireElemental, AlAkirtheWindlord, 
					#Warlock cards
					RitualofDoom, DemonicTyrant, FlameImp, MortalCoil, PossessedVillager, DrainSoul, TinyKnightofEvil, VoidTerror, FiendishCircle, Hellfire, LakkariFelhound, FelsoulJailer, SiphonSoul, DreadInfernal, EnslavedFelLord, TwistingNether, LordJaraxxus,
					#Warrior cards
					BloodsailDeckhand, Whirlwind, CruelTaskmaster, Execute, FieryWarAxe_Core, WarsongCommander, Armorsmith, FrothingBerserker, WarCache, WarsongOutrider, Brawl, Shieldmaiden, Gorehowl, GrommashHellscream,
					]
