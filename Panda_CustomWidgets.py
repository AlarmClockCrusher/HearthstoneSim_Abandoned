from panda3d.core import *

import inspect

from LoadModels import *

Separation_Hands = 5

class HandZone:
	def __init__(self, GUI, ID):
		self.GUI, self.ID, self.btnsDrawn = GUI, ID, []
		ownID = 1 if not hasattr(self.GUI, "ID") else self.GUI.ID  #1PGUI has virtual ID of 1
		self.x, self.y, self.z = 0, 60, -13 if self.ID == ownID else 13
		print(ownID, self.ID, self.z)
		
	def draw(self, cardMoving2=-2, steps=10):
		game, ownHand = self.GUI.Game, self.GUI.Game.Hand_Deck.hands[self.ID]
		print("Card in hand", ownHand)
		leftPos = self.x - Separation_Hands * (len(ownHand) -1) / 2
		posHands = [(leftPos+Separation_Hands*i, self.y-0.3*i, self.z) for i in range(len(ownHand))]
		#Watch for the inclusion of the btnsDrawn and the GUI.pickablesDrawn
		if self.btnsDrawn:
			pass
		else: #When there isn't any hand card drawn yet
			for pos, card in zip(posHands, ownHand):
				print("Drawing card", card)
				nodePath_Card = loadCard(self.GUI, card=card)
				nodePath_Card.setPos(pos)
				nodePath_Card.setScale(0.6)
				self.btnsDrawn.append(nodePath_Card)
				self.GUI.pickablesDrawn.append(nodePath_Card)
				
	##This function is EXCLUSIVE for single-player GUI replay
	#def redraw(self):
	#	#Clear all the buttons drawn.
	#	for btn in reversed(self.btnsDrawn): btn.remove()
	#	#Redraw all the hands
	#	game, ownHand = self.GUI.Game, self.GUI.Game.Hand_Deck.hands[self.ID]
	#	y = int(Y - 0.07 * Y) if self.ID == 1 else int(0.11 * Y)
	#	leftPos = (0.5 - (0.5 - 0.043) * (len(ownHand) - 1) / 14) * X
	#	posHands = [(int(leftPos + (X / 14) * i), y) for i in range(len(ownHand))]
	#	for pos, card in zip(posHands, ownHand):
	#		NodePath_Hand(self.GUI, card).plot(x=pos[0], y=pos[1])


Separation_Minions = 5.4

class BoardZone:
	def __init__(self, GUI, ID):
		self.GUI, self.ID, self.btnsDrawn = GUI, ID, []
		ownID = 1 if not hasattr(self.GUI, "ID") else self.GUI.ID  #1PGUI has virtual ID of 1
		self.x, self.y, self.z = 0, 60, -3 if self.ID == ownID else 3
		
	def draw(self, cardMoving2=-2, steps=10):
		game, ownMinions = self.GUI.Game, self.GUI.Game.minions[self.ID]
		leftPos = self.x - Separation_Minions * (len(ownMinions) - 1) / 2
		posMinions = [(leftPos + Separation_Minions * i, self.y+0.5, self.z) for i in range(len(ownMinions))]
		#Watch for the inclusion of the btnsDrawn and the GUI.pickablesDrawn
		if self.btnsDrawn:
			pass
		else:  #When there isn't any hand card drawn yet
			for pos, card in zip(posMinions, ownMinions):
				nodePath_Card = loadMinion_Played(self.GUI, card=card)
				nodePath_Card.setPos(pos)
				nodePath_Card.setScale(0.75)
				self.btnsDrawn.append(nodePath_Card)
				self.GUI.pickablesDrawn.append(nodePath_Card)


class HeroZone:
	def __init__(self, GUI, ID):
		self.GUI, self.ID, self.btnsDrawn = GUI, ID, []
		ownID = 1 if not hasattr(self.GUI, "ID") else self.GUI.ID  #1PGUI has virtual ID of 1
		self.x, self.y, self.z = 0, 60, -8.5 if self.ID == ownID else 8.5
		
	def draw(self):
		game = self.GUI.Game
		hero, power, weapon = game.heroes[self.ID], game.powers[self.ID], game.availableWeapon(self.ID)
		print(game.weapons)
		if self.btnsDrawn:
			pass
		else:
			#Draw the hero
			nodePath_Card = loadHero_Played(self.GUI, card=hero)
			nodePath_Card.setPos(self.x, self.y, self.z)
			#nodePath_Card.setScale(0.9)
			self.btnsDrawn.append(nodePath_Card)
			self.GUI.pickablesDrawn.append(nodePath_Card)
			#Draw the hero power
			nodePath_Card = loadPower_Played(self.GUI, card=power)
			nodePath_Card.setPos(self.x+4.5, self.y, self.z)
			nodePath_Card.setScale(0.7)
			self.btnsDrawn.append(nodePath_Card)
			self.GUI.pickablesDrawn.append(nodePath_Card)
			if weapon:
				print("Found weapon", weapon)
				nodePath_Card = loadWeapon_Played(self.GUI, card=weapon)
				nodePath_Card.setPos(self.x-5, self.y, self.z)
				nodePath_Card.setScale(0.6)
				self.btnsDrawn.append(nodePath_Card)
				self.GUI.pickablesDrawn.append(nodePath_Card)

#This function is EXCLUSIVE for single-player GUI replay
	#def redraw(self):
	#	#Clear all the buttons drawn.
	#	for btn in reversed(self.btnsDrawn): btn.remove()
	#	#Redraw the hero, power and weapon
	#	game = self.GUI.Game
	#	hero, power, weapon = game.heroes[self.ID], game.powers[self.ID], game.availableWeapon(self.ID)
	#	posBtns = [Hero1Pos, Power1Pos, Weapon1Pos] if self.ID == 1 else [Hero2Pos, Power2Pos, Weapon2Pos]
	#	#Redraw all the hands
	#	HeroButton(self.GUI, hero).plot(posBtns[0][0], posBtns[0][1])
	#	HeroPowerButton(self.GUI, power).plot(posBtns[1][0], posBtns[1][1])
	#	if weapon: WeaponButton(self.GUI, weapon).plot(posBtns[2][0], posBtns[2][1])