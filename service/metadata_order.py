from __future__ import annotations
from typing import Dict, Any, List

# Canonical key orders per detected content type
FOOD_ORDER: List[str] = [
    '_id','cityId','cityName','flagship','foodPlace','lat','lon','address','locationLink',
    'category','vegOrNonVeg','valueForMoney','service','taste','hygiene',
    'menuSpecial','menuLink','openDay','openTime','phone','website','description',
    'images','videos','premium'
]

PLACE_ORDER: List[str] = [
    '_id','cityId','cityName','places','category','lat','lon','address','locationLink',
    'openDay','openTime','establishYear','fee','description','essential','story',
    'images','videos','premium'
]

SOUVENIR_ORDER: List[str] = [
    '_id','cityId','cityName','flagShip','shops','lat','lon','address','locationLink',
    'famousFor','priceRange','openDay','openTime','phone','website','images','premium'
]

TRANSPORT_ORDER: List[str] = [
    '_id','cityId','cityName','from','to','autoPrice','cabPrice','bikePrice','premium'
]

# New category canonical orders
ACCOMMODATION_ORDER: List[str] = [
    '_id','cityId','cityName','flagship','hotels','category','lat','lon','address','locationLink',
    'roomTypes','facilities','images','premium'
]

ACTIVITY_ORDER: List[str] = [
    '_id','cityId','cityName','topActivities','bestPlaces','fee','description','essentials','images','videos','premium'
]

CITYINFO_ORDER: List[str] = [
    '_id','cityId','cityName','stateOrUT','alternateNames','bestTimeToVisit','climateInfo','cityHistory',
    'languagesSpoken','coverImage','premium'
]

CONNECTIVITY_ORDER: List[str] = [
    '_id','cityId','cityName','nearestAirportStationBusStand','distance','majorFlightsTrainsBuses',
    'lat','lon','locationLink','premium'
]

HIDDENGEM_ORDER: List[str] = [
    '_id','cityId','cityName','hiddenGem','category','lat','lon','address','locationLink',
    'description','story','essential','establishYear','fee','openDay','openTime','images','videos','premium'
]

ITINERARY_ORDER: List[str] = [
    '_id','cityId','cityName','day1','day2','day3','premium'
]

MISC_ORDER: List[str] = [
    '_id','cityId','cityName','emergencyContacts','hospital','hospitalLat','hospitalLon','hospitalLocationLink',
    'PoliceLat','PoliceLon','PoliceLocationLink','parking','parkingLat','parkingLon','parkingLocationLink',
    'publicWashrooms','publicWashroomsLat','publicWashroomsLon','publicWashroomsLocationLink','localMap','premium'
]

NEARBYSPOT_ORDER: List[str] = [
    '_id','cityId','cityName','places','category','lat','lon','address','locationLink','distance',
    'description','essential','story','establishYear','fee','openDay','openTime','images','videos','premium'
]

SHOP_ORDER: List[str] = [
    '_id','cityId','cityName','flagship','shops','lat','lon','address','locationLink','famousFor','priceRange','openDay',
    'openTime','phone','website','images','premium'
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
