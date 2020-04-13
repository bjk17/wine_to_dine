# wine_to_dine

[![Build Status](https://img.shields.io/travis/bjk17/wine_to_dine.svg?label=Linux%20CI&logo=travis&logoColor=white)](https://travis-ci.org/bjk17/wine_to_dine)
[![Licence](https://img.shields.io/github/license/bjk17/wine_to_dine.svg)](https://raw.githubusercontent.com/bjk17/wine_to_dine/master/LICENSE)

Recommends _good_ red wines that are available at [Systembolaget](https://www.systembolaget.se) 
(SB) based on scores from [Global Wine Score](https://www.globalwinescore.com) (GWS).


## Prerequisites

_(This project requires Python >= 3.6)_

Sign up and receive an API token from 
 * Systembolaget: [https://api-portal.systembolaget.se/]()
 * GlobalWineScore: [https://www.globalwinescore.com/auth/signup/]()

Set them as environment variables `SB_API_TOKEN` and `GWS_API_TOKEN`, respectively.


## Installing and running

    $ pip install -r requirements.txt
    $ python -m src.recommend_red_wines
    
    [INFO] (Systembolaget) Loaded 5868 red wines from inventory
    [INFO] (GlobalWineScores) Loaded top 10000 red wine scores out of 26496 in database
    [INFO] (RecommendRedWines) Trying to match 5517 red wines with a list of 7660 scorings
    [INFO] (RecommendRedWines) 36 red wines matched with minimum certainty of 90%
    Score: 99.35% | SEK 459 |  750mL, 14.0% | 2015 Hermitage, Domaine Jean-Louis Chave Sélection (https://www.systembolaget.se/7452601) | 2015 Domaine Jean-Louis Chave, Hermitage (https://www.globalwinescore.com/wine-score/domaine-jean-louis-chave-hermitage/2015/) | 100% match
    Score: 99.10% | SEK 850 |  750mL, 13.5% | 2016 Tignanello, None (https://www.systembolaget.se/3215201) | 2016 Marchesi Antinori, Tenuta Tignanello, Solaia, Toscana (https://www.globalwinescore.com/wine-score/marchesi-antinori-tenuta-tignanello-solaia-toscana/2016/) |  92% match
    Score: 98.41% | SEK 164 |  750mL, 14.5% | 2015 Hahn, Cabernet Sauvignon (https://www.systembolaget.se/7496101) | 2015 Kapcsandy Family Winery, State Lane Vineyard Grand-Vin Cabernet Sauvignon, Napa Valley (https://www.globalwinescore.com/wine-score/kapcsandy-family-winery-state-lane-vineyard-grand-vin-cabernet-sauvignon-napa-valley/2015/) |  91% match
    Score: 97.91% | SEK 649 |  750mL, 13.0% | 2015 Chambolle-Musigny, Domaine Roux (https://www.systembolaget.se/534701) | 2015 Domaine Georges & Christophe Roumier, Les Amoureuses, Chambolle Musigny Premier Cru (https://www.globalwinescore.com/wine-score/domaine-georges-christophe-roumier-les-amoureuses-chambolle-musigny-premier-cru/2015/) |  91% match
    Score: 97.85% | SEK 349 |  750mL, 13.0% | 2016 Charmes de Kirwan, Margaux (https://www.systembolaget.se/7745401) | 2016 Chateau Margaux, Margaux (https://www.globalwinescore.com/wine-score/chateau-margaux-margaux/2016/) | 100% match
    Score: 97.73% | SEK 429 |  750mL, 14.0% | 2013 Domaine Jean-Louis Chave, Hermitage Farconnet (https://www.systembolaget.se/7795801) | 2013 Domaine Jean-Louis Chave, Hermitage (https://www.globalwinescore.com/wine-score/domaine-jean-louis-chave-hermitage/2013/) | 100% match
    Score: 96.60% | SEK 699 |  750mL, 13.5% | 2016 Adrianna Vineyard, Fortuna Terrae Malbec (https://www.systembolaget.se/9581701) | 2016 Catena Zapata, Adrianna Vineyard Fortuna Terrae Malbec, Tupungato (https://www.globalwinescore.com/wine-score/catena-zapata-adrianna-vineyard-fortuna-terrae-malbec-tupungato/2016/) |  94% match
    Score: 95.89% | SEK 519 |  750mL, 14.0% | 2014 Vietti Barolo, Castiglione (https://www.systembolaget.se/9524501) | 2014 Vietti, Rocche di Castiglione , Barolo (https://www.globalwinescore.com/wine-score/vietti-rocche-di-castiglione-barolo/2014/) | 100% match
    Score: 95.25% | SEK 149 |  375mL, 14.5% | 2009 Chateau Laroque, Saint-Emilion Grand Cru (https://www.systembolaget.se/7326702) | 2009 Chateau Pavie, Saint Emilion Grand Cru (https://www.globalwinescore.com/wine-score/chateau-pavie-saint-emilion-grand-cru/2009/) |  91% match
    Score: 95.07% | SEK 899 |  750mL, 14.0% | 2014 Barolo Le Vigne, Sandrone (https://www.systembolaget.se/7829501) | 2014 Sandrone, Le Vigne, Barolo (https://www.globalwinescore.com/wine-score/sandrone-le-vigne-barolo/2014/) | 100% match
    
    (...TRUNCATED)


## What does the code do?

It uses [fuzzy string matching](https://chairnerd.seatgeek.com/fuzzywuzzy-fuzzy-string-matching-in-python/)[1]
to assign[2] every red wine from SB's inventory a score from GWS's database[3] and prints out the
score, price, size of bottle, names, URLs and match certainty for all items fulfilling the criteria
 - having a minimum GWS score of 92% and
 - costing no more than SEK 999 

_[1] The fuzzy matching is needed because the wines are registered differently between the sites_

_[2] For performance it pre-filters based on country and vintage (assumes correct registration)_

_[3] Currently only the top 10k scores (out of ~26.5k) are downloaded_

### Caching

All API responses (JSON data) are cached in the `wine_to_dine/cache` folder and are used in
consecutive runs of the program as long as the cache file exists on the disk. This is done partly
because GWS's API has some rate limiting (up to 10 requests per minute) but this also helped when
developing the code. 

To keep it simple stupid there is no cache invalidation logic in the code. Instead the user needs
to clear the cache manually as they see fit. The methods `Systembolaget.clear_cache()` and 
`GlobalWineScore.clear_cache()` were implemented and intentionally left for future development.


## Documentations

 * Systembolaget API: [https://api-portal.systembolaget.se/docs/services/]()
 * GlobalWineScore API: [https://globalwinescore.docs.apiary.io/]()


## Interesting next steps

The project is currently in a usable state for me personally, but as time and interest allows I'd
like to look at implementing the following features:

 - [ ] Filter recommendations on store availability
 - [ ] Make available as an interactive Telegram bot 
     + e.g., a `/recommend_red_wine` command that takes arguments such as store availability, 
     minimum score and price range
 