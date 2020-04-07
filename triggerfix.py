filenames = ["Basic.py",
			"Classic.py",
			#"PacksRotatedOut\\Witchwood.py",
			#"PacksRotatedOut\\Boomsday.py",
			#"PacksRotatedOut\\Rumble.py",
			"Shadows.py",
			"Uldum.py",
			"Dragons.py",
			"Galakrond.py",
			"DemonHunterInitiate.py",
			"Outlands.py",
			#"PacksRotatedOut\\LegendaryfromPast.py",
			#"PacksRotatedOut\\LegendaryfromPast_Backup.py",
			]
			
def lineStartsCardandTriggeerandDeathrattleandOption(line): #Doesn't start Minion, spell, weapon, hero, secret, quest, hero power
	if line.startswith("class "):
		if line.endswith("(Minion):\n") or line.endswith("(Spell):\n") or line.endswith("(Weapon):\n") or line.endswith("(Hero):\n") or line.endswith("(Secret):\n") or line.endswith("(Quest):\n") or line.endswith("(HeroPower):\n") or line.endswith("(Permanent):\n"):
			return True
		elif line1.endswith("(TriggeronBoard):\n") or line1.endswith("(TriggerinHand):\n") or line1.endswith("(TriggerinDeck):\n"):
			return True
		elif line1.endswith("(Deathrattle_Minion):\n") or line1.endswith("(TriggerinHand):\n") or line1.endswith("(Deathrattle_Weapon):\n"):
			return True
		elif line1.endswith("Trigger):\n") or line1.endswith("ChooseOneOption):\n"):
			return True
	return False
	
#Look at triggers
#with open("C:\\Users\\13041\\Desktop\\Python\\HearthStone\\Triggers.txt", "w", encoding="utf-8") as output:
#	for filename in filenames:
#		print("Handling ", filename)
#		with open(filename, 'r', encoding="utf-8") as input:
#			startofTrigger = None
#			intheblockofTrigger = False
#			line1 = input.readline()
#			while line1:
#				if intheblockofTrigger: #正在一个trigger之内
#					if line1.startswith("class ") and line1.startswith("class Trigger_") == False:
#						intheblockofTrigger = False
#					else:
#						output.write(line1)
#				else:
#					if line1.startswith("class Trigger_"):
#						intheblockofTrigger = True
#						output.write(line1)
#				line1 = input.readline()
#				
#				
#Look at deathrattles
#with open("C:\\Users\\13041\\Desktop\\Python\\HearthStone\\Triggers.txt", "w", encoding="utf-8") as output:
#	for filename in filenames:
#		print("Handling ", filename)
#		with open(filename, 'r', encoding="utf-8") as input:
#			intheblockofDeathrattle = False
#			line1 = input.readline()
#			while line1:
#				if intheblockofDeathrattle:
#					if line1.startswith("class "): #不可能有两个亡语连续出现
#						intheblockofDeathrattle = False
#					else:
#						output.write(line1)
#				else:
#					if line1.endswith("(Deathrattle_Minion):\n"):
#						intheblockofDeathrattle = True
#						output.write(line1)
#				line1 = input.readline()
				
#Look at non card entities for selfCopy
with open("Triggers.txt", "w", encoding="utf-8") as output:
	for filename in filenames:
		print("Handling ", filename)
		with open(filename, 'r', encoding="utf-8") as input:
			intheblockofNonCardClass = False
			line1 = input.readline()
			while line1:
				if intheblockofNonCardClass:
					if lineStartsCardandTriggeerandDeathrattle(line1): #如果读到了开始定义卡牌的一行
						intheblockofNonCardClass = False
					else:
						output.write(line1)
				else: #不计算TriggersonBoard这些场上，手牌和牌库扳机
					if lineStartsCardandTriggeerandDeathrattle(line1) == False and line1.startswith("class "):
						intheblockofNonCardClass = True
						output.write(line1)
				line1 = input.readline()