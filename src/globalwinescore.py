import json
import logging
from collections import namedtuple
from pathlib import Path
from typing import List
from urllib.parse import urlencode

import requests

logger = logging.getLogger("GlobalWineScores")

COUNTRY_LIST = ('Argentina', 'Australia', 'Chile', 'China', 'France', 'Italy',
                'New Zealand', 'Spain', 'South Africa', 'Usa')

GWS_FIELDS = [
    "wine", "wine_id", "wine_slug", "appellation", "appellation_slug", "color",
    "wine_type", "regions", "country", "classification", "vintage", "date",
    "is_primeurs", "score", "confidence_index", "journalist_count", "lwin",
    "lwin_11"]


class WineWithScore(namedtuple("WineWithScore", GWS_FIELDS)):

    def is_red_wine(self) -> bool:
        return self.color == 'Red'

    def fuzzy_name(self) -> str:
        return f"{self.wine} {self.appellation}"

    def get_country(self) -> str:
        return self.country if self.country in COUNTRY_LIST else 'Other'

    def get_url(self) -> str:
        return f"https://www.globalwinescore.com/wine-score/{self.wine_slug}" \
               f"/{self.vintage}/"

    def __str__(self) -> str:
        return f"{self.vintage} {self.wine}"

    def __repr__(self) -> str:
        return self.__str__()


class GlobalWineScore:

    def __init__(self, api_token: str):
        self._api_url = \
            'https://api.globalwinescore.com/globalwinescores/latest/'
        self._headers = {
            'Authorization': f"Token {api_token}",
            'Accept': 'application/json'
        }
        self._cache_dir = Path(__file__).resolve().parent.parent / 'cache'
        self._cache_dir.mkdir(exist_ok=True)
        self._red_wines_file = self._cache_dir / 'gws_red_wines.json'

    def clear_cache(self) -> None:
        logger.debug(f"Deleting cache files from '{self._cache_dir}'")
        try:
            # New in Python 3.8: The missing_ok=True parameter
            self._red_wines_file.unlink()
        except FileNotFoundError:
            pass

    def _download_red_wines(self) -> None:
        # As of mid April 2020 there are around 26.5k red wines in the database
        params = urlencode({
            'color': 'red',
            'limit': 10000,
            'ordering': '-score'
        })
        red_wine_api_url = self._api_url + f'?{params}'
        logger.debug(f"Downloading red wine scores from '{red_wine_api_url}'")

        with requests.get(red_wine_api_url, headers=self._headers) as response:
            with open(self._red_wines_file, 'w') as file:
                json.dump(response.json(), file, indent=2, ensure_ascii=False)

    def _load_red_wines(self) -> dict:
        if not self._red_wines_file.is_file():
            self._download_red_wines()

        with open(self._red_wines_file, 'r') as file:
            return json.load(file)

    def get_red_wines(self) -> List[WineWithScore]:
        red_wines = self._load_red_wines()
        logger.info(f"Loaded top {len(red_wines['results'])} red wine "
                    f"scores out of {red_wines['count']} in database")
        return [WineWithScore(**item) for item in red_wines['results']]
