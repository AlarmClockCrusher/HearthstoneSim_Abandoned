from CardTypes import *
from Triggers_Auras import *
from numpy.random import choice as npchoice
from numpy.random import randint as nprandint
from numpy.random import shuffle as npshuffle
from numpy import inf as npinf

from Basic import Claw, ArcaneMissiles, TruesilverChampion, TheCoin
from AcrossPacks import Lackeys

"""Descent of Dragons"""
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
	primaryGalakrond = Game.Counters.primaryGalakronds[ID]
	if primaryGalakrond:
		Class = primaryGalakrond.Class
		if "Priest" in Class:
			if Game.mode == 0:
				if Game.GUI: Game.GUI.showOffBoardTrig(GalakrondtheUnbreakable(Game, ID), linger=False)
				if Game.guides:
					minion = Game.guides.pop(0)
				else:
					minion = npchoice(Game.RNGPools["Priest Minions"])
					Game.fixedGuides.append(minion)
				Game.Hand_Deck.addCardtoHand(minion, ID, byType=True)
		elif "Rogue" in Class:
			if Game.mode == 0:
				if Game.GUI: Game.GUI.showOffBoardTrig(GalakrondtheNightmare(Game, ID), linger=False)
				if Game.guides:
					lackey = Game.guides.pop(0)
				else:
					lackey = npchoice(Lackeys)
					Game.fixedGuides.append(lackey)
			Game.Hand_Deck.addCardtoHand(lackey, ID, byType=True)
		elif "Shaman" in Class:
			if Game.GUI: Game.GUI.showOffBoardTrig(GalakrondtheTempest(Game, ID), linger=False)
			Game.summon(WindsweptElemental(Game, ID), -1, ID, "")
		elif "Warlock" in Class:
			if Game.GUI: Game.GUI.showOffBoardTrig(GalakrondtheWretched(Game, ID), linger=False)
			Game.summon([DraconicImp(Game, ID) for i in range(2)], (-1, "totheRightEnd"), ID, "")
		elif "Warrior" in Class:
			if Game.GUI: Game.GUI.showOffBoardTrig(GalakrondtheUnbreakable(Game, ID), linger=False)
			Game.heroes[ID].gainAttack(3)
	#invocation counter increases and upgrade the galakronds
	Game.Counters.invokes[ID] += 1
	for card in Game.Hand_Deck.hands[ID][:]:
		if "Galakrond, " in card.name:
			upgrade = card.upgradedGalakrond
			isPrimaryGalakrond = (card == primaryGalakrond)
			if hasattr(card, "progress"):
				card.progress += 1
				if upgrade and card.progress > 1:
					Game.Hand_Deck.replaceCardinHand(card, upgrade(Game, ID))
					if isPrimaryGalakrond:
						Game.Counters.primaryGalakronds[ID] = upgrade
	for card in Game.Hand_Deck.decks[ID][:]:
		if "Galakrond, " in card.name:
			upgrade = card.upgradedGalakrond
			isPrimaryGalakrond = (card == primaryGalakrond)
			if hasattr(card, "progress"):
				card.progress += 1
				if upgrade and card.progress > 1:
					Game.Hand_Deck.replaceCardinDeck(card, upgrade(Game, ID))
					if isPrimaryGalakrond:
						Game.Counters.primaryGalakronds[ID] = upgrade
						
						
class Galakrond_Hero(Hero):
	def entersHand(self):
		self.inHand = True
		self.onBoard = self.inDeck = False
		self.enterHandTurn = self.Game.numTurn
		if self.Game.Counters.primaryGalakronds[self.ID] is None:
			self.Game.Counters.primaryGalakronds[self.ID] = self
		for trig in self.trigsHand: trig.connect()
		return self
		
	def entersDeck(self):
		self.onBoard, self.inHand, self.inDeck = False, False, True
		self.Game.Manas.calcMana_Single(self)
		if self.Game.Counters.primaryGalakronds[self.ID] is None:
			self.Game.Counters.primaryGalakronds[self.ID] = self
		for trig in self.trigsDeck: trig.connect()
		
	def replaceHero(self, fromHeroCard=False):
		game, ID = self.Game, self.ID
		self.onBoard, self.pos, self.attTimes = True, ID, game.heroes[ID].attTimes
		while self.auraReceivers: self.auraReceivers[0].effectClear()
		
		game.heroes[ID] = self
		if game.Counters.primaryGalakronds[ID] is None: #迦拉克隆的打出不会影响当前的主迦拉克隆？
			game.Counters.primaryGalakronds[ID] = self
		self.heroPower.replaceHeroPower()
		game.sendSignal("HeroReplaced", ID, self, None, 0, "")
		self.calc_Attack() #因为没有装备武器所以需要自己处理攻击力的变化
		
	def played(self, target=None, choice=0, mana=0, posinHand=0, comment=""): #英雄牌使用不存在触发发现的情况
		game, ID = self.Game, self.ID
		oldHero = game.heroes[ID]
		self.health, self.health_max, self.armor = oldHero.health, oldHero.health_max, oldHero.armor
		self.attack_bare, self.tempAttChanges, self.attTimes, self.armor = oldHero.attack_bare, oldHero.tempAttChanges, oldHero.attTimes, oldHero.armor
		self.onBoard, oldHero.onBoard, self.pos = True, False, ID #这个只是为了方便定义(i, where)
		while self.auraReceivers: self.auraReceivers[0].effectClear()
			
		game.powers[ID].disappears()
		game.powers[ID].heroPower = None
		heroPower = self.heroPower #这个英雄技能必须存放起来，之后英雄还有可能被其他英雄替换，但是这个技能要到最后才登场。
		game.heroes[ID] = self #英雄替换。如果后续有埃克索图斯再次替换英雄，则最后的英雄是拉格纳罗斯。
		#The only difference between the normal hero card being played
		if game.Counters.primaryGalakronds[ID] is None:
			game.Counters.primaryGalakronds[ID] = self
		if game.GUI:
			game.GUI.displayCard(self)
			game.GUI.wait(500)
		game.sendSignal("HeroCardPlayed", ID, self, None, mana, "", choice)
		#Guaranteed to be 5 Armor gained
		self.gainsArmor(5)
		game.sendSignal("HeroReplaced", ID, self, None, 0, "")
		game.gathertheDead()
		
		heroPower.replaceHeroPower()
		if game.status[ID]["Battlecry x2"] > 0:
			self.whenEffective(None, "", choice)
		self.whenEffective(None, "", choice)
		#迦拉克隆本身是没有武器的，其战吼会装备武器
		self.calc_Attack()
		self.decideAttChances_base()
		game.gathertheDead()
		
		
"""Mana 1 cards"""
class BlazingBattlemage(Minion):
	Class, race, name = "Neutral", "", "Blazing Battlemage"
	mana, attack, health = 1, 2, 2
	index = "DRAGONS~Neutral~Minion~1~2~2~~Blazing Battlemage"
	requireTarget, keyWord, description = False, "", ""
	name_CN = "灼光战斗法师"
	
	
class DepthCharge(Minion):
	Class, race, name = "Neutral", "", "Depth Charge"
	mana, attack, health = 1, 0, 5
	index = "DRAGONS~Neutral~Minion~1~0~5~~Depth Charge"
	requireTarget, keyWord, description = False, "", "At the start of your turn, deal 5 damage to all minions"
	name_CN = "深潜炸弹"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_DepthCharge(self)]
		
class Trig_DepthCharge(TrigBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["TurnStarts"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and ID == self.entity.ID
		
	def text(self, CHN):
		return "在你的回合开始时，对所有随从造成5点伤害" if CHN else "At the start of your turn, deal 5 damage to all minions"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		targets = self.entity.Game.minionsonBoard(self.entity.ID) + self.entity.Game.minionsonBoard(3-self.entity.ID)
		self.entity.dealsAOE(targets, [5 for minion in targets])
		
		
class HotAirBalloon(Minion):
	Class, race, name = "Neutral", "Mech", "Hot Air Balloon"
	mana, attack, health = 1, 1, 2
	index = "DRAGONS~Neutral~Minion~1~1~2~Mech~Hot Air Balloon"
	requireTarget, keyWord, description = False, "", "At the start of your turn, gain +1 Health"
	name_CN = "热气球"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_HotAirBalloon(self)]
		
class Trig_HotAirBalloon(TrigBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["TurnStarts"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and ID == self.entity.ID
		
	def text(self, CHN):
		return "在你的回合开始时，获得+1生命值" if CHN else "At the start of your turn, gain +1 Health"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.buffDebuff(0, 1)
		
"""Mana 2 cards"""
class EvasiveChimaera(Minion):
	Class, race, name = "Neutral", "Beast", "Evasive Chimaera"
	mana, attack, health = 2, 2, 1
	index = "DRAGONS~Neutral~Minion~2~2~1~Beast~Evasive Chimaera~Poisonous"
	requireTarget, keyWord, description = False, "Poisonous", "Poisonous. Can't be targeted by spells or Hero Powers"
	name_CN = "辟法奇美拉"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.marks["Evasive"] = True
		
		
class DragonBreeder(Minion):
	Class, race, name = "Neutral", "", "Dragon Breeder"
	mana, attack, health = 2, 2, 3
	index = "DRAGONS~Neutral~Minion~2~2~3~~Dragon Breeder~Battlecry"
	requireTarget, keyWord, description = True, "", "Battlecry: Choose a friendly Dragon. Add a copy of it to your hand"
	name_CN = "幼龙饲养员"
	def effCanTrig(self):
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
			self.Game.Hand_Deck.addCardtoHand(type(target), self.ID, byType=True)
		return target
		
		
class GrizzledWizard(Minion):
	Class, race, name = "Neutral", "", "Grizzled Wizard"
	mana, attack, health = 2, 3, 2
	index = "DRAGONS~Neutral~Minion~2~3~2~~Grizzled Wizard~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Swap Hero Powers with your opponent until next turn"
	name_CN = "灰发巫师"
	
	def swapHeroPowers(self):
		temp = self.Game.powers[1]
		self.Game.powers[1].disappears()
		self.Game.powers[2].disappears()
		self.Game.powers[1] = self.Game.powers[2]
		self.Game.powers[2] = temp
		self.Game.powers[1].appears()
		self.Game.powers[2].appears()
		self.Game.powers[1].ID, self.Game.powers[2].ID = 1, 2
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		#The Hero Powers are swapped at the start of your next turn
		GrizzledWizard.swapHeroPowers(self)
		trigs = self.Game.turnStartTrigger
		trigSwap = SwapHeroPowersBack(self.Game, self.ID)
		for i in reversed(range(len(trigs))):
			if isinstance(trigs[i], SwapHeroPowersBack):
				trigs.pop(i)
		trigs.append(trigSwap)
		return None
		
class SwapHeroPowersBack:
	def __init__(self, Game, ID):
		self.Game, self.ID = Game, ID
		
	def text(self, CHN):
		return "玩家%d的回合开始时，交换双方的英雄技能"%self.ID if CHN \
				else "At the start of player %d's turn, swap players' Hero Powers"%self.ID
				
	def turnStartTrigger(self):
		GrizzledWizard.swapHeroPowers(self)
		try: self.Game.turnStartTrigger.remove(self)
		except: pass
		
	def createCopy(self, game):
		return type(self)(game, self.ID)
		
		
class ParachuteBrigand(Minion):
	Class, race, name = "Neutral", "Pirate", "Parachute Brigand"
	mana, attack, health = 2, 2, 2
	index = "DRAGONS~Neutral~Minion~2~2~2~Pirate~Parachute Brigand"
	requireTarget, keyWord, description = False, "", "After you play a Pirate, summon this minion from your hand"
	name_CN = "空降歹徒"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsHand = [Trig_ParachuteBrigand(self)]
		
class Trig_ParachuteBrigand(TrigHand):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionBeenPlayed"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.inHand and subject.ID == self.entity.ID and "Pirate" in subject.race
		
	def text(self, CHN):
		return "在你使用一张海盗牌后，从你的手牌中召唤该随从" if CHN \
				else "After you play a Pirate, summon this minion from your hand"
				
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		minion = self.entity
		#不知道会召唤在最右边还是打出的海盗的右边。假设在最右边
		if minion.Game.space(minion.ID) > 0:
			try: minion.Game.summonfrom(minion.Game.Hand_Deck.hands[minion.ID].index(minion), minion.ID, -1, minion, fromHand=True)
			except: pass
			
			
class TastyFlyfish(Minion):
	Class, race, name = "Neutral", "Murloc", "Tasty Flyfish"
	mana, attack, health = 2, 2, 2
	index = "DRAGONS~Neutral~Minion~2~2~2~Murloc~Tasty Flyfish~Deathrattle"
	requireTarget, keyWord, description = False, "", "Deathrattle: Give a Dragon in your hand +2/+2"
	name_CN = "美味飞鱼"
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
			else:
				dragons = [i for i, card in enumerate(ownHand) if card.type == "Minion" and "Dragon" in card.race]
				i = npchoice(dragons) if dragons else -1
				curGame.fixedGuides.append(i)
			if i > 1:
				ownHand[i].buffDebuff(2, 2)
				
	def text(self, CHN):
		return "亡语：使你手牌中的一张发现获得+2/+2" if CHN else "Deathrattle: Give a random Dragon in your hand +2/+2"
		
#需要测试法术和随从的抽到时触发效果与这个孰先孰后。以及变形后的加拉克隆的效果触发。
#测试时阿兰纳斯蛛后不会触发其加血效果。场上同时有多个幻术师的时候，会依次发生多冷变形。https://www.bilibili.com/video/av79078930?from=search&seid=4964775667793261235
#源生宝典和远古谜团等卡牌抽到一张牌然后为期费用赋值等效果都会在变形效果生效之后进行赋值。
#与其他“每当你抽一张xx牌”的扳机（如狂野兽王）共同在场时，是按照登场的先后顺序（扳机的正常顺序结算）。
#不太清楚与阿鲁高如果结算，据说是阿鲁高始终都会复制初始随从。不考虑这个所谓特例的可能性
#抽到“抽到时施放”的法术时，不会触发其效果，直接变成传说随从，然后也不追加抽牌。
class Transmogrifier(Minion):
	Class, race, name = "Neutral", "", "Transmogrifier"
	mana, attack, health = 2, 2, 3
	index = "DRAGONS~Neutral~Minion~2~2~3~~Transmogrifier"
	requireTarget, keyWord, description = False, "", "Whenever you draw a card, transform it into a random Legendary minion"
	name_CN = "幻化师"
	poolIdentifier = "Legendary Minions"
	@classmethod
	def generatePool(cls, Game):
		return "Legendary Minions", list(Game.LegendaryMinions.values())
		
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_Transmogrifier(self)]
		
class Trig_Transmogrifier(TrigBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["CardDrawn"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and target[0].ID == self.entity.ID
		
	def text(self, CHN):
		return "每当你抽到一张牌时，随机将其变形成为一张传说随从牌" if CHN \
				else "Whenever you draw a card, transform it into a random Legendary minion"
				
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		curGame = self.entity.Game
		if curGame.mode == 0:
			if curGame.guides:
				minion = curGame.guides.pop(0)
			else:
				minion = npchoice(self.rngPool("Legendary Minions"))
				curGame.fixedGuides.append(minion)
			curGame.Hand_Deck.replaceCardDrawn(target, minion(curGame, self.entity.ID))
			
			
class WyrmrestPurifier(Minion):
	Class, race, name = "Neutral", "", "Wyrmrest Purifier"
	mana, attack, health = 2, 3, 2
	index = "DRAGONS~Neutral~Minion~2~3~2~~Wyrmrest Purifier~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Transform all Neutral cards in your deck into random cards from your class"
	name_CN = "龙眠净化者"
	poolIdentifier = "Druid Cards"
	@classmethod
	def generatePool(cls, Game):
		return [Class+" Cards" for Class in Game.Classes], [list(Game.ClassCards[Class].values()) for Class in Game.Classes]
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		ownDeck = curGame.Hand_Deck.decks[self.ID]
		neutralCards = [i for i, card in enumerate(ownDeck) if card.Class == "Neutral"]
		if neutralCards:
			if curGame.guides:
				newCards = curGame.guides.pop(0)
			else:
				#不知道如果我方英雄没有职业时，变形成的牌是否会是中立。假设会变形成为随机职业
				Class = curGame.heroes[self.ID].Class
				key = Class+" Cards" if Class != "Neutral" else "%s Cards"%npchoice(curGame.Classes)
				newCards = npchoice(self.rngPool(key), len(neutralCards), replace=True)
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
	index = "DRAGONS~Neutral~Minion~3~3~4~~Blowtorch Saboteur~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Your opponent's next Hero Power costs (3)"
	name_CN = "喷灯破坏者"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.Game.Manas.PowerAuras_Backup.append(GameManaAura_NextHeroPower3(self.Game, 3-self.ID))
		return None
		
class GameManaAura_NextHeroPower3(TempManaEffect_Power):
	def __init__(self, Game, ID, changeby=0, changeto=-1):
		self.blank_init(Game, ID, 0, 3)
		self.temporary = False
		
	def applicable(self, target):
		return target.ID == self.ID
		
		
class DreadRaven(Minion):
	Class, race, name = "Neutral", "Beast", "Dread Raven"
	mana, attack, health = 3, 3, 4
	index = "DRAGONS~Neutral~Minion~3~3~4~Beast~Dread Raven"
	requireTarget, keyWord, description = False, "", "Has +3 Attack for each other Dread Raven you control"
	name_CN = "恐惧渡鸦"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.auras["Has +3 Attack for each other Dread Raven you control"] = BuffAura_DreadRaven(self)
		
class BuffAura_DreadRaven(HasAura_toMinion):
	def __init__(self, entity):
		self.entity = entity
		self.signals, self.auraAffected = ["MinionAppears", "MinionDisappears"], []
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		obj = subject if signal == "MinionAppears" else target
		return self.entity.onBoard and obj.ID == self.entity.ID and obj.name == "Dread Raven" and obj != self.entity
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		for minion, receiver in self.auraAffected[:]:
			receiver.effectClear()
			
		self.applies(self.entity)
		
	def applies(self, subject):
		numDreadRavens = 0
		for minion in self.entity.Game.minionsonBoard(self.entity.ID):
			if minion.name == "Dread Raven" and minion != self.entity:
				numDreadRavens += 1
		if numDreadRavens > 0:
			Stat_Receiver(subject, self, 3 * numDreadRavens, 0).effectStart()
			
	def auraAppears(self):
		self.applies(self.entity)
		for sig in self.signals:
			try: self.entity.Game.trigsBoard[self.entity.ID][sig].append(self)
			except: self.entity.Game.trigsBoard[self.entity.ID][sig] = [self]
			
	def selfCopy(self, recipient): #The recipientMinion is the minion that deals the Aura.
		#func that checks if subject is applicable will be the new copy's function
		return type(self)(recipient)
	#可以通过HasAura_toMinion的createCopy方法复制
	
			
class FireHawk(Minion):
	Class, race, name = "Neutral", "Elemental", "Fire Hawk"
	mana, attack, health = 3, 1, 3
	index = "DRAGONS~Neutral~Minion~3~1~3~Elemental~Fire Hawk~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Gain +1 Attack for each card in your opponent's hand"
	name_CN = "火鹰"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.buffDebuff(len(self.Game.Hand_Deck.hands[3-self.ID]), 0)
		return None
		
		
class GoboglideTech(Minion):
	Class, race, name = "Neutral", "", "Goboglide Tech"
	mana, attack, health = 3, 3, 3
	index = "DRAGONS~Neutral~Minion~3~3~3~~Goboglide Tech~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: If you control a Mech, gain +1/+1 and Rush"
	name_CN = "地精滑翔技师"
	def effCanTrig(self):
		self.effectViable = any("Mech" in minion.race for minion in self.Game.minionsonBoard(self.ID))
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if any("Mech" in minion.race for minion in self.Game.minionsonBoard(self.ID)):
			self.buffDebuff(1, 1)
			self.getsKeyword("Rush")
		return None
		
		
class LivingDragonbreath(Minion):
	Class, race, name = "Neutral", "Elemental", "Living Dragonbreath"
	mana, attack, health = 3, 3, 4
	index = "DRAGONS~Neutral~Minion~3~3~4~Elemental~Living Dragonbreath"
	requireTarget, keyWord, description = False, "", "Your minions can't be Frozen"
	name_CN = "活化龙息"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.auras["Your minions can't be Frozen"] = GameRuleAura_LivingDragonbreath(self)
		
class GameRuleAura_LivingDragonbreath(GameRuleAura):
	def auraAppears(self):
		self.entity.Game.status[self.entity.ID]["Minions Can't Be Frozen"] += 1
		
	def auraDisappears(self):
		self.entity.Game.status[self.entity.ID]["Minions Can't Be Frozen"] -= 1
		
		
class Scalerider(Minion):
	Class, race, name = "Neutral", "", "Scalerider"
	mana, attack, health = 3, 3, 3
	index = "DRAGONS~Neutral~Minion~3~3~3~~Scalerider~Battlecry"
	requireTarget, keyWord, description = True, "", "Battlecry: If you're holding a Dragon, deal 2 damage"
	name_CN = "锐鳞骑士"
	
	def returnTrue(self, choice=0):
		return self.Game.Hand_Deck.holdingDragon(self.ID)
		
	def effCanTrig(self): #Friendly characters are always selectable.
		self.effectViable = self.Game.Hand_Deck.holdingDragon(self.ID)
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target and self.Game.Hand_Deck.holdingDragon(self.ID):
			self.dealsDamage(target, 2)
		return target
		
		
"""Mana 4 cards"""
class BadLuckAlbatross(Minion):
	Class, race, name = "Neutral", "Beast", "Bad Luck Albatross"
	mana, attack, health = 4, 4, 3
	index = "DRAGONS~Neutral~Minion~4~4~3~Beast~Bad Luck Albatross~Deathrattle"
	requireTarget, keyWord, description = False, "", "Deathrattle: Shuffle two 1/1 Albatross into your opponent's deck"
	name_CN = "厄运信天翁"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [ShuffleTwoAlbatrossintoOpponentsDeck(self)]
		
class ShuffleTwoAlbatrossintoOpponentsDeck(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		minion = self.entity
		minion.Game.Hand_Deck.shuffleintoDeck([Albatross(minion.Game, 3-minion.ID) for i in range(2)], creator=minion)
		
	def text(self, CHN):
		return "亡语：将两张1/1的信天翁洗入你对手的牌库" if CHN else "Deathrattle: Shuffle two 1/1 Albatross into your opponent's deck"
		
class Albatross(Minion):
	Class, race, name = "Neutral", "Beast", "Albatross"
	mana, attack, health = 1, 1, 1
	index = "DRAGONS~Neutral~Minion~1~1~1~Beast~Albatross~Uncollectible"
	requireTarget, keyWord, description = False, "", ""
	name_CN = "信天翁"
	
	
class DevotedManiac(Minion):
	Class, race, name = "Neutral", "", "Devoted Maniac"
	mana, attack, health = 4, 2, 2
	index = "DRAGONS~Neutral~Minion~4~2~2~~Devoted Maniac~Rush~Battlecry"
	requireTarget, keyWord, description = False, "Rush", "Rush. Battlecry: Invoke Galakrond"
	name_CN = "虔诚信徒"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		invokeGalakrond(self.Game, self.ID)
		return None
		
		
class DragonmawPoacher(Minion):
	Class, race, name = "Neutral", "", "Dragonmaw Poacher"
	mana, attack, health = 4, 4, 4
	index = "DRAGONS~Neutral~Minion~4~4~4~~Dragonmaw Poacher~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: If your opponent controls a Dragon, gain +4/+4 and Rush"
	name_CN = "龙喉偷猎者"
	
	def effCanTrig(self):
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
			self.buffDebuff(4, 4)
			self.getsKeyword("Rush")
		return None
		
		
class EvasiveFeywing(Minion):
	Class, race, name = "Neutral", "Dragon", "Evasive Feywing"
	mana, attack, health = 4, 5, 4
	index = "DRAGONS~Neutral~Minion~4~5~4~Dragon~Evasive Feywing"
	requireTarget, keyWord, description = False, "", "Can't be targeted by spells or Hero Powers"
	name_CN = "辟法灵龙"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.marks["Evasive"] = 1
		
		
class FrizzKindleroost(Minion):
	Class, race, name = "Neutral", "", "Frizz Kindleroost"
	mana, attack, health = 4, 5, 4
	index = "DRAGONS~Neutral~Minion~4~5~4~~Frizz Kindleroost~Battlecry~Legendary"
	requireTarget, keyWord, description = False, "", "Battlecry: Reduce the Cost of Dragons in your deck by (2)"
	name_CN = "弗瑞兹光巢"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		for card in self.Game.Hand_Deck.decks[self.ID]:
			if card.type == "Minion" and "Dragon" in card.race:
				ManaMod(card, changeby=-2, changeto=-1).applies()
		return None
		
		
class Hippogryph(Minion):
	Class, race, name = "Neutral", "Beast", "Hippogryph"
	mana, attack, health = 4, 2, 6
	index = "DRAGONS~Neutral~Minion~4~2~6~Beast~Hippogryph~Rush~Taunt"
	requireTarget, keyWord, description = False, "Rush,Taunt", "Rush, Taunt"
	name_CN = "角鹰兽"
	
	
class HoardPillager(Minion):
	Class, race, name = "Neutral", "Pirate", "Hoard Pillager"
	mana, attack, health = 4, 4, 2
	index = "DRAGONS~Neutral~Minion~4~4~2~Pirate~Hoard Pillager~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Equip one of your destroyed weapons"
	name_CN = "藏宝匪贼"
	def effCanTrig(self):
		self.effectViable = self.Game.Counters.weaponsDestroyedThisGame[self.ID] != []
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if curGame.mode == 0:
			if curGame.guides:
				weapon = curGame.guides.pop(0)
			else:
				weapons = curGame.Counters.weaponsDestroyedThisGame[self.ID]
				weapon = curGame.cardPool[npchoice(weapons)] if weapons else None
				curGame.fixedGuides.append(weapon)
			if weapon: curGame.equipWeapon(weapon(curGame, self.ID))
		return None
		
		
class TrollBatrider(Minion):
	Class, race, name = "Neutral", "", "Troll Batrider"
	mana, attack, health = 4, 3, 3
	index = "DRAGONS~Neutral~Minion~4~3~3~~Troll Batrider~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Deal 3 damage to a random enemy minion"
	name_CN = "巨魔蝙蝠骑士"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if curGame.mode == 0:
			if curGame.guides:
				i = curGame.guides.pop(0)
			else:
				minions = curGame.minionsAlive(3-self.ID)
				i = npchoice(minions).pos if minions else -1
				curGame.fixedGuides.append(i)
			if i > -1: self.dealsDamage(curGame.minions[3-self.ID][i], 3)
		return None
		
		
class WingCommander(Minion):
	Class, race, name = "Neutral", "", "Wing Commander"
	mana, attack, health = 4, 2, 5
	index = "DRAGONS~Neutral~Minion~4~2~5~~Wing Commander"
	requireTarget, keyWord, description = False, "", "Has +2 Attack for each Dragon in your hand"
	name_CN = "空军指挥官"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.auras["Has +2 Attack for each Dragon in your hand"] = BuffAura_WingCommander(self)
		
class BuffAura_WingCommander(HasAura_toMinion):
	def __init__(self, entity):
		self.entity = entity
		self.signals, self.auraAffected = ["CardLeavesHand", "CardEntersHand"], []

	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		card = target[0] if signal == "CardEntersHand" else target
		return self.entity.onBoard and card.ID == self.entity.ID and card.type == "Minion" and "Dragon" in card.race

	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		for minion, receiver in self.auraAffected[:]:
			receiver.effectClear()

		self.applies(self.entity)

	def applies(self, subject):
		numDragonsinHand = 0
		for card in self.entity.Game.minionsonBoard(self.entity.ID):
			if card.type == "Minion" and "Dragon" in card.race:
				numDragonsinHand += 1

		if numDragonsinHand > 0:
			Stat_Receiver(subject, self, 2 * numDragonsinHand, 0).effectStart()

	def auraAppears(self):
		self.applies(self.entity)
		for sig in self.signals:
			try: self.entity.Game.trigsBoard[self.entity.ID][sig].append(self)
			except: self.entity.Game.trigsBoard[self.entity.ID][sig] = [self]

	def selfCopy(self, recipient):  # The recipientMinion is the minion that deals the Aura.
		# func that checks if subject is applicable will be the new copy's function
		return type(self)(recipient)
		#可以通过HasAura_toMinion的createCopy方法复制


class ZulDrakRitualist(Minion):
	Class, race, name = "Neutral", "", "Zul'Drak Ritualist"
	mana, attack, health = 4, 3, 9
	index = "DRAGONS~Neutral~Minion~4~3~9~~Zul'Drak Ritualist~Taunt~Battlecry"
	requireTarget, keyWord, description = False, "Taunt", "Taunt. Battlecry: Summon three random 1-Cost minions for your opponent"
	name_CN = "祖达克仪祭师"
	poolIdentifier = "1-Cost Minions to Summon"
	@classmethod
	def generatePool(cls, Game):
		return "1-Cost Minion to Summon", list(Game.MinionsofCost[1].values())
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if curGame.mode == 0:
			if curGame.guides:
				minions = curGame.guides.pop(0)
			else:
				minions = npchoice(self.rngPool("1-Cost Minions to Summon"), 3, replace=True)
				curGame.fixedGuides.append(tuple(minions))
			curGame.summon([minion(curGame, 3-self.ID) for minion in minions], (-1, "totheRightEnd"), self)
		return None
		
		
"""Mana 5 cards"""
class BigOlWhelp(Minion):
	Class, race, name = "Neutral", "Dragon", "Big Ol' Whelp"
	mana, attack, health = 5, 5, 5
	index = "DRAGONS~Neutral~Minion~5~5~5~Dragon~Big Ol' Whelp~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Draw a card"
	name_CN = "雏龙巨婴"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.Game.Hand_Deck.drawCard(self.ID)
		return None
		
		
class ChromaticEgg(Minion):
	Class, race, name = "Neutral", "", "Chromatic Egg"
	mana, attack, health = 5, 0, 3
	index = "DRAGONS~Neutral~Minion~5~0~3~~Chromatic Egg~Battlecry~Deathrattle"
	requireTarget, keyWord, description = False, "", "Battlecry: Secretly Discover a Dragon to hatch into. Deathrattle: Hatch!"
	name_CN = "多彩龙蛋"
	poolIdentifier = "Dragons as Druid to Summon"
	@classmethod
	def generatePool(cls, Game):
		classCards = {s : [] for s in Game.ClassesandNeutral}
		for key, value in Game.MinionswithRace["Dragon"].items():
			for Class in key.split('~')[1].split(','):
				classCards[Class].append(value)
		return ["Dragons as %s to Summon"+Class for Class in Game.Classes], \
				[classCards[Class]+classCards["Neutral"] for Class in Game.Classes]
				
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [HatchintotheChosenDragon(self)]
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if self.ID == curGame.turn:
			if curGame.mode == 0:
				if curGame.guides:
					dragon = curGame.guides.pop(0)
					for trig in self.deathrattles:
						if isinstance(trig, HatchintotheChosenDragon):
							trig.dragonInside = dragon
				else:
					key = "Dragons as %s to Summon"%classforDiscover(self)
					if "byOthers" in comment:
						dragon = npchoice(self.rngPool(key))
						curGame.fixedGuides.append(dragon)
						for trig in self.deathrattles:
							if isinstance(trig, HatchintotheChosenDragon):
								trig.dragonInside = dragon
					else:
						dragons = npchoice(self.rngPool(key), 3, replace=False)
						curGame.options = [dragon(curGame, self.ID) for dragon in dragons]
						curGame.Discover.startDiscover(self)
		return None
		
	def discoverDecided(self, option, pool):
		self.Game.fixedGuides.append(type(option))
		for trig in self.deathrattles:
			if isinstance(trig, HatchintotheChosenDragon):
				trig.dragonInside = type(option)
				
class HatchintotheChosenDragon(Deathrattle_Minion):
	def __init__(self, entity):
		self.blank_init(entity)
		self.dragonInside = None #This is a class
		
	def text(self, CHN):
		if self.dragonInside:
			return "亡语：孵化为一个巨龙" if CHN else "Deathrattle: Hatch"
		else:
			return "空蛋！" if CHN else "Empty egg!"
	#变形亡语只能触发一次。
	def trig(self, signal, ID, subject, target, number, comment, choice=0):
		if self.canTrig(signal, ID, subject, target, number, comment):
			if self.dragonInside:
				if self.entity.Game.GUI:
					self.entity.Game.GUI.deathrattleAni(self.entity)
				self.entity.Game.transform(self.entity, self.dragonInside(self.entity.Game, self.entity.ID))
				
	def selfCopy(self, recipient):
		trig = type(self)(recipient)
		trig.dragonInside = self.dragonInside
		return trig
		
		
class CobaltSpellkin(Minion):
	Class, race, name = "Neutral", "Dragon", "Cobalt Spellkin"
	mana, attack, health = 5, 3, 5
	index = "DRAGONS~Neutral~Minion~5~3~5~Dragon~Cobalt Spellkin~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Add two 1-Cost spells from your class to your hand"
	name_CN = "深蓝系咒师"
	poolIdentifier = "1-Cost Spells as Druid"
	@classmethod
	def generatePool(cls, Game):
		return ["1-Cost Spells as %s"%Class for Class in Game.Classes], \
				[[value for key, value in Game.ClassCards[Class].items() if "~Spell~" in key and key.split('~')[3] == '1'] for Class in Game.Classes]
				
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if curGame.mode == 0:
			if curGame.guides:
				spells = list(curGame.guides.pop(0))
			else:
				key = "1-Cost Spells as "+self.Game.heroes[self.ID].Class
				spells = npchoice(self.rngPool(key), 2, replace=False)
				curGame.fixedGuides.append(tuple(spells))
			curGame.Hand_Deck.addCardtoHand(spells, self.ID, byType=True)
		return None
		
		
class FacelessCorruptor(Minion):
	Class, race, name = "Neutral", "", "Faceless Corruptor"
	mana, attack, health = 5, 4, 4
	index = "DRAGONS~Neutral~Minion~5~4~4~~Faceless Corruptor~Rush~Battlecry"
	requireTarget, keyWord, description = True, "Rush", "Rush. Battlecry: Transform one of your friendly minions into a copy of this"
	name_CN = "无面腐蚀者"
	
	def targetExists(self, choice=0):
		return self.selectableFriendlyMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.ID == self.ID and target != self and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			Copy = self.selfCopy(self.ID, self) if self.onBoard or self.inHand else type(self)(self.Game, self.ID)
			self.Game.transform(target, Copy)
			return Copy
		return None
		
		
class KoboldStickyfinger(Minion):
	Class, race, name = "Neutral", "Pirate", "Kobold Stickyfinger"
	mana, attack, health = 5, 4, 4
	index = "DRAGONS~Neutral~Minion~5~4~4~Pirate~Kobold Stickyfinger~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Steal your opponent's weapon"
	name_CN = "黏指狗头人"
	
	def effCanTrig(self):
		self.effectViable = self.Game.availableWeapon(3-self.ID)
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		weapon = self.Game.availableWeapon(3-self.ID)
		if weapon:
			weapon.disappears()
			try: self.Game.weapons[3-self.ID].remove(weapon)
			except: pass
			weapon.ID = self.ID
			self.Game.equipWeapon(weapon)
		return None
		
	
class Platebreaker(Minion):
	Class, race, name = "Neutral", "", "Platebreaker"
	mana, attack, health = 5, 5, 5
	index = "DRAGONS~Neutral~Minion~5~5~5~~Platebreaker~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Destroy your opponent's Armor"
	name_CN = "破甲骑士"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.Game.heroes[3-self.ID].armor = 0
		return None
		
		
class ShieldofGalakrond(Minion):
	Class, race, name = "Neutral", "", "Shield of Galakrond"
	mana, attack, health = 5, 4, 5
	index = "DRAGONS~Neutral~Minion~5~4~5~~Shield of Galakrond~Taunt~Battlecry"
	requireTarget, keyWord, description = False, "Taunt", "Taunt. Battlecry: Invoke Galakrond"
	name_CN = "迦拉克隆之盾"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		invokeGalakrond(self.Game, self.ID)
		return None
		
		
class Skyfin(Minion):
	Class, race, name = "Neutral", "Murloc", "Skyfin"
	mana, attack, health = 5, 3, 3
	index = "DRAGONS~Neutral~Minion~5~3~3~Murloc~Skyfin~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: If you're holding a Dragon, summon 2 random Murlocs"
	name_CN = "飞天鱼人"
	poolIdentifier = "Murlocs to Summon"
	@classmethod
	def generatePool(cls, Game):
		return "Murlocs to Summon", list(Game.MinionswithRace["Murloc"].values())
		
	def effCanTrig(self):
		self.effectViable = self.Game.Hand_Deck.holdingDragon(self.ID)
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if curGame.Hand_Deck.holdingDragon(self.ID):
			if curGame.mode == 0:
				if curGame.guides:
					murlocs = curGame.guides.pop(0)
				else:
					murlocs = npchoice(self.rngPool("Murlocs to Summon"), 2, replace=False)
					curGame.fixedGuides.append(tuple(murlocs))
				pos = (self.pos, "leftandRight") if self.onBoard else (-1, "totheRightEnd")
				curGame.summon([murloc(curGame, self.ID) for murloc in murlocs], pos, self)
		return None
		
		
class TentacledMenace(Minion):
	Class, race, name = "Neutral", "", "Tentacled Menace"
	mana, attack, health = 5, 6, 5
	index = "DRAGONS~Neutral~Minion~5~6~5~~Tentacled Menace~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Each player draws a card. Swap their Costs"
	name_CN = "触手恐吓者"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		card1, mana = self.Game.Hand_Deck.drawCard(self.ID)
		card2, mana = self.Game.Hand_Deck.drawCard(3-self.ID)
		if card1 and card2:
			mana1, mana2 = card1.mana, card2.mana
			ManaMod(card1, changeby=0, changeto=mana2).applies()
			ManaMod(card2, changeby=0, changeto=mana1).applies()
			self.Game.Manas.calcMana_Single(card1)
			self.Game.Manas.calcMana_Single(card2)
		return None
		
		
"""Mana 6 cards"""
class CamouflagedDirigible(Minion):
	Class, race, name = "Neutral", "Mech", "Camouflaged Dirigible"
	mana, attack, health = 6, 6, 6
	index = "DRAGONS~Neutral~Minion~6~6~6~Mech~Camouflaged Dirigible~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Give your other Mechs Stealth until your next turn"
	name_CN = "迷彩飞艇"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		for minion in self.Game.minionsonBoard(self.ID):
			if "Mech" in minion.race: minion.status["Temp Stealth"] += 1
		return None
		
		
class EvasiveWyrm(Minion):
	Class, race, name = "Neutral", "Dragon", "Evasive Wyrm"
	mana, attack, health = 6, 5, 3
	index = "DRAGONS~Neutral~Minion~6~5~3~Dragon~Evasive Wyrm~Divine Shield~Rush"
	requireTarget, keyWord, description = False, "Divine Shield,Rush", "Divine Shield, Rush. Can't be targeted by spells or Hero Powers"
	name_CN = "辟法巨龙"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.marks["Evasive"] = 1
		
		
class Gyrocopter(Minion):
	Class, race, name = "Neutral", "Mech", "Gyrocopter"
	mana, attack, health = 6, 4, 5
	index = "DRAGONS~Neutral~Minion~6~4~5~Mech~Gyrocopter~Rush~Windfury"
	requireTarget, keyWord, description = False, "Rush,Windfury", "Rush, Windfury"
	name_CN = "旋翼机"
	
	
class KronxDragonhoof(Minion):
	Class, race, name = "Neutral", "", "Kronx Dragonhoof"
	mana, attack, health = 6, 6, 6
	index = "DRAGONS~Neutral~Minion~6~6~6~~Kronx Dragonhoof~Battlecry~Legendary"
	requireTarget, keyWord, description = False, "", "Battlecry: Draw Galakrond. If you're alread Galakrond, unleash a Devastation"
	name_CN = "克罗斯龙蹄"
	
	def effCanTrig(self):
		self.effectViable =  "Galakrond" in self.Game.heroes[self.ID].name
	#迦拉克隆有主迦拉克隆机制，祈求时只有主迦拉克隆会响应
	#主迦拉克隆会尽量与玩家职业匹配，如果不能匹配，则系统检测到的第一张迦拉克隆会被触发技能
	#http://nga.178.com/read.php?tid=19587242&rand=356
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if not curGame.heroes[self.ID].name.startswith("Galakrond"):
			galakrond = None
			for card in curGame.Hand_Deck.decks[self.ID]:
				if card.name.startswith("Galakrond, "):
					galakrond = card
					break
			if galakrond: curGame.Hand_Deck.drawCard(self.ID, galakrond)
		else:
			if self.ID == curGame.turn:
				if curGame.mode == 0:
					if curGame.guides:
						self.discoverDecided(curGame.guides.pop(0)(), None)
					else:
						if "byOthers" in comment:
							effect = npchoice([Annihilation, Decimation, Domination, Reanimation])
							curGame.fixedGuides.append(effect)
							self.discoverDecided(effect(), None)
						else:
							curGame.options = [Annihilation(), Decimation(), Domination(), Reanimation()]
							curGame.Discover.startDiscover(self)
		return None
		
	def discoverDecided(self, option, pool):
		curGame = self.Game
		curGame.fixedGuides.append(type(option))
		if option.name == "Annihilation":
			targets = curGame.minionsonBoard(self.ID, self) + curGame.minionsonBoard(3-self.ID)
			if targets: self.dealsAOE(targets, [5 for minion in targets])
		elif option.name == "Decimation":
			heal = 5 * (2 ** self.countHealDouble())
			self.dealsDamage(curGame.heroes[3-self.ID], 5)
			self.restoresHealth(curGame.heroes[self.ID], heal)
		elif option.name == "Domination":
			targets = curGame.minionsonBoard(self.ID, self)
			for minion in targets: minion.buffDebuff(2, 2)
		else:
			curGame.summon(ReanimatedDragon(curGame, self.ID), self.pos+1, self)
			
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
	index = "DRAGONS~Neutral~Minion~8~8~8~Dragon~Reanimated Dragon~Uncollectible"
	requireTarget, keyWord, description = False, "", ""
	name_CN = "重生的巨龙"
	
	
class UtgardeGrapplesniper(Minion):
	Class, race, name = "Neutral", "", "Utgarde Grapplesniper"
	mana, attack, health = 6, 5, 5
	index = "DRAGONS~Neutral~Minion~6~5~5~~Utgarde Grapplesniper~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Both players draw a card. If it's a Dragon, summon it"
	name_CN = "乌特加德 鱼叉射手"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		card1 = curGame.Hand_Deck.drawCard(self.ID)[0]
		card2 = curGame.Hand_Deck.drawCard(3-self.ID)[0]
		hands = curGame.Hand_Deck.hands
		if card1 and card1.type == "Minion" and "Dragon" in card1.race and card1 in hands[self.ID]:
			curGame.summonfrom(hands[self.ID].index(card1), self.ID, -1, self, fromHand=True) #不知道我方随从是会召唤到这个随从的右边还是场上最右边。
		if card2 and card2.type == "Minion" and "Dragon" in card2.race and card2 in hands[3-self.ID]:
			curGame.summonfrom(hands[3-self.ID].index(card2), 3-self.ID, -1, self, fromHand=True)
		return None
		
"""Mana 7 cards"""
class EvasiveDrakonid(Minion):
	Class, race, name = "Neutral", "Dragon", "Evasive Drakonid"
	mana, attack, health = 7, 7, 7
	index = "DRAGONS~Neutral~Minion~7~7~7~Dragon~Evasive Drakonid~Taunt"
	requireTarget, keyWord, description = False, "Taunt", "Taunt. Can't be targeted by spells or Hero Powers"
	name_CN = "辟法龙人"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.marks["Evasive"] = 1
		
		
class Shuma(Minion):
	Class, race, name = "Neutral", "", "Shu'ma"
	mana, attack, health = 7, 1, 7
	index = "DRAGONS~Neutral~Minion~7~1~7~~Shu'ma~Legendary"
	requireTarget, keyWord, description = False, "", "At the end of your turn, fill your board with 1/1 Tentacles"
	name_CN = "舒玛"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_Shuma(self)]
		
class Trig_Shuma(TrigBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["TurnEnds"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and ID == self.entity.ID
		
	def text(self, CHN):
		return "在你的回合结束时，召唤数条1/1的触手，直到你的随从数量达到上限" if CHN \
				else "At the end of your turn, fill your board with 1/1 Tentacles"
				
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.Game.summon([Tentacle_Dragons(self.entity.Game, self.entity.ID) for i in range(6)], (self.entity.pos, "leftandRight"), self.entity)
		
class Tentacle_Dragons(Minion):
	Class, race, name = "Neutral", "", "Tentacle"
	mana, attack, health = 1, 1, 1
	index = "DRAGONS~Neutral~Minion~1~1~1~~Tentacle~Uncollectible"
	requireTarget, keyWord, description = False, "", ""
	name_CN = "触手"
	
"""Mana 8 cards"""
class TwinTyrant(Minion):
	Class, race, name = "Neutral", "Dragon", "Twin Tyrant"
	mana, attack, health = 8, 4, 10
	index = "DRAGONS~Neutral~Minion~8~4~10~Dragon~Twin Tyrant~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Deal 4 damage to two random enemy minions"
	name_CN = "双头暴虐龙"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		minions = curGame.minionsAlive(3-self.ID)
		if minions:
			if curGame.mode == 0:
				if curGame.guides:
					targets = [curGame.minions[3-self.ID][i] for i in curGame.guides.pop(0)]
				else:
					targets = list(npchoice(minions, min(2, len(minions)), replace=False))
					curGame.fixedGuides.append(tuple([minion.pos for minion in targets]))
				self.dealsAOE(targets, [4]*len(targets))
		return None
		
"""Mana 9 cards"""
class DragonqueenAlexstrasza(Minion):
	Class, race, name = "Neutral", "Dragon", "Dragonqueen Alexstrasza"
	mana, attack, health = 9, 8, 8
	index = "DRAGONS~Neutral~Minion~9~8~8~Dragon~Dragonqueen Alexstrasza~Battlecry~Legendary"
	requireTarget, keyWord, description = False, "", "Battlecry: If your deck has no duplicates, add two Dragons to your hand. They cost (1)"
	name_CN = "红龙女王 阿莱克丝塔萨"
	poolIdentifier = "Dragons except Dragonqueen Alexstrasza"
	@classmethod
	def generatePool(cls, Game):
		dragons = list(Game.MinionswithRace["Dragon"].values())
		dragons.remove(DragonqueenAlexstrasza)
		return "Dragons except Dragonqueen Alexstrasza", dragons
		
	def effCanTrig(self):
		self.effectViable = self.Game.Hand_Deck.noDuplicatesinDeck(self.ID)
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if curGame.Hand_Deck.noDuplicatesinDeck(self.ID):
			if curGame.mode == 0:
				if curGame.guides:
					dragon1, dragon2 = curGame.guides.pop(0)
				else:
					dragon1, dragon2 = npchoice(self.rngPool("Dragons except Dragonqueen Alexstrasza"), 2, replace=False)
					curGame.fixedGuides.append(tuple((dragon1, dragon2)))
				dragon1, dragon2 = dragon1(curGame, self.ID), dragon2(curGame, self.ID)
				curGame.Hand_Deck.addCardtoHand([dragon1, dragon2], self.ID)
				if dragon1.inHand:
					ManaMod(dragon1, changeby=0, changeto=1).applies()
					curGame.Manas.calcMana_Single(dragon1)
				if dragon2.inHand:
					ManaMod(dragon2, changeby=0, changeto=1).applies()
					curGame.Manas.calcMana_Single(dragon2)
		return None
		
		
class Sathrovarr(Minion):
	Class, race, name = "Neutral", "Demon", "Sathrovarr"
	mana, attack, health = 9, 5, 5
	index = "DRAGONS~Neutral~Minion~9~5~5~Demon~Sathrovarr~Battlecry~Legendary"
	requireTarget, keyWord, description = True, "", "Battlecry: Choose a friendly minion. Add a copy of it to your hand, deck and battlefield"
	name_CN = "萨索瓦尔"
	
	def targetExists(self, choice=0):
		return self.selectableFriendlyMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.ID == self.ID and target != self and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			self.Game.Hand_Deck.addCardtoHand(type(target), self.ID, byType=True)
			#不知道这个加入牌库是否算作洗入牌库，从而可以触发强能雷象等扳机
			self.Game.Hand_Deck.shuffleintoDeck(type(target)(self.Game, self.ID), creator=self)
			#不知道这个召唤的复制是会出现在这个随从右边还是目标随从右边
			Copy = target.selfCopy(self.ID, self) if target.onBoard else type(target)(self.Game, self.ID)
			self.Game.summon(Copy, self.pos+1, self)
		return target
		
"""Druid cards"""
class Embiggen(Spell):
	Class, school, name = "Druid", "Nature", "Embiggen"
	requireTarget, mana = False, 0
	index = "DRAGONS~Druid~Spell~0~Nature~Embiggen"
	description = "Give all minions in your deck +2/+2. They cost (1) more (up to 10)"
	name_CN = "森然巨化"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		for card in self.Game.Hand_Deck.decks[self.ID]:
			if card.type == "Minion":
				card.attack += 2
				card.health += 2
				card.health_max += 2 #By default, this healthGain has to be non-negative.
				card.attack_Enchant += 2
				if card.mana < 10:
					ManaMod(card, changeby=+1, changeto=-1).applies()
		return None
		
		
class SecuretheDeck(Quest):
	Class, school, name = "Druid", "", "Secure the Deck"
	requireTarget, mana = False, 1
	index = "DRAGONS~Druid~Spell~1~Secure the Deck~~Quest"
	description = "Sidequest: Attack twice with your hero. Reward: Add 3 'Claw' to your hand"
	name_CN = "保护甲板"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_SecuretheDeck(self)]
		
class Trig_SecuretheDeck(QuestTrigger):
	def __init__(self, entity):
		self.blank_init(entity, ["HeroAttackedHero", "HeroAttackedMinion"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject == self.entity.Game.heroes[self.entity.ID]
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.counter += 1
		if self.entity.progress > 1:
			self.disconnect()
			try: self.entity.Game.Secrets.sideQuests[self.entity.ID].remove(self.entity)
			except: pass
			self.entity.Game.Hand_Deck.addCardtoHand([Claw, Claw, Claw], self.entity.ID, byType=True)
			
			
class StrengthinNumbers(Quest):
	Class, school, name = "Druid", "", "Strength in Numbers"
	requireTarget, mana = False, 1
	index = "DRAGONS~Druid~Spell~1~Strength in Numbers~~Quest"
	description = "Sidequest: Spend 10 Mana on minions. Rewards: Summon a minion from your deck"
	name_CN = "人多势众"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_StrengthinNumbers(self)]
		
class Trig_StrengthinNumbers(QuestTrigger):
	def __init__(self, entity): #假设人多势众是使用后扳机
		self.blank_init(entity, ["MinionBeenPlayed"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject.ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		quest = self.entity
		curGame = quest.Game
		self.counter += number
		if self.counter > 9:
			self.disconnect()
			try: quest.Game.Secrets.sideQuests[quest.ID].remove(quest)
			except: pass
			if curGame.mode == 0:
				if curGame.guides:
					i = curGame.guides.pop(0)
				else:
					minions = [i for i, card in enumerate(curGame.Hand_Deck.decks[quest.ID]) if card.type == "Minion"]
					i = npchoice(minions) if minions and curGame.space(quest.ID) > 0 else -1
					curGame.fixedGuides.append(i)
				if i > -1: curGame.summonfrom(i, quest.ID, -1, quest, fromHand=False)
				
				
class Treenforcements(Spell):
	Class, school, name = "Druid", "Nature", "Treenforcements"
	requireTarget, mana = True, 1
	index = "DRAGONS~Druid~Spell~1~Nature~Treenforcements~Choose One"
	description = "Choose One - Give a minion +2 Health and Taunt; or Summon a 2/2 Taunt"
	name_CN = "树木增援"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.options = [SmallRepairs_Option(self), SpinemUp_Option(self)]
		
	def need2Choose(self):
		return True
		
	def returnTrue(self, choice=0):
		return choice < 1
		
	def available(self):
		#当场上有全选光环时，变成了一个指向性法术，必须要有一个目标可以施放。
		if self.Game.status[self.ID]["Choose Both"] > 0:
			return self.selectableMinionExists()
		else: #Deal 2 AOE damage.
			return self.selectableMinionExists() or self.Game.space(self.ID) > 0
			
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if choice < 1:
			if target:
				target.buffDebuff(0, 2)
				target.getsKeyword("Taunt")
		if choice != 0:
			self.Game.summon(Treant_Dragons(self.Game, self.ID), -1, self)
		return target
		
class SmallRepairs_Option(ChooseOneOption):
	name, description = "Small Repairs", "Give a minion +2 Health and Taunt"
	index = "DRAGONS~Druid~Spell~1~Nature~Small Repairs~Uncollectible"
	def available(self):
		return self.entity.selectableMinionExists(0)
		
class SpinemUp_Option(ChooseOneOption):
	name, description = "Spin 'em Up", "Summon a Treant"
	index = "DRAGONS~Druid~Spell~1~Nature~Spin'em Up~Uncollectible"
	def available(self):
		return self.entity.Game.space(self.entity.ID)
		
class SmallRepairs(Spell):
	Class, school, name = "Druid", "Nature", "Small Repairs"
	requireTarget, mana = True, 1
	index = "DRAGONS~Druid~Spell~1~Nature~Small Repairs~Uncollectible"
	description = "Give a minion +2 Health and Taunt"
	name_CN = "简单维修"
	def available(self):
		return self.selectableMinionExists(0)
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			target.buffDebuff(0, 2)
			target.getsKeyword("Taunt")
		return target
		
class SpinemUp(Spell):
	Class, school, name = "Druid", "Nature", "Spin 'em Up"
	requireTarget, mana = False, 1
	index = "DRAGONS~Druid~Spell~1~Nature~Spin 'em Up~Uncollectible"
	description = "Summon a 2/2 Treant"
	name_CN = "旋叶起飞"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.Game.summon(Treant_Dragons(self.Game, self.ID), -1, self)
		return None
		
		
class BreathofDreams(Spell):
	Class, school, name = "Druid", "Nature", "Breath of Dreams"
	requireTarget, mana = False, 2
	index = "DRAGONS~Druid~Spell~2~Nature~Breath of Dreams"
	description = "Draw a card. If you're holding a Dragon, gain an empty Mana Crystal"
	name_CN = "梦境吐息"
	def effCanTrig(self):
		self.effectViable = self.Game.Hand_Deck.holdingDragon(self.ID)
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.Game.Hand_Deck.drawCard(self.ID)
		if self.Game.Hand_Deck.holdingDragon(self.ID):
			self.Game.Manas.gainEmptyManaCrystal(1, self.ID)
		return None
		
		
class Shrubadier(Minion):
	Class, race, name = "Druid", "", "Shrubadier"
	mana, attack, health = 2, 1, 1
	index = "DRAGONS~Druid~Minion~2~1~1~~Shrubadier~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Summon a 2/2 Treant"
	name_CN = "盆栽投手"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.Game.summon(Treant_Dragons(self.Game, self.ID), -1, self)
		return None
		
class Treant_Dragons(Minion):
	Class, race, name = "Druid", "", "Treant"
	mana, attack, health = 2, 2, 2
	index = "DRAGONS~Druid~Minion~2~2~2~~Treant~Uncollectible"
	requireTarget, keyWord, description = False, "", ""
	name_CN = "树人"
	
	
class Aeroponics(Spell):
	Class, school, name = "Druid", "Nature", "Aeroponics"
	requireTarget, mana = False, 5
	index = "DRAGONS~Druid~Spell~5~Nature~Aeroponics"
	description = "Draw 2 cards. Costs (2) less for each Treant you control"
	name_CN = "空气栽培"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsHand = [Trig_Aeroponics(self)]
		
	def selfManaChange(self):
		if self.inHand:
			numTreants = 0
			for minion in self.Game.minionsonBoard(self.ID):
				if minion.name == "Treant":
					numTreants += 1
					
			self.mana -= 2 * numTreants
			self.mana = max(0, self.mana)
			
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.Game.Hand_Deck.drawCard(self.ID)
		self.Game.Hand_Deck.drawCard(self.ID)
		return None
		
class Trig_Aeroponics(TrigHand):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionAppears", "MinionDisappears"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.inHand and ((signal[6] == 'A' and subject.name == "Treant") \
										or (signal[6] == 'D' and target.name == "Treant"))
										
	def text(self, CHN):
		return "每当一个友方树人出现或离场，重新计算费用" if CHN else "Whenever a fiendly Treant appears/disappears, recalculate the cost"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.Game.Manas.calcMana_Single(self.entity)
		
		
class EmeraldExplorer(Minion):
	Class, race, name = "Druid", "Dragon", "Emerald Explorer"
	mana, attack, health = 6, 4, 8
	index = "DRAGONS~Druid~Minion~6~4~8~Dragon~Emerald Explorer~Taunt~Battlecry"
	requireTarget, keyWord, description = False, "Taunt", "Taunt. Battlecry: Discover a Dragon"
	name_CN = "翡翠龙探险者"
	poolIdentifier = "Dragons as Druid"
	@classmethod
	def generatePool(cls, Game):
		classCards = {s : [] for s in Game.ClassesandNeutral}
		for key, value in Game.MinionswithRace["Dragon"].items():
			classCards[key.split('~')[1]].append(value)
		return ["Dragons as "+Class for Class in Game.Classes], \
				[classCards[Class]+classCards["Neutral"] for Class in Game.Classes]
				
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if self.ID == curGame.turn:
			if curGame.mode == 0:
				if curGame.guides:
					curGame.Hand_Deck.addCardtoHand(curGame.guides.pop(0), self.ID, byType=True, byDiscover=True)
				else:
					key = "Dragons as "+classforDiscover(self)
					if "byOthers" in comment:
						dragon = npchoice(self.rngPool(key))
						curGame.fixedGuides.append(dragon)
						curGame.Hand_Deck.addCardtoHand(dragon, self.ID, byType=True, byDiscover=True)
					else:
						dragons = npchoice(self.rngPool(key), 3, replace=False)
						curGame.options = [dragon(curGame, self.ID) for dragon in dragons]
						curGame.Discover.startDiscover(self)
		return None
		
		
	def discoverDecided(self, option, pool):
		self.Game.fixedGuides.append(type(option))
		self.Game.Hand_Deck.addCardtoHand(option, self.ID, byDiscover=True)
		
		
class GorutheMightree(Minion):
	Class, race, name = "Druid", "", "Goru the Mightree"
	mana, attack, health = 7, 5, 10
	index = "DRAGONS~Druid~Minion~7~5~10~~Goru the Mightree~Taunt~Battlecry~Legendary"
	requireTarget, keyWord, description = False, "Taunt", "Taunt. Battlecry: For the rest of the game, your Treants have +1/+1"
	name_CN = "强力巨树格鲁"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		GameTrigAura_BuffYourTreants(self.Game, self.ID).auraAppears()
		return None
		
class GameTrigAura_BuffYourTreants(HasAura_toMinion):
	def __init__(self, Game, ID):
		self.Game, self.ID = Game, ID
		self.auraAffected = []
		self.buff = 1
		
	#All minions appearing on the same side will be subject to the buffAura.
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject.ID == self.ID and subject.name == "Treant"
		
	def trig(self, signal, ID, subject, target, number, comment, choice=0):
		if self.canTrig(signal, ID, subject, target, number, comment):
			Stat_Receiver(subject, self, self.buff, self.buff).effectStart()
			
	def text(self, CHN):
		return "在本局对战的剩余时间内，你的树人获得+%d/+%d"%(self.buff, self.buff) if CHN \
				else "For the rest of the game, your Treants have +%d/+%d"%(self.buff, self.buff)
				
	def auraAppears(self):
		trigAuras = self.Game.trigAuras[self.ID]
		for obj in trigAuras:
			if isinstance(obj, GameTrigAura_BuffYourTreants):
				obj.improve()
				return
		trigAuras.append(self)
		for minion in self.Game.minionsonBoard(self.ID):
			if minion.name == "Treant": Stat_Receiver(minion, self, self.buff, self.buff).effectStart()
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
			if minion.name == "Treant": Stat_Receiver(minion, self, self.buff, self.buff).effectStart()
	#这个函数会在复制场上扳机列表的时候被调用。
	def createCopy(self, game):
		#一个光环的注册可能需要注册多个扳机
		if self not in game.copiedObjs: #这个光环没有被复制过
			entityCopy = self.entity.createCopy(game)
			Copy = self.selfCopy(entityCopy)
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
			
class YseraUnleashed(Minion):
	Class, race, name = "Druid", "Dragon", "Ysera, Unleashed"
	mana, attack, health = 9, 4, 12
	index = "DRAGONS~Druid~Minion~9~4~12~Dragon~Ysera, Unleashed~Battlecry~Legendary"
	requireTarget, keyWord, description = False, "", "Battlecry: Shuffle 7 Dream Portals into your deck. When drawn, summon a random Dragon"
	name_CN = "觉醒巨龙 伊瑟拉"
	poolIdentifier = "Dragons to Summon"
	@classmethod
	def generatePool(cls, Game):
		return "Dragons to Summon", list(Game.MinionswithRace["Dragon"].values())
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		portals = [DreamPortal(self.Game, self.ID) for i in range(7)]
		self.Game.Hand_Deck.shuffleintoDeck(portals, creator=self)
		return None
		
class DreamPortal(Spell):
	Class, school, name = "Druid", "", "Dream Portal"
	requireTarget, mana = False, 9
	index = "DRAGONS~Druid~Spell~9~Dream Portal~Casts When Drawn~Uncollectible"
	description = "Casts When Drawn. Summon a random Dragon"
	name_CN = "梦境之门"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if curGame.mode == 0:
			if curGame.guides:
				dragon = curGame.guides.pop(0)
			else:
				dragon = npchoice(self.rngPool("Dragons to Summon"))
				curGame.fixedGuides.append(dragon)
			curGame.summon(dragon(curGame, self.ID), -1, self)
		return None
		
		
"""Hunter cards"""
class CleartheWay(Quest):
	Class, school, name = "Hunter", "", "Clear the Way"
	requireTarget, mana = False, 1
	index = "DRAGONS~Hunter~Spell~1~Clear the Way~~Quest"
	description = "Sidequest: Summon 3 Rush minions. Reward: Summon a 4/4 Gryphon with Rush"
	name_CN = "扫清道路"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_CleartheWay(self)]
		
class Trig_CleartheWay(QuestTrigger):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionBeenSummoned"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		#不知道召唤随从因为突袭光环而具有突袭是否可以算作任务进度
		return subject.ID == self.entity.ID and subject.keyWords["Rush"] > 0
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.counter += 1
		if self.counter > 2:
			self.disconnect()
			try: self.entity.Game.Secrets.sideQuests[self.entity.ID].remove(self.entity)
			except: pass
			self.entity.Game.summon(Gryphon_Dragons(self.entity.Game, self.entity.ID), -1, self.entity)
			
			
class Gryphon_Dragons(Minion):
	Class, race, name = "Hunter", "Beast", "Gryphon"
	mana, attack, health = 4, 4, 4
	index = "DRAGONS~Hunter~Minion~4~4~4~Beast~Gryphon~Rush~Uncollectible"
	requireTarget, keyWord, description = False, "Rush", "Rush"
	name_CN = "狮鹫"
	
	
class DwarvenSharpshooter(Minion):
	Class, race, name = "Hunter", "", "Dwarven Sharpshooter"
	mana, attack, health = 1, 1, 3
	index = "DRAGONS~Hunter~Minion~1~1~3~~Dwarven Sharpshooter"
	requireTarget, keyWord, description = False, "", "Your Hero Power can target minions"
	name_CN = "矮人神射手"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.auras["Your Hero Power can target minions"] = GameRuleAura_DwarvenSharpshooter(self)
		
class GameRuleAura_DwarvenSharpshooter(GameRuleAura):
	def auraAppears(self):
		self.entity.Game.status[self.entity.ID]["Power Can Target Minions"] += 1
		
	def auraDisappears(self):
		self.entity.Game.status[self.entity.ID]["Power Can Target Minions"] -= 1
		
		
class ToxicReinforcements(Quest):
	Class, school, name = "Hunter", "", "Toxic Reinforcements"
	requireTarget, mana = False, 1
	index = "DRAGONS~Hunter~Spell~1~Toxic Reinforcements~~Quest"
	description = "Sidequest: Use your Hero Power three times. Reward: Summon three 1/1 Leper Gnomes"
	name_CN = "病毒增援"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_ToxicReinforcement(self)]
		
class Trig_ToxicReinforcement(QuestTrigger):
	def __init__(self, entity):
		self.blank_init(entity, ["HeroUsedAbility"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.counter += 1
		if self.counter > 2:
			self.disconnect()
			try: self.entity.Game.Secrets.sideQuests[self.entity.ID].remove(self.entity)
			except: pass
			self.entity.Game.summon([LeperGnome_Dragons(self.entity.Game, self.entity.ID) for i in range(3)], (-1, "totheRightEnd"), self.entity)
			
class LeperGnome_Dragons(Minion):
	Class, race, name = "Neutral", "", "Leper Gnome"
	mana, attack, health = 1, 1, 1
	index = "DRAGONS~Neutral~Minion~1~1~1~~Leper Gnome~Deathrattle~Uncollectible"
	requireTarget, keyWord, description = False, "", "Deathrattle: Deal 2 damage to the enemy hero"
	name_CN = "麻风侏儒"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [Deal2DamagetoEnemyHero(self)]
		
class Deal2DamagetoEnemyHero(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.dealsDamage(self.entity.Game.heroes[3-self.entity.ID], 2)
		
	def text(self, CHN):
		return "亡语：对敌方英雄造成2点伤害" if CHN else "Deathrattle: Deal 2 damage to the enemy hero"
		
		
class CorrosiveBreath(Spell):
	Class, school, name = "Hunter", "Nature", "Corrosive Breath"
	requireTarget, mana = True, 2
	index = "DRAGONS~Hunter~Spell~2~Nature~Corrosive Breath"
	description = "Deal 3 damage to a minion. If you're holding a Dragon, it also hits the enemy hero"
	name_CN = "腐蚀吐息"
	def effCanTrig(self):
		self.effectViable = self.Game.Hand_Deck.holdingDragon(self.ID)
		
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			damage = (3 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			self.dealsDamage(target, damage)
			if self.Game.Hand_Deck.holdingDragon(self.ID):
				self.dealsDamage(self.Game.heroes[3-self.ID], damage)
		return target
		
		
class PhaseStalker(Minion):
	Class, race, name = "Hunter", "Beast", "Phase Stalker"
	mana, attack, health = 2, 2, 3
	index = "DRAGONS~Hunter~Minion~2~2~3~Beast~Phase Stalker"
	requireTarget, keyWord, description = False, "", "After you use your Hero Power, cast a Secret from your deck"
	name_CN = "相位追踪者"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_PhaseStalker(self)]
		
class Trig_PhaseStalker(TrigBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["HeroUsedAbility"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and ID == self.entity.ID
		
	def text(self, CHN):
		return "在你使用你的英雄技能后，从你的牌库中施放一个奥秘" if CHN \
				else "After you use your Hero Power, cast a Secret from your deck"
				
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.Game.Secrets.deploySecretsfromDeck(self.entity.ID)
		
		
class DivingGryphon(Minion):
	Class, race, name = "Hunter", "Beast", "Diving Gryphon"
	mana, attack, health = 3, 4, 1
	index = "DRAGONS~Hunter~Minion~3~4~1~Beast~Diving Gryphon~Rush~Battlecry"
	requireTarget, keyWord, description = False, "Rush", "Rush. Battlecry: Draw a Rush minion from your deck"
	name_CN = "俯冲狮鹫"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if curGame.mode == 0:
			if curGame.guides:
				i = curGame.guides.pop(0)
			else:
				rushMinions = [i for i, card in enumerate(curGame.Hand_Deck.decks[self.ID]) if card.type == "Minion" and card.keyWords["Rush"] > 0]
				i = npchoice(rushMinions) if rushMinions else -1
				curGame.fixedGuides.append(i)
			if i > -1: curGame.Hand_Deck.drawCard(self.ID, i)[0]
		return None
		
		
class PrimordialExplorer(Minion):
	Class, race, name = "Hunter", "Dragon", "Primordial Explorer"
	mana, attack, health = 3, 2, 3
	index = "DRAGONS~Hunter~Minion~3~2~3~Dragon~Primordial Explorer~Poisonous~Battlecry"
	requireTarget, keyWord, description = False, "Poisonous", "Poisonous. Battlecry: Discover a Dragon"
	name_CN = "始生龙探险者"
	poolIdentifier = "Dragons as Hunter"
	@classmethod
	def generatePool(cls, Game):
		classCards = {s : [] for s in Game.ClassesandNeutral}
		for key, value in Game.MinionswithRace["Dragon"].items():
			classCards[key.split('~')[1]].append(value)
		return ["Dragons as "+Class for Class in Game.Classes], \
				[classCards[Class]+classCards["Neutral"] for Class in Game.Classes]
				
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if self.ID == curGame.turn:
			if curGame.mode == 0:
				if curGame.guides:
					curGame.Hand_Deck.addCardtoHand(curGame.guides.pop(0), self.ID, byType=True, byDiscover=True)
				else:
					key = "Dragons as "+classforDiscover(self)
					if "byOthers" in comment:
						dragon = npchoice(self.rngPool(key))
						curGame.fixedGuides.append(dragon)
						curGame.Hand_Deck.addCardtoHand(dragon, self.ID, byType=True, byDiscover=True)
					else:
						dragons = npchoice(self.rngPool(key), 3, replace=False)
						curGame.options = [dragon(curGame, self.ID) for dragon in dragons]
						curGame.Discover.startDiscover(self)
		return None
		
	def discoverDecided(self, option, pool):
		self.Game.fixedGuides.append(type(option))
		self.Game.Hand_Deck.addCardtoHand(option, self.ID, byDiscover=True)
		
		
class Stormhammer(Weapon):
	Class, name, description = "Hunter", "Stormhammer", "Doesn't lose Durability while you control a Dragon"
	mana, attack, durability = 3, 3, 2
	index = "DRAGONS~Hunter~Weapon~3~3~2~Stormhammer"
	name_CN = "风暴之锤"
	def loseDurability(self):
		if not any("Dragon" in minion.race for minion in self.Game.minionsonBoard(self.ID)):
			self.durability -= 1
			
			
class Dragonbane(Minion):
	Class, race, name = "Hunter", "Mech", "Dragonbane"
	mana, attack, health = 4, 3, 5
	index = "DRAGONS~Hunter~Minion~4~3~5~Mech~Dragonbane~Legendary"
	requireTarget, keyWord, description = False, "", "After you use your Hero Power, deal 5 damage to a random enemy"
	name_CN = "灭龙弩炮"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_Dragonbane(self)]
		
class Trig_Dragonbane(TrigBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["HeroUsedAbility"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and ID == self.entity.ID
		
	def text(self, CHN):
		return "在你使用你的英雄技能后，随机对一个敌人造成5点伤害" if CHN else "After you use your Hero Power, deal 5 damage to a random enemy"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		curGame = self.entity.Game
		if curGame.mode == 0:
			char = None
			if curGame.guides:
				i, where = curGame.guides.pop(0)
				if where: char = curGame.find(i, where)
			else:
				chars = curGame.charsAlive(3-self.entity.ID)
				if chars:
					char = npchoice(chars)
					curGame.fixedGuides.append((char.pos, char.type+str(char.ID)))
				else:
					curGame.fixedGuides.append((0, ''))
			if char: self.entity.dealsDamage(char, 5)
			
			
class Veranus(Minion):
	Class, race, name = "Hunter", "Dragon", "Veranus"
	mana, attack, health = 6, 7, 6
	index = "DRAGONS~Hunter~Minion~6~7~6~Dragon~Veranus~Battlecry~Legendary"
	requireTarget, keyWord, description = False, "", "Battlecry: Change the Health of all enemy minions to 1"
	name_CN = "维拉努斯"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		for minion in self.Game.minionsonBoard(3-self.ID):
			minion.statReset(False, 1)
		return None
		
		
"""Mage cards"""
class ArcaneBreath(Spell):
	Class, school, name = "Mage", "Arcane", "Arcane Breath"
	requireTarget, mana = True, 1
	index = "DRAGONS~Mage~Spell~1~Arcane~Arcane Breath"
	description = "Deal 2 damage to a minion. If you're holding a Dragon, Discover a spell"
	name_CN = "奥术吐息"
	poolIdentifier = "Mage Spells"
	@classmethod
	def generatePool(cls, Game):
		return [Class+" Spells" for Class in Game.Classes], \
				[[value for key, value in Game.ClassCards[Class].items() if "~Spell~" in key] for Class in Game.Classes]
				
	def effCanTrig(self):
		self.effectViable = self.Game.Hand_Deck.holdingDragon(self.ID)
		
	def targetExists(self, choice=0):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
		
	def text(self, CHN):
		damage = (1 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		return "对一个随从造成%d点伤害，如果你的手牌中有龙牌，便发现一张法术牌"%damage if CHN \
				else "Deal 2 damage to a minion. If you're holding a Dragon, Discover a spell"%damage
				
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if target:
			damage = (2 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			self.dealsDamage(target, damage)
			if curGame.Hand_Deck.holdingDragon(self.ID):
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
		
		
class ElementalAllies(Quest):
	Class, school, name = "Mage", "", "Elemental Allies"
	requireTarget, mana = False, 1
	index = "DRAGONS~Mage~Spell~1~Elemental Allies~~Quest"
	description = "Sidequest: Play an Elemental two turns in a row. Reward: Draw 3 spells from your deck"
	name_CN = "元素盟军"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_ElementalAllies(self)]
		
class Trig_ElementalAllies(QuestTrigger):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionBeenPlayed", "TurnEnds"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		if signal == "TurnEnds": return self.entity.ID == ID
		else: return subject.ID == self.entity.ID and "Elemental" in subject.race and self.counter < 2
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		curGame = self.entity.Game
		if signal == "TurnEnds": self.counter -= 1 * (self.counter > 0)
		else:
			self.counter += 2
			if self.counter > 2:
				self.disconnect()
				try: curGame.Secrets.sideQuests[self.entity.ID].remove(self.entity)
				except: pass
				ownDeck = curGame.Hand_Deck.decks[self.entity.ID]
				for num in range(3):
					if curGame.mode == 0:
						if curGame.guides:
							i = curGame.guides.pop(0)
						else:
							spells = [i for i, card in enumerate(ownDeck) if card.type == "Spell"]
							i = npchoice(spells) if spells else -1
							curGame.fixedGuides.append(i)
						if i > -1: curGame.Hand_Deck.drawCard(self.entity.ID, i)
						else: break
						
						
class LearnDraconic(Quest):
	Class, school, name = "Mage", "", "Learn Draconic"
	requireTarget, mana = False, 1
	index = "DRAGONS~Mage~Spell~1~Learn Draconic~~Quest"
	description = "Sidequest: Spend 8 Mana on spells. Reward: Summon a 6/6 Dragon"
	name_CN = "学习龙语"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_LearnDraconic(self)]
		
class Trig_LearnDraconic(QuestTrigger):
	def __init__(self, entity):
		self.blank_init(entity, ["SpellBeenPlayed"]) #假设是使用后扳机
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject.ID == self.entity.ID and self.entity != subject
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.counter += number
		if self.counter > 7:
			self.disconnect()
			try: self.entity.Game.Secrets.sideQuests[self.entity.ID].remove(self.entity)
			except: pass
			self.entity.Game.summon(DraconicEmissary(self.entity.Game, self.entity.ID), -1, self.entity)
			
class DraconicEmissary(Minion):
	Class, race, name = "Mage", "Dragon", "Draconic Emissary"
	mana, attack, health = 6, 6, 6
	index = "DRAGONS~Mage~Minion~6~6~6~Dragon~Draconic Emissary~Uncollectible"
	requireTarget, keyWord, description = False, "", ""
	name_CN = "龙族使者"
	
	
class VioletSpellwing(Minion):
	Class, race, name = "Mage", "Elemental", "Violet Spellwing"
	mana, attack, health = 1, 1, 1
	index = "DRAGONS~Mage~Minion~1~1~1~Elemental~Violet Spellwing~Deathrattle"
	requireTarget, keyWord, description = False, "", "Deathrattle: Add an 'Arcane Missile' to your hand"
	name_CN = "紫罗兰 魔翼鸦"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [Add1ArcaneMisslestoYourHand(self)]
#这个奥术飞弹是属于基础卡（无标志）
class Add1ArcaneMisslestoYourHand(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.Game.Hand_Deck.addCardtoHand(ArcaneMissiles, self.entity.ID, byType=True)
		
	def text(self, CHN):
		return "亡语：将一张“奥术飞弹”法术牌置入你的手牌" if CHN else "Deathrattle: Add an 'Arcane Missile' to your hand"
		
		
class Chenvaala(Minion):
	Class, race, name = "Mage", "Elemental", "Chenvaala"
	mana, attack, health = 3, 2, 5
	index = "DRAGONS~Mage~Minion~3~2~5~Elemental~Chenvaala~Legendary"
	requireTarget, keyWord, description = False, "", "After you cast three spells in a turn, summon a 5/5 Elemental"
	name_CN = "齐恩瓦拉"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_Chenvaala(self)]
		
class Trig_Chenvaala(TrigBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["SpellBeenPlayed", "TurnEnds", "TurnStarts"])
		self.counter = 0
		
	def connect(self):
		for sig in self.signals:
			try: self.entity.Game.trigsBoard[self.entity.ID][sig].append(self)
			except: self.entity.Game.trigsBoard[self.entity.ID][sig] = [self]
		self.counter = 0
		
	def disconnect(self):
		for sig in self.signals:
			try: self.entity.Game.trigsBoard[self.entity.ID][sig].remove(self)
			except: pass
		self.counter = 0
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return signal[0] == 'T' or (self.entity.onBoard and subject.ID == self.entity.ID)
		
	def text(self, CHN):
		return "你在一回合中施放三个法术后，召唤一个5/5的元素(还差%d个)"%(3-self.counter) if CHN \
				else "After you cast three spells in a turn, summon a 5/5 Elemental(%d spells left)"%(3-self.counter)
				
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		if signal == "SpellBeenPlayed":
			self.counter += 1
			if self.counter > 0 and self.counter % 3 == 0:
				self.counter = 0
				self.entity.Game.summon(SnowElemental(self.entity.Game, self.entity.ID), self.entity.pos+1, self.entity)
		else: #At the start/end of turn, the counter is reset
			self.entity.resetCounter()
	#Chenvaala在游戏内复制的时候不保留扳机进度
	
class SnowElemental(Minion):
	Class, race, name = "Mage", "Elemental", "Snow Elemental"
	mana, attack, health = 5, 5, 5
	index = "DRAGONS~Mage~Minion~5~5~5~Elemental~Snow Elemental~Uncollectible"
	requireTarget, keyWord, description = False, "", ""
	name_CN = "冰雪元素"
	
	
class AzureExplorer(Minion):
	Class, race, name = "Mage", "Dragon", "Azure Explorer"
	mana, attack, health = 4, 2, 3
	index = "DRAGONS~Mage~Minion~4~2~3~Dragon~Azure Explorer~Spell Damage~Battlecry"
	requireTarget, keyWord, description = False, "", "Spell Damage +2. Battlecry: Discover a Dragon"
	name_CN = "碧蓝龙探险者"
	poolIdentifier = "Dragons as Mage"
	@classmethod
	def generatePool(cls, Game):
		classCards = {s : [] for s in Game.ClassesandNeutral}
		for key, value in Game.MinionswithRace["Dragon"].items():
			classCards[key.split('~')[1]].append(value)
		return ["Dragons as "+Class for Class in Game.Classes], \
				[classCards[Class]+classCards["Neutral"] for Class in Game.Classes]
				
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.keyWords["Spell Damage"] = 2
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if self.ID == curGame.turn:
			if curGame.mode == 0:
				if curGame.guides:
					curGame.Hand_Deck.addCardtoHand(curGame.guides.pop(0), self.ID, byType=True, byDiscover=True)
				else:
					key = "Dragons as "+classforDiscover(self)
					if "byOthers" in comment:
						dragon = npchoice(self.rngPool(key))
						curGame.fixedGuides.append(dragon)
						curGame.Hand_Deck.addCardtoHand(dragon, self.ID, byType=True, byDiscover=True)
					else:
						dragons = npchoice(self.rngPool(key), 3, replace=False)
						curGame.options = [dragon(curGame, self.ID) for dragon in dragons]
						curGame.Discover.startDiscover(self)
		return None
		
	def discoverDecided(self, option, pool):
		self.Game.fixedGuides.append(type(option))
		self.Game.Hand_Deck.addCardtoHand(option, self.ID, byDiscover=True)
		
		
class MalygossFrostbolt(Spell):
	Class, school, name = "Mage", "", "Malygos's Frostbolt"
	requireTarget, mana = True, 0
	index = "DRAGONS~Mage~Spell~0~Malygos's Frostbolt~Legendary~Uncollectible"
	description = "Deal 3 damage to a character and Freeze it"
	name_CN = "玛里苟斯的 寒冰箭"
	def text(self, CHN):
		damage = (3 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		return "对一个角色造成%d点伤害，并使其冻结"%damage if CHN else "Deal %d damage to a character and Freeze it"%damage
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			damage = (3 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			self.dealsDamage(target, damage)
			target.getsFrozen()
		return target
		
class MalygossMissiles(Spell):
	Class, school, name = "Mage", "", "Malygos's Missiles"
	requireTarget, mana = False, 1
	index = "DRAGONS~Mage~Spell~1~Malygos's Missiles~Legendary~Uncollectible"
	description = "Deal 6 damage randomly split among all enemies"
	name_CN = "玛里苟斯的 奥术飞弹"
	def text(self, CHN):
		damage = (6 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		return "造成%d点伤害，随机分配到所有敌人身上"%damage if CHN else "Deal %d damage randomly split among all enemies"%damage
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		damage = (6 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		side, curGame = 3-self.ID, self.Game
		if curGame.mode == 0:
			for num in range(damage):
				char = None
				if curGame.guides:
					i, where = curGame.guides.pop(0)
					if where: char = curGame.find(i, where)
				else:
					objs = curGame.charsAlive(side)
					if objs:
						char = npchoice(objs)
						curGame.fixedGuides.append((char.pos, char.type+str(char.ID)))
					else:
						curGame.fixedGuides.append((0, ''))
				if i > -1: self.dealsDamage(char, 1)
				else: break
		return None
		
		
class MalygossNova(Spell):
	Class, school, name = "Mage", "", "Malygos's Nova"
	requireTarget, mana = False, 1
	index = "DRAGONS~Mage~Spell~1~Malygos's Nova~Legendary~Uncollectible"
	description = "Freeze all enemy minions"
	name_CN = "玛里苟斯的 霜冻新星"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		for minion in self.Game.minionsonBoard(3-self.ID):
			minion.getsFrozen()
		return None
		
class MalygossPolymorph(Spell):
	Class, school, name = "Mage", "", "Malygos's Polymorph"
	requireTarget, mana = True, 1
	index = "DRAGONS~Mage~Spell~1~Malygos's Polymorph~Legendary~Uncollectible"
	description = "Transform a minion into a 1/1 Sheep"
	name_CN = "玛里苟斯的 变形术"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			newMinion = MalygossSheep(self.Game, target.ID)
			self.Game.transform(target, newMinion)
			target = newMinion
		return target
			
class MalygossTome(Spell):
	Class, school, name = "Mage", "", "Malygos's Tome"
	requireTarget, mana = False, 1
	index = "DRAGONS~Mage~Spell~1~Malygos's Tome~Legendary~Uncollectible"
	description = "Add 3 random Mage spells to your hand"
	name_CN = "玛里苟斯的 智慧秘典"
	poolIdentifier = "Mage Spells"
	@classmethod
	def generatePool(cls, Game):
		return "Mage Spells", [value for key, value in Game.ClassCards["Mage"].items() if "~Spell~" in key]
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if curGame.guides:
			spells = list(curGame.guides.pop(0))
		else:
			spells = npchoice(self.rngPool("Mage Spells"), 3, replace=True)
			curGame.fixedGuides.append(tuple(spells))
		curGame.Hand_Deck.addCardtoHand(spells, self.ID, byType=True)
		return None
		
class MalygossExplosion(Spell):
	Class, school, name = "Mage", "", "Malygos's Explosion"
	requireTarget, mana = False, 2
	index = "DRAGONS~Mage~Spell~2~Malygos's Explosion~Legendary~Uncollectible"
	description = "Deal 2 damage to all enemy minions"
	name_CN = "玛里苟斯的 魔爆术"
	def text(self, CHN):
		damage = (2 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		return "对所有敌方随从造成%d点伤害"%damage if CHN else "Deal %d damage to all enemy minions"%damage
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		damage = (2 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		targets = self.Game.minionsonBoard(3-self.ID)
		self.dealsAOE(targets, [damage for obj in targets])
		return None
		
class MalygossIntellect(Spell):
	Class, school, name = "Mage", "", "Malygos's Intellect"
	requireTarget, mana = False, 3
	index = "DRAGONS~Mage~Spell~3~Malygos's Intellect~Legendary~Uncollectible"
	description = "Draw 4 cards"
	name_CN = "玛里苟斯的 奥术智慧"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		for i in range(4): self.Game.Hand_Deck.drawCard(self.ID)
		return None
		
class MalygossFireball(Spell):
	Class, school, name = "Mage", "", "Malygos's Fireball"
	requireTarget, mana = True, 4
	index = "DRAGONS~Mage~Spell~4~Malygos's Fireball~Legendary~Uncollectible"
	description = "Deal 8 damage"
	name_CN = "玛里苟斯的 火球术"
	def text(self, CHN):
		damage = (8 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		return "造成%d点伤害"%damage if CHN else "Deal %d damage"%damage
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			damage = (8 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			self.dealsDamage(target, damage)
		return target
		
class MalygossFlamestrike(Spell):
	Class, school, name = "Mage", "", "Malygos's Flamestrike"
	requireTarget, mana = False, 7
	index = "DRAGONS~Mage~Spell~7~Malygos's Flamestrike~Legendary~Uncollectible"
	description = "Deal 8 damage to all enemy minions"
	name_CN = "玛里苟斯的 烈焰风暴"
	def text(self, CHN):
		damage = (8 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		return "对所有敌方随从造成%d点伤害"%damage if CHN else "Deal %d damage to all enemy minions"%damage
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		damage = (8 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		targets = self.Game.minionsonBoard(3-self.ID)
		self.dealsAOE(targets, [damage for minion in targets])
		return None
		
class MalygossSheep(Minion):
	Class, race, name = "Mage", "Beast", "Malygos's Sheep"
	mana, attack, health = 1, 1, 1
	index = "DRAGONS~Mage~Minion~1~1~1~Beast~Malygos's Sheep~Legendary~Uncollectible"
	requireTarget, keyWord, description = False, "", ""
	name_CN = "玛里苟斯的 绵羊"
	
MalygosUpgradedSpells = [MalygossFrostbolt, MalygossMissiles, MalygossNova, MalygossPolymorph, MalygossTome,
						MalygossExplosion, MalygossIntellect, MalygossFireball, MalygossFlamestrike
						]
						
class MalygosAspectofMagic(Minion):
	Class, race, name = "Mage", "Dragon", "Malygos, Aspect of Magic"
	mana, attack, health = 5, 2, 8
	index = "DRAGONS~Mage~Minion~5~2~8~Dragon~Malygos, Aspect of Magic~Battlecry~Legendary"
	requireTarget, keyWord, description = False, "", "Battlecry: If you're holding a Dragon, Discover an upgraded Mage spell"
	name_CN = "织法巨龙 玛里苟斯"
	
	def effCanTrig(self):
		self.effectViable = self.Game.Hand_Deck.holdingDragon(self.ID, self)
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if curGame.Hand_Deck.holdingDragon(self.ID) and self.ID == curGame.turn:
			if curGame.guides:
				curGame.Hand_Deck.addCardtoHand(curGame.guides.pop(0), self.ID, byType=True, byDiscover=True)
			else:
				if "byOthers" in comment:
					spell = npchoice(MalygosUpgradedSpells)
					curGame.fixedGuides.append(spell)
					curGame.Hand_Deck.addCardtoHand(spell, self.ID, byType=True, byDiscover=True)
				else:
					spells = npchoice(MalygosUpgradedSpells, 3, replace=False)
					curGame.options = [spell(curGame, self.ID) for spell in spells]
					curGame.Discover.startDiscover(self)
		return None
		
	def discoverDecided(self, option, pool):
		self.Game.fixedGuides.append(type(option))
		self.Game.Hand_Deck.addCardtoHand(option, self.ID, byDiscover=True)
		
		
#火球滚滚会越过休眠物。直接打在相隔的其他随从上。圣盾随从会分担等于自己当前生命值的伤害。
class RollingFireball(Spell):
	Class, school, name = "Mage", "Fire", "Rolling Fireball"
	requireTarget, mana = True, 5
	index = "DRAGONS~Mage~Spell~5~Fire~Rolling Fireball"
	description = "Deal 8 damage to a minion. Any excess damage continues to the left or right"
	name_CN = "火球滚滚"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
		
	def text(self, CHN):
		damage = (8 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		return "对一个随从造成%d点伤害，超过其生命值的伤害将由左侧或右侧的随从承担"%damage if CHN \
				else "Deal %d damage to a minion. Any excess damage continues to the left or right"%damage
				
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			damage = (8 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			curGame = self.Game
			if curGame.mode == 0:
				minion, direction, damageleft = None, "", damage
				damageDealt = min(target.health, damageleft) if target.health > 0 else 0
				damageleft -= damageDealt
				if curGame.guides:
					i, where, direction = curGame.guides.pop(0)
					if where: minion = curGame.find(i, where)
				else:
					#火球滚滚打到牌库中的随从是没有任何后续效果的。不知道目标随从提前死亡的话会如何
					if target.onBoard:
						neighbors, dist = curGame.neighbors2(target, True) #对目标进行伤害之后，在场上寻找其相邻随从，决定滚动方向。
						#direction = 1 means fireball rolls right, direction = 1 is left
						if dist == 1:
							ran = nprandint(2) #ran == 1: roll right, 0: roll left
							minion, direction = neighbors[ran], ran
						elif dist < 0: minion, direction = neighbors[0], 0
						elif dist == 2: minion, direction = neighbors[0], 1
						if minion: curGame.fixedGuides.append((minion.pos, "Minion%d"%minion.ID, direction))
						else: curGame.fixedGuides.append((0, '', ''))
					else: #如果可以在手牌中找到那个随从时
						#火球滚滚打到手牌中的随从时，会判断目前那个随从在手牌中位置，如果在从左数第3张的话，那么会将过量伤害传递给场上的2号或者4号随从。
						try: i = curGame.Hand_Deck.hands[target.ID].index(target)
						except: i = -1
						if i > -1:
							minions = curGame.minionsonBoard(3-self.ID) #对手牌中的随从进行伤害之后，寻找场上合适的随从并确定滚动方向。
							if minions:
								if i == 0: minion, direction = minions[1] if len(minions) > 1 else None, 1
								elif i + 1 < len(minions): #手牌中第4张（编号3），如果场上有5张随从，仍然随机
									if nprandint(2): minion, direction = minions[i+1], 1
									else: minion, direction = minions[i-1], 0
								#如果随从在手牌中的编号很大，如手牌中第5张（编号4），则如果场上有5张或者以下随从，则都会向左滚
								else: minion, direction = minions[-1], 0
								if minion: curGame.fixedGuides.append((minion.pos, "Minion%d"%minion.ID, direction))
								else: curGame.fixedGuides.append((0, '', ''))
						else:
							curGame.fixedGuides.append((0, '', ''))
				self.dealsDamage(target, damageDealt)
				#当已经决定了要往哪个方向走之后
				while minion and damageleft > 0: #如果下个随从不存在或者没有剩余伤害则停止循环
					if minion.type == "Minion":
						damageDealt = min(minion.health, damageleft) if minion.health > 0 else 0
						self.dealsDamage(minion, damageDealt)
					else: damageDealt = 0 #休眠物可以被直接跳过，伤害为0
					damageleft -= damageDealt
					neighbors, dist = curGame.neighbors2(minion, True)
					if direction: #roll towards right
						minion = neighbors[2-dist] if dist > 0 else None
					else:
						minion = neighbors[0] if dist == 1 or dist == -1 else None
		return target
		
		
class Dragoncaster(Minion):
	Class, race, name = "Mage", "", "Dragoncaster"
	mana, attack, health = 7, 4, 4
	index = "DRAGONS~Mage~Minion~7~4~4~~Dragoncaster~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: If you're holding a Dragon, your next spell this turn costs (0)"
	name_CN = "乘龙法师"
	
	def effCanTrig(self):
		self.effectViable = self.Game.Hand_Deck.holdingDragon(self.ID)
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if self.Game.Hand_Deck.holdingDragon(self.ID):
			tempAura = GameManaAura_InTurnNextSpell0(self.Game, self.ID)
			self.Game.Manas.CardAuras.append(tempAura)
			tempAura.auraAppears()
		return None
		
class GameManaAura_InTurnNextSpell0(TempManaEffect):
	def __init__(self, Game, ID, changeby=0, changeto=-1):
		self.blank_init(Game, ID, 0, 0)
		
	def applicable(self, target):
		return target.ID == self.ID and target.type == "Spell"
		
	def text(self, CHN):
		return "在本回合中，你的下一张法术的法力值消耗为(0)点" if CHN else "Your next spell this turn costs (0)"
		
		
class ManaGiant(Minion):
	Class, race, name = "Mage", "Elemental", "Mana Giant"
	mana, attack, health = 8, 8, 8
	index = "DRAGONS~Mage~Minion~8~8~8~Elemental~Mana Giant"
	requireTarget, keyWord, description = False, "", "Costs (1) less for each card you've played this game that didn't start in your deck"
	name_CN = "法力巨人"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsHand = [Trig_ManaGiant(self)]
		
	def selfManaChange(self):
		if self.inHand:
			self.mana -= self.Game.Counters.createdCardsPlayedThisGame[self.ID]
			self.mana = max(self.mana, 0)
			
class Trig_ManaGiant(TrigHand):
	def __init__(self, entity):
		#假设这个费用改变扳机在“当你使用一张法术之后”。不需要预检测
		self.blank_init(entity, ["SpellBeenPlayed"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.inHand and subject.ID == self.entity.ID and subject.creator
		
	def text(self, CHN):
		return "每当你使用一张你的套牌之外的卡牌，重新计算费用" if CHN \
				else "Whenever you play a card that didn't start in your deck, recalculate the cost"
				
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.Game.Manas.calcMana_Single(self.entity)
		
		
"""Paladin cards"""
class RighteousCause(Quest):
	Class, school, name = "Paladin", "", "Righteous Cause"
	requireTarget, mana = False, 1
	index = "DRAGONS~Paladin~Spell~1~Righteous Cause~~Quest"
	description = "Sidequest: Summon 5 minions. Reward: Give your minions +1/+1"
	name_CN = "正义感召"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_RighteousCause(self)]
		
class Trig_RighteousCause(QuestTrigger):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionBeenSummoned"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject.ID == self.entity.ID
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.counter += 1
		if self.counter > 4:
			self.disconnect()
			try: self.entity.Game.Secrets.sideQuests[self.entity.ID].remove(self.entity)
			except: pass
			for minion in self.entity.Game.minionsonBoard(self.entity.ID):
				minion.buffDebuff(1, 1)
				
				
class SandBreath(Spell):
	Class, school, name = "Paladin", "", "Sand Breath"
	requireTarget, mana = True, 1
	index = "DRAGONS~Paladin~Spell~1~Sand Breath"
	description = "Give a minion +1/+2. Give it Divine Shield if you're holding a Dragon"
	name_CN = "沙尘吐息"
	def effCanTrig(self):
		self.effectViable = self.Game.Hand_Deck.holdingDragon(self.ID)
		
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			target.buffDebuff(1, 2)
			if self.Game.Hand_Deck.holdingDragon(self.ID):
				target.getsKeyword("Divine Shield")
		return target	
		
		
class Sanctuary(Quest):
	Class, school, name = "Paladin", "", "Sanctuary"
	requireTarget, mana = False, 2
	index = "DRAGONS~Paladin~Spell~2~Sanctuary~~Quest"
	description = "Sidequest: Take no damage for a turn. Reward: Summon a 3/6 minion with Taunt"
	name_CN = "庇护"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_Sanctuary(self)]
		
class Trig_Sanctuary(QuestTrigger):
	def __init__(self, entity):
		self.blank_init(entity, ["TurnStarts"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		#在我方回合开始时会触发
		return ID == self.entity.ID and self.entity.Game.Counters.dmgonHero_inOppoTurn[self.entity.ID] == 0
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		game = self.entity.Game
		self.disconnect()
		try: game.Secrets.sideQuests[self.entity.ID].remove(self.entity)
		except: pass
		game.summon(IndomitableChampion(game, self.entity.ID), -1, self.entity)
		
class IndomitableChampion(Minion):
	Class, race, name = "Paladin", "", "Indomitable Champion"
	mana, attack, health = 4, 3, 6
	index = "DRAGONS~Paladin~Minion~4~3~6~~Indomitable Champion~Taunt~Uncollectible"
	requireTarget, keyWord, description = False, "Taunt", "Taunt"
	name_CN = "不屈的勇士"
	
	
class BronzeExplorer(Minion):
	Class, race, name = "Paladin", "Dragon", "Bronze Explorer"
	mana, attack, health = 3, 2, 3
	index = "DRAGONS~Paladin~Minion~3~2~3~Dragon~Bronze Explorer~Lifesteal~Battlecry"
	requireTarget, keyWord, description = False, "Lifesteal", "Lifesteal. Battlecry: Discover a Dragon"
	name_CN = "青铜龙探险者"
	poolIdentifier = "Dragons as Paladin"
	@classmethod
	def generatePool(cls, Game):
		classCards = {s : [] for s in Game.ClassesandNeutral}
		for key, value in Game.MinionswithRace["Dragon"].items():
			classCards[key.split('~')[1]].append(value)
		return ["Dragons as "+Class for Class in Game.Classes], \
				[classCards[Class]+classCards["Neutral"] for Class in Game.Classes]
				
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if self.ID == curGame.turn:
			if curGame.mode == 0:
				if curGame.guides:
					curGame.Hand_Deck.addCardtoHand(curGame.guides.pop(0), self.ID, byType=True, byDiscover=True)
				else:
					key = "Dragons as "+classforDiscover(self)
					if "byOthers" in comment:
						dragon = npchoice(self.rngPool(key))
						curGame.fixedGuides.append(dragon)
						curGame.Hand_Deck.addCardtoHand(dragon, self.ID, byType=True, byDiscover=True)
					else:
						dragons = npchoice(self.rngPool(key), 3, replace=False)
						curGame.options = [dragon(curGame, self.ID) for dragon in dragons]
						curGame.Discover.startDiscover(self)
		return None
		
	def discoverDecided(self, option, pool):
		self.Game.fixedGuides.append(type(option))
		self.Game.Hand_Deck.addCardtoHand(option, self.ID, byDiscover=True)
		
		
class SkyClaw(Minion):
	Class, race, name = "Paladin", "Mech", "Sky Claw"
	mana, attack, health = 3, 1, 2
	index = "DRAGONS~Paladin~Minion~3~1~2~Mech~Sky Claw~Battlecry"
	requireTarget, keyWord, description = False, "", "Your other Mechs have +1 Attack. Battlecry: Summon two 1/1 Microcopters"
	name_CN = "空中飞爪"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.auras["Your other Mechs have +1 Attack"] = StatAura_Others(self, 1, 0)
		
	def applicable(self, target):
		return "Mech" in target.race
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		pos = (self.pos, "leftandRight") if self.onBoard else (-1, "totheRightEnd")
		self.Game.summon([Microcopter(self.Game, self.ID) for i in range(2)], pos, self)
		return None
		
class Microcopter(Minion):
	Class, race, name = "Paladin", "Mech", "Microcopter"
	mana, attack, health = 1, 1, 1
	index = "DRAGONS~Paladin~Minion~1~1~1~Mech~Microcopter~Uncollectible"
	requireTarget, keyWord, description = False, "", ""
	name_CN = "微型旋翼机"
	
	
class DragonriderTalritha(Minion):
	Class, race, name = "Paladin", "", "Dragonrider Talritha"
	mana, attack, health = 3, 3, 3
	index = "DRAGONS~Paladin~Minion~3~3~3~~Dragonrider Talritha~Deathrattle~Legendary"
	requireTarget, keyWord, description = False, "", "Deathrattle: Give a Dragon in your hand +3/+3 and this Deathrattle"
	name_CN = "龙骑士塔瑞萨"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [GiveaDragoninHandPlus3Plus3AndThisDeathrattle(self)]
		
class GiveaDragoninHandPlus3Plus3AndThisDeathrattle(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		curGame = self.entity.Game
		ownHand = curGame.Hand_Deck.hands[self.entity.ID]
		if curGame.mode == 0:
			if curGame.guides:
				i = curGame.guides.pop(0)
			else:
				dragons = [i for i, card in enumerate(ownHand) if card.type == "Minion" and "Dragon" in card.race]
				i = npchoice(dragons) if dragons else -1
				curGame.fixedGuides.append(i)
			if i > -1:
				dragon = ownHand[i]
				dragon.buffDebuff(3, 3)
				dragon.deathrattles.append(GiveaDragoninHandPlus3Plus3AndThisDeathrattle(dragon))
				
	def text(self, CHN):
		return "亡语：使你手牌中的一张龙牌获得+3/+3及此亡语" if CHN else "Deathrattle: Give a Dragon in your hand +3/+3 and this Deathrattle"
		
		
class LightforgedZealot(Minion):
	Class, race, name = "Paladin", "", "Lightforged Zealot"
	mana, attack, health = 4, 4, 2
	index = "DRAGONS~Paladin~Minion~4~4~2~~Lightforged Zealot~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: If your deck has no Neutral cards, equip a 4/2 Truesilver Champion"
	name_CN = "光铸狂热者"
	
	def effCanTrig(self):
		self.effectViable = all(card.Class != "Neutral" for card in self.Game.Hand_Deck.decks[self.ID])
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if all(card.Class != "Neutral" for card in self.Game.Hand_Deck.decks[self.ID]):
			self.Game.equipWeapon(TruesilverChampion(self.Game, self.ID))
		return None
		
		
class NozdormutheTimeless(Minion):
	Class, race, name = "Paladin", "Dragon", "Nozdormu the Timeless"
	mana, attack, health = 4, 8, 8
	index = "DRAGONS~Paladin~Minion~4~8~8~Dragon~Nozdormu the Timeless~Battlecry~Legendary"
	requireTarget, keyWord, description = False, "", "Battlecry: Set each player to 10 Mana Crystals"
	name_CN = "时光巨龙 诺兹多姆"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.Game.Manas.setManaCrystal(10, 1)
		self.Game.Manas.setManaCrystal(10, 2)
		return None
		
		
class AmberWatcher(Minion):
	Class, race, name = "Paladin", "Dragon", "Amber Watcher"
	mana, attack, health = 5, 4, 6
	index = "DRAGONS~Paladin~Minion~5~4~6~Dragon~Amber Watcher~Battlecry"
	requireTarget, keyWord, description = True, "", "Battlecry: Restore 8 Health"
	name_CN = "琥珀看守者"
	
	def text(self, CHN):
		heal = 8 * (2 ** self.countHealDouble())
		return "战吼：恢复%d点生命值"%heal if CHN else "Battlecry: Restore %d health"%heal
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			heal = 8 * (2 ** self.countHealDouble())
			self.restoresHealth(target, heal)
		return target
		
		
class LightforgedCrusader(Minion):
	Class, race, name = "Paladin", "", "Lightforged Crusader"
	mana, attack, health = 7, 7, 7
	index = "DRAGONS~Paladin~Minion~7~7~7~~Lightforged Crusader~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: If your deck has no Neutral cards, add 5 random Paladin cards to your hand"
	name_CN = "光铸远征军"
	poolIdentifier = "Paladin Cards"
	@classmethod
	def generatePool(cls, Game):
		return "Paladin Cards", list(Game.ClassCards["Paladin"].values())
		
	def effCanTrig(self):
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
			else:
				noNeutralCards = True
				for card in curGame.Hand_Deck.decks[self.ID]:
					if card.Class == "Neutral":
						noNeutralCards = False
						break
				cards = tuple(npchoice(self.rngPool("Paladin Cards"), 5, replace=True)) if noNeutralCards else ()
				curGame.fixedGuides.append(cards)
			if cards:
				curGame.Hand_Deck.addCardtoHand(cards, self.ID, byType=True)
		return None
		
		
"""Priest cards"""
class WhispersofEVIL(Spell):
	Class, school, name = "Priest", "", "Whispers of EVIL"
	requireTarget, mana = False, 0
	index = "DRAGONS~Priest~Spell~0~Whispers of EVIL"
	description = "Add a Lackey to your hand"
	name_CN = "怪盗低语"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if curGame.mode == 0:
			if curGame.guides:
				lackey = curGame.guides.pop(0)
			else:
				lackey = npchoice(Lackeys)
				curGame.fixedGuides.append(lackey)
			curGame.Hand_Deck.addCardtoHand(lackey, self.ID, byType=True)
		return None
		
		
class DiscipleofGalakrond(Minion):
	Class, race, name = "Priest", "", "Disciple of Galakrond"
	mana, attack, health = 1, 1, 2
	index = "DRAGONS~Priest~Minion~1~1~2~~Disciple of Galakrond~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Invoke Galakrond"
	name_CN = "迦拉克隆的 信徒"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		invokeGalakrond(self.Game, self.ID)
		return None
		
		
class EnvoyofLazul(Minion):
	Class, race, name = "Priest", "", "Envoy of Lazul"
	mana, attack, health = 2, 2, 2
	index = "DRAGONS~Priest~Minion~2~2~2~~Envoy of Lazul~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Look at 3 cards. Guess which one is in your opponent's hand to get a copy of it"
	name_CN = "拉祖尔的信使"
	
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
					if i > -1:
						HD.addCardtoHand(HD.hands[3-self.ID][i].selfCopy(self.ID, self), self.ID)
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
						curGame.Discover.startDiscover(self)
		return None
		
	def discoverDecided(self, option, pool):
		curGame = self.Game
		if option.inHand:
			i = curGame.Hand_Deck.hands[3-self.ID].index(option)
			curGame.fixedGuides.append(i)
			Copy = option.selfCopy(self.ID, self)
			curGame.Hand_Deck.addCardtoHand(Copy, self.ID)
		else:
			curGame.fixedGuides.append(-1)
			rightCard = None
			for card in curGame.options:
				if card.inHand:
					rightCard = card
					break
					
					
class BreathoftheInfinite(Spell):
	Class, school, name = "Priest", "", "Breath of the Infinite"
	requireTarget, mana = False, 3
	index = "DRAGONS~Priest~Spell~3~Breath of the Infinite"
	description = "Deal 2 damage to all minions. If you're holding a Dragon, only damage enemies"
	name_CN = "永恒吐息"
	def effCanTrig(self):
		self.effectViable = self.Game.Hand_Deck.holdingDragon(self.ID)
		
	def text(self, CHN):
		damage = (2 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		return "对所有随从造成%d点伤害。如果你的手牌中有龙牌，则只对敌方随从造成伤害"%damage if CHN \
				else "Deal %d damage to all minions. If you're holding a Dragon, only damage enemies"%damage
				
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		damage = (2 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		if self.Game.Hand_Deck.holdingDragon(self.ID):
			targets = self.Game.minionsonBoard(3-self.ID)
		else:
			targets = self.Game.minionsonBoard(self.ID) + self.Game.minionsonBoard(3-self.ID)
		self.dealsAOE(targets, [damage for minion in targets])
		return None
		
		
class MindflayerKaahrj(Minion):
	Class, race, name = "Priest", "", "Mindflayer Kaahrj"
	mana, attack, health = 3, 3, 3
	index = "DRAGONS~Priest~Minion~3~3~3~~Mindflayer Kaahrj~Battlecry~Deathrattle~Legendary"
	requireTarget, keyWord, description = True, "", "Battlecry: Choose an enemy minion. Deathrattle: Summon a new copy of it"
	name_CN = "夺心者卡什"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [SummonCopyofaChosenMinion(self)]
		
	def targetExists(self, choice=0):
		return self.selectableEnemyMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.ID != self.ID and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			for trig in self.deathrattles:
				if isinstance(trig, SummonCopyofaChosenMinion):
					trig.chosenMinionType = type(target)
		return target
		
class SummonCopyofaChosenMinion(Deathrattle_Minion):
	def __init__(self, entity):
		self.blank_init(entity)
		self.chosenMinionType = None
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return target == self.entity and self.chosenMinionType
		
	def text(self, CHN):
		if self.chosenMinionType:
			return "亡语：召唤一个%s"%self.chosenMinionType.name if CHN else "Deathrattle: Summon a %s"%self.chosenMinionType.name
		else:
			return "没有选定的随从，无法召唤" if CHN else "No minion chosen. Can't summon"
			
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		minion = self.entity
		minion.Game.summon(self.chosenMinionType(minion.Game, minion.ID), minion.pos+1, minion)
		
	def selfCopy(self, recipient):
		trig = type(self)(recipient)
		trig.chosenMinionType = self.chosenMinionType
		return trig
		
		
class FateWeaver(Minion):
	Class, race, name = "Priest", "Dragon", "Fate Weaver"
	mana, attack, health = 4, 3, 6
	index = "DRAGONS~Priest~Minion~4~3~6~Dragon~Fate Weaver~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: If you've Invoked twice, reduce the Cost of cards in your hand by (1)"
	name_CN = "命运编织者"
	
	def effCanTrig(self):
		self.effectViable = self.Game.Counters.invokes[self.ID] > 1
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if self.Game.Counters.invokes[self.ID] > 1:
			for card in self.Game.Hand_Deck.hands[self.ID]:
				ManaMod(card, changeby=-1, changeto=-1).applies()
			self.Game.Manas.calcMana_All()
		return None
		
		
class GraveRune(Spell):
	Class, school, name = "Priest", "", "Grave Rune"
	requireTarget, mana = True, 4
	index = "DRAGONS~Priest~Spell~4~Grave Rune"
	description = "Give a minion 'Deathrattle: Summon 2 copies of this'"
	name_CN = "墓地符文"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			trig = Summon2CopiesofThis(target)
			target.deathrattles.append(trig)
			if target.onBoard: trig.connect()
		return target
		
class Summon2CopiesofThis(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		newMinions = [type(self.entity)(self.entity.Game, self.entity.ID) for i in range(2)]
		pos = (self.entity.pos, "totheRight")
		self.entity.Game.summon(newMinions, pos, self.entity)
		
		
class Chronobreaker(Minion):
	Class, race, name = "Priest", "Dragon", "Chronobreaker"
	mana, attack, health = 5, 4, 5
	index = "DRAGONS~Priest~Minion~5~4~5~Dragon~Chronobreaker~Deathrattle"
	requireTarget, keyWord, description = False, "", "Deathrattle: If you're holding a Dragon, deal 3 damage to all enemy minions"
	name_CN = "时空破坏者"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [Deal3DamagetoAllEnemyMinions(self)]
		
class Deal3DamagetoAllEnemyMinions(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		if self.entity.Game.Hand_Deck.holdingDragon(self.entity.ID):
			targets = self.entity.Game.minionsonBoard(3-self.entity.ID)
			self.entity.dealsAOE(targets, [3 for minion in targets])
			
	def text(self, CHN):
		return "亡语：如果你的手牌中有龙牌，则对所有敌方随从造成3点伤害" if CHN \
				else "Deathrattle: If you're holding a Dragon, deal 3 damage to all enemy minions"
				
				
class TimeRip(Spell):
	Class, school, name = "Priest", "", "Time Rip"
	requireTarget, mana = True, 5
	index = "DRAGONS~Priest~Spell~5~Time Rip"
	description = "Destroy a minion. Invoke Galakrond"
	name_CN = "时空裂痕"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			if target.onBoard: target.dead = True
			elif target.inHand: self.Game.Hand_Deck.discard(target) #如果随从在手牌中则将其丢弃
		invokeGalakrond(self.Game, self.ID)
		return target
		
		
#加基森的三职业卡可以被迦拉克隆生成。
class GalakrondsWit(HeroPower):
	mana, name, requireTarget = 2, "Galakrond's Wit", False
	index = "Priest~Hero Power~2~Galakrond's Wit"
	description = "Add a random Priest minion to your hand"
	name_CN = "迦拉克隆 的智识"
	def available(self, choice=0):
		return not (self.chancesUsedUp() or self.Game.Hand_Deck.handNotFull(self.ID))
		
	def effect(self, target=None, choice=0):
		curGame = self.Game
		if curGame.mode == 0:
			if curGame.guides:
				minion = curGame.guides.pop(0)
			else:
				minion = npchoice(self.rngPool("Priest Minions"))
				curGame.fixedGuides.append(minion)
			curGame.Hand_Deck.addCardtoHand(minion, self.ID, byType=True)
		return 0
		
		
class GalakrondtheUnspeakable(Galakrond_Hero):
	mana, weapon, description = 7, None, "Battlecry: Destroy a random enemy minion. (Invoke twice to upgrade)"
	Class, name, heroPower, armor = "Priest", "Galakrond, the Unspeakable", GalakrondsWit, 5
	index = "DRAGONS~Priest~Hero Card~7~Galakrond, the Unspeakable~Battlecry~Legendary"
	name_CN = "讳言巨龙 迦拉克隆"
	poolIdentifier = "Priest Minions"
	@classmethod
	def generatePool(cls, Game):
		return "Priest Minions", [value for key, value in Game.ClassCards["Priest"].items() if "~Minion~" in key]
		
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.upgradedGalakrond = GalakrondtheApocalypes_Priest
		self.progress = 0
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if curGame.mode == 0:
			if curGame.guides:
				i = curGame.guides.pop(0)
			else:
				minions = curGame.minionsAlive(3-self.ID)
				i = npchoice(minions).pos if minions else -1
				curGame.fixedGuides.append(i)
			if i > -1: curGame.minions[3-self.ID][i].dead = True
		return None
		
class GalakrondtheApocalypes_Priest(Galakrond_Hero):
	mana, weapon, description = 7, None, "Battlecry: Destroy 2 random enemy minions. (Invoke twice to upgrade)"
	Class, name, heroPower, armor = "Priest", "Galakrond, the Apocalypes", GalakrondsWit, 5
	index = "DRAGONS~Priest~Hero Card~7~Galakrond, the Apocalypes~Battlecry~Legendary~Uncollectible"
	name_CN = "天降浩劫 迦拉克隆"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.upgradedGalakrond = GalakrondAzerothsEnd_Priest
		self.progress = 0
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if curGame.mode == 0:
			if curGame.guides:
				minions = [curGame.minions[3-self.ID][i] for i in curGame.guides.pop(0)]
			else:
				minions = curGame.minionsAlive(3-self.ID)
				minions = npchoice(minions, min(2, len(minions)), replace=False) if minions else ()
				curGame.fixedGuides.append(tuple(minion.pos for minion in minions))
			for minion in minions: curGame.killMinion(self, minion)
		return None
		
class GalakrondAzerothsEnd_Priest(Galakrond_Hero):
	mana, weapon, description = 7, None, "Battlecry: Destroy 4 random enemy minions. Equip a 5/2 Claw"
	Class, name, heroPower, armor = "Priest", "Galakrond, Azeroth's End", GalakrondsWit, 5
	index = "DRAGONS~Priest~Hero Card~7~Galakrond, Azeroth's End~Battlecry~Legendary~Uncollectible"
	name_CN = "世界末日 迦拉克隆"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.upgradedGalakrond = None
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if curGame.mode == 0:
			if curGame.guides:
				minions = [curGame.minions[3-self.ID][i] for i in curGame.guides.pop(0)]
			else:
				minions = curGame.minionsAlive(3-self.ID)
				minions = npchoice(minions, min(4, len(minions)), replace=False) if minions else ()
				curGame.fixedGuides.append(tuple(minion.pos for minion in minions))
			for minion in minions: curGame.killMinion(self, minion)
		curGame.equipWeapon(DragonClaw(curGame, self.ID))
		return None
		
class DragonClaw(Weapon):
	Class, name, description = "Neutral", "Dragon Claw", ""
	mana, attack, durability = 5, 5, 2
	index = "DRAGONS~Neutral~Weapon~5~5~2~Dragon Claw~Uncollectible"
	name_CN = "巨龙之爪"
	
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
	index = "DRAGONS~Priest~Minion~8~8~8~Dragon~Murozond the Infinite~Battlecry~Legendary"
	requireTarget, keyWord, description = False, "", "Battlecry: Play all cards your opponent played last turn"
	name_CN = "永恒巨龙 姆诺兹多"
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
			while cardstoReplay[3-self.ID]:
				card = cardstoReplay[3-self.ID].pop(0)(curGame, self.ID)
				if card.type == "Minion":
					curGame.summon(card, self.pos+1, self)
				elif card.type == "Spell":
					card.cast()
				elif card.type == "Weapon":
					curGame.equipWeapon(card)
				else: #Hero cards. And the HeroClass will change accordingly
					#Replaying Hero Cards can only replace your hero and Hero Power, no battlecry will be triggered
					card.replaceHero()
				curGame.gathertheDead(decideWinner=True)
		return None
		
"""Rogue cards"""
class BloodsailFlybooter(Minion):
	Class, race, name = "Rogue", "Pirate", "Bloodsail Flybooter"
	mana, attack, health = 1, 1, 1
	index = "DRAGONS~Rogue~Minion~1~1~1~Pirate~Bloodsail Flybooter~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Add two 1/1 Pirates to your hand"
	name_CN = "血帆飞贼"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.Game.Hand_Deck.addCardtoHand([SkyPirate, SkyPirate], self.ID, byType=True)
		return None
		
class SkyPirate(Minion):
	Class, race, name = "Rogue", "Pirate", "Sky Pirate"
	mana, attack, health = 1, 1, 1
	index = "DRAGONS~Rogue~Minion~1~1~1~Pirate~Sky Pirate~Uncollectible"
	requireTarget, keyWord, description = False, "", ""
	name_CN = "空中海盗"
	
	
class DragonsHoard(Spell):
	Class, school, name = "Rogue", "", "Dragon's Hoard"
	requireTarget, mana = False, 1
	index = "DRAGONS~Rogue~Spell~1~Dragon's Hoard"
	description = "Discover a Legendary minion from another class"
	name_CN = "巨龙宝藏"
	poolIdentifier = "Druid Legendary Minions"
	@classmethod
	def generatePool(cls, Game):
		return ["%s Legendary Minions"%Class for Class in Game.Classes], \
				[[value for key, value in Game.ClassCards[Class].items() if "~Minion~" in key and "~Legendary" in key] for Class in Game.Classes]
				
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if curGame.mode == 0:
			if curGame.guides:
				curGame.Hand_Deck.addCardtoHand(curGame.guides.pop(0), self.ID, byType=True, byDiscover=True)
			else:
				classes = self.rngPool("Classes")[:]
				try: classes.remove(curGame.heroes[self.ID].Class)
				except: pass
				if self.ID != curGame.turn or "byOthers" in comment:
					minion = npchoice(self.rngPool("%s Legendary Minions"%npchoice(classes)))
					curGame.fixedGuides.append(minion)
					curGame.Hand_Deck.addCardtoHand(minion, self.ID, byType=True, byDiscover=True)
				else:
					classes = npchoice(classes, 3, replace=False)
					minions = [npchoice(self.rngPool("%s Legendary Minions"%Class)) for Class in classes]
					curGame.options = [minion(curGame, self.ID) for minion in minions]
					curGame.Discover.startDiscover(self)
		return None
		
	def discoverDecided(self, option, pool):
		self.Game.fixedGuides.append(type(option))
		self.Game.Hand_Deck.addCardtoHand(option, self.ID, byDiscover=True)
		
		
class PraiseGalakrond(Spell):
	Class, school, name = "Rogue", "", "Praise Galakrond!"
	requireTarget, mana = True, 1
	index = "DRAGONS~Rogue~Spell~1~Praise Galakrond!"
	description = "Give a minion +1 Attack. Invoke Galakrond"
	name_CN = "赞美迦拉克隆"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			target.buffDebuff(1, 0)
		invokeGalakrond(self.Game, self.ID)
		return target
		
		
class SealFate(Spell):
	Class, school, name = "Rogue", "", "Seal Fate"
	requireTarget, mana = True, 3
	index = "DRAGONS~Rogue~Spell~3~Seal Fate"
	description = "Deal 3 damage to an undamaged character. Invoke Galakrond"
	name_CN = "封印命运"
	def text(self, CHN):
		damage = (3 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		return "对一个未受伤的角色造成%d点伤害，祈求迦拉克隆"%damage if CHN else "Deal %d damage to an undamaged character. Invoke Galakrond"%damage
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			damage = (3 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			self.dealsDamage(target, damage)
		invokeGalakrond(self.Game, self.ID)
		return target
		
		
class UmbralSkulker(Minion):
	Class, race, name = "Rogue", "", "Umbral Skulker"
	mana, attack, health = 4, 3, 3
	index = "DRAGONS~Rogue~Minion~4~3~3~~Umbral Skulker~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: If you've Invoked twice, add 3 Coins to your hand"
	name_CN = "幽影潜藏者"
	
	def effCanTrig(self):
		self.effectViable = self.Game.Counters.invokes[self.ID] > 1
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if self.Game.Counters.invokes[self.ID] > 1:
			self.Game.Hand_Deck.addCardtoHand([TheCoin, TheCoin, TheCoin], self.ID, byType=True)
		return None
		
		
class NecriumApothecary(Minion):
	Class, race, name = "Rogue", "", "Necrium Apothecary"
	mana, attack, health = 5, 2, 5
	index = "DRAGONS~Rogue~Minion~5~2~5~~Necrium Apothecary~Combo"
	requireTarget, keyWord, description = False, "", "Combo: Draw a Deathrattle minion from your deck and gain its Deathrattle"
	name_CN = "死金药剂师"
	
	def effCanTrig(self):
		self.effectViable = self.Game.Counters.numCardsPlayedThisTurn[self.ID] > 0
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if curGame.Counters.numCardsPlayedThisTurn[self.ID] > 0:
			if curGame.mode == 0:
				if curGame.guides:
					i = curGame.guides.pop(0)
				else:
					minions = [i for i, card in enumerate(curGame.Hand_Deck.decks[self.ID]) if card.type == "Minion" and card.deathrattles]
					i = npchoice(minions) if minions else -1
					curGame.fixedGuides.append(i)
				if i > -1:
					minion = curGame.Hand_Deck.drawCard(self.ID, i)[0]
					if minion:
						for trig in minion.deathrattles:
							copy = type(trig)(self)
							self.deathrattles.append(copy)
							if self.onBoard: copy.connect()
		return None
		
		
class Stowaway(Minion):
	Class, race, name = "Rogue", "", "Stowaway"
	mana, attack, health = 5, 4, 4
	index = "DRAGONS~Rogue~Minion~5~4~4~~Stowaway~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: If there are cards in your deck that didn't start there, draw 2 of them"
	name_CN = "偷渡者"
	
	def effCanTrig(self):
		return any(card.creator for card in self.Game.Hand_Deck.decks[self.ID])
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		HD = curGame.Hand_Deck
		if curGame.mode == 0:
			for num in range(2):
				if curGame.guides:
					i = curGame.guides.pop(0)
				else:
					createdCards = [i for i, card in enumerate(HD.decks[self.ID]) if card.creator]
					i = npchoice(createdCards) if createdCards else -1
					curGame.fixedGuides.append(i)
				if i > -1: HD.drawCard(self.ID, i)
		return None
		
		
class Waxadred(Minion):
	Class, race, name = "Rogue", "Dragon", "Waxadred"
	mana, attack, health = 5, 7, 5
	index = "DRAGONS~Rogue~Minion~5~7~5~Dragon~Waxadred~Deathrattle~Legendary"
	requireTarget, keyWord, description = False, "", "Deathrattle: Shuffle a Candle into your deck that resummons Waxadred when drawn"
	name_CN = "蜡烛巨龙"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.deathrattles = [ShuffleaCandleintoYourDeck(self)]
		
class ShuffleaCandleintoYourDeck(Deathrattle_Minion):
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		minion = self.entity
		minion.Game.Hand_Deck.shuffleintoDeck(WaxadredsCandle(minion.Game, minion.ID), creator=minion)
		
	def text(self, CHN):
		return "亡语：将一张蜡烛洗入你的牌库" if CHN else "Deathrattle: Shuffle a Candle into your deck"
		
class WaxadredsCandle(Spell):
	Class, school, name = "Rogue", "", "Waxadred's Candle"
	requireTarget, mana = False, 5
	index = "DRAGONS~Rogue~Spell~5~Waxadred's Candle~Casts When Drawn~Uncollectible"
	description = "Casts When Drawn. Summon Waxadred"
	name_CN = "巨龙的蜡烛"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.Game.summon(Waxadred(self.Game, self.ID), -1, self)
		return None
		
		
class CandleBreath(Spell):
	Class, school, name = "Rogue", "Fire", "Candle Breath"
	requireTarget, mana = False, 6
	index = "DRAGONS~Rogue~Spell~6~Fire~Candle Breath"
	description = "Draw 3 cards. Costs (3) less while you're holding a Dragon"
	name_CN = "烛火吐息"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsHand = [Trig_CandleBreath(self)]
		
	def effCanTrig(self):
		self.effectViable = self.Game.Hand_Deck.holdingDragon(self.ID)
		
	def selfManaChange(self):
		if self.inHand and self.Game.Hand_Deck.holdingDragon(self.ID):
			self.mana -= 3
			self.mana = max(0, self.mana)
			
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		for i in range(3): self.Game.Hand_Deck.drawCard(self.ID)
		return None
		
class Trig_CandleBreath(TrigHand):
	def __init__(self, entity):
		self.blank_init(entity, ["CardLeavesHand", "CardEntersHand"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		#Only cards with a different class than your hero class will trigger this
		card = target[0] if signal == "CardEntersHand" else target
		return self.entity.inHand and card.ID == self.entity.ID and card.type == "Minion" and "Dragon" in card.race
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.Game.Manas.calcMana_Single(self.entity)
		
		
class FlikSkyshiv(Minion):
	Class, race, name = "Rogue", "", "Flik Skyshiv"
	mana, attack, health = 6, 4, 4
	index = "DRAGONS~Rogue~Minion~6~4~4~~Flik Skyshiv~Battlecry~Legendary"
	requireTarget, keyWord, description = True, "", "Battlecry: Destroy a minion and all copies of it (wherever they are)"
	name_CN = "菲里克·飞刺"
	def targetExists(self, choice=0):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target != self and target.onBoard
		
	#飞刺的战吼会摧毁所有同名卡，即使有些不是随从，如法师的扰咒术奥秘和随从，镜像法术和其衍生物
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			HD = self.Game.Hand_Deck
			for ID in range(1, 3):
				for minion in self.Game.minionsonBoard(ID):
					if minion.name == target.name: minion.dead = True
				for i in reversed(range(len(HD.decks[ID]))):
					if HD.decks[ID][i].name == target.name: HD.extractfromDeck(i, ID)
				for i in reversed(range(len(HD.hands[ID]))):
					if HD.hands[ID][i].name == target.name: HD.extractfromHand(i, ID, enemyCanSee=True)
		return target
		
		
class GalakrondsGuile(HeroPower):
	mana, name, requireTarget = 2, "Galakrond's Guile", False
	index = "Rogue~Hero Power~2~Galakrond's Guile"
	description = "Add a Lackey to your hand"
	name_CN = "迦拉克隆 的诡计"
	def available(self, choice=0):
		return not (self.chancesUsedUp() or self.Game.Hand_Deck.handNotFull(self.ID))
				
	def effect(self, target=None, choice=0):
		curGame = self.Game
		if curGame.mode == 0:
			if curGame.guides:
				lackey = curGame.guides.pop(0)
			else:
				lackey = npchoice(Lackeys)
				curGame.fixedGuides.append(lackey)
			curGame.Hand_Deck.addCardtoHand(lackey, self.ID, byType=True)
		return 0
		
class GalakrondtheNightmare(Galakrond_Hero):
	mana, weapon, description = 7, None, "Battlecry: Draw a card. It costs (1). (Invoke twice to upgrade)"
	Class, name, heroPower, armor = "Rogue", "Galakrond, the Nightmare", GalakrondsGuile, 5
	index = "DRAGONS~Rogue~Hero Card~7~Galakrond, the Nightmare~Battlecry~Legendary"
	name_CN = "梦魇巨龙 迦拉克隆"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.upgradedGalakrond = GalakrondtheApocalypes_Rogue
		self.progress = 0
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		card, mana = self.Game.Hand_Deck.drawCard(self.ID)
		if card:
			ManaMod(card, changeby=0, changeto=1).applies()
		return None
		
class GalakrondtheApocalypes_Rogue(Galakrond_Hero):
	mana, weapon, description = 7, None, "Battlecry: Draw 2 cards. They cost (1). (Invoke twice to upgrade)"
	Class, name, heroPower, armor = "Rogue", "Galakrond, the Apocalypes", GalakrondsGuile, 5
	index = "DRAGONS~Rogue~Hero Card~7~Galakrond, the Apocalypes~Battlecry~Legendary~Uncollectible"
	name_CN = "天降浩劫 迦拉克隆"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.upgradedGalakrond = GalakrondAzerothsEnd_Rogue
		self.progress = 0
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		for i in range(2):
			card, mana = self.Game.Hand_Deck.drawCard(self.ID)
			if card:
				ManaMod(card, changeby=0, changeto=1).applies()
		return None
		
class GalakrondAzerothsEnd_Rogue(Galakrond_Hero):
	mana, weapon, description = 7, None, "Battlecry: Draw 4 cards. They cost (1). Equip a 5/2 Claw"
	Class, name, heroPower, armor = "Rogue", "Galakrond, Azeroth's End", GalakrondsGuile, 5
	index = "DRAGONS~Rogue~Hero Card~7~Galakrond, Azeroth's End~Battlecry~Legendary~Uncollectible"
	name_CN = "世界末日 迦拉克隆"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.upgradedGalakrond = None
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		for i in range(4):
			card, mana = self.Game.Hand_Deck.drawCard(self.ID)
			if card:
				ManaMod(card, changeby=0, changeto=1).applies()
		self.Game.equipWeapon(DragonClaw(self.Game, self.ID))
		return None
		
"""Shaman cards"""
class InvocationofFrost(Spell):
	Class, school, name = "Shaman", "Frost", "Invocation of Frost"
	requireTarget, mana = True, 2
	index = "DRAGONS~Shaman~Spell~2~Frost~Invocation of Frost"
	description = "Freeze a minion. Invoke Galakrond"
	name_CN = "霜之祈咒"
	def available(self):
		return self.selectableEnemyExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" or target.type == "Hero" and target.onBoard and target.ID != self.ID
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			target.getsFrozen()
		invokeGalakrond(self.Game, self.ID)
		return target
		
		
class SurgingTempest(Minion):
	Class, race, name = "Shaman", "Elemental", "Surging Tempest"
	mana, attack, health = 1, 1, 3
	index = "DRAGONS~Shaman~Minion~1~1~3~Elemental~Surging Tempest"
	requireTarget, keyWord, description = False, "", "Has +1 Attack while you have Overloaded Mana Crystals"
	name_CN = "电涌风暴"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.auras["Buff Aura"] = StatAura_SurgingTempest(self)
		
class StatAura_SurgingTempest:
	def __init__(self, entity):
		self.entity = entity
		self.auraAffected = []
		self.on = False
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and ID == self.entity.ID
		
	def trig(self, signal, ID, subject, target, number, comment, choice=0):
		minion = self.entity
		if minion.onBoard and ID == minion.ID:
			isOverloaded = minion.Game.Manas.manasOverloaded[minion.ID] > 0 or minion.Game.Manas.manasLocked[minion.ID] > 0
			if not isOverloaded and self.on:
				self.on = False
				for recipient, receiver in self.auraAffected[:]:
					receiver.effectClear()
				self.auraAffected = []
			elif isOverloaded and not self.on:
				self.on = True
				Stat_Receiver(minion, self, 1, 0).effectStart()
				
	def auraAppears(self):
		minion = self.entity
		if minion.Game.Manas.manasOverloaded[minion.ID] > 0 or minion.Game.Manas.manasLocked[minion.ID] > 0:
			self.on = True
			Stat_Receiver(minion, self, 1, 0).effectStart()
		try: minion.Game.trigsBoard[minion.ID]["OverloadCheck"].append(self)
		except: minion.Game.trigsBoard[minion.ID]["OverloadCheck"] = [self]
		
	def auraDisappears(self):
		for minion, receiver in self.auraAffected[:]:
			receiver.effectClear()
		self.auraAffected = []
		try: self.entity.Game.trigsBoard[self.entity.ID]["OverloadCheck"].remove(self)
		except: pass
		
	def selfCopy(self, recipient): #The recipientMinion is the minion that deals the Aura.
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
			
			
class Squallhunter(Minion):
	Class, race, name = "Shaman", "Dragon", "Squallhunter"
	mana, attack, health = 4, 5, 7
	index = "DRAGONS~Shaman~Minion~4~5~7~Dragon~Squallhunter~Spell Damage~Overload"
	requireTarget, keyWord, description = False, "", "Spell Damage +2, Overload: (2)"
	name_CN = "猎风巨龙"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.keyWords["Spell Damage"] = 2
		self.overload = 2
		
		
class StormsWrath(Spell):
	Class, school, name = "Shaman", "Nature", "Storm's Wrath"
	requireTarget, mana = False, 1
	index = "DRAGONS~Shaman~Spell~1~Nature~Storm's Wrath~Overload"
	description = "Give your minions +1/+1. Overload: (1)"
	name_CN = "风暴之怒"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.overload = 2
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		for minion in self.Game.minionsonBoard(self.ID):
			minion.buffDebuff(1, 1)
		return None
		
		
class LightningBreath(Spell):
	Class, school, name = "Shaman", "Nature", "Lightning Breath"
	requireTarget, mana = True, 3
	index = "DRAGONS~Shaman~Spell~3~Nature~Lightning Breath"
	description = "Deal 4 damage to a minion. If you're holding a Dragon, also damage its neighbors"
	name_CN = "闪电吐息"
	def effCanTrig(self):
		self.effectViable = self.Game.Hand_Deck.holdingDragon(self.ID)
		
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
		
	def text(self, CHN):
		damage = (4 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		return "对一个随从造成%d点伤害，如果你的手牌中有龙牌，则同样对其相邻的随从造成伤害"%damage if CHN \
				else "Deal %d damage to a minion. If you're holding a Dragon, also damage its neighbors"%damage
				
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			damage = (4 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			if target.onBoard and self.Game.Hand_Deck.holdingDragon(self.ID) and self.Game.neighbors2(target)[0] != []:
				targets = [target] + self.Game.neighbors2(target)[0]
				self.dealsAOE(targets, [damage for minion in targets])
			else:
				self.dealsDamage(target, damage)
		return target
		
		
class Bandersmosh(Minion):
	Class, race, name = "Shaman", "", "Bandersmosh"
	mana, attack, health = 5, 5, 5
	index = "DRAGONS~Shaman~Minion~5~5~5~~Bandersmosh"
	requireTarget, keyWord, description = False, "", "Each turn this is in your hand, transform it into a 5/5 random Legendary minion"
	name_CN = "班德斯莫什"
	poolIdentifier = "Legendary Minions"
	@classmethod
	def generatePool(cls, Game):
		return "Legendary Minions", list(Game.LegendaryMinions.values())
		
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsHand = [Trig_Bandersmosh_PreShifting(self)]
		
class Trig_Bandersmosh_PreShifting(TrigHand):
	def __init__(self, entity):
		self.blank_init(entity, ["TurnStarts"])
		self.makesCardEvanescent = True
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.inHand and ID == self.entity.ID
		
	def text(self, CHN):
		return "在你的回合开始时，变形为一个随机传说随从的5/5复制" if CHN else "Deathrattle: Shuffle two 1/1 Albatross into your opponent's deck"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		curGame = self.entity.Game
		if curGame.mode == 0:
			if curGame.guides:
				minion = curGame.guides.pop(0)
			else:
				minion = npchoice(self.rngPool("Legendary Minions"))(curGame, self.entity.ID)
				curGame.fixedGuides.append(minion)
			minion = minion(curGame, self.entity.ID)
			minion.statReset(5, 5)
			ManaMod(minion, changeby=0, changeto=5).applies()
			trig = Trig_Bandersmosh_KeepShifting(minion)
			trig.connect()
			minion.trigsBoard.append(trig)
			curGame.Hand_Deck.replaceCardinHand(self.entity, minion)
			
class Trig_Bandersmosh_KeepShifting(TrigBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["TurnStarts"])
		self.makesCardEvanescent = True
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.inHand and ID == self.entity.ID
		
	def text(self, CHN):
		return "在你的回合开始时，变形为一个随机传说随从的5/5复制" if CHN else "Deathrattle: Shuffle two 1/1 Albatross into your opponent's deck"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		curGame = self.entity.Game
		if curGame.mode == 0:
			if curGame.guides:
				minion = curGame.guides.pop(0)
			else:
				minion = npchoice(self.rngPool("Legendary Minions"))(curGame, self.entity.ID)
				curGame.fixedGuides.append(minion)
			minion = minion(curGame, self.entity.ID)
			minion.statReset(5, 5)
			ManaMod(minion, changeby=0, changeto=5).applies()
			trig = Trig_Bandersmosh_KeepShifting(minion) #新的扳机保留这个变色龙的原有reference.在对方无手牌时会变回起始的变色龙。
			trig.connect()
			minion.trigsBoard.append(trig)
			curGame.Hand_Deck.replaceCardinHand(self.entity, minion)
			
			
class CumuloMaximus(Minion):
	Class, race, name = "Shaman", "Elemental", "Cumulo-Maximus"
	mana, attack, health = 5, 5, 5
	index = "DRAGONS~Shaman~Minion~5~5~5~Elemental~Cumulo-Maximus~Battlecry"
	requireTarget, keyWord, description = True, "", "Battlecry: If you have Overloaded Mana Crystals, deal 5 damage"
	name_CN = "遮天雨云"
	def returnTrue(self, choice=0):
		return self.Game.Manas.manasLocked[self.ID] + self.Game.Manas.manasOverloaded[self.ID] > 0
		
	def effCanTrig(self):
		if self.Game.Manas.manasLocked[self.ID] + self.Game.Manas.manasOverloaded[self.ID] > 0:
			self.effectViable = self.targetExists()
		else:
			self.effectViable = False
			
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target and self.Game.Manas.manasLocked[self.ID] + self.Game.Manas.manasOverloaded[self.ID] > 0:
			self.dealsDamage(target, 5)
		return target
		
		
class DragonsPack(Spell):
	Class, school, name = "Shaman", "Nature", "Dragon's Pack"
	requireTarget, mana = False, 5
	index = "DRAGONS~Shaman~Spell~5~Nature~Dragon's Pack"
	description = "Summon two 2/3 Spirit Wolves with Taunt. If you've Invoked Galakrond twice, give them +2/+2"
	name_CN = "巨龙的兽群"
	def available(self):
		return self.Game.space(self.ID) > 0
		
	def effCanTrig(self): #法术先检测是否可以使用才判断是否显示黄色
		self.effectViable = self.Game.Counters.invokes[self.ID] > 1
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		minion1, minion2 = SpiritWolf_Dragons(self.Game, self.ID), SpiritWolf_Dragons(self.Game, self.ID)
		self.Game.summon([minion1, minion2], (-1, "totheRightEnd"), self)
		if self.Game.Counters.invokes[self.ID] > 1:
			minion1.buffDebuff(2, 2)
			minion2.buffDebuff(2, 2)
		return None
		
class SpiritWolf_Dragons(Minion):
	Class, race, name = "Shaman", "", "Spirit Wolf"
	mana, attack, health = 2, 2, 3
	index = "DRAGONS~Shaman~Minion~2~2~3~~Spirit Wolf~Taunt~Uncollectible"
	requireTarget, keyWord, description = False, "Taunt", "Taunt"
	name_CN = "幽灵狼"
	
	
class CorruptElementalist(Minion):
	Class, race, name = "Shaman", "", "Corrupt Elementalist"
	mana, attack, health = 6, 3, 3
	index = "DRAGONS~Shaman~Minion~6~3~3~~Corrupt Elementalist~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Invoke Galakrond twice"
	name_CN = "堕落的元素师"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		invokeGalakrond(self.Game, self.ID)
		invokeGalakrond(self.Game, self.ID)
		return None
		
		
class Nithogg(Minion):
	Class, race, name = "Shaman", "Dragon", "Nithogg"
	mana, attack, health = 6, 5, 5
	index = "DRAGONS~Shaman~Minion~6~5~5~Dragon~Nithogg~Battlecry~Legendary"
	requireTarget, keyWord, description = False, "", "Battlecry: Summon two 0/3 Eggs. Next turn they hatch into 4/4 Drakes with Rush"
	name_CN = "尼索格"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		pos = (self.pos, "leftandRight") if self.onBoard else (-1, "totheRightEnd")
		self.Game.summon([StormEgg(self.Game, self.ID) for i in range(2)], pos, self)
		return None
		
class StormEgg(Minion):
	Class, race, name = "Shaman", "", "Storm Egg"
	mana, attack, health = 1, 0, 3
	index = "DRAGONS~Shaman~Minion~1~0~3~~Storm Egg~Uncollectible"
	requireTarget, keyWord, description = False, "", "At the start of your turn, transform into a 4/4 Storm Drake with Rush"
	name_CN = "风暴龙卵"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_StormEgg(self)]
		
class Trig_StormEgg(TrigBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["TurnStarts"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and ID == self.entity.ID
		
	def text(self, CHN):
		return "在你的回合开始时，变形成为一条4/4并具有突袭的风暴幼龙" if CHN \
				else "At the start of your turn, transform into a 4/4 Storm Drake with Rush"
				
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.Game.transform(self.entity, StormDrake(self.entity.Game, self.entity.ID))
		
class StormDrake(Minion):
	Class, race, name = "Shaman", "Dragon", "Storm Drake"
	mana, attack, health = 4, 4, 4
	index = "DRAGONS~Shaman~Minion~4~4~4~Dragon~Storm Drake~Rush~Uncollectible"
	requireTarget, keyWord, description = False, "Rush", "Rush"
	name_CN = "风暴幼龙"
	
	
class GalakrondsFury(HeroPower):
	mana, name, requireTarget = 2, "Galakrond's Fury", False
	index = "Shaman~Hero Power~2~Galakrond's Fury"
	description = "Summon a 2/1 Elemental with Rush"
	name_CN = "迦拉克隆 的愤怒"
	def available(self):
		return not self.chancesUsedUp() and self.Game.space(self.ID)
		
	def effect(self, target=None, choice=0):
		self.Game.summon(WindsweptElemental(self.Game, self.ID), -1, self, "")
		return 0
		
class WindsweptElemental(Minion):
	Class, race, name = "Shaman", "Elemental", "Windswept Elemental"
	mana, attack, health = 2, 2, 1
	index = "DRAGONS~Shaman~Minion~2~2~1~Elemental~Windswept Elemental~Rush~Uncollectible"
	requireTarget, keyWord, description = False, "Rush", "Rush"
	name_CN = "风啸元素"
	
class GalakrondtheTempest(Galakrond_Hero):
	mana, weapon, description = 7, None, "Battlecry: Summon two 2/2 Storms with Rush. (Invoke twice to upgrade)"
	Class, name, heroPower, armor = "Shaman", "Galakrond, the Tempest", GalakrondsFury, 5
	index = "DRAGONS~Shaman~Hero Card~7~Galakrond, the Tempest~Battlecry~Legendary"
	name_CN = "风暴巨龙 迦拉克隆"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.upgradedGalakrond = GalakrondtheApocalypes_Shaman
		self.progress = 0
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.Game.summon([BrewingStorm(self.Game, self.ID) for i in range(2)], (-1, "totheRightEnd"), self)
		return None
		
class GalakrondtheApocalypes_Shaman(Galakrond_Hero):
	mana, weapon, description = 7, None, "Battlecry: Summon two 4/4 Storms with Rush. (Invoke twice to upgrade)"
	Class, name, heroPower, armor = "Shaman", "Galakrond, the Apocalypes", GalakrondsFury, 5
	index = "DRAGONS~Shaman~Hero Card~7~Galakrond, the Apocalypes~Battlecry~Legendary~Uncollectible"
	name_CN = "天降浩劫 迦拉克隆"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.upgradedGalakrond = GalakrondAzerothsEnd_Shaman
		self.progress = 0
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.Game.summon([LivingStorm(self.Game, self.ID) for i in range(2)], (-1, "totheRightEnd"), self)
		return None
		
class GalakrondAzerothsEnd_Shaman(Galakrond_Hero):
	mana, weapon, description = 7, None, "Battlecry: Summon two 8/8 Storms with Rush. Equip a 5/2 Claw"
	Class, name, heroPower, armor = "Shaman", "Galakrond, Azeroth's End", GalakrondsFury, 5
	index = "DRAGONS~Shaman~Hero Card~7~Galakrond, Azeroth's End~Battlecry~Legendary~Uncollectible"
	name_CN = "世界末日 迦拉克隆"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.upgradedGalakrond = None
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.Game.summon([RagingStorm(self.Game, self.ID) for i in range(2)], (-1, "totheRight"), self)
		self.Game.equipWeapon(DragonClaw(self.Game, self.ID))
		return None
		
class BrewingStorm(Minion):
	Class, race, name = "Shaman", "Elemental", "Brewing Storm"
	mana, attack, health = 2, 2, 2
	index = "DRAGONS~Shaman~Minion~2~2~2~Elemental~Brewing Storm~Rush~Uncollectible"
	requireTarget, keyWord, description = False, "Rush", "Rush"
	name_CN = "成型风暴"
	
class LivingStorm(Minion):
	Class, race, name = "Shaman", "Elemental", "Living Storm"
	mana, attack, health = 4, 4, 4
	index = "DRAGONS~Shaman~Minion~4~4~4~Elemental~Living Storm~Rush~Uncollectible"
	requireTarget, keyWord, description = False, "Rush", "Rush"
	name_CN = "活体风暴"
	
class RagingStorm(Minion):
	Class, race, name = "Shaman", "Elemental", "Raging Storm"
	mana, attack, health = 8, 8, 8
	index = "DRAGONS~Shaman~Minion~8~8~8~Elemental~Raging Storm~Rush~Uncollectible"
	requireTarget, keyWord, description = False, "Rush", "Rush"
	name_CN = "狂怒风暴"
	
"""Warlock cards"""
class RainofFire(Spell):
	Class, school, name = "Warlock", "Fel", "Rain of Fire"
	requireTarget, mana = False, 1
	index = "DRAGONS~Warlock~Spell~1~Fel~Rain of Fire"
	description = "Deal 1 damage to all characters"
	name_CN = "火焰之雨"
	def text(self, CHN):
		damage = (1 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		return "对所有角色造成%d点伤害"%damage if CHN else "Deal %d damage to all characters"%damage
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		damage = (1 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		targets = self.Game.minionsonBoard(1) + self.Game.minionsonBoard(2)
		self.dealsAOE(targets, [damage for minion in targets])
		return None
		
		
class NetherBreath(Spell):
	Class, school, name = "Warlock", "Fel", "Nether Breath"
	requireTarget, mana = True, 2
	index = "DRAGONS~Warlock~Spell~2~Fel~Nether Breath"
	description = "Deal 2 damage. If you're holding a Dragon, deal 4 damage with Lifesteal instead"
	name_CN = "虚空吐息"
	def effCanTrig(self):
		self.effectViable = self.Game.Hand_Deck.holdingDragon(self.ID)
		
	def text(self, CHN):
		damage_2 = (2 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		damage_4 = (4 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		return "造成%d点伤害。如果你的手牌中有龙牌，则改为造成%d点伤害并具有吸血"%(damage_2, damage_4) if CHN \
				else "Deal %d damage. If you're holding a Dragon, deal %d damage with Lifesteal instead"%(damage_2, damage_4)
				
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			if self.Game.Hand_Deck.holdingDragon(self.ID):
				damage = (4 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
				self.keyWords["Lifesteal"] = 1
			else:
				damage = (2 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			self.dealsDamage(target, damage)
		return None
		
class DarkSkies(Spell):
	Class, school, name = "Warlock", "Fel", "Dark Skies"
	requireTarget, mana = False, 3
	index = "DRAGONS~Warlock~Spell~3~Fel~Dark Skies"
	description = "Deal 1 damage to a random minion. Repeat for each card in your hand"
	name_CN = "黑暗天际"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		damage = (1 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		curGame = self.Game
		#在使用这个法术后先打一次，然后检测手牌数。总伤害个数是手牌数+1
		minions = curGame.minionsAlive(1) + curGame.minionsAlive(2)
		if minions:
			if curGame.mode == 0:
				if curGame.guides:
					i, where = curGame.guides.pop(0)
					if where: minion = curGame.find(i, where)
				else:
					minion = npchoice(minions)
					curGame.fixedGuides.append((minion.pos, "Minion%d"%minion.ID))
				self.dealsDamage(minion, damage)
				handSize = len(curGame.Hand_Deck.hands[self.ID])
				for num in range(handSize):
					minion = None
					if curGame.guides:
						i, where = curGame.guides.pop(0)
						if where: minion = curGame.find(i, where)
					else:
						minions = self.Game.minionsAlive(1) + self.Game.minionsAlive(2)
						if minions:
							minion = npchoice(minions)
							curGame.fixedGuides.append((minion.pos, "Minion%d"%minion.ID))
						else:
							curGame.fixedGuides.append((0, ''))
					if minion: self.dealsDamage(minion, damage)
					else: break
		return None
		
		
class DragonblightCultist(Minion):
	Class, race, name = "Warlock", "", "Dragonblight Cultist"
	mana, attack, health = 3, 1, 1
	index = "DRAGONS~Warlock~Minion~3~1~1~~Dragonblight Cultist~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Invoke Galakrond. Gain +1 Attack for each other friendly minion"
	name_CN = "龙骨荒野 异教徒"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		invokeGalakrond(self.Game, self.ID)
		if self.onBoard or self.inHand:
			num = len(self.Game.minionsAlive(self.ID, self))
			self.buffDebuff(num, 0)
		return None
		
		
class FiendishRites(Spell):
	Class, school, name = "Warlock", "", "Fiendish Rites"
	requireTarget, mana = False, 4
	index = "DRAGONS~Warlock~Spell~4~Fiendish Rites"
	description = "Invoke Galakrond. Give your minions +1 Attack"
	name_CN = "邪鬼仪式"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		invokeGalakrond(self.Game, self.ID)
		for minion in self.Game.minionsonBoard(self.ID):
			minion.buffDebuff(1, 0)
		return None
		
		
class VeiledWorshipper(Minion):
	Class, race, name = "Warlock", "", "Veiled Worshipper"
	mana, attack, health = 4, 5, 4
	index = "DRAGONS~Warlock~Minion~4~5~4~~Veiled Worshipper~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: If you've Invoked twice, draw 3 cards"
	name_CN = "暗藏的信徒"
	
	def effCanTrig(self):
		self.effectViable = self.Game.Counters.invokes[self.ID] > 1
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if self.Game.Counters.invokes[self.ID] > 1:
			self.Game.Hand_Deck.drawCard(self.ID)
			self.Game.Hand_Deck.drawCard(self.ID)
			self.Game.Hand_Deck.drawCard(self.ID)
		return None
		
		
class CrazedNetherwing(Minion):
	Class, race, name = "Warlock", "Dragon", "Crazed Netherwing"
	mana, attack, health = 5, 5, 5
	index = "DRAGONS~Warlock~Minion~5~5~5~Dragon~Crazed Netherwing~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: If you're holding a Dragon, deal 3 dammage to all other characters"
	name_CN = "疯狂的灵翼龙"
	def effCanTrig(self):
		self.effectViable = self.Game.Hand_Deck.holdingDragon(self.ID, self)
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if self.Game.Hand_Deck.holdingDragon(self.ID):
			targets = [self.Game.heroes[1], self.Game.heroes[2]] + self.Game.minionsonBoard(self.ID, self) + self.Game.minionsonBoard(3-self.ID)
			self.dealsAOE(targets, [3 for minion in targets])
		return None
		
		
class AbyssalSummoner(Minion):
	Class, race, name = "Warlock", "", "Abyssal Summoner"
	mana, attack, health = 6, 2, 2
	index = "DRAGONS~Warlock~Minion~6~2~2~~Abyssal Summoner~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Summon a Demon with Taunt and stats equal to your hand size"
	name_CN = "深渊召唤者"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		handSize = len(self.Game.Hand_Deck.hands[self.ID])
		if handSize == 1:
			self.Game.summon(AbyssalDestroyer(self.Game, self.ID), self.pos+1, self)
		elif handSize > 1:
			cost = min(handSize, 10)
			newIndex = "DRAGONS~Warlock~Minion~%d~%d~%d~Demon~Abyssal Destroyer~Taunt~Uncollectible"%(cost, handSize, handSize)
			subclass = type("AbyssalDestroyer__"+str(handSize), (AbyssalDestroyer, ),
							{"mana": cost, "attack": handSize, "health": handSize,
							"index": newIndex}
							)
			self.Game.cardPool[newIndex] = subclass
			self.Game.summon(subclass(self.Game, self.ID), self.pos+1, self)
		return None
		
class AbyssalDestroyer(Minion):
	Class, race, name = "Warlock", "Demon", "Abyssal Destroyer"
	mana, attack, health = 1, 1, 1
	index = "DRAGONS~Warlock~Minion~1~1~1~Demon~Abyssal Destroyer~Taunt~Uncollectible"
	requireTarget, keyWord, description = False, "Taunt", "Taunt"
	name_CN = "深渊毁灭者"
	
	
class GalakrondsMalice(HeroPower):
	mana, name, requireTarget = 2, "Galakrond's Malice", False
	index = "Shaman~Hero Power~2~Galakrond's Malice"
	description = "Summon two 1/1 Imps"
	name_CN = "迦拉克隆 的恶意"
	def available(self):
		return not self.chancesUsedUp() and self.Game.space(self.ID)
		
	def effect(self, target=None, choice=0):
		self.Game.summon([DraconicImp(self.Game, self.ID) for i in range(2)], (-1, "totheRightEnd"), self, "")
		return 0
		
class GalakrondtheWretched(Galakrond_Hero):
	mana, weapon, description = 7, None, "Battlecry: Summon a random Demon. (Invoke twice to upgrade)"
	Class, name, heroPower, armor = "Warlock", "Galakrond, the Wretched", GalakrondsMalice, 5
	index = "DRAGONS~Warlock~Hero Card~7~Galakrond, the Wretched~Battlecry~Legendary"
	name_CN = "邪火巨龙 迦拉克隆"
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
				demon = npchoice(self.rngPool("Demons to Summon"))
				curGame.fixedGuides.append(demon)
			curGame.summon(demon(curGame, self.ID), -1, self)
		return None
		
class GalakrondtheApocalypes_Warlock(Galakrond_Hero):
	mana, weapon, description = 7, None, "Battlecry: Summon 2 random Demons. (Invoke twice to upgrade)"
	Class, name, heroPower, armor = "Warlock", "Galakrond, the Apocalypes", GalakrondsMalice, 5
	index = "DRAGONS~Warlock~Hero Card~7~Galakrond, the Apocalypes~Battlecry~Legendary~Uncollectible"
	name_CN = "天降浩劫 迦拉克隆"
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
				demons = npchoice(self.rngPool("Demons to Summon"), 2, replace=False)
				curGame.fixedGuides.append(tuple(demons))
			curGame.summon([demon(curGame, self.ID) for demon in demons], (-1, "totheRightEnd"), self)
		return None
		
class GalakrondAzerothsEnd_Warlock(Galakrond_Hero):
	mana, weapon, description = 7, None, "Battlecry: Summon 4 random Demons. Equip a 5/2 Claw"
	Class, name, heroPower, armor = "Warlock", "Galakrond, Azeroth's End", GalakrondsMalice, 5
	index = "DRAGONS~Warlock~Hero Card~7~Galakrond, Azeroth's End~Battlecry~Legendary~Uncollectible"
	name_CN = "世界末日 迦拉克隆"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.upgradedGalakrond = None
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if curGame.mode == 0:
			if curGame.guides:
				demons = list(curGame.guides.pop(0))
			else:
				demons = npchoice(self.rngPool("Demons to Summon"), 4, replace=True)
				curGame.fixedGuides.append(tuple(demons))
			curGame.summon([demon(curGame, self.ID) for demon in demons], (-1, "totheRightEnd"), self)
		curGame.equipWeapon(DragonClaw(curGame, self.ID))
		return None
		
class DraconicImp(Minion):
	Class, race, name = "Warlock", "Demon", "Draconic Imp"
	mana, attack, health = 1, 1, 1
	index = "DRAGONS~Warlock~Minion~1~1~1~Demon~Draconic Imp~Uncollectible"
	requireTarget, keyWord, description = False, "", ""
	name_CN = "龙裔小鬼"
	
	
class ValdrisFelgorge(Minion):
	Class, race, name = "Warlock", "", "Valdris Felgorge"
	mana, attack, health = 7, 4, 4
	index = "DRAGONS~Warlock~Minion~7~4~4~~Valdris Felgorge~Battlecry~Legendary"
	requireTarget, keyWord, description = False, "", "Battlecry: Increase your maximum hand size to 12. Draw 4 cards"
	name_CN = "瓦迪瑞斯·邪噬"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.Game.Hand_Deck.handUpperLimit[self.ID] = 12
		for i in range(4): self.Game.Hand_Deck.drawCard(self.ID)
		return None
		
		
class ZzerakutheWarped(Minion):
	Class, race, name = "Warlock", "Dragon", "Zzeraku the Warped"
	mana, attack, health = 8, 4, 12
	index = "DRAGONS~Warlock~Minion~8~4~12~Dragon~Zzeraku the Warped~Legendary"
	requireTarget, keyWord, description = False, "", "Whenever your hero takes damage, summon a 6/6 Nether Drake"
	name_CN = "扭曲巨龙 泽拉库"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_ZzerakutheWarped(self)]
		
class Trig_ZzerakutheWarped(TrigBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["HeroTakesDmg"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return target == self.entity.Game.heroes[self.entity.ID]
		
	def text(self, CHN):
		return "每当你的英雄受到伤害，召唤一条6/6的虚空幼龙" if CHN else "Whenever your hero takes damage, summon a 6/6 Nether Drake"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.Game.summon(NetherDrake(self.entity.Game, self.entity.ID), self.entity.pos+1, self.entity)
		
class NetherDrake(Minion):
	Class, race, name = "Warlock", "Dragon", "Nether Drake"
	mana, attack, health = 6, 6, 6
	index = "DRAGONS~Warlock~Minion~6~6~6~Dragon~Nether Drake~Uncollectible"
	requireTarget, keyWord, description = False, "", ""
	name_CN = "虚空幼龙"
	
"""Warrior cards"""
class SkyRaider(Minion):
	Class, race, name = "Warrior", "Pirate", "Sky Raider"
	mana, attack, health = 1, 1, 2
	index = "DRAGONS~Warrior~Minion~1~1~2~Pirate~Sky Raider~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Add a random Pirate to your hand"
	name_CN = "空中悍匪"
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
				pirate = npchoice(self.rngPool("Pirates"))
				curGame.fixedGuides.append(pirate)
			curGame.Hand_Deck.addCardtoHand(pirate, self.ID, byType=True)
		return None
		
		
class RitualChopper(Weapon):
	Class, name, description = "Warrior", "Ritual Chopper", "Battlecry: Invoke Galakrond"
	mana, attack, durability = 2, 1, 2
	index = "DRAGONS~Warrior~Weapon~2~1~2~Ritual Chopper~Battlecry"
	name_CN = "仪式斩斧"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		invokeGalakrond(self.Game, self.ID)
		return None
		
		
class Awaken(Spell):
	Class, school, name = "Warrior", "", "Awaken!"
	requireTarget, mana = False, 3
	index = "DRAGONS~Warrior~Spell~3~Awaken!"
	description = "Invoke Galakrond. Deal 1 damage to all minions"
	name_CN = "祈求觉醒"
	def text(self, CHN):
		damage = (1 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		return "祈求迦拉克隆，对所有随从造成1点伤害"%damage if CHN \
				else "Invoke Galakrond. Deal %d damage to all minions"%damage
				
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		damage = (1 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		invokeGalakrond(self.Game, self.ID)
		targets = self.Game.minionsonBoard(self.ID) + self.Game.minionsonBoard(3-self.ID)
		self.dealsAOE(targets, [damage for minion in targets])
		return None
		
		
class Ancharrr(Weapon):
	Class, name, description = "Warrior", "Ancharrr", "After your hero attacks, draw a Pirate from your deck"
	mana, attack, durability = 3, 2, 2
	index = "DRAGONS~Warrior~Weapon~3~2~2~Ancharrr~Legendary"
	name_CN = "海盗之锚"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_Ancharrr(self)]
		
class Trig_Ancharrr(TrigBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["BattleFinished"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return subject == self.entity.Game.heroes[self.entity.ID] and self.entity.onBoard
		
	def text(self, CHN):
		return "在你的英雄攻击后，从你的牌库中抽一张海盗牌" if CHN else "After your hero attacks, draw a Pirate from your deck"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		curGame = self.entity.Game
		if curGame.mode == 0:
			if curGame.guides:
				i = curGame.guides.pop(0)
			else:
				pirates = [i for i, card in enumerate(curGame.Hand_Deck.decks[self.entity.ID]) if card.type == "Minion" and "Pirate" in card.race]
				i = npchoice(pirates) if pirates else -1
				curGame.fixedGuides.append(i)
			if i > -1: curGame.Hand_Deck.drawCard(self.entity.ID, i)
			
			
class EVILQuartermaster(Minion):
	Class, race, name = "Warrior", "", "EVIL Quartermaster"
	mana, attack, health = 3, 2, 3
	index = "DRAGONS~Warrior~Minion~3~2~3~~EVIL Quartermaster~Battlecry"
	requireTarget, keyWord, description = False, "", "Battlecry: Add a Lackey to your hand. Gain 3 Armor"
	name_CN = "怪盗军需官"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if curGame.mode == 0:
			if curGame.guides:
				lackey = curGame.guides.pop(0)
			else:
				lackey = npchoice(Lackeys)
				curGame.fixedGuides.append(lackey)
			curGame.Hand_Deck.addCardtoHand(lackey, self.ID, byType=True)
		curGame.heroes[self.ID].gainsArmor(3)
		return None
		
		
class RammingSpeed(Spell):
	Class, school, name = "Warrior", "", "Ramming Speed"
	requireTarget, mana = True, 3
	index = "DRAGONS~Warrior~Spell~3~Ramming Speed"
	description = "Force a minion to attack one of its neighbors"
	name_CN = "横冲直撞"
	def targetExists(self, choice=0):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard and target.health > 0 and target.dead == False
		
	#不知道目标随从不在手牌中时是否会有任何事情发生
	#不会消耗随从的攻击机会
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target and target.onBoard and target.health > 0 and not target.dead:
			curGame = self.Game
			if curGame.mode == 0:
				neighbor = None
				if curGame.guides:
					i, where = curGame.guides.pop(0)
					if where: neighbor = curGame.find(i, where)
				else:
					neighbors = curGame.neighbors2(target)[0]
					if neighbors:
						neighbor = npchoice(neighbors)
						curGame.fixedGuides.append((neighbor.pos, "Minion%d"%neighbor.ID))
					else:
						curGame.fixedGuides.append((0, ''))
				if neighbor: curGame.battle(target, neighbor, verifySelectable=False, useAttChance=False, resolveDeath=False)
		return target
		
		
class ScionofRuin(Minion):
	Class, race, name = "Warrior", "Dragon", "Scion of Ruin"
	mana, attack, health = 4, 3, 2
	index = "DRAGONS~Warrior~Minion~4~3~2~Dragon~Scion of Ruin~Rush~Battlecry"
	requireTarget, keyWord, description = False, "Rush", "Rush. Battlecry: If you've Invoked twice, summon two copies of this"
	name_CN = "废墟之子"
	
	def effCanTrig(self):
		self.effectViable = self.Game.Counters.invokes[self.ID] > 1
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if self.Game.Counters.invokes[self.ID] > 1:
			if self.onBoard:
				copies = [self.selfCopy(self.ID, self), self.selfCopy(self.ID, self)]
				self.Game.summon(copies, (self.pos, "leftandRight"), self)
			else: #假设废墟之子在战吼前死亡或者离场，则召唤基础复制
				copies = [ScionofRuin(self.Game, self.ID) for i in range(2)]
				self.Game.summon(copies, (-1, "totheRightEnd"), self)
		return None
		
		
class Skybarge(Minion):
	Class, race, name = "Warrior", "Mech", "Skybarge"
	mana, attack, health = 3, 2, 5
	index = "DRAGONS~Warrior~Minion~3~2~5~Mech~Skybarge"
	requireTarget, keyWord, description = False, "", "After you summon a Pirate, deal 2 damage to a random enemy"
	name_CN = "空中炮艇"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_Skybarge(self)]
		
class Trig_Skybarge(TrigBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionBeenSummoned"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and subject.ID == self.entity.ID and "Pirate" in subject.race
		
	def text(self, CHN):
		return "在你召唤一个海盗后，随机对一个敌人造成2点伤害" if CHN \
				else "After you summon a Pirate, deal 2 damage to a random enemy"
				
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		curGame = self.entity.Game
		if curGame.mode == 0:
			char = None
			if curGame.guides:
				i, where = curGame.guides.pop(0)
				if where: char = curGame.find(i, where)
			else:
				chars = curGame.charsAlive(3-self.entity.ID)
				if chars:
					char = npchoice(chars)
					curGame.fixedGuides.append((char.pos, char.type+str(char.ID)))
				else:
					curGame.fixedGuides.append((0, ''))
			if char: self.entity.dealsDamage(char, 2)
			
			
class MoltenBreath(Spell):
	Class, school, name = "Warrior", "Fire", "Molten Breath"
	requireTarget, mana = True, 4
	index = "DRAGONS~Warrior~Spell~4~Fire~Molten Breath"
	description = "Deal 5 damage to a minion. If you're holding Dragon, gain 5 Armor"
	name_CN = "熔火吐息"
	def effCanTrig(self):
		self.effectViable = self.Game.Hand_Deck.holdingDragon(self.ID)
		
	def targetExists(self, choice=0):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target.onBoard
		
	def text(self, CHN):
		damage = (5 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		return "对一个随从造成%d点伤害，如果你的手牌中有龙牌，便获得5点护甲值"%damage if CHN \
				else "Deal %d damage to a minion. If you're holding Dragon, gain 5 Armor"%damage
				
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target:
			damage = (5 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			self.dealsDamage(target, damage)
			if self.Game.Hand_Deck.holdingDragon(self.ID) and self.Game.Hand_Deck.handNotFull(self.ID):
				self.Game.heroes[self.ID].gainsArmor(5)
		return target
		
		
class GalakrondsMight(HeroPower):
	mana, name, requireTarget = 2, "Galakrond's Might", False
	index = "Rogue~Hero Power~2~Galakrond's Might"
	description = "Give your hero +3 Attack this turn"
	name_CN = "迦拉克隆之力"
	def effect(self, target=None, choice=0):
		self.Game.heroes[self.ID].gainAttack(3)
		return 0
		
class GalakrondtheUnbreakable(Galakrond_Hero):
	mana, weapon, description = 7, None, "Battlecry: Draw 1 minion. Give it +4/+4. (Invoke twice to upgrade)"
	Class, name, heroPower, armor = "Warrior", "Galakrond, the Unbreakable", GalakrondsMight, 5
	index = "DRAGONS~Warrior~Hero Card~7~Galakrond, the Unbreakable~Battlecry~Legendary"
	name_CN = "无敌巨龙 迦拉克隆"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.upgradedGalakrond = GalakrondtheApocalypes_Warrior
		self.progress = 0
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if curGame.mode == 0:
			if curGame.guides:
				i = curGame.guides.pop(0)
			else:
				minions = [i for i, card in enumerate(curGame.Hand_Deck.decks[self.ID]) if card.type == "Minion"]
				i = npchoice(minions) if minions else -1
				curGame.fixedGuides.append(i)
			if i > -1:
				minion = curGame.Hand_Deck.drawCard(self.ID, i)[0]
				if minion: minion.buffDebuff(4, 4)
		return None
		
class GalakrondtheApocalypes_Warrior(Galakrond_Hero):
	mana, weapon, description = 7, None, "Battlecry: Draw 2 minions. Give them +4/+4. (Invoke twice to upgrade)"
	Class, name, heroPower, armor = "Warrior", "Galakrond, the Apocalypes", GalakrondsMight, 5
	index = "DRAGONS~Warrior~Hero Card~7~Galakrond, the Apocalypes~Battlecry~Legendary~Uncollectible"
	name_CN = "天降浩劫 迦拉克隆"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.upgradedGalakrond = GalakrondAzerothsEnd_Warrior
		self.progress = 0
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if curGame.mode == 0:
			for num in range(2):
				if curGame.guides:
					i = curGame.guides.pop(0)
				else:
					minions = [i for i, card in enumerate(curGame.Hand_Deck.decks[self.ID]) if card.type == "Minion"]
					i = npchoice(minions) if minions else -1
					curGame.fixedGuides.append(i)
				if i > -1:
					minion = curGame.Hand_Deck.drawCard(self.ID, i)[0]
					if minion: minion.buffDebuff(4, 4)
				else: break
		return None
		
class GalakrondAzerothsEnd_Warrior(Galakrond_Hero):
	mana, weapon, description = 7, None, "Battlecry: Draw 4 minions. Give them +4/+4. Equip a 5/2 Claw"
	Class, name, heroPower, armor = "Warrior", "Galakrond, Azeroth's End", GalakrondsMight, 5
	index = "DRAGONS~Warrior~Hero Card~7~Galakrond, Azeroth's End~Battlecry~Legendary~Uncollectible"
	name_CN = "世界末日 迦拉克隆"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.upgradedGalakrond = None
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		ownDeck = curGame.Hand_Deck.decks[self.ID]
		if curGame.mode == 0:
			for num in range(4):
				if curGame.guides:
					i = curGame.guides.pop(0)
				else:
					minions = [i for i, card in enumerate(ownDeck) if card.type == "Minion"]
					i = npchoice(minions) if minions else -1
					curGame.fixedGuides.append(i)
				if i > -1:
					minion = curGame.Hand_Deck.drawCard(self.ID, i)[0]
					if minion: minion.buffDebuff(4, 4)
				else: break
		curGame.equipWeapon(DragonClaw(curGame, self.ID))
		return None
		
		
#这个战吼的攻击会消耗随从的攻击次数。在战吼结束后给其加上冲锋或者突袭时，其不能攻击
#战吼的攻击可以正常触发奥秘和攻击目标指向扳机
#攻击过程中死亡之翼濒死会停止攻击，但是如果中途被冰冻是不会停止攻击的。即用战斗不检查攻击的合法性。
#战吼结束之后才会进行战斗的死亡结算，期间被攻击的随从可以降到负血量还留在场上。
class DeathwingMadAspect(Minion):
	Class, race, name = "Warrior", "Dragon", "Deathwing, Mad Aspect"
	mana, attack, health = 8, 12, 12
	index = "DRAGONS~Warrior~Minion~8~12~12~Dragon~Deathwing, Mad Aspect~Battlecry~Legendary"
	requireTarget, keyWord, description = False, "", "Battlecry: Attack ALL other minions"
	name_CN = "疯狂巨龙 死亡之翼"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		curGame = self.Game
		if curGame.mode == 0:
			if curGame.guides:
				infos = list(curGame.guides.pop(0))
				if infos:
					while infos:
						i, where = infos.pop(0)
						minion = curGame.find(i, where)
						curGame.battle(curGame.minionPlayed, minion, verifySelectable=False, useAttChance=True, resolveDeath=False, resetRedirTrig=False)
					curGame.sendSignal("BattleFinished", self.Game.turn, self, None, 0, "")
			else:
				minions = curGame.minionsAlive(self.ID, curGame.minionPlayed) + curGame.minionsAlive(3-self.ID)
				npshuffle(minions)
				if minions:
					infos = []
					while minions:
						minion = minions.pop(0)
						if minion.onBoard and minion.health > 0 and not minion.dead:
							infos.append((minion.pos, "Minion%d"%minion.ID))
							curGame.battle(curGame.minionPlayed, minion, verifySelectable=False, useAttChance=True, resolveDeath=False, resetRedirTrig=False)
					curGame.fixedGuides.append(tuple(infos))
				else: curGame.fixedGuides.append(())
		return None
		
		
		
Dragons_Indices = {"DRAGONS~Neutral~Minion~1~2~2~~Blazing Battlemage": BlazingBattlemage,
					"DRAGONS~Neutral~Minion~1~0~5~~Depth Charge": DepthCharge,
					"DRAGONS~Neutral~Minion~1~1~2~Mech~Hot Air Balloon": HotAirBalloon,
					"DRAGONS~Neutral~Minion~2~2~1~Beast~Evasive Chimaera~Poisonous": EvasiveChimaera,
					"DRAGONS~Neutral~Minion~2~2~3~~Dragon Breeder~Battlecry": DragonBreeder,
					"DRAGONS~Neutral~Minion~2~3~2~~Grizzled Wizard~Battlecry": GrizzledWizard,
					"DRAGONS~Neutral~Minion~2~2~2~Pirate~Parachute Brigand": ParachuteBrigand,
					"DRAGONS~Neutral~Minion~2~2~2~Murloc~Tasty Flyfish~Deathrattle": TastyFlyfish,
					"DRAGONS~Neutral~Minion~2~2~3~~Transmogrifier": Transmogrifier,
					"DRAGONS~Neutral~Minion~2~3~2~~Wyrmrest Purifier~Battlecry": WyrmrestPurifier,
					"DRAGONS~Neutral~Minion~3~3~4~~Blowtorch Saboteur~Battlecry": BlowtorchSaboteur,
					"DRAGONS~Neutral~Minion~3~3~4~Beast~Dread Raven": DreadRaven,
					"DRAGONS~Neutral~Minion~3~1~3~Elemental~Fire Hawk~Battlecry": FireHawk,
					"DRAGONS~Neutral~Minion~3~3~3~~Goboglide Tech~Battlecry": GoboglideTech,
					"DRAGONS~Neutral~Minion~3~3~4~Elemental~Living Dragonbreath": LivingDragonbreath,
					"DRAGONS~Neutral~Minion~3~3~3~~Scalerider~Battlecry": Scalerider,
					"DRAGONS~Neutral~Minion~4~4~3~Beast~Bad Luck Albatross~Deathrattle": BadLuckAlbatross,
					"DRAGONS~Neutral~Minion~1~1~1~Beast~Albatross~Uncollectible": Albatross,
					"DRAGONS~Neutral~Minion~4~2~2~~Devoted Maniac~Rush~Battlecry": DevotedManiac,
					"DRAGONS~Neutral~Minion~4~4~4~~Dragonmaw Poacher~Battlecry": DragonmawPoacher,
					"DRAGONS~Neutral~Minion~4~5~4~Dragon~Evasive Feywing": EvasiveFeywing,
					"DRAGONS~Neutral~Minion~4~5~4~~Frizz Kindleroost~Battlecry~Legendary": FrizzKindleroost,
					"DRAGONS~Neutral~Minion~4~2~6~Beast~Hippogryph~Rush~Taunt": Hippogryph,
					"DRAGONS~Neutral~Minion~4~4~2~Pirate~Hoard Pillager~Battlecry": HoardPillager,
					"DRAGONS~Neutral~Minion~4~3~3~~Troll Batrider~Battlecry": TrollBatrider,
					"DRAGONS~Neutral~Minion~4~2~5~~Wing Commander": WingCommander,
					"DRAGONS~Neutral~Minion~4~3~9~~Zul'Drak Ritualist~Taunt~Battlecry": ZulDrakRitualist,
					"DRAGONS~Neutral~Minion~5~5~5~Dragon~Big Ol' Whelp~Battlecry": BigOlWhelp,
					"DRAGONS~Neutral~Minion~5~0~3~~Chromatic Egg~Battlecry~Deathrattle": ChromaticEgg,
					"DRAGONS~Neutral~Minion~5~3~5~Dragon~Cobalt Spellkin~Battlecry": CobaltSpellkin,
					"DRAGONS~Neutral~Minion~5~4~4~~Faceless Corruptor~Rush~Battlecry": FacelessCorruptor,
					"DRAGONS~Neutral~Minion~5~4~4~Pirate~Kobold Stickyfinger~Battlecry": KoboldStickyfinger,
					"DRAGONS~Neutral~Minion~5~5~5~~Platebreaker~Battlecry": Platebreaker,
					"DRAGONS~Neutral~Minion~5~4~5~~Shield of Galakrond~Taunt~Battlecry": ShieldofGalakrond,
					"DRAGONS~Neutral~Minion~5~3~3~Murloc~Skyfin~Battlecry": Skyfin,
					"DRAGONS~Neutral~Minion~5~6~5~~Tentacled Menace~Battlecry": TentacledMenace,
					"DRAGONS~Neutral~Minion~6~6~6~Mech~Camouflaged Dirigible~Battlecry": CamouflagedDirigible,
					"DRAGONS~Neutral~Minion~6~5~3~Dragon~Evasive Wyrm~Divine Shield~Rush": EvasiveWyrm,
					"DRAGONS~Neutral~Minion~6~4~5~Mech~Gyrocopter~Rush~Windfury": Gyrocopter,
					"DRAGONS~Neutral~Minion~6~6~6~~Kronx Dragonhoof~Battlecry~Legendary": KronxDragonhoof,
					"DRAGONS~Neutral~Minion~8~8~8~Dragon~Reanimated Dragon~Uncollectible": ReanimatedDragon,
					"DRAGONS~Neutral~Minion~6~5~5~~Utgarde Grapplesniper~Battlecry": UtgardeGrapplesniper,
					"DRAGONS~Neutral~Minion~7~7~7~Dragon~Evasive Drakonid~Taunt": EvasiveDrakonid,
					"DRAGONS~Neutral~Minion~7~1~7~~Shu'ma~Legendary": Shuma,
					"DRAGONS~Neutral~Minion~1~1~1~~Tentacle~Uncollectible": Tentacle_Dragons,
					"DRAGONS~Neutral~Minion~8~4~10~Dragon~Twin Tyrant~Battlecry": TwinTyrant,
					"DRAGONS~Neutral~Minion~9~8~8~Dragon~Dragonqueen Alexstrasza~Battlecry~Legendary": DragonqueenAlexstrasza,
					"DRAGONS~Neutral~Minion~9~5~5~Demon~Sathrovarr~Battlecry~Legendary": Sathrovarr,
					"DRAGONS~Druid~Spell~0~Embiggen": Embiggen,
					"DRAGONS~Druid~Spell~1~Secure the Deck~~Quest": SecuretheDeck,
					"DRAGONS~Druid~Spell~1~Strength in Numbers~~Quest": StrengthinNumbers,
					"DRAGONS~Druid~Spell~1~Treenforcements~Choose One": Treenforcements,
					"DRAGONS~Druid~Spell~1~Small Repairs~Uncollectible": SmallRepairs,
					"DRAGONS~Druid~Spell~1~Spin 'em Up~Uncollectible": SpinemUp,
					"DRAGONS~Druid~Spell~2~Breath of Dreams": BreathofDreams,
					"DRAGONS~Druid~Minion~2~1~1~~Shrubadier~Battlecry": Shrubadier,
					"DRAGONS~Druid~Minion~2~2~2~~Treant~Uncollectible": Treant_Dragons,
					"DRAGONS~Druid~Spell~5~Aeroponics": Aeroponics,
					"DRAGONS~Druid~Minion~6~4~8~Dragon~Emerald Explorer~Taunt~Battlecry": EmeraldExplorer,
					"DRAGONS~Druid~Minion~7~5~10~~Goru the Mightree~Taunt~Battlecry~Legendary": GorutheMightree,
					"DRAGONS~Druid~Minion~9~4~12~Dragon~Ysera, Unleashed~Battlecry~Legendary": YseraUnleashed,
					"DRAGONS~Druid~Spell~9~Dream Portal~Casts When Drawn~Uncollectible": DreamPortal,
					"DRAGONS~Hunter~Spell~1~Clear the Way~~Quest": CleartheWay,
					"DRAGONS~Hunter~Minion~4~4~4~Beast~Gryphon~Rush~Uncollectible": Gryphon_Dragons,
					"DRAGONS~Hunter~Minion~1~1~3~~Dwarven Sharpshooter": DwarvenSharpshooter,
					"DRAGONS~Hunter~Spell~1~Toxic Reinforcements~~Quest": ToxicReinforcements,
					"DRAGONS~Neutral~Minion~1~1~1~~Leper Gnome~Deathrattle~Uncollectible": LeperGnome_Dragons,
					"DRAGONS~Hunter~Spell~2~Corrosive Breath": CorrosiveBreath,
					"DRAGONS~Hunter~Minion~2~2~3~Beast~Phase Stalker": PhaseStalker,
					"DRAGONS~Hunter~Minion~3~4~1~Beast~Diving Gryphon~Rush~Battlecry": DivingGryphon,
					"DRAGONS~Hunter~Minion~3~2~3~Dragon~Primordial Explorer~Poisonous~Battlecry": PrimordialExplorer,
					"DRAGONS~Hunter~Weapon~3~3~2~Stormhammer": Stormhammer,
					"DRAGONS~Hunter~Minion~4~3~5~Mech~Dragonbane~Legendary": Dragonbane,
					"DRAGONS~Hunter~Minion~6~7~6~Dragon~Veranus~Battlecry~Legendary": Veranus,
					"DRAGONS~Mage~Spell~1~Arcane Breath": ArcaneBreath,
					"DRAGONS~Mage~Spell~1~Elemental Allies~~Quest": ElementalAllies,
					"DRAGONS~Mage~Spell~1~Learn Draconic~~Quest": LearnDraconic,
					"DRAGONS~Mage~Minion~6~6~6~Dragon~Draconic Emissary~Uncollectible": DraconicEmissary,
					"DRAGONS~Mage~Minion~1~1~1~Elemental~Violet Spellwing~Deathrattle": VioletSpellwing,
					"DRAGONS~Mage~Minion~3~2~5~Elemental~Chenvaala~Legendary": Chenvaala,
					"DRAGONS~Mage~Minion~5~5~5~Elemental~Snow Elemental~Uncollectible": SnowElemental,
					"DRAGONS~Mage~Minion~4~2~3~Dragon~Azure Explorer~Spell Damage~Battlecry": AzureExplorer,
					"DRAGONS~Mage~Spell~0~Malygos's Frostbolt~Legendary~Uncollectible": MalygossFrostbolt,
					"DRAGONS~Mage~Spell~1~Malygos's Missiles~Legendary~Uncollectible": MalygossMissiles,
					"DRAGONS~Mage~Spell~1~Malygos's Nova~Legendary~Uncollectible": MalygossNova,
					"DRAGONS~Mage~Spell~1~Malygos's Polymorph~Legendary~Uncollectible": MalygossPolymorph,
					"DRAGONS~Mage~Spell~1~Malygos's Tome~Legendary~Uncollectible": MalygossTome,
					"DRAGONS~Mage~Spell~2~Malygos's Explosion~Legendary~Uncollectible": MalygossExplosion,
					"DRAGONS~Mage~Spell~3~Malygos's Intellect~Legendary~Uncollectible": MalygossIntellect,
					"DRAGONS~Mage~Spell~4~Malygos's Fireball~Legendary~Uncollectible": MalygossFireball,
					"DRAGONS~Mage~Spell~7~Malygos's Flamestrike~Legendary~Uncollectible": MalygossFlamestrike,
					"DRAGONS~Mage~Minion~1~1~1~Beast~Malygos's Sheep~Legendary~Uncollectible": MalygossSheep,
					"DRAGONS~Mage~Minion~5~2~8~Dragon~Malygos, Aspect of Magic~Battlecry~Legendary": MalygosAspectofMagic,
					"DRAGONS~Mage~Spell~5~Rolling Fireball": RollingFireball,
					"DRAGONS~Mage~Minion~7~4~4~~Dragoncaster~Battlecry": Dragoncaster,
					"DRAGONS~Mage~Minion~8~8~8~Elemental~Mana Giant": ManaGiant,
					"DRAGONS~Paladin~Spell~1~Righteous Cause~~Quest": RighteousCause,
					"DRAGONS~Paladin~Spell~1~Sand Breath": SandBreath,
					"DRAGONS~Paladin~Spell~2~Sanctuary~~Quest": Sanctuary,
					"DRAGONS~Paladin~Minion~4~3~6~~Indomitable Champion~Taunt~Uncollectible": IndomitableChampion,
					"DRAGONS~Paladin~Minion~3~2~3~Dragon~Bronze Explorer~Lifesteal~Battlecry": BronzeExplorer,
					"DRAGONS~Paladin~Minion~3~1~2~Mech~Sky Claw~Battlecry": SkyClaw,
					"DRAGONS~Paladin~Minion~1~1~1~Mech~Microcopter~Uncollectible": Microcopter,
					"DRAGONS~Paladin~Minion~3~3~3~~Dragonrider Talritha~Deathrattle~Legendary": DragonriderTalritha,
					"DRAGONS~Paladin~Minion~4~4~2~~Lightforged Zealot~Battlecry": LightforgedZealot,
					"DRAGONS~Paladin~Minion~4~8~8~Dragon~Nozdormu the Timeless~Battlecry~Legendary": NozdormutheTimeless,
					"DRAGONS~Paladin~Minion~5~4~6~Dragon~Amber Watcher~Battlecry": AmberWatcher,
					"DRAGONS~Paladin~Minion~7~7~7~~Lightforged Crusader~Battlecry": LightforgedCrusader,
					"DRAGONS~Priest~Spell~0~Whispers of EVIL": WhispersofEVIL,
					"DRAGONS~Priest~Minion~1~1~2~~Disciple of Galakrond~Battlecry": DiscipleofGalakrond,
					"DRAGONS~Priest~Minion~2~2~2~~Envoy of Lazul~Battlecry": EnvoyofLazul,
					"DRAGONS~Priest~Spell~3~Breath of the Infinite": BreathoftheInfinite,
					"DRAGONS~Priest~Minion~3~3~3~~Mindflayer Kaahrj~Battlecry~Deathrattle~Legendary": MindflayerKaahrj,
					"DRAGONS~Priest~Minion~4~3~6~Dragon~Fate Weaver~Battlecry": FateWeaver,
					"DRAGONS~Priest~Spell~4~Grave Rune": GraveRune,
					"DRAGONS~Priest~Minion~5~4~5~Dragon~Chronobreaker~Deathrattle": Chronobreaker,
					"DRAGONS~Priest~Spell~5~Time Rip": TimeRip,
					"DRAGONS~Priest~Hero Card~7~Galakrond, the Unspeakable~Battlecry~Legendary": GalakrondtheUnspeakable,
					"DRAGONS~Priest~Hero Card~7~Galakrond, the Apocalypes~Battlecry~Legendary~Uncollectible": GalakrondtheApocalypes_Priest,
					"DRAGONS~Priest~Hero Card~7~Galakrond, Azeroth's End~Battlecry~Legendary~Uncollectible": GalakrondAzerothsEnd_Priest,
					"DRAGONS~Neutral~Weapon~5~5~2~Dragon Claw~Uncollectible": DragonClaw,
					"DRAGONS~Priest~Minion~8~8~8~Dragon~Murozond the Infinite~Battlecry~Legendary": MurozondtheInfinite,
					"DRAGONS~Rogue~Minion~1~1~1~Pirate~Bloodsail Flybooter~Battlecry": BloodsailFlybooter,
					"DRAGONS~Rogue~Minion~1~1~1~Pirate~Sky Pirate~Uncollectible": SkyPirate,
					"DRAGONS~Rogue~Spell~1~Dragon's Hoard": DragonsHoard,
					"DRAGONS~Rogue~Spell~1~Praise Galakrond!": PraiseGalakrond,
					"DRAGONS~Rogue~Spell~3~Seal Fate": SealFate,
					"DRAGONS~Rogue~Minion~4~3~3~~Umbral Skulker~Battlecry": UmbralSkulker,
					"DRAGONS~Rogue~Minion~5~2~5~~Necrium Apothecary~Combo": NecriumApothecary,
					"DRAGONS~Rogue~Minion~5~4~4~~Stowaway~Battlecry": Stowaway,
					"DRAGONS~Rogue~Minion~5~7~5~Dragon~Waxadred~Deathrattle~Legendary": Waxadred,
					"DRAGONS~Rogue~Spell~5~Waxadred's Candle~Casts When Drawn~Uncollectible": WaxadredsCandle,
					"DRAGONS~Rogue~Spell~6~Candle Breath": CandleBreath,
					"DRAGONS~Rogue~Minion~6~4~4~~Flik Skyshiv~Battlecry~Legendary": FlikSkyshiv,
					"DRAGONS~Rogue~Hero Card~7~Galakrond, the Nightmare~Battlecry~Legendary": GalakrondtheNightmare,
					"DRAGONS~Rogue~Hero Card~7~Galakrond, the Apocalypes~Battlecry~Legendary~Uncollectible": GalakrondtheApocalypes_Rogue,
					"DRAGONS~Rogue~Hero Card~7~Galakrond, Azeroth's End~Battlecry~Legendary~Uncollectible": GalakrondAzerothsEnd_Rogue,
					"DRAGONS~Shaman~Spell~2~Invocation of Frost": InvocationofFrost,
					"DRAGONS~Shaman~Minion~1~1~3~Elemental~Surging Tempest": SurgingTempest,
					"DRAGONS~Shaman~Minion~4~5~7~Dragon~Squallhunter~Spell Damage~Overload": Squallhunter,
					"DRAGONS~Shaman~Spell~1~Storm's Wrath~Overload": StormsWrath,
					"DRAGONS~Shaman~Spell~3~Lightning Breath": LightningBreath,
					"DRAGONS~Shaman~Minion~5~5~5~~Bandersmosh": Bandersmosh,
					"DRAGONS~Shaman~Minion~5~5~5~Elemental~Cumulo-Maximus~Battlecry": CumuloMaximus,
					"DRAGONS~Shaman~Spell~5~Dragon's Pack": DragonsPack,
					"DRAGONS~Shaman~Minion~2~2~3~~Spirit Wolf~Taunt~Uncollectible": SpiritWolf_Dragons,
					"DRAGONS~Shaman~Minion~6~3~3~~Corrupt Elementalist~Battlecry": CorruptElementalist,
					"DRAGONS~Shaman~Minion~6~5~5~Dragon~Nithogg~Battlecry~Legendary": Nithogg,
					"DRAGONS~Shaman~Minion~1~0~3~~Storm Egg~Uncollectible": StormEgg,
					"DRAGONS~Shaman~Minion~4~4~4~Dragon~Storm Drake~Rush~Uncollectible": StormDrake,
					"DRAGONS~Shaman~Minion~2~2~1~Elemental~Windswept Elemental~Rush~Uncollectible": WindsweptElemental,
					"DRAGONS~Shaman~Hero Card~7~Galakrond, the Tempest~Battlecry~Legendary": GalakrondtheTempest,
					"DRAGONS~Shaman~Hero Card~7~Galakrond, the Apocalypes~Battlecry~Legendary~Uncollectible": GalakrondtheApocalypes_Shaman,
					"DRAGONS~Shaman~Hero Card~7~Galakrond, Azeroth's End~Battlecry~Legendary~Uncollectible": GalakrondAzerothsEnd_Shaman,
					"DRAGONS~Shaman~Minion~2~2~2~Elemental~Brewing Storm~Rush~Uncollectible": BrewingStorm,
					"DRAGONS~Shaman~Minion~4~4~4~Elemental~Living Storm~Rush~Uncollectible": LivingStorm,
					"DRAGONS~Shaman~Minion~8~8~8~Elemental~Raging Storm~Rush~Uncollectible": RagingStorm,
					"DRAGONS~Warlock~Spell~1~Rain of Fire": RainofFire,
					"DRAGONS~Warlock~Spell~2~Nether Breath": NetherBreath,
					"DRAGONS~Warlock~Spell~3~Dark Skies": DarkSkies,
					"DRAGONS~Warlock~Minion~3~1~1~~Dragonblight Cultist~Battlecry": DragonblightCultist,
					"DRAGONS~Warlock~Spell~4~Fiendish Rites": FiendishRites,
					"DRAGONS~Warlock~Minion~4~5~4~~Veiled Worshipper~Battlecry": VeiledWorshipper,
					"DRAGONS~Warlock~Minion~5~5~5~Dragon~Crazed Netherwing~Battlecry": CrazedNetherwing,
					"DRAGONS~Warlock~Minion~6~2~2~~Abyssal Summoner~Battlecry": AbyssalSummoner,
					"DRAGONS~Warlock~Minion~1~1~1~Demon~Abyssal Destroyer~Taunt~Uncollectible": AbyssalDestroyer,
					"DRAGONS~Warlock~Hero Card~7~Galakrond, the Wretched~Battlecry~Legendary": GalakrondtheWretched,
					"DRAGONS~Warlock~Hero Card~7~Galakrond, the Apocalypes~Battlecry~Legendary~Uncollectible": GalakrondtheApocalypes_Warlock,
					"DRAGONS~Warlock~Hero Card~7~Galakrond, Azeroth's End~Battlecry~Legendary~Uncollectible": GalakrondAzerothsEnd_Warlock,
					"DRAGONS~Warlock~Minion~1~1~1~Demon~Draconic Imp~Uncollectible": DraconicImp,
					"DRAGONS~Warlock~Minion~7~4~4~~Valdris Felgorge~Battlecry~Legendary": ValdrisFelgorge,
					"DRAGONS~Warlock~Minion~8~4~12~Dragon~Zzeraku the Warped~Legendary": ZzerakutheWarped,
					"DRAGONS~Warlock~Minion~6~6~6~Dragon~Nether Drake~Uncollectible": NetherDrake,
					"DRAGONS~Warrior~Minion~1~1~2~Pirate~Sky Raider~Battlecry": SkyRaider,
					"DRAGONS~Warrior~Weapon~2~1~2~Ritual Chopper~Battlecry": RitualChopper,
					"DRAGONS~Warrior~Spell~3~Awaken!": Awaken,
					"DRAGONS~Warrior~Weapon~3~2~2~Ancharrr~Legendary": Ancharrr,
					"DRAGONS~Warrior~Minion~3~2~3~~EVIL Quartermaster~Battlecry": EVILQuartermaster,
					"DRAGONS~Warrior~Spell~3~Ramming Speed": RammingSpeed,
					"DRAGONS~Warrior~Minion~4~3~2~Dragon~Scion of Ruin~Rush~Battlecry": ScionofRuin,
					"DRAGONS~Warrior~Minion~3~2~5~Mech~Skybarge": Skybarge,
					"DRAGONS~Warrior~Spell~4~Molten Breath": MoltenBreath,
					"DRAGONS~Warrior~Hero Card~7~Galakrond, the Unbreakable~Battlecry~Legendary": GalakrondtheUnbreakable,
					"DRAGONS~Warrior~Hero Card~7~Galakrond, the Apocalypes~Battlecry~Legendary~Uncollectible": GalakrondtheApocalypes_Warrior,
					"DRAGONS~Warrior~Hero Card~7~Galakrond, Azeroth's End~Battlecry~Legendary~Uncollectible": GalakrondAzerothsEnd_Warrior,
					"DRAGONS~Warrior~Minion~8~12~12~Dragon~Deathwing, Mad Aspect~Battlecry~Legendary": DeathwingMadAspect
					}