from numpy.random import choice as npchoice
from tkinter import messagebox
import tkinter as tk
import PIL.Image, PIL.ImageTk
import threading
import time
from collections import Counter as cnt
import numpy as np

def concatenateDicts(dict1, dict2):
	for key in dict2.keys():
		dict1[key] = copy.deepcopy(dict2[key]) if key not in dict1 else concatenateDicts(dict1[key], dict2[key])
	return dict1
	
def indexHasClass(index, Class):
	return Class in index.split('~')[1]
	
def canBeGenerated(cardType, SV=0):
	return (SV or not cardType.index.startswith("SV_")) and not cardType.description.startswith("Quest:") and \
			not ("Galakrond" in cardType.name or "Galakrond" in cardType.description or "Invoke" in cardType.description or "invoke" in cardType.description)
			
			
class PoolManager:
	def __init__(self):
		self.cardPool = {}
		
		
from Core_2021 import *
from AcrossPacks import *
#from DemonHunterInitiate import *
from Outlands import *
from Academy import *
from Darkmoon import *
from Barrens import *

#from SV_Basic import *
#from SV_Ultimate import *
#from SV_Uprooted import *
#from SV_Fortune import *
#from SV_Rivayle import *
#from SV_Eternal import *

transferStudentPool = {"1 Classic Ogrimmar": TransferStudent_Ogrimmar,
						   "2 Classic Stormwind": TransferStudent_Stormwind,
						   "3 Classic Stranglethorn": TransferStudent_Stranglethorn,
						   "4 Classic Four Wind Valley": TransferStudent_FourWindValley,
						   #"5 Naxxramas": TransferStudent_Naxxramas,
						   #"6 Goblins vs Gnomes": TransferStudent_GvG,
						   #"7 Black Rock Mountain": TransferStudent_BlackRockM,
						   #"8 The Grand Tournament": TransferStudent_Tournament,
						   #"9 League of Explorers Museum": TransferStudent_LOEMuseum,
						   #"10 League of Explorers Ruins": TransferStudent_LOERuins,
						   #"11 Corrupted Stormwind": TransferStudent_OldGods,
						   #"12 Karazhan": TransferStudent_Karazhan,
						   #"13 Gadgetzan": TransferStudent_Gadgetzan,
						   #"14 Un'Goro": TransferStudent_UnGoro,
						   #"15 Frozen Throne": TransferStudent_FrozenThrone,
						   #"16 Kobolds": TransferStudent_Kobold,
						   #"17 Witchwood": TransferStudent_Witchwood,
						   #"18 Boomsday Lab": TransferStudent_Boomsday,
						   #"19 Rumble": TransferStudent_Rumble,
						   #"20 Dalaran": TransferStudent_Shadows,
						   #"21 Uldum Desert": TransferStudent_UldumDesert,
						   #"22 Uldum Oasis": TransferStudent_UldumOasis,
						   #"23 Dragons": TransferStudent_Dragons,
						   "24 Outlands": TransferStudent_Outlands,
						   "25 Scholomance Academy": TransferStudent_Academy,
						   "26 Darkmoon Faire": TransferStudent_Darkmoon,
						   }


def makeCardPool(board="0 Random Game Board", monk=0, SV=0):
	cardPool, info = {}, ""
	
	cardPool.update(AcrossPacks_Indices) #Has the basic hero and hero power definitions.
	info += "from AcrossPacks import *\n"
	
	cardPool.update({card.index: card for card in Core_2021_Cards})
	info += "from Core_2021 import *\n"
	
	cardPool.update({card.index: card for card in Outlands_Cards})
	info += "from Outlands import *\n"
	
	if board == "0 Random Game Board": board = npchoice(list(transferStudentPool))
	transferStudent = transferStudentPool[board]
	cardPool.update({card.index: card for card in Academy_Cards})
	print("The transferStudent in the card pool is currently", transferStudent, transferStudent.index)
	info += "from Academy import *\n"
	
	cardPool.update({card.index: card for card in Darkmoon_Cards})
	info += "from Darkmoon import *\n"
	
	cardPool.update({card.index: card for card in Barrens_Cards})
	info += "from Barrens import *\n"
	#if monk:
	#	print("Including Monk")
	#	cardPool.update(Monk_Indices)
	#	info += "from Monk import *\n"
	#
	#if SV:
	#	cardPool.update(SV_Basic_Indices)
	#	info += "from SV_Basic import *\n"
		
		#cardPool.update(SV_Ultimate_Indices)
		#info += "from SV_Ultimate import *\n"
		#
		#cardPool.update(SV_Uprooted_Indices)
		#info += "from SV_Uprooted import *\n"
		#
		#cardPool.update(SV_Fortune_Indices)
		#info += "from SV_Fortune import *\n"
		#
		#cardPool.update(SV_Rivayle_Indices)
		#info += "from SV_Rivayle import *\n"
		#
		#cardPool.update(SV_Eternal_Indices)
		#info += "from SV_Eternal import *\n"
	
	BasicPowers, UpgradedPowers, Classes, ClassesandNeutral, ClassDict = [], [], [], [], {}
	for key in list(cardPool.keys()):
		if "Hero: " in key:
			Class = key.split(":")[1].strip()
			Classes.append(Class)
			ClassesandNeutral.append(Class)
			ClassDict[Class] = cardPool[key]
			del cardPool[key]
		elif " Hero Power~" in key:
			if "~Upgraded Hero Power~" in key: UpgradedPowers.append(cardPool[key])
			else: BasicPowers.append(cardPool[key])
			del cardPool[key]
	
	ClassesandNeutral.append("Neutral")
	
	Game = PoolManager()
	Game.Classes = Classes
	Game.ClassesandNeutral = ClassesandNeutral
	Game.ClassDict = ClassDict
	Game.cardPool = cardPool
	Game.basicPowers = BasicPowers
	Game.upgradedPowers = UpgradedPowers
	
	#print("SV cards included in card pool:", "SV_Basic~Runecraft~4~3~3~Minion~~Vesper, Witchhunter~Accelerate~Fanfare" in Game.cardPool)
	#cardPool本身需要保留各种祈求牌
	Game.MinionswithRace = {"Beast": {}, "Demon": {}, "Dragon": {}, "Elemental":{},
							"Murloc": {}, "Mech": {}, "Pirate":{}, "Totem": {}}
	if SV:
		SV_Races = ["Officer", "Commander", "Machina", "Natura", "Earth Sigil", "Mysteria", "Artifact", "Levin"]
		for race in SV_Races:
			Game.MinionswithRace[race] = {}
	
	for key, value in Game.cardPool.items(): #Fill MinionswithRace
		if "~Uncollectible" not in key and hasattr(value, "race") and value.race and canBeGenerated(value, SV=SV):
			for race in value.race.split(','):
				Game.MinionswithRace[race][key] = value
	
	Game.MinionsofCost = {}
	for key, value in Game.cardPool.items():
		if "~Minion~" in key and "~Uncollectible" not in key and canBeGenerated(value, SV=SV):
			cost = int(key.split('~')[3])
			try: Game.MinionsofCost[cost][key] = value
			except: Game.MinionsofCost[cost] = {key: value}
	
	Game.ClassCards = {s:{} for s in Game.Classes}
	Game.NeutralCards = {}
	for key, value in Game.cardPool.items():  #Fill NeutralCards
		if "~Uncollectible" not in key and canBeGenerated(value, SV=SV):
			for Class in key.split('~')[1].split(','):
				if Class != "Neutral":
					try: Game.ClassCards[Class][key] = value
					except: print("Failed Class Assignment is ", Class, key, value)
				else: Game.NeutralCards[key] = value
	
	Game.LegendaryMinions = {}
	for key, value in Game.cardPool.items():
		if "~Legendary" in key and "~Minion~" in key and "~Uncollectible" not in key and canBeGenerated(value, SV=SV):
			Game.LegendaryMinions[key] = value
	
	RNGPools = {}
	
	with open("CardPools.py", "w") as out_file:
		#确定RNGPools
		for card in cardPool.values():
			if hasattr(card, "poolIdentifier"):
				identifier, pool = card.generatePool(Game)
				#发现职业法术一定会生成一个职业列表，不会因为生成某个特定职业法术的牌而被跳过
				if isinstance(identifier, list):
					for key, value in zip(identifier, pool):
						RNGPools[key] = value
				else: RNGPools[identifier] = pool
		
		#专门为转校生进行卡池生成
		for card in [TransferStudent_Dragons, TransferStudent_Academy]:
			identifier, pool = card.generatePool(Game)
			if isinstance(identifier, list): #单identifier
				for key, value in zip(identifier, pool):
					RNGPools[key] = value
			else: RNGPools[identifier] = pool
		
		"""只在最后把转校生的类加入pool，假设转校生不会出现在随机生成列表里面"""
		cardPool[transferStudent.index] = transferStudent
		if transferStudent == TransferStudent_Darkmoon:
			cardPool[TransferStudent_Darkmoon.index] = TransferStudent_Darkmoon
		#print(info)
		out_file.write(info)
		
		#把BasicPowers, UpgradedPowers, Classes, ClassesandNeutral, ClassDict写入python里面
		out_file.write("\nBasicPowers = [")
		for power in BasicPowers: out_file.write(power.__name__+", ")
		out_file.write(']\n')
		out_file.write("\nUpgradedPowers = [")
		for power in UpgradedPowers: out_file.write(power.__name__+", ")
		out_file.write(']\n')
		out_file.write("Classes = [")
		for s in Classes: out_file.write("'%s', "%s)
		out_file.write(']\n')
		out_file.write("ClassesandNeutral = [")
		for s in ClassesandNeutral: out_file.write("'%s', "%s)
		out_file.write(']\n')
		out_file.write("ClassDict = {")
		for key, value in ClassDict.items(): out_file.write("'%s': %s, "%(key, value.__name__))
		out_file.write("}\n\n")
		
		#把cardPool写入python里面
		out_file.write("cardPool = {\n")
		for index, obj in cardPool.items():
			out_file.write('\t\t\t"%s": %s,\n'%(index, obj.__name__))
		out_file.write("\t\t}\n\n")
		
		##把MinionswithRace写入python里面
		#out_file.write("MinionswithRace = {\n")
		#for Class, dict in Game.MinionswithRace.items():
		#	out_file.write("\t\t\t'%s': {\n"%Class)
		#	for index, obj in dict.items(): #value is dict
		#		out_file.write('\t\t\t\t"%s": %s,\n'%(index, obj.__name__))
		#	out_file.write("\t\t\t},\n")
		#out_file.write("\t\t\t}\n\n")
		
		#把MinionsofCost写入python里面
		out_file.write("MinionsofCost = {\n")
		for cost, dict in Game.MinionsofCost.items():
			out_file.write("\t\t\t%d: ["%cost)
			i = 1
			for obj in dict.values():
				out_file.write(obj.__name__+", ")
				i += 1
				if i % 10 == 0: out_file.write("\n\t\t\t")
			out_file.write("\t\t\t],\n")
		out_file.write("\t\t}\n")
		
		#把ClassCards写入python里面
		out_file.write("ClassCards = {\n")
		for race, dict in Game.ClassCards.items():
			out_file.write("\t\t\t'%s': {\n"%race)
			for index, obj in dict.items(): #value is dict
				out_file.write('\t\t\t\t"%s": %s,\n'%(index, obj.__name__))
			out_file.write("\t\t\t},\n")
		out_file.write("\t\t\t}\n\n")
		
		#把NeutralCards写入python里面
		out_file.write("NeutralCards = {\n")
		for index, obj in Game.NeutralCards.items():
			out_file.write('\t\t\t"%s": %s,\n'%(index, obj.__name__))
		out_file.write("\t\t}\n\n")
		
		#把RNGPool写入python里面
		out_file.write("RNGPools = {\n")
		for poolIdentifier, objs in RNGPools.items():
			if isinstance(objs, list):
				#出来就休眠的随从现在不能出现在召唤池中
				if poolIdentifier.endswith(" to Summon"):
					try: objs.remove(Magtheridon)
					except: pass
				out_file.write("\t\t'%s': ["%poolIdentifier)
				i = 0
				for obj in objs:
					try: out_file.write(obj.__name__+', ')
					except: out_file.write("'%s', "%obj)
					i += 1
					if i % 10 == 0:
						out_file.write('\n\t\t\t\t')
				out_file.write("],\n")
			elif type(obj) == type({}): #专门给了不起的杰弗里斯提供的
				out_file.write("\t\t\t'%s': {\n"%poolIdentifier)
				for index, value in obj.items():
					out_file.write('\t\t\t\t\t\t"%s": %s,\n'%(index, value.__name__))
				out_file.write("\t\t\t},\n")
		out_file.write("\t\t}")
	
	return board
	
	
def findPicFilepath_Construction(card):
	index, name = card.index, card.__name__
	if not issubclass(card, Hero):
		path = "Images\\%s\\"%index.split('~')[0]
	else: path = "Images\\HerosandPowers\\"
	
	name = name.split("_")[0] if "Mutable" in name else name
	filepath = path + "%s.png"%name
	return filepath
	
class BtnCardAvailable(tk.Button):
	def __init__(self, window, card, SV=0):
		img = PIL.Image.open(findPicFilepath_Construction(card)).resize((225, 300))
		ph = PIL.ImageTk.PhotoImage(img, master=window.displayPanel)
		tk.Button.__init__(self, master=window.displayPanel, image=ph)
		self.window, self.card, self.image = window, card, ph
		self.bind("<Button-1>", self.respond)
		self.deckMax = 40 if SV else 30
		self.SV = SV
		
	def respond(self, event):
		card = self.card
		if len(self.window.cardsinDeck) > self.deckMax-1:
			messagebox.showinfo(message=txt("Your deck is full", CHN))
			return
		numCopies = sum(type == card for type in self.window.cardsinDeck)
		if card.index.startswith("SV_"):
			if numCopies < 3:
				self.window.cardsinDeck.append(self.card)
				if numCopies == 0:
					btn = BtnCardIncluded(self.window, self.card, self.SV)
					btn.pack(fill=tk.X, side=tk.TOP)
					self.window.inDeckDrawn.append(btn)
				else:
					btn = next(btn for btn in self.window.inDeckDrawn if btn.card == card)
					btn.count = numCopies + 1
					btn.config(text=btn.decideText())
				self.window.updateDeckComp()
			else: messagebox.showinfo(message=txt("Can't have >3 copies in the same deck", CHN))
		else:
			if "~Legendary" in card.index:
				if numCopies > 0: messagebox.showinfo(message=txt("Can only have 1 copy of Legendary in the same deck", CHN))
				else:
					self.window.cardsinDeck.append(self.card)
					btn = BtnCardIncluded(self.window, self.card, self.SV)
					btn.pack(fill=tk.X, side=tk.TOP)
					self.window.inDeckDrawn.append(btn)
					self.window.updateDeckComp()
			else:
				if numCopies > 1: messagebox.showinfo(message=txt("Can't have >2 copies in the same deck", CHN))
				else:
					self.window.cardsinDeck.append(self.card)
					if numCopies > 0:
						btn = next(btn for btn in self.window.inDeckDrawn if btn.card == card)
						btn.count = numCopies + 1
						btn.config(text=btn.decideText())
					else:
						btn = BtnCardIncluded(self.window, self.card)
						btn.pack(fill=tk.X, side=tk.TOP)
						self.window.inDeckDrawn.append(btn)
					self.window.updateDeckComp()
		self.window.lbl_Deck.config(text=f"{len(self.window.cardsinDeck)}/{self.deckMax}")
		
	def plot(self, i, j):
		self.grid(row=i, column=j)
		self.window.collectionsDrawn.append(self)
		
class BtnCardIncluded(tk.Button):
	def __init__(self, window, card, SV=0):
		self.count = 1 #画出这张牌的时候就有1计数
		self.window, self.card = window, card
		self.deckMax = 40 if SV else 30
		if len(self.window.inDeckDrawn) < self.deckMax / 2 :
			tk.Button.__init__(self, master=self.window.deckPanel1, text=self.decideText(), font=("Yahei", 11),
								width=20, bg="grey86" if "~Legendary" not in card.index else "gold")
		else:
			tk.Button.__init__(self, master=self.window.deckPanel2, text=self.decideText(), font=("Yahei", 11),
								width=20, bg="grey86" if "~Legendary" not in card.index else "gold")
		self.bind("<Button-1>", self.respond)
		self.bind("<Enter>", self.crosshairEnter)
		self.bind("<Leave>", self.crosshairLeave)
		
	def decideText(self):
		card = self.card
		try: return "{}   {}".format(self.count, card.name if not CHN else card.name_CN)
		except: return "{}   {}".format(self.count, card.name)
		
	def respond(self, event):
		card = self.card
		btn = next((btn for btn in self.window.inDeckDrawn if btn.card == card), None)
		self.window.cardsinDeck.remove(card)
		if btn.count > 1:
			btn.count -= 1
			self.config(text=self.decideText())
		else: btn.destroy()
		self.window.lbl_Deck.config(text=f"{len(self.window.cardsinDeck)}/{self.deckMax}")
		self.window.updateDeckComp()
		
	def crosshairEnter(self, event):
		self.waiting = True
		thread = threading.Thread(target=self.wait2Display, daemon=True)
		thread.start()
		
	def crosshairLeave(self, event):
		self.waiting = False
		try: self.window.lbl_Image.destroy()
		except: pass
		try: self.window.lbl_Text.destroy()
		except: pass
		
	def wait2Display(self):
		time.sleep(0.5)
		if self.waiting:
			try: self.window.lbl_Image.destroy()
			except: pass
			try: self.window.lbl_Text.destroy()
			except: pass
			img = PIL.Image.open(findPicFilepath_Construction(self.card)).resize((240, 320))
			ph = PIL.ImageTk.PhotoImage(img)
			self.window.lbl_Image = tk.Label(self.window.cardInfoPanel)
			self.window.lbl_Image.config(image=ph)
			self.window.lbl_Image.image = ph
			self.window.lbl_Text = tk.Label(self.window.cardInfoPanel, text="Placeholder")
			
			self.window.lbl_Image.pack()
			self.window.lbl_Text.pack()
			
			
numCards4EachRow = 4
manaDistriWidth, manaDistriHeight = 250, 120

class DeckBuilderWindow(tk.Tk):
	def __init__(self, ClassCards, NeutralCards, SV=0):
		tk.Tk.__init__(self)
		self.ClassCards, self.NeutralCards = ClassCards, NeutralCards
		self.Class2Display, self.expansion, self.mana = tk.StringVar(self), tk.StringVar(self), tk.StringVar(self)
		self.cards2Display, self.collectionsDrawn, self.pageNum = {}, [], 0
		self.cardsinDeck, self.inDeckDrawn = [], []
		self.lbl_Image = self.lbl_Text = None
		self.manaObjsDrawn = []
		self.lbl_CardTypes = None
		
		var = tk.IntVar()
		lbl_Class = tk.Label(self, text="Select a class" if not CHN else "选择一个职业", font=("Yahei", 14, "bold"))
		Class2Start = tk.StringVar(self)
		Class2Start.set("Demon Hunter")
		btn_StartBuildDeck = tk.Button(self, text="Start Building Deck"if not CHN else "开始构筑套牌",
										command=lambda: var.set(1), font=("Yahei", 14), bg="green3")
		classOpt = tk.OptionMenu(self, Class2Start, *(list(self.ClassCards.keys())) )
		classOpt.config(width=12, font=("Yahei", 14))
		classOpt["menu"].config(font=("Yahei", 14))
		lbl_Class.grid(row=0, column=0)
		classOpt.grid(row=0, column=1)
		btn_StartBuildDeck.grid(row=0, column=2)
		btn_StartBuildDeck.wait_variable(var)
		#Intialize the interface, based on the class selection
		Class2Start = Class2Start.get()
		lbl_Class.destroy()
		classOpt.destroy()
		btn_StartBuildDeck.destroy()
		self.SV_Class = "craft" in Class2Start
		
		expansions = ["All", "DIY", "Basic", "Classic", "Shadows", "Uldum", "Dragons", "Galakrond", "Initiate", "Outlands", "Academy", "Darkmoon"]
		if SV:
			SV_expansions = ["SV_Basic", "SV_Ultimate", "SV_Uprooted", "SV_Fortune", "SV_Rivayle", "SV_Eternal"]
			expansions.extend(SV_expansions)
		self.init_AllPanels(Class2Start, expansions)
		self.showCards()
		
	def init_AllPanels(self, Class2Start, expansions):
		self.searchPanel = tk.Frame(self)
		self.displayPanel = tk.Frame(self)
		self.deckBtnPanel = tk.Frame(self)
		self.deckManaPanel = tk.Frame(self)
		self.deckPanel1 = tk.Frame(self)
		self.deckPanel2 = tk.Frame(self)
		self.cardInfoPanel = tk.Frame(self)
		self.searchPanel.grid(row=0, column=0)
		self.displayPanel.grid(row=1, column=0, rowspan=2)
		self.deckBtnPanel.grid(row=0, column=1, columnspan=2)
		self.deckManaPanel.grid(row=1, column=1, columnspan=2)
		self.deckPanel1.grid(row=2, column=1)
		self.deckPanel2.grid(row=2, column=2)
		self.cardInfoPanel.grid(row=0, column=14, rowspan=3)
		
		self.init_SearchPanel(Class2Start, expansions)
		self.init_DeckBtnPanel()
		self.init_DeckManaPanel()
		
	def init_SearchPanel(self, Class2Start, expansions):
		self.Class2Display.set(Class2Start)
		self.mana.set("All")
		self.expansion.set("All")
		self.classOpt = tk.OptionMenu(self.searchPanel, self.Class2Display, *([Class2Start, "Neutral"]) )
		self.manaOpt = tk.OptionMenu(self.searchPanel, self.mana, *["All", '0', '1', '2', '3', '4', '5', '6', '7', '7+'])
		self.expansionOpt = tk.OptionMenu(self.searchPanel, self.expansion, *expansions)
		self.classOpt.config(font=("Yahei", 14))
		self.manaOpt.config(font=("Yahei", 14))
		self.expansionOpt.config(font=("Yahei", 14))
		self.classOpt["menu"].config(font=("Yahei", 14))
		self.manaOpt["menu"].config(font=("Yahei", 14))
		self.expansionOpt["menu"].config(font=("Yahei", 14))
		self.search = tk.Entry(self.searchPanel, font=("Yahei", 13), width=20)
		btn_ViewCards = tk.Button(self.searchPanel, text=txt("View Cards", CHN), command=self.showCards, font=("Yahei", 14), bg="green3")
		btn_Left = tk.Button(self.searchPanel, text="Last Page" if not CHN else "上一页", command=self.lastPage, font=("Yahei", 14))
		btn_Right = tk.Button(self.searchPanel, text="Next Page" if not CHN else "下一页", command=self.nextPage, font=("Yahei", 14))
		
		tk.Label(self.searchPanel, text=txt("Class", CHN), font=("Yahei", 13)).grid(row=0, column=0)
		self.classOpt.grid(row=0, column=1)
		tk.Label(self.searchPanel, text=txt("Mana", CHN), font=("Yahei", 13)).grid(row=0, column=2)
		self.manaOpt.grid(row=0, column=3)
		tk.Label(self.searchPanel, text=txt("Expansion", CHN), font=("Yahei", 13)).grid(row=0, column=4)
		self.expansionOpt.grid(row=0, column=5)
		self.search.grid(row=0, column=6)
		btn_ViewCards.grid(row=0, column=7)
		
		tk.Label(self.searchPanel, text="  ", font=("Yahei", 13)).grid(row=0, column=8)
		btn_Left.grid(row=0, column=9)
		btn_Right.grid(row=0, column=10)
		
	def init_DeckBtnPanel(self):
		self.lbl_Deck = tk.Label(self.deckBtnPanel, text="0/40" if self.SV_Class else "0/30", font=("Yahei", 14, "bold"))
		self.lbl_Deck.grid(row=0, column=0)
		tk.Button(self.deckBtnPanel, text="Clear" if not CHN else "清空", font=("Yahei", 14, "bold"), 
					bg="green3", command=lambda : self.clear()).grid(row=0, column=1)
		tk.Button(self.deckBtnPanel, text="Sort by Cost" if not CHN else "按费用排序", font=("Yahei", 14, "bold"), 
					bg="green3", command=lambda : self.sort()).grid(row=0, column=2)
		tk.Button(self.deckBtnPanel, text="Export" if not CHN else "导出", font=("Yahei", 14, "bold"), 
					bg="green3", command=lambda : self.export()).grid(row=0, column=3)
		tk.Label(self.deckBtnPanel, text="Deck Code" if not CHN else "套牌代码", 
					font=("Yahei", 13, "bold")).grid(row=1, column=0, columnspan=2)
		self.deckCode = tk.Entry(self.deckBtnPanel)
		self.deckCode.grid(row=1, column=2, columnspan=2)
		
	def init_DeckManaPanel(self):
		self.lbl_CardTypes = tk.Label(self.deckManaPanel, font=("Yahei", 14), 
							text="Minion:0\nSpell:0\nWeapon:0\nHero:0\nAmulet:0" if not CHN else "随从:0\n法术:0\n武器:0\n英雄牌:0\n护符:0")
		self.manaDistri = tk.Canvas(master=self.deckManaPanel, width=manaDistriWidth, height=manaDistriHeight)
		self.lbl_CardTypes.grid(row=0, column=0)
		self.manaDistri.grid(row=0, column=1)
		for mana in range(8):
			X, Y = (0.125 + 0.1 * mana) * manaDistriWidth, 0.95 * manaDistriHeight
			self.manaDistri.create_text(X, Y, text=str(mana) if mana < 7 else "7+", font=("Yahei", 12, "bold"))
			
	def updateDeckComp(self):
		cardTypes = {"Minion":0, "Spell":0, "Weapon":0, "Hero":0, "Amulet":0}
		for card in self.cardsinDeck:
			if issubclass(card, Minion): cardTypes["Minion"] += 1
			elif issubclass(card, Spell): cardTypes["Spell"] += 1
			elif issubclass(card, Weapon): cardTypes["Weapon"] += 1
			elif issubclass(card, Hero): cardTypes["Hero"] += 1
			#elif issubclass(card, Amulet): cardTypes["Amulet"] += 1
		if not CHN:
			text = "Minion:%d\nSpell:%d\nWeapon:%d\nHero:%d\nAmulet:%d"%(
					cardTypes["Minion"], cardTypes["Spell"], cardTypes["Weapon"], cardTypes["Hero"], cardTypes["Amulet"])
		else:
			text = "随从:%d\n法术:%d\n武器:%d\n英雄牌:%d\n护符:%d"%(
					cardTypes["Minion"], cardTypes["Spell"], cardTypes["Weapon"], cardTypes["Hero"], cardTypes["Amulet"])
		self.lbl_CardTypes.config(text=text)
		for objID in self.manaObjsDrawn: self.manaDistri.delete(objID)
		self.manaObjsDrawn = []
		
		counts = cnt((min(card.mana, 7) for card in self.cardsinDeck))
		most = max(list(counts.values()))
		for key, value in counts.items():
			if value:
				X1, X2 = (0.1 + 0.1 * key) * manaDistriWidth, (0.15 + 0.1 * key) * manaDistriWidth
				Y1, Y2 = (0.88 - 0.75 * (value / most)) * manaDistriHeight, 0.88 * manaDistriHeight
				self.manaObjsDrawn.append(self.manaDistri.create_rectangle(X1, Y1, X2, Y2, fill='gold', width=0))
				self.manaObjsDrawn.append(self.manaDistri.create_text((X1+X2)/2, Y1-0.06*manaDistriHeight, text=str(value), font=("Yahei", 12, "bold")))
				
	def manaCorrect(self, card, mana):
		if mana == "All": return True
		elif mana == "7+": return card.mana > 7
		else: return card.mana == int(mana)
		
	def expansionCorrect(self, index, expansion):
		if expansion == "All": return True
		else: return index.split('~')[0] == expansion
		
	#card here is a class, not an object
	def searchMatches(self, search, card):
		lower = search.lower()
		return (lower in card.name.lower() or lower in card.description.lower()) or search in card.name_CN
		
	def showCards(self):
		self.cards2Display, self.pageNum = {}, 0
		for btn in self.collectionsDrawn: btn.destroy()
		
		Class2Display = self.Class2Display.get()
		mana = self.mana.get()
		expansion = self.expansion.get()
		search = self.search.get()
		if Class2Display == "Neutral": cards = self.NeutralCards
		else: cards = self.ClassCards[Class2Display]
		i, j = 0, -1
		for key, value in cards.items():
			if self.manaCorrect(value, mana) and self.expansionCorrect(key, expansion) \
				and self.searchMatches(search, value):
				if i % (2*numCards4EachRow) == 0:
					j += 1
					self.cards2Display[j] = [value]
				else: self.cards2Display[j].append(value)
				i += 1
		if self.cards2Display: #如果查询结果不为空
			for i, card in enumerate(self.cards2Display[0]):
				btn_Card = BtnCardAvailable(self, card, self.SV_Class)
				btn_Card.plot(0 + i >= numCards4EachRow, i % numCards4EachRow)
		else:
			messagebox.showinfo(message=txt("Your search doesn't have any match", CHN))
			
	def lastPage(self):
		if self.pageNum - 1 in self.cards2Display:
			self.pageNum -= 1
			for btn in self.collectionsDrawn: btn.destroy()
			for i, card in enumerate(self.cards2Display[self.pageNum]):
				btn_Card = BtnCardAvailable(self, card, self.SV_Class)
				btn_Card.plot(0 + i >= numCards4EachRow, i % numCards4EachRow)
		else: messagebox.showinfo(message=txt("Already the first page", CHN))
		
	def nextPage(self):
		if self.pageNum + 1 in self.cards2Display:
			self.pageNum += 1
			for btn in self.collectionsDrawn: btn.destroy()
			for i, card in enumerate(self.cards2Display[self.pageNum]):
				btn_Card = BtnCardAvailable(self, card, self.SV_Class)
				btn_Card.plot(0 + i >= numCards4EachRow, i % numCards4EachRow)
		else: messagebox.showinfo(message=txt("Already the last page", CHN))
		
	def sort(self):
		for btn in self.inDeckDrawn: btn.destroy()
		self.inDeckDrawn = []
		cards_counts = cnt(self.cardsinDeck)
		cards = list(cards_counts.keys())
		indices = np.asarray([card.mana for card in cards]).argsort()
		for i in indices:
			card = cards[i] #Find the correct card in the right order
			btn = BtnCardIncluded(self, card, self.SV_Class)
			btn.count = cards_counts[card]
			btn.config(text=btn.decideText())
			btn.pack(side=tk.TOP)
			self.inDeckDrawn.append(btn)
			
	def clear(self):
		for btn in self.inDeckDrawn: btn.destroy()
		self.cardsinDeck, self.inDeckDrawn = [], []
		self.lbl_Deck.config(text="0/40" if self.SV_Class else "0/30")
		self.updateDeckComp()
		
	def export(self):
		s = "names||"
		for btn in self.inDeckDrawn:
			for i in range(btn.count):
				s += btn.card.name+"||"
		s = s[0:-2]
		print(s)
		self.deckCode.delete(0, tk.END)
		self.deckCode.insert(0, s)
		
		
if __name__ == "__main__":
	SV = 1
	makeCardPool(board="0 Random Game Board", monk=0, SV=SV)
	
	from CustomWidgets import txt, CHN
	from CardPools import ClassCards, NeutralCards
	DeckBuilderWindow(ClassCards, NeutralCards, SV=SV).mainloop()
	