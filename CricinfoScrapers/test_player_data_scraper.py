import unittest

from player_data_scraper import get_player_data_from_player_id
# test_player_data = __import__('../CricinfoScrapers/player_data_scraper.py')


class TestPlayerDataScraper(unittest.TestCase):
    def test_get_player_data_from_player_id(self):
        # self.assertEqual(get_player_data_from_player_id(player_id), expected_result)
        bumrah_id = 625383
        bumrah_data = get_player_data_from_player_id(bumrah_id)
        bumrah_role = bumrah_data['Playing Role']
        self.assertEqual(bumrah_role, 'Bowler')


if __name__ == '__main__':
    unittest.main()
