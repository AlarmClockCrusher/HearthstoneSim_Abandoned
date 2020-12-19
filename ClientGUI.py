import tkinter as tk
from tkinter import messagebox

from CustomWidgets import *
from UICommonPart import *
from Game import *
from Code2CardList import *
from GenerateRNGPools import *

import socket
import select
import time
import numpy
import threading, subprocess
import pickle
import types
import platform
			
CHN = True

class MulliganFinishButton_3(tk.Button):
	def __init__(self, GUI):
		tk.Button.__init__(self, master=GUI.GamePanel, text=txt("Replace Card", CHN), bg="green3", width=13, height=3, font=("Yahei", 12, "bold"))
		self.GUI = GUI
		self.configure(command=self.respond)
		
	def respond(self):
		GUI = self.GUI
		ID, game = GUI.ID, GUI.Game
		indices = [i for i, status in enumerate(GUI.mulliganStatus) if status]
		game.Hand_Deck.mulligan1Side(ID, indices) #之后生成一个起手调度信息
		#牌库和起始手牌决定
		handsAndDecks = [[type(card) for card in game.Hand_Deck.hands[ID]], [type(card) for card in game.Hand_Deck.decks[ID]]]
		s = b"Exchange Deck&Hand||%d||%s"%(ID, pickleObj2Bytes(handsAndDecks))
		GUI.sock.sendall(s)
		while True: #得到的回复可能是b"Wait for Opponent's Mulligan", b"Decks and Hands decided"
			data = GUI.sock.recv(1024)
			if data:
				if data.startswith(b"Wait for Opponent's Mulligan"): #把自己完成的手牌和牌库会给对方
					messagebox.showinfo(message=txt("Wait for opponent to finish mulligan", CHN))
				elif data.startswith(b"P1 Initiates Game"):
					action, handsAndDecks = data.split(b"||")
					game = GUI.Game
					hands, decks = unpickleBytes2Obj(handsAndDecks)
					game.Hand_Deck.decks[2] = [card(game, 2) for card in decks]
					game.Hand_Deck.hands[2] = [card(game, 2) for card in hands]
					GUI.UI = 0
					GUI.update()
					game.Hand_Deck.startGame()
					guides = game.fixedGuides
					game.guides, game.fixedGuides = [], []
					GUI.sock.sendall(b"P1 Sends Start of Game RNG||"+pickleObj2Bytes(guides))
					#游戏开始时的那些随机过程会被发送给对方，而自己可以开始自己的游戏
					break
				elif data.startswith(b"P2 Starts Game After P1"): #会携带对方完成的游戏定义
					action, handsAndDecks, guides = data.split(b"||")
					game = GUI.Game
					hands, decks = unpickleBytes2Obj(handsAndDecks)
					game.Hand_Deck.decks[1] = [card(game, 1) for card in decks]
					game.Hand_Deck.hands[1] = [card(game, 1) for card in hands]
					GUI.UI = 0
					game.guides = unpickleBytes2Obj(guides)
					GUI.update()
					game.Hand_Deck.startGame()
					break
				elif data.startswith(b"Opponent Disconnected"):
					messagebox.showinfo(message=txt("Opponent disconnected. Closing", CHN))
					self.GUI.window.destroy()
		if GUI.ID == 2:
			print("Start waiting for the opponent to make moves")
			GUI.wait4EnemyMovefromServer()
		else:
			print("Start making your moves")
			
	def plot(self, x, y):
		self.place(x=x, y=y, anchor='c')
		self.GUI.btnsDrawn.append(self)
		
		
class Button_Connect2Server(tk.Button):
	def __init__(self, GUI):
		tk.Button.__init__(self, master=GUI.initConnPanel, bg="green3", text=txt("Connect", CHN), font=("Yahei", 15), width=20)
		self.GUI = GUI
		self.bind("<Button-1>", self.leftClick)
		
	def leftClick(self, event): #在这时检测所带的卡组是不正确
		deck, deckCorrect, hero = parseDeckCode(self.GUI.ownDeck.get(), ClassDict[self.GUI.hero.get()], ClassDict)
		if deckCorrect:
			#thread = threading.Thread(target=self.GUI.initConntoServer, args=(hero, deck), daemon=True)
			#thread.start()
			messagebox.showinfo(message=txt("Connecting to server. Please wait", CHN))
			self.GUI.initConntoServer(hero, deck)
		else: messagebox.showinfo(message=txt("Deck code is wrong. Check before retry", CHN))
			
class Button_ConnectandResume(tk.Button):
	def __init__(self, GUI):
		tk.Button.__init__(self, master=GUI.initConnPanel, bg="green3", text=txt("Resume", CHN), font=("Yahei", 12), width=7)
		self.GUI = GUI
		self.bind("<Button-1>", self.leftClick)
		
	def leftClick(self, event): #在这时检测所带的卡组是不正确
		self.GUI.reconnandResume()
		
#import tkinter.font as tkFont
#fontStyle = tkFont.Font(family="Lucida Grande", size=3)
class GUI_Client(GUI_Common):
	def __init__(self):
		self.mulliganStatus, self.btnsDrawn = [], []
		self.selectedSubject = ""
		self.subject, self.target, self.discover = None, None, None
		self.position, self.choice, self.UI = -1, 0, -2 #起手调换的UI为-2
		self.boardID, self.ID = '', 1
		self.CHN = CHN
		self.window = tk.Tk()
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.waiting4Server, self.timer = False, 60
		
		self.initConnPanel = tk.Frame(master=self.window, width=0.005*X, height=int(0.6*Y))
		self.initConnPanel.pack(side=tk.TOP)
		
		tk.Label(self.initConnPanel, text=txt("Enter deck code below", CHN), 
				font=("Yahei", 15)).grid(row=0, column=0)
		self.ownDeck = tk.Entry(self.initConnPanel, text="", font=("Yahei", 15, "bold"), width=20)
		self.ownDeck.grid(row=1, column=0)
		
		self.hero = tk.StringVar(self.initConnPanel)
		self.hero.set(list(ClassDict.keys())[0])
		heroOpt = tk.OptionMenu(self.initConnPanel, self.hero, *list(ClassDict.keys()))
		heroOpt.config(width=15, font=("Yahei", 15))
		heroOpt["menu"].config(font=("Yahei", 15))
		heroOpt.grid(row=2, column=0)
		#连接所需的数据，服务器IP address, port以及申请预订或者加入的桌子ID
		self.serverIP = tk.Entry(self.initConnPanel, font=("Yahei", 15), width=10)
		self.queryPort = tk.Entry(self.initConnPanel, font=("Yahei", 15), width=10)
		self.tableID = tk.Entry(self.initConnPanel, font=("Yahei", 15), width=10)
		self.serverIP.insert(0, "127.0.0.1")
		self.queryPort.insert(0, "65432")
		self.tableID.insert(0, "200") #"%d"%numpy.random.randint(6000)
		
		self.serverIP.grid(row=0, column=1)
		self.queryPort.grid(row=1, column=1)
		self.tableID.grid(row=2, column=1)
		tk.Label(self.initConnPanel, text=txt("Server IP", CHN), 
				font=("Yahei", 15)).grid(row=0, column=2, sticky=tk.W)
		tk.Label(self.initConnPanel, text=txt("Query Port", CHN), 
				font=("Yahei", 15)).grid(row=1, column=2, sticky=tk.W)
		tk.Label(self.initConnPanel, text=txt("Start/Join Table", CHN), 
				font=("Yahei", 15)).grid(row=2, column=2, sticky=tk.W)
		Button_Connect2Server(self).grid(row=3, column=1, columnspan=2)
		Button_ConnectandResume(self).grid(row=4, column=2, columnspan=1)
		self.window.mainloop()
		
	def reconnandResume(self):
		serverIP = self.serverIP.get()
		try: self.sock.connect((serverIP, int(self.queryPort.get()))) #Blocks. If the server port turns this attempt down, it raises error
		except ConnectionRefusedError:
			messagebox.showinfo(message=txt("Can't connect to the server's query port", CHN))
			return
		data = self.sock.recv(1024)
		if data.startswith(b"Ports"): #b"Ports,65433,65434"
			print("Received available ports", data)
			ports = data.decode().split(',')[1:]
			print("Now trying to connect to an available port", ports[0])
			self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			self.sock.connect((serverIP, int(ports[0]))) #Take the first available port returned from the server
			#与initConn2Server不同之处在于这里发送的信号不同
			tableID = self.tableID.get()
			self.initConnPanel.destroy()
			self.initSidePartofUI()
			self.receivePiecesofGameCopy(tableID)
			
		elif data == b"No Ports Left":
			messagebox.showinfo(message=txt("No tables left. Please wait", CHN))
		else:
			print("Received smth else", data)
			
	def initConntoServer(self, hero, deck):
		serverIP = self.serverIP.get()
		param = '-n' if platform.system().lower() == 'windows' else '-c'
		command = ["ping", param, '1', serverIP]
		if subprocess.call(command) != 0:
			messagebox.showinfo(message="Can't ping the address %s"%serverIP)
		try: self.sock.connect((serverIP, int(self.queryPort.get()))) #Blocks. If the server port turns this attempt down, it raises error
		except ConnectionRefusedError:
			messagebox.showinfo(message=txt("Can't connect to the server's query port", CHN))
			return
		data = self.sock.recv(1024)
		if data.startswith(b"Ports"): #b"Ports,65433,65434"
			print("Received available ports", data)
			ports = data.decode().split(',')[1:]
			print("Now trying to connect to an available port", ports[0])
			self.sock.close()
			self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			self.sock.connect((serverIP, int(ports[0]))) #Take the first available port returned from the server
			#Send the server the hero info and deck info, and tableID to request
			tableID = self.tableID.get()
			print("Attemp to start/join a table with ID", tableID, type(tableID.encode()), type(bytes(tableID.encode())))
			self.sock.sendall(b"Start/Join a Table||%s||%s"%(bytes(tableID.encode()), pickleObj2Bytes(hero)) )
			print("Waiting for response from server about START/JOIN TABLE request")
			data = self.sock.recv(1024) #socket之间的连接中断时，socket本身不会立即报错，而是会在尝试发送信息的时候才会发现错误 
			print("Received response to START/JOIN TABLE request:", data)
			if data:
				#预订到桌子的玩家会收到这个信息，而加入到桌子的玩家会直接收到b"Start Mulligan||x||xxx||xxx"
				if data == b"Table reserved. Wait": #向服务发送预订/加入桌子的申请后，服务器会返回ID对已经被占用 / 或者预订成功
					print("Your table has been reserved. Start waiting for an opponent to join the table")
					data = self.sock.recv(1024) #期待收到b"Start Mulligan|1|26 Darkmoon Faire|Uther",从而开始起手调度过程
					if data: #开始起手调度,需要初始化游戏
						print("Opponent Joined. Start your mulligan")
						self.mulliganPrep(hero, deck, data)
				elif data.startswith(b"Start Mulligan"):
					print("You have joined a table. Start your mulligan")
					self.mulliganPrep(hero, deck, data)
				elif data == b"Use another table ID":
					messagebox.showinfo(message=txt("This table ID is already taken.", CHN))
		elif data == b"No Ports Left":
			messagebox.showinfo(message=txt("No tables left. Please wait", CHN))
		else:
			print("Received smth else", data)
			
	def mulliganPrep(self, hero, deck, data):
		action, self.ID, self.boardID, enemyHero = data.split(b'||')
		self.ID, self.boardID = int(self.ID), str(self.boardID.decode())
		enemyHero = unpickleBytes2Obj(enemyHero)
		game = Game(self)
		#需要生成一下cardPool
		board, self.transferStudentType = makeCardPool(monk=0, board=self.boardID)
		from CardPools import Classes, ClassesandNeutral, ClassDict, cardPool, MinionsofCost, RNGPools
		if self.ID == 1: #起手要换的牌会在游戏的初始过程中直接决定
			game.initialize(cardPool, ClassCards, NeutralCards, MinionsofCost, RNGPools, hero, enemyHero, deck, deck)
		else:
			game.initialize(cardPool, ClassCards, NeutralCards, MinionsofCost, RNGPools, enemyHero, hero, deck, deck)
		game.mode = 0
		self.UI, self.Game = -2, game
		game.Classes, game.ClassesandNeutral = Classes, ClassesandNeutral
		self.initConnPanel.destroy()
		self.initMuliganUI()
		
	def initSidePartofUI(self):
		self.GamePanel = tk.Frame(self.window, width=X, height=Y, bg="black")
		self.GamePanel.pack(fill=tk.Y, side=tk.LEFT if LeftorRight else tk.RIGHT)
		self.sidePanel = tk.Frame(self.window, width=int(0.005*X), height=int(0.3*Y), bg="cyan")
		self.sidePanel.pack(side=tk.TOP)
		
		self.lbl_Card = tk.Label(self.sidePanel, text=txt("Resolving Card Effect", CHN))
		self.lbl_wish = tk.Label(master=self.sidePanel, text=txt("Card Wished", CHN), font=("Yahei", 15))
		self.lbl_Card.pack(fill=tk.X)
		
	def initMuliganUI(self):
		self.initSidePartofUI()
		self.initGameDisplay()
		self.UI = -2
		self.heroZones[1].draw()
		self.heroZones[2].draw()
		self.canvas.draw()
		self.mulliganStatus = [0] * len(self.Game.mulligans[self.ID])
		#其他的两个GUI里面都是直接用update(),这里专门写一下
		for i, card in enumerate(self.Game.mulligans[self.ID]):
			pos = (shift+100+i*2*111, 0.5*Y)
			MulliganButton(self, card).plot(x=pos[0], y=pos[1])
		MulliganFinishButton_3(self).plot(x=X/2, y=0.9*Y)
		
	def wait4Enemy2Reconnect(self):
		self.timer, self.UI = 60, -2
		btn_WaitforReconn = tk.Button(self.GamePanel, text=txt("Wait for Opponent to Reconnect: ", CHN) + "60s", bg="red", height=2, font=("Yahei", 12, "bold"))
		btn_WaitforReconn.place(x=X/2, y=Y/2)
		thread_data = threading.Thread(target=self.wait4Reconn, daemon=True)
		thread_timer = threading.Thread(target=self.timerCountdown, args=(self.timer, btn_WaitforReconn), daemon=True)
		thread_data.start()
		thread_timer.start()
		
	def timerCountdown(self, timer, btn_WaitforReconn):
		print("Start countdown")
		while self.timer > 0 and self.UI < -1:
			time.sleep(1)
			btn_WaitforReconn.config(text=txt("Wait for Opponent to Reconnect: ", CHN) + "%ds"%self.timer)
			self.timer -= 1
		print("Finished sending game copy to server")
		if self.timer < 1:
			btn_WaitforReconn.config(text=txt("Opponent failed to reconnect.\nClosing in 2 seconds", CHN))
			self.window.after(2000, self.window.destroy())
		else:
			btn_WaitforReconn.destroy()
			
	def wait4Reconn(self):
		data = self.sock.recv(1024)
		if data.startswith(b"Copy Your Game"):
			self.timer, self.UI = 60, -1 #当收到开始复制的要求时就可以停止倒计时
			gameCopy = self.Game.copyGame()[0]
			gameCopy.GUI = None
			gameCopyInfo = pickleObj2Bytes(gameCopy)
			#因为gameCopy会比较大，所以需要分段进行传输
			numPieces = 1 + round(len(gameCopyInfo) / 950)
			print("%d pieces to send"%numPieces)
			pieces = []
			for i in range(numPieces-1):
				pieces.append(gameCopyInfo[i*950:i*950+950])
			numPiecesReceived = 0
			pieces.append(gameCopyInfo[numPieces*950-950:])
			self.sock.sendall(b"1st Copy Piece||%d||%d||%s"%(self.Game.turn, numPieces, pieces[0]))
			data = self.sock.recv(1024)
			print(data)
			if data.startswith(b"Received"):
				print("First pc of copy received. Send the rest")
				numPiecesReceived += 1
				for i, piece in enumerate(pieces[1:-1]):
					self.sock.sendall(b"Copy Piece_%d||%s"%(i+1, piece))
					data = self.sock.recv(1024)
					if data.startswith(b"Received."):
						print("Copy pc %d delivered. Will keep sending copies"%(i+1))
						numPiecesReceived += 1
				self.sock.sendall(b"Last Copy Piece||%s"%pieces[-1])
				data = self.sock.recv(1024)
				print("Data after sending last copy piece", data)
				if data == b"All Pieces Received":
					numPiecesReceived += 1
					print("Finished sending %d pieces. Num Pieces Received %d"%(numPieces, numPiecesReceived))
			else: print("Received smth else")
		else:
			print("Opponent table ID is wrong")
		self.UI = 0
		
	def sendOwnMovethruServer(self):
		game = self.Game
		moves, gameGuides = game.moves, game.fixedGuides
		print("In Turn Moves:", moves)
		game.moves, game.fixedGuides = [], []
		if moves:
			s = b"Game Move||"+ pickleObj2Bytes(moves) + b"||" + pickleObj2Bytes(gameGuides)
			print("Sending your moves made to the opponent thru server", s)
			self.sock.sendall(s)
			self.UI = -1 #需要把这个调成-1，然后等等server回传move送达到另一方的消息
			data = self.sock.recv(1024)
			#目前是我们的回合，所以对方断线重连了之后可以继续出牌
			if data:
				print("Response of sending our move", data)
				if data == b"Move Received":
					self.UI = 0
				elif data == b"Opponent Disconnected":
					self.wait4Enemy2Reconnect() #在这等待对方的重连，重连之后self.UI会被设回0，从而我方可以继续操作
					
	def sendEndTurnthruServer(self):
		game = self.Game
		moves, gameGuides = game.moves, game.fixedGuides
		print("End Turn moves:", moves)
		game.moves, game.fixedGuides = [], []
		if moves:
			s = b"Game Move||"+ pickleObj2Bytes(moves) + b"||" + pickleObj2Bytes(gameGuides)
			print("Sending TURN END to the opponent thru server", s)
			self.sock.sendall(s)
			self.UI = -1 #需要把这个调成-1，然后等等server回传move送达到另一方的消息
			data = self.sock.recv(1024)
			#我方回合结束，发送之后准备进入等待对方出牌的状态
			if data:
				print("Response of sending our move", data)
				if data == b"Move Received":
					self.UI = 0
				elif data == b"Opponent Disconnected":
					self.wait4Enemy2Reconnect() #在这等待对方的重连，重连之后self.UI会被设回0，从而我方可以继续操作
			#开始等待对方的出牌
			self.wait4EnemyMovefromServer()
			
	def wait4EnemyMovefromServer(self):
		thread = threading.Thread(target=self.waitThreadFunc, daemon=True)
		thread.start()
		
	def waitThreadFunc(self):
		self.waiting4Server = True
		while self.waiting4Server:
			data = self.sock.recv(1024)
			if data:
				if data.startswith(b"Game Move"):
					print("Received moves during opponent's turn", data)
					self.decodePlayfromServer(data) #会自行处理waiting4Server的重置
				elif data.startswith(b"Opponent Disconnected"):
					self.wait4Enemy2Reconnect() #在这等待对方的重连，重连之后self.UI会被设回0，从而我方可以继续操作
					
	def decodePlayfromServer(self, data):
		print("Decoding move", data)
		header, moves, gameGuides = data.split(b"||")
		moves, gameGuides = unpickleBytes2Obj(moves), unpickleBytes2Obj(gameGuides)
		if isinstance(moves, list):
			print("Read in move", moves)
			self.Game.evolvewithGuide(moves, gameGuides)
			self.update()
		#如果结束之后进入了玩家的回合，则不再等待对方的操作
		self.waiting4Server = self.ID != self.Game.turn
		
	def receivePiecesofGameCopy(self, tableID):
		self.UI = -1
		lbl_CopyReceptionProgress = tk.Label(self.GamePanel, text=txt("Receiving Game Copies from Opponent: ", CHN) + "0%", font=("Yahei", 15))
		lbl_CopyReceptionProgress.place(x=X/2, y=Y/2)
		thread = threading.Thread(target=self.receiveandUpdateCount, args=(tableID, lbl_CopyReceptionProgress), daemon=True)
		thread.start()
		
	def receiveandUpdateCount(self, tableID, lbl_CopyReceptionProgress):
		self.UI = -1
		numPiecesTotal, numPiecesReceived, buffer = 0, 0, b''
		print("Ready for data transfer")
		
		print("Start requesting game copy")
		self.sock.sendall(b"Request to Rejoin Table||%s"%bytes(tableID.encode()) )
		#已经验证过这个sock的connection正常注册进了server的table里面
		while True:
			data = self.sock.recv(1024)
			print(data[:20])
			if data.startswith(b"Resume with Copy"): #Receive the first piece of the game copy
				print("First pc of copy received")
				header, yourID, boardID, num, gameCopyInfo = data.split(b"||")
				boardID, numPiecesTotal = str(boardID.decode()), int(num)
				numPiecesReceived += 1
				buffer += gameCopyInfo
				#time.sleep(0.01)
				self.sock.sendall(b"Received. Keep Sending")
			elif data.startswith(b"Copy Piece"):
				print("Copy pc %s received. Provider should keep sending"%str(data.split(b"||")[0].split(b'_')[1].decode()))
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
				lbl_CopyReceptionProgress.config(text=txt("Receiving Game Copies from Opponent: ", CHN) + "%d/%d"%(numPiecesReceived, numPiecesTotal))
		print("Received %d pieces out of %d in total"%(numPiecesReceived, numPiecesTotal))
		try:
			gameCopy = unpickleBytes2Obj(buffer)
			gameCopy.GUI = self
		except Exception as e:
			print("Failed to parse the game. Exception:", e)
		
		self.Game, self.ID, self.boardID = gameCopy, int(yourID), boardID
		lbl_CopyReceptionProgress.destroy()
		self.initGameDisplay()
		self.update()
		self.UI = 0
		if self.ID != self.Game.turn:
			self.wait4EnemyMovefromServer()
			
GUI_Client()