#!/usr/bin/env python
#
# PSWAI: A Plate Solved Where Am I application
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
#
# This script uses json commands to the camera to take a single pic
# It then prints out the filename of the pic in the camera
# The caller can then download the pic using lftp
#
# Assumes env variable XYIIP has been set to the IP of the camera
#

import os, re, sys, time, socket

camaddr = os.environ["XYIIP"]
camport = 7878

srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    srv.connect((camaddr, camport))
except Exception as e:
    print "Error: Could not cpnnect to ", camaddr, ":", camport, " due to Exception ", e
    sys.exit(1) 

srv.send('{"msg_id":257,"token":0}')

found = 0
while found == 0:
   data = srv.recv(512)
   if "rval" in data:
        token = re.findall('"param": (.+) }',data)[0]	
        found = 1
        break


tosend = '{"msg_id":769,"token":%s}' %token
srv.send(tosend)
data=""
while "vf_start" not in data:
  data = srv.recv(512)
  if "photo_taken" in data:
     fname = re.findall('"param":"(.+)"}',data)[0] 
print fname
