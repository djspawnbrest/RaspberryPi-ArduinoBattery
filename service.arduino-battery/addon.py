import time
import os
import signal
import subprocess
import xbmcaddon
import xbmcgui
import sys
sys.path.append('/storage/.kodi/addons/virtual.system-tools/lib')
import smbus

# Config
bus = smbus.SMBus(1)
address = 0x20
iconState = ""
ADDON = xbmcaddon.Addon()
CWD = ADDON.getAddonInfo('path').decode("utf-8")
PNGVIEWPATH = xbmc.translatePath( os.path.join( CWD, 'resources', 'png' ).encode("utf-8") ).decode("utf-8")
ICONPATH = xbmc.translatePath( os.path.join( CWD, 'resources', 'icons' ).encode("utf-8") ).decode("utf-8")

# Calculate screen width
win = xbmcgui.Window(10000)
width = win.getWidth()
height = win.getHeight()
x = width - 42
y = height - 42

# Capacity config
VRef = 1.082
Rh = 46.87 # kOm
Rl = 10.11 # kOm
cell_min = 3.20 # min charge cell
cell_max = 4.15 # max charge cell
oldPrc = None
oldChg = None
# Process kill
kill = False

# chmod for pngview
os.system("chmod 755 " + PNGVIEWPATH + "/pngview")

def changeicon(percent, flag):
    global iconState
    global kill
    if iconState != percent:
        iconsState = percent
        kill = True
        os.system(PNGVIEWPATH + "/pngview -b 0 -l 3000 -x " + str(x) + " -y " + str(y) + " " + ICONPATH + "/batt" + percent + "_" + flag + ".png &")

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

if __name__ == '__main__':
    while not xbmc.abortRequested:
        # code
        try:
            VoltMult = (Rh + Rl) / Rl
            buf = bus.read_i2c_block_data(address,0x00,3)
            AnalogVal = buf[0] << 8 | buf[1]
            Volt = AnalogVal * VoltMult * VRef / 1023
            prcnt = int(round( ((Volt - cell_min) * 100) / (cell_max - cell_min) ))
            if prcnt < 0:
                prcnt = 0
            elif prcnt > 100:
                prcnt = 100

            res = changePerc(prcnt)

            if res != oldPrc or buf[2] != oldChg:
                oldChg = buf[2]
                oldPrc = res
                if kill:
                    kill = False
                    os.system("killall pngview")

                chg = str(int(buf[2]))
                changeicon(str(res), chg)
        except:
            pass
            time.sleep(5) # seconds
        xbmc.sleep(2000) # 1000 - 1 time on second
