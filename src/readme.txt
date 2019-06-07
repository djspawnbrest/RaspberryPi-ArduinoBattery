First install lxpanel-dev:
    type in terminal 'sudo apt-get install lxpanel-dev'

make command:
    gcc -Wall `pkg-config --cflags gtk+-2.0 lxpanel` -shared -fPIC ardbatt.c -o ardbatt.so `pkg-config --libs lxpanel`