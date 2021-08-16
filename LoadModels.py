from direct.interval.FunctionInterval import Func, Wait
from direct.interval.LerpInterval import *
from direct.interval.MetaInterval import Sequence, Parallel
from direct.directutil import Mopath
from direct.interval.MopathInterval import *
from panda3d.core import *
import inspect
from datetime import datetime


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
	
	
red, green, blue = Point4(1, 0, 0, 1), Point4(0.3, 1, 0.2, 1), Point4(0, 0, 1, 1)
yellow, pink = Point4(1, 1, 0, 1), Point4(1, 0, 1, 1)

transparent, grey = Point4(1, 1, 1, 0), Point4(0.5, 0.5, 0.5, 1)
black, white = Point4(0, 0, 0, 1), Point4(1, 1, 1, 1)


#Can only set the color of the textNode itself to transparent. No point in setting the nodePath transparency
def makeText(np_Parent, textName, valueText, pos, scale, color, font, wordWrap=0):
	textNode = TextNode(textName + "_TextNode")
	textNode.setText(valueText)
	textNode.setAlign(TextNode.ACenter)
	textNode.setFont(font)
	textNode.setTextColor(color)
	if wordWrap > 0:
		textNode.setWordwrap(wordWrap)
	textNodePath = np_Parent.attachNewNode(textNode)
	textNodePath.setScale(scale)
	textNodePath.setPosHpr(pos, Point3(0, -90, 0))
	return textNodePath

"""Subclass the NodePath, since it can be assigned attributes directly"""
class Btn_Card:
	def __init__(self, GUI, card, nodePath):
		self.GUI, self.card = GUI, card
		self.selected = self.isPlayed = False
		
		self.np = nodePath #Load the templates, who won't carry btn and then btn will be assigned after copyTo()
		self.cNode = self.cNode_Backup = self.cNode_Backup_Played = None  #cNode holds the return value of attachNewNode
		self.box_Model = None
		self.models, self.icons, self.texts, self.texCards = {}, {}, {}, {}
		
	def changeCard(self, card, isPlayed, pickable=True, onlyShowCardBack=False):
		reTexture = (self.card != card)
		self.card, self.isPlayed = card, isPlayed
		self.np.name = "NP_"+type(card).name+str(datetime.timestamp(datetime.now()))
		loader = self.GUI.loader
		if pickable: card.btn = self
		self.reloadModels(loader, findFilepath(card), pickable, reTexture, onlyShowCardBack)
		
	def reassignCardBtn(self, card):
		card.btn = self
		
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
	
	def dimDown(self):
		self.np.setColor(grey)
		
	def setBoxColor(self, color):
		if self.box_Model: self.box_Model.setColor(color)
	
	def showStatus(self):
		pass
	
	def rightClick(self):
		if self.GUI.UI in (1, 2): self.GUI.cancelSelection()
		else: self.GUI.drawCardZoomIn(self)
	
	def manaChangeAni(self, mana_1):  #mana_1 is the value the mana changes to
		card = self.card
		btn, cardType = card.btn, type(card)
		if not btn: return  #If the btn doesn't exist anymore, skip the rest
		nodePath, scale_0 = btn.texts["mana"], statTextScale if card.type != "Power" else 0.857 * statTextScale
		color = white if card.mana == cardType.mana else (red if card.mana > cardType.mana else green)
		sequence = Sequence(nodePath.scaleInterval(duration=0.15, scale=2 * statTextScale),
							Func(nodePath.node().setText, str(mana_1)),
							nodePath.scaleInterval(duration=0.15, scale=scale_0),
							Func(nodePath.node().setTextColor, color))
		self.GUI.seqHolder[-1].append(Func(sequence.start))
	
	def statusChangeAni(self, name=''):
		pass
	
	def placeIcons(self):
		pass
	
	#Control the moving, rotating and scaling of a nodePath. For color manipulate, another method is used.
	def genLerpInterval(self, pos=None, hpr=None, scale=None, duration=0.3, hpr_AlltheWay=None, blendType="noBlend"):
		pos = pos if pos else self.np.getPos()
		if hpr_AlltheWay: hpr = hpr_AlltheWay
		else: hpr = hpr if hpr else self.np.getHpr()
		scale = scale if scale else self.np.getScale()
		return LerpPosHprScaleInterval(self.np, duration=duration, pos=pos, hpr=hpr, scale=scale,
									   startHpr=hpr_AlltheWay, blendType=blendType)
	
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
	
	
#Minion: cardImage y limit -0.06; nameTag -0.07; stats_Played -0.12
table_PosScaleofTexCard_Minions = {"Aura": (0.057, (0, 0.3, -0.03)),
							   		"Damage": (0.05, (0.15, 0.45, 0.14)),
							   		"DamagePoisonous": (0.05, (0.15, 0.45, 0.143)),
							   		"Divine Shield": (7.3, (0.05, 0.2, 0.078)),
							   		"Exhausted": (5, (0.1, 0.5, 0.062)),
							   		"Frozen": (5.2, (0, 0.55, 0.08)),
							   		"Immune": (4.5, (0.05, 0.5, 0.076)),
							   		"Silenced": (4, (0, 0, 0.068)),
							   		"Spell Damage": (4, (0, 1, 0.07)),
							   		"Stealth": (4.4, (0.1, 0.5, 0.0645)),
							   		"Taunt": (0.044, (0.05, -0.05, 0)),
							   		}

class Btn_Minion(Btn_Card):
	def __init__(self, GUI, card, nodePath):
		super().__init__(GUI, card, nodePath)
		
		self.cNode_Backup = CollisionNode("Minion_cNode_Card")
		self.cNode_Backup.addSolid(CollisionBox(Point3(0.05, -1.1, 0), 2.2, 3.1, 0.1))
		self.cNode_Backup_Played = CollisionNode("Minion_cNode_Played")
		self.cNode_Backup_Played.addSolid(CollisionBox(Point3(0.07, 0.35, 0), 1.5, 1.9, 0.1))
		#self.cNode = self.attachNewNode(self.cNode_Backup)
		
	def reloadModels(self, loader, imgPath, pickable, reTexture, onlyShowCardBack):
		card = self.card
		if self.isPlayed: color4Card, color4Played = transparent, white
		else: color4Card, color4Played = white, transparent
		if card.type == "Minion":
			isLegendary = "~Legendary" in card.index
			for name in ("box_Legendary", "box_Normal", "box_Legendary_Played", "box_Normal_Played"):
				self.models[name].setColor(transparent)
			if isLegendary: self.box_Model = self.models["box_Legendary_Played" if self.isPlayed else "box_Legendary"]
			else: self.box_Model = self.models["box_Normal_Played" if self.isPlayed else "box_Normal"]
		else:
			isLegendary = "~Legendary" in card.minionInside.index if card.minionInside else True #Is dormant
			for name in ("box_Legendary", "box_Normal", "box_Legendary_Played", "box_Normal_Played"):
				self.models[name].setColor(transparent)
		self.models["legendaryIcon"].setColor(white if isLegendary else transparent)
		
		if self.cNode:
			self.cNode.removeNode()
			self.cNode = None
		if pickable:
			self.cNode = self.np.attachNewNode(self.cNode_Backup_Played \
												   if self.isPlayed or card.type != "Minion" else self.cNode_Backup)
			#self.cNode.show()
		cardTexture = loader.loadTexture(imgPath)
		if reTexture:
			for modelName in ("card", "cardImage", "nameTag", "race"):
				self.models[modelName].setTexture(self.models[modelName].findTextureStage('*'), cardTexture, 1)
				
		#Change the card textNodes no matter what (non-mutable texts are empty anyways)
		text = card.text(CHN)
		textNodePath = self.texts["description"]
		textNodePath.node().setText(text)
		textNodePath.setPos(0, -3 + 0.1 * len(text) / 12, 0.2)
		textNodePath.node().setTextColor(black if not self.isPlayed and text else transparent)
		if not self.isPlayed and text:
			model = self.models["description"]
			model.setTexture(model.findTextureStage('*'),
							self.GUI.textures["minion_%s" % card.index.split('~')[0]], 1)
			model.setColor(white)
		else: self.models["description"].setColor(transparent)
		
		for modelName in ("cardImage", "nameTag"):
			self.models[modelName].setColor(white)
		for modelName in ("mana", "stats", "cardBack", "card", "race"):
			self.models[modelName].setColor(color4Card)
		self.models["stats_Played"].setColor(color4Played if card.type == "Minion" else transparent)
		self.models["stats"].setColor(color4Card if card.type == "Minion" else transparent)
		
		if card.type == "Minion":
			cardType = type(card)
			#Refresh the mana
			color = white if card.mana == cardType.mana else (green if card.mana < cardType.mana else red)
			self.texts["mana"].node().setText(str(card.mana))
			self.texts["mana"].node().setTextColor(transparent if self.isPlayed else color)
			#Refresh the attack
			color = white if card.attack <= card.attack_0 else green
			color_Attack = transparent if self.isPlayed else color
			color_Attack_Played = color if self.isPlayed else transparent
			#print("Changing minion attack:", card.name, color_Attack, color_Attack_Played)
			self.texts["attack"].node().setText(str(card.attack))
			self.texts["attack"].node().setTextColor(color_Attack)
			self.texts["attack_Played"].node().setText(str(card.attack))
			self.texts["attack_Played"].node().setTextColor(color_Attack_Played)
			#Refresh the health
			color = white if card.health == card.health_max else (green if card.health > card.health_max else red)
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
			elif UI == 3 and card in game.options: GUI.resolveMove(card, None, "DiscoverOption", info=None)
			
	def statChangeAni(self, num1=None, num2=None, action="set"):
		card = self.card
		#Skip cards not inHand/onBoard or are dormants
		if not (card.inHand or card.onBoard or card.type != "Minion"): return
		color_Health = red if card.health < card.health_max else (green if card.health_max > type(card).health else white)
		if action == "set" or action == "buffDebuff": #一般的攻击力和生命值重置计算也可以用set，只是需要把num1和num2设为0
			parallel = Parallel(name="Stat Change Ani")
			color_Attack = white if card.attack <= card.attack_0 else green
			np_Text_Attack, np_Text_Attack_Played = self.texts["attack"], self.texts["attack_Played"]
			np_Text_Health, np_Text_Health_Played = self.texts["health"], self.texts["health_Played"]
			if num1:
				seq_Attack = Sequence(np_Text_Attack.scaleInterval(duration=0.15, scale=2*0.8 if self.isPlayed else (2*statTextScale)),
									  Func(np_Text_Attack.node().setText, str(card.attack)),
									  Func(np_Text_Attack.node().setTextColor, transparent if self.isPlayed else color_Attack),
									  np_Text_Attack.scaleInterval(duration=0.15, scale=0.8 if self.isPlayed else statTextScale)
									  )
				seq_Attack_Played = Sequence(np_Text_Attack_Played.scaleInterval(duration=0.15, scale=2*0.8 if self.isPlayed else 2*statTextScale),
											 Func(np_Text_Attack_Played.node().setText, str(card.attack)),
											 Func(np_Text_Attack_Played.node().setTextColor, color_Attack if self.isPlayed else transparent),
											 np_Text_Attack_Played.scaleInterval(duration=0.15, scale=0.8 if self.isPlayed else statTextScale)
											 )
				parallel.append(Func(seq_Attack.start))
				parallel.append(Func(seq_Attack_Played.start))
			else:
				parallel.append(Func(np_Text_Attack.node().setText, str(card.attack)))
				parallel.append(Func(np_Text_Attack.node().setTextColor, transparent if self.isPlayed else color_Attack))
				parallel.append(Func(np_Text_Attack_Played.node().setText, str(card.attack)))
				parallel.append(Func(np_Text_Attack_Played.node().setTextColor, color_Attack if self.isPlayed else transparent))
				
			if num2:
				seq_Health = Sequence(np_Text_Health.scaleInterval(duration=0.15, scale=2*0.8 if self.isPlayed else 2*statTextScale),
									  Func(np_Text_Health.node().setText, str(card.health)),
									  Func(np_Text_Health.node().setTextColor, transparent if self.isPlayed else color_Health),
									  np_Text_Health.scaleInterval(duration=0.15, scale=0.8 if self.isPlayed else statTextScale)
									  )
				seq_Health_Played = Sequence(np_Text_Health_Played.scaleInterval(duration=0.15, scale=2*0.8 if self.isPlayed else 2*statTextScale),
											 Func(np_Text_Health_Played.node().setText, str(card.health)),
											 Func(np_Text_Health_Played.node().setTextColor, color_Health if self.isPlayed else transparent),
											 np_Text_Health_Played.scaleInterval(duration=0.15, scale=0.8 if self.isPlayed else statTextScale)
											 )
				parallel.append(Func(seq_Health.start))
				parallel.append(Func(seq_Health_Played.start))
			else: #Only reset the value and color
				parallel.append(Func(np_Text_Health.node().setText, str(card.health)))
				parallel.append(Func(np_Text_Health.node().setTextColor, transparent if self.isPlayed else color_Health))
				parallel.append(Func(np_Text_Health_Played.node().setText, str(card.health)))
				parallel.append(Func(np_Text_Health_Played.node().setTextColor, color_Health if self.isPlayed else transparent))
			
			self.GUI.seqHolder[-1].append(parallel)
		elif action == "damage": #需要显示动画
			if card.inHand: return
			textNode = TextNode("Damage Text Node")
			textNode.setText(str(num2))
			textNode.setTextColor(red)
			textNode.setAlign(TextNode.ACenter)
			textNodePath = self.np.attachNewNode(textNode)
			textNodePath.setPosHprScale(0, 0, 0, 0, -90, 0, 1.6, 1.6, 1.6)
			#Total # of frames: 47. frame 48 will be the first frame
			sequence = Sequence(Func(self.texts["health_Played"].node().setText, str(card.health)),
								Func(self.texts["health_Played"].node().setTextColor, color_Health if self.isPlayed else transparent),
								Func(self.texCards["Damage"].find("+SequenceNode").node().play, 1, 48), Func(textNodePath.setPos, 0, 0.1, 0.15),
								Wait(1.5), Func(textNodePath.removeNode))
			self.GUI.seqHolder[-1].append(Func(sequence.start, name="Damage Ani"))
		elif action == "heal":
			if card.inHand: return
			textNode = TextNode("Heal Text Node")
			textNode.setText('+'+str(num2))
			textNode.setTextColor(yellow)
			textNode.setAlign(TextNode.ACenter)
			textNodePath = self.np.attachNewNode(textNode)
			textNodePath.setPosHprScale(0, 0, 0, 0, -90, 0, 1.6, 1.6, 1.6)
			sequence = Sequence(Func(self.texts["health_Played"].node().setText, str(card.health)),
								Func(self.texts["health_Played"].node().setTextColor, color_Health if self.isPlayed else transparent),
								Func(textNodePath.setPos, 0, 0.1, 0.0145),
								Wait(1.5), Func(textNodePath.removeNode))
			self.GUI.seqHolder[-1].append(Func(sequence.start, name="Heal Ani"))
		
	#需要用inverval.start
	def statusChangeAni(self, name=''):
		if self.card.type != "Minion": return
		card, para = self.card, Parallel(name="Status Change Ani")
		#Handle the loop(False)/pose(0) type of texCards: Aura, Immune, Stealth, Exhausted, Silenced
		if not name or name == "Aura":  #Check the Aura animation
			para.append(Func(self.texCardAni_LoopPose, "Aura", card.onBoard and card.auras != {}))
		if not name or name == "Immune":
			para.append(Func(self.texCardAni_LoopPose, "Immune", card.onBoard and card.status["Immune"] > 0))
		if not name or name == "Spell Damage":
			para.append(Func(self.texCardAni_LoopPose, "Spell Damage", card.onBoard and card.keyWords["Spell Damage"] + card.keyWords["Nature Spell Damage"] > 0))
		if not name or name == "Stealth":
			para.append(Func(self.texCardAni_LoopPose, "Stealth", card.onBoard and card.keyWords["Stealth"] + card.status["Temp Stealth"] > 0))
		if not name or name in ("Exhausted", "Rush", "Charge"):
			para.append(Func(self.texCardAni_LoopPose, "Exhausted", card.onBoard and not card.actionable()))
		if not name or name == "Silenced":
			para.append(Func(self.texCardAni_LoopPose, "Silenced", card.onBoard and card.silenced))
		#Handle the play(num1, num2)/play(num1, num2) type of texCards: Divine Shield, Taunt
		if not name or name == "Divine Shield":
			if card.onBoard: para.append(Func(self.texCardAni_PlayPlay, "Divine Shield", 23, 24, 29, card.keyWords["Divine Shield"] > 0))
			else: para.append(Func(self.texCardAni_LoopPose, "Divine Shield", False))
		if not name or name == "Taunt":
			if card.onBoard: para.append(Func(self.texCardAni_PlayPlay, "Taunt", 13, 14, 28, card.keyWords["Taunt"] > 0))
			else: para.append(Func(self.texCardAni_LoopPose, "Taunt", False))
		#Handle the loop(False, num1, num2)/play(num1, num2) type of texCards: Frozen
		if not name or name == "Frozen":
			if card.onBoard: para.append(Func(self.texCardAni_LoopPlay, "Frozen", 96, 97, 105, card.status["Frozen"] > 0))
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
				if game.Manas.affordable(card, forTrade=False) and game.space(card.ID) > 0:
					color = yellow if card.effectViable else green
				elif "~Tradeable" in card.index and game.Manas.affordable(card, forTrade=True):
					color = green
			elif card.canAttack(): color = green #If this is a minion that is on board
		return color
		
	#Place the "Trigger", "Deathrattle", "Lifesteal", "Poisonous" icons at the right places
	def placeIcons(self):
		para, icons = Parallel(name="Icon Placing Ani"), []
		if self.isPlayed and self.card.trigsBoard:
			para.append(Func(self.icons["Trigger"].updateText))
			icons.append(self.icons["Trigger"])
		else: para.append(Func(self.icons["Trigger"].np.setColor, transparent))
		
		if self.card.type == "Minion":
			para.append(Func(self.icons["SpecTrig"].np.find("SpecTrig").setColor, white))
			if self.isPlayed and any(trig.oneTime for trig in self.card.trigsBoard):
				icons.append(self.icons["SpecTrig"])
			else: para.append(Func(self.icons["SpecTrig"].np.setColor, transparent))
			
			if self.isPlayed and self.card.deathrattles:
				icons.append(self.icons["Deathrattle"])
			else: para.append(Func(self.icons["Deathrattle"].np.setColor, transparent))
			
			for keyWord in ("Lifesteal", "Poisonous"):
				if self.isPlayed and self.card.keyWords[keyWord]: icons.append(self.icons[keyWord])
				else: para.append(Func(self.icons[keyWord].np.setColor, transparent))
			
		leftMostPos = -0.6 * (len(icons) - 1) / 2
		for i, model in enumerate(icons):
			para.append(Func(model.np.setColor, white))
			para.append(Func(model.np.setPos, leftMostPos + i * 0.6, -1.9, 0.01))
			
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
	# card, cardBack, cardImage, description, legendaryIcon, nameTag, race, stats, stats_Played
	for model in root.getChildren():
		model.setTransparency(True)
		#Only retexture the cardBack, legendaryIcon, stats, stats_Played models.
		#These models will be shared by all minion cards.
		if model.name == "cardBack": texture = base.textures["cardBack"]
		elif model.name in ("legendaryIcon", "mana", "stats", "stats_Played"): texture = base.textures["stats_Minion"]
		else: continue
		model.setTexture(model.findTextureStage('*'), texture, 1)
	
	makeText(root, "mana", '0', pos=(-1.8, 1.15, 0.09), scale=statTextScale,
			 color=white, font=font)
	makeText(root, "attack", '0', pos=(-1.7, -4.05, 0.09), scale=statTextScale,
			 color=white, font=font)
	makeText(root, "health", '0', pos=(1.8, -4.05, 0.09), scale=statTextScale,
			 color=white, font=font)
	makeText(root, "attack_Played", '0', pos=(-1.2, -0.74, 0.122), scale=0.8,
			 color=white, font=font)
	makeText(root, "health_Played", '0', pos=(1.32, -0.74, 0.122), scale=0.8,
			 color=white, font=font)
	makeText(root, "description", "", pos=(0, 0, 0), scale=0.3,
			 color=black, font=font, wordWrap=12)
	base.modelTemplates["Trigger"].copyTo(root)
	base.modelTemplates["SpecTrig"].copyTo(root)
	base.modelTemplates["Deathrattle"].copyTo(root)
	base.modelTemplates["Lifesteal"].copyTo(root)
	base.modelTemplates["Poisonous"].copyTo(root)
	
	#print("Check minion loading:")
	#for child in root.getChildren():
	#	print(child)
	for name, posScale in table_PosScaleofTexCard_Minions.items():
		texCard = loader.loadModel("TexCards\\ForMinions\\%s.egg" % name)
		texCard.name = name + "_TexCard"
		texCard.reparentTo(root)
		texCard.setScale(posScale[0])
		texCard.setPosHpr(posScale[1], Point3(0, -90, 0))
		texCard.find("+SequenceNode").node().pose(0)
	
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
		
	def reloadModels(self, loader, imgPath, pickable, reTexture, onlyShowCardBack):
		card = self.card
		isLegendary = "~Legendary" in card.index
		self.models["legendaryIcon"].setColor(white if isLegendary else transparent)
		self.models["box_Normal"].setColor(transparent)
		self.models["box_Legendary"].setColor(transparent)
		self.box_Model = self.models["box_Legendary" if isLegendary else "box_Normal"]
		
		if self.cNode:
			self.cNode.removeNode()
			self.cNode = None
		if pickable:
			self.cNode = self.np.attachNewNode(self.cNode_Backup)
			#self.cNode.show()
			
		texture = loader.loadTexture(imgPath)
		if reTexture:
			for modelName in ("card", "school"):
				model = self.models[modelName]
				model.setTexture(model.findTextureStage('*'), texture, 1)
	
		text = card.text(CHN)
		textNodePath = self.texts["description"]
		textNodePath.node().setText(text)
		textNodePath.setPos(0, -3 + 0.1 * len(text) / 12, 0.2)
		textNodePath.node().setTextColor(black if not self.isPlayed and text else transparent)
		if not self.isPlayed and text:
			model = self.models["description"]
			model.setTexture(model.findTextureStage('*'),
							self.GUI.textures["spell_%s"%card.index.split('~')[0]], 1)
			model.setColor(white)
		else: self.models["description"].setColor(transparent)
		
		cardType = type(card)
		color = white if card.mana == cardType.mana else (red if card.mana > cardType.mana else green)
		self.texts["mana"].node().setText(str(card.mana))
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
		elif GUI.UI == 3 and card in GUI.Game.options: GUI.resolveMove(card, None, "DiscoverOption", info=None)
		
	def decideColor(self):
		color, card = transparent, self.card
		if card == self.GUI.subject: color = pink
		elif card == self.GUI.target: color = blue
		elif card.ID == card.Game.turn and card.inHand:
			if card.inHand and card.Game.Manas.affordable(card, forTrade=False) and card.available():
				color = yellow if card.effectViable else green
			elif "~Tradeable" in card.index and card.Game.Manas.affordable(card, forTrade=True):
				color = green
		return color
		
		
def loadSpell(base):
	loader = base.loader
	font = base.font
	root = loader.loadModel("Models\\SpellModels\\Spell.glb")
	root.name = "NP_Spell"
	
	#Model names: box_Legendary, box_Normal, card, cardBack, description, legendaryIcon, mana, school
	for model in root.getChildren():
		model.setTransparency(True)
		if model.name == "cardBack": texture = base.textures["cardBack"]
		elif model.name in ("mana", "legendaryIcon"): texture = base.textures["stats_Spell"]
		else: continue
		model.setTexture(model.findTextureStage('*'), texture, 1)
	
	makeText(root, "mana", '0', pos=(-1.73, 1.2, 0.09), scale=statTextScale,
			 color=white, font=font, wordWrap=0)
	makeText(root, "description", '', pos=(0, 0, 0), scale=0.25,
			 color=black, font=font, wordWrap=12)
	#After the loading, the NP_Spell root tree structure is:
	#NP_Spell/card|cardBack|legendaryIcon, etc
	#NP_Spell/mana_TextNode|description_TextNode
	return root

#Weapon: cardImage y limit -0.09; nameTag -0.095; stats_Played -0.13
table_PosScaleofTexCard_Weapons = {"Immune": (3.7, (0.1, 0.3, 0.12)),
						   }

"""Load Weapon Cards"""
class Btn_Weapon(Btn_Card):
	def __init__(self, GUI, card, nodePath):
		super().__init__(GUI, card, nodePath)
		
		self.cNode_Backup = CollisionNode("Weapon_cNode_Card")
		self.cNode_Backup.addSolid(CollisionBox(Point3(0.05, -1.1, 0), 2.2, 3.1, 0.1))
		self.cNode_Backup_Played = CollisionNode("Weapon_cNode_Played")
		self.cNode_Backup_Played.addSolid(CollisionBox(Point3(0.07, 0.33, 0), 1.8, 1.8, 0.1))
		
	def reloadModels(self, loader, imgPath, pickable, reTexture, onlyShowCardBack):
		card = self.card
		if self.isPlayed: color4Card, color4Played = transparent, white
		else: color4Card, color4Played = white, transparent
		isLegendary = "~Legendary" in card.index
		self.models["legendaryIcon"].setColor(white if isLegendary else transparent)
		self.models["box_Normal"].setColor(transparent)
		self.models["box_Legendary"].setColor(transparent)
		self.box_Model = None if self.isPlayed else self.models["box_Legendary" if isLegendary else "box_Normal"]
		
		if self.cNode:
			self.cNode.removeNode()
			self.cNode = None
		if pickable:
			self.cNode = self.np.attachNewNode(self.cNode_Backup_Played if self.isPlayed else self.cNode_Backup)
			#self.cNode.show()
		if reTexture:
			self.models["card"].setTexture(self.models["card"].findTextureStage('*'),
										   self.GUI.textures["weapon_"+card.Class], 1)
			
			cardTexture = loader.loadTexture(imgPath)
			for modelName in ("cardImage", "nameTag", "description"):
				self.models[modelName].setTexture(self.models[modelName].findTextureStage('*'), cardTexture, 1)
			
		for modelName in ("cardImage", "nameTag"):
			self.models[modelName].setColor(white)
		for modelName in ("stats", "cardBack", "card", "description"):
			self.models[modelName].setColor(color4Card)
		self.models["stats_Played"].setColor(color4Played)
		
		cardType = type(card)
		color = white if card.mana == cardType.mana else (green if card.mana < cardType.mana else red)
		self.texts["mana"].node().setText(str(card.mana))
		self.texts["mana"].node().setTextColor(transparent if self.isPlayed else color)
		#Refresh the attack
		color = white if card.attack <= cardType.attack else green
		self.texts["attack"].node().setText(str(card.attack))
		self.texts["attack"].node().setTextColor(transparent if self.isPlayed else color)
		self.texts["attack_Played"].node().setText(str(card.attack))
		self.texts["attack_Played"].node().setTextColor(color if self.isPlayed else transparent)
		#Weapon durability
		color = white if card.durability >= cardType.durability else red
		self.texts["durability"].node().setText(str(card.durability))
		self.texts["durability"].node().setTextColor(transparent if self.isPlayed else color)
		self.texts["durability_Played"].node().setText(str(card.durability))
		self.texts["durability_Played"].node().setTextColor(color if self.isPlayed else transparent)
		
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
			elif GUI.UI == 3 and card in game.options: GUI.resolveMove(card, None, "DiscoverOption", info=None)
			
	#Actions: buffDebuff, damage
	def statChangeAni(self, num1=None, num2=None, action="buffDebuff"):
		card = self.card
		if not (card.inHand or card.onBoard): return
		cardType = type(card)
		color_Durability = red if card.durability < cardType.durability else white
		if action == "buffDebuff": #一般的攻击力和耐久度重置计算也可以用set，只是需要把num1和num2设为0
			parallel = Parallel(name="Stat Change Ani")
			color_Attack = white if card.attack <= cardType.attack else green
			np_Text_Attack, np_Text_Attack_Played = self.texts["attack"], self.texts["attack_Played"]
			np_Text_Durability, np_Text_Durability_Played = self.texts["durability"], self.texts["durability_Played"]
			if num1:
				seq_Attack = Sequence(np_Text_Attack.scaleInterval(duration=0.15, scale=2 * 0.9 if self.isPlayed else (2 * statTextScale)),
									  Func(np_Text_Attack.node().setText, str(card.attack)),
									  Func(np_Text_Attack.node().setTextColor, transparent if self.isPlayed else color_Attack),
									  np_Text_Attack.scaleInterval(duration=0.15, scale=0.9 if self.isPlayed else statTextScale)
									  )
				seq_Attack_Played = Sequence(np_Text_Attack_Played.scaleInterval(duration=0.15, scale=2 * 0.9 if self.isPlayed else 2 * statTextScale),
											 Func(np_Text_Attack_Played.node().setText, str(card.attack)),
											 Func(np_Text_Attack_Played.node().setTextColor, color_Attack if self.isPlayed else transparent),
											 np_Text_Attack_Played.scaleInterval(duration=0.15, scale=0.9 if self.isPlayed else statTextScale)
											 )
				parallel.append(Func(seq_Attack.start))
				parallel.append(Func(seq_Attack_Played.start))
			else:
				parallel.append(Func(np_Text_Attack.node().setText, str(card.attack)))
				parallel.append(Func(np_Text_Attack.node().setTextColor, transparent if self.isPlayed else color_Attack))
				parallel.append(Func(np_Text_Attack_Played.node().setText, str(card.attack)))
				parallel.append(Func(np_Text_Attack_Played.node().setTextColor, color_Attack if self.isPlayed else transparent))
			
			if num2:
				seq_Health = Sequence(np_Text_Durability.scaleInterval(duration=0.15, scale=2 * 0.9 if self.isPlayed else 2 * statTextScale),
									  Func(np_Text_Durability.node().setText, str(card.durability)),
									  Func(np_Text_Durability.node().setTextColor, transparent if self.isPlayed else color_Durability),
									  np_Text_Durability.scaleInterval(duration=0.15, scale=0.9 if self.isPlayed else statTextScale)
									  )
				seq_Health_Played = Sequence(np_Text_Durability_Played.scaleInterval(duration=0.15, scale=2 * 0.9 if self.isPlayed else 2 * statTextScale),
											 Func(np_Text_Durability_Played.node().setText, str(card.durability)),
											 Func(np_Text_Durability_Played.node().setTextColor, color_Durability if self.isPlayed else transparent),
											 np_Text_Durability_Played.scaleInterval(duration=0.15, scale=0.9 if self.isPlayed else statTextScale)
											 )
				parallel.append(Func(seq_Health.start))
				parallel.append(Func(seq_Health_Played.start))
			else:
				parallel.append(Func(np_Text_Durability.node().setText, str(card.durability)))
				parallel.append(Func(np_Text_Durability.node().setTextColor, transparent if self.isPlayed else color_Durability))
				parallel.append(Func(np_Text_Durability_Played.node().setText, str(card.durability)))
				parallel.append(Func(np_Text_Durability_Played.node().setTextColor, color_Durability if self.isPlayed else transparent))
			
			self.GUI.seqHolder[-1].append(parallel)
		elif action == "damage":  #不需要动画
			np_Text_Durability_Played = self.texts["durability_Played"]
			para = Parallel(Func(np_Text_Durability_Played.node().setText, str(card.durability)),
							Func(np_Text_Durability_Played.node().setTextColor, color_Durability if self.isPlayed else transparent),
							name="Damage Ani")
			self.GUI.seqHolder[-1].append(para)
		
	#需要用inverval.start
	def statusChangeAni(self, name=''):
		card, para = self.card, Parallel(name="Status Change Ani")
		if not name or name == "Immune":
			para.append(Func(self.texCardAni_LoopPose, "Immune", card.status["Immune"] > 0))
		
		if self.GUI.seqHolder: self.GUI.seqHolder[-1].append(para)
		else: para.start()
			
	#Place the "Trigger", "Deathrattle", "Lifesteal", "Poisonous" icons at the right places
	def placeIcons(self):
		para, icons = Parallel(name="Icon Placing Ani"), []
		if self.isPlayed and any(not trig.oneTime for trig in self.card.trigsBoard):
			para.append(Func(self.icons["Trigger"].updateText))
			icons.append(self.icons["Trigger"])
		else: para.append(Func(self.icons["Trigger"].np.setColor, transparent))
		
		para.append(Func(self.icons["SpecTrig"].np.find("SpecTrig").setColor, white))
		if self.isPlayed and any(trig.oneTime for trig in self.card.trigsBoard):
			icons.append(self.icons["SpecTrig"])
		else: para.append(Func(self.icons["SpecTrig"].np.setColor, transparent))
		
		if self.isPlayed and self.card.deathrattles: icons.append(self.icons["Deathrattle"])
		else: para.append(Func(self.icons["Deathrattle"].np.setColor, transparent))
		
		for keyWord in ("Lifesteal", "Poisonous"):
			if self.isPlayed and self.card.keyWords[keyWord]: icons.append(self.icons[keyWord])
			else: para.append(Func(self.icons[keyWord].np.setColor, transparent))
			
		leftMostPos = -0.6 * (len(icons) - 1) / 2
		for i, model in enumerate(icons):
			para.append(Func(model.np.setColor, white))
			para.append(Func(model.np.setPos, leftMostPos + i * 0.6, -1.8, 0.02))
		
		self.GUI.seqHolder[-1].append(para)
		
	def decideColor(self):
		if self.isPlayed: return transparent
		color, card = transparent, self.card
		cardType, GUI, game = card.type, self.GUI, card.Game
		if card == GUI.subject: color = pink
		elif card == GUI.target: color = blue
		elif card.inHand and card.ID == game.turn:
			if game.Manas.affordable(card, forTrade=False):
				color = yellow if card.effectViable else green
			elif "~Tradeable" in card.index and game.Manas.affordable(card, forTrade=True):
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
	makeText(root, "durability", '0', pos=(1.8, -4, 0.12), scale=statTextScale,
			  color=white, font=font)
	makeText(root, "attack_Played", '0', pos=(-1.28, -0.8, 0.132), scale=0.9,
			  color=white, font=font)
	makeText(root, "durability_Played", '0', pos=(1.27, -0.8, 0.132), scale=0.9,
				  color=white, font=font)
	
	base.modelTemplates["Trigger"].copyTo(root)
	base.modelTemplates["SpecTrig"].copyTo(root)
	base.modelTemplates["Deathrattle"].copyTo(root)
	base.modelTemplates["Lifesteal"].copyTo(root)
	base.modelTemplates["Poisonous"].copyTo(root)
	
	for name, posScale in table_PosScaleofTexCard_Weapons.items():
		texCard = loader.loadModel("TexCards\\ForWeapons\\%s.egg" % name)
		texCard.name = name + "_TexCard"
		texCard.reparentTo(root)
		texCard.setScale(posScale[0])
		texCard.setPosHpr(posScale[1], Point3(0, -90, 0))
		texCard.find("+SequenceNode").node().pose(0)#loop(False, 1, 100)
	
	#After the loading, the NP_Weapon root tree structure is:
	#NP_Weapon/card|stats|cardImage, etc
	#NP_Weapon/mana_TextNode|attack_TextNode, etc
	#NP_Weapon/Trigger_Icon|Deathrattle_Icon, etc
	return root


"""Load Hero Powers"""
class Btn_Power(Btn_Card):
	def __init__(self, GUI, card, nodePath):
		super().__init__(GUI, card, nodePath)
		
		self.cNode_Backup = CollisionNode("Power_cNode")
		self.cNode_Backup.addSolid(CollisionBox(Point3(0, -1.6, 0), 2.3, 3, 0.1))
		self.cNode_Backup_Played = CollisionNode("Power_cNode_Played")
		self.cNode_Backup_Played.addSolid(CollisionBox(Point3(0, 0.3, 0), 1.6, 1.6, 0.1))
		
	def reloadModels(self, loader, imgPath, pickable, reTexture, onlyShowCard=True):
		card = self.card
		self.box_Model = self.models["box"] if self.isPlayed else None
		self.models["box"].setColor(transparent)
		
		for modelName in ("card", "description", "nameTag"):
			self.models[modelName].setColor(transparent if self.isPlayed else white)
		if self.cNode:
			self.cNode.removeNode()
			self.cNode = None
		if pickable:
			self.cNode = self.np.attachNewNode(self.cNode_Backup_Played if self.isPlayed else self.cNode_Backup)
			#self.cNode.show()
		"""The card frame. The front face texture is set according to it class"""
		if reTexture:
			texture = loader.loadTexture(imgPath)
			for modelName in ("card", "cardImage", "nameTag"):
				self.models[modelName].setTexture(self.models[modelName].findTextureStage('*'), texture, 1)
		text = card.text(CHN)
		textNodePath = self.texts["description"]
		textNodePath.node().setText(text)
		textNodePath.setPos(0, -3 + 0.1 * len(text) / 12, 0.2)
		textNodePath.node().setTextColor(black if not self.isPlayed and text else transparent)
		self.models["description"].setColor(white if not self.isPlayed and text else transparent)
		
		cardType = type(self.card)
		#Refresh the mana
		color = white if self.card.mana == cardType.mana else (green if self.card.mana < cardType.mana else red)
		self.texts["mana"].node().setText(str(self.card.mana))
		self.texts["mana"].node().setTextColor(color)
	
	def checkHpr(self):
		card, hprFinal = self.card, None
		if card.ID == self.GUI.Game.turn:
			if card.chancesUsedUp() and self.np.get_r() % 360 == 0:
				hprFinal = Point3(0, 0, 180)  #Flip to back, power unusable
			elif not card.chancesUsedUp() and self.np.get_r() % 360 == 180:
				hprFinal = Point3(0, 0, 0) #Flip to front
		if hprFinal:
			heroZone = self.GUI.heroZones[self.card.ID]
			interval = Sequence(self.genLerpInterval(pos=(heroZone.powerPos[0], heroZone.powerPos[1], heroZone.powerPos[2]+3),
													 hpr=Point3(0, 0, 90), duration=0.2),
								self.genLerpInterval(pos=heroZone.powerPos, hpr=hprFinal, duration=0.2)
								)
			if self.GUI.seqHolder: self.GUI.seqHolder[-1].append(Func(interval.start))
			else: interval.start()
			
	def leftClick(self):
		if self.isPlayed:
			if self.GUI.UI == 0: self.GUI.resolveMove(self.card, self, "Power", info=None)
		else: #Discover a power.
			if self.GUI.UI == 3 and self.card in self.GUI.Game.options:
				self.GUI.resolveMove(self.card, None, "DiscoverOption", info=None)
		
	def decideColor(self):
		color, card = transparent, self.card
		if self.isPlayed and card.ID == card.Game.turn and card.Game.Manas.affordable(card) and card.available():
			color = green
		return color
		
		
def loadPower(base):
	loader = base.loader
	font = base.font
	root = loader.loadModel("Models\\PowerModels\\Power.glb")
	root.name = "NP_Power"
	
	#Model names: box, card, cardImage, description, nameTag, mana
	for model in root.getChildren():
		model.setTransparency(True)
		if model.name in ("border", "mana"): texture = base.textures["stats_Power"]
		else: continue
		model.setTexture(model.findTextureStage('*'), texture, 1)
	#y limit: mana -0.12, description -0.025
	makeText(root, "mana", '0', pos=(0, 1.36, 0.125), scale=0.857*statTextScale, #0.9,
			color=white, font=font)
	makeText(root, "description", '', pos=(0, 0, 0.027), scale=0.3,
			color=black, font=font)
	#After the loading, the NP_Minion root tree structure is:
	#NP_Power/card|mana|cardImage, etc
	#NP_Power/mana_TextNode|description_TextNode
	return root


"""Load Hero Cards"""
table_PosScaleofTexCard_Heroes = {"Breaking": (4.3,   Point3(0, 0.27, 0.062)),
									"Frozen": (8, 	  Point3(-0.1, 0.2, 0.064)),
									"Immune": (5.3,   Point3(0, 0.25), 0.071),
									"Damage": (0.07,  Point3(0, 0.1, 0.14)),
								"Spell Damage": (4.6, Point3(0, 0.15, 0.07)),
									"Stealth": (5.5,  Point3(0, 0.15, 0.064)),
								   }

class Btn_Hero(Btn_Card):
	def __init__(self, GUI, card, nodePath):
		super().__init__(GUI, card, nodePath)
		
		self.cNode_Backup = CollisionNode("Hero_cNode")
		self.cNode_Backup.addSolid(CollisionBox(Point3(0.05, -1.1, 0), 2.2, 3.1, 0.1))
		self.cNode_Backup_Played = CollisionNode("Hero_cNode_Played")
		self.cNode_Backup_Played.addSolid(CollisionBox(Point3(0.05, 0.25, 0), 2, 2.2, 0.1))
		
	def reloadModels(self, loader, imgPath, pickable, reTexture, onlyShowCardBack):
		if self.isPlayed: color4Card, color4Played = transparent, white
		else: color4Card, color4Played = white, transparent
		self.models["box"].setColor(transparent)
		self.models["box_Played"].setColor(transparent)
		self.box_Model = self.models["box_Played" if self.isPlayed else "box"]
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
		if reTexture:
			self.models["cardImage"].setTexture(self.models["cardImage"].findTextureStage('*'),
												loader.loadTexture("Images\\HeroesandPowers\\%s.png"%type(self.card).__name__), 1)
			self.models["card"].setTexture(self.models["card"].findTextureStage('*'),
										   loader.loadTexture(imgPath), 1)
		
		card, cardType = self.card, type(self.card)
		self.models["attack"].setColor(white if self.isPlayed and card.attack > 0 else transparent)
		self.models["health"].setColor(white if self.isPlayed else transparent)
		self.models["armor"].setColor(white if self.isPlayed and card.armor > 0 else transparent)
		
		color = white if card.mana == cardType.mana else (green if card.mana < cardType.mana else red)
		self.texts["mana"].node().setText(str(card.mana))
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
			elif GUI.UI == 3 and card in game.options: GUI.resolveMove(card, None, "DiscoverOption", info=None)
			
	#Actions: buffDebuff, damage, armorChange, heal
	def statChangeAni(self, num1=None, num2=None, action="buffDebuff"):
		card = self.card
		if not (card.inHand or card.onBoard): return
		color_Attack = green if card.attack > 0 and self.isPlayed else transparent
		color_Health = red if card.health < card.health_max else (white if card.health_max <= type(card).health else red)
		color_Armor = white if card.armor > 0 and self.isPlayed else transparent
		np_Text_Attack_Played = self.texts["attack_Played"]
		np_Text_Health_Played = self.texts["health_Played"]
		np_Text_Armor_Played = self.texts["armor_Played"]
		if action == "buffDebuff": #buffDebuff can only change attack
			parallel = Parallel(name="Stat Change Ani")
			if num1:
				seq_Attack_Played = Sequence(Func(self.models["attack"].setColor, white if card.attack > 0 and self.isPlayed else transparent),
											 np_Text_Attack_Played.scaleInterval(duration=0.15, scale=2 * 1.1),
											 Func(np_Text_Attack_Played.node().setText, str(card.attack)),
											 Func(np_Text_Attack_Played.node().setTextColor, color_Attack if self.isPlayed else transparent),
											 np_Text_Attack_Played.scaleInterval(duration=0.15, scale=1.1)
											 )
				parallel.append(Func(seq_Attack_Played.start))
			else: #This is simply refreshing the display without any animation
				parallel.append(Func(np_Text_Attack_Played.node().setText, str(card.attack)))
				parallel.append(Func(np_Text_Attack_Played.node().setTextColor, color_Attack))
				parallel.append(Func(np_Text_Health_Played.node().setText, str(card.health)))
				parallel.append(Func(np_Text_Health_Played.node().setTextColor, color_Health if self.isPlayed else transparent))
				parallel.append(Func(np_Text_Armor_Played.node().setText, str(card.armor)))
				parallel.append(Func(np_Text_Armor_Played.node().setTextColor, color_Armor))
				parallel.append(Func(self.models["attack"].setColor, white if card.attack > 0 and self.isPlayed else transparent))
				parallel.append(Func(self.models["armor"].setColor, white if card.armor > 0 and self.isPlayed else transparent))
			self.GUI.seqHolder[-1].append(parallel)
		elif action == "damage":  #需要显示动画
			color_Health = green if card.health == card.health_max else red
			textNode = TextNode("Damage Text Node")
			textNode.setText(str(num2))
			textNode.setTextColor(red)
			textNode.setAlign(TextNode.ACenter)
			textNodePath = self.np.attachNewNode(textNode)
			textNodePath.setPosHprScale(0, 0, 0, 0, -90, 0, 1.5, 1.5, 1.5)
			#Total # of frames: 47. frame 48 will be the first frame
			sequence = Sequence(Func(np_Text_Health_Played.node().setText, str(card.health)), Func(np_Text_Health_Played.node().setTextColor, color_Health),
								Func(np_Text_Armor_Played.node().setText, str(card.armor)), Func(np_Text_Armor_Played.node().setTextColor, color_Armor),
								Func(self.models["armor"].setColor, white if card.armor > 0 and self.isPlayed else transparent),
								Func(self.texCards["Damage"].find("+SequenceNode").node().play, 1, 48), Func(textNodePath.setPos, 0, -0.1, 0.15),
								Wait(1.5), Func(textNodePath.removeNode))
			self.GUI.seqHolder[-1].append(Func(sequence.start, name="Damage Ani"))
		elif action == "heal":
			textNode = TextNode("Heal Text Node")
			textNode.setText('+'+str(num2))
			textNode.setTextColor(yellow)
			textNode.setAlign(TextNode.ACenter)
			textNodePath = self.np.attachNewNode(textNode)
			textNodePath.setPosHprScale(0, 0, 0, 0, -90, 0, 1.5, 1.5, 1.5)
			sequence = Sequence(Func(np_Text_Health_Played.node().setText, str(card.health)), Func(np_Text_Health_Played.node().setTextColor, color_Health),
								Func(textNodePath.setPos, 0, 0.2, 0.0145), Wait(1.5), Func(textNodePath.removeNode))
			self.GUI.seqHolder[-1].append(Func(sequence.start, name="Heal Ani"))
		elif action == "armorChange":
			parallel = Parallel(Func(self.models["armor"].setColor, color_Armor),
								Func(self.texts["armor_Played"].node().setText, str(card.armor)),
								Func(self.texts["armor_Played"].node().setTextColor, color_Armor),
								name="Armor Change Ani")
			self.GUI.seqHolder[-1].append(parallel)
			
	def statusChangeAni(self, name=''):
		card, para = self.card, Parallel(name="Status Change Ani")
		#Handle the loop(False)/pose(0) type of texCards: Immune, Stealth, Spell Damage
		if not name or name == "Immune":
			para.append(Func(self.texCardAni_LoopPose, "Immune", card.Game.status[card.ID]["Immune"] > 0))
		if not name or name == "Spell Damage":
			para.append(Func(self.texCardAni_LoopPose, "Spell Damage", card.Game.status[card.ID]["Spell Damage"] > 0))
		if not name or name == "Stealth":
			para.append(Func(self.texCardAni_LoopPose, "Stealth", card.status["Temp Stealth"] > 0))
		##Handle the loop(False, num1, num2)/play(num1, num2) type of texCards: Frozen
		if not name or name == "Frozen":
			para.append(Func(self.texCardAni_LoopPlay, "Frozen", 96, 97, 105, card.status["Frozen"] > 0))
			
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
	
	for name, posScale in table_PosScaleofTexCard_Heroes.items():
		texCard = loader.loadModel("TexCards\\ForHeroes\\%s.egg" % name)
		texCard.name = name + "_TexCard"
		texCard.reparentTo(root)
		texCard.setScale(posScale[0])
		texCard.setPosHpr(posScale[1], Point3(0, -90, 0))
		texCard.find("+SequenceNode").node().pose(0)
	
	#After the loading, the NP_Minion root tree structure is:
	#NP_Hero/card|stats|cardImage, etc
	#NP_Hero/mana_TextNode|attack_TextNode, etc
	#NP_Hero/Frozen_TexCard, etc
	return root


class Btn_Trigger:
	def __init__(self, carrierBtn, nodePath):
		self.carrierBtn, self.np = carrierBtn, nodePath
		self.counterText = nodePath.find("Trig Counter")
		self.seqNode = nodePath.find("TexCard").find("+SequenceNode").node()
		
	def trigAni(self): #Index of last frame is 47
		if self.seqNode.isPlaying(): self.seqNode.play(self.seqNode.getFrame(), 48)
		else: self.seqNode.play(1, 48)
		
	def updateText(self):
		s = ""
		for trig in self.carrierBtn.card.trigsBoard:
			if trig.counter > 0: s += str(trig.counter) + ' '
		Sequence(LerpScaleInterval(self.counterText, duration=0.25, scale=1),
				 Func(self.counterText.node().setText, s),
				 LerpScaleInterval(self.counterText, duration=0.25, scale=0.6)).start()
		
class Btn_SpecTrig:
	def __init__(self, carrierBtn, nodePath):
		self.carrierBtn, self.np = carrierBtn, nodePath
		self.seqNode = nodePath.find("TexCard").find("+SequenceNode").node()
	
	def trigAni_1stHalf(self):
		self.seqNode.play(1, 13)
		
	def trigAni_2ndHalf(self):
		self.seqNode.play(14, 24)
		
class Btn_Deathrattle:
	def __init__(self, carrierBtn, nodePath):
		self.carrierBtn, self.np = carrierBtn, nodePath
		self.seqNode = nodePath.find("TexCard").find("+SequenceNode").node()
		
	def trigAni(self, nextAnimWaits=False):
		if self.seqNode.isPlaying():
			self.seqNode.play(self.seqNode.getFrame(), self.seqNode.getNumFrames())
		else:
			self.seqNode.play(1, self.seqNode.getNumFrames())

class Btn_Lifesteal:
	def __init__(self, carrierBtn, nodePath):
		self.carrierBtn, self.np = carrierBtn, nodePath
		self.seqNode = nodePath.find("TexCard").find("+SequenceNode").node()
	
	def trigAni(self, nextAnimWaits=False):
		if self.seqNode.isPlaying():
			self.seqNode.play(self.seqNode.getFrame(), self.seqNode.getNumFrames())
		else:
			self.seqNode.play(1, self.seqNode.getNumFrames())

class Btn_Poisonous:
	def __init__(self, carrierBtn, nodePath):
		self.carrierBtn, self.np = carrierBtn, nodePath
		self.seqNode = nodePath.find("TexCard").find("+SequenceNode").node()
		
	def trigAni(self, nextAnimWaits=False):
		if self.seqNode.isPlaying():
			self.seqNode.play(self.seqNode.getFrame(), self.seqNode.getNumFrames())
		else:
			self.seqNode.play(1, self.seqNode.getNumFrames())


#Used for secrets and quests
class Btn_Secret:
	def __init__(self, GUI, card, nodePath):
		self.GUI, self.card = GUI, card
		self.selected = False
		self.np = nodePath
	
	def reassignCardBtn(self, card):
		card.btn = self
		
	def dimDown(self):
		self.np.setColor(grey)
	
	def setBoxColor(self, color):
		pass
	
	def checkHpr(self, color=False, stat=False, indicator=False, all=True):
		hpr = None
		if self.card.ID == self.GUI.Game.turn and self.np.get_r() % 360 == 0:
			hpr = Point3(0, 0, 180)  #Flip to back, unusable
		elif self.card.ID != self.GUI.Game.turn and self.np.get_r() % 360 == 180:
			hpr = Point3(0, 0, 0)
		if hpr:
			interval = LerpHprInterval(self.np, duration=0.3, hpr=hpr)
			if self.GUI.seqHolder: self.GUI.seqHolder[-1].append(Func(interval.start))
			else: interval.start()
			
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
		self.selected = False
		self.np = nodePath
		self.counterText = nodePath.find("Trig Counter")
		
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
		
	def finishAni(self, newQuest):
		card, pos_0 = self.card, self.np.getPos()
		nodePath, btn = genCard(self.GUI, card, isPlayed=False, pickable=False, scale=0.1)
		sequence = Sequence(Func(self.np.removeNode), Func(nodePath.setPos, pos_0),
							btn.genLerpInterval(pos=pos_QuestFinish, scale=1, duration=0.5), Wait(0.5)
							)
		if newQuest:
			sequence.append(LerpHprInterval(nodePath, duration=0.3, hpr=(0, 0, 180)) )
			sequence.append(Func(btn.changeCard, newQuest, False, False))
			sequence.append(LerpHprInterval(nodePath, duration=0.3, hpr=(0, 0, 360)) )
			sequence.append(Wait(0.7))
			sequence.append(LerpPosHprScaleInterval(btn.np, duration=0.5, pos=pos_0, hpr=(0, 0, 360), scale=0.1))
			sequence.append(Func(nodePath.removeNode))
			nodePath_New, btn_New = genHeroZoneTrigIcon(self.GUI, newQuest, isQuest=True)
			sequence.append(Func(nodePath_New.setPos, pos_0))
		else:
			sequence.append(Func(nodePath.removeNode))
		sequence.append(Func(self.GUI.heroZones[card.ID].placeSecrets))
		
		if self.GUI.seqHolder: self.GUI.seqHolder[-1].append(sequence)
		else: sequence.start()
		
	def leftClick(self):
		pass
	
	def rightClick(self):
		if self.GUI.UI: self.GUI.cancelSelection() #Only responds when UI is 0
		else: self.GUI.drawCardZoomIn(self)

	def setBoxColor(self, color):
		pass
	
	
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
	nodePath = root.find("stats")
	nodePath.setTransparency(True)
	nodePath.setTexture(nodePath.findTextureStage('0'), texture, 1)
	nodePath = root.find("legendaryIcon")
	nodePath.setTransparency(True)
	nodePath.setTexture(nodePath.findTextureStage('0'), base.textures["stats_Spell"], 1)
	
	makeText(root, "mana", '0', pos=(-1.75, 1.15, 0.09), scale=statTextScale,
			 color=white, font=font)
	makeText(root, "attack", '0', pos=(-1.7, -4.05, 0.09), scale=statTextScale,
			 color=white, font=font)
	makeText(root, "health", '0', pos=(1.8, -4.05, 0.09), scale=statTextScale,
			 color=white, font=font)
	
	cNode_Backup = CollisionNode("Option_cNode")
	cNode_Backup.addSolid(CollisionBox(Point3(0.05, -1.1, 0), 2.2, 3.1, 0.1))
	root.attachNewNode(cNode_Backup)
	
	return root


def genOption(GUI, option, pos=None):
	nodePath = GUI.modelTemplates["Option"].copyTo(GUI.render)
	if pos: nodePath.setPos(pos)
	btn_Card = Btn_Option(GUI, option, nodePath)
	nodePath.setPythonTag("btn", btn_Card)
	
	nodePath.find("mana_TextNode").node().setText(str(type(option).mana))
	attack, health = type(option).attack, type(option).health
	nodePath.find("attack_TextNode").node().setText('' if attack < 0 else str(attack))
	nodePath.find("health_TextNode").node().setText('' if health < 0 else str(health))
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
				  "SpecTrig_Icon": Btn_SpecTrig, }


#np_Template is of type NP_Minion, etc and is kept by the GUI.
#card: card object, which the copied nodePath needs to become
#isPlayed: boolean, whether the card is in played form or not
#Only "Trigger", etc reference btn, others reference nodePath
def genCard(GUI, card, isPlayed, pickable=True, pos=None, hpr=None, scale=None, onlyShowCardBack=False):
	type = card.type if card.type != "Dormant" else "Minion"
	nodepath = GUI.modelTemplates[type].copyTo(GUI.render)
	if pos: nodepath.setPos(pos)
	if hpr: nodepath.setHpr(hpr)
	if scale: nodepath.setScale(scale)
	#NP_Minion root tree structure is:
	#NP_Minion/card|stats|cardImage, etc
	#NP_Minion/mana_TextNode|attack_TextNode, etc
	btn_Card = Table_Type2Btn[type](GUI, None, nodepath)
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


def genHeroZoneTrigIcon(GUI, card, pos=None, text='', isQuest=False):
	nodepath = GUI.loader.loadModel("Models\\HeroModels\\TurnTrig.glb")
	icon = nodepath.find("Icon")
	icon.setTexture(icon.findTextureStage('0'),
					GUI.loader.loadTexture(findFilepath(card)), 1)
	nodepath.reparentTo(GUI.render)
	textNode = TextNode("Trig Counter")
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
	if isQuest: nodepath.setScale(1.3)
	return nodepath, btn_Icon