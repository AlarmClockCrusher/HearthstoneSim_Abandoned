# HearthstoneSimulator  #炉石传说模拟(更新到2020年4月1日)
Simulation of Hearthstone game using python (Up to date Apr 1st 2020)

This project's goal is to use python codes to create a simulator of the Hearthstone game. The UI adopts tkinter and makes an UI where a single user controls the mulligan and playing of both sides.
本项目的目标是用python创建一个炉石传说游戏的模拟。UI采用tkinter并依靠一个玩家操纵游戏中双方的抽牌和行动。
The game currently emulates the standard card pool as of the beginning of the Year of Phoenix. The expansion packs include Basic, Classic, Rise of Shadows, Saviors of Uldum, Descent of Dragons, Galakrond's Awakening and Ashes of Outlands.
本游戏目前模拟的是凤凰年开始时的标准牌池。拓展包包括基础，经典，暗影崛起，奥丹姆奇兵，巨龙降临，迦拉克隆的觉醒以及外域的灰烬。
To run the game, either use python to run the GUI.py or simply open the GUI.exe. You will need to select the heroes for the game and enter and deck codes at the bottom right part of the UI. If you enter nothing for decks, defaults decks will be used(editable at the end of Hand.py). Then click Confirm to start the mulligan.
要运行游戏，或使用python来运行GUI.py，或直接打开GUI.exe。你需要在UI的右下方的选项卡中选择对战英雄，并在下方的两个文本框中输入双方的牌组代码。如果没有输入代码则会加载默认牌组(在Hand.py末尾中可以修改)然后点击Confirm开始换牌流程。
There are no animations of the play resolutions. The UI simply allows player to select characters for plays and shows the final results of each play resolution. The resolutions will be printed 'System Output' panel on the top right corner.
结算过程没有动画显示。UI只是允许玩家选择角色，并显示结算的最终结果。结果过程会输出到右上角的"System Output"方框中。
The general rule is left clicks can select subjects or target and right clicks on cards/characters will cancel your current selections. 
总体规则为鼠标左键选择角色，右键单击取消当前选择。
