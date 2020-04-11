import unittest
import json
from pathlib import Path

from src.globalwinescore import WineWithScore, GlobalWineScore


class TestWineWithScore(unittest.TestCase):

    def setUp(self) -> None:
        self.chianti_classico_riserva = json.loads('''
          {
            "wine": "Marchesi Antinori, Villa Antinori, Chianti Classico Riserva",
            "wine_id": 147380,
            "wine_slug": "marchesi-antinori-villa-antinori-chianti-classico-riserva",
            "appellation": "Chianti Classico Riserva",
            "appellation_slug": "chianti-classico-riserva",
            "color": "Red",
            "wine_type": "",
            "regions": [
            "Tuscany"
            ],
            "country": "Italy",
            "classification": null,
            "vintage": "2015",
            "date": "2019-04-30",
            "is_primeurs": false,
            "score": 91.47,
            "confidence_index": "B",
            "journalist_count": 4,
            "lwin": null,
            "lwin_11": null
          }
        ''')
        self.wine = WineWithScore(**self.chianti_classico_riserva)

    def test_object_attributes(self) -> None:
        self.assertTrue(self.wine.is_red_wine())
        self.assertTrue(self.wine.get_url().startswith('https://'))
        self.assertEqual("Italy", self.wine.get_country())


class TestGlobalWineScore(unittest.TestCase):

    def setUp(self) -> None:
        self.gws = GlobalWineScore('api_token')

        # Overwrite file path to use test cache data
        self.gws._red_wines_file = \
            Path(__file__).resolve().parent / 'data' / 'gws_red_wines.json'

    def test_get_red_wines(self) -> None:
        red_wines = self.gws.get_red_wines()
        self.assertEqual(10, len(red_wines))
