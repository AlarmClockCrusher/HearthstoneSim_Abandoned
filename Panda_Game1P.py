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
					"Hero 1 class": "玩家1职业",
					"Hero 2 class": "玩家2职业",
					"Enter Deck 1 code": "玩家1套牌",
					"Enter Deck 2 code": "玩家2套牌",
					"Deck 1 incorrect": "玩家1的套牌代码有误",
					"Deck 2 incorrect": "玩家2的套牌代码有误",
					"Deck 1&2 incorrect": "玩家1与玩家2的套牌代码均有误",
					"Finished Loading. Start!": "加载完成，可以开始",
				  }

def txt(text, CHN):
	if CHN: pass
	try: return translateTable[text]
	except: return text
	#if CHN:
	#	try: return translateTable[text]
	#	except: return text
	#return text

class Layer1Window:
	def __init__(self):
		self.window = tk.Tk()
		self.btn_Connect = tk.Button(self.window, text=txt("Loading. Please wait", CHN), bg="red",
									 font=("Yahei", 20, "bold"), command=self.init_ShowBase)
		self.btn_Reconn = None
		self.lbl_LoadingProgress = tk.Label(master=self.window, text='', font=("Yahei", 15))
		
		self.gameGUI = GUI_1P(self)
		threading.Thread(target=self.gameGUI.preload).start()
		
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
		
		self.entry_Deck1 = tk.Entry(self.window, font=("Yahei", 13), width=30)
		self.entry_Deck2 = tk.Entry(self.window, font=("Yahei", 13), width=30)
		
		"""Place the widgets"""
		lbl_SelectBoard.grid(row=0, column=0)
		boardOpt.grid(row=1, column=0)
		self.btn_Connect.grid(row=2, column=0)
		self.lbl_LoadingProgress.grid(row=3, column=0)
		
		tk.Label(self.window, text="         ").grid(row=0, column=1)
		
		tk.Label(self.window, text=txt("Hero 1 class", CHN),
				 font=("Yahei", 16)).grid(row=0, column=2)
		hero1_Opt.grid(row=0, column=3)
		tk.Label(self.window, text=txt("Hero 2 class", CHN),
				 font=("Yahei", 16)).grid(row=0, column=4)
		hero2_Opt.grid(row=0, column=5)
		
		tk.Label(self.window, text=txt("Enter Deck 1 code", CHN),
				 font=("Yahei", 16)).grid(row=1, column=2)
		self.entry_Deck1.grid(row=1, column=3)
		tk.Label(self.window, text=txt("Enter Deck 2 code", CHN),
				 font=("Yahei", 16)).grid(row=1, column=4)
		self.entry_Deck2.grid(row=1, column=5)
		
		self.lbl_DisplayedCard = tk.Label(self.window)
		self.lbl_DisplayedCard.grid(row=4, column=0)
		
		panel_DeckComp1 = tk.Frame(self.window)
		panel_DeckComp2 = tk.Frame(self.window)
		panel_DeckComp1.grid(row=2, column=2, rowspan=2, columnspan=2)
		panel_DeckComp2.grid(row=2, column=4, rowspan=2, columnspan=2)
		self.lbl_Types1 = tk.Label(panel_DeckComp1, text=("Minion:0\nSpell:0\nWeapon:0\nHero:0\nAmulet:0"), font=("Yahei", 16, "bold"), anchor='e')
		self.lbl_Types2 = tk.Label(panel_DeckComp2, text=("Minion:0\nSpell:0\nWeapon:0\nHero:0\nAmulet:0"), font=("Yahei", 16, "bold"), anchor='e')
		self.canvas_ManaDistri1 = tk.Canvas(panel_DeckComp1, width=250, height=120)
		self.canvas_ManaDistri2 = tk.Canvas(panel_DeckComp2, width=250, height=120)
		self.manaObjsDrawn1, self.manaObjsDrawn2 = [], []
		self.ls_LabelCards1, self.ls_LabelCards2 = [], []
		self.lbl_Types1.grid(row=0, column=0)
		self.lbl_Types2.grid(row=0, column=0)
		self.canvas_ManaDistri1.grid(row=0, column=1)
		self.canvas_ManaDistri2.grid(row=0, column=1)
		for mana in range(8):
			X, Y = (0.125 + 0.1 * mana) * manaDistriWidth, 0.95 * manaDistriHeight
			self.canvas_ManaDistri1.create_text(X, Y, text=str(mana) if mana < 7 else "7+", font=("Yahei", 12, "bold"))
			self.canvas_ManaDistri2.create_text(X, Y, text=str(mana) if mana < 7 else "7+", font=("Yahei", 12, "bold"))
			
		self.panel_Deck1 = tk.Frame(self.window)
		self.panel_Deck2 = tk.Frame(self.window)
		self.panel_Deck1.grid(row=4, column=2, rowspan=2, columnspan=2)
		self.panel_Deck2.grid(row=4, column=4, rowspan=2, columnspan=2)
		from Hand import Default1, Default2
		self.deck1, self.deck2 = Default1, Default2
		self.updateDeckComp()
		
		self.window.mainloop()
		
	def updateDeckComp(self):
		for lbl, deck, manaObjsDrawn, canvas, ls_Labels, panelDeck \
				in zip((self.lbl_Types1, self.lbl_Types2),
						(self.deck1, self.deck2),
						(self.manaObjsDrawn1, self.manaObjsDrawn2),
						(self.canvas_ManaDistri1, self.canvas_ManaDistri2),
						(self.ls_LabelCards1, self.ls_LabelCards2),
						(self.panel_Deck1, self.panel_Deck2)
						):
			cardTypes = {"Minion": 0, "Spell": 0, "Weapon": 0, "Hero": 0, "Amulet": 0}
			for lbl in ls_Labels: lbl.destroy()
			ls_Labels.clear()
			indices = np.array([card.mana for card in deck]).argsort()
			for i, index in enumerate(indices):
				card = deck[index]
				label = Label_Card(master=panelDeck, UI=self, card=card)
				label.grid(row=i%15, column=int(i / 15))
				ls_Labels.append(label)
				if issubclass(card, Minion): cardTypes["Minion"] += 1
				elif issubclass(card, Spell): cardTypes["Spell"] += 1
				elif issubclass(card, Weapon): cardTypes["Weapon"] += 1
				elif issubclass(card, Hero): cardTypes["Hero"] += 1
			lbl["text"] = "Minion: %d\nSpell: %d\nWeapon: %d\nHero: %d\nAmulet: %d" % (
							cardTypes["Minion"], cardTypes["Spell"], cardTypes["Weapon"], cardTypes["Hero"], cardTypes["Amulet"])
			for objID in manaObjsDrawn: canvas.delete(objID)
			manaObjsDrawn.clear()
	
			counts = cnt((min(card.mana, 7) for card in deck))
			most = max(list(counts.values()))
			for key, value in counts.items():
				if value:
					X1, X2 = (0.1 + 0.1 * key) * manaDistriWidth, (0.15 + 0.1 * key) * manaDistriWidth
					Y1, Y2 = (0.88 - 0.75 * (value / most)) * manaDistriHeight, 0.88 * manaDistriHeight
					manaObjsDrawn.append(canvas.create_rectangle(X1, Y1, X2, Y2, fill='gold', width=0))
					manaObjsDrawn.append(canvas.create_text((X1 + X2) / 2, Y1 - 0.06 * manaDistriHeight, text=str(value), font=("Yahei", 12, "bold")))
			
	def displayCardImg(self, card):
		img = PIL.Image.open(findFilepath(card(None, 1)))
		ph = PIL.ImageTk.PhotoImage(img)
		self.lbl_DisplayedCard.config(image=ph)
		self.lbl_DisplayedCard.image = ph
		
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

	def showDeckComposition(self):
		pass
	
	
class Label_Card(tk.Label):
	def __init__(self, master, UI, card):
		super().__init__(master=master, text="%d  "%card.mana+card.name_CN,
						 font=("Yahei", 15, "bold") if issubclass(card, Minion) else ("Yahei", 15))
		self.card = card
		if "~Legendary" in card.index: self.config(bg="yellow")
		self.UI = UI
		self.bind("<Enter>", self.show)
	
	def show(self, event):
		self.UI.displayCardImg(self.card)
		
		
configVars = """
win-size 1620 900
window-title Single Player Hearthstone Simulator
clock-mode limited
clock-frame-rate 45
text-use-harfbuzz true
"""

loadPrcFileData('', configVars)


class GUI_1P(Panda_UICommon):
	def __init__(self, layer1Window):
		super().__init__()
		self.layer1Window = layer1Window
		
	def preload(self):
		#Load the models
		super().prepareTexturesandModels(self.layer1Window)
		print("Finished loading")
		self.loading = "Start!"
		self.layer1Window.btn_Connect.config(text=txt("Finished Loading. Start!", CHN))
		self.layer1Window.btn_Connect.config(bg="green3")
	
	def initMulliganDisplay(self):
		self.handZones = {1: HandZone(self, 1), 2: HandZone(self, 2)}
		self.minionZones = {1: MinionZone(self, 1), 2: MinionZone(self, 2)}
		self.heroZones = {1: HeroZone(self, 1), 2: HeroZone(self, 2)}
		self.deckZones = {1: DeckZone(self, 1), 2: DeckZone(self, 2)}
		
		self.initGameDisplay()
		#threading.Thread(target=self.initGameDisplay).start()
		btn_Mulligan = DirectButton(text=("Confirm", "Confirm", "Confirm", "Confirm"), scale=0.08,
									command=self.mulligan_PreProcess)
		
		self.posMulligans = {1: [(-7, -10, -2.5), (0, -10, -2.5), (7, -10, -2.5)],
							 2: [(-8.25, -10, 6), (-2.75, -10, 6), (2.75, -10, 6), (8.25, -10, 6)]}
		for ID in range(1, 3):
			deckZone, handZone, i = self.deckZones[ID], self.handZones[ID], 0
			pos_0, hpr_0 = deckZone.pos, (90, 0, -90)
			cards2Mulligan = self.Game.mulligans[ID]
			mulliganBtns = handZone.addHands(cards2Mulligan, [pos_0] * len(cards2Mulligan), [hpr_0] * len(cards2Mulligan), [0.9] * len(cards2Mulligan))
			for btn, pos in zip(mulliganBtns, self.posMulligans[ID]):
				Sequence(Wait(0.4 + i * 0.4), btn.genLerpInterval(pos=pos, hpr=(0, 0, 0), scale=1, duration=0.5)).start()
				i += 1
			
		btn_Mulligan["extraArgs"] = [btn_Mulligan]
		btn_Mulligan.setPos(0, 0, 0)
		self.taskMgr.add(self.mouseMove, "Task_MoveCard")
	
	def mulligan_PreProcess(self, btn_Mulligan):
		self.UI = 0
		btn_Mulligan.destroy()
		
		indices1 = [i for i, status in enumerate(self.mulliganStatus[1]) if status]
		indices2 = [i for i, status in enumerate(self.mulliganStatus[2]) if status]
		self.handZones[1].removeHands([self.Game.mulligans[1][i].btn for i in indices1])
		self.handZones[2].removeHands([self.Game.mulligans[2][i].btn for i in indices2])
		print("After removal of mulligans, the cards 1 are", self.Game.mulligans[1])
		print("btns 1", [card.btn for card in self.Game.mulligans[1]])
		print("After removal of mulligans, the cards 2 are", self.Game.mulligans[2])
		print("btns 2", [card.btn for card in self.Game.mulligans[2]])
		
		#直到目前为止不用创建需要等待的sequence
		self.Game.Hand_Deck.mulliganBoth(indices1, indices2)
		
	#Returns a sequence to be started later
	def mulligan_NewCardsfromDeckAni(self, addCoin=True):
		#At this point, the Coin is added to the Game.mulligans[2]
		if addCoin:
			self.handZones[2].addHands([self.Game.mulligans[2][-1]], [(13.75, -10, 6)])
		
		#开始需要生成一个Sequence，然后存储在seqHolder里面
		para = Parallel()
		for ID in range(1, 3):
			deckZone, handZone = self.deckZones[ID], self.handZones[ID]
			pos_DeckZone, hpr_0 = deckZone.pos, (90, 0, -90)
			indices, cards2Mulligan = [], []
			for i, card in enumerate(self.Game.mulligans[ID]):
				if not card.btn:
					indices.append(i)
					cards2Mulligan.append(card)
					
			mulliganBtns = handZone.addHands(cards2Mulligan, [pos_DeckZone] * len(cards2Mulligan), [hpr_0] * len(cards2Mulligan), [0.9] * len(cards2Mulligan))
			for btn, i in zip(mulliganBtns, indices):
				para.append(btn.genLerpInterval(pos=self.posMulligans[ID][i], hpr=(0, 0, 0), scale=1, duration=0.5))
			
		#已经把所有新从牌库里面出来的牌画在了牌库里面
		self.seqHolder = [Sequence(para, Wait(1))]
		#return Sequence(para, Wait(1))
		
	def mulligan_MoveCards2Hand(self):
		#此段不涉及动画和nodepath的生成
		cardsChanged, cardsNew = [], []
		handZone_1, handZone_2 = self.handZones[1], self.handZones[2]
		for ID, handZone in zip(range(1, 3), (handZone_1, handZone_2)):
			ls_Hands = self.Game.Hand_Deck.hands[ID]
			for i, card in enumerate(self.Game.mulligans[ID]):
				newCard = card.entersHand()
				if newCard is not card:
					cardsChanged.append(card)
					cardsNew.append(newCard)
				ls_Hands.append(newCard)
			self.Game.mulligans[ID] = []
		
		#此时，手牌和牌库中的牌已经决定完毕（包括进入手牌会变形的牌）。需要变形的牌直接在调度区完成变形，然后移到手牌区的位置
		sequence = self.seqHolder[0]
		if cardsChanged: #把btn变形
			sequence.append(Func(handZone_1.transformHands([card.btn for card in cardsChanged], cardsNew)))
			sequence.append(Wait(1))
		sequence.append(Parallel(Func(handZone_1.placeCards), Func(handZone_2.placeCards)))


"""Run the game"""
Layer1Window()