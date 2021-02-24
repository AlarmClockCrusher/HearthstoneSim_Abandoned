from direct.showbase.ShowBase import ShowBase
from panda3d.core import loadPrcFileData, OrthographicLens
from panda3d.core import GeomVertexFormat, GeomVertexData, TransparencyAttrib
from panda3d.core import Geom, GeomTriangles, GeomVertexWriter, GeomNode

from panda3d.core import *
from direct.gui.OnscreenText import OnscreenText

import gltf, simplepbr

configVars = """
win-size 1280 720
show-frame-rate-meter 1
"""


def loadMinion(render, loader, cardType, mana):
	cardPath = "Models\\MinionModels\\MinionImages\\%s.png" % cardType.Class
	imgPath = "Images\\%s\\" % cardType.index.split('~')[0] + cardType.__name__ + ".png"
	sansBold = loader.loadFont('Models\\OpenSans-Bold.ttf')
	
	root = NodePath("root")
	root.reparentTo(render)
	
	"""The card frame. The front face texture is set according to it class"""
	card = loader.loadModel("Models\\MinionModels\\Card.glb")
	card.reparentTo(root)
	card.setTexture(card.findTextureStage('*'),
					loader.loadTexture(cardPath), 1)
	
	"""Mana display of the card"""
	crystal = loader.loadModel("Models\\MinionModels\\Mana.glb")
	crystal.reparentTo(root)
	manaText = TextNode("mana")
	manaText.setFont(sansBold)
	manaText.setText('%d'%mana)
	manaTextNode = crystal.attachNewNode(manaText)
	manaTextNode.setScale(1.4)
	manaTextNode.setPos(-2.85, -0.2, 3.85)
	manaText.setAlign(TextNode.ACenter)
	
	"""Card image based on the card type"""
	cardImage = loader.loadModel("Models\\MinionModels\\MinionImage.glb")
	cardImage.reparentTo(root)
	cardImage.setTexture(cardImage.findTextureStage('*'),
						 loader.loadTexture(imgPath), 1)
	
	"""Card Text description of the card"""
	description = loader.loadModel("Models\\MinionModels\\Description.glb")
	description.reparentTo(root)
	cardText = TextNode("description")
	cardText.setFont(sansBold)
	cardText.setTextColor(0, 0, 0, 1)
	cardText.setText(cardType.description)
	cardText.setWordwrap(14)
	cardText.setAlign(TextNode.ACenter)
	cardTextNode = description.attachNewNode(cardText)
	cardTextNode.setScale(0.4)
	cardTextNode.setPos(0.1, -0.3, -2.5)
	
	"""Name Tag of the card, includes the model, and the nameText"""
	nameTag = loader.loadModel("Models\\MinionModels\\NameTag.glb")
	nameTag.reparentTo(root)
	name = cardType.name
	nameText = TextNode("Card Name")
	nameText.setText(name)
	nameText.setFont(sansBold)
	nameText.setAlign(TextNode.ACenter)
	nameTextNode = nameTag.attachNewNode(nameText)
	nameTextNode.setScale(0.5)
	nameTextNode.setPos(0.2, -0.3, -0.5)
	
	"""Attack of the card, includes the model and the attackText"""
	attack = loader.loadModel("Models\\MinionModels\\Attack.glb")
	attack.reparentTo(root)
	text = "%d"%cardType.attack
	attackText = TextNode("attack")
	attackText.setText(text)
	attackText.setFont(sansBold)
	attackText.setAlign(TextNode.ACenter)
	attackTextNode = attack.attachNewNode(attackText)
	attackTextNode.setScale(1.3)
	attackTextNode.setPos(-2.8, -0.3, -4.7)
	
	"""Health of the card, includes the model and the attackText"""
	health = loader.loadModel("Models\\MinionModels\\Health.glb")
	health.reparentTo(root)
	text = '%d'%cardType.health
	healthText = TextNode("Cahealth")
	healthText.setText(text)
	healthText.setFont(sansBold)
	healthText.setAlign(TextNode.ACenter)
	healthTextNode = health.attachNewNode(healthText)
	healthTextNode.setScale(1.3)
	healthTextNode.setPos(2.9, -0.3, -4.7)
	
	if "~Legendary" in cardType.index:
		legendaryIcon = loader.loadModel("Models\\MinionModels\\LegendaryIcon.glb")
		legendaryIcon.reparentTo(root)
		rarity = loader.loadModel("Models\\MinionModels\\Rarity_Legendary.glb")
		rarity.reparentTo(root)
	elif "Uncollectible" not in cardType.index:
		rarity = loader.loadModel("Models\\MinionModels\\Rarity_Rare.glb")
		rarity.reparentTo(root)
		
	if cardType.race:
		race = loader.loadModel("Models\\MinionModels\\Race.glb")
		race.reparentTo(root)
		raceText = TextNode("race")
		raceText.setText(cardType.race)
		raceText.setFont(sansBold)
		raceText.setAlign(TextNode.ACenter)
		raceTextNode = race.attachNewNode(raceText)
		raceTextNode.setScale(0.4)
		raceTextNode.setPos(0.2, -0.3, -4.55)
	
	return root