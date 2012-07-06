#! /usr/bin/env python

# TODO integrate this file into the main script

import sys
import os, shutil

shutil.rmtree("wavs")
os.mkdir("wavs")
i = 0

f = open("toc.toc","w")
f.write("CD_DA\n")

for mp3 in sorted(os.listdir("./mp3s")):
	print mp3
	i += 1
	os.system("ffmpeg -i ./mp3s/\""+mp3+"\"  wavs/"+str(i)+".wav")
	f.write("TRACK AUDIO\n")
	f.write("FILE \"wavs/"+str(i)+".wav\" 0 \n\n")

f.close()


# cdrdao write --driver generic-mmc --device /dev/sr1 toc.toc

