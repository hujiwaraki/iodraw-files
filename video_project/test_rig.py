import skia, numpy as np
from engine import *
s=skia.Surface(W,H); c=s.getCanvas(); c.clear(hexc("#cfd8e3"))
rect(c,0,800,W,280,P("#a99a86"))
draw_person(c,250,900,1.0,MING,dict(face=0.0),t=1)
draw_person(c,500,900,1.0,MING,dict(face=0.6,walk=1.0,backpack=True,brow="worried",mouth="o",eyes="wide"),t=1)
draw_person(c,750,900,1.0,MING,dict(face=-0.6,walk=2.5,run=True,brow="determined",mouth="grin",blush=0.8),t=1)
draw_person(c,1050,900,0.9,WORKER,dict(face=0.5,arms=(30,40,-120,-10),talk=0.8,brow="worried"),t=1)
draw_person(c,1350,900,0.9,STAFF,dict(face=-0.3,mouth="smile"),t=1)
draw_person(c,1650,900,0.9,TEACHER,dict(face=0.0,sit=True),t=1)
draw_robot(c,1750,600,1.0,built=1,glow=1,t=1)
draw_subtitle(c,"Words he didn't know? He skipped them. Questions? He never asked.","不认识的词？跳过。有问题？从来不问。")
s.makeImageSnapshot().save("/tmp/claude-0/-home-user-iodraw-files/f68f4a23-b1f2-5f8c-b6cc-97aac70db429/scratchpad/rig.png")
