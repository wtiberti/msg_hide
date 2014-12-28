#!python

# Simple message hiding software
#
# -> How? 3 bit each image pixel!
# 
# This small script change source image pixels so that, the LSB of each RGB component of each
# pixel in the image contains a bit of the message string (supposed ASCII).
# It stores the msg bytes one after the other and stores message bits from the MSB to LSB
# (big-endian). A NUL character is appended to the msg (if there's enough space)
#
# Example:
# msg = "abc\0", bitwise = AAAAAAAABBBBBBBBCCCCCCCC00000000
# 
# so, for each pixel, P, it changes the LSB of each of the RBG components
# ex. 1=(AAA), 2=(AAA), 3=(AAB), 4=(BBB), 5=(BBB), 6=(BCC), 7=(CCC)
#	  8=(CCC), 9=(000), 10=(000), 11=(00X)
#
# Note: X is the original bit 
#
# syntax:
#	msg_hide.py read <in_file>
#	msg_hide.py write <in_file> <out_file> "<msg>"
#
#
# LICENSE: GPLv3
# Author: Walter Tiberti <wtuniv@gmail.com>

import sys
from PIL import Image

def parseMsg( image ):
	buf = ""
	bitcount = 0
	actual = 0
	total_bytes = 0
	for x in range( image.size[0] ):
		for y in range( image.size[1] ):
			pixel = image.getpixel( (x,y) )
			for i in [0,1,2]:
				actual += pixel[i] & 1
				bitcount+=1
				if bitcount>=8:
					buf += chr(actual)
					bitcount=0
					total_bytes+=1
					if actual == 0:
						return buf
					actual = 0
				else:
					actual<<=1
	return buf

def writeMsg( image, msg ):
	if (len(msg)*8)/3 > image.size[0]*image.size[1]:
		return False
	if len(msg)==0:
		return False
	shift = 7
	i = 0
	for x in range( image.size[0] ):
		for y in range( image.size[1] ):
			pixel = image.getpixel( (x,y) )
			pixel = list(pixel)
			for j in range(len(pixel)):
				if( ((ord(msg[i])>>shift)&1) != 0 ):
					pixel[j]|=1
				else:
					pixel[j]&=0xFE
				shift-=1
				if shift<0:
					i+=1
					shift=7
					if i>=len(msg):
						image.putpixel( (x,y), tuple(pixel) )
						return True
			image.putpixel( (x,y), tuple(pixel) )
	return True

if len(sys.argv) < 2:
	print "syntax: msg_hide.py read <in_file>\n" +\
				  "msg_hide.py write <in_file> <out_file> \"<msg>\"" 
	exit(-1)
if sys.argv[1] == "read":
	image = Image.open( sys.argv[2] )
	image = image.convert("RGB")
	print parseMsg( image )
elif sys.argv[1] == "write":
	if len(sys.argv) != 5:
		print "syntax: msg_hide.py read <in_file>\n" +\
		"msg_hide.py write <in_file> <out_file> \"<msg>\"" 
	image = Image.open( sys.argv[2] )
	image = image.convert("RGB")
	writeMsg( image, sys.argv[4] + "\0" )
	print "Message << " + parseMsg( image ) + " >> was written."
	image.save( sys.argv[3] )
else:
	print "No such operation"
	print str(sys.argv)
