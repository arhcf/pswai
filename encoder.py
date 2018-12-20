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
#
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
    if not os.access("/tmp/pushto/radec.txt", os.R_OK):
      return (ra,dec)
    fileo=open("/tmp/pushto/radec.txt", 'r')
    ln = fileo.readline().split()
    if (len(ln) < 2 ) or (len(ln) > 5):
       return ("0","0")
    try:
       myra=float(ln[0])
       mydec=float(ln[1])
    except (ValueError, IndexError):
       print "Value error, continuing ....", ln
       return ("0","0")
    lta = time.strftime("%H,%M,%S").split(',')
    tha = 15*(float(lta[0])+float(lta[1])/60+float(lta[2])/3600)
    myra = myra - tha  # subtract hour angle from ra
    if (myra < 0.0):
       myra = myra +360.0
    ra = "+%d" % int((myra*8192/360)%8192)
    if(mydec>0) :
        dec  = "+%d" % int(mydec*8192/360)
    else:
        dec = "%d" % int(mydec*8192/360)
    print ra,dec,myra,mydec,tha
    fileo.close()
    return ra,dec

class client(Thread):
    def __init__(self, socket, address):
        Thread.__init__(self)
        self.sock = socket
        self.addr = address
        self.ra=0
        self.dec=0
        print "Starting thread for",address
        self.start()


    def run(self):
            #while 1:
	    rbuf=self.sock.recv(20).decode();
            if(rbuf and rbuf[0] == 'Q') :
               xra,xdec=radec()
               if (xra != "0") :
                  self.ra = xra
                  self.dec = xdec
	       sbuf="%s\t%s\r" % (self.ra,self.dec)
               self.sock.send(sbuf)

             
             


serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

host = os.environ["MYIP"]
port = 4000
print (host)
print (port)
serversocket.bind((host, port))

serversocket.listen(5)
print ('server started and listening')
while 1:
    clientsocket, address = serversocket.accept()
    client(clientsocket, address)
