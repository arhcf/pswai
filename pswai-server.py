#!/usr/bin/env python2.7

# PSWAI: A Plate Solved Where Am I application.
# Copyright (C) 2020 arhcf (user arhcf at github 2020)
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
# pswai-server.py [track] 
#    track: Used for moutns that track (default is  no tracking )
#    Only has sky safari support. No indi/stellarium support
#

import socket
import sys,traceback
import serial
import time
import datetime
import select
import os
import commands
import threading
from math import modf

dec_dir = -1
current_ra = 10.0
current_dec = 10.0
target_ra = 0.0
target_dec = 0.0
latitude = 0.0
longitude = 0.0
time_zone = 1
local_time = 0
local_date = 0
hp = 1
track = 0

skt = 0
moving = 0
move_func=0
move_num=1
debug=False
ptime=0.0
solvecmd=""



def main():
    global skt,track,solvecmd

    if (len(sys.argv) == 2):
        if (sys.argv[1] == "track"):
            track = 1
        else:  # set ptime accurately
            track = 0
            cts = time.strftime("%H:%M:%S").split(':')
            ptime = 15*(float(cts[0])+float(cts[1])/60+float(cts[2])/3600)

    dn = os.path.dirname(os.path.abspath(__file__))
    solvecmd = os.path.join(dn, 'take_pic_solve')

    (st,op)=commands.getstatusoutput('mkdir -p /tmp/pushto')
    # socket
    skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    myip = os.environ["MYIP"]
    myport = 4000
    print myip,":",myport
    skt.bind((myip,myport))
    skt.listen(5)
    #debug = True

    while True:
        client, address = skt.accept()
        #print "Connected ....",address
        data=""
        try:
            while True:
                data += client.recv(16)
                if not data:
                    break;
                #if debug:
                #    print data
                while data:
                    while data[0:1] == "#":
                        # drop leading #s
                        data = data[1:]
                    if not data:
                        break
                    if "#" in data:
                        # cmd is string upto # 
                        scmd = data[:data.index("#")] 
                        data = data[len(scmd)+1:]
                        cmd, value = scmd[:3], scmd[3:]
                        #if debug:
                        #    print "Cmd is ",cmd," ",value
                    else:
                        scmd = data
                        cmd = scmd[:3]
                        value = scmd[3:]
                        data = ""
                    if not cmd:
                        print "Missing command?"
                    elif cmd in lx200_cmds:
                        if value:
                            #if debug:
                            #    print "Command %r, args %r" % (cmd,value)
                            resp = lx200_cmds[cmd](value)
                        else:
                            resp = lx200_cmds[cmd]()
                        if resp:
                            #if debug:
                            #    print "Command ",cmd, " returns ", resp, " sending back"
                            client.sendall(resp)
                            #if debug:
                            #    print "Command ",cmd, " done"
                        else:
                            if debug:
                                print "Command ",cmd, " no response"
                    else:
                        print "Command ",scmd," ", cmd, " ",data," not found"
        finally:
            client.close()
                        

    
# Degrees -> HH:MM.M                        
def d_to_hhmmt(d):
    if d < 0.0:
        d = d + 360
    m,h = modf(d/15.0)
    f,m = modf(m*60.0)
    t = round(f*10.0)
    return "%02i:%02i.%01i#" % (h,m,t)

# Degrees -> HH:MM:SS
def d_to_hhmmss(d):
    if d < 0.0:
        d = d + 360
    m,h = modf(d/15.0)
    f,m = modf(m*60.0)
    s = round(f*60.0)
    return "%02i:%02i:%02i#" % (h,m,s)

# Degrees -> +/-DD*MM
def d_to_sddmm(d):
    if d < 0.0:
        d = abs(d)
        sgn = "-"
    else:
        sgn = "+"
    m,h = modf(d)
    m = round(m*60.0)
    return "%s%02i:%02i#" % (sgn,h,m)

# Degrees -> +/-DD*MM'SS
def d_to_sddmmss(d):
    if d < 0.0:
        d = abs(d)
        sgn = "-"
    else:
        sgn = "+"
    m,h = modf(d)
    f,m = modf(m*60.0)
    s = round(f*60.0)
    return "%s%02i:%02i:%02i#" % (sgn,h,m,s)

# HH:MM.M or HH:MM:SS -> Degrees
def hhmmt_to_d(s):
    words = s.split(":")
    if len(words) == 2:
        d = (int(words[0])+float(words[1])/60.0)*15.0
    else:
        d = (int(words[0])+int(words[1])/60.0+int(words[2])/3600.0)*15.0
    return d


# +/-DD*MM or +/-DD*MM:SS -> Degrees        
def sddmm_to_d(s):
    if s[3] != "*":
        print "Value error ", s
    if s[0] == "+":
        sgn = 1
    elif s[0] == "-":
        sgn = -1
    else:
        print "Bad sign ", s
    d = int(s[1:3])
    sec = 0
    if  len(s) == 6 :
        m = int(s[4:6])
        sec = 0
    elif len(s) == 9 and s[6] == ":":
        m  = int(s[4:6])
        sec= int(s[7:9])
    else:
        print "Bad value ", s
    d = sgn*(d + m/60.0 + sec/3600.0)
    return d

# Do a cpature & platesolve
# Will be started as a Thread from scope_sync
def cap_solve():
    global current_ra,current_dec,track,ptime,solvecmd

    (st,op)=commands.getstatusoutput(solvecmd)
    if not os.access("/tmp/pushto/radec.txt", os.R_OK):
          return 
    fileo=open("/tmp/pushto/radec.txt", 'r')
    ln = fileo.readline().split()
    if (len(ln) < 3 ) or (len(ln) > 5):
       return 
    try:
       mytm=ln[0]
       myra=float(ln[1])
       mydec=float(ln[2])
    except (ValueError, IndexError):
       print "Value error, continuing ....", ln
       return 

    time_pic = mytm
    cts = time.strftime("%H:%M:%S").split(':')
    pts = time_pic.split(':')
    ctime = 15*(float(cts[0])+float(cts[1])/60+float(cts[2])/3600)
    ptime = 15*(float(pts[0])+float(pts[1])/60+float(pts[2])/3600)

    if (track != 1):    # mount is not tracking so adjust RA
        current_ra = myra + (ctime-ptime)
        if (current_ra < 0.0):
             current_ra = current_ra +360.0
        if debug:
            print "current_ra %03.2f = %03.2f - (%03.2f - %03.2f)" % (current_ra,myra,ctime,ptime)
    else:
        current_ra = myra
    current_dec = mydec
    if debug:
        print "Current Location: ",current_ra,current_dec

# This does not do a sync
# Instead it does a platesolve and update current_ra and current_dec
def scope_sync():
    #print "Sync to target %f, %f" % (target_ra,target_dec)
    if moving == 1:
        print "Cannot capture photo while slewing, stop first"
        return "1"    
    capsolve = threading.Thread(target=cap_solve)
    capsolve.start()
    return " M31 EX GAL MAG 3.5 SZ178.0'#" 


def get_dec():
    global current_dec
    if hp == 1:
        s = d_to_sddmmss(current_dec)
    else:
        s = d_to_sddmm(current_dec)
    #print "Client Get Dec ", s
    return s
    
def get_ra():
    global current_ra,ptime
    cts = time.strftime("%H:%M:%S").split(':')
    ctime = 15*(float(cts[0])+float(cts[1])/60+float(cts[2])/3600)
    if (track != 1):    # mount is not tracking so adjust RA
        temp_ra = current_ra + (ctime-ptime)
        if (temp_ra < 0.0):
             temp_ra = temp_ra +360.0
    else:
        temp_ra = current_ra
    if hp == 1:
        s = d_to_hhmmss(temp_ra)
    else:
        s = d_to_hhmmt(temp_ra)
    #print "Client Get RA ", s
    return s

def move_to_target():
    return "2Sorry, no goto"

def set_target_ra(s):
    global target_ra
    if debug:
        print "Set target RA ",s
    try:
        target_ra = hhmmt_to_d(s.strip())
        if debug:
            print "Target RA ",s," = ",target_ra
        return "1"
    except:
        print "Error in setting target RA"
        return "0"
    
def set_target_dec(s):
    global target_dec
    if debug:
        print "Set target DEC ",s
    try:
        target_dec = sddmm_to_d(s.strip())
        if debug:
            print "Target Dec ",s," = ",target_dec
        return "1"
    except:
        print "Error in setting target DEC"
        return "0"

def set_latitude(s):
    if debug:
       print "Client latitude ", s
    return "1"
def set_longitude(s):
    if debug:
        print "Client longitude ", s
    return "1"
def set_local_timezone(s):
    if debug:
        print "Client Timezone ",t
    return "1"
def set_local_date(dt):
    if debug:
        print "Client Local Date ",dt
    return "1"
def set_local_time(t):
    if debug:
        print "Client Local Time ",t
    return "1"
def set_precision():
   global hp
   if debug:
       print "Client Precision Toggle"
   if (hp== 0):
       hp = 1
   else:
       hp = 0

def return_one(value=None):
   return "1"

def return_none(value=None):
   return None
       

       
lx200_cmds = {
    #LX200 commands:
    ":CM": scope_sync,
    ":GD": get_dec,
    ":GR": get_ra,
    ":Me": return_none, #start moving East
    ":Mn": return_none, #start moving North
    ":Ms": return_none, #start moving South
    ":Mw": return_none, #start moving West
    ":MS": move_to_target,
    ":Q":  return_none, #abort all current slewing
    ":Qe": return_none, #abort slew East
    ":Qn": return_none, #abort slew North
    ":Qs": return_none, #abort slew South
    ":Qw": return_none, #abort slew West
    ":RC": return_none, #set slew rate to centering (2nd slowest)
    ":RG": return_none, #set slew rate to guiding (slowest)
    ":RM": return_none, #set slew rate to find (2nd fastest)
    ":RS": return_none, #set Slew rate to max (fastest)
    ":Sd": set_target_dec,
    ":Sr": set_target_ra,
    ":St": set_latitude,
    ":Sg": set_longitude,
    ":Sw": return_one, #set max slew rate
    ":SG": set_local_timezone,
    ":SL": set_local_time,
    ":SC": set_local_date,
    ":U":  set_precision,
}       
       

if __name__=="__main__":
    main()
