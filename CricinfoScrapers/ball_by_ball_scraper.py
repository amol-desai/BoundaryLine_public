__author__ = "Amol Desai"
__copyright__ = "Copyright 2021, BoundaryLine"
__credits__ = ["Amol Desai"]
__license__ = "MPL 2.0"
__version__ = "0.1.0"
__maintainer__ = "Amol Desai"
__email__ = "amol.desai@gmail.com"
__status__ = "Development"

import pandas as pd
import numpy as np
import re
import json
import helpers


def get_ball_by_ball_from_match_id(match_id, include_commentary=True):
    # Scrape ball by ball data from Cricinfo commentary for the match
    # Includes commentary text. This can be disabled to reduce data size

    series_id = helpers.get_series_id_from_match_page(
        helpers.get_match_url_from_match_id(match_id))
    url_template = "http://site.web.api.espn.com/apis/site/v2/sports/cricket/{series_id}/playbyplay?event={match_id}&page={page_num}"

    soup = helpers.get_soup_from_url(url_template.format(
        series_id=str(series_id),
        match_id=str(match_id),
        page_num='1')
    )
    full_commentary_p1 = json.loads(str(soup.text), strict=False)['commentary']
    page_count = full_commentary_p1['pageCount']
    total_count = full_commentary_p1['count']
    rest_of_full_commentary = []
    for i in range(2, page_count+1):
        try:
            rest_of_full_commentary.append(
                json.loads(str(helpers.get_soup_from_url(url_template.format(
                    series_id=str(series_id),
                    match_id=str(match_id),
                    page_num=str(i)
                )).text), strict=False)['commentary']['items']
            )
        except:
            print('failed to get page{} of match{} of series{}'.format(
                str(i), str(match_id), str(series_id)))
    full_commentary = full_commentary_p1['items'] + [
        item for items in rest_of_full_commentary
        for item in items]
    if len(full_commentary) != total_count:
        print('total count does not match expected count')

    # trim the unruly full_commentary bush and and flatten the dict to be converted into a df

    trim_off_fields = ['clock',
                       'id',
                       'mediaId',
                       'preText',
                       'postText',
                       'sequence',
                       'shortText',
                       'team',
                       'athletesInvolved',
                       'scoreValue',
                       'homeScore',
                       'awayScore',
                       'media'
                       ]
    if not include_commentary:
        trim_off_fields = trim_off_fields + ['text']
    sink_hole = [i.pop(k, None)
                 for k in trim_off_fields for i in full_commentary]

    # remove playtype id = 0
    full_commentary = [
        i for i in full_commentary if i['playType']['id'] != '0']

    for ix, item in enumerate(full_commentary):

        full_commentary[ix]['playType'] = item['playType']['description']

        full_commentary[ix]['batsman_id'] = item['batsman']['athlete']['id']
        full_commentary[ix]['batsman_name'] = item['batsman']['athlete']['displayName']
        full_commentary[ix]['batting_team_id'] = item['batsman']['team']['id']
        full_commentary[ix]['batting_team_name'] = item['batsman']['team']['displayName']
        full_commentary[ix]['batsman_runs_cum'] = item['batsman']['totalRuns']
        full_commentary[ix]['batsman_balls_faced_cum'] = item['batsman']['faced']
        full_commentary[ix]['batsman_fours_cum'] = item['batsman']['fours']
        full_commentary[ix]['batsman_sixes_cum'] = item['batsman']['sixes']
        full_commentary[ix].pop('batsman', None)

        try:
            full_commentary[ix]['other_batsman_id'] = item['otherBatsman']['athlete']['id']
            full_commentary[ix]['other_batsman_name'] = item['otherBatsman']['athlete']['displayName']
            full_commentary[ix]['other_batsman_runs_cum'] = item['otherBatsman']['totalRuns']
            full_commentary[ix]['other_batsman_balls_faced_cum'] = item['otherBatsman']['faced']
            full_commentary[ix]['other_batsman_fours_cum'] = item['otherBatsman']['fours']
            full_commentary[ix]['other_batsman_sixes_cum'] = item['otherBatsman']['sixes']
        except:
            full_commentary[ix]['other_batsman_id'] = ''
            full_commentary[ix]['other_batsman_name'] = ''
            full_commentary[ix]['other_batsman_runs_cum'] = np.nan
            full_commentary[ix]['other_batsman_balls_faced_cum'] = np.nan
            full_commentary[ix]['other_batsman_fours_cum'] = np.nan
            full_commentary[ix]['other_batsman_sixes_cum'] = np.nan
        full_commentary[ix].pop('otherBatsman', None)

        full_commentary[ix]['bowler_id'] = item['bowler']['athlete']['id']
        full_commentary[ix]['bowler_name'] = item['bowler']['athlete']['displayName']
        full_commentary[ix]['bowler_maidens_cum'] = item['bowler']['maidens']
        full_commentary[ix]['bowler_balls_cum'] = item['bowler']['balls']
        full_commentary[ix]['bowler_wkts_cum'] = item['bowler']['wickets']
        full_commentary[ix]['bowler_conceded_cum'] = item['bowler']['conceded']
        full_commentary[ix]['fielding_team_id'] = item['bowler']['team']['id']
        full_commentary[ix]['fielding_team_name'] = item['bowler']['team']['displayName']
        full_commentary[ix].pop('bowler', None)

        try:
            full_commentary[ix]['other_bowler_id'] = item['otherBowler']['athlete']['id']
            full_commentary[ix]['other_bowler_name'] = item['otherBowler']['athlete']['displayName']
            full_commentary[ix]['other_bowler_maidens_cum'] = item['otherBowler']['maidens']
            full_commentary[ix]['other_bowler_balls_cum'] = item['otherBowler']['balls']
            full_commentary[ix]['other_bowler_wkts_cum'] = item['otherBowler']['wickets']
            full_commentary[ix]['other_bowler_overs_cum'] = item['otherBowler']['overs']
            full_commentary[ix]['other_bowler_conceded_cum'] = item['otherBowler']['conceded']
        except:
            full_commentary[ix]['other_bowler_id'] = ''
            full_commentary[ix]['other_bowler_name'] = ''
            full_commentary[ix]['other_bowler_maidens_cum'] = np.nan
            full_commentary[ix]['other_bowler_balls_cum'] = np.nan
            full_commentary[ix]['other_bowler_wkts_cum'] = np.nan
            full_commentary[ix]['other_bowler_overs_cum'] = np.nan
            full_commentary[ix]['other_bowler_conceded_cum'] = np.nan
        full_commentary[ix].pop('otherBowler', None)

        full_commentary[ix]['dismissal_type'] = item['dismissal']['type']
        try:
            full_commentary[ix]['dismissal_fielder_id'] = item['dismissal']['fielder']['athlete']['id']
            full_commentary[ix]['dismissal_fielder_name'] = item['dismissal']['fielder']['athlete']['displayName']
        except:
            full_commentary[ix]['dismissal_fielder_id'] = ''
            full_commentary[ix]['dismissal_fielder_name'] = ''
        full_commentary[ix].pop('dismissal', None)

        for k, v in item['innings'].items():
            if k == 'totalRuns':
                full_commentary[ix]['score_for_play'] = v
            elif k == 'day':
                full_commentary[ix]['match_day'] = v
            elif k == 'session':
                full_commentary[ix]['session'] = v
            elif k not in ['id', 'number', 'fallOfWickets', 'byes', 'noBalls', 'legByes', 'wides']:
                full_commentary[ix][k] = v
        full_commentary[ix].pop('innings', None)

        for k, v in item['over'].items():
            if k in ['noBall', 'wide', 'byes', 'legByes']:
                full_commentary[ix][k] = v
            elif k == 'actual':
                full_commentary[ix]['innings_ball'] = v
            elif k == 'unique':
                full_commentary[ix]['innings_unique_ball'] = v
        full_commentary[ix].pop('over', None)

        # using only date now
        # because I don't know what they are doing for timezone and
        # it doesn't look like they have actual time anyway
        full_commentary[ix]['date'] = item['date'][:-9]
        #full_commentary[ix]['date'] = pd.datetime.strptime(item['date'], '%Y-%m-%d')

    # if kph or mph is not available, try to get it from commentary
    def look_for_speed_in_comment(txt, kph_or_mph):
        if type(txt) != str:  # found some NaNs show up when there is no commentary e.g. A to B, 1 wide,
            return txt
        else:
            m = re.search('([0-9]+\.{{0,1}}[0-9]*)\s{{0,1}}{}m{{0,1}}ph'.format(kph_or_mph),
                          txt,
                          re.IGNORECASE)
            return float(m[1]) if m else np.nan
    df = pd.DataFrame.from_dict(full_commentary)
    for unit in ['K', 'M']:
        col = 'speed{}PH'.format(unit)
        df[col] = df.apply(
            lambda x: look_for_speed_in_comment(x['text'] if 'text' in x else '', unit), axis=1)
    df['match_id'] = match_id
    return df


def umpires_from_match_id(match_id):
    espn_soup = helpers.get_soup_from_url(
        f"https://www.espncricinfo.com/matches/engine/match/{match_id}.html")
    umpire_data = espn_soup.find(
        "td", string=re.compile("Umpires")).nextSibling.find_all("h5")
    return [i.text for i in umpire_data]
