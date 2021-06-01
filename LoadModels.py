from direct.interval.FunctionInterval import Func, Wait
from direct.interval.LerpInterval import *
from direct.interval.MetaInterval import Sequence
from direct.directutil import Mopath
from direct.interval.MopathInterval import *
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
			#"20 Dalaran", "21 Uldum Desert", "22 Uldum Oasis", "23 Dragons",
			"24 Outlands", "25 Scholomance Academy", "26 Darkmoon Faire",
			]


#Not used for finding Hero Head, or Hero Power. Hero cards are included in each expansion folder
def findFilepath(card): #card is an instance
	if card.type == "Dormant":
		if card.minionInside:
			name = card.minionInside.__name__ if inspect.isclass(card.minionInside) else type(card.minionInside).__name__
			return "Images\\%s\\%s.png"%(card.minionInside.index.split('~')[0], name)
		else: return "Images\\%s\\%s.png"%(card.index.split('~')[0], type(card).__name__)
	elif "Option" in card.type:
		return "Images\\Options\\%s.png"%type(card).__name__
	elif card.type in ("Minion", "Weapon", "Spell", "Hero"):  #type == "Weapon", "Minion", "Spell", "Hero", "Power"
		return "Images\\%s\\%s.png"%(card.index.split('~')[0], type(card).__name__)
	elif card.type == "Power":
		return "Images\\HeroesandPowers\\%s.png"%type(card).__name__
	
	
red, green, blue = Point4(1, 0, 0, 1), Point4(0.3, 1, 0.2, 1), Point4(0, 0, 1, 1)
yellow, pink = Point4(1, 1, 0, 1), Point4(1, 0, 1, 1)

transparent, grey = Point4(1, 1, 1, 0), Point4(0.5, 0.5, 0.5, 1)
black, white = Point4(0, 0, 0, 1), Point4(1, 1, 1, 1)


#Can only set the color of the textNode itself to transparent. No point in setting the nodePath transparency
def makeText(np_Parent, textName, valueText, pos, scale, color, font, wordWrap=0):
	textNode = TextNode(textName + "_TextNode")
	textNode.setText(valueText)
	textNode.setAlign(TextNode.ACenter)
	textNode.setFont(font)
	textNode.setTextColor(color)
	if wordWrap > 0:
		textNode.setWordwrap(wordWrap)
	textNodePath = np_Parent.attachNewNode(textNode)
	textNodePath.setScale(scale)
	textNodePath.setPos(pos)
	return textNodePath

"""Subclass the NodePath, since it can be assigned attributes directly"""
class Btn_Card:
	def __init__(self, GUI, card, nodePath):
		self.GUI, self.card = GUI, card
		self.selected = self.isPlayed = False
		
		self.np = nodePath #Load the templates, who won't carry btn and then btn will be assigned after copyTo()
		self.cNode = self.cNode_Backup = self.cNode_Backup_Played = None  #cNode holds the return value of attachNewNode
		self.box_Model = None
		self.models, self.icons, self.texts, self.texCards = {}, {}, {}, {}
		
	def changeCard(self, card, isPlayed, pickable=True):
		self.card, self.isPlayed = card, isPlayed
		loader = self.GUI.loader
		if pickable: card.btn = self
		threading.Thread(target=self.reloadModels, args=(loader, findFilepath(card), pickable)).start()
	
	def dimDown(self):
		self.np.setColor(grey)
		
	def setBoxColor(self, color):
		if self.box_Model: self.box_Model.setColor(color)
	
	def showStatus(self):
		pass
	
	def rightClick(self):
		if self.GUI.UI in (1, 2): self.GUI.cancelSelection()
		else: self.GUI.drawCardSpecsDisplay(self)
	
	#Control the moving, rotating and scaling of a nodePath. For color manipulate, another method is used.
	def genLerpInterval(self, pos=None, hpr=None, scale=None, duration=0.3, blendType="noBlend"):
		pos = pos if pos else self.np.getPos()
		hpr = hpr if hpr else self.np.getHpr()
		scale = scale if scale else self.np.getScale()
		return LerpPosHprScaleInterval(self.np, duration=duration, pos=pos, hpr=hpr, scale=scale, blendType=blendType)
	
	def genMoPathIntervals(self, curveFileName, duration=0.3):
		moPath = Mopath.Mopath()
		moPath.loadFile(curveFileName)
		return MopathInterval(moPath, self.np, duration=duration)
	
	#For the selfCopy method, this will simply return a None
	def selfCopy(self, Copy):
		return None
	
def loadCard(base, card):
	return {"Minion": loadMinion, "Spell": loadSpell, "Weapon": loadWeapon, "Hero": loadHero,
			"Power": loadPower, "Dormant": loadDormant,
			"Option_Spell": loadOption_Spell, "Option_Minion": loadOption_Minion
			}[card.type](base)
	
	
#Minion: cardImage y limit -0.06; nameTag -0.07; stats_Played -0.12
table_PosScaleofTexCard_Minions = {"Aura": (0.057, (0, -0.03, 0.3)),
							   		"Damage": (0.045, (0.15, -0.14, 0.45)),
							   		"DamagePoisonous": (0.045, (0.15, -0.143, 0.45)),
							   		"Divine Shield": (7.3, (0.05, -0.078, 0.2)),
							   		"Exhausted": (5, (0.1, -0.062, 0.5)),
							   		"Frozen": (5.2, (0, -0.08, 0.55)),
							   		"Immune": (4.5, (0.05, -0.076, 0.5)),
							   		"Silenced": (4, (0, -0.068, 0)),
							   		"Spell Damage": (4, (0, -0.07, 1)),
							   		"Stealth": (4.2, (0.1, -0.064, 0.5)),
							   		"Taunt": (0.044, (0.05, 0, -0.05)),
							   		}

class Btn_Minion(Btn_Card):
	def __init__(self, GUI, card, nodePath):
		super().__init__(GUI, card, nodePath)
		
		self.cNode_Backup = CollisionNode("Minion_cNode_Card")
		self.cNode_Backup.addSolid(CollisionBox(Point3(0.05, 0, -1.1), 2.2, 0.1, 3.1))
		self.cNode_Backup_Played = CollisionNode("Minion_cNode_Played")
		self.cNode_Backup_Played.addSolid(CollisionBox(Point3(0.07, 0, 0.35), 1.5, 0.1, 1.9))
		#self.cNode = self.attachNewNode(self.cNode_Backup)
		
	def reloadModels(self, loader, imgPath, pickable):
		card = self.card
		if self.isPlayed: color4Card, color4Played = transparent, white
		else: color4Card, color4Played = white, transparent
		isLegendary = "~Legendary" in card.index
		self.models["legendaryIcon"].setColor(white if isLegendary else transparent)
		self.models["box_Legendary"].setColor(transparent)
		self.models["box_Normal"].setColor(transparent)
		self.models["box_Legendary_Played"].setColor(transparent)
		self.models["box_Normal_Played"].setColor(transparent)
		if isLegendary: self.box_Model = self.models["box_Legendary_Played" if self.isPlayed else "box_Legendary"]
		else: self.box_Model = self.models["box_Normal_Played" if self.isPlayed else "box_Normal"]
		
		if pickable and not self.cNode:
			self.cNode = self.np.attachNewNode(self.cNode_Backup_Played if self.isPlayed else self.cNode_Backup)
			self.cNode.show()
		elif not pickable and self.cNode:
			self.cNode.removeNode()
			self.cNode = None
		
		cardTexture = loader.loadTexture(imgPath)
		for modelName in ("card", "cardImage", "nameTag", "race"):
			self.models[modelName].setTexture(self.models[modelName].findTextureStage('*'), cardTexture, 1)
		#Change the card textNodes no matter what (non-mutable texts are empty anyways)
		text = card.text(CHN)
		textNodePath = self.texts["description"]
		textNodePath.node().setText(text)
		textNodePath.setPos(0, -0.2, -3 + 0.1 * len(text) / 12)
		textNodePath.node().setTextColor(black if not self.isPlayed and text else transparent)
		if not self.isPlayed and text:
			model = self.models["description"]
			model.setTexture(model.findTextureStage('*'),
							self.GUI.textures["minion_%s" % card.index.split('~')[0]], 1)
			model.setColor(white)
		else: self.models["description"].setColor(transparent)
		
		for modelName in ("cardImage", "nameTag"):
			self.models[modelName].setColor(white)
		for modelName in ("stats", "cardBack", "card", "race"):
			self.models[modelName].setColor(color4Card)
		self.models["stats_Played"].setColor(color4Played)
		
		self.refresh()
		
	def leftClick(self):
		self.selected = not self.selected
		GUI, card = self.GUI, self.card
		UI, game = GUI.UI, GUI.Game
		if self.isPlayed: #When the minion is on board
			if UI == 0 or UI == 2:
				self.GUI.resolveMove(self.card, self, "MiniononBoard")
		else: #When the minion is in hand
			if UI == -2:
				self.setBoxColor(red if self.selected else green)
				GUI.mulliganStatus[card.ID][game.mulligans[card.ID].index(card)] = 1 if self.selected else 0
			elif UI == -1 or UI == 1: pass #lock out any selection
			elif UI == 3:
				if card in game.options:
					GUI.resolveMove(card, None, "DiscoverOption", info=None)
			else: GUI.resolveMove(card, self, "MinioninHand")
		
	def refresh(self, color=False, stat=False, indicator=False, all=True):
		#Change the box color to indicate the selectability of a card
		if color or all: self.setBoxColor(self.decideColor())
		
		card, GUI = self.card, self.GUI
		cardType, game = type(card), card.Game
		"""Reset the stats of the card"""
		if stat or all:
			#Refresh the mana
			color = white if card.mana == cardType.mana else (green if card.mana < cardType.mana else red)
			self.texts["mana"].node().setText(str(card.mana))
			self.texts["mana"].node().setTextColor(transparent if self.isPlayed else color)
			#Refresh the attack
			color = white if card.attack <= card.attack_0 else green
			self.texts["attack"].node().setText(str(card.attack))
			self.texts["attack"].node().setTextColor(transparent if self.isPlayed else color)
			self.texts["attack_Played"].node().setText(str(card.attack))
			self.texts["attack_Played"].node().setTextColor(color if self.isPlayed else transparent)
			#Refresh the health
			color = white if card.health == card.health_max else (green if card.health == card.health_max else red)
			self.texts["health"].node().setText(str(card.health))
			self.texts["health"].node().setTextColor(transparent if self.isPlayed else color)
			self.texts["health_Played"].node().setText(str(card.health))
			self.texts["health_Played"].node().setTextColor(color if self.isPlayed else transparent)
			#Refresh the description if applicable
			self.texts["description"].node().setText(card.text(CHN))
			
	def decideColor(self):
		color, card = transparent, self.card
		game = card.Game
		if card == self.GUI.subject: color = pink
		elif card == self.GUI.target: color = blue
		else:
			if self.isPlayed:
				if card.ID == game.turn and game.Manas.affordable(card) and game.space(card.ID) > 0:
					color = yellow if card.effectViable else green
			elif card.canAttack(): color = green #If this is a minion that is on board
		return color
		
	#Place the "Trigger", "Deathrattle", "Lifesteal", "Poisonous" icons at the right places
	def placeIcons(self):
		for name in ("Trigger", "Deathrattle", "Lifesteal", "Poisonous"):
			self.icons[name].np.setColor(transparent)
		if self.isPlayed:
			icons = [] #Place the icons, depending on the number of trigs to show
			if self.card.trigsBoard:
				self.icons["Trigger"].updateText()
				icons.append(self.icons["Trigger"])
			if self.card.deathrattles:
				icons.append(self.icons["Deathrattle"])
			for keyWord in ("Lifesteal", "Poisonous"):
				if self.card.keyWords[keyWord] > 0:
					icons.append(self.icons[keyWord])
			leftMostPos = -0.6 * (len(icons) - 1) / 2
			for i, model in enumerate(icons):
				model.np.setColor(white)
				model.np.setPos(leftMostPos + i * 0.6, -0.1, -1.9)
	
	def manageStatusTexCards(self):
		minion = self.card
		if minion.auras: self.texCards["Aura"].find("+SequenceNode").node().loop(False)
		if minion.keyWords["Divine Shield"] > 0: self.texCards["Divine Shield"].find("+SequenceNode").node().play(1, 20)
		if minion.canAttack(): self.texCards["Exhausted"].find("+SequenceNode").node().loop(False, 1, 24)
		if minion.status["Frozen"] > 0: self.texCards["Frozen"].find("+SequenceNode").node().loop(False, 1, 96)
		if minion.status["Immune"] > 0: self.texCards["Immune"].find("+SequenceNode").node().loop(False, 1, 100)
		if minion.silenced: self.texCards["Silenced"].find("+SequenceNode").node().loop(True, 1, 71)
		if minion.keyWords["Spell Damage"] + minion.keyWords["Nature Spell Damage"] > 0:
			seqNode = self.texCards["Spell Damage"].find("+SequenceNode").node()
			Sequence(Func(seqNode.play, 1, 13), Func(seqNode.loop, True, 1, 71)).start()
		if minion.keyWords["Stealth"] + minion.status["Temp Stealth"] > 0:
			self.texCards["Stealth"].find("+SequenceNode").node().loop(False, 1, 119)
		if minion.keyWords["Taunt"]: self.texCards["Taunt"].find("+SequenceNode").node().play(1, 13)
		
statTextScale = 1.05
manaPos = Point3(-2.8, -0.15, 3.85)
healthPos = Point3(3.1, -0.2, -4.95)
attackPos = Point3(-2.85, -0.15, -4.95)


#loadMinion, etc will prepare all the textures and trigIcons to be ready.
def loadMinion(base):
	loader = base.loader
	sansBold = base.font
	root = loader.loadModel("Models\\MinionModels\\Minion.glb")
	root.name = "NP_Minion"
	
	#Model names: box_Legendary, box_Legendary_Played, box_Normal, box_Normal_Played
	# card, cardBack, cardImage, description, legendaryIcon, nameTag, race, stats, stats_Played
	for model in root.getChildren():
		model.setTransparency(True)
		#Only retexture the cardBack, legendaryIcon, stats, stats_Played models.
		#These models will be shared by all minion cards.
		if model.name == "cardBack": texture = base.textures["cardBack"]
		elif model.name in ("legendaryIcon", "stats", "stats_Played"): texture = base.textures["stats_Minion"]
		else: continue
		model.setTexture(model.findTextureStage('*'), texture, 1)
	
	makeText(root, "mana", '0', pos=(-1.8, -0.09, 1.15), scale=statTextScale,
			 color=white, font=sansBold)
	makeText(root, "attack", '0', pos=(-1.7, -0.09, -4.05), scale=statTextScale,
			 color=white, font=sansBold)
	makeText(root, "health", '0', pos=(1.8, -0.09, -4.05), scale=statTextScale,
			 color=white, font=sansBold)
	makeText(root, "attack_Played", '0', pos=(-1.2, -0.122, -0.74), scale=0.8,
			 color=white, font=sansBold)
	makeText(root, "health_Played", '0', pos=(1.32, -0.122, -0.74), scale=0.8,
			 color=white, font=sansBold)
	makeText(root, "description", "", pos=(0, 0, 0), scale=0.3,
			 color=black, font=sansBold, wordWrap=12)
	base.modelTemplates["Trigger"].copyTo(root)
	base.modelTemplates["Deathrattle"].copyTo(root)
	base.modelTemplates["Lifesteal"].copyTo(root)
	base.modelTemplates["Poisonous"].copyTo(root)
	
	for name, posScale in table_PosScaleofTexCard_Minions.items():
		texCard = loader.loadModel("TexCards\\ForMinions\\%s.egg" % name)
		texCard.name = name + "_TexCard"
		texCard.reparentTo(root)
		texCard.setScale(posScale[0])
		texCard.setPos(posScale[1])
		texCard.find("+SequenceNode").node().pose(0)
	
	#After the loading, the NP_Minion root tree structure is:
	#NP_Minion/card|stats|cardImage, etc
	#NP_Minion/mana_TextNode|attack_TextNode, etc
	#NP_Minion/Trigger_Icon|Deathrattle_Icon, etc
	#NP_Minion/Aura_TexCard, etc
	return root


"""Load Spell Cards"""
class Btn_Spell(Btn_Card):
	def __init__(self, GUI, card, nodePath):
		super().__init__(GUI, card, nodePath)
		
		self.cNode_Backup = CollisionNode("Spell_cNode")
		self.cNode_Backup.addSolid(CollisionBox(Point3(0.05, 0, -1.1), 2.2, 0.1, 3.1))
		
	def reloadModels(self, loader, imgPath, pickable):
		card = self.card
		isLegendary = "~Legendary" in card.index
		self.models["legendaryIcon"].setColor(white if isLegendary else transparent)
		self.models["box_Normal"].setColor(transparent)
		self.models["box_Legendary"].setColor(transparent)
		self.box_Model = self.models["box_Legendary" if isLegendary else "box_Normal"]
		
		if pickable and not self.cNode:
			self.cNode = self.np.attachNewNode(self.cNode_Backup)
			self.cNode.show()
		elif not pickable and self.cNode:
			self.cNode.removeNode()
			self.cNode = None
		
		texture = loader.loadTexture(imgPath)
		for modelName in ("card", "school"):
			self.models[modelName].setTexture(self.models[modelName].findTextureStage('*'), texture, 1)
	
		text = card.text(CHN)
		textNodePath = self.texts["description"]
		textNodePath.node().setText(text)
		textNodePath.setPos(0, -0.2, -3 + 0.1 * len(text) / 12)
		textNodePath.node().setTextColor(black if not self.isPlayed and text else transparent)
		if not self.isPlayed and text:
			model = self.models["description"]
			model.setTexture(model.findTextureStage('*'),
							self.GUI.textures["spell_%s"%card.index.split('~')[0]], 1)
			model.setColor(white)
		else: self.models["description"].setColor(transparent)
		
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
		if color or all: self.setBoxColor(self.decideColor())
		
		card = self.card
		cardType = type(card)
		"""Reset the stats of the card"""
		if stat or all:
			#Refresh the mana
			color = white if card.mana == cardType.mana else (red if card.mana > cardType.mana else green)
			self.texts["mana"].node().setText(str(card.mana))
			self.texts["mana"].node().setTextColor(color)
		#Refresh the description if applicable
		self.texts["description"].node().setText(card.text(CHN))
	
	def decideColor(self):
		color, card = transparent, self.card
		if card == self.GUI.subject: color = pink
		elif card == self.GUI.target: color = blue
		else:
			if card.inHand and card.ID == card.Game.turn and card.Game.Manas.affordable(card) and card.available():
				color = yellow if card.effectViable else green
		return color
		
		
def loadSpell(base):
	loader = base.loader
	sansBold = base.font
	root = loader.loadModel("Models\\SpellModels\\Spell.glb")
	root.name = "NP_Spell"
	
	#Model names: box_Legendary, box_Normal, card, cardBack, description, legendaryIcon, mana, school
	for model in root.getChildren():
		model.setTransparency(True)
		if model.name == "cardBack": texture = base.textures["cardBack"]
		elif model.name in ("mana", "legendaryIcon"): texture = base.textures["stats_Spell"]
		else: continue
		model.setTexture(model.findTextureStage('*'), texture, 1)
	
	makeText(root, "mana", '0', pos=(-1.73, -0.09, 1.2), scale=statTextScale,
			 color=white, font=sansBold, wordWrap=0)
	makeText(root, "description", '', pos=(0, 0, 0), scale=0.25,
			 color=black, font=sansBold, wordWrap=12)
	#After the loading, the NP_Spell root tree structure is:
	#NP_Spell/card|cardBack|legendaryIcon, etc
	#NP_Spell/mana_TextNode|description_TextNode
	return root

#Weapon: cardImage y limit -0.09; nameTag -0.095; stats_Played -0.13
table_PosScaleofTexCard_Weapons = {"Immune": (3.7, (0.1, -0.12, 0.3)),
						   }

"""Load Weapon Cards"""
class Btn_Weapon(Btn_Card):
	def __init__(self, GUI, card, nodePath):
		super().__init__(GUI, card, nodePath)
		
		self.cNode_Backup = CollisionNode("Weapon_cNode_Card")
		self.cNode_Backup.addSolid(CollisionBox(Point3(0.05, 0, -1.1), 2.2, 0.1, 3.1))
		self.cNode_Backup_Played = CollisionNode("Weapon_cNode_Played")
		self.cNode_Backup_Played.addSolid(CollisionBox(Point3(0.07, 0, 0.33), 1.8, 0.1, 1.8))
		
	def reloadModels(self, loader, imgPath, pickable):
		card = self.card
		if self.isPlayed: color4Card, color4Played = transparent, white
		else: color4Card, color4Played = white, transparent
		isLegendary = "~Legendary" in card.index
		self.models["legendaryIcon"].setColor(white if isLegendary else transparent)
		self.models["box_Normal"].setColor(transparent)
		self.models["box_Legendary"].setColor(transparent)
		self.box_Model = None if self.isPlayed else self.models["box_Legendary" if isLegendary else "box_Normal"]
		
		if pickable and not self.cNode:
			self.cNode = self.np.attachNewNode(self.cNode_Backup)
			self.cNode.show()
		elif not pickable and self.cNode:
			self.cNode.removeNode()
			self.cNode = None
		
		self.models["card"].setTexture(self.models["card"].findTextureStage('*'),
									   self.GUI.textures["weapon_"+card.Class], 1)
	
		cardTexture = loader.loadTexture(imgPath)
		for modelName in ("cardImage", "nameTag", "description"):
			self.models[modelName].setTexture(self.models[modelName].findTextureStage('*'), cardTexture, 1)
			
		for modelName in ("cardImage", "nameTag"):
			self.models[modelName].setColor(white)
		for modelName in ("stats", "cardBack", "card", "description"):
			self.models[modelName].setColor(color4Card)
		self.models["stats_Played"].setColor(color4Played)
		self.texts["attack"].node().setTextColor(color4Card)
		self.texts["durability"].node().setTextColor(color4Card)
		self.texts["attack_Played"].node().setTextColor(color4Played)
		self.texts["durability_Played"].node().setTextColor(color4Played)
		
		self.refresh()
		
	def leftClick(self):
		if not self.isPlayed:
			self.selected = not self.selected
			GUI, card = self.GUI, self.card
			game = GUI.Game
			if GUI.UI == -2:
				self.setBoxColor(red if self.selected else green)
				GUI.mulliganStatus[card.ID][game.mulligans[card.ID].index(card)] = 1 if self.selected else 0
			elif GUI.UI == -1 or GUI.UI == 1: pass #lock out any selection
			elif GUI.UI == 3:
				if card in game.options:
					GUI.resolveMove(card, None, "DiscoverOption", info=None)
			else: GUI.resolveMove(card, self, "WeaponinHand")
		
	def refresh(self, color=False, stat=False, indicator=False, all=True):
		#Change the box color to indicate the selectability of a card
		if (color or all) and not self.isPlayed:
			self.setBoxColor(self.decideColor())
		
		card, GUI = self.card, self.GUI
		cardType, game = type(card), card.Game
		"""Reset the stats of the card"""
		if stat or all:
			#Refresh the mana
			color = white if card.mana == cardType.mana else (green if card.mana < cardType.mana else red)
			self.texts["mana"].node().setText(str(card.mana))
			self.texts["mana"].node().setTextColor(transparent if self.isPlayed else color)
			#Refresh the attack
			color = white if card.attack <= cardType.attack else green
			self.texts["attack"].node().setText(str(card.attack))
			self.texts["attack"].node().setTextColor(transparent if self.isPlayed else color)
			self.texts["attack_Played"].node().setText(str(card.attack))
			self.texts["attack_Played"].node().setTextColor(color if self.isPlayed else transparent)
			#Weapon durability
			color = white if card.durability >= cardType.durability else red
			self.texts["durability"].node().setText(str(card.durability))
			self.texts["durability"].node().setTextColor(transparent if self.isPlayed else color)
			self.texts["durability_Played"].node().setText(str(card.durability))
			self.texts["durability_Played"].node().setTextColor(color if self.isPlayed else transparent)
		
	#Place the "Trigger", "Deathrattle", "Lifesteal", "Poisonous" icons at the right places
	def placeIcons(self):
		for name in ("Trigger", "Deathrattle", "Lifesteal", "Poisonous"):
			self.icons[name].np.setColor(transparent)
		if self.isPlayed:
			icons = []  #Place the icons, depending on the number of trigs to show
			if self.card.trigsBoard:
				self.icons["Trigger"].updateText()
				icons.append(self.icons["Trigger"])
			if self.card.deathrattles:
				icons.append(self.icons["Deathrattle"])
			for keyWord in ("Lifesteal", "Poisonous"):
				if self.card.keyWords[keyWord] > 0:
					icons.append(self.icons[keyWord])
			leftMostPos = -0.6 * (len(icons) - 1) / 2
			for i, model in enumerate(icons):
				model.np.setColor(white)
				model.np.setPos(leftMostPos + i * 0.6, -0.1, -1.8)
	
	def decideColor(self):
		if self.isPlayed: return transparent
		color, card = transparent, self.card
		cardType, GUI, game = card.type, self.GUI, card.Game
		if card == GUI.subject: color = pink
		elif card == GUI.target: color = blue
		else:
			if card.inHand and card.ID == game.turn and game.Manas.affordable(card):
				color = yellow if card.effectViable else green
		return color
		
		
def loadWeapon(base):
	loader = base.loader
	sansBold = base.font
	root = loader.loadModel("Models\\WeaponModels\\Weapon.glb")
	root.name = "NP_Weapon"
	
	#Model names: border, box_Legendary, box_Normal, card, cardBack, cardImage, description,
	# legendaryIcon, nameTag, stats, stats_Played
	for model in root.getChildren():
		model.setTransparency(True)
		if model.name == "cardBack": texture = base.textures["cardBack"]
		elif model.name in ("border", "legendaryIcon", "stats", "stats_Played"): texture = base.textures["stats_Weapon"]
		else: continue
		model.setTexture(model.findTextureStage('*'), texture, 1)
		
	makeText(root, "mana", '0', pos=(-1.75, -0.11, 1.23), scale=statTextScale,
			  color=white, font=sansBold)
	makeText(root, "attack", '0', pos=(-1.7, -0.12, -4), scale=statTextScale,
			  color=white, font=sansBold)
	makeText(root, "durability", '0', pos=(1.8, -0.12, -4), scale=statTextScale,
			  color=white, font=sansBold)
	makeText(root, "attack_Played", '0', pos=(-1.28, -0.132, -0.8), scale=0.9,
			  color=white, font=sansBold)
	makeText(root, "durability_Played", '0', pos=(1.27, -0.132, -0.8), scale=0.9,
				  color=white, font=sansBold)
	
	base.modelTemplates["Trigger"].copyTo(root)
	base.modelTemplates["Deathrattle"].copyTo(root)
	base.modelTemplates["Lifesteal"].copyTo(root)
	base.modelTemplates["Poisonous"].copyTo(root)
	
	for name, posScale in table_PosScaleofTexCard_Weapons.items():
		texCard = loader.loadModel("TexCards\\ForWeapons\\%s.egg" % name)
		texCard.name = name + "_TexCard"
		texCard.reparentTo(root)
		texCard.setScale(posScale[0])
		texCard.setPos(posScale[1])
		texCard.find("+SequenceNode").node().pose(0)#loop(False, 1, 100)
	
	#After the loading, the NP_Weapon root tree structure is:
	#NP_Weapon/card|stats|cardImage, etc
	#NP_Weapon/mana_TextNode|attack_TextNode, etc
	#NP_Weapon/Trigger_Icon|Deathrattle_Icon, etc
	return root


"""Load Hero Powers"""
class Btn_Power(Btn_Card):
	def __init__(self, GUI, card, nodePath):
		super().__init__(GUI, card, nodePath)
		
		self.cNode_Backup = CollisionNode("Power_cNode")
		self.cNode_Backup.addSolid(CollisionBox(Point3(0, 0, -1.6), 2.3, 0.1, 3))
		self.cNode_Backup_Played = CollisionNode("Power_cNode_Played")
		self.cNode_Backup_Played.addSolid(CollisionBox(Point3(0, 0, 0.3), 1.6, 0.1, 1.6))
		
	def reloadModels(self, loader, imgPath, pickable):
		card = self.card
		self.models["box"].setColor(transparent)
		for modelName in ("card", "description", "nameTag"):
			self.models[modelName].setColor(transparent if self.isPlayed else white)
		if pickable and not self.cNode:
			self.cNode = self.np.attachNewNode(self.cNode_Backup)
			self.cNode.show()
		elif not pickable and self.cNode:
			self.cNode.removeNode()
			self.cNode = None
		
		"""The card frame. The front face texture is set according to it class"""
		texture = loader.loadTexture(imgPath)
		for modelName in ("card", "cardImage", "nameTag"):
			self.models[modelName].setTexture(self.models[modelName].findTextureStage('*'), texture, 1)
		text = card.text(CHN)
		textNodePath = self.texts["description"]
		textNodePath.node().setText(text)
		textNodePath.setPos(0, -0.2, -3 + 0.1 * len(text) / 12)
		textNodePath.node().setTextColor(black if not self.isPlayed and text else transparent)
		self.models["description"].setColor(white if not self.isPlayed and text else transparent)
		
		self.refresh()
		
	def leftClick(self):
		if self.isPlayed:
			if self.GUI.UI == 0:
				self.GUI.resolveMove(self.card, self, "Power", info=None)
		else:
			if self.GUI.UI == 3 and self.card in self.GUI.Game.options:
				self.GUI.resolveMove(self.card, None, "DiscoverOption", info=None)
		
	def refresh(self, color=False, stat=False, indicator=False, all=True):
		if color or all: self.setBoxColor(self.decideColor())
		if stat or all:
			cardType = type(self.card)
			#Refresh the mana
			color = white if self.card.mana == cardType.mana else (green if self.card.mana < cardType.mana else red)
			self.texts["mana"].node().setText(str(self.card.mana))
			self.texts["mana"].node().setTextColor(color)
		
		#if not self.card.chancesUsedUp() and self.card.Game.turn == self.card.ID:
		#	self.GUI.animate(self.genLerpInterval(hpr=Point3(0, 0, 0)), name="Power reset", afterAllFinished=False)
	
	def decideColor(self):
		if not self.isPlayed: return transparent
		color, card = transparent, self.card
		if card.ID == card.Game.turn and card.Game.Manas.affordable(card) and card.available():
			color = green
		return color
		
		
def loadPower(base):
	loader = base.loader
	sansBold = base.font
	root = loader.loadModel("Models\\PowerModels\\Power.glb")
	root.name = "NP_Power"
	
	#Model names: box, card, cardImage, description, nameTag, mana
	for model in root.getChildren():
		model.setTransparency(True)
		if model.name in ("border", "mana"): texture = base.textures["stats_Power"]
		else: continue
		model.setTexture(model.findTextureStage('*'), texture, 1)
	#y limit: mana -0.12, description -0.025
	makeText(root, "mana", '0', pos=(0, -0.125, 1.36), scale=0.9,
			color=white, font=sansBold)
	makeText(root, "description", '', pos=(0, -0.027, 0), scale=0.3,
			color=black, font=sansBold)
	#After the loading, the NP_Minion root tree structure is:
	#NP_Power/card|mana|cardImage, etc
	#NP_Power/mana_TextNode|description_TextNode
	return root


"""Load Hero Cards"""
table_PosScaleofTexCard_Heroes = {"Breaking": (4.3, (0, -0.062, 0.27)),
									"Frozen": (8, (-0.1, -0.064, 0.2)),
									"Immune": (5.3, (0, -0.071, 0.25)),
									"Damage": (0.055, (0, -0.14, 0.1)),
									"Spell Damage": (4.6, (0, -0.07, 0.15)),
									"Stealth": (5.5, (0, -0.064, 0.15)),
								   }

class Btn_Hero(Btn_Card):
	def __init__(self, GUI, card, nodePath):
		super().__init__(GUI, card, nodePath)
		
		self.cNode_Backup = CollisionNode("Hero_cNode")
		self.cNode_Backup.addSolid(CollisionBox(Point3(0.05, 0, -1.1), 2.2, 0.1, 3.1))
		self.cNode_Backup_Played = CollisionNode("Hero_cNode_Played")
		self.cNode_Backup_Played.addSolid(CollisionBox(Point3(0.05, 0, 0.25), 2, 0.1, 2.2))
		
	def reloadModels(self, loader, imgPath, pickable):
		card = self.card
		if self.isPlayed: color4Card, color4Played = transparent, white
		else: color4Card, color4Played = white, transparent
		self.models["box"].setColor(transparent)
		self.models["box_Played"].setColor(transparent)
		self.box_Model = self.models["box_Played" if self.isPlayed else "box"]
		for modelName in ("frame", "cardImage"): #the attack, health and armor will be handle by refresh
			self.models[modelName].setColor(color4Played)
		for modelName in ("card", "cardBack", "stats", "box"):
			self.models[modelName].setColor(color4Card)
		
		if pickable and not self.cNode:
			self.cNode = self.np.attachNewNode(self.cNode_Backup)
			self.cNode.show()
		elif not pickable and self.cNode:
			self.cNode.removeNode()
			self.cNode = None
		
		self.models["cardImage"].setTexture(self.models["cardImage"].findTextureStage('*'),
											loader.loadTexture("Images\\HeroesandPowers\\%s.png"%type(self.card).__name__), 1)
		self.models["card"].setTexture(self.models["card"].findTextureStage('*'),
									   loader.loadTexture(imgPath), 1)
		
		self.refresh()
		
	def leftClick(self):
		self.selected = not self.selected
		GUI, card = self.GUI, self.card
		UI, game = GUI.UI, GUI.Game
		if self.isPlayed:
			if UI == 0 or UI == 2:
				self.GUI.resolveMove(self.card, self, "HeroonBoard")
		else:
			if UI == -2:
				self.setBoxColor(red if self.selected else green)
				GUI.mulliganStatus[card.ID][game.mulligans[card.ID].index(card)] = 1 if self.selected else 0
			elif UI == -1 or UI == 1: pass #Lock out any selection
			elif GUI.UI == 3:
				if card in game.options:
					GUI.resolveMove(card, None, "DiscoverOption", info=None)
			else: GUI.resolveMove(card, self, "HeroinHand")
		
	def refresh(self, color=False, stat=False, indicator=False, all=True):
		#Change the box color to indicate the selectability of a card
		if color or all: self.setBoxColor(self.decideColor())
		
		card = self.card
		cardType = type(card)
		"""Reset the stats of the card"""
		if stat or all:
			#Refresh the mana
			color = white if card.mana == cardType.mana else (green if card.mana < cardType.mana else red)
			self.texts["mana"].node().setText(str(card.mana))
			self.texts["mana"].node().setTextColor(transparent if self.isPlayed else color)
			#Refresh the armor the hero card has
			self.texts["armor"].node().setText(str(card.armor))
			self.texts["armor"].node().setTextColor(transparent if self.isPlayed else white)
			#Refresh the attack
			self.models["attack"].setColor(white if self.isPlayed and card.attack > 0 else transparent)
			self.texts["attack_Played"].node().setText(str(card.attack))
			self.texts["attack_Played"].node().setTextColor(green if card.attack > 0 and self.isPlayed else transparent)
			#Refresh the health
			self.models["health"].setColor(white if self.isPlayed else transparent)
			self.texts["health_Played"].node().setText(str(card.health))
			self.texts["health_Played"].node().setTextColor(red if card.health < card.health_max else green if self.isPlayed else transparent)
			#Refresh the armor
			self.models["armor"].setColor(white if self.isPlayed and card.armor else transparent)
			self.texts["armor_Played"].node().setText(str(card.armor))
			self.texts["armor_Played"].node().setTextColor(white if card.armor > 0 and self.isPlayed else transparent)
			
	def decideColor(self):
		color, card = transparent, self.card
		if card == self.GUI.subject: color = pink
		elif card == self.GUI.target: color = blue
		else:
			if card.evanescent: color = blue
			if card.ID == card.Game.turn and card.Game.Manas.affordable(card):
				color = green
		return color
	
	def manageStatusTexCards(self):
		color = (0.6, 0.6, 0.6, 0.7) if self.card.status["Temp Stealth"] > 0 else transparent
		self.models["Stealth"].setColor(color)
		color = (1, 1, 1, 0.5) if self.card.status["Frozen"] > 0 else transparent
		self.models["Frozen"].setColor(color)
		color = (1, 1, 1, 0.5) if self.card.Game.status[self.card.ID]["Immune"] > 0 else transparent
		self.models["Immune"].setColor(color)
	
	def decideColor(self):
		color, card = transparent, self.card
		if card == self.GUI.subject: color = pink
		elif card == self.GUI.target: color = blue
		elif card.canAttack(): color = green
		return color
		
		
def loadHero(base):
	loader = base.loader
	sansBold = base.font
	root = loader.loadModel("Models\\HeroModels\\Hero.glb")
	root.name = "NP_Hero"
	
	#Model names: armor, attack, box, box_Played, card, cardBack, cardImage, frame, health, stats
	for model in root.getChildren():
		model.setTransparency(True)
		if model.name == "cardBack": texture = base.textures["cardBack"]
		elif model.name in ("stats", "armor", "attack", "frame", "health"):
			texture = base.textures["stats_Hero"]
		else: continue
		model.setTexture(model.findTextureStage('*'), texture, 1)
		
	makeText(root, "mana", '0', pos=(-1.73, -0.09, 1.15), scale=statTextScale,
			  color=white, font=sansBold)
	makeText(root, "armor", '0', pos=(1.81, -0.09, -4.02), scale=statTextScale,
			  color=white, font=sansBold)
	makeText(root, "attack_Played", '0', pos=(-2.15*0.88, -0.122, -2.38*0.88), scale=1.1,
			  color=white, font=sansBold)
	makeText(root, "health_Played", '0', pos=(2.2*0.88, -0.122, -2.38*0.88), scale=1.1,
			  color=white, font=sansBold)
	makeText(root, "armor_Played", '0', pos=(2.2*0.88, -0.122, -0.8*0.88), scale=1.1,
				  color=white, font=sansBold)
	
	for name, posScale in table_PosScaleofTexCard_Heroes.items():
		texCard = loader.loadModel("TexCards\\ForHeroes\\%s.egg" % name)
		texCard.name = name + "_TexCard"
		texCard.reparentTo(root)
		texCard.setScale(posScale[0])
		texCard.setPos(posScale[1])
		texCard.find("+SequenceNode").node().pose(0)
	
	#After the loading, the NP_Minion root tree structure is:
	#NP_Hero/card|stats|cardImage, etc
	#NP_Hero/mana_TextNode|attack_TextNode, etc
	#NP_Hero/Frozen_TexCard, etc
	return root


class Btn_Dormant(Btn_Card):
	def __init__(self, GUI, card, nodePath):
		super().__init__(GUI, card, nodePath)
		
		self.cNode_Backup_Played = CollisionNode("Minion_cNode_Played")
		self.cNode_Backup_Played.addSolid(CollisionBox(Point3(0.07, 0, 0.35), 1.5, 0.1, 1.9))
		
	def reloadModels(self, loader, imgPath, pickable):
		isLegendary = "~Legendary" in self.card.minionInside.index if self.card.minionInside else True
		self.models["legendaryIcon"].setColor(white if isLegendary else transparent)
		for modelName in ("card", "mana"):
			self.models[modelName].setColor(transparent if self.isPlayed else white)
		cardTexture = loader.loadTexture(imgPath)
		for modelName in ("card", "cardImage", "nameTag"):
			self.models[modelName].setTexture(self.models[modelName].findTextureStage('*'),
											cardTexture, 1)
		
	def leftClick(self):
		pass
		
	def refresh(self, color=False, stat=False, indicator=False, all=True):
		pass
		
	#Place the "Trigger", "Deathrattle", "Lifesteal", "Poisonous" icons at the right places
	def placeIcons(self):
		icon = self.icons["Trigger"]
		icon.np.setColor(transparent)
		if self.isPlayed and self.card.trigsBoard:
			icon.updateText()
			icon.np.setColor(white)
			icon.np.setPos(0, -0.1, -1.9)
		
	def manageStatusTexCards(self):
		pass
	
	def decideColor(self):
		return transparent
		

def loadDormant(base):
	loader = base.loader
	root = loader.loadModel("Models\\MinionModels\\Dormant.glb")
	root.name = "NP_Dormant"
	#Model names: card, cardImage, legendaryIcon, mana, nameTag, Trigger
	for model in root.getChildren():
		model.setTransparency(True)
		if model.name in ("mana", "legendaryIcon"): texture = base.textures["stats_Minion"]
		else: continue
		model.setTexture(model.findTextureStage('*'), texture, 1)
	
	base.modelTemplates["Trigger"].copyTo(root)
	#After the loading, the NP_Minion root tree structure is:
	#NP_Dromant/card|mana|cardImage, etc
	#NP_Dormant/Trigger_Icon
	return root


class Btn_Trigger:
	def __init__(self, carrierBtn, nodePath):
		self.carrierBtn, self.np = carrierBtn, nodePath
		self.counterText = nodePath.find("Trig Counter")
		self.seqNode = nodePath.find("TexCard").find("+SequenceNode").node()
		
	def trigAni(self, nextAnimWaits=False):
		self.updateText()
		if self.seqNode.isPlaying():
			self.seqNode.play(self.seqNode.getFrame(), self.seqNode.getNumFrames())
		else:
			self.seqNode.play(1, self.seqNode.getNumFrames())
		
	def updateText(self):
		s = ""
		for trig in self.carrierBtn.card.trigsBoard:
			if trig.counter > -1: s += str(trig.counter) + ' '
		self.counterText.node().setText(s)

class Btn_Deathrattle:
	def __init__(self, carrierBtn, nodePath):
		self.carrierBtn, self.np = carrierBtn, nodePath
		self.seqNode = nodePath.find("TexCard").find("+SequenceNode").node()
		
	def trigAni(self, nextAnimWaits=False):
		if self.seqNode.isPlaying():
			self.seqNode.play(self.seqNode.getFrame(), self.seqNode.getNumFrames())
		else:
			self.seqNode.play(1, self.seqNode.getNumFrames())

class Btn_Lifesteal:
	def __init__(self, carrierBtn, nodePath):
		self.carrierBtn, self.np = carrierBtn, nodePath
		self.seqNode = nodePath.find("TexCard").find("+SequenceNode").node()
	
	def trigAni(self, nextAnimWaits=False):
		if self.seqNode.isPlaying():
			self.seqNode.play(self.seqNode.getFrame(), self.seqNode.getNumFrames())
		else:
			self.seqNode.play(1, self.seqNode.getNumFrames())

class Btn_Poisonous:
	def __init__(self, carrierBtn, nodePath):
		self.carrierBtn, self.np = carrierBtn, nodePath
		self.seqNode = nodePath.find("TexCard").find("+SequenceNode").node()
		
	def trigAni(self, nextAnimWaits=False):
		if self.seqNode.isPlaying():
			self.seqNode.play(self.seqNode.getFrame(), self.seqNode.getNumFrames())
		else:
			self.seqNode.play(1, self.seqNode.getNumFrames())


#Used for secrets and quests
class Btn_Secret:
	def __init__(self, GUI, card, nodePath):
		self.GUI, self.card = GUI, card
		self.selected = False
		self.np = nodePath
	
	def dimDown(self):
		self.np.setColor(grey)
	
	def setBoxColor(self, color):
		pass
	
	def refresh(self, color=False, stat=False, indicator=False, all=True):
		hpr = None
		if self.card.ID == self.GUI.Game.turn and self.get_h() % 360 == 0:
			hpr = Point3(180, 0, 0)  #Flip to back, unusable
		elif self.card.ID != self.GUI.Game.turn and self.get_h() % 360 == 180:
			hpr = Point3(0, 0, 0)
		if hpr: LerpHprInterval(self, duration=0.3, hpr=hpr).start()
	
	def leftClick(self):
		pass
	
	def rightClick(self):
		if self.GUI.UI in (1, 2): self.GUI.cancelSelection()
		else: self.GUI.drawCardSpecsDisplay(self)


class Btn_TurnTrig:
	def __init__(self, GUI, card, nodePath):
		self.GUI, self.card = GUI, card
		self.selected = False
		self.np = nodePath
	
	def dimDown(self):
		self.np.setColor(grey)
	
	def leftClick(self):
		pass
	
	def rightClick(self):
		if self.GUI.UI in (1, 2): self.GUI.cancelSelection()
		else: self.GUI.drawCardSpecsDisplay(self)
	
	def refresh(self, color=False, stat=False, indicator=False, all=True):
		pass
	
	def setBoxColor(self, color):
		pass


class ChooseOptionModel(NodePath):
	def __init__(self, GUI, card, isPlayed):
		NodePath.__init__(self, type(card).__name__ + "_Option")
		#These attributes will be modified by load functions below
		self.card = card
		self.selected = False
		self.GUI = GUI
		self.card_Model = None
		
		self.cNode_Backup = CollisionNode("Option_cNode")
		self.cNode_Backup.addSolid(CollisionBox(Point3(0, 0, 0), 3.5, 0.3, 5))
		self.cNode = self.attachNewNode(self.cNode_Backup)
	
	def changeCard(self, card, pickable=True):
		loader = self.GUI.loader
		self.card = card
		card.btn = self
		self.name = type(card).__name__ + "_Option_" + str(datetime.now().time())
		texture = loader.loadTexture(findFilepath(card))
		self.card_Model.setTexture(self.card_Model.findTextureStage('*'),
								   texture, 1)
		
	def leftClick(self):
		self.GUI.resolveMove(self.card, self, "ChooseOneOption" if self.GUI.UI == 1 else "DiscoverOption")
		
	def rightClick(self):
		pass
	
	
def loadOption_Spell(base, card, isPlayed=False):
	loader = base.loader
	texture = loader.loadTexture(findFilepath(card))
	root = ChooseOptionModel(base, card, isPlayed=False)
	#root.reparentTo(base.render)
	root.card_Model = loader.loadModel("Models\\Option_Spell.glb")
	root.card_Model.reparentTo(root)
	root.card_Model.setTexture(root.card_Model.findTextureStage('*'), texture, 1)

	return root


def loadOption_Minion(base, card, isPlayed=False):
	loader = base.loader
	texture = loader.loadTexture(findFilepath(card))
	
	root = ChooseOptionModel(base, card, isPlayed=False)
	#root.reparentTo(base.render)
	root.card_Model = loader.loadModel("Models\\Option_Minion.glb")
	root.card_Model.reparentTo(root)
	root.card_Model.setTexture(root.card_Model.findTextureStage('*'), texture, 1)
	
	return root


Table_Type2Btn = {"Minion": Btn_Minion, "Spell": Btn_Spell, "Weapon": Btn_Weapon,
				  "Hero": Btn_Hero, "Power": Btn_Power, "Dormant": Btn_Dormant,
				  "Trigger_Icon": Btn_Trigger, "Deathrattle_Icon": Btn_Deathrattle,
				  "Lifesteal_Icon": Btn_Lifesteal, "Poisonous_Icon": Btn_Poisonous}


#np_Template is of type NP_Minion, etc and is kept by the GUI.
#card: card object, which the copied nodePath needs to become
#isPlayed: boolean, whether the card is in played form or not
def genCard(GUI, card, isPlayed, pickable=True, pos=None, hpr=None, scale=None):
	np = GUI.modelTemplates[card.type].copyTo(GUI.render)
	if pos: np.setPos(pos)
	if hpr: np.setHpr(hpr)
	if scale: np.setScale(scale)
	#NP_Minion root tree structure is:
	#NP_Minion/card|stats|cardImage, etc
	#NP_Minion/mana_TextNode|attack_TextNode, etc
	btn_Card = Table_Type2Btn[card.type](GUI, card, np)
	np.setPythonTag("btn", btn_Card)
	for nodePath in np.getChildren():
		name = nodePath.name
		if "TextNode" in name: btn_Card.texts[name.replace("_TextNode", '')] = nodePath
		elif "TexCard" in name: btn_Card.texCards[name.replace("_TexCard", '')] = nodePath
		#Collision Nodes are not inserted into the template tree yet
		elif "_Icon" in name:
			btn_Card.icons[name.replace("_Icon", '')] = Table_Type2Btn[name](btn_Card, nodePath)
		else: btn_Card.models[name] = nodePath
	
	btn_Card.changeCard(card, isPlayed=isPlayed, pickable=pickable)
	return np, btn_Card


def genSecretIcon(GUI, card, pos=None, hpr=None):
	np = GUI.loader.loadModel("Models\\HeroModels\\SecretIcon.glb")
	np.setTexture(np.findTextureStage('0'), GUI.textures["Secret_"+card.Class], 1)
	np.reparentTo(GUI.render)
	if pos: np.setPos(pos)
	if hpr: np.setHpr(hpr)
	btn_Icon = Btn_Secret(GUI, card, np)
	np.setPythonTag("btn", btn_Icon)
	cNode = CollisionNode("Secret_cNode")
	cNode.addSolid(CollisionSphere(0, 0, 0, 0.5))
	np.attachNewNode(cNode)#.show()
	return np, btn_Icon


def genTurnTrigIcon(GUI, card, pos=None):
	np = GUI.loader.loadModel("Models\\HeroModels\\TurnTrig.glb")
	icon = np.find("Icon")
	icon.setTexture(icon.findTextureStage('0'),
					GUI.loader.loadTexture(findFilepath(card)), 1)
	np.reparentTo(GUI.render)
	if pos: np.setPos(pos)
	btn_Icon = Btn_TurnTrig(GUI, card, np)
	np.setPythonTag("btn", btn_Icon)
	cNode = CollisionNode("TurnTrig_cNode")
	cNode.addSolid(CollisionSphere(0, 0, 0, 0.6))
	np.attachNewNode(cNode)#.show()
	return np, btn_Icon