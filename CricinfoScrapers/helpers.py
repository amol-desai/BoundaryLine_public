__author__ = "Amol Desai"
__copyright__ = "Copyright 2021, BoundaryLine"
__credits__ = ["Amol Desai"]
__license__ = "MPL 2.0"
__version__ = "0.1.0"
__maintainer__ = "Amol Desai"
__email__ = "amol.desai@gmail.com"
__status__ = "Development"

from urllib.request import urlopen
from urllib.error import HTTPError
from bs4 import BeautifulSoup
import pandas as pd
import re
import json
import numpy as np
from time import sleep
from datetime import datetime

def get_soup_from_url(url):
# Helper to get response soup from url
    sleep(1)
    try:
        html = urlopen(url).read()
    except HTTPError:
        print("Link Cannot be Reached")
        return -1   
    #soup = BeautifulSoup(html,"lxml")
    soup = BeautifulSoup(html,"html.parser")
    return soup

def get_id_from_url(url):
# url usually ends with an id (match url has match_id, player url has player_id etc.)
    id = re.search('([0-9]+).html$', url)
    if id != None:
        return id[1]
    else:
        return 'NA'
      
def get_match_url_from_match_id(match_id):
# This is specific to match url. This might be redundant with get_id_from_url, but this isn't tested
# and needs replacement where used. So consider this legacy code until tested
    url = "http://stats.espncricinfo.com/ci/engine/match/{match_id}.html".format(match_id=str(match_id))
    return url

def get_series_id_from_match_page(url):
    soup = get_soup_from_url(url)
    series_link = [i.find('a') 
                 for i in soup.find_all(class_='match-details-table') if 'Series' in i.text
                ][0]['href']
    return re.search('([0-9]+)', series_link)[1]
