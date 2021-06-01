import os, subprocess, sys
from PIL import Image
import shutil

def genTexCard(subdir, prefix, fps=24):
    root = os.getcwd()
    folderName = os.path.join(root, subdir)
    print(folderName, '\n')
    fileName_Output = prefix.replace('_', '') + ".egg"
    
    files = [f for f in os.listdir(folderName) if os.path.isfile(os.path.join(folderName, f)) and f.startswith(prefix) and (f.endswith(".png") or f.endswith("jpg"))]
    
    s = "C:\\Panda3D-1.10.8-x64\\bin\\egg-texture-cards -o "
    s += fileName_Output + " -fps %d "%fps
    
    for file in files:
        im = Image.open(os.path.join(folderName, file))
        size = im.size
        s += "-p %d,%d %s "%(size[0], size[1], os.path.join(subdir, file))
        
    s += "\nmove " + fileName_Output + ' ' + os.path.join(root, subdir)
    s += "\ndel " + "CreateTexCard.bat"
    
    print(s)
    with open("CreateTexCard.bat", 'w') as output:
        output.write(s)
    
    subprocess.Popen(["CreateTexCard.bat"], shell=True)
	
	
subdir = sys.argv[1]
prefix = sys.argv[2]
fps = sys.argv[3]
genTexCard(subdir, prefix, int(fps) if fps else 24)