from numpy.random import choice as npchoice
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


from CardTypes import Hero
from Basic import *
from Classic import *
from AcrossPacks import *
from DemonHunterInitiate import *
from Outlands import *
from Academy import *
from Darkmoon import *

from Monk import *
from SV_Basic import *
from SV_Ultimate import *
from SV_Uprooted import *
from SV_Fortune import *
from SV_Rivayle import *
from SV_Eternal import *


def makeCardPool(board="0 Random Game Board", monk=0, SV=0):
	cardPool, info = {}, ""
	
	cardPool.update(Basic_Indices)
	info += "from Basic import *\n"
	
	cardPool.update(Classic_Indices)
	info += "from Classic import *\n"
	
	cardPool.update(AcrossPacks_Indices)
	info += "from AcrossPacks import *\n"
	
	cardPool.update(DemonHunterInit_Indices)
	info += "from DemonHunterInitiate import *\n"
	
	cardPool.update(Outlands_Indices)
	info += "from Outlands import *\n"
	
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
						   "20 Dalaran": TransferStudent_Shadows,
						   "21 Uldum Desert": TransferStudent_UldumDesert,
						   "22 Uldum Oasis": TransferStudent_UldumOasis,
						   "23 Dragons": TransferStudent_Dragons,
						   "24 Outlands": TransferStudent_Outlands,
						   "25 Scholomance Academy": TransferStudent_Academy,
						   "26 Darkmoon Faire": TransferStudent_Darkmoon,
						   }
	if board == "0 Random Game Board": board = npchoice(list(transferStudentPool))
	transferStudent = transferStudentPool[board]
	Academy_Indices[transferStudent.index] = transferStudent
	cardPool.update(Academy_Indices)
	info += "from Academy import *\n"
	
	cardPool.update(Darkmoon_Indices)
	info += "from Darkmoon import *\n"
	
	if monk:
		print("Including Monk")
		cardPool.update(Monk_Indices)
		info += "from Monk import *\n"
	
	if SV:
		cardPool.update(SV_Basic_Indices)
		info += "from SV_Basic import *\n"
		
		cardPool.update(SV_Ultimate_Indices)
		info += "from SV_Ultimate import *\n"
		
		cardPool.update(SV_Uprooted_Indices)
		info += "from SV_Uprooted import *\n"
		
		cardPool.update(SV_Fortune_Indices)
		info += "from SV_Fortune import *\n"
		
		cardPool.update(SV_Rivayle_Indices)
		info += "from SV_Rivayle import *\n"
		
		cardPool.update(SV_Eternal_Indices)
		info += "from SV_Eternal import *\n"
	
	BasicPowers, UpgradedPowers, Classes, ClassesandNeutral, ClassDict = [], [], [], [], {}
	for key in list(cardPool.keys()):
		if "Hero: " in key:
			Class = key.split(":")[1].strip()
			Classes.append(Class)
			ClassesandNeutral.append(Class)
			ClassDict[Class] = cardPool[key]
			del cardPool[key]
		elif " Hero Power~" in key:
			if "~Upgraded Hero Power~" in key:
				UpgradedPowers.append(cardPool[key])
			else:
				BasicPowers.append(cardPool[key])
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
	Game.MinionswithRace = {"Beast": {}, "Demon": {}, "Dragon": {}, "Elemental": {},
							"Murloc": {}, "Mech": {}, "Pirate": {}, "Totem": {}}
	if SV:
		SV_Races = ["Officer", "Commander", "Machina", "Natura", "Earth Sigil", "Mysteria", "Artifact", "Levin"]
		for race in SV_Races:
			Game.MinionswithRace[race] = {}
	
	for key, value in Game.cardPool.items():  #Fill MinionswithRace
		if "~Uncollectible" not in key and hasattr(value, "race") and value.race and canBeGenerated(value, SV=SV):
			for race in value.race.split(','):
				Game.MinionswithRace[race][key] = value
	
	Game.MinionsofCost = {}
	for key, value in Game.cardPool.items():
		if "~Minion~" in key and "~Uncollectible" not in key and canBeGenerated(value, SV=SV):
			cost = int(key.split('~')[3])
			try:
				Game.MinionsofCost[cost][key] = value
			except:
				Game.MinionsofCost[cost] = {key: value}
	
	Game.ClassCards = {s: {} for s in Game.Classes}
	Game.NeutralCards = {}
	for key, value in Game.cardPool.items():  #Fill NeutralCards
		if "~Uncollectible" not in key and canBeGenerated(value, SV=SV):
			for Class in key.split('~')[1].split(','):
				if Class != "Neutral":
					try:
						Game.ClassCards[Class][key] = value
					except:
						print("Failed Class Assignment is ", Class, key, value)
				else:
					Game.NeutralCards[key] = value
	
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
				else:
					RNGPools[identifier] = pool
		
		#专门为转校生进行卡池生成
		for card in [TransferStudent_Dragons, TransferStudent_Academy]:
			identifier, pool = card.generatePool(Game)
			if isinstance(identifier, list):  #单identifier
				for key, value in zip(identifier, pool):
					RNGPools[key] = value
			else:
				RNGPools[identifier] = pool
		
		#print(info)
		out_file.write(info)
		
		#把BasicPowers, UpgradedPowers, Classes, ClassesandNeutral, ClassDict写入python里面
		out_file.write("\nBasicPowers = [")
		for power in BasicPowers: out_file.write(power.__name__ + ", ")
		out_file.write(']\n')
		out_file.write("\nUpgradedPowers = [")
		for power in UpgradedPowers: out_file.write(power.__name__ + ", ")
		out_file.write(']\n')
		out_file.write("Classes = [")
		for s in Classes: out_file.write("'%s', " % s)
		out_file.write(']\n')
		out_file.write("ClassesandNeutral = [")
		for s in ClassesandNeutral: out_file.write("'%s', " % s)
		out_file.write(']\n')
		out_file.write("ClassDict = {")
		for key, value in ClassDict.items(): out_file.write("'%s': %s, " % (key, value.__name__))
		out_file.write("}\n\n")
		
		#把cardPool写入python里面
		out_file.write("cardPool = {\n")
		for index, obj in cardPool.items():
			out_file.write('\t\t\t"%s": %s,\n' % (index, obj.__name__))
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
			out_file.write("\t\t\t%d: [" % cost)
			i = 1
			for obj in dict.values():
				out_file.write(obj.__name__ + ", ")
				i += 1
				if i % 10 == 0: out_file.write("\n\t\t\t")
			out_file.write("\t\t\t],\n")
		out_file.write("\t\t}\n")
		
		#把ClassCards写入python里面
		out_file.write("ClassCards = {\n")
		for race, dict in Game.ClassCards.items():
			out_file.write("\t\t\t'%s': {\n" % race)
			for index, obj in dict.items():  #value is dict
				out_file.write('\t\t\t\t"%s": %s,\n' % (index, obj.__name__))
			out_file.write("\t\t\t},\n")
		out_file.write("\t\t\t}\n\n")
		
		#把NeutralCards写入python里面
		out_file.write("NeutralCards = {\n")
		for index, obj in Game.NeutralCards.items():
			out_file.write('\t\t\t"%s": %s,\n' % (index, obj.__name__))
		out_file.write("\t\t}\n\n")
		
		#把RNGPool写入python里面
		out_file.write("RNGPools = {\n")
		for poolIdentifier, objs in RNGPools.items():
			if isinstance(objs, list):
				#出来就休眠的随从现在不能出现在召唤池中
				if poolIdentifier.endswith(" to Summon"):
					try:
						objs.remove(Magtheridon)
					except:
						pass
				out_file.write("\t\t'%s': [" % poolIdentifier)
				i = 0
				for obj in objs:
					try:
						out_file.write(obj.__name__ + ', ')
					except:
						out_file.write("'%s', " % obj)
					i += 1
					if i % 10 == 0:
						out_file.write('\n\t\t\t\t')
				out_file.write("],\n")
			elif type(obj) == type({}):  #专门给了不起的杰弗里斯提供的
				out_file.write("\t\t\t'%s': {\n" % poolIdentifier)
				for index, value in obj.items():
					out_file.write('\t\t\t\t\t\t"%s": %s,\n' % (index, value.__name__))
				out_file.write("\t\t\t},\n")
		out_file.write("\t\t}")
	
	return board, transferStudent


def findPicFilepath_Construction(card):
	index, name = card.index, card.__name__
	if not issubclass(card, Hero):
		folderName = folderNameTable[index.split('~')[0]]
		path = "Images\\%s\\" % folderName
	else:
		path = "Images\\HerosandPowers\\"
	
	name = name.split("_")[0] if "Mutable" in name else name
	filepath = path + "%s.png" % name
	return filepath


from direct.gui.OnscreenText import OnscreenText
from direct.gui.OnscreenImage import OnscreenImage
from direct.gui.DirectGui import *
from direct.showbase.ShowBase import ShowBase
from panda3d.core import *
from direct.showbase import DirectObject
import simplepbr
from direct.interval.IntervalGlobal import Sequence, Func, Wait

configVars = """
win-size 1400 720
window-title Deck Builder
clock-mode limited
clock-frame-rate 45
text-use-harfbuzz true
"""

loadPrcFileData('', configVars)

numCards4EachRow = 4
manaDistriArea_Y = 0.4

from LoadModels import *


class BtnCardIncluded(DirectButton):
	def __init__(self, base, btnName, card):
		DirectButton.__init__(self, text=(btnName, "Will Remove", "Remove?", btnName), command=self.removeCardfromDeck)
		self.base = base
		self.card = card
		
class Panda_DeckBuilder(ShowBase):
	def __init__(self, ClassCards, NeutralCards, SV=0):
		ShowBase.__init__(self)
		#self.root = NodePath("root")
		#self.root.reparentTo(self.render)
		#simplepbr.init()
		self.disableMouse()
		"""The collision handler in order to pick the card models"""
		self.collHandler = CollisionHandlerQueue()
		self.cTrav = CollisionTraverser()
		
		self.ClassCards, self.NeutralCards = ClassCards, NeutralCards
		#self.Class2Display, self.expansion, self.mana = tk.StringVar(self), tk.StringVar(self), tk.StringVar(self)
		self.cards2Display, self.collectionsDrawn, self.pageNum = {}, [], 0
		self.cardsinDeck, self.btnsinDeck = [], []
		self.manaAreaWidgets = []
		self.txt_Total, self.entry_deckCode = None, None
		self.lbl_CardTypes = None
		
		"""Draw the first layer. All widgets will be destroyed when moving onto next layer"""
		self.widgetsDrawn = []
		lbl_SelectClass = OnscreenText(text="Select a class", pos=(-1.2, 0.8), scale=0.08,
									   fg=(1, 1, 1, 1), align=TextNode.ACenter,
									   mayChange=1)
		self.widgetsDrawn.append(lbl_SelectClass)
		#classText = OnscreenText(text="Demon Hunter", pos=(-0.8, 0.7), scale=0.15,
		#			fg=(1, 1, 1, 1), align=TextNode.ACenter,
		#			mayChange=1)
		classList = list(self.ClassCards.keys())
		self.classMenu = DirectOptionMenu(text="Demon Hunter", scale=0.08,
										  items=classList, initialitem=0,
										  highlightColor=(0, 1, 0, 1))
		self.classMenu.setPos(-0.9, 0, 0.8)
		self.widgetsDrawn.append(self.classMenu)
		btn_StartBuildDeck = DirectButton(text=("Continue", "Click!", "Rolling Over", "Continue"),
										  scale=.08, command=self.init_AllPanels)
		btn_StartBuildDeck.setPos(0.2, 0, 0.8)
		self.widgetsDrawn.append(btn_StartBuildDeck)
		self.expansions = ["All", "DIY", "Basic", "Classic", "Shadows", "Uldum", "Dragons", "Galakrond", "Initiate", "Outlands", "Academy", "Darkmoon"]
	
	def init_AllPanels(self):
		Class2Start = [self.classMenu.get(), "Neutral"]
		for widget in self.widgetsDrawn: widget.destroy()
		
		manas = ["All", '0', '1', '2', '3', '4', '5', '6', '7', '7+']
		
		"""Display the buttons and option menus"""
		searchPanel_Y_1 = 0.9
		searchPanel_Y_2 = 0.78
		OnscreenText(text="Class", pos=(-1.6, searchPanel_Y_1), scale=0.08, align=TextNode.ACenter, mayChange=1)
		self.classOpt = DirectOptionMenu(text=Class2Start[0], scale=0.08,
										 items=Class2Start, initialitem=0,
										 highlightColor=(0, 1, 0, 1))
		self.classOpt.setPos(-1.5, 0, searchPanel_Y_1)
		OnscreenText(text="Mana", pos=(-0.8, searchPanel_Y_1), scale=0.08, align=TextNode.ACenter, mayChange=1)
		self.manaOpt = DirectOptionMenu(text=manas[0], scale=0.08,
										items=manas, initialitem=0,
										highlightColor=(0, 1, 0, 1))
		self.manaOpt.setPos(-0.7, 0, searchPanel_Y_1)
		OnscreenText(text="Expansion", pos=(-0.3, searchPanel_Y_1), scale=0.08, align=TextNode.ACenter, mayChange=1)
		self.expansionOpt = DirectOptionMenu(text=self.expansions[0], scale=0.08,
											 items=self.expansions, initialitem=0,
											 highlightColor=(0, 1, 0, 1))
		self.expansionOpt.setPos(-0.1, 0, searchPanel_Y_1)
		
		sansBold = self.loader.loadFont('Models\\OpenSans-Bold.ttf')
		self.search = DirectEntry(width=10, entryFont=sansBold, scale=0.06)
		btn_ViewCards = DirectButton(text=("View Cards", "Click!", "Rolling Over", "Continue"),
									 scale=.08, command=self.showCards)
		btn_Left = DirectButton(text=("Next", "Click!", "Rolling Over", "Continue"),
								scale=.08, command=self.lastPage)
		btn_Right = DirectButton(text=("Last", "Click!", "Rolling Over", "Continue"),
								 scale=.08, command=self.nextPage)
		self.search.setPos(-1.7, 0, searchPanel_Y_2)
		btn_ViewCards.setPos(-0.8, 0, searchPanel_Y_2)
		btn_Left.setPos(-0.2, 0, searchPanel_Y_2)
		btn_Right.setPos(0, 0, searchPanel_Y_2)
		
		"""Display the total number of cards, deck code, etc"""
		self.txt_Total = OnscreenText(text="0/30", pos=(0.5, 0.9), scale=0.1, fg=(1, 1, 1, 1), font=sansBold)
		btn_Clear = DirectButton(text=("Clear Deck"), scale=0.06, command=self.clear)
		self.entry_DeckCode = DirectEntry(width=10, entryFont=sansBold, scale=0.04)
		self.entry_DeckCode.setPos(0.8, 0, 0.8)
		btn_Clear.setPos(0.8, 0, 0.92)
		btn_Export = DirectButton(text=("Export Deck"), scale=0.06, command=self.export)
		btn_Export.setPos(0.6, 0, 0.8)
		
		"""Draw the texts mana distribution"""
		for i, mana in enumerate(('0', '1', '2', '3', '4', '5', '6', '7', '7+')):
			OnscreenText(text=mana, pos=(0.55+0.07*i, manaDistriArea_Y), scale=0.07, fg=(0, 0, 0, 1), font=sansBold)
			
		"""Define the collision ray for the mouse cursor"""
		self.camera.setPos(0, 0, 0)
		collNode_Picker = CollisionNode("Picker Collider c_node")
		self.raySolid = CollisionRay()
		collNode_Picker.addSolid(self.raySolid)
		pickerNode = self.camera.attachNewNode(collNode_Picker)
		pickerNode.show() #For now, show the pickerRay collision with the card models
		self.cTrav.addCollider(pickerNode, self.collHandler)
		#self.cTrav.showCollisions(self.render)
	
	"""Due to unknown cause, the collision handler queue can only get the correct
			entry the second time the raySolid is repositioned, and this repositioning
			must happen in separate functions/events.
			The solution for now is to let the mouseKeyDown event reposition the raySolid for the 1st time,
			then let mouseKeyUp event reposition for the 2nd time, so the 1st reposition can give the correct position"""
	
	def mouse1_Down(self):
		if self.mouseWatcherNode.hasMouse():
			mpos = self.mouseWatcherNode.getMouse()
			#Reset the Collision Ray orientation, based on the mouse position
			self.raySolid.setFromLens(self.camNode, mpos.getX(), mpos.getY())
	
	def mouse1_Up(self):
		if self.mouseWatcherNode.hasMouse():
			mpos = self.mouseWatcherNode.getMouse()
		#Reset the Collision Ray orientation, based on the mouse position
		self.raySolid.setFromLens(self.camNode, mpos.getX(), mpos.getY())
		if self.collHandler.getNumEntries() > 0:
			self.collHandler.sortEntries()
			#The pickedObj here is the collision node
			collNode_Picked = self.collHandler.getEntry(0).getIntoNodePath()
			pickedModel_NodePath = collNode_Picked.getParent()
			"""Due to unknown reasons, all node paths are involved in the render hierachy
				have their types forced into NodePath, even if they are subclasses of NodePath.
				Therefore, we have to keep a container of the subclass instance, where the original type is preserved"""
			pickedModel_NodePath_Attrib = next((model_NodePath for model_NodePath in self.collectionsDrawn \
											   if model_NodePath == pickedModel_NodePath), None)
			if pickedModel_NodePath_Attrib:
				self.addCardtoDeck(pickedModel_NodePath_Attrib.cardType)
				
	def addCardtoDeck(self, card):
		if len(self.cardsinDeck) >= 30:
			self.showTempText("Your deck is full")
		else:
			numCopies = sum(type == card for type in self.cardsinDeck)
			if "~Legendary" in card.index and numCopies > 0:
				self.showTempText("Can only have 1 copy of Legendary in the same deck")
			elif numCopies > 1:
				self.showTempText("Can't have >2 copies in the same deck")
			else:
				self.cardsinDeck.append(card)
				self.updateDeckComp()
				
	def updateDeckComp(self):
		for btn in self.btnsinDeck: btn.destroy()
		self.btnsinDeck.clear()
		#cardCounts: {CharosStrike: 2}, mana_2_cards: {5: [ChaosNova, GlaiveboundAdept]}
		cardCounts, mana_2_cards = {}, {}
		for card in self.cardsinDeck:
			if card in cardCounts: cardCounts[card] += 1
			else: cardCounts[card] = 1
			cost = card.mana
			if cost not in mana_2_cards: mana_2_cards[cost] = [card]
			elif card not in mana_2_cards[cost]: mana_2_cards[cost].append(card)
		i = 0
		for cost in sorted(list(mana_2_cards.keys())):
			for card in mana_2_cards[cost]:
				for num in range(cardCounts[card]):
					btnName = "%d  "%cost + card.name + (' 2' if num > 1 else '')
					cardBtn = DirectButton(text=(btnName, btnName, btnName, btnName), scale=(0.06, 0.06, 0.06),
										   command=self.removeCardfromDeck, extraArgs=[card])
					print("The button will remove card:", card)
					#cardBtn = BtnCardIncluded(self, btnName, card)
					cardBtn.setPos(0.75, 0, 0.3 - i * 0.08)
					self.btnsinDeck.append(cardBtn)
					i += 1
		self.drawManaDistri()
		self.txt_Total["text"] = "%d/30"%len(self.cardsinDeck)
		
	def drawManaDistri(self):
		for img in self.manaAreaWidgets: img.destroy()
		self.manaAreaWidgets = []
		distriCounts = [0] * 9
		if self.cardsinDeck:
			for card in self.cardsinDeck:
				distriCounts[min(8, card.mana)] += 1
			maxCount = max(distriCounts)
			sansBold = self.loader.loadFont('Models\\OpenSans-Bold.ttf')
			for i in range(8):
				height = distriCounts[i] / maxCount
				img = OnscreenImage(image="Models\\DeckManaBar.png", scale=(0.02, 1, 0.1*height),
									pos=(0.55+0.07*i, 0, manaDistriArea_Y+0.06+0.1*height))
				self.manaAreaWidgets.append(img)
				txt_CardAmount = OnscreenText(text="%d"%distriCounts[i], scale=0.05, font=sansBold, fg=(1, 1, 1, 1),
											  pos=(0.55+0.07*i, manaDistriArea_Y+0.08+0.2*height))
				self.manaAreaWidgets.append(txt_CardAmount)
			#Draw the "7+" mana bar
			height = distriCounts[8]/maxCount
			img = OnscreenImage(image="Models\\DeckManaBar.png", scale=(0.02, 1, 0.1 * height),
								pos=(0.55+0.07*8, 0, manaDistriArea_Y+0.07+0.1*height))
			self.manaAreaWidgets.append(img)
			txt_CardAmount = OnscreenText(text="%d" % distriCounts[8], scale=0.05, font=sansBold, fg=(1, 1, 1, 1),
										  pos=(0.55 + 0.07 * 8, manaDistriArea_Y + 0.08 + 0.2 * height))
			self.manaAreaWidgets.append(txt_CardAmount)
			
	def removeCardfromDeck(self, card):
		print("Trying to remove card:", card, self.cardsinDeck)
		self.cardsinDeck.remove(card)
		print("After removal, the cardsinDeck is:\n", self.cardsinDeck)
		self.updateDeckComp()
		
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
		"""Display the cards"""
		self.cards2Display, self.pageNum = {}, 0
		for nodePath in self.collectionsDrawn: nodePath.removeNode()
		
		Class2Display = self.classOpt.get()
		mana = self.manaOpt.get()
		expansion = self.expansionOpt.get()
		search = self.search.get()
		if Class2Display == "Neutral":
			cards = self.NeutralCards
		else:
			cards = self.ClassCards[Class2Display]
		i, j = 0, -1
		for key, value in cards.items():
			if self.manaCorrect(value, mana) and self.expansionCorrect(key, expansion) \
					and self.searchMatches(search, value):
				if i % (2 * numCards4EachRow) == 0:
					j += 1
					self.cards2Display[j] = [value]
				else:
					self.cards2Display[j].append(value)
				i += 1
		if self.cards2Display:  #如果查询结果不为空
			self.accept("mouse1", self.mouse1_Down)
			self.accept("mouse1-up", self.mouse1_Up)
			for i, card in enumerate(self.cards2Display[0]):
				card_Model = self.loadCardModel(card)
				#print(card_Model, type(card_Model), card_Model.findAllMatches('*'))
				x, y, z = -22 + 8 * (i % numCards4EachRow), 50, 4 -11 * (i >= numCards4EachRow)
				card_Model.setPos(x, y, z)
				self.collectionsDrawn.append(card_Model)
				
				collNode_Card = CollisionNode("%d c_node"%i)
				collNode_Card.addSolid(CollisionBox(Point3(0, 0, 0), 3.7, 0.3, 5.2))
				card_Model.attachNewNode(collNode_Card)
				
	def loadCardModel(self, cardType):
		if "attack" in cardType.__dict__:  #The card is minion or weapon
			if "health" in cardType.__dict__:
				card_Model = loadMinion(self.render, self.loader, cardType, orig=True)
			else:
				card_Model = loadWeapon(self.render, self.loader, cardType, orig=True)
		elif "armor" in cardType.__dict__:  #The card is a hero card
			card_Model = loadHero(self.render, self.loader, cardType, orig=True)
		else:
			card_Model = loadSpell(self.render, self.loader, cardType, orig=True)
		card_Model.reparentTo(self.render)
		return card_Model
	
	def showTempText(self, text):
		sansBold = self.loader.loadFont('Models\\OpenSans-Bold.ttf')
		text = OnscreenText(text=text, pos=(0, 0), scale=0.1, fg=(1, 0, 0, 1),
							align=TextNode.ACenter, mayChange=1, font=sansBold,
							bg=(0.5, 0.5, 0.5, 0.8))
		Sequence(Wait(1.5), Func(text.destroy)).start()
		
	def lastPage(self):
		if self.pageNum - 1 in self.cards2Display:
			self.pageNum -= 1
			for nodePath in self.collectionsDrawn: nodePath.removeNode()
			self.collectionsDrawn.clear()
			for i, card in enumerate(self.cards2Display[self.pageNum]):
				card_Model = self.loadCardModel(card)
				x, y, z = -22 + 8 * (i % numCards4EachRow), 50, 4 - 11 * (i >= numCards4EachRow)
				card_Model.setPos(x, y, z)
				self.collectionsDrawn.append(card_Model)
				
				collNode_Card = CollisionNode("%d c_node" % i)
				collNode_Card.addSolid(CollisionBox(Point3(0, 0, 0), 3.7, 0.3, 5.2))
				card_Model.attachNewNode(collNode_Card)
		else:
			self.showTempText("Already the first page")
		
	def nextPage(self):
		if self.pageNum + 1 in self.cards2Display:
			self.pageNum += 1
			for nodePath in self.collectionsDrawn: nodePath.removeNode()
			self.collectionsDrawn.clear()
			for i, card in enumerate(self.cards2Display[self.pageNum]):
				card_Model = self.loadCardModel(card)
				x, y, z = -22 + 8 * (i % numCards4EachRow), 50, 4 - 11 * (i >= numCards4EachRow)
				card_Model.setPos(x, y, z)
				self.collectionsDrawn.append(card_Model)
				
				collNode_Card = CollisionNode("%d c_node" % i)
				collNode_Card.addSolid(CollisionBox(Point3(0, 0, 0), 3.7, 0.3, 5.2))
				card_Model.attachNewNode(collNode_Card)
		else:
			self.showTempText("Already the last page")
	
	def clear(self):
		self.cardsinDeck = []
		self.txt_Total["text"] = "0/30"
		self.updateDeckComp()
		
	def export(self):
		s = "names||"
		for card in self.cardsinDeck:
			s += card.name + "||"
		s = s[0:-2] #Remove the last "||"
		self.entry_DeckCode.enterText(s)

if __name__ == "__main__":
	SV = 0
	makeCardPool(board="0 Random Game Board", monk=0, SV=SV)
	
	from CustomWidgets import txt, CHN, folderNameTable
	from CardPools import ClassCards, NeutralCards
	
	Panda_DeckBuilder(ClassCards, NeutralCards, SV=SV).run()
