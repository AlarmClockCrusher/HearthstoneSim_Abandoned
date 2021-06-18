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
		self.btn_Connect = tk.Button(self.window, text=txt("Loading. Please wait", CHN), bg="red", font=("Yahei", 20, "bold"), command=self.initConntoServer)
		self.btn_Reconn = tk.Button(self.window, text=txt("Loading. Please wait", CHN), bg="red", font=("Yahei", 13, "bold"), command=self.reconnandResume)
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		
		self.gameGUI = GUI_Online(self)
		
		"""Create the server conn widgets"""
		self.serverIP_Entry = tk.Entry(self.window, font=("Yahei", 20), width=10)
		self.queryPort_Entry = tk.Entry(self.window, font=("Yahei", 20), width=10)
		self.tableID_Entry = tk.Entry(self.window, font=("Yahei", 20), width=10)
		self.serverIP_Entry.insert(0, "127.0.0.1")
		self.queryPort_Entry.insert(0, "65432")
		self.tableID_Entry.insert(0, "200")  #"%d"%numpy.random.randint(6000)
		
		"""Create the hero class selection menu"""
		self.hero_Var = tk.StringVar(self.window)
		self.hero_Var.set(list(ClassDict.keys())[0])
		hero_Opt = tk.OptionMenu(self.window, self.hero_Var, *list(ClassDict.keys()))
		hero_Opt.config(width=15, font=("Yahei", 20))
		hero_Opt["menu"].config(font=("Yahei", 20))
		
		self.deck_Entry = tk.Entry(self.window, font=("Yahei", 13), width=30)
		
		"""Place the widgets"""
		tk.Label(self.window, text=txt("Server IP Address", CHN), font=("Yahei", 20)).grid(row=0, column=0)
		tk.Label(self.window, text=txt("Query Port", CHN), font=("Yahei", 20)).grid(row=1, column=0)
		tk.Label(self.window, text=txt("Table ID to join", CHN), font=("Yahei", 20)).grid(row=2, column=0)
		self.serverIP_Entry.grid(row=0, column=1)
		self.queryPort_Entry.grid(row=1, column=1)
		self.tableID_Entry.grid(row=2, column=1)
		
		self.btn_Connect.grid(row=4, column=0, columnspan=2)
		self.btn_Reconn.grid(row=4, column=4)
		
		tk.Label(self.window, text="         ").grid(row=0, column=2)
		tk.Label(self.window, text=txt("Hero class", CHN), font=("Yahei", 20)).grid(row=1, column=3)
		tk.Label(self.window, text=txt("Enter Deck code", CHN), font=("Yahei", 20)).grid(row=2, column=3)
		hero_Opt.grid(row=1, column=4)
		self.deck_Entry.grid(row=2, column=4)
		
		self.window.mainloop()
	
	def initConntoServer(self):
		if self.gameGUI.loading != "Start!":
			return
		
		boardID = makeCardPool("0 Random Game Board", 0, 0)
		from CardPools import cardPool, MinionsofCost, ClassCards, NeutralCards, RNGPools
		
		for key, value in cardPool.items():
			if value.name == "Transfer Student":
				print("Search the card pool found", key, value)
		
		hero, deckCode = ClassDict[self.hero_Var.get()], self.deck_Entry.get()
		print("Hero type and deck code:", hero, deckCode)
		deck, deckCorrect, hero = parseDeckCode(deckCode, hero, ClassDict)
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
		data = self.sock.recv(1024)
		if data.startswith(b"Ports"):  #b"Ports,65433,65434"
			print("Received available ports", data)
			ports = data.decode().split(',')[1:]
			print("Now trying to connect to an available port", ports[0])
			self.sock.close()
			self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			self.sock.connect((serverIP, int(ports[0])))  #Take the first available port returned from the server
			#Send the server the hero info and deck info, and tableID to request
			tableID = self.tableID_Entry.get()
			print("Attemp to start/join a tableID with info", tableID, type(tableID.encode()), type(bytes(tableID.encode())))
			#首先会询问服务器，然后服务器返回一个
			print("Sending table distribution request:", b"Start/Join a Table||" + bytes(tableID.encode()) + b"||" + pickleObj2Bytes(hero))
			self.sock.sendall(b"Start/Join a Table||" + bytes(tableID.encode()) + b"||" + pickleObj2Bytes(hero))
			print("Waiting for response from server about START/JOIN TABLE request")
			data = self.sock.recv(1024)  #socket之间的连接中断时，socket本身不会立即报错，而是会在尝试发送信息的时候才会发现错误
			print("Received response to START/JOIN TABLE request:", data)
			#可能的data有
			# 	b"Use another Table ID"，
			# 	b"Table reserved. Wait"，
			# 	b"Start Mulligan||1||%s||%s"%(bytes(table.boardID.encode()), table.heroes[2])
			# 	b"Start Mulligan||2||%s||%s"%(bytes(table.boardID.encode()), table.heroes[1])
			if data:
				#预订到桌子的玩家会收到这个信息，而加入到桌子的玩家会直接收到b"Start Mulligan||x||xxx||xxx"
				if data.startswith(b"Table reserved"):  #向服务发送预订/加入桌子的申请后，服务器会返回ID对已经被占用 / 或者预订成功
					print("Your table has been reserved. Start waiting for an opponent to join the table")
					data = self.sock.recv(1024)  #期待收到b"Start Mulligan|1|26 Darkmoon Faire|Uther",从而开始起手调度过程
					if data:  #开始起手调度,需要初始化游戏
						print("Opponent Joined. Confirm card pool and start your mulligan")
						head, ID_Bytes, boardID_Bytes, heroPickled = data.split(b"||")
						print(head, ID_Bytes, boardID_Bytes, heroPickled)
						self.gameGUI.ID = int(ID_Bytes.decode())
						boardID_fromServer = boardID_Bytes.decode()
						self.gameGUI.boardID = boardID_fromServer
						transferStudent_New = transferStudentPool[boardID_fromServer]
						for key, value in list(cardPool.items()):
							if value.name == "Transfer Student":
								del cardPool[key]
						cardPool[transferStudent_New.index] = transferStudent_New
						if transferStudent_New.index.endswith("ToCorrupt"):
							cardPool[TransferStudent_Darkmoon_Corrupt.index] = TransferStudent_Darkmoon_Corrupt
						
						hero_Opponent = unpickleBytes2Obj(heroPickled)
						if self.gameGUI.ID == 1:
							self.gameGUI.Game.initialize_Details(cardPool, ClassCards, NeutralCards, MinionsofCost, RNGPools, hero, hero_Opponent, deck1=deck)
						else:
							self.gameGUI.Game.initialize_Details(cardPool, ClassCards, NeutralCards, MinionsofCost, RNGPools, hero_Opponent, hero, deck2=deck)
						self.init_ShowBase()
				elif data.startswith(b"Start Mulligan"): #b"Start Mulligan||1/2||bytes(boardID)||heroPickled"
					print("You have joined a table. Start your mulligan")
					head, ID_Bytes, boardID_Bytes, heroPickled = data.split(b"||")
					print(head, ID_Bytes, boardID_Bytes, heroPickled)
					self.gameGUI.ID = int(ID_Bytes.decode())
					boardID_fromServer = boardID_Bytes.decode()
					#Replace the randomly chosen transfer student type based on the boardId from the server
					self.gameGUI.boardID = boardID_fromServer
					
					transferStudent_New = transferStudentPool[boardID_fromServer]
					for key, value in list(cardPool.items()):
						if value.name == "Transfer Student":
							del cardPool[key]
					cardPool[transferStudent_New.index] = transferStudent_New
					if transferStudent_New.index.endswith("ToCorrupt"):
						cardPool[TransferStudent_Darkmoon_Corrupt.index] = TransferStudent_Darkmoon_Corrupt
					
					hero_Opponent = unpickleBytes2Obj(heroPickled)
					if self.gameGUI.ID == 1:
						self.gameGUI.Game.initialize_Details(cardPool, ClassCards, NeutralCards, MinionsofCost, RNGPools, hero, hero_Opponent, deck1=deck)
					else:
						self.gameGUI.Game.initialize_Details(cardPool, ClassCards, NeutralCards, MinionsofCost, RNGPools, hero_Opponent, hero, deck2=deck)
					self.init_ShowBase()
				elif data == b"Use another table ID":
					messagebox.showinfo(message=txt("This table ID is already taken", CHN))
		elif data == b"No Ports Left":
			messagebox.showinfo(message=txt("No tables left. Please wait for openings", CHN))
		else:
			print("Received smth else", data)
	
	def reconnandResume(self):
		pass
	
	#data = b"Start Mulligan||1/2||bytes(boardID)||heroPickled"
	def init_ShowBase(self):
		self.gameGUI.sock = self.sock
		self.window.destroy()
		#print("Before init mulligan display, threads are\n", threading.current_thread(), threading.enumerate())
		self.gameGUI.initMulliganDisplay()
		self.gameGUI.run()
		
	
class GUI_Online(Panda_UICommon):
	def __init__(self, layer1Window):
		super().__init__(layer1Window)
		self.sock = None
		self.waiting4Server, self.timer = False, 60
		
	def preloadModel(self, btn_Connect, btn_Reconn):
		self.prepareModels()
		btn_Connect.config(text=txt("Finished Loading. Start!", CHN))
		btn_Reconn.config(text=txt("Resume interrupted game", CHN))
		btn_Connect.config(bg="green3")
		btn_Reconn.config(bg="yellow")
	
	def initMulliganDisplay(self):
		threading.Thread(target=self.initGameDisplay).start()
		
		if self.ID == 1: self.posMulligans = [(8 * (i - 1), 50, -5) for i in range(len(self.Game.mulligans[1]))]
		else: self.posMulligans = [(4 + 8 * (i - 2), 50, -5) for i in range(len(self.Game.mulligans[2]))]
		
		mulliganBtns = []
		for pos, card in zip(self.posMulligans, self.Game.mulligans[self.ID]):
			mulliganBtns.append(self.addinDisplayCard(card, pos, scale=0.7))
		
		btn_Mulligan = DirectButton(text=("Confirm", "Confirm", "Confirm", "Confirm"), scale=0.08,
									command=self.startMulligan)
		print("1", self.sock)
		btn_Mulligan["extraArgs"] = [mulliganBtns, btn_Mulligan]
		btn_Mulligan.setPos(0, 0, 0)
		self.taskMgr.add(self.mouseMove, "Task_MoveCard")
	
	def startMulligan(self, mulliganBtns, btn_Mulligan):
		#需要在这里等待对方的洗牌完成
		self.UI = 0
		indices = [i for i, status in enumerate(self.mulliganStatus[self.ID]) if status]
		btn_Mulligan.destroy()
		for btn in mulliganBtns:
			self.removeBtn(btn)
		game = self.Game
		game.Hand_Deck.mulligan1Side(self.ID, indices)
		handsAndDecks = [[type(card) for card in game.Hand_Deck.hands[self.ID]], [type(card) for card in game.Hand_Deck.decks[self.ID]]]
		print("Finished mulligan", handsAndDecks)
		s = b"Exchange Deck&Hand||%d||%s" % (self.ID, pickleObj2Bytes(handsAndDecks))
		self.sock.sendall(s)
		data = self.sock.recv(1024)
		if data:
			print("data from server", data)
			if data.startswith(b"P1 Initiates Game"):
				head, handsAndDecks = data.split(b"||")
				hands, decks = unpickleBytes2Obj(handsAndDecks)
				game.Hand_Deck.decks[2] = [card(game, 2) for card in decks]
				game.Hand_Deck.hands[2] = [card(game, 2) for card in hands]
				self.UI = 0
				self.executeGamePlay(lambda: game.Hand_Deck.startGame())
				guides = game.fixedGuides
				game.guides, game.fixedGuides = [], []
				self.sock.sendall(b"P1 Sends Start of Game RNG||" + pickleObj2Bytes(guides))
			elif data.startswith(b"P2 Starts Game After P1"):  #会携带对方完成的游戏定义
				head, handsAndDecks, guides = data.split(b"||")
				hands, decks = unpickleBytes2Obj(handsAndDecks)
				game.Hand_Deck.decks[1] = [card(game, 1) for card in decks]
				game.Hand_Deck.hands[1] = [card(game, 1) for card in hands]
				self.UI = 0
				game.guides = unpickleBytes2Obj(guides)
				self.executeGamePlay(lambda: game.Hand_Deck.startGame())
				print("Start waiting for enemy moves from the server")
				self.wait4EnemyMovefromServer()
			elif data.startswith(b"Opponent Disconnected"):
				OnscreenText(text="Opponent disconnected. Closing", pos=())
				Sequence(Wait(2)).start()
				self.exitFunc()
	
	def wait4Enemy2Reconnect(self):
		self.timer, self.UI = 60, -2
		timerText = OnscreenText(text="Wait for Opponent to Reconnect: "+"60s",
					pos=(0, 0), scale = 0.1, fg = (1, 0, 0, 1), bg = (1, 1, 1, 1),
					align = TextNode.ACenter, mayChange = 1, font = self.sansBold
					)
		thread_data = threading.Thread(target=self.wait4Reconn, daemon=True)
		thread_timer = threading.Thread(target=self.timerCountdown, args=(timerText, ), daemon=True)
		thread_data.start()
		thread_timer.start()
	
	def timerCountdown(self, timerText):
		print("Start countdown")
		while self.timer > 0 and self.UI < -1:
			time.sleep(1)
			timerText["text"] = txt("Wait for Opponent to Reconnect: ", CHN) + "%ds" % self.timer
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
	
	def wait4EnemyMovefromServer(self):
		thread = threading.Thread(target=self.wait4EnemyMoveFunc, daemon=True)
		thread.start()
	
	def wait4EnemyMoveFunc(self):
		self.waiting4Server = True
		while self.waiting4Server:
			data = self.sock.recv(1024)
			print("While waiting, received some thing from server", data)
			if data:
				if data.startswith(b"Game Move"):
					print("Received moves during opponent's turn", data)
					self.decodePlayfromServer(data)  #会自行处理waiting4Server的重置
				elif data.startswith(b"Opponent Disconnected"):
					self.wait4Enemy2Reconnect()  #在这等待对方的重连，重连之后self.UI会被设回0，从而我方可以继续操作
	
	def decodePlayfromServer(self, data):
		print("Decoding move", data)
		header, moves, gameGuides = data.split(b"||")
		moves, gameGuides = unpickleBytes2Obj(moves), unpickleBytes2Obj(gameGuides)
		if isinstance(moves, list):
			print("Read in move", moves)
			self.Game.evolvewithGuide(moves, gameGuides)
			self.drawZones(all=False, board=True, hand=True, hero=True, deck=True, secret=True, nextAnimWaits=False)		#如果结束之后进入了玩家的回合，则不再等待对方的操作
		self.waiting4Server = self.ID != self.Game.turn
		
	def receivePiecesofGameCopy(self, tableID):
		self.UI = -1
		pcsText = OnscreenText(text="Receiving Game Copies from Opponent: " + "0%",
							   	pos=(0, 0), scale = 0.1, fg = (1, 0, 0, 1), bg = (1, 1, 1, 1),
								align = TextNode.ACenter, mayChange = 1, font = self.sansBold
								)
		thread = threading.Thread(target=self.receiveandUpdateCount, args=(tableID, pcsText), daemon=True)
		thread.start()
	
	def receiveandUpdateCount(self, tableID, pcsText):
		self.UI = -1
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
		self.update()
		self.UI = 0
		if self.ID != self.Game.turn:
			self.wait4EnemyMovefromServer()
	
	def sendOwnMovethruServer(self):
		print("Sending the move from player to %d server"%self.ID)
		game = self.Game
		moves, gameGuides = game.moves, game.fixedGuides
		print("In Turn Moves:", moves)
		game.moves, game.fixedGuides = [], []
		if moves:
			s = b"Game Move||" + pickleObj2Bytes(moves) + b"||" + pickleObj2Bytes(gameGuides)
			print("Sending your moves made to the opponent thru server", s)
			self.sock.sendall(s)
			self.UI = -1  #需要把这个调成-1，然后等等server回传move送达到另一方的消息
			data = self.sock.recv(1024)
			#目前是我们的回合，所以对方断线重连了之后可以继续出牌
			if data:
				print("Response of sending our move", data)
				if data == b"Move Received":
					self.UI = 0
				elif data == b"Opponent Disconnected":
					self.wait4Enemy2Reconnect()  #在这等待对方的重连，重连之后self.UI会被设回0，从而我方可以继续操作
	
	def sendEndTurnthruServer(self):
		game = self.Game
		moves, gameGuides = game.moves, game.fixedGuides
		print("End Turn moves:", moves)
		game.moves, game.fixedGuides = [], []
		if moves:
			s = b"Game Move||" + pickleObj2Bytes(moves) + b"||" + pickleObj2Bytes(gameGuides)
			print("Sending TURN END to the opponent thru server", s)
			self.sock.sendall(s)
			self.UI = -1  #需要把这个调成-1，然后等等server回传move送达到另一方的消息
			data = self.sock.recv(1024)
			#我方回合结束，发送之后准备进入等待对方出牌的状态
			if data:
				print("Response of sending our move", data)
				if data == b"Move Received":
					self.UI = 0
				elif data == b"Opponent Disconnected":
					self.wait4Enemy2Reconnect()  #在这等待对方的重连，重连之后self.UI会被设回0，从而我方可以继续操作
			#开始等待对方的出牌
			self.wait4EnemyMovefromServer()



Layer1Window()