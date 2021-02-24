"""Forged in the Barrens"""
#假设是随从受伤时触发，不是受伤之后触发
class Frenzy(TrigBoard):
	def __init__(self, entity):
		self.blank_init(entity, ["MinionTakesDmg"])
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.onBoard and target == self.entity and target.health > 0 and not target.dead
		
	def trig(self, signal, ID, subject, target, number, comment, choice=0):
		if self.canTrig(signal, ID, subject, target, number, comment):
			if self.entity.Game.GUI:
				self.entity.Game.GUI.trigBlink(self.entity)
			self.disconnect()
			try: self.entity.trigsBoard.remove(self)
			except: pass
			self.effect(signal, ID, subject, target, number, comment)
			
			
#So far the cards that upgrade when Mana Crystals are enough are all spells
class Trig_ForgeUpgrade(TrigHand):
	def __init__(self, entity, newCard, threshold):
		self.blank_init(entity, ["ManaXtlsCheck"])
		self.threshold = threshold
		self.newCard = newCard
		
	def canTrig(self, signal, ID, subject, target, number, comment, choice=0):
		return self.entity.inHand and ID == self.entity.ID and self.entity.Game.Manas.manasUpper[self.entity.ID] >= self.threshold
		
	def text(self, CHN):
		return "如果玩家的法力水晶为%d，便升级"%self.threshold if CHN else "When player's Mana Crystals is %d, upgrades"%self.threshold
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		card = self.entity
		newCard = self.newCard(card.Game, card.ID)
		for key, value in newCard.keyWords.items(): #Find keywords the new card doesn't have
			if value < 1 and card.keyWords[key] > 0: newCard.keyWords[key] = 1
		for key, value in newCard.marks.items():
			try:
				if value < 1 and card.marks[key] > 0: newCard.marks[key] = 1
			except: pass
		#Inhand triggers and mana modifications
		newCard.trigsHand += [trig for trig in card.trigsHand if not isinstance(trig, Trig_Corrupt)]
		newCard.manaMods = [manaMod.selfCopy(newCard) for manaMod in card.manaMods]
		card.Game.Hand_Deck.replaceCardinHand(card, newCard)
		
		
class Peon(Minion):
	Class, race, name = "Neutral", "", "Peon"
	mana, attack, health = 2, 2, 3
	index = "Barrens~Neutral~Minion~2~2~3~~Peon"
	requireTarget, keyWord, description = False, "", "Frenzy: Add a random spell from your class to your hand"
	name_CN = "苦工"
	poolIdentifier = "Druid Spells"
	@classmethod
	def generatePool(cls, Game):
		return [Class+" Spells" for Class in Game.Classes], \
				[[value for key, value in Game.ClassCards[Class].items() if "~Spell~" in key] for Class in Game.Classes]
				
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_Peon(self)]
		
class Trig_BlademasterSamuro(Frenzy):
	def text(self, CHN):
		return "暴怒：随机将一张你的职业的法术牌置入你的手牌" if CHN else "Frenzy: Add a random spell from your class to your hand"
				
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		minion = self.entity
		curGame = self.entity.Game
		if curGame.mode == 0:
			pool = self.rngPool(curGame.heroes[self.entity.ID].Class + " Spells")
			if curGame.guides:
				spells = curGame.guides.pop(0)
			else:
				spells = npchoice(pool)
				curGame.fixedGuides.append(tuple(spells))
			curGame.Hand_Deck.addCardtoHand(spells, self.entity.ID, byType=True, creator=type(self.entity), possi=pool)
			
			
class Mankrik(Minion):
	Class, race, name = "Neutral", "", "Mankrik"
	mana, attack, health = 3, 3, 4
	index = "Barrens~Neutral~Minion~3~3~4~~Mankrik~Battlecry~Legendary"
	requireTarget, keyWord, description = False, "", "Battlecry: Help Mankrik find his wife! She was last seen somewhere in your deck"
	name_CN = "曼克里克"
	
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		self.Game.Hand_Deck.shuffleintoDeck(MankriksWife(self.Game, self.ID), creator=self)
		return None
		
class MankriksWife(Spell):
	
class BlademasterSamuro(Minion):
	Class, race, name = "Neutral", "", "Blademaster Samuro"
	mana, attack, health = 4, 1, 6
	index = "Barrens~Neutral~Minion~4~1~6~~Blademaster Samuro~Rush~Legendary"
	requireTarget, keyWord, description = False, "Rush", "Rush. Frenzy: Deal damage equal to this minion's Attack equal to all enemy minions"
	name_CN = "剑圣萨穆罗"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_BlademasterSamuro(self)]
		
class Trig_BlademasterSamuro(Frenzy):
	def text(self, CHN):
		return "暴怒：对所有敌方随从造成等同于该随从的攻击力的伤害" if CHN \
				else "Frenzy: Deal damage equal to this minion's Attack equal to all enemy minions"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		minion = self.entity
		targets = minion.Game.minionsonBoard(3-minion.ID)
		minion.dealsAOE(targets, [minion.attack]*len(targets))
		
		
class SpiritHealer(Minion):
	Class, race, name = "Neutral", "", "Spirit Healer"
	mana, attack, health = 4, 3, 5
	index = "Barrens~Neutral~Minion~4~3~5~~Spirit Healer"
	requireTarget, keyWord, description = False, "", "After you cast Holy spell, give a friendly minion +2 Health"
	name_CN = "灵魂医者"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_SpiritHealer(self)]
		
class Trig_SpiritHealer(Frenzy):
	def text(self, CHN):
		return "在你施放一个神圣法术后，随机使一个友方随从获得+2生命值" if CHN \
				else "After you cast Holy spell, give a friendly minion +2 Health"
				
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		curGame, ID = self.entity.Game, self.entity.ID
		if curGame.mode == 0:
			if curGame.guides:
				i = curGame.guides.pop(0)
			else:
				minions = curGame.minionsonBoard[ID]
				i = npchoice(minions).pos if minions else -1
				curGame.fixedGuides.append(i)
			if i > -1: curGame.minions[self.entity.ID][i].buffDebuff(0, 2)
			
			
class ShadowHunterVoljin(Minion):
	Class, race, name = "Neutral", "", "Shadow Hunter Vol'jin"
	mana, attack, health = 5, 3, 6
	index = "Barrens~Neutral~Minion~5~3~6~~Shadow Hunter Vol'jin~Battlecry~Legendary"
	requireTarget, keyWord, description = True, "", "Battlecry: Choose a minion. Swap it with a random one in its owners hand"
	name_CN = "暗影猎手沃金"
	
	def targetExists(self, choice=0):
		return self.selectableMinionExists()
		
	def targetCorrect(self, target, choice=0):
		return target.type == "Minion" and target != self and target.onBoard
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		if target and not target.dead and target.onBoard: #战吼触发时自己不能死亡。
			#假设对方手牌中没有随从时不能交换
			curGame, ID = self.Game, target.ID
			if curGame.mode == 0:
				if curGame.guides:
					i = curGame.guides.pop(0)
				else:
					minions = [i for i, card in enumerate(curGame.Hand_Deck.hands(ID)) if card.type == "Minion"]
					i = npchoice(minions) if minions else -1
					curGame.fixedGuides.append(i)
				if i > -1: 
					minion, pos = curGame.Hand_Deck.hands[ID][i], target.pos
					minion.disappears(deathrattlesStayArmed=False)
					curGame.removeMinionorWeapon(minion)
					minion.reset(ID)
					#下面节选自Hand.py的addCardtoHand方法，但是要跳过手牌已满的检测
					ownHand.append(minion)
					minion.entersHand()
					curGame.sendSignal("CardEntersHand", minion, None, [minion], 0, "")
					#假设先发送牌进入手牌的信号，然后召唤随从
					curGame.summonfrom(i, ID, pos, self.entity, fromHand=True)
		return target
		
		
"""Druid cards"""
class DruidofthePlains(Minion):
	Class, race, name = "Druid", "Beast", "Druid of the Plains"
	mana, attack, health = 7, 7, 6
	index = "Barrens~Druid~Minion~7~7~6~Beast~Druid of the Plains~Rush"
	requireTarget, keyWord, description = False, "Rush", "Rush. Frenzy: Transform into a 6/7 Kodo with Taunt"
	name_CN = "平原德鲁伊"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_DruidofthePlains(self)]
		
class Trig_DruidofthePlains(Frenzy):
	def text(self, CHN):
		return "暴怒：变形成一只6/7并具有嘲讽的科多兽" if CHN else "Frenzy: Transform into a 6/7 Kodo with Taunt"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		self.entity.Game.transform(self.entity, )
		
class Kodo(Minion):
	Class, race, name = "Druid", "Beast", "Druid of the Plains"
	mana, attack, health = 7, 6, 7
	index = "Barrens~Druid~Minion~7~6~7~Beast~Druid of the Plains~Taunt~Uncollectible"
	requireTarget, keyWord, description = False, "Taunt", "Taunt"
	name_CN = "科多兽"
	
	
class SunscaleRaptor(Minion):
	Class, race, name = "Hunter", "Beast", "Sunscale Raptor"
	mana, attack, health = 1, 1, 3
	index = "Barrens~Hunter~Minion~1~1~3~Beast~Sunscale Raptor"
	requireTarget, keyWord, description = False, "", "Frenzy: Shuffle a Sunscale Raptor into your deck with permanent +1/+1"
	name_CN = "赤鳞迅猛龙"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsBoard = [Trig_SunscaleRaptor(self)]
		
class Trig_SunscaleRaptor(Frenzy):
	def text(self, CHN):
		return "暴怒：将一张赤鳞迅猛龙洗入你的牌库并使其永久获得+1/+1" if CHN \
				else "Frenzy: Shuffle a Sunscale Raptor into your deck with permanent +1/+1"
		
	def effect(self, signal, ID, subject, target, number, comment, choice=0):
		game, stat = self.entity.Game, number
		newIndex = "Barrens~Hunter~Minion~1~%d~%d~Beast~Sunscale Raptor~Uncollectible"%(stat, stat)
		subclass = type("HonorStudent_Mutable_%d"%stat, (HonorStudent_Mutable_1, ),
						{"attack": stat, "health": stat, "index": newIndex}
						)
		game.cardPool[newIndex] = subclass
		game.Hand_Deck.shuffleintoDeck(subclass(game, self.entity.ID), creator=self.entity)
		
"""Priest Cards"""
class DesperatePrayer(Spell):
	Class, school, name = "Priest", "Holy", "Desperate Prayer"
	requireTarget, mana = False, 0
	index = "Barrens~Priest~Spell~2~Holy~Desperate Prayer"
	description = "Restore 5 Health to each hero"
	name_CN = "绝望祷言"
	def text(self, CHN):
		heal = 5 * (2 ** self.countHealDouble())
		return "为双方英雄恢复%d点生命值"%heal if CHN else "Restore %d health to each hero"%heal
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=-2):
		heal = 5 * (2 ** self.countHealDouble())
		self.restoresAOE([hero for hero in self.Game.heroes.values()], [heal]*2)
		return None
		
"""Shaman Cards"""
class ChainLightningRank1(Spell):
	Class, school, name = "Shaman", "Nature", "Chain Lightning (Rank 1)"
	requireTarget, mana = True, 2
	index = "Darkmoon~Shaman~Spell~2~Nature~Chain Lightning (Rank 1)"
	description = "Deal 2 damage to a minion and a random adjacent one. (Upgrades when you have 5 mana.)"
	name_CN = "闪电链（等级1）"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsHand = [Trig_ForgeUpgrade(self, ChainLightningRank2, 5)] #只有在手牌中才会升级
		
	def entersHand(self):
		return ChainLightningRank2(self.Game, self.ID) if self.Game.Manas.manasUpper[self.ID] > 4 else self
		
	def text(self, CHN):
		damage = (2 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		return "对一个随从和随机一个相邻随从造成%d点伤害（当你有5点法力值时升级)"%damage if CHN else "Deal %d damage to a minion and a random adjacent one. (Upgrades when you have 5 mana.)"%damage
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if target:
			damage = (2 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			curGame = self.Game
			if curGame.mode == 0:
				if curGame.guides:
					i = curGame.guides.pop(0)
				else:
					neighbors = curGame.neighbors2(target)[0]
					i = npchoice(neighbors).pos if neighbors else -1
					curGame.fixedGuides.append(i)
				if i > -1:
					self.dealsAOE([target, curGame.minions[target.ID][i]], [damage]*2)
				else:
					self.dealsDamage(target, damage)
		return target
		
class ChainLightningRank2(Spell):
	Class, school, name = "Shaman", "Nature", "Chain Lightning (Rank 2)"
	requireTarget, mana = True, 2
	index = "Darkmoon~Shaman~Spell~2~Nature~Chain Lightning (Rank 2)~Uncollectible"
	description = "Deal 3 damage to a minion and a random adjacent one. (Upgrades when you have 10 mana.)"
	name_CN = "闪电链（等级2）"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsHand = [Trig_ForgeUpgrade(self, ChainLightningRank2, 10)] #只有在手牌中才会升级
		
	def entersHand(self):
		return ChainLightningRank2(self.Game, self.ID) if self.Game.Manas.manasUpper[self.ID] > 9 else self
		
	def text(self, CHN):
		damage = (3 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		return "对一个随从和随机一个相邻随从造成%d点伤害（当你有5点法力值时升级)"%damage if CHN else "Deal %d damage to a minion and a random adjacent one. (Upgrades when you have 5 mana.)"%damage
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if target:
			damage = (3 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			curGame = self.Game
			if curGame.mode == 0:
				if curGame.guides:
					i = curGame.guides.pop(0)
				else:
					neighbors = curGame.neighbors2(target)[0]
					i = npchoice(neighbors).pos if neighbors else -1
					curGame.fixedGuides.append(i)
				if i > -1:
					self.dealsAOE([target, curGame.minions[target.ID][i]], [damage]*2)
				else:
					self.dealsDamage(target, damage)
		return target
		
class ChainLightningRank3(Spell):
	Class, school, name = "Shaman", "Nature", "Chain Lightning (Rank 3)"
	requireTarget, mana = True, 2
	index = "Darkmoon~Shaman~Spell~2~Nature~Chain Lightning (Rank 3)~Uncollectible"
	description = "Deal 4 damage to a minion and a random adjacent one"
	name_CN = "闪电链（等级3）"
	def text(self, CHN):
		damage = (4 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
		return "对一个随从和随机一个相邻随从造成%d点伤害"%damage if CHN else "Deal %d damage to a minion and a random adjacent one"%damage
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		if target:
			damage = (4 + self.countSpellDamage()) * (2 ** self.countDamageDouble())
			curGame = self.Game
			if curGame.mode == 0:
				if curGame.guides:
					i = curGame.guides.pop(0)
				else:
					neighbors = curGame.neighbors2(target)[0]
					i = npchoice(neighbors).pos if neighbors else -1
					curGame.fixedGuides.append(i)
				if i > -1:
					self.dealsAOE([target, curGame.minions[target.ID][i]], [damage]*2)
				else:
					self.dealsDamage(target, damage)
		return target
		
		
class Brukan(Minion):
	Class, race, name = "Shaman", "", "Bru'kan"
	mana, attack, health = 4, 5, 4
	index = "Barrens~Shaman~Minion~4~5~4~~Bru'kan~Nature Spell Damage~Legendary"
	requireTarget, keyWord, description = False, "Nature Spell Damage", "Nature Spell Damage +3"
	name_CN = "布鲁坎"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.keyWords["Nature Spell Damage"] = 3
		
		
		
"""Warlock Cards"""
class ImpSwarmRank1(Spell):
	Class, school, name = "Warlock", "Fel", "Imp Swarm (Rank 1)"
	requireTarget, mana = False, 2
	index = "Barrens~Warlock~Spell~2~Fel~Imp Swarm (Rank 1)"
	description = "Summon a 3/2 Imp. (Upgrades when you have 5 mana.)"
	name_CN = "小鬼集群（等级1）"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsHand = [Trig_ForgeUpgrade(self, ImpSwarmRank2, 5)] #只有在手牌中才会升级
		
	def entersHand(self):
		return ImpSwarmRank2(self.Game, self.ID) if self.Game.Manas.manasUpper[self.ID] > 4 else self
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		self.Game.summon(ImpFamiliar(self.Game, self.ID), -1, self)
		return None
		
class ImpFamiliar(Minion):
	Class, race, name = "Warlock", "Demon", "Imp Familiar"
	mana, attack, health = 2, 3, 2
	index = "Barrens~Warlock~Minion~2~3~2~Demon~Imp Familiar~Uncollectible"
	requireTarget, keyWord, description = False, "", ""
	name_CN = ""
	
class ImpSwarmRank2(Spell):
	Class, school, name = "Warlock", "Fel", "Imp Swarm (Rank 2)"
	requireTarget, mana = False, 2
	index = "Barrens~Warlock~Spell~2~Fel~Imp Swarm (Rank 2)~Uncollectible"
	description = "Summon two 3/2 Imps. (Upgrades when you have 10 Mana.)"
	name_CN = "小鬼集群（等级2）"
	def __init__(self, Game, ID):
		self.blank_init(Game, ID)
		self.trigsHand = [Trig_ForgeUpgrade(self, ImpSwarmRank3, 10)] #只有在手牌中才会升级
		
	def entersHand(self):
		return ImpSwarmRank3(self.Game, self.ID) if self.Game.Manas.manasUpper[self.ID] > 9 else self
		
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		self.Game.summon([ImpFamiliar(self.Game, self.ID) for i in range(2)], (-1, "totheRightEnd"), self)
		return None
		
class ImpSwarmRank3(Spell):
	Class, school, name = "Warlock", "Fel", "Imp Swarm (Rank 3)"
	requireTarget, mana = False, 2
	index = "Barrens~Warlock~Spell~2~Fel~Imp Swarm (Rank 3)~Uncollectible"
	description = "Summon three 3/2 Imps"
	name_CN = "小鬼集群（等级3）"
	def whenEffective(self, target=None, comment="", choice=0, posinHand=0):
		self.Game.summon([ImpFamiliar(self.Game, self.ID) for i in range(3)], (-1, "totheRightEnd"), self)
		return None
		