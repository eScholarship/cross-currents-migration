#!/usr/bin/env python3

# MIGRATE.PY
# - A quick little Python3 script to convert Cross-Currents eJournal metadata into 
#   eScholarship batch load format
# - Currently skips photo essays, intentionally, we'll work on those next

# HEADERS IN THE ARTICLES DATA -> CDL HEADER
# Content ID
# Issue ID
# Issue Number
# Title
# Content type
# Article Type
# Subsection
# Author & Affiliation
# Author Email
# Authors, Citation Format
# Image
# Book Covers
# Page Numbers
# Recommended Citation
# Article Region
# File
# Sort Order
# Books
# Abstract
# Article Preview
# Article Body
# Essay Title
# Essay Attribution Label
# Artist Name
# Essay Author
# Essay
# Alternate Essay
# Alternate ToC Image (Reading)
# Editor Display (Reading)
# Link

# TODO: finish up getting the metadata in the right slots for a batch
# TODO: figure out where to put any extra metadata
# TODO: figure out whether multi-author-name-handling is important, and what to do about it

import sys
import csv
from nameparser import HumanName

def pq():
  print('"', end='')

def pqc():
  print('",', end='')


csv.field_size_limit(sys.maxsize)

cdl_headers='unit_id,eschol_id,journal,volume,issue,pub_date,title,pub_status,peer_review,section_header,author_firstname,author_middlename,author_lastname,author_suffix,author_institution,author_email,org_author,doi,first_page,last_page,issn,pub_order,disciplines,keywords,abstract,acknowledgements,pdf_url,supplementalfile_url,supplementafile_label,supplementalfile_description'

######### step one, gather issue data into a set of dictionaries

# instantiate some Dictionaries for later use
IssueDate = dict()
IssueISSN = dict()
IssueTitle = dict()

with open('cross-currents-export-issues-1586192032.csv', 'r', 1, 'utf-8-sig') as csvfile:
  issue_reader = csv.DictReader(csvfile, delimiter=",", quotechar='"')
  for row in issue_reader:
    # print("setting Issue Date for Issue "+ row['Issue Number'] + " to " + row['Issue Date'])
    IssueDate[int(row['Issue Number'])]=row['Issue Date']
    IssueTitle[int(row['Issue Number'])]=row['Title']
    IssueISSN[int(row['Issue Number'])]=row['ISSN']


######## step two, process the article data

with open('cross-currents-articles-1586192134.csv', 'r', 1, 'utf-8-sig') as csvfile:
  article_reader = csv.DictReader(csvfile, delimiter=",", quotechar='"')

  print(cdl_headers+'\n')

  for row in article_reader:

    #short-circuit this by skipping all photo essays
    if row['Content type']=='Photo Essay':
      continue

    #unit_id (always 'crossscurrents')
    pq()
    print('crosscurrents', end='')
    pqc()

    #eschol_id (always 'new')
    pq()
    print('new', end='')
    pqc()

    #journal (always 'Cross-Currents: East Asian History and Culture Review')
    pq()
    print('Cross-Currents: East Asian History and Culture Review', end='')
    pqc()

    #volume (always 1)
    pq()
    print('1', end='')
    pqc()

    #issue (convert to integer and remember)
    pq()
    print(row['Issue Number'], end='')
    pqc()
    i = int(row['Issue Number']) # save this for later lookups
    
    #pub_date (look this up based on issue number)
    pq()
    print(IssueDate[i], end='')
    pqc()

    #title
    pq()
    print(row['Title'], end='')
    pqc()
    
    #pub_status
    pq()
    print('published', end='')
    pqc()
    
    #peer_review
    pq()
    print('no', end='')
    pqc()
    
    #section_header
    pq()
    print(row['Subsection'], end='')
    pqc()
    
    # And now we begin our author name parsing operation

    author_and_affiliation = row['Author & Affiliation']

    # pq()
    # print ("author-and-affiliation-goes-here --->", end='')
    # print(author_and_affiliation)
    # pqc()

    if author_and_affiliation.__len__() == 0:
      print ('ERROR: null author_and_affiliation', end='')
    else:
    # NOTE: we can have more than one author and affiliation, they are split by semicolons
    # for now, let's just grab the first set
      primary_author_and_affiliation = author_and_affiliation.split(';')[0]

      author_and_affiliation_list = primary_author_and_affiliation.split(',')
      author = author_and_affiliation_list[0]

      if len(author_and_affiliation_list) > 1:
        affiliation = author_and_affiliation_list[1]
      else:
        affiliation = ''

      #crank up the human name machine
      name = HumanName(author.strip())

      #author_firstname
      pq()
      print (name.first, end='')
      pqc()
      
      #author_middlename
      pq()
      print (name.middle, end='')
      pqc()
      
      #author_lastname
      pq()
      print (name.last, end='')
      pqc()
      
      #author_suffix
      pq()
      print (name.suffix, end='')
      pqc()
      
      #author_institution
      pq()
      print(affiliation, end='')
      pqc()
    
    #author_email (can have more than one)
    pq()
    print(row['Author Email'], end='')
    pqc()
    
    #org_author
    
    #doi
    
    #first_page
    
    #last_page
    
    #issn
    pq()
    print(IssueISSN[i], end='')
    pqc()
    
    #pub_order
    
    #disciplines
    
    #keywords
    
    #abstract
    
    #acknowledgements
    
    #pdf_url
    
    #supplementalfile_url
    
    #supplementafile_label
    
    #supplementalfile_description

    print('') # let's wrap this up
