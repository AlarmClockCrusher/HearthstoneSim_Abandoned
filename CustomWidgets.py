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
			"24 Outlands", "25 Scholomance Academy",
			]
			
from tkinter import messagebox
import tkinter as tk
import PIL.Image, PIL.ImageTk
import pickle, inspect
import os


def pickleObj2Str(obj):
	s = str(pickle.dumps(obj, 0).decode())
	return s.replace("\n", "_._")
	
def unpickleStr2Obj(s):
	s = s.replace("_._", "\n")
	obj = pickle.loads(bytes(s.encode()))
	return obj
	
def fixedList(listObj):
	return listObj[0:len(listObj)]
	
def extractfrom(target, listObj):
	try: return listObj.pop(listObj.index(target))
	except: return None
	
def findPicFilepath(card):
	if card.type == "Permanent": #休眠的随从会主动查看自己携带的originalMinion的名字和index
		index = card.originalMinion.index
		if inspect.isclass(card.originalMinion):
			name = card.originalMinion.__name__
		else: #Instances don't have __name__
			name = type(card.originalMinion).__name__
		path = "Crops\\%s\\"%index.split('~')[0]
	else: #type == "Weapon", "Minion", "Spell", "Hero", "Power"
		index, name = card.index, type(card).__name__
		if card.type != "Hero" and card.type != "Power":
			path = "Crops\\%s\\"%index.split('~')[0]
		else: path = "Crops\\HerosandPowers\\"
			
	name = name.split("_")[0] if "Mutable" in name else name
	filepath = path+"%s.png"%name
	return filepath
	
def findPicFilepath_FullImg(card):
	if card.type == "Permanent": #休眠的随从会主动查看自己携带的originalMinion的名字和index
		index = card.originalMinion.index
		if inspect.isclass(card.originalMinion):
			name = card.originalMinion.__name__
		else: #Instances don't have __name__
			name = type(card.originalMinion).__name__
		path = "Images\\%s\\"%index.split('~')[0]
	else: #type == "Weapon", "Minion", "Spell", "Hero", "Power"
		index, name = card.index, type(card).__name__
		if card.type != "Hero" and card.type != "Power":
			path = "Images\\%s\\"%index.split('~')[0]
		else: path = "Images\\HerosandPowers\\"
		
	name = name.split("_")[0] if "Mutable" in name else name
	filepath = path+"%s.png"%name
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
		if enemyCanSee or not hasattr(GUI, "ID") or seeEnemyHand or GUI.ID == card.ID:
			self.decideColorOrig(GUI, card)
			img = PIL.Image.open(findPicFilepath(card)).resize((HandImgSize, HandImgSize))
			ph = PIL.ImageTk.PhotoImage(img)
			tk.Button.__init__(self, relief=tk.FLAT, image=ph, master=GUI.GamePanel, bg=self.colorOrig, width=HandIconWidth, height=HandIconHeight)
			self.GUI, self.card, self.selected, self.image = GUI, card, 0, ph
			self.x, self.y, self.labels, self.zone = 0, 0, [], GUI.handZones[card.ID]
			self.bind('<Button-1>', self.leftClick)   # bind left mouse click
			self.bind('<Button-3>', self.rightClick)   # bind right mouse click
			#Info bookkeeping
			self.cardInfo, self.mana = type(card), card.mana
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
				if (card.type == "Spell" and card.available()) or (card.type == "Minion" and game.space(card.ID) > 0) or card.type == "Weapon" or card.type == "Hero":
					self.colorOrig = "blue" if card.evanescent else ("yellow" if card.effectViable else "green3")
		else: self.colorOrig = "grey46" #Only is grey when it's opponent's card in 2PGUI in "Don't show opponent cards" mode
		
	def leftClick(self, event):
		if self.GUI.UI < 3 and self.GUI.UI > -1: #只有不在发现或动画演示中才会响应
			card, ID, game = self.card, self.card.ID, self.GUI.Game
			if ID == game.turn and game.Manas.affordable(card) and ((card.type == "Spell" and card.available()) or (card.type == "Minion" and game.space(ID) > 0) or card.type == "Weapon" or card.type == "Hero"):
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
		self.card.STATUSPRINT()
		self.GUI.displayCard(self.card)
		
	def plot(self, x, y):
		card = self.card
		self.x, self.y, self.labels = x, y, []
		self.place(x=x, y=y, anchor='c')
		if not hasattr(self.GUI, "ID") or seeEnemyHand or self.GUI.ID == card.ID:
			CardLabel(btn=self, text=self.GUI.wrapText(card.name), fg="black").plot(x=x, y=y-CARD_Y/2)
			CardLabel(btn=self, text=str(card.mana), fg="black").plot(x=x-0.39*CARD_X, y=y-0.22*CARD_Y)
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
			CardLabel(btn=self, text=str(card.mana), fg="black").plot(x=self.x-0.39*CARD_X, y=self.y-0.22*CARD_Y)
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
		if not hasattr(self.GUI, "ID") or seeEnemyHand or self.GUI.ID == card.ID:
			if not isinstance(card, self.cardInfo) or self.mana != card.mana: return False
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
			#如果需要让最后一个button等待，总btnsKept不为空且其中最后一个btn就是最后一张手牌时
			i = min(len(ownHand)-1, cardMoving2)
			if cardMoving2 > -2 and btnsKept and btnsKept[i].card == ownHand[i]:
				lastBtn, lastPos = btnsKept.pop(i), posEnds.pop(i)
				self.GUI.moveBtnsAni(btnsKept, posEnds, steps=steps)
				self.GUI.moveBtnsAni(lastBtn, lastPos, steps=steps)
			else: self.GUI.moveBtnsAni(btnsKept, posEnds, steps=steps) #其他情况下最后一个btn不等待，直接与其他的handBtn一同移动
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
		tk.Button.__init__(self, relief=tk.FLAT, master=GUI.GamePanel, image=ph, bg="green", width=2.5*CARD_X, height=int(2.3*CARD_Y))
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
		
	def hide(self): #因为DiscoverCardOption是HandButton上面定义的，不用再次定replot
		self.place_forget()
		for label in self.labels: label.place_forget()
		
		
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
		seq = minion.sequence
		text = {0: "1st", 1: "2nd", 2: "3rd"}[seq] if seq < 3 else "%dth"%(seq+1) + ' '
		for key, value in minion.keyWords.items():
			if value > 0: text += key+'\n'
		img = PIL.Image.open(findPicFilepath(minion)).resize((MinionImgSize, MinionImgSize))
		ph = PIL.ImageTk.PhotoImage(img)
		tk.Button.__init__(self, text=text, image=ph, relief=tk.FLAT, compound=tk.TOP, anchor ='n', master=GUI.GamePanel, bg=self.colorOrig, width=CARD_X, height=CARD_Y, font=("Yahei", 10, "bold"))
		self.GUI, self.card, self.image, self.selected = GUI, minion, ph, 0
		self.bind('<Button-1>', self.leftClick)
		self.bind('<Button-3>', self.rightClick)
		self.x, self.y, self.labels, self.zone = 0, 0, [], GUI.boardZones[minion.ID]
		#Info bookkeeping
		self.cardInfo = type(minion)
		if minion.type == "Minion":
			self.attack, self.health, self.keyWords = minion.attack, minion.health, ''
			for key, value in minion.keyWords.items():
				if value > 0: self.keyWords += key
		self.trigs = [type(trig) for trig in minion.trigsBoard + (minion.deathrattles if minion.type == "Minion" else [])]
		self.counts = 0
		for trig in minion.trigsBoard:
			if hasattr(trig, "counter"): self.counts += trig.counter
			
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
			else: #card.type == "Permanent"
				self.GUI.cancelSelection()
				
	def rightClick(self, event):
		self.GUI.cancelSelection()
		self.card.STATUSPRINT()
		self.GUI.displayCard(self.card)
		print("This button of %s is in zone's btnsDrawn"%self.card.name, self in self.zone.btnsDrawn)
		print("This boardZones' btnsDrawn", self.GUI.boardZones[1].btnsDrawn, self.GUI.boardZones[2].btnsDrawn)
		
	def plot(self, x, y):
		self.x, self.y, self.labels = x, y, []
		self.place(x=x, y=y, anchor='c')
		trigsBoard = [trig for trig in self.card.trigsBoard if not hasattr(trig, "hide")]
		if trigsBoard or (self.card.type == "Minion" and self.card.deathrattles):
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
		if minion.type == "Minion": #Only need to check minion for now. Permanents don't have keyWords
			attack, health, keyWords = minion.attack, minion.health, ''
			for key, value in minion.keyWords.items():
				if value > 0: keyWords += key
			if self.attack != attack or self.health != health or self.keyWords != keyWords: return False
		trigs = [type(trig) for trig in minion.trigsBoard + (minion.deathrattles if minion.type == "Minion" else [])]
		counts = 0
		for trig in minion.trigsBoard:
			if hasattr(trig, "counter"): counts += trig.counter
		return self.trigs == trigs and self.counts == counts
		
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
					seq = minion.sequence
					text = {0: "1st", 1: "2nd", 2: "3rd"}[seq] if seq < 3 else "%dth"%(seq+1) + ' '
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
		img = PIL.Image.open(findPicFilepath(hero)).resize((HeroIconSize, HeroIconSize))
		ph = PIL.ImageTk.PhotoImage(img)
		tk.Button.__init__(self, relief=tk.FLAT, master=GUI.GamePanel, image=ph, bg=self.colorOrig, width=int(1.2*Hand_X), height=int(1.2*Hand_Y))
		self.GUI, self.card, self.image, self.selected = GUI, hero, ph, 0
		self.bind('<Button-1>', self.leftClick)
		self.bind('<Button-3>', self.rightClick)
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
		self.card.STATUSPRINT()
		self.GUI.displayCard(self.card)
		
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
		
	def represents(self, hero):
		if not isinstance(hero, self.cardInfo) or hero.attack != self.attack or hero.health != self.health or hero.armor != self.armor: return False
		counts = 0
		for trig in hero.trigsBoard:
			if hasattr(trig, "counter"): counts += trig.counter
		return self.trigs == [type(trig) for trig in hero.trigsBoard] and self.counts == counts
		
class WeaponButton(tk.Button): #休眠物和武器无论左右键都是取消选择，打印目前状态
	def __init__(self, GUI, weapon):
		self.decideColorOrig(GUI, weapon)
		seq = weapon.sequence
		text = {0: "1st", 1: "2nd", 2: "3rd"}[seq] if seq < 3 else "%dth"%(seq+1) + ' '
		for key, value in weapon.keyWords.items():
			if value > 0: text += key+'\n'
		img = PIL.Image.open(findPicFilepath(weapon)).resize((WeaponImgSize, WeaponImgSize))
		ph = PIL.ImageTk.PhotoImage(img)
		tk.Button.__init__(self, text=text, relief=tk.FLAT, image=ph, compound=tk.TOP, master=GUI.GamePanel, bg=self.colorOrig, width=WeaponIconWidth, height=WeaponIconHeight, font=("Yahei", 10, "bold"))
		self.GUI, self.card, self.image, self.selected = GUI, weapon, ph, 0
		self.bind("<Button-3>", self.rightClick)
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
		self.card.STATUSPRINT()
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
		
class HeroPowerButton(tk.Button): #For Hero Powers that are on board
	def __init__(self, GUI, power):
		self.decideColorOrig(GUI, power)
		img = PIL.Image.open(findPicFilepath(power)).resize((PowerImgSize, PowerImgSize))
		ph = PIL.ImageTk.PhotoImage(img)
		tk.Button.__init__(self, relief=tk.FLAT, master=GUI.GamePanel, image=ph, bg=self.colorOrig, width=PowerIconSize, height=PowerIconSize)
		self.GUI, self.card, self.image, self.selected = GUI, power, ph, 0
		self.bind('<Button-1>', self.leftClick)
		self.bind('<Button-3>', self.rightClick)
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
		self.card.STATUSPRINT()
		self.GUI.displayCard(self.card)
		
	def plot(self, x, y):
		self.x, self.y, self.labels = x, y, []
		self.place(x=x, y=y, anchor='c')
		CardLabel(btn=self, text=str(self.card.mana)).plot(x=x, y=y-int(0.25*CARD_Y))
		self.zone.btnsDrawn.append(self)
		
	def remove(self):
		for label in self.labels: label.destroy()
		self.destroy()
		try: self.zone.btnsDrawn.remove(self)
		except: pass
		
	def represents(self, power):
		if not isinstance(power, self.cardInfo) or power.mana != self.mana: return False
		trigs = [type(trig) for trig in power.trigsBoard]
		counts = 0
		for trig in power.trigsBoard:
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
		heroBtn, powerBtn, weaponBtn = None, None, None
		if self.btnsDrawn:
			if self.btnsDrawn[0].represents(hero):
				heroBtn = self.btnsDrawn.pop(0)
				heroBtn.card = hero
			for i, btn in enumerate(self.btnsDrawn):
				if btn.represents(power):
					powerBtn = self.btnsDrawn.pop(i)
					powerBtn.card = power
					break
			if weapon:
				for i, btn in enumerate(self.btnsDrawn):
					if btn.represents(weapon):
						weaponBtn = self.btnsDrawn.pop(i)
						weaponBtn.card = weapon
						break
			for btn in reversed(self.btnsDrawn): btn.remove()
			if heroBtn:
				self.btnsDrawn.append(heroBtn)
				heroBtn.decideColorOrig(self.GUI, hero)
				heroBtn.configure(bg=heroBtn.colorOrig)
			else: HeroButton(self.GUI, hero).plot(posBtns[0][0], posBtns[0][1])
			if powerBtn:
				self.btnsDrawn.append(powerBtn)
				powerBtn.decideColorOrig(self.GUI, power)
				powerBtn.configure(bg=powerBtn.colorOrig)
			else: HeroPowerButton(self.GUI, power).plot(posBtns[1][0], posBtns[1][1])
			if weapon:
				if weaponBtn: #可能在之前是没有画这个button的
					self.btnsDrawn.append(weaponBtn)
					weaponBtn.decideColorOrig(self.GUI, weapon)
					weaponBtn.configure(bg=weaponBtn.colorOrig)
				else: WeaponButton(self.GUI, weapon).plot(posBtns[2][0], posBtns[2][1])
		else:
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
		if "~~Secret" not in card.index or not hasattr(GUI, "ID") or seeEnemyHand or GUI.ID == card.ID:
			img = PIL.Image.open(findPicFilepath(card)).resize((SecretImgSize, SecretImgSize))
			ph = PIL.ImageTk.PhotoImage(img)
			tk.Button.__init__(self, relief=tk.FLAT, image=ph, compound=tk.TOP, master=GUI.GamePanel, bg=self.colorOrig, width=SecretIconSize_img, height=SecretIconSize_img, font=("Yahei", 10, "bold"))
			self.GUI, self.card, self.image, self.selected = GUI, card, ph, 0
			self.bind("<Button-3>", self.rightClick)
		else:
			tk.Button.__init__(self, relief=tk.FLAT, image=None, compound=tk.TOP, master=GUI.GamePanel, text="?", fg="white", bg=self.colorOrig, width=3, height=1, font=("Yahei", 20, "bold"))
			self.GUI, self.card, self.image, self.selected = GUI, card, None, 0
		self.x, self.y, self.labels, self.zone = 0, 0, [], GUI.secretZones[card.ID]
		self.cardInfo = type(card)
		self.counts = 0
		for trig in card.trigsBoard:
			if hasattr(trig, "counter"): self.counts += trig.counter
			
	def decideColorOrig(self, GUI, card):
		self.colorOrig = "red" if not("~~Secret" in card.index and card.ID == GUI.Game.turn) \
						else {"Paladin": "yellow", "Hunter": "green3", "Rogue": "grey", "Mage": "purple3"}[card.Class]
						
	def rightClick(self, event):
		self.GUI.cancelSelection()
		self.card.STATUSPRINT()
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
		self.text = self.boardInfo + "\nTransfer Student Effect:\n" \
				+ {"1 Classic Ogrimmar": "Battlecry: Deal 2 damage",
				"2 Classic Stormwind": "Divine Shield",
				"3 Classic Stranglethorn": "Stealth, Poisonous",
				"4 Classic Four Wind Valley": "Battlecry: Give a friendly minion +1/+2",
				"20 Dalaran": "Battlecry: Add a Lackey to your hand",
				"21 Uldum Desert": "Reborn",
				"22 Uldum Oasis": "Battlecry: Add a Uldum plague card to your hand",
				"23 Dragons": "Battlecry: Discover a Dragon",
				"24 Outlands": "Dormant for 2 turns. When this awakens, deal 2 damage to 2 random enemy minions",
				"25 Scholomance Academy": "Add a Dual class card to your hand",
				}[self.boardInfo]
		self.create_text(Board_X/2, Board_Y/2, text=self.text, fill="orange2", font=("Yahei", 14, ))
		
	def leftClick(self, event):
		if self.GUI.UI > -1 and self.GUI.UI < 3: #不在发现中和动画演示中才会响应
			self.GUI.resolveMove(None, self, "Board")
			
	def rightClick(self, event):
		self.GUI.cancelSelection()
		
	def plot(self):
		self.place(x=X/2, y=Y/2, anchor='c')
		self.x, self.y = X/2, Y/2
		
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
			if not hasattr(GUI, "ID"): #For 1P GUI
				GUI.resolveMove(None, self, "TurnEnds")
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
			else:
				GUI.resolveMove(None, self, "TurnEnds")
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
				mana.place(relx=0.08+i/13, rely=0.3, anchor='c')
				self.manasDrawn.append(mana)
				i += 1
			for i in range(1, self.overloaded+1):
				#pos = (0.69*X+(X/50)*i, Y - 0.23*Y) if ID == 1 else (0.69*X+(X/50)*i, 0.26*Y)
				img = PIL.Image.open("Crops\\LockedMana.png").resize((int(1.3*ManaXtlSize), int(1.3*ManaXtlSize)))
				ph = PIL.ImageTk.PhotoImage(img)
				mana = tk.Button(self, image=ph, bg="grey46", height=ManaXtlSize, width=ManaXtlSize)
				mana.image = ph
				mana.place(relx=0.08+i/13, rely=0.7, anchor='c')
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
			self.btnsDrawn[0]["text"] = "Hand: %d\n.\n.\nDeck: %d"%(len(HD.hands[self.ID]), len(HD.decks[self.ID]))
			self.btnsDrawn[0].configure(bg="green3"if self.GUI.Game.turn == self.ID else "red")
		else:
			color = "green3"if self.GUI.Game.turn == self.ID else "red"
			text = "Hand: %d\n.\n.\nDeck: %d"%(len(HD.hands[self.ID]), len(HD.decks[self.ID]))
			lbl_HD = tk.Label(self.GUI.GamePanel, text=text, bg=color, fg="black", font=("Yahei", 16, "bold"))
			lbl_HD.place(x=self.x, y=self.y, anchor='c')
			self.btnsDrawn = [lbl_HD]
			