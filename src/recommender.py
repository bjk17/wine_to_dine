import os
import logging
from collections import defaultdict
from typing import Iterable, Iterator, Tuple

from fuzzywuzzy import fuzz, process

from src.globalwinescore import Scoring, GlobalWineScore
from src.systembolaget import InventoryItem, SystembolagetAPI

logger = logging.getLogger("Recommender")
logging.basicConfig(
    format='%(asctime)-15s %(levelname)-4s (%(name)s) %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

Certainty = int
ScoreAssignment = Tuple[InventoryItem, Certainty, Scoring]


def assign_scorings(
        inventory_items: Iterable[InventoryItem], scorings: Iterable[Scoring],
        fuzz_match_min_percentage: int = 90) -> Iterator[ScoreAssignment]:
    # Optimising fuzzy match by pre-filtering GWS scores by country and vintage
    fuzzy_scoring = defaultdict(lambda: defaultdict(dict))
    for i, scoring in enumerate(scorings, start=1):
        country, vintage = scoring.get_country(), scoring.vintage
        fuzzy_scoring[country][vintage][scoring.fuzzy_name()] = scoring

    matched_wines = 0
    for j, inventory_item in enumerate(inventory_items, start=1):
        fuzzy_name = inventory_item.fuzzy_name()
        country = inventory_item.get_country()
        vintage = str(inventory_item.Vintage)
        if fuzzy_scoring[country][vintage]:
            best_match_key, certainty = process.extractOne(
                fuzzy_name, fuzzy_scoring[country][vintage].keys(),
                scorer=fuzz.token_set_ratio)

            if certainty >= fuzz_match_min_percentage:
                matched_wines += 1
                scoring = fuzzy_scoring[country][vintage][best_match_key]
                yield inventory_item, certainty, scoring

    logger.info(f"{matched_wines}/{j} inventory items matched {i} scorings "
                f"with minimum certainty of {fuzz_match_min_percentage}%")


def main() -> None:
    SB_API_TOKEN = os.environ.get('SB_API_TOKEN')
    sb = SystembolagetAPI(SB_API_TOKEN)

    GWS_API_TOKEN = os.environ.get('GWS_API_TOKEN')
    gws = GlobalWineScore(GWS_API_TOKEN)

    print("Recommending red wines available online at Systembolaget.se "
          "for a max price of SEK 400")
    sorted_red_wine_matches = sorted(
        assign_scorings(
            filter(lambda item: item.Price <= 400,
                   sb.get_red_wines(stock_required=True)),
            filter(lambda scoring: scoring.score >= 92,
                   gws.get_red_wines())
        ),
        key=lambda triple: triple[2].score,
        reverse=True
    )

    for (inventory_item, certainty, scoring) in sorted_red_wine_matches:
        print(f"Score: {scoring.score:.2f}% | "
              f"SEK {int(inventory_item.Price):3} | "
              f"{int(inventory_item.Volume):4}mL, "
              f"{inventory_item.AlcoholPercentage:2.1f}% | "
              f"{inventory_item} ({inventory_item.get_url()}) | "
              f"{scoring} ({scoring.get_url()}) | "
              f"{certainty:3d}% match")


if __name__ == "__main__":
    main()
