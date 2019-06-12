"""
" Edit below this line to fit your needs
"""
# Arduino i2c address
address = 0x20

# Path to pngview, video and icons (relative paths)
PNGVIEW = "/resources/png"
VIDEOS = "/resources/video"
ICONS = "/resources/icons"

# Capacity config
# Arduino AREF (need to measure)
VRef = 1.082

# BATT <--[Rh]--AnalogPin--[Rl]--| GND
Rh = 46.87 # kOhm
Rl = 10.11 # kOhm

# min and max charge/discharge value of battery
cell_min = 3.20 # min charge cell
cell_max = 4.15 # max charge cell

# Display some debug values when set to 1, and nothing when set to 0
DEBUGMSG = 1

# Corner is (1)TopLeft, (2)TopRight , (3)BottomRight, (4)BottomLeft
CORNER = 1

# Offset position from corner
XOFFSET = 25
YOFFSET = 15

# Refresh rate (s)
REFRESH_RATE = 10
