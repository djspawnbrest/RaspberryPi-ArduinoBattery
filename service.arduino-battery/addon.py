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
bus = smbus.SMBus(1) # init i2c bus
address = 0x20 # i2c arduino addres
iconState = ""
ADDON = xbmcaddon.Addon()
CWD = ADDON.getAddonInfo('path').decode("utf-8")
PNGVIEWPATH = xbmc.translatePath( os.path.join( CWD, 'resources', 'png' ).encode("utf-8") ).decode("utf-8")
VIDEOPATH = xbmc.translatePath( os.path.join( CWD, 'resources', 'video' ).encode("utf-8") ).decode("utf-8")
ICONPATH = xbmc.translatePath( os.path.join( CWD, 'resources', 'icons' ).encode("utf-8") ).decode("utf-8")

# Capacity config
# VBat <--[Rh]--(AnalogPin)--[Rl]--| GND
VRef = 1.082 # Vref arduino (must be measured)
Rh = 46.87 # kOm
Rl = 10.11 # kOm
cell_min = 3.20 # min charge cell (volts)
cell_max = 4.15 # max charge cell (volts)
oldPrc = None
oldChg = None
# Process kill flag
kill = False
# icon offset (px)
offset = 42

# chmod for pngview
os.system("chmod 755 " + PNGVIEWPATH + "/pngview")

def changeicon(percent, flag):
    global iconState
    global kill
    global offset
    if iconState != percent:
        iconsState = percent
        kill = True
        # Calculate screen width
        x = xbmcgui.getScreenWidth() - offset
        y = xbmcgui.getScreenHeight() - offset
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
            buf = bus.read_i2c_block_data(address,0x00,3) # read values from i2c (arduino)
            AnalogVal = buf[0] << 8 | buf[1] # convert byte values to Vbat analog value from arduino
            Volt = AnalogVal * VoltMult * VRef / 1023 # convert in battery voltage
            prcnt = int(round( ((Volt - cell_min) * 100) / (cell_max - cell_min) )) # convert battery voltage to Capacity
            if prcnt < 0:
                prcnt = 0
            elif prcnt > 100:
                prcnt = 100

            res = changePerc(prcnt) # get icon Capacity value

            if res != oldPrc or buf[2] != oldChg:
                oldChg = buf[2]
                oldPrc = res
                if kill:
                    kill = False
                    os.system("killall pngview")

                chg = str(int(buf[2])) # read charger flag (charger - 1 | 0 - not)
                changeicon(str(res), chg)

            if res == 0 and int(buf[2]) == 0:
                xbmc.executebuiltin('XBMC.PlayMedia(' + VIDEOPATH + '/timer.mp4)')
                time.sleep(60)
                os.system("shutdown -h now")

        except:
            pass
            time.sleep(5) # sleep 5 seconds
        xbmc.sleep(2000) # 1000 - 1 time on second