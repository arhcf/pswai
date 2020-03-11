#!/usr/bin/env python
#
# PSWAI: A Plate Solved Where Am I application.
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

# Usage:
# encoder.py [track] [indi]
#    track: Used for moutns that track (default is  no tracking )
#    indi: Used if you want to use indi/kstars/ekos instead of sky safari
#          defauklt is sky safari

import sys
import os
import socket
import time
from threading import *

# reads ra,dec from file and converts it into encoder values
# after subtracting hr angle from ra
# 
def radec():
    ra = "0"
    dec = "0"
    ticks = 8192

    if not os.access("/tmp/pushto/radec.txt", os.R_OK):
      return (ra,dec)
    fileo=open("/tmp/pushto/radec.txt", 'r')
    ln = fileo.readline().split()
    if (len(ln) < 3 ) or (len(ln) > 5):
       return ("0","0")
    try:
       mytm=ln[0]
       myra=float(ln[1])
       mydec=float(ln[2])
    except (ValueError, IndexError):
       print "Value error, continuing ....", ln
       return ("0","0")
    
    # If tracking is on, assume current time
    if (track == 1):
      lta = time.strftime("%H:%M:%S").split(':')
    # If tracking is off, assume time when pic was taken 
    else: 
      lta = mytm.split(':')
    tha = 15*(float(lta[0])+float(lta[1])/60+float(lta[2])/3600)
    myra = myra - tha  # subtract hour angle from ra
    if (myra < 0.0):
          myra = myra +360.0
    ra = "+%04d" % int((myra*ticks/360)%ticks)
    if(mydec>0) :
          dec  = "+%04d" % int(mydec*ticks/360) # "+" explicit
    else:
          dec = "%05d" % int(mydec*ticks/360)  # includes "-"
    ptime = "%d:%d:%d" % (int(lta[0]),int(lta[1]),int(lta[2]))
    print ptime,ra,dec,myra,mydec,tha
    fileo.close()
    return ra,dec

class client(Thread):
    def __init__(self, socket, address, mode):
        Thread.__init__(self)
        self.sock = socket
        self.addr = address
        self.mode = mode
        self.ra=0
        self.dec=0
        print "Starting thread for",address
        self.daemon = True
        self.start()


    def run(self):
        finish = 0
        while not finish:
	    rbuf=self.sock.recv(20).decode();
            if(rbuf and rbuf[0] == 'Q') :  # send ra/dec
               xra,xdec=radec()
               if (xra != "0") :
                  self.ra = xra
                  self.dec = xdec
	       sbuf="%s\t%s\r" % (self.ra,self.dec)
               self.sock.send(sbuf)
            if(rbuf and rbuf[0] == 'H') :  # send encoder resolution
               sbuf="8192-8192\r"
               self.sock.send(sbuf)
            if (mode != 1 ) :
                finish  = 1
        self.sock.close()

             
             


serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = os.environ["MYIP"]
mode = 0
argsnum = len(sys.argv)
track = 0
argi = 1
while (argi < argsnum) :
  if ( sys.argv[argi] == "indi") :
     mode = 1
  elif ( sys.argv[argi] == "track") :
     track = 1
  else :
      print "Bad option: %s" % (sys.argv[argi])
      print "Usage: encoder.py [track] [indi]"
      sys.exit(1)
  argi = argi +1

if ( mode == 1) :
    port = 4001
    print "For Indi IP: ", host," Port: ", port
else :
    mode = 0
    port = 4000
    print "For Sky Safari IP: ", host," Port: ", port
print (host)
print (port)
serversocket.bind((host, port))

serversocket.listen(5)
print ('server started and listening')
while 1:
    clientsocket, address = serversocket.accept()
    client(clientsocket, address, mode)
