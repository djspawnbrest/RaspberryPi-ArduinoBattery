#!/bin/bash
parent_path=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )
mount -o remount, rw /
mount -o remount, rw /boot
sed -i 's/$/ bcm2708.vc_i2c_override=1/' /boot/cmdline.txt
sed -i '$ a \\ni2c-bcm2708\ni2c-dev' /etc/modules.conf
sed -i '$ a \\ndtparam=i2c_arm=on\ndtparam=i2s=on\ndtparam=spi=on' /boot/config.txt
chmod 755 $parent_path/resources/png/pngview
touch /recalbox/share/system/custom.sh
echo 'python '$parent_path'/main.py &' > /recalbox/share/system/custom.sh
chmod 755 /recalbox/share/system/custom.sh
reboot
