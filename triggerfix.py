filenames = [#"Basic.py",
			#"Classic.py",
			#"Shadows.py",
			#"Uldum.py",
			#"Dragons.py",
			#"Galakrond.py",
			#"DemonHunterInitiate.py",
			#"Outlands.py",
			#"Academy.py",
			"Darkmoon.py"
			]

##Look at triggers
def generateTriggerFixFiles():
	with open("Triggers.txt", "w", encoding="utf-8") as output:
		for filename in filenames:
			print("Handling ", filename)
			output.write("Inspecting %s\n"%filename)
			with open(filename, 'r', encoding="utf-8") as input:
				startofTrigger = None
				intheblockofTrigger = False
				line1 = input.readline()
				while line1:
					if intheblockofTrigger: #正在一个trigger之内
						if line1.startswith("class ") and line1.startswith("class Trig_") == False:
							intheblockofTrigger = False
						else:
							output.write(line1)
					else:
						if line1.startswith("class Trig_"):
							intheblockofTrigger = True
							output.write(line1)
					line1 = input.readline()
					
	with open("Triggers1.txt", "w", encoding="utf-8") as output, open("Triggers.txt", "r", encoding="utf-8") as input:
		hasOtherVars, inInit = False, False
		line1 = input.readline()
		backupLines = []
		while line1:#处理每一行
			if line1.startswith("class Trig_"):
				if hasOtherVars:
					for line in backupLines:
						output.write(line)
				hasOtherVars = False
				backupLines = [] #每次遇到一个trig就开始重新记录这个trig的内容
			backupLines.append(line1)
			
			if "__init__" in line1:
				inInit = True
			if inInit and "self." in line1 and "self.blank" not in line1 \
				and "self.temp" not in line1 and "self.counter" not in line1 \
				and "self.makesCardEvanescent" not in line1:
				hasOtherVars = True
			if "def" in line1 and "__init__" not in line1:
				inInit = False
				
			line1 = input.readline()
			
					
#Look at deathrattles
def generateDeathrattleFixFiles():
	with open("Triggers.txt", "w", encoding="utf-8") as output:
		for filename in filenames:
			print("Handling ", filename)
			with open(filename, 'r', encoding="utf-8") as input:
				intheblockofDeathrattle = False
				line1 = input.readline()
				while line1:
					if intheblockofDeathrattle:
						if line1.startswith("class "): #不可能有两个亡语连续出现
							intheblockofDeathrattle = False
						else:
							output.write(line1)
					else:
						if line1.endswith("(Deathrattle_Minion):\n"):
							intheblockofDeathrattle = True
							output.write(line1)
					line1 = input.readline()
					
	with open("Triggers1.txt", "w", encoding="utf-8") as output, open("Triggers.txt", "r", encoding="utf-8") as input:
		hasOtherVars, inInit = False, False
		line1 = input.readline()
		backupLines = []
		while line1:#处理每一行
			if "Deathrattle_Minion" in line1 or "Deathrattle_Weapon" in line1:
				if hasOtherVars:
					for line in backupLines:
						output.write(line)
				hasOtherVars = False
				backupLines = [] #每次遇到一个trig就开始重新记录这个trig的内容
			backupLines.append(line1)
			
			if "__init__" in line1:
				inInit = True
			if inInit and "self." in line1 and "self.blank" not in line1:
				hasOtherVars = True
			if "def" in line1 and "__init__" not in line1:
				inInit = False
				
			line1 = input.readline()
			
			
			
generateTriggerFixFiles()
#generateDeathrattleFixFiles()
