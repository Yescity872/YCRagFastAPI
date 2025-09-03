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

from bots.tralli_place_bot import PlaceBot
from bots.tralli_food_bot import FoodBot
from bots.tralli_souvenir_bot import SouvenirBot
from bots.tralli_transport_bot import TransportBot
# from bots.tralli_misc_bot import misc_bot

def get_city_handlers(city: str):
    try:
        bot1 = PlaceBot(city)
        bot2 = FoodBot(city)
        bot3 = SouvenirBot(city)
        bot4 = TransportBot(city)

        return {
            "places": lambda query: {"response": bot1.place_bot(query)},
            "food": lambda query: {"response": bot2.food_bot(query)},
            "souvenir": lambda query: {"response": bot3.souvenir_bot(query)},
            "transport": lambda query: {"response": bot4.transport_bot(query)},
            # "miscellaneous": lambda query: {"response": misc_bot(query)},
        }
    except Exception as e:
        print(f"Error initializing bots for city '{city}':", e)
        return None
