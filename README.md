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
