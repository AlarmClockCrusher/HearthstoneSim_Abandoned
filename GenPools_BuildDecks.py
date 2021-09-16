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


translateTable = {"Loading. Please wait": "正在加载模型，请等待",
				 	"Hero 1 class": "选择玩家1的职业",
				 	"Hero 2 class": "选择玩家2的职业",
				 	"Enter Deck 1 code": "输入玩家1套牌代码",
				 	"Enter Deck 2 code": "输入玩家2的套牌代码",
				 	"Deck 1 incorrect": "玩家1的套牌代码有误",
				 	"Deck 2 incorrect": "玩家2的套牌代码有误",
				 	"Deck 1&2 incorrect": "玩家1与玩家2的套牌代码均有误",
				 	"Finished Loading. Start!": "加载完成，可以开始",
					"Go Back to Layer 1": "返回游戏初始UI",
				 
					"Server IP Address": "服务器IP地址",
					"Query Port": "接入端口",
					"Table ID to join": "想要加入的牌桌ID",
					"Hero class": "选择你的职业",
					"Enter Deck code": "输入你的套牌代码",
					"Resume interrupted game": "返回中断的游戏",
	
					"Deck incorrect": "你的套牌代码不正确，请检查后重试",
					"Can't ping the address ": "无法ping通给出的服务器IP地址",
					"Can't connect to the server's query port": "无法连接到给出的服务器接入端口",
					"Can't connect to the server's port": "无法连接到给出的牌桌",
					"No tables left. Please wait for openings": "没有空桌子了，请等待空出",
					"This table ID is already taken": "本桌子目前已有两个玩家",
					"Successfully reserved a table": "已成功预订一张桌子",

					"Connection is lost": "连接断开了",
					"Opponent disconnected. Closing": "对方断开了连接。强制关闭",
					"Wait for Opponent to Reconnect: ": "等待对方重新连接：",
					"Opponent failed to reconnect.\nClosing in 2 seconds": "对方未能重新连接\n2秒后退出",
					"Receiving Game Copies from Opponent: ": "正在接收对方保存的游戏当前进度：",
				  
				  	"Player 1 Conceded!": "玩家1认输了",
				  	"Player 2 Conceded!": "玩家2认输了",
				  }

CHN = True

def txt(text, CHN):
	if CHN: return text
	try: return translateTable[text]
	except: return text


class Pools:
	def __init__(self):
		self.cardPool = {}
		
		
from Core import *
from AcrossPacks import *
from Outlands import *
from Academy import *
from Darkmoon import *
from Barrens import *
from Stormwind import *

#from SV_Basic import *
#from SV_Ultimate import *
#from SV_Uprooted import *
#from SV_Fortune import *
#from SV_Rivayle import *
#from SV_Eternal import *




def makeCardPool(monk=0, SV=0, writetoFile=True):
	cardPool, info = [], ""
	
	cardPool += AcrossPacks_Cards #Has the basic hero and hero power definitions.
	info += "from AcrossPacks import *\n"
	
	cardPool += Core_Cards
	info += "from Core import *\n"
	
	cardPool += Outlands_Cards
	info += "from Outlands import *\n"
	
	cardPool += Academy_Cards
	info += "from Academy import *\n"
	
	cardPool += Darkmoon_Cards
	info += "from Darkmoon import *\n"
	
	cardPool += Barrens_Cards
	info += "from Barrens import *\n"
	
	cardPool += Stormwind_Cards
	info += "from Stormwind import *\n"
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
	
	BasicPowers, UpgradedPowers, Classes, ClassesandNeutral, Class2HeroDict = [], [], [], [], {}
	for card in cardPool[:]:
		if card.type == "Hero" and "~" not in card.index:
			Classes.append(card.Class)
			ClassesandNeutral.append(card.Class)
			Class2HeroDict[card.Class] = card
			cardPool.remove(card)
		elif card.type == "Power":
			if "~Upgraded Hero Power~" in card.index: UpgradedPowers.append(card)
			elif "~Basic Hero Power~" in card.index: BasicPowers.append(card)
			cardPool.remove(card)
	
	ClassesandNeutral.append("Neutral")
	
	pools = Pools()
	pools.Classes = Classes
	pools.ClassesandNeutral = ClassesandNeutral
	pools.Class2HeroDict = Class2HeroDict
	pools.basicPowers = BasicPowers
	pools.upgradedPowers = UpgradedPowers
	
	#print("SV cards included in card pool:", "SV_Basic~Runecraft~4~3~3~Minion~~Vesper, Witchhunter~Accelerate~Fanfare" in cardPool)
	#cardPool本身需要保留各种祈求牌
	pools.MinionsofCost = {}
	pools.MinionswithRace = {"Beast": [], "Demon": [], "Dragon": [], "Elemental":[],
							"Murloc": [], "Mech": [], "Pirate":[], "Quilboar": [], "Totem": []}
	if SV:
		SV_Races = ["Officer", "Commander", "Machina", "Natura", "Earth Sigil", "Mysteria", "Artifact", "Levin"]
		for race in SV_Races:
			pools.MinionswithRace[race] = []
	
	pools.ClassCards = {s: [] for s in pools.Classes}
	pools.NeutralCards = []
	pools.LegendaryMinions = []
	
	for card in cardPool: #Fill MinionswithRace
		if "~Uncollectible" not in card.index and canBeGenerated(card, SV=SV):
			if card.type == "Minion":
				if card.race:
					for race in card.race.split(','):
						pools.MinionswithRace[race].append(card)
				try: pools.MinionsofCost[card.mana].append(card)
				except KeyError: pools.MinionsofCost[card.mana] = [card]
				if "~Legendary" in card.index: pools.LegendaryMinions.append(card)
			for Class in card.Class.split(','):
				if Class != "Neutral": pools.ClassCards[Class].append(card)
				else: pools.NeutralCards.append(card)
				
	#确定RNGPools
	RNGPools = {"Classes": ['Demon Hunter', 'Hunter', 'Rogue', 'Druid', 'Warrior', 'Paladin', 'Shaman', 'Mage', 'Priest', 'Warlock', ]}
	for card in cardPool:
		if hasattr(card, "poolIdentifier"):
			identifier, pool = card.generatePool(pools)
			#发现职业法术一定会生成一个职业列表，不会因为生成某个特定职业法术的牌而被跳过
			if isinstance(identifier, (list, tuple)):
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
			
			#把BasicPowers, UpgradedPowers, Classes, ClassesandNeutral, Class2HeroDict写入python里面
			#out_file.write("\nBasicPowers = [")
			#for power in BasicPowers: out_file.write(power.__name__+", ")
			#out_file.write(']\n')
			#out_file.write("\nUpgradedPowers = [")
			#for power in UpgradedPowers: out_file.write(power.__name__+", ")
			#out_file.write(']\n')
			#out_file.write("Classes = [")
			#for s in Classes: out_file.write("'%s', "%s)
			#out_file.write(']\n')
			#out_file.write("ClassesandNeutral = [")
			#for s in ClassesandNeutral: out_file.write("'%s', "%s)
			#out_file.write(']\n')
			out_file.write("Class2HeroDict = {")
			for key, value in Class2HeroDict.items(): out_file.write("'%s': %s, "%(key, value.__name__))
			out_file.write("}\n\n")
			
			#把cardPool写入python里面
			#out_file.write("cardPool = [")
			#i = 1
			#for card in cardPool:
			#	out_file.write('%s, '%card.__name__)
			#	if i % 10 == 0: out_file.write('\n\t\t\t')
			#	i += 1
			#out_file.write("\t\t]\n\n")
			
			#把ClassCards写入python里面
			out_file.write("ClassCards = {")
			for Class, ls in pools.ClassCards.items():
				out_file.write("\t\t\t'%s': ["%Class)
				i = 1
				for card in ls: #value is dict
					out_file.write('%s, '%card.__name__)
					if i % 10 == 0: out_file.write('\n\t\t\t\t')
					i += 1
				out_file.write("\t\t\t],\n")
			out_file.write("\t\t\t}\n\n")
			
			#把NeutralCards写入python里面
			out_file.write("NeutralCards = [\n")
			i = 1
			for card in pools.NeutralCards:
				out_file.write('%s, '%card.__name__)
				if i % 10 == 0: out_file.write('\n\t\t')
				i += 1
			out_file.write("\n]\n\n")
			
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
						if i % 10 == 0: out_file.write('\n\t\t\t\t\t\t')
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
		self.image = ph
		super().__init__(master=master, text=self.decideText(), #"%d  " % card.mana + card.name_CN,
						 font=("Yahei", 15, "bold") if card.type == "Minion" else ("Yahei", 15),
						 image=ph, compound=tk.LEFT)
		if "~Legendary" in card.index: self.config(bg="gold")
		
		self.bind("<Button-1>", lambda event: self.UI.removeCardfromDeck(card))
		self.bind("<Enter>", lambda event: self.UI.displayCardImg(card))
		#self.bind("<Leave>", lambda event: self.UI.displayCardImg(None))
	
	def decideText(self):
		return "{}  {} {}".format(self.card.mana, self.card.name_CN, ' ' if self.count <= 1 else self.count)


"""A selection panel for the Class"""
numClassIcons_perRow = 5
dict_Class2HeroName = {'Demon Hunter': "Illidan", 'Hunter': 'Rexxar', 'Rogue': 'Valeera', 'Druid': "Malfurion", 'Warrior': 'Garrosh',
					   'Paladin': "Uther", 'Shaman': 'Thrall', 'Mage': 'Jaina', 'Priest': 'Anduin', 'Warlock': 'Guldan', }

class Panel_ClassSelection(tk.Frame):
	def __init__(self, master, UI, ClassPool, Class_0, varName):
		super().__init__(master)
		self.lbls_ClassSelection = []
		self.selectedClass = Class_0
		self.UI, self.varName = UI, varName
		
		img = PIL.Image.open("Images\\HeroesandPowers\\%s.png"%dict_Class2HeroName[Class_0]).resize((48, int(48*395/286)))
		ph = PIL.ImageTk.PhotoImage(img, master=self)
		self.lbl_SelectedClass = tk.Label(self)
		self.lbl_SelectedClass.image = ph
		self.lbl_SelectedClass.config(image=ph)
		self.lbl_SelectedClass.grid(row=0, column=numClassIcons_perRow, rowspan=5)
		for i, Class in enumerate(ClassPool):
			lbl_ClassSelection = Label_ClassSelection(panel=self, Class=Class)
			lbl_ClassSelection.grid(row=int(i/numClassIcons_perRow), column=i%numClassIcons_perRow)
			self.lbls_ClassSelection.append(lbl_ClassSelection)
	
	def setSelection(self, Class):
		self.selectedClass = Class
		img = PIL.Image.open("Images\\HeroesandPowers\\%s.png"%dict_Class2HeroName[Class]).resize((96, int(96 * 395 / 286)))
		ph = PIL.ImageTk.PhotoImage(img)
		self.lbl_SelectedClass.image = ph
		self.lbl_SelectedClass.config(image=ph)
		self.UI.__dict__[self.varName] = Class
		self.UI.showCards()
		
class Label_ClassSelection(tk.Label):
	def __init__(self, panel, Class):
		super().__init__(master=panel)
		self.panel, self.Class = panel, Class
		img = PIL.Image.open("Images\\Icon_%s.png"%Class).resize((48, 48))
		ph = PIL.ImageTk.PhotoImage(img, master=panel)
		self.image = ph
		self.config(image=ph)
		self.bind("<Button-1>", lambda event: self.panel.setSelection(self.Class))
		
		
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
		ph = PIL.ImageTk.PhotoImage(PIL.Image.open("Images\\%s.png"%("LeftArrow" if toLeft else "RightArrow")))
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
		expansions = ["All", "DIY", "Basic", "Classic", "Shadows", "Initiate", "Outlands", "Academy", "Darkmoon", "Barrens", "Stormwind"]
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
		for i, expansion in enumerate(("CORE", "BLACK_TEMPLE", "SCHOLOMANCE", "DARKMOON_FAIRE", "THE_BARRENS", "STORMWIND")):
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
							text="Total:0\n\nMinion:0\nSpell:0\nWeapon:0\nHero:0\nAmulet:0" if not CHN else "总计:0\n\n随从:0\n法术:0\n武器:0\n英雄牌:0\n护符:0")
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
		for card in cards:
			if self.manaCorrect(card, self.manasSelected) and self.expansionCorrect(card.index, self.expansionsSelected) \
				and self.searchMatches(search, card):
				if i % (2*numCardsEachRow) == 0:
					j += 1
					self.cards2Display[j] = [card]
				else: self.cards2Display[j].append(card)
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
	
	from CardPools import ClassCards, NeutralCards
	#NeutralCards.update({"SCHOLOMANCE~Neutral~Minion~2~2~2~~Transfer Student~Vanilla": TransferStudent})
	DeckBuilderWindow(ClassCards, NeutralCards, SV=SV).mainloop()
	