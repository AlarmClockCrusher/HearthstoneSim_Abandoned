import pygame
from Basic import *
from Classic import *
from Witchwood import *
from Boomsday import *
from Rumble import *
from Shadows import *
from Uldum import *
from Dragons import *
from Galakrond import *

print("Ready to load the RNGPools for the Game")
from CardPools import cardPool, MinionsofCost, MinionswithRace, RNGPools

from Game import *

Refresh_rate = 30

green = (0,255,0)
red = (255,0,0)
black = (0,0,0)
white = (255,255,255)
blue = (0, 0, 128)
blueviolet = (138,43,226)
yellow = (255, 255, 0)
lightskyblue = (135,206,250)

X = 800
Y = 700
BoardPosition = (0, 0.35*Y, 0.85*X, 0.35*Y)
Hero1Position = (X/2-30, Y-200, 60, 80)
Hero2Position = (X/2-30, 140, 60, 80)
EndTurnPosition1 = (X-100, Y/2+40, 50, 30)
EndTurnPosition2 = (X-100, Y/2-40, 50, 30)
EndMulliganPosition = (X/2-10, Y/2, 50, 30)
Weapon1Position = (X/2-100, Y-180, 60, 60)
Weapon2Position = (X/2-100, 150, 60, 60)
HeroPower1Position = (X/2+50, Y-170, 60, 60)
HeroPower2Position = (X/2+50, 150, 60, 60)


class GUI:
	def __init__(self):
		self.Game = Game() #Link the game with the GUI creating it.
		self.Game.initialize(cardPool, MinionsofCost, MinionswithRace, RNGPools)
		self.gameOver = False
		pygame.init()
		print("Game Created.")
		self.display = pygame.display.set_mode((X, Y))
		pygame.display.set_caption("Test GUI")
		
		self.heroPositions = [Hero1Position, Hero2Position]
		self.minionsDrawn = {1:[], 2:[]}
		self.posMinionsDrawn = {1:[], 2:[]}
		#All hands are drawn, so we can simply invoke self.Game.Hand_Deck.hands
		self.posHands = {1:[], 2:[]}
		self.posOptions = []
		self.posMulligans = {1:[(18+(X/10)*i, Y - 65, 40, 60) for i in range(len(self.Game.mulligans[1]))],
							2:[(18+(X/10)*i, 20, 40, 60) for i in range(len(self.Game.mulligans[2]))]}
		self.mulliganStatus = {1:[0, 0, 0], 2:[0, 0, 0, 0]}
		
		self.subject = None
		self.target = None
		self.choice = 0
		self.position = -1
		self.UI = -1 #起手调试界面。
		
	#Register the iniator of the discover.
	#def enterDiscover(self):
	#	self.UI = 3 #发现界面。
	#	self.posOptions = []
	#	print("Discover message received. The initiator is ", self.Game.DiscoverHandler.initiator)
	#	print("Discover options are: ")
	#	for option in self.Game.options:
	#		print(option.name)
		
	def update(self):
		self.display.fill(black)
		self.posMinionsDrawn[1].clear()
		self.posMinionsDrawn[2].clear()
		self.posHands[1].clear()
		self.posHands[2].clear()
		self.drawHeroes()
		#Draw the end turn buttion.
		if self.Game.turn == 1:
			pygame.draw.rect(self.display, green, EndTurnPosition1)
		else:
			pygame.draw.rect(self.display, green, EndTurnPosition2)
		#Acquire the positions of the minions to draw them
		for i in range(len(self.Game.minions[1])):
			self.posMinionsDrawn[1].append((30+(X/8)*i, Y-300, 60, 80))
		for i in range(len(self.Game.minions[2])):
			self.posMinionsDrawn[2].append((30+(X/8)*i, 270, 60, 80))
		#Draw the minions
		self.drawMinions()
		
		#Decide the posHands, where to draw the hands.
		for i in range(len(self.Game.Hand_Deck.hands[1])):
			self.posHands[1].append((18+(X/10)*i, Y - 65, 40, 60))
		for i in range(len(self.Game.Hand_Deck.hands[2])):
			self.posHands[2].append((18+(X/10)*i, 40, 40, 60))
		self.drawHands()
		
		self.drawManasHandsDecksSecretsQuests()	
		self.drawHeroPowers()
		self.drawWeapon()
		#The discover options are given in the self.Game.discoverOptions.
		if self.UI == -1:
			self.drawMulligan()
		elif self.UI == 1: #UI == 1 corresponds to Choose One
			self.drawChooseOne()
		#elif self.UI == 3: #UI == 3 corresponds to Discover
		#	self.drawOptions()
			
		pygame.draw.rect(self.display, blue, BoardPosition, 4) #Draw the blue box that indicate the position of board
		pygame.display.update()
		
	def displayText(self, text, color, position, size=12):
		font = pygame.font.Font("freesansbold.ttf", size)
		text = font.render(text, True, color, white)
		textRect = text.get_rect()
		textRect.center = position
		self.display.blit(text, textRect)
		
	def displayCardName(self, name, lastLineCenterPos, size=12):
		if len(name) < 13:
			self.displayText(name, black, lastLineCenterPos, size)
		else:
			lines, string, words = [], "", name.split(' ')
			for i in range(len(words)):
				if i == 0:
					string += words[i] #The first word has to be included no matter what
				else:
					if len(string + words[i]) > 12: #If including next word would make the line too long, wrap around
						lines.append(string)
						string = words[i]
					else: #If including the next word won't make it too long.
						string += ' ' + words[i]
						
			lines.append(string)
			for i in range(len(lines)):
				self.displayText(lines[-i-1], black, (lastLineCenterPos[0], lastLineCenterPos[1]-1.1*size*i), size)
				
	def drawMinions(self):
		for ID in range(1, 3):
			for i in range(len(self.posMinionsDrawn[ID])):
				pos, minion = self.posMinionsDrawn[ID][i], self.Game.minions[ID][i]
				if minion.cardType == "Minion":
					color = green if minion.canAttack() else red
					pygame.draw.rect(self.display, color, pos)
					self.displayCardName(minion.name, (pos[0]+pos[2]/2, pos[1]))
					#self.displayText(minion.name, blue, (pos[0]+pos[2]/2, pos[1]))
					color = blue if minion.attack != type(minion).attack else black
					self.displayText((str)(minion.attack), blue, (pos[0], pos[1]+pos[3]), 15)
					color = blue if minion.health >= minion.health_upper else red
					self.displayText((str)(minion.health), color, (pos[0]+pos[2], pos[1]+pos[3]), 15)
				else:
					pygame.draw.rect(self.display, red, pos)
					self.displayText(minion.name, blue, (pos[0]+pos[2]/2, pos[1]))
					
				keyWords = []
				for key, value in minion.keyWords.items():
					if value > 0 and key != "Echo":
						keyWords.append(key)
				for i in range(min(4, len(keyWords))):
					self.displayText(keyWords[i], blueviolet, (pos[0]+pos[2]/2-5, pos[1]+15+i*13))
				if minion.triggersonBoard != [] or minion.deathrattles != []:
					pygame.draw.rect(self.display, yellow, (pos[0]+0.4*pos[2], pos[1]+0.9*pos[3], pos[2]/5, pos[3]/5))
				self.displayText("Sequence", blueviolet, (pos[0]+pos[2]/2-5, pos[1]+pos[3]-15))
				self.displayText((str)(minion.sequence), blueviolet, (pos[0]+pos[2], pos[1]+pos[3]-15))
				
				
	def drawHands(self):
		for ID in range(1, 3):
			for i in range(len(self.posHands[ID])):
				card, color = self.Game.Hand_Deck.hands[ID][i], red
				if ID == self.Game.turn and card.mana <= self.Game.ManaHandler.manas[ID]:
					if (card.cardType == "Spell" and card.available()) or (card.cardType == "Minion" and self.Game.spaceonBoard(ID) > 0) or card.cardType == "Weapon" or card.cardType == "Hero":
						if card.evanescent:
							color = lightskyblue
						elif hasattr(card, "effectViable") and card.effectViable:
							color = yellow
						else:
							color = green
							
				pos = self.posHands[ID][i]
				pygame.draw.rect(self.display, color, pos)
				self.displayCardName(card.name, (pos[0]+pos[2]/2, pos[1]))
				self.displayText((str)(card.mana), blue, (pos[0], pos[1]+10))
				if card.cardType == "Minion":
					self.displayText((str)(card.attack), blue, (pos[0], pos[1]+pos[3]))
					self.displayText((str)(card.health), blue, (pos[0]+pos[2], pos[1]+pos[3]))
				elif card.cardType == "Weapon":
					self.displayText((str)(card.attack), blue, (pos[0], pos[1]+pos[3]))
					self.displayText((str)(card.durability), blue, (pos[0]+pos[2], pos[1]+pos[3]))
					
	def drawHeroes(self):
		for ID in range(1, 3):
			color = green if self.Game.heroes[ID].canAttack() else red
			pos = Hero1Position if ID == 1 else Hero2Position
			pygame.draw.rect(self.display, color, pos)
			self.displayCardName(self.Game.heroes[ID].name, (pos[0]+pos[2]/2, pos[1]))
			#self.displayText(self.Game.heroes[ID].name, black, (pos[0]+pos[2]/2, pos[1]))
			healthColor = black if self.Game.heroes[ID].health >= self.Game.heroes[ID].health_upper else red
			self.displayText((str)(self.Game.heroes[ID].health), healthColor, (pos[0]+pos[2], pos[1]+pos[3]), 14)
			if self.Game.heroes[ID].attack != 0:
				self.displayText((str)(self.Game.heroes[ID].attack), black, (pos[0], pos[1]+pos[3]), 14)
			if self.Game.heroes[ID].armor != 0:
				self.displayText((str)(self.Game.heroes[ID].armor), black, (pos[0]+pos[2], pos[1]+pos[3] - 20), 14)
				
	def drawWeapon(self):
		for ID in range(1, 3):
			pos = Weapon1Position if ID == 1 else Weapon2Position
			weapon = self.Game.availableWeapon(ID)
			if weapon != None:
				color = blue if self.Game.turn == ID else red
				pygame.draw.rect(self.display, color, pos)
				self.displayCardName(weapon.name, (pos[0]+pos[2]/2, pos[1]))
				#self.displayText(weapon.name, black, (pos[0]+pos[2]/2, pos[1]))
				self.displayText((str)(weapon.attack), black, (pos[0], pos[1]+ pos[3]))
				if weapon.durability < type(weapon).durability:
					self.displayText((str)(weapon.durability), red, (pos[0]+pos[2], pos[1]+ pos[3]))
				else:
					self.displayText((str)(weapon.durability), black, (pos[0]+pos[2], pos[1]+ pos[3]))
					
	def drawHeroPowers(self):
		heroPowerColor1, heroPowerColor2 = red, red
		if self.Game.turn == 1 and self.Game.heroPowers[1].available() and self.Game.heroPowers[1].mana <= self.Game.ManaHandler.manas[1]:
			heroPowerColor1 = green
		if self.Game.turn == 2 and self.Game.heroPowers[2].available() and self.Game.heroPowers[2].mana <= self.Game.ManaHandler.manas[2]:
			heroPowerColor2 = green
			
		pygame.draw.rect(self.display, heroPowerColor1, HeroPower1Position)
		pygame.draw.rect(self.display, heroPowerColor2, HeroPower2Position)
		self.displayCardName(self.Game.heroPowers[1].name, (HeroPower1Position[0]+HeroPower1Position[2]/2, HeroPower1Position[1]))
		self.displayCardName(self.Game.heroPowers[2].name, (HeroPower2Position[0]+HeroPower2Position[2]/2, HeroPower2Position[1]))
		#self.displayText(self.Game.heroPowers[1].name, black, (HeroPower1Position[0]+HeroPower1Position[2]/2, HeroPower1Position[1]))
		#self.displayText(self.Game.heroPowers[2].name, black, (HeroPower2Position[0]+HeroPower2Position[2]/2, HeroPower2Position[1]))
		self.displayText(str(self.Game.heroPowers[1].mana), black, (HeroPower1Position[0]+HeroPower1Position[2]/2, HeroPower1Position[1]+HeroPower1Position[3]/2))
		self.displayText(str(self.Game.heroPowers[2].mana), black, (HeroPower2Position[0]+HeroPower2Position[2]/2, HeroPower2Position[1]+HeroPower2Position[3]/2))
		
	def drawManasHandsDecksSecretsQuests(self): #Draw the manas and the size of hands and decks
		if self.Game.turn == 1:
			color1, color2 = black, red
		else:
			color1, color2 = red, black
			
		self.displayText("Mana:%d/%d"%(self.Game.ManaHandler.manas[1], self.Game.ManaHandler.manasUpper[1]), color1, (X-60, Y-110), 20)
		self.displayText("Overload: %d"%self.Game.ManaHandler.manasOverloaded[1], color1, (X-70, Y-180), 20)
		self.displayText("Locked: %d"%self.Game.ManaHandler.manasLocked[1], color1, (X-70, Y-200), 20)
		self.displayText("Hand:%d"%len(self.Game.Hand_Deck.hands[1]), color1, (X-60, Y-140), 20)
		self.displayText("Deck:%d"%len(self.Game.Hand_Deck.decks[1]), color1, (X-60, Y-160), 20)
		
		self.displayText("Mana:%d/%d"%(self.Game.ManaHandler.manas[2], self.Game.ManaHandler.manasUpper[2]), color2, (X-60, 120), 20)
		self.displayText("Overload: %d"%self.Game.ManaHandler.manasOverloaded[2], color2, (X-70, 180), 20)
		self.displayText("Locked: %d"%self.Game.ManaHandler.manasLocked[2], color2, (X-70, 200), 20)
		self.displayText("Hand:%d"%len(self.Game.Hand_Deck.hands[2]), color2, (X-60, 140), 20)
		self.displayText("Deck:%d"%len(self.Game.Hand_Deck.decks[2]), color2, (X-60, 160), 20)
		
		for i in range(len(self.Game.SecretHandler.secrets[1])):
			self.displayText(self.Game.SecretHandler.secrets[1][i].name, color2, (0.75*X, Y-130-i*16), 15)
			
		for i in range(len(self.Game.SecretHandler.secrets[2])):
			self.displayText(self.Game.SecretHandler.secrets[2][i].name, color1, (0.75*X, 120+i*16), 15)
			
		if self.Game.SecretHandler.mainQuests[1] != []:
			self.displayText(self.Game.SecretHandler.mainQuests[1][0].name+": "+str(self.Game.SecretHandler.mainQuests[1][0].progress), black, (0.25*X, Y-130), 20)
		for i in range(len(self.Game.SecretHandler.sideQuests[1])):
			self.displayText(self.Game.SecretHandler.sideQuests[1][i].name+": "+str(self.Game.SecretHandler.sideQuests[1][i].progress), black, (0.15*X, Y-150-i*16), 20)
		if self.Game.SecretHandler.mainQuests[2] != []:
			self.displayText(self.Game.SecretHandler.mainQuests[2][0].name+": "+str(self.Game.SecretHandler.mainQuests[2][0].progress), black, (0.25*X, 120), 20)
		for i in range(len(self.Game.SecretHandler.sideQuests[2])):
			self.displayText(self.Game.SecretHandler.sideQuests[2][i].name+": "+str(self.Game.SecretHandler.sideQuests[2][i].progress), black, (0.15*X, 140+i*16), 20)
			
			
	def drawChooseOne(self):
		self.posOptions.clear()
		for i in range(len(self.Game.options)):
			position = (30+100*i, Y/2-50, 60, 100)
			self.posOptions.append(position)
			pygame.draw.rect(self.display, green, position)
			self.displayText(self.Game.options[i].name, blue, (position[0]+position[2]/2, position[1]))
			self.displayText(self.Game.options[i].description, blue, (position[0], position[1]+position[3]/2))
			
	#def drawOptions(self):
	#	print("Options to draw are:", self.Game.options)
	#	self.posOptions.clear()
	#	for i in range(len(self.Game.options)):
	#		position = (30+100*i, Y/2-50, 60, 100)
	#		self.posOptions.append(position)
	#		pygame.draw.rect(self.display, green, position)
	#		self.displayText(self.Game.options[i].name, blue, (position[0]+position[2]/2, position[1]))
	#		if self.Game.options[i].cardType == "Minion":
	#			self.displayText((str)(self.Game.options[i].mana), blue, (position[0], position[1]+10))
	#			self.displayText((str)(self.Game.options[i].attack), blue, (position[0], position[1]+position[3]))
	#			self.displayText((str)(self.Game.options[i].health), blue, (position[0]+position[2], position[1]+position[3]))
	#			
	#		elif self.Game.options[i].cardType == "Spell":
	#			self.displayText((str)(self.Game.options[i].mana), blue, (position[0], position[1]+10))
	#			
	#		elif self.Game.options[i].cardType == "Weapon":
	#			self.displayText((str)(self.Game.options[i].mana), blue, (position[0], position[1]+10))
	#			self.displayText((str)(self.Game.options[i].attack), blue, (position[0], position[1]+position[3]))
	#			self.displayText((str)(self.Game.options[i].durability), blue, (position[0]+position[2], position[1]+position[3]))
	#			
	#		elif self.Game.options[i].cardType == "Hero":
	#			self.displayText((str)(self.Game.options[i].mana), blue, (position[0], position[1]+10))
				
	def drawMulligan(self):
		for ID in range(1, 3):
			num = 0
			for i in range(len(self.posMulligans[ID])):
				pos = self.posMulligans[ID][i]
				card = self.Game.mulligans[ID][i]
				if self.mulliganStatus[ID][i]:
					color = red
				else:
					color = green
				pygame.draw.rect(self.display, color, pos)
				self.displayCardName(card.name, (pos[0]+pos[2]/2, pos[1]))
				self.displayText((str)(card.mana), blue, (pos[0], pos[1]+10))
				
				if card.cardType == "Minion":
					self.displayText((str)(card.attack), blue, (pos[0], pos[1]+pos[3]))
					self.displayText((str)(card.health), blue, (pos[0]+pos[2], pos[1]+pos[3]))
				
				elif card.cardType == "Weapon":
					self.displayText((str)(card.attack), blue, (pos[0], pos[1]+pos[3]))
					self.displayText((str)(card.durability), blue, (pos[0]+pos[2], pos[1]+pos[3]))
								
			pygame.draw.rect(self.display, green, EndMulliganPosition)
			
	def entityClicked(self, x, y, entityArea):
		if x > entityArea[0] and x <= (entityArea[0] + entityArea[2]) and y > entityArea[1] and y < (entityArea[1] + entityArea[3]):
			return True
		return False
		
	def scanClicked(self, pos):
		x, y = pos[0], pos[1]
		#界面在抉择和发现中时
		if self.UI == 1: # or self.UI == 3:
			for i in range(len(self.posOptions)):
				if self.entityClicked(x, y, self.posOptions[i]):
					print("The option chosen is ", self.Game.options[i])
					self.posOptions.clear()
					return ("Choose", self.Game.options[i])
					
			return ("Board", None)
		#界面还在调度中时
		elif self.UI == -1:
			for ID in range(1, 3):
				for i in range(len(self.posMulligans[ID])):
					if self.entityClicked(x, y, self.posMulligans[ID][i]):
						if self.mulliganStatus[ID][i] == 0:
							print("The card to mulligan is ", self.Game.mulligans[ID][i])
							self.mulliganStatus[ID][i] = 1
						else:
							print("Cancel mulligan: ", self.Game.mulligans[ID][i])
							self.mulliganStatus[ID][i] = 0
						return ("Mulligan", None)
						
			if self.entityClicked(x, y, EndMulliganPosition):
				return ("EndMulligan", None)
			else:
				return ("Board", None)
		#界面在主体选择过程中时
		elif self.UI == 0:
			if self.entityClicked(x, y, EndTurnPosition1) and self.Game.turn == 1:
				return ("EndTurn", None)
			elif self.entityClicked(x, y, EndTurnPosition2) and self.Game.turn == 2:
				return ("EndTurn", None)
			elif self.entityClicked(x, y, Hero1Position):
				return ("Hero 1", self.Game.heroes[1])
			elif self.entityClicked(x, y, Hero2Position):
				return ("Hero 2", self.Game.heroes[2])
			elif self.entityClicked(x, y, HeroPower1Position):
				return ("Hero Power 1", self.Game.heroPowers[1])
			elif self.entityClicked(x, y, HeroPower2Position):
				return ("Hero Power 2", self.Game.heroPowers[2])
			elif self.entityClicked(x, y, Weapon1Position):
				return ("Weapon 1", self.Game.availableWeapon(1))
			elif self.entityClicked(x, y, Weapon2Position):
				return ("Weapon 2", self.Game.availableWeapon(2))
			else:
				for ID in range(1, 3):
					for i in range(len(self.posMinionsDrawn[ID])):
						if self.entityClicked(x, y, self.posMinionsDrawn[ID][i]):
							return ("MiniononBoard", self.Game.minions[ID][i])
					for j in range(len(self.posHands[ID])):
						if self.entityClicked(x, y, self.posHands[ID][j]):
							if self.Game.Hand_Deck.hands[ID][j].cardType == "Minion":
								return ("MinioninHand", self.Game.Hand_Deck.hands[ID][j])
							if self.Game.Hand_Deck.hands[ID][j].cardType == "Spell":
								return ("SpellinHand", self.Game.Hand_Deck.hands[ID][j])
							if self.Game.Hand_Deck.hands[ID][j].cardType == "Weapon":
								return ("WeaponinHand", self.Game.Hand_Deck.hands[ID][j])
							if self.Game.Hand_Deck.hands[ID][j].cardType == "Hero":
								return ("HeroinHand", self.Game.Hand_Deck.hands[ID][j])
								
				if self.entityClicked(x, y, BoardPosition):
					return ("Board", None)
					
				return ("", None)
		else: #在主体已经选定的情况下选择打出位置和目标的过程中	
			if self.entityClicked(x, y, Hero1Position):
				return ("Hero 1", self.Game.heroes[1])
			elif self.entityClicked(x, y, Hero2Position):
				return ("Hero 2", self.Game.heroes[2])
			else:
				for ID in range(1, 3):
					for i in range(len(self.posMinionsDrawn[ID])):
						if self.entityClicked(x, y, self.posMinionsDrawn[ID][i]):
							return ("MiniononBoard", self.Game.minions[ID][i])
							
				if self.entityClicked(x, y, BoardPosition):
					return ("Board", None)
					
				return ("", None)
				
	def shutDown(self, comment):
		self.gameOver = True
		exit()
		
	def cancelSelection(self):
		self.subject = None
		self.target = None
		self.choice = -1
		self.selectedSubject = ""
		self.position = -1
		self.threadEvent = None
		#self.UI = 0 for subject selection.
		#self.UI = 1 for choose One selection
		#self.UI = 2 for target/position selection
		#self.UI = 3 for discovering.
		self.UI = 0
		
	def run(self):
		print("The GUI is intialized and the Game starts running.")
		running = True
		while running:
			if self.gameOver:
				running = False
				quit()
				
			pygame.time.delay(Refresh_rate)
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					running = False
					quit()
					
			ID = self.Game.turn
			#self.UI = 0: nothing selected yet.
			#1: Choose One option selection.
			#2: selecting target or position to play Minion/Spell/Weapon/Hero
			#3: discovering.
			mouse_events = pygame.mouse.get_pressed()
			pos = pygame.mouse.get_pos()
			#起手调度界面
			if self.UI == -1:#For mulligan
				if mouse_events[0]:
					item = self.scanClicked(pos)
					if item[0] == "EndMulligan":
						self.UI = 0
						indicesCards1 = []
						indicesCards2 = []
						for i in range(len(self.mulliganStatus[1])):
							if self.mulliganStatus[1][i]:
								indicesCards1.append(i)
						for i in range(len(self.mulliganStatus[2])):
							if self.mulliganStatus[2][i]:
								indicesCards2.append(i)
						print("Have decided cards to mulligan.")
						print("Player 1 will replace the following cards", indicesCards1)
						print("Player 2 will replace the following cards", indicesCards2)
						self.Game.Hand_Deck.mulligan(indicesCards1, indicesCards2)
			#主体选择: 打出的牌、英雄技能和攻击者。
			elif self.UI == 0: #Selecting subject.
				if mouse_events[2]: #点击鼠标右键打印该实体目前的状态。
					if "Minion" in item[0] or "Hero" in item[0] or "Spell" in item[0] or "Weapon" in item[0] or "Hero Power" in item[0]:
						print("Right click to see the status of the selected entity ", item[1])
						item[1].statusPrint()
						self.cancelSelection()
				elif mouse_events[0]: #鼠标点击左键。
					item = self.scanClicked(pos) #Selecting subject
					if item[0] == "Board" or item[0] == "": #Weapon won't be detected by scanClicked()
						print("Board is not a valid subject.")
						self.cancelSelection()
					elif item[1] != None and item[1].ID != ID:
						print("You can only select your own characters as subject.")
						self.cancelSelection()
					elif item[0] == "EndTurn": #无论当前选择如何，点击到回合结束即终止回合。
						self.cancelSelection()
						self.Game.switchTurn()
					elif item[0] == "Weapon 1" or item[0] == "Weapon 2":
						print("You can't select the weapon as subject.")
					else: #选择的是我方手牌、我方英雄、我方英雄技能、我方场上随从，
						self.subject = item[1]
						self.target = None
						self.selectedSubject = item[0]
						self.UI = 2 #选择了主体目标，则准备进入选择打出位置或目标界面。抉择法术可能会将界面导入抉择界面。
						self.choice = 0
						print("Selected ", item[0], item[1])
						#Decide if the subject selected is viable. If not, cancel the selection.
						if "inHand" in item[0]: #选择了手牌中的卡
							if item[1].mana > self.Game.ManaHandler.manas[ID]:
								print("No enough mana to play card")
								self.cancelSelection()
							else: #除了法力值不足，然后是指向性法术没有合适目标和随从没有位置使用
								#If the card in hand is Choose One spell.
								if item[0] == "SpellinHand" and item[1].available() == False:
									#法术没有可选目标，或者是不可用的非指向性法术
									print("Selected spell unavailable. All selection canceled.")
									self.cancelSelection()
								elif item[0] == "MinioninHand" and self.Game.spaceonBoard(ID) < 1:
									print("The board is full and minion selected can't be played")
									self.cancelSelection()
								else:
									if item[1].chooseOne > 0:
										if self.Game.playerStatus[item[1].ID]["Choose Both"] > 0:
											self.choice = "ChooseBoth" #跳过抉择，直接进入UI=1界面。
										else:
											self.Game.options = item[1].options
											self.UI = 1 #进入抉择界面，退出抉择界面的时候已经self.choice已经选好。
						#不需目标的英雄技能当即使用。需要目标的进入目标选择界面。
						elif "Hero Power" in item[0]:
							#英雄技能会自己判定是否可以使用。
							if item[1].available() == False:
								print("Hero Power not available.")
								self.cancelSelection()
							else:
								if item[1].needTarget(): #selectedSubject之前是"Hero Power 1"或者"Hero Power 2"
									self.selectedSubject = "Hero Power"
								else:
									print("Request to use Hero Power ", self.subject.name)
									subject = self.subject
									self.cancelSelection()
									subject.use(None) #Whether the Hero Power is used or not is handled in the use method.
						#不能攻击的随从不能被选择。
						elif item[0] == "MiniononBoard" or "Hero" in item[0]:
							if item[1].canAttack() == False:
								print("Selected character can't attack.")
								self.cancelSelection()
			#抉择界面。			
			elif self.UI == 1: #Choose One
				if mouse_events[2]: #鼠标右键取消选择，退回原始的UI=0的主体选择界面。
					print("Selection canceled.")
					self.cancelSelection()
				elif mouse_events[0]: #鼠标左键选择选项。
					item = self.scanClicked(pos)
					if item[0] != "Choose":
						print("You must click an option to continue.")
					else:
						if item[1].available():
							#The first option is indexed as 0.
							for i in range(len(self.Game.options)):
								if item[1] == self.Game.options[i]:
									print("Choice %s chosen"%self.Game.options[i].name)
									self.choice = i
									self.UI = 2 #选项已准备好，进入目标或打出位置选择界面选择界面
									break
			#随从的打出位置选择和目标选择
			elif self.UI == 2: #self.UI = 2
				if mouse_events[2]: #点击鼠标右键以取消选择。
					print("All selection canceled.")
					self.cancelSelection()
				elif mouse_events[0]: #点击鼠标左键。
					item = self.scanClicked(pos)
					self.target = item[1]
					print("Selected target: ", item[1])
					#No matter what the selections are, pressing EndTurn button ends the turn.
					#选择的主体是场上的随从或者英雄。之前的主体在UI=0的界面中已经确定一定是友方角色。
					if self.selectedSubject == "MiniononBoard" or self.selectedSubject == "Hero 1" or self.selectedSubject == "Hero 2":
						if "Hero" not in item[0] and item[0] != "MiniononBoard":
							print("Invalid target for minion attack.")
						else:
							print("Requesting battle: %s attacks %s"%(self.subject.name, item[1]))
							subject = self.subject
							target = self.target
							self.cancelSelection()
							self.Game.battleRequest(subject, target)
					#手中选中的随从在这里结算打出位置，如果不需要目标，则直接打出。
					elif self.selectedSubject == "MinioninHand":
						if item[0] == "Board" or (item[0] == "MiniononBoard" and item[1].ID == ID):
							if item[0] == "Board":
								self.position = -1
							else:
								self.position = item[1].position
							
							print("Position for minion in hand decided: ", self.position)
							self.selectedSubject = "MinionPositionDecided" #将主体记录为标记了打出位置的手中随从。
							#抉择随从如有全选光环，且所有选项不需目标，则直接打出。 连击随从的needTarget()由连击条件决定。
							print("Does the selected minion %s in hand need target: "%self.subject.name, self.subject.needTarget(self.choice))
							if self.subject.needTarget(self.choice) == False or self.subject.targetExists(self.choice) == False:
								print("Requesting to play minion %s without target. The choice is "%self.subject.name, self.choice)
								subject, position, choice = self.subject, self.position, self.choice
								self.cancelSelection()
								self.Game.playMinion(subject, None, position, choice)
							else:
								print("The minion requires target to play. needTarget() returns", self.subject.needTarget(self.choice))
					#随从的打出位置和抉择选项已经在上一步选择，这里处理目标选择。
					elif self.selectedSubject == "MinionPositionDecided":
						if "Hero" not in item[0] and item[0] != "MiniononBoard": #指定目标时必须是英雄或者场上随从
							print("Board is not a valid option. All selections canceled.")
						else:
							print("Requesting to play minion %s, targeting %s with choice: "%(self.subject.name, item[1].name), self.choice)
							subject, position, choice = self.subject, self.position, self.choice
							self.cancelSelection()
							self.Game.playMinion(subject, item[1], position, choice)
					#选中的法术已经确定抉择选项（如果有），下面决定目标选择。
					elif self.selectedSubject == "SpellinHand":
						if self.subject.needTarget(self.choice) == False:
							if item[0] == "Board":
								print("Requesting to play spell %s without target. The choice is "%self.subject.name, self.choice)
								subject, target, choice = self.subject, None, self.choice
								self.cancelSelection()
								self.Game.playSpell(subject, target, choice)
						else: #法术或者法术抉择选项需要指定目标。
							if "Hero" not in item[0] and item[0] != "MiniononBoard":
								print("Targeting spell must be cast on Hero or Minion on board.")
							else:
								print("Requesting to play spell %s with target %s. The choice is "%(self.subject.name, item[1]), self.choice)
								subject, target, choice = self.subject, item[1], self.choice
								self.cancelSelection()
								self.Game.playSpell(subject, target, choice)
					#选择手牌中的武器的打出目标
					elif self.selectedSubject == "WeaponinHand":
						if self.subject.needTarget == False:
							if item[0] == "Board":
								print("Requesting to play Weapon %s"%self.subject.name)
								subject, target = self.subject, None
								self.cancelSelection()
								self.Game.playWeapon(subject, None)
						else:
							if "Hero" not in item[0] and item[0] != "MiniononBoard":
								print("Targeting weapon must be played with a target.")
							else:
								subject, target = self.subject, item[1]
								print("Requesting to play weapon %s with target"%subject.name, target.name)
								self.cancelSelection()
								self.Game.playWeapon(subject, target)
								
					#手牌中的英雄牌是没有目标的
					elif self.selectedSubject == "HeroinHand":
						if item[0] == "Board":
							print("Requesting to play hero card", self.subject.name)
							subject = self.subject
							self.cancelSelection()
							self.Game.playHero(subject)
					#Select the target for a Hero Power.
					#在此选择的一定是指向性的英雄技能。
					elif self.selectedSubject == "Hero Power": #如果需要指向的英雄技能对None使用，HeroPower的合法性检测会阻止使用。
						if "Hero" not in item[0] and item[0] != "MiniononBoard":
							print("Targeting hero power must be used with a target.")
						else:
							print("Requesting to use Hero Power %s on "%self.subject.name, item[1].name)
							subject = self.subject
							self.cancelSelection()
							subject.use(item[1]) #Request to use the Hero Power, and its validity is decided later.
			#发现界面。
			#elif self.UI == 3: #Discovering
			#	if mouse_events[0]: #鼠标左键选择发现选项
			#		item = self.scanClicked(pos)
			#		if item[0] != "Choose":
			#			print("You must click an option to finish the discover.")
			#		else:
			#			self.Game.option = item[1]
			#			self.UI = 0
			#			self.Game.discoverInitiator.discoverDecided = True
			#			
			self.update()
			
GameGUI = GUI()
GameGUI.run()