import unittest
import json
from pathlib import Path

from src.systembolaget import InventoryItem, SystembolagetAPI


class TestInventoryItem(unittest.TestCase):

    def setUp(self) -> None:
        self.black_stallion = json.loads('''
          {
            "ProductId": "975717",
            "ProductNumber": "620701",
            "ProductNameBold": "Black Stallion",
            "ProductNameThin": "Cabernet Sauvignon",
            "Category": "Röda viner",
            "ProductNumberShort": "6207",
            "ProducerName": "Black Stallion Estate Winery",
            "SupplierName": "Ward Wines AB",
            "IsKosher": false,
            "BottleTextShort": "Flaska",
            "Seal": "Naturkork",
            "RestrictedParcelQuantity": 0,
            "IsOrganic": false,
            "IsEthical": false,
            "EthicalLabel": null,
            "IsWebLaunch": false,
            "SellStartDate": "2015-12-01T00:00:00",
            "IsCompletelyOutOfStock": false,
            "IsTemporaryOutOfStock": false,
            "AlcoholPercentage": 14.5,
            "Volume": 750.0,
            "Price": 239.0,
            "Country": "USA",
            "OriginLevel1": "Kalifornien",
            "OriginLevel2": "North Coast",
            "Vintage": 2016,
            "SubCategory": "Rött vin",
            "Type": "Fruktigt & Smakrikt",
            "Style": null,
            "AssortmentText": "Fast sortiment",
            "BeverageDescriptionShort": "Rött vin, Fruktigt & Smakrikt",
            "Usage": "Serveras vid cirka 18°C till rätter av mörkt kött.",
            "Taste": "Nyanserad, mycket fruktig smak med rostad fatkaraktär..",
            "Assortment": "FS",
            "RecycleFee": 0.0,
            "IsManufacturingCountry": false,
            "IsRegionalRestricted": false,
            "IsInStoreSearchAssortment": null,
            "IsNews": false
          }
        ''')
        self.inventory_item = InventoryItem(**self.black_stallion)

    def test_object_attributes(self) -> None:
        self.assertTrue(self.inventory_item.is_red_wine())
        self.assertTrue(self.inventory_item.get_url().startswith('https://'))
        self.assertEqual('Usa', self.inventory_item.get_country())


class TestSystembolaget(unittest.TestCase):

    def setUp(self) -> None:
        _data_dir = Path(__file__).resolve().parent / 'data'
        self.stores = ('Globen', 'Ringen', 'Gullmarsplan')
        self.systembolaget = SystembolagetAPI('api_token')
        self.systembolaget._all_sites_file = _data_dir / 'sb_all_sites.json'
        self.systembolaget._inventory_file = _data_dir / 'sb_inventory.json'

    def test_get_inventory(self) -> None:
        inventory = list(self.systembolaget.get_inventory())
        self.assertEqual(2, len(inventory))

    def test_get_red_wines(self) -> None:
        red_wines = list(self.systembolaget.get_red_wines())
        self.assertEqual(1, len(red_wines))

    def test_get_sites(self) -> None:
        sites = list(self.systembolaget.get_sites())
        self.assertEqual(3, len(sites))


class TestParsingOpeningHours(unittest.TestCase):

    def test_open(self) -> None:
        opening_hours = json.loads('''
          {
            "IsOpen": true,
            "Reason": null,
            "Date": "2020-06-08T00:00:00",
            "OpenFrom": "10:00:00",
            "OpenTo": "19:00:00"
          }
        ''')
        self.assertEqual("Open from 10:00 until 19:00",
                         SystembolagetAPI.parse_opening_hours(opening_hours))

    def test_closed(self) -> None:
        opening_hours = json.loads('''
          {
            "IsOpen": false,
            "Reason": "-",
            "Date": "2020-06-07T00:00:00",
            "OpenFrom": "00:00:00",
            "OpenTo": "00:00:00"
          }
        ''')
        self.assertEqual("Closed",
                         SystembolagetAPI.parse_opening_hours(opening_hours))

    def test_closed_with_reason(self) -> None:
        opening_hours = json.loads('''
          {
            "IsOpen": false,
            "Reason": "Nationaldagen",
            "Date": "2020-06-06T00:00:00",
            "OpenFrom": "00:00:00",
            "OpenTo": "00:00:00"
          }
        ''')
        self.assertEqual("Closed because of 'Nationaldagen'",
                         SystembolagetAPI.parse_opening_hours(opening_hours))
