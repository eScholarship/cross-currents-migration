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
# - these remain: 
#     - pub_order
#     - disciplines
#     - keywords
#     - abstract
#     - acknowledgements
#     - pdf_url
#     - supplementalfile_url
#     - supplementafile_label
#     - supplementalfile_description
#
# TODO: figure out where to put any extra metadata
# TODO: figure out whether multi-author-name-handling is important, and what to do about it

import sys
import csv
import re
from nameparser import HumanName
from urlextract import URLExtract
import urllib

def pq():
  print('"', end='')

def pqc():
  print('",', end='')

def cleanhtml(raw_html):
  cleanr = re.compile('<.*?>')
  cleantext = re.sub(cleanr, '', raw_html)
  cleanr = re.compile('Keywords: ')
  cleantext = re.sub(cleanr, '', cleantext)
  return cleantext

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

  print(cdl_headers)

  for row in article_reader:

    #short-circuit this by skipping all photo essays, Readings - Info and Editors' Notes
    if row['Content type']=='Photo Essay':
      continue
    if row['Content type']=='Readings - Info':
      continue
    if row['Article Type']=='Editors&#039; Note':
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
    print('externalPub', end='')
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
    
    #author_email (input can have more than one, batch only wants one)
    # TODO - handle multiple e-mail addresses correctly
    pq()
    print(row['Author Email'], end='')
    pqc()
    
    #org_author (not used for Cross-Currents, ignore)
    pq()
    pqc()
    
    #doi
    # Hmm.... there are some DOIs present in the export, but they are not in a consistent location, skip for now.
    pq()
    pqc()

    #first_page
    pq()
    pages = row['Page Numbers']
    if len(pages.split('-')) > 1: 
      first_page = pages.split('-')[0]
    else:
      first_page = ''
    if len(pages.split('-')) > 2:
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
    print(row['Sort Order'], end='')
    pqc()
    
    #disciplines
    pq()
    print('Arts and Humanities', end='')
    pqc()
    
    #keywords
    # listed at the end of the abstract, a line that starts: <p><strong>Keywords</strong>:
    pq()
    abstract = row['Abstract']
    # commenting out keyword extraction because we don't actually use keywords, but, I will leave this here as proof that I figured out how to extract them from the abstract
    # if abstract.__len__() > 0:
    #   lines_in_abstract = abstract.splitlines()
    #   last_line = len(lines_in_abstract) -1 #lists are zero-based 
    #   raw_keywords = lines_in_abstract[last_line]
    #   keywords = cleanhtml(raw_keywords)
    #   print(keywords, end='')
    # else:
    print('', end='')
    pqc()
    
    #abstract
    pq()
    print(abstract, end='')
    pqc()
    
    #acknowledgements (leave blank, but might be able to extract from the article body)
    pq()
    pqc()
    
    #pdf_url, extract from the File column
    extractor = URLExtract()
    pdf_urls = extractor.find_urls(row['File'])
    if len(pdf_urls) >= 1: #sometimes the extractor finds more than one URL, we should just always use the first
      pdf_url = pdf_urls[0]
    else:
      pdf_url = 'ERROR, no PDF URL found, content-type: ' + row['Content type'] + '; Content ID: ' + row['Content ID'] + '; Article Type: ' + row['Article Type']
    pq()
    print(urllib.parse.unquote(pdf_url), end='')
    pqc()
    
    #supplementalfile_url
    pq()
    pqc()
    
    #supplementafile_label
    pq()
    pqc()
    
    #supplementalfile_description
    pq()
    pqc()

    print('') # let's wrap this up
