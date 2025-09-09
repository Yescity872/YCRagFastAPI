from __future__ import annotations
from typing import Dict, Any, List

# Canonical key orders per detected content type
FOOD_ORDER: List[str] = [
    'cityId','cityName','flagship','foodPlace','lat','lon','address','locationLink',
    'category','vegOrNonVeg','valueForMoney','service','taste','hygiene',
    'menuSpecial','menuLink','openDay','openTime','phone','website','description',
    'images','videos','premium'
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
    'cityId','cityName','from','to','autoPrice','cabPrice','bikePrice','openDay','openTime','description','premium'
]


def _choose_order(meta: Dict[str, Any]) -> List[str]:
    if 'foodPlace' in meta:
        return FOOD_ORDER
    if 'shops' in meta:
        return SOUVENIR_ORDER
    if 'from' in meta and 'to' in meta:
        return TRANSPORT_ORDER
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
