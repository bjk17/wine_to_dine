import json
import logging
from collections import namedtuple
from pathlib import Path
from typing import List

import requests

logger = logging.getLogger("Systembolaget")

INVENTORY_FIELDS = [
    "ProductId", "ProductNumber", "ProductNameBold", "ProductNameThin",
    "Category", "ProductNumberShort", "ProducerName", "SupplierName",
    "IsKosher", "BottleTextShort", "Seal", "RestrictedParcelQuantity",
    "IsOrganic", "IsEthical", "EthicalLabel", "IsWebLaunch", "SellStartDate",
    "IsCompletelyOutOfStock", "IsTemporaryOutOfStock", "AlcoholPercentage",
    "Volume", "Price", "Country", "OriginLevel1", "OriginLevel2", "Vintage",
    "SubCategory", "Type", "Style", "AssortmentText",
    "BeverageDescriptionShort", "Usage", "Taste", "Assortment", "RecycleFee",
    "IsManufacturingCountry", "IsRegionalRestricted",
    "IsInStoreSearchAssortment", "IsNews"]


class InventoryItem(namedtuple("InventoryItem", INVENTORY_FIELDS)):
    COUNTRY_NAME_LANGUAGE_CONVERSION = {
        'Argentina': 'Argentina',
        'Australien': 'Australia',
        'Chile': 'Chile',
        'Folkrepubliken Kina': 'China',
        'Frankrike': 'France',
        'Italien': 'Italy',
        'Nya Zeeland': 'New Zealand',
        'Sydafrika': 'South Africa',
        'Spanien': 'Spain',
        'USA': 'Usa'
    }

    def is_red_wine(self) -> bool:
        return self.Category == "Röda viner"

    def fuzzy_name(self) -> str:
        return f"{self.ProductNameBold} {self.ProductNameThin} " \
               f"{self.ProducerName}"

    def get_country(self) -> str:
        return self.COUNTRY_NAME_LANGUAGE_CONVERSION.get(self.Country, 'Other')

    def get_url(self) -> str:
        return f"https://www.systembolaget.se/{self.ProductNumber}"

    def __str__(self) -> str:
        return f"{self.Vintage} {self.ProductNameBold}, {self.ProductNameThin}"

    def __repr__(self) -> str:
        return self.__str__()


class Systembolaget:

    def __init__(self, api_token: str):
        self._api_url = 'https://api-extern.systembolaget.se/'
        self._headers = {'Ocp-Apim-Subscription-Key': api_token}
        self._cache_dir = Path(__file__).resolve().parent.parent / 'cache'
        self._cache_dir.mkdir(exist_ok=True)
        self._inventory_file = self._cache_dir / 'systembolaget_inventory.json'
        self._red_wines_file = self._cache_dir / 'systembolaget_red_wines.json'

    def clear_cache(self) -> None:
        logger.debug(f"Deleting cache files from '{self._cache_dir}'")
        for cache_file in (self._inventory_file, self._red_wines_file):
            try:
                # New in Python 3.8: The missing_ok=True parameter
                cache_file.unlink()
            except FileNotFoundError:
                pass

    def _download_inventory(self) -> None:
        product_api_url = self._api_url + 'product/v1/product/'
        logger.debug(f"Downloading inventory from '{product_api_url}'")

        with requests.get(product_api_url, headers=self._headers) as response:
            with open(self._inventory_file, 'w') as file:
                json.dump(response.json(), file, indent=2, ensure_ascii=False)

    def _load_inventory(self) -> List[dict]:
        if not self._inventory_file.is_file():
            self._download_inventory()

        with open(self._inventory_file, 'r') as file:
            return json.load(file)

    def get_inventory(self) -> List[InventoryItem]:
        inventory = [InventoryItem(**item) for item in self._load_inventory()]
        logger.info(f"{len(inventory)} items in inventory")
        return inventory

    def _generate_red_wines(self) -> None:
        red_wines = list(filter(
            lambda item: item['Category'] == 'Röda viner' and not item[
                'IsCompletelyOutOfStock'], self._load_inventory()))

        with open(self._red_wines_file, 'w') as file:
            json.dump(red_wines, file, indent=2, ensure_ascii=False)

    def _load_red_wines(self) -> List[dict]:
        if not self._red_wines_file.is_file():
            self._generate_red_wines()

        with open(self._red_wines_file, 'r') as file:
            return json.load(file)

    def get_red_wines(self) -> List[InventoryItem]:
        red_wines = self._load_red_wines()
        logger.info(f"Loaded {len(red_wines)} red wines from inventory")
        return [InventoryItem(**item) for item in red_wines]
