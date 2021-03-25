import numpy as np
from direct.interval.IntervalGlobal import Parallel, Sequence, Func
from datetime import datetime
import threading

from LoadModels import *

Separation_Hands = 5
OpeningAngle = 50
radius = 9.5
HandZone_Y = 50
HandZone1_Z, HandZone2_Z = -21.5, 22.5

def calc_PosHprHands(num, x, y, z):
	if num < 1: return [], []
	d_angle = min(12, int(OpeningAngle / num))
	posHands, hprHands = [], []
	if z < 0:
		leftAngle = -d_angle * (num - 1) / 2
		for i in range(num):
			angleAboutY = leftAngle+i*d_angle
			hprHands.append(Point3(0, 0, angleAboutY))
			posHands.append(Point3(x+radius*np.sin(np.pi*angleAboutY/180), y-i*0.15,
								z+radius*np.cos(np.pi*angleAboutY/180)))
	else:
		leftAngle = d_angle * (num - 1) / 2
		for i in range(num):
			angleAboutY = leftAngle-i*d_angle
			hprHands.append(Point3(0, 0, angleAboutY+180))
			posHands.append(Point3(x-radius*np.sin(np.pi*angleAboutY/180), y+i*0.15,
								z-radius*np.cos(np.pi*angleAboutY/180)))
	return posHands, hprHands

posHandsTable = {HandZone1_Z: {i: calc_PosHprHands(i, 0, HandZone_Y, HandZone1_Z)[0] for i in range(13)},
				HandZone2_Z: {i: calc_PosHprHands(i, 0, HandZone_Y, HandZone2_Z)[0] for i in range(13)}
				}
				
hprHandsTable = {HandZone1_Z: {i: calc_PosHprHands(i, 0, HandZone_Y, HandZone1_Z)[1] for i in range(13)},
				HandZone2_Z: {i: calc_PosHprHands(i, 0, HandZone_Y, HandZone2_Z)[1] for i in range(13)}
				}

handScale = 0.5

class HandZone:
	def __init__(self, GUI, ID):
		self.GUI, self.ID = GUI, ID
		ownID = 1 if not hasattr(self.GUI, "ID") else self.GUI.ID  #1PGUI has virtual ID of 1
		self.x, self.y, self.z = 0, HandZone_Y, HandZone1_Z if self.ID == ownID else HandZone2_Z
		
	def addaHand(self, card, pos, hpr=Point3(), scale=0.5):
		nodePath_Card = self.GUI.backupCardModels[card.type].popleft()
		nodePath_Card.changeCard(card)
		nodePath_Card.setPosHprScale(pos, hpr, Point3(scale, scale, scale))
		card.x, card.y, card.z = pos
		self.GUI.pickablesDrawn.append(nodePath_Card)
		return nodePath_Card
	
	def addHands(self, ls_Card, ls_Pos, ls_Hpr):
		if ls_Card:
			for card, pos, hpr in zip(ls_Card, ls_Pos, ls_Hpr):
				self.addaHand(card, pos, hpr)
				
	def removeMultiple(self, btns):
		for btn in btns:
			if btn not in self.GUI.backupCardModels[btn.card.type]:
				self.GUI.backupCardModels[btn.card.type].append(btn)
			if btn.card:
				if btn.card.btn is btn: btn.card.btn = None
				btn.card = None
			btn.setPos(BackupModelPos) #Move the btn to backup pos anyways
			#print("After removal, the btn is ", btn, btn.card, btn.getPos())
			try: self.GUI.pickablesDrawn.remove(btn)
			except: pass
			
	def draw(self, afterAllFinished=True, blockwhilePlaying=True):
		#print("Handzone start drawing hand:", self.ID)
		game, ownHand = self.GUI.Game, self.GUI.Game.Hand_Deck.hands[self.ID]
		posHands, hprHands = posHandsTable[self.z][len(ownHand)], hprHandsTable[self.z][len(ownHand)]
		pos_hpr_4Existing = {}  #{btn: (pos, hpr)} the pos and hpr for the btn already drawn that still is in hand
		pos_hpr_4New = {} #{card: (pos, hpr)} the pos and hpr for the card that hasn't been drawn yet
		for i, card in enumerate(ownHand):
			if card.btn in self.GUI.pickablesDrawn:
				pos_hpr_4Existing[card.btn] = (posHands[i], hprHands[i])
			else:
				pos_hpr_4New[card] = (posHands[i], hprHands[i])
		self.addHands(list(pos_hpr_4New.keys()), list(pos_hpr[0] for pos_hpr in pos_hpr_4New.values()), list(pos_hpr[1] for pos_hpr in pos_hpr_4New.values()))
		para = Parallel()
		#if pos_hpr_4New: #If there is new card to be drawn, draw them and highlight for half a second
		for btn, pos_hpr in pos_hpr_4Existing.items():
			para.append(btn.genMoveIntervals(pos_hpr[0], pos_hpr[1], duration=0.25))
		
		self.GUI.animate(para, name="Rearrange hand cards", afterAllFinished=afterAllFinished, blockwhilePlaying=blockwhilePlaying)
		#Multithreading takes ~2ms
		for card in ownHand:
			threading.Thread(target=card.btn.refresh).start()
		

HeroZone1_X, HeroZone2_X = 0.02, 0.08
HeroZone_Y = 51.3
HeroZone1_Z, HeroZone2_Z = -6.87, 7.84

posSecretsTable = {HeroZone1_Z: [Point3(HeroZone1_X, HeroZone_Y-0.2, HeroZone1_Z+2.4),
							Point3(HeroZone1_X-1, HeroZone_Y-0.2, HeroZone1_Z+1.8), Point3(HeroZone1_X+1, HeroZone_Y-0.2, HeroZone1_Z+1.8),
							Point3(HeroZone1_X-1.7, HeroZone_Y-0.2, HeroZone1_Z+1), Point3(HeroZone1_X+1.7, HeroZone_Y-0.2, HeroZone1_Z+1)],
			  HeroZone2_Z: [Point3(HeroZone2_X, HeroZone_Y-0.2, HeroZone2_Z+2),
							Point3(HeroZone2_X-1.2, HeroZone_Y-0.2, HeroZone2_Z+0.5), Point3(HeroZone2_X-1.2, HeroZone_Y-0.2, HeroZone2_Z+0.5),
							Point3(HeroZone2_X-1.5, HeroZone_Y-0.2, HeroZone2_Z+0.2), Point3(HeroZone2_X-1.5, HeroZone_Y-0.2, HeroZone2_Z+0.2)]
			  }

Seperation_Trigs = 1
def calc_posTrigs(num, x, y, z): #Input the x, y, z of the HeroZone
	leftPos = x - Seperation_Trigs * (num - 1) / 2
	posTrigs = [Point3(leftPos + Seperation_Trigs * i, y, z) for i in range(num)]
	return posTrigs

	
class HeroZone(NodePath):
	def __init__(self, GUI, ID):
		super().__init__("NodePath_HeroZone")
		self.reparentTo(GUI.render)
		self.GUI, self.ID = GUI, ID
		ownID = 1 if not hasattr(self.GUI, "ID") else self.GUI.ID  #1PGUI has virtual ID of 1
		if self.ID == ownID:
			self.x, self.y, self.z = HeroZone1_X, HeroZone_Y, HeroZone1_Z
		else:
			self.x, self.y, self.z = HeroZone2_X, HeroZone_Y, HeroZone2_Z
		self.setPos(self.x, self.y, self.z)
		sansBold = GUI.loader.loadFont('Models\\OpenSans-Bold.ttf')
		
		self.manaHD = GUI.Game.Manas
		#Merge the ManaZone with HeroZone
		self.manaText = TextNode("Mana Text")
		self.manaText.setText("0/0")
		self.manaText.setAlign(TextNode.ACenter)
		self.manaText.setFont(sansBold)
		manaTextNode = self.attachNewNode(self.manaText)
		manaTextNode.setScale(0.8)
		if self.z < 0: manaTextNode.setPos(7.2, -0.01, -4.15)
		else: manaTextNode.setPos(6.35, -0.01, 3.05)
		
		self.manasDrawn, self.secretsDrawn, self.trigsDrawn = [], [], []
		
	#Only for hero, power, weapon. Secrets will only use addSecrets
	def addaCard(self, card, pos=Point3(0, 0, 0), hpr=Point3()):
		scale = {"Hero": 0.95, "Power": 0.6, "Weapon": 0.5}[card.type]
		nodePath_Card = self.GUI.backupCardModels[card.type+"Played"].popleft()
		nodePath_Card.changeCard(card)
		nodePath_Card.setPosHprScale(pos, hpr, scale)
		if nodePath_Card not in self.GUI.pickablesDrawn:
			self.GUI.pickablesDrawn.append(nodePath_Card)
		return nodePath_Card
		
	def addSecrets(self, ls_Card, ls_Pos):
		if ls_Card:
			for card, pos in zip(ls_Card, ls_Pos):
				nodePath_Card = self.GUI.backupCardModels["SecretPlayed"].popleft()
				nodePath_Card.changeCard(card)
				if nodePath_Card not in self.GUI.pickablesDrawn:
					self.GUI.pickablesDrawn.append(nodePath_Card)
				nodePath_Card.setPos(pos)
				nodePath_Card.setScale(1.2)
				
	def removeHero(self, btn):
		btn.setPos(BackupModelPos)
		if btn not in self.GUI.backupCardModels["HeroPlayed"]:
			self.GUI.backupCardModels["HeroPlayed"].append(btn)
		if btn.card:
			if btn.card.btn is btn: btn.card.btn = None
			btn.card = None
		try: self.GUI.pickablesDrawn.remove(btn)
		except: pass
		
	def removePower(self, btn):
		btn.setPos(BackupModelPos)
		if btn not in self.GUI.backupCardModels["PowerPlayed"]:
			self.GUI.backupCardModels["PowerPlayed"].append(btn)
		if btn.card:
			if btn.card.btn is btn: btn.card.btn = None
			btn.card = None
		try: self.GUI.pickablesDrawn.remove(btn)
		except: pass
	
	def removeWeapon(self, btn):
		btn.setPos(BackupModelPos)
		if btn not in self.GUI.backupCardModels["WeaponPlayed"]:
			self.GUI.backupCardModels["WeaponPlayed"].append(btn)
		else: print("weapon btn false already in backupmodels")
		if btn.card:
			if btn.card.btn is btn: btn.card.btn = None
			btn.card = None
		try: self.GUI.pickablesDrawn.remove(btn)
		except: pass
	
	def draw(self, blockwhilePlaying=True):
		#The whole func takes ~1ms
		game = self.GUI.Game
		hero, power, weapon = game.heroes[self.ID], game.powers[self.ID], game.availableWeapon(self.ID)
		if hero.btn: threading.Thread(target=hero.btn.refresh).start()
		else:
			print("Redrawing hero", hero, hero.btn)
			self.addaCard(hero, Point3(self.x, self.y, self.z))
		#Changing power or drawing power for the 1st time requires the power to flip to face down
		x, y, z = self.x + 4.5, self.y - 0.1, self.z
		if power.btn: threading.Thread(target=power.btn.refresh).start()
		else:
			btn = self.addaCard(power, Point3(x, y, z))
			btn.setHpr(0, 0, 0)
			riseInterval = btn.genMoveIntervals(pos=Point3(x, y - 3, z), hpr=Point3(90, 0, 0), duration=0.2)
			dropInterval = btn.genMoveIntervals(pos=Point3(x, y, z), hpr=Point3(180, 0, 0), duration=0.2)
			flipInterval = btn.genMoveIntervals(hpr=Point3(360, 0, 0), duration=0.2)
			#新技能出现的时候一定都是可以使用的正面向上状态
			self.GUI.animate(Sequence(riseInterval, dropInterval, flipInterval, Func(btn.refresh)), name="Animate Power Appearing", blockwhilePlaying=False)
		if weapon:
			print("BEFORE DRAWING THE WEAPON BTN WHEN UPDATING, check the btns and nodePaths")
			for nodePath in self.GUI.render.findAllMatches("**/*_NodePath_WeaponPlayed*"):
				if nodePath.getPos() != BackupModelPos:
					print("\t\tWeaponPlayed nodePath being displayed", nodePath.name, nodePath.getPos())
			
			if weapon.btn: threading.Thread(target=weapon.btn.refresh).start()
			else: self.addaCard(weapon, Point3(self.x - 4.5, self.y - 0.2, self.z))
			
		for btn in self.GUI.backupCardModels["WeaponPlayed"]:
			if not btn.card: btn.setPos(BackupModelPos)
			
	def drawMana(self):
		ID = self.ID
		usable, upper = self.manaHD.manas[ID], self.manaHD.manasUpper[ID]
		locked, overloaded = self.manaHD.manasLocked[ID], self.manaHD.manasOverloaded[ID]
		#print("usable, upper", usable, upper)
		self.manaText.setText("%d/%d"%(usable, upper))
		if self.z < 0:
			for btn in self.manasDrawn: btn.setPos(0, -60, 0)
			self.manasDrawn = []
			manas2Draw = ["Mana"] * usable + ["EmptyMana"] * (upper - usable - locked) + ["LockedMana"] * locked
			for i, manaText in enumerate(manas2Draw):
				model = self.GUI.backupCardModels[manaText][i]
				model.setPos(0.8*i, 0.05, 0)
				self.manasDrawn.append(model)
			for i in range(locked):
				model = self.GUI.backupCardModels["OverloadedMana"][i]
				model.setPos(upper-0.8*i-1 , 0.05, 0)
				self.manasDrawn.append(model)
				
	def drawSecrets(self, blockwhilePlaying=True):
		secretHD = self.GUI.Game.Secrets
		ownSecrets = secretHD.mainQuests[self.ID] + secretHD.sideQuests[self.ID] + secretHD.secrets[self.ID]
		posSecrets = posSecretsTable[self.z][:len(ownSecrets)]
		pos_4Existing, pos_4New = {}, {}
		for i, card in enumerate(ownSecrets):
			if card.btn in self.GUI.pickablesDrawn:
				pos_4Existing[card.btn] = posSecrets[i]
			else:
				pos_4New[card] = posSecrets[i]
		self.addSecrets(list(pos_4New.keys()), list(pos_4New.values()))
		para = Parallel()
		for btn, pos in pos_4Existing.items():
			para.append(btn.genMoveIntervals(pos, duration=0.15))
		self.GUI.animate(para, name="Move secrets ani", blockwhilePlaying=blockwhilePlaying)
		for card in ownSecrets:
			threading.Thread(target=card.btn.refresh).start()
			
	def addaTrig(self, card):
		loader = self.GUI.loader
		imgPath = findFilepath(card)
		root_Trig = NodePath_TurnTrig(self.GUI, card)
		root_Trig.reparentTo(self.GUI.render)
		card.btn = root_Trig
		root_Trig.card_Model = loader.loadModel("Models\\HeroModels\\TurnTrig.glb")
		root_Trig.card_Model.setTexture(root_Trig.card_Model.findTextureStage('*'),
									loader.loadTexture(imgPath), 1)
		root_Trig.card_Model.reparentTo(root_Trig)
		self.rearrangeTrigs()
		
	def removeaTrig(self, btn):
		btn.card = None
		try: self.trigsDrawn.remove(btn)
		except: pass
		try: self.GUI.pickablesDrawn.remove(btn)
		except: pass
		btn.removeNode()
		cards = [trig.card for trig in self.GUI.Game.turnEndTrigger + self.GUI.Game.turnStartTrigger if trig.ID == self.ID]
		posTrigs = calc_posTrigs(len(cards), self.x, self.y, self.z)
		for i, card in enumerate(cards):
			card.btn.setPos(posTrigs[i])
			
	def rearrangeTrigs(self):
		cards = [trig.card for trig in self.GUI.Game.turnEndTrigger + self.GUI.Game.turnStartTrigger if trig.ID == self.ID]
		posTrigs = calc_posTrigs(len(cards), self.x, self.y-0.25, self.z-2.1)
		for i, card in enumerate(cards):
			card.btn.setPos(posTrigs[i])
			if card.btn not in self.trigsDrawn:
				self.trigsDrawn.append(card.btn)
			if card.btn not in self.GUI.pickablesDrawn:
				self.GUI.pickablesDrawn.append(card.btn)
		for btn in self.trigsDrawn[:]:
			if btn.card not in cards:
				btn.removeNode()
				self.trigsDrawn.remove(btn)
				try: self.GUI.pickablesDrawn.remove(btn)
				except: pass

Separation_Minions = 3.5
BoardZone_Y = HeroZone_Y
BoardZone1_Z, BoardZone2_Z = -1.05, 3.45

def calc_posMinions(num, x, y, z):
	leftPos = x - Separation_Minions * (num - 1) / 2
	posMinions = [Point3(leftPos + Separation_Minions * i, y, z) for i in range(num)]
	return posMinions

posMinionsTable = {BoardZone1_Z: {i: calc_posMinions(i, 0, BoardZone_Y, BoardZone1_Z) for i in range(15)},
				BoardZone2_Z: {i: calc_posMinions(i, 0, BoardZone_Y, BoardZone2_Z) for i in range(15)}
				}
	
minionScale = 0.58

class BoardZone:
	def __init__(self, GUI, ID):
		self.GUI, self.ID = GUI, ID
		ownID = 1 if not hasattr(self.GUI, "ID") else self.GUI.ID  #1PGUI has virtual ID of 1
		self.x, self.y, self.z = 0, BoardZone_Y, BoardZone1_Z if self.ID == ownID else BoardZone2_Z
		
	def addaMinion(self, card, pos):
		nodePath_Card = self.GUI.backupCardModels[card.type+"Played"].popleft()
		nodePath_Card.changeCard(card)
		if nodePath_Card not in self.GUI.pickablesDrawn:
			self.GUI.pickablesDrawn.append(nodePath_Card)
		nodePath_Card.setPos(pos)
		nodePath_Card.setScale(minionScale)
		return nodePath_Card
	
	def addMinions(self, ls_Card, ls_Pos):
		if ls_Card:
			if not isinstance(ls_Card, list): ls_Card = [ls_Card]
			if not isinstance(ls_Pos, list): ls_Pos = [ls_Pos]
			for card, pos in zip(ls_Card, ls_Pos):
				nodePath_Card = self.GUI.backupCardModels[card.type+"Played"].popleft()
				nodePath_Card.changeCard(card)
				if nodePath_Card not in self.GUI.pickablesDrawn:
					self.GUI.pickablesDrawn.append(nodePath_Card)
			for card, pos in zip(ls_Card, ls_Pos):
				card.x, card.y, card.z = pos
				card.btn.setPos(pos)
				card.btn.setScale(minionScale)
				
	def removeMinion(self, btn):
		btn.setPos(BackupModelPos)
		if btn not in self.GUI.backupCardModels["MinionPlayed"]:
			self.GUI.backupCardModels["MinionPlayed"].append(btn)
		if btn.card:
			if btn.card.btn is btn: btn.card.btn = None
			btn.card = None
		try: self.GUI.pickablesDrawn.remove(btn)
		except: pass
		
	def removeMultiple(self, btns):
		#print("pre removing multiple, own minion btns", [minion.btn for minion in self.GUI.Game.minions[self.ID]])
		for btn in btns:
			if btn not in self.GUI.backupCardModels["MinionPlayed"]:
				self.GUI.backupCardModels["MinionPlayed"].append(btn)
			if btn.card:
				if btn.card.btn is btn: btn.card.btn = None
				btn.card = None
			btn.setPos(BackupModelPos)
			try: self.GUI.pickablesDrawn.remove(btn)
			except: pass
			##except: pass
		#print("AFter removing, own minion btns", [minion.btn for minion in self.GUI.Game.minions[self.ID]])
		
	#It takes negligible time to finish calcing pos and actually start drawing
	def draw(self, blockwhilePlaying=True):
		#print("Start drawing minion zone", self.ID)
		game, ownMinions = self.GUI.Game, [minion for minion in self.GUI.Game.minions[self.ID] if minion.onBoard]
		#Pre-calculated and stored positions for the minions, based on the board location and minion number
		posMinions = posMinionsTable[self.z][len(ownMinions)]
		pos_4Existing = {}  #{btn: (pos, hpr)} the pos and hpr for the btn already drawn that still is in hand
		pos_4New = {}  #{card: (pos, hpr)} the pos and hpr for the card that hasn't been drawn yet
		print("Draw board zone, minions", ownMinions, [minion.btn for minion in ownMinions])
		for i, card in enumerate(ownMinions):
			if card.btn in self.GUI.pickablesDrawn:
				pos_4Existing[card.btn] = posMinions[i]
			else:
				pos_4New[card] = posMinions[i]
		self.addMinions(list(pos_4New.keys()), list(pos_4New.values()))
		para = Parallel()
		for btn, pos in pos_4Existing.items():
			para.append(btn.genMoveIntervals(pos, duration=0.2, blendType="easeOut"))
		self.GUI.animate(para, name="Move minions ani", blockwhilePlaying=blockwhilePlaying)
		for minion in ownMinions:
			threading.Thread(target=minion.btn.refresh).start()
		


Board_Y = HeroZone_Y + 0.2

class Board(NodePath):
	def __init__(self, GUI):
		super().__init__("Board")
		self.reparentTo(GUI.render)
		
		self.setPos(0, 51.4, 0)
		self.GUI = GUI
		self.selected = False
		self.card = None #Just a placeholder
		
		self.board_Model = GUI.loader.loadModel("Models\\BoardModels\\Background.glb")
		self.board_Model.reparentTo(self)
		self.board_Model.setTexture(self.board_Model.findTextureStage('*'),
								self.GUI.loader.loadTexture("Models\\BoardModels\\%s.png"%self.GUI.boardID), 1)
		collNode_Board = CollisionNode("Board_c_node_1")
		collNode_Board.addSolid(CollisionBox(Point3(0, 0.3, 0.5), 12, 0.2, 4.5))
		self.attachNewNode(collNode_Board)#.show()
		collNode_Board = CollisionNode("Board_c_node_2")
		collNode_Board.addSolid(CollisionBox(Point3(10.5, 0.3, 0), 4.2, 0.2, 9))
		self.attachNewNode(collNode_Board)#.show()
		collNode_Board = CollisionNode("Board_c_node_3")
		collNode_Board.addSolid(CollisionBox(Point3(-10.5, 0.53, 0), 4.2, 0.2, 9))
		self.attachNewNode(collNode_Board)#.show()
		
	def leftClick(self):
		if -1 < self.GUI.UI < 3:  #不在发现中和动画演示中才会响应
			self.GUI.resolveMove(None, self, "Board")
	
	def rightClick(self):
		self.GUI.cancelSelection()
		self.GUI.removeCardSpecsDisplay()
		
	def dimDown(self):
		self.setColor(grey)
	
	def setBoxColor(self, color):
		pass
	
	def removeSpecsDisplay(self):
		pass
		
		
class TurnEndButton(NodePath):
	def __init__(self, GUI):
		super().__init__("Turn_End_Button")
		self.reparentTo(GUI.render)
		self.GUI = GUI
		self.card = None  #Just a placeholder
		
		self.model = GUI.loader.loadModel("Models\\BoardModels\\TurnEndButton.glb")
		self.model.reparentTo(self)
		self.model.setTexture(self.model.findTextureStage('*'),
					self.GUI.loader.loadTexture("Models\\BoardModels\\TurnEndButton.png"), 1)
	
		collNode_TurnEndButton = CollisionNode("TurnEndButton_c_node")
		collNode_TurnEndButton.addSolid(CollisionBox(Point3(0, 0 , 0), 1.7, 0.4, 1))
		self.attachNewNode(collNode_TurnEndButton)#.show()
		
	def leftClick(self):
		GUI = self.GUI
		if 3 > GUI.UI > -1:
			GUI.resolveMove(None, self, "TurnEnds")
			
	def rightClick(self):
		self.GUI.cancelSelection()
	
	def dimDown(self):
		self.setColor(grey)
	
	def setBoxColor(self, color):
		pass
	
	def removeSpecsDisplay(self):
		pass


deckScale = 0.5

class DeckZone:
	def __init__(self, GUI, ID):
		self.GUI, self.ID = GUI, ID
		ownID = 1 if not hasattr(self.GUI, "ID") else self.GUI.ID  #1PGUI has virtual ID of 1
		self.x, self.y, self.z = 16, HeroZone_Y - 0.2, -2.25 if self.ID == ownID else 4.55
		self.decksinGame = self.GUI.Game.Hand_Deck.decks
		self.deckModel = None
		
	def draw(self):
		deckSize = len(self.decksinGame[self.ID])
		if self.deckModel:
			if deckSize < 1:
				self.deckModel.setColor(transparent)
			else:
				self.deckModel.setScale(0.5, 0.5*min(15, deckSize), 0.5)
		elif not self.deckModel and deckSize > 0:
			self.deckModel = self.GUI.loader.loadModel("Models\\CardBack.glb")
			self.deckModel.reparentTo(self.GUI.render)
			self.deckModel.setTransparency(True)
			self.deckModel.setPos(self.x, self.y, self.z)
			self.deckModel.setScale(0.5, 0.5*min(15, deckSize), 0.5)
			self.deckModel.setHpr(90, 0, 90)
			
	def rightClick(self):
		if self.GUI.UI == 0:
			self.GUI.showTempText("Deck size: {}\nHand size: {}".format(len([self.ID]),
																		len(self.GUI.Game.Hand_Deck.hands[self.ID])))

