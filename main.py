import os
import sys
import time
import smbus
import signal
import subprocess
from subprocess import check_output
from config import *

# Global vars
bus = smbus.SMBus(1)
WARNING = 0
LAYER = 299999
DICTIONNARY = dict({"batt":0, })

# Get Pathes
PATH = sys.path[0]
PNGVIEWPATH = PATH + PNGVIEW
VIDEOPATH = PATH + VIDEOS
ICONPATH = PATH + ICONS

# Get the screen resolution on X and Y axis
XRESOLUTION = int(check_output("fbset | grep 'x' | tr 'a-z\"-' ' ' | awk '{printf $1;}'", shell=True))
YRESOLUTION = int(check_output("fbset | grep 'x' | tr 'a-z\"-' ' ' | awk '{printf $2;}'", shell=True))

# chmod for pngview
os.system("chmod 755 " + PNGVIEWPATH + "/pngview")

# Debug
if DEBUGMSG:
    print("Screen resolution :          {}x{}".format(XRESOLUTION,YRESOLUTION))

# Positions for the choosen corner
if CORNER == 1:
	XPOS = XOFFSET
	YPOS = YOFFSET
elif CORNER == 2:
	XPOS = XRESOLUTION - XOFFSET
	YPOS = YOFFSET
elif CORNER == 3:
	XPOS = XRESOLUTION - XOFFSET
	YPOS = YRESOLUTION - YOFFSET
elif CORNER == 4:
	XPOS = XOFFSET
	YPOS = YRESOLUTION - YOFFSET

def changeIcon(icon, state, chg):
	global LAYER
	global DICTIONNARY

	#LAYER -= 1 # Useless ???
	cmd = '{}/pngview'.format(PNGVIEWPATH)
	arg1 = '-b 0'
	arg2 = '-l {}'.format(LAYER)
	arg3 = '-x {}'.format(XPOS)
	arg4 = '-y {}'.format(YPOS)
	img = '{}/{}{}_{}.png'.format(ICONPATH, icon, state, chg)

	# New image
	popen = subprocess.Popen([cmd, arg1, arg2, arg3, arg4, img])
	time.sleep(2)

	# Get the last id of pngview for this specific icon
	pid = DICTIONNARY[icon]
	# Remove previous icon if it exist
	if pid != 0:
		os.kill(pid, signal.SIGTERM)
	# Get the process id of the new image
	new_pid = popen.pid
	# Update the dictionnary
	if new_pid != "":
		DICTIONNARY[icon] = new_pid
		
	# Debug
	if DEBUGMSG:
		print("Pngview previous pid was {} for {} icon".format(pid, icon))
		print("Change {} icon to {}".format(icon, state))
		print("Pngview pid is now {} for {} icon".format(new_pid, icon))

def playClip(clip):
	global WARNING
	global VIDEOPATH
	if clip == "alert" and WARNING != 1:
		os.system("/usr/bin/omxplayer --no-osd --layer 999999 " + VIDEOPATH + "/alert.mp4 --alpha 160")
		WARNING = 1
	elif clip == "shutdown":
		os.system("/usr/bin/omxplayer --no-osd --layer 999999 " + VIDEOPATH + "/timer.mp4 --alpha 160;shutdown -h now")

def changePerc(prc):
    result = 0
    if 95 <= prc <= 100:
        result = 100
    elif 85 <= prc <= 94:
        result = 90
    elif 75 <= prc <= 84:
        result = 80
    elif 65 <= prc <= 74:
        result = 70
    elif 55 <= prc <= 64:
        result = 60
    elif 45 <= prc <= 54:
        result = 50
    elif 35 <= prc <= 44:
        result = 40
    elif 25 <= prc <= 34:
        result = 30
    elif 15 <= prc <= 24:
        result = 20
    elif 5 <= prc <= 14:
        result = 10
    elif 0 <= prc <= 4:
        result = 0
    return result

def checkBattery():
	try:
		global WARNING
		VoltMult = (Rh + Rl) / Rl
		buf = bus.read_i2c_block_data(address,0x00,3)
		AnalogPin = buf[0] << 8 | buf[1]
		voltage = AnalogPin * VoltMult * VRef / 1023
		prcnt = int(round( ((voltage - cell_min) * 100) / (cell_max - cell_min) ))
		if prcnt < 0:
			prcnt = 0
		elif prcnt > 100:
			prcnt = 100
		res = changePerc(prcnt)

		if DEBUGMSG:
			print("ADC value: {} ({}V)".format(AnalogPin, voltage))

		# Battery monitor
		chg = str(int(buf[2])) # read charger flag (charger - 1 | 0 - not)
		changeIcon("batt", res, chg)

		if prcnt > 25:
			WARNING = 0

		if 10 <= prcnt <= 20:
			playClip("alert")
		elif prcnt <= 9 and int(buf[2]) != 1:
			playClip("shutdown")

	except:
		pass
		if DEBUGMSG:
			print("ERR")
		time.sleep(2)

def endProcess(signalnum = None, handler = None):
    os.system("killall pngview")
    exit(0)

# Prepare handlers for process exit
signal.signal(signal.SIGTERM, endProcess)
signal.signal(signal.SIGINT, endProcess)

# Main function
while True:
    checkBattery()

    # Debug
    if DEBUGMSG:
        print("GLOBAL Variables are : \nWARNING = {}\nLAYER = {}\n PID = {}".format(WARNING, LAYER, DICTIONNARY))

    # Wainting for next loop
    time.sleep(REFRESH_RATE)
