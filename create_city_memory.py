import json
import os
from langchain.schema import Document
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

with open(r'data/varanasi/varanasi.json','r',encoding='utf-8') as f:
    data=json.load(f)

raw_texts=[]

for city in data["General-city-info"]:
    name = city.get("city-name", "")
    state = city.get("state/union-territory", "")
    alt_names = city.get("alternate-names", "")
    languages = city.get("languages-spoken", "")
    climate = city.get("climate-info", "")
    best_time = city.get("best-time-to-visit", "")
    history = city.get("city-history", "")
    cover_image = city.get("cover-image", "")

    full_desc = (
        f"City: {name}, {state}\n"
        f"Alternate Names: {alt_names}\n"
        f"Languages Spoken: {languages}\n"
        f"Climate Info: {climate}\n"
        f"Best Time to Visit: {best_time}\n"
        f"History:\n{history}\n"
        f"Cover Image: {cover_image}\n"
    )

    raw_texts.append(
        Document(
            page_content=full_desc,
            metadata={
                "section": "general-city-info"
            }
        )
    )

for transport in data["Connectivity(Transportation-Hub"]:
    name = transport.get("nearest-airport/station/bus-stand", "")
    distance = transport.get("distance", "")
    latlon = transport.get("lat-lon", "")
    gmap = transport.get("location-link", "")
    major_routes = transport.get("major-flights/trains/buses", "")

    full_desc = (
        f"Transportation Hub: {name}\n"
        f"Location Coordinates: {latlon}\n"
        f"Distance from City Center: {distance}\n"
        f"Google Maps: {gmap}\n"
        f"Major Connectivity: {major_routes}\n"
    )

    raw_texts.append(
        Document(
            page_content=full_desc,
            metadata={
                "section": "transportation-hub"
            }
        )
    )

for place in data["Places-to-visit"]:
    name = place.get("places ", "").strip()
    category = place.get("category", "")
    latlon = place.get("lat-lon", "")
    address = place.get("address", "")
    gmap = place.get("location-link", "")
    open_day = place.get("open-day", "")
    open_time = place.get("open-time", "")
    guide = place.get("guide-availiblity", "")
    year = place.get("establish-year", "")
    fee = place.get("fee", "")
    description = place.get("description", "")
    essentials = place.get("essential", "")
    story = place.get("story", "")
    image0 = place.get("image0", "")
    image1 = place.get("image1", "")
    image2 = place.get("image2", "")
    video = place.get("video", "")

    # 💡 Build rich description for semantic search
    full_desc = (
        f"Place Name: {name}\n"
        f"Category: {category}\n"
        f"Location: {latlon}\n"
        f"Address: {address}\n"
        f"Google Maps: {gmap}\n"
        f"Open Days: {open_day}\n"
        f"Timings: {open_time}\n"
        f"Guide Availability: {guide}\n"
        f"Established: {year}\n"
        f"Entry Fees: {fee}\n"
        f"Description: {description}\n"
        f"Essentials to Know: {essentials}\n"
        f"Historical Story: {story}\n"
        f"Images: {image0}, {image1}, {image2}\n"
        f"Video: {video}\n"
    )

    raw_texts.append(
        Document(
            page_content=full_desc,
            metadata={
                "section": "places-to-visit"
            }
        )
    )

for gem in data["Hidden-gems"]:
    name = gem.get("hidden-gems", "")
    category = gem.get("category", "")
    latlon = gem.get("lat-lon", "")
    address = gem.get("address", "")
    gmap = gem.get("location-link", "")
    open_day = gem.get("open-day", "")
    open_time = gem.get("open-time", "")
    guide = gem.get("guide-availiblity", "")
    year = gem.get("establish-year", "")
    fee = gem.get("fee", "")
    description = gem.get("description", "")
    essentials = gem.get("essential", "")
    story = gem.get("story", "")
    image0 = gem.get("image0", "")
    image1 = gem.get("image1", "")
    image2 = gem.get("image2", "")
    video = gem.get("video", "")

    # 💡 Build rich description for semantic search
    full_desc = (
        f"Hidden Gem: {name}\n"
        f"Category: {category}\n"
        f"Location: {latlon}\n"
        f"Address: {address}\n"
        f"Google Maps: {gmap}\n"
        f"Open Days: {open_day}\n"
        f"Timings: {open_time}\n"
        f"Guide Availability: {guide}\n"
        f"Established: {year}\n"
        f"Entry Fees: {fee}\n"
        f"Description: {description}\n"
        f"Essentials to Know: {essentials}\n"
        f"Historical Story: {story}\n"
        f"Images: {image0}, {image1}, {image2}\n"
        f"Video: {video}\n"
    )

    raw_texts.append(
        Document(
            page_content=full_desc,
            metadata={
                "section": "hidden-gems"
            }
        )
    )

for spot in data["Nearby-tourist-spot"]:
    name = spot.get("places ", "").strip()
    distance = spot.get("distance", "")
    category = spot.get("category", "")
    latlon = spot.get("lat-lon", "")
    address = spot.get("address", "")
    gmap = spot.get("location-link", "")
    open_day = spot.get("open-day", "")
    open_time = spot.get("open-time", "")
    guide = spot.get("guide availiblity", "")
    year = spot.get("establish-year", "")
    fee = spot.get("fee", "")
    description = spot.get("description", "")
    essentials = spot.get("essential", "")
    story = spot.get("story", "")
    image0 = spot.get("image0", "")
    image1 = spot.get("image1", "")
    image2 = spot.get("image2", "")
    video = spot.get("video", "")

    # 💡 Build rich description for semantic search
    full_desc = (
        f"Tourist Spot: {name}\n"
        f"Distance: {distance}\n"
        f"Category: {category}\n"
        f"Location: {latlon}\n"
        f"Address: {address}\n"
        f"Google Maps: {gmap}\n"
        f"Open Days: {open_day}\n"
        f"Timings: {open_time}\n"
        f"Guide Availability: {guide}\n"
        f"Established: {year}\n"
        f"Entry Fees: {fee}\n"
        f"Description: {description}\n"
        f"Essentials to Know: {essentials}\n"
        f"Historical Story: {story}\n"
        f"Images: {image0}, {image1}, {image2}\n"
        f" Video: {video}\n"
    )

    raw_texts.append(
        Document(
            page_content=full_desc,
            metadata={
                "section": "nearby-tourist-spot"
            }
        )
    )

for activity in data["Activities"]:
    name = activity.get("Activities", "").strip()
    location = activity.get("best - places", "").strip()
    description = activity.get("description ", "").strip()
    essentials = activity.get("essential", "").strip()
    fee = activity.get("fee", "").strip()
    image = activity.get("image", "").strip()
    video = activity.get("video", "").strip()

    # 🧠 Compose detailed description
    full_desc = (
        f"Activity: {name}\n"
        f"Best Place: {location}\n"
        f"Description: {description}\n"
        f"Essentials to Know: {essentials}\n"
        f"Cost: {fee}\n"
        f"Image: {image}\n"
        f"Video: {video}\n"
    )

    # 📦 Append as a Document
    raw_texts.append(
        Document(
            page_content=full_desc,
            metadata={"section": "activities"}
        )
    )

for food in data["Food"]:
    name = food.get("food-place", "").strip()
    category = food.get("category", "")
    latlon = food.get("lat-lon", "")
    address = food.get("address", "")
    gmap = food.get("location-link", "")
    veg_status = food.get("veg/non-veg", "")
    value = food.get("value-for-money", "")
    service = food.get("service", "")
    taste = food.get("taste", "")
    hygiene = food.get("hygeine", "")
    special = food.get("menu-special", "")
    menu_link = food.get("menu-link", "")
    open_day = food.get("open-day", "")
    open_time = food.get("open-time", "")
    phone = food.get("phone", "")
    desc = food.get("description", "")
    image0 = food.get("image0", "")
    image1 = food.get("image1", "")
    image2 = food.get("image2", "")
    video = food.get("video", "")

    # 🧠 Build full description
    full_desc = (
        f"Food Place: {name}\n"
        f"Location: {latlon}\n"
        f"Address: {address}\n"
        f"Google Maps: {gmap}\n"
        f"Category: {category} | Type: {veg_status}\n"
        f"Contact: {phone}\n"
        f"Open Days: {open_day} | Timings: {open_time}\n"
        f"Specialties: {special}\n"
        f"Menu: {menu_link}\n"
        f"Ratings — Value: {value}/5 | Service: {service}/5 | Taste: {taste}/5 | Hygiene: {hygiene}/5\n"
        f"Description: {desc}\n"
        f"Images: {image0}, {image1}, {image2}\n"
        f"Video: {video}\n"
    )

    # 📦 Append to raw_texts
    raw_texts.append(
        Document(
            page_content=full_desc,
            metadata={"section": "food"}
        )
    )  

for shop in data["Shopping"]:
    name = shop.get("shops", "")
    category = shop.get("category", "")
    latlon = shop.get("lat-lon", "")
    address = shop.get("address", "")
    gmap = shop.get("location-link", "")
    famous_for = shop.get("famous-for", "")
    price_range = shop.get("price-range", "")
    open_day = shop.get("open-day", "")
    open_time = shop.get("open-time", "")
    phone = shop.get("phone", "")
    website = shop.get("website", "")
    image0 = shop.get("image0", "")
    image1 = shop.get("image1", "")
    image2 = shop.get("image2", "")

    # 💡 Build rich description for semantic search
    full_desc = (
        f"Shop Name: {name}\n"
        f"Category: {category}\n"
        f"Location: {latlon}\n"
        f"Address: {address}\n"
        f"Google Maps: {gmap}\n"
        f"Famous For: {famous_for}\n"
        f"Price Range: {price_range}\n"
        f"Open Days: {open_day}\n"
        f"Timings: {open_time}\n"
        f"Phone: {phone}\n"
        f"Website: {website}\n"
        f"Images: {image0}, {image1}, {image2}\n"
    )

    raw_texts.append(
        Document(
            page_content=full_desc,
            metadata={
                "section": "shopping"
            }
        )
    )

for hotel in data["Accomodation"]:
    name = hotel.get("hotels", "")
    address = hotel.get("address", "")
    category = hotel.get("category", "")
    room_price = hotel.get("types-of-room-price", "")
    facilities = hotel.get("facilities(parking,lift,ac,wifi,resturant,etc)", "")
    latlon = hotel.get("lat-lon", "")
    gmap = hotel.get("location-link", "")
    image0 = hotel.get("image0", "")
    image1 = hotel.get("image1", "")
    image2 = hotel.get("image2", "")

    # 💡 Build rich description for semantic search
    full_desc = (
        f"Hotel Name: {name}\n"
        f"Address: {address}\n"
        f"Location: {latlon}\n"
        f"Google Maps: {gmap}\n"
        f"Category: {category}\n"
        f"Rooms & Prices: {room_price}\n"
        f"Facilities: {facilities}\n"
    )

    raw_texts.append(
        Document(
            page_content=full_desc,
            metadata={
                "section": "accommodation"
            }
        )
    )

for transport in data["Local-transport"]:
    source = transport.get("from", "").strip()
    destination = transport.get("to", "").strip()
    auto = transport.get("auto-price", "").strip()
    cab = transport.get("cab-price", "").strip()
    bike = transport.get("bike-price", "").strip()

    full_desc = (
        f"Route: {source} to {destination}\n"
        f"Auto Price Range: {auto}\n"
        f"Cab Price Range: {cab}\n"
        f"Bike Price Range: {bike}"
    )

    raw_texts.append(Document(page_content=full_desc))

embedding_model=HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

db = FAISS.from_documents(raw_texts, embedding_model)

DB_FAISS_PATH = "vectorstore/db_faiss_varanasi"
db.save_local(DB_FAISS_PATH)

print(f"Indexed {len(raw_texts)} varanasi data into FAISS DB.")
