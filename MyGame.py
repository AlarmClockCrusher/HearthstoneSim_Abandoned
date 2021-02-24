#from panda3d.core import loadPrcFile
#loadPrcFile("config/conf.prc")

from direct.showbase.ShowBase import ShowBase
from panda3d.core import loadPrcFileData

confVars = """
win-size 1280 720
window-title My Game
show-frame-rate-meter True
"""

loadPrcFileData('', confVars)



class MyGame(ShowBase):
	def __init__(self):
		super().__init__()
		self.disableMouse()
		self.accept("mouse1", self.mouse_click) #Left click action
		self.accept("mouse1-up", self.mouse_click)
		self.accept("mouse2", self.mouse_click) #middle click(scrolling wheel)
		self.accept("mouse2-up", self.mouse_click)
		self.accept("mouse3", self.mouse_click) #Right click
		self.accept("mouse3-up", self.mouse_click)
		
		#self.taskMgr.add(self.update_Continous, "update_Continous") #Updates each frame
		self.taskMgr.add(self.update_Ifin, "update_Ifin")  #Updates each frame
	
	def mouse_click(self):
		md1 = self.win.getPointer(0) #According to the current window size, max is 1280 720
		print(md1.getX(), md1.getY()) #top LEFT is (0, 0), bottom RIGHT is (max_X, max_Y)
		md2 = self.mouseWatcherNode.getMouse() #Returns the relative position -1~1 in the x and y direction
		print(md2.getX(), md2.getY()) #top right is the 1st quadron (+1, +1), bottom left is the 3rd(+1, -1)
		
	#This method prints the coordinates of the cursor the last time it's detected in the window.
	#If the mouse leaves the window, it would continuously report the last position it was still in.
	def update_Continous(self, task):
		md = self.win.getPointer(0)
		print(md.getX(), md.getY())
		return task.cont
	#Reports the coordinate of the mouse only if it is in the window
	def update_Ifin(self, task):
		if self.mouseWatcherNode.hasMouse():
			x = self.mouseWatcherNode.getMouseX()
			y = self.mouseWatcherNode.getMouseY()
			print(x, y)
		return task.cont
		#box = self.loader.loadModel("models/box")
		#box.setPos(0, 10, 0)
		#box.reparentTo(self.render)
		#
		#panda = self.loader.loadModel("models/panda")
		#panda.setPos(-10, 10, 0)
		#panda.setScale(0.1, 0.1, 0.1)
		#panda.reparentTo(self.render)
		#
		##We can use blend2bam to convert a blend file into a bam file that can be loaded in panda3D
		#cube = self.loader.loadModel("models/output.bam")
		#cube.setPos(-15, 10, 0)
		#cube.setScale(0.5, 0.5, 0.5)
		#cube.reparentTo(self.render)
		##self.disableMouse() #This disables the default camera control, not the entire mouse response
		
if __name__ == "__main__":
	game = MyGame()
	game.run()