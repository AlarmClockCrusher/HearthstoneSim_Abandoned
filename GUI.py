import tkinter as tk

from CustomWidgets import *
from UICommonPart import GUI_Common
from Game import *
from Code2CardList import *
from GenerateRNGPools import *

class LoadDeckButton(tk.Button):
	def __init__(self, GUI):
		tk.Button.__init__(self, master=GUI.deckImportPanel, bg="green3", text="Confirm", font=("Yahei", 15))
		self.GUI = GUI
		self.configure(command=self.respond)
		
	def respond(self):
		hero_1 = ClassDict[self.GUI.hero1Label["text"].split(':')[-1]]
		hero_2 = ClassDict[self.GUI.hero2Label["text"].split(':')[-1]]
		decks = {1: [], 2: []}
		deckStrings = {1: self.GUI.deck1.get(), 2: self.GUI.deck2.get()}
		decksCorrect = {1: True, 2: True}
		for ID in range(1, 3):
			if deckStrings[ID] != "":
				if deckStrings[ID].startswith("names||"):
					deckStrings[ID] = deckStrings[ID].split('||')
					deckStrings[ID].pop(0)
					for name in deckStrings[ID]:
						if name != "": decks[ID].append(cardName2Class(name))
				else: decks[ID] = decode_deckstring(deckStrings[ID])
			else: decks[ID] = []
		for ID in range(1, 3):
			for obj in decks[ID]:
				if obj is None:
					decksCorrect[ID] = False
		if decksCorrect[1] and decksCorrect[2]:
			self.GUI.Game = Game(self.GUI)
			self.GUI.Game.transferStudentType = self.GUI.transferStudentType
			for card in decks[1]:
				if card.Class != "Neutral" and ',' not in card.Class:
					hero_1 = ClassDict[card.Class]
					break
			for card in decks[2]:
				if card.Class != "Neutral" and ',' not in card.Class:
					hero_2 = ClassDict[card.Class]
					break
			self.GUI.deckImportPanel.destroy()
			for ID in range(1, 3):
				for i, card in enumerate(decks[ID]):
					if card.name == "Transfer Student": decks[ID][i] = self.GUI.transferStudentType
			self.GUI.Game.initialize(cardPool, MinionsofCost, RNGPools, hero_1, hero_2, decks[1], decks[2])
			self.GUI.Game.mode = 0
			self.GUI.Game.Classes, self.GUI.Game.ClassesandNeutral = Classes, ClassesandNeutral
			self.GUI.posMulligans = {1:[(100+i*2*111, Y-140) for i in range(len(self.GUI.Game.mulligans[1]))],
								2:[(100+i*2*111, 140) for i in range(len(self.GUI.Game.mulligans[2]))]}
			self.destroy()
			self.GUI.lbl_Card.pack()
			self.GUI.update()
		else:
			if not decksCorrect[1]: self.GUI.printInfo("Deck 1 incorrect")
			if not decksCorrect[2]: self.GUI.printInfo("Deck 2 incorrect")
			
			
class GUI_1P(GUI_Common):
	def __init__(self):
		self.mulliganStatus = {1:[0, 0, 0], 2:[0, 0, 0, 0]}
		self.selectedSubject = ""
		self.subject, self.target = None, None
		self.position, self.choice, self.UI = -1, 0, -2 #起手调换为-2
		self.discover = None
		self.gameBackup = None
		self.btnsDrawn = [] #btnsDrawn include the discover options, etc
		self.window = tk.Tk()
		#Select DIY packs
		lbl_SelectPacks = tk.Label(master=self.window, text="Include DIY packs", font=("Yahei", 15))
		monkVar = tk.IntVar()
		includeMonk = tk.Checkbutton(self.window, text='Monk', variable=monkVar, onvalue=1, offvalue=0, font=("Yahei", 15, "bold"))
		lbl_SelectBoard = tk.Label(master=self.window, text="Choose Game Board", font=("Yahei", 15))
		self.boardID = tk.StringVar(self.window)
		self.boardID.set(BoardIndex[0])
		boardOpt = tk.OptionMenu(self.window, self.boardID, *BoardIndex)
		boardOpt.config(width=20, font=("Yahei", 15))
		boardOpt["menu"].config(font=("Yahei", 15))
		var = tk.IntVar()
		
		btn_genCardPool = tk.Button(self.window, text="Continue", bg="green3", font=("Yahei", 15, "bold"), command=lambda : var.set(1))
		lbl_SelectPacks.pack()
		includeMonk.pack()
		lbl_SelectBoard.pack()
		boardOpt.pack() #place(x=60, y=60)
		btn_genCardPool.pack()
		
		btn_genCardPool.wait_variable(var)
		self.boardID, self.transferStudentType = makeCardPool(monkVar.get(), self.boardID.get()) #定义棋盘信息和转校生的类型
		self.window.destroy()
		self.window = tk.Tk()
		#Import the cardPool generated after the selection
		from CardPools import Classes, ClassesandNeutral, ClassDict, cardPool, MinionsofCost, RNGPools
		
		self.GamePanel = tk.Frame(master=self.window, width=X, height=Y, bg="black")
		self.GamePanel.pack(fill=tk.Y, side=tk.LEFT) #place(relx=0, rely=0)
		self.outputPanel = tk.Frame(master=self.window, width=int(0.02*X), height=0.3*Y, bg="cyan")
		self.outputPanel.pack(side=tk.TOP)
		self.inputPanel = tk.Frame(master=self.window, width=int(0.02*X), bg="cyan")
		self.inputPanel.pack(side=tk.TOP)
		self.deckImportPanel = tk.Frame(master=self.window, width=int(0.02*X), height=0.6*Y)
		self.deckImportPanel.pack(side=tk.TOP)
		
		tk.Label(master=self.outputPanel, text="System Resolution", font=("Yahei", 15)).pack(fill=tk.X, side=tk.TOP)
		scrollbar_ver = tk.Scrollbar(master=self.outputPanel)
		scrollbar_ver.pack(fill=tk.Y, side=tk.RIGHT)
		scrollbar_hor = tk.Scrollbar(master=self.outputPanel, orient="horizontal")
		scrollbar_hor.pack(fill=tk.X, side=tk.BOTTOM)
		self.output = tk.Listbox(master=self.outputPanel, xscrollcommand=scrollbar_hor.set, yscrollcommand=scrollbar_ver.set, width=50, height=6, bg="white", font=("Yahei", 13))
		self.output.pack(side=tk.LEFT)
		scrollbar_hor.configure(command=self.output.xview)
		scrollbar_ver.configure(command=self.output.yview)
		
		self.lbl_wish = tk.Label(self.inputPanel, text="Type Card You Wish", font=("Yahei", 15))
		self.wish = tk.Entry(self.inputPanel, font=("Yahei", 12))
		self.lbl_Card = tk.Label(self.inputPanel, text="Resolving Card Effect")
		
		self.printInfo("Import the two decks for players and select the heroes")
		#START in DECKIMPORTPANEL
		#Drop down option menu for the 1st hero
		hero1 = tk.StringVar(self.deckImportPanel)
		hero1.set(list(ClassDict.keys())[0])
		hero1Opt = tk.OptionMenu(self.deckImportPanel, hero1, *list(ClassDict.keys()))
		hero1Opt.config(width=15, font=("Yahei", 15))
		hero1Opt["menu"].config(font=("Yahei", 15))
		hero1Opt.pack()
		self.hero1Label = tk.Label(self.deckImportPanel, text="Hero 1 :Demon Hunter", font=("Yahei", 15))
		self.hero1Label.pack()
		hero1.trace("w", lambda *arg: self.hero1Label.configure(text="Hero 1 :"+hero1.get()))
		
		##Drop down option menu for the 2nd hero
		hero2 = tk.StringVar(self.deckImportPanel)
		hero2.set(list(ClassDict.keys())[0])
		hero2Opt = tk.OptionMenu(self.deckImportPanel, hero2, *list(ClassDict.keys()))
		hero2Opt.config(width=15, font=("Yahei", 15))
		hero2Opt["menu"].config(font=("Yahei", 15))
		hero2Opt.pack()
		self.hero2Label = tk.Label(self.deckImportPanel, text="Hero 2 :Demon Hunter", font=("Yahei", 15))
		self.hero2Label.pack()
		hero2.trace("w", lambda *arg: self.hero2Label.configure(text="Hero 2 :"+hero2.get()))
		
		#Confirm button to start the game
		LoadDeckButton(self).pack()
		self.deck1 = tk.Entry(self.deckImportPanel, font=("Yahei", 12))
		self.deck2 = tk.Entry(self.deckImportPanel, font=("Yahei", 12))
		lbl_deck1 = tk.Label(self.deckImportPanel, text="Deck 1 code", font=("Yahei", 14))
		lbl_deck2 = tk.Label(self.deckImportPanel, text="Deck 2 code", font=("Yahei", 14))
		self.deck1.pack(side=tk.LEFT)
		self.deck2.pack(side=tk.LEFT)
		lbl_deck1.place(relx=0.2, rely=0.82, anchor='c')
		lbl_deck2.place(relx=0.8, rely=0.82, anchor='c')
		self.window.mainloop()
		
				
GUI_1P()