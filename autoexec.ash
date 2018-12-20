#
# PSWAI: A Plate Solved Where Am I  application
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

# This script has been tried on a 2K Xiaomi Yi Action Camera 
# Hardware version: 25L Firmware version: 1.5.12
# Do you own research before using these commands as it could
# potentially brick your camera.
#
#Script created by xyc.sh 0.2.0
#ISO values: 100, 200, 400, 800, 1600, 3200, 6400, 12800, 25600
#shutter speed values: 0 == automatic, 1==7.9s, 8==7.7f, 50==6.1s. 
#100==4.6s, 200==2.7s, 400==1sec, 590==1/3sec, 600==1/5sec, 800==1/10sec, 
#900==1/15sec, 1000==1/30sec, 1100==1/50sec, 1145==1/60sec, 1200==1/80sec, 
#1275==1/125sec, 1300==1/140sec, 1405==1/250sec, 1450==1/320sec, 
#1531==1/500sec, 1607==1/752sec, 1660==1/1002sec, 1788==1/2004sec, 
#1800==1/2138, 1900==1/3675, 2000==1/6316, 2047==1/8147 (EXIF value)


# Set ISO and exposure
t ia2 -ae exp 200 200

# Noise reduction 0 off - 8196 max
t ia2 -adj tidx -1 0 -1  

# Create RAW files
#t app test debug_dump 14


# Enable ftp
sleep 2
lu_util exec 'nohup tcpsvd -u root -vE 0.0.0.0 21 ftpd -w / >> /dev/null 2>&1 &'




