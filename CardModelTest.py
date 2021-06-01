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
		self.manaModels = {}
		
		self.loadBackground()
		self.prepare()
		self.cam.setPos(0, -51.5, 0)
		
		self.handZones = {1: HandZone(self, 1), 2: HandZone(self, 2)}
		self.minionZones = {1: MinionZone(self, 1), 2: MinionZone(self, 2)}
		self.heroZones = {1: HeroZone(self, 1), 2: HeroZone(self, 2)}
		self.deckZones = {1: DeckZone(self, 1), 2: DeckZone(self, 2)}
		
		for ID in range(1, 3):
			self.handZones[ID].placeCards()
			self.minionZones[ID].placeCards()
			self.heroZones[ID].placeCards()
			self.heroZones[ID].drawMana()
			self.heroZones[ID].placeSecrets()
			self.heroZones[ID].placeTurnTrigs()
			self.deckZones[ID].draw()
		
		Sequence(Wait(3), Func(self.deckZones[1].fatigueAni, 8)).start()
		
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
		game.initialize_Details({}, {}, {}, {}, {}, Rexxar, Uther, deck1=[], deck2=[])
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
													  KorvasBloodthorn, AlAkirtheWindlord, Peon, SpiderTank)],
						2: [card(game, 2) for card in (YseratheDreamer, BurningBladePortal, ImprisonedFelmaw,
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
		self.camLens.setFov(51.1, 27.5)
		
	def testTrigIconShining(self):
		models = []
		for i, name in enumerate(("Trigger", "Deathrattle", "Lifesteal", "Poisonous")):
			model = self.modelTemplates[name]
			model.setPos(i * 2, 0, 2)
			model.reparentTo(self.render)
			model.setColor(white)
			if name == "Trigger": model.find("Trig Counter").node().setText("1 3")
			models.append(model)
		Sequence(Wait(1), Func(self.func, models), Wait(4)).start()
	
	def func(self, models, hide=False):
		if hide:
			for model in models: model.setColor(transparent)
		else:
			for model in models: model.find("TexCard").find("+SequenceNode").node().loop(True, 1, 20)
		
	def testCards(self):
		t1 = datetime.now()
		for pos in ((0, -1.05, MinionZone1_Z), (0, -1.05, MinionZone2_Z)):
			card = KorvasBloodthorn(self.Game, 1)
			model, btn_Card = genCard(self, card, isPlayed=True)
			model.setPos(pos)
			model.getPythonTag("btn").placeIcons()
		
		for pos in (Weapon1_Pos, Weapon2_Pos):
			card = RinlingsRifle(self.Game, 1)
			model, btn_Card = genCard(self, card, isPlayed=True)
			model.setPos(pos)
			model.getPythonTag("btn").placeIcons()
		
		for pos in (Hero1_Pos, Hero2_Pos):
			card = LordJaraxxus(self.Game, 1)
			#card.attack = 8
			model, btn_Card = genCard(self, card, isPlayed=True)
			model.setPos(pos)
		
		for pos in (Power1_Pos, Power2_Pos):
			card = SteadyShot(self.Game, 1)
			model, btn_Card = genCard(self, card, isPlayed=True)
			model.setPos(pos)
		
		self.cam.setPos(0, -51.5, 0)
		
		
		pos_Hands_1, hpr_Hands_1 = posHandsTable[HandZone1_Z], hprHandsTable[HandZone1_Z]
		pos_Hands_2, hpr_Hands_2 = posHandsTable[HandZone2_Z], hprHandsTable[HandZone2_Z]
		for i in range(6):
			card = SoulMirror(self.Game, 1)
			pos, hpr = pos_Hands_1[6][i], hpr_Hands_1[6][i]
			genCard(self, card, isPlayed=False, pos=pos, hpr=hpr)
		
		for i in range(3):
			card = LordJaraxxus(self.Game, 1)
			pos, hpr = pos_Hands_2[3][i], hpr_Hands_2[3][i]
			genCard(self, card, isPlayed=False, pos=pos, hpr=hpr)
		
		t2 = datetime.now()
		print("Time needed to place 4 cards", datetime.timestamp(t2) - datetime.timestamp(t1))
		
	def testCardArrays(self):
		t1 = datetime.now()
		for i, type in enumerate(Cards2Test):
			card = type(self.Game, 1)
			card_Model = genCard(self, card, isPlayed=True)
			card_Model.setPos(6*(i % 4), 0, 8*int(i/4))
			self.cam.setPos(0, Cam_PosY, 0)
			
		t2 = datetime.now()
		print("Time used: ", datetime.timestamp(t2) - datetime.timestamp(t1))
	
	def testTrigsSecrets(self):
		posTrigs = calc_posTrigs(6, Hero1_Pos[0], Hero1_Pos[1], Hero1_Pos[2])
		for i in range(6):
			trigCard = SigilofSilence(self.Game, 1)
			genTurnTrigIcon(self, trigCard, pos=posTrigs[i])
		
		posTrigs = calc_posTrigs(4, Hero2_Pos[0], Hero2_Pos[1], Hero2_Pos[2])
		for j in range(4):
			trigCard = InstructorFireheart(self.Game, 1)
			genTurnTrigIcon(self, trigCard, pos=posTrigs[j])
		
	def testCurve(self):
		card = LightningBolt(self.Game, 1)
		np, btn_Card = genCard(self, card, isPlayed=False, pickable=False)
		interval_1 = btn_Card.genMoPathIntervals("Models\\BoardModels\\DisplayCurve_Lower.egg", duration=0.3)
		interval_2 = btn_Card.genMoPathIntervals("Models\\BoardModels\\DisplayCurve_Upper.egg", duration=0.3)
		Sequence(Wait(2), interval_1, Wait(2), interval_2).loop()
		
		
#HSModelTest().run()
VariousTest().run()
#TestPythonTag().run()
