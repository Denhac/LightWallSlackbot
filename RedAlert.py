#!/usr/bin/env python
# Light each LED in sequence, and repeat.
import opc
import time

# Constants
numLEDs = 251
frequency = 0.3

#Connect to light controller  
client = opc.Client('10.0.100.6:80')

while True:
  # [ (red, greeen, blue) ]
  pixels = [ (255,0,0) ] * numLEDs #creates an array of all the pixels (the whole row) at once. 
  client.put_pixels(pixels)
  time.sleep(frequency)
  pixels = [ (0,0,0) ] * numLEDs #creates an array of all the pixels (the whole row) at once. 
  client.put_pixels(pixels)
  time.sleep(frequency)
 
