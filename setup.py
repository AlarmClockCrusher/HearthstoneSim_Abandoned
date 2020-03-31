import sys
import os
from cx_Freeze import setup, Executable
import tkinter
import hearthstone

os.environ['TCL_LIBRARY'] = r'C:\Users\13041\AppData\Local\Programs\Python\Python37\tcl\tcl8.6'
os.environ['TK_LIBRARY'] = r'C:\Users\13041\AppData\Local\Programs\Python\Python37\tcl\tk8.6'

includes = ["tkinter"]
include_files = [r"C:\Users\13041\AppData\Local\Programs\Python\Python37\DLLs\tcl86t.dll",
            r"C:\Users\13041\AppData\Local\Programs\Python\Python37\DLLs\tk86t.dll"]
packages = ["tkinter", "hearthstone"]

# GUI applications require a different base on Windows (the default is for a console application).
base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(name = 'HearthstoneSim',version = '0.1',description = 'Single Player',author = 'Alarm Clock Crusher',
		options = {"build_exe": {"includes": includes,
								'include_files':include_files,
								'packages':packages}},
		executables = [Executable("GUI.py", base=base)])