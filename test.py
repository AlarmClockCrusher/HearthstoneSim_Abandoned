from Outlands import Outlands_Cards
from Academy import Academy_Cards
from Darkmoon import Darkmoon_Cards
from Barrens import Barrens_Cards
from Stormwind import Stormwind_Cards

current_Class = ''
for card in Barrens_Cards:
	if "~Uncollectible" not in card.index:
		Class = card.Class
		if ',' not in card.Class and card.Class != current_Class:
			print('\n#'+card.Class)
			current_Class = card.Class
		print(card.__name__, end=", ")