from CardPools import *
from Academy import TransferStudent
import copy
from numpy.random import choice as npchoice
from numpy.random import randint as nprandint
from numpy.random import shuffle as npshuffle
import numpy as np

import inspect

#对卡牌的费用机制的改变
#主要参考贴（冰封王座BB还在的时候）：https://www.diyiyou.com/lscs/news/194867.html
#
#费用的计算方式是对于一张牌，不考虑基础费用而是把费用光环和费用赋值一视同仁，根据其执行顺序来决定倒数第二步的费用，最终如果一张牌有自己赋值或者费用修改的能力，则这个能力在最后处理。
#
#BB给出的机制例子中：AV娜上场之后，热情的探险者抽一张牌，抽到融核巨人之后的结算顺序是：
#	AV的变1光环首先生效，然后探险者的费用赋值把那张牌的费用拉回5，然后融核巨人再根据自己的血量进行减费用。
#确实可以解释当前娜迦沙漠女巫与费用光环和大帝减费的问题。
#1：对方场上一个木乃伊，我方一个沙漠女巫，对方一个木乃伊，然后分别是-1光环，赋值为5，-1光环，法术的费用变成4费
#2：对方场上一个木乃伊，我方一个沙漠女巫，对方一个木乃伊，然后大帝。结算结果是-1光环，赋值为5，-1光环，-1赋值。结果是3费
#3.对方场上一个木乃伊，我方一个沙漠女巫，对方一个木乃伊，然后大帝，然后第一个木乃伊被连续杀死，光环消失。结算是赋值为5，-1光环，-1费用变化。最终那张法术的费用为3.
#4.对方场上一个木乃伊，我方一个沙漠女巫，对方一个木乃伊，然后大帝，第二个木乃伊被连续杀死，则那个法术-1光环，赋值为5，-1费用变化，最终费用为4.（已经验证是确实如此）
#5。对方场上一个木乃伊，我方一个沙漠女巫，对方一个木乃伊，然后大帝，第一个木乃伊被连续杀死，则那个法术会经历赋值为5，-1光环，-1费用变化，变为3费（注意第一个木乃伊第一次死亡的时候会复生出一个新的带光环的木乃伊，然后把费用变成2费，但是再杀死那个复生出来的木乃伊之后，费用就是正确的3费。）
class Manas:
	def __init__(self, Game):
		self.Game = Game
		self.manas = {1:1, 2: 0}
		self.manasUpper = {1:1, 2: 0}
		self.manasLocked = {1: 0, 2: 0}
		self.manasOverloaded = {1: 0, 2: 0}
		self.manas_UpperLimit = {1:10, 2:10}
		self.manas_withheld = {1: 0, 2: 0}
		#CardAuras只存放临时光环，永久光环不再注册于此
		#对于卡牌的费用修改效果，每张卡牌自己处理。
		self.CardAuras, self.CardAuras_Backup = [], []
		self.PowerAuras, self.PowerAuras_Backup = [], []
		self.effects = {1: {"Spells Cost Health Instead": 0},
						2: {"Spells Cost Health Instead": 0}
						}

	#If there is no setting mana aura, the mana is simply adding/subtracting.
	#If there is setting mana aura
		#The temp mana change aura works in the same way as ordinary mana change aura.

	'''When the setting mana aura disappears, the calcMana function
	must be cited again for every card in its registered list.'''
	def overloadMana(self, num, ID):
		self.manasOverloaded[ID] += num
		GUI = self.Game.GUI
		if GUI: GUI.seqHolder[-1].append(GUI.FUNC(GUI.heroZones[ID].drawMana, self.manas[ID], self.manasUpper[ID], 
												  self.manasLocked[ID], self.manasOverloaded[ID]))
		self.Game.sendSignal("ManaOverloaded", ID, None, None, 0, "")
		self.Game.sendSignal("OverloadCheck", ID, None, None, 0, "")
		
	def unlockOverloadedMana(self, ID):
		self.manas[ID] += self.manasLocked[ID]
		self.manas[ID] = min(self.manas_UpperLimit[ID], self.manas[ID])
		self.manasLocked[ID] = self.manasOverloaded[ID] = 0
		GUI = self.Game.GUI
		if GUI: GUI.seqHolder[-1].append(GUI.FUNC(GUI.heroZones[ID].drawMana, self.manas[ID], self.manasUpper[ID],
												  self.manasLocked[ID], self.manasOverloaded[ID]))
		self.Game.sendSignal("OverloadCheck", ID, None, None, 0, "")
		
	def setManaCrystal(self, num, ID):
		self.manasUpper[ID] = num
		if self.manas[ID] > num:
			self.manas[ID] = num
		GUI = self.Game.GUI
		if GUI: GUI.seqHolder[-1].append(GUI.FUNC(GUI.heroZones[ID].drawMana, self.manas[ID], self.manasUpper[ID],
												  self.manasLocked[ID], self.manasOverloaded[ID]))
		self.Game.sendSignal("ManaXtlsCheck", ID, None, None, 0, "")
		
	def gainTempManaCrystal(self, num, ID):
		self.manas[ID] += num
		self.manas[ID] = min(self.manas_UpperLimit[ID], self.manas[ID])
		GUI = self.Game.GUI
		if GUI: GUI.seqHolder[-1].append(GUI.FUNC(GUI.heroZones[ID].drawMana, self.manas[ID], self.manasUpper[ID],
												  self.manasLocked[ID], self.manasOverloaded[ID]))
		
	def gainManaCrystal(self, num, ID):
		self.manas[ID] += num
		self.manas[ID] = min(self.manas_UpperLimit[ID], self.manas[ID])
		self.manasUpper[ID] += num
		self.manasUpper[ID] = min(self.manas_UpperLimit[ID], self.manasUpper[ID])
		GUI = self.Game.GUI
		if GUI: GUI.seqHolder[-1].append(GUI.FUNC(GUI.heroZones[ID].drawMana, self.manas[ID], self.manasUpper[ID],
												  self.manasLocked[ID], self.manasOverloaded[ID]))
		self.Game.sendSignal("ManaXtlsCheck", ID, None, None, 0, "")
		
	def gainEmptyManaCrystal(self, num, ID):
		before = self.manasUpper[ID]
		if self.manasUpper[ID] + num <= self.manas_UpperLimit[ID]:
			self.manasUpper[ID] += num
			GUI = self.Game.GUI
			if GUI: GUI.seqHolder[-1].append(GUI.FUNC(GUI.heroZones[ID].drawMana, self.manas[ID], self.manasUpper[ID],
												  self.manasLocked[ID], self.manasOverloaded[ID]))
			self.Game.sendSignal("ManaXtlsCheck", ID, None, None, 0, "")
			return True
		else: #只要获得的空水晶量高于目前缺少的空水晶量，即返回False
			self.manasUpper[ID] = self.manas_UpperLimit[ID]
			GUI = self.Game.GUI
			if GUI: GUI.seqHolder[-1].append(GUI.FUNC(GUI.heroZones[ID].drawMana, self.manas[ID], self.manasUpper[ID],
												  self.manasLocked[ID], self.manasOverloaded[ID]))
			self.Game.sendSignal("ManaXtlsCheck", ID, None, None, 0, "")
			return before < self.manas_UpperLimit[ID]

	def restoreManaCrystal(self, num, ID, restoreAll=False):
		before = self.manas[ID]
		if restoreAll:
			self.manas[ID] = self.manasUpper[ID] - self.manasLocked[ID]
		else:
			self.manas[ID] += num
			self.manas[ID] = min(self.manas[ID], self.manasUpper[ID] - self.manasLocked[ID])
		after = self.manas[ID]
		GUI = self.Game.GUI
		if GUI: GUI.seqHolder[-1].append(GUI.FUNC(GUI.heroZones[ID].drawMana, self.manas[ID], self.manasUpper[ID],
												  self.manasLocked[ID], self.manasOverloaded[ID]))
		if after-before > 0:
			self.Game.sendSignal("ManaXtlsRestore", ID, None, None, after-before, "")

	def destroyManaCrystal(self, num, ID):
		self.manasUpper[ID] = max(0, self.manasUpper[ID] - num)
		self.manas[ID] = min(self.manas[ID], self.manasUpper[ID])
		GUI = self.Game.GUI
		if GUI: GUI.seqHolder[-1].append(GUI.FUNC(GUI.heroZones[ID].drawMana, self.manas[ID], self.manasUpper[ID],
												  self.manasLocked[ID], self.manasOverloaded[ID]))
		self.Game.sendSignal("ManaXtlsCheck", ID, None, None, 0, "")

	def affordable(self, subject, canbeTraded=False):
		ID = subject.ID
		if canbeTraded: return self.manas[ID] > subject.mana or (self.Game.Hand_Deck.decks[ID] and self.manas[ID] > 0)
		else:
			mana = subject.getMana()
			if self.cardCostsHealth(subject):
				return mana < self.Game.heroes[ID].health + self.Game.heroes[ID].armor or self.Game.effects[ID]["Immune"] > 0
			else: return mana <= self.manas[ID]
		
	def cardCostsHealth(self, subject):
		return subject.effects["Cost Health Instead"] > 0# or (subject.type == "Spell" and self.effects[subject.ID]["Spells Cost Health Instead"] > 0)
		
	def payManaCost(self, subject, mana):
		ID, mana = subject.ID, max(0, mana)
		if self.cardCostsHealth(subject):
			dmgTaker = self.Game.scapegoat4(self.Game.heroes[ID])
			dmgTaker.takesDamage(None, mana, damageType="Ability")
		else: self.manas[ID] -= mana
		subject.effects["Cost Health Instead"] = 0 #Cleanse the "Cost Health Instead" mark on the card played
		GUI = self.Game.GUI
		if GUI: GUI.seqHolder[-1].append(GUI.FUNC(GUI.heroZones[ID].drawMana, self.manas[ID], self.manasUpper[ID],
												  self.manasLocked[ID], self.manasOverloaded[ID]))
		self.Game.sendSignal("ManaPaid", ID, subject, None, mana, "")
		if subject.type == "Minion":
			self.Game.Counters.manaSpentonPlayingMinions[ID] += mana
		elif subject.type == "Spell":
			self.Game.Counters.manaSpentonSpells[ID] += mana

	#At the start of turn, player's locked mana crystals are removed.
	#Overloaded manas will becomes the newly locked mana.
	def turnStarts(self):
		ID = self.Game.turn
		self.gainEmptyManaCrystal(1, ID)
		self.manasLocked[ID] = self.manasOverloaded[ID]
		self.manasOverloaded[ID] = 0
		self.manas[ID] = max(0, self.manasUpper[ID] - self.manasLocked[ID] - self.manas_withheld[ID])
		GUI = self.Game.GUI
		if GUI: GUI.seqHolder[-1].append(GUI.FUNC(GUI.heroZones[ID].drawMana, self.manas[ID], self.manasUpper[ID],
												  self.manasLocked[ID], self.manasOverloaded[ID]))
		self.Game.sendSignal("OverloadCheck", ID, None, None, 0, "")
		#卡牌的费用光环加载
		i = 0
		while i < len(self.CardAuras_Backup):
			if self.CardAuras_Backup[i].ID == self.Game.turn:
				tempAura = self.CardAuras_Backup.pop(i)
				self.CardAuras.append(tempAura)
				tempAura.auraAppears()
			else: i += 1 #只有在当前aura无法启动时才会去到下一个位置继续检测，否则在pop之后可以在原位置检测
		self.calcMana_All()
		#英雄技能的费用光环加载
		i = 0
		while i < len(self.PowerAuras_Backup):
			if self.PowerAuras_Backup[i].ID == self.Game.turn:
				tempAura = self.PowerAuras_Backup.pop(i)
				self.PowerAuras.append(tempAura)
				tempAura.auraAppears()
			else: i += 1
		self.calcMana_Powers()

	#Manas locked at this turn doesn't disappear when turn ends. It goes away at the start of next turn.
	def turnEnds(self):
		for aura in self.CardAuras + self.PowerAuras:
			if aura.temporary: aura.auraDisappears()
		self.calcMana_All()
		self.calcMana_Powers()

	def calcMana_All(self, comment="HandOnly"):
		#舍弃之前的卡牌的基础法力值设定
		#卡牌的法力值计算：从卡牌的的基础法力值开始，把法力值光环和法力按照入场顺序进行排列，然后依次进行处理。最后卡牌如果有改变自己费用的能力，则其最后结算，得到最终的法力值。
		#对卡牌的法力值增减和赋值以及法力值光环做平等的处理。
		cards = self.Game.Hand_Deck.hands[1] + self.Game.Hand_Deck.hands[2]
		if comment == "IncludingDeck":
			cards += self.Game.Hand_Deck.decks[1] + self.Game.Hand_Deck.decks[2]
		for card in cards: self.calcMana_Single(card)
		
	def calcMana_Single(self, card):
		mana_0 = card.mana
		card.mana = type(card).mana
		for manaMod in card.manaMods: manaMod.handleMana()
		#随从的改变自己法力值的效果在此结算。如果卡牌有回响，则其法力值不能减少至0
		card.selfManaChange()
		if card.mana < 0: #费用修改不能把卡的费用降为0
			card.mana = 0
		if card.mana < 1 and ((card.type == "Minion" and card.effects["Echo"] > 0) or (card.type == "Spell" and "Echo" in card.index)):
			card.mana = 1
		if card.btn and card.mana != mana_0: card.btn.manaChangeAni(card.mana)
		
	def calcMana_Powers(self):
		for ID in range(1, 3):
			power = self.Game.powers[ID]
			mana_0 = power.mana
			power.mana = type(power).mana
			for manaMod in power.manaMods: manaMod.handleMana()
			power.mana = max(0, power.mana)
			if power.btn and mana_0 != power.mana:
				print("Calcing mana powers", power.name, power.btn, power.mana, mana_0)
				power.btn.manaChangeAni(power.mana)

	def createCopy(self, recipientGame):
		Copy = type(self)(recipientGame)
		for key, value in self.__dict__.items():
			if key == "Game" or callable(value):
				pass
			elif "Auras" not in key: #不承载光环的列表都是数值，直接复制即可
				Copy.__dict__[key] = copy.deepcopy(value)
			else: #承载光环和即将加载的光环的列表
				for aura in value:
					Copy.__dict__[key].append(aura.createCopy(recipientGame))
		return Copy


class Secrets:
	def __init__(self, Game):
		self.Game = Game
		self.secrets = {1:[], 2:[]}
		self.mainQuests = {1: [], 2: []}
		self.sideQuests = {1:[], 2:[]}

	def areaNotFull(self, ID):
		return len(self.mainQuests[ID]) + len(self.sideQuests[ID]) + len(self.secrets[ID]) < 5

	def spaceinArea(self, ID):
		return 5 - (len(self.mainQuests[ID]) + len(self.sideQuests[ID]) + len(self.secrets[ID]))
		
	def initSecretHint(self, secret):
		game, ID = self.Game, secret.ID
		secretCreator, Class = secret.creator, secret.Class
		deckSecrets = []
		if secret.tracked: #如果一张奥秘在手牌中且可以追踪，则需要做一些操作
			game.Hand_Deck.ruleOut(secret, fromHD=2)
			deckSecrets = list(secret.possi)
		else:
			if len(secret.possi) == 1:
				for creator, possi in self.Game.Hand_Deck.cards_1Possi[secret.ID]:
					if creator == secretCreator:
						deckSecrets += [T for T in possi if T.description.startswith("Secret:") and T.Class == Class]
			else: #如果一张奥秘有多种可能，则它肯定可以匹配到一个
				game.Hand_Deck.ruleOut(secret, fromHD=2)
				deckSecrets = list(secret.possi)
		secret.possi = list(set(deckSecrets))
		#需要根据一个奥秘的可能性，把所有可能的奥秘的伪扳机先都注册上
		for possi in secret.possi:
			if not isinstance(secret, possi): #把那些虚假的可能性都注册一份伪扳机
				dummyTrig = possi(game, ID).trigsBoard[0]
				#伪扳机和真奥秘之间需要建立双向联系
				dummyTrig.dummy, dummyTrig.realSecret = True, secret
				dummyTrig.connect()
				#game.trigAuras[ID].append(dummyTrig)
				secret.dummyTrigs.append(dummyTrig)
		for trig in secret.trigsBoard: trig.connect()
		
	def deploySecretsfromDeck(self, ID, num=1):
		curGame = self.Game
		for n in range(num):
			if curGame.mode == 0:
				if curGame.picks:
					i = curGame.picks.pop(0)
				else:
					secrets = [i for i, card in enumerate(curGame.Hand_Deck.decks[ID]) if card.description.startswith("Secret:") and not self.sameSecretExists(card, ID)]
					i = npchoice(secrets) if secrets and self.areaNotFull(ID) else -1
					curGame.picks_Backup.append(i)
				if i > -1: curGame.Hand_Deck.extractfromDeck(i, ID, enemyCanSee=False)[0].whenEffective()
				else: break
		if self.Game.GUI: self.Game.GUI.drawZones(all=False, secret=True)
		
	#奥秘被强行移出奥秘区的时候，都是直接展示出来的，需要排除出已知牌
	def extractSecrets(self, ID, index=0, all=False):
		if all:
			for secret in reversed(self.secrets[ID]):
				secret = self.secrets[ID].pop()
				for trig in secret.trigsBoard: trig.disconnect()
				for trig in secret.dummyTrigs: trig.disconnect()
				secret.dummyTrigs = []
				self.Game.Hand_Deck.ruleOut(secret, fromHD=2)
			return None
		else:
			secret = self.secrets[ID].pop(index)
			for trig in secret.trigsBoard: trig.disconnect()
			for trig in secret.dummyTrigs: trig.disconnect()
			secret.dummyTrigs = []
			self.Game.Hand_Deck.ruleOut(secret, fromHD=2)
			#把其他在场奥秘和对方已知牌库 中的牌也去掉
			dummyTrigType2RuleOut = type(secret.trigsBoard[0])
			for obj in self.secrets[ID]:
				#其他在场奥秘的dummyTrigs需要被取消注册和移除
				try: next(trig for trig in obj.dummyTrigs if isinstance(trig, dummyTrigType2RuleOut)).disconnect()
				except: pass
				try: obj.possi.remove(dummyTrigType2RuleOut)
				except: pass
			self.Game.Hand_Deck.ruleOut(secret, fromHD=2)
			return secret
			
	#secret can be type, index or real card.
	def sameSecretExists(self, secret, ID):
		if isinstance(secret, str):
			return any(obj.index == secret for obj in self.secrets[ID])
		else: #If secret is real card or type
			return any(obj.name == secret.name for obj in self.secrets[ID])
			
	#只有Game自己会引用Secrets
	def createCopy(self, recipientGame):
		Copy = type(self)(recipientGame)
		for ID in range(1, 3):
			for secret in self.secrets[ID]:
				Copy.secrets[ID].append(secret.createCopy(recipientGame))
			for quest in self.mainQuests[ID]:
				Copy.mainQuests[ID].append(quest.createCopy(recipientGame))
			for quest in self.sideQuests[ID]:
				Copy.sideQuests[ID].append(quest.createCopy(recipientGame))
		return Copy


class Counters:
	def __init__(self, Game):
		self.Game = Game
		self.cardsPlayedThisGame = {1: [], 2: []}
		self.minionsDiedThisGame = {1: [], 2: []}
		self.weaponsDestroyedThisGame = {1: [], 2: []}
		self.mechsDiedThisGame = {1: [], 2: []}
		self.manaSpentonSpells = {1: 0, 2: 0}
		self.manaSpentonPlayingMinions = {1: 0, 2: 0}
		#self.numPogoHoppers = {1: 0, 2: 0}
		self.healthRestoredThisGame = {1: 0, 2: 0}
		self.cardsDiscardedThisGame = {1: [], 2: []}
		self.createdCardsPlayedThisGame = {1: 0, 2: 0}
		self.spellsonFriendliesThisGame = {1: [], 2: []}

		self.numSpellsPlayedThisTurn = {1: 0, 2: 0}
		self.numMinionsPlayedThisTurn = {1: 0, 2: 0}
		self.minionsDiedThisTurn = {1: [], 2: []}
		self.numCardsPlayedThisTurn = {1: 0, 2: 0} #Specifically for Combo. Because even Countered spells can trig Combos
		self.cardsPlayedEachTurn = {1: [(), (), []], 2: [(), ()]} #保证始终至少有两个回合可以用于判断。当玩家2开始回合时，会变成[(), (), []]
		self.manas4CardsEachTurn = {1: [(), (), []], 2: [(), ()]}
		
		self.dmgonHeroThisTurn = {1: 0, 2: 0}
		self.dmgonHeroLastTurn = {1: 0, 2: 0}
		self.damageDealtbyHeroPower = {1: 0, 2: 0}
		self.numElementalsPlayedLastTurn = {1: 0, 2: 0}
		self.cardsPlayedLastTurn = {1: [], 2: []}
		self.heroAttackTimesThisTurn = {1: 0, 2: 0}
		self.primaryGalakronds = {1: None, 2: None}
		self.invokes = {1: 0, 2: 0} #For Galakrond
		self.hasPlayedQuestThisGame = {1: False, 2: False}
		self.timesHeroChangedHealth_inOwnTurn = {1: 0, 2: 0}
		self.heroChangedHealthThisTurn = {1: False, 2: False}
		self.powerUsedThisTurn = 0
		self.corruptedCardsPlayed = {1: [], 2: []} #For darkmoon YShaarj.
		self.numSecretsTriggeredThisGame = {1: 0, 2: 0}
		self.numWatchPostSummoned = {1: 0, 2: 0}
		self.healthRestoredThisTurn = {1: 0, 2: 0}
		self.deathrattlesTriggered = {1: [], 2: []}
		self.numCardsDrawnThisTurn = {1: 0, 2: 0}
		
		"""Shadowverse Counters"""
		self.numEvolutionTurn = {1:5, 2:4}
		self.numEvolutionPoint = {1:2, 2:3}
		self.shadows = {1: 0, 2: 0}
		self.turns = {1:1, 2: 0}
		self.evolvedThisGame = {1: 0, 2: 0}
		self.evolvedThisTurn = {1: 0, 2: 0}
		self.numMinionsSummonedThisGame = {1: 0, 2: 0}
		self.amuletsDestroyedThisTurn = {1: [], 2: []}
		self.amuletsDestroyedThisGame = {1: [], 2: []}
		self.timesHeroTookDamage_inOwnTurn = {1: 0, 2: 0}
		self.tempVengeance = {1: False, 2: False}
		self.numBurialRiteThisGame = {1: 0, 2: 0}
		self.numCardsExtraPlayedThisTurn = {1: 0, 2: 0}
		self.artifactsDiedThisGame = {1: {}, 2: {}}
		self.numAcceleratePlayedThisGame = {1: 0, 2: 0}
		self.numAcceleratePlayedThisTurn = {1: 0, 2: 0}
		self.cardsDiscardedThisTurn = {1: [], 2: []}

	def turnStarts(self):
		self.cardsPlayedEachTurn[self.Game.turn].append([])
		self.manas4CardsEachTurn[self.Game.turn].append([])
		
	def turnEnds(self):
		print("cards played each Turn", self.Game.turn, self.cardsPlayedEachTurn)
		self.numElementalsPlayedLastTurn[self.Game.turn] = sum("~Elemental~" in card.index for card in \
																self.cardsPlayedEachTurn[self.Game.turn][-1])# if self.cardsPlayedEachTurn[self.Game.turn] else 0
		self.numCardsPlayedThisTurn = {1: 0, 2: 0}
		self.numMinionsPlayedThisTurn = {1: 0, 2: 0}
		self.numSpellsPlayedThisTurn = {1: 0, 2: 0}
		self.dmgonHeroLastTurn = self.dmgonHeroThisTurn
		self.dmgonHeroThisTurn = {1: 0, 2: 0}
		self.minionsDiedThisTurn = {1:[], 2:[]}
		self.amuletsDestroyedThisTurn = {1:[], 2:[]}
		self.heroAttackTimesThisTurn = {1: 0, 2: 0}
		self.heroChangedHealthThisTurn = {1:False, 2:False}
		self.powerUsedThisTurn = 0
		self.numCardsDrawnThisTurn = {1: 0, 2: 0}
		self.tempVengeance = {1: False, 2: False}
		self.numCardsExtraPlayedThisTurn = {1: 0, 2: 0}
		self.evolvedThisTurn = {1: 0, 2: 0}
		self.numAcceleratePlayedThisTurn = {1: 0, 2: 0}
		self.cardsDiscardedThisTurn = {1:[], 2:[]}
		self.healthRestoredThisTurn = {1: 0, 2: 0}
		
	#只有Game自己会引用Counters
	def createCopy(self, recipientGame):
		Copy = type(self)(recipientGame)
		for key, value in self.__dict__.items():
			if value == self.Game:
				pass
			elif callable(value):
				pass
			elif isinstance(value, (type, type(None), int, np.int64, float, str, bool)):
				Copy.__dict__[key] = value
			elif type(value) == list or type(value) == dict or type(value) == tuple:
				Copy.__dict__[key] = self.copyListDictTuple(value, recipientGame)
			else:
				#因为Counters内部的值除了Game都是数字组成的，可以直接deepcopy
				Copy.__dict__[key] = value.createCopy(recipientGame)
		return Copy

	def copyListDictTuple(self, obj, recipientGame):
		if isinstance(obj, list):
			objCopy = []
			for element in obj:
				#check if they're basic types, like int, str, bool, NoneType,
				if isinstance(element, (type(None), int, float, str, bool)):
					#Have tested that basic types can be appended and altering the original won't mess with the content in the list.
					objCopy.append(element)
				elif inspect.isclass(element):
					objCopy.append(element)
				elif type(element) == list or type(element) == dict or type(element) == tuple: #If the element is a list or dict, just recursively use this function.
					objCopy.append(self.copyListDictTuple(element, recipientGame))
				else: #If the element is a self-defined class. All of them have selfCopy methods.
					objCopy.append(element.createCopy(recipientGame))
		elif isinstance(obj, dict):
			objCopy = {}
			for key, value in obj.items():
				if isinstance(value, (type(None), int, float, str, bool)):
					objCopy[key] = value
				elif inspect.isclass(value):
					objCopy[key] = value
				elif type(value) == list or type(value) == dict or type(value) == tuple:
					objCopy[key] = self.copyListDictTuple(value, recipientGame)
				else:
					objCopy[key] = value.createCopy(recipientGame)
		else: #elif isinstance(obj, tuple):
			tupleTurnedList = list(obj) #tuple因为是immutable的，所以要根据它生成一个列表
			objCopy = self.copyListDictTuple(tupleTurnedList, recipientGame) #复制那个列表
			objCopy = list(objCopy) #把那个列表转换回tuple
		return objCopy


class Discover:
	def __init__(self, Game):
		self.Game = Game
		self.initiator = None

	def startDiscover(self, initiator, effectType, info_RNGSync, info_GUISync):
		if self.Game.GUI:
			self.initiator = initiator
			discover = self.Game.GUI.waitforDiscover()
			print("Discover picked. Initiator", self.initiator)
			effectType.discoverDecided(self.initiator, discover, case="Discovered", info_RNGSync=info_RNGSync,
										   info_GUISync=tuple(info_GUISync+[self.Game.options.index(discover)])
										   )
			self.initiator, self.Game.options = None, []

	def startSelect(self, initiator, validTargets):
		if self.Game.GUI:
			self.initiator = initiator
			self.Game.GUI.update()
			self.Game.GUI.waitforSelect(validTargets)
			self.initiator = None

	def startFusion(self, initiator, validTargets):
		if self.Game.GUI:
			self.initiator = initiator
			self.Game.GUI.update()
			self.Game.GUI.waitforFusion(validTargets)
			self.initiator = None

	def typeCardName(self, initiator):
		if self.Game.GUI:
			self.initiator = initiator
			self.Game.GUI.update(all=False, board=True)
			self.Game.GUI.wishforaCard(initiator)
			self.Game.options = []

	#除了Game本身，没有东西会在函数外引用Game.Discover
	def createCopy(self, game):
		return type(self)(game)
