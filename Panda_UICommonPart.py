import math

from direct.gui.DirectGui import *
from direct.interval.IntervalGlobal import Wait, Func
from direct.interval.MetaInterval import Sequence, Parallel
from direct.showbase.ShowBase import ShowBase
from direct.task import Task

from Game import *
from GenPools_BuildDecks import *
from LoadModels import *
from Panda_CustomWidgets import *

import time
from datetime import datetime
import pickle
#from collections import deque

w, h = 1440, 800
configVars = """
win-size 1440 800
window-title Hearthstone Simulator
clock-mode limited
clock-frame-rate 45
text-use-harfbuzz true
"""

loadPrcFileData('', configVars)


boardPool = ["1 Classic Ogrimmar", "2 Classic Stormwind", "3 Classic Stranglethorn", "4 Classic Four Wind Valley",
			#"5 Naxxramas", "6 Goblins vs Gnomes, "7 Black Rock Mountain", "8 The Grand Tournament", "9 League of Explorers Museum", "10 League of Explorers Ruins",
			#"11 Corrupted Stormwind, "12 Karazhan", "13 Gadgetzan",
			#"14 Un'Goro", "15 Frozen Throne", "16 Kobolds": TransferStudent_Kobold,
			#"17 Witchwood", "18 Boomsday Lab", "19 Rumble": TransferStudent_Rumble,
			#"20 Dalaran", "21 Uldum Desert", "22 Uldum Oasis", "23 Dragons",
			"24 Outlands", "25 Scholomance Academy", "26 Darkmoon Faire",
			 ]


def pickleObj2Bytes(obj):
	return pickle.dumps(obj, 0)

def unpickleBytes2Obj(s):
	return pickle.loads(s)

CamPos_Z = 51.5
pos_OffBoardTrig_1, pos_OffBoardTrig_2 =  (-10, -1.8, 10), (-10, 5, 10)

class Panda_UICommon(ShowBase):
	def __init__(self, disableMouse=True):
		ShowBase.__init__(self)
		self.cam.name, self.camera.name = "Model2Keep_Cam", "Model2Keep_Camera"
		#simplepbr.init(max_lights=4)
		if disableMouse: self.disableMouse()
		self.WAIT, self.FUNC = Wait, Func
		self.SEQUENCE, self.PARALLEL  = Sequence, Parallel
		self.LERP_Pos, self.LERP_PosHpr, self.LERP_PosHprScale = LerpPosInterval, LerpPosHprInterval, LerpPosHprScaleInterval
		self.genCard = genCard
		
		"""Attributes to store info"""
		self.ID, self.showEnemyHand = 0, True
		self.boardID = ''
		self.btnBeingDragged = self.arrow = self.np_Fatigue = self.btnBoard = self.btnTurnEnd = None
		self.np_CardZoomIn = None
		#Game play info related
		self.posMulligans = None
		self.mulliganStatus = {1: [0, 0, 0], 2: [0, 0, 0, 0]}
		self.selectedSubject = ""
		self.subject = self.target = None
		self.pos = self.choice = self.UI = -1  #起手调换为-1
		self.discover = None
		self.btns2Remove = []
		#Animation related
		self.gamePlayQueue = []
		self.gamePlayThread = None
		self.seqHolder, self.seq2Play, self.seqReady = [], None, False
		
		self.Game = Game(self)
		self.Game.mode = 0
		self.Game.initialize()
		
		#Online Pvp related
		self.sock = None
		self.waiting4Server, self.msg_BacktoLayer1, self.timer = False, '', 60
		
		#Models
		self.modelTemplates = {}
		self.font = self.loader.loadFont("Models\\OpenSans-Bold.ttf")
		self.minionZones, self.heroZones, self.handZones, self.deckZones = {}, {}, {}, {}
		self.textures, self.manaModels, self.forGameTex = {}, {}, {}
		#Flag whether the game is still loading models for the cards
		self.loading = "Loading. Please Wait"
		
		self.cTrav = self.collHandler = self.raySolid = None
		self.accept("mouse1", self.mouse1_Down)
		self.accept("mouse1-up", self.mouse1_Up)
		self.accept("mouse3", self.mouse3_Down)
		self.accept("mouse3-up", self.mouse3_Up)
		
		threading.Thread(target=self.keepExecutingGamePlays, name="GameThread", daemon=True).start()
		self.init_CollisionSetup()
		
	def prepareTexturesandModels(self, layer1Window=None):
		if layer1Window: layer1Window.lbl_LoadingProgress.config(text="基础贴图加载中...", fg="brown4")
		else: print("基础贴图加载中...")
		self.textures = {"cardBack": self.loader.loadTexture("Models\\CardBack.png"),
						 "Deathrattle": self.loader.loadTexture("Models\\Deathrattle.png"),
						 "Lifesteal": self.loader.loadTexture("Models\\Lifesteal.png"),
						 "Poisonous": self.loader.loadTexture("Models\\Poisonous.png"),
						 "Trigger": self.loader.loadTexture("Models\\Trigger.png"),
						 "SpecTrig": self.loader.loadTexture("Models\\SpecTrig.png"),
						 "Hourglass": self.loader.loadTexture("Models\\Hourglass.png"),
						 }
		self.forGameTex["TurnStart_Banner"] = makeTexCard(self, filePath="TexCards\\ForGame\\TurnStartBanner.egg",
								 							pos=(0, 0, -0.3), scale=15, aspectRatio=332/768,
															name="Tex2Keep_TurnStart_Banner")[0]
		self.forGameTex["TurnStart_Particles"] = makeTexCard(self, filePath="TexCards\\ForGame\\TurnStartParticles.egg",
								 							pos=(0, 0, -1), scale=18, name="Tex2Keep_TurnStart_Particles")[0]
		for name in ("SecretHunter", "SecretMage", "SecretPaladin", "SecretRogue"):
			self.forGameTex[name] = makeTexCard(self, filePath="TexCards\\ForGame\\%s.egg"%name, name="Tex2Keep_"+name, getSeqNode=False)[0]
			
		for cardType in ("Minion", "Spell", "Weapon", "Hero", "Power"):
			self.textures["stats_" + cardType] = self.loader.loadTexture("Models\\%sModels\\Stats.png" % cardType)
		for Class in ("Hunter", "Mage", "Paladin", "Rogue"):
			self.textures["Secret_" + Class] = self.loader.loadTexture("Models\\HeroModels\\Secret_%s.png" % Class)
		for expansion in ("BASIC", "BLACK_TEMPLE", "CORE", "DARKMOON_FAIRE", "EXPERT1", "SCHOLOMANCE", "THE_BARRENS", "STORMWIND"):
			self.textures["minion_" + expansion] = self.loader.loadTexture("Models\\MinionModels\\%s.png" % expansion)
			self.textures["spell_" + expansion] = self.loader.loadTexture("Models\\SpellModels\\%s.png" % expansion)
		self.textures["power_vanilla"] = self.loader.loadTexture("Models\\PowerModels\\Vanilla.png")
		for Class in ("Demon Hunter,Hunter", "Demon Hunter", "Druid", "Hunter", "Mage", "Paladin",
					  "Priest", "Rogue", "Shaman", "Warlock", "Warrior", "Neutral"):
			self.textures["weapon_" + Class] = self.loader.loadTexture("Models\\WeaponModels\\WeaponCards\\%s.png" % Class)
		
		if layer1Window: layer1Window.lbl_LoadingProgress.config(text="基础特效加载中...", fg="gold")
		else: print("基础特效加载中...")
		t1 = datetime.now()
		for iconName, scale in zip(("Trigger", "Deathrattle", "Lifesteal", "Poisonous", "SpecTrig", "Hourglass"),
									(1.1, 3, 1.2, 1.3, 0.63, None),
									):
			np_Icon = self.loader.loadModel("Models\\%s.glb" % iconName)
			np_Icon.setTexture(np_Icon.findTextureStage('0'), self.textures[iconName], 1)
			self.modelTemplates[iconName] = np_Icon
			np_Icon.name = iconName + "_Icon"
			np_Icon.setTransparency(True)
			np_Icon.setColor(transparent)
			if iconName == "Hourglass":
				makeText(np_Icon, "Trig Counter", '', pos=(-0.02, -0.18, 0.04), scale=0.6, font=self.font, color=white)
			else: makeTexCard(self, "TexCards\\Shared\\%s.egg" % iconName, pos=(0, 0, 0), scale=scale, parent=np_Icon)
			#np_Icon is now: Trigger_Icon
								#Trigger|TexCard
								#Trigger|Trigger
							#Hourglass_Icon
								#Hourglass|Trig Counter_TextNode
								#Hourglass|Hourglass
		#Get the templates for the cards, they will load the trig icons and status tex cards
		if layer1Window: layer1Window.lbl_LoadingProgress.config(text="随从模型加载中...", fg="deep pink")
		else: print("随从模型加载中...")
		self.modelTemplates["Minion"] = loadCard(self, SilverHandRecruit(self.Game, 1))
		if layer1Window: layer1Window.lbl_LoadingProgress.config(text="法术模型加载中...", fg="purple3")
		else: print("法术模型加载中...")
		self.modelTemplates["Spell"] = loadCard(self, TheCoin(self.Game, 1))
		if layer1Window: layer1Window.lbl_LoadingProgress.config(text="武器模型加载中...", fg="blue")
		else: print("武器模型加载中...")
		self.modelTemplates["Weapon"] = loadCard(self, FieryWarAxe_Core(self.Game, 1))
		if layer1Window: layer1Window.lbl_LoadingProgress.config(text="英雄模型加载中...", fg="red")
		else: print("英雄模型加载中...")
		self.modelTemplates["Hero"] = loadCard(self, Rexxar(self.Game, 1))
		if layer1Window: layer1Window.lbl_LoadingProgress.config(text="英雄技能模型加载中...", fg="black")
		else: print("英雄技能模型加载中...")
		self.modelTemplates["Power"] = loadCard(self, SteadyShot(self.Game, 1))
		if layer1Window: layer1Window.lbl_LoadingProgress.config(text="抉择模型加载中...", fg="green3")
		else: print("抉择选项模型加载中...")
		self.modelTemplates["Option"] = loadCard(self, RampantGrowth_Option(None))
		
		t2 = datetime.now()
		print("Time needed to load tex cards", datetime.timestamp(t2) - datetime.timestamp(t1))
	
	#Load the board, turnEndButton, manaModels and arrow
	def loadBackground(self):
		if not self.btnBoard: #Loaded models can be reused
			plane = self.loader.loadModel("Models\\BoardModels\\Background.glb")
			plane.setTexture(plane.findTextureStage('*'),
							 self.loader.loadTexture("Models\\BoardModels\\%s.png" % self.boardID), 1)
			plane.name = "Model2Keep_Board"
			plane.reparentTo(self.render)
			plane.setPos(0, 0, 1)
			collNode_Board = CollisionNode("Board_c_node")
			collNode_Board.addSolid(CollisionBox(Point3(0, 0.4, -0.2), 15, 7.5, 0.2))
			plane.attachNewNode(collNode_Board)  #.show()
			self.btnBoard = Btn_Board(self, plane)
			plane.setPythonTag("btn", self.btnBoard)
		else:
			self.btnBoard.np.setTexture(self.btnBoard.np.findTextureStage('*'),
							 			self.loader.loadTexture("Models\\BoardModels\\%s.png" % self.boardID), 1)
		#Load the turn end button
		if not self.btnTurnEnd:
			turnEnd = self.loader.loadModel("Models\\BoardModels\\TurnEndButton.glb")
			turnEnd.reparentTo(self.render)
			turnEnd.name = "Model2Keep_TurnEndBtn"
			turnEnd.setPos(TurnEndBtn_Pos)
			collNode_TurnEndButton = CollisionNode("TurnEndButton_c_node")
			collNode_TurnEndButton.addSolid(CollisionBox(Point3(0, 0, 0), 2, 1, 0.2))
			turnEnd.attachNewNode(collNode_TurnEndButton)  #.show()
			self.btnTurnEnd = Btn_TurnEnd(self, turnEnd)
			turnEnd.setPythonTag("btn", self.btnTurnEnd)
		
		#The fatigue model to show when no more card to draw
		if not self.np_Fatigue:
			self.np_Fatigue = self.loader.loadModel("Models\\BoardModels\\Fatigue.glb")
			self.np_Fatigue.setTexture(self.np_Fatigue.findTextureStage('0'),
									   self.loader.loadTexture("Models\\BoardModels\\Fatigue.png"), 1)
			self.np_Fatigue.name = "Model2Keep_Fatigue"
			self.np_Fatigue.reparentTo(self.render)
			self.np_Fatigue.setPos(4, 0, 0)
			textNode = TextNode("Fatigue_TextNode")
			textNode.setFont(self.font)
			textNode.setTextColor(red)
			textNode.setText('1')
			textNode.setAlign(TextNode.ACenter)
			textNodePath = self.np_Fatigue.attachNewNode(textNode)
			textNodePath.setPosHpr(-0.03, -1.3, 0.04, 0, -90, 0)
			
		if not self.arrow:
			self.arrow = self.loader.loadModel("Models\\Arrow.glb")
			self.arrow.setTexture(self.arrow.findTextureStage('0'), self.loader.loadTexture("Models\\Arrow.png"), 1)
			self.arrow.reparentTo(self.render)
			self.arrow.name = "Model2Keep_Arrow"
			self.arrow.stash()
		
		if not self.manaModels:
			for name in ("Mana", "EmptyMana", "LockedMana", "OverloadedMana"):
				model = self.loader.loadModel("Models\\BoardModels\\Mana.glb")
				model.name = "Model2Keep_" + name
				model.reparentTo(self.render)
				model.setTexture(model.findTextureStage('*'),
								 self.loader.loadTexture("Models\\BoardModels\\%s.png" % name), 1)
				self.manaModels[name] = [model]
				for i in range(9):
					self.manaModels[name].append(model.copyTo(self.render))
	
	def initMulliganDisplay(self, firstTime):
		pass
	
	def setCamera_RaySolid(self):
		self.camLens.setFov(51.1, 27.5)
		self.cam.setPosHpr(0, 0, CamPos_Z, 0, -90, 0)
		try: self.raySolid.setOrigin(0, 0, CamPos_Z)
		except: pass
		props = WindowProperties()
		props.setSize(w, h)
		self.win.requestProperties(props)
		
	def initGameDisplay(self):
		self.loadBackground()
		self.setCamera_RaySolid()
		
		for ID in range(1, 3):
			self.deckZones[ID].draw(len(self.Game.Hand_Deck.decks[ID]), len(self.Game.Hand_Deck.hands[ID]))
			self.heroZones[ID].drawMana(self.Game.Manas.manas[ID], self.Game.Manas.manasUpper[ID],
												  self.Game.Manas.manasLocked[ID], self.Game.Manas.manasOverloaded[ID])
			self.heroZones[ID].placeCards()
			
	#To be overridden by each GUI
	def startMulligan(self, btn_Mulligan):
		pass
	
	"""Animation control setup"""
	def keepExecutingGamePlays(self):
		while True:
			if self.gamePlayQueue:
				self.gamePlayQueue.pop(0)()
				self.cancelSelection()
			time.sleep(0.1)
			
	def highlightTargets(self, legalTargets):
		print("Highlighting targets", [card.name for card in legalTargets])
		game = self.Game
		for ID in range(1, 3):
			for card in game.minions[ID] + game.Hand_Deck.hands[ID] + [game.heroes[ID]]:
				if card not in legalTargets: card.btn.dimDown()
	
	def resetCardColors(self):
		game = self.Game
		for ID in range(1, 3):
			for card in game.minions[ID] + game.Hand_Deck.hands[ID] + [game.heroes[ID]]:
				if card and card.btn and card.btn.np: card.btn.np.setColor(white)
				else: print("Reset color fail", card, card.btn)
				
	def decideCardColors(self):
		game = self.Game
		for card in game.Hand_Deck.hands[1] + game.Hand_Deck.hands[2]:
			card.effCanTrig()
			card.checkEvanescent()
		curTurn = game.turn
		for ID in range(1, 3):
			showCardColor = ID == curTurn and (self.showEnemyHand or not self.sock or ID == self.ID)
			for card in game.Hand_Deck.hands[ID] + game.minions[ID]:
				if not card.btn: print("Card doesn't have a btn", card)
				card.btn.setBoxColor(card.btn.decideColor() if showCardColor else (1, 1, 1, 0))
			hero, power = game.heroes[ID], game.powers[ID]
			if hero.btn: hero.btn.setBoxColor(hero.btn.decideColor() if showCardColor else (1, 1, 1, 0))
			if power.btn: power.btn.setBoxColor(power.btn.decideColor() if showCardColor else (1, 1, 1, 0))
		
		if curTurn == self.ID and not game.morePlaysPossible():
			if not self.btnTurnEnd.jobDone: self.btnTurnEnd.changeDisplay(jobDone=True)
		elif self.btnTurnEnd.jobDone: self.btnTurnEnd.changeDisplay(jobDone=False)
		
	"""Animation details"""
	#Card/Hand animation
	def putaNewCardinHandAni(self, card):
		genCard(self, card, isPlayed=False, onlyShowCardBack=self.need2beHidden(card))
		self.handZones[card.ID].placeCards()
	
	def cardReplacedinHand_Refresh(self, card):
		genCard(self, card, isPlayed=False, onlyShowCardBack=self.need2beHidden(card))
		self.handZones[card.ID].placeCards()
	
	def transformAni_inHand(self, target, newCard):
		texCard = seqNode = None
		if not self.need2beHidden(target):
			texCard, seqNode = makeTexCard(self, filePath="TexCards\\Shared\\TransformMist.egg",
										   pos=(0, 0, 0.2), scale=2.3)
		seq_Holder = self.seqHolder[-1]
		if target.type == newCard.type:
			newCard.btn = target.btn
			if texCard:
				seq_Holder.append(Sequence(Func(texCard.reparentTo, target.btn.np), Func(seqNode.play), Wait(0.05),
										   Func(target.btn.changeCard, newCard, False)))
				seq_Holder.append(Func(Sequence(Wait(0.75), Func(texCard.removeNode)).start))
			else: seq_Holder.append(Func(target.btn.changeCard, newCard, False))
			target.btn = None
		else:
			np_New, btn_New = genCard(self, newCard, isPlayed=False, pickable=True, onlyShowCardBack=target.btn.onlyCardBackShown)
			np_Old = target.btn.np
			if texCard:
				seq_Holder.append(Sequence(Func(texCard.reparentTo, np_Old), Func(seqNode.play), Wait(0.05),
							   		Func(np_New.reparentTo, np_Old), Wait(0.75), Func(np_New.wrtReparentTo, self.render),
							   		Func(np_Old.removeNode))
							)
			else: seq_Holder.append(Func(np_New.reparentTo, np_Old), Func(np_New.wrtReparentTo, self.render), Func(np_Old.removeNode))
		
	def transformAni_onBoard(self, target, newCard):
		newCard.btn = target.btn
		texCard = seqNode = None
		if target.type == "Minion" == newCard.type == "Minion":
			texCard, seqNode = makeTexCard(self, filePath="TexCards\\Shared\\TransformMist.egg",
											pos=(0, 0, 0.2), scale=1.9)
		seq_Holder = self.seqHolder[-1]
		if not texCard: seq_Holder.append(Func(target.btn.changeCard, newCard, True))
		else:
			seq_Holder.append(Sequence(Func(texCard.reparentTo, target.btn.np), Func(seqNode.play), Wait(0.05),
									   Func(target.btn.changeCard, newCard, True)))
			seq_Holder.append(Func(Sequence(Wait(0.65), Func(texCard.removeNode)).start))
		target.btn = None
			
	#因为可以结算的时候一般都是手牌已经发生了变化，所以只能用序号来标记每个btn了
	#linger is for when you would like to see the card longer before it vanishes
	def cardsLeaveHandAni(self, cards, ID=0, enemyCanSee=True, linger=False):
		handZone, para, btns2Destroy = self.handZones[ID], Parallel(), [card.btn for card in cards]
		#此时需要离开手牌的牌已经从Game.Hand_Deck.hands里面移除,手牌列表中剩余的就是真实存在还在手牌中的
		for btn, card in zip(btns2Destroy, cards):
			seq, nodePath = Sequence(), btn.np
			if enemyCanSee and btn.onlyCardBackShown:
				seq.append(Func(btn.changeCard, card, True, False))
			x, y, z = nodePath.getPos()
			if not -9 < y < 9:
				y = DiscardedCard1_Y if self.ID == btn.card.ID else DiscardedCard2_Y
				seq.append(LerpPosHprInterval(nodePath, duration=0.3, pos=(x, y, z), startHpr=(0, 0, 0), hpr=(0, 0, 0)))
				seq.append(Wait(0.6))
			#如果linger为True就留着这张牌的显示，到之后再处理
			if not linger: seq.append(Func(nodePath.detachNode))
			para.append(seq)
		handZone.placeCards()
		self.seqHolder[-1].append(para)
		
	def hand2BoardAni(self, card, fromDragPos=False):
		ID = card.ID
		handZone, minionZone = self.handZones[ID], self.minionZones[ID]
		#At this point, minion has been inserted into the minions list. The btn on the minion won't change. It will simply change "isPlayed"
		ownMinions = self.Game.minions[ID]
		x, y, z = posMinionsTable[minionZone.y][len(ownMinions)][ownMinions.index(card)]
		#Must be first set to isPlayed=True, so that ensuing statChangeAni can correctly respond
		card.btn.isPlayed = True
		card.btn.reassignBox()
		seq = Sequence(LerpPosHprScaleInterval(card.btn.np, duration=0.25, pos=(x, y, z+5), hpr=(0, 0, 0), scale=scale_Minion),
							Func(card.btn.changeCard, card, True),
							Parallel(minionZone.placeCards(False), handZone.placeCards(False)),
							name="Hand to board Ani")
		self.seqHolder[-1].append(seq)
	
	def board2HandAni(self, card):
		handZone, minionZone = self.handZones[card.ID], self.minionZones[card.ID]
		#At this point, minion has been extracted from the minion lists
		ownMinions, ownHands = self.Game.minions[card.ID], self.Game.Hand_Deck.hands[card.ID]
		x, y, z = card.btn.np.getPos()
		#Must be first set to isPlayed=True, so that ensuing statChangeAni can correctly respond
		card.btn.isPlayed = True
		card.btn.reassignBox()
		seq = Sequence(LerpPosInterval(card.btn.np, duration=0.25, pos=Point3(x, y, z + 5)),
							Wait(0.15), Func(card.btn.changeCard, card, False), Wait(0.2),
							Func(self.deckZones[self.ID].draw, len(self.Game.Hand_Deck.decks[self.ID]), len(ownHands)),
							Parallel(handZone.placeCards(False), minionZone.placeCards(False)),
							name="Board 2 hand ani")
		self.seqHolder[-1].append(seq)
	
	def deck2BoardAni(self, card):
		ID = card.ID
		nodePath, btn = genCard(self, card, isPlayed=False) #place these cards at pos(0, 0, 0), to be move into proper position later
		#At this point, minion has been inserted into the minions list. The btn on the minion won't change. It will simply change "isPlayed"
		deckZone, minionZone = self.deckZones[ID], self.minionZones[ID]
		ownMinions = self.Game.minions[ID]
		x, y, z = posMinionsTable[minionZone.y][len(ownMinions)][ownMinions.index(card)]
		deckPos = Deck1_Pos if ID == self.ID else Deck2_Pos
		#The minion must be first set to isPlayed=True, so that the later statChangeAni can correctly respond
		btn.isPlayed = True
		card.btn.reassignBox()
		sequence = Sequence(Func(deckZone.draw, len(card.Game.Hand_Deck.decks[ID]), len(self.Game.Hand_Deck.hands[ID])),
							LerpPosHprScaleInterval(nodePath, duration=0.3, startPos=deckPos, startHpr=hpr_Deck, startScale=deckScale,
													pos=(x, y, z + 5), hpr=(0, 0, 0), scale=scale_Minion),
							Wait(0.2), Func(btn.changeCard, card, True),
							minionZone.placeCards(False),
							name="Deck to board Ani")
		self.seqHolder[-1].append(sequence)
		
	def revealaCardfromDeckAni(self, ID, index, bingo):
		card = self.Game.Hand_Deck.decks[ID][index]
		deckZone = self.deckZones[card.ID]
		pos_Pause = DrawnCard1_PausePos if self.ID == card.ID else DrawnCard2_PausePos
		nodePath, btn = genCard(self, card, isPlayed=False)  #the card is preloaded and positioned at (0, 0, 0)
		sequence = Sequence(Func(nodePath.setPosHpr, deckZone.pos, (90, 90, 0)),
							Func(deckZone.draw, len(self.Game.Hand_Deck.decks[card.ID]), len(self.Game.Hand_Deck.hands[card.ID])),
							LerpPosHprScaleInterval(btn.np, duration=0.4, pos=pos_Pause, hpr=(0, 0, 0), scale=1, blendType="easeOut"),
							Wait(0.6)
							)
		if bingo:
			sequence.append(LerpScaleInterval(nodePath, duration=0.2, scale=1.15))
			sequence.append(LerpScaleInterval(nodePath, duration=0.2, scale=1))
		sequence.append(LerpPosHprInterval(nodePath, duration=0.4, pos=deckZone.pos, hpr=(90, 90, 0), blendType="easeOut"))
		sequence.append(Func(nodePath.removeNode))
		sequence.append(Wait(0.3))
		self.seqHolder[-1].append(sequence)
	
	#Amulets and dormants also count as minions
	def removeMinionorWeaponAni(self, card):
		if not (card.btn and card.btn.np): return
		#At this point, minion/dormant/weapon has left the containing list
		self.seqHolder[-1].append(Func(card.btn.np.detachNode))
		if card.type in ("Minion", "Dormant"):
			self.minionZones[card.ID].placeCards()
			
	#直接出现，而不是从手牌或者牌库中召唤出来
	def summonAni(self, card):
		#At this point, minion has been inserted into the minions list
		genCard(self, card, isPlayed=True)
		self.minionZones[card.ID].placeCards()
		self.seqHolder[-1].append(Wait(0.15))
		
	def weaponEquipAni(self, card):
		nodePath, btn = genCard(self, card, isPlayed=True)
		x, y, z = self.heroZones[card.ID].weaponPos
		self.seqHolder[-1].append(LerpPosHprInterval(nodePath, duration=0.3, startPos=(x, y+0.2, z+5), pos=(x, y, z), hpr=(0, 0, 0)))
		
	def secretDestroyAni(self, secrets):
		if secrets:
			heroZone = self.heroZones[secrets[0].ID]
			pos_Start = Point3(heroZone.x, heroZone.y - 0.2, heroZone.z * 0.8)
			para = Parallel()
			left_X = -3 * (len(secrets) - 1) / 2
			btns2Destroy = []
			for i, secret in enumerate(secrets):
				nodePath, btn = self.addCard(secret, pos=pos_Start, pickable=False)
				
			self.seqHolder[-1].append(para)
			
	def drawCardAni_LeaveDeck(self, card):
		deckZone = self.deckZones[card.ID]
		pos_Pause = DrawnCard1_PausePos if self.ID == card.ID else DrawnCard2_PausePos
		nodePath, btn = genCard(self, card, isPlayed=False, 
								onlyShowCardBack=self.sock and card.ID != self.ID and not self.showEnemyHand) #the card is preloaded and positioned at (0, 0, 0)
		self.seqHolder[-1].append(Sequence(Func(deckZone.draw, len(self.Game.Hand_Deck.decks[card.ID]), len(self.Game.Hand_Deck.hands[card.ID])),
											LerpPosHprScaleInterval(nodePath, duration=0.4, startPos=deckZone.pos, pos=pos_Pause, 
											startHpr=(90, 90, 0), hpr=(0, 0, 0), scale=1, blendType="easeOut"),
											Wait(0.8))
								)
		
	def drawCardAni_IntoHand(self, oldCard, newCard):
		btn = oldCard.btn
		handZone = self.handZones[oldCard.ID]
		if btn.card != newCard:
			print("Drawn card is changed", newCard)
			handZone.transformHands([btn], [newCard])
		handZone.placeCards()
		self.seqHolder[-1].append(Func(self.deckZones[oldCard.ID].draw, len(self.Game.Hand_Deck.decks[newCard.ID]),
									   len(self.Game.Hand_Deck.hands[newCard.ID])))
		
	def millCardAni(self, card):
		deckZone = self.deckZones[card.ID]
		
		pos_Pause = DrawnCard1_PausePos if self.ID == card.ID else DrawnCard2_PausePos
		nodePath, btn = genCard(self, card, isPlayed=False)
		interval = LerpPosHprScaleInterval(nodePath, duration=0.4, startPos=deckZone.pos, pos=pos_Pause,
										   startHpr=(90, 90, 0), hpr=(0, 0, 0), scale=1, blendType="easeOut")
		texCard, seqNode = makeTexCard(self, "TexCards\\ForGame\\Mill.egg", scale=27)
		self.seqHolder[-1].append(Sequence(interval, Func(texCard.setPos, pos_Pause[0], pos_Pause[1]-1, pos_Pause[2]+0.4),
										   Func(seqNode.play), Wait(0.5), Func(nodePath.removeNode), Wait(0.5), Func(texCard.removeNode)))
		
	def cardLeavesDeckAni(self, card, enemyCanSee=True):
		deckZone = self.deckZones[card.ID]
		pos_Pause = DrawnCard1_PausePos if self.ID == card.ID else DrawnCard2_PausePos
		nodePath, btn = genCard(self, card, isPlayed=False)  #the card is preloaded and positioned at (0, 0, 0)
		sequence = Sequence(Func(nodePath.setPosHpr, deckZone.pos, (90, 90, 0)),
							Func(deckZone.draw, len(self.Game.Hand_Deck.decks[card.ID]), len(self.Game.Hand_Deck.hands[card.ID])),
							LerpPosHprScaleInterval(btn.np, duration=0.4, pos=pos_Pause, hpr=(0, 0, 0), scale=1, blendType="easeOut"),
							Wait(0.6), Func(nodePath.detachNode)
							)
		self.seqHolder[-1].append(sequence)
		
	def shuffleintoDeckAni(self, cards, enemyCanSee=True):
		ID = cards[0].ID
		deckZone = self.deckZones[ID]
		para, btns = Parallel(), []
		leftMostPos = -(len(cards)-1) / 2 * 5
		for i, card in enumerate(cards):
			num = len(cards) - i
			if card.btn and card.btn.np:
				nodePath, btn = card.btn.np, card.btn
				para.append(Sequence(Wait(0.2 * num + 0.4),
									LerpPosHprInterval(nodePath, duration=0.25, pos=deckZone.pos, hpr=(90, 90, 0)),
									Func(nodePath.detachNode) #Can be garbage collected
									)
							)
			else:
				nodePath, btn = genCard(self, card, isPlayed=False, pickable=False, 
										onlyShowCardBack=not enemyCanSee and self.need2beHidden(card))
				para.append(Sequence(Func(nodePath.setPos, leftMostPos+5*i, 1.5, 8),
									Wait(0.2 * num + 0.4),
									LerpPosHprInterval(nodePath, duration=0.25, pos=deckZone.pos, hpr=(90, 90, 0)),
									Func(nodePath.detachNode) #Can be garbage collected
									)
							)
		self.seqHolder[-1].append(para)
		self.seqHolder[-1].append(Func(deckZone.draw, len(self.Game.Hand_Deck.decks[ID]), len(self.Game.Hand_Deck.hands[ID])))
	
	def showTempText(self, text):
		text = OnscreenText(text=text, pos=(0, 0), scale=0.1, fg=(1, 0, 0, 1),
							align=TextNode.ACenter, mayChange=1, font=self.font,
							bg=(0.5, 0.5, 0.5, 0.8))
		Sequence(Wait(1.5), Func(text.destroy)).start()
	
	def wait(self, duration=0, showLine=False):
		pass
	
	def offsetNodePath_Wait(self, nodePath, duration=0.3, dx=0, dy=0, dz=0, dh=0, dp=0, dr=0, add2Queue=True):
		if add2Queue:
			self.seqHolder[-1].append(Func(self.offsetNodePath, nodePath, duration, dx, dy, dz, dh, dp, dr))
			self.seqHolder[-1].append(Wait(duration))
		else: return Sequence(Func(self.offsetNodePath, nodePath, duration, dx, dy, dz, dh, dp, dr), Wait(duration))
		
	def offsetNodePath(self, nodePath, duration=0.3, dx=0, dy=0, dz=0, dh=0, dp=0, dr=0):
		x, y, z = nodePath.getPos()
		h, p, r = nodePath.getHpr()
		LerpPosHprInterval(nodePath, duration=duration, pos=(x+dx, y+dy, z+dz), hpr=(h+dh, p+dp, r+dr)).start()
	
	def moveNodePath2_wrt_Wait(self, nodePath_2Move, nodePath_Ref, duration=0.3, dx=0, dy=0, dz=0, add2Queue=True):
		if add2Queue:
			self.seqHolder[-1].append(Func(self.moveNodePath2_wrt, nodePath_2Move, nodePath_Ref, duration, dx, dy, dz))
			self.seqHolder[-1].append(Wait(duration))
		else: return Sequence(Func(self.moveNodePath2_wrt, nodePath_2Move, nodePath_Ref, duration, dx, dy, dz), Wait(duration))
		
	def moveNodePath2_wrt(self, nodePath_2Move, nodePath_Ref, duration, dx, dy, dz):
		x, y, z = nodePath_Ref.getPos()
		LerpPosInterval(nodePath_2Move, duration=duration, pos=(x+dx, y+dy, z+dz)).start()
	
	def attackAni_HitandReturn(self, subject, target):
		np_Subject, np_Target = subject.btn.np, target.btn.np
		if subject.type == "Minion":
			ownMinions = self.Game.minions[subject.ID]
			x_0, y_0, z_0 = posMinionsTable[self.minionZones[subject.ID].y][len(ownMinions)][ownMinions.index(subject)]
		else: x_0, y_0, z_0 = self.heroZones[subject.ID].heroPos
		seq = Sequence(self.moveNodePath2_wrt_Wait(np_Subject, np_Target, duration=0.17, add2Queue=False),
						LerpPosInterval(np_Subject, duration=0.17, pos=(x_0, y_0, z_0+3)),
						LerpPosInterval(np_Subject, duration=0.15, pos=(x_0, y_0, z_0)),
					   )
		self.seqHolder[-1].append(seq)
		
	def attackAni_Cancel(self, subject):
		if subject.type == "Minion":
			minionZone, ownMinions = self.minionZones[subject.ID], self.Game.minions[subject.ID]
			if subject not in ownMinions: return
			pos_Orig = posMinionsTable[minionZone.y][len(ownMinions)][ownMinions.index(subject)]
		else: pos_Orig = self.heroZones[subject.ID].heroPos
		
		self.seqHolder[-1].append(LerpPosInterval(subject.btn.np, duration=0.15, pos=pos_Orig))
		
	def battlecryAni(self, card):
		if card.btn:
			texCard, seqNode = makeTexCard(self, "TexCards\\For%ss\\Battlecry.egg"%card.type, pos=(0, 0.5, 0.03), scale=6)
			texCard.reparentTo(card.btn.np)
			self.seqHolder[-1].append(Func(Sequence(Func(seqNode.play, 0, 32), Wait(32/24), Func(texCard.removeNode)).start))
			self.seqHolder[-1].append(Wait(20/24))
			
	def heroExplodeAni(self, entities):
		for entity in entities:
			if entity.btn:
				texCard, seqNode = makeTexCard(self, "TexCards\\ForHeroes\\Breaking.egg",
											   pos=(0, 0.2, 0.3), scale=5)
				texCard.reparentTo(entity.btn.np)
				headPieces = self.loader.loadModel("Models\\HeroModels\\HeadPieces.glb")
				headPieces.reparentTo(self.render)
				headPieces.setTexture(headPieces.findTextureStage('*'),
									  self.loader.loadTexture("Images\\HeroesandPowers\\%s.png"%type(entity).__name__), 1)
				x_0, y_0, z_0 = self.heroZones[entity.ID].heroPos
				headPieces.setPos(x_0, y_0, z_0)
				para = Parallel()
				for child in headPieces.getChildren():
					x, y, z = child.getPos()
					vec = np.array([x, y + 3 * (-1 if y_0 > 0 else 1), z_0+5])
					x_pos, y_pos, z_pos = np.array([x_0, y_0, -5]) + vec * 60 / np.linalg.norm(vec)
					para.append(LerpPosInterval(child, duration=0.8, pos=(x_pos, y_pos, z_pos)))
					
				self.seqHolder[-1].append(Sequence(Func(seqNode.play, 0, 17), Wait(17/24),
												   Func(texCard.removeNode), Func(entity.btn.np.removeNode),
												   Func(headPieces.setPos, x_0, y_0, z_0), para)
										  )
				
	def minionsDieAni(self, entities):
		para = Parallel()
		for entity in entities:
			if entity.btn:
				entity.btn.dimDown()
				nodePath = entity.btn.np
				dx, dy = 0.07 * np.random.rand(2)
				para.append(Sequence(Func(self.offsetNodePath, nodePath, duration=0.1, dx=dx, dy=dy),
							   		Func(self.offsetNodePath, nodePath, duration=0.1, dx=-2*dx, dy=-2*dy),
							   		Func(self.offsetNodePath, nodePath, duration=0.1, dx=dx, dy=dy),
							   		Wait(0.3))
							)
		self.seqHolder[-1].append(para)
		
	def deathrattleAni(self, entity):
		x, y, z = entity.btn.np.getPos()
		texCard, seqNode = makeTexCard(self, "TexCards\\Shared\\Deathrattle.egg", pos=(x, y+0.4, z+0.5), scale=3.3)
		self.seqHolder[-1].append(Sequence(Func(seqNode.play), Wait(1.2), Func(texCard.removeNode)))
		
	def weaponPlayedAni(self, card):
		ID = card.ID
		handZone = self.handZones[ID]
		x, y, z = self.heroZones[ID].weaponPos
		card.btn.isPlayed = True #The minion must be first set to isPlayed=True, so that the later statChangeAni can correctly respond
		sequence = Sequence(LerpPosHprScaleInterval(card.btn.np, duration=0.25, pos=(x, y+0.2, z+5), hpr=(0, 0, 0), scale=1),
							Func(card.btn.changeCard, card, True),
							Parallel(handZone.placeCards(False), LerpPosInterval(card.btn.np, duration=0.25, pos=(x, y, z)) )
							)
		self.seqHolder[-1].append(sequence)
		
	def secretTrigAni(self, card):
		btn, nodepath = card.btn, card.btn.np
		x, y, z = nodepath.getPos()
		sequence = self.seqHolder[-1]
		texCard = self.forGameTex["Secret%s" % card.Class]
		
		seq = Sequence(Func(print, "secret trigger", card),
					   Func(self.offsetNodePath_Wait, nodepath, duration=0.15, dx=0.1, add2Queue=False),
					   Func(self.offsetNodePath_Wait, nodepath, duration=0.15, dx=-0.2, add2Queue=False),
					   Func(self.offsetNodePath_Wait, nodepath, duration=0.15, dx=0.1, add2Queue=False),
					   Wait(0.3), Func(nodepath.detachNode),
					   LerpPosHprScaleInterval(texCard, duration=0.3, pos=(0, 1, 9), hpr=(0, -90, 0), scale=(25, 1, 25*600/800)),
					   Wait(0.8), LerpPosHprScaleInterval(texCard, duration=0.3, pos=(0, 0, 0), hpr=(0, -90, 0), scale=(1, 1, 1*600/800))
					   )
		sequence.append(seq)
		self.showOffBoardTrig(card)
		
	def need2beHidden(self, card): #options don't have ID, so they are always hidden if the PvP doesn't show enemy hand
		return not self.showEnemyHand and self.sock and (not hasattr(card, "ID") or card.ID != self.ID)
	
	def showOffBoardTrig(self, card, animationType="Curve", text2Show='', textY=-3, isSecret=False):
		if card:
			y = self.heroZones[card.ID].heroPos[1]
			#if card.btn and isinstance(card.btn, Btn_Card) and card.btn.np: nodePath, btn_Card = card.btn.np, card.btn
			nodePath, btn_Card = self.addCard(card, pos=(0, 0, 0), pickable=False,
											  isUnknownSecret=isSecret and self.need2beHidden(card))
			if text2Show:
				textNode = TextNode("Text Disp")
				textNode.setText(text2Show)
				textNode.setAlign(TextNode.ACenter)
				textNodePath = nodePath.attachNewNode(textNode)
				textNodePath.setPosHpr(0, textY, 1, 0, -90, 0)
			seq = self.seqHolder[-1] if self.seqHolder else Sequence()
			if animationType == "Curve":
				moPath = Mopath.Mopath()
				moPath.loadFile("Models\\BoardModels\\DisplayCurve_%s.egg"%("Lower" if y < 0 else "Upper"))
				seq.append(MopathInterval(moPath, nodePath, duration=0.3))
				seq.append(Wait(1))
			elif animationType == "Appear":
				pos = pos_OffBoardTrig_1 if y < 0 else pos_OffBoardTrig_2
				seq.append(Func(nodePath.setPos, pos[0], pos[1], 0))
				seq.append(LerpPosHprScaleInterval(nodePath, duration=0.4, pos=pos,
																  hpr=(0, 0, 0), startScale=0.3, scale=1))
				seq.append(Wait(0.7))
				seq.append(LerpScaleInterval(nodePath, duration=0.2, scale=0.2))
			else: #typically should be ''
				seq.append(Func(nodePath.setPos, pos_OffBoardTrig_1 if y < 0 else pos_OffBoardTrig_2))
				seq.append(Wait(1))
			seq.append(Func(nodePath.detachNode))
			if not self.seqHolder: seq.start()
			
	def eraseOffBoardTrig(self, ID):
		pass
	
	def addCard(self, card, pos, pickable, isUnknownSecret=False, onlyShowCardBack=False):
		if card.type == "Option":
			nodePath, btn_Card = genOption(self, card, pos=pos, onlyShowCardBack=onlyShowCardBack) #Option cards are always pickable
		else:
			if isUnknownSecret:
				btn_Card, nodePath = None, makeTexCard(self, "TexCards\\ForGame\\%sSecretCard.egg"%card.Class,
													   scale=8, aspectRatio=518/375, getSeqNode=False)[0]
			else:
				btn_Orig = card.btn if card.btn and card.btn.np else None
				nodePath, btn_Card = genCard(self, card, pos=pos, isPlayed=False, pickable=pickable,
											 onlyShowCardBack=onlyShowCardBack, makeNewRegardless=True)
				if btn_Orig: card.btn = btn_Orig #一张牌只允许存有其创建伊始指定的btn，不能在有一个btn的情况下再新加其他的btn
		return nodePath, btn_Card
	
	#Targeting/AOE animations
	def targetingEffectAni(self, subject, target, num, color="red"):
		return
		#btn_Subject, btn_Target = subject.btn, target.btn
		#if btn_Target:
		#	if btn_Subject:
		#		x, y, z = btn_Subject.getPos()
		#		pos_Subject = Point3(x, y - 0.2, z)
		#	elif subject.type == "Minion":
		#		pos_Subject = Point3(subject.x, subject.y - 0.2, subject.z)
		#	else:
		#		heroZone = self.heroZones[subject.ID]
		#		pos_Subject = Point3(heroZone.x, heroZone.y - 0.2, heroZone.z)
		#	pos_Target = btn_Target.getPos()
		#	delta_x, delta_z = pos_Target[0] - pos_Subject[0], pos_Target[2] - pos_Subject[2]
		#	distance = max(0.1, math.sqrt(delta_x ** 2 + delta_z ** 2))
		#	angle = (180 / math.pi) * math.acos(delta_z / distance)
		#	if delta_x < 0: angle = -angle
		#
		#	model = self.loader.loadModel("Models\\Fireball.glb")
		#	model.reparentTo(self.render)
		#	model.setPosHpr(pos_Subject, Point3(0, 0, angle))
		#	self.animate(Sequence(model.posInterval(duration=0.35, pos=pos_Target), Func(model.removeNode)), nextAnimWaits=True)
	
	def AOEAni(self, subject, targets, numbers, color="red"):
		pass
	
	#Miscellaneous animations
	def turnEndButtonAni_FlipRegardless(self):
		interval = self.btnTurnEnd.np.hprInterval(0.4, (0, 180 - self.btnTurnEnd.np.get_p(),0))
		self.seqHolder[-1].append(Func(self.btnTurnEnd.changeDisplay, False))
		self.seqHolder[-1].append(Func(interval.start))
		
	def turnEndButtonAni_Flip2RightPitch(self):
		p = 0 if self.ID == self.Game.turn else 180
		if self.btnTurnEnd.np.get_p() != p:
			interval = self.btnTurnEnd.np.hprInterval(0.4, (0, p, 0))
			self.seqHolder[-1].append(Func(interval.start))
	
	def turnStartAni(self):
		self.turnEndButtonAni_Flip2RightPitch()
		if self.ID != self.Game.turn: return
		tex_Parts = self.forGameTex["TurnStart_Particles"]
		tex_Banner = self.forGameTex["TurnStart_Banner"]
		seqNode_Parts = tex_Parts.find("+SequenceNode").node()
		seqNode_Banner = tex_Banner.find("+SequenceNode").node()
		seqNode_Parts.pose(0)
		seqNode_Banner.pose(0)
		sequence_Particles = Sequence(Func(tex_Parts.setPos, 0, 1, 5), Func(seqNode_Parts.play, 0, 27), Wait(0.9), Func(tex_Parts.setPos, 0, 0, 0)) # #27 returns to the begin
		sequence_Banner = Sequence(LerpPosHprScaleInterval(tex_Banner, duration=0.2, pos=(0, 1, 6), hpr=(0, -90, 0), startScale=1, scale=(23, 1, 23*332/768)),
								   Func(seqNode_Banner.play), Wait(1.2), LerpPosHprScaleInterval(tex_Banner, duration=0.2, pos=(0, 0, 0), hpr=(0, 0, 0), scale=(0.15, 0.15, 0.15))
									)
		self.seqHolder[-1].append(Parallel(sequence_Particles, sequence_Banner))
		
	def usePowerAni(self, card):
		btn, pos = card.btn, card.btn.np.getPos()
		sequence = Sequence(LerpPosHprInterval(btn.np, duration=0.3, pos=(pos[0], pos[1], pos[2]+2), hpr=Point3(0, 0, 90)),
							LerpPosHprInterval(btn.np, duration=0.3, pos=pos, hpr=Point3(0, 0, 180)))
		self.seqHolder[-1].append(Func(sequence.start))
		
	"""Mouse click setup"""
	def init_CollisionSetup(self):
		self.cTrav = CollisionTraverser()
		self.collHandler = CollisionHandlerQueue()
		
		self.raySolid = CollisionRay()
		cNode_Picker = CollisionNode("Picker Collider c_node")
		cNode_Picker.addSolid(self.raySolid)
		pickerNode = self.camera.attachNewNode(cNode_Picker)
		pickerNode.show()  #For now, show the pickerRay collision with the card models
		self.cTrav.addCollider(pickerNode, self.collHandler)
	
	def setRaySolidDirection(self):
		mpos = self.mouseWatcherNode.getMouse()
		#Reset the Collision Ray orientation, based on the mouse position
		self.raySolid.setDirection(25*mpos.getX(), 14*mpos.getY(), -50.5)
	
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
	
	def mouse3_Down(self):
		if self.mouseWatcherNode.hasMouse():
			self.setRaySolidDirection()
	
	def mouse3_Up(self):
		if self.mouseWatcherNode.hasMouse():
			self.setRaySolidDirection()
			if self.collHandler.getNumEntries() > 0:
				self.collHandler.sortEntries()
				cNode_Picked = self.collHandler.getEntry(0).getIntoNodePath()
				if self.UI == 0: cNode_Picked.getParent().getPythonTag("btn").rightClick()
				else: self.cancelSelection()
			else: self.cancelSelection()
	
	def restartLayer1Window(self):
		pass
	
	def clearDrawnCards(self):
		for child in self.render.getChildren():
			if not (child.name.startswith("Model2Keep")
					or child.name.startswith("Tex2Keep")
					or child.name.startswith("Text2Keep")):
				print("Remove", child.name, type(child))
				child.removeNode()
		for child in self.render.getChildren():
			if "2Keep" not in child.name:
				print("Kept under render (those that shouldn't):", child.name, type(child))
		self.setCamera_RaySolid()
		print(self.cam.getPos(), self.cam.getHpr(), self.camLens.getFov())
		self.arrow.stash()
		print("Done")
		
	def mainTaskLoop(self, task):
		#seqReady默认是True，只在游戏结算和准备动画过程中把seqReady设为False，保证尚未完成的seq不被误读
		#完成sequence的准备工作时会把seqReady再次设为True
		#只有把当前正在进行的seq走完之后才会读取下一个seq
		if self.seqReady and self.seqHolder and not (self.seq2Play and self.seq2Play.isPlaying()):
			self.seq2Play = self.seqHolder.pop(0)
			self.seq2Play.append(Func(self.decideCardColors))
			self.seq2Play.start()
		#tkinter window必须在主线程中运行，所以必须在ShowBase的main loop中被执行
		#self.msg_BacktoLayer1随机可以被设为非空值。但是一定要等到GUI中的所有seq都排空并且没有正在播放的seq了之后才会退回layer 1 window
		#实际上就是只有当GUI处于空闲状态时才会执行
		elif self.msg_BacktoLayer1 and self.seqReady and not self.seqHolder and not (self.seq2Play and self.seq2Play.isPlaying()):
			#print("\n\n----------\nCheck restart layer 1 window:", self.msg_BacktoLayer1, self.seqReady, self.seqHolder, self.seq2Play, self.seq2Play and self.seq2Play.isPlaying())
			self.seqReady, self.seq2Play = True, None
			self.msg_BacktoLayer1 = ""
			print("Going back to layer 1 window")
			self.restartLayer1Window()
			return Task.cont
		
		if self.mouseWatcherNode.hasMouse():
			self.setRaySolidDirection()
			if not self.arrow.isStashed():
				self.stopCardZoomIn()
				self.replotArrow()
			elif self.btnBeingDragged:
				self.stopCardZoomIn()
				self.dragCard()
			elif self.collHandler.getNumEntries() > 0:
				self.collHandler.sortEntries()
				if self.UI != -1: #Won't show zoom in during mulligan. But will show while waiting for enemy moves
					cNode_Picked = self.collHandler.getEntry(0).getIntoNodePath()
					btn_Picked = cNode_Picked.getParent().getPythonTag("btn")
					#The board also has a btn, but its btn.card is always None
					if btn_Picked.card and btn_Picked.card.type in ("Minion", "Spell", "Weapon", "Hero") \
							and btn_Picked.card.inHand and abs(btn_Picked.np.getY()) > 10: #需要指向的卡牌在位置物靠近手牌位置 才可以
						#如果目前没有正在放大的的卡牌或者正在放大的卡牌不是目前被指向的卡牌，则重新画一个
						if not self.np_CardZoomIn or self.np_CardZoomIn.getPythonTag("btn").card is not btn_Picked.card:
							self.drawCardZoomIn(btn_Picked)
			#If no collision node is picked and the card in display is in hand. Then cancel the card in display
			elif self.np_CardZoomIn and hasattr(self.np_CardZoomIn.getPythonTag("btn").card, "inHand") and self.np_CardZoomIn.getPythonTag("btn").card.inHand:
				self.stopCardZoomIn()
		return Task.cont
	
	def drawCardZoomIn(self, btn):
		card = btn.card
		#Stop showing for btns without card and hero and cards not allowed to show to enemy(hand and secret).
		if not card or (card.type == "Hero" and card.onBoard) \
				or (self.need2beHidden(card) and btn.onlyCardBackShown
						and (card.inHand or card.description.startswith("Secret:"))
					):
			if self.np_CardZoomIn: self.np_CardZoomIn.removeNode()
			self.np_CardZoomIn = None
		else:  #btn是一个牌的按键
			if hasattr(card, "inHand") and card.inHand:
				pos = (btn.np.getX(), ZoomInCard1_Y if self.ID == card.ID else ZoomInCard2_Y, ZoomInCard_Z)
			else: pos = (ZoomInCard_X, ZoomInCard1_Y if self.ID == card.ID else ZoomInCard2_Y, ZoomInCard_Z)
			
			if self.np_CardZoomIn: self.np_CardZoomIn.removeNode()
			if card.type == "Dormant" and card.minionInside: card = card.minionInside
			self.np_CardZoomIn = self.addCard(card, pos, pickable=False,
											  isUnknownSecret=card.description.startswith("Secret:") and self.need2beHidden(card))[0]
	
	def stopCardZoomIn(self):
		if self.np_CardZoomIn:
			self.np_CardZoomIn.removeNode()
			self.np_CardZoomIn = None
	
	def calcMousePos(self, z):
		vec_X, vec_Y, vec_Z = self.raySolid.getDirection()
		delta_Z = abs(CamPos_Z - z)
		x, y = vec_X * delta_Z / (-vec_Z), vec_Y * delta_Z / (-vec_Z)
		return x, y
	
	def dragCard(self):
		if self.btnBeingDragged.cNode:
			self.btnBeingDragged.cNode.removeNode() #The collision nodes are kept by the cards.
			self.btnBeingDragged.cNode = None
		
		#Decide the new position of the btn being dragged
		z = self.btnBeingDragged.np.getZ()
		x, y = self.calcMousePos(z)
		self.btnBeingDragged.np.setPosHpr(x, y, z, 0, 0, 0)
		#No need to change the x, y, z of the card being dragged(Will return anyway)
		card = self.btnBeingDragged.card
		if card.type == "Minion":
			minionZone = self.minionZones[card.ID]
			ownMinions = self.Game.minions[card.ID]
			boardSize = len(ownMinions)
			if not ownMinions:
				self.pos = -1
			elif len(ownMinions) < 7:
				ls_np_temp = [minion.btn.np for minion in ownMinions]
				posMinions_Orig = posMinionsTable[minionZone.y][boardSize]
				posMinions_Plus1 = posMinionsTable[minionZone.y][boardSize + 1]
				if -6 > y or y > 6:  #Minion away from the center board, the minions won't shift
					dict_MinionNp_Pos = {ls_np_temp[i]: posMinions_Orig[i] for i in range(boardSize)}
					self.pos = -1
				elif minionZone.y - 3.8 < y < minionZone.y + 3.8:
					#Recalculate the positions and rearrange the minion btns
					if x < ls_np_temp[0].get_x():  #If placed leftmost, all current minion shift right
						dict_MinionNp_Pos = {ls_np_temp[i]: posMinions_Plus1[i + 1] for i in range(boardSize)}
						self.pos = 0
					elif x < ls_np_temp[-1].get_x():
						ind = next((i + 1 for i, nodePath in enumerate(ls_np_temp[:-1]) if nodePath.get_x() < x < ls_np_temp[i + 1].get_x()), -1)
						if ind > -1:
							dict_MinionNp_Pos = {ls_np_temp[i]: posMinions_Plus1[i + (i >= ind)] for i in range(boardSize)}
							self.pos = ind
						else: return  #If failed to find
					else:  #All minions shift left
						dict_MinionNp_Pos = {ls_np_temp[i]: posMinions_Plus1[i] for i in range(boardSize)}
						self.pos = -1
				else:  #The minion is dragged to the opponent's board, all minions shift left
					dict_MinionNp_Pos = {ls_np_temp[i]: posMinions_Plus1[i] for i in range(boardSize)}
					self.pos = -1
				for nodePath, pos in dict_MinionNp_Pos.items(): nodePath.setPos(pos)
	
	def stopDraggingCard(self, returnDraggedCard=True):
		btn = self.btnBeingDragged
		if btn:
			print("Stop dragging card", btn)
			btn.cNode = btn.np.attachNewNode(btn.cNode_Backup)
			self.btnBeingDragged = None
			if not returnDraggedCard:
				return
			ID = btn.card.ID
			#Put the card back in the right pos_hpr in hand
			handZone = self.handZones[ID]
			ownHand = self.Game.Hand_Deck.hands[ID]
			i = ownHand.index(btn.card)
			pos = posHandsTable[handZone.y][len(ownHand)][i]
			hpr = hprHandsTable[handZone.y][len(ownHand)][i]
			btn.np.setPosHpr(pos, hpr)
			#btn.card.x, btn.card.y, btn.card.z = pos
			#Put the minions back to right positions on board
			ownMinions = self.Game.minions[ID]
			posMinions = posMinionsTable[self.minionZones[ID].y][len(ownMinions)]
			for i, minion in enumerate(ownMinions):
				minion.btn.np.setPos(posMinions[i])
				minion.x, minion.y, minion.z = posMinions[i]
			
	def replotArrow(self):
		#Decide the new orientation and scale of the arrow
		x_0, y_0, z_0 = self.subject.btn.np.getPos()
		x, y = self.calcMousePos(z_0)
		delta_x, delta_y = x - x_0, y - y_0
		distance = max(0.1, math.sqrt(delta_x ** 2 + delta_y ** 2))
		degree = -180 / math.pi * math.asin(delta_x / distance)
		if delta_y < 0: degree = 180-degree
		self.arrow.setScale(1, distance / 7.5, 1)
		self.arrow.setPosHpr(x_0, y_0, z_0, degree, 0, 0)
	
	"""Game resolution setup"""
	def cancelSelection(self, returnDraggedCard=True):
		self.stopDraggingCard(returnDraggedCard)
		self.arrow.stash()
		
		if 3 > self.UI > -1:  #只有非发现状态,且游戏不在结算过程中时下才能取消选择
			if self.subject:
				for option in self.subject.options:
					if option.btn: option.btn.np.removeNode()
			self.subject, self.target = None, None
			self.UI, self.pos, self.choice = 0, -1, -1
			self.selectedSubject = ""
			self.resetCardColors()
			
			curTurn = self.Game.turn
			for card in self.Game.Hand_Deck.hands[curTurn] + self.Game.minions[curTurn] \
						+ [self.Game.heroes[curTurn], self.Game.powers[curTurn]]:
				if card.btn: card.btn.setBoxColor(card.btn.decideColor())
			
			for card in self.Game.Hand_Deck.hands[1] + self.Game.Hand_Deck.hands[2] + [self.Game.powers[1]] + [self.Game.powers[2]]:
				if hasattr(card, "targets"): card.targets = []
	
	def resolveMove(self, entity, button, selectedSubject):
		print("Resolve move", entity, button, selectedSubject)
		game = self.Game
		if self.UI < 0: pass
		elif self.UI == 0:
			self.resetCardColors()
			if selectedSubject == "Board":  #Weapon won't be resolved by this functioin. It automatically cancels selection
				print("Board is not a valid subject.")
				self.cancelSelection()
			elif selectedSubject == "TurnEnds":
				self.cancelSelection()
				self.subject, self.target = None, None
				print("Resolve switch turn from GUI")
				self.gamePlayQueue.append(lambda : game.endTurn())
				print("now the game play queue is", self.gamePlayQueue)
			elif entity.ID != game.turn or (1 < self.ID != entity.ID):
				print("You can only select your own characters as subject.")
				self.cancelSelection()
			else:  #选择的是我方手牌、我方英雄、我方英雄技能、我方场上随从，
				self.subject, self.target = entity, None
				self.selectedSubject = selectedSubject
				self.UI, self.choice = 2, 0  #选择了主体目标，则准备进入选择打出位置或目标界面。抉择法术可能会将界面导入抉择界面。
				button.selected = 1 - button.selected
				self.arrow.stash()
				if selectedSubject.endswith("inHand"):  #Choose card in hand as subject
					if not game.Manas.affordable(entity, canbeTraded="~Tradeable" in entity.index):  #No enough mana to use card
						self.cancelSelection()
					else:  #除了法力值不足，然后是指向性法术没有合适目标和随从没有位置使用
						typewhenPlayed = self.subject.getTypewhenPlayed()
						if entity.effects["Can't be Played"] > 0:
							self.cancelSelection()
						elif typewhenPlayed == "Spell" and not entity.available():
							#法术没有可选目标，或者是不可用的非指向性法术
							self.cancelSelection()
						elif game.space(entity.ID) < 1 and (typewhenPlayed == "Minion" or typewhenPlayed == "Amulet"):  #如果场上没有空位，且目标是护符或者无法触发激奏的随从的话，则不能打出牌
							#随从没有剩余位置
							self.cancelSelection()
						else:  #Playable cards
							if entity.need2Choose():
								print("Choose One card clicked")
								#所选的手牌不是影之诗卡牌，且我方有抉择全选的光环
								if not entity.index.startswith("SV_"):
									if game.effects[entity.ID]["Choose Both"] > 0:
										self.choice = -1  #跳过抉择，直接进入UI=1界面。
										if entity.needTarget(-1):
											self.highlightTargets(entity.findTargets("", self.choice)[0])
									else:  #Will conduct choose one
										self.UI = 1
										leftMost_X = -5 * (len(entity.options) - 1) / 2
										for i, option in enumerate(entity.options):
											self.addCard(option, pos=(leftMost_X + i * 5, 1.5, 10), pickable=True)
								elif entity.index.startswith("SV_"):
									self.UI = 1  #进入抉择界面，退出抉择界面的时候已经self.choice已经选好。
									return
							else:  #No need to choose one
								#如果选中的手牌是一个需要选择目标的SV法术
								if entity.index.startswith("SV_") and typewhenPlayed == "Spell" and entity.needTarget():
									self.choice = -1  #影之诗因为有抉择不发动的情况，所以不能默认choice为0（炉石中的非抉择卡牌都默认choice=0），所以需要把choice默认为-1
									#需要目标选择的影之诗卡牌开始进入多个目标的选择阶段
									game.Discover.startSelect(entity, entity.findTargets("")[0])
									return
								#选中的手牌是需要目标的炉石卡
								#可以是任何类型的炉石卡
								elif entity.needTarget():
									self.highlightTargets(entity.findTargets("", self.choice)[0])
									if typewhenPlayed != "Minion":
										self.arrow.unstash()
										self.arrow.setPos(button.np.getPos())
								self.btnBeingDragged = button
								
				#不需目标的英雄技能当即使用。需要目标的进入目标选择界面。暂时不用考虑技能的抉择
				elif selectedSubject == "Power":
					print("Check if can use power", entity)
					if entity.name == "Evolve":
						self.selectedSubject = "Power"
						game.Discover.startSelect(entity, entity.findTargets("")[0])
					#英雄技能会自己判定是否可以使用。
					elif entity.needTarget():  #selectedSubject之前是"Hero Power 1"或者"Hero Power 2"
						print("Power needs target")
						self.selectedSubject = "Power"
						self.highlightTargets(entity.findTargets("", self.choice)[0])
						self.arrow.unstash()
						self.arrow.setPos(button.np.getPos())
					else:
						print("Request to use Hero Power {}".format(self.subject.name))
						subject = self.subject
						self.cancelSelection()
						self.subject, self.target = subject, None
						self.gamePlayQueue.append(lambda : subject.use(None))
				#不能攻击的随从不能被选择。
				elif selectedSubject.endswith("onBoard"):
					if not entity.canAttack():
						self.cancelSelection()
					else:
						self.highlightTargets(entity.findBattleTargets()[0])
						self.arrow.unstash()
						self.arrow.setPos(button.np.getPos())
		elif self.UI == 1:  #在抉择界面下点击了抉择选项会进入此结算流程
			self.arrow.stash()
			if selectedSubject == "ChooseOneOption" and entity.available():
				if self.subject.index.startswith("SV_"):  #影之诗的卡牌的抉择选项确定之后进入与炉石卡不同的UI
					index = self.subject.options.index(entity)
					self.UI, self.choice = 2, index
					for option in self.subject.options:
						option.btn.np.removeNode()
					if self.subject.needTarget(self.choice):
						self.highlightTargets(self.subject.findTargets("", self.choice)[0])
				else:  #炉石卡的抉择选项确定完毕
					#The first option is indexed as 0.
					index = self.subject.options.index(entity)
					self.UI, self.choice = 2, index
					for option in self.subject.options:
						option.btn.np.removeNode()
					if self.subject.needTarget(self.choice) and self.subject.type == "Spell":
						self.highlightTargets(self.subject.findTargets("", self.choice)[0])
						self.arrow.unstash()
						self.arrow.setPos(button.np.getPos())
					else:
						self.btnBeingDragged = self.subject.btn
			elif selectedSubject == "TurnEnds":
				self.cancelSelection()
				self.subject, self.target = None, None
				self.gamePlayQueue.append(lambda : game.endTurn())
			else:
				print("You must click an available option to continue.")
		#炉石的目标选择在此处进行，可以对场上随从，英雄以及牌库（限于可交易卡牌）进行选择
		elif self.UI == 2:  #影之诗的目标选择是不会进入这个阶段的，直接进入UI == 3，并在那里完成所有的目标选择
			self.target = entity
			print("Selected target: {}".format(entity))
			#No matter what the selections are, pressing EndTurn button ends the turn.
			#选择的主体是场上的随从或者英雄。之前的主体在UI=0的界面中已经确定一定是友方角色。
			if selectedSubject == "TurnEnds":
				self.cancelSelection()
				self.subject, self.target = None, None
				self.gamePlayQueue.append(lambda : game.endTurn())
			elif selectedSubject.endswith("inHand"):  #影之诗的目标选择不会在这个阶段进行
				self.cancelSelection()
			elif self.selectedSubject.endswith("onBoard"):  #已经选择了一个场上的角色，随从或英雄
				if "Hero" not in selectedSubject and selectedSubject != "MiniononBoard":
					print("Not attackable chars for minion attack, e.g. Dormant")
				else:
					print("Requesting battle: {} attacks {}".format(self.subject.name, entity))
					subject, target = self.subject, self.target
					self.cancelSelection()
					self.subject, self.target = subject, target
					self.gamePlayQueue.append(lambda : game.battle(subject, target))
			elif "inHand" in self.selectedSubject:
				if selectedSubject == "Deck":  #在选择牌库的时候只有是手中的可交易卡牌并且当前费用大于0时会有反应
					if "~Tradeable" in self.subject.index and game.Manas.affordable(self.subject, canbeTraded=True):
						subject, target = self.subject, self.target
						self.cancelSelection()
						self.subject = subject
						print("Resolve move Trade card", self.subject)
						self.gamePlayQueue.append(lambda: game.playCard_4Trade(subject))
				elif not game.Manas.affordable(self.subject, canbeTraded=False): #手牌中的牌希望以正常方式找出时,只要费用不足以支付，就放弃之前的所有选择
					self.cancelSelection()
					return
				#手中选中的随从在这里结算打出位置，如果不需要目标，则直接打出。
				#假设有时候选择随从的打出位置时会有鼠标刚好划过一个随从的情况
				if self.selectedSubject == "MinioninHand" or self.selectedSubject == "AmuletinHand":  #选中场上的友方随从，我休眠物和护符时会把随从打出在其左侧
					if selectedSubject == "Board" or (entity.ID == self.subject.ID and (selectedSubject.endswith("onBoard") and not selectedSubject.startswith("Hero"))):
						self.selectedSubject = "MinionPosDecided"  #将主体记录为标记了打出位置的手中随从。
						#抉择随从如有全选光环，且所有选项不需目标，则直接打出。 连击随从的needTarget()由连击条件决定。
						#print("Minion {} in hand needs target: {}".format(self.subject.name, self.subject.needTarget(self.choice)))
						if not (self.subject.needTarget(self.choice) and self.subject.targetExists(self.choice)):
							#print("Requesting to play minion {} without target. The choice is {}".format(self.subject.name, self.choice))
							subject, position, choice = self.subject, self.pos, self.choice
							self.cancelSelection(returnDraggedCard=not self.Game.check_playMinion(subject, None, position, choice))
							self.subject, self.target = subject, None
							self.gamePlayQueue.append(lambda : game.playMinion(subject, None, position, choice))
						else:  #随从打出后需要目标
							#print("The minion requires target to play. needTarget() returns {}".format(self.subject.needTarget(self.choice)))
							#需要区分SV和炉石随从的目标选择。
							subject = self.subject
							#如果是影之诗随从，则需要进入多个目标选择的UI==3阶段，而炉石随从则仍留在该阶段之路等待单目标选择的完成
							if subject.index.startswith("SV_"):  #能到这个阶段的都是有目标选择的随从
								self.choice = 0
								game.Discover.startSelect(subject, subject.findTargets("")[0])
							btn_PlayedMinion = self.subject.btn
							self.arrow.unstash()
							self.arrow.setPos(btn_PlayedMinion.np.getPos())
							#选中的法术已经确定抉择选项（如果有），下面决定目标选择。
				#选择手牌中的法术或武器的打出目标
				elif self.selectedSubject in ("SpellinHand", "WeaponinHand"):
					playFunc = {"Spell": game.playSpell, "Weapon": game.playWeapon, "Hero": game.playHero}[self.subject.type]
					checkFunc = {"Spell": game.check_playSpell, "Weapon": game.check_playWeapon, "Hero": game.check_playHero}[self.subject.type]
					if not self.subject.needTarget(self.choice):  #Non-targeting spells can only be cast by clicking the board
						if "Board" in selectedSubject:  #打出非指向性法术时，可以把卡牌拖动到随从，英雄或者桌面上
							print("Requesting to play {} {} without target. The choice is {}".format(self.subject.type, self.subject.name, self.choice))
							subject, target, choice = self.subject, None, self.choice
							self.cancelSelection(returnDraggedCard=not checkFunc(subject, target, choice))
							self.subject, self.target = subject, target
							self.gamePlayQueue.append(lambda: playFunc(subject, target, choice))
					else:  #法术或者法术抉择选项需要指定目标。
						if selectedSubject == "MiniononBoard" or selectedSubject == "HeroonBoard":
							print("Requesting to play {} {} with target {}. The choice is {}".format(self.subject.type, self.subject.name, entity, self.choice))
							subject, target, choice = self.subject, entity, self.choice
							self.cancelSelection(returnDraggedCard=not checkFunc(subject, target, choice))
							self.subject, self.target = subject, target
							self.gamePlayQueue.append(lambda: playFunc(subject, target, choice))
						else:
							print("Targeting {} must be cast on Hero or Minion on board.".format(self.subject.type))
			#随从的打出位置和抉择选项已经在上一步选择，这里处理目标选择。
			elif self.selectedSubject == "MinionPosDecided":
				if selectedSubject == "MiniononBoard" or selectedSubject == "HeroonBoard":
					print("Requesting to play minion {}, targeting {} with choice: {}".format(self.subject.name, entity.name, self.choice))
					subject, position, choice = self.subject, self.pos, self.choice
					self.cancelSelection(returnDraggedCard=not self.Game.check_playMinion(subject, entity, position, choice))
					self.subject, self.target = subject, entity
					self.gamePlayQueue.append(lambda : game.playMinion(subject, entity, position, choice))
				else:
					print("Not a valid selection. All selections canceled.")
			#Select the target for a Hero Power.
			#在此选择的一定是指向性的英雄技能。
			elif self.selectedSubject == "Power":  #如果需要指向的英雄技能对None使用，HeroPower的合法性检测会阻止使用。
				if selectedSubject == "MiniononBoard" or selectedSubject == "HeroonBoard":
					print("Requesting to use Hero Power {} on {}".format(self.subject.name, entity.name))
					subject = self.subject
					self.cancelSelection()
					self.subject, self.target = subject, entity
					self.gamePlayQueue.append(lambda : subject.use(entity))
				else:
					print("Targeting hero power must be used with a target.")
		else:  #self.UI == 3
			if selectedSubject == "DiscoverOption":
				self.UI = 0
				self.discover = entity
			elif selectedSubject == "SelectObj":
				# print("Selecting obj for SV card")
				self.choice += 1
				self.subject.targets.append(entity)
				try: self.target.append(entity)
				except: self.target = [entity]
				if self.subject.needTarget():
					game.Discover.startSelect(self.subject, self.subject.findTargets("", self.choice)[0])
				else:  #如果目标选择完毕了，则不用再选择，直接开始打出结算
					self.UI = 0
					subject, target, position, choice = self.subject, self.subject.targets, self.pos, -1
					print("Requesting to play Shadowverse spell {} with targets {}".format(subject.name, target))
					self.cancelSelection()
					func = {"Minion": lambda: game.playMinion(subject, target, position, choice),
							"Spell": lambda: game.playSpell(subject, target, choice),
							"Amulet": lambda: game.playAmulet(subject, target, choice),
							"Power": lambda: subject.use(target, choice),
							}[subject.type]
					func()
			elif selectedSubject == "Fusion":
				self.UI = 0
				game.Discover.initiator.fusionDecided(entity)
			else:
				print("You MUST click a correct object to continue.")
	
	#Can only be invoked by the game thread
	def waitforDiscover(self):
		self.UI, self.discover = 3, None
		para = Parallel()
		btns = []
		leftMost_x = -5 * (len(self.Game.options) -1) / 2
		for i, card in enumerate(self.Game.options):
			#self.addCard creates a btn for the card, but the card's original button(if any) is kept.
			#There will be two btns referencing the same card
			nodePath_New, btn_New = self.addCard(card, Point3(0, 0, 0), pickable=True)
			btns.append(btn_New)
			para.append(LerpPosHprScaleInterval(nodePath_New, duration=0.2, pos=(leftMost_x + 5 * i, 1.5, 13), hpr=(0, 0, 0), startScale=0.2, scale=1))
		self.seqHolder[-1].append(para)
		btn_HideOptions = DirectButton(text=("Hide", "Hide", "Hide", "Continue"), scale=.1,
									   pos=(2, 0, 2), command=self.toggleDiscoverHide)
		btn_HideOptions["extraArgs"] = [btn_HideOptions]
		self.btns2Remove.append(btn_HideOptions)
		self.seqHolder[-1].append(Func(btn_HideOptions.setPos, -0.5, 0, -0.5))
		self.seqReady = True
		while self.discover is None:
			time.sleep(0.1)
		#Restart the sequence
		self.seqReady = False
		self.seqHolder.append(Sequence())
		for btn in btns: btn.np.detachNode()
		for btn in self.btns2Remove: btn.destroy()
		return self.discover #No need to reset the self.discover. Need to reset each time anyways
		
	#To be invoked for animation of opponent's discover decision (if PvP) or own random decisions
	def discoverDecideAni(self, isRandom, numOption, indexOption, options):
		seq = self.seqHolder[-1]
		para = Parallel()
		btn_Chosen, btns = None, []
		leftMost_x = -5 * (numOption - 1) / 2
		if isinstance(options, (list, tuple, np.ndarray)):
			for i, card in enumerate(options):
				nodePath, btn = self.addCard(card, Point3(0, 0, 0), pickable=True, onlyShowCardBack=self.need2beHidden(card))
				btns.append(btn)
				if i == indexOption: btn_Chosen = btn
				para.append(LerpPosHprScaleInterval(nodePath, duration=0.2, pos=(leftMost_x + 5 * i, 1.5, 13), hpr=(0, 0, 0), startScale=0.2, scale=1))
		else:
			selectedCard = options
			for i in range(numOption):
				if i == indexOption:
					nodePath, btn_Chosen = self.addCard(selectedCard, Point3(0, 0, 0), pickable=True, onlyShowCardBack=self.need2beHidden(selectedCard))
					btns.append(btn_Chosen)
				else:
					nodePath, btn = self.addCard(TheCoin(self.Game, selectedCard.ID), Point3(0, 0, 0), pickable=False, onlyShowCardBack=True)
					btns.append(btn)
				para.append(LerpPosHprScaleInterval(nodePath, duration=0.2, pos=(leftMost_x + 5 * i, 1.5, 13), hpr=(0, 0, 0), startScale=0.2, scale=1))
		seq.append(para)
		seq.append(Wait(0.5) if isRandom else Wait(1.2))
		sequence = Sequence(LerpScaleInterval(btn_Chosen.np, duration=0.2, scale=1.13),
					   		LerpScaleInterval(btn_Chosen.np, duration=0.2, scale=1.0))
		for btn in btns:
			sequence.append(Func(print, "Discover decision ani: Detaching btn", btn.np))
			sequence.append(Func(btn.np.detachNode))
		seq.append(sequence)
		
	def toggleDiscoverHide(self, btn):
		print("Toggle hide button", btn["text"])
		if btn["text"] == ("Hide", "Hide", "Hide", "Continue"):
			btn["text"] = ("Show", "Show", "Show", "Continue")
			for card in self.Game.options: card.btn.np.stash()
		else: #btn["text"] == ("Show", "Show", "Show", "Continue")
			btn["text"] = ("Hide", "Hide", "Hide", "Continue")
			for card in self.Game.options: card.btn.np.unstash()
			
	def checkCardsDisplays(self, side=0, checkHand=False, checkBoard=False):
		sides = (side, ) if side else (1, 2)
		if checkHand:
			print("   Check cards in hands:")
			for ID in sides:
				for card in self.Game.Hand_Deck.hands[ID]:
					if not card.btn.np.getParent():
						print("      ", ID, card.name, card.btn.np, card.btn.np.getParent(), card.btn.np.getPos())
		if checkBoard:
			print("   Check cards on Board:")
			for ID in sides:
				for card in self.Game.minions[ID]:
					if not card.btn.np.getParent():
						print("      ", ID, card.name, card.btn.np, card.btn.np.getParent(), card.btn.np.getPos())
	
	def sendOwnMovethruServer(self, endingTurn=True):
		pass
		