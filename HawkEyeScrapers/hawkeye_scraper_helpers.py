__author__ = "Amol Desai"
__copyright__ = "Copyright 2021, BoundaryLine"
__credits__ = ["Amol Desai", "James Delaney"]
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
import base64
import struct

def get_candidate_base_urls():
    return [
       'https://cricketapi-icc.pulselive.com',
       'https://cricketapi.platform.bcci.tv',
       'https://cricketapi.platform.iplt20.com'
    ]


def get_candidate_urls_hawkeye(match_id):
    url_suffix = f'//fixtures/{match_id}/uds/stats'
    return [base_url + url_suffix for base_url in get_candidate_base_urls()]

def get_candidate_urls_hawkeye_trajectories(match_id):
    url_suffix = f'//fixtures/{match_id}/uds/traj'
    return [base_url + url_suffix for base_url in get_candidate_base_urls()]

def get_candidate_urls_metadata(match_id):
    url_suffix = f'//fixtures/{match_id}/scoring'
    return [base_url + url_suffix for base_url in get_candidate_base_urls()]


def get_available_match_id_list(starting_page_id=None):
    candidate_base_urls = get_candidate_base_urls()
    url_suffix = f'/fixtures?pageSize=300'

    soup = try_urls([base_url + url_suffix for base_url in candidate_base_urls])

    if soup == -1:
        return soup
    else:
        soup = json.loads(soup)
        num_pages = soup['pageInfo']['numPages']
        page_size = soup['pageInfo']['pageSize']
        total_matches = soup['pageInfo']['numEntries']

    def get_matchids_from_page(page_soup):
        match_id_list = []
        page_content = page_soup['content']
        for i in page_content:
            match_id_list.append(i['scheduleEntry']['matchId']['id'])
        return match_id_list

    def get_match_ids_for_page_list(starting_page_id):
        match_id_list = []
        for i in range(starting_page_id, num_pages):
            if i == num_pages - 1:
                us = f'/fixtures?matchStates=C&pageSize=300'
            else:
                us = url_suffix
            soup = try_urls([base_url + us + f'&page={i}' for base_url in candidate_base_urls])
            if soup not in [-1, -2]:
                match_id_list = match_id_list + get_matchids_from_page(json.loads(soup))
            else:
                pass
        return match_id_list, i

    if starting_page_id is not None:
        match_id_list, p = get_match_ids_for_page_list(starting_page_id)
    else:
        match_id_list, p = get_match_ids_for_page_list(0)

    return match_id_list, p


def try_urls(urls):
    for url in urls:
        try:
            soup = get_soup_from_url(url)
            if soup not in [-1, -2]:
                return soup
            else:
                pass
        except:
            pass
    if soup in [-1, -2]:
        print("Tried all URLs in vain")
        return -1


def get_soup_from_url(url):
    try:
        html = urlopen(url).read()
    except HTTPError:
        print("Link Cannot be Reached", url)
        return -1

    # soup = BeautifulSoup(html,"lxml")
    soup = BeautifulSoup(html, "html.parser")
    # check if soup is empty
    if str(soup):
        return str(soup)
    else:
        print("url is empty, no data available")
        return -2


def get_tracking_df_from_matchid(match_id):
    try:
        df = pd.DataFrame(
            [[k]+v.split(',') for i in json.loads(try_urls(get_candidate_urls_hawkeye(match_id)))['data']
             for k, v in i.items()],
            columns=['over', 'ball_num', 'batter', 'non-striker',
                     'bowler', 'speed', 'catcher', 'dismissal_desc',
                     'total_extras', 'runs', 'bowler_extras', 'extra_type',
                     'is_batter_rhb', 'length', 'line', 'line_at_stumps',
                     'height_at_stumps', 'shot_dist0', 'shot_dist1', 'blank2',
                     'blank3', 'blank4']
        )
        df['match_id'] = str(match_id)
        if ((df.shape[0] == 0) |
           ((df.speed.nunique() == 1) &
            (df.length.nunique() == 1) &
            (df.line.nunique() == 1) &
            (df.line_at_stumps.nunique() == 1) &
                (df.height_at_stumps.nunique() == 1))):
            print(f'no data to fetch for {match_id}')
            return
        else:
            df['over'] = df.over.apply(lambda x: str(x).split('.'))
            df['match_inn'] = df.over.apply(lambda x: x[0])
            df['over_ball'] = pd.to_numeric(
                df.over.apply(lambda x: x[2]), errors='coerce')
            df['over_num'] = pd.to_numeric(
                df.over.apply(lambda x: x[1]), errors='coerce')
            df.drop('over', axis=1, inplace=True)

            df['speed'] = pd.to_numeric(df['speed'], errors='coerce')*3.6
            df.loc[df.speed < 0, 'speed'] = np.nan

            df['length'] = pd.to_numeric(df['length'], errors='coerce')
            df['line'] = pd.to_numeric(df['line'], errors='coerce')
            df['line_at_stumps'] = pd.to_numeric(
                df['line_at_stumps'], errors='coerce')
            df['height_at_stumps'] = pd.to_numeric(
                df['height_at_stumps'], errors='coerce')
            df['deviation'] = df.line_at_stumps - df.line
            df['shot_dist0'] = (pd.to_numeric(df['shot_dist1'], errors='coerce') * 4.05) - 130.33  # based on vendor.js
            df['shot_dist1'] = (pd.to_numeric(df['shot_dist0'], errors='coerce') * 3.45) - 163.64  # based on vendor.js
            return df
    except:
        print(
            f"couldn't retrieve data for match {match_id}. Please check {get_candidate_urls_hawkeye(match_id)} to debug")
        return

def get_trajectories_df_from_matchid(match_id): #retrieves data from uds/traj
    try:
        df = pd.DataFrame(
            [[k]+v.split(',') for i in json.loads(try_urls(get_candidate_urls_hawkeye_trajectories(match_id)))['data']
                for k, v in i.items()],
            columns=['over', 'ball_num', 'batter', 'non-striker',
                        'bowler', 'speed', 'catcher', 'dismissal_desc',
                        'total_extras', 'runs', 'extra_type', 'trajectoryString']
        )
        df['match_id'] = str(match_id)

        if ((df.shape[0] == 0) |
            ((df.speed.nunique() == 1) &
            (df.trajectoryString.nunique() == 1))):
            print(f'no data to fetch for {match_id}')
            return
        else:
            df['over'] = df.over.apply(lambda x: str(x).split('.'))
            df['match_inn'] = df.over.apply(lambda x: x[0])
            df['over_ball'] = pd.to_numeric(
                df.over.apply(lambda x: x[2]), errors='coerce')
            df['over_num'] = pd.to_numeric(
                df.over.apply(lambda x: x[1]), errors='coerce')
            df.drop('over', axis=1, inplace=True)

            df['speed'] = pd.to_numeric(df['speed'], errors='coerce')*3.6
            df.loc[df.speed < 0, 'speed'] = np.nan

            #decode the base64 trajectoryString
            #Decode base64 using base64 package, split into 32-bit hexademical (4 byte) components, and then unpack the IEEE754 float using struct package
            #As way of verification, bp.x and bp.y from uds/traj should match line and length data from uds/stats
            #oba.y returns at 0 at the significance used in the below function
            trajectoryElements = ['bp.x','bp.y','bt',
            'a.x','a.y','a.z',
            'ebv.x','ebv.y','ebv.z',
            'obv.x','obv.y','obv.z',
            'oba.x', 'oba.y', 'oba.z',
            'bh'] #name of columns from vendors.js, listed in the order they are stored in the hex string
            i = 0

            for offset in sorted(set(range(0,64,4))): #for every 4 bytes in the decoded hex string
                #create column for each trajectory element
                df[trajectoryElements[i]] =  df.trajectoryString.apply(
                    lambda x: struct.unpack('>f', base64.b64decode(x)[offset:offset+4])[0] #>f specifies big-endian floating point
                )
                i += 1

            return df
    except:
        print(
            f"couldn't retrieve data for match {match_id}. Please check {get_candidate_urls_hawkeye_trajectories(match_id)} to debug")
        return

def get_metadata_df_from_matchid(match_id):
    m = json.loads(try_urls(get_candidate_urls_metadata(match_id)))
    this_match = pd.DataFrame([{k: v for k, v in m['matchInfo'].items() if k in [
        'matchDate', 'matchEndDate', 'isLimitedOvers', 'description', 'matchType', 'tournamentLabel']}])
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
    venue_df = pd.DataFrame([m['matchInfo']['venue']])
    player_df = pd.concat([pd.DataFrame(m['matchInfo']['teams'][0]['players']),
                           pd.DataFrame(m['matchInfo']['teams'][1]['players'])
                           ]).drop_duplicates()

    venue_df.drop('coordinates', axis=1, inplace=True, errors='ignore')
    try:
        player_df['batter_hand'] = player_df.rightHandedBat.apply(
            lambda x: 'R' if x else 'L')
        player_df['bowler_hand'] = player_df.rightArmedBowl.apply(
            lambda x: 'R' if x else 'L')
    except:
        pass
    match_df.matchType = match_df.apply(lambda x: 'W_' + x.matchType if
                                        re.search('women', x.tournamentLabel.lower()) else x.matchType,
                                        axis=1)
    match_df['toss_winner'] = match_df.toss_elected.apply(
        lambda x: str(x).strip().lower().split(',')[0])
    match_df['toss_decision'] = match_df.toss_elected.apply(
        lambda x: str(x).lower().strip('.').split(' ')[-1])
    match_df['toss_decision'] = match_df.toss_decision.apply(
        lambda x: 'field' if str(x) == 'bowl' else str(x))
    match_df['toss_decision'] = match_df.toss_decision.apply(
        lambda x: x if str(x) in ['field', 'bat'] else '')
    match_df.drop('toss_elected', axis=1, inplace=True)
    return {'match_metadata': match_df,
            'player_metadata': player_df,
            'venue_metadata': venue_df}
