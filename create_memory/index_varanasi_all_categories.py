"""Index all Varanasi category datasets into Pinecone with separate namespaces.

Namespaces pattern: <Category>-Varanasi (e.g., Activity-Varanasi)
Vector id pattern: varanasi-<category-lower>-<idx>

Relies on the split files:
  Accommodation_varanasi.json, Activity_varanasi.json, ... Transport_varanasi.json
Each file keeps the category as its top-level key holding a list.
"""

from __future__ import annotations
import os, sys, json, math
from pathlib import Path
from typing import Dict, Any, List, Callable
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from service.embeddings import get_embeddings

ENV_PATH = ROOT / ".env"
_loaded = load_dotenv(dotenv_path=ENV_PATH, override=True)
if not _loaded:
    load_dotenv(override=True)

DATA_DIR = ROOT / "data" / "varanasi"
CITY = "varanasi"

CATEGORY_FILES: Dict[str, str] = {
    "Accommodation": "Accommodation_varanasi.json",
    "Activity": "Activity_varanasi.json",
    "Cityinfo": "Cityinfo_varanasi.json",
    "Connectivity": "Connectivity_varanasi.json",
    "Food": "Food_varanasi.json",
    "Hiddengem": "Hiddengem_varanasi.json",
    "Itinerary": "Itinerary_varanasi.json",
    "Misc": "Misc_varanasi.json",
    "Nearbyspot": "Nearbyspot_varanasi.json",
    "Place": "Place_varanasi.json",
    "Shop": "Shop_varanasi.json",
    "Transport": "Transport_varanasi.json",
}

# --- Embedding text builders per category (fallback generic) ---
def _join(values: List[str | None]) -> str:
    return " | ".join([v for v in values if v])

def build_text_generic(item: Dict[str, Any]) -> str:
    # Collect a few common textual fields heuristically
    keys = ["places", "hiddenGem", "foodPlace", "shops", "hotels", "topActivities", "from", "to", "description", "category"]
    parts = []
    for k in keys:
        v = item.get(k)
        if isinstance(v, str) and v.strip():
            parts.append(f"{k}:{v.strip()}")
    return " | ".join(parts) or json.dumps(item, ensure_ascii=False)[:1000]

def build_text_food(item):
    return f"Food:{item.get('foodPlace','')} Cat:{item.get('category','')} Menu:{item.get('menuSpecial','')} Desc:{item.get('description','')}"[:2048]

def build_text_place(item):
    return f"Place:{item.get('places','')} Cat:{item.get('category','')} Desc:{item.get('description','')} Story:{item.get('story','')}"[:2048]

def build_text_shop(item):
    return f"Shop:{item.get('shops','')} FamousFor:{item.get('famousFor','')} Price:{item.get('priceRange','')}"[:2048]

def build_text_transport(item):
    return f"Route from {item.get('from','')} to {item.get('to','')} Cab:{item.get('cabPrice','')} Auto:{item.get('autoPrice','')} Bike:{item.get('bikePrice','')}"[:512]

def build_text_activity(item):
    return f"Activity:{item.get('topActivities','')} Places:{item.get('bestPlaces','')} Desc:{item.get('description','')}"[:2048]

def build_text_hidden(item):
    return f"HiddenGem:{item.get('hiddenGem','')} Cat:{item.get('category','')} Desc:{item.get('description','')}"[:2048]

def build_text_accommodation(item):
    return f"Stay:{item.get('hotels','')} Cat:{item.get('category','')} Rooms:{item.get('roomTypes','')} Facilities:{item.get('facilities','')}"[:2048]

def build_text_connectivity(item):
    return f"Connect:{item.get('nearestAirportStationBusStand','')} Distance:{item.get('distance','')} Transport:{item.get('majorFlightsTrainsBuses','')}"[:2048]

def build_text_cityinfo(item):
    return f"City:{item.get('cityName','')} State:{item.get('stateOrUT','')} Climate:{item.get('climateInfo','')} History:{item.get('cityHistory','')}"[:2048]

def build_text_misc(item):
    return f"Info:{item.get('localMap','')} Emergency:{item.get('emergencyContacts','')} Hospital:{item.get('hospital','')}"[:2048]

def build_text_nearbyspot(item):
    return f"NearbySpot:{item.get('places','')} Distance:{item.get('distance','')} Travel:{item.get('travelTime','')} Desc:{item.get('description','')}"[:2048]

TEXT_BUILDERS: Dict[str, Callable[[Dict[str, Any]], str]] = {
    "Food": build_text_food,
    "Place": build_text_place,
    "Shop": build_text_shop,
    "Transport": build_text_transport,
    "Activity": build_text_activity,
    "Hiddengem": build_text_hidden,
    "Accommodation": build_text_accommodation,
    "Connectivity": build_text_connectivity,
    "CityInfo": build_text_cityinfo,
    "Misc": build_text_misc,
    "Nearbyspot": build_text_nearbyspot,
}

def sanitize(meta: Dict[str, Any]) -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    for k, v in meta.items():
        if v is None:
            continue
        if isinstance(v, list):
            out[k] = [x for x in v if x is not None]
        else:
            out[k] = v
    return out

def load_section(cat: str) -> List[Dict[str, Any]]:
    fname = CATEGORY_FILES[cat]
    path = DATA_DIR / fname
    if not path.exists():
        print(f"[SKIP] {cat}: file missing {fname}")
        return []
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    section = data.get(cat)
    if not isinstance(section, list):
        print(f"[WARN] {cat}: top-level key not list")
        return []
    return section

def ensure_index(pc: Pinecone, name: str, dim: int, cloud: str, region: str):
    if not pc.has_index(name):
        pc.create_index(
            name=name,
            dimension=dim,
            metric="cosine",
            spec=ServerlessSpec(cloud=cloud, region=region),
        )

def main():
    index_name = os.getenv("PINECONE_INDEX", "ycrag-travel")
    region = os.getenv("PINECONE_REGION", "us-east-1")
    cloud = os.getenv("PINECONE_CLOUD", "aws")
    api_key = os.getenv("PINECONE_API_KEY")
    if not api_key:
        raise SystemExit("PINECONE_API_KEY missing")

    embeddings = get_embeddings()

    # Preload all data & build texts to derive dimension once
    category_payloads: Dict[str, Dict[str, List[Any]]] = {}
    total_records = 0
    for cat in CATEGORY_FILES.keys():
        records = load_section(cat)
        if not records:
            print(f"[SKIP] {cat}: no records")
            continue
        builder = TEXT_BUILDERS.get(cat, build_text_generic)
        texts = [builder(r) for r in records]
        # metadata is sanitized original record (shallow copy)
        metas = [sanitize(dict(r)) for r in records]
        category_payloads[cat] = {"texts": texts, "metas": metas}
        total_records += len(records)
        print(f"[DATA] {cat}: {len(records)} records")

    if total_records == 0:
        raise SystemExit("No records found across categories.")

    # Embed all texts category by category (keeps memory moderate)
    pc = Pinecone(api_key=api_key)
    first_cat = next(iter(category_payloads.keys()))
    sample_vec = embeddings.embed_documents(category_payloads[first_cat]["texts"][:1])[0]
    dim = len(sample_vec)
    ensure_index(pc, index_name, dim, cloud, region)
    index = pc.Index(index_name)

    for cat, bundle in category_payloads.items():
        texts = bundle["texts"]
        metas = bundle["metas"]
        print(f"[EMBED] {cat} ({len(texts)}) ...")
        vectors = embeddings.embed_documents(texts)
        namespace = f"{cat}-Varanasi"  # Category-Varanasi
        # Map lowercase keys to proper case for namespace consistency
        namespace_map = {
            "Cityinfo": "CityInfo-Varanasi",
            "Hiddengem": "HiddenGem-Varanasi", 
            "Nearbyspot": "NearbySpot-Varanasi"
        }
        namespace = namespace_map.get(cat, f"{cat}-Varanasi")
        payload = []
        for i, (vec, meta) in enumerate(zip(vectors, metas)):
            payload.append({
                "id": f"varanasi-{cat.lower()}-{i}",
                "values": vec,
                "metadata": meta,
            })
        # Upsert in chunks
        CHUNK = 100
        for start in range(0, len(payload), CHUNK):
            batch = payload[start:start+CHUNK]
            index.upsert(vectors=batch, namespace=namespace)
        print(f"[OK] {cat}: upserted {len(payload)} vectors into namespace '{namespace}'.")

    print(f"Done. Total vectors inserted: {total_records}")

if __name__ == "__main__":
    main()
