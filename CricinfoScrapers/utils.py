__author__ = "Amol Desai"
__copyright__ = "Copyright 2021, BoundaryLine"
__credits__ = ["Amol Desai"]
__license__ = "MPL 2.0"
__version__ = "0.1.0"
__maintainer__ = "Amol Desai"
__email__ = "amol.desai@gmail.com"
__status__ = "Development"

from urllib.request import urlopen
from bs4 import BeautifulSoup
from helpers import get_soup_from_url
import re

def get_all_matchids_for_season(season='2018/19'):
    #season = "2018"
    #season = "2018/19"
    season = season.replace('/', '%2F')
    url = "http://www.espncricinfo.com/ci/engine/series/index.html?season={};view=season".format(season)
    soup = get_soup_from_url(url)
    d={}
    for section in soup.find_all('div', class_='match-section-head'):
        series_in_section = [series['data-series-id']
                             for series in section.find_next(
                                 'section',
                                  class_='series-summary-wrap'
                             ).find_all(
                                 'section',
                                  class_="series-summary-block collapsed"
                             )
                            ]
        series_in_section = [
            get_soup_from_url('http://www.espncricinfo.com/ci/engine/match/index/series.html?series={}'.format(s)) 
            for s in series_in_section
        ]
        matches_in_section = [
            re.findall('\/([0-9]+)\/', 
                      m.find('a')['href'])[1] 
            for ss in series_in_section 
            for m in ss.find_all(class_='match-no')
        ]
        d[section.text] = matches_in_section
    return d


def get_available_team_ids_statsguru():
# This is restricted to teams available on statsguru. There is an additional team page that can be tapped into as well for all team ids
# This can also simply be done from the match data once we are able to programatically grab and store it
    return {i.text.strip(): re.search('id=([0-9]+)', i['href']).group(1)
            for i in BeautifulSoup(
                urlopen(
                    'http://stats.espncricinfo.com/ci/engine/records/index.html').read()
         ).find_all(
             'a', class_='RecordLinks') if re.search('team', i['href'])}
  
    
def get_player_id(player_last_name):
# Player id based on player's last name. Shows all players with given last name
    url='http://search.espncricinfo.com/ci/content/site/search.html?search='+player_last_name
    html = urlopen(url).read()
    soup = BeautifulSoup(html,"lxml")
    players = soup.findAll(class_='player-list')[0].findAll('li')
    dict_to_ret={}
    for player in players:
        player_found = re.search(player_last_name,
                                 player.find(class_="alphabetical-name").text,flags=re.IGNORECASE)
        if player_found:
            player_id = re.search('([0-9]*).html',player.a["href"]).group(1)
            player_name = player.find(class_="alphabetical-name").text + ', ' + \
                player.find(class_='country').text
            dict_to_ret[player_name]=int(player_id)
    return dict_to_ret
