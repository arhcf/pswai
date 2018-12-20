# pswai
PSWAI: A "Plate Solved Where Am I" application for astronomy

## File Descriptions
* autoexec.ash: This file controls the settings of the Xiaomi Yi Action Cam and needs to put placed in root (topmost) folder of the microsd card.
* pic.py: Takes a pic on the Xiaomi Yi Action Cam, using json commands and prints out the filename.
* take_pic_solve: This uses pic.py to take a pic on the cam, downloads it, and plate solves it, updating /tmp/pushto/radec.txt
* encoder.py: This updates RA,DEC read from /tmp/pushto/radec.txt and updates [Sky Safari](https://skysafariastronomy.com/ "SkySafari").
* remote.py: This controls the raspverry pi using a wiimote over bluetooth.
* start.all: This starts  encoder.py and remote.py after setting some enviroment variables
* virtual.align: This can be used to align the output of encoder.py to sky safari without moving the scope.
