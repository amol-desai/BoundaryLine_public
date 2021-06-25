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
import numpy as np
import json
import re

def get_url_hawkeye(match_id):  
    url = f'https://cricketapi.platform.bcci.tv//fixtures/{match_id}/uds/stats'
    return url

def get_url_metadata(match_id):
    url = f'https://cricketapi.platform.bcci.tv//fixtures/{match_id}/scoring'
    return url

def get_soup_from_url(url):
    try:
        html = urlopen(url).read()
    except HTTPError:
        print("Link Cannot be Reached", url)
        return -1
        
    #soup = BeautifulSoup(html,"lxml")
    soup = BeautifulSoup(html,"html.parser")
    return str(soup)
  
def get_tracking_df_from_matchid(match_id):
  try:
    df = pd.DataFrame(
        [[k]+v.split(',') for i in json.loads(get_soup_from_url(get_url_hawkeye(match_id)))['data'] 
         for k,v in i.items()],
        columns = ['over','ball_num','batter','non-striker',
                   'bowler','speed','catcher','dismissal_desc',
                   'total_extras','runs','bowler_extras','extra_type',
                  'otw','length','line','line_at_stumps',
                  'height_at_stumps','shot_dist0','shot_dist1','blank2',
                   'blank3','blank4']
    )
    df['match_id'] = str(match_id)
    if ((df.shape[0] == 0) | 
       ((df.speed.nunique() == 1) & 
        (df.length.nunique() == 1) & 
        (df.line.nunique() == 1) & 
        (df.line_at_stumps.nunique() == 1) & 
        (df.height_at_stumps.nunique() == 1))) :
        return
    else:
      df['match_inn'] = df.over.apply(lambda x: x[0])
      df['over_ball'] = pd.to_numeric(df.over.apply(lambda x: x[-1]))
      df['over_num'] = pd.to_numeric(df.over.apply(lambda x: x[2]), errors='coerce')
      df.drop('over', axis=1, inplace=True)

      df['speed'] = pd.to_numeric(df['speed'], errors='coerce')*3.6
      df.loc[df.speed < 0, 'speed'] = np.nan

      df['length'] = pd.to_numeric(df['length'], errors='coerce')
      df['line'] = pd.to_numeric(df['line'], errors='coerce')
      df['line_at_stumps'] = pd.to_numeric(df['line_at_stumps'], errors='coerce')
      df['height_at_stumps'] = pd.to_numeric(df['height_at_stumps'], errors='coerce')
      df['deviation'] = df.line_at_stumps - df.line
      return df
  except:
    print(f"couldn't retrieve data for match {match_id}. Please check {get_url_hawkeye(match_id)} to debug")
    return
  
def get_metadata_df_from_matchid(match_id):
  m = json.loads(get_soup_from_url(get_url_metadata(match_id)))
  this_match = pd.DataFrame([{k: v for k,v in m['matchInfo'].items() if k in [
    'matchDate', 'matchEndDate','isLimitedOvers', 'description', 'matchType', 'tournamentLabel']}])
  this_match['match_id'] = match_id
  try:
      this_match['toss_elected'] = m['matchInfo']['additionalInfo']['toss.elected']
  except:
      this_match['toss_elected'] = ''
  this_match['venue_id'] = m['matchInfo']['venue']['id']
  try:
      this_match['team1_wk'] = m['matchInfo']['teams'][0]['wicketKeeper']['id']
      this_match['team2_wk'] = m['matchInfo']['teams'][1]['wicketKeeper']['id']
  except:
      this_match['team1_wk'] = ''
      this_match['team2_wk'] = ''
  this_match['team1'] = m['matchInfo']['teams'][0]['team']['fullName']
  this_match['team2'] = m['matchInfo']['teams'][1]['team']['fullName']
  match_df = this_match
  venue_df = pd.DataFrame([m['matchInfo']['venue']])])
  player_df = pd.concat([pd.DataFrame(m['matchInfo']['teams'][0]['players']),
                         pd.DataFrame(m['matchInfo']['teams'][1]['players'])
                        ]).drop_duplicates()
  
  venue_df.drop('coordinates',axis=1, inplace=True)
  player_df['batter_hand'] = player_df.rightHandedBat.apply(lambda x: 'R' if x else 'L')
  player_df['bowler_hand'] = player_df.rightArmedBowl.apply(lambda x: 'R' if x else 'L')
  match_df.matchType = match_df.apply(lambda x: 'W_' + x.matchType if 
               re.search('women', x.tournamentLabel.lower()) else x.matchType,
              axis=1)
  match_df['toss_winner'] = match_df.toss_elected.apply(lambda x: str(x).strip().lower().split(',')[0])
  match_df['toss_decision'] = match_df.toss_elected.apply(lambda x: str(x).lower().strip('.').split(' ')[-1])
  match_df['toss_decision'] = match_df.toss_decision.apply(lambda x: 'field' if str(x)=='bowl' else str(x))
  match_df['toss_decision'] = match_df.toss_decision.apply(lambda x: x if str(x) in ['field','bat'] else '')
  match_df.drop('toss_elected', axis=1, inplace=True)
  return {'match_metadata': match_df,
          'player_metadata': player_df,
          'venue_metadata': venue_df}


  
