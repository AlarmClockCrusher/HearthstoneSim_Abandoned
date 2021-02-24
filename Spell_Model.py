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


def loadSpell(render, loader, cardType, mana):
	cardPath = "Models\\SpellModels\\SpellImages\\%s.png"%cardType.Class
	imgPath = "Images\\%s\\" % cardType.index.split('~')[0] + cardType.__name__ + ".png"
	sansBold = loader.loadFont('Models\\OpenSans-Bold.ttf')
	
	root = NodePath("root")
	root.reparentTo(render)
	
	"""The card frame. The front face texture is set according to it class"""
	card = loader.loadModel("Models\\SpellModels\\Card.glb")
	card.reparentTo(root)
	card.setTexture(card.findTextureStage('*'),
						 loader.loadTexture(cardPath), 1)
	
	"""Mana display of the card"""
	crystal = loader.loadModel("Models\\SpellModels\\Mana.glb")
	crystal.reparentTo(root)
	manaText = TextNode("mana")
	manaText.setFont(sansBold)
	manaText.setText('%d'%mana)
	manaTextNode = crystal.attachNewNode(manaText)
	manaTextNode.setScale(1.4)
	manaTextNode.setPos(-2.9, -0.1, 4)
	manaText.setAlign(TextNode.ACenter)
	
	"""Card image based on the card type"""
	cardImage = loader.loadModel("Models\\SpellModels\\SpellImage.glb")
	cardImage.reparentTo(root)
	cardImage.setTexture(cardImage.findTextureStage('*'),
						 loader.loadTexture(imgPath), 1)
	
	"""Card Text description of the card"""
	description = loader.loadModel("Models\\SpellModels\\CardText.glb")
	description.reparentTo(root)
	cardText = TextNode("description")
	cardText.setFont(sansBold)
	cardText.setTextColor(0, 0, 0, 1)
	cardText.setText(cardType.description)
	cardText.setWordwrap(12)
	cardText.setAlign(TextNode.ACenter)
	cardTextNode = description.attachNewNode(cardText)
	cardTextNode.setScale(0.4)
	cardTextNode.setPos(0, -0.1, -2.5)
	
	"""Name Tag of the card, includes the model, and the nameText"""
	nameTag = loader.loadModel("Models\\SpellModels\\NameTag.glb")
	nameTag.reparentTo(root)
	name = cardType.name
	nameText = TextNode("Card Name")
	nameText.setText(name)
	nameText.setFont(sansBold)
	nameText.setAlign(TextNode.ACenter)
	nameTextNode = nameTag.attachNewNode(nameText)
	nameTextNode.setScale(0.5)
	nameTextNode.setPos(0, -0.1, -0.2)
	
	if "~Legendary" in cardType.index:
		legendaryIcon = loader.loadModel("Models\\SpellModels\\LegendaryIcon.glb")
		legendaryIcon.reparentTo(root)
		rarity = loader.loadModel("Models\\SpellModels\\Rarity_Legendary.glb")
		rarity.reparentTo(root)
	elif "Uncollectible" not in cardType.index:
		rarity = loader.loadModel("Models\\SpellModels\\Rarity_Rare.glb")
		rarity.reparentTo(root)
		
	if cardType.school:
		school = loader.loadModel("Models\\SpellModels\\School.glb")
		school.reparentTo(root)
		nameText = TextNode("School")
		nameText.setText(cardType.school)
		nameText.setFont(sansBold)
		nameText.setAlign(TextNode.ACenter)
		nameTextNode = nameTag.attachNewNode(nameText)
		nameTextNode.setScale(0.4)
		nameTextNode.setPos(0, -0.1, -4.45)
	
	return root