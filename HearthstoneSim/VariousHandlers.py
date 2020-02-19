import numpy as np

def extractfrom(target, listObject):
	temp = None
	for i in range(len(listObject)):
		if listObject[i] == target:
			temp = listObject.pop(i)
			break
	return temp
	
def fixedList(listObject):
	return listObject[0:len(listObject)]
	
	
class ManaHandler:
	def __init__(self, Game):
		self.Game = Game
		self.manas = {1:1, 2:0}
		self.manasUpper = {1:1, 2:0}
		self.manasLocked = {1:0, 2:0}
		self.manasOverloaded = {1:0, 2:0}
		self.manas_UpperLimit = {1:10, 2:10}
		self.CardAuras = []
		self.CardAuras_Backup = []
		self.PowerAuras = []
		self.PowerAuras_Backup = []
		self.status = {1: {"Spells Cost Health Instead": 0},
						2: {"Spells Cost Health Instead": 0}
						}
						
	#If there is no setting mana aura, the mana is simply adding/subtracting.
	#If there is setting mana aura
		#The temp mana change aura works in the same way as ordinary mana change aura.
	
	'''When the setting mana aura disappears, the calcMana function
	must be cited again for every card in its registered list.'''
	def overloadMana(self, num, ID):
		self.manasOverloaded[ID] += num
		self.Game.sendSignal("ManaOverloaded", ID, None, None, 0, "")
		self.Game.sendSignal("OverloadStatusCheck", ID, None, None, 0, "")
		
	def unlockOverloadedMana(self, ID):
		self.manas[ID] += self.manasLocked[ID]
		self.manas[ID] = min(self.manas_UpperLimit[ID], self.manas[ID])
		self.manasLocked[ID] = 0
		self.manasOverloaded[ID] = 0
		self.Game.sendSignal("OverloadStatusCheck", ID, None, None, 0, "")
		
	def gainManaCrystal(self, num, ID):
		self.manas[ID] += num
		self.manas[ID] = min(self.manas_UpperLimit[ID], self.manas[ID])
		self.manasUpper[ID] += num
		self.manasUpper[ID] = min(self.manas_UpperLimit[ID], self.manasUpper[ID])
		
	def gainEmptyManaCrystal(self, num, ID):
		if self.manasUpper[ID] + num <= self.manas_UpperLimit[ID]:
			self.manasUpper[ID] += num
			return True
		else:
			self.manasUpper[ID] = self.manas_UpperLimit[ID]
			return False
			
	def destroyManaCrystal(self, num, ID):
		self.manasUpper[ID] -= num
		self.manasUpper[ID] = max(0, self.manasUpper[ID])
		self.manas[ID] = min(self.manas[ID], self.manasUpper[ID])
		
	def costAffordable(self, subject):
		ID = subject.ID
		if subject.cardType == "Spell": #目前只考虑法术的法力消耗改生命消耗光环
			if self.status[ID]["Spells Cost Health Instead"] > 0:
				if subject.mana < self.Game.heroes[ID].health + self.Game.heroes[ID].armor or self.Game.playerStatus[ID]["Immune"] > 0:
					return True
			else:
				if subject.mana <= self.manas[ID]:
					return True
		else:
			if subject.mana <= self.manas[ID]:
				return True
				
		return False
		
	def payManaCost(self, subject, mana):
		ID = subject.ID
		mana = max(0, mana)
		if subject.cardType == "Spell":
			if self.status[ID]["Spells Cost Health Instead"] > 0:
				objtoTakeDamage = self.Game.DamageHandler.damageTransfer(self.Game.heroes[ID])
				targetSurvival = objtoTakeDamage.damageRequest(self, mana)
				if targetSurvival > 0:
					damageActual, survival = objtoTakeDamage.takesDamage(self, mana)
			else:
				self.manas[ID] -= mana
		else:
			self.manas[ID] -= mana
		self.Game.sendSignal("ManaCostPaid", ID, subject, None, mana, "")
		if subject.cardType == "Minion":
			self.Game.CounterHandler.manaSpentonPlayingMinions[ID] += mana
		elif subject.cardType == "Spell":
			self.Game.CounterHandler.manaSpentonSpells[ID] += mana
			
	#At the start of turn, player's locked mana crystals are removed.
	#Overloaded manas will becomes the newly locked mana.
	def turnStarts(self):
		ID = self.Game.turn
		self.manasUpper[ID] += 1
		self.manasUpper[ID] = min(self.manas_UpperLimit[ID], self.manasUpper[ID])
		
		self.manasLocked[self.Game.turn] = self.manasOverloaded[self.Game.turn]
		self.manasOverloaded[self.Game.turn] = 0
		#It's currently okay to have manas being negative, since manas won't be used to compare with things.
		self.manas[self.Game.turn] = self.manasUpper[self.Game.turn] - self.manasLocked[self.Game.turn]
		self.Game.sendSignal("OverloadStatusCheck", ID, None, None, 0, "")
		
		for aura in self.CardAuras_Backup:
			if aura.ID == self.Game.turn:
				tempAura = extractfrom(aura, self.CardAuras_Backup)
				tempAura.activate()
				
		self.calcMana_All()
		for aura in self.PowerAuras_Backup:
			if aura.ID == self.Game.turn:
				tempAura = extractfrom(aura, self.CardAuras_Backup)
				tempAura.activate()
				
		self.calcMana_Powers()
		
	#Manas locked at this turn doesn't disappear when turn ends. It goes away at the start of next turn.
	def turnEnds(self):
		for aura in self.CardAuras:
			if aura.temporary:
				print(aura, " expires at the end of turn.")
				aura.deactivate()
				
		self.calcMana_All()
		for aura in self.PowerAuras:
			if aura.temporary:
				print(aura, " expires at the end of turn.")
				aura.deactivate()
				
		self.calcMana_Powers()
		
	def calcMana_All(self):
		for card in self.Game.Hand_Deck.hands[1] + self.Game.Hand_Deck.hands[2]:
			card.mana = card.mana_set
			for aura in self.CardAuras:
				aura.handleMana(card)
			#Most minions have their selfManaChange() method empty.
			card.selfManaChange()
			
	def calcMana_Single(self, card):
		card.mana = card.mana_set
		for aura in self.CardAuras:
			aura.handleMana(card)
			
		card.selfManaChange()
		
	def calcMana_Powers(self):
		for aura in self.PowerAuras:
			aura.handleMana(self.Game.heroPowers[1])
			aura.handleMana(self.Game.heroPowers[2])
			
	#At this point, the tempManaChange doesn't get involved in the newly added card's mana calc.
	#The mana is decided by Setting first, then the mana aura newer than Setting will keeps decreasing the mana.
	#def calcMana_AddduringTurn(self, card):
	#	thereisTempManaChange = False
	#	if thereisTempManaChange and thereismanaSet:
	#		
	#	for 
	#	
	#巫师学徒光环入场 ， Naga战吼将手牌中所有法术设为5费，此时巫师学徒不会将其他法术重新设为4费，只有当一个新的光环入场时才会将法术重新设为其他费用。
	
#用于不寄存在随从实体上的暂时费用光环，如伺机待发等。寄存在随从身上的光环，由随从自己来控制
class TempManaEffect:
	def __init__(self, Game, ID):
		self.Game = Game
		self.ID = ID
		self.temporary = True
		self.triggersonBoard = []
		
	def activate(self):
		self.Game.ManaHandler.CardAuras.append(self)
		for trigger in self.triggersonBoard:
			trigger.connect()
		self.Game.ManaHandler.calcMana_All()
		
	def deactivate(self):
		extractfrom(self, self.Game.ManaHandler.CardAuras)
		for trigger in self.triggersonBoard:
			#The instance retrieves itself from the game's registered triggersonBoard
			trigger.disconnect()
		self.Game.ManaHandler.calcMana_All()
		
	def handleMana(self, target):
		pass
		
		
class TempManaEffect_Power:
	def __init__(self, Game, ID):
		self.Game = Game
		self.ID = ID
		self.temporary = True
		self.triggersonBoard = []
		
	def activate(self):
		self.Game.ManaHandler.CardAuras.append(self)
		for trigger in self.triggersonBoard:
			trigger.connect()
		self.Game.ManaHandler.calcMana_Powers()
		
	def deactivate(self):
		extractfrom(self, self.Game.ManaHandler.CardAuras)
		for trigger in self.triggersonBoard:
			#The instance retrieves itself from the game's registered triggersonBoard
			trigger.disconnect()
		self.Game.ManaHandler.calcMana_Powers()
		
	def handleMana(self, target):
		pass
		
		
class SecretHandler:
	def __init__(self, Game):
		self.Game = Game
		self.secrets = {1:[], 2:[]}
		
	def deploySecretsfromDeck(self, ID, num=1):
		secretsAvailable = []
		for card in self.Game.Hand_Deck.decks[ID]:
			if "--Secret" in card.index and self.isSecretDeployedAlready(card, ID) == False:
				secretsAvailable.append(card)
				
		if secretsAvailable != []:
			num = min(len(secretsAvailable), num)
			for i in range(num):
				secret = extractfrom(secretsAvailable[i], self.Game.Hand_Deck.decks[ID])
				if self.Game.turn !=secret.ID:
					secret.active = True
				else:
					secret.active = False
				self.secrets[ID].append(secret)
				
	def extractSecrets(self, ID, all=False):
		if all:
			numSecrets = len(self.secrets[ID])
			while self.secrets[ID] != []:
				self.secrets[ID][0].active = False
				self.secrets[ID].pop(0)
				
			return numSecrets
		else:
			if self.secrets[ID] != []:
				secret = self.secrets[ID].pop(np.random.randint(len(self.secrets[ID])))
				secret.active = False
				return secret
			else:
				return None
				
	#secret can be type, index or real card.
	def isSecretDeployedAlready(self, secret, ID):
		if type(secret) == type(""): #If secret is the index
			for deployedSecret in self.secrets[ID]:
				if deployedSecret.index == secret:
					return True
			return False
		else: #If secret is real card or type
			for deployedSecret in self.secrets[ID]:
				if deployedSecret.name == secret.name:
					return True
			return False
			
			
class DamageHandler:
	def __init__(self, Game):
		self.Game = Game
		self.ShellfighterExists = {1: 0, 2: 0}
		self.RamshieldExists = {1: 0, 2: 0}
	
	def isActiveShellfighter(self, target):
		if target.name == "Snapjaw Shellfighter" and target.silenced == False:
			return True
		return False
		
	def isActiveBolfRamshield(self, target):
		if target.name == "Bolf Ramshield" and target.silenced == False:
			return True
		return False
		
	#Will return the leftmost Shellfighter in the chain or the minion itself.
	def leftmostShellfighter(self, minion):
		pos = minion.position
		Shellfighter_Left = minion
		while pos > 0: #Pos must be compared to the leftmost pos possible.
			minion_Left = self.Game.minionsonBoard(minion.ID)[pos-1]
			if self.isActiveShellfighter(minion_Left):
				Shellfighter_Left = minion_left
				pos -= 1
			else: #If the minion on the left is not Shellfighter, the previous Shellfighters has been stored in the Shellfighter_Left variable.
				break
				
		return Shellfighter_Left
		
	#Will return the rightmost Shellfighter in the chain or the minion itself.
	def rightmostShellfighter(self, minion):
		pos = minion.position
		Shellfighter_Right = minion
		rightEndPos = len(self.Game.minionsonBoard(minion.ID)) - 1
		while pos < rightEndPos:
			minion_Right = self.Game.minionsonBoard(minion.ID)[pos+1]
			if self.isActiveShellfighter(minion_Right):
				Shellfighter_Right = minion_Right
				pos += 1
			else: #If the minion on the left is not Shellfighter, the previous Shellfighters has been stored in the Shellfighter_Left variable.
				break
				
		return Shellfighter_Right
		
	#Return the correct minion to take damage.
	#Untested: Immune minions when taking potential damage, they won't transfer the damage.
	def damageTransfer_InitiallyonMinion(self, minion):
		if minion.cardType == "Permanent":
			return minion
		#This method will never be invoked if the minion is dead already or in deck.
		else: #minion.cardType == "Minion"
			if minion.inHand:
				return minion
			elif minion.onBoard:
				if self.ShellfighterExists[minion.ID] <= 0 or minion.status["Immune"] > 0:
					return minion #Immune minions won't need to transfer damage
				else:
					adjacentMinions, distribution = self.Game.findAdjacentMinions(minion)
					if distribution == "Minions on Both Sides":
						ShellfighterontheLeft = self.isActiveShellfighter(adjacentMinions[0])
						ShellfighterontheRight = self.isActiveShellfighter(adjacentMinions[1])
						#If both sides are active Shellfighters, the early one on board will trigger.
						if ShellfighterontheLeft and ShellfighterontheRight:
							if adjacentMinions[0].sequence < adjacentMinions[1].sequence:
								miniontoTakeDamage = self.leftmostShellfighter(minion)
							else:
								miniontoTakeDamage = self.rightmostShellfighter(minion)
						#If there is only a Shellfighter on the left, find the leftmost Shellfighter
						elif ShellfighterontheLeft:
							miniontoTakeDamage = self.leftmostShellfighter(minion)
						#If there is only a Shellfighter on the right, find the rightmost Shellfighter
						else:
							miniontoTakeDamage = self.rightmostShellfighter(minion)
							
					elif distribution == "Minions Only on the Left":
						miniontoTakeDamage = self.leftmostShellfighter(minion)
					elif distribution == "Minions Only on the Right":
						miniontoTakeDamage = self.rightmostShellfighter(minion)
					elif distribution == "No Adjacent Minions":
						miniontoTakeDamage = minion
						
					return miniontoTakeDamage
					
	def damageTransfer_InitiallyonHero(self, hero):
		if self.RamshieldExists[hero.ID] <= 0 or self.Game.playerStatus[hero.ID]["Immune"] > 0:
			return hero
		else:
			Ramshields = []
			for minion in self.Game.minionsonBoard(hero.ID):
				if minion.name == "Bolf Ramshield" and minion.silenced == False:
					Ramshields.append(minion)
					
			if Ramshields != []:
				Ramshields, order = self.Game.sort_Sequence(Ramshield)
				minion = Ramshields[0]
				return self.damageTransfer_InitiallyonMinion(minion)
			else:
				return hero
				
	def damageTransfer(self, target):
		if target.cardType == "Minion":
			return self.damageTransfer_InitiallyonMinion(target)
		elif target.cardType == "Hero":
			return self.damageTransfer_InitiallyonHero(target)
			
			
class CounterHandler:
	def __init__(self, Game):
		self.Game = Game
		self.cardsPlayedThisGame = {1:[], 2:[]}
		self.minionsDiedThisGame = {1:[], 2:[]}
		self.mechsDiedThisGame = {1:[], 2:[]}
		self.manaSpentonSpells = {1: 0, 2: 0}
		self.manaSpentonPlayingMinions = {1: 0, 2: 0}
		self.numPogoHoppersPlayedThisGame = {1: 0, 2: 0}
		self.healthRestoredThisGame = {1: 0, 2: 0}
		self.cardsDiscardedThisGame = {1:[], 2:[]}
		
		self.numSpellsPlayedThisTurn = {1: 0, 2: 0}
		self.numMinionsPlayedThisTurn = {1: 0, 2: 0}
		self.minionsDiedThisTurn = {1:[], 2:[]}
		self.cardsPlayedThisTurn = {1: [], 2: []} #For Combo and Secret.
		self.damageonHeroThisTurn = {1:0, 2:0}
		self.damageDealtbyHeroPower = {1:0, 2:0}
		self.numElementalsPlayedLastTurn = {1:0, 2:0}
		self.spellsPlayedLastTurn = {1:[], 2:[]}
		
		self.CThunAttack = {1:6, 2:6}
		self.jadeGolemCounter = {1:1, 2:1}
		
	def turnEnds(self):
		self.numElementalsPlayedLastTurn[self.Game.turn] = 0
		for index in self.cardsPlayedThisTurn[self.Game.turn]:
			if "-Elemental-" in index:
				self.numElementalsPlayedLastTurn[self.Game.turn] += 1
		self.spellsPlayedLastTurn[self.Game.turn] = []
		for index in self.cardsPlayedThisTurn[self.Game.turn]:
			if "-Spell-" in index:
				self.spellsPlayedLastTurn[self.Game.turn].append(index)
		self.cardsPlayedThisTurn = {1:[], 2:[]}
		self.numMinionsPlayedThisTurn = {1:0, 2:0}
		self.numSpellsPlayedThisTurn = {1:0, 2:0}
		self.damageonHeroThisTurn = {1:0, 2:0}
		self.minionsDiedThisTurn = {1:[], 2:[]}
		
		
def whenEffective():
	self.Game.options = [xx, xx, xx]
	self.Game.DiscoverHandler.startDiscover(initiator=self)
	
#class DiscoverHandler:
#	def __init__(self, Game):
#		self.Game = Game
#		self.initiator = None
#		self.discoveredOption = None
#		self.threadEvent = None
#		
#	def accessGUIDiscover(self):
#		print("Entering the discover UI.")
#		if self.Game.GUI != None:
#			self.Game.GUI.enterDiscover()
#			
#	def startDiscover(self, initiator):
#		self.initiator = initiator
#		self.threadEvent = threading.Event()
#		thread  = threading.Thread(target=self.accessGUIDiscover)
#		print("Start thread ", self.threadEvent)
#		thread.start()
#		#The GUI will discover the option and invoke the threadEvent.set()
#		#The threadEvent.set() can make the threadEvent.wait(timeout=5) return True in the loop and carry on the Game running.
#		while True:
#			if self.threadEvent.wait(timeout=20):
#				break
#			else:
#				print("20 seconds passed. Discover still not decided.")
#				
#		self.threadEvent = None
#		self.initiator.discoverDecided(self.discoveredOption)
#		self.Game.options = []
#		self.Game.option = None
#		self.initiator = None

class DiscoverHandler:
	def __init__(self, Game):
		self.Game = Game
		self.initiator = None
		
	#When there is no GUI selection, the player_HandleRNG should do the discover right away.
	#当Player决定打出一张触发发现的手牌时，进入发现过程，然后player会假设挑选所有的发现选项，然后根据不同的发现选项来分析得到这个发现选项之后的行为（同样
	#是NO_RNG和有一次随机的选项，然后和其他的对比），取分数最高的挑选。
	#这次挑选之后如果有再次发现的情况，则需要再次进行以上流程。
	def branch_discover(self, initiator):
		self.initiator = initiator
		for i in range(len(discoverOptions)):
			game = copy.deepcopy(self.Game)
			option = game.options[i]
			initiatorCopy = game.initiator
			#拿到提供的一个发现选项。
			initiatorCopy.discoverDecided(option)#这里可能会返回多次发现的情况，如档案管理员
			game.options = []
			#根据这个发现选项进行排列组合，挑选无随机的所有可能性。记录下那个分数，和之后其他选项的对比
			discover_branch[key+initiator.name+"_chooses_"+option.name+";"] = game
			
	def startDiscover(self, initiator):
		print("The discover options for %s:"%initiator.name)
		for i in range(len(self.Game.options)):
			option = self.Game.options[i]
			if option.cardType == "Minion":
				print(i+1, " Minion %s: Mana %d	Att %d	Health %d	Race%s."%(option.name, option.mana_set, option.attack_Enchant, option.health_Enchant, option.race))
				keyWords = []
				for key, value in option.keyWords.items():
					if value > 0:
						keyWords.append(key)
				print("\tMinion has keyWords: ", keyWords)
				print("\tMinion description: ", option.description)
			elif option.cardType == "Spell":
				print(i+1, " Spell %s: Mana %d"%(option.name, option.mana_set))
				print("\tSpell description: ", option.description)
			elif option.cardType == "Weapon":
				print(i+1, " Weapon %s: Mana %d	Att %d	Durability %d."%(option.name, option.mana_set, option.attack, option.durability))
				keyWords = []
				for key, value in option.keyWords.items():
					if value > 0:
						keyWords.append(key)
				print("\tWeapon has keyWords: ", keyWords)
				print("\tWeapon description: ", option.description)
			elif option.cardType == "Hero":
				print(i+1, "Hero Card %s: Mana %d	"%(option.name, option.mana_set))
				print("\tHero Card description: ", option.description)
			else:
				print(i+1, "Hero Power %s: Mana %d"%(option.name, option.mana))
				print("\tHero Power description: ", option.description)
				
		while True:
			choice = input("Type the index of the option for discover: ")
			choice = (int)(choice)
			if choice not in [i + 1 for i in range(len(self.Game.options))]:
				print("Type a valid index to continue.")
			else:
				break
				
		option = self.Game.options[choice-1]
		print("The discover option is ", option.name)
		initiator.discoverDecided(option)
		self.Game.options = []
		