"""Index all Agra category datasets into Pinecone with separate namespaces.

Namespaces pattern: <Category>-Agra (e.g., Activity-Agra)
Vector id pattern: agra-<category-lower>-<idx>

Relies on the split files:
  Accommodation_agra.json, Activity_agra.json, ... Transport_agra.json
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

DATA_DIR = ROOT / "data" / "agra"
CITY = "agra"

CATEGORY_FILES: Dict[str, str] = {
    "Accommodation": "Accommodation_agra.json",
    "Activity": "Activity_agra.json",
    "Cityinfo": "Cityinfo_agra.json",
    "Connectivity": "Connectivity_agra.json",
    "Food": "Food_agra.json",
    "Hiddengem": "Hiddengem_agra.json",
    "Itinerary": "Itinerary_agra.json",
    "Misc": "Misc_agra.json",
    "Nearbyspot": "Nearbyspot_agra.json",
    "Place": "Place_agra.json",
    "Shop": "Shop_agra.json",
    "Transport": "Transport_agra.json",
}

# Namespace mapping for consistency with bot expectations
NAMESPACE_MAPPING: Dict[str, str] = {
    "Cityinfo": "CityInfo-Agra",
    "Hiddengem": "HiddenGem-Agra", 
    "Nearbyspot": "NearbySpot-Agra"
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
    return f"Connectivity:{item.get('connectivityName','')} Type:{item.get('connectivityType','')} Desc:{item.get('description','')}"[:2048]

def build_text_cityinfo(item):
    return f"CityInfo:{item.get('cityName','')} Overview:{item.get('overview','')} History:{item.get('history','')}"[:2048]

def build_text_misc(item):
    return f"Misc:{item.get('miscellaneousName','')} Cat:{item.get('category','')} Desc:{item.get('description','')}"[:2048]

def build_text_nearbyspot(item):
    return f"NearbySpot:{item.get('nearbySpot','')} Dist:{item.get('distance','')} Desc:{item.get('description','')}"[:2048]

def build_text_itinerary(item):
    day_info = f"Day{item.get('day','')}:" if item.get('day') else ""
    return f"Itinerary:{day_info}{item.get('itineraryName','')} Places:{item.get('placesToVisit','')} Desc:{item.get('description','')}"[:2048]

TEXT_BUILDERS: Dict[str, Callable[[Dict[str, Any]], str]] = {
    "Food": build_text_food,
    "Place": build_text_place,
    "Shop": build_text_shop,
    "Transport": build_text_transport,
    "Activity": build_text_activity,
    "Hiddengem": build_text_hidden,
    "Accommodation": build_text_accommodation,
    "Connectivity": build_text_connectivity,
    "Cityinfo": build_text_cityinfo,
    "Misc": build_text_misc,
    "Nearbyspot": build_text_nearbyspot,
    "Itinerary": build_text_itinerary,
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
    
    # Use lowercase key for data lookup (consistent with file structure)
    lowercase_cat = cat.lower()
    section = data.get(lowercase_cat)
    if not isinstance(section, list):
        print(f"[WARN] {cat}: top-level key '{lowercase_cat}' not found or not list")
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
        
        # Apply namespace mapping for consistency
        namespace = NAMESPACE_MAPPING.get(cat, f"{cat}-Agra")
        
        payload = []
        for i, (vec, meta) in enumerate(zip(vectors, metas)):
            payload.append({
                "id": f"agra-{cat.lower()}-{i}",
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
