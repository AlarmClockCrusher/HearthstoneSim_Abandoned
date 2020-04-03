import tkinter as tk
from Game import *
from Basic import ClassDict
from CardPools import cardPool, MinionsofCost, MinionswithRace, RNGPools
from Code2CardList import *
import PIL.Image
import PIL.ImageTk
import os
import inspect

def fixedList(listObject):
	return listObject[0:len(listObject)]
	
def extractfrom(target, listObject):
	temp = None
	for i in range(len(listObject)):
		if listObject[i] == target:
			temp = listObject.pop(i)
			break
	return temp
	
def findPicFilepath(card):
	if card.cardType == "Permanent": #休眠的随从会主动查看自己携带的originalMinion的名字和index
		index = card.originalMinion.index
		if inspect.isclass(card.originalMinion):
			name = card.originalMinion.__name__
		else: #Instances don't have __name__
			name = type(card.originalMinion).__name__
		path = "Crops\\%s\\"%index.split('~')[0]
	else: #cardType == "Weapon", "Minion", "Spell", "Hero", "Hero Power"
		index, name = card.index, type(card).__name__
		if card.cardType != "Hero" and card.cardType != "Hero Power":
			path = "Crops\\%s\\"%index.split('~')[0]
		else:
			path = "Crops\\HerosandPowers\\"
			
	name = name.split("_")[0] if "Mutable" in name else name
	filepath = path+"%s.png"%name
	return filepath
	
X, Y = 1000, 750
card_x, card_y = int(0.00818*X), int(0.00625*Y) #XY为（1100， 800）时对应（9，5）
CARD_X, CARD_Y = int(0.073*X), int(0.15*Y) #XY为（1100，800）时对应80, 120#有Image的按钮的大小由这个来确定
SecretIconSize = int(0.08125*Y) #Y为800时对应65
HeroIconSize = int(0.1*Y) #XY为（1100，800）时对应80，80
Hand_X, Hand_Y = int(0.064*X), int(0.0875*Y) #XY为（1100，800）时对应70，100
Board_X, Board_Y = int(0.118*X), int(0.02375*Y)
boardColor = "peach puff"
Hero1Pos = (0.51*X, Y-0.24*Y)
Hero2Pos = (0.51*X, 0.24*Y)
Weapon1Pos = (0.42*X, Y-0.24*Y)
Weapon2Pos = (0.42*X, 0.24*Y)
HeroPower1Pos = (0.6*X, Y-0.24*Y)
HeroPower2Pos = (0.6*X, 0.24*Y)

HeroList = ["Demon Hunter", "Druid", "Hunter", "Mage", "Paladin", "Priest", "Rogue", "Shaman", "Warlock", "Warrior"]


class CardLabel(tk.Label):
	def plot(self, x=11, y=11, anchor='c'):
		self.x, self.y, self.anchor = x, y, anchor
		self.place(x=x, y=y, anchor=anchor)
		
	def replot(self):
		self.place(x=self.x, y=self.y, anchor=self.anchor)
		
class HandButton(tk.Button): #Cards that are in hand. 目前而言只有一张牌是自己可以打出的牌的时候点击是有响应的。
	def leftClick(self, event):
		#一张牌目前是可以打出的
		card, ID = self.card, self.card.ID
		if ID == self.Game.turn and self.Game.ManaHandler.costAffordable(card) and ((card.cardType == "Spell" and card.available()) or (card.cardType == "Minion" and self.Game.spaceonBoard(ID) > 0) or card.cardType == "Weapon" or card.cardType == "Hero"):
			self.selected = 1 - self.selected #在选中一张牌后再次选择它，会取消所有选择
			if self.selected == 1:
				self.configure(bg="white")
				selectedSubject = card.cardType+"inHand"
				self.GUI.resolveMove(card, self, selectedSubject) #把一张牌，这个牌的按钮和这个牌的信息传入resolveMove
			else:
				self.GUI.cancelSelection()
				
		else:
			self.selected = 0
			self.configure(bg="red")
			self.GUI.cancelSelection()
			
	def rightClick(self, event):
		self.GUI.cancelSelection()
		self.card.STATUSPRINT()
		
	def plot(self, x=11, y=11, anchor='c'):
		self.x, self.y, self.anchor = x, y, anchor
		self.labels = []
		self.place(x=x, y=y, anchor=anchor)
		cardName, mana = self.card.name, self.card.mana
		lbl_name = CardLabel(text=self.GUI.wrapText(cardName), bg="white", fg="black", font=("Yahei", 11, "bold"))
		lbl_name.plot(x=x, y=y-CARD_Y/2, anchor='c')
		self.labels.append(lbl_name)
		lbl_mana = CardLabel(text=str(mana), bg="white", fg="black", font=("Yahei", 11, "bold"))
		lbl_mana.plot(x=x-0.39*CARD_X, y=y-0.22*CARD_Y, anchor='c')
		self.labels.append(lbl_mana)
		
		if self.card.cardType == "Minion":
			attack, attack_Enchant, health, health_Enchant, health_upper = self.card.attack, self.card.attack_Enchant, self.card.health, self.card.health_Enchant, self.card.health_upper
			attColor = "green" if attack_Enchant > self.card.attack_0 else "black"
			lbl_attack = CardLabel(text=str(attack), bg="white", fg=attColor, font=("Yahei", 11, "bold"))
			lbl_attack.plot(x=x-0.39*CARD_X, y=y+0.39*CARD_Y, anchor='c')
			self.labels.append(lbl_attack)
			if health >= health_upper:
				healthColor = "black" if health_Enchant <= self.card.health_0 else "green"
			else:
				healthColor = "red"
			lbl_health = CardLabel(text=str(health), bg="white", fg=healthColor, font=("Yahei", 11, "bold"))
			lbl_health.plot(x=x+0.39*CARD_X, y=y+0.39*CARD_Y, anchor='c')
			self.labels.append(lbl_health)
			text = ""
			for key, value in self.card.keyWords.items():
				if value > 1:
					text += "%s:%d\n"%(key, value)
				elif value == 1:
					text += key+'\n'
			if self.card.race != "":
				if ',' not in self.card.race:
					text += self.card.race
				else:
					text += "All"
			self.configure(text=text)
		elif self.card.cardType == "Weapon":
			attack, durability = self.card.attack, self.card.durability
			attColor = "green" if attack > type(self.card).attack else "black"
			lbl_attack = CardLabel(text=str(attack), bg="white", fg=attColor, font=("Yahei", 11, "bold"))
			lbl_attack.plot(x=x-0.39*CARD_X, y=y+0.39*CARD_Y, anchor='c')
			self.labels.append(lbl_attack)
			durabilityColor = "green" if durability > type(self.card).durability else "black"
			lbl_durability = CardLabel(text=str(durability), bg="white", fg=durabilityColor, font=("Yahei", 11, "bold"))
			lbl_durability.plot(x=x+0.39*CARD_X, y=y+0.39*CARD_Y, anchor='c')
			self.labels.append(lbl_durability)
			text = ""
			for key, value in self.card.keyWords.items():
				if value > 0:
					text += key+'\n'
			self.configure(text=text)
			
	def replot(self): #After the button is hidden by place_forget, use this to show the button again
		self.place(x=self.x, y=self.y, anchor=self.anchor)
		for label in self.labels:
			label.replot()
			
	def remove(self):
		self.destroy()
		for label in self.labels:
			label.destroy()
			
			
class DiscoverCardButton(HandButton):
	def leftClick(self, event):
		discoverOptions = []
		for button in self.GUI.buttonsDrawn:
			if type(button) == DiscoverOptionButton or type(button) == DiscoverCardButton:
				discoverOptions.append(button)
		for button in discoverOptions:
			if button == self:
				self.GUI.discover = self.card
				self.configure(bg="white")
				self.selected = 1
			else:
				button.configure(bg="green")
				button.selected = 0
				
	def rightClick(self, event):
		self.card.STATUSPRINT()
		
	#因为DiscoverCardOption是HandButton上面定义的，不用再次定replot
	def hide(self):
		self.place_forget()
		for label in self.labels:
			label.place_forget()
			
class DiscoverOptionButton(tk.Button):
	def plot(self, x=11, y=11, anchor='c'):
		self.x, self.y, self.anchor = x, y, anchor
		self.labels = []
		self.place(x=x, y=y, anchor=anchor)
		optionName, description = self.option.name, self.option.description
		lbl_name = CardLabel(text=self.GUI.wrapText(optionName), bg="white", fg="black", font=("Yahei", 11, "bold"))
		lbl_name.plot(x=x, y=y-CARD_Y/2, anchor='c')
		self.labels.append(lbl_name)
		#lbl_description = CardLabel(text=self.GUI.wrapText(description), bg="white", fg="black", font=("Yahei", 11, "bold"))
		#lbl_description.plot(x=x, y=y+0.2*CARD_Y, anchor='c')
		#self.labels.append(lbl_description)
		
	def respond(self):
		discoverOptions = []
		for button in self.GUI.buttonsDrawn:
			if type(button) == DiscoverOptionButton or type(button) == DiscoverCardButton:
				discoverOptions.append(button)
		for button in discoverOptions:
			if button == self:
				self.GUI.discover = self.option
				self.configure(bg="white")
				self.selected = 1
			else:
				button.configure(bg="green")
				button.selected = 0
				
	def hide(self):
		self.place_forget()
		for label in self.labels:
			label.place_forget()
			
	#DiscoverOption由于是tk.Button上面直接定义的类，所以要再次定义replot函数
	def replot(self): #After the button is hidden by place_forget, use this to show the button again
		self.place(x=self.x, y=self.y, anchor=self.anchor)
		for label in self.labels:
			label.replot()
			
	def remove(self):
		self.destroy()
		for label in self.labels:
			label.destroy()
			
class DiscoverHideButton(tk.Button):
	def respond(self):
		self.selected = 1 - self.selected
		if self.selected == 1: #When hide is positive, the discover option buttons are destroyed
			self.configure(bg="red")
			for button in self.GUI.buttonsDrawn:
				if type(button) == DiscoverOptionButton or type(button) == DiscoverCardButton:
					button.hide()
		else:
			self.configure(bg="green")
			for button in self.GUI.buttonsDrawn:
				if type(button) == DiscoverOptionButton or type(button) == DiscoverCardButton:
					button.replot()
					
					
class ChooseOneButton(tk.Button):
	def plot(self, x=11, y=11, anchor='c'):
		self.x, self.y, self.anchor = x, y, anchor
		self.labels = []
		self.place(x=x, y=y, anchor=anchor)
		optionName, description = self.option.name, self.option.description
		lbl_name = CardLabel(text=self.GUI.wrapText(optionName), bg="white", fg="black", font=("Yahei", 11, "bold"))
		lbl_name.plot(x=x, y=y-0.4*CARD_Y, anchor='c')
		self.labels.append(lbl_name)
		#lbl_description = CardLabel(text=self.GUI.wrapText(description), bg="white", fg="black", font=("Yahei", 11, "bold"))
		#lbl_description.plot(x=x, y=y+0.22*CARD_Y, anchor='c')
		#self.labels.append(lbl_description)
		
	def respond(self):
		self.GUI.resolveMove(self.option, self, "ChooseOneOption")
		
	def remove(self):
		for label in self.labels:
			label.destroy()
		self.destroy()
		
		
class BoardButton(tk.Button):
	def leftClick(self, event):
		self.GUI.resolveMove(None, self, "Board")
		
	def rightClick(self, event):
		self.GUI.cancelSelection()
		
class MulliganButton(HandButton):
	def leftClick(self, event):
		self.selected = 1 - self.selected
		bgColor = "red" if self.selected == 1 else "green"
		self.configure(bg = bgColor)
		for ID in range(1, 3):
			for i in range(len(self.card.Game.mulligans[ID])):
				if self.card.Game.mulligans[ID][i] == self.card: #在mulligans中找到这个按钮对应的卡牌，然后将其对应的换牌状态toggle
					self.card.Game.GUI.mulliganStatus[ID][i] = 1 - self.card.Game.GUI.mulliganStatus[ID][i]
					break
					
	def rightClick(self, event):
		self.card.STATUSPRINT()
		
		
class MinionButton(tk.Button):
	def leftClick(self, event):
		if self.card.cardType == "Minion":
			selectedSubject = "MiniononBoard"
			self.GUI.resolveMove(self.card, self, selectedSubject)
		else: #card.cardType == "Permanent"
			self.GUI.cancelSelection()
			
	def rightClick(self, event):
		self.GUI.cancelSelection()
		self.card.STATUSPRINT()
		
	def plot(self, x=11, y=11, anchor='c'):
		self.labels = []
		self.place(x=x, y=y, anchor=anchor)
		#cardName = self.card.name
		#lbl_name = CardLabel(text=self.GUI.wrapText(cardName), bg="white", fg="black", font=("Yahei", 11, "bold"))
		#lbl_name.plot(x=x, y=y-CARD_Y/2, anchor='c')
		#self.labels.append(lbl_name)
		if self.card.triggersonBoard != [] or (hasattr(self.card, "deathrattles") and self.card.deathrattles != []):
			lbl_trigger = CardLabel(text='  ', bg="yellow", fg="white", font=("Yahei", 6, ))
			lbl_trigger.plot(x=x, y=y+0.47*CARD_Y, anchor='c')
			self.labels.append(lbl_trigger)
		if self.card.cardType == "Minion":
			attack, attack_Enchant, health, health_Enchant, health_upper = self.card.attack, self.card.attack_Enchant, self.card.health, self.card.health_Enchant, self.card.health_upper
			attColor = "green" if attack_Enchant > self.card.attack_0 else "black"
			lbl_attack = CardLabel(text=str(attack), bg="white", fg=attColor, font=("Yahei", 12, "bold"))
			lbl_attack.plot(x=x-0.42*CARD_X, y=y+0.43*CARD_Y, anchor='c')
			self.labels.append(lbl_attack)
			if health >= health_upper:
				healthColor = "black" if health_Enchant <= self.card.health_0 else "green"
			else:
				healthColor = "red"
			lbl_health = CardLabel(text=str(health), bg="white", fg=healthColor, font=("Yahei", 12, "bold"))
			lbl_health.plot(x=x+0.42*CARD_X, y=y+0.43*CARD_Y, anchor='c')
			self.labels.append(lbl_health)
			
	def remove(self):
		self.destroy()
		for label in self.labels:
			label.destroy()
			
class HeroButton(tk.Button):
	def leftClick(self, event):
		self.GUI.resolveMove(self.card, self, "HeroonBoard")
		
	def rightClick(self, event):
		self.GUI.cancelSelection()
		self.card.STATUSPRINT()
		
	def plot(self, x=11, y=11, anchor='c'):
		self.labels = []
		self.place(x=x, y=y, anchor=anchor)
		attack, health, health_upper, armor = self.card.attack, self.card.health, self.card.health_upper, self.card.armor
		if attack > 0:
			lbl_attack = CardLabel(text=str(attack), bg="black", fg="white", font=("Yahei", 12, "bold"))
			lbl_attack.plot(x=x-0.39*CARD_X, y=y+0.3*CARD_Y, anchor='c')
			self.labels.append(lbl_attack)
		if armor > 0:
			lbl_attack = CardLabel(text=str(armor), bg="black", fg="white", font=("Yahei", 12, "bold"))
			lbl_attack.plot(x=x+0.39*CARD_X, y=y+0.1*CARD_Y, anchor='c')
			self.labels.append(lbl_attack)
		healthColor = "black" if health >= health_upper else "red"
		lbl_health = CardLabel(text=str(health), bg="white", fg=healthColor, font=("Yahei", 12, "bold"))
		lbl_health.plot(x=x+0.39*CARD_X, y=y+0.3*CARD_Y, anchor='c')
		self.labels.append(lbl_health)
		
	def remove(self):
		self.destroy()
		for label in self.labels:
			label.destroy()
			
			
class InactionableButton(tk.Button): #休眠物和武器无论左右键都是取消选择，打印目前状态
	def leftClick(self, event):
		self.GUI.cancelSelection()
		self.card.STATUSPRINT()
		
	def rightClick(self, event):
		self.GUI.cancelSelection()
		self.card.STATUSPRINT()
		
	def plot(self, x=11, y=11, anchor='c'):
		self.labels = []
		self.place(x=x, y=y, anchor=anchor)
		if self.card.cardType == "Weapon":
			if self.card.triggersonBoard != [] or (hasattr(self.card, "deathrattles") and self.card.deathrattles != []):
				lbl_trigger = CardLabel(text='  ', bg="yellow", fg="white", font=("Yahei", 6, ))
				lbl_trigger.plot(x=x, y=y+0.36*CARD_Y, anchor='c')
				self.labels.append(lbl_trigger)
			attack, durability = self.card.attack, self.card.durability
			attColor = "green" if attack > type(self.card).attack else "black"
			lbl_attack = CardLabel(text=str(attack), bg="white", fg=attColor, font=("Yahei", 11, "bold"))
			lbl_attack.plot(x=x-0.42*CARD_X, y=y+0.39*CARD_Y, anchor='c')
			self.labels.append(lbl_attack)
			durabilityColor = "black" if durability >= type(self.card).durability else "red"
			lbl_durability = CardLabel(text=str(durability), bg="white", fg=durabilityColor, font=("Yahei", 11, "bold"))
			lbl_durability.plot(x=x+0.42*CARD_X, y=y+0.39*CARD_Y, anchor='c')
			self.labels.append(lbl_durability)
		elif self.card.cardType == "Spell":
			if "~~Quest" in self.card.index:
				bgColor = "yellow" if self.card.description.startswith("Quest:") else "white"
				lbl_progress = CardLabel(text=str(self.card.progress), bg=bgColor, fg="black", font=("Yahei", 14, "bold"))
				lbl_progress.plot(x=x, y=y-0.3*CARD_Y, anchor='c')
				self.labels.append(lbl_progress)
				
	def remove(self):
		self.destroy()
		for label in self.labels:
			label.destroy()
			
			
class HeroPowerButton(tk.Button): #For Hero Powers that are on board
	def leftClick(self, event):
		if self.heroPower.ID == self.Game.turn and self.Game.ManaHandler.costAffordable(self.heroPower) and self.heroPower.available():
			self.GUI.resolveMove(self.heroPower, self, "Hero Power")
		else:
			self.GUI.printInfo("Hero Power can't be selected")
			self.GUI.cancelSelection()
			self.heroPower.STATUSPRINT()
			
	def rightClick(self, event):
		self.GUI.cancelSelection()
		self.heroPower.STATUSPRINT()
		
	def plot(self, x=11, y=11, anchor='c'):
		self.labels = []
		self.place(x=x, y=y, anchor=anchor)
		cardName, mana = self.heroPower.name, self.heroPower.mana
		lbl_mana = CardLabel(text=str(mana), bg="white", fg="black", font=("Yahei", 13, "bold"))
		lbl_mana.plot(x=x, y=y-0.3*CARD_Y, anchor='c')
		self.labels.append(lbl_mana)
		#lbl_name = CardLabel(text=self.GUI.wrapText(cardName), bg="white", fg="black", font=("Yahei", 11, "bold"))
		#lbl_name.plot(x=x, y=y-0.25*CARD_Y, anchor='c')
		#self.labels.append(lbl_name)
		
		
class MulliganFinishButton(tk.Button):
	def respond(self):
		indicesCards1, indicesCards2 = [], []
		for i in range(len(self.GUI.mulliganStatus[1])):
			if self.GUI.mulliganStatus[1][i]:
				indicesCards1.append(i)
		for i in range(len(self.GUI.mulliganStatus[2])):
			if self.GUI.mulliganStatus[2][i]:
				indicesCards2.append(i)
		self.GUI.printInfo("Have decided cards to mulligan.")
		self.GUI.printInfo("\tPlayer 1 will replace the following cards {}".format(indicesCards1))
		self.GUI.printInfo("\tPlayer 2 will replace the following cards {}".format(indicesCards2))
		self.Game.Hand_Deck.mulligan(indicesCards1, indicesCards2)
		self.GUI.UI = 0
		self.GUI.update()
		
class TurnEndButton(tk.Button):
	def respond(self):
		self.GUI.resolveMove(None, self, "TurnEnds")
		
class ClassConfirmationButton(tk.Button):
	def respond(self):
		hero_1 = ClassDict[self.GUI.hero1Label["text"].split(':')[-1]]
		hero_2 = ClassDict[self.GUI.hero2Label["text"].split(':')[-1]]
		global deck1, deck2
		deck1String = self.GUI.deck1.get()
		deck2String = self.GUI.deck2.get()
		deck1Correct, deck2Correct = True, True
		deck1 = decode_deckstring(deck1String) if deck1String != "" else []
		deck2 = decode_deckstring(deck2String) if deck2String != "" else []
		for obj in deck1:
			if obj == None:
				deck1Correct = False
		for obj in deck2:
			if obj == None:
				deck2Correct = False
		if deck1Correct and deck2Correct:
			self.GUI.Game = Game(self.GUI)
			self.GUI.Game.initialize(cardPool, MinionsofCost, MinionswithRace, RNGPools, hero_1, hero_2, deck1, deck2)
			self.GUI.posMulligans = {1:[(70+i*2*111, Y-120) for i in range(len(self.GUI.Game.mulligans[1]))],
								2:[(70+i*2*111, 120) for i in range(len(self.GUI.Game.mulligans[2]))]}
			self.destroy()
			self.GUI.update()
		else:
			if deck1Correct == False:
				self.GUI.printInfo("Deck 1 incorrect")
			if deck2Correct == False:
				self.GUI.printInfo("Deck 2 incorrect")
				
#import tkinter.font as tkFont
#fontStyle = tkFont.Font(family="Lucida Grande", size=3)
class GUI:
	def __init__(self):
		self.posHands = {1:[], 2:[]}
		self.posMinionsDrawn = {1:[], 2:[]}
		self.mulliganStatus = {1:[0, 0, 0], 2:[0, 0, 0, 0]}
		self.buttonsDrawn = []
		self.selectedSubject = ""
		self.subject, self.target = None, None
		self.choice, self.UI = 0, -1 #起手调换
		self.position = -1
		self.discover = None
		self.window = tk.Tk()
		self.GamePanel = tk.Frame(master=self.window, width=X, height=Y, bg="black")
		self.GamePanel.pack(fill=tk.Y, side=tk.LEFT) #place(relx=0, rely=0)
		self.outPutPanel = tk.Frame(master=self.window, width=0.02*X, height=0.3*Y, bg="cyan")
		self.outPutPanel.pack(side=tk.TOP)
		self.inputPanel = tk.Frame(master=self.window, width=int(0.02*X), height=int(0.3*Y), bg="cyan")
		self.inputPanel.pack(side=tk.TOP)
		self.deckImportPanel = tk.Frame(master=self.window, width=0.02*X, height=0.6*Y)
		self.deckImportPanel.pack(side=tk.TOP)
		
		lbl_Output = tk.Label(master=self.outPutPanel, text="System Resolution", font=("Courier", 15))
		lbl_Output.pack(fill=tk.X, side=tk.TOP)
		scrollbar_ver = tk.Scrollbar(master=self.outPutPanel)
		scrollbar_ver.pack(fill=tk.Y, side=tk.RIGHT)
		scrollbar_hor = tk.Scrollbar(master=self.outPutPanel, orient="horizontal")
		scrollbar_hor.pack(fill=tk.X, side=tk.BOTTOM)
		self.output = tk.Listbox(master=self.outPutPanel, xscrollcommand=scrollbar_hor.set, yscrollcommand=scrollbar_ver.set, width=50, height=20, bg="white", font=("Courier", 13))
		self.output.pack(side=tk.LEFT)
		scrollbar_hor.configure(command=self.output.xview)
		scrollbar_ver.configure(command=self.output.yview)
		
		self.text = tk.Entry(master=self.inputPanel, font=("Yahei", 12))
		lbl_Input = tk.Label(master=self.inputPanel, text="Command Input", font=("Courier", 15))
		
		lbl_Input.pack(fill=tk.X)
		self.text.pack(fill=tk.X, side=tk.TOP)
		
		self.printInfo("Import the two decks for players and select the heroes")
		#START in DECKIMPORTPANEL
		#Drop down option menu for the first hero
		hero1 = tk.StringVar(self.deckImportPanel)
		hero1.set(HeroList[0])
		hero1Opt = tk.OptionMenu(self.deckImportPanel, hero1, *HeroList)
		hero1Opt.config(width=15, font=("Yahei", 15))
		hero1Opt["menu"].config(font=("Yahei", 15))
		hero1Opt.pack()#place(x=60, y=60)
		self.hero1Label = tk.Label(self.deckImportPanel, text="Hero 1 :Demon Hunter", font=("Yahei", 15))
		self.hero1Label.pack()
		hero1.trace("w", lambda *arg: self.hero1Label.configure(text="Hero 1 :"+hero1.get()))
		##Drop down option menu for the second hero
		hero2 = tk.StringVar(self.deckImportPanel)
		hero2.set(HeroList[0])
		hero2Opt = tk.OptionMenu(self.deckImportPanel, hero2, *HeroList)
		hero2Opt.config(width=15, font=("Yahei", 15))
		hero2Opt["menu"].config(font=("Yahei", 15))
		hero2Opt.pack()
		self.hero2Label = tk.Label(self.deckImportPanel, text="Hero 2 :Demon Hunter", font=("Yahei", 15))
		self.hero2Label.pack()
		hero2.trace("w", lambda *arg: self.hero2Label.configure(text="Hero 2 :"+hero2.get()))
		#Confirm button to start the game
		btnClassConfirm = ClassConfirmationButton(self.deckImportPanel, bg="green", text="Confirm", font=("Yahei", 15))
		btnClassConfirm.GUI = self
		btnClassConfirm.configure(command=btnClassConfirm.respond)
		btnClassConfirm.pack()
		self.deck1 = tk.Entry(self.deckImportPanel, font=("Yahei", 12))
		self.deck2 = tk.Entry(self.deckImportPanel, font=("Yahei", 12))
		lbl_deck1 = tk.Label(self.deckImportPanel, text="Deck 1 code", font=("Yahei", 14))
		lbl_deck2 = tk.Label(self.deckImportPanel, text="Deck 2 code", font=("Yahei", 14))
		self.deck1.pack(side=tk.LEFT)
		self.deck2.pack(side=tk.LEFT)
		lbl_deck1.place(relx=0.2, rely=0.82, anchor='c')
		lbl_deck2.place(relx=0.8, rely=0.82, anchor='c')
		
		self.window.mainloop()
		
	def printInfo(self, string):
		try:
			self.output.insert(tk.END, string)
			self.output.see("end")
		except:
			self.output.insert(tk.END, "|||||||||||||")
			self.output.insert(tk.END, "|||||||||||||")
			self.output.insert(tk.END, "|||||||||||||")
			self.output.insert(tk.END, "PRINT options is wrong. Continue nonetheless")
			self.output.insert(tk.END, "|||||||||||||")
			self.output.insert(tk.END, "|||||||||||||")
			self.output.insert(tk.END, "|||||||||||||")
			self.output.see("end")
		
	def cancelSelection(self):
		if self.UI != 3: #只有非发现状态下才能取消选择
			self.subject, self.target = None, None
			self.UI, self.position, self.choice = 0, -1, -1
			self.selectedSubject = ""
			for btn in fixedList(self.buttonsDrawn):
				if type(btn) == ChooseOneButton:
					btn.remove()
					extractfrom(btn, self.buttonsDrawn)
				else:
					btn.config(bg=btn.colorOrig)
					
	def wrapText(self, text, lengthLimit=10):
		if len(text) > lengthLimit: #"Savannah Highmane"
			lines, string, words = "", '', text.split(' ')
			for i in range(len(words)): #words = ["Savannah", "Highmane"]
				if string == '': #string为空时，遇到一段文字之后，无论如何都要记录下来，因为这里
					string += words[i] # string += "Savannah"
				else: #如果string不是空的话，则需要判断这个string加上下个单词之后是否会长度过长
					if len(string + words[i]) > lengthLimit: #len("Savannah" + "Highmane") > lengthLimit
						lines += string+'\n' #lines += "Savannah\n"
						string = words[i]
					else: #If including the next word won't make it too long.
						string += ' ' + words[i]
						
			lines += (string)
			return lines
		return text
		
	def update(self):
		if self.UI == -1: #Draw the mulligan part, the cards and the start turn button
			self.printInfo("The game starts. Select the cards you want to replace. Then click the button at the center of the screen")
			self.drawMulligan()
		else:
			if self.UI == 1:
				self.drawChooseOne()
			else:
				self.posMinionsDrawn[1].clear()
				self.posMinionsDrawn[2].clear()
				self.posHands[1].clear()
				self.posHands[2].clear()
				for btn in self.buttonsDrawn:
					btn.remove() if hasattr(btn, "remove") else btn.destroy()
				self.buttonsDrawn = []
				self.drawBoard()
				for i in range(len(self.Game.minions[1])):
					self.posMinionsDrawn[1].append((0.043*X+(X/9)*i, 0.58*Y))
				for i in range(len(self.Game.minions[2])):
					self.posMinionsDrawn[2].append((0.043*X+(X/9)*i, 0.40*Y))
				for i in range(len(self.Game.Hand_Deck.hands[1])):
					self.posHands[1].append((0.043*X+(X/13)*i, Y - 0.07*Y))
				for i in range(len(self.Game.Hand_Deck.hands[2])):
					self.posHands[2].append((0.043*X+(X/13)*i, 0.11*Y))
					
				btnTurnEnd = TurnEndButton(relief=tk.FLAT, master=self.GamePanel, text="Turn End", bg="green", fg="white", width=12, height=2, font=("Yahei", 13, "bold"))
				btnTurnEnd.Game, btnTurnEnd.GUI, btnTurnEnd.colorOrig = self.Game, self, "green"
				btnTurnEnd.configure(command=btnTurnEnd.respond)
				if self.Game.turn == 1:
					btnTurnEnd.place(relx=0.94, rely=0.55, anchor='c')
				else:
					btnTurnEnd.place(relx=0.94, rely=0.45, anchor='c')
				self.buttonsDrawn.append(btnTurnEnd)
				self.drawHands()
				self.drawMinions()
				self.drawHeroesWeaponsPowers()
				self.drawManasHandsDecksSecretsQuests()
				
	def drawMulligan(self):
		for ID in range(1, 3):
			num = 0
			for i in range(len(self.posMulligans[ID])):
				pos = self.posMulligans[ID][i]
				card = self.Game.mulligans[ID][i]
				color = "red" if self.mulliganStatus[ID][i] else "green"
				#代表一张起手牌的按钮被按下时会让这个牌对应的mulliganStatus在1和0之间变化
				img = PIL.Image.open(findPicFilepath(card))
				img = img.resize((78, 75))
				ph = PIL.ImageTk.PhotoImage(img)
				btnMulligan = MulliganButton(relief=tk.FLAT, master=self.GamePanel, image=ph, bg=color, width=CARD_X, height=CARD_Y)
				btnMulligan.image = ph
				btnMulligan.Game, btnMulligan.GUI, btnMulligan.card, btnMulligan.selected = self.Game, self, card, 0
				btnMulligan.bind('<Button-1>', btnMulligan.leftClick)   # bind left mouse click
				btnMulligan.bind('<Button-3>', btnMulligan.rightClick)   # bind right mouse click
				btnMulligan.plot(x=pos[0], y=pos[1], anchor='c')
				self.buttonsDrawn.append(btnMulligan)
		mulliganFinished = MulliganFinishButton(relief=tk.FLAT, master=self.GamePanel, text="Replace Card and\nStart 1st Turn", bg="green", width=13, height=3, font=("Yahei", 12, "bold"))
		mulliganFinished.Game, mulliganFinished.GUI = self.Game, self
		mulliganFinished.configure(command=mulliganFinished.respond)
		mulliganFinished.place(x=X/2, y=Y/2, anchor='c')
		self.buttonsDrawn.append(mulliganFinished)
		
	def drawBoard(self):
		btnBoard = BoardButton(relief=tk.FLAT, master=self.GamePanel, bg=boardColor, width=Board_X, height=Board_Y)
		btnBoard.GUI, btnBoard.selected, btnBoard.colorOrig = self, 0, boardColor
		btnBoard.bind('<Button-1>', btnBoard.leftClick)   # bind left mouse click
		btnBoard.bind('<Button-3>', btnBoard.rightClick)   # bind right mouse click
		btnBoard.place(x=0.37*X, y=Y/2, anchor='c')
		self.buttonsDrawn.append(btnBoard)
		
	def drawHands(self):
		for ID in range(1, 3):
			for i in range(len(self.posHands[ID])):
				card, color = self.Game.Hand_Deck.hands[ID][i], "red"
				if ID == self.Game.turn and self.Game.ManaHandler.costAffordable(card):
					if (card.cardType == "Spell" and card.available()) or (card.cardType == "Minion" and self.Game.spaceonBoard(ID) > 0) or card.cardType == "Weapon" or card.cardType == "Hero":
						if card.evanescent:
							color = "blue"
						elif hasattr(card, "effectViable") and card.effectViable:
							color = "yellow"
						else:
							color = "green"
				pos = self.posHands[ID][i]
				img = PIL.Image.open(findPicFilepath(card))
				img = img.resize((int(0.95*Hand_X), int(0.95*Hand_X)))
				ph = PIL.ImageTk.PhotoImage(img)
				btnHand = HandButton(relief=tk.FLAT, image=ph, master=self.GamePanel, bg=color, width=Hand_X, height=1.3*Hand_Y)
				btnHand.image = ph
				btnHand.GUI, btnHand.Game, btnHand.card, btnHand.selected, btnHand.colorOrig = self, self.Game, card, 0, color
				btnHand.bind('<Button-1>', btnHand.leftClick)   # bind left mouse click
				btnHand.bind('<Button-3>', btnHand.rightClick)   # bind right mouse click
				#btnHand.configure(image=img)
				btnHand.plot(x=pos[0], y=pos[1], anchor='c')
				self.buttonsDrawn.append(btnHand)
				
				
	def drawMinions(self):
		for ID in range(1, 3):
			for i in range(len(self.posMinionsDrawn[ID])):
				pos, minion = self.posMinionsDrawn[ID][i], self.Game.minions[ID][i]
				color = ("green" if minion.canAttack() else "red") if minion.cardType == "Minion" else "grey46"
				#if minion.cardType == "Minion":
				#	color = "green" if minion.canAttack() else "red"
				#else:
				#	color = "grey46"
				if minion.sequence == 0:
					order = "1st"
				elif minion.sequence == 1:
					order = "2nd"
				elif minion.sequence == 2:
					order = "3rd"
				else:
					order = "%dth"%(minion.sequence+1)
				text = order+" "
				if minion.race != "":
					if ',' not in minion.race:
						text += minion.race
					else:
						text += "All"
				if hasattr(minion, "progress"):
					text += " #%d"%minion.progress
				text += '\n'
				for key, value in minion.keyWords.items():
					if value > 1:
						text += "%s:%d\n"%(key, value)
					elif value == 1:
						text += key+'\n'
				img = PIL.Image.open(findPicFilepath(minion))
				img = img.resize((78, 75))
				ph = PIL.ImageTk.PhotoImage(img)
				btnMinion = MinionButton(text=text, image=ph, relief=tk.FLAT, compound=tk.TOP, anchor ='n', master=self.GamePanel, bg=color, width=CARD_X, height=CARD_Y, font=("Yahei", 10, "bold"))
				btnMinion.image = ph
				btnMinion.Game, btnMinion.GUI, btnMinion.card, btnMinion.selected, btnMinion.colorOrig = self.Game, self, minion, 0, color
				btnMinion.bind('<Button-1>', btnMinion.leftClick)
				btnMinion.bind('<Button-3>', btnMinion.rightClick)
				btnMinion.plot(x=pos[0], y=pos[1], anchor='c')
				self.buttonsDrawn.append(btnMinion)
				
	def drawHeroesWeaponsPowers(self):
		for ID in range(1, 3):
			#Draw hero
			hero = self.Game.heroes[ID]
			color = "green" if hero.canAttack() else "red"
			pos = Hero1Pos if ID == 1 else Hero2Pos
			img = PIL.Image.open(findPicFilepath(hero))
			img = img.resize((HeroIconSize, HeroIconSize))
			ph = PIL.ImageTk.PhotoImage(img)
			btnHero = HeroButton(relief=tk.FLAT, master=self.GamePanel, image=ph, bg=color, width=1.2*Hand_X, height=1.4*Hand_Y)
			btnHero.image = ph
			btnHero.Game, btnHero.GUI, btnHero.card, btnHero.selected, btnHero.colorOrig = self.Game, self, hero, 0, color
			btnHero.bind('<Button-1>', btnHero.leftClick)
			btnHero.bind('<Button-3>', btnHero.rightClick)
			btnHero.plot(x=pos[0], y=pos[1], anchor='c')
			self.buttonsDrawn.append(btnHero)
			#Draw Hero Power
			heroPower = self.Game.heroPowers[ID]
			color = "green" if ID == self.Game.turn and heroPower.available() and self.Game.ManaHandler.costAffordable(heroPower) else "red"
			pos = HeroPower1Pos if ID == 1 else HeroPower2Pos
			img = PIL.Image.open(findPicFilepath(heroPower))
			img = img.resize((int(0.9*HeroIconSize), int(0.9*HeroIconSize)))
			ph = PIL.ImageTk.PhotoImage(img)
			btnHeroPower = HeroPowerButton(relief=tk.FLAT, master=self.GamePanel, image=ph, bg=color, width=HeroIconSize, height=HeroIconSize)
			btnHeroPower.image = ph
			btnHeroPower.Game, btnHeroPower.GUI, btnHeroPower.heroPower, btnHeroPower.selected, btnHeroPower.colorOrig = self.Game, self, heroPower, 0, color
			btnHeroPower.bind('<Button-1>', btnHeroPower.leftClick)
			btnHeroPower.bind('<Button-3>', btnHeroPower.rightClick)
			btnHeroPower.plot(x=pos[0], y=pos[1], anchor='c')
			self.buttonsDrawn.append(btnHeroPower)
			#Draw weapon
			weapon = self.Game.availableWeapon(ID)
			if weapon != None:
				pos = Weapon1Pos if ID == 1 else Weapon2Pos
				if weapon.sequence == 0:
					order = "1st"
				elif weapon.sequence == 1:
					order = "2nd"
				elif weapon.sequence == 2:
					order = "3rd"
				else:
					order = "%dth"%(weapon.sequence+1)
				text = order+' '
				if hasattr(weapon, "progress"):
					text += " #%d\n"+str(weapon.progress)
				for key, value in weapon.keyWords.items():
					if value > 0:
						text += key+'\n'
				img = PIL.Image.open(findPicFilepath(weapon))
				img = img.resize((int(0.95*HeroIconSize), int(0.95*HeroIconSize)))
				ph = PIL.ImageTk.PhotoImage(img)
				btnWeapon = InactionableButton(text=text, relief=tk.FLAT, image=ph, compound=tk.TOP, master=self.GamePanel, bg="blue", width=HeroIconSize, height=1.2*HeroIconSize, font=("Yahei", 10, "bold"))
				btnWeapon.image = ph
				btnWeapon.Game, btnWeapon.GUI, btnWeapon.card, btnWeapon.selected, btnWeapon.colorOrig = self.Game, self, weapon, 0, "blue"
				btnWeapon.bind('<Button-1>', btnWeapon.leftClick)
				btnWeapon.bind('<Button-3>', btnWeapon.rightClick)
				btnWeapon.plot(x=pos[0], y=pos[1], anchor='c')
				self.buttonsDrawn.append(btnWeapon)
				
	def drawManasHandsDecksSecretsQuests(self):
		if self.Game.turn == 1:
			color1, color2 = "green", "red"
		else:
			color1, color2 = "red", "green"
		manaText1 = "Mana:{}/{}\nHand:{}\nDeck:{}\nOverload:{}\nLocked:{}".format(self.Game.ManaHandler.manas[1], self.Game.ManaHandler.manasUpper[1],
						len(self.Game.Hand_Deck.hands[1]), len(self.Game.Hand_Deck.decks[1]), self.Game.ManaHandler.manasOverloaded[1], self.Game.ManaHandler.manasLocked[1])
		manaText2 = "Mana:{}/{}\nHand:{}\nDeck:{}\nOverload:{}\nLocked:{}".format(self.Game.ManaHandler.manas[2], self.Game.ManaHandler.manasUpper[2],
						len(self.Game.Hand_Deck.hands[2]), len(self.Game.Hand_Deck.decks[2]), self.Game.ManaHandler.manasOverloaded[2], self.Game.ManaHandler.manasLocked[2])
		lbl_Mana1 = tk.Label(master=self.GamePanel, text=manaText1, bg=color1, fg="black", font=("Yahei", 20, "bold"))
		lbl_Mana2 = tk.Label(master=self.GamePanel, text=manaText2, bg=color2, fg="black", font=("Yahei", 20, "bold"))
		lbl_Mana1.selected, lbl_Mana1.colorOrig, lbl_Mana2.selected, lbl_Mana2.colorOrig = 0, color1, 0, color2
		lbl_Mana1.place(relx=0.9,rely=0.7, anchor='c')
		lbl_Mana2.place(relx=0.9,rely=0.3, anchor='c')
		self.buttonsDrawn.append(lbl_Mana1)
		self.buttonsDrawn.append(lbl_Mana2)
		#Draw the Secrets and Quests
		for ID in range(1, 3):
			list_QuestsandSecrets = []
			for obj in self.Game.SecretHandler.mainQuests[ID]+self.Game.SecretHandler.sideQuests[ID]+self.Game.SecretHandler.secrets[ID]:
				list_QuestsandSecrets.append(obj)
			for i in range(len(list_QuestsandSecrets)):
				obj = list_QuestsandSecrets[i]
				pos = (0.04*X+(X/16)*i, Y - 0.23*Y) if obj.ID == 1 else (0.043*X+(X/14)*i, 0.23*Y)
				img = PIL.Image.open(findPicFilepath(obj))
				img = img.resize((int(0.95*SecretIconSize), int(0.95*SecretIconSize)))
				ph = PIL.ImageTk.PhotoImage(img)
				color = "green" if ("~~Secret" in obj.index and obj.ID != self.Game.turn) else "red"
				btnSecretQuest = InactionableButton(self.GamePanel, image=ph, bg=color, height=SecretIconSize, width=SecretIconSize)
				btnSecretQuest.image = ph
				btnSecretQuest.Game, btnSecretQuest.GUI, btnSecretQuest.card, btnSecretQuest.selected, btnSecretQuest.colorOrig = self.Game, self, obj, 0, color
				btnSecretQuest.plot(x=pos[0], y=pos[1], anchor='c')
				self.buttonsDrawn.append(btnSecretQuest)
				
	def drawChooseOne(self):
		for i in range(len(self.Game.options)):
			option = self.Game.options[i]
			pos = (0.2*X+0.125*X*i, 0.4*Y)
			btnChooseOne = ChooseOneButton(relief=tk.FLAT, master=self.GamePanel, text=self.wrapText(option.description, 8), bg="green", width=card_x, height=card_y, font=("Yahei", 10, "bold"))
			btnChooseOne.option, btnChooseOne.GUI, btnChooseOne.selected, btnChooseOne.colorOrig = option, self, 0, "green"
			btnChooseOne.configure(command=btnChooseOne.respond)
			btnChooseOne.plot(x=pos[0], y=pos[1], anchor='c')
			self.buttonsDrawn.append(btnChooseOne)
			
	def resolveMove(self, entity, button, selectedSubject):
		if self.UI == 0:
			for btn in self.buttonsDrawn:
				btn.configure(bg=btn.colorOrig)
			if selectedSubject == "Board": #Weapon won't be resolved by this functioin. It automatically cancels selection
				self.printInfo("Board is not a valid subject.")
				self.cancelSelection()
			elif selectedSubject == "TurnEnds":
				self.cancelSelection()
				self.Game.switchTurn()
				self.update()
			elif entity.ID != self.Game.turn:
				self.printInfo("You can only select your own characters as subject.")
				self.cancelSelection()
			else: #选择的是我方手牌、我方英雄、我方英雄技能、我方场上随从，
				self.subject, self.target = entity, None
				self.selectedSubject = selectedSubject
				self.UI, self.choice = 2, 0 #选择了主体目标，则准备进入选择打出位置或目标界面。抉择法术可能会将界面导入抉择界面。
				button.selected = 1 - button.selected
				button.configure(bg="white")
				if "inHand" in selectedSubject: #Choose card in hand as subject
					if self.Game.ManaHandler.costAffordable(entity) == False: #No enough mana to use card
						self.cancelSelection()
					else: #除了法力值不足，然后是指向性法术没有合适目标和随从没有位置使用
						#If the card in hand is Choose One spell.
						if selectedSubject == "SpellinHand" and entity.available() == False:
							#法术没有可选目标，或者是不可用的非指向性法术
							self.printInfo("Selected spell unavailable. All selection canceled.")
							self.cancelSelection()
						elif selectedSubject == "MinioninHand" and self.Game.spaceonBoard(entity.ID) < 1:
							self.printInfo("The board is full and minion selected can't be played")
							self.cancelSelection()
						else:
							if entity.chooseOne > 0:
								if self.Game.playerStatus[entity.ID]["Choose Both"] > 0:
									self.choice = "ChooseBoth" #跳过抉择，直接进入UI=1界面。
								else:
									self.Game.options = entity.options
									self.UI = 1 #进入抉择界面，退出抉择界面的时候已经self.choice已经选好。
									self.update()
				#不需目标的英雄技能当即使用。需要目标的进入目标选择界面。暂时不用考虑技能的抉择
				elif selectedSubject == "Hero Power":
					#英雄技能会自己判定是否可以使用。
					if entity.needTarget(): #selectedSubject之前是"Hero Power 1"或者"Hero Power 2"
						self.selectedSubject = "Hero Power"
					else:
						self.printInfo("Request to use Hero Power {}".format(self.subject.name))
						subject = self.subject
						self.cancelSelection()
						subject.use(None) #Whether the Hero Power is used or not is handled in the use method.
						self.update()
				#不能攻击的随从不能被选择。
				elif selectedSubject.endswith("onBoard"):
					if entity.canAttack() == False:
						self.cancelSelection()
						
		elif self.UI == 1:
			if selectedSubject == "ChooseOneOption" and entity.available():
				#The first option is indexed as 0.
				index = self.Game.options.index(entity)
				self.printInfo("Choice {} chosen".format(entity.name))
				self.UI, self.choice = 2, index
				for btn in fixedList(self.buttonsDrawn):
					if type(btn) == ChooseOneButton:
						btn.remove()
						extractfrom(btn, self.buttonsDrawn)
			elif selectedSubject == "TurnEnds":
				self.cancelSelection()
				self.Game.switchTurn()
				self.update()
			else:
				self.printInfo("You must click an available option to continue.")
				
		elif self.UI == 2:
			self.target = entity
			self.printInfo("Selected target: {}".format(entity))
			#No matter what the selections are, pressing EndTurn button ends the turn.
			#选择的主体是场上的随从或者英雄。之前的主体在UI=0的界面中已经确定一定是友方角色。
			if selectedSubject == "TurnEnds":
				self.cancelSelection()
				self.Game.switchTurn()
				self.update()
			elif self.selectedSubject.endswith("onBoard"):
				if "Hero" not in selectedSubject and selectedSubject != "MiniononBoard":
					self.printInfo("Invalid target for minion attack.")
				else:
					self.printInfo("Requesting battle: {} attacks {}".format(self.subject.name, entity))
					subject, target = self.subject, self.target
					self.cancelSelection()
					self.Game.battleRequest(subject, target)
					self.update()
			#手中选中的随从在这里结算打出位置，如果不需要目标，则直接打出。
			elif self.selectedSubject == "MinioninHand":
				if selectedSubject == "Board" or (selectedSubject == "MiniononBoard" and entity.ID == ID):
					self.position = -1 if selectedSubject == "Board" else entity.position
					self.printInfo("Position for minion in hand decided: %d"%self.position)
					self.selectedSubject = "MinionPositionDecided" #将主体记录为标记了打出位置的手中随从。
					#抉择随从如有全选光环，且所有选项不需目标，则直接打出。 连击随从的needTarget()由连击条件决定。
					self.printInfo("Minion {} in hand needs target: {}".format(self.subject.name, self.subject.needTarget(self.choice)))
					if self.subject.needTarget(self.choice) == False or self.subject.targetExists(self.choice) == False:
						self.printInfo("Requesting to play minion {} without target. The choice is {}".format(self.subject.name, self.choice))
						subject, position, choice = self.subject, self.position, self.choice
						self.cancelSelection()
						self.Game.playMinion(subject, None, position, choice)
						self.update()
					else:
						self.printInfo("The minion requires target to play. needTarget() returns {}".format(self.subject.needTarget(self.choice)))
						button.configure(bg="purple")
			#随从的打出位置和抉择选项已经在上一步选择，这里处理目标选择。
			elif self.selectedSubject == "MinionPositionDecided":
				if selectedSubject.endswith("MiniononBoard") == False and selectedSubject.endswith("HeroonBoard") == False: #指定目标时必须是英雄或者场上随从
					self.printInfo("Board is not a valid option. All selections canceled.")
				else:
					self.printInfo("Requesting to play minion {}, targeting {} with choice: {}".format(self.subject.name, entity.name, self.choice))
					subject, position, choice = self.subject, self.position, self.choice
					self.cancelSelection()
					self.Game.playMinion(subject, entity, position, choice)
					self.update()
			#选中的法术已经确定抉择选项（如果有），下面决定目标选择。
			elif self.selectedSubject == "SpellinHand":
				if self.subject.needTarget(self.choice) == False:
					if selectedSubject == "Board":
						self.printInfo("Requesting to play spell {} without target. The choice is {}".format(self.subject.name, self.choice))
						subject, target, choice = self.subject, None, self.choice
						self.cancelSelection()
						self.Game.playSpell(subject, target, choice)
						self.update()
				else: #法术或者法术抉择选项需要指定目标。
					if "Hero" not in selectedSubject and selectedSubject != "MiniononBoard":
						self.printInfo("Targeting spell must be cast on Hero or Minion on board.")
					else:
						self.printInfo("Requesting to play spell {} with target {}. The choice is {}".format(self.subject.name, entity, self.choice))
						subject, target, choice = self.subject, entity, self.choice
						self.cancelSelection()
						self.Game.playSpell(subject, target, choice)
						self.update()
			#选择手牌中的武器的打出目标
			elif self.selectedSubject == "WeaponinHand":
				if self.subject.requireTarget == False:
					if selectedSubject == "Board":
						self.printInfo("Requesting to play Weapon {}".format(self.subject.name))
						subject, target = self.subject, None
						self.cancelSelection()
						self.Game.playWeapon(subject, None)
						self.update()
				else:
					if "Hero" not in selectedSubject and selectedSubject != "MiniononBoard":
						self.printInfo("Targeting weapon must be played with a target.")
					else:
						subject, target = self.subject, entity
						self.printInfo("Requesting to play weapon {} with target {}".format(subject.name, target.name))
						self.cancelSelection()
						self.Game.playWeapon(subject, target)
						self.update()
			#手牌中的英雄牌是没有目标的
			elif self.selectedSubject == "HeroinHand":
				if selectedSubject == "Board":
					self.printInfo("Requesting to play hero card {}".format(self.subject.name))
					subject = self.subject
					self.cancelSelection()
					self.Game.playHero(subject)
					self.update()
			#Select the target for a Hero Power.
			#在此选择的一定是指向性的英雄技能。
			elif self.selectedSubject == "Hero Power": #如果需要指向的英雄技能对None使用，HeroPower的合法性检测会阻止使用。
				if "Hero" not in selectedSubject and selectedSubject != "MiniononBoard":
					self.printInfo("Targeting hero power must be used with a target.")
				else:
					self.printInfo("Requesting to use Hero Power {} on {}".format(self.subject.name, entity.name))
					subject = self.subject
					self.cancelSelection()
					subject.use(entity)
					self.update()
					
		else: #self.UI == 3
			if selectedSubject == "DiscoverOption":
				#The first option is indexed as 0.
				for i in range(len(self.Game.options)):
					if entity == self.Game.options[i]:
						self.printInfo("Discover option {} chosen".format(self.Game.options[i].name))
						self.UI, option = 0, self.Game.options[i] #选项已准备好，进入目标或打出位置选择界面选择界面
						break
				self.update()
				self.Game.DiscoverHandler.initiator.discoverDecided(option)
			else:
				self.printInfo("You must click an Discover option to continue.")
				
	def waitforDiscover(self):
		self.UI, self.discover, var = 3, None, tk.IntVar()
		btnDiscoverConfirm = tk.Button(relief=tk.FLAT, master=self.GamePanel, text="Confirm\nDiscover", bg="lime green", width=10, height=4, font=("Yahei", 12, "bold"))
		btnDiscoverConfirm.GUI, btnDiscoverConfirm.colorOrig = self, "lime green"
		btnDiscoverConfirm.configure(command=lambda: var.set(1) if self.discover != None else print())
		btnDiscoverHide = DiscoverHideButton(relief=tk.FLAT, master=self.GamePanel, text="Hide", bg="green", width=5, height=2, font=("Yahei", 12, "bold"))
		btnDiscoverHide.configure(command=btnDiscoverHide.respond)
		btnDiscoverHide.Game, btnDiscoverHide.GUI, btnDiscoverHide.selected, btnDiscoverHide.colorOrig = self.Game, self, 0, "green"
		btnDiscoverHide.place(x=0.82*X, y=0.5*Y, anchor='c')
		self.buttonsDrawn.append(btnDiscoverHide)
		for i in range(len(self.Game.options)):
			pos = (0.2*X+0.125*X*i, 0.5*Y, 0.09*X, 0.15*Y)
			if hasattr(self.Game.options[i], "cardType"):
				card = self.Game.options[i]
				img = PIL.Image.open(findPicFilepath(card))
				img = img.resize((70, 70))
				ph = PIL.ImageTk.PhotoImage(img)
				btnDiscover = DiscoverCardButton(relief=tk.FLAT, master=self.GamePanel, image=ph, bg="green", width=CARD_X, height=CARD_Y)
				btnDiscover.image = ph
				btnDiscover.bind('<Button-1>', btnDiscover.leftClick)
				btnDiscover.bind('<Button-3>', btnDiscover.rightClick)
				btnDiscover.pos, btnDiscover.card, btnDiscover.GUI, btnDiscover.selected, btnDiscover.colorOrig = pos, card, self, 0, "green"
			else:
				option = self.Game.options[i]
				btnDiscover = DiscoverOptionButton(relief=tk.FLAT, master=self.GamePanel, text=self.wrapText(option.description), bg="green", width=card_x, height=card_y, font=("Yahei", 12, "bold"))
				btnDiscover.pos, btnDiscover.option, btnDiscover.GUI, btnDiscover.selected, btnDiscover.colorOrig = pos, option, self, 0, "green"
				btnDiscover.configure(command=btnDiscover.respond)
			btnDiscover.plot(x=pos[0], y=pos[1], anchor='c')
			self.buttonsDrawn.append(btnDiscover)
		btnDiscoverConfirm.place(x=0.73*X, y=0.5*Y, anchor='c')
		btnDiscoverConfirm.wait_variable(var)
		self.resolveMove(self.discover, None, "DiscoverOption")
		
	def wishforaCard(self, initiator):
		self.UI = 3
		btnTypeConfirm = tk.Button(relief=tk.FLAT, master=self.inputPanel, text="Enter", bg="lime green", width=7, height=1, font=("Yahei", 20, "bold"))
		btnTypeConfirm.GUI, btnTypeConfirm.colorOrig = self, "lime green"
		btnTypeConfirm.pack(fill=tk.X)
		var = tk.IntVar()
		self.text.bind("<Return>", lambda event: var.set(1))
		while True:
			self.printInfo("Type the name of the card you want")
			btnTypeConfirm.configure(command=lambda: var.set(1))
			btnTypeConfirm.wait_variable(var)
			cardName = self.text.get()
			self.text.delete(0, "end")
			if cardName in self.Game.RNGPools["Basic and Classic Card Index"].keys():
				card = self.Game.RNGPools["Basic and Classic Card Index"][cardName](self.Game, initiator.ID)
				self.Game.Hand_Deck.addCardtoHand(card, initiator.ID)
				break
			else:
				self.printInfo("Input has NO match with a Basic or Classic card. Do you want to see card names in a certain class?")
				self.printInfo("y/n to show class card names or search by name: ")
				var = tk.IntVar()
				btnTypeConfirm.wait_variable(var)
				searchinIndex = self.text.get()
				self.text.delete(0, "end")
				if searchinIndex == 'y' or searchinIndex == 'Y' or searchinIndex == 'Yes' or searchinIndex == 'yes':
					self.printInfo("Class: Demon Hunter, Druid, Hunter, Mage, Paladin, Priest, Rogue, Shaman, Warlock, Warrior\n")
					var = tk.IntVar()
					btnTypeConfirm.wait_variable(var)
					className = self.text.get()
					self.text.delete(0, "end")
					if className not in ["Demon Hunter", "Druid", "Mage", "Hunter", "Paladin", "Priest", "Rogue", "Shaman", "Warlock", "Warrior", "Neutral"]:
						self.printInfo("Class input wrong. Returning to search by name")
					else:
						self.printInfo("Showing %s cards"%className)
						for value in self.Game.RNGPools["Basic and Classic %s Cards"%className]:
							self.printInfo("{}:   Mana {},  Description {}".format(value.name, value.mana, value.description))
						self.printInfo("Returning to search by card name")
				else:
					self.printInfo("Returning to search by card name")
		btnTypeConfirm.destroy()
		self.text.unbind("<Return>")
		self.UI = 0
		self.update()
GUI()