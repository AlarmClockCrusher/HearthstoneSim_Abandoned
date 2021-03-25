import math

from direct.gui.DirectGui import *
from direct.interval.IntervalGlobal import Wait, Func
from direct.showbase.ShowBase import ShowBase
from direct.task import Task

from Code2CardList import *
from Game import *
from GenerateRNGPools import *
from Panda_CustomWidgets import *

from datetime import datetime
from collections import deque

import tkinter as tk
from tkinter import messagebox

from Panda_UICommonPart import *


translateTable = {"Choose Game Board(Random by default)": "选择棋盘（默认为随机）",
				  	"Loading. Please wait":"正在加载模型，请等待",
					"Hero 1 class": "选择玩家1职业",
					"Hero 2 class": "选择玩家2职业",
					"Enter Deck 1 code": "输入玩家1的套牌代码",
					"Enter Deck 2 code": "输入玩家2的套牌代码",
					"Deck 1 incorrect": "玩家1的套牌代码有误",
					"Deck 2 incorrect": "玩家2的套牌代码有误",
					"Deck 1&2 incorrect": "玩家1与玩家2的套牌代码均有误",
					"Finished Loading. Start!": "加载完成，可以开始",
				  }

def txt(text, CHN):
	try: return translateTable[text]
	except: return text
	#if CHN:
	#	try: return translateTable[text]
	#	except: return text
	#return text

class Layer1Window:
	def __init__(self):
		self.window = tk.Tk()
		self.btn_Start = tk.Button(self.window, text=txt("Loading. Please wait", CHN), bg="red", font=("Yahei", 20, "bold"), command=self.init_ShowBase)
		
		self.gameGUI = GUI_IP(self)
		
		lbl_SelectBoard = tk.Label(master=self.window, text=txt("Choose Game Board(Random by default)", CHN), font=("Yahei", 20))
		self.boardID_Var = tk.StringVar(self.window)
		self.boardID_Var.set(BoardIndex[0])
		boardOpt = tk.OptionMenu(self.window, self.boardID_Var, *BoardIndex)
		boardOpt.config(width=20, font=("Yahei", 20))
		boardOpt["menu"].config(font=("Yahei", 20))
		
		"""Create the hero class selection menu"""
		self.hero1_Var = tk.StringVar(self.window)
		self.hero1_Var.set(list(ClassDict.keys())[0])
		hero1_Opt = tk.OptionMenu(self.window, self.hero1_Var, *list(ClassDict.keys()))
		hero1_Opt.config(width=15, font=("Yahei", 20))
		hero1_Opt["menu"].config(font=("Yahei", 20))
		
		self.hero2_Var = tk.StringVar(self.window)
		self.hero2_Var.set(list(ClassDict.keys())[0])
		hero2_Opt = tk.OptionMenu(self.window, self.hero2_Var, *list(ClassDict.keys()))
		hero2_Opt.config(width=15, font=("Yahei", 20))
		hero2_Opt["menu"].config(font=("Yahei", 20))
		
		self.deck1 = tk.Entry(self.window, font=("Yahei", 13), width=30)
		self.deck2 = tk.Entry(self.window, font=("Yahei", 13), width=30)
		
		"""Place the widgets"""
		lbl_SelectBoard.grid(row=0, column=0)
		boardOpt.grid(row=1, column=0)
		self.btn_Start.grid(row=3, column=0)
		
		tk.Label(self.window, text="         ").grid(row=0, column=1)
		tk.Label(self.window, text=txt("Hero 1 class", CHN),
				 font=("Yahei", 20)).grid(row=0, column=2)
		tk.Label(self.window, text=txt("Hero 2 class", CHN),
				 font=("Yahei", 20)).grid(row=1, column=2)
		hero1_Opt.grid(row=0, column=3)
		hero2_Opt.grid(row=1, column=3)
		
		tk.Label(self.window, text=txt("Enter Deck 1 code", CHN),
				 font=("Yahei", 20)).grid(row=3, column=2)
		tk.Label(self.window, text=txt("Enter Deck 2 code", CHN),
				 font=("Yahei", 20)).grid(row=4, column=2)
		self.deck1.grid(row=3, column=3)
		self.deck2.grid(row=4, column=3)
		
		self.window.mainloop()
	
	def init_ShowBase(self):
		if self.gameGUI.loading != "Start!":
			return
		
		boardID = makeCardPool(self.boardID_Var.get(), 0, 0)
		from CardPools import cardPool, MinionsofCost, ClassCards, NeutralCards, RNGPools
		
		hero1, hero2 = self.hero1_Var.get(), self.hero2_Var.get()
		deck1, deck2 = self.deck1.get(), self.deck2.get()
		heroes = {1: ClassDict[hero1], 2: ClassDict[hero2]}
		deckStrings = {1: deck1, 2: deck2}
		decks, decksCorrect = {1: [], 2: []}, {1: False, 2: False}
		
		for ID in range(1, 3):
			decks[ID], decksCorrect[ID], heroes[ID] = parseDeckCode(deckStrings[ID], heroes[ID], ClassDict)
		
		if decksCorrect[1] and decksCorrect[2]:
			self.gameGUI.boardID = boardID
			self.gameGUI.Game.initialize_Details(cardPool, ClassCards, NeutralCards, MinionsofCost, RNGPools, heroes[1], heroes[2], deck1=decks[1], deck2=decks[2])
			self.window.destroy()
			print("Before init mulligan display, threads are\n", threading.current_thread(), threading.enumerate())
			self.gameGUI.initMulliganDisplay()
			self.gameGUI.run()
		else:
			if not decksCorrect[1]:
				if decksCorrect[2]: messagebox.showinfo(message=txt("Deck 1 incorrect", CHN))
				else: messagebox.showinfo(message=txt("Both Deck 1&2 incorrect", CHN))
			else: messagebox.showinfo(message=txt("Deck 2 incorrect", CHN))



configVars = """
win-size 1620 900
window-title Single Player Hearthstone Simulator
clock-mode limited
clock-frame-rate 45
text-use-harfbuzz true
"""

loadPrcFileData('', configVars)


class GUI_IP(Panda_UICommon):
	def __init__(self, layer1Window):
		ShowBase.__init__(self)
		#simplepbr.init(max_lights=4)
		self.disableMouse()
		
		self.layer1Window = layer1Window
		self.UI = -2  #Starts at -2, for the mulligan stage
		self.pickablesDrawn = []
		self.board, self.btnTurnEnd = None, None
		self.mulliganStatus = {1: [0, 0, 0], 2: [0, 0, 0, 0]}
		#Attributes of the GUI
		self.selectedSubject = ""
		self.subject, self.target = None, None
		self.pos, self.choice, self.UI = -1, 0, -2  #起手调换为-2
		self.discover = None
		self.btnBeingDragged, self.arrow = None, None
		self.nodePath_CardSpecsDisplay = None
		self.intervalQueue = []
		self.intervalRunning = 0
		self.gamePlayQueue = []
		self.gamePlayThread = None
		#Flag whether the game is still loading models for the cards
		self.loading = "Loading. Please Wait"
		
		self.sansBold = self.loader.loadFont('Models\\OpenSans-Bold.ttf')
		
		self.cTrav = self.collHandler = self.raySolid = None
		self.accept("mouse1", self.mouse1_Down)
		self.accept("mouse1-up", self.mouse1_Up)
		self.accept("mouse3", self.mouse3_Down)
		self.accept("mouse3-up", self.mouse3_Up)
		
		thread_RunningAnimiations = threading.Thread(target=self.thread_AnimationManager, daemon=True)
		print("thread_RunningAnimations created", thread_RunningAnimiations)
		thread_RunningAnimiations.name = "AniManagerThread"
		thread_RunningAnimiations.start()
		self.gamePlayThread = threading.Thread(target=self.keepExecutingGamePlays, daemon=True)
		self.gamePlayThread.name = "GameThread"
		self.gamePlayThread.start()
		self.init_CollisionSetup()
		
		"""Prepare models that will be used later"""
		self.Game = Game(self)
		self.Game.mode = 0
		self.Game.Classes, self.Game.ClassesandNeutral = Classes, ClassesandNeutral
		self.Game.initialize()
		threading.Thread(target=self.preloadModel, args=(self.layer1Window.btn_Start,)).start()
	
	def preloadModel(self, btn_Start):
		#Load the models
		game = self.Game
		self.backupCardModels = {"Minion": deque([loadMinion(self, SilverHandRecruit(game, 1)) for i in range(30)]),
								 "Spell": deque([loadSpell(self, LightningBolt(game, 1)) for i in range(30)]),
								 "Weapon": deque([loadWeapon(self, FieryWarAxe(game, 1)) for i in range(30)]),
								 "Power": deque([loadPower(self, Reinforce(game, 1)) for i in range(10)]),
								 "Hero": deque([loadHero(self, LordJaraxxus(game, 1)) for i in range(30)]),
								 "Dormant": deque([loadDormant(self, BurningBladePortal(game, 1)) for i in range(2)]),
								 "MinionPlayed": deque([loadMinion_Played(self, SilverHandRecruit(game, 1)) for i in range(30)]),
								 "WeaponPlayed": deque([loadWeapon_Played(self, FieryWarAxe(game, 1)) for i in range(6)]),
								 "PowerPlayed": deque([loadPower_Played(self, Reinforce(game, 1)) for i in range(4)]),
								 "HeroPlayed": deque([loadHero_Played(self, Anduin(game, 1)) for i in range(6)]),
								 "SecretPlayed": deque([loadSecret_Played(self, FreezingTrap(game, 1)) for i in range(12)]),
								 "DormantPlayed": deque([loadDormant_Played(self, BurningBladePortal(game, 1)) for i in range(15)]),
								 "Mana": deque(), "EmptyMana": deque(), "LockedMana": deque(), "OverloadedMana": deque(),
								 "Option": deque([loadChooseOption(self, Cenarius(game, 1).options[0]) for i in range(4)]),
								 }
		self.loading = "Start!"
		btn_Start.config(text=txt("Finished Loading. Start!", CHN))
		btn_Start.config(bg="green3")
	
	def initMulliganDisplay(self):
		self.posMulligans = {1: [(8 * (i - 1), 50, -5) for i in range(len(self.Game.mulligans[1]))],
							 2: [(4 + 8 * (i - 2), 50, 5) for i in range(len(self.Game.mulligans[2]))]}
		mulliganBtns = []
		for i in range(1, 3):
			for pos, card in zip(self.posMulligans[i], self.Game.mulligans[i]):
				mulliganBtns.append(self.addinDisplayCard(card, pos, scale=0.7))
		
		btn_Mulligan = DirectButton(text=("Confirm", "Confirm", "Confirm", "Confirm"), scale=0.08,
									command=self.startMulligan)
		btn_Mulligan["extraArgs"] = [mulliganBtns, btn_Mulligan]
		btn_Mulligan.setPos(0, 0, 0)
		threading.Thread(target=self.initGameDisplay).start()
		self.taskMgr.add(self.mouseMove, "Task_MoveCard")
	
	def startMulligan(self, mulliganBtns, btn_Mulligan):
		self.UI = 0
		indices1 = [i for i, status in enumerate(self.mulliganStatus[1]) if status]
		indices2 = [i for i, status in enumerate(self.mulliganStatus[2]) if status]
		#self.GUI.gameBackup = self.GUI.Game.copyGame()[0]
		btn_Mulligan.destroy()
		for btn in mulliganBtns:
			self.removeBtn(btn)
		self.executeGamePlay(lambda: self.Game.Hand_Deck.mulligan(indices1, indices2))
	
	
"""Run the game"""
Layer1Window()