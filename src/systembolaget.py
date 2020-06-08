import json
import logging
from collections import namedtuple
from pathlib import Path
from typing import Iterator, List

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
        return f"https://www.systembolaget.se/{self.ProductNumberShort}"

    def __str__(self) -> str:
        return f"{self.Vintage} {self.ProductNameBold}, {self.ProductNameThin}"

    def __repr__(self) -> str:
        return self.__str__()


class SystembolagetAPI:
    _api_url = 'https://api-extern.systembolaget.se/'

    def __init__(self, api_token: str):
        self._headers = {'Ocp-Apim-Subscription-Key': api_token}
        self._cache_dir = Path(__file__).resolve().parent.parent / 'cache'
        self._cache_dir.mkdir(exist_ok=True)
        self._all_sites_file = self._cache_dir / 'systembolaget_all_sites.json'
        self._inventory_file = self._cache_dir / 'systembolaget_inventory.json'
        self._products_with_stores_file = \
            self._cache_dir / 'systembolaget_products_with_store.json'

    def clear_cache(self) -> None:
        logger.info(f"Deleting cache files from '{self._cache_dir}'")
        self._all_sites_file.unlink(missing_ok=True)
        self._inventory_file.unlink(missing_ok=True)
        self._products_with_stores_file.unlink(missing_ok=True)

    def _download_all_sites(self) -> None:
        api_url = self._api_url + 'site/v1/site'
        logger.info(f"Downloading info on sites from '{api_url}'")
        with requests.get(api_url, headers=self._headers) as response:
            response.raise_for_status()
            with self._all_sites_file.open('w') as file:
                json.dump(response.json(), file, indent=2, ensure_ascii=False)

    def _load_all_sites(self) -> List[dict]:
        if not self._all_sites_file.is_file():
            self._download_all_sites()
        with self._all_sites_file.open('r') as file:
            all_sites = json.load(file)
        logger.info(f"Loaded {len(all_sites)} site info items")
        return all_sites

    def get_sites(self) -> Iterator[dict]:
        yield from self._load_all_sites()

    def _download_products_with_store(self) -> None:
        api_url = self._api_url + 'product/v1/product/getproductswithstore'
        logger.info(f"Downloading product-store availability from '{api_url}'")
        with requests.get(api_url, headers=self._headers) as response:
            response.raise_for_status()
            with self._products_with_stores_file.open('w') as file:
                json.dump(response.json(), file, indent=2, ensure_ascii=False)

    def _load_products_with_store(self) -> List[dict]:
        if not self._products_with_stores_file.is_file():
            self._download_products_with_store()
        with self._products_with_stores_file.open('r') as file:
            products_with_store = json.load(file)
        logger.info(f"Loaded {len(products_with_store)} product-store items")
        return products_with_store

    def get_products_with_store(self) -> Iterator[dict]:
        yield from self._load_products_with_store()

    def _download_inventory(self) -> None:
        api_url = self._api_url + 'product/v1/product/'
        logger.info(f"Downloading inventory from '{api_url}'")
        with requests.get(api_url, headers=self._headers) as response:
            response.raise_for_status()
            with self._inventory_file.open('w') as file:
                json.dump(response.json(), file, indent=2, ensure_ascii=False)

    def _load_inventory(self) -> List[dict]:
        if not self._inventory_file.is_file():
            self._download_inventory()
        with self._inventory_file.open('r') as file:
            inventory = json.load(file)
        logger.info(f"Loaded {len(inventory)} inventory items")
        return inventory

    def get_inventory(self, stock_required=False) -> Iterator[InventoryItem]:
        for item in self._load_inventory():
            if not stock_required or not item['IsCompletelyOutOfStock']:
                yield InventoryItem(**item)

    def get_red_wines(self, stock_required=False) -> Iterator[InventoryItem]:
        for inventory_item in self.get_inventory(stock_required):
            if inventory_item.is_red_wine():
                yield inventory_item

    @staticmethod
    def parse_opening_hours(opening_hours: dict) -> str:
        if opening_hours['IsOpen']:
            return "Open from {} until {}".format(
                opening_hours['OpenFrom'][:5],
                opening_hours['OpenTo'][:5]
            )

        if opening_hours['Reason'] and opening_hours['Reason'] != '-':
            return f"Closed because of '{opening_hours['Reason']}'"

        return "Closed"
