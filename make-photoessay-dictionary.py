#!/usr/bin/env python3

import sys
import csv
import re
from nameparser import HumanName
from urlextract import URLExtract
import urllib
import html


#read all the photoessay metadata from any rows that are not photos
photoessay_metadata = {}
with open('cross-currents-photoessays-1591737571.csv', 'r', 1, 'utf-8-sig') as csvfile:
  photoessay_reader = csv.DictReader(csvfile, delimiter=",", quotechar='"')
  for row in photoessay_reader:
    key = row.pop('Photo Essay ID')
    if key in photoessay_metadata:
      # implement duplicate handling here
      pass
    if row['Content type']=='Photo Essay - Photo':
      pass
    # store the row in the photoessay_metadata dictionary
    photoessay_metadata[key] = row

print("DEBUG: number of rows in photoessay_metadata=" + str(len(photoessay_metadata)) )
breakpoint() # now let's play!

# here's how to reference stuff in the photoessay_metadata list:
# print(photoessay_metadata[168]."Content ID") #233