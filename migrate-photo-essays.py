#!/usr/bin/env python3

# MIGRATE-PHOTO-ESSAYS.PY
# - A quick little Python3 script to convert Cross-Currents eJournal metadata into 
#   eScholarship batch load format
# - only handles photo essays

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

import sys
import csv
import re
from nameparser import HumanName
from urlextract import URLExtract
import urllib
import html

### BEGIN METHODS

def pq():
  # print('"', end='') # suitable for CSV, we're going for TSV, so skip
  print ('', end='')

def pqc():
  # print('",', end='') # suitable for CSV, we're going for TSV, use a tab
  print ('\t', end='')

def cleanhtml(raw_html):
  cleanr = re.compile('<.*?>')
  cleantext = re.sub(cleanr, '', raw_html)
  return cleantext

def stripnewlines(raw_text):
  cleanr = re.compile('\n')
  cleantext = re.sub(cleanr, ' ', raw_text)
  return cleantext

def striptabs(raw_text):
  cleanr = re.compile('\t')
  cleantext = re.sub(cleanr, '', raw_text)
  return cleantext

def remove_nonname_text_from_name(raw_name):
  cleanr = re.compile('Guest editor, ')
  cleantext = re.sub(cleanr, '', raw_name)
  cleanr = re.compile('Guest editor ')
  cleantext = re.sub(cleanr, '', cleantext)
  cleanr = re.compile('Guest co-editor ')
  cleantext = re.sub(cleanr, '', cleantext)
  cleanr = re.compile(' with an addendum by guest co-editor ')
  cleantext = re.sub(cleanr, '', cleantext)
  return cleantext

def print_author_info(author_raw_text, all_emails_list, primary_author=True):

  if not primary_author:
    print(10*'\t', end='') # author names are 10 fields in, non-primary authors are printed after the first row, so, indent 10 fields

  author_and_affiliation_list = author_raw_text.split(',')
  author = author_and_affiliation_list[0]
  number_of_authors = len(author_and_affiliation_list)
  if number_of_authors > 1:
    # affiliation = author_and_affiliation_list[1]
    affiliation = ', '.join(author_and_affiliation_list[1:number_of_authors])
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

  #author_email
  pq()
  author_email_list = [x for x in all_emails_list if re.search(name.last.lower(), x)]
  if len(author_email_list) > 0:
    # well, this is easy, we have a match of last name and an e-mail address, print the first one
    print(author_email_list[0], end='')
  else:
    # huh, weird, print 'em all, let a human figure it out
    print(';'.join(all_emails_list), end='')
  
  # if this is the primary author, more data needs to appear after this, so print a pqc
  if primary_author:
    pqc()

### END METHODS

### BEGIN MAIN LOOP

csv.field_size_limit(sys.maxsize)

cdl_headers="unit_id\teschol_id\tjournal\tvolume\tissue\tpub_date\ttitle\tpub_status\tpeer_review\tsection_header\tauthor_firstname\tauthor_middlename\tauthor_lastname\tauthor_suffix\tauthor_institution\tauthor_email\torg_author\tdoi\tfirst_page\tlast_page\tissn\tpub_order\tdisciplines\tkeywords\tabstract\tcover_image\tpdf_url\tsupplementalfile_url\tsupplementalfile_label\tsupplementalfile_description"

######### step one, gather issue data into a set of dictionaries

# instantiate some Dictionaries for later use
IssueDate = dict()
IssueISSN = dict()
IssueTitle = dict()
IssueNumber = dict()
photoessay_element = dict()
photo_metadata = dict()
photoessay_article = dict()

# read ALL photoessay rows from the articles CSV into a dictionary
with open('cross-currents-articles-1591737565.csv', 'r', 1, 'utf-8-sig') as csvfile:
  article_reader = csv.DictReader(csvfile, delimiter=",", quotechar='"')
  for row in article_reader:
    key = row['Content ID']
    if key in photoessay_article:
      # implement duplicate handling here, if necessary, but... for now, just skip duplicates
      pass
    # store this article row in the photoessay_article dictionary
    else:
      if row['Content type'] == 'Photo Essay':
        photoessay_article[key] = row
        photoessay_article[key]['Photo Essay ID'] = row['Content ID']
      else:
        pass

# read ALL non-photo rows into a dictionary, so we can refer back to each element as we need
with open('cross-currents-photoessays-1591737571.csv', 'r', 1, 'utf-8-sig') as csvfile:
  photoessay_reader = csv.DictReader(csvfile, delimiter=",", quotechar='"')
  for row in photoessay_reader:
    key = row['Photo Essay ID']
    if key in photoessay_element:
      # implement duplicate handling here, if necessary, but... for now, just skip duplicates
      pass
    if row['Content type']=='Photo Essay - Photo':
      pass #and skip photo rows
    # store this bio/statement row in the photoessay_element dictionary
    else:
      photoessay_element[key] = row

# go through the photoessays CSV again, this time gathering up the photos, store them in a Dictionary, using a list to hold all photo rows
with open('cross-currents-photoessays-1591737571.csv', 'r', 1, 'utf-8-sig') as csvfile:
  photo_reader =  csv.DictReader(csvfile, delimiter=",", quotechar='"')
  for row in photo_reader:
    key = row['Photo Essay ID']
    if row['Content type']=='Photo Essay - Photo':
      if key in photo_metadata:
        # append this photo row to the list
        list_of_photos = photo_metadata[key]
      else:
        # store this photo row in the list in the photo_metadata dictionary
        list_of_photos = []
      list_of_photos.append(row)
      photo_metadata[key] = list_of_photos
    else:
      pass

# save some Issue data in dictionaries for later lookup
with open('cross-currents-export-issues-1591737562.csv', 'r', 1, 'utf-8-sig') as csvfile:
  issue_reader = csv.DictReader(csvfile, delimiter=",", quotechar='"')
  for row in issue_reader:
    # print("setting Issue Date for Issue "+ row['Issue Number'] + " to " + row['Issue Date'])
    IssueDate[int(row['Issue Number'])]=row['Issue Date']
    IssueTitle[int(row['Issue Number'])]=row['Title']
    IssueISSN[int(row['Issue Number'])]=row['ISSN']


######## step two, process the photoessay data

print(cdl_headers)

# loop through the photoessay_element dictionary, and the photo_metadata dictionary

for photoessay in photoessay_article.values():

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

    #issue
    pq()
    try:
      i = int(photoessay['Issue Number']) # save this for later lookups
    except ValueError:
      # how in the world did we end up with a missing issue number? fix this by hand and glower about it for weeks
      i=0 # of course, zero will throw key errors below... so... yeah, you'll have to fix it by hand

    print(i, end='')
    pqc()
    
    
    #pub_date (look this up based on issue number)
    pq()
    print(IssueDate[i], end='')
    pqc()

    #title
    pq()
    title = striptabs(html.unescape(photoessay['Title'])).strip()
    print(title, end='')
    pqc()
    
    #pub_status (always internalPub)
    pq()
    print('internalPub', end='')
    pqc()
    
    #peer_review
    pq()
    print('yes', end='') # always yes
    pqc()
    
    #section_header
    pq()
      # skip for now
    pqc()
    
    # start name handling
    author_and_affiliation = remove_nonname_text_from_name(html.unescape(photoessay['Author & Affiliation']))

    if author_and_affiliation.__len__() == 0:
      print ('ERROR: null author_and_affiliation', end='')
    else:
    # NOTE: we can have more than one author and affiliation, they are split by semicolons
      all_authors_list = author_and_affiliation.split(';')
      all_emails_list = photoessay['Author Email'].split(';')
      number_of_authors = len(all_authors_list)

      # first handle the primary author, save the remaining authors for handling after this photoessay is done
      print_author_info(all_authors_list.pop(0), all_emails_list, primary_author=True)

    #org_author (not used for Cross-Currents, ignore)
    pq()
    pqc()
    
    #doi: unable to parse from given data, most DOIs contained are for citations, skip
    pq()
    pqc()

    #first_page
    #124-151
    pq()
    pages = photoessay['Page Numbers']
    if len(pages.split('-')) > 1: 
      first_page = pages.split('-')[0]
    else:
      first_page = ''
    if len(pages.split('-')) > 1:
      last_page = pages.split('-')[1]
    else:
      last_page = ''
    print(first_page, end='')
    if first_page.__len__() > 0 and last_page.__len__() == 0:
      last_page = first_page
    pqc()
    
    #last_page
    pq()
    print(last_page, end='')
    pqc()

    #issn
    pq()
    print(IssueISSN[i], end='')
    pqc()
    
    #pub_order
    pq()
    try:
      pub_order = int(photoessay['Sort Order'])
    except ValueError:
      pub_order = 0
    if pub_order > 0:
      print(photoessay['Sort Order'], end='')
    else:
      print('0', end='')
    pqc()
    
    #disciplines
    pq()
    print('Arts and Humanities', end='')
    pqc()
    
    #keywords
    pq()
    pqc()
    
    #abstract
    pq()
    pqc()
    
    #cover_image (may not work, but might as well try)
    pq()
    cover_image = 'https://cross-currents.berkeley.edu'+photoessay['Image']
    print(cover_image, end='')
    pqc()
    
    #pdf_url, extract from the File column
    extractor = URLExtract()
    pdf_urls = extractor.find_urls(photoessay['File'])
    if len(pdf_urls) >= 1: #sometimes the extractor finds more than one URL, we should just always use the first
      pdf_url = pdf_urls[0]
    else:
      pdf_url = 'ERROR, no PDF URL found, content-type: ' + photoessay['Content type'] + '; Content ID: ' + photoessay['Content ID'] + '; Article Type: ' + photoessay['Article Type']
    pq()
    print(urllib.parse.unquote(pdf_url), end='')
    pqc()

    # Add 3 blank cells here at the end, because supplemental files follow on additional lines
    print(3*'\t', end='')    

    print('') # let's wrap up this photoessay

    # print out the bio and statement here as supplemental files, construct a PDF url for each, using data in the photoessay_element dictionary
    for element in photoessay_element.values():
      if element['Photo Essay ID']==photoessay['Photo Essay ID']:
        print(27*'\t', end='') # skip 27 fields for each element row, because that's how many fields precede the supplemental file fields

        #supplementalfile_url, extract from the File column
        extractor = URLExtract()
        pdf_urls = extractor.find_urls(element['File'])
        if len(pdf_urls) >= 1: #sometimes the extractor finds more than one URL, we should just always use the first
          pdf_url = pdf_urls[0]
        else:
          pdf_url = 'ERROR, no PDF URL found, content-type: ' + element['Content type'] + '; Photo Essay ID: ' + element['Photo Essay ID'] 
        pq()
        print(urllib.parse.unquote(pdf_url), end='')
        pqc()

        #supplementalfile_label
        pq()
        print(element['Content type'], end='')
        pqc()

        #supplementalfile_description -- if Description isn't sufficient, try Article body
        pq()
        print(element['Description'], end='')
        pqc()

        print('') # let's wrap up this element


    # finish up with the indivitual photos as supplemental files here
    for photos in photo_metadata.values():
      # photos is a list of dictionaries, we need to iterate through that list
      for photo in photos:
        if photo['Photo Essay ID']==photoessay['Photo Essay ID']:

          print(27*'\t', end='') # skip 27 fields for each photo row, because that's how many fields precede the supplemental file fields

          #supplementalfile_url
          pq()
          photo_image = 'https://cross-currents.berkeley.edu'+photo['Photo']
          print(photo_image, end='')
          pqc()
          
          #supplementafile_label
          pq()
          print('Photograph', end='')
          pqc()
          
          #supplementalfile_description
          pq()
          print(striptabs(cleanhtml(stripnewlines(photo['Description']))).strip(), end='')
          pq()

          print('') # let's wrap up this photo

# END MAIN LOOP