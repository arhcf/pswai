#!/usr/bin/env python
#
# PSWAI: A Plate Solved Where Am I  application. 
# Copyright (C) 2018 arhcf (user arhcf at github 2018)
# This file is part of the pswai project.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# 
#

# This is just a client for the wiimote which is used
# as a controller for the pswai
#

import os, re, sys, time, socket
import cwiid
import subprocess
import signal
import time


def rumble(n):
   for i in range(n):
      wii.rumble = True
      time.sleep(0.3)
      wii.rumble = False
      time.sleep(0.2)


# pair with wimote
c=0
wii = None
print "Pairing with wiimote"
while not wii:
  try:
     wii=cwiid.Wiimote()
  except RuntimeError:
     if (c>60):
	print "Failed"
	quit()
     print "failed " + str(c) + "...trying again"
     c = c+1
     time.sleep(2)
     

print "Paired"
rumble(1)
wii.led = 1 
pid=0

dn = os.path.dirname(os.path.abspath(__file__))
solvecmd = os.path.join(dn, 'take_pic_solve')


# not needed
#os.environ["XYIIP"]="192.168.42.1"

# Check for Button A press
wii.rpt_mode = cwiid.RPT_BTN

while 1:
  if (wii.state['buttons'] & cwiid.BTN_A):
     print "Call take_pic_solve"
     ret = subprocess.call([solvecmd]) 
     if (ret == 0 ):
         rumble(1)
     else:
         rumble(2)

  time.sleep(0.2)



