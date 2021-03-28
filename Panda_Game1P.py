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
		self.btn_Connect = tk.Button(self.window, text=txt("Loading. Please wait", CHN), bg="red", font=("Yahei", 20, "bold"), command=self.init_ShowBase)
		self.btn_Reconn = None
		
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
		self.btn_Connect.grid(row=3, column=0)
		
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
	def preloadModel(self, btn_Connect, btn_Reconn):
		#Load the models
		self.prepareModels()
		btn_Connect.config(text=txt("Finished Loading. Start!", CHN))
		btn_Connect.config(bg="green3")
	
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