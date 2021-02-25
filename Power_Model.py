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


def loadPower(render, loader, powerType, mana):
	imgPath = "Images\\HerosandPowers\\" + powerType.__name__ + ".png"
	sansBold = loader.loadFont('Models\\OpenSans-Bold.ttf')
	
	root = NodePath("root")
	root.reparentTo(render)
	
	"""The power frame"""
	power = loader.loadModel("Models\\PowerModels\\Power.glb")
	power.reparentTo(root)
	
	"""Mana display of the power"""
	crystal = loader.loadModel("Models\\PowerModels\\Mana.glb")
	crystal.reparentTo(root)
	manaText = TextNode("mana")
	manaText.setFont(sansBold)
	manaText.setText('%d' % mana)
	manaTextNode = crystal.attachNewNode(manaText)
	manaTextNode.setScale(1.4)
	manaTextNode.setPos(0, -0.25, 4)
	manaText.setAlign(TextNode.ACenter)
	
	"""Power image based on the power type"""
	powerImage = loader.loadModel("Models\\PowerModels\\PowerImage.glb")
	powerImage.reparentTo(root)
	powerImage.setTexture(powerImage.findTextureStage('*'),
						 loader.loadTexture(imgPath), 1)
	
	"""Power Border of the Power"""
	border = loader.loadModel("Models\\PowerModels\\Border.glb")
	border.reparentTo(root)
	
	"""Power Text description of the power"""
	powerText = TextNode("description")
	powerText.setFont(sansBold)
	powerText.setTextColor(0, 0, 0, 1)
	powerText.setText(powerType.description)
	powerText.setWordwrap(12)
	powerText.setAlign(TextNode.ACenter)
	powerTextNode = power.attachNewNode(powerText)
	powerTextNode.setScale(0.4)
	powerTextNode.setPos(0, -0.15, -2.2)
	
	"""Name Tag of the power, includes the model, and the nameText"""
	nameTag = loader.loadModel("Models\\PowerModels\\NameTag.glb")
	nameTag.reparentTo(root)
	name = powerType.name
	nameText = TextNode("Power Name")
	nameText.setText(name)
	nameText.setFont(sansBold)
	nameText.setAlign(TextNode.ACenter)
	nameTextNode = nameTag.attachNewNode(nameText)
	nameTextNode.setScale(0.5)
	nameTextNode.setPos(0, -0.2, 0)
	
	return root


def loadPower_Played(render, loader, powerType):
	imgPath = "Images\\HerosandPowers\\" + powerType.__name__ + ".png"
	sansBold = loader.loadFont('Models\\OpenSans-Bold.ttf')
	
	root = NodePath("root")
	root.reparentTo(render)
	
	"""Power border for weapon"""
	border = loader.loadModel("Models\\PowerModels\\Border_Played.glb")
	border.reparentTo(root)
	
	"""Mana display of the power"""
	crystal = loader.loadModel("Models\\PowerModels\\Mana_Played.glb")
	crystal.reparentTo(root)
	manaText = TextNode("mana")
	manaText.setFont(sansBold)
	manaText.setText('%d'%powerType.mana)
	manaTextNode = crystal.attachNewNode(manaText)
	manaTextNode.setScale(1.4)
	manaTextNode.setPos(-0.1, -0.35, 1.75)
	manaText.setAlign(TextNode.ACenter)
	
	"""Power image based on the power type"""
	powerImage = loader.loadModel("Models\\PowerModels\\PowerImage_Played.glb")
	powerImage.reparentTo(root)
	powerImage.setTexture(powerImage.findTextureStage('*'),
						 loader.loadTexture(imgPath), 1)
	
	return root