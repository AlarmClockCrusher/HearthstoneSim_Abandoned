from direct.interval.FunctionInterval import Func, Wait
from direct.interval.LerpInterval import *
from direct.interval.MetaInterval import Sequence, Parallel
from direct.directutil import Mopath
from direct.interval.MopathInterval import *
from panda3d.core import *
import inspect
from datetime import datetime
import numpy as np
import os

CHN = False

BoardIndex = ["0 Random Game Board",
			"1 Classic Ogrimmar", "2 Classic Stormwind", "3 Classic Stranglethorn", "4 Classic Four Wind Valley",
			#"5 Naxxramas", "6 Goblins vs Gnomes", "7 Black Rock Mountain", "8 The Grand Tournament", "9 League of Explorers Museum", "10 League of Explorers Ruins",
			#"11 Corrupted Stormwind", "12 Karazhan", "13 Gadgetzan",
			#"14 Un'Goro", "15 Frozen Throne", "16 Kobolds",
			#"17 Witchwood", "18 Boomsday Lab", "19 Rumble",
			#"20 Dalaran", "21 Uldum Desert", "22 Uldum Oasis", "23 Dragons",
			"24 Outlands", "25 Scholomance Academy", "26 Darkmoon Faire",
			]


#Not used for finding Hero Head, or Hero Power. Hero cards are included in each expansion folder
def findFilepath(card): #card is an instance
	if card.type == "Dormant":
		if card.minionInside:
			name = card.minionInside.__name__ if inspect.isclass(card.minionInside) else type(card.minionInside).__name__
			return "Images\\%s\\%s.png"%(card.minionInside.index.split('~')[0], name)
		else: return "Images\\%s\\%s.png"%(card.index.split('~')[0], type(card).__name__)
	elif "Option" in card.type:
		return "Images\\Options\\%s.png"%type(card).__name__
	elif card.type in ("Minion", "Weapon", "Spell", "Hero"):  #type == "Weapon", "Minion", "Spell", "Hero", "Power"
		return "Images\\%s\\%s.png"%(card.index.split('~')[0], type(card).__name__.split('__')[0]) #Mutable cards need to be handled
	elif card.type == "Power":
		return "Images\\HeroesandPowers\\%s.png"%type(card).__name__
	
	
red, green, blue = (1, 0, 0, 1), (0.3, 1, 0.2, 1), (0, 0, 1, 1)
yellow, pink = (1, 1, 0, 1), (1, 0, 1, 1)
darkGreen = (0.3, 0.8, 0.2, 1)
transparent, grey = (1, 1, 1, 0), (0.5, 0.5, 0.5, 1)
black, white = (0, 0, 0, 1), (1, 1, 1, 1)


#If poseFrame is negative, then the texCard keeps playing
def makeTexCard(GUI, filePath, pos=(0, 0, 0), scale=1.0, aspectRatio=1,
				name='', getSeqNode=True, poseFrame=0, parent=None):
	texCard = GUI.loader.loadModel(filePath)
	texCard.name = name + "_TexCard" if name else "TexCard"
	if aspectRatio == 1: texCard.setScale(scale)
	else: texCard.setScale(scale, 1, scale*aspectRatio)
	texCard.setPosHpr(pos, (0, -90, 0))
	texCard.reparentTo(parent if parent else GUI.render)
	if getSeqNode:
		seqNode = texCard.find("+SequenceNode").node()
		if poseFrame > -1: seqNode.pose(poseFrame)
	else: seqNode = None
	return texCard, seqNode

#Can only set the color of the textNode itself to transparent. No point in setting the nodePath transparency
def makeText(np_Parent, textName, valueText, pos, scale, color, font, wordWrap=0, cardColor=None):
	textNode = TextNode(textName + "_TextNode")
	textNode.setText(valueText)
	textNode.setAlign(TextNode.ACenter)
	textNode.setFont(font)
	textNode.setTextColor(color)
	if wordWrap > 0: textNode.setWordwrap(wordWrap)
	if cardColor:
		textNode.setCardColor(cardColor)
		textNode.setCardAsMargin(0, 0.1, 0, -0.10)
		textNode.setCardDecal(True)
	textNodePath = np_Parent.attachNewNode(textNode)
	textNodePath.setScale(scale)
	textNodePath.setPosHpr(pos, Point3(0, -90, 0))
	return textNodePath, textNode

def textNode_ExpandSetShrink(textNodePath, textNode, scale_0, scale_1, s, color, duration=0.15):
	return Sequence(textNodePath.scaleInterval(duration=duration, scale=scale_1),
					Func(textNode.setText, s), Func(textNode.setTextColor, color),
					textNodePath.scaleInterval(duration=duration, scale=scale_0)
					)

def textNode_setTextandColor(textNode, text, color):
	textNode.setText(text)
	textNode.setTextColor(color)
	
def reassignBtn2Card(btn, card):
	card.btn = btn
	
"""Subclass the NodePath, since it can be assigned attributes directly"""
class Btn_Card:
	def __init__(self, GUI, card, nodePath):
		self.GUI, self.card = GUI, card
		self.selected = self.isPlayed = False
		self.onlyCardBackShown = False
		
		self.np = nodePath #Load the templates, who won't carry btn and then btn will be assigned after copyTo()
		self.cNode = self.cNode_Backup = self.cNode_Backup_Played = None  #cNode holds the return value of attachNewNode
		self.box = None
		self.models, self.icons, self.texts, self.texCards = {}, {}, {}, {}
		self.texCards_Dyna = []
		
	def changeCard(self, card, isPlayed, pickable=True, onlyShowCardBack=False):
		self.card, self.isPlayed = card, isPlayed
		self.np.name = "NP_{}_{}".format(type(card).__name__, datetime.now().microsecond)
		loader = self.GUI.loader
		if pickable: card.btn = self
		while self.texCards_Dyna:
			self.texCards_Dyna.pop().removeNode()
		self.reloadModels(loader, findFilepath(card), pickable, onlyShowCardBack)
		self.np.reparentTo(self.GUI.render)
		self.onlyCardBackShown = onlyShowCardBack
	
	def reassignBox(self):
		card = self.card
		isLegendary = "~Legendary" in card.index
		if card.type == "Minion":
			for name in ("box_Legendary", "box_Normal", "box_Legendary_Played", "box_Normal_Played"):
				self.models[name].setColor(transparent)
			if isLegendary: self.box = self.models["box_Legendary_Played" if self.isPlayed else "box_Legendary"]
			else: self.box = self.models["box_Normal_Played" if self.isPlayed else "box_Normal"]
		elif card.type == "Weapon":
			self.box = None if self.isPlayed else self.models["box_Legendary" if isLegendary else "box_Normal"]
		elif card.type == "Hero":
			self.box = self.models["box_Played" if self.isPlayed else "box"]
		elif card.type == "Dormant":
			self.box = None
			
	def reloadModels(self, loader, imgPath, pickable, onlyShowCardBack):
		pass
	
	def texCardAni_LoopPose(self, name, start=True):
		seqNode = self.texCards[name].find("+SequenceNode").node()
		if start: seqNode.loop(False, 1, seqNode.getNumFrames()-1)
		else: seqNode.pose(0)
	
	def texCardAni_PlayPlay(self, name, end_Gain, start_Lose, end_Lose, gain=True):
		seqNode = self.texCards[name].find("+SequenceNode").node()
		if gain and 0 <= seqNode.getFrame() < end_Gain: seqNode.play(seqNode.getFrame(), end_Gain)
		elif not gain and 0 < seqNode.getFrame() <= end_Gain: seqNode.play(start_Lose, end_Lose)
	
	def texCardAni_LoopPlay(self, name, end_Gain, start_Lose, end_Lose, gain=True):
		seqNode = self.texCards[name].find("+SequenceNode").node()
		if gain: seqNode.loop(False, 1, end_Gain)
		elif not gain and 0 < seqNode.getFrame() <= end_Gain: seqNode.play(start_Lose, end_Lose)
	
	def addaStatusTexCard2Top(self, texCard_New, seqNode_New, num_0, num_1, playorLoop, x_New, y_New):
		i = 0
		for texCard in self.texCards_Dyna[:]:
			seqNode = texCard.find("+SequenceNode").node()
			if seqNode.isPlaying() or seqNode.getFrame() != seqNode.getNumFrames() - 1:
				x, y, z = texCard.getPos()
				texCard.setPos(x, y, 0.17+i*0.03)
				i += 1
			else: #If the texCard is not playing anymore or not waiting at the start, remove it
				self.texCards_Dyna.remove(texCard)
				texCard.removeNode()
		texCard_New.setPos(x_New, y_New, 0.17+i*0.03)
		texCard_New.reparentTo(self.np)
		if playorLoop:
			Sequence(Func(seqNode_New.play, num_0, num_1), Wait(seqNode_New.getNumFrames()/24), Func(texCard_New.removeNode)).start()
		else: seqNode_New.loop(num_0, num_1)
		
	def dimDown(self):
		self.np.setColor(grey)
		
	def setBoxColor(self, color):
		if self.box: self.box.setColor(color)
	
	def showStatus(self):
		pass
	
	def rightClick(self):
		if self.GUI.UI in (1, 2): self.GUI.cancelSelection()
		else: self.GUI.drawCardZoomIn(self)
	
	def manaChangeAni(self, mana_1):  #mana_1 is the value the mana changes to
		card = self.card
		btn, cardType = card.btn, type(card)
		if not btn or btn.onlyCardBackShown: return  #If the btn doesn't exist anymore, skip the rest
		nodePath, scale_0 = btn.texts["mana"], statTextScale if card.type != "Power" else 0.857 * statTextScale
		color = white if card.mana == cardType.mana else (red if card.mana > cardType.mana else green)
		sequence = Sequence(nodePath.scaleInterval(duration=0.15, scale=2 * statTextScale),
							Func(nodePath.node().setText, str(mana_1)),
							nodePath.scaleInterval(duration=0.15, scale=scale_0),
							Func(nodePath.node().setTextColor, color))
		self.GUI.seqHolder[-1].append(Func(sequence.start))
	
	#Minion actions: "set"|"buffDebuff"|"damage"|"heal"
	#Weapon actions: "buffDebuff"|"damage"
	#Hero actions:
	def statChangeAni(self, num1=None, num2=None, action="set"):
		card = self.card
		#只有是在场上的英雄或手牌中/场上的随从/武器才能够进行
		if not ((card.type == "Hero" and card.onBoard) or
				(card.type in ("Minion", "Weapon") and (card.inHand or card.onBoard))):
			return
		cardType = type(card)
		#Decide all the values, text colors, npTexts and nodeTexts
		attack, health = card.attack, card.health
		if card.type == "Weapon": color_Health = red if health < card.health_max else (white if card.health_max <= cardType.durability else green)
		else: color_Health = red if health < card.health_max else (white if card.health_max <= cardType.health else green)
		seq_Holder = self.GUI.seqHolder[-1]
		
		npText_Health_Played, nodeText_Health_Played = self.texts["health_Played"], self.texts["health_Played"].node()
		if action in ("set", "buffDebuff"):  #一般的攻击力和耐久度重置计算也可以用set，只是需要把num1和num2设为0
			if card.type == "Hero" and not self.isPlayed: return
			
			color_Attack = white if card.attack <= cardType.attack else green
			scale_0 = {"Hero": 1.1, "Weapon": 0.9, "Minion": 0.8}[card.type] if self.isPlayed else statTextScale
			
			para = Parallel()
			if not self.isPlayed and action == "buffDebuff":
				scale = self.np.getScale()[0]
				para.append(Sequence(Func(print, "buffDebuff scale", scale), LerpScaleInterval(self.np, duration=0.17, scale=1.2*scale), LerpScaleInterval(self.np, duration=0.17, scale=scale)))
			
			if self.isPlayed: npText, nodeText = self.texts["attack_Played"], self.texts["attack_Played"].node()
			else: npText, nodeText = self.texts["attack"], self.texts["attack"].node()
			s = '' if card.type == "Hero" and attack < 1 else str(attack)
			if num1: para.append(Func(textNode_ExpandSetShrink(npText, nodeText, scale_0, 2 * scale_0, s, color_Attack).start))
			else: para.append(Func(textNode_setTextandColor, nodeText, s, color_Attack))
			
			if self.isPlayed: npText, nodeText = npText_Health_Played, nodeText_Health_Played
			else: npText, nodeText = self.texts["health"], self.texts["health"].node()
			if num2: para.append(Func(textNode_ExpandSetShrink(npText, nodeText, scale_0, 2 * scale_0, str(health), color_Health).start))
			else: para.append(Func(textNode_setTextandColor, nodeText, str(health), color_Health))
				
			if card.type == "Hero": para.append(Func(self.models["attack"].setColor, white if attack > 0 else transparent))
			seq_Holder.append(para)
		else: #damage|healing|armorChange
			if not self.isPlayed: return
			if card.type == "Weapon": #"damage"
				seq_Holder.append(Func(textNode_setTextandColor, nodeText_Health_Played, str(health), color_Health))
			elif card.type == "Minion": #"damage" or "healing"
				if action == "poisonousDamage": s, color, texCardName, num = '', white, "DamagePoisonous", 48
				elif action == "damage": s, color, texCardName, num = str(num2), red, "Damage", 48
				else: s, color, texCardName, num = '+' + str(num2), black, "Healing", 32
				
				texCard, seqNode = makeTexCard(self.GUI, "TexCards\\Shared\\%s.egg"%texCardName, scale=3)
				if s:
					textNodePath, textNode = makeText(np_Parent=texCard, textName='', valueText=s, pos=(0, -0.01, -0.05), scale=0.25, color=color, font=self.GUI.font)
					textNodePath.setHpr(0, 0, 0)
				seq_Holder.append(Func(textNode_setTextandColor, nodeText_Health_Played, str(health), color_Health))
				seq_Holder.append(Func(self.addaStatusTexCard2Top, texCard, seqNode, 1, num, True, 0.15, 0.45))
			else: #Hero
				armor, npText_Armor_Played, nodeText_Armor_Played, model_Armor_Played = card.armor, self.texts["armor_Played"], self.texts["armor_Played"].node(), self.models["armor"]
				color_Armor, s_Armor = transparent if armor < 1 else white, '' if armor < 1 else str(armor)
				if action == "armorChange":  #For hero
					seq_Holder.append(Func(model_Armor_Played.setColor, color_Armor))
					seq_Holder.append(Func(textNode_ExpandSetShrink(npText_Armor_Played, nodeText_Armor_Played, 1.1, 2*1.1, s_Armor, white).start))
				else:
					if action == "damage": s, color, texCardName, num = str(num2), red, "Damage", 48
					else: s, color, texCardName, num = '+' + str(num2), black, "Healing", 32
					
					texCard, seqNode = makeTexCard(self.GUI, "TexCards\\Shared\\%s.egg"%texCardName, scale=4)
					textNodePath, textNode = makeText(np_Parent=texCard, textName='', valueText=s, pos=(0, -0.01, -0.05), scale=0.25, color=color, font=self.GUI.font)
					textNodePath.setHpr(0, 0, 0)
					
					seq_Holder.append(Func(textNode_setTextandColor, nodeText_Health_Played, str(health), color_Health))
					seq_Holder.append(Func(model_Armor_Played.setColor, color_Armor))
					seq_Holder.append(Func(nodeText_Armor_Played.setText, s_Armor))
					seq_Holder.append(Func(self.addaStatusTexCard2Top, texCard, seqNode, 1, num, True, 0.15, 0.25))
					
	def placeIcons(self):
		pass
	
	def genMoPathIntervals(self, curveFileName, duration=0.3):
		moPath = Mopath.Mopath()
		moPath.loadFile(curveFileName)
		return MopathInterval(moPath, self.np, duration=duration)
	
	#For the selfCopy method, this will simply return a None
	def selfCopy(self, Copy):
		return None
	
def loadCard(base, card):
	return {"Minion": loadMinion, "Spell": loadSpell, "Weapon": loadWeapon, "Hero": loadHero,
			"Power": loadPower, "Dormant": loadMinion, "Option": loadOption,
			}[card.type](base)
	
tableTexCards_Minions = {"Aura": (7.2, (0, 0.3, -0.03)),
						"Taunt": (5.5, (0.05, -0.05, 0)),
						"Frozen": (5.2, (0, 0.55, 0.07)),
						"Immune": (4.5, (0.05, 0.5, 0.08)),
						"Stealth": (4.2, (0.1, 0.5, 0.09)),
						"Divine Shield": (7.3, (0.05, 0.2, 0.10)),
						"Silenced": (4, (0, 0, 0.11)),
						"Exhausted": (5, (0.1, 0.5, 0.12)),
						"Spell Damage": (4, (0, 1, 0.13)),
						
						#"Damage": (3.5, (0.15, 0.45, 0.17)),
						#"DamagePoisonous": (3.5, (0.15, 0.45, 0.18)),
						#"Healing": (3.5, (0.1, 0.5, 0.19)),
						}
	
#Minion: cardImage y limit -0.06; nameTag -0.07; stats_Played -0.12

#Need to calculate the curve in order to align the trig icons with the name tag
arr_x = np.array([-1, -0.44, 0.12, 1.24])
arr_y = np.array([-1.37, -1.26, -1.17, -1.12])
arr = np.array([[x**3, x**2, x**1, 1] for x in arr_x])
coeffs_Curve = np.linalg.solve(arr, arr_y)

def x2y_MinionNameTagCurve(x, coeffs):
	return coeffs[0] * x ** 3 + coeffs[1] * x ** 2 + coeffs[2] * x + coeffs[3]

class Btn_Minion(Btn_Card):
	def __init__(self, GUI, card, nodePath):
		super().__init__(GUI, card, nodePath)
		
		self.cNode_Backup = CollisionNode("Minion_cNode_Card")
		self.cNode_Backup.addSolid(CollisionBox(Point3(0.05, -1.1, 0), 2.2, 3.1, 0.1))
		self.cNode_Backup_Played = CollisionNode("Minion_cNode_Played")
		self.cNode_Backup_Played.addSolid(CollisionBox(Point3(0.07, 0.35, 0), 1.5, 1.9, 0.1))
		#self.cNode = self.attachNewNode(self.cNode_Backup)
		
	def reloadModels(self, loader, imgPath, pickable, onlyShowCardBack):
		card = self.card
		if self.isPlayed: color4Card, color4Played = transparent, white
		else: color4Card, color4Played = white, transparent
		isLegendary = "~Legendary" in card.index if card.type == "Minion" else \
						("~Legendary" in card.minionInside.index if card.minionInside else True) #Is dormant
		self.models["legendaryIcon"].setColor(white if isLegendary else transparent)
		self.reassignBox()
		
		if self.cNode:
			self.cNode.removeNode()
			self.cNode = None
		if pickable:
			self.cNode = self.np.attachNewNode(self.cNode_Backup_Played \
												   if self.isPlayed or card.type != "Minion" else self.cNode_Backup)
			#self.cNode.show()
		cardTexture = loader.loadTexture(imgPath)
		for modelName in ("card", "cardImage", "nameTag"):
			self.models[modelName].setTexture(self.models[modelName].findTextureStage('*'), cardTexture, 1)
			
		#Change the card textNodes no matter what (non-mutable texts are empty anyways)
		self.texts["description"].node().setText('' if self.isPlayed else '{}'.format(card.text(CHN)))
		
		for modelName in ("cardImage", "nameTag"):
			self.models[modelName].setColor(white)
		for modelName in ("mana", "stats", "cardBack", "card"):
			self.models[modelName].setColor(color4Card)
		self.models["stats_Played"].setColor(color4Played if card.type == "Minion" else transparent)
		self.models["stats"].setColor(color4Card if card.type == "Minion" else transparent)
		
		if card.type == "Minion":
			cardType = type(card)
			#Refresh the mana
			color = white if card.mana == cardType.mana else (green if card.mana < cardType.mana else red)
			self.texts["mana"].node().setText(str(card.mana) if card.mana > -1 else '')
			self.texts["mana"].node().setTextColor(transparent if self.isPlayed else color)
			#Refresh the attack
			color = white if card.attack <= card.attack_0 else green
			color_Attack = transparent if self.isPlayed else color
			color_Attack_Played = color if self.isPlayed else transparent
			self.texts["attack"].node().setText(str(card.attack))
			self.texts["attack"].node().setTextColor(color_Attack)
			self.texts["attack_Played"].node().setText(str(card.attack))
			self.texts["attack_Played"].node().setTextColor(color_Attack_Played)
			#Refresh the health
			color = red if card.health < card.health_max else (white if card.health_max <= cardType.health else green)
			color_Health = transparent if self.isPlayed else color
			color_Health_Played = color if self.isPlayed else transparent
			#print("Changing minion health:", card.name, color_Attack, color_Attack_Played)
			self.texts["health"].node().setText(str(card.health))
			self.texts["health"].node().setTextColor(color_Health)
			self.texts["health_Played"].node().setText(str(card.health))
			self.texts["health_Played"].node().setTextColor(color_Health_Played)
		else: #休眠物不进行数值显示
			for name in ("mana", "attack", "attack_Played", "health", "health_Played"):
				self.texts[name].node().setText('')
				
		if onlyShowCardBack:
			for model in self.models.values(): model.setColor(transparent)
			for textNodePath in self.texts.values(): textNodePath.node().setTextColor(transparent)
			self.models["cardBack"].setColor(white)
			
	def leftClick(self):
		if self.card.type != "Minion": return
		self.selected = not self.selected
		GUI, card = self.GUI, self.card
		UI, game = GUI.UI, GUI.Game
		if self.isPlayed: #When the minion is on board
			if UI == 0 or UI == 2:
				self.GUI.resolveMove(self.card, self, "MiniononBoard")
		else: #When the minion is in hand
			if UI == -1:
				self.setBoxColor(red if self.selected else green)
				GUI.mulliganStatus[card.ID][game.mulligans[card.ID].index(card)] = 1 if self.selected else 0
			elif UI == 0: GUI.resolveMove(card, self, "MinioninHand")
			elif UI == 3 and card in game.options: GUI.resolveMove(card, None, "DiscoverOption")
			
	#需要用inverval.start
	def effectChangeAni(self, name=''):
		if self.card.type != "Minion": return
		card, para = self.card, Parallel(name="Status Change Ani")
		#Handle the loop(False)/pose(0) type of texCards: Aura, Immune, Stealth, Exhausted, Silenced
		if not name or name == "Aura":  #Check the Aura animation
			para.append(Func(self.texCardAni_LoopPose, "Aura", card.onBoard and card.auras != {}))
		if not name or name == "Immune":
			para.append(Func(self.texCardAni_LoopPose, "Immune", card.onBoard and card.effects["Immune"] > 0))
		if not name or name == "Spell Damage":
			para.append(Func(self.texCardAni_LoopPose, "Spell Damage", card.onBoard and card.effects["Spell Damage"] + card.effects["Nature Spell Damage"] > 0))
		if not name or name == "Stealth":
			para.append(Func(self.texCardAni_LoopPose, "Stealth", card.onBoard and card.effects["Stealth"] + card.effects["Temp Stealth"] > 0))
		if not name or name in ("Exhausted", "Rush", "Charge"):
			para.append(Func(self.texCardAni_LoopPose, "Exhausted", card.onBoard and not card.actionable()))
		if not name or name == "Silenced":
			para.append(Func(self.texCardAni_LoopPose, "Silenced", card.onBoard and card.silenced))
		#Handle the play(num1, num2)/play(num1, num2) type of texCards: Divine Shield, Taunt
		if not name or name == "Divine Shield":
			if card.onBoard: para.append(Func(self.texCardAni_PlayPlay, "Divine Shield", 23, 24, 29, card.effects["Divine Shield"] > 0))
			else: para.append(Func(self.texCardAni_LoopPose, "Divine Shield", False))
		if not name or name == "Taunt":
			if card.onBoard: para.append(Func(self.texCardAni_PlayPlay, "Taunt", 13, 14, 28, card.effects["Taunt"] > 0))
			else: para.append(Func(self.texCardAni_LoopPose, "Taunt", False))
		#Handle the loop(False, num1, num2)/play(num1, num2) type of texCards: Frozen
		if not name or name == "Frozen":
			if card.onBoard: para.append(Func(self.texCardAni_LoopPlay, "Frozen", 96, 97, 105, card.effects["Frozen"] > 0))
			else: para.append(Func(self.texCardAni_LoopPose, "Frozen", False))
			
		if self.GUI.seqHolder: self.GUI.seqHolder[-1].append(para)
		else: para.start()
	
	def decideColor(self):
		color, card = transparent, self.card
		if card.type != "Minion": return color
		game = card.Game
		if card == self.GUI.subject: color = pink
		elif card == self.GUI.target: color = blue
		elif card.ID == game.turn:
			if card.inHand:
				if game.Manas.affordable(card, canbeTraded=False) and game.space(card.ID) > 0:
					color = yellow if card.effectViable else green
				elif "~Tradeable" in card.index and game.Manas.affordable(card, canbeTraded=True):
					color = green
			elif card.canAttack():
				if card.effects["Can't Attack Hero"] > 0 or (card.enterBoardTurn == game.numTurn and card.effects["Rush"] > 0 and
															 card.effects["Borrowed"] + card.effects["Charge"] < 1):
					color = darkGreen #如果随从可以攻击但是不能攻击对方英雄，即有“不能直接攻击英雄”或者是没有冲锋或暗影狂乱的突袭随从
				else: color = green #If this is a minion that is on board
		return color
		
	#Place the "Trigger", "Deathrattle", "Lifesteal", "Poisonous" icons at the right places
	def placeIcons(self):
		card, para, icons = self.card, Parallel(name="Icon Placing Ani"), []
		#Both dormants and minions can have hourglass and trigger
		if self.isPlayed and any(trig.counter > -1 for trig in card.trigsBoard):
			btn_Icon = self.icons["Hourglass"]
			para.append(btn_Icon.seqUpdateText(s='', animate=False))
			icons.append(btn_Icon)
		else: para.append(Func(self.icons["Hourglass"].np.setColor, transparent))
		
		if self.isPlayed and any(trig.counter < 0 and not trig.oneTime for trig in card.trigsBoard):
			icons.append(self.icons["Trigger"])
		else: para.append(Func(self.icons["Trigger"].np.setColor, transparent))
		
		if card.type == "Minion" and self.isPlayed and any(trig.oneTime for trig in card.trigsBoard):
			para.append(Func(self.icons["SpecTrig"].np.find("SpecTrig").setColor, white))
			icons.append(self.icons["SpecTrig"])
		else: para.append(Func(self.icons["SpecTrig"].np.setColor, transparent))
		
		if card.type == "Minion" and self.isPlayed and card.deathrattles: icons.append(self.icons["Deathrattle"])
		else: para.append(Func(self.icons["Deathrattle"].np.setColor, transparent))
		
		for keyWord in ("Lifesteal", "Poisonous"):
			if card.type == "Minion" and self.isPlayed and card.effects[keyWord]: icons.append(self.icons[keyWord])
			else: para.append(Func(self.icons[keyWord].np.setColor, transparent))
			
		nameTagModel = self.models["nameTag"]
		if icons:
			para.append(Func(nameTagModel.setTexture, nameTagModel.findTextureStage('0'),
							self.GUI.loader.loadTexture("Models\\MinionModels\\DarkNameTag.png"), 1))
			leftMostPos = 0.12 - 0.6 * (len(icons) - 1) / 2
			for i, model in enumerate(icons):
				para.append(Func(model.np.setColor, white))
				x = leftMostPos + i * 0.6
				para.append(Func(model.np.setPos, x, x2y_MinionNameTagCurve(x, coeffs_Curve), 0.115))
		else:
			para.append(Func(nameTagModel.setTexture, nameTagModel.findTextureStage('*'),
							 self.GUI.loader.loadTexture(findFilepath(card)), 1))
		if self.GUI.seqHolder: self.GUI.seqHolder[-1].append(para)
		else: para.start()
		
		
statTextScale = 1.05
manaPos = Point3(-2.8, 3.85, -0.15)
healthPos = Point3(3.1, -4.95, -0.2)
attackPos = Point3(-2.85, -4.95, -0.15)

#loadMinion, etc will prepare all the textures and trigIcons to be ready.
def loadMinion(base):
	loader = base.loader
	font = base.font
	root = loader.loadModel("Models\\MinionModels\\Minion.glb")
	root.name = "NP_Minion"
	
	#Model names: box_Legendary, box_Legendary_Played, box_Normal, box_Normal_Played
	# card, cardBack, cardImage, legendaryIcon, nameTag, stats, stats_Played
	for model in root.getChildren():
		model.setTransparency(True)
		#Only retexture the cardBack, legendaryIcon, stats, stats_Played models.
		#These models will be shared by all minion cards.
		if model.name == "cardBack": texture = base.textures["cardBack"]
		elif model.name in ("legendaryIcon", "mana", "stats", "stats_Played"): texture = base.textures["stats_Minion"]
		else: continue
		model.setTexture(model.findTextureStage('*'), texture, 1)
	
	makeText(root, "mana", '0', pos=(-1.78, 1.15, 0.09), scale=statTextScale,
			 color=white, font=font)
	makeText(root, "attack", '0', pos=(-1.63, -4.05, 0.09), scale=statTextScale,
			 color=white, font=font)
	makeText(root, "health", '0', pos=(1.85, -4.05, 0.09), scale=statTextScale,
			 color=white, font=font)
	makeText(root, "attack_Played", '0', pos=(-1.2, -0.74, 0.122), scale=0.8,
			 color=white, font=font)
	makeText(root, "health_Played", '0', pos=(1.32, -0.74, 0.122), scale=0.8,
			 color=white, font=font)
	makeText(root, "description", "", pos=(0.7, -2, 0.1), scale=0.5,
			 color=black, font=font, wordWrap=12, cardColor=yellow)
	
	for name in ("Hourglass", "Trigger", "SpecTrig", "Deathrattle", "Lifesteal", "Poisonous"):
		base.modelTemplates[name].copyTo(root)
	
	#print("Check minion loading:")
	#for child in root.getChildren():
	#	print(child)
	for name, posScale in tableTexCards_Minions.items():
		makeTexCard(base, "TexCards\\ForMinions\\%s.egg" % name,
					pos=posScale[1], scale=posScale[0], name=name)[0].reparentTo(root)
		
	#After the loading, the NP_Minion root tree structure is:
	#NP_Minion/card|stats|cardImage, etc
	#NP_Minion/mana_TextNode|attack_TextNode, etc
	#NP_Minion/Trigger_Icon|Deathrattle_Icon, etc
	#NP_Minion/Aura_TexCard, etc
	return root


"""Load Spell Cards"""
class Btn_Spell(Btn_Card):
	def __init__(self, GUI, card, nodePath):
		super().__init__(GUI, card, nodePath)
		
		self.cNode_Backup = CollisionNode("Spell_cNode")
		self.cNode_Backup.addSolid(CollisionBox(Point3(0.05, -1.1, 0), 2.2, 3.1, 0.1))
		
	def reloadModels(self, loader, imgPath, pickable, onlyShowCardBack):
		card = self.card
		isLegendary = "~Legendary" in card.index
		self.models["legendaryIcon"].setColor(white if isLegendary else transparent)
		self.models["box_Normal"].setColor(transparent)
		self.models["box_Legendary"].setColor(transparent)
		self.box = self.models["box_Legendary" if isLegendary else "box_Normal"]
		
		if self.cNode:
			self.cNode.removeNode()
			self.cNode = None
		if pickable:
			self.cNode = self.np.attachNewNode(self.cNode_Backup)
			#self.cNode.show()
			
		texture = loader.loadTexture(imgPath)
		self.models["mana"].setColor(white)
		model = self.models["card"]
		model.setColor(white)
		model.setTexture(model.findTextureStage('*'), texture, 1)
		
		self.texts["description"].node().setText("{}".format(card.text(CHN)))
		
		cardType = type(card)
		color = white if card.mana == cardType.mana else (red if card.mana > cardType.mana else green)
		self.texts["mana"].node().setText(str(card.mana) if card.mana > -1 else '')
		self.texts["mana"].node().setTextColor(color)
		
		if onlyShowCardBack:
			for model in self.models.values(): model.setColor(transparent)
			for textNodePath in self.texts.values(): textNodePath.node().setTextColor(transparent)
			self.models["cardBack"].setColor(white)
	
	def leftClick(self):
		self.selected = not self.selected
		GUI, card = self.GUI, self.card
		if GUI.UI == -1:
			self.setBoxColor(red if self.selected else green)
			GUI.mulliganStatus[card.ID][GUI.Game.mulligans[card.ID].index(card)] = 1 if self.selected else 0
		elif GUI.UI == 0: GUI.resolveMove(card, self, "SpellinHand")
		elif GUI.UI == 3 and card in GUI.Game.options: GUI.resolveMove(card, None, "DiscoverOption")
		
	def decideColor(self):
		color, card = transparent, self.card
		if card == self.GUI.subject: color = pink
		elif card == self.GUI.target: color = blue
		elif card.ID == card.Game.turn and card.inHand:
			if card.inHand and card.Game.Manas.affordable(card, canbeTraded=False) and card.available():
				color = yellow if card.effectViable else green
			elif "~Tradeable" in card.index and card.Game.Manas.affordable(card, canbeTraded=True):
				color = green
		return color
		
		
def loadSpell(base):
	loader = base.loader
	font = base.font
	root = loader.loadModel("Models\\SpellModels\\Spell.glb")
	root.name = "NP_Spell"
	
	#Model names: box_Legendary, box_Normal, card, cardBack, legendaryIcon, mana
	for model in root.getChildren():
		model.setTransparency(True)
		if model.name == "cardBack": texture = base.textures["cardBack"]
		elif model.name in ("mana", "legendaryIcon"): texture = base.textures["stats_Spell"]
		else: continue
		model.setTexture(model.findTextureStage('*'), texture, 1)
	
	makeText(root, "mana", '0', pos=(-1.8, 1.2, 0.09), scale=statTextScale,
			 color=white, font=font, wordWrap=0)
	makeText(root, "description", '', pos=(0.7, -2, 0.1), scale=0.5,
			 color=black, font=font, wordWrap=12, cardColor=yellow)
	#After the loading, the NP_Spell root tree structure is:
	#NP_Spell/card|cardBack|legendaryIcon, etc
	#NP_Spell/mana_TextNode|description_TextNode
	return root

#Weapon: cardImage y limit -0.09; nameTag -0.095; stats_Played -0.13
tableTexCards_Weapons = {"Immune": (3.7, (0.1, 0.3, 0.12)),
						}

"""Load Weapon Cards"""
class Btn_Weapon(Btn_Card):
	def __init__(self, GUI, card, nodePath):
		super().__init__(GUI, card, nodePath)
		
		self.cNode_Backup = CollisionNode("Weapon_cNode_Card")
		self.cNode_Backup.addSolid(CollisionBox(Point3(0.05, -1.1, 0), 2.2, 3.1, 0.1))
		self.cNode_Backup_Played = CollisionNode("Weapon_cNode_Played")
		self.cNode_Backup_Played.addSolid(CollisionBox(Point3(0.07, 0.33, 0), 1.8, 1.8, 0.1))
		
	def reloadModels(self, loader, imgPath, pickable, onlyShowCardBack):
		card = self.card
		if self.isPlayed: color4Card, color4Played = transparent, white
		else: color4Card, color4Played = white, transparent
		isLegendary = "~Legendary" in card.index
		self.models["legendaryIcon"].setColor(white if isLegendary else transparent)
		self.models["box_Normal"].setColor(transparent)
		self.models["box_Legendary"].setColor(transparent)
		self.reassignBox()
		
		if self.cNode:
			self.cNode.removeNode()
			self.cNode = None
		if pickable:
			self.cNode = self.np.attachNewNode(self.cNode_Backup_Played if self.isPlayed else self.cNode_Backup)
			#self.cNode.show()
		self.models["card"].setTexture(self.models["card"].findTextureStage('*'),
										self.GUI.textures["weapon_"+card.Class], 1)
		
		cardTexture = loader.loadTexture(imgPath)
		for modelName in ("cardImage", "nameTag", "description"):
			self.models[modelName].setTexture(self.models[modelName].findTextureStage('*'), cardTexture, 1)
			
		for modelName in ("cardImage", "nameTag", "border"):
			self.models[modelName].setColor(white)
		for modelName in ("stats", "cardBack", "card", "description"):
			self.models[modelName].setColor(color4Card)
		self.models["stats_Played"].setColor(color4Played)
		
		cardType = type(card)
		color = white if card.mana == cardType.mana else (green if card.mana < cardType.mana else red)
		self.texts["mana"].node().setText(str(card.mana) if card.mana > -1 else '')
		self.texts["mana"].node().setTextColor(transparent if self.isPlayed else color)
		#Refresh the attack
		color = white if card.attack <= cardType.attack else green
		self.texts["attack"].node().setText(str(card.attack))
		self.texts["attack"].node().setTextColor(transparent if self.isPlayed else color)
		self.texts["attack_Played"].node().setText(str(card.attack))
		self.texts["attack_Played"].node().setTextColor(color if self.isPlayed else transparent)
		#Weapon health
		color = red if card.health < card.health_max else (white if card.health_max <= cardType.durability else green)
		self.texts["health"].node().setText(str(card.health))
		self.texts["health"].node().setTextColor(transparent if self.isPlayed else color)
		self.texts["health_Played"].node().setText(str(card.health))
		self.texts["health_Played"].node().setTextColor(color if self.isPlayed else transparent)
		
		if onlyShowCardBack:
			for model in self.models.values(): model.setColor(transparent)
			for textNodePath in self.texts.values(): textNodePath.node().setTextColor(transparent)
			self.models["cardBack"].setColor(white)
	
	def leftClick(self):
		if not self.isPlayed:
			self.selected = not self.selected
			GUI, card = self.GUI, self.card
			game = GUI.Game
			if GUI.UI == -1:
				self.setBoxColor(red if self.selected else green)
				GUI.mulliganStatus[card.ID][game.mulligans[card.ID].index(card)] = 1 if self.selected else 0
			elif GUI.UI == 0: GUI.resolveMove(card, self, "WeaponinHand")
			elif GUI.UI == 3 and card in game.options: GUI.resolveMove(card, None, "DiscoverOption")
			
	#需要用inverval.start
	def effectChangeAni(self, name=''):
		card, para = self.card, Parallel(name="Status Change Ani")
		if not name or name == "Immune":
			para.append(Func(self.texCardAni_LoopPose, "Immune", card.effects["Immune"] > 0))
		
		if self.GUI.seqHolder: self.GUI.seqHolder[-1].append(para)
		else: para.start()
			
	#Place the "Trigger", "Deathrattle", "Lifesteal", "Poisonous" icons at the right places
	def placeIcons(self):
		card, para, icons = self.card, Parallel(name="Icon Placing Ani"), []
		if self.isPlayed and any(trig.counter > -1 for trig in self.card.trigsBoard):
			btn_Icon = self.icons["Hourglass"]
			para.append(btn_Icon.seqUpdateText(s='', animate=False))
			icons.append(btn_Icon)
		else: para.append(Func(self.icons["Hourglass"].np.setColor, transparent))
		
		if self.isPlayed and any(trig.counter < 0 and not trig.oneTime for trig in self.card.trigsBoard):
			icons.append(self.icons["Trigger"])
		else: para.append(Func(self.icons["Trigger"].np.setColor, transparent))
		
		if self.isPlayed and any(trig.oneTime for trig in self.card.trigsBoard):
			para.append(Func(self.icons["SpecTrig"].np.find("SpecTrig").setColor, white))
			icons.append(self.icons["SpecTrig"])
		else: para.append(Func(self.icons["SpecTrig"].np.setColor, transparent))
		
		if self.isPlayed and self.card.deathrattles: icons.append(self.icons["Deathrattle"])
		else: para.append(Func(self.icons["Deathrattle"].np.setColor, transparent))
		
		for keyWord in ("Lifesteal", "Poisonous"):
			if self.isPlayed and self.card.effects[keyWord]: icons.append(self.icons[keyWord])
			else: para.append(Func(self.icons[keyWord].np.setColor, transparent))
		
		nameTagModel = self.models["nameTag"]
		if icons:
			para.append(Func(nameTagModel.setTexture, nameTagModel.findTextureStage("*"),
							self.GUI.loader.loadTexture("Models\\WeaponModels\\DarkNameTag.png"), 1))
			leftMostPos = -0.6 * (len(icons) - 1) / 2
			for i, model in enumerate(icons):
				para.append(Func(model.np.setColor, white))
				para.append(Func(model.np.setPos, leftMostPos + i * 0.6, -1.13, 0.125))
		else:
			para.append(Func(nameTagModel.setTexture, nameTagModel.findTextureStage("*"),
							self.GUI.loader.loadTexture(findFilepath(self.card)), 1))
		self.GUI.seqHolder[-1].append(para)
		
	def decideColor(self):
		if self.isPlayed: return transparent
		color, card = transparent, self.card
		cardType, GUI, game = card.type, self.GUI, card.Game
		if card == GUI.subject: color = pink
		elif card == GUI.target: color = blue
		elif card.inHand and card.ID == game.turn:
			if game.Manas.affordable(card, canbeTraded=False):
				color = yellow if card.effectViable else green
			elif "~Tradeable" in card.index and game.Manas.affordable(card, canbeTraded=True):
				color = green
		return color
		
		
def loadWeapon(base):
	loader = base.loader
	font = base.font
	root = loader.loadModel("Models\\WeaponModels\\Weapon.glb")
	root.name = "NP_Weapon"
	
	#Model names: border, box_Legendary, box_Normal, card, cardBack, cardImage, description,
	# legendaryIcon, nameTag, stats, stats_Played
	for model in root.getChildren():
		model.setTransparency(True)
		if model.name == "cardBack": texture = base.textures["cardBack"]
		elif model.name in ("border", "legendaryIcon", "stats", "stats_Played"): texture = base.textures["stats_Weapon"]
		else: continue
		model.setTexture(model.findTextureStage('*'), texture, 1)
		
	makeText(root, "mana", '0', pos=(-1.75, 1.23, 0.11), scale=statTextScale,
			  color=white, font=font)
	makeText(root, "attack", '0', pos=(-1.7, -4, 0.12), scale=statTextScale,
			  color=white, font=font)
	makeText(root, "health", '0', pos=(1.8, -4, 0.12), scale=statTextScale,
			  color=white, font=font)
	makeText(root, "attack_Played", '0', pos=(-1.28, -0.8, 0.132), scale=0.9,
			  color=white, font=font)
	makeText(root, "health_Played", '0', pos=(1.27, -0.8, 0.132), scale=0.9,
				  color=white, font=font)
	
	for name in ("Hourglass", "Trigger", "SpecTrig", "Deathrattle", "Lifesteal", "Poisonous"):
		base.modelTemplates[name].copyTo(root)
		
	for name, posScale in tableTexCards_Weapons.items():
		makeTexCard(base, "TexCards\\ForWeapons\\%s.egg" % name,
					pos=posScale[1], scale=posScale[0], name=name)[0].reparentTo(root)
		
	#After the loading, the NP_Weapon root tree structure is:
	#NP_Weapon/card|stats|cardImage, etc
	#NP_Weapon/mana_TextNode|attack_TextNode, etc
	#NP_Weapon/Trigger_Icon|Deathrattle_Icon, etc
	return root


"""Load Hero Powers"""
tableTexCards_Powers = {"Power Damage": (3.5, (0, 0.25, 0.13)),
						"Can Target Minions": (2, (0, 0.25, 0.11)),
						}

class Btn_Power(Btn_Card):
	def __init__(self, GUI, card, nodePath):
		super().__init__(GUI, card, nodePath)
		
		self.cNode_Backup = CollisionNode("Power_cNode")
		self.cNode_Backup.addSolid(CollisionBox(Point3(0, -1.6, 0), 2.3, 3, 0.1))
		self.cNode_Backup_Played = CollisionNode("Power_cNode_Played")
		self.cNode_Backup_Played.addSolid(CollisionBox(Point3(0, 0.3, 0), 1.6, 1.6, 0.1))
		
	def reloadModels(self, loader, imgPath, pickable, onlyShowCard=True):
		card = self.card
		self.box = self.models["box"] if self.isPlayed else None
		self.models["box"].setColor(transparent)
		
		for modelName in ("card", "nameTag"):
			self.models[modelName].setColor(transparent if self.isPlayed else white)
		if self.cNode:
			self.cNode.removeNode()
			self.cNode = None
		if pickable:
			self.cNode = self.np.attachNewNode(self.cNode_Backup_Played if self.isPlayed else self.cNode_Backup)
			#self.cNode.show()
		"""The card frame. The front face texture is set according to it class"""
		texture = loader.loadTexture(imgPath)
		for modelName in ("card", "cardImage", "nameTag"):
			self.models[modelName].setTexture(self.models[modelName].findTextureStage('*'), texture, 1)
		self.texts["description"].node().setText('' if self.isPlayed else "{}".format(card.text(CHN)))
		
		cardType = type(card)
		#Refresh the mana
		color = white if card.mana == cardType.mana else (green if card.mana < cardType.mana else red)
		self.texts["mana"].node().setText(str(card.mana) if card.mana > -1 else '')
		self.texts["mana"].node().setTextColor(color)
	
		if onlyShowCard:
			for model in self.models.values(): model.setColor(transparent)
			for textNodePath in self.texts.values(): textNodePath.node().setTextColor(transparent)
		self.models["cardBack"].setColor(white if onlyShowCard else transparent)
		
	def checkHpr(self):
		hprFinal = None
		if self.card.ID == self.GUI.Game.turn:
			if self.card.chancesUsedUp() and self.np.get_r() < 180:
				hprFinal = (0, 0, 180)  #Flip to back, power unusable
			elif not self.card.chancesUsedUp() and self.np.get_r() > 0:
				hprFinal = (0, 0, 0) #Flip to front
		if hprFinal:
			x, y, z = self.GUI.heroZones[self.card.ID].powerPos
			interval = Sequence(LerpPosHprInterval(self.np, duration=0.17, pos=(x, y, z+3), hpr=(0, 0, 90)),
								LerpPosHprInterval(self.np, duration=0.17, pos=(x, y, z), hpr=hprFinal)
								)
			self.GUI.seqHolder[-1].append(Func(interval.start))
			
	def effectChangeAni(self, name=''):
		card, para = self.card, Parallel(name="Status Change Ani")
		#Handle the loop(False)/pose(0) type of texCards: Power Damage
		if not name or name in ("Damage Boost", "Power Damage"):
			para.append(Func(self.texCardAni_LoopPose, "Power Damage", card.onBoard and card.effects["Damage Boost"] + card.Game.effects[card.ID]["Power Damage"] > 0))
		if not name or name in ("Can Target Minions", "Power Can Target Minions"):
			para.append(Func(self.texCardAni_LoopPose, "Can Target Minions", card.onBoard and card.effects["Can Target Minions"] + card.Game.effects[card.ID]["Power Can Target Minions"] > 0))
		print("Power status change", name in ("Can Target Minions", "Power Can Target Minions"), card.onBoard, card.effects["Can Target Minions"] > 0, card.Game.effects[card.ID]["Power Can Target Minions"] > 0)
		if self.GUI.seqHolder: self.GUI.seqHolder[-1].append(para)
		else: para.start()
		
	def leftClick(self):
		if self.isPlayed:
			if self.GUI.UI == 0: self.GUI.resolveMove(self.card, self, "Power")
		else: #Discover a power.
			if self.GUI.UI == 3 and self.card in self.GUI.Game.options:
				self.GUI.resolveMove(self.card, None, "DiscoverOption")
		
	def decideColor(self):
		color, card = transparent, self.card
		if self.isPlayed and card.ID == card.Game.turn and card.Game.Manas.affordable(card) and card.available():
			color = green
		return color
	
	def placeIcons(self):
		para, icons = Parallel(name="Icon Placing Ani"), []
		#Both dormants and minions can have hourglass and trigger
		if self.isPlayed and any(trig.counter > -1 for trig in self.card.trigsBoard):
			btn_Icon = self.icons["Hourglass"]
			para.append(btn_Icon.seqUpdateText(s='', animate=False))
			icons.append(btn_Icon)
		else: para.append(Func(self.icons["Hourglass"].np.setColor, transparent))
		#Power doesn't have oneTime triggers
		if self.isPlayed and any(trig.counter < 0 for trig in self.card.trigsBoard):
			icons.append(self.icons["Trigger"])
		else: para.append(Func(self.icons["Trigger"].np.setColor, transparent))
		
		if self.isPlayed and self.card.effects["Lifesteal"]:
			icons.append(self.icons["Lifesteal"])
		else: para.append(Func(self.icons["Lifesteal"].np.setColor, transparent))
		
		if icons:
			leftMostPos = 0.12 - 0.6 * (len(icons) - 1) / 2
			for i, model in enumerate(icons):
				para.append(Func(model.np.setColor, white))
				x = leftMostPos + i * 0.6
				para.append(Func(model.np.setPos, x, -1, 0.11))
		
		if self.GUI.seqHolder: self.GUI.seqHolder[-1].append(para)
		else: para.start()
		
def loadPower(base):
	loader = base.loader
	font = base.font
	root = loader.loadModel("Models\\PowerModels\\Power.glb")
	root.name = "NP_Power"
	
	#Model names: box, card, cardImage, description, nameTag, mana
	for model in root.getChildren():
		model.setTransparency(True)
		if model.name in ("border", "mana"): texture = base.textures["stats_Power"]
		elif model.name == "cardBack": texture = base.textures["cardBack"]
		else: continue
		model.setTexture(model.findTextureStage('*'), texture, 1)
	#y limit: mana -0.12, description -0.025
	makeText(root, "mana", '0', pos=(0, 1.36, 0.125), scale=0.857*statTextScale, #0.9,
			color=white, font=font)
	makeText(root, "description", '', pos=(1, -2.5, 0.027), scale=0.5,
			color=black, font=font, wordWrap=10, cardColor=yellow)
	
	for name, posScale in tableTexCards_Powers.items():
		makeTexCard(base, "TexCards\\ForPowers\\%s.egg" % name,
					pos=posScale[1], scale=posScale[0], name=name)[0].reparentTo(root)
		
	for name in ("Hourglass", "Trigger", "Lifesteal"):
		base.modelTemplates[name].copyTo(root)
	
	#After the loading, the NP_Minion root tree structure is:
	#NP_Power/card|mana|cardImage, etc
	#NP_Power/mana_TextNode|description_TextNode
	#NP_Power/Trigger
	return root


"""Load Hero Cards"""
tableTexCards_Heroes = {"Breaking": (4.3, Point3(0, 0.27, 0.01)),
						"Frozen": (8, 	  Point3(-0.1, 0.2, 0.06)),
						"Immune": (5.2,   Point3(0, 0.3, 0.07)),
						"Stealth": (5.5,  Point3(0, 0.15, 0.08)),
						"Spell Damage": (4.8, Point3(0, 0.2, 0.09)),
						
						#"Damage": (4, Point3(0, 0.1, 0.10)),
						#"Healing": (4, Point3(0, 0.1, 0.11)),
						}

class Btn_Hero(Btn_Card):
	def __init__(self, GUI, card, nodePath):
		super().__init__(GUI, card, nodePath)
		
		self.cNode_Backup = CollisionNode("Hero_cNode")
		self.cNode_Backup.addSolid(CollisionBox(Point3(0.05, -1.1, 0), 2.2, 3.1, 0.1))
		self.cNode_Backup_Played = CollisionNode("Hero_cNode_Played")
		self.cNode_Backup_Played.addSolid(CollisionBox(Point3(0.05, 0.25, 0), 2, 2.2, 0.1))
		
	def reloadModels(self, loader, imgPath, pickable, onlyShowCardBack):
		if self.isPlayed: color4Card, color4Played = transparent, white
		else: color4Card, color4Played = white, transparent
		self.models["box"].setColor(transparent)
		self.models["box_Played"].setColor(transparent)
		self.reassignBox()
		for modelName in ("frame", "cardImage"): #the attack, health and armor will be handle by refresh
			self.models[modelName].setColor(color4Played)
		for modelName in ("card", "cardBack", "stats", "box"):
			self.models[modelName].setColor(color4Card)
		
		if self.cNode:
			self.cNode.removeNode()
			self.cNode = None
		if pickable:
			self.cNode = self.np.attachNewNode(self.cNode_Backup_Played if self.isPlayed else self.cNode_Backup)
			#self.cNode.show()
		self.models["cardImage"].setTexture(self.models["cardImage"].findTextureStage('*'),
											loader.loadTexture("Images\\HeroesandPowers\\%s.png"%type(self.card).__name__), 1)
		self.models["card"].setTexture(self.models["card"].findTextureStage('*'),
									   loader.loadTexture(imgPath), 1)
		
		card, cardType = self.card, type(self.card)
		self.models["attack"].setColor(white if self.isPlayed and card.attack > 0 else transparent)
		self.models["health"].setColor(white if self.isPlayed else transparent)
		self.models["armor"].setColor(white if self.isPlayed and card.armor > 0 else transparent)
		
		color = white if card.mana == cardType.mana else (green if card.mana < cardType.mana else red)
		self.texts["mana"].node().setText(str(card.mana) if card.mana > -1 else '')
		self.texts["mana"].node().setTextColor(transparent if self.isPlayed else color)
		#Refresh the attack
		self.texts["attack_Played"].node().setText(str(card.attack))
		self.texts["attack_Played"].node().setTextColor(green if card.attack > 0 and self.isPlayed else transparent)
		#Refresh the health
		self.texts["health_Played"].node().setText(str(card.health))
		self.texts["health_Played"].node().setTextColor((red if card.health < card.health_max else (white if card.health_max <= cardType.health else green))
														if self.isPlayed else transparent)
		#Refresh the armor the hero card has
		self.texts["armor"].node().setText(str(card.armor))
		self.texts["armor"].node().setTextColor(transparent if self.isPlayed else white)
		self.texts["armor_Played"].node().setText(str(card.armor))
		self.texts["armor_Played"].node().setTextColor(white if card.armor > 0 and self.isPlayed else transparent)
	
		if onlyShowCardBack:
			for model in self.models.values(): model.setColor(transparent)
			for textNodePath in self.texts.values(): textNodePath.node().setTextColor(transparent)
			self.models["cardBack"].setColor(white)
	
	def leftClick(self):
		self.selected = not self.selected
		GUI, card = self.GUI, self.card
		UI, game = GUI.UI, GUI.Game
		if self.isPlayed:
			if UI == 0 or UI == 2: self.GUI.resolveMove(self.card, self, "HeroonBoard")
		else:
			if UI == -1:
				self.setBoxColor(red if self.selected else green)
				GUI.mulliganStatus[card.ID][game.mulligans[card.ID].index(card)] = 1 if self.selected else 0
			elif UI == 0: GUI.resolveMove(card, self, "HeroinHand")
			elif GUI.UI == 3 and card in game.options: GUI.resolveMove(card, None, "DiscoverOption")
	
	def effectChangeAni(self, name=''):
		card, para = self.card, Parallel(name="Status Change Ani")
		#Handle the loop(False)/pose(0) type of texCards: Immune, Stealth, Spell Damage
		if not name or name == "Immune":
			para.append(Func(self.texCardAni_LoopPose, "Immune", card.Game.effects[card.ID]["Immune"] > 0))
		if not name or name == "Spell Damage":
			para.append(Func(self.texCardAni_LoopPose, "Spell Damage", card.Game.effects[card.ID]["Spell Damage"] > 0))
		if not name or name == "Temp Stealth":
			para.append(Func(self.texCardAni_LoopPose, "Stealth", card.effects["Temp Stealth"] > 0))
		##Handle the loop(False, num1, num2)/play(num1, num2) type of texCards: Frozen
		if not name or name == "Frozen":
			para.append(Func(self.texCardAni_LoopPlay, "Frozen", 96, 97, 105, card.effects["Frozen"] > 0))
			
		if self.GUI.seqHolder: self.GUI.seqHolder[-1].append(para)
		else: para.start()
		
	def decideColor(self):
		color, card = transparent, self.card
		if card == self.GUI.subject: color = pink
		elif card == self.GUI.target: color = blue
		elif not self.isPlayed and card.inHand and card.ID == card.Game.turn and card.Game.Manas.affordable(card):
			color = green
		elif self.isPlayed and card.onBoard and card.canAttack(): color = green
		return color
		
		
def loadHero(base):
	loader = base.loader
	font = base.font
	root = loader.loadModel("Models\\HeroModels\\Hero.glb")
	root.name = "NP_Hero"
	
	#Model names: armor, attack, box, box_Played, card, cardBack, cardImage, frame, health, stats
	for model in root.getChildren():
		model.setTransparency(True)
		if model.name == "cardBack": texture = base.textures["cardBack"]
		elif model.name in ("stats", "armor", "attack", "frame", "health"):
			texture = base.textures["stats_Hero"]
		else: continue
		model.setTexture(model.findTextureStage('*'), texture, 1)
		
	makeText(root, "mana", '0', pos=(-1.73, 1.15, 0.09), scale=statTextScale,
			  color=white, font=font)
	makeText(root, "armor", '0', pos=(1.81, -4.02, 0.09), scale=statTextScale,
			  color=white, font=font)
	makeText(root, "attack_Played", '0', pos=(-2.15*0.88, -2.38*0.88, 0.122), scale=1.1,
			  color=white, font=font)
	makeText(root, "health_Played", '0', pos=(2.2*0.88, -2.38*0.88, 0.122), scale=1.1,
			  color=white, font=font)
	makeText(root, "armor_Played", '0', pos=(2.2*0.88, -0.8*0.88, 0.122), scale=1.1,
				  color=white, font=font)
	
	for name, posScale in tableTexCards_Heroes.items():
		filePath = "TexCards\\ForHeroes\\%s.egg" % name
		if not os.path.isfile(filePath): filePath = "TexCards\\ForMinions\\%s.egg" % name
		makeTexCard(base, filePath, pos=posScale[1], scale=posScale[0], name=name, parent=root)
		
	#After the loading, the NP_Minion root tree structure is:
	#NP_Hero/card|stats|cardImage, etc
	#NP_Hero/mana_TextNode|attack_TextNode, etc
	#NP_Hero/Frozen_TexCard, etc
	return root


class Btn_Trigger:
	def __init__(self, carrierBtn, nodePath):
		self.carrierBtn, self.np = carrierBtn, nodePath
		self.seqNode = nodePath.find("TexCard").find("+SequenceNode").node()
		
	def trigAni(self): #Index of last frame is 47
		if self.seqNode.isPlaying(): self.seqNode.play(self.seqNode.getFrame(), 48)
		else: self.seqNode.play(1, 48)
		
class Btn_SpecTrig:
	def __init__(self, carrierBtn, nodePath):
		self.carrierBtn, self.np = carrierBtn, nodePath
		self.seqNode = nodePath.find("TexCard").find("+SequenceNode").node()
	
	def trigAni(self):
		sequence = Sequence(Func(self.seqNode.play), Wait(0.4),
							Func(self.np.find("SpecTrig").setColor, transparent),
							Wait(0.7))
		self.carrierBtn.GUI.seqHolder[-1].append(sequence)
		
class Btn_Hourglass:
	#nodePath has following structure: Hourglass/Hourglass
											   #/Trig Counter
	def __init__(self, carrierBtn, nodePath):
		self.carrierBtn, self.np = carrierBtn, nodePath
		self.i = 0
		
	def seqUpdateText(self, s='', animate=True):
		model, counterText = self.np.find("Hourglass"), self.np.find("Trig Counter_TextNode")
		counterTextNode = counterText.node()
		if not s:
			s = ""
			for trig in self.carrierBtn.card.trigsBoard:
				if (animate and trig.counter > -1) or (not animate and trig.counter> 0):
					s += str(trig.counter) + ' '
		if animate:
			self.i += 1
			return Sequence(LerpHprInterval(model, duration=0.5, hpr=(self.i*360, 0, 0)),
							LerpScaleInterval(counterText, duration=0.25, scale=1.2),
					 		Func(counterTextNode.setText, s),
					 		LerpScaleInterval(counterText, duration=0.25, scale=0.6)
							)
		else: return Func(counterTextNode.setText, s)

class Btn_Deathrattle:
	def __init__(self, carrierBtn, nodePath):
		self.carrierBtn, self.np = carrierBtn, nodePath
		
class Btn_Lifesteal:
	def __init__(self, carrierBtn, nodePath):
		self.carrierBtn, self.np = carrierBtn, nodePath
		self.seqNode = nodePath.find("TexCard").find("+SequenceNode").node()
	
	def trigAni(self):
		if self.seqNode.isPlaying():
			self.seqNode.play(self.seqNode.getFrame(), self.seqNode.getNumFrames())
		else:
			self.seqNode.play(1, self.seqNode.getNumFrames())

class Btn_Poisonous:
	def __init__(self, carrierBtn, nodePath):
		self.carrierBtn, self.np = carrierBtn, nodePath
		self.seqNode = nodePath.find("TexCard").find("+SequenceNode").node()
		
	def trigAni(self):
		if self.seqNode.isPlaying():
			self.seqNode.play(self.seqNode.getFrame(), self.seqNode.getNumFrames())
		else:
			self.seqNode.play(1, self.seqNode.getNumFrames())


#Used for secrets and quests
class Btn_Secret:
	def __init__(self, GUI, card, nodePath):
		self.GUI, self.card = GUI, card
		self.onlyCardBackShown = self.selected = False
		self.np = nodePath
		
	def dimDown(self):
		self.np.setColor(grey)
	
	def setBoxColor(self, color):
		pass
	
	def checkHpr(self):
		hpr = None
		if self.card.ID == self.GUI.Game.turn and self.np.get_r() < 180:
			hpr = (0, 0, 180)  #Flip to back, unusable
		elif self.card.ID != self.GUI.Game.turn and self.np.get_r() > 0:
			hpr = (0, 0, 0)
		if hpr: self.GUI.seqHolder[-1].append(Func(LerpHprInterval(self.np, duration=0.3, hpr=hpr).start))
			
	def leftClick(self):
		pass
	
	def rightClick(self):
		if self.GUI.UI in (1, 2): self.GUI.cancelSelection()
		else: self.GUI.drawCardZoomIn(self)

pos_QuestFinish = (0, 1.5, 20)
scale_HeroZoneTrigCounter = 0.6

class Btn_HeroZoneTrig:
	def __init__(self, GUI, card, nodePath):
		self.GUI, self.card = GUI, card
		self.onlyCardBackShown = self.selected = False
		self.np = nodePath
		self.counterText = nodePath.find("Trig Counter_TextNode")
		
	def reassignCardBtn(self, card):
		card.btn = self
		
	def dimDown(self):
		self.np.setColor(grey)
		
	def setBoxColor(self, color):
		pass
	
	def trigAni(self, newValue):
		sequence = Sequence(LerpScaleInterval(self.counterText, duration=0.25, scale=1.2),
							Func(self.counterText.node().setText, '' if newValue == 0 else str(newValue)),
							LerpScaleInterval(self.counterText, duration=0.25, scale=scale_HeroZoneTrigCounter)
							)
		if self.GUI.seqHolder: self.GUI.seqHolder[-1].append(sequence)
		else: sequence.start()
		
	def finishAni(self, newQuest=None, reward=None):
		card, pos_0 = self.card, self.np.getPos()
		nodePath, btn = genCard(self.GUI, card, isPlayed=False, pickable=False, scale=0.1, makeNewRegardless=True)
		sequence = Sequence(Func(self.np.removeNode),
							LerpPosHprScaleInterval(nodePath, duration=0.5, startPos=pos_0, pos=pos_QuestFinish, hpr=(0, 0, 0), scale=(1, 1, 1)), Wait(0.5)
							)
		if newQuest:
			sequence.append(LerpHprInterval(nodePath, duration=0.3, hpr=(0, 0, 180)) )
			sequence.append(Func(btn.changeCard, newQuest, False, False))
			sequence.append(LerpHprInterval(nodePath, duration=0.3, hpr=(0, 0, 360)) )
			sequence.append(Wait(0.7))
			sequence.append(LerpPosHprScaleInterval(btn.np, duration=0.5, pos=pos_0, hpr=(0, 0, 360), scale=0.1))
			sequence.append(Func(nodePath.removeNode))
			nodePath_New, btn_New = genHeroZoneTrigIcon(self.GUI, newQuest)
			sequence.append(Func(nodePath_New.setPos, pos_0))
		elif reward:
			nodePath_Reward, btn_Reward = genCard(self.GUI, reward, isPlayed=False, pickable=True, pos=(0, 0, 0.2))
			sequence.append(LerpHprInterval(nodePath, duration=0.3, hpr=(0, 0, 180)))
			sequence.append(Func(nodePath_Reward.reparentTo, nodePath))
			sequence.append(LerpHprInterval(nodePath, duration=0.3, hpr=(0, 0, 360)))
			sequence.append(Wait(0.7))
			sequence.append(Func(nodePath_Reward.wrtReparentTo, self.GUI.render))
			sequence.append(Func(nodePath.removeNode))
		else: #No new quest or reward to add to hand.
			sequence.append(Func(nodePath.removeNode))
		sequence.append(Func(self.GUI.heroZones[card.ID].placeSecrets))
		
		self.GUI.seqHolder[-1].append(sequence)
		
	def leftClick(self):
		pass
	
	def rightClick(self):
		if self.GUI.UI: self.GUI.cancelSelection() #Only responds when UI is 0
		else: self.GUI.drawCardZoomIn(self)

	
class Btn_Option:
	def __init__(self, GUI, option, nodePath):
		self.GUI, self.card = GUI, option
		option.btn = self
		self.np = nodePath
		
	def leftClick(self):
		self.GUI.resolveMove(self.card, self, "ChooseOneOption" if self.GUI.UI == 1 else "DiscoverOption")
		
	def rightClick(self):
		pass
	
	
def loadOption(base):
	loader = base.loader
	texture = base.textures["stats_Minion"]
	font = base.font
	root =  loader.loadModel("Models\\Option.glb")
	root.name = "NP_Option"
	
	#Model names: card, cardImage, mana, stats
	nodePath = root.find("mana")
	nodePath.setTransparency(True)
	nodePath.setTexture(nodePath.findTextureStage('0'), texture, 1)
	root.find("cardImage").setTransparency(True)
	root.find("cardBack").setTransparency(True)
	nodePath = root.find("stats")
	nodePath.setTransparency(True)
	nodePath.setTexture(nodePath.findTextureStage('0'), texture, 1)
	nodePath = root.find("legendaryIcon")
	nodePath.setTransparency(True)
	nodePath.setTexture(nodePath.findTextureStage('0'), base.textures["stats_Spell"], 1)
	
	makeText(root, "mana", '', pos=(-1.75, 1.15, 0.09), scale=statTextScale,
			 color=white, font=font)
	makeText(root, "attack", '', pos=(-1.7, -4.05, 0.09), scale=statTextScale,
			 color=white, font=font)
	makeText(root, "health", '', pos=(1.8, -4.05, 0.09), scale=statTextScale,
			 color=white, font=font)
	
	cNode_Backup = CollisionNode("Option_cNode")
	cNode_Backup.addSolid(CollisionBox(Point3(0.05, -1.1, 0), 2.2, 3.1, 0.1))
	root.attachNewNode(cNode_Backup)
	
	return root


def genOption(GUI, option, pos=None, onlyShowCardBack=False):
	nodePath = GUI.modelTemplates["Option"].copyTo(GUI.render)
	if pos: nodePath.setPos(pos)
	btn_Card = Btn_Option(GUI, option, nodePath)
	nodePath.setPythonTag("btn", btn_Card)
	
	if onlyShowCardBack:
		for child in nodePath.getChildren():
			if child.name != "cardBack" and child.name != "Option_cNode":
				child.setColor(transparent)
	else:
		mana, attack, health = type(option).mana, type(option).attack, type(option).health
		if mana > -1: nodePath.find("mana_TextNode").node().setText(str(mana))
		if attack > -1: nodePath.find("attack_TextNode").node().setText(str(attack))
		if health > -1: nodePath.find("health_TextNode").node().setText(str(health))
		if attack < 0 or health < 0:
			nodePath.find("cardImage").setColor(transparent)
			nodePath.find("stats").setColor(transparent)
		else:
			model = nodePath.find("cardImage")
			model.setTexture(model.findTextureStage('0'),
							 GUI.loader.loadTexture(findFilepath(option)), 1)
		model = nodePath.find("card")
		model.setTexture(model.findTextureStage('0'),
						 GUI.loader.loadTexture(findFilepath(option)), 1)
		nodePath.find("legendaryIcon").setColor(white if option.isLegendary else transparent)
	
	return nodePath, btn_Card



Table_Type2Btn = {"Minion": Btn_Minion, "Spell": Btn_Spell, "Weapon": Btn_Weapon,
				  "Hero": Btn_Hero, "Power": Btn_Power, "Dormant": Btn_Minion,
				  "Trigger_Icon": Btn_Trigger, "Deathrattle_Icon": Btn_Deathrattle,
				  "Lifesteal_Icon": Btn_Lifesteal, "Poisonous_Icon": Btn_Poisonous,
				  "SpecTrig_Icon": Btn_SpecTrig, "Hourglass_Icon": Btn_Hourglass,
				  }


#np_Template is of type NP_Minion, etc and is kept by the GUI.
#card: card object, which the copied nodePath needs to become
#isPlayed: boolean, whether the card is in played form or not
#Only "Trigger", etc reference btn, others reference nodePath

#There are situations where new cards must always be made, like questline popping up from a Trig button
def genCard(GUI, card, isPlayed, pickable=True, pos=None, hpr=None, scale=None,
			onlyShowCardBack=False, makeNewRegardless=False):
	btn = card.btn
	if not makeNewRegardless and btn and btn.np:
		btn.np.reparentTo(GUI.render)
		if btn.isPlayed != isPlayed or btn.onlyCardBackShown != onlyShowCardBack:
			btn.changeCard(card, isPlayed=isPlayed, pickable=pickable, onlyShowCardBack=onlyShowCardBack)
		return btn.np, btn
	
	typeofCard = card.type if card.type != "Dormant" else "Minion"
	nodepath = GUI.modelTemplates[typeofCard].copyTo(GUI.render)
	if pos: nodepath.setPos(pos)
	if hpr: nodepath.setHpr(hpr)
	if scale: nodepath.setScale(scale)
	#NP_Minion root tree structure is:
	#NP_Minion/card|stats|cardImage, etc
	#NP_Minion/mana_TextNode|attack_TextNode, etc
	btn_Card = Table_Type2Btn[typeofCard](GUI, None, nodepath)
	nodepath.setPythonTag("btn", btn_Card)
	for nodePath in nodepath.getChildren():
		name = nodePath.name
		if "TextNode" in name: btn_Card.texts[name.replace("_TextNode", '')] = nodePath
		elif "TexCard" in name: btn_Card.texCards[name.replace("_TexCard", '')] = nodePath
		#Collision Nodes are not inserted into the template tree yet
		elif "_Icon" in name: btn_Card.icons[name.replace("_Icon", '')] = Table_Type2Btn[name](btn_Card, nodePath)
		else: btn_Card.models[name] = nodePath
	
	btn_Card.changeCard(card, isPlayed=isPlayed, pickable=pickable, onlyShowCardBack=onlyShowCardBack)
	return nodepath, btn_Card


def genSecretIcon(GUI, card, pos=None, hpr=None):
	nodepath = GUI.loader.loadModel("Models\\HeroModels\\SecretIcon.glb")
	nodepath.setTexture(nodepath.findTextureStage('0'), GUI.textures["Secret_"+card.Class], 1)
	nodepath.reparentTo(GUI.render)
	if pos: nodepath.setPos(pos)
	if hpr: nodepath.setHpr(hpr)
	btn_Icon = Btn_Secret(GUI, card, nodepath)
	nodepath.setPythonTag("btn", btn_Icon)
	cNode = CollisionNode("Secret_cNode")
	cNode.addSolid(CollisionSphere(0, 0, 0, 0.5))
	nodepath.attachNewNode(cNode)#.show()
	return nodepath, btn_Icon


def genHeroZoneTrigIcon(GUI, card, pos=None, text=''):
	nodepath = GUI.loader.loadModel("Models\\HeroModels\\TurnTrig.glb")
	icon = nodepath.find("Icon")
	icon.setTexture(icon.findTextureStage('0'),
					GUI.loader.loadTexture(findFilepath(card)), 1)
	nodepath.reparentTo(GUI.render)
	textNode = TextNode("Trig Counter_TextNode")
	textNode.setText(text)
	textNode.setAlign(TextNode.ACenter)
	textNode.setTextColor(white)
	textNodePath = nodepath.attachNewNode(textNode)
	textNodePath.setPosHprScale(0.3, -0.33, 0.1, 0, -90, 0,
								scale_HeroZoneTrigCounter, scale_HeroZoneTrigCounter, scale_HeroZoneTrigCounter)
	if pos: nodepath.setPos(pos)
	btn_Icon = Btn_HeroZoneTrig(GUI, card, nodepath)
	card.btn = btn_Icon
	nodepath.setPythonTag("btn", btn_Icon)
	cNode = CollisionNode("HeroZoneTrig_cNode")
	cNode.addSolid(CollisionSphere(0, 0, 0, 0.6))
	nodepath.attachNewNode(cNode)  #.show()
	nodepath.setScale(1.2)
	return nodepath, btn_Icon


