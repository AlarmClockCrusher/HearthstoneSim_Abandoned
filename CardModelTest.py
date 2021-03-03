from direct.showbase.ShowBase import ShowBase
from direct.showbase import DirectObject
from panda3d.core import *
import gltf, simplepbr

from LoadModels import *

configVars = """
win-size 1280 720
window-title Card Model Loading Viewer
clock-mode limited
clock-frame-rate 45
"""

loadPrcFileData('', configVars)


from Basic import Reinforce, Garrosh
from Classic import *
from Outlands import *
from Darkmoon import *

CameraDistance = 3

class HSModelTest(ShowBase):
	def __init__(self):
		ShowBase.__init__(self)
		simplepbr.init(max_lights=4)
		
		card1 = loadMinion(self.render, self.loader, Deathwing, orig=True)
		card2 = loadMinion_Played(self.render, self.loader, AbusiveSergeant)
		card3 = loadWeapon(self.render, self.loader, RinlingsRifle, orig=True)
		card4 = loadWeapon_Played(self.render, self.loader, BulwarkofAzzinoth)
		card5 = loadSpell(self.render, self.loader, SoulMirror, orig=True)
		card6 = loadPower(self.render, self.loader, Reinforce, 1, orig=True)
		card7 = loadPower_Played(self.render, self.loader, Reinforce)
		card8 = loadHero_Played(self.render, self.loader, Garrosh, 3, 26, 10)
		card9 = loadMinion(self.render, self.loader, FacelessManipulator, orig=True)
		card10 = loadMinion_Played(self.render, self.loader, Deathwing)
		card11 = loadWeapon(self.render, self.loader, FieryWarAxe, orig=True)
		card12 = loadWeapon_Played(self.render, self.loader, Gorehowl)
		card13 = loadHero(self.render, self.loader, LordJaraxxus, orig=True)
		
		card1.reparentTo(self.render)
		card2.reparentTo(self.render)
		card3.reparentTo(self.render)
		card4.reparentTo(self.render)
		card5.reparentTo(self.render)
		card6.reparentTo(self.render)
		card7.reparentTo(self.render)
		card8.reparentTo(self.render)
		card9.reparentTo(self.render)
		card10.reparentTo(self.render)
		card11.reparentTo(self.render)
		card12.reparentTo(self.render)
		card13.reparentTo(self.render)
		
		card1.setPos(0, CameraDistance, 0)
		card2.setPos(10, CameraDistance, 0)
		card3.setPos(20, CameraDistance, 0)
		card4.setPos(30, CameraDistance, 0)
		card5.setPos(0, CameraDistance, 15)
		card6.setPos(10, CameraDistance, 15)
		card7.setPos(20, CameraDistance, 15)
		card8.setPos(30, CameraDistance, 15)
		card9.setPos(0, CameraDistance, -15)
		card10.setPos(10, CameraDistance, -15)
		card11.setPos(20, CameraDistance, -15)
		card12.setPos(30, CameraDistance, -15)
		card13.setPos(0, CameraDistance, 30)
		
		#card = self.loader.loadModel("SpellModels\\Card.glb")
		#card.reparentTo(self.render)
		#card.setPos(0, 3, 0)
		##card.setHpr(0, 90, 0)
		#card.setTexture(card.findTextureStage('*'),
		#				self.loader.loadTexture("SpellModels\\SpellImages\\Druid.png"), 1)
		#
		#sansBold = self.loader.loadFont('OpenSans-Bold.ttf')
		#
		#mana = self.loader.loadModel("SpellModels\\Mana.glb")
		#mana.reparentTo(self.render)
		#mana.setPos(0, 3, 0)
		#manaText = TextNode("mana")
		#manaText.setFont(sansBold)
		#manaText.setText('1')
		#manaTextNode = mana.attachNewNode(manaText)
		#manaTextNode.setScale(2)
		#manaTextNode.setPos(-3, -0.1, 3.9)
		#manaText.setAlign(TextNode.ACenter)
		#
		#sansLight = self.loader.loadFont('OpenSans-Light.ttf')
		#tpBold = TextProperties()
		#tpBold.setFont(sansBold)
		#tpLight = TextProperties()
		#tpLight.setFont(sansLight)
		#tpMgr = TextPropertiesManager.getGlobalPtr()
		#tpMgr.setProperties("bold", tpBold)
		#tpMgr.setProperties("light", tpLight)
		#"""Card Text description of the card"""
		#description = self.loader.loadModel("SpellModels\\CardText.glb")
		#description.reparentTo(self.render)
		#description.setPos(0, 3, 0)
		#cardText = TextNode("description")
		#cardText.setFont(sansBold)
		##cardText.setShadow(0.05, 0.05)
		##cardText.setShadowColor(1, 1, 1, 1)
		#cardText.setTextColor(0, 0, 0, 1)
		#cardText.setText("Lifesteal\nCurrently the magnetic field is not the optimal value.")
		#cardText.setWordwrap(12)
		#cardText.setAlign(TextNode.ACenter)
		#cardTextNode = description.attachNewNode(cardText)
		#cardTextNode.setScale(0.4)
		#cardTextNode.setPos(-0.05, -0.1, -2.1)
		#
		##Name Tag of the card, includes the model, and the nameText
		#nameTag = self.loader.loadModel("SpellModels\\NameTag.glb")
		#nameTag.reparentTo(self.render)
		#nameTag.setPos(0, 3, 0)
		#
		#nameText = TextNode("Card Name")
		#nameText.setText("Bananas")
		#nameText.setFont(sansBold)
		#nameText.setAlign(TextNode.ACenter)
		#nameTextNode = nameTag.attachNewNode(nameText)
		#nameTextNode.setScale(0.6)
		#nameTextNode.setPos(0, -0.1, -0.2)
		#
		#cardImage = self.loader.loadModel("SpellModels\\SpellImage.glb")
		#cardImage.reparentTo(self.render)
		#cardImage.setPos(0, 3, 0)
		#cardImage.setTexture(cardImage.findTextureStage('*'),
		#					 self.loader.loadTexture("SpellModels\\Bananas.png"), 1)
		#
		#legendaryIcon = self.loader.loadModel("SpellModels\\LegendaryIcon.glb")
		#legendaryIcon.reparentTo(self.render)
		#legendaryIcon.setPos(0, 3, 0)
		#
		#school = self.loader.loadModel("SpellModels\\School.glb")
		#school.reparentTo(self.render)
		#school.setPos(0, 3, 0)
		#nameText = TextNode("School")
		#nameText.setText("Fel")
		#nameText.setFont(sansBold)
		#nameText.setAlign(TextNode.ACenter)
		#nameTextNode = nameTag.attachNewNode(nameText)
		#nameTextNode.setScale(0.4)
		#nameTextNode.setPos(0, -0.1, -4.5)


#legendaryIcon.setHpr(0, 90, 0)
#blue = self.loader.loadTexture('WeaponModels\\BattleAxe.png')
#for c in smiley.findAllMatches("**/+GeomNode"):
#	gn = c.node() #This gn is a cube that has (CullFaceAttrib MaterialAttrib TextureAttrib))
#	print(gn, type(gn))
#	print(gn.getNumGeoms()) #return 1
#	for i in range(gn.getNumGeoms()):
#		state = gn.getGeomState(i)
#		print(state)
#		print(TextureAttrib.getClassType())
#		state = state.removeAttrib(TextureAttrib.getClassType())
#		gn.setGeomState(i, state)
#	#for i in range(gn.getNumGeoms()):
#	#	state = gn.getGeomState(i)
#	#	state =
#self.NameTagObj.setTexture(blue, 1)


HSModelTest().run()