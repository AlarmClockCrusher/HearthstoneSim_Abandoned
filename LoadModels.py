from panda3d.core import *
import inspect

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
					"GVG": "AcrossPacks", "Kobolds": "AcrossPacks", "Boomsday": "AcrossPacks",
					"Shadows": "Shadows", "Uldum": "Uldum", "Dragons": "Dragons", "Galakrond": "Galakrond",
					"DHInitiate": "DHInitiate", "Outlands": "Outlands", "Academy": "Academy", "Darkmoon": "Darkmoon",
				   "SV_Basic":"SV_Basic","SV_Ultimate":"SV_Ultimate","SV_Uprooted":"SV_Uprooted","SV_Fortune":"SV_Fortune",
				   "SV_Rivayle":"SV_Rivayle","SV_Eternal":"SV_Eternal"
					}

def findFilepath(card):
	if card.type == "Dormant":
		index = card.prisoner.index
		folderName = folderNameTable[index.split('~')[0]]
		if inspect.isclass(card.prisoner):
			name = card.prisoner.__name__
		else:  #Instances don't have __name__
			name = type(card.prisoner).__name__
		path = "Images\\%s\\" % folderName
	else:  #type == "Weapon", "Minion", "Spell", "Hero", "Power"
		index, name = card.index, type(card).__name__
		if card.type != "Hero" and card.type != "Power":
			folderName = folderNameTable[index.split('~')[0]]
			path = "Images\\%s\\" % folderName
		else:
			path = "Images\\HerosandPowers\\"
	
	if "Mutable" in name: name = name.split("_")[0]
	filepath = path + "%s.png" % name
	return filepath


"""Subclass the NodePath, since it can be assigned attributes directly"""
class NodePath_Card(NodePath):
	def __init__(self, GUI, card=None, cardType=None, collBox4="Hand"):
		if cardType: super().__init__(cardType.__name__+"_NodePath_Card")
		else: super().__init__(card.name+"_NodePath_Card")
		#These attributes will be modified by load functions below
		self.cardType = cardType
		self.card = card
		self.GUI = GUI
		self.manaText = self.attackText = self.healthText = self.durabilityText = self.armorText = None
		self.descriptionText = None
		if collBox4:
			box_dx, box_dy, box_dz = {"Hand": (3.5, 0.3, 5),
									  "Minion": (2.4, 0.3, 3), "Dormant": (2, 0.3, 3),
									  "Weapon": (2.7, 0.3, 2.7), "Hero": (2, 0.3, 2.4),
									  "Power": (2, 0.4, 2)}[collBox4]
			collNode_Card = CollisionNode("%s_c_node"%(card.name if card else cardType.name))
			collNode_Card.addSolid(CollisionBox(Point3(0, 0, 0), box_dx, box_dy, box_dz))
			node = self.attachNewNode(collNode_Card)
			#node.show()
	
	def leftClick(self):
		print("Clicked:", self.card if self.card else self.cardType)
	
	def rightClick(self):
		print("Clicked:", self.card if self.card else self.cardType)


def loadCard(base, card=None, cardType=None, pickable=True):
	if card:
		if card.type == "Minion":
			return loadMinion(base, card=card, cardType=cardType, pickable=pickable)
		elif card.type == "Spell":
			return loadSpell(base, card=card, cardType=cardType, pickable=pickable)
		elif card.type == "Weapon":
			return loadWeapon(base, card=card, cardType=cardType, pickable=pickable)
		elif card.type == "Hero":
			return loadHero(base, card=card, cardType=cardType, pickable=pickable)
		elif card.type == "Power":
			return loadPower(base, card=card, cardType=cardType, pickable=pickable)
	else:
		if "attack" in cardType.__dict__:
			if "health" in cardType.__dict__:
				return loadMinion(base, card=card, cardType=cardType, pickable=pickable)
			else:
				return loadWeapon(base, card=card, cardType=cardType, pickable=pickable)
		elif "armor" in cardType.__dict__:
			return loadHero(base, card=card, cardType=cardType, pickable=pickable)
		else: #For now, it can't distinguish the spell and hero power
			return loadSpell(base, card=card, cardType=cardType, pickable=pickable)
			
			
#Either a card or cardType must be defined
def loadMinion(base, card=None, cardType=None, pickable=True):
	loader = base.loader
	if card: imgPath = findFilepath(card)
	else: imgPath = "Images\\%s\\" % cardType.index.split('~')[0] + cardType.__name__ + ".png"
	sansBold = loader.loadFont('Models\\OpenSans-Bold.ttf')
	
	root = NodePath_Card(base, card=card, cardType=cardType, collBox4="Hand" if pickable else '')
	root.reparentTo(base.render)
	
	isLegendary = ("~Legendary" in card.index) if card else ("~Legendary" in cardType.index)
	"""The card frame. The front face texture is set according to it class"""
	filePath = "Models\\MinionModels\\" + ("Card_Legendary.glb" if isLegendary else "Card.glb")
	card_Model = loader.loadModel(filePath)
	card_Model.reparentTo(root)
	card_Model.setTexture(card_Model.findTextureStage('*'),
					loader.loadTexture(imgPath), 1)
	
	"""Card image based on the card type"""
	filePath = "Models\\MinionModels\\" + ("MinionImage_Legendary.glb" if isLegendary else "MinionImage.glb")
	cardImage = loader.loadModel(filePath)
	cardImage.reparentTo(root)
	cardImage.setTexture(cardImage.findTextureStage('*'),
						 loader.loadTexture(imgPath), 1)
	
	"""Name Tag of the card, includes the model, and the nameText"""
	nameTag = loader.loadModel("Models\\MinionModels\\NameTag.glb")
	nameTag.reparentTo(root)
	nameTag.setTexture(nameTag.findTextureStage('*'),
					loader.loadTexture(imgPath), 1)
	
	"""Values to display on the card"""
	manaValue = '%d' % (card.mana if card else cardType.mana)
	attackValue = '%d' % (card.attack if card else cardType.attack)
	healthValue = '%d' % (card.health if card else cardType.health)
	
	"""Mana display of the card"""
	mana_Model = loader.loadModel("Models\\MinionModels\\Mana.glb")
	mana_Model.reparentTo(root)
	root.manaText = TextNode("Mana Text Node")
	root.manaText.setFont(sansBold)
	root.manaText.setText(manaValue)
	root.manaText.setAlign(TextNode.ACenter)
	manaTextNode = mana_Model.attachNewNode(root.manaText)
	manaTextNode.setScale(1.4)
	
	"""Attack of the card, includes the model and the attackText"""
	attack_Model = loader.loadModel("Models\\MinionModels\\Attack.glb")
	attack_Model.reparentTo(root)
	root.attackText = TextNode("Attack Text Node")
	root.attackText.setText(attackValue)
	root.attackText.setFont(sansBold)
	root.attackText.setAlign(TextNode.ACenter)
	attackTextNode = attack_Model.attachNewNode(root.attackText)
	attackTextNode.setScale(1.3)
	attackTextNode.setPos(-2.75, -0.3, -4.7)
	
	"""Health of the card, includes the model and the attackText"""
	health_Model = loader.loadModel("Models\\MinionModels\\Health.glb")
	health_Model.reparentTo(root)
	root.healthText = TextNode("Health Text Node")
	root.healthText.setText(healthValue)
	root.healthText.setFont(sansBold)
	root.healthText.setAlign(TextNode.ACenter)
	healthTextNode = health_Model.attachNewNode(root.healthText)
	healthTextNode.setScale(1.3)
	healthTextNode.setPos(3, -0.3, -4.7)
	
	if isLegendary:
		legendaryIcon = loader.loadModel("Models\\MinionModels\\LegendaryIcon.glb")
		legendaryIcon.reparentTo(root)
		
	race = card.race if card else cardType.race
	if race:
		race_Model = loader.loadModel("Models\\MinionModels\\Race.glb")
		race_Model.reparentTo(root)
		raceText = TextNode("Race Text Node")
		raceText.setText(race)
		raceText.setFont(sansBold)
		raceText.setAlign(TextNode.ACenter)
		raceTextNode = race_Model.attachNewNode(raceText)
		raceTextNode.setScale(0.4)
		raceTextNode.setPos(0.2, -0.3, -4.55)
	
	return root


def loadMinion_Played(base, card):
	loader = base.loader
	imgPath = findFilepath(card)
	sansBold = loader.loadFont('Models\\OpenSans-Bold.ttf')
	
	root = NodePath_Card(base, card=card, cardType=None, collBox4="Minion")
	root.reparentTo(base.render)
	
	"""Card image based on the card type"""
	cardImage = loader.loadModel("Models\\MinionModels\\MinionImage_Played.glb")
	cardImage.reparentTo(root)
	cardImage.setTexture(cardImage.findTextureStage('*'),
						 loader.loadTexture(imgPath), 1)
	
	"""Name Tag of the card, includes the model, and the nameText"""
	nameTag = loader.loadModel("Models\\MinionModels\\NameTag_Played.glb")
	nameTag.reparentTo(root)
	nameTag.setTexture(nameTag.findTextureStage('*'),
					loader.loadTexture(imgPath), 1)
	
	"""Values to display on the minion pawn"""
	attackValue = '%d' % card.attack
	healthValue = '%d' % card.health
	
	"""Attack of the card, includes the model and the attackText"""
	attack_Model = loader.loadModel("Models\\MinionModels\\Attack_Played.glb")
	attack_Model.reparentTo(root)
	root.attackText = TextNode("attack")
	root.attackText.setText(attackValue)
	root.attackText.setFont(sansBold)
	root.attackText.setAlign(TextNode.ACenter)
	attackTextNode = attack_Model.attachNewNode(root.attackText)
	attackTextNode.setScale(1)
	attackTextNode.setPos(-2.05, -0.1, -1.95)
	
	"""Health of the card, includes the model and the attackText"""
	health_Model = loader.loadModel("Models\\MinionModels\\Health_Played.glb")
	health_Model.reparentTo(root)
	root.healthText = TextNode("health")
	root.healthText.setText(healthValue)
	root.healthText.setFont(sansBold)
	root.healthText.setAlign(TextNode.ACenter)
	healthTextNode = health_Model.attachNewNode(root.healthText)
	healthTextNode.setScale(1)
	healthTextNode.setPos(1.95, -0.1, -1.9)
	
	"""Playeds only need to the Legendary Icon surrounding the image"""
	if "~Legendary" in card.index:
		legendaryIcon = loader.loadModel("Models\\MinionModels\\LegendaryIcon_Played.glb")
		legendaryIcon.reparentTo(root)
		
	return root



"""Load Spell Cards"""
def loadSpell(base, card=None, cardType=None, pickable=True):
	loader = base.loader
	if card: imgPath = findFilepath(card)
	else: imgPath = "Images\\%s\\" % cardType.index.split('~')[0] + cardType.__name__ + ".png"
	sansBold = loader.loadFont('Models\\OpenSans-Bold.ttf')
	
	root = NodePath_Card(base, card=card, cardType=cardType, collBox4="Hand" if pickable else '')
	root.reparentTo(base.render)
	
	isLegendary = ("~Legendary" in card.index) if card else ("~Legendary" in cardType.index)
	"""The card frame. The front face texture is set according to it class"""
	filePath = "Models\\SpellModels\\" + ("Card_Legendary.glb" if isLegendary else "Card.glb")
	card_Model = loader.loadModel(filePath)
	card_Model.reparentTo(root)
	card_Model.setTexture(card_Model.findTextureStage('*'),
					loader.loadTexture(imgPath), 1)
	
	"""Mana display of the card"""
	manaValue = "%d"%(card.mana if card else cardType.mana)
	mana_Model = loader.loadModel("Models\\SpellModels\\Mana.glb")
	mana_Model.reparentTo(root)
	root.manaText = TextNode("mana")
	root.manaText.setFont(sansBold)
	root.manaText.setText(manaValue)
	root.manaText.setAlign(TextNode.ACenter)
	manaTextNode = mana_Model.attachNewNode(root.manaText)
	manaTextNode.setScale(1.4)
	manaTextNode.setPos(-2.9, -0.1, 4)
	
	if isLegendary:
		legendaryIcon = loader.loadModel("Models\\SpellModels\\LegendaryIcon.glb")
		legendaryIcon.reparentTo(root)
	
	school = card.school if card else cardType.school
	if school:
		school_Model = loader.loadModel("Models\\SpellModels\\School.glb")
		school_Model.reparentTo(root)
		nameText = TextNode("School")
		nameText.setText(school)
		nameText.setFont(sansBold)
		nameText.setAlign(TextNode.ACenter)
		nameTextNode = school_Model.attachNewNode(nameText)
		nameTextNode.setScale(0.4)
		nameTextNode.setPos(0, -0.1, -4.45)
	
	return root



"""Load Weapon Cards"""
def loadWeapon(base, card=None, cardType=None, pickable=True):
	loader = base.loader
	if card: imgPath = findFilepath(card)
	else: imgPath = "Images\\%s\\" % cardType.index.split('~')[0] + cardType.__name__ + ".png"
	sansBold = loader.loadFont('Models\\OpenSans-Bold.ttf')
	
	root = NodePath_Card(base, card=card, cardType=cardType, collBox4="Hand" if pickable else '')
	root.reparentTo(base.render)
	
	isLegendary = ("~Legendary" in card.index) if card else ("~Legendary" in cardType.index)
	"""The card frame. The front face texture is set according to it class"""
	filePath = "Models\\WeaponModels\\" + ("Card_Legendary.glb" if isLegendary else "Card.glb")
	card_Model = loader.loadModel(filePath)
	card_Model.reparentTo(root)
	#print(card.findAllTextures())
	#print(card.findAllMatches("**/+GeomNode"))
	card_Model.setTexture(card_Model.findTextureStage('*'),
					loader.loadTexture(imgPath), 1)
	
	cardBack = loader.loadModel("Models\\WeaponModels\\CardBack.glb")
	cardBack.reparentTo(root)
	
	"""Weapon head image to display"""
	cardImg = loader.loadModel("Models\\WeaponModels\\Head.glb")
	cardImg.reparentTo(root)
	cardImg.setTexture(cardImg.findTextureStage('*'),
					   loader.loadTexture(imgPath), 1)
	
	"""Values to display on the card"""
	manaValue = '%d' % (card.mana if card else cardType.mana)
	attackValue = '%d' % (card.attack if card else cardType.attack)
	durabilityValue = '%d' % (card.durability if card else cardType.durability)
	
	"""Mana display of the card"""
	mana_Model = loader.loadModel("Models\\WeaponModels\\Mana.glb")
	mana_Model.reparentTo(root)
	root.manaText = TextNode("mana")
	root.manaText.setFont(sansBold)
	root.manaText.setText(manaValue)
	root.manaText.setAlign(TextNode.ACenter)
	manaTextNode = mana_Model.attachNewNode(root.manaText)
	manaTextNode.setScale(1.4)
	manaTextNode.setPos(-2.85, -0.15, 3.85)
	
	"""Attack of the card, includes the model and the attackText"""
	attack_Model = loader.loadModel("Models\\WeaponModels\\Attack.glb")
	attack_Model.reparentTo(root)
	root.attackText = TextNode("attack")
	root.attackText.setText(attackValue)
	root.attackText.setFont(sansBold)
	root.attackText.setAlign(TextNode.ACenter)
	attackTextNode = attack_Model.attachNewNode(root.attackText)
	attackTextNode.setScale(1.3)
	attackTextNode.setPos(-2.85, -0.15, -4.7)
	
	"""Durability of the card, includes the model and the attackText"""
	durability_Model = loader.loadModel("Models\\WeaponModels\\Durability.glb")
	durability_Model.reparentTo(root)
	root.durabilityText = TextNode("Cadurability")
	root.durabilityText.setText(durabilityValue)
	root.durabilityText.setFont(sansBold)
	root.durabilityText.setAlign(TextNode.ACenter)
	durabilityTextNode = durability_Model.attachNewNode(root.durabilityText)
	durabilityTextNode.setScale(1.3)
	durabilityTextNode.setPos(2.9, -0.15, -4.7)
	
	if isLegendary:
		legendaryIcon = loader.loadModel("Models\\WeaponModels\\LegendaryIcon.glb")
		legendaryIcon.reparentTo(root)
	
	return root


def loadWeapon_Played(base, card):
	loader = base.loader
	imgPath = findFilepath(card)
	sansBold = loader.loadFont('Models\\OpenSans-Bold.ttf')
	
	root = NodePath_Card(base, card=card, cardType=None, collBox4="Weapon")
	root.reparentTo(base.render)
	
	"""Card border for weapon"""
	border = loader.loadModel("Models\\WeaponModels\\Border_Played.glb")
	border.reparentTo(root)
	
	"""Card image based on the card type"""
	cardImage = loader.loadModel("Models\\WeaponModels\\WeaponImage_Played.glb")
	cardImage.reparentTo(root)
	cardImage.setTexture(cardImage.findTextureStage('*'),
						 loader.loadTexture(imgPath), 1)
	
	"""Name Tag of the card, includes the model, and the nameText"""
	nameTag = loader.loadModel("Models\\WeaponModels\\NameTag_Played.glb")
	nameTag.reparentTo(root)
	nameTag.setTexture(nameTag.findTextureStage('*'),
					   loader.loadTexture(imgPath), 1)
	
	"""Values to display on the card"""
	attackValue = '%d' % card.attack
	durabilityValue = '%d' % card.durability

	"""Attack of the card, includes the model and the attackText"""
	attack_Model = loader.loadModel("Models\\WeaponModels\\Attack_Played.glb")
	attack_Model.reparentTo(root)
	root.attackText = TextNode("attack")
	root.attackText.setText(attackValue)
	root.attackText.setFont(sansBold)
	root.attackText.setAlign(TextNode.ACenter)
	attackTextNode = attack_Model.attachNewNode(root.attackText)
	attackTextNode.setScale(1)
	attackTextNode.setPos(-2.25, -0.17, -1.7)
	
	"""Durability of the card, includes the model and the attackText"""
	durability_Model = loader.loadModel("Models\\WeaponModels\\Durability_Played.glb")
	durability_Model.reparentTo(root)
	root.durabilityText = TextNode("durability")
	root.durabilityText.setText(durabilityValue)
	root.durabilityText.setFont(sansBold)
	root.durabilityText.setAlign(TextNode.ACenter)
	durabilityTextNode = durability_Model.attachNewNode(root.durabilityText)
	durabilityTextNode.setScale(1)
	durabilityTextNode.setPos(2.25, -0.17, -1.7)
	"""Playeds only need to the Legendary Icon surrounding the image"""
	if "~Legendary" in card.index:
		legendaryIcon = loader.loadModel("Models\\WeaponModels\\LegendaryIcon_Played.glb")
		legendaryIcon.reparentTo(root)
	
	return root



"""Load Hero Powers"""
def loadPower(base, card=None, cardType=None, pickable=True):
	loader = base.loader
	sansBold = loader.loadFont('Models\\OpenSans-Bold.ttf')
	
	root = NodePath_Card(base, card=card, cardType=cardType, collBox4="Power" if pickable else '')
	root.reparentTo(base.render)
	
	"""The power frame"""
	power = loader.loadModel("Models\\PowerModels\\Power.glb")
	power.reparentTo(root)
	
	"""Mana display of the power"""
	manaValue = '%d' % (power.mana if power else cardType.mana)
	mana_Model = loader.loadModel("Models\\PowerModels\\Mana.glb")
	mana_Model.reparentTo(root)
	root.manaText = TextNode("mana")
	root.manaText.setFont(sansBold)
	root.manaText.setText(manaValue)
	root.manaText.setAlign(TextNode.ACenter)
	manaTextNode = mana_Model.attachNewNode(root.manaText)
	manaTextNode.setScale(1.4)
	manaTextNode.setPos(0, -0.25, 4)
	
	return root


def loadPower_Played(base, card):
	loader = base.loader
	imgPath = findFilepath(card)
	sansBold = loader.loadFont('Models\\OpenSans-Bold.ttf')
	
	root = NodePath_Card(base, card=card, cardType=None, collBox4="Power")
	root.reparentTo(base.render)
	
	"""Power border for weapon"""
	border = loader.loadModel("Models\\PowerModels\\Border_Played.glb")
	border.reparentTo(root)
	
	"""Mana display of the power"""
	mana_Model = loader.loadModel("Models\\PowerModels\\Mana_Played.glb")
	mana_Model.reparentTo(root)
	root.manaText = TextNode("mana")
	root.manaText.setFont(sansBold)
	root.manaText.setText('%d' % card.mana)
	root.manaText.setAlign(TextNode.ACenter)
	manaTextNode = mana_Model.attachNewNode(root.manaText)
	manaTextNode.setScale(1.4)
	manaTextNode.setPos(-0.1, -0.35, 1.75)
	
	"""Power image based on the power type"""
	powerImage = loader.loadModel("Models\\PowerModels\\PowerImage_Played.glb")
	powerImage.reparentTo(root)
	powerImage.setTexture(powerImage.findTextureStage('*'),
						  loader.loadTexture(imgPath), 1)
	
	return root



"""Load Hero Cards"""
def loadHero(base, card=None, cardType=None, pickable=True):
	loader = base.loader
	if card: imgPath = findFilepath(card)
	else: imgPath = "Images\\%s\\" % cardType.index.split('~')[0] + cardType.__name__ + ".png"
	sansBold = loader.loadFont('Models\\OpenSans-Bold.ttf')
	
	root = NodePath_Card(base, card=card, cardType=cardType, collBox4="Hand" if pickable else '')
	root.reparentTo(base.render)
	
	
	"""The card frame. The front face texture is set according to it class"""
	card_Model = loader.loadModel("Models\\HeroModels\\Card.glb")
	card_Model.reparentTo(root)
	card_Model.setTexture(card_Model.findTextureStage('*'),
					loader.loadTexture(imgPath), 1)
	
	"""Mana display of the card"""
	manaValue = '%d' % (card.mana if card else cardType.mana)
	mana_Model = loader.loadModel("Models\\HeroModels\\Mana.glb")
	mana_Model.reparentTo(root)
	root.manaText = TextNode("mana")
	root.manaText.setFont(sansBold)
	root.manaText.setText(manaValue)
	root.manaText.setAlign(TextNode.ACenter)
	manaTextNode = mana_Model.attachNewNode(root.manaText)
	manaTextNode.setScale(1.5)
	manaTextNode.setPos(-2.8, -0.15, 3.0)
	
	"""Armor display of the card"""
	armorValue = '%d' % (card.armor if card else cardType.armor)
	armor_Model = loader.loadModel("Models\\HeroModels\\Armor.glb")
	armor_Model.reparentTo(root)
	root.armorText = TextNode("armor")
	root.armorText.setFont(sansBold)
	root.armorText.setText(armorValue)
	root.armorText.setAlign(TextNode.ACenter)
	armorTextNode = armor_Model.attachNewNode(root.armorText)
	armorTextNode.setScale(1.4)
	armorTextNode.setPos(2.5, -0.2, -4.75)
	
	if "~Legendary" in (card.index if card else cardType.index):
		legendaryIcon = loader.loadModel("Models\\HeroModels\\LegendaryIcon.glb")
		legendaryIcon.reparentTo(root)
		
	return root


def loadHero_Played(base, card):
	loader = base.loader
	imgPath = findFilepath(card)
	sansBold = loader.loadFont('Models\\OpenSans-Bold.ttf')
	
	root = NodePath_Card(base, card=card, cardType=None, collBox4="Hero")
	root.reparentTo(base.render)
	
	"""Card image based on the card type"""
	cardImage = loader.loadModel("Models\\HeroModels\\HeroHead.glb")
	cardImage.reparentTo(root)
	cardImage.setTexture(cardImage.findTextureStage('*'),
						 loader.loadTexture(imgPath), 1)
	
	"""Values to display on the card"""
	attackValue = '%d' % card.attack
	durabilityValue = '%d' % card.health
	
	"""Attack of the card, includes the model and the attackText"""
	attack_Node = loader.loadModel("Models\\HeroModels\\Attack.glb")
	attack_Node.reparentTo(root)
	root.attackText = TextNode("attack")
	root.attackText.setText(attackValue)
	root.attackText.setFont(sansBold)
	root.attackText.setAlign(TextNode.ACenter)
	attackTextNode = attack_Node.attachNewNode(root.attackText)
	attackTextNode.setScale(0.6)
	attackTextNode.setPos(-1.98, -0.25, -1.92)
	
	"""Health of the hero"""
	health_Node = loader.loadModel("Models\\HeroModels\\Health.glb")
	health_Node.reparentTo(root)
	root.healthText = TextNode("health")
	root.healthText.setText(durabilityValue)
	root.healthText.setFont(sansBold)
	root.healthText.setAlign(TextNode.ACenter)
	healthTextNode = health_Node.attachNewNode(root.healthText)
	healthTextNode.setScale(0.6)
	healthTextNode.setPos(2.05, -0.22, -1.92)
	
	"""Armor of the hero"""
	if card.armor > 0:
		armor_Node = loader.loadModel("Models\\HeroModels\\Armor_Played.glb")
		armor_Node.reparentTo(root)
		root.armorText = TextNode("health")
		root.armorText.setText('%d' % card.armor)
		root.armorText.setFont(sansBold)
		root.armorText.setAlign(TextNode.ACenter)
		armorTextNode = armor_Node.attachNewNode(root.armorText)
		armorTextNode.setScale(0.6)
		armorTextNode.setPos(2.05, -0.25, -1.05)
	
	return root
	