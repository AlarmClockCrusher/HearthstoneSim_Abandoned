import tkinter as tk
from tkinter import messagebox, filedialog

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
		deck, hero = [], ClassDict[self.GUI.hero.get()]
		deckString, deckCorrect = self.GUI.deck.get(), True
		if deckString:
			if deckString.startswith("names||"):
				deckString = deckString.split('||')
				deckString.pop(0)
				for name in deckString:
					if name != "": deck.append(cardName2Class(name))
			else: deck = decode_deckstring(deckString)
		for obj in deck:
			if obj is None: deckCorrect = False
		if deckCorrect:
			for card in deck:
				if card.Class != "Neutral" and "," not in card.Class:
					hero = ClassDict[card.Class]
					break
			for i, card in enumerate(deck):
				if card.name == "Transfer Student": deck[i] = self.GUI.transferStudentType
			game = Game(self.GUI)
			game.transferStudentType = self.GUI.transferStudentType
			if self.GUI.ID == 1: game.initialize(cardPool, MinionsofCost, RNGPools, hero, None, deck, [])
			#玩家2加载玩家1的换算信息
			else: #If the GUI is player 2, self.guides stores info from player 1
				#player1Info is (heroType, handCards, deckCards)
				game.initialize(cardPool, MinionsofCost, RNGPools, self.GUI.player1Info[0], hero, [], deck)
				game.Hand_Deck.hands[1] = [card(game, 1) for card in self.GUI.player1Info[1]]
				game.Hand_Deck.decks[1] = [card(game, 1) for card in self.GUI.player1Info[2]]
				game.mulligans[1].clear()
			self.GUI.UI, game.mode = -2, 0
			game.Classes, game.ClassesandNeutral = Classes, ClassesandNeutral
			self.GUI.Game = game
			self.destroy()
			self.GUI.deckImportPanel.destroy()
			self.GUI.update()
		else: self.GUI.printInfo("Deck Incorrect")
		
		
class ContinueCancelButton(tk.Button):
	def leftClick(self, event):
		self.conti = True
		self.var.set(1)
		
	def rightClick(self, event):
		self.conti = False
		self.var.set(1)
		
#info会是plays||game.guides
class EnemyPlaysEntry(tk.Entry):
	def respond(self, event): #读入一个字符串，然后转换为plays
		conti = True
		if self.get() == self.GUI.lastInfo:
			confirm = ContinueCancelButton(self.GUI.GamePanel, text="Update same as last time\nLeftclick: Continue/Rightclick: Cancel", bg="red", fg="white", height=2, font=("Yahei", 18, "bold"))
			confirm.bind("<Button-1>", confirm.leftClick)
			confirm.bind("<Button-3>", confirm.rightClick)
			confirm.var, confirm.conti = tk.IntVar(), True
			confirm.place(x=0.5*X, y=0.5*Y, anchor='c')
			confirm.wait_variable(confirm.var)
			conti = confirm.conti
			confirm.destroy()
		if conti:
			self.GUI.lastInfo = self.get()
			moves, gameGuides = self.get().split("||") #is a string
			self.delete(0, tk.END)
			moves = unpickleStr2Obj(moves)
			gameGuides = unpickleStr2Obj(gameGuides)
			if isinstance(moves, list):
				self.GUI.printInfo("Reads in play")
				for move in moves:
					self.GUI.printInfo(move)
				self.GUI.Game.evolvewithGuide(moves, gameGuides)
				self.GUI.update()
			else: #只有玩家1会使用这个功能
				oppo_hero, oppo_Hand, oppo_Deck = gameGuides
				game = self.GUI.Game
				game.heroes[2] = oppo_hero(game, 2)
				game.powers[2] = oppo_hero.heroPower(game, 2)
				game.heroes[2].onBoard, game.powers[2].onBoard = True, True
				game.Hand_Deck.hands[2] = [card(game, 2) for card in oppo_Hand]
				game.Hand_Deck.decks[2] = [card(game, 2) for card in oppo_Deck]
				self.GUI.btnGenInfo.pack(fill=tk.X)
				self.GUI.deckImportPanel.destroy()
				self.GUI.initGameDisplay()
				self.GUI.update()
				game.Hand_Deck.startGame()
				
class InfoGenButton(tk.Button):
	def leftClick(self, event):
		if self.GUI.Game.moves and self.GUI.UI == 0: #没有moves记录的时候不响应
			moves, gameGuides = self.GUI.Game.moves, self.GUI.Game.guides
			s = pickleObj2Str(moves)+"||"+pickleObj2Str(gameGuides)
			self.GUI.info4Opponent.config(text=pickleObj2Str(moves)+"||"+pickleObj2Str(gameGuides))
			self.GUI.window.clipboard_clear()
			self.GUI.window.clipboard_append(s)
			self.GUI.info4Opponent.config(text=s)
			if self.GUI.showReminder.get():
				messagebox.showinfo(message="Info for opponent created in clipboard. \nSend before proceeding")
			self.GUI.Game.moves, self.GUI.Game.fixedGuides, self.GUI.Game.guides = [], [], []
			self.GUI.btnGenInfo.config(bg="Red", text="Send Info in Clipboard!")
		else:
			self.GUI.printInfo("No new info to generate.")
			self.GUI.cancelSelection()
			
	def rightClick(self, event):
		self.GUI.Game.moves, self.GUI.Game.fixedGuides, self.GUI.Game.guides = [], [], []
		gameCopy = self.GUI.Game.copyGame()[0]
		gameCopy.GUI = None
		pickle.dump((1, self.GUI.boardID, gameCopy), open("GametoLoad_asPlayer1.p", "wb"))
		pickle.dump((2, self.GUI.boardID, gameCopy), open("GametoLoad_asPlayer2.p", "wb"))
		if self.GUI.showReminder.get():
			messagebox.showinfo(message="Copied game created as a pickle file")
		self.GUI.Game.moves, self.GUI.Game.fixedGuides, self.GUI.Game.guides = [], [], []
		self.GUI.btnGenInfo.config(bg="Red", text="Send Info in Clipboard!")
		
		
class Info4OppoLabel(tk.Label):
	def __init__(self, GUI):
		tk.Label.__init__(self, master=GUI.inputPanel, text="Info not generated yet", font=("Yahei", 15), width=20)
		self.GUI = GUI
		self.bind("<Button-3>", self.rightClick)
		
	def rightClick(self, event):
		self.GUI.window.clipboard_clear()
		self.GUI.window.clipboard_append(self.cget('text'))
		
		
class LoadPickleButton(tk.Button):
	def __init__(self, GUI, window):
		tk.Button.__init__(self, master=window, bg="green3", text="Choose a Game to load", font=("Yahei", 14))
		self.configure(command=self.respond)
		self.GUI = GUI
		
	def respond(self):
		self.GUI.pickleFile = filedialog.askopenfilename(title="Select pickle file", filetypes=(("pickle files","*.p"),("all files","*.*")))
		
#import tkinter.font as tkFont
#fontStyle = tkFont.Font(family="Lucida Grande", size=3)
class GUI_2P(GUI_Common):
	def __init__(self):
		self.mulliganStatus, self.btnsDrawn = [], []
		self.selectedSubject = ""
		self.subject, self.target, self.discover = None, None, None
		self.position, self.choice, self.UI = -1, 0, -2 #起手调换的UI为-2
		self.ID, self.showReminder = 1, None
		self.lastInfo, self.pickleFile = '', None
		self.DIYs = []
		self.window = tk.Tk()
		#Before entering deck, Player 1 loads the packs and choose the board
		if self: #Draw the first stage of selection
			self.boardID = tk.StringVar(self.window)
			self.boardID.set(BoardIndex[0])
			boardOpt = tk.OptionMenu(self.window, self.boardID, *BoardIndex)
			boardOpt.config(width=20, font=("Yahei", 15))
			boardOpt["menu"].config(font=("Yahei", 15))
			monkVar = tk.IntVar()
			var = tk.IntVar()
			btn1 = tk.Button(self.window, text="Start Loading Deck", bg="green3", font=("Yahei", 15, "bold"), command=lambda : var.set(1))
			btn2 = tk.Button(self.window, text="Load Saved Game/Go 2nd", bg="green3", font=("Yahei", 15, "bold"), command=lambda : var.set(2))
			tk.Label(self.window, text="Start a new game as Player 1\nDecide DIY Packs and Game Board", \
					font=("Yahei", 15, "bold")).grid(row=0, column=0)
			btn1.grid(row=1, column = 0)
			tk.Label(self.window, text="Choose Game Board", \
					font=("Yahei", 15)).grid(row=2, column = 0)
			boardOpt.grid(row=3, column = 0)
			tk.Label(self.window, text="Include DIY packs", \
					font=("Yahei", 15)).grid(row=4, column = 0)
			tk.Checkbutton(self.window, text='Monk', variable=monkVar, onvalue=1, \
							offvalue=0, font=("Yahei", 15, "bold")).grid(row=5, column = 0)
			#Define and grid the buttons for loading
			tempGuides = EnemyPlaysEntry(self.window, font=("Yahei", 14), width=15)
			tempGuides.bind("<Return>", lambda event: var.set(2))
			tempGuides.GUI = self
			
			tk.Label(self.window, text="Load a Game, or\nGo 2nd using Info from Opponent" \
					, font=("Yahei", 15, "bold")).grid(row=0, column=2)
			LoadPickleButton(self, self.window).grid(row=1, column=2)
			tk.Label(self.window, text="Use Info from Opponent" \
					, font=("Yahei", 15)).grid(row=2, column=2)
			tempGuides.grid(row=3, column=2)
			btn2.grid(row=4, column=2)
			
			tk.Label(self.window, text="		 ").grid(row=0, column=1)
			
		self.window.wait_variable(var)
		if var.get() == 1: #点击左边的情况会有要求先换牌，然后把信息传给对方
			self.ID, self.DIYs = 1, monkVar.get()
			#制作cardPool的同时也会返回真正的boardID
			self.boardID, self.transferStudentType = makeCardPool(self.DIYs, self.boardID.get())
			from CardPools import Classes, ClassesandNeutral, ClassDict, cardPool, MinionsofCost, RNGPools
			self.window.destroy()
			self.window = tk.Tk()
			self.initLoadDeckUI() #Draw LoadDeck panel. Do mulligan as Player 1
		else: #var == 2, load saved/defined game
			if self.pickleFile:
				self.ID, self.boardID, gameCopy = pickle.load(open(self.pickleFile, "rb"))
				gameCopy.GUI = self
				self.Game = gameCopy
				print("Copy a game based on info from another GUI")
				self.window.destroy()
				self.window = tk.Tk()
				self.initLoadDeckUI()
				self.deckImportPanel.destroy()
				self.btnGenInfo.pack()
				self.initGameDisplay()
				self.update()
			elif tempGuides.get(): #The loaded entry must be non-empty
				self.ID = 2
				print("Loading defined game for 2")
				#("DefineGame", DIYlist, boardID, guides)
				move, info = tempGuides.get().split('||')
				move = unpickleStr2Obj(move)
				self.DIYs, self.boardID, self.player1Info = unpickleStr2Obj(info)
				if move == "DefineGame":
					self.transferStudentType = makeCardPool(self.DIYs, self.boardID)[1]
					from CardPools import Classes, ClassesandNeutral, ClassDict, cardPool, MinionsofCost, RNGPools
					self.window.destroy()
					self.window = tk.Tk()
					self.initLoadDeckUI() #2号玩家开始自己的换牌。在之之前1号玩家已经换牌完毕并把信息传给了2号
					
		self.window.mainloop()
		
	def initLoadDeckUI(self):
		self.GamePanel = tk.Frame(master=self.window, width=X, height=Y, bg="black")
		self.GamePanel.pack(fill=tk.Y, side=tk.LEFT if LeftorRight else tk.RIGHT)
		self.outputPanel = tk.Frame(master=self.window, width=0.005*X, height=int(0.2*Y), bg="cyan")
		self.outputPanel.pack(side=tk.TOP)
		self.inputPanel = tk.Frame(master=self.window, width=int(0.005*X), height=int(0.3*Y), bg="cyan")
		self.inputPanel.pack(side=tk.TOP)
		self.deckImportPanel = tk.Frame(master=self.window, width=0.005*X, height=int(0.6*Y))
		self.deckImportPanel.pack(side=tk.TOP)
		
		lbl_Output = tk.Label(master=self.outputPanel, text="System Resolution", font=("Yahei", 15))
		scrollbar_hor = tk.Scrollbar(master=self.outputPanel, orient="horizontal")
		scrollbar_ver = tk.Scrollbar(master=self.outputPanel)
		self.output = tk.Listbox(master=self.outputPanel, xscrollcommand=scrollbar_hor.set, yscrollcommand=scrollbar_ver.set, width=50, height=6, bg="white", font=("Yahei", 13))
		scrollbar_hor.configure(command=self.output.xview)
		scrollbar_ver.configure(command=self.output.yview)
		scrollbar_ver.pack(fill=tk.Y, side=tk.RIGHT)
		scrollbar_hor.pack(fill=tk.X, side=tk.BOTTOM)
		lbl_Output.pack(fill=tk.X, side=tk.TOP)
		self.output.pack(side=tk.LEFT)
		
		self.lbl_Card = tk.Label(self.inputPanel, text="Resolving Card Effect")
		self.info4Opponent = Info4OppoLabel(self)
		self.guides = EnemyPlaysEntry(master=self.inputPanel, font=("Yahei", 12), width=10)
		self.guides.bind("<Return>", self.guides.respond)
		self.guides.GUI = self
		
		self.lbl_wish = tk.Label(master=self.inputPanel, text="Type Card You Wish", font=("Yahei", 15))
		self.wish = tk.Entry(master=self.inputPanel, font=("Yahei", 12))
		
		self.btnGenInfo = InfoGenButton(master=self.inputPanel, bg='yellow', text="L:Generate Update / R:Copy Game", font=("Yahei", 12, "bold"), height=1)
		self.btnGenInfo.bind('<Button-1>', self.btnGenInfo.leftClick)
		self.btnGenInfo.bind('<Button-3>', self.btnGenInfo.rightClick)
		self.btnGenInfo.GUI = self
		self.lbl_Card.pack(fill=tk.X)
		tk.Label(master=self.inputPanel, text="Plays to update", font=("Yahei", 15)).pack(fill=tk.X)
		self.guides.pack(fill=tk.X, side=tk.TOP)
		self.info4Opponent.pack(fill=tk.X, side=tk.TOP)
		self.showReminder = tk.IntVar()
		ckb = tk.Checkbutton(self.inputPanel, text="Show Send Info Reminder", font=("Yahei", 14, ), \
						variable=self.showReminder, onvalue=1, offvalue=0)
		ckb.select()
		ckb.pack(side=tk.TOP)
		self.printInfo("Import your deck and select class")
		
		self.hero = tk.StringVar(self.deckImportPanel)
		self.hero.set(list(ClassDict.keys())[0])
		heroOpt = tk.OptionMenu(self.deckImportPanel, self.hero, *list(ClassDict.keys()))
		heroOpt.config(width=15, font=("Yahei", 15))
		heroOpt["menu"].config(font=("Yahei", 15))
		heroOpt.pack()#place(x=60, y=60)
		
		tk.Label(self.deckImportPanel, text="Enter deck code below", \
				font=("Yahei", 14)).pack()
		self.deck = tk.Entry(self.deckImportPanel, font=("Yahei", 12))
		self.deck.pack()
		btn_LoadDeck = LoadDeckButton(self)
		btn_LoadDeck.pack()
		self.deck.bind("<Return>", lambda event: btn_LoadDeck.respond())
		
		
GUI_2P()