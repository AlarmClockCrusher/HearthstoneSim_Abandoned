from CustomWidgets import *

import numpy as np

class MulliganFinishButton_1P(tk.Button):
	def __init__(self, GUI):
		tk.Button.__init__(self, relief=tk.FLAT, master=GUI.GamePanel, text="Replace Card and\nStart 1st Turn", bg="green3", width=13, height=3, font=("Yahei", 12, "bold"))
		self.GUI = GUI
		self.bind("<Button-1>", self.respond)
		
	def respond(self, event):
		print("----Start game---")
		indices1 = [i for i, status in enumerate(self.GUI.mulliganStatus[1]) if status]
		indices2 = [i for i, status in enumerate(self.GUI.mulliganStatus[2]) if status]
		#self.GUI.gameBackup = self.GUI.Game.copyGame()[0]
		print("After game starting, GUI's current game is ", self.GUI.Game, "\nCopied gamebackup is", self.GUI.gameBackup)
		self.GUI.initGameDisplay()
		self.GUI.update()
		self.GUI.Game.Hand_Deck.mulligan(indices1, indices2)
		self.GUI.gameBackup = self.GUI.Game.copyGame()[0]
		
	def plot(self, x, y):
		self.place(x=x, y=y, anchor='c')
		self.GUI.btnsDrawn.append(self)
		
		
class MulliganFinishButton_2PGUI(tk.Button):
	def __init__(self, GUI):
		tk.Button.__init__(self, master=GUI.GamePanel, text="Replace Card", bg="green3", width=13, height=3, font=("Yahei", 12, "bold"))
		self.GUI = GUI
		self.configure(command=self.respond)
		
	def respond(self):
		ID, game = self.GUI.ID, self.GUI.Game
		indices = [i for i, status in enumerate(self.GUI.mulliganStatus) if status]
		game.Hand_Deck.mulligan1Side(ID, indices) #之后生成一个起手调度信息
		guides = [type(game.heroes[ID]), [type(card) for card in game.Hand_Deck.hands[ID]], [type(card) for card in game.Hand_Deck.decks[ID]]]
		if ID == 1: #1号玩家调度结束的时候需要把信息传给2号玩家
			s = pickleObj2Str("DefineGame")+"||"+pickleObj2Str((self.GUI.monk, self.GUI.SV, self.GUI.boardID, guides))
			self.GUI.window.clipboard_clear()
			self.GUI.window.clipboard_append(s)
			self.GUI.info4Opponent.config(text=s)
		else: # 2号玩家需要在换牌之后把游戏信息传回给1。
			self.GUI.deckImportPanel.destroy()
			self.GUI.initGameDisplay()
			self.GUI.btnGenInfo.pack()
			self.GUI.update()
			#看来问题出在这个startGame里面，之前的btnsDrawn很正常
			game.Hand_Deck.startGame() #把2号玩家的手牌和牌库扳机等注册，并开始2号玩家的游戏
			s = pickleObj2Str("P1CanStartGame")+"||"+pickleObj2Str(guides)
			self.GUI.window.clipboard_clear()
			self.GUI.window.clipboard_append(s)
			self.GUI.info4Opponent.config(text=s)
		if self.GUI.showReminder.get():
			messagebox.showinfo(message=txt("Your deck and hand have been decided. Send the info to the opponent", CHN))
		self.destroy()
		
	def plot(self, x, y):
		self.place(x=x, y=y, anchor='c')
		self.GUI.btnsDrawn.append(self)
		
		
class ListboxPanel(tk.Frame):
	def __init__(self, GUI, master):
		self.GUI = GUI
		super().__init__(master=master)
		scrollbar_ver = tk.Scrollbar(master=self) #Horizontal scroll bars need orient="horizontal"
		self.listbox = tk.Listbox(master=self, width=14, height=2, bg="white", font=("Yahei", 10),
							yscrollcommand=scrollbar_ver.set)
		self.listbox.pack(fill=tk.Y, side=tk.LEFT)
		scrollbar_ver.pack(fill=tk.Y, side=tk.LEFT)
		scrollbar_ver.configure(command=self.listbox.yview)
		
	def delete(self, start, end):
		self.listbox.delete(start, end)
		
	def insert(self, start, string):
		self.listbox.insert(start, string)
		
class DeckGravePanel(tk.Frame):
	def __init__(self, GUI):
		self.GUI = GUI
		tk.Frame.__init__(self, master=self.GUI.sidePanel)
		if hasattr(self.GUI, "ID"):
			if self.GUI.ID != 1: player1, player2 = "对方的", "你的"
			else: player1, player2 = "你的", "对方的"
		else: player1, player2 = "玩家1的", "玩家2的"
		tk.Button(self, text="%s's deck&grave"%player1, font=("Yahei", 11, "bold"), 
					command=lambda : self.showDeckGrave(1)).grid(row=0, column=0)
		tk.Button(self, text="%s's deck&grave"%player2, font=("Yahei", 11, "bold"), 
					command=lambda : self.showDeckGrave(2)).grid(row=0, column=1)
		tk.Button(self, text="Clear", font=("Yahei", 11, "bold"), 
					command=lambda : self.clear()).grid(row=1, column=0, columnspan=2)
		tk.Label(self, text="Resources with certainty", font=("Yahei", 10)).grid(row=2, column=0)
		tk.Label(self, text="Resources with possibilities", font=("Yahei", 10)).grid(row=2, column=1)
		tk.Label(self, text="Cards in hand", font=("Yahei", 10)).grid(row=4, column=0)
		tk.Label(self, text="Graveyard", font=("Yahei", 10)).grid(row=4, column=1)
		self.lbx_cards_1Possi = ListboxPanel(self.GUI, self)
		self.lbx_cards_XPossi = ListboxPanel(self.GUI, self)
		self.lbx_trackedHands = ListboxPanel(self.GUI, self)
		self.lbx_Graveyard = ListboxPanel(self.GUI, self)
		self.lbx_cards_1Possi.grid(row=3, column=0)
		self.lbx_cards_XPossi.grid(row=3, column=1)
		self.lbx_trackedHands.grid(row=5, column=0)
		self.lbx_Graveyard.grid(row=5, column=1)
		
	def showDeckGrave(self, ID):
		HD = self.GUI.Game.Hand_Deck
		self.clear()
		img = PIL.Image.open(r"Images\PyHSIcon.png").resize((75, 75))
		ph = PIL.ImageTk.PhotoImage(img)
		self.GUI.lbl_Card.config(image=ph)
		self.GUI.lbl_Card.image = ph
		self.lbx_cards_1Possi.listbox.config(height=13)
		self.lbx_cards_XPossi.listbox.config(height=13)
		self.lbx_trackedHands.listbox.config(height=13)
		self.lbx_Graveyard.listbox.config(height=13)
		cardPool = self.GUI.Game.cardPool
		if CHN:
			print("cards_1Possi", HD.cards_1Possi[ID])
			print("cards_XPossi", HD.cards_XPossi[ID])
			print("trackedHands", HD.trackedHands[ID])
			for tup in HD.cards_1Possi[ID]:
				if tup[0]: self.lbx_cards_1Possi.insert(tk.END, "{}->{}"%format(tup[0].name_CN, tup[1][0].name_CN))
				else: self.lbx_cards_1Possi.insert(tk.END, tup[1][0].name_CN)
			for tup in HD.cards_XPossi[ID]:
				self.lbx_cards_XPossi.insert(tk.END, "创建者：{}"%format(tup[0].name_CN))
				for p in tup[1]: self.lbx_cards_XPossi.insert(tk.END, "    {}"%format(p.name_CN))
			for tup in HD.trackedHands[ID]:
				if tup[0]:
					if len(tup[1]) == 1: self.lbx_trackedHands.insert(tk.END, "{}->{}"%format(tup[0].name_CN, tup[1][0].name_CN))
					else: self.lbx_trackedHands.insert(tk.END, "创建者：{}"%format(tup[0].name_CN))
				else:
					for p in tup[1]: self.lbx_trackedHands.insert(tk.END, "    {}"%format(p.name_CN))
			for index in self.GUI.Game.Counters.minionsDiedThisGame[ID]:
				self.lbx_Graveyard.insert(tk.END, cardPool[index].name_CN)
		else:
			for tup in HD.cards_1Possi[ID]:
				if tup[0]: self.lbx_cards_1Possi.insert(tk.END, "{}->{}"%format(tup[0].name, tup[1][0].name))
				else: self.lbx_cards_1Possi.insert(tk.END, tup[1][0].name)
			for tup in HD.cards_XPossi[ID]:
				self.lbx_cards_XPossi.insert(tk.END, "Created by {}"%format(tup[0].name))
				for p in tup[1]: self.lbx_cards_XPossi.insert(tk.END, "    {}"%format(p.name))
			for tup in HD.trackedHands[ID]:
				if tup[0]:
					if len(tup[1]) == 1: self.lbx_trackedHands.insert(tk.END, "{}->{}"%format(tup[0].name, tup[1][0].name))
					else: self.lbx_trackedHands.insert(tk.END, "Created by {}"%format(tup[0].name))
				else:
					for p in tup[1]: self.lbx_trackedHands.insert(tk.END, "    {}"%format(p.name))
			for index in self.GUI.Game.Counters.minionsDiedThisGame[ID]:
				self.lbx_Graveyard.insert(tk.END, cardPool[index].name)
				
	def clear(self):
		self.lbx_cards_1Possi.delete(0, tk.END)
		self.lbx_cards_XPossi.delete(0, tk.END)
		self.lbx_trackedHands.delete(0, tk.END)
		self.lbx_Graveyard.delete(0, tk.END)
		self.lbx_cards_1Possi.listbox.config(height=2)
		self.lbx_cards_XPossi.listbox.config(height=2)
		self.lbx_trackedHands.listbox.config(height=2)
		self.lbx_Graveyard.listbox.config(height=2)
		
		
class GUI_Common:
	def printInfo(self, string):
		pass
		
	def initGameDisplay(self):
		self.canvas = BoardButton(self)
		self.canvas.plot()
		#handZones, boardZones, secretZones不会实际添加到界面上
		self.handZones = {1: HandZone(self, 1), 2: HandZone(self, 2)}
		self.boardZones = {1: BoardZone(self, 1), 2: BoardZone(self, 2)}
		self.heroZones = {1: HeroZone(self, 1), 2: HeroZone(self, 2)}
		self.secretZones = {1: SecretZone(self, 1), 2: SecretZone(self, 2)}
		self.manaZones = {1: ManaZone(self, 1), 2: ManaZone(self, 2)}
		self.deckZones = {1: DeckZone(self, 1), 2: DeckZone(self, 2)}
		self.offBoardTrigs = {1: None, 2: None}
		
		if hasattr(self, "ID"): ownID, enemyID = self.ID, 3 - self.ID
		else: ownID, enemyID = 1, 2
		self.secretZones[ownID].place(x=int(0.2*X), y=int(0.74*Y), anchor='c')
		self.secretZones[enemyID].place(x=int(0.2*X), y=int(0.26*Y), anchor='c')
		self.manaZones[ownID].place(x=int(0.77*X), y=int(0.75*Y), anchor='c')
		self.manaZones[enemyID].place(x=int(0.77*X), y=int(0.25*Y), anchor='c')
		self.deckZones[ownID].plot()
		self.deckZones[enemyID].plot()
		self.UI = 0
		
	def initSidePanel(self):
		self.btn_ViewCollection = tk.Button(self.sidePanel, text=txt("View Collectible Card", CHN), 
											command=lambda: CardCollectionWindow(self), bg="green3", font=("Yahei", 12))
		self.deckGravePanel = DeckGravePanel(self)
		print("Draw view collection button")
		self.btn_ViewCollection.pack()
		self.lbl_Card.pack()
		self.deckGravePanel.pack()
		
	def cancelSelection(self):
		if self.UI < 3 and self.UI > -1: #只有非发现状态,且游戏不在结算过程中时下才能取消选择
			self.subject, self.target = None, None
			self.UI, self.pos, self.choice = 0, -1, -1
			self.selectedSubject = ""
			for btn in reversed(self.btnsDrawn):
				if isinstance(btn, ChooseOneButton): btn.remove()
			self.resetCardColors()
			for card in self.Game.Hand_Deck.hands[1] + self.Game.Hand_Deck.hands[2] + [self.Game.powers[1]] + [self.Game.powers[2]]:
				if hasattr(card, "targets"): card.targets = []
				
	def wrapText(self, text, lengthLimit=10):
		if len(text) > lengthLimit: #"Savannah Highmane"
			lines, string, words = "", '', text.split(' ')
			for i in range(len(words)): #words = ["Savannah", "Highmane"]
				if string == '': #string为空时，遇到一段文字之后，无论如何都要记录下来，因为这里
					string += words[i] # string += "Savannah"
				else: #如果string不是空的话，则需要判断这个string加上下个单词之后是否会长度过长
					if len(string + words[i]) > lengthLimit: #len("Savannah" + "Highmane") > lengthLimit
						lines += string+'\n' #lines += "Savannah\n"
						string = words[i]
					else: #If including the next word won't make it too long.
						string += ' ' + words[i]
			lines += (string)
			return lines
		return text
		
	def update(self):
		try: self.lbl_CardStatus.destroy()
		except: pass
		if self.UI == -2: #Draw the mulligan part, the cards and the start turn button
			self.printInfo("The game starts. Select the cards you want to replace. Then click the button at the center of the screen")
			if hasattr(self, "ID"):
				self.mulliganStatus = [0] * len(self.Game.mulligans[self.ID])
				for i, card in enumerate(self.Game.mulligans[self.ID]):
					pos = (100+i*2*111, Y-140)
					MulliganButton(self, card).plot(x=pos[0], y=pos[1])
				MulliganFinishButton_2PGUI(self).plot(x=X/2, y=Y/2)
			else:
				for ID in range(1, 3):
					for i, card in enumerate(self.Game.mulligans[ID]):
						pos = (100+i*2*111, Y-140) if ID == 1 else (100+i*2*111, 140)
						MulliganButton(self, card).plot(x=pos[0], y=pos[1])
				MulliganFinishButton_1P(self).plot(x=X/2, y=Y/2)
		else:
			if self.UI == 1:
				for i, option in enumerate(self.Game.options):
					pos = (0.2*X+0.125*X*i, 0.5*Y)
					ChooseOneButton(self, option, "green3" if option.available() else "red").plot(x=pos[0], y=pos[1])
			else:
				for btn in reversed(self.btnsDrawn):
					try: btn.remove()
					except: btn.destroy()
				self.btnsDrawn = []
				for ID in range(1, 3):
					self.handZones[ID].draw()
					self.boardZones[ID].draw()
					self.heroZones[ID].draw()
					self.manaZones[ID].draw()
					self.secretZones[ID].draw()
					self.deckZones[ID].draw()
				self.canvas.draw()
				
			if not hasattr(self, "ID"): TurnEndButton(self).plot(x=int(0.95*X), y=int(0.58*Y) if self.Game.turn == 1 else int(0.42*Y))
			elif self.ID == self.Game.turn: TurnEndButton(self).plot(x=int(0.95*X), y=int(0.5*Y))
			
		if self.Game.gameEnds > 0:
			gameEndMsg = {1: "Player 2 Wins", 2: "Player 1 Wins", 3: "Both Players Died"}[self.Game.gameEnds]
			self.UI = -1
			tk.Label(self.GamePanel, text=gameEndMsg, bg="white", fg="red", font=("Yahei", 30, "bold")).place(relx=0.5, rely=0.5, anchor='c')
			
	def resetCardColors(self):
		for ID in range(1, 3):
			for btn in self.boardZones[ID].btnsDrawn + self.heroZones[ID].btnsDrawn + self.handZones[ID].btnsDrawn + self.btnsDrawn:
				try: btn.decideColorOrig(self, btn.card)
				except: pass
				btn.configure(bg=btn.colorOrig)
		self.canvas.configure(bg=BoardColor)
		
	def highlightTargets(self, legalTargets):
		for ID in range(1, 3):
			for btn in self.boardZones[ID].btnsDrawn + self.heroZones[ID].btnsDrawn:
				if btn.card in legalTargets: btn.config(bg="cyan2")
				
	def resolveMove(self, entity, button, selectedSubject, info=None):
		game = self.Game
		if self.UI < 0: pass
		elif self.UI == 0:
			self.resetCardColors()
			if selectedSubject == "Board": #Weapon won't be resolved by this functioin. It automatically cancels selection
				self.printInfo("Board is not a valid subject.")
				self.cancelSelection()
			elif selectedSubject == "TurnEnds":
				self.cancelSelection()
				self.subject, self.target = None, None
				game.switchTurn()
				self.update()
				if hasattr(self, "sock"):
					print("Turn ends . Send the info to server")
					self.sendEndTurnthruServer()
			elif entity.ID != game.turn or (hasattr(self, "ID") and entity.ID != self.ID):
				self.printInfo("You can only select your own characters as subject.")
				self.cancelSelection()
			else: #选择的是我方手牌、我方英雄、我方英雄技能、我方场上随从，
				self.subject, self.target = entity, None
				self.selectedSubject = selectedSubject
				self.UI, self.choice = 2, 0 #选择了主体目标，则准备进入选择打出位置或目标界面。抉择法术可能会将界面导入抉择界面。
				button.selected = 1 - button.selected
				button.configure(bg="white")
				if selectedSubject.endswith("inHand"): #Choose card in hand as subject
					if not game.Manas.affordable(entity): #No enough mana to use card
						self.cancelSelection()
					else: #除了法力值不足，然后是指向性法术没有合适目标和随从没有位置使用
						typewhenPlayed = self.subject.getTypewhenPlayed()
						if typewhenPlayed == "Spell" and not entity.available():
							#法术没有可选目标，或者是不可用的非指向性法术
							self.printInfo("Selected spell unavailable. All selection canceled.")
							self.cancelSelection()
						elif game.space(entity.ID) < 1 and (typewhenPlayed == "Minion" or typewhenPlayed == "Amulet"): #如果场上没有空位，且目标是护符或者无法触发激奏的随从的话，则不能打出牌
							self.printInfo("The board is full and minion/amulet selected can't be played")
							self.cancelSelection()
						else:
							if entity.chooseOne > 0:
								if game.status[entity.ID]["Choose Both"] > 0:
									self.choice = -1 #跳过抉择，直接进入UI=1界面。
									if entity.needTarget(-1):
										self.highlightTargets(entity.findTargets("", self.choice)[0])
								else:
									game.options = entity.options
									self.UI = 1 #进入抉择界面，退出抉择界面的时候已经self.choice已经选好。
									self.update()
							#如果选中的手牌是一个需要选择目标的SV法术
							elif entity.index.startswith("SV_") and typewhenPlayed == "Spell" and entity.needTarget():
								self.choice = 0
								game.Discover.startSelect(entity, entity.findTargets("")[0])
							#选中的手牌是需要目标的炉石卡
							elif (typewhenPlayed != "Weapon" and entity.needTarget()) or (typewhenPlayed == "Weapon" and entity.requireTarget):
								self.highlightTargets(entity.findTargets("", self.choice)[0])
				#不需目标的英雄技能当即使用。需要目标的进入目标选择界面。暂时不用考虑技能的抉择
				elif selectedSubject == "Power":
					if entity.name == "Evolve":
						self.selectedSubject = "Power"
						game.Discover.startSelect(entity, entity.findTargets("")[0])
					#英雄技能会自己判定是否可以使用。
					elif entity.needTarget(): #selectedSubject之前是"Hero Power 1"或者"Hero Power 2"
						self.selectedSubject = "Power"
						self.highlightTargets(entity.findTargets("", self.choice)[0])
					else:
						self.printInfo("Request to use Hero Power {}".format(self.subject.name))
						subject = self.subject
						self.cancelSelection()
						self.subject, self.target, self.UI = subject, None, -1
						subject.use(None) #Whether the Hero Power is used or not is handled in the use method.
						self.subject, self.target, self.UI = None, None, 0
						self.update()
						if hasattr(self, "sock"):
							self.sendOwnMovethruServer()
				#不能攻击的随从不能被选择。
				elif selectedSubject.endswith("onBoard"):
					if not entity.canAttack(): self.cancelSelection()
					else: self.highlightTargets(entity.findBattleTargets()[0])
					
		elif self.UI == 1:
			if selectedSubject == "ChooseOneOption" and entity.available():
				#The first option is indexed as 0.
				index = game.options.index(entity)
				self.printInfo("Choice {} chosen".format(entity.name))
				self.UI, self.choice = 2, index
				for btn in reversed(self.btnsDrawn):
					if isinstance(btn, ChooseOneButton): btn.remove()
				if self.subject.needTarget(self.choice):
					self.highlightTargets(self.subject.findTargets("", self.choice)[0])
			elif selectedSubject == "TurnEnds":
				self.cancelSelection()
				self.subject, self.target = None, None
				game.switchTurn()
				self.update()
				if hasattr(self, "sock"):
					print("Turn ends . Send the info to server")
					self.sendEndTurnthruServer()
			else:
				self.printInfo("You must click an available option to continue.")
				
		elif self.UI == 2: #影之诗的目标选择是不会进入这个阶段的，直接进入UI == 3，并在那里完成所有的目标选择
			self.target = entity
			self.printInfo("Selected target: {}".format(entity))
			#No matter what the selections are, pressing EndTurn button ends the turn.
			#选择的主体是场上的随从或者英雄。之前的主体在UI=0的界面中已经确定一定是友方角色。
			if selectedSubject == "TurnEnds":
				self.cancelSelection()
				self.subject, self.target = None, None
				game.switchTurn()
				self.update()
				if hasattr(self, "sock"):
					print("Turn ends . Send the info to server")
					self.sendEndTurnthruServer()
			elif selectedSubject.endswith("inHand"): #影之诗的目标选择不会在这个阶段进行
				self.cancelSelection()
			elif self.selectedSubject.endswith("onBoard"):
				if "Hero" not in selectedSubject and selectedSubject != "MiniononBoard":
					self.printInfo("Invalid target for minion attack.")
				else:
					self.printInfo("Requesting battle: {} attacks {}".format(self.subject.name, entity))
					subject, target = self.subject, self.target
					self.cancelSelection()
					self.subject, self.target, self.UI = subject, target, -1
					game.battle(subject, target)
					self.subject, self.target, self.UI = None, None, 0
					self.update()
					if hasattr(self, "sock"):
						self.sendOwnMovethruServer()
			#手中选中的随从在这里结算打出位置，如果不需要目标，则直接打出。
			elif self.selectedSubject == "MinioninHand" or self.selectedSubject == "AmuletinHand": #选中场上的友方随从，我休眠物和护符时会把随从打出在其左侧
				if selectedSubject == "Board" or (entity.ID == self.subject.ID and (selectedSubject.endswith("onBoard") and not selectedSubject.startswith("Hero"))):
					self.pos = -1 if selectedSubject == "Board" else entity.pos
					self.printInfo("Position for minion in hand decided: %d"%self.pos)
					self.selectedSubject = "MinionPositionDecided" #将主体记录为标记了打出位置的手中随从。
					#抉择随从如有全选光环，且所有选项不需目标，则直接打出。 连击随从的needTarget()由连击条件决定。
					#self.printInfo("Minion {} in hand needs target: {}".format(self.subject.name, self.subject.needTarget(self.choice)))
					if not (self.subject.needTarget(self.choice) and self.subject.targetExists(self.choice)):
						#self.printInfo("Requesting to play minion {} without target. The choice is {}".format(self.subject.name, self.choice))
						subject, position, choice = self.subject, self.pos, self.choice
						self.cancelSelection()
						self.subject, self.target, self.UI = subject, None, -1
						game.playMinion(subject, None, position, choice)
						self.subject, self.target, self.UI = None, None, 0
						self.update()
						if hasattr(self, "sock"):
							self.sendOwnMovethruServer()
					else:
						#self.printInfo("The minion requires target to play. needTarget() returns {}".format(self.subject.needTarget(self.choice)))
						button.configure(bg="purple")
						#需要区分SV和炉石随从的目标选择。
						subject = self.subject
						if subject.index.startswith("SV_"): #能到这个阶段的都是有目标选择的随从
							self.choice = 0
							game.Discover.startSelect(subject, subject.findTargets("")[0])
			#随从的打出位置和抉择选项已经在上一步选择，这里处理目标选择。
			elif self.selectedSubject == "MinionPositionDecided":
				if selectedSubject == "MiniononBoard" or selectedSubject == "HeroonBoard":
					self.printInfo("Requesting to play minion {}, targeting {} with choice: {}".format(self.subject.name, entity.name, self.choice))
					subject, position, choice = self.subject, self.pos, self.choice
					self.cancelSelection()
					self.subject, self.target, self.UI = subject, entity, -1
					game.playMinion(subject, entity, position, choice)
					self.subject, self.target, self.UI = None, None, 0
					self.update()
					if hasattr(self, "sock"):
						self.sendOwnMovethruServer()
				else:
					self.printInfo("Not a valid selection. All selections canceled.")
			#选中的法术已经确定抉择选项（如果有），下面决定目标选择。
			elif self.selectedSubject == "SpellinHand":
				if not self.subject.needTarget(self.choice): #Non-targeting spells can only be cast by clicking the board
					if selectedSubject == "Board":
						self.printInfo("Requesting to play spell {} without target. The choice is {}".format(self.subject.name, self.choice))
						subject, target, choice = self.subject, None, self.choice
						self.cancelSelection()
						self.subject, self.target, self.UI = subject, target, -1
						game.playSpell(subject, target, choice)
						self.subject, self.target, self.UI = None, None, 0
						self.update()
						if hasattr(self, "sock"):
							self.sendOwnMovethruServer()
				else: #法术或者法术抉择选项需要指定目标。
					if selectedSubject == "MiniononBoard" or selectedSubject == "HeroonBoard":
						self.printInfo("Requesting to play spell {} with target {}. The choice is {}".format(self.subject.name, entity, self.choice))
						subject, target, choice = self.subject, entity, self.choice
						self.cancelSelection()
						self.subject, self.target, self.UI = subject, target, -1
						game.playSpell(subject, target, choice)
						self.subject, self.target, self.UI = None, None, 0
						self.update()
						if hasattr(self, "sock"):
							self.sendOwnMovethruServer()
					else: self.printInfo("Targeting spell must be cast on Hero or Minion on board.")
			#选择手牌中的武器的打出目标
			elif self.selectedSubject == "WeaponinHand":
				if not self.subject.requireTarget:
					if selectedSubject == "Board":
						self.printInfo("Requesting to play Weapon {}".format(self.subject.name))
						subject, target = self.subject, None
						self.cancelSelection()
						self.subject, self.target, self.UI = subject, None, -1
						game.playWeapon(subject, None)
						self.subject, self.target, self.UI = None, None, 0
						self.update()
						if hasattr(self, "sock"):
							self.sendOwnMovethruServer()
				else:
					if selectedSubject == "MiniononBoard" or selectedSubject == "HeroonBoard":
						subject, target = self.subject, entity
						self.printInfo("Requesting to play weapon {} with target {}".format(subject.name, target.name))
						self.cancelSelection()
						self.subject, self.target, self.UI = subject, target, -1
						game.playWeapon(subject, target)
						self.subject, self.target, self.UI = None, None, 0
						self.update()
						if hasattr(self, "sock"):
							self.sendOwnMovethruServer()
					else: self.printInfo("Targeting weapon must be played with a target.")
			#手牌中的英雄牌是没有目标的
			elif self.selectedSubject == "HeroinHand":
				if selectedSubject == "Board":
					self.printInfo("Requesting to play hero card %s"%self.subject.name)
					subject = self.subject
					self.cancelSelection()
					self.subject, self.target, self.UI = subject, None, -1
					game.playHero(subject)
					self.subject, self.target, self.UI = None, None, 0
					self.update()
					if hasattr(self, "sock"):
						self.sendOwnMovethruServer()
			#Select the target for a Hero Power.
			#在此选择的一定是指向性的英雄技能。
			elif self.selectedSubject == "Power": #如果需要指向的英雄技能对None使用，HeroPower的合法性检测会阻止使用。
				if selectedSubject == "MiniononBoard" or selectedSubject == "HeroonBoard":
					self.printInfo("Requesting to use Hero Power {} on {}".format(self.subject.name, entity.name))
					subject = self.subject
					self.cancelSelection()
					self.subject, self.target, self.UI = subject, entity, -1
					subject.use(entity)
					self.subject, self.target, self.UI = None, None, 0
					self.update()
					if hasattr(self, "sock"):
						self.sendOwnMovethruServer()
				else: self.printInfo("Targeting hero power must be used with a target.")
		else: #self.UI == 3
			if selectedSubject == "DiscoverOption":
				self.UI = 0
				self.update()
				game.Discover.initiator.discoverDecided(entity, info)
			elif selectedSubject == "SelectObj":
				# print("Selecting obj for SV card")
				self.choice += 1
				self.subject.targets.append(entity)
				try: self.target.append(entity)
				except: self.target = [entity]
				if self.subject.needTarget():
					game.Discover.startSelect(self.subject, self.subject.findTargets("", self.choice)[0])
				else: #如果目标选择完毕了，则不用再选择，直接开始打出结算
					self.UI = 0
					subject, target, position, choice = self.subject, self.subject.targets, self.pos, -1
					self.printInfo("Requesting to play Shadowverse spell {} with targets {}".format(subject.name, target))
					self.cancelSelection()
					{"Minion": lambda : game.playMinion(subject, target, position, choice),
					"Spell": lambda : game.playSpell(subject, target, choice),
					"Amulet": lambda : game.playAmulet(subject, target, choice),
					"Power": lambda : subject.use(target, choice),
					}[subject.type]()
					self.update()
					if hasattr(self, "sock"):
						self.sendOwnMovethruServer()
			elif selectedSubject == "Fusion":
				self.UI = 0
				self.update()
				if hasattr(self, "sock"):
					self.sendOwnMovethruServer()
				game.Discover.initiator.fusionDecided(entity)
			else:
				self.printInfo("You MUST click a correct object to continue.")
				
	def waitforDiscover(self, info=None):
		self.UI, self.discover, var = 3, None, tk.IntVar()
		btnDiscoverConfirm = tk.Button(master=self.GamePanel, text="Confirm\nDiscover", bg="lime green", width=10, height=4, font=("Yahei", 12, "bold"))
		btnDiscoverConfirm.GUI, btnDiscoverConfirm.colorOrig = self, "lime green"
		btnDiscoverConfirm.configure(command=lambda: var.set(1) if self.discover else print())
		btnDiscoverHide = DiscoverHideButton(self)
		btnDiscoverHide.place(x=0.82*X, y=0.5*Y, anchor='c')
		self.btnsDrawn.append(btnDiscoverHide)
		for i, option in enumerate(self.Game.options):
			pos = (0.2*X+0.125*X*i, 0.5*Y, 0.09*X, 0.15*Y)
			btnDiscover = DiscoverCardButton(self, option) if hasattr(option, "type") else DiscoverOptionButton(self, option)
			btnDiscover.plot(x=pos[0], y=pos[1])
		btnDiscoverConfirm.place(x=0.73*X, y=0.5*Y, anchor='c')
		btnDiscoverConfirm.wait_variable(var)
		btnDiscoverConfirm.destroy()
		self.resolveMove(self.discover, None, "DiscoverOption", info)
		
	def waitforSelect(self, validTargets):
		self.UI, self.select, var = 3, None, tk.IntVar()
		btnSelectConfirm = tk.Button(master=self.GamePanel, text="Cancel\nSelection", bg="lime green", width=9, height=2, font=("Yahei", 12, "bold"))
		btnSelectConfirm.GUI, btnSelectConfirm.colorOrig = self, "lime green"
		btnSelectConfirm.bind("<Button-1>", lambda event: var.set(2))
		btnSelectConfirm.bind("<Button-3>", lambda event: var.set(2))
		#应该在场上再draw新的button
		validBtns = []
		for target in validTargets:
			for btn in self.handZones[1].btnsDrawn + self.handZones[2].btnsDrawn \
						+ self.boardZones[1].btnsDrawn + self.boardZones[2].btnsDrawn + self.heroZones[1].btnsDrawn + self.heroZones[2].btnsDrawn:
				if btn.card == target:
					btn.var = var
					btn.configure(bg="cyan2")
					btn.unbind("<Button-1>")
					btn.bind("<Button-1>", btn.tempLeftClick)
					validBtns.append(btn)
					break
		btnSelectConfirm.place(x=0.83*X, y=0.5*Y, anchor='c')
		btnSelectConfirm.wait_variable(var)
		# print("btnSelectConfirm clicked, var is", var.get(), var.get())
		btnSelectConfirm.destroy()
		for btn in validBtns:
			btn.configure(bg=btn.colorOrig)
			btn.unbind("<Button-1>")
			btn.bind("<Button-1>", btn.leftClick)
		if var.get() == 1:
			self.resolveMove(self.select, None, "SelectObj")
		else: #var == 2 #If btnSelectConfirm is clicked, cancel the selection
			self.UI = 0
			self.cancelSelection()
			
	def waitforFusion(self, validTargets):
		initiator = self.Game.Discover.initiator
		if initiator.fusion > 0 and initiator.ID == self.Game.turn:
			self.UI, self.fusionMaterials, var = 3, [], tk.IntVar()
			btnSelectConfirm = tk.Button(master=self.GamePanel, text="Left Click to Fuse\nRight Click to Cancel", bg="lime green", width=15, height=3, font=("Yahei", 12, "bold"))
			btnSelectConfirm.GUI, btnSelectConfirm.colorOrig = self, "lime green"
			btnSelectConfirm.bind("<Button-1>", lambda event: var.set(1))
			btnSelectConfirm.bind("<Button-3>", lambda event: var.set(2))
			validBtns = []
			for target in validTargets:
				for btn in self.handZones[validTargets[0].ID].btnsDrawn:
					if btn.card == target:
						btn.var = var
						btn.configure(bg="cyan2")
						btn.unbind("<Button-1>")
						btn.bind("<Button-1>", btn.tempLeftClick_Fusion)
						validBtns.append(btn)
						break
			btnSelectConfirm.place(x=0.83*X, y=0.5*Y, anchor='c')
			btnSelectConfirm.wait_variable(var)
			btnSelectConfirm.destroy()
			for btn in validBtns: #Reset the buttons' color and binding
				btn.configure(bg=btn.colorOrig)
				btn.unbind("<Button-1>")
				btn.bind("<Button-1>", btn.leftClick)
			if var.get() == 1: #var.get() == 2 means cancel the fusion
				if self.fusionMaterials: self.resolveMove(self.fusionMaterials, None, "Fusion")
				else: self.printInfo("Fusion requires other cards selected")
			else:
				self.UI = 0
				self.fusionMaterials = []
				
	def wishforaCard(self, initiator): #initiator is the card instance that starts the process(Zephrys the Great).
		collectionWindow = CardCollectionWindow(self)
		self.UI = 3
		self.btn_ViewCollection.forget()
		self.lbl_Card.forget()
		self.deckGravePanel.forget()
		#Start the wish process
		btnWishConfirm = tk.Button(master=self.sidePanel, text=txt("Wish", CHN), bg="lime green", width=3, height=1, font=("Yahei", 15, "bold"))
		btnWishConfirm.GUI, btnWishConfirm.colorOrig = self, "lime green"
		var = tk.IntVar()
		btnWishConfirm.bind("<Button-1>", lambda event: var.set(1))
		
		self.lbl_wish.pack(side=tk.TOP)
		btnWishConfirm.pack(side=tk.TOP)
		self.lbl_Card.pack(side=tk.TOP)
		self.deckGravePanel.pack(side=tk.TOP)
		while True:
			btnWishConfirm.wait_variable(var)
			if self.cardWished:
				expansion = self.cardWished.index.split('~')[0]
				if expansion == "Basic" or expansion == "Classic":
					break
				else: messagebox.showinfo(message=txt("The card is not a Basic or Classic card", CHN))
			else: messagebox.showinfo(message=txt("No wish card selected yet", CHN))
			collectionWindow = CardCollectionWindow(self)
			var = tk.IntVar()
		self.Game.fixedGuides.append(self.cardWished)
		self.Game.Hand_Deck.addCardtoHand(self.cardWished, initiator.ID, byType=True, creator=type(initiator)) #目前假设许愿的卡牌是双方可以看到的，但是实际上不是
		
		btnWishConfirm.destroy()
		try: collectionWindow.destroy()
		except: pass
		self.lbl_wish.forget()
		self.lbl_Card.forget()
		self.btn_ViewCollection.pack(side=tk.TOP)
		self.lbl_Card.pack(side=tk.TOP)
		self.UI = 0
		self.update()
		
	def displayCard(self, card, notSecretBeingPlayed=True):
		if card:
			#如果打出的牌不是一个正在打出的奥秘或者（是奥秘但是是我方奥秘，或者游戏可以显示对方的信息）， 则直接显示打出的奥秘牌
			if notSecretBeingPlayed or not hasattr(self, "ID") or card.ID == self.ID or not card.description.startswith("Secret:") or seeEnemyHand:
				img = PIL.Image.open(findPicFilepath_FullImg(card))#.resize(((270, 360)))
			else: img = PIL.Image.open("Images\\%sSecret.png"%card.Class)
			#if img.size[1] > 360: img = img.resize((240, 320))
			ph = PIL.ImageTk.PhotoImage(img)
			self.lbl_Card.configure(image=ph)
			self.lbl_Card.image = ph
		else:
			self.lbl_Card.config(image=None)
			self.lbl_Card.image = None
			
	def wait(self, duration, showLine=True):
		self.update()
		if showLine:
			btn1, btn2 = None, None
			if self.subject and self.target:
				for btn in self.boardZones[1].btnsDrawn + self.boardZones[2].btnsDrawn + self.heroZones[1].btnsDrawn + self.heroZones[2].btnsDrawn + \
					([self.offBoardTrigs[1]] if self.offBoardTrigs[1] else []) + ([self.offBoardTrigs[2]] if self.offBoardTrigs[2] else []):
					if btn.card == self.subject:
						btn1 = btn
						break
				if btn1 is None: #如果施放的是法术，则不会找到对应这个法术的button，直接连接施法者和目标
					btn1 = self.heroZones[self.subject.ID].btnsDrawn[0]
				for btn in self.boardZones[1].btnsDrawn + self.boardZones[2].btnsDrawn + self.heroZones[1].btnsDrawn + self.heroZones[2].btnsDrawn:
					if btn.card == self.target or (isinstance(self.target, list) and btn.card in self.target):
						btn2 = btn
						break
				lineID = self.canvas.connectBtns(btn1, btn2)
		var = tk.IntVar()
		self.window.after(duration, var.set, 1)
		self.window.wait_variable(var)
		try: self.canvas.delete(lineID) #If a line is drawn, erase it.
		except: pass
		
	def trigBlink(self, entity, color="yellow"):
		for btn in self.boardZones[entity.ID].btnsDrawn + self.heroZones[entity.ID].btnsDrawn + self.secretZones[entity.ID].btnsDrawn \
					+ (self.handZones[entity.ID].btnsDrawn if not hasattr(self, "ID") or seeEnemyHand or entity.ID == self.ID else []):
			if btn.card == entity:
				btnFound = True
				color_0 = btn.cget("bg")
				btn.config(bg=color)
				self.displayCard(entity, notSecretBeingPlayed=True)
				var = tk.IntVar()
				self.window.after(500, var.set, 1)
				self.window.wait_variable(var)
				btn.config(bg=color_0)
				break
				
	def showOffBoardTrig(self, card, linger=True):
		ID, ownID = card.ID, self.ID if hasattr(self, "ID") else 1
		if self.offBoardTrigs[ID]: self.offBoardTrigs[ID].remove()
		#After erasing the old effect, show the new effect being resolved.
		btn = HandButton(self, card, enemyCanSee=seeEnemyHand)
		pos = int(0.1*X), int(0.65*Y if ID == ownID else 0.35*Y)
		btn.plot(pos[0], pos[1])
		self.handZones[ID].btnsDrawn.remove(btn)
		self.offBoardTrigs[ID] = btn
		if not linger:
			btn.configure(bg="yellow")
			var = tk.IntVar()
			self.window.after(500, var.set, 1)
			self.window.wait_variable(var)
			btn.remove()
			self.offBoardTrigs[ID] = None
			
	def eraseOffBoardTrig(self, ID):
		try: self.offBoardTrigs[ID].remove()
		except: pass
		self.offBoardTrigs[ID] = None
		
	def attackAni(self, subject, target):
		subjectFound = False
		for zone in [self.boardZones[1].btnsDrawn, self.boardZones[2].btnsDrawn]:
			for i, btn in enumerate(zone):
				if btn.card == subject:
					btn1 = MinionButton(btn.GUI, btn.card)
					btn.remove()
					btn1.plot(btn.x, y=btn.y)
					zone.insert(i, zone.pop())
					subjectFound = True
					break
		if not subjectFound:
			for zone in [self.heroZones[1].btnsDrawn, self.heroZones[2].btnsDrawn]:
				for i, btn in enumerate(zone):
					if btn.card == subject:
						btn1 = HeroButton(btn.GUI, btn.card)
						btn.remove()
						btn1.plot(btn.x, y=btn.y)
						break
		for btn in self.boardZones[1].btnsDrawn + self.boardZones[2].btnsDrawn + self.heroZones[1].btnsDrawn + self.heroZones[2].btnsDrawn:
			if btn.card == target:
				btn2 = btn
				break
		x1, y1, x2, y2 = btn1.x, btn1.y, btn2.x, btn2.y
		self.moveBtnsAni(btn1, (x2, y2), timestep=6, stepSize=10)
		self.moveBtnsAni(btn1, (x1, y1), timestep=6, stepSize=10)
		
	def moveBtnsAni(self, btns, posEnds, timestep=14, stepSize=0, vanish=False, vanishTime=250): #vanish means buttons disappear after reaching final positions
		numSteps = 10
		if isinstance(btns, (list, tuple)): #Move multiple buttons
			#Remove those already at the posEnds
			btns_real, posArrays_x, posArrays_y = [], [], []
			for i, btn in enumerate(btns):
				if btn.x != posEnds[i][0] or btn.y != posEnds[i][1]:
					btns_real.append(btn)
					posArrays_x.append(np.linspace(btn.x, posEnds[i][0], numSteps))
					posArrays_y.append(np.linspace(btn.y, posEnds[i][1], numSteps))
			if posArrays_x: #After transposition, posArrays_x has length = 10
				posArrays_x = np.transpose(np.asarray(posArrays_x))
				posArrays_y = np.transpose(np.asarray(posArrays_y))
				var = tk.IntVar()
				for posArray_x, posArray_y in zip(posArrays_x, posArrays_y):
					self.window.after(timestep, var.set, 1)
					self.window.wait_variable(var)
					for btn, pos1, pos2 in zip(btns_real, posArray_x, posArray_y):
						btn.move2(pos1, pos2)
				if vanish:
					self.window.after(vanishTime, var.set, 1)
					self.window.wait_variable(var)
					for btn in btns: btn.remove()
		else: #Move a single button. btns is a button, posEnds is a single tuple
			x1, y1, x2, y2 = btns.x, btns.y, posEnds[0], posEnds[1]
			if x1 != x2 or y1 != y2:
				if stepSize:
					distance = np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
					numSteps = int(distance / stepSize)
				posArray_x = np.linspace(x1, x2, numSteps)
				posArray_y = np.linspace(y1, y2, numSteps)
				var = tk.IntVar()
				for pos1, pos2 in zip(posArray_x, posArray_y):
					self.window.after(timestep, var.set, 1)
					self.window.wait_variable(var)
					btns.move2(pos1, pos2)
				if vanish: btns.remove()
				
	def drawCardAni_1(self, card):
		ownID = self.ID if hasattr(self, "ID") else 1
		btn = HandButton(self, card)
		ID = card.ID
		btn.plot(x=self.deckZones[ID].x, y=self.deckZones[ID].y)
		self.handZones[card.ID].btnsDrawn.remove(btn)
		btn.configure(bg="green")
		posEnds = (int(0.85*X), DrawPos_y if card.ID == ownID else Y-DrawPos_y)
		self.moveBtnsAni(btn, posEnds)
		var = tk.IntVar()
		self.window.after(int(450), var.set, 1)
		self.window.wait_variable(var)
		return btn
		
	def drawCardAni_2(self, btn, newCard): #The drawn card might get transformed
		if btn.card != newCard:
			btn.remove()
			HandButton(self, newCard).plot(x=btn.x, y=btn.y)
			var = tk.IntVar()
			self.window.after(250, var.set, 1)
			self.window.wait_variable(var)
		else: self.handZones[btn.card.ID].btnsDrawn.append(btn)
		self.handZones[btn.card.ID].draw(cardMoving2=-1)
		
	def millCardAni(self, card):
		ID, ownID = card.ID, self.ID if hasattr(self, "ID") else 1
		btn = HandButton(self, card, enemyCanSee=True)
		btn.plot(x=self.deckZones[ID].x, y=self.deckZones[ID].y)
		btn.configure(bg="grey46")
		posEnds = (int(0.85*X), DrawPos_y if ID == ownID else Y-DrawPos_y)
		self.moveBtnsAni(btn, posEnds)
		var = tk.IntVar()
		self.window.after(int(450), var.set, 1)
		self.window.wait_variable(var)
		btn.remove() #Milled cards simply vanish
		
	def fatigueAni(self, ID, damage):
		ownID = self.ID if hasattr(self, "ID") else 1
		btn = tk.Button(master=self.GamePanel, text=str(damage), width=int(0.7*HandIconWidth_noImg), height=int(0.4*HandIconHeight_noImg), font=("Yahei", 20, "bold"))
		btn.x, btn.y = self.deckZones[ID].x, self.deckZones[ID].y
		btn.move2 = lambda x, y: btn.place(x=x, y=y)
		btn.place(x=btn.x, y=btn.y, anchor='c')
		btn.configure(bg="red")
		posEnds = (int(0.85*X), int(0.6*Y) if ID == ownID else int(0.4*Y))
		self.moveBtnsAni(btn, posEnds)
		var = tk.IntVar()
		self.window.after(int(300), var.set, 1)
		self.window.wait_variable(var)
		btn.destroy() #Milled cards simply vanish
		
	def cardEntersHandAni_1(self, card):
		btn = HandButton(self, card)
		btn.plot(x=X/2, y=Y/2)
		self.handZones[card.ID].btnsDrawn.remove(btn)
		btn.configure(bg="green3")
		return btn
		
	def cardEntersHandAni_2(self, btn, i, steps): #Add the card to the correct pos in handZone btnsDrawn
		self.handZones[btn.card.ID].btnsDrawn.insert(i, btn)
		self.handZones[btn.card.ID].draw(cardMoving2=i, steps=steps)
		
	def cardReplacedinHand_Refresh(self, ID):
		self.handZones[ID].redraw()
		
	def cardsLeaveHandAni(self, cards, enemyCanSee=True):
		ownID = self.ID if hasattr(self, "ID") else 1
		if not isinstance(cards, (list, tuple)): cards = [cards]
		ID, btns, posEnds = cards[0].ID, [], []
		for card in cards:
			for i, btn in enumerate(self.handZones[ID].btnsDrawn):
				if btn.card == card:
					btn1 = HandButton(btn.GUI, btn.card, enemyCanSee=enemyCanSee)
					btn.remove()
					btn1.configure(bg="red")
					btn1.plot(x=btn.x, y=btn.y)
					self.handZones[ID].btnsDrawn.insert(i, self.handZones[ID].btnsDrawn.pop())
					btns.append(btn1)
					posEnds.append((btn.x, 0.62*Y if ID == ownID else 0.38*Y))
					break
		self.moveBtnsAni(btns, posEnds, vanish=True)
		
	def cardLeavesDeckAni(self, card, enemyCanSee=True):
		ownID = self.ID if hasattr(self, "ID") else 1
		btn = HandButton(self, card)
		ID = card.ID
		btn.plot(x=self.deckZones[ID].x, y=self.deckZones[ID].y)
		self.handZones[card.ID].btnsDrawn.remove(btn)
		btn.configure(bg="green")
		posEnds = (int(0.85*X), DrawPos_y if card.ID == ownID else Y-DrawPos_y)
		self.moveBtnsAni(btn, posEnds)
		var = tk.IntVar()
		self.window.after(350, var.set, 1)
		self.window.wait_variable(var)
		btn.remove()
		
	def shuffleintoDeckAni(self, cards, enemyCanSee=True):
		if not isinstance(cards, (list, np.ndarray)): cards = [cards]
		ID, cards, btns = cards[0].ID, cards[::-1], []
		ownID = self.ID if hasattr(self, "ID") else 1
		for card in cards:
			btn = HandButton(self, card)
			btn.plot(x=int(0.85*X), y=DrawPos_y if ID == ownID else Y-DrawPos_y)
			self.handZones[ID].btnsDrawn.pop()
			btns.append(btn)
		btns = btns[::-1]
		var = tk.IntVar()
		self.window.after(400, var.set, 1)
		self.window.wait_variable(var)
		posEnd = (self.deckZones[ID].x, self.deckZones[ID].y)
		timestep = 14 if len(cards) > 3 else 20
		for btn in btns:
			self.moveBtnsAni(btn, posEnd, timestep)
			btn.remove()
			
	def targetingEffectAni(self, subject, target, num, color="red"):
		pos1, pos2 = (), ()
		if subject and target:
			for btn in self.boardZones[1].btnsDrawn + self.boardZones[2].btnsDrawn + self.heroZones[1].btnsDrawn + self.heroZones[2].btnsDrawn + \
					([self.offBoardTrigs[1]] if self.offBoardTrigs[1] else []) + ([self.offBoardTrigs[2]] if self.offBoardTrigs[2] else []):
				if btn.card == subject:
					pos1 = btn.x, btn.y
					break
			if not pos1: #如果找不到对应这个subject的button，直接连接英雄和目标
				btnHero = self.heroZones[subject.ID].btnsDrawn[0]
				pos1 = btnHero.x, btnHero.y
			for btn in self.boardZones[1].btnsDrawn + self.boardZones[2].btnsDrawn + self.heroZones[1].btnsDrawn + self.heroZones[2].btnsDrawn:
				if btn.card == target:
					pos2 = btn.x, btn.y
					break
			var = tk.IntVar()
			btn = tk.Button(master=self.GamePanel, text=str(num), bg=color, width=2, height=1, font=("Yahei", 14, "bold"))
			btn.x, btn.y = pos1
			btn.move2 = lambda x, y: btn.place(x=x, y=y)
			btn.place(x=btn.x, y=btn.y, anchor='c')
			self.window.after(250, var.set, 1)
			self.window.wait_variable(var)
			self.moveBtnsAni(btn, pos2, timestep=5, stepSize=8)
			self.window.after(250, var.set, 1)
			self.window.wait_variable(var)
			btn.destroy()
			
	def AOEAni(self, subject, targets, numbers, color="red"):
		if targets:
			if len(targets) == 1: self.targetingEffectAni(subject, targets[0], numbers[0])
			else:
				timestep = 4 if len(targets) < 4 else 5
				pos1, pos2, btns = (), (), []
				for btn in self.boardZones[1].btnsDrawn + self.boardZones[2].btnsDrawn + self.heroZones[1].btnsDrawn + self.heroZones[2].btnsDrawn + \
					([self.offBoardTrigs[1]] if self.offBoardTrigs[1] else []) + ([self.offBoardTrigs[2]] if self.offBoardTrigs[2] else []):
					if btn.card == subject:
						pos1 = btn.x, btn.y
						break
				if not pos1: #如果施放的是法术，则不会找到对应这个法术的button，直接连接施法者和目标
					btnHero = self.heroZones[subject.ID].btnsDrawn[0]
					pos1 = btnHero.x, btnHero.y
				#Starting drawing and moving btns for each target
				var = tk.IntVar()
				for target, num in zip(targets, numbers):
					for btn in self.boardZones[1].btnsDrawn + self.boardZones[2].btnsDrawn + self.heroZones[1].btnsDrawn + self.heroZones[2].btnsDrawn:
						if btn.card == target:
							pos2 = btn.x, btn.y
							break
					btn = tk.Button(master=self.GamePanel, text=str(num), bg=color, width=2, height=1, font=("Yahei", 14, "bold"))
					btn.x, btn.y = pos1
					btn.move2 = lambda x, y: btn.place(x=x, y=y)
					btn.place(x=btn.x, y=btn.y, anchor='c')
					self.window.after(150, var.set, 1)
					self.window.wait_variable(var)
					self.moveBtnsAni(btn, pos2, timestep=timestep, stepSize=8)
					btns.append(btn)
				self.window.after(250, var.set, 1)
				self.window.wait_variable(var)
				for btn in btns: btn.destroy()
				
				
				
				
class CardCollectionWindow(tk.Tk):
	def __init__(self, GUI):
		tk.Tk.__init__(self)
		self.GUI = GUI
		game = self.GUI.Game
		self.Class2Display, self.expansion, self.mana = tk.StringVar(self), tk.StringVar(self), tk.StringVar(self)
		
		self.Class2Display.set(list(game.ClassCards.keys())[0])
		self.mana.set("All")
		self.expansion.set("All")
		self.classOpt = tk.OptionMenu(self, self.Class2Display, *(list(game.ClassCards.keys()) + ["Neutral"]) )
		self.manaOpt = tk.OptionMenu(self, self.mana, *["All", '0', '1', '2', '3', '4', '5', '6', '7', '7+'])
		self.expansionOpt = tk.OptionMenu(self, self.expansion, *["All", "DIY", "Basic", "Classic", "Shadows", "Uldum", "Dragons", "Galakrond", "Initiate", "Outlands", "Academy", "Darkmoon"])
		self.classOpt.config(width=12, font=("Yahei", 14))
		self.classOpt["menu"].config(font=("Yahei", 14))
		self.manaOpt.config(font=("Yahei", 14))
		self.expansionOpt.config(font=("Yahei", 14))
		
		self.search = tk.Entry(self, font=("Yahei", 13), width=20)
		btn_ViewCards = tk.Button(self, text=txt("View Cards", CHN), command=self.showCards, font=("Yahei", 14), bg="green3")
		btn_Left = tk.Button(self, text=txt("Last Page", CHN), command=self.lastPage, font=("Yahei", 14))
		btn_Right = tk.Button(self, text=txt("Next Page", CHN), command=self.nextPage, font=("Yahei", 14))
		self.cards2Display, self.btnsDrawn, self.pageNum = {}, [], 0
		self.displayPanel = tk.Frame(self)
		
		tk.Label(self, text=txt("Class", CHN), font=("Yahei", 13)).grid(row=0, column=0)
		self.classOpt.grid(row=0, column=1)
		tk.Label(self, text=txt("Mana", CHN), font=("Yahei", 13)).grid(row=0, column=2)
		self.manaOpt.grid(row=0, column=3)
		tk.Label(self, text=txt("Expansion", CHN), font=("Yahei", 13)).grid(row=0, column=4)
		self.expansionOpt.grid(row=0, column=5)
		self.search.grid(row=0, column=6)
		btn_ViewCards.grid(row=0, column=7)
		
		tk.Label(self, text="  ", font=("Yahei", 13)).grid(row=0, column=8)
		btn_Left.grid(row=0, column=9)
		btn_Right.grid(row=0, column=10)
		self.displayPanel.grid(row=1, column=0, columnspan=11)
		
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
		self.cards2Display, self.pageNum = {}, 0
		for btn in self.btnsDrawn: btn.destroy()
		
		Class2Display = self.Class2Display.get()
		mana = self.mana.get()
		expansion = self.expansion.get()
		search = self.search.get()
		
		game = self.GUI.Game
		if Class2Display == "Neutral": cards = game.NeutralCards
		else: cards = game.ClassCards[Class2Display]
		i, j = 0, -1
		for key, value in cards.items():
			if self.manaCorrect(value, mana) and self.expansionCorrect(key, expansion) \
				and self.searchMatches(search, value):
				if i % 10 == 0:
					j += 1
					self.cards2Display[j] = [value(game, 1)]
				else: self.cards2Display[j].append(value(game, 1))
				i += 1
		if self.cards2Display: #如果查询结果不为空
			for i, card in enumerate(self.cards2Display[0]):
				btn_Card = CardCollectionButton(self, card)
				btn_Card.plot(0 + i > 4, i % 5)
				
	def lastPage(self):
		if self.pageNum - 1 in self.cards2Display:
			self.pageNum -= 1
			for btn in self.btnsDrawn: btn.destroy()
			for i, card in enumerate(self.cards2Display[self.pageNum]):
				btn_Card = CardCollectionButton(self, card)
				btn_Card.plot(0 + i > 4, i % 5)
		else: messagebox.showinfo(message=txt("Already the last page", CHN))
		
	def nextPage(self):
		if self.pageNum + 1 in self.cards2Display:
			self.pageNum += 1
			for btn in self.btnsDrawn: btn.destroy()
			for i, card in enumerate(self.cards2Display[self.pageNum]):
				btn_Card = CardCollectionButton(self, card)
				btn_Card.plot(0 + i > 4, i % 5)
		else: messagebox.showinfo(message=txt("Already the first page", CHN))
		
		