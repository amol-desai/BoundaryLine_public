from helpers import get_soup_from_url
from bs4 import BeautifulSoup
import pandas as pd

ESPN_BOWLING_COLUMNS = ['Format', 'Mat', 'Inns', 'Balls', 'Runs', 'Wkts', 'BBI', 'BBM', 'Ave',
                        'Econ', 'SR', '4w', '5w', '10w']

ESPN_BATTING_COLUMNS = ['Format', 'Mat', 'Inns', 'NO', 'Runs', 'HS', 'Ave', 'BF', 'SR', '100s',
                        '50s', '4s', '6s', 'Ct', 'St'],


def get_player_data_from_player_id(player_id):
    """
    Gets player data from player id
    """
    player_data_url = f"http://stats.espncricinfo.com/ci/engine/player/{player_id}.html"
    soup = get_soup_from_url(player_data_url)
    player_data = {}
    player_data["player_id"] = player_id
    player_data["name"] = soup.find(
        "div", {"class": "player-card__details"}).find("h2").text
    player_data["country"] = soup.find(
        "span", {"class": "player-card__country-name"}).text
    for header in soup.find("div", {"class": "player_overview-grid"}):
        player_data[header.find("p").text] = header.find("h5").text
    overview_tables = pd.read_html(str(soup.find_all("table")))
    for table in overview_tables:
        if "Wkts" in table.columns:
            player_data["bowling_summary"] = table
        elif "100s" in table.columns:
            player_data["batting_summary"] = table

    return player_data


if __name__ == "__main__":
    player_data = get_player_data_from_player_id(
        "793463")
    print(player_data)
