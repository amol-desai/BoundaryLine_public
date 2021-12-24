#retrieve list of all ICC fixtures
import requests
from requests.structures import CaseInsensitiveDict
import shutil
import json

headers = CaseInsensitiveDict()
headers["Accept"] = "application/json"

#retrieve first page, and find number of pages
page = 0 #first page to download
url = 'https://cricketapi-icc.pulselive.com/fixtures?pageSize=300&page=%s' % page  
print(url)
fixturesJSON = requests.get(url, headers=headers)

with open('ICC-fixtures-%s' % page, 'w') as out_file:
    out_file.write(fixturesJSON.text)

numPages = fixturesJSON.json()['pageInfo']['numPages']

#retrieve rest of pages
for page in range(page+1,numPages+1):
    url = 'https://cricketapi-icc.pulselive.com/fixtures?pageSize=300&page=%s' % page
    print(url)
    fixturesJSON = requests.get(url, headers=headers)
    
    with open('ICC-fixtures-%s' % page, 'w') as out_file:
        out_file.write(fixturesJSON.text)
