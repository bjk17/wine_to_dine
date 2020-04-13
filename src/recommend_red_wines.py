import os
import logging
from collections import defaultdict
from typing import Dict, List, Tuple

from fuzzywuzzy import fuzz, process

from src.globalwinescore import Scoring, GlobalWineScore
from src.systembolaget import InventoryItem, Systembolaget

logger = logging.getLogger("RecommendRedWines")
logging.basicConfig(
    format='[%(levelname)-4s] (%(name)s) %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

Certainty = int
ScoreAssignments = Dict[InventoryItem, Tuple[Certainty, Scoring]]


def match_red_wines(inventory_items: List[InventoryItem],
                    scorings: List[Scoring],
                    fuzz_match_min_percentage: int = 90) -> ScoreAssignments:
    logger.info(f"Trying to match {len(inventory_items)} red wines "
                f"with a list of {len(scorings)} scorings")

    fuzzy_inventory = {item.fuzzy_name(): item for item in inventory_items}

    # Optimising fuzzy match by pre-filtering GWS scores by country and vintage
    fuzzy_scoring = defaultdict(lambda: defaultdict(dict))
    for scoring in scorings:
        country, vintage = scoring.get_country(), scoring.vintage
        fuzzy_scoring[country][vintage][scoring.fuzzy_name()] = scoring

    recommendations = dict()
    for sb_fuzzy_name, item in fuzzy_inventory.items():

        country, vintage = item.get_country(), str(item.Vintage)
        if fuzzy_scoring[country][vintage]:
            best_match_key, certainty = process.extractOne(
                sb_fuzzy_name, fuzzy_scoring[country][vintage].keys(),
                scorer=fuzz.token_set_ratio)

            if certainty >= fuzz_match_min_percentage:
                scoring = fuzzy_scoring[country][vintage][best_match_key]
                recommendations[item] = (certainty, scoring)

    logger.info(f"{len(recommendations)} red wines matched with "
                f"minimum certainty of {fuzz_match_min_percentage}%")

    return recommendations


def main() -> None:
    logging.getLogger().setLevel(logging.DEBUG)

    SB_API_TOKEN = os.environ.get('SB_API_TOKEN')
    sb = Systembolaget(SB_API_TOKEN)

    GWS_API_TOKEN = os.environ.get('GWS_API_TOKEN')
    gws = GlobalWineScore(GWS_API_TOKEN)

    wine_matches = match_red_wines(
        list(filter(lambda item: item.Price <= 999, sb.get_red_wines())),
        list(filter(lambda scoring: scoring.score >= 92, gws.get_red_wines()))
    )

    # Sort by GWS score, best to worst
    for (inventory_item, (certainty, scoring)) in sorted(
            wine_matches.items(),
            key=lambda score_assignment: score_assignment[1][1].score,
            reverse=True):
        print(f"Score: {scoring.score:.2f}% | "
              f"SEK {int(inventory_item.Price):3} | "
              f"{int(inventory_item.Volume):4}mL, "
              f"{inventory_item.AlcoholPercentage:2.1f}% | "
              f"{inventory_item} ({inventory_item.get_url()}) | "
              f"{scoring} ({scoring.get_url()}) | "
              f"{certainty:3d}% match")


if __name__ == "__main__":
    main()
