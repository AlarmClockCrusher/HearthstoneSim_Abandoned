from CardTypes import *
from Triggers_Auras import *
from VariousHandlers import *

from Basic import Claw, ArcaneMissiles, TruesilverChampion
from Shadows import EtherealLackey, FacelessLackey, GoblinLackey, KoboldLackey, WitchyLackey
from Uldum import TitanicLackey

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
	
def classforDiscover(initiator):
	Class = initiator.Game.heroes[initiator.ID].Class
	if Class != "Neutral": return Class #如果发现的发起者的职业不是中立，则返回那个职业
	elif initiator.Class != "Neutral": return initiator.Class #如果玩家职业是中立，但卡牌职业不是中立，则发现以那个卡牌的职业进行
	else: return npchoice(initiator.Game.Classes) #如果玩家职业和卡牌职业都是中立，则随机选取一个职业进行发现。
	
#迦拉克隆通常不能携带多张，但是如果起始卡组中有多张的话，则尽量选择与玩家职业一致的迦拉克隆为主迦拉克隆；如果不能如此，则第一个检测到的为主迦拉克隆
#迦拉克隆如果被变形为其他随从，（通过咒术师等），只要对应卡的职业有迦拉克隆，会触发那个新职业的迦拉克隆的效果。
#视频链接https://www.bilibili.com/video/av80010478?from=search&seid=3438568171430047785
#迦拉克隆只有在我方这边的时候被祈求才能升级，之前的祈求对于刚刚从对方那里获得的迦拉克隆复制没有升级作用。
#牧师的迦拉克隆被两个幻术师先变成贼随从然后变成中立随从，祈求不再生效。
#牧师的加拉克隆被两个幻术师先变成中立随从，然后变成萨满随从，祈求会召唤2/1元素。
#牧师的迦拉克隆被一个幻术师变成中立 随从，然后从对方手牌中偷到术士的迦拉克隆，然后祈求没有任何事情发生。变身成为术士迦拉克隆之后主迦拉克隆刷新成为术士的迦拉克隆。
#不管迦拉克隆的技能有没有被使用过，祈求都会让技能生效。

#假设主迦拉克隆只有在使用迦拉克隆变身的情况下会重置。
#假设主迦拉克隆变成加基森三职业卡时，卡扎库斯视为牧师卡，艾雅黑掌视为盗贼卡，唐汉古视为战士卡
#不知道挖宝把迦拉克隆变成其他牌的话,主迦拉克隆是否会发生变化。
def invokeGalakrond(Game, ID):
	PRINT(Game, "Invoking Galakrond upgrades all of player's Galakronds")
	primaryGalakrond = Game.Counters.primaryGalakronds[ID]
	if primaryGalakrond:
		PRINT(Game, "Primary Galakrond of player %d is %s"%(ID, primaryGalakrond.name))
		Class = primaryGalakrond.Class
		PRINT(Game, "Class of Primary Galakrond of player is %s"%Class)
		if "Priest" in Class:
			if Game.mode == 0:
				if Game.guides and Game.guides[0][1] == "Priest Invoke":
					minion = Game.guides.pop(0)
				else:
					minion = npchoice(Game.RNGPools["Priest Minions"])
					Game.fixedGuides.append(minion)
				PRINT(Game, "On Invocation, Galakrond adds a random Priest minion to player's hand")
				Game.Hand_Deck.addCardtoHand(minion, ID, "CreateUsingType")
		elif "Rogue" in Class:
			if Game.mode == 0:
				if Game.guides and Game.guides[0][1] == "Rogue Invoke":
					lackey = Game.guides.pop(0)
				else:
					lackey = npchoice(Lackeys)
					Game.fixedGuides.append(lackey)
			PRINT(Game, "On Invocation, Galakrond adds a Lackey to player's hand")
			Game.Hand_Deck.addCardtoHand(lackey, ID, "CreateUsingType")
		elif "Shaman" in Class:
			PRINT(Game, "On Invocation, Galakrond summons a 2/1 Elemental with Rush")
			Game.summon(WindsweptElemental(Game, ID), -1, ID, "")
		elif "Warlock" in Class:
			PRINT(Game, "On Invocation, Galakrond summons two 1/1 Imps")
			Game.summon([DraconicImp(Game, ID) for i in range(2)], (-1, "totheRightEnd"), ID, "")
		elif "Warrior" in Class:
			PRINT(Game, "On Invocation, Galakrond gives player +3 Attach this turn")
			Game.heroes[ID].gainTempAttack(3)
	#invocation counter increases and upgrade the galakronds
	Game.Counters.invocationCounts[ID] += 1
	for card in fixedList(Game.Hand_Deck.hands[ID]):
		if "Galakrond, " in card.name:
			upgrade = card.upgradedGalakrond
			isPrimaryGalakrond = (card == primaryGalakrond)
			if hasattr(card, "progress"):
				card.progress += 1
				PRINT(Game, "%s's Invocation progress is now %d"%(card.name, card.progress))
				if upgrade and card.progress > 1:
					Game.Hand_Deck.replaceCardinHand(card, upgrade(Game, ID))
					if isPrimaryGalakrond:
						Game.Counters.primaryGalakronds[ID] = upgrade
	for card in fixedList(Game.Hand_Deck.decks[ID]):
		if "Galakrond, " in card.name:
			upgrade = card.upgradedGalakrond
			isPrimaryGalakrond = (card == primaryGalakrond)
			if hasattr(card, "progress"):
				card.progress += 1
				PRINT(Game, "%s's Invocation progress is now %d"%(card.name, card.progress))
				if upgrade and card.progress > 1:
					Game.Hand_Deck.replaceCardinDeck(card, upgrade(Game, ID))
					if isPrimaryGalakrond:
						Game.Counters.primaryGalakronds[ID] = upgrade
						
						
class Galakrond_Hero(Hero):
	def entersHand(self):
		self.onBoard, self.inHand, self.inDeck = False, True, False
		if self.Game.Counters.primaryGalakronds[self.ID] == None:
			self.Game.Counters.primaryGalakronds[self.ID] = self
		for trigger in self.triggersinHand:
			trigger.connect()
		return self
		
	def entersDeck(self):
		self.onBoard, self.inHand, self.inDeck = False, False, True
		self.Game.Manas.calcMana_Single(self)
		if self.Game.Counters.primaryGalakronds[self.ID] == None:
			self.Game.Counters.primaryGalakronds[self.ID] = self
		for trigger in self.triggersinDeck:
			trigger.connect()
			
	def replaceHero(self, fromHeroCard=False):
		self.attTimes = self.Game.heroes[self.ID].attTimes
		self.Game.heroes[self.ID] = self
		self.Game.heroes[self.ID].onBoard = True
		if self.Game.Counters.primaryGalakronds[self.ID] == None:
			self.Game.Counters.primaryGalakronds[self.ID] = self
		self.heroPower.replaceHeroPower()
		self.Game.sendSignal("HeroReplaced", self.ID, None, self, 0, "")
		
	def played(self, target=None, choice=0, mana=0, posinHand=0, comment=""): #英雄牌使用不存在触发发现的情况
		self.health = self.Game.heroes[self.ID].health
		self.health_upper = self.Game.heroes[self.ID].health_upper
		self.armor = self.Game.heroes[self.ID].armor
		self.attack_bare = self.Game.heroes[self.ID].attack_bare
		self.attTimes = self.Game.heroes[self.ID].attTimes
		self.Game.powers[self.ID].disappears()
		self.Game.powers[self.ID].heroPower = None
		self.Game.heroes[self.ID].onBoard = False
		heroPower = self.heroPower #这个英雄技能必须存放起来，之后英雄还有可能被其他英雄替换，但是这个技能要到最后才登场。
		self.Game.heroes[self.ID] = self #英雄替换。如果后续有埃克索图斯再次替换英雄，则最后的英雄是拉格纳罗斯。
		self.Game.heroes[self.ID].onBoard = True
		if self.Game.Counters.primaryGalakronds[self.ID] == None:
			self.Game.Counters.primaryGalakronds[self.ID] = self
		self.Game.sendSignal("HeroCardPlayed", self.ID, self, None, mana, "", choice)
		self.gainsArmor(type(self).armor)
		self.Game.gathertheDead()
		heroPower.replaceHeroPower()
		if self.Game.status[self.ID]["Battlecry x2"] > 0:
			self.whenEffective(None, "", choice)
		self.whenEffective(None, "", choice)
		if self.weapon: #如果英雄牌本身带有武器，如迦拉克隆等。则装备那把武器
			self.Game.equipWeapon(self.weapon(self.Game, self.ID))
		weapon = self.Game.availableWeapon(self.ID)
		if weapon and self.ID == self.Game.turn:
			self.Game.heroes[self.ID].attack = self.Game.heroes[self.ID].attack_bare + max(0, weapon.attack)
		else:
			self.Game.heroes[self.ID].attack = self.Game.heroes[self.ID].attack_bare
		self.Game.heroes[self.ID].decideAttChances_base()
		self.Game.gathertheDead()
		
		
"""Mana 1 cards"""
class BlazingBattlemage(Minion):
	Class, race, name = "Neutral", "", "Blazing Battlemage"
	mana, attack, health = 1, 2, 2
	index = "Dragons~Neutral~Minion~1~2~2~None~Blazing Battlemage"
	requireTarget, keyWord, description = False, "", ""
	
	
class DepthCharge(Minion):
	Class, race, name = "Neutral", "", "Depth Charge"
	mana, attack, health = 1, 0, 5
	index = "Dragons~Neutral~Minion~1~0~5~None~Depth Charge"
	requireTarget, keyWord, description = False, "", "At the start of your turn, deal 5 damage to all minions"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_DepthCharge(self)]
		
class Trigger_DepthCharge(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["TurnStarts"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self.entity.Game, "At the start of turn, %s deals 5 damage to all minions"%self.entity.name)
		targets = self.entity.Game.minionsonBoard(self.entity.ID) + self.entity.Game.minionsonBoard(3-self.entity.ID)
		self.entity.dealsAOE(targets, [5 for minion in targets])
		
		
class HotAirBalloon(Minion):
	Class, race, name = "Neutral", "Mech", "Hot Air Balloon"
	mana, attack, health = 1, 1, 2
	index = "Dragons~Neutral~Minion~1~1~2~Mech~Hot Air Balloon"
	requireTarget, keyWord, description = False, "", "At the start of your turn, gain +1 Health"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_HotAirBalloon(self)]
		
class Trigger_HotAirBalloon(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["TurnStarts"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self.entity.Game, "At the start of turn, %s gains +1 Health"%self.entity.name)
		self.entity.buffDebuff(0, 1)
		
		
class DraconicLackey(Minion):
	Class, race, name = "Neutral", "", "Draconic Lackey"
	mana, attack, health = 1, 1, 1
	index = "Dragons~Neutral~Minion~1~1~1~None~Draconic Lackey~Battlecry~Uncollectible"
	requireTarget, keyWord, description = False, "", "Battlecry: Discover a Dragon"
	poolIdentifier = "Dragons as Druid"
	@classmethod
	def generatePool(cls, Game):
		classes, lists, neutralCards = [], [], []
		classCards = {s : [] for s in Game.ClassesandNeutral}
		for key, value in Game.MinionswithRace["Dragon"].items():
			classCards[key.split('~')[1]].append(value)
			
		for Class in Game.Classes:
			classes.append("Dragons as "+Class)
			lists.append(classCards[Class]+classCards["Neutral"])
		return classes, lists #返回的包含“Class Cards except Hunter”等identifier的列表和其他职业卡表
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if self.ID == curGame.turn and curGame.Hand_Deck.handNotFull(self.ID):
			if curGame.mode == 0:
				if curGame.guides:
					PRINT(curGame, "Draconic Lackey's battlecry adds a Dragon to player's hand")
					curGame.Hand_Deck.addCardtoHand(curGame.guides.pop(0), self.ID, "CreateUsingType")
				else:
					key = "Dragons as "+classforDiscover(self)
					if "byOthers" in comment:
						dragon = npchoice(self.Game.RNGPools[key])
						curGame.fixedGuides.append(dragon)
						PRINT(curGame, "Draconic Lackey's battlecry adds a random Dragon to player's hand")
						curGame.Hand_Deck.addCardtoHand(dragon, self.ID, "CreateUsingType")
					else:
						dragons = npchoice(self.Game.RNGPools[key], 3, replace=False)
						curGame.options = [dragon(curGame, self.ID) for dragon in dragons]
						PRINT(curGame, "Draconic Lackey's battlecry lets player discover a Dragon")
						curGame.Discover.startDiscover(self, None)
		return None
		
	def discoverDecided(self, option, info):
		self.Game.fixedGuides.append(type(option))
		PRINT(self.Game, "Dragon %s is put into player's hand."%option.name)
		self.Game.Hand_Deck.addCardtoHand(option, self.ID)
		self.Game.sendSignal("DiscoveredCardPutintoHand", self.ID, self, option, 0, "")
		
Lackeys = [DraconicLackey, EtherealLackey, FacelessLackey, GoblinLackey, KoboldLackey, TitanicLackey, WitchyLackey]

"""Mana 2 cards"""
class EvasiveChimaera(Minion):
	Class, race, name = "Neutral", "Beast", "Evasive Chimaera"
	mana, attack, health = 2, 2, 1
	index = "Dragons~Neutral~Minion~2~2~1~Beast~Evasive Chimaera~Poisonous"
	requireTarget, keyWord, description = False, "Poisonous", "Poisonous. Can't be targeted by spells or Hero Powers"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.marks["Evasive"] = True
		
		
class DragonBreeder(Minion):
	Class, race, name = "Neutral", "", "Dragon Breeder"
	mana, attack, health = 2, 2, 3
	index = "Dragons~Neutral~Minion~2~2~3~None~Dragon Breeder~Battlecry"
	requireTarget, keyWord, description = True, "", "Battlecry: Choose a friendly Dragon. Add a copy of it to your hand"
	def effectCanTrigger(self):
		self.effectViable = False
		for minion in self.Game.minionsonBoard(self.ID):
			if "Dragon" in minion.race:
				self.effectViable = True
				break
				
	def targetExists(self, choice=0):
		return self.selectableFriendlyMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.ID == self.ID and "Dragon" in target.race and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			PRINT(self.Game, "Dragon Breeder's battlecry adds a copy of friendly Dragon %s to player's hand"%target.name)
			self.Game.Hand_Deck.addCardtoHand(type(target), self.ID, "CreateUsingType")
		return target
		
		
class GrizzledWizard(Minion):
	Class, race, name = "Neutral", "", "Grizzled Wizard"
	mana, attack, health = 2, 3, 2
	index = "Dragons~Neutral~Minion~2~3~2~None~Grizzled Wizard~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Swap Hero Powers with your opponent until next turn"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		#The Hero Powers are swapped at the start of your next turn
		PRINT(self.Game, "Grizzled Wizard's battlecry swaps player's Hero Powers until next turn")
		temp = self.Game.powers[1]
		self.Game.powers[1].disappears()
		self.Game.powers[2].disappears()
		self.Game.powers[1] = self.Game.powers[2]
		self.Game.powers[2] = temp
		self.Game.powers[1].appears()
		self.Game.powers[2].appears()
		self.Game.powers[1].ID, self.Game.powers[2].ID = 1, 2
		
		trigger = Trigger_GrizzledWizard(self.Game, self.ID)
		trigger.connect()
		return None
		
class Trigger_GrizzledWizard(TriggeronBoard):
	def __init__(self, Game, ID):
		self.Game, self.ID = Game, ID
		self.signals = ["TurnStarts"]
		self.temp = False
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return ID == self.ID
		
	def connect(self):
		for signal in self.signals:
			self.Game.triggersonBoard[self.ID].append((self, signal))
			
	def disconnect(self):
		for signal in self.signals:
			extractfrom((self, signal), self.Game.triggersonBoard[self.ID])
			
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self.entity.Game, "At the start of player's turn, the two players' Hero Powers are swapped back")
		temp = self.Game.powers[1]
		self.Game.powers[1].disappears()
		self.Game.powers[2].disappears()
		self.Game.powers[1] = self.Game.powers[2]
		self.Game.powers[1].appears()
		self.Game.powers[2] = temp
		self.Game.powers[2].appears()
		self.Game.powers[1].ID, self.Game.powers[2].ID = 1, 2
		
		
class ParachuteBrigand(Minion):
	Class, race, name = "Neutral", "Pirate", "Parachute Brigand"
	mana, attack, health = 2, 2, 2
	index = "Dragons~Neutral~Minion~2~2~2~Pirate~Parachute Brigand"
	requireTarget, keyWord, description = False, "", "After you play a Pirate, summon this minion from your hand"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersinHand = [Trigger_ParachuteBrigand(self)]
		
class Trigger_ParachuteBrigand(TriggerinHand):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionBeenPlayed"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.inHand and subject.ID == self.entity.ID and "Pirate" in subject.race
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		minion = self.entity
		PRINT(minion.Game, "After player plays Pirate, %s is summoned from hand"%minion.name)
		#不知道会召唤在最右边还是打出的海盗的右边。假设在最右边
		i = minion.Game.Hand_Deck.hands[minion.ID].index(minion)
		minion.Game.summonfromHand(i, minion.ID, -1, self.entity.ID)
		
		
class TastyFlyfish(Minion):
	Class, race, name = "Neutral", "Murloc", "Tasty Flyfish"
	mana, attack, health = 2, 2, 2
	index = "Dragons~Neutral~Minion~2~2~2~Murloc~Tasty Flyfish~Deathrattle"
	requireTarget, keyWord, description = False, "", "Deathrattle: Give a Dragon in your hand +2/+2"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [GiveaDragoninHandPlus2Plus2(self)]
		
class GiveaDragoninHandPlus2Plus2(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		curGame = self.entity.Game
		ownHand = curGame.Hand_Deck.hands[self.entity.ID]
		if curGame.mode == 0:
			if curGame.guides:
				i = curGame.guides.pop(0)
				if i < 0: return
				else: dragon = ownHand[i]
			else:
				dragonsinHand = [i for i, card in enumerate(ownHand) if card.type == "Minion" and "Dragon" in card.race]
				if dragonsinHand:
					i = npchoice(dragonsinHand)
					dragon = ownHand[i]
					curGame.fixedGuides.append(i)
				else:
					curGame.fixedGuides.append(-1)
					return
			PRINT(curGame, "Deathrattle: Give a random Dragon in your hand +2/+2 triggers")
			dragon.buffDebuff(2, 2)
			
#需要测试法术和随从的抽到时触发效果与这个孰先孰后。以及变形后的加拉克隆的效果触发。
#测试时阿兰纳斯蛛后不会触发其加血效果。场上同时有多个幻术师的时候，会依次发生多冷变形。https://www.bilibili.com/video/av79078930?from=search&seid=4964775667793261235
#源生宝典和远古谜团等卡牌抽到一张牌然后为期费用赋值等效果都会在变形效果生效之后进行赋值。
#与其他“每当你抽一张xx牌”的扳机（如狂野兽王）共同在场时，是按照登场的先后顺序（扳机的正常顺序结算）。
#不太清楚与阿鲁高如果结算，据说是阿鲁高始终都会复制初始随从。不考虑这个所谓特例的可能性
#抽到“抽到时施放”的法术时，不会触发其效果，直接变成传说随从，然后也不追加抽牌。
class Transmogrifier(Minion):
	Class, race, name = "Neutral", "", "Transmogrifier"
	mana, attack, health = 2, 2, 3
	index = "Dragons~Neutral~Minion~2~2~3~None~Transmogrifier"
	requireTarget, keyWord, description = False, "", "Whenever you draw a card, transform it into a random Legendary minion"
	poolIdentifier = "Legendary Minions"
	@classmethod
	def generatePool(cls, Game):
		return "Legendary Minions", list(Game.LegendaryMinions.values())
		
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_Transmogrifier(self)]
		
class Trigger_Transmogrifier(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["CardDrawn"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and target[0].ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		curGame = self.entity.Game
		if curGame.mode == 0:
			if curGame.guides:
				minion = curGame.guides.pop(0)
			else:
				minion = npchoice(curGame.RNGPools["Legendary Minions"])
				curGame.fixedGuides.append(minion)
			PRINT(curGame, "When player draws a card %s, Transmogrifier transforms it into a random Legendary minion"%target[0].name)
			curGame.Hand_Deck.replaceCardDrawn(target, minion(curGame, self.entity.ID))
			
			
class WyrmrestPurifier(Minion):
	Class, race, name = "Neutral", "", "Wyrmrest Purifier"
	mana, attack, health = 2, 3, 2
	index = "Dragons~Neutral~Minion~2~3~2~None~Wyrmrest Purifier~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Transform all Neutral cards in your deck into random cards from your class"
	poolIdentifier = "Mage Cards"
	@classmethod
	def generatePool(cls, Game):
		classes, lists = [], []
		for Class in Game.Classes:
			classes.append(Class+" Cards")
			lists.append(list(Game.ClassCards[Class].values()))
		return classes, lists
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		ownDeck = curGame.Hand_Deck.decks[self.ID]
		neutralCards = [i for i, card in enumerate(ownDeck) if card.Class == "Neutral"]
		PRINT(curGame, "Wyrmrest Purifier's battlecry transforms all Neutral cards in player's deck into random cards from player's class")
		if neutralCards:
			if curGame.guides:
				newCards = list(curGame.guides.pop(0))
			else:
				#不知道如果我方英雄没有职业时，变形成的牌是否会是中立。假设会变形成为随机职业
				Class = curGame.heroes[self.ID].Class
				key = Class+" Cards" if Class != "Neutral" else "%s Cards"%npchoice(curGame.Classes)
				newCards = npchoice(curGame.RNGPools[key], len(neutralCards), replace=True)
				curGame.fixedGuides.append(tuple(newCards))
			for i, newCard in zip(neutralCards, newCards):
				curGame.Hand_Deck.extractfromDeck(i, self.ID)
				card = newCard(curGame, self.ID)
				ownDeck.insert(i, card)
				card.entersDeck()
		return None
		
"""Mana 3 cards"""
class BlowtorchSaboteur(Minion):
	Class, race, name = "Neutral", "", "Blowtorch Saboteur"
	mana, attack, health = 3, 3, 4
	index = "Dragons~Neutral~Minion~3~3~4~None~Blowtorch Saboteur~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Your opponent's next Hero Power costs (3)"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		PRINT(self.Game, "Blowtorch's Saboteur's battlecry makes the opponent's next Hero Power cost (3)")
		self.Game.Manas.PowerAuras_Backup.append(YourOpponentsNextHeroPowerCosts3(self.Game, 3-self.ID))
		return None
		
class YourOpponentsNextHeroPowerCosts3(TempManaEffect_Power):
	def __init__(self, Game, ID):
		self.Game, self.ID = Game, ID
		self.changeby, self.changeto = 0, 3
		#这个效果不会随着回合更替而消失，所以没有temporary属性
		self.auraAffected = []
		
	def applicable(self, target):
		return target.ID == self.ID
		
	def selfCopy(self, recipientGame):
		return type(self)(recipientGame, self.ID)
		
		
class DreadRaven(Minion):
	Class, race, name = "Neutral", "Beast", "Dread Raven"
	mana, attack, health = 3, 3, 4
	index = "Dragons~Neutral~Minion~3~3~4~Beast~Dread Raven"
	requireTarget, keyWord, description = False, "", "Battlecry: Has +3 Attack for each other Dead Raven you control"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.auras["Buff Aura"] = BuffAura_DreadRaven(self)
		
class BuffAura_DreadRaven(AuraDealer_toMinion):
	def __init__(self, entity):
		self.entity = entity
		self.signals, self.auraAffected = ["MinionAppears", "MinionDisappears"], []
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		obj = subject if signal == "MinionAppears" else target
		return self.entity.onBoard and obj.ID == self.entity.ID and obj.name == "Dread Raven" and obj != self.entity
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		for minion, aura_Receiver in fixedList(self.auraAffected):
			aura_Receiver.effectClear()
			
		self.applies(self.entity)
		
	def applies(self, subject):
		numDreadRavens = 0
		for minion in self.entity.Game.minionsonBoard(self.entity.ID):
			if minion.name == "Dread Raven" and minion != self.entity:
				numDreadRavens += 1
				
		if numDreadRavens > 0:
			aura_Receiver = BuffAura_Receiver(subject, self, 3 * numDreadRavens, 0)
			aura_Receiver.effectStart()
			
	def auraAppears(self):
		self.applies(self.entity)
		for signal in self.signals:
			self.entity.Game.triggersonBoard[self.entity.ID].append((self, signal))
			
	def selfCopy(self, recipientMinion): #The recipientMinion is the minion that deals the Aura.
		#func that checks if subject is applicable will be the new copy's function
		return type(self)(recipientMinion)
	#可以通过AuraDealer_toMinion的createCopy方法复制
	
	
class FireHawk(Minion):
	Class, race, name = "Neutral", "Elemental", "Fire Hawk"
	mana, attack, health = 3, 1, 3
	index = "Dragons~Neutral~Minion~3~1~3~Elemental~Fire Hawk~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Gain +1 Attack for each card in your opponent's hand"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		PRINT(self.Game, "Fire Hawk's battlecry gives minion +1 Attack for each card in the opponent's hand")
		self.buffDebuff(len(self.Game.Hand_Deck.hands[3-self.ID]), 0)
		return None
		
		
class GoboglideTech(Minion):
	Class, race, name = "Neutral", "", "Goboglide Tech"
	mana, attack, health = 3, 3, 3
	index = "Dragons~Neutral~Minion~3~3~3~None~Goboglide Tech~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: If you control a Mech, gain +1/+1 and Rush"
	def effectCanTrigger(self):
		self.effectViable = False
		for minion in self.Game.minionsonBoard(self.ID):
			if "Mech" in minion.race:
				self.effectViable = True
				break
				
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		controlsMech = False
		for minion in self.Game.minionsonBoard(self.ID):
			if "Mech" in minion.race:
				controlsMech = True
				break
		if controlsMech:
			PRINT(self.Game, "Goboglide Tech's battlecry gives minion +1/+1 and Rush")
			self.buffDebuff(1, 1)
			self.getsKeyword("Rush")
		return None
		
		
class LivingDragonbreath(Minion):
	Class, race, name = "Neutral", "Elemental", "Living Dragonbreath"
	mana, attack, health = 3, 3, 4
	index = "Dragons~Neutral~Minion~3~3~4~Elemental~Living Dragonbreath"
	requireTarget, keyWord, description = False, "", "Your minions can't be Frozen"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.appearResponse = [self.activateAura]
		self.disappearResponse = [self.deactivateAura]
		self.silenceResponse = [self.deactivateAura]
		
	def activateAura(self):
		PRINT(self.Game, "Living Dragonbreath's aura is registered. Player %d's minions thaw immediately and won't be Frozen again."%self.ID)
		for minion in fixedList(self.Game.minionsonBoard(self.ID)):
			minion.status["Frozen"] = 0
		self.Game.status[self.ID]["Minions Can't Be Frozen"] += 1
		
	def deactivateAura(self):
		PRINT(self.Game, "Living Dragonbreath's aura is removed. Player %d's minions can be Frozen now"%self.ID)
		if self.Game.status[self.ID]["Minions Can't Be Frozen"] > 0:
			self.Game.status[self.ID]["Minions Can't Be Frozen"] -= 1
			
			
class Scalerider(Minion):
	Class, race, name = "Neutral", "", "Scalerider"
	mana, attack, health = 3, 3, 3
	index = "Dragons~Neutral~Minion~3~3~3~None~Scalerider~Battlecry"
	requireTarget, keyWord, description = True, "", "Battlecry: If you're holding a Dragon, deal 2 damage"
	
	def returnTrue(self, choice=0):
		return self.Game.Hand_Deck.holdingDragon(self.ID)
		
	def effectCanTrigger(self): #Friendly characters are always selectable.
		self.effectViable = self.Game.Hand_Deck.holdingDragon(self.ID)
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target and self.Game.Hand_Deck.holdingDragon(self.ID):
			PRINT(self.Game, "Scalerider's battlecry deals 2 damage to %s"%target.name)
			self.dealsDamage(target, 2)
		return target
		
		
"""Mana 4 cards"""
class BadLuckAlbatross(Minion):
	Class, race, name = "Neutral", "Beast", "Bad Luck Albatross"
	mana, attack, health = 4, 4, 3
	index = "Dragons~Neutral~Minion~4~4~3~Beast~Bad Luck Albatross~Deathrattle"
	requireTarget, keyWord, description = False, "", "Deathrattle: Shuffle two 1/1 Albatross into your opponent's deck"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [ShuffleTwoAlbatrossintoOpponentsDeck(self)]
		
class ShuffleTwoAlbatrossintoOpponentsDeck(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self.entity.Game, "Deathrattle: Shuffle two 1/1 Albatross into your opponent's deck triggers")
		self.entity.Game.Hand_Deck.shuffleCardintoDeck([Albatross(self.entity.Game, 3-self.entity.ID) for i in range(2)], self.entity.ID)
		
class Albatross(Minion):
	Class, race, name = "Neutral", "Beast", "Albatross"
	mana, attack, health = 1, 1, 1
	index = "Dragons~Neutral~Minion~1~1~1~Beast~Albatross~Uncollectible"
	requireTarget, keyWord, description = False, "", ""
	
	
class DevotedManiac(Minion):
	Class, race, name = "Neutral", "", "Devoted Maniac"
	mana, attack, health = 4, 2, 2
	index = "Dragons~Neutral~Minion~4~2~2~None~Devoted Maniac~Rush~Battlecry"
	requireTarget, keyWord, description = False, "Rush", "Rush. Battlecry: Invoke Galakrond"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		PRINT(self.Game, "Devoted Maniac's battlecry Invokes Galakrond")
		invokeGalakrond(self.Game, self.ID)
		return None
		
		
class DragonmawPoacher(Minion):
	Class, race, name = "Neutral", "", "Dragonmaw Poacher"
	mana, attack, health = 4, 4, 4
	index = "Dragons~Neutral~Minion~4~4~4~None~Dragonmaw Poacher~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: If your opponent controls a Dragon, gain +4/+4 and Rush"
	
	def effectCanTrigger(self):
		self.effectViable = False
		for minion in self.Game.minionsonBoard(3-self.ID):
			if "Dragon" in minion.race:
				self.effectViable = True
				break
				
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		enemyControlsDragon = False
		for minion in self.Game.minionsonBoard(3-self.ID):
			if "Dragon" in minion.race:
				enemyControlsDragon = True
				break
		if enemyControlsDragon:
			PRINT(self.Game, "Dragonmaw Poacher's battlecry gives minion +4/+4 and Rush")
			self.buffDebuff(4, 4)
			self.getsKeyword("Rush")
		return None
		
		
class EvasiveFeywing(Minion):
	Class, race, name = "Neutral", "Dragon", "Evasive Feywing"
	mana, attack, health = 4, 5, 4
	index = "Dragons~Neutral~Minion~4~5~4~Dragon~Evasive Feywing"
	requireTarget, keyWord, description = False, "", "Can't be targeted by spells or Hero Powers"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.marks["Evasive"] = 1
		
		
class FrizzKindleroost(Minion):
	Class, race, name = "Neutral", "", "Frizz Kindleroost"
	mana, attack, health = 4, 5, 4
	index = "Dragons~Neutral~Minion~4~5~4~None~Frizz Kindleroost~Battlecry~Legendary"
	requireTarget, keyWord, description = False, "", "Battlecry: Reduce the Cost of Dragons in your deck by (2)"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		PRINT(self.Game, "Frizz Kindleroost's battlecry reduces the Cost of Dragons in player's deck by (2)")
		for card in self.Game.Hand_Deck.decks[self.ID]:
			if card.type == "Minion" and "Dragon" in card.race:
				ManaModification(card, changeby=-2, changeto=-1).applies()
		return None
		
		
class Hippogryph(Minion):
	Class, race, name = "Neutral", "Beast", "Hippogryph"
	mana, attack, health = 4, 2, 6
	index = "Dragons~Neutral~Minion~4~2~6~Beast~Hippogryph~Rush~Taunt"
	requireTarget, keyWord, description = False, "Rush,Taunt", "Rush, Taunt"
	
	
class HoardPillager(Minion):
	Class, race, name = "Neutral", "Pirate", "Hoard Pillager"
	mana, attack, health = 4, 4, 2
	index = "Dragons~Neutral~Minion~4~4~2~Pirate~Hoard Pillager~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Equip one of your destroyed weapons"
	def effectCanTrigger(self):
		self.effectViable = self.Game.Counters.weaponsDestroyedThisGame[self.ID] != []
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		PRINT(curGame, "Hoard Pillager's battlecry equips a destroyed weapon of the player")
		if curGame.mode == 0:
			if curGame.guides:
				weapon = curGame.guides.pop(0)
				if weapon is None: return None
			else:
				weaponsDestroyed = curGame.Counters.weaponsDestroyedThisGame[self.ID]
				if weaponsDestroyed:
					weapon = curGame.cardPool[npchoice(weaponsDestroyed)]
					curGame.fixedGuides.append(weapon)
				else:
					curGame.fixedGuides.append(None)
					return None
			PRINT(curGame, "The destroyed weapon %s is equipped"%weapon.name)
			curGame.equipWeapon(weapon(curGame, self.ID))
		return None
		
		
class TrollBatrider(Minion):
	Class, race, name = "Neutral", "", "Troll Batrider"
	mana, attack, health = 4, 3, 3
	index = "Dragons~Neutral~Minion~4~3~3~None~Troll Batrider~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Deal 3 damage to a random enemy minion"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		PRINT(curGame, "Troll Batrider's battlecry deals 3 damage to a random enemy")
		if curGame.mode == 0:
			if curGame.guides:
				i = curGame.guides.pop(0)
				if i < 0: minion = curGame.minions[3-self.ID][i]
				else: return None
			else:
				targets = curGame.minionsAlive(3-self.ID)
				if targets:
					minion = npchoice(targets)
					curGame.fixedGuides.append(minion.position)
				else:
					curGame.fixedGuides.append(-1)
					return None
			PRINT(curGame, "Troll Batrider deals 3 damage to random enemy minion %s"%minion.name)
			self.dealsDamage(minion, 3)
		return None
		
		
class WingCommander(Minion):
	Class, race, name = "Neutral", "", "Wing Commander"
	mana, attack, health = 4, 2, 5
	index = "Dragons~Neutral~Minion~4~2~5~None~Wing Commander"
	requireTarget, keyWord, description = False, "", "Has +2 Attack for each Dragon in your hand"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.auras["Buff Aura"] = BuffAura_WingCommander(self)
		
class BuffAura_WingCommander(AuraDealer_toMinion):
	def __init__(self, entity):
		self.entity = entity
		self.signals, self.auraAffected = ["CardLeavesHand", "CardEntersHand"], []
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		card = target[0] if signal == "CardEntersHand" else target
		return self.minion.onBoard and card.ID == self.minion.ID and card.type == "Minion" and "Dragon" in card.race
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		for minion, aura_Receiver in fixedList(self.auraAffected):
			aura_Receiver.effectClear()
			
		self.applies(self.minion)
		
	def applies(self, subject):
		numDragonsinHand = 0
		for card in self.minion.Game.minionsonBoard(self.minion.ID):
			if card.type == "Minion" and "Dragon" in card.race:
				numDragonsinHand += 1
				
		if numDragonsinHand > 0:
			PRINT(self.Game, "Minion %s gains the %d Attack for the Dragons player's holding"%(subject.name, 2 * numDragonsinHand))
			aura_Receiver = BuffAura_Receiver(subject, self, 2 * numDragonsinHand, 0)
			aura_Receiver.effectStart()
			
	def auraAppears(self):
		self.applies(self.minion)
		for signal in self.signals:
			self.minion.Game.triggersonBoard[self.minion.ID].append((self, signal))
			
	def selfCopy(self, recipientMinion): #The recipientMinion is the minion that deals the Aura.
		#func that checks if subject is applicable will be the new copy's function
		return type(self)(recipientMinion)
	#可以通过AuraDealer_toMinion的createCopy方法复制
	
	
class ZulDrakRitualist(Minion):
	Class, race, name = "Neutral", "", "Zul'Drak Ritualist"
	mana, attack, health = 4, 3, 9
	index = "Dragons~Neutral~Minion~4~3~9~None~Zul'Drak Ritualist~Taunt~Battlecry"
	requireTarget, keyWord, description = False, "Taunt", "Taunt. Battlecry: Summon three random 1-Cost minions for your opponent"
	poolIdentifier = "1-Cost Minions to Summon"
	@classmethod
	def generatePool(cls, Game):
		return "1-Cost Minion to Summon", list(Game.MinionsofCost[1].values())
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if curGame.mode == 0:
			if curGame.guides:
				minions = list(curGame.pop(0)[2])
			else:
				minions = npchoice(curGame.RNGPools["1-Cost Minions to Summon"], 3, replace=True)
				curGame.fixedGuides.append(tuple(minions))
			PRINT(curGame, "Zul'Drak Ritualist's battlecry summons three 1-Cost minions for the opponent")
			minions = [minion(curGame, 3-self.ID) for minion in minions]
			curGame.summon(minions, (-1, "totheRightEnd"), self.ID)
		return None
		
		
"""Mana 5 cards"""
class BigOlWhelp(Minion):
	Class, race, name = "Neutral", "Dragon", "Big Ol' Whelp"
	mana, attack, health = 5, 5, 5
	index = "Dragons~Neutral~Minion~5~5~5~Dragon~Big Ol' Whelp~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Draw a card"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		PRINT(self.Game, "Big Ol' Whelp's battlecry lets player draw a card")
		self.Game.Hand_Deck.drawCard(self.ID)
		return None
		
		
class ChromaticEgg(Minion):
	Class, race, name = "Neutral", "", "Chromatic Egg"
	mana, attack, health = 5, 0, 3
	index = "Dragons~Neutral~Minion~5~0~3~None~Chromatic Egg~Battlecry~Deathrattle"
	requireTarget, keyWord, description = False, "", "Battlecry: Secretly Discover a Dragon to hatch into. Deathrattle: Hatch!"
	poolIdentifier = "Dragons as Druid to Summon"
	@classmethod
	def generatePool(cls, Game):
		classes, lists, neutralCards = [], [], []
		classCards = {s : [] for s in Game.ClassesandNeutral}
		for key, value in Game.MinionswithRace["Dragon"].items():
			classCards[key.split('~')[1]].append(value)
			
		for Class in Game.Classes:
			classes.append("Dragons as %s to Summon"%Class)
			lists.append(classCards[Class]+classCards["Neutral"])
		return classes, lists #返回的包含“Class Cards except Hunter”等identifier的列表和其他职业卡表
		
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [HatchintotheChosenDragon(self)]
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if self.ID == curGame.turn:
			if curGame.mode == 0:
				if curGame.guides:
					dragon = curGame.guides.pop(0)
					PRINT(curGame, "Chromatic Egg's battlecry chooses a Dragon to hacth into")
					for trigger in self.deathrattles:
						if type(trigger) == HatchintotheChosenDragon:
							trigger.dragonInside = dragon
				else:
					key = "Dragons as %s to Summon"%classforDiscover(self)
					if "byOthers" in comment:
						PRINT(curGame, "Chromatic Egg's battlecry chooses a random Dragon to hacth into")
						dragon = npchoice(curGame.RNGPools[key])
						curGame.fixedGuides.append(dragon)
						for trigger in self.deathrattles:
							if type(trigger) == HatchintotheChosenDragon:
								trigger.dragonInside = dragon
					else:
						PRINT(curGame, "Chromatic Egg's battlecry lets player Secretly Discover a Dragon to hatch into")
						dragons = npchoice(curGame.RNGPools[key], 3, replace=False)
						curGame.options = [dragon(curGame, self.ID) for dragon in dragons]
						curGame.Discover.startDiscover(self, None)
		return None
		
	def discoverDecided(self, option, info):
		PRINT(self.Game, "Dragon to hatch into: %s has been decided"%option.name)
		self.Game.fixedGuides.append(type(option))
		for trigger in self.deathrattles:
			if type(trigger) == HatchintotheChosenDragon:
				trigger.dragonInside = type(option)
				
class HatchintotheChosenDragon(Deathrattle_Minion):
	def __init__(self, entity):
		self.blank_init(entity)
		self.dragonInside = None #This is a class
	#变形亡语只能触发一次。
	def trigger(self, signal, ID, subject, target, number, comment, choice=0):
		if self.canTrigger(signal, ID, subject, target, number, comment):
			if self.dragonInside:
				PRINT(self.entity.Game, "Deathrattle: Hatch into a Dragon triggers")
				if self.entity.Game.withAnimation:
					self.entity.Game.GUI.triggerBlink(self.entity)
				self.entity.Game.transform(self.entity, self.dragonInside(self.entity.Game, self.entity.ID))
				
	def selfCopy(self, newMinion):
		trigger = type(self)(newMinion)
		trigger.dragonInside = self.dragonInside
		return trigger
		
		
class CobaltSpellkin(Minion):
	Class, race, name = "Neutral", "Dragon", "Cobalt Spellkin"
	mana, attack, health = 5, 3, 5
	index = "Dragons~Neutral~Minion~5~3~5~Dragon~Cobalt Spellkin~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Add two 1-Cost spells from your class to your hand"
	poolIdentifier = "1-Cost Spells as Druid"
	@classmethod
	def generatePool(cls, Game):
		classes, lists = [], []
		for Class in Game.Classes:
			oneCostSpells = []
			for key, value in Game.ClassCards[Class].items():
				if "~Spell~1~" in key:
					oneCostSpells.append(value)
			classes.append("1-Cost Spells as "+Class)
			lists.append(oneCostSpells)
		return classes, lists #返回的包含“Class Cards except Hunter”等identifier的列表和其他职业卡表
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		PRINT(curGame, "Cobalt Spellkin's battlecry adds two random 1-Cost spells from player's Class to player's hand")
		if curGame.Hand_Deck.handNotFull(self.ID):
			if curGame.mode == 0:
				if curGame.guides:
					spells = list(curGame.guides.pop(0))
				else:
					key = "1-Cost Spells as "+classforDiscover(self)
					spells = npchoice(curGame.RNGPools[key], 2, replace=True)
					curGame.fixedGuides.append(tuple(spells))
				curGame.Hand_Deck.addCardtoHand(spells, self.ID, "CreateUsingType")
		return None
		
		
class FacelessCorruptor(Minion):
	Class, race, name = "Neutral", "", "Faceless Corruptor"
	mana, attack, health = 5, 4, 4
	index = "Dragons~Neutral~Minion~5~4~4~None~Faceless Corruptor~Rush~Battlecry"
	requireTarget, keyWord, description = True, "Rush", "Rush. Battlecry: Transform one of your friendly minions into a copy of this"
	
	def targetExists(self, choice=0):
		return self.selectableFriendlyMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.ID == self.ID and target != self and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target and (self.onBoard or self.inHand):
			PRINT(self.Game, "Faceless Corruptor's battlecry transforms friendly minion %s into a copy of the minion"%target.name)
			Copy = self.selfCopy(self.ID)
			self.Game.transform(target, Copy)
		return Copy
		
		
class KoboldStickyfinger(Minion):
	Class, race, name = "Neutral", "", "Kobold Stickyfinger"
	mana, attack, health = 5, 4, 4
	index = "Dragons~Neutral~Minion~5~4~4~None~Kobold Stickyfinger~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Steal your opponent's weapon"
	
	def effectCanTrigger(self):
		self.effectViable = self.Game.availableWeapon(3-self.ID)
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		PRINT(self.Game, "Kobold Stickyfinger's battlecry steals the opponent's weapon")
		enemyWeapon = self.Game.availableWeapon(3-self.ID)
		if enemyWeapon:
			enemyWeapon.disappears()
			extractfrom(enemyWeapon, self.Game.weapons[3-self.ID])
			enemyWeapon.ID = self.ID
			self.Game.equipWeapon(enemyWeapon)
		return None
		
	
class Platebreaker(Minion):
	Class, race, name = "Neutral", "", "Platebreaker"
	mana, attack, health = 5, 5, 5
	index = "Dragons~Neutral~Minion~5~5~5~None~Platebreaker~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Destroy your opponent's Armor"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		PRINT(self.Game, "Platebreaker's battlecry destroys the opponent's Armor")
		self.Game.heroes[3-self.ID].armor = 0
		return None
		
		
class ShieldofGalakrond(Minion):
	Class, race, name = "Neutral", "", "Shield of Galakrond"
	mana, attack, health = 5, 4, 5
	index = "Dragons~Neutral~Minion~5~4~5~None~Shield of Galakrond~Taunt~Battlecry"
	requireTarget, keyWord, description = False, "Taunt", "Taunt. Battlecry: Invoke Galakrond"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		PRINT(self.Game, "Shield of Galakrond's battlecry Invokes Galakrond")
		invokeGalakrond(self.Game, self.ID)
		return None
		
		
class Skyfin(Minion):
	Class, race, name = "Neutral", "Murloc", "Skyfin"
	mana, attack, health = 5, 3, 3
	index = "Dragons~Neutral~Minion~5~3~3~Murloc~Skyfin~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: If you're holding a Dragon, summon 2 random Murlocs"
	poolIdentifier = "Murlocs to Summon"
	@classmethod
	def generatePool(cls, Game):
		return "Murlocs to Summon", list(Game.MinionswithRace["Murloc"].values())
		
	def effectCanTrigger(self):
		self.effectViable = self.Game.Hand_Deck.holdingDragon(self.ID)
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if curGame.Hand_Deck.holdingDragon(self.ID):
			if curGame.mode == 0:
				if curGame.guides:
					murlocs = curGame.guides.pop(0)
				else:
					murlocs = npchoice(curGame.RNGPools["Murlocs to Summon"], 2, replace=True)
					curGame.fixedGuides.append(tuple(murlocs))
				PRINT(curGame, "Skyfin's battlecry summons two random Murlocs")
				pos = (self.position, "leftandRight") if self.onBoard else (-1, "totheRightEnd")
				curGame.summon([murloc(curGame, self.ID) for murloc in murlocs], pos, self.ID)
		return None
		
		
class TentacledMenace(Minion):
	Class, race, name = "Neutral", "", "Tentacled Menace"
	mana, attack, health = 5, 6, 5
	index = "Dragons~Neutral~Minion~5~6~5~None~Tentacled Menace~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Each player draws a card. Swap their Costs"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		PRINT(self.Game, "Tentacled Menace's battlecry lets both players draw a card and swap their Cost")
		card1, mana = self.Game.Hand_Deck.drawCard(self.ID)
		card2, mana = self.Game.Hand_Deck.drawCard(3-self.ID)
		if card1 and card2:
			mana1, mana2 = card1.mana, card2.mana
			ManaModification(card1, changeby=0, changeto=mana2).applies()
			ManaModification(card2, changeby=0, changeto=mana1).applies()
			self.Game.Manas.calcMana_Single(card1)
			self.Game.Manas.calcMana_Single(card2)
		return None
		
		
"""Mana 6 cards"""
class CamouflagedDirigible(Minion):
	Class, race, name = "Neutral", "Mech", "Camouflaged Dirigible"
	mana, attack, health = 6, 6, 6
	index = "Dragons~Neutral~Minion~6~6~6~Mech~Camouflaged Dirigible~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Give your other Mechs Stealth until your next turn"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		PRINT(self.Game, "Camouflaged Dirigible's battlecry gives all other friendly Mechs Stealth until player's next turn")
		for minion in fixedList(self.Game.minionsonBoard(self.ID)):
			if "Mech" in minion.race:
				minion.status["Temp Stealth"] += 1
		return None
		
		
class EvasiveWyrm(Minion):
	Class, race, name = "Neutral", "Dragon", "Evasive Wyrm"
	mana, attack, health = 6, 5, 3
	index = "Dragons~Neutral~Minion~6~5~3~Dragon~Evasive Wyrm~Divine Shield~Rush"
	requireTarget, keyWord, description = False, "Divine Shield,Rush", "Divine Shield, Rush. Can't be targeted by spells or Hero Powers"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.marks["Evasive"] = 1
		
		
class Gyrocopter(Minion):
	Class, race, name = "Neutral", "Mech", "Gyrocopter"
	mana, attack, health = 6, 4, 5
	index = "Dragons~Neutral~Minion~6~4~5~Mech~Gyrocopter~Rush~Windfury"
	requireTarget, keyWord, description = False, "Rush,Windfury", "Rush, Windfury"
	
	
class KronxDragonhoof(Minion):
	Class, race, name = "Neutral", "", "Kronx Dragonhoof"
	mana, attack, health = 6, 6, 6
	index = "Dragons~Neutral~Minion~6~6~6~None~Kronx Dragonhoof~Battlecry~Legendary"
	requireTarget, keyWord, description = False, "", "Battlecry: Draw Galakrond. If you're alread Galakrond, unleash a Devastation"
	
	def effectCanTrigger(self):
		self.effectViable =  "Galakrond" in self.Game.heroes[self.ID].name
	#迦拉克隆有主迦拉克隆机制，祈求时只有主迦拉克隆会响应
	#主迦拉克隆会尽量与玩家职业匹配，如果不能匹配，则系统检测到的第一张迦拉克隆会被触发技能
	#http://nga.178.com/read.php?tid=19587242&rand=356
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if not curGame.heroes[self.ID].name.startswith("Galakrond"):
			PRINT(curGame, "Kronx Dragonhoof's battlecry lets player draw Galakrond.")
			galakrond = None
			for card in curGame.Hand_Deck.decks[self.ID]:
				if card.name.startswith("Galakrond, "):
					galakrond = card
					break
			if galakrond: curGame.Hand_Deck.drawCard(self.ID, galakrond)
		else:
			if curGame.mode == 0:
				if curGame.guides:
					PRINT(curGame, "Kronx Dragonhoof's battlecry chooses a Devastation to unleash")
					self.discoverDecided(curGame.guides.pop(0)())
				else:
					if "byOthers" in comment:
						effect = npchoice([Annihilation, Decimation, Domination, Reanimation])
						curGame.fixedGuides.append(effect)
						PRINT(curGame, "Kronx Dragonhoof's battlecry chooses a random Devastation to unleash")
						self.discoverDecided(effect())
					else:
						PRINT(curGame, "Kronx Dragonhoof's battlecry lets player choose a Devastation to unleash")
						curGame.options = [Annihilation(), Decimation(), Domination(), Reanimation()]
						curGame.Discover.startDiscover(self, None)
		return None
		
	def discoverDecided(self, option, info):
		curGame = self.Game
		PRINT(curGame, "Kronx Dragonhoof's battlecry unleashs Devastation: %s"%option.name)
		curGame.fixedGuides.append(type(option))
		if option.name == "Annihilation":
			PRINT(curGame, "Devastation: Annihilation deals 5 damage to all other minions")
			targets = curGame.minionsonBoard(self.ID) + curGame.minionsonBoard(3-self.ID)
			extractfrom(self, targets)
			if targets: self.dealsAOE(targets, [5 for minion in targets])
		elif option.name == "Decimation":
			heal = 5 * (2 ** self.countHealDouble())
			PRINT(curGame, "Devastation: Decimation deals 5 damage to the enemy hero and restores %d Health to the player's hero"%heal)
			self.dealsDamage(curGame.heroes[3-self.ID], 5)
			self.restoresHealth(curGame.heroes[self.ID], heal)
		elif option.name == "Domination":
			PRINT(curGame, "Devastation: Domination gives all other friendly minions +2/+2")
			targets = curGame.minionsonBoard(self.ID)
			extractfrom(self, targets)
			for minion in targets: minion.buffDebuff(2, 2)
		else:
			PRINT(curGame, "Devastation: Reanimation summons a 8/8 Dragon with Taunt")
			curGame.summon(ReanimatedDragon(curGame, self.ID), self.position+1, self.ID)
			
class Annihilation:
	def __init__(self):
		self.name = "Annihilation"
		self.description = "Deal 5 damage to all other minions"
		
class Decimation:
	def __init__(self):
		self.name = "Decimation"
		self.description = "Deal 5 damage to the enemy hero. Restore 5 Health to your hero"
		
class Domination:
	def __init__(self):
		self.name = "Domination"
		self.description = "Give your other minions +2/+2"
		
class Reanimation:
	def __init__(self):
		self.name = "Reanimation"
		self.description = "Summon an 8/8 Dragon with Taunt"
		
class ReanimatedDragon(Minion):
	Class, race, name = "Neutral", "Dragon", "Reanimated Dragon"
	mana, attack, health = 8, 8, 8
	index = "Dragons~Neutral~Minion~8~8~8~Dragon~Reanimated Dragon~Uncollectible"
	requireTarget, keyWord, description = False, "", ""
	
	
class UtgardeGrapplesniper(Minion):
	Class, race, name = "Neutral", "", "Utgarde Grapplesniper"
	mana, attack, health = 6, 5, 5
	index = "Dragons~Neutral~Minion~6~5~5~None~Utgarde Grapplesniper~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Both players draw a card. If it's a Dragon, summon it"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		PRINT(curGame, "Utgarde Grapplesniper's battlecry lets both players draw a card. If it's a Dragon, summon it")
		card1 = curGame.Hand_Deck.drawCard(self.ID)[0]
		card2 = curGame.Hand_Deck.drawCard(3-self.ID)[0]
		if card1 and card1.type == "Minion" and "Dragon" in card1.race:
			curGame.summonfromHand(-1, self.ID, -1, self.ID) #不知道我方随从是会召唤到这个随从的右边还是场上最右边。
		if card2 and card2.type == "Minion" and "Dragon" in card2.race:
			curGame.summonfromHand(-1, 3-self.ID, -1, 3-self.ID)
		return None
		
"""Mana 7 cards"""
class EvasiveDrakonid(Minion):
	Class, race, name = "Neutral", "Dragon", "Evasive Drakonid"
	mana, attack, health = 7, 7, 7
	index = "Dragons~Neutral~Minion~7~7~7~Dragon~Evasive Drakonid~Taunt"
	requireTarget, keyWord, description = False, "Taunt", "Taunt. Can't be targeted by spells or Hero Powers"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.marks["Evasive"] = 1
		
		
class Shuma(Minion):
	Class, race, name = "Neutral", "", "Shu'ma"
	mana, attack, health = 7, 1, 7
	index = "Dragons~Neutral~Minion~7~1~7~None~Shu'ma~Legendary"
	requireTarget, keyWord, description = False, "", "At the end of your turn, fill your board with 1/1 Tentacles"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_Shuma(self)]
		
class Trigger_Shuma(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["TurnEnds"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self.entity.Game, "At the end of turn, %s fills player's board with 1/1 Tentacles")
		self.entity.Game.summon([Tentacle_Dragons(self.entity.Game, self.entity.ID) for i in range(6)], (self.entity.position, "leftandRight"), self.entity.ID)
		
class Tentacle_Dragons(Minion):
	Class, race, name = "Neutral", "", "Tentacle"
	mana, attack, health = 1, 1, 1
	index = "Dragons~Neutral~Minion~1~1~1~None~Tentacle~Uncollectible"
	requireTarget, keyWord, description = False, "", ""
	
"""Mana 8 cards"""
class TwinTyrant(Minion):
	Class, race, name = "Neutral", "Dragon", "Twin Tyrant"
	mana, attack, health = 8, 4, 10
	index = "Dragons~Neutral~Minion~8~4~10~Dragon~Twin Tyrant~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Deal 4 damage to two random enemy minions"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		minions = curGame.minionsAlive(3-self.ID)
		if minions:
			if curGame.mode == 0:
				if curGame.guides:
					indices = curGame.guides.pop(0)
					targets = [curGame.minions[3-self.ID][i] for i in indices]
				else:
					num = min(2, len(minions))
					targets = npchoice(minions, num, replace=False)
					indices = [minion.position for minion in targets]
					curGame.fixedGuides.append(tuple(indices))
				PRINT(curGame, "Twin Tyrant's battlecry deals 4 damage to two random enemy minions")
				self.dealsAOE(targets, [damage]*len(targets))
		return None
		
"""Mana 9 cards"""
class DragonqueenAlexstrasza(Minion):
	Class, race, name = "Neutral", "Dragon", "Dragonqueen Alexstrasza"
	mana, attack, health = 9, 8, 8
	index = "Dragons~Neutral~Minion~9~8~8~Dragon~Dragonqueen Alexstrasza~Battlecry~Legendary"
	requireTarget, keyWord, description = False, "", "Battlecry: If your deck has no duplicates, add two Dragons to your hand. They cost (1)"
	poolIdentifier = "Dragons except Dragonqueen Alexstrasza"
	@classmethod
	def generatePool(cls, Game):
		dragons = list(Game.MinionswithRace["Dragon"].values())
		extractfrom(DragonqueenAlexstrasza, dragons)
		return "Dragons except Dragonqueen Alexstrasza", dragons
		
	def effectCanTrigger(self):
		self.effectViable = self.Game.Hand_Deck.noDuplicatesinDeck(self.ID)
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if curGame.Hand_Deck.noDuplicatesinDeck(self.ID) and curGame.Hand_Deck.handNotFull(self.ID):
			if curGame.mode == 0:
				if curGame.guides:
					dragon1, dragon2 = curGame.guides.pop(0)
				else:
					PRINT(curGame, "Dragonqueen Alexstrasza's battlecry adds two random Dragons to player's hand. They cost (1)")
					dragon1, dragon2 = npchoice(curGame.RNGPools["Dragons except Dragonqueen Alexstrasza"], 2, replace=True)
				dragon1, dragon2 = dragon1(curGame, self.ID), dragon2(curGame, self.ID)
				curGame.Hand_Deck.addCardtoHand([dragon1, dragon2], self.ID)
				ManaModification(dragon1, changeby=0, changeto=1).applies()
				ManaModification(dragon2, changeby=0, changeto=1).applies()
				curGame.Manas.calcMana_Single(dragon1)
				curGame.Manas.calcMana_Single(dragon2)
		return None
		
		
class Sathrovarr(Minion):
	Class, race, name = "Neutral", "Demon", "Sathrovarr"
	mana, attack, health = 9, 5, 5
	index = "Dragons~Neutral~Minion~9~5~5~Demon~Sathrovarr~Battlecry~Legendary"
	requireTarget, keyWord, description = True, "", "Battlecry: Choose a friendly minion. Add a copy of it to your hand, deck and battlefield"
	
	def targetExists(self, choice=0):
		return self.selectableFriendlyMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.ID == self.ID and target != self and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			PRINT(self.Game, "Sathrovarr's battlecry puts a copy of friendly minion %s into player's hand, deck, and battlefield"%target.name)
			self.Game.Hand_Deck.addCardtoHand(type(target), self.ID, "CreateUsingType")
			#不知道这个加入牌库是否算作洗入牌库，从而可以触发强能雷象等扳机
			self.Game.Hand_Deck.shuffleCardintoDeck(type(target)(self.Game, self.ID), self.ID)
			#不知道这个召唤的复制是会出现在这个随从右边还是目标随从右边
			Copy = target.selfCopy(self.ID) if target.onBoard else type(target)(self.Game, self.ID)
			self.Game.summon(Copy, self.position+1, self.ID)
		return target
		
"""Druid cards"""
class Embiggen(Spell):
	Class, name = "Druid", "Embiggen"
	requireTarget, mana = False, 0
	index = "Dragons~Druid~Spell~0~Embiggen"
	description = "Give all minions in your deck +2/+2. They cost (1) more (up to 10)"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		PRINT(self.Game, "Embiggen is cast and gives minions in player's deck +2/+2. They cost (1) more (up to 10).")
		for card in self.Game.Hand_Deck.decks[self.ID]:
			if card.type == "Minion":
				card.attack += 2
				card.health += 2
				card.health_upper += 2
				card.health_max += 2 #By default, this healthGain has to be non-negative.
				card.attack_Enchant += 2
				if card.mana < 10:
					ManaModification(card, changeby=+1, changeto=-1).applies()
		return None
		
		
class SecuretheDeck(Quest):
	Class, name = "Druid", "Secure the Deck"
	requireTarget, mana = False, 1
	index = "Dragons~Druid~Spell~1~Secure the Deck~~Quest"
	description = "Sidequest: Attack twice with your hero. Reward: Add 3 'Claw' to your hand"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_SecuretheDeck(self)]
		
class Trigger_SecuretheDeck(QuestTrigger):
	def __init__(self, entity):
		self.blank_init(entity, ["HeroAttackedHero", "HeroAttackedMinion"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return subject == self.entity.Game.heroes[self.entity.ID]
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.progress += 1
		PRINT(self.Game, "After player attacks. Quest Secure the Deck progresses by 1. Current progress: %d"%self.entity.progress)
		if self.entity.progress > 1:
			PRINT(self.Game, "Player has attacked twice and gain Reward: 3 'Claws'")
			self.disconnect()
			extractfrom(self.entity, self.entity.Game.Secrets.sideQuests[self.entity.ID])
			self.entity.Game.Hand_Deck.addCardtoHand([Claw, Claw, Claw], self.entity.ID, "CreateUsingType")
			
			
class StrengthinNumbers(Quest):
	Class, name = "Druid", "Strength in Numbers"
	requireTarget, mana = False, 1
	index = "Dragons~Druid~Spell~1~Strength in Numbers~~Quest"
	description = "Sidequest: Spend 10 Mana on minions. Rewards: Summon a minion from your deck"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_StrengthinNumbers(self)]
		
class Trigger_StrengthinNumbers(QuestTrigger):
	def __init__(self, entity):
		#假设众多势众是使用后扳机
		self.blank_init(entity, ["MinionBeenPlayed"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return subject.ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		curGame = self.entity.Game
		self.entity.progress += number
		PRINT(curGame, "Player plays minion %s and Quest Strength in Numbers progresses by %d. Current progress: %d"%(subject.name, number, self.entity.progress))
		if self.entity.progress > 9:
			PRINT(curGame, "Player has spent at least 10 Mana on playing minions and gains Reward: Summon a minion from your deck")
			self.disconnect()
			extractfrom(self.entity, curGame.Secrets.sideQuests[self.entity.ID])
			if curGame.mode == 0:
				if curGame.guides:
					i = curGame.guides.pop(0)
					if i < 0: return
				else:
					minionsinDeck = [i for i, card in enumerate(curGame.Hand_Deck.decks[self.entity.ID]) if card.type == "Minion"]
					if minionsinDeck:
						i = npchoice(minionsinDeck)
						curGame.fixedGuides.append(i)
					else:
						curGame.fixedGuides.append(-1)
						return
				curGame.summonfromDeck(i, self.entity.ID, -1, self.entity.ID)
				
				
class Treenforcements(Spell):
	Class, name = "Druid", "Treenforcements"
	requireTarget, mana = True, 1
	index = "Dragons~Druid~Spell~1~Treenforcements~Choose One"
	description = "Choose One - Give a minion +2 Health and Taunt; or Summon a 2/2 Taunt"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.chooseOne = 1
		self.options = [SmallRepairs_Option(self), SpinemUp_Option(self)]
		
	def returnTrue(self, choice=0):
		return choice == "ChooseBoth" or choice == 0
		
	def available(self):
		#当场上有全选光环时，变成了一个指向性法术，必须要有一个目标可以施放。
		if self.Game.status[self.ID]["Choose Both"] > 0:
			return self.selectableMinionExists("ChooseBoth")
		else: #Deal 2 AOE damage.
			return self.selectableMinionExists("ChooseBoth") or self.Game.space(self.ID) > 0
			
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if choice == "ChooseBoth" or choice == 0:
			if target:
				PRINT(self.Game, "Treenforcements gives minion %s +2 Health and Taunt"%target.name)
				target.buffDebuff(0, 2)
				target.getsKeyword("Taunt")
		if choice == "ChooseBoth" or choice == 1:
			PRINT(self.Game, "Treenforcements summons a 2/2 Treant")
			self.Game.summon(Treant_Dragons(self.Game, self.ID), -1, self.ID)
		return target
		
class SmallRepairs_Option(ChooseOneOption):
	name, description = "Small Repairs", "Give a minion +2 Health and Taunt"
	index = "Dragons~Druid~Spell~1~Small Repairs~Uncollectible"
	def available(self):
		return self.entity.selectableMinionExists(0)
		
class SpinemUp_Option:
	name, description = "Spin 'em Up", "Summon a Treant"
	index = "Dragons~Druid~Spell~1~Spin'em Up~Uncollectible"
	def available(self):
		return self.entity.Game.space(self.entity.ID)
		
class SmallRepairs(Spell):
	Class, name = "Druid", "Small Repairs"
	requireTarget, mana = True, 1
	index = "Dragons~Druid~Spell~1~Small Repairs~Uncollectible"
	description = "Give a minion +2 Health and Taunt"
	def available(self):
		return self.selectableMinionExists(0)
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			PRINT(self.Game, "Small Repairs is cast and gives minion %s +2 Health and Taunt"%target.name)
			target.buffDebuff(0, 2)
			target.getsKeyword("Taunt")
		return target
		
class SpinemUp(Spell):
	Class, name = "Druid", "Spin 'em Up"
	requireTarget, mana = False, 1
	index = "Dragons~Druid~Spell~1~Spin 'em Up~Uncollectible"
	description = "Summon a 2/2 Treant"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		PRINT(self.Game, "Spin 'em Up is cast and summons a 2/2 Treant")
		self.Game.summon(Treant_Dragons(self.Game, self.ID), -1, self.ID)
		return None
		
		
class BreathofDreams(Spell):
	Class, name = "Druid", "Breath of Dreams"
	requireTarget, mana = False, 2
	index = "Dragons~Druid~Spell~2~Breath of Dreams"
	description = "Draw a card. If you're holding a Dragon, gain an empty Mana Crystal"
	def effectCanTrigger(self):
		self.effectViable = self.Game.Hand_Deck.holdingDragon(self.ID)
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		PRINT(self.Game, "Breath of Dream is cast and player draws a card")
		self.Game.Hand_Deck.drawCard(self.ID)
		if self.Game.Hand_Deck.holdingDragon(self.ID):
			PRINT(self.Game, "Breath of Dreams also gives player an empty Mana Crystal due to player holding a Dragon")
			self.Game.Manas.gainEmptyManaCrystal(1, self.ID)
		return None
		
		
class Shrubadier(Minion):
	Class, race, name = "Druid", "", "Shrubadier"
	mana, attack, health = 2, 1, 1
	index = "Dragons~Druid~Minion~2~1~1~None~Shrubadier~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Summon a 2/2 Treant"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		PRINT(self.Game, "Shrubadier's battlecry summons a 2/2 Treant")
		self.Game.summon(Treant_Dragons(self.Game, self.ID), -1, self.ID)
		return None
		
class Treant_Dragons(Minion):
	Class, race, name = "Druid", "", "Treant"
	mana, attack, health = 2, 2, 2
	index = "Dragons~Druid~Minion~2~2~2~None~Treant~Uncollectible"
	requireTarget, keyWord, description = False, "", ""
	
	
class Aeroponics(Spell):
	Class, name = "Druid", "Aeroponics"
	requireTarget, mana = False, 5
	index = "Dragons~Druid~Spell~5~Aeroponics"
	description = "Draw 2 cards. Costs (2) less for each Treant you control"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersinHand = [Trigger_Aeroponics(self)]
		
	def selfManaChange(self):
		if self.inHand:
			numTreants = 0
			for minion in self.Game.minionsonBoard(self.ID):
				if minion.name == "Treant":
					numTreants += 1
					
			self.mana -= 2 * numTreants
			self.mana = max(0, self.mana)
			
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		PRINT(self.Game, "Aeroponics is cast and player draws 2 cards")
		self.Game.Hand_Deck.drawCard(self.ID)
		self.Game.Hand_Deck.drawCard(self.ID)
		return None
		
class Trigger_Aeroponics(TriggerinHand):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionAppears", "MinionDisappears"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		if self.entity.inHand:
			if signal == "MinionAppears" and subject.name == "Treant":
				return True
			elif signal == "MinionDisappears" and target.name == "Treant":
				return True
		return False
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.Game.Manas.calcMana_Single(self.entity)
		
		
class EmeraldExplorer(Minion):
	Class, race, name = "Druid", "Dragon", "Emerald Explorer"
	mana, attack, health = 6, 4, 8
	index = "Dragons~Druid~Minion~6~4~8~Dragon~Emeral Explorer~Taunt~Battlecry"
	requireTarget, keyWord, description = False, "Taunt", "Taunt. Battlecry: Discover a Dragon"
	poolIdentifier = "Dragons as Druid"
	@classmethod
	def generatePool(cls, Game):
		classes, lists, neutralCards = [], [], []
		classCards = {s : [] for s in Game.ClassesandNeutral}
		for key, value in Game.MinionswithRace["Dragon"].items():
			classCards[key.split('~')[1]].append(value)
			
		for Class in Game.Classes:
			classes.append("Dragons as "+Class)
			lists.append(classCards[Class]+classCards["Neutral"])
		return classes, lists #返回的包含“Class Cards except Hunter”等identifier的列表和其他职业卡表
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if self.ID == curGame.turn and curGame.Hand_Deck.handNotFull(self.ID):
			if curGame.mode == 0:
				if curGame.guides:
					PRINT(curGame, "Emeral Explorer's battlecry adds a Dragon to player's hand")
					curGame.Hand_Deck.addCardtoHand(curGame.guides.pop(0), self.ID, "CreateUsingType")
				else:
					key = "Dragons as "+classforDiscover(self)
					if "byOthers" in comment:
						dragon = npchoice(self.Game.RNGPools[key])
						curGame.fixedGuides.append(dragon)
						PRINT(curGame, "Emeral Explorer's battlecry adds a random Dragon to player's hand")
						curGame.Hand_Deck.addCardtoHand(dragon, self.ID, "CreateUsingType")
					else:
						dragons = npchoice(self.Game.RNGPools[key], 3, replace=False)
						curGame.options = [dragon(curGame, self.ID) for dragon in dragons]
						PRINT(curGame, "Emeral Explorer's battlecry lets player discover a Dragon")
						curGame.Discover.startDiscover(self, None)
		return None
		
		
	def discoverDecided(self, option, info):
		self.Game.fixedGuides.append(type(option))
		PRINT(self.Game, "Dragon %s is put into player's hand."%option.name)
		self.Game.Hand_Deck.addCardtoHand(option, self.ID)
		self.Game.sendSignal("DiscoveredCardPutintoHand", self.ID, self, option, 0, "")
		
		
class GorutheMightree(Minion):
	Class, race, name = "Druid", "", "Goru the Mightree"
	mana, attack, health = 7, 5, 10
	index = "Dragons~Druid~Minion~7~5~10~None~Goru the Mightree~Taunt~Battlecry~Legendary"
	requireTarget, keyWord, description = False, "Taunt", "Taunt. Battlecry: For the rest of the game, your Treants have +1/+1"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		PRINT(self.Game, "Goru the Mightree's battlecry lets player's Treants have +1/+1 for the rest of the game")
		aura = YourTreantsHavePlus1Plus1(self.Game, self.ID)
		self.Game.auras.append(aura)
		aura.auraAppears()
		return None
		
class YourTreantsHavePlus1Plus1(AuraDealer_toMinion):
	def __init__(self, Game, ID):
		self.Game, self.ID = Game, ID
		self.signals, self.auraAffected = ["MinionAppears"], [] #A list of (minion, aura_Receiver)
		
	def applicable(self, target):
		return target.ID == self.ID and target.name == "Treant"
	#All minions appearing on the same side will be subject to the buffAura.
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.applicable(subject)
		
	def applies(self, subject):
		if self.applicable(subject):
			aura_Receiver = BuffAura_Receiver(subject, self, 1, 1)
			aura_Receiver.effectStart()
			
	def auraAppears(self):
		for minion in self.Game.minionsonBoard(self.ID):
			self.applies(minion)
		self.Game.triggersonBoard[self.ID].append((self, "MinionAppears"))
	#没有auraDisappear方法
	#可以通过AuraDealer_toMinion的createCopy方法复制
	
	
class YseraUnleashed(Minion):
	Class, race, name = "Druid", "Dragon", "Ysera, Unleashed"
	mana, attack, health = 9, 4, 12
	index = "Dragons~Druid~Minion~9~4~12~Dragon~Ysera, Unleashed~Battlecry~Legendary"
	requireTarget, keyWord, description = False, "", "Battlecry: Shuffle 7 Dream Portals into your deck. When drawn, summon a random Dragon"
	poolIdentifier = "Dragons to Summon"
	@classmethod
	def generatePool(cls, Game):
		return "Dragons to Summon", list(Game.MinionswithRace["Dragon"].values())
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		PRINT(self.Game, "Ysera, Unleashed's battlecry shuffles 7 Dream Portals into player's deck.")
		portals = [DreamPortal(self.Game, self.ID) for i in range(7)]
		self.Game.Hand_Deck.shuffleCardintoDeck(portals, self.ID)
		return None
		
class DreamPortal(Spell):
	Class, name = "Druid", "Dream Portal"
	requireTarget, mana = False, 9
	index = "Dragons~Druid~Spell~9~Dream Portal~Casts When Drawn~Uncollectible"
	description = "Casts When Drawn. Summon a random Dragon"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if curGame.mode == 0:
			if curGame.guides:
				dragon = curGame.guides.pop(0)
			else:
				dragon = npchoice(curGame.RNGPools["Dragons to Summon"])
				curGame.fixedGuides.append(dragon)
			PRINT(curGame, "Dream Portal is cast and summons a random Dragon.")
			curGame.summon(dragon(curGame, self.ID), -1, self.ID)
		return None
		
		
"""Hunter cards"""
class CleartheWay(Quest):
	Class, name = "Hunter", "Clear the Way"
	requireTarget, mana = False, 1
	index = "Dragons~Hunter~Spell~1~Clear the Way~~Quest"
	description = "Sidequest: Summon 3 Rush minions. Reward: Summon a 4/4 Gryphon with Rush"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_CleartheWay(self)]
		
class Trigger_CleartheWay(QuestTrigger):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionBeenSummoned"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		#不知道召唤随从因为突袭光环而具有突袭是否可以算作任务进度
		return subject.ID == self.entity.ID and subject.keyWords["Rush"] > 0
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.progress += 1
		PRINT(self.Game, "After player summons Rush minion %s, Quest Clear the Way progresses by 1. Current progress: %d"%(subject.name, self.entity.progress))
		if self.entity.progress > 2:
			PRINT(self.Game, "Player has summoned at least 3 Rush minions and gains Reward: Summon a 4/4 Gryphon with Rush")
			self.disconnect()
			extractfrom(self.entity, self.entity.Game.Secrets.sideQuests[self.entity.ID])
			self.entity.Game.summon(Gryphon_Dragons(self.entity.Game, self.entity.ID), -1, self.entity.ID)
			
			
class Gryphon_Dragons(Minion):
	Class, race, name = "Hunter", "Beast", "Gryphon"
	mana, attack, health = 4, 4, 4
	index = "Dragons~Hunter~Minion~4~4~4~Beast~Gryphon~Rush~Uncollectible"
	requireTarget, keyWord, description = False, "Rush", "Rush"
	
	
class DwarvenSharpshooter(Minion):
	Class, race, name = "Hunter", "", "Dwarven Sharpshooter"
	mana, attack, health = 1, 1, 3
	index = "Dragons~Hunter~Minion~1~1~3~None~Dwarven Sharpshooter"
	requireTarget, keyWord, description = False, "", "Your Hero Power can target minions"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.appearResponse = [self.activateAura]
		self.disappearResponse = [self.deactivateAura]
		self.silenceResponse = [self.deactivateAura]
		
	def activateAura(self):
		PRINT(self.Game, "Dwarven Sharpshooter's aura is registered. Player %d's Hero Power can target minions now."%self.ID)
		self.Game.status[self.ID]["Power Can Target Minions"] += 1
		
	def deactivateAura(self):
		PRINT(self.Game, "Dwarven Sharpshooter's aura is removed. Player %d's Hero Powers can't target minions anymore."%self.ID)
		self.Game.status[self.ID]["Power Can Target Minions"] -= 1
		
		
class ToxicReinforcements(Quest):
	Class, name = "Hunter", "Toxic Reinforcements"
	requireTarget, mana = False, 1
	index = "Dragons~Hunter~Spell~1~Toxic Reinforcements~~Quest"
	description = "Sidequest: Use your Hero Power three times. Reward: Summon three 1/1 Leper Gnomes"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_ToxicReinforcement(self)]
		
class Trigger_ToxicReinforcement(QuestTrigger):
	def __init__(self, entity):
		self.blank_init(entity, ["HeroUsedAbility"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.progress += 1
		PRINT(self.Game, "After player uses Hero Power, Quest Toxic Reinforcements progresses by 1. Current progress: %d"%self.entity.progress)
		if self.entity.progress > 2:
			PRINT(self.Game, "Player used Hero Power for the third time and gains Reward: Summon three 1/1 Leper Gnomes")
			self.disconnect()
			extractfrom(self.entity, self.entity.Game.Secrets.sideQuests[self.entity.ID])
			self.entity.Game.summon([LeperGnome_Dragons(self.entity.Game, self.entity.ID) for i in range(3)], (-1, "totheRightEnd"), self.entity.ID)
			
class LeperGnome_Dragons(Minion):
	Class, race, name = "Neutral", "", "Leper Gnome"
	mana, attack, health = 1, 1, 1
	index = "Dragons~Neutral~Minion~1~1~1~None~Leper Gnome~Deathrattle"
	requireTarget, keyWord, description = False, "", "Deathrattle: Deal 2 damage to the enemy hero"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [Deal2DamagetoEnemyHero(self)]
		
class Deal2DamagetoEnemyHero(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self.entity.Game, "Deathrattle: Deal 2 damage to the enemy hero triggers")
		self.entity.dealsDamage(self.entity.Game.heroes[3-self.entity.ID], 2)
		
		
class CorrosiveBreath(Spell):
	Class, name = "Hunter", "Corrosive Breath"
	requireTarget, mana = True, 2
	index = "Dragons~Hunter~Spell~2~Corrosive Breath"
	description = "Deal 3 damage to a minion. If you're holding a Dragon, it also hits the enemy hero"
	def effectCanTrigger(self):
		self.effectViable = self.Game.Hand_Deck.holdingDragon(self.ID)
		
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			damage = (3 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			PRINT(self.Game, "Corrosive Breath is cast and deals %d damage to a minion %s"%(damage, target.name))
			self.dealsDamage(target, damage)
			if self.Game.Hand_Deck.holdingDragon(self.ID):
				PRINT(self.Game, "Corrosive Breath also deals %d damage to the enemy hero"%damage)
				self.dealsDamage(self.Game.heroes[3-self.ID], damage)
		return target
		
		
class PhaseStalker(Minion):
	Class, race, name = "Hunter", "Beast", "Phase Stalker"
	mana, attack, health = 2, 2, 3
	index = "Dragons~Hunter~Minion~2~2~3~Beast~Phase Stalker"
	requireTarget, keyWord, description = False, "", "After you use your Hero Power, cast a Secret from your deck"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_PhaseStalker(self)]
		
class Trigger_PhaseStalker(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["HeroUsedAbility"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self.entity.Game, "After player uses Hero Power, %s puts a Secret from player's deck to battlefield"%self.entity.name)
		self.entity.Game.Secrets.deploySecretsfromDeck(self.entity.ID)
		
		
class DivingGryphon(Minion):
	Class, race, name = "Hunter", "Beast", "Diving Gryphon"
	mana, attack, health = 3, 4, 1
	index = "Dragons~Hunter~Minion~3~4~1~Beast~Diving Gryphon~Rush~Battlecry"
	requireTarget, keyWord, description = False, "Rush", "Rush. Battlecry: Draw a Rush minion from your deck"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if curGame.mode == 0:
			PRINT(curGame, "Diving Gryphon's battlecry lets player draw a Rush minion from deck")
			if curGame.guides:
				i = curGame.guides.pop(0)
				if i < 0: return None
			else:
				rushMinionsinDeck = [i for i, card in enumerate(curGame.Hand_Deck.decks[self.ID]) if card.type == "Minion" and card.keyWords["Rush"] > 0]
				if rushMinionsinDeck:
					i = npchoice(rushMinionsinDeck)
					curGame.fixedGuides.append(i)
				else:
					curGame.fixedGuides.append(-1)
					return None
			curGame.Hand_Deck.drawCard(self.ID, i)[0]
		return None
		
		
class PrimordialExplorer(Minion):
	Class, race, name = "Hunter", "Dragon", "Primordial Explorer"
	mana, attack, health = 3, 2, 3
	index = "Dragons~Hunter~Minion~3~2~3~Dragon~Primordial Explorer~Poisonous~Battlecry"
	requireTarget, keyWord, description = False, "Poisonous", "Poisonous. Battlecry: Discover a Dragon"
	poolIdentifier = "Dragons as Hunter"
	@classmethod
	def generatePool(cls, Game):
		classes, lists, neutralCards = [], [], []
		classCards = {s : [] for s in Game.ClassesandNeutral}
		for key, value in Game.MinionswithRace["Dragon"].items():
			classCards[key.split('~')[1]].append(value)
			
		for Class in Game.Classes:
			classes.append("Dragons as "+Class)
			lists.append(classCards[Class]+classCards["Neutral"])
		return classes, lists #返回的包含“Class Cards except Hunter”等identifier的列表和其他职业卡表
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if self.ID == curGame.turn and curGame.Hand_Deck.handNotFull(self.ID):
			if curGame.mode == 0:
				if curGame.guides:
					PRINT(curGame, "Primordial Explorer's battlecry adds a Dragon to player's hand")
					curGame.Hand_Deck.addCardtoHand(curGame.guides.pop(0), self.ID, "CreateUsingType")
				else:
					key = "Dragons as "+classforDiscover(self)
					if "byOthers" in comment:
						dragon = npchoice(self.Game.RNGPools[key])
						curGame.fixedGuides.append(dragon)
						PRINT(curGame, "Primordial Explorer's battlecry adds a random Dragon to player's hand")
						curGame.Hand_Deck.addCardtoHand(dragon, self.ID, "CreateUsingType")
					else:
						dragons = npchoice(self.Game.RNGPools[key], 3, replace=False)
						curGame.options = [dragon(curGame, self.ID) for dragon in dragons]
						PRINT(curGame, "Primordial Explorer's battlecry lets player discover a Dragon")
						curGame.Discover.startDiscover(self, None)
		return None
		
	def discoverDecided(self, option, info):
		self.Game.fixedGuides.append(type(option))
		PRINT(self.Game, "Dragon %s is put into player's hand."%option.name)
		self.Game.Hand_Deck.addCardtoHand(option, self.ID)
		self.Game.sendSignal("DiscoveredCardPutintoHand", self.ID, self, option, 0, "")
		
		
class Stormhammer(Weapon):
	Class, name, description = "Hunter", "Stormhammer", "Doesn't lose Durability while you control a Dragon"
	mana, attack, durability = 3, 3, 2
	index = "Dragons~Hunter~Weapon~3~3~2~Stormhammer"
	def loseDurability(self):
		controlsDragon = False
		for minion in self.Game.minionsonBoard(self.ID):
			if "Dragon" in minion.race:
				controlsDragon = True
				break
		if controlsDragon:
			PRINT(self.Game, "Weapon %s can't lose Durability as player controls a Dragon"%self.name)
		else:
			self.durability -= 1
			
			
class Dragonbane(Minion):
	Class, race, name = "Hunter", "Mech", "Dragonbane"
	mana, attack, health = 4, 3, 5
	index = "Dragons~Hunter~Minion~4~3~5~Mech~Dragonbane~Legendary"
	requireTarget, keyWord, description = False, "", "After you use your Hero Power, deal 5 damage to a random enemy"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_Dragonbane(self)]
		
class Trigger_Dragonbane(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["HeroUsedAbility"])
		
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
				chars = curGame.charsAlive(3-self.entity.ID)
				if chars:
					char = npchoice(chars)
					curGame.fixedGuides.append((char.position, "minion%d"%char.ID) if char.type == "Minion" else (char.ID, "hero"))
				else:
					curGame.fixedGuides.append((0, ''))
					return
			PRINT(curGame, "After player uses Hero Power, Dragonbane deals 5 damage to random enemy %s"%char.name)
			self.entity.dealsDamage(char, 5)
			
		
class Veranus(Minion):
	Class, race, name = "Hunter", "Dragon", "Veranus"
	mana, attack, health = 6, 7, 6
	index = "Dragons~Hunter~Minion~6~7~6~Dragon~Veranus~Battlecry~Legendary"
	requireTarget, keyWord, description = False, "", "Battlecry: Change the Health of all enemy minions to 1"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		PRINT(self.Game, "Veranus's battlecry changes all enemy minions' Health to 1")
		for minion in fixedList(self.Game.minionsonBoard(3-self.ID)):
			minion.statReset(False, 1)
		return None
		
		
"""Mage cards"""
class ArcaneBreath(Spell):
	Class, name = "Mage", "Arcane Breath"
	requireTarget, mana = True, 1
	index = "Dragons~Mage~Spell~1~Arcane Breath"
	description = "Deal 2 damage to a minion. If you're holding a Dragon, Discover a spell"
	poolIdentifier = "Mage Spells"
	@classmethod
	def generatePool(cls, Game):
		classes, lists = [], []
		for Class in Game.Classes:
			classes.append(Class+" Spells")
			spellsinClass = []
			for key, value in Game.ClassCards[Class].items():
				if "~Spell~" in key:
					spellsinClass.append(value)
			lists.append(spellsinClass)
		return classes, lists
		
	def effectCanTrigger(self):
		self.effectViable = self.Game.Hand_Deck.holdingDragon(self.ID)
		
	def targetExists(self, choice=0):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if target:
			damage = (2 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			PRINT(curGame, "Arcane Breath deals %d damage to minion %s"%(damage, target.name))
			self.dealsDamage(target, damage)
		if self.ID == curGame.turn and curGame.Hand_Deck.holdingDragon(self.ID) and curGame.Hand_Deck.handNotFull(self.ID):
			if curGame.mode == 0:
				if curGame.guides:
					PRINT(curGame, "Arcane Breath adds a spell to player's hand")
					curGame.Hand_Deck.addCardtoHand(curGame.guides.pop(0), self.ID, "CreateUsingType")
				else:
					key = classforDiscover(self)+" Spells"
					if "byOthers" in comment:
						PRINT(curGame, "Arcane Breath adds a random spell to player's hand")
						spell = npchoice(curGame.RNGPools[key])
						curGame.fixedGuides.append(spell)
						curGame.Hand_Deck.addCardtoHand(spell, self.ID, "CreateUsingType")
					else:
						PRINT(curGame, "Arcane Breath lets player discover a spell")
						spells = npchoice(curGame.RNGPools[key], 3, replace=False)
						curGame.options = [spell(curGame, self.ID) for spell in spells]
						curGame.Discover.startDiscover(self, None)
		return target
		
	def discoverDecided(self, option, info):
		PRINT(self.Game, "Spell %s is put into player's hand."%option.name)
		self.Game.fixedGuides.append(type(option))
		self.Game.Hand_Deck.addCardtoHand(option, self.ID)
		self.Game.sendSignal("DiscoveredCardPutintoHand", self.ID, self, option, 0, "")
		
		
class ElementalAllies(Quest):
	Class, name = "Mage", "Elemental Allies"
	requireTarget, mana = False, 1
	index = "Dragons~Mage~Spell~1~Elemental Allies~~Quest"
	description = "Sidequest: Play an Elemental two turns in a row. Reward: Draw 3 spells from your deck"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_ElementalAllies(self)]
		
class Trigger_ElementalAllies(QuestTrigger):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionBeenPlayed"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return subject.ID == self.entity.ID and "Elemental" in subject.race
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		curGame = self.Game
		if curGame.Counters.numElementalsPlayedLastTurn[self.entity.ID] > 0:
			PRINT(curGame, "Player has played Elementals two turns in a row and gains Reward: Draw 3 spells from your deck")
			self.disconnect()
			extractfrom(self.entity, curGame.Secrets.sideQuests[self.entity.ID])
			ownDeck = curGame.Hand_Deck.decks[self.ID]
			for num in range(3):
				if curGame.mode == 0:
					if curGame.guides:
						i = curGame.guides.pop(0)
						if i < 0: break
					else:
						spellsinDeck = [i for i, card in enumerate(ownDeck) if card.type == "Spell"]
						if spellsinDeck:
							i = npchoice(spellsinDeck)
							curGame.fixedGuides.append(i)
						else:
							curGame.fixedGuides.append(-1)
							break
					curGame.Hand_Deck.drawCard(self.ID, i)
					
					
class LearnDraconic(Quest):
	Class, name = "Mage", "Learn Draconic"
	requireTarget, mana = False, 1
	index = "Dragons~Mage~Spell~1~Learn Draconic~~Quest"
	description = "Sidequest: Spend 8 Mana on spells. Reward: Summon a 6/6 Dragon"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_LearnDraconic(self)]
		
class Trigger_LearnDraconic(QuestTrigger):
	def __init__(self, entity):
		self.blank_init(entity, ["SpellBeenPlayed"]) #假设是使用后扳机
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return subject.ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.progress += number
		PRINT(self.Game, "Player spends %d Mana to to play spell, Quest Learn Draconic progresses. Current progress: %d"%(number, self.entity.progress))
		if self.entity.progress > 7:
			PRINT(self.Game, "Player has spent 8 or more Mana on spells and gains Rewards: Summon a 6/6 Dragon")
			self.disconnect()
			extractfrom(self.entity, self.entity.Game.Secrets.sideQuests[self.entity.ID])
			self.entity.Game.summon(DraconicEmissary(self.entity.Game, self.entity.ID), -1, self.entity.ID)
			
class DraconicEmissary(Minion):
	Class, race, name = "Mage", "Dragon", "Draconic Emissary"
	mana, attack, health = 6, 6, 6
	index = "Dragons~Mage~Minion~6~6~6~Dragon~Draconic Emissary~Uncollectible"
	requireTarget, keyWord, description = False, "", ""
	
	
class VioletSpellwing(Minion):
	Class, race, name = "Mage", "Elemental", "Violet Spellwing"
	mana, attack, health = 1, 1, 1
	index = "Dragons~Mage~Minion~1~1~1~Elemental~Violet Spellwing~Deathrattle"
	requireTarget, keyWord, description = False, "", "Deathrattle: Add an 'Arcane Missile' to your hand"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [Add1ArcaneMisslestoYourHand(self)]
#这个奥术飞弹是属于基础卡（无标志）
class Add1ArcaneMisslestoYourHand(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self.entity.Game, "Deathrattle: Add a 'Arcane Missiles' to your hand triggers")
		self.entity.Game.Hand_Deck.addCardtoHand(ArcaneMissiles, self.entity.ID, "CreateUsingType")
		
		
class Chenvaala(Minion):
	Class, race, name = "Mage", "Elemental", "Chenvaala"
	mana, attack, health = 3, 2, 5
	index = "Dragons~Mage~Minion~3~2~5~Elemental~Chenvaala~Legendary"
	requireTarget, keyWord, description = False, "", "After you cast three spells in a turn, summon a 5/5 Elemental"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_Chenvaala(self)]
		self.appearResponse = [self.resetCounter]
		self.disappearResponse = [self.resetCounter]
		self.silenceResponse = [self.resetCounter]
		
	def resetCounter(self):
		for trig in self.triggersonBoard:
			if type(trig) == Trigger_Chenvaala:
				trig.counter = 0
				
class Trigger_Chenvaala(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["SpellBeenPlayed", "TurnEnds", "TurnStarts"])
		self.counter = 0
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		if signal == "SpellBeenPlayed":
			return self.entity.onBoard and subject.ID == self.entity.ID
		return True
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		if signal == "SpellBeenPlayed":
			self.counter += 1
			PRINT(self.entity.Game, "Player casts a spell and %s records its current progress to summon a 5/5 Elemental: %d"%(self.entity.name, self.counter))
			if self.counter > 0 and self.counter % 3 == 0:
				PRINT(self.entity.Game, "Player has cast %d spells, %s summons a 5/5 Elemental"%(self.counter, self.entity.name))
				self.entity.Game.summon(SnowElemental(self.entity.Game, self.entity.ID), self.entity.position+1, self.entity.ID)
		else: #At the start/end of turn, the counter is reset
			self.entity.resetCounter()
			
	#Chenvaala的扳机在游戏内复制的时候不会保留counter
	def createCopy(self, recipientGame):
		if self not in recipientGame.copiedObjs: #这个扳机没有被复制过
			entityCopy = self.entity.createCopy(recipientGame)
			trigCopy = self.selfCopy(entityCopy)
			trigCopy.counter = self.counter
			recipientGame.copiedObjs[self] = trigCopy
			return trigCopy
		else: #一个扳机被复制过了，则其携带者也被复制过了
			return recipientGame.copiedObjs[self]
			
			
class SnowElemental(Minion):
	Class, race, name = "Mage", "Elemental", "Snow Elemental"
	mana, attack, health = 5, 5, 5
	index = "Dragons~Mage~Minion~5~5~5~Elemental~Snow Elemental~Uncollectible"
	requireTarget, keyWord, description = False, "", ""
	
	
class AzureExplorer(Minion):
	Class, race, name = "Mage", "Dragon", "Azure Explorer"
	mana, attack, health = 4, 2, 3
	index = "Dragons~Mage~Minion~4~2~3~Dragon~Azure Explorer~Spell Damage~Battlecry"
	requireTarget, keyWord, description = False, "", "Spell Damage +2. Battlecry: Discover a Dragon"
	poolIdentifier = "Dragons as Mage"
	@classmethod
	def generatePool(cls, Game):
		classes, lists, neutralCards = [], [], []
		classCards = {s : [] for s in Game.ClassesandNeutral}
		for key, value in Game.MinionswithRace["Dragon"].items():
			classCards[key.split('~')[1]].append(value)
			
		for Class in Game.Classes:
			classes.append("Dragons as "+Class)
			lists.append(classCards[Class]+classCards["Neutral"])
		return classes, lists #返回的包含“Class Cards except Hunter”等identifier的列表和其他职业卡表
		
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.keyWords["Spell Damage"] = 2
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if self.ID == curGame.turn and curGame.Hand_Deck.handNotFull(self.ID):
			if curGame.mode == 0:
				if curGame.guides:
					PRINT(curGame, "Azure Explorer's battlecry adds a Dragon to player's hand")
					curGame.Hand_Deck.addCardtoHand(curGame.guides.pop(0), self.ID, "CreateUsingType")
				else:
					key = "Dragons as "+classforDiscover(self)
					if "byOthers" in comment:
						dragon = npchoice(self.Game.RNGPools[key])
						curGame.fixedGuides.append(dragon)
						PRINT(curGame, "Azure Explorer's battlecry adds a random Dragon to player's hand")
						curGame.Hand_Deck.addCardtoHand(dragon, self.ID, "CreateUsingType")
					else:
						dragons = npchoice(self.Game.RNGPools[key], 3, replace=False)
						curGame.options = [dragon(curGame, self.ID) for dragon in dragons]
						PRINT(curGame, "Azure Explorer's battlecry lets player discover a Dragon")
						curGame.Discover.startDiscover(self, None)
		return None
		
	def discoverDecided(self, option, info):
		self.Game.fixedGuides.append(type(option))
		PRINT(self.Game, "Dragon %s is put into player's hand."%option.name)
		self.Game.Hand_Deck.addCardtoHand(option, self.ID)
		self.Game.sendSignal("DiscoveredCardPutintoHand", self.ID, self, option, 0, "")
		
		
class MalygossFrostbolt(Spell):
	Class, name = "Mage", "Malygos's Frostbolt"
	requireTarget, mana = True, 0
	index = "Dragons~Mage~Spell~0~Malygos's Frostbolt~Uncollectible~Legendary"
	description = "Deal 3 damage to a character and Freeze it"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			damage = (3 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			PRINT(self.Game, "Malygos's Frostbolt deals %d damage to %s and freezes it."%(damage, target.name))
			self.dealsDamage(target, damage)
			target.getsFrozen()
		return target
		
class MalygossMissiles(Spell):
	Class, name = "Mage", "Malygos's Missiles"
	requireTarget, mana = False, 1
	index = "Dragons~Mage~Spell~1~Malygos's Missiles~Uncollectible~Legendary"
	description = "Deal 6 damage randomly split among all enemies"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		num = (6 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		side, curGame = 3-self.ID, self.Game
		if curGame.mode == 0:
			PRINT(curGame, "Malygos's Missiles launches %d missiles."%num)
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
				PRINT(curGame, "Malygos's Missiles deals 1 damage to %s"%char.name)
				self.dealsDamage(char, 1)
		return None
		
		
class MalygossNova(Spell):
	Class, name = "Mage", "Malygos's Nova"
	requireTarget, mana = False, 1
	index = "Dragons~Mage~Spell~1~Malygos's Nova~Uncollectible~Legendary"
	description = "Freeze all enemy minions"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		PRINT(self.Game, "Malygos's Nova freezes all enemy minions")
		for minion in fixedList(self.Game.minionsonBoard(3-self.ID)):
			minion.getsFrozen()
		return None
		
class MalygossPolymorph(Spell):
	Class, name = "Mage", "Malygos's Polymorph"
	requireTarget, mana = True, 1
	index = "Dragons~Mage~Spell~1~Malygos's Polymorph~Uncollectible~Legendary"
	description = "Transform a minion into a 1/1 Sheep"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			PRINT(self.Game, "Malygos's Polymorph transforms minion %s into a 1/1 Sheep."%target.name)
			newMinion = MalygossSheep(self.Game, target.ID)
			self.Game.transform(target, newMinion)
			target = newMinion
		return target
			
class MalygossTome(Spell):
	Class, name = "Mage", "Malygos's Tome"
	requireTarget, mana = False, 1
	index = "Dragons~Mage~Spell~1~Malygos's Tome~Uncollectible~Legendary"
	description = "Add 3 random Mage spells to your hand"
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
		PRINT(curGame, "Malygos's Tome is cast and adds 3 random Mage card to player's hand.")	
		if curGame.Hand_Deck.handNotFull(self.ID):
			if curGame.guides:
				mageSpells = list(curGame.guides.pop(0))
			else:
				mageSpells = npchoice(curGame.RNGPools["Mage Spells"], 3, replace=True)
				curGame.fixedGuides.append(tuple(mageSpells))
			curGame.Hand_Deck.addCardtoHand(mageSpells, self.ID, "CreateUsingType")
		return None
		
class MalygossExplosion(Spell):
	Class, name = "Mage", "Malygos's Explosion"
	requireTarget, mana = False, 2
	index = "Dragons~Mage~Spell~2~Malygos's Explosion~Uncollectible~Legendary"
	description = "Deal 2 damage to all enemy minions"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		damage = (1 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		targets = self.Game.minionsonBoard(3-self.ID)
		PRINT(self.Game, "Malygos's Explosion deals %d damage to all enemy minions"%damage)
		self.dealsAOE(targets, [damage for obj in targets])
		return None
		
class MalygossIntellect(Spell):
	Class, name = "Mage", "Malygos's Intellect"
	requireTarget, mana = False, 3
	index = "Dragons~Mage~Spell~3~Malygos's Intellect~Uncollectible~Legendary"
	description = "Draw 4 cards"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		PRINT(self.Game, "Malygos's Intellect lets player draws two cards")
		for i in range(4):
			self.Game.Hand_Deck.drawCard(self.ID)
		return None
		
class MalygossFireball(Spell):
	Class, name = "Mage", "Malygos's Fireball"
	requireTarget, mana = True, 4
	index = "Dragons~Mage~Spell~3~Malygos's Fireball~Uncollectible~Legendary"
	description = "Deal 8 damage"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			damage = (8 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			PRINT(self.Game, "Malygos's Fireball deals %d damage to %s"%(damage, target.name))
			self.dealsDamage(target, damage)
		return target
		
class MalygossFlamestrike(Spell):
	Class, name = "Mage", "Malygos's Flamestrike"
	requireTarget, mana = False, 7
	index = "Dragons~Mage~Spell~7~Malygos's Flamestrike~Uncollectible~Legendary"
	description = "Deal 8 damage to all enemy minions"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		damage = (8 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		PRINT(self.Game, "Malygos's Flamestrike deals %d damage to all enemy minions"%damage)
		targets = self.Game.minionsonBoard(3-self.ID)
		self.dealsAOE(targets, [damage for minion in targets])
		return None
		
class MalygossSheep(Minion):
	Class, race, name = "Mage", "Beast", "Malygos's Sheep"
	mana, attack, health = 1, 1, 1
	index = "Dragons~Mage~Minion~1~1~1~Beast~Malygos's Sheep~Uncollectible~Legendary"
	requireTarget, keyWord, description = False, "", ""
	
MalygosUpgradedSpells = [MalygossFrostbolt, MalygossMissiles, MalygossNova, MalygossPolymorph, MalygossTome,
						MalygossExplosion, MalygossIntellect, MalygossFireball, MalygossFlamestrike
						]
						
class MalygosAspectofMagic(Minion):
	Class, race, name = "Mage", "Dragon", "Malygos, Aspect of Magic"
	mana, attack, health = 5, 2, 8
	index = "Dragons~Mage~Minion~5~2~8~Dragon~Malygos, Aspect of Magic~Battlecry~Legendary"
	requireTarget, keyWord, description = False, "", "Battlecry: If you're holding a Dragon, Discover an upgraded Mage spell"
	
	def effectCanTrigger(self):
		self.effectViable = self.Game.Hand_Deck.holdingDragon(self.ID, self)
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if curGame.Hand_Deck.holdingDragon(self.ID) and curGame.Hand_Deck.handNotFull(self.ID) and self.ID == curGame.turn:
			if curGame.guides:
				PRINT(curGame, "Malygos, Aspect of Magic's battlecry puts an upgraded Mage spell to player's hand")
				curGame.Hand_Deck.addCardtoHand(curGame.guides.pop(0), self.ID, "CreateUsingType")
			else:
				if "byOthers" in comment:
					spell = npchoice(MalygosUpgradedSpells)
					curGame.fixedGuides.append(spell)
					PRINT(curGame, "Malygos, Aspect of Magic's battlecry adds a random upgraded Mage spell to player's hand")
					curGame.Hand_Deck.addCardtoHand(spell, self.ID, "CreateUsingType")
				else:
					spells = npchoice(MalygosUpgradedSpells, 3, replace=False)
					curGame.options = [spell(curGame, self.ID) for spell in spells]
					PRINT(curGame, "Malygos, Aspect of Magic's battlecry lets player discover an upgraded Mage spell")
					curGame.Discover.startDiscover(self, None)
		return None
		
	def discoverDecided(self, option, info):
		self.Game.fixedGuides.append(type(option))
		PRINT(self.Game, "Upgraded Mage spell %s is put into player's hand."%option.name)
		self.Game.Hand_Deck.addCardtoHand(option, self.ID)
		self.Game.sendSignal("DiscoveredCardPutintoHand", self.ID, self, option, 0, "")
		
		
#火球滚滚会越过休眠物。直接打在相隔的其他随从上。圣盾随从会分担等于自己当前生命值的伤害。
class RollingFireball(Spell):
	Class, name = "Mage", "Rolling Fireball"
	requireTarget, mana = True, 5
	index = "Dragons~Mage~Spell~5~Rolling Fireball"
	description = "Deal 8 damage to a minion. Any excess damage continues to the left or right"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			damage = (8 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			curGame = self.Game
			if curGame.mode == 0:
				minion, direction, damageleft, infos = None, "", damage, []
				damageDealt = min(target.health, damageleft) if target.health > 0 else 0
				damageleft -= damageDealt
				if curGame.guides:
					i, where, direction = curGame.guides.pop(0)
					if where: minion = curGame.find(i, where)
					else: minion = None
				else:
					#火球滚滚打到牌库中的随从是没有任何后续效果的。不知道目标随从提前死亡的话会如何
					if target.onBoard:
						neighbors, dist = cuirGame.adjacentMinions2(target, True) #对目标进行伤害之后，在场上寻找其相邻随从，决定滚动方向。
						#direction = 1 means fireball rolls right, direction = 1 is left
						if dist == "1":
							if nprandint(2) == 1: minion, direction = neighbors[1], 1
							else: minion, direction = neighbors[0], 0
						elif dist < 0: minion, direction = neighbors[0], 0
						elif dist == 2: minion, direction = neighbors[0], 1
						infos.append((minion.position, "minion%d"%minion.ID, direction))
					else: #如果可以在手牌中找到那个随从时
						#火球滚滚打到手牌中的随从时，会判断目前那个随从在手牌中位置，如果在从左数第3张的话，那么会将过量伤害传递给场上的2号或者4号随从。
						try: i = curGame.Hand_Deck.hands[target.ID].index(target)
						except: i = -1
						if i > -1:
							minions = curGame.minionsonBoard(3-self.ID) #对手牌中的随从进行伤害之后，寻找场上合适的随从并确定滚动方向。
							if i == 0:
								direction = 1
								if len(minions) > 1: minion = minions[1]
							elif i + 1 < len(minions): #手牌中第4张（编号3），如果场上有5张随从，仍然随机
								if nprandint(2): minion, direction = minions[position+1], 1
								else: minion, direction = minions[position-1], 0
							#如果随从在手牌中的编号很大，如手牌中第5张（编号4），则如果场上有5张或者以下随从，则都会向左滚
							elif len(minions) <= i + 1: minion, direction = minions[-1], 0
							infos.append((minion.position, "minion%d"%minion.ID, direction))
						else:
							infos.append((0, '', ''))
							minion = None
				self.dealsDamage(target, damageDealt)
				#当已经决定了要往哪个方向走之后
				while True:
					if minion is None: break #如果下个目标没有随从了，则停止循环
					else: #还有下个随从
						if minion.type == "Minion":
							damageDealt = min(minion.health, damageleft) if minion.health > 0 else 0
							self.dealsDamage(minion, damageDealt)
						else: damageDealt = 0 #休眠物可以被直接跳过，伤害为0
						damageleft -= damageDealt
						if damageleft <= 0: break #如果没有剩余伤害了，结束循环。
						else:
							neighbors, dist = curGame.adjacentMinions2(minion, True)
							if direction: #roll towards right
								if dist > 0: minion = neighbors[2-dist]
								else: break
							else:
								if dist == 1 or dist == -1: minion = neighbors[0]
								else: break
		return target
		
		
class Dragoncaster(Minion):
	Class, race, name = "Mage", "", "Dragoncaster"
	mana, attack, health = 7, 4, 4
	index = "Dragons~Mage~Minion~7~4~4~None~Dragoncaster~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: If you're holding a Dragon, your next spell this turn costs (0)"
	
	def effectCanTrigger(self):
		self.effectViable = self.Game.Hand_Deck.holdingDragon(self.ID)
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if self.Game.Hand_Deck.holdingDragon(self.ID):
			PRINT(self.Game, "Dragoncaster's battlecry makes player's next spell cost (0) this turn.")
			tempAura = YourNextSpellCosts0ThisTurn(self.Game, self.ID)
			self.Game.Manas.CardAuras.append(tempAura)
			tempAura.auraAppears()
		return None
		
class YourNextSpellCosts0ThisTurn(TempManaEffect):
	def __init__(self, Game, ID):
		self.Game, self.ID = Game, ID
		self.changeby, self.changeto = 0, 0
		self.temporary = True
		self.auraAffected = []
		
	def applicable(self, target):
		return target.ID == self.ID and target.type == "Spell"
		
	def selfCopy(self, recipientGame):
		return type(self)(recipientGame, self.ID)
		
		
class ManaGiant(Minion):
	Class, race, name = "Mage", "Elemental", "Mana Giant"
	mana, attack, health = 8, 8, 8
	index = "Dragons~Mage~Minion~8~8~8~Elemental~Mana Giant"
	requireTarget, keyWord, description = False, "", "Costs (1) less for each card you've played this game that didn't start in your deck"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersinHand = [Trigger_ManaGiant(self)]
		
	def selfManaChange(self):
		if self.inHand:
			self.mana -= self.Game.Counters.createdCardsPlayedThisGame[self.ID]
			self.mana = max(self.mana, 0)
			
class Trigger_ManaGiant(TriggerinHand):
	def __init__(self, entity):
		#假设这个费用改变扳机在“当你使用一张法术之后”。不需要预检测
		self.blank_init(entity, ["SpellBeenPlayed"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.inHand and subject.ID == self.entity.ID and subject.identity not in self.entity.Game.Hand_Deck.startingDeckIdentities[self.entity.ID]
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.Game.Manas.calcMana_Single(self.entity)
		
		
"""Paladin cards"""
class RighteousCause(Quest):
	Class, name = "Paladin", "Righteous Cause"
	requireTarget, mana = False, 1
	index = "Dragons~Paladin~Spell~1~Righteous Cause~~Quest"
	description = "Sidequest: Summon 5 minions. Reward: Give your minions +1/+1"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_RighteousCause(self)]
		
class Trigger_RighteousCause(QuestTrigger):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionBeenSummoned"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return subject.ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.progress += 1
		PRINT(self.Game, "After player summons minion %s, Quest Clear the Way progresses by 1. Current progress: %d"%(subject.name, self.entity.progress))
		if self.entity.progress > 4:
			PRINT(self.Game, "Player has summoned at least 5 minions and gains Reward: Give your minions +1/+1")
			self.disconnect()
			extractfrom(self.entity, self.entity.Game.Secrets.sideQuests[self.entity.ID])
			for minion in fixedList(self.entity.Game.minionsonBoard(self.entity.ID)):
				minion.buffDebuff(1, 1)
				
				
class SandBreath(Spell):
	Class, name = "Paladin", "Sand Breath"
	requireTarget, mana = True, 1
	index = "Dragons~Paladin~Spell~1~Sand Breath"
	description = "Give a minion +1/+2. Give it Divine Shield if you're holding a Dragon"
	def effectCanTrigger(self):
		self.effectViable = self.Game.Hand_Deck.holdingDragon(self.ID)
		
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			PRINT(self.Game, "Sand Breath is cast and gives minion %s +1/+2"%target.name)
			target.buffDebuff(1, 2)
			if self.Game.Hand_Deck.holdingDragon(self.ID):
				PRINT(self.Game, "Sand Breath also gives the minion Divine Shield")
				target.getsKeyword("Divine Shield")
		return target	
		
		
class Sanctuary(Quest):
	Class, name = "Paladin", "Sanctuary"
	requireTarget, mana = False, 2
	index = "Dragons~Paladin~Spell~2~Sanctuary~~Quest"
	description = "Sidequest: Take no damage for a turn. Reward: Summon a 3/6 minion with Taunt"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_Sanctuary(self)]
		
class Trigger_Sanctuary(QuestTrigger):
	def __init__(self, entity):
		self.blank_init(entity, ["TurnStarts"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return ID == self.entity.ID #在我方回合开始时会触发
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		if self.entity.Game.Counters.damageonHeroThisTurn[self.entity.ID] == 0:
			PRINT(self.Game, "Player ends turn with without taking damage this turn and gains Reward: Summon a 4/6 with Taunt")
			self.disconnect()
			extractfrom(self.entity, self.entity.Game.Secrets.sideQuests[self.entity.ID])
			self.entity.Game.summon(IndomitableChampion(self.entity.Game, self.entity.ID), -1, self.entity.ID)
			
class IndomitableChampion(Minion):
	Class, race, name = "Paladin", "", "Indomitable Champion"
	mana, attack, health = 4, 3, 6
	index = "Dragons~Paladin~Minion~4~3~6~None~Indomitable Champion~Taunt~Uncollectible"
	requireTarget, keyWord, description = False, "Taunt", "Taunt"
	
	
class BronzeExplorer(Minion):
	Class, race, name = "Paladin", "Dragon", "Bronze Explorer"
	mana, attack, health = 3, 2, 3
	index = "Dragons~Paladin~Minion~3~2~3~Dragon~Bronze Explorer~Lifesteal~Battlecry"
	requireTarget, keyWord, description = False, "Lifesteal", "Lifesteal. Battlecry: Discover a Dragon"
	poolIdentifier = "Dragons as Paladin"
	@classmethod
	def generatePool(cls, Game):
		classes, lists, neutralCards = [], [], []
		classCards = {s : [] for s in Game.ClassesandNeutral}
		for key, value in Game.MinionswithRace["Dragon"].items():
			classCards[key.split('~')[1]].append(value)
			
		for Class in Game.Classes:
			classes.append("Dragons as "+Class)
			lists.append(classCards[Class]+classCards["Neutral"])
		return classes, lists #返回的包含“Class Cards except Hunter”等identifier的列表和其他职业卡表
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if self.ID == curGame.turn and curGame.Hand_Deck.handNotFull(self.ID):
			if curGame.mode == 0:
				if curGame.guides:
					PRINT(curGame, "Bronze Explorer's battlecry adds a Dragon to player's hand")
					curGame.Hand_Deck.addCardtoHand(curGame.guides.pop(0), self.ID, "CreateUsingType")
				else:
					key = "Dragons as "+classforDiscover(self)
					if "byOthers" in comment:
						dragon = npchoice(self.Game.RNGPools[key])
						curGame.fixedGuides.append(dragon)
						PRINT(curGame, "Bronze Explorer's battlecry adds a random Dragon to player's hand")
						curGame.Hand_Deck.addCardtoHand(dragon, self.ID, "CreateUsingType")
					else:
						dragons = npchoice(self.Game.RNGPools[key], 3, replace=False)
						curGame.options = [dragon(curGame, self.ID) for dragon in dragons]
						PRINT(curGame, "Bronze Explorer's battlecry lets player discover a Dragon")
						curGame.Discover.startDiscover(self, None)
		return None
		
	def discoverDecided(self, option, info):
		self.Game.fixedGuides.append(type(option))
		PRINT(self.Game, "Dragon %s is put into player's hand."%option.name)
		self.Game.Hand_Deck.addCardtoHand(option, self.ID)
		self.Game.sendSignal("DiscoveredCardPutintoHand", self.ID, self, option, 0, "")
		
		
class SkyClaw(Minion):
	Class, race, name = "Paladin", "Mech", "Sky Claw"
	mana, attack, health = 3, 1, 2
	index = "Dragons~Paladin~Minion~3~1~2~Mech~Sky Claw~Battlecry"
	requireTarget, keyWord, description = False, "", "Your other Mechs have +1 Attack. Battlecry: Summon two 1/1 Microcopters"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.auras["Buff Aura"] = BuffAura_Dealer_All(self, 1, 0)
		
	def applicable(self, target):
		return "Mech" in target.race
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		PRINT(self.Game, "Sky Claw's battlecry summons two 1/1 Microcopters")
		pos = (self.position, "leftandRight") if self.onBoard else (-1, "totheRightEnd")
		self.Game.summon([Microcopter(self.Game, self.ID) for i in range(2)], pos, self.ID)
		return None
		
class Microcopter(Minion):
	Class, race, name = "Paladin", "Mech", "Microcopter"
	mana, attack, health = 1, 1, 1
	index = "Dragons~Paladin~Minion~1~1~1~Mech~Microcopter~Uncollectible"
	requireTarget, keyWord, description = False, "", ""
	
	
class DragonriderTalritha(Minion):
	Class, race, name = "Paladin", "", "Dragonrider Talritha"
	mana, attack, health = 3, 3, 3
	index = "Dragons~Paladin~Minion~3~3~3~None~Dragonrider Talritha~Deathrattle~Legendary"
	requireTarget, keyWord, description = False, "", "Deathrattle: Give a Dragon in your hand +3/+3 and this Deathrattle"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [GiveaDragoninHandPlus3Plus3AndThisDeathrattle(self)]
		
class GiveaDragoninHandPlus3Plus3AndThisDeathrattle(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		curGame = self.entity.Game
		ownHand = curGame.Hand_Deck.hands[self.entity.ID]
		PRINT(curGame, "Deathrattle: Give a Dragon in your hand +3/+3 and this Deathrattle triggers.")
		dragonsinHand = [i for i, card in enumerate(ownHand) if card.type == "Minion" and "Dragon" in card.race]
		if curGame.mode == 0:
			if curGame.guides:
				i = curGame.guides.pop(0)
				if i < 0: return
			else:
				if dragonsinHand:
					i = npchoice(dragonsinHand)
					curGame.fixedGuides.append(i)
				else:
					curGame.fixedGuides.append(-1)
					return
			dragon = ownHand[i]
			dragon.buffDebuff(3, 3)
			dragon.deathrattles.append(type(self)(dragon))
			
			
class LightforgedZealot(Minion):
	Class, race, name = "Paladin", "", "Lightforged Zealot"
	mana, attack, health = 4, 4, 2
	index = "Dragons~Paladin~Minion~4~4~2~None~Lightforged Zealot~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: If your deck has no Neutral cards, equip a 4/2 Truesilver Champion"
	
	def effectCanTrigger(self):
		self.effectViable = True
		for card in self.Game.Hand_Deck.decks[self.ID]:
			if card.Class == "Neutral":
				self.effectViable = False
				break
				
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		noNeutralCardsinDeck = True
		for card in self.Game.Hand_Deck.decks[self.ID]:
			if card.Class == "Neutral":
				noNeutralCardsinDeck = False
				break
		if noNeutralCardsinDeck:
			PRINT(self.Game, "Lightforged Zealot's battlecry lets player equip a 4/2 Truesilver Champion")
			self.Game.equipWeapon(TruesilverChampion(self.Game, self.ID))
		return None
		
		
class NozdormutheTimeless(Minion):
	Class, race, name = "Paladin", "Dragon", "Nozdormu the Timeless"
	mana, attack, health = 4, 8, 8
	index = "Dragons~Paladin~Minion~4~8~8~Dragon~Nozdormu the Timeless~Battlecry~Legendary"
	requireTarget, keyWord, description = False, "", "Battlecry: Set each player to 10 Mana Crystals"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		PRINT(self.Game, "Nozdormu the Timeless's battlecry sets both players' mana crystals to 10.")
		self.Game.Manas.setManaCrystal(10, 1)
		self.Game.Manas.setManaCrystal(10, 2)
		return None
		
		
class AmberWatcher(Minion):
	Class, race, name = "Paladin", "Dragon", "Amber Watcher"
	mana, attack, health = 5, 4, 6
	index = "Dragons~Paladin~Minion~5~4~6~Dragon~Amber Watcher~Battlecry"
	requireTarget, keyWord, description = True, "", "Battlecry: Restore 8 Health"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			heal = 8 * (2 ** self.countHealDouble())
			PRINT(self.Game, "Amber Watcher's battlecry restores %d health to %s"%(heal, target.name))
			self.restoresHealth(target, heal)
		return target
		
		
class LightforgedCrusader(Minion):
	Class, race, name = "Paladin", "", "Lightforged Crusader"
	mana, attack, health = 7, 7, 7
	index = "Dragons~Paladin~Minion~7~7~7~None~Lightforged Crusader~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: If your deck has no Neutral cards, add 5 random Paladin cards to your hand"
	poolIdentifier = "Paladin Cards"
	@classmethod
	def generatePool(cls, Game):
		return "Paladin Cards", list(Game.ClassCards["Paladin"].values())
		
	def effectCanTrigger(self):
		self.effectViable = True
		for card in self.Game.Hand_Deck.decks[self.ID]:
			if card.Class == "Neutral":
				self.effectViable = False
				break
				
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if curGame.mode == 0:
			if curGame.guides:
				cards = curGame.guides.pop(0)
				if not cards: return None
			else:
				noNeutralCardsinDeck = True
				for card in curGame.Hand_Deck.decks[self.ID]:
					if card.Class == "Neutral":
						noNeutralCardsinDeck = False
						break
				if noNeutralCardsinDeck:
					cards = npchoice(curGame.RNGPools["Paladin Cards"], 5, replace=True)
					curGame.fixedGuides.append(tuple(cards))
				else:
					curGame.fixedGuides.append(())
					return None
			PRINT(curGame, "Lightforged Crusader's battlecry adds 5 random Paladin cards to player's hand")
			curGame.Hand_Deck.addCardtoHand(cards, self.ID, "CreateUsingType")
		return None
		
		
"""Priest cards"""
class WhispersofEVIL(Spell):
	Class, name = "Priest", "Whispers of EVIL"
	requireTarget, mana = False, 0
	index = "Dragons~Priest~Spell~0~Whispers of EVIL"
	description = "Add a Lackey to your hand"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		PRINT(curGame, "Whispers of EVIL adds a Lackey to player's hand")
		if curGame.mode == 0:
			if curGame.guides:
				lackey = curGame.guides.pop(0)
			else:
				lackey = npchoice(Lackeys)
				curGame.fixedGuides.append(lackey)
			curGame.Hand_Deck.addCardtoHand(lackey, self.ID, "CreateUsingType")
		return None
		
		
class DiscipleofGalakrond(Minion):
	Class, race, name = "Priest", "", "Disciple of Galakrond"
	mana, attack, health = 1, 1, 2
	index = "Dragons~Priest~Minion~1~1~2~None~Disciple of Galakrond~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Invoke Galakrond"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		PRINT(self.Game, "Disciple of Galakrond's battlecry Invokes Galakrond")
		invokeGalakrond(self.Game, self.ID)
		return None
		
		
class EnvoyofLazul(Minion):
	Class, race, name = "Priest", "", "Envoy of Lazul"
	mana, attack, health = 2, 2, 2
	index = "Dragons~Priest~Minion~2~2~2~None~Envoy of Lazul~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Look at 3 cards. Guess which one is in your opponent's hand to get a copy of it"
	
	#One card current in opponent's hand( can be created card). Two other cards are the ones currently in opponent's deck but not in hand.
	#If less than two cards left in opponent's deck, two copies of cards in opponent's starting deck is given.
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		#假设无论我方手牌是否已满，只要对方有牌，就可以进行发现
		curGame = self.Game
		HD = curGame.Hand_Deck
		if HD.hands[3-self.ID] and curGame.turn == self.ID:
			if curGame.mode == 0:
				if curGame.guides:
					i = curGame.guides.pop(0)
					if i < 0:
						PRINT(curGame, "Envoy of Lazul's battlecry doesn't add card, because player guessed wrong.")
						return None
					else: HD.addCardtoHand(HD.hands[3-self.ID][i].selfCopy(self.ID), self.ID)
				else:
					#假设被沙德沃克调用时无效果
					if "byOthers" not in comment:
						cardinHand = npchoice(HD.hands[3-self.ID])
						cards, cardTypes = [], [type(cardinHand)]
						for card in HD.decks[3-self.ID]:
							if type(card) not in cardTypes:
								cards.append(card)
								cardTypes.append(type(card))
						if len(cards) < 2:
							cardTypes = [type(cardinHand)]
							for card in HD.initialDecks[3-self.ID]:
								if card not in cardTypes:
									cardTypes.append(card)
							cards = npchoice(cardTypes, 2, replace=False)
							curGame.options = [cardinHand] + [card(curGame, 3-self.ID) for card in cards]
						else:
							cards = npchoice(cards, 2, replace=False)
							curGame.options = list(cards) + [cardinHand]
						npshuffle(curGame.options)
						curGame.Discover.startDiscover(self, None)
		return None
		
	def discoverDecided(self, option, info):
		curGame = self.Game
		if option.inHand:
			i = curGame.Hand_Deck.hands[3-self.ID].index(option)
			curGame.fixedGuides.append(i)
			PRINT(curGame, "Bingo. Copy of %s from enemy hand is put into player's hand."%option.name)
			Copy = option.selfCopy(self.ID)
			curGame.Hand_Deck.addCardtoHand(Copy, self.ID)
		else:
			curGame.fixedGuides.append(-1)
			rightCard = None
			for card in curGame.options:
				if card.inHand:
					rightCard = card
					PRINT(curGame, "Guess is wrong. The card in player's hand is %s"%rightCard.name)
					break
					
					
class BreathoftheInfinite(Spell):
	Class, name = "Priest", "Breath of the Infinite"
	requireTarget, mana = False, 3
	index = "Dragons~Priest~Spell~3~Breath of the Infinite"
	description = "Deal 2 damage to all minions. If you're holding a Dragon, only damage enemies"
	def effectCanTrigger(self):
		self.effectViable = self.Game.Hand_Deck.holdingDragon(self.ID)
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		damage = (2 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		if self.Game.Hand_Deck.holdingDragon(self.ID):
			PRINT(self.Game, "Breath of the Infinite deals %d damage to only enemy minions"%damage)
			targets = self.Game.minionsonBoard(3-self.ID)
		else:
			PRINT(self.Game, "Breath of the Infinite deals %d damage to all minions"%damage)
			targets = self.Game.minionsonBoard(self.ID) + self.Game.minionsonBoard(3-self.ID)
		self.dealsAOE(targets, [damage for minion in targets])
		return None
		
		
class MindflayerKaahrj(Minion):
	Class, race, name = "Priest", "", "Mindflayer Kaahrj"
	mana, attack, health = 3, 3, 3
	index = "Dragons~Priest~Minion~3~3~3~None~Mindflayer Kaahrj~Battlecry~Deathrattle~Legendary"
	requireTarget, keyWord, description = True, "", "Battlecry: Choose an enemy minion. Deathrattle: Summon a new copy of it"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [SummonCopyofaChosenMinion(self)]
		
	def targetExists(self, choice=0):
		return self.selectableEnemyMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.ID != self.ID and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			PRINT(self.Game, "Mindflayer Kaahrj's battlecry chooses enemy minion %s and lets the Deathrattle summon a new copy of it"%target.name)
			for trigger in self.deathrattles:
				if type(trigger) == SummonCopyofaChosenMinion:
					trigger.chosenMinionType = type(target)
		return target
		
class SummonCopyofaChosenMinion(Deathrattle_Minion):
	def __init__(self, entity):
		self.blank_init(entity)
		self.chosenMinionType = None
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return target == self.entity and self.chosenMinionType
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self.entity.Game, "Deathrattle: Summon a chosen minion %s triggers"%self.chosenMinionType.name)
		#随从的identity的前两个是用于鉴别是否是卡片生成的，第三个用于区别这个随从有没有被返回过手牌。
		self.entity.Game.summon(self.chosenMinionType(self.entity.Game, self.entity.ID), self.entity.position+1, self.entity.ID)
		
	#巫毒娃娃的亡语结果被复制，还会杀死同一个被诅咒的随从。
	def selfCopy(self, newMinion):
		trigger = type(self)(newMinion)
		trigger.chosenMinionType = self.chosenMinionType
		return trigger
		
		
class FateWeaver(Minion):
	Class, race, name = "Priest", "Dragon", "Fate Weaver"
	mana, attack, health = 4, 3, 6
	index = "Dragons~Priest~Minion~4~3~6~Dragon~Fate Weaver~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: If you've Invoked twice, reduce the Cost of cards in your hand by (1)"
	
	def effectCanTrigger(self):
		self.effectViable = self.Game.Counters.invocationCounts[self.ID] > 1
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if self.Game.Counters.invocationCounts[self.ID] > 1:
			PRINT(self.Game, "Fate Weaver's battlecry reduces the Cost of cards in player's hand by (1)")
			for card in self.Game.Hand_Deck.hands[self.ID]:
				ManaModification(card, changeby=-1, changeto=-1).applies()
			self.Game.Manas.calcMana_All()
		return None
		
		
class GraveRune(Spell):
	Class, name = "Priest", "Grave Rune"
	requireTarget, mana = True, 4
	index = "Dragons~Priest~Spell~4~Grave Rune"
	description = "Give a minion 'Deathrattle: Summon 2 copies of this'"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			PRINT(self.Game, "Grave Rune is cast and gives minion %s 'Deathrattle: Summon 2 copies of this'"%target.name)
			trigger = Summon2CopiesofThis(target)
			target.deathrattles.append(trigger)
			if target.onBoard:
				trigger.connect()
		return target
		
class Summon2CopiesofThis(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self.entity.Game, "Deathrattle: Summon 2 copies of %s triggers"%self.entity.name)
		newMinions = [type(self.entity)(self.entity.Game, self.entity.ID) for i in range(2)]
		self.entity.Game.summon(newMinions, (self.entity.position, "totheRight"), self.entity.ID)
		
		
class Chronobreaker(Minion):
	Class, race, name = "Priest", "Dragon", "Chronobreaker"
	mana, attack, health = 5, 4, 5
	index = "Dragons~Priest~Minion~5~4~5~Dragon~Chronobreaker~Deathrattle"
	requireTarget, keyWord, description = False, "", "Deathrattle: If you're holding a Dragon, deal 3 damage to all enemy minions"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [Deal3DamagetoAllEnemyMinions(self)]
		
class Deal3DamagetoAllEnemyMinions(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self.entity.Game, "Deathrattle: If you're holding a Dragon, deal 3 damage to all enemy minions triggers.")
		if self.entity.Game.Hand_Deck.holdingDragon(self.entity.ID):
			targets = self.entity.Game.minionsonBoard(3-self.entity.ID)
			self.entity.dealsAOE(targets, [3 for minion in targets])
			
			
class TimeRip(Spell):
	Class, name = "Priest", "Time Rip"
	requireTarget, mana = True, 5
	index = "Dragons~Priest~Spell~5~Time Rip"
	description = "Destroy a minion. Invoke Galakrond"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			PRINT(self.Game, "Time Rip is cast and destroys minion %s"%target.name)
			self.Game.destroyMinion(target)
		PRINT(self.Game, "Time Rip Invokes Galakrond")
		invokeGalakrond(self.Game, self.ID)
		return target
		
		
#加基森的三职业卡可以被迦拉克隆生成。
class GalakrondsWit(HeroPower):
	mana, name, requireTarget = 2, "Galakrond's Wit", False
	index = "Priest~Hero Power~2~Galakrond's Wit"
	description = "Add a random Priest minion to your hand"
	def available(self, choice=0):
		if self.heroPowerTimes >= self.heroPowerChances_base + self.heroPowerChances_extra:
			return False
		if self.Game.Hand_Deck.handNotFull(self.ID) == False:
			return False
		return True
		
	def effect(self, target=None, choice=0):
		curGame = self.Game
		if curGame.mode == 0:
			if curGame.guides:
				minion = curGame.guides.pop(0)
			else:
				minion = npchoice(curGame.RNGPools["Priest Minions"])
				curGame.fixedGuides.append(minion)
			PRINT(curGame, "Hero Power Galakrond's Wit adds a random Priest minion to player's hand")
			curGame.Hand_Deck.addCardtoHand(minion, self.ID, "CreateUsingType")
		return 0
		
		
class GalakrondtheUnspeakable(Galakrond_Hero):
	mana, weapon, description = 7, None, "Battlecry: Destroy a random enemy minion. (Invoke twice to upgrade)"
	Class, name, heroPower, armor = "Priest", "Galakrond, the Unspeakable", GalakrondsWit, 5
	index = "Dragons~Priest~Hero Card~7~Galakrond, the Unspeakable~Battlecry~Legendary"
	poolIdentifier = "Priest Minions"
	@classmethod
	def generatePool(cls, Game):
		priestMinions = []
		for key, value in Game.ClassCards["Priest"].items():
			if "~Minion~" in key:
				priestMinions.append(value)
		return "Priest Minions", priestMinions
		
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.upgradedGalakrond = GalakrondtheApocalypes_Priest
		self.progress = 0
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		targets = curGame.minionsonBoard(3-self.ID)
		if targets:
			if curGame.mode == 0:
				PRINT(curGame, "Galakrond, the Unspeakable's battlecry destroys a random enemy minion.")
				if curGame.guides:
					minion = curGame.minions[3-self.ID][curGame.guides.pop(0)]
				else:
					minion = npchoice(targets)
					curGame.fixedGuides.append(minion.position)
				minion.dead = True
		return None
		
class GalakrondtheApocalypes_Priest(Galakrond_Hero):
	mana, weapon, description = 7, None, "Battlecry: Destroy 2 random enemy minions. (Invoke twice to upgrade)"
	Class, name, heroPower, armor = "Priest", "Galakrond, the Apocalypes", GalakrondsWit, 5
	index = "Dragons~Priest~Hero Card~7~Galakrond, the Apocalypes~Battlecry~Legendary~Uncollectible"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.upgradedGalakrond = GalakrondAzerothsEnd_Priest
		self.progress = 0
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		targets = curGame.minionsonBoard(3-self.ID)
		if targets:
			if curGame.mode == 0:
				PRINT(curGame, "Galakrond, the Apocalypes's battlecry destroys 2 random enemy minions.")
				if curGame.guides:
					minions = [curGame.minions[3-self.ID][i] for i in curGame.guides.pop(0)]
				else:
					num = min(2, len(targets))
					minions = npchoice(targets, num, replace=True)
					curGame.fixedGuides.append(tuple([minion.position for minion in minions]))
				for minion in minions: minion.dead = True
		return None
		
class GalakrondAzerothsEnd_Priest(Galakrond_Hero):
	mana, weapon, description = 7, None, "Battlecry: Destroy 4 random enemy minions. Equip a 5/2 Claw"
	Class, name, heroPower, armor = "Priest", "Galakrond, Azeroth's End", GalakrondsWit, 5
	index = "Dragons~Priest~Hero Card~7~Galakrond, Azeroth's End~Battlecry~Legendary~Uncollectible"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.upgradedGalakrond = None
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		targets = curGame.minionsonBoard(3-self.ID)
		if targets:
			if curGame.mode == 0:
				PRINT(curGame, "Galakrond, Azeroth's End's battlecry destroys 4 random enemy minions.")
				if curGame.guides:
					minions = [curGame.minions[3-self.ID][i] for i in curGame.guides.pop(0)]
				else:
					num = min(4, len(targets))
					minions = npchoice(targets, num, replace=True)
					curGame.fixedGuides.append(tuple([minion.position for minion in minions]))
				for minion in minions: minion.dead = True
		PRINT(curGame, "Galakrond, Azeroth's End's battlecry equips a 5/2 Claw for player")
		curGame.equipWeapon(DragonClaw(curGame, self.ID))
		return None
		
class DragonClaw(Weapon):
	Class, name, description = "Neutral", "Dragon Claw", ""
	mana, attack, durability = 5, 5, 2
	index = "Dragons~Neutral~Weapon~5~5~2~Dragon Claw~Uncollectible"
	
#施放顺序是随机的。在姆诺兹多死亡之后，依然可以进行施放。如果姆诺兹多被对方控制，则改为施放我方上回合打出的牌。
#https://www.bilibili.com/video/av87286050?from=search&seid=5979238121000536259
#当我方拥有Choose Both光环的时候，复制对方打出的单个抉择的随从和法术： 随从仍然是单个抉择的结果，但是法术是拥有全选效果的。
#如果对方打出了全选抉择的随从，但是我方没有Choose Both光环，那么我方复制会得到全抉择的随从，而法术则是随机抉择。
#与苔丝的效果类似，对于随从是直接复制其打出结果。
#姆诺兹多的战吼没有打出牌的张数的限制。
#无法复制被法反掉的法术，因为那个法术不算作对方打出过的牌（被直接取消）。
#打出一个元素被对方的变形药水奥秘变形为绵羊后，下个回合仍然可以触发元素链。说明打出一张牌人记录是在最终“打出一张随从后”扳机结算前
#同时姆诺兹多能复制抉择变形随从的变形目标说明打出随从牌的记录是在战吼/抉择等之后。
class MurozondtheInfinite(Minion):
	Class, race, name = "Priest", "Dragon", "Murozond the Infinite"
	mana, attack, health = 8, 8, 8
	index = "Dragons~Priest~Minion~8~8~8~Dragon~Murozond the Infinite~Battlecry~Legendary"
	requireTarget, keyWord, description = False, "", "Battlecry: Play all cards your opponent played last turn"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if curGame.mode == 0:
			if curGame.guides:
				cards1, cards2 = curGame.guides.pop(0)
				cardstoReplay = {1: list(cards1), 2: list(cards2)}
			else:
				cardstoReplay = {1: [curGame.cardPool[index] for index in curGame.Counters.cardsPlayedLastTurn[1]],
								2: [curGame.cardPool[index] for index in curGame.Counters.cardsPlayedLastTurn[2]]}
				npshuffle(cardstoReplay[1])
				npshuffle(cardstoReplay[2])
				curGame.fixedGuides.append((tuple(cardstoReplay[1]), tuple(cardstoReplay[2])))
			#应该是每当打出一张卡后将index从原有列表中移除。
			PRINT(curGame, "Murozond the Infinite's battlecry starts replaying cards the opponent played last turn.")
			while cardstoReplay[3-self.ID]:
				card = cardstoReplay[3-self.ID].pop(0)(curGame, self.ID)
				if card.type == "Minion":
					PRINT(curGame, "******Murozond the Infinite's battlecry summons minion %s"%card.name)
					curGame.summon(card, self.position+1, self.ID)
				elif card.type == "Spell":
					PRINT(curGame, "******Murozond the Infinite's battlecry casts spell( at random target) %s"%card.name)
					card.cast(None, "byOthers")
				elif card.type == "Weapon":
					PRINT(curGame, "******Murozond the Infinite's battlecry lets player equip weapon %s"%card.name)
					curGame.equipWeapon(card)
				else: #Hero cards. And the HeroClass will change accordingly
					#Replaying Hero Cards can only replace your hero and Hero Power, no battlecry will be triggered
					PRINT(curGame, "******Murozond the Infinite's battlecry replaces player's hero with %s"%card.name)
					card.replaceHero()
				curGame.gathertheDead()
		return None
		
"""Rogue cards"""
class BloodsailFlybooter(Minion):
	Class, race, name = "Rogue", "Pirate", "Bloodsail Flybooter"
	mana, attack, health = 1, 1, 1
	index = "Dragons~Rogue~Minion~1~1~1~Pirate~Bloodsail Flybooter~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Add two 1/1 Pirates to your hand"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		PRINT(self.Game, "Bloodsail Flybooter's battlecry adds two 1/1 Pirates to player's hand")
		self.Game.Hand_Deck.addCardtoHand([SkyPirate, SkyPirate], self.ID, "CreateUsingType")
		return None
		
class SkyPirate(Minion):
	Class, race, name = "Rogue", "Pirate", "Sky Pirate"
	mana, attack, health = 1, 1, 1
	index = "Dragons~Rogue~Minion~1~1~1~Pirate~Sky Pirate~Uncollectible"
	requireTarget, keyWord, description = False, "", ""
	
	
class DragonsHoard(Spell):
	Class, name = "Rogue", "Dragon's Hoard"
	requireTarget, mana = False, 1
	index = "Dragons~Rogue~Spell~1~Dragon's Hoard"
	description = "Discover a Legendary minion from another class"
	poolIdentifier = "Class Legendary Minions except Rogue"
	@classmethod
	def generatePool(cls, Game):
		classes, lists = [], []
		for Class in Game.Classes:
			classes.append("Class Legendary Minions except "+Class)
			classPool = fixedList(Game.Classes)
			extractfrom(Class, classPool)
			legendaryMinions = []
			for ele in classPool:
				for key, value in Game.ClassCards[ele].items():
					if "~Minion~" in key and "~Legendary" in key:
						legendaryMinions.append(value)
			lists.append(legendaryMinions)
		return classes, lists
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if curGame.Hand_Deck.handNotFull(self.ID):
			if curGame.mode == 0:
				if curGame.guides:
					PRINT(curGame, "Dragon's Hoard adds a Legendary minion from another class to player's hand")
					curGame.Hand_Deck.addCardtoHand(curGame.guides.pop(0), self.ID, "CreateUsingType")
				else:
					key = "Class Legendary Minions except "+classforDiscover(self)
					if "byOthers" in comment:
						minion = npchoice(curGame.RNGPools[key])
						curGame.fixedGuides.append(minion)
						PRINT(curGame, "Dragon's Hoard is cast and adds a random Legendary minion from another class to player's hand")
						curGame.Hand_Deck.addCardtoHand(minion, self.ID, "CreateUsingType")
					else:
						minions = npchoice(curGame.RNGPools[key], 3, replace=False)
						curGame.options = [minion(curGame, self.ID) for minion in minions]
						PRINT(curGame, "Dragon's Hoard is cast and lets player discover a Legendary minion from another class")
						curGame.Discover.startDiscover(self, None)
		return None
		
	def discoverDecided(self, option, info):
		self.Game.fixedGuides.append(type(option))
		PRINT(self.Game, "Legendary minion %s is put into player's hand."%option.name)
		self.Game.Hand_Deck.addCardtoHand(option, self.ID)
		self.Game.sendSignal("DiscoveredCardPutintoHand", self.ID, self, option, 0, "")
		
		
class PraiseGalakrond(Spell):
	Class, name = "Rogue", "Praise Galakrond"
	requireTarget, mana = True, 1
	index = "Dragons~Rogue~Spell~1~Praise Galakrond"
	description = "Give a minion +1 Attack. Invoke Galakrond"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			PRINT(self.Game, "Praise Galakrond is cast and gives minion %s +1 Attack"%target.name)
			target.buffDebuff(1, 0)
		PRINT(self.Game, "Praise Galakrond Frost Invokes Galakrond")
		invokeGalakrond(self.Game, self.ID)
		return target
		
		
class SealFate(Spell):
	Class, name = "Rogue", "Seal Fate"
	requireTarget, mana = True, 3
	index = "Dragons~Rogue~Spell~3~Seal Fate"
	description = "Deal 3 damage to an undamaged character. Invoke Galakrond"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			damage = (3 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			PRINT(self.Game, "Seal Fate is cast and deals %d damage to undamaged minion %s"%(damage, target.name))
			self.dealsDamage(target, damage)
		PRINT(self.Game, "Seal Fate Frost Invokes Galakrond")
		invokeGalakrond(self.Game, self.ID)
		return target
		
		
class UmbralSkulker(Minion):
	Class, race, name = "Rogue", "", "Umbral Skulker"
	mana, attack, health = 4, 3, 3
	index = "Dragons~Rogue~Minion~4~3~3~None~Umbral Skulker~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: If you've Invoked twice, add 3 Coins to your hand"
	
	def effectCanTrigger(self):
		self.effectViable = self.Game.Counters.invocationCounts[self.ID] > 1
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if self.Game.Counters.invocationCounts[self.ID] > 1:
			PRINT(self.Game, "Umbral Skulker's battlecry adds 3 Coins to player's hand")
			self.Game.Hand_Deck.addCardtoHand([TheCoin, TheCoin, TheCoin], self.ID, "CreateUsingType")
		return None
		
		
class NecriumApothecary(Minion):
	Class, race, name = "Rogue", "", "Necrium Apothecary"
	mana, attack, health = 5, 2, 5
	index = "Dragons~Rogue~Minion~5~2~5~None~Necrium Apothecary~Combo"
	requireTarget, keyWord, description = False, "", "Combo: Draw a Deathrattle minion from your deck and gain its Deathrattle"
	
	def effectCanTrigger(self):
		self.effectViable = self.Game.Counters.numCardsPlayedThisTurn[self.ID] > 0
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if curGame.Counters.numCardsPlayedThisTurn[self.ID] > 0:
			if curGame.mode == 0:
				if curGame.guides:
					i = curGame.guides.pop(0)
					if i < 0:
						PRINT(curGame, "No Deathrattle minions in player's hand. Necrium Apothecary's Combo has no effect")
						return None
				else:
					minionsinDeck = [i for i, card in enumerate(curGame.Hand_Deck.decks[self.ID]) if card.type == "Minion" and card.deathrattles]
					if minionsinDeck:
						i = npchoice(minionsinDeck)
						curGame.fixedGuides.append(i)
					else:
						curGame.fixedGuides.append(-1)
						return None
				PRINT(curGame, "Necrium Apothecary's Combo triggers and lets player draw a Deathrattle minion from deck.")
				minion = curGame.Hand_Deck.drawCard(self.ID, i)[0]
				if minion:
					PRINT(curGame, "Necrium Apothecary gains Deathrattle: {}".format(minion.deathrattles))
					for trigger in minion.deathrattles:
						copy = type(trigger)(self)
						self.deathrattles.append(copy)
						if self.onBoard: copy.connect()
		return None
		
		
class Stowaway(Minion):
	Class, race, name = "Rogue", "", "Stowaway"
	mana, attack, health = 5, 4, 4
	index = "Dragons~Rogue~Minion~5~4~4~None~Stowaway~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: If there are cards in your deck that didn't start there, draw 2 of them"
	
	def effectCanTrigger(self):
		self.effectViable = False
		for card in self.Game.Hand_Deck.decks[self.ID]:
			if card.identity not in self.Game.Hand_Deck.startingDeckIdentities[self.ID]:
				self.effectViable = True
				break
				
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		HD = curGame.Hand_Deck
		if curGame.mode == 0:
			for num in range(2):
				if curGame.guides:
					i = curGame.guides.pop(0)
					if i < 0:
						PRINT(curGame, "No cards in player's deck that didn't start in there. Stowaway's battlecry has no effect")
						break
				else:
					createdCards = [i for i, card in enumerate(HD.decks[self.ID]) if card.identity not in HD.startingDeckIdentities[self.ID]]
					if createdCards:
						i = npchoice(createdCards)
						curGame.fixedGuides.append(i)
					else:
						curGame.fixedGuides.append(-1)
						break
				HD.drawCard(self.ID, i)
		return None
		
		
class Waxadred(Minion):
	Class, race, name = "Rogue", "Dragon", "Waxadred"
	mana, attack, health = 5, 7, 5
	index = "Dragons~Rogue~Minion~5~7~5~Dragon~Waxadred~Deathrattle~Legendary"
	requireTarget, keyWord, description = False, "", "Deathrattle: Shuffle a Candle into your deck that resummons Waxadred when drawn"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [ShuffleaCandleintoYourDeck(self)]
		
class ShuffleaCandleintoYourDeck(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self.entity.Game, "Deathrattle: Shuffle a Candle into your deck triggers.")
		self.entity.Game.Hand_Deck.shuffleCardintoDeck(WaxadredsCandle(self.entity.Game, self.entity.ID), self.entity.ID)
		
class WaxadredsCandle(Spell):
	Class, name = "Rogue", "Waxadred's Candle"
	requireTarget, mana = False, 5
	index = "Dragons~Rogue~Spell~5~Waxadred's Candle~Casts When Drawn~Uncollectible"
	description = "Casts When Drawn. Summon Waxadred"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		PRINT(self.Game, "Waxadred's Candle is cast and summons Waxadred")
		self.Game.summon(Waxadred(self.Game, self.ID), -1, self.ID)
		return None
		
		
class CandleBreath(Spell):
	Class, name = "Rogue", "Candle Breath"
	requireTarget, mana = False, 6
	index = "Dragons~Rogue~Spell~6~Candle Breath"
	description = "Draw 3 cards. Costs (3) less while you're holding a Dragon"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersinHand = [Trigger_CandleBreath(self)]
		
	def effectCanTrigger(self):
		self.effectViable = self.Game.Hand_Deck.holdingDragon(self.ID)
		
	def selfManaChange(self):
		if self.inHand and self.Game.Hand_Deck.holdingDragon(self.ID):
			self.mana -= 3
			self.mana = max(0, self.mana)
			
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		PRINT(self.Game, "Candle Breath is cast and lets player draw 3 cards")
		for i in range(3):
			self.Game.Hand_Deck.drawCard(self.ID)
		return None
		
class Trigger_CandleBreath(TriggerinHand):
	def __init__(self, entity):
		self.blank_init(entity, ["CardLeavesHand", "CardEntersHand"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		#Only cards with a different class than your hero class will trigger this
		card = target[0] if signal == "CardEntersHand" else target
		return self.entity.inHand and card.ID == self.entity.ID and card.type == "Minion" and "Dragon" in card.race
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.Game.Manas.calcMana_Single(self.entity)
		
		
class FlikSkyshiv(Minion):
	Class, race, name = "Rogue", "", "Flik Skyshiv"
	mana, attack, health = 6, 4, 4
	index = "Dragons~Rogue~Minion~6~4~4~None~Flik Skyshiv~Battlecry~Legendary"
	requireTarget, keyWord, description = True, "", "Battlecry: Destroy a minion and all copies of it (wherever they are)"
	def targetExists(self, choice=0):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target != self and target.onBoard
		
	#飞刺的战吼会摧毁所有同名卡，即使有些不是随从，如法师的扰咒术奥秘和随从，镜像法术和其衍生物
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			PRINT(self.Game, "Flik Skyshiv's battlecry destroys minion %s and all cards that have the same name"%target.name)
			cardsonBoard, cardsinHand, cardsinDeck = [], [], []
			for minion in self.Game.minionsonBoard(1) + self.Game.minionsonBoard(2):
				if minion.name == target.name:
					cardsonBoard.append(minion)
			for card in self.Game.Hand_Deck.hands[1] + self.Game.Hand_Deck.hands[2]:
				if card.name == target.name:
					cardsinHand.append(card)
			for card in self.Game.Hand_Deck.decks[1] + self.Game.Hand_Deck.decks[2]:
				if card.name == target.name:
					cardsinDeck.append(card)
			for minion in cardsonBoard:
				minion.dead = True
			for card in cardsinHand:
				self.Game.Hand_Deck.extractfromHand(card)
			for card in cardsinDeck:
				self.Game.Hand_Deck.extractfromDeck(card)
		return target
		
		
class GalakrondsGuile(HeroPower):
	mana, name, requireTarget = 2, "Galakrond's Guile", False
	index = "Rogue~Hero Power~2~Galakrond's Guile"
	description = "Add a Lackey to your hand"
	def available(self, choice=0):
		if self.heroPowerTimes >= self.heroPowerChances_base + self.heroPowerChances_extra:
			return False
		if self.Game.Hand_Deck.handNotFull(self.ID) == False:
			return False
		return True
		
	def effect(self, target=None, choice=0):
		curGame = self.Game
		if curGame.mode == 0:
			if curGame.guides:
				lackey = curGame.guides.pop(0)
			else:
				lackey = npchoice(Lackeys)
				curGame.fixedGuides.append(lackey)
			PRINT(curGame, "Hero Power Galakrond's Guile adds a Lackey to player's hand")
			curGame.Hand_Deck.addCardtoHand(lackey, self.ID, "CreateUsingType")
		return 0
		
class GalakrondtheNightmare(Galakrond_Hero):
	mana, weapon, description = 7, None, "Battlecry: Draw a card. It costs (1). (Invoke twice to upgrade)"
	Class, name, heroPower, armor = "Rogue", "Galakrond, the Nightmare", GalakrondsGuile, 5
	index = "Dragons~Rogue~Hero Card~7~Galakrond, the Nightmare~Battlecry~Legendary"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.upgradedGalakrond = GalakrondtheApocalypes_Rogue
		self.progress = 0
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		PRINT(self.Game, "Galakrond, the Nightmare's battlecry lets player draw a card. It costs (0)")
		card, mana = self.Game.Hand_Deck.drawCard(self.ID)
		if card:
			ManaModification(card, changeby=0, changeto=1).applies()
		return None
		
class GalakrondtheApocalypes_Rogue(Galakrond_Hero):
	mana, weapon, description = 7, None, "Battlecry: Draw 2 cards. They cost (1). (Invoke twice to upgrade)"
	Class, name, heroPower, armor = "Rogue", "Galakrond, the Apocalypes", GalakrondsGuile, 5
	index = "Dragons~Rogue~Hero Card~7~Galakrond, the Apocalypes~Battlecry~Legendary~Uncollectible"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.upgradedGalakrond = GalakrondAzerothsEnd_Rogue
		self.progress = 0
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		PRINT(self.Game, "Galakrond, the Apocalypes's battlecry lets player draw 2 cards. They cost (0)")
		for i in range(2):
			card, mana = self.Game.Hand_Deck.drawCard(self.ID)
			if card:
				ManaModification(card, changeby=0, changeto=1).applies()
		return None
		
class GalakrondAzerothsEnd_Rogue(Galakrond_Hero):
	mana, weapon, description = 7, None, "Battlecry: Draw 4 cards. They cost (1). Equip a 5/2 Claw"
	Class, name, heroPower, armor = "Rogue", "Galakrond, Azeroth's End", GalakrondsGuile, 5
	index = "Dragons~Rogue~Hero Card~7~Galakrond, Azeroth's End~Battlecry~Legendary~Uncollectible"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.upgradedGalakrond = None
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		PRINT(self.Game, "Galakrond, Azeroth's End's battlecry lets player draw 4 cards. They cost (0)")
		for i in range(4):
			card, mana = self.Game.Hand_Deck.drawCard(self.ID)
			if card:
				ManaModification(card, changeby=0, changeto=1).applies()
		PRINT(self.Game, "Galakrond, Azeroth's End's battlecry equips a 5/2 Claw for player")
		self.Game.equipWeapon(DragonClaw(self.Game, self.ID))
		return None
		
"""Shaman cards"""
class InvocationofFrost(Spell):
	Class, name = "Shaman", "Invocation of Frost"
	requireTarget, mana = True, 2
	index = "Dragons~Shaman~Spell~2~Invocation of Frost"
	description = "Freeze a minion. Invoke Galakrond"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			PRINT(self.Game, "Invocation of Frost is cast, freezes minion %s"%target.name)
			target.getsFrozen()
		PRINT(self.Game, "Invocation of Frost Invokes Galakrond")
		invokeGalakrond(self.Game, self.ID)
		return target
		
		
class SurgingTempest(Minion):
	Class, race, name = "Shaman", "Elemental", "Surging Tempest"
	mana, attack, health = 1, 1, 3
	index = "Dragons~Shaman~Minion~1~1~3~Elemental~Surging Tempest"
	requireTarget, keyWord, description = False, "", "Has +1 Attack while you have Overloaded Mana Crystals"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.auras["Buff Aura"] = BuffAura_SurgingTempest(self)
		self.activated = False
		
class BuffAura_SurgingTempest(AuraDealer_toMinion):
	def __init__(self, entity):
		self.entity = entity
		self.signals, self.auraAffected = ["OverloadStatusCheck"], []
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		isOverloaded = self.entity.Game.Manas.manasOverloaded[self.entity.ID] > 0 or self.entity.Game.Manas.manasLocked[self.entity.ID] > 0
		if isOverloaded == False and self.entity.activated:
			self.entity.activated = False
			for minion, aura_Receiver in fixedList(self.auraAffected):
				aura_Receiver.effectClear()
			self.auraAffected = []
		elif isOverloaded and self.entity.activated == False:
			self.entity.activated = True
			self.applies(self.entity)
			
	def applies(self, subject):
		if subject == self.entity:
			aura_Receiver = BuffAura_Receiver(subject, self, 2, 0)
			aura_Receiver.effectStart()
			
	def auraAppears(self):
		isOverloaded = self.entity.Game.Manas.manasOverloaded[self.entity.ID] > 0 or self.entity.Game.Manas.manasLocked[self.entity.ID] > 0
		if isOverloaded:
			self.entity.activated = True
			self.applies(self.entity)
			
		self.entity.Game.triggersonBoard[self.entity.ID].append((self, "OverloadStatusCheck"))
		
	def selfCopy(self, recipientMinion): #The recipientMinion is the minion that deals the Aura.
		return type(self)(recipientMinion)
	#可以通过AuraDealer_toMinion的createCopy方法复制
	
	
class Squallhunter(Minion):
	Class, race, name = "Shaman", "Dragon", "Squallhunter"
	mana, attack, health = 4, 5, 7
	index = "Dragons~Shaman~Minion~4~5~7~Dragon~Squallhunter~Spell Damage~Overload"
	requireTarget, keyWord, description = False, "", "Spell Damage +2, Overload: (2)"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.keyWords["Spell Damage"] = 2
		self.overload = 2
		
		
class StormsWrath(Spell):
	Class, name = "Shaman", "Storm's Wrath"
	requireTarget, mana = False, 1
	index = "Dragons~Shaman~Spell~1~Storm's Wrath~Overload"
	description = "Give your minions +1/+1. Overload: (1)"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.overload = 2
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		PRINT(self.Game, "Storm's Wrath is cast and gives all friendly minions +1/+1")
		for minion in fixedList(self.Game.minionsonBoard(self.ID)):
			minion.buffDebuff(1, 1)
		return None
		
		
class LightningBreath(Spell):
	Class, name = "Shaman", "Lightning Breath"
	requireTarget, mana = True, 3
	index = "Dragons~Shaman~Spell~3~Lightning Breath"
	description = "Deal 4 damage to a minion. If you're holding a Dragon, also damage its neighbors"
	def effectCanTrigger(self):
		self.effectViable = self.Game.Hand_Deck.holdingDragon(self.ID)
		
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			damage = (4 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			if target.onBoard and self.Game.Hand_Deck.holdingDragon(self.ID) and self.Game.adjacentMinions2(target)[0] != []:
				PRINT(self.Game, "Lightning Breath is cast and deals %d damage to minion %s and the ones next to it."%(damage, target.name))
				targets = [target] + self.Game.adjacentMinions2(target)[0]
				self.dealsAOE(targets, [damage for minion in targets])
			else:
				PRINT(self.Game, "Lightning Breath is cast and deals %d damage to minion %s"%(damage, target.name))
				self.dealsDamage(target, damage)
		return target
		
		
class Bandersmosh(Minion):
	Class, race, name = "Shaman", "", "Bandersmosh"
	mana, attack, health = 5, 5, 5
	index = "Dragons~Shaman~Minion~5~5~5~None~Bandersmosh"
	requireTarget, keyWord, description = False, "", "Each turn this is in your hand, transform it into a 5/5 random Legendary minion"
	poolIdentifier = "Legendary Minions"
	@classmethod
	def generatePool(cls, Game):
		return "Legendary Minions", list(Game.LegendaryMinions.values())
		
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersinHand = [Trigger_Bandersmosh_PreShifting(self)]
		
class Trigger_Bandersmosh_PreShifting(TriggerinHand):
	def __init__(self, entity):
		self.blank_init(entity, ["TurnStarts"])
		self.makesCardEvanescent = True
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.inHand and ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		curGame = self.entity.Game
		if curGame.mode == 0:
			if curGame.guides:
				minion = curGame.guides.pop(0)
			else:
				minion = npchoice(curGame.RNGPools["Legendary Minions"])(curGame, self.entity.ID)
				curGame.fixedGuides.append(minion)
			minion = minion(curGame, self.entity.ID)
			PRINT(curGame, "At the start of turn, Bandersmosh transforms for the first time into a 5/5 copy of random Legendary minion")
			minion.statReset(5, 5)
			ManaModification(minion, changeby=0, changeto=5).applies()
			trigger = Trigger_Bandersmosh_KeepShifting(minion)
			trigger.connect()
			minion.triggersonBoard.append(trigger)
			curGame.Hand_Deck.replaceCardinHand(self.entity, minion)
		
class Trigger_Bandersmosh_KeepShifting(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["TurnStarts"])
		self.makesCardEvanescent = True
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.inHand and ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		curGame = self.entity.Game
		if curGame.mode == 0:
			if curGame.guides:
				minion = curGame.guides.pop(0)
			else:
				minion = npchoice(curGame.RNGPools["Legendary Minions"])(curGame, self.entity.ID)
				curGame.fixedGuides.append(minion)
			minion = minion(curGame, self.entity.ID)
			PRINT(curGame, "At the start of turn, Bandersmosh transforms for the first time into a 5/5 copy of random Legendary minion")
			minion.statReset(5, 5)
			ManaModification(minion, changeby=0, changeto=5).applies()
			trigger = Trigger_Bandersmosh_KeepShifting(minion) #新的扳机保留这个变色龙的原有reference.在对方无手牌时会变回起始的变色龙。
			trigger.connect()
			minion.triggersonBoard.append(trigger)
			curGame.Hand_Deck.replaceCardinHand(self.entity, minion)
			
			
class CumuloMaximus(Minion):
	Class, race, name = "Shaman", "Elemental", "Cumulo-Maximus"
	mana, attack, health = 5, 5, 5
	index = "Dragons~Shaman~Minion~5~5~5~Elemental~Cumulo-Maximus~Battlecry"
	requireTarget, keyWord, description = True, "", "Battlecry: If you have Overloaded Mana Crystals, deal 5 damage"
	def returnTrue(self, choice=0):
		return self.Game.Manas.manasLocked[self.ID] + self.Game.Manas.manasOverloaded[self.ID] > 0
		
	def effectCanTrigger(self):
		if self.Game.Manas.manasLocked[self.ID] + self.Game.Manas.manasOverloaded[self.ID] > 0:
			self.effectViable = self.targetExists()
		else:
			self.effectViable = False
			
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target and self.Game.Manas.manasLocked[self.ID] + self.Game.Manas.manasOverloaded[self.ID] > 0:
			PRINT(self.Game, "Cumulo-Maximus's battlecry deals 5 damage to %s"%target.name)
			self.dealsDamage(target, 5)
		return target
		
		
class DragonsPack(Spell):
	Class, name = "Shaman", "Dragon's Pack"
	requireTarget, mana = False, 5
	index = "Dragons~Shaman~Spell~5~Dragon's Pack"
	description = "Summon two 2/3 Spirit Wolves with Taunt. If you've Invoked Galakrond, give them +2/+2"
	def available(self):
		return self.Game.space(self.ID) > 0
		
	def effectCanTrigger(self): #法术先检测是否可以使用才判断是否显示黄色
		self.effectViable = self.Game.Counters.invocationCounts[self.ID] > 1
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		PRINT(self.Game, "Dragon's Pack is cast and summons two 2/3 Spirit Wolves with Taunt.")
		minion1, minion2 = SpiritWolf_Dragons(self.Game, self.ID), SpiritWolf_Dragons(self.Game, self.ID)
		self.Game.summon([minion1, minion2], (-1, "totheRightEnd"), self.ID)
		if self.Game.Counters.invocationCounts[self.ID] > 1:
			PRINT(self.Game, "Because player has Invoked twice, Dragon's Pack gives the summon Spirit Wolves +2/+2")
			minion1.buffDebuff(2, 2)
			minion2.buffDebuff(2, 2)
		return None
		
class SpiritWolf_Dragons(Minion):
	Class, race, name = "Shaman", "", "Spirit Wolf"
	mana, attack, health = 2, 2, 3
	index = "Dragons~Shaman~Minion~2~2~3~None~Spirit Wolf~Taunt~Uncollectible"
	requireTarget, keyWord, description = False, "Taunt", "Taunt"
	
	
class CorruptElementalist(Minion):
	Class, race, name = "Shaman", "", "Corrupt Elementalist"
	mana, attack, health = 6, 3, 3
	index = "Dragons~Shaman~Minion~6~3~3~None~Corrupt Elementalist~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Invoke Galakrond twice"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		PRINT(self.Game, "Corrupt Elementalist's battlecry Invokes Galakrond twice")
		invokeGalakrond(self.Game, self.ID)
		invokeGalakrond(self.Game, self.ID)
		return None
		
		
class Nithogg(Minion):
	Class, race, name = "Shaman", "Dragon", "Nithogg"
	mana, attack, health = 6, 5, 5
	index = "Dragons~Shaman~Minion~6~5~5~Dragon~Nithogg~Battlecry~Legendary"
	requireTarget, keyWord, description = False, "", "Battlecry: Summon two 0/3 Eggs. Next turn they hatch into 4/4 Drakes with Rush"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		PRINT(self.Game, "Nithogg's battlecry summons two 0/3 Eggs, which will hatch next turn into 4/4 Drakes with Rush.")
		pos = (self.position, "leftandRight") if self.onBoard else (-1, "totheRightEnd")
		self.Game.summon([StormEgg(self.Game, self.ID) for i in range(2)], pos, self.ID)
		return None
		
class StormEgg(Minion):
	Class, race, name = "Shaman", "", "Storm Egg"
	mana, attack, health = 1, 0, 3
	index = "Dragons~Shaman~Minion~1~0~3~None~Storm Egg~Uncollectible"
	requireTarget, keyWord, description = False, "", "At the start of your turn, transform into a 4/4 Storm Drake with Rush"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_StormEgg(self)]
		
class Trigger_StormEgg(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["TurnStarts"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self.entity.Game, "At the start of turn, %s hatches into a 4/4 Drake with Rush"%self.entity.name)
		self.entity.Game.transform(self.entity, StormDrake(self.entity.Game, self.entity.ID))
		
class StormDrake(Minion):
	Class, race, name = "Shaman", "Dragon", "Storm Drake"
	mana, attack, health = 4, 4, 4
	index = "Dragons~Shaman~Minion~4~4~4~Dragon~Storm Drake~Rush~Uncollectible"
	requireTarget, keyWord, description = False, "Rush", "Rush"
	
	
class GalakrondsFury(HeroPower):
	mana, name, requireTarget = 2, "Galakrond's Fury", False
	index = "Shaman~Hero Power~2~Galakrond's Fury"
	description = "Summon a 2/1 Elemental with Rush"
	def available(self, choice=0):
		if self.heroPowerTimes >= self.heroPowerChances_base + self.heroPowerChances_extra:
			return False
		if self.Game.space(self.ID) < 1:
			return False
		return True
		
	def effect(self, target=None, choice=0):
		PRINT(self.Game, "Hero Power Galakrond's Fury summons a 2/1 Elemental with Rush")
		self.Game.summon(WindsweptElemental(self.Game, self.ID), -1, self.ID, "")
		return 0
		
class WindsweptElemental(Minion):
	Class, race, name = "Shaman", "Elemental", "Windswept Elemental"
	mana, attack, health = 2, 2, 1
	index = "Dragons~Shaman~Minion~2~2~1~Elemental~Windswept Elemental~Rush~Uncollectible"
	requireTarget, keyWord, description = False, "Rush", "Rush"
	
class GalakrondtheTempest(Galakrond_Hero):
	mana, weapon, description = 7, None, "Battlecry: Summon two 2/2 Storms with Rush. (Invoke twice to upgrade)"
	Class, name, heroPower, armor = "Shaman", "Galakrond, the Tempest", GalakrondsFury, 5
	index = "Dragons~Shaman~Hero Card~7~Galakrond, the Tempest~Battlecry~Legendary"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.upgradedGalakrond = GalakrondtheApocalypes_Shaman
		self.progress = 0
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		PRINT(self.Game, "Galakrond, the Tempest's summons two 2/2 Storms with Rush")
		self.Game.summon([BrewingStorm(self.Game, self.ID) for i in range(2)], (-1, "totheRightEnd"), self.ID)
		return None
		
class GalakrondtheApocalypes_Shaman(Galakrond_Hero):
	mana, weapon, description = 7, None, "Battlecry: Summon two 4/4 Storms with Rush. (Invoke twice to upgrade)"
	Class, name, heroPower, armor = "Shaman", "Galakrond, the Apocalypes", GalakrondsFury, 5
	index = "Dragons~Shaman~Hero Card~7~Galakrond, the Apocalypes~Battlecry~Legendary~Uncollectible"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.upgradedGalakrond = GalakrondAzerothsEnd_Shaman
		self.progress = 0
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		PRINT(self.Game, "Galakrond, the Apocalypes' battlecry summons two 4/4 Storms with Rush")
		self.Game.summon([LivingStorm(self.Game, self.ID) for i in range(2)], (-1, "totheRightEnd"), self.ID)
		return None
		
class GalakrondAzerothsEnd_Shaman(Galakrond_Hero):
	mana, weapon, description = 7, None, "Battlecry: Summon two 8/8 Storms with Rush. Equip a 5/2 Claw"
	Class, name, heroPower, armor = "Shaman", "Galakrond, Azeroth's End", GalakrondsFury, 5
	index = "Dragons~Shaman~Hero Card~7~Galakrond, Azeroth's End~Battlecry~Legendary~Uncollectible"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.upgradedGalakrond = None
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		PRINT(self.Game, "Galakrond, Azeroth's End's battlecry summons two 8/8 Storms with Rush")
		self.Game.summon([RagingStorm(self.Game, self.ID) for i in range(2)], (-1, "totheRight"), self.ID)
		PRINT(self.Game, "Galakrond, Azeroth's End's battlecry equips a 5/2 Claw for player")
		self.Game.equipWeapon(DragonClaw(self.Game, self.ID))
		return None
		
class BrewingStorm(Minion):
	Class, race, name = "Shaman", "Elemental", "Brewing Storm"
	mana, attack, health = 2, 2, 2
	index = "Dragons~Shaman~Minion~2~2~2~Elemental~Brewing Storm~Rush~Uncollectible"
	requireTarget, keyWord, description = False, "Rush", "Rush"
	
class LivingStorm(Minion):
	Class, race, name = "Shaman", "Elemental", "Living Storm"
	mana, attack, health = 4, 4, 4
	index = "Dragons~Shaman~Minion~4~4~4~Elemental~Living Storm~Rush~Uncollectible"
	requireTarget, keyWord, description = False, "Rush", "Rush"
	
class RagingStorm(Minion):
	Class, race, name = "Shaman", "Elemental", "Raging Storm"
	mana, attack, health = 8, 8, 8
	index = "Dragons~Shaman~Minion~8~8~8~Elemental~Raging Storm~Rush~Uncollectible"
	requireTarget, keyWord, description = False, "Rush", "Rush"
	
"""Warlock cards"""
class RainofFire(Spell):
	Class, name = "Warlock", "Rain of Fire"
	requireTarget, mana = False, 1
	index = "Dragons~Warlock~Spell~1~Rain of Fire"
	description = "Deal 1 damage to all characters"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		damage = (1 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		PRINT(self.Game, "Rain of Fire is cast and deals %d damage to all minions"%damage)
		targets = self.Game.minionsonBoard(1) + self.Game.minionsonBoard(2)
		self.dealsAOE(targets, [damage for minion in targets])
		return None
		
		
class NetherBreath(Spell):
	Class, name = "Warlock", "Nether Breath"
	requireTarget, mana = True, 2
	index = "Dragons~Warlock~Spell~2~Neth Breath"
	description = "Deal 2 damage. If you're holding a Dragon, deal 4 damage with Lifesteal instead"
	def effectCanTrigger(self):
		self.effectViable = self.Game.Hand_Deck.holdingDragon(self.ID)
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			if self.Game.Hand_Deck.holdingDragon(self.ID):
				damage = (4 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
				PRINT(self.Game, "Nether Breath is cast and deals %d damage to %s with Lifesteal"%(damage, target.name))
				self.keyWords["Lifesteal"] = 1
			else:
				damage = (2 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
				PRINT(self.Game, "Nether Breath is cast and deals %d damage to %s"%(damage, target.name))
			self.dealsDamage(target, damage)
		return None
		
class DarkSkies(Spell):
	Class, name = "Warlock", "Dark Skies"
	requireTarget, mana = False, 3
	index = "Dragons~Warlock~Spell~3~Dark Skies"
	description = "Deal 1 damage to a random minion. Repeat for each card in your hand"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		damage = (1 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		curGame = self.Game
		PRINT(curGame, "Dark Skies is cast and deals %d damage to a random minion. And repeat for each card in player's hand"%damage)
		#在使用这个法术后先打一次，然后检测手牌数。总伤害个数是手牌数+1
		targets = curGame.minionsAlive(1) + curGame.minionsAlive(2)
		if targets != []:
			if curGame.mode == 0:
				if curGame.guides:
					i, where = curGame.guides.pop(0)
					if where: minion = curGame.find(i, where)
					else:
						PRINT(curGame, "No minions on board. Dark Skies has no effect")
						return None
				else:
					minion = npchoice(targets)
					curGame.fixedGuides.append((minion.position, "minion%d"%minion.ID))
				self.dealsDamage(minion, damage)
				handSize = len(curGame.Hand_Deck.hands[self.ID])
				for num in range(handSize):
					if curGame.guides:
						i, where = curGame.guides.pop(0)
						if where: minion = curGame.find(i, where)
						else:
							PRINT(curGame, "No minions on board. Dark Skies has no effect")
							break
					else:
						targets = self.Game.minionsAlive(1) + self.Game.minionsAlive(2)
						if targets:
							minion = npchoice(targets)
							curGame.fixedGuides.append((minion.position, "minion%d"%minion.ID))
						else:
							curGame.fixedGuides.append((0, ''))
							break
					PRINT(curGame, "Dark Skies deals %d damage to minion %s"%(damage, minion.name))
					self.dealsDamage(minion, damage)
		return None
		
		
class DragonblightCultist(Minion):
	Class, race, name = "Warlock", "", "Dragonblight Cultist"
	mana, attack, health = 3, 1, 1
	index = "Dragons~Warlock~Minion~3~1~1~None~Dragonblight Cultist~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Invoke Galakrond. Gain +1 Attack for each other friendly minion"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		PRINT(self.Game, "Dragonblight Cultist's battlecry Invokes Galakrond and gives the minion +1 Attack for each other friendly minion")
		invokeGalakrond(self.Game, self.ID)
		if self.onBoard or self.inHand:
			num = len(self.Game.minionsAlive(self.ID, self))
			self.buffDebuff(num, 0)
		return None
		
		
class FiendishRites(Spell):
	Class, name = "Warlock", "Fiendish Rites"
	requireTarget, mana = False, 4
	index = "Dragons~Warlock~Spell~4~Fiendish Rites"
	description = "Invoke Galakrond. Give your minions +1 Attack"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		PRINT(self.Game, "Fiendish Rites is cast, Invokes Galakrond and gives all friendly minions +1 Attack")
		invokeGalakrond(self.Game, self.ID)
		for minion in fixedList(self.Game.minionsonBoard(self.ID)):
			minion.buffDebuff(1, 0)
		return None
		
		
class VeiledWorshipper(Minion):
	Class, race, name = "Warlock", "", "Veiled Worshipper"
	mana, attack, health = 4, 5, 4
	index = "Dragons~Warlock~Minion~4~5~4~None~Veiled Worshipper~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: If you've Invoked twice, draw 3 cards"
	
	def effectCanTrigger(self):
		self.effectViable = self.Game.Counters.invocationCounts[self.ID] > 1
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if self.Game.Counters.invocationCounts[self.ID] > 1:
			PRINT(self.Game, "Veiled Worshipper's battlecry lets player draw 3 cards")
			self.Game.Hand_Deck.drawCard(self.ID)
			self.Game.Hand_Deck.drawCard(self.ID)
			self.Game.Hand_Deck.drawCard(self.ID)
		return None
		
		
class CrazedNetherwing(Minion):
	Class, race, name = "Warlock", "Dragon", "Crazed Netherwing"
	mana, attack, health = 5, 5, 5
	index = "Dragons~Warlock~Minion~5~5~5~Dragon~Crazed Netherwing~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: If you're holding a Dragon, deal 3 dammage to all other characters"
	def effectCanTrigger(self):
		self.effectViable = self.Game.Hand_Deck.holdingDragon(self.ID, self)
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if self.Game.Hand_Deck.holdingDragon(self.ID):
			PRINT(self.Game, "Crazed Netherwing's battlecry deals 3 damage to all other characters")
			targets = [self.Game.heroes[1], self.Game.heroes[2]] + self.Game.minionsonBoard(1) + self.Game.minionsonBoard(2)
			extractfrom(self, targets)
			self.dealsAOE(targets, [3 for minion in targets])
		return None
		
		
class AbyssalSummoner(Minion):
	Class, race, name = "Warlock", "", "Abyssal Summoner"
	mana, attack, health = 6, 2, 2
	index = "Dragons~Warlock~Minion~6~2~2~None~Abyssal Summoner~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Summon a Demon with Taunt and stats equal to your hand size"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		PRINT(self.Game, "Abyssal Summoner's battlecry summons a Demon with Taunt and stats equal to player's hand size")
		handSize = len(self.Game.Hand_Deck.hands[self.ID])
		if handSize == 1:
			self.Game.summon(AbyssalDestroyer_Mutable_1(self.Game, self.ID), self.position+1, self.ID)
		elif handSize > 1:
			cost = min(handSize, 10)
			newIndex = "Dragons~Warlock~%d~%d~%d~Minion~Demon~Abyssal Destroyer~Taunt~Uncollectible"%(cost, handSize, handSize)
			subclass = type("AbyssalDestroyer_Mutable_"+str(handSize), (AbyssalDestroyer_Mutable_1, ),
							{"mana": cost, "attack": handSize, "health": handSize,
							"index": newIndex}
							)
			self.Game.cardPool[newIndex] = subclass
			self.Game.summon(subclass(self.Game, self.ID), self.position+1, self.ID)
		return None
		
class AbyssalDestroyer_Mutable_1(Minion):
	Class, race, name = "Warlock", "Demon", "Abyssal Destroyer"
	mana, attack, health = 1, 1, 1
	index = "Dragons~Warlock~Minion~1~1~1~Demon~Abyssal Destroyer~Taunt~Uncollectible"
	requireTarget, keyWord, description = False, "Taunt", "Taunt"
	
	
class GalakrondsMalice(HeroPower):
	mana, name, requireTarget = 2, "Galakrond's Malice", False
	index = "Shaman~Hero Power~2~Galakrond's Malice"
	description = "Summon two 1/1 Imps"
	def available(self, choice=0):
		if self.heroPowerTimes >= self.heroPowerChances_base + self.heroPowerChances_extra:
			return False
		if self.Game.space(self.ID) < 1:
			return False
		return True
		
	def effect(self, target=None, choice=0):
		PRINT(self.Game, "Hero Power Galakrond's Malice summons two 1/1 Imps")
		self.Game.summon([DraconicImp(self.Game, self.ID) for i in range(2)], (-1, "totheRightEnd"), self.ID, "")
		return 0
		
class GalakrondtheWretched(Galakrond_Hero):
	mana, weapon, description = 7, None, "Battlecry: Summon a random Demon. (Invoke twice to upgrade)"
	Class, name, heroPower, armor = "Warlock", "Galakrond, the Wretched", GalakrondsMalice, 5
	index = "Dragons~Warlock~Hero Card~7~Galakrond, the Wretched~Battlecry~Legendary"
	poolIdentifier = "Demons to Summon"
	@classmethod
	def generatePool(cls, Game):
		return "Demons to Summon", list(Game.MinionswithRace["Demon"].values())
		
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.upgradedGalakrond = GalakrondtheApocalypes_Warlock
		self.progress = 0
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if curGame.mode == 0:
			if curGame.guides:
				demon = curGame.guides.pop(0)
			else:
				demon = npchoice(curGame.RNGPools["Demons to Summon"])
				curGame.fixedGuides.append(demon)
			PRINT(curGame, "Galakrond, the Wretched's battlecry summons a random Demon")
			curGame.summon(demon(curGame, self.ID), -1, self.ID)
		return None
		
class GalakrondtheApocalypes_Warlock(Galakrond_Hero):
	mana, weapon, description = 7, None, "Battlecry: Summon 2 random Demons. (Invoke twice to upgrade)"
	Class, name, heroPower, armor = "Warlock", "Galakrond, the Apocalypes", GalakrondsMalice, 5
	index = "Dragons~Warlock~Hero Card~7~Galakrond, the Apocalypes~Battlecry~Legendary~Uncollectible"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.upgradedGalakrond = GalakrondAzerothsEnd_Warlock
		self.progress = 0
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if curGame.mode == 0:
			if curGame.guides:
				demons = list(curGame.guides.pop(0))
			else:
				demons = npchoice(curGame.RNGPools["Demons to Summon"], 2, replace=True)
				curGame.fixedGuides.append(tuple(demons))
			PRINT(curGame, "Galakrond, the Apocalypes's battlecry summons 2 random Demons")
			curGame.summon([demon(curGame, self.ID) for demon in demons], -1, self.ID)
		return None
		
class GalakrondAzerothsEnd_Warlock(Galakrond_Hero):
	mana, weapon, description = 7, None, "Battlecry: Summon 4 random Demons. Equip a 5/2 Claw"
	Class, name, heroPower, armor = "Warlock", "Galakrond, Azeroth's End", GalakrondsMalice, 5
	index = "Dragons~Warlock~Hero Card~7~Galakrond, Azeroth's End~Battlecry~Legendary~Uncollectible"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.upgradedGalakrond = None
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if curGame.mode == 0:
			if curGame.guides:
				demons = list(curGame.guides.pop(0))
			else:
				demons = npchoice(curGame.RNGPools["Demons to Summon"], 4, replace=True)
				curGame.fixedGuides.append(tuple(demon))
			PRINT(curGame, "Galakrond, Azeroth's End's battlecry summons 4 random Demons")
			curGame.summon([demon(curGame, self.ID) for demon in demons], -1, self.ID)
		PRINT(curGame, "Galakrond, Azeroth's End's battlecry equips a 5/2 Claw for player")
		curGame.equipWeapon(DragonClaw(curGame, self.ID))
		return None
		
class DraconicImp(Minion):
	Class, race, name = "Warlock", "Demon", "Draconic Imp"
	mana, attack, health = 1, 1, 1
	index = "Dragons~Warlock~Minion~1~1~1~Demon~Draconic Imp~Uncollectible"
	requireTarget, keyWord, description = False, "", ""
	
	
class ValdrisFelgorge(Minion):
	Class, race, name = "Warlock", "", "Valdris Felgorge"
	mana, attack, health = 7, 4, 4
	index = "Dragons~Warlock~Minion~7~4~4~None~Valdris Felgorge~Battlecry~Legendary"
	requireTarget, keyWord, description = False, "", "Battlecry: Increase your maximum hand size to 12. Draw 4 cards"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		PRINT(self.Game, "Valdris Felgorge's battlecry increases player's maximum hand size to 12 and lets player draw 4 cards")
		self.Game.Hand_Deck.handUpperLimit[self.ID] = 12
		for i in range(4):
			self.Game.Hand_Deck.drawCard(self.ID)
		return None
		
		
class ZzerakutheWarped(Minion):
	Class, race, name = "Warlock", "Dragon", "Zzeraku the Warped"
	mana, attack, health = 8, 4, 12
	index = "Dragons~Warlock~Minion~8~4~12~Dragon~Zzeraku the Warped~Legendary"
	requireTarget, keyWord, description = False, "", "Whenever your hero takes damage, summon a 6/6 Nether Drake"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_ZzerakutheWarped(self)]
		
class Trigger_ZzerakutheWarped(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["HeroTakesDamage"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return target == self.entity.Game.heroes[self.entity.ID]
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		PRINT(self.entity.Game, "Player takes damage and %s summons a 6/6 Nether Drake"%self.entity.name)
		self.entity.Game.summon(NetherDrake(self.entity.Game, self.entity.ID), self.entity.position+1, self.entity.ID)
		
class NetherDrake(Minion):
	Class, race, name = "Warlock", "Dragon", "Nether Drake"
	mana, attack, health = 6, 6, 6
	index = "Dragons~Warlock~Minion~6~6~6~Dragon~Nether Drake~Uncollectible"
	requireTarget, keyWord, description = False, "", ""
	
"""Warrior cards"""
class SkyRaider(Minion):
	Class, race, name = "Warrior", "Pirate", "Sky Raider"
	mana, attack, health = 1, 1, 2
	index = "Dragons~Warrior~Minion~1~1~2~Pirate~Sky Raider~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Add a random Pirate to your hand"
	poolIdentifier = "Pirates"
	@classmethod
	def generatePool(cls, Game):
		return "Pirates", list(Game.MinionswithRace["Pirate"].values())
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if curGame.mode == 0:
			if curGame.guides:
				pirate = curGame.guides.pop(0)
			else:
				pirate = npchoice(curGame.RNGPools["Pirates"])
				curGame.fixedGuides.append(pirate)
			PRINT(curGame, "Sky Raider's battlecry adds a random Pirate to player's hand")
			curGame.Hand_Deck.addCardtoHand(pirate, self.ID, "CreateUsingType")
		return None
		
		
class RitualChopper(Weapon):
	Class, name, description = "Warrior", "Ritual Chopper", "Battlecry: Invoke Galakrond"
	mana, attack, durability = 2, 1, 2
	index = "Dragons~Warrior~Weapon~2~1~2~Ritual Chopper~Battlecry"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		PRINT(self.Game, "Ritual Chopper's battlecry Invokes Galakrond")
		invokeGalakrond(self.Game, self.ID)
		return None
		
		
class Awaken(Spell):
	Class, name = "Warrior", "Awaken!"
	requireTarget, mana = False, 3
	index = "Dragons~Warrior~Spell~3~Awaken!"
	description = "Invoke Galakrond. Deal 1 damage to all minions"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		damage = (1 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		PRINT(self.Game, "Awaken! is cast, Invokes Galakrond and deals %d damage to all minions"%damage)
		invokeGalakrond(self.Game, self.ID)
		targets = self.Game.minionsonBoard(self.ID) + self.Game.minionsonBoard(3-self.ID)
		self.dealsAOE(targets, [damage for minion in targets])
		return None
		
		
class Ancharrr(Weapon):
	Class, name, description = "Warrior", "Ancharrr", "After your hero attacks, draw a Pirate from your deck"
	mana, attack, durability = 3, 2, 2
	index = "Dragons~Warrior~Weapon~3~2~2~Ancharrr~Legendary"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_Ancharrr(self)]
		
class Trigger_Ancharrr(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["BattleFinished"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return subject == self.entity.Game.heroes[self.entity.ID] and self.entity.onBoard
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		curGame = self.entity.Game
		if curGame.mode == 0:
			if curGame.guides:
				i = curGame.guides.pop(0)
				if i < 0: return
			else:
				spellsinDeck = [i for i, card in enumerate(ownDeck) if card.type == "Spell"]
				if spellsinDeck:
					i = npchoice(spellsinDeck)
					curGame.fixedGuides.append(i)
				else:
					curGame.fixedGuides.append(-1)
					return
			PRINT(curGame, "After player attacks, Ancharrr lets player draw a Pirate from the deck")
			curGame.Hand_Deck.drawCard(self.ID, i)
			
			
class EVILQuartermaster(Minion):
	Class, race, name = "Warrior", "", "EVIL Quartermaster"
	mana, attack, health = 3, 2, 3
	index = "Dragons~Warrior~Minion~3~2~3~None~EVIL Quartermaster~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Add a Lackey to your hand. Gain 3 Armor"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if curGame.mode == 0:
			if curGame.guides:
				lackey = curGame.guides.pop(0)
			else:
				lackey = npchoice(Lackeys)
				curGame.fixedGuides.append(lackey)
			PRINT(curGame, "EVIL Quartermaster's battlecry adds a random Lackey to player's hand and lets player gain 3 Armor")
			curGame.Hand_Deck.addCardtoHand(lackey, self.ID, "CreateUsingType")
		curGame.heroes[self.ID].gainsArmor(3)
		return None
		
		
class RammingSpeed(Spell):
	Class, name = "Warrior", "Ramming Speed"
	requireTarget, mana = True, 3
	index = "Dragons~Warrior~Spell~3~Ramming Speed"
	description = "Force a minion to attack one of its neighbors"
	def targetExists(self, choice=0):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard and target.health > 0 and target.dead == False
		
	#不知道目标随从不在手牌中时是否会有任何事情发生
	#不会消耗随从的攻击机会
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target and target.onBoard and target.health > 0 and target.dead == False:
			curGame = self.Game
			if curGame.mode == 0:
				if curGame.guides:
					i, where = curGame.guides.pop(0)
					if i < 0: return target
					else: minion = curGame.find(i, where)
				else:
					targets = curGame.adjacentMinions2(target)[0]
					if targets:
						minion = npchoice(targets)
						curGame.fixedGuides.append((minion.position, "minion%d"%minion.ID))
					else:
						curGame.fixedGuides.append((0, ''))
						return target
				curGame.battle(target, minion, False, False)
		return target
		
class ScionofRuin(Minion):
	Class, race, name = "Warrior", "Dragon", "Scion of Ruin"
	mana, attack, health = 4, 3, 2
	index = "Dragons~Warrior~Minion~4~3~2~Dragon~Scion of Ruin~Battlecry"
	requireTarget, keyWord, description = False, "Rush", "Rush. Battlecry: If you've Invoked twice, summon two copies of this"
	
	def effectCanTrigger(self):
		self.effectViable = self.Game.Counters.invocationCounts[self.ID] > 1
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if self.Game.Counters.invocationCounts[self.ID] > 1:
			PRINT(self.Game, "Scion of Ruin's battlecry summons two copies of the minion")
			if self.onBoard:
				copies = [self.selfCopy(self.ID), self.selfCopy(self.ID)]
				self.Game.summon(copies, (self.position, "leftandRight"), self.ID)
			else: #假设废墟之子在战吼前死亡或者离场，则召唤基础复制
				copies = [ScionofRuin(self.Game, self.ID) for i in range(2)]
				self.Game.summon(copies, (-1, "totheRightEnd"), self.ID)
		return None
		
		
class Skybarge(Minion):
	Class, race, name = "Warrior", "Mech", "Skybarge"
	mana, attack, health = 3, 2, 5
	index = "Dragons~Warrior~Minion~3~2~5~Mech~Skybarge"
	requireTarget, keyWord, description = False, "", "After you summon a Pirate, deal 2 damage to a random enemy"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.triggersonBoard = [Trigger_Skybarge(self)]
		
class Trigger_Skybarge(TriggeronBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionBeenSummoned"])
		
	def canTrigger(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject.ID == self.entity.ID and "Pirate" in subject.race
		
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
			PRINT(curGame, "A friendly Pirate %s is summoned and Skybarge deals 1 damage to random enemy %s"%(subject.name, target.name))
			self.entity.dealsDamage(target, 2)
			
			
class MoltenBreath(Spell):
	Class, name = "Warrior", "Molten Breath"
	requireTarget, mana = True, 4
	index = "Dragons~Warrior~Spell~4~Molten Breath"
	description = "Deal 5 damage to a minion. If you're holding Dragon, gain 5 Armor"
	def effectCanTrigger(self):
		self.effectViable = self.Game.Hand_Deck.holdingDragon(self.ID)
		
	def targetExists(self, choice=0):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			damage = (5 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			PRINT(self.Game, "Molten Breath deals %d damage to minion %s"%(damage, target.name))
			self.dealsDamage(target, damage)
			if self.Game.Hand_Deck.holdingDragon(self.ID) and self.Game.Hand_Deck.handNotFull(self.ID):
				PRINT(self.Game, "Molten Breath also lets player gain 5 Armor")
				self.Game.heroes[self.ID].gainsArmor(5)
		return target
		
		
class GalakrondsMight(HeroPower):
	mana, name, requireTarget = 2, "Galakrond's Might", False
	index = "Rogue~Hero Power~2~Galakrond's Might"
	description = "Give your hero +3 Attack this turn"
	def effect(self, target=None, choice=0):
		PRINT(self.Game, "Hero Power Galakrond's Might gives player +3 Attack this turn")
		self.Game.heroes[self.ID].gainTempAttack(3)
		return 0
		
class GalakrondtheUnbreakable(Galakrond_Hero):
	mana, weapon, description = 7, None, "Battlecry: Draw 1 minion. Give it +4/+4. (Invoke twice to upgrade)"
	Class, name, heroPower, armor = "Warrior", "Galakrond, the Unbreakable", GalakrondsMight, 5
	index = "Dragons~Warrior~Hero Card~7~Galakrond, the Unbreakable~Battlecry~Legendary"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.upgradedGalakrond = GalakrondtheApocalypes_Warrior
		self.progress = 0
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		ownDeck = curGame.Hand_Deck.decks[self.ID]
		if curGame.mode == 0:
			if curGame.guides:
				i = curGame.guides.pop(0)
				if i < 0: return None
			else:
				minionsinDeck = [i for i, card in enumerate(ownDeck) if card.type == "Minion"]
				if minionsinDeck:
					i = npchoice(minionsinDeck)
					curGame.fixedGuides.append(i)
				else:
					curGame.fixedGuides.append(-1)
					return None
			PRINT(curGame, "Galakrond, the Unbreakable's battlecry lets player draw a minion from deck")
			minion = curGame.Hand_Deck.drawCard(self.ID, i)[0]
			if minion:
				PRINT(curGame, "Galakrond, the Unbreakable gives the drawn Minion +4/+4")
				minion.buffDebuff(4, 4)
		return None
		
class GalakrondtheApocalypes_Warrior(Galakrond_Hero):
	mana, weapon, description = 7, None, "Battlecry: Draw 2 minions. Give them +4/+4. (Invoke twice to upgrade)"
	Class, name, heroPower, armor = "Warrior", "Galakrond, the Apocalypes", GalakrondsMight, 5
	index = "Dragons~Warrior~Hero Card~7~Galakrond, the Apocalypes~Battlecry~Legendary~Uncollectible"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.upgradedGalakrond = GalakrondAzerothsEnd_Warrior
		self.progress = 0
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		ownDeck = curGame.Hand_Deck.decks[self.ID]
		for num in range(2):
			if curGame.mode == 0:
				if curGame.guides:
					i = curGame.guides.pop(0)
					if i < 0: return None
				else:
					minionsinDeck = [i for i, card in enumerate(ownDeck) if card.type == "Minion"]
					if minionsinDeck:
						i = npchoice(minionsinDeck)
						curGame.fixedGuides.append(i)
					else:
						curGame.fixedGuides.append(-1)
						return None
				PRINT(curGame, "Galakrond, the Apocalypes's battlecry lets player draw a minion from deck")
				minion = curGame.Hand_Deck.drawCard(self.ID, i)[0]
				if minion:
					PRINT(curGame, "Galakrond, the Apocalypes gives the drawn Minion +4/+4")
					minion.buffDebuff(4, 4)
		return None
		
class GalakrondAzerothsEnd_Warrior(Galakrond_Hero):
	mana, weapon, description = 7, None, "Battlecry: Draw 4 minions. Give them +4/+4. Equip a 5/2 Claw"
	Class, name, heroPower, armor = "Warrior", "Galakrond, Azeroth's End", GalakrondsMight, 5
	index = "Dragons~Warrior~Hero Card~7~Galakrond, Azeroth's End~Battlecry~Legendary~Uncollectible"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.upgradedGalakrond = None
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		ownDeck = curGame.Hand_Deck.decks[self.ID]
		for num in range(4):
			if curGame.mode == 0:
				if curGame.guides:
					i = curGame.guides.pop(0)
					if i < 0: return None
				else:
					minionsinDeck = [i for i, card in enumerate(ownDeck) if card.type == "Minion"]
					if minionsinDeck:
						i = npchoice(minionsinDeck)
						curGame.fixedGuides.append(i)
					else:
						curGame.fixedGuides.append(-1)
						return None
				PRINT(curGame, "Galakrond, Azeroth's End's battlecry lets player draw a minion from deck")
				minion = curGame.Hand_Deck.drawCard(self.ID, i)[0]
				if minion:
					PRINT(curGame, "Galakrond, Azeroth's End's battlecry gives the drawn Minion +4/+4")
					minion.buffDebuff(4, 4)
		PRINT(curGame, "Galakrond, Azeroth's End's battlecry equips a 5/2 Claw for player")
		curGame.equipWeapon(DragonClaw(curGame, self.ID))
		return None
		
		
#这个战吼的攻击会消耗随从的攻击次数。在战吼结束后给其加上冲锋或者突袭时，其不能攻击
#战吼的攻击可以正常触发奥秘和攻击目标指向扳机
#攻击过程中死亡之翼濒死会停止攻击，但是如果中途被冰冻是不会停止攻击的。即用战斗不检查攻击的合法性。
#战吼结束之后才会进行战斗的死亡结算，期间被攻击的随从可以降到负血量还留在场上。
class DeathwingMadAspect(Minion):
	Class, race, name = "Warrior", "Dragon", "Deathwing, Mad Aspect"
	mana, attack, health = 8, 12, 12
	index = "Dragons~Warrior~Minion~8~12~12~Dragon~Deathwing, Mad Aspect~Battlecry~Legendary"
	requireTarget, keyWord, description = False, "", "Battlecry: Attack ALL other minions"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if curGame.mode == 0:
			if curGame.guides:
				infos = list(curGame.guides.pop(0))
				PRINT(curGame, "Deathwing, Mad Aspect' battlecry lets minion attack ALL other minions")
				if infos:
					while infos:
						i, where = infos.pop(0)
						minion = curGame.find(i, where)
						PRINT(curGame, "Deathwing, Mad Aspect's battlecry makes %s attacks minion %s"%(curGame.minionPlayed.name, minion.name))
						curGame.battle(curGame.minionPlayed, minion, False, True, False, False)
					curGame.sendSignal("BattleFinished", self.Game.turn, self, None, 0, "")
			else:
				minions = curGame.Game.minionsAlive(self.ID, curGame.minionPlayed) + curGame.minionsAlive(3-self.ID)
				npshuffle(minions)
				if minions:
					infos = []
					while minions:
						minion = minions.pop(0)
						if minion.onBoard and minion.health > 0 and not minion.dead:
							if curGame.battle(curGame.minionPlayed, minion, False, True, False, False):
								infos.append((minion.position, "minion%d"%minion.ID))
							else: break
					curGame.fixedGuides.append(tuple(infos))
				else: curGame.fixedGuides.append(())
		return None
		
		
		
Dragons_Indices = {"Dragons~Neutral~Minion~1~2~2~None~Blazing Battlemage": BlazingBattlemage,
					"Dragons~Neutral~Minion~1~0~5~None~Depth Charge": DepthCharge,
					"Dragons~Neutral~Minion~1~1~2~Mech~Hot Air Balloon": HotAirBalloon,
					"Dragons~Neutral~Minion~1~1~1~None~Draconic Lackey~Battlecry~Uncollectible": DraconicLackey,
					"Dragons~Neutral~Minion~2~2~1~Beast~Evasive Chimaera~Poisonous": EvasiveChimaera,
					"Dragons~Neutral~Minion~2~2~3~None~Dragon Breeder~Battlecry": DragonBreeder,
					"Dragons~Neutral~Minion~2~3~2~None~Grizzled Wizard~Battlecry": GrizzledWizard,
					"Dragons~Neutral~Minion~2~2~2~Pirate~Parachute Brigand": ParachuteBrigand,
					"Dragons~Neutral~Minion~2~2~2~Murloc~Tasty Flyfish~Deathrattle": TastyFlyfish,
					"Dragons~Neutral~Minion~2~2~3~None~Transmogrifier": Transmogrifier,
					"Dragons~Neutral~Minion~2~3~2~None~Wyrmrest Purifier~Battlecry": WyrmrestPurifier,
					"Dragons~Neutral~Minion~3~3~4~None~Blowtorch Saboteur~Battlecry": BlowtorchSaboteur,
					"Dragons~Neutral~Minion~3~3~4~Beast~Dread Raven": DreadRaven,
					"Dragons~Neutral~Minion~3~1~3~Elemental~Fire Hawk~Battlecry": FireHawk,
					"Dragons~Neutral~Minion~3~3~3~None~Goboglide Tech~Battlecry": GoboglideTech,
					"Dragons~Neutral~Minion~3~3~4~Elemental~Living Dragonbreath": LivingDragonbreath,
					"Dragons~Neutral~Minion~3~3~3~None~Scalerider~Battlecry": Scalerider,
					"Dragons~Neutral~Minion~4~4~3~Beast~Bad Luck Albatross~Deathrattle": BadLuckAlbatross,
					"Dragons~Neutral~Minion~1~1~1~Beast~Albatross~Uncollectible": Albatross,
					"Dragons~Neutral~Minion~4~2~2~None~Devoted Maniac~Rush~Battlecry": DevotedManiac,
					"Dragons~Neutral~Minion~4~4~4~None~Dragonmaw Poacher~Battlecry": DragonmawPoacher,
					"Dragons~Neutral~Minion~4~5~4~Dragon~Evasive Feywing": EvasiveFeywing,
					"Dragons~Neutral~Minion~4~5~4~None~Frizz Kindleroost~Battlecry~Legendary": FrizzKindleroost,
					"Dragons~Neutral~Minion~4~2~6~Beast~Hippogryph~Rush~Taunt": Hippogryph,
					"Dragons~Neutral~Minion~4~4~2~Pirate~Hoard Pillager~Battlecry": HoardPillager,
					"Dragons~Neutral~Minion~4~3~3~None~Troll Batrider~Battlecry": TrollBatrider,
					"Dragons~Neutral~Minion~4~2~5~None~Wing Commander": WingCommander,
					"Dragons~Neutral~Minion~4~3~9~None~Zul'Drak Ritualist~Taunt~Battlecry": ZulDrakRitualist,
					"Dragons~Neutral~Minion~5~5~5~Dragon~Big Ol' Whelp~Battlecry": BigOlWhelp,
					"Dragons~Neutral~Minion~5~0~3~None~Chromatic Egg~Battlecry~Deathrattle": ChromaticEgg,
					"Dragons~Neutral~Minion~5~3~5~Dragon~Cobalt Spellkin~Battlecry": CobaltSpellkin,
					"Dragons~Neutral~Minion~5~4~4~None~Faceless Corruptor~Rush~Battlecry": FacelessCorruptor,
					"Dragons~Neutral~Minion~5~4~4~None~Kobold Stickyfinger~Battlecry": KoboldStickyfinger,
					"Dragons~Neutral~Minion~5~5~5~None~Platebreaker~Battlecry": Platebreaker,
					"Dragons~Neutral~Minion~5~4~5~None~Shield of Galakrond~Taunt~Battlecry": ShieldofGalakrond,
					"Dragons~Neutral~Minion~5~3~3~Murloc~Skyfin~Battlecry": Skyfin,
					"Dragons~Neutral~Minion~5~6~5~None~Tentacled Menace~Battlecry": TentacledMenace,
					"Dragons~Neutral~Minion~6~6~6~Mech~Camouflaged Dirigible~Battlecry": CamouflagedDirigible,
					"Dragons~Neutral~Minion~6~5~3~Dragon~Evasive Wyrm~Divine Shield~Rush": EvasiveWyrm,
					"Dragons~Neutral~Minion~6~4~5~Mech~Gyrocopter~Rush~Windfury": Gyrocopter,
					"Dragons~Neutral~Minion~6~6~6~None~Kronx Dragonhoof~Battlecry~Legendary": KronxDragonhoof,
					"Dragons~Neutral~Minion~8~8~8~Dragon~Reanimated Dragon~Uncollectible": ReanimatedDragon,
					"Dragons~Neutral~Minion~6~5~5~None~Utgarde Grapplesniper~Battlecry": UtgardeGrapplesniper,
					"Dragons~Neutral~Minion~7~7~7~Dragon~Evasive Drakonid~Taunt": EvasiveDrakonid,
					"Dragons~Neutral~Minion~7~1~7~None~Shu'ma~Legendary": Shuma,
					"Dragons~Neutral~Minion~1~1~1~None~Tentacle~Uncollectible": Tentacle_Dragons,
					"Dragons~Neutral~Minion~8~4~10~Dragon~Twin Tyrant~Battlecry": TwinTyrant,
					"Dragons~Neutral~Minion~9~8~8~Dragon~Dragonqueen Alexstrasza~Battlecry~Legendary": DragonqueenAlexstrasza,
					"Dragons~Neutral~Minion~9~5~5~Demon~Sathrovarr~Battlecry~Legendary": Sathrovarr,
					"Dragons~Druid~Spell~0~Embiggen": Embiggen,
					"Dragons~Druid~Spell~1~Secure the Deck~~Quest": SecuretheDeck,
					"Dragons~Druid~Spell~1~Strength in Numbers~~Quest": StrengthinNumbers,
					"Dragons~Druid~Spell~1~Treenforcements~Choose One": Treenforcements,
					"Dragons~Druid~Spell~1~Spin 'em Up~Uncollectible": SmallRepairs,
					"Dragons~Druid~Spell~1~Spin 'em Up~Uncollectible": SpinemUp,
					"Dragons~Druid~Spell~2~Breath of Dreams": BreathofDreams,
					"Dragons~Druid~Minion~2~1~1~None~Shrubadier~Battlecry": Shrubadier,
					"Dragons~Druid~Minion~2~2~2~None~Treant~Uncollectible": Treant_Dragons,
					"Dragons~Druid~Spell~5~Aeroponics": Aeroponics,
					"Dragons~Druid~Minion~6~4~8~Dragon~Emeral Explorer~Taunt~Battlecry": EmeraldExplorer,
					"Dragons~Druid~Minion~7~5~10~None~Goru the Mightree~Taunt~Battlecry~Legendary": GorutheMightree,
					"Dragons~Druid~Minion~9~4~12~Dragon~Ysera, Unleashed~Battlecry~Legendary": YseraUnleashed,
					"Dragons~Druid~Spell~9~Dream Portal~Casts When Drawn~Uncollectible": DreamPortal,
					"Dragons~Hunter~Spell~1~Clear the Way~~Quest": CleartheWay,
					"Dragons~Hunter~Minion~4~4~4~Beast~Gryphon~Rush~Uncollectible": Gryphon_Dragons,
					"Dragons~Hunter~Minion~1~1~3~None~Dwarven Sharpshooter": DwarvenSharpshooter,
					"Dragons~Hunter~Spell~1~Toxic Reinforcement~~Quest": ToxicReinforcements,
					"Dragons~Neutral~Minion~1~1~1~None~Leper Gnome~Deathrattle": LeperGnome_Dragons,
					"Dragons~Hunter~Spell~2~Corrosive Breath": CorrosiveBreath,
					"Dragons~Hunter~Minion~2~2~3~Beast~Phase Stalker": PhaseStalker,
					"Dragons~Hunter~Minion~3~4~1~Beast~Diving Gryphon~Rush~Battlecry": DivingGryphon,
					"Dragons~Hunter~Minion~3~2~3~Dragon~Primordial Explorer~Poisonous~Battlecry": PrimordialExplorer,
					"Dragons~Hunter~Weapon~3~3~2~Stormhammer": Stormhammer,
					"Dragons~Hunter~Minion~4~3~5~Mech~Dragonbane~Legendary": Dragonbane,
					"Dragons~Hunter~Minion~6~7~6~Dragon~Veranus~Battlecry~Legendary": Veranus,
					"Dragons~Mage~Spell~1~Arcane Breath": ArcaneBreath,
					"Dragons~Mage~Spell~1~Elemental Allies~~Quest": ElementalAllies,
					"Dragons~Mage~Spell~1~Learn Draconic~~Quest": LearnDraconic,
					"Dragons~Mage~Minion~6~6~6~Dragon~Draconic Emissary~Uncollectible": DraconicEmissary,
					"Dragons~Mage~Minion~1~1~1~Elemental~Violet Spellwing~Deathrattle": VioletSpellwing,
					"Dragons~Mage~Minion~3~2~5~Elemental~Chenvaala~Legendary": Chenvaala,
					"Dragons~Mage~Minion~5~5~5~Elemental~Snow Elemental~Uncollectible": SnowElemental,
					"Dragons~Mage~Minion~4~2~3~Dragon~Azure Explorer~Spell Damage~Battlecry": AzureExplorer,
					"Dragons~Mage~Spell~0~Malygos's Frostbolt~Uncollectible~Legendary": MalygossFrostbolt,
					"Dragons~Mage~Spell~1~Malygos's Missiles~Uncollectible~Legendary": MalygossMissiles,
					"Dragons~Mage~Spell~1~Malygos's Nova~Uncollectible~Legendary": MalygossNova,
					"Dragons~Mage~Spell~1~Malygos's Polymorph~Uncollectible~Legendary": MalygossPolymorph,
					"Dragons~Mage~Spell~1~Malygos's Tome~Uncollectible~Legendary": MalygossTome,
					"Dragons~Mage~Spell~2~Malygos's Explosion~Uncollectible~Legendary": MalygossExplosion,
					"Dragons~Mage~Spell~3~Malygos's Intellect~Uncollectible~Legendary": MalygossIntellect,
					"Dragons~Mage~Spell~3~Malygos's Fireball~Uncollectible~Legendary": MalygossFireball,
					"Dragons~Mage~Spell~7~Malygos's Flamestrike~Uncollectible~Legendary": MalygossFlamestrike,
					"Dragons~Mage~Minion~1~1~1~Beast~Malygos's Sheep~Uncollectible~Legendary": MalygossSheep,
					"Dragons~Mage~Minion~5~2~8~Dragon~Malygos, Aspect of Magic~Battlecry~Legendary": MalygosAspectofMagic,
					"Dragons~Mage~Spell~5~Rolling Fireball": RollingFireball,
					"Dragons~Mage~Minion~7~4~4~None~Dragoncaster~Battlecry": Dragoncaster,
					"Dragons~Mage~Minion~8~8~8~Elemental~Mana Giant": ManaGiant,
					"Dragons~Paladin~Spell~1~Righteous Cause~~Quest": RighteousCause,
					"Dragons~Paladin~Spell~1~Sand Breath": SandBreath,
					"Dragons~Paladin~Spell~2~Sanctuary~~Quest": Sanctuary,
					"Dragons~Paladin~Minion~4~3~6~None~Indomitable Champion~Taunt~Uncollectible": IndomitableChampion,
					"Dragons~Paladin~Minion~3~2~3~Dragon~Bronze Explorer~Lifesteal~Battlecry": BronzeExplorer,
					"Dragons~Paladin~Minion~3~1~2~Mech~Sky Claw~Battlecry": SkyClaw,
					"Dragons~Paladin~Minion~1~1~1~Mech~Microcopter~Uncollectible": Microcopter,
					"Dragons~Paladin~Minion~3~3~3~None~Dragonrider Talritha~Deathrattle~Legendary": DragonriderTalritha,
					"Dragons~Paladin~Minion~4~4~2~None~Lightforged Zealot~Battlecry": LightforgedZealot,
					"Dragons~Paladin~Minion~4~8~8~Dragon~Nozdormu the Timeless~Battlecry~Legendary": NozdormutheTimeless,
					"Dragons~Paladin~Minion~5~4~6~Dragon~Amber Watcher~Battlecry": AmberWatcher,
					"Dragons~Paladin~Minion~7~7~7~None~Lightforged Crusader~Battlecry": LightforgedCrusader,
					"Dragons~Priest~Spell~0~Whispers of EVIL": WhispersofEVIL,
					"Dragons~Priest~Minion~1~1~2~None~Disciple of Galakrond~Battlecry": DiscipleofGalakrond,
					"Dragons~Priest~Minion~2~2~2~None~Envoy of Lazul~Battlecry": EnvoyofLazul,
					"Dragons~Priest~Spell~3~Breath of the Infinite": BreathoftheInfinite,
					"Dragons~Priest~Minion~3~3~3~None~Mindflayer Kaahrj~Battlecry~Deathrattle~Legendary": MindflayerKaahrj,
					"Dragons~Priest~Minion~4~3~6~Dragon~Fate Weaver~Battlecry": FateWeaver,
					"Dragons~Priest~Spell~4~Grave Rune": GraveRune,
					"Dragons~Priest~Minion~5~4~5~Dragon~Chronobreaker~Deathrattle": Chronobreaker,
					"Dragons~Priest~Spell~5~Time Rip": TimeRip,
					"Dragons~Priest~Hero Card~7~Galakrond, the Unspeakable~Battlecry~Legendary": GalakrondtheUnspeakable,
					"Dragons~Priest~Hero Card~7~Galakrond, the Apocalypes~Battlecry~Legendary~Uncollectible": GalakrondtheApocalypes_Priest,
					"Dragons~Priest~Hero Card~7~Galakrond, Azeroth's End~Battlecry~Legendary~Uncollectible": GalakrondAzerothsEnd_Priest,
					"Dragons~Neutral~Weapon~5~5~2~Dragon Claw~Uncollectible": DragonClaw,
					"Dragons~Priest~Minion~8~8~8~Dragon~Murozond the Infinite~Battlecry~Legendary": MurozondtheInfinite,
					"Dragons~Rogue~Minion~1~1~1~Pirate~Bloodsail Flybooter~Battlecry": BloodsailFlybooter,
					"Dragons~Rogue~Minion~1~1~1~Pirate~Sky Pirate~Uncollectible": SkyPirate,
					"Dragons~Rogue~Spell~1~Dragon's Hoard": DragonsHoard,
					"Dragons~Rogue~Spell~1~Praise Galakrond": PraiseGalakrond,
					"Dragons~Rogue~Spell~3~Seal Fate": SealFate,
					"Dragons~Rogue~Minion~4~3~3~None~Umbral Skulker~Battlecry": UmbralSkulker,
					"Dragons~Rogue~Minion~5~2~5~None~Necrium Apothecary~Combo": NecriumApothecary,
					"Dragons~Rogue~Minion~5~4~4~None~Stowaway~Battlecry": Stowaway,
					"Dragons~Rogue~Minion~5~7~5~Dragon~Waxadred~Deathrattle~Legendary": Waxadred,
					"Dragons~Rogue~Spell~5~Waxadred's Candle~Casts When Drawn~Uncollectible": WaxadredsCandle,
					"Dragons~Rogue~Spell~6~Candle Breath": CandleBreath,
					"Dragons~Rogue~Minion~6~4~4~None~Flik Skyshiv~Battlecry~Legendary": FlikSkyshiv,
					"Dragons~Rogue~Hero Card~7~Galakrond, the Nightmare~Battlecry~Legendary": GalakrondtheNightmare,
					"Dragons~Rogue~Hero Card~7~Galakrond, the Apocalypes~Battlecry~Legendary~Uncollectible": GalakrondtheApocalypes_Rogue,
					"Dragons~Rogue~Hero Card~7~Galakrond, Azeroth's End~Battlecry~Legendary~Uncollectible": GalakrondAzerothsEnd_Rogue,
					"Dragons~Shaman~Spell~2~Invocation of Frost": InvocationofFrost,
					"Dragons~Shaman~Minion~1~1~3~Elemental~Surging Tempest": SurgingTempest,
					"Dragons~Shaman~Minion~4~5~7~Dragon~Squallhunter~Spell Damage~Overload": Squallhunter,
					"Dragons~Shaman~Spell~1~Storm's Wrath~Overload": StormsWrath,
					"Dragons~Shaman~Spell~3~Lightning Breath": LightningBreath,
					"Dragons~Shaman~Minion~5~5~5~None~Bandersmosh": Bandersmosh,
					"Dragons~Shaman~Minion~5~5~5~Elemental~Cumulo-Maximus~Battlecry": CumuloMaximus,
					"Dragons~Shaman~Spell~5~Dragon's Pack": DragonsPack,
					"Dragons~Shaman~Minion~2~2~3~None~Spirit Wolf~Taunt~Uncollectible": SpiritWolf_Dragons,
					"Dragons~Shaman~Minion~6~3~3~None~Corrupt Elementalist~Battlecry": CorruptElementalist,
					"Dragons~Shaman~Minion~6~5~5~Dragon~Nithogg~Battlecry~Legendary": Nithogg,
					"Dragons~Shaman~Minion~1~0~3~None~Storm Egg~Uncollectible": StormEgg,
					"Dragons~Shaman~Minion~4~4~4~Dragon~Storm Drake~Rush~Uncollectible": StormDrake,
					"Dragons~Shaman~Minion~2~2~1~Elemental~Windswept Elemental~Rush~Uncollectible": WindsweptElemental,
					"Dragons~Shaman~Hero Card~7~Galakrond, the Tempest~Battlecry~Legendary": GalakrondtheTempest,
					"Dragons~Shaman~Hero Card~7~Galakrond, the Apocalypes~Battlecry~Legendary~Uncollectible": GalakrondtheApocalypes_Shaman,
					"Dragons~Shaman~Hero Card~7~Galakrond, Azeroth's End~Battlecry~Legendary~Uncollectible": GalakrondAzerothsEnd_Shaman,
					"Dragons~Shaman~Minion~2~2~2~Elemental~Brewing Storm~Rush~Uncollectible": BrewingStorm,
					"Dragons~Shaman~Minion~4~4~4~Elemental~Living Storm~Rush~Uncollectible": LivingStorm,
					"Dragons~Shaman~Minion~8~8~8~Elemental~Raging Storm~Rush~Uncollectible": RagingStorm,
					"Dragons~Warlock~Spell~1~Rain of Fire": RainofFire,
					"Dragons~Warlock~Spell~2~Neth Breath": NetherBreath,
					"Dragons~Warlock~Spell~3~Dark Skies": DarkSkies,
					"Dragons~Warlock~Minion~3~1~1~None~Dragonblight Cultist~Battlecry": DragonblightCultist,
					"Dragons~Warlock~Spell~4~Fiendish Rites": FiendishRites,
					"Dragons~Warlock~Minion~4~5~4~None~Veiled Worshipper~Battlecry": VeiledWorshipper,
					"Dragons~Warlock~Minion~5~5~5~Dragon~Crazed Netherwing~Battlecry": CrazedNetherwing,
					"Dragons~Warlock~Minion~6~2~2~None~Abyssal Summoner~Battlecry": AbyssalSummoner,
					"Dragons~Warlock~Minion~1~1~1~Demon~Abyssal Destroyer~Taunt~Uncollectible": AbyssalDestroyer_Mutable_1,
					"Dragons~Warlock~Hero Card~7~Galakrond, the Wretched~Battlecry~Legendary": GalakrondtheWretched,
					"Dragons~Warlock~Hero Card~7~Galakrond, the Apocalypes~Battlecry~Legendary~Uncollectible": GalakrondtheApocalypes_Warlock,
					"Dragons~Warlock~Hero Card~7~Galakrond, Azeroth's End~Battlecry~Legendary~Uncollectible": GalakrondAzerothsEnd_Warlock,
					"Dragons~Warlock~Minion~1~1~1~Demon~Draconic Imp~Uncollectible": DraconicImp,
					"Dragons~Warlock~Minion~7~4~4~None~Valdris Felgorge~Battlecry~Legendary": ValdrisFelgorge,
					"Dragons~Warlock~Minion~8~4~12~Dragon~Zzeraku the Warped~Legendary": ZzerakutheWarped,
					"Dragons~Warlock~Minion~6~6~6~Dragon~Nether Drake~Uncollectible": NetherDrake,
					"Dragons~Warrior~Minion~1~1~2~Pirate~Sky Raider~Battlecry": SkyRaider,
					"Dragons~Warrior~Weapon~2~1~2~Ritual Chopper~Battlecry": RitualChopper,
					"Dragons~Warrior~Spell~3~Awaken!": Awaken,
					"Dragons~Warrior~Weapon~3~2~2~Ancharrr~Legendary": Ancharrr,
					"Dragons~Warrior~Minion~3~2~3~None~EVIL Quartermaster~Battlecry": EVILQuartermaster,
					"Dragons~Warrior~Spell~3~Ramming Speed": RammingSpeed,
					"Dragons~Warrior~Minion~4~3~2~Dragon~Scion of Ruin~Battlecry": ScionofRuin,
					"Dragons~Warrior~Minion~3~2~5~Mech~Skybarge": Skybarge,
					"Dragons~Warrior~Spell~4~Molten Breath": MoltenBreath,
					"Dragons~Warrior~Hero Card~7~Galakrond, the Unbreakable~Battlecry~Legendary": GalakrondtheUnbreakable,
					"Dragons~Warrior~Hero Card~7~Galakrond, the Apocalypes~Battlecry~Legendary~Uncollectible": GalakrondtheApocalypes_Warrior,
					"Dragons~Warrior~Hero Card~7~Galakrond, Azeroth's End~Battlecry~Legendary~Uncollectible": GalakrondAzerothsEnd_Warrior,
					"Dragons~Warrior~Minion~8~12~12~Dragon~Deathwing, Mad Aspect~Battlecry~Legendary": DeathwingMadAspect
					}
					