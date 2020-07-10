import numpy as np
import inspect
import copy
from VariousHandlers import ManaModification

def extractfrom(target, listObject):
	try: return listObject.pop(listObject.index(target))
	except: return None
	
def fixedList(listObject):
	return listObject[0:len(listObject)]
	
def PRINT(game, string, *args):
	if game.GUI:
		if not game.mode: game.GUI.printInfo(string)
	elif not game.mode: print("game's guide mode is 0\n", string)
	
def copyListDictTuple(obj, recipient):
	if isinstance(obj, list):
		objCopy = []
		for element in obj:
			#check if they're basic types, like int, str, bool, NoneType, 
			if isinstance(element, (type(None), int, float, str, bool)):
				#Have tested that basic types can be appended and altering the original won't mess with the content in the list.
				objCopy.append(element)
			elif callable(element): #If the element is a function
				func_name = element.__qualname__.split('.')[1]
				objCopy.append(getattr(recipient, func_name))
			elif inspect.isclass(element):
				objCopy.append(element)
			elif type(element) == type(recipient.Game):
				objCopy.append(recipient.Game)
			elif type(element) == list or type(element) == dict or type(element) == tuple: #If the element is a list or dict, just recursively use this function.
				objCopy.append(copyListDictTuple(element, recipient))
			else: #If the element is a self-defined class. All of them have selfCopy methods.
				objCopy.append(element.selfCopy(recipient))
	elif isinstance(obj, dict):
		objCopy = {}
		for key, value in obj.items():
			if isinstance(value, (type(None), int, float, str, bool)):
				objCopy[key] = value
			#随从的列表中不会引用游戏
			elif callable(value):
				func_name = value.__qualname__.split('.')[1]
				print("The value to copy is ", func_name)
				objCopy[key] = getattr(recipient, func_name)
			elif inspect.isclass(value):
				objCopy[key] = value
			elif type(value) == type(recipient.Game):
				objCopy[key] = recipient.Game
			elif type(value) == list or type(value) == dict or type(value) == tuple:
				objCopy[key] = copyListDictTuple(value, recipient)
			else:
				objCopy[key] = value.selfCopy(recipient)
	else: #elif isinstance(obj, tuple):
		tupleTurnedList = list(obj) #tuple因为是immutable的，所以要根据它生成一个列表
		objCopy = copyListDictTuple(tupleTurnedList, recipient) #复制那个列表
		objCopy = list(objCopy) #把那个列表转换回tuple
	return objCopy
	
	
class Card:
	#For Choose One cards.
	def needTarget(self, choice=0):
		return type(self).requireTarget
		
	def returnTrue(self, choice=0):
		return True
		
	def returnFalse(self, choice=0):
		return False
		
	def selfManaChange(self):
		pass
		
	def randomorDiscover(self):
		return "No RNG"
		
	#This is for battlecries with specific target requirement.
	def effectCanTrigger(self):
		pass
		
	def checkEvanescent(self):
		self.evanescent = False
		for trigger in self.triggersonBoard + self.triggersinHand:
			if hasattr(trigger, "makesCardEvanescent"):
				self.evanescent = True
				break
				
	#处理卡牌进入/离开 手牌/牌库时的扳机和各个onBoard/inHand/inDeck标签
	def entersHand(self):
		self.onBoard, self.inHand, self.inDeck = False, True, False
		for trigger in self.triggersinHand:
			trigger.connect()
		return self
		
	def leavesHand(self, intoDeck=False):
		self.onBoard, self.inHand, self.inDeck = False, False, False
		#将注册了的场上、手牌和牌库扳机全部注销。
		for trigger in self.triggersonBoard:
			trigger.disconnect()
			if hasattr(trigger, "temp") and trigger.temp: #If the trigger is temporary, it will be removed once it leaves hand, whether being discarded, played or shuffled into deck
				extractfrom(trigger, self.triggersonBoard)
		for trigger in self.triggersinHand:
			trigger.disconnect()
			if hasattr(trigger, "temp") and trigger.temp: #If the trigger is temporary, it will be removed once it leaves hand, whether being discarded, played or shuffled into deck
				extractfrom(trigger, self.triggersinHand)
		for trigger in self.triggersinDeck:
			trigger.disconnect()
			if hasattr(trigger, "temp") and trigger.temp: #If the trigger is temporary, it will be removed once it leaves hand, whether being discarded, played or shuffled into deck
				extractfrom(trigger, self.triggersinDeck)
		#无论如果离开手牌，被移出还是洗回牌库，费用修改效果（如大帝-1）都会消失
		for manaMod in fixedList(self.manaModifications):
			manaMod.getsRemoved()
		self.manaModifications = []
		
	def entersDeck(self):
		self.onBoard, self.inHand, self.inDeck = False, False, True
		#Hand_Deck.shuffleCardintoDeck won't track the mana change.
		self.Game.Manas.calcMana_Single(self)
		for trigger in self.triggersinDeck:
			trigger.connect()
			
	def leavesDeck(self, intoHand=True):
		self.onBoard, self.inHand, self.inDeck = False, False, False
		#将注册了的场上、手牌和牌库扳机全部注销。
		for trigger in self.triggersonBoard:
			trigger.disconnect()
			if hasattr(trigger, "temp") and trigger.temp: #If the trigger is temporary, it will be removed once it leaves hand, whether being discarded, played or shuffled into deck
				extractfrom(trigger, self.triggersonBoard)
		for trigger in self.triggersinHand:
			trigger.disconnect()
			if hasattr(trigger, "temp") and trigger.temp: #If the trigger is temporary, it will be removed once it leaves hand, whether being discarded, played or shuffled into deck
				extractfrom(trigger, self.triggersinHand)
		for trigger in self.triggersinDeck:
			trigger.disconnect()
			if hasattr(trigger, "temp") and trigger.temp: #If the trigger is temporary, it will be removed once it leaves hand, whether being discarded, played or shuffled into deck
				extractfrom(trigger, self.triggersinDeck)
		if intoHand == False: #离开牌库时，只有去往手牌中时费用修改效果不会丢失。
			for manaMod in self.manaModifications:
				manaMod.getsRemoved()
			self.manaModifications = []
			
	"""Handle the target selection. All methods belong to minions. Other types will define their own methods."""
	def targetCorrect(self, target, choice=0):
		if target.type != "Minion" and target.type != "Hero":
			PRINT(self.Game, "The target is not minion or hero.")
			return False
		if target.onBoard == False:
			PRINT(self.Game, "The target is not onBoard")
			return False
		return True
		
	def selectablebyBattle(self, subject):
		if self.type == "Minion":
			if self.onBoard and self.ID != subject.ID and self.status["Temp Stealth"] + self.status["Immune"] + self.keyWords["Stealth"] < 1:
				if self.keyWords["Taunt"] > 0 or self.Game.status[subject.ID]["Ignore Taunt"] > 0:
					return True
				else:
					for minion in self.Game.minionsonBoard(self.ID):
						if minion.keyWords["Taunt"] > 0 and minion.status["Temp Stealth"] + minion.status["Immune"] + minion.keyWords["Stealth"] < 1:
							PRINT(self.Game, "%s is behind friendly Taunt minions and can't be attacked first."%self.name)
							return False
					return True
		elif self.type == "Hero":
			if self.onBoard and self.ID != subject.ID and self.status["Temp Stealth"] + self.Game.status[self.ID]["Immune"] < 1:
				if self.Game.status[subject.ID]["Ignore Taunt"] > 0: return True #如果对方的攻击无论嘲讽，则始终可以被选定
				else: #如果对方没有无视嘲讽的光环，则需要判定角色是否藏在嘲讽之后
					for minion in self.Game.minionsonBoard(self.ID):
						if minion.keyWords["Taunt"] > 0 and minion.status["Temp Stealth"] + minion.status["Immune"] + minion.keyWords["Stealth"] < 1:
							PRINT(self.Game, "%s is behind friendly Taunt minions and can't be attacked first."%self.name)
							return False
					return True
		return False
		
	def canSelect(self, target):
		if target.type == "Hero":
			return {"Power": target.onBoard and self.Game.status[target.ID]["Evasive"] < 1 and (self.ID == target.ID or target.status["Temp Stealth"] + self.Game.status[target.ID]["Immune"] < 1),
					"Spell": target.onBoard and self.Game.status[target.ID]["Evasive"] < 1 and (self.ID == target.ID or target.status["Temp Stealth"] + self.Game.status[target.ID]["Immune"] < 1),
					"Minion": target.onBoard and (target.ID == self.ID or self.Game.status[target.ID]["Immune"] + target.status["Temp Stealth"] < 1),
					"Weapon": target.onBoard and (target.ID == self.ID or self.Game.status[target.ID]["Immune"] + target.status["Temp Stealth"] < 1),
					}[self.type]
		else: #"Minion"
			return {"Power": target.onBoard and target.marks["Evasive"] < 1 and (self.ID == target.ID or target.marks["Enemy Evasive"] + target.status["Immune"] + target.keyWords["Stealth"] + target.status["Temp Stealth"] < 1),
					"Spell": target.onBoard and target.marks["Evasive"] < 1 and (self.ID == target.ID or target.marks["Enemy Evasive"] + target.status["Immune"] + target.keyWords["Stealth"] + target.status["Temp Stealth"] < 1),
					"Minion": target.onBoard and (target.ID == self.ID or target.status["Immune"] + target.keyWords["Stealth"] + target.status["Temp Stealth"] < 1),
					"Weapon": target.onBoard and (target.ID == self.ID or target.status["Immune"] + target.keyWords["Stealth"] + target.status["Temp Stealth"] < 1),
					}[self.type]
					
	def selectableEnemyMinionExists(self, choice=0):
		for minion in self.Game.minionsonBoard(3-self.ID):
			if self.canSelect(minion) and self.targetCorrect(minion, choice):
				return True
		return False
		
	def selectableFriendlyMinionExists(self, choice=0):
		for minion in self.Game.minionsonBoard(self.ID):
			if self.canSelect(minion) and self.targetCorrect(minion, choice):
				return True
		return False
		
	def selectableMinionExists(self, choice=0):
		return self.selectableFriendlyMinionExists(choice) or self.selectableEnemyMinionExists(choice)
		
	def selectableEnemyExists(self, choice=0):
		if self.canSelect(self.Game.heroes[3-self.ID]) and self.targetCorrect(self.Game.heroes[3-self.ID], choice):
			return True
		else:
			return self.selectableEnemyMinionExists(choice)
			
	#There is always a selectable friendly character -- hero.
	def selectableFriendlyExists(self, choice=0): #For minion battlecries, the friendly hero is always selectable
		if self.type == "Spell" or self.type == "Power":
			return (self.canSelect(self.Game.heroes[self.ID]) and self.targetCorrect(self.Game.heroes[self.ID])) or self.selectableFriendlyMinionExists(choice)
		return True
		
	def selectableCharacterExists(self, choice=0):
		return self.selectableFriendlyExists(choice) or self.selectableEnemyExists(choice)
		
	#For targeting battlecries(Minions/Weapons)
	def targetExists(self, choice=0):
		return True
		
	def selectionLegit(self, target, choice=0):
		#抉择牌在有全选光环时，选项自动更正为"ChooseBoth"
		if self.chooseOne > 0:
			if self.Game.status[self.ID]["Choose Both"] > 0:
				choice = "ChooseBoth"
			elif choice < 0 or choice >= len(self.options):
				PRINT(self.Game, "Choose One card given an invalid choice {}".format(choice))
				return False
		else: choice = 0
		
		PRINT(self.Game, "Verifying the validity of selection. Subject {}, target {} with choice {}".format(self.name, target, choice))
		if target: #指明了目标
			#在指明目标的情况下，只有抉择牌的选项是合理的，选项需要目标，目标对于这个选项正确，且目标可选时，才能返回正确。
			if self.needTarget(choice) == False:
				PRINT(self.Game, "The card doesn't need target.")
				return False
			if self.targetCorrect(target, choice) == False:
				PRINT(self.Game, "The card is given a wrong target.")
				return False
			if self.canSelect(target) == False:
				PRINT(self.Game, "The target is not selectable to the card.")
				return False
			return True
		else: #No target selected.
			#法术，武器和英雄技能如果是指向性的必须要有指定目标才可能使用。
			if self.type == "Spell" or self.type == "Weapon" or self.type == "Power":
				if self.needTarget(choice) == False:
					return True
				else:
					PRINT(self.Game, "Targeting spell/weapon/hero requires target to be played.")
			elif self.type == "Minion": #随从可以在战吼非指向或者没有战吼目标的情况下使用。
				if self.needTarget(choice) == False or self.targetExists(choice) == False:
					return True
				else:
					PRINT(self.Game, "Minion with targeting battlecry must select a target when possible.")
			else: #英雄牌目标没有需要指定目标的，所以可以直接返回True
				return True
				
		return False
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		return target
		
	"""Handle the card doing battle(Minion and Hero)"""
	#Game.battle() invokes this function.
	#我方有扫荡打击的狂暴者攻击对方相邻的两个狂暴者之一，然后扫荡打击在所有受伤开始之前触发，
	#然后被攻击的那个狂暴者先受伤加攻，然后我方的狂暴者受伤加攻，最后是被AOE波及的那个狂暴者加攻。
	#说明扫荡打击是把相邻的随从列入伤害处理列表 ，主要涉及的两个随从是最先结算的两个，
	#被扫荡打击涉及的两个随从从左到右依次结算。
	def attacks(self, target, consumeAttackChance=True):
		PRINT(self.Game, "%s attacks %s"%(self.name, target.name))
		subject_attack, target_attack = max(0, self.attack), max(0, target.attack)
		if self.type == "Minion" and self.keyWords["Stealth"] > 0:
			self.losesKeyword("Stealth")
		self.status["Temp Stealth"] = 0
		#Manipulate the health of the subject/target's health.
		#Only send out "MinionTakesDamage" signal at this point.
		if consumeAttackChance:
			self.attTimes += 1
			
		damageDealingList = []
		#如果攻击者是英雄且装备着当前回合打开着的武器，则将攻击的伤害来源视为那把武器。
		if self.type == "Hero" and self.Game.availableWeapon(self.ID) and self.ID == self.Game.turn:
			damageDealer_attacker = self.Game.availableWeapon(self.ID)
		else:
			damageDealer_attacker = self
		#如果被攻击者是英雄，且装备着当前回合打开着的武器，则将攻击目标造成的伤害来源视为那把武器。
		if target.type == "Hero" and self.Game.availableWeapon(target.ID) and target.ID == self.Game.turn:
			damageDealer_target = self.Game.availableWeapon(target.ID)
		else:
			damageDealer_target = target
			
		#首先结算攻击者对于攻击目标的伤害，如果攻击力小于1，则攻击目标不会被记入伤害处理列表。
		#注意这个伤害承受目标不一定是攻击目标，因为有博尔夫碎盾以及钳嘴龟持盾者的存在
		#承受伤害者的血量减少，结算剧毒，但是此时不会发出受伤信号。
		objtoTakeDamage = self.Game.DmgHandler.damageTransfer(target)
		damageActual = objtoTakeDamage.takesDamage(damageDealer_attacker, subject_attack, sendDamageSignal=False)
		if damageActual > 0:
			damageDealingList.append((damageDealer_attacker, objtoTakeDamage, damageActual))
			
		#寻找受到攻击目标的伤害的角色。同理，此时受伤的角色不会发出受伤信号，这些受伤信号会在之后统一发出。
		objtoTakeDamage = self.Game.DmgHandler.damageTransfer(self)
		damageActual = objtoTakeDamage.takesDamage(damageDealer_target, target_attack, sendDamageSignal=False)
		if damageActual > 0:
			damageDealingList.append((damageDealer_target, objtoTakeDamage, damageActual))
		#如果攻击者的伤害来源（随从或者武器）有对相邻随从也造成伤害的扳机，则将相邻的随从录入处理列表。
		if damageDealer_attacker.type != "Hero" and damageDealer_attacker.marks["Sweep"] > 0 and target.type == "Minion":
			adjacentMinions = self.Game.adjacentMinions2(target)[0] #此时被攻击的随从一定是在场的，已经由Game.battleRequest保证。
			for minion in adjacentMinions:
				objtoTakeDamage = self.Game.DmgHandler.damageTransfer(minion)
				damageActual = objtoTakeDamage.takesDamage(damageDealer_attacker, subject_attack, sendDamageSignal=False)
				if damageActual > 0:
					damageDealingList.append((damageDealer_attacker, objtoTakeDamage, damageActual))
					
		if damageDealer_attacker.type == "Weapon":
			damageDealer_attacker.loseDurability()
		for damageDealer, objtoTakeDamage, damage in damageDealingList:
			#参与战斗的各方在战斗过程中只减少血量，受伤的信号在血量和受伤名单登记完毕之后按被攻击者，攻击者，被涉及者顺序发出。
			self.Game.sendSignal(objtoTakeDamage.type+"TakesDamage", self.Game.turn, damageDealer, objtoTakeDamage, damage, "")
			self.Game.sendSignal(objtoTakeDamage.type+"TookDamage", self.Game.turn, damageDealer, objtoTakeDamage, damage, "")
			#吸血扳机始终在队列结算的末尾。
			damageDealer.tryLifesteal(damage)
			
	"""Handle cards dealing targeting/AOE damage/heal to target(s)."""
	#Handle Lifesteal of a card. Currently Minion/Weapon/Spell classs have this method.
	##法术因为有因为外界因素获得吸血的能力，所以有自己的tryLifesteal方法。
	def tryLifesteal(self, damage):
		if self.keyWords["Lifesteal"] > 0 or (self.type == "Spell" and self.Game.status[self.ID]["Spells Lifesteal"] > 0):
			heal = damage * (2 ** self.countHealDouble())
			PRINT(self.Game, "%s deals %d damage and restores %d Health to player"%(self.name, damage, heal))
			if self.Game.status[self.ID]["Heal to Damage"] > 0:
				#If the Lifesteal heal is converted to damage, then the obj to take the final 
				#damage will not cause Lifesteal cycle.
				objtoTakeDamage_Auchenai = self.Game.DmgHandler.damageTransfer(self.Game.heroes[self.ID])
				objtoTakeDamage_Auchenai.takesDamage(self, heal)
			else: #Heal is heal.
				self.Game.heroes[self.ID].getsHealed(self, heal)
				
	#可以对在场上以及手牌中的随从造成伤害，同时触发应有的响应，比如暴乱狂战士和+1攻击力和死亡缠绕的抽牌。
	#牌库中的和已经死亡的随从免疫伤害，但是死亡缠绕可以触发抽牌。
	#吸血同样可以对于手牌中的随从生效并为英雄恢复生命值。如果手牌中的随从有圣盾，那个圣盾可以抵挡伤害，那个随从在打出后没有圣盾（已经消耗）。
	#暂时可以考虑不把吸血做成场上扳机，因为几乎没有战吼随从可以获得吸血，直接将吸血视为随从的dealsDamage自带属性也可以。
	def dealsDamage(self, target, damage):
		if target.onBoard or target.inHand:
			objtoTakeDamage = self.Game.DmgHandler.damageTransfer(target)
			#超杀和造成伤害触发的效果为场上扳机.吸血始终会在队列的末尾结算。
			#战斗时不会调用这个函数，血量减少时也不立即发生伤害信号，但是这里是可以立即发生信号触发扳机的。
			#如果随从或者英雄处于可以修改伤害的效果之下，如命令怒吼或者复活的铠甲，伤害量会发生变化
			damageActual = objtoTakeDamage.takesDamage(self, damage)
			self.tryLifesteal(damageActual)
			return objtoTakeDamage, damageActual
		else: #The target is neither on board or in hand. Either removed already or shuffled into deck.
			if target.dead and target.inDeck == False:
				return target, 0
			elif target.inDeck:
				return target, 0 #Minions in deck won't receive any damage and effect following it.
				
	#The targets can be [], [subject], [subject1, subject2, ...]		
	#For now, AOE will only affect targets that are on board. No need to check if the target is dead, in hand or in deck.
	#当场上有血量为2的奥金尼和因为欧米茄灵能者获得的法术吸血时，神圣新星杀死奥金尼仍然会保留治疗转伤害的效果。
	#有的扳机随从默认随从需要在非濒死情况下才能触发扳机，如北郡牧师。
	def dealsAOE(self, targets, damages):
		targets, damages = fixedList(targets), fixedList(damages)
		targets_damaged, damagesConnected, totalDamageDone = [], [], 0
		for target, damage in zip(targets, damages):
			#Handle Immune, Shellfighter and Ramshield here.
			objtoTakeDamage = self.Game.DmgHandler.damageTransfer(target)
			#Handle the Divine Shield and Commanding Shout here.
			damageActual = objtoTakeDamage.takesDamage(self, damage, sendDamageSignal=False)
			if damageActual > 0:
				targets_damaged.append(objtoTakeDamage)
				damagesConnected.append(damageActual)
				totalDamageDone += damageActual
		#AOE首先计算血量变化，之后才发出伤害信号。
		for target, damageActual in zip(targets_damaged, damagesConnected):
			self.Game.sendSignal(target.type+"TakesDamage", self.ID, self, target, damageActual, "")
			self.Game.sendSignal(target.type+"TookDamage", self.ID, self, target, damageActual, "")
		self.tryLifesteal(totalDamageDone)
		return targets_damaged, damagesConnected, totalDamageDone
		
	def restoresAOE(self, targets, heals):
		targets_Heal, heals = fixedList(targets), fixedList(heals)
		if self.Game.status[self.ID]["Heal to Damage"] > 0:
			targets_damaged, damagesConnected, totalDamageDone = self.dealsAOE(targets_Heal, heals)
			healsConnected = [-damage for damage in damagesConnected]
			return targets_damaged, healsConnected, -totalDamageDone #对于AOE回复，如果反而造成伤害，则返回数值为负数
		else:
			targets_healed, healsConnected, totalHealingDone = [], [], 0
			for target, heal in zip(targets, heals):
				healActual = target.getsHealed(self, heal, sendHealSignal=False)
				if healActual > 0:
					targets_healed.append(target)
					healsConnected.append(healActual)
					totalHealingDone += healActual
			for target, healActual in zip(targets_healed, healsConnected):
				self.Game.sendSignal(target.type+"GetsHealed", self.Game.turn, self, target, healActual, "FullyHealed")
		return targets_healed, healsConnected, totalHealingDone
		
	def restoresHealth(self, target, heal):
		if self.Game.status[self.ID]["Heal to Damage"] > 0:
			objtoTakeDamage, damageActual = self.dealsDamage(target, heal)
			return objtoTakeDamage, -damageActual
		else:
			healActual = target.getsHealed(self, heal)
			return target, healActual
			
	#Lifesteal will only calc once with Aukenai,  for a lifesteal damage spell, 
	#the damage output is first enhanced by spell damage, then the lifesteal is doubled by Kangor, then the doubled healing is converted by the Aukenai.
	#Heal is heal at this poin. The Auchenai effect has been resolved before this function
	def getsHealed(self, subject, heal, sendHealSignal=True):
		healActual = 0
		if self.inHand or self.onBoard:#If the character is dead and removed already or in deck. Nothing happens.
			if self.health == self.health_upper:
				PRINT(self.Game, "Character %s at full health already."%self.name)
			else:
				healActual = heal if self.health + heal < self.health_upper else self.health_upper - self.health
				self.health += healActual
				if sendHealSignal: #During AOE healing, the signals are delayed.
					self.Game.sendSignal(self.type+"GetsHealed", self.Game.turn, subject, self, healActual, "")
				self.Game.Counters.healthRestoredThisGame[subject.ID] += healActual
				if self.type == "Minion":
					for func in self.triggers["StatChanges"]:
						func()
		return healActual
		
	"""Handle the battle options for minions and heroes."""
	#Will only be used to find a selectable attack target
	def findBattleTargets(self):
		targets, indices, wheres, side = [], [], [], 3-self.ID
		if self.canAttack():
			if self.canAttackTarget(self.Game.heroes[side]):
				targets.append(self.Game.heroes[side])
				indices.append(side)
				wheres.append("hero")
			for i, minion in enumerate(self.Game.minionsonBoard(side)):
				if self.canAttackTarget(minion):
					targets.append(minion)
					indices.append(i)
					wheres.append("minion%d"%side)
		return targets, indices, wheres
		
	#所有打出效果的目标寻找，包括战吼，法术等
	#To be invoked by AI and Shudderwock.
	def findTargets(self, comment="", choice=0):
		targets, indices, wheres = [], [], []
		if comment == "":
			for ID in range(1, 3):
				if self.canSelect(self.Game.heroes[ID]) and self.targetCorrect(self.Game.heroes[ID], choice):
					targets.append(self.Game.heroes[ID])
					indices.append(ID)
					wheres.append("hero")
			for i, minion in enumerate(self.Game.minionsonBoard(1)):
				if self.canSelect(minion) and self.targetCorrect(minion, choice):
					targets.append(minion)
					indices.append(i)
					wheres.append("minion1")
			for i, minion in enumerate(self.Game.minionsonBoard(2)):
				if self.canSelect(minion) and self.targetCorrect(minion, choice):
					targets.append(minion)
					indices.append(i)
					wheres.append("minion2")
		else:
			for ID in range(1, 3):
				if self.targetCorrect(self.Game.heroes[ID], choice):
					targets.append(self.Game.heroes[ID])
					indices.append(ID)
					wheres.append("hero")
			for i, minion in enumerate(self.Game.minionsonBoard(1)):
				if self.targetCorrect(minion, choice):
					targets.append(minion)
					indices.append(i)
					wheres.append("minion1")
			for i, minion in enumerate(self.Game.minionsonBoard(2)):
				if self.targetCorrect(minion, choice):
					targets.append(minion)
					indices.append(i)
					wheres.append("minion2")
		if targets: return targets, indices, wheres
		else: return [None], [0], ['']
		
	#Minion has its own selfCopy() method.
	#For now, copying non-minion/weapon cards can only create copies that don't have any enchantments on it.
	#The mana of a card can be copied, though.
	def hardCopy(self, ID):
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
			#用于auras，statbyAura，keyWordbyAura和manaModifications等
			elif type(value) == list or type(value) == dict or type(value) == tuple: #If the attribute is a list or dictionary, use the method defined at the start of py
				Copy.__dict__[key] = copyListDictTuple(value, Copy)
			else: #The attribute is a self-defined class. They will all have selfCopy methods
				#A minion can't refernece another minion. The attributes here must be like triggers/deathrattles	
				Copy.__dict__[key] = value.selfCopy(Copy)
		Copy.ID = ID
		return Copy
		
	#给非随从牌用的，目前也没有复制场上武器的牌
	def selfCopy(self, ID):
		Copy = self.hardCopy(ID)
		Copy.identity = [np.random.rand(), np.random.rand(), np.random.rand()]
		#复制一张牌的费用修改情况,移除来自光环影响的费用效果
		size = len(Copy.manaModifications)
		for i in range(size):
			if Copy.manaModifications[size-1-i].source:
				Copy.manaModifications.pop(size-1-i)
		return Copy
		
	def assistCreateCopy(self, Copy):
		pass
		
		
		
class Permanent(Card):
	Class, name = "Neutral", "Vanilla"
	description = ""
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		
	def blank_init(self, Game, ID):
		self.Game, self.ID = Game, ID
		self.Class = type(self).Class
		self.name = type(self).name
		self.description = type(self).description
		self.type = "Permanent"
		self.race = ""
		
		self.onBoard, self.inHand, self.inDeck = False, False, False
		self.dead = False
		self.sequence, self.position = -1, -2
		self.keyWords = {"Taunt": 0, "Stealth": 0, 
						"Divine Shield": 0, "Spell Damage": 0,
						"Lifesteal": 0, "Poisonous": 0,
						"Windfury": 0, "Mega Windfury": 0,
						"Charge": 0, "Rush": 0,
						"Echo": 0
						}
		self.marks = {"Sweep": 0,
						"Evasive": 0, "Enemy Evasive": 0,
						"Can't Attack": 0, "Can't Attack Hero": 0,
						"Heal x2": 0, #Crystalsmith Kangor
						"Spell Heal&Dmg x2": 0, "Power Heal&Dmg x2": 0, #Prophet Velen, Clockwork Automation
						}
		self.status = {"Immune": 0,	"Frozen": 0, "Temp Stealth": 0, "Borrowed": 0
						}
		self.auras = {}
		self.triggersonBoard, self.triggersinHand, self.triggersinDeck = [], [], []
		
	def appears(self):
		PRINT(self.Game, "Permanent %s appears on board."%self.name)
		self.onBoard, self.inHand, self.inDeck = True, False, False
		self.dead = False
		#目前没有Permanent有光环
		for value in self.auras.values():
			PRINT(self.Game, "Now starting %s's Aura {}".format(value))
			value.auraAppears()
		#随从入场时将注册其场上扳机。
		for trigger in self.triggersonBoard:
			trigger.connect() #把(obj, signal)放入Game.triggersonBoard中
			
	#Permanent本身是没有死亡扳机的，所以这个keepDeathrattlesRegistered无论真假都无影响
	def disappears(self, keepDeathrattlesRegistered=False):
		self.onBoard, self.inHand, self.inDeck = False, False, False
		self.dead = False
		#Only the auras and disappearResponse will be invoked when the minion switches side.
		for value in self.auras.values():
			value.auraDisappears()
		#随从离场时清除其携带的普通场上扳机，但是此时不考虑亡语扳机
		for trigger in self.triggersonBoard:
			trigger.disconnect()
			
	def turnStarts(self, ID):
		pass
		
	def turnEnds(self, ID):
		pass
		
	def canAttack(self):
		return False
		
	def takesDamage(self, subject, damage, sendDamageSignal=True):
		return 0
		
	def STATUSPRINT(self):
		PRINT(self.Game, "Game is {}.".format(self.Game))
		PRINT(self.Game, "Permanent: %s.\tDescription: %s"%(self.name, self.description))
		if self.triggersonBoard != []:
			PRINT(self.Game, "\tPermanent's triggersonBoard")
			for trigger in self.triggersonBoard:
				PRINT(self.Game, "\t{}".format(type(trigger)))
		if self.auras != {}:
			PRINT(self.Game, "\tPermanent's aura:")
			for key, value in self.auras.items():
				PRINT(self.Game, "{}: {}".format(key, value))
		if hasattr(self, "progress"):
			PRINT(self.Game, "\tPermanent's progress is currently: %d"%self.progress)
			
	def createCopy(self, game):
		if self in game.copiedObjs: return game.copiedObjs[self]
		else:
			Copy = type(self)(game, self.ID)
			game.copiedObjs[self] = Copy
			Copy.onBoard, Copy.inHand, Copy.inDeck, Copy.dead = self.onBoard, self.inHand, self.inDeck, self.dead
			Copy.sequence, Copy.position = self.sequence, self.position
			Copy.triggersonBoard = [trig.createCopy(game) for trig in self.triggersonBoard]
			self.assistCreateCopy(Copy)
			return Copy
			
			
class Minion(Card):
	Class, race, name = "Neutral", "", "Vanilla"
	mana, attack, health = 2, 2, 2
	index = "Vanilla-Neutral-2-2-2-Minion-None-Vanilla-Uncollectible"
	requireTarget, keyWord, description = False, "", ""
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		
	def blank_init(self, Game, ID):
		self.Game, self.ID = Game, ID
		self.Class, self.name = type(self).Class, type(self).name
		self.type, self.race = "Minion", type(self).race
		#卡牌的费用和对于费用修改的效果列表在此处定义
		self.mana, self.manaModifications = type(self).mana, []
		self.attack, self.attack_0 = type(self).attack, type(self).attack
		self.health_0, self.health, self.health_upper = type(self).health, type(self).health, type(self).health
		self.tempAttackChanges = [] #list of tempAttChange, expiration timepoint
		#The stat of a minion are classified as:
			#self.attack_0; self.attack_Enchant; self.attack(affected by buffAura and tempChange)
			#self.attack_0; self.health_max; self.health, self.health_upper.
		self.attack_Enchant, self.health_max = self.attack, self.health
		self.statbyAura = [0, 0, []] #激怒的攻击力变化直接被记录在第一个元素中，不涉及buffAura_Receiver, The list contains all the Aura Objs put on this minion.
		self.keyWordbyAura = {"Charge":0, "Rush":0, "Mega Windfury":0,
										"Auras":[]}
		self.description = type(self).description
		#当一个实例被创建的时候，其needTarget被强行更改为returnTrue或者是returnFalse，不论定义中如何修改needTarget(self, choice=0)这个函数，都会被绕过。需要直接对returnTrue()函数进行修改。
		self.needTarget = self.returnTrue if type(self).requireTarget else self.returnFalse
		self.keyWords = {"Taunt": 0, "Divine Shield": 0, "Stealth": 0,
						"Lifesteal": 0,	"Spell Damage": 0, "Poisonous": 0,
						"Windfury": 0, "Mega Windfury": 0, "Charge": 0, "Rush": 0,
						"Echo": 0, "Reborn": 0,
						}
		if type(self).keyWord != "":
			for key in type(self).keyWord.split(","):
				self.keyWords[key.strip()] = 1
		#Some state of the minion represented by the marks
		self.marks = {"Sweep": 0,
						"Evasive": 0, "Enemy Evasive": 0,
						"Can't Attack": 0, "Can't Attack Hero": 0,
						"Heal x2": 0, #Crystalsmith Kangor
						"Power Heal&Dmg x2": 0, #Prophet Velen, Clockwork Automation
						"Spell Heal&Dmg x2": 0
						}
		#Temp effects that vanish at certain points.
		self.status = {"Immune": 0,	"Frozen": 0, "Temp Stealth": 0, "Borrowed": 0
						}
		#复制出一个游戏内的Copy时要重新设为初始值的attr	
			#First two are for card authenticity verification. The last is to check if the minion has ever left board.
			#Princess Talanji needs to confirm if a card started in original deck.
		self.identity = [np.random.rand(), np.random.rand(), np.random.rand()]
		self.dead = False
		self.effectViable, self.evanescent = False, False
		self.newonthisSide, self.firstTimeonBoard = True, True #firstTimeonBoard用于防止随从在休眠状态苏醒时再次休眠，一般用不上
		self.onBoard, self.inHand, self.inDeck = False, False, False
		self.activated = False	#This mark is for minion state change, such as enrage.
			#self.sequence records the number of the minion's appearance. The first minion on board has a sequence of 0
		self.sequence, self.position = -1, -2
		self.attTimes, self.attChances_base, self.attChances_extra = 0, 0, 0
		
		self.auras = {}
		self.options = [] #For Choose One minions.
		self.overload, self.chooseOne, self.magnetic = 0, 0, 0
		self.silenced = False
		
		self.triggers = {"Discarded":[], "StatChanges":[], "Drawn":[]}
		self.appearResponse, self.disappearResponse, self.silenceResponse = [], [], []
		self.deathrattles = [] #随从的亡语的触发方式与场上扳机一致，诸扳机之间与
		self.triggersonBoard, self.triggersinHand, self.triggersinDeck = [], [], []
		self.history = {"Spells Cast on This": [],
						"Magnetic Upgrades": {"AttackGain": 0, "HealthGain": 0,
												"Keywords":{}, "Marks":{},
												"Deathrattles":[], "Triggers":[]
												}
						}
						
	def applicable(self, target):
		return target != self
		
	"""Handle the triggersonBoard/inHand/inDeck of minions based on its move"""
	def appears(self):
		PRINT(self.Game, "%s appears on board."%self.name)
		self.newonthisSide = True
		self.onBoard, self.inHand, self.inDeck = True, False, False
		self.dead = False
		self.mana = type(self).mana #Restore the minion's mana to original value.
		self.decideAttChances_base() #Decide base att chances, given Windfury and Mega Windfury
		for value in self.auras.values():
			PRINT(self.Game, "Now starting minion {}'s Aura {}".format(self.name, value))
			value.auraAppears()
		#随从入场时将注册其场上扳机和亡语扳机
		for trigger in self.triggersonBoard + self.deathrattles:
			trigger.connect() #把(obj, signal)放入Game.triggersonBoard中
		#Mainly mana aura minions, e.g. Sorcerer's Apprentice.
		for func in self.appearResponse:
			func()
		#The buffAuras/hasAuras will react to this signal.
		self.Game.sendSignal("MinionAppears", self.ID, self, None, 0, "")
		for func in self.triggers["StatChanges"]: #For Lightspawn and Paragon of Light
			func()
			
	def disappears(self, keepDeathrattlesRegistered=True): #The minion is about to leave board.
		self.onBoard, self.inHand, self.inDeck = False, False, False
		#Only the auras and disappearResponse will be invoked when the minion switches side.
		for value in self.auras.values():
			value.auraDisappears()
		#随从离场时清除其携带的普通场上扳机，但是此时不考虑亡语扳机
		for trigger in self.triggersonBoard:
			trigger.disconnect()
		#随从因离场方式不同，对于亡语扳机的注册是否保留也有不同
			#死亡时触发的区域移动扳机导致的返回手牌或者牌库--保留其他死亡扳机的注册
			#存活状态下因为亡语触发效果而触发的区域移动扳机--保留其他死亡扳机
			#存活状态下因为闷棍等效果导致的返回手牌--注销全部死亡扳机
			#存活状态下因为控制权变更，会取消全部死亡扳机的注册，在随从移动到另一侧的时候重新注册死亡扳机
		#总之，区域移动扳机的触发不会取消其他注册了的死亡扳机,这些死亡扳机会在它们触发之后移除。
		#如果那些死亡扳机是因为其他效果而触发（非死亡），除非随从在扳机触发后已经离场（返回手牌或者牌库），否则可以保留
		if keepDeathrattlesRegistered == False:
			for trigger in self.deathrattles:
				trigger.disconnect()
		#如果随从有离场时需要触发的函数，在此处理
		for func in self.disappearResponse:
			func()
		#Let buffAura_Receivers remove themselves
		while self.statbyAura[2] != []:
			self.statbyAura[2][0].effectClear()
		#Let hasAura_Receivers remove themselves
		while self.keyWordbyAura["Auras"] != []:
			self.keyWordbyAura["Auras"][0].effectClear()
		self.activated = False
		self.Game.sendSignal("MinionDisappears", self.ID, None, self, 0, "")
		
	"""Attack chances handle"""
	#The game will directly invoke the turnStarts/turnEnds methods.
	def turnStarts(self, ID):
		size = len(self.tempAttackChanges) #Remove the temp attack changes.
		for i in range(size):
			PRINT(self.Game, "Temp Attack change: {}".format(self.tempAttackChanges[size-1-i]))
			#self.tempAttackChanges[size-1-i]是一个tuple(tempAttackChange, timepoint)
			if self.tempAttackChanges[size-1-i][1] == "StartofTurn 1" and self.Game.turn == 1:
				self.statChange(-self.tempAttackChanges[size-1-i][0], 0)
				self.tempAttackChanges.pop(size-1-i)
			if self.tempAttackChanges[size-1-i][1] == "StartofTurn 2" and self.Game.turn == 2:
				self.statChange(-self.tempAttackChanges[size-1-i][0], 0)
				self.tempAttackChanges.pop(size-1-i)
		if ID == self.ID:
			if self.onBoard: #Only minions onBoard will lose the temp Stealth
				self.status["Temp Stealth"] = 0
			self.newonthisSide = False
			self.attTimes, self.attChances_extra = 0, 0
			self.decideAttChances_base()
			
	#Violet teacher is frozen in hand. When played right after being frozen or a turn after that, it can't defrost.
	#The minion is still frozen when played. And since it's not actionable, it won't defrost at the end of turn either.
	#随从不能因为有多次攻击机会而自行解冻。只能等回合结束。
	def turnEnds(self, ID):
		#直到回合结束的对攻击力改变效果不论是否是该随从的当前回合，都会消失
		size = len(self.tempAttackChanges)
		for i in range(size):
			if self.tempAttackChanges[size-1-i][1] == "EndofTurn":
				self.statChange(-self.tempAttackChanges[size-1-i][0], 0)
				self.tempAttackChanges.pop(size-1-i)
		if ID == self.ID:
			self.status["Immune"] = 0
			#The minion can only thaw itself at the end of its turn. Not during or outside its turn
			if self.onBoard and self.status["Frozen"] > 0: #The minion can't defrost in hand.
				if self.actionable() and self.attChances_base + self.attChances_extra  > self.attTimes:
					self.status["Frozen"] = 0
					
			self.newonthisSide = False
			self.attTimes, self.attChances_extra = 0, 0
			
	def STATUSPRINT(self):
		PRINT(self.Game, "Game is {}.".format(self.Game))
		PRINT(self.Game, "Minion: %s. ID: %d Race: %s\nDescription: %s"%(self.name, self.ID, self.race, self.description))
		if self.manaModifications != []:
			PRINT(self.Game, "\tCarries mana modification:")
			for manaMod in self.manaModifications:
				if manaMod.changeby != 0:
					PRINT(self.Game, "\t\tChanged by %d"%manaMod.changeby)
				else:
					PRINT(self.Game, "\t\tChanged to %d"%manaMod.changeto)
		PRINT(self.Game, "\tAttacked times: %d. Total attack chances left: %d"%(self.attTimes, self.attChances_extra+self.attChances_base-self.attTimes))
		keyWords = []
		for key, value in self.keyWords.items():
			if value > 0:
				keyWords.append(key)
		if keyWords != []:
			PRINT(self.Game, "\tMinion has keyword:")
			for key in keyWords:
				PRINT(self.Game, "\t\t%s %d"%(key, self.keyWords[key]))
		statusList = []
		for key, value in self.status.items():
			if value > 0:
				statusList.append(key)
		if statusList != []:
			PRINT(self.Game, "\tMinion status: {}".format(statusList))
		if self.triggersonBoard != []:
			PRINT(self.Game, "\tMinion's triggersonBoard")
			for trigger in self.triggersonBoard:
				PRINT(self.Game, "\t{}".format(type(trigger)))
		if self.triggersinHand != []:
			PRINT(self.Game, "\tMinion's triggersinHand")
			for trigger in self.triggersinHand:
				PRINT(self.Game, "\t{}".format(type(trigger)))
		if self.triggersinDeck != []:
			PRINT(self.Game, "\tMinion's triggersinDeck")
			for trigger in self.triggersinDeck:
				PRINT(self.Game, "\t{}".format(type(trigger)))
		if self.auras != {}:
			PRINT(self.Game, "Minion's aura")
			for key, value in self.auras.items():
				PRINT(self.Game, "{}".format(value))
		if self.statbyAura[2] != [] or self.keyWordbyAura["Auras"] != []:
			PRINT(self.Game, "\tEffects of auras on minion")
			PRINT(self.Game, "\t{}".format(self.statbyAura))
			PRINT(self.Game, "\t{}".format(self.keyWordbyAura))
		if self.deathrattles != []:
			PRINT(self.Game, "\tMinion's Deathrattles:")
			for trigger in self.deathrattles:
				PRINT(self.Game, "\t{}".format(type(trigger)))
		if hasattr(self, "progress"):
			PRINT(self.Game, "\tMinion's progress is currently: %d"%self.progress)
			
	#判定随从是否处于刚在我方场上登场，以及暂时控制、冲锋、突袭等。
	def actionable(self):
		#不考虑冻结、零攻和自身有不能攻击的debuff的情况。
		if self.ID == self.Game.turn:
			#如果随从是刚到我方场上，则需要分析是否是暂时控制或者是有冲锋或者突袭。
			if self.newonthisSide:
				if self.status["Borrowed"] > 0 or self.keyWords["Charge"] > 0 or self.keyWords["Rush"] > 0:
					return True
			else: #随从已经在我方场上存在一个回合。则肯定可以行动。
				return True
		return False
		
	def decideAttChances_base(self):
		if self.keyWords["Mega Windfury"] > 0:
			self.attChances_base = 4
		elif self.keyWords["Windfury"] > 0:
			self.attChances_base = 2
		else:
			self.attChances_base = 1
			
	def getsFrozen(self):
		self.status["Frozen"] += 1
		PRINT(self.Game, "%s gets Frozen."%self.name)
		self.Game.sendSignal("MinionGetsFrozen", self.Game.turn, None, self, 0, "")
		
	#对于暂时因为某种aura而获得关键字的情况，直接在keyWordbyAura里面添加对应的关键字，但是不注册aura_Receiver
	def getsKeyword(self, keyWord):
		if self.inDeck == False: # and keyWord in self.keyWords.keys()
			self.keyWords[keyWord] += 1
			if self.onBoard:
				self.decideAttChances_base()
				if keyWord == "Charge":
					self.Game.sendSignal("MinionChargeKeywordChange", self.Game.turn, self, None, 0, "")
				self.STATUSPRINT()
				
	#当随从失去关键字的时候不可能有解冻情况发生。
	def losesKeyword(self, keyWord):
		if self.onBoard or self.inHand:
			if keyWord == "Stealth":
				self.keyWords["Stealth"] = 0
			elif keyWord == "Divine Shield":
				self.keyWords["Divine Shield"] = 0
				self.Game.sendSignal("MinionLosesDivineShield", self.Game.turn, None, self, 0, "")
			else:
				if self.keyWords[keyWord] > 0:
					self.keyWords[keyWord] -= 1
			if self.onBoard:
				self.decideAttChances_base()
				if keyWord == "Charge":
					self.Game.sendSignal("MinionChargeKeywordChange", self.Game.turn, self, None, 0, "")
				self.STATUSPRINT()
				
	def afterSwitchSide(self, activity):
		self.newonthisSide = True
		self.decideAttChances_base()
		if activity == "Borrow": self.status["Borrowed"] = 1
		else: #activity == "Permanent" or "Return"
			self.status["Borrowed"] = 0
		self.STATUSPRINT()
		
	#Whether the minion can select the attack target or not.
	def canAttack(self):
		if self.actionable() == False or self.attack < 1 or self.status["Frozen"] > 0:
			return False
		#THE CHARGE/RUSH MINIONS WILL GAIN ATTACKCHANCES WHEN THEY APPEAR
		if self.attChances_base + self.attChances_extra <= self.attTimes:
			return False
		if self.marks["Can't Attack"] > 0:
			return False
		return True
		
	def canAttackTarget(self, target):
		if self.canAttack() == False:
			return False
		if not target.selectablebyBattle(self):
			PRINT(self.Game, "%s is not selectable by attack."%target.name)
			return False
		#在actionable为True且目标可选的情况下只用一种情况下随从不能攻击一个角色： 突袭不能攻击英雄。
		#刚登场回合，如果不是有冲锋或者是被暂时控制，则一个随从不能攻击对方英雄。
		if self.newonthisSide and self.status["Borrowed"] < 1 and self.keyWords["Charge"] < 1 and target.type == "Hero":
			PRINT(self.Game, "%s has Rush but the target is not minion."%self.name)
			return False
			
		if self.marks["Can't Attack Hero"] > 0 and target.type == "Hero":
			PRINT(self.Game, "The minion is not allowed to attack hero")
			return False
			
		return True
		
	"""Healing, damage, takeDamage, AOE, lifesteal and dealing damage response"""
	#Stealth Dreadscale actually stays in stealth.
	def takesDamage(self, subject, damage, sendDamageSignal=True):
		damageTaken = 0
		if damage > 0 and self.status["Immune"] <= 0: #随从首先结算免疫和圣盾对于伤害的作用，然后进行预检测判定
			if self.keyWords["Divine Shield"] > 0:
				self.losesKeyword("Divine Shield")
			else:
				#伤害量预检测。如果随从有圣盾则伤害预检测实际上是没有意义的。
				damageHolder = [damage] #这个列表用于盛装伤害数值，会经由伤害扳机判定
				self.Game.sendSignal("MinionAbouttoTakeDamage", self.ID, subject, self, damageHolder, "")
				damage = damageHolder[0]
				damageTaken = damage
				self.health -= damage
				#经过检测，被伏击者返回手牌中的紫罗兰老师不会因为毒药贩子加精灵弓箭手而直接丢弃。会减1血，并在打出时复原。
				if subject.keyWords["Poisonous"] > 0 and self.onBoard:
					self.dead = True
				#在同时涉及多个角色的伤害处理中，受到的伤害暂不发送信号而之后统一进行扳机触发。
				if sendDamageSignal:
					self.Game.sendSignal("MinionTakesDamage", self.Game.turn, subject, self, damage, "")
					self.Game.sendSignal("MinionTookDamage", self.Game.turn, subject, self, damage, "")
				if subject.type == "Power":
					self.Game.Counters.damageDealtbyHeroPower[subject.ID] += damage
				#随从的激怒，根据血量和攻击的状态改变都在这里触发。
				for func in self.triggers["StatChanges"]:
					func()
					
		return damageTaken
		
	def deathResolution(self, attackbeforeDeath, triggersAllowed_WhenDies, triggersAllowed_AfterDied):
		self.Game.sendSignal("MinionDies", self.Game.turn, None, self, attackbeforeDeath, "", 0, triggersAllowed_WhenDies)
		#随从的亡语也需要扳机化，因为亡语和“每当你的一个xx随从死亡”的扳机的触发顺序也由其登场顺序决定
		#如果一个随从有多个亡语（后来获得的，那么土狼会在两个亡语结算之间触发。所以说这些亡语是严格意义上的扳机）
		#随从入场时注册亡语扳机，除非注明了是要结算死亡的情况下，disappears()的时候不会直接取消这些扳机，而是等到deathResolution的时候触发这些扳机
		#如果是提前离场，如改变控制权或者是返回手牌，则需要取消这些扳机
		#扳机应该注册为场上扳机，这个扳机应该写一个特殊的类，从而使其可以两次触发，同时这个类必须可存储一个attribute,复制效果可以复制食肉魔块等战吼提供的信息
		#区域移动类扳机一般不能触发两次
		#触发扳机如果随从已经不在场上，则说明它区域移动然后进入了牌库或者手牌。同类的区域移动扳机不会触发。
		#区域移动的死亡扳机大多是伪区域移动，实际上是将原实体移除之后将一个复制置入相应区域。可以通过魔网操纵者来验证。只有莫里甘博士和阿努巴拉克的亡语是真的区域移动
		#鼬鼠挖掘工的洗入对方牌库扳机十分特别，在此不予考虑，直接视为将自己移除，然后给对方牌库里洗入一个复制
		#The minion resets its own status. But it will record its current location.
		#If returned to hand/deck already due to deathrattle, the inHand/inDeck will be kept
		#假设随从只有在场上结算亡语完毕之后才会进行初始化，而如果扳机已经提前将随从返回手牌或者牌库，则这些随从不会
		#移除随从注册了的亡语扳机
		for trigger in self.deathrattles:
			trigger.disconnect()
		self.Game.sendSignal("MinionDied", self.Game.turn, None, self, 0, "", 0, triggersAllowed_AfterDied)
		#MinionDeathResolutionFinished
		
	def magnetCombine(self, target):
	#暂时假设磁力随从如果死亡则不触发磁力。
	#先将随从从场上或者手牌中移除。
		if self.onBoard:
			#磁力随从因为磁力触发离场时会注销其已经注册的死亡扳机，最终会将这些死亡扳机赋予磁力目标
			self.disappears(keepDeathrattlesRegistered=False)
			self.Game.removeMinionorWeapon(self)
		else: #The Magnetic minion is inHand
			self.Game.Hand_Deck.extractfromHand(self)
			
		#在打出磁力随从时，需要得知其原有的关键字、身材和扳机等，需要进行复制，然后录入随从的磁力升级历史
		Copy = self.selfCopy(self.ID) #Find the original keywords the minion has
		attack_orig, health_orig = Copy.attack_Enchant, Copy.health
		keyWords_orig, marks_orig = {}, {}
		for key, value in Copy.keyWords.items():
			if value > 0:
				keyWords_orig[key] = value
		#暂时假设磁力随从不会保留状态，如临时潜行和冰冻
		for key, value in Copy.marks.items():
			if value > 0:
				marks_orig[key] = value
		#将随从携带的扳机也记录,磁力随从是没有手牌扳机和场上扳机的
		triggers_orig, deathrattles_orig = [], []
		for trigger in Copy.triggersonBoard:
			if trigger.temp == False: #临时扳机不会被记录和赋予，如腐蚀术
				triggers_orig.append(type(trigger))
		for trigger in Copy.deathrattles:
			deathrattles_orig.append(type(trigger))
		#磁力随从没有triggers[]的方法，如激怒等
		#将关键字赋予随从
		for key, value in keyWords_orig.items():
			for i in range(value):
				target.getsKeyword(key)
				if key in target.history["Magnetic Upgrades"]["Keywords"].keys():
					target.history["Magnetic Upgrades"]["Keywords"][key] += value
				else: #如果这个关键字是之前没有的，则在dict里面添加这个key
					target.history["Magnetic Upgrades"]["Keywords"][key] = value
		#将类关键字赋予随从
		for key, value in marks_orig.items():
			target.marks[key] += value
			if key in target.history["Magnetic Upgrades"]["Marks"].keys():
				target.history["Magnetic Upgrades"]["Marks"][key] += value
			else:
				target.history["Magnetic Upgrades"]["Marks"][key] = value
		#将扳机赋予随从，同时记录在目标随从的"Magnetic Upgrades"中
		for trigger_Class in deathrattles_orig:
			trigger = trigger_Class(target)
			target.deathrattles.append(trigger)
			trigger.connect()
			target.history["Magnetic Upgrades"]["Deathrattles"].append(trigger_Class)
		#将亡语赋予随从，同时记录在"Magnetic Upgrades"里面
		for trigger_Class in triggers_orig:
			trigger = trigger_Class(target)
			target.triggersonBoard.append(trigger)
			trigger.connect()
			target.history["Magnetic Upgrades"]["Triggers"].append(trigger_Class)
		#最后进行身材的改变，并在这里调用目标随从的StatChanges方法
		target.buffDebuff(attack_orig, health_orig)
		target.history["Magnetic Upgrades"]["AttackGain"] += attack_orig
		target.history["Magnetic Upgrades"]["HealthGain"] += health_orig
		self.Game.minionPlayed = None
		
	#Specifically for battlecry resolution. Doesn't care if the target is in Stealth.
	def targetCorrect(self, target, choice=0):
		if target.type != "Minion" and target.type != "Hero":
			PRINT(self.Game, "Target is not minion or hero.")
			return False
		if target.onBoard == False:
			PRINT(self.Game, "Target is not on board.")
			return False
		if target == self:
			PRINT(self.Game, "Minion can't select self.")
			return False
		return True
		
	#Minions that initiates discover or transforms self will be different.
	#For minion that transform before arriving on board, there's no need in setting its onBoard to be True.
	#By the time this triggers, death resolution caused by Illidan/Juggler has been finished. 
	#If Brann Bronzebeard/ Mayor Noggenfogger has been killed at this point, they won't further affect the battlecry.
	#posinHand在played中主要用于记录一张牌是否是从手牌中最左边或者最右边打出（恶魔猎手职业关键字）
	def played(self, target=None, choice=0, mana=0, posinHand=-2, comment=""):
		#即使该随从在手牌中的生命值为0或以下，打出时仍会重置为无伤状态。
		self.statReset(self.attack_Enchant, self.health_max)
		#此时，随从可以开始建立光环，建立侦听，同时接受其他光环。例如： 打出暴风城勇士之后，光环在Illidan的召唤之前给随从加buff，同时之后打出的随从也是先接受光环再触发Illidan。
		self.appears()
	#使用阶段
		#使用时步骤,触发“每当你使用一张xx牌”的扳机,如伊利丹，任务达人，无羁元素和魔能机甲等
			#触发信号依次得到主玩家的场上，手牌和牌库的侦听器的响应，之后是副玩家的侦听器响应。
			#伊利丹可以在此时插入召唤和飞刀的结算，之后在战吼结算开始前进行死亡的判定，同时subject和target的位置情况会影响战吼结果。
		self.Game.sendSignal("MinionPlayed", self.ID, self, target, mana, "", choice)
		#召唤时步骤，触发“每当你召唤一个xx随从”的扳机.如鱼人招潮者等。
		self.Game.sendSignal("MinionSummoned", self.ID, self, target, mana, "")
		#过载结算
		if self.overload > 0:
			PRINT(self.Game, "%s is played and Overloads %d mana crystals."%(self.name, self.overload))
			self.Game.Manas.overloadMana(self.overload, self.ID)
			
		magneticTarget = None
		if self.magnetic > 0:
			if self.onBoard:
				neighbors, dist = self.Game.adjacentMinions2(self)
				if dist == 1 and "Mech" in neighbors[1].race:
					magneticTarget = neighbors[1]
				elif dist == 2 and "Mech" in neighbors[0].race:
					magneticTarget = neighbors[0]
		#使用阶段结束，开始死亡结算。视随从的存活情况决定战吼的触发情况，此时暂不处理胜负问题。
		self.Game.gathertheDead() #At this point, the minion might be removed/controlled by Illidan/Juggler combo.		
	#结算阶段
		if self.magnetic > 0:
			#磁力相当于伪指向性战吼，一旦指定目标之后，不会被其他扳机改变
			#磁力随从需要目标和自己都属于同一方,且磁力目标在场时才能触发。
			if magneticTarget and magneticTarget.onBoard and self.ID == magneticTarget.ID:
				#磁力结算会让随从离场，不会触发后续的随从召唤后，打出后的扳机
				self.magnetCombine(magneticTarget)
				#磁力随从没有战吼等入场特效，因而磁力结算不会引发死亡，不必进行死亡结算
		else: #无磁力的随从
			#市长会在战吼触发前检测目标，指向性战吼会被随机取向。一旦这个随机过程完成，之后的第二次战吼会重复对此目标施放。
			#如果场上有随从可供战吼选择，但是因为免疫和潜行导致打出随从时没有目标，则不会触发随机选择，因为本来就没有目标。
			#在战吼开始检测之前，如果铜须已经死亡，则其并不会让战吼触发两次。也就是扳机的机制。
			#同理，如果此时市长已经死亡，则其让选择随机化的扳机也已经离场，所以不会触发随机目标。
			if target:
				targetHolder = [target]
				self.Game.sendSignal("BattlecryTargetDecision", self.ID, self, targetHolder, 0, "", choice)
				if target != targetHolder[0] and self.Game.withAnimation and self.Game.GUI:
					target = targetHolder[0]
					self.Game.GUI.target = target
					self.Game.GUI.wait(0.4)
				else: target = targetHolder[0]
			#市长不会让发现和抉择选项的选择随机化。
			#不管target是否还在场上，此时只要市长还在，就要重新在场上寻找合法目标。如果找不到，就不能触发战吼的指向性部分，以及其产生的后续操作。
			#随机条件下，如果所有合法目标均已经消失，则return None. 由随从的战吼决定是否继续生效。
			
			#在随从战吼/连击开始触发前，检测是否有战吼/连击翻倍的情况。如果有且战吼可以进行，则强行执行战吼至两次循环结束。无论那个随从是死亡，在手牌中还是牌库
			num = 1
			if "~Battlecry" in self.index and self.Game.status[self.ID]["Battlecry x2"] + self.Game.status[self.ID]["Shark Battlecry x2"] > 0:
				num = 2
			if "~Combo" in self.index and self.Game.status[self.ID]["Shark Battlecry x2"] > 0:
				num = 2
				#不同的随从会根据目标和自己的位置和状态来决定effectwhenPlayed()产生体积效果。
				#可以变形的随从，如无面操纵者，会有自己的played（） 方法。 大王同理。
				#战吼随从自己不会进入牌库，因为目前没有亡语等效果可以把随从返回牌库。
				#发现随从如果在战吼触发前被对方控制，则不会引起发现，因为炉石没有对方回合外进行操作的可能。
				#结算战吼，连击，抉择
			for i in range(num):
				target = self.whenEffective(target, "", choice, posinHand)
				
			#结算阶段结束，处理死亡情况，不处理胜负问题。
			self.Game.gathertheDead()
		return target
		
	def countHealDouble(self):
		num = 0
		for minion in self.Game.minionsonBoard(self.ID):
			if minion.marks["Heal x2"] > 0:
				num += 1
		return num
		
	"""buffAura effect, Buff/Debuff, stat reset, copy"""
	#Generally invoked by buffAura_Receivers and buffDebuff.
	def statChange(self, attackChange, healthChange):
		self.attack += attackChange
		if healthChange >= 0:
			self.health += healthChange
			self.health_upper += healthChange
		else: #When the buffAura is gone.
			self.health_upper += healthChange
			self.health_upper = max(1, self.health_upper)
			if self.health > self.health_upper:
				self.health = self.health_upper
		for func in self.triggers["StatChanges"]:
			func()
			
	#attChangeDisappearTime = "' or "EndofTurn" or "StartofTurn 1" or "StartofTurn 2"
	def buffDebuff(self, attackGain, healthGain, attChangeDisappearTime=''):
		if self.inDeck == False and self.dead == False: #只有随从在场上或者手牌中的时候可以接受buff。
			self.health_max += healthGain #By default, this healthGain has to be non-negative.
			if attChangeDisappearTime == "": #在场上和手牌中都可以接受永久buff
				self.attack_Enchant += attackGain
				self.statChange(attackGain, healthGain)
			else: #Minions can receive temp attack changes, too. And those will also vanish at the corresponding time point.
				self.tempAttackChanges.append((attackGain, attChangeDisappearTime))
				self.statChange(attackGain, healthGain)
				PRINT(self.Game, "{}".format(self.tempAttackChanges))
				
	#Not all params can be False.
	def statReset(self, newAttack=False, newHealth=False):
		if self.inDeck == False and self.dead == False:
			CurrentBuffAura_Receivers = fixedList(self.statbyAura[2])
			#将随从上的全部buffAura清除，因为部分光环的适用条件可能会因为随从被沉默而变化，如战歌指挥官
			for buffAura_Receiver in CurrentBuffAura_Receivers:
				buffAura_Receiver.effectClear()
				
			if newAttack != False: #The minion's health is reset.
				self.attack, self.attack_Enchant = newAttack, newAttack
				self.tempAttackChanges = [] #Clear the temp attack changes on the minion.
			if newHealth != False:
				self.health, self.health_upper, self.health_max = newHealth, newHealth, newHealth
				
			#清除全部buffAura并重置随从的生命值之后，让原来的buffAura_Dealer自行决定是否重新对该随从施加光环。
			for buffAura_Receiver in CurrentBuffAura_Receivers:
				buffAura_Receiver.source.applies(self)
			for func in self.triggers["StatChanges"]:
				func()
				
	#在原来的Game中创造一个Copy
	def selfCopy(self, ID, attack=False, health=False, mana=False):
		Copy = self.hardCopy(ID)
		#随从的光环和亡语复制完全由各自的selfCopy函数负责。
		for aura_Receiver in Copy.statbyAura[2]:
			aura_Receiver.effectDiscard()
		for aura_Receiver in Copy.keyWordbyAura["Auras"]:
			aura_Receiver.effectDiscard()
		Copy.activated, Copy.onBoard, Copy.inHand, Copy.inDeck = False, False, False, False
		size = len(Copy.manaModifications) #去掉牌上的因光环产生的费用改变
		for i in range(size):
			if Copy.manaModifications[size-1-i].source:
				Copy.manaModifications.pop(size-1-i)
		#在一个游戏中复制出新实体的时候需要把这些值重置
		Copy.identity = [np.random.rand(), np.random.rand(), np.random.rand()]
		Copy.dead = False
		Copy.effectViable, Copy.evanescent = False, False
		Copy.newonthisSide, Copy.firstTimeonBoard = True, True #firstTimeonBoard用于防止随从在休眠状态苏醒时再次休眠，一般用不上
		Copy.onBoard, Copy.inHand, Copy.inDeck = False, False, False
		Copy.activated = False
		Copy.sequence, Copy.position = -1, -2
		Copy.attTimes, Copy.attChances_base, Copy.attChances_extra = 0, 0, 0
		
		Copy.decideAttChances_base()
		#如果要生成一个x/x/x的复制
		if attack != False or health != False:
			Copy.statReset(attack, health)
		if mana != False:
			for manaMod in Copy.manaModifications:
				manaMod.getsRemoved()
			Copy.manaModifications = []
			ManaModification(Copy, changeby=0, changeto=mana).applies()
		return Copy
		
	#破法者因为阿努巴尔潜伏者的亡语被返回手牌，之后被沉默，但是仍然可以触发其战吼
	#在手牌中时不能接受沉默。已经用紫罗兰老师测试过了，仍然可以触发其扳机，没有沉默标记
	def getsSilenced(self):
		if self.onBoard:
			self.silenced, self.activated = True, False
			#随从如需对沉默做出响应，在此处理。然后移除被沉默，出场，离场的特殊响应
			for func in self.silenceResponse:
				func()
			self.silenceResponse, self.appearResponse, self.disappearResponse = [], [], []
			#Remove the enrage/Lightspawn effects. And discard effect.
			for key in self.triggers.keys():
				self.triggers[key] = []
			#Shut down minion's auras, if any. And clear them
			for key, value in self.auras.items():
				value.auraDisappears()
				
			self.auras = {}
			#清除所有场上扳机,亡语扳机，手牌扳机和牌库扳机。然后将这些扳机全部清除	
			for trigger in self.triggersonBoard + self.deathrattles + self.triggersinHand + self.triggersinDeck:
				trigger.disconnect()
			self.triggersonBoard, self.deathrattles, self.triggersinHand, self.triggersinDeck = [], [], [], []
			#清除随从因为关键字光环获得的关键字：冲锋，突袭，超级风怒。这些关键字是否之后恢复由光环施加者决定。
			#暂时不清除随从身上的buffAura增益，统一留到最后的statReset()中处理。
			CurrentKeywordAura_Receivers = fixedList(self.keyWordbyAura["Auras"])
			for keywordAura_Receiver in CurrentKeywordAura_Receivers:
				keywordAura_Receiver.effectClear()
			#清除随从身上的所有原有关键字。
			for key, value in self.keyWords.items():
				if value > 0:
					self.keyWords[key] = 1
					self.losesKeyword(key)
				self.keyWords[key] = 0
			#清除随从身上的所有原有状态。
			for key, value in self.status.items():
				#If Borrowed when silenced, return it to the other side.
				#The minion only remember one Borrowed state, even if repetitively moved between two sides.
				if key == "Borrowed" and value > 0:
					self.Game.minionSwitchSide(self, activity="Return")
				self.status[key] = 0
			#清除随从身上的历史记录，主要为对该随从施放的法术和机械随从的磁力叠加历史。
			for key in self.history.keys():
				self.history[key] = []
			#随从被沉默不发出沉默信号，所有接受的keywordAura就地处理。
			for keywordAura_Receiver in CurrentKeywordAura_Receivers:
				keywordAura_Receiver.source.applies(self)
			self.decideAttChances_base()
			#self.statReset() can handle statbyAura
			#沉默后的血量计算是求当前血量上限与实际血量的差，沉默后在基础血量上扣除该差值。（血量不能小于1）
			damageTaken = self.health_upper - self.health
			#在此处理随从身上存在的buffAura的效果。先是将其全部取消，然后看之前的光环是否还会继续对其产生作用。
			self.statReset(self.attack_0, self.health_0)
			self.health -= damageTaken
			self.health = max(1, self.health)
			
	def createCopy(self, game):
		if self in game.copiedObjs:
			return game.copiedObjs[self]
		else:
			Copy = type(self)(game, self.ID)
			game.copiedObjs[self] = Copy
			Copy.mana = self.mana
			Copy.manaModifications = [mod.selfCopy(Copy) for mod in self.manaModifications]
			Copy.attack, Copy.attack_0, Copy.attack_Enchant = self.attack, self.attack_0, self.attack_Enchant
			Copy.health_0, Copy.health, Copy.health_upper, Copy.health_max = self.health_0, self.health, self.health_upper, self.health_max
			Copy.tempAttackChanges = copy.deepcopy(self.tempAttackChanges)
			Copy.statbyAura = [self.statbyAura[0], self.statbyAura[1], [aura_Receiver.selfCopy(Copy) for aura_Receiver in self.statbyAura[2]]]
			for key, value in self.keyWordbyAura.items():
				if key != "Auras": Copy.keyWordbyAura[key] = value
				else: Copy.keyWordbyAura[key] = [aura_Receiver.selfCopy(Copy) for aura_Receiver in self.keyWordbyAura["Auras"]]
			Copy.keyWords = copy.deepcopy(self.keyWords)
			Copy.marks = copy.deepcopy(self.marks)
			Copy.status = copy.deepcopy(self.status)
			Copy.identity = copy.deepcopy(self.identity)
			Copy.onBoard, Copy.inHand, Copy.inDeck, Copy.dead = self.onBoard, self.inHand, self.inDeck, self.dead
			if hasattr(self, "progress"): Copy.progress = self.progress
			Copy.effectViable, Copy.evanescent, Copy.activated, Copy.silenced = self.effectViable, self.evanescent, self.activated, self.silenced
			Copy.newonthisSide, Copy.firstTimeonBoard = self.newonthisSide, self.firstTimeonBoard
			Copy.sequence, Copy.position = self.sequence, self.position
			Copy.attTimes, Copy.attChances_base, Copy.attChances_extra = self.attTimes, self.attChances_base, self.attChances_extra
			Copy.options = [option.selfCopy(Copy) for option in self.options]
			for key, value in self.triggers.items():
				Copy.triggers[key] = [getattr(Copy, func.__qualname__.split(".")[1]) for func in value]
			Copy.appearResponse = [getattr(Copy, func.__qualname__.split(".")[1]) for func in self.appearResponse]
			Copy.disappearResponse = [getattr(Copy, func.__qualname__.split(".")[1]) for func in self.disappearResponse]
			Copy.silenceResponse = [getattr(Copy, func.__qualname__.split(".")[1]) for func in self.silenceResponse]
			for key, value in self.auras.items():
				Copy.auras[key] = value.createCopy(game)
			Copy.deathrattles = [trig.createCopy(game) for trig in self.deathrattles]
			Copy.triggersonBoard = [trig.createCopy(game) for trig in self.triggersonBoard]
			Copy.triggersinHand = [trig.createCopy(game) for trig in self.triggersinHand]
			Copy.triggersinDeck = [trig.createCopy(game) for trig in self.triggersinDeck]
			Copy.history = copy.deepcopy(self.history)
			self.assistCreateCopy(Copy)
			return Copy
			
			
			
class Spell(Card):
	Class, name = "Neutral", "Test"
	requireTarget, mana = False, 2
	index = "None-1-Spell-Test"
	description = ""
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		
	def blank_init(self, Game, ID):
		self.Game, self.ID = Game, ID
		self.Class, self.name = type(self).Class, type(self).name
		self.type = "Spell"
		self.index = type(self).index
		self.mana, self.manaModifications = type(self).mana, []
		self.needTarget = self.returnTrue if type(self).requireTarget else self.returnFalse
		self.description = type(self).description
		self.overload, self.chooseOne, self.twinSpell = 0, 0, 0
		#法术也设置onBoard标签，但只是placeholder而已
		self.onBoard, self.inHand, self.inDeck = False, False, False
		self.identity = [np.random.rand(), np.random.rand(), np.random.rand()]
		#法术的triggersonBoard只是一个placeholder
		self.triggersonBoard, self.triggersinHand, self.triggersinDeck = [], [], []
		self.options = [] #For Choose One spells
		self.keyWords = {"Poisonous": 0, "Lifesteal": 0}
		self.triggers = {"Discarded": []}
		self.effectViable, self.evanescent = False, False
		
	def STATUSPRINT(self):
		PRINT(self.Game, "Game is {}.".format(self.Game))
		PRINT(self.Game, "Spell: %s. Description: %s"%(self.name, self.description))
		if self.manaModifications != []:
			PRINT(self.Game, "\tCarries mana modification:")
			for manaMod in self.manaModifications:
				if manaMod.changeby != 0:
					PRINT(self.Game, "\t\tChanged by %d"%manaMod.changeby)
				else:
					PRINT(self.Game, "\t\tChanged to %d"%manaMod.changeto)
		if self.triggersinHand != []:
			PRINT(self.Game, "Spell's triggersinHand")
			for trigger in self.triggersinHand:
				PRINT(self.Game, "\t{}".format(trigger))
		if hasattr(self, "progress"):
			PRINT(self.Game, "\tSpell's progress is currently: %d"%self.progress)
			
	"""Handle the card being selected and check the validity of selection and target."""
	def available(self):
		return not self.needTarget() or self.selectableCharacterExists()
		
	"""Handle the spell being played by player and cast by other cards."""
	#用于由其他卡牌释放法术。这个法术会受到风潮和星界密使的状态影响，同时在结算完成后移除两者的状态。
	#这个由其他卡牌释放的法术不受泽蒂摩的光环影响。
	#目标随机，也不触发目标扳机。
	def cast(self, target=None, comment=""):
		curGame = self.Game
		#由其他卡牌释放的法术结算相对玩家打出要简单，只需要结算过载，双生法术， 重复释放和使用后的扳机步骤即可。
		#因为这个法术是由其他序列产生的，所有结束时不会进行死亡处理。
		repeatTimes = 2 if curGame.status[self.ID]["Spells x2"] > 0 else 1
		#多次选择的法术，如分岔路口等会有自己专有的cast方法。
		if curGame.mode == 0:
			if curGame.guides:
				i, where, choice = curGame.guides.pop(0)
				target = curGame.find(i, where) if where else None
			else:
				if self.chooseOne < 1: choice = 0
				else: choice = "ChooseBoth" if curGame.status[self.ID]["Choose Both"] else nprandint(len(self.options))
				if target is None: #沼泽女王哈加莎的恐魔是目前唯一的指定发动的
					if self.needTarget(choice):
						targets = self.findTargets("", choice)[0]
						if targets:
							if "enemyFirst" in comment:
								enemyID, enemies = 3-self.ID, []
								enemies = [minion for minion in curGame.minionsonBoard(enemyID) if self.canSelect(minion) and self.targetCorrect(minion, choice)]
								enemyHero = curGame.heroes[enemyID]
								if self.canSelect(enemyHero) and self.targetCorrect(enemyHero): enemies.append(enemyHero)
								target = npchoice(enemies) if enemies else npchoice(targets)
							else: target = npchoice(targets)
						else: target = None
					else: target = None
				if target:
					if target.type == "Hero": i, where = target.ID, "hero"
					else: i, where = target.position, "minion%d"%target.ID
				else: i, where = 0, ''
				curGame.fixedGuides.append((i, where, choice))
		if curGame.withAnimation and curGame.GUI:
			curGame.GUI.updateCardinResolution(self)
			curGame.GUI.target = target
			curGame.GUI.wait(0.5)
		#在法术要施放两次的情况下，第二次的目标仍然是第一次时随机决定的
		for i in range(repeatTimes):
			if self.overload > 0:
				PRINT(curGame, "%s is cast and Overloads %d mana crystals."%(self.name, self.overload))
				curGame.Manas.overloadMana(self.overload, self.ID)
			if self.twinSpell > 0: #如果不是从手牌中打出，则不会把双生法术牌置入原来的位置
				PRINT(curGame, "Twinspell %s is cast and adds a another copy to player's hand"%self.name)
				curGame.Hand_Deck.addCardtoHand(self.twinSpellCopy, self.ID, "CreateUsingType")
			#指向性法术如果没有目标也可以释放，只是可能没有效果而已
			target = self.whenEffective(target, "byOthers", choice, posinHand=-2)
		#使用后步骤，但是此时的扳机只会触发星界密使和风潮的状态移除。这个信号不是“使用一张xx牌之后”的扳机。
		curGame.sendSignal("SpellBeenCast", self.ID, self, target, 0, "byOthers", choice=0)
		
	#泽蒂摩加风潮，当对泽蒂摩使用Mutate之后，Mutate会连续两次都进化3个随从
	#泽蒂摩是在法术开始结算之前打上标记,而非在连续两次之间进行判定。
	#comment = "InvokedbyAI", "Branching-i", ""
	def played(self, target=None, choice=0, mana=0, posinHand=-2, comment=""):
		#使用阶段
		#判定该法术是否会因为风潮的光环存在而释放两次。发现的子游戏中不会两次触发，直接跳过
		if "Branching" not in comment:
			repeatTimes = 2 if self.Game.status[self.ID]["Spells x2"] > 0 else 1
		#使用时步骤，触发伊利丹和紫罗兰老师等“每当你使用一张xx牌”的扳机
		self.Game.sendSignal("SpellPlayed", self.ID, self, target, mana, "", choice)
		#获得过载和双生法术牌。
		if self.overload > 0:
			PRINT(self.Game, "%s is cast and Overloads %d mana crystals."%(self.name, self.overload))
			self.Game.Manas.overloadMana(self.overload, self.ID)
		if self.twinSpell > 0:
			PRINT(self.Game, "Twinspell %s is cast and adds a another copy to player's hand"%self.name)
			self.Game.Hand_Deck.addCardtoHand(self.twinSpellCopy, self.ID, "CreateUsingType", posinHand)
			
		#使用阶段结束，进行死亡结算。不处理胜负裁定。
		self.Game.gathertheDead() #At this point, the minion might be removed/controlled by Illidan/Juggler combo.		
		#进行目标的随机选择和扰咒术的目标改向判定。
		targetHolder = [target]
		self.Game.sendSignal("SpellTargetDecision", self.ID, self, targetHolder, 0, choice)
		if target != targetHolder[0] and self.Game.withAnimation and self.Game.GUI:
			target = targetHolder[0]
			self.Game.GUI.target = target
			self.Game.GUI.wait(0.4) #If the target is changed, show 0.4 more seconds
		else: target = targetHolder[0]
		
		if target and target.ID == self.ID:
			self.Game.Counters.spellsonFriendliesThisGame[self.ID].append(self.index)
		#Zentimo's effect actually an aura. As long as it's onBoard the moment the spell starts being resolved, 
		#the effect will last even if Zentimo leaves board early.
		targetAdjacentMinions = self.Game.status[self.ID]["Spells Sweep"]
		#没有法术目标，且法术本身是点了需要目标的选项的抉择法术或者需要目标的普通法术。
		for i in range(repeatTimes):
			if i == 1: #第二次施放时照常获得过载和双生法术牌。
				if self.overload > 0:
					PRINT(self.Game, "%s is played and Overloads %d mana crystals."%(self.name, self.overload))
					self.Game.Manas.overloadMana(self.overload, self.ID)
				if self.twinSpell > 0:
					PRINT(self.Game, "Twinspell", self.name, "is cast and adds a another copy to player's hand, index pos", posinHand)
					self.Game.Hand_Deck.addCardtoHand(self.twinSpellCopy, self.ID, "CreateUsingType", posinHand)
					
			PRINT(self.Game, "The target for the spell is now {}".format(target))
			#When the target is an onBoard minion, Zentimo is still onBoard and has adjacent minions next to it.
			if target and target.type == "Minion" and target.onBoard and targetAdjacentMinions > 0 and self.Game.adjacentMinions2(target)[0] != []:
				targets = self.Game.adjacentMinions2(target)[0]
				#只对中间的目标随从返回法术释放之后的新目标。
				#用于变形等会让随从提前离场的法术。需要知道后面的再次生效目标。
				target.history["Spells Cast on This"].append(self.index)
				target = self.whenEffective(target, comment, choice, posinHand)
				PRINT(self.Game, "{} will also be cast upon minions {} adjacent to the target {} with choice {}".format(self.name, targets, target.name, choice))
				for minion in targets: #对相邻的随从也释放该法术。
					minion.history["Spells Cast on This"].append(self.index)
					self.whenEffective(minion, comment, choice, posinHand)
			else: #The target isn't minion or Zentimo can't apply to the situation. Be the target hero, minion onBoard or inDeck or None.
				#如果目标不为空而且是在场上的随从，则这个随从的历史记录中会添加此法术的index。
				if target and target.type == "Minion" and target.onBoard:
					target.history["Spells Cast on This"].append(self.index)
					
				target = self.whenEffective(target, comment, choice, posinHand)
				
		#仅触发风潮，星界密使等的光环移除扳机。“使用一张xx牌之后”的扳机不在这里触发，而是在Game的playSpell函数中结算。
		self.Game.sendSignal("SpellBeenCast", self.Game.turn, self, target, 0, "", choice)
		#使用阶段结束，进行死亡结算，暂不处理胜负裁定。
		self.Game.gathertheDead() #At this point, the minion might be removed/controlled by Illidan/Juggler combo.		
		
	#完成阶段：
		#如果法术具有回响，则将回响牌置入手牌中。因为没有牌可以让法术获得回响，所以可以直接在法术played()方法中处理echo
		if "~Echo" in self.index:
			echoCard = type(minion)(self, self.Game.turn)
			trigger = Trigger_Echo(echoCard)
			echoCard.triggersinHand.append(trigger)
			self.Game.Hand_Deck.addCardtoHand(echoCard, self.ID)
			
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		return target
		
	def afterDrawingCard(self):
		pass
	"""Handle the spell dealing damage and restoring health."""
	def countSpellDamage(self):
		num = 0
		for minion in self.Game.minions[self.ID]:
			num += minion.keyWords["Spell Damage"]
		num += self.Game.status[self.ID]["Spell Damage"]
		return num
		
	def countDamageDouble(self):
		num = 0
		for minion in self.Game.minions[self.ID]:
			if minion.marks["Spell Heal&Dmg x2"] > 0:
				num += 1
		return num
		
	def countHealDouble(self):
		num = 0
		for minion in self.Game.minions[self.ID]:
			if minion.marks["Heal x2"] > 0 or minion.marks["Spell Heal&Dmg x2"] > 0:
				num += 1
		return num
		
	def createCopy(self, game):
		if self in game.copiedObjs:
			return game.copiedObjs[self]
		else:
			Copy = type(self)(game, self.ID)
			game.copiedObjs[self] = Copy
			Copy.mana = self.mana
			Copy.manaModifications = [mod.selfCopy(Copy) for mod in self.manaModifications]
			Copy.inHand, Copy.inDeck = self.inHand, self.inDeck
			Copy.identity = copy.deepcopy(self.identity)
			Copy.triggersonBoard = [trig.createCopy(game) for trig in self.triggersonBoard]
			Copy.triggersinHand = [trig.createCopy(game) for trig in self.triggersinHand]
			Copy.triggersinDeck = [trig.createCopy(game) for trig in self.triggersinDeck]
			Copy.options = [option.selfCopy(Copy) for option in self.options]
			Copy.keyWords = copy.deepcopy(self.keyWords)
			Copy.effectViable, Copy.evanescent = self.effectViable, self.evanescent
			for key, value in self.triggers.items():
				Copy.triggers[key] = [getattr(Copy, func.__qualname__.split(".")[1]) for func in value]
			self.assistCreateCopy(Copy)
			return Copy
			
			
		
class Secret(Spell):
	Class, name = "Neutral", "Vanilla"
	requireTarget, mana = False, 1
	index = "Neutral~1~Spell~Vanilla~~Secret"
	description = ""
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		
	def blank_init(self, Game, ID):
		self.Class = type(self).Class
		self.name = type(self).name
		self.index = type(self).index
		self.mana, self.manaModifications = type(self).mana, []
		self.Game, self.ID = Game, ID
		self.needTarget = self.returnTrue if type(self).requireTarget else self.returnFalse
		self.type = "Spell"
		self.description = type(self).description
		self.overload, self.chooseOne, self.twinSpell = 0, 0, 0
		#法术也设置onBoard标签，但只是placeholder而已
		self.onBoard, self.inHand, self.inDeck = False, False, False
		self.identity = [np.random.rand(), np.random.rand()]
		self.triggersonBoard, self.triggersinHand, self.triggersinDeck = [], [], []
		self.options = [] #For Choose One spells
		self.keyWords = {"Poisonous": 0, "Lifesteal": 0}
		self.triggers = {"Discarded": []}
		self.effectViable, self.evanescent = False, False
		
	def available(self):
		if self.Game.Secrets.areaNotFull(self.ID):
			return self.Game.Secrets.sameSecretExists(self, self.ID) == False
		return False
		
	def selectionLegit(self, target, choice=0):
		return target == None
		
	def cast(self, target=None, comment="byOthers"):
		if self.Game.withAnimation and self.Game.GUI:
			self.Game.GUI.updateCardinResolution(self)
			self.Game.GUI.target = None
			self.Game.GUI.wait(0.5)
		self.whenEffective(None, "byOthers", choice=0, posinHand=-2)
		#使用后步骤，但是此时的扳机只会触发星界密使和风潮的状态移除，因为其他的使用后步骤都要求是玩家亲自打出。
		self.Game.sendSignal("SpellBeenCast", self.ID, self, None, 0, "byOthers")
		
	def played(self, target=None, choice=0, mana=0, posinHand=-2, comment=""):
		self.Game.sendSignal("SpellPlayed", self.ID, self, None, mana, "", choice)
		self.Game.gathertheDead() #At this point, the minion might be removed/controlled by Illidan/Juggler combo.		
		self.whenEffective(None, '', choice, posinHand)
		#There is no need for another round of death resolution.
		self.Game.sendSignal("SpellBeenCast", self.ID, self, None, 0, "")
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		secretcanRegister = True
		if self.Game.Secrets.areaNotFull(self.ID) and self.Game.Secrets.sameSecretExists(self, self.ID) == False:
			self.Game.Secrets.secrets[self.ID].append(self)
			for trigger in self.triggersonBoard:
				trigger.connect() #把(obj, signal)放入Game.triggersonBoard中
		else:
			secretcanRegister = False
		if secretcanRegister == False:
			PRINT(self.Game, "Secret %s cannot register due to full area or existing same kind of secret"%self.name)
		return None
		
		
		
class Quest(Spell):
	Class, name = "Neutral", "Vanilla"
	requireTarget, mana = False, 1
	index = "Neutral-1-Spell-Vanilla--Quest"
	description = ""
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		
	def blank_init(self, Game, ID):
		self.Game, self.ID = Game, ID
		self.Class, self.name = type(self).Class, type(self).name
		self.type = "Spell"
		self.index = type(self).index
		self.mana, self.manaModifications = type(self).mana, []
		self.needTarget = self.returnTrue if type(self).requireTarget else self.returnFalse
		self.description = type(self).description
		self.overload, self.chooseOne, self.twinSpell = 0, 0, 0
		#法术也设置onBoard标签，但只是placeholder而已
		self.onBoard, self.inHand, self.inDeck = False, False, False
		self.identity = [np.random.rand(), np.random.rand()]
		self.triggersonBoard, self.triggersinHand, self.triggersinDeck = [], [], []
		self.options = [] #For Choose One spells
		self.keyWords = {"Poisonous": 0, "Lifesteal": 0}
		self.triggers = {"Discarded": []}
		self.progress = 0
		self.effectViable, self.evanescent = False, False
		
	def available(self):
		if self.Game.Secrets.areaNotFull(self.ID):
			if self.description.startswith("Sidequest"):
				for quest in self.Game.Secrets.sideQuests[self.ID]:
					if quest.name == self.name: #Sidequests can coexist with other different quest and Sidequests
						return False
			else: #If the subject is a main quest. Then there can only be only main quest
				if self.Game.Secrets.mainQuests[self.ID] != []: #Sidequests can coexist with other different quest and sidequests
					return False
			return True #If the there are no same kind of quests in the way, return True
		return False
		
	def selectionLegit(self, target, choice=0):
		return target == None
		
	def cast(self, target=None, comment="byOthers"):
		if self.Game.withAnimation and self.Game.GUI:
			self.Game.GUI.updateCardinResolution(self)
			self.Game.GUI.target = None
			self.Game.GUI.wait(0.5)
		self.whenEffective(None, "byOthers", choice=0, posinHand=-2)
		#使用后步骤，但是此时的扳机只会触发星界密使和风潮的状态移除，因为其他的使用后步骤都要求是玩家亲自打出。
		self.Game.sendSignal("SpellBeenCast", self.ID, self, None, 0, "byOthers")
		
	def played(self, target=None, choice=0, mana=0, posinHand=-2, comment=""):
		self.Game.sendSignal("SpellPlayed", self.ID, self, None, mana, "", choice)
		self.Game.gathertheDead() #At this point, the minion might be removed/controlled by Illidan/Juggler combo.		
		self.whenEffective(None, '', choice, posinHand)
		#There is no need for another round of death resolution.
		self.Game.sendSignal("SpellBeenCast", self.ID, self, None, 0, "")
		self.Game.Counters.hasPlayedQuestThisGame[self.ID] = True
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		questcanRegister = True
		if self.Game.Secrets.areaNotFull(self.ID):
			if self.description.startswith("Sidequest"):
				for quest in self.Game.Secrets.sideQuests[self.ID]:
					if quest.name == self.name:
						questcanRegister = False
						break
				if questcanRegister:
					self.Game.Secrets.sideQuests[self.ID].append(self)
					for trigger in self.triggersonBoard:
						trigger.connect()
			else: #The quest is a main quest	
				if self.Game.Secrets.mainQuests[self.ID] == []:
					self.Game.Secrets.mainQuests[self.ID].append(self)
					for trigger in self.triggersonBoard:
						trigger.connect() #把(obj, signal)放入Game.triggersonBoard中
				else:
					questcanRegister = False
		else:
			questcanRegister = False
		if questcanRegister == False:
			PRINT(self.Game, "Quest %s cannot register due to full area or existing same kind of quest"%self.name)
		return None
		
		
		
class HeroPower(Card):
	mana, name, requireTarget = 2, "Test", False
	index = "Neutral-2-Hero Power-Vanilla"
	description = ""
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		
	def blank_init(self, Game, ID):
		self.Game, self.ID = Game, ID
		self.name = type(self).name
		self.type = "Power"
		self.description = type(self).description
		self.heroPowerTimes = 0
		#额外的英雄技能技能只有考达拉幼龙和要塞指挥官可以更改。
		#技能能否使用，需要根据已使用次数和基础机会和额外机会的和相比较。
		self.heroPowerChances_base, self.heroPowerChances_extra = 1, 0
		self.mana, self.manaModifications = type(self).mana, []
		self.needTarget = self.returnTrue if type(self).requireTarget else self.returnFalse
		self.chooseOne = 0
		self.onBoard = True
		self.options = [] #For Choose One
		self.keyWords = {"Lifesteal": 0,
						"Poisonous": 0 #As a placeholder
						}
		self.triggersonBoard = []
		
	def STATUSPRINT(self):
		PRINT(self.Game, "Game is {}.".format(self.Game))
		PRINT(self.Game, "Hero Power %d: %s. Description: %s"%(self.ID, self.name, self.description))
		PRINT(self.Game, "Chances_base: %d. Chances_extra %d"%(self.heroPowerChances_base, self.heroPowerChances_extra))
		if self.manaModifications != []:
			PRINT(self.Game, "\tCarries mana modification:")
			for manaMod in self.manaModifications:
				if manaMod.changeby != 0:
					PRINT(self.Game, "\t\tChanged by %d"%manaMod.changeby)
				else:
					PRINT(self.Game, "\t\tChanged to %d"%manaMod.changeto)
		
	def turnStarts(self, ID):
		if ID == self.ID:
			self.heroPowerChances_base, self.heroPowerChances_extra = 1, 0
			self.heroPowerTimes = 0
			
	def turnEnds(self, ID):
		if ID == self.ID:
			self.heroPowerChances_base, self.heroPowerChances_extra = 1, 0
			self.heroPowerTimes = 0
			
	def appears(self):
		self.heroPowerChances_base = 1
		self.heroPowerTimes = 0
		for trigger in self.triggersonBoard:
			trigger.connect()
		self.Game.sendSignal("HeroPowerAcquired", self.ID, self, None, 0, "")
		self.Game.Manas.calcMana_Powers()
		
	def disappears(self):
		for trigger in self.triggersonBoard:
			trigger.disconnect()
		for manaMod in self.manaModifications:
			manaMod.getsRemoved()
		self.manaModifications = []
		
	def replaceHeroPower(self):
		if self.Game.powers[self.ID]:
			self.Game.powers[self.ID].disappears()
			self.Game.powers[self.ID] = None
		self.Game.powers[self.ID] = self
		self.appears()
		
	def available(self): #只考虑没有抉择的技能，抉择技能需要自己定义
		if self.heroPowerTimes >= self.heroPowerChances_base + self.heroPowerChances_extra:
			return False
		if self.needTarget() and not self.findTargets("")[0][0]:
			print("Hero Power %s needs target"%self.name, self.needTarget(), self.findTargets("")[0])
			return False
		return True
		
	def targetCorrect(self, target, choice=0):
		if (target.type == "Hero" or target.type == "Minion") and target.onBoard:
			return True
		return True
		
	def use(self, target=None, choice=0):
		canUseHeroPower = False
		if self.Game.Manas.affordable(self) == False:
			PRINT(self.Game, "Not enough mana to use the Hero Power %s"%self.name)
		else:
			if self.available() and self.selectionLegit(target, choice):
				canUseHeroPower = True
			else: PRINT(self.Game, "Invalid selection to use Hero Power {} on target {}, with choice {}".format(self.name, target, choice))
			
		if canUseHeroPower:
			PRINT(self.Game, "*********\nHandling using Hero Power {} with target {}, with choice	{}\n*********".format(self.name, target, choice))
			#支付费用，清除费用状态。
			subIndex, subWhere = self.ID, "power"
			if target:
				if target.type == "Minion": tarIndex, tarWhere = target.position, "minion%d"%target.ID
				else: tarIndex, tarWhere = target.ID, "hero"
			else: tarIndex, tarWhere = 0, ''
			self.Game.Manas.payManaCost(self, self.mana)
			if self.Game.withAnimation and self.Game.GUI:
				self.Game.GUI.updateCardinResolution(self)
				self.Game.GUI.wait(0.5)
			#如果有指向，则触发指向扳机（目前只有市长）
			targetHolder = [target]
			self.Game.sendSignal("HeroPowerTargetDecision", self.ID, self, targetHolder, 0, "", choice)
			if target != targetHolder[0] and self.Game.withAnimation and self.Game.GUI:
				target = targetHolder[0]
				self.Game.GUI.target = target
				self.Game.GUI.wait(0.5) #If the target is changed, show 0.4 more seconds
			else: target = targetHolder[0]
			
			minionsKilled = 0
			if target and target.type == "Minion" and self.Game.status[self.ID]["Power Sweep"] > 0:
				targets = self.Game.adjacentMinions2(target)[0]
				minionsKilled += self.effect(target, choice)
				if targets != []:
					PRINT(self.Game, "%s will also be cast upon minions adjacent to the target minion %s"%(self.name, target.name))
					for minion in targets: minionsKilled += self.effect(minion, choice)
			else: minionsKilled += self.effect(target, choice)
				
			#结算阶段结束，处理死亡，此时尚不进行胜负判定。
			#假设触发英雄技能消灭随从的扳机在死亡结算开始之前进行结算。（可能不对，但是相对比较符合逻辑。）
			if minionsKilled > 0:
				self.Game.sendSignal("HeroPowerKilledMinion", self.Game.turn, self, None, minionsKilled, "")
			self.Game.gathertheDead()
			PRINT(self.Game, "Hero used ability %s"%self.name)
			self.heroPowerTimes += 1
			#激励阶段，触发“每当你使用一次英雄技能”的扳机，如激励，虚空形态的技能刷新等。
			self.Game.sendSignal("HeroUsedAbility", self.ID, self, target, self.mana, "", choice)
			#激励阶段结束，处理死亡。此时可以进行胜负判定。
			self.Game.gathertheDead(True)
			for card in self.Game.Hand_Deck.hands[1] + self.Game.Hand_Deck.hands[2]:
				card.effectCanTrigger()
				card.checkEvanescent()
			self.Game.moves.append(("power", subIndex, subWhere, tarIndex, tarWhere, choice))
		
	def effect(self, target, choice=0):
		return 0
		
	def countDamageDouble(self):
		num = 0
		for minion in self.Game.minions[self.ID]:
			if minion.marks["Power Heal&Dmg x2"] > 0:
				num += 1
		return num
		
	def countHealDouble(self):
		num = 0
		for minion in self.Game.minions[self.ID]:
			if minion.marks["Heal x2"] > 0 or minion.marks["Power Heal&Dmg x2"] > 0:
				num += 1
		return num
		
	def createCopy(self, game):
		if self in game.copiedObjs:
			return game.copiedObjs[self]
		else:
			Copy = type(self)(game, self.ID)
			game.copiedObjs[self] = Copy
			Copy.mana = self.mana
			Copy.manaModifications = [mod.selfCopy(Copy) for mod in self.manaModifications]
			Copy.heroPowerTimes = self.heroPowerTimes
			Copy.heroPowerChances_base, Copy.heroPowerChances_extra = self.heroPowerChances_base, self.heroPowerChances_extra
			Copy.options = [option.selfCopy(Copy) for option in self.options]
			Copy.keyWords = copy.deepcopy(self.keyWords)
			Copy.triggersonBoard = [trig.createCopy(game) for trig in self.triggersonBoard]
			self.assistCreateCopy(Copy)
			return Copy
			

		
class Hero(Card):
	mana, weapon, description = 0, None, ""
	Class, name, heroPower, armor = "Neutral", "InnKeeper", None, 0
	index = ""
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		
	def blank_init(self, Game, ID):
		self.Game, self.ID = Game, ID
		self.mana, self.manaModifications = type(self).mana, []
		self.health_upper, self.health = 30, 30
		self.attack, self.attack_bare, self.armor = 0, 0, type(self).armor
		self.name = type(self).name
		self.index = type(self).index
		self.type = "Hero"
		self.weapon = type(self).weapon
		self.description = type(self).description
		self.Class = type(self).Class
		self.attChances_base, self.attChances_extra, self.attTimes = 1, 0, 0
		self.onBoard, self.inHand, self.inDeck = False, False, False
		self.dead = False
		self.heroPower = type(self).heroPower(self.Game, self.ID) if type(self).heroPower else None
		self.keyWords = {"Poisonous": 0} #Just as a placeholder
		self.status = {"Frozen": 0, "Temp Stealth": 0}
		self.triggers = {"Discarded": []}
		self.identity = [np.random.rand(), np.random.rand()]
		self.options = [] #For Choose One heroes
		self.overload, self.chooseOne = 0, 0
		self.identity = [np.random.rand(), np.random.rand(), np.random.rand()]
		self.triggersonBoard, self.triggersinHand, self.triggersinDeck = [], [], []
		self.effectViable, self.evanescent = False, False
		
	"""Handle hero's attacks, attack chances, attack chances and frozen status."""
	def STATUSPRINT(self):
		PRINT(self.Game, "Game is {}.".format(self.Game))
		PRINT(self.Game, "Hero %d %s: Attacked times: %d.	Base att chances left: %d.	Extra att chances left: %d"%(self.ID, self.name, self.attTimes, self.attChances_base, self.attChances_extra))
		if self.manaModifications != []:
			PRINT(self.Game, "\tCarries mana modification:")
			for manaMod in self.manaModifications:
				if manaMod.changeby != 0:
					PRINT(self.Game, "\t\tChanged by %d"%manaMod.changeby)
				else:
					PRINT(self.Game, "\t\tChanged to %d"%manaMod.changeto)
		PRINT(self.Game, "\tHero %s is frozen	{},  has Temp Stealth {}".format(self.status["Frozen"], self.status["Temp Stealth"]))
		PRINT(self.Game, "Player status")
		for key, value in self.Game.status[self.ID].items():
			if value > 0:
				PRINT(self.Game, "{}: {}".format(key, value))
		if hasattr(self, "progress"):
			PRINT(self.Game, "\tHero's progress is currently: %d"%self.progress)
			
	def actionable(self):
		return self.ID == self.Game.turn
		#不考虑冻结、零攻和自身有不能攻击的debuff的情况。
		
	def decideAttChances_base(self):
		weapon = self.Game.availableWeapon(self.ID)
		self.attChances_base = 2 if weapon and weapon.keyWords["Windfury"] > 0 else 1
			
	def getsFrozen(self):
		self.status["Frozen"] += 1
		PRINT(self.Game, "%s gets Frozen."%self.name)
		
	def turnStarts(self, ID):
		if ID == self.ID:
			self.status["Temp Stealth"] = 0
			if self.Game.status[self.ID]["Immune2NextTurn"] > 0:
				self.Game.status[self.ID]["Immune"] -= self.Game.status[self.ID]["Immune2NextTurn"]
				self.Game.status[self.ID]["Immune"] = max(0, self.Game.status[self.ID]["Immune"])
				self.Game.status[self.ID]["Immune2NextTurn"] = 0
			if self.Game.status[self.ID]["Evasive2NextTurn"] > 0:
				self.Game.status[self.ID]["Evasive"] -= self.Game.status[self.ID]["Evasive2NextTurn"]
				self.Game.status[self.ID]["Evasive2NextTurn"] = 0
				
			weapon = self.Game.availableWeapon(self.ID)
			self.bareAttack, self.attTimes, self.attChances_extra = 0, 0, 0
			if weapon:
				self.attack = self.bareAttack + max(0, weapon.attack)
				PRINT(self.Game, "Hero %s's attack is now %d+%d"%(self.name, self.bareAttack, weapon.attack))
			self.decideAttChances_base()
			
	def turnEnds(self, ID):
		if self.Game.status[self.ID]["ImmuneThisTurn"] > 0:
			self.Game.status[self.ID]["Immune"] -= self.Game.status[self.ID]["ImmuneThisTurn"]
			self.Game.status[self.ID]["Immune"] = max(0, self.Game.status[self.ID]["Immune"])
			self.Game.status[self.ID]["ImmuneThisTurn"] = 0
			
		if ID == self.ID:
			#一个角色只有在自己的回合结束时才能解冻
			if self.status["Frozen"] > 0 and self.attChances_base + self.attChances_extra > self.attTimes:
				self.status["Frozen"] = 0
				
		self.attack, self.attack_bare = 0, 0 #因为英雄没有跨回合的攻击力增加，所有攻击增益都会在回合结束时消失。
		self.attTimes = 0
			
	def gainTempAttack(self, attackGain):
		self.attack_bare += attackGain
		weapon = self.Game.availableWeapon(self.ID)
		self.attack = self.attack_bare + max(0, weapon.attack) if weapon else self.attack_bare
		
	def gainsArmor(self, armor):
		self.armor += armor
		
	"""Handle hero's being selectable by subjects or not. And hero's availability for battle."""
	def canAttack(self):
		if not self.actionable() or self.attack < 1 or self.status["Frozen"] > 0:
			return False
		if self.attChances_base + self.attChances_extra <= self.attTimes:
			return False
		return True
		
	def canAttackTarget(self, target):
		return self.canAttack() and target.selectablebyBattle(self)
		
	#Heroes don't have Lifesteal.
	def tryLifesteal(self, damage):
		pass
		
	def takesDamage(self, subject, damage, sendDamageSignal=True):
		damageTaken = 0
		if damage > 0 and self.Game.status[self.ID]["Immune"] <= 0:
			damageHolder = [damage]
			self.Game.sendSignal("HeroAbouttoTakeDamage", self.ID, subject, self, damageHolder, "")
			damageTaken, damage = damageHolder[0], damageHolder[0]
			if damage > 0:
				if self.armor > damage:
					self.armor -= damage
				else:
					self.health -= damage - self.armor
					self.armor = 0
				self.Game.Counters.damageonHeroThisTurn[self.ID] += damage
				if sendDamageSignal:
					self.Game.sendSignal("HeroTakesDamage", self.Game.turn, subject, self, damage, "")
					self.Game.sendSignal("HeroTookDamage", self.Game.turn, subject, self, damage, "")
		return damage
		
	#专门被英雄牌使用，加拉克苏斯大王和拉格纳罗斯都不会调用该方法。
	def played(self, target=None, choice=0, mana=0, posinHand=-2, comment=""): #英雄牌使用目前不存在触发发现的情况
	#使用阶段
		#英雄牌替换出的英雄的生命值，护甲和攻击机会都会继承当前英雄的值。
		self.health = self.Game.heroes[self.ID].health
		self.health_upper = self.Game.heroes[self.ID].health_upper
		self.armor = self.Game.heroes[self.ID].armor
		self.attack_bare = self.Game.heroes[self.ID].attack_bare
		self.attTimes = self.Game.heroes[self.ID].attTimes
		#英雄牌进入战场。（本来是应该在使用阶段临近结束时移除旧英雄和旧技能，但是为了方便，在此时执行。）
		#继承旧英雄的生命状态和护甲值。此时英雄的被冻结和攻击次数以及攻击机会也继承旧英雄。
		#清除旧的英雄技能。
		self.Game.powers[self.ID].disappears()
		self.Game.powers[self.ID].heroPower = None
		self.Game.heroes[self.ID].onBoard = False
		heroPower = self.heroPower #这个英雄技能必须存放起来，之后英雄还有可能被其他英雄替换，但是这个技能要到最后才登场。
		self.Game.heroes[self.ID] = self #英雄替换。如果后续有埃克索图斯再次替换英雄，则最后的英雄是拉格纳罗斯。
		self.Game.heroes[self.ID].onBoard = True
		if self.Game.withAnimation and self.Game.GUI:
			self.Game.GUI.updateCardinResolution(self)
			self.Game.GUI.wait(0.5)
		#使用时步骤，触发“每当你使用一张xx牌时”的扳机。
		self.Game.sendSignal("HeroCardPlayed", self.ID, self, None, mana, "", choice)
		#英雄牌的最大生命值和现有生命值以及护甲被设定继承旧英雄的数值。并获得英雄牌上标注的护甲值。
		self.gainsArmor(type(self).armor)
		#使用阶段结束，进行死亡结算，此时尚不进行胜负判定。
		self.Game.gathertheDead()
	#结算阶段
		#获得新的英雄技能。注意，在此之前英雄有可能被其他英雄代替，如伊利丹飞刀打死我方的管理者埃克索图斯。
			#埃克索图斯可以替换英雄和英雄技能，然后本英雄牌在此处开始结算，再次替换英雄技能为正确的英雄牌技能。
		heroPower.replaceHeroPower()
		#视铜须等的存在而结算战吼次数以及具体战吼。
		#不用返回主体，但是当沙德沃克调用时whenEffective函数的时候需要。
		if self.Game.status[self.ID]["Battlecry x2"] > 0:
			self.whenEffective(None, "", choice, posinHand)
		self.whenEffective(None, "", choice, posinHand)
		if self.weapon: #如果英雄牌本身带有武器，如迦拉克隆等。则装备那把武器
			self.Game.equipWeapon(self.weapon(self.Game, self.ID))
		weapon = self.Game.availableWeapon(self.ID)
		if weapon and self.ID == self.Game.turn:
			self.Game.heroes[self.ID].attack = self.Game.heroes[self.ID].attack_bare + max(0, weapon.attack)
		else: self.Game.heroes[self.ID].attack = self.Game.heroes[self.ID].attack_bare
		self.Game.heroes[self.ID].decideAttChances_base()
		#结算阶段结束，处理死亡，此时尚不进行胜负判定。
		self.Game.gathertheDead()
		
	#大王，炎魔之王拉格纳罗斯等替换英雄，此时没有战吼。
	#炎魔之王变身不会摧毁玩家的现有装备和奥秘。只会移除冰冻，免疫和潜行等状态。
	def replaceHero(self, fromHeroCard=False):
		#英雄被替换
		#被替换的英雄失去所有护甲。
		#假设直接替换的英雄不会继承之前英雄获得的回合内攻击力增加。
		self.attTimes = self.Game.heroes[self.ID].attTimes
		#英雄牌进入战场。（本来是应该在使用阶段临近结束时移除旧英雄和旧技能，但是为了方便，在此时执行。）
		#继承旧英雄的生命状态和护甲值。此时英雄的被冻结和攻击次数以及攻击机会也继承旧英雄。
		#大王和炎魔之王在替换之前被定义，拥有15或者8点生命值。0点护甲值和英雄技能等也已定义完毕。
		self.Game.heroes[self.ID] = self
		self.Game.heroes[self.ID].onBoard = True
		if self.heroPower: self.heroPower.replaceHeroPower()
		if self.weapon: #如果英雄本身带有装备，则会替换当前的玩家装备（如加拉克苏斯大王）
			self.Game.equipWeapon(self.weapon(self.Game, self.ID))
		if fromHeroCard == False: #英雄牌被其他牌打出时不会取消当前玩家的免疫状态
			#Hero's immune state is gone, except that given by Mal'Ganis
			self.Game.status[self.ID]["Immune"] -= self.Game.status[self.ID]["Immune2NextTurn"] + self.Game.status[self.ID]["ImmuneThisTurn"]
			self.Game.status[self.ID]["Immune2NextTurn"] = 0
			self.Game.status[self.ID]["ImmuneThisTurn"] = 0
			
		self.Game.sendSignal("HeroReplaced", self.ID, None, self, 0, "")
		
	def createCopy(self, game):
		if self in game.copiedObjs:
			return game.copiedObjs[self]
		else:
			Copy = type(self)(game, self.ID)
			game.copiedObjs[self] = Copy
			Copy.mana = self.mana
			Copy.manaModifications = [mod.selfCopy(Copy) for mod in self.manaModifications]
			Copy.attack, Copy.attack_bare, Copy.armor = self.attack, self.attack_bare, self.armor
			Copy.health_upper, Copy.health = self.health_upper, self.health
			Copy.attChances_base, Copy.attChances_extra, Copy.attTimes = self.attChances_base, self.attChances_extra, self.attTimes
			Copy.onBoard, Copy.inHand, Copy.inDeck = self.onBoard, self.inHand, self.inDeck
			Copy.dead = self.dead
			Copy.status = copy.deepcopy(self.status)
			for key, value in self.triggers.items():
				Copy.triggers[key] = [getattr(Copy, func.__qualname__.split(".")[1]) for func in value]
			Copy.identity = copy.deepcopy(self.identity)
			Copy.options = [option.selfCopy(Copy) for option in self.options]
			Copy.triggersonBoard = [trig.createCopy(game) for trig in self.triggersonBoard]
			Copy.triggersinHand = [trig.createCopy(game) for trig in self.triggersinHand]
			Copy.triggersinDeck = [trig.createCopy(game) for trig in self.triggersinDeck]
			Copy.effectViable, Copy.evanescent = self.effectViable, self.evanescent
			self.assistCreateCopy(Copy)
			return Copy
			
			
			
class Weapon(Card):
	Class, name, description = "Neutral", "Vanilla", ""
	mana, attack, durability = 2, 2, 2
	index = "Vanillar-Neutral-2-2-2-Weapon-Vanilla"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		
	def blank_init(self, Game, ID):
		self.Game, self.ID = Game, ID
		self.Class, self.name = type(self).Class, type(self).name
		self.type = "Weapon"
		self.mana, self.manaModifications = type(self).mana, []
		self.attack = type(self).attack
		self.statbyAura = [0, []] #没有针对武器耐久度的光环
		self.durability = type(self).durability #将来会处理有buff的武器洗入牌库的问题，如弑君
		self.description = type(self).description
		self.requireTarget = False
		self.keyWords = {"Lifesteal": False, "Poisonous": False, "Windfury": False}
		self.marks = {"Sweep": 0}
		self.triggers = {"Discarded": []}
		self.overload, self.chooseOne = 0, 0
		self.onBoard, self.inHand, self.inDeck = False, False, False
		self.dead = False
		self.sequence = -1
		self.deathrattles = []
		self.triggersonBoard, self.triggersinHand, self.triggersinDeck = [], [], []
		self.identity = [np.random.rand(), np.random.rand(), np.random.rand()]
		self.options = [] #For Choose One weapon, non-existent at this point.
		self.auras = {}
		self.effectViable, self.evanescent = False, False
		
	def STATUSPRINT(self):
		PRINT(self.Game, "Game is {}.".format(self.Game))
		PRINT(self.Game, "Weapon: %s. Description: %s"%(self.name, self.description))
		if self.manaModifications != []:
			PRINT(self.Game, "\tCarries mana modification:")
			for manaMod in self.manaModifications:
				if manaMod.changeby != 0:
					PRINT(self.Game, "\t\tChanged by %d"%manaMod.changeby)
				else:
					PRINT(self.Game, "\t\tChanged to %d"%manaMod.changeto)
		if self.triggersonBoard != []:
			PRINT(self.Game, "Weapon's triggersonBoard")
			for trigger in self.triggersonBoard:
				PRINT(self.Game, "{}".format(trigger))
		if hasattr(self, "progress"):
			PRINT(self.Game, "\tWeapon's progress is currently: %d"%self.progress)
			
	"""Handle weapon entering/leaving board/hand/deck"""
	#武器进场并连接侦听器，比如公正之剑可以触发伊利丹的召唤，这个召唤又反过来触发公正之剑的buff效果。
	def appears(self):
		#注意，此时武器还不能设为onBoard,因为之后可能会涉及亡语随从为英雄装备武器。
		#尚不能因为武器标记为onBoard而调用其destroyed。
		self.inHand, self.inDeck, self.dead = False, False, False
		self.mana = type(self).mana
		#武器的表面上的场上扳机和亡语都有相同的入场注册方式
		for trigger in self.triggersonBoard:
			trigger.connect() #把(obj, signal)放入Game.triggersonBoard中
		for trigger in self.deathrattles:
			trigger.connect()
		for value in self.auras.values(): #目前似乎只用舔舔魔杖有武器光环
			PRINT(self.Game, "Now starting weapon {}'s Aura {}".format(self.name, value))
			value.auraAppears()
			
	def setasNewWeapon(self):
		self.onBoard, self.dead = True, False
		#因为武器在之前已经被添加到武器列表，所以sequence需要-1，不然会导致错位
		self.sequence = len(self.Game.minions[1]) + len(self.Game.minions[2]) + len(self.Game.weapons[1]) + len(self.Game.weapons[2]) - 1
		if self.ID == self.Game.turn:
			self.Game.heroes[self.ID].attack = self.Game.heroes[self.ID].attack_bare + max(0, self.attack)
			self.Game.heroes[self.ID].decideAttChances_base()
		self.Game.sendSignal("WeaponEquipped", self.ID, self, None, 0, "")
		
	#Take care of the hero's attack chances and attack.
	#The deathrattles will be left to gathertheDead() and deathHandle()
	def destroyed(self):
		if self.onBoard: #只有装备着的武器才会触发，以防连续触发。
			PRINT(self.Game, "Weapon %s is destroyed"%self.name)
			if self.keyWords["Windfury"] > 0:
				self.Game.heroes[self.ID].decideAttChances_base()
			self.onBoard, self.dead = False, True
			self.Game.heroes[self.ID].attack = self.Game.heroes[self.ID].attack_bare
			#移除武器对应的场上扳机，亡语扳机在deathrattles中保存
			for trigger in self.triggersonBoard:
				trigger.disconnect()
				
			for value in self.auras.values():
				value.auraDisappears()
			#self.Game.sendSignal("WeaponRemoved", self.ID, self, None, 0, "")
			
	def deathResolution(self, attackbeforeDeath, triggersAllowed_WhenDies, triggersAllowed_AfterDied):
		PRINT(self.Game, "Now resolving the destruction of weapon %s"%self.name)
		#除了武器亡语以外，目前只有一个应对武器被摧毁的扳机，即冰封王座的Grave Shambler
		self.Game.sendSignal("WeaponDestroyed", self.ID, None, self, 0, "", triggersAllowed_WhenDies)
		self.Game.sendSignal("WeaponRemoved", self.ID, None, self, 0, "")
		for trigger in self.deathrattles:
			trigger.disconnect()
		self.__init__(self.Game, self.ID)
		
	def disappears(self):
		if self.onBoard: #只有装备着的武器才会触发，以防连续触发。
			PRINT(self.Game, "Weapon %s leaves board"%self.name)
			if self.keyWords["Windfury"] > 0:
				self.Game.heroes[self.ID].decideAttChances_base()
			self.onBoard = False
			self.Game.heroes[self.ID].attack = self.Game.heroes[self.ID].attack_bare
			#移除武器对应的场上扳机，亡语扳机在deathrattles中保存
			for trigger in self.triggersonBoard:
				trigger.disconnect()
			for value in self.auras.values():
				value.auraDisappears()
			self.Game.sendSignal("WeaponRemoved", self.ID, self, None, 0, "")
			
	"""Handle the mana, durability and stat of weapon."""
	#This method is invoked by Hero class, not a listner.			
	def loseDurability(self):
		PRINT(self.Game, "Weapon %s loses 1 Durability"%self.name)
		self.durability -= 1
		
	def gainStat(self, attack, durability):
		self.attack += attack
		self.durability += durability
		if self.Game.turn == self.ID and self.onBoard:
			self.Game.heroes[self.ID].attack = self.Game.heroes[self.ID].attack_bare + max(0, self.attack)
			
	"""Handle the weapon being played/equipped."""
	def played(self, target=None, choice=0, mana=0, posinHand=-2, comment=""):
	#使用阶段
		#武器进场并连接侦听器，比如公正之剑可以触发伊利丹的召唤，这个召唤又反过来触发公正之剑的buff效果。
		self.Game.weapons[self.ID].append(self)
		self.appears() #此时可以建立侦听器。此时onBoard还是False
		#注意，暂时不取消已经装备的武器的侦听，比如两把公正之剑可能同时为伊利丹召唤的元素buff。
		#使用时步骤，触发“每当你使用一张xx牌”的扳机，如伊利丹和无羁元素。
		self.Game.sendSignal("WeaponPlayed", self.ID, self, target, 0, "", choice=0)
		#结算过载。
		if self.overload > 0:
			PRINT(self.Game, "%s is played and Overloads %d mana crystals."%(self.name, self.overload))
			self.Game.Manas.overloadMana(self.overload, self.ID)
		#使用阶段结束，处理亡语，暂不处理胜负问题。
		#注意，如果此时伊利丹飞刀造成了我方佛丁的死亡，则其装备的灰烬使者会先替换目前装备的武器。
		#之后在结算阶段的武器正式替换阶段，被替换的武器就变成了灰烬使者。最终装备的武器依然是打出的这把武器。
		self.Game.gathertheDead() #此时被替换的武器先不视为死亡，除非被亡语引起的死亡结算先行替换（如佛丁）。
	#结算阶段
		#根据市长的存在情况来决定随机目标。
		targetHolder = [target]
		self.Game.sendSignal("BattlecryTargetDecision", self.ID, self, targetHolder, 0, "", choice=0)
		if target != targetHolder[0] and self.Game.withAnimation and self.Game.GUI:
			target = targetHolder[0]
			self.Game.GUI.target = target
			self.Game.GUI.wait(0.4)
		else: target = targetHolder[0]
		#根据铜须的存在情况来决定战吼的触发次数。不同于随从，武器的连击目前不会触发
		self.Game.GUI.wait(0.4)
		if self.Game.status[self.ID]["Battlecry x2"] > 0:
			#对方武器而言没有必要返回主体对象，但是当战吼被沙德沃克调用的时候，需要返回。
			target = self.whenEffective(target, "", choice, posinHand)
		target = self.whenEffective(target, "", choice, posinHand)
		#消灭旧武器，并将列表前方的武器全部移除。
		
		for weapon in self.Game.weapons[self.ID]:
			if weapon != self:
				#The removal of the preivous weapons will be left to the gathertheDead() method.
				#只有标记为onBoard的武器调用destroyed会有反应，防止因为之前佛丁的死亡引起同一把武器的多次摧毁信号。
				weapon.destroyed() #触发“每当你的一把武器被摧毁时”和“每当你的一把武器离场时”的扳机，如南海船工。
		#打出的这把武器会成为最后唯一还装备着的武器。触发“每当你装备一把武器时”的扳机，如锈水海盗。
		self.setasNewWeapon() #此时打出的武器的onBoard才会正式标记为True
		PRINT(self.Game, "Weapon {} is now onBoard: {}".format(self.name, self.onBoard))
		
		#结算阶段结束，处理亡语。（此时的亡语结算会包括武器的亡语结算。）
		self.Game.gathertheDead()
		#完成阶段在Game.playWeapon中处理。
		
	"""Handle the weapon restoring health, dealing damage and dealing AOE effects."""
	#对于武器而言，dealsDamage()只有毁灭之刃可以使用，因为其他的武器造成伤害不是AOE伤害就是战斗伤害
	#战斗伤害会在随从和英雄的attacks()方法中统一处理。毁灭之刃是唯一的拥有单体战吼的武器。
	
	def countHealDouble(self):
		num = 0
		for minion in self.Game.minions[self.ID]:
			if minion.marks["Heal x2"]: num += 1
		return num
		
	def createCopy(self, game):
		if self in game.copiedObjs:
			return game.copiedObjs[self]
		else:
			Copy = type(self)(game, self.ID)
			game.copiedObjs[self] = Copy
			Copy.mana = self.mana
			Copy.manaModifications = [mod.selfCopy(Copy) for mod in self.manaModifications]
			Copy.attack, Copy.durability = self.attack, self.durability
			Copy.keyWords, Copy.marks = copy.deepcopy(self.keyWords), copy.deepcopy(self.marks)
			for key, value in self.triggers.items():
				Copy.triggers[key] = [getattr(Copy, func.__qualname__.split(".")[1]) for func in value]
			Copy.onBoard, Copy.inHand, Copy.inDeck = self.onBoard, self.inHand, self.inDeck
			Copy.sequence = self.sequence
			Copy.identity = copy.deepcopy(self.identity)
			Copy.statbyAura = [self.statbyAura[0], [aura_Receiver.selfCopy(Copy) for aura_Receiver in self.statbyAura[1]]]
			for key, value in self.auras.items():
				Copy.auras[key] = value.createCopy(game)
			Copy.options = [option.selfCopy(Copy) for option in self.options]
			Copy.deathrattles = [trig.createCopy(game) for trig in self.deathrattles]
			Copy.triggersonBoard = [trig.createCopy(game) for trig in self.triggersonBoard]
			Copy.triggersinHand = [trig.createCopy(game) for trig in self.triggersinHand]
			Copy.triggersinDeck = [trig.createCopy(game) for trig in self.triggersinDeck]
			Copy.effectViable, Copy.evanescent = self.effectViable, self.evanescent
			self.assistCreateCopy(Copy)
			return Copy
			
			
			
class ChooseOneOption:
	name, description = "", ""
	index = ""
	def __init__(self, entity):
		self.entity = entity
		self.name = type(self).name
		self.description = type(self).description
		if hasattr(type(self), "index"):
			self.index = type(self).index
			
	def available(self):
		return True
		
	def selfCopy(self, recipient):
		return type(self)(recipient)
		
	#抉择选项的复制一定是以复制卡牌为前提的，调用此函数时，抉择主体一定已经被复制了
	def createCopy(self, game):
		entityCopy = game.copiedObjs[self.entity]
		return type(self)(entityCopy)