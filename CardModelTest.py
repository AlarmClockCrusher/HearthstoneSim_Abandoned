from datetime import datetime

from direct.showbase.ShowBase import ShowBase
from direct.showbase import DirectObject
from panda3d.core import *
import gltf, simplepbr

from LoadModels import *
from Panda_CustomWidgets import *
from Panda_UICommonPart import *

configVars = """
win-size 1280 720
window-title Card Model Loading Viewer
clock-mode limited
clock-frame-rate 45
"""

loadPrcFileData('', configVars)

from Game import Game
from AcrossPacks import *
from Core import *#MindSpike, LordJaraxxus, StonetuskBoar, DeathwingtheDestroyer, GrommashHellscream
from Outlands import *
from Academy import *
from Darkmoon import *
from Barrens import *

Cam_PosY = -52

Cards2Test = (HeadhuntersHatchet, BulwarkofAzzinoth, RinlingsRifle, LibramofJudgment_Corrupt,
		KorvasBloodthorn, StoneskinBasilisk, BloodmageThalnos, AlAkirtheWindlord, GrommashHellscream,
		ProfessorSlate, StranglethornTiger,
		Bananas, ArcaneIntellect, ChaosNova, Fireball, FreezingTrap, Avenge, SoulMirror, WildGrowth,
		ExplosiveTrap, FreezingTrap, UnstableFelbolt,
		LordJaraxxus, INFERNO, BurningBladePortal,
		)

OptionCards = (LesserGolem, GreaterGolem, SuperiorGolem,
				Swiftthistle_1, Earthroot_1, Sungrass_1, Liferoot_1, Fadeleaf_1, GraveMoss_1,
				Swiftthistle_5, Earthroot_5, Sungrass_5, Liferoot_5, Fadeleaf_5, GraveMoss_5,
				Swiftthistle_10, Earthroot_10, Sungrass_10, Liferoot_10, Fadeleaf_10, GraveMoss_10,
				Wildvine_1, Gromsblood_1, Icecap_1, Firebloom_1, Fadeleaf_1, Kingsblood_1,
				Wildvine_5, Gromsblood_5, Icecap_5, Firebloom_5, Fadeleaf_5, Kingsblood_5,
				Wildvine_10, Gromsblood_10, Icecap_10, Firebloom_10, Fadeleaf_10, Kingsblood_10,
				)
Option_Cards_Spells = (DemigodsFavor_Option, ShandosLesson_Option, RampantGrowth_Option, Enrich_Option,
						EvolveScales_Option, EvolveSpines_Option, LeaderofthePack_Option, SummonaPanther_Option,
						Rooted_Option, Uproot_Option,
						)

class VariousTest(Panda_UICommon):
	def __init__(self):
		ShowBase.__init__(self)
		self.boardID = "2 Classic Stormwind"
		self.ID = 1
		self.modelTemplates = {}
		self.manaModels = {}
		self.seqHolder = []
		#self.disableMouse()
		
		#self.loadBackground()
		self.prepare()
		
		self.smallTest()
		
	def testEntireGameDisplay(self):
		self.handZones = {1: HandZone(self, 1), 2: HandZone(self, 2)}
		self.minionZones = {1: MinionZone(self, 1), 2: MinionZone(self, 2)}
		self.heroZones = {1: HeroZone(self, 1), 2: HeroZone(self, 2)}
		self.deckZones = {1: DeckZone(self, 1), 2: DeckZone(self, 2)}
		
		self.seqHolder.append(Sequence())
		
		for ID in range(1, 3):
			self.handZones[ID].placeCards()
			self.minionZones[ID].placeCards()
			self.heroZones[ID].placeCards()
			self.heroZones[ID].drawMana(self.Game.Manas.manas[ID], self.Game.Manas.manasUpper[ID],
										self.Game.Manas.manasLocked[ID], self.Game.Manas.manasOverloaded[ID])
			self.heroZones[ID].placeSecrets()
			self.heroZones[ID].placeTurnTrigs()
			self.deckZones[ID].draw(15)
			
		for ID in range(1, 3):
			for minion in self.Game.minions[ID]:
				minion.btn.placeIcons()
				minion.btn.statChangeAni()
				minion.btn.statusChangeAni()
			weapon = self.Game.availableWeapon(ID)
			if weapon:
				weapon.btn.placeIcons()
				weapon.btn.statusChangeAni()
				
		self.heroExplodeAni([self.Game.heroes[ID] for ID in range(1, 3)])
		
		self.seqHolder.pop(0).start()
		#Sequence(Wait(3), Func(self.deckZones[1].fatigueAni, 8)).start()
		
	def prepare(self):
		self.subject = self.target = None
		self.font = self.loader.loadFont("Models\\OpenSans-Bold.ttf")
		
		for name in ("Mana", "EmptyMana", "LockedMana", "OverloadedMana"):
			model = self.loader.loadModel("Models\\BoardModels\\Mana.glb")
			model.reparentTo(self.render)
			model.setTexture(model.findTextureStage('*'),
							 self.loader.loadTexture("Models\\BoardModels\\%s.png" % name), 1)
			self.manaModels[name] = [model]
			for i in range(9):
				self.manaModels[name].append(model.copyTo(self.render))
		
		game = Game()
		game.initialize()
		game.initialize_Details({}, {}, Rexxar, Uther)
		game.Hand_Deck.hands = {1: [card(game, 1) for card in (SoulMirror, YseratheDreamer, BulwarkofAzzinoth,
															   LordJaraxxus, ImprisonedFelmaw, LightningBloom)],
								2: [card(game, 2) for card in (SoulMirror, YseratheDreamer, BulwarkofAzzinoth,
															   LordJaraxxus, ImprisonedFelmaw, LightningBloom)]
								}
		game.Hand_Deck.decks = {1: [card(game, 1) for card in (KorvasBloodthorn, SoulMirror, YseratheDreamer, BulwarkofAzzinoth,
															   LordJaraxxus, ImprisonedFelmaw, LightningBloom)],
								2: [card(game, 2) for card in (SoulMirror, YseratheDreamer, BulwarkofAzzinoth,
															   LordJaraxxus, LibramofJudgment_Corrupt, ImprisonedFelmaw, LightningBloom)]
								}
		game.minions = {1: [card(game, 1) for card in (YseratheDreamer, BurningBladePortal, ImprisonedFelmaw,
													  KorvasBloodthorn, AlAkirtheWindlord, StoneskinBasilisk, FallenHero)],
						2: [card(game, 2) for card in (FallenHero, BurningBladePortal, ImprisonedFelmaw,
											  			KorvasBloodthorn, AlAkirtheWindlord, Peon, SpiderTank)]
						}
		for ID in range(1, 3):
			for minion in game.minions[ID]: minion.onBoard = True
		game.weapons = {1: [BulwarkofAzzinoth(game, 1)], 2: [LibramofJudgment_Corrupt(game, 1)]}
		game.weapons[1][0].onBoard = True
		game.weapons[2][0].onBoard = True
		game.Secrets.secrets = {1: [card(Game, 1) for card in (FreezingTrap, Bamboozle)],
								2: [card(Game, 2) for card in (Counterspell, Avenge, Shenanigans)]}
		game.turnStartTrigger = [InstructorFireheart_Effect(game, ID) for ID in (1, 1, 1, 1, 1, 1)] + [LothraxiontheRedeemed_Effect(game, ID) for ID in (2, 2, 2, 2, 2)]
		self.Game = game
		self.prepareTexturesandModels()
		self.setCamera_RaySolid()
		
	def testTrigIconShining(self):
		models = []
		for i, name in enumerate(("Trigger", "Deathrattle", "Lifesteal", "Poisonous")):
			model = self.modelTemplates[name]
			model.setPos(i * 2, 0, 2)
			model.reparentTo(self.render)
			model.setColor(white)
			if name == "Trigger": model.find("Trig Counter").node().setText("1 3")
			models.append(model)
		
	def smallTest(self):
		pass
	
	def testCurve(self):
		card = LightningBolt(self.Game, 1)
		np, btn_Card = genCard(self, card, isPlayed=False, pickable=False)
		interval_1 = btn_Card.genMoPathIntervals("Models\\BoardModels\\DisplayCurve_Lower.egg", duration=0.3)
		interval_2 = btn_Card.genMoPathIntervals("Models\\BoardModels\\DisplayCurve_Upper.egg", duration=0.3)
		Sequence(Wait(2), interval_1, Wait(2), interval_2).loop()
		
		

class TestRaySolid(ShowBase):
	def __init__(self):
		super().__init__()
		plane = self.loader.loadModel("Models\\BoardModels\\Background.glb")
		plane.reparentTo(self.render)
		plane.setPosHpr(0, 0, -10, 0, -90, 0)
		
		option = self.loader.loadModel("Models\\Option.glb")
		option.reparentTo(self.render)
		
		cNode = CollisionNode("CNDE")
		cNode.addSolid(CollisionBox((0, 0, 0), (2, 2, 2)))
		cNodePath = self.render.attachNewNode(cNode)
		cNodePath.setPos(20, 0, -5)
		cNodePath.show()
		
		textNode = TextNode("Test")
		textNode.setText("200000")
		nodePath = self.render.attachNewNode(textNode)
		nodePath.setScale(20)
		nodePath.setHpr(0, -90, 0)
		
		self.cTrav = CollisionTraverser()
		self.collHandler = CollisionHandlerQueue()
		self.raySolid = CollisionRay()
		self.raySolid.setOrigin(0, 0, 50)
		cNode_Picker = CollisionNode("Picker Collider c_node")
		cNode_Picker.addSolid(self.raySolid)
		pickerNode = self.camera.attachNewNode(cNode_Picker)
		pickerNode.show()  #For now, show the pickerRay collision with the card models
		self.cTrav.addCollider(pickerNode, self.collHandler)
		self.camLens.setFov(51.1, 27.5)
		self.cam.setPosHpr(0, 0, 51.5, 0, -90, 0)
		
		self.accept("mouse1", self.mouse1_Down)
		self.accept("mouse1-up", self.mouse1_Up)
	
	def setRaySolidDirection(self):
		mpos = self.mouseWatcherNode.getMouse()
		#Reset the Collision Ray orientation, based on the mouse position
		self.raySolid.setDirection(25 * mpos.getX(), 14 * mpos.getY(), -50.5)
	
	def mouse1_Down(self):
		if self.mouseWatcherNode.hasMouse():
			self.setRaySolidDirection()
	
	def mouse1_Up(self):
		if self.mouseWatcherNode.hasMouse():
			self.setRaySolidDirection()
			if self.collHandler.getNumEntries() > 0:
				self.collHandler.sortEntries()
				cNode_Picked = self.collHandler.getEntry(0).getIntoNodePath()
				"""The scene graph tree is written in C. To store/read python objects, use NodePath.setPythonTag/getPythonTag()"""
				cNode_Picked.getParent().getPythonTag("btn").leftClick()


class SmallTest(ShowBase):
	def __init__(self):
		super().__init__()
		nodepath, btn = genCard(self, LostinthePark(None, 1), isPlayed=False, pickable=False)
		Sequence(Wait(2), Func(btn.changeCard, DefendtheSquirrels(None, 1), False, False))
	
VariousTest().run()
#TestRaySolid().run()
#SmallTest().run()