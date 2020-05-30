import sys
import csv

csv.field_size_limit(sys.maxsize)

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

print("\n\nnow to see if this works the way I think it ought to, here's some info\n - issue date for issue 31: " + IssueDate[31])
print(" - title for issue 31 is: " + IssueTitle[31])
print(" - ISSN for issue 31 is: " + IssueISSN[31] )
print('\n\n')
