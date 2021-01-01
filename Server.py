import socket
from datetime import datetime
import time
import selectors
import types
from numpy.random import choice as npchoice
from CustomWidgets import BoardIndex
import sys
import tkinter as tkinter

"""
selectors.EVENT_READ = 1; selectors.EVENT_WRITE = 2
So the bitwise or operation '|' and bitwise operation '&'
	can check if it's ready to read or write
"""
	
BoardIndex = ["1 Classic Ogrimmar", "2 Classic Stormwind", "3 Classic Stranglethorn", "4 Classic Four Wind Valley",
				#"5 Naxxramas", "6 Goblins vs Gnomes", "7 Black Rock Mountain", "8 The Grand Tournament", "9 League of Explorers Museum", "10 League of Explorers Ruins",
				#"11 Corrupted Stormwind", "12 Karazhan", "13 Gadgetzan",
				#"14 Un'Goro", "15 Frozen Throne", "16 Kobolds",
				#"17 Witchwood", "18 Boomsday Lab", "19 Rumble",
				"20 Dalaran", "21 Uldum Desert", "22 Uldum Oasis", "23 Dragons",
				"24 Outlands", "25 Scholomance Academy", "26 Darkmoon Faire",
				]
				
class Table:
	def __init__(self):
		#self.playerIDs = {1:0, 2:0}
		self.socks2Players = {1: None, 2: None}
		self.conns2Players = {1: None, 2: None}
		self.infos4Players = {1: b'', 2: b''}
		self.boardID = npchoice(BoardIndex)
		self.decksHandsHeroes  = {1: b'', 2: b''}
		self.mainPlayerID = npchoice([1, 2])
		self.noResponseTime = 0 #如果超过2分钟则尝试断开连接，并保存当前进度
		self.heroes = {1: None, 2: None}
		self.hands_decks = {1: b'', 2: b''}
		self.curTurn = 1
		
class Server:
	def __init__(self, address="127.0.0.1", numTables=1):
		self.address = address
		self.selector = selectors.DefaultSelector()
		self.socketsAvailable = []
		self.socketsOccupied = [] #(sock, conn)
		self.socket4PortQuery = None #Need to a special socket to respond to queries about what port can be connected for playing
		self.conn4PortQuery = None
		self.openSocket4PortQuery()
		self.openSocketsforPlayers(numTables)
		self.tables = {}
		
	def openSocket4PortQuery(self):
		self.socket4PortQuery = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.socket4PortQuery.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.socket4PortQuery.bind((self.address, 65432))
		self.socket4PortQuery.setblocking(False)
		self.socket4PortQuery.listen()
		self.selector.register(self.socket4PortQuery, selectors.EVENT_READ, data=None)
		
	def openSocketsforPlayers(self, numTables):
		port = [65433 + i for i in range(2 * numTables)]
		socks = [socket.socket(socket.AF_INET, socket.SOCK_STREAM) for i in range(2 * numTables)]
		for port, sock in zip(port, socks):
			print("Try bind", self.address, port)
			sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
			sock.bind((self.address, port))
			sock.listen()
			self.socketsAvailable.append((port, sock))
			self.selector.register(sock, selectors.EVENT_READ, data=None)
			
		print("Available ports:", self.socketsAvailable)
		
	def occupyAnAvailableSocket(self, sock, conn, addr):
		conn.setblocking(False)
		data = types.SimpleNamespace(addr=addr, outBytes=b'')
		events = selectors.EVENT_READ | selectors.EVENT_WRITE
		#print("Try to allocate socket to occupied", sock)
		#print("Available ports:", self.socketsAvailable)
		for i in range(len(self.socketsAvailable)):
			if self.socketsAvailable[i][1] == sock:
				port, sock = self.socketsAvailable.pop(i)
				self.socketsOccupied.append((sock, conn, port))
				break
		self.selector.register(conn, events, data=data)
		
	def freeAnOccupiedConn(self, conn):
		table, ID = self.findTableandIDwithConn(conn)
		table.infos4Players[ID] = b''
		table.conns2Players[ID] = None
		table.socks2Players[ID] = None
		for i in range(len(self.socketsOccupied)): #[(sock, connection, port)]
			if conn == self.socketsOccupied[i][1]: #socketsAvailable: [(port, sock)]
				self.socketsAvailable.append((self.socketsOccupied[i][2], self.socketsOccupied[i][0]))
				self.socketsOccupied.pop(i)
				break
		self.selector.unregister(conn)
		conn.close()
		
	def findSocketfromConn(self, conn):
		for s, connection, port in self.socketsOccupied:
			if connection == conn:
				return s
				
	def findTableandIDwithConn(self, conn):
		for table in self.tables.values():
			for ID in range(1, 3):
				if table.conns2Players[ID] == conn:
					return table, ID
					
	def handleConnectionRequest(self, sock):
		conn, addr = sock.accept()
		print("Connection request from ", addr)
		if sock == self.socket4PortQuery: #如果是询问还有什么port可以用,无论如何最后都要关闭这个conn
			if self.socketsAvailable:
				response = b"Ports"
				for port, sock in self.socketsAvailable:
					response += b",%d"%port
				print("Returns available ports to client", response)
				conn.sendall(response)
			else:
				print("Has no available sockets left")
				conn.sendall(b"No Ports Left")
			conn.close()
		else:
			print("Got request to join a table. Establish conn")
			self.occupyAnAvailableSocket(sock, conn, addr) #请求连接到一个port for player
			
	def handleStartorJoinTable(self, conn, data): #data:"Start/Join a Table||gwoiegwog" #Table ID是一个随机字符串
		action, tableID, hero = data.split(b'||')
		if tableID in self.tables: #Join a table, after checking if the table already has two players
			table = self.tables[tableID]
			#If the table found already has both connections established. Then tell the player to find a another table
			if table.conns2Players[1] and table.conns2Players[2]: #玩家输入了正确的playerID但是这个桌子已经建立了两个connection，说明已经有人占用
				conn.sendall(b"Use another Table ID")
			else:  #这个桌子还有空的连接，现在可以凑成一对玩家
				table.socks2Players[2] = self.findSocketfromConn(conn)
				table.conns2Players[2] = conn
				table.heroes[2] = hero
				#随机决定交换双方的出牌顺序与相应的各种信息，然后通知每个玩家
				if npchoice([0, 1]):
					temp = table.socks2Players[1]
					table.socks2Players[1] = table.socks2Players[2]
					table.socks2Players[2] = temp
					temp = table.conns2Players[1]
					table.conns2Players[1] = table.conns2Players[2]
					table.conns2Players[2] = temp
					temp = table.heroes[1]
					table.heroes[1] = table.heroes[2]
					table.heroes[2] = temp
				#保存这个信息，在后面的iteration中分发给各玩家
				table.infos4Players[1] = b"Start Mulligan||1||%s||%s"%(bytes(table.boardID.encode()), table.heroes[2])
				table.infos4Players[2] = b"Start Mulligan||2||%s||%s"%(bytes(table.boardID.encode()), table.heroes[1])
		else: #Start a new table of game.
			table = Table()
			self.tables[tableID] = table
			table.conns2Players[1] = conn
			table.socks2Players[1] = self.findSocketfromConn(conn)
			table.heroes[1] = hero
			table.infos4Players[1] = b"Table reserved. Wait"
			
	def run(self):
		print("Start running the server")
		running = True
		while running:
			try:
				events = self.selector.select(timeout=None)
				for key, mask in events:
					if key.data is None: #客户端尝试连接。如果是询问queryPort,则如果有空余位置时当场返回可用port列表，然后断开； 否则直接断开。
													#如果是询问可用port，则把这个可用port划归那个客户端并且建立连接
						self.handleConnectionRequest(key.fileobj)
					else: #A conn to the client is available for actions.
						conn, data = key.fileobj, key.data
						if mask & selectors.EVENT_READ:
							data = conn.recv(1024)
							if data: #可能是申请预订或者加入一张桌子，或者是起始阶段双方交换手牌牌库和英雄信息，或者是正常的游戏操作
								if data.startswith(b"Start/Join a Table"):
									self.handleStartorJoinTable(conn, data)
								elif data.startswith(b"Exchange Deck&Hand"):
									header, ID, handsAndDecks = data.split(b"||")
									table, ID = self.findTableandIDwithConn(conn)
									table.hands_decks[ID] = handsAndDecks
									if table.hands_decks[3-ID]: #如果双方的牌库手牌信息等都全了
										if table.conns2Players[1] and table.conns2Players[2]:
											table.infos4Players[1] = b"P1 Initiates Game||" + table.hands_decks[2]
											table.infos4Players[2] = b''
										else:
											table.infos4Players[1] = b"Opponent Disconnected"
											table.infos4Players[2] = b"Opponent Disconnected"
								elif data.startswith(b"P1 Sends Start of Game RNG"):
									header, guides = data.split(b'||')
									table, ID = self.findTableandIDwithConn(conn)
									if table.conns2Players[1] and table.conns2Players[2]:
										table.infos4Players[2] = b"P2 Starts Game After P1||%s||%s"%(table.hands_decks[1], guides)
										table.infos4Players[1] = b''
									else:
										table.infos4Players[1] = b"Opponent Disconnected"
										table.infos4Players[2] = b"Opponent Disconnected"
								elif data.startswith(b"Game Move"): #游戏正常进行过程中每个玩家进行了操作之后可以把信息给对面
									table, ID = self.findTableandIDwithConn(conn)
									table.infos4Players[3-ID] = data
									if table.conns2Players[3-ID]:
										table.infos4Players[ID] = b"Move Received"
									else:
										table.infos4Players[ID] = b"Opponent Disconnected"
								elif data.startswith(b"Request to Rejoin Table"): #有一方玩家掉线，请求重新加入牌局
									header, tableID = data.split(b"||")
									#只有table存在，且只有一方还保持连接的状态下可以让一个人回归这个游戏
									if tableID in self.tables and ((self.tables[tableID].conns2Players[1] and not self.tables[tableID].conns2Players[2]) \
																	or (self.tables[tableID].conns2Players[2] and not self.tables[tableID].conns2Players[1])):
										table = self.tables[tableID]
										CopyProviderID = 1 if table.conns2Players[1] else 2 #保持连接的一方会被要求复制
										table.infos4Players[CopyProviderID] = b"Copy Your Game"
										table.infos4Players[3-CopyProviderID] = b''
										table.conns2Players[3-CopyProviderID] = conn
										table.socks2Players[3-CopyProviderID] = self.findSocketfromConn(conn)
									else:
										print("Table ID correct: ", tableID in self.tables)
										conn.sendall(b"Table ID wrong/occupied. Cannot resume")
										conn.close()
								#因为游戏的复制很大，所以需要连续发送许多次。最后一条会有不同的前缀
								elif data.startswith(b"1st Copy Piece"):
									print("Received the first piece of game copy")
									header, curTurn, numPieces, gameCopyInfo = data.split(b"||")
									table, ID = self.findTableandIDwithConn(conn)
									table.curTurn = int(curTurn)
									print("Table connection:", table.conns2Players)
									table.infos4Players[ID] = b''
									table.infos4Players[3-ID] = b"Resume with Copy||%d||%s||%s||%s"%(3-ID, bytes(table.boardID.encode()), numPieces, gameCopyInfo)
								elif data.startswith(b"Copy Piece"):
									#print("Received game copy pc %s"%str(data.split(b"||")[0].split(b'_')[1].decode()))
									table, ID = self.findTableandIDwithConn(conn)
									table.infos4Players[ID] = b''
									table.infos4Players[3-ID] = data
								elif data.startswith(b"Last Copy Piece"):
									#print("Received the last piece of game copy")
									table, ID = self.findTableandIDwithConn(conn)
									table.infos4Players[ID] = b''
									table.infos4Players[3-ID] = data
								elif data.startswith(b"Received. Keep Sending"):
									table, ID = self.findTableandIDwithConn(conn)
									#print("player %d received game copy pc."%ID, data)
									table.infos4Players[ID] = b''
									table.infos4Players[3-ID] = data
								elif data.startswith(b"All Pieces Received"):
									table, ID = self.findTableandIDwithConn(conn)
									#print("player %d received game copy pc."%ID, data)
									table.infos4Players[ID] = b''
									table.infos4Players[3-ID] = data
							else: #如果conn收不到数据说明client与server的连接出了问题
								print("The connection to a player is lost")
								table, ID = self.findTableandIDwithConn(conn)
								table.infos4Players[3-ID] = b"Opponent Disconnected"
								table.infos4Players[ID] = b""
								self.freeAnOccupiedConn(conn)
								
				#应该在上一轮的处理中得到应该向各个桌子 上的玩家发送的内容，然后每个桌子进行遍历，分别根据存好的消息进行分发
				for table in self.tables.values():
					for ID, info in table.infos4Players.items(): #可能是conns2Players没有注册吧
						if info and table.conns2Players[ID]:
							table.infos4Players[ID] = []
							if ID != table.curTurn and (info.startswith(b"Received") or info.startswith(b"All Pieces")):
								#不知道为什么需要重复发送两次可能是出现了send和recv的不同步
								table.conns2Players[ID].sendall(info)
							table.conns2Players[ID].sendall(info)
							
			except ConnectionResetError:
				for tableID, table in zip(list(self.tables.keys()), list(self.tables.values())):
					#Check if a conn is still open.
					for ID in [1, 2]:
						if table.conns2Players[ID]:
							try:
								table.conns2Players[ID].setblocking(True)
								data = table.conns2Players[ID].recv(16, socket.MSG_PEEK)
								table.conns2Players[ID].setblocking(False)
							except Exception as e:
								print("checking connection failed", e)
								print("Trying to free a lost connection")
								self.freeAnOccupiedConn(table.conns2Players[ID])
					if not (table.conns2Players[1] or table.conns2Players[2]):
						print("Both players left the table. Deleting it.")
						del self.tables[tableID]
				print("AFter freeing conns and sockets\nTables are", self.tables,)
				print("Sockets are", self.socketsAvailable)
				#print("An existing connection was forcibly closed by the remote host")
				#for table.ID, table in self.tables.items():
				#	if table.conns2Players[1]:
			except KeyboardInterrupt:
				running = False
				print(datetime.now().strftime("%Y-%m-%d  %H:%M:%S"), "The server is stopped by keyboard interruption")
				
			
				
class Server_GUI:
	def __init__(self):
		self.window = tk.Tk()
		self.window.mainloop()
		
		
class ServerSimp:
	def __init__(self, address="127.0.0.1", numTables=1):
		self.address = address
		self.socket4PortQuery = None #Need to a special socket to respond to queries about what port can be connected for playing
		self.conn4PortQuery = None
		self.openSocket4PortQuery()
		self.openSocketsforPlayers(numTables)
		self.tables = {}
		
if __name__ == "__main__":
	address = sys.argv[1]
	print(address)
	Server(address).run()