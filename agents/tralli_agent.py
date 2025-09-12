# # from bots.tralli_food_bot import food_bot
# from bots.tralli_food_bot import FoodBot
# from bots.tralli_place_bot import PlaceBot
# from bots.tralli_souvenir_bot import SouvenirBot
# from bots.tralli_transport_bot import transport_bot
# from bots.tralli_misc_bot import misc_bot

# bot1=PlaceBot()
# bot2=FoodBot()
# bot3=SouvenirBot()
# # bot4=TransportBot()

# def handle_places_query(query: str) -> dict:
#     return {"response": bot1.place_bot(query)}

# def handle_food_query(query: str) -> dict:
#     # return {"response": food_bot(query)}
#     return {"response": bot2.food_bot(query)}
#     # return {"response": "Food query implemented"}

# def handle_souvenir_query(query: str) -> dict:
#     return {"response": bot3.souvenir_bot(query)}

# def handle_transport_query(query: str) -> dict:
#     return {"response": transport_bot(query)}

# def handle_miscellaneous_query(query: str) -> dict:
#     return {"response": misc_bot(query)}

from functools import lru_cache
from bots.tralli_place_bot import PlaceBot
from bots.tralli_food_bot import FoodBot
from bots.tralli_shop_bot import ShopBot
from bots.tralli_transport_bot import TransportBot
from bots.tralli_accommodation_bot import AccommodationBot
from bots.tralli_activity_bot import ActivityBot
from bots.tralli_hiddengem_bot import HiddenGemBot
from bots.tralli_itinerary_bot import ItineraryBot
from bots.tralli_nearbyspot_bot import NearbySpotBot
from bots.tralli_cityinfo_bot import CityInfoBot
from bots.tralli_connectivity_bot import ConnectivityBot
from bots.tralli_misc_structured_bot import MiscBot
from bots.tralli_misc_bot import misc_bot  # legacy fallback

@lru_cache(maxsize=8)
def get_city_handlers(city: str):
    try:
        place = PlaceBot(city)
        food = FoodBot(city)
        shop = ShopBot(city)
        transport = TransportBot(city)
        accommodation = AccommodationBot(city)
        activity = ActivityBot(city)
        hidden = HiddenGemBot(city)
        itinerary = ItineraryBot(city)
        nearby = NearbySpotBot(city)
        cityinfo = CityInfoBot(city)
        connectivity = ConnectivityBot(city)
        misc_struct = MiscBot(city)

        return {
            "place": lambda q: place.place_bot(q),
            "food": lambda q: food.food_bot(q),
            "shop": lambda q: shop.shop_bot(q),
            "transport": lambda q: transport.transport_bot(q),
            "accommodation": lambda q: accommodation.accommodation_bot(q),
            "activity": lambda q: activity.activity_bot(q),
            "hiddengem": lambda q: hidden.hiddengem_bot(q),
            "itinerary": lambda q: itinerary.itinerary_bot(q),
            "nearbyspot": lambda q: nearby.nearbyspot_bot(q),
            "cityinfo": lambda q: cityinfo.cityinfo_bot(q),
            "connectivity": lambda q: connectivity.connectivity_bot(q),
            "misc": lambda q: misc_struct.misc_bot(q) if misc_struct else {"results": [misc_bot(q)]},
        }
    except Exception as e:
        print(f"Error initializing bots for city '{city}':", e)
        return None
