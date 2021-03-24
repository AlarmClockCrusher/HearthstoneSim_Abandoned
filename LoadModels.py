from direct.interval.FunctionInterval import Func, Wait
from direct.interval.LerpInterval import *
from direct.interval.MetaInterval import Sequence
from panda3d.core import *
import inspect
import threading
from datetime import datetime


CHN = False
BackupModelPos = Point3(60, 56, 0)

BoardIndex = ["0 Random Game Board",
			"1 Classic Ogrimmar", "2 Classic Stormwind", "3 Classic Stranglethorn", "4 Classic Four Wind Valley",
			#"5 Naxxramas", "6 Goblins vs Gnomes", "7 Black Rock Mountain", "8 The Grand Tournament", "9 League of Explorers Museum", "10 League of Explorers Ruins",
			#"11 Corrupted Stormwind", "12 Karazhan", "13 Gadgetzan",
			#"14 Un'Goro", "15 Frozen Throne", "16 Kobolds",
			#"17 Witchwood", "18 Boomsday Lab", "19 Rumble",
			"20 Dalaran", "21 Uldum Desert", "22 Uldum Oasis", "23 Dragons",
			"24 Outlands", "25 Scholomance Academy", "26 Darkmoon Faire",
			]



def findFilepath(card):
	if card.type == "Dormant":
		if hasattr(card, "prisoner"):
			index = card.prisoner.index
			if inspect.isclass(card.prisoner):
				name = card.prisoner.__name__
			else:  #Instances don't have __name__
				name = type(card.prisoner).__name__
			path = "Images\\%s\\" % index.split('~')[0]
		else:
			path = "Images\\%s\\" % type(card).index.split('~')[0]
			name = type(card).__name__
	elif card.type == "Option":
		name = type(card).__name__
		path = "Images\\Options\\"
	else:  #type == "Weapon", "Minion", "Spell", "Hero", "Power"
		index, name = card.index, type(card).__name__
		if card.type != "Power":
			path = "Images\\%s\\" % index.split('~')[0]
		else:
			path = "Images\\HerosandPowers\\"
	
	if "Mutable" in name: name = name.split("_")[0]
	filepath = path + "%s.png" % name
	return filepath

	
red, green, blue = Point4(1, 0, 0, 1), Point4(0.3, 1, 0.2, 1), Point4(0, 0, 1, 1)
yellow, pink = Point4(1, 1, 0, 1), Point4(1, 0, 1, 1)

transparent, grey = Point4(1, 1, 1, 0), Point4(0.5, 0.5, 0.5, 1)
white = Point4(1, 1, 1, 1)


"""Subclass the NodePath, since it can be assigned attributes directly"""
class NodePath_Card(NodePath):
	def __init__(self, GUI, card=None, cardType=None, collBox4="Hand"):
		if cardType: super().__init__(cardType.__name__+"_Card")
		else: super().__init__(card.name+"_Card")
		#These attributes will be modified by load functions below
		self.cardType = cardType
		self.card = card
		self.selected = False
		self.GUI = GUI
		self.collNode = self.collNode_Backup = None  #collNode holds the return value of attachNewNode
		
		self.legendaryIcon = None
		#Attributes that require changing constantly
		self.manaText = self.attackText = self.healthText = self.durabilityText = self.armorText = None
		self.descriptionText = None
		self.card_Model = self.nameTag_Model = self.cardImage_Model = None
		self.indicatorModel = {}
		self.box_Model = None #Indicate if the card is available for play
		
		if collBox4:
			box_dx, box_dy, box_dz = {"Hand": (3.5, 0.3, 5),
									  "Minion": (2.4, 0.3, 3), "Dormant": (2, 0.3, 3),
									  "Weapon": (2.7, 0.3, 2.7), "Hero": (2, 0.3, 2.4),
									  "Power": (2, 0.4, 2)}[collBox4]
			self.collNode_Backup = CollisionNode("%s_c_node"%(card.name if card else cardType.name))
			self.collNode_Backup.addSolid(CollisionBox(Point3(0, 0, 0), box_dx, box_dy, box_dz))
			self.collNode = self.attachNewNode(self.collNode_Backup)
			#self.collNode_Backup.show()
			
	def dimDown(self):
		self.setColor(grey)
		
	def setBoxColor(self, color):
		if self.box_Model:
			self.box_Model.setColor(color)
	
	def showStatus(self):
		pass
	
	def rightClick(self):
		if self.GUI.UI in (1, 2): self.GUI.cancelSelection()
		else: self.GUI.drawCardSpecsDisplay(self)
	
	#Control the moving, rotating and scaling of a nodePath. For color manipulate, another method is used.
	def genMoveIntervals(self, pos=None, hpr=None, scale=None, duration=0.3, blendType="noBlend"):
		pos = pos if pos else self.getPos()
		hpr = hpr if hpr else self.getHpr()
		scale = scale if scale else self.getScale()
		if self.card:
			self.card.x, self.card.y, self.card.z = pos
		interval = LerpPosHprScaleInterval(self, duration=duration, pos=pos, hpr=hpr, scale=scale, blendType=blendType)
		return interval
	
	#For the selfCopy method, this will simply return a None
	def selfCopy(self, Copy):
		return None
	
def loadCard(base, card=None, cardType=None, pickable=True, ):
	if card:
		if card.type == "Minion":
			return loadMinion(base, card=card, cardType=cardType, pickable=pickable)
		elif card.type == "Spell":
			return loadSpell(base, card=card, cardType=cardType, pickable=pickable)
		elif card.type == "Weapon":
			return loadWeapon(base, card=card, cardType=cardType, pickable=pickable)
		elif card.type == "Hero":
			return loadHero(base, card=card, cardType=cardType, pickable=pickable)
		elif card.type == "Power":
			return loadPower(base, card=card, cardType=cardType, pickable=pickable)
		elif card.type == "Option":
			return loadChooseOption(base, card)
		elif card.type == "Dormant":
			return loadDormant(base, card=card, cardType=cardType, pickable=False)
	else:
		if "attack" in cardType.__dict__:
			if "health" in cardType.__dict__:
				return loadMinion(base, card=card, cardType=cardType, pickable=pickable)
			else:
				return loadWeapon(base, card=card, cardType=cardType, pickable=pickable)
		elif "armor" in cardType.__dict__:
			return loadHero(base, card=card, cardType=cardType, pickable=pickable)
		elif "school" in cardType.__dict__: #For now, it can't distinguish the spell and hero power
			return loadSpell(base, card=card, cardType=cardType, pickable=pickable)
		else:
			return loadDormant(base, card=card, cardType=cardType, pickable=False)

class NodePath_Minion(NodePath_Card):
	def __init__(self, GUI, card=None):
		NodePath.__init__(self, card.name + "_Minion")
		#These attributes will be modified by load functions below
		self.card = card
		self.selected = False
		self.GUI = GUI
		
		self.legendaryIcon = None
		#Attributes that require changing constantly
		self.manaText = self.attackText = self.healthText = None
		self.descriptionText = self.descriptionTextNode = None
		self.card_Model = self.nameTag_Model = self.cardImage_Model = self.description_Model = self.race_Model = None
		self.box_Model = None  #Indicate if the card is available for play
		
		self.collNode_Backup = CollisionNode("%s_c_node"%card.name)
		self.collNode_Backup.addSolid(CollisionBox(Point3(0, 0, 0), 3.5, 0.3, 5))
		self.collNode = self.attachNewNode(self.collNode_Backup)
		
	def changeCard(self, card, pickable=True):
		loader = self.GUI.loader
		rarityChanged = not self.card or ("~Legendary" in self.card.index) != ("~Legendary" in card.index)
		self.card = card
		if pickable: card.btn = self
		self.name = type(card).__name__ + "_Minion_" + str(datetime.now().time())
		imgPath = findFilepath(card)
		threading.Thread(target=self.reloadModels, args=(loader, imgPath, rarityChanged, pickable)).start()
		
	def reloadModels(self, loader, imgPath, rarityChanged, pickable):
		card = self.card
		if rarityChanged:
			self.box_Model.removeNode()
			self.box_Model = loader.loadModel("Models\\MinionModels\\%s.glb" % ("Box_Legendary" if "~Legendary" in card.index else "Box_Normal"))
			self.box_Model.reparentTo(self)
			self.box_Model.setTransparency(True)
			self.cardImage_Model.removeNode()
			self.cardImage_Model = loader.loadModel("Models\\MinionModels\\" + ("MinionImage_Legendary.glb" if "~Legendary" in card.index else "MinionImage.glb"))
			self.cardImage_Model.reparentTo(self)
		if pickable and not self.collNode:
			self.collNode = self.attachNewNode(self.collNode_Backup)
		elif not pickable and self.collNode:
			self.collNode.removeNode()
			self.collNode = None
		
		self.legendaryIcon.setColor(white if "~Legendary" in self.card.index else transparent)
		"""The card frame. The front face texture is set according to it class"""
		texture = loader.loadTexture(imgPath)
		self.card_Model.setTexture(self.card_Model.findTextureStage('*'),
									texture, 1)
		self.cardImage_Model.setTexture(self.cardImage_Model.findTextureStage('*'),
										texture, 1)
		self.nameTag_Model.setTexture(self.nameTag_Model.findTextureStage('*'),
									texture, 1)
		self.race_Model.setTexture(self.race_Model.findTextureStage('*'),
									texture, 1)
		if self.descriptionText:  #If card description can change, then set the card image as the texture
			self.description_Model.setTexture(self.description_Model.findTextureStage('*'),
										loader.loadTexture("Models\\MinionModels\\Vanilla_%s.png" % card.index.split('~')[0]), 1)
			text = card.text(CHN)
			self.descriptionText.setText(text)
			self.descriptionTextNode.setPos(0, -0.2, -3+0.1*len(text) / 12)
		else:
			self.description_Model.setTexture(self.description_Model.findTextureStage('*'),
											texture, 1)
		
		self.refresh()
		
	def leftClick(self):
		self.selected = not self.selected
		GUI, card = self.GUI, self.card
		game = GUI.Game
		if GUI.UI == -2:
			self.setBoxColor(red if self.selected else green)
			GUI.mulliganStatus[card.ID][game.mulligans[card.ID].index(card)] = 1 if self.selected else 0
		elif GUI.UI == -1: pass #lock out any selection
		elif GUI.UI == 1: pass
		elif GUI.UI == 3:
			if card in game.options:
				GUI.resolveMove(card, None, "DiscoverOption", info=None)
		else: GUI.resolveMove(card, self, "MinioninHand")
		
	def refresh(self, color=False, stat=False, indicator=False, all=True):
		#Change the box color to indicate the selectability of a card
		if color or all:
			self.setBoxColor(self.decideColor())
		
		card, GUI = self.card, self.GUI
		cardType, game = type(card), card.Game
		"""Reset the stats of the card"""
		if stat or all:
			#Refresh the mana
			self.manaText.setText(str(card.mana))
			if card.mana < cardType.mana: color = green
			elif card.mana > cardType.mana: color = red
			else: color = white
			self.manaText.setTextColor(color)
			#Refresh the attack
			self.attackText.setText(str(card.attack))
			if card.attack > card.attack_0: color = green
			elif card.attack < card.attack_0: color = red
			else: color = white
			self.attackText.setTextColor(color)
			#Refresh the health
			self.healthText.setText(str(card.health))
			if card.health < card.health_max: color = red
			elif card.health_max > card.health_0: color = green
			else: color = white
			self.healthText.setTextColor(color)
		#Refresh the description if applicable
		if self.descriptionText: self.descriptionText.setText(card.text(CHN))
		
	def decideColor(self):
		color, card = transparent, self.card
		cardType, GUI, game = card.type, self.GUI, card.Game
		if card == GUI.subject: color = pink
		elif card == GUI.target: color = blue
		else:
			if card.evanescent: color = blue
			elif card.ID == game.turn and game.Manas.affordable(card) and game.space(card.ID) > 0:
				color = yellow if card.effectViable else green
		return color
		
		
class NodePath_MinionPlayed(NodePath_Card):
	def __init__(self, GUI, card=None):
		NodePath.__init__(self, card.name + "_MinionPlayed")
		self.card = card
		self.selected = False
		self.GUI = GUI
		
		self.legendaryIcon = None
		#Attributes that require changing constantly
		self.attackText = self.healthText = None
		self.nameTag_Model = self.cardImage_Model = None
		self.box_Model = None  #Indicate if the card is available for play
		
		self.indicatorModels = {}
		
		self.collNode_Backup = CollisionNode("%s_c_node"%card.name)
		self.collNode_Backup.addSolid(CollisionBox(Point3(0, 0, 0), 2.4, 0.3, 3))
		self.collNode = self.attachNewNode(self.collNode_Backup)
		
	def changeCard(self, card, pickable=True):
		loader = self.GUI.loader
		self.name = type(card).__name__ + "_MinionPlayed_" + str(datetime.now().time())
		rarityChanged = not self.card or ("~Legendary" in self.card.index) != ("~Legendary" in card.index)
		self.card = card
		if pickable: card.btn = self
		imgPath = findFilepath(card)
		threading.Thread(target=self.reloadModels, args=(loader, imgPath, rarityChanged, pickable)).start()
		#print("btn for card", card, card.btn)
	
	def reloadModels(self, loader, imgPath, rarityChanged, pickable):
		card = self.card
		self.setColor(white)
		if rarityChanged:
			self.box_Model.removeNode()
			self.box_Model = loader.loadModel("Models\\MinionModels\\%s.glb" % ("Box_LegendaryPlayed" if "~Legendary" in card.index else "Box_NormalPlayed"))
			self.box_Model.reparentTo(self)
			self.box_Model.setTransparency(True)
		if pickable and not self.collNode:
			self.collNode = self.attachNewNode(self.collNode_Backup)
		elif not pickable and self.collNode:
			self.collNode.removeNode()
			self.collNode = None
		
		self.legendaryIcon.setColor(white if "~Legendary" in self.card.index else transparent)
		texture = loader.loadTexture(imgPath)
		self.cardImage_Model.setTexture(self.cardImage_Model.findTextureStage('*'),
										texture, 1)
		self.nameTag_Model.setTexture(self.nameTag_Model.findTextureStage('*'),
									texture, 1)
		self.refresh()
		
	def leftClick(self):
		if self.GUI.UI in (0, 2):
			self.GUI.resolveMove(self.card, self, "MiniononBoard")
		
	def refresh(self, color=False, stat=False, indicator=False, all=True):
		#Change the box color to indicate the selectability of a card
		if color or all:
			self.setBoxColor(self.decideColor())
		
		card, GUI = self.card, self.GUI
		"""Reset the stats of the card"""
		if stat or all:
			#Refresh the attack
			self.attackText.setText(str(card.attack))
			if card.attack > card.attack_0: color = green
			elif card.attack < card.attack_0: color = red
			else: color = white
			self.attackText.setTextColor(color)
			#Refresh the health
			self.healthText.setText(str(card.health))
			if card.health < card.health_max: color = red
			elif card.health_max > card.health_0: color = green
			else: color = white
			self.healthText.setTextColor(color)
		if indicator or all:
			self.manageStatusModel()
			
	def manageStatusModel(self):
		num, models = 0, []
		if self.card.trigsBoard:
			self.indicatorModels["Trigger"].setColor(white)
			self.indicatorModels["Trigger"].updateText()
			num += 1
			models.append(self.indicatorModels["Trigger"])
		else: self.indicatorModels["Trigger"].setColor(transparent)
		#self.indicatorModels["Trigger"].updateText()
		if self.card.deathrattles:
			self.indicatorModels["Deathrattle"].setColor(white)
			num += 1
			models.append(self.indicatorModels["Trigger"])
		else: self.indicatorModels["Deathrattle"].setColor(transparent)
		for keyWord in ("Lifesteal", "Poisonous"):
			if self.card.keyWords[keyWord] > 0:
				self.indicatorModels[keyWord].setColor(white)
				num += 1
				models.append(self.indicatorModels[keyWord])
			else: self.indicatorModels[keyWord].setColor(transparent)
		
		color = (1, 1, 1, 0.4) if self.card.auras else transparent
		self.indicatorModels["Aura"].setColor(color)
		
		color = white if self.card.keyWords["Taunt"] > 0 else transparent
		self.indicatorModels["Taunt"].setColor(color)
		
		color = (1, 1, 1, 0.3) if self.card.keyWords["Divine Shield"] > 0 else transparent
		self.indicatorModels["Divine Shield"].setColor(color)
		
		color = (0.4, 0.4, 0.4, 0.65) if self.card.keyWords["Stealth"] + self.card.status["Temp Stealth"] > 0 else transparent
		self.indicatorModels["Stealth"].setColor(color)
		for keyWord in ("Immune", "Frozen"):
			color = (1, 1, 1, 0.5) if self.card.status[keyWord] > 0 else transparent
			self.indicatorModels[keyWord].setColor(color)
			
		color = (1, 1, 1, 0.4) if self.card.silenced else transparent
		self.indicatorModels["Silenced"].setColor(color)
		
		separation = 1.3
		if num:
			leftMostPos = - separation * (num - 1) / 2
			for i, model in enumerate(models):
				model.setPos(leftMostPos + i * separation, 0, 0)
		
	def decideColor(self):
		color, card = transparent, self.card
		if card == self.GUI.subject: color = pink
		elif card == self.GUI.target: color = blue
		elif card.canAttack(): color = green
		return color
		
		
statTextScale = 1.7
manaPos = Point3(-2.7, -0.15, 3.85)
healthPos = Point3(3, -0.2, -4.95)
attackPos = Point3(-2.85, -0.15, -4.95)

#Either a card or cardType must be defined
#Loading a minion card from scratch takes 30ms ~ 100ms
def loadMinion(base, card=None, cardType=None, pickable=True):
	loader = base.loader
	if card: imgPath = findFilepath(card)
	else: imgPath = "Images\\%s\\" % cardType.index.split('~')[0] + cardType.__name__ + ".png"
	sansBold = loader.loadFont('Models\\OpenSans-Bold.ttf')
	cardImgTexture = loader.loadTexture(imgPath)
	
	if card: root = NodePath_Minion(base, card=card)
	else: root = NodePath_Card(base, cardType=cardType, collBox4="Hand" if pickable else '')
	root.reparentTo(base.render)
	
	isLegendary = ("~Legendary" in card.index) if card else ("~Legendary" in cardType.index)
	"""The card frame. The front face texture is set according to it class"""
	filePath = "Models\\MinionModels\\" + ("Card_Legendary.glb" if isLegendary else "Card.glb")
	root.card_Model = loader.loadModel(filePath)
	root.card_Model.reparentTo(root)
	root.card_Model.setTexture(root.card_Model.findTextureStage('*'),
							   cardImgTexture, 1)
	"""Card back of the card"""
	cardBack = loader.loadModel("Models\\CardBack.glb")
	cardBack.reparentTo(root)
	cardBack.setTexture(cardBack.findTextureStage('*'),
						loader.loadTexture("Models\\CardBack.png"), 1)
	
	"""Card image based on the card type"""
	filePath = "Models\\MinionModels\\" + ("MinionImage_Legendary.glb" if isLegendary else "MinionImage.glb")
	root.cardImage_Model = loader.loadModel(filePath)
	root.cardImage_Model.reparentTo(root)
	root.cardImage_Model.setTexture(root.cardImage_Model.findTextureStage('*'),
									cardImgTexture, 1)
	
	"""Name Tag of the card, includes the model, and the nameText"""
	root.nameTag_Model = loader.loadModel("Models\\MinionModels\\NameTag.glb")
	root.nameTag_Model.reparentTo(root)
	root.nameTag_Model.setTexture(root.nameTag_Model.findTextureStage('*'),
								  cardImgTexture, 1)
	
	"""Description and race of the card"""
	root.description_Model = loader.loadModel("Models\\MinionModels\\Description.glb")
	root.description_Model.reparentTo(root)
	if card and card.text(CHN):
		text = card.text(CHN)
		root.description_Model.setTexture(root.description_Model.findTextureStage('*'),
									 loader.loadTexture("Models\\MinionModels\\Vanilla_%s.png"%card.index.split('~')[0]), 1)
		root.descriptionText = TextNode("Description Text Node")
		root.descriptionText.setText(text)
		root.descriptionText.setAlign(TextNode.ACenter)
		root.descriptionText.setFont(sansBold)
		root.descriptionText.setTextColor(0, 0, 0, 1)
		root.descriptionText.setWordwrap(12)
		root.descriptionTextNode = root.attachNewNode(root.descriptionText)
		root.descriptionTextNode.setScale(0.4)
		root.descriptionTextNode.setPos(0, -0.2, -2.5+0.1*len(text) / 12)
	else:
		root.description_Model.setTexture(root.description_Model.findTextureStage('*'),
									 cardImgTexture, 1)
	
	root.race_Model = loader.loadModel("Models\\MinionModels\\Race.glb")
	root.race_Model.reparentTo(root)
	root.race_Model.setTexture(root.race_Model.findTextureStage('*'),
								cardImgTexture, 1)
	"""Values to display on the card"""
	manaValue = '%d' % (card.mana if card else cardType.mana)
	attackValue = '%d' % (card.attack if card else cardType.attack)
	healthValue = '%d' % (card.health if card else cardType.health)
	
	"""Mana display of the card"""
	mana_Model = loader.loadModel("Models\\MinionModels\\Mana.glb")
	mana_Model.reparentTo(root)
	mana_Model.setTexture(mana_Model.findTextureStage('*'),
						  loader.loadTexture("Models\\MinionModels\\MinionStats.png"), 1)
	root.manaText = TextNode("Mana Text Node")
	root.manaText.setFont(sansBold)
	root.manaText.setText(manaValue)
	root.manaText.setAlign(TextNode.ACenter)
	
	root.manaTextNode = root.attachNewNode(root.manaText)
	root.manaTextNode.setScale(statTextScale)
	root.manaTextNode.setPos(manaPos)
	
	"""Attack of the card, includes the model and the attackText"""
	attack_Model = loader.loadModel("Models\\MinionModels\\Attack.glb")
	attack_Model.reparentTo(root)
	attack_Model.setTexture(attack_Model.findTextureStage('*'),
							loader.loadTexture("Models\\MinionModels\\MinionStats.png"), 1)
	root.attackText = TextNode("Attack Text Node")
	root.attackText.setText(attackValue)
	root.attackText.setFont(sansBold)
	root.attackText.setAlign(TextNode.ACenter)
	attackTextNode = root.attachNewNode(root.attackText)
	attackTextNode.setScale(statTextScale)
	attackTextNode.setPos(attackPos)
	
	"""Health of the card, includes the model and the attackText"""
	health_Model = loader.loadModel("Models\\MinionModels\\Health.glb")
	health_Model.reparentTo(root)
	health_Model.setTexture(health_Model.findTextureStage('*'),
							loader.loadTexture("Models\\MinionModels\\MinionStats.png"), 1)
	root.healthText = TextNode("Health Text Node")
	root.healthText.setText(healthValue)
	root.healthText.setFont(sansBold)
	root.healthText.setAlign(TextNode.ACenter)
	healthTextNode = root.attachNewNode(root.healthText)
	healthTextNode.setScale(statTextScale)
	healthTextNode.setPos(healthPos)
	
	root.legendaryIcon = loader.loadModel("Models\\MinionModels\\LegendaryIcon.glb")
	root.legendaryIcon.reparentTo(root)
	root.legendaryIcon.setTransparency(True)
	root.legendaryIcon.setTexture(root.legendaryIcon.findTextureStage('*'),
							 loader.loadTexture("Models\\MinionModels\\LegendaryExample.png"), 1)
	
	if card:
		filePath = "Models\\MinionModels\\%s.glb" % ("Box_Legendary" if isLegendary else "Box_Normal")
		root.box_Model = loader.loadModel(filePath)
		root.box_Model.reparentTo(root)
		root.box_Model.setTransparency(True)
		#root.box_Model.setColor(root.decideColor())
	
	root.setPos(BackupModelPos)
	return root


def loadMinion_Played(base, card):
	loader = base.loader
	imgPath = findFilepath(card)
	sansBold = loader.loadFont('Models\\OpenSans-Bold.ttf')
	cardImgTexture = loader.loadTexture(imgPath)
	
	root = NodePath_MinionPlayed(base, card)
	root.reparentTo(base.render)
	
	"""Card image based on the card type"""
	root.cardImage_Model = loader.loadModel("Models\\MinionModels\\MinionImage_Played.glb")
	root.cardImage_Model.reparentTo(root)
	root.cardImage_Model.setTexture(root.cardImage_Model.findTextureStage('*'),
						 cardImgTexture, 1)
	
	"""Name Tag of the card, includes the model, and the nameText"""
	root.nameTag_Model = loader.loadModel("Models\\MinionModels\\NameTag_Played.glb")
	root.nameTag_Model.reparentTo(root)
	root.nameTag_Model.setTexture(root.nameTag_Model.findTextureStage('*'),
					cardImgTexture, 1)
	
	"""Values to display on the minion pawn"""
	attackValue = '%d' % card.attack
	healthValue = '%d' % card.health
	
	"""Attack of the card, includes the model and the attackText"""
	attack_Model = loader.loadModel("Models\\MinionModels\\Attack_Played.glb")
	attack_Model.reparentTo(root)
	root.attackText = TextNode("attack")
	root.attackText.setText(attackValue)
	root.attackText.setFont(sansBold)
	root.attackText.setAlign(TextNode.ACenter)
	attackTextNode = root.attachNewNode(root.attackText)
	attackTextNode.setScale(1.3)
	attackTextNode.setPos(-2.05, -0.1, -1.95)
	
	"""Health of the card, includes the model and the attackText"""
	health_Model = loader.loadModel("Models\\MinionModels\\Health_Played.glb")
	health_Model.reparentTo(root)
	root.healthText = TextNode("health")
	root.healthText.setText(healthValue)
	root.healthText.setFont(sansBold)
	root.healthText.setAlign(TextNode.ACenter)
	healthTextNode = root.attachNewNode(root.healthText)
	healthTextNode.setScale(1.3)
	healthTextNode.setPos(1.95, -0.1, -1.9)
	
	root.legendaryIcon = loader.loadModel("Models\\MinionModels\\LegendaryIcon_Played.glb")
	root.legendaryIcon.reparentTo(root)
	root.legendaryIcon.setTransparency(True)
	root.legendaryIcon.setTexture(root.legendaryIcon.findTextureStage('*'),
							 loader.loadTexture("Models\\MinionModels\\LegendaryExample.png"), 1)
	
	isLegendary = "~Legendary" in card.index
	filePath = "Models\\MinionModels\\%s.glb" % ("Box_LegendaryPlayed" if isLegendary else "Box_NormalPlayed")
	root.box_Model = loader.loadModel(filePath)
	root.box_Model.reparentTo(root)
	root.box_Model.setTransparency(True)
	#root.box_Model.setColor(root.decideColor())
	
	"""Define the models that indicate the keywords of the minion, for example, Taunt"""
	trig_Model = loadTrigger(root) #TriggerModel(root, "Models\\MinionModels\\Trigger.glb")
	trig_Model.setTransparency(True)
	trig_Model.reparentTo(root)
	root.indicatorModels["Trigger"] = trig_Model
	
	model = loader.loadModel("Models\\MinionModels\\Deathrattle.glb")
	model.setTransparency(True)
	model.reparentTo(root)
	root.indicatorModels["Deathrattle"] = model
	
	model = loader.loadModel("Models\\MinionModels\\Aura.glb")
	model.setTransparency(True)
	#model.setTexture(model.findTextureStage('*'),
	#				 loader.loadTexture(r"Models\MinionModels\Aura.avi"), 1)
	model.reparentTo(root)
	root.indicatorModels["Aura"] = model
	
	for keyWord in ("Lifesteal", "Poisonous", "Taunt", "Divine Shield", "Stealth", "Immune", "Frozen"):
		model = loader.loadModel("Models\\MinionModels\\%s.glb"%keyWord)
		model.setTransparency(True)
		model.reparentTo(root)
		if keyWord in ("Taunt", "Stealth"):
			model.setTexture(model.findTextureStage('*'),
					loader.loadTexture("Models\\MinionModels\\%s.png"%keyWord), 1)
		root.indicatorModels[keyWord] = model
	
	model = loader.loadModel("Models\\MinionModels\\Silenced.glb")
	model.setTransparency(True)
	model.reparentTo(root)
	root.indicatorModels["Silenced"] = model
	root.manageStatusModel()
	
	root.setPos(BackupModelPos)
	return root
	
	
	
"""Load Spell Cards"""
class NodePath_Spell(NodePath_Card):
	def __init__(self, GUI, card=None):
		NodePath.__init__(self, card.name + "_Spell")
		#These attributes will be modified by load functions below
		self.card = card
		self.selected = False
		self.GUI = GUI
		
		self.legendaryIcon = None
		#Attributes that require changing constantly
		self.manaText = self.descriptionText = self.descriptionTextNode = None
		self.card_Model = self.description_Model = self.school_Model = None
		self.box_Model = None  #Indicate if the card is available for play
		
		self.collNode_Backup = CollisionNode("%s_c_node"%card.name)
		self.collNode_Backup.addSolid(CollisionBox(Point3(0, 0, 0), 3.5, 0.3, 5))
		self.collNode = self.attachNewNode(self.collNode_Backup)
		
	def changeCard(self, card, pickable=True):
		loader = self.GUI.loader
		rarityChanged = not self.card or ("~Legendary" in self.card.index) != ("~Legendary" in card.index)
		self.card = card
		if pickable: card.btn = self
		self.name = type(card).__name__ + "_Spell_" + str(datetime.now().time())
		imgPath = findFilepath(card)
		threading.Thread(target=self.reloadModels, args=(loader, imgPath, rarityChanged, pickable)).start()
		
	def reloadModels(self, loader, imgPath, rarityChanged, pickable):
		card = self.card
		if rarityChanged:
			self.box_Model.removeNode()
			self.box_Model = loader.loadModel("Models\\SpellModels\\%s.glb"%("Box_Legendary" if "~Legendary" in card.index else "Box_Normal"))
			self.box_Model.reparentTo(self)
			self.box_Model.setTransparency(True)
		if pickable and not self.collNode:
			self.collNode = self.attachNewNode(self.collNode_Backup)
		elif not pickable and self.collNode:
			self.collNode.removeNode()
			self.collNode = None
		
		self.legendaryIcon.setColor(white if "~Legendary" in self.card.index else transparent)
		"""The card frame. The front face texture is set according to it class"""
		texture = loader.loadTexture(imgPath)
		self.card_Model.setTexture(self.card_Model.findTextureStage('*'),
									texture, 1)
		self.school_Model.setTexture(self.school_Model.findTextureStage('*'),
									texture, 1)
		text = card.text(CHN)
		if text:
			self.description_Model.setTexture(self.description_Model.findTextureStage('*'),
											loader.loadTexture("Models\\SpellModels\\Vanilla_%s.png" % card.index.split('~')[0]), 1)
			self.descriptionText.setText(text)
			self.descriptionTextNode.setPos(0, -0.2, -3+0.1*len(text) / 12)
		else:
			self.description_Model.setTexture(self.description_Model.findTextureStage('*'),
											texture, 1)
		
		self.refresh()
		
	def leftClick(self):
		self.selected = not self.selected
		GUI, card = self.GUI, self.card
		if GUI.UI == -2:
			self.setBoxColor(red if self.selected else green)
			GUI.mulliganStatus[card.ID][GUI.Game.mulligans[card.ID].index(card)] = 1 if self.selected else 0
		elif GUI.UI == -1: pass #Lock out any selection
		elif GUI.UI == 1: pass
		elif GUI.UI == 3:
			if card in GUI.Game.options:
				GUI.resolveMove(card, None, "DiscoverOption", info=None)
		else: GUI.resolveMove(card, self, "SpellinHand")
		
	def refresh(self, color=False, stat=False, indicator=False, all=True):
		#Change the box color to indicate the selectability of a card
		if color or all:
			self.setBoxColor(self.decideColor())
		
		card = self.card
		cardType = type(card)
		"""Reset the stats of the card"""
		if stat or all:
			#Refresh the mana
			self.manaText.setText(str(card.mana))
			if card.mana < cardType.mana: color = green
			elif card.mana > cardType.mana: color = red
			else: color = white
			self.manaText.setTextColor(color)
		#Refresh the description if applicable
		if self.descriptionText: self.descriptionText.setText(card.text(CHN))
		
	def decideColor(self):
		color, card = transparent, self.card
		if card == self.GUI.subject: color = pink
		elif card == self.GUI.target: color = blue
		else:
			if card.evanescent: color = blue
			if card.inHand and card.ID == card.Game.turn and card.Game.Manas.affordable(card) and card.available():
				color = yellow if card.effectViable else green
		return color
		
		
def loadSpell(base, card=None, cardType=None, pickable=True):
	loader = base.loader
	if card: imgPath = findFilepath(card)
	else: imgPath = "Images\\%s\\" % cardType.index.split('~')[0] + cardType.__name__ + ".png"
	sansBold = loader.loadFont('Models\\OpenSans-Bold.ttf')
	cardImgTexture = loader.loadTexture(imgPath)
	
	if card: root = NodePath_Spell(base, card=card)
	else: root = NodePath_Card(base, cardType=cardType, collBox4="Hand" if pickable else '')
	root.reparentTo(base.render)
	
	isLegendary = ("~Legendary" in card.index) if card else ("~Legendary" in cardType.index)
	"""The card frame. The front face texture is set according to it class"""
	filePath = "Models\\SpellModels\\" + ("Card_Legendary.glb" if isLegendary else "Card.glb")
	root.card_Model = loader.loadModel(filePath)
	root.card_Model.reparentTo(root)
	root.card_Model.setTexture(root.card_Model.findTextureStage('*'),
					cardImgTexture, 1)
	"""Card back of the card"""
	cardBack = loader.loadModel("Models\\CardBack.glb")
	cardBack.reparentTo(root)
	cardBack.setTexture(cardBack.findTextureStage('*'),
						loader.loadTexture("Models\\CardBack.png"), 1)
	
	"""Description and school of the card"""
	if isLegendary:
		root.description_Model = loader.loadModel("Models\\SpellModels\\Description_Legendary.glb")
	else:
		root.description_Model = loader.loadModel("Models\\SpellModels\\Description.glb")
	if card:
		text = card.text(CHN)
		root.descriptionText = TextNode("Description Text Node")
		root.descriptionText.setText(text)
		root.descriptionText.setAlign(TextNode.ACenter)
		root.descriptionText.setFont(sansBold)
		root.descriptionText.setTextColor(0, 0, 0, 1)
		root.descriptionText.setWordwrap(12)
		root.descriptionTextNode = root.attachNewNode(root.descriptionText)
		root.descriptionTextNode.setScale(0.44)
		root.descriptionTextNode.setPos(0, -0.2, -3 + 0.1 * len(text) / 12)
		if text:
			root.description_Model.reparentTo(root)
			root.description_Model.setTexture(root.description_Model.findTextureStage('*'),
										 loader.loadTexture("Models\\SpellModels\\Vanilla_%s.png" % card.index.split('~')[0]), 1)
		else:
			root.description_Model.setTexture(root.description_Model.findTextureStage('*'),
										 cardImgTexture, 1)
		
	root.school_Model = loader.loadModel("Models\\SpellModels\\School.glb")
	root.school_Model.reparentTo(root)
	root.school_Model.setTexture(root.school_Model.findTextureStage('*'),
								cardImgTexture, 1)
	"""Mana display of the card"""
	manaValue = "%d"%(card.mana if card else cardType.mana)
	mana_Model = loader.loadModel("Models\\SpellModels\\Mana.glb")
	mana_Model.reparentTo(root)
	mana_Model.setTexture(mana_Model.findTextureStage('*'),
						  loader.loadTexture("Models\\SpellModels\\SpellStats.png"), 1)
	root.manaText = TextNode("mana")
	root.manaText.setFont(sansBold)
	root.manaText.setText(manaValue)
	root.manaText.setAlign(TextNode.ACenter)
	root.manaTextNode = root.attachNewNode(root.manaText)
	root.manaTextNode.setScale(statTextScale)
	root.manaTextNode.setPos(manaPos)
	
	root.legendaryIcon = loader.loadModel("Models\\SpellModels\\LegendaryIcon.glb")
	root.legendaryIcon.reparentTo(root)
	root.legendaryIcon.setTransparency(True)
	root.legendaryIcon.setTexture(root.legendaryIcon.findTextureStage('*'),
								 loader.loadTexture("Models\\SpellModels\\LegendaryExample.png"), 1)
	if card:
		filePath = "Models\\SpellModels\\%s.glb"%("Box_Legendary" if isLegendary else "Box_Normal")
		root.box_Model = loader.loadModel(filePath)
		root.box_Model.reparentTo(root)
		root.box_Model.setTransparency(True)
		#root.box_Model.setColor(root.decideColor())
	
	root.setPos(BackupModelPos)
	return root



"""Load Weapon Cards"""
class NodePath_Weapon(NodePath_Card):
	def __init__(self, GUI, card=None):
		NodePath.__init__(self, card.name + "_Weapon")
		#These attributes will be modified by load functions below
		self.card = card
		self.selected = False
		self.GUI = GUI
		
		self.legendaryIcon = None
		#Attributes that require changing constantly
		self.manaText = self.attackText = self.durabilityText = None
		self.card_Model = self.nameTag_Model = self.cardImage_Model = self.description_Model = None
		self.box_Model = None  #Indicate if the card is available for play
		
		self.collNode_Backup = CollisionNode("%s_c_node"%card.name)
		self.collNode_Backup.addSolid(CollisionBox(Point3(0, 0, 0), 3.5, 0.3, 5))
		self.collNode = self.attachNewNode(self.collNode_Backup)
		
	def changeCard(self, card, pickable=True):
		loader = self.GUI.loader
		rarityChanged = not self.card or ("~Legendary" in self.card.index) != ("~Legendary" in card.index)
		self.card = card
		if pickable: card.btn = self
		self.name = type(card).__name__ + "_Weapon_" + str(datetime.now().time())
		imgPath = findFilepath(card)
		threading.Thread(target=self.reloadModels, args=(loader, imgPath, rarityChanged, pickable)).start()
		
	def reloadModels(self, loader, imgPath, rarityChanged, pickable):
		card = self.card
		if rarityChanged:
			self.box_Model.removeNode()
			self.box_Model = loader.loadModel("Models\\WeaponModels\\%s.glb" % ("Box_Legendary" if "~Legendary" in card.index else "Box_Normal"))
			self.box_Model.reparentTo(self)
			self.box_Model.setTransparency(True)
		if pickable and not self.collNode:
			self.collNode = self.attachNewNode(self.collNode_Backup)
		elif not pickable and self.collNode:
			self.collNode.removeNode()
			self.collNode = None
		
		self.legendaryIcon.setColor(white if "~Legendary" in self.card.index else transparent)
		"""The card frame. The front face texture is set according to it class"""
		texture = loader.loadTexture(imgPath)
		self.card_Model.setTexture(self.card_Model.findTextureStage('*'),
									texture, 1)
		self.cardImage_Model.setTexture(self.cardImage_Model.findTextureStage('*'),
										texture, 1)
		self.nameTag_Model.setTexture(self.nameTag_Model.findTextureStage('*'),
									texture, 1)
		
		self.refresh()
		
	def leftClick(self):
		self.selected = not self.selected
		GUI, card = self.GUI, self.card
		game = GUI.Game
		if GUI.UI == -2:
			self.setBoxColor(red if self.selected else green)
			GUI.mulliganStatus[card.ID][game.mulligans[card.ID].index(card)] = 1 if self.selected else 0
		elif GUI.UI == -1: pass #lock out any selection
		elif GUI.UI == 1: pass
		elif GUI.UI == 3:
			if card in game.options:
				GUI.resolveMove(card, None, "DiscoverOption", info=None)
		else: GUI.resolveMove(card, self, "WeaponinHand")
		
	def refresh(self, color=False, stat=False, indicator=False, all=True):
		#Change the box color to indicate the selectability of a card
		if color or all:
			self.setBoxColor(self.decideColor())
		
		card, GUI = self.card, self.GUI
		cardType, game = type(card), card.Game
		"""Reset the stats of the card"""
		if stat or all:
			#Refresh the mana
			self.manaText.setText(str(card.mana))
			if card.mana < cardType.mana: color = green
			elif card.mana > cardType.mana: color = red
			else: color = white
			self.manaText.setTextColor(color)
			#Refresh the attack
			self.attackText.setText(str(card.attack))
			if card.attack > cardType.attack: color = green
			elif card.attack < cardType.attack: color = red
			else: color = white
			self.attackText.setTextColor(color)
			#Weapon durability
			self.durabilityText.setText(str(card.durability))
			if card.durability > cardType.durability: color = green
			elif card.durability < cardType.durability: color = red
			else: color = white
			self.durabilityText.setTextColor(color)
		
	def decideColor(self):
		color, card = transparent, self.card
		cardType, GUI, game = card.type, self.GUI, card.Game
		if card == GUI.subject: color = pink
		elif card == GUI.target: color = blue
		else:
			if card.evanescent: color = blue
			if card.inHand and card.ID == game.turn and game.Manas.affordable(card):
				color = yellow if card.effectViable else green
		return color
		
		
class NodePath_WeaponPlayed(NodePath_Card):
	def __init__(self, GUI, card=None):
		NodePath.__init__(self, card.name + "_WeaponPlayed")
		self.card = card
		self.selected = False
		self.GUI = GUI
		
		self.legendaryIcon = None
		#Attributes that require changing constantly
		self.attackText = self.durabilityText = None
		self.nameTag_Model = self.cardImage_Model = None
		self.box_Model = None
		
		self.indicatorModels = {}
		
		self.collNode_Backup = CollisionNode("%s_c_node"%card.name)
		self.collNode_Backup.addSolid(CollisionSphere(0, 0, 0, 2.7))
		self.collNode = self.attachNewNode(self.collNode_Backup)
		
	def changeCard(self, card, pickable=True):
		loader = self.GUI.loader
		self.card = card
		if pickable: card.btn = self
		self.name = type(card).__name__ + "_WeaponPlayed_" + str(datetime.now().time())
		imgPath = findFilepath(card)
		threading.Thread(target=self.reloadModels, args=(loader, imgPath, True, pickable)).start()
		#print("After changing card, weaponPlayed.btn is", self, self.card, self.card.btn)
		
	def reloadModels(self, loader, imgPath, rarityChanged, pickable):
		self.setColor(white)
		if pickable and not self.collNode:
			self.collNode = self.attachNewNode(self.collNode_Backup)
		elif not pickable and self.collNode:
			self.collNode.removeNode()
			self.collNode = None
		
		self.legendaryIcon.setColor(white if "~Legendary" in self.card.index else transparent)
		texture = loader.loadTexture(imgPath)
		self.cardImage_Model.setTexture(self.cardImage_Model.findTextureStage('*'),
										texture, 1)
		self.nameTag_Model.setTexture(self.nameTag_Model.findTextureStage('*'),
									texture, 1)
		self.refresh()
		
	def leftClick(self):
		pass
		
	def refresh(self, color=False, stat=False, indicator=False, all=True):
		#Change the box color to indicate the selectability of a card
		if color or all:
			self.setBoxColor(self.decideColor())
		
		card, GUI = self.card, self.GUI
		cardType, game = type(card), card.Game
		"""Reset the stats of the card"""
		if stat or all:
			#Refresh the attack
			self.attackText.setText(str(card.attack))
			if card.attack > cardType.attack: color = green
			elif card.attack < cardType.attack: color = red
			else: color = white
			self.attackText.setTextColor(color)
			#Weapon durability
			self.durabilityText.setText(str(card.durability))
			if card.durability > cardType.durability: color = green
			elif card.durability < cardType.durability: color = red
			else: color = white
			self.durabilityText.setTextColor(color)
		if indicator or all:
			self.manageStatusModel()
			
	def manageStatusModel(self):
		num, models = 0, []
		if self.card.trigsBoard:
			self.indicatorModels["Trigger"].setColor(white)
			self.indicatorModels["Trigger"].updateText()
			num += 1
			models.append(self.indicatorModels["Trigger"])
		else: self.indicatorModels["Trigger"].setColor(transparent)
		#self.indicatorModels["Trigger"].updateText()
		if self.card.deathrattles:
			self.indicatorModels["Deathrattle"].setColor(white)
			num += 1
			models.append(self.indicatorModels["Trigger"])
		else: self.indicatorModels["Deathrattle"].setColor(transparent)
		for keyWord in ("Lifesteal", "Poisonous"):
			if self.card.keyWords[keyWord] > 0:
				self.indicatorModels[keyWord].setColor(white)
				num += 1
				models.append(self.indicatorModels[keyWord])
			else: self.indicatorModels[keyWord].setColor(transparent)
		
		separation = 1.3
		if num:
			leftMostPos = - separation * (num - 1) / 2
			for i, model in enumerate(models):
				model.setPos(leftMostPos + i * separation, 0, 0)
		
	def decideColor(self):
		return transparent
		
		
def loadWeapon(base, card=None, cardType=None, pickable=True):
	loader = base.loader
	if card: imgPath = findFilepath(card)
	else: imgPath = "Images\\%s\\" % cardType.index.split('~')[0] + cardType.__name__ + ".png"
	sansBold = loader.loadFont('Models\\OpenSans-Bold.ttf')
	cardImgTexture = loader.loadTexture(imgPath)
	
	if card: root = NodePath_Weapon(base, card=card)
	else: root = NodePath_Card(base, cardType=cardType, collBox4="Hand" if pickable else '')
	root.reparentTo(base.render)
	
	isLegendary = ("~Legendary" in card.index) if card else ("~Legendary" in cardType.index)
	"""The card frame. The front face texture is set according to it class"""
	filePath = "Models\\WeaponModels\\" + ("Card_Legendary.glb" if isLegendary else "Card.glb")
	root.card_Model = loader.loadModel(filePath)
	root.card_Model.reparentTo(root)
	root.card_Model.setTexture(root.card_Model.findTextureStage('*'),
								cardImgTexture, 1)
	
	cardBack = loader.loadModel("Models\\CardBack.glb")
	cardBack.reparentTo(root)
	cardBack.setTexture(cardBack.findTextureStage('*'),
						loader.loadTexture("Models\\CardBack.png"), 1)
	
	"""Weapon head image to display"""
	root.cardImage_Model = loader.loadModel("Models\\WeaponModels\\Head.glb")
	root.cardImage_Model.reparentTo(root)
	root.cardImage_Model.setTexture(root.cardImage_Model.findTextureStage('*'),
					   				cardImgTexture, 1)
	
	"""Name Tag of the card"""
	root.nameTag_Model = loader.loadModel("Models\\WeaponModels\\NameTag.glb")
	root.nameTag_Model.reparentTo(root)
	root.nameTag_Model.setTexture(root.nameTag_Model.findTextureStage('*'),
								cardImgTexture, 1)
	
	"""Values to display on the card"""
	manaValue = '%d' % (card.mana if card else cardType.mana)
	attackValue = '%d' % (card.attack if card else cardType.attack)
	durabilityValue = '%d' % (card.durability if card else cardType.durability)
	
	"""Mana display of the card"""
	mana_Model = loader.loadModel("Models\\WeaponModels\\Mana.glb")
	mana_Model.reparentTo(root)
	mana_Model.setTexture(mana_Model.findTextureStage('*'),
						  loader.loadTexture("Models\\WeaponModels\\WeaponStats.png"), 1)
	root.manaText = TextNode("mana")
	root.manaText.setFont(sansBold)
	root.manaText.setText(manaValue)
	root.manaText.setAlign(TextNode.ACenter)
	root.manaTextNode = root.attachNewNode(root.manaText)
	root.manaTextNode.setScale(statTextScale)
	root.manaTextNode.setPos(manaPos)
	
	"""Attack of the card, includes the model and the attackText"""
	attack_Model = loader.loadModel("Models\\WeaponModels\\Attack.glb")
	attack_Model.reparentTo(root)
	attack_Model.setTexture(attack_Model.findTextureStage('*'),
						  loader.loadTexture("Models\\WeaponModels\\WeaponStats.png"), 1)
	root.attackText = TextNode("attack")
	root.attackText.setText(attackValue)
	root.attackText.setFont(sansBold)
	root.attackText.setAlign(TextNode.ACenter)
	attackTextNode = root.attachNewNode(root.attackText)
	attackTextNode.setScale(statTextScale)
	attackTextNode.setPos(attackPos)
	
	"""Durability of the card, includes the model and the attackText"""
	durability_Model = loader.loadModel("Models\\WeaponModels\\Durability.glb")
	durability_Model.reparentTo(root)
	durability_Model.setTexture(durability_Model.findTextureStage('*'),
						  loader.loadTexture("Models\\WeaponModels\\WeaponStats.png"), 1)
	root.durabilityText = TextNode("Cadurability")
	root.durabilityText.setText(durabilityValue)
	root.durabilityText.setFont(sansBold)
	root.durabilityText.setAlign(TextNode.ACenter)
	durabilityTextNode = root.attachNewNode(root.durabilityText)
	durabilityTextNode.setScale(statTextScale)
	durabilityTextNode.setPos(healthPos)
	
	root.legendaryIcon = loader.loadModel("Models\\WeaponModels\\LegendaryIcon.glb")
	root.legendaryIcon.reparentTo(root)
	root.legendaryIcon.setTransparency(True)
	root.legendaryIcon.setTexture(root.legendaryIcon.findTextureStage('*'),
							 loader.loadTexture("Models\\WeaponModels\\LegendaryExample.png"), 1)
		
	if card:
		filePath = "Models\\WeaponModels\\%s.glb" % ("Box_Legendary" if isLegendary else "Box_Normal")
		root.box_Model = loader.loadModel(filePath)
		root.box_Model.reparentTo(root)
		root.box_Model.setTransparency(True)
		#root.box_Model.setColor(root.decideColor())
	
	root.setPos(BackupModelPos)
	return root


def loadWeapon_Played(base, card):
	loader = base.loader
	imgPath = findFilepath(card)
	sansBold = loader.loadFont('Models\\OpenSans-Bold.ttf')
	cardImgTexture = loader.loadTexture(imgPath)
	
	root = NodePath_WeaponPlayed(base, card)
	root.reparentTo(base.render)
	
	"""Card border for weapon"""
	border = loader.loadModel("Models\\WeaponModels\\Border_Played.glb")
	border.reparentTo(root)
	border.setTexture(border.findTextureStage('*'),
								 loader.loadTexture("Models\\WeaponModels\\ForBorder.png"), 1)
	
	"""Card image based on the card type"""
	root.cardImage_Model = loader.loadModel("Models\\WeaponModels\\WeaponImage_Played.glb")
	root.cardImage_Model.reparentTo(root)
	root.cardImage_Model.setTexture(root.cardImage_Model.findTextureStage('*'),
						 			cardImgTexture, 1)
	
	"""Name Tag of the card, includes the model, and the nameText"""
	root.nameTag_Model = loader.loadModel("Models\\WeaponModels\\NameTag_Played.glb")
	root.nameTag_Model.reparentTo(root)
	root.nameTag_Model.setTexture(root.nameTag_Model.findTextureStage('*'),
					   			cardImgTexture, 1)
	
	"""Values to display on the card"""
	attackValue = '%d' % card.attack
	durabilityValue = '%d' % card.durability

	"""Attack of the card, includes the model and the attackText"""
	attack_Model = loader.loadModel("Models\\WeaponModels\\Attack_Played.glb")
	attack_Model.reparentTo(root)
	root.attackText = TextNode("attack")
	root.attackText.setText(attackValue)
	root.attackText.setFont(sansBold)
	root.attackText.setAlign(TextNode.ACenter)
	attackTextNode = root.attachNewNode(root.attackText)
	attackTextNode.setScale(1.3)
	attackTextNode.setPos(-2.25, -0.17, -1.7)
	
	"""Durability of the card, includes the model and the attackText"""
	durability_Model = loader.loadModel("Models\\WeaponModels\\Durability_Played.glb")
	durability_Model.reparentTo(root)
	root.durabilityText = TextNode("durability")
	root.durabilityText.setText(durabilityValue)
	root.durabilityText.setFont(sansBold)
	root.durabilityText.setAlign(TextNode.ACenter)
	durabilityTextNode = root.attachNewNode(root.durabilityText)
	durabilityTextNode.setScale(1.3)
	durabilityTextNode.setPos(2.25, -0.17, -1.7)
	
	root.legendaryIcon = loader.loadModel("Models\\WeaponModels\\LegendaryIcon_Played.glb")
	root.legendaryIcon.reparentTo(root)
	root.legendaryIcon.setTransparency(True)
	root.legendaryIcon.setTexture(root.legendaryIcon.findTextureStage('*'),
							 loader.loadTexture("Models\\WeaponModels\\LegendaryExample.png"), 1)
	
	"""Define the models that indicate the keywords of the minion, for example, Taunt"""
	trig_Model = loadTrigger(root) #loader.loadModel("Models\\WeaponModels\\Trigger.glb")
	#trig_Model.setTexture(trig_Model.findTextureStage('*'),
	#				 loader.loadTexture("Models\\WeaponModels\\Trigger.png"), 1)
	trig_Model.reparentTo(root)
	trig_Model.setTransparency(True)
	root.indicatorModels["Trigger"] = trig_Model
	
	model = loader.loadModel("Models\\WeaponModels\\Deathrattle.glb")
	model.setTransparency(True)
	model.reparentTo(root)
	root.indicatorModels["Deathrattle"] = model
	
	for keyWord in ("Lifesteal", "Poisonous"):
		model = loader.loadModel("Models\\WeaponModels\\%s.glb"%keyWord)
		model.setTransparency(True)
		model.reparentTo(root)
		root.indicatorModels[keyWord] = model
		
	root.manageStatusModel()
	
	root.setPos(BackupModelPos)
	return root



"""Load Hero Powers"""
class NodePath_Power(NodePath_Card):
	def __init__(self, GUI, card=None):
		NodePath.__init__(self, card.name + "_Power")
		#These attributes will be modified by load functions below
		self.card = card
		self.selected = False
		self.GUI = GUI
		
		#Attributes that require changing constantly
		self.manaText = self.descriptionText = self.descriptionTextNode = None
		self.card_Model = self.description_Model = None
		self.box_Model = None  #Indicate if the card is available for play
		
		self.collNode_Backup = CollisionNode("%s_c_node"%card.name)
		self.collNode_Backup.addSolid(CollisionBox(Point3(0, 0, 0), 3.5, 0.3, 5))
		self.collNode = self.attachNewNode(self.collNode_Backup)
		
	def changeCard(self, card, pickable=True):
		loader = self.GUI.loader
		self.card = card
		if pickable: card.btn = self
		self.name = type(card).__name__ + "_Power_" + str(datetime.now().time())
		imgPath = findFilepath(card)
		threading.Thread(target=self.reloadModels, args=(loader, imgPath, pickable)).start()
		
	def reloadModels(self, loader, imgPath, pickable):
		card = self.card
		if pickable and not self.collNode:
			self.collNode = self.attachNewNode(self.collNode_Backup)
		elif not pickable and self.collNode:
			self.collNode.removeNode()
			self.collNode = None
		
		"""The card frame. The front face texture is set according to it class"""
		texture = loader.loadTexture(imgPath)
		self.card_Model.setTexture(self.card_Model.findTextureStage('*'),
									texture, 1)
		if self.descriptionText:  #If card description can change, then set the card image as the texture
			self.description_Model.setTexture(self.description_Model.findTextureStage('*'),
											loader.loadTexture("Models\\PowerModels\\Vanilla.png"), 1)
			text = card.text(CHN)
			self.descriptionText.setText(text)
			self.descriptionTextNode.setPos(0, -0.2, -3+0.1*len(text) / 12)
		else:
			self.description_Model.setTexture(self.description_Model.findTextureStage('*'),
											texture, 1)
		
		self.refresh()
		
	def leftClick(self):
		if self.GUI.UI == 3 and self.card in self.GUI.Game.options:
			self.GUI.resolveMove(self.card, None, "DiscoverOption", info=None)
		
	def refresh(self, color=False, stat=False, indicator=False, all=True):
		pass
		
	def decideColor(self):
		return white
		
		
class NodePath_PowerPlayed(NodePath_Card):
	def __init__(self, GUI, card=None):
		NodePath.__init__(self, card.name + "_PowerPlayed")
		#These attributes will be modified by load functions below
		self.card = card
		self.selected = False
		self.GUI = GUI
		
		#Attributes that require changing constantly
		self.manaText = None
		self.cardImage_Model = None
		self.box_Model = None  #Indicate if the card is available for play
		
		self.collNode_Backup = CollisionNode("%s_c_node"%card.name)
		self.collNode_Backup.addSolid(CollisionSphere(0, 0, 0, 2.3))
		self.collNode = self.attachNewNode(self.collNode_Backup)
		
	def changeCard(self, card, pickable=True):
		loader = self.GUI.loader
		self.card = card
		if pickable: card.btn = self
		self.name = type(card).__name__ + "_PowerPlayed_" + str(datetime.now().time())
		imgPath = findFilepath(card)
		threading.Thread(target=self.reloadModels, args=(loader, imgPath, pickable)).start()
		
	def reloadModels(self, loader, imgPath, pickable):
		card = self.card
		if pickable and not self.collNode:
			self.collNode = self.attachNewNode(self.collNode_Backup)
		elif not pickable and self.collNode:
			self.collNode.removeNode()
			self.collNode = None
		
		"""The card frame. The front face texture is set according to it class"""
		self.cardImage_Model.setTexture(self.cardImage_Model.findTextureStage('*'),
									loader.loadTexture(imgPath), 1)
		self.refresh()
		
	def leftClick(self):
		if self.GUI.UI == 0:
			self.GUI.resolveMove(self.card, self, "Power", info=None)
		
	def refresh(self, color=False, stat=False, indicator=False, all=True):
		if color or all:
			self.setBoxColor(self.decideColor())
		if stat or all:
			cardType = type(self.card)
			#Refresh the mana
			self.manaText.setText(str(self.card.mana))
			if self.card.mana < cardType.mana: color = green
			elif self.card.mana > cardType.mana: color = red
			else: color = white
			self.manaText.setTextColor(color)
		
		if not self.card.chancesUsedUp() and self.card.Game.turn == self.card.ID:
			self.GUI.animate(self.genMoveIntervals(hpr=Point3(0, 0, 0)), name="Power reset", afterAllFinished=False)
	
	def decideColor(self):
		color, card = transparent, self.card
		if card.ID == card.Game.turn and card.Game.Manas.affordable(card) and card.available():
			color = green
		return color
		
		
def loadPower(base, card=None, cardType=None, pickable=True):
	loader = base.loader
	imgPath = "Images\\HerosandPowers\\%s.png"%(type(card).__name__ if card else cardType.__name__)
	sansBold = loader.loadFont('Models\\OpenSans-Bold.ttf')
	cardImgTexture = loader.loadTexture(imgPath)
	
	if card: root = NodePath_Power(base, card)
	else: root = NodePath_Card(base, cardType=cardType, collBox4="Hand" if pickable else '')
	root.reparentTo(base.render)
	
	"""The power frame"""
	root.card_Model = loader.loadModel("Models\\PowerModels\\Power.glb")
	root.card_Model.reparentTo(root)
	root.card_Model.setTexture(root.card_Model.findTextureStage('*'),
							   cardImgTexture, 1)
	
	#"""Name Tag of the card, includes the model, and the nameText"""
	#root.nameTag_Model = loader.loadModel("Models\\PowerModels\\NameTag.glb")
	#root.nameTag_Model.reparentTo(root)
	#root.nameTag_Model.setTexture(root.nameTag_Model.findTextureStage('*'),
	#						loader.loadTexture(imgPath), 1)
	
	"""Description of the card"""
	root.description_Model = loader.loadModel("Models\\PowerModels\\Description.glb")
	root.description_Model.reparentTo(root)
	if card and card.text(CHN):  #If card description can change, then set the card image as the texture
		root.description_Model.setTexture(root.description_Model.findTextureStage('*'),
									 	loader.loadTexture("Models\\PowerModels\\Vanilla.png"), 1)
		text = card.text(CHN)
		root.descriptionText = TextNode("Description Text Node")
		root.descriptionText.setText(text)
		root.descriptionText.setAlign(TextNode.ACenter)
		root.descriptionText.setFont(sansBold)
		root.descriptionText.setTextColor(0, 0, 0, 1)
		root.descriptionText.setWordwrap(12)
		root.descriptionTextNode = root.attachNewNode(root.descriptionText)
		root.descriptionTextNode.setScale(0.44)
		root.descriptionTextNode.setPos(0, -0.15, -3+0.1*len(text) / 12)
	else:
		root.description_Model.setTexture(root.description_Model.findTextureStage('*'),
									 	cardImgTexture, 1)
		
	"""Mana display of the power"""
	manaValue = '%d' % (card.mana if card else cardType.mana)
	mana_Model = loader.loadModel("Models\\PowerModels\\Mana.glb")
	mana_Model.reparentTo(root)
	mana_Model.setTexture(mana_Model.findTextureStage('*'),
								  loader.loadTexture("Models\\PowerModels\\HeroPower.png"), 1)
	root.manaText = TextNode("mana")
	root.manaText.setFont(sansBold)
	root.manaText.setText(manaValue)
	root.manaText.setAlign(TextNode.ACenter)
	root.manaTextNode = root.attachNewNode(root.manaText)
	root.manaTextNode.setScale(statTextScale)
	root.manaTextNode.setPos(0, -0.25, 4)
	
	root.setPos(BackupModelPos)
	return root


def loadPower_Played(base, card):
	loader = base.loader
	imgPath = findFilepath(card)
	sansBold = loader.loadFont('Models\\OpenSans-Bold.ttf')
	
	root = NodePath_PowerPlayed(base, card)
	root.reparentTo(base.render)
	
	"""Power border for weapon"""
	border = loader.loadModel("Models\\PowerModels\\Border_Played.glb")
	border.reparentTo(root)
	border.setTexture(border.findTextureStage('*'),
					loader.loadTexture("Models\\PowerModels\\ForBorder.png"), 1)
	
	"""Mana display of the power"""
	mana_Model = loader.loadModel("Models\\PowerModels\\Mana_Played.glb")
	mana_Model.reparentTo(root)
	mana_Model.setTexture(mana_Model.findTextureStage('*'),
						  loader.loadTexture("Models\\PowerModels\\HeroPower.png"), 1)
	root.manaText = TextNode("mana")
	root.manaText.setFont(sansBold)
	root.manaText.setText('%d' % card.mana)
	root.manaText.setAlign(TextNode.ACenter)
	root.manaTextNode = root.attachNewNode(root.manaText)
	root.manaTextNode.setScale(statTextScale)
	root.manaTextNode.setPos(-0.1, -0.35, 1.75)
	
	"""Power image based on the power type"""
	root.cardImage_Model = loader.loadModel("Models\\PowerModels\\PowerImage_Played.glb")
	root.cardImage_Model.reparentTo(root)
	root.cardImage_Model.setTexture(root.cardImage_Model.findTextureStage('*'),
						  loader.loadTexture(imgPath), 1)
	if card:
		root.box_Model = loader.loadModel("Models\\PowerModels\\Box_Played.glb")
		root.box_Model.reparentTo(root)
		root.box_Model.setTransparency(True)
		#root.box_Model.setColor(root.decideColor())
	
	root.setPos(BackupModelPos)
	return root



"""Load Hero Cards"""
class NodePath_Hero(NodePath_Card):
	def __init__(self, GUI, card=None):
		NodePath.__init__(self, card.name + "_Hero")
		#These attributes will be modified by load functions below
		self.card = card
		self.selected = False
		self.GUI = GUI
		
		self.legendaryIcon = None
		#Attributes that require changing constantly
		self.manaText = self.armorText = None
		self.card_Model = None
		self.box_Model = None  #Indicate if the card is available for play
		
		self.collNode_Backup = CollisionNode("%s_c_node"%card.name)
		self.collNode_Backup.addSolid(CollisionBox(Point3(0, 0, 0), 3.5, 0.3, 5))
		self.collNode = self.attachNewNode(self.collNode_Backup)
		
	def changeCard(self, card, pickable=True):
		loader = self.GUI.loader
		self.card = card
		if pickable: card.btn = self
		self.name = type(card).__name__ + "_Hero_" + str(datetime.now().time())
		imgPath = findFilepath(card)
		threading.Thread(target=self.reloadModels, args=(loader, imgPath, pickable)).start()
		
	def reloadModels(self, loader, imgPath, pickable):
		card = self.card
		if pickable and not self.collNode:
			self.collNode = self.attachNewNode(self.collNode_Backup)
		elif not pickable and self.collNode:
			self.collNode.removeNode()
			self.collNode = None
		
		"""The card frame. The front face texture is set according to it class"""
		self.card_Model.setTexture(self.card_Model.findTextureStage('*'),
									loader.loadTexture(imgPath), 1)
		self.refresh()
		
	def leftClick(self):
		self.selected = not self.selected
		GUI, card = self.GUI, self.card
		game = GUI.Game
		if GUI.UI == -2:
			self.setBoxColor(red if self.selected else green)
			GUI.mulliganStatus[card.ID][game.mulligans[card.ID].index(card)] = 1 if self.selected else 0
		elif GUI.UI == -1: pass #Lock out any selection
		elif GUI.UI == 1: pass
		elif GUI.UI == 3:
			if card in game.options:
				GUI.resolveMove(card, None, "DiscoverOption", info=None)
		else: GUI.resolveMove(card, self, "HeroinHand")
		
	def refresh(self, color=False, stat=False, indicator=False, all=True):
		#Change the box color to indicate the selectability of a card
		if color or all:
			self.setBoxColor(self.decideColor())
		
		card = self.card
		cardType = type(card)
		"""Reset the stats of the card"""
		if stat or all:
			#Refresh the mana
			self.manaText.setText(str(card.mana))
			if card.mana < cardType.mana: color = green
			elif card.mana > cardType.mana: color = red
			else: color = white
			self.manaText.setTextColor(color)
			#Refresh the armor
			self.armorText.setText(str(card.armor))
			self.armorText.setTextColor(white if card.armor else transparent)
			
	def decideColor(self):
		color, card = transparent, self.card
		if card == self.GUI.subject: color = pink
		elif card == self.GUI.target: color = blue
		else:
			if card.evanescent: color = blue
			if card.ID == card.Game.turn and card.Game.Manas.affordable(card):
				color = green
		return color
		
		
class NodePath_HeroPlayed(NodePath_Card):
	def __init__(self, GUI, card=None):
		NodePath.__init__(self, card.name + "_HeroPlayed")
		self.card = card
		self.selected = False
		self.GUI = GUI
		
		#Attributes that require changing constantly
		self.attackText = self.healthText = self.armorText = None
		self.cardImage_Model = self.attack_Model = self.armor_Model = None
		self.box_Model = None  #Indicate if the card is available for play
		
		self.indicatorModels = {}
		
		self.collNode_Backup = CollisionNode("%s_c_node"%card.name)
		self.collNode_Backup.addSolid(CollisionBox(Point3(0, 0, 0), 2, 0.3, 2.4))
		self.collNode = self.attachNewNode(self.collNode_Backup)
		
	#Assuming the hero played changes very fast.
	def changeCard(self, card, pickable=True):
		self.card = card
		if pickable: card.btn = self
		imgPath = "Images\\HerosandPowers\\%s.png"%type(card).__name__
		self.name = type(card).__name__ + "_HeroPlayed_" + str(datetime.now().time())
		if pickable and not self.collNode:
			self.collNode = self.attachNewNode(self.collNode_Backup)
		elif not pickable and self.collNode:
			self.collNode.removeNode()
			self.collNode = None
		
		self.cardImage_Model.setTexture(self.cardImage_Model.findTextureStage('*'),
										self.GUI.loader.loadTexture(imgPath), 1)
		self.refresh()
		
	def leftClick(self):
		if self.GUI.UI in (0, 2):
			self.GUI.resolveMove(self.card, self, "HeroonBoard")
		
	def refresh(self, color=False, stat=False, indicator=False, all=True):
		#Change the box color to indicate the selectability of a card
		if color or all:
			self.setBoxColor(self.decideColor())
		
		card, GUI = self.card, self.GUI
		"""Reset the stats of the card"""
		if stat or all:
			#Refresh the attack
			self.attackText.setText(str(card.attack))
			self.attackText.setTextColor(green if card.attack > 0 else transparent)
			self.attack_Model.setColor(white if card.attack > 0 else transparent)
			#Refresh the health
			self.healthText.setText(str(card.health))
			self.healthText.setTextColor(red if card.health < card.health_max else green)
			#Refresh the armor
			self.armorText.setText(str(card.armor))
			self.armorText.setTextColor(white if card.armor > 0 else transparent)
			self.armor_Model.setColor(white if card.armor > 0 else transparent)
		if indicator or all:
			self.manageStatusModel()
			
	def manageStatusModel(self):
		color = (0.6, 0.6, 0.6, 0.7) if self.card.status["Temp Stealth"] > 0 else transparent
		self.indicatorModels["Stealth"].setColor(color)
		color = (1, 1, 1, 0.5) if self.card.status["Frozen"] > 0 else transparent
		self.indicatorModels["Frozen"].setColor(color)
		color = (1, 1, 1, 0.5) if self.card.Game.status[self.card.ID]["Immune"] > 0 else transparent
		self.indicatorModels["Immune"].setColor(color)
	
	def decideColor(self):
		color, card = transparent, self.card
		if card == self.GUI.subject: color = pink
		elif card == self.GUI.target: color = blue
		elif card.canAttack(): color = green
		return color
		
		
def loadHero(base, card=None, cardType=None, pickable=True):
	loader = base.loader
	if card: imgPath = findFilepath(card)
	else: imgPath = "Images\\%s\\" % cardType.index.split('~')[0] + cardType.__name__ + ".png"
	sansBold = loader.loadFont('Models\\OpenSans-Bold.ttf')
	
	if card: root = NodePath_Hero(base, card)
	else: root = NodePath_Card(base, cardType=cardType, collBox4="Hand" if pickable else '')
	root.reparentTo(base.render)
	
	"""The card frame. The front face texture is set according to it class"""
	root.card_Model = loader.loadModel("Models\\HeroModels\\Card.glb")
	root.card_Model.reparentTo(root)
	root.card_Model.setTexture(root.card_Model.findTextureStage('*'),
					loader.loadTexture(imgPath), 1)
	"""Card back of the card"""
	cardBack = loader.loadModel("Models\\CardBack.glb")
	cardBack.reparentTo(root)
	cardBack.setTexture(cardBack.findTextureStage('*'),
						loader.loadTexture("Models\\CardBack.png"), 1)
	
	"""Mana display of the card"""
	manaValue = '%d' % (card.mana if card else cardType.mana)
	mana_Model = loader.loadModel("Models\\HeroModels\\Mana.glb")
	mana_Model.reparentTo(root)
	mana_Model.setTexture(mana_Model.findTextureStage('*'),
								loader.loadTexture("Models\\HeroModels\\HeroStats.png"), 1)
	root.manaText = TextNode("mana")
	root.manaText.setFont(sansBold)
	root.manaText.setText(manaValue)
	root.manaText.setAlign(TextNode.ACenter)
	root.manaTextNode = root.attachNewNode(root.manaText)
	root.manaTextNode.setScale(statTextScale)
	root.manaTextNode.setPos(-2.9, -0.15, 3.85)
	
	"""Armor display of the card"""
	armorValue = '%d' % (card.armor if card else cardType.armor)
	armor_Model = loader.loadModel("Models\\HeroModels\\Armor.glb")
	armor_Model.reparentTo(root)
	armor_Model.setTexture(armor_Model.findTextureStage('*'),
								loader.loadTexture("Models\\HeroModels\\HeroStats.png"), 1)
	root.armorText = TextNode("armor")
	root.armorText.setFont(sansBold)
	root.armorText.setText(armorValue)
	root.armorText.setAlign(TextNode.ACenter)
	armorTextNode = root.attachNewNode(root.armorText)
	armorTextNode.setScale(1.6)
	armorTextNode.setPos(healthPos)
	
	root.legendaryIcon = loader.loadModel("Models\\HeroModels\\LegendaryIcon.glb")
	root.legendaryIcon.reparentTo(root)
	root.legendaryIcon.setTransparency(True)
	root.legendaryIcon.setTexture(root.legendaryIcon.findTextureStage('*'),
							 loader.loadTexture("Models\\HeroModels\\LegendaryExample.png"), 1)
	if card:
		root.box_Model = loader.loadModel("Models\\HeroModels\\Box_Hero.glb")
		root.box_Model.reparentTo(root)
		root.box_Model.setTransparency(True)
		#root.box_Model.setColor(root.decideColor())
		
	root.setPos(BackupModelPos)
	return root


def loadHero_Played(base, card):
	loader = base.loader
	imgPath = "Images\\HerosandPowers\\%s.png"%type(card).__name__
	sansBold = loader.loadFont('Models\\OpenSans-Bold.ttf')
	
	root = NodePath_HeroPlayed(base, card)
	root.reparentTo(base.render)
	
	"""Card image based on the card type"""
	root.cardImage_Model = loader.loadModel("Models\\HeroModels\\HeroHead.glb")
	root.cardImage_Model.reparentTo(root)
	root.cardImage_Model.setTexture(root.cardImage_Model.findTextureStage('*'),
						 loader.loadTexture(imgPath), 1)
	
	"""Attack of the card, includes the model and the attackText"""
	root.attack_Model = loader.loadModel("Models\\HeroModels\\Attack.glb")
	root.attack_Model.reparentTo(root)
	root.attack_Model.setTransparency(True)
	root.attackText = TextNode("attack")
	root.attackText.setText('%d' % card.attack)
	root.attackText.setFont(sansBold)
	root.attackText.setAlign(TextNode.ACenter)
	root.attackText.setTextColor(green if card.attack > 0 else transparent)
	attackTextNode = root.attachNewNode(root.attackText)
	attackTextNode.setScale(1)
	attackTextNode.setPos(-2, -0.25, -2)
	
	"""Health of the hero"""
	health_Node = loader.loadModel("Models\\HeroModels\\Health.glb")
	health_Node.reparentTo(root)
	root.healthText = TextNode("health")
	root.healthText.setText('%d' % card.health)
	root.healthText.setFont(sansBold)
	root.healthText.setAlign(TextNode.ACenter)
	root.healthText.setTextColor(green if card.health >= card.health else red)
	healthTextNode = root.attachNewNode(root.healthText)
	healthTextNode.setScale(1)
	healthTextNode.setPos(2.05, -0.22, -2)
	
	"""Armor of the hero"""
	root.armor_Model = loader.loadModel("Models\\HeroModels\\Armor_Played.glb")
	root.armor_Model.reparentTo(root)
	root.armor_Model.setTransparency(True)
	root.armorText = TextNode("health")
	root.armorText.setText('%d' % card.armor)
	root.armorText.setFont(sansBold)
	root.armorText.setAlign(TextNode.ACenter)
	root.armorText.setTextColor(white if card.armor > 0 else transparent)
	armorTextNode = root.attachNewNode(root.armorText)
	armorTextNode.setScale(1)
	armorTextNode.setPos(2.05, -0.3, -0.7)
	
	root.box_Model = loader.loadModel("Models\\HeroModels\\Box_HeroPlayed.glb")
	root.box_Model.reparentTo(root)
	root.box_Model.setTransparency(True)
	#root.box_Model.setColor(root.decideColor())
	
	for keyWord in ("Stealth", "Immune", "Frozen"):
		model = loader.loadModel("Models\\HeroModels\\%s.glb" % keyWord)
		model.setTransparency(True)
		model.reparentTo(root)
		if keyWord == "Stealth":
			model.setTexture(model.findTextureStage('*'),
							 loader.loadTexture("Models\\HeroModels\\%s.png" % keyWord), 1)
		root.indicatorModels[keyWord] = model
	
	root.manageStatusModel()
	
	root.setPos(BackupModelPos)
	return root


#Used for secrets and quests
class NodePath_Secret(NodePath_Card):
	def __init__(self, GUI, card=None):
		NodePath.__init__(self, type(card).__name__ + "_Secret")
		#These attributes will be modified by load functions below
		self.card = card
		self.selected = False
		self.GUI = GUI
		
		#Attributes that require changing constantly
		self.manaText = self.attackText = self.healthText = self.durabilityText = self.armorText = None
		self.descriptionText = None
		self.card_Model = self.nameTag_Model = self.cardImage_Model = None
		self.box_Model = None  #Indicate if the card is available for play
		
		self.collNode_Backup = CollisionNode("%s_c_node"%card.name)
		self.collNode_Backup.addSolid(CollisionSphere(0, 0, 0, 0.4))
		self.collNode = self.attachNewNode(self.collNode_Backup)
		
	#Assuming the secret icon changes very fast and doesn't need to multithread
	def changeCard(self, card, pickable=True):
		self.card = card
		if pickable: card.btn = self
		self.name = type(card).__name__ + "_Secret_" + str(datetime.now().time())
		if pickable and not self.collNode:
			self.collNode = self.attachNewNode(self.collNode_Backup)
		elif not pickable and self.collNode:
			self.collNode.removeNode()
			self.collNode = None
		
		self.card_Model.removeNode()
		self.card_Model = self.GUI.loader.loadModel("Models\\SecretIcon_%s.glb"%card.Class)
		self.card_Model.reparentTo(self)
		self.refresh()
		
	def dimDown(self):
		self.setColor(grey)
	
	def setBoxColor(self, color):
		pass
		
	def refresh(self, color=False, stat=False, indicator=False, all=True):
		hpr = None
		if self.card.ID == self.GUI.Game.turn and self.get_h() % 360 == 0:
			hpr = Point3(180, 0, 0) #Flip to back, unusable
		elif self.card.ID != self.GUI.Game.turn and self.get_h() % 360 == 180:
			hpr = Point3(0, 0, 0)
		if hpr:
			self.GUI.animate(LerpHprInterval(self, duration=0.3, hpr=hpr), afterAllFinished=False)

	def leftClick(self):
		pass
	
	def rightClick(self):
		if self.GUI.UI in (1, 2): self.GUI.cancelSelection()
		else: self.GUI.drawCardSpecsDisplay(self)


def loadSecret_Played(base, card):
	loader = base.loader
	
	root = NodePath_Secret(base, card)
	root.reparentTo(base.render)
	
	root.card_Model = loader.loadModel("Models\\SecretIcon_%s.glb"%card.Class)
	root.card_Model.reparentTo(root)
	
	root.setPos(BackupModelPos)
	return root



class NodePath_TurnTrig(NodePath):
	def __init__(self, GUI, card=None):
		NodePath.__init__(self, card.name + "_TurnTrig")
		#These attributes will be modified by load functions below
		self.card = card
		self.selected = False
		self.GUI = GUI
		
		self.card_Model = None
		collNode_Backup = CollisionNode("%s_c_node"%card.name)
		collNode_Backup.addSolid(CollisionBox(Point3(0, 0, 0), 0.45, 0.1, 0.45))
		self.attachNewNode(collNode_Backup)
		
	def dimDown(self):
		self.setColor(grey)
		
	def leftClick(self):
		pass
		
	def rightClick(self):
		if self.GUI.UI in (1, 2): self.GUI.cancelSelection()
		else: self.GUI.drawCardSpecsDisplay(self)
	
	def refresh(self, color=False, stat=False, indicator=False, all=True):
		pass
	
	def setBoxColor(self, color):
		pass

class NodePath_Dormant(NodePath_Card):
	def __init__(self, GUI, card=None):
		NodePath.__init__(self, card.name + "_Dormant")
		#These attributes will be modified by load functions below
		self.card = card
		self.selected = False
		self.GUI = GUI
		
		#Attributes that require changing constantly
		self.descriptionText = self.descriptionTextNode = None
		self.card_Model = self.description_Model = None
		self.box_Model = None  #Indicate if the card is available for play
		
	def changeCard(self, card, pickable=False):
		loader = self.GUI.loader
		rarityChanged = (not hasattr(card, "prisoner") and "~Legendary" in type(card).index) != \
							(not hasattr(self.card, "prisoner") and "~Legendary" in type(self.card).index)
		self.card = card
		#Dormant card is never pickable, so need to change the card.btn
		self.name = type(card).__name__ + "_Dormant_" + str(datetime.now().time())
		imgPath = findFilepath(card)
		threading.Thread(target=self.reloadModels, args=(loader, imgPath, rarityChanged, False)).start()
		
	def reloadModels(self, loader, imgPath, rarityChanged, pickable):
		card = self.card
		
		"""The card frame. The front face texture is set according to it class"""
		if rarityChanged:
			isLegendary = not hasattr(card, "prisoner") and "~Legendary" in type(card).index
			self.cardImage_Model.removeNode()
			self.cardImage_Model = loader.loadModel("Models\\MinionModels\\" + ("MinionImage_Legendary.glb" if isLegendary else "MinionImage.glb"))
			self.cardImage_Model.reparentTo(self)
			self.legendaryIcon.setColor(white if isLegendary else transparent)
		
		texture = loader.loadTexture(imgPath)
		self.card_Model.setTexture(self.card_Model.findTextureStage('*'),
									texture, 1)
		text = card.text(CHN)
		if text:
			self.description_Model.setTexture(self.description_Model.findTextureStage('*'),
											loader.loadTexture("Models\\MinionModels\\Vanilla_%s.png" % card.index.split('~')[0]), 1)
			self.descriptionText.setText(text)
			self.descriptionTextNode.setPos(0, -0.2, -3+0.1*len(text) / 12)
		else:
			self.description_Model.setTexture(self.description_Model.findTextureStage('*'),
											texture, 1)
		
		self.refresh()
		
	def leftClick(self):
		self.selected = not self.selected
		pass
		
	def refresh(self, color=False, stat=False, indicator=False, all=True):
		if self.descriptionText: self.descriptionText.setText(self.card.text(CHN))
		
	def decideColor(self):
		return transparent
		
		
class NodePath_DormantPlayed(NodePath_Card):
	def __init__(self, GUI, card=None):
		NodePath.__init__(self, card.name + "_DormantPlayed")
		self.card = card
		self.selected = False
		self.GUI = GUI
		
		self.nameTag_Model = self.cardImage_Model = None
		self.box_Model = None  #Indicate if the card is available for play
		
		self.indicatorModels = {}
		
		self.collNode_Backup = CollisionNode("%s_c_node" % card.name)
		self.collNode_Backup.addSolid(CollisionBox(Point3(0, 0, 0), 2.4, 0.3, 3))
		self.collNode = self.attachNewNode(self.collNode_Backup)
	
	def changeCard(self, card, pickable=True):
		loader = self.GUI.loader
		rarityChanged = (not hasattr(card, "prisoner") and "~Legendary" in type(card).index) != \
						(not hasattr(self.card, "prisoner") and "~Legendary" in type(self.card).index)
		card.btn = self
		self.card = card
		self.name = type(card).__name__ + "_DormantPlayed_" + str(datetime.now().time())
		imgPath = findFilepath(card)
		threading.Thread(target=self.reloadModels, args=(loader, imgPath, rarityChanged, True)).start()
		#print("btn for card", card, card.btn)
	
	def reloadModels(self, loader, imgPath, rarityChanged, pickable):
		card = self.card
		if rarityChanged:
			isLegendary = not hasattr(card, "prisoner") and "~Legendary" in type(card).index
			self.legendaryIcon.setColor(white if isLegendary else transparent)
		
		if pickable and not self.collNode:
			self.collNode = self.attachNewNode(self.collNode_Backup)
		elif not pickable and self.collNode:
			self.collNode.removeNode()
			self.collNode = None
		
		texture = loader.loadTexture(imgPath)
		self.cardImage_Model.setTexture(self.cardImage_Model.findTextureStage('*'),
										texture, 1)
		self.nameTag_Model.setTexture(self.nameTag_Model.findTextureStage('*'),
									  texture, 1)
		self.refresh()
	
	def leftClick(self):
		pass
		
	def refresh(self, color=False, stat=False, indicator=False, all=True):
		#A Dormant is never selectable
		if indicator or all:
			self.indicatorModels["Trigger"].setPos(0, 0, 0)
			self.indicatorModels["Trigger"].updateText()
			#self.indicatorModels["Trigger"].updateText()
			#color = (1, 1, 1, 0.4) if self.card.auras else transparent
			self.indicatorModels["Aura"].setColor(transparent)

	def decideColor(self):
		return transparent


def loadDormant(base, card=None, cardType=None, pickable=True):
	loader = base.loader
	if card:
		imgPath = findFilepath(card)
	else:
		imgPath = "Images\\%s\\" % cardType.index.split('~')[0] + cardType.__name__ + ".png"
	sansBold = loader.loadFont('Models\\OpenSans-Bold.ttf')
	cardImgTexture = loader.loadTexture(imgPath)
	
	if card:
		root = NodePath_Dormant(base, card=card)
	else:
		root = NodePath_Card(base, cardType=cardType, collBox4="Hand" if pickable else '')
	root.reparentTo(base.render)
	
	if card:
		isLegendary = not hasattr(card, "prisoner") and "~Legendary" in type(card).index
	else:
		isLegendary = "~Legendary" in cardType.index
	"""The card frame. The front face texture is set according to it class"""
	filePath = "Models\\MinionModels\\%s.glb" % ("Card_Legendary" if isLegendary else "Card")
	root.card_Model = loader.loadModel(filePath)
	root.card_Model.reparentTo(root)
	root.card_Model.setTexture(root.card_Model.findTextureStage('*'),
							   cardImgTexture, 1)
	
	"""Card image based on the card type"""
	filePath = "Models\\MinionModels\\" + ("MinionImage_Legendary.glb" if isLegendary else "MinionImage.glb")
	root.cardImage_Model = loader.loadModel(filePath)
	root.cardImage_Model.reparentTo(root)
	root.cardImage_Model.setTexture(root.cardImage_Model.findTextureStage('*'),
									cardImgTexture, 1)
	
	"""Name Tag of the card, includes the model, and the nameText"""
	root.nameTag_Model = loader.loadModel("Models\\MinionModels\\NameTag.glb")
	root.nameTag_Model.reparentTo(root)
	root.nameTag_Model.setTexture(root.nameTag_Model.findTextureStage('*'),
								  cardImgTexture, 1)
	
	root.legendaryIcon = loader.loadModel("Models\\MinionModels\\LegendaryIcon.glb")
	root.legendaryIcon.reparentTo(root)
	root.legendaryIcon.setTransparency(True)
	root.legendaryIcon.setTexture(root.legendaryIcon.findTextureStage('*'),
								  loader.loadTexture("Models\\MinionModels\\LegendaryExample.png"), 1)
	
	mana_Model = loader.loadModel("Models\\MinionModels\\Mana.glb")
	mana_Model.reparentTo(root)
	mana_Model.setTexture(mana_Model.findTextureStage('*'),
						  loader.loadTexture("Models\\MinionModels\\MinionStats.png"), 1)

	"""Description and race of the card"""
	root.description_Model = loader.loadModel("Models\\MinionModels\\Description.glb")
	root.description_Model.reparentTo(root)
	if card and card.text(CHN):
		text = card.text(CHN)
		root.description_Model.setTexture(root.description_Model.findTextureStage('*'),
										  loader.loadTexture("Models\\MinionModels\\Vanilla_%s.png" % card.index.split('~')[0]), 1)
		root.descriptionText = TextNode("Description Text Node")
		root.descriptionText.setText(text)
		root.descriptionText.setAlign(TextNode.ACenter)
		root.descriptionText.setFont(sansBold)
		root.descriptionText.setTextColor(0, 0, 0, 1)
		root.descriptionText.setWordwrap(12)
		root.descriptionTextNode = root.attachNewNode(root.descriptionText)
		root.descriptionTextNode.setScale(0.4)
		root.descriptionTextNode.setPos(0, -0.2, -2.5 + 0.1 * len(text) / 12)
	else:
		root.description_Model.setTexture(root.description_Model.findTextureStage('*'),
										  cardImgTexture, 1)
	
	root.setPos(BackupModelPos)
	return root


def loadDormant_Played(base, card):
	loader = base.loader
	imgPath = findFilepath(card)
	sansBold = loader.loadFont('Models\\OpenSans-Bold.ttf')
	cardImgTexture = loader.loadTexture(imgPath)
	
	root = NodePath_DormantPlayed(base, card)
	root.reparentTo(base.render)
	
	"""Card image based on the card type"""
	root.cardImage_Model = loader.loadModel("Models\\MinionModels\\MinionImage_Played.glb")
	root.cardImage_Model.reparentTo(root)
	root.cardImage_Model.setTexture(root.cardImage_Model.findTextureStage('*'),
						 cardImgTexture, 1)
	
	"""Name Tag of the card, includes the model, and the nameText"""
	root.nameTag_Model = loader.loadModel("Models\\MinionModels\\NameTag_Played.glb")
	root.nameTag_Model.reparentTo(root)
	root.nameTag_Model.setTexture(root.nameTag_Model.findTextureStage('*'),
					cardImgTexture, 1)
	
	root.legendaryIcon = loader.loadModel("Models\\MinionModels\\LegendaryIcon_Played.glb")
	root.legendaryIcon.reparentTo(root)
	root.legendaryIcon.setTransparency(True)
	root.legendaryIcon.setTexture(root.legendaryIcon.findTextureStage('*'),
								  loader.loadTexture("Models\\MinionModels\\LegendaryExample.png"), 1)
	
	"""Define the models that indicate the keywords of the minion, for example, Taunt"""
	trig_Model = loadTrigger(root) #TriggerModel(root, "Models\\MinionModels\\Trigger.glb")
	trig_Model.setTransparency(True)
	trig_Model.reparentTo(root)
	root.indicatorModels["Trigger"] = trig_Model
	
	model = loader.loadModel("Models\\MinionModels\\Aura.glb")
	model.setTransparency(True)
	model.reparentTo(root)
	root.indicatorModels["Aura"] = model
	
	root.setPos(BackupModelPos)
	return root


class TriggerModel(NodePath):
	def __init__(self, carrier):
		NodePath.__init__(self, "Trig_NodePath")
		self.carrier = carrier
		self.model = self.counterText = self.counterTextNode = None
		
	def trigAni(self, blockwhilePlaying=False):
		self.updateText()
		pos_Orig = self.getPos()
		seq = Sequence(LerpPosHprScaleInterval(self, pos=(0, -0.3, 12), hpr=Point3(0, 0, 0), scale=3, duration=0.15),
				 		Wait(0.3), LerpPosHprScaleInterval(self, pos=pos_Orig, hpr=Point3(0, 0, 0), scale=1, duration=0.15)
				 		)
		self.carrier.GUI.animate(seq, afterAllFinished=True, blockwhilePlaying=blockwhilePlaying)
		
	def updateText(self):
		s = ""
		#print("updating trig text for carrier", self.carrier, self.carrier.card)
		for trig in self.carrier.card.trigsBoard:
			if hasattr(trig, "counter"):
				s += str(trig.counter) + ' '
		self.counterText.setText(s)
		
def loadTrigger(carrier):
	loader = carrier.GUI.loader
	card = carrier.card
	if card.type == "Minion" or card.type == "Dormant": modelFile = "Models\\MinionModels\\Trigger.glb"
	elif card.type == "Weapon": modelFile = "Models\\WeaponModels\\Trigger.glb"
	root_Trig = TriggerModel(carrier)
	root_Trig.model = loader.loadModel(modelFile)
	root_Trig.model.reparentTo(root_Trig)
	root_Trig.counterText = TextNode("Trig Counter")
	root_Trig.counterText.setTextColor(white)
	root_Trig.updateText()
	root_Trig.counterText.setAlign(TextNode.ACenter)
	root_Trig.counterTextNode = root_Trig.attachNewNode(root_Trig.counterText)
	root_Trig.counterTextNode.setPos(0, -0.2, -4.7)
	root_Trig.counterTextNode.setScale(0.9)
	return root_Trig
	
	
class ChooseOptionModel(NodePath):
	def __init__(self, GUI, card=None):
		NodePath.__init__(self, type(card).__name__ + "_Option")
		#These attributes will be modified by load functions below
		self.card = card
		self.selected = False
		self.GUI = GUI
		
		self.card_Model = self.descriptionText = self.description_Model = None
		
		self.collNode_Backup = CollisionNode("%s_c_node" % card.name)
		self.collNode_Backup.addSolid(CollisionBox(Point3(0, 0, 0), 3.5, 0.3, 5))
		self.collNode = self.attachNewNode(self.collNode_Backup)
	
	def changeCard(self, card, pickable=True):
		loader = self.GUI.loader
		self.card = card
		card.btn = self
		self.name = type(card).__name__ + "_Option_" + str(datetime.now().time())
		texture = loader.loadTexture(findFilepath(card))
		self.card_Model.setTexture(self.card_Model.findTextureStage('*'),
								   texture, 1)
		text = card.text(CHN)
		if text:
			self.description_Model.setTexture(self.description_Model.findTextureStage('*'),
											  loader.loadTexture("Models\\SpellModels\\Vanilla_%s.png" % card.index.split('~')[0]), 1)
			self.descriptionText.setText(text)
			self.descriptionTextNode.setPos(0, -0.2, -3 + 0.1 * len(text) / 12)
		else:
			self.description_Model.setTexture(self.description_Model.findTextureStage('*'),
											  texture, 1)

	def leftClick(self):
		self.GUI.resolveMove(self.card, self, "ChooseOneOption")
		
	def rightClick(self):
		pass
	
	
def loadChooseOption(base, card):
	loader = base.loader
	imgPath = findFilepath(card)
	sansBold = loader.loadFont('Models\\OpenSans-Bold.ttf')
	cardImgTexture = loader.loadTexture(imgPath)
	
	root = ChooseOptionModel(base, card)
	root.reparentTo(base.render)
	
	"""Card image based on the card type"""
	root.card_Model = loader.loadModel("Models\\SpellModels\\Card.glb")
	root.card_Model.reparentTo(root)
	root.card_Model.setTexture(root.card_Model.findTextureStage('*'),
								cardImgTexture, 1)
	root.description_Model = loader.loadModel("Models\\SpellModels\\Description.glb")
	text = card.text(CHN)
	root.descriptionText = TextNode("Description Text Node")
	root.descriptionText.setText(text)
	root.descriptionText.setAlign(TextNode.ACenter)
	root.descriptionText.setFont(sansBold)
	root.descriptionText.setTextColor(0, 0, 0, 1)
	root.descriptionText.setWordwrap(12)
	root.descriptionTextNode = root.attachNewNode(root.descriptionText)
	root.descriptionTextNode.setScale(0.44)
	root.descriptionTextNode.setPos(0, -0.2, -3 + 0.1 * len(text) / 12)
	if text:
		root.description_Model.reparentTo(root)
		root.description_Model.setTexture(root.description_Model.findTextureStage('*'),
										  loader.loadTexture("Models\\SpellModels\\Vanilla_%s.png" % card.index.split('~')[0]), 1)
	else:
		root.description_Model.setTexture(root.description_Model.findTextureStage('*'),
										  cardImgTexture, 1)

	return root