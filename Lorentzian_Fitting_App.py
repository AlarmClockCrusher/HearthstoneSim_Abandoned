import numpy as np
from scipy import optimize
import pandas as pd
import matplotlib.pyplot as plt

import tkinter as tk
from tkinter import filedialog

import PIL.Image, PIL.ImageTk
import os


def antiLorentzBg(H, Hres_bg, antiSym_bg, dH_bg, bg):
	return antiSym_bg * (H - Hres_bg) / ((H - Hres_bg) ** 2 + (dH_bg / 2) ** 2) ** 2 + bg


def singleLorentz_AsymBg(H, Hr1, Sym1, AntiSym1, dH1, Hr2, AntiSym2, dH2, C):
	return (Sym1 + AntiSym1 * (H - Hr1)) / ((H - Hr1) ** 2 + (dH1 / 2) ** 2) ** 2 + AntiSym2 * (H - Hr2) / ((H - Hr2) ** 2 + (dH2 / 2) ** 2) ** 2 + C


def pureBackground(x, Hres, antiSym, dH, bg):
	return antiSym * (x - Hres) / ((x - Hres) ** 2 + (dH / 2) ** 2) ** 2 + bg


finalFitFunc = singleLorentz_AsymBg
background = pureBackground

def finalFitFuncWrapper(H, Hres, sym, antiSym, dH, args):
	return finalFitFunc(H, Hres, sym, antiSym, dH, *args)


def backgroundWrapper(H, args):
	return antiLorentzBg(H, *args)


sideParams = ["entry_Hres", "entry_AntiSym", "entry_dH", "entry_bg"]
labelTexts = ["Hres(G)", "AntiSym", "dH(G)", "bg"]

"""Application definition"""


class LoadFileButton(tk.Button):
	def __init__(self, GUI):
		tk.Button.__init__(self, master=GUI.window, bg="green3", text="Load File", font=("Yahei", 13))
		self.configure(command=self.respond)
		self.GUI = GUI
	
	def respond(self):
		file = self.GUI.file = filedialog.askopenfilename(title="Select  file", filetypes=(("csv files", "*.csv"), ("all files", "*.*")))
		df = pd.read_csv(self.GUI.file)
		fields = self.GUI.fields = df["Field(G)"].values
		lockins = self.GUI.lockins = df["Lockin_Y_Ave"].values if self.GUI.useYChannel.get() else df["Lockin_X_Ave"].values
		
		fig, ax = plt.subplots()
		ax.plot(fields, lockins, "-bo")
		filename = file.replace(".csv", "_BgGuess.png")
		plt.savefig(filename)
		img = PIL.Image.open(filename)  #.resize(((270, 360)))
		ph = PIL.ImageTk.PhotoImage(img)
		self.GUI.figure.configure(image=ph)
		self.GUI.figure.image = ph


class ReplotButton(tk.Button):
	def __init__(self, GUI):
		tk.Button.__init__(self, master=GUI.window, bg="green3", text="Plot Guess", font=("Yahei", 14))
		self.configure(command=self.respond)
		self.GUI = GUI
	
	def respond(self):
		vars = [float(self.GUI.entries[s].get()) for s in sideParams]
		fields, lockins = self.GUI.fields, self.GUI.lockins
		backgrounrdGuess = [background(field, vars) for field in fields]  #read params from the vars list
		#Handle the image
		fig, ax = plt.subplots()
		ax.plot(fields, lockins, "-bo")
		ax.plot(fields, backgrounrdGuess, "-ro")
		filename = self.GUI.file.replace(".csv", "_Fit.png")
		plt.savefig(filename)
		plt.close("all")
		img = PIL.Image.open(filename)
		ph = PIL.ImageTk.PhotoImage(img)
		self.GUI.figure.configure(image=ph)
		self.GUI.figure.image = ph


def sortCSVbyFreqandSave(df, filename):
	indices = df["Freq"].values.argsort()
	with open(filename, "w") as output:
		header = ','.join(list(df.columns)) + '\n'
		output.write(header)
		for i in indices:
			output.write(','.join([str(var) for var in df.iloc[i]]) + '\n')


def fitandReplaceCSV(file, GUI):
	freq = file.split('\\')[-1].split('.')[0].split('_')[-1].replace("GHz", '').replace('p', '.')
	freq = round(float(freq), 1)  #5.0
	fields, lockins = GUI.fields, GUI.lockins
	vars = [float(GUI.entries[s].get()) for s in sideParams]
	
	peakStart, peakEnd = float(GUI.entry_PeakStart.get()), float(GUI.entry_PeakEnd.get())
	try:
		start = next(i for i, field in enumerate(fields) if field > peakStart)
	except:
		start = 0
	try:
		end = next(i for i, field in reversed(enumerate(fields)) if field < peakStart)
	except:
		end = len(fields) - 1
	fields_Center, lockin_Center = fields[start:end], lockins[start:end]
	
	Hres = 0.5 * (fields_Center[lockin_Center.argmax()] + fields_Center[lockin_Center.argmin()])
	dH = np.sqrt(3) * abs(fields_Center[lockin_Center.argmax()] - fields_Center[lockin_Center.argmin()])
	signal_max, signal_min = lockin_Center.max(), lockin_Center.min()
	peakCenter = 0.5 * (signal_max + signal_min)
	antiSym = (signal_max - peakCenter) * dH ** 3 * 2 / (3 * np.sqrt(3))
	sym = (signal_max - peakCenter) * dH ** 4 / 16
	
	params = [Hres, sym, antiSym, dH] + vars
	popt, pcov = optimize.curve_fit(finalFitFunc, fields, lockins, params, maxfev=10000)
	print("Fit params for freq {} derived:".format(freq), popt)
	print("Errors:", [pcov[i][i] for i in range(len(pcov))])
	Hres, sym, antiSym, dH = popt[0:4]
	vars = popt[4:]
	
	fit_Words = file.split('/')[:-1] + ["Fit.txt"]
	fitFileName = '\\'.join(fit_Words)
	
	df_fit = pd.read_csv(fitFileName)
	try:
		i = list(df_fit["Freq"]).index(freq)
		print("Found freq in fit file")
		for item, var in zip(list(df_fit.columns)[1:], popt):
			df_fit.iloc[i][item] = var
	except:
		print("Creating a new row in fit file")
		df_new = pd.DataFrame([[freq] + list(popt)], columns=["Freq"] + list(df_fit.columns)[1:])
		df_fit = df_fit.append(df_new, ignore_index=True)
	sortCSVbyFreqandSave(df_fit, fitFileName)
	
	fig, ax = plt.subplots()
	fit = [finalFitFuncWrapper(field, popt) for field in fields]
	ax.plot(fields, lockins, "bo")
	ax.plot(fields, fit, "-r")
	ax.legend(["X", "Fit"])
	picName = file.replace(".csv", "_fit.png")
	plt.savefig(picName)
	try:
		os.remove(picName.replace("_fit.png", "_temp.png"))
		os.remove(picName.replace("_fit", "_BgGuess.png"))
	except:
		pass
	return picName, list(popt)


class AutoFitButton(tk.Button):
	def __init__(self, GUI):
		tk.Button.__init__(self, master=GUI.window, bg="green3", text="Start Fitting", font=("Yahei", 14))
		self.configure(command=self.respond)
		self.GUI = GUI
		
	def respond(self):
		picName, popt = fitandReplaceCSV(self.GUI.file, self.GUI)
		img = PIL.Image.open(picName)
		ph = PIL.ImageTk.PhotoImage(img)
		self.GUI.figure.configure(image=ph)
		self.GUI.figure.image = ph
		self.GUI.lbl_fitResult.configure(text="{}\nHres {}   Sym {}\nAntiSym {}     dH {}\nHres_bg {}     AntiSym_bg {}\ndH_bg {}      bg {}".format(
			'\\'.join(picName.split('/')[-2:]), popt[0], popt[1], popt[2], popt[3], popt[4], popt[5], popt[6], popt[7]))


class GUI:
	def __init__(self):
		self.window = tk.Tk()
		self.figure = tk.Label(self.window, text="Data and background guess\nwill be displayed here", bg="white", fg='black', font=("Yahei", 10, "bold"))
		self.file = None
		self.fields, self.lockins = None, None
		
		self.useYChannel = tk.IntVar()
		useYChannel = tk.Checkbutton(self.window, text="Use Y, not X", variable=self.useYChannel, onvalue=1, offvalue=0, font=("Yahei", 10, "bold"))
		self.btn_ReplotGuess = ReplotButton(self)
		
		self.lbl_fitResult = tk.Label(self.window, text="Fitting results:", font=("Yahei", 14))
		self.figure.grid(row=0, column=0, rowspan=9)
		self.lbl_fitResult.grid(row=10, column=0, columnspan=3)
		LoadFileButton(self).grid(row=0, column=1)
		useYChannel.grid(row=0, column=2)
		#Include the entries for parameters other than the main Lorentzian peak
		self.entries = {s: tk.Entry(self.window, font=("Yahei", 10)) for s in sideParams}
		for i, s in enumerate(sideParams):
			entry, text = self.entries[s], labelTexts[i]
			entry.insert(0, 1)
			entry.bind("<Return>", lambda e: self.btn_ReplotGuess.respond())
			tk.Label(self.window, text=text).grid(row=i + 1, column=1)
			entry.grid(row=i + 1, column=2)
		#The entry for where the peak should start and stop
		self.entry_PeakStart = tk.Entry(master=self.window, font=("Yahei", 10))
		self.entry_PeakEnd = tk.Entry(master=self.window, font=("Yahei", 10))
		numEntries = len(sideParams)
		tk.Label(self.window, text="Peak Start(G)").grid(row=numEntries + 2, column=1)
		self.entry_PeakStart.grid(row=numEntries + 2, column=2)
		tk.Label(self.window, text="Peak End(G)").grid(row=numEntries + 3, column=1)
		self.entry_PeakEnd.grid(row=numEntries + 3, column=2)
		
		self.btn_ReplotGuess.grid(row=numEntries + 1, column=1, columnspan=2)
		AutoFitButton(self).grid(row=numEntries + 4, column=1, columnspan=2)
		self.window.mainloop()


if __name__ == "__main__":
	GUI()