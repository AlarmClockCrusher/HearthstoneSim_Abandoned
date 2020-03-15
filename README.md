# HearthstoneSimulator
This project uses python to simulate the running of Blizzard's online card game, Hearthstone.
To run the game, download the files and run script GUI.py, which uses pygame to provide a simplified UI for user to control two player's moves.
There are no animations and all the UI does is catching user's plays and display the result of the resolutions.
The resolution details are given in the command window output.

The comments are in English and Chinese and all in-game displays are in English.

Game.py is the skeleton of the game, which stores the lists and handlers of game information, such as minions and hands. It handles player's playing cards and battle requests.
VariousHandlers.py contains multiples handlers that take care of manas, secrets and damage, etc.
Hands.py handles the hands and decks of players.
Triggers_Auras.py defines the triggers used by cards and buff auras.
CardTypes.py defines different types of cards, such as Minion, Spell, Weapon, Hero, Hero Power, Secret and Quests.
Basic.py, Classic.py, Witchwood.py, Boomsday.py, Rumble.py, Shadows.py, Uldum.py, Dragons.py and Galakrond.py have the cards in all the expansion packs in standard mode as of March 2020.
CardIndices.py has the indices for cards in expansion packs.
Cardpool.py is for cardPool and RNGPool used by cards.
Code2CardList.py and cards.collectible.json are for converting codes to deck lists defined at the end of Hands.py
