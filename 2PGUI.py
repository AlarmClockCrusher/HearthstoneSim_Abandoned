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
			self.GUI.initSidePanel()
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
	def __init__(self, GUI, master):
		super().__init__(master=master, font=("Yahei", 12), width=10)
		self.GUI = GUI
		
	def respond(self, event): #读入一个字符串，然后转换为plays
		conti = True
		if self.get() == self.GUI.lastInfo:
			confirm = ContinueCancelButton(self.GUI.GamePanel, text=txt("Update same as last time\nLeftclick: Continue/Rightclick: Cancel", CHN), bg="red", fg="white", height=2, font=("Yahei", 15, "bold"))
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
	def __init__(self, GUI, master):
		super().__init__(master=master, bg='yellow', text=txt("L:Generate Update / R:Copy Game", CHN), 
						font=("Yahei", 10, "bold"), height=2)
		self.bind('<Button-1>', self.leftClick)
		self.bind('<Button-3>', self.rightClick)
		self.GUI = GUI
		
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


class LoadPickleButton(tk.Button):
	def __init__(self, GUI, window):
		tk.Button.__init__(self, master=window, bg="green3", text=txt("Choose a Game to load", CHN), font=("Yahei", 14))
		self.configure(command=self.respond)
		self.GUI = GUI

	def respond(self):
		self.GUI.pickleFile = filedialog.askopenfilename(title="Select pickle file", filetypes=(("pickle files","*.p"),("all files","*.*")))

		
class Info4OppoLabel(tk.Label):
	def __init__(self, GUI, master):
		tk.Label.__init__(self, master=master, text=txt("Info not generated yet", CHN), font=("Yahei", 10), width=20)
		self.GUI = GUI
		self.bind("<Button-3>", self.rightClick)

	def rightClick(self, event):
		self.GUI.window.clipboard_clear()
		self.GUI.window.clipboard_append(self.cget('text'))

class InfoExchangePanel(tk.Frame):
	def __init__(self, GUI):
		self.GUI = GUI
		super().__init__(master=self.GUI.sidePanel)
		self.GUI.info4Opponent = Info4OppoLabel(GUI, self)
		self.GUI.btnGenInfo = InfoGenButton(GUI, self)
		self.GUI.guides = EnemyPlaysEntry(GUI, self)
		self.GUI.guides.bind("<Return>", self.GUI.guides.respond)
		
		tk.Label(master=self, text=txt("Info from opponent", CHN), 
				font=("Yahei", 11)).grid(row=0, column=0)
		self.GUI.guides.grid(row=1, column=0)
		tk.Label(master=self, text=txt("Info to send to opponent", CHN),
				font=("Yahei", 11)).grid(row=0, column=1)
		self.GUI.info4Opponent.grid(row=1, column=1)
		self.GUI.btnGenInfo.grid(row=2, column=0, columnspan=2)
		ckb = tk.Checkbutton(self, text=txt("Show Send Info Reminder", CHN), font=("Yahei", 11, ), \
						variable=self.GUI.showReminder, onvalue=1, offvalue=0)
		if self.GUI.showReminder.get(): ckb.select()
		ckb.grid(row=3, column=0, columnspan=2)
		
#import tkinter.font as tkFont
#fontStyle = tkFont.Font(family="Lucida Grande", size=3)
class GUI_2P(GUI_Common):
	def __init__(self):
		self.window = tk.Tk()
		self.mulliganStatus, self.btnsDrawn = [], []
		self.selectedSubject = ""
		self.subject, self.target, self.discover = None, None, None
		self.pos, self.choice, self.UI = -1, 0, -2 #起手调换的UI为-2
		self.ID, self.showReminder = 1, tk.IntVar()
		self.lastInfo, self.pickleFile = '', None
		self.sidePanel, self.infoExchangePanel = None, None
		
		self.monk = self.SV = False
		self.CHN = CHN
		'''Before entering deck, Player 1 loads the packs and choose the board'''
		self.boardID = tk.StringVar(self.window)
		self.boardID.set(BoardIndex[0])
		onLeftVar = tk.IntVar()
		monkVar, SVVar = tk.IntVar(), tk.IntVar()
		sidePanelonLeft = tk.Checkbutton(self.window, text=txt("Side Panel on Left", CHN), variable=onLeftVar, onvalue=1, offvalue=0, font=("Yahei", 15, "bold"))
		sidePanelonLeft.select() #The side panel shows on the left by default
		var = tk.IntVar()
		tempGuides = tk.Entry(self.window, font=("Yahei", 12), width=10)
		tempGuides.bind("<Return>", lambda event: var.set(2))
		
		self.init1stInterface(var, sidePanelonLeft, onLeftVar, tempGuides,
							monkVar, SVVar)
		"""After the first interface, handle the mulligan and first round of info exchange"""
		if var.get() == 1: #点击左边的情况会有要求先换牌，然后把信息传给对方
			if self.showReminder.get():
				messagebox.showinfo(message=(txt("Decide your deck and class, mulligan and send the generated info to your opponent"), CHN))
			self.ID, self.monk, self.SV, onLeft = 1, monkVar.get(), SVVar.get(), onLeftVar.get()
			#制作cardPool的同时也会返回真正的boardID
			self.boardID, self.transferStudentType = makeCardPool(board=self.boardID.get(), monk=self.monk, SV=self.SV)
			from CardPools import Classes, ClassesandNeutral, ClassDict, cardPool, MinionsofCost, RNGPools
			self.window.destroy()
			self.window = tk.Tk()
			self.initLoadDeckUI(onLeft) #Draw LoadDeck panel. Do mulligan as Player 1
		else: #var == 2, load saved/defined game
			onLeft = onLeftVar.get()
			if self.pickleFile:
				self.ID, self.boardID, gameCopy = pickle.load(open(self.pickleFile, "rb"))
				if self.showReminder.get():
					messagebox.showinfo(message=txt("Saved Game loaded. Will resume after confirmation", CHN))
				gameCopy.GUI = self
				self.Game = gameCopy
				self.window.destroy()
				self.window = tk.Tk()
				self.initLoadDeckUI(onLeft)
				self.deckImportPanel.destroy()
				self.btnGenInfo.pack()
				self.initGameDisplay()
				self.initSidePanel()
				self.update()
			elif tempGuides.get(): #The loaded entry must be non-empty
				self.ID = 2
				#("DefineGame", DIYlist, boardID, guides)
				move, info = tempGuides.get().split('||')
				move = unpickleStr2Obj(move)
				self.monk, self.SV, self.boardID, self.player1Info = unpickleStr2Obj(info)
				if move == "DefineGame":
					self.transferStudentType = makeCardPool(board=self.boardID, monk=self.monk, SV=self.SV)[1]
					from CardPools import Classes, ClassesandNeutral, ClassDict, cardPool, MinionsofCost, RNGPools
					self.window.destroy()
					self.window = tk.Tk()
					self.initLoadDeckUI(onLeft) #2号玩家开始自己的换牌。在之之前1号玩家已经换牌完毕并把信息传给了2号
					if self.showReminder.get():
						messagebox.showinfo(message=txt("Player 1 has decided their deck and initial hand.\nDecide yours and send the info back to start the game", CHN))
		self.window.mainloop()

	def init1stInterface(self, var, sidePanelonLeft, onLeftVar, tempGuides,
						monkVar, SVVar):
		boardOpt = tk.OptionMenu(self.window, self.boardID, *BoardIndex)
		boardOpt.config(width=20, font=("Yahei", 15))
		boardOpt["menu"].config(font=("Yahei", 15))
		#Left half panel
		tk.Label(self.window, text=txt("Start a new game as Player 1\nDecide DIY Packs and Game Board", CHN), \
				font=("Yahei", 15, "bold")).grid(row=0, column=0)
		tk.Button(self.window, text=txt("Start Loading Deck", CHN), bg="green3", font=("Yahei", 15, "bold"),
				command=lambda : var.set(1)).grid(row=1, column = 0)
		tk.Label(self.window, text=txt("Choose Game Board", CHN), \
				font=("Yahei", 15)).grid(row=2, column = 0)
		boardOpt.grid(row=3, column = 0)
		tk.Label(self.window, text=txt("Include DIY packs", CHN), \
				font=("Yahei", 15)).grid(row=4, column = 0)
		tk.Checkbutton(self.window, text=txt('Monk', CHN), variable=monkVar, onvalue=1, \
						offvalue=0, font=("Yahei", 15, "bold")).grid(row=5, column = 0)
		tk.Checkbutton(self.window, text=txt('SV', CHN), variable=SVVar, onvalue=1, \
						offvalue=0, font=("Yahei", 15, "bold")).grid(row=6, column = 0)
		
		tk.Button(self.window, text=txt("Load a Game, or\nGo 2nd using Info from Opponent", CHN), bg="green3", font=("Yahei", 15, "bold"), 
				command=lambda : var.set(2)).grid(row=4, column=2)
		#Middle column
		ckb = tk.Checkbutton(self.window, text=txt("Show Send Info Reminder", CHN), variable=self.showReminder, onvalue=1, \
						offvalue=0, font=("Yahei", 15, "bold"))
		ckb.select()
		ckb.grid(row=3, column=1)
		sidePanelonLeft.grid(row=2, column=1)
		#Right half 
		tk.Label(self.window, text=txt("Load a Game, or\nGo 2nd using Info from Opponent", CHN) \
				, font=("Yahei", 15, "bold")).grid(row=0, column=2)
		LoadPickleButton(self, self.window).grid(row=1, column=2)
		tk.Label(self.window, text=txt("Load Update from Opponent", CHN) \
				, font=("Yahei", 15)).grid(row=2, column=2)
		tempGuides.grid(row=3, column=2)
		#如果没有勾选，则显示提醒内容
		if self.showReminder.get():
			messagebox.showinfo(message=txt("To go 1st, use left panel to decide the DIY expansion and game board.\nTo go 2nd/load a saved game, use right panel to enter info from your opponent/select a .p file", CHN))
		self.window.wait_variable(var)
		
	def initLoadDeckUI(self, onLeft):
		self.GamePanel = tk.Frame(master=self.window, width=X, height=Y, bg="black")
		self.sidePanel = tk.Frame(master=self.window, width=int(0.005*X), height=int(0.3*Y), bg="cyan")
		
		img = PIL.Image.open(r"Images\PyHSIcon.png").resize((75, 75))
		ph = PIL.ImageTk.PhotoImage(img)
		self.lbl_Card = tk.Label(self.sidePanel, image=ph)
		self.lbl_Card.image = ph
		self.lbl_wish = tk.Label(master=self.sidePanel)
		self.infoExchangePanel = InfoExchangePanel(self)
		self.deckImportPanel = tk.Frame(master=self.sidePanel, width=0.005*X, height=int(0.6*Y))
		
		self.GamePanel.pack(fill=tk.Y, side=tk.RIGHT if onLeft else tk.LEFT)
		self.sidePanel.pack(side=tk.TOP)
		self.lbl_Card.pack()
		self.deckImportPanel.pack(side=tk.TOP)
		self.infoExchangePanel.pack(side=tk.TOP)
		
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