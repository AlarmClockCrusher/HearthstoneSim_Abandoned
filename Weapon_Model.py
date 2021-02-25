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


def loadWeapon(render, loader, cardType, mana):
	cardPath = "Models\\WeaponModels\\WeaponImages\\%s.png" % cardType.Class
	imgPath = "Images\\%s\\" % cardType.index.split('~')[0] + cardType.__name__ + ".png"
	sansBold = loader.loadFont('Models\\OpenSans-Bold.ttf')
	
	root = NodePath("root")
	root.reparentTo(render)
	
	"""The card frame. The front face texture is set according to it class"""
	card = loader.loadModel("Models\\WeaponModels\\Card.glb")
	card.reparentTo(root)
	card.setTexture(card.findTextureStage('*'),
					loader.loadTexture(cardPath), 1)
	
	"""Mana display of the card"""
	crystal = loader.loadModel("Models\\WeaponModels\\Mana.glb")
	crystal.reparentTo(root)
	manaText = TextNode("mana")
	manaText.setFont(sansBold)
	manaText.setText('%d' % mana)
	manaTextNode = crystal.attachNewNode(manaText)
	manaTextNode.setScale(1.4)
	manaTextNode.setPos(-2.85, -0.15, 3.85)
	manaText.setAlign(TextNode.ACenter)
	
	"""Card image based on the card type"""
	cardImage = loader.loadModel("Models\\WeaponModels\\WeaponImage.glb")
	cardImage.reparentTo(root)
	cardImage.setTexture(cardImage.findTextureStage('*'),
						 loader.loadTexture(imgPath), 1)
	
	"""Weapon Border of the Card"""
	border = loader.loadModel("Models\\WeaponModels\\Border.glb")
	border.reparentTo(root)
	
	"""Card Text description of the card"""
	description = loader.loadModel("Models\\WeaponModels\\Description.glb")
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
	nameTag = loader.loadModel("Models\\WeaponModels\\NameTag.glb")
	nameTag.reparentTo(root)
	name = cardType.name
	nameText = TextNode("Card Name")
	nameText.setText(name)
	nameText.setFont(sansBold)
	nameText.setAlign(TextNode.ACenter)
	nameTextNode = nameTag.attachNewNode(nameText)
	nameTextNode.setScale(0.5)
	nameTextNode.setPos(0, -0.18, -0.25)
	
	"""Attack of the card, includes the model and the attackText"""
	attack = loader.loadModel("Models\\WeaponModels\\Attack.glb")
	attack.reparentTo(root)
	text = "%d" % cardType.attack
	attackText = TextNode("attack")
	attackText.setText(text)
	attackText.setFont(sansBold)
	attackText.setAlign(TextNode.ACenter)
	attackTextNode = attack.attachNewNode(attackText)
	attackTextNode.setScale(1.3)
	attackTextNode.setPos(-2.85, -0.15, -4.7)
	
	"""Durability of the card, includes the model and the attackText"""
	durability = loader.loadModel("Models\\WeaponModels\\Durability.glb")
	durability.reparentTo(root)
	text = '%d' % cardType.durability
	durabilityText = TextNode("Cadurability")
	durabilityText.setText(text)
	durabilityText.setFont(sansBold)
	durabilityText.setAlign(TextNode.ACenter)
	durabilityTextNode = durability.attachNewNode(durabilityText)
	durabilityTextNode.setScale(1.3)
	durabilityTextNode.setPos(2.9, -0.15, -4.7)
	
	if "~Legendary" in cardType.index:
		legendaryIcon = loader.loadModel("Models\\WeaponModels\\LegendaryIcon.glb")
		legendaryIcon.reparentTo(root)
		rarity = loader.loadModel("Models\\WeaponModels\\Rarity_Legendary.glb")
		rarity.reparentTo(root)
	elif "Uncollectible" not in cardType.index:
		rarity = loader.loadModel("Models\\WeaponModels\\Rarity_Rare.glb")
		rarity.reparentTo(root)
	
	return root


def loadWeapon_Played(render, loader, cardType):
	cardPath = "Models\\WeaponModels\\WeaponImages\\%s.png" % cardType.Class
	imgPath = "Images\\%s\\" % cardType.index.split('~')[0] + cardType.__name__ + ".png"
	sansBold = loader.loadFont('Models\\OpenSans-Bold.ttf')
	
	root = NodePath("root")
	root.reparentTo(render)
	
	"""Card border for weapon"""
	border = loader.loadModel("Models\\WeaponModels\\Border_Played.glb")
	border.reparentTo(root)
	
	"""Card image based on the card type"""
	cardImage = loader.loadModel("Models\\WeaponModels\\WeaponImage_Played.glb")
	cardImage.reparentTo(root)
	cardImage.setTexture(cardImage.findTextureStage('*'),
						 loader.loadTexture(imgPath), 1)
	
	"""Name Tag of the card, includes the model, and the nameText"""
	nameTag = loader.loadModel("Models\\WeaponModels\\NameTag_Played.glb")
	nameTag.reparentTo(root)
	name = cardType.name
	nameText = TextNode("Card Name")
	nameText.setText(name)
	nameText.setFont(sansBold)
	nameText.setAlign(TextNode.ACenter)
	nameTextNode = nameTag.attachNewNode(nameText)
	nameTextNode.setScale(0.5)
	nameTextNode.setPos(0, -0.15, -2.45)
	
	"""Attack of the card, includes the model and the attackText"""
	attack = loader.loadModel("Models\\WeaponModels\\Attack_Played.glb")
	attack.reparentTo(root)
	text = "%d" % cardType.attack
	attackText = TextNode("attack")
	attackText.setText(text)
	attackText.setFont(sansBold)
	attackText.setAlign(TextNode.ACenter)
	attackTextNode = attack.attachNewNode(attackText)
	attackTextNode.setScale(1)
	attackTextNode.setPos(-2.25, -0.17, -1.7)
	
	"""Durability of the card, includes the model and the attackText"""
	durability = loader.loadModel("Models\\WeaponModels\\Durability_Played.glb")
	durability.reparentTo(root)
	text = '%d' % cardType.durability
	durabilityText = TextNode("durability")
	durabilityText.setText(text)
	durabilityText.setFont(sansBold)
	durabilityText.setAlign(TextNode.ACenter)
	durabilityTextNode = durability.attachNewNode(durabilityText)
	durabilityTextNode.setScale(1)
	durabilityTextNode.setPos(2.25, -0.17, -1.7)
	"""Playeds only need to the Legendary Icon surrounding the image"""
	if "~Legendary" in cardType.index:
		legendaryIcon = loader.loadModel("Models\\WeaponModels\\LegendaryIcon_Played.glb")
		legendaryIcon.reparentTo(root)
	
	return root