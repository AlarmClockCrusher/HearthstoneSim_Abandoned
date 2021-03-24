from PIL import Image
 
# Opens a image in RGB mode 
im = Image.open("Netherwalker.png") 

# Size of the image in pixels (size of orginal image) 
# (This is not mandatory) 
width, height = im.size

# Setting the points for cropped image 
left = 96 #width*0.2
top = 80 #height*0.9
right = 276 #width * 0.8
bottom = 260# height * 0.5

# Cropped image of above dimension 
# (It will not change orginal image) 
im1 = im.crop((left, top, right, bottom)) 
  
# Shows the image in image viewer 
#im1.show() 
im1.save("Netherwalker.png")