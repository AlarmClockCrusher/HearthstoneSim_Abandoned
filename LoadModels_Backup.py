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
	elif card.type in ("Minion", "Weapon", "Spell"):  #type == "Weapon", "Minion", "Spell", "Hero", "Power"
		return "Images\\%s\\%s.png"%(card.index.split('~')[0], type(card).__name__)
	elif card.type in ("Power", "Hero"):
		return "Images\\HeroesandPowers\\%s.png"%type(card).__name__
	
	
red, green, blue = Point4(1, 0, 0, 1), Point4(0.3, 1, 0.2, 1), Point4(0, 0, 1, 1)
yellow, pink = Point4(1, 1, 0, 1), Point4(1, 0, 1, 1)

transparent, grey = Point4(1, 1, 1, 0), Point4(0.5, 0.5, 0.5, 1)
black, white = Point4(0, 0, 0, 1), Point4(1, 1, 1, 1)


"""Subclass the NodePath, since it can be assigned attributes directly"""
class NP_Card(NodePath):
	def __init__(self, GUI, card, isPlayed):
		super().__init__("NP_%s"%card.type)
		self.GUI, self.card = GUI, card
		self.selected, self.isPlayed  = False, isPlayed
		self.cNode = self.cNode_Backup = self.cNode_Backup_Played = None  #cNode holds the return value of attachNewNode
		
		self.models, self.texts, self.texCards = {}, {}, {}
		self.box_Model = None
		
	def changeCard(self, card, isPlayed, pickable=True):
		retexture = type(card) != type(self.card)
		self.card, self.isPlayed = card, isPlayed
		loader = self.GUI.loader
		if pickable: card.btn = self
		self.name = "NP_%s_"%card.type + type(card).__name__
		threading.Thread(target=self.reloadModels, args=(loader, findFilepath(card), pickable, retexture)).start()
	
	def makeText(self, textName, valueText, pos, scale, color, font, wordWrap=0):
		textNode = TextNode(textName + "_TextNode")
		textNode.setText(valueText)
		textNode.setAlign(TextNode.ACenter)
		textNode.setFont(font)
		textNode.setTextColor(color)
		if wordWrap > 0:
			textNode.setWordwrap(wordWrap)
		textNode_Att = self.attachNewNode(textNode)
		textNode_Att.setScale(scale)
		textNode_Att.setPos(pos)
		self.texts[textName] = textNode_Att
	
	def dimDown(self):
		self.setColor(grey)
		
	def setBoxColor(self, color):
		if self.box_Model: self.box_Model.setColor(color)
	
	def showStatus(self):
		pass
	
	def rightClick(self):
		if self.GUI.UI in (1, 2): self.GUI.cancelSelection()
		else: self.GUI.drawCardSpecsDisplay(self)
	
	#Control the moving, rotating and scaling of a nodePath. For color manipulate, another method is used.
	def genLerpInterval(self, pos=None, hpr=None, scale=None, duration=0.3, blendType="noBlend"):
		pos = pos if pos else self.getPos()
		hpr = hpr if hpr else self.getHpr()
		scale = scale if scale else self.getScale()
		if self.card: #Let the card remember where it is set to be.
			self.card.x, self.card.y, self.card.z = pos
		interval = LerpPosHprScaleInterval(self, duration=duration, pos=pos, hpr=hpr, scale=scale, blendType=blendType)
		return interval
	
	def genMoPathIntervals(self, curveFileName):
		moPath = Mopath.Mopath()
		moPath.loadFile(curveFileName)
		return MopathInterval(moPath, self)
	
	#For the selfCopy method, this will simply return a None
	def selfCopy(self, Copy):
		return None
	
def loadCard(base, card, isPlayed=False):
	return {"Minion": loadMinion, "Spell": loadSpell, "Weapon": loadWeapon, "Hero": loadHero,
			"Power": loadPower, "Dormant": loadDormant,
			"Option_Spell": loadOption_Spell, "Option_Minion": loadOption_Minion
			}[card.type](base, card, isPlayed)
	
	
class NP_Minion(NP_Card):
	def __init__(self, GUI, card, isPlayed):
		super().__init__(GUI, card, isPlayed)
		
		self.cNode_Backup = CollisionNode("Minion_cNode_Card")
		self.cNode_Backup.addSolid(CollisionBox(Point3(0.05, 0, -1.1), 2.2, 0.1, 3.1))
		self.cNode_Backup_Played = CollisionNode("Minion_cNode_Played")
		self.cNode_Backup_Played.addSolid(CollisionBox(Point3(0.07, 0, 0.35), 1.5, 0.1, 1.9))
		#self.cNode = self.attachNewNode(self.cNode_Backup)
		
	def reloadModels(self, loader, imgPath, pickable, reTexture):
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
			self.cNode = self.attachNewNode(self.cNode_Backup_Played if self.isPlayed else self.cNode_Backup)
		elif not pickable and self.cNode:
			self.cNode.removeNode()
			self.cNode = None
		
		if reTexture:
			cardTexture = loader.loadTexture(imgPath)
			for modelName in ("card", "cardImage", "nameTag", "race"):
				self.models[modelName].setTexture(self.models[modelName].findTextureStage('*'), cardTexture, 1)
			#Change the card textNodes no matter what (non-mutable texts are empty anyways)
			text = card.text(CHN)
			self.texts["description"].node().setText(text)
			self.texts["description"].setPos(0, -0.2, -3 + 0.1 * len(text) / 12)
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
		for modelName in ("Trigger", "Lifesteal", "Poisonous", "Dealthrattle"):
			if modelName in self.models:
				self.models[modelName].seqNode.pose(0)
				self.models[modelName].setColor(transparent)
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
		
	#Only invoked when the minion shows its trigs and keyWords/status for the first time. (Later changes are handled by various methods)
	def manageIconModels(self):
		for iconName, loadFunc in zip(("Trigger", "Deathrattle", "Lifesteal", "Poisonous"),
								  (loadTrigger, loadDeathrattle, loadLifesteal, loadPoisonous)):
			if iconName not in self.models:
				node_Icon = loadFunc(self, self.GUI)
				node_Icon.reparentTo(self)
				self.models[iconName] = node_Icon
			self.models[iconName].setColor(transparent)
		if self.isPlayed:
			#Place the icons, depending on the number of trigs to show
			models = []
			if self.card.trigsBoard:
				self.models["Trigger"].updateText()
				models.append(self.models["Trigger"])
			if self.card.deathrattles:
				models.append(self.models["Deathrattle"])
			for keyWord in ("Lifesteal", "Poisonous"):
				if self.card.keyWords[keyWord] > 0:
					models.append(self.models[keyWord])
			leftMostPos = -0.6 * (len(models) - 1) / 2
			for i, model in enumerate(models):
				model.setColor(white)
				model.setPos(leftMostPos + i * 0.6, 0, -1.95)
	
	def loadStatusTexCards(self): #cardImage y limit -0.06; nameTag -0.07; stats_Played -0.12
		loader = self.GUI.loader
		table_PosScaleofTexCard = {"Aura": (0.025, (0, -0.035, 0.3)),
									"Damage": (0.022, (0, -0.14, 0.5)),
									"DamagePoisonous": (0.022, (0, -0.142, 0.5)),
									"Divine Shield": (7.3, (0.1, -0.078, 0.2)),
									"Exhausted": (5, (0.1, -0.062, 0.5)),
									"Frozen": (5.2, (0, -0.08, 0.55)),
									"Immune": (4.5, (0.05, -0.076, 0.5)),
									"Silenced": (4, (0, -0.068, 0)),
									"Spell Damage": (4, (0, -0.07, 1)),
									"Stealth": (4.2, (0.1, -0.064, 0.5)),
									"Taunt": (0.01, (0.15, 0, 0.3)),
								   }
		for name, posScale in table_PosScaleofTexCard.items():
			texCard = loader.loadModel("TexCards\\ForMinions\\%s.egg"%name)
			texCard.name = name+"_TexCard"
			texCard.reparentTo(self)
			texCard.setScale(posScale[0])
			texCard.setPos(posScale[1])
			texCard.find("**/+SequenceNode").node().pose(0)
			
	def manageStatusTexCards(self):
		minion = self.card
		if minion.auras: self.texCards["Aura"].find("**/+SequenceNode").node().loop(False)
		if minion.keyWords["Divine Shield"] > 0: self.texCards["Divine Shield"].find("**/+SequenceNode").node().play(1, 20)
		if minion.canAttack(): self.texCards["Exhausted"].find("**/+SequenceNode").node().loop(False, 1, 24)
		if minion.status["Frozen"] > 0: self.texCards["Frozen"].find("**/+SequenceNode").node().loop(False, 1, 96)
		if minion.status["Immune"] > 0: self.texCards["Immune"].find("**/+SequenceNode").node().loop(False, 1, 100)
		if minion.silenced: self.texCards["Silenced"].find("**/+SequenceNode").node().loop(True, 1, 71)
		if minion.keyWords["Spell Damage"] + minion.keyWords["Nature Spell Damage"] > 0:
			seqNode = self.texCards["Spell Damage"].find("**/+SequenceNode").node()
			Sequence(Func(seqNode.play, 1, 13), Func(seqNode.loop, True, 1, 71)).start()
		if minion.keyWords["Stealth"] + minion.status["Temp Stealth"] > 0:
			self.texCards["Stealth"].find("**/+SequenceNode").node().loop(False, 1, 119)
		if minion.keyWords["Taunt"]: self.texCards["Taunt"].find("**/+SequenceNode").node().play(1, 13)
		
statTextScale = 1.05
manaPos = Point3(-2.8, -0.15, 3.85)
healthPos = Point3(3.1, -0.2, -4.95)
attackPos = Point3(-2.85, -0.15, -4.95)

#loadMinion, etc will prepare all the textures and trigIcons to be ready.
def loadMinion(base, card, isPlayed=False):
	loader = base.loader
	sansBold = base.font
	cardTexture = loader.loadTexture(findFilepath(card))
	root = NP_Minion(base, card, isPlayed)
	#root.reparentTo(base.render)
	cardModel = loader.loadModel("Models\\MinionModels\\Minion.glb")
	cardModel.reparentTo(root)
	
	if isPlayed: color4Card, color4Played = transparent, white
	else: color4Card, color4Played = white, transparent
	isLegendary = "~Legendary" in card.index
	#Model names: box_Legendary, box_Legendary_Played, box_Normal, box_Normal_Played
	# card, cardBack, cardImage, description, legendaryIcon, nameTag, race, stats, stats_Played
	for model in cardModel.getChildren():
		name = model.name
		model.setTransparency(True)
		root.models[name] = model
		if name == "cardBack":
			texture, color = base.textures["cardBack"], color4Card
		elif name == "legendaryIcon":
			texture, color = base.textures["stats_Minion"], white if isLegendary else transparent
		elif name == "stats":
			texture, color = base.textures["stats_Minion"], color4Card
		elif name == "stats_Played":
			texture, color = base.textures["stats_Minion"], color4Played
		elif name == "nameTag" or name == "cardImage":
			texture, color = cardTexture, white
		elif name == "card" or name == "race":
			texture, color = cardTexture, color4Card
		else: #skip boxes and description retexturing (for now)
			model.setColor(transparent)
			continue
		model.setTexture(model.findTextureStage('*'), texture, 1)
		model.setColor(color)
	
	text = card.text(CHN)
	cardType, game = type(card), card.Game
	if isPlayed:
		color_mana = color_attack = color_health = transparent
		color_attack_Played = white if card.attack <= card.attack_0 else green
		color_health_Played = white if card.health == card.health_max else (green if card.health == card.health_max else red)
	else:
		color_mana = white if card.mana == cardType.mana else (green if card.mana < cardType.mana else red)
		color_attack = white if card.attack <= card.attack_0 else green
		color_health = white if card.health == card.health_max else (green if card.health == card.health_max else red)
		color_attack_Played = color_health_Played = transparent
	root.makeText("mana", str(card.mana), pos=(-1.8, -0.09, 1.15), scale=statTextScale,
				  color=color_mana, font=sansBold)
	root.makeText("attack", str(card.attack), pos=(-1.7, -0.09, -4.05), scale=statTextScale,
				  color=color_attack, font=sansBold)
	root.makeText("health", str(card.health), pos=(1.8, -0.09, -4.05), scale=statTextScale,
				  color=color_health, font=sansBold)
	root.makeText("attack_Played", str(card.attack), pos=(-1.2, -0.122, -0.74), scale=0.8,
				  color=color_attack_Played, font=sansBold)
	root.makeText("health_Played", str(card.health), pos=(1.32, -0.122, -0.74), scale=0.8,
				  color=color_health_Played, font=sansBold)
	root.makeText("description", valueText=text, pos=(0, -0.2, -3+0.1*len(text)/12), scale=0.3,
				  color=black if isPlayed else transparent, font=sansBold, wordWrap=12)
	
	#Handle the descriptions. The description model has been set transparent
	if text and isPlayed: #Only not played cards that do have mutable cardTexts need to show the description model
		model = root.models["description"]
		model.setTexture(model.findTextureStage('*'),
						base.textures["minion_%s" % card.index.split('~')[0]], 1)
		model.setColor(white)
	if isPlayed: root.box_Model = root.models["box_Legendary_Played" if isLegendary else "box_Normal_Played"]
	else: root.box_Model = root.models["box_Legendary" if isLegendary else "box_Normal"]
	
	return root

#np_Template is of type NP_Minion, etc and is kept by the GUI.
#card: card object, which the copied nodePath needs to become
#isPlayed: boolean, whether the card is in played form or not
def copyfromCard(GUI, np_Template, card, isPlayed, pickable=True, pos=None, hpr=None, printChildren=False):
	#The np_Orig has children: Scene(the models), textNodes
	#print("The children of the original nodepath")
	#for model in np_Orig.getChildren():
	#	print(model.name)
		
	#np = {"Minion": NP_Minion, "Spell": NP_Spell, "Weapon": NP_Weapon,
	#	  "Hero": NP_Hero, "Power": NP_Power, "Dormant": NP_Dormant}[np_Orig.cardNP_Minion(GUI, card, isPlayed)
	np = type(np_Template)(GUI, np_Template.card, isPlayed) #The collision nodes are always added each time a node path is created
	np.reparentTo(GUI.render)
	np_Template.copyTo(np) #After the copying, the position is also copied. Need to move it
	#The np nodePath now has a tree:
	# render/NP_Minion/NP_Minion/Scene||textnodes||texCardEgg
	if pos: np.setPos(pos)
	if hpr: np.setHpr(hpr)
	for nodePath in np.getChild(0).getChildren():
		name = nodePath.name
		if "TextNode" in name: np.texts[name.replace("_TextNode", '')] = nodePath
		elif "TexCard" in name: np.texCards[name.replace("_TexCard", '')] = nodePath
		#Collision Nodes are not inserted into the template tree yet
		elif name == "Scene": #The scene's children are the parts of the card model
			for nodePath_Model in nodePath.getChildren():
				np.models[nodePath_Model.name] = nodePath_Model
	
	#If don't load the triggers, takes 1ms to create.
	#cardType = card.type
	#if cardType in ("Minion", "Weapon", "Dormant"): #Prepare the trigger icon
	#	root_Icon = NP_Trigger(np)
	#	root_Icon.setTransparency(True)
	#	root_Icon.reparentTo(np)
	#	GUI.modelTemplates["Trigger"].copyTo(root_Icon)
	#	textNode = TextNode("Trig Counter")
	#	textNode.setAlign(TextNode.ACenter)
	#	root_Icon.counterText = root_Icon.attachNewNode(textNode)
	#	root_Icon.counterText.setPos(0, -0.2, -4.7)
	#	root_Icon.counterText.setScale(0.9)
	#	texCard = GUI.modelTemplates["Trigger_TexCard"].copyTo(root_Icon)
	#	root_Icon.seqNode = texCard.find('**/+SequenceNode').node()
	#	root_Icon.seqNode.pose(0)
	#	root_Icon.setColor(transparent)
	#	np.models["Trigger"] = root_Icon
	#if cardType == "Minion" or cardType == "Weapon": #Prepare the liftsteal, poisonous and deathrattle
	#	for NP_Icon, iconName in zip((NP_Deathrattle, NP_Lifesteal, NP_Poisonous), ("Deathrattle", "Lifesteal", "Poisonous")):
	#		root_Icon = NP_Icon(np)
	#		root_Icon.reparentTo(np)
	#		root_Icon.setTransparency(True)
	#		GUI.modelTemplates[iconName].copyTo(root_Icon)
	#		texCard = GUI.modelTemplates[iconName+"_TexCard"].copyTo(root_Icon)
	#		root_Icon.seqNode = texCard.find('**/+SequenceNode').node()
	#		root_Icon.seqNode.pose(0)
	#		root_Icon.setColor(transparent)
	#		np.models[iconName] = root_Icon
	#
	if printChildren:
		print("np's children")
		for nodePath in np.getChildren():
			print(nodePath)
			if "NP_" in nodePath.name:
				for nodePath_Sub in nodePath.getChildren():
					print("\t", nodePath_Sub)
					if nodePath_Sub.name == "Scene":
						for nodePath_Model in nodePath_Sub.getChildren():
							print("\t\t", nodePath_Model)
		
	np.changeCard(card, isPlayed=isPlayed, pickable=pickable)
	return np

"""Load Spell Cards"""
class NP_Spell(NP_Card):
	def __init__(self, GUI, card, isPlayed):
		super().__init__(GUI, card, isPlayed=False)
		self.name = type(card).__name__ + "_Spell"
		
		self.cNode_Backup = CollisionNode("Spell_cNode")
		self.cNode_Backup.addSolid(CollisionBox(Point3(0.05, 0, -1.1), 2.2, 0.1, 3.1))
		
	def reloadModels(self, loader, imgPath, pickable, reTexture):
		card = self.card
		isLegendary = "~Legendary" in card.index
		self.models["legendaryIcon"].setColor(white if isLegendary else transparent)
		self.models["box_Normal"].setColor(transparent)
		self.models["box_Legendary"].setColor(transparent)
		self.box_Model = self.models["box_Legendary" if isLegendary else "box_Normal"]
		
		if pickable and not self.cNode:
			self.cNode = self.attachNewNode(self.cNode_Backup)
		elif not pickable and self.cNode:
			self.cNode.removeNode()
			self.cNode = None
		
		if reTexture:
			texture = loader.loadTexture(imgPath)
			for modelName in ("card", "school"):
				self.models[modelName].setTexture(self.models[modelName].findTextureStage('*'), texture, 1)
		
			text = card.text(CHN)
			self.texts["description"].node().setText(text)
			self.texts["description"].setPos(0, -0.2, -3 + 0.1 * len(text) / 12)
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
		
		
def loadSpell(base, card, isPlayed=False):
	loader = base.loader
	sansBold = base.font
	cardTexture = loader.loadTexture(findFilepath(card))
	root = NP_Spell(base, card, isPlayed)
	#root.reparentTo(base.render)
	cardModel = loader.loadModel("Models\\SpellModels\\Spell.glb")
	cardModel.reparentTo(root)
	
	#Model names: box_Legendary, box_Normal, card, cardBack, description, legendaryIcon, mana, school
	for model in cardModel.getChildren():
		name = model.name
		model.setTransparency(True)
		root.models[name] = model
		if name in ("card", "school"): texture = cardTexture
		elif name in ("mana", "legendaryIcon"): texture = base.textures["stats_Spell"]
		elif name == "cardBack": texture = base.textures["cardBack"]
		else: #Skip the box and description model retexturing
			model.setColor(transparent)
			continue
		model.setTexture(model.findTextureStage('*'), texture, 1)
	
	cardType = type(card)
	color_mana = white if card.mana == cardType.mana else (green if card.mana < cardType.mana else red)
	root.makeText("mana", str(card.mana), pos=(-1.73, -0.09, 1.2), scale=statTextScale,
				  color=color_mana, font=sansBold, wordWrap=0)
	text = card.text(CHN)
	root.makeText("description", text, pos=(0, -0.09, -3 + 0.1 * len(text) / 12), scale=0.25,
				  color=black if text else transparent, font=sansBold, wordWrap=12)
	if text and isPlayed:
		model = root.models["description"]
		model.setTexture(model.findTextureStage('*'),
						base.textures["spell_%s"%card.index.split('~')[0]], 1)
		model.setColor(white)
	root.models["legendaryIcon"].setColor(white if "~Legendary" in card.index else transparent)
	root.box_Model = root.models["box_Legendary" if "~Legendary" in card.index else "box_Normal"]
	
	return root



"""Load Weapon Cards"""
class NP_Weapon(NP_Card):
	def __init__(self, GUI, card, isPlayed):
		super().__init__(GUI, card, isPlayed)
		self.name = type(card).__name__ + "_Weapon"
		
		self.cNode_Backup = CollisionNode("Weapon_cNode_Card")
		self.cNode_Backup.addSolid(CollisionBox(Point3(0.05, 0, -1.1), 2.2, 0.1, 3.1))
		self.cNode_Backup_Played = CollisionNode("Weapon_cNode_Played")
		self.cNode_Backup_Played.addSolid(CollisionBox(Point3(0.07, 0, 0.33), 1.8, 0.1, 1.8))
		
	def reloadModels(self, loader, imgPath, pickable, retexture):
		card = self.card
		if self.isPlayed: color4Card, color4Played = transparent, white
		else: color4Card, color4Played = white, transparent
		isLegendary = "~Legendary" in card.index
		self.models["legendaryIcon"].setColor(white if isLegendary else transparent)
		self.models["box_Normal"].setColor(transparent)
		self.models["box_Legendary"].setColor(transparent)
		self.box_Model = None if self.isPlayed else self.models["box_Legendary" if isLegendary else "box_Normal"]
		
		if pickable and not self.cNode:
			self.cNode = self.attachNewNode(self.cNode_Backup)
		elif not pickable and self.cNode:
			self.cNode.removeNode()
			self.cNode = None
		
		if retexture:
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
	
	
	def manageIconModels(self):
		for iconName, loadFunc in zip(("Trigger", "Deathrattle", "Lifesteal", "Poisonous"),
									  (loadTrigger, loadDeathrattle, loadLifesteal, loadPoisonous)):
			if iconName not in self.models:
				node_Icon = loadFunc(self, self.GUI)
				node_Icon.reparentTo(self)
				self.models[iconName] = node_Icon
			self.models[iconName].setColor(transparent)
		if self.isPlayed:
			#Place the icons, depending on the number of trigs to show
			models = []
			if self.card.trigsBoard:
				self.models["Trigger"].updateText()
				models.append(self.models["Trigger"])
			if self.card.deathrattles:
				models.append(self.models["Deathrattle"])
			for keyWord in ("Lifesteal", "Poisonous"):
				if self.card.keyWords[keyWord] > 0:
					models.append(self.models[keyWord])
			leftMostPos = -0.6 * (len(models) - 1) / 2
			for i, model in enumerate(models):
				model.setColor(white)
				model.setPos(leftMostPos + i * 0.6, 0, -1.8)
	
	def loadStatusTexCards(self): #cardImage y limit -0.09; nameTag -0.095; stats_Played -0.13
		loader = self.GUI.loader
		table_PosScaleofTexCard = {"Immune": (5.5, (0, -0.092, 0.5)),
								   }
		for name, posScale in table_PosScaleofTexCard.items():
			texCard = loader.loadModel("TexCards\\ForWeapons\\%s.egg" % name)
			texCard.name = name + "_TexCard"
			texCard.reparentTo(self)
			texCard.setScale(posScale[0])
			texCard.setPos(posScale[1])
			texCard.find("**/+SequenceNode").node().pose(0)
	
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
		
		
def loadWeapon(base, card, isPlayed=False):
	loader = base.loader
	sansBold = base.font
	cardTexture = loader.loadTexture(findFilepath(card))
	root = NP_Weapon(base, card, isPlayed)
	#root.reparentTo(base.render)
	cardModel = loader.loadModel("Models\\WeaponModels\\Weapon.glb")
	cardModel.reparentTo(root)
	
	if isPlayed: color4Card, color4Played = transparent, white
	else: color4Card, color4Played = white, transparent
	isLegendary = "~Legendary" in card.index
	#Model names: border, box_Legendary, box_Normal, card, cardBack, cardImage, description,
	# legendaryIcon, nameTag, stats, stats_Played, Deathrattle, Lifesteal, Poisonous, Trigger
	for model in cardModel.getChildren():
		name = model.name
		model.setTransparency(True)
		root.models[name] = model
		if name == "cardBack": texture, color = base.textures["cardBack"], color4Card
		elif name == "border": texture, color = base.textures["stats_Weapon"], white
		elif name == "card": texture, color = base.textures["weapon_%s"%card.Class], color4Card
		elif name == "cardImage" or name == "nameTag": texture, color = cardTexture, white
		elif name == "description": texture, color = cardTexture, color4Card
		elif name == "legendaryIcon": texture, color = base.textures["stats_Weapon"], white if isLegendary else transparent
		elif name == "stats":
			texture, color = base.textures["stats_Weapon"], color4Card
		elif name == "stats_Played":
			texture, color = base.textures["stats_Weapon"], color4Played
		else:
			model.setColor(transparent)
			continue
		model.setTexture(model.findTextureStage('*'), texture, 1)
		model.setColor(color)
	
	cardType = type(card)
	if isPlayed:
		color_mana = color_attack = color_durability = transparent
		color_attack_Played = white if card.attack <= cardType.attack else green
		color_durability_Played = green if card.durability >= cardType.durability else red
	else:
		color_mana = white if card.mana == cardType.mana else (green if card.mana < cardType.mana else red)
		color_attack = white if card.attack <= cardType.attack else green
		color_durability = green if card.durability >= cardType.durability else red
		color_attack_Played = color_durability_Played = transparent
	
	root.makeText("mana", str(card.mana), pos=(-1.75, -0.11, 1.23), scale=statTextScale,
				  color=color_mana, font=sansBold)
	root.makeText("attack", str(card.attack), pos=(-1.7, -0.12, -4), scale=statTextScale,
				  color=color_attack, font=sansBold)
	root.makeText("durability", str(card.durability), pos=(1.8, -0.12, -4), scale=statTextScale,
				  color=color_durability, font=sansBold)
	root.makeText("attack_Played", str(card.attack), pos=(-1.28, -0.132, -0.8), scale=0.9,
				  color=color_attack_Played, font=sansBold)
	root.makeText("durability_Played", str(card.durability), pos=(1.27, -0.132, -0.8), scale=0.9,
				  color=color_durability_Played, font=sansBold)
	
	return root


"""Load Hero Powers"""
class NP_Power(NP_Card):
	def __init__(self, GUI, card, isPlayed):
		super().__init__(GUI, card, isPlayed)
		self.name = type(card).__name__ + "_Power"
		self.isPlayed = False
		
		self.cNode_Backup = CollisionNode("Power_cNode")
		self.cNode_Backup.addSolid(CollisionBox(Point3(0, 0, -1.6), 2.3, 0.1, 3))
		self.cNode_Backup_Played = CollisionNode("Power_cNode_Played")
		self.cNode_Backup_Played.addSolid(CollisionBox(Point3(0, 0, 0.3), 1.6, 0.1, 1.6))
		
	def reloadModels(self, loader, imgPath, pickable, reTexture=True):
		card = self.card
		self.models["box"].setColor(transparent)
		for modelName in ("card", "description", "nameTag"):
			self.models[modelName].setColor(transparent if self.isPlayed else white)
		if pickable and not self.cNode:
			self.cNode = self.attachNewNode(self.cNode_Backup)
		elif not pickable and self.cNode:
			self.cNode.removeNode()
			self.cNode = None
		
		"""The card frame. The front face texture is set according to it class"""
		texture = loader.loadTexture(imgPath)
		if reTexture:
			for modelName in ("card", "cardImage", "nameTag"):
				self.models[modelName].setTexture(self.models[modelName].findTextureStage('*'), texture, 1)
			text = card.text(CHN)
			self.texts["description"].node().setText(text)
			self.texts["description"].setPos(0, -0.2, -3 + 0.1 * len(text) / 12)
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
		
		
def loadPower(base, card, isPlayed=False):
	loader = base.loader
	sansBold = base.font
	cardTexture = loader.loadTexture(findFilepath(card))
	root = NP_Power(base, card, isPlayed)
	#root.reparentTo(base.render)
	cardModel = loader.loadModel("Models\\PowerModels\\Power.glb")
	cardModel.reparentTo(root)
	
	if isPlayed: color4Card, color4Played = transparent, white
	else: color4Card, color4Played = white, transparent
	#model names: border, box, card, cardImage, description, mana, nameTag
	for model in cardModel.getChildren():
		name = model.name
		model.setTransparency(True)
		root.models[name] = model
		if name == "border" or name == "mana": texture, color = base.textures["stats_Power"], white
		elif name == "cardImage": texture, color = cardTexture, white
		elif name == "card" or name == "nameTag": texture, color = cardTexture, color4Card
		elif name == "description": texture, color = cardTexture, transparent
		else: #skip box and description retextureing
			model.setColor(transparent)
			continue
		model.setTexture(model.findTextureStage('*'), texture, 1)
		model.setColor(color)
	
	text = card.text(CHN)
	cardType = type(card)
	color_mana = white if card.mana == cardType.mana else (green if card.mana < cardType.mana else red)
	root.makeText("mana", str(card.mana), pos=(0, -0.1, 1.36), scale=0.9,
				  color=color_mana, font=sansBold)
	root.makeText("description", text, pos=(0, -0.1, 0), scale=0.3,
				  color=black if text and isPlayed else transparent, font=sansBold)
	
	if isPlayed and text:
		model = root.models["description"]
		model.setTexture(model.findTextureStage('*'),
						base.textures["power_vanilla"], 1)
		model.setColor(white)
	if isPlayed: root.box_Model = root.models["box"]
	else: root.box_Model = None
	
	return root


"""Load Hero Cards"""
class NP_Hero(NP_Card):
	def __init__(self, GUI, card, isPlayed):
		super().__init__(GUI, card, isPlayed)
		self.name = type(card).__name__ + "_Hero"
		
		self.cNode_Backup = CollisionNode("Hero_cNode")
		self.cNode_Backup.addSolid(CollisionBox(Point3(0.05, 0, -1.1), 2.2, 0.1, 3.1))
		self.cNode_Backup_Played = CollisionNode("Hero_cNode_Played")
		self.cNode_Backup_Played.addSolid(CollisionBox(Point3(0.05, 0, 0.25), 2, 0.1, 2.2))
		
	def reloadModels(self, loader, imgPath, pickable, reTexture=True):
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
			self.cNode = self.attachNewNode(self.cNode_Backup)
		elif not pickable and self.cNode:
			self.cNode.removeNode()
			self.cNode = None
		
		if reTexture:
			self.models["cardImage"].setTexture(self.models["cardImage"].findTextureStage('*'),
												loader.loadTexture("Images\\%s\\%s.png"%(self.card.index.split('~')[0], type(self.card).__name__)), 1)
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
	
	def loadStatusTexCards(self):  #cardImage y limit -0.001; frame -0.0558; stats_Played -0.12
		loader = self.GUI.loader
		table_PosScaleofTexCard = {"Frozen": (5.2, (0, -0.064, 0.55)),
									"Immune": (5.5, (0, -0.071, 0.5)),
									"Damage": (3, (0, -0.14, 0)),
									"SpellDamage": (5, (0, -0.07, 0)),
									"Stealth": (6, (0, -0.064, 0.2)),
								   }
		for name, posScale in table_PosScaleofTexCard.items():
			texCard = loader.loadModel("TexCards\\ForHeroes\\%s.egg" % name)
			texCard.name = name + "_TexCard"
			texCard.reparentTo(self)
			texCard.setScale(posScale[0])
			texCard.setPos(posScale[1])
			texCard.find("**/+SequenceNode").node().pose(0)
	
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
		
		
def loadHero(base, card, isPlayed=False):
	loader = base.loader
	sansBold = base.font
	cardTexture_Head = loader.loadTexture(findFilepath(card))
	cardTexture = loader.loadTexture("Images\\%s\\%s.png"%(card.index.split('~')[0], type(card).__name__))
	
	root = NP_Hero(base, card, isPlayed)
	#root.reparentTo(base.render)
	cardModel = loader.loadModel("Models\\HeroModels\\Hero.glb")
	cardModel.reparentTo(root)
	
	if isPlayed: color4Card, color4Played = transparent, white
	else: color4Card, color4Played = white, transparent
	#Model names: armor, attack, box, box_Played, card, cardBack, cardImage, frame, health, stats
	for model in cardModel.getChildren():
		name = model.name
		model.setTransparency(True)
		root.models[name] = model
		if name == "cardBack":
			texture, color = base.textures["cardBack"], color4Card
		elif name == "card":
			texture, color = cardTexture, color4Card
		elif name == "cardImage":
			texture, color = cardTexture_Head, color4Played
		elif name == "stats":
			texture, color = base.textures["stats_Hero"], color4Card
		elif name in ("armor", "attack", "frame", "health"):
			texture, color = base.textures["stats_Hero"], color4Played
		else:
			model.setColor(transparent)
			continue #Skip the boxes retexturing
		model.setTexture(model.findTextureStage('*'), texture, 1)
		model.setColor(color)
	#Decide the colors for the stats
	cardType = type(card)
	if isPlayed:
		color_mana = color_armor = transparent
		color_attack_Played = green if card.attack > 0 else 0
		color_health_Played = red if card.health < card.health_max else green
		color_armor_Played = white if card.armor > 0 else transparent
		root.models["armor"].setColor(white if card.armor > 0 else transparent)
		root.models["attack"].setColor(white if card.attack > 0 else transparent)
	else:
		color_mana = white if card.mana == cardType.mana else (green if card.mana < cardType.mana else red)
		color_armor = white
		color_attack_Played = color_health_Played = color_armor_Played = transparent
	root.makeText("mana", str(card.mana), pos=(-1.73, -0.09, 1.15), scale=statTextScale,
				  color=color_mana, font=sansBold)
	root.makeText("armor", str(card.armor), pos=(1.81, -0.09, -4.02), scale=statTextScale,
				  color=color_armor, font=sansBold)
	root.makeText("attack_Played", str(card.attack), pos=(-1.75, -0.122, -1.9), scale=0.9,
				  color=color_attack_Played, font=sansBold)
	root.makeText("health_Played", str(card.health), pos=(1.8, -0.122, -1.9), scale=0.9,
				  color=color_health_Played, font=sansBold)
	root.makeText("armor_Played", str(card.armor), pos=(1.8, -0.122, -0.65), scale=0.9,
				  color=color_armor_Played, font=sansBold)
	
	return root


#Used for secrets and quests
class NP_Secret(NP_Card):
	def __init__(self, GUI, card, isPlayed):
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
		
		self.cNode_Backup = CollisionNode("Secret_cNode")
		self.cNode_Backup.addSolid(CollisionSphere(0, 0, 0, 0.4))
		self.cNode = self.attachNewNode(self.cNode_Backup)
		
	#Assuming the secret icon changes very fast and doesn't need to multithread
	def changeCard(self, card, pickable=True):
		self.card = card
		if pickable: card.btn = self
		self.name = type(card).__name__ + "_Secret_" + str(datetime.now().time())
		if pickable and not self.cNode:
			self.cNode = self.attachNewNode(self.cNode_Backup)
		elif not pickable and self.cNode:
			self.cNode.removeNode()
			self.cNode = None
		
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


def loadSecret_Played(base, card, isPlayed=False):
	loader = base.loader
	
	root = NP_Secret(base, card, isPlayed)
	#root.reparentTo(base.render)
	
	iconModel = loader.loadModel("Models\\HeroModels\\SecretIcon.glb")
	iconModel.reparentTo(root)
	iconModel.setTexture(iconModel.findTextureStage('*'), base.textures["Secret_"+card.Class], 1)
	
	return root



class NP_TurnTrig(NodePath):
	def __init__(self, GUI, card, isPlayed):
		NodePath.__init__(self, card.name + "_TurnTrig")
		#These attributes will be modified by load functions below
		self.card = card
		self.selected = False
		self.GUI = GUI
		
		self.card_Model = None
		cNode_Backup = CollisionNode("TurnTrig_cNode")
		cNode_Backup.addSolid(CollisionBox(Point3(0, 0, 0), 0.45, 0.1, 0.45))
		self.attachNewNode(cNode_Backup)
		
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


class NP_Dormant(NP_Card):
	def __init__(self, GUI, card, isPlayed):
		super().__init__(GUI, card, isPlayed)
		
		self.cNode_Backup_Played = CollisionNode("Minion_cNode_Played")
		self.cNode_Backup_Played.addSolid(CollisionBox(Point3(0.07, 0, 0.35), 1.5, 0.1, 1.9))
		
	def reloadModels(self, loader, imgPath, pickable, reTexture):
		isLegendary = "~Legendary" in self.card.minionInside.index if self.card.minionInside else True
		self.models["legendaryIcon"].setColor(white if isLegendary else transparent)
		for modelName in ("card", "mana"):
			self.models[modelName].setColor(transparent if self.isPlayed else white)
		if reTexture:
			cardTexture = loader.loadTexture(imgPath)
			for modelName in ("card", "cardImage", "nameTag"):
				self.models[modelName].setTexture(self.models[modelName].findTextureStage('*'),
												cardTexture, 1)
		
	def leftClick(self):
		pass
		
	def refresh(self, color=False, stat=False, indicator=False, all=True):
		pass
	
	def manageIconModels(self):
		if "Trigger" not in self.models:
			node_Icon = loadTrigger(self, self.GUI)
			node_Icon.reparentTo(self)
			self.models["Trigger"] = node_Icon
		model = self.models["Trigger"]
		model.setColor(transparent)
		if self.isPlayed and self.card.trigsBoard:
			model.updateText()
			model.setColor(white)
			model.setPos(0, 0, -1.9)
	
	def manageStatusTexCards(self):
		pass
	
	def decideColor(self):
		return transparent
		

def loadDormant(base, card, isPlayed=False):
	loader = base.loader
	cardTexture = loader.loadTexture(findFilepath(card))
	root = NP_Dormant(base, card, isPlayed)
	#root.reparentTo(base.render)
	cardModel = loader.loadModel("Models\\MinionModels\\Dormant.glb")
	cardModel.reparentTo(root)
	
	color4Card = transparent if isPlayed else white
	isLegendary = "~Legendary" in card.minionInside.index if card.minionInside else True
	#Model names: card, cardImage, legendaryIcon, mana, nameTag, Trigger
	for model in cardModel.getChildren():
		name = model.name
		model.setTransparency(True)
		root.models[name] = model
		if name == "mana": texture, color = base.textures["stats_Minion"], color4Card
		elif name == "legendaryIcon":
			texture, color = base.textures["stats_Minion"], white if isLegendary else transparent
		elif name == "cardImage" or name == "nameTag":
			texture, color = cardTexture, white
		elif name == "card": texture, color = cardTexture, color4Card
		model.setTexture(model.findTextureStage('*'), texture, 1)
		model.setColor(color)
	return root


class NP_Trigger(NodePath):
	def __init__(self, carrierBtn):
		NodePath.__init__(self, "NP_Trig")
		self.carrierBtn = carrierBtn
		self.counterText = self.seqNode = None
		self.setTransparency(True)
		
	def trigAni(self, nextAnimWaits=False):
		self.updateText()
		if self.seqNode.isPlaying():
			self.seqNode.play(self.seqNode.getFrame(), self.seqNode.getNumFrames())
		else:
			self.seqNode.play(1, self.seqNode.getNumFrames())
		
		#self.carrierBtn.GUI.animate(seq, afterAllFinished=True, nextAnimWaits=nextAnimWaits)
		
	def updateText(self):
		s = ""
		for trig in self.carrierBtn.card.trigsBoard:
			if trig.counter > -1: s += str(trig.counter) + ' '
		self.counterText.node().setText(s)

class NP_Deathrattle(NodePath):
	def __init__(self, carrierBtn):
		NodePath.__init__(self, "NP_Deathrattle")
		self.carrierBtn = carrierBtn
		self.seqNode = None
		self.setTransparency(True)
	
	def trigAni(self, nextAnimWaits=False):
		if self.seqNode.isPlaying():
			self.seqNode.play(self.seqNode.getFrame(), self.seqNode.getNumFrames())
		else:
			self.seqNode.play(1, self.seqNode.getNumFrames())

class NP_Lifesteal(NodePath):
	def __init__(self, carrierBtn):
		NodePath.__init__(self, "NP_Lifesteal")
		self.carrierBtn = carrierBtn
		self.seqNode = None
		self.setTransparency(True)
	
	def trigAni(self, nextAnimWaits=False):
		if self.seqNode.isPlaying():
			self.seqNode.play(self.seqNode.getFrame(), self.seqNode.getNumFrames())
		else:
			self.seqNode.play(1, self.seqNode.getNumFrames())

class NP_Poisonous(NodePath):
	def __init__(self, carrierBtn):
		NodePath.__init__(self, "NP_Poisonous")
		self.carrierBtn = carrierBtn
		self.seqNode = None
		self.setTransparency(True)
		
	def trigAni(self, nextAnimWaits=False):
		if self.seqNode.isPlaying():
			self.seqNode.play(self.seqNode.getFrame(), self.seqNode.getNumFrames())
		else:
			self.seqNode.play(1, self.seqNode.getNumFrames())


def loadTrigger(carrierBtn, GUI):
	root_Trig = NP_Trigger(carrierBtn)
	iconModel = GUI.loader.loadModel("Models\\Trigger.glb")
	iconModel.setTexture(iconModel.findTextureStage('*'), GUI.textures["Trigger"], 1)
	iconModel.reparentTo(root_Trig)
	textNode = TextNode("Trig Counter")
	textNode.setAlign(TextNode.ACenter)
	root_Trig.counterTextNode = root_Trig.attachNewNode(textNode)
	root_Trig.counterTextNode.setPos(0, -0.2, -4.7)
	root_Trig.counterTextNode.setScale(0.9)
	#Reparent the texCard to this root_trig
	texCard = GUI.loader.loadModel("TexCards\\Shared\\Trigger.egg")
	texCard.reparentTo(root_Trig)
	texCard.setScale(0.8)
	texCard.setPos(0, -0.08, 0)
	root_Trig.seqNode = texCard.find('**/+SequenceNode').node()
	root_Trig.seqNode.pose(0)
	return root_Trig
	
#Lifesteal and Poisonous don't have texts to display
def loadLifesteal(carrierBtn, GUI):
	root_Trig = NP_Lifesteal(carrierBtn)
	iconModel = GUI.loader.loadModel("Models\\Lifesteal.glb")
	iconModel.setTexture(iconModel.findTextureStage('*'), GUI.textures["Lifesteal"], 1)
	iconModel.reparentTo(root_Trig)
	root_Trig.model = iconModel
	texCard = GUI.loader.loadModel("TexCards\\Shared\\Lifesteal.egg")
	texCard.reparentTo(root_Trig)
	texCard.setScale(0.95)
	texCard.setPos(0, -0.08, -0.02)
	root_Trig.seqNode = texCard.find('**/+SequenceNode').node()
	root_Trig.seqNode.pose(0)
	return root_Trig
	
def loadPoisonous(carrierBtn, GUI):
	root_Trig = NP_Poisonous(carrierBtn)
	iconModel = GUI.loader.loadModel("Models\\Poisonous.glb")
	iconModel.setTexture(iconModel.findTextureStage('*'), GUI.textures["Poisonous"], 1)
	iconModel.reparentTo(root_Trig)
	texCard = GUI.loader.loadModel("TexCards\\Shared\\Poisonous.egg")
	texCard.reparentTo(root_Trig)
	texCard.setScale(0.95)
	texCard.setPos(0, -0.08, -0.05)
	root_Trig.seqNode = texCard.find('**/+SequenceNode').node()
	root_Trig.seqNode.pose(0)
	return root_Trig

#Just a placeholder so the processing of Deathrattle is on an equal footing
def loadDeathrattle(carrierBtn, GUI):
	iconModel = GUI.loader.loadModel("Models\\Deathrattle.glb")
	iconModel.setTexture(iconModel.findTextureStage('*'), GUI.textures["Deathrattle"], 1)
	iconModel.setTransparency(True)
	return iconModel


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