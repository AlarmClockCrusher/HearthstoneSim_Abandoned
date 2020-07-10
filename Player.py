from Game import *

import numpy as np
import collections

def sqrtActi(x): return np.sqrt(x) if x >=0 else -np.sqrt(-x)

def extractfrom(target, listObject):
	try: return listObject.pop(listObject.index(target))
	except: return None
	
def fixedList(listObject): return listObject[0:len(listObject)]
	
def exponential(x, ver_offset, amp, rate): return ver_offset + amp * np.exp(rate * x)
	
def inverse(x, hor_offset, ver_offset, amp): return hor_offset + amp / (x - ver_offset)
	
class Player:
	def __init__(self, Game, ID):
		self.Game, self.ID = Game, ID
		self.RNGBranch = RNGBranch(self)
		
	#Decide what card to keep based on the sorted mana cost list.
	def decideMulligan(self):
		indicesCards = []
		for i in range(len(self.Game.mulligans[self.ID])):
			if self.Game.mulligans[self.ID][i].mana > 3:
				indicesCards.append(i)
		return indicesCards
		
	#Return the available subjects for the play to command in a given Game
	def availableSubs(self, Game):
		if Game.turn != self.ID: return []
		else:
			ID, subjectInfos = self.ID, []
			if Game.Manas.affordable(Game.powers[ID]) and Game.powers[ID].available():
				subjectInfos.append((Game.powers[ID], ID, "power"))
			for i, card in enumerate(Game.Hand_Deck.hands[ID]):
				if Game.Manas.affordable(card):
					if card.type == "Weapon" or card.type == "Hero" or (card.type == "Spell" and card.available()) or (card.type == "Minion" and Game.space(ID) > 0):
						subjectInfos.append((card, i, "hand"+ID))
			for i, minion in enumerate(Game.minionsonBoard(ID)):
				if minion.canAttack(): subjectInfos.append((minion, i, "minion%d"%ID))
			if Game.heroes[ID].canAttack(): subjectInfos.append((Game.heroes[ID], ID, "hero"))
			return subjectInfos
			
	#不同的事件类型存在时，怎么让其知道随从在不同的生命值死去时是一样的事件
	#是否应该把一些参数定义为通用的参数，比如所有随从的生命值和关键字等
	
	#在判断事件是否相同的时候应该只关注其最基本的一些事件和定义，无视随从的情况，辅以场上身材的比较
	def sameEventsHappened(self, game1, game2):
		#检测分为两段，首先对比双方手牌和场上角色的基本数值信息,如果对不上就说明不对
		#然后再对比两个游戏储存的游戏中事件列表，基本可以满足保证判断出两个游戏是否是冗余的要求
		for ID in range(1, 3):
			if not game1.heroes[ID].sameState(game2.heroes[ID]): return False
			if not game1.powers[ID].sameState(game2.powers[ID]): return False
			minionsAlive1, minionsAlive2 = game1.minionsonBoard(ID), game2.minionsonBoard(ID)
			if len(minionsAlive1) != len(minionsAlive2): return False
			for i in range(len(minionsAlive1)):
				if not minionsAlive1[i].sameState(minionsAlive2[i]): return False
			if len(game1.Hand_Deck.hands[ID]) != len(game2.Hand_Deck.hands[ID]): return False
			for i in range(len(game1.Hand_Deck.hands[ID])):
				if not game1.Hand_Deck.hands[ID][i].sameState(game2.Hand_Deck.hands[ID][i]): return False
		#因为对比过场上角色的基本数值等，所以事件本身的信息只需要signal和主体名字即可
		events1, events2 = [], []
		for event in game1.eventList:
			try: events1.append((event[0], event[1])) #一般event都是包含signal和主体名称的，如果只有signal，则只执行添加(signal)
			except: events1.append(event) #event可能是只有一个元素的tuple
		for event in game2.eventList:
			try: events2.append((event[0], event[1])) #一般event都是包含signal和主体名称的，如果只有signal，则只执行添加(signal)
			except: events2.append(event)
		#如果两个游戏中的eventList不包含相同的事件（顺序可以不同），则说明两个游戏目前是不等价的
		return collections.Counter(events1) == collections.Counter(events2)
		
	#从一个当前的游戏状态出发，决定从此开始的所有playerMoves
	def pickBestStrategy(self, Game):
		print("Picking the best strategy from the current game state")
		resultsinTurn_NoR, bestStrategy_NoR, highestScore_NoR, resultswithBranching = self.stratsfromCurGames(Game)
		#resultsinTurn_NoR不为空说明操作分叉没有结果，resultswithBranching是有随机分叉都存在的操作
		print("*******************\nThe strategies decided are")
		print("BestStrategy_NoR", highestScore_NoR, bestStrategy_NoR, "DuringTurnRe", resultsinTurn_NoR)
		print("*******************")
		highestScore, bestStrategy = highestScore_NoR, bestStrategy_NoR
		print("HighestScore_FullTurn", highestScore, " bestStrategy_FullTurn", bestStrategy)
		if resultsinTurn_NoR: #未完成的操作分叉较多
			#可以确定的是，总会有一个确定性的分叉，因为那个分叉就是直接结束回合
			for moves, result in resultsinTurn_NoR.items():
				score = self.evaluateStrategy(result)
				if score > highestScore:
					#print("Score of the highest in turn replaces the current highest score", score, moves)
					highestScore, bestStrategy = score, moves
		else: #没有未完成的确定性分叉了，需要做的，就是把确定性分叉中的得分最高者与RNG和发现分叉的做比较
			if highestScore_NoR < 3: #需要把确定性操作的评分与最高的随机分叉作比较
				highestScore_branching = -np.inf
				for moves, result in resultswithBranching.items():
					score = self.evaluateStrategy(result)
					if score > highestScore:
						#print("Score of the highest UNCERTAIN replaces the current highest score", score, moves)
						highestScore, bestStrategy = score, moves
		return highestScore, bestStrategy
		
	#在回合开始的时候，拿到对局目前的Game，然后返回分叉最高的。不确定性的操作分叉只进行一层，主要采用统计的方法求其评分期望
	def stratsfromCurGames(self, curGame):
		#Game在这里要留作原始的copy，让之后打出随机性操作的时候能让Game从这里演化
		resultsinTurn_NoR = {(): curGame}
		#这里的bestStrategy_NoR是分叉至回合结束的分数最高的策略
		bestStrategy_NoR, highestScore_NoR = None, -np.inf
		numPlays, resultswithBranching = 0, {} #numPlays为确定性操作分叉的最高上限，超过的话终止分叉
		#一旦分叉到回合结束就对一个策略进行评分，并与最高分对比，只保留最高分
		while numPlays < 2000: #循环过程中不断把涉及RNG/发现分叉的结果转移出去，相对减少branchResults的size
			#设置prevBranches，每次分叉循环结束后，接收作为工作区域的branchResults的内容
			prevBranches, resultsinTurn_NoR, canFurtherBranch = resultsinTurn_NoR, {}, False
			for playerMove in prevBranches.keys(): #直接用dict的keys()来iterate的话，中途改变其size会报错
				#对一串操作进行分叉尝试，如果分叉成功，则说明可能进行更长远的分叉
				movesBranchable, options = self.movesfromCurKey(playerMove, prevBranches)
				if movesBranchable or options: #分叉尝试返回了可用结果
					canFurtherBranch = True
					for moves, result in options.items(): #需要把options里面的策略和结果逐个处理
						if moves[-1] == ("EndTurn", 0): #回合结束的结果无论是确定性结果还是分叉，都本质上属于确定性操作
							score = self.evaluateStrategy(result)
							if score > highestScore_NoR: highestScore_NoR, bestStrategy_NoR = score, moves
						else: #尚未执行到回合结束阶段的策略，要么是分叉，要么是还可以进行操作分叉的确定性操作
							if isinstance(result, Game): #确定性操作只有不与之前的确定性操作重合的情况下才能加入branchResults中
								strategyRedundant = False
								for game in resultsinTurn_NoR.values():
									#需要考虑判定冗余分叉到底是否需要比较操作顺序
									if self.sameEventsHappened(game, result):
										strategyRedundant = True
										break
								if strategyRedundant == False:
									resultsinTurn_NoR[moves] = result
									numPlays += 1
							else: #分叉/随机实验归入resultswithBranching
								resultswithBranching[moves] = result
								numPlays += 1
								
			if not canFurtherBranch: break
			#最终会从这些操作分叉结果中挑出最好的评分结果。只是确定性操作分叉结果和RNG分叉的评分稍有不同
			#只有分叉过多时，branchResults才会不为{}
		return resultsinTurn_NoR, bestStrategy_NoR, highestScore_NoR, resultswithBranching
		
	#根据推算的结果进行实际的游戏操作，每步move都在结算之后被剔除
	def makeRealMove(self, moves, game):
		#因为操作分叉都会停在有RNG过程发生的步骤，所有在直到进行最后一步之前的所有步骤都是最多涉及确定性的选择问题
		for i in range(len(playerMoves)-1): #对于所有最后一步之前的操作进行确定性的推演
			move, game.mode = moves[i], 0 #需要让游戏知道现在是在没有分叉的情况下运作
			#如果move是list，则其0项是player给出的move，之后的项是选择分叉的选择guide
			if isinstance(move[0], tuple): #如果这个move是move+selection的组合
				game.fixedGuides = move
				game.decodePlay(move[0])
			else: #如果这个move是move+selection的组合
				game.fixedGuides = [move]
				game.decodePlay(move)
			#处理最后一步move
			move = moves[-1]
			game.mode = 0
			gameOrig = game.copyGame()[0]
			if isinstance(move, list):
				game.fixedGuides = move
				#开始推演之后有可能会出现选择/发现过程，那里会调用game.Discover.startDiscover
					#并从那里根据gameOrig复制出对应不同选项的game，并针对选项拿到各自的操作分叉评分，从而得到最优者
				game.decodePlay(move[0])
			else:
				game.fixedGuides = [move]
				game.decodePlay(move)
				
	def attachBranches(self, dict, key, move, cat, result):
		if cat == "!R!S" or cat == "!S1st": dict[tuple(list(key)+[move])] = result #确定性操作返回单个game, 开头是RD分叉的则返回tree
		elif cat == "S1st": #result: {(s1, s2)-trees} #需要把拆分出来的branch纳入playerMove里面
			for selection, branch in result.items(): #如果branch里面没有RNG元素等任何分叉，则视为确定性操作结果，返回单个game
				move_withSGuide = tuple([move] + list(selection)) #(move, SGuide1, SGuide2),其中的每个元素都是一个tuple
				dict[tuple(list(key)+[move_withSGuide])] = branch.game if branch.hasNoRandomness() else branch
		else: #cat == "O" 如果分叉过多导致分叉取消
			#分叉过多一定涉及RNG元素，4次S分叉也只能造成4^4=256种可能
			#result包含两个list，分别是100次的category和100次的结果，如果开头是S分叉，则trials的每个元素都是dict
			flags, trials = result[0], result[1]
			if flags[0] == "O_S1st": #如果有一个branch的开头就是选择，则所有其他99个branch的开头也会是选择
				for selection in trials[0].keys(): #先把所有的选择分叉的selection在dict中创造对应key的列表
					move_withSGuide = tuple([move] + list(selection))
					dict[tuple(list(key)+[move_withSGuide])] = []
				for trial in trials: #element[1]是一个dict: {selection: branch}
					for selection, branch in trial.items():
						move_withSGuide = tuple([move] + list(selection))
						dict[tuple(list(key)+[move_withSGuide])].append(branch) #是列表
			else: #如果随机实验的开头不是选择分叉,dict[key+move]变成一个100个branch的列表
				newKey = tuple(list(key)+[move])
				dict[newKey] = [] #如果分叉的开头还是选择分叉，直接把100次实验结果加入key+playerMove下面的列表里
				for trial in trials: dict[newKey].append(trial)
		
	#最初的branchResults设为dict[[playerMove1, playerMove2]] = Game,然后进行操作分叉。如果还可以操作分叉，则返回True，否则返回False
	#没有确定性选择分叉的playerMove为tuple，若有确定性选择分叉则为list.代表每次操作，如打出一张牌，进行一次攻击。这些列表可以让一个回合开始时的游戏循着这些move一步一步执行到玩家需要的地步
	#如果一个key本身是回合结束了和分叉，其本身不可继续进行操作分叉，返回False, []
	#如果一个key本身除了回合结束没有其他选择，则返回False，options
	#如果一个key还有可以分叉的可能，则返回True，options
	def movesfromCurKey(self, key, dict):
		if key and (key[-1] == ("EndTurn", 0) or not isinstance(dict[key], Game)):
			return False, {}
		else: #可以分叉，则需要对当前这个吸下面的游戏进行备份
			options, gameOrig, subjectInfos = {}, dict[key], self.availableSubs(dict[key])
			game, move = gameOrig.copyGame()[0], ("EndTurn", 0)
			category, result = self.RNGBranch.resultsResolved([move], game)
			#回合结束这个操作里面不可能进行选择，只可能是确定性的或有RNG分叉
			self.attachBranches(options, key, move, category, result)
			#开始尝试根据打出不同牌或者控制角色攻击 进行操作分叉
			if not subjectInfos: return False, options #如果没有更多的操作分叉，则同样返回False，但是options里面有回合结束这个选项
			else:
				for sub, subInd, subWhere in subjectInfos:
					if not sub.onBoard: #Hero Power's onBoard is always True(it's a placeholder)
						choices = [0]
						if sub.chooseOne: #抉择牌或技能需要根据光环决定可以使用的选项
							choices = ["ChooseBoth"] if gameOrig.status[self.ID]["Choose Both"] > 0 else [i for i in range(len(sub.options)) if sub.options[i].available()]
						for choice in choices: #对所有可用的选项进行遍历，返回所有合法目标
							tars, tarInds, tarWheres = sub.findTargets(choice) if sub.needTarget(choice) else [None], [0], ['']
							gameCopies == gameOrig.copyGame(len(tars))
							for tarInd, tarWhere, game in zip(tarInds, tarWheres, gameCopies):
								moveType = "play"+sub.type if sub.type != "Power" else "power"
								if sub.type != "Minion": move = (moveType, subInd, subWhere, tarInd, tarWhere, choice)
								#暂时让所有随从的打出位置都是最右侧
								else: move = (moveType, subInd, subWhere, tarInd, tarWhere, -1, choice)
								#确定性的操作只返回单个game,随机分叉返回tree，选择分叉产生的tree会直接拆分为dict,然后每个key用于改造move，并形成新的move~tree
								category, result = self.RNGBranch.resultsResolved([move], game)
								self.attachBranches(options, key, move, category, result)
					else: #onBoard minions/heroes decide whom to attack
						tars, tarInds, tarWheres = sub.findBattleTargets()
						gameCopies = gameOrig.copyGame(len(tars))
						for tarInd, tarWhere, game in zip(tarInds, tarWheres, gameCopies):
							move = ("battle", subInd, subWhere, tarInd, tarWhere)
							category, result = self.RNGBranch.resultsResolved([move], game)
							self.attachBranches(options, key, playerMove, category, result)
			return True, options #返回True，可以继续尝试是否有更多的可能性
			
		#学习到的矩阵如何在之后变异，导入和保存留到之后思考
	#目前只是把矩阵留在file里面在需要的时候调用而已
	def evaluateEvent(self, event):
		#event是一个tuple，其0号元素应该是signal名称
		if event[0] == "HeroDies":
			return np.inf if event[1] != self.ID else -np.inf
		else:
			matrix = list(dict_Event2Matrices[event[0]])
			#如果event的signal里面没有trigger则直接去掉所有的字符串，如果有trigger,则那些trigger有各自的评分函数
			#这里面应该排除掉所有的字符串,包括signal和主体名称
			array = np.array([ele for ele in event if isinstance(ele, str) == False])
			grade = sqrtActi(np.dot(matrix, np.append(array, 1)))
			#事件的主体名称是否要参与到游戏中进行评分。
			#面临的一个问题是评分系统可能要对于不同扳机和亡语进行打分，
			#如何评价这些分数，以及让它们如何辨认不同的扳机
			#是否应该让不同扳机各自拥有一个评价函数，从而让这个函数开始评分的时候如果是
			return grade
			
	#根据一个game的目前状态来进行评分
	def evaluateStrategy(result, *args):
		#目前先保证整个AI体系可以正常运行，先把所有评分定为随机数，从-10至10
		return 10 * np.random.rand()
		
		
		
class RNGBranch:
	def __init__(self, player):
		self.player, self.backupGame = player, None
		self.tree, self.branching = None, False
		
	#游戏用自己的decodePlay()函数来执行操作。move包含操作类型("battle")，主体/目标的index，位置等
	
	#根据move进行游戏推演，视情况 返回单个游戏或者tree或者100次随机实验的list
	#1. 如果全程是单一结果（无RNG，发现和选择），则返回一个"!R!S"和单个game
	#2. 如果分叉结果有少量，
		#1.若开头就是选择分叉,返回"S1st"和{S_Guide: branch}
		#2.若开头是RNG分叉或者发现分叉，返回"!S1st"和一个tree
	#3. 如果RNG分叉结果太多，则根据内部是否有S分叉及其位置进行整理（开头的S分叉作出的选择成为playerMove）
	
	#操作分叉的dict_key是tuple，但是在这里movesandGuides仍然是list
	def resultsResolved(self, movesandGuides, game, resetFixedGuides=True):
		#print("Start to resolve move", movesandGuides)
		#guideMode -1:强制结束结算 0:AI实际操作, 1:随机实验中, 2:进行RSD分叉
		gameCopy, self.backupGame = game.copyGame()[0], game
		#game的fixedGuides是list，[回合中最新一步的playerMove, guide1, guide2,...]。不会随着一个game的推演而被各随机过程用掉，而是一直保留
		#guides从fixedGuides中剔除playerMove得到，并在推演过程中被RSD过程消耗掉，这些过程遇到看到适配的guide时会将其用掉同时产生一些受指示的结算
		#一般游戏推演都会重置fixedGuides和guides，但AI在实际操作时遇到发现/选择时重新进行分叉模拟时需要保留这些guides，因为它们可能保留了发现/选择之前的RNG的可能guide
		if resetFixedGuides: gameCopy.guides, gameCopy.fixedGuides = [], movesandGuides
		else: gameCopy.guides = fixedList(gameCopy.fixedGuides)
		self.tree = Branch(None, gameCopy, True) #root没有必要携带game的复制，由RNGBranch类本身负责携带
		self.tree.guide = movesandGuides #注意playerMove既可以用于AI在开始实际操作之前对一个假定的操作进行推演，也可以用于在实际操作中遇到发现/选择时对产生的copy的推演。
		gameCopy.mode, self.tree.branching = 2, True
		self.makePlays(movesandGuides[0], gameCopy)
		if self.tree.branching: #如果分叉数量没有过多，会返回单个游戏（没有出现分叉）或者全部的分叉
			if self.tree.sons: #推演过程中有分叉。如果tree前面几轮的分叉都是选择分叉，则应该把这些tree拆分
				openswithSelect, results = self.tree.splitSelectBranches() #所有连续选择分叉的可能性被视为独立且平等的key:branch
				if openswithSelect == "NotS1st": return "!S1st", self.tree #splitSelectBranches函数调用过程中不破坏self.tree
				else: return "S1st", results #以选择分叉开头，需要在playerMove后面添加选项
			else: return "!R!S", self.tree.game #若无分叉，则tree.sons为空
		else: #若分叉过多，进行100次随机实验，用平均结果估计最终的评分期望
			#随机实验时产生的guide也应该保留，从而让backupGame的复制也能循着guide到达同样结果
			ls_cat, trials, gameCopies = [], [], game.copyGame(100) #每次实验如果是选择分叉开头则记录一个dict {selection: branch}
			#[("O_!S1st", self.tree), ("O_S1st", splitBranch)]
			for gameCopy in gameCopies: #开100次branch，按理上来说内存占用不多。问题是在选择分叉的时候如何确定这些tree
				gameCopy.mode, self.tree.branching = 1, False
				if resetFixedGuides: gameCopy.guides, game.fixedGuides = [], movesandGuides
				else: gameCopy.guides = fixedList(gameCopy.fixedGuides)
				self.tree = Branch(None, gameCopy, True)
				guideLenOrig, self.tree.guide = len(movesandGuides), movesandGuides
				self.makePlays(movesandGuides[0], gameCopy)
				#下面就是判断branch是否是选择分叉开头了。  注意，分叉情况过多的情况下一定有发现和RNG分叉过程
				#root.guides里面可能会有进行到此处之前的随机过程。需要记录在推演开始前root.guides的长度和实际推演后root.guides的长度进行比较，
					#从而发现有无自由随机过程产生guide附在root.guide后面
				if guideLenOrig < len(self.tree.guides) or next(iter(self.tree.sons.keys()))[0] != "Select": #tree在根部没有选择分叉
					ls_cat.append("O_!S1st")
					trials.append(self.tree)
				else: #self.tree的根部分叉是Select分叉
					results, parents = {}, {}
					for guide, branch in self.tree.sons.items():
						parents[tuple(guide)] = branch
					while not parents:
						for guides, branch in list(parents.items()):
							parents.pop(guides, None)
							#如果子级branch的guide的长度超过1了，说明是在自由随机实验的过程中在两次选择分叉之前插入了一些随机过程
							if len(branch.guide) > 1 or next(iter(branch.sons.keys()))[0] != "Select":
								results[guides] = branch
							else:
								for guide_son, branch_son in branch.sons.items():
									parents[tuple(list(guides)+[guide_son])] = branch_son
					ls_cat.append("O_S1st")
					trials.append(results)
			return "O", ls_cat, trials
			
	#game自己会携带fixedGuides,然后自己的guides会复制这个列表的内容，用于指导分叉过程
	def gamewithGuides(self, game):
		game.guides = fixedList(game.fixedGuides) #game的fixedGuides只能复制一个fixedList给guides，防止之后的操作对fixedGuides产生影响
		playerMove = game.guides.pop(0) #playerMove用于指导游戏如何操作
		self.makePlays(playerMove, game)
		
	def cancelBranch(self):
		for branch in self.tree.findAllEnds(): branch.game.mode = -1
		
	def branchDrawCard(self, game, ID):
		deckSize = len(game.Hand_Deck.decks[ID])
		#只有我方自己抽牌的时候会发生branch，因为难以计算对方牌库中有什么牌
		if deckSize < 2 or not game.players[game.turn]: game.Hand_Deck.drawCard(ID)
		else:
			if game.mode > -1:
				if game.guides and game.guides[0][1] == "Draw":
					game.Hand_Deck.drawCard(ID, game.guides.pop(0))
				else:
					if game.mode > 1:
						if game.largeUnknownDeck(ID): self.cancelBranch()
						else:
							knownDeckSize = len(game.Hand_Deck.knownDecks[ID]["to self"])
							inds = game.Hand_Deck.returnIndicesofKnownCards(ID)
							otherSons = game.branch.createSons((('R', "Draw", ind) for ind in inds), self.backupGame.copyGame(knownDeckSize-1))
							game.Hand_Deck.drawCard(ID, inds[0]) #iterator的首项会被排除
							for son in otherSons: gamewithGuides(son.game)
					elif game.mode == 1:
						index = npchoice(game.Hand_Deck.returnIndicesofKnownCards(ID))
						game.branch.guide.append(('R', "Draw", index))
						game.fixedGuides.append(('R', "Draw", index))
						game.Hand_Deck.drawCard(ID, index)
					#注意，在抽牌的实际操作阶段，没有必要记录这个抽了哪张牌的信息，因为在追溯过程中一定都要抽这个牌库最顶端的牌
					else: game.Hand_Deck.drawCard(ID)
			else: pass
			
	#对于随机丢弃1张或者在给定的弃牌范围之内弃1张牌
	#只有我方自己弃牌的时候会发生branch
	def branchDiscardCard(self, game, ID, indices=[]):
		if len(indices) == 1: game.Hand_Deck.discardCard(ID, indices[0]) #如果给的indices只有一个元素，说明这是一个固定弃牌
		else: #如果给定的弃牌范围是空或者有多个，说明是随机进行弃牌
			if not game.players[game.turn]: #玩家控制
				if not indices: game.Hand_Deck.discardCard(ID) #没有给弃牌范围
				else: game.Hand_Deck.discard(ID, nprandint(len(game.Hand_Deck.hands[ID]))) #有给定弃牌范围，并且这个范围不止一张
			else: #AI控制
				lenInd, handSize = len(indices), len(game.Hand_Deck.hands[ID])
				if handSize < 2: game.Hand_Deck.discardCard(ID) #即使有AI控制，手牌最多一张时也是确定性的操作
				else: #手牌中有多张时。给定了弃牌范围只有一张的情况已经在上面被排除
					if game.mode > -1:
						if game.guides and game.guides[0][1] == "Discard":
							game.Hand_Deck.discardCard(ID, game.guides.pop(0))
						else:
							if game.mode > 1:
								inds = indices if lenInd > 0 else range(handSize)
								otherSons = game.branch.createSons([('R', "Discard", index) for index in inds], self.backupGame.copyGame(len(inds)-1))
								game.Hand_Deck.discardCard(ID, inds[-1])
								for son in otherSons: gamewithGuides(son.game)
							elif game.mode > -1: #随机实验和实际操作时都要记录这些guide
								index = npchoice(indices) if lenInd > 1 else nprandint(handSize)
								game.branch.guide.append(('R', "Discard", index))
								game.fixedGuides.append(('R', "Discard", index))
								game.Hand_Deck.discardCard(ID, index)
					else: pass
					
					
#是否应该让root的那个branch携带playerMove
class Branch:
	def __init__(self, parent, game, isroot=False):
		game.branch, self.game, self.guide, self.sons = self, game, [], {}
		#guide分： 纯RNG分叉，选择分叉，发现分叉 ("R", name, RNGinfo) ("S", name, selectionInfo) ("D", name, DiscoverInfo)
		if isroot: self.root, self.numEnds, self.parent = self, 1, self
		else:
			self.parent = parent
			self.root = self.parent.root
			
	#playerMove包含在self.tree.root.guide和game.fixedGuides的首项
	#每个游戏进行到这一步的时候需要把自己这一支继续分叉，产生下一级的子代，其中一支继承当前branch的game,同时返回其他支
	#创造过程中需要把自己的game移除并给予下一代。
	def createSons(self, guides, gameCopies):
		otherSons = []
		self.root.numEnds += len(gameCopies) #guides比gameCopies多一项，其末尾的那一项guide用于自己分叉
		if self.root.numEnds > 1000: #如果分叉数量过多，则取消分叉，同时返回的otherSons为[]
			self.root.branching = False
			for branch in self.findAllEnds(): branch.game.mode = -1 #-1对应所有涉及分叉的效果全部失效，然后把这些game结算完毕，准备抛弃
		else: #如果分叉情况没有超过上限,正常分叉 #对于branch自己的game不能修改branch
			#guides一般是list，但是也可能是iterator
			#list最后一项的guide供self.branch使用，而对于iterator，self.branch只能先取其第一项使用
			#但是即使guides是iterator,也依然要比gameCopies长一
			guide_0 = guides.pop() if isinstance(guides, list) else next(guides)
			commonGuide = fixedList(self.game.fixedGuides)
			self.game.fixedGuides.append(guide_0) #直接在这里修改self.game.fixedGuides,注意self.game.guides是不用修改的，因为self.game是要本函数调用后直接执行的
			self.sons = {self.game.fixedGuides[-1]: Branch(self, self.game)} #子代的sons赋予新的值
			self.guide, self.game = guide_0, None
			for guide, gameCopy in zip(guides, gameCopies):
				#不需要再对gameCopy的guides进行修改，因为当这些copy被gamewithGuides调用的时候会直接把fixedGuides赋值给guides
				son, gameCopy.fixedGuides = Branch(self.parent, gameCopy), commonGuide + [guide]
				son.guide, self.sons[guide] = guide, son #在上一代的sons里面直接添加guide~son关系
				otherSons.append(son)
			self.root.numEnds += len(gameCopies)+1
		return otherSons
		
	#不破坏本身的root，而是返回一个新的{((S1), (S2)): 子tree}
	#从根部开始，根部的guide是[playerMove, guide1, guide2...] ---对于随机实验和实际操作中的选项回溯而言，需要这些guide把一个backupGame引导到正确的状态
		#相应的，用于分叉出3个子branch的sons中的key仍然是单个选择或发现的选项
		#所以判断两个selection之间是否有RNGguide必须同时看branch的guide和sons的key
	def splitSelectBranches(self): #这个函数只会在tree确实有分叉的情况下被调用
		#当AI实际操作时面对选项，需要从backupGame生成复制，并记录之前的所有guides，推演到做出此次选择之后的状态，如果之后有可能面临选择分叉，则会在这个branch里面第一次产生分叉
		#自由随机过程产生的guide会添加到branch的guide末尾，而sons.keys只存放真正产生分叉的guide
		if next(iter(self.root.sons.keys()))[0] != "S": return "NotS1st", self.root #不是以选择分叉开头的tree都直接返回
		else: #第一层分叉是select分叉
			results, parents = {}, {}
			#key不保留playerMove，由root.guide[0]保存
			for guide, branch in self.root.sons.items(): #录入第一层分叉，key是一个列表，若之后有新的选择分叉则添加到其末尾
				parents[tuple(guide)] = branch
			while not parents: #这个parents {guide： 分叉之后的branch}
				for guides, branch in list(parents.items()):
					parents.pop(guides, None) #guide先移除，然后再根据select分叉存在与否收纳入results/parents
					#guide长度大于1（除了从父代分叉那里继承的分叉guide之外还有其他guide） 或者 下面没有分叉或者 分叉不再是select分叉的 直接移出工作区域
					if len(branch.guide) > 1 or not branch.sons or next(iter(branch.sons.keys()))[0] != "S":
						results[guides] = branch #这个guides可能是列表
					else: #下面还有选择分叉的branch会把那些子分叉都统计入工作区域
						for guide_son, branch_son in branch.sons.items():
							parents[tuple(list(guides)+[guide_son])] = branch_son
			#results是dict，内含{[possibleGuide, selection1, selection2]: branch}
			return "Select1st", results
			
	#找到root下面所有的携带不同分叉的game的最终演算结果
	def findAllEnds(self):
		root, finalBranches, branches = self.root, [], [list(root.sons.values())]
		while True:
			size = len(branches)
			for i in range(size):
				if branches[size-i-1].sons == {}: #这个branch之下没有sons，应该从工作列表中拿掉，放入finalBranches
					finalBranches.append(branches.pop(size-i-1))
				else:
					branches.append(list(branches.pop(size-i-1).sons.values()))
			if branches == []:
				break
		#返回的是[finalBranch1, finalBranch2...]
		return finalBranches
		
	def hasNoRandomness(self):
		return self.sons == {} and self.game
		
	#用于结算当前branch所携带的game的评分，并通过计算期望之后把这个branch取消收拢到上一级branch里面
	def collapseBranch(self): #将这一个分叉连同其siblings（如果有）的评分做汇总
		if len(self.parent.sons) > 1: #有分叉存在，则根据分叉原因而将
			branchReason = self.guide[0]
			if branchReason == "D":
				gradeExpected = 0
				size = len(self.parent.sons) #可以根据发现选项的size近似计算出指数拟合概率分布所需要的参数
				para1 = inverse(size, 2.24128651e-03, 2.63296083e+00, -7.17663958e-01)
				para2 = inverse(size, -2.20167491e-04, 1.96043490e+00, 5.41273319e-01)
				para3 = inverse(size, 5.91077206e-04, 2.57437175e-01, 1.91889623e+00)
				guides, grades = list(self.parent.sons.keys()), list(self.parent.sons.values())
				sortedGuidesandGrades = [(guides[i], grades[i]) for i in np.argsort(grades)]
				for i in range(2, size): #发现选项会排除评分最低的两个
					guide, grade = sortedGuidesandGrades[i]
					gradeExpected += grade * exponential(i, para1, para2, para3)
					#是否要保留guide呢
				self.parent.grade = gradeExpected
			elif branchReason == "S":
				bestGuide, grade = self.parent.sons.popitem()
				for key, value in self.parent.sons.items():
					if value.grade > grade:
						grade = value.grade
						bestGuide = value.guide
				self.parent.grade = grade
			else: #纯RNG造成的分叉
				grade = 0
				for value in self.parent.sons.values():
					grade += value.grade
				grade = grade / len(self.parent.sons)
				self.parent.grade = grade
			self.parent.sons = {}
		else: #没有其他siblings的存在，只需要把这个branch的评分交给上一代，然后把上一代的sons取消
			self.parent.grade = self.grade
			self.parent.sons = {}
			
	#返回branch所属的parent的其他子分叉,因为在resolve开始时分叉的深度就是1，不用考虑其可能是根的可能性
	def findSiblings(self):
		siblings = fixedList(self.parent.sons)
		extractfrom(self, sons)
		return siblings