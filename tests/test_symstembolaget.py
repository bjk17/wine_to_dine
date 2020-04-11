import unittest
import json
from pathlib import Path

from src.systembolaget import InventoryItem, Systembolaget


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
            "Taste": "Nyanserad, mycket fruktig smak med rostad fatkaraktär, inslag av svarta vinbär, plommon, choklad, blåbär, mynta, kaffe och vanilj.",
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
        self.systembolaget = Systembolaget('api_token')
        self.systembolaget._inventory_file = _data_dir / 'sb_inventory.json'
        self.systembolaget._red_wines_file = _data_dir / 'sb_red_wines.json'

    def tearDown(self) -> None:
        try:
            # New in Python 3.8: The missing_ok=True parameter
            self.systembolaget._red_wines_file.unlink()
        except FileNotFoundError:
            pass

    def test_get_inventory(self) -> None:
        inventory = self.systembolaget.get_inventory()
        self.assertEqual(2, len(inventory))

    def test_get_red_wines(self) -> None:
        red_wines = self.systembolaget.get_red_wines()
        self.assertEqual(1, len(red_wines))
