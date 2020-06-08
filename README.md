# wine_to_dine

[![Build Status](https://img.shields.io/travis/bjk17/wine_to_dine.svg?label=Linux%20CI&logo=travis&logoColor=white)](https://travis-ci.org/bjk17/wine_to_dine)
[![Licence](https://img.shields.io/github/license/bjk17/wine_to_dine.svg)](https://raw.githubusercontent.com/bjk17/wine_to_dine/master/LICENSE)

Recommends red wines that are available at [Systembolaget](https://www.systembolaget.se) 
(SB) based on scores from [Global Wine Score](https://www.globalwinescore.com) (GWS).


## Telegram bot

The easiest way to get recommendations is to interact with the [Telegram bot](https://t.me/SystembolagetBot).

![](docs/TelegramBotDemo.gif)


## Prerequisites

_(This project requires Python >= 3.8)_

Sign up and receive an API token from 
 * Systembolaget: https://api-portal.systembolaget.se/
 * GlobalWineScore: https://www.globalwinescore.com/auth/signup/

Set them as environment variables `SB_API_TOKEN` and `GWS_API_TOKEN`, respectively.


## Installing and running locally

    $ pip install -r requirements.txt
    $ python -m src.recommender
    
    Recommending red wines available online at Systembolaget.se for a max price of SEK 400
    Score: 97.85% | SEK 359 |  750mL, 13.0% | 2016 Charmes de Kirwan, Margaux (https://www.systembolaget.se/77454) | 2016 Chateau Margaux, Margaux (https://www.globalwinescore.com/wine-score/chateau-margaux-margaux/2016/) | 100% match
    Score: 95.25% | SEK 149 |  375mL, 14.5% | 2009 Chateau Laroque, Saint-Emilion Grand Cru (https://www.systembolaget.se/73267) | 2009 Chateau Pavie, Saint Emilion Grand Cru (https://www.globalwinescore.com/wine-score/chateau-pavie-saint-emilion-grand-cru/2009/) |  91% match
    Score: 93.31% | SEK 399 |  750mL, 13.5% | 2009 La Rioja Alta, Gran Reserva 904 (https://www.systembolaget.se/7462) | 2009 La Rioja Alta, Gran Reserva 904, Rioja (https://www.globalwinescore.com/wine-score/la-rioja-alta-gran-reserva-904-rioja/2009/) | 100% match
    Score: 92.78% | SEK 199 |  750mL, 14.5% | 2015 Norton, Privada (https://www.systembolaget.se/72889) | 2015 Bodega Norton, Privada Red, Lujan De Cuyo (https://www.globalwinescore.com/wine-score/bodega-norton-privada-red-lujan-de-cuyo/2015/) | 100% match
    Score: 92.71% | SEK 229 |  750mL, 14.5% | 2014 Beringer, Knights Valley Cabernet Sauvignon (https://www.systembolaget.se/74646) | 2014 Beringer Vineyards, Private Reserve Cabernet Sauvignon, Napa Valley (https://www.globalwinescore.com/wine-score/beringer-vineyards-private-reserve-cabernet-sauvignon-napa-valley/2014/) |  92% match
    Score: 92.66% | SEK 399 |  750mL, 13.5% | 2016 Gevrey-Chambertin, Vieilles Vignes Domaine (https://www.systembolaget.se/93088) | 2016 Domaine Denis Bachelet, Les Corbeaux Vieilles Vignes, Gevrey Chambertin Premier Cru (https://www.globalwinescore.com/wine-score/domaine-denis-bachelet-les-corbeaux-vieilles-vignes-gevrey-chambertin-premier-cru/2016/) |  90% match
    Score: 92.62% | SEK 279 |  750mL, 13.0% | 2016 Saint-Joseph Les Granilites, M Chapoutier (https://www.systembolaget.se/76395) | 2016 M. Chapoutier, Les Granits, Saint Joseph (https://www.globalwinescore.com/wine-score/m-chapoutier-les-granits-saint-joseph/2016/) |  96% match
    Score: 92.59% | SEK 239 |  750mL, 13.5% | 2009 Viña Arana, Reserva (https://www.systembolaget.se/89190) | 2009 La Rioja Alta, Vina Ardanza Reserva, Rioja (https://www.globalwinescore.com/wine-score/la-rioja-alta-vina-ardanza-reserva-rioja/2009/) |  95% match
    Score: 92.59% | SEK 289 |  750mL, 13.5% | 2009 Viña Ardanza, Reserva (https://www.systembolaget.se/2609) | 2009 La Rioja Alta, Vina Ardanza Reserva, Rioja (https://www.globalwinescore.com/wine-score/la-rioja-alta-vina-ardanza-reserva-rioja/2009/) |  99% match
    Score: 92.44% | SEK 359 |  750mL, 13.5% | 2016 Delas Chante-Perdrix, Cornas (https://www.systembolaget.se/2274) | 2016 Delas Freres, Chante Perdrix, Cornas (https://www.globalwinescore.com/wine-score/delas-freres-chante-perdrix-cornas/2016/) | 100% match
    Score: 92.00% | SEK 399 |  750mL, 14.5% | 2012 Brunello di Montalcino, San Filippo (https://www.systembolaget.se/75935) | 2012 San Polo, Brunello Di Montalcino (https://www.globalwinescore.com/wine-score/san-polo-brunello-di-montalcino/2012/) |  91% match


## What does the code do?

It uses [fuzzy string matching](https://chairnerd.seatgeek.com/fuzzywuzzy-fuzzy-string-matching-in-python/)[1]
to assign[2] every red wine from SB's inventory a score from GWS's database[3] and prints out the
score, price, size of bottle, names, URLs and match certainty for all items fulfilling the criteria
 - having a minimum GWS score of 92% and
 - costing no more than SEK 400

_[1] The fuzzy matching is needed because the wines are registered differently between the sites_

_[2] For performance it pre-filters based on country and vintage (assumes correct registration)_

_[3] Currently only the top 10k scores (out of ~26.5k) are downloaded_

### Caching

All API responses (JSON data) are cached in the `wine_to_dine/cache` folder and are used in
consecutive runs of the program as long as the cache file exists on the disk. This is done partly
because GWS's API has some rate limiting (up to 10 requests per minute) but this also helped when
developing the code.

To keep it simple stupid there is no cache invalidation logic in the code. Instead, the user needs
to clear the cache manually as they see fit. The methods `Systembolaget.clear_cache()` and
`GlobalWineScore.clear_cache()` were implemented and intentionally left for future development.


## Documentations

 * Systembolaget API: https://api-portal.systembolaget.se/docs/services/
 * GlobalWineScore API: https://globalwinescore.docs.apiary.io/


## Interesting next steps

The project is currently in a usable state for me personally, but as time and interest allows I'd
like to look at implementing the following features:

 - [x] Filter recommendations on store availability
 - [x] Make available as an interactive Telegram bot 
     + e.g., a `/recommend_red_wine` command that takes arguments such as store availability,
     minimum score and price range
 - [ ] Download all GWS wine scores in order to match with more of SB's inventory items
 - [ ] Also recommend white wines
 - [ ] Also recommend rosé (pink) wines
