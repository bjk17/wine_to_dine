import unittest

from src.globalwinescore import Scoring
from src.recommend_red_wines import match_red_wines
from src.systembolaget import InventoryItem


class TestRedWineRecommendations(unittest.TestCase):

    def setUp(self) -> None:
        self.scoring = Scoring(
            wine="My favorite wine",
            wine_id=123456789,
            wine_slug="my-favorite-wine",
            appellation="Some awesome producer",
            appellation_slug="some-awesome-producer",
            color="Red",
            wine_type="",
            regions=["Moon"],
            country="Space",
            classification=None,
            vintage="1991",
            date="2020-04-14",
            is_primeurs=False,
            score="99.99",
            confidence_index="A+",
            journalist_count=0,
            lwin=321,
            lwin_11=321654,
        )
        self.inventory_item = InventoryItem(
            ProductId="987654321",
            ProductNumber="789456123",
            ProductNameBold="My wine",
            ProductNameThin="Favorite wine",
            Category="Röda viner",
            ProductNumberShort="789456",
            ProducerName="Awesome producer",
            SupplierName="Sneaky import AB",
            IsKosher=False,
            BottleTextShort="Flaska",
            Seal=None,
            RestrictedParcelQuantity=6,
            IsOrganic=False,
            IsEthical=False,
            EthicalLabel=None,
            IsWebLaunch=False,
            SellStartDate="2019-02-11T00:00:00",
            IsCompletelyOutOfStock=False,
            IsTemporaryOutOfStock=False,
            AlcoholPercentage=13.5,
            Volume=750.0,
            Price=444.0,
            Country="Space",
            OriginLevel1="Moon",
            OriginLevel2="Dark side",
            Vintage=1991,
            SubCategory="Rött vin",
            Type=None,
            Style=None,
            AssortmentText="Ordervaror",
            BeverageDescriptionShort="Rött vin",
            Usage=None,
            Taste=None,
            Assortment="BS",
            RecycleFee=0.0,
            IsManufacturingCountry=False,
            IsRegionalRestricted=False,
            IsInStoreSearchAssortment=None,
            IsNews=False,
        )

    def test_recommendation_sunny(self) -> None:
        recommendations = match_red_wines([self.inventory_item],
                                          [self.scoring])
        self.assertEqual(1, len(recommendations))
        self.assertIn(self.inventory_item, recommendations)
        certainty, scoring = recommendations[self.inventory_item]
        self.assertEqual(self.scoring, scoring)

    def test_recommendation_rainy(self) -> None:
        attr_overwriting = {
            'wine': 'A very bad wine',
            'appellation': 'Stinky brand'
        }
        new_scoring = Scoring(**{k: attr_overwriting.get(k, v)
                                 for (k, v) in self.scoring._asdict().items()})
        recommendations = match_red_wines([self.inventory_item], [new_scoring])
        self.assertEqual(0, len(recommendations))
