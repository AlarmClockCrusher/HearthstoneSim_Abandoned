# class AirboundBarrage(Spell):
# 	Class, school, name = "Warrior", "", "Airbound Barrage"
# 	requireTarget, mana = False, 1
# 	index = "Shadowverse~Warrior~Spell~1~Airbound Barrage"
# 	description = "Choose a friendly minion and then an enemy minion. Return the friendly minion to your hand and deal 3 damage to the enemy minion"
# 	def available(self):
# 		return self.selectableFriendlyMinionExists() and self.selectableEnemyMinionExists()
#
# 	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
# 		ownMinions = [minion for minion in self.Game.minionsonBoard(self.ID) if self.canSelect(minion)]
# 		enemyMinions = [minion for minion in self.Game.minionsonBoard(3-self.ID) if self.canSelect(minion)]
# 		if ownMinions and enemyMinions:
# 			self.ownMinion, self.enemyMinion = None, None
# 			self.Game.Discover.startSelectBoard(self, ownMinions)
# 			self.Game.Discover.startSelectBoard(self, enemyMinions)
# 			PRINT(self.Game, "Airbound Barrage returns friendly minion %s to player's hand"%self.ownMinion.name)
# 			self.Game.returnMiniontoHand(self.ownMinion, deathrattlesStayArmed=False)
# 			damage = (3 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
# 			PRINT(self.Game, "Airbound Barrage deals %d damage to enemy minion %s"%(damage, self.enemyMinion.name))
# 			self.dealsDamage(self.enemyMinion, damage)
# 		return None
#
# 	def selectBoardDecided(self, entity):
# 		if entity.ID == self.ID: self.ownMinion = entity
# 		else: self.enemyMinion = entity
#
#
# class EntrancingBlow(Spell):
# 	Class, school, name = "Warrior", "", "Entrancing Blow"
# 	requireTarget, mana = False, 2
# 	index = "Shadowverse~Warrior~Spell~2~Entrancing Blow"
# 	description = "fefwsfe"
# 	def available(self):
# 		for card in self.Game.Hand_Deck.hands[self.ID]:
# 			if card.type == "Minion":
# 				return True
# 		return False
#
# 	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
# 		minions = [card for card in self.Game.Hand_Deck.hands[self.ID]]
# 		if minions:
# 			self.Game.Discover.startSelectHand(self, minions)
# 		return None
#
# 	def selectHandDecided(self, obj):
# 		obj.buffDebuff(2, 0)
# 		minions = self.Game.minionsonBoard(3-self.ID)
# 		if minions:
# 			damage = (3 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
# 			self.dealsDamage(npchoice(minions), damage)
#
#
# class SavoringSlash(Spell):
# 	Class, school, name = "Warrior", "", "Savoring Slash"
# 	requireTarget, mana = False, 2
# 	index = "Shadowverse~Warrior~Spell~2~Savoring Slash"
# 	description = "fefwsfe"
# 	def available(self):
# 		return self.selectableEnemyMinionExists()
#
# 	#葬送是什么东西
# 	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
# 		minionsinHand = [card for card in self.Game.Hand_Deck.hands[self.ID]]
# 		enemyMinions = [minion for minion in self.Game.minionsonBoard(3-self.ID) if self.canSelect(minion)]
# 		if enemyMinions:
# 			self.minioninHand, self.enemyMinion = None, None
# 			if minionsinHand:
# 				self.Game.Discover.startSelectHand(self, minionsinHand)
# 			self.Game.Discover.startSelectBoard(self, enemyMinions)
# 			if self.minioninHand:
# 				pass
# 			damage = (3 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
# 			PRINT(self.Game, "Savoring Slash deals %d damage to enemy minion %s"%(damage, self.enemyMinion.name))
# 			self.dealsDamage(self.enemyMinion, damage)
# 		return None
#
# 	def selectBoardDecided(self, entity):
# 		self.enemyMinion = entity
#
# 	def selectHandDecided(self, entity):
# 		self.minioninHand = entity
#
#
# class PantherScout(SVMinion):
# 	Class, race, name = "Warrior", "", "Panther Scout"
# 	mana, attack, health = 2, 2, 2
# 	index = "Shadowverse~Warrior~Minion~2~2~2~~Panther Scout~Fanfare"
# 	requireTarget, keyWord, description = False, "", "Fanfare: Restore 1 Mana. Enhance 8: Gain +3/+3 and restore 7 Mana instead"
#
# 	def effCanTrig(self):
# 		self.effectViable = self.Game.Manas.manas[self.ID] > 7
#
# 	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
# 		if :
# 			PRINT(self.Game, "Panther Scout's Fanfare restores 7 Mana Crystals and gives minion +3/+3")
# 			self.entity.Game.Manas.restoreManaCrystal(7, self.entity.ID)
# 			self.buffDebuff(3, 3)
# 		else:
# 			PRINT(self.Game, "Panther Scout's Fanfare restores 1 Mana Crystal")
# 			self.entity.Game.Manas.restoreManaCrystal(1, self.entity.ID)
# 		return None
#
#
# class RoanWingedNexx(SVMinion):
# 	Class, race, name = "Warrior", "", "Roan Winged Nexx"
# 	mana, attack, health = 4, 3, 4
# 	index = "Shadowverse~Warrior~Minion~4~3~3~~Reclusive Ponderer~Ambush~Accelerate"
# 	requireTarget, keyWord, description = False, "Ambush", "Ambush. Accelerate 1: Draw a card"
#
# class ReclusivePonderer(SVMinion):
# 	Class, race, name = "Warrior", "", "Reclusive Ponderer"
# 	mana, attack, health = 4, 3, 3
# 	index = "Shadowverse~Warrior~Minion~4~3~3~~Reclusive Ponderer~Ambush~Accelerate"
# 	requireTarget, keyWord, description = False, "Ambush", "Ambush. Accelerate 1: Draw a card"
#
#

# """Token"""
#
#
# class SteelcladKnight(SVMinion):
#	 Class, race, name = "Swordcraft", "Officer", "Steelclad Knight"
#	 mana, attack, health = 2, 2, 2
#	 index = "Shadowverse~Swordcraft~Minion~2~2~2~Officer~Steelclad Knight~Uncollectible"
#	 requireTarget, keyWord, description = False, "", ""
#
#
# class HeavyKnight(SVMinion):
#	 Class, race, name = "Swordcraft", "Officer", "Heavy Knight"
#	 mana, attack, health = 1, 1, 2
#	 index = "Shadowverse~Swordcraft~Minion~1~1~2~Officer~Heavy Knight~Uncollectible"
#	 requireTarget, keyWord, description = False, "", ""
#
#
# class Knight(SVMinion):
#	 Class, race, name = "Swordcraft", "Officer", "Knight"
#	 mana, attack, health = 1, 1, 1
#	 index = "Shadowverse~Swordcraft~Minion~1~1~1~Officer~Knight~Uncollectible"
#	 requireTarget, keyWord, description = False, "", ""
#
#
# class ShieldGuardian(SVMinion):
#	 Class, race, name = "Swordcraft", "Officer", "Shield Guardian"
#	 mana, attack, health = 1, 1, 1
#	 index = "Shadowverse~Swordcraft~Minion~1~1~1~Officer~Shield Guardian~Taunt~Uncollectible"
#	 requireTarget, keyWord, description = False, "Taunt", "Ward"
#
#
# class FortressGuard(SVMinion):
#	 Class, race, name = "Swordcraft", "Officer", "Fortress Guard"
#	 mana, attack, health = 3, 2, 3
#	 index = "Shadowverse~Swordcraft~Minion~3~2~3~Officer~Fortress Guard~Taunt~Uncollectible"
#	 requireTarget, keyWord, description = False, "Taunt", "Ward"
#
#
# class GildedBlade(Spell):
#	 Class, school, name = "Swordcraft", "", "Gilded Blade"
#	 requireTarget, mana = True, 1
#	 index = "Shadowverse~Swordcraft~Spell~1~Gilded Blade~Uncollectible"
#	 description = "Deal 1 damage to an enemy follower."
#
#	 def available(self):
#		 return self.selectableEnemyMinionExists()
#
#	 def targetCorrect(self, target, choice=0):
#		 return target.cardType == "Minion" and target.ID != self.ID and target.onBoard
#
#	 def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
#		 if target is not None:
#			 damage = (1 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
#			 PRINT(self, f"Gilded Blade deals {damage} damage to minion {target.name}")
#			 self.dealsDamage(target, damage)
#		 return target
#
#
# class GildedGoblet(Spell):
#	 Class, school, name = "Swordcraft", "", "Gilded Goblet"
#	 requireTarget, mana = True, 1
#	 index = "Shadowverse~Swordcraft~Spell~1~Gilded Goblet~Uncollectible"
#	 description = "Restore 2 defense to an ally."
#
#	 def targetCorrect(self, target, choice=0):
#		 return target.ID == self.ID and target.onBoard
#
#	 def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
#		 if target is not None:
#			 heal = 2 * (2 ** self.countHealDouble())
#			 PRINT(self, f"Gilded Goblet restores {heal} Health to {target.name}")
#			 self.restoresHealth(target, heal)
#
#
# class GildedBoots(Spell):
#	 Class, school, name = "Swordcraft", "", "Gilded Boots"
#	 requireTarget, mana = True, 1
#	 index = "Shadowverse~Swordcraft~Spell~1~Gilded Boots~Uncollectible"
#	 description = "Give Rush to an allied follower."
#
#	 def available(self):
#		 return self.selectableFriendlyExists()
#
#	 def targetCorrect(self, target, choice=0):
#		 return target.cardType == "Minion" and target.ID == self.ID and target.onBoard
#
#	 def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
#		 if target is not None:
#			 PRINT(self, f"Gilded Boots gives minion {target.name} Rush")
#			 target.getsStatus("Rush")
#		 return target
#
#
# class GildedNecklace(Spell):
#	 Class, school, name = "Swordcraft", "", "Gilded Necklace"
#	 requireTarget, mana = True, 1
#	 index = "Shadowverse~Swordcraft~Spell~1~Gilded Necklace~Uncollectible"
#	 description = "Give +1/+1 to an allied follower."
#
#	 def available(self):
#		 return self.selectableFriendlyExists()
#
#	 def targetCorrect(self, target, choice=0):
#		 return target.cardType == "Minion" and target.ID == self.ID and target.onBoard
#
#	 def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
#		 if target is not None:
#			 PRINT(self, f"Gilded Necklace gives minion {target.name} +1/+1")
#			 target.buffDebuff(1, 1)
#		 return target
#
#
# """1 Cost"""
#
#
# class GrandAcquisition(Spell):
#	 Class, school, name = "Swordcraft", "", "Grand Acquisition"
#	 requireTarget, mana = False, 1
#	 index = "Shadowverse~Swordcraft~Spell~1~Grand Acquisition"
#	 description = "Choose: Put 1 of the following cards into your hand. -Gilded Blade -Gilded Goblet -Gilded Boots -Gilded Necklace Enhance (6): Put 1 of each into your hand instead and recover 6 play points."
#
#	 def getMana(self):
#		 if self.Game.Manas.manas[self.ID] >= 6:
#			 return 6
#		 else:
#			 return self.mana
#
#	 def effCanTrig(self):
#		 self.effectViable = self.getMana() != self.mana
#
#	 def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
#		 if choice == 6:
#			 PRINT(self, "Grand Acquisition is cast")
#			 if self.Game.Hand_Deck.handNotFull(self.ID):
#				 self.Game.Hand_Deck.addCardtoHand(GildedBlade(self.Game, self.ID), self.ID, creator=type(self))
#			 if self.Game.Hand_Deck.handNotFull(self.ID):
#				 self.Game.Hand_Deck.addCardtoHand(GildedGoblet(self.Game, self.ID), self.ID, creator=type(self))
#			 if self.Game.Hand_Deck.handNotFull(self.ID):
#				 self.Game.Hand_Deck.addCardtoHand(GildedBoots(self.Game, self.ID), self.ID, creator=type(self))
#			 if self.Game.Hand_Deck.handNotFull(self.ID):
#				 self.Game.Hand_Deck.addCardtoHand(GildedNecklace(self.Game, self.ID), self.ID, creator=type(self))
#			 self.Game.Manas.manas[self.ID] += 6
#			 PRINT(self, "Grand Acquisition restore 6 manas.")
#		 elif self.ID == self.Game.turn and self.Game.Hand_Deck.handNotFull(self.ID):
#			 PRINT(self, "Grand Acquisition lets player choose a Spell to get:")
#			 self.Game.options = [GildedBlade(self.Game, self.ID), GildedGoblet(self.Game, self.ID),
#								  GildedBoots(self.Game, self.ID), GildedNecklace(self.Game, self.ID)]
#			 self.Game.DiscoverHandler.startDiscover(self)
#		 return None
#
#	 def discoverDecided(self, option):
#		 self.Game.Hand_Deck.addCardtoHand(option, self.ID, creator=type(self))
#		 return None
#
#
# class Quickblader(SVMinion):
#	 Class, race, name = "Swordcraft", "Officer", "Quickblader"
#	 mana, attack, health = 1, 1, 1
#	 index = "Shadowverse~Swordcraft~Minion~1~1~1~Officer~Quickblader~Charge"
#	 requireTarget, keyWord, description = False, "Charge", "Storm"
#
#
# class Kagemitsu(SVMinion):
#	 Class, race, name = "Swordcraft", "Officer", "Kagemitsu, Matchless Blade"
#	 mana, attack, health = 1, 0, 1
#	 index = "Shadowverse~Swordcraft~Minion~1~0~1~Officer~Kagemitsu, Matchless Blade~Battlecry~Deathrattle"
#	 requireTarget, keyWord, description = False, "", "Fanfare: Enhance (3) - Gain +2/+0 and Rush.Last Words: If it is your turn, give your leader the following effect - At the start of your turn, summon a Kagemitsu, Matchless Blade, evolve it, then remove this effect."
#
#	 attackAdd, healthAdd = 1, 0
#
#	 def __init__(self, Game, ID):
#		 super().__init__(Game, ID)
#		 if self.status["Evolved"] < 1:
#			 self.deathrattles = [DeathrattleKagemitsu(self)]
#
#	 def inEvolving(self):
#		 for d in self.deathrattles:
#			 if type(d) == DeathrattleKagemitsu:
#				 d.disconnect()
#				 self.deathrattles.remove(d)
#		 trigger = TriggerKagemitsu(self)
#		 self.trigsBoard.append(trigger)
#		 if self.onBoard:
#			 trigger.connect()
#
#	 def effCanTrig(self):
#		 self.effectViable = self.getMana() != self.mana
#
#	 def getMana(self):
#		 if self.Game.Manas.manas[self.ID] >= 3:
#			 return 3
#		 else:
#			 return self.mana
#
#	 def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
#		 if choice == 3:
#			 PRINT(self, "Levin Beastmaster's Fanfare give it +2/+0 and Rush.")
#			 self.getsStatus("Rush")
#			 self.buffDebuff(2, 0)
#		 return None
#
#
# class TriggerKagemitsu(TriggeronBoard):
#	 def __init__(self, entity):
#		 super().__init__(entity, ["MinionAttackingHero", "MinionAttackingMinion"])
#
#	 def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
#		 return self.entity.onBoard and subject == self.entity
#
#	 def effect(self, signal, ID, subject, target, number, comment, choice=0):
#		 evolved = self.entity.Game.Counters.numMinionsEvolvedThisGame[ID]
#		 PRINT(self, f"Minion {self.entity.name} attacks and get +{evolved}/+{evolved}")
#		 self.entity.buffDebuff(evolved, evolved)
#
#
# class DeathrattleKagemitsu(Deathrattle_Minion):
#	 def effect(self, signal, ID, subject, target, number, comment, choice=0):
#		 if ID == self.entity.ID:
#			 PRINT(self,
#				   "Last Words: If it is your turn, give your leader the following effect - At the start of your turn, summon a Kagemitsu, Matchless Blade, evolve it, then remove this effect.")
#			 trigger = TriggerSummonAEvolvedKagemitsuNextTurn(self.entity.Game.heroes[self.entity.ID])
#			 self.entity.Game.heroes[self.entity.ID].trigsBoard.append(trigger)
#			 trigger.connect()
#
#
# class TriggerSummonAEvolvedKagemitsuNextTurn(TriggeronBoard):
#	 def __init__(self, entity):
#		 super().__init__(entity, ["TurnStarts"])
#
#	 def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
#		 return self.entity.onBoard and ID == self.entity.ID
#
#	 def effect(self, signal, ID, subject, target, number, comment, choice=0):
#		 kag = Kagemitsu(self.entity.Game, ID)
#		 self.entity.Game.summonMinion([kag], (-11, "totheRightEnd"), ID)
#		 kag.evolve()
#		 for t in self.entity.Game.heroes[ID].trigsBoard:
#			 if type(t) == TriggerSummonAEvolvedKagemitsuNextTurn:
#				 t.disconnect()
#				 self.entity.Game.heroes[ID].trigsBoard.remove(t)
#				 break
#
#
# class ErnestaWeaponsHawker(SVMinion):
#	 Class, race, name = "Swordcraft", "Officer", "Ernesta, Weapons Hawker"
#	 mana, attack, health = 1, 1, 1
#	 index = "Shadowverse~Swordcraft~Minion~1~1~1~Officer~Ernesta, Weapons Hawker~Battlecry"
#	 requireTarget, keyWord, description = False, "", "Fanfare: Rally (10) - Put a Dread Hound into your hand."
#
#	 def effCanTrig(self):
#		 self.effectViable = self.Game.Counters.numMinionsSummonThisGame[self.ID] >= 10
#
#	 def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
#		 if self.Game.Counters.numMinionsSummonThisGame[self.ID] >= 10:
#			 if self.Game.Hand_Deck.handNotFull(self.ID):
#				 self.Game.Hand_Deck.addCardtoHand(DreadHound(self.Game, self.ID), self.ID, creator=type(self))
#		 return None
#
#
# class DreadHound(SVMinion):
#	 Class, race, name = "Swordcraft", "Officer", "Dread Hound"
#	 mana, attack, health = 1, 4, 4
#	 index = "Shadowverse~Swordcraft~Minion~1~4~4~Officer~Dread Hound~Battlecry~Poisonous~Taunt~Uncollectable"
#	 requireTarget, keyWord, description = False, "Poisonous,Taunt", "Bane.Ward.Fanfare: Give a random allied Ernesta, Weapons Hawker Last Words - Deal 4 damage to a random enemy follower."
#
#	 def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
#		 ts = self.Game.minionsAlive(self.ID)
#		 targets = []
#		 for t in ts:
#			 if t.name == "Ernesta, Weapons Hawker":
#				 targets.append(t)
#		 if targets:
#			 target = np.random.choice(targets)
#			 PRINT(self,
#				   f"Dread Hound's Fanfare gives {target.name} Last Words - Deal 4 damage to a random enemy follower.")
#			 deathrattle = DeathrattleErnestaWeaponsHawker(target)
#			 target.deathrattles.append(deathrattle)
#			 if target.onBoard:
#				 deathrattle.connect()
#		 return None
#
#
# class DeathrattleErnestaWeaponsHawker(Deathrattle_Minion):
#	 def effect(self, signal, ID, subject, target, number, comment, choice=0):
#		 PRINT(self, "Last Words: Deal 4 damage to a random enemy follower.")
#		 targets = self.entity.Game.minionsAlive(3 - self.entity.entity.ID)
#		 if targets != []:
#			 target = np.random.choice(targets)
#			 PRINT(self, f"Ernesta, Weapons Hawker's Last Words deals 4 damage to minion {target.name}")
#			 self.entity.dealsDamage(target, 4)
#
#
# class DecisiveStrike(Spell):
#	 Class, school, name = "Swordcraft", "", "Decisive Strike"
#	 requireTarget, mana = True, 1
#	 index = "Shadowverse~Swordcraft~Spell~1~Decisive Strike"
#	 description = "Deal X damage to an enemy follower. X equals the attack of the highest-attack Commander follower in your hand.Enhance (5): Deal X damage to all enemy followers instead."
#
#	 def getMana(self):
#		 if self.Game.Manas.manas[self.ID] >= 5:
#			 return 5
#		 else:
#			 return self.mana
#
#	 def effCanTrig(self):
#		 self.effectViable = self.getMana() != self.mana
#
#	 def returnTrue(self, choice=0):
#		 if self.getMana() == 5:
#			 return False
#		 return True
#
#	 def targetCorrect(self, target, choice=0):
#		 return target.cardType == "Minion" and target.ID != self.ID and target.onBoard
#
#	 def available(self):
#		 if self.getMana() == 5:
#			 return True
#		 return self.selectableEnemyMinionExists()
#
#	 def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
#		 damage = 0
#		 for card in self.Game.Hand_Deck.hands[self.ID]:
#			 if card.cardType == "Minion" and "Commander" in card.race and card.attack > damage:
#				 damage = card.attack
#		 damage = (damage + self.countSpellDamage()) * (2 ** self.countDamageDouble())
#		 if choice == 5:
#			 targets = self.Game.minionsonBoard(3 - self.ID)
#			 self.dealsAOE(targets, [damage for minion in targets])
#		 elif self.ID == self.Game.turn:
#			 PRINT(self, f"Decisive Strike deals {damage} damage to minion {target.name}")
#			 self.dealsDamage(target, damage)
#		 return None
#
#
# class PompousSummons(Spell):
#	 Class, school, name = "Swordcraft", "", "Pompous Summons"
#	 requireTarget, mana = False, 1
#	 index = "Shadowverse~Swordcraft~Spell~1~Pompous Summons"
#	 description = "Put a random Swordcraft follower from your deck into your hand.Rally (10): Put 2 random Swordcraft followers into your hand instead."
#
#	 def effCanTrig(self):
#		 self.effectViable = self.Game.Counters.numMinionsSummonThisGame[self.ID] >= 10
#
#	 def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
#		 minions = []
#		 for card in self.Game.Hand_Deck.decks[self.ID]:
#			 if card.cardType == "Minion" and card.Class == "Swordcraft":
#				 minions.append(card)
#		 if minions:
#			 card = np.random.choice(minions)
#			 self.Game.Hand_Deck.drawCard(self.ID, card)
#			 PRINT(self, f"Pompous Summons let you draw {card.name}.")
#		 if self.Game.Counters.numMinionsSummonThisGame[self.ID] >= 10:
#			 minions = []
#			 for card in self.Game.Hand_Deck.decks[self.ID]:
#				 if card.cardType == "Minion" and card.Class == "Swordcraft":
#					 minions.append(card)
#			 if minions:
#				 card = np.random.choice(minions)
#				 self.Game.Hand_Deck.drawCard(self.ID, card)
#				 PRINT(self, f"Pompous Summons let you draw {card.name}.")
#		 return None
#
#
# class LevinJustice(Spell):
#	 Class, school, name = "Swordcraft", "", "Levin Justice"
#	 requireTarget, mana = True, 1
#	 index = "Shadowverse~Swordcraft~Spell~1~Levin Justice"
#	 description = "Put a Yurius, Levin Duke into your hand. Then deal X damage to an enemy follower. X equals the number of Levin cards in your hand."
#
#	 def available(self):
#		 return self.selectableEnemyMinionExists()
#
#	 def targetCorrect(self, target, choice=0):
#		 return target.cardType == "Minion" and target.ID != self.ID and target.onBoard
#
#	 def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
#		 if target:
#			 damage = 0
#			 for card in self.Game.Hand_Deck.hands[self.ID]:
#				 if card.cardType == "Minion" and "Levin" in card.race:
#					 damage += 1
#			 damage = (damage + self.countSpellDamage()) * (2 ** self.countDamageDouble())
#			 PRINT(self, f"Levin Justice deals {damage} damage to minion {target.name}")
#			 self.dealsDamage(target, damage)
#		 if self.Game.Hand_Deck.handNotFull(self.ID):
#			 PRINT(self, "Levin Justice add a Yurius, Levin Duke to your hand.")
#			 self.Game.Hand_Deck.addCardtoHand(YuriusLevinDuke, self.ID, byType=True, creator=type(self))
#		 return target
#
#
# class YuriusLevinDuke(SVMinion):
#	 Class, race, name = "Bloodcraft", "Levin", "Yurius, Levin Duke"
#	 mana, attack, health = 2, 1, 3
#	 index = "Shadowverse~Bloodcraft~Minion~2~1~3~Levin~Yurius, Levin Duke"
#	 requireTarget, keyWord, description = False, "", "Whenever an enemy follower comes into play, deal 1 damage to the enemy leader."
#
#	 def __init__(self, Game, ID):
#		 super().__init__(Game, ID)
#		 self.trigsBoard = [TriggerYuriusLevinDuke(self)]
#
#
# class TriggerYuriusLevinDuke(TriggeronBoard):
#	 def __init__(self, entity):
#		 super().__init__(entity, ["MinionSummoned"])
#
#	 def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
#		 return self.entity.onBoard and subject.ID != self.entity.ID and subject != self.entity
#
#	 def effect(self, signal, ID, subject, target, number, comment, choice=0):
#		 PRINT(self, f"A enemy minion {subject.name} is summoned and {self.entity.name} deals 1 damage to enemy leader.")
#		 self.entity.dealsDamage(self.entity.Game.heroes[3 - self.entity.ID], 1)
#
#
# class MeetTheLevinSisters(Spell):
#	 Class, school, name = "Swordcraft", "", "Meet the Levin Sisters!"
#	 requireTarget, mana = False, 1
#	 index = "Shadowverse~Swordcraft~Spell~1~Meet the Levin Sisters!"
#	 description = "Choose: Put 1 of the following cards into your hand.-Mina, Levin Vice Leader-Mona, Levin Mage-Mena, Levin DuelistEnhance (7): Put 1 of each into your hand instead, and recover 6 play points."
#
#	 def effCanTrig(self):
#		 self.effectViable = self.getMana() != self.mana
#
#	 def getMana(self):
#		 if self.Game.Manas.manas[self.ID] >= 7:
#			 return 7
#		 else:
#			 return self.mana
#
#	 def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
#		 if choice == 7:
#			 PRINT(self, "Meet the Levin Sisters! is cast")
#			 if self.Game.Hand_Deck.handNotFull(self.ID):
#				 self.Game.Hand_Deck.addCardtoHand(MinaLevinViceLeader(self.Game, self.ID), self.ID, creator=type(self))
#			 if self.Game.Hand_Deck.handNotFull(self.ID):
#				 self.Game.Hand_Deck.addCardtoHand(MonaLevinMage(self.Game, self.ID), self.ID, creator=type(self))
#			 if self.Game.Hand_Deck.handNotFull(self.ID):
#				 self.Game.Hand_Deck.addCardtoHand(MenaLevinDuelist(self.Game, self.ID), self.ID, creator=type(self))
#			 self.Game.Manas.manas[self.ID] += 6
#			 PRINT(self, "Meet the Levin Sisters! restore 6 manas.")
#		 elif self.ID == self.Game.turn and self.Game.Hand_Deck.handNotFull(self.ID):
#			 PRINT(self, "Meet the Levin Sisters! lets player choose a Spell to get:")
#			 self.Game.options = [MinaLevinViceLeader(self.Game, self.ID), MonaLevinMage(self.Game, self.ID),
#								  MenaLevinDuelist(self.Game, self.ID)]
#			 self.Game.DiscoverHandler.startDiscover(self)
#		 return None
#
#	 def discoverDecided(self, option):
#		 self.Game.Hand_Deck.addCardtoHand(option, self.ID, creator=type(self))
#		 return None
#
#
# class MinaLevinViceLeader(SVMinion):
#	 Class, race, name = "Swordcraft", "Levin", "Mina, Levin Vice Leader"
#	 mana, attack, health = 2, 2, 2
#	 index = "Shadowverse~Swordcraft~Minion~2~2~2~Levin~Mina, Levin Vice Leader~Battlecry~Uncollectable"
#	 requireTarget, keyWord, description = False, "", "Fanfare: Put a random Levin follower from your deck into your hand."
#
#	 def effect(self, signal, ID, subject, target, number, comment, choice=0):
#		 levins = []
#		 for card in self.Game.Hand_Deck.decks[self.ID]:
#			 if card.cardType == "Minion" and "Commander" in card.race:
#				 levins.append(card)
#		 if levins:
#			 card = np.random.choice(levins)
#			 self.Game.Hand_Deck.drawCard(self.ID, card)
#			 PRINT(self, f"Mina, Levin Vice Leader's Fanfare let you draw {card.name}.")
#
#
# class MonaLevinMage(SVMinion):
#	 Class, race, name = "Swordcraft", "Levin", "Mona, Levin Mage"
#	 mana, attack, health = 4, 3, 3
#	 index = "Shadowverse~Swordcraft~Minion~4~3~3~Levin~Mona, Levin Mage~Battlecry~Uncollectable"
#	 requireTarget, keyWord, description = False, "", "Fanfare: Recover 2 play points. If another allied Levin card is in play, recover 3 instead."
#
#	 def effCanTrig(self):
#		 controlLevin = False
#		 for minion in self.Game.minionsonBoard(self.ID):
#			 if "Levin" in minion.race:
#				 controlLevin = True
#				 break
#		 self.effectViable = controlLevin
#
#	 def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
#		 controlLevin = False
#		 for minion in self.Game.minionsonBoard(self.ID):
#			 if "Levin" in minion.race:
#				 controlLevin = True
#				 break
#		 n = 2
#		 if controlLevin:
#			 n = 3
#		 self.Game.Manas.manas[self.ID] += n
#		 PRINT(self, f"Mona, Levin Mage's Fanfare let you restore {n} mana.")
#
#
# class MenaLevinDuelist(SVMinion):
#	 Class, race, name = "Swordcraft", "Levin", "Mena, Levin Duelist"
#	 mana, attack, health = 3, 3, 2
#	 index = "Shadowverse~Swordcraft~Minion~3~3~2~Levin~Mena, Levin Duelist~Battlecry~Rush~Uncollectable"
#	 requireTarget, keyWord, description = False, "Rush", "Rush.Fanfare: If another allied Levin card is in play, gain +1/+1."
#
#	 def effCanTrig(self):
#		 controlLevin = False
#		 for minion in self.Game.minionsonBoard(self.ID):
#			 if "Levin" in minion.race:
#				 controlLevin = True
#				 break
#		 self.effectViable = controlLevin
#
#	 def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
#		 controlLevin = False
#		 for minion in self.Game.minionsonBoard(self.ID):
#			 if "Levin" in minion.race:
#				 controlLevin = True
#				 break
#		 if controlLevin:
#			 self.buffDebuff(1, 1)
#			 PRINT(self, f"Mena, Levin Duelist's Fanfare give itself +1/+1.")
#
#
# class LounesLevinApprentice(SVMinion):
#	 Class, race, name = "Swordcraft", "Levin", "Lounes, Levin Apprentice"
#	 mana, attack, health = 1, 1, 1
#	 index = "Shadowverse~Swordcraft~Minion~1~1~1~Levin~Lounes, Levin Apprentice~Battlecry"
#	 requireTarget, keyWord, description = False, "", "Fanfare: Gain +0/+1 for each Levin card in your hand.Enhance (3): Can attack 2 times per turn."
#
#	 def effCanTrig(self):
#		 self.effectViable = self.getMana() != self.mana
#
#	 def getMana(self):
#		 if self.Game.Manas.manas[self.ID] >= 3:
#			 return 3
#		 else:
#			 return self.mana
#
#	 def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
#		 levins = 0
#		 for card in self.Game.Hand_Deck.hands[self.ID]:
#			 if card.cardType == "Minion" and "Levin" in card.race:
#				 levins += 1
#		 if levins > 0:
#			 self.buffDebuff(0, levins)
#			 PRINT(self, f"Lounes, Levin Apprentice's Fanfare give itself +1/+{levins}.")
#		 if choice == 3:
#			 self.getsStatus("Windfury")
#			 PRINT(self, f"Lounes, Levin Apprentice's Fanfare give itself Can attack 2 times per turn.")
#
#
# """2 Cost"""
#
#
# class OathlessKnight(SVMinion):
#	 Class, race, name = "Swordcraft", "Officer", "Oathless Knight"
#	 mana, attack, health = 2, 1, 1
#	 index = "Shadowverse~Swordcraft~Minion~2~1~1~Officer~Oathless Knight~Battlecry"
#	 requireTarget, keyWord, description = False, "", "Fanfare: Summon a Knight."
#
#	 def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
#		 PRINT(self, "Oathless Knight's Fanfare summons a 1/1 Knight.")
#		 self.Game.summonMinion([Knight(self.Game, self.ID)], (-11, "totheRightEnd"), self.ID)
#		 return None
#
#
# class PantherScout(SVMinion):
#	 Class, race, name = "Swordcraft", "Officer,Natura", "Panther Scout"
#	 mana, attack, health = 2, 2, 2
#	 index = "Shadowverse~Swordcraft~Minion~2~2~2~Officer,Natura~Panther Scout~Battlecry"
#	 requireTarget, keyWord, description = False, "", "Fanfare: Recover 1 play point.Enhance (8): Gain +3/+3 and recover 7 play points instead."
#
#	 def effCanTrig(self):
#		 self.effectViable = self.getMana() != self.mana
#
#	 def getMana(self):
#		 if self.Game.Manas.manas[self.ID] >= 8:
#			 return 8
#		 else:
#			 return self.mana
#
#	 def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
#		 r = 1
#		 if choice == 8:
#			 r = 7
#			 self.buffDebuff(3, 3)
#			 PRINT(self, f"Panther Scout's Fanfare gives itself +3/+3.")
#		 PRINT(self, f"Panther Scout's Fanfare restores {r} PP.")
#		 self.Game.Manas.manas[self.ID] += r
#		 return None
#
#
# class HonorableThief(SVMinion):
#	 Class, race, name = "Swordcraft", "Officer", "Honorable Thief"
#	 mana, attack, health = 2, 2, 2
#	 index = "Shadowverse~Swordcraft~Minion~2~2~2~Officer~Honorable Thief~Battlecry~Deathrattle"
#	 requireTarget, keyWord, description = False, "", "Fanfare: Rally (7) - Evolve this follower. Last Words: Put a Gilded Boots into your hand."
#
#	 def __init__(self, Game, ID):
#		 super().__init__(Game, ID)
#		 self.deathrattles = [DeathrattleHonorableThief(self)]
#
#	 def effCanTrig(self):
#		 self.effectViable = self.Game.Counters.numMinionsSummonThisGame[self.ID] >= 7
#
#	 def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
#		 if self.Game.Counters.numMinionsSummonThisGame[self.ID] >= 7:
#			 self.evolve()
#		 return None
#
#
# class DeathrattleHonorableThief(Deathrattle_Minion):
#	 def effect(self, signal, ID, subject, target, number, comment, choice=0):
#		 if self.entity.Game.Hand_Deck.handNotFull(self.entity.ID):
#			 PRINT(self, "Last Words: Add a 'GildedBoots' to your hand triggers.")
#			 self.entity.Game.Hand_Deck.addCardtoHand(GildedBoots, self.entity.ID, byType=True, creator=type(self.entity))
#
#
# class WhiteTiger(SVMinion):
#	 Class, race, name = "Havencraft", "", "White Tiger"
#	 mana, attack, health = 3, 3, 2
#	 index = "Shadowverse~Havencraft~Minion~3~3~2~~White Tiger~Taunt"
#	 requireTarget, keyWord, description = False, "Taunt", "Ward Can't be targeted by enemy spells and effects."
#
#	 def __init__(self, Game, ID):
#		 super().__init__(Game, ID)
#		 self.marks["Enemy Effect Evasive"] = 1
#
#
# class LevinWhiteTiger(WhiteTiger):
#	 race = "Levin"
#	 index = "Shadowverse~Havencraft~Minion~3~3~2~Levin~White Tiger~Taunt~Uncollectible"
#
#
# class LevinBeastmaster(SVMinion):
#	 Class, race, name = "Swordcraft", "Levin", "Levin Beastmaster"
#	 mana, attack, health = 2, 2, 2
#	 index = "Shadowverse~Swordcraft~Minion~2~2~2~Levin~Levin Beastmaster~Battlecry"
#	 requireTarget, keyWord, description = False, "", "Fanfare: Enhance (6) - Summon 2 White Tigers and change them into Levin followers."
#
#	 def effCanTrig(self):
#		 self.effectViable = self.getMana() != self.mana
#
#	 def getMana(self):
#		 if self.Game.Manas.manas[self.ID] >= 6:
#			 return 6
#		 else:
#			 return self.mana
#
#	 def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
#		 if choice == 6:
#			 PRINT(self,
#				   "Levin Beastmaster's Fanfare summons two 1/1 White Tigers and change them into Levin followers.")
#			 self.Game.summonMinion([LevinWhiteTiger(self.Game, self.ID) for i in range(2)], (-11, "totheRightEnd"),
#									self.ID)
#		 return None
#
#	 def inEvolving(self):
#		 PRINT(self, "Levin Beastmaster evolves and summons a 1/1 White Tiger and change it into Levin followers.")
#		 self.Game.summonMinion([LevinWhiteTiger(self.Game, self.ID)], (-11, "totheRightEnd"), self.ID)
#
#
# class EleganceInAction(Spell):
#	 Class, school, name = "Swordcraft", "", "Elegance in Action"
#	 requireTarget, mana = False, 2
#	 index = "Shadowverse~Swordcraft~Spell~2~Elegance in Action"
#	 description = "Draw a card. Summon a Heavy Knight for each follower drawn. Deal 3 damage to a random enemy follower for each non-follower drawn.Enhance (5): Draw 3 cards instead."
#
#	 def effCanTrig(self):
#		 self.effectViable = self.getMana() != self.mana
#
#	 def getMana(self):
#		 if self.Game.Manas.manas[self.ID] >= 5:
#			 return 5
#		 else:
#			 return self.mana
#
#	 def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
#		 draw = 1
#		 if choice == 5:
#			 draw = 3
#		 for i in range(draw):
#			 card, mana = self.Game.Hand_Deck.drawCard(self.ID)
#			 if card:
#				 if card.cardType == "Minion":
#					 self.Game.summonMinion([HeavyKnight(self.Game, self.ID)], (-11, "totheRightEnd"), self.ID)
#				 else:
#					 damage = (3 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
#					 targets = self.Game.minionsAlive(3 - self.ID)
#					 if targets != []:
#						 target = np.random.choice(targets)
#						 PRINT(self, f"Elegance in Action deals {damage} damage to minion {target.name}")
#						 self.dealsDamage(target, damage)
#		 return None
#
#
# class ShieldPhalanx(Spell):
#	 Class, school, name = "Swordcraft", "", "Shield Phalanx"
#	 requireTarget, mana = False, 2
#	 index = "Shadowverse~Swordcraft~Spell~2~Shield Phalanx"
#	 description = "Summon a Shield Guardian and Knight.Rally (15): Summon a Frontguard General instead of a Shield Guardian."
#
#	 def available(self):
#		 return self.Game.space(self.ID)
#
#	 def effCanTrig(self):
#		 self.effectViable = self.Game.Counters.numMinionsSummonThisGame[self.ID] >= 15
#
#	 def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
#		 if self.Game.Counters.numMinionsSummonThisGame[self.ID] >= 15:
#			 PRINT(self, "Shield Phalanx summons a Frontguard General and Knight.")
#			 self.Game.summonMinion([FrontguardGeneral(self.Game, self.ID), Knight(self.Game, self.ID)],
#									(-11, "totheRightEnd"), self.ID)
#		 else:
#			 PRINT(self, "Shield Phalanx summons a Shield Guardian and Knight.")
#			 self.Game.summonMinion([ShieldGuardian(self.Game, self.ID), Knight(self.Game, self.ID)],
#									(-11, "totheRightEnd"), self.ID)
#		 return None
#
#
# class MirrorsImage(Spell):
#	 Class, school, name = "Swordcraft", "", "Mirror Image"
#	 requireTarget, mana = True, 2
#	 index = "Shadowverse~Swordcraft~Spell~2~Mirror Image"
#	 description = "Choose an allied follower in play and summon a copy of it. Give it Rush, and banish it at the start of your next turn."
#
#	 def available(self):
#		 return self.selectableFriendlyExists() and self.Game.space(self.ID)
#
#	 def targetCorrect(self, target, choice=0):
#		 return target.cardType == "Minion" and target.ID == self.ID and target.onBoard
#
#	 def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
#		 if target is not None:
#			 m = type(target)(self.Game, self.ID)
#			 PRINT(self, f"Mirror Image summon a copy of {target.name} and give it Rush.")
#			 self.Game.summonMinion([m], (-11, "totheRightEnd"), self.ID)
#			 m.getsStatus("Rush")
#			 trigger = TriggerMirrorsImage(m, self.ID)
#			 m.trigsBoard.append(trigger)
#			 if m.onBoard:
#				 trigger.connect()
#		 return target
#
#
# class TriggerMirrorsImage(TriggeronBoard):
#	 def __init__(self, entity, ID):
#		 super().__init__(entity, ["TurnStarts"])
#		 self.temp = True
#		 self.ID = ID
#
#	 def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
#		 return self.entity.onBoard and ID == self.ID
#
#	 def effect(self, signal, ID, subject, target, number, comment, choice=0):
#		 PRINT(self, f"At the start of player {self.ID}'s turn,  minion {self.entity.name} disappears.")
#		 self.entity.disappears(keepDeathrattlesRegistered=False)
#		 self.entity.Game.removeMinionorWeapon(self.entity)
#		 self.disconnect()
#		 extractfrom(self, self.entity.trigsBoard)
#
#	 def selfCopy(self, recipient):
#		 trigger = type(self)(recipient, self.ID)
#		 return trigger
#
#
# class SteadfastSamurai(SVMinion):
#	 Class, race, name = "Swordcraft", "Officer", "Steadfast Samurai"
#	 mana, attack, health = 2, 1, 1
#	 index = "Shadowverse~Swordcraft~Minion~2~1~1~Officer~Steadfast Samurai"
#	 requireTarget, keyWord, description = False, "", "Fanfare: Enhance (5) - Evolve this follower.Clash: Reduce damage to this follower to 0 until the end of the turn."
#
#	 def __init__(self, Game, ID):
#		 super().__init__(Game, ID)
#		 self.trigsBoard = [TriggerClashSteadfastSamurai(self)]
#
#	 def effCanTrig(self):
#		 self.effectViable = self.getMana() != self.mana
#
#	 def getMana(self):
#		 if self.Game.Manas.manas[self.ID] >= 5:
#			 return 5
#		 else:
#			 return self.mana
#
#	 def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
#		 if choice == 5:
#			 self.evolve()
#		 return None
#
#	 def inEvolving(self):
#		 self.getsStatus("Charge")
#		 self.auras["Buff Aura"] = BuffAuraEvolvedSteadfastSamurai(self)
#		 self.auras["Buff Aura"].auraAppears()
#
#
# class TriggerClashSteadfastSamurai(TriggeronBoard):
#	 def __init__(self, entity):
#		 super().__init__(entity, ["MinionAttackingMinion"])
#
#	 def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
#		 return self.entity.onBoard and (target == self.entity or subject == self.entity)
#
#	 def effect(self, signal, ID, subject, target, number, comment, choice=0):
#		 self.entity.marks["Damage Immune"] += 1
#		 trigger = TriggerTurnEndSteadfastSamurai(self.entity)
#		 self.entity.trigsBoard.append(trigger)
#		 if self.entity.onBoard:
#			 trigger.connect()
#
#
# class TriggerTurnEndSteadfastSamurai(TriggeronBoard):
#	 def __init__(self, entity):
#		 super().__init__(entity, ["TurnEnds"])
#
#	 def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
#		 return self.entity.onBoard
#
#	 def effect(self, signal, ID, subject, target, number, comment, choice=0):
#		 self.entity.marks["Damage Immune"] -= 1
#		 for t in self.entity.trigsBoard:
#			 if type(t) == TriggerTurnEndSteadfastSamurai:
#				 t.disconnect()
#				 self.entity.trigsBoard.remove(t)
#				 break
#
#
# class BuffAuraEvolvedSteadfastSamurai(AuraDealer_toMinion):
#	 def __init__(self, entity):
#		 self.entity = entity
#		 self.signals, self.auraAffected = [], []
#
#	 # Minions appearing/disappearing will let the minion reevaluate the aura.
#	 def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
#		 return self.entity.onBoard
#
#	 def effect(self, signal, ID, subject, target, number, comment, choice=0):
#		 self.applies(self.entity.Game.heroes[self.entity.ID])
#
#	 def applies(self, subject):
#		 subject.marks["Enemy Effect Damage Immune"] += 1
#
#	 def auraAppears(self):
#		 self.applies(self.entity.Game.heroes[self.entity.ID])
#
#	 def auraDisappears(self):
#		 self.entity.Game.heroes[self.entity.ID].marks["Enemy Effect Damage Immune"] -= 1
#
#	 def selfCopy(self, recipientMinion):  # The recipientMinion is the minion that deals the Aura.
#		 return type(self)(recipientMinion)
#
#
# class TwinswordMaster(SVMinion):
#	 Class, race, name = "Swordcraft", "Officer", "Twinsword Master"
#	 mana, attack, health = 2, 2, 2
#	 index = "Shadowverse~Swordcraft~Minion~2~2~2~Officer~Twinsword Master~Battlecry"
#	 requireTarget, keyWord, description = False, "", "Fanfare: If an allied Commander card is in play, gain the ability to evolve for 0 evolution points."
#
#	 attackAdd, healthAdd = 1, 1
#
#	 def effCanTrig(self):
#		 self.effectViable = False
#		 for minion in self.Game.minionsonBoard(self.ID):
#			 if "Commander" in minion.race:
#				 self.effectViable = True
#				 break
#
#	 def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
#		 controlOfficer = False
#		 for minion in self.Game.minionsonBoard(self.ID):
#			 if "Commander" in minion.race:
#				 controlOfficer = True
#				 break
#		 if controlOfficer:
#			 self.getsStatus("Free Evolve")
#		 return None
#
#	 def inEvolving(self):
#		 self.getsStatus("Windfury")
#
#
# class ValseChampionDeadeye(SVMinion):
#	 Class, race, name = "Swordcraft", "Officer", "Valse, Champion Deadeye"
#	 mana, attack, health = 2, 2, 2
#	 index = "Shadowverse~Swordcraft~Minion~2~2~2~Officer~Valse, Champion Deadeye~Battlecry"
#	 requireTarget, keyWord, description = True, "", "Fanfare: Enhance (6) - Banish an enemy follower or amulet."
#	 evolveRequireTarget = True
#
#	 def effCanTrig(self):
#		 self.effectViable = self.getMana() != self.mana
#
#	 def getMana(self):
#		 if self.Game.Manas.manas[self.ID] >= 6:
#			 return 6
#		 else:
#			 return self.mana
#
#	 def targetExists(self, choice=0):
#		 return choice == 6 and self.selectableEnemyMinionExists(choice)
#
#	 def targetCorrect(self, target, choice=0):
#		 return choice == 6 and target.cardType == "Minion" and target.ID != self.ID and target.onBoard
#
#	 def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
#		 if choice == 6:
#			 target.disappears(keepDeathrattlesRegistered=False)
#			 target.Game.removeMinionorWeapon(target)
#			 PRINT(self, f"Valse, Champion Deadeye let {target.name} disappears.")
#		 return None
#
#	 def inHandEvolving(self, target=None):
#		 if target:
#			 target.dead = True
#			 PRINT(self, f"Valse, Champion Deadeye destroys {target.name}.")
#		 return
#
#	 def extraTargetCorrect(self, target, affair):
#		 return target.cardType and target.cardType == "Minion" and target.ID != self.ID and target.onBoard and target.health <= 3
#
#
# class LevinArcher(SVMinion):
#	 Class, race, name = "Swordcraft", "Levin", "Levin Archer"
#	 mana, attack, health = 2, 2, 2
#	 index = "Shadowverse~Swordcraft~Minion~2~2~2~Levin~Levin Archer"
#	 requireTarget, keyWord, description = False, "", ""
#	 evolveRequireTarget = True
#
#	 def inHandEvolving(self, target=None):
#		 if target:
#			 PRINT(self, f"Levin Archer deals 3 damage to minion {target.name}")
#			 self.dealsDamage(target, 3)
#		 return
#
#	 def extraTargetCorrect(self, target, affair):
#		 if target.cardType and target.cardType == "Minion" and target.ID != self.ID and target.onBoard:
#			 for card in self.Game.Hand_Deck.hands[self.ID]:
#				 if card.cardType == "Minion" and "Levin" in card.race:
#					 return True
#		 return False
#
#
# class JenoLevinStalwart(SVMinion):
#	 Class, race, name = "Swordcraft", "Levin", "Jeno, Levin Stalwart"
#	 mana, attack, health = 2, 2, 2
#	 index = "Shadowverse~Swordcraft~Minion~2~2~2~Levin~Jeno, Levin Stalwart"
#	 requireTarget, keyWord, description = False, "", "Can evolve an allied Levin follower (excluding Jeno, Levin Stalwart) each turn for 0 evolution points until this follower leaves play."
#
#	 def __init__(self, Game, ID):
#		 super().__init__(Game, ID)
#		 self.auras["Has Aura"] = EffectAura(self, "Free Evolve")
#
#	 def applicable(self, target):
#		 return target.cardType == "Minion" and "Levin" in target.race
#
#
# """3 Cost"""
#
#
# class GabrielHeavenlyVoice(SVMinion):
#	 Class, race, name = "Neutral", "", "Gabriel, Heavenly Voice"
#	 mana, attack, health = 3, 2, 3
#	 index = "Shadowverse~Neutral~Minion~3~2~3~~Gabriel, Heavenly Voice~Battlecry~Taunt"
#	 requireTarget, keyWord, description = True, "Taunt", "Ward.Fanfare: Use X play points to give +X/+X to this follower and another allied follower. X equals your remaining play points."
#
#	 def targetExists(self, choice=0):
#		 return self.selectableFriendlyMinionExists(choice)
#
#	 def targetCorrect(self, target, choice=0):
#		 return target.cardType == "Minion" and target.ID == self.ID and target.onBoard and target != self
#
#	 def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
#		 x = self.Game.Manas.manas[self.ID]
#		 self.Game.Manas.manas[self.ID] -= x
#		 if target:
#			 target.buffDebuff(x, x)
#		 self.buffDebuff(x, x)
#		 PRINT(self, f"Gabriel, Heavenly Voice's Fanfare give {target.name} and itself +{x}/+{x}.")
#		 return None
#
#
# class EmpressOfSerenity(SVMinion):
#	 Class, race, name = "Swordcraft", "Commander", "Empress of Serenity"
#	 mana, attack, health = 3, 2, 2
#	 index = "Shadowverse~Swordcraft~Minion~3~2~2~Commander~Empress of Serenity~Battlecry"
#	 requireTarget, keyWord, description = False, "", "Fanfare: Summon a Shield Guardian.Enhance (5): Summon 3 instead.Enhance (10): Give +3/+3 to all allied Shield Guardians."
#
#	 def effCanTrig(self):
#		 self.effectViable = self.getMana() != self.mana
#
#	 def getMana(self):
#		 if self.Game.Manas.manas[self.ID] >= 10:
#			 return 10
#		 elif self.Game.Manas.manas[self.ID] >= 5:
#			 return 5
#		 else:
#			 return self.mana
#
#	 def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
#		 if choice == 0:
#			 PRINT(self,
#				   "Empress of Serenity's Fanfare summons a 1/1 Shield Guardian with Taunt.")
#			 self.Game.summonMinion([ShieldGuardian(self.Game, self.ID)], (-11, "totheRightEnd"), self.ID)
#		 else:
#			 PRINT(self,
#				   "Empress of Serenity's Fanfare summons three 1/1 Shield Guardian with Taunt.")
#			 self.Game.summonMinion([ShieldGuardian(self.Game, self.ID) for i in range(3)], (-11, "totheRightEnd"),
#									self.ID)
#			 if choice == 10:
#				 for minion in self.Game.minionsonBoard(self.ID):
#					 if type(minion) == ShieldGuardian:
#						 minion.buffDebuff(3, 3)
#				 PRINT(self,
#					   "Empress of Serenity's Fanfare give +3/+3 to all allied Shield Guardians.")
#		 return None
#
#
# class OluonTheChariot(SVMinion):
#	 Class, race, name = "Swordcraft", "Commander", "VII. Oluon, The Chariot"
#	 mana, attack, health = 3, 3, 3
#	 index = "Shadowverse~Swordcraft~Minion~3~3~3~Commander~VII. Oluon, The Chariot~Battlecry"
#	 requireTarget, keyWord, description = False, "", "Fanfare: Enhance (7) - Transform this follower into a VII. Oluon, Runaway Chariot.At the end of your turn, randomly activate 1 of the following effects.-Gain Ward.-Summon a Knight.-Deal 2 damage to the enemy leader."
#
#	 def __init__(self, Game, ID):
#		 super().__init__(Game, ID)
#		 self.trigsBoard = [TriggerOluonTheChariot(self)]
#
#	 def effCanTrig(self):
#		 self.effectViable = self.getMana() != self.mana
#
#	 def getMana(self):
#		 if self.Game.Manas.manas[self.ID] >= 7:
#			 return 7
#		 else:
#			 return self.mana
#
#	 def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
#		 if choice == 7:
#			 self.Game.transform(self, OluonRunawayChariot(self.Game, self.ID))
#		 return None
#
#
# class OluonRunawayChariot(SVMinion):
#	 Class, race, name = "Swordcraft", "Commander", "VII. Oluon, Runaway Chariot"
#	 mana, attack, health = 7, 8, 16
#	 index = "Shadowverse~Swordcraft~Minion~7~8~16~Commander~VII. Oluon, Runaway Chariot~Uncollectable"
#	 requireTarget, keyWord, description = False, "", "Can't attack.At the end of your turn, randomly deal X damage to an enemy or another ally and then Y damage to this follower. X equals this follower's attack and Y equals the attack of the follower or leader damaged (leaders have 0 attack). Do this 2 times."
#
#	 def __init__(self, Game, ID):
#		 super().__init__(Game, ID)
#		 self.marks["Can't Attack"] = 1
#		 self.trigsBoard = [TriggerOluonRunawayChariot(self)]
#
#
# class TriggerOluonTheChariot(TriggeronBoard):
#	 def __init__(self, entity):
#		 super().__init__(entity, ["TurnEnds"])
#
#	 def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
#		 return self.entity.onBoard and ID == self.entity.ID
#
#	 def effect(self, signal, ID, subject, target, number, comment, choice=0):
#		 es = ["T", "H", "K"]
#		 e = np.random.choice(es)
#		 if e == "T":
#			 self.entity.getsStatus("Taunt")
#		 elif e == "H":
#			 self.entity.dealsDamage(self.entity.Game.heroes[3 - self.entity.ID], 2)
#		 elif e == "K":
#			 PRINT(self,
#				   "VII. Oluon, The Chariot summons a 1/1 Shield Guardian with Ward.")
#			 self.entity.Game.summonMinion([ShieldGuardian(self.entity.Game, self.entity.ID)], (-11, "totheRightEnd"),
#										   self.entity.ID)
#
#
# class TriggerOluonRunawayChariot(TriggeronBoard):
#	 def __init__(self, entity):
#		 super().__init__(entity, ["TurnEnds"])
#
#	 def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
#		 return self.entity.onBoard and ID == self.entity.ID
#
#	 def effect(self, signal, ID, subject, target, number, comment, choice=0):
#		 for i in range(2):
#			 targets = []
#			 for e in self.entity.Game.livingObjtoTakeRandomDamage(1):
#				 if e != self.entity:
#					 targets.append(e)
#			 for e in self.entity.Game.livingObjtoTakeRandomDamage(2):
#				 if e != self.entity:
#					 targets.append(e)
#			 target = np.random.choice(targets)
#			 self.entity.dealsDamage(target, self.entity.attack)
#			 PRINT(self, f"VII. Oluon, Runaway Chariot deals {self.entity.attack} damage to {target}")
#			 damage = 0
#			 if target.cardType == "Minion":
#				 damage = target.attack
#			 target.dealsDamage(self.entity, damage)
#			 PRINT(self, f"{target} deals {damage} damage to VII. Oluon, Runaway Chariot ")
#
#
# class GeltResoluteKnight(SVMinion):
#	 Class, race, name = "Swordcraft", "Officer", "Gelt, Resolute Knight"
#	 mana, attack, health = 3, 3, 3
#	 index = "Shadowverse~Swordcraft~Minion~3~3~3~Officer~Gelt, Resolute Knight~Battlecry~Deathrattle"
#	 requireTarget, keyWord, description = False, "", "Fanfare: If an allied Commander card is in play, gain Rush.Last Words: At the start of your next turn, put a random Commander card from your deck into your hand."
#
#	 def __init__(self, Game, ID):
#		 super().__init__(Game, ID)
#		 self.deathrattles = [DeathrattleGeltResoluteKnight(self)]
#
#	 def effCanTrig(self):
#		 self.effectViable = False
#		 for minion in self.Game.minionsonBoard(self.ID):
#			 if "Commander" in minion.race:
#				 self.effectViable = True
#				 break
#
#	 def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
#		 controlOfficer = False
#		 for minion in self.Game.minionsonBoard(self.ID):
#			 if "Commander" in minion.race:
#				 controlOfficer = True
#				 break
#		 if controlOfficer:
#			 self.getsStatus("Rush")
#		 return None
#
#
# class DeathrattleGeltResoluteKnight(Deathrattle_Minion):
#	 def effect(self, signal, ID, subject, target, number, comment, choice=0):
#		 PRINT(self,
#			   "Last Words: At the start of your next turn, put a random Commander card from your deck into your hand.")
#		 trigger = TriggerDeathrattleGeltResoluteKnight(self.entity.Game.heroes[self.entity.ID])
#		 self.entity.Game.heroes[self.entity.ID].trigsBoard.append(trigger)
#		 trigger.connect()
#
#
# class TriggerDeathrattleGeltResoluteKnight(TriggeronBoard):
#	 def __init__(self, entity):
#		 super().__init__(entity, ["TurnStarts"])
#
#	 def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
#		 return ID == self.entity.ID
#
#	 def effect(self, signal, ID, subject, target, number, comment, choice=0):
#		 commanders = []
#		 for card in self.entity.Game.Hand_Deck.decks[self.entity.ID]:
#			 if card.cardType == "Minion" and "Commander" in card.race:
#				 commanders.append(card)
#		 if commanders:
#			 card = np.random.choice(commanders)
#			 self.entity.Game.Hand_Deck.drawCard(self.entity.ID, card)
#			 PRINT(self, f"Gelt, Resolute Knight's Last Words let you draw {card.name}.")
#		 for t in self.entity.Game.heroes[ID].trigsBoard:
#			 if type(t) == TriggerDeathrattleGeltResoluteKnight:
#				 t.disconnect()
#				 self.entity.Game.heroes[ID].trigsBoard.remove(t)
#				 break
#
#
# class LadyOfTheLance(SVMinion):
#	 Class, race, name = "Swordcraft", "Officer", "Lady of the Lance"
#	 mana, attack, health = 3, 3, 2
#	 index = "Shadowverse~Swordcraft~Minion~3~3~2~Officer~Lady of the Lance~Battlecry~Rush"
#	 requireTarget, keyWord, description = False, "Rush", "Rush.Fanfare: If you have at least 2 Commander cards in your hand, gain Bane and the following effect - The next time this follower takes damage, reduce that damage to 0.Fanfare: Enhance (8) - Gain Storm. Recover 5 play points."
#
#	 def getMana(self):
#		 if self.Game.Manas.manas[self.ID] >= 8:
#			 return 8
#		 else:
#			 return self.mana
#
#	 def effCanTrig(self):
#		 commanders = 0
#		 for card in self.Game.Hand_Deck.hands[self.ID]:
#			 if card.cardType == "Minion" and "Commander" in card.race:
#				 commanders += 1
#		 self.effectViable = commanders >= 2 or self.getMana() != self.mana
#
#	 def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
#		 if choice == 8:
#			 PRINT(self, "Lady of the Lance's Fanfare give it Storm.")
#			 self.getsStatus("Charge")
#			 self.Game.Manas.manas[self.ID] += 5
#		 commanders = 0
#		 for card in self.Game.Hand_Deck.hands[self.ID]:
#			 if card.cardType == "Minion" and "Commander" in card.race:
#				 commanders += 1
#		 if commanders >= 2:
#			 PRINT(self, "Lady of the Lance's Fanfare give it Bane and reduce next damage to 0.")
#			 self.getsStatus("Poisonous")
#			 self.marks["Next Damage 0"] += 1
#		 return None
#
#
# class PecorinePeckishPrincess(SVMinion):
#	 Class, race, name = "Swordcraft", "Commander", "Pecorine, Peckish Princess"
#	 mana, attack, health = 3, 3, 2
#	 index = "Shadowverse~Swordcraft~Minion~3~3~2~Commander~Pecorine, Peckish Princess~Battlecry~Rush"
#	 requireTarget, keyWord, description = True, "Rush", "Rush.Fanfare: Union Burst (10) - Gain +3/+3. Deal 5 damage to an enemy follower.At the end of your turn, gain +0/+1."
#
#	 def __init__(self, Game, ID):
#		 super().__init__(Game, ID)
#		 self.trigsBoard = [TriggerPecorinePeckishPrincess(self)]
#
#	 def effCanTrig(self):
#		 self.effectViable = self.marks["UB"] <= self.Game.Counters.numTurnPassedThisGame[self.ID]
#
#	 def targetExists(self, choice=0):
#		 if self.marks["UB"] <= self.Game.Counters.numTurnPassedThisGame[self.ID]:
#			 return self.selectableEnemyMinionExists(choice)
#		 return False
#
#	 def targetCorrect(self, target, choice=0):
#		 return target.cardType == "Minion" and target.ID != self.ID and target.onBoard
#
#	 def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
#		 if self.marks["UB"] <= self.Game.Counters.numTurnPassedThisGame[self.ID]:
#			 self.buffDebuff(3, 3)
#			 if target:
#				 PRINT(self, f"Pecorine, Peckish Princess deals 5 damage to minion {target.name}")
#				 self.dealsDamage(target, 5)
#		 return None
#
#
# class TriggerPecorinePeckishPrincess(TriggeronBoard):
#	 def __init__(self, entity):
#		 super().__init__(entity, ["TurnEnds"])
#
#	 def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
#		 return self.entity.onBoard and ID == self.entity.ID
#
#	 def effect(self, signal, ID, subject, target, number, comment, choice=0):
#		 PRINT(self, "Pecorine Peckish Princess gains +0/+1.")
#		 self.entity.buffDebuff(0, 1)
#
#
# class TsubakiOfTheDemonBlade(SVMinion):
#	 Class, race, name = "Swordcraft", "Officer", "Tsubaki of the Demon Blade"
#	 mana, attack, health = 3, 3, 2
#	 index = "Shadowverse~Swordcraft~Minion~3~3~2~Officer~Tsubaki of the Demon Blade~Battlecry~Stealth"
#	 requireTarget, keyWord, description = False, "Stealth", "Ambush.Fanfare: If at least 10 allied followers have been destroyed this match, gain +1/+1 and randomly destroy 1 of the enemy followers with the highest attack in play."
#
#	 def effCanTrig(self):
#		 self.effectViable = self.Game.Counters.numMinionsDiedThisGame[self.ID] >= 10
#
#	 def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
#		 if self.Game.Counters.numMinionsDiedThisGame[self.ID] >= 10:
#			 self.buffDebuff(1, 1)
#			 PRINT(self, f"Tsubaki of the Demon Blade's Fanfare gives itself +1/+1.")
#			 ts = self.Game.minionsAlive(3 - self.ID)
#			 maxAttack = 0
#			 for t in ts:
#				 maxAttack = max(maxAttack, t.attack)
#			 targets = []
#			 for t in ts:
#				 if t.attack == maxAttack:
#					 targets.append(t)
#			 if targets:
#				 target = np.random.choice(targets)
#			 if target:
#				 target.dead = True
#				 PRINT(self, f"Tsubaki of the Demon Blade's Fanfare destroys {target.name}.")
#		 return None
#
#
# class StrokeOfConviction(Spell):
#	 Class, school, name = "Swordcraft", "", "Stroke of Conviction"
#	 requireTarget, mana = False, 3
#	 index = "Shadowverse~Swordcraft~Spell~3~Stroke of Conviction"
#	 description = "Choose: Use play points equal to this card's cost and play this card as an Erika's Sleight, Mistolina's Swordplay, or Bayleon's Command."
#
#	 def effCanTrig(self):
#		 self.effectViable = self.getMana() != self.mana
#
#	 def getMana(self):
#		 if self.Game.Manas.manas[self.ID] >= 6:
#			 return 6
#		 else:
#			 return self.mana
#
#	 def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
#		 if choice == 6:
#			 damage = (5 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
#			 PRINT(self,
#				   f"Stroke of Conviction is cast, summons two 1/1 Quickblader with Storm, deals {damage} damage to a random minion and gives all friendly minions +1/+1.")
#			 self.Game.summonMinion([Quickblader(self.Game, self.ID) for i in range(2)], (-11, "totheRightEnd"),
#									self.ID)
#			 targets = self.Game.minionsAlive(3 - self.ID)
#			 if targets != []:
#				 target = np.random.choice(targets)
#				 self.dealsDamage(target, damage)
#			 for minion in self.Game.minionsonBoard(self.ID):
#				 minion.buffDebuff(1, 1)
#		 elif self.ID == self.Game.turn:
#			 PRINT(self, "Stroke of Conviction lets player choose a Spell to cast:")
#			 self.Game.options = [ErikasSleight(self.Game, self.ID), MistolinasSwordplay(self.Game, self.ID),
#								  BayleonsCommand(self.Game, self.ID)]
#			 self.Game.DiscoverHandler.startDiscover(self)
#		 else:
#			 ErikasSleight(self.Game, self.ID).cast()
#		 return None
#
#	 def discoverDecided(self, option):
#		 option.cast()
#		 return None
#
#
# class ErikasSleight(Spell):
#	 Class, school, name = "Swordcraft", "", "Erika's Sleight"
#	 requireTarget, mana = False, 0
#	 index = "Shadowverse~Swordcraft~Spell~0~Erika's Sleight~Uncollectible"
#	 description = "Summon 2 Quickbladers."
#
#	 def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
#		 PRINT(self, "Erika's Sleight summons two 1/1 Quickblader with Storm.")
#		 self.Game.summonMinion([Quickblader(self.Game, self.ID) for i in range(2)], (-11, "totheRightEnd"),
#								self.ID)
#		 return None
#
#
# class MistolinasSwordplay(Spell):
#	 Class, school, name = "Swordcraft", "", "Mistolina's Swordplay"
#	 requireTarget, mana = False, 0
#	 index = "Shadowverse~Swordcraft~Spell~0~Mistolina's Swordplay~Uncollectible"
#	 description = "Deal 5 damage to a random enemy follower."
#
#	 def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
#		 damage = (5 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
#		 PRINT(self,
#			   f"Mistolina's Swordplay is cast and deals {damage} damage to a random minion.")
#		 targets = self.Game.minionsAlive(3 - self.ID)
#		 if targets != []:
#			 target = np.random.choice(targets)
#			 PRINT(self, f"Mistolina's Swordplay deals {damage} damage to minion {target.name}")
#			 self.dealsDamage(target, damage)
#		 return None
#
#
# class BayleonsCommand(Spell):
#	 Class, school, name = "Swordcraft", "", "Bayleon's Command"
#	 requireTarget, mana = False, 0
#	 index = "Shadowverse~Swordcraft~Spell~0~Bayleon's Command~Uncollectible"
#	 description = "Give +1/+1 to all allied followers."
#
#	 def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
#		 PRINT(self, "Bayleon's Command gives all friendly minions +1/+1.")
#		 for minion in self.Game.minionsonBoard(self.ID):
#			 minion.buffDebuff(1, 1)
#		 return None
#
#
# class CourtlyDance(Spell):
#	 Class, school, name = "Swordcraft", "", "Courtly Dance"
#	 requireTarget, mana = False, 3
#	 index = "Shadowverse~Swordcraft~Spell~3~Courtly Dance"
#	 description = "Put a random 1-play point and 2-play point Swordcraft follower from your deck into play.Enhance (8): Then, put a random 3-play point Swordcraft follower from your deck into play and evolve them. Evolve effects will not activate for those followers."
#
#	 def effCanTrig(self):
#		 self.effectViable = self.getMana() != self.mana
#
#	 def getMana(self):
#		 if self.Game.Manas.manas[self.ID] >= 8:
#			 return 8
#		 else:
#			 return self.mana
#
#	 def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
#		 ones, twos, threes = [], [], []
#		 a, b, c = None, None, None
#		 for card in self.Game.Hand_Deck.decks[self.ID]:
#			 if card.cardType == "Minion" and isinstance(card, SVMinion) and \
#					 card.mana == 1 and card.Class == "Swordcraft":
#				 ones.append(card)
#		 if ones != [] and self.Game.space(self.ID) > 0:
#			 a = np.random.choice(ones)
#			 self.Game.summonfromDeck(a, -1, self.ID)
#			 PRINT(self, f"Courtly Dance summons {a.name} from deck.")
#		 for card in self.Game.Hand_Deck.decks[self.ID]:
#			 if card.cardType == "Minion" and isinstance(card, SVMinion) and \
#					 card.mana == 2 and card.Class == "Swordcraft":
#				 twos.append(card)
#		 if twos != [] and self.Game.space(self.ID) > 0:
#			 b = np.random.choice(twos)
#			 self.Game.summonfromDeck(b, -1, self.ID)
#			 PRINT(self, f"Courtly Dance summons {b.name} from deck.")
#		 if choice == 8:
#			 for card in self.Game.Hand_Deck.decks[self.ID]:
#				 if card.cardType == "Minion" and isinstance(card, SVMinion) and \
#						 card.mana == 3 and card.Class == "Swordcraft":
#					 threes.append(card)
#			 if threes != [] and self.Game.space(self.ID) > 0:
#				 c = np.random.choice(threes)
#				 self.Game.summonfromDeck(c, -1, self.ID)
#				 PRINT(self, f"Courtly Dance summons {c.name} from deck.")
#			 if a and a.onBoard:
#				 a.evolve()
#				 PRINT(self, f"Courtly Dance let {a.name} evolve.")
#			 if b and b.onBoard:
#				 b.evolve()
#				 PRINT(self, f"Courtly Dance let {b.name} evolve.")
#			 if c and c.onBoard:
#				 c.evolve()
#				 PRINT(self, f"Courtly Dance let {c.name} evolve.")
#		 return None
#
#
# """4 Cost"""
#
#
# class FieranHavensentWindGod(SVMinion):
#	 Class, race, name = "Neutral", "", "Fieran, Havensent Wind God"
#	 mana, attack, health = 4, 1, 1
#	 index = "Shadowverse~Neutral~Minion~4~1~1~~Fieran, Havensent Wind God~Battlecry"
#	 requireTarget, keyWord, description = True, "Taunt", "Invocation: At the start of your turn, Rally (10) - Invoke this card.------Fanfare: If you have more evolution points than your opponent, gain +0/+2 and deal 2 damage to an enemy follower. (You have 0 evolution points on turns you are unable to evolve.)At the end of your turn, give +1/+1 to all allied followers."
#
#	 def __init__(self, Game, ID):
#		 super().__init__(Game, ID)
#		 self.trigsBoard = [TriggerFieranHavensentWindGod(self), TriggerInvocationFieranHavensentWindGod(self)]
#
#	 def targetExists(self, choice=0):
#		 selfPoint, oppPoint = 0, 0
#		 if self.Game.Counters.numTurnPassedThisGame[self.ID] >= \
#				 self.Game.Counters.numEvolutionTurn[self.ID]:
#			 selfPoint = self.Game.Counters.numEvolutionPoint[self.ID]
#		 if self.Game.Counters.numTurnPassedThisGame[3 - self.ID] >= \
#				 self.Game.Counters.numEvolutionTurn[3 - self.ID]:
#			 oppPoint = self.Game.Counters.numEvolutionPoint[3 - self.ID]
#		 return self.selectableEnemyMinionExists() and selfPoint > oppPoint
#
#	 def targetCorrect(self, target, choice=0):
#		 return target.cardType == "Minion" and target.ID != self.ID and target.onBoard
#
#	 def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
#		 selfPoint, oppPoint = 0, 0
#		 if self.Game.Counters.numTurnPassedThisGame[self.ID] >= \
#				 self.Game.Counters.numEvolutionTurn[self.ID]:
#			 selfPoint = self.Game.Counters.numEvolutionPoint[self.ID]
#		 if self.Game.Counters.numTurnPassedThisGame[3 - self.ID] >= \
#				 self.Game.Counters.numEvolutionTurn[3 - self.ID]:
#			 oppPoint = self.Game.Counters.numEvolutionPoint[3 - self.ID]
#		 if selfPoint > oppPoint:
#			 self.buffDebuff(0, 2)
#			 PRINT(self, f"Panther Scout's Fanfare gives itself +0/+2.")
#			 if target:
#				 PRINT(self, f"Gabriel, Heavenly Voice 2 damage to minion {target.name}")
#				 self.dealsDamage(target, 2)
#		 return None
#
#
# class TriggerFieranHavensentWindGod(TriggeronBoard):
#	 def __init__(self, entity):
#		 super().__init__(entity, ["TurnEnds"])
#
#	 def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
#		 return self.entity.onBoard and ID == self.entity.ID
#
#	 def effect(self, signal, ID, subject, target, number, comment, choice=0):
#		 targets = self.entity.Game.minionsonBoard(self.entity.ID)
#		 extractfrom(self.entity, targets)
#		 if targets:
#			 PRINT(self, "At the end of turn, Fieran, Havensent Wind God gives all friendly minions +1/+1")
#			 for target in targets:
#				 target.buffDebuff(1, 1)
#
#
# class TriggerInvocationFieranHavensentWindGod(TriggerinDeck):
#	 def __init__(self, entity):
#		 super().__init__(entity, ["TurnStarts"])
#
#	 def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
#		 return self.entity.inDeck and ID == self.entity.ID and self.entity.Game.space(self.entity.ID) > 0 and \
#				self.entity.Game.Counters.numMinionsSummonThisGame[self.entity.ID] >= 10 and \
#				self.entity.name not in self.entity.Game.Counters.minionInvocationThisTurn
#
#	 def effect(self, signal, ID, subject, target, number, comment, choice=0):
#		 if self.entity.Game.space(self.entity.ID) > 0:
#			 self.entity.Game.Counters.minionInvocationThisTurn.append(self.entity.name)
#			 self.entity.Game.summonfromDeck(self.entity, -1, self.entity.ID)
#			 PRINT(self, f"Fieran, Havensent Wind God is summoned from player {self.entity.ID}'s deck.")
#
#
# class ResolveOfTheFallen(Spell):
#	 Class, school, name = "Neutral", "", "Resolve of the Fallen"
#	 requireTarget, mana = True, 4
#	 index = "Shadowverse~Neutral~Spell~4~Resolve of the Fallen"
#	 description = "Destroy an enemy follower or amulet.If at least 3 allied followers have evolved this match, recover 3 play points.Then, if at least 5 have evolved, draw 2 cards."
#
#	 def available(self):
#		 return self.selectableEnemyMinionExists()
#
#	 def targetCorrect(self, target, choice=0):
#		 return target.cardType == "Minion" and target.ID != self.ID and target.onBoard
#
#	 def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
#		 if self.ID == self.Game.turn:
#			 target.dead = True
#		 if self.Game.Counters.numMinionsEvolvedThisGame[self.ID] > 3:
#			 self.Game.Manas.manas[self.ID] += 3
#		 if self.Game.Counters.numMinionsEvolvedThisGame[self.ID] > 5:
#			 self.Game.Hand_Deck.drawCard(self.ID)
#			 self.Game.Hand_Deck.drawCard(self.ID)
#		 return None
#
#
# class PrudentGeneral(SVMinion):
#	 Class, race, name = "Swordcraft", "Commander", "PrudentGeneral"
#	 mana, attack, health = 4, 3, 4
#	 index = "Shadowverse~Swordcraft~Minion~4~3~4~Commander~Prudent General"
#	 requireTarget, keyWord, description = False, "", ""
#
#	 def inEvolving(self):
#		 trigger = TriggerPrudentGeneral(self.Game.heroes[self.ID])
#		 for t in self.Game.heroes[self.ID].trigsBoard:
#			 if type(t) == type(trigger):
#				 return
#		 self.Game.heroes[self.ID].trigsBoard.append(trigger)
#		 trigger.connect()
#
#
# class TriggerPrudentGeneral(TriggeronBoard):
#	 def __init__(self, entity):
#		 super().__init__(entity, ["TurnEnds"])
#
#	 def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
#		 return self.entity.onBoard and ID == self.entity.ID
#
#	 def effect(self, signal, ID, subject, target, number, comment, choice=0):
#		 PRINT(self, "Prudent General's ability summons a 2/2 Steelclad Knight.")
#		 self.entity.Game.summonMinion([SteelcladKnight(self.entity.Game, self.entity.ID)], (-11, "totheRightEnd"),
#									   self.entity.ID)
#
#
# class ShizuruSisterlySabreur(SVMinion):
#	 Class, race, name = "Swordcraft", "Officer", "Shizuru, Sisterly Sabreur"
#	 mana, attack, health = 4, 3, 5
#	 index = "Shadowverse~Swordcraft~Minion~4~3~5~Officer~Shizuru, Sisterly Sabreur~Battlecry~Taunt"
#	 requireTarget, keyWord, description = False, "Taunt", "Ward.Fanfare: Union Burst (10) - Deal 3 damage to the enemy leader. Gain the ability to evolve for 0 evolution points."
#
#	 def effCanTrig(self):
#		 self.effectViable = self.marks["UB"] <= self.Game.Counters.numTurnPassedThisGame[self.ID]
#
#	 def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
#		 if self.marks["UB"] <= self.Game.Counters.numTurnPassedThisGame[self.ID]:
#			 self.getsStatus("Free Evolve")
#			 PRINT(self, f"Shizuru, Sisterly Sabreur 3 damage to the enemy leader.")
#			 self.dealsDamage(self.Game.heroes[3 - self.ID], 3)
#		 return None
#
#	 def inEvolving(self):
#		 trigger = TriggerShizuruSisterlySabreur(self)
#		 self.trigsBoard.append(trigger)
#		 if self.onBoard:
#			 trigger.connect()
#
#
# class TriggerShizuruSisterlySabreur(TriggeronBoard):
#	 def __init__(self, entity):
#		 super().__init__(entity, ["TurnEnds"])
#
#	 def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
#		 return self.entity.onBoard and ID == self.entity.ID
#
#	 def effect(self, signal, ID, subject, target, number, comment, choice=0):
#		 selfPoint, oppPoint = 0, 0
#		 if self.entity.Game.Counters.numTurnPassedThisGame[self.entity.ID] >= \
#				 self.entity.Game.Counters.numEvolutionTurn[self.entity.ID]:
#			 selfPoint = self.entity.Game.Counters.numEvolutionPoint[self.entity.ID]
#		 if self.entity.Game.Counters.numTurnPassedThisGame[3 - self.entity.ID] >= \
#				 self.entity.Game.Counters.numEvolutionTurn[3 - self.entity.ID]:
#			 oppPoint = self.entity.Game.Counters.numEvolutionPoint[3 - self.entity.ID]
#		 if selfPoint > oppPoint:
#			 self.entity.restoresHealth(self.entity, 3)
#			 self.entity.restoresHealth(self.entity.Game.heroes[self.entity.ID], 3)
#			 PRINT(self, "Shizuru, Sisterly Sabreur restore 3 defense to your leader and itself.")
#
#
# """5 Cost"""
#
#
# class ZelgeneaTheWorld(SVMinion):
#	 Class, race, name = "Neutral", "", "XXI. Zelgenea, The World"
#	 mana, attack, health = 5, 5, 5
#	 index = "Shadowverse~Neutral~Minion~5~5~5~~XXI. Zelgenea, The World~Battlecry"
#	 requireTarget, keyWord, description = False, "", "Invocation: At the start of your tenth turn, invoke this card. Then, evolve it.----------Fanfare: Restore 5 defense to your leader. If your leader had 14 defense or less before defense was restored, draw 2 cards and randomly destroy 1 of the enemy followers with the highest attack in play.Can't be evolved using evolution points. (Can be evolved using card effects.)"
#
#	 attackAdd, healthAdd = 5, 5
#
#	 def __init__(self, Game, ID):
#		 super().__init__(Game, ID)
#		 self.marks["Can't Evolve"] = 1
#		 self.trigsDeck = [TriggerInvocationZelgeneaTheWorld(self)]
#
#	 def effCanTrig(self):
#		 self.effectViable = self.Game.heroes[self.ID].health < 15
#
#	 def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
#		 if self.Game.heroes[self.ID].health < 15:
#			 self.restoresHealth(self.Game.heroes[self.ID], 5)
#			 PRINT(self, f"XXI. Zelgenea, The World restores 5 Health to its leader.")
#			 ts = self.Game.minionsAlive(3 - self.ID)
#			 maxAttack = 0
#			 for t in ts:
#				 maxAttack = max(maxAttack, t.attack)
#			 targets = []
#			 for t in ts:
#				 if t.attack == maxAttack:
#					 targets.append(t)
#			 if targets:
#				 target = np.random.choice(targets)
#			 if target:
#				 target.dead = True
#				 PRINT(self, f"XXI. Zelgenea, The World destroys {target.name}.")
#			 self.Game.Hand_Deck.drawCard(self.ID)
#			 self.Game.Hand_Deck.drawCard(self.ID)
#		 return None
#
#	 def inEvolving(self):
#		 trigger = TriggerAttackZelgeneaTheWorld(self)
#		 self.trigsBoard.append(trigger)
#		 trigger.connect()
#
#
# class TriggerAttackZelgeneaTheWorld(TriggeronBoard):
#	 def __init__(self, entity):
#		 super().__init__(entity, ["MinionAttackingHero", "MinionAttackingMinion"])
#
#	 def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
#		 return self.entity.onBoard and subject == self.entity
#
#	 def effect(self, signal, ID, subject, target, number, comment, choice=0):
#		 trigger = TriggerEndZelgeneaTheWorld(self.entity.Game.heroes[self.entity.ID])
#		 for t in self.entity.Game.heroes[self.entity.ID].trigsBoard:
#			 if type(t) == type(trigger):
#				 return
#		 self.entity.Game.heroes[self.entity.ID].trigsBoard.append(trigger)
#		 trigger.connect()
#
#
# class TriggerEndZelgeneaTheWorld(TriggeronBoard):
#	 def __init__(self, entity):
#		 super().__init__(entity, ["TurnEnds"])
#
#	 def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
#		 return self.entity.onBoard and ID == self.entity.ID
#
#	 def effect(self, signal, ID, subject, target, number, comment, choice=0):
#		 targets = [self.entity.Game.heroes[1], self.entity.Game.heroes[2]] + self.entity.Game.minionsonBoard(1) \
#				   + self.entity.Game.minionsonBoard(2)
#		 PRINT(self, "XXI. Zelgenea, The World's ability deals 4 damage to all characters.")
#		 self.entity.dealsAOE(targets, [4 for obj in targets])
#
#
# class TriggerInvocationZelgeneaTheWorld(TriggerinDeck):
#	 def __init__(self, entity):
#		 super().__init__(entity, ["TurnStarts"])
#
#	 def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
#		 return self.entity.inDeck and ID == self.entity.ID and self.entity.Game.space(self.entity.ID) > 0 and \
#				self.entity.Game.Counters.numTurnPassedThisGame[self.entity.ID] == 10 and \
#				self.entity.name not in self.entity.Game.Counters.minionInvocationThisTurn
#
#	 def effect(self, signal, ID, subject, target, number, comment, choice=0):
#		 if self.entity.Game.space(self.entity.ID) > 0:
#			 self.entity.Game.summonfromDeck(self.entity, -1, self.entity.ID)
#			 self.entity.Game.Counters.minionInvocationThisTurn.append(self.entity.name)
#			 PRINT(self, f"XXI. Zelgenea, The World is summoned from player {self.entity.ID}'s deck.")
#			 self.entity.evolve()
#
#
# class LuxbladeArriet(SVMinion):
#	 Class, race, name = "Swordcraft", "Officer", "Luxblade Arriet"
#	 mana, attack, health = 5, 4, 5
#	 index = "Shadowverse~Swordcraft~Minion~5~4~5~Officer~Luxblade Arriet~Battlecry"
#	 requireTarget, keyWord, description = False, "", "Fanfare: If at least 1 allied follower has evolved this match, gain Ward.Then, if at least 3 have evolved, recover 3 play points.Then, if at least 5 have evolved, restore 5 defense to your leader.Then, if at least 7 have evolved, draw cards until there are 7 cards in your hand."
#
#	 def effCanTrig(self):
#		 self.effectViable = self.Game.Counters.numMinionsEvolvedThisGame[self.ID] >= 1
#
#	 def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
#		 if self.Game.Counters.numMinionsEvolvedThisGame[self.ID] >= 1:
#			 PRINT(self, "Luxblade Arriet gains Ward.")
#			 self.getsStatus("Taunt")
#		 if self.Game.Counters.numMinionsEvolvedThisGame[self.ID] >= 3:
#			 PRINT(self, "Luxblade Arriet restores 3 PP.")
#			 self.Game.Manas.manas[self.ID] += 3
#		 if self.Game.Counters.numMinionsEvolvedThisGame[self.ID] >= 5:
#			 PRINT(self, "Luxblade Arriet restore 5 defense to your leader.")
#			 self.restoresHealth(self.Game.heroes[self.ID], 5)
#		 if self.Game.Counters.numMinionsEvolvedThisGame[self.ID] >= 7:
#			 PRINT(self, "Luxblade Arriet let you draw cards until there are 7 cards in your hand.")
#			 for i in range(7 - len(self.Game.Hand_Deck.hands[self.ID])):
#				 self.Game.Hand_Deck.drawCard(self.ID)
#		 return None
#
#	 def inEvolving(self):
#		 PRINT(self, "Levin Beastmaster evolves and summons a 1/1 White Tiger and change it into Levin followers.")
#		 self.Game.summonMinion([LevinWhiteTiger(self.Game, self.ID)], (-11, "totheRightEnd"), self.ID)
#
#
# class AmeliaTheSilverflash(SVMinion):
#	 Class, race, name = "Swordcraft", "Commander", "Amelia, the Silverflash"
#	 mana, attack, health = 5, 4, 4
#	 index = "Shadowverse~Swordcraft~Minion~5~4~4~Commander~Amelia, the Silverflash~Battlecry"
#	 requireTarget, keyWord, description = False, "", "Fanfare: Randomly put 2 different Officer followers from your deck into your hand.Enhance (7): Gain the ability to evolve for 0 evolution points and the following effect - The next time this follower takes damage, reduce that damage to 0."
#	 evolveRequireTarget = True
#
#	 def effCanTrig(self):
#		 self.effectViable = self.getMana() != self.mana
#
#	 def getMana(self):
#		 if self.Game.Manas.manas[self.ID] >= 7:
#			 return 7
#		 else:
#			 return self.mana
#
#	 def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
#		 officers = []
#		 for card in self.Game.Hand_Deck.decks[self.ID]:
#			 if card.cardType == "Minion" and "Officer" in card.race:
#				 officers.append(card)
#		 if officers:
#			 card = np.random.choice(officers)
#			 self.Game.Hand_Deck.drawCard(self.ID, card)
#			 PRINT(self, f"Amelia, the Silverflash's Fanfare let you draw {card.name}.")
#			 if self.Game.Hand_Deck.handNotFull(self.ID):
#				 offs = []
#				 for c in officers:
#					 if type(c) != type(card):
#						 offs.append(c)
#				 if offs:
#					 card = np.random.choice(offs)
#					 self.Game.Hand_Deck.drawCard(self.ID, card)
#					 PRINT(self, f"Amelia, the Silverflash's Fanfare let you draw {card.name}.")
#		 if choice == 7:
#			 self.getsStatus("Free Evolve")
#			 self.marks["Next Damage 0"] = 1
#		 return None
#
#	 def inHandEvolving(self, target=None):
#		 if target:
#			 ManaModification(target, changeby=-3).applies()
#			 trigger = TriggerAmeliaTheSilverflash(target)
#			 target.trigsHand.append(trigger)
#			 trigger.connect()
#			 PRINT(self, f"Amelia, the Silverflash let {target.name}'s cost -3 in this turn.")
#		 return
#
#	 def extraTargetCorrect(self, target, affair):
#
#		 return target.cardType and target.cardType == "Minion" and "Officer" in target.race and target.ID == self.ID and target.inHand
#
#
# class TriggerAmeliaTheSilverflash(TriggerinHand):
#	 def __init__(self, entity):
#		 super().__init__(entity, ["TurnEnds"])
#
#	 def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
#		 return self.entity.inHand and ID == self.entity.ID
#
#	 def effect(self, signal, ID, subject, target, number, comment, choice=0):
#		 for m in self.entity.manaModifications:
#			 if m.changeby == -3:
#				 self.entity.manaModifications.remove(m)
#				 break
#		 for t in self.entity.trigsHand:
#			 if type(t) == TriggerAmeliaTheSilverflash:
#				 t.disconnect()
#				 self.entity.trigsHand.remove(t)
#				 break
#
#
# class AlbertLevinChampion(SVMinion):
#	 Class, race, name = "Swordcraft", "Levin", "Albert, Levin Champion"
#	 mana, attack, health = 5, 3, 5
#	 index = "Shadowverse~Swordcraft~Minion~5~3~5~Levin~Albert, Levin Champion~Battlecry"
#	 requireTarget, keyWord, description = False, "Charge", "Storm.Fanfare: Enhance (9) - Randomly put different Levin followers (excluding Albert, Levin Champion) from your deck into play until your area is full.Strike: Gain +1/+0 if another allied Levin card is in play."
#
#	 def __init__(self, Game, ID):
#		 super().__init__(Game, ID)
#		 self.trigsBoard = [TriggerAlbertLevinChampion(self)]
#
#	 def effCanTrig(self):
#		 self.effectViable = self.getMana() != self.mana
#
#	 def getMana(self):
#		 if self.Game.Manas.manas[self.ID] >= 9:
#			 return 9
#		 else:
#			 return self.mana
#
#	 def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
#		 if choice == 9:
#			 names = []
#			 for i in range(4):
#				 minions = []
#				 for card in self.Game.Hand_Deck.decks[self.ID]:
#					 if card.cardType == "Minion" and isinstance(card, SVMinion) and \
#							 "Levin" in card.race and card.Class == "Swordcraft" and card.name not in names:
#						 minions.append(card)
#				 if minions != [] and self.Game.space(self.ID) > 0:
#					 m = np.random.choice(minions)
#					 names.append(m.name)
#					 self.Game.summonfromDeck(m, -1, self.ID)
#					 PRINT(self, f"Albert, Levin Champion's Fanfare summons {m.name} from deck.")
#				 else:
#					 break
#		 return None
#
#
# class TriggerAlbertLevinChampion(TriggeronBoard):
#	 def __init__(self, entity):
#		 super().__init__(entity, ["MinionAttackingHero", "MinionAttackingMinion"])
#
#	 def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
#		 return self.entity.onBoard and subject == self.entity
#
#	 def effect(self, signal, ID, subject, target, number, comment, choice=0):
#		 controlLevin = False
#		 for minion in self.entity.Game.minionsonBoard(self.entity.ID):
#			 if "Levin" in minion.race:
#				 controlLevin = True
#				 break
#		 if controlLevin:
#			 PRINT(self, f"Minion {self.entity.name} attacks and get +1/+0")
#			 self.entity.buffDebuff(1, 0)
#
#
# """6 Cost"""
#
#
# class DiamondPaladin(SVMinion):
#	 Class, race, name = "Swordcraft", "Commander", "Diamond Paladin"
#	 mana, attack, health = 6, 4, 5
#	 index = "Shadowverse~Swordcraft~Minion~6~4~5~Commander~Diamond Paladin~Battlecry~Rush"
#	 requireTarget, keyWord, description = False, "Rush", "Rush.Fanfare: Enhance (8) - Gain the ability to evolve for 0 evolution points.During your turn, whenever this follower attacks and destroys an enemy follower, if this follower is not destroyed, recover 2 play points and gain the ability to attack 2 times this turn."
#	 evolveRequireTarget = True
#
#	 def __init__(self, Game, ID):
#		 super().__init__(Game, ID)
#		 self.trigsBoard = [TriggerDiamondPaladin(self)]
#
#	 def effCanTrig(self):
#		 self.effectViable = self.getMana() != self.mana
#
#	 def getMana(self):
#		 if self.Game.Manas.manas[self.ID] >= 8:
#			 return 8
#		 else:
#			 return self.mana
#
#	 def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
#		 if choice == 8:
#			 self.getsStatus("Free Evolve")
#		 return None
#
#	 def inHandEvolving(self, target=None):
#		 if target:
#			 target.buffDebuff(-4, 0)
#			 PRINT(self, f"Diamond Paladin's Fanfare give {target.name} -4/-0.")
#		 return
#
#	 def extraTargetCorrect(self, target, affair):
#		 return target.cardType and target.cardType == "Minion" and target.ID != self.ID and target.onBoard
#
#
# class TriggerDiamondPaladin(TriggeronBoard):
#	 def __init__(self, entity):
#		 super().__init__(entity, ["MinionAttackedMinion"])
#
#	 def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
#		 return subject == self.entity and self.entity.onBoard and (target.health < 1 or target.dead == True) and \
#				(self.entity.health > 0 and self.entity.dead == False)
#
#	 def effect(self, signal, ID, subject, target, number, comment, choice=0):
#		 PRINT(self,
#			   "After %s attacks and kills minion %s, the player gains 10 Armor." % (self.entity.name, target.name))
#		 self.entity.getsStatus("Windfury")
#		 self.entity.Game.Manas.manas[self.entity.ID] += 2
#		 trigger = TriggerTurnEndDiamondPaladin(self.entity)
#		 self.entity.trigsBoard.append(trigger)
#		 if self.entity.onBoard:
#			 trigger.connect()
#
#
# class TriggerTurnEndDiamondPaladin(TriggeronBoard):
#	 def __init__(self, entity):
#		 super().__init__(entity, ["TurnEnds"])
#
#	 def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
#		 return self.entity.onBoard
#
#	 def effect(self, signal, ID, subject, target, number, comment, choice=0):
#		 self.entity.losesStatus("Windfury")
#		 for t in self.entity.trigsBoard:
#			 if type(t) == TriggerTurnEndDiamondPaladin:
#				 t.disconnect()
#				 self.entity.trigsBoard.remove(t)
#				 break
#
#
# """7 Cost"""
#
#
# class AccelerateRegalWildcat(AccelerateSpell):
#	 Class, school, name = "Swordcraft", "", "Regal Wildcat"
#	 requireTarget, mana = False, 4
#	 index = "Shadowverse~Swordcraft~Spell~4~Regal Wildcat~Uncollectible"
#	 description = "Summon a Steelclad Knight, a Heavy Knight, and a Knight."
#
#	 def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
#		 PRINT(self, "Regal Wildcat's accelerate summons a 2/2 Steelclad Knight, a 1/2 Heavy Knight, and a 1/1 Knight.")
#		 self.Game.summonMinion([SteelcladKnight(self.Game, self.ID), HeavyKnight(self.Game, self.ID),
#								 Knight(self.Game, self.ID)], (-11, "totheRightEnd"), self.ID)
#		 return None
#
#
# class RegalWildcat(AccelerateMinion):
#	 Class, race, name = "Swordcraft", "Commander", "Regal Wildcat"
#	 mana, attack, health = 7, 4, 4
#	 index = "Shadowverse~Swordcraft~Minion~7~4~4~Commander~Regal Wildcat~Battlecry~Charge"
#	 requireTarget, keyWord, description = True, "Charge", "Accelerate (4): Summon a Steelclad Knight, a Heavy Knight, and a Knight.----------Storm.Fanfare: If at least 10 allied followers have been destroyed this match, give another allied follower +2/+2 and Storm."
#	 accelerate = 4
#
#	 def __init__(self, Game, ID):
#		 super().__init__(Game, ID)
#
#	 def effCanTrig(self):
#		 self.effectViable = (self.getMana() > self.accelerate or self.mana <= self.accelerate) and \
#							 self.Game.Counters.numMinionsDiedThisGame[
#								 self.ID] >= 10 or self.getMana() != self.mana
#
#	 def targetExists(self, choice=0):
#		 if (self.getMana() > self.accelerate or self.mana <= self.accelerate) and \
#				 self.Game.Counters.numMinionsDiedThisGame[self.ID] >= 10:
#			 return self.selectableFriendlyMinionExists(choice)
#		 return False
#
#	 def targetCorrect(self, target, choice=0):
#		 return target.cardType == "Minion" and target.ID == self.ID and target != self and target.onBoard
#
#	 def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
#		 if target is not None:
#			 PRINT(self, f"Regal Wildcat gives minion {target.name} +2/+2 and Storm.")
#			 target.buffDebuff(2, 2)
#			 target.getsStatus("Charge")
#		 return target
#
#	 def getAccelerateSpell(self):
#		 return AccelerateRegalWildcat(self.Game, self.ID)
#
#
# class FrontguardGeneral(SVMinion):
#	 Class, race, name = "Swordcraft", "Commander", "Frontguard General"
#	 mana, attack, health = 7, 5, 6
#	 index = "Shadowverse~Swordcraft~Minion~7~5~6~Commander~Fortress Guard~Taunt~Deathrattle"
#	 requireTarget, keyWord, description = False, "Taunt", "Ward.Last Words: Summon a Fortress Guard."
#
#	 def __init__(self, Game, ID):
#		 super().__init__(Game, ID)
#		 self.deathrattles = [DeathrattleFrontguardGeneral(self)]
#
#
# class DeathrattleFrontguardGeneral(Deathrattle_Minion):
#	 def effect(self, signal, ID, subject, target, number, comment, choice=0):
#		 PRINT(self, "Last Words: Summon a Fortress Guard.")
#		 self.entity.Game.summonMinion([FortressGuard(self.entity.Game, self.entity.ID)], (-11, "totheRightEnd"),
#									   self.entity.ID)
#
#
# class HonoredFrontguardGeneral(SVMinion):
#	 Class, race, name = "Swordcraft", "Commander", "Honored Frontguard General"
#	 mana, attack, health = 7, 5, 6
#	 index = "Shadowverse~Swordcraft~Minion~7~5~6~Commander~Honored Fortress Guard~Taunt~Deathrattle"
#	 requireTarget, keyWord, description = False, "Taunt", "Ward.Can't be targeted by enemy spells and effects.Last Words: Summon a Shield Guardian, and give it +X/+X. X equals the number of times that allied followers have evolved during this match."
#
#	 def __init__(self, Game, ID):
#		 super().__init__(Game, ID)
#		 self.deathrattles = [DeathrattleHonoredFrontguardGeneral(self)]
#		 self.marks["Enemy Effect Evasive"] = 1
#
#
# class DeathrattleHonoredFrontguardGeneral(Deathrattle_Minion):
#	 def effect(self, signal, ID, subject, target, number, comment, choice=0):
#		 evolved = self.entity.Game.Counters.numMinionsEvolvedThisGame[self.entity.ID]
#		 PRINT(self, f"Last Words: Summon a Shield Guardian, and give it +{evolved}/+{evolved}.")
#		 s = ShieldGuardian(self.entity.Game, self.entity.ID)
#		 self.entity.Game.summonMinion([s], (-11, "totheRightEnd"), self.entity.ID)
#		 s.buffDebuff(evolved, evolved)# class AirboundBarrage(Spell):
# 	Class, school, name = "Warrior", "", "Airbound Barrage"
# 	requireTarget, mana = False, 1
# 	index = "Shadowverse~Warrior~Spell~1~~Airbound Barrage"
# 	description = "Choose a friendly minion and then an enemy minion. Return the friendly minion to your hand and deal 3 damage to the enemy minion"
# 	def available(self):
# 		return self.selectableFriendlyMinionExists() and self.selectableEnemyMinionExists()
#
# 	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
# 		ownMinions = [minion for minion in self.Game.minionsonBoard(self.ID) if self.canSelect(minion)]
# 		enemyMinions = [minion for minion in self.Game.minionsonBoard(3-self.ID) if self.canSelect(minion)]
# 		if ownMinions and enemyMinions:
# 			self.ownMinion, self.enemyMinion = None, None
# 			self.Game.Discover.startSelectBoard(self, ownMinions)
# 			self.Game.Discover.startSelectBoard(self, enemyMinions)
# 			PRINT(self.Game, "Airbound Barrage returns friendly minion %s to player's hand"%self.ownMinion.name)
# 			self.Game.returnMiniontoHand(self.ownMinion, deathrattlesStayArmed=False)
# 			damage = (3 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
# 			PRINT(self.Game, "Airbound Barrage deals %d damage to enemy minion %s"%(damage, self.enemyMinion.name))
# 			self.dealsDamage(self.enemyMinion, damage)
# 		return None
#
# 	def selectBoardDecided(self, entity):
# 		if entity.ID == self.ID: self.ownMinion = entity
# 		else: self.enemyMinion = entity
#
#
# class EntrancingBlow(Spell):
# 	Class, school, name = "Warrior", "", "Entrancing Blow"
# 	requireTarget, mana = False, 2
# 	index = "Shadowverse~Warrior~Spell~2~~Entrancing Blow"
# 	description = "fefwsfe"
# 	def available(self):
# 		for card in self.Game.Hand_Deck.hands[self.ID]:
# 			if card.type == "Minion":
# 				return True
# 		return False
#
# 	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
# 		minions = [card for card in self.Game.Hand_Deck.hands[self.ID]]
# 		if minions:
# 			self.Game.Discover.startSelectHand(self, minions)
# 		return None
#
# 	def selectHandDecided(self, obj):
# 		obj.buffDebuff(2, 0)
# 		minions = self.Game.minionsonBoard(3-self.ID)
# 		if minions:
# 			damage = (3 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
# 			self.dealsDamage(npchoice(minions), damage)
#
#
# class SavoringSlash(Spell):
# 	Class, school, name = "Warrior", "", "Savoring Slash"
# 	requireTarget, mana = False, 2
# 	index = "Shadowverse~Warrior~Spell~2~~Savoring Slash"
# 	description = "fefwsfe"
# 	def available(self):
# 		return self.selectableEnemyMinionExists()
#
# 	#葬送是什么东西
# 	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
# 		minionsinHand = [card for card in self.Game.Hand_Deck.hands[self.ID]]
# 		enemyMinions = [minion for minion in self.Game.minionsonBoard(3-self.ID) if self.canSelect(minion)]
# 		if enemyMinions:
# 			self.minioninHand, self.enemyMinion = None, None
# 			if minionsinHand:
# 				self.Game.Discover.startSelectHand(self, minionsinHand)
# 			self.Game.Discover.startSelectBoard(self, enemyMinions)
# 			if self.minioninHand:
# 				pass
# 			damage = (3 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
# 			PRINT(self.Game, "Savoring Slash deals %d damage to enemy minion %s"%(damage, self.enemyMinion.name))
# 			self.dealsDamage(self.enemyMinion, damage)
# 		return None
#
# 	def selectBoardDecided(self, entity):
# 		self.enemyMinion = entity
#
# 	def selectHandDecided(self, entity):
# 		self.minioninHand = entity
#
#
# class PantherScout(SVMinion):
# 	Class, race, name = "Warrior", "", "Panther Scout"
# 	mana, attack, health = 2, 2, 2
# 	index = "Shadowverse~Warrior~Minion~2~2~2~~Panther Scout~Fanfare"
# 	requireTarget, keyWord, description = False, "", "Fanfare: Restore 1 Mana. Enhance 8: Gain +3/+3 and restore 7 Mana instead"
#
# 	def effCanTrig(self):
# 		self.effectViable = self.Game.Manas.manas[self.ID] > 7
#
# 	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
# 		if :
# 			PRINT(self.Game, "Panther Scout's Fanfare restores 7 Mana Crystals and gives minion +3/+3")
# 			self.entity.Game.Manas.restoreManaCrystal(7, self.entity.ID)
# 			self.buffDebuff(3, 3)
# 		else:
# 			PRINT(self.Game, "Panther Scout's Fanfare restores 1 Mana Crystal")
# 			self.entity.Game.Manas.restoreManaCrystal(1, self.entity.ID)
# 		return None
#
#
# class RoanWingedNexx(SVMinion):
# 	Class, race, name = "Warrior", "", "Roan Winged Nexx"
# 	mana, attack, health = 4, 3, 4
# 	index = "Shadowverse~Warrior~Minion~4~3~3~~Reclusive Ponderer~Ambush~Accelerate"
# 	requireTarget, keyWord, description = False, "Ambush", "Ambush. Accelerate 1: Draw a card"
#
# class ReclusivePonderer(SVMinion):
# 	Class, race, name = "Warrior", "", "Reclusive Ponderer"
# 	mana, attack, health = 4, 3, 3
# 	index = "Shadowverse~Warrior~Minion~4~3~3~~Reclusive Ponderer~Ambush~Accelerate"
# 	requireTarget, keyWord, description = False, "Ambush", "Ambush. Accelerate 1: Draw a card"
#
#

# """Token"""
#
#
# class SteelcladKnight(SVMinion):
#	 Class, race, name = "Swordcraft", "Officer", "Steelclad Knight"
#	 mana, attack, health = 2, 2, 2
#	 index = "Shadowverse~Swordcraft~Minion~2~2~2~Officer~Steelclad Knight~Uncollectible"
#	 requireTarget, keyWord, description = False, "", ""
#
#
# class HeavyKnight(SVMinion):
#	 Class, race, name = "Swordcraft", "Officer", "Heavy Knight"
#	 mana, attack, health = 1, 1, 2
#	 index = "Shadowverse~Swordcraft~Minion~1~1~2~Officer~Heavy Knight~Uncollectible"
#	 requireTarget, keyWord, description = False, "", ""
#
#
# class Knight(SVMinion):
#	 Class, race, name = "Swordcraft", "Officer", "Knight"
#	 mana, attack, health = 1, 1, 1
#	 index = "Shadowverse~Swordcraft~Minion~1~1~1~Officer~Knight~Uncollectible"
#	 requireTarget, keyWord, description = False, "", ""
#
#
# class ShieldGuardian(SVMinion):
#	 Class, race, name = "Swordcraft", "Officer", "Shield Guardian"
#	 mana, attack, health = 1, 1, 1
#	 index = "Shadowverse~Swordcraft~Minion~1~1~1~Officer~Shield Guardian~Taunt~Uncollectible"
#	 requireTarget, keyWord, description = False, "Taunt", "Ward"
#
#
# class FortressGuard(SVMinion):
#	 Class, race, name = "Swordcraft", "Officer", "Fortress Guard"
#	 mana, attack, health = 3, 2, 3
#	 index = "Shadowverse~Swordcraft~Minion~3~2~3~Officer~Fortress Guard~Taunt~Uncollectible"
#	 requireTarget, keyWord, description = False, "Taunt", "Ward"
#
#
# class GildedBlade(Spell):
#	 Class, school, name = "Swordcraft", "", "Gilded Blade"
#	 requireTarget, mana = True, 1
#	 index = "Shadowverse~Swordcraft~Spell~1~~Gilded Blade~Uncollectible"
#	 description = "Deal 1 damage to an enemy follower."
#
#	 def available(self):
#		 return self.selectableEnemyMinionExists()
#
#	 def targetCorrect(self, target, choice=0):
#		 return target.cardType == "Minion" and target.ID != self.ID and target.onBoard
#
#	 def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
#		 if target is not None:
#			 damage = (1 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
#			 PRINT(self, f"Gilded Blade deals {damage} damage to minion {target.name}")
#			 self.dealsDamage(target, damage)
#		 return target
#
#
# class GildedGoblet(Spell):
#	 Class, school, name = "Swordcraft", "", "Gilded Goblet"
#	 requireTarget, mana = True, 1
#	 index = "Shadowverse~Swordcraft~Spell~1~~Gilded Goblet~Uncollectible"
#	 description = "Restore 2 defense to an ally."
#
#	 def targetCorrect(self, target, choice=0):
#		 return target.ID == self.ID and target.onBoard
#
#	 def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
#		 if target is not None:
#			 heal = 2 * (2 ** self.countHealDouble())
#			 PRINT(self, f"Gilded Goblet restores {heal} Health to {target.name}")
#			 self.restoresHealth(target, heal)
#
#
# class GildedBoots(Spell):
#	 Class, school, name = "Swordcraft", "", "Gilded Boots"
#	 requireTarget, mana = True, 1
#	 index = "Shadowverse~Swordcraft~Spell~1~~Gilded Boots~Uncollectible"
#	 description = "Give Rush to an allied follower."
#
#	 def available(self):
#		 return self.selectableFriendlyExists()
#
#	 def targetCorrect(self, target, choice=0):
#		 return target.cardType == "Minion" and target.ID == self.ID and target.onBoard
#
#	 def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
#		 if target is not None:
#			 PRINT(self, f"Gilded Boots gives minion {target.name} Rush")
#			 target.getsStatus("Rush")
#		 return target
#
#
# class GildedNecklace(Spell):
#	 Class, school, name = "Swordcraft", "", "Gilded Necklace"
#	 requireTarget, mana = True, 1
#	 index = "Shadowverse~Swordcraft~Spell~1~~Gilded Necklace~Uncollectible"
#	 description = "Give +1/+1 to an allied follower."
#
#	 def available(self):
#		 return self.selectableFriendlyExists()
#
#	 def targetCorrect(self, target, choice=0):
#		 return target.cardType == "Minion" and target.ID == self.ID and target.onBoard
#
#	 def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
#		 if target is not None:
#			 PRINT(self, f"Gilded Necklace gives minion {target.name} +1/+1")
#			 target.buffDebuff(1, 1)
#		 return target
#
#
# """1 Cost"""
#
#
# class GrandAcquisition(Spell):
#	 Class, school, name = "Swordcraft", "", "Grand Acquisition"
#	 requireTarget, mana = False, 1
#	 index = "Shadowverse~Swordcraft~Spell~1~~Grand Acquisition"
#	 description = "Choose: Put 1 of the following cards into your hand. -Gilded Blade -Gilded Goblet -Gilded Boots -Gilded Necklace Enhance (6): Put 1 of each into your hand instead and recover 6 play points."
#
#	 def getMana(self):
#		 if self.Game.Manas.manas[self.ID] >= 6:
#			 return 6
#		 else:
#			 return self.mana
#
#	 def effCanTrig(self):
#		 self.effectViable = self.getMana() != self.mana
#
#	 def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
#		 if choice == 6:
#			 PRINT(self, "Grand Acquisition is cast")
#			 if self.Game.Hand_Deck.handNotFull(self.ID):
#				 self.Game.Hand_Deck.addCardtoHand(GildedBlade(self.Game, self.ID), self.ID, creator=type(self))
#			 if self.Game.Hand_Deck.handNotFull(self.ID):
#				 self.Game.Hand_Deck.addCardtoHand(GildedGoblet(self.Game, self.ID), self.ID, creator=type(self))
#			 if self.Game.Hand_Deck.handNotFull(self.ID):
#				 self.Game.Hand_Deck.addCardtoHand(GildedBoots(self.Game, self.ID), self.ID, creator=type(self))
#			 if self.Game.Hand_Deck.handNotFull(self.ID):
#				 self.Game.Hand_Deck.addCardtoHand(GildedNecklace(self.Game, self.ID), self.ID, creator=type(self))
#			 self.Game.Manas.manas[self.ID] += 6
#			 PRINT(self, "Grand Acquisition restore 6 manas.")
#		 elif self.ID == self.Game.turn and self.Game.Hand_Deck.handNotFull(self.ID):
#			 PRINT(self, "Grand Acquisition lets player choose a Spell to get:")
#			 self.Game.options = [GildedBlade(self.Game, self.ID), GildedGoblet(self.Game, self.ID),
#								  GildedBoots(self.Game, self.ID), GildedNecklace(self.Game, self.ID)]
#			 self.Game.DiscoverHandler.startDiscover(self)
#		 return None
#
#	 def discoverDecided(self, option):
#		 self.Game.Hand_Deck.addCardtoHand(option, self.ID, creator=type(self))
#		 return None
#
#
# class Quickblader(SVMinion):
#	 Class, race, name = "Swordcraft", "Officer", "Quickblader"
#	 mana, attack, health = 1, 1, 1
#	 index = "Shadowverse~Swordcraft~Minion~1~1~1~Officer~Quickblader~Charge"
#	 requireTarget, keyWord, description = False, "Charge", "Storm"
#
#
# class Kagemitsu(SVMinion):
#	 Class, race, name = "Swordcraft", "Officer", "Kagemitsu, Matchless Blade"
#	 mana, attack, health = 1, 0, 1
#	 index = "Shadowverse~Swordcraft~Minion~1~0~1~Officer~Kagemitsu, Matchless Blade~Battlecry~Deathrattle"
#	 requireTarget, keyWord, description = False, "", "Fanfare: Enhance (3) - Gain +2/+0 and Rush.Last Words: If it is your turn, give your leader the following effect - At the start of your turn, summon a Kagemitsu, Matchless Blade, evolve it, then remove this effect."
#
#	 attackAdd, healthAdd = 1, 0
#
#	 def __init__(self, Game, ID):
#		 super().__init__(Game, ID)
#		 if self.status["Evolved"] < 1:
#			 self.deathrattles = [DeathrattleKagemitsu(self)]
#
#	 def inEvolving(self):
#		 for d in self.deathrattles:
#			 if type(d) == DeathrattleKagemitsu:
#				 d.disconnect()
#				 self.deathrattles.remove(d)
#		 trigger = TriggerKagemitsu(self)
#		 self.trigsBoard.append(trigger)
#		 if self.onBoard:
#			 trigger.connect()
#
#	 def effCanTrig(self):
#		 self.effectViable = self.getMana() != self.mana
#
#	 def getMana(self):
#		 if self.Game.Manas.manas[self.ID] >= 3:
#			 return 3
#		 else:
#			 return self.mana
#
#	 def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
#		 if choice == 3:
#			 PRINT(self, "Levin Beastmaster's Fanfare give it +2/+0 and Rush.")
#			 self.getsStatus("Rush")
#			 self.buffDebuff(2, 0)
#		 return None
#
#
# class TriggerKagemitsu(TriggeronBoard):
#	 def __init__(self, entity):
#		 super().__init__(entity, ["MinionAttackingHero", "MinionAttackingMinion"])
#
#	 def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
#		 return self.entity.onBoard and subject == self.entity
#
#	 def effect(self, signal, ID, subject, target, number, comment, choice=0):
#		 evolved = self.entity.Game.Counters.numMinionsEvolvedThisGame[ID]
#		 PRINT(self, f"Minion {self.entity.name} attacks and get +{evolved}/+{evolved}")
#		 self.entity.buffDebuff(evolved, evolved)
#
#
# class DeathrattleKagemitsu(Deathrattle_Minion):
#	 def effect(self, signal, ID, subject, target, number, comment, choice=0):
#		 if ID == self.entity.ID:
#			 PRINT(self,
#				   "Last Words: If it is your turn, give your leader the following effect - At the start of your turn, summon a Kagemitsu, Matchless Blade, evolve it, then remove this effect.")
#			 trigger = TriggerSummonAEvolvedKagemitsuNextTurn(self.entity.Game.heroes[self.entity.ID])
#			 self.entity.Game.heroes[self.entity.ID].trigsBoard.append(trigger)
#			 trigger.connect()
#
#
# class TriggerSummonAEvolvedKagemitsuNextTurn(TriggeronBoard):
#	 def __init__(self, entity):
#		 super().__init__(entity, ["TurnStarts"])
#
#	 def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
#		 return self.entity.onBoard and ID == self.entity.ID
#
#	 def effect(self, signal, ID, subject, target, number, comment, choice=0):
#		 kag = Kagemitsu(self.entity.Game, ID)
#		 self.entity.Game.summonMinion([kag], (-11, "totheRightEnd"), ID)
#		 kag.evolve()
#		 for t in self.entity.Game.heroes[ID].trigsBoard:
#			 if type(t) == TriggerSummonAEvolvedKagemitsuNextTurn:
#				 t.disconnect()
#				 self.entity.Game.heroes[ID].trigsBoard.remove(t)
#				 break
#
#
# class ErnestaWeaponsHawker(SVMinion):
#	 Class, race, name = "Swordcraft", "Officer", "Ernesta, Weapons Hawker"
#	 mana, attack, health = 1, 1, 1
#	 index = "Shadowverse~Swordcraft~Minion~1~1~1~Officer~Ernesta, Weapons Hawker~Battlecry"
#	 requireTarget, keyWord, description = False, "", "Fanfare: Rally (10) - Put a Dread Hound into your hand."
#
#	 def effCanTrig(self):
#		 self.effectViable = self.Game.Counters.numMinionsSummonThisGame[self.ID] >= 10
#
#	 def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
#		 if self.Game.Counters.numMinionsSummonThisGame[self.ID] >= 10:
#			 if self.Game.Hand_Deck.handNotFull(self.ID):
#				 self.Game.Hand_Deck.addCardtoHand(DreadHound(self.Game, self.ID), self.ID, creator=type(self))
#		 return None
#
#
# class DreadHound(SVMinion):
#	 Class, race, name = "Swordcraft", "Officer", "Dread Hound"
#	 mana, attack, health = 1, 4, 4
#	 index = "Shadowverse~Swordcraft~Minion~1~4~4~Officer~Dread Hound~Battlecry~Poisonous~Taunt~Uncollectable"
#	 requireTarget, keyWord, description = False, "Poisonous,Taunt", "Bane.Ward.Fanfare: Give a random allied Ernesta, Weapons Hawker Last Words - Deal 4 damage to a random enemy follower."
#
#	 def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
#		 ts = self.Game.minionsAlive(self.ID)
#		 targets = []
#		 for t in ts:
#			 if t.name == "Ernesta, Weapons Hawker":
#				 targets.append(t)
#		 if targets:
#			 target = np.random.choice(targets)
#			 PRINT(self,
#				   f"Dread Hound's Fanfare gives {target.name} Last Words - Deal 4 damage to a random enemy follower.")
#			 deathrattle = DeathrattleErnestaWeaponsHawker(target)
#			 target.deathrattles.append(deathrattle)
#			 if target.onBoard:
#				 deathrattle.connect()
#		 return None
#
#
# class DeathrattleErnestaWeaponsHawker(Deathrattle_Minion):
#	 def effect(self, signal, ID, subject, target, number, comment, choice=0):
#		 PRINT(self, "Last Words: Deal 4 damage to a random enemy follower.")
#		 targets = self.entity.Game.minionsAlive(3 - self.entity.entity.ID)
#		 if targets != []:
#			 target = np.random.choice(targets)
#			 PRINT(self, f"Ernesta, Weapons Hawker's Last Words deals 4 damage to minion {target.name}")
#			 self.entity.dealsDamage(target, 4)
#
#
# class DecisiveStrike(Spell):
#	 Class, school, name = "Swordcraft", "", "Decisive Strike"
#	 requireTarget, mana = True, 1
#	 index = "Shadowverse~Swordcraft~Spell~1~~Decisive Strike"
#	 description = "Deal X damage to an enemy follower. X equals the attack of the highest-attack Commander follower in your hand.Enhance (5): Deal X damage to all enemy followers instead."
#
#	 def getMana(self):
#		 if self.Game.Manas.manas[self.ID] >= 5:
#			 return 5
#		 else:
#			 return self.mana
#
#	 def effCanTrig(self):
#		 self.effectViable = self.getMana() != self.mana
#
#	 def returnTrue(self, choice=0):
#		 if self.getMana() == 5:
#			 return False
#		 return True
#
#	 def targetCorrect(self, target, choice=0):
#		 return target.cardType == "Minion" and target.ID != self.ID and target.onBoard
#
#	 def available(self):
#		 if self.getMana() == 5:
#			 return True
#		 return self.selectableEnemyMinionExists()
#
#	 def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
#		 damage = 0
#		 for card in self.Game.Hand_Deck.hands[self.ID]:
#			 if card.cardType == "Minion" and "Commander" in card.race and card.attack > damage:
#				 damage = card.attack
#		 damage = (damage + self.countSpellDamage()) * (2 ** self.countDamageDouble())
#		 if choice == 5:
#			 targets = self.Game.minionsonBoard(3 - self.ID)
#			 self.dealsAOE(targets, [damage for minion in targets])
#		 elif self.ID == self.Game.turn:
#			 PRINT(self, f"Decisive Strike deals {damage} damage to minion {target.name}")
#			 self.dealsDamage(target, damage)
#		 return None
#
#
# class PompousSummons(Spell):
#	 Class, school, name = "Swordcraft", "", "Pompous Summons"
#	 requireTarget, mana = False, 1
#	 index = "Shadowverse~Swordcraft~Spell~1~~Pompous Summons"
#	 description = "Put a random Swordcraft follower from your deck into your hand.Rally (10): Put 2 random Swordcraft followers into your hand instead."
#
#	 def effCanTrig(self):
#		 self.effectViable = self.Game.Counters.numMinionsSummonThisGame[self.ID] >= 10
#
#	 def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
#		 minions = []
#		 for card in self.Game.Hand_Deck.decks[self.ID]:
#			 if card.cardType == "Minion" and card.Class == "Swordcraft":
#				 minions.append(card)
#		 if minions:
#			 card = np.random.choice(minions)
#			 self.Game.Hand_Deck.drawCard(self.ID, card)
#			 PRINT(self, f"Pompous Summons let you draw {card.name}.")
#		 if self.Game.Counters.numMinionsSummonThisGame[self.ID] >= 10:
#			 minions = []
#			 for card in self.Game.Hand_Deck.decks[self.ID]:
#				 if card.cardType == "Minion" and card.Class == "Swordcraft":
#					 minions.append(card)
#			 if minions:
#				 card = np.random.choice(minions)
#				 self.Game.Hand_Deck.drawCard(self.ID, card)
#				 PRINT(self, f"Pompous Summons let you draw {card.name}.")
#		 return None
#
#
# class LevinJustice(Spell):
#	 Class, school, name = "Swordcraft", "", "Levin Justice"
#	 requireTarget, mana = True, 1
#	 index = "Shadowverse~Swordcraft~Spell~1~~Levin Justice"
#	 description = "Put a Yurius, Levin Duke into your hand. Then deal X damage to an enemy follower. X equals the number of Levin cards in your hand."
#
#	 def available(self):
#		 return self.selectableEnemyMinionExists()
#
#	 def targetCorrect(self, target, choice=0):
#		 return target.cardType == "Minion" and target.ID != self.ID and target.onBoard
#
#	 def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
#		 if target:
#			 damage = 0
#			 for card in self.Game.Hand_Deck.hands[self.ID]:
#				 if card.cardType == "Minion" and "Levin" in card.race:
#					 damage += 1
#			 damage = (damage + self.countSpellDamage()) * (2 ** self.countDamageDouble())
#			 PRINT(self, f"Levin Justice deals {damage} damage to minion {target.name}")
#			 self.dealsDamage(target, damage)
#		 if self.Game.Hand_Deck.handNotFull(self.ID):
#			 PRINT(self, "Levin Justice add a Yurius, Levin Duke to your hand.")
#			 self.Game.Hand_Deck.addCardtoHand(YuriusLevinDuke, self.ID, byType=True, creator=type(self))
#		 return target
#
#
# class YuriusLevinDuke(SVMinion):
#	 Class, race, name = "Bloodcraft", "Levin", "Yurius, Levin Duke"
#	 mana, attack, health = 2, 1, 3
#	 index = "Shadowverse~Bloodcraft~Minion~2~1~3~Levin~Yurius, Levin Duke"
#	 requireTarget, keyWord, description = False, "", "Whenever an enemy follower comes into play, deal 1 damage to the enemy leader."
#
#	 def __init__(self, Game, ID):
#		 super().__init__(Game, ID)
#		 self.trigsBoard = [TriggerYuriusLevinDuke(self)]
#
#
# class TriggerYuriusLevinDuke(TriggeronBoard):
#	 def __init__(self, entity):
#		 super().__init__(entity, ["MinionSummoned"])
#
#	 def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
#		 return self.entity.onBoard and subject.ID != self.entity.ID and subject != self.entity
#
#	 def effect(self, signal, ID, subject, target, number, comment, choice=0):
#		 PRINT(self, f"A enemy minion {subject.name} is summoned and {self.entity.name} deals 1 damage to enemy leader.")
#		 self.entity.dealsDamage(self.entity.Game.heroes[3 - self.entity.ID], 1)
#
#
# class MeetTheLevinSisters(Spell):
#	 Class, school, name = "Swordcraft", "", "Meet the Levin Sisters!"
#	 requireTarget, mana = False, 1
#	 index = "Shadowverse~Swordcraft~Spell~1~~Meet the Levin Sisters!"
#	 description = "Choose: Put 1 of the following cards into your hand.-Mina, Levin Vice Leader-Mona, Levin Mage-Mena, Levin DuelistEnhance (7): Put 1 of each into your hand instead, and recover 6 play points."
#
#	 def effCanTrig(self):
#		 self.effectViable = self.getMana() != self.mana
#
#	 def getMana(self):
#		 if self.Game.Manas.manas[self.ID] >= 7:
#			 return 7
#		 else:
#			 return self.mana
#
#	 def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
#		 if choice == 7:
#			 PRINT(self, "Meet the Levin Sisters! is cast")
#			 if self.Game.Hand_Deck.handNotFull(self.ID):
#				 self.Game.Hand_Deck.addCardtoHand(MinaLevinViceLeader(self.Game, self.ID), self.ID, creator=type(self))
#			 if self.Game.Hand_Deck.handNotFull(self.ID):
#				 self.Game.Hand_Deck.addCardtoHand(MonaLevinMage(self.Game, self.ID), self.ID, creator=type(self))
#			 if self.Game.Hand_Deck.handNotFull(self.ID):
#				 self.Game.Hand_Deck.addCardtoHand(MenaLevinDuelist(self.Game, self.ID), self.ID, creator=type(self))
#			 self.Game.Manas.manas[self.ID] += 6
#			 PRINT(self, "Meet the Levin Sisters! restore 6 manas.")
#		 elif self.ID == self.Game.turn and self.Game.Hand_Deck.handNotFull(self.ID):
#			 PRINT(self, "Meet the Levin Sisters! lets player choose a Spell to get:")
#			 self.Game.options = [MinaLevinViceLeader(self.Game, self.ID), MonaLevinMage(self.Game, self.ID),
#								  MenaLevinDuelist(self.Game, self.ID)]
#			 self.Game.DiscoverHandler.startDiscover(self)
#		 return None
#
#	 def discoverDecided(self, option):
#		 self.Game.Hand_Deck.addCardtoHand(option, self.ID, creator=type(self))
#		 return None
#
#
# class MinaLevinViceLeader(SVMinion):
#	 Class, race, name = "Swordcraft", "Levin", "Mina, Levin Vice Leader"
#	 mana, attack, health = 2, 2, 2
#	 index = "Shadowverse~Swordcraft~Minion~2~2~2~Levin~Mina, Levin Vice Leader~Battlecry~Uncollectable"
#	 requireTarget, keyWord, description = False, "", "Fanfare: Put a random Levin follower from your deck into your hand."
#
#	 def effect(self, signal, ID, subject, target, number, comment, choice=0):
#		 levins = []
#		 for card in self.Game.Hand_Deck.decks[self.ID]:
#			 if card.cardType == "Minion" and "Commander" in card.race:
#				 levins.append(card)
#		 if levins:
#			 card = np.random.choice(levins)
#			 self.Game.Hand_Deck.drawCard(self.ID, card)
#			 PRINT(self, f"Mina, Levin Vice Leader's Fanfare let you draw {card.name}.")
#
#
# class MonaLevinMage(SVMinion):
#	 Class, race, name = "Swordcraft", "Levin", "Mona, Levin Mage"
#	 mana, attack, health = 4, 3, 3
#	 index = "Shadowverse~Swordcraft~Minion~4~3~3~Levin~Mona, Levin Mage~Battlecry~Uncollectable"
#	 requireTarget, keyWord, description = False, "", "Fanfare: Recover 2 play points. If another allied Levin card is in play, recover 3 instead."
#
#	 def effCanTrig(self):
#		 controlLevin = False
#		 for minion in self.Game.minionsonBoard(self.ID):
#			 if "Levin" in minion.race:
#				 controlLevin = True
#				 break
#		 self.effectViable = controlLevin
#
#	 def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
#		 controlLevin = False
#		 for minion in self.Game.minionsonBoard(self.ID):
#			 if "Levin" in minion.race:
#				 controlLevin = True
#				 break
#		 n = 2
#		 if controlLevin:
#			 n = 3
#		 self.Game.Manas.manas[self.ID] += n
#		 PRINT(self, f"Mona, Levin Mage's Fanfare let you restore {n} mana.")
#
#
# class MenaLevinDuelist(SVMinion):
#	 Class, race, name = "Swordcraft", "Levin", "Mena, Levin Duelist"
#	 mana, attack, health = 3, 3, 2
#	 index = "Shadowverse~Swordcraft~Minion~3~3~2~Levin~Mena, Levin Duelist~Battlecry~Rush~Uncollectable"
#	 requireTarget, keyWord, description = False, "Rush", "Rush.Fanfare: If another allied Levin card is in play, gain +1/+1."
#
#	 def effCanTrig(self):
#		 controlLevin = False
#		 for minion in self.Game.minionsonBoard(self.ID):
#			 if "Levin" in minion.race:
#				 controlLevin = True
#				 break
#		 self.effectViable = controlLevin
#
#	 def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
#		 controlLevin = False
#		 for minion in self.Game.minionsonBoard(self.ID):
#			 if "Levin" in minion.race:
#				 controlLevin = True
#				 break
#		 if controlLevin:
#			 self.buffDebuff(1, 1)
#			 PRINT(self, f"Mena, Levin Duelist's Fanfare give itself +1/+1.")
#
#
# class LounesLevinApprentice(SVMinion):
#	 Class, race, name = "Swordcraft", "Levin", "Lounes, Levin Apprentice"
#	 mana, attack, health = 1, 1, 1
#	 index = "Shadowverse~Swordcraft~Minion~1~1~1~Levin~Lounes, Levin Apprentice~Battlecry"
#	 requireTarget, keyWord, description = False, "", "Fanfare: Gain +0/+1 for each Levin card in your hand.Enhance (3): Can attack 2 times per turn."
#
#	 def effCanTrig(self):
#		 self.effectViable = self.getMana() != self.mana
#
#	 def getMana(self):
#		 if self.Game.Manas.manas[self.ID] >= 3:
#			 return 3
#		 else:
#			 return self.mana
#
#	 def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
#		 levins = 0
#		 for card in self.Game.Hand_Deck.hands[self.ID]:
#			 if card.cardType == "Minion" and "Levin" in card.race:
#				 levins += 1
#		 if levins > 0:
#			 self.buffDebuff(0, levins)
#			 PRINT(self, f"Lounes, Levin Apprentice's Fanfare give itself +1/+{levins}.")
#		 if choice == 3:
#			 self.getsStatus("Windfury")
#			 PRINT(self, f"Lounes, Levin Apprentice's Fanfare give itself Can attack 2 times per turn.")
#
#
# """2 Cost"""
#
#
# class OathlessKnight(SVMinion):
#	 Class, race, name = "Swordcraft", "Officer", "Oathless Knight"
#	 mana, attack, health = 2, 1, 1
#	 index = "Shadowverse~Swordcraft~Minion~2~1~1~Officer~Oathless Knight~Battlecry"
#	 requireTarget, keyWord, description = False, "", "Fanfare: Summon a Knight."
#
#	 def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
#		 PRINT(self, "Oathless Knight's Fanfare summons a 1/1 Knight.")
#		 self.Game.summonMinion([Knight(self.Game, self.ID)], (-11, "totheRightEnd"), self.ID)
#		 return None
#
#
# class PantherScout(SVMinion):
#	 Class, race, name = "Swordcraft", "Officer,Natura", "Panther Scout"
#	 mana, attack, health = 2, 2, 2
#	 index = "Shadowverse~Swordcraft~Minion~2~2~2~Officer,Natura~Panther Scout~Battlecry"
#	 requireTarget, keyWord, description = False, "", "Fanfare: Recover 1 play point.Enhance (8): Gain +3/+3 and recover 7 play points instead."
#
#	 def effCanTrig(self):
#		 self.effectViable = self.getMana() != self.mana
#
#	 def getMana(self):
#		 if self.Game.Manas.manas[self.ID] >= 8:
#			 return 8
#		 else:
#			 return self.mana
#
#	 def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
#		 r = 1
#		 if choice == 8:
#			 r = 7
#			 self.buffDebuff(3, 3)
#			 PRINT(self, f"Panther Scout's Fanfare gives itself +3/+3.")
#		 PRINT(self, f"Panther Scout's Fanfare restores {r} PP.")
#		 self.Game.Manas.manas[self.ID] += r
#		 return None
#
#
# class HonorableThief(SVMinion):
#	 Class, race, name = "Swordcraft", "Officer", "Honorable Thief"
#	 mana, attack, health = 2, 2, 2
#	 index = "Shadowverse~Swordcraft~Minion~2~2~2~Officer~Honorable Thief~Battlecry~Deathrattle"
#	 requireTarget, keyWord, description = False, "", "Fanfare: Rally (7) - Evolve this follower. Last Words: Put a Gilded Boots into your hand."
#
#	 def __init__(self, Game, ID):
#		 super().__init__(Game, ID)
#		 self.deathrattles = [DeathrattleHonorableThief(self)]
#
#	 def effCanTrig(self):
#		 self.effectViable = self.Game.Counters.numMinionsSummonThisGame[self.ID] >= 7
#
#	 def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
#		 if self.Game.Counters.numMinionsSummonThisGame[self.ID] >= 7:
#			 self.evolve()
#		 return None
#
#
# class DeathrattleHonorableThief(Deathrattle_Minion):
#	 def effect(self, signal, ID, subject, target, number, comment, choice=0):
#		 if self.entity.Game.Hand_Deck.handNotFull(self.entity.ID):
#			 PRINT(self, "Last Words: Add a 'GildedBoots' to your hand triggers.")
#			 self.entity.Game.Hand_Deck.addCardtoHand(GildedBoots, self.entity.ID, byType=True, creator=type(self.entity))
#
#
# class WhiteTiger(SVMinion):
#	 Class, race, name = "Havencraft", "", "White Tiger"
#	 mana, attack, health = 3, 3, 2
#	 index = "Shadowverse~Havencraft~Minion~3~3~2~~White Tiger~Taunt"
#	 requireTarget, keyWord, description = False, "Taunt", "Ward Can't be targeted by enemy spells and effects."
#
#	 def __init__(self, Game, ID):
#		 super().__init__(Game, ID)
#		 self.marks["Enemy Effect Evasive"] = 1
#
#
# class LevinWhiteTiger(WhiteTiger):
#	 race = "Levin"
#	 index = "Shadowverse~Havencraft~Minion~3~3~2~Levin~White Tiger~Taunt~Uncollectible"
#
#
# class LevinBeastmaster(SVMinion):
#	 Class, race, name = "Swordcraft", "Levin", "Levin Beastmaster"
#	 mana, attack, health = 2, 2, 2
#	 index = "Shadowverse~Swordcraft~Minion~2~2~2~Levin~Levin Beastmaster~Battlecry"
#	 requireTarget, keyWord, description = False, "", "Fanfare: Enhance (6) - Summon 2 White Tigers and change them into Levin followers."
#
#	 def effCanTrig(self):
#		 self.effectViable = self.getMana() != self.mana
#
#	 def getMana(self):
#		 if self.Game.Manas.manas[self.ID] >= 6:
#			 return 6
#		 else:
#			 return self.mana
#
#	 def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
#		 if choice == 6:
#			 PRINT(self,
#				   "Levin Beastmaster's Fanfare summons two 1/1 White Tigers and change them into Levin followers.")
#			 self.Game.summonMinion([LevinWhiteTiger(self.Game, self.ID) for i in range(2)], (-11, "totheRightEnd"),
#									self.ID)
#		 return None
#
#	 def inEvolving(self):
#		 PRINT(self, "Levin Beastmaster evolves and summons a 1/1 White Tiger and change it into Levin followers.")
#		 self.Game.summonMinion([LevinWhiteTiger(self.Game, self.ID)], (-11, "totheRightEnd"), self.ID)
#
#
# class EleganceInAction(Spell):
#	 Class, school, name = "Swordcraft", "", "Elegance in Action"
#	 requireTarget, mana = False, 2
#	 index = "Shadowverse~Swordcraft~Spell~2~~Elegance in Action"
#	 description = "Draw a card. Summon a Heavy Knight for each follower drawn. Deal 3 damage to a random enemy follower for each non-follower drawn.Enhance (5): Draw 3 cards instead."
#
#	 def effCanTrig(self):
#		 self.effectViable = self.getMana() != self.mana
#
#	 def getMana(self):
#		 if self.Game.Manas.manas[self.ID] >= 5:
#			 return 5
#		 else:
#			 return self.mana
#
#	 def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
#		 draw = 1
#		 if choice == 5:
#			 draw = 3
#		 for i in range(draw):
#			 card, mana = self.Game.Hand_Deck.drawCard(self.ID)
#			 if card:
#				 if card.cardType == "Minion":
#					 self.Game.summonMinion([HeavyKnight(self.Game, self.ID)], (-11, "totheRightEnd"), self.ID)
#				 else:
#					 damage = (3 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
#					 targets = self.Game.minionsAlive(3 - self.ID)
#					 if targets != []:
#						 target = np.random.choice(targets)
#						 PRINT(self, f"Elegance in Action deals {damage} damage to minion {target.name}")
#						 self.dealsDamage(target, damage)
#		 return None
#
#
# class ShieldPhalanx(Spell):
#	 Class, school, name = "Swordcraft", "", "Shield Phalanx"
#	 requireTarget, mana = False, 2
#	 index = "Shadowverse~Swordcraft~Spell~2~~Shield Phalanx"
#	 description = "Summon a Shield Guardian and Knight.Rally (15): Summon a Frontguard General instead of a Shield Guardian."
#
#	 def available(self):
#		 return self.Game.space(self.ID)
#
#	 def effCanTrig(self):
#		 self.effectViable = self.Game.Counters.numMinionsSummonThisGame[self.ID] >= 15
#
#	 def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
#		 if self.Game.Counters.numMinionsSummonThisGame[self.ID] >= 15:
#			 PRINT(self, "Shield Phalanx summons a Frontguard General and Knight.")
#			 self.Game.summonMinion([FrontguardGeneral(self.Game, self.ID), Knight(self.Game, self.ID)],
#									(-11, "totheRightEnd"), self.ID)
#		 else:
#			 PRINT(self, "Shield Phalanx summons a Shield Guardian and Knight.")
#			 self.Game.summonMinion([ShieldGuardian(self.Game, self.ID), Knight(self.Game, self.ID)],
#									(-11, "totheRightEnd"), self.ID)
#		 return None
#
#
# class MirrorsImage(Spell):
#	 Class, school, name = "Swordcraft", "", "Mirror Image"
#	 requireTarget, mana = True, 2
#	 index = "Shadowverse~Swordcraft~Spell~2~~Mirror Image"
#	 description = "Choose an allied follower in play and summon a copy of it. Give it Rush, and banish it at the start of your next turn."
#
#	 def available(self):
#		 return self.selectableFriendlyExists() and self.Game.space(self.ID)
#
#	 def targetCorrect(self, target, choice=0):
#		 return target.cardType == "Minion" and target.ID == self.ID and target.onBoard
#
#	 def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
#		 if target is not None:
#			 m = type(target)(self.Game, self.ID)
#			 PRINT(self, f"Mirror Image summon a copy of {target.name} and give it Rush.")
#			 self.Game.summonMinion([m], (-11, "totheRightEnd"), self.ID)
#			 m.getsStatus("Rush")
#			 trigger = TriggerMirrorsImage(m, self.ID)
#			 m.trigsBoard.append(trigger)
#			 if m.onBoard:
#				 trigger.connect()
#		 return target
#
#
# class TriggerMirrorsImage(TriggeronBoard):
#	 def __init__(self, entity, ID):
#		 super().__init__(entity, ["TurnStarts"])
#		 self.temp = True
#		 self.ID = ID
#
#	 def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
#		 return self.entity.onBoard and ID == self.ID
#
#	 def effect(self, signal, ID, subject, target, number, comment, choice=0):
#		 PRINT(self, f"At the start of player {self.ID}'s turn,  minion {self.entity.name} disappears.")
#		 self.entity.disappears(keepDeathrattlesRegistered=False)
#		 self.entity.Game.removeMinionorWeapon(self.entity)
#		 self.disconnect()
#		 extractfrom(self, self.entity.trigsBoard)
#
#	 def selfCopy(self, recipient):
#		 trigger = type(self)(recipient, self.ID)
#		 return trigger
#
#
# class SteadfastSamurai(SVMinion):
#	 Class, race, name = "Swordcraft", "Officer", "Steadfast Samurai"
#	 mana, attack, health = 2, 1, 1
#	 index = "Shadowverse~Swordcraft~Minion~2~1~1~Officer~Steadfast Samurai"
#	 requireTarget, keyWord, description = False, "", "Fanfare: Enhance (5) - Evolve this follower.Clash: Reduce damage to this follower to 0 until the end of the turn."
#
#	 def __init__(self, Game, ID):
#		 super().__init__(Game, ID)
#		 self.trigsBoard = [TriggerClashSteadfastSamurai(self)]
#
#	 def effCanTrig(self):
#		 self.effectViable = self.getMana() != self.mana
#
#	 def getMana(self):
#		 if self.Game.Manas.manas[self.ID] >= 5:
#			 return 5
#		 else:
#			 return self.mana
#
#	 def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
#		 if choice == 5:
#			 self.evolve()
#		 return None
#
#	 def inEvolving(self):
#		 self.getsStatus("Charge")
#		 self.auras["Buff Aura"] = BuffAuraEvolvedSteadfastSamurai(self)
#		 self.auras["Buff Aura"].auraAppears()
#
#
# class TriggerClashSteadfastSamurai(TriggeronBoard):
#	 def __init__(self, entity):
#		 super().__init__(entity, ["MinionAttackingMinion"])
#
#	 def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
#		 return self.entity.onBoard and (target == self.entity or subject == self.entity)
#
#	 def effect(self, signal, ID, subject, target, number, comment, choice=0):
#		 self.entity.marks["Damage Immune"] += 1
#		 trigger = TriggerTurnEndSteadfastSamurai(self.entity)
#		 self.entity.trigsBoard.append(trigger)
#		 if self.entity.onBoard:
#			 trigger.connect()
#
#
# class TriggerTurnEndSteadfastSamurai(TriggeronBoard):
#	 def __init__(self, entity):
#		 super().__init__(entity, ["TurnEnds"])
#
#	 def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
#		 return self.entity.onBoard
#
#	 def effect(self, signal, ID, subject, target, number, comment, choice=0):
#		 self.entity.marks["Damage Immune"] -= 1
#		 for t in self.entity.trigsBoard:
#			 if type(t) == TriggerTurnEndSteadfastSamurai:
#				 t.disconnect()
#				 self.entity.trigsBoard.remove(t)
#				 break
#
#
# class BuffAuraEvolvedSteadfastSamurai(AuraDealer_toMinion):
#	 def __init__(self, entity):
#		 self.entity = entity
#		 self.signals, self.auraAffected = [], []
#
#	 # Minions appearing/disappearing will let the minion reevaluate the aura.
#	 def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
#		 return self.entity.onBoard
#
#	 def effect(self, signal, ID, subject, target, number, comment, choice=0):
#		 self.applies(self.entity.Game.heroes[self.entity.ID])
#
#	 def applies(self, subject):
#		 subject.marks["Enemy Effect Damage Immune"] += 1
#
#	 def auraAppears(self):
#		 self.applies(self.entity.Game.heroes[self.entity.ID])
#
#	 def auraDisappears(self):
#		 self.entity.Game.heroes[self.entity.ID].marks["Enemy Effect Damage Immune"] -= 1
#
#	 def selfCopy(self, recipientMinion):  # The recipientMinion is the minion that deals the Aura.
#		 return type(self)(recipientMinion)
#
#
# class TwinswordMaster(SVMinion):
#	 Class, race, name = "Swordcraft", "Officer", "Twinsword Master"
#	 mana, attack, health = 2, 2, 2
#	 index = "Shadowverse~Swordcraft~Minion~2~2~2~Officer~Twinsword Master~Battlecry"
#	 requireTarget, keyWord, description = False, "", "Fanfare: If an allied Commander card is in play, gain the ability to evolve for 0 evolution points."
#
#	 attackAdd, healthAdd = 1, 1
#
#	 def effCanTrig(self):
#		 self.effectViable = False
#		 for minion in self.Game.minionsonBoard(self.ID):
#			 if "Commander" in minion.race:
#				 self.effectViable = True
#				 break
#
#	 def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
#		 controlOfficer = False
#		 for minion in self.Game.minionsonBoard(self.ID):
#			 if "Commander" in minion.race:
#				 controlOfficer = True
#				 break
#		 if controlOfficer:
#			 self.getsStatus("Free Evolve")
#		 return None
#
#	 def inEvolving(self):
#		 self.getsStatus("Windfury")
#
#
# class ValseChampionDeadeye(SVMinion):
#	 Class, race, name = "Swordcraft", "Officer", "Valse, Champion Deadeye"
#	 mana, attack, health = 2, 2, 2
#	 index = "Shadowverse~Swordcraft~Minion~2~2~2~Officer~Valse, Champion Deadeye~Battlecry"
#	 requireTarget, keyWord, description = True, "", "Fanfare: Enhance (6) - Banish an enemy follower or amulet."
#	 evolveRequireTarget = True
#
#	 def effCanTrig(self):
#		 self.effectViable = self.getMana() != self.mana
#
#	 def getMana(self):
#		 if self.Game.Manas.manas[self.ID] >= 6:
#			 return 6
#		 else:
#			 return self.mana
#
#	 def targetExists(self, choice=0):
#		 return choice == 6 and self.selectableEnemyMinionExists(choice)
#
#	 def targetCorrect(self, target, choice=0):
#		 return choice == 6 and target.cardType == "Minion" and target.ID != self.ID and target.onBoard
#
#	 def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
#		 if choice == 6:
#			 target.disappears(keepDeathrattlesRegistered=False)
#			 target.Game.removeMinionorWeapon(target)
#			 PRINT(self, f"Valse, Champion Deadeye let {target.name} disappears.")
#		 return None
#
#	 def inHandEvolving(self, target=None):
#		 if target:
#			 target.dead = True
#			 PRINT(self, f"Valse, Champion Deadeye destroys {target.name}.")
#		 return
#
#	 def extraTargetCorrect(self, target, affair):
#		 return target.cardType and target.cardType == "Minion" and target.ID != self.ID and target.onBoard and target.health <= 3
#
#
# class LevinArcher(SVMinion):
#	 Class, race, name = "Swordcraft", "Levin", "Levin Archer"
#	 mana, attack, health = 2, 2, 2
#	 index = "Shadowverse~Swordcraft~Minion~2~2~2~Levin~Levin Archer"
#	 requireTarget, keyWord, description = False, "", ""
#	 evolveRequireTarget = True
#
#	 def inHandEvolving(self, target=None):
#		 if target:
#			 PRINT(self, f"Levin Archer deals 3 damage to minion {target.name}")
#			 self.dealsDamage(target, 3)
#		 return
#
#	 def extraTargetCorrect(self, target, affair):
#		 if target.cardType and target.cardType == "Minion" and target.ID != self.ID and target.onBoard:
#			 for card in self.Game.Hand_Deck.hands[self.ID]:
#				 if card.cardType == "Minion" and "Levin" in card.race:
#					 return True
#		 return False
#
#
# class JenoLevinStalwart(SVMinion):
#	 Class, race, name = "Swordcraft", "Levin", "Jeno, Levin Stalwart"
#	 mana, attack, health = 2, 2, 2
#	 index = "Shadowverse~Swordcraft~Minion~2~2~2~Levin~Jeno, Levin Stalwart"
#	 requireTarget, keyWord, description = False, "", "Can evolve an allied Levin follower (excluding Jeno, Levin Stalwart) each turn for 0 evolution points until this follower leaves play."
#
#	 def __init__(self, Game, ID):
#		 super().__init__(Game, ID)
#		 self.auras["Has Aura"] = EffectAura(self, "Free Evolve")
#
#	 def applicable(self, target):
#		 return target.cardType == "Minion" and "Levin" in target.race
#
#
# """3 Cost"""
#
#
# class GabrielHeavenlyVoice(SVMinion):
#	 Class, race, name = "Neutral", "", "Gabriel, Heavenly Voice"
#	 mana, attack, health = 3, 2, 3
#	 index = "Shadowverse~Neutral~Minion~3~2~3~~Gabriel, Heavenly Voice~Battlecry~Taunt"
#	 requireTarget, keyWord, description = True, "Taunt", "Ward.Fanfare: Use X play points to give +X/+X to this follower and another allied follower. X equals your remaining play points."
#
#	 def targetExists(self, choice=0):
#		 return self.selectableFriendlyMinionExists(choice)
#
#	 def targetCorrect(self, target, choice=0):
#		 return target.cardType == "Minion" and target.ID == self.ID and target.onBoard and target != self
#
#	 def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
#		 x = self.Game.Manas.manas[self.ID]
#		 self.Game.Manas.manas[self.ID] -= x
#		 if target:
#			 target.buffDebuff(x, x)
#		 self.buffDebuff(x, x)
#		 PRINT(self, f"Gabriel, Heavenly Voice's Fanfare give {target.name} and itself +{x}/+{x}.")
#		 return None
#
#
# class EmpressOfSerenity(SVMinion):
#	 Class, race, name = "Swordcraft", "Commander", "Empress of Serenity"
#	 mana, attack, health = 3, 2, 2
#	 index = "Shadowverse~Swordcraft~Minion~3~2~2~Commander~Empress of Serenity~Battlecry"
#	 requireTarget, keyWord, description = False, "", "Fanfare: Summon a Shield Guardian.Enhance (5): Summon 3 instead.Enhance (10): Give +3/+3 to all allied Shield Guardians."
#
#	 def effCanTrig(self):
#		 self.effectViable = self.getMana() != self.mana
#
#	 def getMana(self):
#		 if self.Game.Manas.manas[self.ID] >= 10:
#			 return 10
#		 elif self.Game.Manas.manas[self.ID] >= 5:
#			 return 5
#		 else:
#			 return self.mana
#
#	 def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
#		 if choice == 0:
#			 PRINT(self,
#				   "Empress of Serenity's Fanfare summons a 1/1 Shield Guardian with Taunt.")
#			 self.Game.summonMinion([ShieldGuardian(self.Game, self.ID)], (-11, "totheRightEnd"), self.ID)
#		 else:
#			 PRINT(self,
#				   "Empress of Serenity's Fanfare summons three 1/1 Shield Guardian with Taunt.")
#			 self.Game.summonMinion([ShieldGuardian(self.Game, self.ID) for i in range(3)], (-11, "totheRightEnd"),
#									self.ID)
#			 if choice == 10:
#				 for minion in self.Game.minionsonBoard(self.ID):
#					 if type(minion) == ShieldGuardian:
#						 minion.buffDebuff(3, 3)
#				 PRINT(self,
#					   "Empress of Serenity's Fanfare give +3/+3 to all allied Shield Guardians.")
#		 return None
#
#
# class OluonTheChariot(SVMinion):
#	 Class, race, name = "Swordcraft", "Commander", "VII. Oluon, The Chariot"
#	 mana, attack, health = 3, 3, 3
#	 index = "Shadowverse~Swordcraft~Minion~3~3~3~Commander~VII. Oluon, The Chariot~Battlecry"
#	 requireTarget, keyWord, description = False, "", "Fanfare: Enhance (7) - Transform this follower into a VII. Oluon, Runaway Chariot.At the end of your turn, randomly activate 1 of the following effects.-Gain Ward.-Summon a Knight.-Deal 2 damage to the enemy leader."
#
#	 def __init__(self, Game, ID):
#		 super().__init__(Game, ID)
#		 self.trigsBoard = [TriggerOluonTheChariot(self)]
#
#	 def effCanTrig(self):
#		 self.effectViable = self.getMana() != self.mana
#
#	 def getMana(self):
#		 if self.Game.Manas.manas[self.ID] >= 7:
#			 return 7
#		 else:
#			 return self.mana
#
#	 def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
#		 if choice == 7:
#			 self.Game.transform(self, OluonRunawayChariot(self.Game, self.ID))
#		 return None
#
#
# class OluonRunawayChariot(SVMinion):
#	 Class, race, name = "Swordcraft", "Commander", "VII. Oluon, Runaway Chariot"
#	 mana, attack, health = 7, 8, 16
#	 index = "Shadowverse~Swordcraft~Minion~7~8~16~Commander~VII. Oluon, Runaway Chariot~Uncollectable"
#	 requireTarget, keyWord, description = False, "", "Can't attack.At the end of your turn, randomly deal X damage to an enemy or another ally and then Y damage to this follower. X equals this follower's attack and Y equals the attack of the follower or leader damaged (leaders have 0 attack). Do this 2 times."
#
#	 def __init__(self, Game, ID):
#		 super().__init__(Game, ID)
#		 self.marks["Can't Attack"] = 1
#		 self.trigsBoard = [TriggerOluonRunawayChariot(self)]
#
#
# class TriggerOluonTheChariot(TriggeronBoard):
#	 def __init__(self, entity):
#		 super().__init__(entity, ["TurnEnds"])
#
#	 def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
#		 return self.entity.onBoard and ID == self.entity.ID
#
#	 def effect(self, signal, ID, subject, target, number, comment, choice=0):
#		 es = ["T", "H", "K"]
#		 e = np.random.choice(es)
#		 if e == "T":
#			 self.entity.getsStatus("Taunt")
#		 elif e == "H":
#			 self.entity.dealsDamage(self.entity.Game.heroes[3 - self.entity.ID], 2)
#		 elif e == "K":
#			 PRINT(self,
#				   "VII. Oluon, The Chariot summons a 1/1 Shield Guardian with Ward.")
#			 self.entity.Game.summonMinion([ShieldGuardian(self.entity.Game, self.entity.ID)], (-11, "totheRightEnd"),
#										   self.entity.ID)
#
#
# class TriggerOluonRunawayChariot(TriggeronBoard):
#	 def __init__(self, entity):
#		 super().__init__(entity, ["TurnEnds"])
#
#	 def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
#		 return self.entity.onBoard and ID == self.entity.ID
#
#	 def effect(self, signal, ID, subject, target, number, comment, choice=0):
#		 for i in range(2):
#			 targets = []
#			 for e in self.entity.Game.livingObjtoTakeRandomDamage(1):
#				 if e != self.entity:
#					 targets.append(e)
#			 for e in self.entity.Game.livingObjtoTakeRandomDamage(2):
#				 if e != self.entity:
#					 targets.append(e)
#			 target = np.random.choice(targets)
#			 self.entity.dealsDamage(target, self.entity.attack)
#			 PRINT(self, f"VII. Oluon, Runaway Chariot deals {self.entity.attack} damage to {target}")
#			 damage = 0
#			 if target.cardType == "Minion":
#				 damage = target.attack
#			 target.dealsDamage(self.entity, damage)
#			 PRINT(self, f"{target} deals {damage} damage to VII. Oluon, Runaway Chariot ")
#
#
# class GeltResoluteKnight(SVMinion):
#	 Class, race, name = "Swordcraft", "Officer", "Gelt, Resolute Knight"
#	 mana, attack, health = 3, 3, 3
#	 index = "Shadowverse~Swordcraft~Minion~3~3~3~Officer~Gelt, Resolute Knight~Battlecry~Deathrattle"
#	 requireTarget, keyWord, description = False, "", "Fanfare: If an allied Commander card is in play, gain Rush.Last Words: At the start of your next turn, put a random Commander card from your deck into your hand."
#
#	 def __init__(self, Game, ID):
#		 super().__init__(Game, ID)
#		 self.deathrattles = [DeathrattleGeltResoluteKnight(self)]
#
#	 def effCanTrig(self):
#		 self.effectViable = False
#		 for minion in self.Game.minionsonBoard(self.ID):
#			 if "Commander" in minion.race:
#				 self.effectViable = True
#				 break
#
#	 def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
#		 controlOfficer = False
#		 for minion in self.Game.minionsonBoard(self.ID):
#			 if "Commander" in minion.race:
#				 controlOfficer = True
#				 break
#		 if controlOfficer:
#			 self.getsStatus("Rush")
#		 return None
#
#
# class DeathrattleGeltResoluteKnight(Deathrattle_Minion):
#	 def effect(self, signal, ID, subject, target, number, comment, choice=0):
#		 PRINT(self,
#			   "Last Words: At the start of your next turn, put a random Commander card from your deck into your hand.")
#		 trigger = TriggerDeathrattleGeltResoluteKnight(self.entity.Game.heroes[self.entity.ID])
#		 self.entity.Game.heroes[self.entity.ID].trigsBoard.append(trigger)
#		 trigger.connect()
#
#
# class TriggerDeathrattleGeltResoluteKnight(TriggeronBoard):
#	 def __init__(self, entity):
#		 super().__init__(entity, ["TurnStarts"])
#
#	 def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
#		 return ID == self.entity.ID
#
#	 def effect(self, signal, ID, subject, target, number, comment, choice=0):
#		 commanders = []
#		 for card in self.entity.Game.Hand_Deck.decks[self.entity.ID]:
#			 if card.cardType == "Minion" and "Commander" in card.race:
#				 commanders.append(card)
#		 if commanders:
#			 card = np.random.choice(commanders)
#			 self.entity.Game.Hand_Deck.drawCard(self.entity.ID, card)
#			 PRINT(self, f"Gelt, Resolute Knight's Last Words let you draw {card.name}.")
#		 for t in self.entity.Game.heroes[ID].trigsBoard:
#			 if type(t) == TriggerDeathrattleGeltResoluteKnight:
#				 t.disconnect()
#				 self.entity.Game.heroes[ID].trigsBoard.remove(t)
#				 break
#
#
# class LadyOfTheLance(SVMinion):
#	 Class, race, name = "Swordcraft", "Officer", "Lady of the Lance"
#	 mana, attack, health = 3, 3, 2
#	 index = "Shadowverse~Swordcraft~Minion~3~3~2~Officer~Lady of the Lance~Battlecry~Rush"
#	 requireTarget, keyWord, description = False, "Rush", "Rush.Fanfare: If you have at least 2 Commander cards in your hand, gain Bane and the following effect - The next time this follower takes damage, reduce that damage to 0.Fanfare: Enhance (8) - Gain Storm. Recover 5 play points."
#
#	 def getMana(self):
#		 if self.Game.Manas.manas[self.ID] >= 8:
#			 return 8
#		 else:
#			 return self.mana
#
#	 def effCanTrig(self):
#		 commanders = 0
#		 for card in self.Game.Hand_Deck.hands[self.ID]:
#			 if card.cardType == "Minion" and "Commander" in card.race:
#				 commanders += 1
#		 self.effectViable = commanders >= 2 or self.getMana() != self.mana
#
#	 def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
#		 if choice == 8:
#			 PRINT(self, "Lady of the Lance's Fanfare give it Storm.")
#			 self.getsStatus("Charge")
#			 self.Game.Manas.manas[self.ID] += 5
#		 commanders = 0
#		 for card in self.Game.Hand_Deck.hands[self.ID]:
#			 if card.cardType == "Minion" and "Commander" in card.race:
#				 commanders += 1
#		 if commanders >= 2:
#			 PRINT(self, "Lady of the Lance's Fanfare give it Bane and reduce next damage to 0.")
#			 self.getsStatus("Poisonous")
#			 self.marks["Next Damage 0"] += 1
#		 return None
#
#
# class PecorinePeckishPrincess(SVMinion):
#	 Class, race, name = "Swordcraft", "Commander", "Pecorine, Peckish Princess"
#	 mana, attack, health = 3, 3, 2
#	 index = "Shadowverse~Swordcraft~Minion~3~3~2~Commander~Pecorine, Peckish Princess~Battlecry~Rush"
#	 requireTarget, keyWord, description = True, "Rush", "Rush.Fanfare: Union Burst (10) - Gain +3/+3. Deal 5 damage to an enemy follower.At the end of your turn, gain +0/+1."
#
#	 def __init__(self, Game, ID):
#		 super().__init__(Game, ID)
#		 self.trigsBoard = [TriggerPecorinePeckishPrincess(self)]
#
#	 def effCanTrig(self):
#		 self.effectViable = self.marks["UB"] <= self.Game.Counters.numTurnPassedThisGame[self.ID]
#
#	 def targetExists(self, choice=0):
#		 if self.marks["UB"] <= self.Game.Counters.numTurnPassedThisGame[self.ID]:
#			 return self.selectableEnemyMinionExists(choice)
#		 return False
#
#	 def targetCorrect(self, target, choice=0):
#		 return target.cardType == "Minion" and target.ID != self.ID and target.onBoard
#
#	 def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
#		 if self.marks["UB"] <= self.Game.Counters.numTurnPassedThisGame[self.ID]:
#			 self.buffDebuff(3, 3)
#			 if target:
#				 PRINT(self, f"Pecorine, Peckish Princess deals 5 damage to minion {target.name}")
#				 self.dealsDamage(target, 5)
#		 return None
#
#
# class TriggerPecorinePeckishPrincess(TriggeronBoard):
#	 def __init__(self, entity):
#		 super().__init__(entity, ["TurnEnds"])
#
#	 def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
#		 return self.entity.onBoard and ID == self.entity.ID
#
#	 def effect(self, signal, ID, subject, target, number, comment, choice=0):
#		 PRINT(self, "Pecorine Peckish Princess gains +0/+1.")
#		 self.entity.buffDebuff(0, 1)
#
#
# class TsubakiOfTheDemonBlade(SVMinion):
#	 Class, race, name = "Swordcraft", "Officer", "Tsubaki of the Demon Blade"
#	 mana, attack, health = 3, 3, 2
#	 index = "Shadowverse~Swordcraft~Minion~3~3~2~Officer~Tsubaki of the Demon Blade~Battlecry~Stealth"
#	 requireTarget, keyWord, description = False, "Stealth", "Ambush.Fanfare: If at least 10 allied followers have been destroyed this match, gain +1/+1 and randomly destroy 1 of the enemy followers with the highest attack in play."
#
#	 def effCanTrig(self):
#		 self.effectViable = self.Game.Counters.numMinionsDiedThisGame[self.ID] >= 10
#
#	 def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
#		 if self.Game.Counters.numMinionsDiedThisGame[self.ID] >= 10:
#			 self.buffDebuff(1, 1)
#			 PRINT(self, f"Tsubaki of the Demon Blade's Fanfare gives itself +1/+1.")
#			 ts = self.Game.minionsAlive(3 - self.ID)
#			 maxAttack = 0
#			 for t in ts:
#				 maxAttack = max(maxAttack, t.attack)
#			 targets = []
#			 for t in ts:
#				 if t.attack == maxAttack:
#					 targets.append(t)
#			 if targets:
#				 target = np.random.choice(targets)
#			 if target:
#				 target.dead = True
#				 PRINT(self, f"Tsubaki of the Demon Blade's Fanfare destroys {target.name}.")
#		 return None
#
#
# class StrokeOfConviction(Spell):
#	 Class, school, name = "Swordcraft", "", "Stroke of Conviction"
#	 requireTarget, mana = False, 3
#	 index = "Shadowverse~Swordcraft~Spell~3~~Stroke of Conviction"
#	 description = "Choose: Use play points equal to this card's cost and play this card as an Erika's Sleight, Mistolina's Swordplay, or Bayleon's Command."
#
#	 def effCanTrig(self):
#		 self.effectViable = self.getMana() != self.mana
#
#	 def getMana(self):
#		 if self.Game.Manas.manas[self.ID] >= 6:
#			 return 6
#		 else:
#			 return self.mana
#
#	 def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
#		 if choice == 6:
#			 damage = (5 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
#			 PRINT(self,
#				   f"Stroke of Conviction is cast, summons two 1/1 Quickblader with Storm, deals {damage} damage to a random minion and gives all friendly minions +1/+1.")
#			 self.Game.summonMinion([Quickblader(self.Game, self.ID) for i in range(2)], (-11, "totheRightEnd"),
#									self.ID)
#			 targets = self.Game.minionsAlive(3 - self.ID)
#			 if targets != []:
#				 target = np.random.choice(targets)
#				 self.dealsDamage(target, damage)
#			 for minion in self.Game.minionsonBoard(self.ID):
#				 minion.buffDebuff(1, 1)
#		 elif self.ID == self.Game.turn:
#			 PRINT(self, "Stroke of Conviction lets player choose a Spell to cast:")
#			 self.Game.options = [ErikasSleight(self.Game, self.ID), MistolinasSwordplay(self.Game, self.ID),
#								  BayleonsCommand(self.Game, self.ID)]
#			 self.Game.DiscoverHandler.startDiscover(self)
#		 else:
#			 ErikasSleight(self.Game, self.ID).cast()
#		 return None
#
#	 def discoverDecided(self, option):
#		 option.cast()
#		 return None
#
#
# class ErikasSleight(Spell):
#	 Class, school, name = "Swordcraft", "", "Erika's Sleight"
#	 requireTarget, mana = False, 0
#	 index = "Shadowverse~Swordcraft~Spell~0~~Erika's Sleight~Uncollectible"
#	 description = "Summon 2 Quickbladers."
#
#	 def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
#		 PRINT(self, "Erika's Sleight summons two 1/1 Quickblader with Storm.")
#		 self.Game.summonMinion([Quickblader(self.Game, self.ID) for i in range(2)], (-11, "totheRightEnd"),
#								self.ID)
#		 return None
#
#
# class MistolinasSwordplay(Spell):
#	 Class, school, name = "Swordcraft", "", "Mistolina's Swordplay"
#	 requireTarget, mana = False, 0
#	 index = "Shadowverse~Swordcraft~Spell~0~~Mistolina's Swordplay~Uncollectible"
#	 description = "Deal 5 damage to a random enemy follower."
#
#	 def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
#		 damage = (5 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
#		 PRINT(self,
#			   f"Mistolina's Swordplay is cast and deals {damage} damage to a random minion.")
#		 targets = self.Game.minionsAlive(3 - self.ID)
#		 if targets != []:
#			 target = np.random.choice(targets)
#			 PRINT(self, f"Mistolina's Swordplay deals {damage} damage to minion {target.name}")
#			 self.dealsDamage(target, damage)
#		 return None
#
#
# class BayleonsCommand(Spell):
#	 Class, school, name = "Swordcraft", "", "Bayleon's Command"
#	 requireTarget, mana = False, 0
#	 index = "Shadowverse~Swordcraft~Spell~0~~Bayleon's Command~Uncollectible"
#	 description = "Give +1/+1 to all allied followers."
#
#	 def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
#		 PRINT(self, "Bayleon's Command gives all friendly minions +1/+1.")
#		 for minion in self.Game.minionsonBoard(self.ID):
#			 minion.buffDebuff(1, 1)
#		 return None
#
#
# class CourtlyDance(Spell):
#	 Class, school, name = "Swordcraft", "", "Courtly Dance"
#	 requireTarget, mana = False, 3
#	 index = "Shadowverse~Swordcraft~Spell~3~~Courtly Dance"
#	 description = "Put a random 1-play point and 2-play point Swordcraft follower from your deck into play.Enhance (8): Then, put a random 3-play point Swordcraft follower from your deck into play and evolve them. Evolve effects will not activate for those followers."
#
#	 def effCanTrig(self):
#		 self.effectViable = self.getMana() != self.mana
#
#	 def getMana(self):
#		 if self.Game.Manas.manas[self.ID] >= 8:
#			 return 8
#		 else:
#			 return self.mana
#
#	 def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
#		 ones, twos, threes = [], [], []
#		 a, b, c = None, None, None
#		 for card in self.Game.Hand_Deck.decks[self.ID]:
#			 if card.cardType == "Minion" and isinstance(card, SVMinion) and \
#					 card.mana == 1 and card.Class == "Swordcraft":
#				 ones.append(card)
#		 if ones != [] and self.Game.space(self.ID) > 0:
#			 a = np.random.choice(ones)
#			 self.Game.summonfromDeck(a, -1, self.ID)
#			 PRINT(self, f"Courtly Dance summons {a.name} from deck.")
#		 for card in self.Game.Hand_Deck.decks[self.ID]:
#			 if card.cardType == "Minion" and isinstance(card, SVMinion) and \
#					 card.mana == 2 and card.Class == "Swordcraft":
#				 twos.append(card)
#		 if twos != [] and self.Game.space(self.ID) > 0:
#			 b = np.random.choice(twos)
#			 self.Game.summonfromDeck(b, -1, self.ID)
#			 PRINT(self, f"Courtly Dance summons {b.name} from deck.")
#		 if choice == 8:
#			 for card in self.Game.Hand_Deck.decks[self.ID]:
#				 if card.cardType == "Minion" and isinstance(card, SVMinion) and \
#						 card.mana == 3 and card.Class == "Swordcraft":
#					 threes.append(card)
#			 if threes != [] and self.Game.space(self.ID) > 0:
#				 c = np.random.choice(threes)
#				 self.Game.summonfromDeck(c, -1, self.ID)
#				 PRINT(self, f"Courtly Dance summons {c.name} from deck.")
#			 if a and a.onBoard:
#				 a.evolve()
#				 PRINT(self, f"Courtly Dance let {a.name} evolve.")
#			 if b and b.onBoard:
#				 b.evolve()
#				 PRINT(self, f"Courtly Dance let {b.name} evolve.")
#			 if c and c.onBoard:
#				 c.evolve()
#				 PRINT(self, f"Courtly Dance let {c.name} evolve.")
#		 return None
#
#
# """4 Cost"""
#
#
# class FieranHavensentWindGod(SVMinion):
#	 Class, race, name = "Neutral", "", "Fieran, Havensent Wind God"
#	 mana, attack, health = 4, 1, 1
#	 index = "Shadowverse~Neutral~Minion~4~1~1~~Fieran, Havensent Wind God~Battlecry"
#	 requireTarget, keyWord, description = True, "Taunt", "Invocation: At the start of your turn, Rally (10) - Invoke this card.------Fanfare: If you have more evolution points than your opponent, gain +0/+2 and deal 2 damage to an enemy follower. (You have 0 evolution points on turns you are unable to evolve.)At the end of your turn, give +1/+1 to all allied followers."
#
#	 def __init__(self, Game, ID):
#		 super().__init__(Game, ID)
#		 self.trigsBoard = [TriggerFieranHavensentWindGod(self), TriggerInvocationFieranHavensentWindGod(self)]
#
#	 def targetExists(self, choice=0):
#		 selfPoint, oppPoint = 0, 0
#		 if self.Game.Counters.numTurnPassedThisGame[self.ID] >= \
#				 self.Game.Counters.numEvolutionTurn[self.ID]:
#			 selfPoint = self.Game.Counters.numEvolutionPoint[self.ID]
#		 if self.Game.Counters.numTurnPassedThisGame[3 - self.ID] >= \
#				 self.Game.Counters.numEvolutionTurn[3 - self.ID]:
#			 oppPoint = self.Game.Counters.numEvolutionPoint[3 - self.ID]
#		 return self.selectableEnemyMinionExists() and selfPoint > oppPoint
#
#	 def targetCorrect(self, target, choice=0):
#		 return target.cardType == "Minion" and target.ID != self.ID and target.onBoard
#
#	 def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
#		 selfPoint, oppPoint = 0, 0
#		 if self.Game.Counters.numTurnPassedThisGame[self.ID] >= \
#				 self.Game.Counters.numEvolutionTurn[self.ID]:
#			 selfPoint = self.Game.Counters.numEvolutionPoint[self.ID]
#		 if self.Game.Counters.numTurnPassedThisGame[3 - self.ID] >= \
#				 self.Game.Counters.numEvolutionTurn[3 - self.ID]:
#			 oppPoint = self.Game.Counters.numEvolutionPoint[3 - self.ID]
#		 if selfPoint > oppPoint:
#			 self.buffDebuff(0, 2)
#			 PRINT(self, f"Panther Scout's Fanfare gives itself +0/+2.")
#			 if target:
#				 PRINT(self, f"Gabriel, Heavenly Voice 2 damage to minion {target.name}")
#				 self.dealsDamage(target, 2)
#		 return None
#
#
# class TriggerFieranHavensentWindGod(TriggeronBoard):
#	 def __init__(self, entity):
#		 super().__init__(entity, ["TurnEnds"])
#
#	 def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
#		 return self.entity.onBoard and ID == self.entity.ID
#
#	 def effect(self, signal, ID, subject, target, number, comment, choice=0):
#		 targets = self.entity.Game.minionsonBoard(self.entity.ID)
#		 extractfrom(self.entity, targets)
#		 if targets:
#			 PRINT(self, "At the end of turn, Fieran, Havensent Wind God gives all friendly minions +1/+1")
#			 for target in targets:
#				 target.buffDebuff(1, 1)
#
#
# class TriggerInvocationFieranHavensentWindGod(TriggerinDeck):
#	 def __init__(self, entity):
#		 super().__init__(entity, ["TurnStarts"])
#
#	 def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
#		 return self.entity.inDeck and ID == self.entity.ID and self.entity.Game.space(self.entity.ID) > 0 and \
#				self.entity.Game.Counters.numMinionsSummonThisGame[self.entity.ID] >= 10 and \
#				self.entity.name not in self.entity.Game.Counters.minionInvocationThisTurn
#
#	 def effect(self, signal, ID, subject, target, number, comment, choice=0):
#		 if self.entity.Game.space(self.entity.ID) > 0:
#			 self.entity.Game.Counters.minionInvocationThisTurn.append(self.entity.name)
#			 self.entity.Game.summonfromDeck(self.entity, -1, self.entity.ID)
#			 PRINT(self, f"Fieran, Havensent Wind God is summoned from player {self.entity.ID}'s deck.")
#
#
# class ResolveOfTheFallen(Spell):
#	 Class, school, name = "Neutral", "", "Resolve of the Fallen"
#	 requireTarget, mana = True, 4
#	 index = "Shadowverse~Neutral~Spell~4~~Resolve of the Fallen"
#	 description = "Destroy an enemy follower or amulet.If at least 3 allied followers have evolved this match, recover 3 play points.Then, if at least 5 have evolved, draw 2 cards."
#
#	 def available(self):
#		 return self.selectableEnemyMinionExists()
#
#	 def targetCorrect(self, target, choice=0):
#		 return target.cardType == "Minion" and target.ID != self.ID and target.onBoard
#
#	 def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
#		 if self.ID == self.Game.turn:
#			 target.dead = True
#		 if self.Game.Counters.numMinionsEvolvedThisGame[self.ID] > 3:
#			 self.Game.Manas.manas[self.ID] += 3
#		 if self.Game.Counters.numMinionsEvolvedThisGame[self.ID] > 5:
#			 self.Game.Hand_Deck.drawCard(self.ID)
#			 self.Game.Hand_Deck.drawCard(self.ID)
#		 return None
#
#
# class PrudentGeneral(SVMinion):
#	 Class, race, name = "Swordcraft", "Commander", "PrudentGeneral"
#	 mana, attack, health = 4, 3, 4
#	 index = "Shadowverse~Swordcraft~Minion~4~3~4~Commander~Prudent General"
#	 requireTarget, keyWord, description = False, "", ""
#
#	 def inEvolving(self):
#		 trigger = TriggerPrudentGeneral(self.Game.heroes[self.ID])
#		 for t in self.Game.heroes[self.ID].trigsBoard:
#			 if type(t) == type(trigger):
#				 return
#		 self.Game.heroes[self.ID].trigsBoard.append(trigger)
#		 trigger.connect()
#
#
# class TriggerPrudentGeneral(TriggeronBoard):
#	 def __init__(self, entity):
#		 super().__init__(entity, ["TurnEnds"])
#
#	 def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
#		 return self.entity.onBoard and ID == self.entity.ID
#
#	 def effect(self, signal, ID, subject, target, number, comment, choice=0):
#		 PRINT(self, "Prudent General's ability summons a 2/2 Steelclad Knight.")
#		 self.entity.Game.summonMinion([SteelcladKnight(self.entity.Game, self.entity.ID)], (-11, "totheRightEnd"),
#									   self.entity.ID)
#
#
# class ShizuruSisterlySabreur(SVMinion):
#	 Class, race, name = "Swordcraft", "Officer", "Shizuru, Sisterly Sabreur"
#	 mana, attack, health = 4, 3, 5
#	 index = "Shadowverse~Swordcraft~Minion~4~3~5~Officer~Shizuru, Sisterly Sabreur~Battlecry~Taunt"
#	 requireTarget, keyWord, description = False, "Taunt", "Ward.Fanfare: Union Burst (10) - Deal 3 damage to the enemy leader. Gain the ability to evolve for 0 evolution points."
#
#	 def effCanTrig(self):
#		 self.effectViable = self.marks["UB"] <= self.Game.Counters.numTurnPassedThisGame[self.ID]
#
#	 def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
#		 if self.marks["UB"] <= self.Game.Counters.numTurnPassedThisGame[self.ID]:
#			 self.getsStatus("Free Evolve")
#			 PRINT(self, f"Shizuru, Sisterly Sabreur 3 damage to the enemy leader.")
#			 self.dealsDamage(self.Game.heroes[3 - self.ID], 3)
#		 return None
#
#	 def inEvolving(self):
#		 trigger = TriggerShizuruSisterlySabreur(self)
#		 self.trigsBoard.append(trigger)
#		 if self.onBoard:
#			 trigger.connect()
#
#
# class TriggerShizuruSisterlySabreur(TriggeronBoard):
#	 def __init__(self, entity):
#		 super().__init__(entity, ["TurnEnds"])
#
#	 def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
#		 return self.entity.onBoard and ID == self.entity.ID
#
#	 def effect(self, signal, ID, subject, target, number, comment, choice=0):
#		 selfPoint, oppPoint = 0, 0
#		 if self.entity.Game.Counters.numTurnPassedThisGame[self.entity.ID] >= \
#				 self.entity.Game.Counters.numEvolutionTurn[self.entity.ID]:
#			 selfPoint = self.entity.Game.Counters.numEvolutionPoint[self.entity.ID]
#		 if self.entity.Game.Counters.numTurnPassedThisGame[3 - self.entity.ID] >= \
#				 self.entity.Game.Counters.numEvolutionTurn[3 - self.entity.ID]:
#			 oppPoint = self.entity.Game.Counters.numEvolutionPoint[3 - self.entity.ID]
#		 if selfPoint > oppPoint:
#			 self.entity.restoresHealth(self.entity, 3)
#			 self.entity.restoresHealth(self.entity.Game.heroes[self.entity.ID], 3)
#			 PRINT(self, "Shizuru, Sisterly Sabreur restore 3 defense to your leader and itself.")
#
#
# """5 Cost"""
#
#
# class ZelgeneaTheWorld(SVMinion):
#	 Class, race, name = "Neutral", "", "XXI. Zelgenea, The World"
#	 mana, attack, health = 5, 5, 5
#	 index = "Shadowverse~Neutral~Minion~5~5~5~~XXI. Zelgenea, The World~Battlecry"
#	 requireTarget, keyWord, description = False, "", "Invocation: At the start of your tenth turn, invoke this card. Then, evolve it.----------Fanfare: Restore 5 defense to your leader. If your leader had 14 defense or less before defense was restored, draw 2 cards and randomly destroy 1 of the enemy followers with the highest attack in play.Can't be evolved using evolution points. (Can be evolved using card effects.)"
#
#	 attackAdd, healthAdd = 5, 5
#
#	 def __init__(self, Game, ID):
#		 super().__init__(Game, ID)
#		 self.marks["Can't Evolve"] = 1
#		 self.trigsDeck = [TriggerInvocationZelgeneaTheWorld(self)]
#
#	 def effCanTrig(self):
#		 self.effectViable = self.Game.heroes[self.ID].health < 15
#
#	 def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
#		 if self.Game.heroes[self.ID].health < 15:
#			 self.restoresHealth(self.Game.heroes[self.ID], 5)
#			 PRINT(self, f"XXI. Zelgenea, The World restores 5 Health to its leader.")
#			 ts = self.Game.minionsAlive(3 - self.ID)
#			 maxAttack = 0
#			 for t in ts:
#				 maxAttack = max(maxAttack, t.attack)
#			 targets = []
#			 for t in ts:
#				 if t.attack == maxAttack:
#					 targets.append(t)
#			 if targets:
#				 target = np.random.choice(targets)
#			 if target:
#				 target.dead = True
#				 PRINT(self, f"XXI. Zelgenea, The World destroys {target.name}.")
#			 self.Game.Hand_Deck.drawCard(self.ID)
#			 self.Game.Hand_Deck.drawCard(self.ID)
#		 return None
#
#	 def inEvolving(self):
#		 trigger = TriggerAttackZelgeneaTheWorld(self)
#		 self.trigsBoard.append(trigger)
#		 trigger.connect()
#
#
# class TriggerAttackZelgeneaTheWorld(TriggeronBoard):
#	 def __init__(self, entity):
#		 super().__init__(entity, ["MinionAttackingHero", "MinionAttackingMinion"])
#
#	 def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
#		 return self.entity.onBoard and subject == self.entity
#
#	 def effect(self, signal, ID, subject, target, number, comment, choice=0):
#		 trigger = TriggerEndZelgeneaTheWorld(self.entity.Game.heroes[self.entity.ID])
#		 for t in self.entity.Game.heroes[self.entity.ID].trigsBoard:
#			 if type(t) == type(trigger):
#				 return
#		 self.entity.Game.heroes[self.entity.ID].trigsBoard.append(trigger)
#		 trigger.connect()
#
#
# class TriggerEndZelgeneaTheWorld(TriggeronBoard):
#	 def __init__(self, entity):
#		 super().__init__(entity, ["TurnEnds"])
#
#	 def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
#		 return self.entity.onBoard and ID == self.entity.ID
#
#	 def effect(self, signal, ID, subject, target, number, comment, choice=0):
#		 targets = [self.entity.Game.heroes[1], self.entity.Game.heroes[2]] + self.entity.Game.minionsonBoard(1) \
#				   + self.entity.Game.minionsonBoard(2)
#		 PRINT(self, "XXI. Zelgenea, The World's ability deals 4 damage to all characters.")
#		 self.entity.dealsAOE(targets, [4 for obj in targets])
#
#
# class TriggerInvocationZelgeneaTheWorld(TriggerinDeck):
#	 def __init__(self, entity):
#		 super().__init__(entity, ["TurnStarts"])
#
#	 def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
#		 return self.entity.inDeck and ID == self.entity.ID and self.entity.Game.space(self.entity.ID) > 0 and \
#				self.entity.Game.Counters.numTurnPassedThisGame[self.entity.ID] == 10 and \
#				self.entity.name not in self.entity.Game.Counters.minionInvocationThisTurn
#
#	 def effect(self, signal, ID, subject, target, number, comment, choice=0):
#		 if self.entity.Game.space(self.entity.ID) > 0:
#			 self.entity.Game.summonfromDeck(self.entity, -1, self.entity.ID)
#			 self.entity.Game.Counters.minionInvocationThisTurn.append(self.entity.name)
#			 PRINT(self, f"XXI. Zelgenea, The World is summoned from player {self.entity.ID}'s deck.")
#			 self.entity.evolve()
#
#
# class LuxbladeArriet(SVMinion):
#	 Class, race, name = "Swordcraft", "Officer", "Luxblade Arriet"
#	 mana, attack, health = 5, 4, 5
#	 index = "Shadowverse~Swordcraft~Minion~5~4~5~Officer~Luxblade Arriet~Battlecry"
#	 requireTarget, keyWord, description = False, "", "Fanfare: If at least 1 allied follower has evolved this match, gain Ward.Then, if at least 3 have evolved, recover 3 play points.Then, if at least 5 have evolved, restore 5 defense to your leader.Then, if at least 7 have evolved, draw cards until there are 7 cards in your hand."
#
#	 def effCanTrig(self):
#		 self.effectViable = self.Game.Counters.numMinionsEvolvedThisGame[self.ID] >= 1
#
#	 def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
#		 if self.Game.Counters.numMinionsEvolvedThisGame[self.ID] >= 1:
#			 PRINT(self, "Luxblade Arriet gains Ward.")
#			 self.getsStatus("Taunt")
#		 if self.Game.Counters.numMinionsEvolvedThisGame[self.ID] >= 3:
#			 PRINT(self, "Luxblade Arriet restores 3 PP.")
#			 self.Game.Manas.manas[self.ID] += 3
#		 if self.Game.Counters.numMinionsEvolvedThisGame[self.ID] >= 5:
#			 PRINT(self, "Luxblade Arriet restore 5 defense to your leader.")
#			 self.restoresHealth(self.Game.heroes[self.ID], 5)
#		 if self.Game.Counters.numMinionsEvolvedThisGame[self.ID] >= 7:
#			 PRINT(self, "Luxblade Arriet let you draw cards until there are 7 cards in your hand.")
#			 for i in range(7 - len(self.Game.Hand_Deck.hands[self.ID])):
#				 self.Game.Hand_Deck.drawCard(self.ID)
#		 return None
#
#	 def inEvolving(self):
#		 PRINT(self, "Levin Beastmaster evolves and summons a 1/1 White Tiger and change it into Levin followers.")
#		 self.Game.summonMinion([LevinWhiteTiger(self.Game, self.ID)], (-11, "totheRightEnd"), self.ID)
#
#
# class AmeliaTheSilverflash(SVMinion):
#	 Class, race, name = "Swordcraft", "Commander", "Amelia, the Silverflash"
#	 mana, attack, health = 5, 4, 4
#	 index = "Shadowverse~Swordcraft~Minion~5~4~4~Commander~Amelia, the Silverflash~Battlecry"
#	 requireTarget, keyWord, description = False, "", "Fanfare: Randomly put 2 different Officer followers from your deck into your hand.Enhance (7): Gain the ability to evolve for 0 evolution points and the following effect - The next time this follower takes damage, reduce that damage to 0."
#	 evolveRequireTarget = True
#
#	 def effCanTrig(self):
#		 self.effectViable = self.getMana() != self.mana
#
#	 def getMana(self):
#		 if self.Game.Manas.manas[self.ID] >= 7:
#			 return 7
#		 else:
#			 return self.mana
#
#	 def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
#		 officers = []
#		 for card in self.Game.Hand_Deck.decks[self.ID]:
#			 if card.cardType == "Minion" and "Officer" in card.race:
#				 officers.append(card)
#		 if officers:
#			 card = np.random.choice(officers)
#			 self.Game.Hand_Deck.drawCard(self.ID, card)
#			 PRINT(self, f"Amelia, the Silverflash's Fanfare let you draw {card.name}.")
#			 if self.Game.Hand_Deck.handNotFull(self.ID):
#				 offs = []
#				 for c in officers:
#					 if type(c) != type(card):
#						 offs.append(c)
#				 if offs:
#					 card = np.random.choice(offs)
#					 self.Game.Hand_Deck.drawCard(self.ID, card)
#					 PRINT(self, f"Amelia, the Silverflash's Fanfare let you draw {card.name}.")
#		 if choice == 7:
#			 self.getsStatus("Free Evolve")
#			 self.marks["Next Damage 0"] = 1
#		 return None
#
#	 def inHandEvolving(self, target=None):
#		 if target:
#			 ManaModification(target, changeby=-3).applies()
#			 trigger = TriggerAmeliaTheSilverflash(target)
#			 target.trigsHand.append(trigger)
#			 trigger.connect()
#			 PRINT(self, f"Amelia, the Silverflash let {target.name}'s cost -3 in this turn.")
#		 return
#
#	 def extraTargetCorrect(self, target, affair):
#
#		 return target.cardType and target.cardType == "Minion" and "Officer" in target.race and target.ID == self.ID and target.inHand
#
#
# class TriggerAmeliaTheSilverflash(TriggerinHand):
#	 def __init__(self, entity):
#		 super().__init__(entity, ["TurnEnds"])
#
#	 def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
#		 return self.entity.inHand and ID == self.entity.ID
#
#	 def effect(self, signal, ID, subject, target, number, comment, choice=0):
#		 for m in self.entity.manaModifications:
#			 if m.changeby == -3:
#				 self.entity.manaModifications.remove(m)
#				 break
#		 for t in self.entity.trigsHand:
#			 if type(t) == TriggerAmeliaTheSilverflash:
#				 t.disconnect()
#				 self.entity.trigsHand.remove(t)
#				 break
#
#
# class AlbertLevinChampion(SVMinion):
#	 Class, race, name = "Swordcraft", "Levin", "Albert, Levin Champion"
#	 mana, attack, health = 5, 3, 5
#	 index = "Shadowverse~Swordcraft~Minion~5~3~5~Levin~Albert, Levin Champion~Battlecry"
#	 requireTarget, keyWord, description = False, "Charge", "Storm.Fanfare: Enhance (9) - Randomly put different Levin followers (excluding Albert, Levin Champion) from your deck into play until your area is full.Strike: Gain +1/+0 if another allied Levin card is in play."
#
#	 def __init__(self, Game, ID):
#		 super().__init__(Game, ID)
#		 self.trigsBoard = [TriggerAlbertLevinChampion(self)]
#
#	 def effCanTrig(self):
#		 self.effectViable = self.getMana() != self.mana
#
#	 def getMana(self):
#		 if self.Game.Manas.manas[self.ID] >= 9:
#			 return 9
#		 else:
#			 return self.mana
#
#	 def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
#		 if choice == 9:
#			 names = []
#			 for i in range(4):
#				 minions = []
#				 for card in self.Game.Hand_Deck.decks[self.ID]:
#					 if card.cardType == "Minion" and isinstance(card, SVMinion) and \
#							 "Levin" in card.race and card.Class == "Swordcraft" and card.name not in names:
#						 minions.append(card)
#				 if minions != [] and self.Game.space(self.ID) > 0:
#					 m = np.random.choice(minions)
#					 names.append(m.name)
#					 self.Game.summonfromDeck(m, -1, self.ID)
#					 PRINT(self, f"Albert, Levin Champion's Fanfare summons {m.name} from deck.")
#				 else:
#					 break
#		 return None
#
#
# class TriggerAlbertLevinChampion(TriggeronBoard):
#	 def __init__(self, entity):
#		 super().__init__(entity, ["MinionAttackingHero", "MinionAttackingMinion"])
#
#	 def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
#		 return self.entity.onBoard and subject == self.entity
#
#	 def effect(self, signal, ID, subject, target, number, comment, choice=0):
#		 controlLevin = False
#		 for minion in self.entity.Game.minionsonBoard(self.entity.ID):
#			 if "Levin" in minion.race:
#				 controlLevin = True
#				 break
#		 if controlLevin:
#			 PRINT(self, f"Minion {self.entity.name} attacks and get +1/+0")
#			 self.entity.buffDebuff(1, 0)
#
#
# """6 Cost"""
#
#
# class DiamondPaladin(SVMinion):
#	 Class, race, name = "Swordcraft", "Commander", "Diamond Paladin"
#	 mana, attack, health = 6, 4, 5
#	 index = "Shadowverse~Swordcraft~Minion~6~4~5~Commander~Diamond Paladin~Battlecry~Rush"
#	 requireTarget, keyWord, description = False, "Rush", "Rush.Fanfare: Enhance (8) - Gain the ability to evolve for 0 evolution points.During your turn, whenever this follower attacks and destroys an enemy follower, if this follower is not destroyed, recover 2 play points and gain the ability to attack 2 times this turn."
#	 evolveRequireTarget = True
#
#	 def __init__(self, Game, ID):
#		 super().__init__(Game, ID)
#		 self.trigsBoard = [TriggerDiamondPaladin(self)]
#
#	 def effCanTrig(self):
#		 self.effectViable = self.getMana() != self.mana
#
#	 def getMana(self):
#		 if self.Game.Manas.manas[self.ID] >= 8:
#			 return 8
#		 else:
#			 return self.mana
#
#	 def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
#		 if choice == 8:
#			 self.getsStatus("Free Evolve")
#		 return None
#
#	 def inHandEvolving(self, target=None):
#		 if target:
#			 target.buffDebuff(-4, 0)
#			 PRINT(self, f"Diamond Paladin's Fanfare give {target.name} -4/-0.")
#		 return
#
#	 def extraTargetCorrect(self, target, affair):
#		 return target.cardType and target.cardType == "Minion" and target.ID != self.ID and target.onBoard
#
#
# class TriggerDiamondPaladin(TriggeronBoard):
#	 def __init__(self, entity):
#		 super().__init__(entity, ["MinionAttackedMinion"])
#
#	 def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
#		 return subject == self.entity and self.entity.onBoard and (target.health < 1 or target.dead == True) and \
#				(self.entity.health > 0 and self.entity.dead == False)
#
#	 def effect(self, signal, ID, subject, target, number, comment, choice=0):
#		 PRINT(self,
#			   "After %s attacks and kills minion %s, the player gains 10 Armor." % (self.entity.name, target.name))
#		 self.entity.getsStatus("Windfury")
#		 self.entity.Game.Manas.manas[self.entity.ID] += 2
#		 trigger = TriggerTurnEndDiamondPaladin(self.entity)
#		 self.entity.trigsBoard.append(trigger)
#		 if self.entity.onBoard:
#			 trigger.connect()
#
#
# class TriggerTurnEndDiamondPaladin(TriggeronBoard):
#	 def __init__(self, entity):
#		 super().__init__(entity, ["TurnEnds"])
#
#	 def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
#		 return self.entity.onBoard
#
#	 def effect(self, signal, ID, subject, target, number, comment, choice=0):
#		 self.entity.losesStatus("Windfury")
#		 for t in self.entity.trigsBoard:
#			 if type(t) == TriggerTurnEndDiamondPaladin:
#				 t.disconnect()
#				 self.entity.trigsBoard.remove(t)
#				 break
#
#
# """7 Cost"""
#
#
# class AccelerateRegalWildcat(AccelerateSpell):
#	 Class, school, name = "Swordcraft", "", "Regal Wildcat"
#	 requireTarget, mana = False, 4
#	 index = "Shadowverse~Swordcraft~Spell~4~~Regal Wildcat~Uncollectible"
#	 description = "Summon a Steelclad Knight, a Heavy Knight, and a Knight."
#
#	 def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
#		 PRINT(self, "Regal Wildcat's accelerate summons a 2/2 Steelclad Knight, a 1/2 Heavy Knight, and a 1/1 Knight.")
#		 self.Game.summonMinion([SteelcladKnight(self.Game, self.ID), HeavyKnight(self.Game, self.ID),
#								 Knight(self.Game, self.ID)], (-11, "totheRightEnd"), self.ID)
#		 return None
#
#
# class RegalWildcat(AccelerateMinion):
#	 Class, race, name = "Swordcraft", "Commander", "Regal Wildcat"
#	 mana, attack, health = 7, 4, 4
#	 index = "Shadowverse~Swordcraft~Minion~7~4~4~Commander~Regal Wildcat~Battlecry~Charge"
#	 requireTarget, keyWord, description = True, "Charge", "Accelerate (4): Summon a Steelclad Knight, a Heavy Knight, and a Knight.----------Storm.Fanfare: If at least 10 allied followers have been destroyed this match, give another allied follower +2/+2 and Storm."
#	 accelerate = 4
#
#	 def __init__(self, Game, ID):
#		 super().__init__(Game, ID)
#
#	 def effCanTrig(self):
#		 self.effectViable = (self.getMana() > self.accelerate or self.mana <= self.accelerate) and \
#							 self.Game.Counters.numMinionsDiedThisGame[
#								 self.ID] >= 10 or self.getMana() != self.mana
#
#	 def targetExists(self, choice=0):
#		 if (self.getMana() > self.accelerate or self.mana <= self.accelerate) and \
#				 self.Game.Counters.numMinionsDiedThisGame[self.ID] >= 10:
#			 return self.selectableFriendlyMinionExists(choice)
#		 return False
#
#	 def targetCorrect(self, target, choice=0):
#		 return target.cardType == "Minion" and target.ID == self.ID and target != self and target.onBoard
#
#	 def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
#		 if target is not None:
#			 PRINT(self, f"Regal Wildcat gives minion {target.name} +2/+2 and Storm.")
#			 target.buffDebuff(2, 2)
#			 target.getsStatus("Charge")
#		 return target
#
#	 def getAccelerateSpell(self):
#		 return AccelerateRegalWildcat(self.Game, self.ID)
#
#
# class FrontguardGeneral(SVMinion):
#	 Class, race, name = "Swordcraft", "Commander", "Frontguard General"
#	 mana, attack, health = 7, 5, 6
#	 index = "Shadowverse~Swordcraft~Minion~7~5~6~Commander~Fortress Guard~Taunt~Deathrattle"
#	 requireTarget, keyWord, description = False, "Taunt", "Ward.Last Words: Summon a Fortress Guard."
#
#	 def __init__(self, Game, ID):
#		 super().__init__(Game, ID)
#		 self.deathrattles = [DeathrattleFrontguardGeneral(self)]
#
#
# class DeathrattleFrontguardGeneral(Deathrattle_Minion):
#	 def effect(self, signal, ID, subject, target, number, comment, choice=0):
#		 PRINT(self, "Last Words: Summon a Fortress Guard.")
#		 self.entity.Game.summonMinion([FortressGuard(self.entity.Game, self.entity.ID)], (-11, "totheRightEnd"),
#									   self.entity.ID)
#
#
# class HonoredFrontguardGeneral(SVMinion):
#	 Class, race, name = "Swordcraft", "Commander", "Honored Frontguard General"
#	 mana, attack, health = 7, 5, 6
#	 index = "Shadowverse~Swordcraft~Minion~7~5~6~Commander~Honored Fortress Guard~Taunt~Deathrattle"
#	 requireTarget, keyWord, description = False, "Taunt", "Ward.Can't be targeted by enemy spells and effects.Last Words: Summon a Shield Guardian, and give it +X/+X. X equals the number of times that allied followers have evolved during this match."
#
#	 def __init__(self, Game, ID):
#		 super().__init__(Game, ID)
#		 self.deathrattles = [DeathrattleHonoredFrontguardGeneral(self)]
#		 self.marks["Enemy Effect Evasive"] = 1
#
#
# class DeathrattleHonoredFrontguardGeneral(Deathrattle_Minion):
#	 def effect(self, signal, ID, subject, target, number, comment, choice=0):
#		 evolved = self.entity.Game.Counters.numMinionsEvolvedThisGame[self.entity.ID]
#		 PRINT(self, f"Last Words: Summon a Shield Guardian, and give it +{evolved}/+{evolved}.")
#		 s = ShieldGuardian(self.entity.Game, self.entity.ID)
#		 self.entity.Game.summonMinion([s], (-11, "totheRightEnd"), self.entity.ID)
#		 s.buffDebuff(evolved, evolved)