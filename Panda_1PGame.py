from Code2CardList import *
from Game import *
from GenPools_BuildDecks import *
from Panda_CustomWidgets import *

from datetime import datetime

import tkinter as tk
from tkinter import messagebox

from Panda_UICommonPart import *


class Layer1Window:
	def __init__(self, gameGUI=None):
		self.window = tk.Tk()
		np.random.seed(datetime.now().microsecond)
		firstTime = not gameGUI and 1 #make sure gameGui is boolean
		self.btn_Connect = tk.Button(self.window, text=txt("Loading. Please wait", CHN), bg="red", font=("Yahei", 20, "bold"),
									 command=lambda : self.init_ShowBase(firstTime))
		self.btn_Reconn = None
		self.lbl_LoadingProgress = tk.Label(master=self.window, text='', font=("Yahei", 15))
		
		if gameGUI:
			gameGUI.layer1Window = self
			self.gameGUI = gameGUI
			game = Game(gameGUI)
			game.mode = 0
			game.initialize()
			self.gameGUI.Game = game
			#Set the lbls and btns to correct display
			self.lbl_LoadingProgress.config(text=txt("Finished Loading. Start!", CHN), fg="green3")
			self.loading = "Start!"
			self.btn_Connect.config(text=txt("Finished Loading. Start!", CHN), bg="green3")
		else:
			self.gameGUI = GUI_1P(self) #一般而言，gameGUI携带的Game会在这里定义
			threading.Thread(target=self.gameGUI.preload, daemon=True).start()
		
		"""Create the hero class selection menu"""
		self.hero1Class = self.hero2Class = "Demon Hunter"
		self.panel_Class1 = Panel_ClassSelection(master=self.window, UI=self, ClassPool=list(Class2HeroDict.keys()),
												Class_0="Demon Hunter", varName="hero1Class")
		self.panel_Class2 = Panel_ClassSelection(master=self.window, UI=self, ClassPool=list(Class2HeroDict.keys()),
							 Class_0="Demon Hunter", varName="hero2Class")
		self.panel_Class1.grid(row=0, column=3)
		self.panel_Class2.grid(row=0, column=6)
		self.entry_Deck1 = tk.Entry(self.window, font=("Yahei", 13), width=30)
		self.entry_Deck2 = tk.Entry(self.window, font=("Yahei", 13), width=30)
		
		"""Place the widgets"""
		self.btn_Connect.grid(row=2, column=0)
		self.lbl_LoadingProgress.grid(row=3, column=0)
		
		tk.Label(self.window, text="         ").grid(row=0, column=1)
		
		tk.Label(self.window, text=txt("Hero 1", CHN),
				 font=("Yahei", 16)).grid(row=0, column=2)
		tk.Label(self.window, text=txt("Hero 2", CHN),
				 font=("Yahei", 16)).grid(row=0, column=5)
		
		tk.Label(self.window, text=txt("Enter Deck 1 code", CHN),
				 font=("Yahei", 16)).grid(row=1, column=2)
		tk.Label(self.window, text=txt("Enter Deck 2 code", CHN),
				 font=("Yahei", 16)).grid(row=1, column=5)
		self.entry_Deck1.grid(row=1, column=3)
		self.entry_Deck2.grid(row=1, column=6)
		
		self.lbl_DisplayedCard = tk.Label(self.window)
		self.lbl_DisplayedCard.grid(row=4, column=0)
		
		panel_DeckComp1 = tk.Frame(self.window)
		panel_DeckComp2 = tk.Frame(self.window)
		panel_DeckComp1.grid(row=2, column=2, rowspan=2, columnspan=2)
		panel_DeckComp2.grid(row=2, column=5, rowspan=2, columnspan=2)
		self.lbl_Types1 = tk.Label(panel_DeckComp1, text="Total:0\n\nMinion:0\nSpell:0\nWeapon:0\nHero:0\nAmulet:0", font=("Yahei", 16, "bold"), anchor='e')
		self.lbl_Types2 = tk.Label(panel_DeckComp2, text="Total:0\n\nMinion:0\nSpell:0\nWeapon:0\nHero:0\nAmulet:0", font=("Yahei", 16, "bold"), anchor='e')
		self.canvas_ManaDistri1 = tk.Canvas(panel_DeckComp1, width=250, height=120)
		self.canvas_ManaDistri2 = tk.Canvas(panel_DeckComp2, width=250, height=120)
		#Either pressing the button or hitting enter in the entries will refresh the deck composition
		btn_Refresh = tk.Button(self.window, text="刷新", font=("Yahei", 15, "bold"), bg="green3")
		btn_Refresh.bind("<Button-1>", self.updateDeckComp)
		btn_Refresh.grid(row=3, column=4)
		self.entry_Deck1.bind("<Return>", self.updateDeckComp)
		self.entry_Deck2.bind("<Return>", self.updateDeckComp)
		
		self.manaObjsDrawn1, self.manaObjsDrawn2 = [], []
		self.ls_LabelCardsinDeck1, self.ls_LabelCardsinDeck2 = [], []
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
		self.panel_Deck2.grid(row=4, column=5, rowspan=2, columnspan=2)
		
		from Hand import Default1, Default2
		self.deck1_0, self.deck2_0 = Default1, Default2
		self.deck1, self.deck2 = [], []
		self.updateDeckComp(None)
		
		self.window.mainloop()
		
	def updateDeckComp(self, event):
		makeCardPool(0, 0)
		#deck1&2 and hero1&2 parsing
		self.deck1, deckCorrect, hero = parseDeckCode(self.entry_Deck1.get(), self.hero1Class, Class2HeroDict, defaultDeck=self.deck1_0)
		if not deckCorrect: messagebox.showinfo(message=txt("Deck 1 incorrect", CHN))
		self.panel_Class1.setSelection(hero.Class)
		self.deck2, deckCorrect, hero = parseDeckCode(self.entry_Deck2.get(), self.hero2Class, Class2HeroDict, defaultDeck=self.deck2_0)
		if not deckCorrect: messagebox.showinfo(message=txt("Deck 2 incorrect", CHN))
		self.panel_Class2.setSelection(hero.Class)
		
		print("After parsing, the decks and heroes are:\n", self.deck1, "\n", self.deck2)
		for lbl, deck, manaObjsDrawn, canvas, ls_Labels, panelDeck \
				in zip((self.lbl_Types1, self.lbl_Types2),
						(self.deck1, self.deck2),
						(self.manaObjsDrawn1, self.manaObjsDrawn2),
						(self.canvas_ManaDistri1, self.canvas_ManaDistri2),
						(self.ls_LabelCardsinDeck1, self.ls_LabelCardsinDeck2),
						(self.panel_Deck1, self.panel_Deck2)
						):
			cardTypes = {"Minion": 0, "Spell": 0, "Weapon": 0, "Hero": 0, "Amulet": 0}
			for lbl_Card in ls_Labels: lbl_Card.destroy()
			ls_Labels.clear()
			indices = np.array([card.mana for card in deck]).argsort()
			for i, index in enumerate(indices):
				card = deck[index]
				label = Label_CardinDeck(master=panelDeck, UI=self, card=card)
				label.grid(row=i%15, column=int(i / 15))
				ls_Labels.append(label)
				cardTypes[card.type] += 1
				
			lbl["text"] = "Total:%d\n\nMinion: %d\nSpell: %d\nWeapon: %d\nHero: %d\nAmulet: %d" % (
								len(deck), cardTypes["Minion"], cardTypes["Spell"], cardTypes["Weapon"], cardTypes["Hero"], cardTypes["Amulet"])
			for objID in manaObjsDrawn: canvas.delete(objID)
			manaObjsDrawn.clear()
	
			counts = cnt((min(card.mana, 7) for card in deck))
			most = max(list(counts.values()))
			for mana, count in counts.items():
				if count:
					X1, X2 = (0.1 + 0.1 * mana) * manaDistriWidth, (0.15 + 0.1 * mana) * manaDistriWidth
					Y1, Y2 = (0.88 - 0.75 * (count / most)) * manaDistriHeight, 0.88 * manaDistriHeight
					manaObjsDrawn.append(canvas.create_rectangle(X1, Y1, X2, Y2, fill='gold', width=0))
					manaObjsDrawn.append(canvas.create_text((X1 + X2) / 2, Y1 - 0.06 * manaDistriHeight, text=str(count), font=("Yahei", 12, "bold")))
			
	def displayCardImg(self, card):
		ph = PIL.ImageTk.PhotoImage(PIL.Image.open(findFilepath(card(None, 1))))
		self.lbl_DisplayedCard.config(image=ph)
		self.lbl_DisplayedCard.image = ph
		
	def showCards(self):
		pass
	
	def removeCardfromDeck(self, card):
		pass
	
	def init_ShowBase(self, firstTime):
		print("Clicked connect")
		if self.gameGUI.loading != "Start!":
			return
		
		RNGPools = makeCardPool(0, 0)[1]
		heroes = {1: self.hero1Class, 2: self.hero2Class}
		deckStrings = {1: self.entry_Deck1.get(), 2: self.entry_Deck2.get()}
		decks, decksCorrect = {1: [], 2: []}, {1: False, 2: False}
		for ID in range(1, 3):
			decks[ID], decksCorrect[ID], heroes[ID] = parseDeckCode(deckStrings[ID], heroes[ID], Class2HeroDict,
																	defaultDeck=self.deck1_0 if ID == 1 else self.deck2_0)
		
		if decksCorrect[1] and decksCorrect[2]:
			seed = datetime.now().microsecond
			self.gameGUI.boardID = npchoice(boardPool)
			self.gameGUI.Game.initialize_Details(self.gameGUI.boardID, int(seed), RNGPools, heroes[1], heroes[2],
												 deck1=decks[1], deck2=decks[2])
			self.window.destroy()
			if not firstTime: self.gameGUI.clearDrawnCards()
			self.gameGUI.initMulliganDisplay(firstTime)
			"""If the same ShowBase cannot be run multiple times"""
			if firstTime: self.gameGUI.run()
		else:
			if not decksCorrect[1]:
				if decksCorrect[2]: messagebox.showinfo(message=txt("Deck 1 incorrect", CHN))
				else: messagebox.showinfo(message=txt("Both Deck 1&2 incorrect", CHN))
			else: messagebox.showinfo(message=txt("Deck 2 incorrect", CHN))

	def showDeckComposition(self):
		pass
	
	
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
		self.ID = 1
		self.btn_BacktoLayer1 = None
		
	def preload(self):
		#Load the models
		super().prepareTexturesandModels(self.layer1Window)
		print("Finished loading")
		self.loading = "Start!"
		self.layer1Window.btn_Connect.config(text=txt("Finished Loading. Start!", CHN))
		self.layer1Window.btn_Connect.config(bg="green3")
	
	def initMulliganDisplay(self, firstTime):
		self.handZones = {1: HandZone(self, 1), 2: HandZone(self, 2)}
		self.minionZones = {1: MinionZone(self, 1), 2: MinionZone(self, 2)}
		self.heroZones = {1: HeroZone(self, 1), 2: HeroZone(self, 2)}
		if not self.deckZones: self.deckZones = {1: DeckZone(self, 1), 2: DeckZone(self, 2)}
		
		self.mulliganStatus = {1: [0, 0, 0], 2: [0, 0, 0, 0]} #需要在每次退出和重新进入时刷新
		self.UI = -1
		self.initGameDisplay()
		
		self.btns2Remove.append(DirectButton(text=("Confirm", "Confirm", "Confirm", "Confirm"), scale=0.08,
											pos=(0, 0, 0), command=self.mulligan_PreProcess))
		
		#Draw the animation of mulligan cards coming out of the deck
		self.posMulligans = {1: [(-7, -3.3, 10), (0, -3.3, 10), (7, -3.3, 10)],
							 2: [(-8.25, 6, 10), (-2.75, 6, 10), (2.75, 6, 10), (8.25, 6, 10)]}
		for ID in range(1, 3):
			deckZone, handZone, i = self.deckZones[ID], self.handZones[ID], 0
			pos_0, hpr_0 = deckZone.pos, (90, 90, 0)
			cards2Mulligan = self.Game.mulligans[ID]
			mulliganBtns = []
			for card, pos, hpr, scale in zip(cards2Mulligan, [pos_0] * len(cards2Mulligan), [hpr_0] * len(cards2Mulligan), [1] * len(cards2Mulligan)):
				mulliganBtns.append(genCard(self, card, isPlayed=False, pos=pos, hpr=hpr, scale=scale)[1])
			for btn, pos in zip(mulliganBtns, self.posMulligans[ID]):
				Sequence(Wait(0.4 + i * 0.4), LerpPosHprScaleInterval(btn.np, duration=0.5, pos=pos, hpr=(0, 0, 0), scale=1)).start()
				i += 1
		
		for child in self.render.getChildren():
			if "2Keep" not in child.name:
				print("After initGame, Left in render:", child.name, type(child))
		
		if firstTime: self.taskMgr.add(self.mainTaskLoop, "Task_MainLoop")
		
	def mulligan_PreProcess(self):
		self.UI = 0
		for btn in self.btns2Remove: btn.destroy()
		self.btn_BacktoLayer1 = DirectButton(text=("Back", "Back", "Back", "Back"), scale=0.08, pos=(1.55, 0, -0.9),
											 command=self.back2Layer1)
		
		indices1 = [i for i, status in enumerate(self.mulliganStatus[1]) if status]
		indices2 = [i for i, status in enumerate(self.mulliganStatus[2]) if status]
		for i in indices1: self.Game.mulligans[1][i].btn.np.removeNode()
		for i in indices2: self.Game.mulligans[2][i].btn.np.removeNode()
		
		#直到目前为止不用创建需要等待的sequence
		self.Game.Hand_Deck.mulliganBoth(indices1, indices2)
		
	#Returns a sequence to be started later
	def mulligan_NewCardsfromDeckAni(self, addCoin=True):
		#At this point, the Coin is added to the Game.mulligans[2]
		if addCoin: genCard(self, card=self.Game.mulligans[2][-1], isPlayed=False, pos=(13.75, 6, 10))
		
		#开始需要生成一个Sequence，然后存储在seqHolder里面
		para = Parallel()
		for ID in range(1, 3):
			deckZone, handZone = self.deckZones[ID], self.handZones[ID]
			pos_DeckZone, hpr_0 = deckZone.pos, (90, 90, 0)
			indices, cards2Mulligan = [], []
			for i, card in enumerate(self.Game.mulligans[ID]):
				if not card.btn:
					indices.append(i)
					cards2Mulligan.append(card)
					
			mulliganBtns = []
			for card, pos, hpr, scale in zip(cards2Mulligan, [pos_DeckZone] * len(cards2Mulligan), [hpr_0] * len(cards2Mulligan), [1] * len(cards2Mulligan)):
				mulliganBtns.append(genCard(self, card, isPlayed=False, pos=pos, hpr=hpr, scale=scale)[1])
			for btn, i in zip(mulliganBtns, indices):
				para.append(LerpPosHprScaleInterval(btn.np, duration=0.5, pos=self.posMulligans[ID][i], hpr=(0, 0, 0), scale=1))
			
		#已经把所有新从牌库里面出来的牌画在了牌库里面
		self.seqHolder = [Sequence(para, Wait(1))]
		self.seqReady = False
		
	def mulligan_MoveCards2Hand(self):
		#此段不涉及动画和nodePath的生成
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
		sequence = self.seqHolder[-1]
		if cardsChanged: #把btn变形
			sequence.append(Func(handZone_1.transformHands([card.btn for card in cardsChanged], cardsNew)))
			sequence.append(Wait(1))
		handZone_1.placeCards()
		handZone_2.placeCards()
		
	def back2Layer1(self):
		print("Going back to layer1")
		for btn in self.btns2Remove: btn.destroy()
		self.btn_BacktoLayer1.destroy()
		self.UI = -2 #需要调成无响应状态
		self.msg_BacktoLayer1 = "Go Back to Layer 1"
		
	def restartLayer1Window(self):
		print("Current thread while restarting", threading.current_thread())
		Layer1Window(self)
		
"""Run the game"""
if __name__ == "__main__":
	Layer1Window()