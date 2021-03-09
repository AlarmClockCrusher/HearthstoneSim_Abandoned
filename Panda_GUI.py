from direct.gui.OnscreenText import OnscreenText
from direct.gui.DirectGui import *
from direct.showbase.ShowBase import ShowBase
from panda3d.core import *
from direct.interval.IntervalGlobal import Sequence, Func, Wait
from direct.task import Task
import time

import simplepbr

from Game import *
from Code2CardList import *
from GenerateRNGPools import *
from Panda_CustomWidgets import *

CHN = True

configVars = """
win-size 1440 800
window-title Single Player Hearthstone Simulator
clock-mode limited
clock-frame-rate 45
text-use-harfbuzz true
"""

loadPrcFileData('', configVars)

ClassDict = {'Demon Hunter': Illidan, 'Druid': Malfurion, 'Hunter': Rexxar, 'Mage': Jaina, 'Paladin': Uther,
			 'Priest': Anduin, 'Rogue': Valeera, 'Shaman': Thrall, 'Warlock': Guldan, 'Warrior': Garrosh, }


mulliganCard_Y = 40

class GUI_IP(ShowBase):
	def __init__(self):
		ShowBase.__init__(self)
		#simplepbr.init(max_lights=4)
		#self.disableMouse()
		
		self.UI = -2 #Starts at -2, for the mulligan stage
		self.pickablesDrawn = []
		self.board = None
		self.mulliganStatus = {1: [0, 0, 0], 2: [0, 0, 0, 0]}
		#Attributes of the GUI
		self.selectedSubject = ""
		self.subject, self.target = None, None
		self.pos, self.choice, self.UI = -1, 0, -2  #起手调换为-2
		self.discover = None
		self.btnBeingDragged = None
		self.nodePath_CardSpecsDisplay = None
		self.intervalInfos = []
		self.gameThread = None
		
		self.accept("mouse1", self.mouse1_Down)
		self.accept("mouse1-up", self.mouse1_Up)
		self.accept("mouse3", self.mouse3_Down)
		self.accept("mouse3-up", self.mouse3_Up)
		
		"""First layer"""
		widgets_1stLayer = []
		widgets_1stLayer.append(OnscreenText(text="Include DIY", pos=(-0.4, 0.5), scale=0.1,
								align=TextNode.ACenter)
								)
		#monkCheckButton = DirectCheckButton(text = "Monk" ,scale=.1)
		#SVCheckButton = DirectCheckButton(text = "Shadowverse" ,scale=.1)
		
		widgets_1stLayer.append(OnscreenText(text="Select Board", pos=(-0.4, 0.2), scale=0.1,
								align=TextNode.ACenter)
								)
		self.boardMenu = DirectOptionMenu(text=BoardIndex[0], scale=0.1,
										  items=BoardIndex, initialitem=0,
										  highlightColor=(0, 1, 0, 1))
		self.boardMenu.setPos(-1, 0, 0.1)
		btn_genCardPool = DirectButton(text=("Continue", "Click!", "Rolling Over", "Continue"),
                 scale=.1, command=lambda: self.init_Layer1to2(widgets_1stLayer))
		#btn_genCardPool.reparentTo(self.render)
		btn_genCardPool.setPos(-0.4, 0, -0.2)
		widgets_1stLayer.append(btn_genCardPool)
		#The deck codes and hero select for both players
		heroClasses = ['Demon Hunter', 'Druid', 'Hunter', 'Mage', 'Paladin', 'Priest', 'Rogue', 'Shaman', 'Warlock', 'Warrior']
		self.hero1Menu = DirectOptionMenu(text=heroClasses[0], scale=0.1,
										  items=heroClasses, initialitem=0,
										  highlightColor=(0, 1, 0, 1))
		self.hero2Menu = DirectOptionMenu(text=heroClasses[0], scale=0.1,
								  items=heroClasses, initialitem=0,
								  highlightColor=(0, 1, 0, 1))
		self.deck1 = DirectEntry(width=50, scale=0.04)
		self.deck2 = DirectEntry(width=50, scale=0.04)
		widgets_1stLayer.append(OnscreenText(text="Class of 1st Player", pos=(0.7, 0.8), scale=0.1,
								align=TextNode.ACenter))
		self.hero1Menu.setPos(0.35, 0, 0.7)
		widgets_1stLayer.append(OnscreenText(text="Class of 2nd Player", pos=(0.7, 0.6), scale=0.1,
											 align=TextNode.ACenter))
		self.hero2Menu.setPos(0.35, 0, 0.5)
		widgets_1stLayer.append(OnscreenText(text="Deck of 1st Player", pos=(0.7, -0.2), scale=0.1,
											 align=TextNode.ACenter))
		#Decks
		self.deck1.setPos(0.2, 0, -0.3)
		widgets_1stLayer.append(OnscreenText(text="Deck of 2nd Player", pos=(0.7, -0.4), scale=0.1,
											 align=TextNode.ACenter))
		self.deck2.setPos(0.2, 0, -0.5)
		widgets_1stLayer.append(self.boardMenu)
		widgets_1stLayer.append(self.hero1Menu)
		widgets_1stLayer.append(self.hero2Menu)
		widgets_1stLayer.append(self.deck1)
		widgets_1stLayer.append(self.deck2)
		
		self.init_CollisionSetup()
	
	def init_Layer1to2(self, widgets):
		hero1, hero2 = self.hero1Menu.get(), self.hero2Menu.get()
		deck1, deck2 = self.deck1.get(), self.deck2.get()
		heroes = {1: ClassDict[hero1], 2: ClassDict[hero2]}
		deckStrings = {1: deck1, 2: deck2}
		decks, decksCorrect = {1: [], 2: []}, {1: False, 2: False}
		self.boardID, self.transferStudentType = makeCardPool(self.boardMenu.get(), 0, 0)
		for ID in range(1, 3):
			decks[ID], decksCorrect[ID], heroes[ID] = parseDeckCode(deckStrings[ID], heroes[ID], ClassDict)
			
		if decksCorrect[1] and decksCorrect[2]:
			for widget in widgets: widget.destroy()
			
			self.Game = Game(self)
			self.Game.transferStudentType = self.transferStudentType
			print(self.Game.transferStudentType)
			for ID in range(1, 3):
				for i, card in enumerate(decks[ID]):
					if card.name == "Transfer Student": decks[ID][i] = self.transferStudentType
			self.Game.mode = 0
			self.Game.Classes, self.Game.ClassesandNeutral = Classes, ClassesandNeutral
			self.Game.initialize(cardPool, ClassCards, NeutralCards, MinionsofCost, RNGPools, heroes[1], heroes[2], decks[1], decks[2])
			self.initMulliganDisplay()
		else:
			if not decksCorrect[1]:
				if decksCorrect[2]: self.showTempText("Deck 1 incorrect")
				else: self.showTempText("Both Deck 1&2 incorrect")
			else: self.showTempText("Deck 2 incorrect")
			
	def initMulliganDisplay(self):
		self.posMulligans = {1: [(-8*(i-1), 50, -5) for i in range(len(self.Game.mulligans[1]))],
								 2: [(-4-8*(i-2), 50, 5) for i in range(len(self.Game.mulligans[2]))]}
		self.initGameDisplay()
		mulliganBtns = []
		for i in range(1, 3):
			for pos, card in zip(self.posMulligans[i], self.Game.mulligans[i]):
				mulliganBtns.append(self.addCard(card, pos, scale=0.7))
				
		btn_Mulligan = DirectButton(text=("Confirm", "Confirm", "Confirm", "Confirm"), scale=0.08,
									command=self.startMulligan)
		btn_Mulligan["extraArgs"] = [mulliganBtns, btn_Mulligan]
		btn_Mulligan.setPos(0, 0, 0)
		self.taskMgr.add(self.mouseMove, "Task_MoveCard")
	
	def startMulligan(self, mulliganBtns, btn_Mulligan):
		self.UI = 0
		indices1 = [i for i, status in enumerate(self.mulliganStatus[1]) if status]
		indices2 = [i for i, status in enumerate(self.mulliganStatus[2]) if status]
		#self.GUI.gameBackup = self.GUI.Game.copyGame()[0]
		btn_Mulligan.destroy()
		for btn in mulliganBtns:
			self.removeCard(btn)
		self.Game.Hand_Deck.mulligan(indices1, indices2)
		#self.gameBackup = self.Game.copyGame()[0]
		self.update()
		
	def initGameDisplay(self):
		self.handZones = {1: HandZone(self, 1), 2: HandZone(self, 2)}
		self.boardZones = {1: BoardZone(self, 1), 2: BoardZone(self, 2)}
		self.heroZones = {1: HeroZone(self, 1), 2: HeroZone(self, 2)}
		self.deckZones = {1: DeckZone(self, 1), 2: DeckZone(self, 2)}
		#self.Game.Hand_Deck.hands[1] = [AbusiveSergeant(self.Game, 1), Deathwing(self.Game, 1), SoulMirror(self.Game, 1),
		#								LordJaraxxus(self.Game, 1), RinlingsRifle(self.Game, 1)]
		#self.Game.Hand_Deck.hands[2] = [AbusiveSergeant(self.Game, 2), Deathwing(self.Game, 2), SoulMirror(self.Game, 1),
		#								LordJaraxxus(self.Game, 2), RinlingsRifle(self.Game, 2)]
		self.Game.minions[1] = [AbusiveSergeant(self.Game, 1), Deathwing(self.Game, 1), Moonfang(self.Game, 1),
								Huffer(self.Game, 1), Leokk(self.Game, 1), Misha(self.Game, 1)]
		self.Game.minions[2] = [AbusiveSergeant(self.Game, 2), Deathwing(self.Game, 2), Moonfang(self.Game, 2),
								Huffer(self.Game, 2), Leokk(self.Game, 2), Misha(self.Game, 2)]
		self.Game.weapons[1] = [EaglehornBow(self.Game, 1)]
		self.Game.weapons[2] = [BulwarkofAzzinoth(self.Game, 2)]
		for ID in range(1, 3):
			self.Game.weapons[1][0].onBoard = True
			for minion in self.Game.minions[ID]: minion.onBoard = True
		for ID in range(1, 3):
			self.handZones[ID].draw()
			self.boardZones[ID].draw()
			self.heroZones[ID].draw()
			self.heroZones[ID].drawMana()
		self.board = Board(self)
		self.pickablesDrawn.append(self.board)
		btn_TurnEnd = TurnEndButton(self)
		btn_TurnEnd.setPos(14.4, self.board.pos[1], 1)
		self.pickablesDrawn.append(btn_TurnEnd)
		self.cam.setPos(0, 3.8, 0)
		
	"""Control setup"""
	def init_CollisionSetup(self):
		self.cTrav = CollisionTraverser()
		self.collHandler = CollisionHandlerQueue()
		
		self.raySolid = CollisionRay()
		collNode_Picker = CollisionNode("Picker Collider c_node")
		collNode_Picker.addSolid(self.raySolid)
		pickerNode = self.camera.attachNewNode(collNode_Picker)
		#pickerNode.show()  #For now, show the pickerRay collision with the card models
		self.cTrav.addCollider(pickerNode, self.collHandler)
	
		#self.cTrav.showCollisions(self.render)
		
	def mouse1_Down(self):
		if self.mouseWatcherNode.hasMouse():
			mpos = self.mouseWatcherNode.getMouse()
			#Reset the Collision Ray orientation, based on the mouse position
			self.raySolid.setFromLens(self.camNode, mpos.getX(), mpos.getY())
		#if self.btnBeingDragged:
		#	self.resolveMove(self.btnBeingDragged.card, self.btnBeingDragged, self.btnBeingDragged.card.type+"inHand")
		#
	def mouse1_Up(self):
		if self.mouseWatcherNode.hasMouse():
			mpos = self.mouseWatcherNode.getMouse()
			#Reset the Collision Ray orientation, based on the mouse position
			self.raySolid.setFromLens(self.camNode, mpos.getX(), mpos.getY())
			if self.collHandler.getNumEntries() > 0:
				self.collHandler.sortEntries()
				collNode_Picked = self.collHandler.getEntry(0).getIntoNodePath()
				pickedModel_NodePath = collNode_Picked.getParent()
				"""Due to unknown reasons, all node paths are involved in the render hierachy
					have their types forced into NodePath, even if they are subclasses of NodePath.
					Therefore, we have to keep a container of the subclass instance, where the original type is preserved"""
				nodePath_Picked = next((model_NodePath for model_NodePath in self.pickablesDrawn \
													if model_NodePath == pickedModel_NodePath), None)
				if nodePath_Picked:
					nodePath_Picked.leftClick()

	def mouse3_Down(self):
		if self.mouseWatcherNode.hasMouse():
			mpos = self.mouseWatcherNode.getMouse()
			self.raySolid.setFromLens(self.camNode, mpos.getX(), mpos.getY())
		self.cancelSelection()
		
	def mouse3_Up(self):
		if self.mouseWatcherNode.hasMouse():
			mpos = self.mouseWatcherNode.getMouse()
			#Reset the Collision Ray orientation, based on the mouse position
			self.raySolid.setFromLens(self.camNode, mpos.getX(), mpos.getY())
			if self.collHandler.getNumEntries() > 0:
				self.collHandler.sortEntries()
				collNode_Picked = self.collHandler.getEntry(0).getIntoNodePath()
				pickedModel_NodePath = collNode_Picked.getParent()
				nodePath_Picked = next((model_NodePath for model_NodePath in self.pickablesDrawn \
										if model_NodePath == pickedModel_NodePath), None)
				if nodePath_Picked:
					nodePath_Picked.rightClick()
	
	def cancelSelection(self):
		self.stopDraggingCard()
		if 3 > self.UI > -1:  #只有非发现状态,且游戏不在结算过程中时下才能取消选择
			self.subject, self.target = None, None
			self.UI, self.pos, self.choice = 0, -1, -1
			self.selectedSubject = ""
			for btn in self.pickablesDrawn:
				btn.setColor("white")
			self.resetCardColors()
			for card in self.Game.Hand_Deck.hands[1] + self.Game.Hand_Deck.hands[2] + [self.Game.powers[1]] + [self.Game.powers[2]]:
				if hasattr(card, "targets"): card.targets = []
	
	def resolveMove(self, entity, button, selectedSubject, info=None):
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
				game.switchTurn()
				self.update()
				if hasattr(self, "sock"):
					print("Turn ends . Send the info to server")
					self.sendEndTurnthruServer()
			elif entity.ID != game.turn or (hasattr(self, "ID") and entity.ID != self.ID):
				print("You can only select your own characters as subject.")
				self.cancelSelection()
			else:  #选择的是我方手牌、我方英雄、我方英雄技能、我方场上随从，
				self.subject, self.target = entity, None
				self.selectedSubject = selectedSubject
				self.UI, self.choice = 2, 0  #选择了主体目标，则准备进入选择打出位置或目标界面。抉择法术可能会将界面导入抉择界面。
				button.selected = 1 - button.selected
				button.setColor("blue")
				if selectedSubject.endswith("inHand"):  #Choose card in hand as subject
					if not game.Manas.affordable(entity):  #No enough mana to use card
						self.cancelSelection()
					else:  #除了法力值不足，然后是指向性法术没有合适目标和随从没有位置使用
						typewhenPlayed = self.subject.getTypewhenPlayed()
						if typewhenPlayed == "Spell" and not entity.available():
							#法术没有可选目标，或者是不可用的非指向性法术
							self.cancelSelection()
						elif game.space(entity.ID) < 1 and (typewhenPlayed == "Minion" or typewhenPlayed == "Amulet"):  #如果场上没有空位，且目标是护符或者无法触发激奏的随从的话，则不能打出牌
							self.cancelSelection()
						else: #Playable cards
							print("Selected in hand card", entity.name)
							if entity.need2Choose():
								#所选的手牌不是影之诗卡牌，且我方有抉择全选的光环
								if not entity.index.startswith("SV_") and game.status[entity.ID]["Choose Both"] > 0:
									self.choice = -1  #跳过抉择，直接进入UI=1界面。
									if entity.needTarget(-1):
										self.highlightTargets(entity.findTargets("", self.choice)[0])
								elif entity.index.startswith("SV_"):
									game.options = entity.options
									self.UI = 1  #进入抉择界面，退出抉择界面的时候已经self.choice已经选好。
									self.update()
									return
							#如果选中的手牌是一个需要选择目标的SV法术
							elif entity.index.startswith("SV_") and typewhenPlayed == "Spell" and entity.needTarget():
								self.choice = -1  #影之诗因为有抉择不发动的情况，所以不能默认choice为0（炉石中的非抉择卡牌都默认choice=0），所以需要把choice默认为-1
								#需要目标选择的影之诗卡牌开始进入多个目标的选择阶段
								game.Discover.startSelect(entity, entity.findTargets("")[0])
								return
							#选中的手牌是需要目标的炉石卡
							elif (typewhenPlayed != "Weapon" and entity.needTarget()) or (typewhenPlayed == "Weapon" and entity.requireTarget):
								self.highlightTargets(entity.findTargets("", self.choice)[0])
							self.btnBeingDragged = button
							print("Ready for drag")
							
				#不需目标的英雄技能当即使用。需要目标的进入目标选择界面。暂时不用考虑技能的抉择
				elif selectedSubject == "Power":
					if entity.name == "Evolve":
						self.selectedSubject = "Power"
						game.Discover.startSelect(entity, entity.findTargets("")[0])
					#英雄技能会自己判定是否可以使用。
					elif entity.needTarget():  #selectedSubject之前是"Hero Power 1"或者"Hero Power 2"
						self.selectedSubject = "Power"
						self.highlightTargets(entity.findTargets("", self.choice)[0])
					else:
						print("Request to use Hero Power {}".format(self.subject.name))
						subject = self.subject
						self.cancelSelection()
						self.subject, self.target, self.UI = subject, None, -1
						self.executeGamePlay(lambda: subject.use(None))
				#不能攻击的随从不能被选择。
				elif selectedSubject.endswith("onBoard"):
					if not entity.canAttack():
						self.cancelSelection()
					else:
						self.highlightTargets(entity.findBattleTargets()[0])
		
		elif self.UI == 1:  #在抉择界面下点击了抉择选项会进入此结算流程
			if selectedSubject == "ChooseOneOption" and entity.available():
				if self.subject.index.startswith("SV_"):  #影之诗的卡牌的抉择选项确定之后进入与炉石卡不同的UI
					index = game.options.index(entity)
					self.UI, self.choice = 2, index
					for btn in self.pickablesDrawn[:]:
						if isinstance(btn.card, ChooseOneOption): self.removeCard(btn)
					if self.subject.needTarget(self.choice):
						self.highlightTargets(self.subject.findTargets("", self.choice)[0])
				else:  #炉石卡的抉择选项确定完毕
					#The first option is indexed as 0.
					index = game.options.index(entity)
					self.UI, self.choice = 2, index
					for btn in self.pickablesDrawn[:]:
						if isinstance(btn.card, ChooseOneOption): self.removeCard(btn)
					if self.subject.needTarget(self.choice):
						self.highlightTargets(self.subject.findTargets("", self.choice)[0])
			elif selectedSubject == "TurnEnds":
				self.cancelSelection()
				self.subject, self.target = None, None
				game.switchTurn()
				self.update()
				if hasattr(self, "sock"):
					print("Turn ends . Send the info to server")
					self.sendEndTurnthruServer()
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
				self.update()
				if hasattr(self, "sock"):
					print("Turn ends . Send the info to server")
					self.sendEndTurnthruServer()
			elif selectedSubject.endswith("inHand"):  #影之诗的目标选择不会在这个阶段进行
				self.cancelSelection()
			elif self.selectedSubject.endswith("onBoard"):
				if "Hero" not in selectedSubject and selectedSubject != "MiniononBoard":
					print("Invalid target for minion attack.")
				else:
					print("Requesting battle: {} attacks {}".format(self.subject.name, entity))
					subject, target = self.subject, self.target
					self.cancelSelection()
					self.subject, self.target, self.UI = subject, target, -1
					self.executeGamePlay(lambda: game.battle(subject, target))
			#手中选中的随从在这里结算打出位置，如果不需要目标，则直接打出。
			elif self.selectedSubject == "MinioninHand" or self.selectedSubject == "AmuletinHand":  #选中场上的友方随从，我休眠物和护符时会把随从打出在其左侧
				if selectedSubject == "Board" or (entity.ID == self.subject.ID and (selectedSubject.endswith("onBoard") and not selectedSubject.startswith("Hero"))):
					self.pos = -1 if selectedSubject == "Board" else entity.pos
					#print("Position for minion in hand decided: %d"%self.pos)
					self.selectedSubject = "MinionPositionDecided"  #将主体记录为标记了打出位置的手中随从。
					#抉择随从如有全选光环，且所有选项不需目标，则直接打出。 连击随从的needTarget()由连击条件决定。
					#print("Minion {} in hand needs target: {}".format(self.subject.name, self.subject.needTarget(self.choice)))
					if not (self.subject.needTarget(self.choice) and self.subject.targetExists(self.choice)):
						#print("Requesting to play minion {} without target. The choice is {}".format(self.subject.name, self.choice))
						subject, position, choice = self.subject, self.pos, self.choice
						self.cancelSelection()
						self.subject, self.target, self.UI = subject, None, -1
						self.executeGamePlay(lambda: game.playMinion(subject, None, position, choice))
					else:
						#print("The minion requires target to play. needTarget() returns {}".format(self.subject.needTarget(self.choice)))
						button.setColor("purple")
						#需要区分SV和炉石随从的目标选择。
						subject = self.subject
						#如果是影之诗随从，则需要进入多个目标选择的UI==3阶段，而炉石随从则仍留在该阶段之路等待单目标选择的完成
						if subject.index.startswith("SV_"):  #能到这个阶段的都是有目标选择的随从
							self.choice = 0
							game.Discover.startSelect(subject, subject.findTargets("")[0])
			#随从的打出位置和抉择选项已经在上一步选择，这里处理目标选择。
			elif self.selectedSubject == "MinionPositionDecided":
				if selectedSubject == "MiniononBoard" or selectedSubject == "HeroonBoard":
					print("Requesting to play minion {}, targeting {} with choice: {}".format(self.subject.name, entity.name, self.choice))
					subject, position, choice = self.subject, self.pos, self.choice
					self.cancelSelection()
					self.subject, self.target, self.UI = subject, entity, -1
					self.executeGamePlay(lambda : game.playMinion(subject, entity, position, choice))
				else:
					print("Not a valid selection. All selections canceled.")
			#选中的法术已经确定抉择选项（如果有），下面决定目标选择。
			elif self.selectedSubject == "SpellinHand":
				if not self.subject.needTarget(self.choice):  #Non-targeting spells can only be cast by clicking the board
					if selectedSubject == "Board":
						print("Requesting to play spell {} without target. The choice is {}".format(self.subject.name, self.choice))
						subject, target, choice = self.subject, None, self.choice
						self.cancelSelection()
						self.subject, self.target, self.UI = subject, target, -1
						self.executeGamePlay(lambda: game.playSpell(subject, target, choice))
				else:  #法术或者法术抉择选项需要指定目标。
					if selectedSubject == "MiniononBoard" or selectedSubject == "HeroonBoard":
						print("Requesting to play spell {} with target {}. The choice is {}".format(self.subject.name, entity, self.choice))
						subject, target, choice = self.subject, entity, self.choice
						self.cancelSelection()
						self.subject, self.target, self.UI = subject, target, -1
						self.executeGamePlay(lambda : game.playSpell(subject, target, choice))
					else:
						print("Targeting spell must be cast on Hero or Minion on board.")
			#选择手牌中的武器的打出目标
			elif self.selectedSubject == "WeaponinHand":
				if not self.subject.requireTarget:
					if selectedSubject == "Board":
						print("Requesting to play Weapon {}".format(self.subject.name))
						subject, target = self.subject, None
						self.cancelSelection()
						self.subject, self.target, self.UI = subject, None, -1
						self.executeGamePlay(lambda: game.playWeapon(subject, None))
				else:
					if selectedSubject == "MiniononBoard" or selectedSubject == "HeroonBoard":
						subject, target = self.subject, entity
						print("Requesting to play weapon {} with target {}".format(subject.name, target.name))
						self.cancelSelection()
						self.subject, self.target, self.UI = subject, target, -1
						self.executeGamePlay(lambda : game.playWeapon(subject, target))
					else:
						print("Targeting weapon must be played with a target.")
			#手牌中的英雄牌是没有目标的
			elif self.selectedSubject == "HeroinHand":
				if selectedSubject == "Board":
					print("Requesting to play hero card %s" % self.subject.name)
					subject = self.subject
					self.cancelSelection()
					self.subject, self.target, self.UI = subject, None, -1
					self.executeGamePlay(lambda: game.playHero(subject))
			#Select the target for a Hero Power.
			#在此选择的一定是指向性的英雄技能。
			elif self.selectedSubject == "Power":  #如果需要指向的英雄技能对None使用，HeroPower的合法性检测会阻止使用。
				if selectedSubject == "MiniononBoard" or selectedSubject == "HeroonBoard":
					print("Requesting to use Hero Power {} on {}".format(self.subject.name, entity.name))
					subject = self.subject
					self.cancelSelection()
					self.subject, self.target, self.UI = subject, entity, -1
					self.executeGamePlay(lambda: subject.use(entity))
				else:
					print("Targeting hero power must be used with a target.")
		else:  #self.UI == 3
			if selectedSubject == "DiscoverOption":
				self.UI = 0
				self.update()
				self.discover = entity
			elif selectedSubject == "SelectObj":
				# print("Selecting obj for SV card")
				self.choice += 1
				self.subject.targets.append(entity)
				try:
					self.target.append(entity)
				except:
					self.target = [entity]
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
					self.executeGamePlay(func)
			elif selectedSubject == "Fusion":
				self.UI = 0
				self.update()
				if hasattr(self, "sock"):
					self.sendOwnMovethruServer()
				game.Discover.initiator.fusionDecided(entity)
			else:
				print("You MUST click a correct object to continue.")
	
	def executeGamePlay(self, func):
		self.gameThread = threading.Thread(target=lambda : self.targetFunc4GameThread(func), daemon=True)
		self.gameThread.start()
		
	def targetFunc4GameThread(self, func):
		func()
		self.subject, self.target, self.UI = None, None, 0
		self.update()
		if hasattr(self, "sock"):
			self.sendOwnMovethruServer()
			
	def waitforDiscover(self, info=None):
		print("Start discover in GUI")
		self.UI, self.discover = 3, None
		for i, card in enumerate(self.Game.options):
			print("Drawing option ", i, card)
			pos = Point3(-5+5*i, 40, 0)
			self.addCard(card, pos)
		while self.discover is None:
			time.sleep(0.2)
		for card in self.Game.options:
			i, btn = next((i, btn) for i, btn in enumerate(self.pickablesDrawn) if btn.card == card)
			btn.removeNode()
			self.pickablesDrawn.pop(i)
		self.Game.Discover.initiator.discoverDecided(self.discover, info)
		self.discover = None
		
	def mouseMove(self, task):
		if self.mouseWatcherNode.hasMouse():
			mpos = self.mouseWatcherNode.getMouse()
			self.raySolid.setFromLens(self.camNode, mpos.getX(), mpos.getY())
			if self.btnBeingDragged: self.dragCard()
			if self.collHandler.getNumEntries() > 0:
				self.collHandler.sortEntries()
				collNode_Picked = self.collHandler.getEntry(0).getIntoNodePath()
				pickedModel_NodePath = collNode_Picked.getParent()
				nodePath_Picked = next((model_NodePath for model_NodePath in self.pickablesDrawn \
										if model_NodePath == pickedModel_NodePath), None)
				if nodePath_Picked:
					if not self.btnBeingDragged: nodePath_Picked.mouseHoveringOver()
			else: self.removeCardSpecsDisplay()
		return Task.cont
	
	def drawCardSpecsDisplay(self, btn):
		if not btn.card or (btn.card.type == "Hero" and btn.card.onBoard):
			if self.nodePath_CardSpecsDisplay: self.nodePath_CardSpecsDisplay.removeNode()
			self.nodePath_CardSpecsDisplay = None
		else: #btn是一个牌的按键
			if self.nodePath_CardSpecsDisplay:
				if self.nodePath_CardSpecsDisplay.card != btn.card: #Need to change the card displayed
					self.nodePath_CardSpecsDisplay.removeNode()
					self.nodePath_CardSpecsDisplay = loadCard(self, btn.card, pickable=False)
					if btn.card.onBoard: pos = Point3(15 if btn.pos[0] >= 0 else -15, btn.pos[1] - 2, 6 if btn.pos[2] >= 0 else -6)
					else: pos = Point3(btn.pos[0], btn.pos[1] - 5, 0.35 * btn.pos[2])
					self.nodePath_CardSpecsDisplay.setPos(pos)
					if btn.card.type == "Power": print("Plotting specs at pos", pos)
				#If the card specs displayed already is the new card we want to draw
			else: #No previous displayed card
				self.nodePath_CardSpecsDisplay = loadCard(self, btn.card, pickable=False)
				if btn.card.onBoard: pos = Point3(15 if btn.pos[0] >= 0 else -15, btn.pos[1] - 2, 6 if btn.pos[2] >= 0 else -6)
				else: pos = Point3(btn.pos[0], btn.pos[1] - 5, 0.35 * btn.pos[2])
				self.nodePath_CardSpecsDisplay.setPos(pos)
				if btn.card.type == "Power": print("Plotting specs at pos", pos)
				
	def removeCardSpecsDisplay(self):
		if self.nodePath_CardSpecsDisplay:
			self.nodePath_CardSpecsDisplay.removeNode()
			self.nodePath_CardSpecsDisplay = None
			
	def dragCard(self):
		self.btnBeingDragged.collNode.removeNode()
		#Decide the new position of the btn being dragged
		vec_X, vec_Y, vec_Z = self.raySolid.getDirection()
		y = self.btnBeingDragged.pos[1]
		x, z = vec_X * y / vec_Y, vec_Z * y / vec_Y
		self.btnBeingDragged.setPos(x, y, z)
		self.btnBeingDragged.setHpr(0, 0, 0)
		card = self.btnBeingDragged.card
		if card.type == "Minion":
			boardZone = self.boardZones[card.ID]
			boardSize = len(boardZone.btnsDrawn)
			leftPos = boardZone.x - Separation_Minions * boardSize / 2
			if -6 > z or z > 6: #Minion away from the center board, the minions won't shift
				posMinions = {boardZone.btnsDrawn[i]: (leftPos + Separation_Minions * i, boardZone.y, boardZone.z) for i in range(boardSize)}
				self.pos = -1
			elif boardZone.z - 3.8 < z < boardZone.z + 3.8:
				#Recalculate the positions and rearrange the minion btns
				if x < boardZone.btnsDrawn[0].pos[0]: #If placed leftmost, all current minion shift right
					posMinions = {boardZone.btnsDrawn[i]: (leftPos + Separation_Minions * (i + 1), boardZone.y, boardZone.z) for i in range(boardSize)}
					self.pos = 0
				elif x < boardZone.btnsDrawn[-1].pos[0]:
					ind = next((i + 1 for i, btn in enumerate(boardZone.btnsDrawn[:-1]) if btn.pos[0] < x < boardZone.btnsDrawn[i+1].pos[0]), -1)
					if ind > -1:
						posMinions = {boardZone.btnsDrawn[i]: (leftPos + Separation_Minions * (i + (i >= ind)), boardZone.y, boardZone.z) for i in range(boardSize)}
						self.pos = ind
					else: return #If failed to find
				else:
					posMinions = {boardZone.btnsDrawn[i]: (leftPos + Separation_Minions * i, boardZone.y, boardZone.z) for i in range(boardSize)}
					self.pos = -1
			else: #The minion is dragged beyond this side of the board
				posMinions = {boardZone.btnsDrawn[i]: (leftPos + Separation_Minions * i, boardZone.y, boardZone.z) for i in range(boardSize)}
				self.pos = -1
			para_MoveCards = Parallel(name="Move Minions")
			for btn, pos in posMinions.items():
				para_MoveCards.append(btn.genMoveIntervals(pos, hpr=Point3(), duration=0.2)[0])
			para_MoveCards.start()
		#else: #If the card requires target, then draw an arrow
		return Task.cont
	
	def stopDraggingCard(self):
		btn = self.btnBeingDragged
		if btn:
			print("Stop dragging btn", btn)
			btn.collNode = btn.attachNewNode(btn.collNode_Backup)
			btn.setPos(btn.pos)
			btn.setHpr(btn.hpr)
			self.btnBeingDragged = None
		for ID in range(1, 3):
			self.boardZones[ID].draw()
			self.boardZones[ID].draw()
	
	"""Animation setup"""
	def addCard(self, card, pos, hpr=Point3(), scale=0.6):
		nodePath_Card = loadCard(self, card=card)
		nodePath_Card.setPos(pos)
		nodePath_Card.setHpr(hpr)
		nodePath_Card.pos, nodePath_Card.hpr = pos, hpr
		nodePath_Card.setScale(scale)
		self.pickablesDrawn.append(nodePath_Card)
		return nodePath_Card
	
	def update(self):
		if self.UI == -2:
			pass
		else:
			if self.UI == 1:
				pass
			else:
				for ID in range(1, 3):
					self.handZones[ID].draw()
					self.heroZones[ID].draw()
					self.heroZones[ID].drawMana()
	
	def removeCard(self, btn):
		btn.removeNode()
		if btn in self.pickablesDrawn:
			return self.pickablesDrawn.pop(self.pickablesDrawn.index(btn))
		else: return None
	
	def resetCardColors(self):
		for btn in self.pickablesDrawn:
			btn.setColor("white")
	
	def highlightTargets(self, legalTargets):
		print("Legal targets", legalTargets)
		for btn in self.pickablesDrawn:
			if btn.card not in legalTargets: btn.dimDown()
	
	def cardEntersHandAni_1(self, card):
		handZone = self.handZones[card.ID]
		return handZone.addCard(card, (0, handZone.y, 0))
	
	def cardEntersHandAni_2(self, btn, i, steps):  #Add the card to the correct pos in handZone btnsDrawn
		pass  #self.handZones[btn.card.ID].draw()
	
	def cardReplacedinHand_Refresh(self):
		self.handZones[1].draw()
		self.handZones[2].draw()
	
	def startNewIntervals(self):
		if self.intervalInfos:
			self.intervalInfos.pop(0)[0].start()
	
	#Can be sequence too
	def tryInitIntervals(self, parallel, nextWaitTime=0):
		#print(parallel.ivals) #可以返回所有的intervalInfos
		#print("Current intervals")
		#for interval, waitTime in self.intervalInfos:
		#	print(interval.ivals)
		#	for ival in interval.ivals:
		#		if isinstance(ival, Func) and ival.function == self.startNewIntervals:
		#			print("yes")
		#	#if Func(self.startNewIntervals) in interval.ivals: print('yes')
		if not self.intervalInfos:  #第一个sequence需要能够把自己从self.intervalInfos里面摘掉
			sequence = Sequence(parallel, Func(lambda: self.intervalInfos.pop(0)), Func(self.startNewIntervals))
			self.intervalInfos.append((sequence, nextWaitTime))
			sequence.start()
		else: #之后加入的intervals都需要参看上一个的设置nextWaitTime，如果不需要等待，则并入上一个
			#lastSequence, lastWaitTime = self.intervalInfos[-1]
			#if lastWaitTime > 10:
			#	self.intervalInfos.append(Sequence(parallel, Func(self.startNewIntervals), name="Seq"+str(time.time())))
			#elif lastWaitTime > 0:
			#	self.intervalInfos.pop()
			#
			newSequence = Sequence(parallel, Func(self.startNewIntervals))
			self.intervalInfos.append((newSequence, nextWaitTime))
			
	def drawCardAni_1(self, card):
		#print("Drawing by player ", card.ID)
		deckZone = self.deckZones[card.ID]
		pos_Pause = Point3(0.5 * deckZone.x, deckZone.y - 15, 0.2 * deckZone.z)
		btn = self.handZones[card.ID].addCard(card, Point3(deckZone.x, deckZone.y - 2, deckZone.z), hpr=(180, 0, 0))
		
		posInterval, hprInterval = btn.genMoveIntervals(pos_Pause, duration=0.4)
		self.tryInitIntervals(Sequence(Parallel(posInterval, hprInterval), Wait(0.5), name="Draw Card Stage 1"))
		#print("Draw stage 1 HandZone btnsDrawn", self.handZones[card.ID].btnsDrawn)
		return btn
	
	def drawCardAni_2(self, btn, newCard):
		handZone = self.handZones[btn.card.ID]
		#print("Draw stage 2 HandZone btnsDrawn", handZone.btnsDrawn)
		if btn.card != newCard:
			pos = btn.pos
			handZone.removeCard(btn)
			btn = handZone.addCard(newCard, pos)
		#time.sleep(0.5)
		handZone.draw()
	
	def showTempText(self, text):
		sansBold = self.loader.loadFont('Models\\OpenSans-Bold.ttf')
		text = OnscreenText(text=text, pos=(0, 0), scale=0.1, fg=(1, 0, 0, 1),
							align=TextNode.ACenter, mayChange=1, font=sansBold,
							bg=(0.5, 0.5, 0.5, 0.8))
		self.tryInitIntervals(Sequence(Wait(1.5), Func(text.destroy)))
	
	def wait(self, time=0):
		pass
	
	def displayCard(self, card, notSecretBeingPlayed=True):
		pass
	
	def trigBlink(self, entity, color="yellow"):
		btn = next((btn for btn in self.pickablesDrawn if btn.card == entity), None)
		if btn:
			self.tryInitIntervals(Sequence(Func(btn.setColor("yellow")), Wait(0.5), Func(btn.setColor("white"))))
		
	def showOffBoardTrig(self, card, linger=True):
		if card:
			heroZone = self.heroZones[card.ID]
			nodePath_Card = loadCard(self, card=card, pickable=False)
			pos_Start, pos_End = Point3(heroZone.x, heroZone.y - 1, heroZone.z), Point3(-6, 25, 0)
			nodePath_Card.setPos(pos_Start)
			nodePath_Card.setScale(self.handZones[card.ID].cardScale)
			nodePath_Card.pos = pos_Start
			posInterval, hprInterval = nodePath_Card.genMoveIntervals(pos_End, duration=0.1)
			self.tryInitIntervals(Sequence(posInterval, Wait(0.5), Func(nodePath_Card.removeNode)))
	
	def eraseOffBoardTrig(self, ID):
		pass
	
	def attackAni(self, subject, target=None):
		btn_Subject = next(btn for btn in self.pickablesDrawn if btn.card == subject)
		if target:
			btn_Target = next(btn for btn in self.pickablesDrawn if btn.card == target)
			pos, hpr = btn_Target.pos, Point3(0, -30, 0)
			pos_Orig, hpr_Orig = btn_Subject.pos, Point3(0, 0, 0)
			posInterval, hprInterval = btn_Subject.genMoveIntervals(pos, hpr=hpr, duration=0.2)
			self.tryInitIntervals(Parallel(posInterval, hprInterval, name="Attack Forward Ani"))
			posInterval, hprInterval = btn_Subject.genMoveIntervals(pos_Orig, hpr=hpr, duration=0.15)
			self.tryInitIntervals(Parallel(posInterval, hprInterval, name="Attack Retreat Ani 1"))
			posInterval, hprInterval = btn_Subject.genMoveIntervals(Point3(btn_Subject.pos[0], btn_Subject.pos[1]+5, btn_Subject.pos[2]), hpr=hpr, duration=0.1)
			self.tryInitIntervals(Parallel(posInterval, hprInterval, name="Attack Retreat Ani 2"))
		else:
			posInterval, hprInterval = btn_Subject.genMoveIntervals(Point3(btn_Subject.pos[0], btn_Subject.pos[1]-5, btn_Subject.pos[2]), duration=0.3)
			self.tryInitIntervals(Sequence(posInterval, Wait(0.15), name="Attack Init Ani"))
		
	def cancelAttack(self, subject):
		btn_Subject = next(btn for btn in self.pickablesDrawn if btn.card == subject)
		posInterval, hprInterval = btn_Subject.genMoveIntervals(Point3(btn_Subject.pos[0], btn_Subject.pos[1] + 5, btn_Subject.pos[2]), duration=0.4)
		self.tryInitIntervals(Sequence(posInterval, name="Attack Init Ani"))
	
	def millCardAni(self, card):
		self.drawCardAni_1(card)
		
	def fatigueAni(self, ID, damage):
		pass
	
	def cardsLeaveHandAni(self, cards, enemyCanSee=True):
		if not isinstance(cards, (list, tuple)): cards = [cards]
		btnsDrawn = self.handZones[cards[0].ID].btnsDrawn
		para_CardsLeaveHand = Parallel(name="Parallel Cards Leave Hand")
		for card in cards:
			for btn in btnsDrawn:
				if btn.card == card:
					print("Animating card that leaves hand", btn.card)
					btn.setHpr(Point3(0, 0, 0))
					btn.hpr = Point3(0, 0, 0)
					print("Btn leaving hand, moving to", btn.pos)
					posInterval, hprInterval = btn.genMoveIntervals(Point3(btn.pos[0], btn.pos[1]-20, 0.5*btn.pos[2]))
					para_CardsLeaveHand.append(posInterval)
					para_CardsLeaveHand.append(hprInterval)
					break
		self.tryInitIntervals(Sequence(para_CardsLeaveHand, Wait(0.3), name="Sequence Cards Leaves Hand"))
		
	def cardLeavesDeckAni(self, card, enemyCanSee=True):
		pass
	
	def shuffleintoDeckAni(self, cards, enemyCanSee=True):
		pass
	
	def targetingEffectAni(self, subject, target, num, color="red"):
		pass
	
	def AOEAni(self, subject, targets, numbers, color="red"):
		pass
	
	def sendEndTurnthruServer(self):
		pass
	
	def sendOwnMovethruServer(self):
		pass
	
GUI_IP().run()