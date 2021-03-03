from direct.gui.OnscreenText import OnscreenText
from direct.gui.DirectGui import *
from direct.showbase.ShowBase import ShowBase
from panda3d.core import *
from direct.interval.IntervalGlobal import Sequence, Func, Wait

import simplepbr

from Game import *
from Code2CardList import *
from GenerateRNGPools import *
from Panda_CustomWidgets import *

CHN = True

configVars = """
win-size 1440 900
window-title Deck Builder
clock-mode limited
clock-frame-rate 45
text-use-harfbuzz true
"""

loadPrcFileData('', configVars)

ClassDict = {'Demon Hunter': Illidan, 'Druid': Malfurion, 'Hunter': Rexxar, 'Mage': Jaina, 'Paladin': Uther,
			 'Priest': Anduin, 'Rogue': Valeera, 'Shaman': Thrall, 'Warlock': Guldan, 'Warrior': Garrosh, }


mulliganCard_Y = 40

class GUI_IP(ShowBase):
	def __init__(self):
		ShowBase.__init__(self)
		simplepbr.init(max_lights=4)
		
		self.pickablesDrawn = []
		
		self.disableMouse()
		self.accept("mouse1", self.mouse1_Down)
		self.accept("mouse1-up", self.mouse1_Up)
		self.accept("mouse3", self.mouse3_Down)
		self.accept("mouse3-up", self.mouse3_Up)
		
		"""First layer"""
		widgets_1stLayer = []
		widgets_1stLayer.append(OnscreenText(text="Include DIY", pos=(-0.4, 0.5), scale=0.1,
								align=TextNode.ACenter)
								)
		#monkCheckButton = DirectCheckButton(text = "Monk" ,scale=.1)
		#SVCheckButton = DirectCheckButton(text = "Shadowverse" ,scale=.1)
		
		widgets_1stLayer.append(OnscreenText(text="Select Board", pos=(-0.4, 0.2), scale=0.1,
								align=TextNode.ACenter)
								)
		self.boardMenu = DirectOptionMenu(text=BoardIndex[0], scale=0.1,
										  items=BoardIndex, initialitem=0,
										  highlightColor=(0, 1, 0, 1))
		self.boardMenu.setPos(-1, 0, 0.1)
		btn_genCardPool = DirectButton(text=("Continue", "Click!", "Rolling Over", "Continue"),
                 scale=.1, command=lambda: self.init_Layer1to2(widgets_1stLayer))
		#btn_genCardPool.reparentTo(self.render)
		btn_genCardPool.setPos(-0.4, 0, -0.2)
		widgets_1stLayer.append(btn_genCardPool)
		#The deck codes and hero select for both players
		heroClasses = ['Demon Hunter', 'Druid', 'Hunter', 'Mage', 'Paladin', 'Priest', 'Rogue', 'Shaman', 'Warlock', 'Warrior']
		self.hero1Menu = DirectOptionMenu(text=heroClasses[0], scale=0.1,
										  items=heroClasses, initialitem=0,
										  highlightColor=(0, 1, 0, 1))
		self.hero2Menu = DirectOptionMenu(text=heroClasses[0], scale=0.1,
								  items=heroClasses, initialitem=0,
								  highlightColor=(0, 1, 0, 1))
		self.deck1 = DirectEntry(width=50, scale=0.04)
		self.deck2 = DirectEntry(width=50, scale=0.04)
		widgets_1stLayer.append(OnscreenText(text="Class of 1st Player", pos=(0.7, 0.8), scale=0.1,
								align=TextNode.ACenter))
		self.hero1Menu.setPos(0.35, 0, 0.7)
		widgets_1stLayer.append(OnscreenText(text="Class of 2nd Player", pos=(0.7, 0.6), scale=0.1,
											 align=TextNode.ACenter))
		self.hero2Menu.setPos(0.35, 0, 0.5)
		widgets_1stLayer.append(OnscreenText(text="Deck of 1st Player", pos=(0.7, -0.2), scale=0.1,
											 align=TextNode.ACenter))
		#Decks
		self.deck1.setPos(0.2, 0, -0.3)
		widgets_1stLayer.append(OnscreenText(text="Deck of 2nd Player", pos=(0.7, -0.4), scale=0.1,
											 align=TextNode.ACenter))
		self.deck2.setPos(0.2, 0, -0.5)
		widgets_1stLayer.append(self.boardMenu)
		widgets_1stLayer.append(self.hero1Menu)
		widgets_1stLayer.append(self.hero2Menu)
		widgets_1stLayer.append(self.deck1)
		widgets_1stLayer.append(self.deck2)
		
		self.init_CollisionSetup()
	
	def init_Layer1to2(self, widgets):
		hero1, hero2 = self.hero1Menu.get(), self.hero2Menu.get()
		deck1, deck2 = self.deck1.get(), self.deck2.get()
		print("hero1, hero2:", hero1, hero2, deck1, deck2)
		heroes = {1: ClassDict[hero1], 2: ClassDict[hero2]}
		deckStrings = {1: deck1, 2: deck2}
		decks, decksCorrect = {1: [], 2: []}, {1: False, 2: False}
		self.boardID, self.transferStudentType = makeCardPool(self.boardMenu.get(), 0, 0)
		for ID in range(1, 3):
			decks[ID], decksCorrect[ID], heroes[ID] = parseDeckCode(deckStrings[ID], heroes[ID], ClassDict)
			
		if decksCorrect[1] and decksCorrect[2]:
			for widget in widgets: widget.destroy()
			
			self.Game = Game(self)
			self.Game.transferStudentType = self.transferStudentType
			print(self.Game.transferStudentType)
			for ID in range(1, 3):
				for i, card in enumerate(decks[ID]):
					if card.name == "Transfer Student": decks[ID][i] = self.transferStudentType
			self.Game.mode = 0
			self.Game.Classes, self.Game.ClassesandNeutral = Classes, ClassesandNeutral
			self.Game.initialize(cardPool, ClassCards, NeutralCards, MinionsofCost, RNGPools, heroes[1], heroes[2], decks[1], decks[2])
			self.initMulligan()
			#nodePath_Card = NodePath_Hand(self, AbusiveSergeant(self.Game, 1))
			#nodePath_Card.setPos(0, mulliganCard_Y, 0)
			#self.pickablesDrawn.append(nodePath_Card)
			#self.posMulligans = {1: [(100 + i * 2 * 111, Y - 140) for i in range(len(self.Game.mulligans[1]))],
			#						 2: [(100 + i * 2 * 111, 140) for i in range(len(self.Game.mulligans[2]))]}
			#self.destroy()
			#self.initSidePanel()
			#self.update()
		else:
			if not decksCorrect[1]:
				if decksCorrect[2]: self.showTempText("Deck 1 incorrect")
				else: self.showTempText("Both Deck 1&2 incorrect")
			else: self.showTempText("Deck 2 incorrect")
			
	def initMulligan(self):
		self.posMulligans = {1: [(-20 + i * 10, 30, -20) for i in range(len(self.Game.mulligans[1]))],
								 2: [(-20 + i * 10, 30, 20) for i in range(len(self.Game.mulligans[2]))]}
		self.initGameDisplay()
		for i in range(1, 3):
			for pos, card in zip(self.posMulligans[i], self.Game.mulligans[i]):
				nodePath_Card = loadCard(self, card)
				nodePath_Card.setPos(pos[0], pos[1], pos[2])
				self.pickablesDrawn.append(nodePath_Card)
				
	def initGameDisplay(self):
		self.handZones = {1: HandZone(self, 1), 2: HandZone(self, 2)}
		self.minionZones = {1: BoardZone(self, 1), 2: BoardZone(self, 2)}
		self.heroZones = {1: HeroZone(self, 1), 2: HeroZone(self, 2)}
		
		self.Game.Hand_Deck.hands[1] = [AbusiveSergeant(self.Game, 1), Deathwing(self.Game, 1),
										SoulMirror(self.Game, 1), LightningBolt(self.Game, 1),
										EaglehornBow(self.Game, 1), RinlingsRifle(self.Game, 1),
										LordJaraxxus(self.Game, 1)]
		self.Game.minions[1] = [AbusiveSergeant(self.Game, 1), Moonfang(self.Game, 1),
									]
		self.Game.Hand_Deck.hands[2] = [AbusiveSergeant(self.Game, 2), Deathwing(self.Game, 2),
										LightningBolt(self.Game, 2),
										EaglehornBow(self.Game, 2), RinlingsRifle(self.Game, 2),
										LordJaraxxus(self.Game, 2)]
		self.Game.minions[2] = [Deathwing(self.Game, 2), Moonfang(self.Game, 2),
								]
		weapon = EaglehornBow(self.Game, 1)
		weapon.onBoard = True
		self.Game.weapons[1] = [weapon]
		
		for ID in range(1, 3):
			self.handZones[ID].draw()
			self.minionZones[ID].draw()
			self.heroZones[ID].draw()
		#self.secretZones = {1: SecretZone(self, 1), 2: SecretZone(self, 2)}
		#self.manaZones = {1: ManaZone(self, 1), 2: ManaZone(self, 2)}
		#self.deckZones = {1: DeckZone(self, 1), 2: DeckZone(self, 2)}
		#self.offBoardTrigs = {1: None, 2: None}
		
		#if hasattr(self, "ID"): ownID, enemyID = self.ID, 3 - self.ID
		#else: ownID, enemyID = 1, 2
		#self.secretZones[ownID].place(x=int(0.2*X), y=int(0.74*Y), anchor='c')
		#self.secretZones[enemyID].place(x=int(0.2*X), y=int(0.26*Y), anchor='c')
		#self.manaZones[ownID].place(x=int(0.77*X), y=int(0.75*Y), anchor='c')
		#self.manaZones[enemyID].place(x=int(0.77*X), y=int(0.25*Y), anchor='c')
		#self.deckZones[ownID].plot()
		#self.deckZones[enemyID].plot()
		
	def showTempText(self, text):
		sansBold = self.loader.loadFont('Models\\OpenSans-Bold.ttf')
		text = OnscreenText(text=text, pos=(0, 0), scale=0.1, fg=(1, 0, 0, 1),
							align=TextNode.ACenter, mayChange=1, font=sansBold,
							bg=(0.5, 0.5, 0.5, 0.8))
		Sequence(Wait(1.5), Func(text.destroy)).start()
	
	def init_CollisionSetup(self):
		self.cTrav = CollisionTraverser()
		self.collHandler = CollisionHandlerQueue()
		
		self.raySolid = CollisionRay()
		collNode_Picker = CollisionNode("Picker Collider c_node")
		collNode_Picker.addSolid(self.raySolid)
		pickerNode = self.camera.attachNewNode(collNode_Picker)
		pickerNode.show()  #For now, show the pickerRay collision with the card models
		self.cTrav.addCollider(pickerNode, self.collHandler)
	
		self.cTrav.showCollisions(self.render)
		
	def mouse1_Down(self):
		if self.mouseWatcherNode.hasMouse():
			mpos = self.mouseWatcherNode.getMouse()
			#Reset the Collision Ray orientation, based on the mouse position
			self.raySolid.setFromLens(self.camNode, mpos.getX(), mpos.getY())
	
	def mouse1_Up(self):
		if self.mouseWatcherNode.hasMouse():
			mpos = self.mouseWatcherNode.getMouse()
			#Reset the Collision Ray orientation, based on the mouse position
			self.raySolid.setFromLens(self.camNode, mpos.getX(), mpos.getY())
			if self.collHandler.getNumEntries() > 0:
				print("Clicked something")
				self.collHandler.sortEntries()
				collNode_Picked = self.collHandler.getEntry(0).getIntoNodePath()
				pickedModel_NodePath = collNode_Picked.getParent()
				print(pickedModel_NodePath)
				"""Due to unknown reasons, all node paths are involved in the render hierachy
					have their types forced into NodePath, even if they are subclasses of NodePath.
					Therefore, we have to keep a container of the subclass instance, where the original type is preserved"""
				nodePath_Picked = next((model_NodePath for model_NodePath in self.pickablesDrawn \
													if model_NodePath == pickedModel_NodePath), None)
				if nodePath_Picked:
					nodePath_Picked.leftClick()

	def mouse3_Down(self):
		if self.mouseWatcherNode.hasMouse():
			mpos = self.mouseWatcherNode.getMouse()
			self.raySolid.setFromLens(self.camNode, mpos.getX(), mpos.getY())
	
	def mouse3_Up(self):
		if self.mouseWatcherNode.hasMouse():
			mpos = self.mouseWatcherNode.getMouse()
			#Reset the Collision Ray orientation, based on the mouse position
			self.raySolid.setFromLens(self.camNode, mpos.getX(), mpos.getY())
			if self.collHandler.getNumEntries() > 0:
				self.collHandler.sortEntries()
				collNode_Picked = self.collHandler.getEntry(0).getIntoNodePath()
				pickedModel_NodePath = collNode_Picked.getParent()
				nodePath_Picked = next((model_NodePath for model_NodePath in self.pickablesDrawn \
										if model_NodePath == pickedModel_NodePath), None)
				if nodePath_Picked:
					nodePath_Picked.rightClick()
			

GUI_IP().run()