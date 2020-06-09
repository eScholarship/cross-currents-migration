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
#     - supplementalfile_url
#     - supplementafile_label
#     - supplementalfile_description
#
# TODO: figure out where to put any extra metadata
# DOING: figure out whether multi-author-name-handling is important, and what to do about it

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

cdl_headers="unit_id\teschol_id\tjournal\tvolume\tissue\tpub_date\ttitle\tpub_status\tpeer_review\tsection_header\tauthor_firstname\tauthor_middlename\tauthor_lastname\tauthor_suffix\tauthor_institution\tauthor_email\torg_author\tdoi\tfirst_page\tlast_page\tissn\tpub_order\tdisciplines\tkeywords\tabstract\tacknowledgements\tpdf_url\tsupplementalfile_url\tsupplementalfile_label\tsupplementalfile_description"

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

    #short-circuit this by skipping all photo essays, Readings - Info and Editors' Notes, Book Reviews
    if row['Content type']=='Photo Essay':
      continue
    if row['Content type']=='Readings - Info':
      continue
    if row['Article Type']=='Editors&#039; Note':
      continue
    if row['Content type']=='Book Review':
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
    title = striptabs(html.unescape(row['Title'])).strip()
    print(title, end='')
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
    
    # start name handling
    author_and_affiliation = remove_nonname_text_from_name(html.unescape(row['Author & Affiliation']))

    if author_and_affiliation.__len__() == 0:
      print ('ERROR: null author_and_affiliation', end='')
    else:
    # NOTE: we can have more than one author and affiliation, they are split by semicolons
      all_authors_list = author_and_affiliation.split(';')
      all_emails_list = row['Author Email'].split(';')
      number_of_authors = len(all_authors_list)

      # first handle the primary author, save the remaining authors for handling after this row is done
      print_author_info(all_authors_list.pop(0), all_emails_list, primary_author=True)
    
    # #author_email (input can have more than one, batch only wants one)
    # # TODO - handle multiple e-mail addresses correctly
    # pq()
    # print(row['Author Email'], end='')
    # pqc()
    
    #org_author (not used for Cross-Currents, ignore)
    pq()
    pqc()
    
    #doi
    # Hmm.... there are some DOIs present in the export, but they are not in a consistent location, skip for now.
    # one possibility is to concat all the possible fields that might have a DOI, then extract from that concatenation
    # TODO: try to get a DOI from our data
    pq()
    pqc()

    #first_page
    #124-151
    pq()
    pages = row['Page Numbers']
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
    pub_order = int(row['Sort Order'])
    if pub_order > 0:
      print(row['Sort Order'], end='')
    else:
      print('0', end='')
    pqc()
    
    #disciplines
    pq()
    print('Arts and Humanities', end='')
    pqc()
    
    #keywords
    # listed at the end of the abstract, a line that starts: <p><strong>Keywords</strong>:
    pq()
    abstract = striptabs(cleanhtml(stripnewlines(row['Abstract']))).strip()
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
    pq()

    print('') # let's wrap up this row

    # Handle additional authors here
    
    if number_of_authors > 1:      
      for an_author_and_affiliation in all_authors_list:
        i = all_authors_list.index(an_author_and_affiliation)
        print_author_info(an_author_and_affiliation, all_emails_list, primary_author=False)
        print('') # let's wrap up this row

# END MAIN LOOP