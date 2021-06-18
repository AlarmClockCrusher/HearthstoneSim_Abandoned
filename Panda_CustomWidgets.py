import numpy as np
from math import ceil

from LoadModels import *


"""Hand Zone infos"""
Separation_Hands = 5
OpeningAngle = 40
radius = 12.9
HandZone_Y = -8
HandZone1_Z, HandZone2_Z = -24, 25
DrawnCard1_PausePos, DrawnCard2_PausePos = (6.5, -25, -0.8), (6.5, -25, 4.2)
DiscardedCard1_Y, DiscardedCard2_Y = -2, 5.5
ZoomInCard_X, ZoomInCard_Y, ZoomInCard1_Z, ZoomInCard2_Z = -12.3, -20, -2.2, 4.75


def calc_PosHprHands(num, x, y, z):
	if num < 1: return [], []
	d_angle = min(12, int(OpeningAngle / num))
	posHands, hprHands = [], []
	if z < 0:
		leftAngle = -d_angle * (num - 1) / 2
		for i in range(num):
			angleAboutY = leftAngle+i*d_angle
			hprHands.append(Point3(0, 0, angleAboutY))
			posHands.append(Point3(x+radius*np.sin(np.pi*angleAboutY/180), y-i*0.15,
								z+radius*np.cos(np.pi*angleAboutY/180)))
	else:
		leftAngle = d_angle * (num - 1) / 2
		for i in range(num):
			angleAboutY = leftAngle-i*d_angle
			hprHands.append(Point3(0, 0, angleAboutY+180))
			posHands.append(Point3(x-radius*np.sin(np.pi*angleAboutY/180), y+i*0.15,
								z-radius*np.cos(np.pi*angleAboutY/180)))
	return posHands, hprHands

posHandsTable = {HandZone1_Z: {i: calc_PosHprHands(i, 0, HandZone_Y, HandZone1_Z)[0] for i in range(13)},
				HandZone2_Z: {i: calc_PosHprHands(i, 0, HandZone_Y, HandZone2_Z)[0] for i in range(13)}
				}
				
hprHandsTable = {HandZone1_Z: {i: calc_PosHprHands(i, 0, HandZone_Y, HandZone1_Z)[1] for i in range(13)},
				HandZone2_Z: {i: calc_PosHprHands(i, 0, HandZone_Y, HandZone2_Z)[1] for i in range(13)}
				}


class HandZone:
	def __init__(self, GUI, ID):
		self.GUI, self.ID = GUI, ID
		lowerPlayerID = max(1, self.GUI.ID) #GUI_1P has UI = 0
		self.x, self.y, self.z = 0, HandZone_Y, HandZone1_Z if self.ID == lowerPlayerID else HandZone2_Z
		
	#transform hand card into arbitrary type. Minion could become spell
	def transformHands(self, btns, newCards):
		para = Parallel()
		for btn, newCard in zip(btns, newCards):
			isPlayed = btn.isPlayed
			pos, hpr, scale = btn.np.getPos(), btn.np.getHpr(), btn.np.getScale()
			nodePath, btn_NewCard = genCard(self.GUI, newCard, isPlayed=isPlayed, pos=pos, hpr=hpr, scale=scale)
			para.append(Func(btn.np.removeNode))
			para.append(Func(nodePath.setPosHprScale, pos, hpr, scale))
		self.GUI.seqHolder[-1].append(para)
		
	def placeCards(self, add2Queue=True):
		ownHand = self.GUI.Game.Hand_Deck.hands[self.ID]
		posHands, hprHands = posHandsTable[self.z][len(ownHand)], hprHandsTable[self.z][len(ownHand)]
		for i, card in enumerate(ownHand):
			if not card.btn: genCard(self.GUI, card, isPlayed=False)
		para = Parallel()
		for i, card in enumerate(ownHand):
			para.append(card.btn.genLerpInterval(posHands[i], hprHands[i], duration=0.25))
		if self.GUI.seqHolder and add2Queue: self.GUI.seqHolder[-1].append(para)
		else: para.start()
		

"""Hero Zone infos"""
Hero1_Pos, Hero2_Pos = (0, -1.05, -7.35), (0.05, -1.05, 8.54)
Weapon1_Pos, Weapon2_Pos = (-4.75, -1.05, -7.4), (-4.75, -1.05, 8.48)
Power1_Pos, Power2_Pos = (4.67, -1.1, -7.9), (4.67, -1.1, 8)
Hero2_X = Hero2_Pos[0]
posSecretsTable = {Hero1_Pos: [( +0,    -1.15, -4.82),
								(-1.14, -1.15, -5.43),
								(+1.14, -1.15, -5.43),
								(-1.83, -1.15, -6.51),
								(+1.83, -1.15, -6.51)],
					Hero2_Pos: [(Hero2_X+0,    -1.15, 11.05),
								(Hero2_X-1.14, -1.15, 10.44),
								(Hero2_X+1.14, -1.15, 10.44),
								(Hero2_X-1.83, -1.15, 9.36),
								(Hero2_X+1.83, -1.15, 9.36)]
			  		}

Seperation_Trigs = 0.92
def calc_posTrigs(num, x, y, z, firstTime=True): #Input the x, y, z of the HeroZone
	if firstTime: z = z - 2.35
	if num < 4:
		leftPos = x + 0.05 - Seperation_Trigs * (num - 1) / 2
		return [Point3(leftPos + Seperation_Trigs * i, y, z) for i in range(num)]
	else: #num >= 4
		if (num - 3) % 2 == 1: numLeft, numRight = int((num - 2) / 2), int((num - 4) / 2)
		else: numLeft = numRight = int((num - 3) / 2)
		return [(x - 2.87 - i * Seperation_Trigs, y, z) for i in range(numLeft)] \
				+ calc_posTrigs(3, x, y, z, firstTime=False) + [(x + 2.92 + i * Seperation_Trigs, y, z) for i in range(numRight)]
	

ManaText1_Pos, ManaText2_Pos = (7.87, -1.01, -11.9), (6.92, -1.05, 11.65)

class HeroZone:
	def __init__(self, GUI, ID):
		self.GUI, self.ID = GUI, ID
		lowerPlayerID = max(1, self.GUI.ID) #GUI_1P has UI = 0
		if self.ID == lowerPlayerID: self.heroPos, self.weaponPos, self.powerPos = Hero1_Pos, Weapon1_Pos, Power1_Pos
		else: self.heroPos, self.weaponPos, self.powerPos = Hero2_Pos, Weapon2_Pos, Power2_Pos
		
		self.manaHD = GUI.Game.Manas
		#Merge the ManaZone with HeroZone
		self.manaText = TextNode("Mana Text")
		self.manaText.setText("0/0")
		self.manaText.setAlign(TextNode.ACenter)
		self.manaText.setFont(self.GUI.font)
		manaTextNode = self.GUI.render.attachNewNode(self.manaText)
		manaTextNode.setScale(0.8)
		if self.heroPos[2] < 0: manaTextNode.setPos(ManaText1_Pos)
		else: manaTextNode.setPos(ManaText2_Pos)
		
		self.secretsDrawn, self.trigsDrawn = [], []
		
	def placeCards(self, add2Queue=True):
		#The whole func takes ~1ms
		game = self.GUI.Game
		hero, power, weapon = game.heroes[self.ID], game.powers[self.ID], game.availableWeapon(self.ID)
		if not hero.btn: genCard(self.GUI, hero, isPlayed=True, pos=self.heroPos)
		if not power.btn:
			nodePath, btn = genCard(self.GUI, power, isPlayed=True, pos=self.powerPos)
			x, y, z = self.powerPos
			riseInterval = btn.genLerpInterval(pos=Point3(x, y - 3, z), hpr=Point3(90, 0, 0), duration=0.2)
			dropInterval = btn.genLerpInterval(pos=Point3(x, y, z), hpr=Point3(180, 0, 0), duration=0.2)
			flipInterval = btn.genLerpInterval(hpr=Point3(360, 0, 0), duration=0.2)
			#新技能出现的时候一定都是可以使用的正面向上状态
			sequence = Sequence(riseInterval, dropInterval, flipInterval, name="Animate Power Appearing")
			if self.GUI.seqHolder and add2Queue: self.GUI.seqHolder[-1].append(sequence)
			else: sequence.start()
		if weapon and not weapon.btn:
			nodePath, btn = genCard(self.GUI, weapon, isPlayed=True)
			sequence = Sequence(Func(nodePath.setPos, (self.weaponPos[0], self.weaponPos[1]-0.5, self.weaponPos[2]+0.2)),
								btn.genLerpInterval(pos=self.weaponPos))
			if self.GUI.seqHolder and add2Queue: self.GUI.seqHolder[-1].append(sequence)
			else: sequence.start()
			
	def drawMana(self, usable, upper, locked, overloaded):
		#usable, upper = self.manaHD.manas[ID], self.manaHD.manasUpper[ID]
		#locked, overloaded = self.manaHD.manasLocked[ID], self.manaHD.manasOverloaded[ID]
		#print("usable, upper", usable, upper)
		self.manaText.setText("%d/%d"%(usable, upper))
		manas = self.GUI.manaModels
		if self.heroPos[2] < 0:
			for i in range(usable): manas["Mana"][i].setPos(i * 0.82, -1, 0)
			for i in range(usable, 10): manas["Mana"][i].setPos(0, 0, 0)
			for j in range(upper - usable - locked): manas["EmptyMana"][j].setPos((usable+j) * 0.82, -1, 0)
			for j in range(upper - usable - locked, 10): manas["EmptyMana"][j].setPos(0, 0, 0)
			for k in range(locked): manas["LockedMana"][k].setPos((upper - usable - locked + k)  * 0.82, -1, 0)
			for k in range(locked, 10): manas["LockedMana"][k].setPos(0, 0, 0)
			for m in range(overloaded): manas["OverloadedMana"][m].setPos(m * 0.82, -1, -1.2)
			for m in range(overloaded, 10): manas["OverloadedMana"][m].setPos(0, 0, 0)
			
	#Secrets and quests are treated in the same way
	def placeSecrets(self):
		secretHD = self.GUI.Game.Secrets
		ownSecrets = secretHD.mainQuests[self.ID] + secretHD.sideQuests[self.ID] + secretHD.secrets[self.ID]
		posSecrets = posSecretsTable[self.heroPos][:len(ownSecrets)]
		para = Parallel()
		for i, card in enumerate(ownSecrets):
			if card.btn:
				if card.btn.np.getPos() != posSecrets[i]:
					para.append(card.btn.np.posInterval(0.4, pos=posSecrets[i]))
			else:
				nodePath, btn_Secret = genSecretIcon(self.GUI, card, posSecrets[i])
				hpr = (0, 0, 0) if self.ID != self.GUI.Game.turn else (180, 0, 0)
				para.append(Sequence(Func(nodePath.setPosHpr, posSecrets[i], (90, 0, 0)), 
									LerpHprInterval(nodePath, duration=0.3, hpr=hpr))
							)
				
		if self.GUI.seqHolder: self.GUI.seqHolder[-1].append(para)
		else: para.start()
		
	def addaTrig(self, card):
		genTurnTrigIcon(self.GUI, card) #Add the trig to (0, 0, 0)
		if self.GUI.seqHolder: self.GUI.seqHolder[-1].append(Func(self.placeTurnTrigs))
		else: self.placeTurnTrigs()
		
	def removeaTrig(self, card):
		if self.GUI.seqHolder:
			self.GUI.seqHolder[-1].append(Func(card.btn.np.removeNode))
			self.GUI.seqHolder[-1].append(Func(self.placeTurnTrigs))
		else:
			card.btn.np.removeNode()
			self.placeTurnTrigs()
			
	def placeTurnTrigs(self):
		cards = [trig.card for trig in self.GUI.Game.turnEndTrigger + self.GUI.Game.turnStartTrigger if trig.ID == self.ID]
		posTrigs = calc_posTrigs(len(cards), self.heroPos[0], self.heroPos[1]-0.1, self.heroPos[2])
		seqHolder = self.GUI.seqHolder
		if seqHolder:
			para = Parallel()
			for i, card in enumerate(cards):
				if not card.btn: genTurnTrigIcon(self.GUI, card, pos=posTrigs[i])
			for i, card in enumerate(cards):
				if card.btn: para.append(card.btn.np.posInterval(0.25, pos=posTrigs[i]))
			seqHolder[-1].append(para)
		else:
			for i, card in enumerate(cards):
				if not card.btn: nodePath, card.btn = genTurnTrigIcon(self.GUI, card, pos=posTrigs[i])
			for i, card in enumerate(cards):
				if card.btn: card.btn.np.posInterval(0.25, pos=posTrigs[i]).start()
				
				
Separation_Minions = 3.7
MinionZone_Y = Hero1_Pos[1] - 2
MinionZone1_Z, MinionZone2_Z = -1.62, 3.2

def calc_posMinions(num, x, y, z):
	leftPos = x - Separation_Minions * (num - 1) / 2
	posMinions = [Point3(leftPos + Separation_Minions * i, y-0.04*i, z) for i in range(num)]
	return posMinions

#0~14 minions
posMinionsTable = {MinionZone1_Z: {i: calc_posMinions(i, 0, MinionZone_Y, MinionZone1_Z) for i in range(15)},
				MinionZone2_Z: {i: calc_posMinions(i, 0, MinionZone_Y, MinionZone2_Z) for i in range(15)}
				}

class MinionZone:
	def __init__(self, GUI, ID):
		self.GUI, self.ID = GUI, ID
		lowerPlayerID = max(1, self.GUI.ID) #GUI_1P has UI = 0
		self.z = MinionZone1_Z if self.ID == lowerPlayerID else MinionZone2_Z
		
	#It takes negligible time to finish calcing pos and actually start drawing
	def placeCards(self, add2Queue=True):
		ownMinions = self.GUI.Game.minions[self.ID]
		posMinions = posMinionsTable[self.z][len(ownMinions)]
		for i, card in enumerate(ownMinions):
			if not card.btn: genCard(self.GUI, card, isPlayed=True)
		para = Parallel()
		for i, card in enumerate(ownMinions):
			para.append(card.btn.genLerpInterval(posMinions[i], duration=0.25))
		if self.GUI.seqHolder and add2Queue: self.GUI.seqHolder[-1].append(para)
		else: para.start()
		

class Btn_Board:
	def __init__(self, GUI, nodePath):
		self.GUI = GUI
		self.selected = False
		self.np = nodePath
		self.card = None #Just a placeholder
		
	def leftClick(self):
		print("Board is clicked")
		if -1 < self.GUI.UI < 3:  #不在发现中和动画演示中才会响应
			self.GUI.resolveMove(None, self, "Board")
	
	def rightClick(self):
		self.GUI.cancelSelection()
		self.GUI.stopCardZoomIn()
		
	def dimDown(self):
		self.np.setColor(grey)
	
	def setBoxColor(self, color):
		pass
	
	def stopCardZoomIn(self):
		pass
		
		
TurnEndBtn_Pos = (15.5, -1, 1.16)

class Btn_TurnEnd:
	def __init__(self, GUI, nodePath):
		self.GUI = GUI
		self.np = nodePath
		self.card = None  #Just a placeholder
		
	def leftClick(self):
		if 3 > self.GUI.UI > -1:
			self.GUI.resolveMove(None, self, "TurnEnds")
			
	def rightClick(self):
		self.GUI.cancelSelection()
	
	def dimDown(self):
		self.np.setColor(grey)
	
	def setBoxColor(self, color):
		pass
	
	def stopCardZoomIn(self):
		pass


deckScale = 0.9
Deck1_Pos, Deck2_Pos = (16.85, -3, -2.5), (16.75, -3, 4.85)
hpr_Deck = (90, 180, -88)

class DeckZone:
	def __init__(self, GUI, ID):
		self.GUI, self.ID = GUI, ID
		lowerPlayerID = max(1, self.GUI.ID) #GUI_1P has UI = 0
		self.pos = Deck1_Pos if self.ID == lowerPlayerID else Deck2_Pos
		self.HD = self.GUI.Game.Hand_Deck
		np_Deck = GUI.loader.loadModel("Models\\BoardModels\\Deck.glb")
		np_Deck.setTexture(np_Deck.findTextureStage('*'), GUI.textures["cardBack"], 1)
		np_Deck.reparentTo(GUI.render)
		np_Deck.setPosHpr(self.pos, hpr_Deck)
		for nodePath in np_Deck.getChildren(): nodePath.setTransparency(True)
		np_Deck.setScale(0.9)
		self.np_Deck = np_Deck
		self.textNode = TextNode("Deck_TextNode")
		self.textNode.setText("Deck: {}\nHand: {}".format(0, 0))
		self.textNode.setFont(GUI.font)
		#textNode.setAlign(TextNode.)
		textNodePath = GUI.render.attachNewNode(self.textNode)
		textNodePath.setPos(self.pos[0] + 1.5, self.pos[1], self.pos[2] + 0.4)
		
		#The fatigue model to show when no more card to draw
		self.np_Fatigue = GUI.loader.loadModel("Models\\BoardModels\\Fatigue.glb")
		self.np_Fatigue.setTexture(self.np_Fatigue.findTextureStage('0'),
							  GUI.loader.loadTexture("Models\\BoardModels\\Fatigue.png"), 1)
		self.np_Fatigue.reparentTo(GUI.render)
		textNode = TextNode("Fatigue_TextNode")
		textNode.setFont(GUI.font)
		#textNode.setTextColor(1, 0, 0.1, 1)
		textNode.setText('1')
		textNode.setAlign(TextNode.ACenter)
		textNodePath = self.np_Fatigue.attachNewNode(textNode)
		textNodePath.setPos(-0.03, -0.04, -1.3)

	def draw(self, deckSize):
		i, numPairs2Draw = 1, min(10, ceil(deckSize / 3))
		for nodePath in self.np_Deck.getChildren():
			nodePath.setColor(white if i <= numPairs2Draw else transparent)
			i += 1
		self.textNode.setText("Deck: {}\nHand: {}".format(len(self.HD.decks[self.ID]), len(self.HD.hands[self.ID])))
		
	def fatigueAni(self, numFatigue):
		self.np_Fatigue.find("Fatigue_TextNode").node().setText(str(numFatigue))
		moPath = Mopath.Mopath()
		moPath.loadFile("Models\\BoardModels\\FatigueCurve.egg")
		interval = MopathInterval(moPath, self.np_Fatigue, duration=0.6)
		if self.GUI.seqHolder: self.GUI.seqHolder[-1].append(Sequence(interval, Wait(1), Func(self.np_Fatigue.setPos, (0, 0, 0) ) ))
		else: Sequence(interval, Wait(1), Func(self.np_Fatigue.setPos, (0, 0, 0) ) ).start()
		
	def rightClick(self):
		if self.GUI.UI == 0:
			self.GUI.showTempText("Deck size: {}\nHand size: {}".format(len([self.ID]),
																		len(self.GUI.Game.Hand_Deck.hands[self.ID])))
