files = ["Basic.py",
		"Classic.py",
		"2021Core.py",
		"Academy.py",
		"AcrossPacks.py",
		"Barrens.py",
		"Darkmoon.py",
		"DemonHunterInitiate.py",
		"Dragons.py",
		"Galakrond.py",
		"Monk.py",
		"Outlands.py",
		"Races.py",
		"Shadows.py",
		"SV_Basic.py",
		"SV_Eternal.py",
		"SV_Fortune.py",
		"SV_Glory.py",
		"SV_Rivayle.py",
		"SV_Ultimate.py",
		"SV_Uprooted.py",
		"SVBackup.py",
		"Uldum.py",
		"CardPools.py"
		]

for filename in files:
	with open(filename, 'r', encoding="utf-8") as input:
		with open("New\\"+filename, 'a', encoding="utf-8") as output:
			line1 = input.readline()
			while line1:
				if "~Spell~" in line1 and "~Spell~" not in line1:
					words = line1.split('~')
					line1 = '~'.join(words[:4]) + "~" + '~'.join(words[4:])
					print("New line is", line1.replace('\t', ''))
				output.write(line1)
				line1 = input.readline()