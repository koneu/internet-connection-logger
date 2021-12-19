# internet-connection-logger


i tried to setup a way to monitor the performance of my internet connection on the raspberry.

Turned out the rapsberry is not capable to max out the connection, which renders this kinda useless on any smaleish device.


Everything this does is already done by https://github.com/geerlingguy/internet-pi.git but i could not get it to work on the raspberry.


Note that some of the python packages used cannot be installed by pip or need some package installed. You should first try to get the packages via apt-get e.g.

sudo apt-get install python-pandas 
...

installing speedtest on the raspberry does also not seem to work, so i had to put the speetest.py next to the provided test_internet

