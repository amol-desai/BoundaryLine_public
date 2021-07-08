__author__ = "Amol Desai"
__copyright__ = "Copyright 2021, BoundaryLine"
__credits__ = ["Amol Desai"]
__license__ = "MPL 2.0"
__version__ = "0.1.0"
__maintainer__ = "Amol Desai"
__email__ = "amol.desai@gmail.com"
__status__ = "Development"

import pandas as pd
import re
from helpers import get_soup_from_url, get_id_from_url


base_url = "http://stats.espncricinfo.com"

types = {}
types['batting'] = "batting"
types['bowling'] = "bowling"
types['fielding'] = "fielding"
types['all_round'] = 'allround'
types['partnership'] = 'fow'
types['team'] = 'team'
types['umpires and refrees'] = 'official'
types['overall'] = 'aggregate'

classes = {}
classes['tests'] = '1'
classes['odi'] = '2'
classes['t20'] = '3'
classes['all'] = '11'
classes['w_tests'] = '8'
classes['w_odi'] = '9'
classes['w_t20'] = '10'
classes['y_tests'] = '20'
classes['y_odi'] = '21'
classes['y_t20'] = '22'

views = {}
views['overall'] = ''
views['innings'] = 'innings'
views['match'] = 'match'
views['result'] = 'results'
views['cum_avg'] = 'cumulative'
views['rev_cum_avg'] = 'reverse_cumulative'
views['series'] = 'series'
views['ground'] = 'ground'
views['host country'] = 'host'
views['partnership_summary'] = 'fow_summary'
views['partnership_list'] = 'fow_list'
views['dismissal_summary'] = 'dismissal_summary'
views['dismissal_list'] = 'dismissal_list'
views['batsman_summary'] = 'batsman_summary'
views['bowler_summary'] = 'bowler_summary'
views['fielder_summary'] = 'fielder_summary'
views['opposition'] = 'opposition'
views['year'] = 'year'
views['season'] = 'season'
views['extras_summary'] = 'extras'
views['extras_list'] = 'extras_innings'


def parse_cells_in_row(arr):
# Parsing helper
    toret=[]
    for i in arr:
        link = i.find('a')
        if (link != None):
            link = get_id_from_url(link['href'])
            value = i.get_text() + ',' + link
        else:
            value = i.get_text()
        if not (re.match('.*\n.*',value) or value == 'Go to page'):
            toret.append(value) 
    return toret


def get_url(qtype, qclass, qview, mode='sport', player_id=None):
# get appropriate statsguru query url
    if mode=='player':
        url_adder1 = '/ci/engine/player/' + str(player_id)
    else:
        url_adder1 = '/ci/engine/stats/index'

    url = base_url + url_adder1 + '.html?class=' + classes[qclass] + ';template=results;type=' + types[qtype] \
    + ';view='+views[qview]
    return url


def get_cols_from_soup(soup):
# parsing helper
    columns = soup.find('tr',class_='headlinks')
    columns = columns.findAll('th')
    columns = [str(c.get_text()) for c in columns if c!=None]
    return columns


def get_link_to_next_page(soup):
# parsing helper to go hit the next page
    return base_url+[x["href"] 
                    for x in soup.findAll('a',class_='PaginationLink') 
                    if x.find(text="Next ")
                   ][0]


def get_stats_page(url,mode):
# get data from one page.
# Available modes: 'player', 'sport'
    soup = get_soup_from_url(url)
    if soup == -1:
        return -1,-1,-1

    try:
        columns = get_cols_from_soup(soup)
    except AttributeError:
        print("Table Not Found")
        return -1,-1,-1

    if mode == 'player':
        data_soup = soup.findAll('table')[-4]
    else:
        data_soup = soup

    data = get_data_from_soup(data_soup)

    match_ids = [get_id_from_url(u['href']) for u in soup.find_all('a') if u.text == 'Match scorecard']
    if len(match_ids) == len(data):
        columns.append('match_id')
        for i, match_id in enumerate(match_ids):
            data[i].append(match_id)

    try:
        next_page = get_link_to_next_page(soup)
    except IndexError:
        next_page = False
    return columns,data,next_page


def get_stats_table(qtype=None,qclass=None,qview=None,url=None,mode='sport',player_id=None,limit=999999):
# This is the main method that gets a table resulting from a query
# qtype (ignored if url provided): Query Type. See types{} eg. 'batting'
# qclass (ignored if url provided): Query Class. See classes{} eg. 'tests'
# qview (ignored if url provided): Query View. See views{} eg. 'innings'
# url: Pass url directly instead of having the function build it. Overrides qtype, qclass, qview
# mode: 'player', 'sport'
# player_id (needed and used only when in 'player' mode): When in player mode, specifies the player id that the query should get data for
# limit: limit for number of records captured.
    if mode=='player' and not player_id:
    print("Please provide id for player")
    return

    if not url:
        url = get_url(qtype,qclass,qview,mode,player_id)

    #print(url)

    columns,data,next_page = get_stats_page(url,mode)
    if columns == data and data == next_page and data == -1:
        return
    #try to adjust columns to data
    if len(data[0]) == len(columns)+1:
        columns = columns + [qview]

    #print columns,data[0]
    try:
        df = pd.DataFrame(data,columns=columns)        
    except AssertionError:
          print("Column count ("+str(len(columns))+") does not match data ("+str(len(data[0]))+")")
          return

    while next_page and (df.shape[0] < limit or not limit):
        _,data_next,next_page = get_stats_page(next_page,mode)
        if data == next_page and data == -1:
            return
        df_next = pd.DataFrame(data_next,columns=columns)
        df = df.append(df_next)
        df = df.reset_index(drop=True)

    if limit:
        df = df[:limit]

    # get rid of empty columns    
    col_to_keep = []    
    for i, c in enumerate(df.columns):
        if (c != '') | (df.iloc[:,i].unique()[0] != ''):
            col_to_keep.append(i)

    df = df.iloc[:, col_to_keep]
    return df

