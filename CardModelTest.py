from datetime import datetime

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

from Game import Game
from Core import *#MindSpike, LordJaraxxus, StonetuskBoar, DeathwingtheDestroyer, GrommashHellscream
from Outlands import *
from Academy import *
from Darkmoon import *
from Barrens import *

CameraDistance = 3

class HSModelTest(ShowBase):
	def __init__(self):
		ShowBase.__init__(self)
		simplepbr.init(max_lights=4)
		self.subject = self.target = None
		
		game = Game()
		game.initialize()
		t1 = datetime.now()
		for i, type in enumerate([HeadhuntersHatchet, BulwarkofAzzinoth, RinlingsRifle, LibramofJudgment_Corrupt,
								  KorvasBloodthorn, StoneskinBasilisk, BloodmageThalnos, AlAkirtheWindlord, GrommashHellscream,
								  ProfessorSlate, StranglethornTiger,
								  Bananas, ArcaneIntellect, ChaosNova, Fireball, FreezingTrap, Avenge, SoulMirror, WildGrowth,
								  ExplosiveTrap, FreezingTrap, UnstableFelbolt,
								  LordJaraxxus, INFERNO,
								  BurningBladePortal]):
			card = type(game, 1)
			#print("Drawing main card", card)
			card_Model = loadCard(self, card)
			card_Model.changeCard(card)
			card_Model.setPos(10*(i % 4), CameraDistance, 15*int(i/4))
			card_Model.setHpr(360, 0, 0)
			#card_Model.setHpr(90, 0, -90)
			card_Model_1 = None
			if card.type == "Minion":
				card_Model_1 = loadMinion_Played(self, card)
				card_Model_1.changeCard(card)
			elif card.type == "Weapon":
				card_Model_1 = loadWeapon_Played(self, card)
				card_Model_1.changeCard(card)
			elif card.type == "Power":
				card_Model_1 = loadPower_Played(self, card)
				card_Model_1.changeCard(card)
			elif card.type == "Hero":
				card_Model_1 = loadHero_Played(self, card)
				card_Model_1.changeCard(card)
			elif card.type == "Dormant":
				card_Model_1 = loadDormant_Played(self, card)
				card_Model_1.changeCard(card)
			if card_Model_1:
				card_Model_1.setPos(-10-10*(i % 4), CameraDistance, 15*int(i/4))
				
		arrow_Model = self.loader.loadModel("Models\\Arrow.glb")
		arrow_Model.reparentTo(self.render)
		arrow_Model.setPos(-30, CameraDistance, 40)
		
		for i, option in enumerate((LesserGolem, GreaterGolem, SuperiorGolem,
									Swiftthistle_1, Earthroot_1, Sungrass_1, Liferoot_1, Fadeleaf_1, GraveMoss_1,
									Swiftthistle_5, Earthroot_5, Sungrass_5, Liferoot_5, Fadeleaf_5, GraveMoss_5,
									Swiftthistle_10, Earthroot_10, Sungrass_10, Liferoot_10, Fadeleaf_10, GraveMoss_10,
									Wildvine_1, Gromsblood_1, Icecap_1, Firebloom_1, Fadeleaf_1, Kingsblood_1,
									Wildvine_5, Gromsblood_5, Icecap_5, Firebloom_5, Fadeleaf_5, Kingsblood_5,
									Wildvine_10, Gromsblood_10, Icecap_10, Firebloom_10, Fadeleaf_10, Kingsblood_10,
									)):
			model = loadCard(self, option())
			model.setPos(50+10 * (i % 4), CameraDistance, 15 * int(i / 4))
			
		for i, option in enumerate((BearForm_Option, CatForm_Option, )):
			model = loadCard(self, option(None))
			model.setPos(10 * (i % 4), CameraDistance, -20 -15 * int(i / 4))
		
		for i, option in enumerate((DemigodsFavor_Option, ShandosLesson_Option, RampantGrowth_Option, Enrich_Option,
									EvolveScales_Option, EvolveSpines_Option, LeaderofthePack_Option, SummonaPanther_Option,
									Rooted_Option, Uproot_Option,
									)):
			model = loadCard(self, option(None))
			model.setPos(50+10 * (i % 4), CameraDistance, -20 - 15 * int(i / 4))
		
		t2 = datetime.now()
		print(t1, t2)
		print("Total time used", datetime.timestamp(t2)-datetime.timestamp(t1))
		
		self.camLens.setFov(38, 38)

	def animate(self, animation, name="Power reset", afterAllFinished=False, blockwhilePlaying=True):
		pass
	
	
HSModelTest().run()