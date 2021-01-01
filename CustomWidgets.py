X, Y = 1000, 750
card_x, card_y = int(0.00818*X), int(0.00625*Y) #XY为（1100， 800）时对应（9，5）
CARD_X, CARD_Y = int(0.073*X), int(0.15*Y) #XY为（1100，800）时对应80, 120#有Image的按钮的大小由这个来确定
ManaXtlSize = int(0.02*Y)
HeroIconSize = int(0.1*Y) #XY为（1100，800）时对应80，80
Hand_X, Hand_Y = int(0.064*X), int(0.0875*Y) #XY为（1100，800）时对应70，100
Board_X, Board_Y = int(0.94*X), int(0.64*Y)
BoardColor = 'lemon chiffon' #"#%02x%02x%02x"%(219, 156, 29) 

PowerImgSize = int(0.78*HeroIconSize)
PowerIconSize = int(0.83*HeroIconSize)
HandImgSize = int(0.95*Hand_X)
HandIconWidth, HandIconHeight = Hand_X, int(1.2*Hand_Y)
HandIconWidth_noImg, HandIconHeight_noImg = int(0.12*Hand_X), int(0.08*Hand_Y)
MinionImgSize = 78
WeaponImgSize = int(0.78*HeroIconSize)
WeaponIconWidth, WeaponIconHeight =  int(0.83*HeroIconSize), HeroIconSize
SecretIconSize_img, SecretIconSize_noImg = int(0.85*HeroIconSize), int(0.1*HeroIconSize)
SecretImgSize = int(0.95*SecretIconSize_img)

waitTime4Info = 1
infoDispXPos = 0.9
CHN = True
texts = {"Include DIY packs": "包含DIY卡牌",
		"Choose Game Board": "选择棋盘版本",
		"Continue": "继续", "Confirm": "确定",
		"Monk": "武僧",
		"System Resolution": "系统结算",
		"Type Card You Wish": "输入许愿卡牌的英文名称",
		"Resolving Card Effect": "正在结算卡牌",
		"Enter Deck 1 code": "玩家1套牌代码", "Enter Deck 2 code": "玩家2套牌代码",
		"Deck 1 incorrect": "套牌代码1无效", "Deck 2 incorrect": "套牌代码2无效",
		"Enter deck code below": "输入套牌代码",
		"Show Send Info Reminder": "显示向对方发送信息的提示",
		"Plays to update": "向对方发送的信息",
		"L:Generate Update / R:Copy Game": "左键：生成要发送的信息\n右键：复制游戏",
		"Load Update from Opponent": "加载对方的操作信息",
		"To go 1st, use left panel to decide the DIY expansion and game board.\nTo go 2nd/load a saved game, use right panel to enter info from your opponent/select a .p file": \
			"作为先手方：用左侧面板确定要加载的DIY和棋盘\n作为后手方/加载已保存的游戏，使用右侧面板输入先手方发送给你的信息/选择一个.p文件",
		"Load a Game, or\nGo 2nd using Info from Opponent": "加载已保存的游戏，\n或输入对方信息、作为后手开始游戏",
		"Start a new game as Player 1\nDecide DIY Packs and Game Board": "作为先手开始游戏\n并决定使用的DIY卡牌与棋盘",
		"Choose a Game to load": "选择加载已保存的游戏文件",
		"Decide your deck and class, mulligan and send the generated info to your opponent": "确定你的套牌和职业，在起手调度后将生成的信息发送给对方",
		"Saved Game loaded. Will resume after confirmation": "已加载保存的游戏。确定后回到游戏",
		"Player 1 has decided their deck and initial hand.\nDecide yours and send the info back to start the game": "先手方已经确定了其牌库与起始手牌。确定你的牌库和起始手牌后将信息回传给对方",
		"Your deck and hand have been decided. Send the info to the opponent": "你的牌库和手牌已确定。将生成的信息发送给对方",
		"Info not generated yet": "尚无更新信息",
		"Game Copy Generated": "游戏进度已保存为两份.p文件。双方可以各加载一个返回当前游戏进度",
		"Send Info in Clipboard!": "操作信息已经保存至剪贴板，请发送至对方玩家",
		"Update same as last time\nLeftclick: Continue/Rightclick: Cancel": "游戏更新信息与上次相同，\n可能存在重复，确认使用?\n左键：确定\n右键：取消",
		"Connecting to server. Please wait": "正在连接服务器，请等待",
		"Receiving Game Copies from Opponent: ": "正在接收对方发送的游戏复制",
		"Opponent failed to reconnect.\nClosing in 2 seconds": "对方玩家重连失败\n2秒后关闭",
		"Wait for Opponent to Reconnect: ": "等待对方重连中",
		"Replace Card": "替换手牌",
		"Connect": "连接服务器", "Resume": "重连游戏",
		"Server IP": "服务器IP地址", "Query Port": "服务器端口", "Start/Join Table": "新开/加入一桌",
		"Wait for opponent to finish mulligan": "等待对方完成换牌",
		"Want to request game copy. But table iD is wrong": "请求对方发送当前游戏的复制。但是桌子ID错误",
		"No tables left. Please wait": "目前没有空桌子了，请等待",
		"This table ID is already taken.": "输入的桌子ID已经被占用",
		"Can't connect to the server's query port": "无法连接到服务器端口",
		"Deck code is wrong. Check before retry": "套牌代码错误。请检查后重试",
		"Opponent disconnected. Closing": "对方连接断开。正在关闭",
		"View Cards": "显示卡牌", "Last Page": "上一页", "Next Page": "下一页",
		"Class": "职业", "Mana": "费用", "Expansion": "版本",
		"Card Wished": "许愿的卡牌", "Wish": "许愿",
		"The card is not a Basic or Classic card": "选择的卡不是基础卡或经典卡",
		"No wish card selected yet": "尚未选择许愿的卡牌",
		"Already the first page": "已是第一页", "Already the last page": "已是最后一页",
		"View Collectible Card": "查看所有可收藏卡牌",
		}
		
def txt(s, CHN=True):
	return s if not CHN else texts[s]
	
#For single-player GUI
Hero1Pos, Hero2Pos = (0.5*X, Y-0.25*Y), (0.5*X, 0.25*Y)
Weapon1Pos, Weapon2Pos = (0.42*X, Y-0.25*Y), (0.42*X, 0.25*Y)
Power1Pos, Power2Pos = (0.58*X, Y-0.25*Y), (0.58*X, 0.25*Y)

#For 2-player GUI
seeEnemyHand = False
ReplayMovesThisTurn = False
LeftorRight = 1
if LeftorRight: shift, offset =  0, 0
else: shift, offset = 100, 320

OwnHeroPos, EnemyHeroPos = (shift+0.5*X, Y-0.25*Y), (shift+0.5*X, 0.25*Y)
OwnWeaponPos, EnemyWeaponPos = (shift+0.41*X, Y-0.25*Y), (shift+0.41*X, 0.25*Y)
OwnPowerPos, EnemyPowerPos = (shift+0.58*X, Y-0.25*Y), (shift+0.58*X, 0.25*Y)

#For Transfer Student and board info
BoardIndex = ["0 Random Game Board",
			"1 Classic Ogrimmar", "2 Classic Stormwind", "3 Classic Stranglethorn", "4 Classic Four Wind Valley",
			#"5 Naxxramas", "6 Goblins vs Gnomes", "7 Black Rock Mountain", "8 The Grand Tournament", "9 League of Explorers Museum", "10 League of Explorers Ruins",
			#"11 Corrupted Stormwind", "12 Karazhan", "13 Gadgetzan",
			#"14 Un'Goro", "15 Frozen Throne", "16 Kobolds",
			#"17 Witchwood", "18 Boomsday Lab", "19 Rumble",
			"20 Dalaran", "21 Uldum Desert", "22 Uldum Oasis", "23 Dragons",
			"24 Outlands", "25 Scholomance Academy", "26 Darkmoon Faire",
			]
			
folderNameTable = {"Basic":"Basic", "Classic": "Classic",
					"GVG": "Pre_Dalaran", "Kobolds": "Pre_Dalaran", "Boomsday": "Pre_Dalaran",
					"Shadows": "Shadows", "Uldum": "Uldum", "Dragons": "Dragons", "Galakrond": "Galakrond",
					"DHInitiate": "DHInitiate", "Outlands": "Outlands", "Academy": "Academy", "Darkmoon": "Darkmoon",
					}
					
from tkinter import messagebox
import tkinter as tk
import PIL.Image, PIL.ImageTk
import pickle, inspect
import os
import threading
import time

from Game import gameStatusDict

def pickleObj2Str(obj):
	s = str(pickle.dumps(obj, 0).decode())
	return s.replace("\n", "*")
	
def unpickleStr2Obj(s):
	s = s.replace("*", "\n")
	obj = pickle.loads(bytes(s.encode()))
	return obj
	
def pickleObj2Bytes(obj):
	return pickle.dumps(obj, 0)
	
def unpickleBytes2Obj(s):
	return pickle.loads(s)
	
def fixedList(listObj):
	return listObj[0:len(listObj)]
	
def extractfrom(target, listObj):
	try: return listObj.pop(listObj.index(target))
	except: return None
	
def findPicFilepath(card):
	if card.type == "Dormant": #休眠的随从会主动查看自己携带的originalMinion的名字和index
		index = card.originalMinion.index
		folderName = folderNameTable[index.split('~')[0] ]
		if inspect.isclass(card.originalMinion):
			name = card.originalMinion.__name__
		else: #Instances don't have __name__
			name = type(card.originalMinion).__name__
		path = "Crops\\%s\\"%folderName
	else: #type == "Weapon", "Minion", "Spell", "Hero", "Power"
		index, name = card.index, type(card).__name__
		if card.type != "Hero" and card.type != "Power":
			folderName = folderNameTable[index.split('~')[0] ]
			path = "Crops\\%s\\"%folderName
		else: path = "Crops\\HerosandPowers\\"
		
	name = name.split("_")[0] if "Mutable" in name else name
	if card.type == "Minion" and card.index.startswith("SV_") and card.status["Evolved"] > 0:
		name += "_1"
	if "Accelerate" in name: name = name.replace("_Accelerate","")
	if "Crystallize" in name: name = name.replace("_Crystallize","")
	if "_Token" in name: name = name.replace("_Token","")
	filepath = path + "%s.png"%name
	return filepath
	
def findPicFilepath_FullImg(card):
	if card.type == "Dormant": #休眠的随从会主动查看自己携带的originalMinion的名字和index
		index = card.originalMinion.index
		folderName = folderNameTable[index.split('~')[0] ]
		if inspect.isclass(card.originalMinion):
			name = card.originalMinion.__name__
		else: #Instances don't have __name__
			name = type(card.originalMinion).__name__
		path = "Images\\%s\\"%folderName
	else: #type == "Weapon", "Minion", "Spell", "Hero", "Power"
		index, name = card.index, type(card).__name__
		if card.type != "Hero" and card.type != "Power":
			folderName = folderNameTable[index.split('~')[0] ]
			path = "Images\\%s\\"%folderName
		else: path = "Images\\HerosandPowers\\"
		
	name = name.split("_")[0] if "Mutable" in name else name
	if card.type == "Minion" and card.index.startswith("SV_") and card.status["Evolved"] > 0:
		name += "_1"
	if "Accelerate" in name: name = name.replace("_Accelerate","")
	if "Crystallize" in name: name = name.replace("_Crystallize","")
	if "_Token" in name: name = name.replace("_Token","")
	filepath = path + "%s.png"%name
	return filepath
	
	
	
class CardLabel(tk.Label):
	def __init__(self, btn, text='', bg="white", fg='black', font=("Yahei", 11, "bold")):
		tk.Label.__init__(self, text=text, bg=bg, fg=fg, font=font)
		self.btn = btn
		self.x, self.y = 0, 0
		
	def plot(self, x, y):
		self.x, self.y = x, y
		self.place(x=x, y=y, anchor='c')
		self.btn.labels.append(self)
		
	def replot(self):
		self.place(x=self.x, y=self.y, anchor='c')
		
	def moveby(self, xOffset, yOffset):
		self.x, self.y = self.x + xOffset, self.y + yOffset
		self.place(x=self.x, y=self.y, anchor='c')
		
"""Hand Buttons"""
class HandButton(tk.Button): #Cards that are in hand. 目前而言只有一张牌是自己可以打出的牌的时候点击是有响应的。
	def __init__(self, GUI, card, enemyCanSee=False):
		game = GUI.Game
		self.waiting = False
		if enemyCanSee or not hasattr(GUI, "ID") or seeEnemyHand or GUI.ID == card.ID:
			self.decideColorOrig(GUI, card)
			img = PIL.Image.open(findPicFilepath(card)).resize((HandImgSize, HandImgSize))
			ph = PIL.ImageTk.PhotoImage(img)
			tk.Button.__init__(self, relief=tk.FLAT, image=ph, master=GUI.GamePanel, bg=self.colorOrig, width=HandIconWidth, height=HandIconHeight)
			self.GUI, self.card, self.selected, self.image = GUI, card, 0, ph
			self.x, self.y, self.labels, self.zone = 0, 0, [], GUI.handZones[card.ID]
			self.bind('<Button-1>', self.leftClick)   # bind left mouse click
			self.bind('<Button-3>', self.rightClick)   # bind right mouse click
			self.bind("<Enter>", self.crosshairEnter)
			self.bind("<Leave>", self.crosshairLeave)
			if card.index.startswith("SV_") and hasattr(card, "fusion"):
				self.bind("<Double-Button-1>", lambda event: game.Discover.startFusion(card, card.findFusionMaterials()))
			#Info bookkeeping
			self.cardInfo, self.mana = type(card), card.getMana()
			if card.type == "Minion": self.attack, self.health = card.attack, card.health
			elif card.type == "Weapon": self.attack, self.health = card.attack, card.durability
			else: self.attack, self.health = 0, 0
		else:
			tk.Button.__init__(self, relief=tk.FLAT, master=GUI.GamePanel, bg="grey46", width=HandIconWidth_noImg, height=HandIconHeight_noImg)
			self.GUI, self.card, self.selected, self.image = GUI, card, 0, None
			self.x, self.y, self.labels, self.zone = 0, 0, [], GUI.handZones[card.ID]
			
	def decideColorOrig(self, GUI, card): #decide the correct colorOrig and set it
		if not hasattr(GUI, "ID") or seeEnemyHand or GUI.ID == card.ID:
			game, self.colorOrig = card.Game, "red"
			if card.ID == game.turn and game.Manas.affordable(card):
				if (card.type == "Spell" and card.available()) or ((card.type == "Minion" or card.type == "Amulet") and game.space(card.ID) > 0 and card.available()) or card.type == "Weapon" or card.type == "Hero":
					self.colorOrig = "blue" if card.evanescent else ((card.effectViable if isinstance(card.effectViable, str) else "yellow") if card.effectViable else "green3")
		else: self.colorOrig = "grey46" #Only is grey when it's opponent's card in 2PGUI in "Don't show opponent cards" mode
		
	def leftClick(self, event):
		if self.GUI.UI < 3 and self.GUI.UI > -1: #只有不在发现或动画演示中才会响应
			card, ID, game = self.card, self.card.ID, self.GUI.Game
			if ID == game.turn and game.Manas.affordable(card) and ((card.type == "Spell" and card.available()) or ((card.type == "Minion" or card.type == "Amulet") and game.space(ID) > 0 and card.available()) or card.type == "Weapon" or card.type == "Hero"):
				self.selected = 1 - self.selected #在选中一张牌后再次选择它，会取消所有选择
				if self.selected == 1:
					self.configure(bg="white")
					selectedSubject = card.type+"inHand"
					self.GUI.resolveMove(card, self, selectedSubject) #把一张牌，这个牌的按钮和这个牌的信息传入resolveMove
				else: self.GUI.cancelSelection()
			else:
				self.selected = 0
				self.configure(bg="red")
				self.GUI.cancelSelection()
				
	def rightClick(self, event):
		self.GUI.cancelSelection()
		
	def crosshairEnter(self, event):
		self.waiting = True
		thread = threading.Thread(target=self.wait2Display, daemon=True)
		thread.start()
		
	def crosshairLeave(self, event):
		self.waiting = False
		try: self.GUI.lbl_CardStatus.destroy()
		except: pass
		
	def wait2Display(self):
		time.sleep(waitTime4Info)
		if self.waiting:
			try: self.GUI.lbl_CardStatus.destroy()
			except: pass
			self.GUI.lbl_CardStatus = tk.Label(self.GUI.GamePanel, text=self.card.cardStatus(), bg="SteelBlue1", font=("Yahei", 12, "bold"), anchor='w', justify="left")
			self.GUI.lbl_CardStatus.place(relx=infoDispXPos, rely=0.5, anchor='c')
			self.GUI.displayCard(self.card)
			
	def tempLeftClick(self, event): #For Shadowverse
		self.GUI.select = self.card
		self.var.set(1)
		
	def tempLeftClick_Fusion(self, event):
		self.selected = 1 - self.selected
		if self.selected:
			self.configure(bg="white")
			self.GUI.fusionMaterials.append(self.card)
		else:
			self.configure(bg="cyan2")
			try: self.GUI.fusionMaterials.remove(self.card)
			except: pass
			
	def plot(self, x, y):
		card = self.card
		self.x, self.y, self.labels = x, y, []
		self.place(x=x, y=y, anchor='c')
		if not hasattr(self.GUI, "ID") or seeEnemyHand or self.GUI.ID == card.ID:
			CardLabel(btn=self, text=self.GUI.wrapText(card.name), fg="black").plot(x=x, y=y-CARD_Y/2)
			CardLabel(btn=self, text=str(card.getMana()), fg="black").plot(x=x-0.39*CARD_X, y=y-0.22*CARD_Y)
			#Minions and weapons have stats
			if card.type == "Minion":
				attack, attack_Enchant, health, health_max = card.attack, card.attack_Enchant, card.health, card.health_max
				attColor = "green3" if attack_Enchant > card.attack_0 else "black"
				healthColor = ("black" if health_max <= card.health_0 else "green3") if health >= health_max else "red"
				CardLabel(btn=self, text=str(attack), fg=attColor).plot(x=x-0.39*CARD_X, y=y+0.39*CARD_Y)
				CardLabel(btn=self, text=str(health), fg=healthColor).plot(x=x+0.39*CARD_X, y=y+0.39*CARD_Y)
			elif card.type == "Weapon":
				attack, dura = card.attack, card.durability
				attColor = "green3" if attack > type(card).attack else "black"
				duraColor = "green3" if dura > type(card).durability else "black"
				CardLabel(btn=self, text=str(attack), fg=attColor).plot(x=x-0.39*CARD_X, y=y+0.39*CARD_Y)
				CardLabel(btn=self, text=str(dura), fg=duraColor).plot(x=x+0.39*CARD_X, y=y+0.39*CARD_Y)
			text = "" #Spells also have keyWords
			for key, value in card.keyWords.items():
				if value > 0: text += key+'\n'
			self['text'] = text
		self.zone.btnsDrawn.append(self)
		
	def hide(self): #因为DiscoverCardOption是HandButton上面定义的，不用再次定replot
		self.place_forget()
		for label in self.labels: label.place_forget()
		
	def replot(self): #After the button is hidden by place_forget, use this to show the button again
		self.place(x=self.x, y=self.y, anchor='c')
		for label in self.labels: label.replot()
		
	def showOpponent(self):
		if not self.labels: #Copy the content from plot() method
			card = self.card
			img = PIL.Image.open(findPicFilepath(card)).resize((HandImgSize, HandImgSize))
			ph = PIL.ImageTk.PhotoImage(img)
			self.image = ph
			self.configure(image=ph)
			self.configure(width=HandIconWidth)
			self.configure(height=HandIconHeight)
			CardLabel(btn=self, text=self.GUI.wrapText(card.name), fg="black").plot(x=self.x, y=self.y-CARD_Y/2)
			CardLabel(btn=self, text=str(card.getMana()), fg="black").plot(x=self.x-0.39*CARD_X, y=self.y-0.22*CARD_Y)
			#Minions and weapons have stats
			if card.type == "Minion":
				attack, attack_Enchant, health, health_max = card.attack, card.attack_Enchant, card.health, card.health_max
				attColor = "green3" if attack_Enchant > card.attack_0 else "black"
				healthColor = ("black" if health_max <= card.health_0 else "green3") if health >= health_max else "red"
				CardLabel(btn=self, text=str(attack), fg=attColor).plot(x=self.x-0.39*CARD_X, y=self.y+0.39*CARD_Y)
				CardLabel(btn=self, text=str(health), fg=healthColor).plot(x=self.x+0.39*CARD_X, y=self.y+0.39*CARD_Y)
			elif card.type == "Weapon":
				attack, dura = card.attack, card.durability
				attColor = "green3" if attack > type(card).attack else "black"
				duraColor = "green3" if dura > type(card).durability else "black"
				CardLabel(btn=self, text=str(attack), fg=attColor).plot(x=self.x-0.39*CARD_X, y=self.y+0.39*CARD_Y)
				CardLabel(btn=self, text=str(dura), fg=duraColor).plot(x=self.x+0.39*CARD_X, y=self.y+0.39*CARD_Y)
			text = "" #Spells also have keyWords
			for key, value in card.keyWords.items():
				if value > 0: text += key+'\n'
			self['text'] = text
			
	def remove(self):
		for label in self.labels: label.destroy()
		self.destroy()
		try: self.zone.btnsDrawn.remove(self)
		except: pass
		
	def move2(self, x, y):
		xOffset, yOffset = x - self.x, y - self.y
		self.x, self.y = x, y
		self.place(x=x, y=y, anchor='c')
		for label in self.labels: label.moveby(xOffset, yOffset)
		
	def represents(self, card):
		if not hasattr(self.GUI, "ID") or seeEnemyHand or self.GUI.ID == card.ID: #If UI shows it
			if not isinstance(card, self.cardInfo) or self.mana != card.getMana(): return False
			if card.type == "Minion": attack, health = card.attack, card.health
			elif card.type == "Weapon": attack, health = card.attack, card.durability
			else: attack, health = 0, 0
			return self.attack == attack and self.health == health
		else: return True
		
class HandZone:
	def __init__(self, GUI, ID):
		self.GUI, self.ID, self.btnsDrawn = GUI, ID, []
		
	def draw(self, cardMoving2=-2, steps=10):
		game, ownHand = self.GUI.Game, self.GUI.Game.Hand_Deck.hands[self.ID]
		ownID = 1 if not hasattr(self.GUI, "ID") else self.GUI.ID #1PGUI has virtual ID of 1
		y = int(Y - 0.07*Y) if self.ID == ownID else int(0.11*Y) #The vertical position of the cards drawn
		leftPos = (0.5 - (0.5-0.043) * (len(ownHand) - 1) / 14) * X
		posHands = [(int(leftPos+(X/14)*i), y) for i in range(len(ownHand))]
		if self.btnsDrawn:
			#Goal: For each card in hand, find the corresponding buttons already drawn.
			#If buttons no longer has a card it represents, remove it.
			btns, btnsKept, posEnds = [None] * len(ownHand), [], []
			for i, card in enumerate(ownHand): #第i张处于是否已经有button代表它了
				for j, btn in enumerate(self.btnsDrawn):
					if btn.card == card and btn.represents(card):
						btn = self.btnsDrawn.pop(j)
						btn.card = card
						btns[i] = btn
						btnsKept.append(btn) #已经有btn代表的牌会被录入btnsKept和posEnds
						posEnds.append(posHands[i])
						break
			for btn in reversed(self.btnsDrawn): btn.remove()
			#如果需要第cardMoving2个btn等待时
			if cardMoving2 > -2 and btnsKept:
				lastBtn, lastPos = None, None
				if cardMoving2 == -1:
					if btnsKept[-1].card == ownHand[-1]:
						lastBtn, lastPos = btnsKept.pop(), posEnds.pop()
				else:
					for i, btn in enumerate(btnsKept):
						if btn.card == ownHand[cardMoving2]:
							lastBtn, lastPos = btnsKept.pop(i), posEnds.pop(i)
				self.GUI.moveBtnsAni(btnsKept, posEnds)
				if lastBtn:
					self.GUI.moveBtnsAni(lastBtn, lastPos)
			else: self.GUI.moveBtnsAni(btnsKept, posEnds) #其他情况下最后一个btn不等待，直接与其他的handBtn一同移动
			for pos, btn, card in zip(posHands, btns, ownHand):
				if btn:
					self.btnsDrawn.append(btn)
					btn.decideColorOrig(self.GUI, card)
					btn.configure(bg=btn.colorOrig) #Reset the color of the button
				else: HandButton(self.GUI, card).plot(x=pos[0], y=pos[1])
		else:
			for pos, card in zip(posHands, ownHand):
				HandButton(self.GUI, card).plot(x=pos[0], y=pos[1])
				
	#This function is EXCLUSIVE for single-player GUI replay
	def redraw(self):
		#Clear all the buttons drawn.
		for btn in reversed(self.btnsDrawn): btn.remove()
		#Redraw all the hands
		game, ownHand = self.GUI.Game, self.GUI.Game.Hand_Deck.hands[self.ID]
		y = int(Y - 0.07*Y) if self.ID == 1 else int(0.11*Y)
		leftPos = (0.5 - (0.5-0.043) * (len(ownHand) - 1) / 14) * X
		posHands = [(int(leftPos+(X/14)*i), y) for i in range(len(ownHand))]
		for pos, card in zip(posHands, ownHand):
			HandButton(self.GUI, card).plot(x=pos[0], y=pos[1])
			
			
class MulliganButton(tk.Button):
	def __init__(self, GUI, card):
		img = PIL.Image.open(findPicFilepath_FullImg(card)).resize((210, 280))
		ph = PIL.ImageTk.PhotoImage(img)
		tk.Button.__init__(self, relief=tk.FLAT, master=GUI.GamePanel, image=ph, bg="green", width=int(2.5*CARD_X), height=int(2.4*CARD_Y))
		self.GUI, self.card, self.image, self.selected = GUI, card, ph, 0
		self.bind("<Button-1>", self.respond)
		
	def respond(self, event):
		self.selected = 1 - self.selected
		self.configure(bg = "red" if self.selected == 1 else "green3")
		if hasattr(self.GUI, "ID"):
			for i, card in enumerate(self.GUI.Game.mulligans[self.GUI.ID]):
				if card == self.card:
					self.GUI.mulliganStatus[i] = 1 - self.GUI.mulliganStatus[i]
					break
		else:
			for ID in range(1, 3):
				for i, card in enumerate(self.GUI.Game.mulligans[ID]):
					if card == self.card: #在mulligans中找到这个按钮对应的卡牌，然后将其对应的换牌状态toggle
						self.GUI.mulliganStatus[ID][i] = 1 - self.GUI.mulliganStatus[ID][i]
						break
		
	def plot(self, x, y, shrink=False):
		self.place(x=x, y=y, anchor='c')
		self.GUI.btnsDrawn.append(self)
		
	def remove(self):
		self.destroy()
		
		
class CardCollectionButton(tk.Button):
	def __init__(self, window, card):
		img = PIL.Image.open(findPicFilepath_FullImg(card)).resize((270, 360))
		ph = PIL.ImageTk.PhotoImage(img, master=window.displayPanel)
		tk.Button.__init__(self, master=window.displayPanel, image=ph)
		self.window, self.GUI, self.card, self.image = window, window.GUI, card, ph
		self.bind("<Button-1>", self.respond)
		
	def respond(self, event):
		img = PIL.Image.open(findPicFilepath_FullImg(self.card)).resize((210, 280))
		ph = PIL.ImageTk.PhotoImage(img, master=self.window.GUI.sidePanel)
		self.GUI.lbl_wish.config(image=ph)
		self.GUI.lbl_wish.image = ph
		self.GUI.cardWished = type(self.card)
		
	def plot(self, i, j):
		self.grid(row=i, column=j)
		self.window.btnsDrawn.append(self)
		
"""Choice or discover buttons"""
class DiscoverCardButton(HandButton):
	def __init__(self, GUI, card):
		game = GUI.Game
		img = PIL.Image.open(findPicFilepath(card)).resize((int(0.95*Hand_X), int(0.95*Hand_X)))
		ph = PIL.ImageTk.PhotoImage(img)
		tk.Button.__init__(self, relief=tk.FLAT, image=ph, master=GUI.GamePanel, bg="green3", width=Hand_X, height=int(1.3*Hand_Y))
		self.GUI, self.card, self.selected, self.image, self.colorOrig = GUI, card, 0, ph, "green3"
		self.x, self.y, self.labels, self.zone = 0, 0, [], GUI.handZones[card.ID]
		self.bind('<Button-1>', self.leftClick)   # bind left mouse click
		self.bind('<Button-3>', self.rightClick)   # bind right mouse click
		
	def leftClick(self, event):
		discoverOptions = [btn for btn in self.GUI.btnsDrawn if isinstance(btn, (DiscoverOptionButton, DiscoverCardButton))]
		for button in discoverOptions:
			if button == self:
				self.GUI.discover = self.card
				self.configure(bg="white")
				self.selected = 1
			else:
				button.configure(bg="green3")
				button.selected = 0
				
	def rightClick(self, event):
		self.card.STATUSPRINT()
		self.GUI.displayCard(self.card)
		
	def plot(self, x, y):
		self.x, self.y, self.labels = x, y, []
		self.place(x=x, y=y, anchor='c')
		CardLabel(btn=self, text=self.GUI.wrapText(self.card.name), fg="black").plot(x=x, y=y-CARD_Y/2)
		CardLabel(btn=self, text=str(self.card.mana), fg="black").plot(x=x-0.39*CARD_X, y=y-0.22*CARD_Y)
		#Minions and weapons have stats
		if self.card.type == "Minion":
			attack, attack_Enchant, health, health_max = self.card.attack, self.card.attack_Enchant, self.card.health, self.card.health_max
			attColor = "green3" if attack_Enchant > self.card.attack_0 else "black"
			healthColor = ("black" if health_max <= self.card.health_0 else "green3") if health >= health_max else "red"
			CardLabel(btn=self, text=str(attack), fg=attColor).plot(x=x-0.39*CARD_X, y=y+0.39*CARD_Y)
			CardLabel(btn=self, text=str(health), fg=healthColor).plot(x=x+0.39*CARD_X, y=y+0.39*CARD_Y)
		elif self.card.type == "Weapon":
			attack, dura = self.card.attack, self.card.durability
			attColor = "green3" if attack > type(self.card).attack else "black"
			duraColor = "green3" if dura > type(self.card).durability else "black"
			CardLabel(btn=self, text=str(attack), fg=attColor).plot(x=x-0.39*CARD_X, y=y+0.39*CARD_Y)
			CardLabel(btn=self, text=str(dura), fg=duraColor).plot(x=x+0.39*CARD_X, y=y+0.39*CARD_Y)
		text = "" #Spells also have keyWords
		for key, value in self.card.keyWords.items():
			if value > 0: text += key+'\n'
		self['text'] = text
		self.GUI.btnsDrawn.append(self)
		
	def remove(self):
		for label in self.labels: label.destroy()
		self.destroy()
		try: self.GUI.btnsDrawn.remove(self)
		except: pass
		
		
class DiscoverOptionButton(tk.Button):
	def __init__(self, GUI, card):
		tk.Button.__init__(self, relief=tk.FLAT, master=GUI.GamePanel, bg="green3", width=card_x, height=card_y, font=("Yahei", 12, "bold"))
		self.GUI, self.card, self.selected = GUI, card, 0
		self.x, self.y, self.labels = 0, 0, []
		self.bind("<Button-1>", self.respond)
		
	def plot(self, x, y):
		self.x, self.y, self.labels = x, y, []
		self.place(x=x, y=y, anchor='c')
		CardLabel(btn=self, text=self.GUI.wrapText(self.card.name), fg="black").plot(x=x, y=y-CARD_Y/2)
		self['text'] = self.GUI.wrapText(self.card.description)
		self.GUI.btnsDrawn.append(self)
		
	def respond(self, event):
		discoverOptions = [btn for btn in self.GUI.btnsDrawn if isinstance(btn, (DiscoverOptionButton, DiscoverCardButton))]
		for button in discoverOptions:
			if button == self:
				self.GUI.discover = self.card
				self.configure(bg="white")
				self.selected = 1
			else:
				button.configure(bg="green3")
				button.selected = 0
				
	def hide(self):
		self.place_forget()
		for label in self.labels: label.place_forget()
		
	#DiscoverOption由于是tk.Button上面直接定义的类，所以要再次定义replot函数
	def replot(self): #After the button is hidden by place_forget, use this to show the button again
		self.place(x=self.x, y=self.y, anchor='c')
		for label in self.labels: label.replot()
		
	def remove(self):
		for label in self.labels: label.destroy()
		self.destroy()
		try: self.GUI.btnsDrawn.remove(self)
		except: pass
		
		
class DiscoverHideButton(tk.Button):
	def __init__(self, GUI):
		tk.Button.__init__(self, relief=tk.FLAT, master=GUI.GamePanel, text="Hide", bg="green3", width=5, height=2, font=("Yahei", 12, "bold"))
		self.bind("<Button-1>", self.respond)
		self.GUI, self.selected, self.colorOrig = GUI, 0, "green3"
		
	def respond(self, event):
		self.selected = 1 - self.selected
		if self.selected == 1: #When hide is positive, the discover option buttons are destroyed
			self.configure(bg="red")
			for btn in self.GUI.btnsDrawn:
				if isinstance(btn, (DiscoverOptionButton, DiscoverCardButton)): btn.hide()
		else:
			self.configure(bg="green3")
			for btn in self.GUI.btnsDrawn:
				if isinstance(btn, (DiscoverOptionButton, DiscoverCardButton)): btn.replot()
				
				
class ChooseOneButton(tk.Button):
	def __init__(self, GUI, card, color):
		tk.Button.__init__(self, relief=tk.FLAT, master=GUI.GamePanel, text=GUI.wrapText(card.description, 8), bg="green3", width=card_x, height=card_y, font=("Yahei", 10, "bold"))
		self.GUI, self.card, self.selected, self.colorOrig = GUI, card, 0, color
		self.bind("<Button-1>", self.respond)
		self.x, self.y, self.labels = 0, 0, []
		
	def plot(self, x, y):
		self.x, self.y, self.labels = x, y, []
		self.place(x=x, y=y, anchor='c')
		CardLabel(self, text=self.GUI.wrapText(self.card.name), fg="black").plot(x=x, y=y-0.4*CARD_Y)
		self.GUI.btnsDrawn.append(self)
		
	def respond(self, event):
		self.GUI.resolveMove(self.card, self, "ChooseOneOption")
		
	def remove(self):
		for label in self.labels: label.destroy()
		self.destroy()
		try: self.GUI.btnsDrawn.remove(self)
		except: pass
		
		
"""Minion/Permanet buttons and zone"""
class MinionButton(tk.Button):
	def __init__(self, GUI, minion):
		self.decideColorOrig(GUI, minion)
		self.waiting = False
		seq = minion.seq
		text = {0: "1st", 1: "2nd", 2: "3rd"}[seq] if seq < 3 else "%dth"%(seq+1) + ' '
		for key, value in minion.keyWords.items():
			if value > 0: text += key+'\n'
		img = PIL.Image.open(findPicFilepath(minion)).resize((MinionImgSize, MinionImgSize))
		ph = PIL.ImageTk.PhotoImage(img)
		tk.Button.__init__(self, text=text, image=ph, relief=tk.FLAT, compound=tk.TOP, anchor ='n', master=GUI.GamePanel, bg=self.colorOrig, width=CARD_X, height=CARD_Y, font=("Yahei", 10, "bold"))
		self.GUI, self.card, self.image, self.selected = GUI, minion, ph, 0
		self.bind('<Button-1>', self.leftClick)
		self.bind('<Button-3>', self.rightClick)
		self.bind("<Enter>", self.crosshairEnter)
		self.bind("<Leave>", self.crosshairLeave)
		self.x, self.y, self.labels, self.zone = 0, 0, [], GUI.boardZones[minion.ID]
		#Info bookkeeping
		self.cardInfo = type(minion)
		if minion.type == "Minion":
			self.attack, self.health, self.keyWords = minion.attack, minion.health, ''
			for key, value in minion.keyWords.items():
				if value > 0: self.keyWords += key
		self.trigs = [type(trig) for trig in minion.trigsBoard + (minion.deathrattles if minion.type == "Minion" else [])]
		self.counts = sum(trig.counter for trig in minion.trigsBoard if hasattr(trig, "counter"))
		self.auras = [type(aura) for aura in minion.auras.values()]
		
	def decideColorOrig(self, GUI, minion):
		if minion.type != "Minion": self.colorOrig = "grey46"
		else:
			if minion.dead: self.colorOrig = "grey25"
			elif minion == GUI.subject: self.colorOrig = "white"
			elif minion == GUI.target: self.colorOrig = "cyan2"
			else: self.colorOrig = "green3" if minion.canAttack() else "red"
			
	def leftClick(self, event):
		if self.GUI.UI < 3 and self.GUI.UI > -1:
			if self.card.type == "Minion":
				selectedSubject = "MiniononBoard"
				self.GUI.resolveMove(self.card, self, selectedSubject)
			elif self.card.type == "Dormant":
				if self.GUI.UI == 2:
					selectedSubject = "DormantonBoard"
					self.GUI.resolveMove(self.card, self, selectedSubject)
				else: self.GUI.cancelSelection()
			elif self.card.type == "Amulet":
				selectedSubject = "AmuletonBoard"
				self.GUI.resolveMove(self.card, self, selectedSubject)
				
	def rightClick(self, event):
		self.GUI.cancelSelection()
		
	def crosshairEnter(self, event):
		self.waiting = True
		thread = threading.Thread(target=self.wait2Display, daemon=True)
		thread.start()
		
	def crosshairLeave(self, event):
		self.waiting = False
		try: self.GUI.lbl_CardStatus.destroy()
		except: pass
		
	def wait2Display(self):
		time.sleep(waitTime4Info)
		if self.waiting:
			if not hasattr(self.GUI, "ID") or seeEnemyHand or self.card.ID == self.GUI.ID:
				hideSomeTrigs = False
			else: hideSomeTrigs = True
			try: self.GUI.lbl_CardStatus.destroy()
			except: pass
			self.GUI.lbl_CardStatus = tk.Label(self.GUI.GamePanel, text=self.card.cardStatus(hideSomeTrigs), bg="SteelBlue1", font=("Yahei", 12, "bold"), anchor='w', justify="left")
			self.GUI.lbl_CardStatus.place(relx=infoDispXPos, rely=0.5, anchor='c')
			self.GUI.displayCard(self.card)
			
	def tempLeftClick(self, event): #For Shadowverse
		self.GUI.select = self.card
		self.var.set(1)
		
	def plot(self, x, y):
		self.x, self.y, self.labels = x, y, []
		self.place(x=x, y=y, anchor='c')
		if self.card.auras:
			CardLabel(btn=self, text='                            ', bg="gold", font=("yellow", 4)).plot(x=x, y=y+0.53*CARD_Y)
		trigsBoard = [trig for trig in self.card.trigsBoard if not hasattr(trig, "hide")]
		if trigsBoard or ((self.card.type == "Minion" or self.card.type == "Amulet") and self.card.deathrattles):
			string = ""
			for trig in self.card.trigsBoard:
				if hasattr(trig, "counter"): string += "%d "%trig.counter
			CardLabel(btn=self, text=' %s'%string, bg="yellow").plot(x=x, y=y+0.54*CARD_Y)
		if self.card.type == "Minion":
			attColor = "green3" if self.card.attack_Enchant > self.card.attack_0 else "black"
			healthColor = "red" if self.card.health < self.card.health_max else \
						("black" if self.card.health_max <= self.card.health_0 else "green3")
			CardLabel(btn=self, text=str(self.card.attack), fg=attColor).plot(x=x-0.42*CARD_X, y=y+0.43*CARD_Y)
			CardLabel(btn=self, text=str(self.card.health), fg=healthColor).plot(x=x+0.42*CARD_X, y=y+0.43*CARD_Y)
		self.zone.btnsDrawn.append(self)
		
	def move2(self, x, y):
		xOffset, yOffset = x - self.x, y - self.y
		self.x, self.y = x, y
		self.place(x=x, y=y, anchor='c')
		for label in self.labels: label.moveby(xOffset, yOffset)
		
	def remove(self):
		for label in self.labels: label.destroy()
		self.destroy()
		try: self.zone.btnsDrawn.remove(self)
		except: pass
		
	def represents(self, minion):
		if not isinstance(minion, self.cardInfo): return False
		if minion.type == "Minion": #Only need to check minion for now. Dormants don't have keyWords
			attack, health, keyWords = minion.attack, minion.health, ''
			for key, value in minion.keyWords.items():
				if value > 0: keyWords += key
			if self.attack != attack or self.health != health or self.keyWords != keyWords: return False
		trigs = [type(trig) for trig in minion.trigsBoard + (minion.deathrattles if minion.type == "Minion" else [])]
		counts = sum(trig.counter for trig in minion.trigsBoard if hasattr(trig, "counter"))
		auras = [type(aura) for aura in minion.auras.values()]
		return self.trigs == trigs and self.counts == counts and self.auras == auras
		
class BoardZone:
	def __init__(self, GUI, ID):
		self.GUI, self.ID, self.btnsDrawn = GUI, ID, []
		
	def draw(self):
		game, ownMinions = self.GUI.Game, self.GUI.Game.minions[self.ID]
		ownID = 1 if not hasattr(self.GUI, "ID") else self.GUI.ID #1PGUI has virtual ID of 1
		y = int(0.59*Y) if self.ID == ownID else int(0.41*Y) #vertical position of the minions/dormants drawn
		leftPos = max(0.1, 0.5-0.05*(len(ownMinions)-1) ) * X
		posMinions = [(int(leftPos+(X/10)*i), y) for i in range(len(ownMinions))]
		if self.btnsDrawn:
			btns, btnsKept, posEnds = [None] * len(ownMinions), [], []
			for i, minion in enumerate(ownMinions):
				for j, btn in enumerate(self.btnsDrawn):
					if btn.card == minion and btn.represents(minion):
						btn = self.btnsDrawn.pop(j)
						btn.card = minion
						btns[i] = btn
						btnsKept.append(btn)
						posEnds.append(posMinions[i])
						break
			for btn in reversed(self.btnsDrawn): btn.remove()
			self.GUI.moveBtnsAni(btnsKept, posEnds)
			for pos, btn, minion in zip(posMinions, btns, ownMinions):
				if btn:
					self.btnsDrawn.append(btn)
					#Reset the text involving sequence and the color of the minion
					seq = minion.seq
					text = {0: "1st", 1: "2nd", 2: "3rd"}[seq] if seq < 3 else "%dth"%(seq+1) + ' '
					if minion.type == "Minion":
						for key, value in minion.keyWords.items():
							if value > 0: text += key+'\n'
						btn.decideColorOrig(self.GUI, minion)
						btn['text'] = text
						btn.configure(bg=btn.colorOrig) #Reset the color of the button
				else: MinionButton(self.GUI, minion).plot(x=pos[0], y=pos[1])
		else:
			for pos, minion in zip(posMinions, ownMinions):
				MinionButton(self.GUI, minion).plot(pos[0], pos[1])
				
	#This function is EXCLUSIVE for single-player GUI replay
	def redraw(self):
		#Clear all the buttons drawn. 
		for btn in reversed(self.btnsDrawn): btn.remove()
		#Redraw all the hands
		game, ownMinions = self.GUI.Game, self.GUI.Game.minions[self.ID]
		y = int(0.59*Y) if self.ID == 1 else int(0.41*Y) #vertical position of the minions/dormants drawn
		leftPos = (0.5 - 0.0583 * (len(ownMinions) - 1)) * X
		posMinions = [(int(leftPos+(X/10)*i), y) for i in range(len(ownMinions))]
		for pos, card in zip(posMinions, ownMinions):
			HandButton(self.GUI, card).plot(x=pos[0], y=pos[1])
			
"""Hero/Weapon/HeroPower buttons and zone"""
class HeroButton(tk.Button):
	def __init__(self, GUI, hero):
		self.decideColorOrig(GUI, hero)
		self.waiting = False
		img = PIL.Image.open(findPicFilepath(hero)).resize((HeroIconSize, HeroIconSize))
		ph = PIL.ImageTk.PhotoImage(img)
		tk.Button.__init__(self, relief=tk.FLAT, master=GUI.GamePanel, image=ph, bg=self.colorOrig, width=int(1.2*Hand_X), height=int(1.2*Hand_Y))
		self.GUI, self.card, self.image, self.selected = GUI, hero, ph, 0
		self.bind('<Button-1>', self.leftClick)
		self.bind('<Button-3>', self.rightClick)
		self.bind("<Enter>", self.crosshairEnter)
		self.bind("<Leave>", self.crosshairLeave)
		self.x, self.y, self.labels, self.zone = 0, 0, [], GUI.heroZones[hero.ID]
		self.cardInfo = type(hero)
		self.attack, self.health, self.armor = hero.attack, hero.health, hero.armor
		self.trigs = [type(trig) for trig in hero.trigsBoard]
		self.counts = 0
		for trig in hero.trigsBoard:
			if hasattr(trig, "counter"): self.counts += trig.counter
			
	def decideColorOrig(self, GUI, hero):
		if hero == GUI.subject: self.colorOrig = "white"
		elif hero == GUI.target: self.colorOrig = "cyan2"
		else: self.colorOrig = "green3" if hero.canAttack() else "red"
		
	def leftClick(self, event):
		if self.GUI.UI < 3 and self.GUI.UI > -1:
			self.GUI.resolveMove(self.card, self, "HeroonBoard")
			
	def rightClick(self, event):
		self.GUI.cancelSelection()
		
	def crosshairEnter(self, event):
		self.waiting = True
		thread = threading.Thread(target=self.wait2Display, daemon=True)
		thread.start()
		
	def crosshairLeave(self, event):
		self.waiting = False
		try: self.GUI.lbl_CardStatus.destroy()
		except: pass
		
	def wait2Display(self):
		time.sleep(waitTime4Info)
		if self.waiting:
			try: self.GUI.lbl_CardStatus.destroy()
			except: pass
			self.GUI.lbl_CardStatus = tk.Label(self.GUI.GamePanel, text=self.card.cardStatus(), bg="SteelBlue1", font=("Yahei", 12, "bold"), anchor='w', justify="left")
			self.GUI.lbl_CardStatus.place(relx=infoDispXPos, rely=0.5, anchor='c')
			self.GUI.displayCard(self.card)
			
	def tempLeftClick(self, event): #For Shadowverse
		self.GUI.select = self.card
		self.var.set(1)
		
	def plot(self, x=11, y=11):
		self.x, self.y, self.labels = x, y, []
		self.place(x=x, y=y, anchor='c')
		if self.card.attack > 0: CardLabel(btn=self, text=str(self.card.attack)).plot(x=x-0.39*CARD_X, y=y+0.3*CARD_Y)
		if self.card.armor > 0: CardLabel(btn=self, text=str(self.card.armor)).plot(x=x+0.39*CARD_X, y=y+0.1*CARD_Y)
		healthColor = "black" if self.card.health >= self.card.health_max else "red"
		CardLabel(btn=self, text=str(self.card.health), fg=healthColor).plot(x=x+0.39*CARD_X, y=y+0.3*CARD_Y)
		if self.card.trigsBoard:
			string = ""
			for trig in self.card.trigsBoard:
				if hasattr(trig, "counter"): string += "%d "%trig.counter
			CardLabel(btn=self, text=' %s'%string, bg="yellow").plot(x=x, y=y+0.45*CARD_Y)
		self.zone.btnsDrawn[0] = self
		
	def move2(self, x, y):
		xOffset, yOffset = x - self.x, y - self.y
		self.x, self.y = x, y
		self.place(x=x, y=y, anchor='c')
		for label in self.labels: label.moveby(xOffset, yOffset)
		
	def remove(self):
		for label in self.labels: label.destroy()
		self.destroy()
		try: self.zone.btnsDrawn[0] = None
		except: pass
		
	def represents(self, hero):
		if not isinstance(hero, self.cardInfo) or hero.attack != self.attack or hero.health != self.health or hero.armor != self.armor: return False
		counts = 0
		for trig in hero.trigsBoard:
			if hasattr(trig, "counter"): counts += trig.counter
		return self.trigs == [type(trig) for trig in hero.trigsBoard] and self.counts == counts
		
class HeroPowerButton(tk.Button): #For Hero Powers that are on board
	def __init__(self, GUI, power):
		self.decideColorOrig(GUI, power)
		self.waiting = False
		img = PIL.Image.open(findPicFilepath(power)).resize((PowerImgSize, PowerImgSize))
		ph = PIL.ImageTk.PhotoImage(img)
		tk.Button.__init__(self, relief=tk.FLAT, master=GUI.GamePanel, image=ph, bg=self.colorOrig, width=PowerIconSize, height=PowerIconSize)
		self.GUI, self.card, self.image, self.selected = GUI, power, ph, 0
		self.bind('<Button-1>', self.leftClick)
		self.bind('<Button-3>', self.rightClick)
		self.bind("<Enter>", self.crosshairEnter)
		self.bind("<Leave>", self.crosshairLeave)
		self.x, self.y, self.labels, self.zone = 0, 0, [], GUI.heroZones[power.ID]
		#Info bookkeeping
		self.cardInfo = type(power)
		self.mana = power.mana
		self.trigs = [type(trig) for trig in power.trigsBoard]
		self.counts = 0
		for trig in power.trigsBoard:
			if hasattr(trig, "counter"): self.counts += trig.counter
			
	def decideColorOrig(self, GUI, power):
		self.colorOrig = "green3" if power.ID == GUI.Game.turn and power.available() and GUI.Game.Manas.affordable(power) else "red"
		
	def leftClick(self, event):
		if self.GUI.UI < 3 and self.GUI.UI > -1:
			if self.card.ID == self.GUI.Game.turn and self.GUI.Game.Manas.affordable(self.card) and self.card.available():
				self.GUI.resolveMove(self.card, self, "Power")
			else:
				self.GUI.printInfo("Hero Power can't be selected")
				self.GUI.cancelSelection()
				self.card.STATUSPRINT()
				self.GUI.displayCard(self.card)
				
	def rightClick(self, event):
		self.GUI.cancelSelection()
		
	def crosshairEnter(self, event):
		self.waiting = True
		thread = threading.Thread(target=self.wait2Display, daemon=True)
		thread.start()
		
	def crosshairLeave(self, event):
		self.waiting = False
		try: self.GUI.lbl_CardStatus.destroy()
		except: pass
		
	def wait2Display(self):
		time.sleep(waitTime4Info)
		if self.waiting:
			try: self.GUI.lbl_CardStatus.destroy()
			except: pass
			self.GUI.lbl_CardStatus = tk.Label(self.GUI.GamePanel, text=self.card.cardStatus(), bg="SteelBlue1", font=("Yahei", 12, "bold"), anchor='w', justify="left")
			self.GUI.lbl_CardStatus.place(relx=infoDispXPos, rely=0.5, anchor='c')
			self.GUI.displayCard(self.card)
			
	def plot(self, x, y):
		self.x, self.y, self.labels = x, y, []
		self.place(x=x, y=y, anchor='c')
		if self.card.name == "Evolve":
			mana = self.card.Game.Counters.numEvolutionPoint[self.card.ID]
		else:
			mana = self.card.mana
		CardLabel(btn=self, text=str(mana)).plot(x=x, y=y-int(0.25*CARD_Y))
		self.zone.btnsDrawn[1] = self
		
	def remove(self):
		for label in self.labels: label.destroy()
		self.destroy()
		try: self.zone.btnsDrawn[1] = None
		except: pass
		
	def represents(self, power):
		if self.card.name == "Evolve":
			return False
		if not isinstance(power, self.cardInfo) or power.mana != self.mana: return False
		trigs = [type(trig) for trig in power.trigsBoard]
		counts = 0
		for trig in power.trigsBoard:
			if hasattr(trig, "counter"): counts += trig.counter
		return self.trigs == trigs and self.counts == counts
		
class WeaponButton(tk.Button): #休眠物和武器无论左右键都是取消选择，打印目前状态
	def __init__(self, GUI, weapon):
		self.decideColorOrig(GUI, weapon)
		self.waiting = False
		seq = weapon.seq
		text = {0: "1st", 1: "2nd", 2: "3rd"}[seq] if seq < 3 else "%dth"%(seq+1) + ' '
		for key, value in weapon.keyWords.items():
			if value > 0: text += key+'\n'
		img = PIL.Image.open(findPicFilepath(weapon)).resize((WeaponImgSize, WeaponImgSize))
		ph = PIL.ImageTk.PhotoImage(img)
		tk.Button.__init__(self, text=text, relief=tk.FLAT, image=ph, compound=tk.TOP, master=GUI.GamePanel, bg=self.colorOrig, width=WeaponIconWidth, height=WeaponIconHeight, font=("Yahei", 10, "bold"))
		self.GUI, self.card, self.image, self.selected = GUI, weapon, ph, 0
		self.bind("<Button-3>", self.rightClick)
		self.bind("<Enter>", self.crosshairEnter)
		self.bind("<Leave>", self.crosshairLeave)
		self.x, self.y, self.labels, self.zone = 0, 0, [], GUI.heroZones[weapon.ID]
		#Info bookkeeping
		self.cardInfo = type(weapon)
		self.attack, self.dura = weapon.attack, weapon.durability
		self.trigs = [type(trig) for trig in weapon.trigsBoard + weapon.deathrattles]
		self.counts = 0
		for trig in weapon.trigsBoard:
			if hasattr(trig, "counter"): self.counts += trig.counter
			
	def decideColorOrig(self, GUI, weapon):
		self.colorOrig = "blue" if not weapon.dead else "grey25"
		
	def rightClick(self, event):
		self.GUI.cancelSelection()
		
	def crosshairEnter(self, event):
		self.waiting = True
		thread = threading.Thread(target=self.wait2Display, daemon=True)
		thread.start()
		
	def crosshairLeave(self, event):
		self.waiting = False
		try: self.GUI.lbl_CardStatus.destroy()
		except: pass
		
	def wait2Display(self):
		time.sleep(waitTime4Info)
		if self.waiting:
			try: self.GUI.lbl_CardStatus.destroy()
			except: pass
			self.GUI.lbl_CardStatus = tk.Label(self.GUI.GamePanel, text=self.card.cardStatus(), bg="SteelBlue1", font=("Yahei", 12, "bold"), anchor='w', justify="left")
			self.GUI.lbl_CardStatus.place(relx=infoDispXPos, rely=0.5, anchor='c')
			self.GUI.displayCard(self.card)
			
	def plot(self, x, y):
		self.x, self.y, self.labels = x, y, []
		self.place(x=x, y=y, anchor='c')
		if self.card.trigsBoard or self.card.deathrattles:
			string = ""
			for trig in self.card.trigsBoard:
				if hasattr(trig, "counter"): string += "%d "%trig.counter
			CardLabel(btn=self, text=' %s'%string, bg="yellow", font=("Yahei", 6, )).plot(x=x, y=y+0.39*CARD_Y)
		attack, dura = self.card.attack, self.card.durability
		attColor = "green3" if attack > type(self.card).attack else "black"
		duraColor = "black" if dura >= type(self.card).durability else "red"
		CardLabel(btn=self, text=str(attack), fg=attColor).plot(x=x-0.42*CARD_X, y=y+0.39*CARD_Y)
		CardLabel(btn=self, text=str(dura), fg=duraColor).plot(x=x+0.42*CARD_X, y=y+0.39*CARD_Y)
		self.zone.btnsDrawn.append(self)
		
	def remove(self):
		for label in self.labels: label.destroy()
		self.destroy()
		try: self.zone.btnsDrawn.remove(self)
		except: pass
		
	def represents(self, weapon):
		if not isinstance(weapon, self.cardInfo) or weapon.attack != self.attack or weapon.durability != self.dura: return False
		trigs = [type(trig) for trig in weapon.trigsBoard + weapon.deathrattles]
		counts = 0
		for trig in weapon.trigsBoard:
			if hasattr(trig, "counter"): counts += trig.counter
		return self.trigs == trigs and self.counts == counts
		
class HeroZone: #Include heroes, weapons and powers
	def __init__(self, GUI, ID):
		self.GUI, self.ID, self.btnsDrawn = GUI, ID, []
		
	def draw(self):
		game = self.GUI.Game
		hero, power, weapon = game.heroes[self.ID], game.powers[self.ID], game.availableWeapon(self.ID)
		if not hasattr(self.GUI, "ID"): posBtns = [Hero1Pos, Power1Pos, Weapon1Pos] if self.ID == 1 else [Hero2Pos, Power2Pos, Weapon2Pos]
		else: posBtns = [OwnHeroPos, OwnPowerPos, OwnWeaponPos] if self.ID == self.GUI.ID else [EnemyHeroPos, EnemyPowerPos, EnemyWeaponPos]
		if self.btnsDrawn:
			#Check if the hero button still correctly show the hero
			if self.btnsDrawn[0] and self.btnsDrawn[0].represents(hero):
				heroBtn = self.btnsDrawn[0]
				heroBtn.card = hero
				heroBtn.decideColorOrig(self.GUI, hero)
				heroBtn.configure(bg=heroBtn.colorOrig)
			else:
				try: self.btnsDrawn[0].remove()
				except: pass
				HeroButton(self.GUI, hero).plot(posBtns[0][0], posBtns[0][1])
			#Check if the power button still correctly show the Hero Power
			if self.btnsDrawn[1] and self.btnsDrawn[1].represents(power):
				powerBtn = self.btnsDrawn[1]
				powerBtn.card = power
				powerBtn.decideColorOrig(self.GUI, power)
				powerBtn.configure(bg=powerBtn.colorOrig)
			else:
				try: self.btnsDrawn[1].remove()
				except: pass
				HeroPowerButton(self.GUI, power).plot(posBtns[1][0], posBtns[1][1])
			if weapon:
				if len(self.btnsDrawn) < 3 or not self.btnsDrawn[2].represents(weapon): #之前没有武器button或者武器button不再能正确显示数值
					try: self.btnsDrawn[2].remove()
					except: pass
					WeaponButton(self.GUI, weapon).plot(posBtns[2][0], posBtns[2][1])
			else:
				for i in reversed(range(2, len(self.btnsDrawn))):
					self.btnsDrawn[i].remove()
		else:
			self.btnsDrawn = [None, None]
			HeroButton(self.GUI, hero).plot(posBtns[0][0], posBtns[0][1])
			HeroPowerButton(self.GUI, power).plot(posBtns[1][0], posBtns[1][1])
			if weapon: WeaponButton(self.GUI, weapon).plot(posBtns[2][0], posBtns[2][1])
			
	#This function is EXCLUSIVE for single-player GUI replay
	def redraw(self):
		#Clear all the buttons drawn. 
		for btn in reversed(self.btnsDrawn): btn.remove()
		#Redraw the hero, power and weapon
		game = self.GUI.Game
		hero, power, weapon = game.heroes[self.ID], game.powers[self.ID], game.availableWeapon(self.ID)
		posBtns = [Hero1Pos, Power1Pos, Weapon1Pos] if self.ID == 1 else [Hero2Pos, Power2Pos, Weapon2Pos]
				#Redraw all the hands
		HeroButton(self.GUI, hero).plot(posBtns[0][0], posBtns[0][1])
		HeroPowerButton(self.GUI, power).plot(posBtns[1][0], posBtns[1][1])
		if weapon: WeaponButton(self.GUI, weapon).plot(posBtns[2][0], posBtns[2][1])
		
		
"""Secret, quests buttons and zone"""
class SecretButton(tk.Button): #休眠物和武器无论左右键都是取消选择，打印目前状态
	def __init__(self, GUI, card):
		self.decideColorOrig(GUI, card)
		self.waiting = False
		if not card.description.startswith("Secret:") or not hasattr(GUI, "ID") or seeEnemyHand or GUI.ID == card.ID:
			img = PIL.Image.open(findPicFilepath(card)).resize((SecretImgSize, SecretImgSize))
			ph = PIL.ImageTk.PhotoImage(img)
			tk.Button.__init__(self, relief=tk.FLAT, image=ph, compound=tk.TOP, master=GUI.GamePanel, bg=self.colorOrig, width=SecretIconSize_img, height=SecretIconSize_img, font=("Yahei", 10, "bold"))
			self.GUI, self.card, self.image, self.selected = GUI, card, ph, 0
			self.bind("<Button-3>", self.rightClick)
			self.bind("<Enter>", self.crosshairEnter)
			self.bind("<Leave>", self.crosshairLeave)
		else:
			tk.Button.__init__(self, relief=tk.FLAT, image=None, compound=tk.TOP, master=GUI.GamePanel, text="?", fg="white", bg=self.colorOrig, width=3, height=1, font=("Yahei", 20, "bold"))
			self.GUI, self.card, self.image, self.selected = GUI, card, None, 0
		self.x, self.y, self.labels, self.zone = 0, 0, [], GUI.secretZones[card.ID]
		self.cardInfo = type(card)
		self.counts = 0
		for trig in card.trigsBoard:
			if hasattr(trig, "counter"): self.counts += trig.counter
			
	def decideColorOrig(self, GUI, card):
		if card.description.startswith("Secret:") and card.ID != GUI.Game.turn:
			self.colorOrig = {"Paladin": "gold", "Hunter": "green3", "Rogue": "grey", "Mage": "magenta3"}[card.Class]
		elif card.description.startswith("Quest:"):
			self.colorOrig = "goldenrod1"
		elif card.description.startswith("Sidequest:"):
			self.colorOrig = "magenta2"
		else:
			self.colorOrig = "red"

	def rightClick(self, event):
		self.GUI.cancelSelection()
		
	def crosshairEnter(self, event):
		self.waiting = True
		thread = threading.Thread(target=self.wait2Display, daemon=True)
		thread.start()
		
	def crosshairLeave(self, event):
		self.waiting = False
		try: self.GUI.lbl_CardStatus.destroy()
		except: pass
		
	def wait2Display(self):
		time.sleep(waitTime4Info)
		if self.waiting:
			try: self.GUI.lbl_CardStatus.destroy()
			except: pass
			self.GUI.lbl_CardStatus = tk.Label(self.GUI.GamePanel, text=self.card.cardStatus(), bg="SteelBlue1", font=("Yahei", 12, "bold"), anchor='w', justify="left")
			self.GUI.lbl_CardStatus.place(relx=infoDispXPos, rely=0.5, anchor='c')
			self.GUI.displayCard(self.card)
			
	def plot(self, x, y):
		self.x, self.y, self.labels = x, y, []
		self.place(x=x, y=y, anchor='c')
		if "~~Quest" in self.card.index:
			string = ""
			for trig in self.card.trigsBoard:
				string += "%d "%trig.counter
			bgColor = "yellow" if self.card.description.startswith("Quest:") else "white"
			CardLabel(btn=self, text=' %s'%string, bg=bgColor).plot(x=x, y=y-0.28*CARD_Y)
		self.zone.btnsDrawn.append(self)
		
	def move2(self, x, y):
		xOffset, yOffset = x - self.x, y - self.y
		self.x, self.y = x, y
		self.place(x=x, y=y, anchor='c')
		for label in self.labels: label.moveby(xOffset, yOffset)
		
	def remove(self):
		for label in self.labels: label.destroy()
		self.destroy()
		try: self.zone.btnsDrawn.remove(self)
		except: pass
		
	def represents(self, card):
		if not hasattr(self.GUI, "ID") or seeEnemyHand or self.GUI.ID == card.ID:
			if not isinstance(card, self.cardInfo): return False
			counts = 0
			for trig in card.trigsBoard:
				if hasattr(trig, "counter"): counts += trig.counter
			return self.counts == counts
		else: return True
		
class SecretZone(tk.Frame):
	def __init__(self, GUI, ID):
		tk.Frame.__init__(self, master=GUI.GamePanel, bg=BoardColor, width=int(0.35*X), height=int(0.12*Y))
		self.GUI, self.ID, self.btnsDrawn = GUI, ID, []
		
	def draw(self):
		secretHD = self.GUI.Game.Secrets
		ownSecrets = secretHD.mainQuests[self.ID]+secretHD.sideQuests[self.ID]+secretHD.secrets[self.ID]
		ownID = 1 if not hasattr(self.GUI, "ID") else self.GUI.ID #1PGUI has virtual ID of 1
		y = int(Y - 0.25*Y) if self.ID == ownID else int(0.25*Y) #vertical position of the minions/dormants drawn
		posSecrets = [(int(0.33*X-(X/15)*i), y) for i in range(len(ownSecrets))]
		if self.btnsDrawn:
			btns, btnsKept, posEnds = [None] * len(ownSecrets), [], []
			for i, card in enumerate(ownSecrets):
				for j, btn in enumerate(self.btnsDrawn):
					if btn.card == card and btn.represents(card):
						btn = self.btnsDrawn.pop(j)
						btn.card = card
						btns[i] = btn
						btnsKept.append(btn) #已经有btn代表的牌会被录入btnsKept和posEnds
						posEnds.append(posSecrets[i])
						break
			for btn in reversed(self.btnsDrawn): btn.remove()
			self.GUI.moveBtnsAni(btnsKept, posEnds)
			for pos, btn, card in zip(posSecrets, btns, ownSecrets):
				if btn:
					self.btnsDrawn.append(btn)
					btn.decideColorOrig(self.GUI, card)
					btn.configure(bg=btn.colorOrig)
				else: SecretButton(self.GUI, card).plot(x=pos[0], y=pos[1])
		else:
			for pos, card in zip(posSecrets, ownSecrets):
				SecretButton(self.GUI, card).plot(x=pos[0], y=pos[1])
				
	#This function is EXCLUSIVE for single-player GUI replay
	def redraw(self):
		#Clear all the buttons drawn. 
		for btn in reversed(self.btnsDrawn): btn.remove()
		#Redraw the quests, sidequests and secrets
		secretHD = self.GUI.Game.Secrets
		ownSecrets = secretHD.mainQuests[self.ID]+secretHD.sideQuests[self.ID]+secretHD.secrets[self.ID]
		y = int(Y - 0.25*Y) if self.ID == 1 else int(0.25*Y) #vertical position of the minions/dormants drawn
		posSecrets = [(int(0.33*X-(X/15)*i), y) for i in range(len(ownSecrets))]
		for pos, card in zip(posSecrets, ownSecrets):
			SecretButton(self.GUI, card).plot(x=pos[0], y=pos[1])
			
"""Buttons that are don't belong to cards"""
class BoardButton(tk.Canvas):
	def __init__(self, GUI):
		tk.Canvas.__init__(self, master=GUI.GamePanel, bg=BoardColor, width=Board_X, height=Board_Y)
		self.GUI, self.selected, self.colorOrig, self.boardInfo = GUI, 0, BoardColor, GUI.boardID
		self.bind('<Button-1>', self.leftClick)   # bind left mouse click
		self.bind('<Button-3>', self.rightClick)   # bind right mouse click
		self.text = "Transfer Student--%s" if not CHN else "转校生--%s"% \
					{"1 Classic Ogrimmar": "Battlecry: Deal 2 damage" if not CHN else "战吼：造成2点伤害",
					"2 Classic Stormwind": "Divine Shield" if not CHN else "圣盾",
					"3 Classic Stranglethorn": "Stealth, Poisonous" if not CHN else "潜行，剧毒",
					"4 Classic Four Wind Valley": "Battlecry: Give a friendly minion +1/+2" if not CHN \
													else "战吼：使一个友方随从获得+1/+2",
					"20 Dalaran": "Battlecry: Add a Lackey to your hand" if not CHN else "战吼：将一张跟班牌置入你的手牌",
					"21 Uldum Desert": "Reborn" if not CHN else "复生",
					"22 Uldum Oasis": "Battlecry: Add a Uldum plague card to your hand" if not CHN \
										else "战吼：将一张奥丹姆灾祸法术牌置入你的手牌",
					"23 Dragons": "Battlecry: Discover a Dragon" if not CHN else "战吼：发现一张龙牌",
					"24 Outlands": "Dormant for 2 turns. When this awakens, deal 3 damage to 2 random enemy minions" if not CHN \
									else "休眠两回合。唤醒时，随机对两个敌方随从造成3点伤害",
					"25 Scholomance Academy": "Battlecry: Add a Dual class card to your hand" if not CHN \
												else "战吼：将一张双职业卡牌置入你的手牌",
					"26 Darkmoon Faire": "Corrupt: Gain +2/+2" if not CHN else "腐化：获得+2/+2",
					}[self.boardInfo]
		self.effectIDs = []
		
	def leftClick(self, event):
		if self.GUI.UI > -1 and self.GUI.UI < 3: #不在发现中和动画演示中才会响应
			self.GUI.resolveMove(None, self, "Board")
			
	def rightClick(self, event):
		self.GUI.cancelSelection()
		try: self.GUI.lbl_CardStatus.destroy()
		except: pass
		
	def plot(self):
		self.place(x=X/2, y=Y/2, anchor='c')
		self.x, self.y = X/2, Y/2
		
	def draw(self):
		while self.effectIDs:
			self.delete(self.effectIDs.pop())
		game, lines = self.GUI.Game, [self.text]
		for ID in range(1, 3):
			lines.append("Player %d has:"%ID if not CHN else "玩家%d有："%ID)
			for key, value in game.status[ID].items():
				if value > 0: lines.append("   %s:%d"%(key if not CHN else gameStatusDict[key], value))
			for obj in game.trigAuras[ID]: lines.append("   %s"%obj.text(CHN))
		lines.append("Temp Effects:" if not CHN else "临时效果")
		for obj in game.turnStartTrigger + game.turnEndTrigger:
			lines.append("   %s"%obj.text(CHN))
		textID = self.create_text(int(0.3*Board_X), Board_Y/2, text='\n'.join(lines), 
									fill="orange2", font=("Yahei", 14, ))
		self.effectIDs.append(textID)
		
	def remove(self):
		pass
		
	def connectBtns(self, btn1, btn2):
		if btn1 and btn2:
			x1, y1, x2, y2 = btn1.x, btn1.y, btn2.x, btn2.y
			x1 += Board_X/2 - self.x
			y1 += Board_Y/2 - self.y
			x2 += Board_X/2 - self.x
			y2 += Board_Y/2 - self.y
			return self.create_line(x1, y1, x2, y2, width=5, fill="blue")
		return None
		
class TurnEndButton(tk.Button):
	def __init__(self, GUI):
		tk.Button.__init__(self, master=GUI.GamePanel, text="Turn End", bg="green3", fg="white", width=10, height=2, font=("Yahei", 13, "bold"))
		self.GUI, self.colorOrig = GUI, "green3"
		self.bind("<Button-1>", self.respond)
		
	def respond(self, event):
		GUI = self.GUI
		if GUI.UI < 3 and GUI.UI > -1:
			GUI.resolveMove(None, self, "TurnEnds")
			if not hasattr(GUI, "ID"): #For 1P GUI
				if ReplayMovesThisTurn:
					s = pickleObj2Str(GUI.Game.moves)+"||"+pickleObj2Str(GUI.Game.fixedGuides)
					#GUI.Game.moves, GUI.Game.fixedGuides, GUI.Game.guides = [], [], []
					moves, gameGuides = s.split("||") #is a string
					moves, gameGuides = unpickleStr2Obj(moves), unpickleStr2Obj(gameGuides)
					for ID in range(1, 3):
						for btn in GUI.handZones[ID].btnsDrawn + GUI.boardZones[ID].btnsDrawn \
									+ GUI.heroZones[ID].btnsDrawn + GUI.secretZones[ID].btnsDrawn:
							btn.remove()
					GUI.manaZones[1].reset(GUI.gameBackup)
					GUI.manaZones[2].reset(GUI.gameBackup)
					GUI.Game = GUI.gameBackup
					#Need to clear all the buttons drawn. There seems to be no GUI.btnsDrawn
					GUI.canvas.configure(bg=BoardColor)
					GUI.update()
					lbl_SwitchTurn = tk.Label(GUI.GamePanel, text="Repeat Player's Moves This Turn", bg="red", fg="black", font=("Yahei", 22, "bold"))
					lbl_SwitchTurn.place(x=X/2, y=Y/2, anchor='c')
					var = tk.IntVar()
					GUI.window.after(800, var.set, 1)
					GUI.window.wait_variable(var)
					lbl_SwitchTurn.destroy()
					GUI.Game.evolvewithGuide(moves, gameGuides)
					GUI.gameBackup = GUI.Game.copyGame()[0]
				GUI.update()
			elif not hasattr(GUI, "sock"): #双人无服务器版本
				game = GUI.Game
				moves, gameGuides = game.moves, game.fixedGuides
				s = pickleObj2Str(moves)+"||"+pickleObj2Str(gameGuides)
				GUI.info4Opponent.config(text=s)
				GUI.window.clipboard_clear()
				GUI.window.clipboard_append(s)
				if GUI.showReminder.get():
					messagebox.showinfo(message="Info for opponent created in clipboard.\nSend before proceeding")
				for move in moves:
					GUI.printInfo(move)
				game.moves, game.fixedGuides, game.guides = [], [], []
				GUI.btnGenInfo.config(bg="grey")
				
	def plot(self, x, y):
		self.place(x=x, y=y, anchor="c")
		self.GUI.btnsDrawn.append(self)
		
		
class ManaZone(tk.Frame):
	def __init__(self, GUI, ID):
		tk.Frame.__init__(self, master=GUI.GamePanel, width=int(0.3*X), height=int(0.1*Y), bg=BoardColor)
		self.GUI, self.ID, self.curTurn, self.manaHD = GUI, ID, GUI.Game.turn, GUI.Game.Manas
		self.mana, self.upper, self.overloaded, self.locked = -1, -1, -1, -1
		self.manasDrawn = []
		
	def draw(self):
		ID = self.ID
		if not (self.curTurn == self.GUI.Game.turn and self.mana == self.manaHD.manas[ID] and self.upper == self.manaHD.manasUpper[ID] \
				and self.overloaded == self.manaHD.manasOverloaded[ID] and self.locked == self.manaHD.manasLocked[ID]):
			for widget in self.manasDrawn: widget.destroy()
			self.curTurn, self.mana, self.upper, self.overloaded, self.locked = self.GUI.Game.turn, self.manaHD.manas[ID], self.manaHD.manasUpper[ID], self.manaHD.manasOverloaded[ID], self.manaHD.manasLocked[ID]
			usable, locked = self.mana, self.locked
			unlocked = self.upper - locked
			empty = max(0, unlocked - usable)
			manastoDraw = locked + empty + usable
			lbl_Mana = tk.Label(self, text="%d/%d"%(self.mana, self.upper), bg="green3" if ID == self.curTurn else "red", fg="black", font=("Yahei", 15, "bold"))
			lbl_Mana.place(relx=0.07, rely=0.3, anchor='c')
			self.manasDrawn.append(lbl_Mana)
			i = 1
			while i < manastoDraw + 1:
				#pos = (0.69*X+(X/50)*i, Y - 0.26*Y) if ID == 1 else (0.69*X+(X/50)*i, 0.23*Y)
				if usable > unlocked:
					if i > self.upper: img = PIL.Image.open("Crops\\Mana.png")
					elif i > unlocked: img = PIL.Image.open("Crops\\LockedMana.png")
					else: img = PIL.Image.open("Crops\\Mana.png")
				else:
					if i > unlocked: img = PIL.Image.open("Crops\\LockedMana.png")
					elif i > usable: img = PIL.Image.open("Crops\\EmptyMana.png")
					else: img = PIL.Image.open("Crops\\Mana.png")
				img = img.resize((int(1.3*ManaXtlSize), int(1.3*ManaXtlSize)))
				ph = PIL.ImageTk.PhotoImage(img)
				mana = tk.Button(self, image=ph, bg="grey46", height=ManaXtlSize, width=ManaXtlSize)
				mana.image = ph
				mana.place(relx=0.1+i/13, rely=0.3, anchor='c')
				self.manasDrawn.append(mana)
				i += 1
			for i in range(1, self.overloaded+1):
				#pos = (0.69*X+(X/50)*i, Y - 0.23*Y) if ID == 1 else (0.69*X+(X/50)*i, 0.26*Y)
				img = PIL.Image.open("Crops\\LockedMana.png").resize((int(1.3*ManaXtlSize), int(1.3*ManaXtlSize)))
				ph = PIL.ImageTk.PhotoImage(img)
				mana = tk.Button(self, image=ph, bg="grey46", height=ManaXtlSize, width=ManaXtlSize)
				mana.image = ph
				mana.place(relx=0.1+i/13, rely=0.7, anchor='c')
				self.manasDrawn.append(mana)
				
	#Exclusively for single-player replay. It needs the new game for preparation
	def reset(self, game):
		self.curTurn, self.manaHD = game.turn, game.Manas
		self.mana, self.upper, self.overloaded, self.locked = -1, -1, -1, -1
		for widget in self.manasDrawn: widget.destroy()
		
		
class DeckZone(tk.Frame):
	def __init__(self, GUI, ID):
		tk.Frame.__init__(self, master=GUI.GamePanel, height=int(0.2*Y), bg='black')
		self.GUI, self.ID = GUI, ID
		self.x, self.y, self.btnsDrawn = 0, 0, []
		
	def plot(self):
		ID = self.GUI.ID if hasattr(self.GUI, "ID") else 1
		if self.ID == ID: x, y= int(0.94*X), int(0.93*Y)
		else: x, y= int(0.94*X), int(0.07*Y)
		self.x, self.y = x, y
		self.place(x=x, y=y, anchor='c')
		
	def draw(self):
		HD = self.GUI.Game.Hand_Deck
		if self.btnsDrawn:
			self.btnsDrawn[0]["text"] = "Hand: %d\nDeck: %d\nTurn: %d\nShadow: %d"%(len(HD.hands[self.ID]), len(HD.decks[self.ID]), self.GUI.Game.Counters.turns[self.ID] ,self.GUI.Game.Counters.shadows[self.ID])
			self.btnsDrawn[0].configure(bg="green3"if self.GUI.Game.turn == self.ID else "red")
		else:
			color = "green3"if self.GUI.Game.turn == self.ID else "red"
			text = "Hand: %d\n.\n.\nDeck: %d"%(len(HD.hands[self.ID]), len(HD.decks[self.ID]))
			lbl_HD = tk.Label(self.GUI.GamePanel, text=text, bg=color, fg="black", font=("Yahei", 16, "bold"))
			lbl_HD.place(x=self.x, y=self.y, anchor='c')
			self.btnsDrawn = [lbl_HD]
			