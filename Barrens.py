from CardTypes import *
from Triggers_Auras import *

from AcrossPacks import Frog, SilverHandRecruit, WaterElemental_Basic, DreamCards, Adventurers
import inspect

"""Forged in the Barrens"""
#假设是随从受伤时触发，不是受伤之后触发
class Frenzy(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["MinionTakesDmg"])
		self.oneTime = True
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and target == self.entity and target.health > 0 and not target.dead
		
	def trig(self, signal, ID, subject, target, number, comment, choice=0):
		if self.canTrig(signal, ID, subject, target, number, comment):
			btn, GUI = self.entity.btn, self.entity.Game.GUI
			if btn and "SpecTrig" in btn.icons:
				icon = btn.icons["SpecTrig"]
				GUI.seqHolder[-1].append(GUI.PARALLEL(GUI.FUNC(icon.trigAni_1stHalf), GUI.WAIT(0.5)))
				GUI.seqHolder[-1].append(GUI.FUNC(icon.np.setColor, 1, 1, 1, 0)) #
				GUI.seqHolder[-1].append(GUI.PARALLEL(GUI.FUNC(icon.trigAni_2ndHalf), GUI.WAIT(0.5)))
			self.entity.losesTrig(self)
			self.effect(signal, ID, subject, target, number, comment)
			
			
#So far the cards that upgrade when Mana Crystals are enough are all spells
class Trig_ForgeUpgrade(TrigHand):
	def __init__(self, entity, newCard, threshold):
		super().__init__(entity, ["ManaXtlsCheck"])
		self.threshold = threshold
		self.newCard = newCard
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.inHand and ID == self.entity.ID and self.entity.Game.Manas.manasUpper[self.entity.ID] >= self.threshold
		
	def text(self, CHN):
		return "如果玩家的法力水晶为%d，便升级"%self.threshold if CHN else "When player's Mana Crystals is %d, upgrades"%self.threshold
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		card = self.entity
		newCard = self.newCard(card.Game, card.ID)
		for key, value in newCard.keyWords.items(): #Find keywords the new card doesn't have
			if value < 1 and card.keyWords[key] > 0: newCard.keyWords[key] = 1
		for key, value in newCard.marks.items():
			try:
				if value < 1 and card.marks[key] > 0: newCard.marks[key] = 1
			except: pass
		#Inhand triggers and mana modifications
		newCard.trigsHand += [trig for trig in card.trigsHand if not isinstance(trig, Trig_Corrupt)]
		newCard.manaMods = [manaMod.selfCopy(newCard) for manaMod in card.manaMods]
		card.Game.Hand_Deck.replaceCardinHand(card, newCard)
		
		
"""Mana 1 Cards"""
class KindlingElemental(Minion):
	Class, race, name = "Neutral", "Elemental", "Kindling Elemental"
	mana, attack, health = 1, 1, 2
	index = "THE_BARRENS~Neutral~Minion~1~1~2~Elemental~Kindling Elemental~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Your next Elemental costs (1) less"
	name_CN = "火光元素"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		tempAura = GameManaAura_NextElemental1Less(self.Game, self.ID)
		self.Game.Manas.CardAuras.append(tempAura)
		tempAura.auraAppears()
		return None

class GameManaAura_NextElemental1Less(TempManaEffect):
	def __init__(self, Game, ID, changeby=0, changeto=-1):
		super().__init__(Game, ID, -1, -1)
		self.temporary = False
	
	def applicable(self, target):
		return target.ID == self.ID and target.type == "Minion" and "Elemental" in target.race
	
	def text(self, CHN):
		return "你的下一张元素牌的法力值消耗减少(1)点" if CHN else "Your next Spelldamage minion costs (1) less"


"""Mana 2 Cards"""
class FarWatchPost(Minion):
	Class, race, name = "Neutral", "", "Far Watch Post"
	mana, attack, health = 2, 2, 3
	index = "THE_BARRENS~Neutral~Minion~2~2~3~~Far Watch Post"
	requireTarget, keyWord, description = False, "", "Can't attack. After your opponent draws a card, it costs (1) more (up to 10)"
	name_CN = "前沿哨所"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.marks["Can't Attack"] = 1
		self.trigsBoard = [Trig_FarWatchPost(self)]

class Trig_FarWatchPost(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["CardEntersHand"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject.ID != self.entity.ID
	
	def text(self, CHN):
		return "在你的对手抽一张牌后，使其法力值消耗增加(1)点（最高不超过10点）" if CHN else "After your opponent draws a card, it costs (1) more (up to 10)"
	
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		if target[0].mana < 10:
			ManaMod(target[0], changeby=+1, changeto=-1).applies()
			
			
class HecklefangHyena(Minion):
	Class, race, name = "Neutral", "Beast", "Hecklefang Hyena"
	mana, attack, health = 2, 2, 4
	index = "THE_BARRENS~Neutral~Minion~2~2~4~Beast~Hecklefang Hyena~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Deal 3 damage to your hero"
	name_CN = "乱齿土狼"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.dealsDamage(self.Game.heroes[self.ID], 3)
		return None


class LushwaterMurcenary(Minion):
	Class, race, name = "Neutral", "Murloc", "Lushwater Murcenary"
	mana, attack, health = 2, 3, 2
	index = "THE_BARRENS~Neutral~Minion~2~3~2~Murloc~Lushwater Murcenary~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: If you control a Murloc, gain +1/+1"
	name_CN = "甜水鱼人斥侯"
	
	def effCanTrig(self):
		self.effectViable = any("Murloc" in minion.race for minion in self.Game.minionsonBoard(self.ID))

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if any("Murloc" in minion.race and minion != self for minion in self.Game.minionsonBoard(self.ID)):
			self.buffDebuff(1, 1)
		return None
	
	
class LushwaterScout(Minion):
	Class, race, name = "Neutral", "Murloc", "Lushwater Scout"
	mana, attack, health = 2, 1, 3
	index = "THE_BARRENS~Neutral~Minion~2~1~3~Murloc~Lushwater Scout"
	requireTarget, keyWord, description = False, "", "After you summon a Murloc, give it +1 Attack and Rush"
	name_CN = "甜水鱼人斥侯"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_LushwaterScout(self)]

class Trig_LushwaterScout(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["MinionSummoned"])
	
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject.ID == self.entity.ID and subject != self.entity and "Murloc" in subject.race
	
	def text(self, CHN):
		return "在你召唤一个鱼人后，使其获得+1攻击力和突袭" if CHN else "After you summon a Murloc, give it +1 Attack and Rush"
	
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		subject.buffDebuff(1, 0)
		subject.getsStatus("Rush")


class OasisThrasher(Minion):
	Class, race, name = "Neutral", "Beast", "Oasis Thrasher"
	mana, attack, health = 2, 2, 3
	index = "THE_BARRENS~Neutral~Minion~2~2~3~Beast~Oasis Thrasher~Frenzy"
	requireTarget, keyWord, description = False, "", "Frenzy: Deal 3 damage to the enemy hero"
	name_CN = "绿洲长尾鳄"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_OasisThrasher(self)]

class Trig_OasisThrasher(Frenzy):
	def text(self, CHN):
		return "暴怒：对敌方英雄造成3点伤害" if CHN else "Frenzy: Deal 3 damage to the enemy hero"
	
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.dealsDamage(self.entity.heroes[3-self.entity.ID], 3)
		

class Peon(Minion):
	Class, race, name = "Neutral", "", "Peon"
	mana, attack, health = 2, 2, 3
	index = "THE_BARRENS~Neutral~Minion~2~2~3~~Peon~Frenzy"
	requireTarget, keyWord, description = False, "", "Frenzy: Add a random spell from your class to your hand"
	name_CN = "苦工"
	poolIdentifier = "Druid Spells"
	@classmethod
	def generatePool(cls, pools):
		return [Class + " Spells" for Class in pools.Classes], \
			   [[card for card in cards if card.type == "Spell"] for cards in pools.ClassCards.values()]
	
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_Peon(self)]
		
class Trig_Peon(Frenzy):
	def text(self, CHN):
		return "暴怒：随机将一张你的职业的法术牌置入你的手牌" if CHN else "Frenzy: Add a random spell from your class to your hand"
				
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.addCardtoHand(npchoice(self.rngPool(self.entity.Game.heroes[self.entity.ID].Class + " Spells")), self.entity.ID)
			
			
class TalentedArcanist(Minion):
	Class, race, name = "Neutral", "", "Talented Arcanist"
	mana, attack, health = 2, 1, 3
	index = "THE_BARRENS~Neutral~Minion~2~1~3~~Talented Arcanist~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Your next spell this turn has Spell Damage +2"
	name_CN = "精明的奥术师"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.Game.status[self.ID]["Spell Damage"] += 2
		TalentedArcanist_Effect(self.Game, self.ID, self).connect()
		return None

class TalentedArcanist_Effect:
	def __init__(self, Game, ID, card):
		self.Game, self.ID = Game, ID
		self.card = TalentedArcanist(Game, ID)
		self.boost = 2
		
	def connect(self):
		try: trigs = self.Game.trigsBoard[self.ID]["SpellBeenCast"]
		except: trigs = self.Game.trigsBoard[self.ID]["SpellBeenCast"] = []
		trig = next((trig for trig in trigs if isinstance(trig, TalentedArcanist_Effect)), None)
		if trig:
			trig.boost += 2
			if trig.card.btn: trig.card.btn.trigAni(trig.boost)
		else:
			trigs.append(self)
			if self.Game.GUI: self.Game.GUI.heroZones[self.ID].addaTrig(self.card, text='2')
		
	def disconnect(self):
		try: self.Game.trigsBoard[self.ID]["SpellBeenCast"].remove(self)
		except: pass
		try: self.Game.turnEndTrigger.remove(self)
		except: pass
		if self.Game.GUI: self.Game.GUI.heroZones[self.ID].removeaTrig(self.card)
	
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject.ID == self.ID
	
	def trig(self, signal, ID, subject, target, number, comment, choice=0):
		if self.canTrig(signal, ID, subject, target, number, comment):
			if self.Game.GUI: self.Game.GUI.showOffBoardTrig(self.card)
			self.effect(signal, ID, subject, target, number, comment)
	
	def text(self, CHN):
		return "在本回合结束，或你使用一张法术后，你的法术不再获得法术伤害+2" if CHN \
			else "After then turn ends or you play a spell, your spells will no longer has Spell Damage +2"
	
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.Game.status[self.ID]["Spell Damage"] -= 1
		self.disconnect()
	
	def turnEndTrigger(self):
		self.Game.status[self.ID]["Spell Damage"] -= 1
		self.disconnect()
	
	def createCopy(self, game):  #不是纯的只在回合结束时触发，需要完整的createCopy
		if self not in game.copiedObjs:  #这个扳机没有被复制过
			trigCopy = type(self)(game, self.ID, None)
			game.copiedObjs[self] = trigCopy
			return trigCopy
		else:  #一个扳机被复制过了，则其携带者也被复制过了
			return game.copiedObjs[self]


class ToadoftheWilds(Minion):
	Class, race, name = "Neutral", "Beast", "Toad of the Wilds"
	mana, attack, health = 2, 2, 2
	index = "THE_BARRENS~Neutral~Minion~2~2~2~Beast~Toad of the Wilds~Taunt~Battlecry"
	requireTarget, keyWord, description = False, "Taunt", "Taunt. Battlecry: If you're holding a Nature spell, gain +2 Health"
	name_CN = "狂野蟾蜍"
	
	def effCanTrig(self):
		self.effectViable = any(card.type == "Spell" and card.school == "Nature" for card in self.Game.Hand_Deck.hands[self.ID])
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if any(card.type == "Spell" and card.school == "Nature" for card in self.Game.Hand_Deck.hands[self.ID]):
			self.buffDebuff(0, 2)
		return None


"""Mana 3 Cards"""
class BarrensTrapper(Minion):
	Class, race, name = "Neutral", "", "Barrens Trapper"
	mana, attack, health = 3, 2, 4
	index = "THE_BARRENS~Neutral~Minion~3~2~4~~Barrens Trapper"
	requireTarget, keyWord, description = False, "", "Your Deathrattle cards cost (1) less"
	name_CN = "贫瘠之地诱捕者"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.auras["Your Deathrattle cards cost (1) less"] = ManaAura(self, changeby=-1, changeto=-1)
	
	def manaAuraApplicable(self, subject):  #ID用于判定是否是我方手中的随从
		return subject.ID == self.ID and hasattr(subject, "deathrattles") and subject.deathrattles


class CrossroadsGossiper(Minion):
	Class, race, name = "Neutral", "", "Crossroads Gossiper"
	mana, attack, health = 3, 4, 3
	index = "THE_BARRENS~Neutral~Minion~3~4~3~~Crossroads Gossiper~Battlecry"
	requireTarget, keyWord, description = False, "", "After a friendly Secret is revealed, gain +2/+2"
	name_CN = "十字路口大嘴巴"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_CrossroadsGossiper(self)]

class Trig_CrossroadsGossiper(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["SecretRevealed"])
	
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject.ID == self.entity.ID and self.entity.onBoard
	
	def text(self, CHN):
		return "每当一个友方奥秘被提示时，便获得+2/+2" if CHN else "After a friendly Secret is revealed, gain +2/+2"
	
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.buffDebuff(2, 2)


class DeathsHeadCultist(Minion):
	Class, race, name = "Neutral", "Quilboar", "Death's Head Cultist"
	mana, attack, health = 3, 2, 4
	index = "THE_BARRENS~Neutral~Minion~3~2~4~Quilboar~Death's Head Cultist~Taunt~Deathrattle"
	requireTarget, keyWord, description = False, "Taunt", "Deathrattle: Restore 4 Health to your hero"
	name_CN = "亡首教徒"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.deathrattles = [Restore5HealthtoYourHero(self)]

class Restore5HealthtoYourHero(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		heal = 8 * (2 ** self.entity.countHealDouble())
		self.entity.restoresHealth(self.entity.heroes[self.entity.ID], heal)
		
	def text(self, CHN):
		heal = 8 * (2 ** self.entity.countHealDouble())
		return "亡语：为你的英雄恢复%d点生命值"% heal if CHN else "Deathrattle: Restore %d Health to your hero" % heal
	

class HogRancher(Minion):
	Class, race, name = "Neutral", "", "Hog Rancher"
	mana, attack, health = 3, 3, 2
	index = "THE_BARRENS~Neutral~Minion~3~3~2~~Hog Rancher~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Summon a 2/1 Hog with Rush"
	name_CN = "放猪牧人"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.summon(Hog(self.Game, self.ID), self.pos+1)
		return None

class Hog(Minion):
	Class, race, name = "Neutral", "Beast", "Hog"
	mana, attack, health = 1, 2, 1
	index = "THE_BARRENS~Neutral~Minion~1~2~1~Beast~Hog~Rush~Uncollectible"
	requireTarget, keyWord, description = False, "Rush", "Rush"
	name_CN = "小猪"


class HordeOperative(Minion):
	Class, race, name = "Neutral", "", "Horde Operative"
	mana, attack, health = 3, 3, 4
	index = "THE_BARRENS~Neutral~Minion~3~3~4~~Horde Operative~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Copy your opponent's secrets and put them into play"
	name_CN = "部落特工"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		#假设先复制最早入场的奥秘
		secretHD = self.Game.Secrets
		for secret in secretHD.secrets[3-self.ID]:
			if secretHD.areaNotFull(self.ID):
				if not secretHD.sameSecretExists(secret, self.ID):
					secret.selfCopy(self.ID, self).whenEffective()
			else: break
		return None


class Mankrik(Minion):
	Class, race, name = "Neutral", "", "Mankrik"
	mana, attack, health = 3, 3, 4
	index = "THE_BARRENS~Neutral~Minion~3~3~4~~Mankrik~Battlecry~Legendary"
	requireTarget, keyWord, description = False, "", "Battlecry: Help Mankrik find his wife! She was last seen somewhere in your deck"
	name_CN = "曼克里克"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.Game.Hand_Deck.shuffleintoDeck(OlgraMankriksWife(self.Game, self.ID), creator=self)
		return None
		
class OlgraMankriksWife(Spell):
	Class, school, name = "Neutral", "", "Olgra, Mankrik's Wife"
	requireTarget, mana = False, 3
	index = "THE_BARRENS~Neutral~Spell~3~~Olgra, Mankrik's Wife~Uncollectible~Casts When Drawn"
	description = "Casts When Drawn. Summon a 3/10 Mankrik, who immediately attaks the enemy hero"
	name_CN = "奥格拉，曼克里克的妻子"
	def available(self):
		return self.Game.space(self.ID) > 0
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		minion = MankrikConsumedbyHatred(self.Game, self.ID)
		self.summon(minion, -1)
		if minion.onBoard and minion.health > 0 and not minion.dead:
			self.Game.battle(minion, self.Game.heroes[3-self.ID], verifySelectable=False, useAttChance=False)
		return None

class MankrikConsumedbyHatred(Minion):
	Class, race, name = "Neutral", "", "Mankrik, Consumed by Hatred"
	mana, attack, health = 5, 3, 7
	index = "THE_BARRENS~Neutral~Minion~5~3~7~~Mankrik, Consumed by Hatred~Legendary~Uncollectible"
	requireTarget, keyWord, description = False, "", ""
	name_CN = "曼克里克"
	

class MorshanWatchPost(Minion):
	Class, race, name = "Neutral", "", "Mor'shan Watch Post"
	mana, attack, health = 3, 3, 4
	index = "THE_BARRENS~Neutral~Minion~3~3~4~~Mor'shan Watch Post"
	requireTarget, keyWord, description = False, "", "Can't attack. After your opponent plays a minion, summon a 2/2 Grunt"
	name_CN = "莫尔杉哨所"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.marks["Can't Attack"] = 1
		self.trigsBoard = [Trig_MorshanWatchPost(self)]

class Trig_MorshanWatchPost(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["MinionBeenPlayed"])
	
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject.ID != self.entity.ID
	
	def text(self, CHN):
		return "在你的对手使用一张随从牌后，召唤一个2/2的步兵" if CHN else "After your opponent plays a minion, summon a 2/2 Grunt"
	
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.summon(WatchfulGrunt(self.entity.Game, self.entity.ID), self.entity.pos)

class WatchfulGrunt(Minion):
	Class, race, name = "Neutral", "", "Watchful Grunt"
	mana, attack, health = 2, 2, 2
	index = "THE_BARRENS~Neutral~Minion~2~2~2~~Watchful Grunt~Uncollectible"
	requireTarget, keyWord, description = False, "", ""
	name_CN = "警觉的步兵"


class RatchetPrivateer(Minion):
	Class, race, name = "Neutral", "Pirate", "Ratchet Privateer"
	mana, attack, health = 3, 4, 3
	index = "THE_BARRENS~Neutral~Minion~3~4~3~Pirate~Ratchet Privateer~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Give your weapon +1 Attack"
	name_CN = "棘齿城私掠者"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		weapon = self.Game.availableWeapon(self.ID)
		if weapon: weapon.gainStat(1, 0)
		return None


class SunwellInitiate(Minion):
	Class, race, name = "Neutral", "", "Sunwell Initiate"
	mana, attack, health = 3, 3, 4
	index = "THE_BARRENS~Neutral~Minion~3~3~4~~Sunwell Initiate~Frenzy"
	requireTarget, keyWord, description = False, "", "Frenzy: Gain Divine Shield"
	name_CN = "太阳之井新兵"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_SunwellInitiate(self)]

class Trig_SunwellInitiate(Frenzy):
	def text(self, CHN):
		return "暴怒：获得圣盾" if CHN else "Frenzy: Gain Divine Shield"
	
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.getsStatus("Divine Shield")


class VenomousScorpid(Minion):
	Class, race, name = "Neutral", "Beast", "Venomous Scorpid"
	mana, attack, health = 3, 1, 3
	index = "THE_BARRENS~Neutral~Minion~3~1~3~Beast~Venomous Scorpid~Poisonous~Battlecry"
	requireTarget, keyWord, description = False, "Poisonous", "Poisonous. Battlecry: Discover a spell"
	name_CN = "剧毒魔蝎"
	poolIdentifier = "Druid Spells"
	@classmethod
	def generatePool(cls, pools):
		return [Class + " Spells" for Class in pools.Classes], \
			   [[card for card in cards if card.type == "Spell"] for cards in pools.ClassCards.values()]
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.discoverandGenerate(VenomousScorpid, comment, lambda : self.rngPool(classforDiscover(self) + " Spells"))
		return None


"""Mana 4 Cards"""
class BlademasterSamuro(Minion):
	Class, race, name = "Neutral", "", "Blademaster Samuro"
	mana, attack, health = 4, 1, 6
	index = "THE_BARRENS~Neutral~Minion~4~1~6~~Blademaster Samuro~Rush~Frenzy~Legendary"
	requireTarget, keyWord, description = False, "Rush", "Rush. Frenzy: Deal damage equal to this minion's Attack equal to all enemy minions"
	name_CN = "剑圣萨穆罗"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_BlademasterSamuro(self)]
		
class Trig_BlademasterSamuro(Frenzy):
	def text(self, CHN):
		return "暴怒：对所有敌方随从造成等同于该随从的攻击力的伤害" if CHN \
				else "Frenzy: Deal damage equal to this minion's Attack equal to all enemy minions"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		minion = self.entity
		targets = minion.Game.minionsonBoard(3-minion.ID)
		minion.dealsAOE(targets, [minion.attack]*len(targets))
		
		
class CrossroadsWatchPost(Minion):
	Class, race, name = "Neutral", "", "Crossroads Watch Post"
	mana, attack, health = 4, 4, 6
	index = "THE_BARRENS~Neutral~Minion~4~4~6~~Crossroads Watch Post"
	requireTarget, keyWord, description = False, "", "Can't attack. Whenever you opponent casts a spell, give your minions +1/+1"
	name_CN = "十字路口哨所"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.marks["Can't Attack"] = 1
		self.trigsBoard = [Trig_CrossroadsWatchPost(self)]

class Trig_CrossroadsWatchPost(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["SpellPlayed"])
	
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject.ID != self.entity.ID
	
	def text(self, CHN):
		return "每当你的对手施放一个法术，使你的所有随从获得+1/+1" if CHN else "Whenever you opponent casts a spell, give your minions +1/+1"
	
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		for minion in self.entity.Game.minionsonBoard(self.entity.ID):
			minion.buffDebuff(1, 1)
		
		
class DarkspearBerserker(Minion):
	Class, race, name = "Neutral", "", "Darkspear Berserker"
	mana, attack, health = 4, 5, 7
	index = "THE_BARRENS~Neutral~Minion~4~5~7~~Darkspear Berserker~Deathrattle"
	requireTarget, keyWord, description = False, "", "Deathrattle: Deal 5 damage to your hero"
	name_CN = "暗矛狂战士"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.deathrattles = [Deal5DamagetoYourHero(self)]

class Deal5DamagetoYourHero(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.dealsDamage(self.entity.Game.heroes[self.entity.ID], 5)
		
	def text(self, CHN):
		return "亡语：对你的英雄造成5点伤害" if CHN else "Deathrattle: Deal 5 damage to your hero"


class GruntledPatron(Minion):
	Class, race, name = "Neutral", "", "Gruntled Patron"
	mana, attack, health = 4, 3, 3
	index = "THE_BARRENS~Neutral~Minion~4~3~3~~Gruntled Patron~Frenzy"
	requireTarget, keyWord, description = False, "", "Frenzy: Summon another Gruntled Patron"
	name_CN = "满意的奴隶主"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_GruntledPatron(self)]
	
class Trig_GruntledPatron(Frenzy):
	def text(self, CHN):
		return "暴怒：召唤另一个满意的奴隶主" if CHN else "Frenzy: Summon another Gruntled Patron"
	
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.summon(GruntledPatron(self.entity.Game, self.entity.ID), self.entity.pos+1)


class InjuredMarauder(Minion):
	Class, race, name = "Neutral", "", "Injured Marauder"
	mana, attack, health = 4, 5, 10
	index = "THE_BARRENS~Neutral~Minion~4~5~10~~Injured Marauder~Taunt~Battlecry"
	requireTarget, keyWord, description = False, "Taunt", "Taunt. Battlecry: Deal 6 damage to this minion"
	name_CN = "受伤的掠夺者"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.dealsDamage(self, 6)
		return None


class KazakusGolemShaper(Minion):
	Class, race, name = "Neutral", "", "Kazakus, Golem Shaper"
	mana, attack, health = 4, 3, 3
	index = "THE_BARRENS~Neutral~Minion~4~3~3~~Kazakus, Golem Shaper~Battlecry~Legendary"
	requireTarget, keyWord, description = False, "", "Battlecry: If your deck has no 4-Cost cards, build a custom Golem"
	name_CN = "魔像师卡扎库斯"
	
	def effCanTrig(self):
		self.effectViable = all(card.mana != 4 for card in self.Game.Hand_Deck.decks[self.ID])
		
	def createGolem(self, mana, keyWord, golem):
		name = golem.name
		words = golem.index.split('~')
		for i, word in enumerate(words):
			if word == name: words.insert(i+2, keyWord)
		newIndex = '~'.join(words)
		#Example: "SuperiorGolem__Mageroyal"
		subclass = type(golem.__name__+'__'+keyWord, (golem,),
						{"index": newIndex, "keyWord": keyWord, "description": keyWord + ". " + golem.description}
						)
		return subclass
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		game, ID = self.Game, self.ID
		if ID == game.turn and all(card.mana != 4 for card in game.Hand_Deck.decks[ID]):
			if game.mode == 0:
				manas, keyWords = (1, 5, 10), ("Rush", "Taunt", "Divine Shield", "Lifesteal", "Stealth", "Poisonouus")
				if game.picks:
					info_RNGSync, info_GUISync, isRandom, golemInfo = game.picks.pop(0)
					mana, keyWord, golem = golemInfo
					npchoice(range(6), 3, replace=False)
					npchoice(range(6), 3, replace=False)
					if game.GUI:
						i_mana, i_keyWord, i_golem = info_GUISync
						option_mana = (LesserGolem, GreaterGolem, SuperiorGolem)[i_mana](ID=ID)
						option_keyWord = GolemKeywordOptions[mana][keyWords.index(keyWord)](ID=ID)
						for indexOption, option in zip((i_mana, i_keyWord, i_golem), (option_mana, option_keyWord, golem(ID=ID))):
							game.GUI.discoverDecideAni(isRandom=isRandom, numOption=3, indexOption=indexOption, options=option)
					KazakusGolemShaper.discoverDecided(self, (mana, keyWord, golem), case="Guided")
				else:
					keyWords = npchoice(keyWords, 3, replace=False)
					if "byOthers" in comment:
						microsecond = datetime.now().microsecond
						i_mana, i_keyWord, i_golem = microsecond % 3, int(microsecond/10) % 3, int(microsecond/100) % 3
						mana, keyWord = manas[i_mana], keyWords[i_keyWord]
						if mana == 1: golems = (LesserGolem__Wildvine, LesserGolem__Gromsblood, LesserGolem__Icecap, LesserGolem__Firebloom, LesserGolem__Mageroyal, LesserGolem__Kingsblood)
						elif mana == 5: golems = (GreaterGolem__Wildvine, GreaterGolem__Gromsblood, GreaterGolem__Icecap, GreaterGolem__Firebloom, GreaterGolem__Mageroyal, GreaterGolem__Kingsblood)
						else: golems = (SuperiorGolem__Wildvine, SuperiorGolem__Gromsblood, SuperiorGolem__Icecap, SuperiorGolem__Firebloom, SuperiorGolem__Mageroyal, SuperiorGolem__Kingsblood)
						#Another n_choose_3
						golems = npchoice(golems, 3, replace=False)
						golem = golems[i_golem]
						if game.GUI:
							option_mana = (LesserGolem, GreaterGolem, SuperiorGolem)[i_mana](ID=ID)
							option_keyWord = GolemKeywordOptions[mana][keyWords.index(keyWord)](ID=ID)
							for indexOption, option in zip((i_mana, i_keyWord, i_golem), (option_mana, option_keyWord, golem(ID=ID))):
								game.GUI.discoverDecideAni(isRandom=True, numOption=3, indexOption=indexOption, options=option)
						KazakusGolemShaper.discoverDecided(self, (mana, keyWord, golem),
											 				case="Random", info_RNGSync=(6, 6), info_GUISync=(i_mana, i_keyWord, i_golem))
					else:
						info = [] #3次选择中积累出2+2+1个元素 (indexOption_mana, mana, indexOption_keyWord, keyWord, indexOption_effect)
						game.options = [LesserGolem(ID=ID), GreaterGolem(ID=ID), SuperiorGolem(ID=ID)]
						game.Discover.startDiscover(self, effectType=KazakusGolemShaper, info_RNGSync=(6, 6), info_GUISync=info)
						#The first discover changes the choices and leave a mana in there
						mana = info[0]
						#Whatever mana is, the keyword poolSize is always 6
						game.options = [choice(ID=ID) for choice in npchoice(GolemKeywordOptions[mana], 3, replace=False)]
						game.Discover.startDiscover(self, effectType=KazakusGolemShaper, info_RNGSync=(6, 6), info_GUISync=info)
						#Whatever mana is, the keyword poolSize is always 6
						game.options = [choice(ID=ID) for choice in npchoice(GolemEffectOptions[mana], 3, replace=False)]
						game.Discover.startDiscover(self, effectType=KazakusGolemShaper, info_RNGSync=(6, 6), info_GUISync=info)
		return None
	
	def discoverDecided(self, option, case, info_RNGSync=None, info_GUISync=None):
		if case == "Discovered": #The mana option and effect options have names
			if not option.name: #Keyword options。此时info_GUISync为[indexOption_mana, mana, indexOption_keyWord]
				info_GUISync.append(option.keyWord)
			else: #费用和效果选择
				#先选择费用，发现一次之后info_GUISync变为[indexOption_mana]
				if option.name == "Lesser Golem": info_GUISync.append(1)
				elif option.name == "Greater Golem": info_GUISync.append(5)
				elif option.name == "Superior Golem": info_GUISync.append(10)
				else: #effect option。此时info_GUISync为[indexOption_mana, mana, indexOption_keyWord, keyWord, indexOption_effect]
					#3次发现完成
					golem = GolemTable[option.name]
					indexOption_mana, mana, indexOption_keyWord, keyWord, indexOption_effect = info_GUISync
					self.Game.picks.append(((6, 6), (indexOption_mana, indexOption_keyWord, indexOption_effect),
											False, (mana, keyWord, golem)))
					self.addCardtoHand(KazakusGolemShaper.createGolem(self, mana, keyWord, golem), self.ID)
		else:
			mana, keyWord, golem = option
			if case == "Random": self.Game.picks.append((info_RNGSync, info_GUISync, True, option))
			self.addCardtoHand(KazakusGolemShaper.createGolem(self, mana, keyWord, golem), self.ID)
			
			
class LesserGolem(Option):
	name, type = "Lesser Golem", "Option_Minion"
	mana, attack, health = 1, -1, -1
	
class GreaterGolem(Option):
	name, type = "Greater Golem", "Option_Minion"
	mana, attack, health = 5, -1, -1
	
class SuperiorGolem(Option):
	name, type = "Superior Golem", "Option_Minion"
	mana, attack, health = 10, -1, -1
	
class Swiftthistle_1(Option):
	type, keyWord = "Option_Minion", "Rush"
	mana, attack, health = 1, -1, -1
	
class Swiftthistle_5(Option):
	type, keyWord = "Option_Minion", "Rush"
	mana, attack, health = 5, -1, -1
	
class Swiftthistle_10(Option):
	type, keyWord = "Option_Minion", "Rush"
	mana, attack, health = 10, -1, -1
	
class Earthroot_1(Option):
	type, keyWord = "Option_Minion", "Taunt"
	mana, attack, health = 1, -1, -1
	
class Earthroot_5(Option):
	type, keyWord = "Option_Minion", "Taunt"
	mana, attack, health = 5, -1, -1
	
class Earthroot_10(Option):
	type, keyWord = "Option_Minion", "Taunt"
	mana, attack, health = 10, -1, -1
	
class Sungrass_1(Option):
	type, keyWord = "Option_Minion", "Divine Shield"
	mana, attack, health = 1, -1, -1
	
class Sungrass_5(Option):
	type, keyWord = "Option_Minion", "Divine Shield"
	mana, attack, health = 5, -1, -1
	
class Sungrass_10(Option):
	type, keyWord = "Option_Minion", "Divine Shield"
	mana, attack, health = 10, -1, -1
	
class Liferoot_1(Option):
	type, keyWord = "Option_Minion", "Lifesteal"
	mana, attack, health = 1, -1, -1
	
class Liferoot_5(Option):
	type, keyWord = "Option_Minion", "Lifesteal"
	mana, attack, health = 5, -1, -1
	
class Liferoot_10(Option):
	type, keyWord = "Option_Minion", "Lifesteal"
	mana, attack, health = 10, -1, -1
	
class Fadeleaf_1(Option):
	type, keyWord = "Option_Minion", "Stealth"
	mana, attack, health = 1, -1, -1
	
class Fadeleaf_5(Option):
	type, keyWord = "Option_Minion", "Stealth"
	mana, attack, health = 5, -1, -1
	
class Fadeleaf_10(Option):
	type, keyWord = "Option_Minion", "Stealth"
	mana, attack, health = 10, -1, -1
	
class GraveMoss_1(Option):
	type, keyWord = "Option_Minion", "Poisonous"
	mana, attack, health = 1, -1, -1
	
class GraveMoss_5(Option):
	type, keyWord = "Option_Minion", "Poisonous"
	mana, attack, health = 5, -1, -1
	
class GraveMoss_10(Option):
	type, keyWord = "Option_Minion", "Poisonous"
	mana, attack, health = 10, -1, -1
	
GolemKeywordOptions = {1: (Swiftthistle_1, Earthroot_1, Sungrass_1, Liferoot_1, Fadeleaf_1, GraveMoss_1),
						5: (Swiftthistle_5, Earthroot_5, Sungrass_5, Liferoot_5, Fadeleaf_5, GraveMoss_5),
						10: (Swiftthistle_10, Earthroot_10, Sungrass_10, Liferoot_10, Fadeleaf_10, GraveMoss_10)
					   }
#Battlecries
class Wildvine_1(Option):
	name, type, description = "Wildvine_1", "Option_Minion", "Battlecry: Give your other minions +1/+1"
	mana, attack, health = 1, -1, -1
	
class Wildvine_5(Option):
	name, type, description = "Wildvine_5", "Option_Minion", "Battlecry: Give your other minions +2/+2"
	mana, attack, health = 5, -1, -1
	
class Wildvine_10(Option):
	name, type, description = "Wildvine_10", "Option_Minion", "Battlecry: Give your other minions +4/+4"
	mana, attack, health = 10, -1, -1
	
class Gromsblood_1(Option):
	name, type, description = "Gromsblood_1", "Option_Minion", "Battlecry: Summon a copy of this"
	mana, attack, health = 1, -1, -1
	
class Gromsblood_5(Option):
	name, type, description = "Gromsblood_5", "Option_Minion", "Battlecry: Summon a copy of this"
	mana, attack, health = 5, -1, -1
	
class Gromsblood_10(Option):
	name, type, description = "Gromsblood_10", "Option_Minion", "Battlecry: Summon a copy of this"
	mana, attack, health = 10, -1, -1
	
class Icecap_1(Option):
	name, type, description = "Icecap_1", "Option_Minion", "Battlecry: Freeze a random enemy minion"
	mana, attack, health = 1, -1, -1
	
class Icecap_5(Option):
	name, type, description = "Icecap_5", "Option_Minion", "Battlecry: Freeze two random enemy minions"
	mana, attack, health = 5, -1, -1
	
class Icecap_10(Option):
	name, type, description = "Icecap_10", "Option_Minion", "Battlecry: Freeze all enemy minions"
	mana, attack, health = 10, -1, -1
	
class Firebloom_1(Option):
	name, type, description = "Firebloom_1", "Option_Minion", "Battlecry: Deal 3 damage to a random enemy minion"
	mana, attack, health = 1, -1, -1
	
class Firebloom_5(Option):
	name, type, description = "Firebloom_5", "Option_Minion", "Battlecry: Deal 3 damage to two random enemy minions"
	mana, attack, health = 5, -1, -1
	
class Firebloom_10:
	name, type, description = "Firebloom_10", "Option_Minion", "Battlecry: Deal 3 damage to all enemy minions"
	mana, attack, health = 10, -1, -1
	
class Mageroyal_1:
	name, type, description = "Mageroyal_1", "Option_Minion", "Spell Damage +1"
	mana, attack, health = 1, -1, -1
	
class Mageroyal_5:
	name, type, description = "Mageroyal_5", "Option_Minion", "Spell Damage +2"
	mana, attack, health = 5, -1, -1
	
class Mageroyal_10:
	name, type, description = "Mageroyal_10", "Option_Minion", "Spell Damage +4"
	mana, attack, health = 10, -1, -1
	
class Kingsblood_1:
	name, type, description = "Kingsblood_1", "Option_Minion", "Battlecry: Draw a card"
	mana, attack, health = 1, -1, -1
	
class Kingsblood_5:
	name, type, description = "Kingsblood_5", "Option_Minion", "Battlecry: Draw 2 cards"
	mana, attack, health = 5, -1, -1
	
class Kingsblood_10:
	name, type, description = "Kingsblood_10", "Option_Minion", "Battlecry: Draw 4 cards"
	mana, attack, health = 10, -1, -1
	
GolemEffectOptions = {1: (Wildvine_1, Gromsblood_1, Icecap_1, Firebloom_1, Mageroyal_1, Kingsblood_1),
						5: (Wildvine_5, Gromsblood_5, Icecap_5, Firebloom_5, Mageroyal_5, Kingsblood_5),
						10: (Wildvine_10, Gromsblood_10, Icecap_10, Firebloom_10, Mageroyal_10, Kingsblood_10),
					  }
"""The Golems"""
#Mana 1 Golems
class LesserGolem__Wildvine(Minion):
	Class, race, name = "Neutral", "", "Lesser Golem"
	mana, attack, health = 1, 1, 1
	index = "THE_BARRENS~Neutral~Minion~1~1~1~~Lesser Golem~Wildvine~Battlecry~Uncollectible"
	requireTarget, keyWord, description = False, "", "Battlecry: Give your other minions +1/+1"
	name_CN = "小型魔像"

	def text(self, CHN):
		return effectsDict[type(self).keyWord]+"。战吼：使你的其他随从获得+1/+1" if CHN else type(self).description

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		for minion in self.Game.minionsonBoard(self.ID, self):
			minion.buffDebuff(1, 1)
		return None
		
class LesserGolem__Gromsblood(Minion):
	Class, race, name = "Neutral", "", "Lesser Golem"
	mana, attack, health = 1, 1, 1
	index = "THE_BARRENS~Neutral~Minion~1~1~1~~Lesser Golem~Gromsblood~Battlecry~Uncollectible"
	requireTarget, keyWord, description = False, "", "Battlecry: Summon a copy of this"
	name_CN = "小型魔像"

	def text(self, CHN):
		return effectsDict[type(self).keyWord]+"。战吼：召唤一个该随从的复制" if CHN else type(self).description

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.summon(self.selfCopy(self.ID, self), self.pos+1)
		return None
	
class LesserGolem__Icecap(Minion):
	Class, race, name = "Neutral", "", "Lesser Golem"
	mana, attack, health = 1, 1, 1
	index = "THE_BARRENS~Neutral~Minion~1~1~1~~Lesser Golem~Icecap~Battlecry~Uncollectible"
	requireTarget, keyWord, description = False, "", "Battlecry: Freeze a random enemy minion"
	name_CN = "小型魔像"

	def text(self, CHN):
		return effectsDict[type(self).keyWord]+"。战吼：随机冻结一个敌方随从" if CHN else type(self).description

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		targets = self.Game.minionsAlive(3 - self.ID)
		if targets: npchoice(targets).getsStatus("Frozen")
		return None

class LesserGolem__Firebloom(Minion):
	Class, race, name = "Neutral", "", "Lesser Golem"
	mana, attack, health = 1, 1, 1
	index = "THE_BARRENS~Neutral~Minion~1~1~1~~Lesser Golem~Firebloom~Battlecry~Uncollectible"
	requireTarget, keyWord, description = False, "", "Battlecry: Deal 3 damage to a random enemy minion"
	name_CN = "小型魔像"

	def text(self, CHN):
		return effectsDict[type(self).keyWord]+"。战吼：随机对一个敌方随从造成3点伤害" if CHN else type(self).description

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		targets = self.Game.minionsAlive(3 - self.ID)
		if targets: self.dealsDamage(npchoice(targets), 3)
		return None

class LesserGolem__Mageroyal(Minion):
	Class, race, name = "Neutral", "", "Lesser Golem"
	mana, attack, health = 1, 1, 1
	index = "THE_BARRENS~Neutral~Minion~1~1~1~~Lesser Golem~Mageroyal~Spell Damage~Uncollectible"
	requireTarget, keyWord, description = False, "", "Spell Damage +1"
	name_CN = "小型魔像"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.keyWords["Spell Damage"] = 1

	def text(self, CHN):
		return effectsDict[type(self).keyWord]+"。法术伤害+1" if CHN else type(self).description

class LesserGolem__Kingsblood(Minion):
	Class, race, name = "Neutral", "", "Lesser Golem"
	mana, attack, health = 1, 1, 1
	index = "THE_BARRENS~Neutral~Minion~1~1~1~~Lesser Golem~Kingsblood~Battlecry~Uncollectible"
	requireTarget, keyWord, description = False, "", "Battlecry: Draw a card"
	name_CN = "小型魔像"

	def text(self, CHN):
		return effectsDict[type(self).keyWord]+"。战吼：抽一张牌" if CHN else type(self).description

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.Game.Hand_Deck.drawCard(self.ID)
		return None
		
#Mana 5 Golems
class GreaterGolem__Wildvine(Minion):
	Class, race, name = "Neutral", "", "Greater Golem"
	mana, attack, health = 5, 5, 5
	index = "THE_BARRENS~Neutral~Minion~5~5~5~~Greater Golem~Wildvine~Battlecry~Uncollectible"
	requireTarget, keyWord, description = False, "", "Battlecry: Give your other minions +2/+2"
	name_CN = "大型魔像"

	def text(self, CHN):
		return effectsDict[type(self).keyWord]+"。战吼：使你的其他随从获得+2/+2" if CHN else type(self).description

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		for minion in self.Game.minionsonBoard(self.ID, self):
			minion.buffDebuff(2, 2)
		return None
		
class GreaterGolem__Gromsblood(Minion):
	Class, race, name = "Neutral", "", "Greater Golem"
	mana, attack, health = 5, 5, 5
	index = "THE_BARRENS~Neutral~Minion~5~5~5~~Greater Golem~Gromsblood~Battlecry~Uncollectible"
	requireTarget, keyWord, description = False, "", "Battlecry: Summon a copy of this"
	name_CN = "大型魔像"

	def text(self, CHN):
		return effectsDict[type(self).keyWord]+"。战吼：召唤一个该随从的复制" if CHN else type(self).description

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.summon(self.selfCopy(self.ID, self), self.pos+1)
		return None
	
class GreaterGolem__Icecap(Minion):
	Class, race, name = "Neutral", "", "Greater Golem"
	mana, attack, health = 5, 5, 5
	index = "THE_BARRENS~Neutral~Minion~5~5~5~~Greater Golem~Icecap~Battlecry~Uncollectible"
	requireTarget, keyWord, description = False, "", "Battlecry: Freeze two random enemy minions"
	name_CN = "大型魔像"

	def text(self, CHN):
		return effectsDict[type(self).keyWord]+"。战吼：随机冻结两个敌方随从" if CHN else type(self).description

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		minions = self.Game.minionsAlive(3 - self.ID)
		if minions:
			minions = list(npchoice(minions, min(2, len(minions)), replace=False))
			for minion in minions: minion.getsStatus("Frozen")
		return None

class GreaterGolem__Firebloom(Minion):
	Class, race, name = "Neutral", "", "Greater Golem"
	mana, attack, health = 5, 5, 5
	index = "THE_BARRENS~Neutral~Minion~5~5~5~~Greater Golem~Firebloom~Battlecry~Uncollectible"
	requireTarget, keyWord, description = False, "", "Battlecry: Deal 3 damage to two random enemy minions"
	name_CN = "大型魔像"

	def text(self, CHN):
		return effectsDict[type(self).keyWord]+"。战吼：随机对两个敌方随从造成3点伤害" if CHN else type(self).description

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		minions = self.Game.minionsAlive(3 - self.ID)
		if minions:
			minions = npchoice(minions, min(2, len(minions)), replace=False)
			self.dealsAOE(minions, [3] * len(minions))
		return None

class GreaterGolem__Mageroyal(Minion):
	Class, race, name = "Neutral", "", "Greater Golem"
	mana, attack, health = 5, 5, 5
	index = "THE_BARRENS~Neutral~Minion~5~5~5~~Greater Golem~Mageroyal~Spell Damage~Uncollectible"
	requireTarget, keyWord, description = False, "", "Spell Damage +2"
	name_CN = "大型魔像"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.keyWords["Spell Damage"] = 2

	def text(self, CHN):
		return effectsDict[type(self).keyWord]+"。法术伤害+2" if CHN else type(self).description

class GreaterGolem__Kingsblood(Minion):
	Class, race, name = "Neutral", "", "Greater Golem"
	mana, attack, health = 5, 5, 5
	index = "THE_BARRENS~Neutral~Minion~5~5~5~~Greater Golem~Kingsblood~Battlecry~Uncollectible"
	requireTarget, keyWord, description = False, "", "Battlecry: Draw 2 cards"
	name_CN = "大型魔像"

	def text(self, CHN):
		return effectsDict[type(self).keyWord]+"。战吼：抽两张牌" if CHN else type(self).description

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.Game.Hand_Deck.drawCard(self.ID)
		self.Game.Hand_Deck.drawCard(self.ID)
		return None
		
#Mana 10 Golems
class SuperiorGolem__Wildvine(Minion):
	Class, race, name = "Neutral", "", "Superior Golem"
	mana, attack, health = 10, 10, 10
	index = "THE_BARRENS~Neutral~Minion~10~10~10~~Superior Golem~Wildvine~Battlecry~Uncollectible"
	requireTarget, keyWord, description = False, "", "Battlecry: Give your other minions +4/+4"
	name_CN = "超级魔像"

	def text(self, CHN):
		return effectsDict[type(self).keyWord]+"。战吼：使你的其他随从获得+4/+4" if CHN else type(self).description

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		for minion in self.Game.minionsonBoard(self.ID, self):
			minion.buffDebuff(4, 4)
		return None
		
class SuperiorGolem__Gromsblood(Minion):
	Class, race, name = "Neutral", "", "Superior Golem"
	mana, attack, health = 10, 10, 10
	index = "THE_BARRENS~Neutral~Minion~10~10~10~~Superior Golem~Gromsblood~Battlecry~Uncollectible"
	requireTarget, keyWord, description = False, "", "Battlecry: Summon a copy of this"
	name_CN = "超级魔像"
	
	def text(self, CHN):
		return effectsDict[type(self).keyWord]+"。战吼：召唤一个该随从的复制" if CHN else type(self).description

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.summon(self.selfCopy(self.ID, self), self.pos+1)
		return None
	
class SuperiorGolem__Icecap(Minion):
	Class, race, name = "Neutral", "", "Superior Golem"
	mana, attack, health = 10, 10, 10
	index = "THE_BARRENS~Neutral~Minion~10~10~10~~Superior Golem~Icecap~Battlecry~Uncollectible"
	requireTarget, keyWord, description = False, "", "Battlecry: Freeze all enemy minions"
	name_CN = "超级魔像"
	
	def text(self, CHN):
		return effectsDict[type(self).keyWord]+"。战吼：冻结所有敌方随从" if CHN else type(self).description

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		for minion in self.Game.minionsonBoard(3-self.ID):
			minion.getsStatus("Frozen")
		return None

class SuperiorGolem__Firebloom(Minion):
	Class, race, name = "Neutral", "", "Superior Golem"
	mana, attack, health = 10, 10, 10
	index = "THE_BARRENS~Neutral~Minion~10~10~10~~Superior Golem~Firebloom~Battlecry~Uncollectible"
	requireTarget, keyWord, description = False, "", "Battlecry: Deal 3 damage to all enemy minions"
	name_CN = "超级魔像"
	
	def text(self, CHN):
		return effectsDict[type(self).keyWord]+"。战吼：对所有敌方随从造成3点伤害" if CHN else type(self).description

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		targets = self.Game.minionsonBoard(3-self.ID)
		self.dealsAOE(targets, [3]*len(targets))
		return None

class SuperiorGolem__Mageroyal(Minion):
	Class, race, name = "Neutral", "", "Superior Golem"
	mana, attack, health = 10, 10, 10
	index = "THE_BARRENS~Neutral~Minion~10~10~10~~Superior Golem~Mageroyal~Spell Damage~Uncollectible"
	requireTarget, keyWord, description = False, "", "Spell Damage +4"
	name_CN = "超级魔像"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.keyWords["Spell Damage"] = 4
	
	def text(self, CHN):
		return effectsDict[type(self).keyWord]+" 法术伤害+4" if CHN else type(self).description

class SuperiorGolem__Kingsblood(Minion):
	Class, race, name = "Neutral", "", "Superior Golem"
	mana, attack, health = 10, 10, 10
	index = "THE_BARRENS~Neutral~Minion~10~10~10~~Superior Golem~Kingsblood~Battlecry~Uncollectible"
	requireTarget, keyWord, description = False, "", "Battlecry: Draw 4 cards"
	name_CN = "超级魔像"

	def text(self, CHN):
		return effectsDict[type(self).keyWord]+"。战吼：抽四张牌" if CHN else type(self).description

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		for i in range(4):
			self.Game.Hand_Deck.drawCard(self.ID)
		return None
	
GolemTable = {"Wildvine_1": LesserGolem__Wildvine, "Wildvine_5": GreaterGolem__Wildvine, "Wildvine_10": SuperiorGolem__Wildvine,
				"Gromsblood_1": LesserGolem__Gromsblood, "Gromsblood_5": GreaterGolem__Gromsblood, "Gromsblood_10": SuperiorGolem__Gromsblood,
				"Icecap_1": LesserGolem__Icecap, "Icecap_5": GreaterGolem__Icecap, "Icecap_10": SuperiorGolem__Icecap,
				"Firebloom_1": LesserGolem__Firebloom, "Firebloom_5": GreaterGolem__Firebloom, "Firebloom_10": SuperiorGolem__Firebloom,
				"Mageroyal_1": LesserGolem__Mageroyal,  "Mageroyal_5": GreaterGolem__Mageroyal,  "Mageroyal_10": SuperiorGolem__Mageroyal,
				"Kingsblood_1": LesserGolem__Kingsblood, "Kingsblood_5": GreaterGolem__Kingsblood, "Kingsblood_10": SuperiorGolem__Kingsblood,
			  }



class SouthseaScoundrel(Minion):
	Class, race, name = "Neutral", "Pirate", "Southsea Scoundrel"
	mana, attack, health = 4, 5, 5
	index = "THE_BARRENS~Neutral~Minion~4~5~5~Pirate~Southsea Scoundrel~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Discover a card from your opponent's deck. They draw theirs as well"
	name_CN = "南海恶徒"
	
	def getCopyfromOppoDeck_TheyDrawTheirs(self, index, card):
		self.addCardtoHand(card.selfCopy(self.ID, self), self.ID, byDiscover=True, creator=type(self))
		self.Game.Hand_Deck.drawCard(3 - self.ID, index)
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.discoverfromList(SouthseaScoundrel, comment, conditional=lambda card: True,
							  ls=self.Game.Hand_Deck.decks[3-self.ID])
		return None
	
	def discoverDecided(self, option, case, info_RNGSync=None, info_GUISync=None):
		self.handleDiscoveredCardfromList(option, case, ls=self.Game.Hand_Deck.decks[3 - self.ID],
										  func=lambda index, card: SouthseaScoundrel.getCopyfromOppoDeck_TheyDrawTheirs(self, index, card),
										  info_RNGSync=info_RNGSync, info_GUISync=info_GUISync)
		

class SpiritHealer(Minion):
	Class, race, name = "Neutral", "", "Spirit Healer"
	mana, attack, health = 4, 3, 6
	index = "THE_BARRENS~Neutral~Minion~4~3~6~~Spirit Healer"
	requireTarget, keyWord, description = False, "", "After you cast Holy spell, give a friendly minion +2 Health"
	name_CN = "灵魂医者"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_SpiritHealer(self)]
		
class Trig_SpiritHealer(TrigBoard):
	def text(self, CHN):
		return "在你施放一个神圣法术后，随机使一个友方随从获得+2生命值" if CHN \
				else "After you cast Holy spell, give a friendly minion +2 Health"
				
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		minions = self.entity.Game.minionsonBoard[ID]
		if minions: npchoice(minions).buffDebuff(0, 2)
			
			
"""Mana 5 Cards"""
class BarrensBlacksmith(Minion):
	Class, race, name = "Neutral", "", "Barrens Blacksmith"
	mana, attack, health = 5, 3, 5
	index = "THE_BARRENS~Neutral~Minion~5~3~5~~Barrens Blacksmith~Frenzy"
	requireTarget, keyWord, description = False, "", "Frenzy: Give your other minions +2/+2"
	name_CN = "贫瘠之地铁匠"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_BarrensBlacksmith(self)]

class Trig_BarrensBlacksmith(Frenzy):
	def text(self, CHN):
		return "暴怒：对所有敌方随从造成等同于该随从的攻击力的伤害" if CHN \
			else "Frenzy: Give your other minions +2/+2"
	
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		for minion in self.entity.Game.minionsonBoard(self.entity.ID, self.entity):
			minion.buffDebuff(2, 2)


class BurningBladeAcolyte(Minion):
	Class, race, name = "Neutral", "", "Burning Blade Acolyte"
	mana, attack, health = 5, 1, 1
	index = "THE_BARRENS~Neutral~Minion~5~1~1~~Burning Blade Acolyte~Deathrattle"
	requireTarget, keyWord, description = False, "", "Deathrattle: Summon a 5/8 Demonspawn with Taunt"
	name_CN = "火刃侍僧"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.deathrattles = [SummonaDemonspawn(self)]

class SummonaDemonspawn(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.summon(Demonspawn(self.entity.Game, self.entity.ID), self.entity.pos + 1)
	
	def text(self, CHN):
		return "亡语：召唤一个5/8并具有嘲讽的的恶魔生物" if CHN else "Deathrattle: Summon a 5/8 Demonspawn with Taunt"

class Demonspawn(Minion):
	Class, race, name = "Neutral", "Demon", "Demonspawn"
	mana, attack, health = 6, 5, 8
	index = "THE_BARRENS~Neutral~Minion~6~5~8~Demon~Demonspawn~Taunt~Uncollectible"
	requireTarget, keyWord, description = False, "Taunt", "Taunt"
	name_CN = "恶魔生物"


class GoldRoadGrunt(Minion):
	Class, race, name = "Neutral", "", "Gold Road Grunt"
	mana, attack, health = 5, 3, 7
	index = "THE_BARRENS~Neutral~Minion~5~3~7~~Gold Road Grunt~Taunt~Frenzy"
	requireTarget, keyWord, description = False, "Taunt", "Taunt. Frenzy: Gain Armor equal to the damage taken"
	name_CN = "黄金之路步兵"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_GoldRoadGrunt(self)]

class Trig_GoldRoadGrunt(Frenzy):
	def text(self, CHN):
		return "暴怒：获得等同于所受伤害的护甲值" if CHN else "Frenzy: Gain Armor equal to the damage taken"
	
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.heroes[self.entity.ID].gainsArmor(number)


class RazormaneRaider(Minion):
	Class, race, name = "Neutral", "Quilboar", "Razormane Raider"
	mana, attack, health = 5, 5, 6
	index = "THE_BARRENS~Neutral~Minion~5~5~6~Quilboar~Razormane Raider~Frenzy"
	requireTarget, keyWord, description = False, "", "Frenzy: Attack a random enemy"
	name_CN = "钢鬃掠夺者"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_RazormaneRaider(self)]

class Trig_RazormaneRaider(Frenzy):
	def text(self, CHN):
		return "暴怒：随机攻击一个敌人" if CHN else "Frenzy: Attack a random enemy"
	
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		objs = self.entity.Game.charsAlive(3-self.entity.ID)
		if objs: self.entity.Game.battle(self.entity, npchoice(objs), verifySelectable=False, useAttChance=False, resolveDeath=False)
	

class ShadowHunterVoljin(Minion):
	Class, race, name = "Neutral", "", "Shadow Hunter Vol'jin"
	mana, attack, health = 5, 3, 6
	index = "THE_BARRENS~Neutral~Minion~5~3~6~~Shadow Hunter Vol'jin~Battlecry~Legendary"
	requireTarget, keyWord, description = True, "", "Battlecry: Choose a minion. Swap it with a random one in its owners hand"
	name_CN = "暗影猎手沃金"
	
	def targetExists(self, choice=0):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target != self and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target and not target.dead and target.onBoard: #战吼触发时自己不能死亡。
			#假设对方手牌中没有随从时不能交换
			curGame, ID = self.Game, target.ID
			hand = curGame.Hand_Deck.hands[ID]
			if curGame.mode == 0:
				minions = [i for i, card in enumerate(hand) if card.type == "Minion"]
				if minions:
					i = npchoice(minions)
					minion, pos = curGame.Hand_Deck.hands[ID][i], target.pos
					minion.disappears(deathrattlesStayArmed=False)
					curGame.removeMinionorWeapon(minion)
					minion.reset(ID)
					#下面节选自Hand.py的addCardtoHand方法，但是要跳过手牌已满的检测
					hand.append(minion)
					minion.entersHand()
					curGame.sendSignal("CardEntersHand", minion, None, [minion], 0, "")
					#假设先发送牌进入手牌的信号，然后召唤随从
					curGame.summonfrom(i, ID, pos, self, source='H')
		return target
		
		
class TaurajoBrave(Minion):
	Class, race, name = "Neutral", "", "Taurajo Brave"
	mana, attack, health = 6, 4, 8
	index = "THE_BARRENS~Neutral~Minion~6~4~8~~Taurajo Brave~Frenzy"
	requireTarget, keyWord, description = False, "", "Frenzy: Destroy a random enemy minion"
	name_CN = "陶拉祖武士"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_TaurajoBrave(self)]

class Trig_TaurajoBrave(Frenzy):
	def text(self, CHN):
		return "暴怒：随机消灭一个敌方随从" if CHN else "Frenzy: Destroy a random enemy minion"
	
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		minions = self.entity.Game.minionsAlive(3 - self.entity.ID)
		if minions: self.entity.Game.killMinion(self.entity, npchoice(minions))


class KargalBattlescar(Minion):
	Class, race, name = "Neutral", "", "Kargal Battlescar"
	mana, attack, health = 7, 5, 5
	index = "THE_BARRENS~Neutral~Minion~7~5~5~~Kargal Battlescar~Battlecry~Legendary"
	requireTarget, keyWord, description = False, "", "Battlecry: Summon a 5/5 Lookout for each Watch Post you've summoned this game"
	name_CN = "卡加尔·战痕"
	
	def effCanTrig(self):
		self.effectViable = self.Game.Counters.numWatchPostSummoned[self.ID] > 0
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		minions = [Lookout(self.Game, self.ID) for i in range(len(self.Game.Counters.numWatchPostSummoned))]
		if minions:
			pos = (self.pos, "leftandRight") if self.onBoard else (-1, "totheRightEnd")
			self.summon(minions, pos)
		return None

class Lookout(Minion):
	Class, race, name = "Neutral", "", "Lookout"
	mana, attack, health = 5, 5, 5
	index = "THE_BARRENS~Neutral~Minion~5~5~5~~Lookout~Uncollectible"
	requireTarget, keyWord, description = False, "", ""
	name_CN = "哨兵"


class PrimordialProtector(Minion):
	Class, race, name = "Neutral", "Elemental", "Primordial Protector"
	mana, attack, health = 8, 6, 6
	index = "THE_BARRENS~Neutral~Minion~8~6~6~Elemental~Primordial Protector~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Draw your highest Cost spell. Summon a random minion with the same Cost"
	name_CN = "始生保护者"
	poolIdentifier = "0-Cost Minions to Summon"
	@classmethod
	def generatePool(cls, pools):
		return ["%d-Cost Minions to Summon" % cost for cost in pools.MinionsofCost.keys()], \
			   list(pools.MinionsofCost.values())
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		highestCost, spells = -1, []
		for i, card in enumerate(self.Game.Hand_Deck.decks[self.ID]):
			if card.type == "Spell":
				if card.mana > highestCost: highestCost, spells = card.mana, [i]
				elif card.mana == highestCost: spells.append(i)
		if spells:
			minion = npchoice(self.rngPool("%d-Cost Minions to Summon" % highestCost))
			self.Game.Hand_Deck.drawCard(self.ID, npchoice(spells))
			self.summon(minion(self.Game, self.ID), self.pos+1)
		return None


""""Demon Hunter cards"""
class FuryRank1(Spell):
	Class, school, name = "Demon Hunter", "Fel", "Fury (Rank 1)"
	requireTarget, mana = False, 1
	index = "THE_BARRENS~Demon Hunter~Spell~1~Fel~Fury (Rank 1)"
	description = "Give your hero +2 Attack this turn. (Upgrades when you have 5 mana.)"
	name_CN = "怒火（等级1）"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsHand = [Trig_ForgeUpgrade(self, FuryRank2, 5)]  #只有在手牌中才会升级
	
	def entersHand(self):
		card = FuryRank2(self.Game, self.ID) if self.Game.Manas.manasUpper[self.ID] > 4 else self
		card.inHand = True
		card.onBoard = card.inDeck = False
		card.enterHandTurn = card.Game.numTurn
		for trig in card.trigsHand: trig.connect()
		return card
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		self.Game.heroes[self.ID].gainAttack(2)
		return None


class FuryRank2(Spell):
	Class, school, name = "Demon Hunter", "Fel", "Fury (Rank 2)"
	requireTarget, mana = False, 1
	index = "THE_BARRENS~Demon Hunter~Spell~1~Fel~Fury (Rank 2)~Uncollectible"
	description = "Give your hero +3 Attack this turn. (Upgrades when you have 10 mana.)"
	name_CN = "怒火（等级2）"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsHand = [Trig_ForgeUpgrade(self, FuryRank3, 10)]  #只有在手牌中才会升级
	
	def entersHand(self):
		card = FuryRank3(self.Game, self.ID) if self.Game.Manas.manasUpper[self.ID] > 9 else self
		card.inHand = True
		card.onBoard = card.inDeck = False
		card.enterHandTurn = card.Game.numTurn
		for trig in card.trigsHand: trig.connect()
		return card
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		self.Game.heroes[self.ID].gainAttack(3)
		return None


class FuryRank3(Spell):
	Class, school, name = "Demon Hunter", "Fel", "Fury (Rank 3)"
	requireTarget, mana = False, 1
	index = "THE_BARRENS~Demon Hunter~Spell~1~Fel~Fury (Rank 3)~Uncollectible"
	description = "Give your hero +4 Attack this turn"
	name_CN = "怒火（等级3）"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		self.Game.heroes[self.ID].gainAttack(4)
		return None


class Tuskpiercer(Weapon):
	Class, name, description = "Demon Hunter", "Tuskpiercer", "Deathrattle: Draw a Deathrattle minion"
	mana, attack, durability = 1, 1, 2
	index = "THE_BARRENS~Demon Hunter~Weapon~1~1~2~Tuskpiercer~Deathrattle"
	name_CN = "獠牙锥刃"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.deathrattles = [DrawaDeathrattleMinion(self)]

class DrawaDeathrattleMinion(Deathrattle_Weapon):
	def text(self, CHN):
		return "亡语：抽一张亡语随从牌" if CHN else "Deathrattle: Draw a Deathrattle minion"
	
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		minions = [i for i, card in enumerate(self.entity.Game.Hand_Deck.decks[self.entity.ID]) if card.type == "Minion" and card.deathrattles]
		if minions: self.entity.Game.Hand_Deck.drawCard(self.entity.ID, npchoice(minions))


class Razorboar(Minion):
	Class, race, name = "Demon Hunter", "Beast", "Razorboar"
	mana, attack, health = 2, 3, 2
	index = "THE_BARRENS~Demon Hunter~Minion~2~3~2~Beast~Razorboar~Deathrattle"
	requireTarget, keyWord, description = False, "", "Deathrattle: Summon a Deathrattle minion that costs (3) or less from your hand"
	name_CN = "剃刀野猪"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.deathrattles = [SummonDeathrattleMinionfromHand_Mana3orLess(self)]

class SummonDeathrattleMinionfromHand_Mana3orLess(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		minion = self.entity
		minions = [i for i, card in enumerate(minion.Game.Hand_Deck.hands[minion.ID]) if card.type == "Minion" and card.deathrattles and card.mana < 4]
		if minions:
			minion.Game.summonfrom(npchoice(minions), minion.ID, minion.pos+1, minion, source='H')
	
	def text(self, CHN):
		return "亡语：从你的手牌中召唤一个法力值消耗小于或等于(3)点的亡语随从" if CHN \
			else "Deathrattle: Summon a Deathrattle minion that costs (3) or less from your hand"


class SigilofFlame(Spell):
	Class, school, name = "Demon Hunter", "Fel", "Sigil of Flame"
	requireTarget, mana = False, 2
	index = "THE_BARRENS~Demon Hunter~Spell~2~Fel~Sigil of Flame"
	description = "At the start of your next turn, deal 3 damage to all enemy minions"
	name_CN = "烈焰咒符"
	def text(self, CHN):
		damage = (3 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		return "在你的下个回合开始时，对所有敌方随从造成%d点伤害" % damage if CHN else "At the start of your next turn, deal %d damage to all enemy minions" % damage
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		SigilofFlame_Effect(self.Game, self.ID).connect()
		return None

class SigilofFlame_Effect:
	def __init__(self, Game, ID):
		self.Game, self.ID = Game, ID
		self.card = SigilofFlame(self.Game, self.ID)
		
	def connect(self):
		if all(not isinstance(trig, SigilofFlame_Effect) or trig.ID != self.ID for trig in self.Game.turnStartTrigger):
			self.Game.turnStartTrigger.append(self)
			if self.Game.GUI: self.Game.GUI.heroZones[self.ID].addaTrig(self.card)
			
	def turnStartTrigger(self):
		if self.Game.GUI: self.Game.GUI.showOffBoardTrig(self.card)
		damage = (3 + self.card.countSpellDamage()) * (2 ** self.card.countDamageDouble())
		targets = self.Game.minionsonBoard(3-self.ID)
		self.card.dealsAOE(targets, [damage]*len(targets))
		try: self.Game.turnStartTrigger.remove(self)
		except: pass
		if self.Game.GUI: self.Game.GUI.heroZones[self.ID].removeaTrig(self.card)
		
	def createCopy(self, game):
		if self not in game.copiedObjs:
			trigCopy = type(self)(game, self.ID)
			game.copiedObjs[self] = trigCopy
			return trigCopy
		else:
			return game.copiedObjs[self]


class SigilofSilence(Spell):
	Class, school, name = "Demon Hunter", "Shadow", "Sigil of Silence"
	requireTarget, mana = False, 0
	index = "THE_BARRENS~Demon Hunter~Spell~0~Shadow~Sigil of Silence"
	description = "At the start of your next turn, Silence all enemy minions"
	name_CN = "沉默咒符"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		SigilofSilence_Effect(self.Game, self.ID).connect()
		return None

class SigilofSilence_Effect:
	def __init__(self, Game, ID):
		self.Game, self.ID = Game, ID
		self.card = SigilofSilence(self.Game, self.ID)
		
	def connect(self):
		if all(not isinstance(trig, SigilofSilence_Effect) or trig.ID != self.ID for trig in self.Game.turnStartTrigger):
			self.Game.turnStartTrigger.append(self)
			if self.Game.GUI: self.Game.GUI.heroZones[self.ID].addaTrig(self.card)
			print("After adding, self.card.btn", self.card.btn)
	
	def turnStartTrigger(self):
		print("self.card.btn before triggering", self.card.btn)
		if self.Game.GUI: self.Game.GUI.showOffBoardTrig(self.card)
		print("self.card.btn before triggering2", self.card.btn)
		for minion in self.Game.minionsonBoard(3 - self.ID):
			minion.getsSilenced()
		try: self.Game.turnStartTrigger.remove(self)
		except: pass
		print("self.card.btn", self.card.btn)
		if self.Game.GUI: self.Game.GUI.heroZones[self.ID].removeaTrig(self.card)
	
	def createCopy(self, game):
		if self not in game.copiedObjs:
			trigCopy = type(self)(game, self.ID)
			game.copiedObjs[self] = trigCopy
			return trigCopy
		else:
			return game.copiedObjs[self]


class VileCall(Spell):
	Class, school, name = "Demon Hunter", "", "Vile Call"
	requireTarget, mana = False, 3
	index = "THE_BARRENS~Demon Hunter~Spell~3~~Vile Call"
	description = "Summon two 2/2 Demons with Lifesteal"
	name_CN = "邪恶召唤"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.summon([RavenousVilefiend(self.Game, self.ID) for i in range(2)], (-1, "totheRightEnd"))
		return None

class RavenousVilefiend(Minion):
	Class, race, name = "Demon Hunter", "Demon", "Ravenous Vilefiend"
	mana, attack, health = 2, 2, 2
	index = "THE_BARRENS~Demon Hunter~Minion~2~2~2~Demon~Ravenous Vilefiend~Lifesteal~Uncollectible"
	requireTarget, keyWord, description = False, "Lifesteal", "Lifesteal"
	name_CN = "贪食邪犬"


class RazorfenBeastmaster(Minion):
	Class, race, name = "Demon Hunter", "Quilboar", "Razorfen Beastmaster"
	mana, attack, health = 3, 3, 3
	index = "THE_BARRENS~Demon Hunter~Minion~3~3~3~Quilboar~Razorfen Beastmaster~Deathrattle"
	requireTarget, keyWord, description = False, "", "Deathrattle: Summon a Deathrattle minion that costs (4) or less from your hand"
	name_CN = "剃刀沼泽兽王"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.deathrattles = [SummonDeathrattleMinionfromHand_Mana4orLess(self)]

class SummonDeathrattleMinionfromHand_Mana4orLess(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		def effect(self, signal, ID, subject, target, number, comment, choice=0):
			minion = self.entity
			minions = [i for i, card in enumerate(minion.Game.Hand_Deck.hands[minion.ID]) if card.type == "Minion" and card.deathrattles and card.mana < 5]
			if minions:
				minion.Game.summonfrom(npchoice(minions), minion.ID, minion.pos + 1, minion, source='H')
	
	def text(self, CHN):
		return "亡语：从你的手牌中召唤一个法力值消耗小于或等于(4)点的亡语随从" if CHN \
			else "Deathrattle: Summon a Deathrattle minion that costs (4) or less from your hand"


class KurtrusAshfallen(Minion):
	Class, race, name = "Demon Hunter", "", "Kurtrus Ashfallen"
	mana, attack, health = 4, 3, 4
	index = "THE_BARRENS~Demon Hunter~Minion~4~3~4~~Kurtrus Ashfallen~Battlecry~Outcast~Legendary"
	requireTarget, keyWord, description = False, "", "Battlecry: Attack the left and right-most enemy minions. Outcast: Immune this turn"
	name_CN = "库尔特鲁斯·陨烬"
	
	def effCanTrig(self):
		self.effectViable = self.Game.Hand_Deck.outcastcanTrig(self)
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if posinHand == 0 or posinHand == -1:
			self.getsSilenced("Immune")
		minions = self.Game.minionsonBoard(3-self.ID)
		if minions and self.onBoard and self.health > 0 and not self.dead and minions[0].health > 0 and not minions[0].dead:
			self.Game.battle(self, minions[0], verifySelectable=False, useAttChance=False, resolveDeath=False)
		if minions and self.onBoard and self.health > 0 and not self.dead and minions[-1].health > 0 and not minions[-1].dead:
			self.Game.battle(self, minions[-1], verifySelectable=False, useAttChance=False, resolveDeath=False)
		return None


class VengefulSpirit(Minion):
	Class, race, name = "Demon Hunter", "", "Vengeful Spirit"
	mana, attack, health = 4, 4, 4
	index = "THE_BARRENS~Demon Hunter~Minion~4~4~4~~Vengeful Spirit~Outcast"
	requireTarget, keyWord, description = False, "", "Outcast: Draw two Deathrattle minions"
	name_CN = "复仇之魂"
	
	def effCanTrig(self):
		self.effectViable = self.Game.Hand_Deck.outcastcanTrig(self)
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if posinHand == 0 or posinHand == -1:
			ownDeck = self.Game.Hand_Deck.decks[self.ID]
			for num in range(2):
				minions = [i for i, card in enumerate(ownDeck) if card.type == "Minion" and card.deathrattles]
				if minions: self.Game.Hand_Deck.drawCard(self.ID, npchoice(minions))
				else: break
		return None


class DeathSpeakerBlackthorn(Minion):
	Class, race, name = "Demon Hunter", "Quilboar", "Death Speaker Blackthorn"
	mana, attack, health = 7, 3, 6
	index = "THE_BARRENS~Demon Hunter~Minion~7~3~6~Quilboar~Death Speaker Blackthorn~Battlecry~Legendary"
	requireTarget, keyWord, description = False, "", "Battlecry: Summon 3 Deathrattle minions that cost (5) or less from your deck"
	name_CN = "亡语者布莱克松"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		game = self.Game
		refMinion = self
		for num in range(3):
			minions = [i for i, card in enumerate(game.Hand_Deck.hands[self.ID]) if card.type == "Minion" and card.deathrattles]
			if minions: refMinion = game.summonfrom(npchoice(minions), self.ID, refMinion.pos + 1, self, source='D')
			else: break
		return None


"""Druid cards"""
class LivingSeedRank1(Spell):
	Class, school, name = "Druid", "Nature", "Living Seed (Rank 1)"
	requireTarget, mana = False, 2
	index = "THE_BARRENS~Druid~Spell~2~Nature~Living Seed (Rank 1)"
	description = "Draw a Beast. Reduce its Cost by (1). (Upgrades when you have 5 mana.)"
	name_CN = "生命之种（等级1）"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsHand = [Trig_ForgeUpgrade(self, LivingSeedRank2, 5)]  #只有在手牌中才会升级
	
	def entersHand(self):
		card = LivingSeedRank2(self.Game, self.ID) if self.Game.Manas.manasUpper[self.ID] > 4 else self
		card.inHand = True
		card.onBoard = card.inDeck = False
		card.enterHandTurn = card.Game.numTurn
		for trig in card.trigsHand: trig.connect()
		return card
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		beasts = [i for i, card in enumerate(self.Game.Hand_Deck.decks[self.ID]) if card.type == "Minion" and "Beast" in card.race]
		if beasts:
			beast = self.Game.Hand_Deck.drawCard(self.ID, npchoice(beasts))[0]
			if beast: ManaMod(beast, changeby=-1).applies()
		return None

class LivingSeedRank2(Spell):
	Class, school, name = "Druid", "Nature", "Living Seed (Rank 2)"
	requireTarget, mana = False, 2
	index = "THE_BARRENS~Druid~Spell~2~Nature~Living Seed (Rank 2)~Uncollectible"
	description = "Draw a Beast. Reduce its Cost by (2). (Upgrades when you have 10 mana.)"
	name_CN = "生命之种（等级2）"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsHand = [Trig_ForgeUpgrade(self, LivingSeedRank3, 10)]  #只有在手牌中才会升级
	
	def entersHand(self):
		card = LivingSeedRank3(self.Game, self.ID) if self.Game.Manas.manasUpper[self.ID] > 9 else self
		card.inHand = True
		card.onBoard = card.inDeck = False
		card.enterHandTurn = card.Game.numTurn
		for trig in card.trigsHand: trig.connect()
		return card
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		beasts = [i for i, card in enumerate(self.Game.Hand_Deck.decks[self.ID]) if card.type == "Minion" and "Beast" in card.race]
		if beasts:
			beast = self.Game.Hand_Deck.drawCard(self.ID, npchoice(beasts))[0]
			if beast: ManaMod(beast, changeby=-2).applies()
		return None
		
class LivingSeedRank3(Spell):
	Class, school, name = "Druid", "Nature", "Living Seed (Rank 3)"
	requireTarget, mana = False, 2
	index = "THE_BARRENS~Druid~Spell~2~Nature~Living Seed (Rank 3)~Uncollectible"
	description = "Draw a Beast. Reduce its Cost by (3)"
	name_CN = "生命之种（等级3）"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		beasts = [i for i, card in enumerate(self.Game.Hand_Deck.decks[self.ID]) if card.type == "Minion" and "Beast" in card.race]
		if beasts:
			beast = self.Game.Hand_Deck.drawCard(self.ID, npchoice(beasts))[0]
			if beast: ManaMod(beast, changeby=-3).applies()
		return None


class MarkoftheSpikeshell(Spell):
	Class, school, name = "Druid", "Nature", "Mark of the Spikeshell"
	requireTarget, mana = True, 2
	index = "THE_BARRENS~Druid~Spell~2~Nature~Mark of the Spikeshell"
	description = "Give a minion +2/+2. If it has Taunt, add a copy of it to your hand"
	name_CN = "尖壳印记"
	def available(self):
		return self.selectableMinionExists()
	
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			target.buffDebuff(2, 2)  #buffDebuff() and getsStatus() will check if the minion is onBoard or inHand.
			if target.keyWords["Taunt"] > 0:
				self.addCardtoHand(target.selfCopy(self.ID, self), self.ID)
		return target


class RazormaneBattleguard(Minion):
	Class, race, name = "Druid", "Quilboar", "Razormane Battleguard"
	mana, attack, health = 2, 2, 3
	index = "THE_BARRENS~Druid~Minion~2~2~3~Quilboar~Razormane Battleguard"
	requireTarget, keyWord, description = False, "", "The first Taunt minion your play each turn costs (2) less"
	name_CN = "钢鬃卫兵"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.auras["The first Taunt minion you play each turn costs (1)"] = ManaAura_1stTaunt2Less(self)

class GameManaAura_InTurn1stTaunt2Less(TempManaEffect):
	def __init__(self, Game, ID):
		super().__init__(Game, ID, 0, 1)
	
	def applicable(self, target):
		return target.ID == self.ID and target.type == "Minion" and target.keyWords["Taunt"] > 0

class ManaAura_1stTaunt2Less(ManaAura_1UsageEachTurn):
	def auraAppears(self):
		game, ID = self.entity.Game, self.entity.ID
		if game.turn == ID and not any(card.index.endswith("~Taunt") for card in game.Counters.cardsPlayedEachTurn[ID][-1]):
			self.aura = GameManaAura_InTurn1stTaunt2Less(game, ID)
			game.Manas.CardAuras.append(self.aura)
			self.aura.auraAppears()
		try: game.trigsBoard[ID]["TurnStarts"].append(self)
		except: game.trigsBoard[ID]["TurnStarts"] = [self]


class ThorngrowthSentries(Spell):
	Class, school, name = "Druid", "Nature", "Thorngrowth Sentries"
	requireTarget, mana = False, 2
	index = "THE_BARRENS~Druid~Spell~2~Nature~Thorngrowth Sentries"
	description = "Summon two 1/2 Turtles with Taunt"
	name_CN = "荆棘护卫"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.summon([ThornguardTurtle(self.Game, self.ID) for i in range(2)], (-1, "totheRightEnd"))
		return None

class ThornguardTurtle(Minion):
	Class, race, name = "Druid", "Beast", "Thornguard Turtle"
	mana, attack, health = 1, 1, 2
	index = "THE_BARRENS~Druid~Minion~1~1~2~Beast~Thornguard Turtle~Taunt~Uncollectible"
	requireTarget, keyWord, description = False, "Taunt", "Taunt"
	name_CN = "棘甲龟"


class GuffRunetotem(Minion):
	Class, race, name = "Druid", "", "Guff Runetotem"
	mana, attack, health = 3, 2, 4
	index = "THE_BARRENS~Druid~Minion~3~2~4~~Guff Runetotem~Legendary"
	requireTarget, keyWord, description = False, "", "After you cast a Nature spell, give another friendly minion +2/+2"
	name_CN = "古夫·符文图腾"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_GuffRunetotem(self)]

class Trig_GuffRunetotem(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["SpellBeenPlayed"])
	
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject.ID == self.entity.ID and subject.school == "Nature"
	
	def text(self, CHN):
		return "在你施放一个自然法术后，使另一个友方随从获得+2/+2" if CHN else "After you cast a Nature spell, give another friendly minion +2/+2"
	
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		minions = self.entity.Game.minionsonBoard(self.entity.ID, self.entity)
		if minions: npchoice(minions).buffDebuff(2, 2)
		

class PlaguemawtheRotting(Minion):
	Class, race, name = "Druid", "Quilboar", "Plaguemaw the Rotting"
	mana, attack, health = 4, 3, 4
	index = "THE_BARRENS~Druid~Minion~4~3~4~Quilboar~Plaguemaw the Rotting~Legendary"
	requireTarget, keyWord, description = False, "", "After a friendly Taunt minion dies, summon a new copy of it with Taunt"
	name_CN = "腐烂的普雷莫尔"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_PlaguemawtheRotting(self)]

class Trig_PlaguemawtheRotting(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["MinionDied"])
	
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and target != self.entity and target.ID == self.entity.ID and target.keyWords["Taunt"] > 0#Technically, minion has to disappear before dies. But just in case.
	
	def text(self, CHN):
		return "在一个友方嘲讽随从死亡后，召唤一个它的不具有嘲讽的新的复制" if CHN else "After a friendly Taunt minion dies, summon a new copy of it with Taunt"
	
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		minion = self.entity
		Copy = type(target)(minion.Game, minion.ID)
		Copy.keyWords["Taunt"] = 0
		minion.summon(Copy, minion.pos+1)


class PridesFury(Spell):
	Class, school, name = "Druid", "", "Pride's Fury"
	requireTarget, mana = False, 4
	index = "THE_BARRENS~Druid~Spell~4~~Pride's Fury"
	description = "Give your minions +1/+3"
	name_CN = "狮群之怒"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		for minion in self.Game.minionsonBoard(self.ID):
			minion.buffDebuff(1, 3)
		return None


class ThickhideKodo(Minion):
	Class, race, name = "Druid", "Beast", "Thickhide Kodo"
	mana, attack, health = 4, 3, 5
	index = "THE_BARRENS~Druid~Minion~4~3~5~Beast~Thickhide Kodo~Taunt~Deathrattle"
	requireTarget, keyWord, description = False, "Taunt", "Taunt. Deathrattle: Gain 5 Armor"
	name_CN = "厚皮科多兽"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.deathrattles = [Gain5Armor(self)]

class Gain5Armor(Deathrattle_Minion):
	def text(self, CHN):
		return "亡语：获得5点护甲值" if CHN else "Deathrattle: Gain 5 Armor"
	
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.Game.heroes[self.entity.ID].gainsArmor(5)


class CelestialAlignment(Spell):
	Class, school, name = "Druid", "Arcane", "Celestial Alignment"
	requireTarget, mana = False, 7
	index = "THE_BARRENS~Druid~Spell~7~Arcane~Celestial Alignment"
	description = "Set each player to 0 Mana Crystals. Set the Cost of cards in all hands and decks to (1)"
	name_CN = "超凡之盟"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		for ID in range(1, 3):
			self.Game.Manas.setManaCrystal(0, ID)
			for card in self.Game.Hand_Deck.hands[ID]:
				ManaMod(card, changeby=0, changeto=1).applies()
			for card in self.Game.Hand_Deck.decks[ID]:
				ManaMod(card, changeby=0, changeto=1).applies()
		return None


class DruidofthePlains(Minion):
	Class, race, name = "Druid", "Beast", "Druid of the Plains"
	mana, attack, health = 7, 7, 6
	index = "THE_BARRENS~Druid~Minion~7~7~6~Beast~Druid of the Plains~Rush~Frenzy"
	requireTarget, keyWord, description = False, "Rush", "Rush. Frenzy: Transform into a 6/7 Kodo with Taunt"
	name_CN = "平原德鲁伊"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_DruidofthePlains(self)]
		
class Trig_DruidofthePlains(Frenzy):
	def text(self, CHN):
		return "暴怒：变形成一只6/7并具有嘲讽的科多兽" if CHN else "Frenzy: Transform into a 6/7 Kodo with Taunt"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.transform(self.entity, DruidofthePlains_Taunt(self.entity.Game, self.entity.ID))
		
class DruidofthePlains_Taunt(Minion):
	Class, race, name = "Druid", "Beast", "Druid of the Plains"
	mana, attack, health = 7, 6, 6
	index = "THE_BARRENS~Druid~Minion~7~6~7~Beast~Druid of the Plains~Taunt~Uncollectible"
	requireTarget, keyWord, description = False, "Taunt", "Taunt"
	name_CN = "平原德鲁伊"
	
	
"""Hunter Cards"""
class SunscaleRaptor(Minion):
	Class, race, name = "Hunter", "Beast", "Sunscale Raptor"
	mana, attack, health = 1, 1, 3
	index = "THE_BARRENS~Hunter~Minion~1~1~3~Beast~Sunscale Raptor~Frenzy"
	requireTarget, keyWord, description = False, "", "Frenzy: Shuffle a Sunscale Raptor into your deck with permanent +2/+1"
	name_CN = "赤鳞迅猛龙"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_SunscaleRaptor(self)]
		
class Trig_SunscaleRaptor(Frenzy):
	def text(self, CHN):
		return "暴怒：将一张赤鳞迅猛龙洗入你的牌库并使其永久获得+2/+1" if CHN \
				else "Frenzy: Shuffle a Sunscale Raptor into your deck with permanent +1/+1"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		game = self.entity.Game
		if self.entity.onBoard: newAtt, newHealth = self.entity.attack + 2, self.entity.health + 1
		else: newAtt, newHealth = self.entity.attack_0 + 2, self.entity.health_0 + 1
		newIndex = "THE_BARRENS~Hunter~Minion~1~%d~%d~Beast~Sunscale Raptor~Uncollectible"%(newAtt, newHealth)
		subclass = type("SunscaleRaptor__%d_%d"%(newAtt, newHealth), (SunscaleRaptor, ),
						{"attack": newAtt, "health": newHealth, "index": newIndex}
						)
		game.Hand_Deck.shuffleintoDeck(subclass(game, self.entity.ID), creator=self.entity)
		
		
class WoundPrey(Spell):
	Class, school, name = "Hunter", "", "Wound Prey"
	requireTarget, mana = True, 1
	index = "THE_BARRENS~Hunter~Spell~1~~Wound Prey"
	description = "Deal 1 damage. Summon a 1/1 Hyena with Rush"
	name_CN = "击伤猎物"
	
	def text(self, CHN):
		damage = (1 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		return "造成%d点伤害。召唤一个1/1并具有突袭的土狼" % damage if CHN \
			else "Deal %d damage. Summon a 1/1 Hyena with Rush" % damage
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		damage = (1 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		self.dealsDamage(target, damage)
		self.summon(SwiftHyena(self.Game, self.ID), -1)
		return target

class SwiftHyena(Minion):
	Class, race, name = "Hunter", "Beast", "Swift Hyena"
	mana, attack, health = 1, 1, 1
	index = "THE_BARRENS~Hunter~Minion~1~1~1~Beast~Swift Hyena~Rush~Uncollectible"
	requireTarget, keyWord, description = False, "Rush", "Rush"
	name_CN = "迅捷土狼"


class KolkarPackRunner(Minion):
	Class, race, name = "Hunter", "", "Kolkar Pack Runner"
	mana, attack, health = 3, 3, 4
	index = "THE_BARRENS~Hunter~Minion~3~3~4~~Kolkar Pack Runner"
	requireTarget, keyWord, description = False, "", "After you cast a spell, summon a 1/1 Hyena with Rush"
	name_CN = "科卡尔驯犬者"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_KolkarPackRunner(self)]

class Trig_KolkarPackRunner(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["SpellBeenPlayed"])
	
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject.ID == self.entity.ID
	
	def text(self, CHN):
		return "在你施放一个法术后，对所有随从造成1点伤害" if CHN else "After you cast a spell, deal 1 damage to ALL minions"
	
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		minion = self.entity
		minion.summon(SwiftHyena(minion.Game, minion.ID), minion.pos+1)


class ProspectorsCaravan(Minion):
	Class, race, name = "Hunter", "", "Prospector's Caravan"
	mana, attack, health = 2, 1, 3
	index = "THE_BARRENS~Hunter~Minion~2~1~3~~Prospector's Caravan"
	requireTarget, keyWord, description = False, "", "At the start of your turn, give all minions in your hand +1/+1"
	name_CN = "勘探者车队"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_ProspectorsCaravan(self)]

class Trig_ProspectorsCaravan(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["TurnStarts"])
	
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and ID == self.entity.ID
	
	def text(self, CHN):
		return "在你的回合开始时，使你的手牌中的所有随从牌获得+1/+1" if CHN \
			else "At the start of your turn, give all minions in your hand +1/+1"
	
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		for card in self.entity.Game.Hand_Deck.hands[self.entity.ID]:
			if card.type == "Minion":
				card.buffDebuff(1, 1)


class TameBeastRank1(Spell):
	Class, school, name = "Hunter", "", "Tame Beast (Rank 1)"
	requireTarget, mana = False, 2
	index = "THE_BARRENS~Hunter~Spell~2~~Tame Beast (Rank 1)"
	description = "Summon a 2/2 Beast with Rush. (Upgrades when you have 5 mana.)"
	name_CN = "驯服野兽（等级1）"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsHand = [Trig_ForgeUpgrade(self, TameBeastRank2, 5)]  #只有在手牌中才会升级
	
	def entersHand(self):
		card = TameBeastRank2(self.Game, self.ID) if self.Game.Manas.manasUpper[self.ID] > 4 else self
		card.inHand = True
		card.onBoard = card.inDeck = False
		card.enterHandTurn = card.Game.numTurn
		for trig in card.trigsHand: trig.connect()
		return card
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		self.summon(TamedCrab(self.Game, self.ID), -1)
		return None

class TameBeastRank2(Spell):
	Class, school, name = "Hunter", "", "Tame Beast (Rank 2)"
	requireTarget, mana = False, 2
	index = "THE_BARRENS~Hunter~Spell~2~~Tame Beast (Rank 2)~Uncollectible"
	description = "Summon a 4/4 Beast with Rush. (Upgrades when you have 10 mana.)"
	name_CN = "驯服野兽（等级2）"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsHand = [Trig_ForgeUpgrade(self, TameBeastRank3, 10)]  #只有在手牌中才会升级
	
	def entersHand(self):
		card = TameBeastRank3(self.Game, self.ID) if self.Game.Manas.manasUpper[self.ID] > 9 else self
		card.inHand = True
		card.onBoard = card.inDeck = False
		card.enterHandTurn = card.Game.numTurn
		for trig in card.trigsHand: trig.connect()
		return card
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		self.summon(TamedScorpid(self.Game, self.ID), -1)
		return None

class TameBeastRank3(Spell):
	Class, school, name = "Hunter", "", "Tame Beast (Rank 3)"
	requireTarget, mana = False, 2
	index = "THE_BARRENS~Hunter~Spell~2~~Tame Beast (Rank 3)~Uncollectible"
	description = "Summon a 6/6 Beast with Rush"
	name_CN = "驯服野兽（等级3）"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		self.summon(TamedThunderLizard(self.Game, self.ID), -1)
		return None

class TamedCrab(Minion):
	Class, race, name = "Hunter", "Beast", "Tamed Crab"
	mana, attack, health = 2, 2, 2
	index = "THE_BARRENS~Hunter~Minion~2~2~2~Beast~Tamed Crab~Rush~Uncollectible"
	requireTarget, keyWord, description = False, "Rush", "Rush"
	name_CN = "驯服的螃蟹"

class TamedScorpid(Minion):
	Class, race, name = "Hunter", "Beast", "Tamed Scorpid"
	mana, attack, health = 4, 4, 4
	index = "THE_BARRENS~Hunter~Minion~4~4~4~Beast~Tamed Scorpid~Rush~Uncollectible"
	requireTarget, keyWord, description = False, "Rush", "Rush"
	name_CN = "驯服的蝎子"

class TamedThunderLizard(Minion):
	Class, race, name = "Hunter", "Beast", "Tamed Thunder Lizard"
	mana, attack, health = 6, 6, 6
	index = "THE_BARRENS~Hunter~Minion~6~6~6~Beast~Tamed Thunder Lizard~Rush~Uncollectible"
	requireTarget, keyWord, description = False, "Rush", "Rush"
	name_CN = "驯服的雷霆蜥蜴"


class PackKodo(Minion):
	Class, race, name = "Hunter", "Beast", "Pack Kodo"
	mana, attack, health = 3, 3, 3
	index = "THE_BARRENS~Hunter~Minion~3~3~3~Beast~Pack Kodo~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Discove a Beast, Secret, or weapon"
	name_CN = "载货科多兽"
	poolIdentifier = "Beasts as Druid"
	@classmethod
	def generatePool(cls, pools):
		Classes, ls_Pools = [], []
		neutralBeasts, neutralWeapons = [], []
		for card in pools.NeutralCards:
			if card.type == "Weapon": neutralWeapons.append(card)
			elif "Beast" in card.race: neutralBeasts.append(card)
		for Class in pools.Classes:
			beasts, secrets, weapons = [], [], []
			for card in pools.ClassCards[Class]:
				if card.type == "Minion" and "Beast" in card.race: beasts.append(card)
				elif card.description.startswith("Secret:"): secrets.append(card)
				elif card.type == "Weapon": weapons.append(card)
			beasts.extend(neutralBeasts)
			weapons.extend(neutralWeapons)
			Classes.append("Beasts as "+Class)
			Classes.append(Class+" Secrets")
			Classes.append("Weapons as "+Class)
			ls_Pools.extend(beasts)
			ls_Pools.extend(secrets)
			ls_Pools.extend(weapons)
		return Classes, ls_Pools
	
	def decideSecretPool(self):
		HeroClass = self.Game.heroes[self.ID].Class
		key = HeroClass + " Secrets" if HeroClass in ["Hunter", "Mage", "Paladin", "Rogue"] else "Mage Secrets"
		return self.rngPool(key)
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.discoverandGenerate_MultiplePools(PackKodo, comment,
											   poolFuncs=[lambda : self.rngPool("Beasts as " + classforDiscover(self)),
														lambda : PackKodo.decideSecretPool(self),
														lambda : self.rngPool("Weapons as " + classforDiscover(self))])
		return None
	

class TavishStormpike(Minion):
	Class, race, name = "Hunter", "", "Tavish Stormpike"
	mana, attack, health = 3, 2, 5
	index = "THE_BARRENS~Hunter~Minion~3~2~5~~Tavish Stormpike~Legendary"
	requireTarget, keyWord, description = False, "", "After a friendly Beast attacks, summon a Beast from your deck that costs (1) less"
	name_CN = "塔维什·雷矛"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_TavishStormpike(self)]

class Trig_TavishStormpike(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["MinionAttackedHero", "MinionAttackedMinion"])
	
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject.ID == self.entity.ID and "Beast" in subject.race
	
	def text(self, CHN):
		return "在一个友方野兽攻击后，从你的牌库召唤一个法力值消耗减少（1）点的野兽" if CHN \
				else "After a friendly Beast attacks, summon a Beast from your deck that costs (1) less"
	
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		minion = self.entity
		beasts = [i for i, card in enumerate(minion.Game.Hand_Deck.decks[ID]) \
						  	if card.type == "Minion" and "Beast" in card.race and card.mana == subject.mana - 1]
		if beasts and minion.Game.space(minion.ID):
			minion.Game.summonfrom(npchoice(beasts), minion.ID, minion.pos + 1, self, source='D')
		

class PiercingShot(Spell):
	Class, school, name = "Hunter", "", "Piercing Shot"
	requireTarget, mana = True, 4
	index = "THE_BARRENS~Hunter~Spell~4~~Piercing Shot"
	description = "Deal 6 damage to a minion. Excess damage hits the enemy hero"
	name_CN = "穿刺射击"
	def available(self):
		return self.selectableMinionExists()
	
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
	
	def text(self, CHN):
		damage = (6 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		return "对一个随从造成%d点伤害。超过目标生命值的伤害会命中敌方英雄" % damage if CHN \
				else "Deal %d damage to a minion. Excess damage hits the enemy hero" % damage
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if target:
			totalDamage = (6 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			realDamage = max(target.health, 0)
			excessDamage = totalDamage - realDamage
			self.dealsDamage(target, realDamage)
			if excessDamage > 0: self.dealsDamage(self.Game.heroes[3-self.ID], excessDamage)
		return target


class WarsongWrangler(Minion):
	Class, race, name = "Hunter", "", "Warsong Wrangler"
	mana, attack, health = 4, 3, 4
	index = "THE_BARRENS~Hunter~Minion~4~3~4~~Warsong Wrangler~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Discover a Beast in your deck. Give all copies of it +2/+1 (wherever they are)"
	name_CN = "战歌驯兽师"
	
	def drawBeastandBuffAllCopies(self, i, beast):
		beast = self.Game.Hand_Deck.decks[self.ID][i]
		cardType = type(beast)
		self.Game.Hand_Deck.drawCard(self.ID, i)
		for minion in self.Game.minionsonBoard(self.ID):
			if isinstance(minion, cardType):
				minion.buffDebuff(2, 1)
		for card in self.Game.Hand_Deck.hands[self.ID]:
			if isinstance(card, cardType):
				card.buffDebuff(2, 1)
		for card in self.Game.Hand_Deck.decks[self.ID]:
			if isinstance(card, cardType):
				card.attack += 2
				card.attack_Enchant += 2
				card.health += 1
				card.health_max += 1
				
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.discoverfromList(WarsongWrangler, comment, lambda card: "Beast" in card.race)
		return None
	
	def discoverDecided(self, option, case, info_RNGSync=None, info_GUISync=None):
		self.handleDiscoveredCardfromList(option, case, ls=self.Game.Hand_Deck.decks[self.ID],
										  func=lambda index, card: WarsongWrangler.drawBeastandBuffAllCopies(self, index, card),
										  info_RNGSync=info_RNGSync, info_GUISync=info_GUISync)
		

class BarakKodobane(Minion):
	Class, race, name = "Hunter", "", "Barak Kodobane"
	mana, attack, health = 5, 3, 5
	index = "THE_BARRENS~Hunter~Minion~5~3~5~~Barak Kodobane~Battlecry~Legendary"
	requireTarget, keyWord, description = False, "", "Battlecry: Draw a 1, 2, and 3-Cost spell"
	name_CN = "巴拉克·科多班恩"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		ownDeck = self.Game.Hand_Deck.decks[self.ID]
		for cost in range(1, 4):
			spells = [i for i, card in enumerate(ownDeck) if card.type == "Spell" and card.mana == cost]
			if spells: self.Game.Hand_Deck.drawCard(self.ID, npchoice(ownDeck))
		return None


"""Mage Cards"""
class FlurryRank1(Spell):
	Class, school, name = "Mage", "Frost", "Flurry (Rank 1)"
	requireTarget, mana = False, 0
	index = "THE_BARRENS~Mage~Spell~0~Frost~Flurry (Rank 1)"
	description = "Freeze a random enemy minion. (Upgrades when you have 5 mana.)"
	name_CN = "冰风暴（等级1）"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsHand = [Trig_ForgeUpgrade(self, FlurryRank2, 5)]  #只有在手牌中才会升级
	
	def entersHand(self):
		card = FlurryRank2(self.Game, self.ID) if self.Game.Manas.manasUpper[self.ID] > 4 else self
		card.inHand = True
		card.onBoard = card.inDeck = False
		card.enterHandTurn = card.Game.numTurn
		for trig in card.trigsHand: trig.connect()
		return card
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		minions = self.Game.minionsonBoard(3-self.ID)
		if minions: npchoice(minions).getsStatus("Frozen")
		return None

class FlurryRank2(Spell):
	Class, school, name = "Mage", "Frost", "Flurry (Rank 2)"
	requireTarget, mana = False, 0
	index = "THE_BARRENS~Mage~Spell~0~Frost~Flurry (Rank 2)~Uncollectible"
	description = "Freeze two random enemy minions. (Upgrades when you have 10 mana.)"
	name_CN = "冰风暴（等级2）"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsHand = [Trig_ForgeUpgrade(self, FlurryRank3, 10)]  #只有在手牌中才会升级
	
	def entersHand(self):
		card = FlurryRank3(self.Game, self.ID) if self.Game.Manas.manasUpper[self.ID] > 9 else self
		card.inHand = True
		card.onBoard = card.inDeck = False
		card.enterHandTurn = card.Game.numTurn
		for trig in card.trigsHand: trig.connect()
		return card
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		minions = self.Game.minionsonBoard(3-self.ID)
		minions = npchoice(minions, min(2, len(minions)), replace=False)
		for minion in minions: minion.getsStatus("Frozen")
		return None

class FlurryRank3(Spell):
	Class, school, name = "Mage", "Frost", "Flurry (Rank 3)"
	requireTarget, mana = False, 0
	index = "THE_BARRENS~Mage~Spell~0~Frost~Flurry (Rank 3)~Uncollectible"
	description = "Freeze three random enemy minions"
	name_CN = "冰风暴（等级3）"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		minions = self.Game.minionsonBoard(3 - self.ID)
		minions = npchoice(minions, min(3, len(minions)), replace=False)
		for minion in minions: minion.getsStatus("Frozen")
		return None


class RunedOrb(Spell):
	Class, school, name = "Mage", "Arcane", "Runed Orb"
	requireTarget, mana = True, 2
	index = "THE_BARRENS~Mage~Spell~2~Arcane~Runed Orb"
	description = "Deal 2 damage. Discover a Spell"
	name_CN = "符文宝珠"
	poolIdentifier = "Mage Spells"
	@classmethod
	def generatePool(cls, pools):
		return [Class + " Spells" for Class in pools.Classes], \
			   [[card for card in cards if card.type == "Spell"] for cards in pools.ClassCards.values()]
	
	def text(self, CHN):
		damage = (2 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		return "对一个随从造成%d点伤害。发现一张法术牌" % damage if CHN \
			else "Deal %d damage to a minion. Discover a Spell" % damage
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if target:
			damage = (2 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			self.dealsDamage(target, damage)
			self.discoverandGenerate(RunedOrb, comment, lambda : self.rngPool(classforDiscover(self) + " Spells"))
		return target
	

class Wildfire(Spell):
	Class, school, name = "Mage", "Fire", "Wildfire"
	requireTarget, mana = False, 2
	index = "THE_BARRENS~Mage~Spell~2~Fire~Wildfire"
	description = "Increase the damage of your Hero Power by 1"
	name_CN = "野火"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.Game.powers[self.ID].marks["Damage Boost"] += 1
		return None


class ArcaneLuminary(Minion):
	Class, race, name = "Mage", "Elemental", "Arcane Luminary"
	mana, attack, health = 3, 4, 3
	index = "THE_BARRENS~Mage~Minion~3~4~3~Elemental~Arcane Luminary"
	requireTarget, keyWord, description = False, "", "Cards that didn't start in your deck cost (2) less, but not less than (1)"
	name_CN = "奥术发光体"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.auras["Cards that didn't start in your deck cost (2) less, but not less than (1)"] = ManaAura(self, changeby=-2, changeto=-1, lowerbound=1)
	
	def manaAuraApplicable(self, subject):  #ID用于判定是否是我方手中的随从
		return subject.ID == self.ID and subject.creator


class OasisAlly(Secret):
	Class, school, name = "Mage", "Frost", "Oasis Ally"
	requireTarget, mana = False, 3
	index = "THE_BARRENS~Mage~Spell~3~Frost~Oasis Ally~~Secret"
	description = "Secret: When a friendly minion is attacked, summon a 3/6 Water Elemental"
	name_CN = "绿洲盟军"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_OasisAlly(self)]

class Trig_OasisAlly(SecretTrigger):
	def __init__(self, entity):
		super().__init__(entity, ["MinionAttacksMinion", "HeroAttacksMinion"])
	
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):  #target here holds the actual target object
		#The target has to a friendly minion and there is space on board to summon minions.
		return self.entity.ID != self.entity.Game.turn and target[0].type == "Minion" and target[0].ID == self.entity.ID and self.entity.Game.space(self.entity.ID) > 0
	
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.summon(WaterElemental_Basic(self.entity.Game, self.entity.ID), -1)


class Rimetongue(Minion):
	Class, race, name = "Mage", "", "Rimetongue"
	mana, attack, health = 3, 3, 4
	index = "THE_BARRENS~Mage~Minion~3~3~4~~Rimetongue"
	requireTarget, keyWord, description = False, "", "After you cast a Frost spell, summon a 1/1 Elemental that Freezes"
	name_CN = "霜舌半人马"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_Rimetongue(self)]

class Trig_Rimetongue(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["SpellBeenPlayed"])
	
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject.ID == self.entity.ID and subject.school == "Frost"
	
	def text(self, CHN):
		return "在你施放一个冰霜法术后，召唤一个1/1的可以冻结攻击目标的元素" if CHN else "After you cast a Frost spell, summon a 1/1 Elemental that Freezes"
	
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.summon(FrostedElemental(self.entity.Game, self.entity.ID), self.entity.pos+1)

class FrostedElemental(Minion):
	Class, race, name = "Mage", "Elemental", "Frosted Elemental"
	mana, attack, health = 1, 1, 1
	index = "THE_BARRENS~Mage~Minion~1~1~1~Elemental~Frosted Elemental~Uncollectible"
	requireTarget, keyWord, description = False, "", "Freeze any character damaged by this minion"
	name_CN = "霜冻元素"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_FrostedElemental(self)]

class Trig_FrostedElemental(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["MinionTakesDmg", "HeroTakesDmg"])
	
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject == self.entity
	
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		target.getsStatus("Frozen")
	
	def text(self, CHN):
		return "冻结任何受到该随从伤害的角色" if CHN else "Freeze any character damaged by this minion"


class RecklessApprentice(Minion):
	Class, race, name = "Mage", "", "Reckless Apprentice"
	mana, attack, health = 4, 3, 5
	index = "THE_BARRENS~Mage~Minion~4~3~5~~Reckless Apprentice~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Fire your Hero Power at all enemies"
	name_CN = "鲁莽的学徒"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		#假设只有指向性的英雄技能才能触发，同时目标需要符合条件
		power = self.Game.powers[self.ID]
		if power.needTarget():
			for char in self.Game.minionsonBoard(3 - self.ID) + [self.Game.heroes[3 - self.ID]]:
				if power.targetCorrect(char):
					power.effect(target)
		else:
			for char in self.Game.minionsonBoard(3 - self.ID) + [self.Game.heroes[3 - self.ID]]:
				power.effect()
		return None


class RefreshingSpringWater(Spell):
	Class, school, name = "Mage", "", "Refreshing Spring Water"
	requireTarget, mana = False, 5
	index = "THE_BARRENS~Mage~Spell~5~~Refreshing Spring Water"
	description = "Draw 2 cards. Refresh 2 Mana Crystals for each spell drawn"
	name_CN = "清凉的泉水"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		card1 = self.Game.Hand_Deck.drawCard(self.ID)[0]
		card2 = self.Game.Hand_Deck.drawCard(self.ID)[0]
		num = 0
		if card1 and card1.type == "Spell": num += 2
		if card2 and card2.type == "Spell": num += 2
		if num > 0:
			self.Game.Manas.restoreManaCrystal(num, self.ID)
		return None


class VardenDawngrasp(Minion):
	Class, race, name = "Mage", "", "Varden Dawngrasp"
	mana, attack, health = 4, 3, 3
	index = "THE_BARRENS~Mage~Minion~4~3~3~~Varden Dawngrasp~Battlecry~Legendary"
	requireTarget, keyWord, description = False, "", "Battlecry: Freeze all enemy minions. If any are already Frozen, deal 4 damage to them instead"
	name_CN = "瓦尔登·晨拥"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		targets_Freeze, targets_Damage = [], []
		for minion in self.Game.minionsonBoard(3-self.ID):
			if minion.status["Frozen"] < 1: targets_Freeze.append(minion)
			else: targets_Damage.append(minion)
		for minion in targets_Freeze: minion.getsStatus("Frozen")
		if targets_Damage:
			self.dealsAOE(targets_Damage, [4]*len(targets_Damage))
		return None


class MordreshFireEye(Minion):
	Class, race, name = "Mage", "", "Mordresh Fire Eye"
	mana, attack, health = 10, 10, 10
	index = "THE_BARRENS~Mage~Minion~10~10~10~~Mordresh Fire Eye~Battlecry~Legendary"
	requireTarget, keyWord, description = False, "", "Battlecry: If you've dealt 10 damage with your hero power this game, deal 10 damage to all enemies"
	name_CN = "火眼莫德雷斯"
	
	def effCanTrig(self):
		self.effectViable = self.Game.Counters.damageDealtbyHeroPower[self.ID] > 9
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if self.Game.Counters.damageDealtbyHeroPower[self.ID] > 9:
			targets = self.Game.minionsonBoard(3-self.ID) + [self.Game.heroes[3-self.ID]]
			self.dealsAOE(targets, [10] * len(targets))
		return None


"""Paladin Cards"""
class ConvictionRank1(Spell):
	Class, school, name = "Paladin", "Holy", "Conviction (Rank 1)"
	requireTarget, mana = False, 2
	index = "THE_BARRENS~Paladin~Spell~2~Holy~Conviction (Rank 1)"
	description = "Give a random friendly minion +3 Attack. (Upgrades when you have 5 mana.)"
	name_CN = "定罪（等级1）"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsHand = [Trig_ForgeUpgrade(self, ConvictionRank2, 5)]  #只有在手牌中才会升级
	
	def entersHand(self):
		card = ConvictionRank2(self.Game, self.ID) if self.Game.Manas.manasUpper[self.ID] > 4 else self
		card.inHand = True
		card.onBoard = card.inDeck = False
		card.enterHandTurn = card.Game.numTurn
		for trig in card.trigsHand: trig.connect()
		return card
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		minions = self.Game.minionsonBoard(self.ID)
		if minions: npchoice(minions).buffDebuff(3, 0)
		return None

class ConvictionRank2(Spell):
	Class, school, name = "Paladin", "Holy", "Conviction (Rank 2)"
	requireTarget, mana = False, 2
	index = "THE_BARRENS~Paladin~Spell~2~Holy~Conviction (Rank 2)~Uncollectible"
	description = "Give two random friendly minions +3 Attack. (Upgrades when you have 10 mana.)"
	name_CN = "定罪（等级2）"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsHand = [Trig_ForgeUpgrade(self, ConvictionRank3, 10)]  #只有在手牌中才会升级
	
	def entersHand(self):
		card = ConvictionRank3(self.Game, self.ID) if self.Game.Manas.manasUpper[self.ID] > 9 else self
		card.inHand = True
		card.onBoard = card.inDeck = False
		card.enterHandTurn = card.Game.numTurn
		for trig in card.trigsHand: trig.connect()
		return card
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		minions = self.Game.minionsonBoard(self.ID)
		minions = npchoice(minions, min(2, len(minions)), replace=False)
		for minion in minions: minion.buffDebuff(3, 0)
		return None

class ConvictionRank3(Spell):
	Class, school, name = "Paladin", "Holy", "Conviction (Rank 3)"
	requireTarget, mana = False, 2
	index = "THE_BARRENS~Paladin~Spell~2~Holy~Conviction (Rank 3)~Uncollectible"
	description = "Give three random friendly minions +3 Attack"
	name_CN = "定罪（等级3）"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		minions = self.Game.minionsonBoard(self.ID)
		minions = npchoice(minions, min(3, len(minions)), replace=False)
		for minion in minions: minion.buffDebuff(3, 0)
		return None


class GallopingSavior(Secret):
	Class, school, name = "Paladin", "", "Galloping Savior"
	requireTarget, mana = False, 1
	index = "THE_BARRENS~Paladin~Spell~1~~Galloping Savior~~Secret"
	description = "Secret: After your opponent plays three cards in a turn, summon a 3/4 Steed with Taunt"
	name_CN = "迅疾救兵"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_GallopingSavior(self)]

class Trig_GallopingSavior(SecretTrigger):
	def __init__(self, entity):
		super().__init__(entity, ["MinionBeenPlayed", "SpellBeenPlayed", "WeaponBeenPlayed", "HeroBeenPlayed"])
	
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		secret = self.entity
		return secret.ID != secret.Game.turn and subject.ID != secret.ID \
			   and len(secret.Game.Counters.cardsPlayedEachTurn[subject.ID][-1]) > 2 \
				and secret.Game.space(secret.ID)
	
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.summon(HolySteed(self.entity.Game, self.entity.ID), -1)

class HolySteed(Minion):
	Class, race, name = "Paladin", "Beast", "Holy Steed"
	mana, attack, health = 3, 3, 4
	index = "THE_BARRENS~Paladin~Minion~3~3~4~Beast~Holy Steed~Taunt~Uncollectible"
	requireTarget, keyWord, description = False, "Taunt", "Taunt"
	name_CN = "神圣战马"


class KnightofAnointment(Minion):
	Class, race, name = "Paladin", "", "Knight of Anointment"
	mana, attack, health = 1, 1, 1
	index = "THE_BARRENS~Paladin~Minion~1~1~1~~Knight of Anointment~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Draw a Holy spell"
	name_CN = "圣礼骑士"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		spells = [i for i, card in enumerate(self.Game.Hand_Deck.decks[self.ID]) if card.type == "Spell" and card.school == "Holy"]
		if spells: self.Game.Hand_Deck.drawCard(self.ID, npchoice(spells))
		return None


class SoldiersCaravan(Minion):
	Class, race, name = "Paladin", "", "Soldier's Caravan"
	mana, attack, health = 2, 1, 3
	index = "THE_BARRENS~Paladin~Minion~2~1~3~~Soldier's Caravan"
	requireTarget, keyWord, description = False, "", "At the start of your turn, summon two 1/1 Silver Hand Recruits"
	name_CN = "士兵车队"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_SoldiersCaravan(self)]

class Trig_SoldiersCaravan(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["TurnStarts"])
	
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and ID == self.entity.ID
	
	def text(self, CHN):
		return "在你的回合开始时，召唤两个1/1的白银之手新兵" if CHN else "At the start of your turn, summon two 1/1 Silver Hand Recruits"
	
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		minion = self.entity
		minion.summon([SilverHandRecruit(minion.Game, minion.ID) for i in range(2)], (minion.pos, "leftandRight"))


class SwordoftheFallen(Weapon):
	Class, name, description = "Paladin", "Sword of the Fallen", "After your hero attack, cast a Secret from your deck"
	mana, attack, durability = 2, 1, 3
	index = "THE_BARRENS~Paladin~Weapon~2~1~3~Sword of the Fallen"
	name_CN = "逝者之剑"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_SwordoftheFallen(self)]

class Trig_SwordoftheFallen(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["HeroAttackedMinion", "HeroAttackedHero"])
	
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject == self.entity.Game.heroes[self.entity.ID] and self.entity.onBoard
	
	def text(self, CHN):
		return "在你的英雄攻击后，从你的牌库中谢谢一个奥秘" if CHN else "After your hero attack, cast a Secret from your deck"
	
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.Game.Secrets.deploySecretsfromDeck(self.entity.ID)


class NorthwatchCommander(Minion):
	Class, race, name = "Paladin", "", "Northwatch Commander"
	mana, attack, health = 3, 3, 4
	index = "THE_BARRENS~Paladin~Minion~3~3~4~~Northwatch Commander~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: If you control a Secret, draw a minion"
	name_CN = "北卫军指挥官"
	
	def effCanTrig(self):
		self.effectViable = self.Game.Secrets.secrets[self.ID] != []
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if self.Game.Secrets.secrets[self.ID]:
			minions = [i for i, card in enumerate(self.Game.Hand_Deck.decks[self.ID]) if card.type == "Minion"]
			if minions: self.Game.Hand_Deck.drawCard(self.ID, npchoice(minions))
		return None


class CarielRoame(Minion):
	Class, race, name = "Paladin", "", "Cariel Roame"
	mana, attack, health = 4, 4, 3
	index = "THE_BARRENS~Paladin~Minion~4~4~3~~Cariel Roame~Rush~Divine Shield~Legendary"
	requireTarget, keyWord, description = False, "Rush,Divine Shield", "Rush, Divine Shield. Whenever this attacks, reduce the Cost of Holy Spells in your hand by (1)"
	name_CN = "凯瑞尔·罗姆"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_CarielRoame(self)]

class Trig_CarielRoame(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["MinionAttackingMinion", "MinionAttackingHero"])
	
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject == self.entity and self.entity.onBoard
	
	def text(self, CHN):
		return "" if CHN else "Whenever this attacks, reduce the Cost of Holy Spells in your hand by (1)"
	
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		for card in self.entity.Game.Hand_Deck.hands[self.entity.ID]:
			if card.type == "Spell" and card.school == "Holy":
				ManaMod(card, changeby=-1, changeto=-1).applies()


class VeteranWarmedic(Minion):
	Class, race, name = "Paladin", "", "Veteran Warmedic"
	mana, attack, health = 4, 3, 5
	index = "THE_BARRENS~Paladin~Minion~4~3~5~~Veteran Warmedic"
	requireTarget, keyWord, description = False, "", "After you cast a Holy spell, summon a 2/2 Medic with Lifesteal"
	name_CN = "战地医师老兵"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_VeteranWarmedic(self)]

class Trig_VeteranWarmedic(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["SpellBeenPlayed"])
	
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject == self.entity.Game.heroes[self.entity.ID] and self.entity.onBoard and target.school == "Holy"
	
	def text(self, CHN):
		return "在你施放一个神圣法术后，召唤一个2/2并具有吸血的医师" if CHN else "After you cast a Holy spell, summon a 2/2 Medic with Lifesteal"
	
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.summon(BattlefieldMedic(self.entity.Game, self.entity.ID), self.entity.pos+1)

class BattlefieldMedic(Minion):
	Class, race, name = "Paladin", "", "Battlefield Medic"
	mana, attack, health = 2, 2, 2
	index = "THE_BARRENS~Paladin~Minion~2~2~2~~Battlefield Medic~Lifesteal~Uncollectible"
	requireTarget, keyWord, description = False, "Lifesteal", "Lifesteal"
	name_CN = "战地医师"


class InvigoratingSermon(Spell):
	Class, school, name = "Paladin", "Holy", "Invigorating Sermon"
	requireTarget, mana = False, 4
	index = "THE_BARRENS~Paladin~Spell~4~Holy~Invigorating Sermon"
	description = "Give +1/+1 to all minions in your hand, deck and battlefield"
	name_CN = "动员布道"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		for card in self.Game.Hand_Deck.hands[self.ID]:
			if card.type == "Minion":
				card.buffDebuff(1, 1)
		for card in self.Game.Hand_Deck.decks[self.ID]:
			if card.type == "Minion":
				card.attack += 1
				card.attack_Enchant += 1
				card.health += 1
				card.health_max += 1  #By default, this healthGain has to be non-negative.
		for minion in self.Game.minionsonBoard(self.ID):
			minion.buffDebuff(1, 1)
		return None


class CannonmasterSmythe(Minion):
	Class, race, name = "Paladin", "", "Cannonmaster Smythe"
	mana, attack, health = 5, 4, 4
	index = "THE_BARRENS~Paladin~Minion~5~4~4~~Cannonmaster Smythe~Battlecry~Legendary"
	requireTarget, keyWord, description = False, "", "Battlecry: Transform your secrets into 3/3 Soldiers. They transform back when they die"
	name_CN = "火炮长斯密瑟"
	
	def effCanTrig(self):
		self.effectViable = self.Game.Secrets.secrets[self.ID] != []
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		secretsHD = self.Game.Secrets
		for i in range(len(secretsHD.secrets[self.ID])):
			if self.Game.space(self.ID):
				secret = secretsHD.extractSecrets(self.ID, 0)
				minion = NorthwatchSoldier(self.Game, self.ID)
				minion.deathrattles[0].secret = secret
				self.summon(minion, self.pos+1)
			else: break
		return None

class NorthwatchSoldier(Minion):
	Class, race, name = "Paladin", "", "Northwatch Soldier"
	mana, attack, health = 3, 3, 3
	index = "THE_BARRENS~Paladin~Minion~3~3~3~~Northwatch Soldier~Uncollectible"
	requireTarget, keyWord, description = False, "", ""
	name_CN = "北卫军士兵"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.deathrattles = [ReturnStoredSecret(self)]

class ReturnStoredSecret(Deathrattle_Minion):
	def __init__(self, entity):
		super().__init__(entity)
		self.secret = None
	
	def text(self, CHN):
		return "亡语：将奥秘移回" if CHN \
			else "Deathrattle: Transform back the secret"
	
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		if self.secret:
			self.secret.ID = self.entity.ID
			self.secret.whenEffective()
			
	def selfCopy(self, recipient):
		trig = type(self)(recipient)
		trig.secret = self.secret.selfCopy(self.entity.ID, None)
		return trig

	def createCopy(self, game):
		if self not in game.copiedObjs:  #这个扳机没有被复制过
			entityCopy = self.entity.createCopy(game)
			trigCopy = type(self)(entityCopy)
			trigCopy.secret = self.secret.createCopy(game)
			game.copiedObjs[self] = trigCopy
			return trigCopy
		else:  #一个扳机被复制过了，则其携带者也被复制过了
			return game.copiedObjs[self]


"""Priest Cards"""
class DesperatePrayer(Spell):
	Class, school, name = "Priest", "Holy", "Desperate Prayer"
	requireTarget, mana = False, 0
	index = "THE_BARRENS~Priest~Spell~0~Holy~Desperate Prayer"
	description = "Restore 5 Health to each hero"
	name_CN = "绝望祷言"
	def text(self, CHN):
		heal = 5 * (2 ** self.countHealDouble())
		return "为双方英雄恢复%d点生命值"%heal if CHN else "Restore %d health to each hero"%heal
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		heal = 5 * (2 ** self.countHealDouble())
		self.restoresAOE([hero for hero in self.Game.heroes.values()], [heal]*2)
		return None
		
		
class CondemnRank1(Spell):
	Class, school, name = "Priest", "Holy", "Condemn (Rank 1)"
	requireTarget, mana = False, 2
	index = "THE_BARRENS~Priest~Spell~2~Holy~Condemn (Rank 1)"
	description = "Deal 1 damage to all enemy minions. (Upgrades when you have 5 mana.)"
	name_CN = "罪罚（等级1）"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsHand = [Trig_ForgeUpgrade(self, CondemnRank2, 5)]  #只有在手牌中才会升级
	
	def entersHand(self):
		card = CondemnRank2(self.Game, self.ID) if self.Game.Manas.manasUpper[self.ID] > 4 else self
		card.inHand = True
		card.onBoard = card.inDeck = False
		card.enterHandTurn = card.Game.numTurn
		for trig in card.trigsHand: trig.connect()
		return card
		
	def text(self, CHN):
		damage = (1 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		return "对所有敌方随从造成%d点伤害（当你有5点法力值时升级)" % damage if CHN else "Deal %d damage to all enemy minions, (Upgrades when you have 5 mana.)" % damage
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		damage = (1 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		targets = self.Game.minionsonBoard(3-self.ID)
		self.dealsAOE(targets, [damage]*len(targets))
		return None

class CondemnRank2(Spell):
	Class, school, name = "Priest", "Holy", "Condemn (Rank 2)"
	requireTarget, mana = False, 2
	index = "THE_BARRENS~Priest~Spell~2~Holy~Condemn (Rank 2)~Uncollectible"
	description = "Deal 2 damage to all enemy minions. (Upgrades when you have 10 mana.)"
	name_CN = "罪罚（等级2）"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsHand = [Trig_ForgeUpgrade(self, CondemnRank3, 10)]  #只有在手牌中才会升级
	
	def entersHand(self):
		card = CondemnRank3(self.Game, self.ID) if self.Game.Manas.manasUpper[self.ID] > 9 else self
		card.inHand = True
		card.onBoard = card.inDeck = False
		card.enterHandTurn = card.Game.numTurn
		for trig in card.trigsHand: trig.connect()
		return card
		
	def text(self, CHN):
		damage = (2 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		return "对所有敌方随从造成%d点伤害（当你有5点法力值时升级)" % damage if CHN else "Deal %d damage to all enemy minions, (Upgrades when you have 5 mana.)" % damage
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		damage = (2 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		targets = self.Game.minionsonBoard(3 - self.ID)
		self.dealsAOE(targets, [damage] * len(targets))
		return None

class CondemnRank3(Spell):
	Class, school, name = "Priest", "Holy", "Condemn (Rank 3)"
	requireTarget, mana = False, 2
	index = "THE_BARRENS~Priest~Spell~2~Holy~Condemn (Rank 3)~Uncollectible"
	description = "Deal 3 damage to all enemy minions"
	name_CN = "罪罚（等级3）"
	def text(self, CHN):
		damage = (3 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		return "对所有敌方随从造成%d点伤害（当你有5点法力值时升级)" % damage if CHN else "Deal %d damage to all enemy minions, (Upgrades when you have 5 mana.)" % damage

	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		damage = (3 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		targets = self.Game.minionsonBoard(3 - self.ID)
		self.dealsAOE(targets, [damage] * len(targets))
		return None


class SerenaBloodfeather(Minion):
	Class, race, name = "Priest", "", "Serena Bloodfeather"
	mana, attack, health = 2, 1, 1
	index = "THE_BARRENS~Priest~Minion~2~1~1~~Serena Bloodfeather~Battlecry~Legendary"
	requireTarget, keyWord, description = True, "", "Battlecry: Choose an enemy minion. Steal Attack and Health from it until this has more"
	name_CN = "塞瑞娜·血羽"
	
	def targetExists(self, choice=0):
		return self.selectableEnemyMinionExists(choice)
	
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.ID != self.ID and target.onBoard

	
class SoothsayersCaravan(Minion):
	Class, race, name = "Priest", "", "Soothsayer's Caravan"
	mana, attack, health = 2, 1, 3
	index = "THE_BARRENS~Priest~Minion~2~1~3~~Soothsayer's Caravan"
	requireTarget, keyWord, description = False, "", "At the start of your turn, copy a spell from your opponent's deck to your hand"
	name_CN = "占卜者车队"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_SoothsayersCaravan(self)]

class Trig_SoothsayersCaravan(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["TurnStarts"])
	
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and ID == self.entity.ID
	
	def text(self, CHN):
		return "在你的回合开始时，从你对手的牌库中复制一张法术牌置入你的手牌" if CHN \
				else "At the start of your turn, copy a spell from your opponent's deck to your hand"
	
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		minion = self.entity
		spells = [card for card in self.entity.Game.Hand_Deck[3-minion.ID] if card.type == "Spell"]
		if spells: self.entity.addCardtoHand(npchoice(spells).selfCopy(minion.ID, minion), minion.ID)


class DevouringPlague(Spell):
	Class, school, name = "Priest", "Shadow", "Devouring Plague"
	requireTarget, mana = False, 3
	index = "THE_BARRENS~Priest~Spell~3~Shadow~Devouring Plague~Lifesteal"
	description = "Lifesteal. Deal 4 damage randomly split among all enemies"
	name_CN = "噬灵疫病"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.keyWords["Lifesteal"] = 1
		
	def text(self, CHN):
		damage = (4 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		return "吸血。造成%d点伤害，随机分配到所有敌人身上" % damage if CHN \
				else "Lifesteal. Deal %d damage randomly split among all enemies" % damage
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		damage = (4 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		for num in range(damage):
			objs = self.Game.charsAlive(3 - self.ID)
			if objs: self.dealsDamage(npchoice(objs), 1)
			else: break
		return None


class VoidFlayer(Minion):
	Class, race, name = "Priest", "", "Void Flayer"
	mana, attack, health = 4, 3, 4
	index = "THE_BARRENS~Priest~Minion~4~3~4~~Void Flayer~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: For each spell in your hand, deal 1 damage to a random enemy minion"
	name_CN = "剥灵者"

	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		damage = sum(card.type == "Spell" for card in self.Game.Hand_Deck.hands[self.ID])
		for num in range(damage):
			objs = self.Game.charsAlive(3-self.ID)
			if objs: self.dealsDamage(npchoice(objs), 1)
			else: break
		return None
	
	
class Xyrella(Minion):
	Class, race, name = "Priest", "", "Xyrella"
	mana, attack, health = 4, 4, 4
	index = "THE_BARRENS~Priest~Minion~4~4~4~~Xyrella~Battlecry~Legendary"
	requireTarget, keyWord, description = False, "", "Battlecry: If you've restored Health this turn, deal that much damage to all enemy minions"
	name_CN = "泽瑞拉"
	
	def effCanTrig(self):
		self.effectViable = self.Game.Counters.healthRestoredThisTurn[self.ID] > 0

	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		damage = self.Game.healthRestoredThisTurn[self.ID]
		if damage > 0:
			targets = self.Game.minionsonBoard(3-self.ID)
			self.dealsAOE(targets, [damage]*len(targets))
		return None


class PriestofAnshe(Minion):
	Class, race, name = "Priest", "", "Priest of An'she"
	mana, attack, health = 5, 5, 5
	index = "THE_BARRENS~Priest~Minion~5~5~5~~Priest of An'she~Taunt~Battlecry"
	requireTarget, keyWord, description = False, "Taunt", "Taunt. Battlecry: If you've restored Health this turn, gain +3/+3"
	name_CN = "安瑟祭司"
	
	def effCanTrig(self):
		self.effectViable = self.Game.Counters.healthRestoredThisTurn[self.ID] > 0

	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if self.Game.healthRestoredThisTurn[self.ID] > 0:
			self.buffDebuff(3, 3)
		return None


class LightshowerElemental(Minion):
	Class, race, name = "Priest", "Elemental", "Lightshower Elemental"
	mana, attack, health = 6, 6, 6
	index = "THE_BARRENS~Priest~Minion~6~6~6~Elemental~Lightshower Elemental~Taunt~Deathrattle"
	requireTarget, keyWord, description = False, "Taunt", "Taunt. Deathrattle: Restore 8 Health to all friendly characters"
	name_CN = "光沐元素"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.deathrattles = [Restore8HealthtoAllFriendlies(self)]

class Restore8HealthtoAllFriendlies(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		minion = self.entity
		heal = 8 * (2 ** minion.countHealDouble())
		targets = minion.minionsonBoard(minion.ID) + [minion.Game.heroes[minion.ID]]
		self.entity.restoresAOE(targets, [heal]*len(targets))

	def text(self, CHN):
		heal = 8 * (2 ** self.entity.countHealDouble())
		return "亡语：为所有友方角色恢复%d点生命值" % heal if CHN else "Deathrattle: Restore %d Health to all friendly characters" % heal


class PowerWordFortitude(Spell):
	Class, school, name = "Priest", "Holy", "Power Word: Fortitude"
	requireTarget, mana = True, 8
	index = "THE_BARRENS~Priest~Spell~8~Holy~Power Word: Fortitude"
	description = "Give a minion +3/+5. Costs (1) less for each spell in your hand"
	name_CN = "真言术：韧"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsHand = [Trigger_PowerWordFortitude(self)]
	
	def selfManaChange(self):
		if self.inHand:
			self.mana -= sum(card.type == "Spell" for card in self.Game.Hand_Deck.hands[3 - self.ID])
			self.mana = max(0, self.mana)

class Trigger_PowerWordFortitude(TrigHand):
	def __init__(self, entity):
		super().__init__(entity, ["CardLeavesHand", "CardEntersHand"])
	
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.inHand and ((target[0] if signal == "CardEntersHand" else target).ID == self.entity.ID)
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.Game.ManaHandler.calcMana_Single(self.entity)


"""Rogue Cards"""
class ParalyticPoison(Spell):
	Class, school, name = "Rogue", "Nature", "Paralytic Poison"
	requireTarget, mana = False, 1
	index = "THE_BARRENS~Rogue~Spell~1~Nature~Paralytic Poison"
	description = "Give your weapon +1 Attack and 'Your hero is Immune while attacking'"
	name_CN = "麻痹药膏"
	def available(self):
		return self.Game.availableWeapon(self.ID) is not None
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		weapon = self.Game.availableWeapon(self.ID)
		if weapon:
			weapon.gainStat(1, 0)
			trig = Trig_ParalyticPoison(weapon)
			weapon.trigsBoard.append(trig)
			trig.connect()
		return None

class Trig_ParalyticPoison(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["BattleStarted", "BattleFinished"])
	
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject == self.entity.Game.heroes[self.entity.ID] and self.entity.onBoard
	
	def text(self, CHN):
		return "你的英雄在攻击时具有免疫" if CHN else "Your hero is Immune while attacking"
	
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		if signal == "BattleStarted": subject.getsStatus("Immune")
		else: subject.losesStatus("Immune")
		

class Yoink(Spell):
	Class, school, name = "Rogue", "", "Yoink!"
	requireTarget, mana = False, 1
	index = "THE_BARRENS~Rogue~Spell~1~~Yoink!"
	description = "Discover a Hero Power and set its Cost to (0). Swap back after 2 uses"
	name_CN = "偷师学艺"
	poolIdentifier = "Basic Powers"
	@classmethod
	def generatePool(cls, pools):
		return "Basic Powers", pools.basicPowers
	
	def getaNewPowerThatSwapsBack(self, power_New, power_Orig):
		power_New.getsTrig(Trig_SwapBackPowerAfter2Uses(power_New, power_Orig), trigType="TrigBoard", connect=False)
		power_New.replaceHeroPower()
		
	def decidePowerPool(self):
		pool = self.rngPool("Basic Powers")[:]
		try: pool.remove(type(self.Game.powers[self.ID]))
		except: pass
		return pool
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.discoverandGenerate(Yoink, comment, lambda : Yoink.decidePowerPool(self))
		return None
	
	def discoverDecided(self, option, case, info_RNGSync=None, info_GUISync=None):
		if case == "Discovered" or case == "Random":
			self.Game.picks.append((info_RNGSync, info_GUISync, case == "Random",
									option if inspect.isclass(option) else type(option)) )
		Yoink.getaNewPowerThatSwapsBack(self, option, self.Game.powers[self.ID])
		
class Trig_SwapBackPowerAfter2Uses(TrigBoard):
	def __init__(self, entity, powerReplaced):
		super().__init__(entity, ["HeroUsedAbility"])
		self.counter = 0
		self.powerReplaced = powerReplaced
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject == self.entity
	
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.counter += 1
		if self.counter > 1:
			self.powerReplaced.replaceHeroPower()
			

class EfficientOctobot(Minion):
	Class, race, name = "Rogue", "Mech", "Efficient Octo-bot"
	mana, attack, health = 2, 1, 4
	index = "THE_BARRENS~Rogue~Minion~2~1~4~Mech~Efficient Octo-bot~Frenzy"
	requireTarget, keyWord, description = False, "", "Frenzy: Reduce the cost of cards in your hand by (1)"
	name_CN = "高效八爪机器人"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_EfficientOctobot(self)]

class Trig_EfficientOctobot(Frenzy):
	def text(self, CHN):
		return "暴怒：你的手牌法力值消耗减少(1)点" if CHN else "Frenzy: Reduce the cost of cards in your hand by (1)"
	
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		for card in self.entity.Game.Hand_Deck.hands[self.entity.ID]:
			ManaMod(card, changeby=-1, changeto=-1).applies()


class SilverleafPoison(Spell):
	Class, school, name = "Rogue", "Nature", "Silverleaf Poison"
	requireTarget, mana = False, 2
	index = "THE_BARRENS~Rogue~Spell~2~Nature~Silverleaf Poison"
	description = "Give your weapon 'After your hero attacks draw a card'"
	name_CN = "银叶草药膏"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		weapon = self.Game.availableWeapon(self.ID)
		if weapon:
			trig = Trig_SilverleafPoison(weapon)
			weapon.trigsBoard.append(trig)
			trig.connect()
		return None

class Trig_SilverleafPoison(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["HeroAttackedMinion", "HeroAttackedHero"])
	
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject.ID == self.entity.ID
	
	def text(self, CHN):
		return "在你的英雄攻击后，抽一张牌" if CHN else "After your hero attacks draw a card"
	
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.Game.Hand_Deck.drawCard(self.entity.ID)
		

class WickedStabRank1(Spell):
	Class, school, name = "Rogue", "", "Wicked Stab (Rank 1)"
	requireTarget, mana = True, 2
	index = "THE_BARRENS~Rogue~Spell~2~~Wicked Stab (Rank 1)"
	description = "Deal 2 damage. (Upgrades when you have 5 mana.)"
	name_CN = "邪恶挥刺（等级1）"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsHand = [Trig_ForgeUpgrade(self, WickedStabRank2, 5)]  #只有在手牌中才会升级
	
	def entersHand(self):
		card = WickedStabRank2(self.Game, self.ID) if self.Game.Manas.manasUpper[self.ID] > 4 else self
		card.inHand = True
		card.onBoard = card.inDeck = False
		card.enterHandTurn = card.Game.numTurn
		for trig in card.trigsHand: trig.connect()
		return card
	
	def text(self, CHN):
		damage = (2 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		return "造成%d点伤害（当你有5点法力值时升级)" % damage if CHN else "Deal %d damage. (Upgrades when you have 5 mana.)" % damage
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if target:
			damage = (2 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			self.dealsDamage(target, damage)
		return target

class WickedStabRank2(Spell):
	Class, school, name = "Rogue", "", "Wicked Stab (Rank 2)"
	requireTarget, mana = True, 2
	index = "THE_BARRENS~Rogue~Spell~2~~Wicked Stab (Rank 2)~Uncollectible"
	description = "Deal 4 damage. (Upgrades when you have 10 mana.)"
	name_CN = "邪恶挥刺（等级2）"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsHand = [Trig_ForgeUpgrade(self, WickedStabRank3, 10)]  #只有在手牌中才会升级
	
	def entersHand(self):
		card = WickedStabRank3(self.Game, self.ID) if self.Game.Manas.manasUpper[self.ID] > 9 else self
		card.inHand = True
		card.onBoard = card.inDeck = False
		card.enterHandTurn = card.Game.numTurn
		for trig in card.trigsHand: trig.connect()
		return card
	
	def text(self, CHN):
		damage = (4 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		return "造成%d点伤害（当你有10点法力值时升级)" % damage if CHN else "Deal %d damage. (Upgrades when you have 10 mana.)" % damage
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if target:
			damage = (4 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			self.dealsDamage(target, damage)
		return target

class WickedStabRank3(Spell):
	Class, school, name = "Rogue", "", "Wicked Stab (Rank 3)"
	requireTarget, mana = True, 2
	index = "THE_BARRENS~Rogue~Spell~2~~Wicked Stab (Rank 3)~Uncollectible"
	description = "Deal 6 damage"
	name_CN = "邪恶挥刺（等级3）"
	def text(self, CHN):
		damage = (6 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		return "对一个随从和随机一个相邻随从造成%d点伤害" % damage if CHN else "Deal %d damage to a minion and a random adjacent one" % damage
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if target:
			damage = (6 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			self.dealsDamage(target, damage)
		return target


class FieldContact(Minion):
	Class, race, name = "Rogue", "", "Field Contact"
	mana, attack, health = 3, 3, 2
	index = "THE_BARRENS~Rogue~Minion~3~3~2~~Field Contact"
	requireTarget, keyWord, description = False, "", "After you play a Battlecry or Combo card, draw a card"
	name_CN = "原野联络人"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_FieldContact(self)]

class Trig_FieldContact(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["MinionBeenPlayed", "SpellBeenPlayed", "WeaponBeenPlayed", "HeroBeenPlayed"])
	
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject.ID == self.entity.ID
	
	def text(self, CHN):
		return "在你使用一张战吼牌或连击牌后，抽一张牌" if CHN else "After you play a Battlecry or Combo card, draw a card"
	
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.Game.Hand_Deck.drawCard(self.entity.ID)


class SwinetuskShank(Weapon):
	Class, name, description = "Rogue", "Swinetusk Shank", "After you play a Poison gain +1 Durability"
	mana, attack, durability = 3, 2, 2
	index = "THE_BARRENS~Rogue~Weapon~3~2~2~Swinetusk Shank"
	name_CN = "猪牙匕首"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_SwinetuskShank(self)]

class Trig_SwinetuskShank(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["SpellBeenPlayed"])
	
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject.ID == self.entity.ID and self.entity.onBoard and "Poison" in subject.name
	
	def text(self, CHN):
		return "在你使用一张药膏牌后，便获得+1耐久度" if CHN else "After you play a Poison gain +1 Durability"
	
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.gainStat(0, 1)


class ApothecaryHelbrim(Minion):
	Class, race, name = "Rogue", "", "Apothecary Helbrim"
	mana, attack, health = 4, 3, 2
	index = "THE_BARRENS~Rogue~Minion~4~3~2~~Apothecary Helbrim~Battlecry~Deathrattle~Legendary"
	requireTarget, keyWord, description = False, "", "Battlecry and Deathrattle: Add a random Poison to your hand"
	name_CN = "药剂师赫布拉姆"
	poolIdentifier = "Poisons"
	@classmethod
	def generatePool(cls, pools):
		return "Poisons", [card for card in pools.ClassCards["Rogue"] if card.type == "Spell" and "Poison" in card.name]
		
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.deathrattles = [AddaPoisontoYourHand(self)]

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.addCardtoHand(npchoice(self.rngPool("Poisons")), self.ID)
		return None

class AddaPoisontoYourHand(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.addCardtoHand(npchoice(self.rngPool("Poisons")), self.entity.ID)
		
	def text(self, CHN):
		return "亡语：随机将一张药膏置入你的手牌" if CHN else "Deathrattle: Add a random Poison to your hand"
	
	
class OilRigAmbusher(Minion):
	Class, race, name = "Rogue", "", "Oil Rig Ambusher"
	mana, attack, health = 4, 4, 4
	index = "THE_BARRENS~Rogue~Minion~4~4~4~~Oil Rig Ambusher~Battlecry"
	requireTarget, keyWord, description = True, "", "Battlecry: Deal 2 damamge. If this entered your hand this turn, deal 4 damage instead"
	name_CN = "油田伏击者"
	
	def effCanTrig(self):
		self.effectViable = self.enterHandTurn == self.Game.numTurn
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			self.dealsDamage(target, 4 if self.enterHandTurn == self.Game.numTurn else 2)
		return target


class ScabbsCutterbutter(Minion):
	Class, race, name = "Rogue", "", "Scabbs Cutterbutter"
	mana, attack, health = 4, 3, 3
	index = "THE_BARRENS~Rogue~Minion~4~3~3~~Scabbs Cutterbutter~Combo~Legendary"
	requireTarget, keyWord, description = False, "", "Combo: The next two cards you play this turn cost (3) less"
	name_CN = "斯卡布斯·刀油"
	
	def effCanTrig(self):
		self.effectViable = self.Game.Counters.numCardsPlayedThisTurn[self.ID] > 0
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if self.Game.Counters.numCardsPlayedThisTurn[self.ID] > 0:
			tempAura = GameManaAura_InTurnNext2Cards3Less(self.Game, self.ID)
			self.Game.Manas.CardAuras.append(tempAura)
			tempAura.auraAppears()
		return None

class GameManaAura_InTurnNext2Cards3Less(TempManaEffect):
	def __init__(self, Game, ID, changeby=0, changeto=-1):
		super().__init__(Game, ID, changeby, changeto)
		self.counter = 2
	
	def applicable(self, target):
		return target.ID == self.ID
	
	def trig(self, signal, ID, subject, target, number, comment, choice=0):
		if (target[0] if signal[0] == "C" else subject).ID == self.ID:
			if signal[0] == "C":
				self.applies(target[0])
			else:
				self.counter -= 1
				if self.counter < 1: self.auraDisappears()
	
	def selfCopy(self, game):
		aura = type(self)(game, self.ID)
		aura.counter = self.counter
		return aura
	

"""Shaman Cards"""
class SpawnpoolForager(Minion):
	Class, race, name = "Shaman", "Murloc", "Spawnpool Forager"
	mana, attack, health = 1, 1, 2
	index = "THE_BARRENS~Shaman~Minion~1~1~2~Murloc~Spawnpool Forager~Deathrattle"
	requireTarget, keyWord, description = False, "", "Deathrattle: Summon a 1/1 Tinyfin"
	name_CN = "孵化池觅食者"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.deathrattles = [SummonaTinyfin(self)]

class SummonaTinyfin(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.summon(DiremuckTinyfin(self.entity.Game, self.entity.ID), self.entity.pos + 1)
	
	def text(self, CHN):
		return "亡语：召唤一个1/1的鱼人宝宝" if CHN else "Deathrattle: Summon a 1/1 Tinyfin"

class DiremuckTinyfin(Minion):
	Class, race, name = "Shaman", "Murloc", "Diremuck Tinyfin"
	mana, attack, health = 1, 1, 1
	index = "THE_BARRENS~Shaman~Minion~1~1~1~Murloc~Diremuck Tinyfin~Uncollectible"
	requireTarget, keyWord, description = False, "", ""
	name_CN = "凶饿的鱼人宝宝"


class ChainLightningRank1(Spell):
	Class, school, name = "Shaman", "Nature", "Chain Lightning (Rank 1)"
	requireTarget, mana = True, 2
	index = "THE_BARRENS~Shaman~Spell~2~Nature~Chain Lightning (Rank 1)"
	description = "Deal 2 damage to a minion and a random adjacent one. (Upgrades when you have 5 mana.)"
	name_CN = "闪电链（等级1）"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsHand = [Trig_ForgeUpgrade(self, ChainLightningRank2, 5)] #只有在手牌中才会升级
		
	def entersHand(self):
		card = ChainLightningRank2(self.Game, self.ID) if self.Game.Manas.manasUpper[self.ID] > 4 else self
		card.inHand = True
		card.onBoard = card.inDeck = False
		card.enterHandTurn = card.Game.numTurn
		for trig in card.trigsHand: trig.connect()
		return card
	
	def available(self):
		return self.selectableMinionExists()
	
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard

	def text(self, CHN):
		damage = (2 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		return "对一个随从和随机一个相邻随从造成%d点伤害（当你有5点法力值时升级)"%damage if CHN else "Deal %d damage to a minion and a random adjacent one. (Upgrades when you have 5 mana.)"%damage
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if target:
			damage = (2 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			neighbors = self.Game.neighbors2(target)[0]
			if neighbors: self.dealsAOE([target, npchoice(neighbors)], [damage] * 2)
			else: self.dealsDamage(target, damage)
		return target
		
class ChainLightningRank2(Spell):
	Class, school, name = "Shaman", "Nature", "Chain Lightning (Rank 2)"
	requireTarget, mana = True, 2
	index = "THE_BARRENS~Shaman~Spell~2~Nature~Chain Lightning (Rank 2)~Uncollectible"
	description = "Deal 3 damage to a minion and a random adjacent one. (Upgrades when you have 10 mana.)"
	name_CN = "闪电链（等级2）"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsHand = [Trig_ForgeUpgrade(self, ChainLightningRank2, 10)] #只有在手牌中才会升级
		
	def entersHand(self):
		card = ChainLightningRank2(self.Game, self.ID) if self.Game.Manas.manasUpper[self.ID] > 9 else self
		card.inHand = True
		card.onBoard = card.inDeck = False
		card.enterHandTurn = card.Game.numTurn
		for trig in card.trigsHand: trig.connect()
		return card
	
	def available(self):
		return self.selectableMinionExists()
	
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
	
	def text(self, CHN):
		damage = (3 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		return "对一个随从和随机一个相邻随从造成%d点伤害（当你有5点法力值时升级)"%damage if CHN else "Deal %d damage to a minion and a random adjacent one. (Upgrades when you have 5 mana.)"%damage
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if target:
			damage = (3 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			neighbors = self.Game.neighbors2(target)[0]
			if neighbors: self.dealsAOE([target, npchoice(neighbors)], [damage]*2)
			else: self.dealsDamage(target, damage)
		return target
		
class ChainLightningRank3(Spell):
	Class, school, name = "Shaman", "Nature", "Chain Lightning (Rank 3)"
	requireTarget, mana = True, 2
	index = "THE_BARRENS~Shaman~Spell~2~Nature~Chain Lightning (Rank 3)~Uncollectible"
	description = "Deal 4 damage to a minion and a random adjacent one"
	name_CN = "闪电链（等级3）"
	def available(self):
		return self.selectableMinionExists()
	
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
	
	def text(self, CHN):
		damage = (4 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		return "对一个随从和随机一个相邻随从造成%d点伤害"%damage if CHN else "Deal %d damage to a minion and a random adjacent one"%damage
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if target:
			damage = (4 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			neighbors = self.Game.neighbors2(target)[0]
			if neighbors: self.dealsAOE([target, npchoice(neighbors)], [damage]*2)
			else: self.dealsDamage(target, damage)
		return target
		
		
class FiremancerFlurgl(Minion):
	Class, race, name = "Shaman", "Murloc", "Firemancer Flurgl"
	mana, attack, health = 2, 2, 3
	index = "THE_BARRENS~Shaman~Minion~2~2~3~Murloc~Firemancer Flurgl~Legendary"
	requireTarget, keyWord, description = False, "", "After you play a Murloc, deal 1 damage to all enemies"
	name_CN = "火焰术士弗洛格尔"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_FiremancerFlurgl(self)]

class Trig_FiremancerFlurgl(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["MinionBeenPlayed"])
	
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject.ID == self.entity.ID
	
	def text(self, CHN):
		return "在你使用一个鱼人后，对所有敌人造成1点伤害" if CHN else "After you play a Murloc, deal 1 damage to all enemies"
	
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		targets = self.entity.Game.minionsonBoard(3-self.entity.ID) + [self.entity.Game.heroes[3-self.entity.ID]]
		self.entity.dealsAOE(targets, [1]*len(targets))


class SouthCoastChieftain(Minion):
	Class, race, name = "Shaman", "Murloc", "South Coast Chieftain"
	mana, attack, health = 2, 3, 2
	index = "THE_BARRENS~Shaman~Minion~2~3~2~Murloc~South Coast Chieftain~Battlecry"
	requireTarget, keyWord, description = True, "", "Battlecry: If you control another Murloc, deal 2 damage"
	name_CN = "南海岸酋长"
	
	def effCanTrig(self):
		self.effectViable = any("Murloc" in minion.race for minion in self.Game.minionsonBoard(self.ID))

	def returnTrue(self, choice=0):
		return any("Murloc" in minion.race for minion in self.Game.minionsonBoard(self.ID))

	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target != self and target.onBoard
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target and any("Murloc" in minion.race for minion in self.Game.minionsonBoard(self.ID)):
			self.dealsDamage(target, 2)
		return target


class TinyfinsCaravan(Minion):
	Class, race, name = "Shaman", "", "Tinyfin's Caravan"
	mana, attack, health = 2, 1, 3
	index = "THE_BARRENS~Shaman~Minion~2~1~3~~Tinyfin's Caravan"
	requireTarget, keyWord, description = False, "", "At the start of your turn, draw a Murloc"
	name_CN = "鱼人宝宝车队"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_TinyfinsCaravan(self)]

class Trig_TinyfinsCaravan(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["TurnStarts"])
	
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and ID == self.entity.ID
	
	def text(self, CHN):
		return "在你的回合开始时，从抽一张鱼人牌" if CHN else "At the start of your turn, draw a Murloc"
	
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		murlocs = [i for i, card in enumerate(self.entity.Game.Hand_Deck.decks[self.entity.ID]) if card.type == "Minion" and "Murloc" in card.race]
		if murlocs: self.entity.Game.Hand_Deck.drawCard(self.entity.ID, npchoice(murlocs))
			
			
class AridStormer(Minion):
	Class, race, name = "Shaman", "Elemental", "Arid Stormer"
	mana, attack, health = 3, 2, 5
	index = "THE_BARRENS~Shaman~Minion~3~2~5~Elemental~Arid Stormer~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: If you played an Elemental last turn, gain Rush and Windfury"
	name_CN = "旱地风暴"
	
	def effCanTrig(self):
		self.effectViable = self.Game.Counters.numElementalsPlayedLastTurn[self.ID] > 0
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if self.Game.Counters.numElementalsPlayedLastTurn[self.ID] > 0:
			self.getsStatus("Rush")
			self.getsStatus("Windfury")
		return None


class NofinCanStopUs(Spell):
	Class, school, name = "Shaman", "", "Nofin Can Stop Us"
	requireTarget, mana = False, 3
	index = "THE_BARRENS~Shaman~Spell~3~~Nofin Can Stop Us"
	description = "Give your minions +1/+1. Give your Murlocs an extra +1/+1"
	name_CN = "鱼勇可贾"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		for minion in self.Game.minionsonBoard(self.ID):
			buff = 2 if "Murloc" in minion.race else 1
			minion.buffDebuff(buff, buff)
		return None


class Brukan(Minion):
	Class, race, name = "Shaman", "", "Bru'kan"
	mana, attack, health = 4, 5, 4
	index = "THE_BARRENS~Shaman~Minion~4~5~4~~Bru'kan~Legendary"
	requireTarget, keyWord, description = False, "", "Nature Spell Damage +3"
	name_CN = "布鲁坎"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.keyWords["Nature Spell Damage"] = 3


class EarthRevenant(Minion):
	Class, race, name = "Shaman", "Elemental", "Earth Revenant"
	mana, attack, health = 4, 2, 6
	index = "THE_BARRENS~Shaman~Minion~4~2~6~Elemental~Earth Revenant~Taunt~Battlecry"
	requireTarget, keyWord, description = False, "Taunt", "Taunt. Battlecry: Deal 1 damage to all enemy minions"
	name_CN = "大地亡魂"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		targets = self.Game.minionsonBoard(3-self.ID)
		self.dealsAOE(targets, [1]*len(targets))
		return None

class LilypadLurker(Minion):
	Class, race, name = "Shaman", "Elemental", "Lilypad Lurker"
	mana, attack, health = 5, 5, 6
	index = "THE_BARRENS~Shaman~Minion~5~5~6~Elemental~Lilypad Lurker~Battlecry"
	requireTarget, keyWord, description = True, "", "Battlecry: If you played an Elemental last turn, transform an enemy minion into a 0/1 Frog with Taunt"
	name_CN = "荷塘潜伏者"
	
	def returnTrue(self, choice=0):
		return self.Game.Counters.numElementalsPlayedLastTurn[self.ID] > 0
	
	def effCanTrig(self):
		self.effectViable = self.Game.Counters.numElementalsPlayedLastTurn[self.ID] > 0
	
	def targetExists(self, choice=0):
		return self.selectableMinionExists(choice)
	
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target != self and target.onBoard
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target and self.Game.Counters.numElementalsPlayedLastTurn[self.ID] > 0:
			self.transform(target, Frog(self.Game, self.ID))
		return target


"""Warlock Cards"""
class AltarofFire(Spell):
	Class, school, name = "Warlock", "Fire", "Altar of Fire"
	requireTarget, mana = False, 1
	index = "THE_BARRENS~Warlock~Spell~1~Fire~Altar of Fire"
	description = "Destroy a friendly minion. Deal 2 damage to all enemy minions"
	name_CN = "火焰祭坛"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		self.Game.Hand_Deck.removeDeckTopCard(self.ID, num=3)
		self.Game.Hand_Deck.removeDeckTopCard(3-self.ID, num=3)
		return None


class GrimoireofSacrifice(Spell):
	Class, school, name = "Warlock", "Shadow", "Grimoire of Sacrifice"
	requireTarget, mana = True, 1
	index = "THE_BARRENS~Warlock~Spell~1~Shadow~Grimoire of Sacrifice"
	description = "Destroy a friendly minion. Deal 2 damage to all enemy minions"
	name_CN = "牺牲魔典"
	def available(self):
		return self.selectableFriendlyMinionExists()
	
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard and target.ID == self.ID
	
	def text(self, CHN):
		damage = (2 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		return "消灭一个友方随从。对所有敌方随从造成%d点伤害" % damage if CHN else "Destroy a friendly minion. Deal %d damage to all enemy minions" % damage
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			self.Game.killMinion(self, target)
			damage = (2 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			targets = self.Game.minionsonBoard(3-self.ID)
			self.dealsAOE(targets, [damage]*len(targets))
		return target
	
	
class ApothecarysCaravan(Minion):
	Class, race, name = "Warlock", "", "Apothecary's Caravan"
	mana, attack, health = 2, 1, 3
	index = "THE_BARRENS~Warlock~Minion~2~1~3~~Apothecary's Caravan"
	requireTarget, keyWord, description = False, "", "At the start of your turn, summon a 1-Cost minion from your deck"
	name_CN = "药剂师车队"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_ApothecarysCaravan(self)]

class Trig_ApothecarysCaravan(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["TurnStarts"])
	
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and ID == self.entity.ID
	
	def text(self, CHN):
		return "在你的回合开始时，从你的牌库召唤一个法力值消耗为(1)的随从" if CHN else "At the start of your turn, summon a 1-Cost minion from your deck"
	
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		minion = self.entity
		minions = [i for i, card in enumerate(minion.Game.Hand_Deck.decks[minion.ID]) if card.type == "Minion" and card.mana == 1]
		if minions: minion.Game.summonfrom(npchoice(minions), minion.ID, minion.pos+1, minion, source='D')
		

class ImpSwarmRank1(Spell):
	Class, school, name = "Warlock", "Fel", "Imp Swarm (Rank 1)"
	requireTarget, mana = False, 2
	index = "THE_BARRENS~Warlock~Spell~2~Fel~Imp Swarm (Rank 1)"
	description = "Summon a 3/2 Imp. (Upgrades when you have 5 mana.)"
	name_CN = "小鬼集群（等级1）"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsHand = [Trig_ForgeUpgrade(self, ImpSwarmRank2, 5)] #只有在手牌中才会升级
		
	def entersHand(self):
		card = ImpSwarmRank2(self.Game, self.ID) if self.Game.Manas.manasUpper[self.ID] > 4 else self
		card.inHand = True
		card.onBoard = card.inDeck = False
		card.enterHandTurn = card.Game.numTurn
		for trig in card.trigsHand: trig.connect()
		return card
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		self.summon(ImpFamiliar(self.Game, self.ID), -1)
		return None
		
class ImpFamiliar(Minion):
	Class, race, name = "Warlock", "Demon", "Imp Familiar"
	mana, attack, health = 2, 3, 2
	index = "THE_BARRENS~Warlock~Minion~2~3~2~Demon~Imp Familiar~Uncollectible"
	requireTarget, keyWord, description = False, "", ""
	name_CN = "小鬼魔仆"
	
class ImpSwarmRank2(Spell):
	Class, school, name = "Warlock", "Fel", "Imp Swarm (Rank 2)"
	requireTarget, mana = False, 2
	index = "THE_BARRENS~Warlock~Spell~2~Fel~Imp Swarm (Rank 2)~Uncollectible"
	description = "Summon two 3/2 Imps. (Upgrades when you have 10 Mana.)"
	name_CN = "小鬼集群（等级2）"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsHand = [Trig_ForgeUpgrade(self, ImpSwarmRank3, 10)] #只有在手牌中才会升级
		
	def entersHand(self):
		card = ImpSwarmRank3(self.Game, self.ID) if self.Game.Manas.manasUpper[self.ID] > 9 else self
		card.inHand = True
		card.onBoard = card.inDeck = False
		card.enterHandTurn = card.Game.numTurn
		for trig in card.trigsHand: trig.connect()
		return card
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		self.summon([ImpFamiliar(self.Game, self.ID) for i in range(2)], (-1, "totheRightEnd"))
		return None
		
class ImpSwarmRank3(Spell):
	Class, school, name = "Warlock", "Fel", "Imp Swarm (Rank 3)"
	requireTarget, mana = False, 2
	index = "THE_BARRENS~Warlock~Spell~2~Fel~Imp Swarm (Rank 3)~Uncollectible"
	description = "Summon three 3/2 Imps"
	name_CN = "小鬼集群（等级3）"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		self.summon([ImpFamiliar(self.Game, self.ID) for i in range(3)], (-1, "totheRightEnd"))
		return None
		
		
class BloodShardBristleback(Minion):
	Class, race, name = "Warlock", "Quilboar", "Blood Shard Bristleback"
	mana, attack, health = 3, 3, 3
	index = "THE_BARRENS~Warlock~Minion~3~3~3~Quilboar~Blood Shard Bristleback~Lifesteal~Battlecry"
	requireTarget, keyWord, description = True, "Lifesteal", "Lifesteal. Battlecry: If your deck contains 10 or fewer cards, deal 6 damage to a minion"
	name_CN = " 血之碎片刺背野猪人"
	def need2Choose(self):
		return len(self.Game.Hand_Deck.decks[self.ID]) < 11
	
	def targetExists(self, choice=0):
		return self.selectableMinionExists()
	
	def targetCorrect(self, target, choice=0):
		return target.onBoard and target.type == "Minion" and target != self
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target and len(self.Game.Hand_Deck.decks[self.ID]) < 11:
			self.dealsDamage(target, 6)
		return target


class KabalOutfitter(Minion):
	Class, race, name = "Warlock", "", "Kabal Outfitter"
	mana, attack, health = 3, 3, 3
	index = "THE_BARRENS~Warlock~Minion~3~3~3~~Kabal Outfitter~Battlecry~Deathrattle"
	requireTarget, keyWord, description = False, "", "Battlecry and Deathrattle: Give another random friendly minion +1/+1"
	name_CN = "暗金教物资官"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.deathrattles = [GiveaFriendlyMinionPlus1Plus1(self)]
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		minions = self.Game.minionsonBoard(self.ID, self)
		if minions: npchoice(minions).buffDebuff(1, 1)
		return None

class GiveaFriendlyMinionPlus1Plus1(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		minions = self.entity.Game.minionsonBoard(self.entity.ID, self.entity)
		if minions: npchoice(minions).buffDebuff(1, 1)
	
	def text(self, CHN):
		return "亡语：随机使另一个友方随从获得+1/+1" if CHN else "Deathrattle: Give another random friendly minion +1/+1"


class TamsinRoame(Minion):
	Class, race, name = "Warlock", "", "Tamsin Roame"
	mana, attack, health = 3, 1, 3
	index = "THE_BARRENS~Warlock~Minion~3~1~3~~Tamsin Roame~Legendary"
	requireTarget, keyWord, description = False, "", "Whenever you cast a Shadow spell that costs (1) or more, add a copy to your hand that costs (0)"
	name_CN = "塔姆辛·罗姆"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_TamsinRoame(self)]

class Trig_TamsinRoame(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["SpellPlayed"])
	
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject.ID == self.entity.ID and subject.school == "Shadow" and number > 0
	
	def text(self, CHN):
		return "每当你施放一个法力值消耗大于或等于(1)点的暗影法术时，将法术牌的一张复制置入你的手牌，其法力值消耗为(0)点" if CHN \
			else "Whenever you cast a Shadow spell that costs (1) or more, add a copy to your hand that costs (0)"
	
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		Copy = subject.selfCopy(self.entity.ID, self.entity)
		self.entity.addCardtoHand(Copy, self.entity.ID)
		if Copy.inHand: ManaMod(Copy, changeto=0).applies()


class SoulRend(Spell):
	Class, school, name = "Warlock", "Shadow", "Soul Rend"
	requireTarget, mana = False, 4
	index = "THE_BARRENS~Warlock~Spell~4~Shadow~Soul Rend"
	description = "Deal 5 damage to all minions. Destroy a card in your deck for each killed"
	name_CN = "灵魂撕裂"
	def text(self, CHN):
		damage = (5 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		return "对所有随从造成%d点伤害。每消灭一个随从，便摧毁你牌库中的一张牌" % damage if CHN \
			else "Deal %d damage to all minions. Destroy a card in your deck for each killed" % damage
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		damage = (5 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		targets = self.Game.minionsonBoard(1) + self.Game.minionsonBoard(2)
		self.dealsAOE(targets, [damage]*len(targets))
		numKilled = sum(minion.health < 1 or minion.dead for minion in targets)
		if numKilled:
			self.Game.Hand_Deck.removeDeckTopCard(self.ID, numKilled)
		return None


class NeeruFireblade(Minion):
	Class, race, name = "Warrior", "", "Neeru Fireblade"
	mana, attack, health = 5, 5, 5
	index = "THE_BARRENS~Warrior~Minion~5~5~5~~Neeru Fireblade~Battlecry~Legendary"
	requireTarget, keyWord, description = False, "", "Battlecry: If your deck is empty, open a portal that fills your board with 3/2 Imps each turn"
	name_CN = "尼尔鲁·火刃"
	
	def effCanTrig(self):
		self.effectViable = not self.Game.Hand_Deck.decks[self.ID]
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		game = self.Game
		if not game.Hand_Deck.decks[self.ID]:
			if game.space(self.ID) > 0:
				pos = self.pos
				portal = BurningBladePortal(game, self.ID)
				portal.seq = len(game.minions[1]) + len(game.minions[2]) + len(game.weapons[1]) + len(game.weapons[2])
				game.minions[self.ID].insert(pos + 100 * (pos < 0), portal)  #If position is too large, the insert() simply puts it at the end.
				game.sortPos()
				game.sortSeq()
				game.GUI.summonAni(portal)
				portal.appears()
		return None
	
class BurningBladePortal(Dormant):
	Class, name = "Warlock", "Burning Blade Portal"
	description = "At the end of your turn, fill your board with 3/2 Imps"
	index = "THE_BARRENS~Dormant~Burning Blade Portal~Legendary"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_BurningBladePortal(self)]
		
class Trig_BurningBladePortal(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["TurnEnds"])  #假设是死亡时扳机，而还是死亡后扳机
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and ID == self.entity.ID
	
	def text(self, CHN):
		return "在你的回合结束时，召唤数个3/2的小鬼，直到你的随从数量达到上限" if CHN else "At the end of your turn, fill your board with 3/2 Imps"
	
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		minion = self.entity
		minion.summon([ImpFamiliar(minion.Game, minion.ID) for i in range(6)], (minion.pos, "leftandRight"))


class BarrensScavenger(Minion):
	Class, race, name = "Warrior", "", "Barrens Scavenger"
	mana, attack, health = 6, 6, 6
	index = "THE_BARRENS~Warrior~Minion~6~6~6~~Barrens Scavenger~Taunt"
	requireTarget, keyWord, description = False, "Taunt", "Taunt。 Costs(1) while your deck has 10 or fewer cards"
	name_CN = "贫瘠之地拾荒者"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsHand = [Trig_BarrensScavenger(self)]
	
	def selfManaChange(self):
		if self.inHand and len(self.Game.Hand_Deck.decks[self.ID]) < 11:
			self.mana = 1

class Trig_BarrensScavenger(TrigHand):
	def __init__(self, entity):
		super().__init__(entity, [""])
	
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.inHand and ID == self.entity.ID
	
	def text(self, CHN):
		return "每当你的牌库改变，重新计算费用" if CHN else "Whenever your deck changes, recalculate the cost"
	
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.Game.Manas.calcMana_Single(self.entity)


"""Warrior Cards"""
class WarsongEnvoy(Minion):
	Class, race, name = "Warrior", "", "Warsong Envoy"
	mana, attack, health = 1, 1, 3
	index = "THE_BARRENS~Warrior~Minion~1~1~3~~Warsong Envoy~Frenzy"
	requireTarget, keyWord, description = False, "", "Frenzy: Gain +1 Attack for each damaged character"
	name_CN = "战歌大使"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_WarsongEnvoy(self)]

class Trig_WarsongEnvoy(Frenzy):
	def text(self, CHN):
		return "暴怒：每有一个受伤的角色，便获得+1攻击力" if CHN else "Frenzy: Gain +1 Attack for each damaged character"
	
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		num = self.entity.Game.heroes[self.entity.ID]
		num += sum(minion.health < minion.health_max for minion in self.entity.Game.minionsonBoard(self.entity.ID))
		self.entity.buffDebuff(num, 0)
		

class BulkUp(Spell):
	Class, school, name = "Warrior", "", "Bulk Up"
	requireTarget, mana = False, 2
	index = "THE_BARRENS~Warrior~Spell~2~~Bulk Up"
	description = "Give a random Taunt minion in your hand +1/+1 and copy it"
	name_CN = "重装上阵"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		minions = [card for card in self.Game.Hand_Deck.hands[self.ID] if card.type == "Minion" and card.keyWords["Taunt"] > 0]
		if minions:
			minion = npchoice(minions)
			minion.buffDebuff(1, 1)
			self.addCardtoHand(minion.selfCopy(self.ID, self), self.ID)
		return None


class ConditioningRank1(Spell):
	Class, school, name = "Warrior", "", "Conditioning (Rank 1)"
	requireTarget, mana = False, 2
	index = "THE_BARRENS~Warrior~Spell~2~~Conditioning (Rank 1)"
	description = "Give minions in your hand +1/+1. (Upgrades when you have 5 mana.)"
	name_CN = "体格训练（等级1）"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsHand = [Trig_ForgeUpgrade(self, ConditioningRank2, 5)]  #只有在手牌中才会升级
	
	def entersHand(self):
		card = ConditioningRank2(self.Game, self.ID) if self.Game.Manas.manasUpper[self.ID] > 4 else self
		card.inHand = True
		card.onBoard = card.inDeck = False
		card.enterHandTurn = card.Game.numTurn
		for trig in card.trigsHand: trig.connect()
		return card
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		for card in self.Game.Hand_Deck.hands[self.ID]:
			if card.type == "Minion":
				card.buffDebuff(1, 1)
		return None


class ConditioningRank2(Spell):
	Class, school, name = "Warrior", "", "Conditioning (Rank 2)"
	requireTarget, mana = False, 2
	index = "THE_BARRENS~Warrior~Spell~2~~Conditioning (Rank 2)~Uncollectible"
	description = "Give minions in your hand +2/+2. (Upgrades when you have 10 mana.)"
	name_CN = "体格训练（等级2）"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsHand = [Trig_ForgeUpgrade(self, ConditioningRank3, 10)]  #只有在手牌中才会升级
	
	def entersHand(self):
		card = ConditioningRank3(self.Game, self.ID) if self.Game.Manas.manasUpper[self.ID] > 9 else self
		card.inHand = True
		card.onBoard = card.inDeck = False
		card.enterHandTurn = card.Game.numTurn
		for trig in card.trigsHand: trig.connect()
		return card
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		for card in self.Game.Hand_Deck.hands[self.ID]:
			if card.type == "Minion":
				card.buffDebuff(2, 2)
		return None

class ConditioningRank3(Spell):
	Class, school, name = "Warrior", "", "Conditioning (Rank 3)"
	requireTarget, mana = False, 2
	index = "THE_BARRENS~Warrior~Spell~2~~Conditioning (Rank 3)~Uncollectible"
	description = "Give minions in your hand +3/+3"
	name_CN = "体格训练（等级3）"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		for card in self.Game.Hand_Deck.hands[self.ID]:
			if card.type == "Minion":
				card.buffDebuff(3, 3)
		return None


class Rokara(Minion):
	Class, race, name = "Warrior", "", "Rokara"
	mana, attack, health = 3, 2, 3
	index = "THE_BARRENS~Warrior~Minion~3~2~3~~Rokara~Rush~Legendary"
	requireTarget, keyWord, description = False, "Rush", "Rush. After a friendly minion attacks and survives, give it +1/+1"
	name_CN = "洛卡拉"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_Rokara(self)]

class Trig_Rokara(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["MinionAttackedHero", "MinionAttackedMinion"])
	
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject.ID == self.entity.ID and subject.health > 0 and not subject.dead
	
	def text(self, CHN):
		return "在一个友方随从攻击并没有死亡后，使其获得+1/+1" if CHN else "After a friendly minion attacks and survives, give it +1/+1"
	
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.buffDebuff(1, 1)


class OutridersAxe(Weapon):
	Class, name, description = "Warrior", "Outrider's Axe", "After your hero attacks and kills a minion draw a card"
	mana, attack, durability = 4, 3, 3
	index = "THE_BARRENS~Warrior~Weapon~4~3~3~Outrider's Axe"
	name_CN = "先锋战斧"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_OutridersAxe(self)]

class Trig_OutridersAxe(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["HeroAttackedMinion"])
	
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject == self.entity.Game.heroes[self.entity.ID] and self.entity.onBoard and target.type == "Minion" and (target.health < 1 or target.dead)
	
	def text(self, CHN):
		return "在你的英雄攻击并消灭一个随从后，抽一张牌" if CHN else "After your hero attacks and kills a minion draw a card"
	
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.Game.Hand_Deck.drawCard(self.entity.ID)


class WhirlingCombatant(Minion):
	Class, race, name = "Warrior", "", "Whirling Combatant"
	mana, attack, health = 4, 3, 6
	index = "THE_BARRENS~Warrior~Minion~4~3~6~~Whirling Combatant~Frenzy~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry and Frenzy: Deal 1 damage to all other minions"
	name_CN = "旋风争斗者"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_WhirlingCombatant(self)]

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		targets = self.Game.minionsonBoard(self.ID, self) + self.Game.minionsonBoard(3-self.ID)
		self.dealsAOE(targets, [1]*len(targets))
		return None
	
class Trig_WhirlingCombatant(Frenzy):
	def text(self, CHN):
		return "暴怒：对所有其他随从造成1点伤害" if CHN else "Frenzy: Deal 1 damage to all other minions"
	
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		targets = self.entity.Game.minionsonBoard(self.entity.ID, self.entity) + self.entity.Game.minionsonBoard(3 - self.entity.ID)
		self.entity.dealsAOE(targets, [1] * len(targets))


class MorshanElite(Minion):
	Class, race, name = "Warrior", "", "Mor'shan Elite"
	mana, attack, health = 5, 4, 4
	index = "THE_BARRENS~Warrior~Minion~5~4~4~~Mor'shan Elite~Taunt~Battlecry"
	requireTarget, keyWord, description = False, "Taunt", "Taunt. Battlecry: If your hero attacked this turn, summon a copy of this"
	name_CN = "莫尔杉精锐"
	
	def effCanTrig(self):
		self.effectViable = self.Game.Counters.heroAttackTimesThisTurn[self.ID] > 0
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if self.Game.Counters.heroAttackTimesThisTurn[self.ID] > 0:
			minion = self.selfCopy(self.ID, self) if self.onBoard else type(self)(self.Game, self.ID)
			self.summon(minion, self.pos+1)
		return None


class StonemaulAnchorman(Minion):
	Class, race, name = "Warrior", "Pirate", "Stonemaul Anchorman"
	mana, attack, health = 5, 4, 5
	index = "THE_BARRENS~Warrior~Minion~5~4~5~Pirate~Stonemaul Anchorman~Rush~Frenzy"
	requireTarget, keyWord, description = False, "Rush", "Rush. Frenzy: Draw a card"
	name_CN = "石槌掌锚者"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_StonemaulAnchorman(self)]

class Trig_StonemaulAnchorman(Frenzy):
	def text(self, CHN):
		return "暴怒：抽一张牌" if CHN else "Frenzy: Draw a card"
	
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.Game.Hand_Deck.drawCard(self.entity.ID)


class OverlordSaurfang(Minion):
	Class, race, name = "Warrior", "", "Overlord Saurfang"
	mana, attack, health = 7, 5, 4
	index = "THE_BARRENS~Warrior~Minion~7~5~4~~Overlord Saurfang~Battlecry~Legendary"
	requireTarget, keyWord, description = False, "", "Battlecry: Resurrect two friendly Frenzy minions. Deal 1 damage to all other minions"
	name_CN = "萨鲁法尔大王"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		game = self.Game
		minions = [card for card in game.Counters.minionsDiedThisGame[self.ID] if "~Frenzy" in card.index]
		if minions:
			minions = npchoice(minions, min(2, len(minions)), replace=False)
			self.summon([minion(game, self.ID) for minion in minions], (self.pos, "leftandRight"))
		targets = game.minionsonBoard(self.ID, self) + game.minionsonBoard(3-self.ID)
		self.dealsAOE(targets, [1]*len(targets))
		return None


"""Mini expansion set"""
#Neutral cards
class MeetingStone(Minion):
	Class, race, name = "Neutral", "", "Meeting Stone"
	mana, attack, health = 1, 0, 2
	index = "THE_BARRENS~Neutral~Minion~1~0~2~~Meeting Stone"
	requireTarget, keyWord, description = False, "", "At the end of your turn, add a 2/2 Adventurer with random bonus effect to your hand"
	name_CN = "集合石"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_MeetingStone(self)]

class Trig_MeetingStone(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["TurnEnds"])
	
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and ID == self.entity.ID
	
	def text(self, CHN):
		return "在你抽牌后，使抽到的牌消耗生命值，而非法力值" if CHN \
			else "After you draw a card, change its Cost to Health instead of Mana"
	
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.addCardtoHand(npchoice(Adventurers), self.entity.ID)


class DevouringEctoplasm(Minion):
	Class, race, name = "Neutral", "", "Devouring Ectoplasm"
	mana, attack, health = 3, 3, 2
	index = "THE_BARRENS~Neutral~Minion~3~3~2~~Devouring Ectoplasm~Deathrattle"
	requireTarget, keyWord, description = False, "", "Deathrattle: Summon a 2/2 Adventurer with random bonus effect"
	name_CN = "吞噬软浆怪"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.deathrattles = [Summona22RandomAdventurer(self)]

class Summona22RandomAdventurer(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.summon(npchoice(Adventurers)(self.entity.Game, self.entity.ID), self.entity.pos+1)
	
	def text(self, CHN):
		return "亡语：召唤一个2/2并具有随机效果的冒险者" if CHN else "Deathrattle: Summon a 2/2 Adventurer with random bonus effect"


class ArchdruidNaralex(Minion):
	Class, race, name = "Neutral", "", "Archdruid Naralex"
	mana, attack, health = 3, 3, 3
	index = "THE_BARRENS~Neutral~Minion~3~3~3~~Archdruid Naralex~Legendary"
	requireTarget, keyWord, description = False, "", "Dormant for 2 turns. While Dormant, add a Dream card to your hand at the end of your turn"
	name_CN = "大德鲁伊纳拉雷克斯"
	def played(self, target=None, choice=0, mana=0, posinHand=-2, comment=""):
		self.statReset(self.attack_Enchant, self.health_max)
		self.appears(firstTime=True)  #打出时一定会休眠，同时会把Game.minionPlayed变为None
		return None  #没有目标可以返回
	
	def appears(self, firstTime=True):
		self.onBoard = True
		self.inHand = self.inDeck = self.dead = False
		self.enterBoardTurn = self.Game.numTurn
		self.mana = type(self).mana  #Restore the minion's mana to original value.
		self.decideAttChances_base()  #Decide base att chances, given Windfury and Mega Windfury
		#没有光环，目前炉石没有给随从人为添加光环的效果, 不可能在把手牌中获得的扳机带入场上，因为会在变形中丢失
		#The buffAuras/hasAuras will react to this signal.
		if firstTime:  #首次出场时会进行休眠，而且休眠状态会保持之前的随从buff
			self.Game.transform(self, SleepingNaralex(self.Game, self.ID, self), firstTime=True)
		else:  #只有不是第一次出现在场上时才会执行这些函数
			if self.btn:
				self.btn.isPlayed, self.btn.card = True, self
				self.btn.placeIcons()
				self.btn.statChangeAni()
				self.btn.statusChangeAni()
			for aura in self.auras.values(): aura.auraAppears()
			for trig in self.trigsBoard + self.deathrattles: trig.connect()
			self.Game.sendSignal("MinionAppears", self.ID, self, None, 0, comment=firstTime)

class SleepingNaralex(Dormant):
	Class, school, name = "Neutral", "", "Sleeping Naralex"
	description = "Dormant for 2 turns. While Dormant, add a Dream card to your hand at the end of your turn"
	def __init__(self, Game, ID, minionInside=None):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_SleepingNaralex(self)]
		self.minionInside = minionInside
		if minionInside:  #When creating a copy, this is left blank temporarily
			self.Class = minionInside.Class
			self.name = "Dormant " + minionInside.name
			self.description = minionInside.description
			self.index = minionInside.index
	
	def assistCreateCopy(self, Copy):
		Copy.minionInside = self.minionInside.createCopy(Copy.Game)
		Copy.name, Copy.Class, Copy.description = self.name, self.Class, self.description

class Trig_SleepingNaralex(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["TurnStarts", "TurnEnds"])
		self.counter = 2
		self.nextAniWait = True
	
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and ID == self.entity.ID  #会在我方回合开始时进行苏醒
	
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		curGame = self.entity.Game
		if signal.endswith("Ends"):
			self.counter -= 1
			if self.counter < 1:
				#假设唤醒的Imprisoned Vanilla可以携带buff
				curGame.transform(self.entity, self.entity.minionInside, firstTime=False)
				if hasattr(self.entity.minionInside, "awakenEffect"):
					self.entity.minionInside.awakenEffect()
		else: #"TurnStarts"
			self.entity.addCardtoHand(npchoice(DreamCards), self.entity.ID)
			

class MutanustheDevourer(Minion):
	Class, race, name = "Neutral", "Murloc", "Mutanus the Devourer"
	mana, attack, health = 7, 4, 4
	index = "THE_BARRENS~Neutral~Minion~7~4~4~Murloc~Mutanus the Devourer~Battlecry~Legendary"
	requireTarget, keyWord, description = False, "", "Battlecry: Eat a minion in your opponent's hand. Gain its effect"
	name_CN = "吞噬者穆坦努斯"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		enemyHand = self.Game.Hand_Deck.hands[3-self.ID]
		minions = [i for i, card in enumerate(enemyHand) if card.type == "Minion"]
		if minions:
			i = npchoice(minions)
			att, health = enemyHand[i].attack, enemyHand[i].health
			self.Game.Hand_Deck.extractfromDeck(i, self.ID, animate=False)
			self.buffDebuff(att, health)
		return None


class SelflessSidekick(Minion):
	Class, race, name = "Neutral", "", "Selfless Sidekick"
	mana, attack, health = 7, 6, 6
	index = "THE_BARRENS~Neutral~Minion~7~6~6~~Selfless Sidekick~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Equip a random weapon from your deck"
	name_CN = "无私的同伴"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		weapons = [i for i, card in enumerate(self.Game.Hand_Deck.decks[self.ID]) if card.type == "Weapon"]
		if weapons:
			self.Game.equipWeapon(self.Game.Hand_Deck.extractfromDeck(npchoice(weapons), self.ID, animate=False)[0])
		return None


#Demon Hunter
class SigilofSummoning(Spell):
	Class, school, name = "Demon Hunter", "Shadow", "Sigil of Summoning"
	requireTarget, mana = False, 2
	index = "THE_BARRENS~Demon Hunter~Spell~2~Fel~Sigil of Summoning"
	description = "At the start of your next turn, summmon two 2/2 Demons with Taunt"
	name_CN = "召唤咒符"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		SigilofSummoning_Effect(self.Game, self.ID).connect()
		return None

class SigilofSummoning_Effect:
	def __init__(self, Game, ID):
		self.Game, self.ID = Game, ID
		self.card = SigilofSummoning(self.Game, self.ID)
	
	def connect(self):
		if all(not isinstance(trig, SigilofSummoning_Effect) or trig.ID != self.ID for trig in self.Game.turnStartTrigger):
			self.Game.turnStartTrigger.append(self)
			if self.Game.GUI: self.Game.GUI.heroZones[self.ID].addaTrig(self.card)
			
	def turnStartTrigger(self):
		game = self.Game
		if game.GUI: self.Game.GUI.showOffBoardTrig(self.card)
		self.card.summon([WailingDemon(game, self.ID) for i in range(2)], (-1, "totheRightEnd"))
		try: game.turnStartTrigger.remove(self)
		except: pass
		if game.GUI: game.GUI.heroZones[self.ID].removeaTrig(self.card)
	
	def createCopy(self, game):
		if self not in game.copiedObjs:
			trigCopy = type(self)(game, self.ID)
			game.copiedObjs[self] = trigCopy
			return trigCopy
		else: return game.copiedObjs[self]

class WailingDemon(Minion):
	Class, race, name = "Demon Hunter", "Demon", "Wailing Demon"
	mana, attack, health = 2, 2, 2
	index = "THE_BARRENS~Demon Hunter~Minion~2~2~2~Demon~Wailing Demon~Taunt~Uncollectible"
	requireTarget, keyWord, description = False, "Taunt", "Taunt"
	name_CN = "哀嚎恶魔"


class Felrattler(Minion):
	Class, race, name = "Demon Hunter", "Beast", "Felrattler"
	mana, attack, health = 3, 3, 2
	index = "THE_BARRENS~Demon Hunter~Minion~3~3~2~Beast~Felrattler~Rush~Deathrattle"
	requireTarget, keyWord, description = False, "Rush", "Rush. Deathrattle: Deal 1 damage to all enemy minions"
	name_CN = "邪能响尾蛇"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.deathrattles = [Deal1DamagetoEnemyMinions(self)]

class Deal1DamagetoEnemyMinions(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		minion = self.entity
		targets = minion.Game.minionsonBoard(1) + minion.Game.minionsonBoard(2)
		minion.dealsAOE(targets, 1)
		
	def text(self, CHN):
		return "亡语：对所有敌方随从造成1点伤害" if CHN else "Deathrattle: Deal 1 damage to all enemy minions"


class TaintheartTormenter(Minion):
	Class, race, name = "Demon Hunter", "Demon", "Taintheart Tormenter"
	mana, attack, health = 8, 8, 8
	index = "THE_BARRENS~Demon Hunter~Minion~8~8~8~Demon~Taintheart Tormenter~Taunt"
	requireTarget, keyWord, description = False, "Taunt", "Taunt. Your opponent's spells cost (2) more"
	name_CN = "污心拷问者"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.auras["Your opponent's spells cost (2) more"] = ManaAura(self, changeby=+2, changeto=-1)
		
		def manaAuraApplicable(self, subject):
			return subject.ID != self.ID and subject.type == "Spell"


"""Druid Cards"""
class FangboundDruid(Minion):
	Class, race, name = "Druid", "", "Fangbound Druid"
	mana, attack, health = 3, 4, 3
	index = "THE_BARRENS~Druid~Minion~3~4~3~~Fangbound Druid~Taunt~Deathrattle"
	requireTarget, keyWord, description = False, "Taunt", "Taunt. Deathrattle: Reduce the cost of a random Beast in your hand by (2)"
	name_CN = "牙缚德鲁伊"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.deathrattles = [ARandomBeastinYourHandCosts1Less(self)]

class ARandomBeastinYourHandCosts1Less(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		beasts = [card for card in enumerate(self.entity.Game.Hand_Deck.hands[self.entity.ID]) if card.type == "Minion" and "Beast" in card.race]
		if beasts: ManaMod(npchoice(beasts), changeby=-2).applies()
	
	def text(self, CHN):
		return "亡语：使你手牌中的一张野兽牌的法力消耗值减少(2)点" if CHN else "Deathrattle: Reduce the cost of a random Beast in your hand by (2)"


class LadyAnacondra(Minion):
	Class, race, name = "Druid", "", "Lady Anacondra"
	mana, attack, health = 6, 3, 7
	index = "THE_BARRENS~Druid~Minion~6~3~7~~Lady Anacondra~Legendary"
	requireTarget, keyWord, description = False, "", "Your Nature spells cost (2) less"
	name_CN = "安娜康德拉"
	
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.auras["Your Nature spells cost (2) less"] = ManaAura(self, changeby=-2, changeto=-1)
	
	def manaAuraApplicable(self, subject):
		return subject.ID != self.ID and subject.type == "Spell" and subject.school == "Nature"


class DeviateDreadfang(Minion):
	Class, race, name = "Druid", "Beast", "Deviate Dreadfang"
	mana, attack, health = 8, 4, 9
	index = "THE_BARRENS~Druid~Minion~8~4~9~Beast~Deviate Dreadfang"
	requireTarget, keyWord, description = False, "", "After you cast a Nature spell, summon a 4/2 Viper with Rush"
	name_CN = "变异尖牙风蛇"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_DeviateDreadfang(self)]

class Trig_DeviateDreadfang(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["SpellBeenPlayed"])
	
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject.ID == self.entity.ID
	
	def text(self, CHN):
		return "在你使用一张自然法术后，召唤一个4/2并具有突袭的飞蛇" if CHN else "After you cast a Nature spell, summon a 4/2 Viper with Rush"
	
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.summon(DeviateViper(self.entity.Game, self.entity.ID), self.entity.pos+1)
		
class DeviateViper(Minion):
	Class, race, name = "Druid", "Beast", "Deviate Viper"
	mana, attack, health = 3, 4, 2
	index = "THE_BARRENS~Druid~Minion~3~4~2~Beast~Deviate Viper~Rush~Uncollectible"
	requireTarget, keyWord, description = False, "Rush", "Rush"
	name_CN = "变异飞蛇"


"""Hunter cards"""
class Serpentbloom(Spell):
	Class, school, name = "Hunter", "", "Serpentbloom"
	requireTarget, mana = True, 0
	index = "THE_BARRENS~Hunter~Spell~0~~Serpentbloom"
	description = "Give a friendly Beast Poisonous"
	name_CN = "毒蛇花"
	def available(self):
		return self.selectableFriendlyMinionExists()
	
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.ID == self.ID and target.onBoard and "Beast" in target.race
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			target.getsStatus("Poisonous")
		return target


class SindoreiScentfinder(Minion):
	Class, race, name = "Hunter", "", "Sin'dorei Scentfinder"
	mana, attack, health = 4, 1, 6
	index = "THE_BARRENS~Hunter~Minion~4~1~6~~Sin'dorei Scentfinder~Frenzy"
	requireTarget, keyWord, description = False, "", "Frenzy: Summon four 1/1 Hyenas with Rush"
	name_CN = "辛多雷气味猎手"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_SindoreiScentfinder(self)]

class Trig_SindoreiScentfinder(Frenzy):
	def text(self, CHN):
		return "暴怒：召唤四只1/1并具有突袭的土狼" if CHN else "Frenzy: Summon four 1/1 Hyenas with Rush"
	
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		minion = self.entity
		minion.summon([SwiftHyena(minion.Game, minion.ID) for i in range(4)], (minion.pos, "leftandRight"))


class VenomstrikeBow(Weapon):
	Class, name, description = "Hunter", "Venomstrike Bow", "Poisonous"
	mana, attack, durability = 4, 1, 2
	index = "THE_BARRENS~Hunter~Weapon~4~1~2~Venomstrike Bow~Poisonous"
	name_CN = "毒袭之弓"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.keyWords["Poisonous"] = 1


"""Mage cards"""
class FrostweaveDungeoneer(Minion):
	Class, race, name = "Mage", "", "Frostweave Dungeoneer"
	mana, attack, health = 3, 2, 3
	index = "THE_BARRENS~Mage~Minion~3~2~3~~Frostweave Dungeoneer~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Draw a spell. If it's a Frost spell, summon two 1/1 Elementals that Freeze"
	name_CN = "织霜地下城历险家"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		spells = [i for i, card in enumerate(self.Game.Hand_Deck.decks[self.ID]) if card.type == "Spell"]
		if spells:
			spell = self.Game.Hand_Deck.drawCard(self.ID, npchoice(spells))[0]
			if spell and spell.school == "Frost":
				pos = (self.pos, "leftandRight") if self.onBoard else (-1, "totheRightEnd")
				self.summon([FrostedElemental(self.Game, self.ID) for i in range(2)], pos)
		return None


class ShatteringBlast(Spell):
	Class, school, name = "Mage", "Frost", "Shattering Blast"
	requireTarget, mana = False, 3
	index = "THE_BARRENS~Mage~Spell~3~Frost~Shattering Blast"
	description = "Destroy all Frozen minions"
	name_CN = "冰爆冲击"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		targets = [minion for minion in self.Game.minionsonBoard(1) + self.Game.minionsonBoard(2)]
		self.Game.killMinion(self, targets)
		

class Floecaster(Minion):
	Class, race, name = "Mage", "", "Floecaster"
	mana, attack, health = 6, 5, 5
	index = "THE_BARRENS~Mage~Minion~6~5~5~~Floecaster"
	requireTarget, keyWord, description = False, "", "Costs (2) less for each Frozen enemy"
	name_CN = "浮冰施法者"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsHand = [Trig_Floecaster(self)]
	
	def selfManaChange(self):
		if self.inHand:
			num = sum(char.status["Frozen"] > 0 for char in self.Game.minionsonBoard(3-self.ID))
			if self.Game.heroes[3-self.ID].status["Frozen"] > 0: num += 1
			self.mana -= num
			self.mana = max(0, self.mana)

class Trig_Floecaster(TrigHand):
	def __init__(self, entity):
		super().__init__(entity, ["MinionAppears", "MinionDisappears", "CharGets_Frozen"])
	
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.inHand and ID != self.entity.ID
	
	def text(self, CHN):
		return "每当受伤随从的数量变化，重新计算该随从的费用" if CHN \
			else "When number of damaged minions change, recalculate mana"
	
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.Game.Manas.calcMana_Single(self.entity)


class JudgmentofJustice(Secret):
	Class, school, name = "Paladin", "Holy", "Judgment of Justice"
	requireTarget, mana = False, 1
	index = "THE_BARRENS~Paladin~Spell~1~Holy~Judgment of Justice~~Secret"
	description = "Secret: When an enemy minion attacks, set its Attack and Health to 1"
	name_CN = "公正审判"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_JudgmentofJustice(self)]

class Trig_JudgmentofJustice(SecretTrigger):
	def __init__(self, entity):
		super().__init__(entity, ["MinionAttackingMinion", "MinionAttackingHero"])
	
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.ID != self.entity.Game.turn and subject.ID != self.entity.ID
	
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		subject.statReset(1, 1)
		

class SeedcloudBuckler(Weapon):
	Class, name, description = "Paladin", "Seedcloud Buckler", "Deathrattle: Give your minions Divine Shield"
	mana, attack, durability = 3, 2, 3
	index = "THE_BARRENS~Paladin~Weapon~3~2~3~Seedcloud Buckler~Deathrattle"
	name_CN = "淡云圆盾"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.deathrattles = [GiveYourMinionsDivineShield(self)]

class GiveYourMinionsDivineShield(Deathrattle_Weapon):
	def text(self, CHN):
		return "亡语：使你的所有随从获得圣盾" if CHN else "Deathrattle: Give your minions Divine Shield"
	
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		for minion in self.entity.Game.minionsonBoard(self.entity.ID):
			minion.getsStatus("Divine Shield")


class PartyUp(Spell):
	Class, school, name = "Paladin", "", "Party Up!"
	requireTarget, mana = False, 7
	index = "THE_BARRENS~Paladin~Spell~7~~Party Up!"
	description = "Summon five 2/2 Adventurers with random bonus effects"
	name_CN = "小队集合"
	def available(self):
		return self.Game.space(self.ID) > 0
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.summon([minion(self.Game, self.ID) for minion in npchoice(Adventurers, 5, replace=True)], (-1, "totheRightEnd"))
		return None


#Priest cards
class ClericofAnshe(Minion):
	Class, race, name = "Priest", "", "Cleric of An'she"
	mana, attack, health = 1, 1, 2
	index = "THE_BARRENS~Priest~Minion~1~1~2~~Cleric of An'she~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: If you've restored Health this turn, Discover a spell from your deck"
	name_CN = "安瑟教士"

	def effCanTrig(self):
		self.effectViable = self.Game.Counters.healthRestoredThisTurn[self.ID] > 0

	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if self.Game.Counters.healthRestoredThisTurn[self.ID] > 0:
			self.discoverfromList(ClericofAnshe, comment, conditional=lambda card: card.type == "Spell",
								  ls=self.Game.Hand_Deck.decks[self.ID])
		return None
	
	def discoverDecided(self, option, case, info_RNGSync=None, info_GUISync=None):
		self.handleDiscoveredCardfromList(option, case, ls=self.Game.Hand_Deck.decks[self.ID],
										  func=lambda index, card: self.Game.Hand_Deck.drawCard(self.ID, index),
										  info_RNGSync=info_RNGSync, info_GUISync=info_GUISync)
		

class DevoutDungeoneer(Minion):
	Class, race, name = "Priest", "", "Devout Dungeoneer"
	mana, attack, health = 3, 2, 3
	index = "THE_BARRENS~Priest~Minion~3~2~3~~Devout Dungeoneer~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Draw a spell. If it's a Holy spell, reduce its Cost by (2)"
	name_CN = "虔诚地下城历险家"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		spells = [i for i, card in enumerate(self.Game.Hand_Deck.decks[self.ID]) if card.type == "Spell"]
		if spells:
			spell = self.Game.Hand_Deck.drawCard(self.ID, npchoice(spells))[0]
			if spell and spell.school == "Holy": ManaMod(spell, changeby=-2).applies()
		return None


class AgainstAllOdds(Spell):
	Class, school, name = "Priest", "Holy", "Against All Odds"
	requireTarget, mana = False, 5
	index = "THE_BARRENS~Priest~Spell~5~Holy~Against All Odds"
	description = "Destroy ALL odd-Attack minions"
	name_CN = "除奇致胜"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		targets = [minion for minion in self.Game.minionsonBoard(1) + self.Game.minionsonBoard(2) if minion.attack % 2 == 1]
		if targets: self.Game.killMinion(self, targets)
		return None


#Rogue cards
class SavoryDeviateDelight(Spell):
	Class, school, name = "Rogue", "", "Savory Deviate Delight"
	requireTarget, mana = False, 1
	index = "THE_BARRENS~Rogue~Spell~1~~Savory Deviate Delight"
	description = "Transform a minion in both players' hands into a Pirate or Stealth minion"
	name_CN = "美味风蛇"
	poolIdentifier = "Pirates"
	@classmethod
	def generatePool(cls, pools):
		pirates = pools.MinionswithRace["Pirate"]
		stealthMinions = []
		for minions in pools.MinionsofCost.values(): #pool here is still a dict 1: {index: cls}
			stealthMinions += [minion for minion in minions if "Stealth" in minion.keyWord]
		return ["Pirates", "Stealth Minions"], [pirates, stealthMinions]
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		game = self.Game
		if game.mode == 0:
			pool = self.rngPool("Pirates") + self.rngPool("Stealth Minions")
			minions1 = [i for i, card in enumerate(game.Hand_Deck.hands[1]) if card.type == "Minion"]
			minions2 = [i for i, card in enumerate(game.Hand_Deck.hands[2]) if card.type == "Minion"]
			if minions1: i, minion1 = npchoice(minions1), npchoice(pool)
			else: i, minion1 = -1, None
			if minions2: j, minion2 = npchoice(minions2), npchoice(pool)
			else: j, minion2 = -1, None
			if i > -1: self.transform(game.Hand_Deck.hands[1][i], minion1(game, 1))
			if j > -1: self.transform(game.Hand_Deck.hands[2][j], minion2(game, 2))
		return None


class WaterMoccasin(Minion):
	Class, race, name = "Rogue", "Beast", "Water Moccasin"
	mana, attack, health = 3, 2, 5
	index = "THE_BARRENS~Rogue~Minion~3~2~5~Beast~Water Moccasin~Stealth"
	requireTarget, keyWord, description = False, "Stealth", "Stealth. Has Poisonous while you have no other minions"
	name_CN = "水栖蝮蛇"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.auras["Has Aura"] = HasAura_WaterMoccasin(self)

class HasAura_WaterMoccasin:
	def __init__(self, entity):
		self.entity = entity
		self.auraAffected = []
		self.on = False
	
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject.ID == self.entity.ID and subject != self
	
	def trig(self, signal, ID, subject, target, number, comment, choice=0):
		minion = self.entity
		otherMinions = minion.Game.minionsonBoard(minion.ID, minion)
		if otherMinions and self.on:
			self.on = False
			for recipient, receiver in self.auraAffected[:]:
				receiver.effectClear()
			self.auraAffected = []
		elif not otherMinions and not self.on:
			self.on = True
			Effect_Receiver(minion, self, "Poisonous").effectStart()
	
	def auraAppears(self):
		minion = self.entity
		if not minion.Game.minionsonBoard(minion.ID, minion):
			self.on = True
			Effect_Receiver(minion, self, "Poisonous")
		for sig in ("MinionAppears", "MinionDisappears"):
			try: minion.Game.trigsBoard[minion.ID][sig].append(self)
			except: minion.Game.trigsBoard[minion.ID][sig] = [self]
	
	def auraDisappears(self):
		for minion, receiver in self.auraAffected[:]:
			receiver.effectClear()
		self.auraAffected = []
		for sig in ("MinionAppears", "MinionDisappears"):
			try: self.entity.Game.trigsBoard[self.entity.ID][sig].remove(self)
			except: pass
	
	def selfCopy(self, recipient):  #The recipientMinion is the minion that deals the Aura.
		return type(self)(recipient)
	
	def createCopy(self, game):
		if self not in game.copiedObjs:  #这个光环没有被复制过
			entityCopy = self.entity.createCopy(game)
			Copy = self.selfCopy(entityCopy)
			game.copiedObjs[self] = Copy
			Copy.on = self.on
			for minion, receiver in self.auraAffected:
				minionCopy = minion.createCopy(game)
				index = minion.auraReceivers.index(receiver)
				receiverCopy = minionCopy.auraReceivers[index]
				receiverCopy.source = Copy  #补上这个receiver的source
				Copy.auraAffected.append((minionCopy, receiverCopy))
			return Copy
		else:
			return game.copiedObjs[self]


class ShroudofConcealment(Spell):
	Class, school, name = "Rogue", "Shadow", "Shroud of Concealment"
	requireTarget, mana = False, 3
	index = "THE_BARRENS~Rogue~Spell~3~Shadow~Shroud of Concealment"
	description = "Draw 2 minions. Any played this turn gain Stealth for 1 turn"
	name_CN = "潜行帷幕"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		minionsDrawn = []
		for num in range(2):
			minions = [i for i, card in enumerate(self.Game.Hand_Deck.decks[self.ID]) if card.type == "Minion"]
			if minions:
				card = self.Game.Hand_Deck.drawCard(self.ID, npchoice(minions))[0]
				if card: minionsDrawn.append(card)
		if minionsDrawn: ShroudofConcealment_Effect(self.Game, self.ID, minionsDrawn).connect()
		return None
	
class ShroudofConcealment_Effect:
	def __init__(self, Game, ID, cardsDrawn):
		self.Game, self.ID = Game, ID
		self.card = ShroudofConcealment(Game, ID)
		#Assume the trig is after the card is played
		self.signals = ["MinionBeenPlayed"]
		self.cardsDrawn = cardsDrawn
	
	def connect(self):
		try: self.Game.trigsBoard[self.ID]["MinionBeenPlayed"].append(self)
		except: self.Game.trigsBoard[self.ID]["MinionBeenPlayed"] = [self]
		self.Game.turnEndTrigger.append(self)
		if self.Game.GUI: self.Game.GUI.heroZones[self.ID].addaTrig(self.card)
	
	def disconnect(self):
		try: self.Game.trigsBoard[self.ID]["MinionBeenPlayed"].remove(self)
		except: pass
		try: self.Game.turnEndTrigger.remove(self)
		except: pass
		if self.Game.GUI: self.Game.GUI.heroZones[self.ID].removeaTrig(self.card)
	
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject.ID == self.ID and subject in self.cardsDrawn
	
	def trig(self, signal, ID, subject, target, number, comment, choice=0):
		if self.canTrig(signal, ID, subject, target, number, comment):
			if self.Game.GUI: self.Game.GUI.showOffBoardTrig(self.card)
			self.effect(signal, ID, subject, target, number, comment)
	
	def text(self, CHN):
		return "如果你使用了空翻杂技抽到的两张牌，则可以再抽两张" if CHN else "If you use the two cards drawn by Acrobatics, draw 2 more"
	
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		subject.getsStatus("Temp Stealth")
		self.disconnect()
	
	def turnEndTrigger(self):
		self.disconnect()
	
	def createCopy(self, game):  #不是纯的只在回合结束时触发，需要完整的createCopy
		if self not in game.copiedObjs:  #这个扳机没有被复制过
			trigCopy = type(self)(game, self.ID, [])
			trigCopy.cardsDrawn = [card.createCopy(game) for card in self.cardsDrawn]
			game.copiedObjs[self] = trigCopy
			return trigCopy
		else:  #一个扳机被复制过了，则其携带者也被复制过了
			return game.copiedObjs[self]
	

#Shaman cards
class PerpetualFlame(Spell):
	Class, school, name = "Shaman", "Fire", "Perpetual Flame"
	requireTarget, mana = False, 1
	index = "THE_BARRENS~Shaman~Spell~1~Fire~Perpetual Flame~Overload"
	description = "Deal 3 damage to a random enemy minion. If it dies, recast this. Overload: (1)"
	name_CN = "永恒之火"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.overload = 1
	
	def text(self, CHN):
		damage = (3 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		return "随机对一个敌方随从造成%d点伤害。如果该随从死亡，则再次施放此法术"%damage if CHN else "Deal %d damage to a random enemy minion. If it dies, recast this. Overload: (1)"%damage
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		damage = (3 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		while True:
			targets = self.Game.minionsAlive(3 - self.ID)
			if targets:
				minion = npchoice(targets)
				self.dealsDamage(minion, damage)
				if not minion.dead and minion.health > 0: break
		return None


class WailingVapor(Minion):
	Class, race, name = "Shaman", "Elemental", "Wailing Vapor"
	mana, attack, health = 1, 1, 3
	index = "THE_BARRENS~Shaman~Minion~1~1~3~Elemental~Wailing Vapor"
	requireTarget, keyWord, description = False, "", "After you play an Elemental, gain +1 Attack"
	name_CN = "哀嚎蒸汽"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_WailingVapor(self)]
	
class Trig_WailingVapor(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["MinionBeenPlayed"])
	
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject.ID == self.entity.ID and subject != self.entity
	
	def text(self, CHN):
		return "在你使用一张元素牌后，获得+1攻击力" if CHN else "After you play an Elemental, gain +1 Attack"
	
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.buffDebuff(1, 0)


class PrimalDungeoneer(Minion):
	Class, race, name = "Shaman", "", "Primal Dungeoneer"
	mana, attack, health = 3, 2, 3
	index = "THE_BARRENS~Shaman~Minion~3~2~3~~Primal Dungeoneer~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Draw a spell. If it's a Nature spell, draw an Elemental"
	name_CN = "原初地下城历险家"

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		ownDeck = self.Game.Hand_Deck.decks[self.ID]
		spells = [i for i, card in enumerate(ownDeck) if card.type == "Spell"]
		if spells:
			spell = self.Game.Hand_Deck.drawCard(self.ID, npchoice(spells))[0]
			if spell and spell.school == "Nature":
				elementals = [i for i, card in enumerate(ownDeck) if card.type == "Minion" and "Elemental" in card.race]
				if elementals: self.Game.Hand_Deck.drawCard(self.ID, npchoice(elementals))
		return None


#Warlock cards
class FinalGasp(Spell):
	Class, school, name = "Warlock", "Shadow", "Final Gasp"
	requireTarget, mana = True, 1
	index = "THE_BARRENS~Warlock~Spell~1~Shadow~Final Gasp"
	description = "Deal 1 damage to a minion. If it dies, summon a 2/2 Adventurer with random bonus effect"
	name_CN = "临终之息"
	def available(self):
		return self.selectableMinionExists()
	
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
	
	def text(self, CHN):
		damage = (1 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		return "对一个随从造成%d点伤害。如果该随从死亡，召唤一个2/2并具有随从效果的冒险者"%damage if CHN \
			else "Deal %d damage to a minion. If it dies, summon a 2/2 Adventurer with random bonus effect"%damage
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if target:
			damage = (1 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			self.dealsDamage(target, damage)
			if target.dead or target.health < 0: self.summon(npchoice(Adventurers)(self.Game, self.ID), -1)
		return target


class UnstableShadowBlast(Spell):
	Class, school, name = "Warlock", "Shadow", "Unstable Shadow Blast"
	requireTarget, mana = True, 2
	index = "THE_BARRENS~Warlock~Spell~2~Shadow~Unstable Shadow Blast"
	description = "Deal 6 damage to a minion. Excess damage hits your hero"
	name_CN = "不稳定的暗影震爆"
	def available(self):
		return self.selectableMinionExists()
	
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
	
	def text(self, CHN):
		damage = (6 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		return "对一个随从造成%d点伤害。超过目标生命值的伤害会命中你的英雄" % damage if CHN \
			else "Deal %d damage to a minion. Excess damage hits your hero" % damage
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if target:
			totalDamage = (6 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			realDamage = max(target.health, 0)
			excessDamage = totalDamage - realDamage
			self.dealsDamage(target, realDamage)
			if excessDamage > 0: self.dealsDamage(self.Game.heroes[self.ID], excessDamage)
		return target


class StealerofSouls(Minion):
	Class, race, name = "Warlock", "Demon", "Stealer of Souls"
	mana, attack, health = 4, 2, 6
	index = "THE_BARRENS~Warlock~Minion~4~2~6~Demon~Stealer of Souls"
	requireTarget, keyWord, description = False, "", "After you draw a card, change its Cost to Health instead of Mana"
	name_CN = "灵魂窃者"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_StealerofSouls(self)]

class Trig_StealerofSouls(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["CardEntersHand"])
	
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and target[0].ID == self.entity.ID and comment == "byDrawing"
	
	def text(self, CHN):
		return "在你抽牌后，使抽到的牌消耗生命值，而非法力值" if CHN \
			else "After you draw a card, change its Cost to Health instead of Mana"
	
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		target[0].getsStatus("Cost Health Instead")
		
		
#Warrior cards
class ManatArms(Minion):
	Class, race, name = "Warrior", "", "Man-at-Arms"
	mana, attack, health = 2, 2, 3
	index = "THE_BARRENS~Warrior~Minion~2~2~3~~Man-at-Arms~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: If you have a weapon equipped, gain +1/+1"
	name_CN = "武装战士"


class WhetstoneHatchet(Weapon):
	Class, name, description = "Warrior", "Whetstone Hatchet", "After your hero attack, give a minion in your hand +1 Attack"
	mana, attack, durability = 1, 1, 4
	index = "THE_BARRENS~Warrior~Weapon~1~1~4~Whetstone Hatchet"
	name_CN = "砥石战斧"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_WhetstoneHatchet(self)]

class Trig_WhetstoneHatchet(TrigBoard):
	def __init__(self, entity):
		super().__init__(entity, ["HeroAttackedMinion", "HeroAttackedHero"])
	
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject == self.entity.Game.heroes[self.entity.ID] and self.entity.onBoard
	
	def text(self, CHN):
		return "在你的英雄攻击后，使你手牌中的一张随从牌获得+1攻击力" if CHN else "After your hero attack, give a minion in your hand +1 Attack"
	
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		minions = [card for card in self.entity.Game.Hand_Deck.hands[self.entity.ID] if card.type == "Minion"]
		if minions: npchoice(minions).buffDebuff(1, 0)
		

class KreshLordofTurtling(Minion):
	Class, race, name = "Warrior", "Beast", "Kresh, Lord of Turtling"
	mana, attack, health = 6, 3, 9
	index = "THE_BARRENS~Warrior~Minion~6~3~9~Beast~Kresh, Lord of Turtling~Frenzy~Deathrattle"
	requireTarget, keyWord, description = False, "", "Frenzy: Gain 8 Armor. Deathrattle: Equip a 2/5 Turtle Spike"
	name_CN = "克雷什，群龟之王"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.trigsBoard = [Trig_KreshLordofTurtling(self)]
		self.deathrattles = [EquipTurtleSpike(self)]

class Trig_KreshLordofTurtling(Frenzy):
	def text(self, CHN):
		return "暴怒：获得8点护甲值" if CHN else "Frenzy: Gain 8 Armor"
	
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.Game.heroes[self.entity.ID].gainsArmor(8)

class EquipTurtleSpike(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.equipWeapon(TurtleSpike(self.entity.Game, self.entity.ID))
		
	def text(self, CHN):
		return "亡语：装备一把2/5的龟甲尖刺" if CHN else "Deathrattle: Equip a 2/5 Turtle Spike"

class TurtleSpike(Weapon):
	Class, name, description = "Warrior", "Turtle Spike", ""
	mana, attack, durability = 4, 2, 5
	index = "THE_BARRENS~Warrior~Weapon~4~2~5~Turtle Spike~Uncollectible"
	name_CN = "龟甲尖刺"


Barrens_Cards = [#Neutral cards
				KindlingElemental, FarWatchPost, HecklefangHyena, LushwaterMurcenary, LushwaterScout, OasisThrasher, Peon, TalentedArcanist, ToadoftheWilds, BarrensTrapper, CrossroadsGossiper, DeathsHeadCultist, HogRancher, Hog,
				HordeOperative, Mankrik, OlgraMankriksWife, MankrikConsumedbyHatred, MorshanWatchPost, WatchfulGrunt, RatchetPrivateer, SunwellInitiate, VenomousScorpid, BlademasterSamuro, CrossroadsWatchPost, DarkspearBerserker, GruntledPatron,
				InjuredMarauder, KazakusGolemShaper, SouthseaScoundrel, SpiritHealer, BarrensBlacksmith, BurningBladeAcolyte, Demonspawn, GoldRoadGrunt, RazormaneRaider, ShadowHunterVoljin, TaurajoBrave, KargalBattlescar, Lookout, PrimordialProtector,
				#Demon Hunter cards
				FuryRank1, FuryRank2, FuryRank3, Tuskpiercer, Razorboar, SigilofFlame, SigilofSilence, VileCall, RavenousVilefiend, RazorfenBeastmaster, KurtrusAshfallen, VengefulSpirit, DeathSpeakerBlackthorn,
				#Druid cards
				LivingSeedRank1, LivingSeedRank2, LivingSeedRank3, MarkoftheSpikeshell, RazormaneBattleguard, ThorngrowthSentries, ThornguardTurtle, GuffRunetotem, PlaguemawtheRotting, PridesFury, ThickhideKodo, CelestialAlignment, DruidofthePlains, DruidofthePlains_Taunt,
				#Hunter cards
				SunscaleRaptor, WoundPrey, SwiftHyena, KolkarPackRunner, ProspectorsCaravan, TameBeastRank1, TameBeastRank2, TameBeastRank3, TamedCrab, TamedScorpid, TamedThunderLizard, PackKodo, TavishStormpike, PiercingShot, WarsongWrangler, BarakKodobane,
				#Mage cards
				FlurryRank1, FlurryRank2, FlurryRank3, RunedOrb, Wildfire, ArcaneLuminary, OasisAlly, Rimetongue, FrostedElemental, RecklessApprentice, RefreshingSpringWater, VardenDawngrasp, MordreshFireEye,
				#Paladin cards
				ConvictionRank1, ConvictionRank2, ConvictionRank3, GallopingSavior, HolySteed, KnightofAnointment, SoldiersCaravan, SwordoftheFallen, NorthwatchCommander, CarielRoame, VeteranWarmedic, BattlefieldMedic, InvigoratingSermon, CannonmasterSmythe, NorthwatchSoldier,
				#Priest cards
				DesperatePrayer, CondemnRank1, CondemnRank2, CondemnRank3, SerenaBloodfeather, SoothsayersCaravan, DevouringPlague, VoidFlayer, Xyrella, PriestofAnshe, LightshowerElemental, PowerWordFortitude,
				#Rogue cards
				ParalyticPoison, Yoink, EfficientOctobot, SilverleafPoison, WickedStabRank1, WickedStabRank2, WickedStabRank3, FieldContact, SwinetuskShank, ApothecaryHelbrim, OilRigAmbusher, ScabbsCutterbutter,
				#Shaman cards
				SpawnpoolForager, DiremuckTinyfin, ChainLightningRank1, ChainLightningRank2, ChainLightningRank3, FiremancerFlurgl, SouthCoastChieftain, TinyfinsCaravan, AridStormer, NofinCanStopUs, Brukan, EarthRevenant, LilypadLurker,
				#Warlock cards
				AltarofFire, GrimoireofSacrifice, ApothecarysCaravan, ImpSwarmRank1, ImpFamiliar, ImpSwarmRank2, ImpSwarmRank3, BloodShardBristleback, KabalOutfitter, TamsinRoame, SoulRend, NeeruFireblade, BarrensScavenger,
				#Warrior cards
				WarsongEnvoy, BulkUp, ConditioningRank1, ConditioningRank2, ConditioningRank3, Rokara, OutridersAxe, WhirlingCombatant, MorshanElite, StonemaulAnchorman, OverlordSaurfang,
				
				#Mini expansion set
				MeetingStone, DevouringEctoplasm, ArchdruidNaralex, MutanustheDevourer, SelflessSidekick, SigilofSummoning, WailingDemon, Felrattler, TaintheartTormenter,
				FangboundDruid, LadyAnacondra, DeviateDreadfang, DeviateViper, Serpentbloom, SindoreiScentfinder, VenomstrikeBow,
				FrostweaveDungeoneer, ShatteringBlast, Floecaster, JudgmentofJustice, SeedcloudBuckler, PartyUp, ClericofAnshe, DevoutDungeoneer, AgainstAllOdds,
				SavoryDeviateDelight, WaterMoccasin, ShroudofConcealment, PerpetualFlame, WailingVapor, PrimalDungeoneer, FinalGasp, UnstableShadowBlast, StealerofSouls,
				ManatArms, WhetstoneHatchet, KreshLordofTurtling, TurtleSpike,
				]

Barrens_Cards_Collectible = [#Neutral
							KindlingElemental, FarWatchPost, HecklefangHyena, LushwaterMurcenary, LushwaterScout, OasisThrasher, Peon, TalentedArcanist, ToadoftheWilds, BarrensTrapper, CrossroadsGossiper, DeathsHeadCultist, HogRancher, HordeOperative,
							Mankrik, MorshanWatchPost, RatchetPrivateer, SunwellInitiate, VenomousScorpid, BlademasterSamuro, CrossroadsWatchPost, DarkspearBerserker, GruntledPatron, InjuredMarauder, KazakusGolemShaper, SouthseaScoundrel, SpiritHealer,
							BarrensBlacksmith, BurningBladeAcolyte, GoldRoadGrunt, RazormaneRaider, ShadowHunterVoljin, TaurajoBrave, KargalBattlescar, PrimordialProtector,
							#Demon Hunter
							FuryRank1, Tuskpiercer, Razorboar, SigilofFlame, SigilofSilence, VileCall, RazorfenBeastmaster, KurtrusAshfallen, VengefulSpirit, DeathSpeakerBlackthorn,
							#Druid
							LivingSeedRank1, MarkoftheSpikeshell, RazormaneBattleguard, ThorngrowthSentries, GuffRunetotem, PlaguemawtheRotting, PridesFury, ThickhideKodo, CelestialAlignment, DruidofthePlains,
							#Hunter
							SunscaleRaptor, WoundPrey, KolkarPackRunner, ProspectorsCaravan, TameBeastRank1, PackKodo, TavishStormpike, PiercingShot, WarsongWrangler, BarakKodobane,
							#Mage
							FlurryRank1, RunedOrb, Wildfire, ArcaneLuminary, OasisAlly, Rimetongue, RecklessApprentice, RefreshingSpringWater, VardenDawngrasp, MordreshFireEye,
							#Paladin
							ConvictionRank1, GallopingSavior, KnightofAnointment, SoldiersCaravan, SwordoftheFallen, NorthwatchCommander, CarielRoame, VeteranWarmedic, InvigoratingSermon, CannonmasterSmythe,
							#Priest
							DesperatePrayer, CondemnRank1, SerenaBloodfeather, SoothsayersCaravan, DevouringPlague, VoidFlayer, Xyrella, PriestofAnshe, LightshowerElemental, PowerWordFortitude,
							#Rogue
							ParalyticPoison, Yoink, EfficientOctobot, SilverleafPoison, WickedStabRank1, FieldContact, SwinetuskShank, ApothecaryHelbrim, OilRigAmbusher, ScabbsCutterbutter,
							#Shaman
							SpawnpoolForager, ChainLightningRank1, FiremancerFlurgl, SouthCoastChieftain, TinyfinsCaravan, AridStormer, NofinCanStopUs, Brukan, EarthRevenant, LilypadLurker,
							#Warlock
							AltarofFire, GrimoireofSacrifice, ApothecarysCaravan, ImpSwarmRank1, BloodShardBristleback, KabalOutfitter, TamsinRoame, SoulRend,
							#Warrior
							NeeruFireblade, BarrensScavenger, WarsongEnvoy, BulkUp, ConditioningRank1, Rokara, OutridersAxe, WhirlingCombatant, MorshanElite, StonemaulAnchorman, OverlordSaurfang,
							#Miniset
							#Neutral
							MeetingStone, DevouringEctoplasm, ArchdruidNaralex, MutanustheDevourer, SelflessSidekick,
							#Class cards
							SigilofSummoning, Felrattler, TaintheartTormenter, FangboundDruid, LadyAnacondra, DeviateDreadfang, Serpentbloom, SindoreiScentfinder, VenomstrikeBow,
							FrostweaveDungeoneer, ShatteringBlast, Floecaster, JudgmentofJustice, SeedcloudBuckler, PartyUp, ClericofAnshe, DevoutDungeoneer, AgainstAllOdds, SavoryDeviateDelight, WaterMoccasin, ShroudofConcealment,
							PerpetualFlame, WailingVapor, PrimalDungeoneer, FinalGasp, UnstableShadowBlast, StealerofSouls, ManatArms, WhetstoneHatchet, KreshLordofTurtling,
							]