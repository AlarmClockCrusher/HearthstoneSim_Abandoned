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


def loadHero(render, loader, cardType, mana):
	cardPath = "Models\\HeroModels\\HeroImages\\%s.png" % cardType.Class
	imgPath = "Images\\%s\\" % cardType.index.split('~')[0] + cardType.__name__ + ".png"
	sansBold = loader.loadFont('Models\\OpenSans-Bold.ttf')
	
	root = NodePath("root")
	root.reparentTo(render)
	
	"""The card frame. The front face texture is set according to it class"""
	card = loader.loadModel("Models\\HeroModels\\Card.glb")
	card.reparentTo(root)
	card.setTexture(card.findTextureStage('*'),
					loader.loadTexture(cardPath), 1)
	
	"""Mana display of the card"""
	crystal = loader.loadModel("Models\\HeroModels\\Mana.glb")
	crystal.reparentTo(root)
	manaText = TextNode("mana")
	manaText.setFont(sansBold)
	manaText.setText('%d' % mana)
	manaTextNode = crystal.attachNewNode(manaText)
	manaTextNode.setScale(1.4)
	manaTextNode.setPos(-2.85, -0.15, 3.85)
	manaText.setAlign(TextNode.ACenter)
	
	"""Card image based on the card type"""
	cardImage = loader.loadModel("Models\\HeroModels\\HeroImage.glb")
	cardImage.reparentTo(root)
	cardImage.setTexture(cardImage.findTextureStage('*'),
						 loader.loadTexture(imgPath), 1)
	
	"""Hero Border of the Card"""
	border = loader.loadModel("Models\\HeroModels\\Border.glb")
	border.reparentTo(root)
	
	"""Card Text description of the card"""
	description = loader.loadModel("Models\\HeroModels\\Description.glb")
	description.reparentTo(root)
	cardText = TextNode("description")
	cardText.setFont(sansBold)
	cardText.setTextColor(1, 1, 1, 1)
	cardText.setText(cardType.description)
	cardText.setWordwrap(12)
	cardText.setAlign(TextNode.ACenter)
	cardTextNode = description.attachNewNode(cardText)
	cardTextNode.setScale(0.4)
	cardTextNode.setPos(0, -0.1, -2.2)
	
	"""Name Tag of the card, includes the model, and the nameText"""
	nameTag = loader.loadModel("Models\\HeroModels\\NameTag.glb")
	nameTag.reparentTo(root)
	name = cardType.name
	nameText = TextNode("Card Name")
	nameText.setText(name)
	nameText.setFont(sansBold)
	nameText.setAlign(TextNode.ACenter)
	nameTextNode = nameTag.attachNewNode(nameText)
	nameTextNode.setScale(0.5)
	nameTextNode.setPos(0, -0.18, -0.25)
	
	"""Health of the card, includes the model and the attackText"""
	health = loader.loadModel("Models\\HeroModels\\Health.glb")
	health.reparentTo(root)
	text = '%d' % cardType.health
	healthText = TextNode("Cahealth")
	healthText.setText(text)
	healthText.setFont(sansBold)
	healthText.setAlign(TextNode.ACenter)
	healthTextNode = health.attachNewNode(healthText)
	healthTextNode.setScale(1.3)
	healthTextNode.setPos(2.9, -0.15, -4.7)
	
	if "~Legendary" in cardType.index:
		legendaryIcon = loader.loadModel("Models\\HeroModels\\LegendaryIcon.glb")
		legendaryIcon.reparentTo(root)
		rarity = loader.loadModel("Models\\HeroModels\\Rarity_Legendary.glb")
		rarity.reparentTo(root)
	elif "Uncollectible" not in cardType.index:
		rarity = loader.loadModel("Models\\HeroModels\\Rarity_Rare.glb")
		rarity.reparentTo(root)
	
	return root


def loadHero_Played(render, loader, cardType, attack, health, armor):
	imgPath = "Images\\HerosandPowers\\" + cardType.__name__ + ".png"
	sansBold = loader.loadFont('Models\\OpenSans-Bold.ttf')
	
	root = NodePath("root")
	root.reparentTo(render)
	
	"""Card image based on the card type"""
	cardImage = loader.loadModel("Models\\HeroModels\\HeroHead.glb")
	cardImage.reparentTo(root)
	cardImage.setTexture(cardImage.findTextureStage('*'),
						 loader.loadTexture(imgPath), 1)
	
	"""Attack of the card, includes the model and the attackText"""
	attack_Node = loader.loadModel("Models\\HeroModels\\Attack.glb")
	attack_Node.reparentTo(root)
	text = "%d" % attack
	attackText = TextNode("attack")
	attackText.setText(text)
	attackText.setFont(sansBold)
	attackText.setAlign(TextNode.ACenter)
	attackTextNode = attack_Node.attachNewNode(attackText)
	attackTextNode.setScale(0.5)
	attackTextNode.setPos(-1.98, -0.25, -1.92)
	
	"""Health of the hero"""
	health_Node = loader.loadModel("Models\\HeroModels\\Health.glb")
	health_Node.reparentTo(root)
	text = '%d' % health
	healthText = TextNode("health")
	healthText.setText(text)
	healthText.setFont(sansBold)
	healthText.setAlign(TextNode.ACenter)
	healthTextNode = health_Node.attachNewNode(healthText)
	healthTextNode.setScale(0.5)
	healthTextNode.setPos(2.05, -0.22, -1.92)
	
	"""Armor of the hero"""
	if armor > 0:
		armor_Node = loader.loadModel("Models\\HeroModels\\Armor.glb")
		armor_Node.reparentTo(root)
		text = '%d' % armor
		armorText = TextNode("health")
		armorText.setText(text)
		armorText.setFont(sansBold)
		armorText.setAlign(TextNode.ACenter)
		armorTextNode = armor_Node.attachNewNode(armorText)
		armorTextNode.setScale(0.5)
		armorTextNode.setPos(2.05, -0.25, -1.05)
		
	return root