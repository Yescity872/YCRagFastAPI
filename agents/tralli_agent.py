# from bots.tralli_food_bot import food_bot
from bots.tralli_food_bot import FoodBot
from bots.tralli_place_bot import places_bot
from bots.tralli_souvenir_bot import SouvenirBot
from bots.tralli_transport_bot import transport_bot
from bots.tralli_misc_bot import misc_bot

bot2=FoodBot()
bot3=SouvenirBot()

def handle_places_query(query: str) -> dict:
    return {"response": places_bot(query)}

def handle_food_query(query: str) -> dict:
    # return {"response": food_bot(query)}
    return {"response": bot2.food_bot(query)}
    # return {"response": "Food query implemented"}

def handle_souvenir_query(query: str) -> dict:
    return {"response": bot3.souvenir_bot(query)}

def handle_transport_query(query: str) -> dict:
    return {"response": transport_bot(query)}

def handle_miscellaneous_query(query: str) -> dict:
    return {"response": misc_bot(query)}
