from direct.interval.FunctionInterval import Wait
from direct.showbase.ShowBase import ShowBase
from panda3d.core import *
from direct.particles.ParticleEffect import ParticleEffect
from direct.gui.OnscreenText import OnscreenText
from direct.gui.DirectGui import *
from direct.interval.LerpInterval import *
from direct.interval.IntervalGlobal import Sequence, Func, Parallel
import os, time, threading, math
from direct.actor.Actor import Actor
import numpy as np

from datetime import datetime

base = ShowBase()

model = base.loader.loadModel("TotemicCall.egg")
model.reparentTo(base.render)
model.setPos(0, -0.5, -0.5)
model.setScale(6)

power = base.loader.loadModel("..\\Border_Played.glb")
power.reparentTo(base.render)
base.run()