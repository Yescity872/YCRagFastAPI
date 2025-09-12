from __future__ import annotations
from typing import Dict, Any, List

# Canonical key orders per detected content type
FOOD_ORDER: List[str] = [
    'cityId','cityName','flagship','foodPlace','lat','lon','address','locationLink',
    'category','vegOrNonVeg','valueForMoney','service','taste','hygiene',
    'menuSpecial','menuLink','openDay','openTime','phone','website','description',
    'images','videos','premium','section'
]

PLACE_ORDER: List[str] = [
    'cityId','cityName','places','category','lat','lon','address','locationLink',
    'openDay','openTime','establishYear','fee','description','essential','story',
    'images','videos','premium','section'
]

SOUVENIR_ORDER: List[str] = [
    'cityId','cityName','flagShip','shops','lat','lon','address','locationLink',
    'famousFor','priceRange','openDay','openTime','phone','website','images','premium','section'
]

TRANSPORT_ORDER: List[str] = [
    'cityId','cityName','from','to','autoPrice','cabPrice','bikePrice','openDay','openTime','description','premium','section'
]

# New category canonical orders
ACCOMMODATION_ORDER: List[str] = [
    'cityId','cityName','hotels','category','lat','lon','address','locationLink',
    'roomTypes','facilities','amenities','priceRange','rating','checkIn','checkOut',
    'phone','website','description','images','videos','premium','section'
]

ACTIVITY_ORDER: List[str] = [
    'cityId','cityName','topActivities','bestPlaces','category','fee','season','duration','difficulty',
    'description','equipment','safetyTips','images','videos','premium','section'
]

CITYINFO_ORDER: List[str] = [
    'cityId','cityName','stateOrUT','bestTimeToVisit','climateInfo','cityHistory',
    'famousFor','localLanguages','safety','altitude','population','areaSqKm','timezone','currency','tips','premium','section'
]

CONNECTIVITY_ORDER: List[str] = [
    'cityId','cityName','nearestAirportStationBusStand','distance','timeToReach','mode','majorFlightsTrainsBuses',
    'frequency','lastMileOptions','notes','premium','section'
]

HIDDENGEM_ORDER: List[str] = [
    'cityId','cityName','hiddenGem','category','lat','lon','address','locationLink',
    'description','story','bestTime','access','difficulty','tips','images','videos','premium','section'
]

ITINERARY_ORDER: List[str] = [
    'cityId','cityName','duration','theme','day1','day2','day3','day4','day5','totalCost','bestFor','notes','premium','section'
]

MISC_ORDER: List[str] = [
    'cityId','cityName','topic','question','answer','category','tags','source','updatedAt','premium','section'
]

NEARBYSPOT_ORDER: List[str] = [
    'cityId','cityName','places','category','lat','lon','address','locationLink','distance','travelTime','bestTime',
    'description','essential','story','images','videos','premium','section'
]

SHOP_ORDER: List[str] = [
    'cityId','cityName','shops','category','lat','lon','address','locationLink','famousFor','priceRange','openDay',
    'openTime','phone','website','description','images','videos','premium','section'
]


def _choose_order(meta: Dict[str, Any]) -> List[str]:
    if 'foodPlace' in meta:
        return FOOD_ORDER
    if 'shops' in meta and 'famousFor' in meta:
        # Distinguish souvenir vs general shop by presence of flagShip / flagShip vs shops only
        if 'flagShip' in meta or 'famousFor' in meta and 'priceRange' in meta and 'flagShip' in meta:
            return SOUVENIR_ORDER
        # Generic shop category (new Shop bot)
        return SHOP_ORDER
    if 'hotels' in meta:
        return ACCOMMODATION_ORDER
    if 'topActivities' in meta:
        return ACTIVITY_ORDER
    if 'nearestAirportStationBusStand' in meta:
        return CONNECTIVITY_ORDER
    if 'hiddenGem' in meta:
        return HIDDENGEM_ORDER
    if 'day1' in meta or 'day2' in meta or 'day3' in meta:
        return ITINERARY_ORDER
    if 'topic' in meta or ('question' in meta and 'answer' in meta):
        return MISC_ORDER
    if 'from' in meta and 'to' in meta:
        return TRANSPORT_ORDER
    if 'cityHistory' in meta or 'bestTimeToVisit' in meta:
        return CITYINFO_ORDER
    if 'places' in meta and ('distance' in meta or 'travelTime' in meta):
        return NEARBYSPOT_ORDER
    if 'places' in meta:
        return PLACE_ORDER
    return list(meta.keys())  # fallback: keep whatever order we got


def ordered_meta(meta: Dict[str, Any], drop_missing: bool = True) -> Dict[str, Any]:
    """Return a new dict with keys ordered canonically.

    Args:
        meta: Original metadata dict.
        drop_missing: If True, only include keys present in meta; otherwise include
                      all canonical keys inserting None for missing.
    """
    order = _choose_order(meta)
    if drop_missing:
        return {k: meta[k] for k in order if k in meta}
    return {k: meta.get(k) for k in order}

__all__ = ['ordered_meta']
