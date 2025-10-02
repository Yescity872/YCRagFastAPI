#!/usr/bin/env python3
"""
Split Agra.json into individual category files with _id metadata.
Similar to split_varanasi_data.py but for Agra city.

Input: data/agra/Agra.json
Output: data/agra/Category_agra.json files (12 categories)

Removes __v fields and preserves all other data including _id.
"""

import json
import os
from pathlib import Path

def split_agra_data():
    # Paths
    base_dir = Path("data/agra")
    input_file = base_dir / "Agra.json"
    
    if not input_file.exists():
        print(f"❌ Error: {input_file} not found!")
        return
    
    # Load main file
    print(f"📖 Loading {input_file}...")
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"✅ Found {len(data)} categories in Agra.json")
    
    # Category mapping (lowercase from file → PascalCase for filenames)
    category_mapping = {
        'accommodation': 'Accommodation',
        'activity': 'Activity', 
        'cityinfo': 'Cityinfo',  # Keep lowercase in key for consistency with Varanasi
        'connectivity': 'Connectivity',
        'food': 'Food',
        'hiddengem': 'Hiddengem',  # Keep lowercase in key for consistency with Varanasi
        'itinerary': 'Itinerary',
        'misc': 'Misc',
        'nearbyspot': 'Nearbyspot',  # Keep lowercase in key for consistency with Varanasi
        'place': 'Place',
        'shop': 'Shop',
        'transport': 'Transport',
    }
    
    total_processed = 0
    
    for source_key, target_category in category_mapping.items():
        if source_key not in data:
            print(f"⚠️  Category '{source_key}' not found in Agra.json")
            continue
            
        items = data[source_key]
        if not isinstance(items, list):
            print(f"⚠️  Category '{source_key}' is not a list, skipping")
            continue
        
        # Remove __v field from each item and preserve everything else
        cleaned_items = []
        items_with_id = 0
        
        for item in items:
            if isinstance(item, dict):
                # Create a copy without __v field
                cleaned_item = {k: v for k, v in item.items() if k != '__v'}
                cleaned_items.append(cleaned_item)
                
                # Count items with _id
                if '_id' in cleaned_item and cleaned_item['_id']:
                    items_with_id += 1
            else:
                cleaned_items.append(item)
        
        # Create output file with lowercase key (consistent with Varanasi)
        output_file = base_dir / f"{target_category}_agra.json"
        output_data = {source_key: cleaned_items}  # Use original lowercase key
        
        # Write to file
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ {target_category:12} → {output_file.name:25} ({len(cleaned_items)} items, {items_with_id} with _id)")
        total_processed += len(cleaned_items)
    
    print(f"\n🎉 Successfully processed {total_processed} items from Agra!")
    print(f"📁 Files created in: {base_dir}")
    
    # Verify all files were created
    created_files = list(base_dir.glob("*_agra.json"))
    print(f"\n📋 Created files ({len(created_files)}):")
    for file in sorted(created_files):
        print(f"   • {file.name}")

if __name__ == "__main__":
    split_agra_data()
