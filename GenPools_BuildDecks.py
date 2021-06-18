from numpy.random import choice as npchoice
from tkinter import messagebox
import tkinter as tk
import PIL.Image, PIL.ImageTk
import numpy as np

def indexHasClass(index, Class):
	return Class in index.split('~')[1]
	
def canBeGenerated(cardType, SV=0):
	return (SV or not cardType.index.startswith("SV_")) and not cardType.description.startswith("Quest:") and \
			not ("Galakrond" in cardType.name or "Galakrond" in cardType.description or "Invoke" in cardType.description or "invoke" in cardType.description) and \
			not "Transfer Student" in cardType.name
			
			
class Pools:
	def __init__(self):
		self.cardPool = {}
		
		
from Core import *
from AcrossPacks import *
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




def makeCardPool(monk=0, SV=0, writetoFile=True):
	cardPool, info = {}, ""
	
	cardPool.update(AcrossPacks_Indices) #Has the basic hero and hero power definitions.
	info += "from AcrossPacks import *\n"
	
	cardPool.update({card.index: card for card in Core_Cards})
	info += "from Core import *\n"
	
	cardPool.update({card.index: card for card in Outlands_Cards})
	info += "from Outlands import *\n"
	
	cardPool.update({card.index: card for card in Academy_Cards})
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
	
	pools = Pools()
	pools.Classes = Classes
	pools.ClassesandNeutral = ClassesandNeutral
	pools.ClassDict = ClassDict
	pools.basicPowers = BasicPowers
	pools.upgradedPowers = UpgradedPowers
	
	#print("SV cards included in card pool:", "SV_Basic~Runecraft~4~3~3~Minion~~Vesper, Witchhunter~Accelerate~Fanfare" in cardPool)
	#cardPool本身需要保留各种祈求牌
	pools.MinionswithRace = {"Beast": {}, "Demon": {}, "Dragon": {}, "Elemental":{},
							"Murloc": {}, "Mech": {}, "Pirate":{}, "Totem": {}}
	if SV:
		SV_Races = ["Officer", "Commander", "Machina", "Natura", "Earth Sigil", "Mysteria", "Artifact", "Levin"]
		for race in SV_Races:
			pools.MinionswithRace[race] = {}
	
	for key, value in cardPool.items(): #Fill MinionswithRace
		if "~Uncollectible" not in key and hasattr(value, "race") and value.race and canBeGenerated(value, SV=SV):
			for race in value.race.split(','):
				pools.MinionswithRace[race][key] = value
	
	pools.MinionsofCost = {}
	for key, value in cardPool.items():
		if "~Minion~" in key and "~Uncollectible" not in key and canBeGenerated(value, SV=SV):
			cost = int(key.split('~')[3])
			try: pools.MinionsofCost[cost][key] = value
			except: pools.MinionsofCost[cost] = {key: value}
	
	pools.ClassCards = {s:{} for s in pools.Classes}
	pools.NeutralCards = {}
	for key, value in cardPool.items():  #Fill NeutralCards
		if "~Uncollectible" not in key and canBeGenerated(value, SV=SV):
			for Class in key.split('~')[1].split(','):
				if Class != "Neutral":
					try: pools.ClassCards[Class][key] = value
					except: print("Failed Class Assignment is ", Class, key, value)
				else: pools.NeutralCards[key] = value
	
	pools.LegendaryMinions = {}
	for key, value in cardPool.items():
		if "~Legendary" in key and "~Minion~" in key and "~Uncollectible" not in key and canBeGenerated(value, SV=SV):
			pools.LegendaryMinions[key] = value
	
	#确定RNGPools
	RNGPools = {}
	for card in cardPool.values():
		if hasattr(card, "poolIdentifier"):
			identifier, pool = card.generatePool(pools)
			#发现职业法术一定会生成一个职业列表，不会因为生成某个特定职业法术的牌而被跳过
			if isinstance(identifier, list):
				for key, value in zip(identifier, pool):
					RNGPools[key] = value
			else: RNGPools[identifier] = pool
	
	#专门为转校生进行卡池生成
	for card in [TransferStudent_Dragons, TransferStudent_Academy]:
		identifier, pool = card.generatePool(pools)
		if isinstance(identifier, list):  #单identifier
			for key, value in zip(identifier, pool):
				RNGPools[key] = value
		else: RNGPools[identifier] = pool
	
	if writetoFile:
		with open("CardPools.py", "w") as out_file:
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
			
			#没有必要把MinionswithRace写入python里面，因为卡池生成某种种族的随从是记录在RNGPool里面的
			
			#把MinionsofCost写入python里面
			out_file.write("MinionsofCost = {\n")
			for cost, dict in pools.MinionsofCost.items():
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
			for race, dict in pools.ClassCards.items():
				out_file.write("\t\t\t'%s': {\n"%race)
				for index, obj in dict.items(): #value is dict
					out_file.write('\t\t\t\t"%s": %s,\n'%(index, obj.__name__))
				out_file.write("\t\t\t},\n")
			out_file.write("\t\t\t}\n\n")
			
			#把NeutralCards写入python里面
			out_file.write("NeutralCards = {\n")
			for index, obj in pools.NeutralCards.items():
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
	
	return cardPool, RNGPools
	
	
from LoadModels import findFilepath

class Label_Card4Pick(tk.Label):
	def __init__(self, master, UI, card):
		self.UI = UI
		img = PIL.Image.open(findFilepath(card(None, 1))).resize((188, 259))
		ph = PIL.ImageTk.PhotoImage(img, master=master)
		super().__init__(master=master, image=ph)
		self.card, self.image = card, ph
		self.bind("<Button-1>", lambda event: self.UI.addCard2Deck(card))
		
		
class Label_CardinDeck(tk.Label):
	def __init__(self, master, UI, card, count=1):
		self.UI, self.card = UI, card
		self.count = count  #画出这张牌的时候就有1计数
		img = PIL.Image.open("Images\\%s\\Icon.png" % card.index.split("~")[0]).resize((30, 30))
		ph = PIL.ImageTk.PhotoImage(img)
		super().__init__(master=master, text=self.decideText(), #"%d  " % card.mana + card.name_CN,
						 font=("Yahei", 15, "bold") if issubclass(card, Minion) else ("Yahei", 15),
						 image=ph, compound=tk.LEFT)
		self.image = ph
		if "~Legendary" in card.index: self.config(bg="gold")
		
		self.bind("<Button-1>", lambda event: self.UI.removeCardfromDeck(card))
		self.bind("<Enter>", lambda event: self.UI.displayCardImg(card))
		#self.bind("<Leave>", lambda event: self.UI.displayCardImg(None))
	
	def decideText(self):
		return "{}  {} {}".format(self.card.mana, self.card.name_CN, ' ' if self.count <= 1 else self.count)


"""A selection panel for the Class"""
class Panel_ClassSelection(tk.Frame):
	def __init__(self, master, UI, ClassPool, Class_0, varName):
		super().__init__(master)
		self.lbls_ClassSelection = []
		self.UI, self.varName = UI, varName
		for i, Class in enumerate(ClassPool):
			lbl_ClassSelection = Label_ClassSelection(panel=self, Class=Class, selected=Class == Class_0)
			lbl_ClassSelection.grid(row=0, column=i)
			self.lbls_ClassSelection.append(lbl_ClassSelection)
	
	def handleSelection(self, Class, invoker):
		for lbl in self.lbls_ClassSelection:
			if lbl != invoker and lbl.selected:
				lbl.selected = False
				img = PIL.Image.open("Images\\Icon_%s.png" % lbl.Class).resize((48, 48) if lbl.selected else (36, 36))
				ph = PIL.ImageTk.PhotoImage(img)
				lbl.image = ph
				lbl.config(image=ph)
		self.UI.__dict__[self.varName] = Class
		self.UI.showCards()
		
class Label_ClassSelection(tk.Label):
	def __init__(self, panel, Class, selected=False):
		self.panel, self.Class = panel, Class
		self.selected = selected
		img = PIL.Image.open("Images\\Icon_%s.png"%Class).resize((48, 48) if self.selected else (36, 36))
		ph = PIL.ImageTk.PhotoImage(img)
		self.image = ph
		super().__init__(master=panel, image=ph)
		self.bind("<Button-1>", self.respond)
		
	def respond(self, event):
		if not self.selected:
			self.selected = True
			img = PIL.Image.open("Images\\Icon_%s.png"%self.Class).resize((48, 48) if self.selected else (36, 36))
			ph = PIL.ImageTk.PhotoImage(img)
			self.image = ph
			self.config(image=ph)
			self.panel.handleSelection(self.Class, invoker=self)
		
		
class Label_ManaSelection(tk.Label):
	def __init__(self, master, UI, mana, selected=False):
		self.UI, self.mana = UI, mana
		img = PIL.Image.open("Images\\EmptyMana.png").resize((24, 24))
		ph = PIL.ImageTk.PhotoImage(img)
		self.image = ph
		super().__init__(master, text=str(mana), image=ph, compound=tk.CENTER, fg="white", font=("Yahei", 15, "bold"))
		self.selected = selected
		self.bind("<Button-1>", self.respond)
		
	def respond(self, event):
		self.selected = not self.selected
		img = PIL.Image.open("Images\\%s.png"%("Mana" if self.selected else "EmptyMana")).resize((36, 36) if self.selected else (24, 24))
		ph = PIL.ImageTk.PhotoImage(img)
		self.image = ph
		self.config(image=ph)
		self.config(fg="green3" if self.selected else "white")
		self.config(font=("Yahei", 21 if self.selected else 15, "bold"))
		if self.selected: self.UI.manasSelected.append(self.mana)
		else: self.UI.manasSelected.remove(self.mana)
		self.UI.showCards()
		
class Label_ExpansionSelection(tk.Label):
	def __init__(self, master, UI, expansion):
		self.UI, self.expansion = UI, expansion
		img = PIL.Image.open("Images\\%s\\Icon.png"%expansion).resize((48, 48))
		ph = PIL.ImageTk.PhotoImage(img)
		self.image = ph
		super().__init__(master, image=ph, compound=tk.CENTER)
		self.selected = False
		self.bind("<Button-1>", self.respond)
	
	def respond(self, event):
		self.selected = not self.selected
		img = PIL.Image.open("Images\\%s\\Icon.png"%self.expansion).resize((64, 64) if self.selected else (48, 48))
		ph = PIL.ImageTk.PhotoImage(img)
		self.image = ph
		self.config(image=ph)
		if self.selected: self.UI.expansionsSelected.append(self.expansion)
		else: self.UI.expansionsSelected.remove(self.expansion)
		self.UI.showCards()


class Label_TurnPage(tk.Label):
	def __init__(self, master, UI, toLeft=True,):
		self.UI, self.toLeft = UI, toLeft
		img = PIL.Image.open("Images\\%s.png"%("LeftArrow" if toLeft else "RightArrow"))#.resize((32, 32))
		ph = PIL.ImageTk.PhotoImage(img)
		self.image = ph
		super().__init__(master, image=ph)
		self.bind("<Button-1>", self.respond)

	def respond(self, event):
		if self.toLeft: self.UI.lastPage()
		else: self.UI.nextPage()
		


		
numCardsEachRow = 4
manaDistriWidth, manaDistriHeight = 250, 120

class DeckBuilderWindow(tk.Tk):
	def __init__(self, ClassCards, NeutralCards, SV=0):
		tk.Tk.__init__(self)
		self.panel_Search = None
		self.panel_Cards4Pick = None
		self.panel_DeckWidgets = None
		self.panel_CardsinDeck = None
		self.stage = 0
		
		self.manasSelected, self.expansionsSelected = [], []
		self.Class2Display = "Demon Hunter"
		
		self.ClassCards, self.NeutralCards = ClassCards, NeutralCards
		self.cards2Display, self.ls_LabelCards4Pick, self.pageNum = {}, [], 0
		self.cardsinDeck, self.ls_LabelCardsinDeck = [], []
		self.lbl_DisplayedCard_Left = self.lbl_DisplayedCard_Right = None
		self.manaObjsDrawn = []
		self.lbl_Types = None
		self.canvas_ManaDistri = None
		
		var = tk.IntVar()
		i = 0
		panel_ClassSelection = Panel_ClassSelection(master=self, UI=self,
								   					ClassPool=("Demon Hunter", "Druid", "Hunter", "Mage", "Paladin",
															   "Priest", "Rogue", "Shaman", "Warlock", "Warrior"),
							 						Class_0="Demon Hunter", varName="Class2Display")
		panel_ClassSelection.grid(row=0, column=0)
		btn_Start = tk.Button(self, text="Start Building Deck" if not CHN else "开始构筑套牌",
							  command=lambda: var.set(1), font=("Yahei", 14), bg="green3")
		btn_Start.grid(row=0, column=1)
		btn_Start.wait_variable(var)
		
		panel_ClassSelection.destroy()
		btn_Start.destroy()
		self.deckMax = 40 if "craft" in self.Class2Display else 30
		self.stage = 1
		expansions = ["All", "DIY", "Basic", "Classic", "Shadows", "Uldum", "Dragons", "Galakrond", "Initiate", "Outlands", "Academy", "Darkmoon"]
		if SV:
			SV_expansions = ["SV_Basic", "SV_Ultimate", "SV_Uprooted", "SV_Fortune", "SV_Rivayle", "SV_Eternal"]
			expansions.extend(SV_expansions)
		self.init_AllPanels(self.Class2Display, expansions)
		self.showCards()
		
	def init_AllPanels(self, Class2Start, expansions):
		self.panel_Search = tk.Frame(self)
		self.panel_Cards4Pick = tk.Frame(self)
		self.panel_DeckWidgets = tk.Frame(self)
		self.panel_CardsinDeck = tk.Frame(self)
		
		self.panel_Search.grid(row=0, column=0)
		self.panel_Cards4Pick.grid(row=1, column=0, columnspan=2)
		self.panel_DeckWidgets.grid(row=0, column=1)
		self.panel_CardsinDeck.grid(row=1, column=2)
		panel_DisplayCard_Right = tk.Frame(self)
		panel_DisplayCard_Right.grid(row=0, column=2)
		self.lbl_DisplayedCard_Right = tk.Label(panel_DisplayCard_Right)
		self.lbl_DisplayedCard_Right.grid(row=0, column=3, rowspan=3)
		
		self.init_SearchPanel(Class2Start, expansions)
		self.init_DeckWidgetsPanel()
		
	def init_SearchPanel(self, Class2Start, expansions):
		Panel_ClassSelection(master=self.panel_Search, UI=self,
							 ClassPool=(Class2Start, "Neutral"), Class_0=Class2Start,
							 varName="Class2Display").grid(row=0, column=0)
		for i, mana in enumerate(("0", "1", '2', '3', '4', '5', '6', '7+')):
			Label_ManaSelection(self.panel_Search, self, mana).grid(row=0, column=2+i)
		
		panel_Expansions = tk.Frame(self.panel_Search)
		panel_Expansions.grid(row=1, column=0, columnspan=10)
		for i, expansion in enumerate(("CORE", "BLACK_TEMPLE", "SCHOLOMANCE", "DARKMOON_FAIRE", "THE_BARRENS")):
			Label_ExpansionSelection(panel_Expansions, self, expansion).grid(row=0, column=i)
			
		panel_EntrySearch = tk.Frame(self.panel_Search)
		panel_EntrySearch.grid(row=2, column=0, columnspan=10)
		ph = PIL.ImageTk.PhotoImage(PIL.Image.open("Images\\Search.png").resize((32, 32)) )
		lbl_SearchIcon = tk.Label(panel_EntrySearch, image=ph)
		lbl_SearchIcon.image = ph
		lbl_SearchIcon.grid(row=0, column=0)
		self.entry_Search = tk.Entry(panel_EntrySearch, font=("Yahei", 13), width=40)
		self.entry_Search.bind("<Return>", lambda event: self.showCards())
		self.entry_Search.grid(row=0, column=2)
		self.lbl_DisplayedCard_Left = tk.Label(panel_EntrySearch)
		self.lbl_DisplayedCard_Left.grid(row=1, column=0, columnspan=2)
		
		tk.Label(self.panel_Search, text="  ", font=("Yahei", 13)).grid(row=2, column=0)
		Label_TurnPage(self.panel_Cards4Pick, self, toLeft=True).grid(row=0, column=0, rowspan=2)
		Label_TurnPage(self.panel_Cards4Pick, self, toLeft=False).grid(row=0, column=5, rowspan=2)
		
	def init_DeckWidgetsPanel(self):
		self.lbl_Deck = tk.Label(self.panel_DeckWidgets, text="0/%d" % self.deckMax, font=("Yahei", 14, "bold"))
		self.lbl_Deck.grid(row=0, column=0)
		tk.Button(self.panel_DeckWidgets, text="Clear" if not CHN else "清空", font=("Yahei", 14, "bold"),
				  bg="green3", command=self.clear).grid(row=0, column=1)
		#tk.Button(self.panel_DeckWidgets, text="Sort by Cost" if not CHN else "按费用排序", font=("Yahei", 14, "bold"),
		#		  bg="green3", command=lambda: self.sort()).grid(row=0, column=2)
		tk.Button(self.panel_DeckWidgets, text="Export" if not CHN else "导出", font=("Yahei", 14, "bold"),
				  bg="green3", command=self.export).grid(row=0, column=2)
		tk.Label(self.panel_DeckWidgets, text="Deck Code" if not CHN else "套牌代码",
				 font=("Yahei", 13, "bold")).grid(row=1, column=0)
		self.deckCode = tk.Entry(self.panel_DeckWidgets, width=30)
		self.deckCode.grid(row=1, column=1, columnspan=2)
		
		self.lbl_Types = tk.Label(self.panel_DeckWidgets, font=("Yahei", 14),
							text="Minion:0\nSpell:0\nWeapon:0\nHero:0\nAmulet:0" if not CHN else "随从:0\n法术:0\n武器:0\n英雄牌:0\n护符:0")
		self.canvas_ManaDistri = tk.Canvas(master=self.panel_DeckWidgets, width=manaDistriWidth, height=manaDistriHeight)
		self.lbl_Types.grid(row=2, column=0)
		self.canvas_ManaDistri.grid(row=2, column=1, columnspan=2)
		for mana in range(8):
			X, Y = (0.125 + 0.1 * mana) * manaDistriWidth, 0.95 * manaDistriHeight
			self.canvas_ManaDistri.create_text(X, Y, text=str(mana) if mana < 7 else "7+", font=("Yahei", 12, "bold"))
			
	def addCard2Deck(self, card):
		numCopies = self.cardsinDeck.count(card)
		if len(self.cardsinDeck) >= self.deckMax:
			messagebox.showinfo(message=txt("Your deck is full", CHN))
		elif card.index.startswith("SV_") and numCopies >= 2:
			messagebox.showinfo(message=txt("Can't have >3 copies in the same deck", CHN))
		elif not card.index.startswith("SV_") and "~Legendary" in card.index and numCopies >= 1:
			messagebox.showinfo(message=txt("Can only have 1 copy of Legendary in the same deck", CHN))
		elif not card.index.startswith("SV_") and "~Legendary" not in card.index and numCopies > 1:
			messagebox.showinfo(message=txt("Can't have >2 copies in the same deck", CHN))
		else:
			self.cardsinDeck.append(card)
			self.updateDeckLabels()
			self.updateDeckComp()
			
	def removeCardfromDeck(self, card):
		try:
			self.cardsinDeck.remove(card)
			self.updateDeckLabels()
			self.updateDeckComp()
		except: pass
		
	def displayCardImg(self, card):
		return
		if card:
			img = PIL.Image.open(findFilepath(card(None, 1)))
			ph = PIL.ImageTk.PhotoImage(img)
			if onLeft:
				self.lbl_DisplayedCard_Right.config(image=ph)
				self.lbl_DisplayedCard_Left.image = ph
				#self..config(image=None)
			else:
				self.lbl_DisplayedCard_Right.config(image=ph)
				self.lbl_DisplayedCard_Right.image = ph
				self.lbl_DisplayedCard_Left.config(image=None)
		else:
			self.lbl_DisplayedCard_Left.config(image=None)
			self.lbl_DisplayedCard_Right.config(image=None)
		
	def updateDeckLabels(self):
		for lbl in self.ls_LabelCardsinDeck: lbl.destroy()
		dict_CardsCounts = {card: self.cardsinDeck.count(card) for card in self.cardsinDeck}
		cards = list(dict_CardsCounts.keys())
		indices_ArgSort = np.array([card.mana for card in cards]).argsort()
		for i, index in enumerate(indices_ArgSort):
			card = cards[index]
			count = dict_CardsCounts[card]
			lbl_CardinDeck = Label_CardinDeck(self.panel_CardsinDeck, self, card, count)
			self.ls_LabelCardsinDeck.append(lbl_CardinDeck)
			lbl_CardinDeck.grid(row=i % 15, column=int(i / 15))
			
	def updateDeckComp(self):
		self.lbl_Deck.config(text="%d/%d"%(len(self.cardsinDeck), self.deckMax))
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
		self.lbl_Types.config(text=text)
		for objID in self.manaObjsDrawn: self.canvas_ManaDistri.delete(objID)
		self.manaObjsDrawn = []
		
		manas = [min(card.mana, 7) for card in self.cardsinDeck]
		counts = {mana: manas.count(mana) for mana in range(1, 7)}
		most = max(list(counts.values()))
		for key, value in counts.items():
			if value:
				X1, X2 = (0.1 + 0.1 * key) * manaDistriWidth, (0.15 + 0.1 * key) * manaDistriWidth
				Y1, Y2 = (0.88 - 0.75 * (value / most)) * manaDistriHeight, 0.88 * manaDistriHeight
				self.manaObjsDrawn.append(self.canvas_ManaDistri.create_rectangle(X1, Y1, X2, Y2, fill='gold', width=0))
				self.manaObjsDrawn.append(self.canvas_ManaDistri.create_text((X1+X2)/2, Y1-0.06*manaDistriHeight, text=str(value), font=("Yahei", 12, "bold")))
				
	def manaCorrect(self, card, manasSelected):
		#If manasSelect is empty, return True
		return not manasSelected or ("7+" in manasSelected and card.mana > 7) or (str(card.mana) in manasSelected)
		
	def expansionCorrect(self, index, expansionsSelected):
		#If expansionsSelected, return True
		return not expansionsSelected or index.split('~')[0] in expansionsSelected
		
	#card here is a class, not an object
	def searchMatches(self, search, card):
		lower = search.lower()
		return (lower in card.name.lower() or lower in card.description.lower()) or search in card.name_CN
		
	def showCards(self):
		if self.stage < 1: return
		self.cards2Display, self.pageNum = {}, 0
		for btn in self.ls_LabelCards4Pick: btn.destroy()
		
		search = self.entry_Search.get()
		if self.Class2Display == "Neutral": cards = self.NeutralCards
		else: cards = self.ClassCards[self.Class2Display]
		i, j = 0, -1
		for key, value in cards.items():
			if self.manaCorrect(value, self.manasSelected) and self.expansionCorrect(key, self.expansionsSelected) \
				and self.searchMatches(search, value):
				if i % (2*numCardsEachRow) == 0:
					j += 1
					self.cards2Display[j] = [value]
				else: self.cards2Display[j].append(value)
				i += 1
		if self.cards2Display: #如果查询结果不为空
			for i, card in enumerate(self.cards2Display[0]):
				lbl_Card4Pick = Label_Card4Pick(self.panel_Cards4Pick, self, card)
				lbl_Card4Pick.grid(row=0 + i >= numCardsEachRow, column=1 + i % numCardsEachRow)
				self.ls_LabelCards4Pick.append(lbl_Card4Pick)
		else:
			messagebox.showinfo(message=txt("Your search doesn't have any match", CHN))
			
	def lastPage(self):
		if self.pageNum - 1 in self.cards2Display:
			self.pageNum -= 1
			for btn in self.ls_LabelCards4Pick: btn.destroy()
			for i, card in enumerate(self.cards2Display[self.pageNum]):
				lbl_Card4Pick = Label_Card4Pick(self.panel_Cards4Pick, self, card)
				self.ls_LabelCards4Pick.append(lbl_Card4Pick)
				lbl_Card4Pick.grid(row=0 + i >= numCardsEachRow, column=1 + i % numCardsEachRow)
		else: messagebox.showinfo(message=txt("Already the first page", CHN))
		
	def nextPage(self):
		if self.pageNum + 1 in self.cards2Display:
			self.pageNum += 1
			for btn in self.ls_LabelCards4Pick: btn.destroy()
			for i, card in enumerate(self.cards2Display[self.pageNum]):
				lbl_Card4Pick = Label_Card4Pick(self.panel_Cards4Pick, self, card)
				self.ls_LabelCards4Pick.append(lbl_Card4Pick)
				lbl_Card4Pick.grid(row=0 + i >= numCardsEachRow, column=1 + i % numCardsEachRow)
		else: messagebox.showinfo(message=txt("Already the last page", CHN))
		
	def clear(self):
		for lbl in self.ls_LabelCardsinDeck: lbl.destroy()
		self.cardsinDeck, self.ls_LabelCardsinDeck = [], []
		self.updateDeckComp()
		
	def export(self):
		s = "names||"
		for btn in self.ls_LabelCardsinDeck:
			for i in range(btn.count):
				s += btn.card.name+"||"
		s = s[0:-2]
		print(s)
		self.deckCode.delete(0, tk.END)
		self.deckCode.insert(0, s)
		
		
if __name__ == "__main__":
	SV = 1
	makeCardPool(monk=0, SV=SV)
	
	from CustomWidgets import txt, CHN
	from CardPools import ClassCards, NeutralCards
	NeutralCards.update({"SCHOLOMANCE~Neutral~Minion~2~2~2~~Transfer Student~Vanilla": TransferStudent})
	DeckBuilderWindow(ClassCards, NeutralCards, SV=SV).mainloop()
	