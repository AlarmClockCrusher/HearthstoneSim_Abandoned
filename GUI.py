import tkinter as tk
from tkinter import messagebox

from CustomWidgets import *
from UICommonPart import *
from Game import *
from Code2CardList import *
from GenerateRNGPools import *

CHN = True

class LoadDeckButton(tk.Button):
	def __init__(self, GUI):
		tk.Button.__init__(self, master=GUI.deckImportPanel, bg="green3", text=txt("Confirm", CHN), font=("Yahei", 15))
		self.GUI = GUI
		self.configure(command=self.respond)
		
	def respond(self):
		heroes = {1: ClassDict[self.GUI.hero1Label["text"].split(':')[-1]],
				2: ClassDict[self.GUI.hero2Label["text"].split(':')[-1]] }
		deckStrings = {1: self.GUI.deck1.get(), 2: self.GUI.deck2.get()}
		decks, decksCorrect = {1: [], 2: []}, {1: False, 2: False}
		for ID in range(1, 3):
			decks[ID], decksCorrect[ID], heroes[ID] = parseDeckCode(deckStrings[ID], heroes[ID], ClassDict)
		if decksCorrect[1] and decksCorrect[2]:
			self.GUI.Game = Game(self.GUI)
			self.GUI.Game.transferStudentType = self.GUI.transferStudentType
			self.GUI.deckImportPanel.destroy()
			for ID in range(1, 3):
				for i, card in enumerate(decks[ID]):
					if card.name == "Transfer Student": decks[ID][i] = self.GUI.transferStudentType
			self.GUI.Game.initialize(cardPool, ClassCards, NeutralCards, MinionsofCost, RNGPools, heroes[1], heroes[2], decks[1], decks[2])
			self.GUI.Game.mode = 0
			self.GUI.Game.Classes, self.GUI.Game.ClassesandNeutral = Classes, ClassesandNeutral
			self.GUI.posMulligans = {1:[(100+i*2*111, Y-140) for i in range(len(self.GUI.Game.mulligans[1]))],
								2:[(100+i*2*111, 140) for i in range(len(self.GUI.Game.mulligans[2]))]}
			self.destroy()
			self.GUI.initSidePanel()
			self.GUI.update()
		else:
			if not decksCorrect[1]: messagebox.showinfo(message=txt("Deck 1 incorrect", CHN))
			if not decksCorrect[2]: messagebox.showinfo(message=txt("Deck 2 incorrect", CHN))
			
			
class GUI_1P(GUI_Common):
	def __init__(self):
		self.mulliganStatus = {1:[0, 0, 0], 2:[0, 0, 0, 0]}
		self.selectedSubject = ""
		self.subject, self.target = None, None
		self.pos, self.choice, self.UI = -1, 0, -2 #起手调换为-2
		self.discover = None
		self.gameBackup = None
		self.btnsDrawn = [] #btnsDrawn include the discover options, etc
		self.CHN = CHN
		self.lbx_cards_1Possi = None
		self.lbx_cards_XPossi = None
		self.lbx_trackedHands = None
		self.lbx_Graveyard = None
		
		self.window = tk.Tk()
		#Select DIY packs
		lbl_SelectPacks = tk.Label(master=self.window, text=txt("Include DIY packs", CHN), font=("Yahei", 15))
		monkVar, SVVar = tk.IntVar(), tk.IntVar()
		includeMonk = tk.Checkbutton(self.window, text=txt("Monk", CHN), variable=monkVar, onvalue=1, offvalue=0, font=("Yahei", 15, "bold"))
		includeSV = tk.Checkbutton(self.window, text=txt("SV", CHN), variable=SVVar, onvalue=1, offvalue=0,
									 font=("Yahei", 15, "bold"))
		includeSV.select()
		lbl_SelectBoard = tk.Label(master=self.window, text=txt("Choose Game Board", CHN), font=("Yahei", 15))
		self.boardID = tk.StringVar(self.window)
		self.boardID.set(BoardIndex[0])
		boardOpt = tk.OptionMenu(self.window, self.boardID, *BoardIndex)
		boardOpt.config(width=20, font=("Yahei", 15))
		boardOpt["menu"].config(font=("Yahei", 15))
		var = tk.IntVar()
		
		onLeftVar = tk.IntVar()
		sidePanelonLeft = tk.Checkbutton(self.window, text=txt("Side Panel on Left", CHN), variable=onLeftVar, onvalue=1, offvalue=0, font=("Yahei", 15, "bold"))
		sidePanelonLeft.select() #The side panel shows on the left by default
		btn_genCardPool = tk.Button(self.window, text=txt("Continue", CHN), bg="green3", font=("Yahei", 15, "bold"), command=lambda : var.set(1))
		lbl_SelectPacks.pack()
		includeMonk.pack()
		includeSV.pack()
		lbl_SelectBoard.pack()
		boardOpt.pack() #place(x=60, y=60)
		sidePanelonLeft.pack()
		btn_genCardPool.pack()
		
		btn_genCardPool.wait_variable(var)
		self.boardID, self.transferStudentType = makeCardPool(self.boardID.get(), monkVar.get(), SVVar.get()) #定义棋盘信息和转校生的类型
		onLeft = onLeftVar.get()
		self.window.destroy()
		self.window = tk.Tk()
		#Import the cardPool generated after the selection
		from CardPools import Classes, ClassesandNeutral, ClassDict, cardPool, MinionsofCost, RNGPools
		
		self.GamePanel = tk.Frame(master=self.window, width=X, height=Y, bg="black")
		self.sidePanel = tk.Frame(master=self.window, width=int(0.02*X), bg="cyan")
		self.deckImportPanel = tk.Frame(master=self.window, width=int(0.02*X), height=0.6*Y)
		self.GamePanel.pack(fill=tk.Y, side=tk.RIGHT if onLeft else tk.LEFT) #place(relx=0, rely=0)
		self.sidePanel.pack(side=tk.TOP)
		self.deckImportPanel.pack(side=tk.TOP)
		
		self.lbl_wish = tk.Label(self.sidePanel, text=txt("Card Wished", CHN), font=("Yahei", 15))
		img = PIL.Image.open(r"Images\PyHSIcon.png").resize((75, 75))
		ph = PIL.ImageTk.PhotoImage(img)
		self.lbl_Card = tk.Label(self.sidePanel, image=ph)
		self.lbl_Card.image = ph
		#START in DECKIMPORTPANEL
		#Drop down option menu for the 1st&2nd hero
		self.initHero1ClassSelection()
		self.initHero2ClassSelection()
		#Confirm button to start the game
		LoadDeckButton(self).pack()
		self.deck1 = tk.Entry(self.deckImportPanel, font=("Yahei", 12))
		self.deck2 = tk.Entry(self.deckImportPanel, font=("Yahei", 12))
		tk.Label(self.deckImportPanel, text=txt("Enter Deck 1 code", CHN),
				font=("Yahei", 14)).place(relx=0.2, rely=0.82, anchor='c')
		tk.Label(self.deckImportPanel, text=txt("Enter Deck 2 code", CHN),
				font=("Yahei", 14)).place(relx=0.8, rely=0.82, anchor='c')
		self.deck1.pack(side=tk.LEFT)
		self.deck2.pack(side=tk.LEFT)
		self.window.mainloop()
		
	def initHero1ClassSelection(self):
		hero1 = tk.StringVar(self.deckImportPanel)
		hero1.set(list(ClassDict.keys())[0])
		hero1Opt = tk.OptionMenu(self.deckImportPanel, hero1, *list(ClassDict.keys()))
		hero1Opt.config(width=15, font=("Yahei", 15))
		hero1Opt["menu"].config(font=("Yahei", 15))
		hero1Opt.pack()
		self.hero1Label = tk.Label(self.deckImportPanel, text="Hero 1:Demon Hunter", font=("Yahei", 15))
		self.hero1Label.pack()
		hero1.trace("w", lambda *arg: self.hero1Label.configure(text="Hero 1 :"+hero1.get()))
		
	def initHero2ClassSelection(self):
		hero2 = tk.StringVar(self.deckImportPanel)
		hero2.set(list(ClassDict.keys())[0])
		hero2Opt = tk.OptionMenu(self.deckImportPanel, hero2, *list(ClassDict.keys()))
		hero2Opt.config(width=15, font=("Yahei", 15))
		hero2Opt["menu"].config(font=("Yahei", 15))
		hero2Opt.pack()
		self.hero2Label = tk.Label(self.deckImportPanel, text="Hero 2:Demon Hunter", font=("Yahei", 15))
		self.hero2Label.pack()
		hero2.trace("w", lambda *arg: self.hero2Label.configure(text="Hero 2 :"+hero2.get()))
				
GUI_1P()