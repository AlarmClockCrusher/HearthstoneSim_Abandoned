import tkinter as tk
from tkinter import messagebox, filedialog

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
		deck, hero = [], ClassDict[self.GUI.hero.get()]
		deck, deckCorrect, hero = parseDeckCode(self.GUI.deck.get(), hero, ClassDict)
		if deckCorrect:
			for i, card in enumerate(deck):
				if card.name == "Transfer Student": deck[i] = self.GUI.transferStudentType
			game = Game(self.GUI)
			game.transferStudentType = self.GUI.transferStudentType
			if self.GUI.ID == 1: game.initialize(cardPool, ClassCards, NeutralCards, MinionsofCost, RNGPools, hero, None, deck, [])
			#玩家2加载玩家1的换牌信息
			else: #If the GUI is player 2, self.guides stores info from player 1
				#player1Info is (heroType, handCards, deckCards)
				game.initialize(cardPool, ClassCards, NeutralCards, MinionsofCost, RNGPools, self.GUI.player1Info[0], hero, [], deck)
				game.Hand_Deck.hands[1] = [card(game, 1) for card in self.GUI.player1Info[1]]
				game.Hand_Deck.decks[1] = [card(game, 1) for card in self.GUI.player1Info[2]]
				game.mulligans[1].clear()
			self.GUI.UI, game.mode = -2, 0
			game.Classes, game.ClassesandNeutral = Classes, ClassesandNeutral
			self.GUI.Game = game
			self.destroy()
			self.GUI.deckImportPanel.destroy()
			self.GUI.update()
		else: messagebox.showinfo(message=txt("Deck code is wrong. Check before retry", CHN))
		
		
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
			confirm = ContinueCancelButton(self.GUI.GamePanel, text=txt("Update same as last time\nLeftclick: Continue/Rightclick: Cancel", CHN), bg="red", fg="white", height=2, font=("Yahei", 18, "bold"))
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
				messagebox.showinfo(message=txt("Send Info in Clipboard!", CHN))
			self.GUI.Game.moves, self.GUI.Game.fixedGuides, self.GUI.Game.guides = [], [], []
		else:
			self.GUI.cancelSelection()
			
	def rightClick(self, event):
		self.GUI.Game.moves, self.GUI.Game.fixedGuides, self.GUI.Game.guides = [], [], []
		gameCopy = self.GUI.Game.copyGame()[0]
		gameCopy.GUI = None
		pickle.dump((1, self.GUI.boardID, gameCopy), open("GametoLoad_asPlayer1.p", "wb"))
		pickle.dump((2, self.GUI.boardID, gameCopy), open("GametoLoad_asPlayer2.p", "wb"))
		if self.GUI.showReminder.get():
			messagebox.showinfo(message=txt("Copied game created as a pickle file", CHN))
		self.GUI.Game.moves, self.GUI.Game.fixedGuides, self.GUI.Game.guides = [], [], []
		self.GUI.btnGenInfo.config(bg="Red", text=txt("Game Copy Generated", CHN))
		
		
class Info4OppoLabel(tk.Label):
	def __init__(self, GUI):
		tk.Label.__init__(self, master=GUI.sidePanel, text=txt("Info not generated yet", CHN), font=("Yahei", 15), width=20)
		self.GUI = GUI
		self.bind("<Button-3>", self.rightClick)
		
	def rightClick(self, event):
		self.GUI.window.clipboard_clear()
		self.GUI.window.clipboard_append(self.cget('text'))
		
		
class LoadPickleButton(tk.Button):
	def __init__(self, GUI, window):
		tk.Button.__init__(self, master=window, bg="green3", text=txt("Choose a Game to load", CHN), font=("Yahei", 14))
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
		self.CHN = CHN
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
			btn1 = tk.Button(self.window, text=txt("Start Loading Deck", CHN), bg="green3", font=("Yahei", 15, "bold"), command=lambda : var.set(1))
			btn2 = tk.Button(self.window, text=txt("Load Saved Game/Go 2nd", CHN), bg="green3", font=("Yahei", 15, "bold"), command=lambda : var.set(2))
			tk.Label(self.window, text=txt("Start a new game as Player 1\nDecide DIY Packs and Game Board", CHN), \
					font=("Yahei", 15, "bold")).grid(row=0, column=0)
			btn1.grid(row=1, column = 0)
			tk.Label(self.window, text=txt("Choose Game Board", CHN), \
					font=("Yahei", 15)).grid(row=2, column = 0)
			boardOpt.grid(row=3, column = 0)
			tk.Label(self.window, text=txt("Include DIY packs", CHN), \
					font=("Yahei", 15)).grid(row=4, column = 0)
			tk.Checkbutton(self.window, text=txt('Monk', CHN), variable=monkVar, onvalue=1, \
							offvalue=0, font=("Yahei", 15, "bold")).grid(row=5, column = 0)
			#Define and grid the buttons for loading
			tempGuides = EnemyPlaysEntry(self.window, font=("Yahei", 14), width=15)
			tempGuides.bind("<Return>", lambda event: var.set(2))
			tempGuides.GUI = self
			
			tk.Label(self.window, text=txt("Load a Game, or\nGo 2nd using Info from Opponent", CHN) \
					, font=("Yahei", 15, "bold")).grid(row=0, column=2)
			LoadPickleButton(self, self.window).grid(row=1, column=2)
			tk.Label(self.window, text=txt("Load Update from Opponent", CHN) \
					, font=("Yahei", 15)).grid(row=2, column=2)
			tempGuides.grid(row=3, column=2)
			btn2.grid(row=4, column=2)
			
			tk.Label(self.window, text="		 ").grid(row=0, column=1)
			
		messagebox.showinfo(message=txt("To go 1st, use left panel to decide the DIY expansion and game board.\nTo go 2nd/load a saved game, use right panel to enter info from your opponent/select a .p file", CHN))
		self.window.wait_variable(var)
		if var.get() == 1: #点击左边的情况会有要求先换牌，然后把信息传给对方
			messagebox.showinfo(message(txt("Decide your deck and class, mulligan and send the generated info to your opponent"), CHN))
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
				messagebox.showinfo(message=txt("Saved Game loaded. Will resume after confirmation", CHN))
				gameCopy.GUI = self
				self.Game = gameCopy
				self.window.destroy()
				self.window = tk.Tk()
				self.initLoadDeckUI()
				self.deckImportPanel.destroy()
				self.btnGenInfo.pack()
				self.initGameDisplay()
				self.update()
			elif tempGuides.get(): #The loaded entry must be non-empty
				self.ID = 2
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
					messagebox.showinfo(message=txt("Player 1 has decided their deck and initial hand.\nDecide yours and send the info back to start the game", CHN))
		self.window.mainloop()
		
	def initLoadDeckUI(self):
		self.GamePanel = tk.Frame(master=self.window, width=X, height=Y, bg="black")
		self.GamePanel.pack(fill=tk.Y, side=tk.LEFT if LeftorRight else tk.RIGHT)
		self.sidePanel = tk.Frame(master=self.window, width=int(0.005*X), height=int(0.3*Y), bg="cyan")
		self.sidePanel.pack(side=tk.TOP)
		self.deckImportPanel = tk.Frame(master=self.window, width=0.005*X, height=int(0.6*Y))
		self.deckImportPanel.pack(side=tk.TOP)
		
		self.lbl_Card = tk.Label(self.sidePanel, text=txt("Resolving Card Effect", CHN))
		self.info4Opponent = Info4OppoLabel(self)
		self.guides = EnemyPlaysEntry(master=self.sidePanel, font=("Yahei", 12), width=10)
		self.guides.bind("<Return>", self.guides.respond)
		self.guides.GUI = self
		
		self.lbl_wish = tk.Label(master=self.sidePanel, text=txt("Card Wished", CHN), font=("Yahei", 15))
		
		self.btnGenInfo = InfoGenButton(master=self.sidePanel, bg='yellow', text=txt("L:Generate Update / R:Copy Game", CHN), font=("Yahei", 12, "bold"), height=1)
		self.btnGenInfo.bind('<Button-1>', self.btnGenInfo.leftClick)
		self.btnGenInfo.bind('<Button-3>', self.btnGenInfo.rightClick)
		self.btnGenInfo.GUI = self
		self.lbl_Card.pack(fill=tk.X)
		tk.Label(master=self.sidePanel, text=txt("Plays to update", CHN), font=("Yahei", 15)).pack(fill=tk.X)
		self.guides.pack(fill=tk.X, side=tk.TOP)
		self.info4Opponent.pack(fill=tk.X, side=tk.TOP)
		self.showReminder = tk.IntVar()
		ckb = tk.Checkbutton(self.sidePanel, text=txt("Show Send Info Reminder", CHN), font=("Yahei", 14, ), \
						variable=self.showReminder, onvalue=1, offvalue=0)
		ckb.select()
		ckb.pack(side=tk.TOP)
		
		self.hero = tk.StringVar(self.deckImportPanel)
		self.hero.set(list(ClassDict.keys())[0])
		heroOpt = tk.OptionMenu(self.deckImportPanel, self.hero, *list(ClassDict.keys()))
		heroOpt.config(width=15, font=("Yahei", 15))
		heroOpt["menu"].config(font=("Yahei", 15))
		heroOpt.pack()#place(x=60, y=60)
		
		tk.Label(self.deckImportPanel, text=txt("Enter deck code below", CHN), \
				font=("Yahei", 14)).pack()
		self.deck = tk.Entry(self.deckImportPanel, font=("Yahei", 12))
		self.deck.pack()
		btn_LoadDeck = LoadDeckButton(self)
		btn_LoadDeck.pack()
		self.deck.bind("<Return>", lambda event: btn_LoadDeck.respond())
		
		
GUI_2P()