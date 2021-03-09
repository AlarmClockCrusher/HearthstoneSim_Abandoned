from panda3d.core import *
from direct.interval.IntervalGlobal import Parallel, Func, Sequence

import inspect
import numpy as np

from LoadModels import *

Separation_Hands = 5
OpeningAngle = 70
radius = 9.5

class HandZone:
	def __init__(self, GUI, ID):
		self.GUI, self.ID, self.btnsDrawn = GUI, ID, []
		ownID = 1 if not hasattr(self.GUI, "ID") else self.GUI.ID  #1PGUI has virtual ID of 1
		self.x, self.y, self.z = 0, 50, -21.5 if self.ID == ownID else 22.5
		self.cardScale = 0.5
		
	def addCard(self, card, pos, hpr=Point3()):
		nodePath_Card = loadCard(self.GUI, card=card)
		nodePath_Card.setPos(pos)
		nodePath_Card.setHpr(hpr)
		nodePath_Card.pos, nodePath_Card.hpr = pos, hpr
		nodePath_Card.setScale(self.cardScale)
		self.btnsDrawn.append(nodePath_Card)
		self.GUI.pickablesDrawn.append(nodePath_Card)
		return nodePath_Card
	
	def removeCard(self, btn):
		btn.removeNode()
		try: self.GUI.pickablesDrawn.remove(btn)
		except: pass
		try: self.btnsDrawn.remove(btn)
		except: pass
		
	def draw(self):
		game, ownHand = self.GUI.Game, self.GUI.Game.Hand_Deck.hands[self.ID]
		handSize = len(ownHand)
		#print("Card in hand", ownHand)
		hprHands, posHands = [], []
		if handSize > 0:
			d_angle = min(12, OpeningAngle / handSize)
			if self.z < 0:
				leftAngle = -d_angle * (handSize - 1) / 2
				#leftPos = self.x - Separation_Hands * (len(ownHand) -1) / 2
				#posHands = [(leftPos+Separation_Hands*i, self.y-0.3*i, self.z) for i in range(len(ownHand))]
				#setHpr(h, p, r) rotation about the z axis, x axis, and y axis.
				for i in range(handSize):
					angleAboutY = leftAngle+i*d_angle
					hprHands.append((0, 0, angleAboutY))
					posHands.append((self.x+radius*np.sin(np.pi*angleAboutY/180), self.y-i*0.15,
										self.z+radius*np.cos(np.pi*angleAboutY/180)))
			else:
				leftAngle = d_angle * (handSize - 1) / 2
				for i in range(handSize):
					angleAboutY = leftAngle-i*d_angle
					hprHands.append((0, 0, angleAboutY+180))
					posHands.append((self.x-radius*np.sin(np.pi*angleAboutY/180), self.y+i*0.15,
										self.z-radius*np.cos(np.pi*angleAboutY/180)))
		#Watch for the inclusion of the btnsDrawn and the GUI.pickablesDrawn
		if self.btnsDrawn:
			#print("In draw(), hand btns to draw and their original pos and hpr")
			#for btn in self.btnsDrawn:
			#	print('\t', btn, btn.pos, btn.hpr)
			#Find the positions and hprs for each of the cards already existing in btnsDrawn, destroy others
			pos_hpr_4Existing = {} #{btn: (pos, hpr)} the pos and hpr for the btn already drawn that still is in hand
			pos_hpr_4New = {} #{card: (pos, hpr)} the pos and hpr for the card that hasn't been drawn yet
			btns2Destroy = [] #Btns for cards that aren't in hand any more should be destroyed
			for ind, btn in enumerate(self.btnsDrawn):
				#If a btn holds a card still in hand, keep it and register its new pos and hpr
				#otherwise, register it to be destroyed
				i = next((i for i, card in enumerate(ownHand) if card == btn.card), -1)
				if i > -1:
					pos_hpr_4Existing[btn] = (posHands[i], hprHands[i])
				else: btns2Destroy.append(btn)
			for i, card in enumerate(ownHand):
				#If can't find a btn that has the card in hand, register it to be drawn
				if not next((card for btn in self.btnsDrawn if card == btn.card), None):
					pos_hpr_4New[card] = (posHands[i], hprHands[i])
			for btn in btns2Destroy:
				self.removeCard(btn)
			#if pos_hpr_4New: #If there is new card to be drawn, draw them and highlight for half a second
			if pos_hpr_4Existing:
				#print("Moving existing cards in hand", pos_hpr_4Existing)
				para_MoveCards = Parallel(name="Move Cards %d"%self.ID)
				for btn, pos_hpr in pos_hpr_4Existing.items():
					posInterval, hprInterval = btn.genMoveIntervals(pos_hpr[0], pos_hpr[1], duration=0.3)
					para_MoveCards.append(posInterval)
					para_MoveCards.append(hprInterval)
				self.GUI.tryInitIntervals(para_MoveCards)
				#for btn in self.btnsDrawn: print('\t', btn, btn.getPos(), btn.getHpr())
			for card, pos_hpr in pos_hpr_4New.items():
				self.addCard(card, pos_hpr[0], pos_hpr[1])
		else: #When there isn't any hand card drawn yet
			for pos, hpr, card in zip(posHands, hprHands, ownHand):
				self.addCard(card, pos, hpr)
		for btn in self.btnsDrawn: btn.refresh()
		#print("After drawing hand, the buttons are", self.btnsDrawn)


HeroZone1_X, HeroZone2_X = 0.07, 0.08
HeroZone_Y = 51.3
HeroZone1_Z, HeroZone2_Z = -6.87, 7.84

class HeroZone(NodePath):
	def __init__(self, GUI, ID):
		super().__init__("NodePath_HeroZone")
		self.reparentTo(GUI.render)
		self.GUI, self.ID, self.btnsDrawn = GUI, ID, []
		ownID = 1 if not hasattr(self.GUI, "ID") else self.GUI.ID  #1PGUI has virtual ID of 1
		if self.ID == ownID:
			self.x, self.y, self.z = HeroZone1_X, HeroZone_Y, HeroZone1_Z
		else:
			self.x, self.y, self.z = HeroZone2_X, HeroZone_Y, HeroZone2_Z
		self.setPos(self.x, self.y, self.z)
		#filePath = "Models\\BoardModels\\HeroHolder_1.glb" if self.ID == ownID else "Models\\BoardModels\\HeroHolder_2.glb"
		#self.frame_Model = GUI.loader.loadModel(filePath)
		#self.frame_Model.reparentTo(self.GUI.render)
		#self.frame_Model.setPos(0, self.y+0.1, 0)
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
		
		self.manasDrawn = []
	
	def addCard(self, card, pos=Point3(0, 0, 0), hpr=Point3()):
		loadFunc, scale = {"Hero": (loadHero_Played, 0.95), "Power": (loadPower_Played, 0.6), "Weapon": (loadWeapon_Played, 0.5)}[card.type]
		nodePath_Card = loadFunc(self.GUI, card=card)
		nodePath_Card.setPos(pos)
		nodePath_Card.setHpr(hpr)
		nodePath_Card.pos, nodePath_Card.hpr = pos, hpr
		nodePath_Card.setScale(scale)
		self.btnsDrawn.append(nodePath_Card)
		self.GUI.pickablesDrawn.append(nodePath_Card)
		return nodePath_Card
	
	def draw(self):
		game = self.GUI.Game
		hero, power, weapon = game.heroes[self.ID], game.powers[self.ID], game.availableWeapon(self.ID)
		if self.btnsDrawn:
			pass
		else:
			#Draw the hero, power and weapon, if applicable
			self.addCard(hero, Point3(self.x, self.y, self.z))
			self.addCard(power, Point3(self.x+4.5, self.y-0.1, self.z))
			if weapon: self.addCard(weapon, Point3(self.x-4.5, self.y-0.2, self.z))

	def drawMana(self):
		ID = self.ID
		usable, upper = self.manaHD.manas[ID], self.manaHD.manasUpper[ID]
		locked, overloaded = self.manaHD.manasLocked[ID], self.manaHD.manasOverloaded[ID]
		#print("usable, upper", usable, upper)
		self.manaText.setText("%d/%d"%(usable, upper))
		if self.z < 0:
			for btn in self.manasDrawn: btn.removeNode()
			self.manasDrawn.clear()
			manas2Draw = ["Mana"] * usable + ["EmptyMana"] * (upper - usable - locked) + ["LockedMana"] * locked
			for i, manaText in enumerate(manas2Draw):
				mana_Model = self.GUI.loader.loadModel("Models\\BoardModels\\%s.glb"%manaText)
				mana_Model.reparentTo(self)
				if manaText == "Mana":
					mana_Model.setTexture(mana_Model.findTextureStage('*'),
							self.GUI.loader.loadTexture("Models\\BoardModels\\ManaExample.png"), 1)
				elif manaText == "LockedMana":
					mana_Model.setTexture(mana_Model.findTextureStage('*'),
										  self.GUI.loader.loadTexture("Models\\BoardModels\\LockedMana.png"), 1)
				mana_Model.setPos(0.8*i, 0.1, 0)
				self.manasDrawn.append(mana_Model)
			for i in range(overloaded):
				mana_Model = self.GUI.loader.loadModel("Models\\BoardModels\\OverloadedMana.glb")
				mana_Model.reparentTo(self)
				mana_Model.setTexture(mana_Model.findTextureStage('*'),
									  self.GUI.loader.loadTexture("Models\\BoardModels\\LockedMana.png"), 1)
				mana_Model.setPos(upper-0.8*i-1 , 0.1, 0.05)
				self.manasDrawn.append(mana_Model)
			
		
#Used for secrets and quests
class NodePath_Secret(NodePath):
	def __int__(self, GUI, card):
		super().__init__(card.name+"_NodePath_Secret")
		self.reparentTo(GUI.render)
		
		self.card = card
		self.selected = False
		self.GUI = GUI
		self.card_Model = GUI.loader.loadModel("Models\\SecretIcon.glb")
		self.cardText = TextNode("?")
		self.cardText.setText('?')
		self.pos, self.hpr = Point3(), Point3()
		
		collNode_Card = CollisionNode("%s_c_node"%card.name)
		collNode_Card.addSolid(CollisionSphere(0, 0, 0, 1))
		node = self.attachNewNode(collNode_Card)
		node.show()
		
	def refresh(self):
		if self.card.ID == self.GUI.Game.turn:
			self.card_Model.setColor((0, 0, 0, 1))
			self.cardText.setTextColor((0.3, 0.3, 0.3, 1))
		else:
			color = {"Hunter": (0.353, 0.510, 0.192, 1), "Mage": (0.867, 0.212, 0.808, 1),
					 "Paladin": (0.973, 0.894, 0.271), "Rogue": (0.271, 0.271, 0.271, 1)}[self.card.Class]
			self.card_Model.setColor(color)
			self.cardText.setTextColor((1, 1, 1, 1))
			
			
class SecretZone:
	def __init__(self, GUI, ID):
		self.GUI, self.ID, self.btnsDrawn = GUI, ID, []
		ownID = 1 if not hasattr(self.GUI, "ID") else self.GUI.ID
		self.x, self.y, self.z = 0, 51, HeroZone1_Z+1.5 if self.ID == ownID else HeroZone2_Z+1.5
		
	def addCard(self, card, pos):
		nodePath_Secret = NodePath_Secret(self.GUI, card=card)
		nodePath_Secret.setPos(pos)
		nodePath_Secret.pos = pos
		#nodePath_Secret.setScale(0.6)
		self.btnsDrawn.append(nodePath_Secret)
		self.GUI.pickablesDrawn.append(nodePath_Secret)
		return nodePath_Secret

	def draw(self):
		secretHD = self.GUI.Game.Secrets
		ownSecrets = secretHD.mainQuests[self.ID] + secretHD.sideQuests[self.ID] + secretHD.secrets[self.ID]
		posSecrets = [(0, self.y, self.z+1), (-1.5, self.y, self.z), (1.5, self.y, self.z), (-2, self.y, self.z-1), (2, self.y, self.z-1)][:len(ownSecrets)]
		if self.btnsDrawn:
			pass
		else:
			for pos, card in zip(posSecrets, ownSecrets):
				self.addCard(card, pos)


Separation_Minions = 3.5
BoardZone_Y = HeroZone_Y

class BoardZone:
	def __init__(self, GUI, ID):
		self.GUI, self.ID, self.btnsDrawn = GUI, ID, []
		ownID = 1 if not hasattr(self.GUI, "ID") else self.GUI.ID  #1PGUI has virtual ID of 1
		self.x, self.y, self.z = 0, BoardZone_Y, -1.3 if self.ID == ownID else 3.2
		self.cardScale = 0.58
	
	def addCard(self, card, pos):
		nodePath_Card = loadMinion_Played(self.GUI, card=card)
		nodePath_Card.setPos(pos)
		nodePath_Card.pos = pos
		nodePath_Card.setScale(self.cardScale)
		self.btnsDrawn.append(nodePath_Card)
		self.GUI.pickablesDrawn.append(nodePath_Card)
		return nodePath_Card
	
	def removeCard(self, btn):
		btn.removeNode()
		try: self.GUI.pickablesDrawn.remove(btn)
		except: pass
		try: self.btnsDrawn.remove(btn)
		except: pass
	
	def draw(self):
		game, ownMinions = self.GUI.Game, self.GUI.Game.minions[self.ID]
		leftPos = self.x - Separation_Minions * (len(ownMinions) - 1) / 2
		posMinions = [(leftPos + Separation_Minions * i, self.y, self.z) for i in range(len(ownMinions))]
		#Watch for the inclusion of the btnsDrawn and the GUI.pickablesDrawn
		if self.btnsDrawn:
			#Find the positions and hprs for each of the cards already existing in btnsDrawn, destroy others
			pos_4Existing = {}  #{btn: (pos, hpr)} the pos and hpr for the btn already drawn that still is in hand
			pos_4New = {}  #{card: (pos, hpr)} the pos and hpr for the card that hasn't been drawn yet
			btns2Destroy = []  #Btns for cards that aren't in hand any more should be destroyed
			for ind, btn in enumerate(self.btnsDrawn):
				#If a btn holds a card still in hand, keep it and register its new pos and hpr
				#otherwise, register it to be destroyed
				i = next((i for i, card in enumerate(ownMinions) if card == btn.card), -1)
				if i > -1:
					pos_4Existing[btn] = posMinions[i]
				else:
					btns2Destroy.append(btn)
			for i, card in enumerate(ownMinions):
				#If can't find a btn that has the card in hand, register it to be drawn
				if not next((card for btn in self.btnsDrawn if card == btn.card), None):
					pos_4New[card] = posMinions[i]
			for btn in btns2Destroy: self.removeCard(btn)
			#if pos_hpr_4New: #If there is new card to be drawn, draw them and highlight for half a second
			if pos_4Existing:
				para_MoveCards = Parallel(name="Move Cards")
				for btn, pos in pos_4Existing.items():
					para_MoveCards.append(btn.genMoveIntervals(pos, hpr=Point3(), duration=0.2)[0])
				self.GUI.tryInitIntervals(para_MoveCards)
			#para_MoveCards.start()  #Move the cards first, then draw the cards previously missing
			for card, pos in pos_4New.items():
				self.addCard(card, pos)
		else:  #When there isn't any hand card drawn yet
			for pos, card in zip(posMinions, ownMinions):
				self.addCard(card, pos)
		for btn in self.btnsDrawn: btn.refresh()
	
	def rearrange(self):
		pass



Board_Y = HeroZone_Y + 0.2

class Board(NodePath):
	def __init__(self, GUI):
		super().__init__("Board")
		self.reparentTo(GUI.render)
		
		self.pos = Point3(0, 51.4, 0)
		self.setPos(self.pos)
		self.GUI = GUI
		self.selected = False
		self.card = None #Just a placeholder
		
		self.board_Model = GUI.loader.loadModel("Models\\BoardModels\\Background.glb")
		self.board_Model.reparentTo(self)
		self.board_Model.setTexture(self.board_Model.findTextureStage('*'),
								self.GUI.loader.loadTexture("Models\\BoardModels\\%s.png"%self.GUI.boardID), 1)
		collNode_Board = CollisionNode("Board_c_node_1")
		collNode_Board.addSolid(CollisionBox(Point3(0, 0.3, 0.5), 12, 0.2, 4.5))
		self.attachNewNode(collNode_Board).show()
		collNode_Board = CollisionNode("Board_c_node_2")
		collNode_Board.addSolid(CollisionBox(Point3(10.5, 0.3, 0), 4.2, 0.2, 9))
		self.attachNewNode(collNode_Board).show()
		collNode_Board = CollisionNode("Board_c_node_3")
		collNode_Board.addSolid(CollisionBox(Point3(-10.5, 0.53, 0), 4.2, 0.2, 9))
		self.attachNewNode(collNode_Board).show()
		
	def leftClick(self):
		if -1 < self.GUI.UI < 3:  #不在发现中和动画演示中才会响应
			self.GUI.resolveMove(None, self, "Board")
	
	def rightClick(self):
		pass

	def setColor(self, color):
		color = colorDict[color]
		self.board_Model.setColor(color[0], color[1], color[2], color[3])
	
	def dimDown(self):
		pass
	
	def mouseHoveringOver(self):
		pass
	
	def removeSpecsDisplay(self):
		pass
		
		
class TurnEndButton(NodePath):
	def __init__(self, GUI):
		super().__init__("Turn_End_Button")
		self.reparentTo(GUI.render)
		self.GUI = GUI
		self.curTurn = 1
		self.angle = 0
		self.card = None  #Just a placeholder
		
		self.model = GUI.loader.loadModel("Models\\BoardModels\\TurnEndButton.glb")
		self.model.reparentTo(self)
		self.model.setTexture(self.model.findTextureStage('*'),
					self.GUI.loader.loadTexture("Models\\BoardModels\\TurnEndButton.png"), 1)
	
		sansBold = GUI.loader.loadFont('Models\\OpenSans-Bold.ttf')
		
		collNode_TurnEndButton = CollisionNode("TurnEndButton_c_node")
		collNode_TurnEndButton.addSolid(CollisionBox(Point3(0, 0 , 0), 1.7, 0.4, 1))
		self.attachNewNode(collNode_TurnEndButton)#.show()
		
	def setColor(self, color):
		color = colorDict[color]
		self.model.setColor(color[0], color[1], color[2], color[3])
		
	def leftClick(self):
		GUI = self.GUI
		if 3 > GUI.UI > -1:
			self.rotate()
			GUI.resolveMove(None, self, "TurnEnds")
			GUI.update()
			if self.curTurn != GUI.Game.turn: self.curTurn = 3 - self.curTurn
			else: self.rotate()
	
	def rightClick(self):
		pass
	
	def rotate(self):
		hprInterval = self.hprInterval(0.4, (0, 180-self.angle, 0), startHpr=(0, self.angle, 0))
		self.angle = 180 - self.angle
		self.GUI.tryInitIntervals(Parallel(hprInterval, name="Turn End Button Rotate"))
		
	def dimDown(self):
		pass
	
	def mouseHoveringOver(self):
		pass
	
	def removeSpecsDisplay(self):
		pass


class DeckZone:
	def __init__(self, GUI, ID):
		self.GUI, self.ID, self.btnsDrawn = GUI, ID, []
		ownID = 1 if not hasattr(self.GUI, "ID") else self.GUI.ID  #1PGUI has virtual ID of 1
		self.x, self.y, self.z = 15, 49, -8 if self.ID == ownID else 8
		self.cardScale = 0.5
	
	