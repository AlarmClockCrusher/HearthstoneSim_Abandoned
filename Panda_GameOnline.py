from direct.gui.DirectGui import *
from direct.interval.IntervalGlobal import Wait, Func
from direct.showbase.ShowBase import ShowBase
from direct.task import Task

from Code2CardList import *
from Game import *
from GenPools_BuildDecks import *
from Panda_CustomWidgets import *

from datetime import datetime
from collections import deque
from numpy.random import choice as npchoice

import tkinter as tk
from tkinter import messagebox

import socket, threading, subprocess, platform, numpy

from Panda_UICommonPart import *


class Layer1Window:
	def __init__(self):
		self.window = tk.Tk()
		self.btn_Connect = tk.Button(self.window, text=txt("Loading. Please wait", CHN), bg="red",
									 font=("Yahei", 20, "bold"), command=self.initConntoServer)
		self.btn_Reconn = tk.Button(self.window, text=txt("Loading. Please wait", CHN), bg="red",
									font=("Yahei", 13, "bold"), command=self.reconnandResume)
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		
		self.gameGUI = GUI_Online(self)
		self.lbl_LoadingProgress = tk.Label(master=self.window, text='', font=("Yahei", 15))
		self.lbl_LoadingProgress.grid(row=4, column=0, columnspan=2)
		
		"""Create the server conn widgets"""
		self.serverIP_Entry = tk.Entry(self.window, font=("Yahei", 20), width=10)
		self.queryPort_Entry = tk.Entry(self.window, font=("Yahei", 20), width=10)
		self.tableID_Entry = tk.Entry(self.window, font=("Yahei", 20), width=10)
		self.serverIP_Entry.insert(0, "127.0.0.1")
		self.queryPort_Entry.insert(0, "65432")
		self.tableID_Entry.insert(0, "200")  #"%d"%numpy.random.randint(6000)
		
		"""Create the hero class selection menu"""
		self.entry_Deck = tk.Entry(self.window, font=("Yahei", 13), width=30)
		
		"""Place the widgets"""
		tk.Label(self.window, text=txt("Server IP Address", CHN), font=("Yahei", 20)).grid(row=0, column=0)
		tk.Label(self.window, text=txt("Query Port", CHN), font=("Yahei", 20)).grid(row=1, column=0)
		tk.Label(self.window, text=txt("Table ID to join", CHN), font=("Yahei", 20)).grid(row=2, column=0)
		self.serverIP_Entry.grid(row=0, column=1)
		self.queryPort_Entry.grid(row=1, column=1)
		self.tableID_Entry.grid(row=2, column=1)
		
		self.btn_Connect.grid(row=5, column=0)#, columnspan=2)
		self.btn_Reconn.grid(row=5, column=1)
		
		tk.Label(self.window, text="         ").grid(row=0, column=2)
		tk.Label(self.window, text=txt("Enter Deck code", CHN), font=("Yahei", 20)).grid(row=0, column=3)
		self.entry_Deck.grid(row=1, column=3)
		self.lbl_DisplayedCard = tk.Label(self.window)
		self.lbl_DisplayedCard.grid(row=6, column=0, columnspan=2)
		
		self.heroClass = "Demon Hunter"
		self.panel_Class = Panel_ClassSelection(master=self.window, UI=self, ClassPool=list(Class2HeroDict.keys()),
							 					Class_0="Demon Hunter", varName="hero")
		self.panel_Class.grid(row=2, column=3, columnspan=2)
		panel_DeckComp = tk.Frame(self.window)
		panel_DeckComp.grid(row=0, column=5, rowspan=5)
		self.lbl_Types = tk.Label(panel_DeckComp, text="Minion:0\nSpell:0\nWeapon:0\nHero:0\nAmulet:0", font=("Yahei", 16, "bold"), anchor='e')
		self.canvas_ManaDistri = tk.Canvas(panel_DeckComp, width=250, height=120)
		#Either pressing the button or hitting enter in the entries will refresh the deck composition
		btn_Refresh = tk.Button(self.window, text="刷新", font=("Yahei", 15, "bold"), bg="green3")
		btn_Refresh.bind("<Button-1>", self.updateDeckComp)
		btn_Refresh.grid(row=1, column=4)
		self.entry_Deck.bind("<Return>", self.updateDeckComp)
		
		self.manaObjsDrawn = []
		self.ls_LabelCardsinDeck = []
		self.lbl_Types.grid(row=0, column=0)
		self.canvas_ManaDistri.grid(row=0, column=1)
		for mana in range(8):
			X, Y = (0.125 + 0.1 * mana) * manaDistriWidth, 0.95 * manaDistriHeight
			self.canvas_ManaDistri.create_text(X, Y, text=str(mana) if mana < 7 else "7+", font=("Yahei", 12, "bold"))
			
		self.panel_Deck = tk.Frame(self.window)
		self.panel_Deck.grid(row=6, column=2, rowspan=3, columnspan=4)
		
		self.freezeBtns = False
		from Hand import Default1
		self.deck_0 = Default1
		self.updateDeckComp(None)
		
		#Threading和wait_variable不兼容
		self.canStartMulligan = False
		threading.Thread(target=self.gameGUI.preload, daemon=True).start()
		"""self.window constantly checks if the game can start mulligan after 0.5seconds"""
		self.window.after(500, self.closeLayer1andInitMulligan)
		#self.gameGUI.initMulliganDisplay()
		#self.gameGUI.run()
		self.window.mainloop()
	
	def closeLayer1andInitMulligan(self):
		if self.canStartMulligan:
			self.window.destroy()
			self.init_ShowBase()
			#self.gameGUI.initMulliganDisplay()
			#self.gameGUI.run()
		else: self.window.after(500, self.closeLayer1andInitMulligan)
		
	def updateDeckComp(self, event):
		makeCardPool(0, 0)
		#deck and hero parsing
		self.deck, deckCorrect, hero = parseDeckCode(self.entry_Deck.get(), self.heroClass, Class2HeroDict, defaultDeck=self.deck_0)
		if not deckCorrect: messagebox.showinfo(message=txt("Deck incorrect", CHN))
		self.panel_Class.setSelection(hero.Class)
		
		lbl, deck, manaObjsDrawn = self.lbl_Types, self.deck, self.manaObjsDrawn
		canvas, ls_Labels, panelDeck = self.canvas_ManaDistri, self.ls_LabelCardsinDeck, self.panel_Deck
		cardTypes = {"Minion": 0, "Spell": 0, "Weapon": 0, "Hero": 0, "Amulet": 0}
		for lbl_Card in ls_Labels: lbl_Card.destroy()
		ls_Labels.clear()
		indices = np.array([card.mana for card in deck]).argsort()
		for i, index in enumerate(indices):
			card = deck[index]
			label = Label_CardinDeck(master=panelDeck, UI=self, card=card)
			label.grid(row=i % 15, column=int(i / 15))
			ls_Labels.append(label)
			cardTypes[card.type] += 1
			
		self.lbl_Types["text"] = "Minion: %d\nSpell: %d\nWeapon: %d\nHero: %d\nAmulet: %d" % (
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
	
	def showCards(self):
		pass
	
	def removeCardfromDeck(self, card):
		pass
	
	def initConntoServer(self):
		if self.gameGUI.loading != "Start!" or self.freezeBtns:
			return
		
		makeCardPool(0, 0)
		deck, deckCorrect, hero = parseDeckCode(self.entry_Deck.get(), self.heroClass, Class2HeroDict, defaultDeck=self.deck_0)
		if not deckCorrect:
			messagebox.showinfo(message=txt("Deck incorrect", CHN))
			return
		
		serverIP = self.serverIP_Entry.get()
		param = '-n' if platform.system().lower() == 'windows' else '-c'
		command = ["ping", param, '1', serverIP]
		if subprocess.call(command) != 0:
			messagebox.showinfo(message=txt("Can't ping the address ", CHN)+serverIP)
			return
		try:
			self.sock.connect((serverIP, int(self.queryPort_Entry.get())))  #Blocks. If the server port turns this attempt down, it raises error
		except ConnectionRefusedError:
			messagebox.showinfo(message=txt("Can't connect to the server's query port", CHN))
			return
		
		#self.reserveJoinaTable(serverIP, hero, deck)
		threading.Thread(target=self.reserveJoinaTable, args=(serverIP, hero, deck), daemon=True).start()
		
	def reserveJoinaTable(self, serverIP, hero, deck):
		self.freezeBtns = True
		#Wait for info from the query port at the server. Possible responses:
			#b"No Ports Left"
			#b"Port available"
		info_PortAvailability = self.sock.recv(1024)
		if info_PortAvailability == b"No Ports Left":
			self.freezeBtns = False
			messagebox.showinfo(message=txt("No tables left. Please wait for openings", CHN))
		elif info_PortAvailability.startswith(b"Port available"):  #b"Ports,65433"
			port = int(info_PortAvailability.split(b',')[1])
			
			#After getting available ports, send the table ID wanted and see if it is available
			tableID = self.tableID_Entry.get()
			self.sock.sendall(b"Table ID,"+tableID.encode())
			info_TableAvailability = self.sock.recv(1024)
			#Possible responses:
				#b"Use another Table ID"
				#b"Join Reserved Table via Port||24123"
				#b"Table can be Reserved"
			if info_TableAvailability.startswith(b"Use another Table ID"):
				self.freezeBtns = False
				messagebox.showinfo(message=txt("This table ID is already taken", CHN))
				return
			elif info_TableAvailability.startswith(b"Join Reserved Table via Port"):
				port = int(info_TableAvailability.split(b"||")[1])
				print("Will join a reserved table via port", port)
			else: #info_TableAvailability can be b"Table can be Reserved"
				print("Successfully reserved a table. Connect via port", port)
				self.lbl_LoadingProgress.config(text=txt("Successfully reserved a table", CHN), font=("Yahei", 17, "bold"), fg="purple1")
			#A table has been assigned on the server side at this point.
			print("Now trying to connect to an available table port", port)
			self.sock.close()
			self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			self.sock.connect((serverIP, port))
			
			#After connecting to table port, get playerID, boardID and the RNG seed
			b"PlayerID BoardID Seed||playerID||boardID||seed" #is the info received
			info_PlayerID_BoardID_Seed = self.sock.recv(1024)
			header, ID, boardID, seed = info_PlayerID_BoardID_Seed.split(b"||")
			self.gameGUI.ID = int(ID)
			self.gameGUI.Game.boardID = self.gameGUI.boardID = boardID.decode()
			
			#Send the server the hero and deck info. Wait for opponents info
			self.sock.sendall(b"Hero Picked||"+pickleObj2Bytes(hero))
			info_Opponent = self.sock.recv(1024)  #socket之间的连接中断时，socket本身不会立即报错，而是会在尝试发送信息的时候才会发现错误
			#When get the opponent info, can then start the mulligan
			if info_Opponent.startswith(b"Enemy Hero Picked"):
				head, heroPickle = info_Opponent.split(b"||")
				hero_Oppo = unpickleBytes2Obj(heroPickle)
				print("\n**********\nBoth player connected to server. Start mulligan of game\n**********")
				if self.gameGUI.ID == 1:
					self.gameGUI.Game.initialize_Details(self.gameGUI.boardID, int(seed), RNGPools, hero, hero_Oppo, deck1=deck)
				else:
					self.gameGUI.Game.initialize_Details(self.gameGUI.boardID, int(seed), RNGPools, hero_Oppo, hero, deck2=deck)
				
				self.canStartMulligan = True
				#self.init_ShowBase() #从这里进入单人的换牌阶段
			
		else: print("Received smth else", info_PortAvailability)
	
	def reconnandResume(self):
		pass
	
	#data = b"Start Mulligan||1/2||bytes(boardID)||heroPickled"
	def init_ShowBase(self):
		print("Try to destroy the layer 1 window, with threads running")
		self.gameGUI.sock = self.sock
		#self.window.destroy()
		print("Before init mulligan display, threads are\n", threading.current_thread(), threading.enumerate())
		self.gameGUI.initMulliganDisplay()
		self.gameGUI.run()
		print("Able to reach the end of the layer 1 window")
	
class GUI_Online(Panda_UICommon):
	def __init__(self, layer1Window):
		super().__init__()
		self.layer1Window = layer1Window
		self.sock = None
		self.waiting4Server, self.timer = False, 60
		
	def preload(self):
		self.prepareTexturesandModels(self.layer1Window)
		print("Finished loading")
		self.loading = "Start!"
		self.layer1Window.btn_Connect.config(text=txt("Finished Loading. Start!", CHN))
		self.layer1Window.btn_Reconn.config(text=txt("Resume interrupted game", CHN))
		self.layer1Window.btn_Connect.config(bg="green3")
		self.layer1Window.btn_Reconn.config(bg="yellow")
		
	def initMulliganDisplay(self):
		self.handZones = {1: HandZone(self, 1), 2: HandZone(self, 2)}
		self.minionZones = {1: MinionZone(self, 1), 2: MinionZone(self, 2)}
		self.heroZones = {1: HeroZone(self, 1), 2: HeroZone(self, 2)}
		self.deckZones = {1: DeckZone(self, 1), 2: DeckZone(self, 2)}
		
		self.initGameDisplay()
		btn_Mulligan = DirectButton(text=("Confirm", "Confirm", "Confirm", "Confirm"), scale=0.08,
									command=self.mulligan_PreProcess)
		
		#Draw the animation of mulligan cards coming out of the deck
		ID = self.ID
		self.posMulligans = {1: [(-7, 1.5, 10), (0, 1.5, 10), (7, 1.5, 10)],
							 2: [(-8.25, 1.5, 10), (-2.75, 1.5, 10), (2.75, 1.5, 10), (8.25, 1.5, 10)]}[ID]
		deckZone, handZone, i = self.deckZones[ID], self.handZones[ID], 0
		pos_0, hpr_0 = deckZone.pos, (90, 90, 0)
		cards2Mulligan = self.Game.mulligans[ID]
		mulliganBtns = []
		for card, pos, hpr, scale in zip(cards2Mulligan, [pos_0] * len(cards2Mulligan), [hpr_0] * len(cards2Mulligan), [1] * len(cards2Mulligan)):
			mulliganBtns.append(genCard(self, card, isPlayed=False, pos=pos, hpr=hpr, scale=scale)[1])
		for btn, pos in zip(mulliganBtns, self.posMulligans):
			Sequence(Wait(0.4 + i * 0.4), btn.genLerpInterval(pos=pos, hpr=(0, 0, 0), scale=1, duration=0.5)).start()
			i += 1
		
		print("1", self.sock)
		btn_Mulligan["extraArgs"] = [btn_Mulligan]
		btn_Mulligan.setPos(0, 0, -0.35)
		self.taskMgr.add(self.mouseMove, "Task_MoveCard")
	
	def mulligan_PreProcess(self, btn_Mulligan):
		#需要在这里等待对方的洗牌完成
		ID, self.UI = self.ID, 0
		indices = [i for i, status in enumerate(self.mulliganStatus[self.ID]) if status]
		btn_Mulligan.destroy()
		game = self.Game
		for i in indices: game.mulligans[ID][i].btn.np.removeNode()
		
		game.Hand_Deck.mulligan1Side(ID, indices)
		handDeck = [[type(card) for card in game.Hand_Deck.hands[self.ID]], [type(card) for card in game.Hand_Deck.decks[self.ID]]]
		#self.sendMulliganedDeckHand2Server(handDeck, game)
		threading.Thread(target=self.sendMulliganedDeckHand2Server, args=(handDeck, game), daemon=True).start()
		
	def sendMulliganedDeckHand2Server(self, handDeck, game):
		time.sleep(0.5)
		self.sock.sendall(b"Exchange Deck&Hand||%s"%pickleObj2Bytes(handDeck))
		info_HandDeckfromOppo = self.sock.recv(1024)
		print("Received deck hand info from enemy")
		if info_HandDeckfromOppo.startswith(b"Start Game with Oppo Hand_Deck"):
			header, handDeck_Oppo = info_HandDeckfromOppo.split(b"||")
			print("Deck info byte string length is", len(handDeck_Oppo))
			hand, deck = unpickleBytes2Obj(handDeck_Oppo) #IF THE DECK IS TOO LONG, THEN 1024 IS NOT ENOUGH TO SEND ALL INFO
			ID_Oppo = 3 - self.ID
			game.Hand_Deck.decks[ID_Oppo] = [card(game, ID_Oppo) for card in deck]
			game.Hand_Deck.hands[ID_Oppo] = [card(game, ID_Oppo) for card in hand]
			#此时双方手牌中的牌都还没有进行entersHand、entersDeck处理。留给game.Hand_Deck.finalizeHandDeck_StartGame处理
			self.UI = 0
			print("\n-----------------\nStart the game as PLAYER %d\n----------------"%self.ID)
			game.Hand_Deck.finalizeHandDeck_StartGame()
			#If ID is 2, wait for move from enemy
			if self.ID == 2: self.startWaiting4EnemyMove()
		elif info_HandDeckfromOppo.startswith(b"Opponent Disconnected"):
			OnscreenText(text="Opponent disconnected. Closing", pos=(0, 0))
			Sequence(Wait(2), Func(quit)).start()
			
	#Returns a sequence to be started later
	def mulligan_NewCardsfromDeckAni(self, ID, addCoin=True):
		#At this point, the Coin is added to the Game.mulligans[2]
		if addCoin: genCard(self, card=self.Game.mulligans[2][-1], isPlayed=False, pos=(13.75, 1.5, 10))
		
		#开始需要生成一个Sequence，然后存储在seqHolder里面
		para = Parallel()
		deckZone, handZone = self.deckZones[ID], self.handZones[ID]
		pos_DeckZone, hpr_0 = deckZone.pos, (90, 90, 0)
		indices, cards2Mulligan = [], []
		for i, card in enumerate(self.Game.mulligans[ID]):
			if not card.btn:
				indices.append(i)
				cards2Mulligan.append(card)
		
		mulliganBtns = []
		for card, pos, hpr in zip(cards2Mulligan, [pos_DeckZone] * len(cards2Mulligan), [hpr_0] * len(cards2Mulligan)):
			mulliganBtns.append(genCard(self, card, isPlayed=False, pos=pos, hpr=hpr, scale=1)[1])
			print("Card to come out deck", card, card.btn.np.getPos())
		for btn, i in zip(mulliganBtns, indices):
			para.append(btn.genLerpInterval(pos=self.posMulligans[i], hpr=(0, 0, 0), scale=1, duration=0.5))
		
		self.Game.Hand_Deck.hands[ID] = self.Game.mulligans[ID]
		#已经把所有新从牌库里面出来的牌画在了牌库里面
		para.start()#self.seqHolder = [Sequence(para, Wait(1))]
		
	def wait4Enemy2Reconnect(self):
		self.timer, self.UI = 60, -2
		timerText = OnscreenText(text="Wait for Opponent to Reconnect: "+"60s",
					pos=(0, 0), scale = 0.1, fg = (1, 0, 0, 1), bg = (1, 1, 1, 1),
					align = TextNode.ACenter, mayChange = 1, font = self.font
					)
		thread_data = threading.Thread(target=self.wait4Reconn, daemon=True)
		thread_timer = threading.Thread(target=self.timerCountdown, args=(timerText, ), daemon=True)
		thread_data.start()
		thread_timer.start()
	
	def timerCountdown(self, timerText):
		print("Start countdown")
		while self.timer > 0 and self.UI < -1:
			time.sleep(1)
			timerText["text"] = "Wait for Opponent to Reconnect: " + "%ds" % self.timer
			self.timer -= 1
		print("Finished sending game copy to server")
		if self.timer < 1:
			timerText["text"] = txt("Opponent failed to reconnect.\nClosing in 2 seconds", CHN)
			Sequence(Wait(2), Func(self.destroy)).start()
		else:
			timerText.destroy()
	
	def wait4Reconn(self):
		data = self.sock.recv(1024)
		if data.startswith(b"Copy Your Game"):
			self.timer, self.UI = 60, -1  #当收到开始复制的要求时就可以停止倒计时
			gameCopy = self.Game.copyGame()[0]
			gameCopy.GUI = None
			gameCopyInfo = pickleObj2Bytes(gameCopy)
			#因为gameCopy会比较大，所以需要分段进行传输
			numPieces = 1 + round(len(gameCopyInfo) / 950)
			print("%d pieces to send" % numPieces)
			pieces = []
			for i in range(numPieces - 1):
				pieces.append(gameCopyInfo[i * 950:i * 950 + 950])
			numPiecesReceived = 0
			pieces.append(gameCopyInfo[numPieces * 950 - 950:])
			self.sock.sendall(b"1st Copy Piece||%d||%d||%s" % (self.Game.turn, numPieces, pieces[0]))
			data = self.sock.recv(1024)
			print(data)
			if data.startswith(b"Received"):
				print("First pc of copy received. Send the rest")
				numPiecesReceived += 1
				for i, piece in enumerate(pieces[1:-1]):
					self.sock.sendall(b"Copy Piece_%d||%s" % (i + 1, piece))
					data = self.sock.recv(1024)
					if data.startswith(b"Received."):
						print("Copy pc %d delivered. Will keep sending copies" % (i + 1))
						numPiecesReceived += 1
				self.sock.sendall(b"Last Copy Piece||%s" % pieces[-1])
				data = self.sock.recv(1024)
				print("Data after sending last copy piece", data)
				if data == b"All Pieces Received":
					numPiecesReceived += 1
					print("Finished sending %d pieces. Num Pieces Received %d" % (numPieces, numPiecesReceived))
			else:
				print("Received smth else")
		else:
			print("Opponent table ID is wrong")
		self.UI = 0
	
	def startWaiting4EnemyMove(self):
		threading.Thread(target=self.wait4EnemyMoveFunc, daemon=True).start()
	
	def wait4EnemyMoveFunc(self):
		self.UI, self.waiting4Server = -2, True
		while self.waiting4Server:
			data = self.sock.recv(1024)
			print("While waiting, received something from server\n   ", data)
			if data:
				if data.startswith(b"Game Move"):
					self.decodePlayfromServer(data)  #会自行处理waiting4Server和UI的重置
				elif data.startswith(b"Opponent Disconnected"):
					self.wait4Enemy2Reconnect()  #在这等待对方的重连，重连之后self.UI会被设回0，从而我方可以继续操作
			print("Keep waiting for enemy plays? {}. Self ID {}, current turn {}".format(self.waiting4Server, self.ID, self.Game.turn))
	
	def decodePlayfromServer(self, data):
		header, moves, picks = data.split(b"||")
		moves, picks = unpickleBytes2Obj(moves), unpickleBytes2Obj(picks)
		print("Decoding move", moves, picks)
		if isinstance(moves, list):
			self.Game.evolvewithGuide(moves, picks)
		self.waiting4Server = self.ID != self.Game.turn
		self.UI = -2 if self.waiting4Server else 0
		#print("\n\n*******Decoded play from server*******")
		#self.checkCardsDisplays(checkHand=True)
		
	def receivePiecesofGameCopy(self, tableID):
		self.UI = -2
		pcsText = OnscreenText(text="Receiving Game Copies from Opponent: " + "0%",
							   	pos=(0, 0), scale = 0.1, fg = (1, 0, 0, 1), bg = (1, 1, 1, 1),
								align = TextNode.ACenter, mayChange = 1, font = self.font
								)
		thread = threading.Thread(target=self.receiveandUpdateCount, args=(tableID, pcsText), daemon=True)
		thread.start()
	
	def receiveandUpdateCount(self, tableID, pcsText):
		self.UI = -2
		numPiecesTotal, numPiecesReceived, buffer = 0, 0, b''
		print("Ready for data transfer")
		
		print("Start requesting game copy")
		self.sock.sendall(b"Request to Rejoin Table||%s" % bytes(tableID.encode()))
		#已经验证过这个sock的connection正常注册进了server的table里面
		while True:
			data = self.sock.recv(1024)
			print(data[:20])
			if data.startswith(b"Resume with Copy"):  #Receive the first piece of the game copy
				print("First pc of copy received")
				header, yourID, boardID, num, gameCopyInfo = data.split(b"||")
				boardID, numPiecesTotal = str(boardID.decode()), int(num)
				numPiecesReceived += 1
				buffer += gameCopyInfo
				#time.sleep(0.01)
				self.sock.sendall(b"Received. Keep Sending")
			elif data.startswith(b"Copy Piece"):
				print("Copy pc %s received. Provider should keep sending" % str(data.split(b"||")[0].split(b'_')[1].decode()))
				numPiecesReceived += 1
				buffer += data.split(b"||")[1]
				#time.sleep(0.01)
				self.sock.sendall(b"Received. Keep Sending")
			elif data.startswith(b"Last Copy Piece"):
				print("Last piece received.")
				numPiecesReceived += 1
				buffer += data.split(b"||")[1]
				#time.sleep(0.01)
				self.sock.sendall(b"All Pieces Received")
				break
			elif data == b"Table ID wrong/occupied. Cannot resume":
				messagebox.showinfo(message=txt("Want to request game copy. But table iD is wrong", CHN))
				return
			if numPiecesReceived % 5 == 1:
				pcsText["text"] = txt("Receiving Game Copies from Opponent: ", CHN) + "%d/%d" % (numPiecesReceived, numPiecesTotal)
		print("Received %d pieces out of %d in total" % (numPiecesReceived, numPiecesTotal))
		try:
			gameCopy = unpickleBytes2Obj(buffer)
			gameCopy.GUI = self
		except Exception as e:
			print("Failed to parse the game. Exception:", e)
		
		self.Game, self.ID, self.boardID = gameCopy, int(yourID), boardID
		pcsText.destroy()
		self.initGameDisplay()
		self.UI = 0
		if self.ID != self.Game.turn:
			self.startWaiting4EnemyMove()
	
	def sendOwnMovethruServer(self, endingTurn=False):
		game = self.Game
		moves, picks = game.moves, game.picks
		game.moves, game.picks = [], []
		if moves:
			s = b"Game Move||" + pickleObj2Bytes(moves) + b"||" + pickleObj2Bytes(picks)
			print("Sending plays thru server", moves, picks)
			self.sock.sendall(s)
			self.UI = -2 #需要把这个调成-2，然后等server回传move送达到另一方的消息
			data = self.sock.recv(1024)
			#目前是我们的回合，所以对方断线重连了之后可以继续出牌
			print("Response of sending our play --", data)
			if data:
				if data == b"Move Received":
					self.UI = -2 if endingTurn else 0
				elif data == b"Opponent Disconnected":
					self.wait4Enemy2Reconnect()  #在这等待对方的重连，重连之后self.UI会被设回0，从而我方可以继续操作
			if endingTurn: self.startWaiting4EnemyMove()
			


Layer1Window()