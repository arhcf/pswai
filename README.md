# pswai
PSWAI: A "Plate Solved Where Am I" application for astronomy

## What it does
Takes images of the night sky with a camera, plate solves them for location and hooks it up
to Sky Safari to display current location in the sky.

## Cloudynights post with description

https://www.cloudynights.com/topic/644024-pswai-a-diy-plate-solved-push-to-for-visual-astronomy/?p=9023950

## File Descriptions
* autoexec.ash: This file controls the settings of the Xiaomi Yi Action Cam and needs to put placed in root (topmost) folder of the microsd card.
* pic.py: Takes a pic on the Xiaomi Yi Action Cam, using json commands and prints out the filename.
* take_pic_solve: This uses pic.py to take a pic on the cam, downloads it, and plate solves it, updating /tmp/pushto/radec.txt
* encoder.py: This reads RA,DEC from /tmp/pushto/radec.txt and updates [Sky Safari](https://skysafariastronomy.com/ "SkySafari").
* remote.py: This controls the raspberry pi using a wiimote over bluetooth.
* start.all: This starts  encoder.py and remote.py after setting some enviroment variables
* virtual.align: This can be used to align the output of encoder.py to sky safari without moving the scope.

## Pre Requisites
 * You need to get a plate solver. The [astrometry.net](https://github.com/dstndstn/astrometry.net "Astrometry.net") platesolver is used here as an example but you can use any other by modifying the take_pic_solve scripts.
 * Required python libraries like python-cwiid (used by remote.py for the wiimote connect)
 * lftp to get the files from the Xiaomy Yi Action cam.
 * The setup here assumes your computer uses Wifi to connect to the camera, and an ethernet connection to connect to your home network ie you need two network connections. You could also do it with one network connection by having the Yi connect to your local network, but it has a terrible range, and the image will take a long time downloading, making the plate solve lag a lot longer. If you want to do that look at the nutseynuts site in the link below on how to connect to a local network. You would also have to set XYIIP appropriately.
 
## How to run
 * Use the Xiaomi Yi app to connect to the camera, learn how to use the app, update to the lastest firmware etc.
 * Choose your options, like auto enable wifi, turn off leds, disable fisheye correction (important for plate solving), choose 8M jpeg as picture type.
 * Add autoexec.ash and an empty file called enable_info_display.script to the root (topmost) folder of the micro sd card to enable telnet to the cam.
 * You need to set 2 enviroment variables (using setenv, export etc depending on your shell)
    * XYIIP: This is the IP of camera. The hotspot IP of the camera is something like 192.168.42.1. You can use ifconfig -a to find out after you connect to the Yi hotspot.
    * MYIP: This is the IP of the computer running the scripts.
 * At this point you can run the script take_pic_solve to test out the picture taking and the platesolver.
 * You can set the above env variables in the start.all script and run it, or set the env vars in the shell, and run encoder.py and remote.py on two different windows. If you do not have a wiimote you can just rum encoder.py on one window, and run take_pic_solve on another window when you want to take a pic.
 * Pair the wiimote with the Pi soon after runnning start.all as it times out after a while.
 * On skysafari (pro/plus) you need to set the scope type to "Basic Encoder", the mount type to "Equatorial Go to" for tracking and "Equatorial Push To" for non tracking mounts. Encoder Steps to +8192 for both RA,DEC, IP address to the MYIP or IP address of the computer running these scripts, and Port Number to 4000.
 * You need to have encoder.py running on the computer before you can connect the scope in sky safari.
 * If everything works you can click the main button (Button A) on the wiimote, hear the shutter sounds, and feel the remote rumble after about 20 seconds when it updates the sky safari location. If you do not have a wiimote you can run the take_pic_solve script from a window on the computer.
 * Do a 2 star alignment in sky safari and you are good to go.
 
## Tracking
 Added a different mode for tracking mounts. "encoder.py [track] [indi] " . The option  "track" assumes the mount tracks, so keeps the Hour Angle  (HA) updating in between pics. If you do not provide option "track", it assumes the mount does not track and always uses the HA when the pic was taken. This lets you have matching views to Skysafari (or Kstars/Stellarium) if you look at the EP sometime after the pic was taken for both tracking and non tracking mounts. This helps both kinds of mounts if the platesolving lag is big too. The default options if you just run "encoder.py" are "no tracking" and "Skysafari".



## Indi support
 Added some [Indi](https://www.indilib.org/ "Indi") support to encoder.py (run "encoder.py indi"). It talks to the indi_dsc_telescope driver. Port used: 4001 (as opposed to sky safari which uses port 4000). Settings in the indi/ekos panel in Kstars, EQ mount, encoder, ticks=8192. Alignment in Indi is through Kstars. You need 2 star alignment for Kstars. Alignment is done by picking a star/object, triggering a platesolve, waiting for the kstars/indi update, and then go the star/object and right click on it and pick sync from the DSC submenu. Somehow the corsshairs do not move after the first star alignment, you only see them lock after the second alignment onwards. You can use the indi server in Stellarium as well, but I cannot see anyway to do alignment in Stellarium, but once you align using Kstars, you don't need alignment if you use the same server instance in Stellarium. The encoder.py run for Indi cannot be used by Sky Safari, but you can run another instance of encoder.py (without the indi flag) in parallel. This is in case you want to use both Sky Safari and Indi/Stellarium.
 
## Note
In Kstars/Ekos, double check the encoder ticks everytime, it tends to set it back to 4096. 
 
## Important links about the Xiaomi Yi Action Cam
 I have found the following sites useful to understand the Xiaomi Yi Action Cam
 
 https://www.tawbaware.com/xiaomiyi.htm
 
 https://dashcamtalk.com/forum/forums/yi-action-camera.153/
 
 http://nutseynuts.blogspot.com/2015/06/xiaomi-yi-action-cam-custom-scripts.html
 
 ## Discussion forum
 https://www.cloudynights.com/topic/644024-pswai-a-diy-plate-solved-push-to-for-visual-astronomy/
