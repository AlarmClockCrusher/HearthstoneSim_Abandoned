from Handlers import *
from Triggers_Auras import Trig_Borrow

from Basic import Illidan, Anduin
from SV_Basic import SVClasses

import numpy as np
import copy

gameStatusDict = {"Immune": "你的英雄免疫", "Immune2NextTurn": "你的英雄免疫直到你的下个回合", "ImmuneThisTurn": "你的英雄在本回合免疫",
				"Evasive": "你的英雄无法成为法术或英雄技能的目标", "Evasive2NextTurn": "直到下回合，你的英雄无法成为法术或英雄技能的目标",
				"Spell Damage": "你的英雄的法术伤害加成", "Spells Lifesteal": "你的法术具有吸血", "Spells x2": "你的法术会施放两次",
				"Spells Sweep": "你的法术也会对目标随从的相邻随从施放", "Spells Poisonous": "你的法术具有剧毒",

				"Power Sweep": "你的英雄技能也会对目标随从的相邻随从生效", "Power Damage": "你的英雄技能伤害加成", #Power Damage.
				"Power Can Target Minions": "你的英雄技能可以以随从为目标",
				"Power Chance 2": "可以使用两次英雄技能", "Power Chance Inf": "可以使用任意次数的英雄技能",
				"Heal to Damage": "你的治疗改为造成伤害", "Lifesteal Damages Enemy": "你的吸血会对敌方英雄造成伤害，而非治疗你",
				"Choose Both": "你的抉择卡牌可以同时拥有两种效果",
				"Battlecry x2": "你的战吼会触发两次", "Shark Battlecry x2": "你的战吼或连击会触发两次",
				"Deathrattle X": "你的亡语不会触发", "Deathrattle x2": "你的随从的亡语触发两次", "Weapon Deathrattle x2": "你的武器的亡语触发两次",
				"Summon x2": "你的卡牌效果召唤的随从数量翻倍", "Secrets x2": "你的奥秘触发两次",
				"Minions Can't Be Frozen": "你的随从无法被冻结", #Living Dragonbreath prevents minions from being Frozen
				"Ignore Taunt": "所有友方攻击无视嘲讽", #Kayn Sunfury allows player to ignore Taunt
				"Hero Can't Be Attacked": "你的英雄不能被攻击",
				}

statusDict = {key: 0 for key in gameStatusDict.keys()}

class Game:
	def __init__(self, GUI=None):
		self.mainPlayerID = np.random.randint(2) + 1
		self.GUI = GUI

	def initialize(self):
		self.heroes = {1:Illidan(self, 1), 2:Anduin(self, 2)}
		self.powers = {1:self.heroes[1].heroPower, 2:self.heroes[2].heroPower}
		self.heroes[1].onBoard, self.heroes[2].onBoard = True, True
		#Multipole weapons can coexitst at minions in lists. The newly equipped weapons are added to the lists
		self.minions, self.weapons = {1:[], 2:[]}, {1:[], 2:[]}
		self.options, self.mulligans = [], {1:[], 2:[]}
		self.players = {1:None, 2:None}
		#handlers.
		self.Counters, self.Manas, self.Discover, self.Secrets = Counters(self), Manas(self), Discover(self), Secrets(self)

		self.minionPlayed = None #Used for target change induced by triggers such Mayor Noggenfogger and Spell Bender.
		self.gameEnds, self.turn, self.numTurn = 0, 1, 1
		#self.turnstoTake = {1:1, 2:1} #For Temporus & Open the Waygate
		self.tempDeads, self.deads = [[], []], [[], []] #1st list records dead objects, 2nd records object attacks when they die.
		self.resolvingDeath = False
		self.tempImmuneStatus = {"ImmuneThisTurn": 0, "Immune2NextTurn":0}
		self.status = {1:statusDict, 2:copy.deepcopy(statusDict)}
		self.turnStartTrigger, self.turnEndTrigger = [], [] #用于一个回合的光环的取消
		self.trigAuras = {1:[], 2:[]} #用于一些永久光环，如砰砰博士的机械获得突袭。
		#登记了的扳机，这些扳机的触发依次遵循主玩家的场上、手牌和牌库。然后是副玩家的场上、手牌和牌库。
		self.trigsBoard, self.trigsHand, self.trigsDeck = {1:{}, 2:{}}, {1:{}, 2:{}}, {1:{}, 2:{}}
		
		self.mode = 0
		self.fixedGuides, self.guides, self.moves = [], [], []
		self.board = "Ogrimmar"
		
		self.possibleSecrets = {1: [], 2: []}

	def initialize_Details(self, cardPool, ClassCards, NeutralCards, MinionsofCost, RNGPools, hero1, hero2, deck1=[], deck2=[]):
		hero1 = hero1(self, 1)
		hero1.onBoard = True
		self.heroes[1] = hero1
		self.powers[1] = hero1.heroPower
		hero2 = hero2(self, 2)
		hero2.onBoard = True
		self.heroes[2] = hero2
		self.powers[2] = hero2.heroPower
		
		self.cardPool, self.ClassCards, self.NeutralCards = cardPool, ClassCards, NeutralCards
		self.MinionsofCost, self.RNGPools = MinionsofCost, RNGPools
		from Hand import Hand_Deck
		self.Hand_Deck = Hand_Deck(self, deck1, deck2)
		self.Hand_Deck.initialize()
		
	def minionsAlive(self, ID, target=None): #if target is not None, return all living minions except the target
		if target: return [minion for minion in self.minions[ID] if minion.type == "Minion" \
							and minion != target and minion.onBoard and (not minion.dead or minion.marks["Can't Break"] > 0) and minion.health > 0]
		else: return [minion for minion in self.minions[ID] if minion.type == "Minion" and minion.onBoard and (not minion.dead or minion.marks["Can't Break"] > 0) and minion.health > 0]

	def minionsonBoard(self, ID, target=None): #if target is not None, return all onBoard minions except the target
		if target: return [minion for minion in self.minions[ID] if minion.type == "Minion" and minion.onBoard and minion != target]
		else: return [minion for minion in self.minions[ID] if minion.type == "Minion" and minion.onBoard]

	def amuletsonBoard(self, ID, target=None):
		if target: return [amulet for amulet in self.minions[ID] if amulet.type == "Amulet" and amulet.onBoard and amulet != target]
		else: return [amulet for amulet in self.minions[ID] if amulet.type == "Amulet" and amulet.onBoard]

	def minionsandAmuletsonBoard(self, ID, target=None):
		if target: return [amulet for amulet in self.minions[ID] if amulet.type != "Dormant" and amulet.onBoard and amulet != target]
		else: return [amulet for amulet in self.minions[ID] if amulet.type != "Dormant" and amulet.onBoard]

	def earthsonBoard(self, ID, target=None):
		if target: return [amulet for amulet in self.minions[ID] if amulet.type == "Amulet" and amulet.onBoard and "Earth Sigil" in amulet.race and amulet != target]
		else: return [amulet for amulet in self.minions[ID] if amulet.type == "Amulet" and amulet.onBoard and "Earth Sigil" in amulet.race]

	def neighbors2(self, target, countDormants=False):
		targets, ID, pos, i = [], target.ID, target.pos, 0
		while pos > 0:
			pos -= 1
			obj_onLeft = self.minions[ID][pos]
			if not countDormants and obj_onLeft.type != "Minion": break #If Dormants aren't considered as adjacent entities, they block the search
			elif obj_onLeft.onBoard: #If the minion is not onBoard, skip it; if on board, count it.
				targets.append(obj_onLeft)
				i -= 1
				break
		pos = target.pos
		boardSize = len(self.minions[ID])
		while pos < boardSize - 1:
			pos += 1
			obj_onRight = self.minions[ID][pos]
			if not countDormants and obj_onRight.type != "Minion": break
			elif obj_onRight.onBoard:
				targets.append(obj_onRight)
				i += 2
				break
		#i = 0 if no adjacent; -1 if only left; 1 if both; 2 if only right
		return targets, i

	def charsAlive(self, ID, target=None):
		hero = self.heroes[ID]
		objs = [obj for obj in self.minions[ID] if obj.type == "Minion" and obj != target and obj.onBoard and not obj.dead and obj.health > 0]
		if hero.health > 0 and not hero.dead and hero != target: objs.append(hero)
		return objs

	def playAmulet(self, amulet, target, position, choice=0, comment=""):
		ID, canPlayAmulet = amulet.ID, False
		if self.Manas.affordable(amulet) and self.space(ID) and amulet.selectionLegit(target, choice):
			# 打出随从到所有结算完结为一个序列，序列完成之前不会进行胜负裁定。
			# 打出随从产生的序列分为
			# 1）使用阶段： 支付费用，随从进入战场（处理位置和刚刚召唤等），抉择变形类随从立刻提前变形，黑暗之主也在此时变形。
			# 如果随从有回响，在此时决定其将在完成阶段结算回响
			# 使用时阶段：使用时扳机，如伊利丹，任务达人和魔能机甲等
			# 召唤时阶段：召唤时扳机，如鱼人招潮者，饥饿的秃鹫等
			# 得到过载
			###开始结算死亡事件。此时序列还没有结束，不用处理胜负问题。
			# 2）结算阶段： 根据随从的死亡，在手牌、牌库和场上等位置来决定战吼，战吼双次的扳机等。
			# 开始时判定是否需要触发多次战吼，连击
			# 指向型战吼连击和抉择随机选取目标。如果此时场上没有目标，则不会触发 对应指向部分效果和它引起的效果。
			# 抉择和磁力也在此时结算，不过抉择变形类随从已经提前结算，此时略过。
			###开始结算死亡事件，不必处理胜负问题。
			# 3）完成阶段
			# 召唤后步骤：召唤后扳机触发：如飞刀杂耍者，船载火炮等
			# 将回响牌加入打出者的手牌
			# 使用后步骤：使用后扳机：如镜像实体，狙击，顽石元素。低语元素的状态移除结算和dk的技能刷新等。
			###结算死亡，此时因为序列结束可以处理胜负问题。

			# 在打出序列的开始阶段决定是否要产生一个回响copy
			subIndex, subWhere = self.Hand_Deck.hands[amulet.ID].index(amulet), "Hand%d" % amulet.ID
			if target: #因为护符是SV特有的卡牌类型，所以其目标选择一定是列表填充式的
				tarIndex, tarWhere = [], []
				for obj in target:
					if obj.onBoard:
						tarIndex.append(obj.pos)
						tarWhere.append(obj.type+str(obj.ID))
					else:
						tarIndex.append(self.Hand_Deck.hands[obj.ID].index(obj))
						tarWhere.append("Hand%d"%obj.ID)
			else: tarIndex, tarWhere = 0, ''
			amulet, mana, posinHand = self.Hand_Deck.extractfromHand(amulet, enemyCanSee=True)
			amuletIndex = amulet.index
			self.Manas.payManaCost(amulet, mana)  # 海魔钉刺者，古加尔和血色绽放的伤害生效。
			# The new minion played will have the largest sequence.
			# 处理随从的位置的登场顺序。
			amulet.seq = len(self.minions[1]) + len(self.minions[2]) + len(self.weapons[1]) + len(self.weapons[2])
			self.minions[ID].insert(position + 100 * (position < 0), amulet)
			self.sortPos()
			# 使用随从牌、召唤随从牌、召唤结束信号会触发
			# 把本回合召唤随从数的计数提前至打出随从之前，可以让小个子召唤师等“每回合第一张”光环在随从打出时正确结算。连击等结算仍依靠cardsPlayedThisTurn
			self.amuletPlayed = amulet
			armedTrigs = self.armedTrigs("AmuletBeenPlayed")
			if self.GUI: self.GUI.wait(400)
			target = amulet.played(target, choice, mana, posinHand, comment)
			# 完成阶段
			# 只有当打出的随从还在场上的时候，飞刀杂耍者等“在你召唤一个xx随从之后”才会触发。当大王因变形为英雄而返回None时也不会触发。
			# 召唤后步骤，触发“每当你召唤一个xx随从之后”的扳机，如飞刀杂耍者，公正之剑和船载火炮等
			if self.amuletPlayed and self.amuletPlayed.onBoard:
				self.sendSignal("AmuletBeenSummoned", self.turn, self.amuletPlayed, target, mana, "")
			self.Counters.numCardsPlayedThisTurn[self.turn] += 1
			# 假设打出的随从被对面控制的话仍然会计为我方使用的随从。被对方变形之后仍记录打出的初始随从
			self.Counters.cardsPlayedThisTurn[self.turn]["Indices"].append(amuletIndex)
			self.Counters.cardsPlayedThisTurn[self.turn]["ManasPaid"].append(mana)
			self.Counters.cardsPlayedThisGame[self.turn].append(amuletIndex)
			# 使用后步骤，触发镜像实体，狙击，顽石元素等“每当你使用一张xx牌”之后的扳机。
			if self.amuletPlayed and self.amuletPlayed.type == "Amulet":
				if self.amuletPlayed.creator: self.Counters.createdCardsPlayedThisGame[self.turn] += 1
				# The comment here is posinHand, which records the position a card is played from hand. -1 means the rightmost, 0 means the leftmost
				self.sendSignal("AmuletBeenPlayed", self.turn, self.amuletPlayed, target, mana, posinHand, choice,
								armedTrigs)
			# ............完成阶段结束，开始处理死亡情况，此时可以处理胜负问题。
			self.gathertheDead(True)
			for card in self.Hand_Deck.hands[1] + self.Hand_Deck.hands[2]:
				card.effCanTrig()
				card.checkEvanescent()
			if not isinstance(tarIndex, list):
				self.moves.append(
					("playAmulet", subIndex, subWhere, tarIndex, tarWhere, position, choice))
			else:
				self.moves.append(("playAmulet", subIndex, subWhere, tuple(tarIndex), tuple(tarWhere), position, choice))

	#There probably won't be board size limit changing effects.
	#Minions to die will still count as a placeholder on board. Only minions that have entered the tempDeads don't occupy space.
	def space(self, ID):
		#Minions and Dormants both occupy space as long as they are on board.
		return 7 - 2 * (self.heroes[ID].Class in SVClasses) - sum(minion.onBoard for minion in self.minions[ID])

	def playMinion(self, minion, target, position, choice=0, comment=""):
		ID, canPlayMinion = minion.ID, False
		#当场上没有空位且打出的随从不是一个有Accelerate的Shadowverse随从时，不能打出
		if self.Manas.affordable(minion) and (self.space(ID) or (minion.index.startswith("SV_") and minion.willAccelerate())) \
				and minion.selectionLegit(target, choice):
			#打出随从到所有结算完结为一个序列，序列完成之前不会进行胜负裁定。
			#打出随从产生的序列分为
				#1）使用阶段： 支付费用，随从进入战场（处理位置和刚刚召唤等），抉择变形类随从立刻提前变形，黑暗之主也在此时变形。
					#如果随从有回响，在此时决定其将在完成阶段结算回响
					#使用时阶段：使用时扳机，如伊利丹，任务达人和魔能机甲等
					#召唤时阶段：召唤时扳机，如鱼人招潮者，饥饿的秃鹫等
					#得到过载
					###开始结算死亡事件。此时序列还没有结束，不用处理胜负问题。
				#2）结算阶段： 根据随从的死亡，在手牌、牌库和场上等位置来决定战吼，战吼双次的扳机等。
					#开始时判定是否需要触发多次战吼，连击
					#指向型战吼连击和抉择随机选取目标。如果此时场上没有目标，则不会触发 对应指向部分效果和它引起的效果。
					#抉择和磁力也在此时结算，不过抉择变形类随从已经提前结算，此时略过。
					###开始结算死亡事件，不必处理胜负问题。
				#3）完成阶段
					#召唤后步骤：召唤后扳机触发：如飞刀杂耍者，船载火炮等
					#将回响牌加入打出者的手牌
					#使用后步骤：使用后扳机：如镜像实体，狙击，顽石元素。低语元素的状态移除结算和dk的技能刷新等。
					###结算死亡，此时因为序列结束可以处理胜负问题。

			subIndex, subWhere = self.Hand_Deck.hands[minion.ID].index(minion), "Hand%d"%minion.ID
			if target:
				if isinstance(target, list):
					tarIndex, tarWhere = [], []
					for obj in target:
						if obj.onBoard:
							tarIndex.append(obj.pos)
							tarWhere.append(obj.type+str(obj.ID))
						else:
							tarIndex.append(self.Hand_Deck.hands[obj.ID].index(obj))
							tarWhere.append("Hand%d"%obj.ID)
				else: #非列表状态的target一定是炉石卡指定的
					tarIndex, tarWhere = target.pos, target.type+str(target.ID)
			else: tarIndex, tarWhere = 0, ''
			minion, mana, posinHand = self.Hand_Deck.extractfromHand(minion, enemyCanSee=True, animate=False)
			print("Play minion extract from hand finished")
			#如果打出的随从是SV中的爆能强化，激奏和结晶随从，则它们会返回自己的真正要打出的牌以及对应的费用
			try: minion, mana = minion.becomeswhenPlayed(choice)
			except: pass #如果随从没有爆能强化等，则无事发生。
			self.Manas.payManaCost(minion, mana) #海魔钉刺者，古加尔和血色绽放的伤害生效。
			#需要根据变形成的随从来进行不同的执行
			if minion.type == "Spell": #Shadowverse Accelerate minion might become spell when played
				self.minionPlayed, spell = None, minion
				spellHolder, origSpell = [spell], spell
				self.sendSignal("SpellOKtoCast?", self.turn, spellHolder, None, mana, "")
				if not spellHolder:
					self.Counters.numCardsPlayedThisTurn[self.turn] += 1
				else:
					if origSpell != spellHolder[0]: spellHolder[0].cast()
					else:
						armedTrigs = self.armedTrigs("SpellBeenPlayed")
						self.Counters.cardsPlayedThisTurn[self.turn]["Indices"].append(spell.index)
						self.Counters.cardsPlayedThisTurn[self.turn]["ManasPaid"].append(mana)
						spell.played(target, choice, mana, posinHand, comment) #choice用于抉择选项，comment用于区分是GUI环境下使用还是AI分叉
						self.Counters.numCardsPlayedThisTurn[self.turn] += 1
						self.Counters.numSpellsPlayedThisTurn[self.turn] += 1
						if "~Accelerate" in spell.index:
							self.Counters.numAcceleratePlayedThisGame[self.turn] += 1
							self.Counters.numAcceleratePlayedThisTurn[self.turn] += 1
						self.Counters.cardsPlayedThisGame[self.turn].append(spell.index)
						if "~Corrupted~" in spell.index: self.Counters.corruptedCardsPlayed[self.turn].append(spell.index)
						#使用后步骤，触发“每当使用一张xx牌之后”的扳机，如狂野炎术士，西风灯神，星界密使的状态移除和伊莱克特拉风潮的状态移除。
						if spell.creator: self.Counters.createdCardsPlayedThisGame[self.turn] += 1
						self.sendSignal("SpellBeenPlayed", self.turn, spell, target, mana, posinHand, choice, armedTrigs)
						if "~Accelerate" in spell.index:
							self.sendSignal("AccelerateBeenPlayed", self.turn, spell, target, mana, posinHand, choice, armedTrigs)
						#完成阶段结束，处理亡语，此时可以处理胜负问题。
						self.gathertheDead(True)
						for card in self.Hand_Deck.hands[1] + self.Hand_Deck.hands[2]:
							card.effCanTrig()
							card.checkEvanescent()
					if not isinstance(tarIndex, list):
						self.moves.append(("playSpell", subIndex, subWhere, tarIndex, tarWhere, choice))
					else:
						self.moves.append(("playSpell", subIndex, subWhere, tuple(tarIndex), tuple(tarWhere), choice))
					self.Counters.shadows[spell.ID] += 1
			else: #Normal or Enhance X or Crystallize X minion played
				typewhenPlayed = minion.type
				minionIndex = minion.index
				minion.seq = len(self.minions[1]) + len(self.minions[2]) + len(self.weapons[1]) + len(self.weapons[2])
				self.minions[ID].insert(position+100*(position < 0), minion)
				self.sortPos()
				if typewhenPlayed == "Minion": #只有随从打出的时候会计入打出的随从数
					self.Counters.numMinionsPlayedThisTurn[self.turn] += 1
				self.minionPlayed = minion
				armedTrigs = self.armedTrigs("%sBeenPlayed"%typewhenPlayed)
				if self.GUI:
					self.GUI.showOffBoardTrig(minion, alsoDisplayCard=True, animate=False)
					self.GUI.hand2BoardAni(minion)
				target = minion.played(target, choice, mana, posinHand, comment)
				if self.minionPlayed and self.minionPlayed.onBoard:
					self.sendSignal("%sBeenSummoned"%typewhenPlayed, self.turn, self.minionPlayed, target, mana, "")
					if typewhenPlayed=="Minion":
						self.Counters.numMinionsSummonedThisGame[self.minionPlayed.ID] += 1
				self.Counters.numCardsPlayedThisTurn[self.turn] += 1
				#假设打出的随从被对面控制的话仍然会计为我方使用的随从。被对方变形之后仍记录打出的初始随从
				self.Counters.cardsPlayedThisTurn[self.turn]["Indices"].append(minionIndex)
				self.Counters.cardsPlayedThisTurn[self.turn]["ManasPaid"].append(mana)
				self.Counters.cardsPlayedThisGame[self.turn].append(minionIndex)
				if "~Corrupted~" in minion.index: self.Counters.corruptedCardsPlayed[self.turn].append(minionIndex)
				if minion.name.endswith("Watch Post"): self.Counters.numWatchPostSummoned[self.turn] += 1
				#使用后步骤，触发镜像实体，狙击，顽石元素等“每当你使用一张xx牌”之后的扳机。
				if self.minionPlayed and self.minionPlayed.type != "Dormant":
					if self.minionPlayed.creator: self.Counters.createdCardsPlayedThisGame[self.turn] += 1
					#The comment here is posinHand, which records the position a card is played from hand. -1 means the rightmost, 0 means the leftmost
					self.sendSignal("%sBeenPlayed"%typewhenPlayed, self.turn, self.minionPlayed, target, mana, posinHand, choice, armedTrigs)
			#............完成阶段结束，开始处理死亡情况，此时可以处理胜负问题。
			self.gathertheDead(True)
			for card in self.Hand_Deck.hands[1] + self.Hand_Deck.hands[2]:
				card.effCanTrig()
				card.checkEvanescent()
			if not isinstance(tarIndex, list):
				self.moves.append(("playMinion", subIndex, subWhere, tarIndex, tarWhere, position, choice))
			else:
				self.moves.append(("playMinion", subIndex, subWhere, tuple(tarIndex), tuple(tarWhere), position, choice))

	#召唤随从会成为夹杂在其他的玩家行为中，不视为一个完整的阶段。也不直接触发亡语结算等。
	#This method can also summon minions for enemy.
	#SUMMONING MINIONS ONLY CONSIDERS ONBOARD MINIONS. MINIONS THAT HAVE ENTERED THE tempDeads DON'T COUNT AS MINIONS.
	#Khadgar doubles the summoning from any card, except Invoke-triggererd Galakrond(Galakrond, the Tempest; Galakrond, the Wretched).
	def summonx2(self, subject, position, summoner):
		if not isinstance(subject, (list, np.ndarray)): #Summon a single minion
			if self.space(subject.ID) > 0:
				newSubjects = [subject, subject.selfCopy(subject.ID)]
				pos = [position, position]
				self.summon(newSubjects, pos, summoner)
		elif len(subject) == 1: #A list that has only 1 minion to summon
			if self.space(subject[0].ID) > 0:
				self.summonx2(subject[0], position[0], summoner) #Go back to doubling a single minion
		else:
			if self.space(subject[0].ID) > 0:
				newSubjects = []
				newPositions = []
				num_orig, pos = len(subject), position[0]
				if position[1] == "totheRightEnd":
					for sub in subject:
						newSubjects.append(sub)
						newSubjects.append(sub.selfCopy(sub.ID))
						newPositions.append(-1)
						newPositions.append(-1)
				elif position[1] == "leftandRight": #Can only be even: 2, 4, 6
					if num_orig == 2:
						newSubjects = [subject[0], subject[0].selfCopy(subject[0].ID),
										subject[1], subject[1].selfCopy(subject[1].ID)]
						newPositions = [pos+1, pos+1, pos, pos]
					else: #num_orig == 4 or 6
						newSubjects = [subject[0], subject[0].selfCopy(subject[0].ID),
										subject[1], subject[1].selfCopy(subject[1].ID),
										subject[2], subject[2].selfCopy(subject[2].ID)]
						newPositions = [pos+1, pos+1, pos, pos, pos+5, pos+5]
				else: #position[1] == "totheRight":
					for i in range(min(4, num_orig)): #Deathrattle summoning is also handled here.
						newSubjects.append(subject[i])
						newSubjects.append(subject[i].selfCopy(subject[i].ID))
						newPositions.append(pos+1)
						newPositions.append(pos+1)
				#Preprocessing finished, don't invoke doubling. Use the newSubjects and newPositions created.
				self.summon(newSubjects, newPositions, summoner)

	#不考虑卡德加带来的召唤数量翻倍。用于被summon引用。
	#returns the single minion summoned. Used for anchoring the position of the original minion summoned during doubling
	#fromHandDeck {created: 0, fromHand: 1, fromDeck: 2}
	def summonSingle(self, subject, position, summoner, fromHandDeck=0):
		ID = subject.ID
		if self.space(ID) > 0:
			subject.creator = summoner
			subject.seq = len(self.minions[1]) + len(self.minions[2]) + len(self.weapons[1]) + len(self.weapons[2])
			self.minions[subject.ID].insert(position+100*(position<0), subject)  #If position is too large, the insert() simply puts it at the end.
			self.sortPos()
			self.sortSeq()
			if self.GUI:
				if fromHandDeck == 1: self.GUI.hand2BoardAni(subject)
				elif fromHandDeck == 2: self.GUI.deck2BoardAni(subject)
				else: self.GUI.minionAppearAni(subject)
			subject.appears()
			self.Counters.numWatchPostSummoned[ID] += 1
			if subject.type=="Minion":
				self.sendSignal("MinionSummoned", self.turn, subject, None, 0, "")
				self.sendSignal("MinionBeenSummoned", self.turn, subject, None, 0, "")
				self.Counters.numMinionsSummonedThisGame[subject.ID] += 1
			elif subject.type=="Amulet":
				self.sendSignal("AmuletSummoned", self.turn, subject, None, 0, "")
			return subject
		return None

	#只能为同一方召唤随从，如有需要，则多次引用这个函数即可。subject不能是空的
	#注意，卡德加的机制是2 ** n倍。每次翻倍会出现多召唤1个，2个，4个的情况。
	#return the first minion summoned, even if subject is list. Return None if no space left
	def summon(self, subject, position, summoner):
		summonerID = summoner.ID
		if not isinstance(subject, (list, np.ndarray)): #Summon a single minion
			ID, timesofx2 = subject.ID, self.status[summonerID]["Summon x2"]
			if summoner and summoner.type == "Power": timesofx2 = 0 #如果是英雄技能进行的召唤，则不会翻倍。
			if timesofx2 > 0:
				numCopies = 2 ** timesofx2 - 1
				copies = [subject.selfCopy(ID) for i in range(numCopies)]
				minionSummoned = self.summonSingle(subject, position, summoner)
				if minionSummoned: #只有最初的本体召唤成功的时候才会进行复制的随从的召唤
					if self.summonSingle(copies[0], subject.pos+1, summoner):
						for i in range(1, numCopies): #复制的随从列表中剩余的随从，如果没有剩余随从了，直接跳过
							if not self.summonSingle(copies[i], copies[i-1].pos, summoner): break #翻倍出来的复制会始终紧跟在初始随从的右边。
					return minionSummoned #只要第一次召唤出随从就视为召唤成功
				return None
			else: return self.summonSingle(subject, position, summoner)
		else: #Summoning multiple minions in a row. But the list can be of length 1
			if len(subject) == 1: #用列表形式但是只召唤一个随从的时候，position一定是(self.pos, "totheRight")或者（-1, "totheRightEnd"）
				position = position[0] + 1 if position[0] >= 0 else -1
				return self.summon(subject[0], position, summoner)
			else: #真正召唤多个随从的时候，会把它们划分为多次循环。每次循环后下次循环召唤的随从紧贴在这次循环召唤的随从的右边。
				if position[1] == "leftandRight":
					centralMinion, totheRight = self.minions[subject[0].ID][position[0]], 1 #必须得到中间的随从的位置
					for i in range(len(subject)):
						if i == 0: pos = centralMinion.pos+1 #i == 0 召唤的第一个随从直接出现在传递进来的位置的右+1，没有任何问题。但是之后的召唤需要得知发起随从的位置或者之前召唤的随从的位置
						elif i == 1: pos = centralMinion.pos #这个召唤实际上是在列表中插入一个新的随从把中间随从向右挤
						else: #i > 1 向左侧召唤随从也是让新召唤的随从紧贴上一次在左边召唤出来的初始随从。
							pos = subject[i-2].pos+1 if totheRight == 1 else subject[i-2].pos

						totheRight = 1 - totheRight
						if not self.summon(subject[i], pos, summoner):
							if i == 0: return None #只有第一次召唤就因为没有位置而失败时会返回False
							else: break
					return subject[0]
				else: #totheRight or totheRightEnd
					#如果position[1]是"totheRight"，那么position[0]是-2的话会返回pos=1
					pos = -1 if position[1] == "totheRightEnd" else position[0]+1
					for i in range(len(subject)):
						pos = pos if i == 0 else subject[i-1].pos+1
						if not self.summon(subject[i], pos, summoner) and i == 0:
							return None
					return subject[0]

	#一次只从一方的手牌中召唤一个随从。没有列表，从手牌中召唤多个随从都是循环数次检索，然后单个召唤入场的。
	#首个召唤的随从不进行creator的修改，如果有召唤效果翻倍，则把产生的复制的creator修改为召唤者
	def summonfrom(self, i, ID, position, summoner, fromHand=True):
		if self.space(ID) > 0:
			if fromHand: subject = self.Hand_Deck.extractfromHand(i, ID, all=False, enemyCanSee=True)[0]
			else: subject = self.Hand_Deck.extractfromDeck(i, ID, all=False, enemyCanSee=True)[0]
			summonerID = summoner.ID
			ID, timesofx2 = subject.ID, self.status[summonerID]["Summon x2"]
			if summoner and summoner.type == "Power": timesofx2 = 0 #如果是英雄技能进行的召唤，则不会翻倍。
			if timesofx2 > 0:
				numCopies = 2 ** timesofx2 - 1
				copies = [subject.selfCopy(ID) for i in range(numCopies)]
				subject = self.summonSingle(subject, position, None, fromHandDeck=1 if fromHand else 2)
				if subject: #只有最初的本体召唤成功的时候才会进行复制的随从的召唤
					if self.summonSingle(copies[0], subject.pos+1, summoner):
						for i in range(1, numCopies): #复制的随从列表中剩余的随从，如果没有剩余随从了，直接跳过
							if not self.summonSingle(copies[i], copies[i-1].pos, summoner): break #翻倍出来的复制会始终紧跟在初始随从的右边。
					return subject #只要第一次召唤出随从就视为召唤成功
				return None
			else: return self.summonSingle(subject, position, None)
		return None

	def killMinion(self, subject, target):
		if isinstance(target, (list, tuple, np.ndarray)):
			if len(target) > 0:
				if self.GUI and subject: self.GUI.AOEAni(subject, target, ['X'] * len(target), color="grey46")
				for obj in target: obj.dead = True
		elif target:
			if self.GUI and subject: self.GUI.targetingEffectAni(subject, target, 'X', color="grey46")
			if target.onBoard: target.dead = True
			elif target.inHand: self.Hand_Deck.discard(target.ID, target)  # 如果随从在手牌中则将其丢弃

	def necromancy(self, subject, ID, number):
		if self.Counters.shadows[ID] >= number:
			self.Counters.shadows[ID] -= number
			self.sendSignal("Necromancy", ID, subject, None, number, "")
			return True
		return False

	def transform(self, target, newMinion, firstTime=True):
		ID = target.ID
		if target in self.minions[ID]:
			pos = target.pos
			target.disappears(deathrattlesStayArmed=False, disappearResponse=False)
			self.removeMinionorWeapon(target, animate=False)
			if self.minionPlayed == target: self.minionPlayed = newMinion
			#removeMinionorWeapon invokes sortPos() and sortSeq()
			newMinion.seq = len(self.minions[1]) + len(self.minions[2]) + len(self.weapons[1]) + len(self.weapons[2])
			self.minions[ID].insert(pos, newMinion)
			self.sortPos()
			if self.GUI:
				if newMinion.type == target.type:
					target.btn.changeCard(newMinion)
				else: #主要用于随从和休眠物之间的变形
					btn = target.btn
					boardZone = self.GUI.boardZones[ID]
					pos = target.btn.getPos()
					boardZone.addaMinion(newMinion, pos)
					boardZone.removeMinion(btn)
					self.GUI.ensureBtnMovedAway(btn)
			newMinion.appears(firstTime)
		elif target in self.Hand_Deck.hands[target.ID]:
			if self.minionPlayed == target: self.minionPlayed = newMinion
			self.Hand_Deck.replaceCardinHand(target, newMinion)
		
	#This method is always invoked after the minion.disappears() method.
	def removeMinionorWeapon(self, target, animate=True):
		target.onBoard = False
		zone = self.weapons[target.ID] if target.type == "Weapon" else self.minions[target.ID]
		try: zone.remove(target)
		except: pass
		self.sortSeq()
		if target.type != "Weapon": self.sortPos()
		if self.GUI and animate:
			self.GUI.removeMinionorWeaponAni(target)

	def banishMinion(self, subject, target):
		if target:
			if isinstance(target, list):
				if self.GUI and subject: self.GUI.AOEAni(subject, target, ['○']*len(target), color="grey46")
				for obj in target:
					obj.disappears(deathrattlesStayArmed=False)
					self.removeMinionorWeapon(obj)
			else:
				if self.GUI and subject: self.GUI.targetingEffectAni(subject, target, '○', color="grey46")
				if target.onBoard:
					target.disappears(deathrattlesStayArmed=False)
					self.removeMinionorWeapon(target)
				elif target.inHand: self.Hand_Deck.extractfromHand(target.ID, target) #如果随从在手牌中则将其丢弃


	def isVengeance(self, ID):
		return self.heroes[ID].health <= 10 or self.Counters.tempVengeance[ID]

	def isAvarice(self, ID):
		return self.Counters.numCardsDrawnThisTurn[ID] >= 2

	def isWrath(self, ID):
		return self.Counters.timesHeroTookDamage_inOwnTurn[ID] >= 7

	def isResonance(self, ID):
		return len(self.Hand_Deck.decks[ID]) % 2 == 0

	def isOverflow(self, ID):
		return self.Manas.manasUpper[ID] >= 7

	def combCards(self, ID):
		return self.Counters.numCardsPlayedThisTurn[ID]

	def getEvolutionPoint(self, ID):
		point = 0
		if self.heroes[ID].heroPower.name == "Evolve" and self.Counters.turns[ID] >= \
				self.Counters.numEvolutionTurn[ID]:
			point = self.Counters.numEvolutionPoint[ID]
		return point

	def restoreEvolvePoint(self, ID, number=1):
		if self.heroes[ID].heroPower.name == "Evolve":
			self.Counters.numEvolutionPoint[ID] = min(1 + ID, self.Counters.numEvolutionPoint[ID] + number)

	def earthRite(self, subject, ID, number=1):
		earths = self.earthsonBoard(ID)
		if len(earths) >= number:
			for i in range(number):
				self.killMinion(subject, earths[i])
				self.gathertheDead()
			return True
		return False

	def reanimate(self, ID, mana):
		if self.mode == 0:
			t = None
			if self.guides:
				t = self.cardPool[self.guides.pop(0)]
			else:
				indices = self.Counters.minionsDiedThisGame[ID]
				minions = {}
				for index in indices:
					try:
						minions[self.cardPool[index].mana].append(self.cardPool[index])
					except:
						minions[self.cardPool[index].mana] = [self.cardPool[index]]
				for i in range(mana, -1, -1):
					if i in minions:
						t = np.random.choice(minions[i])
						break
				self.fixedGuides.append(t.index)
			if t:
				subject = t(self, ID)
				self.summon([subject], (-1, "totheRightEnd"), None)
				self.sendSignal("Reanimate", ID, subject, None, mana, "")
				return subject
		return None

	#The leftmost minion has position 0. Consider Dormant
	def sortPos(self):
		for i, obj in enumerate(self.minions[1]): obj.pos = i
		for i, obj in enumerate(self.minions[2]): obj.pos = i

	#Rearrange all livng minions' sequences if change is true. Otherwise, just return the list of the sequences.
	#需要考虑Dormant的出场顺序
	def sortSeq(self):
		objs = self.weapons[1] + self.weapons[2] + self.minions[1] + self.minions[2]
		for i, obj in zip(np.asarray([obj.seq for obj in objs]).argsort().argsort(), objs): obj.seq = i

	def returnMiniontoHand(self, target, deathrattlesStayArmed=False, manaMod=None):
		ID = target.ID
		if target in self.minions[ID]: #如果随从仍在随从列表中
			if self.Hand_Deck.handNotFull(ID):
				#如果onBoard仍为True，则其仍计为场上存活的随从，需调用disappears以注销各种扳机。
				if target.onBoard: #随从存活状态下触发死亡扳机的区域移动效果时，不会注销其他扳机
					target.disappears(deathrattlesStayArmed)
				#如onBoard为False,则disappears已被调用过了。主要适用于触发死亡扳机中的区域移动效果
				print("Card to move 01", target, target.btn)
				self.removeMinionorWeapon(target, animate=False)
				print("Card to move 02", target, target.btn)
				if self.GUI: self.GUI.board2HandAni(target)
				print("Card to move 1", target, target.btn)
				target.reset(ID)
				if manaMod: manaMod.applies()
				print("Card to move 2", target, target.btn)
				self.Hand_Deck.addCardtoHand(target, ID)
				for func in target.returnResponse:
					func()
				return target
			else: #让还在场上的活着的随从返回一个满了的手牌只会让其死亡
				if target.onBoard: target.dead = True
				for func in target.returnResponse:
					func()
				return None #如果随从这时已死亡，则满手牌下不会有任何事情发生。
		elif target.inDeck: #如果目标阶段已经在牌库中了，将一个基础复制置入其手牌。
			Copy = type(target)(self, ID)
			self.Hand_Deck.addCardtoHand(Copy, ID)
			return Copy
		elif target.inHand: return target
		else: return None #The target is dead and removed already

	#targetDeckID decides the destination. initiatorID is for triggers, such as Trig_AugmentedElekk
	def returnMiniontoDeck(self, target, targetDeckID, initiatorID, deathrattlesStayArmed=False):
		if target in self.minions[target.ID]:
			#如果onBoard仍为True，则其仍计为场上存活的随从，需调用disappears以注销各种扳机
			if target.onBoard: #随从存活状态下触发死亡扳机的区域移动效果时，不会注销其他扳机
				target.disappears(deathrattlesStayArmed)
			#如onBoard为False，则disappears已被调用过了。主要适用于触发死亡扳机中的区域移动效果
			self.removeMinionorWeapon(target)
			target.reset(targetDeckID) #永恒祭司的亡语会备份一套enchantment，在调用该函数之后将初始化过的本体重新增益
			self.Hand_Deck.shuffleintoDeck(target)
			return target
		elif target.inHand: #如果随从已进入手牌，仍会将其强行洗入牌库
			self.Hand_Deck.shuffleintoDeck(self.Hand_Deck.extractfromHand(target)[0])
			return target
		else: return None

	def minionSwitchSide(self, target, activity="Permanent"):
		#如果随从在手牌中，则该会在手牌中换边；如果随从在牌库中，则无事发生。
		if target.inHand and target in self.Hand_Deck.hands[target.ID]:
			card, mana, posinHand = self.Hand_Deck.extractfromHand(target, enemyCanSee=True)
			#addCardtoHand method will force the ID of the card to change to the target hand ID.
			#If the other side has full hand, then the card is extracted and thrown away.
			self.Hand_Deck.addCardtoHand(card, 3-card.ID)
		elif target.onBoard: #If the minion is on board.
			if self.space(3-target.ID) < 1:
				target.dead = True
			else:
				target.disappears(deathrattlesStayArmed=False) #随从控制权的变更会注销其死亡扳机，随从会在另一方重新注册其所有死亡扳机
				self.minions[target.ID].remove(target)
				target.ID = 3 - target.ID
				self.minions[target.ID].append(target)
				self.sortPos() #The appearance sequence stays intact.
				target.appears(firstTime=False) #控制权的变更不会触发水晶核心以及休眠随从的再次休眠等
				#Possible activities are "Permanent" "Borrow" "Return"
				#每个随从只有携带一个回合结束后将随从归为对方的turnEndTrigger
				#被暂时控制的随从如果被无面操纵者复制，复制者也可以攻击，回合时，连同复制者一并归还对面。
				if activity == "Borrow":
					if target.status["Borrowed"] < 1:
						target.status["Borrowed"] = 1
						#因为回合结束扳机的性质，只有第一个同类扳机会触发，因为后面的扳机检测时会因为ID已经不同于当前回合的ID而不能继续触发
						trig = Trig_Borrow(target)
						target.trigsBoard.append(trig)
						trig.connect()
				else: #Return or permanent
					target.status["Borrowed"] = 0
					#假设归还或者是控制对方随从的时候会清空所有暂时控制的标志，并取消回合结束归还随从的扳机
					for trig in reversed(target.trigsBoard):
						if isinstance(trig, Trig_Borrow):
							trig.disconnect()
							target.trigsBoard.remove(trig)
				target.afterSwitchSide(activity)

	#Given a list of targets to sort, return the list that
	#contains the targets in the right order to trigger.
	def orderofDead(self, targets):
		temp, seqs = targets, [target.seq for target in targets]
		order = np.asarray(seqs).argsort()
		return [temp[i] for i in order], order

	def armedTrigs(self, sig):
		trigs = []
		for ID in [self.mainPlayerID, 3 - self.mainPlayerID]:
			try: trigs += self.trigsBoard[ID][sig]
			except: pass
			try: trigs += self.trigsHand[ID][sig]
			except: pass
			try: trigs += self.trigsDeck[ID][sig]
			except: pass
		return trigs

	#New signal processing can be interpolated during the processing of old signal
	def sendSignal(self, signal, ID, subject, target, number, comment, choice=0, trigPool=None):
		hasResponder = False
		if trigPool is not None: #主要用于打出xx牌和随从死亡时/后扳机，它们有预检测机制。
			for trig in trigPool: #扳机只有仍被注册情况下才能触发，但是这个状态可以通过canTrigger来判断，而不必在所有扳机列表中再次检查。
				if trig.canTrig(signal, ID, subject, target, number, comment, choice): #扳机能触发通常需要扳机记录的实体还在场上等。
					hasResponder = True
					trig.trig(signal, ID, subject, target, number, comment, choice)
		else: #向所有注册的扳机请求触发。
			mainPlayerID = self.mainPlayerID #假设主副玩家不会在一次扳机结算之中发生变化。先触发主玩家的各个位置的扳机。
			#Trigger the trigs on main player's side, in the following order board-> hand -> deck.
			for triggerID in [mainPlayerID, 3-mainPlayerID]:
				trigs = [] #TrigsBoard
				try: #这个信号有扳机在监听时，记录所有满足条件的扳机
					trigs = [trig for trig in self.trigsBoard[triggerID][signal] if trig.canTrig(signal, ID, subject, target, number, comment, choice)]
					#某个随从死亡导致的队列中，作为场上扳机，救赎拥有最低优先级，其始终在最后结算
					if trigs: hasResponder = True
					#Redemption has been rotated out
					#if signal == "MinionDies" and self.Secrets.sameSecretExists(Redemption, 3-self.turn):
					#	for i in range(len(trigs)):
					#		if type(trigs[i]) == Trig_Redemption:
					#			trigs.append(trigs.pop(i)) #把救赎的扳机移到最后
					#			break
					for trig in trigs: trig.trig(signal, ID, subject, target, number, comment, choice)
				except: pass
				try: #TrigsHand
					trigs = [trig for trig in self.trigsHand[triggerID][signal] if trig.canTrig(signal, ID, subject, target, number, comment, choice)]
					if trigs: hasResponder = True
					for trig in trigs: trig.trig(signal, ID, subject, target, number, comment, choice)
				except: pass
				try: #TrigsDeck
					trigs = [trig for trig in self.trigsDeck[triggerID][signal] if trig.canTrig(signal, ID, subject, target, number, comment, choice)]
					if trigs: hasResponder = True
					invocation = []
					for trig in trigs:
						if "Invocation" in type(trig).__name__:
							if trig.entity.name not in invocation:
								trig.trig(signal, ID, subject, target, number, comment, choice)
								invocation.append(trig.entity.name)
						else:
							trig.trig(signal, ID, subject, target, number, comment, choice)
				except: pass
		return hasResponder

	#Process the damage transfer. If no transfer happens, the original target is returned
	def scapegoat4(self, target, subject=None):
		holder = [target]
		while self.sendSignal("DmgTaker?", 0, subject, holder, 0, ""):
			pass
		dmgTaker = holder[0]
		self.sendSignal("DmgTaker?", 0, None, None, 0, "Reset")
		return dmgTaker

	#The weapon will also join the deathList and compare its own sequence against other minions.
	def gathertheDead(self, decideWinner=False):
		#Determine what characters are dead. The die() method hasn't been invoked yet.
		#序列内部不包含胜负裁定，即只有回合开始、结束产生的序列；
		#回合开始抽牌产生的序列；打出随从，法术，武器，英雄牌产生的序列；
		#以及战斗和使用英雄技能产生的序列以及包含的所有亡语等结算结束之后，胜负才会被结算。
		for ID in range(1, 3):
			#Register the weapons to destroy.(There might be multiple weapons in queue,
			#since you can trigger Tirion Fordring's deathrattle twice and equip two weapons in a row.)
			#Pop all the weapons until no weapon or the latest weapon equipped.
			while self.weapons[ID]:
				if self.weapons[ID][0].durability < 1 or self.weapons[ID][0].dead:
					self.weapons[ID][0].destroyed() #武器的被摧毁函数，负责其onBoard, dead和英雄风怒，攻击力和场上扳机的移除等。
					weapon = self.weapons[ID].pop(0)
					self.Counters.weaponsDestroyedThisGame[weapon.ID].append(weapon.index)
					self.tempDeads[0].append(weapon)
					self.tempDeads[1].append(weapon.attack)
				else: #If the weapon is the latest weapon to equip
					break
			for minion in self.minionsonBoard(ID) + self.amuletsonBoard(ID):
				if minion.dead and minion.marks["Can't Break"] > 0:
					minion.dead = False
				if minion.type == "Minion":
					if minion.health < 1 or minion.dead:
						if minion.marks["Disappear When Die"] > 0:
							self.banishMinion(None, minion)
							continue
						minion.dead = True
						self.tempDeads[0].append(minion)
						self.tempDeads[1].append(minion.attack)
						minion.disappears(deathrattlesStayArmed=True) #随从死亡时不会注销其死亡扳机，这些扳机会在触发之后自行注销
						self.Counters.minionsDiedThisTurn[minion.ID].append(minion.index)
						self.Counters.minionsDiedThisGame[minion.ID].append(minion.index)
						if "Artifact" in minion.race:
							if minion.index in self.Counters.artifactsDiedThisGame[minion.ID]:
								self.Counters.artifactsDiedThisGame[minion.ID][minion.index] += 1
							else:
								self.Counters.artifactsDiedThisGame[minion.ID][minion.index] = 1
						self.Counters.shadows[minion.ID] += 1
				elif minion.dead: #The obj is Amulet and it's been marked dead
					minion.dead = True
					self.tempDeads[0].append(minion)
					self.tempDeads[1].append(0)
					minion.disappears(deathrattlesStayArmed=True) #随从死亡时不会注销其死亡扳机，这些扳机会在触发之后自行注销
					self.Counters.amuletsDestroyedThisTurn[minion.ID].append(minion.index)
					self.Counters.amuletsDestroyedThisGame[minion.ID].append(minion.index)
					self.Counters.shadows[minion.ID] += 1
			#无论是不在此时结算胜负，都要在英雄的生命值降为0时将其标记为dead
			if self.heroes[ID].health < 1: self.heroes[ID].dead = True

		if self.tempDeads[0]: #self.tempDeads != [[], []]
			#Rearrange the dead minions according to their sequences.
			self.tempDeads[0], order = self.orderofDead(self.tempDeads[0])
			temp = self.tempDeads[1]
			self.tempDeads[1] = []
			for i in range(len(order)):
				self.tempDeads[1].append(temp[order[i]])
			if self.GUI: self.GUI.minionsDieAni(self.tempDeads[0])
			#If there is no current deathrattles queued, start the deathrattle calc process.
			if not self.deads[0]: self.deads = self.tempDeads
			else:
				#If there is deathrattle in queue, simply add new deathrattles to the existing list.
				self.deads[0] += self.tempDeads[0]
				self.deads[1] += self.tempDeads[1]

			#The content stored in self.tempDeads must be released.
			#Clean the temp list to wait for new input.
			self.tempDeads = [[], []]
			if self.GUI: self.GUI.wait(500)

		if not self.resolvingDeath: #如果游戏目前已经处于死亡结算过程中，不会再重复调用deathHandle
			#如果要执行胜负判定或者有要死亡/摧毁的随从/武器，则调用deathHandle
			if decideWinner or self.deads[0]:  #self.deads != [[], []]
				self.deathHandle(decideWinner)

	#大法师施放的闷棍会打断被闷棍的随从的回合结束结算。可以视为提前离场。
	#死亡缠绕实际上只是对一个随从打1，然后如果随从的生命值在1以下，则会触发抽牌。它不涉及强制死亡导致的随从提前离场
	#当一个拥有多个亡语的随从死亡时，多个亡语触发完成之后才会开始结算其他随从死亡的结算。
	#每次gathertheDead找到要死亡的随从之后，会在它们这一轮的死亡事件全部处理之后，才再次收集死者，用于下次死亡处理。
		#复生随从也会在一轮死亡结算之后统一触发。
	#亡语实际上是随从死亡时触发的扳机，例如食腐土狼与亡语野兽的结算是先登场者先触发
	def deathHandle(self, decideWinner=False):
		while True:
			rebornMinions = []
			if not self.deads[0]: break #If no minions are dead, then stop the loop
			armedTrigs_WhenDies = self.armedTrigs("MinionDies") + self.armedTrigs("WeaponDestroyed") + self.armedTrigs("AmuletDestroys")
			armedTrigs_AfterDied = self.armedTrigs("MinionDied") + self.armedTrigs("AmuletDestroyed")
			while self.deads != [[], []]:
				self.resolvingDeath = True
				objtoDie, attackwhenDies = self.deads[0][0], self.deads[1][0] #留着这个attackwhenDies是因为随从可能会因为光环的失去而产生攻击力的变化
				#For now, assume Tirion Fordring's deathrattle equipping Ashbringer won't trigger player's weapon's deathrattles right away.
				#weapons with regard to deathrattle triggering is handled the same way as minions.
				#一个亡语随从另附一个亡语时，两个亡语会连续触发，之后才会去结算其他随从的亡语。
				#当死灵机械师与其他 亡语随从一同死亡的时候， 不会让那些亡语触发两次，即死灵机械师、瑞文戴尔需要活着才能有光环
				#场上有憎恶时，憎恶如果死亡，触发的第一次AOE杀死死灵机械师，则第二次亡语照常触发。所以亡语会在第一次触发开始时判定是否会多次触发
				print("Removing dead minion/weapon before deathresolution", objtoDie, objtoDie.btn)
				if objtoDie.type == "Minion" and objtoDie.keyWords["Reborn"] > 0: rebornMinions.append(objtoDie)
				objtoDie.deathResolution(attackwhenDies, armedTrigs_WhenDies, armedTrigs_AfterDied)
				print("Removing dead minion/weapon", objtoDie, objtoDie.btn)
				self.removeMinionorWeapon(objtoDie) #结算完一个随从的亡语之后将其移除。
				objtoDie.reset(objtoDie.ID)
				objtoDie.dead = True
				self.deads[0].pop(0)
				self.deads[1].pop(0)
			#当一轮死亡结算结束之后，召唤这次死亡结算中死亡的复生随从
			for rebornMinion in rebornMinions:
				miniontoSummon = type(rebornMinion)(self, rebornMinion.ID)
				miniontoSummon.keyWords["Reborn"], miniontoSummon.health = 0, 1 #不需要特殊的身材处理，激怒等直接在随从的appears()函数中处理。
				self.summon(miniontoSummon, rebornMinion.pos, rebornMinion)
			#死亡结算每轮结束之后才进行死亡随从的收集，然后进行下一轮的亡语结算。
			self.gathertheDead(decideWinner) #See if the deathrattle results in more death or destruction.
			if self.deads == [[], []]: break #只有没有死亡随从要结算了才会终结

		self.resolvingDeath = False
		#The reborn effect take place after the deathrattles of minions have been triggered.
		if decideWinner: #游戏中选手的死亡状态
			self.gameEnds = (self.heroes[1].dead or self.heroes[1].health <= 0) + 2 * (self.heroes[2].dead or self.heroes[2].health <= 0)

	"""
	At the start of turn, the AOE destroy/AOE damage/damage effect won't kill minions make them leave the board.
	As long as the minion is still on board, it can still trigger its turn start/end effects.
	Special things are Sap/Defile, which will force the minion to leave board early.
	#The Defile will cause the game to preemptively start death resolution.
	Archmage casting spell will be able to target minions with health <= 0, since they are not regarded as dead yet.
	The deaths of minions will be handled at the end of triggering, which is then followed by drawing card.
	"""
	def switchTurn(self):
		if self.GUI: self.GUI.switchTurnAni()
		for minion in self.minions[self.turn] + self.minions[3-self.turn]: #Include the Dormants.
			minion.turnEnds(self.turn) #Handle minions' attTimes and attChances
		for card in self.Hand_Deck.hands[self.turn]	+ self.Hand_Deck.hands[3-self.turn]:
			if card.type == "Minion": #Minions in hands will clear their temp buffDebuff
				card.turnEnds(self.turn) #Minions in hands can't defrost

		self.heroes[self.turn].turnEnds(self.turn)
		self.heroes[3-self.turn].turnEnds(self.turn)
		self.powers[self.turn].turnEnds(self.turn)
		self.powers[3-self.turn].turnEnds(self.turn)
		self.sendSignal("TurnEnds", self.turn, None, None, 0, "")
		self.gathertheDead(True)
		#The secrets and temp effects are cleared at the end of turn.
		for obj in self.turnEndTrigger[:]: #所有一回合光环都是回合结束时消失，即使效果在自己回合外触发了也是如此
			obj.turnEndTrigger()

		self.Counters.turnEnds()
		self.Manas.turnEnds()

		self.turn = 3 - self.turn #Changes the turn to another hero.
		self.numTurn += 1
		self.Counters.turns[self.turn] += 1
		self.Manas.turnStarts()
		for obj in self.turnStartTrigger[:]: #This is for temp effects.
			if not hasattr(obj, "ID") or obj.ID == self.turn: obj.turnStartTrigger()
		self.heroes[self.turn].turnStarts(self.turn)
		self.heroes[3-self.turn].turnStarts(self.turn)
		self.powers[self.turn].turnStarts(self.turn)
		self.powers[3-self.turn].turnStarts(self.turn)
		for minion in self.minions[1] + self.minions[2]: #Include the Dormants.
			minion.turnStarts(self.turn) #Handle minions' attTimes and attChances
		for card in self.Hand_Deck.hands[1]	+ self.Hand_Deck.hands[2]:
			if card.type == "Minion":
				card.turnStarts(self.turn)

		self.sendSignal("TurnStarts", self.turn, None, None, 0, "")
		self.gathertheDead(True)
		#抽牌阶段之后的死亡处理可以涉及胜负裁定。
		self.Hand_Deck.drawCard(self.turn)
		if self.turn == 2 and self.Counters.turns[2] == 1 and self.heroes[2].Class in SVClasses:
			self.Hand_Deck.drawCard(self.turn)
		self.gathertheDead(True) #There might be death induced by drawing cards.
		for card in self.Hand_Deck.hands[1] + self.Hand_Deck.hands[2]:
			card.effCanTrig()
			card.checkEvanescent()
		self.moves.append(("EndTurn", ))

	def battle(self, subject, target, verifySelectable=True, useAttChance=True, resolveDeath=True, resetRedirTrig=True):
		if verifySelectable and not subject.canAttackTarget(target):
			return False
		else:
		#战斗阶段：
			#攻击前步骤： 触发攻击前扳机，列队结算，如爆炸陷阱，冰冻陷阱，误导
				#如果扳机结算完毕后，被攻击者发生了变化，则再次进行攻击前步骤的扳机触发。重复此步骤直到被攻击者没有变化为止。
				#在这些额外的攻击前步骤中，之前已经触发过的攻击前扳机不能再能触发。主要是指市长和傻子
			#攻击时步骤：触发攻击时扳机，如真银圣剑，智慧祝福，血吼，收集者沙库尔等
			#如果攻击者，被攻击目标或者任意一方英雄离场或者濒死，则攻击取消，跳过伤害和攻击后步骤。
			#无论攻击是否取消，攻击者的attackedTimes都会增加。
			#伤害步骤：攻击者移除潜行，攻击者对被攻击者造成伤害，被攻击者对攻击者造成伤害。然后结算两者的伤害事件。
			#攻击后步骤：触发“当你的xx攻击之后”扳机。如捕熊陷阱，符文之矛。
				#蜡烛弓和角斗士的长弓给予的免疫被移除。
			#战斗阶段结束，处理死亡事件
		#如果有攻击之后的发现效果需要结算，则在此结算之后。


			#如果一个角色被迫发起攻击，如沼泽之王爵德，野兽之心，群体狂乱等，会经历上述的战斗阶段的所有步骤，之后没有发现效果结算。同时角色的attackedTimes不会增加。
			#之后没有阶段间步骤（因为这种强制攻击肯定是由其他序列引发的）
			#疯狂巨龙死亡之翼的连续攻击中，只有第一次目标选择被被市长改变，但之后的不会
			if self.GUI:
				self.GUI.wait(275)
				self.GUI.attackAni(subject)
			if verifySelectable:
				subIndex, subWhere = subject.pos, subject.type+str(subject.ID)
				tarIndex, tarWhere = target.pos, target.type+str(target.ID)
			#如果英雄的武器为蜡烛弓和角斗士的长弓，则优先给予攻击英雄免疫，防止一切攻击前步骤带来的伤害。
			self.sendSignal("BattleStarted", self.turn, subject, target, 0, "") #这里的target没有什么意义，可以留为target
			#在此，奥秘和健忘扳机会在此触发。需要记住初始的目标，然后可能会有诸多扳机可以对此初始信号响应。
			targetHolder = [target, target] #第一个target是每轮要触发的扳机会对应的原始随从，目标重导向扳机会改变第二个
			signal = subject.type + "Attacks" + targetHolder[0].type
			self.sendSignal(signal, self.turn, subject, targetHolder, 0, "1stPre-attack")
			#第一轮攻击前步骤结束之后，Game的记录的target如果相对于初始目标发生了变化，则再来一轮攻击前步骤，直到目标不再改变为止。
			#例如，对手有游荡怪物、误导和毒蛇陷阱，则攻击英雄这个信号可以按扳机入场顺序触发误导和游荡怪物，改变了攻击目标。之后的额外攻击前步骤中毒蛇陷阱才会触发。
			#如果对手有崇高牺牲和自动防御矩阵，那么攻击随从这个信号会将两者都触发，此时攻击目标不会因为这两个奥秘改变。
			#健忘这个特性，如果满足触发条件，且错过了50%几率，之后再次满足条件时也不会再触发这个扳机。这个需要在每个食人魔随从上专门放上标记。
				#如果场上有多个食人魔勇士，则这些扳机都只会在第一次信号发出时触发。
			#如果一个攻击前步骤中，目标连续发生变化，如前面提到的游荡怪物和误导，则只会对最新的目标进行下一次攻击前步骤。
			#如果一个攻击前步骤中，目标连续发生变化，但最终又变回与初始目标相同，则不会产生新的攻击前步骤。

			#在之前的攻击前步骤中触发过的扳机不能再后续的额外攻击前步骤中再次触发，主要作用于傻子和市长，因为其他的攻击前扳机都是奥秘，触发之后即消失。
			#只有在攻击前步骤中可能有攻击目标的改变，之后的信号可以大胆的只传递目标本体，不用targetHolder
			while targetHolder[1] != targetHolder[0]: #这里的target只是refrence传递进来的target，赋值过程不会更改函数外原来的target
				targetHolder[0] = targetHolder[1] #攻击前步骤改变了攻击目标，则再次进行攻击前步骤，与这个新的目标进行比对。
				if self.GUI:
					self.GUI.target = targetHolder[0]
					self.GUI.wait(400)
				signal = subject.type+"Attacks"+targetHolder[0].type #产生新的触发信号。
				self.sendSignal(signal, self.turn, subject, targetHolder, 0, "FollowingPre-attack")
			target = targetHolder[1] #攻击目标改向结束之后，把targetHolder里的第二个值赋给target(用于重导向扳机的那个),这个target不是函数外的target了
			#攻击前步骤结束，开始结算攻击时步骤
			#攻击时步骤：触发“当xx攻击时”的扳机，如真银圣剑，血吼，智慧祝福，血吼，收集者沙库尔等
			signal = subject.type+"Attacking"+target.type
			self.sendSignal(signal, self.turn, subject, target, 0, "")
			#如果此时攻击者，攻击目标或者任意英雄濒死或离场所，则攻击取消，跳过伤害和攻击后步骤。
			battleContinues = True
			#如果目标随从变成了休眠物，则攻击会取消，但是不知道是否会浪费攻击机会。假设会浪费
			if ((subject.type != "Minion" and subject.type != "Hero") or not subject.onBoard or subject.health < 1 or subject.dead) \
				or ((target.type != "Minion" and target.type != "Hero") or not target.onBoard or target.health < 1 or target.dead) \
				or (self.heroes[1].health < 1 or self.heroes[1].dead or self.heroes[2].health < 1 or self.heroes[2].dead):
				battleContinues = False
				if useAttChance: subject.attTimes += 1 #If this attack is canceled, the attack time still increases.

			if battleContinues:
				#伤害步骤，攻击者移除潜行，攻击者对被攻击者造成伤害，被攻击者对攻击者造成伤害。然后结算两者的伤害事件。
				#攻击者和被攻击的血量都减少。但是此时尚不发出伤害判定。先发出攻击完成的信号，可以触发扫荡打击。
				if self.GUI: self.GUI.attackAni(subject, target)
				subject.attacks(target, useAttChance)
				#巨型沙虫的获得额外攻击机会的触发在随从死亡之前结算。同理达利乌斯克罗雷的触发也在死亡结算前，但是有隐藏的条件：自己不能处于濒死状态。
				self.sendSignal(subject.type+"Attacked"+target.type, self.turn, subject, target, 0, "")
				if subject == self.heroes[1] or subject == self.heroes[2]:
					self.Counters.heroAttackTimesThisTurn[subject.ID] += 1
			elif self.GUI: self.GUI.cancelAttack(subject)
			#重置蜡烛弓，角斗士的长弓，以及傻子和市长的trigedThisBattle标识。
			if resetRedirTrig: #这个选项目前只有让一个随从连续攻击其他目标时才会选择关闭，不会与角斗士的长弓冲突
				self.sendSignal("BattleFinished", self.turn, subject, None, 0, "")
			#战斗阶段结束，处理亡语，此时可以处理胜负问题。
			if resolveDeath:
				self.gathertheDead(True)
			for card in self.Hand_Deck.hands[1] + self.Hand_Deck.hands[2]:
				card.effCanTrig()
				card.checkEvanescent()
			if verifySelectable:
				self.moves.append(("battle", subIndex, subWhere, tarIndex, tarWhere))
			return battleContinues

	#comment = "InvokedbyAI", "Branching-i", ""(GUI by default)
	def playSpell(self, spell, target, choice=0, comment=""):
		#古加尔的费用光环需要玩家的血量加护甲大于法术的当前费用或者免疫状态下才能使用
		if self.Manas.affordable(spell) and spell.available() and spell.selectionLegit(target, choice):
			#使用阶段：
				#支付费用，相关费用状态移除，包括血色绽放，墨水大师，卡雷苟斯以及暮陨者艾维娜。
				#奥秘和普通法术会进入不同的区域。法术反制触发的话会提前终止整个序列。
				#使用时步骤： 触发伊利丹，紫罗兰老师，法力浮龙等“每当你使用一张xx牌”的扳机
				#获得过载和双重法术。
			#结算阶段
				#目标随机化和修改：市长和扰咒术结算（有主副玩家和登场先后之分）
				#按牌面结算，泽蒂摩不算是扳机，所以只要法术开始结算时在场，那么后面即使提前离场也会使用第二次结算的法术对相信随从生效。
			#完成阶段：
				#如果该牌有回响，结算回响（没有其他牌可以让法术获得回响）
				#使用后步骤：触发“当你使用一张xx牌之后”的扳机，如狂野炎术士，西风灯神，星界密使和风潮的状态移除。

			#如果是施放的法术（非玩家亲自打出）
			#获得过载，与双生法术 -> 依照版面描述结算，如有星界密使或者风潮，这个法术也会被重复或者法强增益，但是不会触发泽蒂摩。 -> 星界密使和风潮的状态移除。
			#符文之矛和导演释放的法术也会使用风潮或者星界密使的效果。
			#西风灯神和沃拉斯的效果仅是获得过载和双生法术 ->结算法术牌面

			subIndex, subWhere = self.Hand_Deck.hands[spell.ID].index(spell), "Hand%d"%spell.ID
			if target:
				if isinstance(target, list):
					tarIndex, tarWhere = [], []
					for obj in target:
						if obj.onBoard:
							tarIndex.append(obj.pos)
							tarWhere.append(obj.type+str(obj.ID))
						else:
							tarIndex.append(self.Hand_Deck.hands[obj.ID].index(obj))
							tarWhere.append("Hand%d"%obj.ID)
				else: #非列表状态的target一定是炉石卡指定的
					tarIndex, tarWhere = target.pos, target.type+str(target.ID)
			else: tarIndex, tarWhere = 0, ''
			#支付法力值，结算血色绽放等状态。
			spell, mana, posinHand = self.Hand_Deck.extractfromHand(spell, enemyCanSee=not spell.description.startswith("Secret:"))
			try: spell, mana = spell.becomeswhenPlayed(choice)
			except: pass #如果随从没有爆能强化等，则无事发生。
			self.Manas.payManaCost(spell, mana)
			#请求使用法术，如果此时对方场上有法术反制，则取消后续序列。
			#法术反制会阻挡使用时扳机，如伊利丹和任务达人等。但是法力值消耗扳机，如血色绽放，肯瑞托法师会触发，从而失去费用光环
			#被反制掉的法术会消耗“下一张法术减费”光环，但是卡雷苟斯除外（显然其是程序员自己后写的）
			#被反制掉的法术不会触发巨人的减费光环，不会进入你已经打出的法术列表，不计入法力飓风的计数
			#被反制的法术不会被导演们重复施放
			#很特殊的是，连击机制仍然可以通过被反制的法术触发。所以需要一个本回合打出过几张牌的计数器
			#https://www.bilibili.com/video/av51236298?zw
			spellHolder, origSpell = [spell], spell
			self.sendSignal("SpellOKtoCast?", self.turn, spellHolder, None, mana, "")
			if not spellHolder:
				self.Counters.numCardsPlayedThisTurn[self.turn] += 1
			else:
				if origSpell != spellHolder[0]: spellHolder[0].cast()
				else:
					armedTrigs = self.armedTrigs("SpellBeenPlayed")
					self.Counters.cardsPlayedThisTurn[self.turn]["Indices"].append(spell.index)
					self.Counters.cardsPlayedThisTurn[self.turn]["ManasPaid"].append(mana)
					spell.played(target, choice, mana, posinHand, comment) #choice用于抉择选项，comment用于区分是GUI环境下使用还是AI分叉
					self.Counters.numCardsPlayedThisTurn[self.turn] += 1
					self.Counters.numSpellsPlayedThisTurn[self.turn] += 1
					self.Counters.cardsPlayedThisGame[self.turn].append(spell.index)
					if "~Corrupted~" in spell.index: self.Counters.corruptedCardsPlayed[self.turn].append(spell.index)
					#使用后步骤，触发“每当使用一张xx牌之后”的扳机，如狂野炎术士，西风灯神，星界密使的状态移除和伊莱克特拉风潮的状态移除。
					if spell.creator: self.Counters.createdCardsPlayedThisGame[self.turn] += 1
					self.sendSignal("SpellBeenPlayed", self.turn, spell, target, mana, posinHand, choice, armedTrigs)
					#完成阶段结束，处理亡语，此时可以处理胜负问题。
					self.gathertheDead(True)
					for card in self.Hand_Deck.hands[1] + self.Hand_Deck.hands[2]:
						card.effCanTrig()
						card.checkEvanescent()
				if not isinstance(tarIndex, list):
					self.moves.append(("playSpell", subIndex, subWhere, tarIndex, tarWhere, choice))
				else:
					self.moves.append(("playSpell", subIndex, subWhere, tuple(tarIndex), tuple(tarWhere), choice))
				self.Counters.shadows[spell.ID] += 1

	def availableWeapon(self, ID):
		return next((weapon for weapon in self.weapons[ID] if weapon.durability > 0 and weapon.onBoard), None)

	"""Weapon with target will be handle later"""
	def playWeapon(self, weapon, target, choice=0):
		ID = weapon.ID
		if self.Manas.affordable(weapon):
			#使用阶段
				#卡牌从手中离开，支付费用，费用状态移除，但是目前没有根据武器费用支付而产生响应的效果。
				#武器进场，此时武器自身的扳机已经可以开始触发。如公正之剑可以通过触发的伊利丹召唤的元素来触发，并给予召唤的元素buff
				#使用时步骤，触发“每当你使用一张xx牌”的扳机”，如伊利丹，无羁元素等
				#结算过载。
				#结算死亡，尚不处理胜负问题。
			#结算阶段:
				#根据市长和铜须的存在情况决定战吼触发次数和目标（只有一个武器有指向性效果）
				#结算战吼、连击
				#消灭你的旧武器，将列表中前面的武器消灭，触发“每当你装备一把武器时”的扳机。
				#结算死亡（包括武器的亡语。）
			#完成阶段
				#使用后步骤，触发“每当你使用一张xx牌”之后的扳机。如捕鼠陷阱和瑟拉金之种等
				#死亡结算，可以处理胜负问题。
			if self.GUI: self.GUI.showOffBoardTrig(weapon, alsoDisplayCard=True)
			subIndex, subWhere = self.Hand_Deck.hands[weapon.ID].index(weapon), "Hand%d"%weapon.ID
			if target:
				tarIndex, tarWhere = target.pos, target.type+str(target.ID)
			else: tarIndex, tarWhere = 0, ''
			#卡牌从手中离开，支付费用，费用状态移除，但是目前没有根据武器费用支付而产生响应的效果。
			weapon, mana, posinHand = self.Hand_Deck.extractfromHand(weapon, enemyCanSee=True)
			weaponIndex = weapon.index
			self.Manas.payManaCost(weapon, mana)
			#使用阶段，结算阶段。
			armedTrigs = self.armedTrigs("WeaponBeenPlayed")
			weapon.played(target, 0, mana, posinHand, comment="") #There are no weapon with Choose One.
			self.Counters.numCardsPlayedThisTurn[ID] += 1
			self.Counters.cardsPlayedThisTurn[ID]["Indices"].append(weaponIndex)
			self.Counters.cardsPlayedThisTurn[ID]["ManasPaid"].append(mana)
			self.Counters.cardsPlayedThisGame[ID].append(weaponIndex)
			#if "~Corrupted~" in weaponIndex: self.Counters.corruptedCardsPlayed[self.turn].append(weaponIndex)
			#完成阶段，触发“每当你使用一张xx牌”的扳机，如捕鼠陷阱和瑟拉金之种等。
			if weapon.creator: self.Counters.createdCardsPlayedThisGame[ID] += 1
			self.sendSignal("WeaponBeenPlayed", self.turn, weapon, target, mana, posinHand, 0, armedTrigs)
			#完成阶段结束，处理亡语，可以处理胜负问题。
			self.gathertheDead(True)
			for card in self.Hand_Deck.hands[1] + self.Hand_Deck.hands[2]:
				card.effCanTrig()
				card.checkEvanescent()
			self.moves.append(("playWeapon", subIndex, subWhere, tarIndex, tarWhere, 0))

	#只是为英雄装备一把武器。结算相对简单
	#消灭你的旧武器，新武器进场，这把新武器设置为新武器，并触发扳机。
	def equipWeapon(self, weapon):
		ID = weapon.ID
		if self.weapons[ID] != []: #There are currently weapons before it.
			for obj in self.weapons[ID]:
				#The destruction of the preivous weapons will be left to the gathertheDead() method.
				obj.destroyed() #如果此时英雄正在攻击，则蜡烛弓和角斗士的长弓仍然可以为英雄提供免疫，因为它们是依靠扳机的。

		self.weapons[ID].append(weapon)
		weapon.onBoard = True
		weapon.appears() #新武器的扳机在此登记。
		#武器被设置为英雄的新武器，触发“每当你装备一把武器时”的扳机。”
		weapon.setasNewWeapon()

	def playHero(self, heroCard, choice=0):
		ID = heroCard.ID
		if self.Manas.affordable(heroCard):
			#使用阶段
				#支付费用，费用状态移除
				#英雄牌进入战场
				#使用时步骤，触发“每当你使用一张xx牌”的扳机，如魔能机甲，伊利丹等。
				#新英雄的最大生命值，当前生命值以及护甲被设定为与旧英雄一致。获得英雄牌上标注的额外护甲。
				#使用阶段结束，结算死亡情况。
			#结算阶段
				#获得新的英雄技能
				#确定战吼触发的次数。
				#结算战吼和抉择。
				#结算阶段结束，处理死亡。
			#完成阶段
				#使用后步骤，触发“每当你使用一张xx牌之后”的扳机。如捕鼠陷阱和瑟拉金之种等
				#完成阶段结束，处理死亡，可以处理胜负问题。

			subIndex, subWhere = self.Hand_Deck.hands[heroCard.ID].index(heroCard), "Hand%d"%heroCard.ID
			#支付费用，以及费用状态移除
			heroCard, mana, posinHand = self.Hand_Deck.extractfromHand(heroCard, enemyCanSee=True)
			heroCardIndex = heroCard.index
			self.Manas.payManaCost(heroCard, mana)
			#使用阶段，结算阶段的处理。
			armedTrigs = self.armedTrigs("HeroCardBeenPlayed")
			heroCard.played(None, choice, mana, posinHand, comment="")
			self.Counters.numCardsPlayedThisTurn[ID] += 1
			self.Counters.cardsPlayedThisTurn[ID]["Indices"].append(heroCardIndex)
			self.Counters.cardsPlayedThisTurn[ID]["ManasPaid"].append(mana)
			self.Counters.cardsPlayedThisGame[ID].append(heroCardIndex)
		#完成阶段
			#使用后步骤，触发“每当你使用一张xx牌之后”的扳机，如捕鼠陷阱等。
			if heroCard.creator: self.Counters.createdCardsPlayedThisGame[self.turn] += 1
			self.sendSignal("HeroCardBeenPlayed", self.turn, heroCard, None, mana, posinHand, choice, armedTrigs)
			#完成阶段结束，处理亡语，可以处理胜负问题。
			self.gathertheDead(True)
			for card in self.Hand_Deck.hands[1] + self.Hand_Deck.hands[2]:
				card.effCanTrig()
				card.checkEvanescent()
			self.moves.append(("playHero", subIndex, subWhere, 0, "", choice))

	def createCopy(self, game):
		return game

	def copyGame(self, num=1):
		#start = datetime.now()
		copies = [Game(self.GUI) for i in range(num)]
		for Copy in copies:
			Copy.copiedObjs = {}
			Copy.mainPlayerID, Copy.GUI = self.mainPlayerID, self.GUI
			Copy.cardPool, Copy.ClassCards, Copy.NeutralCards = self.cardPool, self.ClassCards, self.NeutralCards
			Copy.MinionsofCost, Copy.RNGPools = self.MinionsofCost, self.RNGPools
			#t1 = datetime.now()
			Copy.heroes = {1: self.heroes[1].createCopy(Copy), 2: self.heroes[2].createCopy(Copy)}
			Copy.powers = {1: self.powers[1].createCopy(Copy), 2: self.powers[2].createCopy(Copy)}
			Copy.weapons = {1: [weapon.createCopy(Copy) for weapon in self.weapons[1]], 2: [weapon.createCopy(Copy) for weapon in self.weapons[2]]}
			Copy.Hand_Deck = self.Hand_Deck.createCopy(Copy)
			Copy.minions = {1: [minion.createCopy(Copy) for minion in self.minions[1]],
							2: [minion.createCopy(Copy) for minion in self.minions[2]]}
			#t2 = datetime.now()
			#print("Time to copy characters onBoard", datetime.timestamp(t2)-datetime.timestamp(t1))
			#t1 = datetime.now()
			Copy.trigAuras = {ID: [aura.createCopy(Copy) for aura in self.trigAuras[ID]] for ID in range(1, 3)}
			Copy.mulligans, Copy.options, Copy.tempDeads, Copy.deads = {1:[], 2:[]}, [], [[], []], [[], []]
			Copy.Counters, Copy.Manas = self.Counters.createCopy(Copy), self.Manas.createCopy(Copy)
			Copy.minionPlayed, Copy.gameEnds, Copy.turn, Copy.numTurn = None, self.gameEnds, self.turn, self.numTurn
			Copy.resolvingDeath = False
			Copy.tempImmuneStatus = self.tempImmuneStatus
			Copy.status = copy.copy(self.status)
			Copy.players = self.players
			Copy.Discover = self.Discover.createCopy(Copy)
			Copy.Secrets = self.Secrets.createCopy(Copy)
			#t2 = datetime.now()
			#print("Time to copy various Handlers", datetime.timestamp(t2)-datetime.timestamp(t1))
			#t1 = datetime.now()
			#t2 = datetime.now()
			#print("Time to copy Hands/Decks", datetime.timestamp(t2)-datetime.timestamp(t1))
			#t1 = datetime.now()
			Copy.trigsBoard, Copy.trigsHand, Copy.trigsDeck = {1:{}, 2:{}}, {1:{}, 2:{}}, {1:{}, 2:{}}
			for trigs1, trigs2 in zip([Copy.trigsBoard, Copy.trigsHand, Copy.trigsDeck], [self.trigsBoard, self.trigsHand, self.trigsDeck]):
				for ID in range(1, 3):
					for sig in trigs2[ID].keys(): trigs1[ID][sig] = [trig.createCopy(Copy) for trig in trigs2[ID][sig]]
			Copy.turnStartTrigger, Copy.turnEndTrigger = [trig.createCopy(Copy) for trig in self.turnStartTrigger], [trig.createCopy(Copy) for trig in self.turnEndTrigger]
			#t2 = datetime.now()
			#print("Time to copy triggers", datetime.timestamp(t2)-datetime.timestamp(t1))
			Copy.mode = self.mode
			Copy.moves, Copy.fixedGuides, Copy.guides = copy.deepcopy(self.moves), copy.deepcopy(self.fixedGuides), copy.deepcopy(self.guides)
			del Copy.copiedObjs

		#finish = datetime.now()
		#print("Total time for copying %d games"%num, datetime.timestamp(finish)-datetime.timestamp(start))
		return copies

	def find(self, i, where):
		return {"Minion1": self.minions[1],
				"Minion2": self.minions[2],
				"Amulet1": self.minions[1],
				"Amulet2": self.minions[2],
				"Hero1": self.heroes, #For heroes, their position is kept the same as their ID
				"Hero2": self.heroes,
				"Power": self.powers,
				"Hand1": self.Hand_Deck.hands[1],
				"Hand2": self.Hand_Deck.hands[2],
				"Deck1": self.Hand_Deck.decks[1],
				"Deck2": self.Hand_Deck.decks[2],
				}[where][i]

	def evolvewithGuide(self, moves, guides):
		self.fixedGuides, self.guides = guides[:], guides[:]
		for move in moves:
			self.decodePlay(move)
			if self.GUI and move[0] != "EndTurn": self.GUI.wait(600)
		self.moves, self.fixedGuides, self.guides = [], [], []

	def decodePlay(self, move):
		if move[0] == "EndTurn": self.switchTurn()
		else:
			sub = self.find(move[1], move[2])
			if isinstance(move[3], tuple):
				tar = [(self.find(i, where) if where else None) for i, where in zip(move[3], move[4])]
			else:
				tar = self.find(move[3], move[4]) if move[4] else None
			if self.GUI: self.GUI.subject, self.GUI.target = sub, tar
			{"battle": lambda: self.battle(sub, tar),
			"Power": lambda: sub.use(tar, move[5]),
			"playMinion": lambda: self.playMinion(sub, tar, move[5], move[6]),
			"playAmulet": lambda: self.playAmulet(sub, tar, move[5], move[6]),
			"playWeapon": lambda: self.playWeapon(sub, tar, move[5]),
			"playSpell": lambda: self.playSpell(sub, tar, move[5]),
			"playHero": lambda: self.playHero(sub, move[5]),
			}[move[0]]()
			if self.GUI: self.GUI.subject, self.GUI.target = None, None