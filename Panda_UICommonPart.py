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

configVars = """
win-size 1260 700
window-title Single Player Hearthstone Simulator
clock-mode limited
clock-frame-rate 45
text-use-harfbuzz true
"""

loadPrcFileData('', configVars)


translateTable = {"Loading. Please wait":"正在加载模型，请等待",
					"Hero 1 class": "选择玩家1的职业",
					"Hero 2 class": "选择玩家2的职业",
					"Enter Deck 1 code": "输入玩家1套牌代码",
					"Enter Deck 2 code": "输入玩家2的套牌代码",
					"Deck 1 incorrect": "玩家1的套牌代码有误",
					"Deck 2 incorrect": "玩家2的套牌代码有误",
					"Deck 1&2 incorrect": "玩家1与玩家2的套牌代码均有误",
					"Finished Loading. Start!": "加载完成，可以开始",
					
					"Server IP Address": "服务器IP地址",
					"Query Port": "接入端口",
					"Table ID to join": "想要加入的牌桌ID",
				  	"Hero class": "选择你的职业",
				  	"Enter Deck code": "输入你的套牌代码",
					"Resume interrupted game": "返回中断的游戏",
				  	
				  	"Deck incorrect": "你的套牌代码不正确，请检查后重试",
				  	"Can't ping the address ": "无法ping通给出的服务器IP地址",
				  	"Can't connect to the server's query port": "无法连接到给出的服务器接入端口",
				  	"No tables left. Please wait for openings": "没有空桌子了，请等待空出",
				  	"This table ID is already taken": "本桌子目前已有两个玩家",
				  
					"Opponent disconnected. Closing": "对方断开了连接。强制关闭",
					"Wait for Opponent to Reconnect: ": "等待对方重新连接：",
					"Opponent failed to reconnect.\nClosing in 2 seconds": "对方未能重新连接\n2秒后退出",
					"Receiving Game Copies from Opponent: ": "正在接收对方保存的游戏当前进度：",
				  
				  }

def txt(text, CHN):
	try: return translateTable[text]
	except: return text
	
def pickleObj2Bytes(obj):
	return pickle.dumps(obj, 0)

def unpickleBytes2Obj(s):
	return pickle.loads(s)

CamPos_Y = -51.5

class Panda_UICommon(ShowBase):
	def __init__(self):
		ShowBase.__init__(self)
		#simplepbr.init(max_lights=4)
		self.disableMouse()
		self.WAIT, self.FUNC = Wait, Func
		self.SEQUENCE, self.PARALLEL = Sequence, Parallel
		self.seqHolder, self.seq2Play, self.seqReady = [], None, False
		self.ID = 0
		self.boardID = ''
		self.board, self.btnTurnEnd = None, None
		self.mulliganStatus = {1: [0, 0, 0], 2: [0, 0, 0, 0]}
		#Attributes of the GUI
		self.selectedSubject = ""
		self.subject, self.target = None, None
		self.pos = self.choice = self.UI = -1  #起手调换为-1
		self.discover = None
		self.btnBeingDragged, self.arrow = None, None
		self.np_CardZoomIn = None
		self.intervalQueue = []
		self.intervalRunning = 0
		self.gamePlayQueue = []
		self.gamePlayThread = None
		self.modelTemplates = {}
		self.font = None
	
		self.minionZones, self.heroZones, self.handZones, self.deckZones = {}, {}, {}, {}
		self.textures, self.manaModels = {}, {}
		self.posMulligans = None
		#Flag whether the game is still loading models for the cards
		self.loading = "Loading. Please Wait"
		
		self.cTrav = self.collHandler = self.raySolid = None
		self.accept("mouse1", self.mouse1_Down)
		self.accept("mouse1-up", self.mouse1_Up)
		self.accept("mouse3", self.mouse3_Down)
		self.accept("mouse3-up", self.mouse3_Up)
		
		self.gamePlayThread = threading.Thread(target=self.keepExecutingGamePlays, daemon=True)
		self.gamePlayThread.name = "GameThread"
		self.gamePlayThread.start()
		self.init_CollisionSetup()
		
		"""Prepare models that will be used later"""
		self.Game = Game(self)
		self.Game.mode = 0
		self.Game.initialize()
		
		self.sock = None
		self.waiting4Server, self.timer = False, 60
	
	def prepareTexturesandModels(self, layer1Window=None):
		if layer1Window: layer1Window.lbl_LoadingProgress["text"] = "基础贴图加载中..."
		else: print("基础贴图加载中...")
		self.font = self.loader.loadFont("Models\\OpenSans-Bold.ttf")
		self.textures = {"cardBack": self.loader.loadTexture("Models\\CardBack.png"),
						 "Deathrattle": self.loader.loadTexture("Models\\Deathrattle.png"),
						 "Lifesteal": self.loader.loadTexture("Models\\Lifesteal.png"),
						 "Poisonous": self.loader.loadTexture("Models\\Poisonous.png"),
						 "Trigger": self.loader.loadTexture("Models\\Trigger.png"),
						 }
		for cardType in ("Minion", "Spell", "Weapon", "Hero", "Power"):
			self.textures["stats_" + cardType] = self.loader.loadTexture("Models\\%sModels\\Stats.png" % cardType)
		for Class in ("Hunter", "Mage", "Paladin", "Rogue"):
			self.textures["Secret_" + Class] = self.loader.loadTexture("Models\\HeroModels\\Secret_%s.png" % Class)
		for expansion in ("BASIC", "BLACK_TEMPLE", "CORE", "DARKMOON_FAIRE", "EXPERT1", "SCHOLOMANCE", "THE_BARRENS"):
			self.textures["minion_" + expansion] = self.loader.loadTexture("Models\\MinionModels\\%s.png" % expansion)
			self.textures["spell_" + expansion] = self.loader.loadTexture("Models\\SpellModels\\%s.png" % expansion)
		self.textures["power_vanilla"] = self.loader.loadTexture("Models\\PowerModels\\Vanilla.png")
		for Class in ("Demon Hunter,Hunter", "Demon Hunter", "Druid", "Hunter", "Mage", "Paladin",
					  "Priest", "Rogue", "Shaman", "Warlock", "Warrior", "Neutral"):
			self.textures["weapon_" + Class] = self.loader.loadTexture("Models\\WeaponModels\\WeaponCards\\%s.png" % Class)
		
		if layer1Window: layer1Window.lbl_LoadingProgress["text"] = "基础特效加载中..."
		else: print("基础特效加载中...")
		t1 = datetime.now()
		for iconName, scale, pos in zip(("Trigger", "Deathrattle", "Lifesteal", "Poisonous"),
										(1.1, 3, 1.2, 1.3),
										((0, -0.08, 0), (0, -0.1, 0), (0, -0.08, -0.02), (0, -0.08, -0.05))):
			np_Icon = self.loader.loadModel("Models\\%s.glb" % iconName)
			texCard = self.loader.loadModel("TexCards\\Shared\\%s.egg" % iconName)
			texCard.reparentTo(np_Icon)
			np_Icon.setTexture(np_Icon.findTextureStage('0'), self.textures[iconName], 1)
			texCard.setPos(pos)
			texCard.setScale(scale)
			self.modelTemplates[iconName] = np_Icon
			np_Icon.name, texCard.name = iconName + "_Icon", "TexCard"
			np_Icon.setTransparency(True)
			texCard.find("+SequenceNode").node().pose(0)
			if iconName == "Trigger":
				textNode = TextNode("Trig Counter")
				textNode.setAlign(TextNode.ACenter)
				textNodePath = np_Icon.attachNewNode(textNode)
				textNodePath.setScale(0.6)
				textNodePath.setPos(0, -0.1, -0.55)
			np_Icon.setColor(transparent)
			#np_Icon is now: Trigger_Icon
								#Trigger|TexCard|Trig Counter
		#Get the templates for the cards, they will load the trig icons and status tex cards
		if layer1Window: layer1Window.lbl_LoadingProgress["text"] = "随从模型加载中..."
		else: print("随从模型加载中...")
		self.modelTemplates["Minion"] = loadCard(self, SilverHandRecruit(self.Game, 1))
		if layer1Window: layer1Window.lbl_LoadingProgress["text"] = "法术模型加载中..."
		else: print("法术模型加载中...")
		self.modelTemplates["Spell"] = loadCard(self, TheCoin(self.Game, 1))
		if layer1Window: layer1Window.lbl_LoadingProgress["text"] = "武器模型加载中..."
		else: print("武器模型加载中...")
		self.modelTemplates["Weapon"] = loadCard(self, FieryWarAxe_Core(self.Game, 1))
		if layer1Window: layer1Window.lbl_LoadingProgress["text"] = "英雄模型加载中..."
		else: print("英雄模型加载中...")
		self.modelTemplates["Hero"] = loadCard(self, Rexxar(self.Game, 1))
		if layer1Window: layer1Window.lbl_LoadingProgress["text"] = "英雄技能模型加载中..."
		else: print("英雄技能模型加载中...")
		self.modelTemplates["Power"] = loadCard(self, SteadyShot(self.Game, 1))
		if layer1Window: layer1Window.lbl_LoadingProgress["text"] = "休眠物模型加载中..."
		else: print("休眠物模型加载中...")
		self.modelTemplates["Dormant"] =loadCard(self, BurningBladePortal(self.Game, 1))
		if layer1Window: layer1Window.lbl_LoadingProgress["text"] = "抉择选项模型加载中..."
		else: print("抉择选项模型加载中...")
		self.modelTemplates["Option"] = loadCard(self, RampantGrowth_Option(None))
		
		t2 = datetime.now()
		print("Time needed to load tex cards", datetime.timestamp(t2) - datetime.timestamp(t1))
	
	def loadBackground(self):
		plane = self.loader.loadModel("Models\\BoardModels\\Background.glb")
		plane.setTexture(plane.findTextureStage('*'),
						 self.loader.loadTexture("Models\\BoardModels\\%s.png" % self.boardID), 1)
		plane.reparentTo(self.render)
		plane.setPos(0, -1, 0)
		collNode_Board = CollisionNode("Board_c_node")
		collNode_Board.addSolid(CollisionBox(Point3(0, 0.2, 0.4), 15, 0.2, 7.5))
		plane.attachNewNode(collNode_Board)  #.show()
		plane.setPythonTag("btn", Btn_Board(self, plane))
		
		#Load the turn end button
		turnEnd = self.loader.loadModel("Models\\BoardModels\\TurnEndButton.glb")
		turnEnd.reparentTo(self.render)
		turnEnd.setPos(TurnEndBtn_Pos)
		turnEnd.setTexture(turnEnd.findTextureStage('*'),
						   self.loader.loadTexture("Models\\BoardModels\\TurnEndBtn.png"), 1)
		collNode_TurnEndButton = CollisionNode("TurnEndButton_c_node")
		collNode_TurnEndButton.addSolid(CollisionBox(Point3(0, 0, 0), 2, 0.2, 1))
		turnEnd.attachNewNode(collNode_TurnEndButton)  #.show()
		self.btnTurnEnd = Btn_TurnEnd(self, turnEnd)
		turnEnd.setPythonTag("btn", self.btnTurnEnd)
	
		self.arrow = self.loader.loadModel("Models\\Arrow.glb")
		self.arrow.setTexture(self.arrow.findTextureStage('0'), self.loader.loadTexture("Models\\Arrow.png"), 1)
		self.arrow.reparentTo(self.render)
		self.arrow.stash()
		
	def initMulliganDisplay(self):
		pass
	
	def initGameDisplay(self):
		self.loadBackground()
		self.camLens.setFov(51.1, 27.5)
		self.cam.setPos(0, CamPos_Y, 0)
		self.raySolid.setOrigin(0, CamPos_Y, 0)
		for name in ("Mana", "EmptyMana", "LockedMana", "OverloadedMana"):
			model = self.loader.loadModel("Models\\BoardModels\\Mana.glb")
			model.reparentTo(self.render)
			model.setTexture(model.findTextureStage('*'),
							 self.loader.loadTexture("Models\\BoardModels\\%s.png"%name), 1)
			self.manaModels[name] = [model]
			for i in range(9):
				self.manaModels[name].append(model.copyTo(self.render))
		
		for ID in range(1, 3):
			self.deckZones[ID].draw(len(self.Game.Hand_Deck.decks[ID]))
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
	
	def resetCardColors(self):
		game = self.Game
		for ID in range(1, 3):
			for card in game.minions[ID] + game.Hand_Deck.hands[ID] + game.Secrets.secrets[ID] \
						+ [game.heroes[ID]]:
				card.btn.np.setColor(white)
		
	def highlightTargets(self, legalTargets):
		game = self.Game
		for ID in range(1, 3):
			for card in game.minions[ID] + game.Hand_Deck.hands[ID] + game.Secrets.secrets[ID] \
				+ [game.heroes[ID]]:
				if card not in legalTargets: card.btn.dimDown()
	
	"""Animation details"""
	#Card/Hand animation
	def putaNewCardinHandAni(self, card):
		handZone = self.handZones[card.ID]
		handZone.addaHand(card, (0, handZone.y, 0))
		handZone.draw(afterAllFinished=False)
	
	def cardReplacedinHand_Refresh(self, card):
		handZone = self.handZones[card.ID]
		ownHand = self.Game.Hand_Deck.hands[card.ID]
		#此时卡牌已经进入了玩家的手牌
		posHand = posHandsTable[handZone.z][len(ownHand)]
		hprHand = hprHandsTable[handZone.z][len(ownHand)]
		i = ownHand.index(card)
		handBtn = handZone.addaHand(card, posHand[i])
		para = Parallel(Sequence(Wait(0.2), handBtn.genLerpInterval(pos=posHand[i], hpr=hprHand[i], duration=0.2)))
		for i, hand in enumerate(ownHand):
			if hand is not card:
				para.append(hand.btn.genLerpInterval(pos=posHand[i], hpr=hprHand[i], duration=0.2))
		self.seqHolder[-1].append(para)
	
	#因为可以结算的时候一般都是手牌已经发生了变化，所以只能用序号来标记每个btn了
	#linger is for when you would like to see the card longer before it vanishes
	def cardsLeaveHandAni(self, cards, ID=0, enemyCanSee=True, linger=False):
		handZone, para, btns2Destroy = self.handZones[ID], Parallel(), [card.btn for card in cards]
		#此时需要离开手牌的牌已经从Game.Hand_Deck.hands里面移除,手牌列表中剩余的就是真实存在还在手牌中的
		for btn in btns2Destroy:
			para.append(Sequence(btn.genLerpInterval(pos=Point3(btn.np.get_x(), btn.np.get_y(),
																DiscardedCard1_Y if self.ID == btn.card.ID else DiscardedCard2_Y),
													 hpr_AlltheWay=(0, 0, 0)),
								Wait(0.6), Func(btn.np.detachNode))
						)
		handZone.placeCards()
		self.seqHolder[-1].append(para)
		
	def hand2BoardAni(self, card):
		ID = card.ID
		#At this point, minion has been inserted into the minions list. The btn on the minion won't change. It will simply change "isPlayed"
		handZone, minionZone = self.handZones[ID], self.minionZones[ID]
		ownMinions = self.Game.minions[ID]
		posMinions = posMinionsTable[minionZone.z][len(ownMinions)]
		pos_ontoBoard = posMinions[ownMinions.index(card)]
		#The minion must be first set to isPlayed=True, so that the later statChangeAni can correctly respond
		card.btn.isPlayed = True
		sequence = Sequence(Sequence(card.btn.genLerpInterval(pos=(pos_ontoBoard[0], MinionZone_Y - 5, pos_ontoBoard[2]),
														 hpr=(0, 0, 0), hpr_AlltheWay=(0, 0, 0), duration=0.25),
									 Func(card.btn.changeCard, card, True)),
							Parallel(Func(handZone.placeCards, False), Func(minionZone.placeCards, False)),
							name="Hand to board Ani")
		self.seqHolder[-1].append(sequence)
		
	def deck2BoardAni(self, card):
		ID = card.ID
		if not card.btn: genCard(self, card, isPlayed=False) #place these cards at pos(0, 0, 0), to be move into proper position later
		#At this point, minion has been inserted into the minions list. The btn on the minion won't change. It will simply change "isPlayed"
		deckZone, minionZone = self.deckZones[ID], self.minionZones[ID]
		ownMinions = self.Game.minions[ID]
		posMinions = posMinionsTable[minionZone.z][len(ownMinions)]
		pos_ontoBoard = posMinions[ownMinions.index(card)]
		deckPos = Deck1_Pos if ID == self.ID else Deck2_Pos
		#The minion must be first set to isPlayed=True, so that the later statChangeAni can correctly respond
		card.btn.isPlayed = True
		sequence = Sequence(Sequence(Func(deckZone.draw, len(card.Game.Hand_Deck.decks[ID])),
									Func(card.btn.np.setPosHprScale, deckPos, hpr_Deck, (deckScale, deckScale, deckScale)),
									card.btn.genLerpInterval(pos=(pos_ontoBoard[0], MinionZone_Y - 5, pos_ontoBoard[2]),
														  hpr=(0, 0, 0),duration=0.25),
									Func(card.btn.changeCard, card, True)),
							Func(minionZone.placeCards, False),
							name="Deck to board Ani")
		self.seqHolder[-1].append(sequence)
		
	#Amulets and dormants also count as minions
	def removeMinionorWeaponAni(self, card):
		if card.type in ("Minion", "Dormant"):
			minionZone = self.minionZones[card.ID]
			#At this point, minion has left the minions list
			ownMinions = self.Game.minions[card.ID]
			posMinions = posMinionsTable[minionZone.z][len(ownMinions)]
			self.seqHolder[-1].append(Func(card.btn.np.removeNode))
			parallel = Parallel()
			for i, minion in enumerate(ownMinions):
				parallel.append(minion.btn.genLerpInterval(pos=posMinions[i], duration=0.2))
			self.seqHolder[-1].append(parallel)
		elif card.type == "Weapon":
			self.seqHolder[-1].append(Func(card.btn.np.removeNode))
			
	#直接出现，而不是从手牌或者牌库中召唤出来
	def summonAni(self, card):
		minionZone = self.minionZones[card.ID]
		#At this point, minion has been inserted into the minions list
		ownMinions = self.Game.minions[card.ID]
		posMinions = posMinionsTable[minionZone.z][len(ownMinions)]
		genCard(self, card, isPlayed=True)
		para = Parallel()
		for i, minion in enumerate(ownMinions):
			para.append(minion.btn.genLerpInterval(pos=posMinions[i], duration=0.2))
		para.append(Wait(0.15))
		self.seqHolder[-1].append(para)
		
	def board2HandAni(self, card):
		handZone, minionZone = self.handZones[card.ID], self.minionZones[card.ID]
		btn = card.btn
		#At this point, minion has been extracted from the minion lists
		ownMinions, ownHands = self.Game.minions[card.ID], self.Game.Hand_Deck.hands[card.ID]
		posMinions = posMinionsTable[minionZone.z][len(ownMinions)]  #此时被移回手牌的随从已经离开了minions列表
		x, y, z = btn.np.getPos()
		btn.isPlayed = True
		para1 = Parallel(btn.genLerpInterval(pos=Point3(x, y - 5, z), duration=0.25))
		for i, minion in enumerate(ownMinions):
			para1.append(minion.btn.genLerpInterval(pos=posMinions[i], duration=0.2))
		self.seqHolder[-1].append(para1)
		self.seqHolder[-1].append(Func(btn.changeCard, card, False))
	#Only need to draw the btn, and the following addCardtoHand func handles moving the card
	
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
		nodePath, btn = genCard(self, card, isPlayed=False) #the card is preloaded and positioned at (0, 0, 0)
		sequence = Sequence(Func(nodePath.setPosHpr, deckZone.pos, Point3(90, 0, -90)),
							Func(deckZone.draw, len(self.Game.Hand_Deck.decks[card.ID])),
							btn.genLerpInterval(pos=pos_Pause, hpr=(0, 0, 0), scale=1, duration=0.4, blendType="easeOut"),
							Wait(1)
							)
		self.seqHolder[-1].append(sequence)
		
	def drawCardAni_IntoHand(self, oldCard, newCard):
		btn = oldCard.btn
		handZone = self.handZones[oldCard.ID]
		if btn.card != newCard:
			print("Drawn card is changed", newCard)
			handZone.transformHands([btn], [newCard])
		handZone.placeCards()
		self.seqHolder[-1].append(Func(self.deckZones[oldCard.ID].draw, len(self.Game.Hand_Deck.decks[newCard.ID])))
		
	def millCardAni(self, card):
		pos_Pause = DrawnCard1_PausePos if self.ID == card.ID else DrawnCard2_PausePos
		nodePath, btn = genCard(self, card, isPlayed=False)
		interval = btn.genLerpInterval(pos=pos_Pause, hpr=(0, 0, 0), duration=0.4, blendType="easeOut")
		self.seqHolder[-1].append(Sequence(interval, Wait(0.6), Func(nodePath.removeNode)))
		
	def cardLeavesDeckAni(self, card, enemyCanSee=True):
		pass
	
	def shuffleintoDeckAni(self, cards, enemyCanSee=True):
		ID = cards[0].ID
		deckZone = self.deckZones[ID]
		x, y, z = 0.3 * deckZone.x, deckZone.y - 15, 0.2 * deckZone.z
		para_ShuffleintoDeck, btns = Parallel(), []
		for i, card in enumerate(cards):
			nodePath, btn = genCard(self, card, isPlayed=False, pickable=False)
			para_ShuffleintoDeck.append(Sequence(Wait(0.4 * i + 0.6),
												 btn.genLerpInterval(pos=Point3(deckZone.x, deckZone.y, deckZone.z), hpr=Point3(90, 0, -90)),
												 Func(nodePath.removeNode)
												 )
										)
		self.seqHolder[-1].append(para_ShuffleintoDeck)
		self.seqHolder[-1].append(Func(deckZone.draw, len(self.Game.Hand_Deck.decks[ID])))
	
	def showTempText(self, text):
		text = OnscreenText(text=text, pos=(0, 0), scale=0.1, fg=(1, 0, 0, 1),
							align=TextNode.ACenter, mayChange=1, font=self.font,
							bg=(0.5, 0.5, 0.5, 0.8))
		Sequence(Wait(1.5), Func(text.destroy)).start()
	
	def wait(self, duration=0, showLine=False):
		pass
	
	#Attack animations
	def attackAni_Raise(self, subject):
		btn_Subject = subject.btn
		self.seqHolder[-1].append(btn_Subject.genLerpInterval(Point3(btn_Subject.np.get_x(), btn_Subject.np.get_y() - 5, btn_Subject.np.get_z()), duration=0.3))
		self.seqHolder[-1].append(Wait(0.15))
	
	def attackAni_HitandReturn(self, subject, target):
		btn_Subject, btn_Target = subject.btn, target.btn
		if subject.type == "Minion":
			minionZone, ownMinions = self.minionZones[subject.ID], self.Game.minions[subject.ID]
			pos_Orig = posMinionsTable[minionZone.z][len(ownMinions)][ownMinions.index(subject)]
		else: pos_Orig = self.heroZones[subject.ID].heroPos
		seq = Sequence(btn_Subject.genLerpInterval(btn_Target.np.getPos(), duration=0.17),
					   btn_Subject.genLerpInterval((pos_Orig[0], pos_Orig[1]-5, pos_Orig[2]), duration=0.17),
					   btn_Subject.genLerpInterval(pos_Orig, duration=0.15)
					   )
		self.seqHolder[-1].append(seq)
		
	def attackAni_Cancel(self, subject):
		btn = subject.btn
		self.seqHolder[-1].append(btn.genLerpInterval(Point3(btn.np.get_x(), btn.np.get_y() + 5, btn.np.get_z()), duration=0.15))
	
	def heroExplodeAni(self, entities):
		pass
	
	def minionsDieAni(self, entities):
		para = Parallel()
		for entity in entities:
			btn = entity.btn
			if btn:
				btn.dimDown()
				x, y, z = btn.np.getPos()
				dx, dz = 0.07 * np.random.rand(2)
				para.append(Sequence(btn.genLerpInterval(pos=Point3(x + dx, y, z + dz), duration=0.1),
									 btn.genLerpInterval(pos=Point3(x - dx, y, z - dz), duration=0.1),
									 btn.genLerpInterval(pos=Point3(x, y, z), duration=0.1),
									 ))
		self.seqHolder[-1].append(para)
		
	def deathrattleAni(self, entity, color="grey40"):
		self.showOffBoardTrig(entity)
		pos_Start = Point3(entity.x, entity.y, entity.z)
		deathrattle_Ani = self.loader.loadModel("TexCards\\Shared\\Deathrattle.egg")
		seqNode = deathrattle_Ani.find("+SequenceNode").node()
		seqNode.pose(0)
		deathrattle_Ani.reparentTo(self.render)
		self.seqHolder[-1].append(seqNode.play)
		
	def secretTrigAni(self, secret):
		heroZone = self.heroZones[secret.ID]
		btn = secret.btn
		if btn:
			heroZone.removeSecret(btn)
			heroZone.drawSecrets()
		self.showOffBoardTrig(secret)
	
	def showOffBoardTrig(self, card, followCurve=True):
		if card:
			z = self.heroZones[card.ID].heroPos[2]
			#if card.btn and isinstance(card.btn, Btn_Card) and card.btn.np: nodePath, btn_Card = card.btn.np, card.btn
			nodePath, btn_Card = self.addCard(card, pos=(0, 0, 0), pickable=False)
			self.seqHolder[-1].append(Func(nodePath.reparentTo, self.render))
			if followCurve:
				curveFile = "Models\\BoardModels\\DisplayCurve_%s.egg"%("Lower" if z < 0 else "Upper")
				self.seqHolder[-1].append(btn_Card.genMoPathIntervals(curveFileName=curveFile, duration=0.3))
			self.seqHolder[-1].append(Wait(1))
			self.seqHolder[-1].append(Func(nodePath.detachNode))
			
	def eraseOffBoardTrig(self, ID):
		pass
	
	def addCard(self, card, pos, pickable):
		if card.type == "Option":
			nodePath, btn_Card = genOption(self, card, pos=pos) #Option cards are always pickable
		else:
			btn_Orig = card.btn if card.btn and card.btn.np else None
			nodePath, btn_Card = genCard(self, card, pos=pos, isPlayed=False, pickable=pickable)
			if btn_Orig: card.btn = btn_Orig #一张牌只允许存有其创建伊始指定的btn
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
	def switchTurnAni(self):
		interval = self.btnTurnEnd.np.hprInterval(0.4, (0, 180 - self.btnTurnEnd.np.get_p(), 0))
		self.seqHolder[-1].append(Func(interval.start))
		
	def usePowerAni(self, card):
		btn, pos = card.btn, card.btn.np.getPos()
		sequence = Sequence(btn.genLerpInterval(pos=(pos[0], pos[1]-2, pos[2]), hpr=Point3(90, 0, 0)),
							btn.genLerpInterval(pos=pos, hpr=Point3(180, 0, 0)))
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
	
	def mouse1_Down(self):
		if self.mouseWatcherNode.hasMouse():
			mpos = self.mouseWatcherNode.getMouse()
			#Reset the Collision Ray orientation, based on the mouse position
			self.raySolid.setDirection(25 * mpos.getX(), 50.5, 14 * mpos.getY())
			
	def mouse1_Up(self):
		if self.mouseWatcherNode.hasMouse():
			mpos = self.mouseWatcherNode.getMouse()
			#Reset the Collision Ray orientation, based on the mouse position
			self.raySolid.setDirection(25 * mpos.getX(), 50.5, 14 * mpos.getY())
			if self.collHandler.getNumEntries() > 0:
				self.collHandler.sortEntries()
				cNode_Picked = self.collHandler.getEntry(0).getIntoNodePath()
				"""The scene graph tree is written in C. To store/read python objects, use NodePath.setPythonTag/getPythonTag()"""
				cNode_Picked.getParent().getPythonTag("btn").leftClick()
	
	def mouse3_Down(self):
		if self.mouseWatcherNode.hasMouse():
			mpos = self.mouseWatcherNode.getMouse()
			self.raySolid.setDirection(25 * mpos.getX(), 50.5, 14 * mpos.getY())
			
	def mouse3_Up(self):
		if self.mouseWatcherNode.hasMouse():
			mpos = self.mouseWatcherNode.getMouse()
			#Reset the Collision Ray orientation, based on the mouse position
			self.raySolid.setDirection(25*mpos.getX(), 50.5, 14*mpos.getY())
			if self.collHandler.getNumEntries() > 0:
				self.collHandler.sortEntries()
				cNode_Picked = self.collHandler.getEntry(0).getIntoNodePath()
				if self.UI == 0: cNode_Picked.getParent().getPythonTag("btn").rightClick()
				else: self.cancelSelection()
			else: self.cancelSelection()
	
	def mouseMove(self, task):
		#seqReady默认是True，只有在游戏操作结算中需要把seqReady设为False，而操作结算完成sequence的准备工作时会把seqReady再次设为True
		#seq2Play只在第一次进行游戏操作时为None，之后都是之前最近一次的操作的sequence，不再被清除
		if self.seqReady and self.seqHolder and (not self.seq2Play or not self.seq2Play.isPlaying()):
			self.seq2Play = self.seqHolder.pop(0)
			self.seq2Play.start()
			
		if self.mouseWatcherNode.hasMouse():
			mpos = self.mouseWatcherNode.getMouse()
			self.raySolid.setDirection(25 * mpos.getX(), 50.5, 14 * mpos.getY())
			if not self.arrow.isStashed():
				self.stopCardZoomIn()
				self.replotArrow()
			elif self.btnBeingDragged:
				self.stopCardZoomIn()
				self.dragCard()
			elif self.collHandler.getNumEntries() > 0:
				self.collHandler.sortEntries()
				if self.UI > -1:
					cNode_Picked = self.collHandler.getEntry(0).getIntoNodePath()
					btn_Picked = cNode_Picked.getParent().getPythonTag("btn")
					#The board also has a btn, but its btn.card is always None
					if btn_Picked.card and btn_Picked.card.type in ("Minion", "Spell", "Weapon", "Hero") \
							and btn_Picked.card.inHand and abs(btn_Picked.np.getZ()) > 10: #需要指向的卡牌在位置物靠近手牌位置 才可以
						#如果目前没有正在放大的的卡牌或者正在放大的卡牌不是目前被指向的卡牌，则重新画一个
						if not self.np_CardZoomIn or self.np_CardZoomIn.getPythonTag("btn").card is not btn_Picked.card:
							self.drawCardZoomIn(btn_Picked)
			#If no collision node is picked and the card in display is in hand. Then cancel the card in display
			elif self.np_CardZoomIn and hasattr(self.np_CardZoomIn.getPythonTag("btn").card, "inHand") and self.np_CardZoomIn.getPythonTag("btn").card.inHand:
				self.stopCardZoomIn()
		return Task.cont
	
	def drawCardZoomIn(self, btn):
		if not btn.card or (btn.card.type == "Hero" and btn.card.onBoard):
			if self.np_CardZoomIn: self.np_CardZoomIn.removeNode()
			self.np_CardZoomIn = None
		else:  #btn是一个牌的按键
			if hasattr(btn.card, "inHand") and btn.card.inHand:
				pos = (btn.np.getX(), ZoomInCard_Y, ZoomInCard1_Z if self.ID == btn.card.ID else ZoomInCard2_Z)
			else:
				pos = (ZoomInCard_X, ZoomInCard_Y, ZoomInCard1_Z if self.ID == btn.card.ID else ZoomInCard2_Z)
			if self.np_CardZoomIn: self.np_CardZoomIn.removeNode()
			self.np_CardZoomIn = self.addCard(btn.card, pos, pickable=False)[0]
	
	def stopCardZoomIn(self):
		if self.np_CardZoomIn:
			self.np_CardZoomIn.removeNode()
			self.np_CardZoomIn = None
	
	def dragCard(self):
		if self.btnBeingDragged.cNode:
			self.btnBeingDragged.cNode.removeNode() #The collision nodes are kept by the cards.
			self.btnBeingDragged.cNode = None
		
		#Decide the new position of the btn being dragged
		vec_X, vec_Y, vec_Z = self.raySolid.getDirection()
		y = self.btnBeingDragged.np.getY()
		delta_Y = abs(CamPos_Y - y)
		x, z = vec_X * delta_Y / vec_Y, vec_Z * delta_Y / vec_Y
		self.btnBeingDragged.np.setPosHpr(x, y, z, 0, 0, 0)
		#No need to change the x, y, z of the card being dragged(Will return anyway)
		card = self.btnBeingDragged.card
		if card.type == "Minion":
			minionZone = self.minionZones[card.ID]
			ownMinions = self.Game.minions[card.ID]
			boardSize = len(ownMinions)
			if not ownMinions:
				self.pos = -1
			else:
				ls_np_temp = [minion.btn.np for minion in ownMinions]
				posMinions_Orig = posMinionsTable[minionZone.z][boardSize]
				posMinions_Plus1 = posMinionsTable[minionZone.z][boardSize + 1]
				if -6 > z or z > 6:  #Minion away from the center board, the minions won't shift
					dict_MinionNp_Pos = {ls_np_temp[i]: posMinions_Orig[i] for i in range(boardSize)}
					self.pos = -1
				elif minionZone.z - 3.8 < z < minionZone.z + 3.8:
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
	
	def stopDraggingCard(self):
		btn = self.btnBeingDragged
		if btn:
			print("Stop dragging card", btn)
			btn.cNode = btn.np.attachNewNode(btn.cNode_Backup)
			ID = btn.card.ID
			#Put the card back in the right pos_hpr in hand
			handZone = self.handZones[ID]
			ownHand = self.Game.Hand_Deck.hands[ID]
			i = ownHand.index(btn.card)
			pos = posHandsTable[handZone.z][len(ownHand)][i]
			hpr = hprHandsTable[handZone.z][len(ownHand)][i]
			btn.np.setPosHpr(pos, hpr)
			btn.card.x, btn.card.y, btn.card.z = pos
			#Put the minions back to right positions on board
			ownMinions = self.Game.minions[ID]
			posMinions = posMinionsTable[self.minionZones[ID].z][len(ownMinions)]
			for i, minion in enumerate(ownMinions):
				minion.btn.np.setPos(posMinions[i])
				minion.x, minion.y, minion.z = posMinions[i]
			self.btnBeingDragged = None
	
	def replotArrow(self):
		#Decide the new orientation and scale of the arrow
		vec_X, vec_Y, vec_Z = self.raySolid.getDirection()
		btn_Subject = self.subject.btn
		x_0, y_0, z_0 = btn_Subject.np.getPos()
		x, z = vec_X * (y_0-CamPos_Y) / vec_Y, vec_Z * (y_0-CamPos_Y) / vec_Y
		delta_x, delta_z = x - x_0, z - z_0
		distance = max(0.1, math.sqrt(delta_x ** 2 + delta_z ** 2))
		angle = (180 / math.pi) * math.acos(delta_z / distance)
		if delta_x < 0: angle = -angle
		self.arrow.setScale(1, 1, distance / 7.5)
		self.arrow.setHpr(0, 0, angle)
	
	"""Game resolution setup"""
	def cancelSelection(self):
		self.stopDraggingCard()
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
				card.btn.setBoxColor(card.btn.decideColor())
			
			for card in self.Game.Hand_Deck.hands[1] + self.Game.Hand_Deck.hands[2] + [self.Game.powers[1]] + [self.Game.powers[2]]:
				if hasattr(card, "targets"): card.targets = []
	
	def resolveMove(self, entity, button, selectedSubject, info=None):
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
				self.gamePlayQueue.append(lambda : game.switchTurn())
			elif entity.ID != game.turn or (self.ID > 1 and entity.ID != self.ID):
				print("You can only select your own characters as subject.")
				self.cancelSelection()
			else:  #选择的是我方手牌、我方英雄、我方英雄技能、我方场上随从，
				self.subject, self.target = entity, None
				self.selectedSubject = selectedSubject
				self.UI, self.choice = 2, 0  #选择了主体目标，则准备进入选择打出位置或目标界面。抉择法术可能会将界面导入抉择界面。
				button.selected = 1 - button.selected
				self.arrow.stash()
				if selectedSubject.endswith("inHand"):  #Choose card in hand as subject
					if not game.Manas.affordable(entity):  #No enough mana to use card
						self.cancelSelection()
					else:  #除了法力值不足，然后是指向性法术没有合适目标和随从没有位置使用
						typewhenPlayed = self.subject.getTypewhenPlayed()
						if typewhenPlayed == "Spell" and not entity.available():
							#法术没有可选目标，或者是不可用的非指向性法术
							self.cancelSelection()
						elif game.space(entity.ID) < 1 and (typewhenPlayed == "Minion" or typewhenPlayed == "Amulet"):  #如果场上没有空位，且目标是护符或者无法触发激奏的随从的话，则不能打出牌
							#随从没有剩余位置
							self.cancelSelection()
						else:  #Playable cards
							if entity.need2Choose():
								#所选的手牌不是影之诗卡牌，且我方有抉择全选的光环
								if not entity.index.startswith("SV_"):
									if game.status[entity.ID]["Choose Both"] > 0:
										self.choice = -1  #跳过抉择，直接进入UI=1界面。
										if entity.needTarget(-1):
											self.highlightTargets(entity.findTargets("", self.choice)[0])
									else:  #Will conduct choose one
										self.UI = 1
										for i, option in enumerate(entity.options):
											pos = (4 + 8 * (i - 1), 45, -3 if entity.ID == 1 else 3)
											self.addCard(option, pos=pos, pickable=True)
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
								elif (typewhenPlayed not in ("Weapon", "Hero") and entity.needTarget()) or (typewhenPlayed == "Weapon" and entity.requireTarget):
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
						self.sendOwnMovethruServer() #In the 1P version, the sendOwnMovethruServer is blank anyways
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
				game.switchTurn()
			else:
				print("You must click an available option to continue.")
		#炉石的目标选择在此处进行
		elif self.UI == 2:  #影之诗的目标选择是不会进入这个阶段的，直接进入UI == 3，并在那里完成所有的目标选择
			self.target = entity
			print("Selected target: {}".format(entity))
			#No matter what the selections are, pressing EndTurn button ends the turn.
			#选择的主体是场上的随从或者英雄。之前的主体在UI=0的界面中已经确定一定是友方角色。
			if selectedSubject == "TurnEnds":
				self.cancelSelection()
				self.subject, self.target = None, None
				game.switchTurn()
				self.sendEndTurnthruServer()  #In the 1P version, the sendEndTurnthruServer is blank anyways
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
					self.sendOwnMovethruServer()  #In the 1P version, the sendOwnMovethruServer is blank anyways
			#手中选中的随从在这里结算打出位置，如果不需要目标，则直接打出。
			#假设有时候选择随从的打出位置时会有鼠标刚好划过一个随从的情况
			elif self.selectedSubject == "MinioninHand" or self.selectedSubject == "AmuletinHand":  #选中场上的友方随从，我休眠物和护符时会把随从打出在其左侧
				if selectedSubject == "Board" or (entity.ID == self.subject.ID and (selectedSubject.endswith("onBoard") and not selectedSubject.startswith("Hero"))):
					self.selectedSubject = "MinionPosDecided"  #将主体记录为标记了打出位置的手中随从。
					#抉择随从如有全选光环，且所有选项不需目标，则直接打出。 连击随从的needTarget()由连击条件决定。
					#print("Minion {} in hand needs target: {}".format(self.subject.name, self.subject.needTarget(self.choice)))
					if not (self.subject.needTarget(self.choice) and self.subject.targetExists(self.choice)):
						#print("Requesting to play minion {} without target. The choice is {}".format(self.subject.name, self.choice))
						subject, position, choice = self.subject, self.pos, self.choice
						self.cancelSelection()
						self.subject, self.target = subject, None
						self.gamePlayQueue.append(lambda : game.playMinion(subject, None, position, choice))
						self.sendOwnMovethruServer()  #In the 1P version, the sendOwnMovethruServer is blank anyways
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
			#随从的打出位置和抉择选项已经在上一步选择，这里处理目标选择。
			elif self.selectedSubject == "MinionPosDecided":
				if selectedSubject == "MiniononBoard" or selectedSubject == "HeroonBoard":
					print("Requesting to play minion {}, targeting {} with choice: {}".format(self.subject.name, entity.name, self.choice))
					subject, position, choice = self.subject, self.pos, self.choice
					self.cancelSelection()
					self.subject, self.target = subject, entity
					self.gamePlayQueue.append(lambda : game.playMinion(subject, entity, position, choice))
					self.sendOwnMovethruServer()  #In the 1P version, the sendOwnMovethruServer is blank anyways
				else:
					print("Not a valid selection. All selections canceled.")
			#选中的法术已经确定抉择选项（如果有），下面决定目标选择。
			elif self.selectedSubject == "SpellinHand":
				if not self.subject.needTarget(self.choice):  #Non-targeting spells can only be cast by clicking the board
					if "Board" in selectedSubject:  #打出非指向性法术时，可以把卡牌拖动到随从，英雄或者桌面上
						print("Requesting to play spell {} without target. The choice is {}".format(self.subject.name, self.choice))
						subject, target, choice = self.subject, None, self.choice
						self.cancelSelection()
						self.subject, self.target = subject, target
						self.gamePlayQueue.append(lambda : game.playSpell(subject, target, choice))
						self.sendOwnMovethruServer()  #In the 1P version, the sendOwnMovethruServer is blank anyways
				else:  #法术或者法术抉择选项需要指定目标。
					if selectedSubject == "MiniononBoard" or selectedSubject == "HeroonBoard":
						print("Requesting to play spell {} with target {}. The choice is {}".format(self.subject.name, entity, self.choice))
						subject, target, choice = self.subject, entity, self.choice
						self.cancelSelection()
						self.subject, self.target = subject, target
						self.gamePlayQueue.append(lambda : game.playSpell(subject, target, choice))
						self.sendOwnMovethruServer()  #In the 1P version, the sendOwnMovethruServer is blank anyways
					else:
						print("Targeting spell must be cast on Hero or Minion on board.")
			#选择手牌中的武器的打出目标
			elif self.selectedSubject == "WeaponinHand":
				if not self.subject.requireTarget:
					if selectedSubject == "Board":
						print("Requesting to play Weapon {}".format(self.subject.name))
						subject, target = self.subject, None
						self.cancelSelection()
						self.subject, self.target = subject, None
						self.gamePlayQueue.append(lambda : game.playWeapon(subject, None))
						self.sendOwnMovethruServer()  #In the 1P version, the sendOwnMovethruServer is blank anyways
				else:
					if selectedSubject == "MiniononBoard" or selectedSubject == "HeroonBoard":
						subject, target = self.subject, entity
						print("Requesting to play weapon {} with target {}".format(subject.name, target.name))
						self.cancelSelection()
						self.subject, self.target = subject, target
						self.gamePlayQueue.append(lambda : game.playWeapon(subject, target))
						self.sendOwnMovethruServer()  #In the 1P version, the sendOwnMovethruServer is blank anyways
					else:
						print("Targeting weapon must be played with a target.")
			#手牌中的英雄牌是没有目标的
			elif self.selectedSubject == "HeroinHand":
				if selectedSubject == "Board":
					print("Requesting to play hero card %s" % self.subject.name)
					subject = self.subject
					self.cancelSelection()
					self.subject, self.target = subject, None
					self.gamePlayQueue.append(lambda : game.playHero(subject))
					self.sendOwnMovethruServer()  #In the 1P version, the sendOwnMovethruServer is blank anyways
			#Select the target for a Hero Power.
			#在此选择的一定是指向性的英雄技能。
			elif self.selectedSubject == "Power":  #如果需要指向的英雄技能对None使用，HeroPower的合法性检测会阻止使用。
				if selectedSubject == "MiniononBoard" or selectedSubject == "HeroonBoard":
					print("Requesting to use Hero Power {} on {}".format(self.subject.name, entity.name))
					subject = self.subject
					self.cancelSelection()
					self.subject, self.target = subject, entity
					self.gamePlayQueue.append(lambda : subject.use(entity))
					self.sendOwnMovethruServer()  #In the 1P version, the sendOwnMovethruServer is blank anyways
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
					self.sendOwnMovethruServer() #In the 1P version, the sendEndTurnthruServer is blank anyways
			elif selectedSubject == "Fusion":
				self.UI = 0
				game.Discover.initiator.fusionDecided(entity)
			else:
				print("You MUST click a correct object to continue.")
	
	#Can only be invoked by the game thread
	def waitforDiscover(self, info=None):
		self.UI, self.discover = 3, None
		for i, card in enumerate(self.Game.options):
			self.addCard(card, Point3(-5 + 5 * i, 40, 0), pickable=True)
		btn_HideOptions = DirectButton(text=("Hide", "Hide", "Hide", "Continue"),
									   scale=.1)
		btn_HideOptions.setPos(-0.5, 0, -0.5)
		btn_HideOptions.command = lambda: self.toggleDiscoverHide(btn_HideOptions)
		while self.discover is None:
			time.sleep(0.1)
		for card in self.Game.options:
			card.btn.np.removeNode()
		btn_HideOptions.destroy()
		self.Game.Discover.initiator.discoverDecided(self.discover, info)
		self.discover = None
	
	def toggleDiscoverHide(self, btn):
		print("Toggle hide button", btn["text"])
		if btn["text"] == ("Hide", "Hide", "Hide", "Continue"):
			btn["text"] = ("Show", "Show", "Show", "Continue")
			for card in self.Game.options: card.btn.np.stash()
		else:
			btn.text = ("Hide", "Hide", "Hide", "Continue")
			for card in self.Game.options: card.btn.np.unstash()
			
	def sendOwnMovethruServer(self):
		pass
		
	def sendEndTurnthruServer(self):
		pass