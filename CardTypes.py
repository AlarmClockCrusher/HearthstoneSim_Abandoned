import inspect
import copy
import numpy as np

from numpy.random import choice as npchoice
from numpy.random import randint as nprandint
from collections import Counter as cnt
from datetime import datetime

from Triggers_Auras import ManaMod, Aura_Receiver

def wrapTxt(s, CHN=True, wrapLength=11):
	if CHN:
		numSubstrings = int(len(s) / wrapLength) + 1 if len(s) % wrapLength else int(len(s) / wrapLength)
		if numSubstrings == 0: return ''
		elif numSubstrings == 1: return ' ' + s + '\n'
		else:
			substrings = [s[i*wrapLength:(i+1)*wrapLength] for i in range(numSubstrings-1)]
			substrings.append(s[(numSubstrings-1)*wrapLength:])
			return ' ' + "\n  ".join(substrings) + '\n'
	else:
		return wrapEng(s, int(1.6 * wrapLength))

def wrapEng(s, wrapLength):
	if len(s) > wrapLength: #"Savannah Highmane"
		#The currentLine stores at least one word, if the total length exceeds the limit, save the currentLine to substrings
		substrings, currentLine, words = [], '', s.split(' ')
		for word in words: #words = ["Savannah", "Highmane"]
			if currentLine == '': currentLine += word #string为空时，遇到一段文字之后，无论如何都要记录下来 string += "Savannah"
			else: #如果string不是空的话，则需要判断这个string加上下个单词之后是否会长度过长
				if len(currentLine + word) > wrapLength: #len("Savannah" + "Highmane") > lengthLimit
					substrings.append(currentLine) #substrings += "  Savannah\n"
					currentLine = word
				else: #If including the next word won't make it too long.
					currentLine += ' ' + word
		substrings.append(currentLine)
		return "  " + "\n   ".join(substrings) + '\n'
	return "  " + s + '\n'

def classforDiscover(initiator):
	Class = initiator.Game.heroes[initiator.ID].Class
	if Class != "Neutral": return Class #如果发现的发起者的职业不是中立，则返回那个职业
	elif initiator.Class != "Neutral": return initiator.Class.split(',')[0] #如果玩家职业是中立，但卡牌职业不是中立，则发现以那个卡牌的职业进行
	else: return initiator.Game.initialClasses[initiator.ID] #如果玩家职业和卡牌职业都是中立，则随机选取一个职业进行发现。

def count(listObj):
	count = {}
	for i in listObj:
		if i in count: count[i] += 1
		else: count[i] = 1
	return count
	
def countTypes(listObj):
	count = {}
	for i in listObj:
		T = type(i)
		if T in count: count[T] += 1
		else: count[T] = 1
	return count
	
#Return an empty tuple if num == 0 or listObj is empty
#If want to return 3 indices but there aren't enough different types, then return len-2 tuple
def npChoice_inds(listTypes, listInds, num):
	total = len(listTypes)
	if num == 0 or total < 1: return []
	elif num == 1: return [nprandint(total)]
	else:
		count, inds = {}, {}
		for T, i in zip(listTypes, listInds):
			if T in count:
				count[T] += 1
				inds[T].append(i)
			else:
				count[T], inds[T] = 1, [i]
		Ts = npchoice(list(count.keys()), min(num, total), p=[i / total for i in count.values()], replace=False)
		return [npchoice(inds[T]) for T in Ts] #从随机选出的inds里面再随机各选一个
		
def discoverProb(listObj):
	counts, total = cnt(listObj), len(listObj)
	if total: return list(counts.keys()), [value/total for value in counts.values()]
	else: return [], []

def copyListDictTuple(obj, recipient):
	if isinstance(obj, list):
		objCopy = []
		for element in obj:
			# check if they're basic types, like int, str, bool, NoneType,
			if isinstance(element, (type(None), int, float, str, bool)):
				# Have tested that basic types can be appended and altering the original won't mess with the content in the list.
				objCopy.append(element)
			elif callable(element):  # If the element is a function
				pass
			elif inspect.isclass(element):
				objCopy.append(element)
			elif type(element) == type(recipient.Game):
				objCopy.append(recipient.Game)
			elif type(element) == list or type(element) == dict or type(
					element) == tuple:  # If the element is a list or dict, just recursively use this function.
				objCopy.append(copyListDictTuple(element, recipient))
			else:  # If the element is a self-defined class. All of them have selfCopy methods.
				objCopy.append(element.selfCopy(recipient))
	elif isinstance(obj, dict):
		objCopy = {}
		for key, value in obj.items():
			if isinstance(value, (type(None), int, float, str, bool)):
				objCopy[key] = value
			# 随从的列表中不会引用游戏
			elif callable(value):
				pass
			elif inspect.isclass(value):
				objCopy[key] = value
			elif type(value) == type(recipient.Game):
				objCopy[key] = recipient.Game
			elif type(value) == list or type(value) == dict or type(value) == tuple:
				objCopy[key] = copyListDictTuple(value, recipient)
			else:
				objCopy[key] = value.selfCopy(recipient)
	else:  # elif isinstance(obj, tuple):
		tupleTurnedList = list(obj)  # tuple因为是immutable的，所以要根据它生成一个列表
		objCopy = copyListDictTuple(tupleTurnedList, recipient)  # 复制那个列表
		objCopy = list(objCopy)  # 把那个列表转换回tuple
	return objCopy

effectsDict = {"Taunt": "嘲讽", "Divine Shield": "圣盾", "Stealth": "潜行",
				"Lifesteal": "吸血", "Spell Damage": "法术伤害", "Poisonous": "剧毒",
				"Windfury": "风怒", "Mega Windfury": "超级风怒", "Charge": "冲锋", "Rush": "突袭",
				"Echo": "回响", "Reborn": "复生", "Bane": "毁灭", "Drain": "虹吸",

				"Cost Health Instead": "消耗生命值，而非法力值",
				"Sweep": "对攻击目标的相邻随从造成同样伤害",
				"Evasive": "无法成为法术或英雄技能的目标", "Enemy Evasive": "只有成为你的法术或英雄技能的目标",
				"Can't Attack": "无法攻击", "Can't Attack Hero": "无法攻击英雄",
				"Heal x2": "你的治疗效果翻倍",  # Crystalsmith Kangor
				"Power Heal&Dmg x2": "你的英雄技能的治疗或伤害翻倍",  # Prophet Velen, Clockwork Automation
				"Spell Heal&Dmg x2": "你的法术的治疗或伤害翻倍",
				"Enemy Effect Evasive": "敌方的能力无法指定此卡牌", "Enemy Effect Damage Immune": "因能力所受到的伤害皆转变为0",
				"Can't Break": "无法被能力破坏", "Can't Disappear": "无法被能力消失", "Can't Be Attacked": "无法对这个随从进行攻击", "Disappear When Die": "离场时消失",
				"Next Damage 0": "下一次受到的伤害转变为0", "Ignore Taunt": "可无视守护效果进行攻击", "Can't Evolve": "无法使用进化点进化", "Free Evolve": "不消费进化点即可进化",
				"Can Attack 3 times" : "一回合中可以进行3次攻击",

				"Immune": "免疫", "Frozen": "被冻结", "Temp Stealth": "潜行直到你的下个回合开始", "Borrowed": "被暂时控制",
				"Evolved": "已进化",
				}

class Card:
	Class = name = index = description = ''
	type = race = school = effects = ''
	mana = attack = health = durability = armor = 0
	requireTarget = False
	def __init__(self, Game, ID):
		cardType = type(self)
		self.Game, self.ID = Game, ID
		self.Class, self.name = cardType.Class, cardType.name
		self.type = cardType.type
		self.school, self.race, self.index = cardType.school, cardType.race, cardType.index
		self.mana, self.manaMods = cardType.mana, []
		# 当一个实例被创建的时候，其needTarget被强行更改为returnTrue或者是returnFalse，不论定义中如何修改needTarget(self, choice=0)这个函数，都会被绕过。需要直接对returnTrue()函数进行修改。
		self.needTarget = self.returnTrue if cardType.requireTarget else self.returnFalse
		self.description = cardType.description
		self.overload = self.twinSpell = self.magnetic = 0
		#法术也设置onBoard标签，但只是placeholder而已
		self.onBoard = self.inHand = self.inDeck = self.dead = False
		self.enterBoardTurn = self.enterHandTurn = 0
		self.seq, self.pos = -1, -2
		self.usageCount = 0
		self.attChances_base = -1
		
		#health_max is the health equivalent of attack_Enchant
		self.attack_0 = self.attack = self.attack_Enchant = cardType.attack
		self.health_0 = self.health = self.health_max = (cardType.health if cardType.health > 0 else cardType.durability)
		self.armor = cardType.armor
		
		self.trigsBoard, self.trigsHand, self.trigsDeck, self.deathrattles = [], [], [], []
		self.auras = {}
		self.auraReceivers = []
		self.options = []  #For Choose One spells
		
		self.effects = {}
		self.effectViable, self.evanescent = False, False
		#用于跟踪卡牌的可能性
		self.creator, self.tracked, self.possi = None, False, (cardType,)
		
		self.btn, self.x, self.y, self.z = None, 0, 0, 0

	def getMana(self):
		return self.mana

	def getTypewhenPlayed(self):
		return self.type
	#For Choose One cards.
	def needTarget(self, choice=0):
		return type(self).requireTarget

	def returnTrue(self, choice=0):
		return True

	def returnFalse(self, choice=0):
		return False

	def selfManaChange(self):
		pass

	#This is for battlecries with specific target requirement.
	def effCanTrig(self):
		pass

	def text(self, CHN):
		return ''

	def checkEvanescent(self):
		self.evanescent = any(trig.changesCard for trig in self.trigsBoard + self.trigsHand)
		
	#处理卡牌进入/离开 手牌/牌库时的扳机和各个onBoard/inHand/inDeck标签
	def entersHand(self):
		self.inHand = True
		self.onBoard = self.inDeck = False
		self.enterHandTurn = self.Game.numTurn
		for trig in self.trigsHand: trig.connect()
		return self

	def leavesHand(self, intoDeck=False):
		#将注册了的场上、手牌和牌库扳机全部注销。
		for trig in reversed(self.trigsBoard):
			trig.disconnect()
			#If the trig is temporary, it will be removed once it leaves hand, whether being discarded, played or shuffled into deck
			if not trig.inherent: self.trigsBoard.remove(trig)
		for trig in reversed(self.trigsHand):
			trig.disconnect()
			if not trig.inherent: self.trigsHand.remove(trig)
		for trig in reversed(self.trigsDeck): trig.disconnect() #没有给卡牌施加外来扳机的机制
		self.onBoard = self.inHand = self.inDeck = False
		#无论如果离开手牌，被移出还是洗回牌库，费用修改效果（如大帝-1）都会消失
		for manaMod in reversed(self.manaMods): manaMod.getsRemoved()
		self.manaMods = []

	def entersDeck(self):
		self.inDeck = True
		self.onBoard = self.inHand = False
		#Hand_Deck.shuffleintoDeck won't track the mana change.
		self.Game.Manas.calcMana_Single(self)
		for trig in self.trigsDeck: trig.connect()

	def leavesDeck(self, intoHand=True):
		#将注册了的场上、手牌和牌库扳机全部注销。
		for trig in reversed(self.trigsBoard):
			trig.disconnect()
			#If the trig is temporary, it will be removed once it leaves hand, whether being discarded, played or shuffled into deck
			if not trig.inherent: self.trigsBoard.remove(trig)
		for trig in reversed(self.trigsHand):
			trig.disconnect()
			if not trig.inherent: self.trigsHand.remove(trig)
		for trig in reversed(self.trigsDeck): trig.disconnect() #没有给卡牌施加外来扳机的机制
		self.onBoard = self.inHand = self.inDeck = False
		if not intoHand: #离开牌库时，只有去往手牌中时费用修改效果不会丢失。
			for manaMod in self.manaMods: manaMod.getsRemoved()
			self.manaMods = []

	def whenDrawn(self):
		pass

	def whenDiscarded(self):
		pass
	"""Handle the target selection. All methods belong to minions. Other types will define their own methods."""
	def need2Choose(self):
		return False
		
	def available(self):
		return True

	def targetCorrect(self, target, choice=0):
		return (target.type == "Minion" or target.type == "Hero") and target.onBoard

	def selectablebyBattle(self, subject):
				#攻击目标必须是在场上的没有潜行的敌方随从或英雄
				#被攻击目标必须能够被选择(没有免疫，潜行和“不能被攻击”)的随从或者英雄
				#攻击方如果有无视嘲讽，则不用判定嘲讽问题
		if self.onBoard and self.ID != subject.ID and self.effects["Temp Stealth"] < 1:
			if self.type == "Minion":
				return self.effects["Immune"] + self.effects["Stealth"] + self.effects["Can't Be Attacked"] < 1 \
						and (self.effects["Taunt"] > 0
							or not any(minion.effects["Taunt"] > 0 and minion.effects["Temp Stealth"] + minion.effects["Immune"] + minion.effects["Stealth"] < 1 for minion in self.Game.minionsonBoard(self.ID))
							or self.Game.effects[subject.ID]["Ignore Taunt"] > 0 or (subject.type == "Minion" and subject.effects["Ignore Taunt"]))
			elif self.type == "Hero":
				return self.Game.effects[self.ID]["Immune"] + self.Game.effects[self.ID]["Hero Can't Be Attacked"] < 1 \
						and not (subject.type == "Hero" and any(weapon.effects["Can't Attack Heroes"] > 0 for weapon in self.Game.weapons[subject.ID])) \
						and (not any(minion.effects["Taunt"] > 0 and minion.effects["Temp Stealth"] + minion.effects["Immune"] + minion.effects["Stealth"] < 1 for minion in self.Game.minionsonBoard(self.ID))
							or self.Game.effects[subject.ID]["Ignore Taunt"] > 0 or (subject.type == "Minion" and subject.effects["Ignore Taunt"]))
						#The last 2 lines handle the case of blockage by Taunt minions
		return False

	def canSelect(self, target):
		targets = target if isinstance(target, list) else [target]
		for target in targets:
			targetType = target.type
			selectable = False
			if target.onBoard and targetType in ("Hero", "Minion", "Amulet"):
				if targetType == "Hero":
					#如果英雄是敌方英雄且目前有潜行，免疫，且“不可被敌方效果指定”，则无论什么指向性效果都无法进行选择
					if target.ID != self.ID and self.Game.effects[target.ID]["Immune"] + target.effects["Temp Stealth"] + target.effects["Enemy Effect Evasive"] > 0:
						pass
					#如果subject是法术或者英雄技能，则如果英雄有魔免，或者对方英雄有对对方的魔免，则无法进行选择
					elif (self.type == "Power" or self.type == "Spell") and self.Game.effects[target.ID]["Evasive"] > 0:
						pass
					else: selectable = True #其余情况下可以选择一个英雄
				elif targetType == "Minion":
					#print("Checking if can select. Subject", self, self.type, "target:", target, target.type)
					#print("Is a spell that can't target evasive?", (self.type == "Power" or self.type == "Spell") \
					#	and (target.effects["Evasive"] > 1 or (target.ID != self.ID and target.effects["Enemy Evasive"] > 1)))
					#print("Is a spell or hero power?", self.type == "Power" or self.type == "Spell")
					#print("Target evasive?", target, target.effects, target.effects["Evasive"])
					#print("Is the target an evasive minion?", target.effects["Evasive"] > 0, target.ID != self.ID and target.effects["Enemy Evasive"] > 1)
					#如果目标随从是敌方的，且目前拥有免疫，潜行或者临时潜行，则无法进行选择
					if target.ID != self.ID and target.effects["Immune"] + target.effects["Stealth"] + target.effects["Temp Stealth"] + target.effects["Enemy Effect Evasive"] > 0:
						pass
					#如果subject是法术或者英雄技能，且目标随从有魔免，或者是一个有“对对方魔免”的对方随从，则无法进行选择
					elif (self.type == "Power" or self.type == "Spell") \
						and (target.effects["Evasive"] > 0 or (target.ID != self.ID and target.effects["Enemy Evasive"] > 0)):
						print("Evasive works on subject", self, "by", target)
						pass
					else: selectable = True
				elif targetType == "Amulet":
					if target.ID != self.ID and target.effects["Enemy Effect Evasive"] > 0:
						pass
					elif self.type == "Spell" and target.effects["Evasive"] > 0:
						pass
					else: selectable = True
					
			#selectable = target.onBoard and targetType != "Dormant" and targetType != "Power" and \
			#			 (
			#				(targetType == "Hero" and (target.ID == self.ID or self.Game.effects[target.ID]["Immune"] + target.effects["Temp Stealth"] + target.effects["Enemy Effect Evasive"] < 1) \
			#											and not ((self.type == "Power" or self.type == "Spell") and self.Game.effects[target.ID]["Evasive"] > 1)) \
			#				#不能被法术或者英雄技能选择的随从是： 魔免随从 或者 是对敌方魔免且法术或英雄技能是敌方的
			#				or (targetType == "Minion" and (target.ID == self.ID or target.effects["Immune"] + target.effects["Stealth"] + target.effects["Temp Stealth"] + target.effects["Enemy Effect Evasive"] < 1) \
			#												and not ((self.type == "Power" or self.type == "Spell") and (target.effects["Evasive"] > 1 or (target.ID != self.ID and target.effects["Enemy Evasive"] > 1)))) \
			#				or (targetType == "Amulet" and (target.ID == self.ID or target.effects["Enemy Effect Evasive"] < 1) \
			#												and not (self.type == "Spell" and target.effects["Evasive"] > 1)) \
			#
			#				)
			if not selectable: return False
		return True

	def selectableEnemyMinionExists(self, choice=0):
		return any(minion.type == "Minion" and minion.onBoard and self.canSelect(minion) and self.targetCorrect(minion, choice) \
					for minion in self.Game.minions[3-self.ID])

	def selectableFriendlyMinionExists(self, choice=0):
		return any(minion.type == "Minion" and minion.onBoard and self.canSelect(minion) and self.targetCorrect(minion, choice) \
					for minion in self.Game.minions[self.ID])

	def selectableEnemyAmuletExists(self, choice=0):
		return any(minion.type == "Amulet" and minion.onBoard and self.canSelect(minion) and self.targetCorrect(minion, choice) \
					for minion in self.Game.minions[3-self.ID])

	def selectableFriendlyAmuletExists(self, choice=0):
		return any(minion.type == "Amulet" and minion.onBoard and self.canSelect(minion) and self.targetCorrect(minion, choice) \
					for minion in self.Game.minions[self.ID])

	def selectableMinionExists(self, choice=0):
		return self.selectableFriendlyMinionExists(choice) or self.selectableEnemyMinionExists(choice)

	def selectableEnemyExists(self, choice=0):
		hero = self.Game.heroes[3-self.ID]
		return (self.canSelect(hero) and self.targetCorrect(hero, choice)) or self.selectableEnemyMinionExists(choice)

	#There is always a selectable friendly character -- hero.
	def selectableFriendlyExists(self, choice=0): #For minion battlecries, the friendly hero is always selectable
		hero = self.Game.heroes[self.ID]
		return (self.type != "Spell" or self.type != "Power") \
				or (self.canSelect(hero) and self.targetCorrect(hero, choice) or self.selectableFriendlyMinionExists(choice))

	def selectableCharacterExists(self, choice=0):
		return self.selectableFriendlyExists(choice) or self.selectableEnemyExists(choice)

	#For targeting battlecries(Minions/Weapons)
	def targetExists(self, choice=0):
		return True

	def selectionLegit(self, target, choice=0):
		#抉择牌在有全选光环时，选项自动更正为一个负数。
		choice -= 3 * (self.need2Choose() and self.Game.effects[self.ID]["Choose Both"] > 0)
		if target: #指明了目标
			#在指明目标的情况下，只有抉择牌的选项是合理的，选项需要目标，目标对于这个选项正确，且目标可选时，才能返回正确。
			print("Checking if selecting target is correct", self, target)
			return self.needTarget(choice) and self.targetCorrect(target, choice) and self.canSelect(target)
		else: #打出随从如果没有指定目标，则必须是其不要求目标或没有目标。
			return not self.needTarget(choice) or ((self.type == "Minion" or self.type == "Amulet") and not (self.needTarget(choice) and self.targetExists(choice)))

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		return target

	def countSpellDamage(self):
		return self.Game.effects[self.ID]["Spell Damage"] + (self.school == "Fire" and self.Game.effects[self.ID]["Fire Spell Damage"])\
				+ sum(minion.effects["Spell Damage"] or (minion.effects["Nature Spell Damage"] and self.school == "Nature")
					  for minion in self.Game.minions[self.ID])

	def dmgtoDeal(self, dmg, role="att"):
		return dmg

	def dmgtoRec(self, dmg, role="def"):
		return dmg

	"""Handle the card doing battle(Minion and Hero)"""
	def decideAttChances_base(self):
		if self.type == "Minion":
			if self.effects["Mega Windfury"] > 0: self.attChances_base = 4
			elif self.effects["Can Attack 3 times"] > 0: self.attChances_base = 3
			elif self.effects["Windfury"] > 0: self.attChances_base = 2
			else: self.attChances_base = 1
			if self.btn: self.btn.effectChangeAni("Exhausted")
		elif self.type == "Hero":
			weapon = self.Game.availableWeapon(self.ID)
			self.attChances_base = 2 if self.effects["Windfury"] > 0 or (weapon and weapon.effects["Windfury"] > 0) else 1
		
	def actionable(self):
		# 不考虑冻结、零攻和自身有不能攻击的debuff的情况。
		if self.type == "Minion":
			# 判定随从是否处于刚在我方场上登场，以及暂时控制、冲锋、突袭等。
			# 如果随从是刚到我方场上，则需要分析是否是暂时控制或者是有冲锋或者突袭。
			# 随从已经在我方场上存在一个回合。则肯定可以行动。
			return self.onBoard and self.ID == self.Game.turn and \
				   (self.enterBoardTurn != self.Game.numTurn or (self.effects["Borrowed"] > 0 or self.effects["Charge"] > 0 or self.effects["Rush"] > 0))
		elif self.type == "Hero": return self.ID == self.Game.turn
		else: return False
		
	#Game.battle() invokes this function.
	#我方有扫荡打击的狂暴者攻击对方相邻的两个狂暴者之一，然后扫荡打击在所有受伤开始之前触发，
	#然后被攻击的那个狂暴者先受伤加攻，然后我方的狂暴者受伤加攻，最后是被AOE波及的那个狂暴者加攻。
	#说明扫荡打击是把相邻的随从列入伤害处理列表 ，主要涉及的两个随从是最先结算的两个，
	#被扫荡打击涉及的两个随从从左到右依次结算。
	def attacks(self, target, useAttChance=True):
		game = self.Game
		subjectAtt, targetAtt = [max(0, self.attack)], [max(0, target.attack)]
		self.losesEffect("Stealth", 0)
		self.losesEffect("Temp Stealth", 0)
		if useAttChance: self.usageCount += 1

		dmgList = []
		#如果攻击者是英雄且装备着当前回合打开着的武器，则将攻击的伤害来源视为那把武器。
		weapon = game.availableWeapon(self.ID)
		dmgDealer_att = weapon if self.type == "Hero" and weapon and self.ID == game.turn else self
		#如果被攻击者是英雄，且装备着当前回合打开着的武器，则将攻击目标造成的伤害来源视为那把武器。
		weapon = game.availableWeapon(target.ID)
		dmgDealer_def = weapon if target.type == "Hero" and weapon and target.ID == game.turn else target
		#Manipulate the health of the subject/target's health.
		#Only send out "MinionTakesDmg" signal at this point.
		#首先结算攻击者对于攻击目标的伤害，如果攻击力小于1，则攻击目标不会被记入伤害处理列表。
		#注意这个伤害承受目标不一定是攻击目标，因为有博尔夫碎盾以及钳嘴龟持盾者的存在
		#承受伤害者的血量减少，结算剧毒，但是此时不会发出受伤信号。
		dmgTaker = game.scapegoat4(target, dmgDealer_att)
		game.sendSignal("BattleDmg" + target.type, 0, dmgDealer_att, target, subjectAtt, "") #不能把这个东西写入和伤害承受目标判定同时进行的结算，因为存在互相干扰的情况
		dmgActual = dmgTaker.takesDamage(dmgDealer_att, subjectAtt[0], sendDmgSignal=False, damageType="Battle")
		if dmgActual: dmgList.append((dmgDealer_att, dmgTaker, dmgActual))

		#寻找受到攻击目标的伤害的角色。同理，此时受伤的角色不会发出受伤信号，这些受伤信号会在之后统一发出。
		dmgTaker = game.scapegoat4(self, dmgDealer_def)
		game.sendSignal("BattleDmg" + target.type, 0, target, dmgDealer_def, targetAtt, "") #不能把这个东西写入和伤害承受目标判定同时进行的结算，因为存在互相干扰的情况
		dmgActual = dmgTaker.takesDamage(dmgDealer_def, targetAtt[0], sendDmgSignal=False, damageType="Battle")
		if dmgActual: dmgList.append((dmgDealer_def, dmgTaker, dmgActual))
		dmg_byDef = dmgActual #The damage dealt by the character under attack
		#如果攻击者的伤害来源（随从或者武器）有对相邻随从也造成伤害的扳机，则将相邻的随从录入处理列表。
		if dmgDealer_att.type != "Hero" and dmgDealer_att.effects["Sweep"] > 0 and target.type == "Minion":
			neighbors = game.neighbors2(target)[0] #此时被攻击的随从一定是在场的，已经由Game.battleRequest保证。
			for minion in neighbors:
				dmgTaker = game.scapegoat4(minion, dmgDealer_att)
				#目前假设横扫时造成的战斗伤害都一样，不会改变。毕竟炉石里面没有相似的效果
				dmgActual = dmgTaker.takesDamage(dmgDealer_att, subjectAtt[0], sendDmgSignal=False, damageType="Ability")
				if dmgActual: dmgList.append((dmgDealer_att, dmgTaker, dmgActual))

		if dmgDealer_att.type == "Weapon": dmgDealer_att.loseDurability()
		dmg_byAtt = 0 #The damage dealt by the character that attacks
		for dmgDealer, dmgTaker, damage in dmgList:
			#参与战斗的各方在战斗过程中只减少血量，受伤的信号在血量和受伤名单登记完毕之后按被攻击者，攻击者，被涉及者顺序发出。
			game.sendSignal(dmgTaker.type+"TakesDmg", 0, dmgDealer, dmgTaker, damage, "")
			game.sendSignal(dmgTaker.type+"TookDmg", 0, dmgDealer, dmgTaker, damage, "")
			#吸血扳机始终在队列结算的末尾。
			dmgDealer.tryLifesteal(damage, damageType="Battle")
			dmg_byAtt += damage
		if dmg_byAtt: game.sendSignal("DealtDmg", 0, dmgDealer_att, None, dmg_byAtt, "")
		if dmg_byDef: game.sendSignal("DealtDmg", 0, dmgDealer_def, None, dmg_byDef, "")
		
	# 对于Game.status的变更，需要在Game.changeStatus里面寻找
	# 对于暂时因为某种aura而获得关键字的情况，直接在effectfromAura里面添加对应的关键字，但是不注册receiver
	def getsEffect(self, name, amount=1):
		if not self.inDeck:
			prev = now = 0
			if name in self.effects:
				prev = self.effects[name]
				self.effects[name] += amount
			elif name in self.Game.effects[self.ID]:
				prev = self.Game.effects[self.ID][name]
				self.Game.effects[self.ID][name] += amount
			if self.onBoard and (self.type == "Minion" or self.type == "Hero"):
				self.decideAttChances_base()
				if prev < 1: self.Game.sendSignal("CharGets_"+name, self.Game.turn, self, None, 0, "")
			if (self.onBoard or self.inHand) and self.btn:
				if name in ("Lifesteal", "Poisonous"): self.btn.placeIcons()
				else: self.btn.effectChangeAni(name)
				
	# 当随从失去关键字的时候不可能有解冻情况发生。
	def losesEffect(self, name, amount=1): #当角色失去所有keyWords时，amount需要小于0
		if not self.inDeck:
			prev = now = 0
			if name in self.effects:
				prev = self.effects[name]
				now = self.effects[name] = max(0, self.effects[name] - amount) if amount > 0 else 0
			elif name in self.Game.effects[self.ID]:
				prev = self.Game.effects[self.ID][name]
				now = self.Game.effects[self.ID][name] = max(0, self.Game.effects[self.ID][name] - amount) if amount > 0 else 0
			if self.onBoard:
				self.decideAttChances_base()
				if now < 1 and now < prev: self.Game.sendSignal("CharLoses_"+name, self.Game.turn, self, None, 0, "")
			if (self.onBoard or self.inHand) and self.btn: #Lifesteal, Poisonous, Deathrattle and Trig will show up at the bottom of the minion icon
				if name not in ("Lifesteal", "Poisonous"): self.btn.effectChangeAni(name)
				else: self.btn.placeIcons()
	
	#Can acquire trigBoard, deathrattle
	def getsTrig(self, trig, trigType="TrigBoard", connect=True):
		trig.inherent = False
		{"TrigBoard": self.trigsBoard,
		"Deathrattle": self.deathrattles,
		"TrigHand": self.trigsHand}[trigType].append(trig)
		if connect: trig.connect()
		if self.btn: self.btn.placeIcons()
		
	def losesTrig(self, trig, trigType="TrigBoard", all=False):
		if all:
			for trig in self.trigsBoard + self.deathrattles + self.trigsHand + self.trigsDeck:
				trig.disconnect()
			self.trigsBoard, self.deathrattles, self.trigsHand, self.trigsDeck = [], [], [], []
		else:
			ls = {"TrigBoard": self.trigsBoard,
			 	"Deathrattle": self.deathrattles,
			 	"TrigHand": self.trigsHand}[trigType]
			if trig in ls: ls.remove(trig)
			trig.disconnect()
		if self.btn: self.btn.placeIcons()
	
	"""Handle cards dealing targeting/AOE damage/heal to target(s)."""
	#Handle Lifesteal of a card. Currently Minion/Weapon/Spell classs have this method.
	##法术因为有因为外界因素获得吸血的能力，所以有自己的tryLifesteal方法。
	def tryLifesteal(self, damage, damageType="None"):
		game = self.Game
		if self.effects["Lifesteal"] > 0 or (self.type == "Spell" and game.effects[self.ID]["Spells Lifesteal"] > 0)\
				or (damageType == "Battle" and "Drain" in self.effects and self.effects["Drain"] > 0):
			heal = damage * (2 ** self.countHealDouble())
			if game.effects[self.ID]["Heal to Damage"] > 0:
				#If the Lifesteal heal is converted to damage, then the obj to take the final
				#damage will not cause Lifesteal cycle.
				dmgTaker = self.Game.scapegoat4(game.heroes[self.ID])
				dmgTaker.takesDamage(self, heal, damageType="Ability")
			elif game.effects[self.ID]["Lifesteal Damages Enemy"] > 0:
				dmgTaker = self.Game.scapegoat4(game.heroes[3-self.ID])
				dmgTaker.takesDamage(self, heal, damageType="Ability")
			else: #Heal is heal.
				GUI = self.Game.GUI
				if GUI and "Lifesteal" in self.btn.icons:
					icon = self.btn.icons["Lifesteal"]
					GUI.seqHolder[-1].append(GUI.PARALLEL(GUI.FUNC(icon.trigAni), GUI.WAIT(0.25)))
				game.heroes[self.ID].getsHealed(self, heal)

	#可以对在场上以及手牌中的随从造成伤害，同时触发应有的响应，比如暴乱狂战士和+1攻击力和死亡缠绕的抽牌。
	#牌库中的和已经死亡的随从免疫伤害，但是死亡缠绕可以触发抽牌。
	#吸血同样可以对于手牌中的随从生效并为英雄恢复生命值。如果手牌中的随从有圣盾，那个圣盾可以抵挡伤害，那个随从在打出后没有圣盾（已经消耗）。
	#暂时可以考虑不把吸血做成场上扳机，因为几乎没有战吼随从可以获得吸血，直接将吸血视为随从的dealsDamage自带属性也可以。
	def dealsDamage(self, target, damage):
		damage = [damage]
		if target.onBoard or target.inHand:
			if self.Game.GUI:
				self.Game.GUI.targetingEffectAni(self, target, damage[0])
			dmgTaker = self.Game.scapegoat4(target, self)
			#超杀和造成伤害触发的效果为场上扳机.吸血始终会在队列的末尾结算。
			#战斗时不会调用这个函数，血量减少时也不立即发生伤害信号，但是这里是可以立即发生信号触发扳机的。
			#如果随从或者英雄处于可以修改伤害的效果之下，如命令怒吼或者复活的铠甲，伤害量会发生变化
			self.Game.sendSignal("AbilityDmg" + target.type, 0, self, target, damage, "")  # 不能把这个东西写入和伤害承受目标判定同时进行的结算，因为存在互相干扰的情况
			dmgActual = dmgTaker.takesDamage(self, damage[0], damageType="Ability")
			self.tryLifesteal(dmgActual, "Ability")
			if dmgActual: self.Game.sendSignal("DealtDmg", 0, self, None, dmgActual, "")
			return dmgTaker, dmgActual
		else: return target, 0 #The target is neither on board or in hand. Either removed already or shuffled into deck.

	#The targets can be [], [subject], [subject1, subject2, ...]
	#For now, AOE will only affect targets that are on board. No need to check if the target is dead, in hand or in deck.
	#当场上有血量为2的奥金尼和因为欧米茄灵能者获得的法术吸血时，神圣新星杀死奥金尼仍然会保留治疗转伤害的效果。
	#有的扳机随从默认随从需要在非濒死情况下才能触发扳机，如北郡牧师。
	def dealsAOE(self, targets, damages):
		game = self.Game
		targets, damages = targets[:], damages[:]
		dmgTakers, dmgsActual, totalDmg = [], [], 0
		if targets and game.GUI:
			game.GUI.AOEAni(self, targets, damages)
		for target, damage in zip(targets, damages):
			dmg = [damage]
			dmgTaker = game.scapegoat4(target, self)
			#Handle the Divine Shield and Commanding Shout here.
			self.Game.sendSignal("AbilityDmg" + target.type, 0, self, target, dmg, "")  # 不能把这个东西写入和伤害承受目标判定同时进行的结算，因为存在互相干扰的情况
			dmgActual = dmgTaker.takesDamage(self, dmg[0], sendDmgSignal=False, damageType="Ability")
			if dmgActual > 0:
				dmgTakers.append(dmgTaker)
				dmgsActual.append(dmgActual)
				totalDmg += dmgActual
		#AOE首先计算血量变化，之后才发出伤害信号。
		for target, dmgActual in zip(dmgTakers, dmgsActual):
			game.sendSignal(target.type+"TakesDmg", self.ID, self, target, dmgActual, "")
			game.sendSignal(target.type+"TookDmg", self.ID, self, target, dmgActual, "")
		self.tryLifesteal(totalDmg, "Ability")
		if totalDmg: game.sendSignal("DealtDmg", 0, self, None, totalDmg, "")
		return dmgTakers, dmgsActual, totalDmg

	def restoresAOE(self, targets, heals):
		game = self.Game
		targets_Heal, heals = targets[:], heals[:]
		if game.effects[self.ID]["Heal to Damage"] > 0:
			dmgTakers, dmgsActual, totalDmgDone = self.dealsAOE(targets_Heal, heals)
			healsActual = [-damage for damage in dmgsActual]
			return dmgTakers, healsActual, -totalDmgDone #对于AOE回复，如果反而造成伤害，则返回数值为负数
		else:
			targets_healed, healsActual, totalHealDone = [], [], 0
			if targets and game.GUI:
				game.GUI.AOEAni(self, targets, heals, color="green3")
			for target, heal in zip(targets, heals):
				healActual = target.getsHealed(self, heal, sendHealSignal=False)
				if healActual > 0:
					targets_healed.append(target)
					healsActual.append(healActual)
					totalHealDone += healActual
			containHero = False
			for target, healActual in zip(targets_healed, healsActual):
				game.sendSignal(target.type+"GetsHealed", game.turn, self, target, healActual, "")
				game.sendSignal(target.type+"GotHealed", game.turn, self, target, healActual, "")
				if target.type == "Hero":
					containHero = target.ID
			if containHero:
				game.sendSignal("AllCured", containHero, self, None, 0, "")
			else:
				game.sendSignal("MinionsCured", game.turn, self, None, 0, "")
		return targets_healed, healsActual, totalHealDone

	def restoresHealth(self, target, heal):
		if self.Game.effects[self.ID]["Heal to Damage"] > 0:
			dmgTaker, dmgActual = self.dealsDamage(target, heal)
			return dmgTaker, -dmgActual
		else:
			#if self.Game.GUI:
			#	self.Game.GUI.targetingEffectAni(self, target, heal, color="green3")
			healActual = target.getsHealed(self, heal)
			return target, healActual

	#Lifesteal will only calc once with Aukenai,  for a lifesteal damage spell,
	#the damage output is first enhanced by spell damage, then the lifesteal is doubled by Kangor, then the doubled healing is converted by the Aukenai.
	#Heal is heal at this poin. The Auchenai effect has been resolved before this function
	def getsHealed(self, subject, heal, sendHealSignal=True):
		game, healActual = self.Game, 0
		if self.inHand or self.onBoard:#If the character is dead and removed already or in deck. Nothing happens.
			#This doesn't check if the heal actually changes anything.
			game.sendSignal(self.type + "ReceivesHeal", game.turn, subject, self, 0, "")
			if self.health < self.health_max:
				healActual = heal if self.health + heal < self.health_max else self.health_max - self.health
				self.health += healActual
				if self.btn: self.btn.statChangeAni(num2=healActual, action="heal")
				if sendHealSignal: #During AOE healing, the signals are delayed.
					game.sendSignal(self.type+"GetsHealed", game.turn, subject, self, healActual, "")
				game.Counters.healthRestoredThisGame[subject.ID] += healActual
				game.Counters.healthRestoredThisTurn[subject.ID] += healActual
				if self.type == "Minion":
					game.sendSignal("MinionStatCheck", self.ID, None, self, 0, "")
				elif game.turn == self.ID:
					game.Counters.timesHeroChangedHealth_inOwnTurn[self.ID] += 1
					game.Counters.heroChangedHealthThisTurn[self.ID] = True
					game.sendSignal("HeroChangedHealthinTurn", self.ID, None, None, 0, "")
				if sendHealSignal: #During AOE healing, the signals are delayed.
					game.sendSignal(self.type+"GotHealed", game.turn, subject, self, healActual, "")
		return healActual

	def rngPool(self, identifier):
		pool = self.Game.RNGPools[identifier][:]
		try: pool.remove(type(self))
		except: pass
		return pool


	"""Common statChange/buffDebuff"""
	# attRevertTime = "' or "EndofTurn" or "StartofTurn 1" or "StartofTurn 2"
	def buffDebuff(self, attackGain, healthGain, attRevertTime=''):
		if self.type == "Minion":
			if not self.inDeck and not self.dead:  # 只有随从在场上或者手牌中的时候可以接受buff。
				if attRevertTime == "": self.attack_Enchant += attackGain# 在场上和手牌中都可以接受永久buff
				# Minions can receive temp attack changes, too. And those will also vanish at the corresponding time point.
				else: self.tempAttChanges.append((attackGain, attRevertTime))
				self.statChange(attackGain, healthGain, action="buffDebuff")
				if attackGain > 0 or healthGain > 0:
					self.Game.sendSignal("MinionBuffed", self.ID, self, None, 0, "")
		elif self.type == "Weapon":
			self.attack_Enchant += attackGain
			self.health_max += healthGain
			self.statChange(attackGain, healthGain)
			
	# Generally invoked by Stat_Receivers and buffDebuff.
	def statChange(self, attGain, healthGain=0, action="set"):
		if self.type == "Minion":
			self.attack += attGain
			self.health_max += healthGain
			if healthGain >= 0: self.health += healthGain
			else:  # When the buffAura is gone.
				self.health_max = max(1, self.health_max)
				self.health = min(self.health, self.health_max)
			if self.btn: self.btn.statChangeAni(num1=attGain, num2=healthGain, action=action)
			self.Game.sendSignal("MinionStatCheck", self.ID, None, self, 0, "")
		elif self.type == "Weapon":
			self.attack += attGain
			self.health += healthGain
			hero = self.Game.heroes[self.ID]
			hero.calc_Attack()
			if self.btn: self.btn.statChangeAni(num1=attGain, num2=healthGain, action="buffDebuff")
			if hero.btn: hero.btn.statChangeAni(num1=0, action="buffDebuff")
			self.Game.sendSignal("WeaponAttChanges", self.ID, None, None, 0, "")
	
	"""Common discover handlers"""
	#因为所有发现界面的东西才会进行picks的读取，所以即使是跳过人工发现的随机过程也需要上。
	#即使这一个发现可能没有问题，也可能会有连续发现的情况，导致出现问题
	
	#默认的discoverDecided是把一张生成的卡牌加入手牌中
	def discoverDecided(self, option, case, info_RNGSync=None, info_GUISync=None):
		self.handleDiscoverGeneratedCard(option, case, info_RNGSync, info_GUISync)
	
	def discoverandGenerate(self, effectType, comment, poolFunc):
		game, ID = self.Game, self.ID
		if self.type == "Minion" and ID != game.turn:
			return
		if game.mode == 0:
			if game.picks:
				info_RNGSync, info_GUISync, isRandom, cardType = game.picks.pop(0) #, info_GUISync is (numOption, indexOption)
				if not cardType: return
				#For discoverandGenerate, info_RNGSync is simply poolSize
				npchoice(range(info_RNGSync), info_GUISync[0], replace=False)
				card = cardType(game, ID)
				if game.GUI: game.GUI.discoverDecideAni(isRandom=isRandom, numOption=info_GUISync[0], indexOption=info_GUISync[1], options=card)
				effectType.discoverDecided(self, card, case="Guided", info_RNGSync=info_RNGSync, info_GUISync=info_GUISync)
			else:
				pool = poolFunc()
				if not pool: game.picks_Backup.append((None, None, None, None))
				else:
					numOption = min(3, len(pool))
					options = npchoice(pool, numOption, replace=False)
					if ID != game.turn or "byOthers" in comment:
						i = datetime.now().microsecond % numOption
						#info_RNGSync=poolSize, info_GUISync = [numOption, i]
						card = options[i](game, ID)
						if game.GUI: game.GUI.discoverDecideAni(isRandom=True, numOption=numOption, indexOption=i, options=card)
						effectType.discoverDecided(self, card, case="Random", info_RNGSync=len(pool), info_GUISync=(numOption, i))
					else:
						game.options = [card(game, ID) for card in options]
						#info_RNGSync=poolSize, info_GUISync = [numOption] #discover will add the indexOption to info_GUISync
						game.Discover.startDiscover(self, effectType=effectType, info_RNGSync=len(pool), info_GUISync=[numOption])
	
	def discoverandGenerate_MultiplePools(self, effectType, comment, poolsFunc):
		game, ID = self.Game, self.ID
		if self.type == "Minion" and ID != game.turn:
			return
		if game.mode == 0:
			if game.picks:
				info_RNGSync, info_GUISync, isRandom, card = game.picks.pop(0)
				for poolSize in info_RNGSync: npchoice(range(poolSize))
				card = card(game, ID)
				if game.GUI: game.GUI.discoverDecideAni(isRandom=isRandom, numOption=info_GUISync[0], indexOption=info_GUISync[1], options=card)
				effectType.discoverDecided(self, card, case="Guided", info_RNGSync=info_RNGSync, info_GUISync=info_GUISync)
			else:
				pools = poolsFunc()
				#Such pools is definitely non-empty
				if ID != game.turn or "byOthers" in comment:
					i = datetime.now().microsecond % len(pools)
					card = npchoice(pools[i])(game, ID)
					if game.GUI: game.GUI.discoverDecideAni(isRandom=True, numOption=len(pools), indexOption=i, options=card)
					effectType.discoverDecided(self, card, case="Random", info_RNGSync=(len(pools[i]), ), info_GUISync=(len(pools), i))
				else:
					info_RNGSync, game.options = [], []
					for pool in pools:
						game.options.append(npchoice(pool)(game, ID))
						info_RNGSync.append(len(pool))
					game.Discover.startDiscover(self, effectType=effectType, info_RNGSync=tuple(info_RNGSync), info_GUISync=[len(pools)])
	
	def discoverandGenerate_Types(self, effectType, comment, typePoolFunc):
		game, ID = self.Game, self.ID
		if self.type == "Minion" and ID != game.turn:
			return
		if game.mode == 0:
			if game.picks:
				info_RNGSync, info_GUISync, isRandom, card = game.picks.pop(0)
				if not card: return
				numOption, indexOption = info_GUISync
				if info_RNGSync: npchoice(range(info_RNGSync[0]), numOption, p=info_RNGSync[1], replace=False)
				card = card(game, ID)
				if game.GUI: game.GUI.discoverDecideAni(isRandom=isRandom, numOption=numOption, indexOption=indexOption, options=card)
				effectType.discoverDecided(self, card, case="Guided", info_RNGSync=info_RNGSync, info_GUISync=info_GUISync)
			else:
				cardTypes, p = discoverProb(typePoolFunc())
				if not cardTypes: game.picks_Backup.append((None, None, None, None))
				else:
					numOption = min(3, len(cardTypes))
					types = npchoice(cardTypes, numOption, p=p, replace=False)
					if numOption == 1 or ID != game.turn or "byOthers" in comment:
						i = datetime.now().microsecond % numOption
						card = types[i](game, ID)
						if game.GUI: game.GUI.discoverDecideAni(isRandom=True, numOption=numOption, indexOption=i, options=card)
						effectType.discoverDecided(self, card, case="Random", info_RNGSync=(len(cardTypes), p), info_GUISync=(numOption, i))
					else:
						game.options = [card(game, ID) for card in types]
						game.Discover.startDiscover(self, effectType=effectType, info_RNGSync=(len(cardTypes), p), info_GUISync=[numOption])
	
	#For selections like Totemic Slam. The options are totally predictable
	def chooseFixedOptions(self, effectType, comment, options):
		game, ID = self.Game, self.ID
		if self.type == "Minion" and ID != game.turn:
			return
		if game.mode == 0:
			if game.picks:
				info_RNGSync, info_GUISync, isRandom, optionType = game.picks.pop(0)  #, info_GUISync is (numOption, indexOption)
				numOption, indexOption = info_GUISync
				option = options[indexOption]
				if game.GUI: game.GUI.discoverDecideAni(isRandom=isRandom, numOption=numOption, indexOption=indexOption, options=option)
				effectType.discoverDecided(self, option, case="Guided", info_RNGSync=info_RNGSync, info_GUISync=info_GUISync)
			else:
				numOption = len(options)
				if ID != game.turn or "byOthers" in comment:
					i = datetime.now().microsecond % numOption
					card = options[i](game, ID)
					if game.GUI: game.GUI.discoverDecideAni(isRandom=True, numOption=numOption, indexOption=i, options=card)
					effectType.discoverDecided(self, card, case="Random", info_RNGSync=None, info_GUISync=(numOption, i))
				else:
					game.options = options
					game.Discover.startDiscover(self, effectType=effectType, info_RNGSync=None, info_GUISync=[numOption])
	
	#case can be "Discovered", "Guided" or "Random"
	def handleDiscoverGeneratedCard(self, option, case, info_RNGSync, info_GUISync, func=None):
		cardType, card = type(option), option
		if case != "Guided": self.Game.picks_Backup.append((info_RNGSync, info_GUISync, case == "Random", cardType))
		
		if func: func(cardType, card) #card can be an object or None
		else: self.addCardtoHand(card, self.ID, byDiscover=True)
		
	def discoverfromList(self, effectType, comment, conditional, ls):
		game, ID = self.Game, self.ID
		if not ls or (self.type == "Minion" and ID != game.turn): return
		if game.mode == 0:
			if game.picks:
				#选哪2/3张牌的序号记录在info_GUISync里面，indexPicked就是被选中的那张牌在ls中的序号
				info_RNGSync, info_GUISync, isRandom, indexPicked = game.picks.pop(0)
				if not indexPicked: #indices here are the indices of the 2/3 cards to show from ls
					return		#info_GUISync[1] is the indexOption
				indices_from_ls, numOption, indexOption = info_GUISync
				if info_RNGSync: #If no card to discover, then no RNG was involved
					numPools, p = info_RNGSync[0]
					npchoice(range(numPools), min(3, numPools), p=p, replace=False)
					for poolSize in info_RNGSync[1:]: nprandint(poolSize) #nprandint和npchoice效果完全相同
				if game.GUI: game.GUI.discoverDecideAni(isRandom=isRandom, numOption=numOption, indexOption=indexOption,
														options=[ls[i] for i in indices_from_ls])
				effectType.discoverDecided(self, indexPicked, case="Guided", info_RNGSync=info_RNGSync, info_GUISync=info_GUISync)
			else:
				cardTypes, p = discoverProb([type(card) for card in ls if conditional(card)])
				if not cardTypes:
					self.Game.picks_Backup.append((None, None, None, None))
				else:
					numOption = min(3, len(cardTypes))
					types = npchoice(cardTypes, numOption, p=p, replace=False)
					#2/3 different cards have their own indices make up indices_2Pickfrom
					#(len(cardTypes), p) + 2/3 different cards have their own poolSizes make up info_RNGSync
					info_RNGSync, indices_from_ls, options = [(len(cardTypes), p)], [], []
					for cardType in types:
						indices = [i for i, card in enumerate(ls) if isinstance(card, cardType)]
						index = npchoice(indices) #indices is of the same-typed cards in ls
						options.append(ls[index]) #a random card from the type is picked
						info_RNGSync.append(len(indices)) #len(indices) is the poolSize to pick a certain type from
						indices_from_ls.append(index)
					if numOption == 1 or ID != game.turn or "byOthers" in comment: #如果只有一个选项则跳过手动发现过程
						i = datetime.now().microsecond % numOption
						if game.GUI: game.GUI.discoverDecideAni(isRandom=True, numOption=numOption, indexOption=i, options=options)
						effectType.discoverDecided(self, indices_from_ls[i], case="Random", info_RNGSync=tuple(info_RNGSync),
												   info_GUISync=(tuple(indices_from_ls), numOption, i))
					else:
						game.options = options
						game.Discover.startDiscover(self, effectType=effectType, info_RNGSync=tuple(info_RNGSync),
													info_GUISync=[tuple(indices_from_ls), numOption])
						
	def handleDiscoveredCardfromList(self, option, case, ls, func, info_RNGSync, info_GUISync):
		if case == "Random":  #option here the index from ls
			card, index = ls[option], option
			self.Game.picks_Backup.append((info_RNGSync, info_GUISync, True, index))
		elif case == "Guided": #option here is index from ls
			card, index = ls[option], option
		else: #case == "Discovered" #option here is a real card selected
			card, index = option, ls.index(option)
			self.Game.picks_Backup.append((info_RNGSync, info_GUISync, False, index) )
		func(index, card)
		
	"""Common card generation handlers"""
	def addCardtoHand(self, card, ID, byDiscover=False, pos=-1, ani="fromCenter"):
		self.Game.Hand_Deck.addCardtoHand(card, ID, byDiscover=byDiscover, pos=pos,
										  ani=ani, creator=type(self))
		
	def shuffleintoDeck(self, obj, enemyCanSee=True):
		self.Game.Hand_Deck.shuffleintoDeck(obj, initiatorID=self.ID, enemyCanSee=enemyCanSee, creator=type(self))
		
	def summon(self, subject, position):
		self.Game.summon(subject, position, summoner=self)
		
	def transform(self, target, newMinion):
		self.Game.transform(target, newMinion, firstTime=True, creator=type(self))
		
	def equipWeapon(self, weapon):
		self.Game.equipWeapon(weapon, creator=self)
	"""Handle the battle options for minions and heroes."""
	#Will only be used to find a selectable attack target
	def findBattleTargets(self):
		side = 3 - self.ID
		if self.canAttack():
			targets = [minion for minion in self.Game.minionsonBoard(side) if self.canAttackTarget(minion)]
			indices = [minion.pos for minion in targets]
			wheres = ["Minion%d"%side] * len(indices)
			enemyHero = self.Game.heroes[side]
			if self.canAttackTarget(enemyHero):
				targets.append(enemyHero)
				indices.append(side)
				wheres.append("Hero%d"%side)
			return targets, indices, wheres
		else: return [], [], []

	#所有打出效果的目标寻找，包括战吼，法术等
	#To be invoked by AI and Shudderwock.
	def findTargets(self, comment="", choice=0): #comment="" is for random choosing, ignoring Stealth, etc. Non-empty comment will require target to be selectable
		game, targets, indices, wheres = self.Game, [], [], []
		targets = [minion for minion in game.minionsonBoard(1) if self.targetCorrect(minion, choice) and (not comment or self.canSelect(minion))]
		indices = [minion.pos for minion in targets]
		wheres = ["Minion1"] * len(indices)
		targets2 = [minion for minion in game.minionsonBoard(2) if self.targetCorrect(minion, choice) and (not comment or self.canSelect(minion))]
		targets += targets2
		indices += [minion.pos for minion in targets2]
		wheres += ["Minion2"] * len(targets2)
		for ID in range(1, 3):
			hero = game.heroes[ID]
			if self.targetCorrect(hero, choice) and (not comment or self.canSelect(hero)):
				targets.append(hero)
				indices.append(ID)
				wheres.append("Hero%d"%ID)
		if targets: return targets, indices, wheres
		else: return [None], [0], ['']

	#继承一张卡的所有附魔时一定是那张卡要消失的时候。一般用于一张牌的升级/腐蚀变形
	def inheritEnchantmentsfrom(self, card):
		for receiver in card.auraReceivers: receiver.effectClear()
		#Buff and mana effects, etc, will be preserved
		#Buff to cards in hand will always be permanent or temporary, not from Auras
		if self.type in ("Minion", "Weapon"):
			attBuff, healthBuff = card.attack_Enchant - card.attack_0, card.health_max - card.health_0
			self.buffDebuff(attBuff, healthBuff)
			#Temporary attack changes on minions are NOT included in attack_Enchant
			if self.type == "Minion": #Assume temporary attack changes applied on a minion won't carry over to the weapon
				for attGain, attRevertTime in card.tempAttChanges:
					self.buffDebuff(attGain, 0, attRevertTime)
			for trig in card.deathrattles:
				if not trig.inherent:
					trig.entity = self
					self.deathrattles.append(trig)
		#Keep the keywords and marks consistent
		basicEffects = {}
		if type(card).effects:
			for key in type(card).effects.split(","):
				if '_' in key:
					keyWord, s = key.strip().split('_')
					basicEffects[keyWord] = int(s)
				else: basicEffects[key.strip()] = 1
		for key in basicEffects.keys():  #Find keywords the new card doesn't have
			if key in card.effects: self.effects[key] += card.effects[key] - basicEffects[key]
		#Inhand triggers and mana modifications
		for trig in card.trigsBoard:
			if not trig.inherent:
				trig.entity = self
				self.trigsBoard.append(trig)
		for trig in card.trigsHand: #Some cards can get trigs that discard them.
			if not trig.inherent:
				trig.entity = self
				self.trigsHand.append(trig)
		self.manaMods = [manaMod.selfCopy(self) for manaMod in card.manaMods if not manaMod.source]
		
	#Minion has its own selfCopy() method.
	#For now, copying non-minion/weapon cards can only create copies that don't have any enchantments on it.
	#The mana of a card can be copied, though.
	def hardCopy(self, ID, creator=""):
		Copy = type(self)(self.Game, ID)
		for key, value in self.__dict__.items():
			#Copy the attributes of basic types, or simply types.
			if isinstance(value, (type, type(None), int, np.int64, float, str, bool)):
				Copy.__dict__[key] = value
			#随从实例上带有的函数一经__init__确定不会改变。所以不需要进行复制
			elif callable(value): #If the attribute is a function
				pass
			elif inspect.isclass(value): #如果复制目标是一个类的话
				Copy.__dict__[key] = value
			elif value == self.Game: #Only shallow copy the Game.
				Copy.__dict__[key] = self.Game
			#用于auras，effectfromAura和manaMods等
			elif isinstance(value, (list, dict, tuple)): #If the attribute is a list or dictionary, use the method defined at the start of py
				Copy.__dict__[key] = copyListDictTuple(value, Copy)
			else: #The attribute is a self-defined class. They will all have selfCopy methods
				#A minion can't refernece another minion. The attributes here must be like triggers/deathrattles
				Copy.__dict__[key] = value.selfCopy(Copy)
		Copy.ID, Copy.creator = ID, creator
		return Copy

	#给非随从牌用的，目前也没有复制场上武器的牌
	def selfCopy(self, ID, creator):
		Copy = self.hardCopy(ID)
		Copy.creator = creator
		#复制一张牌的费用修改情况,移除来自光环影响的费用效果
		for i in reversed(range(len(Copy.manaMods))):
			if Copy.manaMods[i].source: Copy.manaMods.pop(i)
		return Copy

	def assistCreateCopy(self, Copy):
		pass



class Dormant(Card):
	type = "Dormant"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.minionInside = None
		self.effects = {"Taunt": 0, "Stealth": 0,
						 "Divine Shield": 0, "Spell Damage": 0, "Nature Spell Damage": 0,
						 "Lifesteal": 0, "Poisonous": 0,
						 "Windfury": 0, "Mega Windfury": 0,
						 "Charge": 0, "Rush": 0,
						 "Echo": 0,
						
						 "Sweep": 0,
						 "Evasive": 0, "Enemy Evasive": 0,
						 "Can't Attack": 0, "Can't Attack Hero": 0, "Can't be Played": 0,
						 "Heal x2": 0,  # Crystalsmith Kangor
						 "Spell Heal&Dmg x2": 0, "Power Heal&Dmg x2": 0,  # Prophet Velen, Clockwork Automation
						
						 "Immune": 0, "Frozen": 0, "Temp Stealth": 0, "Borrowed": 0
						 }
		
	def appears(self, firstTime=True):
		self.onBoard = True
		self.inHand = self.inDeck = self.dead = False
		self.enterBoardTurn = self.Game.numTurn
		# 目前没有Dormant有光环
		if self.btn:
			self.btn.isPlayed, self.btn.card = True, self
			self.btn.placeIcons()
		for aura in self.auras.values(): aura.auraAppears()
		for trig in self.trigsBoard: trig.connect()
		
	# Dormant本身是没有死亡扳机的，所以这个deathrattlesStayArmed无论真假都无影响
	def disappears(self, deathrattlesStayArmed=False, disappearResponse=True):
		self.onBoard = self.inHand = self.inDeck = self.dead = False
		for aura in self.auras.values(): aura.auraDisappears()
		for trig in self.trigsBoard: trig.disconnect()

	def turnStarts(self, ID):
		pass

	def turnEnds(self, ID):
		pass

	def canAttack(self):
		return False

	def takesDamage(self, subject, damage, sendDmgSignal=True, damageType="None"):
		return 0

	def createCopy(self, game):
		if self in game.copiedObjs:
			return game.copiedObjs[self]
		else:
			Copy = type(self)(game, self.ID)
			game.copiedObjs[self] = Copy
			Copy.onBoard, Copy.inHand, Copy.inDeck, Copy.dead = self.onBoard, self.inHand, self.inDeck, self.dead
			Copy.seq, Copy.pos = self.seq, self.pos
			Copy.enterBoardTurn = self.enterBoardTurn
			Copy.trigsBoard = [trig.createCopy(game) for trig in self.trigsBoard]
			Copy.x, Copy.y, Copy.z = self.x, self.y, self.z
			self.assistCreateCopy(Copy)
			return Copy


class Minion(Card):
	type = "Minion"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		cardType = type(self)
		self.race = cardType.race
		# 卡牌的费用和对于费用修改的效果列表在此处定义
		self.tempAttChanges = []  # list of tempAttChange, expiration timepoint
		self.effectfromAura = {"Charge": 0, "Rush": 0, "Mega Windfury": 0,
								"Free Evolve": 0,}
		self.auraReceivers = []
		self.effects = {"Taunt": 0, "Divine Shield": 0, "Stealth": 0,
						 "Lifesteal": 0, "Spell Damage": 0, "Nature Spell Damage": 0, "Poisonous": 0,
						 "Windfury": 0, "Mega Windfury": 0, "Charge": 0, "Rush": 0,
						 "Echo": 0, "Reborn": 0, "Bane": 0, "Drain": 0,
						
						 "Cost Health Instead": 0,
						 "Sweep": 0,
						 "Evasive": 0, "Enemy Evasive": 0,
						 "Can't Attack": 0, "Can't Attack Hero": 0, "Can't be Played": 0,
						 "Heal x2": 0,  # Crystalsmith Kangor
						 "Power Heal&Dmg x2": 0,  # Prophet Velen, Clockwork Automation
						 "Spell Heal&Dmg x2": 0,
						 "Enemy Effect Evasive": 0, "Enemy Effect Damage Immune": 0,
						 "Can't Break": 0, "Can't Disappear": 0, "Can't Be Attacked": 0, "Disappear When Die": 0,
						 "Next Damage 0": 0, "Ignore Taunt": 0, "Can't Evolve": 0, "Free Evolve": 0,
						 "Can Attack 3 times": 0,
						
						 "Immune": 0, "Frozen": 0, "Temp Stealth": 0, "Borrowed": 0,
						 "Evolved": 0,
						 }
		for key in cardType.effects.split(","):
			if '_' in key:
				keyWord, s = key.strip().split('_')
				self.effects[keyWord] = int(s)
			else: self.effects[key.strip()] = 1
		self.silenced = False  # This mark is for minion state change, such as enrage.
		self.appearResponse, self.disappearResponse, self.silenceResponse, self.returnResponse = [], [], [], []
		# self.seq records the number of the minion's appearance. The first minion on board has a sequence of 0
		self.usageCount = self.attChances_base = self.attChances_extra = 0

		self.history = {"Spells Cast on This": [],
						"Magnetic Upgrades": {"AttackGain": 0, "HealthGain": 0,
											  "Keywords": {}, "Marks": {},
											  "Deathrattles": [], "Triggers": []
											  }
						}
		
	def reset(self, ID, isKnown=True): #如果一个随从被返回手牌或者死亡然后进入墓地，其上面的身材改变(buff/statReset)会被消除，但是保留其白字变化
		creator, possi = self.creator, type(self) if isKnown else self.possi
		att_0, health_0 = self.attack_0, self.health_0
		btn, x, y, z = self.btn, self.x, self.y, self.z
		self.__init__(self.Game, ID)
		self.attack_0 = self.attack = self.attack_Enchant = att_0
		self.health_0 = self.health = self.health_max = health_0
		self.creator = creator
		self.possi = possi
		self.btn, self.x, self.y, self.z = btn, x, y, z
		
	def applicable(self, target):
		return target != self

	"""Handle the trigsBoard/inHand/inDeck of minions based on its move"""
	def appears(self, firstTime=True):
		self.onBoard = True
		self.inHand = self.inDeck = self.dead = False
		self.enterBoardTurn = self.Game.numTurn
		self.mana = type(self).mana  # Restore the minion's mana to original value.
		self.decideAttChances_base()  # Decide base att chances, given Windfury and Mega Windfury
		if self.btn:
			self.btn.isPlayed, self.btn.card = True, self
			self.btn.placeIcons()
			self.btn.statChangeAni()
			self.btn.effectChangeAni()
		for aura in self.auras.values(): aura.auraAppears()
		for trig in self.trigsBoard + self.deathrattles: trig.connect()
		for func in self.appearResponse: func()
		# The buffAuras/hasAuras will react to this signal.
		self.Game.sendSignal("MinionAppears", self.ID, self, None, 0, comment=firstTime)

	def disappears(self, deathrattlesStayArmed=True, disappearResponse=True):  # The minion is about to leave board.
		self.onBoard = self.inHand = self.inDeck = False
		for aura in self.auras.values(): aura.auraDisappears()
		for trig in self.trigsBoard: trig.disconnect()
		# 随从因离场方式不同，对于亡语扳机的注册是否保留也有不同
		# 死亡时触发的区域移动扳机导致的返回手牌或者牌库--保留其他死亡扳机的注册
		# 存活状态下因为亡语触发效果而触发的区域移动扳机--保留其他死亡扳机
		# 存活状态下因为闷棍等效果导致的返回手牌--注销全部死亡扳机
		# 存活状态下因为控制权变更，会取消全部死亡扳机的注册，在随从移动到另一侧的时候重新注册死亡扳机
		# 总之，区域移动扳机的触发不会取消其他注册了的死亡扳机,这些死亡扳机会在它们触发之后移除。
		# 如果那些死亡扳机是因为其他效果而触发（非死亡），除非随从在扳机触发后已经离场（返回手牌或者牌库），否则可以保留
		if not deathrattlesStayArmed:
			for trig in self.deathrattles: trig.disconnect()
		if disappearResponse:
			for func in self.disappearResponse: func()
		# Let Stat_Receivers and hasreceivers remove themselves
		while self.auraReceivers: self.auraReceivers[0].effectClear()
		self.Game.sendSignal("MinionDisappears", self.ID, None, self, 0, "")

	"""Attack chances handle"""
	# The game will directly invoke the turnStarts/turnEnds methods.
	def turnStarts(self, ID):
		for i in reversed(range(len(self.tempAttChanges))):  # Remove the temp attack changes.
			# self.tempAttChanges[size-1-i]是一个tuple(tempAttackChange, timepoint)
			if self.tempAttChanges[i][1] == "StartofTurn 1" and self.Game.turn == 1:
				self.statChange(-self.tempAttChanges[i][0], 0)
				self.tempAttChanges.pop(i)
			if self.tempAttChanges[i][1] == "StartofTurn 2" and self.Game.turn == 2:
				self.statChange(-self.tempAttChanges[i][0], 0)
				self.tempAttChanges.pop(i)
		if ID == self.ID:
			if self.onBoard: self.losesEffect("Temp Stealth", 0) # Only minions on board lose Temp Stealth
			self.usageCount, self.attChances_extra = 0, 0
			self.decideAttChances_base()
		# 影之诗中的融合随从每个回合只能进行一次融合，需要在每个回合开始时重置
		if self.index.startswith("SV_") and hasattr(self, "fusion"):
			self.fusion = 1
	# Violet teacher is frozen in hand. When played right after being frozen or a turn after that, it can't defrost.
	# The minion is still frozen when played. And since it's not actionable, it won't defrost at the end of turn either.
	# 随从不能因为有多次攻击机会而自行解冻。只能等回合结束。
	def turnEnds(self, ID):
		# 直到回合结束的对攻击力改变效果不论是否是该随从的当前回合，都会消失
		for i in reversed(range(len(self.tempAttChanges))):
			if self.tempAttChanges[i][1] == "EndofTurn":
				self.statChange(-self.tempAttChanges[i][0], 0)
				self.tempAttChanges.pop(i)
		self.losesEffect("Immune", 0)
		if ID == self.ID:
			# The minion can only thaw itself at the end of its turn. Not during or outside its turn
			if self.onBoard and self.effects["Frozen"] > 0:  # The minion can't defrost in hand.
				if self.actionable() and self.attChances_base + self.attChances_extra > self.usageCount:
					self.losesEffect("Frozen", 0)
			self.usageCount, self.attChances_extra = 0, 0
		if self.btn: self.btn.effectChangeAni()
		
	# 判定随从是否处于刚在我方场上登场，以及暂时控制、冲锋、突袭等。
	def actionable(self):
		# 不考虑冻结、零攻和自身有不能攻击的debuff的情况。
		# 如果随从是刚到我方场上，则需要分析是否是暂时控制或者是有冲锋或者突袭。
		# 随从已经在我方场上存在一个回合。则肯定可以行动。
		return self.onBoard and self.ID == self.Game.turn and \
			   (self.enterBoardTurn != self.Game.numTurn or (self.effects["Borrowed"] > 0 or self.effects["Charge"] > 0 or self.effects["Rush"] > 0))

	def afterSwitchSide(self, activity):
		self.decideAttChances_base()
		# activity == "Permanent" or "Return"
		self.effects["Borrowed"] = 0 + activity == "Borrow"

	# Whether the minion can select the attack target or not.
	def canAttack(self):
		# THE CHARGE/RUSH MINIONS WILL GAIN ATTACKCHANCES WHEN THEY APPEAR
		return self.actionable() and self.attack > 0 and self.effects["Frozen"] < 1 \
			   and self.attChances_base + self.attChances_extra > self.usageCount \
			   and self.effects["Can't Attack"] < 1

	def canAttackTarget(self, target):
		return self.canAttack() and target.selectablebyBattle(self) and \
			   (target.type == "Minion" or (target.type == "Hero" and
											(self.enterBoardTurn != self.Game.numTurn or self.effects["Borrowed"] > 0 or self.effects["Charge"] > 0)
											and self.effects["Can't Attack Hero"] < 1)
				)

	"""Healing, damage, takeDamage, AOE, lifesteal and dealing damage response"""

	# Stealth Dreadscale actually stays in stealth.
	def takesDamage(self, subject, damage, sendDmgSignal=True, damageType="None", canTransfer=True):
		game = self.Game
		if canTransfer:
			dmgTaker = self.Game.scapegoat4(self) #只有没有伤害来源的伤害会直接调用takesDamage，其他的都是调用dealsDamage,dealsAOE
			if dmgTaker != self: dmgTaker.takesDamage(subject=None, damage=damage, sendDmgSignal=sendDmgSignal, damageType=damageType, canTransfer=False)
		if self.effects["Immune"] < 1:  # 随从首先结算免疫和圣盾对于伤害的作用，然后进行预检测判定
			if "Next Damage 0" in self.effects and self.effects["Next Damage 0"] > 0:
				if not subject.type == "Hero" or not damage == 0:
					damage = 0
					self.effects["Next Damage 0"] = 0
			if self.effects["Enemy Effect Damage Immune"] > 0 and damageType == "Ability":
				damage = 0
			if "Deal Damage 0" in subject.effects and subject.effects["Deal Damage 0"] > 0:
				damage = 0
			if "Bane" in subject.effects and subject.effects["Bane"] > 0 and damageType == "Battle" and self.onBoard:
				self.dead = True
			if damage > 0:
				if self.effects["Divine Shield"] > 0:
					damage = 0
					self.losesEffect("Divine Shield")
				else:
					# 伤害量预检测。如果随从有圣盾则伤害预检测实际上是没有意义的。
					damageHolder = [damage]  # 这个列表用于盛装伤害数值，会经由伤害扳机判定
					game.sendSignal("FinalDmgonMinion?", 0, subject, self, damageHolder, "")
					damage = damageHolder[0]
					self.health -= damage
					deadbyPoisonous = ((subject.type == "Spell" and game.effects[subject.ID]["Spells Poisonous"] > 0) or
										subject.effects["Poisonous"] > 0) and self.onBoard
					if self.btn: self.btn.statChangeAni(num2=-damage, action="poisonousDamage" if deadbyPoisonous else "damage")
					# 经过检测，被伏击者返回手牌中的紫罗兰老师不会因为毒药贩子加精灵弓箭手而直接丢弃。会减1血，并在打出时复原。
					if deadbyPoisonous:
						GUI = self.Game.GUI
						if GUI and "Poisonous" in subject.btn.icons:
							icon = subject.btn.icons["Poisonous"]
							GUI.seqHolder[-1].append(GUI.PARALLEL(GUI.FUNC(icon.trigAni), GUI.WAIT(0.2)))
						self.dead = True
					# 在同时涉及多个角色的伤害处理中，受到的伤害暂不发送信号而之后统一进行扳机触发。
					if sendDmgSignal:
						game.sendSignal("MinionTakesDmg", game.turn, subject, self, damage, "")
						game.sendSignal("MinionTookDmg", game.turn, subject, self, damage, "")
					if subject.type == "Power":
						game.Counters.damageDealtbyHeroPower[subject.ID] += damage
					# 随从的激怒，根据血量和攻击的状态改变都在这里触发。
					self.Game.sendSignal("MinionStatCheck", self.ID, None, self, 0, "")
			else:
				game.sendSignal("MinionTakes0Dmg", game.turn, subject, self, 0, "")
				game.sendSignal("MinionTook0Dmg", game.turn, subject, self, 0, "")
		else:
			damage = 0
		return damage

	def deathResolution(self, attackwhenDies, armedTrigs_WhenDies, armedTrigs_AfterDied):
		self.Game.sendSignal("MinionDies", self.Game.turn, None, self, attackwhenDies, '', 0,
							 armedTrigs_WhenDies)
		# 随从的亡语也需要扳机化，因为亡语和“每当你的一个xx随从死亡”的扳机的触发顺序也由其登场顺序决定
		# 如果一个随从有多个亡语（后来获得的，那么土狼会在两个亡语结算之间触发。所以说这些亡语是严格意义上的扳机）
		# 随从入场时注册亡语扳机，除非注明了是要结算死亡的情况下，disappears()的时候不会直接取消这些扳机，而是等到deathResolution的时候触发这些扳机
		# 如果是提前离场，如改变控制权或者是返回手牌，则需要取消这些扳机
		# 扳机应该注册为场上扳机，这个扳机应该写一个特殊的类，从而使其可以两次触发，同时这个类必须可存储一个attribute,复制效果可以复制食肉魔块等战吼提供的信息
		# 区域移动类扳机一般不能触发两次
		# 触发扳机如果随从已经不在场上，则说明它区域移动然后进入了牌库或者手牌。同类的区域移动扳机不会触发。
		# 区域移动的死亡扳机大多是伪区域移动，实际上是将原实体移除之后将一个复制置入相应区域。可以通过魔网操纵者来验证。只有莫里甘博士和阿努巴拉克的亡语是真的区域移动
		# 鼬鼠挖掘工的洗入对方牌库扳机十分特别，在此不予考虑，直接视为将自己移除，然后给对方牌库里洗入一个复制
		# The minion resets its own status. But it will record its current location.
		# If returned to hand/deck already due to deathrattle, the inHand/inDeck will be kept
		# 假设随从只有在场上结算亡语完毕之后才会进行初始化，而如果扳机已经提前将随从返回手牌或者牌库，则这些随从不会
		# 移除随从注册了的亡语扳机
		for trig in self.deathrattles: trig.disconnect()
		self.Game.sendSignal("MinionDied", self.Game.turn, None, self, 0, "", 0, armedTrigs_AfterDied)

	# MinionDeathResolutionFinished

	def magnetCombine(self, target):
		# 暂时假设磁力随从如果死亡则不触发磁力。
		# 先将随从从场上或者手牌中移除。
		if self.onBoard:
			# 磁力随从因为磁力触发离场时会注销其已经注册的死亡扳机，最终会将这些死亡扳机赋予磁力目标
			self.disappears(deathrattlesStayArmed=False)
			self.Game.removeMinionorWeapon(self)
		else:  # The Magnetic minion is inHand
			self.Game.Hand_Deck.extractfromHand(self)

		# 在打出磁力随从时，需要得知其原有的关键字、身材和扳机等，需要进行复制，然后录入随从的磁力升级历史
		Copy = self.selfCopy(self.ID)  # Find the original keywords the minion has
		attack_orig, health_orig = Copy.attack_Enchant, Copy.health
		keyWords_orig, marks_orig = {}, {}
		for key, value in Copy.effects.items():
			if value > 0:
				keyWords_orig[key] = value
		# 暂时假设磁力随从不会保留状态，如临时潜行和冰冻
		for key, value in Copy.effects.items():
			if value > 0:
				marks_orig[key] = value
		# 将随从携带的扳机也记录,磁力随从是没有手牌扳机和场上扳机的
		triggers_orig, deathrattles_orig = [], []
		for trig in Copy.trigsBoard:
			if trig.inherent:  # 外来扳机不会被记录和赋予，如腐蚀术
				trig.append(type(trig))
		for trig in Copy.deathrattles:
			deathrattles_orig.append(type(trig))
		# 磁力随从没有triggers[]的方法，如激怒等
		# 将关键字赋予随从
		for key, value in keyWords_orig.items():
			for i in range(value):
				target.getsEffect(key)
				if key in target.history["Magnetic Upgrades"]["Keywords"].keys():
					target.history["Magnetic Upgrades"]["Keywords"][key] += value
				else:  # 如果这个关键字是之前没有的，则在dict里面添加这个key
					target.history["Magnetic Upgrades"]["Keywords"][key] = value
		# 将类关键字赋予随从
		for key, value in marks_orig.items():
			target.effects[key] += value
			if key in target.history["Magnetic Upgrades"]["Marks"].keys():
				target.history["Magnetic Upgrades"]["Marks"][key] += value
			else:
				target.history["Magnetic Upgrades"]["Marks"][key] = value
		# 将扳机赋予随从，同时记录在目标随从的"Magnetic Upgrades"中
		for Trig_Class in deathrattles_orig:
			trig = Trig_Class(target)
			target.deathrattles.append(trig)
			trig.connect()
			target.history["Magnetic Upgrades"]["Deathrattles"].append(Trig_Class)
		# 将亡语赋予随从，同时记录在"Magnetic Upgrades"里面
		for Trig_Class in triggers_orig:
			trig = Trig_Class(target)
			target.trigsBoard.append(trig)
			trig.connect()
			target.history["Magnetic Upgrades"]["Triggers"].append(Trig_Class)
		# 最后进行身材的改变，并在这里调用目标随从的StatChanges方法
		target.buffDebuff(attack_orig, health_orig)
		target.history["Magnetic Upgrades"]["AttackGain"] += attack_orig
		target.history["Magnetic Upgrades"]["HealthGain"] += health_orig
		self.Game.minionPlayed = None

	# Specifically for battlecry resolution. Doesn't care if the target is in Stealth.
	def targetCorrect(self, target, choice=0):
		return (target.type == "Minion" or target.type == "Hero") and target.onBoard and target != self

	# Minions that initiates discover or transforms self will be different.
	# For minion that transform before arriving on board, there's no need in setting its onBoard to be True.
	# By the time this triggers, death resolution caused by Illidan/Juggler has been finished.
	# If Brann Bronzebeard/ Mayor Noggenfogger has been killed at this point, they won't further affect the battlecry.
	# posinHand在played中主要用于记录一张牌是否是从手牌中最左边或者最右边打出（恶魔猎手职业关键字）
	def played(self, target=None, choice=0, mana=0, posinHand=-2, comment=""):
		# 即使该随从在手牌中的生命值为0或以下，打出时仍会重置为无伤状态。
		self.statReset(self.attack_Enchant, self.health_max)
		# 此时，随从可以开始建立光环，建立侦听，同时接受其他光环。例如： 打出暴风城勇士之后，光环在Illidan的召唤之前给随从加buff，同时之后打出的随从也是先接受光环再触发Illidan。
		self.appears(firstTime=True)
		GUI = self.Game.GUI
		# 使用阶段
		# 使用时步骤,触发“每当你使用一张xx牌”的扳机,如伊利丹，任务达人，无羁元素和魔能机甲等
		# 触发信号依次得到主玩家的场上，手牌和牌库的侦听器的响应，之后是副玩家的侦听器响应。
		# 伊利丹可以在此时插入召唤和飞刀的结算，之后在战吼结算开始前进行死亡的判定，同时subject和target的位置情况会影响战吼结果。
		self.Game.sendSignal("MinionPlayed", self.ID, self, target, mana, "", choice)
		# 召唤时步骤，触发“每当你召唤一个xx随从”的扳机.如鱼人招潮者等。
		self.Game.sendSignal("MinionSummoned", self.ID, self, target, mana, "")
		# 过载结算
		if self.overload > 0:
			self.Game.Manas.overloadMana(self.overload, self.ID)

		magneticTarget = None
		if self.magnetic > 0:
			if self.onBoard:
				neighbors, dist = self.Game.neighbors2(self)
				if dist == 1 and "Mech" in neighbors[1].race:
					magneticTarget = neighbors[1]
				elif dist == 2 and "Mech" in neighbors[0].race:
					magneticTarget = neighbors[0]
		# 使用阶段结束，开始死亡结算。视随从的存活情况决定战吼的触发情况，此时暂不处理胜负问题。
		self.Game.gathertheDead()  # At this point, the minion might be removed/controlled by Illidan/Juggler combo.
		# 结算阶段
		if self.magnetic > 0:
			# 磁力相当于伪指向性战吼，一旦指定目标之后，不会被其他扳机改变
			# 磁力随从需要目标和自己都属于同一方,且磁力目标在场时才能触发。
			if magneticTarget and magneticTarget.onBoard and self.ID == magneticTarget.ID:
				# 磁力结算会让随从离场，不会触发后续的随从召唤后，打出后的扳机
				self.magnetCombine(magneticTarget)
		# 磁力随从没有战吼等入场特效，因而磁力结算不会引发死亡，不必进行死亡结算
		else:  # 无磁力的随从
			# 市长会在战吼触发前检测目标，指向性战吼会被随机取向。一旦这个随机过程完成，之后的第二次战吼会重复对此目标施放。
			# 如果场上有随从可供战吼选择，但是因为免疫和潜行导致打出随从时没有目标，则不会触发随机选择，因为本来就没有目标。
			# 在战吼开始检测之前，如果铜须已经死亡，则其并不会让战吼触发两次。也就是扳机的机制。
			# 同理，如果此时市长已经死亡，则其让选择随机化的扳机也已经离场，所以不会触发随机目标。
			if target and not isinstance(target, list):
				targetHolder = [target]
				self.Game.sendSignal("BattlecryTargetDecision", self.ID, self, targetHolder, 0, "", choice)
				if target != targetHolder[0] and GUI:
					target = targetHolder[0]
					GUI.target = target
					GUI.wait(400)
				else:
					target = targetHolder[0]
			# 市长不会让发现和抉择选项的选择随机化。
			# 不管target是否还在场上，此时只要市长还在，就要重新在场上寻找合法目标。如果找不到，就不能触发战吼的指向性部分，以及其产生的后续操作。
			# 随机条件下，如果所有合法目标均已经消失，则return None. 由随从的战吼决定是否继续生效。

			# 在随从战吼/连击开始触发前，检测是否有战吼/连击翻倍的情况。如果有且战吼可以进行，则强行执行战吼至两次循环结束。无论那个随从是死亡，在手牌中还是牌库
			num, status = 1, self.Game.effects[self.ID]
			if "~Battlecry" in self.index and status["Battlecry x2"] + status["Shark Battlecry x2"] > 0:
				num = 2
			if "~Combo" in self.index and status["Shark Battlecry x2"] > 0:
				num = 2
			# 不同的随从会根据目标和自己的位置和状态来决定effectwhenPlayed()产生体积效果。
			# 可以变形的随从，如无面操纵者，会有自己的played（） 方法。 大王同理。
			# 战吼随从自己不会进入牌库，因为目前没有亡语等效果可以把随从返回牌库。
			# 发现随从如果在战吼触发前被对方控制，则不会引起发现，因为炉石没有对方回合外进行操作的可能。
			# 结算战吼，连击，抉择
			for i in range(num):
				if GUI and "~Battlecry" in self.index: GUI.battlecryAni(self)
				target = self.whenEffective(target, "", choice, posinHand)
			# 结算阶段结束，处理死亡情况，不处理胜负问题。
			self.Game.gathertheDead()
		return target

	def countHealDouble(self):  # 随从和武器的治疗效果
		return sum(minion.effects["Heal x2"] > 0 for minion in self.Game.minions[self.ID])

	"""buffAura effect, Buff/Debuff, stat reset, copy"""
	# Not all params can be False.
	def statReset(self, newAttack=False, newHealth=False, attRevertTime=""):
		if not self.inDeck and not self.dead:
			stat_Receivers = [receiver for receiver in self.auraReceivers if isinstance(receiver, Aura_Receiver)]
			# 将随从上的全部buffAura清除，因为部分光环的适用条件可能会因为随从被沉默而变化，如战歌指挥官
			for receiver in stat_Receivers:
				receiver.effectClear()
			if newAttack != False:  # The minion's health is reset.
				self.tempAttChanges = []  # Clear the temp attack changes on the minion.
				if attRevertTime:
					attGain = newAttack - self.attack
					self.tempAttChanges.append((attGain, attRevertTime))
				self.attack = self.attack_Enchant = newAttack
			if newHealth: self.health = self.health_max = newHealth
			# 清除全部buffAura并重置随从的生命值之后，让原来的buffAura_Dealer自行决定是否重新对该随从施加光环。
			for receiver in stat_Receivers:
				receiver.source.applies(self)
			if self.btn: self.btn.statChangeAni(action="set")
			self.Game.sendSignal("MinionStatCheck", self.ID, None, self, 0, "")

	# 在原来的Game中创造一个Copy
	def selfCopy(self, ID, creator, attack=False, health=False, mana=False):
		Copy = self.hardCopy(ID)
		# 随从的光环和亡语复制完全由各自的selfCopy函数负责。
		for receiver in Copy.auraReceivers: receiver.effectClear()
		Copy.onBoard = Copy.inHand = Copy.inDeck = False
		size = len(Copy.manaMods)  # 去掉牌上的因光环产生的费用改变
		for i in reversed(range(size)):
			if Copy.manaMods[i].source: Copy.manaMods.pop(i)
		# 在一个游戏中复制出新实体的时候需要把这些值重置
		Copy.creator = creator
		Copy.dead = False
		Copy.effectViable = Copy.evanescent = False
		Copy.seq, Copy.pos = -1, -2
		Copy.usageCount, Copy.attChances_base, Copy.attChances_extra = 0, 0, 0
		Copy.decideAttChances_base()
		# 如果要生成一个x/x/x的复制
		if attack or health: Copy.statReset(attack, health)
		if mana:
			for manaMod in reversed(Copy.manaMods): manaMod.getsRemoved()
			Copy.manaMods = []
			ManaMod(Copy, changeby=0, changeto=mana).applies()
		return Copy

	# 破法者因为阿努巴尔潜伏者的亡语被返回手牌，之后被沉默，但是仍然可以触发其战吼
	def loseAbility(self):
		self.silenced = True
		for aura in self.auras.values(): aura.auraDisappears() #Clear the minion's auras
		self.auras = {}
		if self.btn: self.btn.effectChangeAni("Aura")
		# 清除所有场上扳机,亡语扳机，手牌扳机和牌库扳机。然后将这些扳机全部清除
		self.losesTrig(None, all=True)
		# 清除随从因为关键字光环获得的关键字：冲锋，突袭，超级风怒。这些关键字是否之后恢复由光环施加者决定。
		# 暂时不清除随从身上的buffAura增益，统一留到最后的statReset()中处理。
		receivers2Remove, effect_Receivers2Restore = [], []
		for receiver in self.auraReceivers:
			if receiver.source in self.auras.values(): receivers2Remove.append(receiver)
			elif not isinstance(receiver, Aura_Receiver): effect_Receivers2Restore.append(receiver)

		for receiver in receivers2Remove + effect_Receivers2Restore: receiver.effectClear()
		# 清除随从身上的所有原有关键字。
		for key, value in self.effects.items():
			if value > 0:
				self.effects[key] = 1
				self.losesEffect(key, amount=-1)
			self.effects[key] = 0
		# 清除随从身上的所有原有状态。
		for key, value in self.effects.items():
			# If Borrowed when silenced, return it to the other side.
			# The minion only remember one Borrowed state, even if repetitively moved between two sides.
			if key == "Borrowed" and value > 0 and self.onBoard:
				self.Game.minionSwitchSide(self, activity="Return")
			self.effects[key] = 0
		# 清除随从身上的历史记录，主要为对该随从施放的法术和机械随从的磁力叠加历史。
		for key in self.history.keys(): self.history[key] = []
		# 随从被沉默不发出沉默信号，所有接受的keywordAura就地处理。
		for receiver in effect_Receivers2Restore: receiver.source.applies(self)
		self.decideAttChances_base()
		
	def getsSilenced(self):
		self.loseAbility()
		# 沉默后的血量计算是求当前血量上限与实际血量的差，沉默后在基础血量上扣除该差值。（血量不能小于1）
		damageTaken = self.health_max - self.health
		# 在此处理随从身上存在的buffAura的效果。先是将其全部取消，然后看之前的光环是否还会继续对其产生作用。
		self.statReset(self.attack_0, self.health_0)
		self.health -= damageTaken
		self.health = max(1, self.health)
		if self.btn: self.btn.effectChangeAni()
		
	def createCopy(self, game):
		if self in game.copiedObjs:
			return game.copiedObjs[self]
		else:
			Copy = type(self)(game, self.ID)
			game.copiedObjs[self] = Copy
			Copy.mana = self.mana
			Copy.manaMods = [mod.selfCopy(Copy) for mod in self.manaMods]
			Copy.attack, Copy.attack_0, Copy.attack_Enchant = self.attack, self.attack_0, self.attack_Enchant
			Copy.health_0, Copy.health, Copy.health_max = self.health_0, self.health, self.health_max
			Copy.tempAttChanges = copy.deepcopy(self.tempAttChanges)
			Copy.effectfromAura = copy.deepcopy(self.effectfromAura)
			Copy.auraReceivers = [receiver.selfCopy(Copy) for receiver in self.auraReceivers]

			Copy.appearResponse, Copy.disappearResponse, Copy.silenceResponse, Copy.returnResponse = self.appearResponse, self.disappearResponse, self.silenceResponse, self.returnResponse
			Copy.effects = copy.deepcopy(self.effects)
			Copy.effects = copy.deepcopy(self.effects)
			Copy.effects = copy.deepcopy(self.effects)
			Copy.onBoard, Copy.inHand, Copy.inDeck, Copy.dead = self.onBoard, self.inHand, self.inDeck, self.dead
			if hasattr(self, "progress"): Copy.progress = self.progress
			Copy.effectViable, Copy.evanescent, Copy.silenced = self.effectViable, self.evanescent, self.silenced
			Copy.enterHandTurn, Copy.enterBoardTurn = self.enterHandTurn, self.enterBoardTurn
			Copy.seq, Copy.pos = self.seq, self.pos
			Copy.usageCount, Copy.attChances_base, Copy.attChances_extra = self.usageCount, self.attChances_base, self.attChances_extra
			Copy.options = [option.selfCopy(Copy) for option in self.options]
			for key, value in self.auras.items():
				Copy.auras[key] = value.createCopy(game)
			Copy.deathrattles = [trig.createCopy(game) for trig in self.deathrattles]
			Copy.trigsBoard = [trig.createCopy(game) for trig in self.trigsBoard]
			Copy.trigsHand = [trig.createCopy(game) for trig in self.trigsHand]
			Copy.trigsDeck = [trig.createCopy(game) for trig in self.trigsDeck]
			Copy.history = copy.deepcopy(self.history)
			Copy.tracked, Copy.creator, Copy.possi = self.tracked, self.creator, self.possi
			Copy.x, Copy.y, Copy.z = self.x, self.y, self.z
			self.assistCreateCopy(Copy)
			return Copy


class Spell(Card):
	type = "Spell"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.effects = {"Poisonous": 0, "Lifesteal": 0,
						 "Cost Health Instead": 0, "Can't be Played": 0,
						 }
		for key in type(self).effects.split(","):
			self.effects[key.strip()] = 1
	
	def reset(self, ID, isKnown=True):
		creator, possi = self.creator, type(self) if isKnown else self.possi
		btn, x, y, z = self.btn, self.x, self.y, self.z
		self.__init__(self.Game, ID)
		self.creator, self.possi = creator, possi
		self.btn, self.x, self.y, self.z = btn, x, y, z
	
	"""Handle the card being selected and check the validity of selection and target."""
	def available(self):
		return not self.needTarget() or self.selectableCharacterExists()

	"""Handle the spell being played by player and cast by other cards."""
	#用于由其他卡牌释放法术。这个法术会受到风潮和星界密使的状态影响，同时在结算完成后移除两者的状态。
	#这个由其他卡牌释放的法术不受泽蒂摩的光环影响。
	#目标随机，也不触发目标扳机。
	def cast(self, target=None, comment="", preferedTarget=None):
		curGame = self.Game
		GUI = curGame.GUI
		#由其他卡牌释放的法术结算相对玩家打出要简单，只需要结算过载，双生法术， 重复释放和使用后的扳机步骤即可。
		#因为这个法术是由其他序列产生的，所有结束时不会进行死亡处理。
		repeatTimes = 2 if curGame.effects[self.ID]["Spells x2"] > 0 else 1
		#多次选择的法术，如分岔路口等会有自己专有的cast方法。
		if curGame.mode == 0:
			if curGame.picks:
				i, where, choice = curGame.picks.pop(0)
				target = curGame.find(i, where) if where else None
			else:
				if not self.need2Choose(): choice = 0
				else: choice = -1 if curGame.effects[self.ID]["Choose Both"] else nprandint(len(self.options))
				if target is None: #沼泽女王哈加莎的恐魔是目前唯一的指定发动的
					if self.needTarget(choice):
						targets = self.findTargets("", choice)[0]
						if targets:
							if "enemy1st" in comment:
								enemies = [char for char in targets if self.canSelect(char) and self.targetCorrect(char, choice)]
								target = npchoice(enemies) if enemies else npchoice(targets)
							elif "targetPrefered" in comment and preferedTarget:
								target = preferedTarget if self.canSelect(preferedTarget) and self.targetCorrect(preferedTarget, choice) else npchoice(targets)
							else: target = npchoice(targets)
						else: target = None
					else: target = None
				if target: i, where = target.pos, target.type+str(target.ID)
				else: i, where = 0, ''
				curGame.picks_Backup.append((i, where, choice))
		if GUI:
			GUI.showOffBoardTrig(self)
			GUI.subject, GUI.target = self, target
		#在法术要施放两次的情况下，第二次的目标仍然是第一次时随机决定的
		for i in range(repeatTimes):
			if self.overload > 0: curGame.Manas.overloadMana(self.overload, self.ID)
			if self.twinSpell > 0: #如果不是从手牌中打出，则不会把双生法术牌置入原来的位置
				curGame.Hand_Deck.addCardtoHand(self.twinSpellCopy, self.ID, byType=True,
												creator=type(self), possi=(self.twinSpellCopy,))
			#指向性法术如果没有目标也可以释放，只是可能没有效果而已
			target = self.whenEffective(target, "byOthers", choice, posinHand=-2)
		if GUI: GUI.eraseOffBoardTrig(self.ID)
		#使用后步骤，但是此时的扳机只会触发星界密使和风潮的状态移除。这个信号不是“使用一张xx牌之后”的扳机。
		curGame.sendSignal("SpellBeenCast", self.ID, self, target, 0, "byOthers", choice=0)

	#泽蒂摩加风潮，当对泽蒂摩使用Mutate之后，Mutate会连续两次都进化3个随从
	#泽蒂摩是在法术开始结算之前打上标记,而非在连续两次之间进行判定。
	#comment = "InvokedbyAI", "Branching-i", ""
	def played(self, target=None, choice=0, mana=0, posinHand=-2, comment=""):
		game, ID, GUI = self.Game, self.ID, self.Game.GUI
		#使用阶段
		#判定该法术是否会因为风潮的光环存在而释放两次。发现的子游戏中不会两次触发，直接跳过
		repeatTimes = 2 if game.effects[ID]["Spells x2"] > 0 else 1
		if GUI: GUI.showOffBoardTrig(self)
		#使用时步骤，触发伊利丹和紫罗兰老师等“每当你使用一张xx牌”的扳机
		game.sendSignal("SpellPlayed", ID, self, target if not isinstance(target, list) else None, mana, "", choice)
		game.sendSignal("Spellboost", ID, self, None, mana, "", choice)
		#获得过载和双生法术牌。
		if self.overload > 0: game.Manas.overloadMana(self.overload, ID)
		if self.twinSpell > 0:
			game.Hand_Deck.addCardtoHand(self.twinSpellCopy, ID, byType=True, pos=posinHand,
													creator=type(self), possi=(self.twinSpellCopy,))
		#使用阶段结束，进行死亡结算。不处理胜负裁定。
		game.gathertheDead() #At this point, the minion might be removed/controlled by Illidan/Juggler combo.
		#进行目标的随机选择和扰咒术的目标改向判定。
		if target:
			holder = [target]
			game.sendSignal("SpellTargetDecision", ID, self, holder, 0, choice)
			if target != holder[0] and GUI:
				target = holder[0]
				GUI.target = target
				GUI.wait(400) #If the target is changed, show 0.4 more seconds
			else: target = holder[0]

		if target and target.ID == ID:
			game.Counters.spellsonFriendliesThisGame[ID].append(self.index)
		#Zentimo's effect actually an aura. As long as it's onBoard the moment the spell starts being resolved,
		#the effect will last even if Zentimo leaves board early.
		sweep = game.effects[ID]["Spells Sweep"]
		#没有法术目标，且法术本身是点了需要目标的选项的抉择法术或者需要目标的普通法术。
		for i in range(repeatTimes):
			if i == 1: #第二次施放时照常获得过载和双生法术牌。
				if self.overload > 0: game.Manas.overloadMana(self.overload, ID)
				if self.twinSpell > 0:
					game.Hand_Deck.addCardtoHand(self.twinSpellCopy, ID, byType=True, pos=posinHand,
													creator=type(self), possi=(self.twinSpellCopy,))
			#When the target is an onBoard minion, Zentimo is still onBoard and has adjacent minions next to it.
			if target and target.type == "Minion" and target.onBoard and sweep > 0 and game.neighbors2(target)[0]:
				neighbors = game.neighbors2(target)[0]
				#只对中间的目标随从返回法术释放之后的新目标。
				#用于变形等会让随从提前离场的法术。需要知道后面的再次生效目标。
				target.history["Spells Cast on This"].append(self.index)
				target = self.whenEffective(target, comment, choice, posinHand)
				for minion in neighbors: #对相邻的随从也释放该法术。
					minion.history["Spells Cast on This"].append(self.index)
					self.whenEffective(minion, comment, choice, posinHand)
			else: #The target isn't minion or Zentimo can't apply to the situation. Be the target hero, minion onBoard or inDeck or None.
				#如果目标不为空而且是在场上的随从，则这个随从的历史记录中会添加此法术的index。
				if target and (target.type == "Minion" or target.type == "Amulet") and target.onBoard:
					target.history["Spells Cast on This"].append(self.index)
				target = self.whenEffective(target, comment, choice, posinHand)

		#仅触发风潮，星界密使等的光环移除扳机。“使用一张xx牌之后”的扳机不在这里触发，而是在Game的playSpell函数中结算。
		game.sendSignal("SpellBeenCast", game.turn, self, target, 0, "", choice)
		#使用阶段结束，进行死亡结算，暂不处理胜负裁定。
		game.gathertheDead() #At this point, the minion might be removed/controlled by Illidan/Juggler combo.
	#完成阶段：
		#如果法术具有回响，则将回响牌置入手牌中。因为没有牌可以让法术获得回响，所以可以直接在法术played()方法中处理echo
		#if "~Echo" in self.index:
		#	echoCard = type(minion)(self, game.turn)
		#	trig = Trig_Echo(echoCard)
		#	echoCard.trigsHand.append(trig)
		#	game.Hand_Deck.addCardtoHand(echoCard, ID)
		if GUI: GUI.eraseOffBoardTrig(ID)

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		return target

	def afterDrawingCard(self):
		pass
		
	"""Handle the spell dealing damage and restoring health."""
	def countDamageDouble(self):
		return sum(minion.effects["Spell Heal&Dmg x2"] > 0 for minion in self.Game.minions[self.ID])

	def countHealDouble(self):
		return sum(minion.effects["Heal x2"] > 0 or minion.effects["Spell Heal&Dmg x2"] > 0 for minion in self.Game.minions[self.ID])

	def createCopy(self, game):
		if self in game.copiedObjs:
			return game.copiedObjs[self]
		else:
			Copy = type(self)(game, self.ID)
			game.copiedObjs[self] = Copy
			Copy.mana = self.mana
			Copy.manaMods = [mod.selfCopy(Copy) for mod in self.manaMods]
			Copy.inHand, Copy.inDeck = self.inHand, self.inDeck
			Copy.enterHandTurn = self.enterHandTurn
			Copy.trigsBoard = [trig.createCopy(game) for trig in self.trigsBoard]
			Copy.trigsHand = [trig.createCopy(game) for trig in self.trigsHand]
			Copy.trigsDeck = [trig.createCopy(game) for trig in self.trigsDeck]
			Copy.options = [option.selfCopy(Copy) for option in self.options]
			Copy.effects = copy.deepcopy(self.effects)
			Copy.effects = copy.deepcopy(self.effects)
			Copy.effectViable, Copy.evanescent = self.effectViable, self.evanescent
			Copy.tracked, Copy.creator, Copy.possi = self.tracked, self.creator, self.possi
			Copy.x, Copy.y, Copy.z = self.x, self.y, self.z
			self.assistCreateCopy(Copy)
			return Copy


class Secret(Spell):
	def available(self):
		return self.Game.Secrets.areaNotFull(self.ID) and not self.Game.Secrets.sameSecretExists(self, self.ID)

	def selectionLegit(self, target, choice=0):
		return target is None

	def cast(self, target=None, comment="", preferedTarget=None):
		if self.Game.GUI:
			self.Game.GUI.showOffBoardTrig(self, animationType='', isSecret=True)
		self.whenEffective(None, "byOthers", choice=0, posinHand=-2)
		self.Game.sendSignal("SpellBeenCast", self.ID, self, None, 0, "byOthers")

	def played(self, target=None, choice=0, mana=0, posinHand=-2, comment=""):
		if self.Game.GUI:
			self.Game.GUI.showOffBoardTrig(self, animationType='', isSecret=True)
		self.Game.sendSignal("SpellPlayed", self.ID, self, None, mana, "", choice)
		self.Game.sendSignal("Spellboost", self.ID, self, None, mana, "", choice)
		self.Game.gathertheDead()  # At this point, the minion might be removed/controlled by Illidan/Juggler combo.
		self.whenEffective(None, '', choice, posinHand)
		# There is no need for another round of death resolution.
		self.Game.sendSignal("SpellBeenCast", self.ID, self, None, 0, "")

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		secretHD = self.Game.Secrets
		if secretHD.areaNotFull(self.ID) and not secretHD.sameSecretExists(self, self.ID):
			secretHD.secrets[self.ID].append(self)
			for trig in self.trigsBoard: trig.connect()
			if self.Game.GUI: self.Game.GUI.heroZones[self.ID].placeSecrets()
			#secretHD.initSecretHint(self) #Let the game know what possible secrets each player has
		return None
	

class Quest(Spell):
	#Upper limit of secrets and quests is 5. There can only be one main quest, but multiple different sidequests
	def available(self):
		secretZone = self.Game.Secrets
		if secretZone.areaNotFull(self.ID):
			if self.description.startswith("Sidequest"):
				return all(quest.name != self.name for quest in secretZone.sideQuests[self.ID])
			else: return secretZone.mainQuests[self.ID] != []
		return False

	def selectionLegit(self, target, choice=0):
		return target is None

	def cast(self, target=None, comment="", preferedTarget=None):
		if self.Game.GUI:
			self.Game.GUI.showOffBoardTrig(self)
			self.Game.GUI.wait(500)
		self.whenEffective(None, "byOthers", choice=0, posinHand=-2)
		# 使用后步骤，但是此时的扳机只会触发星界密使和风潮的状态移除，因为其他的使用后步骤都要求是玩家亲自打出。
		if self.Game.GUI: self.Game.GUI.eraseOffBoardTrig(self.ID)
		self.Game.sendSignal("SpellBeenCast", self.ID, self, None, 0, "byOthers")

	def played(self, target=None, choice=0, mana=0, posinHand=-2, comment=""):
		if self.Game.GUI:
			self.Game.GUI.showOffBoardTrig(self)
			self.Game.GUI.wait(500)
		self.Game.sendSignal("SpellPlayed", self.ID, self, None, mana, "", choice)
		self.Game.sendSignal("Spellboost", self.ID, self, None, mana, "", choice)
		self.Game.gathertheDead()  # At this point, the minion might be removed/controlled by Illidan/Juggler combo.
		self.whenEffective(None, '', choice, posinHand)
		# There is no need for another round of death resolution.
		if self.Game.GUI: self.Game.GUI.eraseOffBoardTrig(self.ID)
		self.Game.sendSignal("SpellBeenCast", self.ID, self, None, 0, "")
		self.Game.Counters.hasPlayedQuestThisGame[self.ID] = True

	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		secretZone = self.Game.Secrets
		if secretZone.areaNotFull(self.ID):
			if self.description.startswith("Sidequest") \
				and all(quest.name != self.name for quest in secretZone.sideQuests[self.ID]):
				secretZone.sideQuests[self.ID].append(self)
				for trig in self.trigsBoard: trig.connect()
			else:  # The quest is a main quest
				if not secretZone.mainQuests[self.ID]:
					secretZone.mainQuests[self.ID].append(self)
					for trig in self.trigsBoard: trig.connect()
		return None


class Power(Card):
	type = "Power"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		#额外的英雄技能技能只有考达拉幼龙和要塞指挥官可以更改。
		#技能能否使用，需要根据已使用次数和基础机会和额外机会的和相比较。
		self.onBoard = True
		self.effects = {"Lifesteal": 0, "Poisonous": 0,
		
						 "Damage Boost": 0, "Can Target Minions": 0,
						 "Cost Health Instead": 0, "Can't be Played": 0,
						 }
		for key in type(self).effects.split(","):
			self.effects[key.strip()] = 1
	
	def turnStarts(self, ID):
		if ID == self.ID:
			self.usageCount = 0
			if self.btn: self.btn.checkHpr()
			
	def turnEnds(self, ID):
		if ID == self.ID:
			self.usageCount = 0

	def appears(self):
		self.usageCount = 0
		for trig in self.trigsBoard: trig.connect()
		if self.btn:
			self.btn.isPlayed, self.btn.card = True, self
			self.btn.placeIcons()
			self.btn.effectChangeAni()
		self.Game.sendSignal("HeroPowerAcquired", self.ID, self, None, 0, "")
		self.Game.Manas.calcMana_Powers()

	def disappears(self):
		for trig in self.trigsBoard: trig.disconnect()
		for manaMod in self.manaMods: manaMod.getsRemoved()
		self.manaMods = []

	def replaceHeroPower(self):
		powers, ID = self.Game.powers, self.ID
		GUI = self.Game.GUI
		if powers[ID]:
			oldPower = powers[ID]
			if GUI and oldPower.btn and oldPower.btn.np:
				GUI.seqHolder[-1].append(GUI.FUNC(print, "detaching power nodepath", oldPower.btn, oldPower.btn.np))
				GUI.seqHolder[-1].append(GUI.FUNC(oldPower.btn.np.detachNode))
			powers[ID].disappears()
		powers[ID] = self
		if GUI: GUI.heroZones[ID].placeCards()
		self.appears()
		print("Hero power replaced. ", powers[ID], powers[ID].btn, powers[ID].btn.np, powers[ID].btn.np.getParent())
		
	def chancesUsedUp(self):
		return self.Game.effects[self.ID]["Power Chance Inf"] < 1 \
				and self.usageCount >= (1 + (self.Game.effects[self.ID]["Power Chance 2"] > 0) )
				
	def available(self): #只考虑没有抉择的技能，抉择技能需要自己定义
		return not self.chancesUsedUp() and (not self.needTarget() or self.findTargets("")[0][0])

	def use(self, target=None, choice=0, sendthruServer=True):
		game = self.Game
		if not (game.Manas.affordable(self) and self.available() and self.selectionLegit(target, choice)):
			return False
		print("Using hero power", self.name)
		#支付费用，清除费用状态。
		subIndex, subWhere = self.ID, "Power"
		if target: tarIndex, tarWhere = target.pos, target.type+str(target.ID)
		else: tarIndex, tarWhere = 0, ''
		#准备游戏操作的动画
		GUI = game.GUI
		game.prepGUI4Ani(GUI)
		if GUI: GUI.showOffBoardTrig(self)
		
		game.Manas.payManaCost(self, self.mana)
		#如果有指向，则触发指向扳机（目前只有市长）
		targetHolder = [target]
		game.sendSignal("HeroPowerTargetDecision", self.ID, self, targetHolder, 0, "", choice)
		if target != targetHolder[0] and GUI:
			target = targetHolder[0]
			GUI.target = target
		else: target = targetHolder[0]
		minionsKilled = 0
		if target and target.type == "Minion" and game.effects[self.ID]["Power Sweep"] > 0:
			targets = game.neighbors2(target)[0]
			minionsKilled += self.effect(target, choice)
			if targets != []:
				for minion in targets: minionsKilled += self.effect(minion, choice)
		else: minionsKilled += self.effect(target, choice)
		
		#结算阶段结束，处理死亡，此时尚不进行胜负判定。
		#假设触发英雄技能消灭随从的扳机在死亡结算开始之前进行结算。（可能不对，但是相对比较符合逻辑。）
		if minionsKilled > 0:
			game.sendSignal("HeroPowerKilledMinion", game.turn, self, None, minionsKilled, "")
		game.gathertheDead()
		
		self.usageCount += 1
		#激励阶段，触发“每当你使用一次英雄技能”的扳机，如激励，虚空形态的技能刷新等。
		game.Counters.powerUsedThisTurn += 1
		game.sendSignal("HeroUsedAbility", self.ID, self, target, self.mana, "", choice)
		if GUI: GUI.usePowerAni(self)
		#激励阶段结束，处理死亡。此时可以进行胜负判定。
		game.gathertheDead(True)
		if GUI: GUI.decideCardColors()
		game.moves.append(("Power", subIndex, subWhere, tarIndex, tarWhere, choice))
		self.Game.wrapUpPlay(GUI, sendthruServer)
		return True
	
	def effect(self, target, choice=0):
		return 0

	def countDamageDouble(self):
		return sum(minion.effects["Power Heal&Dmg x2"] > 0 for minion in self.Game.minions[self.ID])

	def countHealDouble(self):
		return sum(minion.effects["Heal x2"] > 0 or minion.effects["Power Heal&Dmg x2"] > 0 for minion in self.Game.minions[self.ID])

	def createCopy(self, game):
		if self in game.copiedObjs:
			return game.copiedObjs[self]
		else:
			Copy = type(self)(game, self.ID)
			game.copiedObjs[self] = Copy
			Copy.mana = self.mana
			Copy.manaMods = [mod.selfCopy(Copy) for mod in self.manaMods]
			Copy.usageCount = self.usageCount
			Copy.options = [option.selfCopy(Copy) for option in self.options]
			Copy.effects = copy.deepcopy(self.effects)
			Copy.trigsBoard = [trig.createCopy(game) for trig in self.trigsBoard]
			Copy.x, Copy.y, Copy.z = self.x, self.y, self.z
			self.assistCreateCopy(Copy)
			return Copy


class Hero(Card):
	weapon, type = None, "Hero"
	health, heroPower = 30, None
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		cardType = type(self)
		self.attack_bare = 0
		self.tempAttChanges = []
		self.weapon = cardType.weapon
		self.attChances_base, self.attChances_extra = 1, 0
		self.pos = self.ID
		self.heroPower = cardType.heroPower(self.Game, self.ID) if cardType.heroPower else None
		self.effects = {"Windfury": 0, "Poisonous": 0,
		
						 "Enemy Effect Evasive": 0, "Cost Health Instead": 0, "Can't be Played": 0,
						 "Enemy Effect Damage Immune": 0, "Can't Be Attacked": 0, "Next Damage 0": 0,
						
						 "Frozen": 0, "Temp Stealth": 0, "Draw to Win": 0
						 }
		self.effectfromAura = {"Windfury": 0}
		
	def reset(self, ID, isKnown=True):
		creator, possi = self.creator, type(self) if isKnown else self.possi
		btn, x, y, z = self.btn, self.x, self.y, self.z
		self.__init__(self.Game, ID)
		self.creator, self.possi = creator, possi
		self.btn, self.x, self.y, self.z = btn, x, y, z
	
	"""Handle hero's attacks, attack chances, attack chances and frozen status."""
	def turnStarts(self, ID):
		if ID == self.ID:
			self.losesEffect("Temp Stealth", 0)
			if self.Game.effects[self.ID]["Immune2NextTurn"] > 0:
				self.losesEffect("Immune", amount=self.Game.effects[self.ID]["Immune2NextTurn"])
				self.Game.effects[self.ID]["Immune2NextTurn"] = 0
			if self.Game.effects[self.ID]["Evasive2NextTurn"] > 0:
				self.losesEffect("Evasive", amount=self.Game.effects[self.ID]["Evasive2NextTurn"])
				self.Game.effects[self.ID]["Evasive2NextTurn"] = 0

			weapon = self.Game.availableWeapon(self.ID)
			self.bareAttack, self.usageCount, self.attChances_extra = 0, 0, 0
			self.decideAttChances_base()
		self.calc_Attack()
		if self.btn: self.btn.statChangeAni()
		
	def turnEnds(self, ID):
		if self.Game.effects[self.ID]["ImmuneThisTurn"] > 0:
			self.losesEffect("Immune", amount=self.Game.effects[self.ID]["ImmuneThisTurn"])
			self.Game.effects[self.ID]["ImmuneThisTurn"] = 0
		#一个角色只有在自己的回合结束时有剩余的攻击机会才能解冻
		if ID == self.ID and self.effects["Frozen"] > 0 and self.attChances_base + self.attChances_extra > self.usageCount:
			self.losesEffect("Frozen", 0)

		self.usageCount = 0
		for attGain, revertTime in self.tempAttChanges:
			self.attack_bare -= attGain
		self.tempAttChanges = []
		self.calc_Attack()
		if self.btn: self.btn.effectChangeAni()
		
	def gainAttack(self, attGain, revertTime="EndofTurn"):
		self.attack_bare += attGain
		if revertTime: self.tempAttChanges.append((attGain, revertTime))
		self.calc_Attack()
		self.Game.sendSignal("HeroAttGained", self.ID, self, None, attGain, "")
		if self.btn: self.btn.statChangeAni(num1=attGain, action="buffDebuff")

	def calc_Attack(self):
		if self.Game.turn == self.ID:
			weapon = self.Game.availableWeapon(self.ID)
			self.attack = self.attack_bare + max(0, weapon.attack) if weapon else self.attack_bare
		else:
			self.attack = self.attack_bare
		self.Game.sendSignal("HeroAttCalc", self.ID, self, None, 0, "")

	def gainsArmor(self, armor):
		if armor > 0:
			self.armor += armor
			if self.btn: self.btn.statChangeAni(action="armorChange")
			self.Game.sendSignal("ArmorGained", self.ID, self, None, armor, "")

	def losesArmor(self, armor, all=False):
		if all:
			ownArmor = self.armor
			self.armor = 0
			if ownArmor: self.Game.sendSignal("ArmorLost", self.ID, self, None, ownArmor, "")
		else:
			self.armor -= armor
			self.Game.sendSignal("ArmorLost", self.ID, self, None, armor, "")
		if self.btn: self.btn.statChangeAni(action="armorChange")
	
	"""Handle hero's being selectable by subjects or not. And hero's availability for battle."""
	def canAttack(self):
		return self.actionable() and self.attack > 0 and self.effects["Frozen"] < 1 \
				and self.attChances_base + self.attChances_extra > self.usageCount

	def canAttackTarget(self, target):
		return self.canAttack() and target.selectablebyBattle(self)

	#Heroes don't have Lifesteal.
	def tryLifesteal(self, damage, damageType="None"):
		pass

	def takesDamage(self, subject, damage, sendDmgSignal=True, damageType="None"):
		game = self.Game
		if game.effects[self.ID]["Immune"] < 1:  # 随从首先结算免疫和圣盾对于伤害的作用，然后进行预检测判定
			if "Next Damage 0" in self.effects and self.effects["Next Damage 0"] > 0:
				damage = self.effects["Next Damage 0"] = 0
			if "Enemy Effect Damage Immune" in self.effects and self.effects[
				"Enemy Effect Damage Immune"] > 0 and damageType == "Ability":
				damage = 0
			if subject and "Deal Damage 0" in subject.effects and subject.effects["Deal Damage 0"] > 0:
				damage = 0
			if damage > 0:
				damageHolder = [damage]
				game.sendSignal("FinalDmgonHero?", self.ID, subject, self, damageHolder, "")
				damage = damageHolder[0]
				if damage > 0:
					if self.armor > damage:
						self.losesArmor(damage)
					else:
						self.health -= damage - self.armor
						self.losesArmor(0, all=True)
					if self.btn: self.btn.statChangeAni(num2=-damage, action="damage")
					game.Counters.dmgonHeroThisTurn[self.ID] += damage
					if sendDmgSignal:
						game.sendSignal("HeroTakesDmg", game.turn, subject, self, damage, "")
						game.sendSignal("HeroTookDmg", game.turn, subject, self, damage, "")
					if game.turn == self.ID:
						game.Counters.timesHeroChangedHealth_inOwnTurn[self.ID] += 1
						game.Counters.timesHeroTookDamage_inOwnTurn[self.ID] += 1
						game.Counters.heroChangedHealthThisTurn[self.ID] = True
						game.sendSignal("HeroChangedHealthinTurn", self.ID, None, None, 0, "")
			else:
				game.sendSignal("HeroTakes0Dmg", game.turn, subject, self, 0, "")
				game.sendSignal("HeroTook0Dmg", game.turn, subject, self, 0, "")
		else:
			damage = 0
		return damage

	def healthReset(self, health, health_max=False):
		healthChanged = health != self.health
		self.health = health
		if health_max: self.health_max = health_max
		if self.btn: self.btn.statChangeAni(num2=0, action="buffDebuff")
		if healthChanged and self.Game.turn == self.ID:
			self.Game.Counters.timesHeroChangedHealth_inOwnTurn[self.ID] += 1
			self.Game.Counters.heroChangedHealthThisTurn[self.ID] = True
			self.Game.sendSignal("HeroChangedHealthinTurn", self.ID, None, None, 0, "")

	#专门被英雄牌使用，加拉克苏斯大王和拉格纳罗斯都不会调用该方法。
	def played(self, target=None, choice=0, mana=0, posinHand=-2, comment=""): #英雄牌使用目前不存在触发发现的情况
	#使用阶段
		#英雄牌替换出的英雄的生命值，护甲和攻击机会等数值都会继承当前英雄的值。
		game, ID = self.Game, self.ID
		oldHero = game.heroes[ID]
		self.health, self.health_max, self.armor = oldHero.health, oldHero.health_max, oldHero.armor
		self.attack_bare, self.tempAttChanges, self.usageCount, self.armor = oldHero.attack_bare, oldHero.tempAttChanges, oldHero.usageCount, oldHero.armor
		self.onBoard, oldHero.onBoard, self.pos = True, False, ID #这个只是为了方便定义(i, where)
		#英雄牌进入战场。（本来是应该在使用阶段临近结束时移除旧英雄和旧技能，但是为了方便，在此时执行。）
		#继承旧英雄的生命状态和护甲值。此时英雄的被冻结和攻击次数以及攻击机会也继承旧英雄。
		#清除旧的英雄技能。
		game.powers[ID].disappears()
		game.powers[ID].heroPower = None
		game.heroes[ID].onBoard = False
		#旧英雄在消失前需要归还其所有的光环buff效果，目前只有Inara Stormcrash的+2攻和风怒
		while self.auraReceivers: self.auraReceivers[0].effectClear()
		heroPower = self.heroPower #这个英雄技能必须存放起来，之后英雄还有可能被其他英雄替换，但是这个技能要到最后才登场。
		game.heroes[ID] = self #英雄替换。如果后续有埃克索图斯再次替换英雄，则最后的英雄是拉格纳罗斯。
		game.heroes[ID].onBoard = True
		if game.GUI:
			game.GUI.showOffBoardTrig(self)
			game.GUI.wait(500)
		#使用时步骤，触发“每当你使用一张xx牌时”的扳机。
		game.sendSignal("HeroCardPlayed", ID, self, None, mana, "", choice)
		#英雄牌的最大生命值和现有生命值以及护甲被设定继承旧英雄的数值。并获得英雄牌上标注的护甲值。
		self.gainsArmor(type(self).armor)
		game.sendSignal("HeroReplaced", ID, self, None, 0, "")
		#使用阶段结束，进行死亡结算，此时尚不进行胜负判定。
		game.gathertheDead()
	#结算阶段
		#获得新的英雄技能。注意，在此之前英雄有可能被其他英雄代替，如伊利丹飞刀打死我方的管理者埃克索图斯。
			#埃克索图斯可以替换英雄和英雄技能，然后本英雄牌在此处开始结算，再次替换英雄技能为正确的英雄牌技能。
		heroPower.replaceHeroPower()
		#视铜须等的存在而结算战吼次数以及具体战吼。
		#不用返回主体，但是当沙德沃克调用时whenEffective函数的时候需要。
		if game.effects[ID]["Battlecry x2"] > 0:
			self.whenEffective(None, "", choice)
		self.whenEffective(None, "", choice)
		if self.weapon: #如果英雄牌本身带有武器，如迦拉克隆等。则装备那把武器
			self.equipWeapon(self.weapon(game, ID))
		self.calc_Attack()
		if self.btn: self.btn.statChangeAni()
		self.decideAttChances_base()
		#结算阶段结束，处理死亡，此时尚不进行胜负判定。
		game.gathertheDead()

	#大王，炎魔之王拉格纳罗斯等替换英雄，此时没有战吼。
	#炎魔之王变身不会摧毁玩家的现有装备和奥秘。只会移除冰冻，免疫和潜行等状态。
	def replaceHero(self, fromHeroCard=False):
		#英雄被替换
		#被替换的英雄失去所有护甲。
		#假设直接替换的英雄不会继承之前英雄获得的回合内攻击力增加。
		game, ID = self.Game, self.ID
		healthChanged = game.heroes[ID].health == self.health #目前只有大王和拉格纳罗斯会改变英雄的血量
		self.onBoard, self.pos, self.usageCount = True, ID, game.heroes[ID].usageCount
		if not fromHeroCard: self.losesArmor(0, all=True) #被大王等非英牌替换时，护甲会被摧毁
		#旧英雄在消失前需要归还其所有的光环buff效果，目前只有Inara Stormcrash的+2攻和风怒
		while self.auraReceivers: self.auraReceivers[0].effectClear()
		#英雄牌进入战场。（本来是应该在使用阶段临近结束时移除旧英雄和旧技能，但是为了方便，在此时执行。）
		#继承旧英雄的生命状态和护甲值。此时英雄的被冻结和攻击次数以及攻击机会也继承旧英雄。
		#大王和炎魔之王在替换之前被定义，拥有15或者8点生命值。0点护甲值和英雄技能等也已定义完毕。
		game.heroes[ID] = self
		if self.heroPower: self.heroPower.replaceHeroPower()
		if self.weapon: #如果英雄本身带有装备，则会替换当前的玩家装备（如加拉克苏斯大王）
			self.equipWeapon(self.weapon(game, ID)) #装备武器本身就会处理英雄攻击力的变化
		else:
			self.calc_Attack()
			if self.btn: self.btn.effectChangeAni()
		if not fromHeroCard: #英雄牌被其他牌打出时不会取消当前玩家的免疫状态
			#Hero's immune state is gone, except that given by Mal'Ganis
			status = game.effects[ID]
			self.losesEffect("Immune", amount=status["Immune2NextTurn"] + status["ImmuneThisTurn"])
			status["ImmuneThisTurn"] = status["Immune2NextTurn"] = 0
		#Send signal to notify auras that change hero status, e.g., Inara Stormcrash
		game.sendSignal("HeroReplaced", ID, self, None, 0, "")
		if healthChanged and game.turn == ID:
			game.Counters.timesHeroChangedHealth_inOwnTurn[ID] += 1
			game.Counters.heroChangedHealthThisTurn[ID] = True
			game.sendSignal("HeroChangedHealthinTurn", ID, None, None, 0, "")

	def createCopy(self, game):
		if self in game.copiedObjs:
			return game.copiedObjs[self]
		else:
			Copy = type(self)(game, self.ID)
			game.copiedObjs[self] = Copy
			Copy.mana = self.mana
			Copy.manaMods = [mod.selfCopy(Copy) for mod in self.manaMods]
			Copy.attack, Copy.attack_bare, Copy.armor = self.attack, self.attack_bare, self.armor
			Copy.health_max, Copy.health = self.health_max, self.health
			Copy.attChances_base, Copy.attChances_extra, Copy.usageCount = self.attChances_base, self.attChances_extra, self.usageCount
			Copy.tempAttChanges = copy.deepcopy(self.tempAttChanges)
			Copy.effectfromAura = copy.deepcopy(self.effectfromAura)
			Copy.auraReceivers = [receiver.selfCopy(Copy) for receiver in self.auraReceivers]

			Copy.onBoard, Copy.inHand, Copy.inDeck = self.onBoard, self.inHand, self.inDeck
			Copy.enterHandTurn = self.enterHandTurn
			Copy.dead = self.dead
			Copy.effects = copy.deepcopy(self.effects)
			Copy.effects = copy.deepcopy(self.effects)
			Copy.effects = copy.deepcopy(self.effects)
			Copy.options = [option.selfCopy(Copy) for option in self.options]
			Copy.trigsBoard = [trig.createCopy(game) for trig in self.trigsBoard]
			Copy.trigsHand = [trig.createCopy(game) for trig in self.trigsHand]
			Copy.trigsDeck = [trig.createCopy(game) for trig in self.trigsDeck]
			Copy.effectViable, Copy.evanescent = self.effectViable, self.evanescent
			Copy.tracked, Copy.creator, Copy.possi = self.tracked, self.creator, self.possi
			Copy.x, Copy.y, Copy.z = self.x, self.y, self.z
			self.assistCreateCopy(Copy)
			return Copy


class Weapon(Card):
	type = "Weapon"
	def __init__(self, Game, ID):
		super().__init__(Game, ID)
		self.effects = {"Lifesteal": 0, "Poisonous": 0, "Windfury": 0,
						 "Immune": 0,
						 "Sweep": 0, "Cost Health Instead": 0, "Can't Attack Heroes": 0, "Can't be Played": 0,
						 }
		for key in type(self).effects.split(","):
			self.effects[key.strip()] = 1
	
	def reset(self, ID, isKnown=True):
		creator, possi = self.creator, type(self) if isKnown else self.possi
		btn, x, y, z = self.btn, self.x, self.y, self.z
		self.__init__(self.Game, ID)
		self.creator, self.possi = creator, possi
		self.btn, self.x, self.y, self.z = btn, x, y, z
	
	"""Handle weapon entering/leaving board/hand/deck"""
	# 武器进场直接连接侦听器，比如公正之剑可以触发伊利丹的召唤，这个召唤又反过来触发公正之剑的buff效果。
	def appears(self):
		# 注意，此时武器还不能设为onBoard,因为之后可能会涉及亡语随从为英雄装备武器。
		# 尚不能因为武器标记为onBoard而调用其destroyed。
		self.inHand = self.inDeck = self.dead = False
		self.mana = type(self).mana
		if self.btn: self.btn.placeIcons()
		for trig in self.trigsBoard + self.deathrattles: trig.connect()
		for aura in self.auras.values(): aura.auraAppears() #目前似乎只用舔舔魔杖有武器光环

	def setasNewWeapon(self):
		curGame = self.Game
		self.onBoard, self.dead = True, False
		# 因为武器在之前已经被添加到武器列表，所以sequence需要-1，不然会导致错位
		self.seq = len(curGame.minions[1]) + len(curGame.minions[2]) + len(curGame.weapons[1]) + len(curGame.weapons[2]) - 1
		hero = curGame.heroes[self.ID]
		hero.calc_Attack()
		if hero.btn: hero.btn.statChangeAni(action="buffDebuff")
		hero.decideAttChances_base()
		curGame.sendSignal("WeaponEquipped", self.ID, self, None, 0, "")

	# Take care of the hero's attack chances and attack.
	# The deathrattles will be left to gathertheDead() and deathHandle()
	def destroyed(self):
		if self.onBoard:  # 只有装备着的武器才会触发，以防连续触发。
			if self.effects["Windfury"] > 0:
				self.Game.heroes[self.ID].decideAttChances_base()
			self.onBoard, self.dead = False, True
			hero = self.Game.heroes[self.ID]
			hero.calc_Attack()
			if hero.btn: hero.btn.statChangeAni(action="buffDebuff")
			# 移除武器对应的场上扳机，亡语扳机在deathrattles中保存
			for trig in self.trigsBoard: trig.disconnect()
			for aura in self.auras.values(): aura.auraDisappears()
	# self.Game.sendSignal("WeaponRemoved", self.ID, self, None, 0, "")

	def deathResolution(self, attackwhenDies, armedTrigs_WhenDies, armedTrigs_AfterDied):
		# 除了武器亡语以外，目前只有一个应对武器被摧毁的扳机，即冰封王座的Grave Shambler
		self.Game.sendSignal("WeaponDestroyed", self.ID, None, self, attackwhenDies, "", armedTrigs_WhenDies)
		self.Game.sendSignal("WeaponRemoved", self.ID, None, self, 0, "")
		for trig in self.deathrattles: trig.disconnect()
		
	def disappears(self):
		if self.onBoard:  # 只有装备着的武器才会触发，以防连续触发。
			if self.effects["Windfury"] > 0:
				self.Game.heroes[self.ID].decideAttChances_base()
			self.onBoard = False
			hero = self.Game.heroes[self.ID]
			hero.calc_Attack()
			if hero.btn: hero.btn.statChangeAni()
			# 移除武器对应的场上扳机，亡语扳机在deathrattles中保存
			for trig in self.trigsBoard: trig.disconnect()
			for aura in self.auras.values(): aura.auraDisappears()
			self.Game.sendSignal("WeaponRemoved", self.ID, self, None, 0, "")

	"""Handle the mana, durability and stat of weapon."""
	# This method is invoked by Hero class, not a listner.
	def loseDurability(self):
		self.health -= 1
		if self.btn: self.btn.statChangeAni(action="damage")
	
	def countHealDouble(self):  # 随从和武器的治疗效果
		return sum(minion.effects["Heal x2"] > 0 for minion in self.Game.minions[self.ID])

	"""Handle the weapon being played/equipped."""
	def played(self, target=None, choice=0, mana=0, posinHand=-2, comment=""):
		# 使用阶段
		# 武器连接侦听器，比如公正之剑可以触发伊利丹的召唤，这个召唤又反过来触发公正之剑的buff效果。
		self.appears()  # 此时可以建立侦听器。此时onBoard还是False
		# 注意，暂时不取消已经装备的武器的侦听，比如两把公正之剑可能同时为伊利丹召唤的元素buff。
		# 使用时步骤，触发“每当你使用一张xx牌”的扳机，如伊利丹和无羁元素。
		self.Game.sendSignal("WeaponPlayed", self.ID, self, target, 0, "", choice=0)
		# 结算过载。
		if self.overload > 0:
			self.Game.Manas.overloadMana(self.overload, self.ID)
		# 使用阶段结束，处理亡语，暂不处理胜负问题。
		# 注意，如果此时伊利丹飞刀造成了我方佛丁的死亡，则其装备的灰烬使者会先替换目前装备的武器。
		# 之后在结算阶段的武器正式替换阶段，被替换的武器就变成了灰烬使者。最终装备的武器依然是打出的这把武器。
		self.Game.gathertheDead()  # 此时被替换的武器先不视为死亡，除非被亡语引起的死亡结算先行替换（如佛丁）。
		# 结算阶段
		# 根据市长的存在情况来决定随机目标。
		targetHolder = [target]
		self.Game.sendSignal("BattlecryTargetDecision", self.ID, self, targetHolder, 0, "", choice=0)
		if target != targetHolder[0] and self.Game.GUI:
			target = targetHolder[0]
			self.Game.GUI.target = target
		else:
			target = targetHolder[0]
		# 根据铜须的存在情况来决定战吼的触发次数。不同于随从，武器的连击目前不会触发
		if self.Game.effects[self.ID]["Battlecry x2"] > 0:
			# 对方武器而言没有必要返回主体对象，但是当战吼被沙德沃克调用的时候，需要返回。
			target = self.whenEffective(target, "", choice, posinHand)
		target = self.whenEffective(target, "", choice, posinHand)
		# 消灭旧武器，并将列表前方的武器全部移除。
		for weapon in self.Game.weapons[self.ID]:
			if weapon != self:
				# The removal of the preivous weapons will be left to the gathertheDead() method.
				# 只有标记为onBoard的武器调用destroyed会有反应，防止因为之前佛丁的死亡引起同一把武器的多次摧毁信号。
				weapon.destroyed()  # 触发“每当你的一把武器被摧毁时”和“每当你的一把武器离场时”的扳机，如南海船工。
		# 打出的这把武器会成为最后唯一还装备着的武器。触发“每当你装备一把武器时”的扳机，如锈水海盗。
		self.setasNewWeapon()  # 此时打出的武器的onBoard才会正式标记为True
		# 结算阶段结束，处理亡语。（此时的亡语结算会包括武器的亡语结算。）
		self.Game.gathertheDead()
	# 完成阶段在Game.playWeapon中处理。

	"""Handle the weapon restoring health, dealing damage and dealing AOE effects."""
	# 对于武器而言，dealsDamage()只有毁灭之刃可以使用，因为其他的武器造成伤害不是AOE伤害就是战斗伤害
	# 战斗伤害会在随从和英雄的attacks()方法中统一处理。毁灭之刃是唯一的拥有单体战吼的武器。

	def createCopy(self, game):
		if self in game.copiedObjs:
			return game.copiedObjs[self]
		else:
			Copy = type(self)(game, self.ID)
			game.copiedObjs[self] = Copy
			Copy.mana = self.mana
			Copy.manaMods = [mod.selfCopy(Copy) for mod in self.manaMods]
			Copy.attack, Copy.health = self.attack, self.health
			Copy.effects, Copy.effects = copy.deepcopy(self.effects), copy.deepcopy(self.effects)
			Copy.onBoard, Copy.inHand, Copy.inDeck = self.onBoard, self.inHand, self.inDeck
			Copy.enterHandTurn = self.enterHandTurn
			Copy.seq = self.seq
			#对武器的光环目前只有增加攻击力
			Copy.auraReceivers = [receiver.selfCopy(Copy) for receiver in self.auraReceivers]
			for key, value in self.auras.items():
				Copy.auras[key] = value.createCopy(game)
			Copy.options = [option.selfCopy(Copy) for option in self.options]
			Copy.deathrattles = [trig.createCopy(game) for trig in self.deathrattles]
			Copy.trigsBoard = [trig.createCopy(game) for trig in self.trigsBoard]
			Copy.trigsHand = [trig.createCopy(game) for trig in self.trigsHand]
			Copy.trigsDeck = [trig.createCopy(game) for trig in self.trigsDeck]
			Copy.effectViable, Copy.evanescent = self.effectViable, self.evanescent
			Copy.tracked, Copy.creator, Copy.possi = self.tracked, self.creator, self.possi
			Copy.x, Copy.y, Copy.z = self.x, self.y, self.z
			self.assistCreateCopy(Copy)
			return Copy


class Option:
	name, type, description = "", "", ""
	index, effect, isLegendary = '', '', False
	def __init__(self, entity=None, ID=0): #ID is a placeholder.
		self.entity, self.ID = entity, entity.ID if entity else ID
		self.type = "Option"
		self.index, self.effect = type(self).index, type(self).effect
		self.isLegendary = type(self).isLegendary
		self.btn, self.x, self.y, self.z = None, 0, 0, 0
	
	def available(self):
		return True

	def text(self, CHN):
		return ''
	
	def selfCopy(self, recipient):
		return type(self)(recipient)

	# 抉择选项的复制一定是以复制卡牌为前提的，调用此函数时，抉择主体一定已经被复制了
	def createCopy(self, game):
		return type(self)(game.copiedObjs[self.entity])

#用于处理卡牌的可能性
class PossiHolder:
	def __init__(self, card, real, possi, creator="", related=[]):
		self.real = real #真实的牌类型
		self.possi = possi #可能的牌类型的列表
		self.creator = creator
		self.related = related #一张牌的可能性是可以与其他牌存在互斥关系的，这时盛放其他可能性容器
		self.card = card

	def confirm(self): #自己的可能性完全确定时
		self.possi = [self.real]
		for possiHolder in self.related:
			possiHolder.possi.remove(self.real)
			possiHolder.related.remove(self) #当一个可能性容器被完全确定时，其他的可能性容器就不再与这个可能性相关联

	def ruleOut(self, type): #从这个容器的可能性中移除一个。与此牌相关联的其他牌
		self.possi.remove(type)
		#当一个可能性容器被完全确定时，其他的可能性容器就不再与这个可能性相关联
		if len(self.possi) == 1:
			for possiHolder in self.related:
				possiHolder.possi.remove(self.real)
				possiHolder.related.remove(self)

	def createCopy(self, game):
		Copy = PossiHolder(self.card.createCopy(game),  self.real, self.possi[:], self.creator, self.related)